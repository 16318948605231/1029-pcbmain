# ROI 几何与编辑独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`CoreSlice-01, Interaction-01, Codec-01, Spatial-01`

- 模块：`IM-024` / `roi-geometry`（中文：ROI 几何与编辑）
- 历史职责映射：`PKG-020`；限定 LF 数学参考：[DEV-VIS-024](../../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection%20Target%20Selection开发指导.md)
- 指导版本：`0.4.4-prep`；日期：2026-10-11
- 状态：`DesignReview` / `Prep`；2026-10-11主控接收：`CoreSlice-01 / Interaction-01 / Codec-01 / Spatial-01` 软件切片六项文档规格为 `ModuleCoreImplementationReady`。`HALCON-01 / WPF-01` 接线与Owner恢复指导限定内容接收，真实适配/运行/客户用途仍为 `PreparationIncomplete / NotReady`。
- 本轮全范围自审：`0.4.4-prep` 可决定的软件设计欠账已关闭，结论与剩余Owner见§15.3；不升级实际运行/生产资格。
- 适用基线：C# / .NET 10；目标 HALCON 26.05；平台视觉调用经 `ImageLibDotNet`
- 规划消费者：算法工具、计量工具、检测宿主
- 本文是模块唯一实施指导。附录 A 的 `Module API Contract v0.3` 按切片定义本模块唯一 API 权威；产品 Schema、HALCON/持久化/UI 适配器仍是后续切片。当前不表示已实现、已构建、性能通过或已取得实机资格。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/roi-geometry/Asun.Modules.RoiGeometry.Core/Asun.Modules.RoiGeometry.Core.csproj`；namespace：`Asun.Modules.RoiGeometry`。预定测试工程：`tests/Modules/roi-geometry/Asun.Modules.RoiGeometry.Core.Tests/Asun.Modules.RoiGeometry.Core.Tests.csproj`。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前状态：`CoreSlice-01` 及 `Interaction-01 / Codec-01 / Spatial-01` 纯软件切片已由主控按 DEV-GOV-010 §3.1 接收为 `ModuleCoreImplementationReady`（仅六项文档规格准备）。创建工程及代码实现仍须后续明确派发与权威仓库/代码快照绑定；本绑定不是已实现、已构建、集成或生产资格通过声明。

### CoreSlice-01 首片范围

`CoreSlice-01` 是可在无 UI、无产品 Shell、无数据库、无设备 SDK、无 HALCON/AsunImage 的最小宿主中独立实现和测试的纯 Core。它只拥有进程内、内存态的几何和编辑事实，`RetentionScope` 固定为 `ProcessLocalEphemeral`，`Durable` 固定为 `false`；进程退出或实例引用丢失后不保证保留；Drain/Dispose后同一仍存活实例保留有界请求/回执墓碑及最后只读Snapshot用于回查，不提供跨进程恢复。首片没有 `Save`、`Load`、`Commit` 或数据库写权，也不产生质量、目标、设备或发布事实。

首片包含：附录 A.1 的不可变二维几何/文档值对象、结构/有限数/严格环拓扑校验、typed 创建/替换/删除/仿射/多项原子命令、内存态会话、CAS 修订与 Undo/Redo、可取消 Preview、查询和排空。同步纯计算不调用 HALCON；所有处理入口使用相同校验和预算。仿射只用于数学值对象编辑，图像/Region/XLD 派生使用视觉适配切片；不以托管首片替代 HALCON 视觉算法。

首片明确排除：HALCON Region/XLD 布尔、`ImageLibDotNet` 适配、Region/XLD 转换、native object/lease、文件/数据库/持久提交、`ICommitPort` 实现、WPF/DevExpress 控件、Pointer/HitTest/UI 适配、目标/制程/质量/设备语义。上述能力只能作为后续端口或切片准入项；本文已固定的HALCON路线按后续真实类型/Golden/资源/性能验收准入，不得标记 `Ready`。

## 1. 目标与边界

### 1.1 模块负责

模块提供与制程无关的二维 ROI 几何、编辑和显式三维点域选择能力：

1. 以稳定身份表示点、线段、圆、圆弧、轴对齐矩形、旋转矩形、椭圆、折线和带外环/洞/组件的多边形。
2. 对几何做结构、数值、拓扑、坐标域和资源上限校验。
3. 在首片执行托管的平移、旋转、缩放、镜像和仿射变换；布尔、Region/XLD 转换及误差路线属于后续切片。
4. 创建进程内编辑草稿，记录可逆命令，支持预览、撤销/重做和差异；不提交生产事实。
5. 以同步纯计算入口和异步可取消入口提供同一套校验与结果语义；持久化、HALCON/AsunImage 和 WPF 控件通过后续端口接入。

### 1.2 模块禁止负责

- 不创建、拥有或解释 `TargetId`、位号、焊盘、孔、针号、板件、工单、面别业务或任何制程对象。
- 不决定搜索区/测量区/排除区的工艺含义，不计算缺陷、质量合格、机判、人判、复判或最终放行。
- 不持有配方、程序发布指针、私有数据库表、权限事实、报告事实或设备 SDK 句柄。
- 不因 ROI 为空、无图、转换失败或支持域不足而返回 PASS；未知观察保持 Unknown/DrainUnknown，拒绝执行用 Rejected 与具体错误；不使用未定义的 Blocked 状态。
- 不把屏幕缩放、镜像、旋转、行号、图形顺序、显示文字或旧控件 `ShapeIndex` 当作业务身份。
- 不通过隐藏窗口初始化核心，不复制 `Asun_ROI` 内部 Session/Recipe Store/抓边算法，不扫描或修改 AsunImage 内部。

调用方拥有调用顺序、目标关联、方法/阈值、产品流程、质量处置、程序发布、复判和设备副作用。模块输出只能作为候选几何事实或编辑事务回执。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.RoiGeometry.Core`、`Asun.Modules.RoiGeometry.Serialization`、`Asun.Modules.RoiGeometry.RoiSnapshotValidator` 与 `Asun.Modules.RoiGeometry.AsunImage` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.RoiGeometry.Wpf`（编辑控件）可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1.1 首片的托管几何、校验、变换与草稿事务是这条门禁的天然验证面——它在无 WPF、无 HALCON、无 AsunImage 的宿主中即可完整运行。

**Blazor/Web 宿主中的 ROI 编辑与查询**：Web 端需要"选中一个 ROI 并查其几何/拓扑事实"时，服务端调用本模块 Core 的同步纯计算入口取得强类型几何、校验结论与拓扑信息，再投影到浏览器。约束：
- 浏览器端只负责交互与渲染，**不重算几何、不自建 Shape 模型、不判断拓扑合法性**；几何事实只有 Core 一个来源
- 持久化由宿主通过 `RoiGeometry.Serialization` 的独立 Codec 桥完成（只读写字节，不做文件/数据库 IO）；Web 端不直接读写存储，也不依赖 Core 内部草稿状态跨请求存活
- 编辑草稿（§1.1 第 4 项的可逆命令、撤销/重做、预览）是**会话内事务**，其存活范围由宿主会话决定；不得为支持 Web 而把草稿状态变成跨会话的全局可变状态
- ROI 的业务身份（§1.2 禁止项）仍由上游拥有；Web 端不得由几何反推目标/位号

**AI 推理 Tiling 适配**：本模块是 `ai-inference` 分块推理的**ROI 裁切来源**。[IM-047 ai-inference](../ai-inference/DEVELOPMENT-GUIDE.md) §2.3B.4（Tiling）已冻结"推理侧只处理已切好的 tile 张量，不自行裁切大图"，且数据流为"`roi-geometry` 模块产出 ROI 坐标列表 → `image-frame` 模块产出 tile 张量（按 ROI 裁切 + resize）"，本模块据此明确：
- 推理链路的裁切区域必须来自本模块的已校验 ROI 快照（带 revision），推理侧只消费裁切结果，不自行决定裁切范围
- 裁切结果的坐标与 `EffectiveDomain` 必须随 tile 字节一起传递，供 `coordinate-geometry` 做推理结果的逆变换（见 [IM-007](../coordinate-geometry/DEVELOPMENT-GUIDE.md) §1A）
- 本模块不实现 `RequestTileAsync`、不持有 tile 租约、不参与分块编排；它只提供裁切几何与域语义
- ROI 为空、支撑域不足或校验失败时，本模块产出**明确拒绝/Unknown**（§1.2），不得以"裁不出就取全图"兜底

**HALCON 备选交叉验证适用性**：本模块是 2D 视觉链中双跑 CI 的**几何语义落点**，且是"同一几何在两路实现下必须给出同一答案"的守门人。约束：
- 首片托管变换（平移、旋转、缩放、镜像、仿射）与 HALCON `Region`/XLD 转换路线在**同一 Golden 数据集**双跑：逐顶点坐标、包围盒、面积/周长、拓扑（洞数、连通性、组件数）、坐标域逐项比对，差值超容差即 CI 失败并产出差异报告
- **已知的必然差异，不得抹平**：HALCON 的 `region_features`、`shape_trans`、XLD 转换使用其自身的数值容差、采样与量化策略（例如 `smallest_rectangle2` 的取向约定、`contour_area` 的多边形近似语义）。因此双跑的门禁是**顶点级坐标与拓扑结构**，**不是**面积/周长这类已聚合量的逐位相等；面积/周长差异登记为诊断并标注"聚合/近似实现差异"
- 容差按坐标域冻结（像素域与归一化域用不同容差），不得用单一 eps 覆盖全部 Shape 类型；圆形/椭圆/圆弧的弧长与多边形近似在两路必然不同，须显式区分"参数一致"与"离散结果一致"
- §1.2 的"不因 ROI 为空而返回 PASS"在双跑中同样成立：两路都拒绝时是**一致通过**，不是被掩盖的失败；一路拒绝一路接受必须判失败并定位到路由/契约差异
- HALCON 仍是生产路线；托管路线只作交叉验证与降级保险，不作发布依据，不引入 OpenCV 平行生产算法。**第三方 oracle 覆盖有限**：本仓固定 OpenCV 快照（commit `a0cda081f8d769f40ab2f4904738b4787b44d07c`）只含 `geometry`/`imgproc`/`stitching`，**不含** XLD/Region 转换与多边形布尔（见 §16.4 与 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)），故本模块双跑为"HALCON vs 自建托管参照"两路；OpenCV `geometry` 的读取已用于确认"面积/周长是依赖点序与深度的聚合量"，支撑上面的强门禁/仅诊断分层，不作发布依据

## 2. 架构、Owner 与发布单元

```text
算法工具 / 计量工具 / 检测宿主
        | 只通过候选 Contract 和端口组合
RoiGeometry.Core（无 UI、无产品 VM）
        | 后续端口（不属于首片实现）
