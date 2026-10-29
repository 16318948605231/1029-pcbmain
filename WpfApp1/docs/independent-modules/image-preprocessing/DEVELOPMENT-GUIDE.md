# 图像预处理独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`P0, P1, P3`

- 模块：`image-preprocessing` / `IM-021`；来源映射：`PKG-014`、`SM-011`、`DEV-VIS-021C`。
- 文档版本：`0.5.0-prep`；P0/P1/P3 API 仍为 `0.4`，P4 保存 API 仍为 `0.4.1`、显示挂接增量为 `0.4.2`，P2 装配增量为 `0.1-prep`；日期：`2026-10-11`；任务：`IM-REVIEW-20261009/image-preprocessing`。
- 永久会话、写入 Owner：`01a10306-f2a8-79e3-b466-b8fd194666ec`，见 [模块索引](../MODULE-INDEX.md)。历史 accepted 仅表示文档接收。
- 状态：`DesignReview`；P0/P1/P3 保持主控已接收的 `ModuleCoreImplementationReady（仅规格准备）`，P4 保存查询指导内容限定接收保持。2026-10-11 主控限定接收附录E.1–E.6的P2公开装配、CPU帧桥、独立Owner及完整软件双Host/原Task恢复确定指导内容；P2真实HALCON/稳定RuntimeOwner/CPU接线/原生资源/Golden/运行/性能仍 `PreparationIncomplete`，不标纯Core Ready。P4真实WPF/Host持久保存恢复及运行资格仍 `PreparationIncomplete`，整模块/P5未完成。内容接收不声明代码、构建、运行或生产通过。
- 固定基线：C# / .NET 10；可选 WPF / 本机 DevExpress 25.2.3；HALCON 26.05 经 `ImageLibDotNet.cv2`。不扫描 AsunImage 内部、不核验算子是否存在、不另接 halcondotnet.dll。具体 C# 类型/重载/封送确有歧义时才查公共签名或消费工程编译。
- 全范围文档准备结论：2026-10-11 本永久原会话按当前架构完整范围收口，见§16.1、附录F。P0–P5可决定的软件设计已明确；新增编辑/挂接/显示投影、草稿codec、参数模板/候选、分块容量与验收规格只表示文档准备，不提升既有代码/真实运行/产品门。总控只接收状态，不再等待其代审模块正文。

## 1. 职责、非目标与切片

本模块提供不可变预处理图规划、通道/数值/几何/有效域处理、派生证据、有界参数建议和可选编辑控件。分割消费者使用固定归一化/平滑图；OCR/读码消费者使用显式通道与裁剪/缩放图。双方引用同一 Core，不能按消费者名称改变算法。

不包含目标发现/关联、缺陷判定、客户阈值、工艺放行、复判、设备动作/触发、业务编排、私有数据库、训练、隐式 AI、任意脚本、隐式配准/去畸变/补洞。显示 LUT、伪彩、亮度窗口与标注是 `PresentationOnly`，不改变算法输入；结果不覆盖原图或业务事实。模块全部核心能力可无 UI 调用。

| 切片 | 实现职责与唯一合同 | 依赖/资格边界 |
|---|---|---|
| P0 GraphPlanner | §3、附录 A：图/端口/参数、DAG、规范字节/hash、规格/支撑/last-use；纯托管无像素 | ModuleCoreImplementationReady（仅规格准备）；无帧、租约、native、UI、IO |
| P1 ExecutionCore | §4–7、附录 B：接纳、幂等、查询、执行端口、预算、取消排空、结果一次交接；有界 Simulator | ModuleCoreImplementationReady（仅规格准备）；真实 image-frame 映射是 P2/P5 门 |
| P2 HalconBackend | §7/8、附录E：公开工厂、CPU帧桥、稳定runtime借用、真实输入/节点、有效域、分块、导出/释放 | 附录E确定指导内容限定接收；真实HALCON/稳定RuntimeOwner/CPU接线/原生资源/Golden/运行/性能保持PreparationIncomplete，不标纯Core Ready |
| P3 ParameterAdvice | §9、附录 C：有限候选/样本/评分、排名与草稿应用 | ModuleCoreImplementationReady（仅规格准备）；评分值与标注来自消费者，不获得发布权 |
| P4 WpfEditor | §10、附录 D：可嵌入控件、双图/参数/诊断联动、三语与预览版本、保存身份及有界查询 | 保存查询指导内容已接收；真实 WPF/Host 持久保存恢复及运行资格仍 PreparationIncomplete，含 25.2.3、1920×1080、键盘/UIA/当前OS DPI 验收 |
| P5 HostIntegration | §11/15：分割及 OCR 两宿主、公开帧映射、发布/回退 | 正式平台映射、消费者 Profile、真实样本/性能/现场资格 |

P0 收窄不能替代整模块完善。常规技术语义在本页明确；缺客户值只阻相应用途，不阻无关 Core。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ImagePreprocessing.Core` 及 `Asun.Modules.ImagePreprocessing.AsunImage` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.ImagePreprocessing.Wpf`（编辑控件）可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。P0 GraphPlanner 与 P1 ExecutionCore 为纯托管无像素路径，因此可在无 WPF、无 HALCON runtime、无 AsunImage 程序集的宿主中运行。

**Blazor/Web 宿主中的预处理图发布**：预处理结果是 `image-frame` 意义上的派生平面，Web 端展示时由服务端按 §11/15 已冻结的公开帧映射发布，浏览器只消费发布后的平面引用或按 tile 粒度取字节。约束：
- 浏览器端不重算归一化、不重建 LUT、不自行裁剪/缩放；显示 LUT、伪彩、亮度窗口属 `PresentationOnly`，不改变算法输入
- 预处理图的 `EffectiveDomain` 必须随平面一起传递，坐标逆变换由 `coordinate-geometry` 负责（见 [IM-007](../coordinate-geometry/DEVELOPMENT-GUIDE.md) §1A）
- 发布/回退走 P5 HostIntegration 的已冻结路径，不为 Web 端另建一条旁路发布链

**AI 推理 Tiling 适配**：本模块是 `ai-inference` 分块推理的**上游预处理来源**，但推理链路的 tile 请求与租约由 `image-frame` 拥有，本模块不参与分块编排。适配约束：
- 分块推理所需的归一化/裁剪/缩放图，必须作为已发布的预处理平面被 `image-frame` 按 tile 粒度切出；本模块不实现 `RequestTileAsync`，也不持有 tile 租约
- 预处理的通道/数值/几何处理在**发布前**一次完成并写入平面元数据；推理侧不得对 tile 再做隐式归一化，否则同一像素在两段链路得到不同数值
- 分块边界处的 halo/支撑域不足由本模块在发布时如实标注，不在推理侧补边

**HALCON 备选交叉验证适用性**：本模块是 2D 视觉链中双跑 CI 的**数值层落点**。约束：
- P2 HalconBackend 的 §7/8 路线与一条纯托管参照路线在**同一 Golden 数据集**双跑：通道/数值归一化、几何变换、有效域与派生证据逐项比对，差值超容差即 CI 失败并产出差异报告
- **已知的必然差异，不得抹平**：§7 路线依赖 HALCON 的邻域/形态学语义与 `mean_image` 等算子的实际响应，托管参照只能覆盖"原始值矩和"类可精确复算的量。凡涉及邻域 halo、形态学次序、算子内部量化或 OpenCL 路径的项，双跑只登记差异并标注来源，**不作为失败判据**；只有可精确复算的数值项进入容差门禁
- 归一化必须以**实际位深和实际直方图**为依据，不得用容器上限或显示 LUT 反推；托管参照同样按原始值计算，否则双跑只是把同一错误复制两遍
- HALCON 仍是生产路线；托管参照只作交叉验证与降级保险，不作发布依据。OpenCV 仅在需要第三方独立参照时使用，固定 commit `a0cda081f8d769f40ab2f4904738b4787b44d07c` 的本地已读快照见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)，不引入平行生产算法
- 双跑不得成为引入未批准算子或未批准预处理节点的理由；新节点仍按 §3/§4 的图与端口规范先入契约再实现

## 2. 工程、依赖与允许路径

P0/P1/P3 唯一 namespace：`Asun.Modules.ImagePreprocessing`；Core：
`src/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.Core/Asun.Modules.ImagePreprocessing.Core.csproj`。
唯一 Core 测试/最小 Host：
`tests/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.Core.Tests/Asun.Modules.ImagePreprocessing.Core.Tests.csproj`。工程尚未创建，不提前建空项目。

P2 可选工程在同 src 模块目录，名称 `Asun.Modules.ImagePreprocessing.AsunImage`、namespace 后缀 `.AsunImage`；P4 名称 `Asun.Modules.ImagePreprocessing.Wpf`、namespace 后缀 `.Wpf`。相应测试在同 tests 模块目录，工程名称加 `.Tests`。P2/P4 依 Core，Core 不反向引用 native/UI；宿主组合各公开端口，不引入强制 DI 框架、静态可变状态、产品 ViewModel、私有表、SDK 句柄或隐藏窗口初始化。P4为net10.0-windows/UseWPF=true的Library，其.Tests为同target/UseWPF=true的BCL Exe，直接引用P4/Core及本机25.2.3的Xpf Core/Grid/PropertyGrid/Docking/Charts，所需配套程序集取这些已安装组件的原引用，不从NuGet替换。附录F的纯codec定义由Host适配器消费，不新增Core IO或另一独立包。

P2 同一可选 DLL 的公开装配见附录E：额外引用 `Asun.Modules.ImageFrame.Core` v0.2、`Asun.Modules.ImageFrame.Resources` v0.1 与既定 AsunImage；不消费 Tiles/Halcon/GPU 适配，不反向扩充 image-frame。CPU桥只调用其公共 Resources API。P2 为 net10.0 Library，测试/最小双Host为同名 `.Tests` net10.0 BCL Exe，显式引用 P2/Core/上述帧 DLL；没有 WPF/DevExpress/平台 Shell 依赖。

本轮只写本指导。未来获准实现只写相应切片工程/测试目录；禁止其它模块、共享合同/页面/入口/进度/登记、客户项目、tools、技能、来源快照和 AsunImage 内部。实际代码开工前主控绑定权威仓库/分支或可审计代码快照；当前无 .git 不阻文档修订。

Core 与测试均用 `Microsoft.NET.Sdk`、`net10.0`；Core 为 Library，测试为 `OutputType=Exe`，Nullable/ImplicitUsings 开启。测试仅 ProjectReference 到 Core 与 .NET BCL（包括 System.Collections.Immutable），无 PackageReference/待选测试框架。沿 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门) 的确定性断言/固定时钟/可控闩锁，测试用例总截止点 120 秒，外层进程截止点 180 秒；任一失败、未完成或必需项跳过返回非零并列用例 ID。

未来实现的唯一有限验证命令（本轮未执行；由执行环境给每条命令 180 秒进程上限）：

```powershell
dotnet build src/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.Core/Asun.Modules.ImagePreprocessing.Core.csproj -c Release --disable-build-servers
dotnet run --project tests/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.Core.Tests/Asun.Modules.ImagePreprocessing.Core.Tests.csproj -c Release --no-launch-profile
```

`dotnet test` 无报错不等于执行 Exe 断言。真实 HALCON/WPF 验证另按适用切片运行，不借 Core harness 冒充。包只发布已实现切片的 DLL/API/节点方法/依赖/Golden引用/限制/回退闭包，P0 不捆绑 P2/P4。

## 3. 图、参数与规格不变量

### 3.1 冻结、确定性与校验顺序

P0 唯一公开类型见附录 A。Plan 入口深冻结全部集合并将全部double参数的−0规范为+0，GraphSnapshot/Definition/执行使用同一规范值；拒 null/default ImmutableArray、未知枚举/NodeParameters 子类、NaN/Infinity。ID 为 ASCII `[A-Za-z0-9._-]{1,64}`，Ordinal 比较；图修订为非空可打印 ASCII 1..128。输入/输出键在各自集合唯一，NodeId 唯一，重复节点用 DuplicateNodeId，其它重复键用 InvalidIdentifier。InputGridKey 是已配准像素格身份，不是采集帧身份。

图非空，声明输出非空；每个节点和源声明必须被输出的上游闭包使用，孤立项拒绝 UnsupportedParameter，不隐式删掉改变图。GraphInput / NodeOutput / DomainInput 显式区分；所有节点只产一个 image。DomainLimit 的 mask 只能引用 DomainInput，独立离散域，不拿图像灰度/前景当有效域。

Kahn 拓扑：零入度优先队列按 NodeId Ordinal；出边排序后递减入度；同一前驱的多端口只计一次拓扑边。Terms、通道、矩阵行列次序不重排。Required 不得传递依赖 OptionalForPartial；声明输出继承其生产节点 Required/Optional，无隐式覆盖。

校验阶段固定：Envelope/预算→Parameters→References/端口→Topology→Dependencies→Shape/支撑→Canonical→Planning。每阶段错误按 NodeId、FieldPath、Code Ordinal；阶段失败即不进入后阶段。已取消 token 优先；阶段/循环/每 4 KiB 编码块检查单调期限。失败不泄漏可执行前缀：GraphSnapshot=null、Nodes/CanonicalBytes 为空、GraphHash=""。P0 不保留请求，无事件/Dispose/Close，无资源排空；并发 Plan 只用本次局部状态，同 ID 重复不是服务幂等事务。

### 3.2 节点参数合同

下面范围是模块工程域，不是客户阈值或算子上限。无运行期隐式默认；UI 可填模板，进入图后必须显式。MethodVersion=1。像素 UInt8/UInt16/Int16/Float32 对应 byte/uint2/int2/real；HALCON real 为 Float32。当前 Float64 输入拒绝，double 控制参数不许诺 Float64 像素。

| 节点 | 参数/单位/输入端口 | 输出与拒绝边界 |
|---|---|---|
| SelectChannel | image；ChannelKey 精确匹配 | 单通道，原类型/尺寸/域/格；不猜RGB/BGR索引 |
| LinearCombine | image0..imageN-1，N=Terms.Length=1..8；Terms、Offset double [-1e6,1e6] | 同格/尺寸、单通道；Float32；按 Terms 顺序累加，再加 Offset |
| BinaryArithmetic | left/right；Add/Subtract/Multiply/Divide；Scale/Offset 同范围；Divide 必填 MinAbsDenominator 有限 >0，其它操作必须 null | 单通道 Float32；`(left op right)*Scale+Offset`；除法剔除绝对分母小于阈值的域 |
| ColorTransform | image；InputKeys/OutputKeys 各1..4；MatrixRowMajor、Offsets [-1e6,1e6]；InputSpace/OutputSpace 稳定标识 | 已声明线性值空间矩阵；InputKeys 必须等于输入通道原顺序；Float32，不猜gamma/Bayer/标定 |
| FlatField | image/reference；Gain/Offset 同范围；MinAbsDenominator 有限 >0（参考数值单位） | 同格/尺寸、单通道；image/reference*Gain+Offset；不冒充暗电平/颜色校准 |
| NeighborhoodFilter | image；Mean KernelWidth/Height 奇数1..255、MaskSize=null；Gaussian MaskSize=3/5/7/9/11、Kernel字段null；Border=Reflect | Float32 同尺寸/通道；非适用字段必须null；核宽高各小于对应尺寸2倍，避免未冻结大核重复反射 |
| Sharpen | image；MaskWidth/Height 奇数3..255，且各小于对应尺寸2倍；Factor[0,100]；Reflect | Float32；冻结 HALCON emphasize 的舍入，不换“等价公式” |
| Normalize | image；FixedRange/PerFrameRange；OutputMin<Max 有限；Fixed 必填 InputMin<Max，PerFrame 必须null | Float32，同格/通道；每通道独立范围，不隐式clamp；常值 PerFrame 拒绝 ConstantRange |
| Crop | image；Row/Column int>=0；Width/Height1..32768；唯一 RejectOutOfBounds | 原类型/通道；当前输入内边界，新尺寸与格变换 |
| Resize | image；TargetWidth/Height1..32768；NearestNeighbor/Bilinear | 原类型/通道；仅完整有效矩形；禁止Scale第二权威、隐式抗混叠 |
| DomainLimit | image/mask；mask=DomainInput，宽高/InputGridKey匹配 | 域交集、矩阵尺寸不变；不宣称节省像素内存 |

图像输入通道 1..16；算术键统一 derived，颜色键为 OutputKeys，Select 取源键，其它保持有序键。点运算域取交集，Divide/FlatField 再剔小分母。坐标格须一致，不能只对尺寸；同尺寸不同源只有宿主先提供真实配准证据后才能使用同 InputGridKey。

算术/颜色/滤波/锐化/归一化必须先 convert_image_type(real) 再运算，禁止 byte 先减/乘后转换。Float32 中间量及控制系数产生的 Mult/Add 必须有限且可表示，超界 NumericInvalid。数值节点统一 Float32，不隐式量化整数；byte/uint16 下游须未来显式版本化量化节点（舍入/裁切/域/误差），当前不授权凭 convert 默认裁切实现。显示 byte 仅 PresentationOnly。

### 3.3 Crop、格与有效域

Crop 以该节点当前输入尺寸 checked(Row+Height)/checked(Column+Width) 校验，非总是原帧。宽高零/负/超范围→ParameterOutOfRange；负坐标、加法 overflow、右下越界→CropOutOfBounds。合法边内1×1通过；padding/clip是未登记能力，拒绝 UnsupportedParameter，不取绝对值、不补零、不裁边。crop_part 本身可右下越界并限域，本模块预拒。

P0 Shape 的 GridTrace 是 InputGridKey 加有序 Crop/Resize 纯参数路径；点操作不改路径。多输入仅接受逐字段相同路径，宁可拒绝尚未证明等价格，也不猜注册。Crop/Resize 恒等尺寸且零平移时不追加步骤；其它参数追加，checked尺寸传播。P2 输出坐标回执保留相同路径，坐标服务/宿主用对应方法版本提供映射；Crop 的精确映射为输入(row+Row,col+Column)。Resize 遵 HALCON 采样约定，§8要求坡度/脉冲 Golden 绑定中心/边角及实际映射；未验证映射不显示坐标叠层、不授计量资格，不能自行写“除Scale”声称精确。恒等Resize仍执行节点并核runtime/域，只是GridTrace无新增几何步骤；不能因不追加步骤跳过计划节点。

源有效域 V、请求限制域、下游批准排除域、二值前景、显示补值不同来源。DomainInput 只是传入的离散请求限制，输出=V∩mask；模块不批准免检。空有效输出→OutputDomainEmpty，不等无缺陷。孔洞/支撑不足不得变零，物理图边不等孔洞边。

RawSelection 仅像素未数值运算，仍有共享矩阵 Owner；Crop/DomainLimit 为派生几何/域证据，不能伪装采集原件。派生回执保留源内容/域/修订/通道、图/schema/method/runtime、格变换、输出规格/有限性及范围。端点0/255不证明实际裁切；不可观测内部 clipping 标 NotObserved，不编统计。

## 4. 计划与输出闭包

成功 GraphPlanResult 必须携带完整深冻结 GraphSnapshot（源/域声明、节点参数/输入绑定、声明输出）与拓扑 PlanNode；PlanNode 的 Definition 为该快照节点，带 Shape/LocalHalo/RequiredInputHalo/RequiresGlobalStatistics/WholeFrameBarrier/LastUseOrder，执行无需从 UI、旧 JSON 或哈希逆猜参数。CanonicalBytes 是同一快照的规范编码，不是另一份可变图。

RequestId/时刻/语言不进入 GraphHash；GraphId/GraphRevision/schema/method/有序参数/声明格/端口/域模式进入。节点容器排列不改 hash，Terms 改序会改 hash。附录 A 唯一编码/错误；不提供存储/JSON/公开解码器。

P1 接收完整 ProcessingGraph+ExpectedGraphHash，重新 Plan 并核 hash；不信任外部 new/with 伪造的成功结果或 PlanNode。最终 PreprocessResult 见附录 B：Succeeded 为全部 Required 和声明输出完成；PartiallyCompleted 只在显式 AllowCompletedNodes、Required 全部完成且失败局限 Optional 闭包时成立，输出仅声明且已完成项，CompleteGraph=false。Atomic 默认由宿主显式填写；Required 失败、取消、期限、系统资源/完整性/runtime故障均不允许部分输出。

Rejected/Cancelled/TimedOut/Failed 的 Outputs 为空，不返回原图/上一步冒成功。每个 DerivedImageRef 有 OutputKey/Shape/域/坐标/源回执/独立 Owner，不含业务 PASS。节点内容/参数 hash 与含耗时诊断回执分开。

operation 只允许一次 TryTakeResult 原子交接整个结果；Query/Wait 只返值快照不复制 Owner。尚未交接时 operation 拥有输出，Close 须收回并释放；交接后输出 Owner 独立，不由 executor.Close 关闭。下游共享必须独立只读 borrow；OutputOwner.Close 停新borrow，等待在途borrow归还，超时仍保留 Owner/计费。

## 5. 服务、幂等、状态与事件

公开 API/局部端口闭包唯一见附录 B；不含产品 DTO 或 native 句柄。Start 的无资源预检检查图/hash/声明/预算/运行时策略后接纳；实际 Acquire/import 是已接纳阶段，错误须排空后失败。一个 executor 最多一个非终态操作，无内部队列；多实例共享预算，不能丢正式帧或偷偷缩图。

RequestId+RequestHash 同内容返回原 operation；相同 ID 不同内容 Conflict。RequestHash 由模块按附录 B 投影重算，不接受宿主伪造身份。每实例最多 MaxRequestsPerInstance=1..4096（显式设置）个墓碑/operation；达到上限返回 BudgetExceeded，直到整个实例关闭后新实例新epoch，不能清掉旧墓碑让旧ID重跑。重复墓碑在 Closed 时仍可Query；已交接结果重试只查值快照。未知身份 NotFound，不从 Query 启动。

状态 Validating→Running→Completing→Completed；取消/期限/故障停止派发，转 Cancelling/Draining。Start的本次Timeout从方法进入即开始，预检Plan耗时也计剩余，接纳时保存该最早单调截止点，不给native续期。Outcome 一旦选定不覆盖：先锁内记录先发生的执行失败、取消或期限；执行验证/导出完成与取消竞争以同一提交门线性化。内部待提交Outcome=TimedOut时，native未退出仍为Draining、IsTerminal=false且公开Outcome=null，不先发TimedOut终态；DrainTimeout只界定本次观察，不证明退出。

WaitAsync 的 waitLimit/waiterToken 只结束等待，返回当前快照及 WaitOutcome；不取消 operation。请求token/RequestCancellation 才取消执行。单调执行期限在 Start 接纳时固定，导入/节点/全域归约/tile/导出/验证共用剩余预算，不每节点续期；UTC仅诊断。

CloseAsync 原子停新准入并取消未完成操作，等待本实例输入/中间/未交接输出；已交接输出由其Owner关闭。观察期限到返回 Released=false，保留恢复句柄和真实Owner/预算；后续Close仅重试未完成阶段，不能空Dispose伪成功或重复析构。依赖生命周期归宿主，Core 不关共享provider/backend/budget。锁外 native/回调；回调内Close只能有限返回，不同步等待正在回调的自身。

Observer 用不可变 ProcessingEvent(RequestId,Sequence,Kind,NodeId,State,Code)。单请求Sequence递增，关键事件通过固定64槽有界串行通知；v1节点一次一条执行链，不会有并发64节点突发。每executor最多一个固定通知泵，回调完成前不建替代泵；事件只携小值无像素/Owner。通知不在状态锁内；进度可合并，接纳/失败/排空/终态不得静默丢。Observer阻塞不得占核心线程：独立通知泵，达到槽上限记 ObserverUnavailable 并停该订阅（核心值快照仍可Query），不为无限等待回调阻断资源释放；通知顺序不证明业务提交。若回调永久未退出，operation可在图像资源真实归还后终态，executor.Close仍Released=false并保留通知泵/依赖及有界诊断缓冲；不能伪造线程已停。Host待回调退出后重Close，不强杀线程。

无资源预检：Received→ValidationCompleted(Rejected)→Rejected；不发 Drained/ResourcesReleased。接纳：Accepted→PlanBound→NodeStarted/Completed/Failed→OutcomeRecorded→Drained→ResourcesReleased（输入/中间归还；输出待交接）→Terminal。NativeDrainUnknown/ReleaseFailed 保持Draining并隔离实例，只有实际退出/关闭完成才终态。终态后Observer可关闭，订阅关闭不取消执行。源断连但不变borrow仍有效可继续；CheckCurrent失效则停止派发/发布并排空，不重连设备、不换新源。

## 6. 错误、保留内容与恢复

所有诊断为稳定 Code/Stage/NodeId/FieldPath/ResourceKey/Retryable；ResourceKey=`Preprocess.`+Code，Host本地化。不显示 native 异常/堆栈，不把失败降为警告。P0 Code闭包在附录A，P1扩展在附录B。

| 错误链 | 输出/保留与安全恢复 |
|---|---|
| null/非法ID/重复/未知字段/未登记方法 | 预检拒绝；定位字段，改图并新修订 |
| 环/引用缺失/端口冲突/Optional→Required | 计划为空；不删节点或重连替用户修图 |
| 参数/Crop越界/类型或格不符 | 保留草稿；无native前拒，源运行期不符则排空失败 |
| 注册/域失效/空输出 | 不补帧补零，不把空域当PASS；换完整可信输入新请求 |
| NumericInvalid/ConstantRange/BackendError/RuntimeDrift | 清输出/归还资源；绑定已验证图/runtime新请求，不自动替路线 |
| BudgetExceeded/ConcurrencyViolation/Conflict | 分配前拒或停止派发排空；查原操作、降低负载，不扩大预算或丢正式输入 |
| Cancelled/TimedOut | 真正排空后终态；等待超时不等执行终态 |
| NativeDrainUnknown/ReleaseFailed | Draining 或 Close.Released=false，Owner/预算保留；隔离并显式查询/Close，不重用句柄 |
| GraphRevisionMismatch/PersistenceCorrupt/RevisionUnavailable | 未知/损坏闭包拒绝；宿主显式旧闭包回退，不借缓存恢复成功 |
| Closed/NotFound/ObserverUnavailable | 停准入/身份不存在/通知停用；Query仍为真状态，不能自动重跑 |

P0未知JSON字段由宿主严格解码拒绝，P0本身无JSON IO；未知参数子类/枚举仍本地拒。Retryable只表示再次观察/显式恢复可能，不能以true自动重复副作用。

## 7. Owner、累计支撑、统计与分块

所有输入Acquire获得独立只读borrow，不释放宿主原lease。共享矩阵算子 access_channel/append_channel/同类型convert 的新 iconic 对象不证明独立像素；输出交接用copy_image深复制或显式保留底层Owner，本版固定copy_image导出。copy_obj不是像素复制。

checked reservation 先于分配；源实际RetainedCapacityBytes、输入复制、各同时活中间量、域行段/tuple、tile+halo、统计缓冲、导出副本都累计。P0只给形状/last-use及像素逻辑估算，不冒 native workspace 硬上界；P1预留硬管理额度、后端native额度，后端未知workspace标 SoftObserved。真实allocator不能保证硬上界时不称hard guarantee。释放失败仍占账，无Owner丢失；v1 CacheMode=Disabled，不引未定义缓存端口。

邻域输出有效域固定用HALCON二值支撑路线：gen_image_const(byte)→paint_region(整图矩形,0,fill)显式覆盖全部像素（不依赖init_new_image）→paint_region(V,1,fill)→full_domain→gray_erosion_rect(同核宽高)→threshold(1,1)。灰度矩形腐蚀在物理图边镜像，与Mean/Gaussian/Sharpen Reflect一致；孔洞为0，只有全部支持为1的像素留有效，不用普通region腐蚀误丢物理边。
计算视图同样防无效洞中的NaN污染：每通道gen_image_const(real)后paint_region(整图,0,fill)明确清零；把原输入reduce_domain到真实V后paint_gray到该临时零矩阵，append_channel组装并full_domain→实际滤波→reduce_domain到上述支撑。原V/像素不变；临时无效区置0只是计算scratch，不是补洞/有效证据，也不能产生跨洞有效输出。二值/清零/复制矩阵及tuple全部计预算，禁止修改原图或靠init_new_image全局设置。真实有效域输入有NaN/Inf则NumericInvalid；输出只核已证明支撑域，未支持临时数值不授有效。使用gray_erosion_rect不等于增加业务形态学节点。

halo每轴：Mean/Sharpen=(kernel−1)/2；Gaussian=(mask−1)/2；点节点0。同格连续路径累加，分支取路径最大；Gaussian3→Mean5=3，不是max(1,2)=2。计划 RequiredInputHalo 从所有声明输出逆推：叶输出need=0，节点inputNeed=outputNeed+LocalHalo；每条边对前驱逐轴max，Crop保留格时映射偏移，Resize切断固定halo推理并设WholeFrameBarrier。RequiredInputHalo存本节点各image输入所需最大halo，非实际原图大小。

RequiresGlobalStatistics 与 WholeFrameBarrier 分开：PerFrameRange=true/false（统计/整图），Resize=false/true。没有用 null 表示全域统计；每节点都有非负Halo。Normalize全域归约不把local halo改大，也不让tile各自归一化。

P2 默认 WholeFrame；显式Tiled模式由宿主给CoreWidth/Height1..32768、MaxTiles1..65536。以Row优先网格划互斥core，输入扩累计halo并裁到物理边；内部tile边不得Reflect，计算后去halo只留core。v1冻结为逐节点Tiled：每节点从其已完整拼接的上游矩阵按RequiredInputHalo保守扩展输入，完成该节点全部tile后拼成完整输出，再进入下一个节点；不跨节点融合/重算，后继累计halo即使大于本节点LocalHalo仍保守读入并计费。这样API单节点ExecuteNode不需要暗藏图执行器，未来跨节点流式必须新Profile/合同。tile临时与core待拼接都计账。每个节点拼接core：按固定row/col顺序调用tile_images_offset，显式crop Row1/Col1/Row2/Col2到core并Offset到全图；无重叠/无缺口，域为core有效域并集，拒借“高索引覆盖”掩接缝。输入core列表/全图输出可并存，峰值照计，不许承诺流式零额外内存。

