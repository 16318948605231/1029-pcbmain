# 图像分割与区域特征独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`SG-C1, SG-C2, SG-C3, SG-C4`

- 模块 ID：`IM-029`
- 来源包：`PKG-025`
- 中文名称：图像分割与区域特征
- 英文键：`segmentation`
- 文档版本：`0.2.4-prep`
- 文档状态：`DesignReview / Prep`
- 内容接收（2026-10-10）：主控已接收本页已明确的相关 Core/适配文档规格，确认 §12 HostHeldCall 预登记、异常/取消 finally、未接纳 reservation 同 ticket 恢复、KnownResult 与资源闭合分开、两轮有限恢复及原 Owner 保留。此次为规格接收，不授予整模块 Ready，不启动实现；具体切片的完整准入仍见 §19。
- 历史主控接收（2026-10-11）：按§19.1六项逐片接收SG-C1/C2/C3/C4为`ModuleCoreImplementationReady`（仅文档准备）；SG-A1公开装配、SG-U1（W1）装配/Owner恢复增量限定内容接收。主控独立逐字段重建Parameter 131 bytes、Request 1181 bytes及SG-ID-02/03/04的1181/1181/1090 bytes，完整hex/hash一致，并核对四图八case及search/holdout不改冠军。真实代码/集成/运行资格门见§20.2，不启动实现或授予整模块Ready。
- 原会话全范围自审（2026-10-12）：0.2.3-prep已按当前全部批准范围完成两轮有限文档走查，含Adapter、WPF/viewport、语言、只读结果、恢复与有限参数建议；可决定的软件设计已闭合，覆盖与具体剩余Owner见§20.3。本轮新增内容由IM-029永久原会话自审，不等待总控内容审核，不声称新增内容已获历史主控接收；未授予整模块ImplementationSpecificationReady或运行资格。
- 消费窄同步（2026-10-12，0.2.4-prep）：仅补viewport 0.3.5-prep §20.5确认的内置renderer源生产者装配，见§13.1.2.1；选中bbox叠加与局部Clear保持。原全批准范围可决定软件设计闭合结论保持，有限反例/本轮文档自审见§20.4；不提升任何真实运行资格。
- 责任模块：`SM-011 Vision Features`
- 规划消费者：外观、阻焊、涂覆、胶体检测，以及其它视觉项目的通用区域候选工具
- 技术基线：C# / .NET 10；HALCON 26.05；通过 `ImageLibDotNet` 公共边界接入 AsunImage

> 本页是独立模块的唯一开发指导。模块 Core 的类型与行为以 §4、§8 和附录 A 的 `Module API Contract v0.2` 为唯一规格，SG-C1～C4已获主控逐片文档准备接收；产品持久化/State 映射仍为候选，不自动成为平台 DTO。模块不定义制程缺陷名称、目标关联、工艺阈值、质量放行或设备动作。所有新增验收条目均为拟执行要求，不是已经通过的结果。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/segmentation/Asun.Modules.Segmentation.Core/Asun.Modules.Segmentation.Core.csproj`；namespace：`Asun.Modules.Segmentation`。预定测试工程：`tests/Modules/segmentation/Asun.Modules.Segmentation.Core.Tests/Asun.Modules.Segmentation.Core.Tests.csproj`。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前状态：SG-C1/C2/C3/C4原`ModuleCoreImplementationReady`文档接收与§12 Host收尾保持；SG-A1/SG-U1历史限定内容接收保持。0.2.3-prep在原会话完成全批准范围可决定的软件设计闭合（§20.3），不是只完成Core。整模块仍为`PreparationIncomplete`，完整ImplementationSpecificationReady及运行/产品资格按§20.2–20.3保留；真实代码仓库/分支、实现指令与本方编译/运行/实测均未完成。本次仅修改本指导，不创建工程或自动派发实现。

后续切片落点固定如下；此处只定义位置，不创建工程，也不把这些路径作为本轮写入许可：

| 层 | namespace / 唯一工程 | 唯一测试/最小 Host |
|---|---|---|
| Core：契约、纯校验、派发、支撑/接缝/结果校验、三值筛选、生命周期 | `Asun.Modules.Segmentation`；上述 Core 工程 | 上述 Core.Tests；其 Fixtures 下的两种内存宿主，模拟后端只返回冻结测试域，不实现替代生产视觉算法 |
| AsunImage adapter：cv2/线程/native/RLE 投影 | `Asun.Modules.Segmentation.AsunImage`；`src/Modules/segmentation/Asun.Modules.Segmentation.AsunImage/Asun.Modules.Segmentation.AsunImage.csproj` | `tests/Modules/segmentation/Asun.Modules.Segmentation.AsunImage.Tests/Asun.Modules.Segmentation.AsunImage.Tests.csproj` |
| 可选嵌入式控件 | `Asun.Modules.Segmentation.Wpf`；`src/Modules/segmentation/Asun.Modules.Segmentation.Wpf/Asun.Modules.Segmentation.Wpf.csproj`，`net10.0-windows` | `tests/Modules/segmentation/Asun.Modules.Segmentation.Wpf.Tests/Asun.Modules.Segmentation.Wpf.Tests.csproj`；UIA 最小窗口只在该测试工程中 |

所有层只允许修改自身明确获准的上述工程/测试目录；不得因接入问题修改其它模块、平台 Shell/共享契约、参考项目、AsunImage 内部。Core/adapter 使用 `net10.0`；WPF 只依赖 Core 与宿主公开视口端口，不直接创建图像或算法 handle。本轮允许写入只有当前指导文件。

## 1. 目标与边界

### 1.1 模块负责

模块接收一个具有稳定像素格和质量支持的标量图、已登记颜色通道或冻结的外部分割 mask，在指定处理域内执行下列能力：

1. 固定闭区间、已资格化的全局自动阈值、动态参考比较和局部 Sauvola；按方法与输入适用域确定性派发。颜色转换/学习推理由宿主公开端口提供，模块只消费注册通道/mask。
2. 前景、背景、未知三态及每个未知像素的原因。
3. 有支撑约束的开、闭、腐蚀、膨胀等区域形态操作，并保留原始/派生来源。
4. 4 邻接或 8 邻接连通组件，含分块计算的跨 tile 等价合并。
5. 区域面积、质心、包围盒、离散边界、轮廓长度、HALCON 圆度和孔洞，以及类型化筛选、缺值和排除原因；未知触边时拒绝确定拓扑。
6. 输入、方法、参数、质量、资源、取消、算法版本和证据引用的可追溯回执。

### 1.2 模块禁止

- 不解释“漏涂、露铜、残胶、焊桥、污染”等制程语义。
- 不拥有 PCB/PCBA、工单、网表、目标 ID、元件关系、缺陷代码或最终 PASS/FAIL。
- 不选择或修改相机、光源、运动、PLC、设备安全互锁，不拍照、不重拍、不提交生产事实。
- 不创建或写入产品数据库、质量事实、报表事实或设备命令。
- 不让 AI 分数、候选区域或 UI 操作隐式获得放行权。
- 不把 `HObject`、HALCON handle、DevExpress 控件、产品 ViewModel 或私有表类型泄漏到核心契约。
- 不根据当前图像偷偷改变方法、邻接、ROI、阈值或单位；替代路线必须由已批准方法资格明确允许。

调用方拥有流程编排、目标/设计关联、配方和权限、工艺解释、质量规则、复判、结果提交与设备副作用。模块只返回算法事实和支持证据。

### 1.3 完整批准能力、消费者与不适用条件

当前IM-029范围是二值响应域及其区域分析、工程参数建议和可选嵌入式UI；不是通用多类推理引擎。传统阈值、注册规则与模型mask共用同一三态/支撑/后处理/结果契约，只有§4.1六种Kind可执行。下表完整覆盖当前架构与USER-002第16项，不以已获代码准备状态的Core切片代替Adapter/UI设计。

| 已批准能力 / 使用场景 | 确定输入和结果 | 消费者与不适用边界 |
|---|---|---|
| 无训练标签的规则二值化与Blob调参 | 冻结Fixed/Global/Dynamic/Sauvola请求；输出F/B/U、组件、特征和筛选；人工试算不要求像素真值 | 独立灰度工具ConsoleHost及阻焊/涂覆工程调用；无标签不等于无用途/支撑资格，Global仍须冻结双峰资产。不能从无标签图猜材料阈值或合格判定 |
| 规则/颜色/深度模型输出后处理 | 一次请求选择一个ForegroundClassKey和同格FrozenMask；相同形态、连通、特征/筛选 | SurfaceToolHost及外观/胶体工程调用；规则联合通道和模型训练/推理由上游负责，模块不执行网络、不选模型、不收logits或三通道未注册数据 |
| 多类/重叠实例的显式二值投影 | 宿主逐ClassKey构造独立mask/operation；F为该类已确认像素，B为对该类已确认的非前景，U为abstention/冲突/缺域，不把其它类的未知改为B | 类别本体、互斥/多标签冲突和概率阈值归上游分类Owner，ClassificationThresholdRevision绑定该规则。模块不跨请求消冲突、合并类名或发布类别计数；PerInputObject只保留本类分组，重叠最终集合去重 |
| 超大图与严格邻域 | long父格、显式TileCore、真实halo、一次全局阈值、跨缝/角点等价和原像素结果 | 两Host及生产消费者均可调用；不存在内存容不下就缩图/局部阈值/截前N的隐式备用。超native重建限只影响对应特征，不把合法像素面积丢弃 |
| 工程有限参数建议 | 有标签Search/Holdout、有限候选/权重/次数/资源，返回完整评分、排序与未执行项 | 同Core服务和可选参数UI；无标注返回InsufficientEvidence，UI人工选参数仍可用。不会另造无监督优劣分数、在线学习或用期望组件数调参 |
| 无UI与可选WPF | 无隐藏窗口的两个独立组合根；WPF编辑草稿/试算/建议/应用请求，只读图像/结果/恢复 | 工程Host与只读复判Host通过公开端口复用同Core；应用生产参数、持久化、权限最终核对和质量放行均由宿主承担 |

无标签、没有物理尺度、没有UI、没有设备分别只影响其实际依赖部分：无标签不阻断显式分割，缺Scale只禁物理特征，headless不建WPF，纯软件不等待硬件SDK。图像/工艺语义或授权确实未知时按§20.3的Owner关闭相应门。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Segmentation.Core` 与 `Asun.Modules.Segmentation.AsunImage` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.Segmentation.Wpf` 可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。这条门禁直接支撑本模块已有的"两个独立组合根"（无 UI 组合根与 WPF 组合根）设计：Core 侧可在 Blazor Server 或控制台宿主中完整运行。

**Blazor/Web 宿主中的分割结果展示**：Web 端需要"显示前景区域、组件与筛选结果"时，服务端调用本模块的同一 Core 服务取得三态 F/B/U、组件、特征与排除原因，再投影到浏览器。约束：
- 浏览器端只渲染区域叠加与数值，不重算阈值、不自建连通组件、不自行判断前景/背景；**F/B/U 三态语义只有本模块一个来源**
- 前端不得把"未匹配到合格组件"显示为合格；U（abstention/冲突/缺域）在投影中必须与 B 视觉可区分，不得合并
- §1.2 的"不解释制程语义"在 Web 投影中同样成立：前端不显示"漏涂/露铜/残胶"等工艺结论
- 超大图场景（§1.3 "超大图与严格邻域"行）的 Web 展示由服务端按 tile 粒度发布分割结果平面，浏览器不下载整幅超大图

**AI 推理 Tiling 适配**：本模块与 `ai-inference` 的关系是**上游/并行两条产出、宿主侧合并**，不是替代。适配约束：
- AI 产出的模型 mask 走 §1.3 "规则/颜色/深度模型输出后处理"路径：宿主逐 `ClassKey` 构造 `FrozenMask` 交本模块做同格形态/连通/特征/筛选。**本模块不执行网络、不选模型、不收 logits**（§1.2 与 §1.3 明文）
- 类别本体、互斥/多标签冲突与概率阈值归上游分类 Owner；本模块不跨请求消冲突、不合并类名、不发布类别计数
- 本模块的 TileCore/halo 机制（§1.3 "超大图与严格邻域"）**不是**为 AI 推理服务的分块机制，两者的 tile 边界与 halo 语义各自独立；不得把本模块的 TileCore 契约当作 `ai-inference` 的 `RequestTileAsync` 契约使用
- §1.2 的"不根据当前图像偷偷改变方法、邻接、ROI、阈值"在 AI 链路上同样成立：AI 建议的阈值只能作为已批准方法资格下的显式新 `MethodRevision`，不能隐式改写

**HALCON 备选交叉验证适用性**：本模块是 2D 视觉链中双跑 CI 的**像素分类落点**，也是"两路都必须逐像素一致"的一环——与 `features-2d` 的容差门禁策略不同。约束：
- §4.1 六种 Kind（`FixedIntervals`/`GlobalMaxSeparability`/`GlobalSmoothHistogram`/`DynamicReference`/`LocalSauvola`/`RegisteredMask`）在 HALCON 路线与一条纯托管参照路线上按**同一 Golden 数据集**双跑：F/B/U 三态逐像素一致、连通组件的划分与邻接（4/8）一致、形态学结果一致、区域特征（面积/质心/包围盒/孔洞数/圆度）一致，逐项比对，差值超容差即 CI 失败并产出差异报告
- **已知的必然差异，不得抹平**：
  - `GlobalMaxSeparability`（Otsu）与 `GlobalSmoothHistogram` 是 HALCON 各自的实现，托管参照只能复算 Otsu 语义；`smooth_histo` 一路的差异**结构性不可消除**，标为仅诊断
  - `LocalSauvola` 依赖 HALCON `local_threshold` 的窗口边界、缩放与量化语义，托管参照在窗口边缘与低对比区必然不同；标为仅诊断，但**窗口内主体区域**的 F/B/U 一致性可作强门禁
  - `DynamicReference` 依赖 `mean_image` 的均值滤波语义与注册关系；注册关系不一致即整体不可比，此时门禁必须**先判可比性**再判像素一致，不可在不可比状态下产出"通过"
  - 形态学次序（§2.1 已核对：`opening` 先腐蚀后 Minkowski addition，`closing` 先膨胀后 Minkowski subtraction，且二者对每个输入 Region **独立**处理、`closing` **不会**自动合并相邻独立 Region）必须逐字复现：托管参照若把多 Region 先 union1 再形态学，即使像素结果相同也是**契约违规**，须单独断言
- **组件级一致性门禁**：`connection` 的 4/8 邻接必须与 HALCON 一致（OpenCV 固定 commit `a0cda081f8d769f40ab2f4904738b4787b44d07c` 的 `connectedcomponents.cpp` 在 `connectedComponents_sub1`（5652 行起）按 4/8 走不同算法路径，8 连通的 `CV_Assert(connectivity == 8)`（1138/1201 行）与 4 连通的 `CV_Assert(connectivity == 4)`（1768/1830 行）分属不同实现分支，见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)）；§2.1 已核对的 `max_connection` 返回非零即表示结果被截断，双跑中托管参照**不得**用局部组件计数猜测截断
- §1.2 的"不因当前图像偷偷改变方法"在双跑中同样成立：双跑 CI 不得以"两路取并集/交集"或"以像素更多的一路为准"规避失败
- HALCON 仍是生产路线；托管参照只作交叉验证与降级保险，不作发布依据，不引入 OpenCV 平行生产算法

## 2. 适用架构与依赖

```text
视觉项目 / 工具宿主 / 制程应用
        |  SegmentationRequest / SegmentationResult
        v
Segmentation.Core（无 UI、无厂商类型）
        |  ISegmentationBackend
        v
Segmentation.AsunImageAdapter
        |  ImageLibDotNet 公共 API
        v
HALCON 26.05（threshold / dyn_threshold / mean_image / connection /
               opening / closing / region_features / select_shape 等）
```

### 2.1 HALCON 路线选择和参数建议闭环

执行路径不得只写“自动阈值/Blob”，必须冻结 `MethodRevision`，明确输入类型与有效统计域、阈值路线、参数来源、连通规则和后处理。候选算子按以下用途分工；具体可用参数和输入限制以本地 HALCON 26.05 页及 `ImageLibDotNet` 公开签名为准：

| 目标 | 首选候选路线 | 自动化能力与限制 | 比较/拒绝条件 |
|---|---|---|---|
| 已知灰度边界、重复性优先 | `threshold` | 两端点来自已冻结 Profile；HALCON对整数图浮点端点截断，模块按§5先拒绝非整数端点，实际参数绑定请求hash | 模块非整数/不完整/范围不符的整数端点接纳前拒绝，不调用算子让其截断 |
| 全局双峰且直方图统计域完整 | `binary_threshold`，比较 `max_separability` 与 `smooth_histo` | HALCON 26.05 文档说明 `max_separability` 基于 Otsu，常比 `smooth_histo` 快；两者仅面向双峰直方图。该事实不是样本准确率保证，也不能用于单峰/多峰域 | 先做双峰/有效样本数/饱和比例资格检查；无资格返回 `NotQualified`，不自动挑另一方法掩盖 |
| 当前图相对独立参考图的局部变化 | `dyn_threshold` | 当前图、参考图、注册关系、平滑窗口和差值阈值均显式冻结；参考不能来自未注册的另一帧 | halo/配准/参考支撑不满足即拒绝，不以全局自动阈值替代 |
| 文档/细笔画在非均匀背景上二值化 | `local_threshold(adapted_std_deviation)` | §4.1/§5 冻结 mask_size、scale、range 和极性，仅 Byte/UInt16；属于独立方法，不替代材料覆盖 | 缺用途资格、窗口/编码不符或支撑不足即拒识；禁止自由生成参数 |
| 明确双阈值区间或迟滞分割 | `dual_threshold` / `hysteresis_threshold` | 低/高门限及连通/生长关系须属于显式方法快照 | 不把未达高门限但由低门限连通的像素与普通固定阈值混为同一语义 |
| 适应性全局候选或快速预筛 | `auto_threshold` / `fast_threshold` | 只作为独立注册方法，不得因为名称带 `auto/fast` 就假定适合所有分布或输出质量等同 | 必须比较适用输入、完整性、速度和误分割；未有目标样本证据时不得作为默认生产路线 |

参数“自动建议”只可在离线配置/工程 UI 产生候选：在相同的冻结样本集和相同有效域上，针对用户选定的目标函数（如候选几何一致性、漏分/过分割代价或人工标注差异）有限搜索类型化参数；返回排名、样本覆盖、参数范围、算法/后端版本、目标函数和失败样本。推荐值须经调用方确认、生成新 `ParameterRevision` 并冻结后才能用于生产。运行时不得从当前图像静默改变阈值、极性、连通方式、形态核或过滤范围，也不得把组件数量接近期待值作为调参目标。

自动/候选路线必须在同一 Golden/Replay 集上比较：像素/区域差异与标注真值、漏检/过检分层、边界和小目标表现、`P50/P95/P99` 端到端时间、峰值内存、输入规模、HALCON 线程/并行设置及资源释放。分布至少覆盖双峰、单峰、多峰、低对比、极稀前景、饱和、噪声、相邻粘连、孔洞、边缘截断和不同位深。测试记录实际阈值、实际算子、有效域与停止原因；不能只比较“看起来更干净”或算子微基准。没有代表性标注和Profile时，参数建议返回 `InsufficientEvidence`，由工程师提供显式值。

### 2.2 依赖端口

| 端口 | 方向 | 最小责任 | 核心是否强制依赖 |
|---|---|---|---|
| `IImagePlaneSource` | 入 | 提供不可变图像快照、位深、域和布局 | 是，宿主注入 |
| `SupportDomain` | 请求值 | D/I/W、有效域和分类资格在不可变请求内提供；不另读 latest 支撑源 | 是 |
| `ISegmentationBackend` | 入 | 执行已核对的视觉算子并返回托管投影 | 是，adapter 注入 |
| `IWorkingSetSource` | 入 | 唯一宿主资源账下预留/转交/释放确认；模拟宿主使用有界内存账 | 是 |
| `TimeProvider` | 入 | 单调计时和 UTC 时间；生产用 .NET 实现，测试用可推进时钟 | 是 |
| `IProgress<SegmentationEvent>` | 出 | 每次执行/服务实例的只读事件；异常隔离、终态不丢失 | 可选 |

核心 DLL 可在没有 WPF、数据库、相机 SDK、设备 SDK 或产品 Shell 的最小宿主中运行。HALCON 资源仅由 adapter 创建、租约和释放。

## 3. 统一数据语义

### 3.1 三态支持域

请求中的 `D` 是应处理像素域，`I` 是调用方批准的排除域，二者在接收时必须满足 `D ∩ I = empty`。模块不得因为缺 tile、预算或算法失败而缩小 `D`。

执行完成后的分类资格为：

```text
V = D ∩ V_image ∩ V_support ∩ V_class ∩ V_done
F = 前景且位于 V
B = 背景且位于 V
U = D - (F ∪ B)
```

`U` 不是背景。至少区分：`MissingImage`、`InvalidPixel`、`Saturated`、`InsufficientHalo`、`ReferenceUnavailable`、`GrayAmbiguous`、`MethodOutOfDomain`、`NotExecuted`、`Cancelled`、`BudgetExceeded`、`NumericError`。

以下三种空结果语义不可合并：

| 情况 | 语义 | 允许的输出 |
|---|---|---|
| `D` 为空 | 本次没有任务域 | `Completed`，`classificationScope=Empty`，组件数为 0 |
| `D` 非空且 `V` 为空 | 没有有效分类资格 | `Rejected` 或 `NotQualified`，不得报告“空前景” |
| `V=D` 且 `F` 为空 | 完整有效域内未观察到响应 | `Completed`，`foregroundEmpty=true` |

### 3.2 原始与派生结果

固定阈值或参考比较先生成 `F0/B0/U0`，再按请求生成 `F1/B1/U1` 等派生域。形态学可能改变孔洞和连通关系；任何派生区域都必须带 `sourceStageId`、算子、结构元和支撑损失。派生结果不得覆盖原始区域，也不得把被未知影响的像素转成背景。

### 3.3 标签与稳定身份

HALCON 返回的对象序号仅是本次计算的临时索引。模块输出 `componentKey` 由输入快照修订、方法修订和组件最小像素坐标形成的确定性诊断键；它不代表跨重检的物理目标身份。目标关联由调用方完成。

## 4. Module API Contract v0.2：请求与结果

这些是模块内唯一公开契约，不是平台持久化 DTO。namespace 为 `Asun.Modules.Segmentation`；所有列表使用ImmutableArray<T>；宿主在请求构造边界冻结可变数据，不能通过Unsafe/底层数组别名继续修改。Core不无条件复制整份冻结像素域，先按MaxRuns校验请求中各域/Mask runs总数和checked字节，再做有界元数据投影；超限接纳前拒绝。禁止自由算子字符串、反射脚本、产品 ID 和厂商 handle。下列代码定义主记录；相关类型的完整字段表在附录 A，不能仅声明空类型或由实施者补字段。

```csharp
public sealed record SegmentationRequest(
    string ContractVersion, string OperationId, long RequestRevision,
    ImageSnapshotRef Image, SupportDomain Domain,
    MethodSpec Method, ProcessingSpec Processing,
    MethodQualification Qualification, ExecutionLimits Limits,
    string AlgorithmRevision, string ParameterRevision, string ParameterHash,
    FrozenMask? Mask, PixelScale? Scale);

public enum SegmentationMethod {
    FixedIntervals, GlobalMaxSeparability, GlobalSmoothHistogram,
    DynamicReference, LocalSauvola, RegisteredMask
}
public enum ForegroundPolarity { Light, Dark }
public enum DynamicMode { Light, Dark, Equal, NotEqual }
public enum Connectivity { Four = 4, Eight = 8 }
public enum UnknownReason {
    MissingImage, InvalidPixel, Saturated, InsufficientHalo,
    ReferenceUnavailable, GrayAmbiguous, MethodOutOfDomain,
    NotExecuted, Cancelled, BudgetExceeded, NumericError,
    ModelAbstained, ColorUndefined
}
public enum ExecutionState {
    Created, Validating, Accepted, Queued, Acquiring, Segmenting,
    Morphology, Connecting, FeatureExtraction, Draining, Drained,
    ResourcesReleased, Completed, CompletedPartial, Rejected,
    NotQualified, RecoverableError, Cancelled, TimedOut, Failed, Unknown
}
public enum Completeness { Empty, Complete, Partial, NotEvaluated }
public enum FeatureStatus {
    Valid, Empty, InsufficientSupport, NotRequested,
    BudgetExceeded, NumericError, NotApplicable
}
public enum ResultUse { DiagnosticOnly, AlgorithmFacts }
public readonly record struct OperationTicket(
    string InstanceId, string OperationId, long RequestRevision);
public readonly record struct PixelRun(
    long Row, long ColumnBegin, long ColumnEnd);
public sealed record PixelRegion(ImmutableArray<PixelRun> Runs);
public sealed record SegmentationResult(
    OperationTicket Ticket, ExecutionState State, ResultUse Use,
    ClassificationSummary Summary, QualitySummary Quality,
    Provenance Provenance, ResourceUsage Resources,
    IResultLease? Data, ImmutableArray<ModuleError> Errors);