HALCON/AsunImage、旧 ROI 控件、宿主提交（独立 Codec 只读写字节）
```

发布单元按 §8.3 分为 Core、Serialization、AsunImage 和可选 Wpf；宿主持久桥由宿主发布：

| 单元 | 内容 | 约束 |
|---|---|---|
| `RoiGeometry.Core` | 首片强类型几何、校验、托管变换、内存态草稿、撤销、预览、排空 | 不引用 WPF、DevExpress、产品 VM、数据库、设备 SDK、HALCON 或 AsunImage |
| `RoiGeometry.Wpf`（可选） | 独立编辑控件和投影适配 | 只调用 Core；不拥有目标、权限、发布和质量事实 |
| `RoiGeometry.Serialization` | 独立 Codec 字节转换 | 仅引用 Core，不进行文件/数据库 IO |
| `RoiGeometry.AsunImage` | ImageLibDotNet 视觉适配 | 资源和线程边界明确，不泄漏 native 句柄 |
| 宿主 adapter（模块外） | 旧格式导入、viewport/持久事务桥 | 按公开端口接入，不把旧产品运行库作为 Core 依赖 |

模块 Owner 只写本目录和未来独立工程。正式 Contract、State、Owner、权限和持久化提交点由原权威 Owner 串行冻结；不得在本模块再造第二套 Schema 或状态机。

## 3. 几何、坐标与文档模型

本节给字段语义，唯一声明在附录 A；不得凭正文生成另一个 DTO。`GeometrySnapshot` 是带 revision 的完整 ROI 文档，不是单个 Shape。一个会话拥有一个文档写入权威；Snapshot、RoiNode、Shape 和 ImmutableArray 内容不可变。Core 不读取 Frame Registry，全套 Frame 定义由宿主显式注入。

### 3.1 单位、身份与有效域

- ID 是 1～128 字符的 ASCII `[A-Za-z0-9._:-]`，Ordinal 比较，不 trim/大小写合并；Revision 为非负 `long`，加一溢出拒绝。OperationId 在同一会话内唯一，不能用屏幕索引、颜色、名称、TargetId 替代。
- `Point2(X,Y)` 数学列向量；Pixel 文档明确 `X=column,Y=row`、整数位于像素中心。二维Snapshot的Pixel仅配ColumnRowPixelCenters、物理仅配RightHandedPhysicalXY；空间点块/Profile用RightHandedPhysicalXYZ，不能把XYZ Frame当二维Snapshot。物理文档的轴/手性由Frame给出；UI 的 Y 向下不是自动换基。Length 与文档 Unit 同单位，Angle 和 Sweep 为 rad，缩放无量纲。仅 `Pixel/Millimeter/Micrometer`，未知单位只读，不能改标签完成换算。
- Affine2D 六数顺序 `(M11,M12,Tx,M21,M22,Ty)`，`x'=M11*x+M12*y+Tx`、`y'=M21*x+M22*y+Ty`；组合 `A*L` 先 L 后 A。矩阵最后一行为 `(0,0,1)`；本节唯一缩放2-norm条件门与逆舍入门适用于所有使用者，奇异/超过Profile条件数/结果非有限拒绝，不以平均尺度代替。
- 所有数值有限；Profile 显式给坐标绝对界、正尺寸下界、最大条件数、拓扑工作量、输出/历史/在途预算和有限 deadline。示例数值只为软件反例，不是物理允差。精度声明区分输入实际 binary64、坐标舍入上界、曲线近似误差及像素离散化；`AnalyticVector` 不声称恢复真实连续精度。
- 原设计域 D、已有数据域 F、观察有效支持 V 分开；缺口 `D−V` 不得改成 Exclude、零值或从必检分母删除。Core 的无图几何合法性不代表图像可观测或机台通过。

Source可为null（无图纯编辑），不代表观测完整。RoiSupportDomains只携带宿主给出的D/F/V同Frame/Unit严格Polygon：NotProvided三域必须null；Partial/Complete三域均非null，V包含于F、F包含于D（边界可重合）；Complete还必须D=V。Core做数值/拓扑/完整边界段分类与材料点包含核对，不授生产资格，不只测包围框、不需构造D−V布尔新对象。支持域顶点/环/候选对计入同Profile总预算。Source.Revision>=0、Sha256为64位小写hex，PositionErrorBound有限>=0且同长度单位；Core不验证外部来源仍当前，采用资格由宿主核source revision。编辑保留出处/原域，不把旧PositionErrorBound冒称变换后输出误差；Backend另报输出误差。缺口由D/V投影，Core不填补或改算法Enabled。

二维条件数统一为**线性2×2块的2-norm条件数**，仅这一执行判据用于Affine2D、Curve的B=[U V]、Rectangle半轴校验及DocumentToViewport/逆投影；Tx/Ty不进入条件数。令输入块A=[[a,b],[c,d]]，finite前检后取m=max(abs(a),abs(b),abs(c),abs(d))，m=0拒RG-003；令q=floor(log₂m)由IEEE指数/尾数位求得（包括subnormal，不调用浮点log），按指数移位以dyadic整数精确表示E=A*2^(−q)，使maxabs(E)∈[1,2)。E只作为精确dyadic值，不先写入double缩放临时数组；很小系数仍按指数保留，不能下溢成0。

在E上精确求h=abs(e11*e22−e12*e21)、τ=e11²+e12²+e21²+e22²；h=0是精确奇异RG-003，不能用任意epsilon判断。数学定义 `κ₂=(τ+sqrt(τ²−4h²))/(2h)`，但**执行边界不求sqrt或减相近特征值**：K=Profile.MaxCondition是实际finite binary64且K>=1，严格采用 `τ*K <= h*(K²+1)`，等号允许。这等价κ₂<=K，因为τ/h=κ₂+1/κ₂且κ₂>=1。两边全部dyadic整数乘加、统一指数后BigInteger比较，不在double里计算det/τ/K²或换成1-/∞-/Frobenius-norm；不满足拒RG-007-ApproximationBudget、FieldPath指出对应矩阵/半轴。精确整数临时量计MaxWorkingBytes且受deadline，预算不足RG-011，不用估计值放行。

需要逆投影时，先通过上述判据，再用精确det(A)与adj(A)计算六个逆系数有理值（平移项为−A⁻¹*[Tx Ty]），最后逐项round-to-nearest/ties-to-even成binary64。实现用BigInteger分子/正分母求二进制指数和53位商/余数，半值比较`2*remainder`与divisor、偶尾数决定tie；subnormal固定量阶2^(−1074)，处理尾数进位，不能先把det转double。精确非零逆系数舍入为0（下溢）、舍入Infinity/NaN（溢出/非法）、逆作用于有效输入所得非有限值均拒RG-007，不静默截断或继续HitTest；精确零正常输出0。原finite subnormal输入不因其小就判奇异，条件数精确比较没有double中间下溢/溢出；MinLength/坐标界仍按各入口独立核定。Curve无需求逆时不额外建立逆矩阵。

### 3.2 形状、拓扑与层次

| Shape | 必需字段与冻结处理 |
|---|---|
| Point/Segment | 1 点/2 点；Segment长度<MinLength拒绝。Segment显式顶点ID与坐标分别保存；Point中心无独立VertexId |
| Curve（圆/椭圆/弧统一参数形） | `p(t)=Center+U*cos(t)+V*sin(t)`，Start/Sweep 显式，`0<abs(Sweep)<=2π`；Closed只允许Sweep为精确double常量 ±(2*Math.PI)，开放弧必须abs(Sweep)<2π。U/V独立非零且长度>=MinLength、[U V]按本节唯一2-norm判据通过MaxCondition；Circle 为等长正交 U/V 的便捷构造，Ellipse/Arc 使用同一 Shape。仿射后直接变换 Center/U/V，保留 t，不误把参数角变成新椭圆方位角 |
| Rectangle | Center 与两条正交非零半轴 U/V；轴对齐仅为特例。一般剪切后四角形成 Polygon，不能保留 Rectangle 伪造正交。固定顶点顺序 `c−u−v,c+u−v,c+u+v,c−u+v`；声明矩形前以实际binary64精确谓词检查dot(U,V)=0，不静默改轴。Transform先检查新轴的同一谓词，非零则以四角Polygon保真（小舍入剪切也不投影成矩形）；转换顶点ID固定为 `v.`+小写hex SHA256(UTF8 NodeId)+`.corner0`～`.corner3`，与已有顶点碰撞拒绝；不含OperationId使Preview/Apply内容一致 |
| Polyline | ≥2 个稳定顶点，开放；不重复相邻点，不自动变成面积，允许不同非相邻边相交但不授闭面积资格 |
| Polygon | 叶节点必须>=1 Component（空结果用Snapshot的Empty Nodes表达）；支持域的Polygon可Empty Components表示空域。Component包含一个 Outer 与直接 Holes，洞内岛为另一 Component；Ring 保存 ≥3 个不同稳定顶点，不重复首点，闭合边隐式 last→first。外环/洞/组件不可接触或相交；不自动修复自交，不按最大区域截断 |
| Group（Node 层次） | Node.ParentId 为同文档 Group 节点；无环/悬挂父 ID，不能跨 Frame。Group 无 Shape，叶节点有 Shape。Group 是编辑集合，不把重叠子项解释成已 Union 的材料 |

严格 Polygon 前检：数值/数量→重复/零边→非邻边交叉/重合→环间交叉/接触→严格包含→Outer/Holes/岛。节点/组件/环/顶点/约束ID各类别在document内唯一（不同类别可同字串），所有引用显式指节点/顶点，不用数组位置。外环方向按数学signed area规范为正、洞为负；反射后反转环序但顶点 ID 跟随，不能重绑边引用。定向/段分类使用 DEV-VIS-024 §12 的实际 IEEE 值→二进整数精确谓词；只采纳谓词部分，不把固定三角片交点上界扩为任意 ROI 布尔。AABB/BVH 仅筛候选，段对检查必须完整；计数超 Profile 返回 Resource，不跳过剩余边。环间既无接触再做精确射线包含，不能只测一个洞顶点就证明洞合法。display tolerance 不参与拓扑判定。

空间选择采用闭材料政策：Box各轴Min<=Max允许零厚切片，Sphere.Radius>=MinLength，Prism MinZ<=MaxZ且有限；Outer边界及Hole边界入材料、Hole严格内部不入，z端面包含，洞内岛独立组件。边界分类使用§3精确谓词；Sphere用实际binary64值的dyadic整数平方差比较 Σ(point_i−center_i)²<=Radius²，复用§3精确谓词表示/工作预算，避免中间double溢出，不把空间容差变成球半径膨胀。未知支持声明不阻纯数学点集合选择，但Source.Support原样随结果返回，不能称全域观测完成。空间Profile.Frame必须和PointBlock.Source.Frame逐值相等且XYZ物理Frame，点/ROI坐标与半径/高度同Unit。

Prism按实际提供的B=[U V Normal]解释局部坐标，不因近正交就用dot当逆。**唯一执行判据**：t为Profile.SpatialBasisTolerance的实际dyadic值，0<t<=1e-6；对每axis用 `(1−t)² <= Σaxis_i² <= (1+t)²`，每两axis用 `abs(dot(axis_i,axis_j))<=t`，手性用 `Σ(cross(U,V)_i−Normal_i)²<=t²`，全部精确dyadic整数比较（等号允许）。不调用sqrt/norm再减1，不在double里计算平方/dot/cross/t²。

查询点以dyadic整数Cramer行列式求局部x/y/z有理值（统一把分母调整为正）；det(B)=0拒RG-003，不能投影/正交化输入。二维环orientation/ray crossing与z闭区间只需清分母做BigInteger符号比较，不生成新的布尔交点或浮点局部坐标。工作量/整数临时bytes计Profile，逐点核取消。3D保持既有G=BᵀB/Gershgorin保守路线：精确求 `e=max行Σ|G−I|`，e>=1拒RG-007；e<1时只用 `1+e <= K²*(1−e)` 精确dyadic交叉乘比较，K=实际Profile.MaxCondition，等号允许，不能在double中求K²或除(1−e)。这是κ₂(B)²<=(1+e)/(1−e)的可证保守门，未通过不换路线。全部有限前检与整数预算失败规则同本节二维；实际dyadic没有double平方溢出问题。这一限定点包含不是通用有理布尔，资格坐标关系仍由外部Owner提供。

### 3.3 参数与变更影响

`ValidationProfile` 字段全部由调用宿主显式给值，无无限预算。附录 A 的数值范围为：计数/字节/在途/队列/候选对上限正整数；历史步数/字节可为 0（同时为 0 禁用）；MinLength>0、MaxAbsCoordinate>MinLength、MaxCondition>=1、MaxCurveDeviation>0、MaxTessellationVertices>=2、0<SpatialBasisTolerance<=1e-6（无量纲）、MaxBackendWorkers/MaxHalconParallelism/MaxPointBlockSize/MaxRuns>0、CloseTimeout>0。Profile.Id/Revision/Hash 标识配置来源，Frame/Unit 必须匹配；Hash为64位小写hex SHA-256，由宿主已批准的版本化Profile字节取得，不把Geometry Codec当Profile Codec，也不由Core猜。

更换 Profile 必须 Drain 原会话并显式重开，不能静默影响在途请求；旧 Preview/Index/Codec 结果绑定原 document/revision/Profile。运行预算可以是宿主软件配置；Benchmark 验收阈值另由消费者采纳，不因能执行 Profile 就判性能合格。

### 3.4 2D/3D ROI 联动边界

2D footprint 可显式绑定到 3D Frame 的平面/高度域：PlanarPrism的Footprint必须>=1 Component、单位与空间相同，平面模型为 `Origin + U*x + V*y + Normal*z`，U/V/Normal 正交单位向量、`cross(U,V)=Normal`，x/y 与 footprint 同物理单位，z 区间有限且有序。像素 footprint 必须先经宿主提供的已资格坐标关系转物理域，禁止从屏幕深度或四角猜标定。Spatial-01 同时支持轴对齐 Box、Sphere 的点包含；本模块不扩展为通用 3D CSG、网格修补或重建算法。

3D 点选择先在同 Frame 的 AABB 粗筛，再作 Box/Sphere/Prism的冻结包含判据；Prism 投影到平面后按 Outer/Holes 检查、z 闭区间核对。按原point index返回有界索引块并原样携带来源支持声明，所有候选包括被遮挡点；屏幕只看最近面不等物理域只包含最近面。拾取所需 ray/相机/可见性由 viewport 端口提供，3D 对象/native 租约由 surface-data/viewport 持有，ROI 只消费，不复制它们算法。缺source revision则拒请求；未资格标定关系或缺支持时只能给软件数学选择，宿主不得采用为全域生产事实，保持缺口。

## 4. 创建、编辑、批量与约束

### 4.1 最小调用与内存事实

`IRoiGeometryFactory.Open(RoiOpenRequest)` 是唯一会话创建入口，注入完整 InitialSnapshot、Profile、关闭预算；无效时 Core=null。成功后 Query→Validate→Apply/Preview→Query→Drain→Dispose。每个实例 SessionId 唯一；不使用服务定位器、静态 Store、隐藏窗口或产品 VM。输入数组在边界复制为 ImmutableArray，调用者的后续修改不得改变 Snapshot。

### 4.2 命令与原子发布

Create/Replace/Delete/Transform/Reparent/Undo/Redo 都有 typed command。Create的新Node/Component/Ring/Vertex ID 由请求给出，复制/阵列由宿主预先生成完整 ID 映射后作为一个批量 Create；禁止 Core 用随机输出顺序生成身份。空命令数组拒绝，空 InitialSnapshot 合法。所有选中叶节点的 Transform 在同一 Frame/Unit 下使用一个请求中已合成的完整 Affine2D（含显式Pivot对应的平移项），不逐 ROI 猜中心；不同 Frame 要先经坐标端口明确转换。

Apply顺序：结构/身份有效性前检→按原OperationId查完整typed payload（§5固定优先级）→原请求回放或冲突直接返回→仅新请求核当前state/epoch/Profile/CAS/token/deadline→接纳OperationId（占有界墓碑槽）→冻结BaseRevision/选择/锁/约束/Profile→估算并预约预算→在候选副本上执行全部命令→统一结果校验→再次核 token/deadline/当前 revision→CAS 一次发布→记录历史/Receipt→释放临时工作→返回 Completed。一个批量中最后一项失败，前 N 项、UI当前选择、undo/redo 栈全部不变。无变化命令返回 Completed、Changed=false、revision 不增、历史不增。单文档 revision 一次递增，不对每个节点分别递增作为 CAS。

Undo/Redo 只用历史中已验证的完整 Before/After 内容，不做浮点逆变换累计误差。Undo/Redo 是新操作，成功 revision 仍递增；保留内容可与旧值逐字段一致（不含revision），但包含revision的payload hash改变、revision不回退。Undo/Redo 不得混在其它命令里；Steps 全链存在才一次应用。新编辑清空 redo；历史超过预算时整步拒绝，不偷偷删除历史。关闭释放实例历史；Undo 不回滚宿主持久提交或质量事实。

### 4.3 约束、多选择与锁

约束为 typed FixedLength、Coincident、Horizontal/Vertical、EqualLengths、AspectRatio；目标为稳定 vertex/node ID。本轮主路线是**验证式约束**：候选满足全部约束才发布；不做隐藏的非线性自动求解。宽高比编辑按显式锚点和固定比值派生另一尺寸；多约束有冲突返回逐条 ConstraintViolation，保留输入。未支持约束返回 Unsupported，不能忽略后继续。

多选操作使用完整 immutable SelectionSet；排序按 Ordinal NodeId，重复 ID 拒绝；Group 展开去重叶节点、校验锁和 MaxNodes。Locked 节点可被 Query/HitTest 命中但不能编辑，锁仅是会话编辑限制，不代表权限授权。Visible、Selected、Layer 与宿主算法 Enabled 分离；隐藏图层不自动免检。Reparent 防祖先循环，并只改变文档层次；层次排序/Z-order 不改变几何。SelectionSet是附录A的独立不可变ID投影，不储存在GeometrySnapshot。父Group Visible=false隐藏整子树，Locked=true禁止子树编辑，子项不能绕过祖先锁。

Delete Group递归删除完整子树；同批引用父/子先展开去重，只删一次。剩余节点上任何约束引用被删节点/顶点时整批拒绝ConstraintViolation，调用者须同批显式Replace删除这些约束，不能隐式去约束。Replace必须已有同NodeId，不改ParentId（改父用Reparent）；Group/叶类型互换拒绝，顶点替换须保留或显式处理全部引用。约束在全部命令执行后的候选统一校验。Transform选择父/子重叠先展开去重叶，逐叶同矩阵一次；Reparent选择祖先与后代同时出现拒绝。结构变动验证被影响节点及原/新父祖先锁；Locked节点Replace仅允许其它字段逐值相同的显式解锁（仍不得越过祖先锁）。锁是编辑保护，宿主权限独立检查。Group锁切换不改子项自有锁。

约束容差有限且>=0、Length>0、Ratio>0；Length/Tolerance与Frame同长度单位，AspectRatio.Tolerance无量纲。FixedLength/EqualLengths比较欧氏长度绝对差，Coincident比较点距，Horizontal检查abs(ΔY)、Vertical检查abs(ΔX)，不用屏幕轴。AspectRatio只引用Rectangle，比较||U||/||V||与Ratio；剪切降为Polygon后若未同批显式移除该约束则拒绝。VertexRef仅引用Segment/Polyline/Polygon的显式顶点，Curve/Rectangle隐式角点不假冒稳定VertexId。槽/预算等待计入原deadline，超MaxPending短拒Resource；同步等待检查token/deadline，不持会话锁等待槽或调用sink，UI后台调用Apply。

## 5. 错误、状态、事件与幂等

附录 A 是唯一 enum/Receipt 定义。接纳前失败短路径 `RequestRejected`，不伪造 Running/Drained。接纳后 `Accepted→Running→LogicalResult（可选）→Draining→Drained→ResourcesReleased→Terminal`；资源状态和操作终态分开。PreviewReady 是终态的一种，只在临时工作释放后返回；当前CanAdopt只存在QueryOperation的Adoption投影，不修改原Receipt（规则见下文）。Faulted/Cancelled/DeadlineExceeded/Stale/Unknown 无 Candidate；Query 可另取当前合法 Snapshot，不能把原 Snapshot 塞进失败 Candidate 冒成功。

事件是 immutable 投影，经附录 A 的 `IRoiEventSink.Publish` 非阻塞端口交付；sink 必须自己排队，Core 捕获 sink 异常、撤销故障 sink 并记诊断，不能回滚已发布几何或在锁内调用回调。每个操作 Sequence 递增、标明 Kind/OperationState/ResourceState/OperationId/SessionId/Epoch/Revision/StopwatchTimestamp；跨操作不要求全局事件顺序。超出 sink 预算只丢进度，Terminal/Receipt 以 QueryOperation 返回为权威，不无限队列。

编辑请求入口的唯一顺序（Apply/PreviewAsync相同，全部查找/新接纳在同一会话短锁内线性化）：

1. **结构与固定身份**：检查非null请求、合法OperationId/SessionId、SessionId等于本实例固定身份、非负Epoch/ExpectedRevision、已知Mode且与入口匹配、Commands非default/非空且长度有界、已知typed命令及字段/ID/有限数、Deadline.Frequency=本进程Frequency且Timestamp值形状合法。这里不检查期限是否已到、不读当前epoch/revision/锁/节点存在性，不展开当前Group，不观察调用者token。坏结构返回短拒，不改任何已登记项。
2. **按原ID查完整typed payload**：冻结调用边界值后，按声明字段递归比较（Commands保留顺序、NodeIds每条原始列表按Ordinal排序、重复ID在步骤1拒绝；数组比较内容、浮点负零统一为0），不靠record数组引用Equals/JSON/hash单值。Group展平只在新执行阶段，不能从改变后的当前文档重建旧请求载荷。RoiEditRequest所有字段都参与比较，包括原Epoch/ExpectedRevision/Mode/ProfileRevision与完整Deadline；固定实例Profile完整值绑定既有项，token对象不入payload。
3. **已有项优先**：同ID不同payload直接Rejected/RG-008-Conflict（仅本次短拒回执），不覆盖原项，即使只改deadline也冲突。同payload已终态直接返回逐字段相同的原RoiOperationReceipt；原deadline已过、观察者token已取消、当前revision改变、Drain/Disposed或epoch变化都不能把它改成Stale/Expired/Cancelled。同payload在途立即返回既有非终态观察（Candidate=null、不二次执行），重复观察者token不取消原工作、不阻止该有界快照读取；只有首次接纳调用的token/会话关闭意图能影响原执行。终态形成后固定原Receipt；在途观察随原工作真实进展更新，不是第二操作。
4. **只有未登记的新ID**：依次核SessionState=Open（否则RG-013-Disposed，诊断注明Draining/Drained/Disposed）、当前Epoch（不符RG-020-Stale）、ProfileRevision（不符RG-020-Stale）、ExpectedRevision CAS（不符RG-008-Conflict）、token（取消RG-009）、单调deadline（到期RG-016）、接纳容量；前一失败决定主码，均短拒、不占原ID、不发Accepted。新接纳与Drain封口同锁，随后按§4计算、发布前再次检查token/deadline/epoch/CAS。接纳前/后状态检查不得前置到步骤2/3抢走原回执。

QueryOperation只按合法ID有界查表，不要求当前epoch/token/deadline，Found=false/Receipt=null/Adoption=null只表示本实例未登记，不猜原操作失败。已登记项在Open/Draining/Drained/Disposed均可查，终态Receipt与初次返回逐字段相同；不因“关闭”消失。MaxReceipts满拒新接纳，不淘汰登记项。Dispose释放运行工作/索引/Undo历史但仍保留完整typed payload/终态Receipt及最后只读Snapshot，直到同一实例被GC或进程结束；这些有界托管墓碑/值保留量在接纳时计入Profile的字节预算，不称零存储。原生或在途资源必须真正归还，不能靠保留墓碑冒充排空。

`RoiOperationReceipt`记录历史事实且没有CanAdopt；`RoiOperationQuery.Adoption`是一次与Receipt/当前SessionSnapshot同锁读取的独立`RoiAdoptionProjection`。CanAdopt=true仅在Receipt为Completed或PreviewReady、IsTerminal/ResourcesReleased=true、Candidate非null、Session仍Open、当前Epoch等于原Epoch、固定Profile绑定不变，并且当前revision等于Preview的BaseRevision或Completed的OutputRevision（含no-op）时成立；其余false。Query未知ID无投影。执行deadline只限制原操作执行，终态后期限到期不自动使仍当前的候选失效；生产来源资格/权限/持久提交仍由Host核。投影是观察时点事实，不是后续CAS授权，Apply仍须新ID/当前基线/新期限。Drain/Disposed及revision变化只令当前投影false，不能删原成功Candidate或重写原Receipt；回放入口仅返回Receipt，需当前资格者另QueryOperation。


| 稳定码 | 触发与恢复 |
|---|---|
| RG-001-InvalidArgument / RG-002-NonFinite | 缺失/非法范围、NaN/Infinity；修正输入新 OperationId |
| RG-003-Degenerate / RG-004-Topology | 零长度/奇异/自交/接触/非法洞；定位 Node/Ring/Edge，禁止静默修复 |
| RG-005-FrameMismatch / RG-006-Unsupported | 单位/Frame/表示不匹配或无支持能力；显式转换或选择批准表示 |
| RG-007-ApproximationBudget / RG-011-Resource | 误差/复杂度/内存/队列/候选对超限；释放已可释放临时物，旧事实保持 |
| RG-008-Conflict | revision/重复请求/锁快照冲突；查询后合并，不自动覆盖 |
| RG-009-Cancelled / RG-016-DeadlineExpired | 发布前撤销/单调到期；等待真实排空，不能延长同请求期限 |
| RG-012-Serialization / RG-013-Disposed | 损坏或关闭；保留原字节/新建会话，不复用失效句柄 |
| RG-014-Backend / RG-015-Unknown | 视觉/提交端口异常或终态不可证；保留操作与资源，查询同 ID，不自动重跑 |
| RG-017-ConstraintViolation / RG-018-HistoryUnavailable | 约束冲突/历史不足；查看冲突、调整命令，不部分应用 |
| RG-019-ReadOnlyUnknown / RG-020-Stale | 未知 Schema/字段或过期来源；只读导出/刷新，不能采纳已知子集 |

旧 `RG-010-Timeout` 只用于兼容历史诊断，新执行统一 RG-016；没有质量 PASS 错误状态。MessageKey/RecoveryKey 为可本地化资源键，详细技术诊断不作为唯一用户文字。

## 6. 取消、deadline、排空与资源 Owner

- 同步 Validate/Apply 和异步 Preview 的大规模计算均接收 token 与 MonotonicDeadline；Query/QueryOperation只读取已发布immutable引用/有界墓碑，不执行几何重算；工厂完整初始文档校验也受同Profile预算，不能称短校验而遗漏拓扑。Stopwatch clock 只在当前进程有效，跨进程只传剩余 duration 并收紧重建期限，不序列化 timestamp。新操作执行中到期、取消同时被观察时操作状态Cancelled（两原因可同时记录）；二者均优先于发布前普通完成。
- 长循环每节点/环、每批段对/顶点/点块检查，单批不超过 Profile.CheckBatchSize；native 算子不能被 token 强制中止。排队同样计入期限，不在 Started 时重置计时。deadline 构造使用 checked 向上取整到 timestamp ticks、frequency 必须 Stopwatch.Frequency、timeout 有限正数；默认 struct/非法频率拒绝。
- 同一会话写入串行（MaxPending有界、入队按已接纳顺序），读冻结Snapshot；跨会话独立，不共享可变 Profile、语言、native 或取消。Preview 不持锁运行；完成重新核 BaseRevision/Epoch。Drain 禁止新请求、epoch加一（checked，溢出时封住接纳并按既有pending排空，不回绕）、请求内部取消并等待工作真实退出；不存在 UI Dispatcher 等待环。
- `RoiDrainReceipt.Status=DrainUnknown` 是排空观察结果，Session 仍 Draining、ResourcesReleased=false，列出 PendingOperationIds；不发布操作 Terminal、Disposed 或成功。deadline 到期或 Drain token 取消仅停止此次观察，不撤销关闭意图，允许再次 Drain/Query 原会话。纯 Core 也可能因工作尚未到取消点返回 DrainUnknown，不能因“无 native”假定已经停止。
- 实际排空后 NativeResourcesOwned=false、PendingOperationIds 空，Drain=Drained，ResourcesReleased=true；DisposeAsync 使用 Open 时冻结的 CloseTimeout，不能偷偷无限等待。未排空时抛 RoiDrainIncompleteException（带 Receipt），实例仍隔离可查询/Drain；不置 Disposed、不丢引用。无需 native 的短同步操作只释放自己的临时工作，不清除会话草稿/历史/Receipt；实例关闭释放历史/可释放运行工作，最后Snapshot及登记请求/终态Receipt按§5保留为有界只读墓碑。
- HALCON-01 的 iconic/control/native 临时对象由 adapter worker 拥有，v0.3输入只接受immutable Vector/Runs值，外部native Owner先导出有界runs后调用，借用lease由外部Owner归还，先退出算子和回调再归还。对象在输出租约中时只释放临时资源，结果租约由消费者 Dispose；Benchmark 同时记操作临时释放与输出归还，不偷换端点。不为 ROI 模块关闭 surface-data/viewport 的共享所有者。

## 7. HALCON 26.05 路线、参数与表示

### 7.1 调用基线与确定选择

AsunImage 是 HALCON 26.05 薄封装，全部算子经 `ImageLibDotNet.cv2` 使用；不再重复核验“有没有此算子”，不直接引用 HOperatorSet/halcondotnet.dll、不查 AsunImage 内部。只有实际 C# 重载/参数类型/封送歧义才查公共签名或消费项目编译。下表 operator 名称对应本地同名 `.html`（26.05.0.0），既有资料复用，本轮读取并修正会影响结果的语义。

| 能力/输入域 | 冻结主路线与分支 | 参数、失败与后检 |
|---|---|---|
| 连续线性闭多边形布尔 | `cv2.Union2ClosedPolygonsXld` / `IntersectionClosedPolygonsXld` / `DifferenceClosedPolygonsXld` / `SymmDifferenceClosedPolygonsXld`；满足§7.4无损xld_poly转换后，线性输入输出标为 AnalyticVector、Precision=BackendNumeric（不能冒称严格 Exact） | 每 operand 先核严格环/洞/组件；HALCON 使用 Even-Odd、自动闭开放环并可拆自交，故 Core 必须先拒绝开放/自交。一个组件的 Outer+Holes 可组成一个 boundary set；**重叠材料组件必须逐组件 Union，不能把重叠外环一起打包**，否则交叠被当洞。Difference 按 S−Union(C1…Cn)，保留角色。后检完整环包含树、身份来源、全部组件；无引用的输出不能假装带原 XLD contour reference |
| 同 grid 离散 Region 布尔 | `union1` 合并明确实心 Region、`intersection`、`difference`，Xor 以两差集 Union；仅 RasterizedRegion 请求可走此支 | iconic tuple 为 0 项与 1 个空 Region 必须分别识别；有效 Empty 不是无输入/异常。保留 grid、空策略和源角色，不用 Region 结果覆盖连续原件 |
| Shape 仿射/轮廓仿射 | 纯值对象编辑按 §3.2；XLD 用 `affine_trans_contour_xld`/`affine_trans_polygon_xld`；点对照 `affine_trans_point_2d` | XLD/Region 采用 corner 原点。设 S 交换 column/row，C 是 `(0.5,0.5)` 平移，中心数学 T 传角点算子时为 `C*S*T*S*C^-1`；原生角点矩阵不重复补偿。点算子传 Px=row、Py=column，无角点补偿。非对称旋转/平移用例必须抓住反序与双补偿 |
| 原 Region 仿射 | `affine_trans_region`，本版请求固定显式 `nearest_neighbor`；`constant`仅官方对照，不在A.4可执行域 | 官方说明插值可显著增耗、变换不可逆；不以运行成功证明原集合等价。先核 grid/矩阵，后记录离散化/裁剪/支持域，不自动以 Region 作连续变换备用 |
| 曲线→XLD | Curve以B=[U V]、R=1统一写 `e<=2||B||₂*sin²(Δt/4)` 界细分、`gen_contour_polygon_xld`；只派生 Tessellated | 单段角域 ≤π，端点显式包含、MaxDeviation 与顶点上限受 Profile；近似界加坐标舍入，拓扑重新核。若批准用途禁止近似或预算不足直接拒绝；不按每度一点/显示 LOD 做量测 |
| Vector/XLD→Region | 对 polygon 请求 `gen_region_polygon_filled`；XLD 请求 `gen_region_contour_xld`，本版Mode固定显式filled；margin仅官方对照，不在A.4可执行域 | 前者先舍入亚像素顶点，后者按 Bresenham、neighborhood 且自动闭合/舍入，二者不等精确 PixelCenterInside。每组件 Outer 与 Hole 按相同方法栅格化后 Difference，再 Union 组件；顺序不得重排。polygon方法名为HalconRoundedFilled26，contour方法名为HalconBresenhamFilled26，不声称别的扫描规则等价 |
| Region→XLD/精确保存离散集 | 需要洞必须 `gen_contour_region_xld(...,'border_holes')`；center/border 只用于显式请求。保存离散集用单 Region `get_region_runs`/`gen_region_runs` | Region→border XLD→filled Region 不无损；单像素 (1,1) 可变四像素，禁用作复制。runs 行/列有序，空 Region 给三个空 tuple；多个 Region 逐对象处理，run 数不是组件数 |
| 相交/HitTest 核查 | `test_self_intersection_xld` 仅后端诊断；`distance_pc` 可对照点到轮廓**线段**最短距离 | 官方说明精确点在边上受数值限制，不能取代 §3 严格谓词/完整洞资格。HitTest 多候选排序由 Core 冻结，不以算子返回第一个决定身份 |
| 3D 域点筛选 | 外部点云 adapter 使用 `select_points_object_model_3d` 的 point_coord_x/y/z 范围作粗筛；Sphere/Prism 由 §3.4 有界点包含精筛 | 多属性阈值为 AND；属性/索引来源必须存在。Box 用同 Frame x/y/z 闭范围；曲面/遮挡不自动修复。3D 数据 Owner 与 native lease 仍属外部模块 |

`LF-Exact-Dyadic-FixedPair-1` 只用于既有固定片资格与实际 binary64 谓词，**不作为一般连续布尔替代**。Clipper/NTS 不引入产品依赖，不偷偷换路线。当前只冻结上述输入域/分支/参数与方法，不宣称最快；HALCON-01 仍需同样本 Golden、类型编译和精度/性能资格。未验证的一般有理递归布尔保持 Unsupported。

### 7.2 系统参数隔离与 native 顺序

本轮 `set_system.html` 明确 tsp_ 变体只影响当前线程；普通值可能影响当前/新线程，不能依赖共享全局设置。HALCON-01 采用专用有界 worker 线程，在该线程读取并保存 `tsp_clip_region`、`tsp_store_empty_region`、`tsp_neighborhood`、`tsp_thread_num`，显式设置 false/true/请求的 4 或 8/Profile.MaxHalconParallelism，完成后在 finally 原线程恢复并读回；**设置到算子调用/恢复之间不 await、不迁移到另一线程**。生成全部原域后再显式裁 grid，不丢设计域。恢复失败隔离该 worker，拒绝后续工作；不继续污染其它消费者。没有证明资源退出前不得丢输入/输出引用。worker 数与 HALCON 自动并行额度由 Profile 限制，不叠加无界线程池。

算子返回错误不自动重试、不换表示；先完整释放实际可释放临时物再返回Faulted/RG-014-Backend。不可中断调用超过 deadline：撤销采纳资格、标 Draining，观察返回 DrainUnknown，native 实际返回后清理再登记 Cancelled/DeadlineExceeded 终态。预览断连不等停止；原 OperationId 查询保持，未证明退出不重新提交。

### 7.3 自动参数建议（只产候选）

唯一自动建议是曲线离散步长：输入Curve半轴B=[U V]/扫角、批准 MaxCurveDeviation ε、最大顶点；取B=[U V]（完整目标坐标中的半轴），用 `2s*sin²(Δt/4)<=s*Δt²/8` 的保守界计算安全段角，s>=||B||₂，向上取整段数、预算内等分并后检向外舍入界（附录A.3前的实施步骤）。通过附录A.3的IRoiCurveTessellationPlanner.Suggest输出输入hash、公式版本、建议顶点数、几何误差界和拒绝原因；宿主明确接受后形成新 Profile/请求。ε、拓扑政策、栅格方法、物理阈值不由图像弱信号或机器内存自动猜。不训练模型，不自动补遮挡边，不在生产静默改参数。

### 7.4 HALCON-01 完整桥与输出规约

这一节补具体适配步骤，§7.1/§3/A.4仍定义选择与数值门。**本轮实际发现并修正的内部缺口**：连续布尔算子接收的是 `xld_poly`，`gen_contour_polygon_xld`只产生 `xld_cont`，不能直接送布尔算子；`gen_polygons_xld(...,'ramer',Alpha)`官方要求Alpha>0，不能用0猜测无损转换。因此冻结下列正Alpha转换+实际线性边界等价后检，不更换HALCON路线，不改旧Golden期望，不把近似结果标Exact。

1. **接纳/输入冻结**：A.4完整请求结构/Profile/Frame/hash/表示组合前检，原ID优先回放后才接纳新ID。operand按A.4顺序，Snapshot所有Shape叶节点（含隐藏/锁定）是明确输入集合；Group只层次，不推断Enabled；不同Snapshot是不同集合，不把父/子重复材料。空Snapshot是合法空集合；Point/Segment/Polyline/开放Curve不能进入面积路径。预算预约输入、每个native中间物、输出及leased结果；专用worker按§7.2原线程设tsp，不在native片段await。
2. **Vector→闭边界**：Rectangle按§3四角；Polygon每Component的Outer/Holes保留材料结构；Curve仅在请求Tessellated/Rasterize时按§8有界弦差细分，MaxDeviation在当前Frame单位，末点明确等于首点，Curve原参数不改。Closed Curve请求AnalyticVector布尔拒RG-006（不能把曲线多边形叫解析保真）；纯Vector Transform可以直接返回变换后的参数Curve/Rectangle/Polygon。所有数组column=X,row=Y；不在创建XLD时加0.5，也不改Unit标签。
3. **闭边界→xld_poly及布尔**：逐环 `gen_contour_polygon_xld(Row,Col)`（显式重复首点闭合）→`gen_polygons_xld(Contour,'ramer',Alpha)`。Alpha固定为`min(Profile.MinLength,request.MaxDeviation)/1024`，finite正数才执行，若下溢到0以这两者的正最小值为Alpha；Alpha只是HALCON类型转换阈值，**不授额外简化误差**。`count_obj`→`select_obj`用1-based索引→`get_polygon_xld`取Row/Col，按§3实际dyadic精确谓词比较输入/取回边界：去掉重复闭合点、连续重复点、位于相邻端点间的精确共线中点，统一方向/最小起点后逐字段相等。只能省去真正共线冗余点，不允许移动角点；不同、拆为多环或打开边界即RG-007，不偷偷加Alpha误差或换Region。曲线离散输入也做这一等价检查，Report只记录已证明的弦差界。
4. **材料fold**：同Component Outer+Holes组成一组xld_poly（`concat_obj`）；先由§3保证同组环不接触，自含洞由Even-Odd解释；不同Component/不同叶材料通过 `union2_closed_polygons_xld`逐组联合。operand集合生成后，Union/Intersection/Xor按A.4固定Id fold；Difference第一项为Subject，其余Clip先Union再Difference。不交Intersection/减尽返回确定Empty，显式空集合按代数规则处理，不用0-object行为设置猜结果；Union/Xor空与S为S，Intersection空为Empty，Difference空Subject为空/空Clip保持Subject。结果按下一步重新取回，不继承输入contour reference。
5. **xld_poly输出→typed Vector**：`count_obj`只计对象，不当组件数；逐1-based `select_obj`→`get_polygon_xld`，明确xld_poly不用get_contour_xld。除重复闭合/连续重复/精确共线中点外不修补、不容差合点；不足3个不同点、零面积、非finite、交叉或触边拒RG-004/RG-002，保留原请求诊断。严格非相交闭环通过精确射线包含建立最小包含父环（按绝对面积最小且确实包含），深度偶数Outer、奇数Hole，洞内岛是新Component；方向/起点/排序/派生ID按§3/A.4，给完整新document revision0。空结果为Empty Nodes。完整后检及所有计数/字节预算通过才能交付lease；用户取消/期限已到不能发布Candidate。
6. **栅格坐标/两方法**：定义`G(column,row)=Origin+(column*StepX,row*StepY)`。Vector先显式处于Pixel Frame，按 `G^-1`转成grid中心坐标再传Row/Col，不把非零Origin/非单位Step丢掉。HalconRoundedFilled26固定 `gen_region_polygon_filled`；HalconBresenhamFilled26固定 `gen_contour_polygon_xld`→`gen_region_contour_xld(...,'filled')`。每Component按同方法Outer减各Hole，然后材料Union；曲线先离散，点/线不栅格成面积。两条路线不同，禁止依据速度自动换。ClipExplicitly=true时在完整结果上 `gen_rectangle1(0,0,Height-1,Width-1)`→`intersection`，false不裁；裁剪前后 `difference`非空才Report.Clipped=true。不用图像 `crop_rectangle1`处理Region，不全图铺mask；Grid/Frame原样绑定结果。
7. **Runs/Transform/Boundary**：输入runs分ObjectIndex `gen_region_runs`（End>=Start先校验）→`union1`成明确材料集合，合法空用 `gen_empty_region`不是空tuple。Runs Transform的数学T在Frame单位，角点矩阵为 `C*S*G^-1*T*G*S*C^-1`；G=identity时回到§7.1公式，不能传Frame单位平移当pixel步数。`affine_trans_region(...,'nearest_neighbor')`后按步骤6显式裁。ExtractBoundary固定 `gen_contour_region_xld(...,'border_holes')`→逐对象 `get_contour_xld`，取回Row/Col再按G转Frame坐标/严环后检，结果Tessellated，不能做Region→XLD→Region无损拷贝。对8邻域角点接触产生不满足严格Vector拓扑的输出，返回RG-004，**Runs材料仍可独立保存/布尔**，不为Vector自动裂点或伪造洞。
8. **计数/空/导出**：Region主结果为一个已union的material对象，面积0时gen_empty_region，lease Components/Holes=0、runs Empty。非空Components用 `connection`→`count_obj`；先读 `get_system('max_connection')`，非0拒RG-014说明可能截断，**不写全局max_connection**。为防宿主并发改全局，结果组件数以实际get_region_runs按行区间邻接的有界union-find核对（4邻居比较相邻行区间相交，8邻居允许一列扩展；int边界用long），不一致拒RG-014。该检查是离散完整性后检，不代替HALCON布尔算法。Holes=`difference(fill_up(material),material)`的组件数，按官方fill_up同Neighborhood；洞集合也须执行同一get_region_runs邻接计数与connection/count_obj核对，读回max_connection非0或数量不等即RG-014。两次核对均先核MaxRuns/MaxWorkingBytes，以规范行runs双指针比较相邻行、union-find合并邻接，计数和int扩展用checked/long，每CheckBatchSize核取消/期限；预算不足拒RG-011，不跳过核验。MaxRings/输出上限前检；不把XLD对象数或run数当洞数。`get_region_runs`逐结果对象导出，保持ObjectIndex连续且每行合并成规范runs；返回的三个tuple长度必须相等、坐标在Int32及Grid政策范围，超范围RG-011，不unchecked截断。Materialize只读取此已冻结结果，不再运行另一种算法。
9. **租约/数值**：临时native对象/HTuple在同worker按依赖逆序释放；`select_obj`是引用型结果，不深复制、不得先释放消费者在用的结果所有权。输出交同一IRoiGeometryLease，Info/Report/typed结果只读，空也有有界空lease；输出取回的工作区/tuples/resources计§13。RequireBoundedCoordinates=true但无法证明native坐标舍入界时RG-006/007；false保留CoordinateErrorBound=null/BackendNumeric。高效Runs保存为DiscreteGridExact只指整数集合/同grid，不给连续精度承诺。异步观察/原ID/lease/关闭恢复沿§10.2/A.4，没有未归还就Dispose掉的路径。

HALCON参数均由Profile/Grid/RasterPolicy/MaxDeviation或本节具名政策取得，无隐藏机器内存/工艺阈值；推荐只为§7.3曲线分段候选。worker自启动、停止和lease生命周期属于本模块，第三方图像/点云native导出由外部Owner，输入只有typed Vector/Runs/point块，不扫描共享句柄。算法/装配定位固定，实际消费程序集的C# out参数/tuple类型以ImageLibDotNet公开签名编译确认，不以编译调整这里的坐标、材料或误差合同。

## 8. 无 UI 能力、端口与独立发布

RoiCurveTessellationPlanner在Core公开无参数构造。Suggest只做值对象建议，不执行native或改Profile，先核Curve/Frame/InputSha256/MaxDeviation（0<值<=Profile.MaxCurveDeviation）。冻结保守算法，避免把libm的asin/sin计算误差当严格界：取 `s>=||B||₂`，利用 `2s*sin²(Δt/4)<=s*Δt²/8`。scale=max(abs(U.X),abs(U.Y),abs(V.X),abs(V.Y))>0；四个abs/scale向上舍入后，求最大行和r、列和c，s=scale*sqrt(r*c)全向上舍入，作为可证的诱导范数上界（不直接用可能低估的谱范数公式）。取向下舍入q=min(ε/s,1)，delta=sqrt(8q)向下舍入，`n=ceil(向上舍入(abs(Sweep)/delta))`，checked n+1<=MaxTessellationVertices；显式等分并核 `向上舍入(s*(abs(Sweep)/n)²/8)<=ε`，不满足增加n且受顶点/deadline上限。下溢到q/delta=0、非有限或预算超限拒ApproximationBudget，不返回默认角度。

非负+/*/除法的向上/下运算分别为 `Math.BitIncrement/BitDecrement`包住实际结果（0下界取0）；任何非有限立即拒，不把Infinity当预算。sqrt从Math.Sqrt取seed，用§3 dyadic整数精确比较seed²与输入，必要时BitIncrement/BitDecrement到指定侧；最多4次修正且每次核deadline，未证到边界拒ApproximationBudget。因此不依赖未声明的区间库。理想弦误差界与顶点坐标舍入分开，后者由Backend.Report记录，建议不证明拓扑/物理资格。公式版本`RG-CurveSagittaBound-1`，失败Segments/Vertices/GeometricErrorBound全null。例：R=20、Sweep=2π、ε=0.01得n=100、首尾闭合共101点，理想弦误差约0.009868792685、保守报告界略高于0.009869604402且仍<0.01；ε只是软件样例，不是客户允差。

### 8.1 HitTest、框选、层次与多候选

Interaction-01 是无窗口纯 Core 扩展；坐标输入为ViewportPoint/ViewportBox与宿主已冻结的DocumentToViewport Affine2D，容差是 DIP（必须显式正值），不是文档物理容差。先反投影容差窗口 AABB→按 Snapshot revision 的不可变 BVH 粗筛→在 viewport 坐标做点/边/曲线最近距离与实体内包含精筛。Polyline/Polygon 线段使用投影夹限；Curve 按有界细分，返回区间距离与曲线误差，误差覆盖边界时输出 AmbiguousCandidates，不挑一个假定精确命中。

候选排序固定：可见编辑 handle→顶点→边→实体内；同类别按distanceDIP升序、ZOrder降序、NodeId/ElementId Ordinal升序。恰同距离不靠渲染/线程完成顺序；Alt 循环候选列表，改变 viewport/source revision 必须重算。隐藏节点不参与 UI pick，Locked 可选但标只读；算法 Enabled 与 Visibility 无关联。Group selection 以稳定 ParentId 投影，子/父重复选择展开一次。窗口框选=完全包含，右至左 crossing=相交；孔内空白不命中实体，边界可命中边。空文档返回 Completed、空 candidates。

主索引是内部 immutable median-split AABB BVH：轴选包围盒跨度最大（相等 X），按中心坐标再 Ordinal ID 排序，中位分割；每 revision 建一次，旧 reader 持自己的快照。叶项不能用 index ordinal 当 ID；构建/查询工作量受 Profile，上限超出拒绝完整结果。比较基线为线性扫描，按同样输入核候选集合一致。大图不创建整图 mask、不逐 pointer move 扫全顶点、不创建逐顶点 WPF Element；只更新可见 overlay，非选中用 display LOD，真源始终保留。图像 Tile/Pyramid/GPU 缓存归 viewport/image-frame，ROI 不复制或全图解码。

HitTestRequest.Selection明确输入，重复/缺节点ID拒绝，Group展开一次；Handle候选只为当前选中且可见叶节点的center（Point/Curve/Rectangle）及Curve/Rectangle的u+/v+半轴端点，ElementId固定`handle.center/u/v`；Segment/Polyline/Polygon显式顶点走Vertex，边ElementId由起止稳定VertexId排序对组成（长度超限只内部用结构键，不造外部NodeId）。Closed实体才有Interior，开放Curve无内域。Point模式ViewportBox=null，框选必须有效Box且忽略ViewportPoint；曲线窗口包含/相交以保守段误差区间核定，覆盖决定边界时AmbiguousCandidates=true、不可自动采纳。HitTest不截断超MaxCandidates成成功；BVH构建/结果缓存总bytes计Profile且旧revision缓存按有限预算整份淘汰，不淘汰已有reader持有的对象。

Interaction/绘制的内部确定补充：BVH叶容量固定8个Shape；叶AABB由实际几何获得，Segment/Polyline/Polygon取全部顶点，Rectangle取四角；Curve用整椭圆保守界 `Center.X±sqrt(U.X²+V.X²)` / Y同式，即使弧短也不截掉潜在点，平方/sqrt向外包络复用§8有向舍入（非finite拒RG-007）。构建中位排序的center用端点dyadic和/2比较，不double溢出；Group没有面积叶。索引键为documentId/revision、几何逐字段内容与完整Profile（含Id/Revision/Hash及全部预算值），不能只拿revision跨不同文档共享；同revision不同完整值拒冲突。每个Interaction实例持有已完成不可变索引，构建私有工作区、锁内仅发布引用/预算计账，取消构建不发布半树；reader有借用计数且在finally归还，无UI隐藏依赖。缓存仅当前1个已发布revision与仍被reader使用的旧revision，占用总额按实例核；切换Profile也只保留一个当前索引，所有旧reader引用与新工作区合并计账，按新请求Profile核预算（不能为每个Profile另开无限缓存），容量不足拒RG-011而不是无限保留或驱逐在用reader。关闭WPF时等待实际HitTest Task退出；Interaction无后台线程/Dispose入口，最终无reader的实例由托管Owner回收。

Point命中不含near-zero除数：边到viewport点距离投影参数先检查精确长度平方为0，退化可见边按点；非零以有理t=(p−a)·(b−a)/||b−a||²清分母夹[0,1]，端点距离平方以dyadic整数比较ToleranceDip²，线段内投影的有理距离平方清正分母后整数交叉相乘比较；不能将非dyadic有理值round到double再决定命中。Curve使用§8分段误差在完整DocumentToViewport线性块放大；设其保守正谱范数上界为s，document离散界取min(Profile.MaxCurveDeviation,ToleranceDip/(4*s))并后检向外舍入，确保DIP界<=ToleranceDip/4（下溢/无法证明则RG-007）；最小弦距d与包络e形成[max(0,d−e),d+e]，下界>容差排除，上界<=容差确定命中，中间AmbiguousCandidates=true且保留候选；任何误差/顶点/MaxCandidates超预算返回错误而非偏选。精确Interior仍按§3洞材料政策，框选完整包含/相交使用边界分类，不仅AABB；BVH与全扫描使用同一精筛。Arc保持参数区间，整圆AABB只粗筛不授额外命中。

大图overlay冻结为**显示投影**：由viewport bridge自己的Renderer消费A.6 Snapshot/Preview/Selection、最新document→DIP投影和借用图像，不创造ROI专用图像窗口。先用同BVH可见框筛Shape（选中但框外只保留Selection，不画越界控件）；Preview优先显示候选虚线、实草稿仍可看原差异。非选中Polyline/Polygon只用于画边的Ramer分段栈，以精确viewport距离检查每条被省略链到新弦<=0.5 DIP，不能把这种简化环填充当命中/拓扑/算法输入；Polygon填色需要原完整边界（预算不足只显示边并提示显示简化）。选中节点/正在编辑边和全部稳定vertex使用原值，Curve绘制弦差<=0.25 DIP；handle只给当前选中、可见的点，视觉尺寸8 DIP不改变Core长度单位。LOD结果按document/revision/ViewRevision/DPI/Selection/Preview完整键缓存最多当前1份，取消/过期不能发布；占用含旧reader实际引用，不借大图像像素数推断ROI几何规模。

每个Renderer输入/输出都受Attach Profile.MaxWorkingBytes/MaxOutputBytes/MaxVertices、MaxInFlight及deadline约束；最多一个后台构建任务和一个最新待构建overlay引用，替换pending前释放已可释放引用，不每次PointerMove积压。WPF绘制用一个clip到ClientBounds的DrawingVisual/冻结StreamGeometry批量路径；不逐像素/顶点建WPF Element。两图层（原事实/候选）在实际Dispatcher上一次交换，当前可见drawing token带ViewRevision；帧内只合并请求，不承诺固定FPS，实际Pointer/Render P95由§13采纳。预算未能画完时PublishOverlay=false/诊断 `Roi.DisplayBudget`，不能把截断Shape假装完整，更不影响Core事实；宿主恢复入口可缩小可视范围/释放闲置视口资源后刷新。桥只借图像/viewport，不Dispose其Owner，native图像或点云租约由该Owner已有公开接口保持。Geometry/Runs结果与大图显示LOD绝不相互覆盖。

### 8.2 Codec-01 字节序列化与迁移

CoreSlice-01 无文件 IO；独立 Codec-01 的 `IRoiGeometryCodec.Encode/Decode` 无 UI、无 Store、仅消费/返回 bytes，由宿主选择文件/数据库保留，不赋予 Core 持久事实权。格式 `roi-json-v1`：UTF-8 无 BOM，固定 envelope 顺序 `format,major,minor,payloadHash,payload`；major=1、minor=0。payload=`documentId,revision,frame,nodes`，frame=`id,unit,axisConvention`，node 按 Ordinal ID，字段=`id,parentId,zOrder,visible,locked,shape,constraints,source`；shape首字段kind，值为point/segment/curve/rectangle/polyline/polygon；约束首字段kind，值为fixedLength/coincident/axis/equalLengths/aspectRatio。其余字段按附录声明顺序，字段名将PascalCase首字符小写（Sha256→sha256、U→u、StartRadians→startRadians），数组保留顶点/洞/组件顺序，字符串转义固定：双引号/反斜线用JSON短转义，U+0000～001F全用小写四位unicode转义，其余Unicode按UTF-8原码写出（拒未配对surrogate），不转义斜杠/非ASCII；finite double用InvariantCulture R，负零写 0，integer 十进制，no whitespace。`payloadHash=SHA256(规范payload字节)`；该规约具名为 roi-json-v1，**不是 RFC8785/JCS**，不重算其它模块旧身份。

payload/frame/node字段以§8.2显式映射为准（frame.axisConvention映射RoiFrame.Axes，node.id映射Id），其它DTO遵守首字母小写规则；shape无额外ShapeId，Point2/Affine/Curve 的 double 依上表；node/vertex/ring/component ID 必须写入。Curve U/V 与角域原样保存，不序列化拟合 Circle 标签覆盖一般 Curve。约束不重复写基类Id，Id紧跟kind，VertexRef字段nodeId/vertexId；所有null字段必须写null、bool小写true/false、enum使用附录声明的大小写敏感名称，不用整数；Source 的来源sha256/revision/frameId/method/positionErrorBound/support全部留存，外部权限/Target/设备不入 payload；不保存 SessionId、Stopwatch timestamp、线程、native handle、缓存/历史。几何hash按同规约payload（包括revision）；Undo内容等价逐字段比较除revision外的值，不另造未声明ContentHash。浮点负零统一为0；ImmutableArray按内容比较，不用record默认Equals的数组引用相等。

Decode 先检查 MaxSerializedBytes/MaxJsonDepth/MaxNodes→重复 JSON 字段、编码、format/version、finite 数→按具名规范重编码比 payloadHash→结构与拓扑→返回 DraftImport；不直接改会话。顺序优先级：先有限bytes/合法UTF-8/完整JSON/重复字段前检，再识别版本；未知版本或嵌套字段不按v1 schema强解、不擅自规范化未知payload hash，保留原bytes的RawSha256，不称已验证其未知规范hash。已知v1才验证payloadHash并进行全部结构/拓扑前检。未知major/minor/discriminator/字段不能静默丢弃：返回 ReadOnlyUnknown、Snapshot=null、RawPayload保留原bytes，RawSha256=SHA256原bytes，可原样导出，不能执行已知子集。损坏/截断 hash 返回 Serialization，原件仍归调用者；只读未知不是成功几何。兼容升级由宿主产生显式迁移草稿（仍用DraftImport状态），新文档 ID/来源闭包，保留原 bytes/hash；回退使用旧 Codec+Core 完整包。

Codec独立固定向量 `RG-K03`（不含下面围栏和行尾换行）：

```json
{"documentId":"doc.vector","revision":0,"frame":{"id":"pixel.xy","unit":"Pixel","axisConvention":"ColumnRowPixelCenters"},"nodes":[]}
```

规范payload为UTF-8无BOM、**133 bytes**；payloadHash=`0aae522e5aa588fdc37e53d93bb346a34e970a24d27b442b29d638ac019ea35b`。该值只哈希payload，完整envelope按既定顺序嵌入它；RoiEncodeResult.Sha256为完整返回Bytes的SHA-256，不能拿payloadHash代替。Encode空文档所得envelope内的规范payload必须逐字节等于此向量；Decode已知v1需验证payloadHash并返回DraftImport空Nodes。BCL测试用固定字节串独立SHA256.HashData核对133/hash，不从受测Codec取得“期望值”；增加BOM/空格/尾换行不是此规范字节向量。主控BCL与本轮Python标准库复算一致只证明字节向量，不是C#模块运行或性能证据。

Codec公开创建入口唯一见A.3：`Asun.Modules.RoiGeometry.Serialization.RoiGeometryCodec` 是 public sealed partial具体类，公开无参数 `RoiGeometryCodec()`，实现既有 `IRoiGeometryCodec.Encode/Decode`，两方法参数顺序/返回值/默认token保持不变。它属于§8.3已有Serialization工程/DLL，只引用已有Core与.NET 10 BCL（System.Text.Json、System.Collections.Immutable、SHA256、Stopwatch）；不新加DLL、DI容器、文件库、DevExpress/HALCON或产品依赖。构造只创建实例，不验证外部资料、不启动Task/线程/计时器、不Open编辑会话、读文件或持有native资源；无Dispose/Drain/Close要求。实例不保存最后Profile/输入/结果、没有OperationId表或可变静态缓存；OperationId是本次诊断身份，不是编辑事务幂等键，同ID重复纯值调用重新计算，不改变Core/Owner事实。

既有Core校验的实现复用边界：Core的Open/Validate与Codec已知v1几何校验共用Core工程内同一纯值校验器，不在Serialization复制§3数值/拓扑/约束/支持域谓词。实现落点固定为Core内部 `Asun.Modules.RoiGeometry.RoiSnapshotValidator`（internal static纯函数类，无可变静态字段），唯一内部签名为 `internal static RoiValidationResult Validate(RoiValidationRequest request, CancellationToken cancellationToken)`；无会话、历史或资源句柄，参数/预算完全来自request，按A.1 Validate规则处理。Core仅向已有 `Asun.Modules.RoiGeometry.Serialization` 程序集授此内部实现的友元访问，声明 `InternalsVisibleTo("Asun.Modules.RoiGeometry.Serialization")`，其它内部不成为消费者可调用的公共API；正式签名程序集沿同发布闭包配置友元公钥。Core Factory/实例Validate同样调用这一内部实现；Codec以当前operationId/snapshot/profile/原deadline构造既有RoiValidationRequest并直接调用上述纯值校验，传同一token，失败沿用Errors；成功才编码或返回DraftImport。不重置期限，不为Encode/Decode另Open隐式Core再遗留Owner；ReadOnlyUnknown没有可解释Snapshot，不能调用已知几何校验后声称已验证未知格式。本段固定内部复用落点，未创建代码，未声称现有工程中已存在该类。外部消费者仍仅使用A.1 Factory/Validate和A.3 Codec公开入口。

每次调用的边界固定如下：

- `operationId`遵守§3.1；snapshot/profile非null，bytes非default；合法Empty bytes作为损坏JSON拒RG-012，不与default bytes的RG-001混用。Profile全部字段按§3.3/A.1校验，Hash只核格式/来源声明，不由Geometry Codec重算Profile.Hash。Frame/单位按已知几何/Profile逐字段核；未知payload仍按§8.2整份只读，不猜Frame。没有文件名、格式推断、默认Profile、外部服务或隐式单位转换。
- 唯一前检顺序：参数结构/身份/Profile范围及deadline Frequency/Timestamp形状→token取消/单调到期→Encode完整几何前检或Decode有界UTF-8/JSON/版本前检→§8.2规范编码/验证→发布结果前再核token/deadline。结构坏优先RG-001（非finite RG-002、Frame不符RG-005）；结构合法且token已取消RG-009；仅执行期限到期RG-016；两者同时可记录，但主码RG-009。几何/损坏/资源错误沿既有码，不改Decode未知版本规则或任何正式Schema。
- 运行中每个节点/环/字段、每批顶点/段对和字节批核token/deadline；批元素数不超过Profile.CheckBatchSize。System.Text.Json逐token读取，MaxJsonDepth显式设为Profile上限，避免一次无界整文反序列化。输出/原件hash按有界增量块计算，长字符串先按UTF-8字节计预算再分块处理，不能绕检查点。取消是协作检查，同步方法返回前临时工作已经退出；不发后台工作、不返回半份Bytes/Snapshot成功，不靠外层WaitAsync宣称执行结束。
- 每次调用独立工作区，工作/输出/输入暂持/UTF-8缓冲/未知原bytes拷贝分别按Profile.MaxWorkingBytes、MaxOutputBytes、MaxSerializedBytes及计数/深度限额预约，checked长度后分配；取消/异常/失败均清本次临时工作；正常输入失败和已捕获计算/分配异常按既有RG-011/012等返回错误，hash/reader/buffer退出finally时不覆盖首个业务错误，不清理其它并发调用的工作区。调用者强持输入ImmutableArray/几何/配置，不能借底层可变数组绕immutable约束；成功Encode.Bytes、Decode.Snapshot/RawPayload是不依赖实例寿命的不可变托管值，由接收Host拥有，无native lease。Codec不缓存或保留输出，不释放调用者输入。
- 同一个Codec可由不同线程同时调用；无Dispatcher/STA要求，跨调用不共享可变预算/取消源/输入结果。Profile预算是**每次调用**的上限，不是进程并发或总内存承诺；Host按§10.1根槽/总预约限制并发，原同步调用若被放进Task则该Task/输入/实例由原Owner强持直至退出。不同Frame/Profile可并行，取消A不影响B；无需为了创建Codec等待客户或程序集外部条件。
- Encode任何失败：Bytes=Empty、Sha256为空字串、Errors非空。Decode非法/取消/超期：State=Rejected、Snapshot=null、RawPayload=Empty、RawSha256为空字串、Errors非空，调用者保留原bytes；已知v1成功仍DraftImport，未知合法载荷仍ReadOnlyUnknown并在预算内保留完整原bytes/hash。已完成成功返回后晚取消不改该值；结果本身不证明落盘、生产用途或物理资格。

无UI最小消费（一行构造+Encode/Decode；c沿§10.1完整公开Pixel Host配置，两个独立ID/新期限，失败显式停止）：

```csharp
var c = RoiHostExamples.HostCases.Pixel(); IRoiGeometryCodec codec = new Asun.Modules.RoiGeometry.Serialization.RoiGeometryCodec(); var e = codec.Encode("pixel.codec.encode.1", c.Initial, c.Profile, RoiHostExamples.HostCases.Deadline(c.OperationTimeout), CancellationToken.None); if (!e.Errors.IsEmpty) throw new InvalidOperationException(e.Errors[0].Code); var d = codec.Decode("pixel.codec.decode.1", e.Bytes, c.Profile, RoiHostExamples.HostCases.Deadline(c.OperationTimeout), CancellationToken.None); if (d.State != RoiDecodeState.DraftImport || d.Snapshot is null || !d.Errors.IsEmpty) throw new InvalidOperationException("Codec decode rejected");
```

宿主using为 `Asun.Modules.RoiGeometry.Serialization`、System、Threading；§10.1 HostCases放消费宿主本身，并非要求引用Core.Tests程序集。改用HostCases.Metric得到mm/不同几何同一路线。上述没有Core会话/持久化副作用；需要编辑时，Decode的DraftImport Snapshot由Host显式传A.1 `new RoiGeometryFactory().Open(...)` 并沿§10.1根Owner关闭，不能Codec自动Open或覆盖旧文档。一行只是公开API装配示例，采用与A.3接口完全相同参数，无using/await using释放Codec，不代替已批准Core Host，也不表示已运行。诊断异常由消费Host映射资源Key后呈现，不把示例技术异常文字直接交操作者。

旧 `.roi` 二进制**只读来源转换**，不使用 BinaryFormatter 反序列化未知文件。已提供且有文档公开字段的旧格式由隔离 import adapter 解析；缺来源版本/公开字段定义返回 ReadOnlyUnknown，不猜 TypeId/ShapeIndex/10 个字符串。不得写回客户原件；宿主确认迁移后新 ID、Frame/Unit、未知原字节引用保持。

### 8.3 组合与交付切片

| 切片 | namespace / 唯一计划工程（同本模块根） | 无 UI 消费与独立门 |
|---|---|---|
| CoreSlice-01 | `Asun.Modules.RoiGeometry`；已绑定 Core/test 工程 | 几何文档、typed 编辑/历史/生命周期；不依赖其余 DLL |
| Interaction-01 | 同 Core namespace/工程；同 Core.Tests | Headless HitTest/多选/约束/索引，不含 Pointer/UI 类型 |
| Codec-01 | `Asun.Modules.RoiGeometry.Serialization`；`src/Modules/roi-geometry/Asun.Modules.RoiGeometry.Serialization/Asun.Modules.RoiGeometry.Serialization.csproj`，对应 `tests/Modules/roi-geometry/Asun.Modules.RoiGeometry.Serialization.Tests/…Tests.csproj` | 只引用 Core，bytes 输入输出、schema/迁移/损坏测试 |
| Spatial-01 | 同 Core namespace/工程；Core.Tests 的 Spatial 类 | 3D Box/Sphere/PlanarPrism 点包含；点云只经公开端口，无自建重建/工作台 |
| HALCON-01 | `Asun.Modules.RoiGeometry.AsunImage`；同模块根 `Asun.Modules.RoiGeometry.AsunImage/…csproj`，测试同名 `.Tests` | 只引用 Core 和现有 AsunImage；上述 operators/Golden/tsp/native 资格 |
| WPF-01 | `Asun.Modules.RoiGeometry.Wpf`；同模块根 `Asun.Modules.RoiGeometry.Wpf/…csproj`，对应 `.Wpf.Tests` | 引用 Core/已批准 viewport 公共契约与本机 DevExpress25.2.3；不得包含图像引擎或测量工作台流程 |
| HostCommit-01 | 本模块仅定义附录 A.4 端口；宿主实现另行接收 | 权限/持久化/C-03/C-04 产品映射由宿主 Owner；不能阻断纯 Core/Codec/Interaction |

`.Tests` 完整规则为 `tests/Modules/roi-geometry/<程序集>.Tests/<程序集>.Tests.csproj`，所有新工程 net10.0（WPF 为 net10.0-windows/UseWPF），不自动创建空工程。允许实施路径仅被接收切片对应工程/test 目录；本轮只修改本指导。既有视口/测量工作台/坐标/共享契约改动由主会话串行安排，禁止复制其 VM/算法/私表到本模块。

DLL 随 API/Codec/Profile 版本发布，公开类型 nullable/enum/错误语义变化视为破坏版本；v0.2→v0.3 的创建/请求/Receipt 改变为不兼容设计修订，未有实现消费者，不称兼容升级。发布包包含 DLL/依赖清单/契约版本/测试适用范围/回退包；Core、Codec 可单独引用构建测试。最小 Host 不用平台 Shell；第二消费者和真实 WPF/HALCON 资格分别接收，不用安装/授权检查挡开发。

## 9. WPF-01 可嵌入 ROI 编辑器

### 9.1 操作流程与真实控件

不另建测量工作台/Shell。独立 `RoiEditorControl` 是可嵌入控件，宿主给 Core、viewport 公开适配、只读目标关联摘要、授权命令能力、语言/主题；操作全部调用同一 Core/Interaction，Core 不依赖 WPF。工作流：选择节点→看原几何/单位/来源→绘制或参数编辑→差异预览→应用到草稿→宿主显式保存。`应用`只写内存草稿；`保存`是宿主命令，未装配时不出现，不假装已持久化。

1920×1080 固定验证 viewport；扣除实际任务栏/边框/标题/状态后测 client。顶部单行44 DIP（选取、绘制、平移/旋转、撤销/重做、应用/取消）；底部28 DIP（Frame/Unit、revision、候选/近似/缺口、坐标和排空状态）。中区 `DockLayoutManager + LayoutGroup + LayoutPanel`：左240 DIP ROI树，右320 DIP参数，中央影像至少 client 宽60%，底部差异区默认收起、展开最大中区高18%；宽度不足先自动收右高级页，中央不压缩成缩略图，关键应用/取消始终可见。宿主 viewport 占中央，2D/3D 切换是现有视口投影，不拉新 window 或复制渲染器。

- 左 `TreeListControl/TreeListView`：KeyFieldName=`RowKey`、ParentFieldName=`ParentRowKey`（唯一typed行投影键，映射规则见§9.5），树列为形状图标/名称、可见、锁；Group→ROI→Outer/Hole 层次，所有行绑定稳定 ID。搜索/筛选只隐藏投影，不删 Geometry/改变算法 Enabled。虚拟化行/延迟子级投影，选择变化→viewport 高亮→右属性/底差异一次联动，使用 SelectionSet 消除回流循环。
- 右 `PropertyGridControl.SelectedObject/SelectedObjects`：typed 编辑代理，按“几何/坐标/约束/来源”分组，常用字段先展开，高级误差/栅格政策折叠；多选不同值显示混合态，不拿第一项覆盖其它项。输入先字符串草稿，`-`/`.`/指数未完显示“未完成”，不向 Core 发 double.NaN。显式应用生成一个批量命令，失败保留文本/caret/原 Snapshot。
- 差异区 `GridControl`：每 Node 的前/后尺寸、单位、约束、组件/洞变化及错误；点行定位 viewport 和 tree，不用图表代替无定义数值。诊断趋势仅由宿主诊断页消费，本 ROI 编辑器不凭空加 Chart。
- `FlyoutControl`（正确 namespace `DevExpress.Xpf.Editors.Flyout`）仅用于冲突详情/多候选列表，不能把重要命令藏其中；`BarItem.SuperTip`/`SuperTip`说明预算、近似和安全恢复，键盘也能打开。主题使用控件根 attached `ThemeManager.ThemeName`，不改 ApplicationThemeName 全局；宿主切换语言/主题保持草稿、选择、文本与焦点。Dock layout 只读写宿主提供的可信 stream，官方明确反序列化安全限制，不加载 ROI 用户文件作为布局。

### 9.2 视觉层级与交互

仅用宿主主题字体/色/图标 token：主体14 DIP、辅助12 DIP，4/8/12 DIP间距；影像原色不随主题，选择边加轮廓/handle而不遮缺陷，Locked 灰锁、错误橙/红图标配文字、近似虚线加“近似”，不以颜色独占信息。Hover/选中80～120ms非阻塞淡入，拖拽/采样/3D排空禁止会延迟反馈的动画；ReduceMotion可关。图标用项目批准向量资源，没有设计资源不从字符/随机 emoji 拼工业界面。

Ctrl+Z/Ctrl+Y 在视口/树执行 Core Undo/Redo，焦点在文本框时只处理该文本历史；Esc 先取消当前绘制/拖拽，后关闭 flyout，不抹已应用草稿；Enter 仅在有效 ≥3 顶点 polygon/合法参数时完成，输入未完保持错误。Delete 先在差异区展示引用/Group影响，确认才产生一个命令；方向键的物理步长来自宿主编辑 Profile，Shift步长倍数明确显示，不固定为像素常量。Ctrl/Shift多选、Alt循环全部 HitTest 候选、Tab按树→视口→属性→应用→差异的任务顺序；AutomationId 固定 `Roi.Tree`、`Roi.Viewport`、`Roi.Parameters`、`Roi.Apply`、`Roi.Cancel`、`Roi.Diff`，行/handle以Node/Vertex ID后缀。

PointerMove 每帧合并最新输入，同一手势只建临时候选；鼠标释放/Enter只 Apply 一次、一个历史单元。文本解析使用当前culture，Core/Codec使用Invariant；语言切换不重新解析已 typed 数值。宽文本换行到两行/tooltip、单位列不截断；错误用“发生了什么＋下一步”，不展示营销或AI口吻。布局锁定同1920×1080，按实际DPI使用DIP并覆盖三语长文本；不改变用户显示设置、不跑额外分辨率矩阵。

### 9.3 状态与三语资源

| Key | zh-CN / zh-TW / en-US |
|---|---|
| Roi.Apply / Roi.Cancel | 应用 / 套用 / Apply；取消 / 取消 / Cancel |
| Roi.Undo / Roi.Redo | 撤销 / 復原 / Undo；重做 / 重做 / Redo |
| Roi.NoSelection | 未选择 ROI / 尚未選取 ROI / No ROI selected |
| Roi.InputPending | 输入未完成 / 輸入未完成 / Incomplete input |
| Roi.Conflict | 草稿已更新，请刷新 / 草稿已更新，請重新整理 / Draft changed. Refresh |
| Roi.Constraint | 不满足约束，请检查参数 / 不符合約束，請檢查參數 / Constraint failed. Check parameters |
| Roi.Approximate | 近似 / 近似 / Approximate |
| Roi.Draining / Roi.DrainUnknown | 正在结束 / 正在結束 / Closing；尚未结束，请稍候 / 尚未結束，請稍候 / Still closing. Wait |
| Roi.ReadOnlyUnknown | 格式未识别，可导出原文件 / 格式未識別，可匯出原檔 / Unknown format. Export original |
| Roi.SupportMissing | 数据不完整，请检查来源 / 資料不完整，請檢查來源 / Missing data. Check source |

所有标题、参数/单位、状态、代码表RG错误/Recovery和UIA Name在三语资源中覆盖，Key=`Roi.Error.<Code>`/`Roi.Recovery.<Code>`；错误参数只传类型化路径/ID/数值，UI不得拼 raw exception。产品命令权限由宿主给，Core Locked 不代替权限。Draining/DrainUnknown 时禁用编辑、应用和宿主保存，保留查询/差异；关闭显示 pending 操作，可安全等待或宿主隔离，不能“强制关闭并标已释放”。过期 Preview 显示“预览已过期，请重算”，禁止采纳；多个候选不默认选第一个后应用。

三语资源补齐是Wpf DLL实施输入，不等真实语言长度验收。Key后缀为下表首列，资源类为私有Presenter.Text/内置ResourceManager，变更Culture只重绑定文本，不重解析已typed数值；未列动态ID只格式化参数，不当标签。`Roi.Field.<后缀>`按同一词表组合路径：Center/U/V/Start/Sweep/Closed/Length/Angle/Width/Height/Pivot/ScaleX/ScaleY/Vertices/Components/Holes/Visible/Locked/Constraint/Source/Revision/Frame/Unit/Tolerance/MaxDeviation/Representation/Method/Status/Selection/Coordinates对应下表，X/Y/Z轴直接ASCII，单位Pixel→px、Millimeter→mm、Micrometer→µm（单位符号不翻译）。Unknown/Partial/Complete显示来源声明，不由UI补Complete。

| Key后缀/含义 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title / Nodes / Parameters / Diff / Image | ROI 编辑 / ROI 列表 / 参数 / 差异 / 影像 | ROI 編輯 / ROI 清單 / 參數 / 差異 / 影像 | ROI editor / ROI list / Parameters / Changes / Image |
| Select / Draw / Move / Rotate / Scale / Refresh | 选取 / 绘制 / 平移 / 旋转 / 缩放 / 刷新 | 選取 / 繪製 / 平移 / 旋轉 / 縮放 / 重新整理 | Select / Draw / Move / Rotate / Scale / Refresh |
| Point / Segment / Polyline / Polygon / Circle / Ellipse / Rectangle / Arc / Group | 点 / 线段 / 折线 / 多边形 / 圆 / 椭圆 / 矩形 / 圆弧 / 分组 | 點 / 線段 / 折線 / 多邊形 / 圓 / 橢圓 / 矩形 / 圓弧 / 群組 | Point / Segment / Polyline / Polygon / Circle / Ellipse / Rectangle / Arc / Group |
| Center / U / V / Start / Sweep / Closed | 中心 / 半轴 U / 半轴 V / 起始角 / 扫角 / 闭合 | 中心 / 半軸 U / 半軸 V / 起始角 / 掃角 / 閉合 | Center / Axis U / Axis V / Start angle / Sweep / Closed |
| Length / Angle / Width / Height / Pivot / ScaleX / ScaleY | 长度 / 角度 / 宽度 / 高度 / 旋转中心 / X 缩放 / Y 缩放 | 長度 / 角度 / 寬度 / 高度 / 旋轉中心 / X 縮放 / Y 縮放 | Length / Angle / Width / Height / Pivot / X scale / Y scale |
| Vertices / Components / Holes / Visible / Locked / Constraint | 顶点 / 组件 / 孔洞 / 可见 / 锁定 / 约束 | 頂點 / 組件 / 孔洞 / 可見 / 鎖定 / 約束 | Vertices / Components / Holes / Visible / Locked / Constraint |
| Source / Revision / Frame / Unit / Tolerance / MaxDeviation | 来源 / 修订 / 坐标系 / 单位 / 容差 / 最大偏差 | 來源 / 修訂 / 座標系 / 單位 / 容差 / 最大偏差 | Source / Revision / Frame / Unit / Tolerance / Maximum deviation |
| Representation / Method / Status / Selection / Coordinates | 表示 / 方法 / 状态 / 选择 / 坐标 | 表示 / 方法 / 狀態 / 選取 / 座標 | Representation / Method / Status / Selection / Coordinates |
| Unknown / Partial / Complete / Mixed | 未知 / 部分 / 完整 / 混合值 | 未知 / 部分 / 完整 / 混合值 | Unknown / Partial / Complete / Mixed values |
| Add / Remove / Reparent / ExportOriginal / Recompute | 添加 / 移除 / 移到分组 / 导出原件 / 重算 | 新增 / 移除 / 移至群組 / 匯出原檔 / 重算 | Add / Remove / Move to group / Export original / Recompute |
| DeletePrompt / Permission / DisplayBudget | 删除所选 ROI？请检查引用 / 无编辑权限 / 显示超出预算，请缩小视野 | 刪除所選 ROI？請檢查引用 / 無編輯權限 / 顯示超出預算，請縮小視野 | Delete selected ROI? Check references / Editing is not permitted / Display budget exceeded. Narrow the view |
| DisplaySimplified / ProjectionFailed / Refresh | 轮廓已简化显示 / 显示更新失败，刷新重试 / 刷新 | 輪廓已簡化顯示 / 顯示更新失敗，重新整理後重試 / 重新整理 | Contour display simplified / Display update failed. Refresh and retry / Refresh |
| FixedLength / Coincident / Horizontal / Vertical / EqualLengths / AspectRatio | 固定长度 / 重合 / 水平 / 垂直 / 等长 / 宽高比 | 固定長度 / 重合 / 水平 / 垂直 / 等長 / 寬高比 | Fixed length / Coincident / Horizontal / Vertical / Equal lengths / Aspect ratio |
| PreviewReady / Completed / PreviewStale / RetryClose | 预览就绪 / 已应用到草稿 / 预览已过期，请重算 / 重试关闭 | 預覽就緒 / 已套用至草稿 / 預覽已過期，請重算 / 重試關閉 | Preview ready / Applied to draft / Preview is stale. Recompute / Retry close |

Error/Recovery资源用§5完整Code作后缀，以下每行冻结“错误；恢复”两字符串，不把Errors.Diagnostics拼进UI：

| Code数字（对应§5具名码） | zh-CN错误；恢复 | zh-TW错误；恢复 | en-US错误；恢复 |
|---|---|---|---|
| 001 | 参数无效；检查标记字段 | 參數無效；檢查標記欄位 | Invalid parameter; Check highlighted fields |
| 002 | 数值无效；输入有限数值 | 數值無效；輸入有限數值 | Invalid number; Enter a finite value |
| 003 | 几何退化；检查长度或矩阵 | 幾何退化；檢查長度或矩陣 | Degenerate geometry; Check lengths or matrix |
| 004 | 轮廓无效；检查交叉和孔洞 | 輪廓無效；檢查交叉和孔洞 | Invalid contour; Check crossings and holes |
| 005 | 坐标系不匹配；使用明确坐标转换 | 座標系不符；使用明確座標轉換 | Frame mismatch; Apply an explicit coordinate mapping |
| 006 | 此表示不支持该操作；选择支持的表示 | 此表示不支援此操作；選擇支援的表示 | Unsupported operation; Choose a supported representation |
| 007 | 无法满足误差预算；检查误差和坐标范围 | 無法符合誤差預算；檢查誤差和座標範圍 | Error budget cannot be met; Check error and coordinate bounds |
| 008 | 草稿或请求冲突；刷新后合并改动 | 草稿或請求衝突；重新整理後合併變更 | Draft or request conflict; Refresh and merge changes |
| 009 | 操作已取消；等待结束后重试 | 操作已取消；等待結束後重試 | Operation cancelled; Wait for completion before retrying |
| 010（仅旧诊断） / 016 | 操作已到期；等待结束后用新期限重试 | 操作已到期；等待結束後用新期限重試 | Operation expired; Wait, then retry with a new deadline |
| 011 | 资源预算不足；缩小范围或释放闲置资源 | 資源預算不足；縮小範圍或釋放閒置資源 | Resource budget exceeded; Reduce scope or release idle resources |
| 012 | 文件内容无效；保留原件并检查格式 | 檔案內容無效；保留原檔並檢查格式 | Invalid content; Keep the original and check its format |
| 013 | 会话已关闭；打开新会话 | 工作階段已關閉；開啟新工作階段 | Session closed; Open a new session |
| 014 | 视觉处理失败；查看诊断并等待释放 | 視覺處理失敗；查看診斷並等待釋放 | Vision processing failed; Check diagnostics and wait for release |
| 015 | 操作结果未确认；查询原操作 | 操作結果未確認；查詢原操作 | Outcome unconfirmed; Query the original operation |
| 017 | 不满足约束；检查引用和参数 | 不符合約束；檢查引用和參數 | Constraint failed; Check references and parameters |
| 018 | 撤销记录不足；刷新当前草稿 | 復原記錄不足；重新整理目前草稿 | History unavailable; Refresh the current draft |
| 019 | 格式未识别；只读导出原件 | 格式未識別；唯讀匯出原檔 | Unknown format; Export the original without changes |
| 020 | 来源或预览已更新；刷新并重算 | 來源或預覽已更新；重新整理並重算 | Source or preview changed; Refresh and recompute |

SuperTip的内容由这些资源组合：“应用”说明只改草稿、“近似”显示Profile上限/当前已证界与单位、“关闭未完成”显示pending数与RetryClose、“栅格”显示Origin/Step/方法及不可声称连续精确。三语参数列表允许自然换行，不裁Recovery命令；PropertyGrid扩展culture若缺任何模块Key拒启动该culture，默认三语缺Key为测试失败，不静默掉回中文。

### 9.4 25.2.3 API 依据与未测限制

本轮 dxdocs 未提供、无匹配 WPF skill，网站 `docs.devexpress.com/WPF` 请求403；改读本机 **25.2.3 官方 XML**（§16.3）。已核 DockLayoutManager/LayoutGroup/LayoutPanel/SaveLayoutToStream/RestoreLayoutFromStream、TreeListControl/TreeListView.KeyFieldName/ParentFieldName、PropertyGrid.SelectedObject/SelectedObjects、Flyout.FlyoutControl、SuperTip/BarItem.SuperTip、BarContainerControl/BarButtonItem、ThemeManager.Get/SetThemeName。0.4.4-prep进一步实际核对DataControlBase.ItemsSource/SelectedItems/SelectionMode、MultiSelectMode.MultipleRow、TreeListControlBase.SelectionChanged/GridControl.SelectionChanged、TreeDerivationMode.Selfreference、BarContainerControl.Bars与BarItem.SuperTip；事件/属性绑定按§9.5固定，不把未编译当缺少设计；这不触发安装或授权门。真实 WPF控件组合、UIA、Dispatcher关闭、三语长度、DPI与大图性能仍须 WPF-01测试证明，本文不是UI运行证据。

### 9.5 控件装配、typed手势与资源覆盖

本节只确定已规划的编辑任务，不新增Shell/生产保存/图像导航/标定算法。根控件通过A.6 Attach插入借用的Viewport.View；内部唯一编辑代理与Core Preview/Apply共享校验。以下是Wpf工程 `RoiEditorControl` 内容骨架，真实命令/三语Resource在该DLL内初始化，DataContext是本控件私有Presenter，不能依赖产品VM或全局ServiceLocator。DevExpress名称及选择事件按本机25.2.3 XML，匹配版本dxdocs不可用时不编造API；本骨架仍需真实编译/UI验证。

```xml
<UserControl x:Class="Asun.Modules.RoiGeometry.Wpf.RoiEditorControl"
 xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
 xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
 xmlns:dxd="http://schemas.devexpress.com/winfx/2008/xaml/docking"
 xmlns:dxg="http://schemas.devexpress.com/winfx/2008/xaml/grid"
 xmlns:dxprg="http://schemas.devexpress.com/winfx/2008/xaml/propertygrid"
 xmlns:dxb="http://schemas.devexpress.com/winfx/2008/xaml/bars">
 <Grid>
  <Grid.RowDefinitions><RowDefinition Height="44"/><RowDefinition Height="*"/>
   <RowDefinition Height="28"/></Grid.RowDefinitions>
  <dxb:BarContainerControl Grid.Row="0">
   <dxb:BarContainerControl.Bars>
   <dxb:Bar><dxb:BarButtonItem Content="{Binding Text.Select}" Command="{Binding SelectCommand}"/>
    <dxb:BarButtonItem Content="{Binding Text.Draw}" Command="{Binding DrawCommand}"/>
    <dxb:BarButtonItem Content="{Binding Text.Rotate}" Command="{Binding RotateCommand}"/>
    <dxb:BarButtonItem Content="{Binding Text.Undo}" Command="{Binding UndoCommand}"/>
    <dxb:BarButtonItem Content="{Binding Text.Redo}" Command="{Binding RedoCommand}"/>
    <dxb:BarButtonItem Content="{Binding Text.Apply}" Command="{Binding ApplyCommand}"/>
    <dxb:BarButtonItem Content="{Binding Text.Cancel}" Command="{Binding CancelCommand}"/>
   </dxb:Bar>
   </dxb:BarContainerControl.Bars>
  </dxb:BarContainerControl>
  <dxd:DockLayoutManager Grid.Row="1">
   <dxd:LayoutGroup Orientation="Vertical">
    <dxd:LayoutGroup Orientation="Horizontal">
     <dxd:LayoutPanel Caption="{Binding Text.Nodes}" ItemWidth="240">
      <dxg:TreeListControl x:Name="RoiTree" ItemsSource="{Binding Rows}" SelectionMode="MultipleRow"
       AutomationProperties.AutomationId="Roi.Tree">
       <dxg:TreeListControl.View><dxg:TreeListView TreeDerivationMode="Selfreference"
        KeyFieldName="RowKey" ParentFieldName="ParentRowKey"/></dxg:TreeListControl.View>
      </dxg:TreeListControl>
     </dxd:LayoutPanel>
     <dxd:LayoutPanel Caption="{Binding Text.Image}" ItemWidth="*">
      <ContentControl x:Name="ViewportSlot" AutomationProperties.AutomationId="Roi.Viewport"/>
     </dxd:LayoutPanel>
     <dxd:LayoutPanel Caption="{Binding Text.Parameters}" ItemWidth="320">
      <dxprg:PropertyGridControl x:Name="RoiParameters" SelectedObjects="{Binding ParameterProxies}"
       AutomationProperties.AutomationId="Roi.Parameters"/>
     </dxd:LayoutPanel>
    </dxd:LayoutGroup>
    <dxd:LayoutPanel Caption="{Binding Text.Diff}" Visibility="{Binding DiffVisibility}">
     <dxg:GridControl ItemsSource="{Binding Differences}" AutomationProperties.AutomationId="Roi.Diff">
      <dxg:GridControl.View><dxg:TableView/></dxg:GridControl.View>
     </dxg:GridControl>
    </dxd:LayoutPanel>
   </dxd:LayoutGroup>
  </dxd:DockLayoutManager>
  <TextBlock Grid.Row="2" Text="{Binding StatusText}" VerticalAlignment="Center"/>
 </Grid>
