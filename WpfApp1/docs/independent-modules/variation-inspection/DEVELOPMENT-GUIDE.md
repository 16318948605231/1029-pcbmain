# 良品变化与印刷差异模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, C3, C4`

- 模块：`IM-030 variation-inspection`；来源：`PKG-026`
- 版本：`0.2.2-prep`；状态：C1～C4 `ModuleCoreImplementationReady`（仅Core/托管协调/Simulator规格）；N/U确定指导增量已限定内容接收；完整批准范围可决定软件设计已闭合并经原会话文档自审；N1/N2/U1实际实现/运行/资格 `PreparationIncomplete / NotReady`；修订日期：2026-10-12
- 范围：通用灰度变化模型、固定图样差异候选与稳定纹理差异
- 技术目标：C# / .NET 10；HALCON 26.05 经 AsunImage `ImageLibDotNet` 公共边界调用
- 规划消费者：不同视觉应用中的良品变化、印刷差异、稳定纹理检查
- 模块级设计评审态：`DesignReview`（方案可评审）。§13.3「完整批准范围的设计结论与剩余Owner」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本指导是 IM-030 算法、公开契约、工程、Host和测试的唯一实施规格；附录 A 定义模块自身的公开契约，主控已接收C1～C4六项规格，N/U确定指导增量已由主控限定内容接收，实际实现/运行/资格仍未就绪，不表示产品合同批准、实现或生产资格。[PKG-026](../../shared-modules/packages/PKG-026_VariationInspection.md)、MODULE-CATALOG、[DEV-VIS-026 §6/16](../../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#variation-inspection-method)及[原合同候选](../../13-contract-candidates/CONTRACT-CANDIDATES.md#variation-inspection-contract)仅为应用/历史导航，不反向定义本模块。原实施约束已收于本页§3–7、§9–12及附录A，研究原件及hash按§14保留；实现不得借导航或研究候选补定义。产品映射采纳只阻对应产品集成。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/variation-inspection/Asun.Modules.VariationInspection.Core/Asun.Modules.VariationInspection.Core.csproj`；namespace：`Asun.Modules.VariationInspection`。预定测试工程：`tests/Modules/variation-inspection/Asun.Modules.VariationInspection.Core.Tests/Asun.Modules.VariationInspection.Core.Tests.csproj`。上述项目尚未创建。
- 未来Core实现允许范围仅上述Core/测试工程；真实Adapter/WPF后续切片工程按§13.1逐项授权。本次文档任务允许写入仅本文件，不创建任何工程。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前状态：C1～C4已由主控按DEV-GOV-010 §3.1接收为`ModuleCoreImplementationReady`，仅限本页原Core/托管协调/Simulator规格范围；后续实现仍须明确派发及权威代码仓库/可审计快照起点。N1/N2/U1保持`PreparationIncomplete`；本绑定不是实现、集成或资格通过声明，本次不启动编码。

## 1. 职责与边界

模块接收已经确定参考坐标、已配准、通道/位深/预处理一致的单通道图像和不可变方法快照；它负责模型创建、良品训练、阈值准备、单图比较、亮暗响应分槽、完整评价支持统计、模型检查/装载/释放及自身运行诊断。输出是指定参考姿态下的像素差异候选、支持与模型来源，不是业务结论。

模块不得执行图像定位/配准、OCR 内容解释、文字/产品身份关联、目标或工单流程编排、业务规则、缺陷命名、工艺阈值解释、质量放行、复判处置、生产事实提交、设备控制、数据采集或训练样本自动接纳。不得读取宿主私有数据库、产品 ViewModel、全局状态、产品页面或设备 SDK。调用方保留运行顺序、目标关联、模板/工艺解释、最终判定、授权、审计写入及任何设备副作用。

算法边界：先经已批准定位/坐标能力把图像变换到固定参考格；在统一成像/通道/位深与完整支持上使用 Variation Model。HALCON 26.05 手册中的 `create_variation_model`、`train_variation_model`、`prepare_variation_model`、`prepare_direct_variation_model`、`compare_variation_model` / `compare_ext_variation_model`、`get_variation_model`、`get_thresh_images_variation_model`、`clear_train_data_variation_model`、`read_variation_model`、`write_variation_model` 是候选原语。经 `ImageLibDotNet` 的确切可调用签名、对象所有权和异常映射必须按该公共边界绑定，不从 HALCON 签名或同名旧包装推导。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.VariationInspection.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"不得读取宿主私有数据库、产品 ViewModel、全局状态、产品页面或设备 SDK"。

**Blazor/Web**：变化检测结果通过 gRPC/REST 查询；差异热图通过 HTTP Range 分片加载；浏览器不重新执行变化模型比较。

**AI 推理集成**：本模块使用 HALCON `compare_variation_model` 进行传统差异检测；`ai-inference` 的 anomalib PatchCore 是**并行**路线；两路结果都产出候选，宿主侧合并后进行三态仲裁。两路对同一缺陷的响应不同是预期语义差异，不是双跑失败。

**HALCON 双跑**：`create_variation_model`/`compare_variation_model` 与托管参照路线双跑；像素差异掩码的 F/B/U 分布设容差门禁（与 `segmentation` §1A 逻辑一致）。本仓 OpenCV 快照不含 variation model 方法，无第三方 oracle；托管参照须按 §1 已核对 26.05 语义自证。

## 2. 独立交付形态与依赖

发布边界固定为下列单元；Core 必需，其余按消费者部署：

| 单元 | 职责 | 依赖边界 |
|---|---|---|
| Core | 强类型请求/结果、参数校验、状态机、无 UI 能力入口 | 不引用 WPF、DevExpress、宿主 Shell 或产品领域类型 |
| AsunImage Adapter | 将 Core 图像/操作映射到 `ImageLibDotNet`；封装 HALCON 对象和 Variation Model 生命周期 | 原生对象仅在适配器内；以目标消费项目已引用的公共程序集/文档和编译核对为准，不把源码树作为运行依赖 |
| Optional WPF | 方法参数编辑、样本/模型诊断图和差异候选投影 | 调用同一 Core 校验/执行端口；不拥有业务规则、模型激活或事实写入 |

核心业务可无 UI 调用。运行时依赖以宿主构造参数注入。无静态单例、Service Locator、隐式磁盘路径、自动下载或宿主窗口初始化。输入图像采用 `image-frame` 等公开帧契约；模型字节与封存/保持沿既有 ModelAssets/InspectionEvidence Owner 的契约，模块不另建资产库、注册表或存储事务。

## 3. 公共数据语义与参数

下表是模块参数语义，精确公开形状按附录 A；平台 DTO 映射仍待原 Owner 采纳。`FrameReference` 绑定单通道帧、参考格、处理链和上游资格证据；Core 从注入的帧端口取得独立只读租约，保持到实际使用结束。公共边界不接收或返回 `HObject`、HALCON handle、可变图像指针或 UI 图形对象。

### 3.1 参数表

| 参数语义 | 强类型建议 | 单位/范围 | 缺省与校验 |
|---|---|---|---|
| 图像类型 | `VariationPixelType` | `Byte`、`Int16`、`UInt16`；对应 HALCON `byte`、`int2`、`uint2` | 必填；不接 RGB/多通道/real，不自动转型；输入与模型精确匹配 |
| 参考图宽、高 | `int Width/Height` | pixel；正整数且在 HALCON/宿主/Profile 共同限制内 | 必填；模型固定尺寸；训练及运行尺寸/参考格不符即拒绝 |
| 方法 | `VariationMethod` | `Standard`、`Robust`、`Direct` | 必填，不设隐式缺省；由调用方冻结的方法快照提供 |
| 比较方向 | `VariationDirection` | `Absolute`、`Light`、`Dark`、`LightDark` | 必填，不设默认方向；`LightDark` 固定亮、暗两个结果槽，空槽也保留 |
| 绝对阈值 A | `ThresholdPair(Light,Dark)` | 输入灰度单位；每个值均须有限且 ≥ 0 | 不设默认；标量由Host显式展开，两值顺序亮、暗 |
| 变化阈值系数 B | `ThresholdPair(Light,Dark)` | 无量纲；每个值均须有限且 ≥ 0 | 不设默认；由方法/Profile提供；不得命名为概率或未经确认的sigma倍数 |
| 训练帧序列 | 不可变、有序 `ImmutableArray<QualifiedSample>` | Standard/Robust 为 2–65,535 张且至少两个独立来源组；实际数量和更小上限由 Profile 给出 | 至少两组仅防单样本退化，不证明统计充分；顺序固定；Robust 一次传完整样本集；Direct 训练序列必须为空 |
| Direct 输入 | `DirectModelSource`：ReferenceImage、ExternalMap的VariationImage或Sobel3的SobelSource、SourceGroupIds和构造来源 | Reference/v与模型同尺寸/类型/参考格；SobelSource为W+2/H+2真实halo，格原点−1/−1；v非负且合法图型 | Direct必填；不得把real诊断v未经批准量化回灌；重建闭包保留原来源和全部硬同源组 |
| 参考支持 R、检查域 D、排除域 I | 强类型参考格 Region/Mask 引用及来源 | pixel；`D ⊆ R`，冻结时 `D ∩ I = ∅` | 必填且来源可追溯；首版训练/比较要求整个 R 和逐级采样足迹均有真实完整输入支持。I 不允许在 R 内伪造填充值 |
| 超时预算 | `RequestHeader.DeadlineUtc` | UTC截止点；接纳时剩余时长>0且有限 | 每请求必填；由Host显式Profile确定，不表示同步native可抢占 |
| 并发/资源预算 | `VariationResourceBudget` | 图像数、并发实例数、临时字节和输出上限为非负整数/字节数 | 显式 Profile；预算不足在分配/派发前失败，不自动抽样、缩域或切换算法 |
| 取消 | 请求入口`CancellationToken`及operation.RequestCancellation | 非数值 | 同步校验/查询无IO、无取消令牌；执行入口按附录A，底层不可中断时仅在安全调用边界检查 |

阈值公式唯一按本页§3.4；训练资格/来源隔离按§3.5/§4.1–4.2，完整支持/D/I及分块按§3.5/§4.1，方向按§3.2/附录A.4，模型闭包按§7。HALCON 文档未定义的标准差分母、MAD 精确缩放、整数舍入/饱和和缺失域训练口径不得由实现者补猜。不能把 `AbsThreshold = 10`、`VarThreshold = 4` 等示例数当默认值。

### 3.2 输出语义

一次比较必须返回输入请求关联、模型修订/内容身份、算法/适配器版本、参考格、已处理块、原始方向结果槽、完整支持和不确定原因。结果分清：`E` 为有完整支持且实际比较的范围；双向时 `L`、`K` 分别为亮、暗候选，`N = E − (L ∪ K)`，`U = D − E`。单方向时 N 仅指该请求方向无候选，另一方向标 `NotRequested`，不能称双向无变化；Absolute 返回一个无方向合并槽，不能伪造 L/K 分解。输出 `RequestedDirection`、槽种类和覆盖质量必须同时保留。候选区域不由本模块命名为缺陷类别；区域连接、形态派生和量测由调用方按各自批准方法完成。

比较成功只说明方法完成，并不表示无缺陷或质量合格。空候选与全域无响应只有在 `U` 为空且请求中所有必需方向/块均完成时才能区分表达。结果为部分评价时保留已算块并同时返回 U/未完成原因；宿主不得把部分结果折算为全域结果。

### 3.3 空输入、空结果与部分成功

- 空的训练帧列表、空的 Direct 理想图/变化图、零宽/零高图像、空 R 或空 D 都是 `InvalidParameter`；它们不能创建模型，也不能以“无变化”完成。
- 合法输入经过比较而候选 Region 为空是正常完成：仅表示在 `E` 内没有超过模型阈值的像素。只有 `U` 为空、请求的方向槽均已返回且没有降级步骤时，才可报告“已完整评价、候选为空”。
- 分块、批处理或多目标请求中部分块成功时，结果必须逐块标记 `Completed`/`Unknown`，将已完成候选和剩余 U 一起返回；整个 operation 终态为 `Completed` 仅适用于所有必需块完成。若取消、预算或错误发生，终态为相应非成功状态，不能把已返回块拼成全域成功。
- 缺少一个 `light_dark` 槽、缺少一个训练样本的支持足迹、只得到一半诊断图或只读到旧模型版本，均是结构/支持错误而非空结果；适用时返回 `IncompleteSupport`、`AdapterFailure` 或 `PersistenceFailure`。

### 3.4 上下阈值、严格边界与可复算反例

依据目标26.05的[prepare_variation_model](../../../halcon算子手册/operators/prepare_variation_model.html)、[prepare_direct_variation_model](../../../halcon算子手册/operators/prepare_direct_variation_model.html)及[compare_ext_variation_model](../../../halcon算子手册/operators/compare_ext_variation_model.html) Description 内嵌公式SVG。设p为参考格像素，i(p)为理想灰度，v(p)为非负变化值，c(p)为当前灰度；`a_u=A.Light`、`a_l=A.Dark`、`b_u=B.Light`、`b_l=B.Dark`。HALCON两元素tuple索引0是亮/上、1是暗/下；若各参数单值，则该参数分别显式展开为相同两值，A与B可以各自独立对称。模块公开面始终传ThresholdPair，不再传不定长tuple。

```text
t_upper(p) = i(p) + max(a_u, b_u * v(p))
t_lower(p) = i(p) - max(a_l, b_l * v(p))
L = { p in E : c(p) > t_upper(p) }
K = { p in E : c(p) < t_lower(p) }
Absolute = [L union K]; Light = [L]; Dark = [K]; LightDark = [L, K]
```

使用max而不是A+Bv。B相对变化图响应，不是当前灰度百分比、概率或跨模式统一的sigma倍数。理论允许带是闭区间`[t_lower,t_upper]`：等于任一边界不入对应候选，禁止加epsilon、改成≥/≤或把值先四舍五入后自行判定。`v=0`时半宽为A；`A=B=0`时理论上下界均为i，只有严格偏离i才响应。A/B非负有限且v非负时下界≤i≤上界，亮暗理论集合不相交。实际训练/prepare/compare始终交HALCON，Core不逐像素计算这些式子、不手写第二native算法。

| 解析向量（不是生产参数） | 理论阈值及预期 | 可检出的错误 |
|---|---|---|
| i=100、v=3、A=(5,8)、B=(2,1) | 上106、下92；c=107只亮、91只暗；106/92和100均无候选；LightDark固定两槽，Absolute一个合并槽 | A+Bv会错误放宽到111/89，并漏掉107/91；颠倒tuple会错置方向 |
| i=100、v=0、A=(5,8)、B=(2,1) | 上105、下92；105/92无候选，106亮、91暗 | 把A也乘v会错误退化为零宽带 |
| i=100、v=3、A=(0,0)、B=(0,0) | 上下均100；99暗、100无候选、101亮 | 使用≥/≤会把100同时计亮暗；零阈值合法不等于适合生产 |
| i=100、v=3、A=(5.5,8.25)、B=(2.25,1) | 未量化理论上106.75、下91.75；真实边界必须读回并用整数输入挑战 | 不得把106.75自行floor/round/ceil来预言HALCON输出 |

上述式子定义官方语义及解析Oracle，不给HALCON内部量化背书。实际阈值通过`get_thresh_images_variation_model`按MinImage→MaxImage读取并按真实图型保存；VI-N01覆盖理论值与实际读回、整数可表达的内/等/外、极小/极大灰度及饱和边界。理论上界超出byte等输入范围时不自行裁回、包绕或声称可表达等号；记录实际阈值及可表达输入的比较结果。数值/舍入差异属于native Golden门，不改变严格比较语义。Standard的ddof/内部累计精度、Robust的精确MAD倍率/偶数中位数舍入未由所读官方页明确，不借NumPy/SciPy默认值补定义；Direct的v来自冻结构造，不称统计标准差。

### 3.5 成像、资格、支持传播与应用约束

Host在训练前冻结产品/印刷修订适用域、独立参考格/到父格映射、通道/曝光/照明/材料范围、实际类型/有效位、有序预处理/插值链、配准基准/自由度/残差门、R/D/I、来源用途及资源。公共载荷通过MethodSnapshot的Applicability/QualificationProfile/ProcessingHash/DomainSource及帧证据绑定这些已物化事实；模块验证身份、一致性和支持，不从私表获取，也不替外部Owner判定这些领域事实。12-bit-in-uint2与byte不无依据共用A。显示LUT、每图min-max、从本件拟合亮度迎合参考均不作为隐式前处理；已批准校正需独立稳定基准及校正前证据/实际参数。

上游先核板/面/标签/印刷修订→独立基准定位→唯一候选、残差、适用范围→按冻结方向映射到参考格→逐级核真实足迹→固定R。令V0为源真实有效样本，第j级输出q的实际滤波/插值取样集合为Kj(q)，要求`Kj(q) subset of V(j-1)`且坐标/方法/质量合格；逐级传播，不能只变换mask中心或只核最后一级。双线性四点缺一、坏点/饱和/未采/越界/足迹未知都不能被0、镜像、上一帧或常数填补后算实测。R固定完整矩形，D⊆R非空，D∩I为空；训练及单块compare要求整个R和全部所需足迹完整，I不解除R支持义务。不完整单块全D为U；Host只能合并预冻结完整矩形块，不按本件缺失位置临时切块/缩D/重训。

配准保留原位移/角度/尺度/形变及其独立几何门。不得只用待检印刷边缘对齐并以局部形变消除待检偏位；一像素平移被复原后外观无响应仍可能位置不合格。差异沿同一保存变换一次回投，显示缩放不计物理面积；形变反映射/计量资格不足时只交参考格候选。外部segmentation/计量按各自唯一指导消费原始槽、派生关系/过滤理由/未知接触边界，不能把LightDark两个Region当两个缺陷。

来源先于增强/裁图/选参分组：同板/标签、同观察、重拍、双面/返修及增强的硬同源关系由Host提供；必要时隔离批次、材料、设备和时间范围。训练良品须独立核正确修订、非缺笔/污染、成像及支持；OCR读对或本模型无响应不能自证良品。纳排有独立理由；不得看残差删“难良品”，标签修正追加新修订并重建受影响评价。模板、参考图、亮度校正、D/I、自由度、A/B只用获准拟合/Validation数据；看过最终测试再修改即新候选并保留曝光。单金板的Direct/合成与真实多件统计分开，合成不增加独立观察或覆盖，不训练掉本应检出的偏移/缺笔。

固定/变量文字分开：批准I排除序列/日期并不完成变量内容/字形义务；OCR内容正确也不能抹掉固定字形候选。亮并不恒等缺笔：黑字浅底缺笔常偏亮，白字深底常偏暗，材料/照明变更重新取资格。像素候选、几何公差、物理缺陷定义及质量放行分别由原Owner处理；模块不给业务PASS，不发布程序或设备命令。

## 4. 算法路线、备用与恢复

路线选择由调用方冻结的方法快照和资格 Profile 给出，模块不得在运行时按结果自行换路：

| 路线 | 适用前提 | 处理顺序 | 可用备用/恢复 |
|---|---|---|---|
| `Standard` | 多张合格、同参考姿态且期望保留正常灰度变化；训练样本顺序已冻结 | 建模 → 按冻结顺序逐次 `TrainVariationModel` → `PrepareVariationModel` → 独立留出评价 | 单次训练/prepare 失败时销毁该工作实例并按同一快照重建；不能在已 prepare 实例上隐式追加 |
| `Robust` | 允许候选集中存在少量异常但仍有独立良品资格；完整训练集可一次提交 | 建模 → 一次提交完整训练集合 → prepare → 独立留出评价 | 缺内存时拒绝或切换到事先批准的新快照/新空间分块方案；不得把多个批次的 robust 结果合并或只保留最后一批 |
| `Direct` | 有经过批准的理想图和变化图来源；不声称统计训练充分 | 建模 → `PrepareDirectVariationModel` → 诊断/留出评价 | Direct 来源不完整、值域/量化不合格时拒绝；不得把 `GetVariationModel` 得到的 real 变化图未经批准量化后回灌 |

变化模型不是配准器、去噪器或亮度自适应器。噪声、遮挡、曝光异常和严重姿态偏差先由调用方通过 image-quality/registration 端口处理；如果质量门不通过，模块返回 `IncompleteSupport` 或 `UnsupportedInput`。只有已批准方法快照明确登记的预处理、遮挡排除域 I 和注册自由度可以参与；模块不为“让结果通过”自动调曝光、归一化、局部形变或缩小 D。候选路线失败时的备用是重新执行已批准的完整快照并保留原失败证据，不是在线学习、调阈值或接受当前输入。

### 4.1 26.05 路线决策与逐能力步骤

主路线固定为 Variation Model 的逐像素统计/阈值比较，使用 CPU；不在模块内调用 set_system 改全局线程、OpenCL 或空对象政策。方法已明确模式时遵循该模式；新方法设计优先选择独立合格多件样本的 Standard。确有离群风险且具备全量内存预算时，工程人员可明确请求 Robust 候选，经同分组留出集比较后冻结；没有多件独立图时只能请求带显式来源的 Direct。失败不自动换模式。本表冻结方法分支，不宣称同样本最快或最准确；真实比较按 §10–11。

Standard在每个相同参考像素使用训练集均值/标准差；Robust使用中位数/适当缩放的MAD，精确缩放与量化按§3.4保留未知，不能由实现者补值。少量外点可改变Standard参考并放大v，多数固定缺陷也可成为Robust参考，MAD=0不证明完整工况。Direct/Sobel边缘放宽恰在细笔画/间隙处，须挑战弱缺笔/重影/字距，不能把高残差自动回灌v。输入资格和独立评价不可被模式名替代。

| 能力/候选 | 调用顺序、输入域和分支 | 正确性/拒识、资源与退路 |
|---|---|---|
| Standard | 核样本/完整 R → create_variation_model(standard) → 按固定顺序逐张 train_variation_model → get_variation_model → prepare_variation_model → get_thresh_images_variation_model | 均值/离散度易吸收污染；禁止在线追加；每张调用结束才归还输入；预算保留模型/诊断/临时量；失败清工作实例后从全清单重建 |
| Robust | 同一完整 R、相同样本集合 → concat_obj → 一次 train_variation_model → 诊断/prepare | 全量样本租约直到训练返回；重调覆盖旧集合，不能流式分批；多数固定缺陷/MAD=0不自证良品；预算不足拒绝，不抽样 |
| Direct/ExternalMap | 核冻结 Reference/Variation 两图来源、类型/尺寸/非负响应 → create(direct) → prepare_direct_variation_model → 读取阈值 | v单位是来源响应，不叫 sigma；Ref/Var 不存入 .vam，运行闭包保存构造引用，重建闭包保留原图；参数改变用隔离新工作实例重建 |
| Direct/Sobel3 | 核参考图及已完成的全局预处理/真实一像素邻域 → sobel_amp(sum_abs,3) → 核实际输出类型/非负范围 → prepare_direct_variation_model | 仅接受 byte 参考图的该固定构造分支，实际 v 必须属于 Direct 允许类型；无静默 convert_image_type、缩放或饱和修复。3 是此构造的固定核尺寸，不是工艺阈值；R 四周一像素真实 halo 由宿主先准备，图边不能靠虚构邻域。高位深采用 ExternalMap，新的构造需修订本指导/Golden |
| 灰度范围候选 | gray_range_rect 的 max−min、奇数窗口、镜像边界及 reduced-domain 警告已查 | 会放宽边缘附近细缺笔，且偶数窗口被算子改小；不作为 v0.2 自动备选。需要新方法修订及边缘挑战后才可采用 |
| 纯差分候选 | abs_diff_image 倍率1；sub_image 有符号差但整数越界会裁剪；dyn_threshold 常用于图与平滑图比较 | abs_diff 丢极性且整数裁剪；dyn_threshold 不能自动当 Variation 的严格阈值等价。三者可供 Host 另行批准诊断/分割，不替代训练和模型闭包，不回填候选主结果 |
| 单图比较 | 完整 R、精确 Loaded 模型 → compare_ext_variation_model，模式与请求一致 → select_obj 保留空槽 → 与固定 D 相交 → 输出原槽/E/N/U | 输出 Region 数不是缺陷数；区域过大/游程超额以 ResourceBudgetExceeded 失败，不丢小响应；无支持的单块不调 native，只返回 E=空/U=D |
| ROI/空间块 | 固定完整矩形 R，小 R 可由 crop_part 从冻结父格取出；每块建立独立模型并沿父格映射合并 | reduce_domain 只交域、不缩矩阵/峰值；crop_part 可产生不完整边域，必须再核支持。空间块使用同一全训练集/全局处理/真实 halo；整图与块同样本 Golden 前不宣称等价。块编排和跨缝连接由 Host/原区域能力负责 |
| 诊断/保存/重开 | 训练图 i/v 必须在 clear_train_data 前取得；阈值查询先 Min 后 Max；写候选闭流/hash → 外部封存 → fresh read_variation_model → 查询子集+固定 Golden | Direct 及瘦模型的 i/v 查询为 Unsupported，不隐式 prepare；写/读失败保留旧运行模型；正式读回禁缓存命中，返回技术报告而非激活回执 |

诊断 v 不足以证明光照还是缺陷。每个 FrameReference 必须绑定上游 `InputEvidence`：IndependentAlignment、Illumination、ImageQuality 三项结论、各自方法/结果内容引用、处理链 hash、参考格、逐级足迹结论。结论为 Accepted/Rejected/Unknown，不由本模块重新估计。错格/证据修订不匹配拒绝；对齐候选不唯一、照明/质量 Rejected 或 Unknown 时不进入 compare，返回整块 U 和独立原因。宿主用独立基准判断位置偏差、稳定照明基准判断漂移；本件目标边缘对齐或全图直方图归一化不能把待检差异消掉。已有明确批准的校正只作为冻结处理链输入；原图和实际校正引用随证据保持。

参数变更影响固定：A/B、模式、参考图/v、训练成员或顺序、参考格/尺度/通道/位深/处理链/排除域发生变化，均产生新的 MethodSnapshot hash 和新候选/prepare；生产 Loaded handle 不接受这些修改。方向是冻结方法字段，改变方向也需新的方法快照和技术匹配；只重用内容可证明相同的 native 模型字节，仍不得沿旧 runtime token 调用。显示 LUT、语言/布局变化不重训、不改方法 hash。外部来源失联不会改已持有模型；尚未取得的输入按失败结算，Unknown 不能返回空差异。

固定空间块的等价前提逐项为：同一全局参考格和独立配准、每个位置同一完整训练成员集与次序、相同类型/处理链/统计量化/A/B/方向、所有插值/滤波/Sobel真实halo在裁core前取得、全图亮度参数不逐块重估。先形成合格全局注册图或等价按需采样→取各固定块及halo→构造输入/v→裁core建立独立尺寸模型→比较→只并集core响应/E/N/U→外部区域能力做跨缝连接/全局特征→最后过滤。每块Robust仍一次全N；不裁原模型、不把小图送整图handle、不按块筛掉小候选。逐块独立“拉正”偏位、镜像补halo、挑不同良品子集或先过滤均非等价。模型总存储仍随全域面积，只有按需加载且无其它持有者才可能降低活跃峰值；native量化/顺序/采样及跨缝真实Golden未测，不能仅据逐点数学可分离就称整图等价。

### 4.2 离线参数建议与独立评价

`Recommend` 是无 UI 工程能力，不接受 ProductionRead runtime。输入冻结训练清单、Validation 成员/真值域、有限且有序的候选 MethodSnapshot 列表、搜索预算和 `SelectionPolicy`；不自动扩展候选，不学习当前运行帧。候选只允许改变 A/B，参考格/通道/模式/训练与 Direct 源不变；跨模式比较用分别 Build/Evaluate，不能悄悄多路训练。A/B 每值有限非负并处于宿主批准闭区间；无合法范围/候选返回 InvalidParameter。

固定流程：核来源组和用途互斥 → 顺序处理候选 → 独立工作 handle 训练/prepare → 用 Validation 集 Evaluate → 释放该 worker → 按可判定政策选结果。保守 v0.2 不克隆/重用未知训练状态；以后若优化只读诊断/训练缓存，须保持同样本输出和资源顺序。最大候选数、最大比较数、每候选期限和全局资源来自 Profile；取消/超时保留已测条目，但建议状态为 Incomplete，SelectedOrdinal=null，不把早期候选当搜索完成。

指标精确定义：每个labelled图核真值域⊆D、槽形状与请求一致；逐SlotKind计算TP_s=|C_s∩G_s|、FP_s=|C_s−G_s|、FN_s=|G_s−C_s|，再checked求和；LightDark不能合并后把极性错配当TP，亮暗真值交集须为空。Absolute只有一个Absolute真值槽；单方向不声明另一方向已检。图像级漏检为真值槽总面积非空且所有正确槽匹配TP总数=0；良品误报为所有G空且任一C非空。像素指标只作方法挑战，不代缺陷级召回；Unknown仍计计划分母，未读/预算不静默删除。IndependentTest与Training/Validation硬同源组均不相交；重拍/增强仍同组。样本不足/无真实正例时真实指标NotEvaluated。

筛选顺序固定为：全部计划 Validation 成员完成且 U=空 → 满足 Policy 的最大漏检图数和良品误报图数 → 按漏检图数、良品误报图数、FP像素数升序 → 同分取输入候选 ordinal 最小。上限由调用方明确提供，可以为0但没有隐式生产默认。无候选满足为 NoFeasibleCandidate；返回每个阈值、实测计数、未评价原因、版本/hash 和选择依据。建议需 Host 人工采纳后构造新冻结方法/候选，不能写回生产参数。最终独立评价只报告，不反向调参；测试集已曝光后改方法须新候选和新的独立测试资格。

Policy.RequireRealEvidence由Host显式设置，常规生产准备设true；false仅允许对合成/解析/模拟数据给工程建议，返回RealEvidenceComplete=false并显示“仅工程建议，真实样本未评价”。计算计数/排序与真实资格分开，不能把测试声明的标签当实际观察。所有候选仍须有良品和正例两类、完整计划和支持；缺任一类不选择。最终IndependentTest不因该开关降低曝光/来源隔离。

### 4.3 ImageLibDotNet 接入面与类型歧义

平台已明确 `ImageLibDotNet.cv2` 可调用全部 HALCON 26.05 算子，Adapter 主入口固定为 cv2。下表仅保留历史 `HVariationModel` 对象式参考面，不能视为本轮已核实的 C# 重载，也不要求实现者先证明算子存在；真实 C# 类型/重载/封送存在歧义时才查公开签名或消费编译。原生对象只能停留在 Adapter。

| 已见方法面 | 语义和 Adapter 约束 |
|---|---|
| `HVariationModel(int width, int height, string type, string mode)`；`CreateVariationModel(...)` | 创建/替换可变模型实例；Core 必须先验证尺寸、像素类型和方法，替换前排空旧实例，不把旧对象隐式复用 |
| `TrainVariationModel(HImage images)` | 参考面以 `HImage` 承载 HALCON `singlechannelimage(-array)`；Adapter 负责把有序帧集合组装为拥有明确租约的对象，并在返回前保持输入 |
| `PrepareVariationModel(HTuple,HTuple)` / `(double,double)`；`PrepareDirectVariationModel(HImage,HImage,HTuple,HTuple)` / `(HImage,HImage,double,double)` | A/B 可走标量或 `HTuple`；Core公开面固定ThresholdPair，Adapter可将对称对显式传标量或亮/暗两元素tuple，Adapter 不把旧文档默认 10/2 变成平台默认 |
| `CompareVariationModel(HImage) -> HRegion`；`CompareExtVariationModel(HImage,string) -> HRegion` | 单图比较；`light_dark` 的对象序列不能被 Adapter 压成一个无方向区域，必须保留槽序/空槽和返回资源 |
| `GetVariationModel(out HImage)`；`GetThreshImagesVariationModel(out HImage)` | 诊断图必须在 `ClearTrainDataVariationModel()` 前复制需要保留的证据；返回对象由 Adapter 释放/转移，不能暴露给 UI |
| `ReadVariationModel(string)` / 构造 `HVariationModel(string)`；`WriteVariationModel(string)` | 文件路径由A.6暂存端口控制；正式资产先由Host物化为精确包，读入新实例并完成 hash/尺寸/能力/fresh Golden 后才可装载，失败不替换当前实例 |
| `Serialize(Stream)` / `Deserialize(Stream)`、`SerializeVariationModel()` / `DeserializeVariationModel(...)` | 可作为受控字节适配候选；序列化字节须在封存租约内闭流并核 hash，不能把 `HSerializedItem` 当 Core 结果或持久化事实 |
| `ClearTrainDataVariationModel()`；`ClearVariationModel()`；继承 `Dispose()` | 前者仅在 prepare 后释放训练数据，之后不可继续训练或读取训练图；后者/Dispose 只在所有在途 native 调用排空后执行 |

该参考面显示包装以同步方法为主；模块异步入口应由 Core 的有界调度和 Adapter 调用边界实现，不能宣称 HALCON 同步调用可被 `CancellationToken` 抢占。`HRegion` 可能承载对象数组，实际多对象/空对象形状仍须在目标程序集上编译与 Golden 核验。

### 4.4 调用入口与执行顺序

公开入口及全部载荷按附录 A 的 v0.2 候选契约实施；产品 Schema 和 Adapter C# 重载不反向定义 Core。下表说明职责，后面的最小 Host 顺序使用同一方法名。

| 入口职责 | 语义 |
|---|---|
| 参数/输入校验 | 同步、无副作用；返回字段级问题、支持域/版本问题及所需修正，不创建 native handle |
| 建模/训练/准备 | 非阻塞返回operation；一个工作实例独占可变model handle；取消不发布半成品；v0.2不提供阻塞包装 |
| 比较 | 一次一帧一模型；非阻塞operation调度；结果绑定请求/输入/模型/方法。Evaluate内部有界逐图执行，批量板流/多ROI编排由Host调用单块接口 |
| 诊断读取 | 只读理想图/变化图/阈值图；在 clear-training 或 direct 模型失去源数据前，先复制调用方要求保留的证据 |
| 释放/关闭 | 请求停止接收、取消可取消工作、排空真实运行中的 native 调用，再归还租约并清句柄 |

无 UI 正常流程：

1. 宿主创建独立实例，注入Backend、帧租约端口、TimeProvider和Options；读取能力版本。资产IO/事实提交在Host，诊断通过operation拉取。
2. 构造冻结的方法/样本/阈值/支持快照；调用校验。校验不通过时不分配模型或改变现行模型。
3. 验证每张训练图的身份、用途、成像/注册一致性、完整 R 支持及资格；不由模块从“上次通过”的在线图自动收样。
4. Standard 按冻结顺序向同一工作模型累计；Robust 将完整训练集合一次提交；Direct 使用显式理想图与变化图来源，不伪称统计训练。
5. 准备阈值并读取需要保留的诊断证据；BuildCandidate 返回工程候选，不包含生产资格。再用 Evaluate 独立评价；评价未满足接受门时仍保留工程证据，但不得请求生产采用。
6. 宿主按原资产 Owner 保存候选并通过真实 fresh 读回验证；模块只报告技术能力和未知项，不激活生产模型。
7. 运行时验证模型适用修订、像素类型、参考格、输入完整支持和参数快照，然后逐请求比较并返还亮暗槽、E/N/U、版本与诊断。
8. 宿主接收结果后自行应用领域规则和提交流程；关闭实例时取消、排空、释放并归还帧/模型租约。

无 UI 最小 Host 顺序（语义伪代码；模块方法名按附录A。owner/Track/AwaitTracked等为Host自身职责，不是遗漏的模块API；其有限等待/保留责任见代码后规则）：

```text
owner = host.ExistingLifetimeOwner // 在本次任务返回后仍存活，先登记Owner再创建
module = owner.CreateAndAttach(() => AsunImageVariationModule.Create(options, adapterOptions, frames, scratch, timeProvider))
// 创建前已预留Owner槽，返回值立即强登记；纯Core测试换VariationModule.Create+ScriptedBackend
try:
    capabilities = module.GetCapabilities(); owner.BindInstanceAndSequence(capabilities.InstanceId)
    issues = module.ValidateTraining(trainingSnapshot)
    if issues.Issues not empty: host.Report(issues); return
    candidate = await owner.AwaitTracked(owner.Track(module.BuildCandidate(buildRequest, ct)))
    owner.RequireCompleted(candidate) // 非Completed不进入下一步，partial也不发布
    preview = await owner.AwaitTracked(owner.Track(module.Load(previewRequest(candidate.Value), ct)))
    owner.RequireCompleted(preview); owner.Remember(preview.Value.Runtime)
    evaluation = await owner.AwaitTracked(owner.Track(module.Evaluate(holdout(preview.Value.Runtime), ct)))
    owner.RequireCompleted(evaluation)
    if not host.Accepts(evaluation.Value): return // 仍执行finally；不是模块生产批准
    sealedPackage = await host.SealMaterializeAndVerify(candidate.Value.Package)
    loaded = await owner.AwaitTracked(owner.Track(module.Load(productionRequest(sealedPackage, golden), ct)))
    owner.RequireCompleted(loaded); owner.Remember(loaded.Value.Runtime)
    result = await owner.AwaitTracked(owner.Track(module.Compare(request(loaded.Value.Runtime), ct)))
    owner.RequireCompleted(result)
    host.ApplyDomainRulesAndCommit(result.Value) // 消费/提交抛异常也执行finally
finally:
    try:
        owner.CancelPendingAndReleaseKnownTerminal() // 每项隔离异常；终态才ReleaseOperation
        for token in owner.KnownLoadedTokens:
            try:
                unload = owner.Track(module.Unload(newHeaderAndToken(token), CancellationToken.None))
                await owner.ObserveWithinCleanupBudget(unload)
            catch cleanupError: owner.Record(cleanupError) // 拒绝/满槽不跳过Stop
    finally:
        try:
            receipt = await module.StopAndDrainAsync(owner.FiniteCloseDeadlineUtc, owner.CleanupWaitToken)
            owner.Record(receipt)
            if receipt.State == Drained:
                owner.ReleaseAllKnownTerminal() // 此时包括迟到Load/失败/Unload
                await module.DisposeAsync()
                owner.MarkClosed() // 确认完成后才解除强引用
            else:
                owner.KeepForObservation(receipt) // 不再发新工作，不Dispose backend/帧端口
        catch closeError:
            owner.KeepForObservation(closeError) // 关闭/释放异常保留原身份和资源
        finally:
            owner.ConfirmRetentionOrAcceptedHandoff() // 未获确认仍由原Owner持有
```

CreateAndAttach是Host原Owner的创建接管辅助：调用工厂前预留持有槽，工厂返回即保存强引用，不在创建成功和登记之间执行可能抛出的业务动作；工厂失败按§7.1回滚，无module需关闭。ConfirmRetentionOrAcceptedHandoff不因转交拒绝/异常抛出而掩盖业务失败，只保留并报告状态。Track在拿到每个入口返回handle后立即登记Key/handle/Completion及所属InstanceId；不等消费成功才登记。重复冲突的只读Rejected handle不替换原Key的operation。AwaitTracked以Host显式有限观察预算等待；时间到只请求该原operation取消并保留其Completion/Query，不把等待超时当底层完成。观察期限与请求DeadlineUtc区分，业务ct已取消不取消finally；清理等待用单独有限token/截止点。cleanup错误单独保留，不能覆盖原消费/验证异常。operation上限/保留槽由Options限制；先Release已终态项再尝试Unload，Unload拒绝/超时由StopAndDrain兜底，不反复补发新Key。未知Load可能晚返token，Stop覆盖全部内部模型，不依赖Host当时已知token列表。

原LifetimeOwner在任务返回后保留module、借用端口的上游保持权、原operations、pending tokens和关闭记录；每次有限tick只Query原Key/读有界事件/观测原Completion，必要时以新有限等待调用同实例StopAndDrain，不重新Load/Build或创建替代backend。真实Drained后归还所有终态记录并完成Dispose，才释放Owner登记及上游保持权。若需要转交，由既有宿主生命周期服务显式接受该同一实例/上下文并返回确认，确认前原Owner不解除强引用；拒绝、超时或转交抛异常均原Owner继续持有并报告“资源仍在排空”。不得只记录日志、丢后台Task、以进程临时对象/GC或无限阻塞finally冒充关闭；现场进程退出/强制终止由宿主策略决定，不由模块假造已释放。借用共享Core的UI不执行本段实例Stop/Dispose，仍按§8卸载自身资源。

## 5. 事件顺序、状态与错误

### 5.1 事件

每项操作使用唯一 `OperationId`、请求修订、实例代次和单调序号。事件为诊断投影，不构成第二结果权威。

1. `RequestReceived → Validating`：同步结构/版本/参数预检；无资源的失败只发 `Rejected`。
2. `Accepted → Queued`：结构接收并绑定输入/方法/模型版本和预算额度；后续帧物化、内容核验或 native 失败均按已接纳路径结算。
3. `Started`：资源已取得，正式操作开始。
4. 零到多个 `Progress` / `Diagnostic`：训练样本或块进度、候选计数、耗时；允许合并旧进度，不允许丢失终态或将中间量冒充结果。
5. `Draining`：停止新工作并等待底层实际退出。
6. `Drained`：仅在底层实际退出、句柄/帧资源已可归还后发出。
7. `ResourcesReleased`：本次拥有的临时图、工作handle、帧/输入租约及比较借用租约已归还；结果是有界托管不可变复制，没有输出native租约。Loaded长期模型由实例持有、仍计资源，只有Unload/关闭才释放；保留operation的托管输出按驻留预算计，不把逻辑完成说成进程内存归零。
8. 资源归还后恰好一个 `Completed`、`Cancelled`、`TimedOut` 或 `Failed` 终态；预检未接纳的请求只发 `Rejected`，不得伪造 `Started`、`Drained` 或已接纳终态。排空未确认统一为非终态 `DrainUnknown`；保留租约/句柄并持续计入预算，不发 `ResourcesReleased` 或终态，待原调用退出后结算。正常完成也经过排空/资源归还。并发取消和 deadline 以模块单调时钟观察的最早停止原因为准；相同时间取 Cancelled，资源已归还且终态已定后不改写。

v0.2 不公开算法回调或订阅入口；调用方通过 operation 的 `Query` / `ReadEvents` 拉取不可变投影，Completion 是唯一权威结果。事件环有界，旧进度允许合并；缺序由 EventBatch.FirstAvailableSequence 显式报告，Query 始终提供当前状态和最终结果。调用方的 UI 回调/慢处理不占 native 线程，也不持有 native 租约；迟到投影按 OperationId、请求修订、runtime epoch 和 UI 草稿代丢弃。

### 5.2 状态语义

operation 状态精确按附录 A；事件 RequestReceived/Started 分别投影为状态 Validating/Running。排队取消可跳过 Running，但必须走 Draining/Drained/ResourcesReleased。`IncompleteSupport` 是结果覆盖质量：单块 R 不完整时不调用 compare，E/N/候选为空、U=D，Completed 只表示已完成本次支持检查，不表示已比较。多块由 Host 调用多个单块 operation 并按冻结计划合并；本模块不隐含批量执行。训练缺支持始终失败，不生成候选。模型生命周期分开表达：`CandidatePrepared → Sealed → ReadBackVerified → Loaded → Draining → Released`；Sealed/用途批准由外部 Owner 持有，Loaded 不等于激活。

### 5.3 错误码语义

以下稳定类别和附录 A 的 `VariationError` 是模块错误键；平台错误码映射另行采纳。不得以空区域、空结果或 `false` 代替错误。

| 错误类别 | 语义与调用方动作 |
|---|---|
| `InvalidParameter` | 类型、非有限/负阈值、配对长度或跨字段关系非法；修正请求，不重试原快照 |
| `UnsupportedInput` | 多通道/real/不支持像素类型、未支持模型能力；调用方明确转换或拒绝，不静默转型 |
| `ReferenceMismatch` | 尺寸、姿态格、方法/模型修订不一致；重新定位或提供匹配模型 |
| `IncompleteSupport` | R/采样足迹缺采、坏点或域未知；返回 U 或拒绝训练，不填零或缩 D |
| `InsufficientTrainingSet` | 样本资格、数量或非退化要求不满足；补充独立合格样本或选择已批准 Direct 来源 |
| `ModelStateInvalid` | 未训练/未 prepare/训练资料已清却要求重训或读回；销毁工作实例并按完整来源重建 |
| `ResourceBudgetExceeded` | 分配/并发/输出预算不足；排队、缩减经批准的并发或提高经审核预算，不抽样 |
| `Cancelled` / `DeadlineExceeded` | 请求被取消或等待预算到期；返回后仍检查 drain 状态，不能释放 native 正在使用的资源 |
| `AdapterFailure` | AsunImage 公共调用失败或结果形状异常；隔离实例、保留原模型并记录算子/版本/参数摘要 |
| `PersistenceFailure` | 候选字节写入、封存、物化或 fresh 读回失败；不激活，不覆盖上一模型，按原资产回执恢复 |
| `InternalFailure` | 未分类模块异常；返回关联 ID、诊断信息和可否重试标志，不映射成“无差异” |

## 6. 取消、超时、线程与资源

- 取消阻止尚未派发的样本/块和后续步骤；仅当公共适配 API 明确支持可中断执行时才声称 native 计算可中断。同步 HALCON 调用尚未返回时必须保持输入帧、模型实例、临时图及适配器租约。
- 超时先发 `DeadlineExceeded` 诊断并使 operation 进入等待排空语义；停止后续派发。只有 native 退出、`Drained` 且资源归还后才发最终 `TimedOut`；后台工作仍计入并发/内存预算。不可用 `Task.Run` 后丢弃任务来伪造已停止。
- 每个可变 Variation Model handle 由一个工作 owner 独占；同一 handle 的 train/prepare/clear/save/read 生命周期串行。首版比较也采用独占实例或串行租约；只有公开资料与实测证明后才允许同 handle 并发比较。
- 并行仅用于不同独立实例且受有界队列/预算约束。HALCON 算子内部并行不能推导出同 handle 可并行或资源免费的结论。WPF Dispatcher 不运行训练、比较或等待 drain。
- 关闭次序：拒绝新任务 → 通知取消 → 处理未开始队列 → 等待所有已启动调用真实退出 → 发 `Drained` → 释放本次临时物并归还帧/操作租约 → 发 `ResourcesReleased` → 发布唯一终态 → 释放实例持有的运行模型和 Adapter。关闭期限到达仍未退出时 `StopAndDrainAsync` 返回 `DrainUnknown`，operation 保持非终态；继续查询原操作，不能抢先释放或复用 native 内存。运行模型由实例持有而非每次比较销毁，其活动数量计入实例预算；Unload/关闭等该模型比较租约归还后释放。
- Adapter把原生Region转规范游程、诊断图转真实类型托管复制，输出maxBytes/maxRuns须在物化前检查；原生对象成功/失败/取消路径均由Adapter待实际退出后释放。Core结果不含HALCON对象或输出租约；实际公开类型/封送歧义在Adapter消费编译核定，不让Core或UI持native对象。

## 7. 模型、兼容与 Adapter

模型身份绑定精确字节 hash、模型格式、像素类型/尺寸、参考格、预处理/配准方法引用、训练集合及资格引用、阈值快照、HALCON/AsunImage 适配器能力版本和实际查询能力。不得用 `latest`、路径同名、模型标签或版本号代替内容身份。

外部资产保持三个不同闭包：运行闭包为native包+参考格/R/D/I+成像/处理/配准/适用性+A/B/方向+精确依赖；重建闭包为原训练/Direct素材+资格/真值/组/顺序+转换/合成来源；证据闭包为实际i/v/上下阈值+曝光/独立评价+资源/读回报告。它们沿原Owner保持，不由模块新建Store或把报告写回核心造成hash循环。Direct不保存i/v，清训练后不能get/续训；所需证据在不可逆边界前复制，来源仍可重建。候选暂存技术预检与外部封存后ProductionRead fresh报告分开：任何暂存预检不能替正式读回，封存/写事实Unknown按原事务身份查询，不新键盲重试或删除可能被引用证据。

可选的 prepared-handle 内存缓存只能作为 Adapter 内部优化，不能成为第二模型注册表或改变公共结果。缓存键必须由精确模型内容 hash、Variation 方法/阈值/参考格等不可变 profile hash、HALCON runtime 修订及 Adapter 能力修订共同构成；任一部分缺失、改变或运行时漂移时拒绝命中，不按路径、显示版本或 `latest` 回退。缓存项只读，按单调 generation 发出有界租约；候选训练/prepare 使用隔离工作 handle，不得修改缓存项。Inspect 热路径只允许在已验证租约上 compare，禁止隐式训练或 prepare。淘汰/撤销先停止该 generation 的新租约，再等待现有 compare 真实退出并排空，最后释放 handle；排空前缓存项仍计入句柄和内存预算。缓存未配置时直接加载精确模型也必须保持同一结果语义。

Core 公共契约遵循语义化版本：兼容新增可选能力/诊断字段可在同一主版本内演进；改变阈值含义、支持域、亮暗槽序、所有权、取消或终态语义属于破坏性变化，提升主版本并提供旧模型读取/拒绝迁移的明确路径。适配器声明其支持的像素类型、模式、查询项、并发方式、保存/读回能力；未知能力明确拒绝或返回 `Unsupported`，不猜测。

HALCON 26.05 手册定义原语行为，Adapter 经 `ImageLibDotNet.cv2` 调用；Core 不引用视觉程序集。只对实际存在的 C# 类型/重载/封送歧义查公共签名或消费编译，不检查 AsunImage 内部、不重复核验算子存在，不另接 HalconDotNet/halcondotnet.dll。未完成的真实适配和 native Golden 只阻该适配/资格切片。

### 7.1 独立 Adapter 装配与资源 Owner

N1/N2的公开工厂、Options、暂存端口唯一按附录A.6冻结。一般Host调用`AsunImageVariationModule.Create`获得同一`IVariationInspectionModule`，无需产品Shell、静态当前对象或WPF初始化；需要组合自有Core装配时调用`AsunImageVariationBackend.Create`再传Core的`VariationModule.Create`。两入口均在本模块Adapter DLL实现，不等待主控补自有接口；共享solution/正式产品端口接线仍由主控串行处理。

| 资源 | 唯一Owner、交接与退出 |
|---|---|
| Core/module与Backend | Core.Create成功时独占接收backend所有权，失败时调用方仍拥有backend；成功后禁止共享到另一个Core或由Host直接Dispose。组合工厂自己创建backend，若Core构造失败则在返回异常前回滚该尚无native工作的backend；无半构造module返回。构造只校验/复制不可变元数据，挂载有界调度，成功交接前不派发worker、不取得帧/暂存文件、不创建native handle，因此回滚不需要等待native |
| FrameSource、ScratchStore、TimeProvider | Host借给模块，不转移服务所有权、不由模块Dispose；Host在Drained且module Dispose完成前保持端口及其上游资源可用。每次Acquire/Create取得的独立lease则分别交给Core/Adapter，直至真实退出/释放确认；父帧和Host目录从未转移 |
| IBackendModel及内部图/tuple/Region | Backend创建的模型交Core工作实例或Loaded表独占持有；Backend负责其native内容，不对Host暴露。Core只在借用者退出后调用模型DisposeAsync；Backend不得在最终Dispose时绕过未退调用。每步临时图/数组/诊断Region由Adapter在该步真正返回前释放；失败/取消也一样，未知释放保持原操作DrainUnknown |
| Native序列化暂存 | Adapter经ScratchStore申请独占lease，仅访问该AbsolutePath；Serialize写完整→关native/文件IO→核长度/hash→有界托管复制，ReadFresh写入已核payload→闭流→用独立read句柄读取→释放暂存lease。每次read禁缓存且不改旧句柄；写/读/取消失败先清新句柄再释放暂存。不得默认拼系统temp路径、覆盖原模型、整目录清理或把暂存当正式封存 |
| 结果、候选与外部封存 | 有界托管复制交Host，无native输出lease；Host保存/封存/用途批准仍外部Owner。暂存文件/handle不随ModelPackage逃逸；Dispose未确认的路径/字节仍记预算及原operation，不能把删除失败只记日志后报ResourcesReleased |

Adapter.GetCapabilities的ContractVersion固定0.2、IsSimulator=false、BackendRevision来自本模块程序集的确定修订、HalconRuntimeRevision来自实际运行信息，不能由Host随意填写。PixelTypes固定Byte/Int16/UInt16，Methods固定Standard/Robust/Direct；ReadableDiagnostics列实际可读取项，单个模型不适用项仍按Unsupported返回。能力还必须兑现IVariationBackend全部入口、保存/fresh读回、单模型串行和有界复制；实现缺项不得以声明能力绕过N1/N2测试。NumericEncodingEvidence须对应实际复制语义和fixture，资源预留按A.6显式规则；没有适用规则在native前ResourceBudgetExceeded，不把模型理论存储当全峰值或把未知暂态当0。

工厂参数非法同步抛ArgumentException（null为ArgumentNullException），构造内部失败保持原异常且已创建资源回滚；此时没有operation/生产副作用。创建成功后的Acquire、scratch申请、native执行、释放失败全部走附录A.3原operation/排空链。Backend.DisposeAsync仅在Core确认所有调用、模型及暂存lease已归还后结束；否则等待实际退出，module的有限StopAndDrain返回DrainUnknown并由§4.4原Owner保留。工厂成功不是native/性能验收，本轮没有运行这些路径。

HALCON 26.05 本地证据页：`halcon算子手册/operators/{create_variation_model,train_variation_model,prepare_variation_model,prepare_direct_variation_model,compare_variation_model,compare_ext_variation_model,get_variation_model,get_thresh_images_variation_model,clear_train_data_variation_model,clear_variation_model,read_variation_model,write_variation_model}.html`，目录 `toc_inspection_variationmodel.html`。重点约束：输入类型为 byte/int2/uint2；Robust 训练需全集合一次调用，再调用会替换先前训练；训练成员上限 65,535；prepare 阈值序列长度为 1 或 2 且非负；direct 必须由直接理想图/变化图准备；`light_dark` 返回顺序为亮、暗；clear training 后不能继续训练或读取训练理想/变化图。内部统计精度/分母/MAD 常数及阈值量化未知时必须用实际读回和 Golden 验证，不能用本地自算替代 HALCON。

## 8. 可选 UI 契约

本节就是模块可选工程控件的 PageContract，不借宿主页面补缺。角色为工程调试人员；生产调用方可以完全不部署 UI。任务链：选择冻结训练/资格与用途→核支持/分组→编辑方法草稿→校验/训练→样本与 i/v/阈值/候选联动→有限阈值建议→显式采用到草稿→独立评价→交候选给宿主。交候选、资产封存、资格批准、程序发布/生产激活是不同动作，模块不执行后四项。

### 8.1 1920×1080 构图与 DevExpress 组合

只用固定1920×1080物理验证viewport；先扣OS任务栏、边框、标题/状态栏，按实际client可用DIP布局，不改显示设置、不另跑分辨率矩阵。基准主题沿宿主匹配25.2.3主题；模块不设置全局ThemeManager。主命令栏48DIP、底状态28DIP；剩余工作区横向17%样本/来源、62%图像、21%参数，面板间距8DIP、内部8DIP，标题14DIP半粗、内容13DIP，数值对齐且保留单位。下方诊断区占工作区高度约22%，可折叠；图像仍优先，不能以四排状态卡侵占影像。

| 区域 | 固定控件组合及行为 |
|---|---|
| 工作台 | `DevExpress.Xpf.Docking.DockLayoutManager` + `LayoutGroup`、`LayoutPanel`；稳定Name为Samples/Images/Parameters/Diagnostics。Samples/Parameters可收起，Images不能关闭；保存/恢复使用已查到的SaveLayoutToStream(Stream)/RestoreLayoutFromStream(Stream)，只读本宿主可信布局，应用前核布局修订/面板ID，失败保留原文件并恢复本节默认布局，不改变方法/模型/事实 |
| 样本区 | `GridControl`+`TableView`，ItemsSource为只读样本投影，SelectedItem只代表当前行，训练成员由独立勾选集冻结；列为用途、来源组、资格、支持、修订。ShowGroupPanel=false默认，按来源/用途分组是工具栏明确命令；AutoWidth=false保留列最小宽/横滚动，内容列可截断但完整值可复制。大列表虚拟化，缩略图按可见行加载且有界，不把所有训练像素塞VM |
| 来源树 | Diagnostics中的`GridControl`+`TreeListView`显示模型→方法→来源/资格引用；不把树选择等同批准。树/表/图统一绑定不可变ContentReference，不按行号关联 |
| 主图 | 已有公共视口经宿主注入，每控件独立presenter；上方原图/理想/变化/下阈/上阈模式条，核心区域单主图；需要对照时才切双图50/50且共用参考格、同步缩放/游标。原图不变，Light青色/Dark橙色以图例及标签区分；Unknown紫色斜纹，N透明，不只靠红绿。点击表行定位该参考格，移动游标显示同位置原灰度/阈值/响应，Unsupported显示“此模型不提供该图”，不显示黑图 |
| 参数栏 | `PropertyGridControl`绑定独立草稿SelectedObject、PropertyDefinitions显式列出方法/方向/A亮/A暗/B亮/B暗；ShowCategories按Basic/Advanced显示。参考格/处理链/位深/来源/资源为只读高级项。阈值数字草稿允许未完成输入，失焦不静默归零；采用时同一Core Validate。改A/B只标旧结果过期，不每键重训；基本栏保留主要命令，不把关键操作藏Flyout |
| 诊断区 | `GridControl`显示候选ordinal、冻结A/B、误报/漏检/Unknown、真实正例数和选择理由；`ChartControl`只展示已测候选/阶段耗时，SelectedItem联动同一ordinal，CrosshairEnabled=true显示样本数/单位；不可把未知画成零、不同profile时延排成“最佳”。曲线/表选择只预览，不自动采用建议 |
| 命令/说明 | `BarManager`/`BarButtonItem`承载“校验、训练、比较、参数建议、独立评价、提交候选、取消”；每次只突出当前安全下一步。`SuperTip`说明阈值/Direct/训练来源影响和恢复；非关键高级说明用`DevExpress.Xpf.Editors.Flyout.FlyoutControl`，按PlacementTarget锚定，Escape关闭不提交。错误与Unknown另有固定可见摘要，不只悬停 |

主内容宽不足1400DIP（同1920物理viewport的DPI/窗口chrome原因）时，Parameters收为右侧dock标签、Samples保留可恢复标签；图像占当前client至少60%宽。不能隐藏取消、资源占用和当前状态。长英文字串局部换行/滚动；hash以短显示+复制完整值，参数值/单位和主要命令不能截断。布局恢复不能浮出当前验证viewport，无法放下时恢复安全dock。高级图表/树只有对应诊断存在才展示，不造模拟数据填空。

### 8.2 控件公开面与状态

WPF命名空间 `Asun.Modules.VariationInspection.Wpf`；`VariationInspectionControl : UserControl, IAsyncDisposable` 构造 `(IVariationInspectionModule module, IVariationImagePresenter presenter, IWorkspaceOperationHeaders headers)`。module由Host拥有/控件借用；presenter是此控件独占实例，由控件卸载归还。`IWorkspaceOperationHeaders`提供 `RequestHeader Next(string requestRevision)`，Host为共享module提供同一个接纳协调器：UI/服务在同一协调线程连续Next→调用module入口，不在Next后await，不让多个控件各自生成Sequence。deadline由Host当前明确Profile预算计算，Revision用当前冻结草稿/输入修订；错误不默认无限。异步native工作仍由Coreworker执行。`IVariationImagePresenter : IAsyncDisposable` 提供 `FrameworkElement View { get; }`、`ValueTask PresentAsync(WorkspaceImageProjection projection, CancellationToken ct)`；只消费公开帧/诊断/区域，不泄露native对象。`WorkspaceImageProjection`字段 `long ViewEpoch, FrameReference? Frame, DiagnosticImage? Diagnostic, ComparisonResult? Overlay, bool IsStale`，Frame/Diagnostic至多一项非null、Overlay同参考格，呈现不等算法完成。

控件方法：`Configure(WorkspaceInput input)`、`ApplyPresentation(WorkspacePresentation presentation)`、`ValueTask<DrainReceipt> DetachAsync(DateTimeOffset deadlineUtc, CancellationToken ct)`；`event EventHandler<CandidateReadyEventArgs>? CandidateReady`只传给宿主，不作资产IO。`WorkspaceInput`字段为 `TrainingSnapshot? Training, RuntimeModelToken? Runtime, FrameReference? PreviewFrame, ImmutableArray<LabelledFrame> Validation, ImmutableArray<LabelledFrame> IndependentTest, ExposureHistory Exposure, ImmutableArray<MethodSnapshot> SuggestionCandidates, SelectionPolicy Selection, VariationResourceBudget Budget, bool CanHandoff`；Profile/真值来自Host，CanHandoff只是可见性/操作资格投影，不代实际Host授权。`WorkspacePresentation`为 `string CultureName, string ThemeName, ImmutableDictionary<string,string> Resources`，资源包含本节全部控件/参数/状态/错误/提示键；默认三语、可扩展文化，不在控件重复放语言菜单。

`CandidateReadyEventArgs : EventArgs`只读 `Guid IntentId, VariationModelCandidate Candidate`，构造同两字段。提交候选只发一次当前草稿代的Intent，宿主自行按原事务保存/查询；事件异常显示“宿主未接收候选”，不释放尚未交接的托管包、不自动重新发起存储。控件不显示“已发布/已激活”。Host无监听者时提交命令不可用且明确“宿主未接入提交”；无UI候选由API直接返回，不受事件影响。

状态为草稿/已校验/训练中/比较中/评价中/等待排空/候选可交接/过期/错误。运行命令时复制冻结快照并禁重复发起同命令，保留取消；用户可继续编辑下一草稿，但旧Operation不改参数。每次输入/草稿/图像变化增加ViewEpoch，A→B→A第一次A也过期。拉取Query/ReadEvents投影最多10Hz，图像呈现一项在途+一项最新待呈现；旧图真实退出后再释放帧/诊断引用，不占native worker线程、不在Dispatcher同步wait。终态由Completion读取，不依赖进度刷新或丢序事件。

Unload/Detach先停止本控件新命令、撤自身事件及timer、增加ViewEpoch，取消本控件创建的操作/呈现→等待真实退出→归还自身presenter/托管引用；不调用借用module的StopAndDrain/Dispose、不取消另一宿主操作。未退出则Detach回DrainUnknown并保留Query入口；真实归还前不声称控件已释放。宿主关闭Core按§6独立执行。

### 8.3 键盘、三语与恢复

Tab顺序：样本用途/选择→图像模式/视口→基本参数→主命令→诊断→状态。F6在四面板循环，Ctrl+Enter执行当前明确主命令（IME组合/参数无效时不执行），Escape只关闭Flyout/编辑弹层，不暗中取消算法；取消命令Alt+C带清楚按钮。焦点可见、AutomationId稳定不翻译；资源变更不重建编辑控件、不丢caret/草稿/选择，数值解析文化冻结到采用/取消，UI文化切换不重新解释A/B。危险/未知不靠动效强调：无支持显示固定U和“检查输入或重新采图”，读回错显示精确包修订并“重新读取指定模型”，取消显示“正在等待当前步骤结束”，继续保留资源计数。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Variation.Title | 图像差异 | 影像差異 | Image differences |
| Variation.Train | 训练 | 訓練 | Train |
| Variation.Compare | 比较 | 比較 | Compare |
| Variation.Suggest | 参数建议 | 參數建議 | Suggest parameters |
| Variation.Evaluate | 独立评价 | 獨立評估 | Independent evaluation |
| Variation.Handoff | 提交候选 | 提交候選 | Submit candidate |
| Variation.Cancel | 取消 | 取消 | Cancel |
| Variation.Incomplete | 输入支持不完整 | 輸入支援範圍不完整 | Input coverage is incomplete |
| Variation.Draining | 正在等待当前步骤结束 | 正在等待目前步驟結束 | Waiting for the current step to finish |
| Variation.Stale | 参数已变化，结果已过期 | 參數已變更，結果已過期 | Parameters changed; result is out of date |
| Variation.UnsupportedGraph | 此模型不提供该图 | 此模型未提供此圖 | This model does not provide this image |
| Variation.InvalidThreshold | 阈值须为非负有限值 | 閾值須為非負有限值 | Threshold must be finite and nonnegative |

资源完整性预检缺关键键拒绝应用新呈现包、保留旧包；参数/列头/方向/质量/错误/恢复/图例/图表单位均纳入同目录键，新增词条不写在VM字串中。真实WPF检验固定viewport、当前OS DPI记录、三语长度、键盘/UIA、dock恢复、IME及取消/关闭竞态；本轮仅API/规格研究，未运行控件，不以XML成员存在证明交互/性能通过。

错误资源固定`Variation.Error.<VariationError>`；恢复键固定`Variation.Recovery.<VariationError>`，一个错误键可共享下表同一自然文案但所有枚举均有映射，禁止直接显示enum或exception.ToString。错误旁同时显示操作阶段/输入修订/关联Key。状态映射`Variation.State.<OperationState>`；Validating/Accepted/Queued分别“校验中/已接收/等待执行”，Running使用当前训练/比较/评价阶段，Draining/DrainUnknown同显示等待当前步骤并区分资源未知；Drained/ResourcesReleased作为诊断事件，主要状态只在Completion后显示完成/取消/超时/失败，Unknown绝不显示失败已释放。繁中/英文分别“驗證中/已接收/等待執行”和“Validating/Accepted/Queued”，终态“完成/已取消/逾時/失敗”和“Completed/Cancelled/Timed out/Failed”；API拼写不由翻译改动。

| 错误键后缀 | zh-CN / zh-TW / en-US | 安全恢复（对应三语资源） |
|---|---|---|
| InvalidParameter | 参数无效 / 參數無效 / Invalid parameter | 检查标出的参数 / 檢查標示的參數 / Check the highlighted parameters |
| UnsupportedInput | 输入类型不支持 / 不支援此輸入類型 / Unsupported input type | 提供匹配输入 / 提供相符輸入 / Provide a matching input |
| ReferenceMismatch | 参考版本不匹配 / 參考版本不符 / Reference version mismatch | 选择指定参考版本 / 選取指定參考版本 / Select the specified reference version |
| IncompleteSupport,InputNotQualified | 输入未满足检查条件 / 輸入未符合檢查條件 / Input does not meet inspection conditions | 检查输入支持和质量 / 檢查輸入範圍與品質 / Check input coverage and quality |
| InsufficientTrainingSet | 缺少独立良品样本 / 缺少獨立良品樣本 / Independent good samples are missing | 补充合格独立样本 / 補充合格獨立樣本 / Add qualified independent samples |
| ModelStateInvalid | 模型状态不适用 / 模型狀態不適用 / Model state is not suitable | 从冻结来源重建候选 / 從凍結來源重建候選 / Rebuild the candidate from frozen sources |
| ResourceBudgetExceeded | 资源额度不足 / 資源額度不足 / Resource budget exceeded | 等待资源归还或调整预算 / 等待資源歸還或調整額度 / Wait for resources or adjust the budget |
| Cancelled | 任务已取消 / 作業已取消 / Operation cancelled | 用新请求重新执行 / 以新請求重新執行 / Start a new request |
| DeadlineExceeded | 已超过等待期限 / 已超過等候期限 / Deadline exceeded | 查看排空状态 / 查看排空狀態 / Check the drain state |
| AdapterFailure,InternalFailure | 当前步骤执行失败 / 目前步驟執行失敗 / The current step failed | 查看诊断和资源状态 / 查看診斷與資源狀態 / Check diagnostics and resource state |
| PersistenceFailure,ReadBackMismatch | 模型读取或核验失败 / 模型讀取或驗證失敗 / Model read or verification failed | 重新取得指定模型 / 重新取得指定模型 / Retrieve the specified model again |
| DuplicateConflict | 请求编号已用于其它内容 / 請求編號已用於其他內容 / Request ID was used for different content | 使用新请求编号 / 使用新請求編號 / Use a new request ID |
| RequestExpired | 请求记录已释放 / 請求記錄已釋放 / Request record was released | 使用新请求编号 / 使用新請求編號 / Use a new request ID |
| ModuleClosing | 模块正在关闭 / 模組正在關閉 / Module is closing | 等待关闭完成 / 等待關閉完成 / Wait for shutdown |
| NoFeasibleCandidate | 没有满足条件的候选 / 沒有符合條件的候選 / No candidate meets the conditions | 检查候选范围和样本 / 檢查候選範圍與樣本 / Check candidate bounds and samples |

参数资源键`Variation.Parameter.<MethodSnapshot字段/子字段>`至少包括“模式/模式/Method、方向/方向/Direction、亮绝对阈值/亮絕對閾值/Light absolute threshold、暗绝对阈值/暗絕對閾值/Dark absolute threshold、亮变化系数/亮變化係數/Light variation factor、暗变化系数/暗變化係數/Dark variation factor、参考格/參考格/Reference grid、处理链/處理鏈/Processing chain、位深/位元深度/Bit depth”。范围/单位取§3不从译文解析；Light/Dark/Absolute/LightDark分别亮/暗/双向合并/亮暗分槽，繁中同语义，en-US Light/Dark/Combined/Separate light and dark。Unknown图例“未评价/未評估/Not evaluated”，真值来源“真实/真實/Real、合成/合成/Synthetic、解析/解析/Analytical”；Variation.NonFiniteDiagnostic为“诊断图含非有限值/診斷圖含非有限值/Diagnostic image contains non-finite values”，工程建议未评价为“仅工程建议，真实样本未评价/僅工程建議，真實樣本未評估/Engineering suggestion; real samples have not been evaluated”。


### 8.4 U1公开装配补充：会话、图像来源与原样检查

本节是2026-10-11的U1增量规格，已由主控限定内容接收；§8.1–3既有控件构造、WorkspaceInput/Presentation、CandidateReady和共享Core边界不变。C1～C4/API v0.2及固定向量不修改。下面新增类型仅在Wpf DLL；声明省略实现体，不表示已编译。所有Options必填、不可变复制，constructor/factory无文件/帧读取、Bind/Attach、native或Dispatcher异步工作；失败不接收借用对象所有权。控件必须在自己的STA Dispatcher构造，业务Core仍无UI。

```text
namespace Asun.Modules.VariationInspection.Wpf
enum WorkspaceAction { Inspect, Train, Suggest, Validate, CompareExisting, Handoff }
record WorkspaceAccessReceipt(bool Allowed, string AuthorityRevision,
    DateTimeOffset ValidUntilUtc, string? ReasonResourceKey)
interface IVariationWorkspaceAccess
    ValueTask<WorkspaceAccessReceipt> CheckAsync(WorkspaceAction action,
        string inputRevision, CancellationToken ct)

record WorkspaceSessionOptions(string SessionId, int MaxTrackedCalls,
    long MaxRetainedBytes, int MaxCleanupErrors, TimeSpan ObservationWait,
    TimeSpan CleanupExecution, int MaxRecoveryTicks)
record WorkspaceSessionObservation(string SessionId, bool AdmissionClosed,
    bool Detached, bool ResourcesReleased, ImmutableArray<string> PendingCallIds,
    ImmutableArray<string> CleanupResourceKeys)
class WorkspaceOperationHeaders : IWorkspaceOperationHeaders
    static WorkspaceOperationHeaders CreateForNewInstance(IVariationInspectionModule module,
        TimeProvider timeProvider, TimeSpan requestDuration)
class VariationWorkspaceSession : IAsyncDisposable
    static VariationWorkspaceSession Create(WorkspaceSessionOptions options,
        IVariationInspectionModule module, IVariationImagePresenter presenter,
        IWorkspaceOperationHeaders headers, IVariationWorkspaceAccess access,
        TimeProvider timeProvider)
    VariationInspectionControl Control { get; }
    WorkspaceSessionObservation Query()
    ValueTask<WorkspaceSessionObservation> CloseAsync(DateTimeOffset deadlineUtc,
        CancellationToken waitToken)
```

Control新增实例方法`ConfigureReference(RuntimeModelToken? runtime)`，仅保存原模型比较用的可选token；null清除，无Load/IO且无Core/API改变。必须与Configure在同Dispatcher串行，token的InstanceId同module、PackageHash/MethodHash完整，用途沿A.4；变化增加ViewEpoch，原比较过期。两个Compare各自冻结header/token/同Input，单项失败/支持未知按原结果保留，不做差值质量判定；两项均有结果才并列显示并逐列标包/方法/原模型身份。没有reference token时“与原模型比较”不可用。

WorkspaceOperationHeaders.CreateForNewInstance仅供新建未派发实例：从GetCapabilities读取InstanceId，sequence从1开始，checked递增耗尽拒绝；requestDuration正且有限。Host记录首次调用后禁止第二CreateForNewInstance，所有UI/服务共享同一headers及协调线程，不能在已用实例上重置Sequence；借用已运行module必须注入其现有headers。Next只按当前明确时间+requestDuration产生有限DeadlineUtc，不发起Task；连续Next→入口无await规则仍§8.2。

Create先校验options/端口/Dispatcher→创建空控件/内部有界调用账→成功返回session，成功时独占接收presenter，module/headers/access/clock仍借用；直接构造旧Control也沿§8.2卸载规则，Host须在Configure前登记其强保持权。Session只是本控件的任务/呈现/卸载Owner，不是第二算法入口、资产服务或Core生命周期Owner。MaxTrackedCalls至少6（命令/授权/呈现/Detach/Dispose与恢复保留槽），MaxRetainedBytes/MaxCleanupErrors/MaxRecoveryTicks均正；两个期限正且有限、ObservationWait≤CleanupExecution，来自宿主软件预算，不是客户节拍。资源不足在发起原调用前拒绝；独立关闭保留槽不能被普通命令吃完。pending项不淘汰，不因查询再建Task。Close在首次调用封门/取消自身操作/递增ViewEpoch并创建唯一detach工作，重复Close只有限观察同一工作；外部waitToken只撤本次等待，执行期限按单调时钟固定、不被重试重置。DisposeAsync只能在Query.ResourcesReleased=true后作为一次终结；不是无期限关闭捷径。Session不Stop/Dispose借用Core。

命令调用先在session有界账预留原授权Task/请求修订→CheckAsync→本Dispatcher复核ViewEpoch/权限有效期/输入未变→同步Next→module入口→立即登记原operation handle/Completion。授权Unknown、Denied、取消、超期或迟到禁止进入模块，不以旧CanHandoff=true补许可；CanHandoff仍只是可见性。CheckAsync实现须一次返回原ValueTask并保持原权限服务Task，Allowed只表示这个工程动作准入，不授予保存/用途批准/质量放行。撤权后封该输入新命令、撤受限旧图及未接收候选，原操作仅请求取消并沿原Owner排空；不会销毁已确认资产或改旧模型。Handoff事件前再CheckAsync(Handoff)，宿主收到候选后仍按其原资产/用途authority执行。事件未被宿主接收或抛错按§8.2保留原Intent，不重发存储。

| 独立任务 | 输入及入口；冻结后下一步 | 图/表/图表联动与不可越界项 |
|---|---|---|
| 独立训练 | TrainingSnapshot→ValidateTraining→BuildCandidate→CandidatePreview Load | 样本勾选冻结在用途/来源组，主图当前样本，诊断i/v/阈值。训练可独立完成并查看候选，不强迫先推荐参数 |
| 参数推荐 | 原冻结训练/Validation/Candidates/Selection→Recommend | Grid/Chart都按CandidateScore.Ordinal联动；表列A/B、真实良/坏数量、漏检/误报/Unknown与失败。显式“采用参数”只改下一草稿，原结果过期；不改已加载模型 |
| 独立验证 | 明确Validation或IndependentTest→Evaluate，Exposure必须保留 | 逐样本结果/真值/完整支持与未执行分母可追溯；最终测试不得回流推荐；完成不等接受/生产批准 |
| 原样检查（Inspect） | 现有Runtime+PreviewFrame→Compare；必要诊断→ReadDiagnostics | 不Train/Prepare/重建/改方向A/B/缩D；保留包/方法/hash/输入身份。无Runtime时要求明确装载，不能偷偷训练。工程CandidatePreview或正式ProductionRead按原用途使用 |
| 与原模型比较 | 宿主显式提供两个已Load的Runtime，Configure选择当前模型，ConfigureReference选择原模型，控件冻结两次Compare意图 | 当前与原模型对同一FrameReference逐次Compare，控件两原Completion取得的托管结果只读并列亮暗/E/N/U和身份。不能算“改善”后自动替换；装载由无UI原Load承担，失败不替换旧token |
| 交候选 | 当前不陈旧candidate+Handoff授权→原CandidateReady一次 | 仅显示“候选已交给宿主”或未接收，不显示已封存/激活。无监听者禁用；asset/quality按钮不塞本控件 |

“原模型比较”不新增Core或WorkspaceInput字段：新增Wpf ConfigureReference只绑定Host已Load的reference token，两结果在同控件诊断区通过两列组和同格双图展示，各列绑定自己的包/方法/token，不冒充另一个token的结果。原模型包不支持i/v时保持Unsupported；不读取训练图重造原模型图。主命令栏同时保留五项任务入口与取消，当前任务用明确选中态；Dock默认仍§8.1的17/62/21与下方22%，不添加五张重复页面。样本行/诊断候选/Chart ordinal/视口共用冻结身份，切选A→B→A不复用第一次A的呈现；长包身份复制完整值，三语补键如下。

| 键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Variation.Inspect | 原样检查 | 原樣檢查 | Inspect unchanged |
| Variation.CompareExisting | 与原模型比较 | 與原模型比較 | Compare with original model |
| Variation.ApplySuggestion | 采用参数 | 採用參數 | Apply parameters |
| Variation.AccessDenied | 无此操作权限 | 無此操作權限 | Permission denied |
| Variation.CandidateHandedOff | 候选已交给宿主 | 候選已交給宿主 | Candidate handed to host |

#### 8.4.1 公共viewport presenter与图像来源

直接复用[viewport 0.3.5-prep §10.6～10.9/15.2.2.1](../viewport/DEVELOPMENT-GUIDE.md)的WPF Assembly Contract v0.2与[ImageFrame§4.3](../image-frame/DEVELOPMENT-GUIDE.md)。以下是本模块Wpf接入薄桥，不另造renderer/缓存/源事实Owner。namespace仍为Asun.Modules.VariationInspection.Wpf；Viewport类型来自Asun.UI.Viewports/Asun.UI.Viewports.Wpf，CPU源生产者来自Asun.UI.Viewports.ImageFrame，Frame服务来自Asun.Modules.ImageFrame.Resources。此处是目标声明，不声称现有二进制已实现这些入口。

```text
record WorkspaceImagesOptions(string ConsumerId, int MaxFrames,
    long MaxCopiedBytes, int MaxRegionRuns, TimeSpan ReadTimeout,
    TimeSpan ReleaseObservation, int MaxRecoveryTicks)
record WorkspaceFrameBinding(FrameReference Reference,
    ImageFrame.Resources.FrameDescriptor Descriptor, int PlaneIndex)
class VariationWorkspaceImages : IAsyncDisposable
    static VariationWorkspaceImages Create(WorkspaceImagesOptions options,
        ImageFrame.Resources.IFrameService frames,
        ImmutableArray<WorkspaceFrameBinding> bindings,
        Viewports.IViewportProcessRoot root,
        Viewports.ImageFrame.ViewportImageFrameSourceOptions sourceOptions,
        Viewports.LutWindow displayWindow, TimeProvider timeProvider)
    Viewports.IFramePort Frames { get; }
    Viewports.ICoordinatePort Coordinates { get; }
    Viewports.IProbePort Probe { get; }
record VariationViewportPresenterOptions(string BindingId,
    Viewports.AuthorizationSnapshot Access, Viewports.ViewState InitialView,
    Viewports.Wpf.ViewportUiResources Resources, TimeSpan ObservationWait,
    TimeSpan CleanupExecution, int MaxRecoveryTicks,
    Viewports.Wpf.IViewportUiLifetimePort Lifetime,
    Viewports.Wpf.ViewportUiExecutionBudget ExecutionBudget)
class VariationViewportPresenter : IVariationImagePresenter
    static VariationViewportPresenter Create(VariationViewportPresenterOptions options,
        Viewports.Wpf.ViewportControl control, Viewports.IViewportSession session,
        Viewports.IViewportProcessRoot root, VariationWorkspaceImages images)
    Task<Viewports.PortResult<string>> SetResourcesAsync(
        Viewports.Wpf.ViewportUiResources resources, TimeSpan timeout,
        CancellationToken ct)
```

这些缩写在实施时使用上述完整namespace别名，不能当新命名空间；Wpf WorkspaceFrameBinding仅用于显示源（诊断还支持Real32/Real64），原输入的身份/plane映射遵循A.7的同一规则，SourceKey准确取Descriptor.Key；不引用Adapter DLL或视觉SDK。images只借frames/已登记父帧，presenter只借root/session/images，独占当前control的绑定；View返回注入control（同一个FrameworkElement），控件不能已挂其它父元素/已绑定别处。构造无源获取；所有数量/字节上限正、集合非default且唯一，Read/Release及呈现/清理期限有限，时间规则同8.4。成功未Bind的presenter也必须可Dispose而不Attach；失败不关借用session/root/images。images.Dispose在全部presenter退出后才能完成，不关闭frames；pending发布/读/lease/retireTask保留，不把GC当归还。

Host顺序固定为ViewportRootFactory().Create(rootOptions)→同STA的new ViewportControl()→ViewportRendererFactory.Create(control,root,显式ViewportRendererOptions)→VariationWorkspaceImages.Create（内部一次ViewportImageFrameSourceFactory.Create(frames,root,sourceOptions)）→root.CreateFactory().Create(viewportOptions)。逐个PortResult核Succeeded+Value后保存强引用，失败不继续；Backend=同renderer.Backend、Presentation=同control.Presentation（稳定门面直接返回原Commit Task，不加async包装）、Frames=images.Frames、Coordinates=images.Coordinates、Probe=images.Probe，Authorization注入可信原端口；ReadOnly、Navigation|Probe|Presentation，Roi/Surface=null。所有options按上游公开形状给，不能用空port启用能力。离线无共享池可显式BudgetOnly/OfflineRasterOnly，生产/共享物理池Required/HalconRequired；本控件不代签permit，资源/权限失败不降为离线成功。

本presenter第一次Present才调用并保存原BindAsync(session,root,new ViewportUiBindingOptions(BindingId,false,Resources,CleanupExecution,Lifetime:Lifetime,ExecutionBudget:ExecutionBudget),ct)，Created/generation0时按上游root保留原Bind/Dispatcher Task。Lifetime必需非null且正是前述同Control/root的renderer.Lifetime，不能因上游语法可选而省略；null在Reserve/Dispatcher前007，交叉Owner016。ExecutionBudget同样必填，正且受root/Profile限制：上游默认8MiB不作为1920×1080预算，可见读回保守峰值至少16*物理client W*H，加tile/native baseline/对象与新旧代并存，在dump/分配前预留；不填未经实测的节拍。OwnSession=false固定，Presenter退出后由Host在UI workslot之外独立关闭自己拥有的session。Bind只安装空视觉；拿到实际IViewportUiBinding后才首次AttachAsync，后续UpdateAsync(new ViewportUpdate(原BaseContextRevision,完整replacement))，Clear后仍Update；原Task与有限WaitAsync观察分开。

Frame投影按binding取得原FrameKey/plane/Content身份；直接Register时Image.SourceId/SourceRevision逐值等于原FrameDescriptor.SourceId/SourceRevision，完整Content三元组+PixelHash保留在该精确token的可信映射，不重编码父源字段。同token异内容拒绝，不拿文件名/行号推来源。诊断或选plane/显示派生帧才由images为PublishCopy明确分配独立SourceId/SourceRevision，绑定本次PackageHash/DiagnosticKind/ContentHash或原帧/plane/显示变换身份；Register仍读取真实发布回执的原字段，不在其后改名。Available诊断原值保留真实Byte/Int16/UInt16/Real32/Real64托管只读数据；若发布原值父帧则按IFrameInputRows+PublishCopyAsync有界复制，Layout/Metadata为真实存储位宽、unit=1、Scale=1、Bias=0、单通道Intensity、小端且有效域明确。Unsupported无像素发布，非有限值保留无效域/明确提示。诊断/显示副本父帧归images，原输入父帧归Host。发布原Task迟到也先接住FrameKey再Retire，失败不伪造SourceDescriptor。每个投影先预约新旧并存容量/发布槽再构造，旧generation归还后才能退役旧诊断；不能不断Publish无限源。

Frames与Coordinates直接返回上述同sourcePorts的稳定实例，不返回本模块自建IFramePayload；内置renderer仅接受此公开生产者的实际私有payload。每项完整ViewportPublishedFrameBinding先Register，BindingId与本投影唯一，PlaneIndices=[0]、level0 identity、CenterInteger、Image.CoordinateRevision/PixelSpace/Frame.CoordinateReference精确同源；source/coordinate/decode修订有界无碰撞编码，Validity保留完整支持mask，不用包围框伪Full。无定位/标定时只用本Frame的像素参考格，不编造物理单位。多plane/plane非0不能假称producer支持：images在有界scope中无损选plane发布独立单plane副本（原Content/plane映射保留），不改原源。

公开producer首版仅Gray8/Gray16/RGB8，本控件单通道：UInt8/UInt16在plane0及Layout/域完全匹配时直接Register真实父帧，不重复Publish；Image.BitsPerSample按存储8/16，与算法EffectiveBits分别记录。Int16/Real32/Real64使用明确仅供显示的Gray8派生帧：按已冻结displayWindow做q=255*clamp((raw−Minimum)/(Maximum−Minimum),0,1)，byte=floor(q+0.5)；范围/差值算术须有限，超范围截断明确提示，非有限值标无效域而不是有效黑。displayWindow.Minimum/Maximum有限且Minimum<Maximum，StatisticsRevision为非空受控显示范围修订，不声称测得统计；缺范围先拒，不自动估参。派生修订绑定原值完整身份+范围两数及修订+`variation-display-gray8/1`，pixel hash为真实副本；域为原完整支持与有限值集合交集，逐行形成规范RowSegments并先核域段/字节预算，不建全图bool mask。副本Publish确认Completed/Error=None/OperationResourcesReleased后Register实际FrameDescriptor，显示Lut固定(0,255,"variation-display-gray8/1")，不再套原signed/real范围。原输入/诊断包不变，不回灌训练/Compare或质量事实；改变显示范围须显式以新投影修订替换。Source描述真实Gray8，图旁显示原类型/范围/显示截断，诊断表仍真实原值。sourceOptions.ConsumerId与options.ConsumerId一致且已注册，MaxBindings覆盖MaxFrames新旧并存，metadata预算显式计Host Profile；所有原值/派生副本/发布与新旧代同时容量计MaxCopiedBytes及父服务账。

Probe为本images薄桥，按ProbeSourceRequest.Original的完整SourceId/SourceRevision/CoordinateRevision/Generation查当前有界映射并保持同CallContext/权限；读取原输入父帧或本次诊断原值，不读Gray8显示副本。OriginalSample在整数中心格取floor(center+0.5)，出界/域外分别Outside/MaskInvalid；成功Support单原(column,row,1)。Interpolated按原level0 floor中心的四邻及双线性权重，零权重邻点不要求，全部非零支撑有限且有效才返回Interpolated及完整原支撑，否则SupportInvalid、Value=null；不填0/最近邻补洞。ValueKind=GrayValue、Unit=GrayValue，保持原Channel/身份，不把强度当长度；Int16/UInt16/Real32/Real64按小端解码至double。真实FrameService读取、scope.CopyRow、allocation身份及Release/Query按viewport§15.2.2和A.7，预算在Read前预留；算术溢出拒绝，不报告可消费值。探针还由session交付点复核授权/代号。Coordinates仅同PixelSpace identity，不自行配准/标定。

换图固定Register新entry→Attach或完整Update→旧borrow/原Task确认Return→Remove旧BindingId→由发布Owner Retire旧key；Remove不能代Retire或归还借用父源。不每帧造新producer，不反射内部payload、不另写renderer。Overlay仅同格/同输入/同模型：PixelRun闭区间变像素边界矩形[x0,y,x1+1,y+1]，再按上游CenterInteger ROI几何记录中心/宽高，Light/Dark/Unknown分层、非交互、标签资源化，N不填色；超MaxRegionRuns拒绝叠加并显示原因，不丢游程。不做全图bool mask或按显示几何重算候选。Inspect不加算法图像变换；Fit/LUT/缩放只改显示计划。

PresentAsync确认的是此投影调用/借用实际退出；可见状态须上游PresentationReceipt.VisibleConfirmed及对应generation，不以Dispatcher完成冒充。内置renderer的HALCON/GDI读回/同Control观察复用viewport§10.8，不复制第二观察算法。binding从完整ViewportPresenterSubmission(Request,原Presentation,SourceCall)Acquire，不删原submission/授权/backend代；同请求Commit返回同原Task，不二次Acquire。本presenter只观察GetPresentations的OriginalCommit/Acquire/Confirm/Revoke/Return与Cleanup，不接收Presenter租约Owner、不另Return。迟到/失败Value中的lease由同root捕获，原Owner固定Revoke→固定ReturnId→Query原Unknown，不换Owner重取。ViewEpoch/身份过期取消本投影、撤旧呈现，新旧借用都由root留账。

Dispose只封本binding、一次UnbindAsync并观察原Task；UiUnbindReceipt.Drained及本桥读/发布/借用真退后才成功。不先Dispose session/frames，未知时session原detachTask继续持presenter、images、control和Dispatcher；外层有限Close可返ResourcesReleased=false。Bind失败若上游已Reserve仍按原root/Task留账，不因Value=null忽略已开始worker；全部归还后images移除metadata并仅Retire自己发布的key，借用父帧不退役。

完整三语资源由ViewportUiResourceCatalog.Get(language)核Succeeded+Value取得，Revision固定SchemaId=`viewport-ui-text/1`，RequiredKeys完整Ordinal集合直接复用，不传旧七键/fixture-text revision；实际Overlay.LabelResourceKey也加入同快照，通过上游每键/值/扩展数量/全UTF8限额。资源限额/原子SetResources/失败保旧包以viewport§10.9为唯一权威，不复制其表。Variation.*资源仍§8.3/8.4，新增`Variation.DisplayProjection`三语“仅显示副本 / 僅顯示副本 / Display copy”、`Variation.DisplayClipped`三语“显示范围已截断 / 顯示範圍已截斷 / Display range clipped”；LabelResourceKey使用Variation键时将其解析文字作为Host扩展键，不冒充上游内置必需键。

Host保留具体presenter的借用引用，用上述SetResourcesAsync更新viewport资源，不能从Control私有字段取binding。未开始Bind时仅按上游同一schema/限额完整预检冻结下一Bind快照，返回有界已完成Task，不读源/创建Dispatcher工作，也不声称当前已可见；Bind开始后至完成前返回Rejected/015，Host保旧完整包、在原Bind收敛后才重试语言更新。已Bind时直接返回同binding.SetResourcesAsync的原Task并登记，禁止async包装替换它；失败保持原包，Close已封门则拒绝且不复活binding。Host有限观察并强持此原Task，结束前不放开本locale快照借用。此转发不新增语言菜单/第二locale authority、不改IVariationImagePresenter/Core接口；所有实际标签键须预检，资源切换不启动像素或算法工作。

Wpf DLL因此显式引用既有Viewport Core、目标Asun.UI.Viewports.Wpf、Asun.UI.Viewports.ImageFrame与ImageFrame Core/Resources；公共依赖版本分别记录，Core仍纯BCL，不把WPF/HALCON传入Core或借用Adapter DLL。images.Create若公开producer工厂拒绝，参数错误同步ArgumentException（null为ArgumentNullException），其它构造失败InvalidOperationException带安全诊断；无部分images/IO/native/新Root返回，借用对象Owner不变。构造与Register/发布/Read仍按前文分开，不能以“入口公开”声称上游实现已经交付。

清除投影使用viewport§4.7.1：WorkspaceImageProjection.Frame/Diagnostic皆null且Overlay=null时，在已Attach的同session发空Sources/空Layers的完整UpdateAsync，new ContextRevision为当前+1，初始view保导航偏好且Profile=null，不调用Unbind/Dispose再复活。未Attach的空投影仍一次合法Empty Attach；InstallEmpty不等实际清屏。原Clear Task强持，成功须EmptyTransition.PreviousPresentationsRevoked、PreviousSourceBorrowsReturned、PreviousWorkQuiesced全部true、PreviousCleanup=Drained，UI还须本代BlankPresentation.VisibleConfirmed=true。清理Unknown/空画面未确认禁新非空投影，只观察原Task/snapshot或Dispose；确认后下一Present仍Update，不再Attach/Bind。Read撤销只允许逐字段匹配当前撤权快照的删除输入，不换授权获取新读权。旧源Remove/Retire依真实borrow/work退出，空Presenter由同Owner留至下次Revoke/Return。Viewport新增EmptyTransition回执字段按此窄消费；本控件Region叠加仍非交互，不采用BC-U2 SelectOverlayObjectCommand/ObjectSelectionChanged，不为该通知新增选择功能。

#### 8.4.2 语言与权限服务的确定映射

空STA Host显式装配[Localization§4](../localization/DEVELOPMENT-GUIDE.md)的LocalizationService(RuntimeOptions,loader,TimeProvider,scheduler,diagnostics)，或借用已经Ready的同service；不得依赖Shell语言菜单/静态CurrentCulture。LoadCatalogAsync原Task确认Loaded+ResourcesReleased后CreateScope(OwnerTag,InitialLocale,CatalogRevision,本节全部RequiredKeys,false,FormatProfile)→AcquireSnapshot(SnapshotRequest("variation-workspace",ExpectedActivityRevision))→对每key用Resolve(lease,ResolveRequest("variation-inspection",key,Arguments,MaxOutputChars))生成一次完整不可变WorkspacePresentation。控件ApplyPresentation与具体presenter.SetResourcesAsync（已Bind时直接转发binding.SetResourcesAsync原Task）使用同一Locale并由Host记录各自完整快照版本；ViewportUiResources.Revision必须为viewport-ui-text/1文本schema，不是Localization的CatalogRevision/ActivityRevision。Host用上游ViewportUiResourceCatalog.Get取得完整包，再加入本模块实际Overlay标签文字；不得把Variation.*子集或Localization revision直接作为viewport资源包。两入口先完整预检，再在同Dispatcher投影；缺关键键保持各自旧完整包并报告，不声称跨模块事务原子。Resolve的参数按上游ArgumentValue精确类型，不能用当前文化解析既有数字。ReportSnapshotLease用完Dispose，语言批Context不跨回调保存；订阅的Detach/CloseScope/原呈现Task退出由Host持有，借用共享service不Stop。独立Host拥有service时全部scope/原任务/报告lease退后才Stop，Unknown保持原Owner。

权限借用[Authorization§3](../authorization/DEVELOPMENT-GUIDE.md)的IAuthorizationPort；独立Host需要自建时准确构造AuthorizationService(profile,authority,fence,audit,clock)，全部为明确Host输入，不补账号/SDK/缓存。IVariationWorkspaceAccess在Host只作映射：按action取Host已批准ActionRef/PolicyRef/PurposeCode与资源绑定，用当前AuthorizationContext/原输入修订构造新AuthorizationRequest(新Guid RequestId/CorrelationId,context,action,resource,UseKind,policy,purpose,CreatedAtUtc,有限DeadlineUtc,approver)→AuthorizeAsync；已批准关系涉及前决定时用RecheckAsync(new RecheckRequest(原RequestId,currentRequest))。Allowed要求Completed、非HistoricalReplay、Policy允许、GateError=None：Read必须Eligibility=Blocked且Audit=NotRequired（上游明确只读规则），Mutate必须Eligibility=EligibleAtEvaluation且Audit=Persisted，有效期/AuthorityRevision取返回authority证据，不能从输入CanHandoff推得。读Inspect/Validate/CompareExisting映Read，创建Train/Suggest及Handoff意图映Mutate；具体action/policy/主体/审批人由Host批准配置，缺项禁对应命令不阻只读任务。权限原Task/订阅/Cancel/Stop由Host强持，取消观察不是撤执行；原Unknown通过GetOperationAsync(context,原RequestId)恢复，不重发新许可。viewport的CheckAsync/Changed仍按其独立公开端口要求绑定同可信authority，用途/访问域不可凭字符串互推；本模块不复制权限权威或放行逻辑。

## 9. 正常、边界与失败案例

| 案例 | 输入与预期 | 禁止行为 |
|---|---|---|
| 稳定良品比较 | 同参考格、同尺寸 byte 单通道、完整支持；E=D、L/K 为空、N=D、U 空 | 将“算法成功”当成业务放行 |
| 亮暗双向 | 明确 `LightDark`；返回两个有固定顺序的槽，即使其中一个为空；在图像边界用独立 Golden 核验证相等阈值是否响应 | 删除空槽导致亮暗索引错位 |
| 阈值边界 | §3.4明确max及严格比较；A/B=0、非对称对、等于可表达实际上下界和内外相邻值用26.05 Golden核量化 | 猜整数阈值取整、加epsilon或改为非严格比较 |
| 训练样本污染 | 少数训练图含稳定错误时，展示模型 i/v 变化并由独立资格和留出样本发现；Robust 多数固定错误也必须能揭示资格风险 | 因为使用 robust 就自动接受样本 |
| 不完整输入 | Host预冻结多块D共100像素：完整块80已比较L=2/K=1，另一块20的R不完整→整块未知，合并E=80/N=77/U=20。若同一个R中缺20点，则该单块E=N=空/U=D=100 | 在不完整单块内仍比较80点；将其余20点计正常或删D |
| 注册采样足迹缺失 | 插值中心有效但参与插值的邻点有缺采，则该块不能宣称完整比较；保留未知原因 | 填 0、镜像或常数补边后当成实测良品 |
| 参数/类型错误 | RGB、real、尺寸错、负阈值、NaN、错模型修订均返回明确错误；不分配或不污染现有模型 | 自动灰度化、裁尺寸、改模型或返回空区域 |
| 取消/超时 | 取消训练后不发布半模型；native 调用未退仍持有资源，迟到事件按 epoch 丢弃 | 取消即清句柄、将超时计作已释放 |
| 保存/读回失败 | 保留旧模型；报告精确失败阶段和原资产回执状态，Unknown 按原操作回查 | 用暂存预检冒充封存后 fresh 读回或覆盖上一模型 |
| 第二消费者 | 同一个 Core 在另一独立视觉工具中只替换输入/参数来源/展示宿主，算法结果语义不变 | 复制算法源码或要求引用原宿主私有库 |

统计解释反例仅作资格/实现警戒，不写入Backend训练Oracle：`[100,100,100,100,140]`在显式ddof=0的数学例中均值108、标准差16，A=5/B=3时理论上界156会吸收140；其中位100、未缩放MAD=0。`[100,100,140,140,140]`的中位140/MAD0则说明多数固定错误可变“参考”。时间批`[0,0,100]`和`[101,101,101]`全集中位100.5，批中位再中位为50.5，仅保留末批为101；两批`[100,100]`/`[140,140]`各方差0，全集ddof0方差400。禁止合并批中位/平均批方差、重复未知已更新训练或把上述数值当HALCON实测；native只按VI-N01读回。

### 9.1 第二轮场景驱动架构复审矩阵

下表是开发人员和审核者的逐场景执行卡。每一行都必须能够从正式契约和输入样例走到确定终态；无法确定的字段仍是准入阻断，不得靠实现者猜测。

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态/错误 | 恢复动作与可判定验收 |
|---|---|---|---|---|
| 正常配置/执行 | 完整单通道帧；尺寸/类型/参考格来自冻结方法快照；A/B、方向、D/I 来自批准 Profile | Validate → 创建模型 → Standard/Robust/Direct 路线 → prepare → 留出评价 → 比较 | `Completed`；亮/暗槽、E/N/U、模型 hash、耗时齐全；候选为空是合法空结果 | 同一快照重放结果/槽序/支持一致；无 UI 与 UI 调用语义相同；不输出业务 PASS |
| 空输入与部分成功 | 空训练集、空 Direct 源、零尺寸图，或多块中仅部分有完整支持 | 在分配 handle 前拒绝空输入；合法请求按块执行并逐块记账 | 空输入为 `Rejected + InvalidParameter`；所有计划块执行完但仍有 U 时为 `Completed` + 结果质量 `IncompleteSupport`；未完成才是 `Cancelled`/`Failed` | 空输入不创建或污染模型；部分结果不可冒充全域结果；E/N/U 守恒，空候选仅在 U 为空时成立 |
| 歧义/错误输入 | RGB/real、多通道、尺寸错、修订不一致、A/B NaN/负数、native返回缺槽 | 可静态判断的错误预检拒绝，不进入native；返回缺槽只能在compare后发现 | 预检为Rejected+UnsupportedInput/ReferenceMismatch/InvalidParameter；已接纳后缺槽为Failed+AdapterFailure，排空释放后结算 | 用新Key修正输入；隔离出错模型，旧独立模型不变，不把native错误写预检Rejected |
| 超大/高并发 | 图像/样本达到 Profile 上限，或多请求竞争同一模型 | 预估图像、native 暂态、输出和队列预算；有界排队；不同实例可并行，同 handle 串行 | 预算不足为 `ResourceBudgetExceeded`；排队超期为 `DeadlineExceeded`，仍需 drain；不自动抽样 | 只执行批准的 tile/降并发方案；记录 P95/P99、峰值内存和队列；无 OOM、无结果串写 |
| 噪声/遮挡/退化 | 质量门报告低对比、污染、遮挡、饱和、坏点或注册残差超限；来源为上游质量/坐标端口 | 先验证质量和逐级采样足迹；只使用已批准预处理/排除 I；不自适应改阈值或形变 | `IncompleteSupport` 或 `UnsupportedInput`，U/原因保留；不把退化图当良品 | 上游补采/重定位/换获批快照；相同坏输入重放得到相同拒绝原因；不得在线吸收 |
| 取消/超时/native 排空 | 训练或比较在途；宿主发取消或 deadline | 标记取消 → 停止未派发工作 → 等同步 Adapter 返回 → `Drained` → 释放临时对象/归还租约 → `ResourcesReleased` | `Cancelled`/`TimedOut` 只在 `Drained` 与 `ResourcesReleased` 后发布；迟到回调按 epoch 丢弃 | 在真实退出前保持图像/handle；关闭测试证明无 native 使用后释放、无旧结果覆盖新代 |
| 资源上限 | 样本数超过 65,535、内存/Region/诊断图/并发预算不足 | 先拒绝硬上限或批准的分块；Robust 不拆成批次中位数；Direct 不偷偷量化 | `ResourceBudgetExceeded` 或 `InvalidParameter`；原候选仍保留 | 调用方减少输入或提交新 Profile/空间方案；验收确认不丢样、不缩 D、不覆盖旧模型 |
| 持久化/版本修订 | 写入、封存、物化、fresh 读回任一步失败；模型或输入修订 hash 不匹配 | 新实例暂存预检 → 原资产 Owner 封存 → 同一字节 fresh 读回 → 功能 Golden → 才装载 | `PersistenceFailure`/`ReferenceMismatch`；旧 Loaded 模型继续有效 | 修复存储或重新封存；原模型保持；报告列实际字节 hash、可查能力和未知项，保存不等激活 |
| 升级/回退 | 新 Core/Adapter 或模型主版本与当前运行版本不同 | 并行载入新候选 → 同输入/参数回放 → 比较结果/支持/资源 → 停止新准入 → 排空旧版本 | 通过才由宿主切换；不兼容为 `UnsupportedInput`/`ReferenceMismatch`；回退由宿主执行 | 旧版租约未归还前不清除；升级失败保留旧内容/回执；不自动选择 latest 或触发设备回退 |
| 无 UI 调用 | 命令行/服务/Replay注入帧、快照、Backend/时钟/Options | ValidateTraining→BuildCandidate/Load/Compare operation→Query/Completion→Unload/StopAndDrainAsync | 强类型结果/错误；没有UI或事件监听也完成 | 最小Host正常/拒绝/取消/关闭路径；不依赖Dispatcher |
| 可选 UI | 宿主提供草稿、语言、主题和图像投影；核心仍接收不可变快照 | UI 编辑 → Core Validate → 冻结执行 → 进度/诊断投影 → 取消/关闭 | 参数无效显示字段问题；旧结果标过期；不显示业务 PASS/NG | UI 卸载后核心仍可运行；三语和异常订阅不改变结果；真实 WPF/UIA/DPI 另验 |
| 第二消费者/长期运行 | 不同视觉工具、不同配置来源；连续运行/反复换版/重复取消 | 两个独立实例共享发布包；定期采集句柄/队列/内存/迟到事件指标；换版按租约排空 | 每请求 OperationId/epoch 单调；资源趋于稳定；故障隔离到实例/请求 | Soak/重启/重复 Dispose/取消竞态后无增长或串写；第二消费者无需改 Core；异常回调不影响后续请求 |

## 10. 测试矩阵与验收

| 层级 | 用例 | 通过断言 |
|---|---|---|
| Contract/Schema | 必填、像素类型、阈值长度/有限值、序列顺序、跨字段关系、版本 | 合法样例通过；非法样例稳定拒绝且不创建 handle |
| HALCON Golden | byte/int2/uint2，Standard/Robust/Direct，A/B 两槽、四方向、阈值内/等于/外、空结果 | 固定 26.05 环境输出槽序/阈值/方向一致；量化不变量和实际原生值分开记录 |
| 统计边界 | 奇偶样本、常数图、离群点、多批次、顺序变化、robust 重复调用 | 不以自算统计替代 native；检出重调覆盖训练集语义；资格门能识别污染风险 |
| 支持/空间 | 缺采、坏点、饱和、边缘/插值 halo、洞、块缝、取消中断 | E/N/U 守恒；未知不变正常；分块与整图只在本页§3.5/§4.1条件和实测样本成立时接受 |
| 状态/故障注入 | prepare 失败、Adapter 异常、资源不足、写/读损坏、fresh 读回失败 | 状态只有一个终态；原模型不变；成功/失败/取消都归还资源 |
| 并发/生命周期 | 同handle竞争、独立实例并行、慢事件拉取者、停止准入、取消竞态、epoch乱序 | 同model串行，拉取不占native线程；事件丢序显式可查，关闭只在真实drain后释放 |
| 兼容 | 同主版本扩展、主版本破坏、旧/未知能力模型、模型字节损坏 | 明确兼容或拒绝；不按路径/标签自动选旧版 |
| 可选 prepared-handle 缓存 | 同模型/配置重复加载、profile/runtime/capability 任一项变化、generation 撤销与在途比较 | 只有完整精确键命中；改变后拒绝旧项，停止新租约并 drain 后才释放；启用/关闭缓存结果一致 |
| 无 UI / UI 等价 | 同输入参数由命令行/API 与可选控件发起；两种调用对比核心返回 | 参数校验、结果、错误、取消和资源语义完全一致 |
| 两个消费者 | 两套独立最小宿主，替换 UI、配置来源和模拟输入 | 两者均只依赖公开包，均可运行核心正常/拒绝/取消/关闭流程，无私有类型泄漏 |

最低接收断言：训练与运行输入的版本/完整支持逐项可审；比较结果能区分亮、暗、N、U和未执行；模型候选只有在封存核心 fresh 读取及功能 Golden 后才记技术验证；两个真实规划消费者独立接入同一包；无 UI 路径完成同一业务能力。Mock、算例或通过编译不能代替 HALCON 原生行为、真实样本或现场资格。

### 10.1 可执行 Core/模拟断言

全部用例落§13.1唯一Core测试Exe，固定TimeProvider、闩锁和游程集合Oracle；不调用HALCON、不把脚本模型当训练实现。下述数值只属于解析测试fixture，不是生产默认。正常fixture：R为4×2 Byte、D=全8像素/I空、有效位8、全支持，两个独立Observation/Group的训练图；ScriptedBackend返回Light槽(0,1..1)和Dark槽(1,2..2)，Core应E=8/C=2/N=6/U=0。所有测试清楚标TruthOrigin=Synthetic/Analytical；即使真值标记模拟“真实来源”用于反例，也不记生产证据。

| 用例ID/组 | 具体输入或交错 | 必需断言 |
|---|---|---|
| VI-C01/contract | 上述fixture，四方向返回形状；LightDark第二槽合法空 | E/N/U游程精确、固定槽数/顺序；Light only N=7且未检Dark，Absolute不能给伪L/K；native成功不输出业务PASS |
| VI-C02/contract | 训练空/default/一组、W=0、溢出面积、非法枚举、阈值NaN/∞/负数、游程越界/重叠、错误SHA | Rejected且Create/Acquire调用数0；非法request不污染实例高水位，修正请求新Key可接纳 |
| VI-C02b/contract | A.2的VI-METHOD-CANON-01完整合法MethodSnapshot及固定canonical字节；独立逐字段Writer与独立Oracle；日期/null/枚举编码探针 | 输出逐字节等于固定单行、长度911、SHA256=`eeb9d16a38fcf8e351ff045d8e22957838292b39da40395f20026457e39923b2`，ComputeMethodHash同值；不得用待测函数生成expected。默认encoder/非ASCII/特殊字符按固定字节；nullable显式null、非法枚举拒绝、UTC O日期保留七位小数/+00:00，详见A.2；无Backend/Acquire/生产副作用 |
| VI-C03/contract | 同Observation重复、同Group重拍、不同真实观察同像素常数；训练组与Validation/IndependentTest曝光组交叉 | 重复Observation拒绝；同组不增独立组数；独立相同像素可接受；同源泄漏拒绝，不通过删除难样本修复 |
| VI-C04/contract | 单R缺一点、I中缺足迹邻点、gate Unknown；两个Host冻结块80/20分母；MetadataRuns超预算 | 单块无compare调用/E=N=空/U=D；多块Host仅合并完整块保留U；参数/D/hash不随坏输入改变，超额不丢游程 |
| VI-C05/lifecycle | Build各Create/Train/Prepare/诊断/Serialize逐步闩锁，分别失败；Robust N张和Standard N张 | Standard N次每次一帧、Robust一次全N、Direct零Train；未知更新不重试同handle；最终资源归还计数准确，候选未完整不返回 |
| VI-C06/lifecycle | 同Key同载荷再提交、同Key不同阈值、已Release的旧Key、保留槽满 | 原operation同一Completion/工作次数1；DuplicateConflict不改原任务；过期RequestExpired；有界拒绝而非自动淘汰原查询 |
| VI-C07/lifecycle | compare闩锁未退时取消/推进deadline/StopAndDrain；墙钟向前/后跳；队列中取消 | 底层在用时Query=Draining/DrainUnknown，模型/帧不Dispose且Completion不结束；释放闩锁后Drained→ResourcesReleased→唯一终态；单调deadline不被墙钟跳变延长；未Started也完整清账 |
| VI-C08/lifecycle | 同model两个Compare，与另一model独立Compare；Unload与新Compare竞态；关闭期限到达后释放闩锁 | 同model串行，不同model在额度内可并行；Unload接纳即停止该token新租约，无饿死；模型Dispose仅一次、旧epoch不重用，关闭未知可查后最终归还 |
| VI-C09/lifecycle | Frame Acquire失联/迟到、Dispose闩锁、错PackageHash/Format/版本、模拟器ProductionRead | 返回资源未知不先终态；错hash拒绝不ReadFresh；模拟器生产Load拒绝；Direct/瘦模型诊断Unsupported保持请求槽，不读黑图或implicit Prepare |
| VI-C10/recommendation | 解析2候选在冻结Validation上同分、换输入ordinal；范围外A/B；没有正例/Unknown/搜索取消 | 全部合法且RequireRealEvidence=false时以ordinal破同分，RealEvidenceComplete=false；true且无真实两类则Incomplete；超界Rejected；计划未全完不选早期结果；不改当前Production token |
| VI-C11/recommendation | G有2点，C命中1点且另有1假点；G空的良品C有1点；一帧不完整 | 第一帧TP=1/FP=1/FN=1，图像级不算全漏检；良品误报1；未知独立计入Planned/Unknown，指标不伪完整；取消/异常已算item保留，U不转N |
| VI-C11b/recommendation | LightDark真值Dark在(0,1)，结果只有Light在同一点 | TP=0/FP=1/FN=1且图像级漏检1；不能由空间并集相同判正确方向 |
| VI-C12/consumers | PG006/PG022两个独立最小Host；A取消/回退/卸载与B运行交错；token跨实例 | 同公开包/同输入等价，私有类型不依赖；A旧代结果不覆盖新代，B不中断；方法hash变更新包/epoch，旧精确包回退仍经新Load；ReleaseOperation不改变已交Host的托管结果 |
| VI-C13/consumers+lifecycle | §4.4 Host在Validate拒绝、Build/Load/Evaluate非成功、接受门拒绝、封存Unknown/抛异常、ApplyDomainRulesAndCommit抛异常逐点退出；Unload/Release再抛异常；Load晚返token | 每条路径均进入finally并调用同实例Stop；清理不复用已取消业务ct；终态才Release、不遗漏迟到Load；消费原异常与清理异常均保留；有限等待后原Owner仍强持实例/端口及handle |
| VI-C14/consumers+lifecycle | 关闭DrainUnknown（含仅Backend.Dispose闩锁未退且HeldBytes/Pending为空）、观察一次有限tick、转交拒绝/超时/抛异常，后释放原worker闩锁；无订阅者 | 未获接受原Owner持续持有/查原Key、不新Load/新backend；接受确认后仅新Owner负责；真实Drained后Release/Dispose恰好一次，Pending/资源不伪0；Owner记录不因测试方法返回被GC丢弃 |

### 10.2 真实适配与 UI 断言

| 用例ID | 场景与判定 | 后续证据门 |
|---|---|---|
| VI-N01 | byte/int2/uint2三型×Standard/Robust/Direct，奇偶N/常数/外点/重复robust调用；读i/v/阈值实际类型、下/上顺序；§3.4四组向量及可表达实际边界的内/等/外、极值与非整数理论阈值 | 固定26.05 CPU、原图/模式/A/B/hash；max且亮>上/暗<下，等号不入槽；记录实际量化而非自行round；以原生读回和compare Golden验，不用SciPy缩放或手算ddof冒充native |
| VI-N02 | 弱信号细缺笔、边缘重影、独立mark错位、照明漂移、反光/遮挡；同组分离的真良品/真缺陷 | 分开差异/对齐质量/照明拒识/真缺陷；统计未知/误拒/误接受及真实覆盖，未读不删除分母；用户/客户物理限值来自Profile |
| VI-N03 | ExternalMap/Sobel3类型与真实halo，负v/缺halo拒绝；高规模Robust峰值；四方向空Region形状/游程上限 | native图类型/饱和/量化/资源实测；相同代表图对候选正确性/拒识/P50/P95/P99/峰值，无实测不宣布最快 |
| VI-N04 | 完整/瘦/Direct `.vam`保存与正式封存后fresh读回，损坏/缺依赖/查询不支持，缓存键任一项变更，fresh禁缓存 | 原字节/依赖hash、同Golden等价、诊断未知项保留；暂存读回≠正式报告；N资源取消/关闭真实退回前不clear |
| VI-N05 | 固定完整空间块与整图同训练集合/全局处理/真实halo，跨缝响应、缺块/版本切换/回退 | 同输入原槽/支持core并集等价；Host跨缝连接前不逐块过滤；native执行资源尾延迟和取消到排空实测 |
| VI-N06 | A.6独立/组合工厂，非法Options/Core构造失败、两个独立Host、无UI；首次native创建失败 | 构造无native/Acquire/scratch副作用，失败回滚backend；成功所有权仅交Core，端口仍借用；实际revision/能力对应环境，独立DLL不依赖Shell；声明不替代实际执行 |
| VI-N07 | Serialize/ReadFresh每个暂存申请/写/闭流/核长/读/删除阶段故障，迟到申请/释放闩锁、额度满、超长/坏字节、取消/关闭 | 所有文件只限该lease；fresh确为新句柄；新handle/流/单文件真实退出才减模型及scratch计数，未知由原Owner观察；旧Loaded不变，不删父目录/原件，不以日志吞释放失败 |
| VI-U01 | 1920×1080可用client、三语/长hash/阈值/单位、dock恢复/越屏、图表表格/同格双图联动 | 本机25.2.3真WPF，布局/选中与冻结参数分开；关键命令/Unknown可见；无模拟数据填空 |
| VI-U02 | Tab/F6/Ctrl+Enter/Alt+C、IME和数字草稿中切文化、图像呈现迟到A→B→A | 自动化ID/焦点/读屏信息、caret/解析文化保持；旧结果过期，不自动采用；只影响本控件 |
| VI-U03 | 可见候选被取消、Core共享A/B、UI卸载时presenter未退/宿主handoff抛异常 | Detach未知保留资源/查询、不Stop共享Core；宿主未接收候选明确提示，不假称封存/发布；真实Dispatcher/内存/长稳别验 |

## 11. 性能预算与可观测性

26.05 create_variation_model Complexity给的是模型部分：Standard/Robust的Byte为12WH bytes、Int16/UInt16为14WH；Direct或清训练后的Byte为2WH、另两型为4WH。不包括全部训练/注册图、native暂态、托管复制、UI、写盘/fresh双实例。解析例4096² Byte完整模型约192MiB，50张单平面输入约800MiB，还未加上述开销；concat_obj共享存储也不解除输入lease。此估算只解释资源组成，不替A.6适用预留Profile或实测峰值；不得用它反推诊断图实际类型、把Robust全量预算当模型大小、靠OOM试限。

每个消费者必须提供不可变 `BenchmarkProfile`，绑定模块/adapter、HALCON 26.05/AsunImage、OS/硬件/运行时、Variation 方法、模型/阈值图/参数/输入 fixture revision/hash。负载按图像尺寸和底层字节、训练数 `N`、tile 数、像素类型、并发实例、预览/诊断队列和保留图像数、Robust 全量样本集及冷/热状态分桶。Profile 必须在运行前冻结预热次数、测量次数、最低有效样本数、有限 deadline、峰值驻留字节/句柄/队列上限、固定吞吐窗口、各阶段测点及阈值来源。冷启动单独测；热态按固定次数预热且样本不计入统计。训练图数量 65,535 是 HALCON 26.05 `train_variation_model` 公布的协议上限（见本地算子页），并非推荐训练规模或内存/性能目标；其它数值上限由已采纳的 Profile 提供，不能写经验默认。

分别测冷启动、热运行、校验、训练、prepare、单图 compare、输入/配准 lease、诊断复制、序列化/fresh 读回、结果搬运、队列等待、端到端至资源释放，以及取消到 native 真实退出/排空/lease 归还。负载按训练样本数、图像底层字节、native 暂存与并发分桶；Robust 全量样本集峰值必须按实测暂存计入，不能只按模型字节估算。记录模型/句柄/Region 数量、托管/native 峰值、队列高水位、固定窗口吞吐和阶段耗时。通用 P50/P95/P99 统计、样本有效性、失败/删失及未排空规则按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。模块结果中的比较拒识、预算拒绝、训练失败和 `DrainUnknown` 必须分别保留原因。所有验收阈值来自已采纳消费者/客户 Profile；缺失时标 `TargetPending`。

诊断字段至少含模块/适配器/能力版本、OperationId/epoch、方法/模型内容 hash、输入帧 hash/修订、参数快照 hash、尺寸/类型/参考格、E/N/U 像素数与比例、L/K 像素数、样本数量、块状态、阶段耗时、队列等待、资源峰值、取消请求/真实退出时间、错误类别和恢复建议。不得记录原始私有业务数据、未授权图像或宿主密钥；图像证据保留由调用方策略控制。

Benchmark CLI的Profile直接由现有消费者提供，不在本轮新增报告/manifest。字段绑定：ProfileId/Revision/hash、Core/Backend/runtime/OS/CPU/内存、MethodHash/PackageHash/fixtures/用途、图W/H/Type/位深/stride、TrainingN/模式、同时持有帧数/active models、候选数×Validation数、块数/真实halo、Cold/预热次数/测量次数/最低有效n、并发/排队上限、deadline、Options/Budget、阶段测点、目标阈值与来源ContentReference。阶段固定validation/queue/frame.acquire/model.create/train/prepare/diagnostics/serialize/read.fresh/compare/evaluate/recommend/drain/release；逐帧比较时长与整请求端到端分开。输出stdout保留Profile身份/全部失败和删失/资源未知，不只成功样本；统计方法唯一按DEV-GOV-010 §3.1。

负载必须覆盖各已支持像素型、2与Profile上限N、一个/最大Loaded、一个/最大并发、正常/全响应Region、最大的合法D游程/diagnostic/model包、Sobel真实halo、cold/warm以及换版双实例；先冻结具体负载而不试OOM选限。样本峰值按实际输入storage、model、native暂态、托管输出/保留operation分别采集，Unknown native bytes为null并标NativeAccountingVerified=false，不能用预估当实测。Benchmark没有目标值则NotEvaluated；DrainUnknown或实际资源超过Profile硬上限为失败。Core simulator只衡量调度/元数据/支持/排序和泄漏，不给HALCON节拍/峰值结论。UI另记排队/帧呈现/dispatcher阻塞和呈现峰值，10Hz刷新设计上限不是已测帧率。

## 12. 发布、回退与第二消费者

独立包至少固定 Core、AsunImage Adapter 和可选 UI 的版本、目标框架、公开能力清单、依赖闭包、模型格式能力及兼容矩阵。发布阶段为：契约批准 → HALCON 26.05/`ImageLibDotNet` 适配核签 → Golden/故障/资源测试 → 两个独立消费者集成 → 候选包签名和内容 hash → 影子回放/受控评价 → 原 Owner 批准接入。当前文档不表示任何一步已完成。

升级先并行载入新候选并用同一固定输入/参数回放；结果、完整支持、错误/取消和资源差异符合批准 Profile 后，调用方再在自己的边界切换模型。运行中模型按租约排空后释放；失败则停止新版本准入，旧版保留原内容和回执，调用方按自身产品流程回退。禁止模块自动选“最近版本”、覆盖现行模型或触发产品/设备回滚副作用。

两个已规划消费者固定为PG006 PCB固定丝印检查与PG022终装标签固定印刷检查，任务边界按本页§3.5及本节；二者独立Host只共享公开包，不共享页面/私表/全局状态/训练集。A由独立板Mark配准固定R10字形，IM-030输出差异，OCR即使读对也保留字形候选；A Host另做位置/区域派生/规则提交。B由壳体/标签基准配准固定logo/警示语D，序列号/日期从D预先扣I但保留独立OCR内容/字形义务，遮挡整块未知；B Host另做成品关联/区域/规则。可选UI只用于工程调试，生产Host通过相同API；真实产品Owner、原图/真值/性能阈值和接入证据尚未提供，不能称已集成。

两个最小Host在同一Core测试Exe内保持独立FrameSource、Backend、TimeProvider及module instance，分别使用A/B公开输入fixture并完成Validate→Build→PreviewLoad→Compare→Evaluate→Unload→关闭；不调用产品库。在A/B给出同一解析输入时槽/E/N/U等价；A取消/卸载/语言切换不影响B，token跨实例拒绝。客户真实图片/产品合同只阻真实接入资格，不阻这些公开契约与模拟隔离断言。

包发布固定Core/AsunImageAdapter/Wpf独立DLL，Core只引用BCL；Wpf/Adapter只引用Core与各自已批准依赖。Host只替换自己的公开端口适配，不复制Core。当前包格式/契约版本精确`0.2`；加载必须BackendRevision/HalconRuntimeRevision与Manifest一致，漂移拒绝，不自动改参数或read/prepare迁移。未来允许的新可选字段需显式能力兼容；改变资源/方向/阈值/状态或canonical形状是破坏变更，升版本并在隔离候选上重建/Golden。回退保留旧DLL及原模型/配置/样本闭包，由Host建立新实例、新epoch重新Load旧精确内容，再在合法边界切换；原在途任务留原版本，禁止在正在使用的实例替换程序集。

## 13. 实施准入与当前未决项

2026-10-10主控接收C1～C4六项为`ModuleCoreImplementationReady`，范围仅原Core、托管协调与Simulator规格；这是主控内容复核结论，不由会话登记accepted或API附录存在推得。2026-10-11主控限定内容接收§8.4、A.6.1～A.8的N/U确定指导增量，涵盖公开构造、语言权限、ModelAssets/ImageFrame映射及N无UI/U独立STA完整Owner恢复；N1/N2/U1实际HALCON/资源/WPF/Golden/运行及现场资格仍为`PreparationIncomplete / NotReady`，整模块及产品资格未提升。进入Core编码仍须明确实现派发及权威代码仓库/可审计快照起点；当前工程未创建，未执行实现/产品编译/测试Exe。平台合同、真实native/WPF、集成、Golden、性能与现场门按受影响范围另行关闭。

### 13.1 唯一代码与测试落点

下表定义未来获准实现落点，当前不创建目录。每切片只能写表中自己的工程目录；共享solution/Directory.Build/其它模块/产品装配由主任务串行处理。禁止AsunImage内部、只读参考、项目规则/入口/进度、共享契约、SDK源码、其它src/Modules和tests/Modules；项目内AsunImage的现有消费引用由Adapter复用，不改库/版本、不下载包。

| 单元 | 唯一工程/测试工程 | 技术和执行 |
|---|---|---|
| Core，C1–C4 | `src/Modules/variation-inspection/Asun.Modules.VariationInspection.Core/Asun.Modules.VariationInspection.Core.csproj`；`tests/Modules/variation-inspection/Asun.Modules.VariationInspection.Core.Tests/Asun.Modules.VariationInspection.Core.Tests.csproj` | Microsoft.NET.Sdk/net10.0，Nullable/ImplicitUsings启用；Core无第三方PackageReference。测试OutputType=Exe，仅BCL+Core ProjectReference，ScriptedBackend/最小Host/断言均在此测试工程，不新增测试框架或模拟包 |
| AsunImage Adapter，N1–N2 | `src/Modules/variation-inspection/Asun.Modules.VariationInspection.AsunImageAdapter/Asun.Modules.VariationInspection.AsunImageAdapter.csproj`；`tests/Modules/variation-inspection/Asun.Modules.VariationInspection.AsunImageAdapter.Tests/Asun.Modules.VariationInspection.AsunImageAdapter.Tests.csproj` | net10.0-windows、x64、Core+已有AsunImage引用及ImageFrame Core/Resources公开引用（仅A.7薄桥），经cv2，不引用halcondotnet；测试net10.0-windows Exe，固定26.05环境/fixture/Profile。真实使用进程临时物化目录由Host端口受控创建，测试关闭排空后只清本次生成且无引用文件，不动原件 |
| Optional Wpf，U1 | `src/Modules/variation-inspection/Asun.Modules.VariationInspection.Wpf/Asun.Modules.VariationInspection.Wpf.csproj`；`tests/Modules/variation-inspection/Asun.Modules.VariationInspection.Wpf.Tests/Asun.Modules.VariationInspection.Wpf.Tests.csproj` | net10.0-windows/UseWPF=true，Core+本机DevExpress25.2.3程序集+ImageFrame Core/Resources及viewport Core/Wpf公开引用（§8.4薄桥；不反向改Core），公开面按§8；UI测试为STA Exe，使用明确1920×1080 viewport、真实WPF/UIA，不以Core测试或截图替代 |

Core执行命令固定：`dotnet build src/Modules/variation-inspection/Asun.Modules.VariationInspection.Core/Asun.Modules.VariationInspection.Core.csproj -c Release`；`dotnet run --project tests/Modules/variation-inspection/Asun.Modules.VariationInspection.Core.Tests/Asun.Modules.VariationInspection.Core.Tests.csproj -c Release -- --scenario all`。按需`--scenario contract/lifecycle/recommendation/consumers`定向运行；Benchmark用`--scenario benchmark --profile <消费者现有Profile路径>`。`dotnet test`不执行此Exe，不能把空执行算通过。

Core的`contract/lifecycle/recommendation/consumers/all`软件机制测试固定真实时间保护：每个具名case（含参数化展开项及其清理）10秒，所选suite从首case开始到全部清理/断言结束120秒，外层测试启动器从启动`dotnet run`子进程到退出180秒（包含该命令的隐式构建/启动）。单case与suite先到者生效，不因重试或finally重置计时；外层显式build若单独执行按构建门处理，不算进120秒suite。10秒覆盖纯BCL小夹具/可控闩锁的机制验证，120秒约束全组，180秒给构建/启动余量；均为测试卡死保护，不是算法/客户性能目标。当前未运行这些测试。

case/suite使用真实单调`Stopwatch.GetTimestamp`及`TimeProvider.System`的真实等待保护，外层独立启动器用自己的单调wall计时；不能使用注入模块的虚拟TimeProvider推进这些保护。虚拟clock只驱动被测请求deadline、排队、取消等确定性语义，推进/冻结虚拟时间不延长或触发真实保护。case到期先记录用例ID/未完成断言并请求原operation取消，后续清理/观察仍受剩余suite/外层预算且沿§4.4原Owner保持；不可将等待超时写成module已排空。suite到期停止派发并返回非零；死锁阻止进程退出时由独立外层保护在180秒终止测试子进程并记录超时/未完成，不能记ResourcesReleased或测试通过。失败、必需跳过、未排空、任何未完成断言（含0个必需case被执行）均非零退出；只有所选组的全部必需case完成且清理确认才0。Benchmark以及N/U耗时由各冻结Profile定义，不把上述小夹具保护冒充native/WPF/性能验收期限。

N/U执行分别用表中测试工程相同`dotnet run --project ... -c Release`，N传`--scenario all --fixtures <只读fixture目录> --profile <Profile路径>`，U传`--scenario all --viewport 1920x1080 --culture zh-CN,zh-TW,en-US`。这是后续实现须具备的CLI约定，当前未运行/未创建项目。每Exe有有限场景截止点和外层进程截止点；失败、必需跳过、未排空、断言未完成均非零退出并列用例ID，只有所有必需断言完成才0。性能目标缺失时可打印诊断测量但资格为NotEvaluated，不能归入性能通过。

### 13.2 逐切片六项规格定位与剩余门

G1边界/消费者，G2精确API/单位/版本，G3无UI端口/最小Host，G4失败/可执行断言，G5Benchmark方法，G6工程/路径/顺序，唯一条件按DEV-GOV-010 §3.1。下表记录主控逐切片规格接收及剩余门；Ready只表示标明范围的六项规格获接收，不是代码、测试或真实能力已完成。

| 切片（覆盖整模块能力） | 六项规格定位 | 主控接收状态 | 真实剩余门/影响 |
|---|---|---|---|
| C1 参数/域/版本/canonical/支持集合 | G1§1/12；G2§3/A.1–2；G3A.5；G4VI-C01/02/02b/03/04；G5§11；G6§13.1 | `ModuleCoreImplementationReady`，2026-10-10，仅Core规格 | 实现派发、代码基线确认、实际构建/断言未执行；无客户物理值依赖 |
| C2 异步操作/有界接纳/重复/租约/Loaded生命周期/包校验与读回控制端口 | G1§1/7/12；G2A.1–4；G3A.5；G4VI-C05～09；G5§11；G6§13.1+§4.4 | `ModuleCoreImplementationReady`，2026-10-10，仅托管协调/Simulator规格 | 实现/可控Backend断言未执行；真实AsunImage行为/文件物化仍属N2/产品接入，不以模拟器证明native |
| C3 无UIEvaluate/Recommend/曝光隔离/有界排序 | G1§1/4.2/12；G2A.1–4；G3A.5；G4VI-C10/11；G5§11；G6§13.1 | `ModuleCoreImplementationReady`，2026-10-10，仅Core/Simulator规格 | 实现/解析fixture断言未执行；真实缺陷召回、生产阈值/跨批覆盖只影响模型资格，不自造参数值 |
| C4 两最小Host/公开包发布回退/模拟故障接入 | G1§12；G2§7/A；G3§4.4/A.5/§12；G4VI-C12/13/14；G5§11；G6§13.1 | `ModuleCoreImplementationReady`，2026-10-10，仅最小Host/托管协调/Simulator规格 | 实现/正常异常关闭断言未执行；真实PG006/PG022产品合同/调用代码与样本另接，不将Host示例当产品集成完成 |
| N1 26.05 Standard/Robust/Direct/诊断/单图compare/实际资源 | G1§1/12；G2A+§3.4/4.1/7.1；G3A.6–8工厂/Backend/Frame桥/无UIHost；G4VI-N01/02/03/06+A.8.4；G5§11；G6Adapter工程 | 确定指导增量已限定内容接收（2026-10-11）；实际实现/运行/资格 `PreparationIncomplete / NotReady` | 自有装配/所有权已冻结；真实C#类型/重载/封送歧义按消费编译处理；训练/阈值量化/输出形状/CPU/资源Golden及同样本比较未执行，无需再验证算子存在 |
| N2 Native保存/封存后fresh读回/瘦模型/版本升级/固定块资格 | G1§7/12；G2A.4/A.6；G3A.6.1/A.7.1/A.8暂存/资产映射/Host；G4VI-N04/05/07+A.8.4；G5§11；G6Adapter工程 | 确定指导增量已限定内容接收（2026-10-11）；实际实现/运行/资格 `PreparationIncomplete / NotReady` | 自有暂存/IO/回滚须本模块实现验证，非外部门；仅外部资产封存/保持正式接线及客户资格另接；原字节fixture、整图块等价/回退/性能未执行，未知不当已发布 |
| U1 可选工程控件及三语/联动/卸载 | G1§8/12；G2§8.2；G3§8.4公开session/presenter/服务+A.8.3独立STA；G4VI-U01～03+A.8.4；G5§11及UI采样；G6Wpf工程 | 确定指导增量已限定内容接收（2026-10-11）；实际实现/运行/资格 `PreparationIncomplete / NotReady` | 25.2.3本机官方API依据已核；真实WPF/IME/UIA/DPI/布局/性能与宿主资源接线未验，不以xml确认交互通过 |

接收依据：主控永久会话`01a1020f-126c-7242-97f9-0f50b4cd3553`于2026-10-10明确接收C1～C4六项；已复核算法/支持/训练评价隔离、资源/API/canonical、§4.4/A.5异常收尾、UI、VI-C01～14及六项定位，并独立按A.2输入字段/字符串转义重建VI-METHOD-CANON-01，完整字节一致、UTF8长度911、SHA256=`eeb9d16a38fcf8e351ff045d8e22957838292b39da40395f20026457e39923b2`。A.2完整Writer/enum/null/日期编码及case10秒/suite120秒/外进程180秒亦获复核；此为规格/固定向量复算证据，不是产品实现/测试Exe或N/U真实验证。此次同步不改API、算法、编码或Host。

任意部分域训练、native抢占式取消、同handle并行比较不是等待客户拍板的内部空白：v0.2分别固定不支持/仅边界取消/同模型串行。空间块Host路线已明确，真实整图等价资格未测；不得以“首片”将这些限制扩为整模块功能未定义。客户物理阈值、设备曝光/照明允差和生产误接受/拒绝/时延目标由真实Profile提供，缺失只影响对应qualification，不改变Core算法/Owner。

### 13.3 完整批准范围的设计结论与剩余Owner（2026-10-12）

本结论覆盖IM-030当前架构批准的良品变化/印刷差异/稳定纹理能力及其独立工程控件，不仅C1～C4或最近N/U增量。唯一软件实施基线为本页Core API v0.2及N/U具体装配；在现有输入与支持范围内，可决定的软件设计已闭合。未知HALCON内部统计/量化是待真实测定的数值行为，已有读回/拒绝/Golden路线，不交实现者另选算法。缺客户数值时不伪造生产Profile；已批准不支持项亦不是未决软件设计。

| 完整能力 | 唯一实施章节 | 可决定设计结论 |
|---|---|---|
| 三种模型、亮暗/合并/分槽、完整支持与未知 | §3.4/3.5/4.1、A.1～4 | 输入资格/类型/公式/严格边界、Standard顺序/Robust一次全集/Direct ExternalMap与Sobel真halo、R/D/I/E/N/U及槽顺序已固定；不配准/曝光/质量放行 |
| 独立训练、诊断、原样检查、运行模型/重复/取消/排空 | §4.4～7、A.3/4/6/6.2/8 | 明确factory/backend/帧/scratch/资源Owner和迟到保持；CPU→native→托管原值/游程具体搬运、瘦模型/fresh/readback、缓存和关闭路线已固定 |
| 有界参数推荐与验证/最终测试 | §4.2、A.1～4、§10 | 有序A/B候选、Validation选择/排序/Unknown分母、IndependentTest不回流；无自动生产改参或“改善”质量结论 |
| 包身份、保存/封存/升级/回退 | §7/12、A.2/4/6.1/7.1/8 | VI-CANONICAL-1、Method/Training/Package/native摘要、ModelAssets JCS独立身份、两文件/精确依赖/用途/读回及Unknown恢复已定；不另建资产事实库 |
| 完整图/固定空间块、两业务消费者与无UI | §3.5/4.1/11/12、A.5/7/8.2 | 同全局处理/成员/格/真halo→独立块模型→仅core响应并集→外部跨缝处理；PG006与PG022均用同公开无UI能力，未假称块等价或产品集成已测 |
| 独立工程WPF任务流、DevExpress/三语/权限 | §8.1～4.2、A.8.3 | 五任务入口及取消、原模型比较、Candidate交接、1920×1080/键盘/IME/UIA/渐进参数、语言与Read/Mutate精确消费，借用Core不被UI关闭 |
| 实际viewport装配/显示/探针/空清屏与资源恢复 | §8.4.1、A.8.3/4 | 同Control Presentation/backend/lifetime、公开源producer、原值/Gray8显示投影、同binding原Task/lease、完整Catalog/schema、有限清理/Clear确认后同session Update已定；不采用区域选择新能力 |
| 发布/版本/验证/性能方法 | §10～13、A.8.4 | 工程/测试唯一落点、两个Host、失败断言、Profile负载/P50/P95/P99与峰值/真实排空/第二消费者门已有消费者；不创建空工程/同义报告替代实现 |

下面是实际尚未完成的工作或确实外部门；**不列为内部设计欠账，不据设计闭合提升N1/N2/U1运行资格或整模块ImplementationSpecificationReady。** 本原会话完成内容自审/修复/文档验证，不再等待主控内容审核；共享集成/实现派发职责保持原边界。

| 剩余项 | 精确Owner | 实际影响与未运行门 |
|---|---|---|
| 本模块产品实现与消费编译、Simulator及失败/资源断言 | IM-030本永久会话；权威仓库/明确实现派发由总控/用户提供 | C1～C4规格接收保留，真实代码未开工；N1/N2/U1必须按原工程/路径实施，公开C#重载/封送歧义只在消费编译解决，不安排依赖安装/授权检查 |
| HALCON实际统计/整数量化、native fresh/瘦模型/输出及真实资源、scratch文件锁/IO/删除 | IM-030本永久会话 | VI-N01～07、目标样本Golden/Replay、块等价/回退、端到端性能/峰值/长稳尚未运行；这是本方实现验证，不能写为客户/上游设计门 |
| 上游公开producer、renderer/lifetime/Catalog/Clear实际代码与真实呈现资格 | viewport原登记会话，IM-030负责本方§8.4.1消费实现和VI-U断言 | 0.3.5-prep公开设计已经可接；未证明其真实二进制/WPF/HALCON/GDI可见确认已实现或运行。只影响实际U接入，不阻无UICore/本地N训练Inspect |
| 原CPU来源/Content/PixelHash/存储域，以及独立对齐、照明、质量/逐级足迹Gate | 来源Host与对应image-frame/alignment-2d/image-quality及处理链原Owner | 本模块只核映射并拒未知；缺证据只阻对应真实输入native/生产评价，不要求本模块补采图、配准、曝光或造物理事实 |
| 真实资产/完整精确依赖与用途批准、持久介质/产品调用链 | ModelAssets原会话负责资产服务；PG006/PG022产品Host负责其批准映射/权限与封存、加载、回退接线 | 正式ProductionRead/封存/产品集成门；不阻独立CandidatePreview、本地Scratch、Core/Simulator或工程显示设计 |
| 真实缺陷/良品组/真值、物理阈值/曝光照明允差、生产误接受/拒绝和时延/峰值目标 | PG006/PG022产品与质量Owner、客户现场/设备Owner | 对应QualificationProfile、Golden/IndependentTest、生产性能/计量/现场验收；缺数值不填合成阈值、不提升候选用途 |
| 实际WPF/DevExpress控件、三语/UIA/IME/DPI/键盘与长稳、独立DLL发布/两个真实消费者 | IM-030本永久会话负责模块；两个产品Host负责各自正式嵌入及现场验收 | VI-U01～03/1920×1080固定viewport及真实集成尚未运行；XML/API阅读、文档自审或合成Host不证明这些门通过 |

不属于当前批准范围的内容保持§1/3.5/4/8的边界：在线自训练/生产静默采用、任意部分域训练、native抢占式取消、同handle并行比较、自动配准/曝光、缺陷命名/合并过滤、产品数据库/设备动作或质量放行。它们不被列为“以后补齐本模块”的隐含任务；新增需求须先由用户扩大范围再修本页。版本更新、当前自审不改C1～C4接收行、Core/API、911-byte向量或既有三种模型算法。

## 14. 资料与只读借鉴

- 项目内 HALCON 26.05.0.0 Operator Reference：`halcon算子手册/operators/`，尤其 `toc_inspection_variationmodel.html` 与本页列出的各 Variation Model 算子页。HALCON 语义不等于 AsunImage 包装签名。
- [PKG-026](../../shared-modules/packages/PKG-026_VariationInspection.md)、[DEV-VIS-026 §16](../../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#variation-inspection-method)、[原合同候选](../../13-contract-candidates/CONTRACT-CANDIDATES.md#variation-inspection-contract)、[DEV-VIS-020](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md)、[DEV-GOV-004](../../01-governance/DEV-GOV-004_Contract_Schema_Validator开发标准.md)、[DEV-GOV-005](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。
- 只读参考：`../../references/project-snapshots/AsunControl/20261004/original/Vision_Variation_Model\开发文档.md`。其拆分 Core/参数/UI、展示训练-prepare-compare 流程及区域结果联动可作工具组织参考；其旧参数默认、3 通道拆分、自动配准、大图裁切、并行同类 handle 和追加训练等表述不能直接迁入。当前实施唯一按本页，原语语义按HALCON 26.05、实际C#歧义按AsunImage公共签名/消费编译处理；PKG/DEV-VIS仅应用导航。
- 本次只读核查来源：`H:\docs\40-development\40-vision\2D检测器开发指导.md`，核查文件 SHA-256：`84435fbe446ba21dccace13d8bdc08cb35fa8b38eeb424e69b529082f4272d9c`。仅采纳与本模块一致的 prepared-handle 内存缓存约束：精确绑定模型内容、方法/profile、HALCON runtime 与 Adapter 能力修订；缓存项只读并以 generation 租约管理；训练/prepare 使用隔离句柄；Inspect 不隐式训练或 prepare；撤销先停止新租约、等待在途比较排空后再释放。来源中的 Create/Train/Prepare/Challenge/Publish 流程、拒绝在线吸收及候选模型外部发布等内容已有本指导覆盖；AOI Inspector、配方/历史帧/产品存储、多 ROI 聚合、面积/缺陷判定、产品 UI，以及 HALCON 24.11 参数/API结论不属于本模块可采纳范围。

### 14.1 本轮复用与目标版本证据

- 2026-10-09/10已定向读取本地26.05的create/train/prepare/prepare_direct/compare/compare_ext/get/get_thresh/clear_train/clear/read/write Variation页，以及sobel_amp、gray_range_rect、sub_image、abs_diff_image、dyn_threshold、reduce_domain、crop_part；正文落点§4.1、A.2–4。`prepare_variation_model.html` SHA256=`8d30923e9ee5ce75c555eccb188571a290539cd2b7548560e64f3a8ef07d1510`；prepare_direct=`100574644242ee27567d08ad210317ef301138e20174c842f83f1b871e44d318`；compare_ext=`1260f567051f5dcfb59325e30ccd5ab6008813fa04cec5fde79b1a0c2f2c02e1`。26.05正文公式SVG与既有25.11已阅公式逐项字节相同（目标序号0对应归档序号1，页面logo偏移，不是公式变更）；再次读既有公式图确认max/严格比较。数学约束为 `upper=i+max(A_light,B_light*v)`、`lower=i−max(A_dark,B_dark*v)`，L为c>upper、K为c<lower；等号/整数实际阈值量化另有VI-N01。只把公式匹配及目标页行为作依据，不把旧版整页自动当26.05。
- 联网实读[26.05 create](https://www.mvtec.com/doc/halcon/2605/en/create_variation_model.html)、[26.05 Direct](https://www.mvtec.com/doc/halcon/2605/en/prepare_direct_variation_model.html)，页头26.05.0.0，响应字节SHA256分别`c18710caf184be630c7d48226f0479ae6c23d4435564a37692623cf2991ca50e`、`2c4f3b01f8ce0990220073b891aca11ae30773aec9f95f73e03d78e73f8eeff0`；核位置一致、统计模式差异、Direct阈值/不保留Ref/Var。未下载新的持久快照，目标本地资料仍为实施入口；未知ddof/MAD倍率/整数饱和不补猜。
- 固定SciPy v1.16.2 commit `b1296b9b4393e251511fe8fdd3e58c22a1124899`：联网实读[`_mad_1d`/`median_abs_deviation`](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/_stats_py.py)及[`TestMedianAbsDeviation`](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/stats/tests/test_stats.py)，来源SHA256与已保留原件分别相同=`c1f98867bce4a0bdb336b6c33bd930bcf50f8b9aae6a654e1f9a6d2064bda3b4`、`3aef67e95ddaf368f647d90ab77f3757b4c24d0f15b6863562906bb7c83c4d79`；实际实现空集NaN、按axis median(abs(x−median))、normal scale作除数0.6744897501960817，测试覆盖NaN/空维/inf/轴/错误center。已读LICENSE.txt为BSD-3-Clause（SHA256=`221e59f5e910fd7f94e44f0dac77436a11338c285c6346232e4a850a50da0e94`）及pyproject（SHA256=`3f9c882e10cb29a2b4fbb59f7106fc1b7a749e6cf8c08ccd637231604dc7df7f`）：Python≥3.11、NumPy≥1.25.2,<2.6，build Meson-Python/Cython/pybind11/Pythran/NumPy。复用按样本轴、缺值/外点反例与来源隔离测试思想，落§4/10；其scale/NaN omission不是HALCON内部口径，不复制源码、不增加Python运行依赖，未运行上游测试。
- NumPy v2.3.3固定commit `f2a77a76e08719556527e0819182073fe9b5f1c3` 的`numpy/_core/_methods.py`和`tests/test_multiarray.py`复用已归档固定源码及此前阅读证据（研究定位按本节末尾原件目录）：显式dtype/n−ddof/退化值、批方差不能平均的反例。BSD-3-Clause，Python≥3.11、Meson-Python/Cython构建；不新增平台依赖。它只作统计解释/测试警戒，不实现第二Variation后端、不证明HALCON逐值等价。既有证据输入/版本未变，没有重复全审。
- 有界调度采用.NET10 BCL，而不复制队列源码。联网读取[Channels官方说明](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)；复用[现有固定源码/测试研究](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)中的dotnet/runtime v10.0.0 commit `60629d14374c56f1cb51819049ad1fa529307f8d`，BoundedChannel/BoundedChannelTests（MIT/BCL依赖）。Wait不是预留、挂起writer也可能无界、DropWrite成功不证明保留；落A.3的先接纳/预算后执行、禁止丢检测请求。实现可用内部Channel Wait+有界接纳，不把公共帧/用户回调直接放无界Channel，未运行外部测试。

原研究定位为[既有来源说明](../../../.work/variation-inspection-method-study-20260929/source.md)、[原字节清单](../../../.work/variation-inspection-method-study-20260929/sources.json)及其sources子目录；保留全部原件/hash，不把其中旧版本/候选决定当当前实施入口。2026-10-10退修再次读取三份26.05目标页Description的SVG glyph序列并与已视觉读取的公式图逐项匹配，公式/单双参数/亮暗严格边界落实§3.4；旧实施约束按原候选逐项核回§3.5/4.1/7/9/11，当前实现不依赖研究脚本或旧§16。未重复获取源码/核算子存在或依赖授权，未执行native/产品验证。

### 14.2 DevExpress官方API与限制

本工具环境没有可调用dxdocs/匹配25.2 WPF skill；官网DockLayoutManager/TableView的`?v=25.2`请求返回403，未声称已读网页。实际读取本机官方XML文档 `C:\Program Files\DevExpress 25.2\Components\Bin\Framework\`，对应已用程序集25.2.3.0；这是API资料读取，不安排安装/兼容性/授权核验。§8使用已查到的类型/属性，不从旧24.2示例推25.2签名。

| 官方文档文件/SHA256 | 已读成员及正文落点 |
|---|---|
| DevExpress.Xpf.Docking.v25.2.xml / `b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f` | DockLayoutManager/LayoutPanel/LayoutGroup、SaveLayoutToStream(System.IO.Stream)/RestoreLayoutFromStream(System.IO.Stream)；可信布局及恢复安全注意，§8.1 |
| DevExpress.Xpf.Grid.v25.2.xml / `7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd`；Grid.v25.2.Core.xml / `9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba` | GridControl/TableView/TreeListView、GridViewBase.ShowGroupPanel、TableView.AutoWidth、DataControlBase.ItemsSource/SelectedItem；表/树/图联动，不把SelectedItem作勾选训练集 |
| DevExpress.Xpf.PropertyGrid.v25.2.xml / `0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9` | PropertyGridControl.SelectedObject/PropertyDefinitions/ShowCategories，ShowCategories是枚举不是bool；草稿分组/只读高级参数 |
| DevExpress.Xpf.Charts.v25.2.xml / `2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0` | ChartControl.SelectedItem、ChartControlBase.CrosshairEnabled（nullable状态），候选表/图选择对应ordinal而非自动采用 |
| DevExpress.Xpf.Core.v25.2.xml / `cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196` | BarManager/BarButtonItem、SuperTip、Editors.Flyout.FlyoutControl与FlyoutBase.PlacementTarget；具体命令/提示/弹层，核心状态不靠popup |

来源只支持上述成员语义，未运行WPF/布局/刷新/IME/UIA/真实图像联动或性能；许可与依赖按用户基线直接使用。官方XML原件/参考项目均未修改；没有创建新快照/报告/脚本，关键算法与控件决定已留在正文，不要求开发者查临时研究脚本才能编码。

本次完成IM-REVIEW-20261009/variation-inspection的指导修订与两种反例视角（逐能力输入/算法，以及外部Host/并发生命周期）自审；仅修改本模块唯一指导。结构/引用/类型定向检查不等于真实C#编译或产品资格；未运行HALCON、AsunImage、产品构建、WPF、真实Golden、Benchmark或现场验收。

## HALCON 26.05 算子资料入口

实现 Variation Model 节点时，使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 作为目标版本 26.05 的资料入口。算子语义按本页引用资料；只有实际 C# 类型/重载/封送歧义才查 `ImageLibDotNet` 公共签名。


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

## 附录 A：Module API Contract v0.2（唯一当前模块契约；C1～C4规格已接收，N/U确定指导增量限定内容接收；实际运行/资格未就绪）

v0.2 替代未实施的旧 v0.1 入口；不是产品 C-02～C-07 的批准声明。所有类型在 `Asun.Modules.VariationInspection`，只使用 .NET 10 BCL；下面是完整公开声明形状，不含实现，未执行编译。记录构造后必须深度不可变；在接纳边界复制外部可变容器。枚举不认识的数值拒绝，数组 `default` 不当合法空数组，空数组是否允许见各字段规则。

### A.1 类型与入口声明

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
namespace Asun.Modules.VariationInspection;

public enum VariationPixelType { Byte, Int16, UInt16 }
public enum VariationMethod { Standard, Robust, Direct }
public enum VariationDirection { Absolute, Light, Dark, LightDark }
public enum SlotKind { Absolute, Light, Dark }
public enum EvidenceVerdict { Accepted, Rejected, Unknown }
public enum SamplePurpose { Training, Validation, IndependentTest }
public enum DirectConstruction { ExternalMap, Sobel3 }
public enum LoadPurpose { CandidatePreview, ProductionRead }
public enum CoverageQuality { Complete, IncompleteSupport, InputNotQualified }
public enum OperationState {
    Validating, Rejected, Accepted, Queued, Running, Draining, DrainUnknown,
    Drained, ResourcesReleased, Completed, Cancelled, TimedOut, Failed
}
public enum VariationError {
    InvalidParameter, UnsupportedInput, ReferenceMismatch, IncompleteSupport,
    InsufficientTrainingSet, ModelStateInvalid, ResourceBudgetExceeded,
    Cancelled, DeadlineExceeded, AdapterFailure, PersistenceFailure,
    InternalFailure, DuplicateConflict, RequestExpired, ModuleClosing,
    InputNotQualified, ReadBackMismatch, NoFeasibleCandidate
}
public enum DrainState { Drained, DrainUnknown }
public enum SuggestionState { Selected, NoFeasibleCandidate, Incomplete }
public enum DiagnosticKind { Ideal, Variation, LowerThreshold, UpperThreshold }
public enum QueryAvailability { Available, Unsupported }
public enum DiagnosticPixelType { Byte, Int16, UInt16, Real32, Real64 }
public enum GroundTruthOrigin { RealObservation, Synthetic, Analytical }

public readonly record struct ContentReference(string Id, string Revision, string Sha256);
public readonly record struct OperationKey(Guid InstanceId, long Sequence);
public readonly record struct PixelRun(int Row, int FirstColumn, int LastColumn);
public sealed record PixelRegion(int Width, int Height, ImmutableArray<PixelRun> Runs);
public sealed record ThresholdPair(double Light, double Dark);
public sealed record GateEvidence(EvidenceVerdict Verdict, ContentReference Evidence);
public sealed record InputEvidence(GateEvidence IndependentAlignment,
    GateEvidence Illumination, GateEvidence ImageQuality,
    EvidenceVerdict FootprintSupport, ContentReference FootprintEvidence);
public sealed record FrameReference(ContentReference Content, int Width, int Height,
    VariationPixelType PixelType, int EffectiveBits, string ReferenceGridId,
    string ProcessingHash, string PixelHash, int GridRowOrigin, int GridColumnOrigin,
    PixelRegion ValidSupport, InputEvidence Evidence);
public sealed record QualifiedSample(FrameReference Frame, string SourceGroupId,
    SamplePurpose Purpose, ContentReference Observation, ContentReference Qualification);
public sealed record DirectModelSource(DirectConstruction Construction,
    FrameReference ReferenceImage, FrameReference? VariationImage,
    FrameReference? SobelSource,
    ImmutableArray<string> SourceGroupIds,
    ContentReference ConstructionEvidence);
public sealed record MethodSnapshot(VariationMethod Method, VariationPixelType PixelType,
    int Width, int Height, int EffectiveBits, string ReferenceGridId,
    string ProcessingHash, PixelRegion InspectionDomain, PixelRegion ExclusionDomain,
    ContentReference DomainSource, ThresholdPair AbsoluteThreshold,
    ThresholdPair VariationThreshold, VariationDirection Direction,
    ContentReference Applicability, ContentReference QualificationProfile);
public sealed record TrainingSnapshot(MethodSnapshot Method,
    ImmutableArray<QualifiedSample> Samples, DirectModelSource? DirectSource);
public sealed record RequestHeader(OperationKey Key, string RequestRevision,
    DateTimeOffset DeadlineUtc);
public sealed record VariationResourceBudget(long MaxWorkingBytes, int MaxTrainingFrames,
    int MaxRegionRuns, int MaxOutputBytes, int MaxModelBytes, int MaxDiagnosticBytes,
    int MaxEvaluationFrames, int MaxSuggestionCandidates);
public sealed record VariationModuleOptions(int MaxConcurrentOperations,
    int MaxQueuedOperations, int MaxRetainedOperations, int MaxLoadedModels,
    int EventCapacityPerOperation, int MaxMetadataRuns, int MaxMetadataBytes,
    long MaxResidentBytes, TimeSpan DefaultDrainWait);
public sealed record FieldIssue(string FieldPath, VariationError Error, string ResourceKey);
public sealed record ValidationResult(ImmutableArray<FieldIssue> Issues);
public sealed record VariationFailure(VariationError Error, string Stage,
    string ResourceKey, bool RetryWithNewRequest, ContentReference? Evidence);
public sealed record VariationCapabilities(Guid InstanceId, string ContractVersion,
    string BackendRevision, string HalconRuntimeRevision, bool IsSimulator,
    long TimestampFrequency, ContentReference NumericEncodingEvidence,
    ImmutableArray<VariationPixelType> PixelTypes, ImmutableArray<VariationMethod> Methods,
    ImmutableArray<DiagnosticKind> ReadableDiagnostics);
public sealed record ModelManifest(MethodSnapshot Method, string MethodHash,
    string TrainingHash, ImmutableArray<QualifiedSample> TrainingSources,
    DirectModelSource? DirectSource, bool TrainingDataCleared,
    string ContractVersion, string BackendRevision, string HalconRuntimeRevision);
public sealed record NativeModelPayload(string Format, ImmutableArray<byte> Bytes,
    string Sha256);
public sealed record ModelPackage(ModelManifest Manifest, NativeModelPayload Payload,
    string PackageHash);
public sealed record DiagnosticImage(DiagnosticKind Kind, QueryAvailability Availability,
    DiagnosticPixelType? PixelType, int Width, int Height, int StrideBytes,
    ImmutableArray<byte> Pixels, string? ContentHash);
public sealed record ModelDiagnostics(string PackageHash,
    ImmutableArray<DiagnosticImage> Images);
public sealed record VariationModelCandidate(ModelPackage Package, ModelDiagnostics Diagnostics);
public readonly record struct RuntimeModelToken(Guid InstanceId, long Epoch,
    string PackageHash, string MethodHash, LoadPurpose Purpose);
public sealed record DifferenceSlot(SlotKind Kind, PixelRegion Region);
public sealed record ComparisonResult(OperationKey Operation, RuntimeModelToken Model,
    ContentReference Input, VariationDirection RequestedDirection,
    ImmutableArray<DifferenceSlot> Slots, PixelRegion Evaluated,
    PixelRegion NoCandidate, PixelRegion Unknown, CoverageQuality Quality,
    ImmutableArray<VariationFailure> Reasons);
public sealed record GoldenFixture(FrameReference Frame,
    ImmutableArray<DifferenceSlot> ExpectedSlots, PixelRegion ExpectedEvaluated,
    PixelRegion ExpectedNoCandidate, PixelRegion ExpectedUnknown);
public sealed record ReadBackReport(string PackageHash, bool BytesVerified,
    bool GoldenVerified, ImmutableArray<DiagnosticKind> UnsupportedQueries);
public sealed record LoadedModel(RuntimeModelToken Runtime, ReadBackReport Report);
public sealed record BuildRequest(RequestHeader Header, TrainingSnapshot Snapshot,
    VariationResourceBudget Budget, bool ClearTrainingData);
public sealed record LoadRequest(RequestHeader Header, ModelPackage Package,
    LoadPurpose Purpose, ContentReference? SealedContent,
    ImmutableArray<GoldenFixture> Golden, VariationResourceBudget Budget);
public sealed record VariationRequest(RequestHeader Header, RuntimeModelToken Runtime,
    FrameReference Input, VariationResourceBudget Budget);
public sealed record DiagnosticRequest(RequestHeader Header, RuntimeModelToken Runtime,
    ImmutableArray<DiagnosticKind> Kinds, VariationResourceBudget Budget);
public sealed record UnloadRequest(RequestHeader Header, RuntimeModelToken Runtime);
public sealed record LabelledFrame(QualifiedSample Sample,
    ImmutableArray<DifferenceSlot> ExpectedCandidates, ContentReference GroundTruth,
    GroundTruthOrigin TruthOrigin);
public sealed record ExposureHistory(ContentReference Record,
    ImmutableArray<string> ValidationGroupIds);
public sealed record EvaluationRequest(RequestHeader Header, RuntimeModelToken Runtime,
    SamplePurpose Purpose, ImmutableArray<LabelledFrame> Frames,
    ExposureHistory Exposure, VariationResourceBudget Budget);
public sealed record EvaluationItem(ContentReference Input, OperationState State,
    ComparisonResult? Comparison, long? TruePositivePixels, long? FalsePositivePixels,
    long? FalseNegativePixels, VariationFailure? Failure);
public sealed record EvaluationReport(string PackageHash, SamplePurpose Purpose,
    int PlannedFrames, int CompletedFrames, int UnknownFrames, int DefectFrames,
    int RealDefectFrames, int GoodFrames, int RealGoodFrames,
    int MissedDefectFrames, int FalseAlarmGoodFrames,
    ImmutableArray<EvaluationItem> Items, bool MetricsEvaluated);
public sealed record SelectionPolicy(double MinAbsolute, double MaxAbsolute,
    double MinVariation, double MaxVariation, int MaxMissedDefectFrames,
    int MaxFalseAlarmGoodFrames, bool RequireRealEvidence);
public sealed record RecommendationRequest(RequestHeader Header, TrainingSnapshot Training,
    ImmutableArray<MethodSnapshot> Candidates, ImmutableArray<LabelledFrame> Validation,
    SelectionPolicy Policy, TimeSpan PerCandidateDeadline, VariationResourceBudget Budget);
public sealed record CandidateScore(int Ordinal, string MethodHash, EvaluationReport? Report,
    VariationFailure? Failure);
public sealed record ParameterSuggestion(SuggestionState State, int? SelectedOrdinal,
    ImmutableArray<CandidateScore> Scores, bool RealEvidenceComplete);
public sealed record UnitReceipt();
public sealed record StageTiming(string Stage, TimeSpan Duration, bool Completed);
public sealed record ResourceCounters(long ReservedBytes, long ManagedBytes,
    long? NativeBytes, int FrameLeases, int Models, int RegionRuns, int QueuedRequests,
    long ReservedScratchBytes, int ScratchFiles);
public sealed record OperationMetrics(ImmutableArray<StageTiming> Stages,
    TimeSpan? AcceptedToResourcesReleased, TimeSpan? CancellationToDrained,
    TimeSpan? CancellationToResourcesReleased, long PeakManagedBytes,
    long? PeakNativeBytes, bool NativeAccountingVerified);
public sealed record OperationResult<T>(OperationKey Key, OperationState State,
    T? Value, VariationFailure? Failure, OperationMetrics Metrics) where T : class;
public sealed record OperationSnapshot(OperationKey Key, OperationState State,
    long LastEventSequence, bool CancellationRequested, VariationFailure? Failure,
    ResourceCounters Resources);
public sealed record VariationEvent(OperationKey Key, long Sequence, OperationState State,
    string Stage, int CompletedUnits, int PlannedUnits, long TimestampTicks,
    VariationFailure? Failure);
public sealed record EventBatch(long FirstAvailableSequence, long LastSequence,
    ImmutableArray<VariationEvent> Events);
public sealed record DrainReceipt(DrainState State, ImmutableArray<OperationKey> Pending,
    ImmutableArray<RuntimeModelToken> PendingModels, long HeldBytes);

public interface IVariationOperation<T> where T : class {
    OperationKey Key { get; }
    Task<OperationResult<T>> Completion { get; }
    OperationSnapshot Query();
    EventBatch ReadEvents(long afterSequence, int maxCount);
    void RequestCancellation();
}
public interface IVariationInspectionModule : IAsyncDisposable {
    VariationCapabilities GetCapabilities();
    string ComputeMethodHash(MethodSnapshot snapshot);
    ValidationResult ValidateTraining(TrainingSnapshot snapshot);
    IVariationOperation<VariationModelCandidate> BuildCandidate(BuildRequest request, CancellationToken ct);
    IVariationOperation<LoadedModel> Load(LoadRequest request, CancellationToken ct);
    IVariationOperation<ComparisonResult> Compare(VariationRequest request, CancellationToken ct);
    IVariationOperation<ModelDiagnostics> ReadDiagnostics(DiagnosticRequest request, CancellationToken ct);
    IVariationOperation<EvaluationReport> Evaluate(EvaluationRequest request, CancellationToken ct);
    IVariationOperation<ParameterSuggestion> Recommend(RecommendationRequest request, CancellationToken ct);
    IVariationOperation<UnitReceipt> Unload(UnloadRequest request, CancellationToken ct);
    OperationSnapshot? Query(OperationKey key);
    bool ReleaseOperation(OperationKey key);
    ValueTask<DrainReceipt> StopAndDrainAsync(DateTimeOffset deadlineUtc, CancellationToken waitCancellation);
}
public static class VariationModule {
    public static IVariationInspectionModule Create(VariationModuleOptions options,
        IVariationBackend backend, IFrameSource frames, TimeProvider timeProvider)
        => throw new NotImplementedException(); // 声明占位；不是产品实现
}

// 技术适配端口：不传 SDK handle，模型仅在 Core 与注入的 Backend 间借用。
public interface IFrameLease : IAsyncDisposable {
    FrameReference Reference { get; }
    ReadOnlyMemory<byte> Pixels { get; }
    int StrideBytes { get; }
    long StorageBytes { get; }
}
public interface IFrameSource {
    ValueTask<IFrameLease> AcquireAsync(FrameReference reference, CancellationToken ct);
}
public interface IBackendModel : IAsyncDisposable { }
public sealed record BackendComparison(ImmutableArray<DifferenceSlot> Slots);
public sealed record BackendResourceEstimate(long ResidentModelBytes,
    long PeakTemporaryBytes, ContentReference ReservationProfile);
public sealed record BackendResourceUsage(long? CurrentNativeBytes,
    long? PeakNativeBytes, bool NativeAccountingVerified,
    long ReservedScratchBytes, int ScratchFiles);
public interface IVariationBackend : IAsyncDisposable {
    VariationCapabilities GetCapabilities(Guid instanceId);
    BackendResourceUsage GetResourceUsage();
    BackendResourceEstimate Estimate(MethodSnapshot method, int trainingFrames,
        int simultaneouslyHeldFrames, bool includesFreshReadback);
    ValueTask<IBackendModel> CreateAsync(MethodSnapshot method, CancellationToken ct);
    ValueTask TrainAsync(IBackendModel model, ImmutableArray<IFrameLease> frames,
        VariationMethod method, CancellationToken ct);
    ValueTask PrepareAsync(IBackendModel model, MethodSnapshot method,
        IFrameLease? reference, IFrameLease? variation, IFrameLease? sobelSource,
        DirectConstruction? construction,
        CancellationToken ct);
    ValueTask<ImmutableArray<DiagnosticImage>> ReadDiagnosticsAsync(IBackendModel model,
        ImmutableArray<DiagnosticKind> kinds, int maxBytes, CancellationToken ct);
    ValueTask ClearTrainingDataAsync(IBackendModel model, CancellationToken ct);
    ValueTask<NativeModelPayload> SerializeAsync(IBackendModel model, int maxBytes, CancellationToken ct);
    ValueTask<IBackendModel> ReadFreshAsync(NativeModelPayload payload, CancellationToken ct);
    ValueTask<BackendComparison> CompareAsync(IBackendModel model, IFrameLease frame,
        VariationDirection direction, int maxRuns, CancellationToken ct);
}
```

### A.2 字段有效域、内容身份与所有权

| 类型/字段 | 必需校验与唯一语义 |
|---|---|
| ContentReference | Id/Revision 非空、Ordinal 比较，Sha256 为64个小写十六进制字符；是来源定位与内容证据，不证明用途批准。不得用路径/latest补全。所有公开字符串 UTF-8 长度≤4,096字节；Stage/FieldPath/ResourceKey≤256字节，超额拒绝 |
| PixelRegion | 固定 W/H 与方法一致；坐标单位 pixel，0-based，行列闭区间；Runs 按 Row/FirstColumn 排序、同排不重叠且相邻段合并。空=ImmutableArray.Empty；不接受越界/反向/重复段。面积用 checked long 累加；R 是 [0,H−1]×[0,W−1]，D非空且与 I 不相交。最大游程数受 Budget/构造时 ModuleOptions 对应资源控制，不先分配完整 bool 矩阵 |
| MethodSnapshot | W/H>0，W×H×每像素字节及 stride 检查溢出；Byte EffectiveBits=1..8，Int16=1..16，UInt16=1..16；有效位深描述不能自行量化图。ReferenceGridId、ProcessingHash（SHA256）、Applicability、QualificationProfile、DomainSource 均必需；阈值用显式亮暗对，单值输入由 Host 明确展开。R父格映射由参考格证据持有；不在模块拟合 |
| FrameReference/租约 | 训练/比较/Direct Reference/Variation元数据与方法匹配，GridRowOrigin/GridColumnOrigin=0；ValidSupport/FootprintSupport合格才可native。Content引用上游帧证据的序列化hash，不能直接当CPU内存hash；PixelHash独立为原始有效行像素（忽略padding）从上至下串接SHA256，由Core在租约内增量核验。帧端口核Content来源hash，Core核元数据/PixelHash。CPU行存储单通道little-endian，stride≥W×元素字节且为元素字节倍数，Pixels.Length≥(H−1)×stride+W×元素字节并≤int.MaxValue，StorageBytes≥Pixels.Length。不可截断有效位/负数。超大图走固定块；Pixels只在租约期间有效；Host持父帧、端口返独立租约，Backend不归还父帧、不执行采集/配准/曝光 |
| TrainingSnapshot | Standard/Robust ≥2独立组且≤min(65,535,MaxTrainingFrames)，Samples Purpose=Training，按明确顺序处理；Observation表示真实采集观察，重复Observation或同Frame.Content.Id/Revision拒绝，重拍/增强仍同SourceGroupId。不同真实独立观察恰好同像素字节是合法常数样本，不能只因hash相等删除；资格/组事实由Host确认。Direct接受空Samples+DirectSource；Reference必需，ExternalMap的Variation必需、非负、与模型同PixelType，SobelSource=null；Sobel3的Variation=null、SobelSource必需，且Reference/Source均Byte。Source尺寸=W+2/H+2、格原点=−1/−1、全图完整真实支持；其中央裁出W/H必须逐字节等于Reference，处理链/格/位深一致。Backend在Source上sobel_amp，再crop_part(row=1,col=1,W,H)取得v，不使用Source最外边界结果；所有两帧及派生图至Prepare返回保持。此真实halo是工程构造输入，不新增配准职责 |
| Budget/Options | working/resident字节>0，所有数量/字节上限>0，Concurrent/Retained/Loaded/EventCapacity/MetadataRuns/MetadataBytes>0，Queued可为0；DefaultDrainWait>0有限。请求额度须在模块总预算内；入队也占资源槽。MaxMetadataRuns限制每个区域及请求累计游程，MaxMetadataBytes限制canonical请求/manifest和event摘要累计。Backend.Estimate返回非负模型/暂态字节及显式ReservationProfile，Core加上实际输入stride/输出/诊断/byte包/fresh双实例所需容量核MaxWorkingBytes；没有适用预留Profile或估计超过预算，在native前拒绝，不假设暂态为0。实例预留采用整个请求MaxWorkingBytes直到实际释放；Loaded常驻及保留operation托管结果另计，预留转长期持有时只转移记账、避免重复物理计数。所有int/long checked，单缓冲≤int.MaxValue。MaxEvaluationFrames限制每候选及全搜索累计帧比较数；MaxSuggestionCandidates限制候选数。Host持有结果在ReleaseOperation之后的内存由Host预算负责 |
| ModelManifest/Package | Manifest 固定方法及训练/Direct来源，无产品BOM/程序状态。NativePayload SHA256由 Core 对真实 Bytes 重算，Format 固定 `halcon-variation/vam`，模拟端固定 `variation-simulator/v1`，两者不互读。PackageHash绑定 Manifest+Payload.Sha256；负载/依赖不完整拒绝。TrainingDataCleared 表示不能重训，Direct 永远不要求保存 native i/v。包字节与诊断为有界托管不可变复制，调用方持有；没有 native输出租约或 Dispose 义务 |
| RuntimeModelToken | 仅在创建它的 InstanceId 有效，Epoch 单调且不复用，精确 Package/MethodHash/Purpose必须匹配注册实例。注册只是实例资源表，不是资产注册表/用途Owner。Unload 后旧 token 无效；回退也是新 Load/new Epoch，不接受A→B→A旧token |
| DiagnosticImage | Available 时 PixelType/ContentHash必需，W/H与R相同，stride/长度 checked，内容hash实际重算，Real图保留真实32/64位而不量化；Unsupported 时 W/H/stride=0、Pixels空、类型/hash=null。返回所有请求槽，缺项为 AdapterFailure；Direct i/v和清训练后i/v为 Unsupported。数据只用于诊断投影，不当方法重建值 |
| Golden/LabelledFrame | Frame属于同方法，Expected槽种类/数目与方向精确一致，E/N/U守恒且候选⊆E；Golden是内容精确fixture，不是客户质量结论。评价GroundTruth必需、同方向、D内；Purpose只能Validation或IndependentTest且每Sample.Purpose匹配。重复Observation或相同Frame.Content.Id/Revision成员拒绝，组与训练不相交；IndependentTest须Exposure.Record和完整ValidationGroupIds（含历史已曝光组），不与其相交；显式空Exposure数组只表示外部Owner确认从未曝光，不能代Unknown。TruthOrigin区分真实/合成/解析；RealDefectFrames/RealGoodFrames任一=0或UnknownFrames>0时MetricsEvaluated=false。模拟Backend的指标仅为synthetic诊断，不计真实资格 |
| Result/Errors | Completed须Value非null、Failure=null；Rejected/Failed/Cancelled/TimedOut须Failure非null，Value可为明确 partial Evaluate/Recommend/Comparison，绝不能有部分 ModelCandidate/LoadedModel。未处理像素记U，不用默认Region填空。错误不携带原始异常敏感串；Stage/ResourceKey映射三语。NoFeasibleCandidate为完成的建议状态，不是运行崩溃 |

内容散列编码固定为 `VI-CANONICAL-1`，使用目标.NET10 BCL的Utf8JsonWriter；完整Writer Options冻结为下列值，不依靠默认Options或宿主JsonSerializerOptions：

```csharp
new System.Text.Json.JsonWriterOptions {
    Encoder = System.Text.Encodings.Web.JavaScriptEncoder.Default,
    Indented = false,
    IndentCharacter = ' ',
    IndentSize = 2,
    NewLine = "\n",
    MaxDepth = 64,
    SkipValidation = false
}
```

直接写UTF8缓冲，Flush后只散列已写字节，无BOM、无开头/结尾空格、无行尾LF/CRLF；NewLine/Indent选项显式固定但在Indented=false下不产生字符。字段名和字符串值均用此同一encoder的WritePropertyName/WriteString字符串重载，不提前自定义JsonEncodedText、不用UnsafeRelaxedJsonEscaping、WriteRawValue或反射序列化。字符串按原Unicode序列写，不归一化；先拒绝不成对UTF16 surrogate，不以替换字符悄然改变身份。非ASCII/HTML敏感字符使用Default的JSON转义，固定向量中的`参考<&"`对应`\u53C2\u8003\u003C\u0026\u0022`；运行时更新必须复跑字节一致断言，不能静默改变VI-CANONICAL-1或改成JCS。

对象字段逐一按本附录record声明顺序写，名称大小写精确，不按alphabet排序。必需字段先校验，缺值拒绝；nullable字段有值递归写该值，无值在其原字段位置WriteNull，绝不omit-null/补默认对象；空合法数组写`[]`，default数组拒绝。枚举用显式有效值映射写A.1拼写字符串（例如`Standard`/`Byte`/`LightDark`），不允许数字、大小写变体或Enum.ToString对未知值的回退；bool写JSON true/false。int字段调用WriteNumber的Int32重载、long/TimeSpan.Ticks用Int64重载；ThresholdPair.Light/Dark为double，先核有限及有效域，将正/负零均归一为正`0d`后调用Double重载（例如5d写5，不额外写5.0），不先转decimal、文化格式字符串或自定义浮点文本。日期字段（RequestHeader.DeadlineUtc）先按字段规则核UTC，再以`DateTimeOffset.ToUniversalTime().ToString("O", CultureInfo.InvariantCulture)`产生字符串，必须七位小数及`+00:00`，再用WriteString；不调用Writer的日期重载、不裁小数/改Z。编码探针：`2026-10-10T00:00:00.0000000+00:00`的JSON字符串字节为`"2026-10-10T00:00:00.0000000\u002B00:00"`。Guid同样先ToString("D",InvariantCulture)得到小写形式再WriteString；数组保留有语义顺序，区域先按有效域核规范游程。

Hash字段不进入自身散列：MethodHash=SHA256(MethodSnapshot的canonical字节)，TrainingHash=SHA256(TrainingSnapshot)，PackageHash=SHA256(ModelManifest与Payload.Format/Sha256)，不含Bytes/PackageHash，散列返回64字符小写十六进制。canonical写入前校验，溢出/深度/额度不合法拒绝，不输出partial hash；引用的Sha256仍保留，避免metadata与native字节相互写回。请求去重摘要包含入口名、请求载荷（包括Header全部字段）、Budget和token，排除CancellationToken；ComputeMethodHash只计算方法，不发布/激活。

canonical容器形状精确：TrainingSnapshot字段为Method/Samples/DirectSource；Package散列根对象按序为Manifest/Format/Sha256，Manifest按声明全部字段并含MethodHash/TrainingHash（它们是子内容hash、无循环），Payload.Bytes不写入；request摘要根对象按序EntryPoint/Request，字段大小写与声明一致。Guid写小写`D`，TimeSpan写Ticks整数，nullable缺值写null，所有数组按声明值逐项写，不得改成dictionary、omit-null或默认JsonSerializer反射字段顺序。DiagnosticImage hash只核实际行像素字节，忽略stride padding；Package Format不是文件名/扩展推得，显式固定。模型源Samples/DirectSource应与TrainingHash一致，Load用Manifest.Method/TrainingSources/DirectSource重建TrainingSnapshot重算，不接受Host只传不相符hash。

固定向量`VI-METHOD-CANON-01`使用§10.1现有4×2完整域夹具的合法MethodSnapshot，不需要训练/native才可ComputeMethodHash；补齐如下确定输入。以下SHA只绑定解析fixture原字节，不表示外部生产资格：ProcessingHash/各ContentReference.Sha256分别为UTF8无BOM、无换行的`vi-processing-v1`、`vi-domain-v1`、`vi-applicability-v1`、`vi-qualification-v1`的SHA256。

| 字段（按声明次序） | 固定值 |
|---|---|
| Method / PixelType / Width / Height / EffectiveBits | Standard / Byte / 4 / 2 / 8 |
| ReferenceGridId | 字符序列`grid/参考<&"`（末尾是一个双引号，无反斜杠；与所有fixture帧保持同一格） |
| ProcessingHash | `042d19ed94a6d301fcc65cba9c380f00eb76178b8c8d0ff3a292636f29f3d0ec` |
| InspectionDomain | Width=4，Height=2；Runs按序为PixelRun(0,0,3)、PixelRun(1,0,3) |
| ExclusionDomain | Width=4，Height=2；Runs=ImmutableArray.Empty |
| DomainSource | Id=`domain-4x2`，Revision=`1`，Sha256=`feac4bd0d3bf5d74974cbfd4e23c0c325ca9b838801136faca9ae6c03870791c` |
| AbsoluteThreshold / VariationThreshold / Direction | ThresholdPair(5d,8d) / ThresholdPair(2d,1d) / LightDark |
| Applicability | Id=`applicability-4x2`，Revision=`1`，Sha256=`83b8f00f18d52e4165a94fb4ad554652b6ac12980be13d22162ccc95b7279446` |
| QualificationProfile | Id=`qualification-4x2`，Revision=`1`，Sha256=`b55b754d028c575454d96aa226313a2a41e3ab717376c327925d1b6848d2dc32` |

完整canonical UTF8字符串如下，仅这一物理单行的字节属于向量；代码围栏和显示换行均不参与散列，`\u`为JSON中的实际ASCII反斜杠序列，不先解码成中文再散列：

```json
{"Method":"Standard","PixelType":"Byte","Width":4,"Height":2,"EffectiveBits":8,"ReferenceGridId":"grid/\u53C2\u8003\u003C\u0026\u0022","ProcessingHash":"042d19ed94a6d301fcc65cba9c380f00eb76178b8c8d0ff3a292636f29f3d0ec","InspectionDomain":{"Width":4,"Height":2,"Runs":[{"Row":0,"FirstColumn":0,"LastColumn":3},{"Row":1,"FirstColumn":0,"LastColumn":3}]},"ExclusionDomain":{"Width":4,"Height":2,"Runs":[]},"DomainSource":{"Id":"domain-4x2","Revision":"1","Sha256":"feac4bd0d3bf5d74974cbfd4e23c0c325ca9b838801136faca9ae6c03870791c"},"AbsoluteThreshold":{"Light":5,"Dark":8},"VariationThreshold":{"Light":2,"Dark":1},"Direction":"LightDark","Applicability":{"Id":"applicability-4x2","Revision":"1","Sha256":"83b8f00f18d52e4165a94fb4ad554652b6ac12980be13d22162ccc95b7279446"},"QualificationProfile":{"Id":"qualification-4x2","Revision":"1","Sha256":"b55b754d028c575454d96aa226313a2a41e3ab717376c327925d1b6848d2dc32"}}
```

UTF8 byte长度=`911`；MethodHash=`eeb9d16a38fcf8e351ff045d8e22957838292b39da40395f20026457e39923b2`。VI-C02b必须从表中输入独立构造MethodSnapshot，逐字段Writer输出与此完整字节比较；expected是本文固定字节和hash，不能由待测ComputeMethodHash/相同序列化函数现算。附加codec探针核有效Standard训练的DirectSource在原位置为JSON null，nullable有值写实际对象；未知enum预检拒绝、不写数字；日期字符串按上述固定转义；将合法阈值0d换成负零时canonical仍为同一0/hash，而改变A.Light=5→6或方向时hash改变；中文未经encoder或CRLF/BOM误混入必须字节不等。探针只通过现有ComputeMethodHash、模块校验/去重或测试内部Writer观察，不新增公开codec/产品入口。

本次在内存调用实际.NET10 Utf8JsonWriter逐字段生成，并用独立输入/独立字符串转义及SHA256重算该向量；不创建工程或脚本文件。这只确认本文固定编码向量，不表示Core产品实现/测试Exe、HALCON、WPF、Golden或性能已执行。

整数CPU输入/输出为little-endian 8/16位；Real32/Real64诊断为IEEE754 little-endian，仅Adapter按实际图型复制，不用BCL统计重建。GetCapabilities.NumericEncodingEvidence绑定实际公开图读取/复制类型语义和fixture；Simulator用固定解析证据。诊断图若出现NaN/Inf，不以0代替：保留原始位型并标图表无法计量（UI键Variation.NonFiniteDiagnostic），后续处理该值不能作为合法Direct输入。JSON canonical不序列化图像浮点像素、只绑定byte hash，有限阈值要求仍严格。BackendRevision、runtime和数值编码证据需真实匹配才能N接收，不把文档声明当真实native验证。

DirectSource.SourceGroupIds必需有界且去重按Ordinal排序，来自Reference/v/构造素材全部硬同源组；ExternalMap也不能遗漏v拟合组。Evaluate/Recommend的Validation/Test与这些组及TrainingSources组均不交叉；Direct无训练Samples不是“无需隔离”。PerCandidateDeadline>0有限且不超过请求接纳剩余deadline，每候选从本候选派发开始用单调时钟计算，先到全局/候选deadline停止后续派发；候选已开始的native仍真实排空才能结束。SelectionPolicy范围有限且0≤Min≤Max，误报/漏检上限≥0，候选数组非空/无重复MethodHash/仅A/B变化；SourceGroupId/Exposure.ValidationGroupIds长度受MaxMetadataBytes，不容许无限来源历史。

Metrics.Stages使用模块单调时钟计时，stage名称取§11固定表；Acquire、底层调用、释放从真实进入计至真实返回，不以CancellationToken触发当结束。完成前的阶段Completed=false；未接纳AcceptedToResourcesReleased=null；NativeBytes/PeakNativeBytes未知为null，BackendResourceUsage只提供计数、不影响结果/质量。Core按每次完成/边界采样及Backend提供的原生峰值合并，不能声称采样抓住未报告的所有native暂态峰值；NativeAccountingVerified需真实profile/adapter证据。ResourceCounters.Models包括隔离/pending unload/fresh实例，FrameLeases含在途Acquire迟到已取得租约；ReservedScratchBytes/ScratchFiles按本operation的申请/归还账本投影，backend总计由A.6提供，模拟器两项为0。scratch不加进NativeBytes/HeldBytes，未确认归还保留Pending；错误计账不归零隐藏资源。

### A.3 接纳、重复、释放与适配失败

Host 从 GetCapabilities 取 InstanceId，并串行发起短接纳调用，Sequence 从1单调递增；同实例由Host维护一个序列分配器，多UI调用不能各自产生冲突Sequence。并发执行通过内部队列进行，接纳锁线性化，拿不到队列/运行/保留/资源额度立即Rejected，不无界等写者。Key实例不符或非正序号拒绝。已保留同Key+同摘要+同入口返回同operation/Completion，不重复工作；不同载荷DuplicateConflict不改原任务；已释放/未保留且≤接纳高水位RequestExpired。未接纳结构拒绝不更新高水位；Host更正用新Sequence。MaxRetainedOperations含运行/终态槽，满则拒绝，不自动淘汰原查询。ReleaseOperation仅终态资源已归还true并移除记录，未终态false；已移除true；对别实例Key为ArgumentException、不释放别实例。Host仍持的托管结果归Host预算。

同Key重取operation不把新CancellationToken注册到原请求，仅首次接纳的token生效；需要撤销原任务用返回handle.RequestCancellation。DuplicateConflict返回只读Rejected handle，它不写入原Key注册/事件环；Query(Key)仍指原操作，调用者必须读这次入口返回的Completion，不能把Query原结果当重复提交已成功。接纳前token已取消为Rejected+Cancelled且无资源，已接纳后取消走完整排空链。Unload只有成功接纳才关闭该token的新租约，预检/额度拒绝不改变模型准入；StopAndDrain一旦调用进入closing不可撤销。

DeadlineUtc 必须为UTC、晚于接纳时刻；入队开始就消耗总预算。TimeProvider.GetUtcNow只在接纳转换剩余时长，运行用GetTimestamp/ElapsedTime推进，墙钟跳变不延长已接纳任务；事件TimestampTicks用该TimeProvider单位、TimestampFrequency给换算。剩余deadline不得超过TimeSpan.FromMilliseconds(uint.MaxValue−1)的BCL定时器范围（约49.7天，工程上限而非工艺默认）；DefaultDrainWait/PerCandidateDeadline同域，拒绝Timeout.InfiniteTimeSpan。GetCapabilities/Validate/ComputeHash同步无IO，ComputeHash非法输入抛ArgumentException；Query未知/已释放null。ReadEvents afterSequence≥0、maxCount=1..EventCapacity；非法ArgumentOutOfRangeException，不改operation；环丢序显式报告，终态仍存Query/Completion。

Build/Create/Train/Prepare/Serialize 任一步失败都销毁隔离工作实例，真实退出后归还帧；不重试可能已变更的同 handle。Standard 每次 TrainAsync 传一个租约并顺序累计；Robust 仅一次传全集；Direct 不 Train。Backend完成值表示底层调用真正返回，禁止早返回Task后后台继续使用资源。CancellationToken只在安全边界检查；未返回、异常释放不确定或帧端口未排空均保持 DrainUnknown，Completion不结束，继续Query原操作。DisposeAsync 按 DefaultDrainWait调用关闭，未排空时抛带DrainReceipt的模块关闭异常并保留实例；后续可重试StopAndDrain，不能释放Backend。成功重复Dispose安全。

Backend/Core共同捕获已归还资源的可分类故障；扩展公开 `VariationBackendException : Exception`，只读属性 `VariationError Error`、`string Stage`、`ContentReference? Evidence`，构造 `(VariationError error, string stage, ContentReference? evidence, Exception? inner)`；`VariationCloseException : Exception` 只读 `DrainReceipt Receipt`、构造 `(DrainReceipt receipt)`。未知异常为InternalFailure，不映射无差异。参数Validator返回FieldIssue，不调用Backend。Null请求/对象、非法枚举、数组default、Hash不符、预算越界为Rejected；取得租约/native后发现错误为Failed并走完整释放链。OOM不能承诺绝不发生；预估预算拒绝在先，实际OOM尝试按现有所有权清账，底层状态未知继续隔离，不能伪造已释放。

Unload先原子停止该 token 新租约，再等待已有compare/read/evaluate真实退出，再Dispose模型；排队Unload不能被持续新比较饿死。Unload期限到达返回非终态DrainUnknown，保留原操作；其它独立模型可继续运行但被隔离资源仍占总预算。模块StopAndDrain使所有模型停止新准入、取消运行操作并释放未开始队列；waitCancellation只取消本次等待，返回DrainUnknown，绝不重新开放准入。内部worker不需要UI或订阅者。保持可查询的 pending keys与模型token，确实已退出后发Drained/ResourcesReleased/唯一终态。恢复是等待原worker退出后Unload/新Load，不是native未退就换backend或重训。

StopAndDrain的UTC deadline只限制本次等待，不是新工作请求；到调用时已经过期仍先线性化closing，再立即返Drained或DrainUnknown快照，不能因等待预算耗尽跳过关闭。实例级Drained回执须所有工作调用/帧/临时物/Loaded模型/scratch均实际归还且Backend.DisposeAsync成功；Backend只Dispose一次，随后module.DisposeAsync仅完成/重入同一关闭并清托管调度，不重复释放Backend。操作级Drained事件不等于实例级Drained回执。帧/模型/暂存释放未知保留对应原operation或PendingModels及Owner；仅Backend退出未知时Pending/PendingModels可以为空，但State仍为DrainUnknown，原Owner继续观察同实例Stop，不以HeldBytes=0假报实例Drained；只终态记录尚保留不阻真实排空，Query/Release仍可用。§4.4清理阶段共用一个有限总预算，逐token观察不能逐次重置成无界期限。

### A.4 工程候选与生产读取

BuildCandidate只返回新候选包和诊断，不持有长期工作 handle，不创建生产runtime。ReadDiagnostics读取已加载模型的实际能力；不支持项保留，必要项调用失败是AdapterFailure。ClearTrainingData只用于Standard/Robust，证据复制后执行；Direct传true为InvalidParameter，不对不适用算子试探调用。Load CandidatePreview可以无SealedContent/无Golden，但禁止请求生产激活；Evaluate/Recommend工程能力只接受CandidatePreview（IndependentTest也在隔离候选上执行），ProductionRead仅Compare/ReadDiagnostics/Unload。

ProductionRead必须有外部封存引用且SealedContent.Sha256=PackageHash、非空Golden；Host实际物化全部依赖并核Package身份后传入。Core独立核canonical/字节/版本→Backend.ReadFreshAsync（禁缓存）→固定Golden逐图比较→规范区域/槽/支持精确匹配→形成ReadBackReport和新token。非空Golden必须含完整支持的空候选和非空候选fixture，LightDark要覆盖仅亮/仅暗两种槽保留；任何差异、读取失败、取消或预算失败都不发布token、不覆盖已加载实例。正式报告仅技术读回，Host外部授权/资格/发布不由引用存在推得。模拟Backend的IsSimulator=true时ProductionRead为UnsupportedInput；纯Core测试用可控假Backend也必须标模拟，只验证分支拒绝，真实生产加载另外测试。

生产每请求使用明确Runtime token且不接受新阈值字段；Compare核输入/处理链/域/gate再调用已准备模型，不调用Train/Prepare。Loaded拥有模型，Compare只借租约；操作ResourcesReleased归还本次引用，不销毁长期模型。Direct/Slim模型需要改阈值时从完整重建闭包Build新候选；不靠read后尝试prepare。实例闭包最多MaxLoadedModels个，所有缓存/generation也计入模型数/字节；正式读回报告不能由缓存命中替代。

槽验证固定：Absolute=[Absolute]、Light=[Light]、Dark=[Dark]、LightDark=[Light,Dark]，每项必需且空Region保留；Backend返回R外游程/错误W/H/缺槽为AdapterFailure，不修剪非法结果掩盖错误。合法原槽再交D，E=D且N=E−union(Slots)、U=空；R支持不完整或gate拒绝/未知时不调用Backend，槽仍按方向保留但全空，E=N=空/U=D，Quality按IncompleteSupport或InputNotQualified并含原因。训练对此直接失败。Compare对valid支持仅一方向评价不能宣称另一方向无变化。

Evaluate顺序逐图处理；结构/分组错在接纳前整体Rejected，帧Acquire失联且确认无在途租约时/该图gate未知记该成员Unknown后可继续独立成员；Acquire未退为DrainUnknown并停止，不能先跳下一图。model.Compare适配错误/模型状态未知则停止余下成员，按未执行Unknown保留计划，整个Evaluate为Failed。正常遍历结束即使部分图Unknown也可Completed+报告，MetricsEvaluated=false；取消/超时保留已算item/未执行成员，终态Cancelled/TimedOut。Recommend任一计划候选未完整评价、缺良品/正例两类或RequireRealEvidence=true但无真实两类/Backend为模拟时State=Incomplete，SelectedOrdinal=null；只有false才允许完整合成计数给工程Selected，RealEvidenceComplete=false。全部完整且来源满足Policy但均过接受上限才NoFeasibleCandidate。候选间串行且资源真实归还才派发下一项，建议不批准任何生产事实。

### A.5 最小 Host 与模拟器落点

Core及其BCL Exe测试/两个最小Host共用一个唯一测试工程（§13）；TestHost从Program命令行 `--scenario contract|lifecycle|recommendation|consumers|benchmark|all` 选组，每组均为真实断言，不建立额外产品工程。帧源用固定CPU只读字节和可控租约，Backend用显式 `ScriptedVariationBackend` 实现本端口，可控制每步闩锁、失败、返回槽和Dispose。模拟器绝不宣称实现HALCON统计；主要断言 Core 调用顺序/预算/映射/恢复；对预登记的compare返回游程计算支持/指标用纯集合Oracle。模拟模型字节只读固定fixture，Format隔离，不写磁盘模型，也不驱动设备。

最小无UI正常与异常链唯一执行§4.4的try/finally，不另用无finally的简写序列。创建前绑定持久LifetimeOwner；所有Build/Load/Compare/Evaluate/Recommend/Unload立即Track，有限Await、终态释放、已知token卸载；验证拒绝、独立评价未接受、封存Unknown、消费抛异常或取消都进入finally。Stop不能被Unload/Release异常跳过。DrainUnknown保留同一实例、原handle及端口保持权；转交未明确接受则原Owner继续负责。Query/ReadEvents可在等待期间拉取；测试没有订阅也必须完成。Host不通过反射取得后台句柄，不引用原产品VM/数据库。模块自身Adapter工厂和端口按A.6实现，只有共享solution/产品接线由主任务串行接收；本次不创建工程。

### A.6 AsunImage Adapter 公开工厂与暂存端口

以下类型只位于Adapter DLL、namespace `Asun.Modules.VariationInspection.AsunImageAdapter`，引用Core公开契约；不加到纯BCL Core，不暴露SDK对象。工厂签名体省略，仅是实施契约，未实现/未编译：

```text
public static class AsunImageVariationBackend
    public static IVariationBackend Create(AsunImageBackendOptions options,
        IVariationScratchStore scratch);
public static class AsunImageVariationModule
    public static IVariationInspectionModule Create(VariationModuleOptions moduleOptions,
        AsunImageBackendOptions backendOptions, IFrameSource frames,
        IVariationScratchStore scratch, TimeProvider timeProvider);
```

```csharp
// namespace Asun.Modules.VariationInspection.AsunImageAdapter;
// using System; using System.Collections.Immutable; using System.Threading;
// using System.Threading.Tasks; using Asun.Modules.VariationInspection;
public sealed record AsunImageBackendOptions(long MaxScratchBytes, int MaxScratchFiles,
    int MaxSerializedModelBytes, int MaxMetadataBytes, ContentReference NumericEncodingEvidence,
    ImmutableArray<AsunImageReservationRule> Reservations);
public sealed record AsunImageReservationRule(VariationMethod Method, VariationPixelType PixelType,
    int MaxWidth, int MaxHeight, int MaxTrainingFrames, int MaxHeldFrames,
    bool IncludesFreshReadback, long ResidentModelBytes, long PeakTemporaryBytes,
    ContentReference Evidence);
public interface IVariationScratchStore {
    ValueTask<IVariationScratchFile> CreateAsync(long reservedBytes, CancellationToken ct);
}
public interface IVariationScratchFile : IAsyncDisposable {
    string AbsolutePath { get; }
    long ReservedBytes { get; }
}
```

Options不可变复制，所有scratch/serialized上限正数且有限，MaxSerializedModelBytes≤int.MaxValue且≤MaxScratchBytes；MaxMetadataBytes>0，组合工厂要求其≤moduleOptions.MaxMetadataBytes；Reservations非default/非空、有界（canonical元数据≤options.MaxMetadataBytes），各类型/模式有效，尺寸及HeldFrames>0、TrainingFrames≥0且≤65,535，模型/暂态预留>0、加乘checked，证据为有效ContentReference。Standard/Robust规则至少能覆盖2训练帧，Direct允许0；fresh规则显式IncludesFreshReadback=true。Estimate筛选模式/类型相同、全部请求数量/尺寸≤规则上限、需要fresh则规则标true的项；逐字段取所有匹配项的最大ResidentModelBytes/PeakTemporaryBytes，ReservationProfile绑定参与规则及证据的canonical hash；无匹配拒绝，不插值外推/静默降输入。规则是本适配器接入的明确预留输入，不是HALCON已测峰值；真实NativeAccountingVerified只来自实际计账证据。Core继续加实际帧stride/输出/包/诊断/fresh双实例预留并核请求与实例预算，不能重复把同一物理驻留计两次。

ResidentModelBytes始终是一份模型的驻留上界；PeakTemporaryBytes只计Backend额外native暂态，排除Core已计输入lease/托管输出/模型副本。IncludesFreshReadback表示该规则覆盖此工作路线的暂态，不把两份模型藏进Resident字段；Core按路线显式乘实例数。ReservationProfile.Id固定`variation-asunimage/reservation`、Revision=`0.2`，Sha256按VI-CANONICAL-1对根`Rules`数组散列，匹配规则保留Options声明顺序、字段按上述record顺序（含Evidence）；不引入第二资产注册。Backend.GetResourceUsage及Core.Query只读已记账快照，不做native/文件IO。

Scratch申请额度：Serialize为min(请求maxBytes,MaxSerializedModelBytes)，ReadFresh为真实payload.Bytes.Length且≤MaxSerializedModelBytes；每次在Store调用前以原子额度同时占文件槽和ReservedBytes，和已在途申请累计≤MaxScratchFiles/MaxScratchBytes，失败不调用native。Store返回一个新建、空白、普通本地文件的独占lease，AbsolutePath为精确绝对路径、显式.vam扩展，不含latest或指向原件；ReservedBytes等于请求值且保持到Dispose确认。Adapter核路径/额度，所有文件流的长度受同一上限控制；HALCON写出文件后核真实长度再读有界bytes，超额为ResourceBudgetExceeded，仍先真实清理。该上限是准入/回读限制；预留不承诺对同步HALCON写盘实施逐字节抢占或硬文件配额。真实超额/磁盘错误均失败并清理，不把申请额度当实际峰值；原生写盘峰值及预留充分性纳入VI-N04/Profile验证，不靠磁盘满试限。

Store负责该单文件路径的创建、独占与容量预留；Adapter负责使用、所有流关闭及调用lease.DisposeAsync。Dispose成功表示流/底层IO已退、该文件已删除或已回收且不再占本lease；不得删除父目录或他人文件。申请取消后迟到lease仍归原Adapter操作，真实Dispose后才减scratch计数；申请/释放未知均保持operation DrainUnknown及预留，不先终态。BackendResourceUsage的ReservedScratchBytes/ScratchFiles含在途申请、已取得及释放未知lease（非native内存）；DrainReceipt.HeldBytes仍是内存，不用其0推断无磁盘资源，Pending保留该原operation。实际暂存IO在Adapter实现，外部封存/权限/保持事务在Host；缺少产品存储接线不阻此文件端口/工厂及可控故障测试。

ReadFresh创建的native句柄在成功交Core前始终由Adapter持有；scratch释放未确认不得先返该模型。若后续校验/释放失败，保留并清理新句柄及scratch，均确认归还后才返失败；返回成功则只转移该新模型，暂存已归还。Serialize同样须暂存归还确认后才返回payload；迟到scratch申请、IO或清理Task不能被丢弃。释放失败但已确认归还可分类失败；未确认则原ValueTask保持在途并由同一有界worker观察，不能先throw终态后让无人持有的后台清理继续。Store.CreateAsync仅在确认没有lease/在途创建时才可取消/失败返回；否则保持原申请，由Adapter保留预留及观察。

组合工厂按§7.1一次完成参数校验→创建未开工backend→Core.Create所有权交接→返回module；失败反向回滚，不留在途Acquire/文件/native。独立backend工厂返回的实例在Core.Create成功前归调用者；若后者构造失败，调用者在finally Dispose此backend。成功后Host只关闭module，不能另关backend。首次native失败按原operation返回/隔离，不把工厂成功当能力Golden通过。N1/N2测试工程内提供独立受控ScratchStore，真实文件及闩锁/失败端口两者分别验证；不由产品Shell或共享文件补定义。

##### A.6.1 现有Scratch端口的独立本地构造

A.6的接口/Options/工厂不变；Adapter DLL补唯一可直接构造实现，避免让空Host自己猜temp/存储SDK。公开声明：

```text
namespace Asun.Modules.VariationInspection.AsunImageAdapter
record VariationScratchOptions(string RootDirectory, string OwnerId,
    long MaxReservedBytes, int MaxFiles)
class LocalVariationScratchStore : IVariationScratchStore, IAsyncDisposable
    LocalVariationScratchStore(VariationScratchOptions options, TimeProvider timeProvider)
```

构造只校验/复制：RootDirectory为Host明确给定并受其授权的绝对本地目录，OwnerId非空/无路径分隔符，数量/额度正且至少覆盖BackendOptions对应额度；不创建/扫描目录、不调用native、不中途换根。首次CreateAsync才在该根下为本Owner创建独占空.vam，文件名由新Guid生成，CreateNew拒绝碰撞，根/文件不得为链接或reparse点，不沿相对路径/UNC/latest/原模型；实际创建和同目录并发替换防护由这个Store实现并在VI-N07验证，不列成无消费者的外部SDK门。Store有原子文件槽/bytes账；Adapter账为同lease逻辑预留，不两账相加当磁盘实占。非本Owner生成或没有确认归还的文件不清理，不能递归删根。Directory/文件创建、校验失败若已有文件仍在原CreateTask内清理到确认，再返回失败；不可先throw再遗失部分文件。

Store在返回lease前登记路径/原Task/所有流及quota；迟到Create和单文件Dispose由同账保持。Lease.DisposeAsync第一次创建唯一清理Task并真实关闭其所有IO/删除该单文件，重复只观察该Task；文件不存在只有确认本Owner原文件已归还且无IO时成功，权限/IO/删除未知不置quota=0。Store.DisposeAsync先停新申请，在所有原Task/lease真实归还后终结，不自行取消正在借用的文件、不重Dispose底层。Host按A.8有限观察原DisposeTask，超期保留Store/根使用权和原Task。进程崩溃的孤留文件是另一次明确恢复任务的原Owner证据，不凭启动扫目录删除；真实介质故障/文件锁/写盘峰值仍为N2实际验证门。

##### A.6.2 CPU输入、原生诊断与Region的确定适配

本节补N1具体搬运步骤，不改A.1～5的API、阈值/方向/支持算法。全部算子经ImageLibDotNet.cv2；下列是26.05语义调用顺序，不猜C#封送重载、不接HOperatorSet、不检查封装内部。官方本地依据：[gen_image1](../../../halcon算子手册/operators/gen_image1.html)、[gen_image_const类型表](../../../halcon算子手册/operators/gen_image_const.html)、[get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html)、[count_obj](../../../halcon算子手册/operators/count_obj.html)、[select_obj](../../../halcon算子手册/operators/select_obj.html)、[get_region_runs](../../../halcon算子手册/operators/get_region_runs.html)、[clip_region](../../../halcon算子手册/operators/clip_region.html)、[area_center](../../../halcon算子手册/operators/area_center.html)、[smallest_rectangle1](../../../halcon算子手册/operators/smallest_rectangle1.html)。这些是本轮实际读取的目标手册页；版本、原页与现有Variation研究共同为实施依据，不新增来源报告。

| 步骤 | 实施顺序、边界与所有权 |
|---|---|
| CPU→native单图 | 先按A.2核真实lease/PixelHash/单通道、小端、stride及完整支持，checked预留H*W*元素字节的紧凑缓冲、native复制和两者并存。逐行只复制W*元素字节，不复制padding；Byte/Int16/UInt16分别传`byte`/`int2`/`uint2`，不按EffectiveBits改存储类型/截高位。pin自有紧凑数组→`gen_image1(Type,W,H,实际64位地址)`→原调用真返回后unpin。该算子创建自己的存储，禁止gen_image1_ex借用pointer、截断地址或传指针变量地址；原lease至少持到实际输入复制/调用退出，不从UI借native对象 |
| 有序训练与Direct | 各图转为上述同Owner独立image后，Standard仍按原Samples次序逐图train；Robust组装有序完整N并一次train，所选对象/原数组均保持到调用退。Direct ExternalMap同尺寸/类型非负；SobelSource按A.2实际W+2/H+2、−1/−1真halo搬运，中央逐byte等于Reference后sobel_amp(sum_abs,3)→crop_part(1,1,W,H)，实际v类型/范围合法才prepare。临时concat/裁图/派生图、输入image与模型资源分别登记，失败/取消等native真退后释放，不变更已冻结训练或预处理 |
| native→DiagnosticImage | 单诊断图先核count_obj=1/单通道与预期W/H；`get_image_pointer1`取得真实Type/Width/Height及借用pointer，按byte/int2/uint2/real分别映Byte/Int16/UInt16/Real32及1/2/2/4字节。HALCON real是4字节，不能凭C# double改为Real64；不支持类型拒绝AdapterFailure，Direct/清训练后缺图沿既有Unsupported。checked核maxBytes与总诊断预算后，图对象及模型借用保持到逐行托管复制真退，再释放返回image；不得写该pointer（reduce_domain等可共享matrix）。输出StrideBytes=W*元素字节、真实小端位模式/ContentHash，非有限值保原位模式及诊断，不修0/量化。原生完整图复制，不从缩减domain推测紧凑布局 |
| native→方向槽 | `count_obj`核预期：LightDark恰2（index1亮/index2暗），Light/Dark/Absolute恰1并映原请求槽；对象数不是连通分量数，缺槽是AdapterFailure而非空。逐slot `select_obj`（1-based）保持原数组和选择对象；area_center面积0返回空Runs但保留slot。非空先smallest_rectangle1核全部整数边界在R，越界拒绝，不能先裁掉越界冒充合法 |
| 有界游程提取 | 逐slot在上述非空包围范围逐row，用clip_region(region,row,0,row,W−1)→get_region_runs(单region)；单行最多ceil(W/2)段，调用前checked预留三个tuple暂态/原生对象及行输出预算，超软件硬预算拒绝ResourceBudgetExceeded，不抽样。每次核三个tuple等长、row同当前row、整数且0≤first≤last<W；空行是三个空tuple。追加前核累计maxRuns与输出bytes，按原顺序形成PixelRun(row,first,last)并核规范，相邻段按A.2合并，累加checked面积；只保存有界最终Runs，不建bool mask、不连接/过滤或改变方向槽。每行临时Region/tuple真退后释放再处理下一行；取消在行边界停止，但原compare/native/输出资源仍沿A.3真实排空。此分行只是同Region的无损提取，不能改E/N/U或缺陷语义；端到端复制与行提取耗时计§11，未声称性能通过 |

每个本方数组、pin、image、对象数组、region/tuple、模型与scratch均有同操作Owner；正常、异常、输出预算失败与迟到返回沿同一排空链，最后释放不覆盖原业务错误。不能用托管长度预估声称native实际字节已知；未知native账沿§11标null/NativeAccountingVerified=false，真实峰值/失败释放必须VI-N03/06验证。真实签名歧义在消费编译处理；统计ddof/MAD倍率/整数量化仍由原VI-N01读回/Golden核定，不在本节猜测。

### A.7 N/U借用端口与既有模块的确定映射

新增薄桥只在Adapter DLL，引用[ImageFrame Resources/Core](../image-frame/DEVELOPMENT-GUIDE.md)公开类型；Core/API/CPU像素语义不改。以下声明为本模块增量，已由主控限定内容接收：

```text
namespace Asun.Modules.VariationInspection.AsunImageAdapter
record VariationFrameBinding(FrameReference Reference,
    ImageFrame.Resources.FrameKey SourceKey, int PlaneIndex,
    ImageFrame.Resources.FrameDescriptor Descriptor)
record VariationFrameSourceOptions(string ConsumerId, int MaxConcurrentReads,
    int MaxLeases, long MaxCopiedBytes, TimeSpan ReadTimeout,
    TimeSpan ReleaseObservation, int MaxRecoveryTicks)
class VariationImageFrameSource : IFrameSource, IAsyncDisposable
    static VariationImageFrameSource Create(VariationFrameSourceOptions options,
        ImageFrame.Resources.IFrameService frames,
        ImmutableArray<VariationFrameBinding> bindings, TimeProvider timeProvider)
```

Host已持有真实FrameDescriptor/FrameKey及Content、PixelHash、参考格、处理链、完整支持/质量证据后才能造binding，Content三元组唯一、Descriptor.Key=SourceKey、PlaneIndex为存在的单通道plane；不把ImageFrame SourceRevision或Guid直接猜成SHA256/资格。binding深复制，ImageFrame的Scalar UInt8/Int16/UInt16逐名映Variation Byte/Int16/UInt16，unit=1、Scale=1、Bias=0，尺寸/位深/单通道/参考格/有效域须精确匹配，浮点/多通道/物理缩放拒绝而不转换。Content/PixelHash由Host来源保持证据明确提供；Core仍核真实有效行PixelHash。FrameService构造只用公开FrameServiceFactory().Create(ResourceLimits,new Asun.Modules.ImageFrame.Core.ManagedLayoutValidator(),TimeProvider,events)，实际输入由Host先PublishCopyAsync或取得已有FrameKey；本桥不采图/加载任意文件/重复发布父源。

| 本端口步骤 | 上游准确入口/DTO与结果规则 |
|---|---|
| Create/Acquire预检 | 所有上限正，时间正且有限，ConsumerId在上游ResourceLimits.Consumers已登记；MaxCopiedBytes计桥紧凑副本+每个保留lease的同时容量，不把父池字节抹零。Create无IO/lease/worker；Acquire先预约读槽/副本/迟到归还槽，按完整Content精确查binding，未见拒绝不fallback到最近图 |
| 原源读取 | new FrameReadRequest(新Guid,ConsumerId,SourceKey,[PlaneIndex],PixelWindow(0,0,W,H),0,RejectMissingSupport,ExactSamples,ReadTimeout)→IFrameService.ReadAsync(req,ct)，原ValueTask一次AsTask保存；只有Completed、Error=None、对应epoch/request/lease、完整R及Slice非null才成功。不用Display/LOD/插值/LUT补算法输入 |
| CPU无损投影 | 原Slice.TryOpenReadScope(out scope)，逐y在scope.CopyRow(局部plane索引0,y,精确RowBytes的Span)真实复制；checked预约new byte[H*RowBytes]（≤Array.MaxLength/本桥预算/上游容器），StrideBytes=RowBytes，小端UInt8/Int16/UInt16不量化。scope退出才可关闭上游lease；桥IFrameLease.StorageBytes为自有副本实际容量，Pixels不可变借用，Reference为原冻结Reference |
| 父/子保持 | 在桥lease交付前关闭scope、单次Slice.ReleaseAsync(ReleaseObservation)并保存原Task。ReleaseReceipt同lease、LeaseClosed=true、Error=None、Drain=Drained才确认本借用归还；StorageReleased=false合法（Host父帧还在）。若原Task结束仅Draining，受限恢复在同lease下调用其公开幂等ReleaseAsync获取观察，不捏造QueryRelease；未结束不重发 |
| 失败/取消/迟到 | 复制中取消先退出CopyRow/scope；异常也接住迟到Slice，释放确认前Acquire原Task保持pending、Core DrainUnknown，不先交lease/throw完成。Read未知按原ServiceEpoch/RequestId用QueryOperation查，不用新Guid重读；查询NotFound不证明未读。重放Read回执没有新Slice，不能把ResultLeaseId当可重建对象 |
| 本桥退出 | 返回Core的桥lease.DisposeAsync在Backend真退出后撤自有副本/强引用才确认；原父服务借用已在交付前归还。Bridge.Dispose停新Acquire，全部原读/释放/副本lease退后完成；不Close/Dispose借用FrameService、不Retire父FrameKey |

ImageFrame.Layout.BitsPerSample是存储位宽（UInt8=8，Int16/UInt16=16），与FrameReference.EffectiveBits分别校验：例如合法12-bit UInt16帧仍Layout=16，不因16≠12拒绝，也不截高位；有效位深由Host可信来源/方法证据给，不从容器位宽推得。Reference.Width/Height是本次真实读取尺寸，正常格原点0/0；只有A.2已允许的SobelSource保留W+2/H+2、−1/−1和完整真halo，ReadWindow仍其父源局部(0,0,实际Width,实际Height)，不能裁成W/H或将原点归0。桥不猜Sobel用途、不豁免Core的中央相等/处理链/完整支持校验。

ValidSupport映射为Layout.Domain与选定PlaneMetadata.ValidDomain的精确交集：Full/Empty不补行，RowSegments `[StartXInclusive,EndXExclusive)`映PixelRun(row,start,end−1)，按真实局部尺寸与原A.2规范冻结；intersection用有界有序游程处理，不建全图bool mask/只保包围框。与Reference.ValidSupport不一致拒绝；FootprintSupport和IndependentAlignment/Illumination/ImageQuality仍由Host独立证据给，FrameService存储合法不证明上游Gate合格。域段预算与原值hash核验在复制前/lease内完成，不以显示有效域覆盖算法支持。

N1/N2无UI完整R的内存复制开销计§11资源/性能门；大图既有固定块Host先由上游明确发布块FrameKey/参考格及真实halo，再用同桥，不在桥内变换/切块或重定义支持。图像文件解码/相机/注册归真实来源Owner，空Host用已发布CPU源，不猜SDK。

#### A.7.1 ModelAssets Service与包身份/保持权

仅Host引用[ModelAssets Service§5A、附录B.3/B.5](../model-assets/DEVELOPMENT-GUIDE.md)，本模块Core/Adapter/Wpf不新建Store/私表。Host准确用ModelAssetsHostRoot(profile,clock).Reserve(hostId,scope)→原slot.SetCleanupPlan→ModelAssetsHost.Create(options,ports,slot)，或借同Scope已创建IModelAssetService；scope/principal/profile/formats/usage authority都是Host明确输入。Storage桥若使用，沿其既有ModelAssetsStorageBridge.Create(binding,ports,slot)，不在Variation再建Runtime/私有存储合同。Factory前的Root先强持输入包/源流/端口，原Service Task由StartCall保持；Create/封存Unknown不改另一ID重发。

内容映射固定使用已有VI-CANONICAL-1：metadata文件角色variation.metadata、逻辑路径variation.json，字节恰为A.2的Package散列根Manifest/Format/Sha256（无Bytes/PackageHash/BOM/换行）；其原文件SHA256就是PackageHash。native文件角色variation.native、逻辑路径model.vam，字节恰Payload.Bytes，文件SHA256=Payload.Sha256。这只是现有包的物化，不能把整ModelPackage反射序列化或加入服务Digest重算VI身份。AssetManifest.Files为两个必需AssetFileEntry，LengthBytes/原文件摘要逐项从真实字节取得；Format.Entrypoint=model.vam、Layout明确两原路径，Format/Producer版本绑定A.6实际capabilities及Host原格式登记。依赖TrainingSources/DirectSource/Domain/Processing/Applicability/Qualification/Golden按照上游Runtime/RebuildSource/ValidationEvidence及Host完整精确AssetRef映射传入；没有ContentReference→AssetRef的可信查表拒绝对应用途，不猜namespace或用hash代替资产身份。薄桥无新的公开codec/模型类型；Host写metadata必须复用本页固定逐字段规则并验证hash，不更改Core API。

ImportAndSealAsync(Context,Manifest,SourceSnapshot,ExpectedAbsent=true的原AssetImportRequest,两个ContentInput)前先用ModelAssetRequestProjection.ProjectImport冻结RequestDigest，source只借原只读流；ConfirmedCommitted的SealReceipt绑定实际文件/引用才封存。恢复QueryOperationAsync(originalOperationId/digest)，ServiceOutcome与资源Disposition分别记录；Seal已成功而后续Load失败，保留已seal及旧Loaded，不删历史资产。asset Ref.Digest为上游自己的model-core-jcs-v1等规则，**不是VI PackageHash**；SealedContent.ContentReference采用可信Host编码的exact AssetIdentity Id/Revision，Sha256明确为variation.json真实SHA256=PackageHash。同时保留完整AssetRef/SealReceipt在Host账；不能把asset Digest塞SealedContent.Sha256，也不能凭此字段声称用途批准。

正式读取顺序：ResolveExactAsync(ExactRef,Runtime,Access)完整闭包→AcquireContentLeaseAsync→OpenFileAsync(OwnerRef=精确root,Role/LogicalPath分别为上述两项)→受限读原ContentReadLease.ReadOnlyStream核真实长度/EOF/原文件digest→metadata严格字段/enum/null/顺序规则解码与native字节绑定，重算Package/Method/TrainingHash→实际物化并核全部Runtime/Golden依赖→本模块原Load(ProductionRead,SealedContent,完整Golden,Budget)。解析器限metadata/model上限、拒重复/未知字段/类型/非规范编码，不补默认值；native依赖保持仍在Host。Load fresh/Golden正常或失败都沿A.4，不用上游VerifyFormatAsync成功替代本模块Load报告；若Host另调用VerifyFormatAsync，Adapter/RuntimeSnapshot/Challenge按上游生产者来源给，报告只证明其指定读回，不升级质量。

ContentReadLease及IAssetContentLease用原ResourceReleaseRequest(ResourceId,固定ReleaseOperationId,Budget)/ReleaseAsync，未确认沿Service.QueryResourceAsync查原ResourceId；流IO原Task真实退出后才release child，child退出再父lease，Load/native借用不退时不关parent hold。ModelPackage为有界独立托管复制，所有真实依赖已复制且元数据/Golden依赖不再借stream后可归还相应hold；否则持到对应Load/比较退出，何时归还按真实借用而不是UI按钮。缺真实asset/物理介质/用途authority只阻该生产接线，N的本地Scratch和CandidatePreview独立训练/Inspect不依赖生产Store。

### A.8 两个独立空Host与有限Owner恢复

以下仅是N/U未来既有测试工程内的Host实施伪码与断言，当前不创建工程/代码/测试。复用§4.4/A.5的Core调用顺序和原finally，**不改已接收Core Host**。N为无Dispatcher控制台；U为自己的STA Window/Dispatcher。两者不引用产品Shell/私表，彼此不共享可变模型、sequence或取消域。外部注入已有真实公共服务可借用，合成机制夹具必须标来源/模拟，不能称真实HALCON/WPF运行已通过。

#### A.8.1 Host根槽和两轴的精确定义

Host入口创建显式、非static的有界LifetimeRoot；其私有实现只在N/U测试/真实宿主，不能作为另一公共模块合同。RootProfile必填HostId、MaxSlots、MaxCallsPerSlot、MaxRetainedBytes、MaxCleanupErrors、MaxRecoveryTicks及ObservationWait/CleanupExecution有限正期限；Unknown也占槽，cleanup有预留槽。Root在应用入口强持，Window/业务方法结束不结束它。下列辅助是Host局部语义，不要求开发者猜生命周期动作：

| 辅助 | 必须实现的精确行为 |
|---|---|
| Reserve/Attach | factory调用前预约槽/输入/端口/最坏留存byte与原任务槽；创建返回立即在同槽存module/session/backend/帧/scratch/asset/viewport对象及owns标志，不在返回与Attach之间执行业务。无容量不启动factory；构造抛错仍访问原槽，借用上游不Dispose |
| StartOriginal(id,start) | 先在锁内预约记录并强持输入闭包→锁外有界worker进入start→ValueTask一次AsTask（Task直接保存）→存真实原Task；同时保留受管dispatch Task。外层AwaitFinite使用WaitAsync只能作为观察包装。同步start卡住时原dispatch/闭包仍有Owner，不额外无限线程；迟到模型/lease/result先Attach再走同cleanup，不能以已关闭丢Value |
| TrackOperation(handle) | 入口返回即保存InstanceId/Key/原Completion/输入/token，重复Rejected不替换原Key；Query/ReadEvents有界。借用被module内部持有时Root保module/frames/scratch及上游权利，不反射backend |
| Observe | 每次只有限看同原Task/同Key/同release ID与已授权资源查询；时间到记本次WaitEnded并请求合作取消，不改原OperationResult/asset提交事实。BusinessOutcome含原返回/主异常/已确认封存，CleanupState独立为Pending/Unknown/Released，不能一bool覆盖两轴 |
| Close/Recover | 首Close封新请求并创建唯一cleanup工作；执行token与业务ct/WindowClosed/waitToken分离，单调执行截止点固定。最多MaxRecoveryTicks，每次有限原Task观察/Query，结束仍Unknown保根槽/资源/原Task；不重新Build/Load/StoreCommit/Dispose。原cleanup执行期限结束后仅观察已发Task/资源事实；仍未发的必要安全后续清理由同Owner显式登记下一有限cleanup意图，保留原身份/错误，不能无限自动续预算 |
| TryReturn | 全部原Task观察、晚到Value接管、实际借用/流/帧/scratch/presenter归还和唯一Dispose完成才解除；primary error保第一业务失败，cleanup errors有界另列。转交要活Owner明确确认同上下文/容量，确认前原Owner留账；Task.IsCompleted/fault/日志/窗口关闭均不是资源归还 |

#### A.8.2 N：无UI独立训练、检查与读回Host

```text
root = new LifetimeRoot(explicit N profile, TimeProvider.System)
slot = root.Reserve("N", input/profile/ports; owned vs borrowed)
try:
    // 在slot内创建，原factory/ValueTask都用StartOriginal；同步factory也先Reserve
    frames = slot.Attach(VariationImageFrameSource.Create(frameOptions, frameService, bindings, clock))
    scratch = slot.Attach(new LocalVariationScratchStore(scratchOptions, clock))
    module = slot.Attach(AsunImageVariationModule.Create(coreOptions, backendOptions, frames, scratch, clock))
    // 不另保存/Dispose backend；工厂已在成功时交Core所有权
    capabilities = module.GetCapabilities(); require actual runtime/revision and non-simulator for N
    // request/header/budget用冻结Profile，Track/Await采用§4.4完整finally
    validate frozen Training; BuildCandidate -> CandidatePreview Load -> Inspect Compare
    // 可独立Recommend与Evaluate，非Completed/Incomplete不得进入后续接受
    if explicit asset roundtrip requested:
        slot.StartOriginal(original seal request, assets.ImportAndSealAsync)
        if seal Unknown: finite Query original; stop business progression if still Unknown
        Resolve/Acquire/Open/copy+verify/dependency holds per A.7.1
        production = Track(module.Load(ProductionRead, exact seal/Golden))
        if production completed: Inspect unchanged; do not replace original runtime implicitly
catch primary:
    slot.RecordBusiness(primary)
finally:
    // 每步自己的try/catch/finally；一个cleanup错误不跳过独立可退资源
    request cancel original pending -> release terminal records -> known token Unload
    module StopAndDrainAsync(original instance, independent finite deadline)
    if truly Drained: slot.StartOriginal("module-dispose", module.DisposeAsync) once
    if module dispose actually confirmed:
        dispose owned frame bridge/scratch store once via original tasks
        release completed stream/read/asset leases with original resource IDs
    if all borrowers exited: retire only Host-owned source frames / close owned upstream services
    slot.KeepPendingOrTryReturn(); root finite Recover same tasks/identity
```

FrameService/父帧/Assets是借用时永不Close/Retire；自建FrameService仅在全部桥/presenter借用归还后Retire自己的FrameKey，再Close/Dispose。asset child/hold可以在已独立退出时先释放，不因不相关模型失败无限保留；被native/原IO借用的父项必须等其退。module.Dispose、bridge/store.Dispose各只创建一次原Task，异常/超时原Owner继续持有，不再次调用析构来“试一下”。cleanup与业务两轴：Build成功+关闭Unknown仍保Build事实；Seal成功+fresh/Golden失败保Seal和旧runtime；取消+late Create/ReadFresh/Scratch/Frame lease只能接管原结果并清理，不能重读/重新工厂规避留账。N1/N2正常/每阶段故障、关闭中迟到资源用VI-N06/07及A.8.4验证，真实介质/公式/类型/资源/Golden另门。

#### A.8.3 U：独立STA工程Window Host

```text
// 独立[STAThread]入口，固定1920x1080验证viewport，不改OS显示
root = new LifetimeRoot(explicit U profile, clock); slot = root.Reserve("U", all anchors/owned flags)
Application + Dispatcher + Window are this STA's own objects; do not borrow product Shell
try:
    N-style public module/frame/scratch assembly; each anchored before work
    viewportRoot = slot.Attach(new ViewportRootFactory().Create(rootOptions))
    view = new ViewportControl() // STA, no Bind yet
    renderer = ViewportRendererFactory.Create(view, viewportRoot, rendererOptions)
    check renderer Succeeded + Value; immediately anchor original ports/control/root
    images = slot.Attach(VariationWorkspaceImages.Create(imageOptions, frameService, workspaceBindings,
        viewportRoot, sourceOptions, explicit displayWindow, clock))
    viewport = slot.Attach(viewportRoot.CreateFactory().Create(options with
        Backend=renderer.Value.Backend, Presentation=view.Presentation,
        Frames=images.Frames, Coordinates=images.Coordinates, Probe=images.Probe))
    presenterOptions includes renderer.Value.Lifetime, explicit ExecutionBudget and complete Catalog resources
    presenter = slot.Attach(VariationViewportPresenter.Create(presenterOptions, view, viewport, viewportRoot, images))
    headers = WorkspaceOperationHeaders.CreateForNewInstance(module, clock, explicit requestDuration)
    ui = slot.Attach(VariationWorkspaceSession.Create(uiOptions, module, presenter, headers, access, clock))
    // 成功后presenter ownership已交ui；slot只保其borrow，不再直接Dispose
    locale catalog/scope/snapshot -> ui.Control.ApplyPresentation(complete Variation resources)
    viewport Catalog.Get(same locale) -> complete schema snapshot + actual overlay label keys
    ui.Control.Configure(frozen WorkspaceInput); attach CandidateReady handler, then Window.Content=ui.Control
    // 当前公开任务逐项验证Train/Suggest/Validation/Inspect/reference compare，
    // 不把空UIA/只有Grid绑定当成功；每条沿冻结输入及原operation
    await own Dispatcher pump; command awaits never synchronous Wait/Result
finally:
    // Closing第一次拦截普通关窗，先停新UI动作，移除本Host CandidateReady/语言权限订阅
    ui CloseAsync(independent finite deadline, waitToken) -> save original Task
    // unknown时清空可撤视觉/禁交互但保ui/presenter/images/Dispatcher及viewport原任务
    // Window Closed也不Shutdown Dispatcher；有限Recovery由入口root继续驱动
    if ui resources truly released:
        viewport.DisposeAsync(finite budget,None) via original task, outside its work slot
        viewportRoot.CloseAsync(finite budget,None) -> verify original presenter/render/return
    // module停止与UI/viewport清理是独立轴，UI失败不得跳过模块Stop
    N-style own module Cancel/Unload/StopAndDrain via independent original tasks
    if module truly Drained: module.DisposeAsync once
    if viewport borrower tasks truly quiesced: images.DisposeAsync once
    if all module and display borrowers exited:
        frame bridge/scratch Dispose once, then close only owned source/asset services
    release owned locale scope / authorization subscriptions and original callback tasks
    if root all released: Window.Close and Dispatcher/application shutdown
    else: keep original root/STA pump for finite observation, report pending; no forced PASS
```

任何factory失败按slot内实际已Attach对象清理；未创建项不调用其方法。Session.Create失败时presenter仍归Host，原Owner执行一次presenter.Dispose；成功才交给session，Host不再重复Dispose。Window/STA创建失败也不跳过已经创建的无UI模块清理，cleanup按资源依赖而不是最后执行到的行号。

Closing事件不能async void遗失原任务：同步设置Cancel=true，根先Reserve关闭worker再派发；worker实际完成后在本Dispatcher执行一次最终Close。用户重复关闭只观察同cleanup，不再建Window/Presenter/module。只有本Window允许关闭而原STA资源仍未知时，由同入口根保持Dispatcher和原控制对象到实际退出；真正进程结束/测试外层终止不再声称有continuation或ResourcesReleased。UI Close异常也必须进入module独立关闭；但images/父帧的关闭必须依赖presenter/viewport真实退。可借用共享Core的嵌入情形只关闭本ui/presenter，不Stop/Dispose Core，不取消其它Host操作；独立U拥有Core才走N关闭，owns标志不可由控件猜。

合成离线装配可复用上游STA Profile：OfflineRasterOnly、MaxNativeBaselineBytes=0、MaxRasterBytes=64MiB、MaxPendingSubmissions=2、CleanupBudget=2s，UI ExecutionBudget=(64MiB,32,32)，这些是软件有界夹具上限，不是生产目标/实测性能；checked核实际1920×1080验证client与原root/session/父服务限额，不足则先拒绝。生产使用批准Profile的Required/HalconRequired与预算，不复制合成值。Control必须先于session，session.Presentation准确同view.Presentation；本presenter固定OwnSession=false，不继承别的Host的true。真实首次Present：Register→Bind空→Attach，后续Register→Update→Return→Remove→Retire。两个业务消费者仍§12的PG006/PG022，不把上述同U流程的A/B实例当第三产品或生产资格。

#### A.8.4 两轮自审断言与精确剩余门

第一轮按外部接入逐段核：全部必需Options/准确构造、Source/资产/语言/权限公开入口、独立Train/Suggest/Validate/Inspect/reference compare与正常N/U调用链。第二轮按Owner反例核：factory前满槽、原start同步抛错/卡住、late Acquire/Scratch/Create/Bind、取消/Close、Dispose异常、asset提交Unknown、UI回调/Dispatcher关闭。下列追加到现有VI-N06/07、VI-U01～03，不新建同义测试目录/报告；它们是待实施可判定断言，不是本轮运行结果。

- 无容量/非法Options在factory/Read/Bind之前拒绝；构造零native/帧/scratch IO。创建返回到Attach无不受保护窗口；Core/Adapter已接收字节/公共API不变。
- 原task只一次AsTask；wait包装结束不解除Borrow。late文件/帧/token/binding有原Owner，帧副本完整且byte/int2/uint2保真，文件与租约只释放自己项，已发Dispose不重发。模块scratch/nativemodel计数与Hoststream/parent hold账分开。
- SealReceipt确认后fresh失败仍保资产/旧模型；Service原Unknown/digest不新ID重放，asset JCS Digest不代PackageHash；生产用途/readback和工程推荐不混淆。
- UI取消/关闭/权限撤销不Stop借用Core；原Dispatcher/Bind/Unbind/呈现资源仍由root/session保持。原样Inspect不会Train/Prepare，原模型比较不自动采用，三语/IME/dock/Chart选择不改算法快照。
- 无UIHost运行不得初始化WPF；STA Host必须是真WPF固定1920×1080 viewport，独立Window/输入/语言/取消域；Mock/合成资料不作native/资产耐久/真实呈现或客户性能证据。

2026-10-12增量自审将以下断言定位到既有VI-N03/06、VI-U01～03（仅文档断言，尚未运行）：

- 12-bit UInt16输入保16-bit容器/原值与独立EffectiveBits；Sobel W+2/H+2及−1/−1保持，中央错/halo缺失拒绝。存储Domain交集半开→闭游程无孔丢失；gen_image1真退才unpin，诊断real返回Real32而非猜Real64，指针不写、原image保到复制结束。
- LightDark两个空/非空槽顺序保留，零objects不冒两个空slots；逐行clip/get_region_runs全行无损、越界/输出超额拒绝，失败/取消原资源真实退，不改原阈值/E/N/U。
- Lifetime=null在Reserve/Dispatcher前拒绝，跨Control/root/lifetime拒绝；control.Presentation直接转发同binding原Task，同Commit不多Acquire，完整submission+SourceCall/授权+代号一致。GetPresentations仅观察，同Owner迟到lease一次Revoke/Return，Unbind超时继续保原任务；Host slot外关闭session。
- 公开source producer识别真实源payload；UInt8/UInt16直接Register，signed/real显示Gray8有显式冻结范围/派生修订，Probe和诊断表仍原值，非法范围/多plane未映射/容量不足先拒。换图Register→Update→Return→Remove→Retire，借用父源不退役；显示副本不回灌算法。
- 三语完整Catalog schema与实际标签齐全；Host经公开presenter.SetResourcesAsync转发同binding原Task，未Bind仅完整冻结、正在Bind/关闭先拒；旧七键/假revision/缺键/超限拒绝且保旧包，Locale切换不把Localization activity revision写进Viewport资源schema。1920×1080读回实际预算不足先拒，可见确认只依据原renderer，未确认不显示成功。

2026-10-11两轮有界文档自审已完成：首轮核构造/映射/独立任务流，第二轮核原Task/权限Read分支/双模型结果及factory失败与UI关闭依赖，修正只读授权不得要求写入Eligible、补ConfigureReference结果消费及共享Core不被UI停止。定向文档核对复用现有validate_docs.targets检查本页本地链接、围栏/状态，逐段比较§1–7、§8.1–3、§9–12及A.1–5和C1～C4接收行未改；911-byte向量SHA256复核一致。上述是规格/结构自审，不是实际实现、运行测试或产品资格。

2026-10-12原会话两轮限定文档自审完成：外部接入视角核全部批准能力和实际公开构造/端口，补CPU/native搬运、16-bit存储与12-bit有效位深、Sobel源尺寸/原点、viewport公开producer及同Control Presentation/Lifetime、Catalog schema和语言转发入口；Owner反例核晚到lease/原Task、一次Revoke/Return、Clear部分确认与禁止复活、工厂失败/独立UI与module关闭轴，修正直接Register须取真实FrameDescriptor的SourceId/SourceRevision、Clear准确PreviousPresentationsRevoked字段。viewport 0.3.5-prep只消费BC-U1/BC-U3实际采用部分，不采用BC-U2，不重做上游已完成内容。定向结构检查复用validate_docs.targets，核本页33个本地链接与26个围栏、N/U未就绪口径；逐段比较§1～7、§8.1～3、§9～12、A.1～5及C1～C4接收行与本轮修改前字节相同，911-byte固定向量也保持。此为正文/契约/结构自审，不是产品编译或运行测试。

2026-10-11主控对N/U装配确定指导的限定内容接收保留；2026-10-12本轮增量与全模块设计结论在本原会话完成自审，不再设主控内容审核门。N1/N2/U1实际HALCON/资源/WPF/Golden/运行及现场资格继续`PreparationIncomplete / NotReady`，不是整模块Ready。真实实现/编译/运行未执行；HALCON类型/整数量化/真实模型和资源Golden、文件锁/删除/介质/写盘峰值、真实资产/用途/完整依赖、viewport renderer/可见确认、WPF/UIA/IME/DPI/长稳各按对应VI-N/U门实际验证，剩余Owner唯一按§13.3。客户物理阈值、误接受/拒绝、时延/峰值目标须真实Profile，缺失仅阻对应资格；已能冻结的自有构造/装配/恢复不能再写成外部门。C1～C4接收状态及911-byte固定向量完全保留。