```

`PixelRun` 是包含两端的父图坐标区间，按 (Row, ColumnBegin) 升序；同一行重叠或相邻 run 必须归一合并，拒绝 end<begin、越界和 checked 面积溢出。空区域为零 run，不能用空 object tuple 与有一个空 Region 混淆。像素中心从 (0,0) 起；ParentGridId/Revision 冻结坐标格，不做隐式重采样。Core 的坐标/面积用 long；结构元PixelRegion是以原点为中心的有符号偏移，不套父图非负边界，但仍校验canonical/核尺寸；其它像素域须在父图内。HALCON adapter只接纳能够表示的局部tile坐标和尺寸，并在返回时 checked 加父图偏移。

`SegmentationResult` 的 Summary/Quality/Provenance 是小型不可变值。大型 F/B/U、组件和边界归 `IResultLease` 管理，均为托管 RLE/值投影，无 native handle；调用方明确持有、分页读取并释放。执行资源归还和结果租约的所有权转交是两件事，见 §10.1。结果不会把完整大图复制进 ViewModel。

### 4.1 输入和派发封闭性

`MethodSpec` 为抽象 record，仅允许以下五种 sealed 类型（GlobalSpec 承载两个 Kind，共六种方法）；`Kind`除GlobalSpec仅允许两个全局Kind外由类型固定，不接受与分支不一致的枚举。没有名为 Fallback 的可执行方法；fallback 是 §6.5 的一个显式新 operation。

| 分支 / Kind | 必填字段、适用输入及顺序 |
|---|---|
| `FixedIntervalsSpec / FixedIntervals` | `Intervals:ImmutableArray<GrayInterval>`；1..64 个有限闭区间，排序、去重并合并相邻整数/重叠区间；单标量 Byte/UInt16/Real32。在同一有效域逐区间 threshold 后 union1；区间外为 B，不另用 Polarity 翻转 |
| `GlobalSpec / GlobalMaxSeparability` | `Polarity, StatisticsDomain:PixelRegion`；Byte/UInt16；完整统计域必须属于 W 的真实有效域；一次 binary_threshold(max_separability) |
| `GlobalSpec / GlobalSmoothHistogram` | 同上，Kind 显式为 GlobalSmoothHistogram；Byte/UInt16 基线；一次 binary_threshold(smooth_histo)，不得根据当前图临时挑两者之一 |
| `DynamicSpec / DynamicReference` | `Mode:DynamicMode, Offset:double, Reference:ImageSnapshotRef?, MeanWindow:WindowSpec?`；且 Reference/MeanWindow 恰一非空；同格/同编码/同灰度单位与处理修订；一幅冻结参考或从当前原图生成一次均值背景 |
| `SauvolaSpec / LocalSauvola` | `Polarity, WindowSize:int, Scale:double, Range:double`；仅 Byte/UInt16 单通道文档/细笔画响应用途，cv2 local_threshold(adapted_std_deviation)，三个生成参数都显式传入 |
| `MaskSpec / RegisteredMask` | `MaskRevision, ForegroundClassKey:string`；请求 Mask 必填，经典方法 Mask 必须为空；只消费外部冻结 F/B/U，不调模型、不训练、不修改模型资产 |

`GlobalSpec` 的 Kind 只允许上述两个值，其它值拒绝。相关字段是方法参数，不从当前 UI 或最近成功请求补齐。

颜色路径仍是**注册标量输入**：宿主通过预处理公开端口提供 RGB 单通道或已冻结颜色转换的一个输出通道，Image.Origin 声明转换/通道/编码/单位/父图修订。模块不得接三通道图后猜“取最亮”。HSV Hue 是周期量，跨零范围由宿主在同一编码下提供两个闭区间；灰/黑像素的未定义 Hue 从 ClassificationValid 移出，标 ColorUndefined；不能仅凭 Hue 低值判断红色。若应用需要 H/S 联合分类，宿主先提供带规则修订的冻结 mask，再走 RegisteredMask，模块不增加第二个颜色转换引擎。

学习路径必须携带原输入 hash、模型 hash/版本、预处理 hash、backend 版本、类别键、分类阈值修订、F/B/U 和 abstention 来源；坐标不一致接纳前 SEG-002。模块只做支持交集、形态/拓扑/特征，学习置信或高通响应不能隐式成为材料覆盖事实。ROI 变化、模型或预处理变化必须换 operation/参数修订；不复用旧 mask；Mask.Maturity=Shadow/Advice 时即使 State=Completed，Result.Use 也强制 DiagnosticOnly，不受 Qualification.Use 覆盖。

### 4.2 SG-C1～C4 的 Core 构造边界

SG-C1～C4 的生产 Core 只公开 §4、§8 和附录 A 中的值类型、端口与 `SegmentationService` 构造；不会把 Simulator、ConsoleHost、SurfaceToolHost 或测试 Profile 编译进 Core DLL。记录类型使用其声明的公开构造，构造时不得静默填默认值、排序或归一化：`PixelRegion(ImmutableArray<PixelRun>)` 接受已按附录 A 规则冻结的 RLE，非法顺序、相邻未合并 run、越界或 checked 溢出由 `Validate` 拒绝。`SegmentationIdentity.ComputeParameterHash`、`ComputeRequestHash` 是 C1 唯一身份入口；没有第二个字符串拼接或显示文本 hash 入口。

Core.Tests 中的 Simulator 只实现这些端口，不是产品 API：`FrozenFixtureSource(ImageSnapshotRef image, ImmutableArray<FrozenTile> tiles, SimulatorFaultControl faults)` 实现 `IImagePlaneSource`，按 `TileReadRequest` 返回冻结lease/缺测；`FrozenProjectionBackend(BackendProfile profile, ImmutableArray<FrozenBackendCase> cases, SimulatorFaultControl faults)` 实现 `ISegmentationBackend`，`Plan`按请求/Profile返回有界计划，`ExecuteAsync`只返回按RequestHash选中的冻结BackendOutput，不执行视觉算法；`BoundedWorkingSetSimulator(RuntimeLimits runtime,long capacityBytes,int sourceSlotCapacity,TimeProvider time,SimulatorFaultControl faults)`实现`IWorkingSetSource`，按Owner/ticket/lease记录预留/转交/确认释放。FrozenFixtureSource另有 `(ImmutableArray<FrozenImageFixture> images,SimulatorFaultControl faults)` 重载供SG-C4多冻结图输入，单图构造委托到一个fixture的同一路由；SnapshotId/Revision/hash三者匹配才返回对应tile，不读latest。三个构造都拒绝空身份/负容量；数据冻结、故障闩锁和两Host的精确字段见A.5，测试可注入固定时钟/闩锁，不从当前UI补值。

两个无 UI Host 的唯一装配顺序是：`FrozenFixtureSource` + `FrozenProjectionBackend` + `BoundedWorkingSetSimulator` + 固定 `TimeProvider` + `RuntimeLimits` → `new SegmentationService(images, backend, workingSets, time, runtime, events)`；`ConsoleHost` 只使用 FixedIntervals/全局路线的冻结标量 fixture，`SurfaceToolHost` 只使用注册通道或 RegisteredMask fixture。两者各自创建新的 `InstanceId`、`OperationId` 和 `originalOwnerHeld`，均执行 §12.2 的 `Validate → Start → Wait/Query → 消费 try/finally → Release/Recover → Close`；没有隐藏窗口、产品数据库、设备 SDK 或共享可变静态状态。C2 的完整状态/Simulator 断言与 C1 的值校验共用同一装配，不另造第二套服务入口。

## 5. 强类型参数、单位、范围和来源

所有计算字段必须显式提供。下表安全范围是本模块技术决策，不是客户验收阈值；示例数值只用于合成测试，取消旧 `ExecutionLimits.Default`、8-bit 门限和机器相关默认值。Profile 由宿主冻结并带修订/hash。

| 参数 | 类型/单位 / 技术有效域 | 来源、失效/拒绝规则 |
|---|---|---|
| `GrayInterval.Min/Max` | finite double，原始灰度单位，Min≤Max | 整数图端点必须是整数且在声明编码范围内；Real32 不接受 NaN/Inf；不让 HALCON 隐式截断 |
| `GlobalSpec.Polarity` | Light / Dark | 只影响全局自动路线；Light 为 g≥T，Dark 为 g<T，实际 T 记录；固定闭区间不使用它 |
| `DynamicSpec.Offset` | finite double，0..声明灰度跨度 | 不接受负 Offset；零允许诊断但需噪声/资源资格，手册示例值不自动成为本模块推荐 |
| `WindowSpec.Width/Height` | pixel，1..16383 奇数 | 实际读窗口完整；偶数拒绝而非升级；均值只在真实矩形输入执行 |
| `SauvolaSpec.WindowSize` | pixel，3..16383 奇数 | 必须大于方法资产声明的目标笔画宽度；不把薄笔画资格用于厚材料覆盖 |
| `SauvolaSpec.Scale/Range` | Scale finite，0<k≤1；Range finite，R>0 且≤编码跨度 | 明确传入，不使用每图 min/max 计算新 Range；缺细笔画资格为 NotQualified |
| `Processing.MorphologySteps` | 有序 ImmutableArray，0..16 步 | 每步 Op、Kernel、Iterations、ObjectMode、StageId；开闭先后/迭代不同即参数修订不同 |
| `RectangleKernel` | 奇数 Width/Height，1..4095 pixel | 以精确整数支持集合定义，不用显示缩放；非等距像素不称物理圆 |
| `CircleKernel` | Radius=n+0.5，n=1..2047；中心整数 | 排除 HALCON 整数半径的半像素移位；记录 gen_circle 的真实 runs/hash，支撑按实际 runs 算，不只 ceil(radius) |
| `ExplicitKernel` | 非空 PixelRegion，≤4095×4095、有原点且关于原点中心对称 | 第一版拒绝非对称/分数锚点，避免 erosion1 的重心/镜像歧义；后续独立方法才能扩展 |
| `Iterations` | int，1..64 | Opening/Closing 用 cv2 对同一整步重复；纯 Erosion/Dilation 显式迭代；复合支撑累加，不能仅取最大半径 |
| `Connectivity` | Four/Eight | 输出组件邻接；native 线程作用域与孔洞背景邻接见 §7.1 |
| `FeatureSet/FeatureFilters` | §7 枚举/不可变列表；≤64 键/256 谓词 | 单位、阶段、端点、缺值行为固定；拒绝未知键、自由脚本和矛盾端点 |
| `TilePlan` | 显式非重叠core列表（宿主可先按固定网格生成该列表，API不另有网格分支）；core 宽高 1..32768 pixel | checked 计算 core+复合 halo 后仍须满足 adapter Profile 尺寸/预算；排列变化不改算法/稳定 key |
| `MaxPixels/MaxRuns/MaxComponents/MaxEquivalences` | 正 long / 正 long / 正 int / 正 long | 宿主有限 Profile；按整个 operation 累计。MaxPixels 对 D 像素计一次，halo/各阶段实读另计资源 |
| `MaxWorkingBytes/MaxResultBytes/MaxProjectionBytes` | 正 long，byte | 分配前 checked；执行、结果转交、UI 投影分别有界，不从证据额度推导 |
| `Timeout/DrainTimeout/CleanupTimeout` | TimeSpan，1 ms..24 h | 分别计算期限、排空等待和清理预算；执行取消 token 不替代 cleanup token |
| `MaxParallelTiles/QueueCapacity/MaxRetainedResults` | 1..64 / 0..4096 / 1..1024 | 宿主容量预算；0 表示不排队，忙时接纳前拒绝；没有隐式 CPU 核数默认值 |
| `ProgressInterval` | TimeSpan，10 ms..10 s | 通知节流，仅合并 Progress；不丢生命周期/终态事件 |

D/I/W/Valid/ClassificationValid、灰度范围、stride、父图格、参考版本和方法资格是请求的一部分。D 可以为空，但 descriptor 必须有效；D 非空时 D⊆W、D∩I=∅，域不允许越界。缺物理尺度仅令 AreaPhysical 不可评价，不阻断像素分割；要求它筛选时明确返回 Unknown，不按零正常排除。

## 6. 方法选择与处理步骤

### 6.1 通用流程

1. 纯校验 OperationId/RequestRevision、输入快照、D/I/W、坐标/编码、方法和参数 hash；未接纳时不创建像素/native 对象。
2. 校验 backend.Profile/Plan 的能力、core+累计 halo 尺寸和最坏字节数，按完整请求与并发 Profile 预留有限工作集并接纳，随后取得精确输入租约；冻结统计域，不在 tile 内重估全局阈值。
3. 按已批准路线计算原始 `F0/B0/U0`，记录实际阈值或参考图 revision。
4. 如请求包含形态操作，在有足够支撑的工作域上执行，并输出派生域及支持损失。
5. 以请求的 4/8 邻接生成局部组件；分块时保留 core 边界 run/pixel 和 support。
6. 汇总跨 tile 等价关系，所有 tile 到齐后再形成全局组件。
7. 计算完整特征，执行类型化筛选，保留每个排除原因和前后引用。
8. 形成质量摘要、资源摘要、诊断事件和不可变结果；释放临时租约。

### 6.2 路线决策

公开方法仅为 §4.1 的六个 Kind；dual/hysteresis/auto/fast_threshold 在 §2.1 只是后续研究候选，不可通过自由字符串执行。FixedIntervals 不使用极性；Global 两方法须完整统计域与双峰资格；DynamicReference 须注册参考或显式 MeanWindow；LocalSauvola 须 DocumentStroke；RegisteredMask 须原输入/格/类别绑定。任何适用门失败都按 §8/§9 返回，不在 operation 内替换方法。备用仅是调用方按已冻结规则发起的新 operation，见 §6.5。

### 6.3 HALCON 26.05 / AsunImage 核对结果

项目内 `halcon算子手册\operators` 提供 HALCON 26.05 的 `threshold`、`binary_threshold`、`dyn_threshold`、`local_threshold`、`mean_image`、`connection`、`opening`、`closing`、`region_features`、`select_shape`、`union1` 文档。适配器统一通过 `ImageLibDotNet.cv2` 调用算子；算子名和语义按目标版本文档，不另接 `HOperatorSet`/`halcondotnet.dll`，不扫描 AsunImage 内部，也不重复核验封装是否包含这些算子。

这些算子不是核心 API，也不代表本模块算法已获资格。输入域、空对象、整数截断、异常、线程和参数边界以 26.05 手册为准；仅当 C# 参数类型、重载或封送方式确有歧义时，查看公共签名或在消费项目编译确认。adapter 必须显式映射并记录 method、适用的 polarity/mode、offset、kernel 和 connectivity，不能靠 wrapper 默认决定前景极性或其它参数。

已直接核对的 HALCON 26.05 页面语义包括：`threshold` 对整数图像会截断 min/max 的浮点阈值，对 real/vector 图像使用浮点精度；`binary_threshold` 的 `max_separability` 与 `smooth_histo` 均只适用于双峰直方图，前者基于 Otsu 且常比后者快，但不构成对具体样本更准确的保证；`threshold` 是 reentrant、global scope，并在 tuple/data level 自动并行。模块不得将这些页面事实扩展成未经 Golden 验证的生产质量结论。

形态学和区域对象语义也按 HALCON 26.05 冻结为适配器候选约束：`opening` 先腐蚀再做 Minkowski addition，`closing` 先膨胀再做 Minkowski subtraction；两者都对每个输入 Region 独立处理，`closing` 不会把相邻的独立 Region 自动合并。若请求的语义是“整个二值前景作为一个集合”再做形态学，必须先显式 `union1`，把这一步和输入对象数写入 provenance，再调用形态算子；否则保留对象边界。形态学之后才可按已合并的组件执行形状筛选，筛选全排除不能删除 `F0/B0/U0` 或改变原始前景证据。

算子/参数决策表依据本地 HALCON 26.05 页面：[`threshold`](../../../halcon算子手册/operators/threshold.html)、[`binary_threshold`](../../../halcon算子手册/operators/binary_threshold.html)、[`dyn_threshold`](../../../halcon算子手册/operators/dyn_threshold.html)、[`local_threshold`](../../../halcon算子手册/operators/local_threshold.html)、[`auto_threshold`](../../../halcon算子手册/operators/auto_threshold.html)、[`fast_threshold`](../../../halcon算子手册/operators/fast_threshold.html)、[`dual_threshold`](../../../halcon算子手册/operators/dual_threshold.html)、[`hysteresis_threshold`](../../../halcon算子手册/operators/hysteresis_threshold.html)。形态/对象语义依据 [`opening`](../../../halcon算子手册/operators/opening.html)、[`closing`](../../../halcon算子手册/operators/closing.html)、[`union1`](../../../halcon算子手册/operators/union1.html)、[`connection`](../../../halcon算子手册/operators/connection.html)、[`region_features`](../../../halcon算子手册/operators/region_features.html)。手册事实不等于本模块样本资格。

### 6.4 连通和分块

- 整域在资源允许时先以 HALCON `connection` 建立基准结果。
- 分块时每 tile 必须取得真实 halo，只写 core 的 F/B/U；不得按 tile 独立过滤后再拼接。
- 通过边界 run/像素建立等价关系，采用有界并查集或等价实现合并；所有 core/接缝到齐后才输出全局组件。
- 固定 native worker 上经 cv2 读取/设置/恢复 `tsp_neighborhood` 与 `tsp_clip_region`，设置作用域内不跨 await 或重入；用 `get_system('max_connection')` 核完整返回要求为 0，仅读取不修改全局。非零返回 SEG-003，不靠局部组件计数猜是否被截断。

### 6.5 具体路线、备用、训练与恢复条件

下表是模块固定派发的路线集合。MethodSpec 与输入适用域一致且 Qualification 满足才执行，多个可用方法也不按运行结果挑选。`Fallback` 不在同一 operation 内发生：调用方收到拒识后按自身冻结决策表提交新 OperationId/ParameterRevision，请求 Qualification.FallbackFrom 绑定原 ticket、失败门和规则修订；模块再次完整校验，不扩大 W 或降低质量门。

| 路线 | 具体公共调用顺序 | 允许条件 | 拒绝/备用条件 | 训练与恢复 |
|---|---|---|---|---|
| 固定灰度 | 校验位深/端点 → 经 `cv2` 调用 `threshold` → 限定 `D` → 计算 F/B/U | 灰度端点、输入位深和处理域已由 Profile 资格化 | `min > max`、NaN/Inf、位深不匹配、输入域缺失 | 不需要训练；修正请求后以新 operation 重试 |
| 全局自动 | 冻结完整统计域 → 经 `cv2` 调用 `binary_threshold` → 记录 `usedThreshold` → 应用至 core | 统计域完整；Profile 明确方法（如已资格化的 `max_separability` 或 `smooth_histo`）；双峰/饱和门通过 | 单峰、极稀前景、饱和、统计域被 tile 截断 | 不需要训练；可按决策表转局部路线，但不能静默转固定阈值 |
| 局部参考 | 校验注册参考/halo → 经 `cv2` 调用 `mean_image`（或调用方提供等价背景）→ `dyn_threshold` | 参考图与当前图同格、同位深/预处理；奇数窗口和 halo 足够；只分类完整窗口落在真实有效输入内的中心 | 参考缺失、配准不一致、边界支撑不足、参考被污染 | 不需要训练；补齐参考/halo 后新 operation；`mean_image` 镜像边界影响的中心必须排除并置 U |
| 局部 Sauvola | 取得真实矩形 core+halo → cv2 `local_threshold(adapted_std_deviation)`，显式 mask_size/scale/range → 支撑内中心投影到 D | 仅 §4.1 的文档/细笔画用途、Byte/UInt16、已冻结参数/用途证据 | 其它像素类型/厚材料用途拒绝；缺窗口输入置 U；偶数不升级 | 不训练；修订请求后新 operation，不转动态阈值掩盖 |
| 受控形态 | 保存 F0/B0/U0 → 按请求明确逐对象/先 `union1` → 构造已登记结构元 → 经 `cv2` 调用形态算子 → 传播支撑 → connection/全局合并 → features/filter | 奇数 kernel、锚点/形状/支撑明确；调用方允许派生域 | 偶数/空 kernel、未知支撑、物理尺度不能映射像素 | 不训练；失败保留 F0/B0/U0，不能把派生失败当空结果 |
| 学习/模型分割 | **不在本模块执行训练或推理**；由 `ai-inference` 返回已冻结 mask/score/abstention，再按同一 D/I/坐标适配 | 仅消费已批准模型输出，且模型/输入/预处理/置信和 abstention 可追溯 | 无模型 revision、类别语义不明、mask 未注册到同一像素格、低置信或缺支持 | 训练归 `model-assets`/`ai-dataset-governance`；模型切换先排空旧请求并重新验证，不能在本模块内在线学习 |

`VariationInspection` 的良品模型训练、准备和比较也不属于本模块。若调用方要使用其差异域，必须以已冻结、带 revision 的区域/支持输入调用本模块；本模块不得反向修改或吸收模型样本。

噪声、反光、遮挡和退化不自动触发隐式去噪或补洞。成像质量和预处理由上游模块提供并在输入快照中引用；本模块只执行已批准的参考/阈值/形态路线。任何 fallback 都必须满足：

1. 目标语义仍是同一类“响应区域候选”，且调用方明确允许路线替换；
2. 新路线的支撑、单位、灰度尺度、极性和质量门不低于原路线要求；
3. 原ticket的Provenance.Method保留原路线，新结果的Provenance.Method为新路线；FallbackFrom.From/FailureCode/RuleRevision绑定原ticket、触发门与规则修订，适用域由各自请求保存，不另造自由路线字段；
4. 没有可证明等价的路线时返回 `NotQualified`/`Rejected`，不返回猜测结果。


### 6.6 阈值比较、严格支撑与大图实施步骤

**固定与自动阈值。** 固定区间 F={p∈V:a≤g(p)≤b}，多区间取并集且 B=V−F；ForegroundPolarity 不适用于它。所有方法先按 QualifiedDomain 限定分类资格，D 中不在资格域的像素置 MethodOutOfDomain；不得缩小 D。

资格统计冻结如下：全局 S=GlobalSpec.StatisticsDomain，非全局 S=D∩Qualification.QualifiedDomain；实际样本数 N=|S∩ImageValid|，饱和分子为 |S∩ImageValid∩union(Saturated patches)|，重叠只计一次，SaturatedFraction=分子/N；ValidFraction=|D∩ImageValid∩ClassificationValid∩QualifiedDomain|/|D|。空分母为 null。全局要求 S 非空且 S⊆W∩ImageValid，缺一个实际样本即 NotQualified，不用部分直方图；N≥MinStatisticsPixels、饱和比例≤MaxSaturatedFraction、HistogramBimodal=true 才可执行。像素虽然可供统计，Saturated patch 中的分类仍是 U。非全局仅对 D 非空时应用相同数量/饱和门；D 空直接走 Empty。双峰、用途、笔画宽和弱信号资格来自冻结资产，单峰/多峰/低对比/极稀响应无资格不得以算子成功补证；本模块不发明对比度阈值。

全局自动返回 T 后：Light 是 g≥T，Dark 是 g<T；整数 Dark 分块应用为 [编码最小值,T−1]，T=编码最小值时是空 F，不能把 g=T 放两类。原 native 返回域作为整图基准，UsedThreshold/统计样本数/统计域 hash 都必须记录。统计域完整性与双峰用途资格来自冻结方法资产，未提供为 NotQualified；不运行图像后临时估一个“双峰阈值”通过门。若原完整统计域不能放进 native 预算，拒绝该全局路线 SEG-007；不暗中每 tile Otsu 或用缩图漏小目标。诊断预览与材料覆盖用途分别资格化。

**动态参考的闭/开边界。** 对非负 Offset=d、参考 L：Light: g≥L+d；Dark: g≤L−d；Equal: L−d≤g≤L+d；NotEqual: g<L−d 或 g>L+d。每次只选一个 Mode，B 是这个响应谓词的互补，不是另调相反极性；d=0 时 Light/Dark 的等号都命中，故不能同时当两个互斥类别。合成 g=[95,100,105]、L=100、d=5 时四模式 F 分别为 {105}/{95}/{95,100,105}/空。均值背景会像高通突出边缘，B 不自动表示没有涂层。Offset 靠近零的噪声峰值需 Profile 覆盖，禁止将手册的 5..40 经验值作为通用生产门限。

**Sauvola。** 按 local_threshold 的 adapted_std_deviation 实施，Dark 为严格 g<T(r,c)；Light 为官方反相等价语义，不能只把 Dark 求补集。T=μ[1+k(σ/R−1)]；μ/σ、编码、k/R 与窗口来自冻结参数/手册语义，由 cv2 算子完成，不另写托管实现。窗口/Range 不从每图 min/max 静默改变；只处理细笔画用途。等于阈值、均匀窗、低对比和饱和窗必须作为 adapter Golden，不因原图看起来干净就选这个方法。

**严格支撑不是最终与原 V 相交。** W 是允许读取的真实上下文，D 是输出/分母；排除域 I 可否用于上下文由 Domain.ContextPolicy 声明（AllowValidExcluded / ExcludeAll）。初始有效域V0=W∩ImageValid∩ClassificationValid∩QualifiedDomain；ContextPolicy=ExcludeAll时再减I。窗口可越D但不越真实W；失去资格的邻域不当可支撑背景。每个有限邻域步骤 j 的依赖支持 K_j 均固定为真实离散集合，V_j={p:p+K_j⊆V_(j−1)}；缺窗口像素、真实图边、U/缺帧均失去支撑。先在 W 上逐步处理，只在末尾投影到 D；不能每步裁 D、补零、镜像 tile 或补洞当观测。Opening/Closing 每步含两个依赖，重复迭代逐次累加；3×3 均值后 3×3 closing 的总行列 halo=1+1+1=3。实际结构元投影由 runs/hash 固定，非对称核当前拒绝；tsp_clip_region=false 在受控 scope 内保留负坐标核/区域，最终显式交 W/D，异常也恢复。

对每个派生阶段返回 F_j/B_j/U_j、依赖支持修订、Added/Removed/SupportLost。Added=(F_j−F_(j−1))∩V_j；Removed=(F_(j−1)−F_j)∩V_j；原 F 后来变 U 计 SupportLost，不计“已去除”。形态学不会把未知邻域填成背景。ObjectMode 必填；WholeForegroundSet：union1→形态→connection；PerInputObject 只接受带对象分组的 FrozenMask，逐对象 provenance 保留，组件计算前把同类重叠前景 union1 去重，不能重复面积。

**超大图。** 父图 long 坐标，单 tile 本地 int 坐标；ImageSource 每次交付连续完整矩形 core+累积 halo 的只读槽，执行 scope 预先覆盖最坏返回（棋盘噪声的 runs/组件）。在 core 上 cv2 connection 后，经 get_region_runs 投影每个单 Region，checked 平移到父图；只写 core、halo 不计面积/矩。接缝以父图中 4 邻接 (0,1)/(1,0)，8 邻接另加 (1,1)/(1,−1) 的已知 F 对建立一次等价，必须含四 tile 角点；RLE 范围匹配必须等价。并查集采用路径压缩、按秩；稳定 key 选全局字典序最小像素而非内部 root。局部 3+3 像素、面积下限 5 的跨缝组件只能合并成 6 后筛选。

面积/一阶原矩/包围盒只计不重叠 core、checked 合并；周长、孔洞和圆度不能求 tile 值的和，须从完整全局 runs 重建一个 Region 再求。若该单组件超出 native 坐标或重建预算，像素面积仍合法，依赖 native 的特征返回 BudgetExceeded/NotApplicable，不能伪造 0 或退回局部和。缺 tile/接缝时仅交诊断片段，所有邻 U/未闭前沿的组件 TopologyStatus=TouchesUnknown 或 Incomplete，不发布最终计数或稳定全局 key。粗 ROI/缩图只可供定位/显示或离线候选；生产分类必须回原像素与原 D/W，不能据低分辨率“无响应”跳过未经批准的 D。

### 6.7 有界、可复现的参数建议操作

建议不是生产 Execute 的副作用。附录 A 的 SuggestParametersAsync 仅接受冻结标注集、训练/留出 fixture hash、明确用途/评价参数、离散候选值列表、MaxEvaluations/Timeout/MaxWorkingBytes；不含设备或生产写入能力。按候选参数 canonical hash 排序，用相同 D/W/真值执行相同方法，遇预算/取消停止并列出未执行项，不改搜索顺序；候选不能自动扩大 ROI/改变分类用途。评分按冻结真值域计算像素 FP/FN/U，成本仅用附录 A 的三项权重；边界、过分/粘连只作组件诊断，不参与未定义的排序成本，不把“组件接近预计个数”当真值。

先只用搜索集排名，按全部成本、U 比例、参数 hash 的字典序破同分；选前 request.MaxCandidates 个对冻结留出集再评价，留出不参与搜索。输出候选完整参数/实际路线、各样本失败/漏分/过分、运行资源及停止原因；空标注、全未知真值、用途不匹配或未完整评估返回 InsufficientEvidence/Partial，不给默认推荐。生产引用仍由宿主显式确认、生成新参数修订/hash；样本/输入/算法/adapter 变化使候选过期。技术建议不能冻结客户材料阈值。

## 7. 区域、边界、拓扑、特征与筛选

首批 feature 的单位/数值槽由附录 A 的 FeatureKey/FeatureValue 固定。Processing.FeatureStageId 指定 `raw` 或已登记形态 StageId；只在该阶段计算组件/特征/筛选，避免实施者随意混用原/派生区域。所有 StageRegions 仍保留原始三态和差区。FeatureStageId 不存在为 SEG-001。HALCON 对多 Region 返回 tuple 时按显式 component 迭代或核 tuple 长度/order，不能把另一组件的 area 配到本组件的 centroid。

| Feature | 定义、单位、主算子/拒识 |
|---|---|
| AreaPixels | CountValue:long，pixel²；全局去重 F 像素数；run inclusive checked 累加，不按 halo 或对象重叠重复算 |
| CentroidRow/Column | Value:double，pixel；像素中心一阶矩/N；N=0 不创建组件/无质心。矩累计 checked long，超界用 BCL BigInteger 内部累加后 finite 投影，不浮点乱序累加 |
| BoundingBox | Box:PixelBox，pixel，含最后像素，直接 canonical runs 的极值；不存在外部 half-open 转换 |
| Perimeter | Value:double，pixel；HALCON `contlength`：轴邻 1、斜邻 √2，**不含孔洞轮廓**；这是离散外轮廓长度，不是 4A/P² 的圆度定义，不宣称亚像素物理边界 |
| Circularity | Value:double，Dimensionless；HALCON `circularity` 原定义和 clipping，不能替换为其它库的 4πA/P²；必须完整全局组件且 finite，否则明确 FeatureStatus |
| HoleAreaPixels | CountValue:long，pixel²；HALCON `area_holes` 对完整组件的孔洞像素总和；未知/支撑洞不能当真实孔洞 |
| Boundary | Boundary:PixelRegion，pixel；cv2 `boundary(...,'inner')`，保留孔洞边界，不用 inner_filled 擦掉孔洞；触 U/输出域裁边时 Status=InsufficientSupport，不画成真实物体闭边 |
| GrayMean/Min/Max | Value:double，Gray；对应同一输入快照的 valid 灰度，用 cv2 `intensity`/`min_max_gray`；灰度 valid 计数不足 N 时 InsufficientSupport，不能填零 |
| AreaPhysical | Value:double，SquareMillimeter；N×PixelScale.AreaPerPixelMm2，仅已资格化等面积平面格；无 Scale、格不符或非线性用途为 NotApplicable |

### 7.1 闭合、背景邻接与未知

前景 Four 则孔洞背景用 Eight，前景 Eight 则孔洞背景用 Four，形成数字拓扑的对偶邻接。area_holes/fill_up 所需背景作用域在同一受控 worker 设 `tsp_neighborhood`，调用后恢复前景值；Boundary/contlength 按前景邻接。直接把区域对象数量当拓扑组件数错误，先 connection；孔洞计量需 bbox 周围至少一层真实支持且该层位于W内已知背景，能够确认组件闭合。触 U、缺 tile/未闭接缝、D 裁边或工作域边界时分别 TouchesUnknown/Incomplete/TouchesDomainBoundary，禁止定义“一个完整物体”。

合成一行 F,U,F 的两个已知片段不能证明有两个物体；在 D 内观测到的片段面积/bbox可返回，但全局 ComponentCount=null，未闭组件 ComponentKey=null，拓扑/边界/孔洞等依赖完整形状的特征 InsufficientSupport。任一组件 Topology 不为 Complete 时 ComponentCompleteness=Partial、终态 CompletedPartial；即使 F/B/U 已全分类也不报告全局物体数。只有完整组件集合可给 ComponentCount（含过滤前所有组件），筛选不改变它。拓扑状态优先级 Incomplete→TouchesUnknown→TouchesDomainBoundary→Complete，保存具体缺口原因；不能称 D 裁边已闭合。ClassificationScope 可以 Complete 而对象因 D 裁边仍不完整，二者不能共用一个 complete bool。只有完整组件给确定性 key：按域标签seg-component-v2写InputHash、ComputeSemanticHash(Method,Processing)、FeatureStageId、ParentGridRevision及minRow/minColumn的SHA256（编码规则复用附录A；ComputeSemanticHash内部采用参数编码但省略Processing.Tiles与Processing.Revision，保留实际算法字段，确保仅分区/排列改变不换key）；FragmentKey按seg-fragment-v2域标签写ticket的三字段、FeatureStageId、该未闭片段canonical runs的SHA256，仅诊断，不能作为物理目标 ID。

### 7.2 类型化筛选和统计

FeatureFilter 在全局合并后逐组件计算。All/Any 按三值逻辑：All 有任一已知 false 即 Excluded，全 true Accepted，否则 Unknown；Any 任一已知 true Accepted，全 false Excluded，否则 Unknown；空 All 是不筛选。缺 Scale/预算/数值失败不会成为 false/0，FilterReasons 包含对应 feature status 的 SEG-019，不隐藏无法评价项。筛选仅形成组件的 Filter 状态，不改原 F/B/U；全部 Excluded 也不能报 ForegroundEmpty=true。

区域集合交并、数值聚合和宿主布尔判定各自独立，模块不新增质量 AND/OR 决策树。完整不重叠组件面积 12/8 pixel² 时最大单块 12、总和 20、count 2；有重叠 Region 必须 union1 去重后面积才能称集合总面积。成组宽/高/位置/极值须同 ComponentKey，禁止宽来自 A、高来自 B。范围不完整时不提供全集统计；UI 只统计当前页须明确“当前页”，不能当总数。长组件无法在 native 预算/坐标内重建时，像素面积/bbox继续合法，其它 feature 明确 BudgetExceeded/NotApplicable；不得把 tile 周长/孔洞相加当最终特征。

## 8. 无 UI 入口、状态与事件

### 8.1 唯一服务入口

`SegmentationService` 构造只接收 IImagePlaneSource、ISegmentationBackend、IWorkingSetSource、TimeProvider、RuntimeLimits 和可选 IProgress<SegmentationEvent>；不会读配置文件/环境变量或打开隐藏窗口。端口的精确字段/方法见附录 A。

```csharp
public interface ISegmentationService {
    ValidationResult Validate(SegmentationRequest request);
    ValueTask<StartReceipt> StartAsync(
        SegmentationRequest request, CancellationToken executionToken);
    SegmentationResult Execute(
        SegmentationRequest request, CancellationToken executionToken);
    ValueTask<SegmentationResult> ExecuteAsync(
        SegmentationRequest request, CancellationToken executionToken);
    OperationSnapshot Query(OperationTicket ticket);
    ValueTask<OperationSnapshot> RecoverAsync(
        OperationTicket ticket, TimeSpan budget, CancellationToken cleanupToken);
    ValueTask<OperationSnapshot> WaitAsync(
        OperationTicket ticket, TimeSpan waitBudget, CancellationToken waitToken);
    ValueTask<DrainReport> DrainAsync(
        TimeSpan waitBudget, CancellationToken waitToken);
    ValueTask<DrainReport> CloseAsync(
        TimeSpan waitBudget, CancellationToken waitToken);
    ValueTask<SuggestionResult> SuggestParametersAsync(
        SuggestionRequest request, CancellationToken cancellationToken);
}
```

Validate 是纯值校验，不分配像素/native、不取得输入 lease。StartAsync 经过校验/有限容量预留后返回 Accepted 的 ticket 或未接纳回执；executionToken 是整个 operation 的取消请求。Execute/ExecuteAsync 内部走同一个 Start/终态等待入口，不重新算；仅对本次新接纳的 operation 在真实排空/确认执行资源归还后返回终态结果，native 未返回时 Task 保持未完成。UI/有 deadline 的宿主必须用 Start→Wait/Query，不能在 UI 上同步 Execute。Wait 的 token 仅停止等待，返回/查询当前 snapshot，不取消 execution、不释放任何租约；waitBudget 到期返回非终态 snapshot。token 已取消则 Wait 抛 OperationCanceledException，operation 可继续 Query；计算域错误使用 ModuleError，不抛裸 native 异常。

同一实例同一OperationId只接纳一次：完全相同RequestRevision/完整RequestHash也返回 SEG-014 DuplicateOperation 和原 ticket，不再次执行；内容不同返回SEG-002且Stage=Identity（请求/版本校验的SEG-002使用其实际阶段，不能误作重复身份冲突）。重试必须新 OperationId；CancellationToken 不参与参数 hash。InstanceId 隔离升级前后实例，旧 ticket 不得解析到新实例；参数 A→B→A 的视图必须仍使用不同 RequestRevision。Query未登记或已正常释放且超过冻结详细墓碑保留期的ticket 返回 State=Unknown、IsTerminal=false、PendingReason=None、LastSequence=0、Result=null、SEG-016；Unknown 仅是查询哨兵，不是 operation 状态/终态，不自动重算。比较重复内容必须用完整 RequestHash，不能只比 ParameterHash。Execute/ExecuteAsync 未接纳且无待确认资源时立即返回DiagnosticOnly/Rejected/Data=null的调用回执（Summary 两种 Completeness=NotEvaluated、Count/Empty=null），错误按 StartReceipt，Ticket 为原 ticket 或本次请求键；不等待重复 operation、不再领取它的 Data、不改原状态。若未接纳但有ReleasePending登记，Execute仍须等待原清理确认后返回，受限宿主用Start/Wait可提前得到pending，不能把资源悬挂藏在Rejected中。重复调用方用Query观察原结果；结果 lease 仍只归最初消费 Owner。

**有限观察与在途I/O。** Wait/Recover/Drain/Close的每次budget为1ms..24h，Query只取内存快照、不等待source/backend/ledger I/O；ReleaseAsync同样受每次独立cleanup budget约束。Start的准入等待由本请求Limits.Timeout限定，接纳前先保存请求键和原Owner登记，再启动ReserveAsync。所有在途Reserve/OpenTile/释放/转交任务都先在服务/原Owner登记再await，超时或等待取消不能移除task/Owner或假退款。Start等待到期/执行token在预留期间取消时停止本请求接纳，返回Accepted=false、非空原ticket和非终态snapshot；未返回I/O为DrainPending，返回后只做清理不再启动算法；资源已取得但归还未确认为ReleasePending。原任务真实返回且清理确认后，才发该登记的Rejected终态（保留SEG-007/008/009及来源原因）。没有在途任务/资源才允许Ticket=null即时拒绝；不能把I/O仍执行的拒绝伪装成无责任回执。端口throw前若可能取得资源也须已有可追踪登记。

Recover/Release/Close预算只限制本次观察；已启动清理由原Owner继续登记至真实回执。等待到期返回当前snapshot/Pending/Waiting，不强制Dispose仍在使用的对象。Query异常或Unknown仅说明结果知识未知；Close已确认Drained与结果lease归还仍分别判定。宿主异常走§12的finally，不改写已有算法终态。内部I/O不遵守token仍保留task/Owner并报告DrainPending，不用外层取消等待冒充排空。

### 8.2 状态、关闭与非终态诊断

核心冻结 CompletedPartial 为模块终态，平台怎样映射仍由宿主决定。状态主链：

`Created → Validating → [Rejected | Accepted → Queued → Acquiring → Segmenting → Morphology? → Connecting → FeatureExtraction → Draining → Drained → ResourcesReleased → unique terminal]`

| 终态 | 结果资格 |
|---|---|
| Completed | D 为空：Summary.ClassificationScope=Empty；否则分类/组件全集完整，个别特征资格单独报告；通常 Use=AlgorithmFacts，Shadow/Advice 强制 DiagnosticOnly，仍不代表材料/质量结论 |
| CompletedPartial | 部分 D 未分类或组件集合不完整；Summary.ClassificationScope 或 ComponentCompleteness=Partial；Use=DiagnosticOnly，不提供确定全局计数 |
| Rejected | 请求/能力/容量接纳失败，无可消费算法数据；Use=DiagnosticOnly；接纳后发生来源/版本错误也先清理再返回 |
| NotQualified | 方法用途/支撑/分类资格未满足；可保留原始诊断域，不填空前景成功 |
| RecoverableError | 临时输入/后端故障；新 OperationId 才能重试；保留原错误 |
| Cancelled / TimedOut | 已停止派发、native 真返回且资源已确认归还；输出仅诊断，不返回可消费部分结果 |
| Failed | 非法后端输出、不可恢复数值/内部错误；保留错误码、阶段、来源 |

DeadlineExceeded 是立即可查询的诊断，不是 TimedOut 终态；DrainPending表示native/worker或已登记source/预留/释放I/O尚未真实返回，ReleasePending 表示已 Drained 但执行资源归还未确认。两者放在 OperationSnapshot.PendingReason 中，**不是额外 ExecutionState 终态**。资源未确认时不得重用 adapter、自动重启实例或删除记录；原 Owner 的恢复完成后才能继续唯一终态。

DrainAsync只等待调用开始时已登记工作的排空，不关闭接纳、不主动取消；CloseAsync 原子关闭接纳、取消 queued/active operation、关闭建议任务，随后bounded wait 并返回 DrainReport。重复 Close 幂等；Closed 实例不能 reopen，新配置用新实例。报告Waiting/ReleasePending时保留实例/资源账，宿主有限Query；仅ReleasePending沿原ticket Recover，然后有限Close复核，不能把重复Close当已执行恢复；不以 Dispose 成功代替排空。Core 自有定时器/有界队列在全部操作终态后停止，输入 source/backend/资源端口由宿主拥有，不能顺手 Dispose 宿主共享对象。结果 lease 是已转交的消费者资源：Close 不抢夺正在读的 lease，只报告 outstandingResultLeases；调用方释放后资源 Owner 才完成其计费寿命。

已接纳operation的终态按固定优先级选择：非法后端输出/不可恢复内部错误→Failed；已观测执行deadline→TimedOut；随后用户取消→Cancelled；接纳后版本/能力错误→Rejected；已知临时来源/转交/后端IO失败且无可消费完整结果→RecoverableError；方法门失败或D非空而有效分类像素为0→NotQualified；可校验输出有U或组件全集不完整/预算截断→CompletedPartial；其余Completed。未接纳请求的在途I/O/预留清理完成后为Rejected，保留其取消/期限错误，不套已接纳的Cancelled/TimedOut优先级。只缺某项feature资格但组件全集完整不改变Completed，FeatureStatus/Filter独立报告。没有有效Data的Rejected/Failed/Cancelled/TimedOut均Data=null，其他诊断仅在实际存在合法已知域且成功转交时才有Data。D空纯Validate通过后绕过backend.Plan/Execute/源，给Empty；无native不捏造资源指标。executionToken进入Start前已取消且无在途I/O/资源则返回未接纳SEG-008，不注册计算；预留期间取消按§8.1保留原ticket。Deadline与Cancel并发按上述冻结优先级，不能由callback到达顺序决定。

### 8.3 事件与结果发布

`SegmentationEvent` 包含 ticket、Sequence:long（每个已登记 ticket 从 1 递增）、Utc:DateTimeOffset、Elapsed:TimeSpan、Kind、StageId?、CompletedUnits/TotalUnits:long?、PendingReason?、Error?。Kind 限定为 RequestReceived、ValidationStarted、ValidationCompleted、RequestAccepted、ResourceAcquired、StageStarted、Progress、StageCompleted、QualityEvaluated、ResultAvailable、CancelRequested、DeadlineExceeded、DrainStarted、Drained、ReleasePending、ResourcesReleased、Terminal。只有 Terminal 带终态且发一次。

新请求键在容量允许建立小型登记时，未接纳路径为 RequestReceived→ValidationStarted→ValidationCompleted→Terminal(Rejected)，没有 RequestAccepted/native 阶段。重复/冲突、关闭实例和无登记容量的请求只返回 StartReceipt.Errors，不写原 ticket 事件、不发送第二个 Terminal；未分配 ticket 时没有事件。通过预留才 RequestAccepted；若预留拒绝但有在途I/O/待释放reservation，StartReceipt须携原ticket和非终态snapshot；先真实排空、释放确认再Terminal(Rejected)，接纳前也不能伪终态。接纳后输出候选 ResultAvailable 仅表示诊断可见，不能消费终态/改质量；投影租约未成功转交前不暴露结果数据。

正常/失败/取消都先 DrainStarted→Drained→ResourcesReleased→Terminal；ResourcesReleased 表示执行 lease/native/临时状态都已归还，输出 lease 已按 §10.1 转交，宿主池的物理占用仍由登记 Owner 计费。未确认释放时 Drained→ReleasePending（可多次诊断），无 ResourcesReleased/Terminal。纯值 Core 不存在 native 调用时 Drained 只表示其有限 worker 停止，不捏造 native 成绩。

事件由单个实例序列器排序，但Sequence是每ticket的严格递增序号（Progress合并可留序号缺口），OperationSnapshot.LastSequence 同一口径；Progress 可按冻结间隔合并，权威生命周期/唯一终态先写OperationSnapshot；外部通知使用单个有界callback worker，不能在native scope内同步调用订阅者或用无界 Task.Run。生命周期先记录再回调，队列拥堵丢/合并Progress；无法及时投递时禁用该sink并记录SEG-020 CallbackFailure，已记录Terminal仍可Query，不能等待阻塞订阅者来结束Drain/Release；后台回调不携Data/像素/handle，不无限Task.Run。订阅异常记录CallbackFailure，不能改变算法状态/阻止释放；最新权威 snapshot 可 Query，即使 UI 丢弃旧事件仍须让原 operation 释放资源。提交事实/权限事件不属于本模块。

## 9. 错误码语义与恢复

错误码为稳定字符串，消息由宿主本地化；错误对象至少含 `Code`、`Stage`、`Recoverability`、`Cause`、`EvidenceRef`。

| 错误码 | 语义 | 恢复 |
|---|---|---|
| `SEG-001 InvalidRequest` | 必填项、域关系、数值或枚举非法 | 修正请求后新 operation |
| `SEG-002 VersionMismatch` | 图像/方法/参数/坐标版本不一致 | 重新绑定兼容快照 |
| `SEG-003 UnsupportedMethod` | 方法未登记或 adapter 不支持 | 选择已批准路线；不得自动降级 |
| `SEG-004 InvalidDomain` | D/I 越界、重叠或坐标不一致 | 调用方修正域 |
| `SEG-005 InsufficientSupport` | 图像、参考、halo 或有效域不足 | 提供支持或接受 NotQualified |
| `SEG-006 BackendFailure` | AsunImage/HALCON 返回异常 | 释放资源，按幂等规则重试 |
| `SEG-007 BudgetExceeded` | 像素、组件、内存或时间预算耗尽 | 调用方处理不完整结果；不得当空结果 |
| `SEG-008 Cancelled` | 调用方取消且 native 已排空 | 仅返回取消回执 |
| `SEG-009 TimedOut` | 期限耗尽，native 可能仍在排空 | 查询 DeadlineExceeded；等待 `DrainAsync`，不得重用资源 |
| `SEG-010 NumericError` | NaN/Inf、溢出或不支持位深 | 标记受影响域为 Unknown 或失败 |
| `SEG-011 ResourceLeakDetected` | 租约/对象未确认归还或释放失败 | 保留原 Owner/句柄及额度；非终态 ReleasePending；确认归还前隔离实例并阻断发布 |
| `SEG-012 StaleResult` | 结果或事件 revision 已过期 | 丢弃投影，不改变当前事实 |
| `SEG-013 PartialOutput` | 部分 tile/阶段完成，仍有未知域 | 仅可用于诊断/预览；补齐缺口后以新 operation 重算 |
| `SEG-014 DuplicateOperation` | 同 ID/同内容再次启动 | 返回原 ticket，仅 Query 不重算 |
| `SEG-015 ServiceClosed` | 实例已关闭接纳 | 等原实例资源闭合后创建显式新实例 |
| `SEG-016 UnknownOperation` | ticket 属其它实例/已过正常墓碑期限 | 不自动重算；宿主查自己保存的回执 |
| `SEG-017 InvalidBackendOutput` | backend 域/计数/特征/身份矛盾 | 隔离该后端并保留资源，修复后新 operation |
| `SEG-018 SourceUnavailable` | 来源断连/租约中断且所需输入无法取得 | 未处理域置 MissingImage；新快照才重试 |
| `SEG-019 FeatureUnavailable` | 特征/筛选缺值或失去支撑 | 保留FeatureStatus/Filter=Unknown，不当正常排除 |
| `SEG-020 CallbackFailure` | 订阅异常/通知积压；权威snapshot保留 | 禁用受影响sink，不改计算状态/阻止释放；宿主Query |

计算重试必须新 OperationId/ticket；CalculationIdentity 是 §A.1 的 ticket+RequestHash+AlgorithmRevision 组合，不另定义平台提交身份。资源恢复沿原ticket/Owner，不重算；Accepted=false但有pending ticket仍沿同ticket处理。Host消费/读取异常与资源观察错误独立保存，不改写已有算法结果；模块没有CommitIdentity或提交重试。

## 10. 取消、超时、排空、线程与资源

1. 取消请求后停止派发新 tile，在每个 stage 边界检查 token；正在运行的 HALCON 调用必须由 adapter 等待真实返回。
2. 调用预算到期先通知宿主并进入 `Draining`，不构成 `TimedOut` operation 终态；后台 worker 仍持有资源租约，直到 native 调用结束并发送 `ResourcesReleased`，随后才可发送最终 `TimedOut`。
3. `DrainAsync` 等待调用开始时已登记 operations 的 native 调用、队列、内部事件发布和执行租约结束（不包含已转交的消费者结果 lease）；调用自身可用独立 drain timeout/token。drain timeout 返回排空未完成诊断，不释放仍在使用的对象。
4. 每个 operation 使用独立的 `OperationScope`、临时图、Region、标签和并查集；禁止可变静态缓存、跨请求借用和隐式单例 handle。
5. 视觉后端 worker 数量由 `MaxParallelTiles` 和资源 Profile 限定；HALCON 线程局部设置在同一 worker 内保存、设置、调用、恢复，期间不得跨 `await` 或重入其它参数。
6. 所有成功、取消、超时和异常路径都执行 finally 释放；输入借用由 OpenTile 的调用方经 `IImageLease.ReleaseAsync` 归还，底层物理存储仍归 source Owner，结果引用不得在释放后悬挂。
7. 背压使用有界队列；队列满接纳前返回 `Rejected/SEG-007`，不能无限排队；排队等待计入本次 Timeout。

8. 通过纯 Validate 后、`RequestAccepted` 前，宿主/adapter 必须为准确的 OperationId、输入快照、方法/参数修订和并发 Profile 提供有限工作集预留；所有受控副本、clone、`ToArray`、临时 Region/标签、scratch 和 native dispatch 都须在实际分配/派发前获得其额度。证据字节上限不能代替完整工作集预算；原图借用与私有工作分配分别归原 Owner，模块不能另建平台总账。native baseline/峰值来源未明确时只拒绝受影响路线的准入，不猜零或经验容量。
9. 若算法保留 tile A 才能等待 tile B/参考输入，必须在持有 A 前预留 B、halo、scratch 和不可中断阶段所需的最小依赖工作集；不足则接纳前以 `SEG-007` 拒绝，或由宿主重新提供已批准计划，不能占住 A 永久等待、丢 A 或隐式补输入。每阶段使用同一预留，不按 tile 重置。
10. 池化数组和 native cache 在真实存活期持续计费；Scope 归还不等于物理释放，暖池复用同一已计费槽不重复扣费。仅允许宿主批准、容量有界、非静态的运行期 Owner 持有池/缓存；operation 结束要确认其借用归还，物理额度仍由该 Owner 保留至真实释放。不得借“移交给池”隐藏释放异常或未知所有权。
11. finally 发起释放但不证明成功。callback 异常、释放确认失败或未知时，保留原句柄/parent、Owner、OperationId、未确认项和额度，报告 `SEG-011` 与非终态 `ReleasePending`；第二次 no-op Dispose 不得证明成功、删除登记或退款。原 Owner 以有界、可追踪的恢复操作确认释放后，才可归还相应额度并完成 §8 的事件顺序；同一已释放对象不得重复归还。
12. 清理使用独立、有限的 cleanup budget/token，不复用已取消的执行 token；它仅授权资源清理，不授权继续计算。只有相关 native 调用及其它借用者真实排空后才能清理保留对象；cleanup 到期/失败保持 `ReleasePending` 和隔离，native 未返回仍为 `DrainPending`，两者均不提前发送终态或 `ResourcesReleased`。


### 10.1 执行资源、结果转交与恢复

执行 scope 先涵盖输入 borrow 登记、native/托管 scratch、最坏 runs/组件及结果投影；同一 allocation 只扣一次。backend 输出托管值仍计在 scope，Core 校验后向 working-set source 的已确认结果 Owner TransferResultAsync；成功后Core激活同一preparedResult，OwnerId一次绑定TransferReceipt.ResultOwnerId，归消费者，scope 可释放其它资源。TransferResultAsync传入Core已构造的preparedResult（尚不可读/IsReleased=false），其Bytes是scope内全部ResultProjection allocation的checked总和（包括 stages/组件/边界和冻结对象开销），须≤Plan.RequiredResultBytes≤MaxResultBytes，执行期间各 private allocations 合计≤RequiredBytes。只转 ResultProjection 的账项，source/scratch 不随它转交；结果释放只退该 Owner 的账。已知转交失败不发布Data，清理本次投影并返回RecoverableError/SEG-011；未知转交保持ReleasePending，同ticket/leaseId沿原scope重查确认，确认转交后若原operation拟失败则用ReleaseResultAsync归还已转交账，再丢像素；未知不得假清理/退款。保存小型 Summary/Provenance/终态墓碑不持 pixel/native 对象，容量由 RuntimeLimits 限定。

RecoverAsync 仅对 PendingReason=ReleasePending 的原 ticket 做释放重试；其他已知 ticket 原样返回、未知按 Query 哨兵返回。对 ReleasePending：先确认原backend/native及全部相关I/O已返回；确曾派发backend才调用backend.RecoverAsync，预留阶段未派发则backend.Execute/Recover次数均为0。按原登记归还输入source lease，再继续原scope.ReleaseAsync；不为恢复创建新scope；cleanup token/budget 只约束本次恢复等待。backend/资源 Owner 不同内容回执或未知均不确认，SEG-011 保留原实例。DrainPending的Recover只返回原snapshot，不关闭活跃native或I/O；须等真实返回，原reservation晚返后只清理不派发计算。同ticket计算完成、恢复与查询用同一状态锁；并发Recover合并为一个清理任务，其他调用有界等待原snapshot，cleanup token只影响各自等待，不中止已启动Owner清理。恢复多次不重复计费/退款/Terminal，原算法拟终态保存且不被恢复“成功”改为 Completed。

result lease的ReleaseAsync先结束其读借用，调用workingSetSource.ReleaseResultAsync取得匹配Owner/lease/ticket的确认，才清空大数据引用并置IsReleased=true；失败保留原 lease、只读数据与 Owner，宿主继续该 lease.ReleaseAsync，不能用服务新 operation 代替。MaxRetainedResults 满时拒绝新接纳，不偷释放旧结果；结果引用不在正常墓碑 TTL 内被驱逐。源断连时已有合法只读借用若仍有效可完成，否则未处理域标 U/SEG-018；模块不 reconnect 摄像头、不取另一帧顶替。native 性能 Unknown 或 release Unknown 都阻断对应性能/发布门，不能推断零。

## 11. 适配器、版本和迁移

### 11.1 适配器职责

`Segmentation.AsunImageAdapter` 将模块值对象转换为 `ImageLibDotNet.HImage/HRegion`，负责：输入复制/借用策略、HALCON 26.05 operator 调用、线程设置作用域、异常映射、native 释放和结果投影。核心层只能看到 `ISegmentationBackend`。

适配器不得把旧项目的静态 helper、UI 控件、`HObject` 或私有坐标表带入核心。若某个公开签名无法满足三态/支撑/取消语义，应返回 `UnsupportedMethod` 或 `NotQualified`，不能在 adapter 内偷偷改语义。

### 11.2 兼容策略

模块版本采用 `Major.Minor.Patch`：

- `Patch`：不改变语义、单位、默认值和错误码的修复。
- `Minor`：新增可选 feature/事件/adapter；旧请求和旧结果必须可读。
- `Major`：单位、三态、连通、结果来源、错误语义或资源生命周期改变。

模块结果必须带 `Provenance.ContractVersion`、`Provenance.AlgorithmRevision`、`Provenance.ParameterRevision`/`Provenance.ParameterHash`、`Provenance.HalconRuntimeVersion`、`Provenance.AdapterVersion`。如何序列化、持久化和迁移由宿主的 Contract/Schema Owner 决定；若宿主读取旧快照，须使用显式 migrator，无法证明等价就返回版本不兼容，不猜测转换。模块不提供存储接口、不创建持久化回执。

HALCON 26.05 是本模块当前基线。升级 HALCON、AsunImage 或 adapter 时，按受影响调用核对目标版本行为；C# 类型/重载/封送发生变化或存在歧义时才核对公共签名，并执行相关 Golden/Replay、线程/释放、性能和两消费者接入验证；未完成前保持旧 adapter 可回退。

### 11.3 SG-A1 的公开装配与资源模型

唯一可构造后端为 `Asun.Modules.Segmentation.AsunImage.AsunImageSegmentationBackend`，public sealed class 实现附录 A 的 `ISegmentationBackend`；公开构造 `(BackendProfile profile, NativeFootprintProfile footprint, TimeProvider time)`，另公开 `ValueTask<ReleaseReceipt> CloseAsync(TimeSpan budget, CancellationToken cleanupToken)`。构造只冻结/校验值，不开线程、图像或 native 对象。Owner在Factory/构造之前登记一份有界根槽，保存 profile/footprint/time 和原source/workingSets；构造返回后先把 backend 强引用加入原槽，再构造 Core 服务。Dispose不另设捷径；先服务Close并处置结果lease，再backend.Close，未确认时继续原槽和原ticket Recover，不创建第二后端顶替。

`NativeFootprintProfile`/`NativeFootprintRule`为adapter namespace下public sealed record；`NativeFootprintProfile` 的公开字段固定为 `(Revision:string, Sha256:string, BackendProfileHash:string, Rules:ImmutableArray<NativeFootprintRule>)`；`NativeFootprintRule(Method:SegmentationMethod, Encoding:PixelEncoding, BaseBytes:long, BytesPerInputPixel:long, BytesPerRun:long, BytesPerComponent:long, BytesPerEquivalence:long, ResultBaseBytes:long, ResultBytesPerRun:long, ResultBytesPerComponent:long, MaxLiveInputSlots:int)`。每个支持的Method/Encoding恰一rule，系数非负、BaseBytes与ResultBaseBytes正、输入slots=0..128、相同profile绑定；规则缺失/不完整拒绝受影响组合SEG-003，未测native上界不填0。这些是资源上界模型，不是准确率/速度资格或新视觉方法。

Plan令T为同时读取的core+累计halo矩形像素总上界（含并发worker及独立参考），G为全局组件重建/灰度特征需要的完整父图矩形像素上界，P=checked(T+G)，S为raw及全部形态阶段数，R为全部存活阶段/结构元/边界canonical runs的累计上界，C为同时存活组件记录数上界，E为跨缝等价对上界。G单独受MaxReconstructionPixels约束，重建runs受MaxReconstructionRuns约束；不能只用局部tile面积估全局feature。R/C/E按请求上限及几何最坏值取较小已证明上界；不能证明比上限小就取请求上限。ResultBytes=ResultBaseBytes+ResultBytesPerRun×R+ResultBytesPerComponent×C；WorkingBytes=ResultBytes+BaseBytes+BytesPerInputPixel×P×S+BytesPerRun×R+BytesPerComponent×C+BytesPerEquivalence×E，checked并与Limits核对。每条rule必须上界覆盖该Method/Encoding全部合法FeatureSet及形态核组合的私有灰度副本、native Region/轮廓、标签、重建及重标记表、特征值槽/数组头和托管投影；无法证明阶段可先释放则计同时存活，不以最终输出字节代替峰值。源/池既有物理allocation不重复扣费；输入私有copy及native对象包含在该rule，不把源borrow footprint当private退款。缺rule、溢出、超重建或tile坐标能力分别按附录A/§6拒绝，不让开发者临时选另一算法。

实现顺序唯一复用§6.5/6.6与§7：source取得精确只读矩形→有界私有输入→cv2已选方法→形态及支撑→局部connection→全局接缝合并→完整Region/native特征→托管投影→归还输入/native→Core校验/筛选/lease。并发worker在首次Execute后按请求有限名额建立，线程设置scope不跨await，异常也恢复。native实际调用的C#重载只在消费程序集编译时核歧义；公开后端/装配/Plan/Owner已明确，SG-A1的剩余真实native footprint系数与编译/运行证据不能冒充内部构造欠账。

### 11.4 SG-A1 图像/RLE转换、执行器与具体native接线

本节补齐§11.3公开后端背后的实施步骤，不新增视觉方法、请求字段或第二个Core算法。以下算子序列是HALCON语义调用形状，不冒称已经编译的ImageLibDotNet重载；C#只在消费程序集按公共签名落实out/tuple/pointer类型，不查看封装内部。全部通过cv2。

1. **输入与布局。** 单次OpenTile请求是core加完整累计halo与父图矩形的交集；W的稀疏洞仍保留，不据其bbox补真值。核SnapshotId/Revision/hash、ReadRequest、格、编码、Valid和Missing；每tile记原OpenTile Task后再await，lease先入scope登记。Byte/UInt16/Real32分别用1/2/4 bytes，little-endian，rowBytes=checked(width*bpp)，最后可访问byte=checked((height−1)*stride+rowBytes)，拒绝截断/短行/越界。复制每行rowBytes到本方已预留的tight缓冲，padding不复制/不hash为像素；源原byte/stride不改。所有用于计算的Real32必须finite，超声明灰度范围或NaN/Inf像素加NumericError未知patch；不能当0背景。对仅为native矩形计算准备的私有无效格可填0，但其窗口依赖中心已从V_j排除，填充值永不成为统计/分类或灰度证据。
2. **创建图像。** 在同一受控worker pin tight缓冲，用`gen_image1(Type,Width,Height,PixelPointer)`，Type精确byte/uint2/real；指针为实际64位地址，size在pin前校验。官方算子创建自己的像素存储，故真实调用返回后才unpin/归还私有copy；调用未返回绝不unpin。禁用外借指针的gen_image1_extern。native image及其domain变体各自登记，并在最后使用者退出后Dispose/确认。`reduce_domain`只缩定义域、不缩矩阵；不能用它假称已省整幅输入内存。
3. **RLE转换。** 所有本地Region坐标=父坐标−该矩形原点，checked转native可表示范围；ExplicitKernel保有符号原点偏移，不加tile原点。`gen_region_runs(Row,ColumnBegin,ColumnEnd)`三tuple长度一致、canonical、inclusive，合法空集使用`gen_empty_region`，不是空object tuple。`get_region_runs`逐个单Region读取三tuple，先核同长度/累计上限/顺序/范围，再投影为PixelRun并checked加父偏移；native已保证的升序仍验证，异常输出不偷偷修复。只对经显式union1合并后的集合合并相邻run；请求非法RLE仍由Core拒绝。所有tuple/Region和托管数组分别先计费再分配，导出完成不证明native已归还。
4. **固定/全局。** Fixed每闭区间threshold后union1，最后交V0；Global取得StatisticsDomain的完整bbox矩形与原有效统计域，用gen_region_runs→reduce_domain→一次binary_threshold(Method,LightDark,out T)，其中Method仅max_separability/smooth_histo，LightDark精确light/dark。完整统计像素中间不可缺测；bbox/tight/native预算含稀疏域外矩阵且须受重建能力约束，超限SEG-007。随后每core按同T及§6.6端点threshold，不再binary_threshold。保留原统计T/N/域回执，统计buffer归还确认后才进入后续需要额度的stage。
5. **动态/局部。** Dynamic.Reference非空时取得同一矩形的独立参考lease，两输入slots一起预留；MeanWindow非空时仅原图mean_image(width,height)生成背景，二者不混用。dyn_threshold的LightDark按light/dark/equal/not_equal与冻结Offset，严格谓词沿§6.6。Sauvola直接`local_threshold(Image,'adapted_std_deviation',LightDark,['mask_size','scale','range'],[WindowSize,Scale,Range])`；light直接交算子，不求dark补集；实际传值及参数顺序不从native默认补。窗口无效/真实边界按V_j置U，算子镜像值不充观测。
6. **mask与形态。** RegisteredMask先交初始V0并保原U原因；不含GrayMean/Min/Max时不OpenTile或构造无用image。核Rectangle用gen_rectangle1(−h/2,−w/2,h/2,w/2)，h/w为奇数且除法为整数；Circle用gen_circle(0,0,Radius)，Explicit用本地gen_region_runs。核构造后get_region_runs复核中心/对称/实支持；WholeForegroundSet先union1，PerInputObject逐原Object处理。每步Opening/Closing调用对应opening/closing一次并重复Iterations次；Erosion/Dilation调用erosion1/dilation1且显式Iterations。支撑Region每个原子依赖用erosion1(前级V,同核,1)递推，Opening/Closing每迭代两次；每级结果与其V_j相交，B_j=V_j−F_j，U_j=D−V_j，新增支撑缺口加InsufficientHalo。以当前阶段序列构造确定性SourceRevision（域标签seg-stage-source-v1后依次写AlgorithmRevision、StageId，沿A.1字符串长度编码取SHA-256），不抹掉原UnknownPatches。最后投影D，不能提前裁D。
7. **连接与特征。** core connection→单对象导出→接缝归并严格沿§6.6；本地结果按TileCore顺序封存，native完成顺序不决定预算接受/稳定key。聚合使用一位协调器和有界归并表；每条等价边只登记一次，集合/矩/边界内存计同scope。全局完整组件在本地bbox原点重建Region，尺寸/坐标/MaxReconstructionPixels/Runs逐项核；按组件key串行重建，最大一个重建组件加当前tile峰值一起Plan。Perimeter/Boundary/Circularity/HoleArea用contlength/boundary('inner')/circularity/area_holes，孔洞临时切对偶邻接。GrayMean用intensity的Mean，GrayMin/Max用min_max_gray的Percent=0，不能用裁剪百分位替代极值；读取同输入快照的完整组件bbox并交该组件，支持不足InsufficientSupport。纯AreaPixels/Centroid/BoundingBox/AreaPhysical无需native重建/灰度源；只缺native重建能力时上述像素特征继续有效，依赖特征BudgetExceeded/NotApplicable，不使整个分割拒绝。
8. **工作线程与关闭。** 每后端一个有界协调器、最多MaxParallelTiles个专用native worker；首次Execute后才创建。每个native工作单元在同线程同步完成get_system原tsp_neighborhood/tsp_clip_region→设置→调用→finally恢复，不跨await、不改全局max_connection；源/账异步等待在native作用域外。每个ticket独立登记scope、原Task、输入lease、native对象与账token，失败/取消也回同一恢复表。backend.Close原子封新Execute/Plan接纳，取消排队单元、等待真实worker与恢复；Released仅所有原任务退出、输入/native清理确认且本方worker停止，ResourceId为该后端实例关闭键，OwnerId为同原根Owner。已转交的托管结果仍归Core/消费者，不抢lease；预算到期返回Pending/Failed并保留原对象/Task，重复Close沿同关闭记录。Recover只清理原ticket，原worker尚未返不能Dispose它的image，停止不使用Thread.Abort/强杀native。

**预算细化。** §11.3的T包含当前/参考/统计矩形的同时读取上界，G按所选FeatureSet的实际重建需求取得；像素特征-only或空组件G=0，不让native bbox限制阻断纯像素分析。native特征允许的G取Profile有限重建上界，Gray特征额外source slot和tight/private image同时纳入；超限组件在执行中按上项返回特征不可用。R含F/B/U及重叠原因patch、全部存活阶段/核/边界，C含所有合法feature槽；形态最多16×64及有限输入Object数的最坏native中间量也必须由rule覆盖。输入Objects/runs、tile元数据、UnknownPatches、kernel累计runs、队列/ticket和scores元数据按checked大小在复制前校验；无能力证明的rule拒绝受影响Method/Encoding，不能把MaxResultBytes当scratch上界。NativeFootprintProfile.Sha256为域标签`seg-native-footprint-v1`后按§11.3字段顺序编码Revision/BackendProfileHash/按Method、Encoding排序的Rules（不含Sha256自身；编码沿A.1），构造复算。rule上界由未来Adapter实现Owner按目标负载实测并核上界提供，不是客户阈值，不以“待客户”转交本方职责；未实测数据不填0、不宣称准确峰值。

## 12. 最小 Host 与无 UI 调用

Core.Tests 的 `Fixtures/ConsoleHost` 和 `Fixtures/SurfaceToolHost` 是两个不同组合根，均只引用 Core 和 BCL；前者给固定闭区间的原始灰度快照，后者给已登记通道/外部 mask 与自有 Profile。测试后端按冻结 fixture 返回三态/组件，不把模拟通过当视觉正确性。真实 adapter Host 使用同一端口替换 backend/source，仍不加载 WPF/设备/产品数据库。宿主拥有 source/backend/workingSetSource 的运行期，模块不代为 Dispose。

### 12.1 结果知识、调用错误与资源闭合

必须分别保存四项：最后一次 OperationSnapshot、由终态回执确认的 KnownResult（尚未确认则 null）、本次调用/消费异常、I/O/执行/结果资源闭合。ReadComponents 或下游消费失败不撤销已知 Completed/CompletedPartial，不把算法结果改为 Failed；Wait 取消/预算到期只结束观察，不能证明 operation 已取消或释放。Close 报 Drained 仅证明执行资源闭合；尚有结果 lease 时不能称全部 I/O/资源闭合。反之，Close 已确认闭合但结果因查询错误/墓碑到期仍未知，也不能捏造算法终态。

`Accepted=false` 不能直接退出：Ticket=null 表示没有需本次调用继续观察的登记；Ticket非空须检查Snapshot/错误码。新请求的DrainPending/ReleasePending仍由原ticket负责，前者有限Wait/Query，后者同ticket RecoverAsync；只有真实释放后才出现Rejected终态。SEG-014或SEG-002且Stage=Identity的身份冲突给出的原ticket属于既有操作，本次不取得它的Data或清理权，交原调用Owner处理。没有ticket却声称有待释放资源违反StartReceipt契约，不能当拒绝成功。

### 12.2 完整收尾示例

下例是两个最小Host共用的**测试宿主代码形状**，不是新模块公开API。request由宿主显式构造并冻结：3×3 Byte，D=W=全格、无I/U、中心15其它0，FixedIntervals=[10,20]、无形态、Eight、面积/质心/bbox；期望F面积1、B面积8、U空、质心(1,1)。hash直接复用附录A，不增算法或编码。

组合根传入全新、独占的service与runtime.InstanceId、新OperationId及其原source/backend/workingSets。originalOwnerHeld是**原组合根**持有的容量1恢复槽，寿命长于本次调用；进入Start前先登记全部强引用。槽未空时拒绝启动本例的新调用；字典仅归原组合根私有，所有访问在同一lock下，禁止外部移除/替换/清空，只准本例或同Owner恢复路径在确认闭合后移除。消费回调为同步有界动作，不保留page/borrow、不开后台I/O；若实际消费者需要异步I/O，必须在调用前单独登记其有限任务/Owner，未完成也阻断归还并保留原槽，不套用此同步消费例。共享service的控件不得调用本例Close，按§13只等自身ticket并交宿主恢复。

```csharp
// 以下类型/函数仅在Core.Tests的Fixtures宿主中；组合根保存originalOwnerHeld。
sealed record HostHeldCall(
    ISegmentationService Service, IImagePlaneSource Images,
    ISegmentationBackend Backend, IWorkingSetSource WorkingSets,
    CancellationTokenSource Execution, OperationTicket Ticket)
{
    public OperationTicket CurrentTicket { get; set; } = Ticket;
    public bool StartAttempted { get; set; }
    public bool OwnOperation { get; set; } = true; // 全新实例/新ID，重复回执时撤回
    public ValidationResult? Validation { get; set; }
    public StartReceipt? Start { get; set; }
    public OperationSnapshot? LastSnapshot { get; set; }
    public SegmentationResult? KnownResult { get; set; }
    public IResultLease? Data { get; set; }
    public DrainReport? CloseReport { get; set; }
    public Exception? CallError { get; set; }
    public Exception? CleanupError { get; set; } // 仅保留首项，避免无界异常列表
    public bool IoClosed { get; set; }
    public bool OriginalOwnerConfirmed { get; set; }
    public bool RetainedByOwner { get; set; }

    public void Observe(OperationSnapshot snapshot)
    {
        LastSnapshot = snapshot;
        if (!OwnOperation || !snapshot.IsTerminal) return;
        KnownResult ??= snapshot.Result; // 不从阶段/非终态诊断推断结果
        Data ??= snapshot.Result?.Data; // 消费/读取前先保存lease责任
    }
}