</UserControl>
```

窗口几何按固定1920×1080**物理验证视口**，DIP尺寸=物理像素/实际DPI.Scale，WorkArea同DIP；不要把1920 DIP当高DPI的1920像素。client宽W时先保留240/320 DIP侧板；若`W−560<0.6W`先隐藏右参数板，由顶部Parameters命令/F4暂开flyout（参数应用仍显式），再必要时左树变可收起240 DIP抽屉；中央保持0.6W以上，不隐应用/取消。两侧由用户拖动后的可信布局仍受同中央最小宽约束，布局保存是宿主已有可信stream用途，不接用户ROI文件反序列化。差异区展高<=中区18%，调整动画ReduceMotion关闭，ThemeManager只作用本控件。构造内生成DrawingImage矢量符号（点/折线/闭环/锁/旋转/撤销箭头），用路径/几何资源加三语ToolTip/SuperTip，不用emoji或下载替代设计；选中/错误颜色来自Host主题，文字/轮廓保证对比。

树RowKey固定为类别+原ID的长度前缀编码（仅私有键，不写Core或Codec）：Node=`n.<len>.<NodeId>`，Component/Ring/Vertex在此前缀后加 `.c/.r/.v.<len>.<Id>`；ParentRowKey按真实Group/组件/环父关系，OwnerNodeId始终实际Node.Id，任何行选择映射成去重Ordinal SelectionSet。`TreeListControlBase.SelectionChanged`读取控件SelectedItems映射OwnerNodeId，SetSelection同值不回流；内部标志仅防投影循环，不作权限。GridControl.SelectionChanged取差异NodeId同路；PropertyGrid SelectedObjects只能是本Presenter typed草稿代理，禁止直接绑定immutable Node或产品对象。选择变化先保存文本草稿引用→取消旧Preview等待实际退出→刷新新代理/overlay，几何revision不增；各selection/键盘事件Detach成功时解除，不使用静态事件。

手势与字段规则冻结（viewport数学坐标通过§3精确可逆投影获得，所有创建先向Host.NewId取得Node及所需Component/Ring/Vertex ID）：

| 任务 | 本控件内部工具状态与typed处理 | 完成/拒绝/恢复 |
|---|---|---|
| 选取/框选 | 初始Select；Down HitTest完整候选，Ctrl切换集合、Shift并集、Alt循环；空处拖框按左→右Contains/右→左Crossing，固定原ViewRevision | 多候选Flyout可键盘上下/Enter选；没有确定选择不编辑；新ViewRevision或Core revision取消旧手势，重算 |
| 点/线/折线/多边形 | Draw下拉是本控件工具选择（Point/Segment/Polyline/Polygon）；Point单点击；Segment两点；Polyline逐点击；Polygon逐点击后Enter闭合，不重复写首点 | Enter至少2/3个点，所有长度/严格环/锁/预算Core验证；Esc取消尚未Apply的整份手势；DoubleClick等价Enter不再加重复点；洞/组件必须显式选父组件后在参数列表增删，先保留草稿 |
| 圆/椭圆/矩形/弧 | Circle Down为center，Up距离给r，U=(r,0)、V=(0,r)、Start0、Sweep2π、Closed=true；Ellipse/Rectangle拖对角框，center=(a+b)/2、U=(abs(dx)/2,0)、V=(0,abs(dy)/2)。Arc先同Ellipse轴构造，输入Start0/Sweepπ/2作为明确软件起始值、Closed=false，参数页必显示角域可修改 | MinLength/finite/CAS照Core，不修零尺寸。旋转矩形/椭圆由下一行旋转工具或方位角字段完成；所有起始值只为编辑草稿不是生产默认参数 |
| 平移/旋转/缩放/handle | Translation=当前点−Down点，完整选中叶一个Affine；Rotation以当前选择AABB中心或用户显式Pivot为p，theta=atan2(Down/Current相对p)的有符号差，T=Translate(p)*Rotate(theta)*Translate(−p)；Scale显式X/Y数值（非零有限）、镜像负值允许，通过同Pivot组成T | 位于Pivot长度<MinLength拒旋转，Shift只使角度为15°软件格点并显示；不把屏幕顺时针当数学顺时针。Center handle平移；Curve U/V handle替换相应半轴；Rectangle handle只沿原轴投影改长度、不剪切，幅度<MinLength拒。显式一般Affine会剪切Rectangle为Polygon，约束按§4拒/移除，不隐式正交化 |
| 参数/批量/约束/层次 | 参数名Center.X/Y、U.X/Y、V.X/Y、Start/Sweep（界面度→一次转换弧度）、Closed、Vertices、Components/Holes；Polyline/Polygon列表按稳定ID，锁/可见用Replace；Reparent单独命令；约束用§4类型与引用；多选混合值只有用户明确改的字段进入每个Replace | 当前Culture字符串解析，空/-/小数/指数未完不构造非法double，保留caret；同批跨Frame拒；改变Node类型不能用Replace偷换；结构/单位不猜转换；单个批量失败全部原值不变 |
| Undo/Redo/Delete/应用 | Undo/Redo从Core Query深度启用，同步Apply在后台已持原Task运行；Delete先列引用/锁/子树差异，确认后新IDApply；参数编辑先PreviewReady与当前Adoption核再Apply新ID | Up/Enter/Apply同手势只一个Apply/历史；取消/超时/CAS冲突保留文本与错误、Query当前基线后明确重算；不延长同IDdeadline、不在收到旧成功投影后再发布 |

闭Curve变开放/反向扫角必须按§3合法值用户确认，不补遮挡或拟合图像。批量阵列/复制不隐藏模式：Host预生成完整ID映射，以同一次Create批执行，UI只显示此批差异；Node.Source若有仍保留输入出处，派生误差不能假装旧来源上界继续有效。锁只编辑保护、CanEdit/CanSave及生产资格仍Host；UI不调设备/持久事务、不解释制程Enabled。

所有几何编辑/校验任务无UI也可由A.1～A.4同一typed输入计算；焦点、布局、display LOD与投影恢复属于Wpf/Bridge内部职责；ToolMode/代理/RowKey/Display LOD不进入共享契约。`Viewport.PublishOverlay`/`Host.Publish`若抛异常或false，控件捕获为本次投影Diagnostic，事实不回滚/不在锁内重入Host；记当前不可发送状态，保留最后已确认投影，下一次明确Refresh或Host恢复重发最新值，不能逐帧故障无限重试。外部Host.NewId异常发生在接纳前，草稿保持、报告诊断，不Reuse已用ID。所有入口/state setter的错误参数短拒后不改变原Attach；错线程抛既有InvalidOperationException，合法线程/无权限只禁命令，不给Core新的授权权威。

## 10. 最小无 UI Host 与同步/异步调用

### 10.1 两个完整 Core Host 与有限进程根

下列代码是未来 `.Core.Tests` 中的 BCL Exe 装配输入，放在宿主 namespace `RoiHostExamples`，**不是 Core DLL 新增公开契约**。引用 `Asun.Modules.RoiGeometry`，以及 System、Collections.Generic/Immutable、Diagnostics、Globalization、Linq、Security.Cryptography、Text、Threading/Tasks。两入口分别调用 `HostCases.Pixel()` / `HostCases.Metric()`；无需从外部补 `profile/timeout/token`、窗口或服务。以下数值是有界软件负载配置，非客户允差/节拍。业务成败、观察结束、cleanup 结果和资源归还四轴独立；异常保留原对象，不在 finally 抛 cleanup 异常覆盖它。

Profile 来源规约仅用于这两个 TestHost 配置，不更改模块/Profile生产编码：宿主显式写出下表代码中全部具名字段；`Hash` 列之外，按 A.1 `ValidationProfile` 声明顺序写值，Frame展开为 `id,unit,axes`；以 UTF-8 无 BOM 的 `RG-HOST-PROFILE-1\n` 加每个 scalar 的 `InvariantCulture` 十进制/enum 名字及 LF 结束行，double 用 R、TimeSpan 用 Ticks；Hash=该字节 SHA-256 小写hex。规约无客户字符串输入，生产宿主仍注入其已批准配置来源的 hash。`CloseTimeout` 是每次模块关闭的执行预算；Host另有独立观察预算，不能修改原操作 Deadline 或传已取消业务 token 给关闭。

```csharp
public sealed record HostCase(
    string Prefix, GeometrySnapshot Initial, ValidationProfile Profile,
    string NodeId, Affine2D Transform, TimeSpan OperationTimeout,
    TimeSpan ObservationTimeout, TimeSpan CleanupObservation);