PerFrameRange为阶段屏障：先完成上游所有节点到该Normalize的输入矩阵与真实有效域；逐通道min_max_gray(Percent=0)只归约一次→冻结本请求min/max→下游所有tile用同Mult/Add。一个通道range0整节点ConstantRange；空域OutputDomainEmpty。多屏障按拓扑逐个处理，不重复猜当前tile统计。Resize为整图屏障：先拼上游→确认FullRectangle→整图zoom→继续下游新格tile；不同格分支分别处理，算术合流须同GridTrace。不能以tile不支持而静默切模式；预估总tile/halo/屏障矩阵超限拒绝。ROI优化仅在请求已限制该域且同支撑/全域统计语义时另建经Golden验证的新执行Profile，不裁小ROI改变“全帧范围”。

上述同Mult/Add仅用于本次Normalize节点的全部tile，后续节点不再次套用归一化。NormalizationReceipt在Normalize节点必填、其它节点为null，InputMin/Max与Mult/Add数组按输出通道顺序，长度等通道数；Fixed重复声明范围，PerFrame保存本次真实归约值。CPU/backend自行归约并生成回执，Core核版本/数组长度/有限性/公式，不能用最终输出min/max冒实际输入范围。

Tiled的core坐标属于当前节点输出格；Crop先将输出core及halo映射到输入(row+Row,col+Column)，只允许原Crop输出矩形内的取样，后继滤波的物理边是该Crop图矩形边，不偷读被裁掉的原图。Select/点节点同格映射；Resize按WholeFrameBarrier执行，无分块近似。MaxTiles界定整个请求所有逐节点网格tile数之和（checked累加），不是给每节点重开上限；Resize整图调用计一个执行块。所有输入/输出域Run转换都绑定当前坐标与尺寸，不能将tile-local行段直接当全图行段拼接。

## 8. HALCON 26.05 路线、数值与资格

[本地官方operators](../../../halcon算子手册/operators/)是目标版本语义权威；全部算子经 `ImageLibDotNet.cv2`。下表是算子语义次序，不猜 C# 重载。

| 功能 | 主路线/分支 | 不采用/拒绝 |
|---|---|---|
| 通道/颜色 | access_channel 按键定位（1-based）；每行 real→scale_image→add_image，按OutputKeys append_channel | append_channel取域交集且矩阵共享，不是加权算术 |
| 线性/二元 | convert_image_type(real)；Terms按顺序scale/add；add/sub/mult/div按显式Scale/Offset | 不重排/融合float求和，不byte原类型裁切后转real |
| Divide/FlatField | real→abs_image(右/参考)→threshold取得abs>=MinAbs支持→与原有效域相交→div_image→reduce_domain | div_image除0置0不能标有效，不加epsilon，不按整型截断小阈值 |
| Normalize | Fixed显式范围；PerFrame显式region上min_max_gray Percent=0；scale_image，Mult=(outMax−outMin)/(inMax−inMin)，Add=outMin−inMin*Mult | min_max_gray忽略image domain，必须显式Regions；常值拒绝，不换直方图均衡 |
| Mean/Gaussian | mean_image；gauss_filter 3/5/7/9/11对应sigma .600/1.075/1.550/2.025/2.550；Reflect | 偶数核拒（算子会自加到下一奇数）；binomial核/sigma不同，仅新方法候选 |
| Sharpen | real→emphasize→已证明支撑域；保留round((orig−mean)*Factor)+orig | 不用scale/sub“等价”替舍入；清晰度不证明保留弱边 |
| Crop/Domain | checked当前尺寸→crop_part；get_domain/reduce_domain、gen_region_runs/get_region_runs绑定离散域；邻域支撑按§7二值gray_erosion_rect，scratch用paint_region/paint_gray显式初始化 | Crop预拒越界；域改变不减矩阵容量；不从灰度阈值猜有效域 |
| Resize | TargetWidth/Height→zoom_image_size nearest_neighbor/bilinear；full-valid输入；Host稳定int_zooming=false | zoom忽略输入domain，有洞/ROI域预拒；不混factor与target权威 |
| Tile拼接 | 按§7固定core crop/Offset调用tile_images_offset，域并集 | 覆盖/缺口拒；不把拼接当几何配准 |
| 显示均衡 | equ_histo_image仅PresentationOnly | 官方指出可能虚假边缘，不为本版算法节点 |

Float32输入/输出按有界块检查真实有效域NaN/Inf；这是完整性验证，不以托管循环重写视觉算子。块缓冲计预算。mean_image real内部单精度累加：保守按最大绝对值×核面积验证不超Float32有限上界，超界拒；其它运算逐中间有限性检查，不能只看最终minmax/spec。Integer输出不增加未冻结量化策略。

CPU为v1主backend，不宣称最快，也不禁止HALCON内部SIMD。RuntimeDescriptor含HALCON版本、BackendRevision、DeviceKey、mmx_enable、int_zooming、线程政策，Host RuntimeOwner保证整个session稳定；模块不set_system，不用全局锁偷改。前后回读只检漂移，不证明没有并发写。Resize runtime若int_zooming=true拒RuntimeDrift，不照推荐在模块里改用户设置。

OpenCL是显式后续新backend资格，不能静默fallback；Gaussian至少64×64且可有数值差异，Mean还有大宽累加溢出限制。Fallback固定Disabled。同输入/域/标注/图/预算比较CPU/OpenCL、Mean/Gaussian/Binomial、整图/tile/ROI：先域/正确性/误接受拒绝，再端到端P50/P95/P99、峰值/实际释放；未同样本实测不写“更快”。方法/格/类型/域/舍入改变新版本与Golden。

Resize中心/角映射不能凭比例猜：HALCON affine_trans_image说明其边角坐标系与标准像素中心不同；zoom只引用插值说明，v1回执固定保留操作序列，不对未验证的逆映射给精确数值。P2坡度/单像素脉冲/四角/缩小高动态样本验证实际采样及边域，宿主坐标端口绑定该Method/Runtime的映射后才供叠层/物理测量；纯图像OCR可以只消费派生像素与操作序列。bilinear缩小不保证抗混叠，细桥/细字留出样本验证损失，不自动添平滑节点。

## 9. 有界参数建议、评分与草稿

P3唯一API/类型见附录C。StartEvaluation接收不可变样本组、BaseGraph、单个可变节点ID及完整参数候选、ScoreSpec与有限期限/总预算，返回IAdviceOperation供Wait/Query/Close；最多64候选、256样本，全部候选Plan通过后按候选GraphHash Ordinal→样本Key Ordinal执行。候选重复hash拒绝，不隐式去重；不做无界笛卡尔搜索或训练。

每个候选/样本使用P1/P2同执行核心；max并行=1，执行器工厂/输入借用由宿主注入，每次Acquire独立borrow。候选结果输出交给评分端口只读borrow，评分/迟到均真实归还后才进入下一样本。评分端口必须在规定有限deadline内返回；无法停止则Advice处于Draining、保留输出Owner并占账，Wait/Close只有观察期限，不冒完成。

ScoreSpec由消费者Owner冻结 Revision/样本标注来源/指标单位/目的，Evaluate返回有限double Loss（越小越好）、Applicable和ReasonCode；模块不猜清晰度/客户阈值。Required样本任一执行失败/不可评分→候选Ineligible；Optional不可评分保留缺失原因，候选至少一个可评分且全部Required通过才Eligible。ScoreReceipt绑定SampleKey/SourceHash/GraphHash/ScoreSpecRevision；不匹配拒绝。按WorstLoss、MeanLoss、GraphHash排序；Mean用固定样本顺序double逐项求和/样本数，溢出NumericInvalid，不能忽略失败。完全相同Worst/Mean为并列，hash仅稳定显示顺序，不宣称其中更优。

无ScoreSpec时只执行/给数值诊断，不排名；无样本、无候选为Rejected；无eligible为NoRecommendation。执行资源/完整性失败导致整Advice失败，取消/超时不返“已知最佳”。每候选记录逐样本损失、样本数、有效域/有限性/缺失、方法/runtime与源绑定，不把建议当生产事实。

ApplyToDraft要求当前BaseGraphHash、SampleSetHash、ScoreSpecRevision/RuntimeRevision与建议绑定全匹配，候选Eligible且建议已完整结束，生成新GraphRevision的不可变草稿并重新Plan；不直接写发布/生产图。源/域/标注/评分/图/runtime变化即建议Stale。PerFrameRange是明确冻结的算法规则，不是回写生产系数；实得min/max只进本次回执。

## 10. 可选 WPF 编辑器 PageContract

P4可嵌入PreprocessingEditor，无Window/Shell/模块语言入口；API见附录D。选可信源及用途→核来源/域→增删节点并连端口→编辑→Plan定位问题→显式预览→原/派生联动→保存草稿→由宿主发布。预览/存草稿/发布权限分别由Host提供；发布不属于模块API。编辑缓冲保留非法中间文本、光标和原有效值，不转0或直接变生产图。

唯一验证屏1920×1080，扣任务栏/窗边/标题/状态栏实际可用区。工具区48DIP、状态28DIP；左节点220–280DIP，右参数260–320DIP，按真实中央图像区域>=可用工作区60%收窄/折叠，专注模式>=80%；底部诊断默认折叠。当前OS DPI下若比例不满足，互斥侧栏/临时Flyout，不减图像优先级；不改显示设置，不跑其它分辨率矩阵。不要用固定DIP总和假称面积满足。

| 区域 | DevExpress25.2控件/连续操作 |
|---|---|
| 工作区 | DockLayoutManager+LayoutGroup/LayoutPanel，中央DocumentGroup；可停靠/折叠，来源身份与取消常驻；恢复布局不改图 |
| 节点/连接 | TreeListControl+TreeListView，拓扑序/键/类型/Required/状态/耗时；DAG多父显示引用行，不能树化丢边；选择联动参数/图/诊断，显示排序不改执行 |
| 参数 | PropertyGridControl.SelectedObject绑定缓冲，单位/范围/高级项渐进展示；提交字段后同Core Plan；多节点批量只修改同类型同字段并生成单新草稿 |
| 诊断/比较 | GridControl点错误定位节点/字段；ChartControl按需直方图/耗时，标域/单位/缺失；原/派生联动zoom/pan/十字，缺图显示“该步骤图未生成” |
| 命令 | 常驻预览/取消/保存草稿/撤销重做/恢复布局，节点新增可下拉；熟悉图标+本地化SuperTip，关键故障常驻 |

保存操作显示原GraphRevision/保存RequestId，状态按附录D：已保存、已确认未保存、保存状态未知、未准入，与编辑/预览状态分别显示。未知或未排空时保存命令转“查询保存状态”，不把重试按钮当再次提交；可继续编辑，旧Found只更新旧revision。三语采用“保存状态未知。查询原请求后再保存。”/“儲存狀態未知。查詢原請求後再儲存。”/“Save status is unknown. Check the original request before saving.”；“查询保存状态”/“查詢儲存狀態”/“Check save status”。保留原Identity及可信主体/存储域绑定，不在UI自行输入主体或生产发布命令。

Host viewport端口承接显示映射，不把native图留ViewModel。只保留源/当前结果/选中步骤的有界预览Owner，不每节点留全尺寸图。步骤图需要核心明确导出新请求或本请求声明输出，不套最终图。Preview绑定RequestId/SourceRevision/GraphHash/RuntimeRevision/Generation；源/ROI/图改立即Stale并取消旧预览，迟到只Close其Owner或展示明确历史诊断，不能覆盖当前代。失败保留草稿与旧图、标旧修订；语言切换不重算。

统一主题、字号层级、间距/对齐/图标/状态文字，状态不只靠色。双图可同步/独立缩放，擦拭比较只在可信同格映射成立时可用，否则普通并列。参数变化显示节点/输出影响，不每键自动执行；撤销/重做仅草稿，有界最多100步/16MiB先到限移除最旧步，不隐藏关键命令。通知刷新<=10次/秒，关键状态不丢。布局保存由Host用户配置，不混图参数；动画不触发重算。

Tab按源→节点→参数→命令→图→诊断；Enter确认字段，F5预览，Esc取消当前，Ctrl+S存草稿不发布，文本编辑时不抢键；Delete显示下游影响，用户确认后新草稿，绝不静默连线。UIA AutomationId含稳定节点/字段键。
Host SetCulture支持zh-CN/zh-TW/en-US，覆盖标题/参数/状态/诊断/工具提示/权限/恢复；不丢草稿/选择/在途，不重放。资源示例：预览/預覽/Preview；保存草稿/儲存草稿/Save draft；结果已过期/結果已過期/Preview is stale；等待释放资源/等待釋放資源/Waiting for resources。Crop故障“裁剪范围超出图像。修改位置或尺寸。”自然三语，英文长标签换行、值/单位不截断。
控件状态Ready/EditingInvalid/Planning/Previewing/Stale/Rejected/Draining/Closed，不显示业务PASS/智能最佳/保证提升。Close停新操作，取消并真实排空控件自己持有的请求/Owner，不取消另一消费者。Released=false须Host保留控件恢复句柄；不能隐藏窗就称释放。视觉品质、键盘/UIA/三语、迟到/关闭及算法正确性分别验收。

字段缓冲/连线/模板、具体显示挂接、三语资源及独立Editor双Host按附录F.2–F.5实施；保存/读取原图保真与恢复codec按F.6，既有附录D的保存身份与NoCommit语义不变。

## 11. 最小 Host、第二消费者与调用顺序

P0测试Exe兼最小Host，构造器/记录按附录A；这是未来C#调用规格，未编译：

```csharp
using System.Collections.Immutable;
using Asun.Modules.ImagePreprocessing;
var graph = new ProcessingGraph("g1", "im021-graph-v1", "r1",
    [new GraphInput("source", new ImageSpec(32, 24, PixelType.UInt8,
        ["mono"], DomainMode.FullRectangle), "grid1")],
    [],
    [new ProcessingNode("crop", 1, CompletionRequirement.Required,
        [new InputBinding("image", SourceKind.GraphInput, "source")],
        new CropParameters(0, 0, 1, 1))],
    [new GraphOutput("result", "crop")]);
var factory = new PreprocessingGraphPlannerFactory();
var planner = factory.Create(new GraphPlannerDependencies(new GraphLimits(256, 1024, 1048576)));
var result = planner.Plan(graph, new GraphPlanningOptions("q1",
    CancellationToken.None, TimeSpan.FromSeconds(2)));
Console.WriteLine($"{result.Status} {result.GraphHash}");
```

合成计划为Succeeded、1×1 UInt8、grid1原点(0,0)；不是图像效果结果。失败只诊断，改图新Plan，不改PlanNode。

P1空Host组合FrameProvider/Backend Simulator/共享ResourceBudget/固定Clock/可选Observer→factory.Create→Start→Wait/Query至真终态→TryTakeResult一次→下游AcquireRead借用并Close→OutputOwner.Close确认Released→executor.Close。Wait超时只观察，不在finally丢operation；每个Released=false保留原恢复句柄，继续Query/Close。请求token、输出Owner与Host原源lease生命周期不同。P2具体工厂/帧桥与两个独立无UI Host完整装配、构造前根Owner及迟到恢复见附录E.1–E.5，不改Core规则。

P4保存最小Host流程（签名/顺序示例，未编译；editor/sink由可信Host组装，原图/身份用Host已有恢复存储保留，不新增模块IO实现）：

```csharp
var requestId = Guid.NewGuid().ToString("N");
DraftSaveResult saved = await editor.SaveDraftAsync(requestId, waiterToken);
if (saved.State == DraftSaveState.Unknown && saved.Identity is { } original)
{
    DraftSaveQueryResult query = await editor.QuerySavedDraftAsync(original, waiterToken);
    if (query.Lookup == DraftSaveLookup.Found)
    {
        // Receipt is bound to the original revision, even after further editing.
        Console.WriteLine(query.Receipt!.StoreRevision);
    }
    else if (query.Lookup == DraftSaveLookup.NotFound)
    {
        CloseReceipt closed = await sink.CloseAsync(original, TimeSpan.FromSeconds(2));
        // A new save needs NoCommit proof, IoDrained and Released, plus a new command.
        Console.WriteLine($"{query.NoCommitRevision} {query.IoDrained} {closed.Released}");
    }
    // Unknown keeps the original identity and disables another submission.
}
```

每个保存/查询/Close先有界观察；sink.Context必须与editor组装/原Identity一致，query.IoDrained=false即使closed.Released=true也先Query确认，不能由日志输出三字段自动启动新保存。控件先冻结/保留Identity，Sink.SaveAsync的Host适配器从入参取得该Identity，先可靠保留恢复记录，才允许实际草稿写入；没有隐含的“控件内部生成身份后Host提前知道”步骤。请求已准入但观察返回Unknown时只查原identity。Host恢复示例：按原Identity取得经当前主体授权的恢复Sink（同Context）→QueryAsync(original,2s,waiterToken)→Found读取原StoreRevision或NotFound核NoCommit并Close→Unknown保持待核；不调用SaveAsync重放。实际取得恢复Sink是Host组合根责任，不伪造模块恢复factory。

消费者1分割：同可信UInt8 mono/full域，Select→Normalize(Fixed0..255→0..1)→Gaussian3，Float32及有效域由分割解释，预处理不代判。消费者2 OCR/读码：同源独立borrow，Crop合法区域→Select→Resize显式尺寸，输出来源/操作序列独立；有洞Resize预拒，Host可另选无Resize已发布图新请求，不自动原图回退。两个Host分别成功、取消/失败、Close；关闭分割不得撤销OCRborrow，源字节/hash不变。双方引用同DLL无UI，不复制“简化版”代码。此为明确复用计划，真实接线/样本待实施验收。

## 12. 两轮怀疑式走查与可判定反例

A=图/数值/支撑正确性；B=集成人/资源及时间交错。矩阵是实现验收规格，不是本轮测试成绩。

| 用例 | 输入、期望与恢复 |
|---|---|
| PP-A01 确定性 | 独立a/b节点容器排列不同→拓扑a,b/hash相同；Terms换序→hash不同；多端口同前驱不重复入度 |
| PP-A02 图闭合 | 空/环/重复/断引用/未知子类/孤立/Optional传递供Required→稳定阶段诊断、GraphSnapshot=null、无前缀 |
| PP-A03 数值 | UInt8 200平方→Float32 40000；10−20→−10；byte255/0不能为真值 |
| PP-A04 分母 | 0和1e-8，MinAbs=1e-6→域剔除；阈值恰好1e-6保留；全剔除OutputDomainEmpty，不把div的0当有效 |
| PP-A05 归一化 | PerFrame常值→ConstantRange；Fixed可返回常值；多通道逐通道统计；tile统一全域min/max，NormalizationReceipt真实输入范围/Mult/Add逐通道闭合 |
| PP-A06 支撑 | 洞不补零；Reflect物理边完整V可有效，孔洞边收缩；Gaussian3→Mean5累计halo3；tile core对整图域/像素 |
| PP-A07 Crop | 宽高0/负→ParameterOutOfRange；负坐标/overflow/右下越界→CropOutOfBounds；合法1×1通过；二次Crop按当前尺寸 |
| PP-A08 格/Resize | 同尺寸不同格/不同Crop路径算术拒；有洞/ROI Resize native前拒；真实映射未验不叠层 |
| PP-A09 预算 | 32768²×多通道/branch/导出copy/全部tilecore/统计屏障矩阵累计checked预算，超限拒，不减位深/尺寸；MaxTiles按整个请求累计，Crop边界不偷读裁掉区域 |
| PP-A10 建议 | 平手明确并列，Required样本失败Ineligible，无评分不排名，标注变化Stale，Apply仅草稿 |
| PP-A11 细结构 | 平滑/锐化造成断笔/细桥/弱边损失按消费者留出标注量化，清晰度不代效果 |
| PP-B01 重复 | 同ID同hash同operation；同ID不同hash Conflict；墓碑上限拒，不能清墓碑重跑 |
| PP-B02 并发 | 同实例两个Start仅一接纳；多实例共享预算；P0并发无可变共享状态；Close/Start线性化 |
| PP-B03 等待/取消 | native不可中断时取消/期限保持Draining/计费；waiterToken只停止等待；晚输出仍被原session接管释放 |
| PP-B04 源当前性 | 断连但可信不变borrow可继续；revoked停止派发/发布，排空，不换帧/设备重连 |
| PP-B05 交接 | TryTakeResult只能一次；Close并发Take由同门决定；已交接输出不被executor回收；两borrow独立；Transfer子Owner与主账分开，同RequestId跨实例/多输出FrameId唯一 |
| PP-B06 释放失败 | Close Released=false保留Owner/账；重复Close不重复已完成阶段；超时不等析构；RetainedBytesExact=false不能判释放/精确峰值通过 |
| PP-B07 回调 | Observer抛错/阻塞/重入不持核心锁、不阻排空；通知停用有诊断且Query真实 |
| PP-B08 迟到 | r1预览→r2草稿→r1迟到→语言切换，r1不覆盖r2、Owner归还、草稿不丢 |
| PP-B09 版本/损坏 | 未知schema/篡改hash/缺方法/runtime→拒；旧闭包回退新请求，不热换在途 |
| PP-B10 二消费者 | 分割Close时OCR借用仍有效；最后Owner释放；原图字节/hash不变，无产品类型引用 |
| PP-P4S01 正常/重复 | 同Context/RequestId及完整图重复保存只一提交；Found回执全身份/StoreRevision匹配；同键改hash/原revision Conflict不覆盖 |
| PP-P4S02 查询未知 | 保存等候超时/取消、断连、外部写入不确定→Unknown且保留Identity；数据库无行/Released=true不能假NotFound，不分配新请求补写 |
| PP-P4S03 无提交/迟到 | Query持久NoCommit封锁后NotFound；尚未准入旧Save迟到见封锁不写；已有不确定写入不能假封锁，NoCommit+IoDrained+Close.Released后仅新命令可新ID |
| PP-P4S04 提交/迟到 | 写入已提交但返回/回调迟到→Found可IoDrained=false；Close不撤销；r1回执/Query迟到不将r2标已保存；状态矛盾降Unknown |
| PP-P4S05 主体/实例 | 跨主体/域/epoch伪造与权限撤回→Unknown/拒绝且不泄露Receipt；当前权限每入口/提交门核；重启经同主体恢复原epoch只Query/Close |
| PP-P4S06 并发/上限 | 一个未决Save/一个Query，重复Ctrl+S转原查询；Close/Query/Save竞争不重复提交；墓碑/图快照超限前拒、不删Unknown；保存事实与IO释放分别断言 |

P0取消/超时测阶段边界/编码块，不能因小图太快而跳过用例；使用取消前置、大图和确定性受控Clock（附录A内部可测时钟构造仅测试internal，不新增公共任意算法注入）。P0无Close/native，PP-B03/05/06用于P1，不给P0虚构Draining。P0重复身份只再次确定性Plan，不返回服务墓碑。

## 13. 测试、真值与资格

P0 BCL Exe执行PP-A01/02/07/08及所有参数/类型/端口/尺寸/Required闭包、未知方法/schema、字节限/取消/超时/并发/重复/版本；规范字节/hash用独立参考编码和附录A固定向量，不用同canonicalizer两次调用自证。
P1 Exe Simulator执行PP-B01–07/10、晚Acquire/Begin/Execute/Export、失败Close及资源reservation；用固定Clock和可控TaskCompletionSource闩锁，所有未完成路径有有限观察/背景drain句柄。模拟只证明托管协调，不冒native可中断/硬内存资格。
P2真实已知像素/灰阶坡度/脉冲/负值/零除/空域/洞/高动态/tile对整图、Float32转换/共享矩阵/copy/runtime/取消排空。基准来自独立数值算例或冻结HALCON参考；绝不拿byte裁切路径作Float32真值。
P3有限候选/评分异常/平手/Required缺失/绑定改变/迟到/Close；P4真实WPF三语1920屏、编辑中间态、联动/未生成图、快捷键/UIA/当前DPI、占图比例/迟到/资源关闭。文档原型/合成截图不能算WPF通过。
P4保存端口的软件契约验收执行PP-P4S01–06：冻结假时钟、可控提交闩锁及可信主体变化，逐入口断言Identity、Found/NotFound/Unknown和IoDrained/Released互不替代，控件仍仅原Generation接收；Host真实持久提交、NoCommit封锁耐久性、崩溃重启/权限恢复另执行故障验证。软件契约规格本轮已明确，不能列为“待存储外部门才能定义”；本轮未运行上述断言。
P5双方实际代表样本含正常、弱信号、过曝、遮挡、细结构及必需输出；效果/误接受拒绝/容差由消费者Profile，不编客户数值。Golden锁源内容/域hash、通道/格/来源、图/schema/method/runtime、输出类型/域/像素容差及来源，无真实样本/批准容差不提升客户资格。

## 14. BenchmarkProfile、预算与观测

公共统计仅引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不另造分位算法。模块Profile冻结：图/hash/version、链/宽DAG/branch、节点/绑定/规范字节数，图像宽高/位深/通道/域密度/域行段，整图或core/累计halo/统计及Resize屏障，冷/热/预热、样本/最低有效数、实例并发/共享预算、有限期限/观察deadline、测点/目标来源。
P0从Plan调用到返回并记托管分配/峰值，无native/lease则ResourcesReleased等价局部计算退出；P1/P2接纳→Acquire/import/validate/native/全域归约/tile/拼接/copy/export/verify→ResourcesReleased，另记输出Owner持有期、取消到真实排空与释放。管理/native预留、源RetainedCapacity、实际RSS/句柄、域/统计缓冲、通知槽及请求墓碑分列；SoftObserved workspace不写hard。
成功/失败/未读/取消/超时/删失/排空未知各列，不删失败；无目标结果NotEvaluated。消费者冻结负载及P95/P99/资源目标，模块不造250ms/512MiB承诺。GraphLimits/ExecutionOptions是工程硬域，超预算/未排空不算通过。
日志RequestId/RequestHash/GraphHash/schema/method/runtime、NodeId/Sequence/state/error、尺寸/域、阶段elapsed/copy/import/peak/retained；默认不记像素/客户内容。标RawSelection/Derived/PresentationOnly与参数来源，观察/日志故障不改算法事实。

## 15. 平台接入、发布与回退

Host负责来源可信绑定、当前性/注册/坐标、保存及发布权限；附录E的自有CPU桥将 [image-frame唯一指导](../image-frame/DEVELOPMENT-GUIDE.md) §4.3/4.4公共 ReadAsync/lease/scope 映射到本地端口，核实际容量/域。上游 FrameDescriptor 没有 ContentHash/IsCurrent，不能猜不存在的字段或 retain 方法；本地接口不依其它模块内部，不改共享文件或临时shim掩盖缺口。
每次执行核provider返回的SourceReceipt/规格/域/格与请求声明，核后端每节点实际结果与计划；Plan成功不是像素资格。graph hash不是批准，规范字节不是签名；IO/缓存/持久化在Host，v1 Core不写文件。Host JSON严格拒未知字段/尾部损坏，旧JSON不直接当规范摘要。
图schema、节点Method、Backend/Runtime分别版本化；字段编号/单位/域/格/舍入/默认/错误/字节改变新合同/方法，旧字节不改。0.3.1为未实施候选，不是已发布兼容基线；本轮Schema=`im021-graph-v1`、域分隔=`ASUN-IM021-GRAPH-V1`，不静默沿用旧候选1.0。未知schema拒绝。
回退需旧图+方法+backend/runtime完整闭包，Host原子发布新请求，不热换在途；新部署不宣称清掉隔离中的旧Owner，后者仍由原实例排空。模块无跨重启执行恢复，Host只保存图/来源/回执，重启后未知执行结果不得自动重放。

## 16. DEV-GOV-010 六项规格结论与真实门

2026-10-10 按主控明确接收同步的 P0 GraphPlanner、P1 ExecutionCore（托管协调/Simulator）、P3 ParameterAdvice 六项规格保持 ModuleCoreImplementationReady（仅规格准备）。2026-10-11 主控定向回读 §11 保存调用、PP-P4S01–06、本节及附录D完整D-SAVE，限定接收保存查询指导内容；P4 真实 WPF/Host 持久保存恢复及运行资格仍 PreparationIncomplete，整体/P2/P5亦未完成。不从 accepted/附录存在推断其它切片就绪。

2026-10-11 主控回读0.4.3-review附录E.1–E.6，并定向比对image-frame公开字段/Factory/rows/scope/回执，限定接收P2公开工厂/稳定runtime借用、CPU平面/域/真实held容量、Import/Export独立Owner、完整32×24软件双Host及有限原Task恢复的确定指导内容。主控另独立生成768-byte实际标量及52-byte PIXELS头，raw/local的768/820bytes两份hash一致；该证据只核软件fixture像素编码，不扩大为两图/请求/域摘要的本次主控独立复算或真实算法结果。P2真实HALCON/稳定RuntimeOwner/CPU接线/原生资源/Golden/运行/性能门保持PreparationIncomplete，不以内容接收授真实运行资格，不机械标为纯Core ModuleCoreImplementationReady。

| 六项 | P0定位与本轮闭合内容 | 其它切片/实际验证 |
|---|---|---|
| 1 边界/依赖/第二消费者 | §1/2/11，纯托管方向及分割/OCR复用计划 | P5真实接线另验 |
| 2 唯一Module API | 附录A全部类型/工厂/参数/字节/错误，§3/4计划闭包，附录B/C本地端口/Owner/观察闭包已接收 | 附录D保存查询限定接收保持；附录E P2公开装配/CPU映射确定指导内容限定接收，真实签名/映射另验，P2运行门PreparationIncomplete |
| 3 最小无UI Host | §2/11，net10 BCL Exe/明确factory/调用顺序 | 附录E.5完整软件双Host及原Task有限恢复指导限定接收；未实际build/run，不授P2/P4运行资格 |
| 4 场景/恢复/测试 | §5–7/12/13，两轮A/B反例，P0无native关闭 | 实施时执行确定性断言/真实资源与图像验证 |
| 5 BenchmarkProfile | §14模块负载/测点/资源，公共统计引用 | 目标/样本数待消费者Profile；不阻无关P0诊断测量 |
| 6 工程/路径/顺序 | §2唯一工程/Exe/有限命令，§11 | 主控绑定实际代码基线后派发，不因文档阶段无.git阻本修订 |