static async Task<HostHeldCall> RunHostOnceAsync(
    ISegmentationService service, IImagePlaneSource images,
    ISegmentationBackend backend, IWorkingSetSource workingSets,
    RuntimeLimits runtime, SegmentationRequest request,
    Dictionary<OperationTicket, HostHeldCall> originalOwnerHeld,
    Action<ResultUse, ComponentPage> consume, CancellationToken waitToken)
{
    var key = new OperationTicket(
        runtime.InstanceId, request.OperationId, request.RequestRevision);
    HostHeldCall call;
    lock (originalOwnerHeld) {
        if (originalOwnerHeld.Count != 0)
            throw new InvalidOperationException("原恢复槽尚未闭合");
        call = new(service, images, backend, workingSets,
            new CancellationTokenSource(), key);
        originalOwnerHeld.Add(key, call); // 先登记，后进入任何可取得资源的调用
    }

    var budget = TimeSpan.FromMilliseconds(250); // 示例有限控制，非生产Profile
    try {
        call.Validation = service.Validate(request);
        if (call.Validation.IsValid) {
            call.StartAttempted = true;
            var start = await service.StartAsync(request, call.Execution.Token);
            call.Start = start;
            call.CurrentTicket = start.Ticket ?? key;
            call.OwnOperation = !start.Errors.Any(e =>
                e.Code == "SEG-014" ||
                (e.Code == "SEG-002" && e.Stage == "Identity"));
            if (start.Snapshot is { } initial) call.Observe(initial);

            if (start.Accepted) {
                call.Observe(await service.WaitAsync(
                    call.CurrentTicket, budget, waitToken));
                if (call.KnownResult is { } result && call.Data is { } data) {
                    // 即使读取/consume抛异常，finally仍负责Data与service。
                    var page = data.ReadComponents(0, 128);
                    consume(result.Use, page);
                }
            }
            // Accepted=false仍进入finally；新reservation待释放不能直接return。
        }
    }
    catch (Exception error) { call.CallError = error; }
    finally {
        try {
            try { call.Execution.Cancel(); }
            catch (Exception error) { call.CleanupError ??= error; }

            // 有限两轮；原ticket的资源恢复不发新请求、不重新计算。
            for (var round = 0; round < 2; round++) {
                try {
                    if (call.StartAttempted && call.OwnOperation) {
                        var snapshot = service.Query(call.CurrentTicket);
                        call.Observe(snapshot);
                        if (snapshot.PendingReason == PendingReason.ReleasePending)
                            call.Observe(await service.RecoverAsync(
                                call.CurrentTicket, budget, CancellationToken.None));
                        else if (!snapshot.IsTerminal &&
                                 snapshot.State != ExecutionState.Unknown)
                            call.Observe(await service.WaitAsync(
                                call.CurrentTicket, budget, CancellationToken.None));
                    }
                }
                catch (Exception error) { call.CleanupError ??= error; }
                finally {
                    // Query/Recover/Wait失败也不能跳过已取得Data的归还。
                    try {
                        if (call.Data is { IsReleased: false } data)
                            await data.ReleaseAsync(budget, CancellationToken.None);
                    }
                    catch (Exception error) { call.CleanupError ??= error; }
                }
            }
        }
        finally {
            try {
                // 全新独占实例：无论Validate/Start/消费/释放何处失败都关闭接纳。
                call.CloseReport = await service.CloseAsync(
                    budget, CancellationToken.None);
            }
            catch (Exception error) { call.CleanupError ??= error; }
            finally {
                try {
                    // Close期间可能迟到完成并转交Data；先登记，交原Owner接续归还。
                    if (call.StartAttempted && call.OwnOperation)
                        call.Observe(service.Query(call.CurrentTicket));
                }
                catch (Exception error) { call.CleanupError ??= error; }
                finally {
                    call.IoClosed = call.CloseReport is {
                        Status: DrainStatus.Drained, AdmissionClosed: true,
                        OutstandingResultLeases: 0
                    } && call.CloseReport.Pending.IsEmpty && (call.Data is null || call.Data.IsReleased);
                    lock (originalOwnerHeld) {
                        call.OriginalOwnerConfirmed =
                            originalOwnerHeld.TryGetValue(key, out var held) &&
                            ReferenceEquals(held, call);
                        if (!call.OriginalOwnerConfirmed)
                            throw new InvalidOperationException("原Owner登记丢失");
                        call.RetainedByOwner = !call.IoClosed;
                        if (call.IoClosed) originalOwnerHeld.Remove(key);
                    }
                    if (call.IoClosed) call.Execution.Dispose();
                    // 未闭合：原Owner已确认保留同一对象、CTS、端口、ticket/Data。
                }
            }
        }
    }
    return call; // 分别读KnownResult/CallError/IoClosed/RetainedByOwner，不合并成bool成功
}
```

上述record和方法放在Fixtures宿主类内，使用System、Collections.Generic、Linq、Threading、Threading.Tasks及本模块namespace；不是完整产品源码。本例冻结request.Limits.Timeout=1秒、每次观察250ms、最多两轮、页长128，均为合成测试控制值，不是生产Profile。连同Start、主Wait、两轮观察/释放及Close，有限等待上界2.5秒；有限同步校验/消费另纳入§15的单例10秒截止，不用测试进程结束证明I/O释放。finally的cleanup不使用waitToken或已取消的executionToken；预算到期返回Pending/Waiting，只结束本轮等待。StartAsync/RecoverAsync/ReleaseAsync/CloseAsync的有限等待保证及迟到任务登记见§8.1/§10.1；禁止用外层Task.WaitAsync超时后丢弃真实进行中的I/O任务。

OriginalOwnerConfirmed只证明**恢复责任记录**仍在原Owner手中，不是资源释放、退款、算法终态或新Owner接管物理资源的证明。IoClosed=false时，此函数可以结束观察，但原组合根不能退出/Dispose端口、清槽、创建新实例顶替，必须保留call并在下一次有界恢复动作中沿CurrentTicket执行Query/ReleasePending时Recover、必要时Wait；从新终态发现Data先登记后Release，最后Close复核OutstandingResultLeases。每次动作沿用上述两轮上限，不递归/无限轮询；仍未闭合就再次确认同一槽原样保留。组合根的显式恢复触发/宿主生命周期Owner必须在对应真实消费者接入时绑定，不能把恢复责任交给一个即将返回的局部变量。程序进程终止不是原Owner确认释放；本例不声称支持跨进程native恢复。

关闭期间迟到Data会被最后Query收进原槽；即使KnownResult已为Completed，IoClosed仍可为false，原Owner须先确认结果lease归还才能清槽。若Close确认执行闭合且OutstandingResultLeases=0而最终Query不可知，则IoClosed可为true、KnownResult仍null，返回Unknown知识而非伪造Rejected/Cancelled。ReleaseAsync返回Failed/Pending或抛异常时保留同一Data/Owner/账项，不因下一次no-op或Dispose成功退款。只读Replay由宿主显式新OperationId重放冻结输入，不覆盖原ticket；结果仅按Use消费，不提交生产事实。

## 13. 可选 WPF UI Contract v0.3

本节是本模块可选控件的实施级页面合同，不新增平台 PageContract。v0.3补显式显示清理/导航面、只读结果接收和完整资源入口；旧控件/Session构造签名保留，传入viewport新增必须实现§13.1.2清理面，扩展语言用§13.4资源重载。该装配行为须随WPF包版本明确迁移，不能把旧任意FrameworkElement+窄port当已支持此清理。Core Contract v0.2和hash不变；UI尚未实现，不声称二进制兼容。控件只编辑宿主草稿和投影 Core 结果；全部算法/建议都有无 UI API。宿主可以单独嵌入 `SegmentationParameterEditor`（UserControl）或 `SegmentationOverlayView`（UserControl），完整 `SegmentationWorkbench`（UserControl）组合二者，不创建自己的顶层 Shell、权限服务、语言入口或隐藏窗口。

### 13.1 挂接、Owner 与角色

公开 WPF 类型放在 `Asun.Modules.Segmentation.Wpf`：`ISegmentationUiSession` 是宿主传入的每控件绑定会话，属性 `Service:ISegmentationService, Draft:SegmentationRequest, ViewGeneration:long, Culture:CultureInfo, Access:UiAccess, Viewport:ISegmentationViewportPort`；方法 `ValueTask<DraftApplyReceipt> RequestApplyAsync(SegmentationRequest draft,long generation,CancellationToken token)` 和 `event EventHandler<UiContextChangedEventArgs> ContextChanged`。UiAccess 为不可变 `(CanEdit:bool,CanPreview:bool,CanSuggest:bool,CanApply:bool,Revision:string)`；DraftApplyReceipt 为 `(Accepted:bool,NewParameterRevision:string?,Errors:ImmutableArray<ModuleError>)`。UiContextChangedEventArgs 只携带新的 generation、draft、culture、access，不能包含产品对象。每个控件 `Attach(ISegmentationUiSession session)` 一次、`DetachAsync(TimeSpan budget,CancellationToken token):ValueTask<DrainReport>`；重复 Attach 必须先完成旧 Detach，否则抛 InvalidOperationException（接入编程错误）。

只读操作者看原图/三态、组件/未知原因，允许缩放和选择；工程师在 CanEdit/CanPreview 下改草稿、试算、建议；发布由宿主 RequestApplyAsync 再核权限与参数 hash。无 CanApply 时按钮仍可见且不可用，显示短原因，不把控件按钮当授权。权限撤回立刻阻止新编辑/Apply，取消该控件预览；存量资源继续沿原 ticket 清理。语言变化只改资源/数字显示，不生成新 operation，不触及算法参数。

`ISegmentationViewportPort` 只用模块值类型：`SetContext(ImageSnapshotRef image,long generation)`、`SetOverlay(OverlayProjection projection)`、`SelectComponent(string? componentKey,long generation)`、`event EventHandler<ViewportSelectionEventArgs> SelectionChanged`、`Clear(long generation)`。OverlayProjection 为 `(Generation:long,Ticket:OperationTicket,StageId:string,Foreground:PixelRegion,Unknown:PixelRegion,UnknownReasons:ImmutableArray<UnknownPatch>,Boundaries:ImmutableArray<PixelRegion>,SelectedKey:string?,IsDisplayLod:bool)`，v0.3保留此构造并增加只读init属性`ComponentHits:ImmutableArray<SegmentationComponentHit>`（默认Empty）；WPF值`SegmentationComponentHit(Key:string,Region:PixelRegion)`。模块生成投影时同时给当前页/可见域内有界组件runs及`Key=ComponentKey ?? FragmentKey`，copy同计MaxProjectionBytes，不传lease借用数组；没有ComponentHits只显示、不得猜组件身份。ViewportSelectionEventArgs 为 `(Generation:long,ComponentKey:string?)`。投影须先按 MaxProjectionBytes 与宿主视域有界裁剪，只影响显示；宿主适配已有视口公开能力，不把其它模块控件或 ViewModel 类型带进 Core。组件选择失效时清选且保留当前图，不因列表过滤重新算。

### 13.1.1 SG-U1（W1）公开接线补全

三个UserControl均有public无参构造、`Attach(ISegmentationUiSession)`和`DetachAsync(TimeSpan,CancellationToken)`；必须在其Dispatcher STA线程构造/Attach，构造不启动算法/建隐藏窗口。`SegmentationWorkbench`内部创建一份参数编辑器和一份OverlayView，同session组合，但只有参数编辑器拥有命令/CTS，不能子控件各开一次预览。独立OverlayView只展示，不发Execute。Detach返回Waiting/ReleasePending时，原session/根槽仍持ticket、CTS、Data与未完成task；控件可退出显示，但不能清Owner。该有限Detach只操作本控件tickets，共享service不Close。

`ISegmentationUiSession`补充只读`ViewportContent:System.Windows.FrameworkElement`和`SuggestionRequest? CreateSuggestion(SegmentationRequest draft)`；前者是同Viewport端口的宿主可嵌入内容，只在OverlayView放置且不能已有别的WPF parent，参数编辑器不持其父关系；后者只生成已冻结标注/候选的请求，不运行/训练。没有标注返回null并显示“未提供标注”，按钮不执行。公开装配实现为`SegmentationUiSession`，sealed class构造 `(ISegmentationService service, SegmentationRequest draft, long generation, CultureInfo culture, UiAccess access, ISegmentationViewportPort viewport, FrameworkElement viewportContent, Dispatcher dispatcher, Func<SegmentationRequest,long,CancellationToken,ValueTask<DraftApplyReceipt>> apply, Func<SegmentationRequest,SuggestionRequest?> suggestions)`；无空端口/委托、generation≥1，同一Dispatcher，构造只保存/校验值。Session不拥有source/backend/账，不隐式Dispose它们。

`UiContextChangedEventArgs`是sealed EventArgs，public构造 `(long generation,SegmentationRequest draft,CultureInfo culture,UiAccess access)`，对应四个只读属性；`ViewportSelectionEventArgs`是sealed EventArgs，public构造 `(long generation,string? componentKey)`，对应两个只读属性。Session及ISegmentationUiSession公开`void UpdateContext(UiContextChangedEventArgs context)`和`ValueTask<DrainReport> CloseAsync(TimeSpan budget,CancellationToken token)`：更新只在Dispatcher原子替换草稿/文化/权限，草稿变更generation必须递增，纯语言变化可保持generation但不重算；权限撤回立即阻止新的Apply并取消自己的预览。多播逐订阅者隔离异常，不能因监听者抛异常断言宿主Apply未提交或回滚参数；Apply异常/未知由宿主自身原事务查询，控件不能自动重发。Session.Close只退订/取消/归还自身投影/等待自身ticket，不关闭共享service，未完成task仍归原根槽。SuggestAsync在调用前冻结并保存A.4候选×fixture派生OperationId集合与真实task；Close/Detach需要接续时用Service.DrainAsync作有限观察，按该集合筛本session评价ticket，只对这些原ticket Query/Recover，不取消/释放其他session。原建议task未完成即返回Waiting；报告Pending可空时仍保留task。Close预算仅观察，恢复每次最多两轮，重入只接续原登记，不重新Suggest。

控件执行只能走Session的公开Owner入口；`ISegmentationUiSession`及其实现另提供 `ValueTask<StartReceipt> StartPreviewAsync(SegmentationRequest request,long generation,CancellationToken executionToken)`、`OperationSnapshot ObservePreview(OperationTicket ticket)`、`void CancelPreview(OperationTicket ticket)`、`ValueTask<ReleaseReceipt> ReleasePreviewAsync(OperationTicket ticket,TimeSpan budget,CancellationToken cleanupToken)`、`ValueTask<SuggestionResult> SuggestAsync(SuggestionRequest request,long generation,CancellationToken executionToken)`。Start/Suggest须核当前generation/权限；Observe/Cancel/Release只允许本session登记的原ticket，旧代仍可清理，不能领取或释放别的session结果。`Service`仅供宿主装配/只读诊断，控件不能绕Session直接Start/Suggest或持Data。

Session每次Start之前建立有界预备槽，保存request/generation、命令Owner、linked执行CTS及Start task；Start返回先保存ticket，再允许显示。Observe先保存唯一Data lease再给只读snapshot，控件仅同步借用并生成有界显示投影，释放由Session唯一执行；ReleasePreview确认后才移除登记/Dispose CTS。每session最多一个在途预览或建议；未闭合槽阻止新命令，避免代次变化造成无界保留。参数编辑器仍是命令CTS Owner，Session在首次I/O前持其linked CTS与任务，不因编辑器卸载丢根。Detach只取消/归还本控件登记，session.Close负责最后接续；不把共享service关闭当本控件清理。Apply委托调用前也登记其原task；预算内未返回则保留，禁止自动重发。`DrainReport.Pending`列本session所有未闭合预览ticket/建议当前评价ticket，Apply未返但无ticket时Status=Waiting，Pending可空，附SEG-011与Stage=Apply，不能假Drained。

两个独立STA测试Host各自在创建Session/控件之前登记容量1的进程根恢复槽，保存service、source/backend/workingSets和Dispatcher强引用；按`new SegmentationUiSession(...) → new SegmentationWorkbench() → Attach(session) → 放入测试Window.Content`接线。关闭路径`Window停止新命令 → control.Detach → session.Close → 原Owner有限Query/Recover/归还Data → 独占service.Close → backend.Close`；任何异常均用finally走后续步骤，未确认沿原槽保留，不用窗口关闭证明资源完成。两个Host分别注入灰度与mask组合，不给模块重复放语言入口。宿主提供的viewportContent/port是必需图像消费方，不是隐藏初始化；实际viewport Assembly v0.2装配/有限Unbind按§13.1.2冻结，生产Source/权限/资源binding按SG-I1由原Owner采纳，不能让开发者临时选Presenter/Owner。

### 13.1.2 实际viewport Host装配、同binding呈现与有限归还

SG-U1自身只依赖Core和§13.1的窄端口/FrameworkElement，不反向引用viewport的私有VM/renderer或建立第二资源Root。实际双STA Host选择viewport公开控件，故本节定向消费[viewport 0.3.4-prep §10.6～10.9](../viewport/DEVELOPMENT-GUIDE.md#106-公开bindingunbind与presenter借用)的WPF Assembly v0.2；本轮仅按viewport 0.3.5-prep §20.5补§13.1.2.1公开源装配，已对齐的v0.2呈现/资源与Root/Close复用，不重新定义。Host桥放本模块Wpf.Tests/Fixtures的`SegmentationViewportHostBridge`，生产消费者将同公开端口映射放自己的Integration层，不进入Core/DLL业务层；以下是已冻结目标装配，不是已实现成员或运行结果。

**公开窄桥的清理面。** WPF namespace另有`SegmentationViewportSnapshot(Generation:long,ImageHash:string,VisibleDomain:PixelBox?,ProjectionPending:bool,Errors:ImmutableArray<ModuleError>)`及`ISegmentationViewportLifetimePort`：只读`SegmentationViewportSnapshot Snapshot`、`ValueTask<DrainReport> ClearAndDrainAsync(long generation,TimeSpan budget,CancellationToken token)`。实际传给Session的viewport必须同时实现此接口，否则构造在任何I/O前拒绝；导航面同样为必需，见下文。Snapshot不取图/不等Dispatcher，VisibleDomain为空表示尚无有效画布/同源计划，不随便取全图。它不宣称屏幕VisibleConfirmed，也不把viewport资源错误改成算法错误。Snapshot.Generation是Segmentation ViewGeneration；Host另存映射到viewport当前DisplayGeneration/ContextRevision，不能假定两者数值相等。映射只保当前+一项未闭合旧代；SetLayers引起的新显示generation只更新该映射，不生成算法RequestRevision。ClearAndDrain只清指定代的本桥叠加/在途投影借用，保留宿主图像、长期选择订阅和他人session；成功后当前代可再次SetOverlay，普通Clear不是永久封门。Detach/Session.Close先由Session封闭新命令和退订自己的事件，再清当代与一项未闭旧代；封门后不能重新投影。Drained要原SetLayers/选择/Dispatcher工作真实退出，本桥旧像素复制无后续borrow，且对应呈现已Revoke/Return确认。Session.Close/Detach在释放Data前先ClearAndDrain；Waiting/异常保留显示copy/原task/同binding，不清显示Owner。

**导航面与桥构造。** 同WPF namespace新增`ISegmentationViewportNavigationPort`，唯一方法`void Fit(long generation)`，实际viewport须同时实现清理和导航两面。Ctrl+0只调用该Fit；无有效当前代/正画布/DPI时不派发，Snapshot.Errors保留SEG-012/Stage=Viewport，禁止隐式使用旧画布。Host在其唯一串行队列保存原`viewSession.ApplyAsync(new SetViewCommand(ViewState.Fit2D(canvasDip,dpiX,dpiY)),token)`任务，canvas/DPI来自同Control实际布局；排队不等于可见确认，不影响算法代次。普通缩放由同viewport公开交互提供，不由分割模块另实现变换。

Tests/Fixtures桥是public sealed class，构造精确`SegmentationViewportHostBridge(ImageSnapshotRef image,long generation,ViewportControl control,IViewportUiBinding binding,IViewportSession session,IViewportProcessRoot root,ViewportContext context,long maxProjectionBytes,TimeSpan budget)`，实现上述三个ISegmentationViewport*Port；viewport类型使用其Core/Wpf公开namespace，Segmentation DLL不引用这些类型。构造在Control Dispatcher按Host原Bind/Attach回执登记验证同Control/binding/session/root及可信context/source mapping（不猜binding.Control之类未公开属性）、generation≥1、budget>0、maxProjectionBytes≥1，保存已Attach成功的同源context；只登记不做I/O、不取latest。Host原槽在构造前持全部引用，桥的源生命周期不由构造创建。窗口布局变化通过同Control的SizeChanged与宿主窗口DPI通知（每次用VisualTreeHelper.GetDpi读取当前Control）更新本桥画布记录，限一项pending；清理只退订属于本桥的监听，Detach封门后原Host继续持旧任务直至确认。

1. Host在任何异步创建前使用已有进程Owner槽强持image/source/profile/viewport root、Control、renderer ports及原Task；创建viewport Control之后立即取得该实例`control.Presentation`。取`ViewportRendererFactory.Create(control,root,rendererOptions)`的Value.Backend/Value.Lifetime为一组同Control/root端口，或使用Host已实现的同签名有限CPU fixture；不把record本身当Lifetime，不另造第二root。内置renderer源生产者在本节§13.1.2.1用公开Factory预装配，具体源/坐标/授权/admission映射消费viewport §15.2已冻结公开端口；ImageSnapshotRef须与该来源SnapshotId/hash/父格完全同源，投影不偷取latest。
2. viewport factory.Create的Options显式`Frames=sourcePorts.Frames`、`Coordinates=sourcePorts.Coordinates`（均为§13.1.2.1预装配的稳定实例）、`Presentation=control.Presentation`、`Backend=rendererPorts.Backend`、RequestedFeatures=Navigation|Presentation（Probe仅在注入Probe时追加），ReadOnly、不请求RoiEditing；工程参数编辑权在Segmentation Session而非图像ROI编辑权。生产只读Host使用Required和真实授权/资源port；离线工程Host可显式BudgetOnly，不能套用生产。保存原session，然后调用下面目标语义形状；resources实际是完整schema，不用七键假快照：

```csharp
var resourceReceipt = ViewportUiResourceCatalog.Get(culture.Name);
if (resourceReceipt.Outcome != PortOutcome.Succeeded || resourceReceipt.Value is null)
    throw new InvalidOperationException("视口语言资源不完整");