public static class HostCases
{
    public static MonotonicDeadline Deadline(TimeSpan t)
    {
        if (t <= TimeSpan.Zero || t > TimeSpan.FromMinutes(1))
            throw new ArgumentOutOfRangeException(nameof(t));
        long delta = checked((long)Math.Ceiling(t.TotalSeconds * Stopwatch.Frequency));
        return new(checked(Stopwatch.GetTimestamp() + delta), Stopwatch.Frequency);
    }
    public static ValidationProfile Profile(RoiFrame f, bool metric)
    {
        var p = new ValidationProfile(
            Id: metric ? "host.metric.profile" : "host.pixel.profile", Revision: "1",
            Hash: new string('0', 64), Frame: f,
            MaxAbsCoordinate: metric ? 10000 : 1000000,
            MinLength: metric ? 0.000001 : 0.0001, MaxCondition: 1000000,
            MaxNodes: metric ? 128 : 256, MaxVertices: metric ? 8192 : 16384,
            MaxRings: 256, MaxComponents: 128, MaxCandidatePairs: 1000000,
            MaxWorkingBytes: metric ? 16777216 : 33554432,
            MaxOutputBytes: metric ? 4194304 : 8388608,
            MaxUndoSteps: 16, MaxUndoBytes: metric ? 4194304 : 8388608,
            MaxInFlight: 2, MaxPending: 2, MaxReceipts: 128, CheckBatchSize: 32,
            MaxCurveDeviation: metric ? 0.001 : 0.01,
            MaxTessellationVertices: 4096, MaxSerializedBytes: 1048576, MaxJsonDepth: 32,
            CloseTimeout: TimeSpan.FromSeconds(1), SpatialBasisTolerance: 0.0000001,
            MaxBackendWorkers: 1, MaxHalconParallelism: 1, MaxPointBlockSize: 4096,
            MaxRuns: 65536);
        object[] values = { p.Id, p.Revision, f.Id, f.Unit, f.Axes,
            p.MaxAbsCoordinate, p.MinLength, p.MaxCondition, p.MaxNodes, p.MaxVertices,
            p.MaxRings, p.MaxComponents, p.MaxCandidatePairs, p.MaxWorkingBytes,
            p.MaxOutputBytes, p.MaxUndoSteps, p.MaxUndoBytes, p.MaxInFlight, p.MaxPending,
            p.MaxReceipts, p.CheckBatchSize, p.MaxCurveDeviation, p.MaxTessellationVertices,
            p.MaxSerializedBytes, p.MaxJsonDepth, p.CloseTimeout.Ticks,
            p.SpatialBasisTolerance, p.MaxBackendWorkers, p.MaxHalconParallelism,
            p.MaxPointBlockSize, p.MaxRuns };
        string Scalar(object v) => v is double d ? d.ToString("R", CultureInfo.InvariantCulture)
            : v is IFormattable n ? n.ToString(null, CultureInfo.InvariantCulture) : v.ToString()!;
        var bytes = Encoding.UTF8.GetBytes("RG-HOST-PROFILE-1\n" +
            string.Join("\n", values.Select(Scalar)) + "\n");
        return p with { Hash = Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant() };
    }
    public static HostCase Pixel()
    {
        var f = new RoiFrame("camera.xy", GeometryUnit.Pixel, AxisConvention.ColumnRowPixelCenters);
        var n = new RoiNode("roi.circle", null, 0, true, false,
            new CurveShape(new(200,100), new(20,0), new(0,20), 0, 2*Math.PI, true),
            ImmutableArray<RoiConstraint>.Empty, null);
        return new("pixel", new("doc.pixel", 7, f, ImmutableArray.Create(n)),
            Profile(f, false), n.Id, new(1,0,5,0,1,-2),
            TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(3), TimeSpan.FromSeconds(2));
    }
    public static HostCase Metric()
    {
        var f = new RoiFrame("fixture.xy", GeometryUnit.Millimeter, AxisConvention.RightHandedPhysicalXY);
        var n = new RoiNode("roi.rectangle", null, 0, true, false,
            new RectangleShape(new(10,20), new(2,0), new(0,1)),
            ImmutableArray<RoiConstraint>.Empty, null);
        return new("metric", new("doc.metric", 0, f, ImmutableArray.Create(n)),
            Profile(f, true), n.Id, new(1,0,0.5,0,1,-0.25),
            TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(2));
    }
}
```

两个正常断言分别为：Pixel Preview中心(205,98)/revision7 → Apply revision8 → Undo中心(200,100)/revision9；Metric Preview中心(10.5,19.75)/revision0 → Apply revision1 → Undo中心(10,20)/revision2。Frame/Profile/hash不同，两个实例互不取消或排空。无 Source 只表明纯编辑。ID由每个Root登记时给出的 `pixel.<递增序号>` / `metric.<递增序号>` ticket派生 `.open/.session/.validate/.preview/.apply/.undo`，计数checked、失败不回收已给序号；节点身份来自两完整构造，不依赖屏幕/数组行号。这里 factory 为 A.1 的公开 `new RoiGeometryFactory()`，事件 sink明确null。

以下有界根对象由进程入口**在任何 Factory 前**构造；最多2个Owner槽、总预约128MiB。`ReservedBytes`覆盖 Profile工作/输出/历史上限、两份序列化缓冲和1MiB宿主固定元数据；模块自身请求墓碑/索引按§13计预算。此预约不是实测进程峰值。Root满时拒新工作，不能另开根绕额度或淘汰待恢复Owner。Root是显式实例，不是Core全局服务；foreground Thread强持Root，Root表强持Owner、原Task、Profile、CTS、Core与后续关闭Task，因此入口返回/观察到期/窗口暂隐藏均不丢Owner。

```csharp
internal interface IRecoveryOwner
{
    long ReservedBytes { get; }
    Task<bool> CloseOnceAsync(); // 每次有界；返回false保留原Owner，不能创建替代实例。
    TaskCompletionSource<bool> Released { get; }
}
internal sealed class RecoveryRoot
{
    private sealed class Entry(IRecoveryOwner owner)
    {
        public readonly IRecoveryOwner Owner = owner;
        public bool Retry; public Task<bool>? Sweep;
    }
    private readonly object gate = new();
    private readonly Dictionary<string, Entry> entries = new(StringComparer.Ordinal);
    private readonly Thread supervisor;
    private long next, bytes; private bool stopping;
    public RecoveryRoot()
    {
        supervisor = new Thread(Loop) { IsBackground = false, Name = "ROI.Host.Recovery" };
        supervisor.Start();
    }
    public string? Reserve(string prefix, IRecoveryOwner owner)
    {
        lock (gate)
        {
            if (stopping || next == long.MaxValue || entries.Count == 2 || owner.ReservedBytes <= 0 ||
                owner.ReservedBytes > 134217728 - bytes) return null;
            string id = prefix + "." + checked(++next).ToString(CultureInfo.InvariantCulture);
            entries.Add(id, new Entry(owner)); bytes = checked(bytes + owner.ReservedBytes);
            return id;
        }
    }
    // 返回true就是转交确认；登记Owner在此前已强持，并非现在才登记。
    public bool Handoff(string ticket, IRecoveryOwner owner)
    {
        lock (gate)
        {
            if (!entries.TryGetValue(ticket, out var e) || !ReferenceEquals(e.Owner, owner))
                return false;
            e.Retry = true; return true;
        }
    }
    public IRecoveryOwner? Query(string ticket)
    { lock (gate) return entries.TryGetValue(ticket, out var e) ? e.Owner : null; }
    public bool Retry(string ticket)
    {
        lock (gate) { if (!entries.TryGetValue(ticket, out var e)) return false;
            e.Retry = true; return true; }
    }
    public bool StopIfEmpty()
    {
        lock (gate) { if (entries.Count != 0) return false; stopping = true; }
        return supervisor.Join(TimeSpan.FromSeconds(1)); // 不Join无界等待。
    }
    private void Loop()
    {
        while (true)
        {
            lock (gate)
            {
                if (stopping) return;
                foreach (var pair in entries.ToArray())
                {
                    var e = pair.Value;
                    if (e.Sweep?.IsCompleted == true)
                    {
                        bool done = e.Sweep.IsCompletedSuccessfully && e.Sweep.Result;
                        if (e.Sweep.IsFaulted) _ = e.Sweep.Exception; // 观察，保留Owner诊断。
                        e.Sweep = null;
                        if (done)
                        {
                            entries.Remove(pair.Key); bytes -= e.Owner.ReservedBytes;
                            e.Owner.Released.TrySetResult(true); continue;
                        }
                    }
                    if (e.Retry && e.Sweep is null)
                    {
                        e.Retry = false;
                        // 先持有Sweep再允许cleanup执行，不在表锁内调Owner/Dispatcher。
                        var start = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
                        e.Sweep = Task.Run(async () => { await start.Task;
                            return await e.Owner.CloseOnceAsync(); });
                        start.SetResult(true);
                    }
                }
            }
            Thread.Sleep(100); // 有限监督节拍；未确认的槽不自动淘汰。
        }
    }
}
internal sealed record HostBusiness(
    bool Succeeded, ImmutableArray<RoiError> Errors, Exception? Failure, GeometrySnapshot? Final);
internal sealed record HostObservation(
    string? Ticket, HostBusiness? Business, Exception? ObservationFailure,
    bool ResourcesReleased, bool RecoveryConfirmed, bool CapacityRejected);