公开API/常规算法/halo/评分/Owner/控件任务流是模块内部规格，不再列“实现者决定”。P2 Factory/Options、CPU逐字段映射、RuntimeOwner借用及双Host根Owner按附录E闭合，确定指导内容已限定接收；常规装配不列外部门。P4保存查询指导内容已限定接收，不能以保存IO资格外部门替代端口规格。真正运行/集成门仍为P2该映射与RuntimeOwner稳定保证的实际验证、具体C#重载歧义的编译确认、真实HALCON资源/数值/坐标Golden；P4本机25.2.3真实WPF/三语/DPI、Host持久保存与恢复的真实故障验证；P5双方真实样本/标注/客户阈值/性能目标与产品批准。内部未实施测试不是外部审批，不以“未build”撤销已接收规格；P0/P1/P3保持既有接收、不重审，本次不授予P2/P4整体Ready，不等ImplementationSpecificationReady或生产通过。

### 16.1 当前完整批准范围的文档准备结论（2026-10-11）

按DEV-GOV-010 §4的“文档完整”定义，本永久原会话已将当前IM-021批准范围内可决定的软件设计收口；没有继续留给普通实现者选择的算法、参数默认、端口、线程/Owner、草稿格式或页面任务流。这里的完整范围是§1的P0–P5及F.1能力表，不包括尚未批准的流式超驻留输入、非线性色彩算法、多源Advice、任意脚本/导入器或产品放行。内部文档准备闭合不表示整模块实现、构建、运行或生产完成。

| 范围 | 实现者唯一读取位置 | 当前结论 |
|---|---|---|
| 图/通道/算术/颜色/补偿/滤波/几何/域 | §3/7/8、附录A、F.1/F.7 | 11节点的输入输出、公式、路由、累计支撑/统计、驻留与分块拒绝界明确；P0既有规格接收保持 |
| 接纳/执行/取消/排空/结果交接 | §4–7、附录B、E.1–E.4 | P1既有规格接收保持；P2确定装配内容接收保持，真实后端资格不提升 |
| 参数候选/评估/应用草稿 | §9、附录C、F.2 | P3既有规格接收保持；新增模板/单字段候选/无评分拒绝和双消费者协调oracle明确 |
| 编辑/挂接/显示/三语/保存恢复 | §10、附录D、F.2–F.6 | P4保存查询内容接收保持；挂接0.4.2、CPU显示与Host草稿codec新增文档设计闭合，真实WPF/持久恢复仍PreparationIncomplete |
| 独立宿主/第二消费者/验收发布回退 | §2/11/13–15、E.5/E.6、F.5/F.7 | 无UI双Host和可选Editor双Host的构造/原Task/有限恢复明确；P5真实集成/产品资格未完成 |

剩余责任精确分开：**本模块实现Owner**负责未来获准切片的真实C#公共调用编译、代码和正式断言、HALCON26.05数值/域/采样Golden、native实际容量/排空与性能测量，这些是尚未执行的研发工作，不是要求外部再设计本模块。**Host RuntimeOwner与Frame Owner**提供并实证附录E的稳定运行配置、可信源Receipt/CPU接线及原lease寿命；**Host持久Store/权限Owner**提供实际介质与注册/Schema、当前主体/提交门/NoCommit/重启恢复和耐久故障验证；**本模块UI实现Owner及集成Host**执行真实WPF/25.2.3、固定1920×1080可用视口/当前OS DPI、键盘/UIA与三语检查。**消费者视觉/产品Owner**提供真实图像/标注、可信ScoreSpec和方法Golden所需参考、客户误接受/拒绝与细结构损失目标、物理允差/性能Profile及产品批准；缺这些值只阻对应准确率/性能/产品结论，不能阻无关Core。

本轮只完成指导及定向文档/字节验证；未创建工程，未编译运行Core/P2/P4，未执行HALCON/WPF、持久故障/重启、Golden图像、Benchmark或现场验收。P0/P1/P3仍仅ModuleCoreImplementationReady（规格），P2/P4真实运行及P5仍PreparationIncomplete，不授整模块ImplementationSpecificationReady。模块正文由本永久原会话自审和修正，总控接收状态；不再把内容复审列为等待总控的外部门。

## 17. 研究锁定、引用与取舍