var bindTask = control.BindAsync(viewSession, root,
    new ViewportUiBindingOptions(bindingId, OwnSession: false,
        Resources: resourceReceipt.Value, UiCleanupBudget: uiBudget,
        Lifetime: rendererPorts.Lifetime, ExecutionBudget: uiExecutionBudget), token);
// HostOwner保存bindTask原实例；预算只观察该task，不能丢弃真实绑定。
var bound = await bindTask;
if (bound.Outcome != PortOutcome.Succeeded || bound.Value is null)
    throw new InvalidOperationException("视口绑定失败");
var binding = bound.Value; // 同control.Presentation转发的唯一binding
// 先保存binding，后保存/启动AttachAsync(完整同源ViewportContext)原task。
// Attach成功后才以当前实际画布调用SetViewCommand并保存成功回执Plans；零画布等待布局，不借图。
// 其后new bridge，再new SegmentationUiSession(..., bridge, control, dispatcher, ...)。
```

Host完整Context及Profile逐项沿viewport §§3.3/4.1/11.2构造；本模块测试只将源换A.5的独立scalar/mask输入，坐标仍是源像素中心，实际renderer显示原图而非mask替代原图。source不能仅因为hash字符相等而被Host认作可信来源，须来自同一冻结source binding。ViewportUiBindingOptions.Resources.Revision精确viewport-ui-text/1；本模块Seg.*资源保持自己的schema。已绑定control只由OverlayView放一个WPF parent，Workbench不再放第二份。OwnSession=false固定由外层Host负责viewSession.Dispose，Segmentation控件不取得共享关闭权。

3. **窄端口实施映射。** SetContext纯校验Image/hash/generation与Host可信SourceBinding，代次变化保存完整新context，进入一项有界latest-pending；所有异步Update/Apply原task先登记，由Host串行执行，未闭合旧呈现不覆盖其Owner。SetOverlay只能接受当前generation/ticket/StageId同源的有界独立copy；host通过`viewSession.ApplyAsync(new SetLayersCommand(replacement),token)`提交本桥图层，Replacement包含宿主当前不可变层及本桥层，不删除他人层。Clear仅移除本桥LayerId前缀，若宿主在同session并发改层须由唯一Host串行合成；不能用旧Replacement覆盖别人变更。SelectComponent只改变只读选择层和列表联动，不发分割操作或ROI提交。SelectionChanged只回同generation及原ComponentKey/FragmentKey；桥为ComponentHits的各已显示run保有界LayerId→Key映射，组件run与聚合F不重复绘制。通过同session.EventRaised的IntentReady/Intent.Selection接选择结果，核SourceRevision/CoordinateRevision/DisplayGeneration并逐候选映LayerId；零项清选，单一Key选该行，多Key或Truncated只列有限候选让用户明确选择，不自动取首项。普通聚合F/U层Interactive=false；组件run层Interactive=true。此为source polyline只读导航命中，不能声称精确物体边界/生产定位；未显示或页外组件从结果分页选，不把LOD未命中当不存在。
4. **有界几何/裁剪。** Host从首次Attach后同session.SetViewCommand的成功ViewportReceipt.Plans（以及后续成功Apply回执）保留有界同源DisplayPlan，沿其DipToSourceCenter变换四个画布角得到父图可见bbox；正向矩阵名是SourceCenterToDip，不猜SourceToDip成员。向外floor/ceil到像素中心，再交图像与D；非invertible/零画布/不同格时VisibleDomain=null。先校验runs/字节上限再复制：前景run画从(cBegin−0.5,row)到(cEnd+0.5,row)的SourcePolyline，未知域用同格斜线短段/文字图例，边界用真实Boundary runs，选中用该组件bbox闭合polyline。每个独立线段是一个OverlayPayload(SourcePolyline)，SourcePoint2D顺序Column/Row，SourceId/SourceRevision/CoordinateRevision沿可信当前Context原值保真，OverlayLayer.SourceRevision不得替换成RequestHash；GeometryRevision由Host显式冻结的叠加修订映射，RequestHash/StageId放本桥有界关联表/LayerId映射，不覆盖源身份；原Region不可借给viewport留存。受Limits.MaxLayers/MaxGeometryPoints及MaxProjectionBytes约束，保留固定前缀按(row,column)逐段有界展示，截断标IsDisplayLod=true和“仅显示部分叠加”，从不暗示全集已覆盖；不得按采样结果删生产F/U。viewport原控件负责实际绘制/同binding变换，本模块不在HALCON HwndHost上叠WPF透明Canvas规避airspace。当前公开viewport不提供独立质量配色/填充参数，不猜不存在的Style API；模块图例和结果行用§13.2颜色，图像层靠线型/纹理/图例区分，实际主题遵上游renderer。
5. **原呈现任务。** 同Control.Presentation直接转发原Commit/Revoke Task，不能用async包装替换、手造PresentationReceipt或以WPF属性赋值当VisibleConfirmed。Host将binding.GetPresentations中的OriginalCommit/Acquire/Confirm/Revoke/Return及PresenterIdentity关联到同generation/ticket；viewport root持其原Task/lease，Segmentation根仅强持观测/桥copy，不重复归还Presenter。回调迟到或失败Value带lease仍由原root抽取保留；桥只停止采用并Revoke/Return同一presentation，不能clear表、重Bind或新Root逃Unknown。
6. **有限Detach/晚到Return。** 由control.Detach/session.Close驱动一次共同的幂等收尾：先停本桥新命令→取消本session预览/建议→ClearAndDrain→释放原Data；不能清理后递归调用Detach形成循环。外层Host再对独占图像binding.UnbindAsync，按原uiBudget有限观察。Unbind未Drained或原Bind/Dispatcher/Return仍在途时保留control/binding/renderer/root/桥copy，晚到lease由原root继续Return；Detached或Window.Close不算完成。原binding收敛后Host对其独占viewSession.Dispose与root.Close作已有有限观察，不借本模块重写Root/Close。共享viewSession不由控件Dispose，外层Host串行安排；图像窗口和分割service是两条独立生命周期，任一pending都不能退出原进程Owner。

A/B两STA Host分别组合工程scalar与只读mask，使用独立root/control/renderer/service和source borrow，界面都可带参数Editor但B的CanEdit/Preview/Suggest/Apply全false。B由外层Host先按§12运行冻结mask请求并保原结果，再用下述AdoptReadOnlyResult一次转交显示/释放责任，不因只读权限留下空参数页。合成UI Profile沿viewport §10.8的源显示64MiB、UI64MiB、ExecutionBudget=(67108864,32,32)、root总268435456bytes、2presenter槽、2秒观察；它们是软件容量上限，不是客户推荐/实测峰值。Segmentation的MaxProjectionBytes另取A.5的8192，不自动继承64MiB；超层数/投影上限明确LOD/拒绝显示，算法Data保持。真实1920×1080当前DPI窗口、airspace、内容与授权/Return另按§15验证。

**只读结果接收。** `ISegmentationUiSession`及实现新增同步`ValidationResult AdoptReadOnlyResult(SegmentationRequest request,OperationSnapshot snapshot,long generation)`。调用仅在Dispatcher、当前代、无本Session未闭预览/建议/Apply槽时；用于Host已运行的同Service结果，不Start/重算、不调用Apply。先纯校验request与Draft同源/同参数身份、snapshot终态且Result/Data非空未释放、Ticket与RequestHash匹配、Service.Query(ticket)的Result/Data是同一引用、服务状态无Pending；失败返回IsValid=false和SEG-012/017，资源责任仍由调用Host原槽持有。成功在任何事件通知前把request/ticket/唯一Data及显示generation登记到Session原槽，再返回IsValid=true：Host在收到成功回执后仅保留恢复根强引用，停止读取/释放同Data，Session为唯一结果释放Owner；回执丢失时查Session.ObservePreview原ticket确认，不重交/双释放。授权由Host在调用前核对，同一结果不得向两个Session转交；重复同ticket/Data调用须先查本Session已接收记录，当前代返回同成功知识、不增加Owner；此幂等分支先于“无未闭槽”检查，旧代重复只返回原记录知识且不重新投影。CanPreview=false只禁止新计算，不禁止显示已授权结果。控件按现有ReadStage/ReadComponents流程生成有界页和叠加，分页/选择照常可用；Detach先清显示借用再ReleasePreview，失败沿同Data/原Host根恢复。持久化历史结果不冒充本接口的活lease，须由消费者另按正式Replay请求在同service产生结果；本模块不新增存储codec。

#### 13.1.2.1 内置renderer的公开源生产者装配（viewport 0.3.5限定消费）

本节只补[viewport §15.2.2.1](../viewport/DEVELOPMENT-GUIDE.md#15221-公开cpu发布源生产者与预装配bc-u1)公开生产者到当前双STA Host的接线。原图仍由Host/source Owner提供；RegisteredMask只作分割输入，不能用mask F/B/U冒充原图像素。分割Core/AsunImage backend不取得发布服务所有权，也不创建viewport私有payload。以下类型来自可选适配包`Asun.UI.Viewports.ImageFrame`（net10.0），只由Wpf.Tests Host或正式消费者Integration引用；Segmentation Core/Wpf DLL的公开依赖和构造不改：

```csharp
using System.Collections.Immutable;
using IF = Asun.Modules.ImageFrame.Resources;
using VP = Asun.UI.Viewports;
// 上游公开形状摘录；唯一声明归viewport指导，不在本模块另行实现这些类型。
// namespace Asun.UI.Viewports.ImageFrame
public sealed record ViewportImageFrameSourceOptions(
    string ConsumerId, int MaxBindings, long MaxRetainedMetadataBytes);
public sealed record ViewportPublishedFrameBinding(string BindingId,
    IF.FrameDescriptor Frame, VP.ImageSourceDescriptor Image,
    ImmutableArray<int> PlaneIndices, string PixelSpace);