internal sealed class CoreHostOwner(HostCase c, CancellationToken caller, bool openOnly = false) : IRecoveryOwner
{
    public long ReservedBytes => checked(c.Profile.MaxWorkingBytes + c.Profile.MaxOutputBytes +
        c.Profile.MaxUndoBytes + 2L*c.Profile.MaxSerializedBytes + 1048576);
    public TaskCompletionSource<bool> Released { get; } =
        new(TaskCreationOptions.RunContinuationsAsynchronously);
    private readonly CancellationTokenSource stop = CancellationTokenSource.CreateLinkedTokenSource(caller);
    public Task<HostBusiness>? OriginalTask { get; private set; }
    public IRoiGeometryCore? Core { get; private set; }
    public RoiDrainReceipt? LastDrain { get; private set; }
    public Exception? CleanupFailure { get; private set; }
    private Task<RoiDrainReceipt>? drainTask; private Task? disposeTask;
    private bool closed;
    public void RejectBeforeStart() => stop.Dispose();
    public void Start(string id)
    {
        var start = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        OriginalTask = Task.Run(async () => { await start.Task; return await Work(id); });
        start.SetResult(true); // Root已登记且原Task已强持，然后才调用Factory。
    }
    private async Task<HostBusiness> Work(string id)
    {
        try
        {
            var open = new RoiGeometryFactory().Open(new(id+".open", id+".session", c.Initial,
                c.Profile, HostCases.Deadline(c.OperationTimeout)), null, stop.Token);
            Core = open.Core; // factory返回即由Root持有的Owner接住；失败null契约不残留资源。
            if (Core is null) return new(false, open.Errors, null, null);
            if (openOnly) return new(true, ImmutableArray<RoiError>.Empty, null, Core.Query().Snapshot);
            var q = Core.Query();
            var v = Core.Validate(new(id+".validate", q.Snapshot, c.Profile,
                HostCases.Deadline(c.OperationTimeout)), stop.Token);
            if (!v.IsValid) return new(false, v.Errors, null, q.Snapshot);
            var commands = ImmutableArray.Create<RoiEditCommand>(new TransformCommand(
                ImmutableArray.Create(c.NodeId), c.Transform));
            var r = new RoiEditRequest(id+".preview", q.SessionId, q.Epoch, q.Snapshot.Revision,
                q.ProfileRevision, RoiEditMode.Preview, commands, HostCases.Deadline(c.OperationTimeout));
            var preview = await Core.PreviewAsync(r, stop.Token);
            if (preview.State != RoiOperationState.PreviewReady ||
                Core.QueryOperation(r.OperationId).Adoption?.CanAdopt != true)
                return new(false, preview.Errors, null, Core.Query().Snapshot);
            var applied = Core.Apply(r with { OperationId=id+".apply", Mode=RoiEditMode.Apply,
                Deadline=HostCases.Deadline(c.OperationTimeout) }, stop.Token);
            if (applied.State != RoiOperationState.Completed)
                return new(false, applied.Errors, null, Core.Query().Snapshot);
            q = Core.Query();
            var undo = Core.Apply(new(id+".undo", q.SessionId, q.Epoch, q.Snapshot.Revision,
                q.ProfileRevision, RoiEditMode.Apply, ImmutableArray.Create<RoiEditCommand>(new UndoCommand(1)),
                HostCases.Deadline(c.OperationTimeout)), stop.Token);
            return new(undo.State == RoiOperationState.Completed, undo.Errors, null, Core.Query().Snapshot);
        }
        catch (Exception ex) { return new(false, ImmutableArray<RoiError>.Empty, ex, null); }
    }
    public async Task<bool> CloseOnceAsync()
    {
        if (closed) return true;
        var until = HostCases.Deadline(c.CleanupObservation);
        TimeSpan Remaining()
        {
            long left = until.Timestamp - Stopwatch.GetTimestamp();
            if (left <= 0) throw new TimeoutException();
            return TimeSpan.FromSeconds((double)left / until.Frequency);
        }
        try
        {
            stop.Cancel(); // 本Owner唯一业务取消源；不传给cleanup。
            if (OriginalTask is null) { stop.Dispose(); closed=true; return true; } // 未启动则Factory从未调用。
            await OriginalTask.WaitAsync(Remaining()); // 观察超时不取消/替换原Task。
            if (Core is null) { stop.Dispose(); closed=true; return true; }
            if (drainTask?.IsCompleted == true &&
                (!drainTask.IsCompletedSuccessfully || !drainTask.Result.ResourcesReleased))
                drainTask = null; // 仅已结束的关闭调用才允许下一次独立观察。
            drainTask ??= Core.DrainAsync(HostCases.Deadline(c.Profile.CloseTimeout),
                CancellationToken.None).AsTask();
            LastDrain = await drainTask.WaitAsync(Remaining());
            if (!LastDrain.ResourcesReleased || LastDrain.NativeResourcesOwned ||
                !LastDrain.PendingOperationIds.IsEmpty) return false;
            if (disposeTask?.IsFaulted == true || disposeTask?.IsCanceled == true) disposeTask = null;
            disposeTask ??= Core.DisposeAsync().AsTask();
            await disposeTask.WaitAsync(Remaining());
            if (Core.Query().State != RoiSessionState.Disposed) return false;
            stop.Dispose(); closed=true; return true;
        }
        catch (Exception ex) { CleanupFailure = ex; return false; } // 不改HostBusiness。
    }
}
internal static class CoreHosts
{
    public static async Task<HostObservation> Run(RecoveryRoot root, HostCase c, CancellationToken caller)
    {
        var owner = new CoreHostOwner(c, caller);
        string? ticket = root.Reserve(c.Prefix, owner); // 在Factory和Task启动前预约。
        if (ticket is null) { owner.RejectBeforeStart();
            return new(null,null,null,false,false,true); }
        Exception? observation = null; bool acknowledged;
        try
        {
            owner.Start(ticket);
            await owner.OriginalTask!.WaitAsync(c.ObservationTimeout); // 不用此超时延长执行deadline。
        }
        catch (Exception ex) { observation = ex; }
        finally
        {
            acknowledged = root.Handoff(ticket, owner);
            // 当前私有表在Handoff前无Sweep、禁止移除/停止，此处必为true；不抛cleanup异常。
        }
        try { await owner.Released.Task.WaitAsync(c.CleanupObservation); }
        catch (TimeoutException) { } // 查询入口=root.Query(ticket)，Retry是显式有限新观察。
        var business = owner.OriginalTask?.IsCompletedSuccessfully == true ? owner.OriginalTask.Result : null;
        return new(ticket, business, observation, owner.Released.Task.IsCompletedSuccessfully,
            acknowledged, false);
    }
    public static async Task<int> Main()
    {
        var root = new RecoveryRoot(); // foreground Supervisor是离栈后的实际进程Owner。
        using var caller = new CancellationTokenSource(); // 本例显式无用户取消；可调用caller.Cancel测试。
        var a = await Run(root, HostCases.Pixel(), caller.Token);
        var b = await Run(root, HostCases.Metric(), caller.Token);
        int exit = a.Business?.Succeeded == true && b.Business?.Succeeded == true &&
            !a.CapacityRejected && !b.CapacityRejected &&
            a.ObservationFailure is null && b.ObservationFailure is null ? 0 : 1;
        // 不在try里return后期望finally改退出码。每次恢复尝试与等待都有限。
        foreach (var result in new[] { a, b })
            if (!result.ResourcesReleased && result.Ticket is string id)
            {
                root.Retry(id);
                if (root.Query(id) is CoreHostOwner held)
                    try { await held.Released.Task.WaitAsync(TimeSpan.FromSeconds(2)); }
                    catch (TimeoutException) { exit = 2; }
            }
        if (!root.StopIfEmpty()) return 2; // 非空时Thread继续持根，不把Main返回当进程排空。
        return exit;
    }
}
```

`Main`返回2但Root非空时foreground Supervisor仍活着，**不是一个已经退出的 CLI**；真实宿主应保留服务/UI恢复入口调用 `root.Query(ticket)`（拿回原 `CoreHostOwner.Core/OriginalTask/LastDrain/CleanupFailure`）和 `root.Retry(ticket)`，每次Retry只发一个有界Sweep，已有Sweep未结束不并发发Drain/Dispose。自动测试须从外层有界进程监督观察该情形并标非零/删失，不让测试无限等待，不将进程强制结束写成成功释放。进程重启不保证Core恢复；显式强制终止是宿主事故处置，不能通过GC/finalizer补交释放证据。Root为空才 `StopIfEmpty`，join超时保留Root/Thread引用、不得另启一个根；这里不提供根的无界Dispose。

`CoreHostOwner.CloseOnceAsync`只在原业务Task退出后排空纯计算Core，没有HALCON lease，也不把Core的 `ResourcesReleased` 等同适配器输出归还。原业务结果始终在原Task内可回读；即使最后操作失败，cleanup可成功；即使业务成功，cleanup仍可未完成。关闭异常保存在CleanupFailure，最新Drain在LastDrain，已完成关闭Task才允许Retry重建新的观察，正在运行的原Task不丢、不补发。Root可观察结束但原对象不离Owner；Handoff确认前Host不释放持有关系。同步Factory/Open/Validate/Apply由已登记原Task执行，观察到期也仍受该Task/Owner强持，不能用外层 `Task.Run` 超时假装底层中断。

### 10.2 无 UI 扩展与视觉接入顺序

Interaction：snapshot→DocumentToViewport→HitTest→完整 Candidates/SelectionSet→显式 Apply；无 Pointer/WPF 依赖。Codec：Encode(snapshot)→Host 保存 bytes；读取→Decode→DraftImport→Host 显式 Open 新会话，绝不 Decode 后隐式覆盖现会话。Spatial：外部已资格坐标映射→每点块 SourceId/Revision/Frame→Select→块完整结果与支持缺口；宿主不得只累加成功块称全域完成。

HALCON-01沿用§10.1根协议，但其Owner额外强持 `IGeometryBackendPort`、每个 `IRoiGeometryLease`、原Execute/Materialize/Drain/Dispose Task及typed请求/ID。Factory前按Profile预约worker/输出及lease槽；至少为当前最大并发Execute预留输出lease槽，容量满在调用前拒绝，不能收到了迟到lease才发现无处持有。Factory在已登记原Task中返回时立即将Backend写入Owner；原Execute Task的实际完成路径在同一Owner中登记Receipt.Lease，然后才向观察者投影，不借前端await继续注册。Query重复返回同lease，不克隆；核LeaseId/引用后只保留一份释放权。每个lease的Materialize ID/Task同样先登记再执行，超时/取消只观察，原Task与lease仍强持。

关闭步骤固定为：封住新请求并请求业务取消→等待原Execute真正退出/回查原ID（迟到lease仍登记）→对每个lease先等待原materialize任务退出并QueryMaterialization同ID，再用新的有限期限 `lease.DrainAsync(..., CancellationToken.None)`→确认ResourcesReleased且Pending空→持有唯一 `lease.DisposeAsync().AsTask()` 并有限观察其实际完成→标此lease已归还→最后Backend.DrainAsync独立新期限→确认所有OutstandingLeaseIds/Pending空及ResourcesReleased→有限观察Backend.DisposeAsync实际完成。观察期限、执行期限、临时释放、输出归还分别记录；每个调用只有一个在途Task，Retry不得补发正在运行的Dispose。所有阶段沿§10.1 Remaining预算/WaitAsync方式，超时保存原Task/lease/Backend并向根Handoff；不在finally抛错覆盖业务、不在窗口卸载或Task超时后丢Owner。临时 `TemporaryResourcesReleased=true` 不等lease归还，Core纯计算 `ResourcesReleased` 不证明native释放。完成的materialize纯值可复制给宿主，但native输出仍只能由此Owner按序归还；未完成lease不被adapter强行释放。共享viewport的native Owner不归此ROI根处置，按其原公开端口独立关闭。提交仍只由HostCommit-01把Candidate+Owner/CAS/授权快照交给宿主；Unknown回查原ID，Core不写库。

### 10.3 两个 STA 编辑 Host、迟到与窗口关闭

这是WPF-01测试宿主装配，在对应 `.Wpf.Tests` 引用Core和Wpf DLL、安装的DevExpress程序集；采用§10.1同一Root/Owner协议和两个公开 `HostCases` 构造。以下类型均放宿主 `RoiHostExamples` namespace，不新增Core/Wpf公共API。额外using为 Windows、Windows.Controls、Windows.Input、Windows.Media、Windows.Shapes、Windows.Threading，以及 `Asun.Modules.RoiGeometry.Wpf`。两个 `[STAThread] Main` **分别编译为测试宿主入口**（同工程用StartupObject选 `PixelEditorEntrance` 或 `MetricEditorEntrance`，不把两个Main混为一个程序集默认入口）。入口在Dispatcher.Run前先Reserve，STA Window构造前Core Factory已在root强持的原Task中执行；root容量满不建窗口或控件。

装配的 `FixtureViewport` 是明确的无图几何测试桥，new Canvas，没有native/图像/设备Owner；仅显示这两个软件样例的Curve/Rectangle，其它Shape返回false且保留旧overlay，不作生产viewport替身。实产品把这个实现替换为viewport原Owner的公开桥，不能更换Core构造。画布用同一个DocumentToViewport投影，样例桥的返回true只表示overlay被同步接收，不表示真实图像/性能/资格通过。

```csharp
internal sealed class FixtureViewport(Affine2D projection) : IRoiEditorViewportBridge
{
    public Canvas Canvas { get; } = new() { Background = Brushes.White, Focusable = true };
    public UIElement View => Canvas;
    private long sequence = -1;
    public bool PublishOverlay(RoiEditorOverlay o)
    {
        Canvas.Dispatcher.VerifyAccess();
        if (o.Sequence <= sequence) return false;
        var snapshot = o.Preview ?? o.Snapshot;
        var visual = new Canvas { IsHitTestVisible = false };
        foreach (var n in snapshot.Nodes.Where(n => n.Visible))
        {
            Shape shape;
            if (n.Shape is CurveShape c && c.Closed)
            {
                shape = new Ellipse { Width=2, Height=2 };
                shape.RenderTransform = new MatrixTransform(new Matrix(
                    c.U.X,c.U.Y,c.V.X,c.V.Y,
                    c.Center.X-c.U.X-c.V.X,c.Center.Y-c.U.Y-c.V.Y));
            }
            else if (n.Shape is RectangleShape r)
                shape = new Polygon { Points = new PointCollection(new[] {
                    new Point(r.Center.X-r.U.X-r.V.X,r.Center.Y-r.U.Y-r.V.Y),
                    new Point(r.Center.X+r.U.X-r.V.X,r.Center.Y+r.U.Y-r.V.Y),
                    new Point(r.Center.X+r.U.X+r.V.X,r.Center.Y+r.U.Y+r.V.Y),
                    new Point(r.Center.X-r.U.X+r.V.X,r.Center.Y-r.U.Y+r.V.Y) }) };
            else return false;
            shape.Stroke=Brushes.SteelBlue; shape.StrokeThickness=0.1;
            shape.Fill=Brushes.Transparent; visual.Children.Add(shape);
        }
        visual.RenderTransform=new MatrixTransform(new Matrix(projection.M11,projection.M21,
            projection.M12,projection.M22,projection.Tx,projection.Ty));
        Canvas.Children.Clear(); Canvas.Children.Add(visual); sequence=o.Sequence; return true;
    }
}
internal sealed class FixtureEditorHost(string ticket) : IRoiEditorHost
{
    private long next;
    public RoiEditorNotification? Last { get; private set; } // 一格最新投影，无队列。
    public string NewId(RoiEditorIdentityKind kind) =>
        ticket+"."+kind+"."+checked(++next).ToString(CultureInfo.InvariantCulture);
    public bool Publish(RoiEditorNotification n)
    { if (Last is not null && n.Sequence <= Last.Sequence) return false; Last=n; return true; }
}
internal sealed class EditorOwner(RecoveryRoot root, HostCase c) : IRecoveryOwner
{
    private readonly CoreHostOwner inner = new(c, CancellationToken.None, openOnly:true);
    public long ReservedBytes => checked(inner.ReservedBytes + 1048576);
    public TaskCompletionSource<bool> Released { get; } =
        new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource<bool> Attached { get; } =
        new(TaskCreationOptions.RunContinuationsAsynchronously);
    public Exception? BusinessFailure { get; private set; }
    public Exception? CleanupFailure { get; private set; }
    public RoiEditorDetachReceipt? LastDetach { get; private set; }
    private Dispatcher? dispatcher;
    private Window? window;
    private RoiEditorControl? editor;
    private FixtureViewport? bridge;
    private FixtureEditorHost? host;
    private bool attachAttempted, allowClose, editorClosed;
    private Task<RoiEditorDetachReceipt>? detachTask, detachDispatchTask;
    private Task? editorDisposeTask, assemblyTask;
    private RoiViewportProjection? projection;
    private Action? unhookPointer;
    private Task<bool>? coreCleanupTask;
    private Task? finishTask;
    public void RejectBeforeStart() => inner.RejectBeforeStart();
    public void StartupFailed(Exception ex)
    { BusinessFailure=ex; Attached.TrySetResult(false); }
    public void Start(string ticket)
    {
        dispatcher=Dispatcher.CurrentDispatcher; // 入口已STA，保持本线程的Dispatcher.Run。
        inner.Start(ticket);
        dispatcher.BeginInvoke(new Action(() => assemblyTask=AssembleAsync(ticket)));
    }
    private async Task AssembleAsync(string ticket)
    {
        try
        {
            var opened = await inner.OriginalTask!.WaitAsync(c.ObservationTimeout);
            if (!opened.Succeeded || inner.Core is null)
                throw opened.Failure ?? new InvalidOperationException("Core Open rejected");
            var q=inner.Core.Query();
            var transform=c.Initial.Frame.Unit==GeometryUnit.Pixel
                ? new Affine2D(2,0,0,0,2,0) : new Affine2D(20,0,0,0,20,0);
            bridge=new FixtureViewport(transform); host=new FixtureEditorHost(ticket);
            editor=new RoiEditorControl();
            projection=new RoiViewportProjection(q.Snapshot.DocumentId,q.Snapshot.Revision,
                q.Snapshot.Frame.Id,0,transform,new Bounds2(0,0,960,700));
            var input=new RoiEditorInputProfile(c.OperationTimeout,c.Profile.CloseTimeout,
                4,c.Initial.Frame.Unit==GeometryUnit.Pixel ? 1 : 0.01,10,32);
            attachAttempted=true; // 即使Attach异常，Root也不丢控件/借用对象。
            var attached=editor.Attach(new RoiEditorAttachRequest(inner.Core,
                new RoiGeometryInteraction(),c.Profile,bridge,projection,host,
                new RoiEditorPermissions(true,false),input,
                new RoiEditorPresentation("zh-CN","Office2019Colorful",false),null));
            if (!attached.Attached) throw new InvalidOperationException("ROI Attach rejected");
            editor.SetSelection(new SelectionSet(ImmutableArray.Create(c.NodeId)));
            HookPointer();
            var retry=new Button { Content="重试关闭" };
            System.Windows.Automation.AutomationProperties.SetAutomationId(retry,"Roi.Host.RetryClose");
            var panel=new DockPanel(); DockPanel.SetDock(retry,Dock.Bottom);
            panel.Children.Add(retry); panel.Children.Add(editor);
            retry.Click += (_,_) => root.Retry(ticket);
            var area=SystemParameters.WorkArea;
            window=new Window { Left=area.Left,Top=area.Top,Content=panel };
            window.SourceInitialized += (_,_) =>
            {
                var dpi=System.Windows.Media.VisualTreeHelper.GetDpi(window);
                window.Width=Math.Min(1920/dpi.DpiScaleX,area.Width);
                window.Height=Math.Min(1080/dpi.DpiScaleY,area.Height);
            }; // 固定物理外框；client再扣标题/边框/宿主恢复栏，测试不改屏幕设置。
            window.Closing += (_,e) =>
            {
                if (allowClose) return;
                e.Cancel=true; if (!editorClosed) editor.SetPermissions(new(false,false));
                root.Handoff(ticket,this); // 同Owner确认；窗口/Dispatcher此刻保持存活。
            };
            window.Show();
        }
        catch (Exception ex)
        {
            BusinessFailure=ex;
            root.Handoff(ticket,this); // Open迟到或Attach失败均交同根恢复，不直接Shutdown。
        }
        finally { Attached.TrySetResult(BusinessFailure is null); }
    }
    private void HookPointer()
    {
        var canvas=bridge!.Canvas; bool active=false;
        void Send(RoiPointerPhase phase,RoiPointerButton button,Point p)
        {
            var m=Keyboard.Modifiers;
            editor!.ProcessPointer(new RoiPointerInput(projection!.ViewRevision,phase,button,
                new Point2(p.X,p.Y),(m&ModifierKeys.Control)!=0,
                (m&ModifierKeys.Shift)!=0,(m&ModifierKeys.Alt)!=0));
        }
        MouseButtonEventHandler down=(_,e) =>
        { if (!canvas.CaptureMouse()) return; active=true;
            Send(RoiPointerPhase.Down,RoiPointerButton.Primary,e.GetPosition(canvas)); };
        MouseEventHandler move=(_,e) =>
        { if (active) Send(RoiPointerPhase.Move,RoiPointerButton.None,e.GetPosition(canvas)); };
        MouseButtonEventHandler up=(_,e) =>
        { if (!active) return; active=false;
            Send(RoiPointerPhase.Up,RoiPointerButton.Primary,e.GetPosition(canvas)); canvas.ReleaseMouseCapture(); };
        MouseEventHandler lost=(_,e) =>
        { if (!active) return; active=false;
            Send(RoiPointerPhase.Cancel,RoiPointerButton.None,e.GetPosition(canvas)); };
        SizeChangedEventHandler resize=(_,e) =>
        {
            if (e.NewSize.Width<=0 || e.NewSize.Height<=0) return;
            projection=projection! with { ViewRevision=checked(projection.ViewRevision+1),
                GeometryRevision=inner.Core!.Query().Snapshot.Revision,
                ClientBoundsDip=new Bounds2(0,0,e.NewSize.Width,e.NewSize.Height) };
            editor!.RefreshProjection(projection);
        };
        canvas.MouseLeftButtonDown+=down; canvas.MouseMove+=move;
        canvas.MouseLeftButtonUp+=up; canvas.LostMouseCapture+=lost; canvas.SizeChanged+=resize;
        unhookPointer=() => { active=false; canvas.ReleaseMouseCapture();
            canvas.MouseLeftButtonDown-=down; canvas.MouseMove-=move;
            canvas.MouseLeftButtonUp-=up; canvas.LostMouseCapture-=lost; canvas.SizeChanged-=resize; };
    }
    public async Task<bool> CloseOnceAsync()
    {
        // 此方法由Root串行调用；总观察预算有限，UI调用经Dispatcher、保留派发的原Task。
        var until=HostCases.Deadline(c.CleanupObservation);
        TimeSpan Remaining()
        {
            long ticks=until.Timestamp-Stopwatch.GetTimestamp();
            if (ticks<=0) throw new TimeoutException();
            return TimeSpan.FromSeconds((double)ticks/until.Frequency);
        }
        try
        {
            if (dispatcher is null) return await inner.CloseOnceAsync(); // Start前失败无UI。
            await Attached.Task.WaitAsync(Remaining());
            if (assemblyTask is not null) await assemblyTask.WaitAsync(Remaining());
            if (attachAttempted && editor is not null && !editorClosed)
            {
                if (detachDispatchTask?.IsCompleted == true &&
                    (!detachDispatchTask.IsCompletedSuccessfully || !detachDispatchTask.Result.Detached))
                    detachDispatchTask=null;
                detachDispatchTask ??= dispatcher.InvokeAsync(async () =>
                {
                    editor.SetPermissions(new(false,false));
                    if (detachTask?.IsCompleted == true &&
                        (!detachTask.IsCompletedSuccessfully || !detachTask.Result.Detached))
                        detachTask=null;
                    detachTask ??= editor.DetachAsync(HostCases.Deadline(c.Profile.CloseTimeout),
                        CancellationToken.None).AsTask();
                    return await detachTask;
                }).Task.Unwrap();
                LastDetach=await detachDispatchTask.WaitAsync(Remaining());
                if (!LastDetach.Detached || !LastDetach.ResourcesReleased ||
                    !LastDetach.PendingOperationIds.IsEmpty) return false;
                if (editorDisposeTask?.IsFaulted == true || editorDisposeTask?.IsCanceled == true)
                    editorDisposeTask=null;
                editorDisposeTask ??= dispatcher.InvokeAsync(async () =>
                { unhookPointer?.Invoke(); unhookPointer=null;
                    await editor.DisposeAsync(); }).Task.Unwrap();
                await editorDisposeTask.WaitAsync(Remaining()); editorClosed=true;
            }
            if (coreCleanupTask?.IsCompleted == true &&
                (!coreCleanupTask.IsCompletedSuccessfully || !coreCleanupTask.Result)) coreCleanupTask=null;
            coreCleanupTask ??= inner.CloseOnceAsync();
            if (!await coreCleanupTask.WaitAsync(Remaining())) return false;
            finishTask ??= dispatcher.InvokeAsync(() =>
            {
                allowClose=true; window?.Close();
                dispatcher.BeginInvokeShutdown(DispatcherPriority.Background);
            }).Task;
            await finishTask.WaitAsync(Remaining());
            return true;
        }
        catch (Exception ex) { CleanupFailure=ex; return false; }
    }
}
internal static class EditorEntrances
{
    public static int Run(HostCase c)
    {
        if (Thread.CurrentThread.GetApartmentState()!=ApartmentState.STA)
            throw new InvalidOperationException("STA required");
        var root=new RecoveryRoot(); var owner=new EditorOwner(root,c);
        string? ticket=root.Reserve(c.Prefix+".ui",owner);
        if (ticket is null) { owner.RejectBeforeStart(); root.StopIfEmpty(); return 2; }
        try { owner.Start(ticket); }
        catch (Exception ex) { owner.StartupFailed(ex); root.Handoff(ticket,owner); } // 原Owner保留。
        Dispatcher.Run(); // 正常WPF消息循环，不是无界Dispose/Detach等待。
        try { owner.Released.Task.WaitAsync(TimeSpan.FromSeconds(2)).GetAwaiter().GetResult(); }
        catch (TimeoutException) { return 2; } // Supervisor继续持根，不能无界Join。
        return root.StopIfEmpty() && owner.BusinessFailure is null ? 0 : 2;
    }
}
public static class PixelEditorEntrance
{
    [STAThread] public static int Main() => EditorEntrances.Run(HostCases.Pixel());
}
public static class MetricEditorEntrance
{
    [STAThread] public static int Main() => EditorEntrances.Run(HostCases.Metric());
}
```

无本机图像引擎也能按A.6公开构造从空Host装配并查询/编辑两样例；“真实WPF尚未运行”是运行验证门，不是缺Core/控件构造。HookPointer已经显式连接Canvas事件、DIP坐标、鼠标capture、修饰键和projection，Root持事件源/委托到Detach实际完成才unhook；捕获期间移出Canvas继续手势，失捕获发送Cancel。外部Core修改时由Host按同SizeChanged规则刷新GeometryRevision/ViewRevision，不能让旧投影继续参与采用。默认样例只用于移动两个合法Shape；生产viewport的图像域、命中、绘制支持和高级工作台仍按原公开桥及§9验收。重试按钮只出现在宿主恢复入口，文本Key=`Roi.Host.RetryClose`，三语分别“重试关闭”/“重試關閉”/“Retry close”；样例Main默认zh-CN，实际宿主切换时更新本按钮内容并调用editor.SetPresentation，同一资源来源，不露出技术异常全文。窗口只在固定1920×1080验证视口内按WorkArea扣除任务栏/边框，布局按真实Client DIP刷新，不改屏设置或跑其它分辨率。

窗口Closing取消本次关闭，封住输入并Handoff；第一次Detach超时仍保留Window/Dispatcher/bridge/host/editor/inner/Core及所有调用Task，Root.Query(ticket)返回原 `EditorOwner`，`LastDetach/CleanupFailure`可读，Root.Retry(ticket)发新的有限观察。支持恢复按钮/宿主诊断入口在同STA调用Retry；不能在Dispatcher关闭后调用Detach，不从其它线程同步Invoke等待Dispatcher。Dispatcher正常shutdown只在Detach、Core真实排空和关闭Window动作都完成后；外部强制结束线程/进程只能记中断，不能补写ResourcesReleased。迟到Preview/Interaction按A.6 attach generation、document/view revision核对，不能回写新Attach。两个入口以不同Core/Profile/Frame/projection/ID启动，zh-CN/zh-TW/en-US通过SetPresentation由宿主设置，不在编辑器放独立切换入口；这个小Host不代替§9的完整UI视觉和真实viewport验收。

### 10.4 两个 HALCON-01 typed 消费输入与结果

下列装配输入放本模块`.AsunImage.Tests`的宿主namespace `RoiHostExamples`，复制§10.1的HostCases到该消费Host，不引用Core.Tests程序集；引用Core/Serialization/AsunImage及System.Text.Json、System.Linq。这是已公开v0.3的消费配方，未新增模块DTO/设备端口。ticket来自§10.1根在Factory前的Reserve；测试辅助Owner落实§10.2的原Task/输出槽/恢复协议，不得省略或用未定义NativeOwner代替。

```csharp
internal static class BackendInputs
{
    private static string PayloadHash(string id, GeometrySnapshot s, ValidationProfile p)
    {
        var e=new Asun.Modules.RoiGeometry.Serialization.RoiGeometryCodec().Encode(
            id,s,p,HostCases.Deadline(TimeSpan.FromSeconds(2)),CancellationToken.None);
        if (!e.Errors.IsEmpty) throw new InvalidOperationException(e.Errors[0].Code);
        // 这份有限buffer也计Host预约；e.Sha256是整个envelope，不能充当几何hash。
        using var json=JsonDocument.Parse(e.Bytes.ToArray());
        return json.RootElement.GetProperty("payloadHash").GetString()
            ?? throw new InvalidOperationException("Missing geometry payload hash");
    }
    public static (RoiBackendOpenRequest Open,RoiBackendRequest Execute) PixelRaster(string ticket)
    {
        var c=HostCases.Pixel();
        var n=c.Initial.Nodes[0] with { Id="roi.rectangle", Shape=
            new RectangleShape(new(14,26),new(4,0),new(0,6)) };
        var s=c.Initial with { DocumentId="doc.raster",Revision=0,Nodes=ImmutableArray.Create(n) };
        var operand=new RoiVectorOperand("a",s,PayloadHash(ticket+".hash",s,c.Profile));
        var grid=new RoiGrid("grid.raster",8,8,new(10,20),2,3,true,4);
        return (new(ticket+".open",ticket+".session",c.Profile,HostCases.Deadline(c.OperationTimeout)),
            new(ticket+".raster",ticket+".session",0,RoiBackendOperation.Rasterize,null,
                ImmutableArray.Create<RoiBackendOperand>(operand),Representation.RasterizedRegion,
                RoiRasterPolicy.HalconRoundedFilled26,grid,null,0.01,false,c.Profile,
                HostCases.Deadline(c.OperationTimeout)));
    }
    public static (RoiBackendOpenRequest Open,RoiBackendRequest Execute) MetricBoolean(
        string ticket,RoiBooleanKind kind=RoiBooleanKind.Union)
    {
        if (kind!=RoiBooleanKind.Union && kind!=RoiBooleanKind.Intersection)
            throw new ArgumentOutOfRangeException(nameof(kind));
        var c=HostCases.Metric(); var a=c.Initial;
        var b=a with { DocumentId="doc.metric.b",Nodes=ImmutableArray.Create(
            a.Nodes[0] with { Id="roi.rectangle.b",Shape=
                new RectangleShape(new(12,20),new(2,0),new(0,1)) }) };
        var operands=ImmutableArray.Create<RoiBackendOperand>(
            new RoiVectorOperand("a",a,PayloadHash(ticket+".hash.a",a,c.Profile)),
            new RoiVectorOperand("b",b,PayloadHash(ticket+".hash.b",b,c.Profile)));
        return (new(ticket+".open",ticket+".session",c.Profile,HostCases.Deadline(c.OperationTimeout)),
            new(ticket+".boolean",ticket+".session",0,RoiBackendOperation.Boolean,kind,operands,
                Representation.AnalyticVector,null,null,null,0.001,false,c.Profile,
                HostCases.Deadline(c.OperationTimeout)));
    }
}
```

正常消费顺序（均由已Reserve的Owner登记原Task并在实际完成路径写回Owner，再允许观察；不是另起匿名Task）：创建 `IRoiGeometryBackendFactory factory = new Asun.Modules.RoiGeometry.AsunImage.RoiAsunImageBackendFactory()` → `factory.Open(inputs.Open,null,CancellationToken.None)`，Errors空且Backend非null才继续 → `backend.ExecuteAsync(inputs.Execute,CancellationToken.None)` → 核IsTerminal/TemporaryResourcesReleased/Errors及Lease → `lease.MaterializeAsync(new RoiMaterializationRequest(ticket+".materialize",inputs.Execute.Profile.MaxOutputBytes,HostCases.Deadline(TimeSpan.FromSeconds(2))),CancellationToken.None)` → 完整纯值断言 → §10.2先归还lease再关闭backend。这里inputs为上述一个返回tuple，backend/lease分别是原Open/Execute回执的已登记引用；执行/Materialize观察超期或异常走原ID Query与Handoff，不能进入没有lease的后续调用或在finally强行Dispose。Materialize新期限只约束这次读出，不更新Execute原deadline；同ticket不可改kind重发，Intersection使用新ticket。

| 消费者与输入 | 必判定纯值期望 | 出错与恢复 |
|---|---|---|
| Pixel算法Host / PixelRaster | Frame=camera.xy，G逆映射矩形col/row各[0,4]；RoundedFilled后25像素、1组件0洞，ObjectIndex=0、Row=0..4的5个runs，各Start=0/End=4；Clipped=false、离散报告，Source hash为各原payload | 错Frame/grid/预算在native前拒；取消/期限仍原ID可查；观察未知不作空结果，按§10.2实际退出后归还 |
| mm计量Host / MetricBoolean | Union一组件0洞，bbox x[8,14]/y[19,21]、面积12 mm²；新ticket Intersection的bbox x[10,12]/y[19,21]、面积4 mm²；Grid=null、CoordinateErrorBound=null、Precision=BackendNumeric，Sources为两原payload | RequireBoundedCoordinates=true但无证明数值界必须拒；不能改填0。输入保持原参数/身份，结果是新document/revision0、非生产测量事实 |

两例只用于可复现软件/真实算子验收输入，不替代客户Golden与计量允差。§7.4转换若未满足严格无损边界后检，应拒绝并在本模块实现/验收中解决，不静默更换路线或旧期望；任何运行失败不授修改合同。

## 11. 两种视角的反例与恢复

全部表项是可执行软件/集成断言，合成坐标不构成物理允差或现场资格。每行记录完整输入、Profile版本、候选内容/错误、revision/历史、实际资源终态；无需另建重复过程报告。

### 11.1 视角一：几何算法与操作员逐能力走查

| 用例 ID / 能力 | 具体输入/改变 | 可判定结果与下一步 |
|---|---|---|
| RG-C01 值对象/创建 | 空 Nodes、default Nodes、重复NodeId；Circle R=20与R=0/NaN | 空文档合法；default/重复/退化/非有限分别拒绝；错误无Candidate、原文档/历史不变 |
| RG-C02 变换 | 中心(200,100)平移(5,-2)；A平移(100,50)、L旋转90°、点(2,1) | 中心(205,98)；A*L=(99,52)，反序不能通过；圆非均匀scale得到一般Curve，剪切Rectangle→Polygon；singular拒绝 |
| RG-C03 拓扑 | 10×10外环、2×2洞，洞内1×1岛；bow-tie、洞碰Outer、孔在凹口外 | 合法材料面积97；拒自交/接触/越界，不能只测一个洞顶点；原环ID/洞/岛完整 |
| RG-C04 退化/大坐标 | 相邻重复点、极窄环、近共线三点、MaxAbsCoordinate边界±一ULP | exact stored-value谓词正反/循环置换一致；MinLength/条件/坐标超限显式拒绝，不拿display tolerance吞细缝 |
| RG-C05 批量/约束 | A/B多选同Pivot变换，B Locked；固定长度为10而候选11，Undo Steps多于历史 | 任一失败整批不发布、不改变SelectionSet/历史；ConstraintViolation/HistoryUnavailable精确归因，解锁/修命令后新操作 |
| RG-C06 Undo/Redo | r7→平移→r8→Undo→r9→Redo→r10→新编辑 | Undo内容逐字段恢复r7但revision=9；Redo内容恢复r8但revision=10；新编辑清redo；no-op不增revision/history；一次手势一历史 |
| RG-I01 多候选/层次 | 两同边/同distance节点不同Z-order，Group含重复被选子；孔中点/隐藏/锁节点 | 按§8.1全部候选确定排序；孔内不命中实体，隐藏不pick、锁可选不可编辑；Group展开叶一次；MaxCandidates超限拒完整结果 |
| RG-I02 viewport改变 | 非均匀显示变换、DPI/旋转/镜像、Curve误差区间跨命中阈值；多Profile/reader占满缓存；语言在半输入时切换 | DIP容差一致、逆换基正确，区间跨阈值Ambiguous不偏选；全部旧reader/新工作区总预算核算、取消不发布半树；无几何事实修改；文本/caret/typed数值保持，旧HitTest/Preview source过期不采纳 |
| RG-H01 布尔 | 两重叠方形Union；A−(C1∪C2)；不交Intersection；多洞/组件 | Union交叠保留，不被Even-Odd误抹成洞；Difference不换角色；空为Empty且成功释放，不等未输入/异常；后检全部组件 |
| RG-H02 raster转换 | 连续矩形[0.2,0.8]×[0.2,2.6]；单像素(1,1)border往返 | 连续面积1.44不等像素面积；HalconRoundedFilled不是PixelCenterInside；单像素可变4像素，往返不得标DiscreteGridExact |
| RG-H03 参数改变 | neighborhood=4/8、filled与不支持的margin、固定nearest_neighbor与不支持的constant、ε减半 | 参数/方法/输入hash绑定；v0.3不支持margin/constant请求而非暗换算法；合法新请求重算、老结果不可覆盖；顶点增加超预算拒绝，不静默调生产Profile |
| RG-H05 typed桥/非单位Grid | §10.4两Host；xld_cont误送布尔；正Alpha转换移动一角点；Pixel G非零Origin/非单位Step、非对称旋转 | 用xld_poly/get_polygon_xld且实际边界无损；移动/拆环拒RG-007；5 runs/25像素，T角点按§7.4 G矩阵、禁止双补0.5；mm Union12/Intersection4且仍BackendNumeric |
| RG-H06 完整性/接触 | 两对角像素；4/8邻域；带洞集合；max_connection预先非0/connection过程中改小；一个合法空Region | Components分别2/1；8邻接接触Runs可保存、严格Vector边界拒RG-004；材料/洞各runs计数核connection，无截断放行；非0/不一致RG-014且不改全局，预算不足明确拒；空lease Components/Holes=0且可归还 |
| RG-S01 3D/遮挡 | Prism外环[0,10]²、洞[4,6]²、z=[1,3]；点(5,5,2)/(2,2,2)/(2,2,4)，存在遮挡 | 选择仅(2,2,2)，原index保持；遮挡不填点；非有限/错误Frame/未资格变换拒采纳；缺支持另报不得将缺点当0 |
| RG-C07 弱信号/噪声 | 原图低对比/遮挡→上游不完整轮廓；本模块收到开放线/缺Source | 不推理/补边/猜洞；Polyline只作开放几何，面积布尔Unsupported；没有来源不能授图像/计量资格，要求上游提供新版本 |
| RG-K01 Codec | 重复JSON key、未知minor/shape字段、hash错、压缩炸弹/过深/超字节 | 重复/损坏Rejected；未知完整载荷ReadOnlyUnknown、Snapshot=null且原bytes可导出；预算前检不解压无界内容；不存在二进制magic假定 |

### 11.2 视角二：外部实现者、并发与资源故障走查

| 用例 ID | 故障注入/前置 | 不允许退让的断言 |
|---|---|---|
| RG-L01 重复/缓存 | Apply相同ID相同payload两次；同ID不同矩阵；达到MaxReceipts | 一次revision/history；Conflict不覆盖原Receipt；满预算拒新操作，旧操作可Query且不重放 |
| RG-L02 CAS竞争 | 两请求都ExpectedRevision=7并发；一个延迟候选计算 | 最多一者发布r8，另一Conflict；Preview r7迟到时Stale无Candidate；不把UI锁当CAS |
| RG-L03 两消费者 | Pixel算法工具Session A与mm计量工具Session B；A取消/B继续 | Profile/Frame/语言/事件/取消/历史隔离；两Host无平台Shell仍调用同DLL；B不被A Drain干扰 |
| RG-L04 取消/期限 | token预取消、排队期间过期、候选发布前取消、成功发布后才取消 | 前检短拒绝；已接纳操作真实释放后Cancelled/DeadlineExceeded；成功事实晚取消不回滚；不存在deadline重置 |
| RG-L05 关闭/迟到 | Preview闩锁卡住→Drain期限到；native算子仍运行；旧epoch回调晚到 | DrainUnknown/Session Draining/pendingId非空，资源仍持有、无Terminal/Disposed；解闩真实退出后再Drained；旧回调不能复活或释放新租约 |
| RG-L06 native恢复 | 同worker tsp参数设置后异常/恢复失败；另一worker执行 | finally原线程恢复；恢复失败worker隔离不接新单；不改其它消费者系统值；前端断连不重跑未确认工作 |
| RG-L07 事件 | sink抛异常/返回false/很慢，UI Dispatcher关闭 | sink按非阻塞契约；隔离故障sink、Core事实不回滚，Query/Receipt仍权威；无锁内回调/Dispatcher环，无队列无限增长 |
| RG-L08 预算 | 全包围盒重叠导致O(n²)候选、输出爆炸、UndoBytes满、MaxPending满 | 分配前预约+分块核实际；超限不取前N顶点/最大组件作成功，原revision/history不改；测量峰值/拒绝原因完整 |
| RG-L09 租约 | materialize超过maxBytes、重复Dispose、观察者Query原Lease，超deadline | 有界拒、同Lease唯一Owner一次归还；重复释放幂等，归还后materialize Disposed；临时退出不冒全部输出归还 |
| RG-L10 Host提交 | commit响应丢失/断连、授权快照变化、另一Owner改revision | Core无数据库写；HostQuery原OperationId后确认，Unknown不当Committed、不自动重试；权限/CAS归HostOwner |
| RG-L11 迁移/回退 | 旧.roi未知版本、新Codec多字段、旧Profile正在使用、切换旧DLL | 原件/hash不改，新Draft新身份；旧Core+Codec闭包回退，不解释未知子集、不跨版本重复提交；与缓存/Deadline无跨进程序列化 |
| RG-L13 Host根/异常四轴 | 两个§10.1 Host；Factory前故障/Open失败/Validate失败；Preview闩锁超过观察，原业务失败再cleanup异常；两根槽满后第三工作 | 满额拒在Factory前，无新实例；原Task/Profile/CTS/Core与ticket可Query；Business原异常/错误逐字段不变，ObservationFailure/CleanupFailure单列；Handoff确认后才离栈；释放前不淘汰槽、不补发Task；解闩后Retry有限排空、空根StopIfEmpty，业务失败+cleanup成功仍失败 |
| RG-L14 Core/native分门 | 纯Core关闭成功，同时HALCON原Execute迟到给lease、Materialize超时、Dispose尚未完成 | Core无native lease，不为backend代验；原Execute实际完成先登记原lease；Backend临时释放不减少lease账；lease/原materialize/close Task根强持、原ID可Query、Retry只复用在途Task；全部归还后才Backend关闭，无二次释放/覆盖业务错误 |
| RG-W05 全任务/LOD/投影故障 | §9.5全部手势/混合参数/三语、嵌套行键同NodeId、DPI换算固定物理视口、满显示预算、PublishOverlay/Host.Publish抛错或false | 同手势一个Apply/历史；稳定RowKey映射OwnerNodeId去重、批量失败原值不变；文本/caret保留、关键命令可见；display LOD不改填充/HitTest/Core，最多一任务一pending、预算不足不截断成功；投影故障不回滚，明确Refresh恢复，Detach解除事件/归还借用引用 |
| RG-W04 双STA空Host | PixelEditorEntrance / MetricEditorEntrance按§10.3装配，Factory/Open/Attach分别失败，关闭窗口、Detach延迟、迟到Preview、第三根槽请求 | 两Frame/Profile/ID/实例隔离；无隐藏外部配置；STA创建/Attach/Refresh/Detach/Dispose；Closing先取消并Handoff、恢复按钮有限Retry；原Dispatcher/控件/桥/事件/Task保留，成功Detach后unhook/Core排空/窗口关；迟到不复活旧挂接；容量拒在构造前 |


补充直接验收断言：RG-C10固定圆建议n=100/101顶点、过小ε超限拒绝、取消/过期无建议且Profile不变；RG-C08 Group父/子重复Transform仅变一次；锁祖先拒编辑、同值解锁可恢复、删除Group保留外约束时整批拒，显式移除引用后成功；RG-C09近正交Rectangle拒绝，合法Rectangle经微剪切变Polygon、AspectRatio未移除拒、移除后成功且新顶点ID确定；RG-S02同点在XYZ/mm与XY/Pixel错Frame拒、hole边界入/内部不入、未知支持仍标未知；RG-H04非法runs的End<Start/重叠/乱序在native前拒，Materialize超时保留ID与lease、退出后可Query、lease未归还时Backend DrainUnknown；RG-K02三种支持域/每约束/每shape字段逐字节roundtrip和未知嵌套字段整份只读，Profile.Hash绝不按Geometry payload猜；RG-L12按下表验证原ID优先回放、独立当前采用投影与关闭墓碑；MaxReceipts满不清旧项、未知ID不猜终态。

本轮退修的定向断言（全部软件合成，按实际typed字段/字节/整数判据核对，不能只比较消息文字）：

| 用例 | 输入与顺序 | 唯一期望 |
|---|---|---|
| RG-L12a 成功回放优先 | epoch0/revision7，Apply `op.a`→Completed/revision8；另一新ID编辑→revision9；原op.a请求字段完全相同且原deadline已过，重复调用传已取消token | 原op.a Receipt含Candidate/revision8/Changed/终态/错误逐字段保持；revision仍9、历史不增、无二次Accepted/Terminal；QueryOperation(op.a).Adoption.CanAdopt=false/ObservedRevision=9；不返回Stale/Expired/Cancelled覆盖原事实 |
| RG-L12b 期限与载荷冲突 | 已终态op.a，将同ID的Deadline.Timestamp加1（其它相同）；再换ExpectedRevision或Epoch；对完成/在途各做一次 | Rejected/RG-008-Conflict，QueryOperation仍返回原项；不得延长原期限、重放或占新墓碑。完全相同原期限即使已过仍按a回放 |
| RG-L12c 在途观察者 | 首次token未取消、Preview闩锁未放行；同ID同payload的重复观察者token已取消/原deadline到期 | 返回既有非终态观察，无Candidate、不新执行；观察者不请求原工作取消。若原执行期限确已到，它按自己的执行检查走DeadlineExceeded、实际释放后成终态；不能由观察调用先发布终态 |
| RG-L12d Drain/Disposed/旧epoch | 完成op.a后Drain首次epoch0→1，排空再Dispose；在Draining、Drained、Disposed三状态Query/同payload回放；另一未知新ID带旧epoch0 | 旧op.a终态Receipt始终相同、Adoption=false且ObservedEpoch=1，最后Snapshot只读；未知新ID短拒RG-013、不占ID。Open状态未知ID错epoch拒RG-020；原ID改epoch则步骤3 Conflict，不能抢先Disposed/Stale |
| RG-L12e 终态Preview与截止 | PreviewReady/当前revision7，等待原执行deadline到期但不改文档；Query采用投影；再Apply其它新ID至revision8 | 截止已过本身不改PreviewReady/Candidate；仍Open/epoch相同且revision7时投影true；revision8后false。Apply另需新ID/新期限及CAS，不能用投影直接发布 |
| RG-C11a 边界/精确奇异 | A=diag(1,2)，K=2/Math.BitDecrement(2)；A=[[1,1],[1,1]]与d=Math.BitIncrement(1)两种 | diag等号通过，K下降一ULP拒RG-007；exact det0拒RG-003，near-det非零不误判奇异；near-det在K=10拒RG-007，在K=2^56条件门通过（后续坐标/逆规则独立） |
| RG-C11b norm固定 | A=[[1,1],[0,1]]，K=3；同系数分别装配Affine/Curve/Viewport（尺寸/单位/Profile合法） | κ₂≈2.618，统一精确门通过；不能选择1-/∞-norm乘积4而拒绝。K=2拒RG-007；阈值与不涉及平移的结论三入口一致 |
| RG-C11c 缩放/中间溢出 | diag(1,2)同时乘2^600或2^(−600)，K=2；MinLength显式足够小/MaxAbsCoordinate显式足够大 | 条件数门结果与未缩放完全相同，原double det会溢出/下溢也不能用作奇异依据；有理逆均可有限表示；实际几何/坐标预算照常核，不因条件门过即免除 |
| RG-C11d 逆下溢/溢出 | A=double.Epsilon*I；A=[[2^1023,2^(−1074)],[0,2^1023]]，K=2 | 两者精确det非零/条件门可通过；首例inverse溢出，次例inverse非零off-diagonal舍入0，需逆的Viewport拒RG-007，不创建可采用命中；Curve不需逆不额外被inverse门拒 |
| RG-C11e K平方溢出 | A=diag(1,2)，K=double.MaxValue；零块/NaN/Infinity另测 | exact条件比较可通过，不计算double K²；零块RG-003、非finite RG-002；新值整数预算不足RG-011，不能用Overflow代替正确条件结论 |
| RG-S03 空间唯一判据 | Prism B=I、t=2^(−20)，K=1和double.MaxValue；B的U=(1+t,0,0)，V=(0,1,0)，Normal=(0,0,1)；再将U.X增一ULP，K=2 | I通过，K²不double溢出；1+t范数上界/手性平方边界等号通过且Gershgorin门用K=2通过；一ULP外范数/手性拒RG-007；未知数值预算仍RG-011，不换浮点sqrt分支 |
| RG-K03 Codec独立向量 | §8.2固定空文档payload/133bytes/hash，附已知v1 envelope；改变culture，负零用其它向量测 | payload逐字节/hash相同，正常DraftImport；不把envelope hash混作payloadHash、不用Codec自己生成expected；未知字段仍整份只读，固定向量不提供运行/性能资格 |
| RG-K04 公开创建/非法 | 无UI公开new RoiGeometryCodec()，使用§10.1 Pixel/Metric；合法Profile下default bytes、Empty bytes、default Deadline、坏ID、Profile.MaxWorkingBytes=0、snapshot含NaN/错Frame | 无隐藏初始化；default bytes/期限/坏ID/非法Profile RG-001，Empty bytes RG-012，NaN RG-002，错Frame RG-005；结果按§8.2失败形状，输入与Core revision不变，不创建内部编辑会话 |
| RG-K05 取消/期限 | 完整Pixel已编码bytes；有效前检+已取消token；合法Frequency但过去Timestamp；编码/解析中测试闩锁使取消发生在发布前；失败后新ID/期限重调 | RG-009/仅到期RG-016；Encode无Bytes/hash，Decode Rejected无Snapshot/RawPayload/hash；返回前临时工作退出，无后台Owner/lease；取消源撤离后同实例正常调用不继承取消，晚取消不改既有返回值 |
| RG-K06 同实例并发 | 同一个公开Codec实例，Pixel A与Metric B两个Task/不同Profile，A发布前取消、B正常Encode→Decode，另两正常并行重复同输入/ID | A失败不影响B，B Frame/mm/几何与typed原值一致（负零按现规约）；相同合法输入在各culture的规范bytes/hash一致；无跨请求Profile/取消污染或缓存，Host根槽限制总并发/预约，不把每次预算当全进程上限 |


## 12. 定向测试与执行验收

### 12.1 Core、Interaction、Codec、Spatial 软件验证

按 DEV-GOV-010 §3.1 首版测试栈：`Microsoft.NET.Sdk / net10.0 / OutputType=Exe`，BCL确定性断言，仅引用受测DLL；不留待选xUnit/NUnit包。唯一落点为Core binding及§8.3中的对应 `.Tests.csproj`。实施后构建/验证分别执行 `dotnet build <唯一工程> -c Release`、`dotnet run --project <唯一测试工程> -c Release`；Core确定命令为 `dotnet build src/Modules/roi-geometry/Asun.Modules.RoiGeometry.Core/Asun.Modules.RoiGeometry.Core.csproj -c Release` 和 `dotnet run --project tests/Modules/roi-geometry/Asun.Modules.RoiGeometry.Core.Tests/Asun.Modules.RoiGeometry.Core.Tests.csproj -c Release`，§10.1两个Host共用该BCL测试入口。§10.3两个STA入口作为该模块 `.Wpf.Tests` 内两个 StartupObject fixture；分别用 `-p:StartupObject=RoiHostExamples.PixelEditorEntrance` 与 `-p:StartupObject=RoiHostExamples.MetricEditorEntrance` 构建/运行，正常输入交互/关闭断言由RG-W04测试驱动执行，不能只开窗口就返回PASS；CoreHosts.Main不参与WPF入口编译；非零表示任一失败、未完成或必需项跳过，逐用例列RG ID。`dotnet test`不能执行这些Exe。异步闩锁和固定输入控制RG-L场景，内部时钟测试通过internal Stopwatch读取接缝/测试程序集友元实现，公开API始终校验真实时钟频率；不新增公开设备/产品端口。

| 套件 | 必执行断言/比较 | 不得冒称 |
|---|---|---|
| Core.Tests | RG-C01～11的纯值对象/编辑/建议/数值门部分，RG-L01～05/07/08/11～13纯托管分支；结构逐字段相等、revision/undo/redo/错误/事件/资源与独立Adoption.CanAdopt | 软件合成不替代真实图像/物理资格 |
| 同步/异步等价 | 固定Commands通过Apply与Preview；统一数学候选内容、错误码/路径、预算拒绝；仅持久状态/revision差异按§10 | 不要求调度时间等价，不用PreviewReady当发布 |
| Interaction | RG-I01/02；BVH与完整线性扫描的**候选集合与排序**相等；缩放镜像/误差边界/框选/空/超限 | 截图相似不等HitTest精确 |
| Serialization.Tests | RG-K01～06/L11，稳定byte/hash、culture-independent、负零、double roundtrip、全部shape/constraint discriminator/未知原bytes | Encode成功不等宿主落盘、损坏测试不等现场迁移 |
| Spatial Core.Tests | RG-S01～03与全部Frame/finite/边界/大范围/错映射分支；原index/点块完整性 | 不替代3D重建、标定或遮挡支持事实 |

### 12.2 视觉与 UI 分门验收

HALCON-01 `.AsunImage.Tests` 在现有AsunImage引用下运行真实operator；执行RG-H01～06/L05～06/L08～09/L14，按§7逐method/grid/neighborhood/版本比全部组件/洞/runs/source/误差，与纯矢量真源分别记录。释放计数在成功/取消/异常/DrainUnknown后实际监测；无法观测到完整排空不能PASS。Golden样本由消费者提供并hash锁定，不能用合成图替代真实客户误接受/拒绝。类型/重载编译只是API调用验证，不是算子是否存在审查。

WPF-01 `.Wpf.Tests` 为 `net10.0-windows/UseWPF/OutputType=Exe`，BCL STA TestHost直接嵌入RoiEditorControl并引用本机DevExpress25.2.3和已批准viewport公共DLL。针对§9表中的AutomationId执行：绘制→改参数→多选/约束→Preview→Apply→Undo/Redo→错误恢复→语言切换→Close；同时执行A.6的RG-W01～03及§10.3/RG-W04与§9.5/RG-W05；UIA/键盘真WPF，固定1920×1080物理验证视口，按实际DPI换DIP并扣任务栏/边框/标题/状态/宿主恢复栏测client，无其它分辨率矩阵或改屏设置。控件内部测试适配不模拟真实DevExpress行为。验收分视觉（影像占比/对齐/图标/主题/三语长度）和操作（焦点/手势一次发布/关闭排空）两门，截图只能证明所截静态布局。已有未变场景证据复用，改变API/文案/布局的对应断言重测。

HostCommit-01按宿主正式Contract/权限/实际持久回执测试RG-L10；本模块不新造数据库模拟证明交付。真实Replay/现场验收与HIL（只对确依赖硬件链）按产品任务接收，本轮全部未执行。

## 13. 性能、预算与超大图负载

### 13.1 RoiBenchmarkProfile

Benchmark采纳的字段与维度在附录A.5；软件ValidationProfile防无界分配与性能目标是两类输入。所有性能数值来自消费者采纳Profile，不从此文合成例赋节拍/允差。公共统计口径只引用DEV-GOV-010 §3.1：请求接纳→ResourcesReleased端点、P50/P95/P99与n、失败/超时/删失/排空未知另列。输出Lease长寿命另记录“候选形成→消费者使用完成→Lease归还”，若整次请求宣称资源全部归还，端点必须包括Lease归还，不能把TemporaryResourcesReleased冒作End-to-end归还。

| 模块负载维度 | 对照/测点 | 失败与资源断言 |
|---|---|---|
| 节点/点/环/组件/洞密度、重叠AABB、深Group | 校验/精确谓词段对、约束、深层展平、BVH构建/查询对照全扫描 | 阶段候选/已检对数与预算；最坏O(n²)不被索引隐藏，超限明确拒 |
| 原图width/height（64位元信息）、viewport可见tiles、DIP/DPI、2D/3D覆盖 | Pointer到候选/overlay present、LOD层级、Tree/PropertyGrid更新 | ROI不分配width*height mask、不解码整图；LOD不能用于测量，GPU/图像缓存属viewport，不混入ROI owned bytes |
| command批量、历史steps/bytes、replace/undo/redo、Session/在途/队列 | 请求→排队→候选→CAS→临时释放；冷热开/关与长稳循环 | 全历史/Receipt/索引/在途输入输出都计内存；历史禁用/满预算、旧rev held reader计峰值 |
| HALCON布尔/栅格/提取/仿射、曲线细分ε、runs/tessellation碎片 | 每operator、pre/post校验、tsp保存恢复、native分配、materialize/Lease归还 | native bytes/object/worker/AOP/碎片/run上限；近似误差和拓扑分别验收；native调用不能强制中断 |
| Codec bytes/深度/未知格式、3D point块/选择比例 | encode/hash/decode、点块粗精包含与索引输出 | 不按输入bytes估整个展开量；处理取消/上限/错误不截断成成功 |
| deadline/取消位置、sink抛异常、重复关闭/断连 | CancelRequested→实际退出→资源归还、Drain观察延迟 | pending资源未消失时单列DrainUnknown；不得删失败样本求达标 |

逻辑预算不是“硬保证工作集”措辞。`MaxWorkingBytes`按本模块拥有的数组/租约实际capacity、BigInteger位长临时量、索引和历史预约；对象header/GC滞留另以实际managed/native/process峰值测量阈值验证，不能凭请求顶点估算即宣称峰值满足。分配前checked尺寸/总额，分块累计，回退/取消/后端错误全部解除可释放预约。Profile最多允许已知有限数值，不能取机器剩余内存自动无限扩容。

### 13.2 判定与诊断

缺采纳阈值、最低有效样本/预热/hash缺失→`NotEvaluated`；DrainUnknown或未收齐完整失败资源终态→`NotEvaluated`；完整证据的任一延迟/资源/失败阈值超限→`Failed`；全部完备且所有目标满足才`Passed`。正确性断言失败仍是测试失败，不因性能NotEvaluated忽略。两个不同消费者分别判定，不能平均混成单一Throughput承诺；没有同样本比较不宣称最快/零泄漏。

每操作诊断含OperationId/SessionId/Epoch、document/revision/Profile/Backend/Codec版本hash、Frame/Unit、method/representation/precision、原/输出hash、节点/环/洞/段对/run/碎片/point块计数、队列/线程、各单调时间点、预算预约/actual峰值、资源终态、错误/下一步。event不作持久事实库；host按授权脱敏并保存足以Replay的输入/版本闭包，ROI不记录Target/生产判定。

## 14. 独立发布、回退与两个真实消费者计划

发布顺序按真实能力门：Core/Interaction/Codec软件契约→算法工具接入→计量工具/独立测量工作台接入→HALCON/Spatial adapter Golden→WPF真实验证→各产品Shadow/Replay/现场；消费纯几何的工具不必等待HALCON。每DLL单独构建、test、版本/依赖锁定；公开包不能泄漏平台Shell/ViewModel/私有表或其它模块SDK。

- **消费者A：无UI算法调试/Replay工具**。Pixel Frame、固定polygon/curve、BCL Host，Validate/Preview/布尔派生Rasterized结果，严格保持D/F/V缺口、来源revision；用相同Commands验证主机批量API，取消不能影响其它Session。tool拥有采样域用途/算法Enabled，ROI不输出质量判定或修改生产Profile。
- **消费者B：计量工具及已批准独立 measurement-workbench**。Millimeter Frame、坐标模块公开资格关系，Circle/Ellipse/线/孔轮廓、约束/多选/UndoRedo/Codec；同一ROI DLL提供候选，metrology提供测量结果，viewport提供图像/3D资源与坐标投影，workbench只组合用户任务。无窗口BCL模式与可嵌入WPF模式计算内容一致，物理允差和量测放行由宿主，不由ROI或UI颜色决定。

两者各自提交Profile/数据hash、正常/缺支持/取消/关闭Replay与版本适用域；对共享Frame/同输入的纯计算结果逐字段比较，对单位不同的输入只能经已资格转换比较，不能仅修改Unit标签。检测宿主的目标绑定作为后续第三接入，不以两消费者“能画圆”证明全模块资格。

回退保留旧Core/Codec/AsunImageAdapter/Host配置完整包hash和原输入，不重算旧身份；停止新接纳、排空旧会话/输出租约，再切实例，新请求不会穿越旧epoch。未结束native留在旧隔离worker直到真实退出；Unknown commit查询原Owner/版本/ID，不在新版本重复提交。布局配置按WPF可信stream单独迁移，不混入ROI payload。新Schema只读未知原bytes可导出，不能强制降级写回旧客户.roi。

## 15. 逐切片六项准备与真正外部门

### 15.1 当前内容接收结论

六项定位以附录A.5为唯一结论表；既有算法/公开契约/切片范围保持。2026-10-11主控定向回读0.4.2-prep后，接收§10.1完整Pixel/Metric Profile、公开Factory、原Task、有界Root、业务/cleanup独立轴与确认移交及首次关闭恢复，§10.2 native lease/原ID/有限归还，§10.3双STA构造、Pointer桥、Detach及根恢复。**CoreSlice-01 / Interaction-01 / Codec-01 / Spatial-01纯软件切片的六项文档规格接收为 `ModuleCoreImplementationReady`；HALCON-01 / WPF-01仅接收指定接线/Owner恢复指导内容，真实适配/运行/viewport/性能/客户用途仍为 `PreparationIncomplete / NotReady`。** HostCommit-01仅为宿主端口边界，不授真实提交或产品事实写权。此接收不表示任何工程已创建、代码已实现、实际build/run/UI/性能或现场资格已通过；本轮只同步接收范围。

| 切片 | 本轮具体接收范围/状态 | 仅影响本片的后续接收/验证 |
|---|---|---|
| CoreSlice-01 | `ModuleCoreImplementationReady`（六项文档规格）；A.1/2、§3～6/10～14，BCL几何/编辑/CAS/历史、两个完整Host及有限Root恢复 | 权威仓库/代码快照绑定与后续明确代码任务；实际构建/运行/资源/性能验证未执行，不等产品Schema/设备 |
| Interaction-01 | `ModuleCoreImplementationReady`（软件六项文档规格）；A.3、§8.1/10/11/12，typed无UI HitTest/框选/BVH | 实现与全扫描对照、实际viewport桥接/资格另验，不复制上游算法 |
| Codec-01 | `ModuleCoreImplementationReady`（软件六项文档规格）；A.3、§8.2，roi-json-v1逐字段/顺序/哈希/未知策略 | 实际实现与roundtrip/损坏验证；未知旧客户格式只阻断该legacy importer，已知v1不等旧文件 |
| Spatial-01 | `ModuleCoreImplementationReady`（软件六项文档规格）；A.3、§3.2/3.4，Box/Sphere/Prism数学/点块/Frame/支持定义 | 实际软件验证；生产坐标资格、真实点云支持与物理精度另验，无关2D不阻断 |
| HALCON-01 | §10.2/A.4指定接线、原ID、独立lease与有限归还/Owner恢复指导限定内容接收；真实适配/资格 `PreparationIncomplete / NotReady` | 实际adapter/C#重载/封送调用编译、真实HALCON/代表Golden、误差/取消/资源/性能及客户用途；不核验算子存在或依赖授权 |
| WPF-01 | §10.3/A.6双STA公开构造、Pointer桥、Attach/Detach/迟到与根Owner恢复指导限定内容接收；真实运行/资格 `PreparationIncomplete / NotReady` | 实际25.2.3+viewport接线/编译、真实WPF、1920×1080UIA/焦点/操作/大图/视觉品质、性能及客户用途；不是依赖安装门 |
| HostCommit-01 | 仅接收A.4宿主Owner/CAS/授权/回查端口边界，不授真实提交或产品事实 | 正式产品Schema/权限、实际持久回执与unknown对账；只阻断持久业务接入 |

0.4.3-prep补充：2026-10-11主控已回读并限定内容接收§8.2/A.3的Serialization包RoiGeometryCodec公开无参创建、同一Core纯值验证复用、参数/资源/线程/期限与并发边界、最小消费及RG-K04～06；S-Codec创建入口文档欠账已关闭。0.4.2-prep的原Core/Interaction/Codec/Spatial接收范围保持，本次只接收Codec装配增量，不授实际构建/运行、native/WPF、性能或客户资格；metrology原Owner的消费接线由主控另行派发，本会话不改共享或消费者指导。

### 15.2 不能编造的外部事实

真正待外部来源的只有：消费者采纳物理允差/代表图像点云及观测支持、性能目标和负载；已资格坐标/标定关系与适用范围；未提供旧.roi版本字段/原始载荷；正式宿主权限/产品持久Schema/Owner回执。实际HALCON/WPF运行、构建、Golden、性能和现场/HIL是未执行验证门，不写成“缺SDK/封装可能没算子”来阻止内部开发。固定图形/数值样例可以做软件正确性，不能提供客户允差或产线节拍。

共享跨文件修正交主会话：旧PKG-020工程根/DEV-VIS-024历史Exact表述与v0.3映射、viewport/measurement-workbench公开接入端口/Frame/SelectionSet/租约形状、C-03/04产品映射和PageContract索引。旧原件保持原hash，不把本模块API写进别的模块指导制造第二权威。本会话未写共享文件/代码/原件/AsunImage内部。

### 15.3 0.4.4-prep 全部批准范围原会话自审结论

本永久会话完成本轮执行、第二消费视角审核、修复和定向文档验证，不再等待主控内容复核。覆盖§1.1及A.1～A.6全部已批准范围：几何/层次/批量/约束/历史、无UI互动、Codec与已知迁移政策、3D选择、HALCON typed桥、可嵌入WPF编辑器、宿主提交端口、预算/取消/排空/第二消费者与三语。**本轮可依据公开资料和既有权威决定的软件设计欠账已关闭**；新增实质补充是§7.4、§8.1、§9.3/9.5、§10.4及RG-H05/H06/W05。不是实现或运行验收结论；切片六项准入仍由A.5与DEV-GOV-010控制，既有四个软件Ready保持，HALCON/WPF实际资格保持NotReady。

| 剩余事实或执行门 | 明确Owner / 原会话职责 | 影响与关闭证据 |
|---|---|---|
| 权威仓库/代码快照与实现派发；本模块build/run、native重载/封送、资源/异常/Golden/性能、WPF/UIA/视觉品质 | 主会话负责仓库绑定和调度；IM-024原会话为实现/测试/修复Owner | 只在获派发切片内实现；真实Tests/测量及完整归还，不能以本文结构校验替代 |
| viewport桥接、Document→DIP和生产坐标/标定资格、外部native导出 | viewport及coordinate-geometry/标定资产原Owner；具体消费宿主持有Frame/租约 | IM-024 A.6/A.4端口不再待内部设计；外部Owner实现公开接线并验证实际变换/租约，仅阻相关跨模块/生产用途 |
| 客户物理允差、代表图像/点云/观测支持、性能Profile/负载和采纳值 | 算法工具/计量工具/检测宿主各消费者Owner，客户事实由该Owner取得并采纳 | 给版本/hash闭包和判定值，实际Golden/性能/计量/现场验收；软件固定例不能替代 |
| 旧.roi来源版本/字段/原载荷 | 提供该客户旧格式的宿主迁移Owner | 未提供保持ReadOnlyUnknown，仅阻该legacy importer，不阻roi-json-v1 |
| 正式Schema、权限/CAS/持久回执与Unknown对账 | HostCommit所属宿主领域Owner | 实际产品合同和持久事务验收，只阻HostCommit-01，不授ROI事实写权 |
| 共享入口/历史PKG映射、其它模块消费接线与PageContract索引 | 主会话串行整合共享文件，各模块永久原会话改自身指导 | §15.2既有交接事项；本轮不写共享/其它模块，不将跨文件接线改称本模块待设计 |

本轮已执行的最小文档验证：`python tools/validate_docs.py`通过；本指导§1～16/A.1～6唯一、围栏配对、相对链接、附录公开类型唯一与30字段Profile顺序核对通过；§9.5 XAML仅XML解析通过，所用DevExpress名称在本机25.2.3官方XML中存在。独立Fraction反例核Grid角点矩阵/恒等复合/非对称旋转，Pixel输入得到5 runs/25像素、mm Union/Intersection面积12/4；4/8邻域runs计数与独立逐像素BFS（含Int32边界与空集）一致。既有133字节payload与SHA-256保持。以上只校验指导/软件样例，不是受测DLL或真实算子执行；未执行任何产品build/run、HALCON、WPF/UIA、性能、HIL或客户现场验收。

HIL只在产品确依赖设备链时由该设备/产品Owner执行；纯ROI模块的HIL不适用，客户现场验收仍属产品Owner。没有依赖安装/授权/封装算子存在核验门。实际实现若发现契约矛盾，仍按DEV-GOV-010暂停受影响切片、先修唯一指导再继续，不能以当前自审结论跳过该纪律。

## 16. 依据与只读来源

### 16.1 平台权威与历史项目采纳

- [DEV-GOV-005](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)：独立DLL/无UI/双消费者、逐切片六门与BCL Exe验证约定。
- [DEV-VIS-024](../../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection%20Target%20Selection开发指导.md)：实际binary64精确谓词、固定片限制及Clipper来源；本模块当前实施范围/接口按本文，不据旧Exact总述承诺一般布尔。[PKG-020](../../shared-modules/packages/PKG-020_RoiGeometry.md)仅历史职责/迁移映射。
- [PKG-007](../../shared-modules/packages/PKG-007_Coordinates.md)、[ROI候选语义](../../13-contract-candidates/CONTRACT-CANDIDATES.md#roi-topology-contract-semantics)：坐标/支持域背景；正式跨模块坐标由原Owner契约，本文API不自动成为产品Schema。
- [PCBA-AOI ROI原件](../../references/project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/01-foundation/ROI几何与通用参数模型开发指导.md)：采纳草稿/预览/CAS、相对来源revision、未知提交回查、支持缺口与只读旧格式迁移。本文以DocumentId/ExpectedRevision/typed命令落实，不继续使用旧BaseGeometryId/Patch字段；批量失败采用本文整批原子，不能搬入历史逐项成功替代完整成功。
- [AsunMeasure快照入口](../../references/project-snapshots/AsunMeasure/20261004/README.md)：`RoiContracts/RoiGeometryService/RoiParameterValidator/RoiSkiaRenderAdapter`的职责分层、范围/交叉校验、确定性绘制和负向测试可借鉴。不复制WinForms/Skia/System.Drawing句柄、全局状态、测量派生值或客户流程；不迁移参考项目版本。
- [AsunControl快照入口](../../references/project-snapshots/AsunControl/20261004/README.md)：`original/ROI/ROI开发文档.md`、`ShapeBase.cs/DrawCore.cs/ShapeSerializer.cs`为旧控件能力/迁移来源。ShapeIndex/显示名不授业务身份，旧格式缺公开字段/原bytes只阻其importer。

原件保留来源快照及既有manifest哈希，不修改原件、不另建来源包；上述旧实现不是平台生产正确性证据。

### 16.2 HALCON 26.05 本地官方算子语义

唯一目标版本入口是 [halcon算子手册/operators](../../../halcon算子手册/operators/)，页面标识26.05.0.0。本轮实际读取以下页面并冻结§7/A.4，未执行算子：

- `union2_closed_polygons_xld/intersection_closed_polygons_xld/difference_closed_polygons_xld/symm_difference_closed_polygons_xld`：Even-Odd、自动闭合/自交处理、输出不带原contour reference；采纳材料逐组件Union与完整后检，不把reentrant/global误作共享对象任意释放安全。
- `union1/intersection/difference`：同grid离散集合支；`affine_trans_point_2d/affine_trans_region/affine_trans_contour_xld`：row/column与中心/角点补偿、Region插值/不可逆。
- `gen_region_polygon_filled/gen_region_contour_xld/gen_contour_region_xld`：舍入、Bresenham、filled/margin、center/border/border_holes、单像素往返非无损；`gen_contour_polygon_xld`：按显式Row/Col序列生成轮廓，闭合由模块完整端点序列保证，不猜自动闭合。
- `get_region_runs/gen_region_runs`：单Region有序runs/空tuple，gen不检查End>=Start，模块前检/按Object分调用。
- 0.4.4-prep新增直接读取 `gen_polygons_xld/get_polygon_xld/get_contour_xld/count_obj/select_obj/concat_obj/gen_empty_region/gen_rectangle1/connection/fill_up/get_system`：xld_poly与xld_cont不同，ramer Alpha严格正值、1-based选择且是共享引用、Region组件不等对象数、max_connection非0可能截断；§7.4明确转换/后检、grid、材料与输出取回，未执行算子。`crop_rectangle1`是图像裁剪而非Region裁剪，本模块不用。
- `distance_pc/test_self_intersection_xld`：点到segment距离与触边数值局限，诊断不替严格谓词；`select_points_object_model_3d`：多属性AND，仅点云外部adapter粗筛。
- `set_system`：当前线程tsp_clip_region/tsp_store_empty_region/tsp_neighborhood；同线程保存/设置/恢复不跨await。

平台直接使用已确定的AsunImage，所有算子可经ImageLibDotNet.cv2调用；仅具体C#重载/类型/封送有歧义时查公共签名或消费项目编译，不核验算子存在、不扫描内部、不直接引用HALCON程序集。25.11历史文字快照仅历史对照，不作26.05实施依据。

### 16.3 DevExpress 25.2.3 官方安装资料

本轮dxdocs未提供、无匹配WPF skill，官网请求403；直接读取本机 `C:/Program Files/DevExpress 25.2/Components/Offline Packages/` 下四份25.2.3官方XML（各包 `25.2.3/lib/net8.0-windows/`）：

| 包 / XML | 实际核对与采用 | 局限 |
|---|---|---|
| devexpress.wpf.docking / DevExpress.Xpf.Docking.v25.2.xml | DockLayoutManager/LayoutGroup/LayoutPanel、SaveLayoutToStream/RestoreLayoutFromStream | 布局流必须可信；不能当ROI格式或安全反序列化器 |
| devexpress.wpf.grid.core / DevExpress.Xpf.Grid.v25.2.xml | TreeListControl/TreeListView、KeyFieldName/ParentFieldName/TreeDerivationMode | 本轮补核DataControlBase.ItemsSource/SelectedItems/SelectionMode、TreeListControlBase.SelectionChanged、GridControl.SelectionChanged与MultiSelectMode.MultipleRow；§9.5固定绑定，实际编译/虚拟化性能另验 |
| devexpress.wpf.propertygrid / DevExpress.Xpf.PropertyGrid.v25.2.xml | SelectedObject/SelectedObjects多选代理 | 控件属性不替Core参数/批量校验 |
| devexpress.wpf.core / DevExpress.Xpf.Core.v25.2.xml | DevExpress.Xpf.Editors.Flyout.FlyoutControl、SuperTip/BarItem.SuperTip、ThemeManager.GetThemeName/SetThemeName | 只控件根主题，不改全局；XML不是真实UIA/语言/焦点/性能验收 |

使用本机已有25.2.3程序集，不下载NuGet替换、不安排安装/授权确认。A.6模块端口与§9任务流由本模块实施，viewport桥由其原Owner接线。

### 16.4 固定GitHub源码与实际测试研究

本轮已读取NetTopologySuite **v2.6.0 / commit `97d26b92586448b52d5a4f0c060217f94f882c75`** 的实际源码和测试；[固定树](https://github.com/NetTopologySuite/NetTopologySuite/tree/97d26b92586448b52d5a4f0c060217f94f882c75)。只采纳思想，不复制源码/引NTS产品依赖，也未执行上游测试。

| 固定树路径 | 采纳 | 限制 / 读取内容SHA-256 |
|---|---|---|
| src/NetTopologySuite/Algorithm/Orientation.cs | 明确定向谓词资格与合法ring前提 | IsCCW不证明自交/近退化环合法；`99ad41f579e022f61c98312bb7704a99a25d3ae8c98d960dbde7e2a599d1f3b0` |
| src/NetTopologySuite/Algorithm/RobustLineIntersector.cs | envelope筛选再定向、端点命中复制原值 | 浮点稳健不等一般精确构造；`95a30d69a34b5680a7a4b831eb8675272a6c85435abfedffe7c86538fb4740d6` |
| src/NetTopologySuite/Index/Strtree/STRtree.cs | build后只读索引与确定生命周期 | Insert非线程安全，Build后不插入；不直接移植semi-static可变树；`1a12383c5d9c9a023b531c7528f81249c13f490ca26fbc7b6f54098372d1fa0a` |
| src/NetTopologySuite/Index/Strtree/AbstractSTRtree.cs | Build锁/发布完成后释放构建暂存 | 本模块采用immutable median-split BVH，原实现不授本模块性能资格；`45eedf2497dd072eede0152514903e3ff4e46e4b06403ccf1bff4586e979d102` |

实际测试位置 `test/NetTopologySuite.Tests.NUnit/Algorithm/OrientationIndexTest.cs`（近重合三点、CCW/循环orientation一致）及 `.../Index/Strtree/STRtreeTest.cs`（空/范围查询、build后insert拒绝、remove/serialization）支持§11反例和索引对照；NUnit不迁入本模块测试栈。License.md为BSD-3-Clause并保留JTS/third-party条件，读取hash `81be2ef7f10ff8f27339062bf1a9182c1f8b3a4fe7882699fc328a1a8f8b2693`；csproj为netstandard2.0/2.1、2.0分支System.Memory4.6.0，hash `edaa37a4c4637997f9f7a33ea0e2f4cce96b39d9a272dad0fe487710fbdc0c1f`。不据README/星数认定生产质量。

复用DEV-VIS-024 §5.3已读取的Clipper2 **tag Clipper2_1.5.4 / commit `ef88ee97c0e759792e43a2b2d8072def6c9244e8` / Boost许可**研究及其实际测试：采纳PolyTree/FillRule/显式失败状态思想；整数舍入、低层bool、路径数不等组件数是限制，未批准本模块依赖或替换HALCON。输入/版本未变，不重复下载全库。

本轮为 §1A 双跑门禁定向读取 OpenCV 固定 commit `a0cda081f8d769f40ab2f4904738b4787b44d07c` 的 `modules/geometry/src/geometry.cpp` 与 `modules/geometry/test/test_convhull.cpp`（本地已读快照见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)；该快照共17个文件，仅覆盖 `geometry`/`imgproc`/`stitching`，**不含** XLD/Region 转换与多边形布尔，故本模块双跑仍只有"HALCON vs 自建托管参照"两路）：`contourArea`（438行）对 `CV_32F`/`CV_32S` 两种深度各走一遍并以 `fabs` 取绝对面积，`arcLength`（471行）按 `is_closed` 选择首尾连接、点数≤1直接返回0；`test_convhull.cpp` 的 `Imgproc_FitLine`（248/264行）验证拟合直线的主方向稳定，`ordering_4539`（288行）验证凸包/缺陷的**点序**约定。采纳：**面积/周长是依赖点序与深度类型的聚合量**（支撑 §1A"聚合量仅诊断、顶点与拓扑才是强门禁"）、**点序必须显式冻结**（支撑 §3 顶点序与拓扑的强门禁）；限制：这些聚合量的两路差异不引入产品判定，未构建或运行上游测试，不引入 OpenCV runtime。实际读取 SHA-256（本地为 CRLF，下列为 LF 归一化值，`geometry.cpp` 与 REF-002 登记一致）：`geometry.cpp`=`250a4dc2618f979253ce4b5b279847b68c1738cfc63bc9f40877844420600466`；`test_convhull.cpp`=`526763142413487383b8bb659ca921d9df3bfe9befe14ea3427e372e6ce48380`；根 `LICENSE`（Apache-2.0）=`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`。

### 16.5 .NET 生命周期依据

[Cancellation in Managed Threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)明确协作取消请求不等工作已停止；据此§6/A.2/A.4/A.6把调用观察期限、实际排空和资源归还分开。Stopwatch单调期限仅当前进程有效；ImmutableArray是值内容不可变投影，数组内容相等须显式比较；JSON规范为本模块具名roi-json-v1，不声称JCS。上述官方行为与自有规约均仍须对应C#测试，不以文档读取代替运行。

本轮Host依据链接：[Task.WaitAsync](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0)（观察包装Task超时不证明原Task退出）、[Thread.IsBackground](https://learn.microsoft.com/en-us/dotnet/api/system.threading.thread.isbackground?view=net-10.0)（foreground保持进程存活）、[Window.Closing](https://learn.microsoft.com/en-us/dotnet/api/system.windows.window.closing?view=windowsdesktop-10.0)（Cancel保留窗口）、[Dispatcher.InvokeAsync](https://learn.microsoft.com/en-us/dotnet/api/system.windows.threading.dispatcher.invokeasync?view=windowsdesktop-10.0)（保留DispatcherOperation.Task并解包异步委托）。2026-10-11新增页面联网读取遇DNS不可达，未声称本轮读取全文；原协作取消依据复用，Host规约按BCL/WPF公开签名给出，实际编译/运行验证仍未执行。


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

## 附录 A：Module API Contract v0.3（逐切片唯一公开契约）

这是模块自有 API；不冻结产品 Schema/Owner/数据库或厂商内部。以下 C# 是**公开声明形状**，接口/record可作为实施输入，按DLL namespace分文件；具体方法体按正文完成，不能把有方法体缺省的类片段宣称已编译。全部数组使用 System.Collections.Immutable 的 ImmutableArray，默认(default)数组非法、Empty明确空集合；所有实例参数显式，隐藏全局服务禁止。API v0.2全部替换，不保留两套兼容候选。v0.3的Core/Interaction/Codec/Spatial规格及后续Codec装配接收见§15/A.5，仍属未实现声明：RoiOperationReceipt去掉CanAdopt、RoiOperationQuery增加独立Adoption；未有已实现消费者，不冒称二进制兼容，正式发布后此类结构变化必须升破坏版本。

### A.1 CoreSlice-01 值对象与入口

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
namespace Asun.Modules.RoiGeometry;

public enum GeometryUnit { Pixel, Millimeter, Micrometer }
public enum AxisConvention { ColumnRowPixelCenters, RightHandedPhysicalXY, RightHandedPhysicalXYZ }
public enum RetentionScope { ProcessLocalEphemeral }
public enum RoiOperationState
{
    Accepted, Running, CancelRequested, Completed, PreviewReady,
    Rejected, Cancelled, DeadlineExceeded, Stale, Faulted, Unknown
}
public enum RoiResourceState { Idle, Working, Draining, Drained, ResourcesReleased }
public enum RoiSessionState { Open, Draining, Drained, Disposed }
public enum RoiDrainStatus { Drained, DrainUnknown, Disposed }
public enum RoiEventKind
{
    RequestRejected, Accepted, Running, LogicalResult, CancelRequested,
    Draining, Drained, ResourcesReleased, Terminal, Diagnostic
}
public enum RoiEditMode { Apply, Preview }
public enum RoiResultKind { Value, Empty, None }
public enum Representation { AnalyticVector, Tessellated, RasterizedRegion }
public enum PrecisionClass { StoredValues, BoundedApproximation, BackendNumeric, DiscreteGridExact }

public readonly record struct Point2(double X, double Y);
public readonly record struct Vector2(double X, double Y);
public readonly record struct Affine2D(
    double M11, double M12, double Tx, double M21, double M22, double Ty);
public sealed record RoiFrame(string Id, GeometryUnit Unit, AxisConvention Axes);
public sealed record RoiVertex(string Id, Point2 Point);
public sealed record RoiRing(string Id, ImmutableArray<RoiVertex> Vertices);
public sealed record RoiComponent(string Id, RoiRing Outer, ImmutableArray<RoiRing> Holes);
public abstract record RoiShape;
public sealed record PointShape(Point2 Center) : RoiShape;
public sealed record SegmentShape(RoiVertex Start, RoiVertex End) : RoiShape;
public sealed record CurveShape(
    Point2 Center, Vector2 U, Vector2 V, double StartRadians,
    double SweepRadians, bool Closed) : RoiShape;
public sealed record RectangleShape(Point2 Center, Vector2 U, Vector2 V) : RoiShape;
public sealed record PolylineShape(ImmutableArray<RoiVertex> Vertices) : RoiShape;
public sealed record PolygonShape(ImmutableArray<RoiComponent> Components) : RoiShape;
public enum RoiSupportStatus { NotProvided, Partial, Complete }
public sealed record RoiSupportDomains(
    RoiSupportStatus Status, PolygonShape? DesignDomain,
    PolygonShape? DataDomain, PolygonShape? ObservedDomain);
public sealed record RoiSource(
    string SourceId, long Revision, string Sha256, string FrameId,
    string Method, double PositionErrorBound, RoiSupportDomains Support);
public sealed record SelectionSet(ImmutableArray<string> NodeIds);
public readonly record struct VertexRef(string NodeId, string VertexId);
public abstract record RoiConstraint(string Id);
public sealed record FixedLengthConstraint(
    string Id, VertexRef A, VertexRef B, double Length, double Tolerance) : RoiConstraint(Id);
public sealed record CoincidentConstraint(
    string Id, VertexRef A, VertexRef B, double Tolerance) : RoiConstraint(Id);
public sealed record AxisConstraint(
    string Id, VertexRef A, VertexRef B, bool Horizontal, double Tolerance) : RoiConstraint(Id);
public sealed record EqualLengthsConstraint(
    string Id, VertexRef A, VertexRef B, VertexRef C, VertexRef D,
    double Tolerance) : RoiConstraint(Id);
public sealed record AspectRatioConstraint(
    string Id, string RectangleNodeId, double Ratio, double Tolerance) : RoiConstraint(Id);
public sealed record RoiNode(
    string Id, string? ParentId, int ZOrder, bool Visible, bool Locked,
    RoiShape? Shape, ImmutableArray<RoiConstraint> Constraints, RoiSource? Source);
public sealed record GeometrySnapshot(
    string DocumentId, long Revision, RoiFrame Frame, ImmutableArray<RoiNode> Nodes);
public sealed record ValidationProfile(
    string Id, string Revision, string Hash, RoiFrame Frame,
    double MaxAbsCoordinate, double MinLength, double MaxCondition,
    int MaxNodes, int MaxVertices, int MaxRings, int MaxComponents,
    long MaxCandidatePairs, long MaxWorkingBytes, long MaxOutputBytes,
    int MaxUndoSteps, long MaxUndoBytes, int MaxInFlight, int MaxPending,
    int MaxReceipts, int CheckBatchSize, double MaxCurveDeviation,
    int MaxTessellationVertices, int MaxSerializedBytes, int MaxJsonDepth,
    TimeSpan CloseTimeout, double SpatialBasisTolerance,
    int MaxBackendWorkers, int MaxHalconParallelism, int MaxPointBlockSize, int MaxRuns);

// Timestamp 来自当前进程 Stopwatch.GetTimestamp，Frequency=Stopwatch.Frequency。
// 创建/到期公式见A.2；此值对象没有隐藏计时方法。
public readonly record struct MonotonicDeadline(long Timestamp, long Frequency);
public sealed record RoiOpenRequest(
    string OperationId, string SessionId, GeometrySnapshot InitialSnapshot,
    ValidationProfile Profile, MonotonicDeadline Deadline);
public sealed record RoiOpenReceipt(
    string OperationId, IRoiGeometryCore? Core, ImmutableArray<RoiError> Errors);
public sealed record RoiValidationRequest(
    string OperationId, GeometrySnapshot Snapshot, ValidationProfile Profile,
    MonotonicDeadline Deadline);
public sealed record RoiValidationResult(
    string OperationId, bool IsValid, RoiOperationState State,
    bool ResourcesReleased, ImmutableArray<RoiError> Errors);
public abstract record RoiEditCommand;
public sealed record CreateCommand(RoiNode Node) : RoiEditCommand;
public sealed record ReplaceCommand(RoiNode Node) : RoiEditCommand;
public sealed record DeleteCommand(ImmutableArray<string> NodeIds) : RoiEditCommand;
public sealed record TransformCommand(
    ImmutableArray<string> NodeIds, Affine2D Transform) : RoiEditCommand;
public sealed record ReparentCommand(
    ImmutableArray<string> NodeIds, string? ParentId) : RoiEditCommand;
public sealed record UndoCommand(int Steps) : RoiEditCommand;
public sealed record RedoCommand(int Steps) : RoiEditCommand;
public sealed record RoiEditRequest(
    string OperationId, string SessionId, long Epoch, long ExpectedRevision,
    string ProfileRevision, RoiEditMode Mode,
    ImmutableArray<RoiEditCommand> Commands, MonotonicDeadline Deadline);
public sealed record RoiOperationReceipt(
    string OperationId, string SessionId, long Epoch, long BaseRevision,
    long? OutputRevision, RoiOperationState State, RoiResultKind ResultKind,
    GeometrySnapshot? Candidate, bool Changed,
    bool ResourcesReleased, bool IsTerminal, RetentionScope RetentionScope, bool Durable,
    ImmutableArray<RoiError> Errors);
public sealed record RoiError(
    string Code, string MessageKey, string RecoveryKey, string OperationId,
    string? NodeId, string? FieldPath, string Diagnostic);
public sealed record RoiOperationEvent(
    long Sequence, RoiEventKind Kind, string OperationId, string SessionId,
    long Epoch, long Revision, RoiOperationState? OperationState,
    RoiResourceState ResourceState, long StopwatchTimestamp);
public interface IRoiEventSink
{
    // 不阻塞/不回调Core/不运行UI；实现者有界排队，false表示该投影未接收。
    bool Publish(RoiOperationEvent notification);
}
public sealed record RoiSessionSnapshot(
    string SessionId, long Epoch, RoiSessionState State,
    GeometrySnapshot Snapshot, string ProfileRevision,
    int UndoDepth, int RedoDepth, ImmutableArray<string> PendingOperationIds);
public sealed record RoiAdoptionProjection(
    string OperationId, RoiSessionState SessionState, long ObservedEpoch,
    long ObservedRevision, string ProfileRevision, bool CanAdopt);
public sealed record RoiOperationQuery(
    bool Found, RoiOperationReceipt? Receipt, RoiAdoptionProjection? Adoption);
public sealed record RoiDrainReceipt(
    string SessionId, RoiDrainStatus Status, RoiSessionState SessionState,
    MonotonicDeadline Deadline, bool ResourcesReleased, bool NativeResourcesOwned,
    ImmutableArray<string> PendingOperationIds, ImmutableArray<RoiError> Errors);
public sealed class RoiDrainIncompleteException : Exception
{
    public RoiDrainReceipt Receipt { get; }
    public RoiDrainIncompleteException(RoiDrainReceipt receipt)
        : base("ROI session drain is incomplete") { Receipt = receipt; }
}
public interface IRoiGeometryFactory
{
    RoiOpenReceipt Open(
        RoiOpenRequest request, IRoiEventSink? eventSink,
        CancellationToken cancellationToken = default);
}
public interface IRoiGeometryCore : IAsyncDisposable
{
    RoiSessionSnapshot Query();
    RoiOperationQuery QueryOperation(string operationId);
    RoiValidationResult Validate(
        RoiValidationRequest request, CancellationToken cancellationToken = default);
    RoiOperationReceipt Apply(
        RoiEditRequest request, CancellationToken cancellationToken = default);
    ValueTask<RoiOperationReceipt> PreviewAsync(
        RoiEditRequest request, CancellationToken cancellationToken = default);
    ValueTask<RoiDrainReceipt> DrainAsync(
        MonotonicDeadline deadline, CancellationToken cancellationToken = default);
}
```