- [架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)、[DEV-VIS-021C](<../../shared-modules/guidance/03-vision/DEV-VIS-021C_图像通道与预处理独立能力开发指导.md>)是约束链；PKG-014/SM-011仅历史映射。
- HALCON26.05本地页2026-10-09实际读取：access_channel/append_channel/add_image/sub_image/mult_image/div_image/scale_image/convert_image_type、mean_image/gauss_filter/binomial_filter/emphasize、crop_part/zoom_image_factor/zoom_image_size、reduce_domain/min_max_gray/equ_histo_image/erosion_rectangle1/threshold/full_domain/copy_image/paint_gray/affine_trans_image；恢复后定向补abs_image/get_domain/get_region_runs/gen_region_runs/tile_images_offset、gen_image_const/paint_region/gray_erosion_rect（核镜像支撑及显式初始化）、mirror_image/min_image/rank_image仅候选排除。落§3/7/8；paint_gray/affine是候选及坐标边界线索，不自动加业务节点。无native运行，不审既定依赖许可。
- [NetworkX3.4.2固定commit](https://github.com/networkx/networkx/tree/2acf1590f82757c01a57b81b8c5dfb79e60aa416)：`2acf1590f82757c01a57b81b8c5dfb79e60aa416`；本轮联网读dag.py的lexicographical_topological_sort及test_dag.py的环/变化图/多个序/lex测试、LICENSE.txt、pyproject.toml。BSD-3-Clause，Python>=3.10、基础dependencies=[]、可选numpy/scipy/绘图不引入。借Kahn零入度堆及反例→§3/12/附录A；可变图/惰性迭代及同key插入id局限用冻结+唯一Ordinal NodeId解决。未复制Python/运行上游测试，恢复不重复研究。
- DevExpress25.2官方页已实际读取：[DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[TreeListControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListControl?v=25.2)、[PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、[ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)、[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)。v25.2程序集、Dock布局/MVVM、TreeList虚拟化/ItemsSource/TreeListView、SelectedObject、BarItem.SuperTip及HeaderItem/Item/Separator→§10。dxdocs/匹配WPF技能未提供，改官方网页；页面后续patch不替代用户25.2.3，不下载替换/复制示例，不称WPF通过。
- [AsunControl快照](../../references/project-snapshots/AsunControl/20261004/README.md)：既有DataCodeScannerEngine/Config、DeformableFinderBase只借临时释放、顺序及Crop坐标恢复；读码/查找/INI/重试/客户流程不迁，未变原件不重扫。
- H:\docs成像指导2026-10-06审查hash `14903113483e10088d44def9b003828bc7fa127921f5ad9ff80a14d66b9345dd`，见 [来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)。复用预览来源/修订/迟到约束→§10；累计预算/原派生显示区分仅反例线索，规范取本页。排除AOI/板级编排/Stage、客户质量阈值、签名/审批/持久化接口、来源验收和24.11算子事实。

## 18. 两轮自审及本轮证据范围

第一轮A按真实功能链：关闭整数先运算裁切、Float64错误许诺、除零置零被当有效、zoom忽略域、emphasize舍入猜测、孤立节点及端口歧义、计划缺参数、halo仅max、tile各自归一化。同步参数/API/方法/字节/示例/测试。
第二轮B从空宿主到退出：关闭任意注入hash/校验器改变语义、伪造Plan、无界墓碑/观察、Wait超时伪终态、晚资源丢Owner、共享矩阵提前释放、重复交接/Close竞争、回调锁内重入、旧建议/预览误用。分清无native P0与真实drain切片，补BCL Exe/有限命令/两消费者。
2026-10-10定向退修第一轮从保存命令推到恢复：冻结原graph/revision/hash、请求/存储域/原实例/当前主体绑定，填IEditorDraftSink.QueryAsync/CloseAsync与控件查询/事件，NotFound必须NoCommit封锁。第二轮以提交竞争/关窗/权限/重启反例核：Unknown不得默认未保存，Found与IoDrained可不同，NotFound也要等排空，迟到旧Save不可穿过NoCommit，查询不得重放写入。同步PP-P4S01–06、三语状态和Host示例；P0/P1/P3只同步主控接收，不改算法/规范图字节。

2026-10-11全范围补缺自审第一轮从字段编辑→候选→实际View挂接→显示→保存/恢复顺读，补F.1–F.7及§16.1：确定模板/缓冲事务、公开CPU viewport/语言入口、草稿唯一codec及完整软件Host。第二轮定向反查新附录的预算/迟到/误用：计入256个long及换图旧新位图并存、分开Editor/Executor预算、读Memory只在原Task退出后复用、viewport用自身epoch并由Editor撤权失效、常值直方图/非有限拒绝、Clear到epoch上限仍可恢复、固定物理验证视口与DPI。已接收A–E代码围栏/fixture不改，不重复旧全审。

本轮内存短程序按字段独立重建197bytes原图、415bytes档案前缀/483bytes完整档案，并用另一有限reader逐字段读取/重新编码一致；全档案所有截断位置及尾字节/错hash/超长声明共486个结构反例拒绝。另核binary64负零/NaN/Infinity拒绝与正零/有限值、展示采样索引/端点/行调用界和容量数学。原附录F之前全部围栏正文拼接SHA256仍`c4e176f851b3fef8865d47fcd23880d0233558a179d3628a37fcdee928e0d7cf`；旧图197bytes/hash不变。已核本地链接目标、§16.1/F.1–F.7/F.6.1定位、全部43个稳定Code的三语映射覆盖及资源表平行项、围栏/尾空白；本机官方XML核BitmapSource.Create/Bgra32/MatrixTransform及PropertyGrid字段/枚举。以上只证明指导结构、所列字节/数学命题及API资料存在，不是完整产品decoder、C#编译、UI或HALCON运行测试。

只修改本指导；旧0.3.1受审前SHA256=`d3e996539778c98bd4dcb28510036a11dc739231c917ee8194fc4d57ca9d6595`。本轮定向结构/链接/合同/独立字节向量检查不能代替产品执行。未新建报告/脚本/清单/代码/工程/Goal、未派生代理或消息其它会话，未改共享/来源/AsunImage。重启前草稿未落盘，当前正文是本次接续成果。

## 附录 A：P0 Module API Contract 0.4

P0当前Module API Contract 0.4已获主控规格接收，状态ModuleCoreImplementationReady（仅规格准备）；不批准平台schema/native/lease，不表示实现。集合System.Collections.Immutable，深冻结不暴露builder。命名空间/字段顺序如下（签名规格，不是产品实现）：

```csharp
namespace Asun.Modules.ImagePreprocessing;
public enum PixelType { UInt8=1, UInt16=2, Int16=3, Float32=4 }
public enum DomainMode { FullRectangle=1, ExplicitMask=2 }
public enum SourceKind { GraphInput=1, NodeOutput=2, DomainInput=3 }
public enum CompletionRequirement { Required=1, OptionalForPartial=2 }
public enum PlanStatus { Succeeded=1, Rejected=2, Cancelled=3, TimedOut=4, Failed=5 }
public enum ArithmeticOperation { Add=1, Subtract=2, Multiply=3, Divide=4 }
public enum FilterKind { Mean=1, Gaussian=2 }
public enum BorderPolicy { Reflect=1 }
public enum NormalizeMode { FixedRange=1, PerFrameRange=2 }
public enum Interpolation { NearestNeighbor=1, Bilinear=2 }
public sealed record ImageSpec(int Width, int Height, PixelType PixelType,
    ImmutableArray<string> Channels, DomainMode DomainMode);
public sealed record GraphInput(string Key, ImageSpec Spec, string InputGridKey);
public sealed record DomainInput(string Key, int Width, int Height, string InputGridKey);
public sealed record InputBinding(string Port, SourceKind SourceKind, string SourceId);
public sealed record GraphOutput(string Key, string NodeId);
public abstract record NodeParameters;
public sealed record SelectChannelParameters(string ChannelKey) : NodeParameters;
public sealed record LinearCombineParameters(ImmutableArray<double> Terms, double Offset) : NodeParameters;
public sealed record BinaryArithmeticParameters(ArithmeticOperation Operation, double Scale,
    double Offset, double? MinAbsDenominator) : NodeParameters;
public sealed record ColorTransformParameters(ImmutableArray<string> InputKeys,
    ImmutableArray<string> OutputKeys, string InputSpace, string OutputSpace,
    ImmutableArray<double> MatrixRowMajor, ImmutableArray<double> Offsets) : NodeParameters;
public sealed record FlatFieldParameters(double Gain, double Offset, double MinAbsDenominator) : NodeParameters;
public sealed record FilterParameters(FilterKind Kind, int? KernelWidth,
    int? KernelHeight, int? MaskSize, BorderPolicy Border) : NodeParameters;
public sealed record SharpenParameters(int MaskWidth, int MaskHeight,
    double Factor, BorderPolicy Border) : NodeParameters;
public sealed record NormalizeParameters(NormalizeMode Mode, double? InputMin,
    double? InputMax, double OutputMin, double OutputMax) : NodeParameters;
public sealed record CropParameters(int Row, int Column, int Width, int Height) : NodeParameters;
public sealed record ResizeParameters(int TargetWidth, int TargetHeight,
    Interpolation Interpolation) : NodeParameters;
public sealed record DomainLimitParameters() : NodeParameters;
public sealed record ProcessingNode(string NodeId, int MethodVersion,
    CompletionRequirement Completion, ImmutableArray<InputBinding> Inputs, NodeParameters Parameters);
public sealed record ProcessingGraph(string GraphId, string SchemaVersion, string GraphRevision,
    ImmutableArray<GraphInput> Inputs, ImmutableArray<DomainInput> Domains,
    ImmutableArray<ProcessingNode> Nodes, ImmutableArray<GraphOutput> Outputs);
public sealed record GraphLimits(int MaxNodes, int MaxBindings, int MaxCanonicalBytes);
public sealed record GraphPlannerDependencies(GraphLimits Limits);
public sealed record GraphPlanningOptions(string RequestId, CancellationToken CancellationToken, TimeSpan Timeout);
public sealed record GridStep(NodeParameters Parameters);
public sealed record GridTrace(string InputGridKey, ImmutableArray<GridStep> Steps);
public sealed record PlannedShape(ImageSpec Spec, GridTrace Grid);
public sealed record Halo(int Rows, int Columns);
public sealed record PlanNode(ProcessingNode Definition, int Order, PlannedShape Shape,
    Halo LocalHalo, Halo RequiredInputHalo, bool RequiresGlobalStatistics,
    bool WholeFrameBarrier, int LastUseOrder);
public sealed record PlanDiagnostic(string Code, string Stage, string? NodeId,
    string? FieldPath, string ResourceKey, bool Retryable);
public sealed record GraphPlanResult(PlanStatus Status, string RequestId, string GraphRevision,
    string GraphHash, ImmutableArray<byte> CanonicalBytes, ProcessingGraph? GraphSnapshot,
    ImmutableArray<PlanNode> Nodes, ImmutableArray<PlanDiagnostic> Diagnostics);
public interface IPreprocessingGraphPlanner {
    GraphPlanResult Plan(ProcessingGraph graph, GraphPlanningOptions options);
}
public interface IPreprocessingGraphPlannerFactory {
    IPreprocessingGraphPlanner Create(GraphPlannerDependencies dependencies);
}
```

唯一具体公开sealed类 `PreprocessingGraphPlannerFactory : IPreprocessingGraphPlannerFactory`；无参构造 `public PreprocessingGraphPlannerFactory()`；方法 `public IPreprocessingGraphPlanner Create(GraphPlannerDependencies dependencies)`，方法体不在指导伪造。Factory null/非法limits抛ArgumentNullException/ArgumentOutOfRangeException（组装错误）；Plan所有输入错误返回值诊断，内部异常Failed/InternalError。非法RequestId结果为""，未知修订为""，其它可识别身份照返。失败GraphSnapshot=null，其它可执行字段空；成功hash为小写64hex。

GraphLimits：MaxNodes1..4096，MaxBindings1..32768（全部节点输入数），MaxCanonicalBytes1024..16777216；Inputs1..256、Domains0..256、Outputs1..256；宽高1..32768、通道1..16、Timeout1ms..24h。集合count先checked，再遍历/深冻，budget超限不分配完整规范字节；GraphId/所有键/通道/InputSpace/OutputSpace/InputGridKey用§3ID规则。Crop负坐标保留§3专码，不被普通范围校验抢先改为ParameterOutOfRange。

端口集精确匹配，未知/重复/缺口PortTypeMismatch：Select/Filter/Sharpen/Normalize/Crop/Resize/Color=`image`；Linear=`image0..imageN-1`；Binary=`left/right`；FlatField=`image/reference`；DomainLimit=`image/mask`。image只GraphInput/NodeOutput；mask只DomainInput。Color matrix rows=OutputKeys.Length、cols=InputKeys.Length，行主序长度rows×cols，Offsets.Length=rows；重复通道键拒。所有方法1，schema只im021-graph-v1。

P0域模式保守传播：Select/Crop/Resize/FixedNormalize保持；Linear/Color/Binary非Divide全输入FullRectangle时FullRectangle，否则ExplicitMask；Divide/FlatField/DomainLimit/邻域/Sharpen为ExplicitMask，P2实际可证明完整但P0不推翻保守属性；PerFrame保持输入域。因此邻域后Resize在本版本静态拒，不运行期偷偷放宽；合法需要单独明示/验证新图或未来更精确域合同，不重排图。

GridTrace只有Crop/Resize步骤，参数必须对应已知类型；比较按参数值序列/InputGridKey，不含节点身份。因此不同节点ID但相同操作路径可以同格，不同路径即使数学上可化简也保守拒。LastUseOrder为最大直接后继Order，声明输出保留到Nodes.Length；Order从0开始，叶非输出不可能（孤立拒）。
RequiredInputHalo按§7反向逐边；Crop偏移只影响取样范围，Halo仍累计；DomainLimit只接受image的GridTrace.Steps为空（恒等Crop/Resize无步骤），且DomainInput格/尺寸一致；Resize输入全帧并WholeFrameBarrier，停止跨格固定halo传播，RequiredInputHalo=(0,0)并不表示无需全帧。全局统计标志仅PerFrame；不存在null/无限Halo。

规范字节：域字符串ASUN-IM021-GRAPH-V1→GraphId→SchemaVersion→GraphRevision→Inputs→Domains→Nodes→Outputs；Inputs/Domains/Outputs各按Key Ordinal，Nodes按拓扑，字段按记录声明顺序。ProcessingNode写NodeId/MethodVersion/Completion/Inputs/Parameters；Bindings按Port Ordinal；参数先discriminator再按参数记录顺序。ImageSpec字段按定义，数组按原顺序。discriminator固定Select1/Linear2/Binary3/Color4/FlatField5/Filter6/Sharpen7/Normalize8/Crop9/Resize10/DomainLimit11。
字符串UTF8无BOM：uint32大端字节数+字节；集合uint32大端数量+元素；enum/int=int32大端；double IEEE754 binary64大端bits，−0归+0、NaN/Inf拒；nullable先byte0/1再值；空参数仅discriminator。无RequestId/时刻/语言/派生Plan/实际域内容；GraphHash=SHA256(规范字节)小写64hex。不得拼无长度字段。Host外部格式版本/未知字段/尾字节严格拒；P0无公开decoder/IO。

P0稳定Code：InputNull/InvalidIdentifier/DuplicateNodeId/UnknownField/GraphRevisionMismatch/GraphCycle/ReferenceMissing/PortTypeMismatch/OptionalDependency/ParameterOutOfRange/CropOutOfBounds/UnsupportedParameter/InputShapeMismatch/BudgetExceeded/Cancelled/TimedOut/InternalError。Stage=Envelope/Parameters/References/Topology/Dependencies/Shape/Canonical/Planning。ChannelKey缺失InputShapeMismatch；只有InternalError可Retryable=true，不能自动改图重试。

固定编码向量采用§11完整图；本轮独立短程序按上述字段逐一编码，仅验证数学字节定义，不执行产品Core；实现必须逐字节比对，不需读取研究脚本。

字节数=`197`；SHA256=`a7944d71f7ffe5979623997c0b7eb36ea4a3f3f51529e0bba2dbfe52f587f9f9`。
完整hex（不换字段/不含换行字节）：

```text
000000134153554e2d494d3032312d47524150482d56310000000267310000000e696d3032312d67726170682d76310000000272310000000100000006736f7572636500000020000000180000000100000001000000046d6f6e6f0000000100000005677269643100000000000000010000000463726f7000000001000000010000000100000005696d6167650000000100000006736f7572636500000009000000000000000000000001000000010000000100000006726573756c740000000463726f70
```


## 附录 B：P1 ExecutionCore Module API Contract 0.4

P1本地托管协调/Simulator合同0.4已获主控规格接收，状态ModuleCoreImplementationReady（仅规格准备），不承诺native可中断。以下所有值记录不可变且深冻结；接口不暴露SDK句柄，扩展namespace仍为Asun.Modules.ImagePreprocessing。操作/Owner返回引用是明确生命周期能力，不进入canonical值。标准using为System、System.Collections.Immutable、System.Threading、System.Threading.Tasks（附录A同样适用）。

```csharp
public enum ExecutionState {
    Validating=1, Running=2, Completing=3, Cancelling=4, Draining=5,
    Completed=6, Rejected=7, Cancelled=8, TimedOut=9, Failed=10
}
public enum ExecutionOutcome { Succeeded=1, PartiallyCompleted=2, Rejected=3, Cancelled=4, TimedOut=5, Failed=6 }
public enum PartialOutputPolicy { Atomic=1, AllowCompletedNodes=2 }
public enum ExecutionMode { WholeFrame=1, Tiled=2 }
public enum WaitOutcome { Terminal=1, WaitLimitReached=2, WaiterCancelled=3 }
public enum EvidenceKind { RawSelection=1, Derived=2, PresentationOnly=3 }
public enum StartStatus { Accepted=1, Rejected=2 }
public enum PortStatus { Succeeded=1, Rejected=2, Failed=3 }
public sealed record DomainRun(int Row, int StartColumn, int EndColumn);
public sealed record DomainSnapshot(int Width, int Height, string InputGridKey,
    ImmutableArray<DomainRun> Runs, string DomainHash);
public sealed record FrameReceipt(string FrameId, string SourceRevision, string ContentHash,
    string RegistrationRevision, string CoordinateRevision, ImageSpec Spec,
    string InputGridKey, GridTrace Grid, DomainSnapshot Domain);
public sealed record FrameBinding(string GraphInputKey, string ProviderKey, FrameReceipt Expected);
public sealed record DomainBinding(string GraphDomainKey, DomainSnapshot Value);
public sealed record RuntimeDescriptor(string HalconVersion, string BackendRevision,
    string DeviceKey, bool MmxEnabled, bool IntZooming, string ThreadPolicyRevision);
public sealed record TileOptions(int CoreWidth, int CoreHeight, int MaxTiles);
public sealed record ExecutionOptions(TimeSpan Timeout, TimeSpan DrainTimeout,
    long MaxManagedBytes, long MaxNativeReservedBytes, long MaxRetainedBytes,
    PartialOutputPolicy PartialOutputPolicy, ExecutionMode Mode,
    TileOptions? Tiles, RuntimeDescriptor Runtime, CancellationToken CancellationToken);
public sealed record ExecutionRequest(string RequestId, ProcessingGraph Graph,
    string ExpectedGraphHash, string RequestHash, ImmutableArray<FrameBinding> Frames,
    ImmutableArray<DomainBinding> Domains, ExecutionOptions Options);
public sealed record ExecutionDiagnostic(string Code, string Stage, string? NodeId,
    string? FieldPath, string ResourceKey, bool Retryable);
public sealed record CloseReceipt(bool Released, long RetainedBytes,
    bool RetainedBytesExact,
    ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record OperationSnapshot(string RequestId, string RequestHash,
    ExecutionState State, bool IsTerminal, ExecutionOutcome? Outcome,
    long RetainedBytes, bool RetainedBytesExact, bool ResultTaken,
    ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record OperationWait(WaitOutcome WaitOutcome, OperationSnapshot Snapshot);
public sealed record StartResult(StartStatus Status, IPreprocessingOperation? Operation,
    ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record NumericReceipt(bool Finite, ImmutableArray<double> ChannelMin,
    ImmutableArray<double> ChannelMax, long ValidPixels, long InvalidPixels,
    string ClippingObservation);
public sealed record NormalizationReceipt(NormalizeMode Mode,
    ImmutableArray<double> InputMin, ImmutableArray<double> InputMax,
    double OutputMin, double OutputMax,
    ImmutableArray<double> Mult, ImmutableArray<double> Add);
public sealed record NodeReceipt(string NodeId, string ParameterHash, PlannedShape Shape,
    string DomainHash, string MethodKey, RuntimeDescriptor Runtime, NumericReceipt Numeric,
    NormalizationReceipt? Normalization,
    TimeSpan Elapsed, long PeakReservedBytes, ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record SourceFrameReceipt(string GraphInputKey, FrameReceipt Frame);
public sealed record SourceReceipt(ImmutableArray<SourceFrameReceipt> Frames,
    ImmutableArray<DomainBinding> Domains, string GraphHash,
    string SchemaVersion, RuntimeDescriptor Runtime);
public sealed record DerivedImageRef(string OutputKey, PlannedShape Shape,
    DomainSnapshot Domain, SourceReceipt Source, EvidenceKind EvidenceKind,
    IPreprocessOutputOwner Owner);
public sealed record PreprocessResult(string RequestId, string RequestHash, string GraphHash,
    string GraphRevision, RuntimeDescriptor Runtime, ExecutionOutcome Status,
    bool CompleteGraph, ImmutableArray<DerivedImageRef> Outputs,
    ImmutableArray<NodeReceipt> NodeReceipts, ImmutableArray<ExecutionDiagnostic> Diagnostics);
public interface IPreprocessingExecutor {
    StartResult Start(ExecutionRequest request);
    OperationSnapshot? Query(string requestId);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public interface IPreprocessingOperation {
    string RequestId { get; }
    OperationSnapshot Query();
    void RequestCancellation();
    ValueTask<OperationWait> WaitAsync(TimeSpan waitLimit, CancellationToken waiterToken);
    bool TryTakeResult(out PreprocessResult? result);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public interface IPreprocessOutputOwner {
    ValueTask<PortResult<IFrameBorrow>> AcquireReadAsync(CancellationToken token);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public sealed record PortResult<T>(PortStatus Status, T? Value,
    ImmutableArray<ExecutionDiagnostic> Diagnostics) where T : class;
public interface IFrameInputProvider {
    ValueTask<PortResult<IFrameBorrow>> AcquireAsync(string providerKey,
        FrameReceipt expected, CancellationToken token);
}
public interface IFrameBorrow {
    FrameReceipt Receipt { get; }
    long RetainedCapacityBytes { get; }
    bool IsCurrent { get; }
    ValueTask<int> CopyRowsAsync(int plane, int firstRow, int rowCount,
        Memory<byte> destination, CancellationToken token);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public sealed record BackendImageInfo(PlannedShape Shape, DomainSnapshot Domain,
    NumericReceipt Numeric, RuntimeDescriptor Runtime);
public interface IBackendImage {
    BackendImageInfo Info { get; }
}
public sealed record BackendNodeRequest(PlanNode Plan,
    ImmutableArray<IBackendImage> Images, DomainSnapshot? Mask,
    ExecutionMode Mode, TileOptions? Tiles);
public sealed record BackendNodeResult(IBackendImage Image, NodeReceipt Receipt);
public sealed record BackendSessionContext(string OwnerKey, string RequestId, string RequestHash,
    string GraphHash, string GraphRevision, string SchemaVersion, RuntimeDescriptor Runtime);
public interface IPreprocessingBackend {
    ValueTask<PortResult<IBackendSession>> BeginAsync(BackendSessionContext context,
        IResourceReservation reservation, CancellationToken token);
}
public interface IBackendSession {
    ValueTask<PortResult<IBackendImage>> ImportAsync(IFrameBorrow source,
        PlannedShape expected, CancellationToken token);
    ValueTask<PortResult<BackendNodeResult>> ExecuteNodeAsync(BackendNodeRequest request,
        CancellationToken token);
    ValueTask<CloseReceipt> ReleaseImageAsync(IBackendImage image, TimeSpan waitLimit);
    ValueTask<PortResult<DerivedImageRef>> ExportAsync(string outputKey,
        IBackendImage image, SourceReceipt source, EvidenceKind kind, CancellationToken token);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public interface IResourceBudget {
    PortResult<IResourceReservation> TryReserve(string ownerKey,
        long managedLimit, long nativeLimit, long retainedLimit);
}
public interface IResourceReservation {
    string OwnerKey { get; }
    bool TryCharge(string allocationKey, long managedBytes, long nativeBytes, long retainedBytes);
    void ConfirmReleased(string allocationKey);
    PortResult<IResourceReservation> Transfer(ImmutableArray<string> allocationKeys, string newOwnerKey);
    long RetainedBytes { get; }
    bool RetainedBytesExact { get; }
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public interface IMonotonicClock {
    long GetTimestamp();
    TimeSpan Elapsed(long start, long end);
    ValueTask DelayAsync(TimeSpan delay, CancellationToken token);
}
public sealed record ProcessingEvent(string RequestId, long Sequence, string Kind,
    string? NodeId, ExecutionState State, string? Code);
public interface IProcessingObserver { void OnEvent(ProcessingEvent value); }
public sealed record ExecutionDependencies(GraphPlannerDependencies Planning,
    IFrameInputProvider Frames, IPreprocessingBackend Backend, IResourceBudget Budget,
    IMonotonicClock Clock, IProcessingObserver? Observer, int MaxRequestsPerInstance);
public interface IPreprocessingExecutorFactory {
    IPreprocessingExecutor Create(ExecutionDependencies dependencies);
}
```

唯一具体sealed `PreprocessingExecutorFactory`，无参构造，实现Create。Create的null/范围非法为组装异常，不执行；Start非法返回Rejected/Operation=null。Query未知返回null（Host显示NotFound）；operation.Query本身份始终快照，Close后保留最终墓碑。已接纳即使最终失败也有operation；Rejected无借用/输出。PortResult成功必须Value非null。失败/拒绝通常Value=null；Acquire/Begin/Import/Execute/Export如曾创建未释放资源，必须以非null Value返回原资源/会话供Core接管排空，即使Status=Failed，也不能遗失。Score等纯值失败Value必须null。Core先接管任何非null资源再处理Status；仅在本端口实际未得资源或已确认释放时才可抛异常/取消而不返资源。后台native未退出Port task不先完成，不用异常逃过Owner。

请求数据集闭合：Frames按GraphInputKey一一对应图Inputs，无重复/多余/缺失；Domains对应图Domains。provider实际Receipt必须与Expected各身份/hash/规格/格/域一致，Import逐行复制时计算ContentHash并核对。ContentHash本地格式为SHA256：ASCII域串长度前缀ASUN-IM021-PIXELS-V1、ImageSpec（域模式也含）、按plane从0起/row从0起紧密LittleEndian像素字节；不含stride padding。Provider若使用其它内容hash约定，适配器须提供该本地hash及原来源hash追溯，不能直接冒同一摘要。CopyRows plane零基、rowCount1..64、destination长度必须等于rowCount×Width×bytesPerPixel；返回written必须恰好长度。每通道平面按Spec.Channels顺序，禁止暴露指针；Memory在该task真实完成前不得复用/归还，取消不证明完成。

DomainSnapshot行段Row从0起，EndColumn包含；按(row,start)升序，无重叠且同一行相邻段合并，坐标在尺寸内。空Runs表示空域，绝不表示full；FullRectangle必须每行一段0..Width−1。MaxDomainRuns=1048576且计托管额度。DomainHash=SHA256：普通字符串ASUN-IM021-DOMAIN-V1→Width→Height→InputGridKey→Runs(count、每段三个int)，使用附录A大端/UTF8规则。域坐标限制Mask在图声明格上；Crop后的DomainLimit需DomainInput给对应GridTrace的格绑定，v1图DomainInput只原InputGridKey无Steps，故禁止在非恒等Crop/Resize后直接DomainLimit，需在几何前限制域或未来版本显式域变换，不能尺寸相同就猜兼容。Shape.Spec.DomainMode是静态保守属性，实际全矩形可更精确，但输出仍带计划Shape；BackendInfo.Domain是真事实。

Receipt源注册/坐标修订各为1..128可打印ASCII，未知用显式`unknown`；多输入同格时RegistrationRevision必须非unknown且一致，否则RegistrationMissing，单输入/同FrameId选择不同通道可用unknown。Graph/端口/节点标识沿§3为1..64；FrameId/SourceRevision是回执身份，单独允许1..128可打印ASCII，hash为64小写hex；FrameReceipt不含物理mm单位，坐标Owner的CoordinateRevision是引用，不创造物理值。FrameReceipt.Grid对图Inputs必须为空Steps且InputGridKey一致；派生输出borrow携带完整PlannedShape.Grid，不能因换成borrow丢几何来源。输出borrow的FrameId/SourceRevision按本附录末尾派生身份规则创建，ContentHash按导出像素独立计算，SourceReceipt另保原帧闭包，不能拿原ContentHash冒派生hash。输入IsCurrent在import前、每节点前、发布前检查；borrow在途仍不可回收，无效即停止派发后排空。

RequestHash规范投影：域ASUN-IM021-REQUEST-V1→ExpectedGraphHash→Frames（GraphInputKey排序，写GraphInputKey/ProviderKey/Expected全部记录字段，Domain按值编码含DomainHash）→Domains（GraphDomainKey排序，全值编码）→Options（按记录顺序但不含token）。Runtime按RuntimeDescriptor字段顺序写字符串/bool；TimeSpan ticks和long为int64大端，bool为byte0/1，nullable存在位；其余附录A。RequestId/接纳时刻/等待限/MaxRequestsPerInstance/内部OwnerKey不入hash。Start重算后匹配请求RequestHash，空/不符Conflict。参数哈希=域ASUN-IM021-PARAMETER-V1→MethodVersion→参数discriminator和值的SHA256；NodeId不入参数hash。

Start无IO预检必须有限：同P0 Limits、options Timeout1ms..24h、DrainTimeout1ms..10min；三个字节上限各1..64GiB且受共享部署预算更低上限；Mode WholeFrame时Tiles=null，Tiled时Tiles必填；runtime HALCON固定26.05/本版DeviceKey=cpu，标识符按ID规则。Start只能处理已经托管不可变请求/调用Planner与Budget.TryReserve，不调用native/Frame Acquire；Budget.TryReserve必须同步不阻塞IO。节点执行固定按Plan拓扑串行，输入image按Port规则顺序与Plan绑定，BackendNodeRequest.Images包含image端口，不包含mask。Last-use后ReleaseImage，仅实际关闭成功ConfirmReleased。

reservation的allocationKey实例/请求内唯一，TryCharge按模块硬限与共享总限原子累计；同物理底层只计一次allocation retained，同时每个逻辑borrow分别记录held责任，不因去重丢borrow。无法共享底层身份时保守重复计费不低估。ConfirmReleased只在真实allocator/Owner确认后，重复同key无副作用但不得提前调用；reservation.Close尚有自身charge返回Released=false。Transfer原子将列明allocation归属移至新的子reservation（同共享总额度与原请求限），返回子Owner恢复句柄；缺key/重复转移失败不改账，不复制或减总charge。Export导出独立copy后将其像素/域/显示借用charge转给OutputOwner持有的子reservation，原reservation.Close只等待原Owner剩余charge，不因已交接输出永久阻断operation終态；子Close须本Owner真实释放后ConfirmReleased。Transfer失败则不发布输出、仍由原session/Core释放。该本地预算Port对接image-frame已批准allocation/held规则，不重定义全平台分配事实。

Session拥有Import/Execute返回的全部IBackendImage至ReleaseImage/Close完成，调用者只是能力引用；失败/异常也由session保管临时资源。Export成功深复制并生成独立OutputOwner，转给Core待交接；Export未完成session不可Close成功，晚成功也转原operation并由其Close，不能被迟到分支遗忘。Acquire/Begin晚成功的borrow/session同样由已接纳operation接管，即使请求已取消。

所有Port任务只有本次native/read真实退出后才能完成/抛取消；取消token是请求信号不是释放证明。Core用task完成状态与有限Wait观察分开，不能把WaitAsync超时包装成Port任务“已完成”。Close released=false后对象及在途task留原Owner；released=true保证本Owner的native已退出、所拥有资源归还，输出已交接则不属session/executor。IMonotonicClock的timestamp单位不外猜，Elapsed保证同clock非负单调，DelayAsync按同clock有限推进、无IO；测试假Clock由闩锁显式Advance唤醒。Core等待/测试不用UTC或任意真实sleep替预算。输出Owner必须保留共享reservation中的自身charge直至借用排空/实际释放；executor资源释放事件不能偷清已转出charge。executor.Close.Released仅本Owner资源是否释放，与外部已交接输出独立。

事件Kind闭包为Received/ValidationCompleted/Rejected/Accepted/PlanBound/NodeStarted/NodeCompleted/NodeFailed/OutcomeRecorded/DrainPending/Drained/ResourcesReleased/Terminal；Stage=P0阶段加Acquire/Import/Execute/Statistics/Tile/Export/Verify/Drain/Release/Observe。P1错误为P0 Code加RegistrationMissing/DomainInvalid/OutputDomainEmpty/NumericInvalid/ConstantRange/BackendError/RuntimeDrift/ConcurrencyViolation/Conflict/NativeDrainUnknown/ReleaseFailed/Closed/NotFound/ObserverUnavailable/PersistenceCorrupt/RevisionUnavailable/SourceInvalidated。P1无自动重试；ReleaseFailed/NativeDrainUnknown只允许观察/关闭，Retryable=true不授权重执行。

Operation.Close与TryTakeResult用同原子门：先Take成功输出属Host，先Close则后Take=false且输出Core释放；关闭后已Taken墓碑ResultTaken=true。失败结果也最多Take一次（无Owner）；Query/Wait永远不转移。Close成功终态与Result消费是两件事；结果未取而关闭则值快照保留、Owner已释放，不能再次提供已释放结果。

## 附录 C：P3 ParameterAdvice Module API Contract 0.4

P3 Module API Contract 0.4已获主控规格接收，状态ModuleCoreImplementationReady（仅规格准备）。所有值深冻结。无图像结果Owner进入AdviceResult：只在每样本真实评分/排空/释放后聚合；未排空由AdviceOperation持有。P3无生产Apply，只有生成草稿。

```csharp
public enum AdviceStatus { Succeeded=1, NoRecommendation=2, Rejected=3, Cancelled=4, TimedOut=5, Failed=6 }
public enum AdviceState { Running=1, Draining=2, Completed=3, Rejected=4, Cancelled=5, TimedOut=6, Failed=7 }
public enum CandidateEligibility { Eligible=1, Ineligible=2, Unranked=3 }
public sealed record AdviceSample(string Key, FrameBinding Frame, string LabelRevision,
    string LabelHash, CompletionRequirement Requirement);
public sealed record ScoreSpec(string Revision, string MetricKey, string Unit, string PurposeKey);
public sealed record AdviceCandidate(string Key, NodeParameters Parameters);
public sealed record AdviceRequest(string RequestId, ProcessingGraph BaseGraph,
    string BaseGraphHash, string MutableNodeId, string OutputKey,
    ImmutableArray<AdviceSample> Samples, string SampleSetHash,
    ImmutableArray<AdviceCandidate> Candidates, ScoreSpec? Score,
    ExecutionOptions ExecutionTemplate, TimeSpan Timeout, TimeSpan DrainTimeout,
    CancellationToken CancellationToken);
public sealed record ScoreInput(string SampleKey, string SourceHash, string GraphHash,
    string LabelRevision, string LabelHash, ScoreSpec Spec, IFrameBorrow Output);
public sealed record ScoreReceipt(string SampleKey, string SourceHash, string GraphHash,
    string ScoreSpecRevision, bool Applicable, double? Loss, string ReasonCode);
public interface IAdviceScorer {
    ValueTask<PortResult<ScoreReceipt>> ScoreAsync(ScoreInput request, CancellationToken token);
}
public sealed record AdviceSampleReceipt(string SampleKey, ExecutionOutcome ExecutionStatus,
    bool Applicable, double? Loss, string ReasonCode, NumericReceipt? Numeric);
public sealed record CandidateReceipt(string Key, string GraphHash, NodeParameters Parameters,
    CandidateEligibility Eligibility, double? WorstLoss, double? MeanLoss, int? Rank,
    ImmutableArray<AdviceSampleReceipt> Samples);
public sealed record AdviceBinding(string BaseGraphHash, string SampleSetHash,
    string? ScoreSpecRevision, RuntimeDescriptor Runtime);
public sealed record AdviceResult(string RequestId, AdviceStatus Status, AdviceBinding Binding,
    ImmutableArray<CandidateReceipt> Candidates, ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record AdviceSnapshot(string RequestId, AdviceState State, bool IsTerminal,
    long RetainedBytes, bool RetainedBytesExact, ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record AdviceWait(WaitOutcome WaitOutcome, AdviceSnapshot Snapshot);
public sealed record AdviceStart(IAdviceOperation? Operation,
    ImmutableArray<ExecutionDiagnostic> Diagnostics);
public interface IAdviceOperation {
    AdviceSnapshot Query();
    void RequestCancellation();
    ValueTask<AdviceWait> WaitAsync(TimeSpan waitLimit, CancellationToken waiterToken);
    bool TryTakeResult(out AdviceResult? result);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public sealed record DraftApplication(string BaseGraphHash, AdviceBinding CurrentBinding,
    AdviceResult Advice, string CandidateKey, string NewGraphRevision);
public sealed record DraftApplicationResult(ProcessingGraph? Draft, GraphPlanResult Plan);
public interface IParameterAdvisor {
    AdviceStart StartEvaluation(AdviceRequest request);
    DraftApplicationResult ApplyToDraft(DraftApplication request);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public sealed record AdviceDependencies(ExecutionDependencies Execution,
    IPreprocessingExecutorFactory Executors, IAdviceScorer? Scorer);
public interface IParameterAdvisorFactory {
    IParameterAdvisor Create(AdviceDependencies dependencies);
}
```

具体sealed ParameterAdvisorFactory公开无参构造/上述Create。单advisor最多一非终态Advice；墓碑上限复用Execution.MaxRequestsPerInstance，每Advice RequestId/内部请求hash幂等、冲突拒；内部hash不是新公共参数，advisor从完整请求规范投影计算。AdviceStart.Operation=null表示拒绝；操作等待/取消/Close/结果一次take与P1相同，值结果无资源仍需保证真实drain后才IsTerminal。Close Released=false保留执行器/评分task/borrow/输出恢复句柄。Scorer输入borrow只在任务实际完成后归还，不能靠deadline先关闭在用图。IAdviceScorer本身生命周期宿主拥有；收到取消不授予module暴力终止。AdviceSamples的CompletionRequirement不得未知；ExecutionTemplate.CancellationToken与Advice请求token合并，二者任一取消均停止本Advice，不以新子token抹掉宿主取消。

P3 v1为了可判定不猜多帧样本集合：BaseGraph恰好一个GraphInput、无Domains；AdviceSample.Frame.GraphInputKey须匹配。多源颜色/平场的参数建议可正常手动配置/正式执行，但不在首版单源Advice搜索资格；需未来版本显式Sample Frames/Domain映射。OutputKey是声明且Required输出，MutableNodeId存在且Required。样本Key/候选Key/Revision遵ID规则，LabelRevision可unknown、LabelHash可空，但Score非null时Required样本必须有可信标注hash及非unknownRevision，否则Ineligible。无ScoreSpec有Scorer也不调用；Score有值而Scorer缺失则Rejected，不能静默无评分排名。
候选Graph沿BaseGraph替换唯一节点参数，保留其它字段/修订；Candidate.Key不进入GraphHash，不同Key相同hash拒UnsupportedParameter。ScoreInput.LabelHash只是引用，Scorer用自身已绑定可信不可变标注提供评分，不让module加载数据库/文件。

SampleSetHash规则：域ASUN-IM021-SAMPLES-V1→按Key Ordinal Samples，逐字段写Key、FrameBinding完整值、LabelRevision、LabelHash、Requirement，用附录A/B编码。Advice RequestHash内部计算：域ASUN-IM021-ADVICE-V1→BaseGraphHash→MutableNodeId→OutputKey→SampleSetHash→Candidates按候选Key Ordinal完整参数→Score(nullable)→ExecutionTemplate（除token）→Timeout ticks→DrainTimeout ticks；RequestId/token不入。Bind一致性用全部字段，不能只GraphHash。
Advice总Timeout1ms..24h、DrainTimeout1ms..10min；单样本remaining=min(Advice剩余、ExecutionTemplate.Timeout)，所有候选/样本累计持有量与分配遵同一总预算，不重开64份独立额度；已释放可再使用，总预算表示同时活峰值不是累计历史分配。评分耗时共用remaining。每候选持有执行器至Close Released后复用预算；内部子请求ID采用a0001.s0001形式（Advice实例私有executor），不拼用户RequestId超64字符。

所有Required评分通过且至少一个样本Loss时按§9排序；Rank为dense rank（同Worst/Mean同Rank，下组加1），无评分Rank/Worst/Mean=null、Eligibility=Unranked。无Score的完整候选Result.Status=Succeeded（只完成诊断），不宣称推荐。已取消/TimedOut/Failed的Result.Candidates为空，仅Diagnostics，成功/NoRecommendation保留全部候选的拒绝原因。
ApplyToDraft完全无IO/执行：重新Plan BaseGraph（从Advice内部保存的冻结BaseGraph取，不从外部AdviceResult相信参数）并比CurrentBinding；只接受本advisor原operation完整Succeeded且评分Eligible候选，生成新修订重新Plan，失败Draft=null；外部new/with伪造AdviceResult拒Conflict。advisor最多保存已完成建议墓碑上限；Close后可Query快照，Apply拒Closed。表面DraftApplication携Advice用于匹配身份/内容，不允许它替换内部冻结建议。

## 附录 D：P4 WPF Editor Contract 0.4.1（保存查询指导内容已接收）

2026-10-11 主控限定接收本附录保存查询指导内容及其正文/示例/反例；P4真实WPF/Host持久保存恢复及运行资格仍PreparationIncomplete，不表示整套P4或产品验收通过。Core值不依WPF；控件namespace `Asun.Modules.ImagePreprocessing.Wpf`，`public sealed class PreprocessingEditor : System.Windows.Controls.Control`；具体Visual实现消费§10已查官方控件，禁在Core引DevExpress。控件没有自有Window/生产发布命令。

```csharp
public enum EditorState { Ready=1, EditingInvalid=2, Planning=3, Previewing=4, Stale=5, Rejected=6, Draining=7, Closed=8 }
public sealed record EditorSource(ImmutableArray<FrameBinding> Frames,
    ImmutableArray<DomainBinding> Domains, string SourceRevision);
public sealed record EditorPermissions(bool CanEdit, bool CanPreview, bool CanSaveDraft, bool CanApplyAdvice);
public sealed record EditorOptions(GraphLimits GraphLimits, ExecutionOptions PreviewOptions,
    long MaxPreviewRetainedBytes, TimeSpan CommandWaitLimit);
public sealed record DraftChangedEvent(long Generation, ProcessingGraph? ValidGraph,
    ImmutableArray<PlanDiagnostic> Diagnostics);
public sealed record PreviewStateEvent(long Generation, string RequestId,
    string SourceRevision, string GraphHash, EditorState State,
    ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record AdviceStateEvent(long Generation, AdviceSnapshot Snapshot, AdviceResult? Result);
public sealed record ViewportSelection(string SourceKey, string? OutputKey,
    string CoordinateRevision, string DomainHash);
public interface IPreprocessingViewport {
    ValueTask<CloseReceipt> SetContentAsync(IFrameBorrow content, ViewportSelection selection,
        TimeSpan waitLimit, CancellationToken token);
    ValueTask<CloseReceipt> ClearAsync(TimeSpan waitLimit);
}
public enum DraftSaveState { Saved=1, NotSaved=2, Unknown=3, Rejected=4 }
public enum DraftSaveLookup { Found=1, NotFound=2, Unknown=3 }
public sealed record DraftStoreContext(string StoreScopeKey, string OriginHostEpoch,
    string PrincipalKey, int MaxSaveRequests);
public sealed record DraftSaveIdentity(DraftStoreContext Context, string RequestId,
    string GraphId, string GraphRevision, string GraphHash);
public sealed record DraftSaveRequest(DraftSaveIdentity Identity, ProcessingGraph Draft);
public sealed record DraftSaveReceipt(DraftSaveIdentity Identity, string StoreRevision);
public sealed record DraftSaveResult(DraftSaveIdentity? Identity, DraftSaveState State,
    DraftSaveReceipt? Receipt, string? NoCommitRevision, bool IoDrained,
    ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record DraftSaveQueryResult(DraftSaveIdentity Identity, DraftSaveLookup Lookup,
    DraftSaveReceipt? Receipt, string? NoCommitRevision, bool IoDrained,
    ImmutableArray<ExecutionDiagnostic> Diagnostics);
public sealed record DraftSaveStateEvent(long Generation, DraftSaveResult Result);
public interface IEditorDraftSink {
    DraftStoreContext Context { get; }
    ValueTask<DraftSaveResult> SaveAsync(DraftSaveRequest request,
        TimeSpan waitLimit, CancellationToken requestToken);
    ValueTask<DraftSaveQueryResult> QueryAsync(DraftSaveIdentity identity,
        TimeSpan waitLimit, CancellationToken waiterToken);
    ValueTask<CloseReceipt> CloseAsync(DraftSaveIdentity identity, TimeSpan waitLimit);
}
public sealed record EditorDependencies(GraphPlannerDependencies Planning,
    IPreprocessingExecutorFactory Executors, ExecutionDependencies Execution,
    IFrameInputProvider Frames, IParameterAdvisor? Advisor,
    IPreprocessingViewport Original, IPreprocessingViewport Derived, IEditorDraftSink DraftSink);
```

PreprocessingEditor的唯一公开成员签名如下；返回Task操作是有界UI观察，未drain不静默隐藏Owner：

| 成员 | 精确签名/语义 |
|---|---|
| 构造 | `public PreprocessingEditor(EditorDependencies dependencies, EditorOptions options, EditorPermissions permissions)`；Host UI线程组装，null/非法options抛组装异常 |
| 装草稿 | `public void LoadDraft(ProcessingGraph graph)`；复制冻结，Generation+1、Stale旧预览并取消，Plan异步在非UI线程 |
| 来源 | `public void SetSourceSelection(EditorSource source)`；无IO值赋予，Generation+1，身份修改取消旧预览 |
| 权限 | `public void SetPermissions(EditorPermissions permissions)`；撤回预览权停止新预览并取消旧请求；撤回保存权禁新提交并请求取消本控件保存，保存知识仍按查询/证明而非权限推断；不取消别宿主 |
| 语言 | `public void SetCulture(string cultureName)`；zh-CN/zh-TW/en-US及资源支持扩展，非法名参数异常；不改图/Generation |
| 预览 | `public ValueTask<PreviewStateEvent> RequestPreviewAsync(CancellationToken waiterToken)`；只观察CommandWaitLimit，返回当前Previewing/Draining等状态，内部操作继续排空 |
| 存草稿 | `public ValueTask<DraftSaveResult> SaveDraftAsync(string requestId, CancellationToken waiterToken)`；先冻结当前有效草稿及Sink.Context生成Identity，等待CommandWaitLimit；超时/等候取消返回Unknown，Identity不可丢；晚回执只更新该原revision保存状态 |
| 保存查询 | `public ValueTask<DraftSaveQueryResult> QuerySavedDraftAsync(DraftSaveIdentity identity, CancellationToken waiterToken)`；同Sink.Context、本次或Host恢复的原Identity，有界Found/NotFound/Unknown；不从查询触发保存 |
| 建议应用 | `public DraftApplicationResult ApplyAdviceToDraft(DraftApplication request)`；同Advisor本地绑定，无直接生产Apply |
| 建议评估 | `public ValueTask<AdviceSnapshot> EvaluateAdviceAsync(AdviceRequest request, CancellationToken waiterToken)`；使用Host显式样本/ScoreSpec与当前草稿，验证全部绑定，控件记录本次operation；CommandWaitLimit只停止观察，迟到/关闭仍由控件排空 |
| 关闭 | `public ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit)`；停准入，取消本请求/保存，Clear两viewport并等本borrow/drain |
| 事件 | `public event EventHandler<DraftChangedEvent>? DraftChanged;` / `public event EventHandler<PreviewStateEvent>? PreviewStateChanged;`；UI dispatcher更新，回调异常诊断、不丢Owner |
| 建议事件 | `public event EventHandler<AdviceStateEvent>? AdviceStateChanged;`；值结果只对当前Generation展示，旧建议保留诊断但禁止应用 |
| 保存事件 | `public event EventHandler<DraftSaveStateEvent>? DraftSaveStateChanged;`；含完整原Identity；草稿已改也只更新原revision历史，不能将新代标为已保存 |

依赖实例/端口宿主拥有，控件只关本次借用/自己创建executor，不关共享Advisor/Provider；控件Close请求取消其advisor操作时必须是本控件发起的operation，不按全局Advisor.Close取消他人。原/派生viewport SetContent成功后仅借用显示，borrowOwner仍控件；Released含义为“上一个content显示借用已退出”，不是新content已关闭。失败/超时SetContent若已用新content必须在Clear Released=true后才释放，UI保留该content并计账；端口不得在返回Released=false时忘掉新/旧内容。控件最多每viewport一个在途更新，新代到来等旧Clear再换，不能无限叠图/无限task队列。viewport不Dispose传入borrow，Clear真实退显示后控件Close借用；等待取消/窗体消失都不是退显示证明。

SourceRevision是本次有序来源集合的Host可信修订，另外逐FrameReceipt核源hash/域；不只用文件名。原Viewport以第一选中可信FrameBinding取得独立borrow；Derived来自本请求声明OutputKey，AcquireRead得到独立borrow，不直接把BackendImage给WPF。MaxPreviewRetainedBytes1..64GiB且受Host更小预算；输入/结果/显示副本合计，Source原lease不被控件释放。
所有Load/Set/事件/草稿缓冲在WPF Dispatcher线程；耗时Plan/Executor/Scorer/保存只在背景，完成只用绑定Generation的dispatcher小更新，关窗/旧代到来晚Owner仍归原控件恢复域。API自有值校验/权限拒为ExecutionDiagnostic，不native堆栈；缺源/不完整图拒预览但可继续编辑。

保存是Host独立草稿IO端口；本模块冻结身份、查询、幂等和未知恢复语义，见下列D-SAVE规格。SaveAsync/QueryAsync/CloseAsync每次waitLimit均1ms..10min，控件用CommandWaitLimit；本地等待期限/等待者取消返回Unknown及原Identity，不靠抛取消丢失身份。Host保管未结束IO、日志/无提交封锁及可信主体校验，生产发布仍归Host。CloseReleased=true只证明本Owner任务/借用退出，保存事实只由Saved/Found或带无提交证明的NotSaved/NotFound决定，两者不得互推。EditorOptions.MaxPreview/ExecutionOptions预算一致，真实IO恢复/WPF验收另行执行，不能替代本端口规格。

### D-SAVE：保存身份、有限查询与恢复

1. **冻结身份。** Host为本Sink构造可信不可变Context：StoreScopeKey是隔离存储域ID，OriginHostEpoch为Host实例32位小写Guid N，PrincipalKey为当前认证主体稳定ID（均不是密码/token），MaxSaveRequests为1..4096。控件从Sink.Context读取，不能让文本框、EditorPermissions或请求自报主体授予权限。StoreScopeKey/PrincipalKey各为1..128可打印ASCII；Context启动后不变。每次新保存RequestId为32位小写Guid N（UI/Host事先分配），绑定GraphId/原GraphRevision/GraphHash；调用前冻结全部Draft并用已接收P0重新Plan核Hash，之后编辑/语言/源变化不改变此Identity。GraphId沿§3、GraphRevision沿原1..128规则。身份定位键=(StoreScopeKey,OriginHostEpoch,PrincipalKey,RequestId)；同键不同GraphId/Revision/Hash/Context限制值为Conflict，不覆盖原记录，不因为只按revision查询串请求。
2. **当前主体核验。** Sink每个Save/Query/Close入口依据Host当前可信身份验证与Context.PrincipalKey一致及对应保存/查询/停止本请求权限，权限在实际提交门前再核；身份字段只是匹配值，不是能力凭证。过期会话、撤销权限、跨主体/域/epoch的Save/Query返回Unknown+PermissionDenied或SaveIdentityMismatch，无Receipt/NoCommitRevision，不能泄露他人保存事实，也不能把拒绝当未保存。Close未授权返回Released=false及权限诊断，不伪造成功；Host可信后台Owner仍须在权限撤回时取消未提交写入并独立排空，不依赖操作者继续有查询权，不丢原资源。EditorPermissions只控制UI入口，不能代替Sink授权。切主体不换Context并重用旧请求；原请求留原Owner排空，新主体另建其自身控件/Sink，不继承旧保存权。
3. **单一提交门。** Host在可信范围内为identity键原子登记不可变graph闭包，记录Commit/NoCommit终态。Draft写入及Saved回执必须绑定同一原Identity/StoreRevision，不能只把内容写了再靠内存状态猜是否成功。同键同内容重复Save只回原结果/Unknown，绝不执行第二次写入；同键不同内容Conflict，原请求仍可查。Host不可把超时/异常/取消假定为回滚。旧写入若提交或“是否已提交”未知，保留原记录/Owner；不自动续一个新RequestId补写。
4. **Found。** Query返回Found时Receipt非null且Identity全字段一致，StoreRevision为1..128非空可打印ASCII；NoCommitRevision=null。它表示该原请求草稿已提交且可由Host按StoreRevision读取，后续删除/保留期变化不应把此提交墓碑降为NotFound。控件显示原revision已保存，不再提交；草稿已变化则新草稿仍未保存。Found可IoDrained=false（旧写入回调仍退出中），不能用保存成功提前释放IO Owner。
5. **NotFound。** 仅在Host完成与提交门串行的持久NoCommit封锁后返回：Receipt=null、NoCommitRevision非空1..128可打印ASCII，证明该原identity未提交，而且任何在途/迟到旧Save都不能再提交。普通数据库无行、文件暂未出现、在途尚未登记、复制滞后、超时或进程退出均不足。Query对已验证、确实无写入且没有不确定外部提交的identity，可原子建立NoCommit墓碑封住尚未开始的旧请求；这只关闭该保存尝试，不写草稿/不发布。若外部写入无法证明未提交或无法隔离，必须Unknown，不能建立假封锁。晚Save见NoCommit只返回NotSaved，不解封。NotFound可IoDrained=false表示旧IO还在退出中，控件先Close/回查排空，不能马上新建保存。
6. **Unknown。** Receipt/NoCommitRevision均null；涵盖在途、观测超时/取消、断连、损坏/缺失日志、权限不确定、回执不匹配以及不确定写入。保留原Identity/冻结图/来源Generation和IO Owner，保存命令禁用，允许编辑/预览和显式“查询保存状态”。同一Sink/identity最多一个后台Save和一个Query，没有轮询风暴；重复Query只附着同一查询或返回Unknown+ConcurrencyViolation，不派新IO。Query本身有独立waitLimit，不修改原Save期限或续写；迟到Query只能记录原Identity。Unknown晚于已有可信Found/NotFound到来仅记录观察诊断，不降级原确定事实；Found与NotFound互相矛盾或错Identity/Receipt则保存知识隔离为Unknown+SaveReceiptMismatch，禁止重提，交Host核对，不择一个顺眼结果。
7. **重新保存与重复命令。** Saved/Found确认且IoDrained=true、原Close.Released=true后不重复原请求；操作者明确保存新修订才分配新RequestId。仅NotSaved/NotFound具有匹配NoCommitRevision且IoDrained=true、原Close.Released=true并当前权限仍允许，才可明确新RequestId再次保存；不自动重试，原NoCommit墓碑仍在。Unknown或IoDrained=false期间，同控件所有新Save禁用（编辑/预览可继续），Ctrl+S转为查询原Identity，不改变原graph/hash。SaveDraftAsync收到已登记RequestId时先比当前有效graph/hash及Context：一致只附着原attempt，不分配新IO；草稿已改则Unknown+Conflict并保留原Identity，需Query原记录而非按新草稿覆盖。同键变体到Sink也Unknown+Conflict，不修改原提交记录。NotSaved不是一般异常：必须对应上述NoCommit证明。Rejected只用于本地参数/无效草稿且该次从未派发时，Identity可null、IoDrained=true；不撤销任何先前同ID的结果，也不能替代已派发请求查询。
8. **有限Owner与恢复。** 每Context最多MaxSaveRequests个稳定墓碑/控件保存记录（含Unknown），超限在准入前Rejected/BudgetExceeded，不删除Unknown或已封锁键以供旧ID重跑。冻结图/规范字节/保存及查询缓冲/墓碑元数据纳入EditorOptions.MaxPreviewRetainedBytes累计账，与预览共享更低Host上限；每图仍受GraphLimits字节限，超总限前拒，不无限保留每次完整graph。确定且IoDrained/Close已完成后控件可释放完整图、只留有界Identity/Receipt/NoCommit墓碑；Host持久记录按自身保留策略提供真实旧查询，缺失或损坏为Unknown，不恢复成NotFound。每控件仅一个未决保存（包括未排空的终态）；已结束且排空后可明确保存下一请求。Close(identity)停止该identity的新写入准入、请求取消本写入/查询并有限等待，重复Close只观察未完成阶段；Found已提交不撤销，Released=false保留原IO/额度；Released=true而查询仍Unknown也不允许重提。端口每次方法有界返回，后台IO只有Host在真退出后释放，不能把观察返回当task真停。控件关窗依次对本未排空Identity调用Sink.Close，组合其CloseReceipt与viewport/executor释放；调用者等候取消只结束观察，不能清记录。已Closed控件只可对已登记Identity执行Query/Close恢复，不可保存/编辑，Host也可直接调用原Sink的相同入口，不关其它控件共享Sink实例。已经匹配旧Identity的Query/Close恢复在记录上限时仍允许；新的未登记键超过上限只Unknown+BudgetExceeded，不能建NoCommit后谎称已查。
9. **重启。** Sink.SaveAsync的Host适配器从请求入参先可靠登记完整Identity/冻结图或可验证引用/Unknown状态，才派发任何实际草稿写入；控件本地把Identity与Generation关联，不要求Host读取控件私有状态。登记本身无法确认则Unknown，不开始草稿写入；只有可证明NoCommit封锁才返NotSaved。重启后由当前可信同主体显式打开原存储域/OriginHostEpoch的恢复Sink，Context必须仍匹配原Identity，不改旧epoch“凑当前实例”；Host验证恢复授权，可与当前进程epoch不同。恢复仅Query/Close；新的保存另用当前Host epoch的Sink，且原请求Found或有NoCommit证明且排空后才能进入新保存。Host丢失/不能验证原Identity或提交日志为Unknown，按原域人工核对，不重新写入猜结果。生产发布始终为独立Host事务，本模块不获得发布权。

Sink保存结果约束：Saved→Receipt非null且匹配、NoCommitRevision=null；NotSaved→Receipt=null且NoCommitRevision匹配已封锁原记录；Unknown→两者null；Rejected仅表示本次入口未准入，不能用于证明先前同键未提交。除控件本地Rejected外Identity必须非null且等原Identity；IoDrained是该identity本Owner已发起全部后台写入/查询实际退出的观察（不包括本次将返回的同步值封装），未知为false，与草稿提交状态独立。Query结果始终携原Identity，限Found/NotFound/Unknown，非法字段组合/错revision/hash均降Unknown+SaveReceiptMismatch。CloseReceipt仍沿P1真实释放语义，不能把NotFound当Released或反之。保存requestToken由控件自有取消源+真实权限撤回/关闭驱动，SaveDraftAsync的waiterToken只停止等候；Query waiterToken只取消该观察，不能越权取消旧写入。

Context按值冻结并在每次入口与Sink.Context逐字段比较，查询不持久更换主体/epoch。合法waitLimit从各入口进入计单调时间，登记/权限/本次IO观察共用剩余，子阶段不续期；非法waitLimit抛参数异常且不派IO，端口超时/取消/通信异常在合法identity下返回Unknown而非丢身份的异常。NoCommitRevision由Host真实封锁记录提供，不接受控件传值冒证明；Found回执与查询均由Sink当前可信范围验证后给出。唯一保存位置键不含GraphRevision作为唯一键，避免相同revision不同请求绕过幂等；Hash重新Plan检查，模块图schema及规范图字节仍沿已接收0.4，不为保存协议换hash算法。

Query若需要新建NoCommit封锁，当前主体除查询权外还必须有停止该原请求的权限，否则Unknown+PermissionDenied；纯查询权限只能读已经证明的Found/NotFound，不能悄悄封住仍可提交的尝试。已Closed控件的恢复Query可产生新的有界观察Owner，此时先将自身恢复清理状态置为未排空，后续Close再确认；旧Released回执只证明当时所有权已清，不覆盖新观察，仍禁止重开编辑/保存。

附录C补充稳定Code：P1全集加AdviceStale/ScoreInvalid/LabelUnavailable；NoRecommendation为AdviceStatus不是错误。附录D补充PermissionDenied/SourceMissing/DraftInvalid/SaveOutcomeUnknown/SaveIdentityMismatch/SaveReceiptMismatch；Timeout/等候取消给原Identity的Unknown并用既有TimedOut/Cancelled诊断，不当写入终态。全部本地化ResourceKey仍Preprocess.+Code，不把错误文本当可重试命令。API所有waitLimit/CommandWaitLimit都是1ms..10min的有限观察；WaiterCancelled只停止观察，Close内部取消仅其Owner的执行，不能越权关共享依赖。Editor/Advice的公开结果/事件同样无产品放行权。

P1/Editor从Planning用唯一PreprocessingGraphPlannerFactory创建本版本planner，不注入任意canonicalizer/hasher/planner改变相同合同语义。Backend返回值由Core核对Definition/Shape/Runtime/域/有限性，不因PortStatus成功跳过约束。AcquireRead只返回独立借用，Control等待期间若Acquire晚完成仍归原Control，Close接管并真实归还。

EditorOptions.GraphLimits必须逐字段等于EditorDependencies.Planning.Limits，Execution.Planning也须相同，否则构造拒ArgumentException；不允许UI与执行用两套范围。所有factory/构造器对null/非法组装值抛标准参数异常；Wait/Close非法waitLimit抛ArgumentOutOfRangeException且不触发取消/关闭副作用。合法Close先停准入，不因调用者等候结束重新开放。WaitAsync已terminal立即Terminal；未terminal且token已取消时返回WaiterCancelled及当前快照。TryTakeResult非终态/已交接/先关闭均false且out=null，唯一成功在真终态之后；非terminal Outcome永远null。RetainedBytes为已知仍计账字节的非负总数，RetainedBytesExact=false表示另有无法量化的native/迟到分配，0只是已知账项为0，不证明释放；Released=false且Exact=true也可能仅等待未结束回调而无像素残留。未知部分不得作为精确峰值或达标证据，保留Owner/额度。Released=true必须本Owner资源真实退出且RetainedBytes=0、Exact=true，不包括已转出的独立输出。

Shape/Domain/Receipt新增字段与canonical统一：FrameReceipt.Grid按记录顺序写InputGridKey和Steps；每Step写Crop/Resize参数discriminator及字段，不能写NodeId/Method的隐式默认。RuntimeDescriptor的HalconVersion固定26.05，BackendRevision/DeviceKey/ThreadPolicyRevision按ID规则；所有Expected/实际值深比较，不靠record的ImmutableArray引用相等。NodeReceipt.Numeric数组长度必须等输出通道数，min/max有限且min<=max，ValidPixels+InvalidPixels=Width×Height（像素计数不是乘通道数）；有效域empty不得成功。ClippingObservation仅NotObserved/NotApplicable，本版Float32不编整数裁切计数。

高级参数建议面板采用GridControl展示候选/逐样本损失/有效性/并列及拒绝原因，显式“评估候选/取消/应用到草稿”；条件不足给字段诊断。候选数/样本数/ScoreSpec来源常驻，无评分只诊断且应用禁用。Host传入样本/标注，不在模块读业务库；同Generation完成才更新列表，旧结果标过期，不自动选排名第一。控件自有AdviceOperation自行Wait/Take一次，Host接收值结果后调用Apply；别宿主Advisor操作不能被控件取消。应用权限撤回只取消本控件Advice并禁用Apply；保存观察超时为Unknown/SaveOutcomeUnknown，后台写入及查询真结束才可通过Sink.Close确认该IO Owner已归还，方法有界返回本身不证明IO退出。

既有0.4.0定向校验：本地链接目标存在，代码围栏成对，无尾随空白/替换字符；§11固定图独立编码197字节，SHA256与附录A一致。2026-10-10同步P0/P1/P3已接收规格并定向修订P4保存查询；2026-10-11仅同步主控对保存查询指导内容的限定接收，P4真实WPF/Host持久保存恢复及运行资格仍PreparationIncomplete。文本/字节对应关系不能替代Core或产品测试，本次未重审或执行运行验证。

本次收口同步BackendSessionContext、NormalizationReceipt、SourceFrameReceipt/SourceReceipt.Domains与RetainedBytesExact到公开记录：Core每实例创建Guid.NewGuid().ToString("N")为内部InstanceEpoch。主reservation.OwnerKey=InstanceEpoch+"."+SHA256(长度前缀字符串域ASUN-IM021-OWNER-V1→RequestId)；子OwnerKey=主OwnerKey+"."+SHA256(长度前缀字符串域ASUN-IM021-OUTPUT-OWNER-V1→OutputKey)。摘要为64小写hex，字符串编码沿附录A；不直接用带点ID拼接，避免a.b/c与a/b.c歧义。资源身份不进入Graph/Request摘要，不当来源内容hash。共享Budget以OwnerKey区分实例，allocationKey只在该Owner内唯一，Transfer不能改变所属请求硬限或复用已有子OwnerKey。Backend Begin按该Context取得请求/图/修订/runtime及OwnerKey，导出无需从日志或隐藏静态状态猜身份。

派生FrameReceipt.FrameId固定为`derived.`+SHA256(长度前缀字符串域ASUN-IM021-DERIVED-ID-V1→Context.OwnerKey→OutputKey)，长度72，落在回执身份1..128范围；SourceRevision=Context.RequestHash，ContentHash独立按导出像素计算，GraphHash保留在SourceReceipt，避免同请求多输出/多实例串帧。SourceReceipt.Frames逐项含GraphInputKey及实际FrameReceipt并按该Key排序，Domains按GraphDomainKey排序保留实际限制域/摘要，不能只保原帧域漏掉本次mask。真实Backend必须核session Context与Export.Source一致，失败仍归原Owner排空。

BackendNodeRequest.Images唯一顺序为Linear的image0..N-1、Binary的left/right、FlatField的image/reference、其它的image；不因canonical把port按Ordinal排序而重排操作数。Mask只DomainLimit可非null、必须为该图绑定域，其它节点必须null。Fixed/PerFrame范围回执与§7公式同步，整图/Tiled都保存同一次选择范围；MaxTiles总额及Crop局部边界按§7实施，不把待运行的native资格当已通过。

## 附录 E：P2 公开装配与 CPU 帧桥 0.1-prep（确定指导内容限定接收）

2026-10-11 主控已回读0.4.3-review本附录E.1–E.6，定向比对image-frame公开字段/Factory/rows/scope/回执，限定接收公开工厂/稳定runtime借用、CPU平面/域/真实held容量、Import/Export独立Owner、完整32×24软件双Host及有限原Task恢复的确定指导内容。主控独立按x/y生成768-byte标量并构建52-byte PIXELS头，raw768/local820bytes的两hash与本页一致。此限定接收和编码证据不表示真实HALCON、稳定RuntimeOwner、CPU接线、原生资源、Golden、运行或性能通过；这些门保持PreparationIncomplete，P2不标纯Core Ready。

本附录只补 P2 装配，不修改附录A/B/C/D已接收的公共类型、算法、图向量、保存事务或准入状态。依据为 image-frame 当前 §4.3 Resources v0.1、§4.4 Core v0.2、§4.5 scope并发与 §19.4迟到交付规则；这些上游类型只读。以下为未来C#公共签名规格，尚未创建工程、编译或运行。namespace 均为 `Asun.Modules.ImagePreprocessing.AsunImage`，using 为 System/Collections.Immutable/Threading/Tasks、Core namespace `Asun.Modules.ImagePreprocessing` 及 `Asun.Modules.ImageFrame.Resources`；没有 native 类型出现在签名中。

### E.1 自有 Factory/Options 和稳定 RuntimeOwner

```csharp
public sealed record AsunImageBackendOptions(RuntimeDescriptor Runtime,
    int MaxSessions, TimeSpan DrainObservationLimit);
public sealed record AsunImageBackendDependencies(
    IStableRuntimeOwner RuntimeOwner, IMonotonicClock Clock);
public interface IStableRuntimeOwner {
    ValueTask<PortResult<IStableRuntimeBorrow>> AcquireAsync(
        BackendSessionContext context, CancellationToken token);
}
public interface IStableRuntimeBorrow {
    RuntimeDescriptor Runtime { get; }
    bool IsCurrent { get; }
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public interface IAsunImageBackend : IPreprocessingBackend {
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public sealed class AsunImageBackendFactory {
    public AsunImageBackendFactory();
    public IAsunImageBackend Create(AsunImageBackendOptions options,
        AsunImageBackendDependencies dependencies);
}
public interface ICpuFrameCurrency {
    bool IsCurrent(FrameKey key, FrameReceipt expected);
}
public sealed record CpuFrameSourceBinding(string ProviderKey,
    IFrameService Service, FrameDescriptor Published,
    ImmutableArray<int> SourcePlaneIndices, FrameReceipt Receipt,
    string OriginalContentHash, ICpuFrameCurrency Currency);
public sealed record CpuFrameProviderOptions(
    ImmutableArray<CpuFrameSourceBinding> Sources, string ConsumerId,
    int MaxConcurrentAcquires, int MaxAcquisitions, long MaxScratchBytes,
    TimeSpan ReadTimeout, TimeSpan DrainObservationLimit);
public interface ICpuFrameInputProvider : IFrameInputProvider {
    ValueTask<CloseReceipt> CloseAsync(TimeSpan waitLimit);
}
public sealed class CpuFrameInputProviderFactory {
    public CpuFrameInputProviderFactory();
    public ICpuFrameInputProvider Create(CpuFrameProviderOptions options,
        IMonotonicClock clock);
}
```

上述sealed类的公开无参构造和Create是签名声明，代码围栏不提供方法体。Create只深冻结/校验配置，不Acquire、不native、不启动Task、不读像素、不接管外部Service/RuntimeOwner。null抛ArgumentNullException，范围非法抛ArgumentOutOfRangeException，字段/跨绑定不一致抛ArgumentException；构造失败全部外部对象仍归Host。MaxSessions/MaxConcurrentAcquires为1..256；MaxAcquisitions为1..4096且不小于MaxConcurrentAcquires；Sources为1..256项、ProviderKey唯一且沿附录A标识规则。ReadTimeout为1ms..24h，DrainObservationLimit/所有Close观察为1ms..10min；MaxAcquisitions计本实例所有已接纳Acquire的关联墓碑，不因归还就清掉身份，满额BudgetExceeded且不发起上游读。并发超限ConcurrencyViolation，无内部队列。Sources的frame/metadata/receipt全值冻结，Service/Currency是明确借用能力，不能用可变字典热换源；换绑定须新provider。

Options.Runtime必须为HALCON `26.05`、BackendRevision=`im021-asunimage-cpu-v1`、DeviceKey=`cpu`、IntZooming=false；MmxEnabled显式由Host冻结，ThreadPolicyRevision为1..128可打印ASCII且不为unknown。每次Begin.Context.Runtime与Options.Runtime全字段相等，reservation.OwnerKey与Context.OwnerKey相等，不一致RuntimeDrift/Conflict，不触发native。Clock必须与同一executor的ExecutionDependencies.Clock为同一对象；双Host可共用该Clock。后端各有限观察/耗时用它，不能另建UTC/Stopwatch预算，也不能将image-frame.ObservedUtc当执行期限。两个Options.DrainObservationLimit用于各自内部单次恢复观察上限，公开Close的waitLimit另限本次调用；均不停止或替换原Task。恢复查询每轮按原Clock有界等待，不忙轮询；未知关联不释放或自动重做业务。

RuntimeOwner由Host实现这个本地端口，无须构造隐藏的全平台Runtime服务。Host在首次借用前已显式设置runtime；活跃稳定borrow期间阻止所有受管理路径修改这些进程设置/线程政策，多个同descriptor只读借用可并存。无法约束其它写入者则拒借RuntimeDrift，前后回读相等不能证明稳定。Acquire按原Context关联，取消/失败后未释放borrow仍须非null返回供session接管；端口Task不能因观察期限而提前结束并遗失晚borrow。IsCurrent同步、线程安全、无IO；失效单调为false，不许恢复为true，重设runtime需新借用/新执行请求。模块不调用set_system。

Begin先在门内占session槽并创建拥有Context/reservation/原Task的session恢复壳，再调用RuntimeOwner.Acquire；非null借用立即归该session，核Runtime及IsCurrent。晚成功归原session关闭，不交新请求。Acquire在途时Begin原Task仍保留，Backend.Close只有限观察、停新Begin，不抢关RuntimeOwner。每session串行Import/Execute/Export，原native真实退出后才ReleaseImage/Close；同session重叠调用拒ConcurrencyViolation。每次算子前后及导出交付门核稳定borrow.IsCurrent与Runtime，漂移即停后续派发/交付并排空。失败临时iconic/tuple/pin仍登记session；即使Begin Failed，若曾取得未释资源则Value为该session，沿附录B接管。session最后归还稳定borrow且自身创建的charge确认释放才Close.Released=true并归还session槽，不要求同reservation中的Core源borrow已关闭，不代Core关闭主reservation。已交接的托管输出独立，不继续持runtime借用，不阻session槽回收；Backend.Close只关闭自己的sessions，不关闭Host RuntimeOwner/共享Budget/provider。

### E.2 image-frame CPU 逐字段映射

CpuFrameSourceBinding由可信Host从已成功Publish的实际FrameDescriptor建立；Published不是预发布草稿。FrameDescriptor没有ContentHash、RegistrationRevision、CoordinateRevision或IsCurrent，不从SourceId/CoordinateReference推导这些字段。Receipt.ContentHash必须是附录B `ASUN-IM021-PIXELS-V1` 的本地SHA256，OriginalContentHash保留原来源摘要及其算法标识（非空、UTF8最多1024bytes）；若原来源未给摘要，Host明确保存 `unavailable`，不能把文件名当hash。OriginalContentHash只作该绑定的Host追溯，不进请求摘要、不替代ContentHash，也不改变SourceReceipt合同；需要持久追溯由Host保存绑定与原SourceId/SourceRevision/CoordinateReference。

| 上游实际字段/调用 | 本地值与必须核对 |
|---|---|
| Published.Key / Service.ServiceEpoch | 非空Key.Id、Revision>0、非空epoch；FrameId=`Key.Id.ToString("N")`，SourceRevision=`Key.Revision.ToString(InvariantCulture)`。原Published.SourceRevision另保Host追溯，不伪装这个版本号 |
| Published.SourceId/SourceRevision/CoordinateReference | 按上游必填规则核；可信Host提供RegistrationRevision、CoordinateRevision、InputGridKey及空Steps的Grid。CoordinateReference是引用，CoordinateRevision是修订，不互相冒用；同格多源按附录B要求真实配准 |
| SourcePlaneIndices | 源plane索引非空、严格递增唯一且在Published.Layout内；Acquire全帧，Window=(0,0,Width,Height)、Halo=0、ExactSamples、ClipAndMarkInvalid，保留洞/空域，不用RejectMissingSupport强迫Full |
| ReadAsync返回lease | 核ServiceEpoch/原RequestId/ResultLeaseId=lease.Id、lease.ConsumerId、SourceKey、两个Window全帧一致、SourcePlaneIndices与请求一致；Layout/Metadata与所选源plane的实际全帧描述一致。Readonly局部plane索引0..N−1，与源索引不能混用 |
| Layout scalar/packing/Metadata | 仅UInt8/UInt16/Int16/Float32，均LittleEndian、Intensity/ColorR/G/B、Unit=`1`/Scale=1/Bias=0；SinglePlane/Planar单通道或Interleaved2..4通道。拒Int32/Float64/Height/Mask/Auxiliary及未解码格式，不隐式单位/颜色变换 |
| 通道展平 | 按SourcePlaneIndices的源顺序，再各Metadata.Channels原顺序展平，1..16个、全局唯一，所有通道同Scalar。对应Receipt.Spec.Channels/PixelType。逻辑borrow plane是展平后的单通道，独立于上游多通道plane |
| 有效域 | 每个选中plane取Layout.Domain∩Metadata.ValidDomain，必须全部逐段等值。不能偷偷交集不同channel域来改本图输入；不等DomainInvalid，Host可分别发布独立输入。Full展开每行[0,Width−1]；Empty为空Runs；RowSegments的EndXExclusive转checked(EndXExclusive−1)。按本地排序/合并规则核并用附录B重算DomainHash，格/尺寸一致 |
| Receipt.Spec.DomainMode | 实际Full为FullRectangle，洞/Empty为ExplicitMask；必须与图声明和Expected一致，不能扩大域满足Resize。有效Float32有限性仍在Import核，域外字节不授质量事实 |
| lease.Allocations | 当前Resources CPU路线恰好一项Cpu、Guid非空/Bytes>0，Bytes=Layout.DeclaredBufferBytes；核AccessibleBytes及布局边界。源held容量即该真实allocation.Bytes；共享小窗口也不能按逻辑像素低报，本桥固定全帧。borrow.RetainedCapacityBytes还包括E.3自有行scratch实际容量；多allocation/其它ResourceKind不是本版能力 |
| ICpuFrameCurrency | Host绑定(key,Receipt)的可信失效状态，源关闭/撤权/替换按宿主政策失效；单纯相机断连不改变稳定快照。接口同步、线程安全、无IO、非阻塞，同绑定失效单调为false，未知/抛错按SourceInvalidated停止派发。Acquire前后、每次CopyRows前后及Core既有节点/发布检查均核IsCurrent；失效不Release正在使用的lease |

Domain模式来自实际域，不从空Rows误判Full；上游发布归一化后的Padding/stride/offset不是算法数据，CopyRow由上游负责地址计算，本桥不访问数组或指针。所有上述结构先校验范围/总段数及checked算术，再线性扫描/分配；域Runs≤1048576，元数据暂存计入provider有界绑定容量及Host预算，不绕过Core请求预算。绑定源通道数/尺寸沿附录A范围；存在但本桥不支持的布局为UnsupportedParameter，规格不一致InputShapeMismatch，域错DomainInvalid，摘要不一致Conflict，当前性失效SourceInvalidated。

Options.ConsumerId由Host在任何Factory前生成，固定为 `im021.`+独立Guid的N格式（38字符），并在创建共享FrameService前登记ConsumerLimit；同provider全部Service都登记该键。不同provider使用不同ConsumerId，便于两Host持有隔离。它是额度/持有键，不是权限凭证，ProviderKey不兼作consumer。

### E.3 Acquire、逐行复制、归还与关联

MaxScratchBytes为1..256MiB，是本provider同时持有的行缓冲总硬限，须不超Host显式部署预算；ConsumerId沿E.2已预登记。它们均是必填Options，不留构造后补配步骤。

Acquire不重用Host原lease：预检ProviderKey/expected逐字段等值/IsCurrent→门内占有界Acquire槽并创建borrow恢复壳→生成一个新的上游Guid RequestId并保原ServiceEpoch/FrameKey/ConsumerId→强持Service.ReadAsync(...).AsTask()。同绑定多Acquire分别拿独立lease；每个ValueTask只转Task一次。上游请求Timeout用Options.ReadTimeout；Core请求截止点仍是附录B原Clock，任一取消/期限停止交付。Core有限观察不能改写原read Task。

成功Completed/Empty且Slice非null时，borrow先接管lease再核E.2/取消/当前性。上游仍在Draining/DrainUnknown或Query Unknown时原Acquire Task不得伪完成，保原关联由provider用同Clock有限观察再QueryOperation(originalEpoch,originalGuid)，不重新Read、不把NotFound当释放。Read Task完成与Receipt.OperationResourcesReleased分开核；只有合规上游确认本操作已退出且没有未交付lease才可返无Value失败。出现任何非null Slice均接管，不因业务失败丢弃；核对失败返回Failed+原borrow，由Core Close。未交付或迟到资源归原borrow/provider，Close不停用恢复查询。上游若异常产生ResultLeaseId但不交能力对象，记录BackendError/NativeDrainUnknown并保关联、服务Owner协同恢复，不能造一个新lease或靠ID猜已归还。

borrow.Receipt是该绑定冻结的本地Receipt；IsCurrent为未Close且Currency仍真。成功Acquire交付前按所选plane最大RowBytes精确分配一块byte[]行scratch，门内先原子预占MaxScratchBytes，分配失败BackendError，原lease仍归borrow排空；不用ArrayPool。RetainedCapacityBytes=源held容量+scratch.LongLength，交付后容量恒定，Core按实际值计请求/共享retained预算；provider硬限与上游consumer限额属于Host同时峰值的一部分，不重复相加当RSS。元数据对象和CLR头另测，不宣称这个字节限覆盖进程堆。

CopyRows按附录B精确规则：plane为展平通道零基，rowCount1..64，行范围合法，destination恰为rowCount×Width×标量字节数（checked且≤int.MaxValue），成功written等于全部字节数。一次borrow只允许一个CopyRows；并发参数错误在写destination前抛ArgumentException。每次开独立scope，先检查TryOpenReadScope返回None且非null，逐行scope.CopyRow(上游局部plane,y,scratch.AsSpan(0,该plane精确RowBytes))；Interleaved按像素原顺序抽出选定channel，单通道直接复制，源padding不传。域外标量仍按原完整行字节复制，摘要含域外像素，域外浮点不当有效值；不得先置零再验证源摘要。

逐行前后核token/当前性；CopyRows没有本地deadline参数，不自行按ReadTimeout新造复制期限，Core原deadline通过其取消信号停止后续行；所有有限Close观察仍用原Clock。CopyRow同步真返回后才复用scratch，scope.Dispose真完成后才结束本地Task。取消抛OperationCanceledException只允许在实际同步读取退出/本次scope已归还后；读取错误以原borrow关联保留稳定FieldPath/上游错误供Host诊断，Core按BackendError接管，不能返回短written冒成功。destination在原CopyRows Task完成前仍由调用方强持；失败时其内容不可消费。Close与CopyRows用同门：停止新CopyRows，已有同步复制真实退出/Dispose后才lease.ReleaseAsync(waitLimit)。不以关闭标志提前释放scratch。

上游Error映射：BudgetUnavailable/BudgetExceeded→BudgetExceeded；StaleRevision→SourceInvalidated；InsufficientSupport/InvalidSample→DomainInvalid/NumericInvalid；Cancelled/Timeout→Cancelled/TimedOut业务候选；DrainUnknown/Unknown→NativeDrainUnknown；Conflict→Conflict；LeaseClosed/Closed→Closed；NotFound→ReferenceMissing；InvalidArgument/UnsupportedFormat/LayoutOutOfBounds/AdapterFailure→BackendError。这些错误不证明资源释放，原上游Code/阶段由Host诊断关联保留，用户文字仍用Preprocess资源键。不扩充已接收P1错误闭包。

borrow.Close.Released只证明本borrow归还：全部CopyRows/Read原Task真实退出，读取OperationResourcesReleased=true，且ReleaseReceipt.LeaseClosed=true/Drain=Drained/Error=None后撤其held账、撤scratch全部强引用及预占，再归还Acquire槽。StorageReleased可能false（注册表/OCR仍持有），不阻本borrow的Released=true；它不谎报源存储已释放。RetainedBytes在自己尚持有期间为实际源allocation加scratch容量，归还后0/Exact=true；上游释放未知或关联丢失则保持原容量/Exact状态，未知容量Exact=false而不写精确0。provider.Close停新Acquire、关闭自己的borrow/等待原read，不调用Service.Close/Retire，不等待其它消费者；外部Service唯一Owner另行收尾。每次Close独立有限清理，不传已取消业务token、不重Read。所有Released=false对象/Task/回执/账留在原根Owner。

### E.4 Import、Export 与输出独立生命周期

Import以逻辑单通道plane/row顺序，通过CopyRows1..64行取得完整紧密LittleEndian标量矩阵；先预留实际托管容器、源held、native矩阵、域/tuple与暂存峰值，再分配。按附录B初始化SHA256投影并逐plane/row写像素，核Receipt.ContentHash；不使用OriginalContentHash充数。复制期间变旧停止，不因最后hash相等跳过当前性。Import前后核尺寸/类型/通道/域/格/Runtime，域内Float32 NaN/Inf拒NumericInvalid，源域外原字节参与hash但不参与有效运算。

冻结导入路线：每通道完整矩阵暂存保持pin→`cv2.gen_image1`按byte/uint2/int2/real复制进HALCON自有矩阵→真实返回才解pin→按通道顺序append_channel→gen_region_runs/reduce_domain恢复真实域。类型宽高由已验Shape指定，指针保IntPtr位宽，不暴露公共句柄或采用gen_image1_extern的外部内存回调。源borrow不因gen_image1返回就被session替Core关闭；Core仍按附录B生命周期归还。每通道输入/输出byte[]容量必须checked且≤Array.MaxLength及预算，否则BudgetExceeded；分配仍可能OOM，已接纳时BackendError且保原资源清理，不假预算拒绝。完整矩阵暂存不偷偷换块容器/改尺寸；这是本版明确实现限界。

Export校验SourceReceipt.Frames/Domains/GraphHash/schema/runtime与Context及实际导入闭包一致；每帧带原本地ContentHash/域/格，域限制不漏。`copy_image`取得独立深复制native图，按通道access_channel→get_image_pointer1只读→核返回类型/宽高→逐行复制到本版完整托管输出矩阵；拷贝中始终强持对应iconic，指针只在内部同步块使用，不写共享矩阵、不带出Task。输出域从实际get_domain/get_region_runs转本地DomainSnapshot并重算DomainHash，绑定PlannedShape.Grid.InputGridKey/完整Steps。

本版输出Owner固定托管CPU：完整紧密行像素、实际域、Receipt深冻结，并按附录B同一PIXELS投影独立计算派生ContentHash。域外导出像素明确置零（Float32为+0），只改新输出副本；域仍原实际域，不将零填标有效。FrameId/SourceRevision沿附录B派生规则，RegistrationRevision与CoordinateRevision仅在来源全部相同且原已知时保留，否则unknown，SourceReceipt仍保每个来源；几何新格完整Steps不冒充原帧坐标。源hash不写派生ContentHash，结果不含客户PASS。

深复制图/通道引用/tuple真实释放、托管输出完成后，Export原子将输出矩阵/域/Owner及其charge Transfer给附录B指定子OwnerKey；独立OutputOwner不持native/runtime，也不依Service/provider仍打开。Transfer失败、hash/域校验失败或取消竞争中未交付均归session/Core收尾。若晚成功已有子Owner，Export Value非null供原operation接管Close，不能丢给新请求。整个导出期间原native图、copy_image图、托管输出、域及hash缓冲同时计峰值；不能称一次像素大小足够。

OutputOwner.AcquireRead返回独立托管borrow，Receipt带真实派生hash/域/格；RetainedCapacityBytes为实际全部输出矩阵容量（不按所读行减账），分离borrow持有责任与共享物理charge。CopyRows仍沿附录B，无指针/native调用；Close停新borrow，已交付borrow/其在途行读取全部归还后才撤子账并Released=true。session/executor/backend.Close均不能关闭已Take输出或它的借用；输出可在这些对象关闭后继续读。输出IsCurrent只受自身Owner关闭/Host显式放弃约束，原相机后续断连不撤销已产出的派生事实；消费时仍须宿主核SourceReceipt的业务适用性，不给输出隐含放行权。

本轮只补读两页 HALCON26.05官方原件：[gen_image1](../../../halcon算子手册/operators/gen_image1.html#sec_description)明确新分配及调用后可归还输入存储；[get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html#sec_attention)明确行主序/首通道及对应iconic在世期间指针有效、共享写影响全部引用。真实C#签名仅按公共重载/消费编译确认；未检查封装内部、未重选既定算法。

### E.5 两个无 UI Host 的完整组装与收尾

本节是未来最小Host执行规格。下面冻结完整32×24 UInt8 mono/full域Replay软件夹具；其限额、像素和期限由本模块决定，不等待未知客户Profile，也不用于真实产线性能或物理验收。两Host共用源FrameService、同一个IMonotonicClock、Host稳定RuntimeOwner和共享IResourceBudget，各用独立provider/backend/executor/请求/输出Owner（每backend MaxSessions=1），不可共享一个executor并发执行。所有片段按第1–5步逐段执行，每次取得资源立即登记原根Owner，再进入下一步；它们不是省略收尾的独立脚本。

1. **任何Factory前**，Host进程根监督器先占有界Owner槽（每Host最多256个待恢复组、全部进程任务槽上限由Host Profile明确），保强引用到源Owner/Service、RuntimeOwner、Budget、Clock及两Host槽。满额先拒新Host，不开始任何工厂/读取/native。槽在方法离栈、关窗、观察结束后仍存在；只有全部自有资源确归还或另一根Owner明确接管并回执后才归还。根槽不是模块新增公共服务，也不写数据库。固定源服务owner独立于两个Host，不因一个Host退出而关闭。
2. Host先生成seg/ocr及来源绑定读取各自ConsumerId、登记到FrameService的ConsumerLimit；源Owner用 `new FrameServiceFactory().Create(resourceLimits, new ManagedLayoutValidator(), timeProvider, null)` 成功服务，再PublishCopyAsync并核Completed/OperationResourcesReleased/实际FrameDescriptor；源码行提供者保持至Publish真实退出。Published服务已由外部建立时只接受已登记这些键的实例，不热增消费者。上游TimeProvider与本地Clock采用下面同一对象；两模块timestamp不能交叉相减。FrameService构造无部分资源，失败Service=null；Publish未排空则原Task/Source/epoch/Guid留源根槽，不启动消费。**MaxCpuBytes为正；仅MaxNativeBytes/MaxGpuBytes/MaxCacheBytes=0。** 上游CPU单buffer能力仍为C=min(1_073_741_824L,Array.MaxLength)，本例768bytes不改变该1GiB边界。
3. 源Owner在其根槽强持一次精确全帧Read/lease/scope，按E.2展平行及附录B PIXELS投影算实际发布像素hash，scope退出/lease归还确认后才建立两份可信绑定；PublishCopy可能清域外/换序，不能拿发布前的原文件hash当本地hash。原摘要留OriginalContentHash。下面完整构造两份SourceBinding/Options/provider/backend/executor；本软件夹具每请求MaxManagedBytes=8MiB、MaxNativeReservedBytes=16MiB、MaxRetainedBytes=32MiB，Timeout=10s、DrainTimeout=2s。源FrameService的Native=0不代表AsunImage后端不需要native预算。预算不足仍按原错误/排空契约，不扩大限额或切换算法。
4. 分割图`seg/r1/im021-graph-v1`：输入source的实际Spec/grid1；SelectChannelParameters("mono")→NormalizeParameters(FixedRange,0,255,0,1)→FilterParameters(Gaussian,null,null,3,Reflect)，输出result绑定最后节点，各MethodVersion=1/Required、端口image显式指前驱。OCR图`ocr/r1`同schema/输入：CropParameters(2,3,16,12)→SelectChannelParameters("mono")→ResizeParameters(32,24,Bilinear)，输出result，各1/Required。分割32×24 Float32/full有效域；OCR32×24 UInt8/full域，GridTrace依次Crop与Resize。期望范围与细字效果仍按真实输入核，不给OCR精确计量坐标资格。
5. 两Host各用 `new PreprocessingGraphPlannerFactory().Create(planning)`→Plan完整图成功→核下面GraphHash并绑定Plan.GraphSnapshot。Frames为一个FrameBinding("source",自己的ProviderKey,绑定Receipt)，Domains为空，Options为Atomic/WholeFrame/Tiles=null/冻结runtime；下面请求给出完整参数和按附录B复算的RequestHash，不引用不存在的公共hasher、不发送空串要求Core代填。原完整图/RequestId/hash/options/关联记录先存根槽。Rejected无operation，仍关闭本Host已构造组件；Accepted立刻登记operation，再将WaitAsync(...).AsTask()一次登记，Wait超时只有限观察原operation.Query，不重Start。
6. 真终态后TryTakeResult一次。成功/完整图核result身份/GraphHash/runtime/SourceReceipt/输出类型域，再将每个输出Owner登记根槽（交接与登记同Host门，不留离栈空窗）。下游分割/OCR本身为Host消费者，不是模块新能力：AcquireReadAsync原Task先登记，得到borrow后强持直到下游原Task真实结束，才borrow.CloseAsync有限观察。示例消费逐行CopyRows记录Float32/UInt8标量及完整Grid/Domain/SourceReceipt；不调用不存在的下游实现，不把像素读取当分割/OCR业务验收。下游失败/取消仍先等其实际退出，晚borrow归原输出Owner收尾。失败结果不自动取原图替代。
7. 收尾顺序：本Host停止新工作/operation.RequestCancellation（需要时）→有限观察原Task/operation.Close→下游退出及所有borrow.Close→OutputOwner.Close→executor.Close→backend.Close→provider.Close。每步独立有限2s，用未取消清理路径；失败逐项保存并继续其它可独立关闭对象，不让cleanup异常覆盖原业务失败。每个Close.Released=false保原对象、原Task、账、身份/epoch/Guid及上次回执，根监督器后续只Query/Close原对象，不再Start/Read/换帧/换runtime。provider/backend可先停准入但真Released仍按自有Task/lease实际退出判断。主业务结论与cleanup结论分别显示。
8. 分割Host先Close时，OCR的原lease/Task/output仍可读，源服务和RuntimeOwner不由分割关闭；OCR也归还后，源唯一Owner才Retire/Close原FrameService，核其OutstandingLeaseIds/ResourcesReleased。根槽移交需接收监督器确认收到全部未决Task/资源/原身份，再原子撤旧责任，不能把消息发出当接管成功。进程不能强制删除未知native资源；未决情况下禁止重建假Released实例。P2没有跨重启native执行恢复，重启旧执行未知不得重放。

#### E.5.1 源服务、实际行 bytes 与共用 Clock

软件夹具进程根Owner预占3个组（源Owner、seg、ocr），总未退出Task槽64；未知Task仍占原槽，满额先拒。共享 `IResourceBudget budget` 和 `IStableRuntimeOwner runtimeOwner` 是组合入口两个显式注入端口（类型已经在附录B/E.1），不是模块新增工厂。budget软件端口按附录B原子预占/Charge/Transfer/Close配置总管理16MiB、native32MiB、retained64MiB、最多2个根reservation及其各1个输出子Owner；这覆盖两请求下列8/16/32MiB上限，子Transfer不再加总预占。服务/Replay来源及Host域元数据在源根Owner独立记账，跨Owner共享源不相加成RSS。runtimeOwner绑定下面完整descriptor并允许最多2个同descriptor稳定borrow，进程启动Owner预先配置/冻结相应HALCON政策，真实读取相符才准入；不能用恒true的假borrow运行native。受控fake只用于生命周期组，不作真实runtime证据。这两个已有端口不要求客户另给软件预算，真实HALCON绑定仍按E.1运行门验。

以下ReplayClock/ReplayRows32x24/ReplayFrameCurrency是最小Host内部辅助类型，可在未来同一个Tests Exe中实现；没有新模块API、发布DLL或独立工程，本轮只给指导内完整定义。标准using为System、System.Collections.Immutable、System.Threading、System.Threading.Tasks、System.Security.Cryptography，另引用 `Asun.Modules.ImageFrame.Core`、`.Resources`、`Asun.Modules.ImagePreprocessing`、`.AsunImage`。

```csharp
internal sealed class ReplayClock : IMonotonicClock {
    private readonly TimeProvider time;
    public ReplayClock(TimeProvider time) => this.time = time;
    public long GetTimestamp() => time.GetTimestamp();
    public TimeSpan Elapsed(long start, long end) {
        if (end < start) throw new ArgumentOutOfRangeException(nameof(end));
        return time.GetElapsedTime(start, end);
    }
    public ValueTask DelayAsync(TimeSpan delay, CancellationToken token) {
        if (delay <= TimeSpan.Zero || delay > TimeSpan.FromHours(24))
            throw new ArgumentOutOfRangeException(nameof(delay));
        return new ValueTask(Task.Delay(delay, time, token));
    }
}
internal sealed class ReplayRows32x24 : IFrameInputRows {
    public FrameError CopyRow(int planeIndex, int y, Span<byte> destination) {
        if (planeIndex != 0 || y < 0 || y >= 24 || destination.Length != 32)
            return FrameError.InvalidArgument;
        for (int x = 0; x < 32; x++)
            destination[x] = (byte)((7 * x + 11 * y) & 255);
        return FrameError.None;
    }
}
internal sealed class ReplayFrameCurrency : ICpuFrameCurrency {
    private readonly FrameKey key;
    private readonly string frameId, sourceRevision, contentHash;
    private int revoked;
    public ReplayFrameCurrency(FrameKey key, FrameReceipt receipt) {
        this.key = key;
        frameId = receipt.FrameId;
        sourceRevision = receipt.SourceRevision;
        contentHash = receipt.ContentHash;
    }
    public bool IsCurrent(FrameKey key, FrameReceipt expected) =>
        Volatile.Read(ref revoked) == 0 && key == this.key &&
        expected.FrameId == frameId && expected.SourceRevision == sourceRevision &&
        expected.ContentHash == contentHash;
    public void Revoke() => Interlocked.Exchange(ref revoked, 1);
}
```

下面所有构造值都是本夹具明确值。固定Guid只用于本次新服务/新Host的软件夹具，不在同一实例重新发布或重放；实际运行新数据使用新身份。sourceConsumer既负责Publish也负责随后绑定读；上游ConsumerLimit.MaxHeldBytes=1024容纳发布同时峰值768+32=800，seg/ocr各持源768；注册holder留sourceConsumer，独立lease归各消费者。

```csharp
TimeProvider timeProvider = TimeProvider.System;
IMonotonicClock clock = new ReplayClock(timeProvider);
TimeSpan timeout = TimeSpan.FromSeconds(10);
TimeSpan observe = TimeSpan.FromSeconds(2);
string sourceConsumer = "im021.31000000000000000000000000000001";
string segConsumer = "im021.41000000000000000000000000000001";
string ocrConsumer = "im021.51000000000000000000000000000001";
var frameBudget = new BudgetLimit(
    DeploymentHardMaxBytes: 4096, ProfileMaxBytes: 1024,
    DeploymentMaxDomainSegments: 128, ProfileMaxDomainSegments: 32,
    DeploymentSourceId: "im021-replay-deployment",
    DeploymentSourceRevision: "v1", ProfileId: "im021-replay-32x24",
    ProfileRevision: "v1");
var resourceLimits = new ResourceLimits(
    FrameBudget: frameBudget, MaxCpuBytes: 4096,
    MaxNativeBytes: 0, MaxGpuBytes: 0, MaxCacheBytes: 0, MaxFrames: 1,
    MaxActiveOperations: 2, MaxQueuedOperations: 0, MaxReceipts: 8194,
    ReceiptRetention: TimeSpan.FromHours(1), DrainTimeout: observe,
    Consumers: [new ConsumerLimit(sourceConsumer, 1024, 1, 1, 0),
        new ConsumerLimit(segConsumer, 1024, 1, 1, 0),
        new ConsumerLimit(ocrConsumer, 1024, 1, 1, 0)]);
var full = new DomainDescriptor(DomainKind.Full, ImmutableArray<DomainRow>.Empty);
var layout = new ManagedFrameLayout(32, 24,
    [new PlaneLayout(PixelScalarKind.UInt8, ByteOrder.LittleEndian, 8, 1,
        PlanePacking.SinglePlane, PlaneRole.Intensity, 0, 32, 32, 768)],
    full, 768);
var key = new FrameKey(new Guid("21000000-0000-0000-0000-000000000001"), 1UL);
var descriptor = new FrameDescriptor(key, layout,
    [new PlaneMetadata("1", 1, 0, ["mono"], full, "")],
    "im021-replay", "fixture-v1", "replay-grid1");
var frameFactory = new FrameServiceFactory();
FrameServiceCreateResult created = frameFactory.Create(resourceLimits,
    new ManagedLayoutValidator(), timeProvider, null);
if (created.Error != FrameError.None || created.Service is null)
    throw new InvalidOperationException("Replay.FrameServiceCreate");
IFrameService service = created.Service;
// 在原源根Owner登记service，下一步才允许Publish。
var rows = new ReplayRows32x24();
var publishRequest = new CopyPublishRequest(
    new Guid("61000000-0000-0000-0000-000000000001"), sourceConsumer,
    descriptor, rows, timeout);
Task<PublishResult> publishTask = service.PublishCopyAsync(
    publishRequest, CancellationToken.None).AsTask();
// 在原源根Owner登记publishTask/rows/ServiceEpoch/RequestId，观察超时也保留。
PublishResult publish = await publishTask.WaitAsync(observe, timeProvider);
if (publish.Receipt.Error != FrameError.None ||
    publish.Receipt.Phase != OperationPhase.Completed ||
    !publish.Receipt.OperationResourcesReleased || publish.Frame is null)
    throw new InvalidOperationException("Replay.PublishNotCompleted");
FrameDescriptor published = publish.Frame;
// 按E.2核实际published全字段，禁止换成预发布descriptor或更晚的其它帧。
var bindReadRequest = new FrameReadRequest(
    new Guid("71000000-0000-0000-0000-000000000001"), sourceConsumer,
    key, [0], new PixelWindow(0, 0, 32, 24), 0,
    BoundaryPolicy.ClipAndMarkInvalid, ReadIntent.ExactSamples, timeout);
Task<ReadResult> bindReadTask = service.ReadAsync(
    bindReadRequest, CancellationToken.None).AsTask();
// 原源根Owner登记bindReadTask/原epoch/Guid，任何非null Slice先接管再核状态。
ReadResult bindRead = await bindReadTask.WaitAsync(observe, timeProvider);
IFrameLease? bindLease = bindRead.Slice;
if (bindRead.Receipt.Error != FrameError.None ||
    bindRead.Receipt.Phase != OperationPhase.Completed ||
    !bindRead.Receipt.OperationResourcesReleased || bindLease is null)
    throw new InvalidOperationException("Replay.ReadNotCompleted");
// 根Owner已接管bindLease；按E.2核全部identity/layout/metadata/allocation。
if (bindLease.TryOpenReadScope(out IFrameReadScope? bindScope) != FrameError.None ||
    bindScope is null)
    throw new InvalidOperationException("Replay.ScopeUnavailable");
byte[] publishedPixels = new byte[768];
using (bindScope) {
    for (int y = 0; y < 24; y++)
        if (bindScope.CopyRow(0, y, publishedPixels.AsSpan(y * 32, 32)) != FrameError.None)
            throw new InvalidOperationException("Replay.CopyRowFailed");
}
Task<ReleaseReceipt> bindReleaseTask = bindLease.ReleaseAsync(observe).AsTask();
// 原源根Owner登记release原Task；不因等候到期丢lease或新Read。
ReleaseReceipt bindRelease = await bindReleaseTask.WaitAsync(observe, timeProvider);
if (bindRelease.Error != FrameError.None || !bindRelease.LeaseClosed ||
    bindRelease.Drain != DrainState.Drained)
    throw new InvalidOperationException("Replay.LeaseNotReturned");
byte[] pixelHeader = Convert.FromHexString(
    "000000144153554e2d494d3032312d504958454c532d563100000020000000180000000100000001000000046d6f6e6f00000001");
string actualRawHash = Convert.ToHexString(SHA256.HashData(publishedPixels)).ToLowerInvariant();
string actualContentHash;
using (IncrementalHash pixelsHash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256)) {
    pixelsHash.AppendData(pixelHeader);
    pixelsHash.AppendData(publishedPixels);
    actualContentHash = Convert.ToHexString(pixelsHash.GetHashAndReset()).ToLowerInvariant();
}
if (actualRawHash != "2f7c22b8a227f529e1a1e65bc101471bff7f1e97a5098a3700532c12f486b375" ||
    actualContentHash != "d4e0c1b74e422b0d757f55e10ff40b0ec5616817e32a5eddda5a0e29018f387a")
    throw new InvalidOperationException("Replay.PixelIdentityMismatch");
```

发布后逐字段核实际Frame等于这个紧密布局/Metadata/key/来源。绑定读取按E.2核回执/lease；scope实际退出后ReleaseAsync(observe)，核LeaseClosed/Drained/Error=None，不要求StorageReleased。只有这些确认成立才执行E.5.2。pixelHeader是本夹具按附录B独立编码的52bytes固定头，不是新增公开codec；图像Spec变更就不能沿用。所有WaitAsync只观察原Task，超时/异常交回既有第7步根监督恢复，不能在catch清空源Owner或继续绑定。原行字节定义覆盖全部x=0..31、y=0..23，无padding；首行hex=`00070e151c232a31383f464d545b626970777e858c939aa1a8afb6bdc4cbd2d9`，末行hex=`fd040b121920272e353c434a51585f666d747b828990979ea5acb3bac1c8cfd6`。768byte原标量SHA256=`2f7c22b8a227f529e1a1e65bc101471bff7f1e97a5098a3700532c12f486b375`；它与包含PIXELS域串/ImageSpec的本地摘要不同，代码核实际发布读回字节再计算本地ContentHash。

ResourceLimits.MaxReceipts=8194覆盖1次Publish、1次绑定Read与两个provider各4096次Acquire关联；本场景只各Start一次，不承诺清旧receipt给新读腾位。MaxCpuBytes限制服务受控payload，Host自有行缓冲/Replay临时读取数组/CLR头不冒充已经由服务计账。每provider源held768+自有scratch32=800bytes，两个Core请求因没有公开物理Id映射可保守各计800；实际源服务同allocation仍只记物理768。

#### E.5.2 两个 source bindings、Receipt 与端口 Options

本地Full域必须有24个inclusive Runs，不能将上游Full的空Rows直接塞成空域；每段(y,0,31)。下面采用已冻结像素/域编码的固定摘要，运行时仍按实际帧复算核对。`published`变量是前一步 `PublishResult.Frame` 的已核实际值，`budget/runtimeOwner`是本节规定的显式入参。两个Receipt全值相同，各Host有自己的provider/源borrow，Currency由源Owner共用（撤销同时停止后续新消费，不能回收正在读的lease）。

```csharp
var spec = new ImageSpec(32, 24, PixelType.UInt8, ["mono"], DomainMode.FullRectangle);
var runBuilder = ImmutableArray.CreateBuilder<DomainRun>(24);
for (int y = 0; y < 24; y++) runBuilder.Add(new DomainRun(y, 0, 31));
var domain = new DomainSnapshot(32, 24, "grid1", runBuilder.ToImmutable(),
    "e50bee113639adcfd2cea8bef1842e5144b8373c217d9137f2b82edcd9738769");
var grid = new GridTrace("grid1", ImmutableArray<GridStep>.Empty);
const string contentHash = "d4e0c1b74e422b0d757f55e10ff40b0ec5616817e32a5eddda5a0e29018f387a";
const string originalHash = "sha256:2f7c22b8a227f529e1a1e65bc101471bff7f1e97a5098a3700532c12f486b375";
var segReceipt = new FrameReceipt("21000000000000000000000000000001", "1",
    contentHash, "replay-registration-v1", "replay-coordinate-v1", spec,
    "grid1", grid, domain);
var ocrReceipt = new FrameReceipt("21000000000000000000000000000001", "1",
    contentHash, "replay-registration-v1", "replay-coordinate-v1", spec,
    "grid1", grid, domain);
var currency = new ReplayFrameCurrency(key, segReceipt);
var segSource = new CpuFrameSourceBinding("seg-source", service, published,
    [0], segReceipt, originalHash, currency);
var ocrSource = new CpuFrameSourceBinding("ocr-source", service, published,
    [0], ocrReceipt, originalHash, currency);
var segProviderOptions = new CpuFrameProviderOptions([segSource], segConsumer,
    MaxConcurrentAcquires: 1, MaxAcquisitions: 4096, MaxScratchBytes: 32,
    ReadTimeout: timeout, DrainObservationLimit: observe);
var ocrProviderOptions = new CpuFrameProviderOptions([ocrSource], ocrConsumer,
    MaxConcurrentAcquires: 1, MaxAcquisitions: 4096, MaxScratchBytes: 32,
    ReadTimeout: timeout, DrainObservationLimit: observe);
var providerFactory = new CpuFrameInputProviderFactory();
ICpuFrameInputProvider segProvider = providerFactory.Create(segProviderOptions, clock);
ICpuFrameInputProvider ocrProvider = providerFactory.Create(ocrProviderOptions, clock);
var runtime = new RuntimeDescriptor("26.05", "im021-asunimage-cpu-v1", "cpu",
    MmxEnabled: true, IntZooming: false, ThreadPolicyRevision: "im021-replay-threads-v1");
var backendOptions = new AsunImageBackendOptions(runtime, 1, observe);
var backendDependencies = new AsunImageBackendDependencies(runtimeOwner, clock);
var backendFactory = new AsunImageBackendFactory();
IAsunImageBackend segBackend = backendFactory.Create(backendOptions, backendDependencies);
IAsunImageBackend ocrBackend = backendFactory.Create(backendOptions, backendDependencies);
var planning = new GraphPlannerDependencies(new GraphLimits(32, 64, 8192));
var segDependencies = new ExecutionDependencies(planning, segProvider, segBackend,
    budget, clock, Observer: null, MaxRequestsPerInstance: 4096);
var ocrDependencies = new ExecutionDependencies(planning, ocrProvider, ocrBackend,
    budget, clock, Observer: null, MaxRequestsPerInstance: 4096);
var executorFactory = new PreprocessingExecutorFactory();
IPreprocessingExecutor segExecutor = executorFactory.Create(segDependencies);
IPreprocessingExecutor ocrExecutor = executorFactory.Create(ocrDependencies);
```

两个backend共用同一个Host RuntimeOwner，分别最多1个session，所以冻结的2个稳定borrow槽足够。本例ThreadPolicyRevision绑定Host启动时已冻结的HALCON内部线程数1及CPU政策，MMX=true、int_zooming=false；模块不设置这些值，不能凭这个record宣称本机实际设置已合格。原Clock对象还要用于后续Wait/Close观察，不能因两个executor而创建两套时钟。Full域规范投影333bytes，PIXELS投影820bytes（52bytes域串/ImageSpec头+768bytes标量）；上述摘要只表示本地编码，不是现场图像真值。

#### E.5.3 两个完整图请求与明确三维预算

本例CancellationToken.None是软件正常路径显式值；取消夹具使用独立新RequestId与实际token，token不进入RequestHash，不能修改旧请求的图/预算后冒用原身份。所有下列构造都是附录A/B公开类型，两个图的节点都有完整绑定和参数，没有未知默认/额外字段。

```csharp
var segGraph = new ProcessingGraph("seg", "im021-graph-v1", "r1",
    [new GraphInput("source", spec, "grid1")], [],
    [new ProcessingNode("select", 1, CompletionRequirement.Required,
        [new InputBinding("image", SourceKind.GraphInput, "source")],
        new SelectChannelParameters("mono")),
     new ProcessingNode("normalize", 1, CompletionRequirement.Required,
        [new InputBinding("image", SourceKind.NodeOutput, "select")],
        new NormalizeParameters(NormalizeMode.FixedRange, 0, 255, 0, 1)),
     new ProcessingNode("smooth", 1, CompletionRequirement.Required,
        [new InputBinding("image", SourceKind.NodeOutput, "normalize")],
        new FilterParameters(FilterKind.Gaussian, null, null, 3, BorderPolicy.Reflect))],
    [new GraphOutput("result", "smooth")]);
var ocrGraph = new ProcessingGraph("ocr", "im021-graph-v1", "r1",
    [new GraphInput("source", spec, "grid1")], [],
    [new ProcessingNode("crop", 1, CompletionRequirement.Required,
        [new InputBinding("image", SourceKind.GraphInput, "source")],
        new CropParameters(2, 3, 16, 12)),
     new ProcessingNode("select", 1, CompletionRequirement.Required,
        [new InputBinding("image", SourceKind.NodeOutput, "crop")],
        new SelectChannelParameters("mono")),
     new ProcessingNode("resize", 1, CompletionRequirement.Required,
        [new InputBinding("image", SourceKind.NodeOutput, "select")],
        new ResizeParameters(32, 24, Interpolation.Bilinear))],
    [new GraphOutput("result", "resize")]);
var planner = new PreprocessingGraphPlannerFactory().Create(planning);
GraphPlanResult segPlan = planner.Plan(segGraph,
    new GraphPlanningOptions("seg-plan-1", CancellationToken.None, observe));
GraphPlanResult ocrPlan = planner.Plan(ocrGraph,
    new GraphPlanningOptions("ocr-plan-1", CancellationToken.None, observe));
const string segGraphHash = "132df5063fcfa6480d72c4639b0a022184a38b49ae56a73402898cbf5f7f1627";
const string ocrGraphHash = "a06089ef61bda044659971c7574be4d8c7bfc969cf9c012901bbc6aa3d85941e";
if (segPlan.Status != PlanStatus.Succeeded || segPlan.GraphHash != segGraphHash ||
    segPlan.GraphSnapshot is null || ocrPlan.Status != PlanStatus.Succeeded ||
    ocrPlan.GraphHash != ocrGraphHash || ocrPlan.GraphSnapshot is null)
    throw new InvalidOperationException("Replay.GraphBindingMismatch");
var segOptions = new ExecutionOptions(timeout, observe,
    MaxManagedBytes: 8L * 1024 * 1024, MaxNativeReservedBytes: 16L * 1024 * 1024,
    MaxRetainedBytes: 32L * 1024 * 1024, PartialOutputPolicy: PartialOutputPolicy.Atomic,
    Mode: ExecutionMode.WholeFrame, Tiles: null, Runtime: runtime,
    CancellationToken: CancellationToken.None);
var ocrOptions = new ExecutionOptions(timeout, observe,
    MaxManagedBytes: 8L * 1024 * 1024, MaxNativeReservedBytes: 16L * 1024 * 1024,
    MaxRetainedBytes: 32L * 1024 * 1024, PartialOutputPolicy: PartialOutputPolicy.Atomic,
    Mode: ExecutionMode.WholeFrame, Tiles: null, Runtime: runtime,
    CancellationToken: CancellationToken.None);
var segRequest = new ExecutionRequest("seg-replay-1", segPlan.GraphSnapshot!,
    segGraphHash, "9e35fc495cc2528efc8cb24d8711a8d724fcdf56d4351f58989257549657779c",
    [new FrameBinding("source", "seg-source", segReceipt)], [], segOptions);
var ocrRequest = new ExecutionRequest("ocr-replay-1", ocrPlan.GraphSnapshot!,
    ocrGraphHash, "945f7148dbea7b28ac93605448d072a88158484f1c9885877f28d82e9ceaebb1",
    [new FrameBinding("source", "ocr-source", ocrReceipt)], [], ocrOptions);
// 各原根组先保存完整request，Start后立即接管Operation再进入下一步。
StartResult segStart = segExecutor.Start(segRequest);
// 在seg原根组登记segStart.Operation；Rejected仍执行已构造组件的独立有限Close。
StartResult ocrStart = ocrExecutor.Start(ocrRequest);
// 在ocr原根组登记ocrStart.Operation；其错误不覆盖或撤销seg原Operation。
```

每个Start返回后立即登记其Operation，按既有第6–8步分别Wait/Take/消费/有限Close；不从这些顺序样例推导“第二Start失败就丢第一个Operation”。分割图规范351bytes、OCR图316bytes；两个请求规范各831bytes，记录字段/nullable/TimeSpan ticks/Runtime bool均沿附录A/B。固定字节摘要由本轮按字段独立复算，实施时Plan与Core必须重算匹配，不能在Host重写已批准codec。分割输出实际有效域full，但Plan.Shape.Spec.DomainMode保持邻域的保守ExplicitMask；OCR为FullRectangle，两个都核真实Domain/SourceReceipt。8/16/32MiB是软件资格预算，不承诺HALCON workspace有硬上界，不作为生产吞吐/峰值通过证据。

本次第一轮按上游逐字段核所有源布局/metadata/Factory/ResourceLimits/ConsumerLimit正值、768+32发布峰值、24个域Runs、两个source bindings及图/request构造；第二轮核任一步失败/取消/迟到时仍用原根Owner/Task、独立consumer及2s清理，检查没有将源服务Native=0误写成后端Native预算0。本机.NET10参考程序集XML已定向核TimeProvider.GetElapsedTime、Task.Delay(TimeSpan,TimeProvider,CancellationToken)、Task<T>.WaitAsync(TimeSpan,TimeProvider)公共重载；只证明签名存在，不代替本例编译或运行。两轮为有界规格自审；只补本节与文档版本，P0/P1/P3/P4接收及P2真实运行/Golden/性能门保持，未新建工程/测试/报告或执行native。

P4同链接线只用上述executor/provider/backend组装ExecutionDependencies，原Clock及Planning三个位置逐字段一致；Editor公开构造仍沿附录D，保存Sink/Viewport/Currency/权限为Host既有端口，预览先登记根Owner、Acquire迟到留原control/operation，关窗有限Close不替代持久根监督。动态语言/保存Unknown/查询规则不变，不另加模块Runtime开关/保存或语言入口；本轮未扩展WPF审查。

P2未来唯一有限验证入口如下，每条外层进程上限180s、Exe用例总截止点120s（本轮未执行）：

```powershell
dotnet build src/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.AsunImage/Asun.Modules.ImagePreprocessing.AsunImage.csproj -c Release --disable-build-servers
dotnet run --project tests/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.AsunImage.Tests/Asun.Modules.ImagePreprocessing.AsunImage.Tests.csproj -c Release --no-launch-profile
```

Exe先以受控FrameService/Clock/RuntimeOwner闩锁验证E.6映射/生命周期，再在同入口直接引用既定AsunImage运行实际导入/节点/导出及双Host断言。两组结果分别记录，未运行真实组为NotEvaluated/非零，不将模拟通过改写真实资格。实际消费者Profile未知只阻对应数值/性能/业务验收，不改本附录已定的API/Owner/映射。

### E.6 两轮定向自审与实施断言

| 断言 | 输入与可判定期望 |
|---|---|
| PP-P2M01 帧/通道 | CPU Interleaved RGB源索引与局部plane分开，CopyRows逻辑R/G/B每行长度为Width×scalarBytes，源padding不进hash；源通道次序改变即Receipt/Expected不匹配，不猜BGR |
| PP-P2M02 域/容量 | EndXExclusive转本地inclusive正确；Full空Rows展开，Empty不变Full，通道域不同拒；Allocations.Bytes大于窗口像素时按整容量占账，释放本lease不等StorageReleased |
| PP-P2M03 来源/hash | 错原Key/epoch、伪本地ContentHash、读中Currency失效均不交付；原SourceRevision/摘要/坐标引用追溯保留；源域外原字节进输入hash，导出零填后独立派生hash |
| PP-P2M04 runtime | 两同descriptor稳定borrow共存；外部写者无法约束则Begin拒；Begin取消后晚borrow归原session；session真释放前槽/原Task/预算不撤，不通过前后值相等假稳定 |
| PP-P2M05 复制/输出 | gen_image1真实返回后才解pin；export含copy_image/native图/托管输出同时峰值；输出独立hash/子Owner/托管borrow在backend关闭后仍读，关闭原源不改已产出像素 |
| PP-P2R01 异常/迟到 | 工厂无副作用；Read/CopyRow/native闩锁阻塞后Wait/Close到期保原Task/lease/scope/charge；解除闩锁后逐项真归还，未知上游查询不重Read，不提前scope.Dispose/归还destination |
| PP-P2R02 关闭/竞争 | CopyRows并发拒且不写目的缓冲；Close先停新scope而等在用复制；Take/Close只一次交接；分割Close不使OCR失效，LeaseClosed/Drained/StorageReleased分开断言 |
| PP-P2R03 根Owner/限额 | Factory前槽满零启动；构造第N步失败仍关闭已取得对象；业务失败+清理失败分别保存；Released=false离栈后仍可查/关；移交无接收确认不撤槽；MaxAcquisitions满不新读 |

第一轮从Host构造推至双消费者：核公开工厂/不可变Options/原Clock、上游不存在的hash和currency、plane展平/实际域/实际容量、输入摘要及派生copy/hash/子预算。第二轮按取消/迟到/并发/关闭/失败反向走查：核构造前根槽、原Task与上游epoch/Guid、scope真退出、有限cleanup、业务/清理两轴、独立消费者持有及移交确认。这是规格自审与未来验收断言，不是C#测试通过。2026-10-11 P2该增量的确定指导内容已获主控限定接收；真实HALCON/稳定RuntimeOwner/CPU接线/原生资源/Golden/运行/性能仍PreparationIncomplete，不标纯Core Ready；P0/P1/P3和P4保存限定接收保持。本次仅同步接收结论，不重审、不改API/算法/fixture或旧P0向量，未执行产品编译、native或性能验证。


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

## 附录 F：当前完整范围的实施收口（2026-10-11）

本附录补当前架构内尚不够确定的编辑、显示挂接、草稿codec、候选生成及容量/验收细节；复用§3–9和附录A–E，不重做已接收算法/API或向量。P0/P1/P3、P4保存及P2确定指导的历史接收保持，新增文档语义由本永久原会话审核验证；文档闭合与运行资格分开。

### F.1 全能力覆盖与驻留/分块边界

| 已批准能力/消费者 | 唯一执行路径与不适用条件 |
|---|---|
| 分割、OCR/读码、字符/阻焊/胶体/外观的派生输入 | §3/8全部11节点，§11/E.5两个独立Host；这些消费者只取图像/域/来源，不从模块取缺陷分类/读码文本/质量放行。制程物理阈值不进入Core |
| 通道与颜色 | Select/Linear/Binary/ColorTransform；显式通道键和已冻结线性空间矩阵。RGB/BGR、曝光、偏振不猜；非线性色空间、gamma、去Bayer/配准在上游，不因UI名叫“颜色”自动增加路线 |
| 照明/背景补偿 | FlatField的image/reference及显式Gain/Offset/MinAbsDenominator；暗场/白场可由已批准Binary+FlatField组合，保持多帧同格/配准闭包。没有参考、可靠注册或分母界则拒，不能从本图静默拟合光照背景 |
| 滤波/锐化/归一化 | §7/8 real→Mean/Gaussian/Sharpen/Normalize，冻结Reflect/支撑域/全域统计；常量PerFrame不返回看似正常图。未登记的median/bilateral/去噪AI不在本版，不由工程师换“更好”算子 |
| 几何与限制域 | Crop/Resize/DomainLimit；只改派生格/域，坐标来源保持。Resize有洞拒，未经实际采样资格不授计量/同格擦拭资格 |
| 大图分块 | 本版Tiled是**已驻留完整节点矩阵上的有界逐节点计算**，累计halo/core裁切/域及统计屏障按§7；不承诺磁盘流式或超过源能力仍能无界拼全图。CPU源单buffer C=min(1GiB,Array.MaxLength)，超C不能通过Tiled绕过；真超驻留能力由上游image-frame Tiles及另行批准的流式消费切片处理，本版不暗造tile-source端口 |
| 自动参数与离线调参 | P3单源/无Domains/单Required可变节点/有限显式候选；评分Owner由消费者提供。多源FlatField可手动执行，首版Advice没有多帧样本合同，不伪造样本或偷偷固定当前参考。建议仅草稿，未评分不推荐 |
| 编辑、预览、保存/恢复 | §10、附录D、F.2–F.6；全部计算同Core，无UI可调用Plan/Executor/Advisor。控件保存的是图草稿，不保存原像素或授发布权；持久Sink是Host显式IO能力 |

每完整逻辑单通道CPU暂存/托管输出容量B=checked(W*H*scalarBytes)须≤Array.MaxLength且≤请求预算；CPU源还受C约束。各channel完整矩阵、同时活分支、copy_image副本、导出托管副本、域/tuple、tile/halo及统计同时峰值按§7/E.4累计，不能只验证单tile能分配。tile网格`ceil(W/CoreWidth)*ceil(H/CoreHeight)`用checked整数，整个请求节点执行块之和≤MaxTiles；尾core截到本节点尺寸，halo不把Crop外像素带回。示例：单源UInt8 32768²=1GiB只通过源容器界检查，不证明分配成功；转real单矩阵=4GiB，超过本版单byte[]暂存/输出界，执行前BudgetExceeded，不将它写成可运行超大图。16384² UInt8源256MiB/real单通道1GiB在容器数学域内，但需要全部同时活预算与实测；不因分块缩小本页冻结的完整驻留语义。后端工作区未知仍SoftObserved，不宣称hard RSS。

分块与整图等价性按同runtime/同方法、同完整有效域核：整数点/选择/Crop必须精确；real不使用普适客户容差，数值对照由F.7的软件Profile与实际HALCON参考给出，失败不得自动切回整图冒成功。输入源hash/原lease/字节在全部路径不变。

### F.2 字段缓冲、图编辑与模板/推荐

控件只用一个活动深冻结ProcessingGraph和一个私有编辑缓冲；GraphRevision由控件每次成功草稿事务生成`Guid.NewGuid().ToString("N")`，LoadDraft/保存恢复保传入原revision，语言/显示变化不改revision。Generation为非负long，初始0、每次Load/来源/有效编辑checked+1，到long.MaxValue停止新编辑/预览并保原Owner关闭，不回绕。节点新ID固定`n`+Guid.N，输出键/来源键不随语言改变。

缓冲按(NodeId,FieldPath)保RawText、ParsedValue、上一有效值、错误键；单文本≤1024 UTF16单元、集合元素≤§3范围、总缓冲≤1MiB，超界保上一文本并提示限额。Int只接受不带小数的十进制符号整数；double使用当前文化的十进制分隔符、允许指数、禁止千分位/NaN/Infinity，Invariant原值只用于冻结/codec；小数文本完整解析后转换有限binary64、−0规范+0。矩阵/Terms/Offsets采用有编号行的单元格，不通过逗号分隔文本猜分隔符；长度由记录字段决定。不适用nullable字段UI禁用且提交为null，不保隐藏旧值。

Enter/失焦提交整个节点参数缓冲，Plan通过才交换活动图并增加一次undo快照；非法中间文本保持EditingInvalid、活动有效图不变，预览/保存/Advice/Apply禁用，取消字段恢复上一有效值。批量编辑只对同NodeParameters类型同FieldPath且共同有效域内的选中节点执行一次原子事务，全图Plan任一错则不改任何节点；共同不同值显示“多个值”，不当0。撤销/重做替换完整草稿参数值与选择并生成新revision/Generation（不回滚已提交保存/源事实，不复用历史保存revision），清空相应非法缓冲并取消旧预览/建议；100步/16MiB上限按规范图bytes+缓冲实际估计先到限移除最旧已知步，不删除未知保存记录。

连线采用显式端口列表和源选择器，无自由字符串/任意表达式：image可选图输入或其它节点，mask仅已声明DomainInput；先按附录A完整端口集建立候选，再Plan校环/格/类型/Required依赖。重复/未知端口不自动修复。删除节点先列出所有下游/声明输出，操作者可取消或明确删除依赖闭包；后一动作同时移除闭包输出及不再使用的源/域声明，显示变更清单，Plan成功才交换。结果无输出时保非法编辑候选，要求显式添加输出，不生成虚构输出。重排仅显示；执行拓扑仍唯一P0算法。新增节点必须显式接齐端口并指明哪个输出替换/新增，未接齐保编辑候选，不静默旁路或让孤立节点通过。

以下是“新增节点”**可见草稿模板**，不成为执行默认/批准配方。用户确认后才写活动图，所有字段仍显式；上下界/单位全部引用§3.2，不建立第二张有效域表。

| 节点 | 模板值/适用前提 | 自动候选生成规则（单次仅改一个字段） |
|---|---|---|
| SelectChannel | 当前输入第一个明确通道键，页面显示名称/来源，不猜R；要求确认 | 依原通道顺序，各键一个完整Parameters，最多16 |
| LinearCombine | N为已选端口数；Terms第一项1其它0，Offset0，保各端口源 | 选中一个Terms槽或Offset后，取用户显式有限值列表；不自动铺笛卡尔网格 |
| BinaryArithmetic | 明示Operation=Add、Scale1、Offset0；Divide选定后MinAbsDenominator空且禁提交，须给分母单位下的可信值 | Operation/Scale/Offset/分母界由单字段显式候选列表生成；不推测epsilon |
| ColorTransform | 已选InputKeys原顺序，输出同名/同空间的方阵单位矩阵，Offsets0；空间Key必填 | 选矩阵单元/Offset槽后使用显式值列表，其它元素完整保留；不搜索颜色空间 |
| FlatField | Gain1/Offset0，reference显式同格帧，MinAbsDenominator必填 | Gain/Offset/分母界单字段显式列表；首版Advice不接多源，UI仅允许正式手动图配置 |
| Mean | KernelWidth=Height=3且各<输入对应尺寸2倍，Border=Reflect，MaskSize=null；尺寸不符需编辑 | 可选宽或高之一的[1,3,5,7,9,11]，先向用户显示符合尺寸/§3界的列表，确认后生成完整候选；不暗改另一轴 |
| Gaussian | MaskSize3、两个Kernel字段null、Reflect，满足尺寸界 | [3,5,7,9,11]与合法尺寸交集，确认后生成，各候选完整保Border/其它字段 |
| Sharpen | MaskWidth/Height3，Factor0、Reflect，满足尺寸界；0是可见不增强模板 | Factor显式列表，或某一核轴[3,5,7,9,11]合法交集；不承诺锐化提升效果 |
| Normalize | 默认可见FixedRange；UInt8输入0..255、UInt16为0..65535、Int16为−32768..32767；Float32两输入界空待填。Output0..1；改PerFrame显式清InputMin/Max | 仅用户选中的InputMin/Max/OutputMin/Max单字段显式候选；全节点范围仍须严格有序。PerFrame是另一显式方法，不暗入候选 |
| Crop/Resize | Crop=(0,0,当前W,H)，Resize=(当前W,H,NearestNeighbor)，都为可见恒等模板 | 尺寸/插值只接受显式完整候选，不用默认搜索牺牲细字/细桥 |
| DomainLimit | mask从已声明同格域列表明确选择，缺域无模板 | 首版无Domains Advice不适用；手动限制域按§3/7执行 |

候选生成在开始评估前完整展示(字段、单位、原值、候选值/完整Parameters、数量、预算)，最多64；重复参数图hash按P3拒绝，不自动去重改变用户意图。候选Key固定`c0001`起顺序编号，不影响算法hash。任一候选Plan错误在派像素前拒，显示具体候选及FieldPath；不隐式丢掉失败项后声称完成搜索。超预算不截断样本或候选。

P3最小无UI装配用E.5同源/provider/backend/budget/clock与`new ParameterAdvisorFactory().Create(new AdviceDependencies(execution, new PreprocessingExecutorFactory(), scorer))`；scorer非null仅当ScoreSpec非null且已绑定可信样本标注。参考软件双Host：分割以segGraph的smooth节点生成Gaussian3/5两个候选、OCR以ocrGraph的resize节点生成显式NearestNeighbor/Bilinear两个候选，Sample分别是各自单个FrameBinding、Key=`s1`/LabelRevision=`label-v1`/LabelHash为可信标注摘要/Required；两个Advice实例各串行、共用预算，Source/InputGrid/hash同E.5。SampleSetHash及Advice投影沿附录C逐字段计算，不拿E.5执行RequestHash顶替。软件scorer提供已登记的损失表，分割c0001=0.2/c0002=0.4、OCR两候选均0.1，回显实际GraphHash/SourceHash/Spec.Revision；断言Rank分别1/2及1/1。这是评分端口协调oracle，不声称高斯或OCR业务正确。真实Loss/Metric/单位由消费者评分Owner提供，不从图清晰度猜。

软件协调夹具的标注替身精确为无BOM UTF8串`ASUN-IM021-SEG-LABEL-V1`与`ASUN-IM021-OCR-LABEL-V1`，两LabelHash分别`b6092872d6a9a70fe31c7ddd6520320ab0bc9c46745bbecb7b0ed264dd66722f`/`56942e7c7840bdc1972134f6a21e9a0c110abdd36a2d4aa076969f6dfe051ccd`；它们只验证绑定，不能当图像标注。ScoreSpec固定new("score-fixture-v1","loss-table-v1","ratio","protocol-only")，Scorer预绑定本Host Sample/LabelHash及由Planner生成的两候选GraphHash→上述损失表，错绑定返回Failed/Conflict，不按候选名猜评分。AdviceRequest分别RequestId=`advice-seg-1`/`advice-ocr-1`，BaseGraph/BaseGraphHash沿E.5，MutableNodeId=`smooth`/`resize`，OutputKey=`result`，Samples为本Host唯一s1，Candidates按c0001/c0002完整参数，ExecutionTemplate沿本HostsegOptions/ocrOptions、Timeout10s/DrainTimeout2s、CancellationToken.None；取消组显式新请求/token。这样Host只需按附录C编码SampleSetHash，无待选标注/评分常量；真实调用必须替换为消费者可信标注/ScoreSpec。

Apply必须原Advisor完整结果/当前Binding匹配且权限仍有效；推荐样本或Profile已改即AdviceStale，重新评估由显式新请求触发。没有scorer/标注只可执行诊断，不产生自动推荐。本模块不存在尚待开发者选的“最佳参数”算法。

### F.3 WPF 实际挂接与有界 CPU 呈现

附录D的IPreprocessingViewport显示借用语义保持；补可选WPF挂接及CPU展示构造，namespace仍`Asun.Modules.ImagePreprocessing.Wpf`，P4挂接API增量0.4.2（不改0.4.1保存协议）。以下是公开签名规格，无方法体，不声称已编译：

```csharp
public interface IPreprocessingViewportView : IPreprocessingViewport {
    System.Windows.FrameworkElement View { get; }
    void SetCulture(string cultureName);
}
public sealed record CpuViewportOptions(int MaxDisplayEdge, long MaxDisplayBytes,
    TimeSpan ReadTimeout, TimeSpan DrainObservationLimit);
public sealed class CpuPreprocessingViewport : IPreprocessingViewportView {
    public CpuPreprocessingViewport(System.Windows.Threading.Dispatcher dispatcher,
        IMonotonicClock clock, CpuViewportOptions options);
    public System.Windows.FrameworkElement View { get; }
    public void SetCulture(string cultureName);
    public ValueTask<CloseReceipt> SetContentAsync(IFrameBorrow content,
        ViewportSelection selection, TimeSpan waitLimit, CancellationToken token);
    public ValueTask<CloseReceipt> ClearAsync(TimeSpan waitLimit);
}
```

EditorDependencies.Original/Derived均须实现这个接口，View非null、不同实例、同Editor Dispatcher、未有其它逻辑/可视父节点；否则构造ArgumentException且零后台任务/借用。Editor将两View各置独立ContentControl（内部稳定名OriginalView/DerivedView），关闭先Clear真归还再移除父关系；Host仍拥有端口对象，Editor不关闭共享FrameService或全局viewport。控件使用ControlTemplate的Grid/Dock区域，OnApplyTemplate只重挂已有唯一View/绑定，不重新Create executor/Acquire/Save；重套模板先撤旧父节点，失败保原根Owner恢复。无Hidden Window初始化。

实际Host可用viewport模块的已批准Adapter实现该接口；本模块不复制其3D/ROI/原值查询/授权服务。独立Editor的首版同WPF DLL提供上述**公开CpuPreprocessingViewport**，Host直接构造，不靠内部类/隐藏factory。构造必须在给定Dispatcher线程，null参数/非法范围抛标准参数异常且零Task/像素读取，MaxDisplayEdge为1..2048、MaxDisplayBytes为1..64MiB、ReadTimeout为1ms..24h、DrainObservationLimit/waitLimit为1ms..10min；要求checked(4L*MaxDisplayEdge*MaxDisplayEdge+32768L*4+256L*8)≤MaxDisplayBytes，否则ArgumentException。ReadTimeout从SetContent进入计单调期限，两遍采样不续期；本次观察至多min(waitLimit,DrainObservationLimit)，不推迟读取期限，退出任务仍原Owner持有。最多1在途更新，重叠入口不队列叠加，返回Released=false/ConcurrencyViolation且不读取/保留该被拒的新content；Clear可停在途读取且独立有限观察。本例MaxDisplayEdge2048/MaxDisplayBytes20MiB/ReadTimeout10s/DrainObservationLimit2s。View为带Image/Canvas/状态TextBlock的Grid，两个独立实例由两个ContentControl容纳，不共享Image控件或可变Bitmap。它只读IFrameBorrow，不加入Core/AsunImage依赖，不承担视觉算法或质量判断。

SetContent/Clear/SetCulture均从该Dispatcher线程进入，跨线程抛InvalidOperationException且零副作用；异步入口在取得字段快照后立即让出UI，不同步等复制。SetCulture按Editor相同文化校验/逐键回退，只刷新本View的状态/通道/范围/图例文字，不读像素、不改选通道/显示epoch/图hash；Editor.SetCulture必须转发两端口，构造初始zh-CN。每次获准SetContent或Clear将端口私有displayEpoch checked+1（初始0），到long.MaxValue拒新SetContent为BudgetExceeded；此时Clear不再加1，只置内容无效/取消并排空，不能因overflow阻恢复。语言/平移不递增。借用Receipt/selection在准入时冻结核对，SourceKey/OutputKey沿Editor选中来源，CoordinateRevision/DomainHash须等content.Receipt；错配Rejected诊断且不读。权限/Editor Generation由Editor守卫：撤权或换代必须取消原显示并Clear使epoch失效，端口本身不能从selection推测权限或读取Editor私有Generation。私有通道选择器在读取/清理期间禁用；空闲时只从当前Receipt通道列表选一个合法索引，递增同一epoch并用同一仍被借用的content启动一次上述有界呈现，端口原根Task/预算持续跟踪，不能在Editor Clear后再启动或自行Close该borrow；无像素原值查询旁路。

显示算法是有界CPU标量解码/屏幕打包，不替代§8视觉处理：选择一个明确逻辑通道（初次0，选择器变更只是展示，界面常驻通道Key），由Receipt.Spec取得UInt8/UInt16/Int16/Float32小端标量。D=min(1,MaxDisplayEdge/max(W,H))按double计算，displayW=max(1,floor(W*D))、displayH=max(1,floor(H*D))；输出BGRA字节数checked(displayW*displayH*4)≤MaxDisplayBytes，最多4194304个显示像素。每显示像素最近源中心索引`x=min(W−1,floor((dx+0.5)*W/displayW))`，y同式；只为所需唯一源行调用`CopyRowsAsync(plane,y,1,rowMemory,readToken)`，rowMemory长度精确W*scalarBytes，返回written必须恰等，否则BackendError；同一行Memory直到原Task真退出不可复用/归还。不复制全原图；最大源行128KiB计入20MiB总限。本版固定两遍采样（无整幅浮点采样缓存）：首遍同域求展示range/直方图所需边界，次遍按该范围写BGRA及累计bin计数，预占BGRA+一行+256个long计数；两遍输入Receipt/IsCurrent不一致整批Stale，不读最新帧续补。最大行调用数2*MaxDisplayEdge，有取消/期限检查，受原根Task槽/Editor总预算；有效点写B=G=R=byte、A=255。

UInt8固定0..255、UInt16固定0..65535、Int16固定−32768..32767显示；Float32按**本次采样且有效**点的有限min/max显示，标签“显示范围（采样）”，不是Normalize节点或全图计量。常值有效Float32显示中灰128；没有有效采样点显示透明+“没有可显示的有效像素”，不报图像PASS。byte=`round(255*clamp((v−min)/(max−min),0,1),MidpointRounding.AwayFromZero)`只用于显示副本，中间减/除按double避免Float32跨度溢出；域外像素BGRA全0，背景棋盘标无效。计算只解释当前DomainSnapshot.Runs，不能按包围框当Full；float域内非有限错误NumericInvalid，失败不提交半Bitmap，不能改透明掩盖坏值。原矩阵/域/hash不修改，PresentationOnly不进任何算法输出。单通道显式选择不把16通道压成未经声明的伪RGB。

背景任务完整写完BGRA后，在当前displayEpoch/选通道/冻结selection仍匹配且content.IsCurrent时Dispatcher一次提交：`BitmapSource.Create(w,h,96,96,PixelFormats.Bgra32,null,bytes,checked(w*4))`→Freeze→Image.Source，Canvas只画十字/无效域提示，无原生句柄。Bitmap只在所属UI线程使用；完成/失败都保原Task直到复制与Dispatcher回调真实退出。SetContent先停止旧显示任务，新旧借用分别保留；返回CloseReceipt.Released=true仅旧内容显示读取/引用已退出，新内容仍按附录D由Editor保borrow直到Clear。Clear首先使epoch失效/取消读取，Dispatcher清除Image.Source/Canvas/位图引用并等本端口原读取Task退出，绝不Dispose调用者borrow；若Dispatcher提交未退出，仍Released=false并保原根Task。没有读取任务的Clear也须真的完成UI清引用才Released=true。Clear不永久关闭端口，正常可再次SetContent；Editor已关闭不能借此重开命令。

20MiB只限制本次受控BGRA+一行+256个long，不包含旧Bitmap和WPF新像素副本。令P=displayW*displayH*4，换图前Editor/Host另预留旧Bitmap payload Pold+新Bitmap payload P；本次托管P与上述两项同时计账，最坏每viewport为Pold+2P+128KiB+2048，两端口及源/result/undo/保存合并，额度不足在开始读取/分配前拒。旧引用在新提交前仍活，失败保旧图，不提前减旧账；新BGRA在Create/原Task退出且引用解除后才能减账，位图替换后的逻辑减账不等于GC/native RSS已降低。端口原Task/外部不可量化WPF缓存另按RetainedBytesExact=false观测并计Host峰值；不声称hard WPF堆上界，也不能用20MiB×2冒总峰值。

平移/缩放用WPF MatrixTransform绑定同一冻结图像矩形；fitScale=min(可用宽DIP/displayW,可用高DIP/displayH)，区域零尺寸时不计算变换；缩放z是相对fitScale的1/64..64，初始/双击/Home为z=1且居中，鼠标滚轮每完整120刻度以指针为锚点乘/除1.2、限制z，左键拖动按DIP平移。按键仅图像获得焦点时作用，文本字段不抢键；每次View尺寸/DPI/选图变化重建屏幕映射，DIP≠原像素。十字仅显示最近有效采样像素索引与源通道，不给物理单位或未验证Resize逆坐标。内置CPU两端口由Editor私有导航协调器接收(epoch、源中心行/列、行/列各自源像素每DIP、交互序号)值事件，仅当前活动预览的两端口epoch各自匹配且GridTrace相等或全部步骤为已验证Crop时应用另一侧，Crop逐步加/减偏移，写回抑制同序号事件循环；两端口epoch无需数值相等。目标z超界则禁本次联动并提示独立视图，不偷偷夹值后称同尺度；离开对应有效域只清十字不夹到别的像素。Resize路径缺采样资格只并列独立视图，禁用联动/擦拭并提示原因。公共挂接接口不许诺外部Adapter导航能力，外部Adapter默认独立视图，其已批准导航桥另由Host接入，不能反射View内部找API。不要凭图像等尺寸开启同格。

直方图为所选展示通道的**采样有效点**256bin投影，标“采样直方图”；bin固定等于本节生成的灰度byte，UInt8即原值，常值Float32进bin128，其它按显示公式量化，256个long初始0、每有效采样一次checked+1。缺有效点呈空表，不把全0计数画成有效分布；它不替代image-quality原量/全图分布。端点只显示计数，不称实际裁切/饱和原因。ChartControl每显示epoch至多一次数据刷新，语言刷新只换图例；节点耗时来源NodeReceipt，不从UI渲染时间伪造算法耗时。超预算/取消不提交半屏，保旧预览并标旧revision及失败原因。

### F.4 DevExpress 组合、三语与操作状态

本机dxdocs MCP及匹配WPF技能未提供；复用§17官方25.2研究，补按本机`DevExpress 25.2/Components/Bin/NetCore`官方XML定向核PropertyGridControl.SelectedObject/PropertyDefinitions/ShowProperties、PropertyDefinitionBase.Path/Header/IsReadOnly、PropertyDefinition.CellTemplate、TreeListView.KeyFieldName/ParentFieldName、BarItem.SuperTip、SuperTip.Items、DockLayoutManager.SaveLayoutToStream/RestoreLayoutFromStream。查API资料不做组件安装/许可证或版本适配准入；使用现有25.2.3。P4不得调用未登记的“自动画DAG”或多选批量API。

确定组合：DockLayoutManager的中心DocumentGroup含原/派生两个LayoutPanel；工具BarButtonItem绑定私有ICommand，取消/预览/保存或查询常驻，不能藏到Flyout。节点TreeListView用私有显示行RowKey/ParentRowKey：根行是拓扑节点，多父连接作为引用子行，选择引用仍选真实NodeId；KeyFieldName=`RowKey`、ParentFieldName=`ParentRowKey`，此树仅投影，不改图DAG。PropertyGridControl.SelectedObject绑定私有EditBuffer对象，PropertyDefinitions显式列出当前节点适用字段，Path指缓冲string/enum属性，Header本地化，CellTemplate使用已安装TextEdit/ComboBoxEdit及本地FieldError提示；不自动反射Native/Owner或把record直接双向写。只读图/schema/method/runtime移到可折叠说明区；不可改的高级字段IsReadOnly=true。PropertyGridControl.ShowProperties=`DevExpress.Xpf.PropertyGrid.ShowPropertiesMode.WithPropertyDefinitions`只展示明确字段（本机官方XML已核枚举），GridControl另展示错误和候选，不把ShowProperties误挂GridControl。

布局以实际可用工作区计算中央图像占比，不照DIP总宽假称合格：默认两图等宽，中间8DIP；侧栏默认240/280DIP但不同时占用超40%面积，高DPI时左/右互斥显示，选参数自动收节点侧栏；专注模式两侧和下诊断都折叠、中央≥80%。主间距8DIP、字段垂直间距4DIP、常用触点≥28DIP、层级字号12/14/18DIP，使用Host当前主题/字体/高对比度，禁强改全局主题。选中线/当前节点轻描边，状态图标+文字，不仅红绿；异步更新不做跨页动画。Dock布局仅Host可信用户配置读写流≤64KiB，恢复失败重置本控件默认布局且保草稿/源/保存Identity，不从任意文件反序列化，不让布局含图参数/Owner。

全部文字在WPF本地资源表或Host localization投影内，用stable key和参数，SetCulture刷新Header/Command/SuperTip/错误/状态、保RawText不重解析已在编辑的文本；下次提交仍按该字段开始编辑时文化解析，避免1,5切语言变15。Core仍仅返回Code/FieldPath。扩展culture缺项逐键回退zh-CN并给Host缺键诊断，不显示裸ResourceKey或native异常。以下表为该控件资源清单，slash分隔的平行名称按相同顺序一一映射，不将键名显示给操作者。

| 键/用途 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title/Original/Derived/Nodes/Parameters/Diagnostics/Advice | 图像预处理/原图/派生图/节点/参数/诊断/参数建议 | 影像前處理/原圖/衍生影像/節點/參數/診斷/參數建議 | Image preprocessing/Original/Derived/Nodes/Parameters/Diagnostics/Parameter suggestions |
| Preview/Cancel/Save/Query/Undo/Redo/Restore/Focus/Add/Delete/Connect | 预览/取消/保存草稿/查询保存状态/撤销/重做/恢复布局/专注图像/添加节点/删除节点/连接端口 | 預覽/取消/儲存草稿/查詢儲存狀態/復原/重做/還原配置/專注影像/新增節點/刪除節點/連接埠 | Preview/Cancel/Save draft/Check save status/Undo/Redo/Reset layout/Focus image/Add node/Delete node/Connect ports |
| Evaluate/Apply/Compare/Fit/Sync/Channel/Multiple | 评估候选/应用到草稿/并列比较/适配窗口/联动视图/显示通道/多个值 | 評估候選/套用至草稿/並排比較/適合視窗/連動檢視/顯示通道/多個值 | Evaluate candidates/Apply to draft/Compare side by side/Fit to window/Link views/Display channel/Multiple values |
| Select/Linear/Binary/Color/Flat/Filter/Sharpen/Normalize/Crop/Resize/Domain | 选择通道/线性组合/双图运算/颜色矩阵/平场补偿/邻域滤波/锐化/归一化/裁剪/缩放/限制有效域 | 選擇通道/線性組合/雙影像運算/色彩矩陣/平場補償/鄰域濾波/銳化/正規化/裁切/縮放/限制有效域 | Select channel/Linear combination/Image arithmetic/Color matrix/Flat-field correction/Neighborhood filter/Sharpen/Normalize/Crop/Resize/Limit valid domain |
| ChannelKey/Terms/Offset/Operation/Scale/MinAbsDenominator/Gain | 通道键/权重/偏移/运算/倍率/分母绝对值下限/增益 | 通道鍵/權重/偏移/運算/倍率/分母絕對值下限/增益 | Channel key/Weights/Offset/Operation/Scale/Minimum absolute denominator/Gain |
| InputKeys/OutputKeys/MatrixRowMajor/Offsets/InputSpace/OutputSpace | 输入通道/输出通道/颜色矩阵/通道偏移/输入空间/输出空间 | 輸入通道/輸出通道/色彩矩陣/通道偏移/輸入空間/輸出空間 | Input channels/Output channels/Color matrix/Channel offsets/Input space/Output space |
| Kind/KernelWidth/KernelHeight/MaskSize/Border/MaskWidth/MaskHeight/Factor | 滤波方式/核宽/核高/高斯核大小/边界/锐化窗宽/锐化窗高/锐化系数 | 濾波方式/核寬/核高/高斯核大小/邊界/銳化窗寬/銳化窗高/銳化係數 | Filter type/Kernel width/Kernel height/Gaussian mask size/Boundary/Sharpen window width/Sharpen window height/Sharpen factor |
| Mode/InputMin/InputMax/OutputMin/OutputMax | 归一化方式/输入下限/输入上限/输出下限/输出上限 | 正規化方式/輸入下限/輸入上限/輸出下限/輸出上限 | Normalization/Input minimum/Input maximum/Output minimum/Output maximum |
| Row/Column/Width/Height/TargetWidth/TargetHeight/Interpolation | 起始行/起始列/宽/高/目标宽/目标高/插值 | 起始行/起始列/寬/高/目標寬/目標高/內插 | Start row/Start column/Width/Height/Target width/Target height/Interpolation |
| Enum operators/filter/modes | 加/减/乘/除/均值/高斯/镜像/固定范围/逐图范围/最近邻/双线性 | 加/減/乘/除/平均/高斯/鏡射/固定範圍/逐影像範圍/最近鄰/雙線性 | Add/Subtract/Multiply/Divide/Mean/Gaussian/Reflect/Fixed range/Per-frame range/Nearest neighbor/Bilinear |
| Required/Optional/Eligible/Ineligible/Unranked/Tie | 必需/允许部分输出/可评分/不可评分/未排名/并列 | 必要/允許部分輸出/可評分/不可評分/未排名/並列 | Required/Optional for partial output/Eligible/Ineligible/Unranked/Tied |
| State Ready/Invalid/Planning/Previewing/Stale/Rejected/Draining/Closed | 就绪/参数未完成/正在检查图/正在预览/预览已过期/未准入/等待资源归还/已关闭 | 就緒/參數未完成/正在檢查圖/正在預覽/預覽已過期/未准入/等待資源歸還/已關閉 | Ready/Incomplete parameters/Checking graph/Previewing/Preview is stale/Not admitted/Waiting for resources/Closed |
| Save Saved/NotSaved/Unknown/Rejected | 已保存/已确认未保存/保存状态未知/未准入 | 已儲存/已確認未儲存/儲存狀態未知/未准入 | Saved/Confirmed not saved/Save status unknown/Not admitted |
| Evidence Raw/Derived/Presentation | 原值选择/派生数据/仅供显示 | 原值選擇/衍生資料/僅供顯示 | Raw selection/Derived data/Display only |
| Source/Revision/Graph/Node/Field/Status/Time/Range/Valid/Invalid/Loss/Rank | 来源/修订/处理图/节点/字段/状态/耗时/范围/有效像素/无效像素/损失/排名 | 來源/修訂/處理圖/節點/欄位/狀態/耗時/範圍/有效像素/無效像素/損失/排名 | Source/Revision/Graph/Node/Field/Status/Elapsed/Range/Valid pixels/Invalid pixels/Loss/Rank |
| Unit pixel/ms/ratio/raw/sample | 像素/毫秒/比值/原值单位/采样 | 像素/毫秒/比值/原值單位/取樣 | pixels/ms/ratio/raw value units/sampled |
| DisplayRange/Histogram/EmptyDisplay/MissingStep | 显示范围（采样）/采样直方图/没有可显示的有效像素/该步骤图未生成 | 顯示範圍（取樣）/取樣直方圖/沒有可顯示的有效像素/此步驟影像未產生 | Display range (sampled)/Sampled histogram/No valid pixels to display/Step image was not generated |
| Zoom/Linked/Independent | 缩放/已联动/独立视图 | 縮放/已連動/獨立檢視 | Zoom/Linked/Separate views |
| Disable Edit/Preview/Save/Apply | 无编辑权限/无预览权限/无保存权限/无应用建议权限 | 無編輯權限/無預覽權限/無儲存權限/無套用建議權限 | Edit permission required/Preview permission required/Save permission required/Apply permission required |
| CropOutOfBounds | 裁剪范围超出图像。修改位置或尺寸。 | 裁切範圍超出影像。修改位置或尺寸。 | Crop is outside the image. Change its position or size. |
| SaveOutcomeUnknown | 保存状态未知。查询原请求后再保存。 | 儲存狀態未知。查詢原請求後再儲存。 | Save status is unknown. Check the original request before saving. |
| NoMapping | 坐标映射未验证。使用独立视图。 | 座標對應尚未驗證。使用獨立檢視。 | Coordinate mapping is unverified. Use separate views. |
| DeleteConfirm | 删除此节点及其依赖？共{0}个节点。 | 刪除此節點及其相依項？共{0}個節點。 | Delete this node and its dependents? {0} nodes. |
| Limit/NoScore/StaleAdvice | 已达限额。减少本次内容。/缺少评分依据。仅显示诊断。/建议已过期。重新评估后再应用。 | 已達限額。減少本次內容。/缺少評分依據。僅顯示診斷。/建議已過期。重新評估後再套用。 | Limit reached. Reduce this request./Scoring evidence is missing. Showing diagnostics only./Suggestions are stale. Evaluate again before applying. |

FieldPath上的row/column中文简体/繁体都按图像行/列术语，不借表格列标题混用。其余稳定错误Code闭包按以下分组映射短文案+本地化Field/Node占位，原Code保诊断详情不直显英文枚举：输入类(InputNull/InvalidIdentifier/DuplicateNodeId/UnknownField/GraphRevisionMismatch/ReferenceMissing/PortTypeMismatch/ParameterOutOfRange/UnsupportedParameter/InputShapeMismatch/DraftInvalid)→“输入不符合要求。检查{字段}。”/“輸入不符合要求。檢查{欄位}。”/“Invalid input. Check {field}.”；图依赖(GraphCycle/OptionalDependency)→“节点依赖无效。修改连接。”/“節點相依無效。修改連接。”/“Invalid node dependencies. Change the connections.”；来源与域(RegistrationMissing/DomainInvalid/OutputDomainEmpty/SourceInvalidated/SourceMissing/RevisionUnavailable/LabelUnavailable)→“来源或有效域不可用。重新选择可信来源。”/“來源或有效域無法使用。重新選擇可信來源。”/“Source or valid domain unavailable. Select a trusted source.”；数值(NumericInvalid/ConstantRange/ScoreInvalid)→“数值不适用。检查范围或评分输入。”/“數值不適用。檢查範圍或評分輸入。”/“Values are not applicable. Check ranges or scoring inputs.”；预算BudgetExceeded用Limit；Conflict/ConcurrencyViolation→“请求冲突。查询原请求后再操作。”/“請求衝突。查詢原請求後再操作。”/“Request conflict. Check the original request before continuing.”；Cancelled/TimedOut→“请求已取消。等待资源归还。”或“执行期限已到。等待资源归还。”/对应“請求已取消/執行期限已到。等待資源歸還。”/“Request cancelled/Execution deadline reached. Waiting for resources.”；RuntimeDrift/BackendError/NativeDrainUnknown/ReleaseFailed/InternalError/PersistenceCorrupt/ObserverUnavailable→“执行或恢复未确认。保留原请求并查看诊断。”/“執行或復原尚未確認。保留原請求並查看診斷。”/“Execution or recovery is unconfirmed. Keep the original request and check diagnostics.”；Closed/NotFound→“对象已关闭或请求不存在。检查原身份。”/“物件已關閉或請求不存在。檢查原識別。”/“Object closed or request not found. Check the original identity.”；PermissionDenied用对应权限文案；SaveIdentityMismatch/SaveReceiptMismatch→“保存记录不匹配。按原身份核对。”/“儲存記錄不符。依原識別核對。”/“Save record mismatch. Check the original identity.”；AdviceStale用StaleAdvice。每Code必须命中一种已定映射，新增Code时同步资源，不回退native.Message。

SuperTip按Command Header+动作/范围+禁用原因/恢复+快捷键，复用上述资源而不另建第二套文案；值/单位和原请求Identity在状态栏/详情可复制，敏感主体不泄露到未授权屏幕。UIA AutomationId固定`Preprocess.Command.{key}`、`Preprocess.Node.{NodeId}`、`Preprocess.Field.{NodeId}.{FieldPath}`、Original/Derived/SaveState，语言不改ID。删除必须明确确认，Ctrl+S Unknown期间转原Query；F5在字段非法/无权限/关闭时不发请求，Esc不取消别Host。Preview/Save/Advice各自状态轴显示，保存Unknown不掩盖图仍可编辑/预览，Preview Failed不把已保存状态清掉。

### F.5 独立编辑器双 Host 的实际组装与关闭

未来P4.Tests用net10.0-windows BCL Exe、`[STAThread]`入口创建WPF Application/Dispatcher，在一个固定1920×1080物理验证视口内按当前OS DPI/WorkArea限定实际Window；记录任务栏、边框、标题栏及状态栏后的可用内容区，不把Window.Width=1920DIP冒充物理基线。两个Editor依次在同固定可用视口验证，不改变显示设置或跑第二分辨率。Host A用分割segGraph/segSource/segDependencies；Host B用OCR对应值，来源/budget/clock沿E.5，组件与root任务槽独立，Dispatcher可同一。原有全根3组为源/seg/ocr；每Editor各最多1预览operation、1Advice、1保存、1查询、每viewport1显示Task，64个总原Task槽不足先拒，不无限按generation派任务。

组合过程精确为：各根槽先强持Frame/Backend/Runtime/Budget/Clock与该Host的IEditorDraftSink；`var viewOptions = new CpuViewportOptions(2048,20L*1024*1024,TimeSpan.FromSeconds(10),TimeSpan.FromSeconds(2))`→分别`new CpuPreprocessingViewport(Dispatcher.CurrentDispatcher,clock,viewOptions)`构造original/derived两实例→按需创建本Host专用advisor→`new EditorDependencies(planning,new PreprocessingExecutorFactory(),segDependencies,segProvider,advisor,original,derived,sink)`→`new EditorOptions(planning.Limits,segOptions,128L*1024*1024,TimeSpan.FromSeconds(2))`→`new PreprocessingEditor(dependencies,options,new EditorPermissions(true,true,true,true))`，B改为ocr对象；每次构造成功立即登记根槽，任一步失败清理已取得对象，剩余项不启动。128MiB是该软件Editor总保留限，受共享Host更低上限；把显示新旧位图、图/undo、保存/查询快照及源/result/late Owner同时计入，不把它额外加到共享Core额度宣称RSS保证。该限包含F.3换图并存账，不改变附录E请求自身三项预算。真实Host明确配置自己的预算，不照抄该测试值。

Editor构造校验Execution.Frames与Frames为同provider对象、三个Planning.Limits逐字段一致、预览Runtime/Clock与backend绑定同一冻结值，Original/Derived不同且同Dispatcher、Sink.Context固定；缺权时UI可构造只读但不发写/预览。附录D的预算一致指同一分配同时服从各适用上限，不要求显示/undo也塞进Executor的32MiB保留额，或把128MiB冒充Core可用额度；Executor仍用E.5共享16/32/64MiB三维预算。软件Host另为两Editor预设合计256MiB UI/草稿逻辑保留池，每Editor≤128MiB，实际与Executor交叠的源/result字节在Host联合峰值只计一次，未知WPF开销另测。Editor在调用viewport前按F.3保守预占像素账，直到原Task/UI引用真退才释放；自定义Adapter未知额必须报告非精确，不授硬限保证。随后SetCulture→LoadDraft(segGraph/ocrGraph)→SetSourceSelection(new EditorSource([本Host FrameBinding],[],"replay-source-set-v1"))，等本代Plan小更新完成→把Editor挂Host ContentControl→显式RequestPreviewAsync。Load/Set均须Host UI线程，setter不读像素/持久化。

保存软件Host A使用Context=("seg-draft-scope",本Host Guid.N,可信测试主体"replay-engineer",64)，B用ocr scope和另一个OriginHostEpoch；IEditorDraftSink由测试Host实现附录D/F.6语义、有限字典最多64、可控原Task/提交闩锁，真实Host用相同codec及提交门适配持久Store。测试Sink不可报告耐久/重启资格，按钮显示“草稿”且不发布。无Advisor时CanApplyAdvice=false且Eval/Apply给原因，不用空实现伪运行；有Advisor时Host显式准备F.2的AdviceRequest/可信ScoreSpec再调用EvaluateAdviceAsync，UI不猜标注来源。Host订阅四类值事件不持像素/Owner，任何回调异常分别记诊断，不破坏清理。

该软件预算只准两个同时活Executor根reservation，故每Host的Preview/Advice调用顺序明确互斥，上一operation真实排空/输出释放后才启动另一项；A/B仍可各自一个并行，保存/查询独立但共用其Editor总保留限。故意重叠的反例必须得到BudgetExceeded/有界拒绝，不能临时调大共享限额或偷偷取消别Host来让它通过。真实Host需要更多计算并发时按同一公开预算端口显式配置，不改模块语义。

Close顺序：禁新命令/撤挂接输入→Editor.Close(2s)取消其预览/Advice并Clear两个viewport/Close自有borrow/Sink identity→根监督器保原Task/原控件及未决Owner继续QuerySavedDraft/Close，不因Unloaded强退→控件实际显示引用全退后移除View父关系/Host.Content→专用advisor.Close→executor/backend/provider按E.5归还；外部已Take输出独立关闭。每步有限且独立，原业务失败与cleanup诊断分列，Released=false的根槽只可带确认移交。B保持预览/保存时关闭A，不关闭共享FrameService/Runtime/Budget；源Owner最后关闭。重挂/模板更新/切语言不能重新Save/Start原请求或丢Unknown身份。

### F.6 草稿恢复 codec 与 Host Sink 的精确责任

模块Core保持无IO/无公开decoder；Host接受草稿档案/恢复记录时必须使用本节确定的纯编解码算法，再调LoadDraft。该算法是本模块图格式的唯一映射，不让各Host任选JSON/序列化器改变身份；实现落在宿主适配代码或本模块既有P4.Tests私有codec，图领域规则由本指导定义。没有新增产品数据库/文件Store或通用持久模块。实际介质、目录/连接/凭证、事务耐久和保留期由Host持久Store Owner提供，是显式能力输入；用它完成附录D NoCommit，不把临时文件存在/数据库无行冒证明。

冻结档案格式`im021-draft-archive-v1`：按附录A长度前缀/大端编码依次写字符串`ASUN-IM021-DRAFT-V1`→DraftStoreContext完整四字段(StoreScopeKey/OriginHostEpoch/PrincipalKey/MaxSaveRequests int32)→RequestId→GraphId→GraphRevision→GraphHash→CanonicalGraphBytes(uint32长度+完整字节)→ArchiveHash字符串。ArchiveHash=SHA256前述从域串至完整图bytes的全部前缀，小写64hex；hash不含自身/StoreRevision/NoCommit/时刻/显示文化/像素。图hash仍SHA256(CanonicalGraphBytes)，绝不将档案hash当GraphHash或RequestHash。最大档案字节数=checked(GraphLimits.MaxCanonicalBytes+2048)，同时受Editor总保留/Host IO上限；字符串在分配前依附录D/§3严格字符域/长度验证，declared length/count超实际剩余立即PersistenceCorrupt，不靠先读巨数组再拒。

解码固定顺序：核完整有限输入/域标记/字段length→核Context/原Identity及当前可信授权→定位末尾ArchiveHash且无尾字节并重算前缀→核图byte长度和GraphHash→按附录A的**精确逆映射**重建ProcessingGraph→由唯一Planner重新Plan→比较规范bytes逐字节/GraphHash/GraphId/Revision一致后才LoadDraft，错误保当前草稿不替换。图逆映射：按A的Inputs/Domains/拓扑Nodes/Outputs字段顺序读record；每Parameters先读1..11 discriminator再按对应record顺序/nullable0或1/enum/int/double解；拒非法enum、NaN/Inf、负零非规范字节、未知schema/method/类、重复/乱序规范容器、default/null数组或超GraphLimits。不从Plan推测缺字段/默认参数；若输入可Plan但重编码字节不同仍拒，不自动迁移旧档。恢复的源帧不在档案内，Host另显式SetSourceSelection并核ContentHash/域/坐标，再可预览；原图丢失不会把草稿显示成已可执行。

档案仅保存完整图草稿和原保存Identity，StoreRevision与NoCommitRevision是Sink真实事务回执，不是本codec计算的hash。Sink适配器的内部唯一记录按附录D身份键持有：完整Identity/ArchiveHash/档案或其不可变可验证引用、知识态Pending/Committed/NoCommit/Unknown、StoreRevision或NoCommitRevision、原执行/清理Task关联。登记与最终决定在可信持久提交门内CAS：Pending→Committed或Pending/未登记→NoCommit，二者互斥，既有终态不改；同键档案hash变Conflict。主张Committed的保存图及回执必须同提交原子可见，Query不可把裸object上传成功当Saved。Query若需NoCommit，先核停止原请求权并隔离所有旧写者，持久封锁成功才NotFound；隔离/事实未知只Unknown。回执丢失沿原记录Query，绝不另发Save、另换GraphRevision或解封NoCommit。

Host若使用storage-database，消费其[§6.1–6.3/7公开Runtime、RegisteredTransactionRequest、RegisteredReadRequest、原Operation/资源恢复](../storage-database/DEVELOPMENT-GUIDE.md#61-字段有效域和注册)：档案是Owner payload内部不透明字节，域Owner启动前注册不可变codec/catalog及精确CLR type/有界参数化CAS语句；Host自己的scope/store/generation/current principal绑定技术identity，不能直接把DraftSaveIdentity伪装OperationIdentity。技术事务Committed还需本Sink原Identity/StoreRevision结果codec匹配才Found；技术NotFound不能变本地NoCommit。这里没有把数据库SQL/权限/根协调责任偷放Core；本模块不提供数据库适配包，任一选定产品Host的真实存储注册/Schema/权限/耐久测试由该Host Owner显式完成，缺该能力只禁该Host保存/恢复，不阻图/预览/Advice设计或实现。

软件固定档案向量复用§11已有197bytes图，Context=("replay-draft","81000000000000000000000000000001","replay-engineer",64)，RequestId="91000000000000000000000000000001"，GraphId=g1/Revision=r1/GraphHash沿附录A。F.6.1记录本轮独立复算的完整档案长度/hash；实施应构造上述完整字段，不读取研究脚本或聊天才能恢复。旧JSON仅是Host输入媒介，必须先严格映射/Plan再编码本格式，不接受JsonSerializer默认多态、忽略未知属性或浮点字符串。架构范围不含通用JSON导入器/任意版本迁移；未知档案版本按RevisionUnavailable保留原件，Host显式迁移任务另门。

### F.6.1 固定草稿档案字节向量

前缀415bytes；ArchiveHash=`aa25e18e22a33ccb4724915993d160f473ef3a635d66f6ac44a5b347f7775407`；末尾为uint32长度64及该ASCII hash，完整档案483bytes；完整档案SHA256=`0e77e113bb739639440407986013c631ba69d13dbc38549bec5993d9617f6212`。后者仅用于核对夹具，不另作保存Identity。完整hex如下（换行不入字节）：

```text
000000134153554e2d494d3032312d44524146542d56310000000c7265706c61792d64726166740000002038313030303030303030303030303030303030303030303030303030303030310000000f7265706c61792d656e67696e656572000000400000002039313030303030303030303030303030303030303030303030303030303030310000000267310000000272310000004061373934346437316637666665353937393632333939376330623765623336656134613366336635313532396530626261326462666535326635383766396639000000c5000000134153554e2d494d3032312d47524150482d56310000000267310000000e696d3032312d67726170682d76310000000272310000000100000006736f7572636500000020000000180000000100000001000000046d6f6e6f0000000100000005677269643100000000000000010000000463726f7000000001000000010000000100000005696d6167650000000100000006736f7572636500000009000000000000000000000001000000010000000100000006726573756c740000000463726f700000004061613235653138653232613333636362343732343931353939336431363066343733656633613633356436366636616334346135623334376637373735343037
```

### F.7 正确性、UI/恢复与性能验收补充

既有PP-A/B/P4S/P2M/P2R及有效向量复用，草稿档案精确值见F.6.1；以下是补缺口对应必需断言，不另建测试套件/工程/过程报告：

| 用例 | 可判定输入/期望与失败恢复 |
|---|---|
| PP-F01 编辑/连接 | RawText=`-`/不完整指数/本地小数/NaN/1025字符→保原图/非法字段；切语言不把1,5解析为15。连接形成环/错端口/错格→不交换活动图；删除闭包需确认，取消字节不变；成功多字段只一revision/undo |
| PP-F02 模板/建议 | UInt8 Fixed模板0/255、Float32无未知输入界；Divide分母界空不发执行。Gaussian尺寸不合法候选预检失败；两候选/两评分oracle排名按F.2，平手不选冠军。标注/源域/hash/ScoreSpec/runtime变则Apply拒，无评分只诊断 |
| PP-F03 UI挂接/双Host | 同View双父/跨Dispatcher/原派生同View构造拒且零Acquire；重复OnApplyTemplate不重Start/Save；A关闭时B原请求/显示仍有效。普通/专注中央面积分别≥60%/80%，三语长文字不截关键值/单位，Tab/F5/Esc/Ctrl+S/UIA与权限按F.4 |
| PP-F04 显示保真 | UInt8 [0,255]显示[0,255]，Int16端点映射一致；Float32常值采样显示128/bin128且原值/hash不变，域内非有限失败；域外透明不授有效；Resize无映射资格禁同步；最大2048边/20MiB/2*2048行调用，直方图2048bytes及旧新位图均计账，差1byte预算前拒；切语言两View同步且无像素重读；超限/过期不提交半Bitmap |
| PP-F05 codec/恢复 | 完整档案编码解码再Plan字节一致；截断/尾字节/错hash/重复ID/非规范负零/未知schema/超长度/default集合均拒且保原草稿。外部new/with身份变不能沿原保存键；档案正确不证明原来源尚可读 |
| PP-F06 迟到/权限 | Save已提交回执迟到Found可IoDrained=false，关闭不撤草稿事实；NoCommit持久封锁后晚Save不提交；查询/viewport/Dispatcher原Task卡住后2s观察到期仍根持有，业务与cleanup两轴，未证归还不释放额度 |
| PP-F07 容量/块 | 单buffer C/C+1边界在上游读取前拒超界；32768² UInt8→real导出超过单数组界拒，不靠tile假通过。Gaussian3→Mean5累计halo3、PerFrame一次全域统计、Crop后Reflect不偷读原裁外，tile core全覆盖无叠/漏 |

软件数值Golden的目的仅验证冻结公式/边界：UInt8 200乘200输出Float32 40000、10−20输出−10；Fixed 0..255→0..1的0/255精确端点，128参考float32(128/255)，可用float32 1ULP以内误差作为该算例断言；小分母阈值恰等保留/更小剔除，域必须精确。Mean常量1、Gaussian常量1（full有效/Reflect）、Factor0锐化原值及恒等Crop/Resize作为基础oracle；真实算子近端点/高动态/脉冲的浮点误差和采样要用固定HALCON26.05参考结果/Runtime Golden，不能将软件1ULP泛化为全部算法/客户容差。Tiled对WholeFrame实际域必须精确一致，数值容差若未由方法Golden冻结不得给通过。

Benchmark负载冻结矩阵：§11的32×24正确性夹具；1024²/4096²/16384²且实际能驻留的UInt8/UInt16/Float32单/三通道；full/单洞/多段域、单链/双分支/PerFrame屏障、core256/512/1024与全图、单/双Host、取消位置Acquire/Import/Execute/Export/viewport/Save。超能力点只测确定拒绝不分配；不强行跑所有超过实际预算的组合。记录原图/图/方法/runtime/Profile/域hash与软件版本，热身/样本量/最低有效数由消费者Profile沿DEV-GOV-010冻结；无目标只NotEvaluated，不用预设次数制造达标。

§14测点新增字段解析/Plan/UI小更新、sample row复制/显示打包/Dispatcher提交、图/档案codec、Sink登记/提交/Query/NoCommit及IO真实归还；分列UI可观察返回与真资源排空。功能硬判据是非法输入零副作用、原hash不变、合法域/来源/结果匹配、原Task根有界、无码隐藏降级及PP反例全部成立；时延/峰值/误接受拒绝/细结构损失目标Owner分别是消费者/产品性能Owner、消费者视觉方法Owner，不由模块编造。UI通知≤10Hz、布局占比、内存/节点/候选/缓冲上限是本页设计约束，实施须实测，不因常量已写就算通过。

P4未来验证命令：`dotnet build src/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.Wpf/Asun.Modules.ImagePreprocessing.Wpf.csproj -c Release --disable-build-servers`，`dotnet run --project tests/Modules/image-preprocessing/Asun.Modules.ImagePreprocessing.Wpf.Tests/Asun.Modules.ImagePreprocessing.Wpf.Tests.csproj -c Release --no-launch-profile`。沿E.5外层180s/用例总120s，WPF真Dispatcher与1920×1080实际视口，软件Sink/Scorer模拟项单列，不冒真实存储/HALCON/三语母语/产品运行资格。模块当前没有授权建这些工程或执行native，当前结果仅文档准备。