public interface IViewportImageFrameSource
{
    VP.IFramePort Frames { get; }
    VP.ICoordinatePort Coordinates { get; }
    VP.PortResult<string> Register(ViewportPublishedFrameBinding binding);
    VP.PortResult<string> Remove(string bindingId);
}
// ViewportImageFrameSourceFactory.Create(IF.IFrameService source,
//     VP.IViewportProcessRoot root, ViewportImageFrameSourceOptions options)
//     : VP.PortResult<IViewportImageFrameSource>
```

**两类身份和输入。** Host在任何异步工作前的原恢复槽保存：实际`IF.IFrameService`及其原ServiceEpoch、同viewport root、已登记read ConsumerId、sourcePorts，以及每帧的完整已发布`IF.FrameDescriptor`/发布回执、Segmentation ImageSnapshotRef、完整viewport ImageSourceDescriptor、sourceBindingId与PixelSpace。工厂身份是`(source实例+原epoch,root实例,read ConsumerId)`，整个viewSession内固定；逐帧身份是`(Frame.Key的Guid/ulong,SourceId,SourceRevision,CoordinateRevision,DecodeRevision)`，sourceBindingId仅是该entry的稳定登记键，**不同于**UI绑定的bindingId。禁止以同名root/ConsumerId或相同hash替代实例，禁止把FrameKey/源修订当工厂身份，每次换图重建sourcePorts或替换已冻结Options.Frames。

逐帧输入必须已由发布Owner核实`PublishResult.Receipt`为Completed/Error=None/OperationResourcesReleased=true且Frame非空。Host把其原Frame直接传Register；SnapshotId/Revision/Sha256/ParentGridId/ParentGridRevision到Frame.Key、SourceId/SourceRevision、PixelSpace的对应由原来源Owner显式保存，不假定字符串相等就同源。Frame与Image.SourceId/SourceRevision逐值一致，CoordinateRevision为正且对应同整数像素中心格；Frame.CoordinateReference精确等于PixelSpace。来源换格或单位时不套identity，仍走既有明确坐标Owner端口，本内置工厂路线拒绝。

**预装配顺序。** 原source Owner提供已发布CPU level0帧及借用服务；若测试Host从A.5独立冻结像素制作显示源，只在本Host使用image-frame公开`FrameServiceFactory.Create(ResourceLimits,IManagedLayoutValidator,TimeProvider,IFrameEventSink?)`与`PublishCopyAsync(CopyPublishRequest,CancellationToken)`，`IFrameInputRows.CopyRow(int planeIndex,int y,Span<byte> destination):FrameError`同步复制原行，不保存destination或改原像素。Publish的原ValueTask只AsTask一次，原槽先保存ServiceEpoch/RequestId/FrameKey、输入稳定借用与原Task；未知时沿`QueryOperation(原epoch,原RequestId)`观察，不换RequestId重发或归还仍在复制的输入。图像发布属于Host，不新增分割API/算法；正式消费者可以直接注入其已发布源，无需再复制。

本双STA合成Host的source资源Profile显式取：FrameBudget的Deployment/Profile字节上限各67108864、DomainSegments上限各65536，来源/修订取本Host冻结来源，ProfileId=`seg-display-test`/Revision=`1`；ResourceLimits MaxCpuBytes=67108864、MaxNativeBytes/MaxGpuBytes/MaxCacheBytes=0、MaxFrames=2、MaxActiveOperations=2、MaxQueuedOperations=0、MaxReceipts=64、ReceiptRetention=1秒、DrainTimeout=2秒。每Host单独登记publish/read两个ConsumerLimit，MaxHeldBytes=67108864/MaxLeases=4/MaxActiveOperations=2/MaxQueuedOperations=0；FrameServiceFactory配`Asun.Modules.ImageFrame.Core.ManagedLayoutValidator`、原TimeProvider、events=null，成功必须Error=None且Service非空。source及publisher额度独立于§13.1.2原viewport root/UI预算；本表是Synthetic容量，不声称实际峰值，不占分割Core工作账。FrameBudget来源字段是限额来源，不用它替代每帧实际身份。

| 本Host实际输入 / 调用 | 工程scalar Host A | 只读mask Host B |
|---|---|---|
| source与消费者 | A自己的FrameService/epoch；publish=`seg-ui-a/publish`，read=`seg-ui-a/viewport` | B自己的FrameService/epoch；publish=`seg-ui-b/publish`，read=`seg-ui-b/viewport`；不借A或分割结果lease |
| 冻结原图 | A.5的原Byte 3×3像素，单plane Scalar=UInt8/BitsPerSample=8/ChannelCount=1/Packing=SinglePlane/Role=Intensity、LittleEndian、rowBytes=stride=3、offset=0、accessible=declared=9；Layout/Metadata域Full，unit=1/scale=1/bias=0/Channels={Gray} | 与B的A.5 mask请求Image同源的原Byte 3×3图，显示原图不显示mask替代；同布局，每个原FrameKey由B发布Owner生成并保存 |
| source descriptor | 原Frame.SourceId/SourceRevision、3×3/1channel/8bits/unsigned、CenterInteger、正CoordinateRevision、Full Validity；level0为3×3、tile256×256、identity层中心映射、MaxDecodedTileBytes=65536、DecodeRevision绑定本帧原内容/域/adapter修订；PixelSpace由本Host明确映原g/r父格 | 同结构，全部来源/坐标token与Frame/PixelSpace使用B自己的冻结映射，不跨Host合并身份；换图的新revision仍属同工厂 |
| 预装配 | `ViewportImageFrameSourceFactory.Create(displayService,root,new ViewportImageFrameSourceOptions("seg-ui-a/viewport",2,1048576))`，核Succeeded且Value非空，保存sourcePorts；不读源/发布或创建Task | 同调用改B的实际displayService/root及read ID；2 entries/1MiB为本Host合成metadata上限，不借A额度 |
| 稳定端口与登记 | session.Create之前把sourcePorts.Frames/Coordinates放Options；Control/renderer/Presentation/Lifetime/Bind沿§13.1.2原v0.2。随后`sourcePorts.Register(new ViewportPublishedFrameBinding(sourceBindingId,publishedFrame,imageDescriptor,ImmutableArray.Create(0),pixelSpace))`成功才第一次Attach | 同顺序，独立root/control/session；Coordinates只给同PixelSpace identity、二维有限点/Z=0，不能签物理标定 |
| LUT与像素解释 | InitialView.Lut显式`new LutWindow(0,255,"seg-display-range/byte/1")`，只用于显示格式范围，不冒测得min/max/参数建议 | 同手动显示范围；生产UInt16可用(0,65535)且显式修订，无损保原编码；Real32显示不由本CPU首版工厂支持，采用原公开自有backend路线或明确拒绝，不静默量化 |

**替换、Remove与恢复。** Create/Register/Remove是同步有限元数据操作，先核Options/ViewportLimits与1MiB保留上界再深冻结，不启动Read/IO或猜有帧。该CPU首版仅一个plane索引0、原尺寸level0/identity、UInt8灰度/UInt16灰度或RGB8 Interleaved；本两Host只用Byte灰度。Register同sourceBindingId同完整内容幂等，同ID异内容或同SourceId+SourceRevision+CoordinateRevision+DecodeRevision歧义拒绝；同SourceId+CoordinateRevision新旧PixelSpace必须一致。不把分割IImageLease、任意IFramePayload marker或私有buffer交给内置renderer。

后续切图唯一顺序：同sourcePorts.Register新entry→保存原`viewSession.UpdateAsync(new ViewportUpdate(原baseRevision,完整新Context),token)` Task→观察其原代/ContextRevision回执及旧Revoke/源Return/实际CPU和Dispatcher退出→`sourcePorts.Remove(旧sourceBindingId)`→仅发布Owner按原FrameKey调用`RetireAsync(key,2秒)`并保其原Task/回执。新旧最多2个entry，不覆盖未闭旧代；容量满先拒新，不能强移除旧entry。首次Attach后更新仍Update，不重Attach/Bind；不据Update Task完成、已采用新图或Sources.Count推断旧借用已归还。Remove在原entry仍被Context引用、原Read/未知operation/CPU scope/lease未实际Returned时拒绝或Unknown，保entry/原task/lease与预算；原服务epoch变化/QueryOperation NotFound不证明不存在借用。有限观察耗尽只保原槽，禁止新工厂/新Read/新root绕Unknown。viewport原源Adapter保存ReadAsync一次AsTask、原FrameKey/consumer/root签发call与失败/迟到lease；归还沿原ReturnId及同lease.ReleaseAsync/有限查询，不由Segmentation再Return一次。

Remove成功只证明producer元数据已卸载，不Retire源、不Close服务、不证明storage退款；Retire/Close无ct，只限制观察、未知仍由原source Owner保留。发布失败/Conflict或登记失败时只撤本Host确已成功创建且从未交付/无借用的发布；不Retire同key既有他人帧。新entry已登记而Update未接纳时，先核它未被Context采用且所有原操作已退出，再Remove该新entry/由发布Owner Retire，不能删仍活跃的旧entry。同源共享服务不由本控件关闭；本测试Host独占服务时也须先按已有viewport Dispose/Root关闭事实确认无Context/borrow，再Remove/Retire其发布并有限Close，原Root/Close签名和责任不变。未确认源责任仍阻Host退出，禁止用窗口关闭或new epoch证明清理。

**本次未采用能力的准确边界。** 已定向读取viewport §4.5.1完整`OverlayObjectRef`复合键及`ApplyAsync(new SelectOverlayObjectCommand(OverlayObjectSelectionRequest),ct)`，但当前SelectComponent仍按§13.1.2步骤3～4替换自身bbox闭合Polyline；原IntentReady/LayerId→Key与局部Clear逐字保持，不迁移该新命令。也已读§4.7.1：空Sources/Layers完整Update须旧Revoke、源Return/工作退出及同代真实空画面确认，Unknown禁止新非空请求；本模块Clear只撤己方叠加并保图，因此不调用整源Empty Update、不读其新EmptyTransition字段。切图采用上项合法非空Update；最终关闭采用已有Dispose/Unbind收尾，均不借这两项新增能力绕恢复门。

### 13.2 1920×1080 布局与 DevExpress 组合

只验证一个固定 1920×1080 物理视口，扣除真实任务栏/边框/标题栏/宿主导航后以可用客户区布局；不得把 1920×1080 当可用客户区或改系统设置。横向三栏目标 18%/60%/22%，左参数宽 280..360 DIP、右结果 320..420 DIP，中间影像优先；高 DPI 客户区不足时右栏与下方图表转选项卡，左高级参数可折叠，试算/取消/状态始终可见。这些是布局目标，不声称每个 DPI 下均达到固定像素宽。

| 区域 | 控件与具体行为 |
|---|---|
| 顶部 40 DIP 命令条 | DevExpress Bars 的可见“试算 / 取消 / 参数建议 / 应用草稿 / 重置布局”；图层切换和版本状态。Apply 显式展示草稿/生产差异并交宿主，不将取消/恢复藏在菜单 |
| 左侧参数 | PropertyGridControl.SelectedObject 只绑定可编辑草稿投影，明确 PropertyDefinitions/分类为输入、方法、形态、筛选、资源；常用字段常显，高级类折叠；同 Core Validate 的字段路径错误放到对应 editor，不能反射显示所有后台字段 |
| 中央影像 | DockLayoutManager 的中央 LayoutPanel 承载宿主视口，保持不可关闭；左右 LayoutPanel 可停靠/自藏但不能盖住关键命令；原图/原三态/派生差/边界/未知原因图层，轮廓和格坐标固定同一父图；缩放联动双视图不复制算法/原图 |
| 右侧结果 | GridControl.View=TableView，AllowPerPixelScrolling=true；列固定 key、面积/单位、边界状态、筛选状态、原因。结果 lease 分页投影，组件 key 为选择权威；排序同值按 key 破同分。分组/筛选是只读投影，页外/LOD 计数标签明确，不改原全集 |
| 下方诊断 | 默认折叠160 DIP的ChartControl+XYDiagram2D+BarSideBySideSeries2D，只绑定ReadStage中各UnknownReason区域并集的像素数；同像素多原因可重叠，标题“未知原因覆盖”，不把柱和当U总数。选柱只高亮该原因，不改threshold。当前API不输出直方图，首版不显示/猜造灰度直方图，也不为画图重跑全图 |
| 底部 28 DIP 状态栏 | 当前输入/参数修订、完成/部分/未知、阶段、实际阈值、预算和释放状态；释放未确认给可见“等待释放 / 查看原因”，保留原 ticket，恢复经 Service.RecoverAsync |

主题跟随宿主已用 DevExpress 主题，控件不写全局 ThemeManager；8 DIP 间距、16 DIP 内边距、正文 13..14 DIP、数字右对齐/单位列分离。图例/结果行的前景用青色、Unknown用琥珀色，图像实际线型/纹理及选中框按§13.1.2由同viewport绘制；不能只靠红/绿区别状态。只在选择/展开时使用短动效，计算/错误/排空状态不以动画延迟。高级参数的风险/支撑限制使用 `SuperTip` 的 HeaderItem/Item/Separator；Bars 通过 BarItem.SuperTip，其它按钮通过 SuperTipControl 挂 ToolTip，不能给普通控件猜不存在的 SuperTip 属性。TreeList 不适用于平铺组件；只有形态有序阶段的树状来源视图确有消费时才用，首版阶段列表保持扁平。

### 13.3 代次、键盘、恢复与三语

编辑只生成新 Draft/RequestRevision/ViewGeneration；250 ms 输入防抖（仅 UI），保留最多一个 active 和一个 latest pending，旧 native 排空前新预览不能挪走其额度。Start/Wait 用后台 await，不阻塞 Dispatcher；返回核 image hash、parameter hash、ticket、generation，A→B→A 第一代 A 仍过期。旧结果 lease 完成归还后释放，迟到回调不改新图。图层/行选择只读，按冻结 generation 联动 Grid/Viewport/Chart，递归选择事件有幂等保护。

F5 试算、Esc 取消 active 预览（编辑器弹出框优先接 Esc）、Ctrl+Enter 请求应用草稿（宿主权限门仍生效）、Ctrl+0 适应图像、Tab 顺序命令→参数→影像→结果→诊断；箭头浏览组件、Enter 定位选择，焦点不随 Progress 跳转。AutomationId 固定为 Seg.Run/Cancel/Suggest/Apply/Parameters/Image/Components/Diagnostics/Status；每个参数字段附稳定 field path。Unknown/失败用文字与图标；原始异常留诊断详情不当主提示。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Seg.Run / Cancel | 试算 / 取消 | 試算 / 取消 | Preview / Cancel |
| Seg.Apply / Suggest | 应用草稿 / 参数建议 | 套用草稿 / 參數建議 | Apply draft / Suggest parameters |
| Seg.Partial | 部分区域未处理 | 部分區域未處理 | Some regions were not processed |
| Seg.SupportMissing | 邻域输入缺失 | 鄰域輸入缺失 | Neighborhood input missing |
| Seg.ReleasePending | 资源尚未释放 | 資源尚未釋放 | Resources are still held |
| Seg.FilterUnknown | 特征无法计算 | 特徵無法計算 | Feature unavailable |
| Seg.Recovery | 等待释放后重试 | 等待釋放後重試 | Retry after resources are released |

所有标题/字段/错误/单位/建议/菜单/权限提示用资源键扩展，英文长句换行不挡操作按钮；数字以 culture 显示，写回参数按显式 editor parse，不用显示文本作 hash。Detach 先阻止新 UI 请求并退订上下文/选择，取消本控件 CTS，只等待其 ticket（共享服务不 Close）；释放其 Data/投影租约。若控件独占服务才 CloseAsync；等待未完保留宿主恢复对象、提示 pending，不能靠窗口消失当释放完成。重新 Attach 使用新 generation。

UI 验收在同一 1920×1080 视口完成三语与当前实际 DPI：长错误/三位以上参数、Grid 首尾页、多选/筛选、键盘/UIA、编辑抖动、权限撤回、A→B→A、关闭时 native 未返、释放失败、未知域斜纹和有界投影。记录真实客户区和图像占比；截图或合成 UI 不能证明 HALCON/现场资格。本轮只冻结页面规格，未启动 WPF。

### 13.4 编辑器、资源、分页与应用的确定性行为

**控件API依据。** 本轮dxdocs工具不可调用，定向读取本机DevExpress25.2官方XML：`C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`下PropertyGrid/Grid/Grid.Core/Docking/Core五份文档。已核`PropertyGridControl.SelectedObject/PropertyDefinitions/ShowProperties`、`PropertyDefinitionBase.Path/Header`、`ShowPropertiesMode.WithPropertyDefinitions`、`TableView.AllowPerPixelScrolling`、继承的`DataViewBase.AllowEditing`、`BaseLayoutItem.AllowClose/AllowFloat`、`BarItem.SuperTip`和`SuperTip.Items`，与§20.1既有官方资料复用；这不是XAML编译或窗口验收。实现不下载/替换本机25.2.3、不查授权。

PropertyGrid只绑定本模块WPF的有限DraftProjection（非Core输入对象，不公开为产品DTO），ShowProperties=WithPropertyDefinitions，PropertyDefinition.Path对应以下显式字段。身份/格/Origin/Qualification/预算来源只读；编辑方法Kind不静默搬旧参数，用户选新Kind后必须显式补齐资格与必填值，Validate全部通过才可试算。每个SpinEdit的类型/端点/nullable和步进沿§5；double有限校验且Culture解析，整数端点不四舍五入。没有生产默认；合成A.5只能由测试Host显式载入，用户“恢复草稿”回宿主初始冻结Draft，不加载最近一次成功参数。

| 字段组与控件 | 显式路径 / 操作 | 固定行为 |
|---|---|---|
| 输入/状态，只读PropertyDefinition | Image.SnapshotId/Revision/Encoding/GrayUnit、Domain.Revision、Qualification.Use/Revision、ParameterRevision/Hash | 原图格、单位和版本常显；F/B/U计数及完整性分开，不显示PASS |
| 方法，ComboBoxEdit与按Kind可见的字段 | Method.Kind；Fixed的Intervals.Min/Max；Global.Polarity/StatisticsDomain；Dynamic.Mode/Offset/Reference或MeanWindow；Sauvola.Polarity/WindowSize/Scale/Range；MaskRevision/ClassKey | Interval用只含Min/Max的有限Grid（最多64行），新增行空值直到用户填写；Global统计域、Reference/Mask从Host冻结快照只读选择，不现场读latest或新建算法 |
| 形态，GridControl有序行+内嵌明确editor | Processing.MorphologySteps的StageId/Op/Kernel/Iterations/ObjectMode | 添加/删除/上移/下移四个常显命令；最多16步，重排改ParameterHash，核分支只开该字段，ExplicitKernel由Host冻结RLE提供，不能粘任意脚本 |
| 特征与筛选，CheckedComboBoxEdit/有限Grid | FeatureSet、FeatureStageId、FeatureFilters.Feature/Comparison/Min/Max/Unit、FilterCombination | 最多64键/256谓词；Key决定单位与唯一Value槽；BoundingBox/Boundary不能拿数值editor筛选；Any/All缺值沿Core三值逻辑 |
| 资源，高级折叠PropertyDefinition | Limits各显式字段、Processing.Tiles.Revision | 字节/次数/时长按§5，客户上限由Host限制不可越权扩大；TileCore冻结由Host提供，不增加“自动猜网格”按钮 |

结果Grid只读AllowEditing=false，每页128组件（≤A.2 count上限）；首/前/后/末页按钮显式，Unknown TotalKnown不启末页。默认顺序按Core key，不直接把所有Data读入ItemsSource；筛选/排序只作用当前页并显示“当前页”，要全集统计由已有Summary给，不伪装全局重排。选择key只有一个权威，换页无key则清选择，原F/组件总数不改。Overlaycopy/页copy/未知原因计数都在MaxProjectionBytes内，先算run/point/对象头的保守上界再复制；超限先给有限LOD/列出未显示量，不无限后台分页。模块不得在lease释放后用page或Region底层引用；显示需要保留的copy由显示Owner持至ClearAndDrain确认。

Apply先显示输入/方法/形态/筛选差异和“仅应用草稿”，CanApply及当前generation通过后调用唯一RequestApplyAsync。Accepted只表示宿主接收；NewParameterRevision用于刷新宿主Context，不自行设置生产配置。异常/未知保留原Apply task并显示“应用结果未知，请查询原请求”，再次点击只观察原事务，不能重发。Suggestion选中候选只产生新Draft/ParameterHash，不自动Apply；成本/覆盖/失败/Search与Holdout分别展示，InsufficientEvidence/Partial不给“推荐已合格”。

**完整资源入口。** Wpf增加`SegmentationUiResources(Language:string,SchemaId:string,Text:ImmutableDictionary<string,string>)`，`SegmentationUiResourceCatalog.Get(string language):SegmentationUiResources`和只读`RequiredKeys:ImmutableArray<string>`。SchemaId固定`segmentation-ui-text/1`，Get只对规范化zh-CN/zh-TW/en-US返回本表完整快照，未知/非法culture抛ArgumentException，不隐式回退机器语言。RequiredKeys在发布时展开组合行并冻结不可变值，不在运行时解析Markdown。现有Session构造Culture在三内置语言时显式Get该资源；扩展语言使用公开新增构造重载（原§13.1.1全部参数末尾再加必填SegmentationUiResources resources），不改Core/API编码。Session及接口补只读Resources、`void SetResources(SegmentationUiResources resources)`及`void UpdateContext(UiContextChangedEventArgs context,SegmentationUiResources resources)`重载。SetResources只替换当前Culture同名资源；跨语言（含扩展语言）用后者在Dispatcher先一起校验context.Culture.Name/resources.Language、schema、全部RequiredKeys和每值1..2048字符，再原子替换context与resources，最后发一次ContextChanged；失败抛ArgumentException并保留原context/资源/代次。原单参UpdateContext在切到内置Culture时先Get完整包，当前扩展Culture保持同名包；切到不同扩展Culture须使用双参重载，单参拒绝，禁止“先设不同语言包再改Culture”的不可执行顺序。纯语言切换可同generation，不从旧Culture重排算法。控件资源/表头/UIA Name/HelpText/禁用原因/字段错误均取此快照；ID、数值、类键和来源事实不翻译。

以下表为同DLL随包发布的完整必需文本，前缀均为Seg.；斜线组合行各侧键/值按同顺序一一对应，不是运行时分词。原§13.3七行保留，重复键取相同文字。Error键按SEG编号、State/Method/Feature/Unknown/Field等明确映射表，不能直接显示Enum.ToString或异常。

| 键（Seg.前缀） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title / Image / Parameters / Components / Diagnostics | 分割 / 图像 / 参数 / 区域 / 诊断 | 分割 / 影像 / 參數 / 區域 / 診斷 | Segmentation / Image / Parameters / Regions / Diagnostics |
| RestoreLayout / ResetDraft / Add / Delete / MoveUp / MoveDown | 恢复布局 / 恢复草稿 / 添加 / 删除 / 上移 / 下移 | 還原配置 / 還原草稿 / 新增 / 刪除 / 上移 / 下移 | Restore layout / Reset draft / Add / Delete / Move up / Move down |
| First / Previous / Next / Last / CurrentPage / DisplayPartial | 首页 / 上一页 / 下一页 / 末页 / 当前页 / 仅显示部分叠加 | 首頁 / 上一頁 / 下一頁 / 末頁 / 目前頁面 / 僅顯示部分疊加 | First / Previous / Next / Last / Current page / Some overlays are hidden |
| NoLabels / NoStatistics / NoImage / ReadOnly / ApplyUnknown / ApplyDraftOnly | 未提供标注 / 无统计数据 / 无图像 / 只读 / 应用结果未知，请查询原请求 / 仅应用草稿 | 未提供標註 / 無統計資料 / 無影像 / 唯讀 / 套用結果未知，請查詢原請求 / 僅套用草稿 | No labels provided / No statistics / No image / Read only / Apply result unknown; query the original request / Apply draft only |
| Search / Holdout / Candidate / Cost / Coverage / NotEvaluated / UnknownCoverage | 搜索集 / 留出集 / 候选 / 成本 / 覆盖率 / 未评价 / 未知原因覆盖 | 搜尋集 / 保留集 / 候選 / 成本 / 覆蓋率 / 未評估 / 未知原因涵蓋 | Search set / Holdout set / Candidate / Cost / Coverage / Not evaluated / Unknown reason coverage |
| Stage / Raw / Derived / Boundary / Foreground / Background / Unknown / Filter | 阶段 / 原始 / 派生 / 边界 / 前景 / 背景 / 未知 / 筛选 | 階段 / 原始 / 衍生 / 邊界 / 前景 / 背景 / 未知 / 篩選 | Stage / Raw / Derived / Boundary / Foreground / Background / Unknown / Filter |
| Field.ComponentKey / Field.FragmentKey / Field.Topology / Field.FilterReasons / Field.ParameterHash / Field.ImageHash / Field.UsedThreshold / Field.StatisticsPixels | 区域键 / 片段键 / 边界状态 / 筛选原因 / 参数标识 / 图像标识 / 实际阈值 / 统计像素数 | 區域鍵 / 片段鍵 / 邊界狀態 / 篩選原因 / 參數識別 / 影像識別 / 實際閾值 / 統計像素數 | Region key / Fragment key / Boundary state / Filter reasons / Parameter identity / Image identity / Actual threshold / Statistics pixels |
| Value.Byte / Value.UInt16 / Value.Real32 / Value.AllowValidExcluded / Value.ExcludeAll | 8位灰度 / 16位无符号灰度 / 32位浮点灰度 / 允许有效免判域支撑 / 排除全部免判域 | 8位灰階 / 16位無號灰階 / 32位浮點灰階 / 允許有效免判區域支撐 / 排除全部免判區域 | 8-bit gray / Unsigned 16-bit gray / 32-bit real gray / Allow valid excluded support / Exclude all ignored regions |
| Value.DiagnosticOnly / Value.AlgorithmFacts / Value.ResponseCandidate / Value.QualifiedBinaryClassification / Value.DocumentStroke | 仅诊断 / 算法事实 / 响应候选 / 已限定二值用途 / 文档笔画 | 僅診斷 / 演算法事實 / 響應候選 / 已限定二值用途 / 文件筆畫 | Diagnostic only / Algorithm facts / Response candidate / Qualified binary use / Document strokes |
| Value.ExternalAlgorithm / Value.Shadow / Value.Advice / Value.ReleasedModel / State.DrainPending / State.ReleasePending / State.Waiting | 外部算法 / 影子结果 / 辅助建议 / 已发布模型 / 等待执行排空 / 等待资源归还 / 等待中 | 外部演算法 / 影子結果 / 輔助建議 / 已發布模型 / 等待執行排空 / 等待資源歸還 / 等待中 | External algorithm / Shadow result / Advice / Released model / Waiting for execution drain / Waiting for resource return / Waiting |
| State.Created / State.Validating / State.Accepted / State.Queued / State.Acquiring | 已创建 / 正在校验 / 已接纳 / 排队中 / 正在读取 | 已建立 / 正在驗證 / 已接納 / 排隊中 / 正在讀取 | Created / Validating / Accepted / Queued / Reading |
| State.Segmenting / State.Morphology / State.Connecting / State.FeatureExtraction | 正在分割 / 正在处理形态 / 正在合并区域 / 正在计算特征 | 正在分割 / 正在處理形態 / 正在合併區域 / 正在計算特徵 | Segmenting / Applying morphology / Merging regions / Computing features |
| State.Draining / State.Drained / State.ResourcesReleased / State.Completed / State.CompletedPartial | 正在排空 / 已排空 / 资源已归还 / 已完成 / 部分完成 | 正在排空 / 已排空 / 資源已歸還 / 已完成 / 部分完成 | Draining / Drained / Resources returned / Completed / Partly completed |
| State.Rejected / State.NotQualified / State.RecoverableError / State.Cancelled / State.TimedOut / State.Failed / State.Unknown | 未接纳 / 不满足用途条件 / 执行中断 / 已取消 / 已超时 / 执行失败 / 状态未知 | 未接納 / 不符合用途條件 / 執行中斷 / 已取消 / 已逾時 / 執行失敗 / 狀態未知 | Rejected / Use conditions not met / Execution interrupted / Cancelled / Timed out / Failed / State unknown |
| Method.FixedIntervals / Method.GlobalMaxSeparability / Method.GlobalSmoothHistogram / Method.DynamicReference / Method.LocalSauvola / Method.RegisteredMask | 固定区间 / 全局最大可分性 / 全局平滑直方图 / 动态参考 / 局部Sauvola / 注册遮罩 | 固定區間 / 全域最大可分性 / 全域平滑直方圖 / 動態參考 / 區域Sauvola / 註冊遮罩 | Fixed intervals / Global maximum separability / Global smoothed histogram / Dynamic reference / Local Sauvola / Registered mask |
| Feature.AreaPixels / Feature.CentroidRow / Feature.CentroidColumn / Feature.BoundingBox / Feature.Perimeter / Feature.Circularity | 像素面积 / 质心行 / 质心列 / 包围盒 / 外轮廓长度 / 圆度 | 像素面積 / 質心行座標 / 質心列座標 / 邊界框 / 外輪廓長度 / 圓度 | Pixel area / Centroid row / Centroid column / Bounding box / Outer contour length / Circularity |
| Feature.HoleAreaPixels / Feature.GrayMean / Feature.GrayMin / Feature.GrayMax / Feature.AreaPhysical / Feature.Boundary | 孔洞面积 / 平均灰度 / 最小灰度 / 最大灰度 / 物理面积 / 离散边界 | 孔洞面積 / 平均灰階 / 最小灰階 / 最大灰階 / 實體面積 / 離散邊界 | Hole area / Mean gray / Minimum gray / Maximum gray / Physical area / Discrete boundary |
| FeatureStatus.Valid / FeatureStatus.Empty / FeatureStatus.InsufficientSupport / FeatureStatus.NotRequested / FeatureStatus.BudgetExceeded / FeatureStatus.NumericError / FeatureStatus.NotApplicable | 有效 / 为空 / 支撑不足 / 未请求 / 超出预算 / 数值错误 / 不适用 | 有效 / 為空 / 支撐不足 / 未請求 / 超出預算 / 數值錯誤 / 不適用 | Valid / Empty / Insufficient support / Not requested / Budget exceeded / Numeric error / Not applicable |
| Filter.Accepted / Filter.Excluded / Filter.Unknown / Completeness.Complete / Completeness.Partial / Completeness.Empty | 已保留 / 已排除 / 无法筛选 / 完整 / 部分 / 为空 | 已保留 / 已排除 / 無法篩選 / 完整 / 部分 / 為空 | Included / Excluded / Filter unavailable / Complete / Partial / Empty |
| Topology.Complete / Topology.TouchesUnknown / Topology.TouchesDomainBoundary / Topology.Incomplete | 已闭合 / 邻接未知 / 触及域边界 / 未闭合 | 已閉合 / 鄰接未知 / 接觸域邊界 / 未閉合 | Closed / Touches unknown / Touches domain edge / Not closed |
| Field.Input / Field.Method / Field.Morphology / Field.Features / Field.Limits / Field.Revision / Field.Unit / Field.Min / Field.Max | 输入 / 方法 / 形态 / 特征 / 资源 / 修订 / 单位 / 下限 / 上限 | 輸入 / 方法 / 形態 / 特徵 / 資源 / 修訂 / 單位 / 下限 / 上限 | Input / Method / Morphology / Features / Resources / Revision / Unit / Minimum / Maximum |
| Field.Polarity / Field.Mode / Field.Offset / Field.Reference / Field.Width / Field.Height / Field.WindowSize / Field.Scale / Field.Range | 极性 / 比较模式 / 差值 / 参考图 / 宽度 / 高度 / 窗口大小 / 系数 / 灰度范围 | 極性 / 比較模式 / 差值 / 參考影像 / 寬度 / 高度 / 視窗大小 / 係數 / 灰階範圍 | Polarity / Comparison mode / Offset / Reference image / Width / Height / Window size / Scale / Gray range |
| Field.Kernel / Field.Radius / Field.Iterations / Field.ObjectMode / Field.ClassKey / Field.Connectivity / Field.Comparison / Field.Combination / Field.Domain | 结构元 / 半径 / 迭代次数 / 对象模式 / 类别 / 邻接 / 比较 / 组合 / 域 | 結構元素 / 半徑 / 迭代次數 / 物件模式 / 類別 / 鄰接 / 比較 / 組合 / 區域 | Kernel / Radius / Iterations / Object mode / Class / Connectivity / Comparison / Combination / Domain |
| Field.MaxPixels / Field.MaxRuns / Field.MaxComponents / Field.MaxEquivalences / Field.MaxWorkingBytes / Field.MaxResultBytes / Field.MaxProjectionBytes | 像素上限 / run上限 / 区域上限 / 等价对上限 / 工作字节上限 / 结果字节上限 / 显示字节上限 | 像素上限 / run上限 / 區域上限 / 等價對上限 / 工作位元組上限 / 結果位元組上限 / 顯示位元組上限 | Pixel limit / Run limit / Region limit / Equivalence limit / Working byte limit / Result byte limit / Display byte limit |
| Field.Timeout / Field.DrainTimeout / Field.CleanupTimeout / Field.MaxParallelTiles / Field.ProgressInterval | 执行时限 / 排空观察时限 / 清理观察时限 / 并发块上限 / 进度间隔 | 執行時限 / 排空觀察時限 / 清理觀察時限 / 並行區塊上限 / 進度間隔 | Execution timeout / Drain wait / Cleanup wait / Parallel tile limit / Progress interval |
| Value.Light / Value.Dark / Value.Equal / Value.NotEqual / Value.Four / Value.Eight / Value.All / Value.Any | 亮响应 / 暗响应 / 区间内 / 区间外 / 四邻接 / 八邻接 / 全部 / 任一 | 亮響應 / 暗響應 / 區間內 / 區間外 / 四鄰接 / 八鄰接 / 全部 / 任一 | Light response / Dark response / Within interval / Outside interval / Four neighbors / Eight neighbors / All / Any |
| Value.Opening / Value.Closing / Value.Erosion / Value.Dilation / Value.Rectangle / Value.Circle / Value.Explicit | 开运算 / 闭运算 / 腐蚀 / 膨胀 / 矩形 / 圆形 / 显式核 | 開運算 / 閉運算 / 侵蝕 / 膨脹 / 矩形 / 圓形 / 明確核心 | Opening / Closing / Erosion / Dilation / Rectangle / Circle / Explicit kernel |
| Value.WholeForegroundSet / Value.PerInputObject / Value.GreaterOrEqual / Value.LessOrEqual / Value.ClosedRange | 前景集合 / 逐输入对象 / 大于等于 / 小于等于 / 闭区间 | 前景集合 / 逐輸入物件 / 大於等於 / 小於等於 / 閉區間 | Foreground set / Per input object / At least / At most / Closed range |
| Unit.PixelArea / Unit.Pixel / Unit.Gray / Unit.Dimensionless / Unit.SquareMillimeter / Unit.Bytes / Unit.Millisecond | 像素² / 像素 / 灰度 / 无量纲 / mm² / 字节 / ms | 像素² / 像素 / 灰階 / 無因次 / mm² / 位元組 / ms | pixel² / pixel / gray / dimensionless / mm² / bytes / ms |
| Unknown.MissingImage / Unknown.InvalidPixel / Unknown.Saturated / Unknown.InsufficientHalo / Unknown.ReferenceUnavailable / Unknown.GrayAmbiguous | 图像缺失 / 无效像素 / 像素饱和 / 邻域不足 / 参考不可用 / 灰度不确定 | 影像缺失 / 無效像素 / 像素飽和 / 鄰域不足 / 參考不可用 / 灰階不確定 | Image missing / Invalid pixel / Saturated pixel / Neighborhood missing / Reference unavailable / Gray ambiguous |
| Unknown.MethodOutOfDomain / Unknown.NotExecuted / Unknown.Cancelled / Unknown.BudgetExceeded / Unknown.NumericError / Unknown.ModelAbstained / Unknown.ColorUndefined | 超出方法适用域 / 未处理 / 已取消 / 超出预算 / 数值错误 / 模型拒识 / 颜色未定义 | 超出方法適用域 / 未處理 / 已取消 / 超出預算 / 數值錯誤 / 模型拒識 / 色彩未定義 | Outside method domain / Not processed / Cancelled / Budget exceeded / Numeric error / Model abstained / Color undefined |
| Error.001 / Error.002 / Error.003 / Error.004 / Error.005 | 参数无效，请修正标记字段 / 输入版本不一致，请重新绑定 / 此方法不可用，请选择已批准方法 / 处理域无效，请检查坐标 / 邻域输入不足，请补齐输入 | 參數無效，請修正標記欄位 / 輸入版本不一致，請重新綁定 / 此方法不可用，請選擇已核准方法 / 處理區域無效，請檢查座標 / 鄰域輸入不足，請補齊輸入 | Invalid parameter; correct marked fields / Input versions differ; bind again / Method unavailable; select an approved method / Invalid domain; check coordinates / Neighborhood missing; provide input |
| Error.006 / Error.007 / Error.008 / Error.009 / Error.010 | 算法执行失败，请查看详情 / 超出预算，请检查范围与资源 / 已取消 / 已超时，正在等待排空 / 数值无效，请检查输入 | 演算法執行失敗，請查看詳情 / 超出預算，請檢查範圍與資源 / 已取消 / 已逾時，正在等待排空 / 數值無效，請檢查輸入 | Algorithm failed; view details / Budget exceeded; check scope and resources / Cancelled / Timed out; waiting for drain / Invalid numeric value; check input |
| Error.011 / Error.012 / Error.013 / Error.014 / Error.015 | 资源尚未归还，请重试清理 / 结果已过期，请重新试算 / 结果不完整，请查看未知域 / 请求已存在，请查询原请求 / 服务已关闭，请等待清理 | 資源尚未歸還，請重試清理 / 結果已過期，請重新試算 / 結果不完整，請查看未知區域 / 請求已存在，請查詢原請求 / 服務已關閉，請等待清理 | Resources still held; retry cleanup / Result stale; preview again / Result incomplete; inspect unknown regions / Request exists; query the original / Service closed; wait for cleanup |
| Error.016 / Error.017 / Error.018 / Error.019 / Error.020 | 请求状态未知，请查询原记录 / 后端结果无效，请停止采用并查看详情 / 图像来源不可用，请重新绑定 / 特征不可用，请查看原因 / 通知中断，请查询当前状态 | 請求狀態未知，請查詢原記錄 / 後端結果無效，請停止採用並查看詳情 / 影像來源不可用，請重新綁定 / 特徵不可用，請查看原因 / 通知中斷，請查詢目前狀態 | Request state unknown; query the original record / Invalid backend result; stop using it and view details / Image source unavailable; bind again / Feature unavailable; view the cause / Notifications interrupted; query current state |
| Tip.Support / Tip.Suggest / Tip.Apply / Tip.Recovery | 窗口需要真实邻域；缺失部分标为未知 / 参数建议需要独立搜索与留出标注；不会修改生产参数 / 仅向宿主请求应用草稿；权限由宿主核对 / 沿原请求清理；资源未归还前不能重建实例 | 視窗需要真實鄰域；缺失部分標為未知 / 參數建議需要獨立搜尋與保留標註；不會修改生產參數 / 僅向宿主請求套用草稿；權限由宿主核對 / 沿原請求清理；資源未歸還前不能重建實例 | Window requires real neighbors; missing support stays unknown / Suggestions need separate search and holdout labels; production parameters stay frozen / Request draft application from the host; the host checks permission / Clean up the original request; keep the instance until resources return |

RequiredKeys为本表逐个键加§13.3原键的并集，Ordinal排序。API/参数字段到上述键显式绑定在同WPF定义，不从翻译回写参数；资源schema新增键要升文本schema而非改请求ContractVersion。未列的Host事实文字来自Host的完整快照并验证，不把工艺/物料名称塞入模块字典。键/值错配、缺键或空字符串是资源错误，在原资源上显示简短诊断并拒绝切换，原算法/lease不受影响。

## 14. 正常、边界和失败案例

全部数值是合成软件断言，不是客户工艺值；完整性、Data 与事件按 §§7–10 判定，不因表内简写忽略资源门。

| ID / 场景 | 冻结输入与操作 | 期望结果 |
|---|---|---|
| N01 固定区间 | §12 的 3×3 Byte，中心15、其它0，[10,20] | F=中心，B面积8，U空；完整组件面积1、质心(1,1)、bbox=(1,1,1,1)，Completed |
| N02 动态等号 | g=[95,100,105]、独立 L=100、d=5，四次新 operation | Light={105}、Dark={95}、Equal=全集、NotEqual=空；非相反极性拼接，回执含参考修订 |
| N03 全局阈值 | Byte 与 UInt16 双峰，固定统计域，两种 GlobalSpec 分别执行 | 各记实际 T/N；g=T 只属于 Light、不属于 Dark；整图与多 tile 同域，不逐 tile Otsu |
| N04 Sauvola | Byte/UInt16 细笔画，DocumentStroke、窗口15、k/R显式、真实halo | 等价官方反相语义；厚材料用途/Real32拒绝，不退为 Dynamic |
| N05 颜色与mask | 同格注册Hue跨零两区间；灰色ColorUndefined；Shadow/Advice外部mask | 未定义Hue为U，mask错类别拒绝；Shadow/Advice即使Completed也仅DiagnosticOnly |
| B01 空D | 有效descriptor，D空 | 纯Validate后绕过backend.Plan/Execute及源借用，Completed+Empty，组件0、无假质心 |
| B02 全/空前景 | D置于更大已支持W内，完整分类；全前景另测D裁边 | 空F为ForegroundEmpty=true；全F仍保留事实，若裁边则组件Partial/计数null |
| B03 4/8对角 | (1,1)/(2,2)两F像素，周围已知B | Four为2、Eight为1；孔洞背景对偶邻接独立校验 |
| B04 跨缝/后筛选 | 一组件跨四tile角；左右各3像素，面积下限5 | 四角等价完备；合并成6才筛选；halo不重复面积，不用局部标签作稳定key |
| B05 复合支撑 | 3×3均值后3×3 closing，W中注入缺口 | 累计halo=3；逐步依赖域递推，U不变B；Added/Removed/SupportLost各自正确 |
| B06 整数端点 | Byte闭区间端点10.5 | 接纳前Rejected/SEG-001，不取整；Real32有限端点按浮点闭区间 |
| B07 形态集合 | 孤点/细桥/小孔；WholeForegroundSet与Mask.PerInputObject | 顺序/对象语义符合26.05；重叠去重，raw保留，孔洞变化为派生事实 |
| B08 筛选缺值 | 完整面积12/8，两者全Excluded；缺Scale请求AreaPhysical筛选 | 原F/组件数不改；缺值不是0，All/Any三值逻辑，原因SEG-019 |
| B09 触未知/裁边 | F,U,F；已知F在D边而W外未知 | 片段面积/bbox可读，ComponentKey/全局count=null；边界/孔洞不可计算，CompletedPartial |
| F01 非法参数/版本 | min>max、NaN、偶核、重叠D/I、错格/参考revision | Rejected/SEG-001/002/004；backend dispatch=0 |
| F02 无用途资格 | 单峰/多峰/低对比/极稀响应无冻结资格；饱和比例超门 | NotQualified，不调用global native；不会自动换方法 |
| F03 容量/预算 | 接纳前不足；或接纳后累计runs/组件超限 | 前者Rejected/SEG-007、无dispatch；后者封存可校验partial（若无有效分类则NotQualified），不截前N再报全集；若无法封存合法partial则Failed |
| F04 native异常 | 原请求校验合法，HALCON抛异常 | SEG-006；临时IO类RecoverableError、不可恢复算术/非法输出Failed；先排空/确认释放，Data仅合法诊断 |
| F05 取消/超时 | 阈值/接缝/特征阶段及native闩锁中触发 | 先DeadlineExceeded/CancelRequested；未返DrainPending、无终态；真实排空/归还后Cancelled/TimedOut，Data=null |
| F06 释放恢复 | 第一次释放异常、第二次no-op、第三次Owner确认；独立cleanup token | ReleasePending，不退款/终态；同ticket RecoverAsync后仅一次ResourcesReleased/Terminal，不重算 |
| F07 重复/未知 | 同ID同hash并发Start/Execute；同ID不同完整RequestHash；错InstanceId | 一次执行；SEG-014原ticket无第二Terminal/lease；内容冲突SEG-002；Query未知哨兵SEG-016 |
| F08 转交与关闭 | scope结果转交失败/成功；Close时消费者仍持Data | 失败不暴露Data、不丢scope Owner；成功无账空窗；Close不抢lease，报告outstanding |
| F09 来源中断 | OpenTile缺测/失败且已有借用 | 原Owner登记可恢复；无伪零图、无替换帧；未处理域U/MissingImage+SEG-018 |
| F10 后端伪成功 | F/B交叠、run越界、计数错、特征错单位 | SEG-017/Failed；隔离输出，不转交Data；资源仍按原Owner释放 |
| F11 迟到/回退 | A→B→A视图代次；旧manifest结果与新实例ticket | 旧回调只退投影租约，不覆盖新视图；不能解析到新实例或重算历史 |
| F12 Host消费异常 | 已知Completed且Data取得后ReadComponents/consume分别抛异常；Release另抛异常 | KnownResult仍Completed，CallError与CleanupError分别保存；finally必尝试原Data.Release/独占service.Close；未确认归还同一Data/Owner保留，不提前退款 |
| F13 拒绝与在途reservation | Accepted=false+原ticket：Reserve闩锁未返DrainPending，或已返但释放失败ReleasePending | 不直接return/伪Rejected；同ticket有界Query/Wait/Recover/Close；未派发backend，Execute/Recover次数均0；晚返只清理，真归还后唯一Rejected终态 |
| F14 有限观察与原Owner | Wait被取消、Recover/Release/Close预算到期或抛异常；Close期间迟到Data；恢复槽满 | 每次有界，无重新Start/新scope/新实例；已知结果与IoClosed独立。Start前槽满dispatch=0；退出观察前原Owner强引用/同slot确认，未闭合不清槽/Dispose端口；Close已闭合但结果Unknown不能伪造结果 |

## 14A. 场景驱动架构复审

本节只定义整条操作链断言，复用 §14 的 fixture，不重复创建证据或把模拟称为现场结果。

| ID / 场景 | 调用与责任链 | 可判定断言与恢复 |
|---|---|---|
| S01 无UI正常 | 宿主冻结request→Validate→Start→Wait/Query→消费→Release | N01–N05只输出算法/诊断，无设备/数据库/质量写入；两个组合根均成立 |
| S02 空/缺测/裁边 | Empty走纯值；缺tile保留D→U→诊断片段 | B01/B09/F09分别区分空任务/无资格/空前景/组件不闭；不缩D或拼旧局部标签 |
| S03 资格及备用 | 原operation NotQualified→宿主决策表→新OperationId/ParameterRevision+FallbackFrom | F02无隐式切换；原失败保留，新方法完整再校验，不降质量门 |
| S04 参考/颜色/学习 | 参考与标量注册由宿主；模型训练推理在外部→冻结mask→Core | 错格接纳前拒绝；无未声明转换/训练；Shadow/Advice仅DiagnosticOnly |
| S05 非法/重复输入 | 纯校验、请求身份与有限登记→Start回执 | F01/F07无native；重复/冲突不发原ticket第二终态；Execute重复立即无Data回执 |
| S06 超大图/并发 | Profile/Plan→预留→有界队列→tile/接缝→后筛选 | B04/B05/F03；接缝协调在adapter统一路径；队列满接纳前Rejected，不拆D逃预算；两实例隔离线程设置 |
| S07 取消/超时 | 原CTS→停派发→native闩锁→Drain→Release→原拟终态 | F05/F06；Wait取消只结束等待，Close取消实例作业；恢复不计算且保留ticket/Owner |
| S08 资源转交/Host收尾 | scope charge→验证输出→TransferResult→消费try/finally→原lease归还→独占Close | F08/F12–F14；所有时点账守恒；Accepted=false pending沿原ticket；消费异常不改KnownResult；有限观察未闭合先确认原恢复槽责任，Close不抢结果 |
| S09 UI共享关闭 | 草稿/权限/代次→Start→有界投影；Detach只等自身ticket | F11及§13；共享服务另一消费者继续，独占服务才Close；隐藏窗口不等于释放 |
| S10 持久化失败 | 模块结果→宿主事务/证据回执；模块不提交 | 宿主用原计算身份重试证据；参数变化新operation，不把未保存候选称生产事实 |
| S11 升级/回退 | 停接纳→旧版本Close/结果lease处置→新manifest→Replay差异检查 | 旧资源未确认禁止重用；合同/单位/三态不等价阻断混用；保持旧包可回退 |
| S12 第二消费者/长稳 | 两个独立组合根→循环执行/释放/故障恢复→周期排空 | 无PCB类型/静态可变状态；账、lease、handle无无界增长，失败按原Owner恢复 |

共用不变量：所有参数来自不可变请求；部分结果同时具备已知域/U/原因/完整性；计算重试与备用用新operation，资源恢复沿原ticket；AI、UI、日志和持久化投影不获得生产事实或设备权威。

## 15. 测试矩阵、执行命令与验收断言

以下是拟执行测试，当前只修指导。Core.Tests 固定 Microsoft.NET.Sdk / net10.0 / OutputType=Exe，仅 ProjectReference Core 和 BCL；Fixtures 下两个组合根共用确定性断言、可推进TimeProvider及异步闩锁，不选待定测试包。入口逐条执行 §14/14A 中适用Core的断言，任一失败/未完/必需项跳过返回非零并列ID；无native的模拟不冒称算法Golden。

获准并创建工程后仅执行绑定路径：

```text
dotnet build src/Modules/segmentation/Asun.Modules.Segmentation.Core/Asun.Modules.Segmentation.Core.csproj -c Release
dotnet run --project tests/Modules/segmentation/Asun.Modules.Segmentation.Core.Tests/Asun.Modules.Segmentation.Core.Tests.csproj -c Release
```

Core harness 每例截止10秒、全进程外层截止120秒（测试控制值，不是生产Profile）；可控native闩锁必在finally解除并核释放，超时不可返回成功。dotnet test不执行此Exe，空执行不算验证。

| 切片/层 | 必测ID/具体断言 | 适用门 |
|---|---|---|
| 纯值/身份 SG-C1 | F01、B06：端点/枚举/域/hash；canonical重复run拒绝、空集合/NaN/−0；请求字段变更影响hash、token不参与；B01 空D不调用backend | 独立BCL构建运行 |
| 生命周期/账 SG-C2 | F03/F05–F10/F12–F14/S05/S07/S08：重复并发一次接纳；Wait取消不执行取消；Queued Timeout；未知ticket；pre-admission Reserve/OpenTile I/O晚返仅清理、scope释放失败同ticket可恢复；Host读取/消费异常不跳Release/Close、独立结果知识/IoClosed及原Owner确认；result转交成功/失败与关闭；callback异常/no-op不能退款；一ticket一终态 | 闩锁/时钟/Owner账反例；不创建厂商对象 |
| 支撑/接缝输出校验 SG-C3 | B03–B09/F10：4/8四tile角，局部3+3合并6后过滤；F,U,F不报2物体；3×3均值+closing halo3；All/Any缺值；裁边与分类完整分开；checkerboard累计上限 | fixture返回冻结tile三态，Core核组件是否漏并跨缝邻接及统计/支撑，不写替代threshold/形态/特征 |
| 参数建议 SG-C4 | 有效真值FP/FN/U成本；候选hash/fixture排序；search/holdout不交；同分破序；搜索不全不排名；留出失败/预算/取消停止；每次Data确认释放 | 有界候选×fixture次数/资源；不改变生产request |
| AsunImage SG-A1 | N01–N05、B03–B07、F04/F05/F06：26.05原native与tile像素等价、等号、Sauvola反相、实际kernel、dual邻接、contlength/circularity/孔洞、超大组件拒识、tsp异常恢复/max_connection只读 | 真cv2执行；测试端口保留故障注入；不可用simulate替代native |
| WPF SG-U1 | §13、F11/S09：三语/当前DPI固定1920×1080、UIA/键盘、长字串、权限撤回、代次、共享Detach、投影上限/分页 | 最小STA窗口真实WPF；测试为net10.0-windows/Exe，仅绑定Core/WPF和本机25.2.3，不下载包 |
| 集成/发布 SG-I1 | 两真实宿主/各自Profile、Golden/Replay、故障恢复、§16性能、版本兼容/回退、结果Owner资源账 | 正式消费者与产品Contract映射，非模拟/截图资格 |

SG-A1测试工程为net10.0/Exe，只引用Core、adapter及其既定AsunImage依赖；SG-U1为STA Exe。各自 dotnet build 对应 §Core binding 的唯一代码工程、dotnet run --project 对应唯一测试工程 -c Release；native测试每例30秒/外层300秒，WPF任务每例60秒/外层600秒，进程超时/未知资源非零且保留原Owner诊断。这些截止值仅控制软件测试进程，不改变native不可强制中断的生产释放语义。只有获准相关切片才运行。真实材料、客户阈值、计量和现场验收在SG-I1另外绑定，不能以两种同机台页面代替第二消费者。

### 15.1 全批准范围的定向补充断言（本轮只定义，未运行）

复用§14/14A与A.5所有有效fixture/身份向量，不重复生成报告或重新审算。下列只覆盖本轮实际设计增量，未来分别放已有规划Adapter.Tests/Wpf.Tests工程；普通实现者只按输入与断言写测试，不另选算法。

| ID / 层 | 完整合成反例输入 | 可判定预期 |
|---|---|---|
| SG-A15 图像codec | UInt16、2×2、stride=6，字节`01 00 00 01 aa bb ff 0f 02 00 cc dd`，声明0..4095、Intervals=[256,4095]、Full域；另短length=9与stride=3 | tight为`01 00 00 01 ff 0f 02 00`，F={(0,1),(1,0)}，8邻接1片、面积2，padding不入像素；短源/短stride按SEG-018/017拒采用且原lease归还；不会交换行列或端序 |
| SG-A16 Real/未知 | Real32 1×3，值[0,NaN,1]，端点[0.5,1]，合法descriptor、源Valid=Full、Missing空 | 读取发现NaN位置U/NumericError，F只最后像素、B只首像素；均值/Sauvola等邻域缺支撑，NaN不能补0参与资格；Shape/完整性沿未知触边规则，不伪组件全数 |
| SG-A17 位移/RLE/上限 | 父图Width=10000000003/Height=3，tile原点(row=0,column=10000000000)，本地3×3与N01且只借该tile，不分配完整父图；另跨tile长组件bbox宽超过MaxReconstructionPixels及本地尺寸限制，但合法全局runs | native输入坐标仍0..2，输出中心(row=1,column=10000000001)；面积1/bbox精确，不把父long转int；超重建组件像素特征有效，Perimeter/Hole/Boundary等不可用，不求tile周长和，不截全集 |
| SG-A18 真值支撑/线程 | N02/B05/B07，显式负坐标对称核；native中抛异常/取消，两个不同Connectivity实例并发 | halo=3，实际kernel runs绑定；V_j严格依赖，原Unknown原因保留；get/set/恢复同worker且无await，原tsp设置恢复、全局max_connection未写；image pin在真实调用退出后才解除 |
| SG-A19 类投影/空标签 | ClassA mask F={(1,1)}，ClassB F={(1,2)}；两者共有U={(0,0)}，独立op/ClassKey且同格；无标注Suggest | A/B分开事实，另类已确认非A才是A的B，U仍U；错ClassKey接纳前拒绝；显式分割可运行，Suggest InsufficientEvidence且不Start任何评价 |
| SG-U15 真装配 | §13.1.2双STA Host，故意省Lifetime、另Control.Presentation或schema不完整；合法组随后Bind/Attach/Commit | 非法组在源/Dispatcher/native前拒绝，未出现可见成功；合法组原Commit Task与GetPresentations OriginalCommit同一引用/同binding，无伪receipt；独立窗口核原图中心/身份/未知层，非模拟VisibleConfirmed |
| SG-U16 取消与晚归还 | 原Acquire闩锁延迟到Unbind观察到期；另失败Value仍携PresenterLease，原Return第一次Pending | Detach/Unbind返回Waiting，root/桥copy/原Task/lease仍持有；解除闩锁后同Owner Revoke/Return，有限观察耗尽仍不伪Drained，不发第二Bind/Root、不终止另一Host |
| SG-U17 资源/分页/代次 | 完整内置三语及完整fr-FR扩展包；en-US包删Seg.Error.011；组件129条、page128，Image/generation A→B→A；8192byte投影上限及零画布 | 三包必需键完全覆盖/Name HelpText已翻译；双参UpdateContext原子切fr-FR，缺键/语言错不改context/代次/包；单参切新扩展Culture拒绝；第2页1项，排序/筛选标当前页；第一代A迟到不覆盖；超投影可见LOD，零画布不借图/不伪可见 |
| SG-U20 源生产者限定消费 | A/B分别Create sourcePorts且Register自己的原3×3已发布帧；sourceBindingId同内容/异内容；另一root/epoch/consumer；两个entry已占且旧Read/Return闩锁未返；同producer新revision更新后Remove旧entry | session所有代Options.Frames/Coordinates引用同实例，原图字节不变、mask不替原图；同ID同内容幂等/异内容拒绝，交叉实例/未登记consumer不得读取；Register不读源，容量满/旧entry活跃拒新或拒Remove且保原Owner/Task/lease；晚到归还确认后才Remove/由发布Owner Retire，无第二Read/Return/新工厂；bbox选择/局部Clear仍保source及其它层 |
| SG-U19 导航/只读/重用 | B外层先运行N01 mask并AdoptReadOnlyResult；投影ComponentHits原key，另无hit/多候选/Truncated；CanPreview=false；Ctrl+0；普通Clear→ClearAndDrain→同代再次SetOverlay；Detach时另一个旧代仍Pending | 只读显示原三态/组件且分页可用，Start计数不增加；选中层只回原key，多候选需明确选，页外不假称不存在；重复接收不增加lease，失败接收由Host持Owner；Fit转发同session原SetView task，零画布不派发；普通清图不封桥，Detach封门且两代未闭不能Drained；先清copy再释放同Data |
| SG-U18 Apply/建议/权限 | Apply委托真实task暂停后撤权、Detach；Suggestion当前评价ResultRelease失败 | Apply结果未知保原task且禁止重发；撤权阻新命令不丢原事务；建议同ticket恢复前不执行下一评价，显示Search/Holdout分别且不换冠军；资源未知不得“应用成功” |

SG-U19所用mask取N01相同3×3/F={(1,1)}/B其余8像素/无U，方法RegisteredMask、ClassKey明确由测试Host注册；不把scalar源冒充mask。SG-A15/16的F/B/U断言是算法域事实，组件是否完整仍按W/D闭合条件；需要拓扑测试时将D嵌入更大的已知B支撑域，不把小图边上的对角像素误称完整物体。UI键盘/三语/当前DPI与截图的职责沿§13；这里只定义计划，不报告通过。

## 16. 性能预算与资源记录

每个消费者冻结 BenchmarkProfile（外部输入，不增模块生产DTO）：输入/hash、Core/adapter/HALCON/AsunImage/OS/硬件版本、方法/参数/资格、冷/热预热及测量数量/最低有效n、并发、有限deadline、队列/工作/结果/投影/源槽上限、吞吐窗口、阈值来源和失败规则。统计定义唯一复用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，不复制或更换分位算法。目标未采纳为TargetPending/NotEvaluated，允许诊断测量，不宣称达标。

| 必须冻结的负载桶 | 实际输入/尺寸与反例 |
|---|---|
| 标量/方法 | Byte/UInt16/Real32适用方法；固定两端点、全局双峰/单峰/多峰/低对比/稀响应/饱和、独立参考/均值/Sauvola、注册Hue/Shadow mask；每桶实际W×H/hash，不用缩略图代替 |
| 尺寸/域 | profile至少含最小支持窗、单native整域、2×2 tile跨角、实际最大批准父图/最大tile；D/W比例和累计halo显式，缺tile/未知缝/裁边另桶 |
| 密度/拓扑 | 空F、完整高密F、Four/Eight棋盘（最坏runs/组件）、跨多tile长组件、孔洞/细桥/粘连；超重建上限明确FeatureUnavailable |
| 复合支持 | 3×3均值+3×3 closing的halo3，多个迭代累计，真实图边/支撑洞和I上下文策略；同时测正确U面积 |
| 资源/并发 | 1与Profile最大active/parallel，队列满，最小依赖工作集不足，暖池复用，result长期持有/容量满，转交失败/释放未知 |
| 恢复/长稳 | 每阶段取消/native中deadline，DrainPending/ReleasePending，源中断、旧回调、连续执行释放、周期Close与版本切换 |

单调计时测 Validate/Plan/预留、源借用、背景/threshold、形态、局部连接、接缝、重建/特征、输出校验/转交、队列等待和接纳→ResourcesReleased；另测 cancel→native真实返回、Drain/执行归还、消费者持有Data→确认释放。性能报告只在已有实现/真实测量后写入其既有测试产物；本轮不造文件/数据。

资源测点为每次分配前/后、tile/stage边界、转交前/后、终态与lease释放：managed/native峰值与不可测null、真实Owner账及borrow逻辑footprint、runs/临时Region/组件/等价对、高水位队列与retained结果、结果/投影字节。核账合计与Scope不重复物理计费；未知释放/删失不丢样本且阻断该性能门。零候选、NotQualified、partial和失败独立统计；显示LOD、截前N、逐tile重置预算不能算优化。外层测试进程结束或模拟fixture通过不证明真实P95/P99、长稳或客户达标。

### 16.1 Adapter/UI可执行软件负载与判据

Core冷/热/次数复用A.5。Adapter与UI另用同一批准软件输入Profile，客户目标为空时只NotEvaluated，不拿合成容量称达标。native计算冷1、预热2、测20、有效n至少20；WPF实际可见端到端冷1/预热2/测20，三语各同固定1920×1080物理视口和当前DPI，串行执行；未知排空/必需项跳过为失败，不剔除超时/失败样本。截止沿§15的native单例30秒/外层300秒，UI60秒/外层600秒；长稳软件序列明确100次Execute→消费→释放，每10次Close旧实例并新InstanceId，新实例操作身份按A.5规则重新绑定，未闭合则终止测量并保原Owner，不能为赶截止强杀后冒充释放。

固定负载桶：N01原3×3/SG-A15的2×2 codec；8×8 Byte棋盘（(row+col)%2=0为15、否则0），D=[1..6]²/W=Full、单8×8与4块4×4两计划、Four/Eight分别；32×32 Byte以[12..19]²为15、其余0，D=[3..28]²/W=Full，DynamicReference的Reference=null、MeanWindow3×3、Mode=Light、Offset=5，再closing矩形3×3/Iterations=1，单32tile与4块16tile真实halo=3；大图4096×4096 Byte以[1536..2559]²为15、其余0，D=[1..4094]²/W=Full、256×256 cores、Fixed[10,20]；另同尺寸棋盘仅作runs/组件预算拒识与partial路径，不假定必能全量完成。未另列的Fixed桶统一[10,20]，RegisteredMask桶直接用同F/B/U；各桶处理默认显式WholeForegroundSet、FeatureSet=[AreaPixels,CentroidRow,CentroidColumn,BoundingBox]、无筛选/空形态，32×32桶除所列closing外为空。Gray/Boundary/Perimeter/Circularity/HoleArea特征分别作开启变体，不把不同FeatureSet混测；Scale=null不测物理精度，Connectivity除棋盘分别Four/Eight外固定Eight。所有像素公式是冻结合成输入，实际source.sha按原编码完整字节计算并登记；无标注时不测推荐泛化。mask/Gray feature开启与关闭各测SourceBorrowCount，只有所请求路线才读图。

每桶Limits显式MaxPixels=父图像素数、MaxRuns=1048576、MaxComponents=262144、MaxEquivalences=1048576、MaxWorkingBytes=536870912、MaxResultBytes=134217728、MaxProjectionBytes=8192、MaxParallelTiles=1，Timeout=10秒、Drain/Cleanup=2秒、Progress=10ms；Runtime Active1/Queue1/Retained2/Tombstones4096/Retention1秒/Event32，sourceSlots=2。均标Synthetic，超过上限按固定拒绝/Partial/FeatureStatus，不能扩大到“测试通过”。NativeFootprint coefficients及backend能力来自本实现测得绑定的Profile，缺失的组合明确NotEvaluated并阻其native性能门；本方Owner仍须采集，非客户外部门。UI显示负载另沿§13.1.2已明64MiB/UI及root容量，上述工作账不重复计source/viewport物理allocation。

正确性门：Fixed/mask/RLE/计数/支持域/身份必须exact；浮点特征以同源单native整Region为基准，软件投影允许误差`abs(a-b)≤1e-12*max(1,abs(a),abs(b))`（仅计算一致性，不是物理精度）。若HALCON该特征无法满足，保存误差/拒绝该等价门并修实现/经说明修该技术公差，不静默调宽。Area/BoundingBox/Boundary/holes用离散exact，Circularity/Perimeter/Gray用上式；不得拿不同定义的4πA/P²作为基准。正确性、lease/账守恒、唯一终态、取消后真实排空、同binding/原Task和资源键完整是硬断言，性能采样不覆盖它们。时延/吞吐/物理精度客户数值仍由§20.3的具体Owner采纳，P50/P95/P99唯一算法沿DEV-GOV-010。

## 17. 可观测性与证据

每个 operation 输出结构化 trace：`OperationId`、`RequestRevision`、输入快照/hash、域摘要、方法/参数/算法/adapter/HALCON 版本、路线、阶段时间、资源计数、质量门、错误码、组件完整性和输入/诊断 `EvidenceRef`。模块只返回引用，不创建或持久化证据；宿主负责写入状态和持久化回执。日志不得记录完整图像像素或敏感产品数据，除非宿主显式授予证据策略。

固定诊断计数（同现有sink输出，不增加模块存储）：

- `segmentation.operations.total{method,state}`
- `segmentation.stage.duration_ms{stage}`
- `segmentation.unknown_pixels{reason}`
- `segmentation.components.count`、`segmentation.components.incomplete`
- `segmentation.resource.peak_bytes`、`segmentation.queue.depth`
- `segmentation.cancel.drain_ms`、`segmentation.stale_events.total`

诊断事件是只读证据，不是质量事实；未知回执应由调用方沿其原 operation 查询，模块不重算、不重拍、不提交。

## 18. 发布、回退和第二消费者

Core、adapter、可选WPF是三个独立DLL/版本边界；Core只依赖BCL，adapter依赖Core/既定AsunImage，WPF依赖Core/本机25.2.3与宿主公开端口。包中不带平台页面、PCB类型、私有表或SDK handle。发布记录沿现有交付流程绑定ContractVersion/AlgorithmRevision/adapter版本、公开依赖、错误码、支持矩阵、测试/Golden引用和Profile，不为此新增重复manifest权威。

### 18.1 两个消费者的验收

| 消费者与唯一组合根 | 输入/独立解释 | 接收要求 |
|---|---|---|
| 外观候选宿主；Core.Tests/Fixtures/ConsoleHost为软件样例 | 自有灰度快照/ROI/Profile→Fixed/Global/Dynamic；宿主解释制程/目标，模块不知PCB | 只引用Core的模拟接入先核合同；SG-I1改接真实adapter+其代表样本/Profile，冻结算法/资源/错误，不能把Console fixture称产品验收 |
| 平台外通用表面区域工具；Core.Tests/Fixtures/SurfaceToolHost为软件样例 | 自有注册颜色/外部mask、自有ROI与参数资产→同服务；与第一消费者不同组合根/状态/权限 | 不引用PCB/Shell/私有表；单独注入Owner资源账/语言/viewport；同等取消恢复/未知/结果寿命断言，真实样本与Profile另采纳 |

这两个宿主是明确复用计划及可执行软件接入样例；真实消费者包、客户输入与验收Owner尚待集成任务绑定，不伪称已存在/接入。独立控件验收还须证明只挂接公开session即可使用，不依赖隐藏窗口初始化。

### 18.2 升级与回退

宿主选择完整Core/adapter/WPF版本组合；停止旧实例接纳→Close→确认执行资源及自行处置结果lease→Replay/兼容检查→换实例/InstanceId。若旧实例DrainPending/ReleasePending，保留旧Owner和资源，禁止“重启worker”掩盖它。新算法不重写历史receipt/hash；新major输出不可与旧单位/三态/连接语义混用。保留上一版本包、参数与样本证据；回退重复以上顺序，不用反序列化成功当语义兼容。开发/模拟接入、真实算法与产品资格分别验收。

## 19. 实施切片与六项准备接收

本轮0.2.3-prep只完善并自审指导，不创建工程。当前全批准范围的可决定软件设计已闭合，定位与剩余门见§20.3；不以历史Core接收代替全模块检查。2026-10-10已接收范围与§12收尾保持；2026-10-11主控回读§4.2/A.3/A.4/A.5、两无UI Host根与§12.2恢复，按§19.1六项逐片接收SG-C1/C2/C3/C4为`ModuleCoreImplementationReady`（仅文档准备）。§11.3后端预算/构造的SG-A1公开装配及§13.1.1双STA接线的SG-U1装配/Owner恢复增量限定内容接收；未执行构建/运行，不授予整模块Ready。

DEV-GOV-010 §3.1 六项准备定位：

| 六项条件 | 本文冻结位置 | 既有Core文档接收结论（本轮保持） |
|---|---|---|
| 1 职责/非目标/第二消费者 | §§1–3、12、18.1 | 已明确的相关 Core/适配规格已接收；两个真实消费者接线仍另验 |
| 2 唯一API/参数/状态/Owner/版本 | §§4–11、13.1.1、A.1–A.5 | v0.2已接收规格保持；0.2.2构造/Owner接线与Golden已接收，§6/7算法及A.1编码不改；平台Schema不冒充模块API |
| 3 无UI最小宿主/端口 | Core binding、§§4.2/8/12.1–12.2、A.3/A.5 | 已接收Host finally/同ticket恢复保持；三个Simulator和双Host根装配已获0.2.2接收；工程未创建/运行 |
| 4 正常/边界/错误/重复/并发/关闭/回退断言 | §§14/14A/15 | F12–F14及两轮有限恢复的文档断言已接收；Exe/闩锁及其他真实验证未执行 |
| 5 Benchmark维度/测点/预算/阈值来源 | §§5/10/16、A.5 | Core有限合成Profile/次数/测点规格已接收；真实客户目标另绑，不作为纯Core规格欠账或已测成绩 |
| 6 唯一工程/测试/允许禁止路径/调用/后续门 | Core binding、§§12/15/19/20 | 已写；权威代码仓库/分支待实现开工绑定 |

### 19.1 SG-C1～C4 六项实际走查

下表记录主控按 DEV-GOV-010 §3.1 对四个纯托管 Core/Simulator 切片的六项逐片接收结论：SG-C1/C2/C3/C4均为`ModuleCoreImplementationReady`（仅文档准备）。此接收不等于实现派发、构建/运行通过或整模块Ready；真实HALCON/WPF、正式消费者和生产资格仍按保留门处理。

| 切片 | 1 职责/复用 | 2 API/状态/Owner/版本 | 3 无UI构造/端口 | 4 断言/异常/恢复 | 5 Benchmark/资源 | 6 工程/测试/调用 | 结论 |
|---|---|---|---|---|---|---|---|
| SG-C1 纯校验、RLE、身份 | §1–4；ConsoleHost + SurfaceToolHost为两个组合根 | §4、A.1/A.2；`seg-request-v2`/`seg-parameters-v2`，错误/版本/资源身份已冻结 | Core只依赖BCL；构造边界、ImmutableArray冻结和 `Validate` 见§4.2 | A.5的SG-ID-01–04及F01/B06/B01；非法run/NaN/Overflow拒绝，−0编码为+0，空D短路Completed/Empty；无资源副作用 | §16/A.5的软件Profile与Validate/Plan测点；RLE/元数据按MaxRuns/MaxProjectionBytes，有界计账 | Core.csproj、Core.Tests Exe、SG-C1命令见Core binding/§15；无native/UI | **ModuleCoreImplementationReady（仅文档准备，主控已接收）** |
| SG-C2 状态、Simulator、两Host | 同一Core服务，两组合根各自Owner/InstanceId；不引入产品事实 | §8、A.2/A.3；Start/Wait/Query/Recover/Drain/Close、lease与Owner/Instance隔离 | §4.2/A.5三个Simulator构造/双Host装配；§12.2完整收尾和原Owner槽；无UI/BCL | F03/F05–F14、S05/S07/S08；重复、取消、在途reservation、消费异常、恢复/no-op释放和唯一Terminal | §16/A.5的软件Profile及排队/预留/转交/释放/Drain/长稳测点；Managed/native不可测记Unknown | SG-C2使用同一Core.Tests Exe和两Fixtures；命令§15；Simulator不执行视觉算法 | **ModuleCoreImplementationReady（仅文档准备，主控已接收）** |
| SG-C3 支撑、接缝、托管投影 | Core只校验/协调冻结投影，不复制threshold/形态/feature实现；可被两个Host复用 | §3、§6.6、§7、A.2；D/I/W/U、4/8、Component/Feature/Filter与Partial一致 | `BackendOutput` identity/Profile匹配；FrozenProjectionBackend返回冻结Stages/Components；Core校验三态/组件/三值筛选 | B03–B09/F10；跨tile四角、F,U,F、halo递推、伪成功、缺值和裁边断言；异常沿C2收尾 | §16/A.5的软件Profile及checkerboard/runs/组件/等价对/MaxProjectionBytes；整图/tile真实等价属于A1 | SG-C3在Core.Tests冻结输出断言；无HALCON、无第二生产算法；命令§15 | **ModuleCoreImplementationReady（仅文档准备，主控已接收）** |
| SG-C4 参数建议 | 只做有限、可解释的候选评价；不训练、不改生产参数；两个Host可提供候选fixture | §6.7、A.4；SuggestionId/候选/真值/权重/排序/Partial/InsufficientEvidence已冻结 | A.4/A.5的SuggestionRequest、四图source/八case构造及task/Owner进入同一service；评价身份域分隔、共享一个active名额和同一账 | SG-C4断言候选hash/fixture排序、search/holdout隔离、Data释放、取消/预算和重复SuggestionId | §16/A.5的2×2+2×2上限及Profile、临时Data/资源逐次归还、P50/P95/P99与未知资源规则 | Core.Tests Exe中独立Suggestion fixtures；不依赖训练包/数据库/UI；命令§15 | **ModuleCoreImplementationReady（仅文档准备，主控已接收）** |

四个切片共同的接收范围：Core/Simulator端口、两个无UI Host、RLE/请求身份、状态/结果lease/资源恢复和拟执行测试/Profile定位已由主控接收；SG-A1公开装配与SG-U1装配/Owner恢复增量仅限定内容接收，不等同这两片完整准入。本页未执行构建或运行，不能写“测试通过”。共同保留门：真实消费者 Contract/State/Owner 映射，SG-A1 的真实 cv2/HALCON 26.05 调用与 native footprint/Golden，SG-U1 的真实 WPF/UIA/DevExpress 25.2.3，SG-I1 的真实样本、Replay/性能和现场资格。

| 切片与真实消费方 | 允许实现责任/前置 | 本切片验收及保留门 |
|---|---|---|
| SG-C1：两最小Host | Core/Tests内API、纯校验/身份/RLE/空D；六项文档准备已接收；获明确实现任务并绑定仓库/分支后创建唯一工程 | §15 SG-C1 build/run；不接HALCON、不写生产threshold；真实仓库/分支先绑定 |
| SG-C2：同Host的异步调用 | SG-C1后，状态/有限队列/事件/结果store/Owner账/恢复，端口仅fixture | §15 SG-C2反例；公开端口不依赖产品资源authority，真实adapter/集成另门 |
| SG-C3：tile候选消费 | SG-C2后，支撑域/接缝及托管组件投影校验/三值筛选；不复制视觉算法 | §15 SG-C3；native特征用adapter值，整图/tile真实等价仍SG-A1 |
| SG-C4：工程调参消费 | SG-C2/C3后，同执行管线的有限候选/标注评价，生产无副作用 | §15 SG-C4；真实用途/参数资格与代表标注仍SG-I1 |
| SG-A1：两个真实视觉Host | 独立AsunImage工程/Tests；§6/7和§11.4算子/转换/线程已冻结；歧义重载只核公共签名，冻结native footprint Plan | §15 SG-A1真cv2/异常/线程/资源；客户材料、Golden/Profile/集成资格尚未关闭 |
| SG-U1：嵌入式工程控件 | 独立WPF工程/Tests；只用Core/session/viewport；§13为唯一页面合同 | 真实STA/UIA/三语固定视口，不把截图当算法资格；本机25.2.3直接使用不核许可证/下载安装 |
| SG-I1：两个正式消费者 | 本模块仅配合其既定工程；不授予本会话跨模块写入 | Contract/State/Owner/证据映射、真实样本/Golden/Profile、发布回退/适用现场门由原Owner采纳验收 |

主控已按§19.1接收SG-C1～C4各片`ModuleCoreImplementationReady`（仅文档准备），不受无关客户样本或真实HALCON/WPF门阻断；SG-A1公开装配与SG-U1装配/Owner恢复增量限定内容接收。主控独立逐字段重建Parameter 131 bytes、Request 1181 bytes及SG-ID-02/03/04的1181/1181/1090 bytes，完整hex/hash均一致；四图八case与search/holdout不改冠军已核。此为规格核对，不是模块C#或算法运行验证；整模块不自行Ready，不沿旧队列写产品代码。真实消费者接线、HALCON/WPF、性能/现场与ImplementationSpecificationReady另判。

## 20. 依据与未决项

2026-10-06 来源接收（仅分割职责相关段落）：只读原件 `H:\docs\40-development\40-vision\2D检测器开发指导.md`，SHA-256 `84435fbe446ba21dccace13d8bdc08cb35fa8b38eeb424e69b529082f4272d9c`；来源绑定见 [20261006 source-manifest](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)。该项原登记为 `prior-snapshot-stale`，20261004 不同 hash 的选取快照不证明本原件已审阅；本次未修改清单。采纳 CROSS-FOV R2/在线工作集补充/§5 中分配前有限预留、最小依赖工作集、池化物理占用和释放失败保留 Owner 的通用约束，以及 §3.0.4 的集合顺序、同组件聚合和原始证据保留，落在 §§6–10、14–15。形态/区域算子语义重新按本地 HALCON 26.05 核对。未采纳 AOI 身份与运行流、源接口/状态名、权限、质量放行、工艺门限、Variation/OCR/标定、来源性能百分比或其测试/验收声明；已有自动参数候选约束直接复用 §2.1。此历史来源接收不扩大模块范围；本轮模块资源端口已在附录 A 冻结为模块接口，产品资源 authority 的映射仍归宿主；不改变 `DesignReview / Prep` 或 `PreparationIncomplete`，也不证明实现/性能/现场资格。

- [INDEPENDENT-MODULE-ARCHITECTURE.md](../INDEPENDENT-MODULE-ARCHITECTURE.md)：独立模块准入、层次、禁止边界和指导章节要求。
- [PKG-025_Segmentation.md](../../shared-modules/packages/PKG-025_Segmentation.md)：IM-029的来源包/应用消费者与依赖导航映射，不另定义资源或三态契约。
- [DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md](../../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md)：产品接入/材料解释映射，保留原锚点；算法/契约/资源/验证的唯一权威为本页，不反向依赖共享页补实施语义。
- [DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md)：视觉契约和厂商边界。
- [DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md](../../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md)：HALCON 优先选择与拒识规则。
- [FS-010_Local_segmentation.md](../../shared-modules/guidance/12-function-specs/FS-010_Local_segmentation.md)、[FS-011_2D_candidate_scoring.md](../../shared-modules/guidance/12-function-specs/FS-011_2D_candidate_scoring.md)：历史功能映射；不建立第二套契约。

### 20.1 本轮已读取依据与具体采纳

- HALCON 26.05：§6.3的本地算子页及 mean_image、erosion1、dilation1、set_system、contlength、circularity、area_holes、fill_up、boundary、gen_circle、get_region_runs、gen_region_runs、trans_from_rgb。实际采纳为整数端点拒绝隐式截断、全局Light≥T/Dark<T、动态四模式等号、Sauvola用途/反相、严格累计支撑、半整数圆核实际runs、线程局部邻接与max_connection仅读、周长不含孔洞/圆度不替代4πA/P²；不是视觉/性能已验证结论。
- [scikit-image固定commit](https://github.com/scikit-image/scikit-image/tree/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22)，版本来源复用[REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)：直接读 src/_skimage2/measure/_label.py 1–82、src/_skimage2/measure/_ccomp.pyx 199–250/345–410/467–533、tests/skimage2/measure/test_ccomp.py 1–95/105–155及LICENSE/pyproject。采纳4/8对角、背景、输入不变、union-find和实际反例测试思想。限制：bool路径与整数同值相邻合并不同；整图复制+每像素forest并非有界超大图方案，不迁入依赖/生产算法。
- 上述实际读取SHA-256：_label.py=`5a84738defe564b6e5074052a46b1be2b1e27d683d64ef6ed7d16e76afc798f5`；_ccomp.pyx=`a6081f8e142e39f8d323265338151dfbf3b1a06873a186f650cc856a1684b43b`；test_ccomp.py=`5638bea3e7f989ce5a562f7c046f80f44866e0d494f02adf259d72f38adc3cb8`；LICENSE=`611d3207504dcb4a808df209d2e7c9b4f2e89fe690f84735c0d548160966b527`；pyproject=`374eb358f7255c091fb8dd61c2553c5e8e1c998c774b1b90c6a9000b83c19d4f`，与既有快照一致。BSD-3-Clause及文件通知按原件保留；Python≥3.12、NumPy≥2.1、SciPy≥1.15等只作来源依赖元数据，本模块不引入Python/NumPy。
- DevExpress 25.2 官方页：直接读 [DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[TableView](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TableView?v=25.2)、[PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、[ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)、[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)。采纳布局停靠/恢复、TableView像素滚动、SelectedObject草稿投影、XYDiagram2D柱形绑定及Bars/普通控件不同SuperTip挂接。页面当前展示25.2.10信息不替换本机25.2.3；§13仍需本项目真实WPF验收，不安排依赖/授权审查。
- ImageLibDotNet公开边界只在参数类型/重载/封送有实质歧义时读取公共签名/消费编译；不查内部、不重核算子存在、不另接HOperatorSet/halcondotnet.dll。上游参考原件和历史hash保留，本轮不新增快照/报告。

- 2026-10-12定向补读HALCON 26.05的gen_image1/gen_image1_extern、gen_empty_region、gen_region_runs/get_region_runs、reduce_domain/get_domain、intersection/difference、gen_rectangle1/gen_circle、erosion1/dilation1、binary_threshold/local_threshold、boundary、intensity/min_max_gray、get_system/set_system：采纳私有像素存储与pin寿命、空Region非空tuple、inclusive坐标、完整统计bbox、严格支撑与灰度极值，落§11.4，不构成运行证据。
- 2026-10-12复用viewport 0.3.4-prep §10.6–10.9 Assembly v0.2公开装配/资源/原Task/晚到lease与§15.2来源边界；新增本方桥只消费其公开合同（§13.1.2），未审改其Root或源模块。dxdocs不可调用，定向读取本机DevExpress25.2官方XML五份，具体成员和采纳见§13.4；未下载、反编译或核依赖许可。
- OpenCV 固定 commit `a0cda081f8d769f40ab2f4904738b4787b44d07c`（本地已读快照见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)）：定向读 `modules/imgproc/src/connectedcomponents.cpp` 的 `connectedComponents_sub1`（5652行起）、4/8 连通分支的 `CV_Assert`（1138/1201行对 8、1768/1830行对 4、2300行对二者）与 `modules/imgproc/test/test_connectedcomponents.cpp` 的 `missing_background_pixels`（227行）。采纳：**连通邻接定义必须随结果显式记录、标签序号不是元素身份、比较区域前须规范化标签**；采纳该三条作为 §1A 双跑组件级门禁的来源依据。限制：实现中的标签序号、并行分支与 OpenCL 路径不引入产品；未构建或运行该仓库测试；Apache-2.0 根许可与文件内第三方声明按原来源保留，本模块不引入 OpenCV runtime 或平行生产算法。实际读取 SHA-256（本地快照为 CRLF 字节，下列为其 LF 归一化值，与 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md) 登记口径一致）：`connectedcomponents.cpp`=`7e41d56df91eec3185fd037387ef6262fa17cd17c1ffcc1e251d06db706b9e2d`；`test_connectedcomponents.cpp`=`b1a0cc6fb63917a7a2ea3e399178e317216b195048f0e96419f95636e58cdb72`；根 `LICENSE`=`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`（本地原始字节 `3ddf9be5c28fe27dad143a5dc76eea25222ad1dd68934a047064e56ed2fa40c5`，同为 Apache-2.0 文本）。

### 20.2 精确后续门

0.2.3-prep全批准范围设计闭合及本方/外部Owner的精确剩余项见§20.3；以下保留历史接收和真实后续门，不代表需要总控再审本轮内容。

0.2.1-prep已接收的§12 Host闭包及相关Core/适配内容保持。0.2.2-prep窄补§4.2/A.5 Simulator/双Host、1181-byte完整请求Golden、§11.3 A1后端资源模型/构造与§13.1.1 W1接线，已接收算法与A.1请求编码规则未改。SG-C1～C4已由主控按§19.1逐片接收为`ModuleCoreImplementationReady`（仅文档准备）；SG-A1公开装配与SG-U1装配/Owner恢复增量限定内容接收，不自行授整模块Ready。

1. SG-C1～C4六项规格已由主控接收为`ModuleCoreImplementationReady`（仅文档准备），该Core规格接收门已关闭。实现开工仍须明确任务并绑定权威代码仓库/分支与唯一新工程；不是内部API/算法欠账，也不证明任何HEAD/构建状态。
2. SG-A1的AsunImageSegmentationBackend/Profile/Footprint/Plan/Close及资源Owner已在§11.3明确，0.2.2公开装配增量已获限定内容接收；0.2.3的§11.4转换/完整统计/特征/线程设计由本原会话自审闭合，未授予SG-A1完整准入。保留真实消费程序集重载歧义编译核对、native footprint实测系数、整图/tile像素/特征等价、线程/资源异常与取消证据；不以“没运行”替代明确内部设计。
3. SG-U1（W1）三个控件、Session/Apply/Suggestion/Context、viewportContent/端口和根Owner接线在§13.1.1明确，0.2.2装配/Owner恢复增量已获限定内容接收；0.2.3的§13.1.2–13.4公开桥/导航/只读结果/三语/页面和恢复设计由本原会话自审闭合，未授予SG-U1完整准入。保留真实1920×1080当前DPI/三语/键盘/UIA/关闭验收及真实viewport消费编译/运行；不改显示设置，也不凭规格接收称WPF已运行。
4. SG-I1由两个真实消费者绑定组合根生命周期/有界恢复槽与接续触发Owner，确认未闭合时不退出宿主/Dispose共享端口；采纳产品Contract/State映射、证据事务Owner与计算身份；模块CompletedPartial与平台映射必须显式，不改模块状态来迎合未定Schema。
5. 客户/消费者冻结真实材料用途、双峰/饱和/弱信号/笔画/颜色或模型资格、备用决策表、Golden/标注及物理尺度；本文不编造客户门限，Shadow/Advice不能覆盖生产事实。
6. 对应BenchmarkProfile目标和代表输入、现场计量/生产资格另验收；无设备副作用的纯Core不被未提供硬件SDK/HIL阻断。未知资源/未排空只阻断实际受影响路线，不外推为全模块完成。

### 20.3 全部批准范围的设计闭合结论与剩余Owner

**结论（0.2.3-prep，2026-10-12）：当前全部批准范围内，可由本方决定的软件设计已闭合；没有把Adapter/UI/恢复/智能参数留作“程序员自行设计”，也没有把它们排除后仅宣称Core闭合。** 本永久原会话完成两轮有限走查：一轮按普通实现者的正常→错误→取消/恢复路径；一轮按独立Host/只读操作者的装配→呈现→交互→关闭路径。实际缺口已在正文修复，结构/引用与已接收片段保持的检查只证明文档，不证明代码运行。以下覆盖是当前范围说明，不新增准入等级。

本轮已执行定向文档校验：复用validate_docs.targets核本文本地链接，viewport新增锚点存在，代码围栏/表格列数/标题无结构错误，三语资源组合对齐、键无冲突、错误编号与已显示枚举覆盖通过。与0.2.2-prep修改前快照逐字比较，§6–7、§12.2、A.1和A.5完全保持；A.2只澄清非空计数字段与可空ComponentCount/ForegroundEmpty，未改字段或编码。新增UInt16样例核小端值1/256/4095/2、最后必需byte=10而短length=9；long坐标样例父图面积可用long表示。未重新计算旧身份Golden，未执行任何C#/HALCON/WPF/性能测试。

| 当前批准范围 | 唯一可实施落点 / 本轮检查结论 |
|---|---|
| 输入、用途、六种方法、规则/颜色/模型、多类二值投影与无标签 | §§1.3/3–6、A.1；同格单类、U/资格与不适用已明；无标签仍可显式分割，无真值不做建议排名 |
| 支撑、形态、分块/接缝、完整组件、特征/三值筛选 | §§5–7/11.3–11.4、A.2/A.3；复用已接收算法；转换、资源上界、超native特征状态及原Owner已明 |
| 无UI服务、身份、异步/结果lease、拒识/异常/恢复/版本 | §§4.2/8–12/18、A.1–A.3/A.5；双Host/原ticket/有界等待/未知保留已明，计算事实与资源闭合分开 |
| 有限智能参数建议、候选解释与人工采用 | §§2.1/6.7/8/13.4、A.4/A.5；候选/真值/预算/排序/Search与Holdout/取消与释放已明，不训练、不自动Apply |
| 可选控件与真实viewport接线、导航、只读结果 | §§13.1–13.3；唯一公开构造、同binding/原Task、Host来源映射、三态/LOD/只读接收与双STA已明；普通Clear可重用，Detach封门 |
| 操作体验、DevExpress、资源/三语/扩展语言、权限/Apply/分页 | §§13.2–13.4；白名单字段、原子资源切换、完整键值/错误、页128、键盘/UIA/1920×1080和未知应用路径已明 |
| 可判定验收、软件负载/容差/资源、发布回退/第二消费者 | §§14–19/A.5；原Golden复用，新增§15.1/16.1只覆盖本轮设计增量；不降低DEV-GOV-010 |

剩余项逐项归Owner；它们是实现开工、实现验证或真实消费者/生产门，不能改称内部设计欠账，也不能以“设计闭合”略过：

| 具体剩余项 | 唯一责任Owner | 关闭证据 / 仅阻断范围 |
|---|---|---|
| 明确实现任务、权威代码仓库/分支或可审计快照、唯一工程创建 | 用户/项目代码基线Owner；本模块实现Owner执行 | 绑定后按§19逐片开工；当前仅文档授权，无Git元数据不称HEAD；不因未提供仓库重复改指导 |
| Core实现与既有/新增断言实际执行 | IM-029永久原会话的Core实现Owner | §15/A.5的实际build/run、身份/状态/资源/建议反例；C1～C4原文档准备接收保持，不冒充运行通过 |
| ImageLibDotNet具体C#类型/重载消费编译、HALCON真实像素/特征/线程/清理 | IM-029 Adapter实现Owner | §11.4/15 SG-A1与SG-A15～19真实编译/执行；只核有歧义公开签名，不查AsunImage内部；非客户待办 |
| NativeFootprint rule系数与能力上界、峰值/冷热/长稳 | IM-029 Adapter实现Owner，复用本模块测试Owner | §11.3–11.4/16.1同输入实测并核保守上界；未测Unknown/NotEvaluated，阻受影响native组合/性能门，不填0、不转交客户 |
| WPF/DevExpress真实窗口、同viewport装配/原Task、三语/键盘/UIA、晚到Return/双代清理 | IM-029 WPF实现Owner；正式消费者Integration Owner接同公开桥 | §§13/15.1/16.1真实1920×1080当前DPI运行与关闭证据；无截图/模拟替代可见或释放确认，不等待依赖授权 |
| 正式产品Contract/State/权限/资源/来源与证据事务映射、恢复触发、两个消费者集成 | 各正式消费者的Domain/Integration Owner；本模块只负责其公开边界 | §18/20.2绑定真实Owner与有限根槽；不改其它模块合同、不新增平台事实权威；只阻相关产品接入 |
| 真实材料用途、双峰/饱和/弱信号/笔画/颜色/模型资格、代表图像/标注、物理尺度、允许备用 | 各消费者工艺/质量Owner；客户提供不可公开确定的材料与物理验收事实 | 冻结用途/样本/资格/Golden/Scale，保参数来源；无标签只禁需要标签的评价、缺Scale只禁物理特征，不阻无关Core |
| 客户时延/吞吐/资源/误接受拒绝目标、物理精度、现场与产品发布 | 各产品验收/质量Owner，与客户验收Owner共同签收 | 真实BenchmarkProfile、Replay/计量与适用现场证据；非设备计算不凭空要求SDK/HIL，不把软件容差当物理精度 |

整模块仍为`PreparationIncomplete`；这里的“软件设计闭合”不等同整模块`ImplementationSpecificationReady`、编译/Golden/性能/WPF通过或生产Ready。SG-A1/SG-U1新增设计由本原会话自行审核完成，不等待总控内容复核；总控只接收状态。后续只推进获授权切片与上述真实门；已接收Core、有效研究和Golden在输入/范围未变时直接复用，不再全审算。

### 20.4 viewport 0.3.5消费窄同步与闭合保持（0.2.4-prep）

原§20.3完整批准范围设计闭合结论保持。本轮只按viewport原Owner §20.5确认的源装配欠项补§13.1.2.1：公开Factory/Create/稳定Frames与Coordinates/Register/Remove、双Host source输入与原Task/epoch/FrameKey/代/预算/恢复。§4.5.1稳定对象命令和§4.7.1整源Empty Update已定向读清，本模块未采用，现有bbox叠加选择和局部Clear保持。§10.6–10.9 v0.2 Lifetime/Presentation/资源、Root/Close、分割算法、三语与身份向量不重新审算。

原会话完成两轮有限文档自审：正常预装配→首次Register/Attach→同producer换帧；异常容量/错实例/未登记consumer→晚到Read/Return→Remove/Retire原Owner收尾。新增SG-U20是未来真实运行反例，不是已通过测试。限定文档检查核公开签名/链接与保护段保持，结论仅为消费设计闭合；没有新产品代码、工程、报告或脚本。

真实门仍由§20.3原Owner承担：本模块WPF/Integration实现Owner完成工厂实际消费编译、原3×3显示/同binding/原Task/lease与故障恢复；image-frame发布/源Owner提供真实成功发布/原epoch与Return/Retire事实，客户用途/样本/性能/现场验收另门。SG-C1～C4原文档准备接收、SG-A1/SG-U1历史限定接收保持，整模块仍PreparationIncomplete，不提升ImplementationSpecificationReady或任何真实运行资格；本轮不等总控内容审核，实际范围闭合即停止。

## HALCON 26.05 算子资料入口

实现分割节点时，使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 作为目标版本 26.05 的资料入口，通过 `ImageLibDotNet.cv2` 调用；仅有具体 C# 类型、重载或封送歧义时核对公共签名，算法、线程、资源和取消行为按受影响切片验证。


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

## 附录 A：Module API Contract v0.2（唯一字段与端口）

接收状态（2026-10-10）：本附录中已明确的相关 Core/适配规格随主控本次内容复核接收；StartReceipt pending/同ticket恢复与§12 Host责任闭包保持一致。2026-10-11主控已回读§4.2/A.3/A.4/A.5并接收SG-C1/C2/C3/C4为`ModuleCoreImplementationReady`（仅文档准备）；A.5测试构造/Golden及A.4建议Owner收口在该接收范围内。主控独立逐字段重建Parameter 131 bytes、Request 1181 bytes及SG-ID-02/03/04的1181/1181/1090 bytes，完整hex/hash一致，并核对四图八case及search/holdout不改冠军。A.1规范编码保持。真实消费者端口接线、HALCON/WPF、性能及现场验收仍未执行，不能从附录接收推导整模块Ready。

本附录补全 §4/§8 的相关类型，不重复声明另一套请求/状态；adapter公开构造另见§11.3，Wpf/UI Contract v0.3另见§13.1–13.4，Tests-only另见A.5，均不扩为Core公共类型。表中 `T(Name:type,...)` 表示相同字段次序的 public sealed record T；枚举明确列出有效值。数组均为 ImmutableArray，字符串ID/hash不为空，OperationId/InstanceId长1..128、其它ID/修订1..256，RequestRevision≥1；SHA-256 为 64 位小写 hex；修订为不透明稳定字符串；任意值无来源不得自动填 latest。除明确可空字段，所有字段必填。API 未列出的内部工具类型不得扩成公共流程。

### A.1 输入、方法、处理与资格

| 类型 | 唯一字段/有效域 |
|---|---|
| `PixelEncoding` | Byte / UInt16 / Real32；内存为小端，单通道；真实有限编码范围见 ImageSnapshotRef.MinValue/MaxValue |
| `PlaneOrigin` | `(Kind:PlaneOriginKind,SourceHash:string,PreprocessHash:string,TransformRevision:string,ChannelKey:string,ColorSpace:string?,ColorEncodingRevision:string?)`；Kind=RawScalar/RegisteredColorChannel/DerivedScalar；颜色转换来源和通道不可缺 |
| `ImageSnapshotRef` | `(SnapshotId:string,Revision:string,Sha256:string,ParentGridId:string,ParentGridRevision:string,Width:long,Height:long,Encoding:PixelEncoding,GrayUnit:string,MinValue:double,MaxValue:double,Origin:PlaneOrigin)`；宽高正、Min<Max finite；Byte 在 0..255、UInt16 在 0..65535 内；12-bit 存 UInt16 仍按声明 0..4095 校验 |
| `ContextPolicy` | AllowValidExcluded / ExcludeAll；前者 I 仅免判，仍必须在 ImageValid 内才能支撑 |
| `UnknownPatch` | `(Region:PixelRegion,Reason:UnknownReason,SourceRevision:string)`；允许重叠不同原因；展示主原因按枚举顺序破同分，不能因此删来源 |
| `SupportDomain` | `(D:PixelRegion,I:PixelRegion,W:PixelRegion,ImageValid:PixelRegion,ClassificationValid:PixelRegion,UnknownPatches:ImmutableArray<UnknownPatch>,ContextPolicy:ContextPolicy,Revision:string)`；D⊆W、D∩I=∅，均属同父图格，ClassificationValid⊆ImageValid⊆W；W−ClassificationValid全部有UnknownPatch原因，patch只能位于W且不与ClassificationValid相交 |
| `GrayInterval` / `WindowSpec` | `(Min:double,Max:double)` / `(Width:int,Height:int)`，§5 范围 |
| `MethodSpec` | 抽象 record，`Kind:SegmentationMethod` 只读计算属性；五种 sealed 类型字段按 §4.1；`FixedIntervalsSpec(Intervals)`、`GlobalSpec(Kind,Polarity,StatisticsDomain)`、`DynamicSpec(Mode,Offset,Reference?,MeanWindow?)`、`SauvolaSpec(Polarity,WindowSize,Scale,Range)`、`MaskSpec(MaskRevision,ForegroundClassKey)`；其余类型拒绝 |
| `MorphologyOp/ObjectMode` | Op=Opening/Closing/Erosion/Dilation，无None枚举；不处理表示空MorphologySteps；ObjectMode=WholeForegroundSet/PerInputObject |
| `KernelSpec` | 抽象 record；sealed `RectangleKernel(Width:int,Height:int)`、`CircleKernel(Radius:double)`、`ExplicitKernel(Support:PixelRegion)`；全部关于原点对称、中心整数；实际 support 由 adapter 回执冻结 |
| `MorphologyStep` | `(StageId:string,Op:MorphologyOp,Kernel:KernelSpec,Iterations:int,ObjectMode:ObjectMode)`；StageId唯一且不得等于保留名raw，按数组顺序执行，不能用字典排序 |
| `FeatureKey` | AreaPixels/CentroidRow/CentroidColumn/BoundingBox/Perimeter/Circularity/HoleAreaPixels/GrayMean/GrayMin/GrayMax/AreaPhysical/Boundary |
| `FeatureUnit` | PixelArea/Pixel/Gray/Dimensionless/SquareMillimeter；BoundingBox/Boundary 的 Unit=Pixel |
| `Comparison` / `FilterCombination` | GreaterOrEqual/LessOrEqual/ClosedRange；All/Any，空谓词时仅 All 合法并表示不筛选 |
| `FeatureFilter` | `(Feature:FeatureKey,Comparison:Comparison,Min:double?,Max:double?,Unit:FeatureUnit,FilterRevision:string)`；GE 仅 Min、LE 仅 Max、Range 二者齐且 Min≤Max；BoundingBox/Boundary 非标量不能筛选；feature 必须在 FeatureSet |
| `TileCore` / `TilePlan` | `(TileKey:string,Row:long,Column:long,Width:int,Height:int)` / `(Revision:string,Cores:ImmutableArray<TileCore>)`；非重叠矩形 core 覆盖 D（允许覆盖 D 外 W），tile key 唯一；不得用到达顺序推编号。D 为空允许空 core |
| `ProcessingSpec` | `(MorphologySteps:ImmutableArray<MorphologyStep>,Connectivity:Connectivity,FeatureStageId:string,FeatureSet:ImmutableArray<FeatureKey>,FeatureFilters:ImmutableArray<FeatureFilter>,FilterCombination:FilterCombination,Tiles:TilePlan,Revision:string)` |
| `FallbackBinding` | `(From:OperationTicket,FailureCode:string,RuleRevision:string)`；仅 provenance，不授权本模块执行其它路线 |
| `MethodQualification` | `(Revision:string,Sha256:string,Use:QualificationUse,QualifiedDomain:PixelRegion,HistogramBimodal:bool?,MaxSaturatedFraction:double,MinStatisticsPixels:long,ExpectedStrokeWidth:double?,FallbackFrom:FallbackBinding?)`；Use=ResponseCandidate/QualifiedBinaryClassification/DocumentStroke；比例 0..1、min>0；全局须 HistogramBimodal=true 且实际饱和比例/样本数门满足；Sauvola 必须 DocumentStroke 和正笔画宽。不存在用途证据拒识；Profile 资格是输入事实，不由算子成功生成 |
| `FrozenMask` | `(Revision:string,Sha256:string,ParentGridId:string,ParentGridRevision:string,InputHash:string,ModelHash:string?,ModelVersion:string?,PreprocessHash:string,BackendVersion:string,ClassKey:string,ClassificationThresholdRevision:string,Foreground:PixelRegion,Background:PixelRegion,Unknown:ImmutableArray<UnknownPatch>,Objects:ImmutableArray<MaskObject>,Maturity:MaskMaturity)`；Maturity=ExternalAlgorithm/Shadow/Advice/ReleasedModel；ModelHash/ModelVersion两项同时有或全空；Shadow/Advice/ReleasedModel必须有两项，ExternalAlgorithm可全空；InputHash=Image.Sha256、PreprocessHash=Image.Origin.PreprocessHash，格/类/MaskRevision绑定相等；F/B不交，U 是 W 内未分类补集且有原因；Classes 不映射制程名称 |
| `MaskObject` | `(ObjectKey:string,ClassKey:string,Region:PixelRegion)`；同类可重叠；只用于 PerInputObject；ClassKey必须匹配MaskSpec，否则拒绝；ObjectKey唯一，PerInputObject时所有Object.Region并集须等于FrozenMask.Foreground；WholeForegroundSet可无Objects |
| `PixelScale` | `(Revision:string,QualificationHash:string,AreaPerPixelMm2:double,ParentGridId:string,ParentGridRevision:string)`；正 finite、仅等面积已资格化平面格；非线性/曲面物理面积本模块不计算 |
| `ExecutionLimits` | `(ProfileRevision:string,ProfileHash:string,MaxPixels:long,MaxRuns:long,MaxComponents:int,MaxEquivalences:long,MaxWorkingBytes:long,MaxResultBytes:long,MaxProjectionBytes:long,Timeout:TimeSpan,DrainTimeout:TimeSpan,CleanupTimeout:TimeSpan,MaxParallelTiles:int,ProgressInterval:TimeSpan)`；§5 逐字段范围；QueueCapacity/MaxRetainedResults 为实例 RuntimeLimits，不能在单请求替换 |
| `RuntimeLimits` | `(InstanceId:string,MaxActiveOperations:int,QueueCapacity:int,MaxRetainedResults:int,MaxTombstones:int,TombstoneRetention:TimeSpan,MaxEventBacklog:int)`；active 1..64、队列 0..4096、结果 1..1024、墓碑 1..65536/1 ms..24 h、事件积压 16..65536；全部显式，满容量接纳前 SEG-007/015；未确认资源/未释放结果不得按墓碑期限淘汰；详细查询墓碑到期可丢Result元数据，但紧凑身份围栏(OperationId/RequestRevision/RequestHash/原ticket)保留到实例结束，计入MaxTombstones，不允许到期同ID再执行。围栏容量满接纳前SEG-007；须原实例Close/Owner闭合后显式新InstanceId，不偷偷轮换实例 |

Hash不由显示文本生成；流开头只写一次域标签字符串（参数seg-parameters-v2、请求seg-request-v2），随后按字段递归编码，普通record不另加域标签；每个string都写UTF-8 byte长度int32+字节，int字段int32小端、long字段int64小端，PixelRun三个long依§4次序。`SegmentationIdentity.ComputeParameterHash(MethodSpec method,ProcessingSpec processing):string` 和 `ComputeRequestHash(SegmentationRequest request):string` 是 Core 唯一公开身份工具。冻结 `seg-parameters-v2` / `seg-request-v2` 二进制编码：依 §4 请求字段/上表字段次序递归写；枚举 int32、bool 0/1 byte、long int64 小端、double IEEE754 int64 位模式小端（−0 规范成 +0）、TimeSpan.Ticks int64；可空字段先写存在 byte；列表先写 int32 数量（必须≤int.MaxValue），域 runs 按 canonical 顺序，FeatureSet 按枚举去重排序，形态/过滤/TileCore 数组保持请求顺序。方法/核分支先写固定枚举 tag（方法按 §4 顺序 0..5；核 Rectangle=0/Circle=1/Explicit=2），再写该分支表内字段，GlobalSpec.Kind 不再重复写；所有其它 enum 按本文列举顺序从 0 编号，Connectivity 显式 4/8；record 固定字段次序且不另写类型名，Nullable bool 同样写存在 byte+值；字符串为非空，空集合允许但 ImmutableArray.IsDefault 拒绝，DateTimeOffset 非请求字段不入 hash；Processing.Revision 包含。SHA256.HashData 后小写 hex。RequestHash 包含全部 §4 请求字段，唯独 OperationId/RequestRevision/ParameterHash 不参与（其 ParameterHash 必须先复算一致）；ContractVersion 限定 `0.2`。输入关联不用模糊字符串拼接；CancellationToken 不在请求内。计算身份为 ticket+RequestHash+AlgorithmRevision；不能升级后重算旧身份替换历史。排序/分区改变可能改变请求 hash，但同参数/格的规范化像素结果必须等价。

### A.2 输出与诊断值

| 类型 | 唯一字段/语义 |
|---|---|
| `ValidationResult` | `(IsValid:bool,Errors:ImmutableArray<ModuleError>,RequestHash:string?)`；有限小型元数据；纯校验不得读取帧 |
| `ModuleError` | `(Code:string,Stage:string,FieldPath:string?,Recoverability:Recoverability,Cause:string,EvidenceRef:string?)`；Recoverability=CorrectRequest/NewOperation/WaitForDrain/RecoverOwner/None；Cause 是稳定诊断键，原异常在宿主诊断 sink，不充当操作文案 |
| `ClassificationSummary` | `(ClassificationScope:Completeness,DCount:long,FCount:long,BCount:long,UCount:long,ComponentCompleteness:Completeness,ComponentCount:long?,ForegroundEmpty:bool?)`；F+B+U=D；ComponentCount仅ComponentCompleteness=Complete/Empty可给；ForegroundEmpty仅ClassificationScope=Complete/Empty可给，筛选不影响F。NotEvaluated的ComponentCount/ForegroundEmpty为null；DCount/FCount/BCount/UCount仍是非空long，未执行D全计U且F=B=0，不捏造已知分类 |
| `QualitySummary` | `(QualificationRevision:string,Use:QualificationUse,GatePassed:bool,ValidFraction:double?,SaturatedFraction:double?,Issues:ImmutableArray<ModuleError>)`；空分母 null；不能导出产品 PASS |
| `StageReceipt` | `(StageId:string,Operator:string,ParameterHash:string,KernelRuns:PixelRegion?,UsedThreshold:double?,StatisticsPixels:long?,InputDomainHash:string,OutputDomainHash:string,SupportHash:string,Elapsed:TimeSpan)`；全局 threshold 回执须 UsedThreshold/StatisticsPixels，其他阶段二者 null；Operator 为回执非可执行自由字符串 |
| `Provenance` | `(ContractVersion:string,RequestHash:string,InputHash:string,ParameterRevision:string,ParameterHash:string,AlgorithmRevision:string,Method:SegmentationMethod,AdapterVersion:string,HalconRuntimeVersion:string?,QualificationRevision:string,StageReceipts:ImmutableArray<StageReceipt>,FallbackFrom:FallbackBinding?,MaskMaturity:MaskMaturity?)`；模拟 HalconRuntimeVersion=null，不能填真机版本 |
| `ResourceUsage` | `(PeakManagedBytes:long,PeakNativeBytes:long?,ResultBytes:long,SourceBorrowCount:int,OutstandingResources:int,QueueWait:TimeSpan,DrainElapsed:TimeSpan,ReleaseElapsed:TimeSpan)`；不可测 native=null，不是零 |
| `StageRegions` | `(StageId:string,Foreground:PixelRegion,Background:PixelRegion,Unknown:ImmutableArray<UnknownPatch>,Added:PixelRegion,Removed:PixelRegion,SupportLost:PixelRegion)`；F0 附加差区为空，所有集合可复查 |
| `PixelBox` | `(Row1:long,Column1:long,Row2:long,Column2:long)`；包含端点、非空且不倒置 |
| `TopologyStatus` / `FilterStatus` | Complete/TouchesUnknown/TouchesDomainBoundary/Incomplete；Accepted/Excluded/Unknown |
| `FeatureValue` | `(Key:FeatureKey,Status:FeatureStatus,Unit:FeatureUnit,CountValue:long?,Value:double?,Box:PixelBox?,Boundary:PixelRegion?)`；Valid 仅填与 Key 相符的一类（area/hole long、bbox box、boundary region、其它 double）；非 Valid 全部 null |
| `RegionComponent` | `(ComponentKey:string?,FragmentKey:string,StageId:string,Region:PixelRegion,Topology:TopologyStatus,Features:ImmutableArray<FeatureValue>,Filter:FilterStatus,FilterReasons:ImmutableArray<ModuleError>)`；未闭片段 ComponentKey=null；key 不跨重检关联目标 |
| `ComponentPage` | `(Offset:long,TotalKnown:long?,Items:ImmutableArray<RegionComponent>,HasMore:bool,Completeness:Completeness)`；片段集合 total 不称全局组件数；offset≥0、count=1..1024；offset≥存储条目数返回空页/HasMore=false。页列表只借用结果数据，页元数据新分配≤MaxProjectionBytes，完整Region/Boundary底层仍计在lease，不重复计费；UI绘制另裁剪复制并计投影预算；条目按ComponentKey或FragmentKey字典序稳定，分页total只称存储条目数、不称全局物体数 |
| `PendingReason` | None/DrainPending/ReleasePending；DeadlineExceeded 用独立 bool，避免变成另一终态 |
| `StartReceipt` | `(Accepted:bool,Ticket:OperationTicket?,Snapshot:OperationSnapshot?,Errors:ImmutableArray<ModuleError>)`；新请求已启动I/O/持有reservation却未接纳时必须非空原Ticket/非终态Snapshot/DrainPending或ReleasePending，无RequestAccepted；无在途I/O/资源才可Ticket=null。重复为false+原ticket/SEG-014，身份内容冲突为SEG-002且Stage=Identity，不移交原Data/清理权；其它SEG-002按实际发生阶段保留新请求责任 |
| `OperationSnapshot` | `(Ticket:OperationTicket,State:ExecutionState,IsTerminal:bool,PendingReason:PendingReason,DeadlineExceeded:bool,LastSequence:long,Result:SegmentationResult?,Errors:ImmutableArray<ModuleError>)`；未知 ticket Result=null，错误 SEG-016；Query 不分配新结果/再 acquire lease |
| `DrainStatus` / `DrainReport` | Status=Drained/Waiting/ReleasePending；`(Status:DrainStatus,AdmissionClosed:bool,Pending:ImmutableArray<OperationTicket>,OutstandingResultLeases:int,Errors:ImmutableArray<ModuleError>)`；覆盖调用开始时已登记请求（包含Accepted=false但尚有I/O/reservation的ticket）；Drained只确认执行/在途I/O与执行账项闭合，OutstandingResultLeases仍可>0，不冒充消费者lease消失。Close返回Drained后本实例不得再产生未登记迟到Data；结果转交/终态发布先于闭合计数 |
| `SegmentationEventKind` / `SegmentationEvent` | Kind 与 §8.3 同一枚举；字段为 `(Ticket:OperationTicket,Sequence:long,Utc:DateTimeOffset,Elapsed:TimeSpan,Kind:SegmentationEventKind,StageId:string?,CompletedUnits:long?,TotalUnits:long?,PendingReason:PendingReason,TerminalState:ExecutionState?,Error:ModuleError?)`；TerminalState 仅 Kind=Terminal 有值 |

`IResultLease` 属性 `LeaseId:string,OwnerId:string,Ticket:OperationTicket,IsReleased:bool,Bytes:long`；方法 `StageRegions ReadStage(string stageId)`、`ComponentPage ReadComponents(long offset,int count)`、`ValueTask<ReleaseReceipt> ReleaseAsync(TimeSpan budget,CancellationToken cleanupToken)`。ReadStage 返回同一冻结只读值，不做算法/复制全图；ReleaseAsync逐次有界，重复调用合并同一在途归还任务，预算/token到期返回Pending或取消本次观察，原Owner/task/数据/账仍保留；未确认不置IsReleased，不因第二次no-op改Released。数据为借用视图，调用方不得在lease归还后持有/使用其数组引用；并发读取必须先结束，释放者负责丢弃borrow，独立长期保存须先在宿主新Owner账下复制。ReadStage/ReadComponents与Release由lease锁串行，已释放读取抛ObjectDisposedException；成功Release清空lease内部大数据引用，Query只留小型摘要/已释放lease壳，不挂原像素。托管归还表示引用寿命闭合，不声称GC已将进程物理内存归还OS；真实工作集仍按§16实测。Core result store 同一个 ticket 只构造一个 lease，Query/Wait 返回该引用，不因查询重复计费/重复转交；两个并行消费者若需独立寿命由宿主在消费边界复制/独立收费，不能二者各 Dispose 同一个未声明共享资源。

### A.3 输入、资源与 backend 端口

| 接口/值 | 精确公开形状与 Owner |
|---|---|
| `IImagePlaneSource` | `ValueTask<TileReadReceipt> OpenTileAsync(ImageSnapshotRef image,TileReadRequest request,CancellationToken token)`；read request=`(Ticket:OperationTicket,Row:long,Column:long,Width:int,Height:int)`。source 按 SnapshotId/hash 的真实登记取只读存储，不读取“当前图” |
| `TileReadReceipt` | `(Lease:IImageLease?,Missing:ImmutableArray<UnknownPatch>,Errors:ImmutableArray<ModuleError>)`；缺 tile 是已知缺测不是一个全零 lease；坐标版本错 SEG-002；若失败时已借用，receipt 仍携原 Lease/Owner，backend 登记后释放；抛异常仅允许无借用或 Owner 已可恢复登记，禁止失去未知资源 |
| `IImageLease` | 属性 `LeaseId:string,OwnerId:string,Snapshot:ImageSnapshotRef,ReadRequest:TileReadRequest,StrideBytes:int,Pixels:ReadOnlyMemory<byte>,Valid:PixelRegion`；方法同 `ReleaseAsync(TimeSpan,CancellationToken):ValueTask<ReleaseReceipt>`。本地连续矩形槽、stride≥width*bytesPerPixel，length≥checked((height−1)*stride+rowBytes) 且≤Array.MaxLength；source 保证只读至确认归还，未确认时保留原 source Owner。没有字段允许调用方释放底层 shared frame |
| `WorkingSetRequest` | `(Ticket:OperationTicket,RequestHash:string,ProfileHash:string,Limits:ExecutionLimits,RequiredBytes:long,RequiredSourceSlots:int)`；RequiredBytes=BackendPlan.RequiredWorkingBytes（执行期间含结果投影），须≤MaxWorkingBytes；BackendPlan.RequiredResultBytes≤MaxResultBytes、RequiredSourceSlots≥同时依赖的tile/参考数；只消费mask且无灰度特征时可为0；来源 frame 不重复物理计费 |
| `IWorkingSetSource` | `ValueTask<ReservationReceipt> ReserveAsync(WorkingSetRequest request,CancellationToken token)`；另有 `ValueTask<ReleaseReceipt> ReleaseResultAsync(string ownerId,string resultLeaseId,OperationTicket ticket,long bytes,TimeSpan budget,CancellationToken cleanupToken)`，只确认转交后对应账项归还，按原lease身份幂等；由Core IResultLease.ReleaseAsync调用，source不持结果像素。容量竞争由同一宿主authority；返回前已真实预留，不先分配再申请 |
| `ReservationReceipt` | `(Granted:bool,Lease:IWorkingSetLease?,Errors:ImmutableArray<ModuleError>)`；false 且 Lease=null 表示从未持有；若已有 scope 尚待归还则必须返回 Lease 并保持待确认，禁止丢 Owner |
| `ResourceToken` | `(ScopeId:string,AllocationId:string,OwnerId:string)`；资源键稳定且 operation 绑定、禁止 ambient/static 身份 |
| `AllocationSpec` / `AllocationKind` | `(AllocationId:string,OwnerId:string,Kind:AllocationKind,Bytes:long)`；Kind=ManagedScratch/NativeScratch/ResultProjection/PoolBorrow/SourceBorrow；source/pool physical 原 Owner 持有，Borrow 的 Bytes 记录逻辑 footprint 不重复物理扣费，Private 分配计真实占用 |
| `ChargeReceipt` | `(Granted:bool,Token:ResourceToken?,Errors:ImmutableArray<ModuleError>)`；重复 AllocationId 同尺寸/owner 返回原 token 不重扣，不同内容 SEG-002 |
| `IWorkingSetLease` | 属性 `ScopeId:string,OwnerId:string,Ticket:OperationTicket,RequestHash:string`；方法 `ChargeReceipt TryCharge(AllocationSpec allocation)`、`ReleaseReceipt ConfirmRelease(ResourceToken token,ReleaseReceipt physicalReceipt)`、`ValueTask<TransferReceipt> TransferResultAsync(IResultLease preparedResult,CancellationToken token)`、`ValueTask<ReleaseReceipt> ReleaseAsync(TimeSpan budget,CancellationToken cleanupToken)`。TryCharge 在真实分配前，不自动扩容；确认须匹配原 owner/token，未知不退账 |
| `ReleaseStatus/ReleaseReceipt` | Status=Released/Pending/Failed；`(Status:ReleaseStatus,OwnerId:string,ResourceId:string,Errors:ImmutableArray<ModuleError>)`；释放回执承认 scope/borrow 归还，不假称池 physical free；重复只有原 Released 墓碑可 Released，无确认 no-op 必为 Pending |
| `TransferReceipt` | `(Transferred:bool,ResultOwnerId:string?,Errors:ImmutableArray<ModuleError>)`；true须ResultOwnerId非空，false为null且仍归原scope。容器由Core先在scope内构造，source只读取preparedResult元数据，不读/创建像素store；成功receipt后Core激活同一lease。ledger按ticket/resultLeaseId幂等，已确认提交不得因token取消回false；未知保持原scope责任、SEG-011/ReleasePending，不发布Data；原scope在新Owner确认接收后解占，无空窗/重扣 |
| `ISegmentationBackend` | 属性 `Profile:BackendProfile`；纯值 `BackendPlan Plan(SegmentationRequest request)`；`ValueTask<BackendOutput> ExecuteAsync(BackendRequest request,IImagePlaneSource images,IWorkingSetLease scope,IProgress<SegmentationEvent>? events,CancellationToken executionToken)`；`ValueTask<ReleaseReceipt> RecoverAsync(OperationTicket ticket,TimeSpan budget,CancellationToken cleanupToken)`。不接平台对象；ExecuteAsync只在该operation全部native/worker已返回后完成，失败也保留资源登记供恢复 |
| `BackendProfile` | `(Revision:string,Sha256:string,AdapterVersion:string,HalconRuntimeVersion:string?,SupportedMethods:ImmutableArray<SegmentationMethod>,SupportedEncodings:ImmutableArray<PixelEncoding>,MaxTileWidth:int,MaxTileHeight:int,MaxReconstructionPixels:long,MaxReconstructionRuns:long)`；尺寸/数量正且有限，模拟版本不得填 HALCON；能力表不授予用途资格 |
| `BackendPlan` | `(Supported:bool,ProfileHash:string,RequiredWorkingBytes:long,RequiredResultBytes:long,RequiredSourceSlots:int,Errors:ImmutableArray<ModuleError>)`；Plan 不读帧/分配像素/native，是基于请求和实测 adapter footprint 模型的 checked 最坏上界；缺 native 上界拒绝受影响路线。工作额度含结果形成期间的占用 |
| `BackendRequest` | `(Ticket:OperationTicket,RequestHash:string,Request:SegmentationRequest)`；ticket/请求绑定相符，所有 native 对象只在 adapter 内 |
| `BackendOutput` | `(Ticket:OperationTicket,RequestHash:string,ProfileHash:string,Stages:ImmutableArray<StageRegions>,Components:ImmutableArray<RegionComponent>,Summary:ClassificationSummary,Quality:QualitySummary,Receipts:ImmutableArray<StageReceipt>,Resources:ResourceUsage,Errors:ImmutableArray<ModuleError>)`；值投影分配预先 TryCharge；backend 临时 Region 仍须确认释放，与输出值分开 |
| `SegmentationService` | sealed class 实现 §8 接口；构造 `(IImagePlaneSource images,ISegmentationBackend backend,IWorkingSetSource workingSets,TimeProvider time,RuntimeLimits runtime,IProgress<SegmentationEvent>? events)`；新增 `ValueTask<OperationSnapshot> RecoverAsync(OperationTicket ticket,TimeSpan budget,CancellationToken cleanupToken)` 与接口一致；恢复仅释放原资源，不重算 |

处理责任固定：adapter执行threshold/形态/局部connection、有界全局接缝协调、完整Region重建和native feature，形成未经筛选的托管投影；Core负责请求/身份/资源/状态、输出完整性校验、三值筛选和结果lease。backend的Filter初值Unknown/FilterReasons空，Core验证Features后按§7.2重算Filter，不信任后端筛选，不改变F/B/U。纯Core SG-C3检验冻结投影和错误反例，不实现第二套生产视觉算法。服务在后台完成operation，必须验证 BackendOutput 的 F/B/U 分割、run 编码/计数、组件无重复/支持、特征单位/状态和回执 RequestHash；非法输出 SEG-017 并隔离，不能将模拟后端的“成功”直接转 Completed。source/scope 尚未确认归还时 backend 必须保留精确 lease 引用与原 Owner；预留接纳前在途时保存请求键/I/O task和DrainPending；晚返失败/待释放lease保存ReleasePending并开放同一个RecoverAsync，StartReceipt始终携原ticket/snapshot，不因Accepted=false丢Owner/退款；从未派发backend时恢复不调用backend。backend返回须匹配Ticket/RequestHash/ProfileHash；Terminal由Core产生。backend事件仅允许StageStarted/Progress/StageCompleted/QualityEvaluated，Ticket匹配、Sequence=0、TerminalState=null，由Core重新编号；不能发ResourcesReleased/Terminal。source/working set 抛 IO 异常映射 SEG-006/018，CancellationToken 导致的等待取消与运行取消按 §8 区分，恢复抛异常保留 Owner/原 ticket。

### A.4 参数建议

不增加训练/模型管理 API。公开契约为：
- `SuggestionRequest(SuggestionId:string,Search:ImmutableArray<SuggestionFixture>,Holdout:ImmutableArray<SuggestionFixture>,Candidates:ImmutableArray<SuggestionCandidate>,Weights:SuggestionWeights,MaxEvaluations:int,MaxCandidates:int,Timeout:TimeSpan,MaxWorkingBytes:long)`；search/holdout fixture hash 无重叠，SuggestionId长1..64，Timeout=1ms..24h，MaxWorkingBytes正且所有同时存活评价/scores在其内；列表1..4096，候选1..4096，MaxEvaluations 正且≥候选数、MaxCandidates 1..候选数。评价数为候选×搜索 fixture+留出测试总数，上限含两者，达限明确 Partial。
- `SuggestionFixture(FixtureHash:string,Request:SegmentationRequest,TruthForeground:PixelRegion,TruthBackground:PixelRegion)`；FixtureHash为一次域标签`seg-suggestion-fixture-v2`后依次编码ComputeRequestHash(Request)/TruthForeground/TruthBackground的SHA256（沿A.1），接纳前复算；真值不交且在原 D/ImageValid 内，未知真值不作为正确背景；Request 固定输入/用途/处理域。候选只能改 Method/Processing 参数，不能改 input/domain/qualification 的适用事实。
- `SuggestionCandidate(Method:MethodSpec,Processing:ProcessingSpec,ParameterHash:string)`；hash 复算一致，重复 hash 去重。
- `SuggestionWeights(FalsePositive:double,FalseNegative:double,Unknown:double)`；有限非负，至少一项正。
- `SuggestionStatus`=Completed/Partial/Cancelled/TimedOut/InsufficientEvidence/Failed。
- `FixtureScore(FixtureHash:string,FalsePositive:long,FalseNegative:long,Unknown:long,TruthPixels:long,Cost:double?,Errors:ImmutableArray<ModuleError>)`；Cost=(wFP*FP+wFN*FN+wU*U)/TruthPixels，分母>0，否则 InsufficientEvidence；在冻结真值域之外不计分。边界/粘连的 diagnostics 复用组件投影，不作为未定义额外排序成本。
- `CandidateEvaluation(ParameterHash:string,SearchScores:ImmutableArray<FixtureScore>,HoldoutScores:ImmutableArray<FixtureScore>,MeanSearchCost:double?,UnknownFraction:double?,Resources:ResourceUsage)`；宏平均每 fixture 成本，不按大图面积无声加权；非完整搜索不排名。
- `SuggestionResult(SuggestionId:string,Status:SuggestionStatus,Evaluations:ImmutableArray<CandidateEvaluation>,Ranked:ImmutableArray<string>,ExecutedEvaluations:int,NotExecuted:ImmutableArray<string>,Errors:ImmutableArray<ModuleError>)`；Ranked仅完整搜索排名的前MaxCandidates且留出完整的候选；MeanSearchCost宏平均，UnknownFraction为各fixture(U/TruthPixels)宏平均，留出只展示，不反向挑冠军；失败/Partial不输出可称合格的推荐。

建议只允许每个candidate保持fixture原Method.Kind/用途、FeatureStageId和D/W/TilePlan，改变连续参数/有序形态/筛选须仍在已资格域；不把候选变更解释为另一方法资格。每次评价派生OperationId为一次域标签`seg-suggestion-operation-v2`，随后依次编码SuggestionId/ParameterHash/FixtureHash/标签search或holdout四个字符串并SHA256（编码沿A.1，64字符），RequestRevision沿冻结fixture≥1、ParameterRevision固定`suggestion:`加SuggestionId、hash按新Method/Processing复算，不复用原fixture OperationId。建议重复SuggestionId在本实例围栏中拒绝，不重算；已接纳后的候选执行共享建议的一个active名额，不再排入同实例队列造成MaxActive=1自等，资源仍逐次申请同一有限账；并行外部请求受同一容量门。建议执行与普通operation共用内部已接纳管线（不递归公开Start排队），并确认 Data/临时资源归还再下一次；冻结候选排序按 ParameterHash，Search/Holdout 按 FixtureHash。同分按 UnknownFraction、ParameterHash；Close/取消停止新评价，已有 native 按原生命周期排空。建议使用独立ID，占同实例一个有限活动名额/资源；内部评价身份围栏纳入MaxTombstones，候选开始前须确认有限登记容量，满时停止为Partial；不得并行暗中开多服务逃预算。

建议协调器在首次异步工作之前登记SuggestionId、冻结request、linked执行CTS、唯一`Task<SuggestionResult>`和当前评价预备槽；`SuggestParametersAsync`返回同一task的ValueTask，取消只请求停止，不在native/I/O未返时提前完成/丢任务。每个评价的原ticket、Start/执行/转交task和Data归协调器持有，OpenTile/Reserve晚返及Release失败走§8/10同ticket恢复；未确认时不开始下一评价。`CloseAsync`关闭新建议并取消已有建议，DrainReport.Pending包含当前评价未闭合ticket；task尚未返回（包括纯建议计分）时Status=Waiting，即使Pending空也不称Drained。建议结果不持pixel lease，只有全部评价/资源确认归还后task才可完成；service强持协调器直到终结，宿主/Session在调用前持其原task/CTS，不能用等待取消丢弃真实建议。Core可沿DrainReport.Pending逐ticket Recover，不能重发SuggestionId来恢复。

### A.5 测试装配与完整身份 Golden（仅 Core.Tests，非产品 API）

以下构造/fixture只放入唯一Core.Tests的 `Asun.Modules.Segmentation.Tests.Fixtures` namespace，构造是供同Tests程序集的两个测试Host调用，不进入Core产品DLL。所有值字段沿附录A类型，冻结后不再可变；测试入口不得用“省略字段”替代构造。

| 测试类型 | 精确构造/控制与消费者 |
|---|---|
| FrozenTile | `(Row:long,Column:long,Width:int,Height:int,StrideBytes:int,Pixels:ImmutableArray<byte>,Valid:PixelRegion,Missing:ImmutableArray<UnknownPatch>)`；tile矩形/编码与Image相符；读请求必须恰匹配冻结tile，未登记读为MissingImage，不返回零图；source实际创建IImageLease，released前保持冻结字节 |
| FrozenImageFixture | `(Image:ImageSnapshotRef,Tiles:ImmutableArray<FrozenTile>)`；图像身份唯一，多个fixture可有同格但不能用latest替代。source多图重载由本表输入路由，borrow仍按原ticket/Owner归还 |
| FrozenBackendCase | `(RequestHash:string,Plan:BackendPlan,Output:BackendOutput)`；case hash唯一、Plan.ProfileHash等于构造Profile；Execute返回的外层Ticket使用本次BackendRequest.Ticket，逐组件FragmentKey也用该ticket按§7.1重绑定；ComponentKey/冻结像素/特征不变，其余请求身份完全匹配，不依OperationId重算fixture算法。测试每例构造自己的case，不允许来源不同却复用输出 |
| SimulatorFaultControl | public sealed class无参构造；`SetGate(SimulatorCall call,TaskCompletionSource<bool> gate)`、`SetFailure(SimulatorCall call,int attempts,Exception error)`；调用次数用`int GetCallCount(SimulatorCall call)`读取。每个call最多一个gate/一项有限attempt错误，attempts=1..16，禁用注入时零gate/零failure；gate用RunContinuationsAsynchronously。Call=OpenTile/Reserve/BackendExecute/BackendRecover/Transfer/SourceRelease/ScopeRelease/ResultRelease，各一固定槽，无任意脚本/无界队列。故障发生时原task/Owner先登记；未返回gate不当已释放 |
| 三个Simulator | §4.2三个构造均已含必填`SimulatorFaultControl faults`，无隐式创建；gate/异常只控制时序/恢复，不执行生产算法。FrozenProjectionBackend.Plan按ComputeRequestHash选case，未登记返回Supported=false/SEG-003，纯Plan不取source；BackendExecute调用source时按冻结tile请求/原scope登记，有借用必finally归还；BackendRecover只处理自己原登记。BoundedWorkingSetSimulator按预留容量与sourceSlots真实占位，TryCharge/Transfer/Confirm/Release遵循A.3，Pending不退款/clear，ResultRelease与ScopeRelease分账 |
| ConsoleHost / SurfaceToolHost | 两个internal static测试Host均提供 `internal static Task<HostHeldCall> RunAsync(SegmentationRequest request,FrozenFixtureSource source,FrozenProjectionBackend backend,BoundedWorkingSetSimulator workingSets,TimeProvider time,RuntimeLimits runtime,PreparedHostRootSlot root,Action<ResultUse,ComponentPage> consume,CancellationToken token)`；root先登记所有端口/fixture/配置强引用，再构造SegmentationService，返回的service先写root.Service后才调用§12.2，传入root.Calls作为originalOwnerHeld。构造是纯值且不取图/native/I/O；factory异常也finally走原根保留/归还。HostHeldCall/RunHostOnceAsync为§12.2同一测试helper；实际装配的二者为同Tests程序集internal可见，不把含内部类型的签名公开到外部DLL，不复制第二套收尾 |

原根预登记在构造source/backend/workingSets/service**之前**。测试组合根持容量1的`List<PreparedHostRootSlot>`（同lock，仅原Owner可写），先确认空后Add预备槽；这个外层根与§12.2的ticket字典是两层不同容器，不替换/清空已持有的HostHeldCall。`PreparedHostRootSlot`为测试internal sealed class，构造 `(SegmentationRequest request,RuntimeLimits runtime,TimeProvider time,ImmutableArray<FrozenTile> tiles,ImmutableArray<FrozenBackendCase> cases,BackendProfile profile,SimulatorFaultControl faults)`；只读属性`Request,Runtime,Time,Tiles,Cases,Profile,Faults`及`Dictionary<OperationTicket,HostHeldCall> Calls`（容量1）；另`FrozenImages:ImmutableArray<FrozenImageFixture>`初始空，由同Owner在source构造前填一次供C4多图强持，可空属性 `Images:IImagePlaneSource?,Backend:ISegmentationBackend?,WorkingSets:IWorkingSetSource?,Service:ISegmentationService?,CreationTask:Task?,Suggestion:SuggestionRequest?,SuggestionTask:Task<SuggestionResult>?,SuggestionExecution:CancellationTokenSource?,Error:Exception?`由同Owner串行填一次/保留原引用；不是模块DTO。每个构造返回即写相应root属性，异常也finally保留原槽，禁止先清槽再Add。完全闭合后先Dispose属于本组合根的CTS/对象，再移除外层槽；同步纯构造没有native/I/O，Create抛异常本身不证明以前对象已归还。这里只同步示例创建前Owner槽，§12.2已接收收尾行为不改。两个Host的主调用失败保留CallError；未闭合Returned HostHeldCall仍归原root，恢复触发用同ticket两轮Query/Recover/Release/Close而非Start。

两个Host从空组合根装配如下；`request/profile/tiles/cases/runtime/faults/time/consume/token`是本附录逐字段冻结的测试输入，Console与Surface分别取下表自己的完整request/case，不共享实例/槽。Host.RunAsync必须检查传入端口与root强引用为同对象、runtime/time/request身份匹配；不在Host内部重新创建第二组Simulator。该示例的外层槽由测试进程Owner持有至恢复结束，不是函数返回即丢弃的局部容器。

```csharp
// 原测试进程Owner预先持有 roots（容量1，同一个lock访问）。
var root = new PreparedHostRootSlot(request, runtime, time, tiles, cases, profile, faults);
lock (roots) {
    if (roots.Count != 0) throw new InvalidOperationException("原调用尚未闭合");
    roots.Add(root);
}
try {
    var source = new FrozenFixtureSource(request.Image, root.Tiles, root.Faults);
    root.Images = source;
    var backend = new FrozenProjectionBackend(root.Profile, root.Cases, root.Faults);
    root.Backend = backend;
    var ledger = new BoundedWorkingSetSimulator(root.Runtime, 131072, 2, root.Time, root.Faults);
    root.WorkingSets = ledger;
    // Surface组合根仅把ConsoleHost换为SurfaceToolHost，使用其独立mask输入。
    var hostTask = ConsoleHost.RunAsync(request, source, backend, ledger,
        time, runtime, root, consume, token);
    root.CreationTask = hostTask;
    var call = await hostTask;
    if (call.CallError is not null) root.Error ??= call.CallError;
}
catch (Exception error) { root.Error ??= error; }
finally {
    // Host内部在new SegmentationService返回后先写root.Service，再进入§12.2。
    // 若service已创建但helper未进入，仍有限Close；Waiting/抛异常保留根。
    if (root.Service is not null) {
        try {
            var closed = await root.Service.CloseAsync(TimeSpan.FromMilliseconds(250), CancellationToken.None);
            if (closed is { Status: DrainStatus.Drained, AdmissionClosed: true,
                OutstandingResultLeases: 0 } && closed.Pending.IsEmpty) {
                lock (root.Calls) {
                    if (root.Calls.Count == 0 && (root.CreationTask is null || root.CreationTask.IsCompleted))
                        lock (roots) { roots.Remove(root); }
                }
            }
        }
        catch (Exception error) { root.Error ??= error; }
    }
    // service未构造：只创建了无I/O/native的Simulator值对象时可以移除根；
    // factory原task未返回或已有任何Owner/账登记则保留，不用catch推定释放。
}
```

此例不替代§12.2收尾；Calls非空时原Owner使用同ticket两轮恢复，直到原helper的IoClosed/OriginalOwnerConfirmed确认后移除该Calls条目并Dispose其CTS，再Close复核后移除外层root。构造前/Host调用前错误无I/O且Service=null、CreationTask为空或真实完成、Calls空、三个Simulator无borrow/charge/执行登记时，原Owner可串行确认后移除root；任何一项未知继续保留。

**SG-ID-01 完整请求。** 仅身份编码/合成测试；非真实材料资格。Image字节为row-major `00 00 00 00 0f 00 00 00 00`，Image.Sha256与Origin.SourceHash均为 `e099346009a2e9607a5748d4732bf84245c7b608ccb1b286f9aa858b6347d7fc`。所有SHA字段下列重复hex值是明确的合成外部资产身份，不声称实际资格文件已获生产批准。OperationId=`golden`、RequestRevision=1；ParameterHash必须为下面131-byte向量hash。

| 请求成员 | 完整值（字段顺序严格沿§4/A.1） |
|---|---|
| ContractVersion / AlgorithmRevision / ParameterRevision | `0.2 / a / v` |
| Image | SnapshotId=i, Revision=r, ParentGridId=g, ParentGridRevision=r, Width=3, Height=3, Encoding=Byte, GrayUnit=gray, MinValue=0, MaxValue=255；Sha256如上。Origin=(RawScalar,SourceHash如上,PreprocessHash=`22`重复32次,TransformRevision=raw,ChannelKey=gray,ColorSpace=null,ColorEncodingRevision=null) |
| Domain | Full=[(0,0,2),(1,0,2),(2,0,2)]；D/W/ImageValid/ClassificationValid均Full，I=空、UnknownPatches=空、ContextPolicy=AllowValidExcluded、Revision=d |
| Method | FixedIntervalsSpec，Intervals=[(10,20)]；无Polarity字段 |
| Processing | MorphologySteps=空,Connectivity=Eight,FeatureStageId=raw,FeatureSet=[AreaPixels,CentroidRow,CentroidColumn,BoundingBox],FeatureFilters=空,FilterCombination=All,Tiles=(Revision=t,Cores=[(TileKey=c,Row=0,Column=0,Width=3,Height=3)]),Revision=p |
| Qualification | Revision=q,Sha256=`11`重复32次,Use=ResponseCandidate,QualifiedDomain=Full,HistogramBimodal=null,MaxSaturatedFraction=0,MinStatisticsPixels=1,ExpectedStrokeWidth=null,FallbackFrom=null |
| Limits | ProfileRevision=l,ProfileHash=`44`重复32次,MaxPixels=9,MaxRuns=128,MaxComponents=16,MaxEquivalences=64,MaxWorkingBytes=65536,MaxResultBytes=32768,MaxProjectionBytes=8192,Timeout=1秒,DrainTimeout=250ms,CleanupTimeout=250ms,MaxParallelTiles=1,ProgressInterval=10ms |
| Mask / Scale | Mask=null；Scale=(Revision=s,QualificationHash=`33`重复32次,AreaPerPixelMm2=0.25,ParentGridId=g,ParentGridRevision=r) |

Parameter Golden（131 bytes，SHA-256 `6a12fa424adf53e5093db84393a28a06787352163ed7541e958492b1e6cdd2ab`）：

```text
110000007365672d706172616d65746572732d763200000000010000000000000000002440000000000000344000000000080000000300000072617704000000
00000000010000000200000003000000000000000000000001000000740100000001000000630000000000000000000000000000000003000000030000000100
000070
```

Request Golden（1181 bytes，SHA-256 `73654f2fe35b4e66b68c2a56b5207c93a2a8ab88c71bae36683fc353a67fc103`）。只去掉下列hex的换行后解码，不将hex文本/JSON当规范字节：

```text
0e0000007365672d726571756573742d763203000000302e32010000006901000000724000000065303939333436303039613265393630376135373438643437
33326266383432343563376236303863636231623238366639616138353862363334376437666301000000670100000072030000000000000003000000000000
0000000000040000006772617900000000000000000000000000e06f400000000040000000653039393334363030396132653936303761353734386434373332
62663834323435633762363038636362316232383666396161383538623633343764376663400000003232323232323232323232323232323232323232323232
32323232323232323232323232323232323232323232323232323232323232323232323232323232320300000072617704000000677261790000030000000000
00000000000000000000000000000200000000000000010000000000000000000000000000000200000000000000020000000000000000000000000000000200
00000000000000000000030000000000000000000000000000000000000002000000000000000100000000000000000000000000000002000000000000000200
00000000000000000000000000000200000000000000030000000000000000000000000000000000000002000000000000000100000000000000000000000000
00000200000000000000020000000000000000000000000000000200000000000000030000000000000000000000000000000000000002000000000000000100
00000000000000000000000000000200000000000000020000000000000000000000000000000200000000000000000000000000000001000000640000000001
00000000000000000024400000000000003440000000000800000003000000726177040000000000000001000000020000000300000000000000000000000100
00007401000000010000006300000000000000000000000000000000030000000300000001000000700100000071400000003131313131313131313131313131
31313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131310000000003000000000000000000
00000000000000000000020000000000000001000000000000000000000000000000020000000000000002000000000000000000000000000000020000000000
000000000000000000000001000000000000000000010000006c4000000034343434343434343434343434343434343434343434343434343434343434343434
34343434343434343434343434343434343434343434343434343434343409000000000000008000000000000000100000004000000000000000000001000000
0000008000000000000000200000000000008096980000000000a025260000000000a02526000000000001000000a08601000000000001000000610100000076
00010100000073400000003333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
3333333333333333333333000000000000d03f01000000670100000072
```

| 顶层段 | 起始byte（0-based） | byte长度 |
|---|---|---|
| tag | 0 | 18 |
| ContractVersion | 18 | 7 |
| Image | 25 | 289 |
| Domain | 314 | 321 |
| Method | 635 | 24 |
| Processing | 659 | 86 |
| Qualification | 745 | 172 |
| Limits | 917 | 161 |
| AlgorithmRevision | 1078 | 5 |
| ParameterRevision | 1083 | 5 |
| Mask | 1088 | 1 |
| Scale | 1089 | 92 |

| SG-ID反例 | 字节数 / RequestHash | 断言 |
|---|---|---|
| OperationId/RequestRevision换新，或executionToken变更 | 1181 / `73654f2fe35b4e66b68c2a56b5207c93a2a8ab88c71bae36683fc353a67fc103` | 请求内容hash不变，但ticket不同；同实例同OperationId不同revision按身份围栏拒绝，不把hash当允许重复执行 |
| SG-ID-02：仅Domain.Revision=e | 1181 / `99b0428bf7600719a1f95a0d0eb691c0e99b3ee9e3b395baa2d0342abbb7093e` | ParameterHash保持不变；RequestHash必须变化 |
| SG-ID-03：仅Limits.MaxResultBytes=32769（int64从offset 1026起；MaxProjectionBytes仍为8192） | 1181 / `ef2a78acf56396b0ee5eb67030e2aeb40f5706a550ed3e725a67e101f21aa381` | ParameterHash保持不变；RequestHash必须变化 |
| SG-ID-04：仅Scale=null | 1090 / `93d5f9e53cd56514a2438f10a0abd0ba78bbcea08a72da8e200a1185aa10f772` | ParameterHash保持不变；RequestHash必须变化 |

两种独立字段编码路径在文档辅助内存计算中得到同一1181-byte/131-byte与上述hash，只是规格复算，未执行模块C#。SG-C1实现时测试必须从本表构造完整request、逐段比较offset/bytes并调用唯一SegmentationIdentity，不能只hash抄来的hex宣布请求编码正确。SG-C2用同request新ticket绑定冻结Output，SG-C3核F={(1,1)}、B=Full−F、U空及面积1/质心(1,1)/bbox四个槽；SG-C4从其独立search/holdout的完整请求变体构造候选，不把同一fixture放两集。

**两Host/SG-C2～C4软件Profile。** runtime=(InstanceId各自console/surface,MaxActiveOperations=1,QueueCapacity=1,MaxRetainedResults=2,MaxTombstones=256,TombstoneRetention=1秒,MaxEventBacklog=32)，Simulator工作容量131072 bytes、sourceSlots=2，单case Plan=(Supported=true,ProfileHash=注入BackendProfile.Sha256,RequiredWorkingBytes=32768,RequiredResultBytes=8192,RequiredSourceSlots=1；纯mask无gray则0,Errors=空)。BackendProfile=(Revision=sim,Sha256=`55`重复32次,AdapterVersion=sim-v2,HalconRuntimeVersion=null,SupportedMethods=本例方法,SupportedEncodings=本例Byte,MaxTileWidth=32,MaxTileHeight=32,MaxReconstructionPixels=1024,MaxReconstructionRuns=128)。未知native峰值=null，不填真实HALCON版本。ConsoleHost用SG-ID-01；SurfaceToolHost将方法显式换RegisteredMask、Scale=null且重算Parameter/RequestHash：Mask.ClassKey=class1、Foreground={(1,1)}、Background=Full−F、Unknown=空、Objects=空、Maturity=ExternalAlgorithm、ModelHash/Version=null、InputHash/PreprocessHash与Image一致，Mask.Revision=mask1、Sha256=`66`重复32次、BackendVersion=external-v1、ClassificationThresholdRevision=mask-thr1、ParentGridId=g/Revision=r、Objects=空，MaskSpec=(mask1,class1)；Domain/资格保持、ParameterRevision=surface-v、AlgorithmRevision=a，hash按新内容复算。其余版本/资格保持；这是第二组合根，不共享产品数据/Owner。

测试输出不是由托管threshold生成：Simulator冻结raw StageRegions、一个Complete组件和上述四项FeatureValue（有效槽按A.2），Filter=Unknown/Reasons空交Core重算Accepted；Summary=(Complete,9,1,8,0,Complete,1,false)，Quality=(q,ResponseCandidate,true,1,0,空)。StageReceipt为Console的raw/threshold、Surface的raw/registered_mask，ParameterHash各自重算、KernelRuns/UsedThreshold/StatisticsPixels=null，其余域hash是SHA256域标签`seg-region-v2`+A.1编码的canonical PixelRegion（只一次标签，非string拼接）；InputDomainHash=raw valid Full，OutputDomainHash=raw F，SupportHash=Full，Elapsed由时钟实际记录；FrozenOutput模板中的Elapsed/Resources为零初值（PeakNativeBytes=null），Simulator在Execute只绑定本次ticket/FragmentKey、实际Elapsed/Resources，几何/Feature/Quality保持冻结。所有Provenance由Core根据请求/模拟Profile组装。ComponentKey由冻结输入/语义生成；每次Execute只以本次ticket重绑定FragmentKey，不重算像素/特征，按§7.1固定公式生成，无HALCON handle。Resources记录实际Simulator分配/源borrow，错误空；BackendOutput外层Ticket/RequestHash/ProfileHash绑定本次调用。

**SG-C4完整合成输入绑定。** 四个fixture的Request逐字段沿SG-ID-01，唯一差异为Image.SnapshotId、中心像素、Image.Sha256/Origin.SourceHash；OperationId各用下表SnapshotId，RequestRevision=1，其余Origin/格/Domain/Processing/Qualification/Limits/Scale完整保持。TruthForeground={(1,1)}、TruthBackground=Full−F；FixtureHash按域标签`seg-suggestion-fixture-v2`依次写完整RequestHash、TruthForeground、TruthBackground（编码沿A.1），避免用任意ID假装独立样本。每图FrozenTile为(0,0,3,3,3,对应9-byte数组,Full,空Missing)。四图都是合成软件反例，不证明真实标注泛化。

| 集 | SnapshotId | 中心Byte（其余8格0） | Image.Sha256 / Origin.SourceHash |
|---|---|---|---|
| Search | search-1 | 11 | `ea24d33b8cc70d2524d569726e6e769185b4ad65a682659e05ea97d4712f8a6e` |
| Search | search-2 | 15 | `e099346009a2e9607a5748d4732bf84245c7b608ccb1b286f9aa858b6347d7fc` |
| Holdout | holdout-1 | 16 | `6b8c2a4d795e67c47e54a3391275d13205ed66ca67c863270da1875f7fa09f72` |
| Holdout | holdout-2 | 19 | `50d1d6fed33700f6a4d88931b641cfba5cdb9dcf8abb591f38dcccb30d2cf86e` |

SuggestionRequest=(SuggestionId=sg-c4,Search=两Search fixture,Holdout=两Holdout fixture,Candidates=[FixedIntervals(10,20),FixedIntervals(14,18)]且各Processing沿SG-ID-01/ParameterHash重算,Weights=(1,1,1),MaxEvaluations=8,MaxCandidates=2,Timeout=1秒,MaxWorkingBytes=65536)。每个fixture请求保持原ParameterRevision=v；评价派生修订固定`suggestion:sg-c4`。每次评价OperationId按A.4的`seg-suggestion-operation-v2`域标签依次编码SuggestionId/ParameterHash/FixtureHash/标签search或holdout，四个字符串均用A.1编码后SHA256；无模糊拼接。评价RequestHash用替换后Method/Processing/ParameterRevision重算，不依OperationId。八个FrozenBackendCase均按该评价RequestHash预登记：候选(10,20)四图F均中心；候选(14,18)在11/19图F空、B=Full，在15/16图F中心；全部U空。F空case组件空、ComponentCount=0、ForegroundEmpty=true；有F的沿上述完整投影重绑定身份/回执。Search宏平均成本分别0与1/18，Holdout只展示0与1/18，(10,20)排名第一；完全同分才按UnknownFraction/ParameterHash破序，不按留出改冠军。

C4在同一个root构造source前写`FrozenImages`为这四个FrozenImageFixture，再用多图FrozenFixtureSource重载；BackendCases恰为上述八例，Profile支持FixedIntervals/Byte，Plan/有限账沿软件Profile。原Owner先写root.Suggestion与root.SuggestionExecution，再构造并保存独占SegmentationService至root.Service；调用SuggestParametersAsync后立即AsTask一次写root.SuggestionTask，后续只观察同task。外层250ms等待到期只停止观察，finally取消该CTS，有限Close得到当前评价原ticket，再两轮Query/Recover；全部task/lease/Close确认前保留root，沿A.4/§8接续，不将超时当SuggestionResult。不会为每fixture另造service或递归公开Start。故障例固定在第二评价BackendExecute闩锁暂停，取消后当前task/root/ticket仍保留，finally解除闩锁，确认原lease释放/Close后不执行第三评价；另让首个ResultRelease失败一次，原ticket恢复成功前不开始第二评价。

测试Benchmark配置放在Core.Tests的 `Fixtures/SegmentationBenchmarkCases.cs`（只在获准实现时创建）：C1测校验/编码、C2测Queue/Release/故障、C3测投影校验/三值筛选、C4固定Candidates=2、Search=2、Holdout=2、MaxCandidates=2、MaxEvaluations=8，测2×2搜索+2×2留出=8次上限。冷态单独1次，热态固定预热2次/测量20次、最低有效n=20；每次调用使用完全闭合后新建的独立InstanceId组合根，沿用冻结Request/SuggestionId/hash和八case，不在同实例重发ID；冷热区分进程/JIT预热而非未声明的native池、观察250ms、每例10秒/外层120秒，负载与fixturehash固定；资源上限以上表为有限合成控制，P50/P95/P99/失败删失按DEV-GOV-010，客户时延/吞吐目标=null即NotEvaluated。它有明确测试/Profile消费者，不新增独立报告/产品依赖，不声称软件/性能已通过。