- Factory 具体实现 `RoiGeometryFactory` 在 Core DLL，有公开无参数构造，不访问外部服务；Open检查初始Snapshot/Frame/Profile/ID/全部结构拓扑/预算/token/deadline，失败不创建 Core。InitialSnapshot 空 Nodes 合法，Default array 非法。
- Profile.Hash为配置来源闭包，不授执行资格；Open 验证格式和与宿主传入配置匹配，不能因 hash 非空就相信外部几何。固定SessionId先核，当前epoch只用于§5步骤4的新ID接纳；旧ID同payload在关闭/换epoch后仍可回放；Apply Mode 必须 Apply，PreviewAsync Mode 必须 Preview，错配 InvalidArgument。
- Validate 是独立只读请求，OperationId由宿主给，无 epoch/幂等写事务，不修改会话；失败 IsValid=false，Errors非空，ResourcesReleased为实际临时工作退出。新ID编辑请求须以当前Query Snapshot为基线且ProfileRevision相同，实例Profile.Id/Hash固定；已登记回放优先按§5；不能只因Revision同字串就替换配置。
- §5是原ID回放唯一优先级，Apply/Preview返回不可变事实Receipt，不带CanAdopt；当前资格另QueryOperation.Adoption。Preview Candidate.Revision=BaseRevision、不发布；Apply成功且Changed才BaseRevision+1，no-op保持原revision。失败OutputRevision=null/Candidate=null/Changed=false。合法Empty Nodes或布尔空结果为ResultKind.Empty，不混为None；Completed/PreviewReady不表示质量合格。
- Query返回不可变当前状态；Drain/Disposed后仍Query最后只读Snapshot和关闭状态，QueryOperation仍按§5保留/返回原回执及当前Adoption=false。资源归还不等托管墓碑已丢弃；未知ID为Found=false/Receipt=null/Adoption=null，不猜失败或复活Core。

### A.2 Deadline、线程、生命周期与兼容

`MonotonicDeadline` 不可序列化为跨进程执行期限；宿主创建 `timestamp=checked(now + ceil(timeout.TotalSeconds*Stopwatch.Frequency))`，now取一次GetTimestamp、timeout有限正数。Core验证Frequency、timestamp和溢出；到期是 `now>=timestamp`，默认值非法，接纳后不能延长。CloseTimeout从Profile建立独立关闭观察期限，不能复用已经到期的编辑deadline伪造释放。

按§5先查原ID；以下token/到期规则仅适用于新ID或原已接纳执行，不能覆盖原回放。新ID接纳前token取消→Rejected/Cancelled原因短路径；接纳后发布前撤销→Draining后真实ResourcesReleased才Cancelled；发布前deadline到期→同顺序后DeadlineExceeded。发布和取消请求使用同一线性化检查，已发布成功不能被晚取消重写。Preview完成时revision不同→Stale、无Candidate。DrainUnknown含未退出OperationIds，SessionState=Draining、不发布Terminal、不释放在用工作；再次Drain只查询同一关闭意图。资源真实退出后才Drained/ResourcesReleased。DisposeAsync在预算内排空失败抛带Receipt的RoiDrainIncompleteException，仍可Drain/Query，禁止空catch标已关。

Core API正式发布后的错误/单位/序列化语义变更必须升破坏版本并更新本文；v0.3 Prep声明修订与规格接收范围已在附录入口及§15明示；新可选只读字段可Minor，但未知类型仍拒执行。外部程序集、C-03/C-04/产品Commit映射按宿主显式Adapter，不把本附录字段自动宣布平台Schema获批。

### A.3 Interaction-01、Codec-01、Spatial-01 公开端口

```csharp
// Interaction/Spatial均在Asun.Modules.RoiGeometry；Codec enum/两个result/interface/具体class在Asun.Modules.RoiGeometry.Serialization。
// 实施时按namespace分文件，不能把整段直接放同一file-scoped namespace。
public enum HitPart { Handle, Vertex, Edge, Interior }
public enum HitSelectionMode { Point, WindowContains, CrossingIntersects }
public readonly record struct Bounds2(double MinX, double MinY, double MaxX, double MaxY);
public sealed record HitTestRequest(
    string OperationId, GeometrySnapshot Snapshot, SelectionSet Selection, Affine2D DocumentToViewport,
    Point2 ViewportPoint, Bounds2? ViewportBox, double ToleranceDip,
    HitSelectionMode Mode, int MaxCandidates, MonotonicDeadline Deadline);
public sealed record HitCandidate(
    string NodeId, string? ElementId, HitPart Part, double DistanceDip,
    double ErrorBoundDip, int ZOrder, bool Locked);
public sealed record HitTestResult(
    string OperationId, long Revision, RoiOperationState State,
    bool AmbiguousCandidates, ImmutableArray<HitCandidate> Candidates,
    ImmutableArray<RoiError> Errors);
public interface IRoiGeometryInteraction
{
    HitTestResult HitTest(
        HitTestRequest request, ValidationProfile profile,
        CancellationToken cancellationToken = default);
}
public sealed record RoiCurveSuggestionRequest(
    string OperationId, string InputSha256, RoiFrame Frame, CurveShape Curve,
    double MaxDeviation, MonotonicDeadline Deadline);
public sealed record RoiCurveSuggestionResult(
    string OperationId, RoiOperationState State, string FormulaVersion,
    string InputSha256, string ProfileHash, int? Segments, int? Vertices,
    double? GeometricErrorBound, ImmutableArray<RoiError> Errors);
public interface IRoiCurveTessellationPlanner
{
    RoiCurveSuggestionResult Suggest(
        RoiCurveSuggestionRequest request, ValidationProfile profile,
        CancellationToken cancellationToken = default);
}
public enum RoiDecodeState { DraftImport, ReadOnlyUnknown, Rejected }
public sealed record RoiEncodeResult(
    ImmutableArray<byte> Bytes, string Sha256, ImmutableArray<RoiError> Errors);
public sealed record RoiDecodeResult(
    RoiDecodeState State, GeometrySnapshot? Snapshot,
    ImmutableArray<byte> RawPayload, string RawSha256, ImmutableArray<RoiError> Errors);
public interface IRoiGeometryCodec
{
    RoiEncodeResult Encode(
        string operationId, GeometrySnapshot snapshot, ValidationProfile profile,
        MonotonicDeadline deadline, CancellationToken cancellationToken = default);
    RoiDecodeResult Decode(
        string operationId, ImmutableArray<byte> bytes, ValidationProfile profile,
        MonotonicDeadline deadline, CancellationToken cancellationToken = default);
}
// 此类仅在Serialization工程，namespace Asun.Modules.RoiGeometry.Serialization。
// 这是公开构造声明片段；同一partial类的Encode/Decode实现按上方接口与§8.2完成。
// 不将仅有构造片段宣称完整实现或已编译程序集。
public sealed partial class RoiGeometryCodec : IRoiGeometryCodec
{
    public RoiGeometryCodec() { } // 无参数/外部服务，构造不启动工作、不创建Core/native会话。
}
public readonly record struct Point3(double X, double Y, double Z);
public enum SpatialRoiKind { Box, Sphere, PlanarPrism }
public abstract record SpatialRoi(string FrameId, GeometryUnit Unit);
public sealed record BoxRoi(
    string FrameId, GeometryUnit Unit, Point3 Min, Point3 Max) : SpatialRoi(FrameId, Unit);
public sealed record SphereRoi(
    string FrameId, GeometryUnit Unit, Point3 Center, double Radius) : SpatialRoi(FrameId, Unit);
public sealed record PlanarPrismRoi(
    string FrameId, GeometryUnit Unit, Point3 Origin, Point3 U, Point3 V,
    Point3 Normal, PolygonShape Footprint, double MinZ, double MaxZ) : SpatialRoi(FrameId, Unit);
public sealed record RoiPointBlockSource(
    string SourceId, long Revision, string Sha256, RoiFrame Frame, RoiSupportStatus Support);
public sealed record SpatialSelectionRequest(
    string OperationId, RoiPointBlockSource Source,
    SpatialRoi Roi, ImmutableArray<Point3> Points, int StartPointIndex,
    int MaxSelectedIndices, MonotonicDeadline Deadline);
public sealed record SpatialSelectionResult(
    string OperationId, RoiOperationState State, RoiPointBlockSource Source, int ProcessedCount,
    ImmutableArray<int> SelectedIndices, ImmutableArray<RoiError> Errors);
public interface ISpatialRoiEvaluator
{
    SpatialSelectionResult Select(
        SpatialSelectionRequest request, ValidationProfile profile,
        CancellationToken cancellationToken = default);
}
```

HitTest失败Candidates空，不截断MaxCandidates后冒完整；无命中成功空。具体实现RoiGeometryInteraction/SpatialRoiEvaluator在Core、RoiGeometryCodec在Serialization，均公开无参数构造、无外部服务/静态可变状态；Grid/Pointer/Dispatcher不入API。Profile Frame必须匹配Snapshot；DIP明确来自viewport，不是物理Tolerance。3D点块必须有限且Points.Length<=MaxPointBlockSize，Source.Revision/Sha256/Frame明确，Source.Frame匹配Roi.FrameId/Unit，物理空间拒Pixel。Source.Support只是外部声明，不因点均有限就改Complete；StartPointIndex加法checked、输出为全局原始point索引；任一坏点/预算/取消整块拒绝，ProcessedCount仅诊断，SelectedIndices空。块间拼接和缺支持由数据宿主编排，不用部分处理标全域成功。3D保边界Close政策按§3.4，球距离平方按§3的dyadic整数比较避免中间double溢出，orthonormal容差来自ValidationProfile.SpatialBasisTolerance，仅执行§3.2冻结的dyadic范数平方/dot/cross平方判据及 `1+e<=K²*(1−e)` 精确比较，不存在浮点norm/sqrt减1或double MaxCondition²分支，不静默正交化。未经资格的映射只可软件测试。Codec result自己拥有不可变bytes，无native租约；Encode失败Bytes=Empty/Sha256为空字串/Errors非空，成功hash为64位小写hex。Decode Rejected时Snapshot=null，RawPayload不要求复制原件（超bytes预算时必须Empty），调用者仍拥有原bytes；ReadOnlyUnknown在预算内保留完整原bytes，不截断后假装可导出。没有Save/Load/FilePath/DatabaseId。

### A.4 HALCON-01 与 HostCommit-01

```csharp
public enum RoiBooleanKind { Union, Intersection, Difference, Xor }
public enum RoiBackendOperation { Boolean, Rasterize, ExtractBoundary, Transform }
public enum RoiRasterPolicy { HalconRoundedFilled26, HalconBresenhamFilled26 }
public sealed record RoiGrid(
    string Id, int Width, int Height, Point2 Origin,
    double StepX, double StepY, bool ClipExplicitly, int Neighborhood);
public abstract record RoiBackendOperand(string Id);
public sealed record RoiVectorOperand(
    string Id, GeometrySnapshot Snapshot, string Sha256) : RoiBackendOperand(Id);
public sealed record RoiRunsOperand(
    string Id, RoiFrame Frame, RoiGrid Grid, ImmutableArray<RoiRun> Runs,
    RoiSource Source) : RoiBackendOperand(Id);
public enum RoiOperandRole { Material, Subject, Clip }
public sealed record RoiBackendSource(
    string OperandId, RoiOperandRole Role, string SourceId, long Revision,
    string Sha256, string FrameId);
public sealed record RoiBackendReport(
    double CurveErrorBound, double? CoordinateErrorBound, bool Discretized,
    bool Clipped, ImmutableArray<RoiBackendSource> Sources);
public sealed record RoiBackendRequest(
    string OperationId, string SessionId, long Epoch, RoiBackendOperation Operation,
    RoiBooleanKind? BooleanKind, ImmutableArray<RoiBackendOperand> Operands,
    Representation OutputRepresentation, RoiRasterPolicy? RasterPolicy,
    RoiGrid? Grid, Affine2D? Transform, double MaxDeviation, bool RequireBoundedCoordinates,
    ValidationProfile Profile, MonotonicDeadline Deadline);
public sealed record RoiGeometryLeaseInfo(
    string LeaseId, Representation Representation, PrecisionClass Precision,
    string FrameId, GeometryUnit Unit, RoiGrid? Grid, long Bytes,
    int Components, int Holes, string BackendVersion, string Method, RoiBackendReport Report);
public interface IRoiGeometryLease : IAsyncDisposable
{
    RoiGeometryLeaseInfo Info { get; }
    // 无native句柄泄漏；消费者只可请求有界、类型化的托管快照。
    ValueTask<RoiMaterializationReceipt> MaterializeAsync(
        RoiMaterializationRequest request, CancellationToken cancellationToken = default);
    RoiMaterializationReceipt? QueryMaterialization(string operationId);
    ValueTask<RoiDrainReceipt> DrainAsync(
        MonotonicDeadline deadline, CancellationToken cancellationToken = default);
}
public sealed record RoiMaterializationRequest(
    string OperationId, long MaxBytes, MonotonicDeadline Deadline);
public sealed record RoiMaterializationReceipt(
    string OperationId, RoiOperationState State, bool IsTerminal, bool ResourcesReleased,
    GeometrySnapshot? Vector,
    ImmutableArray<RoiRun> Runs, ImmutableArray<RoiError> Errors);
public readonly record struct RoiRun(int ObjectIndex, int Row, int StartColumn, int EndColumn);
public sealed record RoiBackendReceipt(
    string OperationId, RoiOperationState State, RoiResultKind ResultKind,
    IRoiGeometryLease? Lease, bool TemporaryResourcesReleased, bool IsTerminal,
    ImmutableArray<RoiError> Errors);
public sealed record RoiBackendOpenRequest(
    string OperationId, string SessionId, ValidationProfile Profile, MonotonicDeadline Deadline);
public sealed record RoiBackendOpenReceipt(
    IGeometryBackendPort? Backend, ImmutableArray<RoiError> Errors);
public sealed record RoiBackendSnapshot(
    string SessionId, long Epoch, RoiSessionState State,
    ImmutableArray<string> PendingOperationIds, ImmutableArray<string> OutstandingLeaseIds);
public interface IRoiGeometryBackendFactory
{
    RoiBackendOpenReceipt Open(
        RoiBackendOpenRequest request, IRoiEventSink? sink,
        CancellationToken cancellationToken = default);
}
public interface IGeometryBackendPort : IAsyncDisposable
{
    RoiBackendSnapshot Query();
    ValueTask<RoiBackendReceipt> ExecuteAsync(
        RoiBackendRequest request, CancellationToken cancellationToken = default);
    RoiBackendReceipt? QueryOperation(string operationId);
    ValueTask<RoiDrainReceipt> DrainAsync(
        MonotonicDeadline deadline, CancellationToken cancellationToken = default);
}
// 仅此具体factory位于Asun.Modules.RoiGeometry.AsunImage；端口/DTO在Core。
// 公开构造声明片段，Open实现按上方接口及§7/§10.2，不是已编译实现。
public sealed partial class RoiAsunImageBackendFactory : IRoiGeometryBackendFactory
{
    public RoiAsunImageBackendFactory() { } // 构造不启动native/worker；Open才创建有界会话。
}
public enum RoiCommitState { Rejected, Committed, Conflict, Unknown }
public sealed record RoiCommitRequest(
    string OperationId, string OwnerId, string BaseDocumentId, long ExpectedRevision,
    GeometrySnapshot Candidate, string AuthorizationSnapshotId,
    MonotonicDeadline Deadline);
public sealed record RoiCommitReceipt(
    string OperationId, RoiCommitState State, string? DurableReceiptId,
    long? OwnerRevision, ImmutableArray<RoiError> Errors);
public interface ICommitPort
{
    ValueTask<RoiCommitReceipt> CommitAsync(
        RoiCommitRequest request, CancellationToken cancellationToken = default);
    ValueTask<RoiCommitReceipt> QueryAsync(
        string operationId, MonotonicDeadline deadline,
        CancellationToken cancellationToken = default);
}
```

AsunImage DLL公开无参数实现RoiAsunImageBackendFactory（完整namespace见§8.3，公开构造声明见上方）；Open检查Profile/Frame/期限/预算后创建有界独立worker会话，失败Backend=null、不残留worker。新Backend.Query().Epoch=0；Execute固定SessionId结构身份先核，原ID/完整载荷查表优先同§5（包括原deadline，冲突不覆盖登记项），仅新ID要求当前SessionId/Epoch及完整Profile逐值相等；Drain封住新操作、只首次epoch递增、取消在途、等待未归还lease，未完成保持Draining。backend.DisposeAsync用Profile.CloseTimeout，未退出抛RoiDrainIncompleteException、保留可Query/Drain实例，完成才Disposed；sink同A.1非阻塞/故障隔离。读取Query返回有界不可变状态；接口不是静态全局实例，无隐藏Open/native初始化依赖。

Backend请求的RoiVectorOperand只抽取明确Shape叶节点，Group/hidden不产生算法启用推断；每Snapshot表示集合，Difference首项S，其余C，Union/Intersection/Xor按Ordinal operand.Id固定fold顺序；Difference保留首项Subject、剩余按Ordinal Id组成Clip联合。空operand列表非法，合法空Snapshot为Empty集合；布尔角色/请求hash绑定。Rasterized输出必须Grid，Physical→Pixel映射须先显式完成；native输入不在v0.3 API范围：外部Owner在其租约有效期导出typed RoiRunsOperand，退出导出调用后自行归还租约；本端口不接raw句柄/隐式lease。图像域参数状态统一§7，Ellipse/Curve先有界离散；需要严格Exact且无已资格路线拒绝Unsupported，不静默换Region。

Backend成功临时资源退出后给输出lease；资源峰值包含输出直到消费者归还。失败/取消/超时无lease；无法证明退出Receipt State=Running/Unknown、IsTerminal=false且TemporaryResourcesReleased=false、无lease，Query/Drain继续原请求。Materialize只给Vector或同Grid Runs；不全图铺bitmask；raw句柄禁止进入VM。ResultKind.Empty仍需确定后端实际成功。Committed只存在HostCommit端口，由Owner CAS/权限/持久回执证明，Unknown先Query同Id；该端口不由Core实现，未采纳产品Schema只阻断HostCommit-01。断连、重复、授权变化与跨Owner事务由宿主处理，不能给ROI隐含写权。

IsTerminal=true只允许Completed/PreviewReady/Rejected/Cancelled/DeadlineExceeded/Stale/Faulted且本次临时资源已退出；Unknown是非终态观察，不能发Terminal，Query Found=false另表未知ID。Core纯计算不产生不确定成功终态；已发布CAS成功只能Completed，释放未完仍非终态。Backend Completed只表示临时资源退出，lease仍归唯一消费者，不等会话全部释放。Materialize同样先按OperationId/完整RoiMaterializationRequest载荷（含原deadline）查表、同payload优先原回执/在途观察、异payload Conflict，再仅新ID核lease关闭状态/token/deadline/预算；观察期限结束且native仍在运行时返回Running、IsTerminal=false、ResourcesReleased=false、无Vector/Runs，保留工作并通过QueryMaterialization回查。lease关闭禁止新materialize，等待全部工作，再释放输出native；lease.DisposeAsync用冻结CloseTimeout，失败抛RoiDrainIncompleteException并可继续Query/Drain。后端Drain等待算子和全部未归还lease，不主动释放消费者在用lease。重复Query的lease是同一Owner引用，归还后留墓碑、Materialize拒Disposed，不发第二份有效租约。lease排空Receipt.SessionId为LeaseId，PendingOperationIds为其materialize ID。

RoiGrid中心坐标为Origin+(column*StepX,row*StepY)，StepX/StepY有限正值且同Frame长度单位、Width/Height>0、Neighborhood=4或8；Physical Vector必须先显式转Pixel Frame，不以grid标签转换单位。ClipExplicitly=true才裁[0,Width−1]×[0,Height−1]，false允许有界负runs。runs按ObjectIndex/Row/StartColumn升序，每行Start<=End、同对象同行不重叠/相邻（先显式合并）；非空ObjectIndex从0连续，空Runs表示一个空集合，不猜组件数。MaxRuns/MaxOutputBytes同时限制。gen_region_runs不检查End>=Start，适配前必须检查；一对象一调用，Region tuple最终按材料Union。不同Grid/Frame禁止隐式重采样。

操作组合冻结：Boolean至少1 operand、BooleanKind非null/Transform=null，全Vector闭面积（Closed Curve/Rectangle/Polygon）→AnalyticVector/Tessellated，或全同Grid Runs→RasterizedRegion，不混表示。Rasterize一个Vector→RasterizedRegion，Grid/RasterPolicy必需。ExtractBoundary一个Runs→Tessellated，固定border_holes、保留Grid，不声称原连续边界。Transform一个Vector→AnalyticVector/Tessellated或一个Runs→RasterizedRegion，Transform必需/BooleanKind=null；Region固定nearest_neighbor，v0.3不开放constant选项。未使用的Grid/RasterPolicy/Transform/BooleanKind必须null（所有Runs路径Grid显式相同）；MaxDeviation有限正值<=Profile.MaxCurveDeviation。点/线/开放曲线不能作面积，面积路径遇此输入拒Unsupported。Vector输入全部Frame相同，重复operand.Id拒绝，每种操作前后检，不把后端自动闭合当资格。

输出vector身份不继承HALCON丢失的contour reference：环方向按§3、起点取坐标字典序最小顶点，组件/洞按规范坐标序列字典序排序，赋 `g.<operationId>.n<index>`/`r<index>`/`v<index>`。派生OperationId最多80字符、完整ID<=128，Vertex/Ring索引在整个document唯一；新document同前缀、revision=0，不覆盖原件。Report保存每operand角色/source闭包；CurveErrorBound为同Frame单位的几何离散上界且有限非负（另含数值舍入政策），CoordinateErrorBound仅有已验证数值界时非null、有限非负，HALCON一般连续布尔未证明该界时必须null。RequireBoundedCoordinates=true且无界则拒Unsupported/ApproximationBudget，不能填0编造保证；false只给BackendNumeric候选，由宿主资格判断。裁剪如实标记；DiscreteGridExact仅指保存/同grid集合，不声称连续误差零。无Source的Vector用operand/Snapshot documentId/revision/Sha256标几何来源，不编图像来源。Empty也给可归还的有界空lease并保留Report/版本。

### A.5 Benchmark 与逐片准备结论

```csharp
// Benchmark值在Core；测量执行器属于对应Tests/TestHost，不是生产服务。
public enum BenchmarkEvaluation { NotEvaluated, Failed, Passed }
public sealed record RoiBenchmarkWorkload(
    string Id, string Slice, string InputSha256, string ValidationProfileHash,
    int Nodes, int Vertices, int Rings, int Components, int Holes,
    int GroupDepth, int BatchCommands, int HistorySteps, int ConcurrentSessions,
    long ImageWidth, long ImageHeight, int VisibleTiles,
    double DpiScale, int PointCount, int RunCount);
public sealed record RoiBenchmarkTargets(
    double P50Milliseconds, double P95Milliseconds, double P99Milliseconds,
    double CloseP99Milliseconds, double PointerP95Milliseconds,
    long PeakManagedBytes, long PeakNativeBytes, long PeakProcessBytes,
    int MaxFailedRequests, int MaxDeadlineExceededRequests);
public sealed record RoiBenchmarkProfile(
    string Id, string Revision, string Sha256, string ConsumerId,
    ImmutableArray<RoiBenchmarkWorkload> Workloads,
    int WarmupRequests, int MinCompleteSamples, int MaxIssuedRequests,
    TimeSpan MaxRunDuration, RoiBenchmarkTargets? Targets);
public sealed record RoiBenchmarkResult(
    string ProfileSha256, string WorkloadId, string EnvironmentSha256,
    BenchmarkEvaluation Evaluation, int Issued, int Complete, int Successful,
    int Failed, int Cancelled, int DeadlineExceeded, int Censored, int DrainUnknown,
    double? P50Milliseconds, double? P95Milliseconds, double? P99Milliseconds,
    double? CloseP99Milliseconds, double? PointerP95Milliseconds,
    long PeakManagedBytes, long PeakNativeBytes, long PeakProcessBytes,
    bool AllResourcesReturned, ImmutableArray<string> Reasons);
```

每个Workload单独输出Result，冷启动另组，不与Warmup后稳态合并。计数维度非负、ConcurrentSessions>=1、WarmupRequests>=0、MinCompleteSamples>=1、MaxIssuedRequests>=MinCompleteSamples、MaxRunDuration有限正值、DpiScale>0，Profile/输入/环境hash均64位小写hex；不适用图像/点云维度填0。Targets整体null表示消费者未采纳→NotEvaluated；适用门目标有限正数，非适用Pointer/Native门为0且Slice明确排除，不用0表示无限。Close始终适用、MaxFailedRequests/MaxDeadlineExceededRequests为非负数，峰值为实测bytes不是预约。Workload记录切片、维度之外还需锁输入hash和真实环境hash（framework/AsunImage/HALCON/DevExpress/CPU/内存/DPI/worker/AOP），不以硬件型号代替实际占用测量。用户主动取消单列；Successful/Failed/Cancelled/DeadlineExceeded/Censored互斥，Issued为五者之和；Complete为前四类中有接纳时刻且已完整排空/归还的有效端到端样本数，分位按该Complete全组统计，不能只挑Successful。接纳前短拒归Failed但无端到端时长；DrainUnknown为Censored子集。失败/取消/超时另列具体耗时/资源结局但不从Issued删除。未完整排空的阶段观测不能充Complete；任何正确性失败禁止Passed，资源未归还或阈值/最低样本缺失NotEvaluated。统计口径与切片门优先按下文引用执行。

统计方法唯一采用 DEV-GOV-010 §3.1（包括nearest-rank、完整排空样本和失败/删失单列），不在本模块重定义分位算法。测点和负载见§13；未有阈值/样本/版本闭包→NotEvaluated，排空未知不得Passed，已给阈值超限→Failed，全部完整且满足才Passed。

| 六项门 | 本轮规格接收定位 | 实际状态/剩余范围 |
|---|---|---|
| 1 职责/复用 | §1～4、§8、§14 两具体消费者 | 四个纯软件切片规格已接收；没有消费者代码运行证据 |
| 2 API/错误/Owner | A.1～A.3、§3/5/6、Codec v1；HALCON/WPF边界见A.4/A.6 | 四个软件切片公开契约规格已接收；产品Schema不授获批，真实HALCON/WPF类型编译未执行 |
| 3 独立最小Host | §10.1两个完整HostCases/Profile/Factory/原Task/有限Root；§10.2独立lease；§10.3双STA；§8.3 DLL边界 | 四个软件切片Host六项规格已接收；HALCON/WPF指定接线与Owner恢复指导限定内容接收，工程尚未创建/构建、真实运行/viewport另验 |
| 4 正反例/生命周期 | §11两视角、RG-L13/L14/W04根/异常/迟到/恢复，§12逐片断言 | 四个软件切片验收计划已接收；HALCON/WPF恢复断言限定内容接收，未执行C#/native/UI测试 |
| 5 Benchmark | §13与DEV-GOV-010统计口径 | 四个软件切片测量方法/负载维度/阈值来源规格已接收；消费者目标与真实样本未采纳，实际性能 `NotEvaluated` |
| 6 落点/范围/调用 | Core binding、§8.3 DLL/test、§10.1 Main及§10.3 StartupObject、§12命令 | 四个软件切片工程/测试/禁止路径与调用定位已接收；Host辅助仅放对应Tests，无共享层新API；代码开工前仍须绑定权威仓库/快照 |

2026-10-11主控对0.4.2-prep的接收结论：`CoreSlice-01 / Interaction-01 / Codec-01 / Spatial-01` 纯软件切片为 `ModuleCoreImplementationReady`（仅六项文档规格准备），不是已实现、已构建或运行合格。`HALCON-01 / WPF-01` 仅指定接线/Owner恢复指导内容接收，真实adapter/HALCON/WPF/viewport/性能及客户用途仍 `PreparationIncomplete / NotReady`；HostCommit-01只限定宿主端口边界，不授真实提交或产品事实写权。既有算法/公开契约范围保持，后续实际build/run/UI/性能/现场资格未执行；客户物理允差、代表图像/点云、生产坐标资格与正式持久权限只阻依赖范围，不阻无关纯软件工作。原0.4.2-prep接收范围保持；0.4.3-prep的§8.2/A.3公开Codec创建/纯值校验/期限并发边界及RG-K04～06已获主控限定内容接收，S-Codec创建入口文档欠账关闭；不创建工程，不改变API/算法/旧Golden/正式Schema，不授真实运行、native/WPF、性能或客户资格。


0.4.4-prep的全部批准范围在本模块永久原会话自行审核、修复和文档验证；详见§15.3。HALCON转换/计数/非单位grid、Interaction缓存/LOD、三语/手势/控件骨架、公开Backend构造与两typed消费配方的内部设计欠账已闭合。A.5六项表的既有准入与真实运行门保持，不等待总控内容复核，不将结构校验扩张为build/run/UI/性能/现场通过。

### A.6 WPF-01 公开挂接、输入与投影契约

以下类型只在 `Asun.Modules.RoiGeometry.Wpf`（WPF DLL），Core不引用它们。实现类 `RoiEditorControl : System.Windows.Controls.UserControl, IRoiEditorControl` 有公开无参数构造；构造只初始化控件与本模块三语资源，不开Core/native会话，不访问全局服务。控件由Host显式嵌入，viewport视图依旧由其Owner提供，不从本控件创建图像引擎。

```csharp
// 使用Core namespace及System.Windows.UIElement；这些UI类型不进入Core。
public enum RoiEditorIdentityKind { Operation, Node, Ring, Component, Vertex }
public enum RoiPointerPhase { Down, Move, Up, Cancel }
public enum RoiPointerButton { None, Primary, Secondary }
public enum RoiEditorNotificationKind { SelectionChanged, DraftChanged, SaveRequested, Diagnostic }
public sealed record RoiEditorPermissions(bool CanEdit, bool CanSave);
public sealed record RoiEditorPresentation(string CultureName, string ThemeName, bool ReduceMotion);
public sealed record RoiEditorInputProfile(
    TimeSpan OperationTimeout, TimeSpan CloseTimeout, double HitToleranceDip,
    double NudgeLength, double ShiftMultiplier, int MaxHitCandidates);
public sealed record RoiViewportProjection(
    string DocumentId, long GeometryRevision, string FrameId, long ViewRevision,
    Affine2D DocumentToViewport, Bounds2 ClientBoundsDip);
public sealed record RoiPointerInput(
    long ViewRevision, RoiPointerPhase Phase, RoiPointerButton Button,
    Point2 PositionDip, bool Control, bool Shift, bool Alt);
public sealed record RoiEditorOverlay(
    long Sequence, long ViewRevision, GeometrySnapshot Snapshot,
    GeometrySnapshot? Preview, SelectionSet Selection);
public interface IRoiEditorViewportBridge
{
    System.Windows.UIElement View { get; }
    bool PublishOverlay(RoiEditorOverlay overlay);
}
public sealed record RoiEditorNotification(
    long Sequence, RoiEditorNotificationKind Kind, SelectionSet Selection,
    GeometrySnapshot Snapshot, RoiOperationReceipt? Operation,
    ImmutableArray<RoiError> Errors);
public interface IRoiEditorHost
{
    // 唯一ID符合§3.1，不依赖行号；绘制前生成全套ID，失败也不重用已接纳OperationId。
    string NewId(RoiEditorIdentityKind kind);
    // 有界非阻塞投影；SaveRequested只是请求，不是持久化回执。
    bool Publish(RoiEditorNotification notification);
}
public interface IRoiEditorTextResources
{
    // 缺Key返回null，由模块内置对应culture资源回退；扩展culture须覆盖全部模块Key。
    string? Resolve(string cultureName, string key);
}
public sealed record RoiEditorAttachRequest(
    IRoiGeometryCore Core, IRoiGeometryInteraction Interaction, ValidationProfile Profile,
    IRoiEditorViewportBridge Viewport, RoiViewportProjection Projection,
    IRoiEditorHost Host, RoiEditorPermissions Permissions,
    RoiEditorInputProfile Input, RoiEditorPresentation Presentation,
    IRoiEditorTextResources? TextResources);
public sealed record RoiEditorAttachReceipt(bool Attached, ImmutableArray<RoiError> Errors);
public sealed record RoiEditorDetachReceipt(
    bool Detached, bool ResourcesReleased, ImmutableArray<string> PendingOperationIds,
    ImmutableArray<RoiError> Errors);
public interface IRoiEditorControl : IAsyncDisposable
{
    RoiEditorAttachReceipt Attach(RoiEditorAttachRequest request);
    void SetPresentation(RoiEditorPresentation presentation);
    void SetPermissions(RoiEditorPermissions permissions);
    void RefreshProjection(RoiViewportProjection projection);
    void SetSelection(SelectionSet selection); // 不回发同值，避免Host/viewport循环。
    void ProcessPointer(RoiPointerInput input);
    ValueTask<RoiEditorDetachReceipt> DetachAsync(
        MonotonicDeadline deadline, CancellationToken cancellationToken = default);
}
```

未Attach/已完成Detach的控件，DetachAsync在同STA返回Detached=true、ResourcesReleased=true、PendingOperationIds=Empty，不关闭借用Core；失败Attach必须原子回到未挂接，若内部有已启动工作则先按实际退出保留可Detach实例，不将失败返回冒作资源释放。Dispose在无活动Attach后只释放本控件资源，同STA有界完成；Repeated Dispose幂等，disposed不接受新Attach。上述规则支持§10.3构造/Attach中途异常的有限恢复。

全部控件入口在创建的STA Dispatcher线程，错误线程短拒明确InvalidOperationException，不跨线程静默Send；await只在无锁位置，后台Pure Core/Interaction结果通过Dispatcher投影、先核Attach generation/DocumentRevision/ViewRevision。Attach检查Core.Open、Profile绑定、视图尚未挂另一父、Frame/Document/revision匹配、按§3.2精确2-norm门及有理逆舍入规则验证的投影、有限Input；一次挂接，重复挂接拒Conflict、先Detach再换Host。Input的两个TimeSpan/HitTolerance/NudgeLength>0、ShiftMultiplier>=1、MaxHitCandidates>0且受Profile，NudgeLength用文档长度单位。ThemeName由Host提供安装主题名，SetPresentation只应用本控件根，不改全局；未知culture在编辑启动前拒Unsupported，不静默显示错误语言。权限不足禁止启动编辑/保存，手势中撤销编辑权限取消本手势且发布前复核；这只是UI限制，Core端的外部调用仍由Host授权。

Host提供中央View并把其pointer事件转换成ProcessPointer，坐标必须相对中央视图的DIP；Host外部修改Core后也须RefreshProjection新的GeometryRevision、控件Query同步；视图transform/client变化显式RefreshProjection、ViewRevision递增，旧手势/HitTest失效重算。控件挂接不订阅外部静态事件、不持native对象；Core/Interaction/Viewport/TextResources/Host全部借用。Overlay仅有immutable geometry/selection值，PublishOverlay=false记录拒收、不回滚已应用Core，下一次刷新发送最新投影；序号递增，Bridge不回调Core或控件入口。3D ray/native可见性由viewport原契约处理，本2D pointer通道不把屏幕深度当Spatial标定，3D域参数用同一typed Spatial API。

绘制Down冻结基线、Frame与原投影，Move仅合并最新输入；Curve/矩形先参数候选，Polygon逐点击顶点、Enter闭合并严格校验，未满3点不提交。拖拽/参数编辑均生成typed Replace/Transform批量，所有几何/约束走Core PreviewAsync；最多Profile.MaxInFlight个本控件请求，过期工作先取消，仍在退出则只保留最新未执行输入，不无界入队。Up/Enter/应用最多发一个新OperationId的Apply；应用只使用本次合法预览的同Commands/BaseRevision，CAS失败保持文本并刷新冲突。命中歧义先展示全候选，用户选择后继续；框选调用HitTest对应Mode；Delete受§4引用/锁预检且用户确认，Undo/Redo走同Apply。CanSave且用户点宿主保存按钮才Publish SaveRequested，持久权限/回执仍由宿主，控件不显示未确认“已保存”。Core中的Visible/Locked变动通过Replace，选择本身不产生几何revision。

Detach立即封住新输入、取消本控件请求，同时等待本控件持有的实际调用Task退出（含Interaction后台工作）并逐已接纳ID QueryOperation核IsTerminal/ResourcesReleased；Found=false仅在本地调用已结束且确认短拒时不列pending；**不调用借用Core.Drain/Dispose、不关闭viewport Owner**。未完成时Detached=false、ResourcesReleased=false并列PendingOperationIds，保留挂接/借用引用，允许再次Detach；完成才清overlay、从控件父移除借用View、解除本控件事件、清订阅/文本，Core事实保持可由Host继续Query。DisposeAsync按Input.CloseTimeout建立独立期限，失败抛InvalidOperationException并保留可查询/Detach的实例，消息为技术诊断而非UI文字；只有成功Detach才标Disposed。Host窗口关闭先Detach，再按Host自己的所有权排空Core/后端/viewport。RG-W01验证两个控件借用不同Core；RG-W02验证语言/权限/viewport变化与一次Apply；RG-W03验证Detach超时→保留pending→实际退出→再Detach，不用控件卸载事件冒充资源退出。
