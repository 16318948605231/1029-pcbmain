# 坐标变换与有量纲几何独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`CG-Core-A, CG-Core-B, CG-Core-C, CG-Core-D, CG-Core-E`

## Core implementation binding

- 模块：`IM-007 coordinate-geometry`；来源映射：`PKG-007`、`SM-008`。
- 版本：`0.3.6-prep`；整体状态：`DesignReview/Prep`；CG-Core-A/B/C/D/E：`ModuleCoreImplementationReady`（仅规格准备，主控已接收六项文档规格）；任务：`IM-REVIEW-20261009/coordinate-geometry`。
- 永久会话：`01a10306-e6e9-7c61-b5c1-29109ed8f6c1`；本轮仅编辑本文，不创建产品工程、测试工程、会话或子代理。
- 固定基线：C# / .NET 10；可选 UI 为 WPF / 本机 DevExpress **25.2.3**；视觉桥使用 AsunImage / HALCON **26.05**，经 `ImageLibDotNet.cv2` 调用。
- 唯一 Core 工程落点：`src/Modules/coordinate-geometry/Asun.Modules.CoordinateGeometry.Core/`；命名空间：`Asun.Modules.CoordinateGeometry`。
- 唯一 Core 测试落点：`tests/Modules/coordinate-geometry/Asun.Modules.CoordinateGeometry.Core.Tests/`。
- 首次建项路径为 `NewProjectRequired`。主控已按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 接收CG-Core-A/B/C/D六项文档规格，四个Core切片标为`ModuleCoreImplementationReady`（规格准备）。整模块范围及其它切片门见§19；本轮仅同步接收状态，不执行建项或产品代码。
- 后续适配工程按同目录下 `Asun.Modules.CoordinateGeometry.Halcon`、`.Wpf` 落点接收，测试位于同模块测试目录的对应工程；不机械创建 Runtime、Persistence 或 TestHost DLL。调度属于服务实现，资产存储属于宿主，避免空壳分层。
- 实现切片允许路径见 §19；全部切片禁止修改产品 Shell、产品私表、制程项目、AsunImage 内部、其它模块及共享文档。产品 Contract/Schema、权限、质量放行、设备和客户验收由其 Owner 接收。
- 当前未实现、未构建、未运行真实 HALCON/WPF/性能/Golden/现场计量。本轮核对是规格和来源阅读。
- 新增`CG-Core-E`：逐run闭像素支撑经显式affine映射后的全域projective分母证据，唯一公开契约为§4.4 `DenominatorEvidenceV1`；主控于2026-10-10接收六项文档规格，状态`ModuleCoreImplementationReady`（仅规格准备）。保留完整witness、CheckEvidence、同步有界scratch及上游ROI完整性Owner；不证明Alignment其它Jacobian/条件/物理门或真实运行。既有CG-Core-A/B/C/D接收不撤销、公开契约v0.2不改；本轮仅同步状态，不启动实现。
- 2026-10-11本轮接收：CG-Halcon公开装配/Camera Read消费及CG-Wpf外部Host/权限/借用显示的新增确定指导内容已获主控限定接收，复用§11.4既有Inspector声明。§3.5–3.8/4.3/4.4、Core A/B/C/D/E六项文档规格接收、编码及Golden保持；CG-Halcon/CG-Wpf仍为`PreparationIncomplete/NotReady`。真实HALCON、CameraRead/Viewport接线、WPF/性能及物理资格未验，不授适配产品准入，不创建工程或执行真实运行。当前限定内容接收状态以本页首及§17为准，§19后续运行门保持。
- 2026-10-11参数名称接收：§4.3.1–2既有模型的稳定Name/ParameterOrder/ScalarPath/Scale规则及Affine3索引、两条软件单位边指导已获主控限定内容接收，S-CG参数名的文档欠账已关闭；由metrology原Owner精确消费。数学、身份编码算法、公开DTO、旧Golden及Core A/B/C/D/E接收保持；真实Host/C#/HALCON/WPF/性能/物理资格未验，不扩模型或产品准入。
- 2026-10-11完整范围收口：复用已接收Core与既有自审，仅补§8.4参数封送顺序、§9.1.1–2既有Bilinear局部场公开装配/逆场配对、§11.5–6控件配置/完整资源及§14.3参数来源。全部批准范围的文档准备结论及剩余Owner见§19.3；不授产品实现或运行资格。

## 1. 职责、消费者与非目标

本模块消费明确版本的坐标帧、变换边、几何和数值策略，验证不可变坐标图，解析路径，执行点、向量、法向、线段、圆/圆弧、椭圆、折线、多边形、有限 3D 几何及一阶协方差传播，返回有单位、域、版本和路径证据的结果。可选 Inspector 只读投影这些结果；所有业务能力可无 UI 调用。

真实复用计划：ROI 几何工具消费点/线/多边形与支持域；无 UI 计量工具消费有量纲线段/圆弧/法向及不确定度摘要；FOV/拼接消费显式坐标链和支持域。消费者自己的身份、用途、目标顺序、质量阈值和提交事务不进入几何算法。

本模块拥有本次快照校验、路径选择规则、组合/逆的适用性、几何映射、数值诊断及操作回执。宿主/资产 Owner 拥有帧和变换的发布、标定资格、模型参数求解、物理有效域及授权引用。不得把”结构有效/数值可算”解释为标定合格或工艺放行。

非目标：Mark 匹配、Alignment 拟合、标定采集/求解、鲁棒对应估计、拼接编排、图像重采样、ROI 编辑事务、目标身份、工单、配方发布、测量定义/MSA、缺陷判定、复判、报告签发和设备动作。没有训练或在线学习路线；不从图像猜单位、轴、面别或深度，不使用静态当前标定、latest、缺路径单位阵、静默夹紧或自动删点。输出不直接写 `InspectionFact`、`MachineDecision` 或设备命令。

### 1A. 新架构适配要点

**架构门禁**：`Asun.CoordinateGeometry.Core` 及 `Asun.CoordinateGeometry.Managed` 子程序集不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.CoordinateGeometry.Wpf`（Inspector 控件）可引用 WPF/DevExpress，且该程序集不得被 Core 反向引用。

**Blazor/Web 宿主中的坐标职责**：当 Web 端（Blazor Server）需要展示检测结果时，服务端必须调用本模块将所有坐标转换为像素坐标后再传给浏览器。浏览器端不重写仿射/透视数学。具体约束：
- 服务端提供 `MapToPixel(CoordinateChain, ImmutableArray<Point2D>)` 计算好的像素坐标数组
- 浏览器只调用 Canvas `drawPolygon(pixelCoords)` 类接口，不自己做矩阵乘法
- 这保证 Web 端坐标与 WPF Viewport 端坐标精确一致

**AI 推理坐标逆变换**：`ai-inference` 分块推理后，tile 坐标需逆变换回原图坐标：
1. `ai-inference` 输出的检测框/点坐标是 tile 本地坐标（像素坐标）
2. 调用本模块的 `InvertTileTransform(TileRef, ImmutableArray<Point2D>)` 逆变换到 Frame 坐标
3. 再调用 `MapPhysical(CoordinateChain, ...)` 变换到物理坐标
- **本模块不保存 AI 推理结果**，只提供变换计算；结果所有权在调用方

**HALCON 备选交叉验证**：本模块的 `HalconBackend` 使用 HALCON 26.05 算子执行坐标变换。`ManagedBackend`（纯 C# 实现）作为独立对照。CI 门禁：对同一批输入点，两路输出的最大差值不超过 `1e-9`（相对）；超出即 CI 失败，双跑产出差异报告。

## 2. 独立交付与数据流

| 包/边界 | 职责 | 依赖与资源 |
|---|---|---|
| Core | 本地值契约、图校验/路径、非视觉数学、映射请求生命周期；纯托管数值路线是明确的独立 Core 能力 | .NET 10 BCL；无 UI/数据库/设备；不复制相机/畸变算法 |
| Halcon | 已登记模型的视觉桥、2D/3D HALCON 矩阵与点/像素映射、相机平面/投影/畸变 | Core + `ImageLibDotNet`；句柄/tuple 仅在此层，输出值副本 |
| Wpf（可选） | Inspector、联动、三语、宿主主题和诊断投影 | Core + 本机 DevExpress 25.2.3 + 宿主已有视口公共能力 |
| 宿主资产边界 | 读取并传入封存快照，保存结果、草稿与审计 | 不强制模块 Persistence DLL，不传私表/连接/页面/SDK 句柄 |
| 外部受限模型边界 | 消费已有局部场/相机资产，不估计模型或改变质量 Owner | §9 定义值协议；真实外部公开类型映射只阻断对应集成 |

数据流为：宿主绑定精确资产 → 传入完整只读快照 → 接纳/限额 → 图/模型/域校验 → 固定路径 → 逐边几何映射 → 误差传播与诊断 → 排空/释放 → 唯一回执 → 宿主决定如何消费。显示链与物理链分别请求，不通过控件初始化 Core。不用服务定位器、反射扫描、全局可变缓存或产品静态对象。

## 3. 数学、量纲与逐能力规则

### 3.1 帧、单位与矩阵

采用列向量 `p_target=T_target_source*p_source`，A→B→C 为 `T_C_A=T_C_B*T_B_A`。矩阵数组按 row-major 储存；2D 仿射固定九元齐次矩阵，最后行为 `[0,0,1]`；3D 仿射固定十六元，最后行为 `[0,0,0,1]`；2D 投影固定九元且允许整体非零尺度等价。不得靠数组长度猜模型。

数学图像帧 `(u,v)=(column,row)`，整数为像素中心，列向右、行向下；普通 Cartesian 帧必须声明轴和方向，不能默认图像也是 Y 向上。3D 帧声明有序 XYZ、手性及物理基准引用。轴方向/基准不是 UI 文字标签，换轴、换手性均为显式边。显示 X 镜像 det=-1；绕 Y 轴物理旋转 180° 是 `diag(-1,1,-1)`、det=+1，两者不等价。

长度单位闭集为 Pixel、Nanometre、Micrometre、Millimetre、Metre；弧度用于角度。SI 长度比例由定义精确换算，pixel→长度只能通过有明确资产来源的变换。各帧轴使用同一单位，混合量纲轴不支持。变换矩阵的线性系数以“目标单位/源单位”、平移以目标单位解释；**已编码的单位比例不能再自动乘一次**。若需独立单位换算，宿主登记显式 scale 边。Identity/Translation/Rigid要求源目标单位相同，跨单位用独立scale或Affine边。Pixel→Pixel 的缩放不是物理标定。角度不是长度轴；Core不在长度几何中加入角度坐标轴。

Frame/Edge 的 `(Id,Revision)` 是精确引用；Id 为 1–128 个 ASCII 字母、数字、`._:-/`，区分大小写，不 trim/改大小写；Revision 为正 uint64。此限制是本地契约，不宣称平台 C-03 已批准。同一引用不同内容即版本冲突；源=目标也须登记存在的帧并显式申请 identity，不借缺失帧返回单位阵。

所有 double 必须有限；-0 规范为 +0。输入、中间值和输出溢出均拒绝；不返回无限点或隐式伪逆。圆半径/尺度/期限等须满足对应正值条件。量纲归一后的数值安全与客户物理精度不同：线性模型用 `B=diag(1/Ltarget)*A*diag(Lsource)` 的 2-norm 条件数，L 为请求数值策略中逐轴正尺度。奇异/超条件数限拒绝；不以 det≠0 或固定 epsilon 代替稳定性检查。条件数固定使用 §3.5 的单侧 cyclic Jacobi SVD、误差包围与双侧逆残差验证；不形成 `AᵀA` 求特征值作准入判据，不在编码时另选 QR/伪逆路线。

### 3.2 有效域

Domain 为显式 Unbounded、Box2、Polygon2（外环+洞）或 Box3。Unbounded 仅允许纯数学帧/边；Pixel、标定平面、相机和局部场必有来源域。Box 各轴 min<max、边界规则 Closed/Open/HalfOpen 必填；HalfOpen 指 min 包含、max 排除。Polygon 外环 CCW、洞 CW，以声明坐标数值方向计算，首点不重复结尾；至少三点、无自交/零面积、洞互不相交且严格位于外环内。Closed 包含外环边界，洞内部及洞边界均排除；Open 还排除外环边界；Polygon 不支持 HalfOpen。不自动修复顶点或改变绕序。近边界按数值策略的 `BoundaryGuard` 做保守拒绝：不能可靠判定则 `CG004DomainViolation` 并给 `BoundaryUncertain`，不视作内点。

每条边先检查源 ValidDomain，再执行，再检查目标帧域；禁止只检查起点终点。线段/曲线/多边形的**全体几何**必须属于域，不能只检查顶点。例：线两端在外环内但穿过洞应拒绝。仿射线段用与边界的精确线段相交及区间内点判定；多边形除边界外检查内部是否包含域洞；圆弧/椭圆须解边界交点/极值并检查区间，数值不能证明时拒绝。局部场仅支持声明的点/有限采样，采样不证明连续几何全部有效。

Domain.Polygon2的CCW/CW约束只用于域资产规范；GeometryValue.Polygon2按Outer/Holes角色定义填充，可保留任意原始合法绕序。映射反射后的CW外环仍是合法几何，不能在下一条边把它当域资产重新拒绝；仍须simple、holes嵌入且无重叠/自交，顶点索引/绕序不自动改写。

### 3.3 模型、几何与返回类型

| 能力 | 固定处理 | 返回/拒绝与验收 |
|---|---|---|
| Identity/Translation/Rigid2D/3D | identity 显式；rigid 检查归一基正交、proper rotation det=+1；镜像只作为 affine | identity 不补缺边；点加平移，向量不加平移 |
| Affine2D/3D | `y=A*x+t`；组合依方向；逆前稳定性检查 | 点/线段/折线/多边形逐结构保持索引；法向见下文 |
| 向量/切向/法向 | affine 向量 `A*v`；方向单位化；法向 `normalize(A^-T*n)`；零向量/零法向拒绝 | `A=diag(2,1), n=(1,1)` 单位法向为 `(1/√5,2/√5)`；平移不影响它们 |
| 圆/圆弧 | affine 用中心及二列基 `r*A*[e1,e2]` 表示参数曲线；只有证明 similarity 才保留 Circle | 非均匀缩放返回 Ellipse/EllipticArc；不以平均半径冒充圆；角区间/方向保留 |
| 椭圆/椭圆弧 | `c+B*(cos(t),sin(t))`，B 满秩；affine 返回 `(A*c+t,A*B)` | start与sweep有限，`0<abs(sweep)<2π`；完整圆/ellipse用独立full分支，不靠浮点sweep等于2π猜full；正负sweep表达方向，不重排主轴丢弧方向 |
| Polygon/Polyline | 保持环、洞、顶点和源索引；反射后绕序符号变化有诊断 | 不擅自 reverse 为“更好看的方向”；需要规范环的消费者显式另作操作 |
| Projective2D 点 | `q=H*p`，显式除 w；用 `abs(w)/(||第三行||₂*||p||₂)` 与策略 `MinimumDenominatorRatio` 比较 | 尺度不影响判定；w=0/近0/输出越域拒绝；不能把 projective 当 affine |
| Projective2D 线段/多边形 | 每段检查 w 在全区间同号且远离安全带，再映射端点；保留线性边 | 线段跨无穷远即拒绝；域/洞完整性同 §3.2 |
| Projective2D 圆/椭圆 | 保留齐次参数曲线 `Q(t)=H*[c+B(cos t,sin t);1]`；同时给 `K'=H^-T*K*H^-1` 二次曲线矩阵 | 返回 RationalConicArc，不强转 Ellipse；w(t) 极值/根检查整个区间；不支持其连续域证明的请求明确拒绝 |
| 3D 几何 | affine 点/向量/法向/线段/折线/平面；平面 `(n,d)` 按逆转置齐次变换并一起归一 | 3D mesh、实体布尔、球体自动转形不在本模块；2D→3D 必须显式平面/深度边 |
| 局部非刚性 | §9 消费已有局部场，按版本固定插值/Jacobian/域 | 不猜通用逆；不能证明唯一根/方向/域则拒绝；不按采样把整条曲线认证有效 |
| 相机/平面/畸变 | §8 的固定 HALCON 路线 | 无深度仅能与已声明平面相交，不恢复未知 Z/翘曲 |

非 affine 的自由向量没有与位置无关的全局映射；须给 Anchor，使用该位置 J。法向在可逆方阵 Jacobian 下用 J^-T；3D→2D 投影不返回“3D 法向的唯一2D法向”。PlaneLift 的两列基满秩、单位/方向明确，可将2D点/线段/折线升维；需要2D逆时须资产明确声明所在平面、稳定投影基与域，不能只丢Z。跨维度、位置缺失、不可微或不具所需输出表示时 `CG019UnsupportedGeometry`，不能退化成点集成功。Circle/Arc/Ellipse表达边界曲线，不表达填充盘；Polygon表达外环内去洞的区域，连续域检查必须包括其内部。

### 3.4 协方差与误差

协方差输入明确变量顺序、单位、平方/交叉单位、均值、来源及相关性；literal字段与混合量纲归一见§4.3/§3.8。有限、对称、PSD 检查由 `CovarianceTolerance` 控制；小负特征值若在数值容差内仅报告 `NumericallySemidefinite`，不静默更改原矩阵。超限拒绝。每个几何项可携带坐标/参数联合协方差；缺失表示 `NotProvided`，不是零不确定度。

令 `z=(x,θ1,…,θk)`，`Σy=Jz*Σz*Jzᵀ`。只有明确声明输入与各边参数相互独立时才可逐边用 `JxΣxJxᵀ+JθΣθJθᵀ`；有相关性须传完整联合块及交叉项，不能每次假定独立加和。单位换算1 mm→1000 μm，方差乘10⁶。变换拟合残差/条件数不是完整测量不确定度，标定资格由外部 Owner 保持。

affine 为解析精确一阶传播；projective/camera/localfield 是局部线性化，结果标 `FirstOrderLocal`，必须给 LinearizationDomain、导数版本和所用锚点。不能跨洞、不可微边界或无穷远传播。没有局部误差/线性化有效域证据时只返回几何及 `Uncertainty=NotEvaluated`；请求显式 Required 时全批 `CG020UncertaintyUnavailable`。不得用有限差分步长常量猜相机或局部场 Jacobian。


### 3.5 固定数值路线：SVD、稳定逆及正确性证书

ManagedCore算法版本为 `cg-managed-numeric-1`。这是非视觉小矩阵/事务数学；HALCON视觉路线仍经cv2，不以本节绕过相机或畸变算子。实际代码不得引入LAPACK/Python/Java运行包，本节从已读实现借鉴算法和测试思想，并按BCL实现固定路线。

1. 支持二维/三维线性块、3×3 projective和3×2平面基；拒绝未知尺寸。输入binary64先精确转成BigInteger有理数；按源/目标AxisScales形成精确有理B，再除最大绝对元素的2次幂使最大幅值在[0.5,1]。零矩阵为奇异。转double仅供迭代，精确B保留用于最终误差证书；任何尺度/转换无法有限表达时CG005，不夹subnormal为零。
2. 固定单侧 cyclic Jacobi：W=B、V=I，依 `(0,1),(0,2),…` 字典序列对。a=wp·wp、b=wq·wq、g=wp·wq；点积使用精确dyadic求和后round-to-nearest-even，列norm使用缩放hypot。g=0跳过；`τ=(b-a)/(2g)`，`t=signNonZero(τ)/(abs(τ)+sqrt(1+τ²))`（τ=0取+1），c=1/sqrt(1+t²)、sn=c*t。`wp'=c*wp-sn*wq, wq'=sn*wp+c*wq`，V同样右旋转。τ/sqrt的候选计算用§3.6有理包围再nearest-even，不让τ²溢出；每次旋转及每sweep检查取消/预算。
3. 一完整sweep后最大归一内积 `abs(g)/(normp*normq)≤64u` 才结束；u=2^-53是binary64舍入单位，**不是double.Epsilon**（后者为最小subnormal）。零列保持零并视为秩亏；排序σ降序，相等按原列号，U列取归一W。翻转某列时U/V一起翻，重复奇异值不要求唯一向量。MaxJacobiSweeps来自AlgorithmLimits（1–128）；超限CG005+NumericalNonConvergence，不换算法继续。
4. 最后不凭迭代“收敛”就算通过。对保留的精确B和候选double U,D,V，按§3.6精确有理运算给出 `eU=||UᵀU-I||F`、`eV=||VᵀV-I||F`、`r=||B-U D Vᵀ||F` 的向上包围。要求eU/eV<1且≤NumericPolicy.OrthogonalityTolerance。由乘积奇异值界，`lo=σmin(D)*sqrt(1-eU)*sqrt(1-eV)-r` 向下取界，`hi=σmax(D)*sqrt(1+eU)*sqrt(1+eV)+r` 向上取界；lo>0且hi/lo≤MaximumConditionNumber才允许稳定逆/法向。不能以估计σ比略低于限就放行；证书不够紧则继续剩余sweep/包围细化，仍不能证明则CG005。
5. 逆固定用已认证SVD的 `X=V D^-1 Uᵀ`，矩阵乘/和在精确有理中求候选并nearest-even；返回前同时认证 `||I-BX||∞`、`||I-XB||∞≤InverseResidualTolerance`，并检查重建/逆所有元素有限、前后FrameNumericRules幅值和域。Tolerance属于软件数值策略，0<值<1；不作物理精度判定。失败CG005，不调用伪逆/正则化/另一求解器救结果。归一B=Ltarget^-1*A*Lsource的scale因子在候选逆中显式还原：A^-1=Lsource*B^-1*Ltarget^-1（B额外除2次幂时B^-1相应乘其倒数）；affine逆平移=-A^-1*t；projective用完整H稳定逆后归一。Point/Vector的正向运算也拒绝超稳定性策略的边，不把原生成功等同稳定。
6. projective规范化选绝对值最大元素（相同按row-major索引）作为pivot，除pivot使其为+1；ParameterOrder/协方差按此chart，pivot变化是新数值分支，导数跨chart边界Required拒绝。PlaneLift满列秩沿同SVD证书验证；允许的已声明平面逆使用 `V D^-1 Uᵀ` 左逆，并验证点位于平面域/OffPlaneTolerance（由外部物理资产给出），不从未知3D点自动丢Z。

必测：diag(1,1)、diag(1,10^-12)、反射、相同σ、零列、`[[1,1],[1,1+2^-50]]`、大/小2次幂尺度与不均匀量纲；检查重构、U/V正交、双侧逆残差和上下界；条件数门附近证书不确定拒绝。实际测得64u/迭代性能不能作为客户精度或节拍承诺。

### 3.6 精确谓词、有理包围、交点与连续线/区域

固定BCL数值底座：binary64由BitConverter.DoubleToInt64Bits拆 sign/exponent/mantissa，精确表示 `BigInteger numerator / 2^k`；subnormal也保留。通用有理运算分母正、GCD约分；每次乘法之前以位长上界预约内存，超过MaxRationalBits/MaxWorkingBytes为CG007。MaxRationalBits/MaxPredicateSteps与根细化/三角级数限见§4.3 AlgorithmLimits，全部调用共用递减预算，不为每一小操作重置。

- orientation固定**精确有理行列式** `(bx-ax)*(cy-ay)-(by-ay)*(cx-ax)`取符号；ring面积精确鞋带和。v1不启用快速浮点filter或double-double近似，避免错误的epsilon共线；后续优化须保留精确fallback与新算法版本。输入精确共线就0，BoundaryGuard是另一步，不修改orientation。
- 段交点先exact bounding box→四orientation→分类None/Proper/Endpoint/Overlap；共线用跨度较大轴的精确闭区间求重叠，返回有理端点/原段t参数，不round后再做inside判断。零长度Segment可当单点处理；ring重复相邻点/零边拒绝。每个ring所有非相邻段对检查，邻接仅共享预期端点；自交/重叠CG001。允许O(n²)但每对计入PredicateSteps，不因大输入换近似。
- point-in-ring用+X半开射线：先exact on-segment；对 `(ay≤py<by)` 或反向穿越按orientation与上/下方向累加winding number；winding≠0为inside。洞按§3.2排除，坐标手性不改数值winding规则。
- BoundaryGuard=0时精确边界直接按Closed/Open判定，不能把一切边界都拒绝；guard>0时点到段的最小距离平方用有理投影参数夹[0,1]，与guard²比较；距离≤guard且不能确定在允许侧则CG004 BoundaryUncertain，洞边界始终拒绝。
- 连续Segment：收集与所有外环/洞/box边的exact交点及重叠端t，加0/1并exact排序去重；逐开区间取有理中点做inside，另逐事件点/重叠区间按boundary策略检查。guard>0再检查段对每条边的最小距离平方；二维不相交段距离为四端点到对方段的最小值。全线段成立才可返回，不只测端点。
- Polyline逐段（closed时含末→首）。Polygon作为填充区域：先全部环边连续检查，再为**每个域洞**取内部见证点检查是否落在输入填充区域；取其非退化顶点的相邻边中点向洞内偏移，用dyadic逐半细化直至exact winding确认，预算用尽CG007。输入区域内部包含域洞即CG004，即使两者边界没相交。box/简单外域在输入所有边inside且无域洞覆盖时全区域成立；由Jordan分区保证，不以几个随机点宣称覆盖。
- Box3的点/段/折线为逐轴线性极值与boundary政策；无限Plane3不属于有界Box3，只有Unbounded数学目标才可返回整平面。无限平面截面/mesh不是本模块输出，明确CG019。

包围算术是数值安全证据：有理基本运算精确；sqrt非负有理用2次幂初界+有理二分，直至上下端round到同一个目标double或满足所需判定，不以固定小数位结束。输出double上下界用精确nearest-even转值后与有理值比较，必要时Math.BitIncrement/BitDecrement向外一格；overflow为拒绝。Norm/残差/多项式判据不把Math.Sin/Cos的经验ULP当严格误差界。

### 3.7 曲线根与连续全域证明（非采样路线）

曲线统一成 `q(t)=D*[cos(t),sin(t),1]ᵀ`：Circle/Ellipse用center/basis形成D，projective左乘H；输出RationalConic保存此**参数系数D**，不是二次型K，K仅作为诊断/等价证据。所有系数先按binary64精确有理提升，跨边组合的证明使用精确链；返回的round曲线再次执行域证明，源与输出都必须有效，不以表示舍入偷越界。

1. Full曲线覆盖整周期；有向arc仅接受 `start∈[-π,π]`、`0<abs(sweep)<2π`，数学π用下述包围比较；end=start+sweep以精确dyadic相加，不先round。端点均包含，正负sweep选方向。超范围CG001，不隐式模巨角度。弧是否跨π/0用严格包围比较；不能分清（例如预算耗尽）CG004 BoundaryUncertain。
2. 三角值固定有理Taylor区间：π由Machin式 `π=16 atan(1/5)-4 atan(1/239)` 的交错级数生成上下界，下一项包围余项；按π区间分到[-π/4,π/4]且象限唯一，再用sin/cos交错Taylor和下一项余项区间，加有理参数区间宽度的Lipschitz界（导数幅≤1）。MaxSeriesTerms/MaxRootBisections/MaxRationalBits有限；无法认证象限/端点不猜。zero/有理t=0能exact处理。实际显示值允许Math.Sin/Cos，**证明不能依赖显示值**。
3. 全域分割使用半角 `z=tan(t/2)`，`cos=(1-z²)/(1+z²),sin=2z/(1+z²)`；曲线分子N(z)、分母W(z)至多二次，π处z=∞单独代入极限并检查连续连接。部分arc端点z以步骤2求sin/(1+cos)区间，靠近π时拆分/用倒数chart，不遗漏极限点。
4. 边界事件：对polygon/box每条支持线l解 `lᵀ[Nx,Ny,W]=0`，精确有理多项式；确认其交点在线段范围，范围不能证明时细化。齐次W=0根、投影分母安全带、坐标幅值和guard距离事件一并加入。guard距离用点到边段的投影case分割（投影=0/1的根），对应平方距离-guard²乘正W²，得到至多四次多项式；box按对应面处理。不仅查过线，还查圆弧和边段相切及沿边重合。
5. 固定根算法：去零前导→常数/零多项式分支→Euclidean GCD(f,f')去重根并保留重数→Sturm链 `[f,f',-rem,…]`（只乘正因子约简，不随意翻sign）→Cauchy bound `1+max|ai/an|` 包全部有限根→按有理二分、Sturm sign variation计根、exact endpoint/root单独剥离→每区间唯一根；不同多项式共同根用GCD判等，不无限细化企图区分同根。最多四次，但仍用统一算法，不另选浮点四次公式或Newton。零多项式代表整条curve在该支持线上，按overlap/full边界规则处理，不能当“无交点”。
6. 合并所有root隔离区间、π极限/arc端点，证明顺序与归属；root位于角端点无法严格分清则按Closed/Open/洞政策保守CG004，不用假等号。每个无事件开区间取**有理z见证点**，做§3.6 exact域/guard判定；其between-events符号不变，故覆盖整区间。每个事件点用有理区间细化认证boundary/洞/guard；相切重复根也必须按边界政策判，不用变号漏掉偶重根。无法证明、不在表示支持范围CG004/019；资源/根预算耗尽CG007，不返回采样近似成功。
7. projective分母安全固定用source齐次p：认证 `w²-ρ²*||第三行(H)||²*||p||²>0` 的整个参数区间（ρ=MinimumDenominatorRatio），并w符号恒定。由于N/W为二次有理式，乘 `(1+z²)²` 得至多四次多项式；同时source数值幅值及目标域成立。不把只检查w=0替代安全带。projective线/多边形同理：每条边形成t二次多项式，区域内部检查分母符号用顶点极值，安全比下界用分子最小绝对值/分母范数上界作保守证书；界不够紧拒绝，不暗中采样填过。

曲线全域证明在每条路径边源ValidDomain、目标Frame域执行；有未认证native/外部模型的连续曲线能力则CG019，不把有限point批结果升格曲线。例：单位圆与box x≤1在t=0相切，Closed/guard0可通过、Open须拒绝；圆穿小洞须拒绝；W(z)双根触无限也拒绝。上述证明是软件几何完整性，不能证明客户标定范围、光学可见性或计量精度。

### 3.8 PSD与联合Jacobian的固定路线

CovarianceInput固定变量顺序为所有几何项的canonical scalar顺序，再按实际path步骤追加各边ParameterOrder；显式map允许重复同一参数引用时只出现一次，以Ref+参数名索引复用同一变量。Independent要求每个block给Ref、VariableKeys、Covariance、正VariableScales；Joint给全体同顺序块与相关声明。缺变量、重复/错单位、维度不符不补零。数值矩阵先 `Cij=Σij/(si*sj)` 无量纲归一，si为每变量正尺度，θ单位来自矩阵系数/平移/角等；不要用长度尺度直接归一所有混合量纲参数。

PSD固定**exact rational symmetric pivoted LDLᵀ**：先以归一矩阵检查 `max|Cij-Cji|≤CovarianceTolerance`，超限CG001。满足但不完全相等时仅计算副本S=(C+Cᵀ)/2，并诊断CovarianceSymmetrized，原输入/hash不改。先exact判S PSD：每步从剩余对角选最大（同值按原索引）、同时换行/列；负pivot拒绝；零pivot要求剩余该行/列全零，否则非PSD；正pivot计算exact Schur补并继续。若S不PSD，再判 `S+τI`，τ=CovarianceTolerance；仍非PSD拒绝；通过标NumericallySemidefinite并保留原S，不clip负特征值，不将其改成零不确定度。传播输出重复此检查；预算不足CG007，不换Cholesky或自动加jitter。

Jacobian固定前向自动微分（dual scalar value+按VariableKeys排序的导数向量），只沿已经选择的路径/模型表达式执行。加/乘/除/平方根/sin/cos解析规则，除零/根零/规范化零拒绝；affine/projective/PlaneLift/bilinear使用其正文表达式。向量及法向单位化令 `d normalize(v)=(I-n nᵀ)*dv/||v||`；逆矩阵微分 `d(A^-1)=-A^-1(dA)A^-1`，不得用另一次数值逆作finite difference。circle/arc/ellipse投影保留参数表示并对scalar系数微分，不偷偷对拟合后的radius传协方差。

ParameterOrder唯一：Identity为空；Translation按x,y[,z]；Rigid2/3、Affine2/3取公开矩阵row-major的线性块系数随后offset各轴，Rigid用受约束系数协方差，不另引Euler/Quaternion；Projective固定pivot=1后其余8项row-major；PlaneLift先origin XYZ再basis行序6项；External取封存model明确提供的ParameterOrder。Geometry顺序：Point/Vector/Normal轴序，Anchor若有追加轴序；Segment a再b；Polyline/rings顶点依序；Circle center再r；Arc center/r/start/sweep；Ellipse center再basis row-major；EllipticArc再start/sweep；Plane normalXYZ/d；RationalConic D row-major再start/sweep（full分支无角变量）。跨参数chart/局部cell导数不连续、arc拓扑/采样未定义时Required CG020；Optional明确NotEvaluated。

上述模型参数的逐项Name、单位、Scale来源及稳定ScalarPath唯一见§4.3.1；完整Affine3索引和两条软件单位边见§4.3.2。本表补全既有顺序，不改变本节PSD/Jacobian或Geometry顺序。

对全部输入/参数一次形成Jz，`Σy=JzΣzJzᵀ`，精确有理矩阵乘和后nearest-even，保留交叉块；计算量按MaxVariables²/³预估并计WorkingBytes/PredicateSteps。外部model必须经BackendMapOutcome给InputJacobian/ParameterJacobian、同版本LinearizationDomain与证据Ref；缺失不能数值扰动猜导数。projective/相机/局部场必须由CovarianceBlock.Linearizations给出按Frame绑定的局部有效Domain及EvidenceRef，并逐anchor检查；BackendDerivatives证据/域须与之相容，否则Required CG020、Optional NotEvaluated。局部模型/相机只返回FirstOrderLocal，Core不证明线性化物理准确度。Normal/方向协方差以切空间导数自然可能秩亏，应接受PSD零特征值。Required不接受NotProvided/NotEvaluated。

## 4. Module API Contract v0.2（设计接收稿）

这是`ICoordinateGeometryService`本地契约 v0.2 的唯一规格，替代此前点/矩形专用 v0.1；不等同产品 C-03。§4.3冻结literal C#公开声明及factory，下面字段表是该声明的语义索引；分支不能自行改成其它DTO或添加默认单位/状态。新增独立计算端口`ICellDenominatorEvaluator`以§4.4 `DenominatorEvidenceV1`为唯一规格，不改变此服务v0.2。本文仅提供契约声明，不伪造服务方法实现或声称已经构建运行。

### 4.1 完整值形状

下列 `List<T>` 指不可变快照、有序、可为空但不可含 null；`Ref` 为 `(Id:string,Revision:uint64,Hash:string)`，Hash 为小写 SHA-256 hex64。本地 `Bytes` 是封存字节的只读副本，最多 RuntimeLimits.MaxInputBytes。所有枚举拒绝未定义数值。

| 类型 | 必填字段/闭合分支 |
|---|---|
| Unit | §3.1 五个值；Angle 单独为 Radian |
| Frame | Ref、Dimension(2/3)、Axes（按维度有序的 Name/Direction 字符串及 BasisRef）、Handedness（Oriented2D/Right3D/Left3D）、Unit、PixelConvention（None/Center/Corner）、Domain、SourceRef；Pixel 帧必须 ImageColumnRow 轴定义与明确 convention |
| Domain | Unbounded；Box2(min[2],max[2],boundary)；Polygon2(outer:List<Point2>,holes:List<List<Point2>>,boundary)；Box3(min[3],max[3],boundary)。域点单位取所在帧，不重复单位标签 |
| Point2/Point3 | 分别有 x,y 或 x,y,z double；Unit/Frame 由外层 GeometryBatch 指定，禁止各点自行换单位 |
| GeometryValue | Point2/3；Vector2/3(value,anchor可选)；Normal2/3(value,anchor可选)；Segment2/3(a,b)；Polyline2/3(vertices,closed:bool)；Polygon2(outer,holes)；Circle2(center,radius)；Arc2(center,radius,start,sweep)；Ellipse2(center,basis2×2)；EllipticArc2(center,basis,start,sweep)；Plane3(normal,d)；RationalConicArc2(coefficients3×3,start,sweep,full:bool)。均按 §3 定义；不允许在输入接受不支持的模型/维度组合 |
| GeometryBatch | Frame:Ref、Items:List<GeometryValue>、Uncertainty（NotProvided/Independent/JointCovariance），相关变量顺序和协方差块按 §3.4；结果保持项索引/内部顶点索引 |
| TransformModel | Identity；Translation2/3(offset)；Rigid2/3(rotation,offset)；Affine2/3(matrix)；Projective2(matrix)；PlaneLift(origin,basis3×2)；ExternalModel(modelRef,capabilityId)。矩阵元素按 §3.1，外部模型按 §9 |
| Edge | Ref、Source:Ref、Target:Ref、Model、ValidDomain、Inverse（Forbidden/Analytic/ProvidedInverse，后者含 inverseEdgeRef）、InverseValidDomain（Analytic 必填，其它分支无此字段）、SourceRef、ParameterOrder、ParameterCovariance可选、QualityRef可选。QualityRef 仅透传外部引用，无本地资格枚举 |
| GraphSnapshot | Ref、Frames:List<Frame>、Edges:List<Edge>；内容全在快照，不在执行中读 latest。登记即接纳校验该快照，持久登记由宿主完成 |
| PathSelection | Explicit(steps:List<EdgeStep>)；ResolveUnique；CheckConsistency(probes:GeometryBatch,tolerance:double)。EdgeStep=(edgeRef,Forward/Inverse)，源=目标须 Explicit 空steps；tolerance使用目标单位、来源引用必填 |
| NumericPolicy | Ref、FrameRules:List<FrameNumericRule>、MaximumConditionNumber≥1、MinimumDenominatorRatio∈(0,1)、OrthogonalityTolerance∈(0,1)、CovarianceTolerance∈[0,1)、InverseResidualTolerance∈(0,1)、AlgorithmLimits、MaxPathDepth/MaxPathCandidates（正 int）/MaxGraphVisits（正 long）、UncertaintyRequirement（Optional/Required）、SourceRef。FrameNumericRule=(Frame:Ref,AxisScales:按维度正double数组,BoundaryGuard≥0,MaximumCoordinateMagnitude>0)，后两项使用该帧单位；每个实际帧恰一条。单项适用性见 §14，不复制客户精度 |
| RequestWork | Map(graph,source:Ref,target:Ref,path,batch,numericPolicy)；ValidateGraph(graph,numericPolicy)。ValidateGraph 返回图结构/可执行性诊断，不产生几何；没有隐含 MapPreview 模式 |
| GeometryRequest | ContractVersion=`0.2`、RequestId:string（与 Id 同字符范围）、Work:RequestWork、ExecutionBudget:TimeSpan（有限正值）；输入身份由服务计算，调用方 hash 只能作为待验证声明，不能用于绕过内容比较 |
| RuntimeLimits | MaxConcurrentOperations、MaxRetainedOperations、MaxItems、MaxVertices、MaxFrames、MaxEdges、MaxInputBytes、MaxResultBytes、MaxWorkingBytes（均正整数）；MaxExecutionBudget:TimeSpan>0；MaxRetainedOperations≥MaxConcurrentOperations；构造服务时固定，单请求不能提高 |
| Receipt | ServiceInstanceId:string、RequestId、Admission（Accepted/Duplicate/Rejected）、InputHash可选、Error可选；短拒绝无操作/资源记录 |
| GeometryResult | literal分支MappedResult/GraphValidatedResult；Mapped含GeometryBatch、Source/Target Ref、Path:List<EdgeStep>、OutputCovariance可选、LinearizationEvidence可选；两分支均含GraphRef、InputHash、NumericPolicyRef、BackendRef、Diagnostics；不增加另一个Kind enum，也不存在生产质量结果 |
| Diagnostic | Code（§6）、MessageKey、Stage、ItemIndex/VertexIndex可选、EdgeRef可选、SafeDetails（有限标量/单位/版本引用）；无异常对象/句柄/图像数据 |
| OperationSnapshot | Receipt、State（§7）、Sequence:uint64、CancellationCause（None/User/Deadline/ServiceStop）、Drain（Pending/Confirmed/Unknown）、Result可选、Error可选。仅 Completed 可有 GeometryResult |
| Lookup | Kind（Found/NotFound/Unknown）、Snapshot可选、Error可选；Unknown 不等于不存在 |
| WaitOutcome | Observation（Terminal/WaitExpired/WaitCancelled/Unknown/NotFound）、Lookup；等待结束不是计算终态；NotFound只指原实例明确无记录 |
| DrainOutcome | Service（Accepting/Draining/Stopped）、Drain（Pending/Confirmed/Unknown）、ActiveCount:int64、Error可选 |
| OperationEvent | ServiceInstanceId、RequestId、Sequence、Kind（Lifecycle/Progress）、State、ItemsCompleted可选、Error可选；可靠性见 §7 |

literal声明见§4.3；上表在同名字段存在时沿用其C#类型，新增AlgorithmLimits/联合变量/参数chart字段按§4.3补充，不保留另一套匿名DTO。

服务工厂、后端值端口与公开声明固定为§4.3。CreateManaged只使用Core数学；CreateWithBackend注入固定版本的IGeometryBackend（HALCON或已封存外部模型的组合adapter），不由请求切换。TimeProvider生产使用System、测试使用BCL自定义固定时钟；所有deadline按GetTimestamp/GetElapsedTime计算。工厂Create只做参数校验和纯值构造，无IO/原生对象/后台任务；失败抛ArgumentNullException或ArgumentException并命名无效字段，不创建半初始化服务。

### 4.2 身份、快照与有界保留

接纳前只校验 envelope、版本、预算、服务接纳状态、配额及可封存的字节/集合形状；调用方必须在 SubmitAsync 返回前不并发修改输入。服务复制快照、重新计算 canonical 身份，原子登记后才返回 Accepted；之前取消为短拒绝 `CG008Cancelled`，不发 Accepted。封存/配额失败也为短拒绝，调用方始终拥有原输入，不产生墓碑。结构/模型/点错误在接纳后 Validating 返回，走完整释放路径。不可有限封存的图/集合直接短拒绝，不能无限遍历用户 enumerable。

本地摘要规约 `coordinate-core-values-v1`：SHA-256；固定字段顺序及类型分支标签、UTF-8 字符串加 uint32 little-endian 长度、整数 little-endian、double IEEE754 little-endian（-0→+0；非有限拒绝）、list 数量加顺序、nullable presence byte。图的帧/边与FrameRules按 ordinal Id+Revision 排序；几何项/顶点、路径、协方差变量顺序保留。包含 ContractVersion、全部 Work、Budget、策略及精确来源引用；不包含 RequestId、服务实例、UI/消费者用途。本地Frame/Edge/Graph/Policy/Batch对象自身Ref.Hash及嵌套VariableKey.Owner指向自身时的Hash在计算其内容hash时排除；Edge.Inverse.InverseEdge仅编码对方Id/Revision（不编码对方hash，避免双向边互引hash循环），同Graph再校验它实际对应的完整Ref；其余子引用hash包括；之后请求hash包括这些已验证Ref/hash，避免自引用摘要。此摘要不是平台持久化 Schema/JCS，外部资产 hash 按其原规则验证，不能重算替换；外部SourceRef只做精确引用，本地值快照有自己的Ref与hash。

同 RequestId+逐字段等价快照返回 Duplicate，不另起运算；同 ID 不同内容返回短拒绝 `CG014RequestConflict`，原操作不变。仅凭调用方 hash 相同不视作等价。重复者的 admissionToken 不能取消原操作；显式 CancelAsync 才作用于已登记请求。同 ID 终态重提只能取原回执，改输入须新 ID。

记录保留至服务实例关闭且宿主已取回所需结果，不按 LRU 覆盖、不复用 ID。超过 MaxRetainedOperations 立即短拒绝，不创建无法查询的操作。成功结果和值回执由服务持有不可变副本；临时快照/工作缓冲在 ResourcesReleased 释放，结果与墓碑占用已计入 MaxResultBytes/保留配额，不把“释放工作资源”说成删除结果。Stop 后仍可查终态和墓碑；宿主停止使用服务并释放实例后，不保证跨实例查询。可连续生产的宿主按服务 epoch 轮转并保存已取回回执，不以无限保留实现长稳。


### 4.3 冻结literal公开声明与factory

以下为可组成一个`net10.0`契约源文件的**公开声明规格**，仅使用BCL（System.Collections.Immutable随.NET共享框架提供，不引NuGet包）；无业务实现/构建结果声明。record/ImmutableArray本身不验证值：服务接纳/工厂统一执行正文规则，ImmutableArray.IsDefault/null必填值拒绝；sealed叶类型闭合分支，抽象基类外部未知派生一律CG001。所有枚举显式值稳定，序列化type tag固定为下列大小写名称；枚举以int32、bool一字节0/1、TimeSpan.Ticks以int64编码，其余结构按声明参数顺序。Ref自身Hash排除规则见§4.2，nullable/default不能等价空集合。

```csharp
using System;
using System.Collections.Immutable;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
namespace Asun.Modules.CoordinateGeometry;

public enum Unit { Pixel=0, Nanometre=1, Micrometre=2, Millimetre=3, Metre=4 }
public enum Boundary { Closed=0, Open=1, HalfOpen=2 }
public enum Handedness { Oriented2D=0, Right3D=1, Left3D=2 }
public enum PixelConvention { None=0, Center=1, Corner=2 }
public enum Traversal { Forward=0, Inverse=1 }
public enum InverseKind { Forbidden=0, Analytic=1, ProvidedInverse=2 }
public enum UncertaintyRequirement { Optional=0, Required=1 }
public enum UncertaintyKind { NotProvided=0, Propagated=1, FirstOrderLocal=2, NotEvaluated=3 }
public enum Admission { Accepted=0, Duplicate=1, Rejected=2 }
public enum OperationState { Accepted=0, Validating=1, Executing=2, Draining=3,
    Drained=4, ResourcesReleased=5, Completed=6, Rejected=7, Cancelled=8, TimedOut=9, Failed=10 }
public enum CancellationCause { None=0, User=1, Deadline=2, ServiceStop=3 }
public enum DrainStatus { Pending=0, Confirmed=1, Unknown=2 }
public enum LookupKind { Found=0, NotFound=1, Unknown=2 }
public enum WaitObservation { Terminal=0, WaitExpired=1, WaitCancelled=2, Unknown=3, NotFound=4 }
public enum ServiceState { Accepting=0, Draining=1, Stopped=2 }
public enum EventKind { Lifecycle=0, Progress=1 }
public enum ErrorCode { CG001=1, CG002=2, CG003=3, CG004=4, CG005=5, CG006=6,
    CG007=7, CG008=8, CG009=9, CG010=10, CG011=11, CG012=12, CG013=13,
    CG014=14, CG015=15, CG016=16, CG017=17, CG018=18, CG019=19, CG020=20 }
public enum ParameterUnit { SourceLength=0, TargetLength=1, TargetPerSource=2,
    Radian=3, Dimensionless=4 }
public enum GeometryScalarUnit { FrameLength=0, ReciprocalFrameLength=1, Radian=2, Dimensionless=3 }
public sealed record AssetRef(string Id, ulong Revision, string Hash);
public readonly record struct Point2(double X, double Y);
public readonly record struct Point3(double X, double Y, double Z);
public sealed record Matrix(int Rows, int Columns, ImmutableArray<double> Values);
public sealed record AxisSpec(string Name, string Direction, AssetRef BasisRef);
public abstract record Domain;
public sealed record UnboundedDomain : Domain;
public sealed record Box2Domain(Point2 Minimum, Point2 Maximum, Boundary Boundary) : Domain;
public sealed record Polygon2Domain(ImmutableArray<Point2> Outer,
    ImmutableArray<ImmutableArray<Point2>> Holes, Boundary Boundary) : Domain;
public sealed record Box3Domain(Point3 Minimum, Point3 Maximum, Boundary Boundary) : Domain;
public sealed record Frame(AssetRef Ref, int Dimension, ImmutableArray<AxisSpec> Axes,
    Handedness Handedness, Unit Unit, PixelConvention PixelConvention, Domain Domain, AssetRef SourceRef);
public abstract record GeometryValue;
public sealed record Point2Value(Point2 Value) : GeometryValue;
public sealed record Point3Value(Point3 Value) : GeometryValue;
public sealed record Vector2Value(Point2 Value, Point2? Anchor) : GeometryValue;
public sealed record Vector3Value(Point3 Value, Point3? Anchor) : GeometryValue;
public sealed record Normal2Value(Point2 Value, Point2? Anchor) : GeometryValue;
public sealed record Normal3Value(Point3 Value, Point3? Anchor) : GeometryValue;
public sealed record Segment2Value(Point2 A, Point2 B) : GeometryValue;
public sealed record Segment3Value(Point3 A, Point3 B) : GeometryValue;
public sealed record Polyline2Value(ImmutableArray<Point2> Vertices, bool Closed) : GeometryValue;
public sealed record Polyline3Value(ImmutableArray<Point3> Vertices, bool Closed) : GeometryValue;
public sealed record Polygon2Value(ImmutableArray<Point2> Outer,
    ImmutableArray<ImmutableArray<Point2>> Holes) : GeometryValue;
public sealed record Circle2Value(Point2 Center, double Radius) : GeometryValue;
public sealed record Arc2Value(Point2 Center, double Radius, double Start, double Sweep) : GeometryValue;
public sealed record Ellipse2Value(Point2 Center, Matrix Basis) : GeometryValue;
public sealed record EllipticArc2Value(Point2 Center, Matrix Basis, double Start, double Sweep) : GeometryValue;
public sealed record Plane3Value(Point3 Normal, double D) : GeometryValue;
public sealed record AngleInterval(double Start, double Sweep);
public sealed record RationalConicArc2Value(Matrix Coefficients, AngleInterval? Interval) : GeometryValue;
// Interval null means full curve; Coefficients is D multiplying [cos(t),sin(t),1], not K.
public sealed record VariableKey(AssetRef Owner, string ScalarPath, double Scale,
    ParameterUnit? ParameterUnit, GeometryScalarUnit? GeometryUnit);
public abstract record CovarianceInput;
public sealed record NoCovariance : CovarianceInput;
public sealed record LinearizationSpec(AssetRef Frame, Domain Domain, AssetRef EvidenceRef);
public sealed record CovarianceBlock(ImmutableArray<VariableKey> Variables, Matrix Values, AssetRef SourceRef,
    ImmutableArray<LinearizationSpec> Linearizations);
public sealed record IndependentCovariance(ImmutableArray<CovarianceBlock> Blocks) : CovarianceInput;
public sealed record JointCovariance(CovarianceBlock Block) : CovarianceInput;
public sealed record GeometryBatch(AssetRef Ref, AssetRef Frame,
    ImmutableArray<GeometryValue> Items, CovarianceInput Uncertainty);
public abstract record TransformModel;
public sealed record IdentityModel : TransformModel;
public sealed record Translation2Model(Point2 Offset) : TransformModel;
public sealed record Translation3Model(Point3 Offset) : TransformModel;
public sealed record Rigid2Model(Matrix Rotation, Point2 Offset) : TransformModel;
public sealed record Rigid3Model(Matrix Rotation, Point3 Offset) : TransformModel;
public sealed record Affine2Model(Matrix Parameters) : TransformModel;
public sealed record Affine3Model(Matrix Parameters) : TransformModel;
public sealed record Projective2Model(Matrix Parameters) : TransformModel;
public sealed record PlaneLiftModel(Point3 Origin, Matrix Basis) : TransformModel;
public sealed record ExternalModel(AssetRef ModelRef, string CapabilityId) : TransformModel;
public sealed record ModelParameter(string Name, ParameterUnit Unit, double Scale);
public sealed record InverseSpec(InverseKind Kind, AssetRef? InverseEdge,
    Domain? ValidDomain, AssetRef? EvidenceRef);
public sealed record Edge(AssetRef Ref, AssetRef Source, AssetRef Target, TransformModel Model,
    Domain ValidDomain, InverseSpec Inverse, AssetRef SourceRef,
    ImmutableArray<ModelParameter> ParameterOrder, CovarianceBlock? ParameterCovariance,
    AssetRef? QualityRef);
public sealed record GraphSnapshot(AssetRef Ref, ImmutableArray<Frame> Frames, ImmutableArray<Edge> Edges);
public sealed record EdgeStep(AssetRef Edge, Traversal Direction);
public abstract record PathSelection;
public sealed record ExplicitPath(ImmutableArray<EdgeStep> Steps) : PathSelection;
public sealed record ResolveUniquePath : PathSelection;
public sealed record CheckConsistencyPath(GeometryBatch Probes, double Tolerance,
    AssetRef ToleranceSourceRef) : PathSelection;
public sealed record FrameNumericRule(AssetRef Frame, ImmutableArray<double> AxisScales,
    double BoundaryGuard, double MaximumCoordinateMagnitude);
public sealed record AlgorithmLimits(int MaxJacobiSweeps, int MaxRationalBits,
    long MaxPredicateSteps, int MaxRootBisections, int MaxSeriesTerms, int MaxVariables);
public sealed record NumericPolicy(AssetRef Ref, ImmutableArray<FrameNumericRule> FrameRules,
    double MaximumConditionNumber, double MinimumDenominatorRatio, double OrthogonalityTolerance,
    double CovarianceTolerance, double InverseResidualTolerance, int MaxPathDepth,
    int MaxPathCandidates, long MaxGraphVisits, UncertaintyRequirement UncertaintyRequirement,
    AlgorithmLimits AlgorithmLimits, AssetRef SourceRef);
public abstract record RequestWork;
public sealed record MapWork(GraphSnapshot Graph, AssetRef Source, AssetRef Target,
    PathSelection Path, GeometryBatch Batch, NumericPolicy NumericPolicy) : RequestWork;
public sealed record ValidateGraphWork(GraphSnapshot Graph, NumericPolicy NumericPolicy) : RequestWork;
public sealed record GeometryRequest(string ContractVersion, string RequestId,
    RequestWork Work, TimeSpan ExecutionBudget);
public sealed record RuntimeLimits(int MaxConcurrentOperations, long MaxRetainedOperations,
    long MaxItems, long MaxVertices, int MaxFrames, int MaxEdges, long MaxInputBytes,
    long MaxResultBytes, long MaxWorkingBytes, TimeSpan MaxExecutionBudget);
public sealed record Receipt(string ServiceInstanceId, string RequestId, Admission Admission,
    string? InputHash, ErrorCode? Error);
public sealed record DiagnosticDetail(string Name, double? Number, Unit? Unit,
    string? Token, AssetRef? Ref);
public sealed record Diagnostic(ErrorCode? Code, string MessageKey, string Stage,
    long? ItemIndex, long? VertexIndex, AssetRef? EdgeRef, ImmutableArray<DiagnosticDetail> Details);
public abstract record GeometryResult(AssetRef GraphRef, string InputHash,
    AssetRef NumericPolicyRef, AssetRef BackendRef, ImmutableArray<Diagnostic> Diagnostics);
public sealed record MappedResult(AssetRef Graph, string Input, AssetRef Policy, AssetRef Backend,
    ImmutableArray<Diagnostic> Messages, GeometryBatch Batch, AssetRef Source, AssetRef Target,
    ImmutableArray<EdgeStep> Path, UncertaintyKind Uncertainty, CovarianceBlock? OutputCovariance,
    AssetRef? LinearizationEvidence) : GeometryResult(Graph, Input, Policy, Backend, Messages);
public sealed record GraphValidatedResult(AssetRef Graph, string Input, AssetRef Policy, AssetRef Backend,
    ImmutableArray<Diagnostic> Messages) : GeometryResult(Graph, Input, Policy, Backend, Messages);
public sealed record OperationSnapshot(Receipt Receipt, OperationState State, ulong Sequence,
    CancellationCause CancellationCause, DrainStatus Drain, GeometryResult? Result, ErrorCode? Error);
public sealed record Lookup(LookupKind Kind, OperationSnapshot? Snapshot, ErrorCode? Error);
public sealed record WaitOutcome(WaitObservation Observation, Lookup Lookup);
public sealed record DrainOutcome(ServiceState Service, DrainStatus Drain, long ActiveCount, ErrorCode? Error);
public sealed record OperationEvent(string ServiceInstanceId, string RequestId, ulong Sequence,
    EventKind Kind, OperationState State, long? ItemsCompleted, ErrorCode? Error);
public sealed record BackendCapabilities(AssetRef Ref, ImmutableArray<string> CapabilityIds);
public sealed record BackendInvocation(string InvocationId, GraphSnapshot Graph,
    EdgeStep Step, GeometryBatch Input, NumericPolicy NumericPolicy, TimeSpan RemainingBudget);
public sealed record BackendDerivatives(Matrix InputJacobian, Matrix ParameterJacobian,
    ImmutableArray<ModelParameter> ParameterOrder, Domain LinearizationDomain, AssetRef EvidenceRef);
public sealed record BackendMapOutcome(GeometryBatch? Output, BackendDerivatives? Derivatives,
    DrainStatus Drain, ErrorCode? Error, ImmutableArray<Diagnostic> Diagnostics);
public sealed record BackendDrainOutcome(string InvocationId, DrainStatus Drain,
    long ActiveLeaseCount, ErrorCode? Error);
public interface IGeometryBackend
{
    BackendCapabilities Capabilities { get; }
    ValueTask<BackendMapOutcome> MapAsync(BackendInvocation invocation, CancellationToken operationToken);
    ValueTask<BackendDrainOutcome> DrainAsync(string invocationId, TimeSpan waitBudget,
        CancellationToken waitToken);
}
public interface ICoordinateGeometryService
{
    string ServiceInstanceId { get; }
    AssetRef BackendRef { get; }
    ValueTask<Receipt> SubmitAsync(GeometryRequest request, CancellationToken admissionToken);
    ValueTask<WaitOutcome> WaitAsync(string requestId, TimeSpan waitBudget, CancellationToken waitToken);
    ValueTask<Lookup> QueryAsync(string requestId, CancellationToken queryToken);
    ValueTask<Lookup> CancelAsync(string requestId, CancellationToken commandToken);
    ValueTask<DrainOutcome> StopAndDrainAsync(TimeSpan waitBudget, CancellationToken waitToken);
    IAsyncEnumerable<OperationEvent> ObserveAsync(string requestId, ulong afterSequence,
        CancellationToken observationToken);
}
public interface ICoordinateGeometryFactory
{
    ICoordinateGeometryService CreateManaged(RuntimeLimits limits, TimeProvider clock);
    ICoordinateGeometryService CreateWithBackend(RuntimeLimits limits, TimeProvider clock,
        IGeometryBackend backend);
}
```

实现类固定公开为`CoordinateGeometryFactory : ICoordinateGeometryFactory`，公开无参构造`CoordinateGeometryFactory()`；两factory方法签名与interface相同，内部创建不公开具体service类。生产入口/Exe可`new CoordinateGeometryFactory().CreateManaged(limits, TimeProvider.System)`；声明以上interface方便宿主显式注入，不能靠反射寻找factory。没有待选factory/容器/API。CreateWithBackend借用backend，只由共同宿主在所有service Confirmed后卸载；service不得Dispose宿主backend。Managed固定BackendRef为版本化算法引用，由发布包实际程序集/算法hash提供，不伪造预发布hash；factory读取已经注入/发布的静态本包版本元数据，不访问文件/网络。

Matrix.Values长度必须checked等于Rows×Columns、shape按模型约束；列数/值类型不推模型。AxisSpec.Direction固定ASCII`PositiveX/NegativeX/PositiveY/NegativeY/PositiveZ/NegativeZ`及BasisRef，同frame轴名不同且匹配维度；Cartesian/ImageColumnRow是帧轴语义而非新增enum。后端Capabilities显式声明`Affine2Points/Affine3Points/Projective2Points/PixelBridge/PlaneToWorld/CameraProjection/DistortionPoints/LocalFieldPoints`；能力ID大小写固定，未知ID拒绝，不用前缀猜能力。IGeometryBackend只映射**一条已选边**，不能自己解析另一条路径；不支持的geometry返回CG019，不能quietly point-sample。

AlgorithmLimits所有项正整数，MaxJacobiSweeps≤128、MaxRationalBits≥4096且≤1,048,576、MaxVariables≤4096；MaxRootBisections/MaxSeriesTerms≤65,536。MaxPredicateSteps为正long，每个谓词、精确算术、Sturm除法/二分、级数项/SVD旋转都递减；资源/duration同时有效。硬上限是软件表示/有界运行域，不是性能目标。NumericPolicy OrthogonalityTolerance/InverseResidualTolerance∈(0,1)，CovarianceTolerance∈[0,1)，其余§4.1范围。Ref/声明/参数有限性按§3；非有限在接纳封存时CG001短拒绝，不为不可hash的值创建Accepted记录。

VariableKey.Owner用GeometryBatch.Ref或Edge.Ref定位；ScalarPath是§3.8顺序的稳定路径，如`items[0].point.x`、`items[1].outer[2].y`、`parameters.m11`；名称由本模块编码表生成而非任意JSON路径。ParameterUnit/GeometryUnit二选一，Scale正有限，geometry位置/中心/半径/Vector位移为FrameLength，Normal单位方向为Dimensionless；本契约不另加含糊的Direction向量类别，需要方向的消费者用单位化Normal仅限其法向语义，切向方向由Vector自行显式单位化并保留长度变量来源；Plane单位法向Dimensionless、d为FrameLength，Ellipse基为FrameLength，Conic chart为Dimensionless规范系数。JointCovariance包含输入和路径参数全部变量则Edge.ParameterCovariance必须null，避免重复加同一块；Independent时重复同Edge参数仅一块；NoCovariance+存在Edge协方差只能产生PartialUncertainty诊断/NotEvaluated，Required拒绝，不宣称完整传播。

Model parameter矩阵系数canonical列表由模型生成并与Edge.ParameterOrder逐项一致；Position维度/向量意义在§3.3；BackendInvocation RemainingBudget不得重置原期限，operationToken仅发协作取消，Drain接口waitToken只停止观察。Output.Ref及hash由模块值规约验证，外部不是可信结果签名；BackendMapOutcome.Drain=Confirmed且ActiveLeaseCount最终0才归还，返回Output但Drain未知仍无可消费结果。Dispose调用从service移除：唯一资源关闭方法是StopAndDrainAsync；没有隐式await using掩盖Unknown。

结果GeometryBatch.Ref固定为Id=`out.`+InputHash（68 ASCII字符）、Revision=1、Hash按输出值自身Ref排除规约计算；同一input/backend/policy确定输出值才得相同hash，不包括随机ServiceInstanceId。InputHash的请求身份还要编码实际BackendRef/Capabilities.Ref作为执行身份前缀（区别§4.2的caller原始快照声明），否则相同请求改backend不能伪称同一次计算；该版本前缀在服务接纳时固定，进度/epoch不参与。结果协方差VariableKey.Owner以输出Batch.Ref引用，ScalarPath对应实际输出几何表示；输出从Circle变Ellipse时键/维度按新结构重建，不复用源radius键冒充ellipse误差。Result中的batch.Uncertainty与OutputCovariance一致：Propagated/FirstOrderLocal为JointCovariance输出块；NotProvided/NotEvaluated为NoCovariance，诊断可引用输入缺口但不提供可消费“部分完整”块。


#### 4.3.1 已支持模型的参数名称编码表

本表是§3.8/4.3所称“本模块编码表”的唯一模型参数名称来源。`ModelParameter.Name`为下表裸名，按ordinal逐字、区分大小写比较；不含`parameters.`前缀。本地固定名称全部ASCII。`VariableKey.Owner=原Edge.Ref`，`ScalarPath="parameters."+Name`，`ParameterUnit=同项ModelParameter.Unit`，`GeometryUnit=null`，`Scale=同项ModelParameter.Scale`。不按DTO属性名、JSON路径、轴显示名、数组顺序猜别名；例如`parameters.tx`有效，`tx`、`parameters.offset.x`、`parameters.m14`均不能替代Affine3的偏移键。几何变量仍用原GeometryBatch.Ref及既有`items[...]`路径，不改名。

| 模型（实际公开叶类型） | ParameterOrder的完整Name顺序 | ParameterUnit与值来源 |
|---|---|---|
| IdentityModel | 空数组（非default），0项 | 无参数；不插入单位阵系数 |
| Translation2Model / Translation3Model | `tx,ty` / `tx,ty,tz`，2/3项 | 全部TargetLength；分别取Offset.X/Y[/Z] |
| Rigid2Model | `m11,m12,m21,m22,tx,ty`，6项 | 前4项Dimensionless，按Rotation 2×2 row-major；末2项TargetLength，取Offset.X/Y |
| Rigid3Model | `m11,m12,m13,m21,m22,m23,m31,m32,m33,tx,ty,tz`，12项 | 前9项Dimensionless，按Rotation 3×3 row-major；末3项TargetLength，取Offset.X/Y/Z |
| Affine2Model | `m11,m12,m21,m22,tx,ty`，6项 | 前4项TargetPerSource，取Parameters 3×3线性块；末2项TargetLength，取最后列的前2值 |
| Affine3Model | `m11,m12,m13,m21,m22,m23,m31,m32,m33,tx,ty,tz`，12项 | 前9项TargetPerSource，取Parameters 4×4线性块；末3项TargetLength，取最后列的前3值；逐索引见§4.3.2 |
| Projective2Model | 从`m11,m12,m13,m21,m22,m23,m31,m32,m33`删除§3.5确定的唯一pivot名称，保持剩余row-major，8项 | 全部Dimensionless，取除pivot后的数值chart系数；pivot=+1是约束，不生成VariableKey，不固定假设m33为pivot |
| PlaneLiftModel | `ox,oy,oz,b11,b12,b21,b22,b31,b32`，9项 | 前3项TargetLength，取Origin.X/Y/Z；后6项TargetPerSource，取Basis 3×2 row-major |
| ExternalModel | 原封存Model/BackendDerivatives.ParameterOrder明确提供的Name顺序 | 原Unit与Scale逐项透传、核对；不得从camera tuple、capabilityId或局部cell自行发明本地参数表 |

`mij`/`bij`中的行列号为**1-based**语义编号；存储下标为**0-based**。Affine2的值索引依次为`0,1,3,4,2,5`；Rigid2的Rotation索引为`0,1,2,3`，Rigid3为`0..8`；PlaneLift的Basis为`0..5`。固定齐次末行不属于ParameterOrder。Rigid的矩阵系数仍是受正交约束的参数表示，不因列出9项而改成自由Affine参数或另用Euler/Quaternion。

Projective的Dimensionless是已冻结**数值chart**的单位：源坐标以“1个源Frame单位”、目标坐标以“1个目标Frame单位”表示为数值，H作用于这些数值后按§3.3除w；不把m31/m32称为物理TargetPerSource，不新增缺失的倒长度ParameterUnit，也不在映射/Jacobian时另乘Frame单位。pivot选择、整体尺度消除、chart边界和局部协方差适用性沿§3.5/3.8，源目标Frame单位/引用仍完整绑定；本节只命名已存在的chart参数。

**Scale来源与验证。** `ModelParameter.Scale`是该参数在本行Unit/chart中用于协方差归一的正有限数值尺度，宿主从冻结的参数/协方差数值配置显式提供；无协方差时也必须显式给完整ParameterOrder。它不是变换系数或单位换算因子，也不表示已声明标准差或FrameNumericRule.AxisScales；不从`abs(value)`生成，不因系数为0而给0，不自动按单位设默认值。模块由模型生成Name/Unit模板，用调用方显式Scale校验完整数组，并使同参数VariableKey逐项同Scale；相同名字错误顺序/单位、漏项/重复/未知名、default、非正/非有限Scale均按原CG001拒绝，缺协方差变量按原§3.8/4.3处理。Scale不同意味着不同值快照，沿旧编码/hash规约处理，不增加新身份算法。

External名字非空、ordinal唯一，必须来自同一封存参数声明；ScalarPath仅在名称原样加一次`parameters.`，作为不透明键与原声明严格匹配，不解析`.`、`[]`为DTO成员访问。无原声明则不能替它造协方差参数；几何调用能否无导数执行仍沿Optional/Required及§9，不扩大外部模型支持。Forward/Inverse遍历均以原Edge参数Owner/Name/Scale为变量来源，逆的导数沿原表达式求，不生成“inverse.tx”或另一套参数身份；ProvidedInverse实际采用另一Edge时使用那条Edge自己的表。

#### 4.3.2 Affine3逐项索引、Host-B软件单位边与一致断言

真实消费者为[metrology §20.5 Host-B](../metrology/DEVELOPMENT-GUIDE.md#205-两个独立无ui-host的装配配方)的S-CG。这里只补原Host的矩阵/参数literal条目，不改它的Reader、RS、Scope、Trace、数值策略或运行门。U为Micrometre源Frame，M为Metre源Frame，T为Millimetre目标Frame；沿其冻结的Frame、Domain、SourceRef与ExplicitPath，不把换单位当改标签。两条边均使用既有`Affine3Model(new Matrix(4,4,Values))`；Translation/Rigid不允许跨单位。

| ParameterOrder索引（0-based） | Name | ScalarPath | Parameters.Values索引 | ParameterUnit | U→T系数值 | M→T系数值 | ModelParameter.Scale |
|---|---|---|---|---|---|---|---|
| 0 | m11 | parameters.m11 | 0 | TargetPerSource | .001 | 1000 | 1 |
| 1 | m12 | parameters.m12 | 1 | TargetPerSource | 0 | 0 | 1 |
| 2 | m13 | parameters.m13 | 2 | TargetPerSource | 0 | 0 | 1 |
| 3 | m21 | parameters.m21 | 4 | TargetPerSource | 0 | 0 | 1 |
| 4 | m22 | parameters.m22 | 5 | TargetPerSource | .001 | 1000 | 1 |
| 5 | m23 | parameters.m23 | 6 | TargetPerSource | 0 | 0 | 1 |
| 6 | m31 | parameters.m31 | 8 | TargetPerSource | 0 | 0 | 1 |
| 7 | m32 | parameters.m32 | 9 | TargetPerSource | 0 | 0 | 1 |
| 8 | m33 | parameters.m33 | 10 | TargetPerSource | .001 | 1000 | 1 |
| 9 | tx | parameters.tx | 3 | TargetLength | 0 | 0 | 1 |
| 10 | ty | parameters.ty | 7 | TargetLength | 0 | 0 | 1 |
| 11 | tz | parameters.tz | 11 | TargetLength | 0 | 0 | 1 |

两条软件边的`ParameterOrder`是相同的完整12项：按上表Name顺序分别构造`new ModelParameter(name,ParameterUnit.TargetPerSource,1d)`九项，再`new ModelParameter(name,ParameterUnit.TargetLength,1d)`三项；它们仍属于不同原Edge.Ref，不共享参数Owner。U→T前9项单位含义为mm/μm，M→T为mm/m；末3项均为mm。此处显式Scale=1仅为已指定**软件配置**，不冻结生产协方差尺度。ParameterCovariance/QualityRef仍null；无协方差的本Host不实际创建VariableKey，表中的ScalarPath用于后续有协方差时精确对应。

完整row-major `Values`：U→T为`[.001,0,0,0, 0,.001,0,0, 0,0,.001,0, 0,0,0,1]`；M→T为`[1000,0,0,0, 0,1000,0,0, 0,0,1000,0, 0,0,0,1]`。参数值来自这16项，不在ModelParameter中藏第二份值。`.001`为C# `0.001d`的binary64值（bits `0x3f50624dd2f1a9fc`），`1000d`为bits `0x408f400000000000`；不从本地化文本解析或以Scale再乘一次。Ref/hash继续按§4.2/4.3旧规则从实际完整Frame/Edge/Graph/Policy构造，本文不捏造它们的内容hash。

**多作者一致验收（接入原CGT-API/CGT-COV/CGT-VERSION与消费者Host断言，不新增测试工程/Golden文件）。** 独立作者A按本表逐项literal构造，作者B按`i=1..3`、`j=1..3`循环生成`mij`并读`Values[4*(i-1)+(j-1)]`，随后按XYZ生成`tx,ty,tz`并读`Values[3,7,11]`。两者必须得到完全相同的12项Name/Unit/Scale、ScalarPath和参数值bits；不得由同一产品生成函数同时生成输入和期望。检查项如下，实际C#执行仍属后续实现验证：

1. 完整表包含9系数+3偏移，零项仍保留；非对称诊断矩阵`[1,2,3,10, 4,5,6,20, 7,8,10,30, 0,0,0,1]`的参数值顺序必须为`[1,2,3,4,5,6,7,8,10,10,20,30]`，用于捕获把齐次4×4前12项直接当ParameterOrder或列主序的错误；仅为索引断言，不新增数学Golden。
2. 原U四点`(0,0,0),(1000,0,0),(0,1000,-100),(1000,1000,0)`映到T为`(0,0,0),(1,0,0),(0,1,-.1),(1,1,0)`，结果按原Host Numeric公差比较，矩阵输入bits逐值严格相同。原M平面`n=+Z,d=-2m`沿既有Plane规则到T仍`n=+Z,d=-2000mm`；RS原点`(1/3,1/3,2)m`到`(1000/3,1000/3,2000)mm`。不再按Unit或Scale加乘1000/.001，不为软件平面授物理支撑。
3. A/B构造相同完整快照时，旧`coordinate-core-values-v1`编码字节、Edge/Graph/InputHash及逐字段值一致（使用原自Ref排除规则，不把不同Edge的hash要求相等）；两个Edge的Name/Unit/Scale虽相同，Ref/源Frame/系数值及请求绑定仍不同。交换m12/m21、改名为m14/offset.x、漏零项、加末行、用Dimensionless替Affine3的TargetPerSource必须拒绝；Scale=0/NaN或VariableKey.Scale与原参数不一致也拒绝，不仅凭hash相等采用。
4. 其它已支持模型逐表核数量/名称/单位；Projective分别选不同pivot时只删除实际pivot并保留剩余顺序，同幅值按旧row-major首项决定，不固用m33；Scale/协方差chart不同按原版本/值规约处理，不跨chart冒充相同参数。Forward/Inverse重用同Edge变量仍只登记一次。全部断言沿原有限预算、取消和资源协议，不借此重审SVD/PSD/Jacobian或旧Golden。

§4.3.1–2完整名称/顺序/ScalarPath/Scale规则及Affine3索引、两条软件单位边指导已获主控限定内容接收，S-CG参数名的**文档欠账已关闭**；metrology原Owner已获派精确消费，本模块不修改其欠账表或宣称Host-B已运行。未执行本模块C#编译、上述Host/多作者产品测试、HALCON/CameraRead/Viewport/WPF、性能或物理资格；原Core A/B/C/D/E接收与适配PreparationIncomplete/NotReady保持。

### 4.4 CG-Core-E：通用闭像素支撑全域分母证据（DenominatorEvidenceV1）

**职责与单一Owner。** 真实首消费者是定位宿主的全域projective用途证据桥（只读需求依据：[alignment-2d §4.14及§12.2](../alignment-2d/DEVELOPMENT-GUIDE.md)），第二复用消费者是ROI投影/拼接预检；二者都通过此公开计算能力取得相同w界和witness，不复制几何算法。本模块只计算提交系数在显式支撑域上的分母事实/比例门，不拟合矩阵、不签Qualified/质量/物理资格。定位模块§4.14的用途DTO只由其宿主adapter映射，本文/本程序集不引用该DTO/程序集或其专用枚举。新增独立namespace、factory与输出，不扩展/重审已接收`ICoordinateGeometryService` v0.2、NumericPolicy或CG-Core-A/B/C/D。

| 门口径 | 定义/消费者 | 禁止混用 |
|---|---|---|
| 既有点/projective数值安全 | `abs(w)/(norm2(H第三行)*norm2(p))`，norm2为Euclidean norm，p为源frame齐次点，§3.3/3.7/4.3的MinimumDenominatorRatio | 该门回答局部数值远离分母安全带；本新切片不读取/替换它 |
| 本切片全域分母变化比 | 闭像素run凸片各自不跨0，`global MinAbs(w)/global MaxAbs(w)≥MinimumGlobalAbsRatio` | 不包含第三行或p的norm；只通过该门不表示旧安全门/条件数/Jacobian/伸缩/shear/质量通过 |

明确反例：identity H的w=1，本门在任意有限支撑域ratio=1；若源点x=10⁶，旧归一比约10^-6，旧门0.5拒绝。反向例：单run经affine x=0.99*c+1.51（c∈[-0.5,0.5]）、H第三行=(1,0,-1)，w∈[0.015,1.005]，本门0.02拒绝；旧归一门0.001可以全部通过（最小旧比仍>0.007）。各自门保持参数来源，不用统一“DenominatorRatio”名字覆盖含义。

#### 4.4.1 完整literal公开值/端口与创建

新协议标识`cg-cell-denominator-v1`，方法版本`ExactBinary64DyadicV1`。只依赖本Core的AssetRef、Frame、Matrix、ErrorCode及BCL；不调用HALCON、不读取ROI、不取得lease、不发设备动作。像素输入整数定义与§3图像column/row（Y向下）区别由显式`PixelCellCoordinates.ColumnNegativeRow`声明。以下声明置于独立契约源文件，既有v0.2公开声明保持原样。

```csharp
using System;
using System.Collections.Immutable;
using System.Numerics;
using System.Threading;
using Asun.Modules.CoordinateGeometry;
namespace Asun.Modules.CoordinateGeometry.DenominatorEvidenceV1;

public enum PixelCellCoordinates { ColumnNegativeRow=0 }
public enum PixelSupportConvention { ClosedPixelCells=0 }
public enum DenominatorSign { Positive=0, Negative=1, ContainsZero=2 }
public enum CellCorner { LeftBottom=0, RightBottom=1, RightTop=2, LeftTop=3 }
public enum DomainRangeState { Complete=0, InvalidInput=1, ResourceLimited=2,
    Cancelled=3, TimedOut=4, Failed=5 }
public enum EvidenceCheckState { Consistent=0, Inconsistent=1, NotEvaluated=2 }
public readonly record struct PixelRun(int Row, int FirstColumn, int LastColumn);
public sealed record ExactDyadic(BigInteger Mantissa, int Exponent2);
public sealed record PixelRunDomain(AssetRef DomainRef, AssetRef SourceBindingRef,
    Frame PixelFrame, int RasterWidth, int RasterHeight,
    PixelCellCoordinates Coordinates, PixelSupportConvention Support,
    ImmutableArray<PixelRun> Runs);
public sealed record AffineDomainMapping(AssetRef Ref, Frame Source, Frame Target,
    Matrix CentreMatrix, AssetRef SourceRef);
public sealed record ProjectiveCoefficients(AssetRef Ref, Frame Source, Frame Target,
    Matrix CentreMatrix);
public sealed record DomainRangeInput(string CalculationId, PixelRunDomain Domain,
    AffineDomainMapping PixelToSource, ProjectiveCoefficients Projective,
    double MinimumGlobalAbsRatio, AssetRef RatioPolicyRef);
public sealed record DomainRangeLimits(int MaxRuns, long MaxBytes, int MaxMantissaBits,
    long MaxExactSteps);
public sealed record DomainRangeControl(DomainRangeLimits Limits, long DeadlineTimestamp);
public sealed record CornerWitness(CellCorner Corner, ExactDyadic PixelX, ExactDyadic PixelY,
    ExactDyadic SourceX, ExactDyadic SourceY, ExactDyadic W);
public sealed record RunDenominatorPiece(int RunIndex, PixelRun Run,
    ImmutableArray<CornerWitness> Corners, ExactDyadic MinW, ExactDyadic MaxW,
    DenominatorSign Sign, ExactDyadic MinAbs, ExactDyadic MaxAbs);
public sealed record RunCoverage(int ExpectedRunCount, int EvaluatedRunCount, bool Complete);
public sealed record DomainRangeEvidence(string ContractVersion, string NumericMethod,
    AssetRef EvaluatorRevision, DomainRangeInput Input, string InputDigest,
    ImmutableArray<RunDenominatorPiece> Pieces, RunCoverage Coverage,
    ExactDyadic? MinAbs, ExactDyadic? MaxAbs, bool? ThresholdPassed);
public sealed record DomainRangeOutcome(string CalculationId, DomainRangeState State,
    ErrorCode? Error, DomainRangeEvidence? Evidence, bool WorkingResourcesReleased,
    long ChargedBytes, long ExactSteps);
public sealed record EvidenceCheckOutcome(EvidenceCheckState State, ErrorCode? Error,
    long ChargedBytes, long ExactSteps);
public interface ICellDenominatorEvaluator
{
    AssetRef Revision { get; }
    DomainRangeOutcome Evaluate(DomainRangeInput input, DomainRangeControl control,
        CancellationToken operationToken);
    EvidenceCheckOutcome CheckEvidence(DomainRangeInput expectedInput, DomainRangeEvidence evidence,
        DomainRangeControl verificationControl, CancellationToken verificationToken);
}
public interface ICellDenominatorEvaluatorFactory
{
    ICellDenominatorEvaluator Create(TimeProvider clock);
}
```

公开实现固定`CellDenominatorEvaluatorFactory : ICellDenominatorEvaluatorFactory`，public无参构造，Create签名如上；具体evaluator类内部化。`new CellDenominatorEvaluatorFactory().Create(hostOperationClock)`为准确装配入口。Create仅校验clock非null并保存只读引用、发布包的算法Revision，不订阅/IO/后台/lease；Revision.Id=`cg-cell-denominator-v1`、Revision.Revision=1、Hash由未来真实实现发布包给出，本轮不伪造二进制hash。Evaluate/CheckEvidence同步、有界、可并发，每调用隔离scratch、计账与取消；不拥有/Dispose调用方时钟/资产/ROI资源，不要求调用者关闭evaluator。方法返回意味着本次工作已经真实结束，WorkingResourcesReleased=true才允许宿主adapter回执；无在途native/Task，不能设置假Draining或用Task.WhenAny早返回。进程级OOM等无法返回受控回执时由宿主隔离记录，不承诺总能恢复。

null input/control/必填record、非法shape/enum/Ref、不可hash非有限输入返回InvalidInput/CG001（record字段失败不使用隐藏默认）。Create(null)仍ArgumentNullException。InvalidInput的Evidence=null；封存前预算/取消/截止或内部失败导致不能形成安全证据时也为null，此时无Complete或全域结论。完整计算结果State=Complete（不代表“合格”），通过/不通过独立读取ThresholdPassed；跨零或比例门拒绝时Error=null、ThresholdPassed=false，不能伪装执行失败或生成质量ErrorCode。中断State分别ResourceLimited/Cancelled/TimedOut对应CG007/CG008/CG009，纯数值实现内部异常Failed/CG010；未知外部资产/绑定CG018映射为InvalidInput。映射或H奇异/全零CG005映射为InvalidInput，不返回四角“已验完整”。CalculationId沿§3.1 Id范围；无可回显的合法ID时Outcome.CalculationId为空字符串，仅用于短拒绝。

#### 4.4.2 输入坐标、引用绑定与支撑域

本独立协议复用`Frame`值形状，但有自己的帧校验入口：`Domain.PixelFrame`必须2D、Handedness.Oriented2D、Unit.Pixel、PixelConvention.Center，轴名`X/Y`、Direction=`PositiveX/PositiveY`且同BasisRef，数值为x=column、y=-row；这是显式Cartesian像素chart，不是`ImageColumnRow`的y=row。此chart仅由新端口接收，不交给v0.2服务的Pixel帧校验器；旧§4.1的Pixel规则保持不变。其它Pixel帧在此协议中须明确选择该Cartesian chart或§3.1的ImageColumnRow，禁止同一个Ref声明两种轴/域；SI帧沿用旧规则。RasterWidth/Height正int，所有run满足`0≤Row<Height, 0≤FirstColumn≤LastColumn<Width`；端点包含，array非default且非空，按(row,firstColumn)严格排序，同row区间不交叠。相邻run共享cell边允许（即使未合并也逐条保留原run），孔/组件间隔不补，不能转一个外接矩形。Runs是完整域的值快照，不接受IEnumerable逐步截取/抽样。row/col支撑在±0.5处计算用exact整数/二分之一，先提升int64/BigInteger，int.MaxValue附近不int溢出。

每run定义闭连续矩形`x∈[FirstColumn-1/2,LastColumn+1/2]，y∈[-Row-1/2,-Row+1/2]`。固定四角顺序LB→RB→RT→LT，对应CellCorner；map/H的Matrix均必须Rows=Columns=3、Values.Length=9且非default。仿射末行**逐值严格**(0,0,1)，含-0可作精确零但输入bit原样留证。映射Source完整Frame/Ref必须与Domain.PixelFrame逐字段相等，Target与Projective.Source逐字段相等；所有重复Frame Ref的完整值/原始bit必须一致，否则CG002。Frame revision和Domain revision独立，禁止相互等号冒充绑定。相同帧也提供显式identity Matrix。mapping Ref/SourceRef为宿主明确已冻结坐标链引用，不调用latest/Resolve/重新标定；源Pixel单位、target可Pixel或SI长度，比例/平移已在矩阵编码，不再按Unit乘一次。

Domain.PixelFrame、mapping.Source/Target、Projective.Source/Target均为2D，按本节显式chart规则校验；其它Ref/单位/域/手性规则沿§3/4.3，不要求本端口未声明的AxisScales。Frame.Domain明确包含所需连续cell/映射片时，按既有§3.6 exact点/段/域内核检查原cell、四条mapped边及整个填充片（洞覆盖也检查）后再给w界；复用的是exact几何内核，不构造旧服务Map请求或绕过它的Pixel校验。不能只因四角在frame域就证明片内有效。资源计入同次Limits，不能在桥另写Polygon算法；PixelFrame.Domain固定为Closed Box2，至少包含完整栅格cell支撑[-1/2,Width-1/2]×[-Height+1/2,1/2]，不能把整数中心box误当cell域。Projective.Target域不在此切片评估（此刻只求w、未除w），输出明确不证明目标映射/越域；Projective.Source域和mapping target域对整片须有效。其它源域边界按原Core-C规则，不因新算法偷偷放宽。

拒绝Projective/nonlinear作为PixelToSource，即使它给四个看似可用角点；二维affine非奇异由**精确线性块det≠0**验证，全H精确3×3det≠0、9个finite double，末行不全零。这里不重新应用已接收NumericPolicy的条件数门，不把非奇异视为稳定/物理资格；宿主其它用途门仍另验。真Frame域检查预算不足CG007/中断，不能签全域；精确已知域外CG004为InvalidInput（完整w证据不生成）。Frame.Hash为来源值绑定，本能力不冒充验证所有外部Frame/Domain签名；宿主来源桥核发布引用，所有改变都在InputDigest可见。连续源域检查固定复用§3.6 exact guard=0规则（Boundary来自Frame.Domain，不加本切片没有声明的NumericPolicy/epsilon）；只检查实数声明域，没有新的数值/物理容差门。执行仅限2D Unbounded数学源或Box2/Polygon2值域，任何Box3/其它表示InvalidInput/CG003。检查四角/四条边/填充片及域洞见证，内部临时一般有理数的分子/分母各受本次MaxMantissaBits，primitive全部计入MaxExactSteps/MaxBytes，无隐藏domain预算或另一次无限求解。

SourceBindingRef含ROI/域Owner所确认的完整域内容绑定引用。坐标计算者可以核请求字段/本地Runs内容hash、一对一覆盖，却不能从输入数组凭空证明上游没漏run。SourceBindingRef不是模块随机签发“已完整”证书；宿主只有按准确DomainRef获取**整个**public Runs并核Owner内容引用后才可构造此输入，绑定不足在调用前返回NotEvaluated/CG018，不能把ExpectedRunCount设置为截断后count洗白。像素域本身的revision/hash与PixelFrame.Ref分别存留。CheckEvidence也只证明相对于expected完整快照的数值一致，不能代替上游完整性Owner。

#### 4.4.3 固定exact计算、证据与预算

复用§3.6 binary64→exact dyadic算术，不新增浮点几何实现。ExactDyadic值为`Mantissa×2^Exponent2`；Mantissa非零规范odd（剥除2因子）、zero唯一(0,0)，指数[-8192,8192]、位数受MaxMantissaBits，内部每次add/mul/compare在对齐指数或乘前预估新位数/bytes，超过即CG007。finite binary64包括subnormal、原H/-0 bit原样保留；算术零规范不影响原矩阵bit绑定。H不得先按max元素归一、换h33=1或经HALCON桥重新round。仿射xy不转回double后再算w，必须以输入系数exact multiply/add一路保持dyadic。

1. 先校验control/limits，再有界复制/验证完整有限input，核所有Frame/ref/axis/unit/map、runs及连续源域；预约输入、全结果witness与scratch上界，未获得额度不开始w片运算。调用期间调用方不得改变输入；封存/hash/域验证也受相同预算、token和截止，不在片循环前无限遍历。全部域验证在w片循环前完成，若此阶段发现域外则InvalidInput/Evidence=null；此阶段预算中断且安全输入/header已封存时只能给零片prefix。完整input快照、limits、clock和相同DeadlineTimestamp从宿主本operation传入，不重置期限。进入封存/原循环前、每个编码/验证/exact primitive、每片写入证据和返回完整结论前检查operationToken和同clock.GetTimestamp；先观察取消优先，然后deadline。deadline已过返回TimedOut；timestamp以该实例频率的future绝对tick声明，使用checked减/转换，overflow InvalidInput，不转UTC/另一clock；仅本进程活动有效，不持久恢复为新截止点。MaxRuns>0、MaxBytes>0、MaxExactSteps>0、MaxMantissaBits∈[4096,1048576]均必填；input count超过MaxRuns短路ResourceLimited，不返回伪完整。
2. 每run按四角exact生成(px,py)，以中心仿射矩阵求sx=`a11*px+a12*py+tx`、sy=`a21*px+a22*py+ty`；w=`h31*sx+h32*sy+h33`。四个CornerWitness同时返回px/py、sx/sy、w，固定位置顺序。MinW/MaxW取四w extrema；每个极值必须等于至少一个实际corner w，不用另一全局点/边界外的“估计值”。相同极值保留所有witness，不选择随机角。w在凸平行四边形是线性函数，极值在角点，所以这是全闭片证明，**不是只验角点是否非零**。
3. `MinW≤0≤MaxW`为ContainsZero；片MinAbs=0（哪怕四角都非零）、MaxAbs=max(abs(MinW),abs(MaxW))。否则Positive/Negative，MinAbs=min(abs(MinW),abs(MaxW))、MaxAbs同上。即使某片跨零也继续完整剩余run（在预算允许时），这样Complete=false不会误变Complete=true；全部完成再给Complete=true+ThresholdPassed=false。非连通片正/负可以并存，**不对所有片混合MinW/MaxW后推全域跨零**，也不把中间孔填上。
4. 聚合MinAbs=min(所有片MinAbs)，MaxAbs=max(所有片MaxAbs)；threshold输入finite `(0,1]`转exact binary64 dyadic，只在无ContainsZero、MaxAbs>0且`MinAbs≥threshold*MaxAbs`时true。跨零/all w零为false，不除零。精确相等通过，不凭double显示ratio≈threshold放行。MinAbs/MaxAbs均为原H尺度的证据，ratio才无量纲；此证书只证明提交系数，不包模型拟合/物理误差。H精确可表示非零倍数保持结论；对重新round的近似倍数不承诺相等。
5. 任一预算/取消/deadline中断时仅保留**全部四角及界已完成的连续run前缀**，未完run不得加EvaluatedRunCount；Coverage.Complete=false、聚合MinAbs/MaxAbs/ThresholdPassed=null。已完成的片仅Diagnostic证据，不签WholeDomain。如果资源不足连输入/最小header都无法保留则Evidence=null。绝不能用Equal count忽略错误状态，完整必须State=Complete且每个RunIndex/Run和四角都逐一匹配expectedInput。`ExpectedRunCount`固定为冻结完整Runs.Length，不能在中断时改小。
6. 输入摘要为`cg-cell-denominator-v1`专用证据编码的SHA-256小写hex64：先编码该协议字符串，再按DomainRangeInput声明顺序编码除CalculationId外的全部字段。保留H/map/threshold及Frame域等所有binary64**原始bit（包括-0）**，保留Frame/Domain/SourceBinding/map/Projective/Policy的全部引用、Frame/unit/axis/domain、raster dimensions、两项convention及原runs；字段顺序按声明、list顺序保留、int32/int64/uint64 little-endian、double按raw int64、bool一字节0/1、UTF8字符串加uint32字节长度、array加uint32数量、nullable presence一字节、闭合分支先编码§4.3大小写type tag字符串、enum为int32，Ref.Hash含原值。CalculationId与deadline/时钟/token/limits不纳入几何InputDigest（CalculationId仍在Outcome/Evidence.Input原样回显）；不能借digest相同丢掉请求ID、输入byte逐字段复核或EvaluatorRevision。对本地frame/domain嵌套值编码沿§4.3参数顺序但不生成/改写来源hash；这是外部证据输入，不重复计算Frame原hash。本方法digest不复用旧`coordinate-core-values-v1`的-0规范，从而consumer原矩阵逐bit绑定可成立。
7. 结果方法版本/ContractVersion/EvaluatorRevision/InputDigest、Input原值、每run/index/角名/像素xy/源xy/w、片sign/min/max、覆盖/聚合阈值必须互相一致。ContractVersion必须为`cg-cell-denominator-v1`、NumericMethod为`ExactBinary64DyadicV1`、EvaluatorRevision逐字段等于当前evaluator.Revision；跨方法/发布版本不能借数值相同签一致。CheckEvidence在新verificationControl的有限预算/同注入clock内重算expectedInput（它是**新的校验操作**，不延长原Evaluate截止）、调用同exact内核比较全部值/bit/refs及prefix要求；Consistent只对Complete=true、ExpectedRunCount=EvaluatedRunCount=expectedInput.Domain.Runs.Length、完整有序pieces且三个聚合字段非null的证据成立，Evidence.Input.CalculationId也须等于expectedInput.CalculationId。输入不同/漏片/改witness/非canonical dyadic/错误sign/错阈值/digest/version返回Inconsistent/CG002或CG001；expectedInput/control自身无效为NotEvaluated/相应输入错误，取消/预算/校验期限结束为NotEvaluated/对应CG008/007/009，不能false签一致。Partial证据只诊断，CheckEvidence返回NotEvaluated/CG018，不可得到WholeDomain；Complete=true却覆盖不全则Inconsistent。consumer可自行做结构/identity/整数覆盖/精确阈值交叉积核对；**不得另实现角点mapping/extrema证明**，数学复算由本Owner此方法及数值oracle负责。

可判定资源计账：ChargedBytes是本次同时驻留的**逻辑编码字节峰值**，不能冒充进程private bytes；Input编码、结果Input回显共享同一封存对象只记一次，所有pieces/witness、digest/Refs/证据header以及scratch每个BigInteger按uint32长度+signed little-endian最小字节+4-byte Exponent2（零mantissa1 byte）、每组tag/count/primitive固定编码宽度，字符串UTF8+4 length计。仅固定形状的Outcome拒绝回执壳不计MaxBytes，ID最多128 ASCII并共享合法输入ID引用；这使极小MaxBytes仍可返回Evidence=null/ResourceLimited，不超配额构造证据header。乘/add对齐新mantissa位长上界先checked预算；同时保留的算术临时都计，不只最终结果。对象容器/BigInteger backing 的实际托管分配另在Benchmark记录，内部存储受Array.MaxLength/int容量限制，不把long MaxBytes当无限数组许可。MaxExactSteps按每个dyadic encode/add/sub/mul/compare、domain primitive、run验证/摘要primitive一次递减；四角/域检查全过程共享累积，不对每run重置。可行预估不足则ResourceLimited，不临时抬quota；元数据封存之后中断的prefix不能比预估额外多分配。WorkingResourcesReleased只表示scratch所有权已清除、池借用已归还、没有工作仍使用临时对象；托管对象等待GC回收不承诺private bytes立即归零。结果immutable值由调用方拥有，不保留无界静态cache/回执。

#### 4.4.4 宿主桥与最小消费（语义用法，未编译执行）

1. 宿主建立`ICellDenominatorEvaluator evaluator = new CellDenominatorEvaluatorFactory().Create(operationClock)`；同operation用实际剩余额度换成DomainRangeLimits，TimeProvider、DeadlineTimestamp与定位原operation相同，不创建新的clock/5s默认预算。
2. 在ROI现有Acquire/lease边界取得完整Runs，核DomainRef内容绑定由ROI Owner adapter完成；lease公开只有FrameId/Revision/Runs/DisposeAsync时，不读取/捏造lease.ContentHash。核公开frame/revision和门要求的明确Pixel→Source映射，复制完整已排序非重叠Runs（计宿主copy bytes）；DomainRef/SourceBindingRef来自Owner真正核实的内容引用，domain与frame revision分别比较。lease保留至复制及evaluator调用真实结束，再按其公开DisposeAsync回执归还，失败/取消同样处理；evaluator本身不拥有lease，不凭自己同步结束宣布ROI已归还。
3. 宿主只做已有PixelRun字段逐项映射、Frame/单位/轴/Ref和Matrix九值逐bit复制。Domain.PixelFrame来自请求已冻结的ColumnNegativeRow chart，与PixelToSource.Source逐字段相等；原ROI图像frame的身份留在SourceBindingRef的Owner绑定中，不把原ImageColumnRow Ref重标为Cartesian。若H.Source为row-down图像frame，请求须明确提供chart→该frame的affine（例如y=-r还原到y=r），包括单独的chart Ref/域/来源；adapter不能在执行时自行创建/推断新Ref或反转符号/加0.5。所选域映射必须按请求固定，同帧仍identity。构造`DomainRangeInput(calculationId, PixelRunDomain(...), AffineDomainMapping(...), ProjectiveCoefficients(...), threshold, thresholdPolicyRef)`，threshold是定位全域门，不传本模块既有MinimumDenominatorRatio来凑同名字段。
4. 在宿主现有有界executor同步调用`evaluator.Evaluate(input,new DomainRangeControl(limits,originalDeadlineTimestamp),operationToken)`；异步消费端可在其已有worker中真实await adapter方法，adapter在该调用返回并复制必要值后才`ValueTask.FromResult(mappedEvidence)`，不每候选Task.Run、不用Task.WhenAny“native已停”假回执。CheckEvidence在显式新的verification窗口下可用于接收/Replay；要把它放在原operation中时仍用其剩余截止，不暗自延时。
5. adapter把本模块Pieces逐一投影到消费者piece格式，已有消费者不含CornerWitness字段时仍保留`DomainRangeEvidence`完整值作为SourceRevision/InputDigest绑定的原件，不能丢实际witness仅保留一个WholeDomain bool。字段映射为source matrix=Evidence.Input.Projective.CentreMatrix原bits、domain/mapping=Input原值、片min/max/sign=同run结果、MinAbs/MaxAbs/ThresholdPassed=原聚合、Coverage=原完整coverage、数值版本=NumericMethod与EvaluatorRevision。宿主自身类型包装只表明引用/消费，不成为另一算法。
6. `State=Complete && Coverage.Complete`时消费者可读ratio门true/false；其它情况映射NotEvaluated，不把Cancelled/ResourceLimited prefix当完整Rejected几何结论。用途最终资格须合并它自己的Jacobian/伸缩/shear/条件/物理门，本能力不会给其Qualification枚举。已旧证据只有Status=Qualified/WholeDomain或display比率没有确切pieces与witness时拒绝消费。任何变H/Domain/map/threshold/frame/SourceBindingRef重建input并新Calculate，consumer不能修改evidence归属/ID来复用。

本闭包声明门是**内部公共契约准备**，本轮已在本Owner冻结，不冒作“客户物理值缺失”。两个真实adapter绑定/运行oracle/Golden与lease释放验证是随后实施集成门，不撤销既有Core-A/B/C/D接收。若以后需仿射全域Jacobian等其它证据，继续复用本Owner已存在数值路线并另按实际门接收，不把本分母输出假称提供全部用途资格。

#### 4.4.5 固定正常/反例、Test与两轮有限自审

CG-Core-E继续使用binding唯一Core工程与BCL Exe测试工程，不创建另一个测试包。新增必需组`CGT-DENOMAIN`加入§13.1 `--suite core-all`（新增切片实施后不可skip；既有A/B/C/D接收不代表E实现通过）；自定义TimeProvider/预算/Profile沿既有2s运算和10s case/120s run/180s外进程截止，无真实库/设备。正常E软件Limits固定MaxRuns=128、MaxBytes=4MiB、MaxMantissaBits=65536、MaxExactSteps=1000000，边界组显式缩小一项计步骤/封存拒绝；deadline用同clock受控推进，不用sleep猜竞态。所有mask/frame/map/hash测试引用来自固定合成快照，不赋客户公差。

E专属BenchmarkProfile沿§14.2统计入口，另固定runs数量/长度、组件间隔、Frame域vertices/holes、系数指数/有效位长、输出四角witness数量、逻辑ChargedBytes/ExactSteps峰值、实际托管分配、并发、Complete/partial与各中断原因。测点为输入封存/hash、全源域验证、逐片exact乘加/界、聚合/证据构造、scratch释放及Evaluate真实返回；CheckEvidence单独测量并记录是否共享原operation剩余截止。宿主copy/acquire/ROI DisposeAsync计入桥端到端，与纯Core时间分别记录；不把同步返回或逻辑字节计账当ROI释放/private bytes下降。无消费者已采纳目标只做诊断并标NotEvaluated，不造吞吐或物理达标值。

| case | 输入（中心矩阵系数为实际binary64；显式frame域覆盖整片） | 必须预期/证据 |
|---|---|---|
| CGE-01 正常 | identity PixelToSource；run=(0,0,0)，H=identity，threshold=1 | 四角(-.5,-.5),(.5,-.5),(.5,.5),(-.5,.5)，sourcexy相同，w全1；min=max=1、Complete=true/通过，相等门允许 |
| CGE-02 中心盲区 | 同域/映射，H末行=(1,0,.25) | 中心w=.25仍片w∈[-.25,.75]，四角两负两正、ContainsZero，MinAbs=0、MaxAbs=.75、ThresholdPassed=false；不是中心点成功 |
| CGE-03 有孔/异号 | 同row两run=(0,0,0)/(0,4,4)，H末行=(1,0,-2)，threshold=.5 | 片界[-2.5,-1.5]/[1.5,2.5]；两片各自不跨0、MinAbs=1.5/MaxAbs=2.5，通过；不填孔/不对总MinW/MaxW跨0误拒 |
| CGE-04 门边binary64 | run=(0,0,0)，H末行=(2.25,0,1.375)，threshold为binary64 .1，再用精确-2H | w界[.25,2.5]，数学ratio=1/10但binary64 .1大于1/10，exact门false；-2H尺度相反同拒识，显示.1不放行 |
| CGE-05 精确affine/单位 | run=(2,1,2)，map=[[2,1,3],[0,3,-1],[0,0,1]]，Pixel→毫米，H末行=(1,2,4)，threshold=.2 | pixelxy四角(.5,-2.5),(2.5,-2.5),(2.5,-1.5),(.5,-1.5)；sourcexy=(1.5,-8.5),(5.5,-8.5),(6.5,-5.5),(2.5,-5.5) mm；w=-11.5,-7.5,-.5,-4.5，MinAbs=.5、MaxAbs=11.5、false；不重复单位比例 |
| CGE-06 精确零边 | 单run，H末行=(1,0,.5)（全H nonsingular） | w界[0,1]，即使仅闭边touch0也ContainsZero/false；Open域不能当ClosedPixelCells略过触边 |
| CGE-07 输入/退化 | default/空runs、乱序/重叠/越界、map末行非(0,0,1)/奇异、H singular/NaN/Inf、错FrameRef/revision/Unit/SourceBinding；把row-down Ref重标Cartesian、mapped片包含域洞 | 明确InvalidInput/CG001/002/003/004/005/018、Evidence=null；显式独立chart+反转affine可受新端口接收，同chart不能直接交旧服务Pixel校验；ROI Owner绑定不满足不得调用洗白 |
| CGE-08 完整性/篡改 | CGE-03漏第二run、duplicate index、换旧H/map/domain/policy/threshold、修改corner sx/w或min/max/sign、非canonical dyadic | CheckEvidence(expected完整input,evidence) Inconsistent；只数count不够，witness/extrema数值复核由Owner；原inputdigest覆盖rawbits，H的-0改+0数学可相同但身份不同 |
| CGE-09 budget/取消/截止 | 完成第0片后下一primitive耗尽/取消/推进到deadline；全源域预验证中断；封存/最小header字节不足 | w循环中断仅保留已完整第0片，全域预验证中断最多零片prefix；Expected=原总数、Complete=false、聚合三项null；无header额度Evidence=null，固定拒绝回执壳仍返回且ChargedBytes≤MaxBytes；返回时scratch无继续使用/池借用，GC/private bytes不保证归零，ROI lease由adapter另Drain |
| CGE-10 区分两门 | identity H、source x=10⁶（显式affine），threshold=1；§4.4反向例 | 本门过但旧norm安全门可拒；反向例本门拒旧门可过，adapter不能交换threshold/意义 |
| CGE-11 来源/Replay | 相同全部输入在两个独立evaluator、不同CalculationId；改domain/frame/map/threshold或方法Revision | 同内容InputDigest/数值证据一致，request IDs各自回显；改绑定/方法拒旧证据，SourceBinding完整性仍由ROI Owner |
| CGE-12 native/API隔离 | 两宿主分别调用factory；consumer DTO缺witness字段；ROI Dispose待确认 | 独立Core无Alignment/ROI/HALCON/WPF引用、输入值不变；原证据witness另保留；evaluator结束不冒ROI已归还，不提交质量事实 |

自审第一轮（数学/域）：按CGE-01–06/10逐项exact手算四角/范围/孔/异号、门边binary64与affine单位；全域成立依据是每个完整run凸片线性极值，不采样、不以外接框补孔。第二轮（消费/异常）：按CGE-07–09/11–12检查literal引用、来源完整性、bit级identity、预算中断prefix与null聚合、同clock截止、同步scratch/ROI lease分离、原证据保留和CheckEvidence职责。仅两轮有限定向自审；此处断言是规格，实际BCL/数值oracle/两个真实宿主运行尚未执行。

## 5. 图、路径、组合与逆的固定算法

1. 校验帧/边引用唯一、hash、维度/单位/轴、域、模型、逆策略；同 Ref 不同内容为 CG002，重复相同项也拒绝结构重复，不按加载顺序覆盖。边端点必须存在，不能自环替代显式 identity。未知同帧请求拒绝。图结构校验不加载未选中的外部模型：ValidateGraph仅证明结构/参数声明一致，并列出未绑定的能力诊断，不声称整个图可在当前backend执行；Map只对实际路径检查backend/模型端口及资产可用性。
2. 可逆 affine/projective 仅在 Analytic 且模型可逆、量纲归一稳定、InverseValidDomain明确时构造逆遍历；逆向先检查此域，再变换并检查原ValidDomain，不能把正向source域原样当逆source域。ProvidedInverse 必须同快照存在、方向/域相容；矩阵模型验证组合等价identity，外部模型双向闭环仅使用§9资产提供的见证集/唯一性证据。正向可算不等于逆向有资格。平面 lift、相机投影和局部场不自动求逆。
3. Explicit 严格按 EdgeStep 连接起止 Ref，重复帧/循环路径拒绝（identity为空路径除外）；不会暗中用其它路径修复。逐边有效域即时检查，保留所有中间约定。单矩阵只在同维度可组合模型上作为执行优化；不能合并相机/局部场后丢域检查。
4. ResolveUnique 用按 EdgeRef ordinal 排序邻接表的有界 DFS，枚举不重复帧的简单路径；候选按图结构/声明模型/方向定义，不按当前输入域、残差、backend可用性或质量排名删边。MaxPathDepth、MaxPathCandidates、MaxGraphVisits 及 ExecutionBudget 同时限制。找到两条即 CG016PathConflict；完整搜索未找到为 CG015MissingPath；任何分支触及深度/访问/候选预算而尚不能完成判定为 CG007，**不能将未搜完误报无路径或唯一**。唯一路径实际执行时端口不支持返回CG017，资产不可用CG018，不改用别路。循环图本身可登记，路径不带循环，图诊断标出环；不穷举无限 walk。
5. CheckConsistency 在同样有界枚举完成后，对调用方明确的 probes/共同域比较候选路径目标结果，差异用目标单位欧氏范数，与有来源的 tolerance 比较。probe 缺失、越域或能力不匹配拒绝，不由模块自动猜样点。全部探针通过仅表示该见证集一致，不证明连续全域等价；按 EdgeRef 序列字典序选第一条并保留全部比较证据。未完整枚举、超差或无法比较拒绝。物理全域资格须外部 Owner 提供证据。
6. 实际几何沿固定路径映射：输入全部预检 → 中间域 → 数值模型 → 目标域 → 全几何有效性 → 误差传播。先完成全请求可判定预检，再按项索引串行处理，每项沿完整路径执行；并行向量化只有在保留相同错误优先级/路径/原索引时才可优化，不让“先报错的线程”决定失败索引。任何项失败全批无结果，仅报告输入顺序首个错误（及有界诊断），不支持部分成功。空 Items 仍验证图/路径/策略，不调用 native 点运算，返回 Completed 空集合，不能证明域内任何物理点成功。

空Items没有输出随机变量，Required误差不因NoCovariance拒绝；输出为空Batch/NoCovariance、Uncertainty=NotProvided并诊断EmptyNoUncertaintyTarget。若请求携带非空协方差则与零维输入结构不匹配CG001。GraphValidatedWork同样没有几何传播目标，Required不作物理误差资格判断；两种空目标分支不例外跳过graph/model声明/Policy验证。
7. 只有全部项、误差要求和资源归还成立才 Completed。禁止找“残差更好”的路径、静默选 latest、伪逆、正则化、单位阵和自动变模型。

## 6. 唯一错误与恢复表

枚举代码/英文标识供分支判断；MessageKey 三语显示。字段错误优先顺序：envelope/配额 → 图身份 → 单位/维度 → 路径 → 模型 → 输入原索引域/数值 → 执行 → 不确定度。取消/到期若先线性化则覆盖尚未提交的成功，已终态不改；两者同一检查点先读用户取消，再读期限，原因一次固定。

| 代码 | 标识/含义 | 允许恢复 |
|---|---|---|
| CG001 | InvalidArgument：结构、非有限、枚举、域定义或无效期限 | 修正输入、新 RequestId |
| CG002 | RevisionMismatch：Ref/hash/契约版本不匹配 | 绑定明确修订，不选 latest |
| CG003 | UnitOrDimensionMismatch：单位/维度/轴声明不兼容 | 明确换单位/换基/深度边 |
| CG004 | DomainViolation：域外或边界/连续域无法可靠证明 | 补支持域或换合法几何；不夹紧 |
| CG005 | InvalidTransform：奇异、条件数/正交/分母安全不满足 | 更正变换/数值策略；不伪逆 |
| CG006 | PolicyRequired：执行数值策略缺失或字段无效 | 提供显式软件数值策略；不是客户验收门 |
| CG007 | ResourceLimit：图遍历/字节/点/并发/保留/工作区超限 | 新请求缩小输入/合法预算；不悄悄拆批改变结果语义 |
| CG008 | Cancelled：用户或 ServiceStop 已停止且排空释放 | 查询原回执；再次运算使用新 ID |
| CG009 | DeadlineExceeded：运算期限触发且已排空释放 | 保留原回执，不盲重试 |
| CG010 | ExecutionFailed：托管/native/模型端口确定执行异常 | 保存安全诊断，修复后新 ID；不静默换后端 |
| CG011 | LookupUnavailable：查询/观察源无法判断 | Unknown；继续查询原实例，不猜 NotFound |
| CG012 | ServiceStopped：停止接纳 | 完成旧实例 Drain 后显式新 epoch |
| CG013 | DrainUnconfirmed：等待期限内无法确认排空 | 保留服务与资源，继续查/等，不重用句柄 |
| CG014 | RequestConflict：重复 ID 不同快照 | 原请求不变，新 ID 提交修正值 |
| CG015 | MissingPath：有界搜索完整结束且确无路径 | Owner 提供新图修订 |
| CG016 | PathConflict：多路径/探针差异未消歧 | 提供显式路径或新图；UI 不能质量放行 |
| CG017 | UnsupportedModel：该 backend/端口无声明模型 | 拒绝该切片；不补同名平行算法 |
| CG018 | AssetUnavailable：外部模型/证据快照不可用/不匹配 | 绑定准确资产，无关 Core 可继续 |
| CG019 | UnsupportedGeometry：维度/模型不支持所需表示 | 调用方显式选支持表示/请求；不自动采样伪成功 |
| CG020 | UncertaintyUnavailable：Required 但联合协方差/导数/有效域不足 | 补证；Optional 只给 NotEvaluated 摘要 |

OperationSnapshot 的 Error 仅失败时存在；Completed 无错误但可有诊断（如不确定度缺失）。未知是观察状态，不在终态枚举；失败/取消/到期不返回可消费几何或迟到 native 数值。

## 7. 并发、取消、等待、事件和真实排空

### 7.1 状态与线性化

操作状态闭集：`Accepted → Validating → [Executing] → Draining → Drained → ResourcesReleased → {Completed,Rejected,Cancelled,TimedOut,Failed}`。短拒绝没有操作状态事件；接纳后验证拒绝也经过完整释放。Drain Unknown 时 State 保持 Draining、Drain=Unknown，不发布 Drained/ResourcesReleased/终态。Query 可 Found+Draining/Unknown（操作明确存在，仅排空不明）；查询源自身不确定才 Lookup Unknown，不能混成 NotFound。

接纳、重复判定、终态提交、取消原因与服务停止各有一个线性化点。单请求一个执行 Owner、一个唯一终态。无内置等待队列；超并发/配额即时拒绝。服务限额在构造时固定，不能被多个不同 Profile 相互覆盖。各请求图/策略/缓冲隔离；缓存只读，以完整图/模型/后端/策略版本键隔离，并计入限额。

ExecutionBudget 从 Accepted 的单调时钟起算，涵盖验证/路径/native 派发；到期停止新工作但不是“本机已停止”。在每项/每边/每个有界遍历步骤及 native 调用前后检查取消/期限；提交成功前在同一锁/原子提交点再检查一次。不能用 wall clock 或强杀线程保证 deadline。

SubmitAsync 的 admissionToken 只管接纳前操作；返回 Accepted 后显式 CancelAsync 取消计算。WaitAsync 的 waitBudget/waitToken 只结束该观察者，分别返回 WaitExpired/WaitCancelled，不修改原计算。Wait/Stop的waitBudget必须有限正值；Query/Cancel只访问有界本地记录及短原子状态，不另设不存在的waitBudget参数、不执行计算/外部IO；Query 的 token 在访问前取消可抛 OperationCanceledException，不改状态。CancelAsync 的 commandToken 在取消线性化点前取消则不提交命令；提交后返回原请求快照，即使结果读取被打断也不能撤销命令。重复取消幂等；不存在返回 NotFound，不创建记录。

Wait在原实例确定无RequestId时Observation=NotFound、Lookup=NotFound，立即返回；观察源故障则Observation=Unknown、Lookup=Unknown/CG011。WaitExpired/WaitCancelled都附最后可确认Lookup（可以Found+Draining/Drain Unknown），不伪装操作终态。Observe对不存在ID在首次MoveNext抛KeyNotFoundException，不隐式接纳；afterSequence大于当前Sequence拒绝ArgumentOutOfRangeException，避免无限等未来序号；相等时等新事件，终态且afterSequence等于终态序号则正常结束。Observe source故障抛IOException并由宿主Query对账，不吞掉成空成功；observer取消只结束本订阅。

### 7.2 Drain 与资源

取消/到期/Stop：记录一次原因 → 不派发新计算 → 等当前托管/native/外部端口真的退出 → 归还操作持有租约/临时对象 → Drained → ResourcesReleased → 终态。临时对象的 Dispose 必须实际完成；失败则 Drain Unknown 并保留隔离记录。纯托管 Core 不伪造 native 句柄/worker；其停止在有界循环协作检查后可确认，外部适配器则必须报告真实归还。

StopAndDrainAsync 首次调用原子转 Service Draining，停止接纳，对所有活动请求发 ServiceStop 取消；waitBudget 到期/等待 token 取消只结束 Stop 的等待，不撤销服务停止或已发取消。返回 Draining+Unknown+CG013，保留活动数/资源。再次 Stop 继续等同一批；全部操作归还则 Stopped+Confirmed+0。Stop 不能卸载仍运行的适配器，窗口关闭不能销毁服务或替宿主执行 Stop。

### 7.3 事件与查询

每个已接纳操作 Sequence 从1严格递增。Lifecycle 在权威记录内可靠保留，终态一次，ObserveAsync 从 afterSequence 重放并持续订阅，订阅晚于终态也能取得终态；事件集合受保留配额限制，终态后无新事件。Progress 仅 Executing，可合并/丢弃，序号允许有间隙，不能承担释放/终态证据。慢观察者不能阻塞计算：不在计算线程调用任意用户回调；生命周期从回执存储读取，进度用有界缓冲。若订阅源不可用，Observe 返回错误，调用方 Query；不得伪装观察成功。

观察 token 只取消订阅；不同观察者不互相取消。Core 不捕获 UI SynchronizationContext，不保证回调在 Dispatcher；Wpf Adapter 负责投递投影。终态和结果以 Query/Wait 的不可变权威快照为准。ServiceInstanceId+RequestId 共同定位，旧 epoch 的未知不能在新实例下被 NotFound 覆盖。

## 8. HALCON 26.05 / AsunImage 视觉路线

算子语义依据项目内 [HALCON 26.05 operators](../../../halcon算子手册/operators/)。AsunImage 是薄封装，以下算子均经 `ImageLibDotNet.cv2` 使用；不检查是否“包含算子”、不扫描内部、不另接 HALCON 程序集。只有实际 C# 参数类型/重载/封送不明才查看公开签名或消费端编译。这里记录已读官方页面的语义，不写未经确认的 C# 大小写/重载调用。Core 纯数学不是图像算法；Halcon backend 不因 native 异常静默切回 ManagedCore，后端变更必须新请求及版本证据。

### 8.1 换轴与半像素链（唯一公式）

令 `p=(u,v,1)` 为 column/row 中心坐标，`q=S*p` 为 row/column 中心坐标：

```text
S = [[0,1,0],[1,0,0],[0,0,1]]
C = [[1,0,0.5],[0,1,0.5],[0,0,1]]
Hrc = S * Huv * S
Hcorner = C * Hrc * inverse(C)
```

普通点路线 `affine_trans_point_2d`：参数 Px=row、Py=column，传 Hrc；corner/pixel/XLD 路线使用 Hcorner。`affine_trans_pixel` 对输入中心先 +0.5，映射后 -0.5，因此 `q'=C^-1*Hcorner*C*q=Hrc*q`。`affine_trans_contour_xld` 同样使用 row=x、column=y 与角点约定，不能把中心旋转矩阵直接传入。已有 native 矩阵必须带其 Center/Corner 和 RowColumn 元数据，先还原到 Huv；禁止重复补偿。

可手算反例：中心缩放2，`(u,v)=(2,3)` 应到 `(4,6)`。Hcorner 的两个平移为 -0.5；把 Hrc 直接传 `affine_trans_pixel` 得 `(4.5,6.5)`，这是错误，不是“容差内差异”。中心原点旋转90° `(u,v)→(-v,u)`，`(2,3)→(-3,2)`；Hcorner 仍须按完整换基推导，不能只交换平移。

crop 起点 `(x0,y0)=(100,20)` 为局部到父帧平移，局部 `(0,0)`→父 `(100,20)`。resize 必须消费图像模块记录的实际重采样坐标关系、尺寸、域/裁切及算子参数；按 extent 锚定的中心公式通常 `p'=s*(p+0.5)-0.5`，s=2 时 p=0→0.5，而中心原点数学缩放p=0→0。二者不能混用；未知实际 resize 关系为 CG018，不一律乘比例。图像插值、灰度、image domain、负坐标裁切属于图像/拼接模块，坐标模块不执行图像重采样。

### 8.2 逐能力算子及限制

| 视觉能力 | 固定算子/参数语义 | 前置、失败与替代 |
|---|---|---|
| 2D affine 点/像素/XLD 桥 | [affine_trans_point_2d](../../../halcon算子手册/operators/affine_trans_point_2d.html)、[affine_trans_pixel](../../../halcon算子手册/operators/affine_trans_pixel.html)、[affine_trans_contour_xld](../../../halcon算子手册/operators/affine_trans_contour_xld.html)；按 §8.1 换基 | 点路线和pixel路线同夹具对账；XLD仅适配器临时对象，不进领域值；异常 CG010，无默认单位阵 |
| 2D 组合/逆 | [hom_mat2d_compose](../../../halcon算子手册/operators/hom_mat2d_compose.html)、[hom_mat2d_invert](../../../halcon算子手册/operators/hom_mat2d_invert.html)；列向量顺序不因 native row-major 改变 | six-value `[ra,rb,tc,rd,re,tf]` 与九元形状显式转换；逆前 §3稳定性检查，native 成功不等于稳定 |
| 2D projective | [projective_trans_point_2d](../../../halcon算子手册/operators/projective_trans_point_2d.html) 返回 Qx,Qy,Qw，显式除Qw；[projective_trans_pixel](../../../halcon算子手册/operators/projective_trans_pixel.html)按corner | 点/像素各用对应换基；分母/域先后检查，W=0拒绝，不返回大数代替无限点 |
| 3D affine/逆 | [affine_trans_point_3d](../../../halcon算子手册/operators/affine_trans_point_3d.html)、[hom_mat3d_invert](../../../halcon算子手册/operators/hom_mat3d_invert.html) | native row-major十二元与完整十六元明确转换，XYZ/单位/手性不猜；法向仍按逆转置，不调用点算子加平移 |
| Pixel→世界平面 | [image_points_to_world_plane](../../../halcon算子手册/operators/image_points_to_world_plane.html)；WorldPose为 **camera←world**，只求 world z=0 | 资产须含相机参数、world frame、pose方向、原标定单位和图像支持域；Scale按目标/原单位比例。未知尺度/离面/平行或不支持相机模型拒绝；没有通用3D输出 |
| World/Camera→Pixel | [project_3d_point](../../../halcon算子手册/operators/project_3d_point.html) 输入已在 camera frame 的XYZ、输出Row/Column | 世界点先显式外参至camera；相机模型/可见深度/有效图像域均来自资产，透视前方Z条件不能照搬所有相机类型；不猜不同模型的遮挡/可见性 |
| 畸变桥 | [change_radial_distortion_points](../../../halcon算子手册/operators/change_radial_distortion_points.html)，原cam→目标cam参数均固定 | **不支持透视镜头线扫相机**；禁止以全局缩放近似径向畸变；校正与原图frame分开，图像校正不产生计量资格 |

矩阵/点等算子文档声明 reentrant/global，部分点变换内部并行；compose/invert/world-plane/畸变等不能默认自动并行。线程安全不等于可硬取消。适配器一请求一临时资源集合，批处理粒度受请求预算限制，native 前后检查取消；运行中的算子等待真实返回与对象释放。HALCON route 不引入拟合 `vector_to_*`、Kabsch或自制相机备用算法；拟合由 Alignment/标定 Owner 输出版本化边。

多条视觉候选对照仅比较合法点与pixel桥、相同快照/同样本、同坐标表示；记录正确性、拒识、P50/P95/P99与峰值资源。此轮没有运行对照，不把官方线程说明当作本机性能证据。

### 8.3 Halcon后端自有公开装配（Assembly 1，指导冻结、未实施）

原§4.3已有`IGeometryBackend`、Map/Drain和`CoordinateGeometryFactory.CreateWithBackend`，§8.1–2已有算子路线；缺的是供外部Host构造该backend的本模块入口。本节仅补装配，不修改Core接口或另写算法。唯一落点为binding中`.Halcon`，net10.0，引用本Core、既有AsunImage及[calibration-assets Core/CameraRead](../calibration-assets/DEVELOPMENT-GUIDE.md#93-已解相机参数公开读取增量camera-read-api-1)公开值；不引用其solver/Writer/Wpf或上游内部。

```csharp
using System;
using System.Collections.Immutable;
using Asun.Modules.CoordinateGeometry;
using Cal = Asun.Modules.CalibrationAssets;
using Read = Asun.Modules.CalibrationAssets.CameraRead;
namespace Asun.Modules.CoordinateGeometry.Halcon;
public enum CameraRoute { PixelToWorldPlane=0, CameraToPixel=1,
    WorldToPixel=2, DistortionPoints=3 }
public sealed record CameraUseEvidence(Cal.IntendedUse Use, AssetRef EvidenceRef,
    AssetRef PoseRef, AssetRef? WorkPlaneRef, Cal.AuthorityWatermark Watermark,
    Cal.OperatingDomain ApprovedConditions, Domain VisibleCameraDomain,
    DateTimeOffset ValidFrom, DateTimeOffset? ValidTo,
    DateTimeOffset ExposureFrom, DateTimeOffset ExposureTo);
public sealed record CameraBinding(AssetRef ModelRef, CameraRoute Route,
    Read.CameraReadRequest ReadRequest, Read.CameraParametersSnapshot Camera,
    Read.CameraReadRequest? TargetReadRequest, Read.CameraParametersSnapshot? TargetCamera,
    Frame PixelFrame, Frame CameraFrame, Frame? WorldFrame, Frame? PlaneFrame,
    Frame? TargetPixelFrame, Matrix? CameraFromWorld, CameraUseEvidence UseEvidence);
public sealed record HalconBackendLimits(int MaxInvocations, int MaxPointsPerInvocation,
    long MaxSnapshotBytes, long MaxWorkingBytes, int MaxNativeCallsPerInvocation);
public sealed record HalconBackendOptions(string ContractVersion, AssetRef BackendRevision,
    ImmutableArray<string> CapabilityIds, ImmutableArray<CameraBinding> Cameras,
    HalconBackendLimits Limits);
public interface IHalconGeometryBackendFactory
{
    IGeometryBackend Create(HalconBackendOptions options, TimeProvider clock);
}
```

公开实现`HalconGeometryBackendFactory : IHalconGeometryBackendFactory`，public无参构造，`Create(options,clock)`按上述签名返回内部backend；准确装配为`backend=new HalconGeometryBackendFactory().Create(options,clock)`→`service=new CoordinateGeometryFactory().CreateWithBackend(runtimeLimits,clock,backend)`。Create只有限预检/深拷贝和建账本：无cv2调用、相机解参、文件/资格IO、线程/Dispatcher/窗口/句柄。null抛ArgumentNullException，shape/引用/能力/限额不合法抛ArgumentException并命名字段；任何失败均无native工作。ContractVersion=`cg-halcon-assembly-1`，BackendRevision为真实发布包引用，不用本轮杜撰hash。整数/bytes正，MaxInvocations≤1000000、MaxPoints≤10000000、MaxNativeCalls≤1000000；关系和snapshot逻辑字节按§4.2编码宽度有界核算，完整CAL快照/ReadRequest另按CAL既有codec规则核算，不重算CAL原件身份；复制前检查字符串/集合上限。Capabilities固定为`new BackendCapabilities(options.BackendRevision,options.CapabilityIds)`的不可变副本；采用§4.3既有名称中本节明确实现的七项，拒重复/未知/LocalFieldPoints（其既有外部路径不在本Halcon装配实现）；不因Cameras非空隐式开启camera能力。无camera时空数组合法，可独立运行点/像素桥。

Backend只执行§8.2已选路线：Affine2Points/Affine3Points/Projective2Points/PixelBridge按原模型和单位/半像素规则；camera ExternalModel的ModelRef必须逐字段命中此实例冻结binding，`PlaneToWorld`只匹配PixelToWorldPlane，`CameraProjection`匹配CameraToPixel/WorldToPixel，`DistortionPoints`匹配DistortionPoints，源/目标帧及方向必须逐字段相等。纯矩阵组合/域/曲线/法向/不确定度继续由已接收Core决定，不搬入backend。不支持的geometry为CG019，不支持的能力/模型为CG017；不能以点抽样提供连续曲线/全域相机证明。相机路线本轮只交付已定义ordered Point2/Point3点值，未提供已冻结BackendDerivatives时Optional按原规则NotEvaluated，Required CG020；不数值扰动猜Jacobian。支持模型按CAL §7.2C精确参数和§8.2对应算子适用性核验，未知或算子不支持的组合显式拒绝，不另选视觉路线。

Map调用前原子占本backend的Invocation槽、全部最坏scratch/native-call及迟到清理额度，ID保存完整BackendInvocation；超限CG007、零native副作用。同InvocationId同完整输入只观察原调用，不重算；不同内容CG014。每个原ValueTask仅消费一次，需跟踪时只AsTask一次，保留该Task，观察Task不替换它。批处理不能重置RemainingBudget：入Map按注入clock形成单调截止，每批/每native前后及值封存前检查剩余期限/token；越时只停止后续派发。每次临时tuple/对象在成功/异常/取消的同一Owner finally中实际Dispose，归还失败或native未返回保持Drain Unknown/CG013和原调用/资源，不能向Core签Completed或释放槽。原业务异常CG010与cleanup异常分别保留，不用后者覆盖前者。DrainAsync只有限等/查询原Invocation，不执行新Map，不用Task.WhenAny早返回假Confirmed；Confirmed须原Map/native/cleanup退出且ActiveLeaseCount=0，返回的不可变值由Core持有。已完成的有界墓碑保留至宿主服务epoch退役，满MaxInvocations拒绝新调用；不自动覆盖旧ID，不保留native缓存。本backend无长期native对象/Dispose入口，只有服务Stopped+所有原调用Confirmed后Host才能退役其托管引用。

MaxSnapshotBytes同时限制冻结Cameras/options、所有保留Invocation输入/托管结果/墓碑及重复返回引用，不只构造时静态快照；MaxWorkingBytes限制本实例并发总scratch，新旧输出/临时并存计峰值，native-call次数逐调用累计。Map预检RemainingBudget有限正值、原ID/Graph/Step/Input及源目标联合，失效/不支持在native前明确返回Error/Output=null。本装配camera边的源→目标固定为PixelFrame→PlaneFrame、CameraFrame→PixelFrame、WorldFrame→PixelFrame或PixelFrame→TargetPixelFrame；逆向相机能力未由本节声明，拒绝而不靠Core det/ProvidedInverse或临时反pose开通。Closed/Open域判断复用原点域规则；不把遥测有效域扩大为物理资格。Dispose结果未知时不重复归还/伪造零handle，Drain仅观察已登记cleanup并保留Owner，不能另起无界Dispose循环。

### 8.4 矩阵及相机调用顺序、参数封送与输出校验

本节只落实§8.1–3路线的参数顺序，复用26.05原算子，不新增视觉求解或备用算法。读入已封存Graph/Edge/Frame→原Core预检域/数值策略/已选Step→按能力准备有界tuple→调用→按原索引恢复Core值→目标域/有限性检查→原Owner归还→原Map回执。各路线选择由CapabilityId、Frame语义及CameraRoute确定，不在执行中择优试算。

| 已选路线 | native调用的精确控制参数顺序/转换 | 输出处理与选择理由 |
|---|---|---|
| Affine2Points | 普通Cartesian使用原3×3矩阵前两行六元`[a11,a12,tx,a21,a22,ty]`，`affine_trans_point_2d(H,x[],y[])`；ImageColumnRow/Center按§8.1先生成Hrc，输入`Px=row[],Py=column[]` | 回Qx/Qy后按原轴序写Point2；图像路线交换回column/row；此路线无半像素补偿 |
| PixelBridge | 仅ImageColumnRow/Center二维Point2，生成Hcorner后`affine_trans_pixel(Hcorner六元,row[],column[])`；Projective时用完整九元`projective_trans_pixel(Hcorner,row[],column[])` | 返回RowTrans/ColTrans后恢复(column,row)；HALCON内部中心/角点转换只执行一次；Cartesian调用PixelBridge拒CG003 |
| Projective2Points | 原H九元；图像帧用Hrc与row/column，普通Cartesian用x/y；`projective_trans_point_2d(H,Px[],Py[],Pw[])`，Pw逐点为1 | 返回Qx/Qy/Qw；逐值有限、Qw与原Core安全门有效后除Qw。Pixel算子已经除w，不能再除；结果数目必须等输入数目 |
| Affine3Points | 从原4×4取**前3行完整十二元**`[m11,m12,m13,tx,m21,m22,m23,ty,m31,m32,m33,tz]`；`affine_trans_point_3d(H12,x[],y[],z[])` | native十二元顺序与§4.3.2的ParameterOrder顺序不同；末行只在Core为(0,0,0,1)，不得传九项线性块代替十二元；输出XYZ不再按Unit缩放 |
| 已选矩阵compose/invert的桥对账 | `hom_mat2d_compose(T_C_B六元,T_B_A六元)`；`hom_mat2d_invert(H6)`/`hom_mat3d_invert(H12)`；inverse输出补固定末行 | Core仍是路径/稳定逆的权威，不让native另选路径或绕数值门；这些算子用于明确的桥转换/对账，不给External模型临时求逆 |
| PixelToWorldPlane | 原相机tuple：模型原Name作为首项，随后CAL已解参数表原顺序/单位；已核camera←world米矩阵前3行十二元→`hom_mat3d_to_pose(H12)`→type0 pose→`image_points_to_world_plane(camTuple,pose,row[],column[],"m"/"mm"/"um")` | 回X/Y为指定plane单位Point2，只能是该world z=0；§9.2.1要求的域/用途仍必检。nm走独立已发布米→nm边，不造第三返回Z |
| CameraToPixel / WorldToPixel | 输入按CameraFrame.Unit**一次转米**；WorldToPixel先按已批准camera←world将原世界米点映到camera米。`project_3d_point(X[],Y[],Z[],camTuple)` | 回Row/Column→Point2(Column,Row)；调用前核VisibleCameraDomain、调用后核原Pixel域。无需pose的CameraToPixel不构造虚拟world frame |
| DistortionPoints | `change_radial_distortion_points(row[],column[],camTupleIn,camTupleOut)`；两个完整CAL快照严格原序 | 回RowChanged/ColChanged→目标pixel帧；透视线扫拒绝。不是image重采样，也不把输出重新标为原图 |

XLD桥仅处理已由ROI/宿主显式提供的合法临时XLD对象：生成Hcorner→`affine_trans_contour_xld(Contour,HomMat2D)`→读取原索引顶点→归还临时ContourTrans。§8.3的Core GeometryBatch公开入口没有HObject/XLD，不能让开发者向其加裸句柄；其Point/Segment/Polyline值路线按Core既有算法。原XLD所有权、轮廓创建和结果codec归ROI/宿主，本文的XLD说明是坐标约定接入，不新增坐标模块图像对象API。

Camera参数模型字符串/数值类型沿CAL CameraSolutionCodec；width/height为合法整数值，其余有限double，不拿InitialParameters或修改Sx/Sy/Cx/Cy补crop。所有输出tuple长度按输入项checked核对，空批不调native；未知相机模型/算子不支持组合在调用前CG017，错单位CG003、用途/快照缺失CG018、源目标域CG004、native确定异常CG010；cleanup未确认仍CG013/Unknown。C#公开重载/封送在后续消费编译验证，**算子顺序、值shape、方向和资源Owner在本文已决定**，不扫描AsunImage内部。

## 9. 外部模型与宿主端口值协议

下面是本模块接入端口的语义定义；公开装配为§4.3、§8.3、§9.1.1和§11.4。camera按§9.2.1消费既有上游公开值，localfield由本模块自己的冻结值承接Host已持有的网格，不把未见外部API留给程序员猜测。端口可无 UI 实现，不通过隐藏窗口装配。

| 端口 | 输入→输出 | 所有权、取消与接收门 |
|---|---|---|
| 模型读取 | `(modelRef,capabilityId)`→不可变 ModelSnapshot 或 CG018 | 宿主在请求接纳前封存；执行中不读 latest/网络/数据库；失败不影响纯 Core |
| 模型映射 | ModelSnapshot + 源/目标Ref + ordered points + Deadline→ModelMapValues | 值结果含原索引、域验证、Jacobian可选、版本/模型hash；不得返回 native 句柄或质量决定；不完整结果全批拒绝 |
| 模型排空 | ModelInvocationId + waitBudget→Pending/Confirmed/Unknown 与 ActiveLeaseCount | InvocationId 在执行前登记；取消不保证停止；Confirmed必须同时完成所有租约释放。无此保证的适配器不可准入 |
| Inspector宿主输入 | 图/结果快照、视口只读投影、主题、Culture、权限投影 | 控件只保留值引用和订阅；Close解绑，不 Stop服务/Dispose宿主视口 |
| 草稿请求（可选） | 基线GraphRef + DraftChanges + HostCommandId→宿主保存回执 | 缺宿主明确草稿能力即无编辑命令；模块不激活/写生产资产，保存失败保留草稿供宿主恢复 |

### 9.1 局部场/非刚性消费

ModelSnapshot 必含：Ref、源/目标帧、GridOrigin、Spacing（每轴正且源单位）、Nx/Ny、NodeValues（目标位置或目标位移二选一标签）、CellValidity、Interpolation=Bilinear、适用域、方向、Jacobian证据、逆能力、来源。节点数/洞/网格范围须与数组一致且受 MaxInputBytes；不推断数组方向或零值代表缺失。

单点：确定有效cell → 计算归一权重 tx/ty∈[0,1] → 四节点双线性插值 → 若位移模型加源位置（源目标单位不同时须先有明确单位/基准变换）→ 解析局部Jacobian → 检查目标域。grid线采用左/下闭右/上开cell归属，最外有效边归最后cell；无cell/洞/超界拒绝，不用最近节点外推。cell边界导数不唯一时不传播法向/协方差，返回CG019或Optional NotEvaluated，不平均两侧导数。

逆只有资产显式提供已验证逆场或保证唯一根及域的求逆能力时开放。单cell det不为0、全部 det同号、正向probe成功均不证明全局单射；存在多根/折叠/越域/未证明唯一性即拒绝。模块不临时牛顿搜索、训练补洞或自动改网格。连续线/圆/多边形不得仅采样后宣称精确映射；调用方显式提交有限点集时结果只覆盖这些点，消费者自有的曲线近似/公差不迁入本模块。

#### 9.1.1 LocalFieldV1冻结值与无UI构造

这是已规划ExternalModel/Bilinear点场的消费装配，落在本Core工程的`LocalFieldV1/`，不新拆DLL，不拟合图像、求场或自动求逆。消费者为ROI有限顶点诊断与无UI计量锚点/局部误差；连续曲线/填充ROI资格仍拒绝而非采样认证。纯数学插值复用§3.6/3.8的精确有理与dual底座；不另造视觉配准。没有可替代网格消费语义的图像重采样路线：图像灰度/插值归预处理/拼接，HALCON矩阵/相机路线仍§8。

```csharp
using System;
using System.Collections.Immutable;
using Asun.Modules.CoordinateGeometry;
namespace Asun.Modules.CoordinateGeometry.LocalFieldV1;
public enum NodeMeaning { TargetPosition=0, TargetDisplacement=1 }
public sealed record LocalFieldSnapshot(AssetRef Ref, Frame Source, Frame Target,
    Point2 GridOrigin, Point2 Spacing, int Nx, int Ny,
    ImmutableArray<Point2> Nodes, ImmutableArray<bool> ValidCells,
    NodeMeaning Meaning, Matrix? DisplacementBase, Domain ValidDomain,
    ImmutableArray<ModelParameter> ParameterOrder,
    Domain? LinearizationDomain, AssetRef? DerivativeEvidenceRef, AssetRef SourceRef);
public sealed record LocalFieldInversePair(AssetRef Forward, AssetRef Reverse,
    Domain ForwardDomain, Domain ReverseDomain, ImmutableArray<Point2> ForwardWitnesses,
    ImmutableArray<Point2> ReverseWitnesses, double SourceTolerance,
    double TargetTolerance, AssetRef EvidenceRef);
public sealed record LocalFieldLimits(int MaxFields, int MaxInvocations,
    long MaxNodes, long MaxSnapshotBytes, long MaxWorkingBytes, int MaxItems);
public sealed record LocalFieldOptions(string ContractVersion, AssetRef BackendRevision,
    ImmutableArray<LocalFieldSnapshot> Fields,
    ImmutableArray<LocalFieldInversePair> InversePairs, LocalFieldLimits Limits);
public interface ILocalFieldBackendFactory
{
    IGeometryBackend Create(LocalFieldOptions options, TimeProvider clock);
}
```

公开`LocalFieldBackendFactory : ILocalFieldBackendFactory`无参构造；`new LocalFieldBackendFactory().Create(options,clock)`返回本模块内部IGeometryBackend；随后原`CoordinateGeometryFactory.CreateWithBackend`。ContractVersion=`cg-local-field-1`，Capabilities恰`["LocalFieldPoints"]`、Ref=BackendRevision；无IO/Dispatcher/native/任务/隐式求场。null→ArgumentNullException，值/限额非法→ArgumentException并指出字段；失败不建活动计算。Fields非空、Ref唯一，完整Frame/源/目标均2D，单位/轴/域按§3；Pixel仍原ImageColumnRow/Center，不能把像素节点当mm。所有Limits正，MaxFields≤1024、MaxInvocations≤1000000、MaxNodes≤10000000、MaxItems≤10000000；字段/账本/返回托管结果的总字节受MaxSnapshotBytes，scratch含导数矩阵并发峰值受MaxWorkingBytes。

Spacing.X/Y正且以Source单位表示，Nx/Ny≥2；节点row-major `k=j*Nx+i`、i沿源第一轴、j沿源第二轴递增；Nodes.Length=checked(Nx*Ny)，ValidCells.Length=checked((Nx-1)*(Ny-1))、cell下标`j*(Nx-1)+i`。所有节点有限，即使无效cell也不填NaN/隐含缺节点；无效cell显式false。外边界为GridOrigin至`GridOrigin+((Nx-1)*Spacing.X,(Ny-1)*Spacing.Y)`，溢出拒绝。ValidDomain为源域并包含在grid支撑内；查询点同时核Frame.Domain/Edge.ValidDomain/field.ValidDomain及选中cell，任何层拒绝均不外推。内部运算exact保留binary64源值，cell归属用精确比的floor，不以epsilon移动到旁cell；最后一列/行中心节点归最后cell，跨内网格线用右/上cell（即该cell的左/下边），边界规则仍沿原Domain。

TargetPosition时Nodes是Target单位的绝对目标位置，DisplacementBase=null。TargetDisplacement时Nodes是Target单位位移，DisplacementBase为**必填**3×3 affine，最后行(0,0,1)、有限、源→目标方向及单位/基准显式；即使单位相同也传identity，不从同名轴猜基准。输出为`base(sourcePoint)+interpolatedDisplacement`；跨单位只由此矩阵或请求已有明确单位边编码一次。矩阵稳健性沿§3.5，不新增逆/拟合路线。

ParameterOrder为节点坐标变量全部`node[0].x,node[0].y,node[1].x,node[1].y,…`，每项TargetLength、正有限Scale显式提供；与Edge.ParameterOrder逐项相等，ScalarPath按§4.3.1原样前缀`parameters.`。GridOrigin/Spacing/base作为冻结坐标定义，不在此节点参数chart中拟合；其不确定度若有关，由前级已登记Edge/联合输入提供，不能静默宣布为0。节点拟合协方差由原Edge/JointCovariance显式输入，缺失按原Optional/Required规则，不把残差当节点完整协方差。Ref.Hash使用§4.2现codec字段序/分支tag=`LocalFieldSnapshot`、排除自身Ref.Hash；BackendRevision绑定完整Options，原SourceRef/EvidenceRef是Owner发布引用，不能重算替换其原hash。

每个实际Map的ExternalModel.ModelRef精确命中Fields.Ref，CapabilityId=LocalFieldPoints，实际Step/Frame/域/ParameterOrder一致；未知模型CG017，缺原封存版本CG018，错单位CG003。Forward映射直接该场；Analytic inverse不支持。ProvidedInverse只消费**另一条已存在反向Edge/反向field**：两Ref必须命中同Options.InversePairs，pair两域等批准用途域并位于各field有效域，两个方向的原源/目标Frame交叉相等，双向Witnesses非空、finite、预算内；Tolerance有限非负，SourceTolerance用Forward.Source单位，TargetTolerance用Forward.Target单位。Owner在注入前验证EvidenceRef所指唯一性/有效域原件与这两完整field/域/版本绑定，factory保存该已冻结值；Core按§5在使用时以正反向见证回环对账，不能将probe通过当全域唯一证明。无原证据/配对CG018，不捏造新逆场、牛顿搜索或用det非零代替资格。

Map原子占Invocation槽/输入深拷贝/导数与输出最坏字节→记录原InvocationId/Task→有界执行；同ID同完整值观察原调用，不同值CG014；超限CG007且零外部副作用。不捕获SynchronizationContext；前台Submit/Dispatcher不执行插值长循环。deadline按注入clock、token在逐item/节点导数/budget检查点生效。无native租约，scratch不再被原工作访问后才Confirmed/0；异常保CG010、到期CG009/取消CG008，晚结果不交Core消费。DrainAsync只查/等原调用，未知原IDCG011/Unknown而非伪Confirmed；wait token只结束观察。完整账本/墓碑有限且保留到原service epoch退役，满限不覆盖；借用backend无Dispose入口，所有service Stopped/Confirmed后Host才卸载托管引用。

混合相机/局部场的Host需要组合backend时，在本Core `Adapters/` 使用公开无参`GeometryBackendRouterFactory`，唯一方法`IGeometryBackend Create(AssetRef revision, ImmutableArray<IGeometryBackend> children, int maxInvocations, long maxRetainedBytes)`。只借用非空children；完整Capabilities.Ref/ID不重复且child能力ID集合互斥，否则构造ArgumentException，不按注册先后选赢家。Create无工作，Map按实际ExternalModel.CapabilityId或原§8.3矩阵能力精确路由一个child，保存原Invocation/child/Map Task；原值/预算/ID不改，Drain只交原child，无后端fallback/隐式重试。自己的有界输入/账本字节与child额度分账，超限先CG007；child返回Confirmed/0后才归还router临时强持，仍保墓碑。router本身不Dispose children；其Owner只在全部service/child确认后退役。纯Core数学和单backend不需要router，不增加全局服务定位器。

#### 9.1.2 插值、导数与固定消费反例

四节点记N00/N10/N01/N11，`tx=(x-x0)/sx,ty=(y-y0)/sy`；`F=(1-tx)(1-ty)N00+tx(1-ty)N10+(1-tx)tyN01+tx*ty*N11`，全部用原exact有理求值后nearest-even到double。`Fx=((1-ty)(N10-N00)+ty(N11-N01))/sx`、`Fy=((1-tx)(N01-N00)+tx(N11-N10))/sy`；位移分支加base线性块。双线性混合二阶导数为`(N11-N10-N01+N00)/(sx*sy)`，其它二阶导数0；用§3.8同dual表达式生成J，不数值扰动猜步长。

支持ordered Point2以及带Anchor的Vector2/Normal2：Point=F(p)，Vector=`J(anchor)*v`、Anchor=F(anchor)；Normal=`normalize(J(anchor)^-T*n)`、Anchor=F(anchor)，先按原§3.5证明该局部方阵稳定；缺Anchor/零法向/边界导数不唯一拒CG019/005。Source/Target均二维；3D局部场、连续Polyline/曲线/填充Polygon/plane未声明则CG019，不自动转点。纯Point落网格线可取固定所属cell算值；需要导数时内网格线或四节点支撑不完整不返回导数，Required CG020、Optional NotEvaluated；锚点向量/法向依赖导数则整个几何拒CG019，不给近似平均J。

BackendDerivatives按输入/输出实际Geometry scalar顺序，InputJacobian为各item解析块组成block-diagonal，ParameterJacobian为对全部原node参数的导数；无贡献节点列仍保留零，不能缩短ParameterOrder。LinearizationDomain与DerivativeEvidenceRef要成对，由Owner给并核全部点/anchor在该域；必须处于**同一有效cell的严格内部**才回单个BackendDerivatives（现DTO只有一个Domain）；跨cell的多点仍可映射，但Optional不回误差、Required CG020。曲线全域不因此开放。参数误差、不同项相关性仍由原联合块处理，参数重复只登记一次；对Vector/Normal的anchor/J/node导数使用上述dual和原normalize/inverse微分。

两消费者各自实例，复用§10.1根预算及§13.1runner。软件正常field Source/Target均mm、GridOrigin=(0,0)、Spacing=(1,1)、Nx=Ny=2，Nodes=`[(0,0),(2,0),(0,3),(2,3)]`、ValidCells=[true]、TargetPosition/base=null、ValidDomain=Closed Box2(0,0)-(1,1)，ParameterOrder为上述8项且Scale=1，LinearizationDomain=Open Box2(0,0)-(1,1)、DerivativeEvidenceRef/SourceRef均独立具名synthetic原件。每个Frame/Field/Edge/Graph按旧codec现算真实hash。A用ROI有限顶点Point2(.25,.5)，B用计量同点；分别Map应(.5,1.5)、J=diag(2,3)，源协方差diag(.01,.04)且节点协方差**明确零块**时目标diag(.04,.36)；不把缺节点块当零。带Anchor(.25,.5)的Vector(1,1)→(2,3)，单位Normal(1/√2,1/√2)→(3/√13,2/√13)，仍输出映后Anchor。

补充反例/必需断言直接归原CGT-MODEL/COV/DRAIN/VERSION，不新建Golden文件：invalid cell→CG004；x<0不夹紧；间距0/节点数量错/default/漏node零项→构造拒绝；DisplacementBase未给→构造拒绝；显式base=diag(.001,.001,1)、Source um点(250,500)、位移四节点均(1,2)mm→(1.25,2.5)mm，仅一次缩放；网格内线x=1的Nx=3场Point值可算但Required导数CG020；折叠场/无逆Evidence不开放inverse。原正常field的独立反向场Spacing=(2,3)、Nodes=`[(0,0),(1,0),(0,1),(1,1)]`、域[0,2]×[0,3]，配对software Evidence明确Synthetic，双向Witnesses包含各原点/角点及内点，Source/TargetTolerance=1e-12，只验证显式配对消费，不能授生产全域单射。相同输入两作者同node序/字段/旧codec须同hash/结果；A取消/关闭不影响B，deadline/迟到/重复ID沿原账本与根关闭断言。

负载冻结到原Benchmark维度：field数、Nx/Ny/有效洞、items/anchors、node参数列数与协方差维数、跨cell无导数、配对见证数、并发/保留水位；记录封存/选cell/插值/dual/矩阵传播/释放，node参数最坏Jacobian字节checked预约。软件Profile为单field/4nodes、MaxFields2/MaxInvocations64/MaxNodes128/MaxItems128、snapshot4MiB/working4MiB、原2s执行与10/120/180s测试截止；实测目标仍取消费者Profile。字段来源/逆场发布、唯一性及物理线性化证据归外部坐标资产Owner，内部类型/算法/构造/失败/Owner已确定，真实实现/运行另验。

### 9.2 相机资产消费

相机模型来源 Owner 提供精确 HALCON camera参数形状、camera frame、world frame、WorldPose方向、标定单位、图像尺寸/像素约定、工作平面、可见域、质量引用、版本/hash及适用条件。模型可解析不等于合格；Owner或宿主要求质量引用时，缺失只阻断该物理模型请求，不阻断SI换算/纯数学域检查。未知Z、非world z=0平面或缺平面映射不得借本模块偷偷求新标定。

#### 9.2.1 Camera Read API 1 → CameraBinding的有限只读桥

精确上游是[calibration-assets §9.3](../calibration-assets/DEVELOPMENT-GUIDE.md#93-已解相机参数公开读取增量camera-read-api-1)：`Asun.Modules.CalibrationAssets.CameraRead.CameraParametersReader.Create(CalibrationAssetsOptions,CameraReadAdapters)`→`ICameraParametersReader.ReadAsync(CameraReadRequest,ct)`，不是`ReferenceGeometryRef`/SolvedParameters引用自动解参、不是InitialParameters，不调用Prepare/Solve/标定板检测/重新求解，不读Joint或camera_setup。`CameraBinding`持有完整ReadRequest及CameraParametersSnapshot以保存原OperationId/用途/输入和资格原件；`AssetRef ModelRef`只是此本地冻结binding的地址，不能替代上游原string revision/hash。

1. Host先按§10.1占根Owner槽，构造显式reader options/adapters（Store/Content/Qualifications/ExecutionGate/Diagnostics/Clock全部非null，借用端口）再调用唯一Create。ReadRequest逐字段取已发布Asset、该asset精确ExpectedSolvedParameters、实际设备/OperatingDomain、曝光闭区间、有限预算、新OperationId和确切IntendedUse；不使用CalibrationExecutionBudget.Default隐式延长本流程。Read原ValueTask只AsTask一次登记；Wait/Cancel到期保留原Task/reader/OperationId/依赖。仅`Completion=OperationCompletion.ResourcesReleased && Status=ApplicabilityStatus.Applicable && Error=null && Snapshot!=null`进入下一步；DrainPending、Unknown、NotApplicable全部不构造成功binding，CAL原诊断/错误保留并映CG018，明确不含图像像素/设备控制。
2. 保留Snapshot.Asset、SolvedParameters完整ContentRef（format/revision/length/digest）、Solution全部原字段/Parameters、CalibrationDevice、Qualified、Watermark、ApprovedDomain、ObservedAtUtc；核Asset/ExpectedSolvedParameters/Use/ActualDevice/ActualDomain/曝光与ReadRequest绑定，Qualified.Artifact等Asset。Solution.Model/顺序/单位用CAL §7.2C和CameraSolutionCodec定义，不按数组长度猜模型、不重排/alias；width/height整数pixel须等CalibrationDevice真实尺寸。area_scan_division顺序Focus/Kappa/Sx/Sy/Cx/Cy/ImageWidth/ImageHeight（Meter/PerMeterSquared/Meter/Meter/Pixel/Pixel/Pixel/Pixel）；line_scan_division追加Vx/Vy/Vz，严格MeterPerRow，**不是m/s**。其它CAL已支持模型按其原表原样传cv2，但不据此开启本backend未声明路线。原参数一直保留米和原模型单位；输出几何单位只在既有§8映射边执行一次转换。
3. Read只给内参/设备/资格，不给当前图像Frame、外参WorldPose或工作平面。这些由本次Host冻结的独立来源提供：完整原Pixel Frame/Ref、Camera Frame、World/Plane Frame、CameraFromWorld矩阵、PoseRef及WorkPlaneRef/UseEvidence.EvidenceRef所指用途原件。原件须明确绑定上述全部Frame/pose/已解资产/Read Use/设备/曝光、实际工况/批准域、可见深度和plane z=0资格；只给一个来源Reference而无对应实际值不能构造成功binding。此Host已持有完整来源值/批准证据，不让backend在Map里读latest或IO。不把CAL CoordinateFrame(Id/Handedness/AxisConvention)无revision字符串直接伪造本Core Frame.Ref；宿主坐标资产Owner显式发布两者绑定及版本。crop/resize/去畸变frame必须先有已批准链到原相机pixel frame，不改Cx/Cy冒匹配，原像素域取完整栅格与批准图像域的明确交集。
4. 路由闭合：PixelToWorldPlane必须PlaneFrame为2D SI、WorldFrame/CameraFrame为3D右手SI且有明确同名物理基准的单位链，PixelFrame为原ImageColumnRow/Center。PlaneFrame由证据明确为该WorldFrame的z=0坐标图，CameraFromWorld为4×4 rigid camera←world、平移按CameraFrame单位；按§3既有正交/方向验证后转换到米再经[hom_mat3d_to_pose](../../../halcon算子手册/operators/hom_mat3d_to_pose.html)（输出type0）取HALCON pose，不让它把非rigid近似成pose。HALCON源米→目标mm使用Scale=`"mm"`（目标Metre=`"m"`、Micrometre=`"um"`、Nanometre先`"m"`再显式10⁹边，拒隐式双缩放），只返回plane x/y；不猜Z。WorldToPixel同样要求WorldFrame/CameraFromWorld，世界Point3先已批准camera←world米变换再project_3d_point。CameraToPixel只需camera米Point3，WorldFrame/PlaneFrame/CameraFromWorld为null。DistortionPoints要求TargetReadRequest/TargetCamera/TargetPixelFrame完整且两次读取各自ResourcesReleased/Applicable、同曝光/明确用途，原目标参数原样传；其它路线这三个字段必须null。WorldToPixel的PlaneFrame/WorkPlaneRef为null，PixelToWorldPlane二者必填，其它route WorkPlaneRef=null；PoseRef在有外参route绑定外参，在其它route绑定原camera frame的坐标定义，不填随机证据。
5. 有效性与资格：Current Clock须在每份Watermark.ObservedAtUtc..ValidUntilUtc，Authority/Epoch/Revision逐字段保留，UseEvidence.Use等ReadRequest.Use、Watermark等原Camera.Watermark、ExposureFrom/To等ReadRequest曝光。UseEvidence.ApprovedConditions按同CAL OperatingDomain量/单位规则覆盖ReadRequest.ActualDomain，VisibleCameraDomain为同CameraFrame单位的明确有限Box3（不能Unbounded/默认Z>0套所有镜头），来源Owner对该模型可见性有证据。曝光在Qualified.QualifiedAtUtc..ValidUntilUtc及用途ValidFrom..ValidTo覆盖窗；validTo=null只表示Owner明示无上界，不免当前水位。Reader已核本次ActualDomain落在ApprovedDomain，Host另核每个输入点/图像有效域、plane用途和当前配置。Map每native前/结果发布前再次核本次冻结水位仍在有效窗；失效/撤销/断线时Host先关相关service的物理请求接纳、显式Cancel原计算并撤显示，保留旧结果为历史，不把原快照改成新资格。**新请求重新Read并取得当前水位，构造新backend/service epoch**；不长期cache、不开默认TTL，不用新OperationId重试旧在途Read。若使用时无法证明当前权威水位或用途，CG018/NotEvaluated不执行native；Read Applicable不等于plane/pose/整个测量链合格。
6. 收尾按原reader接口：只登记一次`StopAsync(new DrainRequest(cleanupOperationId,finiteWaitLimit≤30s),independentCleanupToken)`，查询原`GetOperationState(readOperationId)`；所有原Read/Stop Task及流/预约均ResourcesReleased后只登记一次`DisposeAsync().AsTask()`。Dispose仍Pending则根继续持有，不退借用端口。新有界观察可等原Task，不重复Read/Dispose/更换原OperationId；迟到Snapshot在关门后仅留诊断，不启动backend。根转交须接收者预留并确认全部原Task/reader/引用/预算/错误的同TransferId，未确认仍由原根持有；转交不是ResourcesReleased。

单位与域执行补充：PixelToWorldPlane的native输出PlaneFrame.Unit只允许Metre/Millimetre/Micrometre，对应`m/mm/um`；需要Nanometre时先在独立Metre PlaneFrame返回，再沿Host明确发布的Core scale边×10⁹到另一个Nanometre Frame，不能让ExternalModel目标声明nm而回米。PlaneFrame.World的轴/单位关系必须由证据给实际已批准值；不能仅按同名XY默认重合。对PixelToWorldPlane输出点再按既有plane→world及camera←world值链核VisibleCameraDomain；其它projection路线在native前核camera点域，DistortionPoints核两原pixel有效域和原上游模型限制。不支持/无可验证域CG018/CG004，未知真实可见域不默认为无限。

此桥封住软件字段/Owner缺口，不授物理资格。客户/设备外门精确为：真实已发布solved writer/content/资格Owner当前水位、原frame坐标链及尺寸域、真实camera←world与工作平面批准用途、独立像素/空间误差/可见深度/曝光工况样本和性能目标。它们只阻依赖这些事实的CameraRoute请求及真实桥验收；不重退Core，不阻无camera的HALCON矩阵桥或无图像Inspector。用途Name/Revision由Host既有批准请求原值传Read和UseEvidence，不将mosaic的LineScanRow0Projection资格移植到平面测量。

### 9.3 Motion CoordinatePort 责任边界（只消费上游合同）

本模块是通用坐标/几何资产与变换的Owner，不实现 Motion 的 `IMotionCoordinatePort`、`CoordinateQuery`、机器权限/lease、运动 operation、Stop/Recover 或设备状态对账，也不拥有 Motion 的写入或安全责任。需要运动的产品组合由 [motion-control](../motion-control/DEVELOPMENT-GUIDE.md) §17.2 的原始端口合同负责接入，并由 [googol-motion-adapter](../googol-motion-adapter/DEVELOPMENT-GUIDE.md) 的已转换路径消费；本模块不向这两个模块添加第二个坐标端口、适配器或隐式业务依赖。

上游 `CoordinateQuery` 必须显式携带 `Kind` 与冻结的机器域 `Start`：`Move` 的点是用户目标，`MoveRelative` 的点是用户坐标系中的 Delta，`Trajectory` 保留用户点列和 Offset。坐标端口按 `Kind` 解析，不按数值、tick 大小或字段形状猜绝对/相对语义，不把机器 actual 再次参与坐标变换；相对请求只把 Delta 按批准资产映射到机器域后加到冻结 Machine Start。需要时，上游同时提供完整 Start/目标或轨迹、Frame、`CoordinateAssetSha256`/资产摘要和每轴 `ApproachPolicy`，端口输出唯一机器域路径、禁区校验、映射摘要及接近方向。时间化、控制器能力、Stop、授权和最终设备回执仍由 Motion Owner 负责。

坐标几何向该端口提供的仅是已发布、带版本和适用域的几何资产/变换能力及其摘要；缺少 Frame、资产资格、Approach 证据或当前水位时返回可判定拒绝/Unknown，不用默认 Frame、默认资产或本地重标定补齐。`ResolvedMachinePath` 一旦由上游生成，后续适配器只验证其逐段摘要和时间化字段，不由本模块重排、改速、补路径或重算设备目标。该边界不改变本模块 Core API、Inspector、无 UI 计量消费者或既有 Golden。

## 10. 无 UI 最小宿主与两个消费者

以下为语义调用样例，全部类型由 §4 定义；不依赖未定义的宿主factory，也不声称示例已编译。软件数值限值由宿主自己的 NumericPolicy 与 RuntimeLimits 明确提供，不依赖客户物理精度值。

1. 宿主构造已接收的 RuntimeLimits、选择 ManagedCore 与 TimeProvider，外部模型端口为空；创建服务实例并保存 ServiceInstanceId。
2. 构造 Fsrc/Fdst 的精确 Frame Ref、毫米单位、Cartesian轴、显式Box2域；仿射边 Tdst_src 平移(3,4)、再scale2的矩阵为 `[[2,0,6],[0,2,8],[0,0,1]]`，源域和目标域须覆盖算例；数值策略和图用各自封存hash。
3. 构造 Map Work：graph={两帧/该边}、source=Fsrc、target=Fdst、path=Explicit[边Forward]、batch=[Point2(1,2)]、NumericPolicy、ExecutionBudget，RequestId唯一，ContractVersion=0.2。
4. `receipt = await service.SubmitAsync(request, admissionToken)`；短拒绝直接按错误恢复。Accepted/Duplicate后 `await service.WaitAsync(receipt.RequestId, finiteWaitBudget, waitToken)`，只有 Terminal且Snapshot=Completed/ResourcesReleased后消费 `(8,12) mm`；WaitExpired只Query原操作。
5. 运算取消用 `CancelAsync`；仅停止等待用waitToken；拿到终态后由宿主保存来源引用和结果。关闭先 `StopAndDrainAsync`，Confirmed后才卸载相关适配器；Unknown保留实例继续查询。

ROI消费者传自己的工程/像素图、Polygon/Segment；返回几何项原索引、环/洞结构和变换来源，不返回ROI用途、目标ID或自动改ROI版本。计量消费者用同包、无WPF引用，传已确定的物理链、Normal/Segment/Arc及协方差，返回数值与NotEvaluated/传播摘要；测量定义、MSA/容差与最终决定仍在计量Owner。两个消费者同图/同数值策略/同后端应得到等价canonical结果；显示格式或语言切换不影响hash/数值。一方Cancel/Close/Profile更新不污染另一方；最好各持自己的服务实例，若共享则Stop权仅由共同宿主掌握。

### 10.1 构造前Host根Owner与原身份恢复（Host辅助规格，不新增产品DLL）

本节供§10.2两个外部Host及其WPF模式共用，只是允许测试/真实宿主中的有限Owner实现规格，不改Core service API、不强迫新建Runtime/Host DLL。每个Host在任何Reader/Backend/Service/Viewport/Inspector factory或Dispatcher操作**之前**由进程长期对象持有自己的根账本；离开Run/catch/finally不能销毁仍Pending的根。根限额显式为MaxOwners/MaxOriginalTasks/MaxRetainedBytes/MaxCleanupAttempts、独立CleanupAttemptBudget/ObservationBudget和Clock，全部正、checked；MaxOriginalTasks含原业务/枚举MoveNext+Dispose/Dispatcher/Close/Stop/Dispose及已预留迟到收敛槽，禁止只记外层async方法。合成Host Profile固定各Owner≤16、原Task≤128、retained≤32MiB、清理最多2次各2s、每次观察2s、每case10s/整run120s/外层180s；不是生产时延门，真实Profile按消费者显式收紧/批准。

每次启动的顺序固定为：根原子预留Owner/字节/原工作及独立cleanup槽→保存完整构造参数/依赖/Clock/epoch/原ID→调用factory一次→立即登记返回对象。同步factory必须只有限本地构造；若Host选择后台/Dispatcher构造，先保留启动委托及原Task槽，返回值提取器由根保存，迟到对象先接住再关闭，不能以观察wrapper完成或赋值变量为保留证据。工厂配置拒绝只撤明确未Started槽；启动后异常结果不明不假称未构造。每个ValueTask只AsTask一次，原Task加入同一根；等待投影/WaitAsync结果只作观察。原Task仍挂起、返回资源、故障且归还未明都占槽；借用端口的物理pool容量和本根强持引用分账，不把逻辑归还当物理退款。

正常/异常/取消finally先关闭Host工作门、保存原业务ExceptionDispatchInfo/错误，cleanup错误另轴收集。Inspector.Close/服务Stop/Reader.Stop各只启动一条原关闭过程，不把UI关闭当Service.Stop；原Service/RequestId、Reader/OperationId、backend/InvocationId、Viewport root/session/binding及每个原Task均强持。服务恢复只在**原**service上`QueryAsync(originalRequestId,finiteQueryToken)`/`WaitAsync(originalRequestId,finiteBudget,waitToken)`，WaitExpired或未知不生成替代RequestId；显式Cancel同ID且保存原Cancel Task，查原操作直到其真实终态/Drain Confirmed。元组ServiceInstanceId+RequestId不改；同内容重提仅接纳重试原ID，不因观察超时再Submit。进程重启无法恢复原内存worker：持久未知记录由原Host恢复机制对账，不在新Service上把NotFound当旧请求不存在。

cleanup使用独立有限token，不链接已取消的操作/窗口token，也不使用无限CancellationToken.None。先撤自己的Inspector/Display观察与图层，持有并等待全部原Bind/Present/Clear/Dispatcher动作；原Close到期只重新有限观察同关闭Task。必要再次调用已定义Close/Stop只是观察其同一关闭过程，并逐次登记观察Task，不重发底层Clear/Dispose。服务Host随后一次`StopAndDrainAsync`，Reader按§9.2.1一次Stop/Dispose；Viewport仍由其Owner一次Unbind、同Session.Dispose/root.Close（见§11.4.1）收敛。关闭协调者不计入它自己正在等待的资源worker集合，不在Control/Dispatcher清理回调内await同Session/root Close，避免自等待。只在原Task全退出、lease/显示缓冲确已归还、各关闭回执明确Confirmed/Drained后退Owner槽。方法返回/终态字符串/GC/Dispatcher退出不能代替这些证明。

两次有限尝试后仍Unknown：关新接纳并保存Pending原Task/构造与请求/结果或迟到提取器/所有借用/字节/原错误/cleanup额度，留根恢复面板；可在实际状态变化后新有限观察，不能无限轮询/强杀native。移交只能是同TransferId全量offer，接收Owner先在自己的有限根预留并强持全部对象/原Task/待归还和预算，再确认唯一Owner切换；拒绝/异常/超时/迟到未确认，原根不退槽。AcceptedTransfer不是ResourcesReleased。Dispatcher即将退出时若未获Confirmed，Host关闭视觉输入可隐藏窗口，但根保留控件/任务与显式未排空错误，不能Dispose借用viewport/后端或声称干净进程退出。

### 10.2 两个独立外部Host的准确装配与调用卡（未创建/运行）

本轮只定义真实公开成员的实施调用，**不是本轮已实际调用的记录**。唯一允许的后续Host消费者位于对应既有计划测试工程`Asun.Modules.CoordinateGeometry.Halcon.Tests/Consumers`与`.Wpf.Tests/Consumers`，不生成新的TestHost项目。A=`RoiInspectorHost`（独立STA/UI），B=`OfflineMetrologyHost`（net10.0无UI）且在既有Wpf.Tests用同B服务消费逻辑增加`OfflineMetrologyInspectorHost`独立STA壳；它仅作同第二消费者的UI资格模式，不作为第三产品/新模块。两个STA串行占同一个固定1920×1080验证viewport，不开分辨率矩阵；二者独立Thread/Dispatcher/Window/ConsumerId/root/service/clock/参数，noUI模式不引用Wpf/Dispatcher。运行模式明确区分Managed、HalconMatrix、CameraRead、STA-NullDisplay、STA-BorrowedViewport；任何未执行模式不能记通过。

公共合成输入复用§10的毫米Frame/Box域、matrix `[[2,0,6],[0,2,8],[0,0,1]]`、Point2(1,2)及**既有**CGT-API/GRAPH fixture公开值/Policy/RuntimeLimits构造，不新增编码/Golden；A/B分别构造相同内容新RequestId（如hostA:map:1、hostB:map:1），预期(8,12) mm。Host Profile沿§10.1。HalconOptions=`("cg-halcon-assembly-1",发布BackendRevision,["Affine2Points"],ImmutableArray<CameraBinding>.Empty,new HalconBackendLimits(64,128,4MiB,4MiB,16))`；后端版本来自实际发布包，缺时该模式不执行，不以假hash过验。Managed模式仍用原CreateManaged，无需相机或HALCON。

BorrowedViewport模式的Host根retained上限显式改为256MiB（同时预留Inspector/新旧显示/上游root强持），ViewportRootOptions固定`(rootId,MaxSessions=1,MaxTrackedTasks=64,MaxPendingReturns=64,MaxRetainedBytes=128MiB,CleanupAttemptBudget=2s,MaxCleanupAttempts=2)`；ViewportOptions.ConsumerId等本Host、AccessMode=ReadOnly、Features=Navigation|Presentation、MaxDisplayBytes=64MiB、MaxInFlightTiles=1、OperationTimeout=2s、DrainTimeout=2s、Roi/Surface/Probe/IntentSink=null，Frames/Coordinates/Authorization/Backend/Presentation及Required时ResourceAdmission均完整由其已批准Host或上游完整夹具提供。Limits采用上游§11完整有界Host profile并明确来源版本，资源实际计划超过本根剩余容量先拒绝，未提供不使用隐含默认。离线Synthetic可BudgetOnly且授权Purpose=OfflineViewing，ProductionDisplay/EvidenceReview必须Required/HalconRequired。STA-null和B noUI仍为32MiB根Profile，不因本显示模式扩大Core RuntimeLimits或未来生产配置。

| Host/阶段 | 准确外部调用顺序及保留对象 | 验收断言 |
|---|---|---|
| A/B noUI工作 | 各自先占§10.1根槽→`new HalconGeometryBackendFactory().Create(options,clock)`→`new CoordinateGeometryFactory().CreateWithBackend(limits,clock,backend)`；保存实例ID→登记`SubmitAsync(request,admissionToken).AsTask()`一次→回执Accepted/Duplicate后登记`WaitAsync(receipt.RequestId,2s,waitToken).AsTask()`；读取同原Query，不改ID | actual HALCON矩阵组须调用真实cv2并与原Golden断言(8,12)，不能以Script backend代替；Managed模式独立原Core结果；不需要客户物理样本 |
| A/B CameraRead模式 | 各自占reader槽→`CameraParametersReader.Create(readerOptions,adapters)`→`ReadAsync(exactReadRequest,ct).AsTask()`一次，字段/有限预算沿§9.2.1→完整释放/Applicable后构造各自CameraBinding/Options→backend/service/ExternalModel edge→同Submit/Wait/Query协议；源/目标Frame及Capability按route | 纯协议夹具可直接复用上游CAL §9.3.4完整Synthetic已解向量/Store/Qualification/Clock/Options/ReadRequest与字节原件；断言Focus=.010不是initial .009、line Vy=.00002不是initial .000018，原模型/单位/资格水位保真。该夹具Use仅LineScanRow0Projection，**不运行plane投影**；面阵/plane成功必须另输入真实批准Use/已解参数/pose/plane，不能改fixture字符串赋资格 |
| A STA构造/绑定 | STA线程设ApartmentState.STA后Start，线程内取Dispatcher.CurrentDispatcher，先占根/UI安装槽→在同Dispatcher一次`new CoordinateInspectorFactory().Create(new InspectorOptions("host-A",guardedService,displayOrNull,new CultureInfo("zh-CN"),hostThemeKey,new InspectorLimits(128,1024,4MiB,2s,2s)))`→保存View/控件→登记`BindAsync(snapshot,waitToken).AsTask()`一次；Generation从1，本Graph/DisplayFrame/显式display矩阵/ref和原Operation都准确绑定，Display=null无隐藏image窗口 | Create不计算；Bind不Submit，只有点击预览才Submit；same generation冲突拒绝、旧事件/迟到不覆盖。View挂载之前无Parent，1920×1080键盘/UIA/状态和影像优先布局按§11.1–3 |
| B独立STA观察 | 另线程/root/service/ConsumerId="host-B"，同factory/options但Culture="en-US"；Bind自身snapshot；依次Dispatcher调用SetCulture(zh-TW/en-US/zh-CN)、SetHostTheme(本Host已有资源key)，bind的Graph/hash/数值不变；借用显示按§11.4.1 | A关闭/取消/切文化/Profile不改变B。B.Display=null时只读矢量/三维表，不造影像；B noUI模式根本不创建Wpf factory/Window/STA |
| 取消/观察/原恢复 | A只取消Wait观察，继续原Query应可Executing；另显式CancelAsync原RequestId，旧成功提交点规则不变。B保持正常；对Read/Map/Dispatcher延迟均保留原Task和清理槽；关门后迟到结果只回收/诊断 | 不同service/request/epoch无串用；未知不改NotFound、不再Read/Submit；native不硬取消，迟到不发布用途/overlay；响应慢不当作已释放 |
| 关闭/故障/退出 | A/B各保存原业务错误→独立cleanup token启动本Inspector.CloseAsync(2s,ct)并保留原Task→Confirmed后Dispatcher移除Inspector.View→本Host一次service.StopAndDrainAsync；CameraRead模式再同reader Stop/Dispose；借用viewport收尾在所有Inspector/UI作用域外由其Owner执行§11.4.1→全部确收敛才允许Dispatcher.BeginInvokeShutdown/Thread退出 | 异常/取消/窗口Close/native/Dispose失败不覆盖原业务错误；Unknown保留根/原Task/view/cache。Dispatcher提前退出的注入例必须返回未排空失败，不能记录正常Close；外层测试180s硬截止只记失败，不当生产释放证据 |

两STA/noUI调用均在各自Root保留原Submit/Wait/Query/Cancel/Bind/Close/Stop Task及实际DispatcherOperation.Task，不能用`InvokeAsync(Func<Task>)`的外层Task冒充内层Bind/Close：先入Dispatcher启动成员，再分别登记其返回的唯一AsTask。两个消费者只有已明确借用的外部只读Store/Content/Qualification或frame源可共享；一方不Dispose这些共享Owner，不传Shell/页面/私表/全局当前资产。真实相机/Viewport/HALCON组与纯协议Synthetic分别报告，任何必需skip/Unknown/未排空都非零；本轮尚无这些Host工程与运行证据。

## 11. CoordinateInspector PageContract（本模块唯一 UI 规格）

### 11.1 角色、布局与视觉

工程/维护人员定位“用了哪个帧/路径/单位、哪里越域、为何无法映射”，操作员只读结果与下一恢复动作。本控件不是测量工作台，不创建ROI/相机控制或质量放行页面。基线仅 **1920×1080** 固定验证视口；记录当次OS任务栏、窗口边框/标题/状态栏，按实际可用客户端DIP布局，不改变用户显示设置、不扩展分辨率矩阵。现有DPI下检验布局/键盘/三语。

使用 `DockLayoutManager` + `LayoutGroup/LayoutPanel`：顶部单行身份/命令栏；左侧帧和路径树（初始约280 DIP）；中央几何/只读图像视口（客户区主区域，至少占可用横向一半）；右侧属性（约300 DIP，可折叠）；下方逐点表（约220 DIP，可收起）及始终可见状态行。数值是设计初始布局，不是分辨率/性能门。不足空间先折叠属性/逐点表，不遮挡主要影像、请求身份、状态和取消。布局由宿主存取个人偏好，损坏/旧布局允许“恢复布局”，不改变坐标资产。

继承宿主DevExpress主题、字号/间距/图标资源；层级清楚、数值等宽对齐、单位列独立。Raw/Canonical/Display分层入口固定可见，当前层及帧/单位标识醒目；不能只用颜色表达错误，配图标+短文字。非法域/洞、路径边、选中几何使用不同线型与图例。动效仅用于折叠/选择反馈，遵循宿主减少动画设置，不让忙碌动画掩盖Draining。

### 11.2 控件与联动

| 区域 | 25.2控件/模型 | 固定交互 |
|---|---|---|
| 帧/路径树 | TreeListControl + TreeListView，显式ItemsSource列 | 分组按帧/路径投影，图允许环故不能把图直接当无限递归树；重复引用为叶节点；点选边联动矩阵/域/来源，不能触发Map |
| 几何主区 | 宿主已有视口公共能力，2D/3D可用性由宿主端口声明 | 同一ItemIndex联动树/表；缩放/平移/镜像只作用Display；鼠标坐标同时标显示帧及可用canonical帧，不混单位 |
| 逐点/矩阵表 | GridControl + TableView，明确列，不靠AutoGenerate猜字段 | 固定索引/源值/目标值/单位/状态；排序仅视图，不能改变结果索引；筛选显示当前/总数；大输入虚拟化和有界显示LOD不改核心事实 |
| 帧/边属性 | PropertyGridControl + 显式只读属性定义/投影对象 | 按身份/轴单位/域/模型/来源分类；隐藏内部集合/服务对象/句柄；矩阵列显示方向和存储约定；复制包含单位/Ref |
| 错误/诊断 | 可展开的LayoutPanel（沿用已核对Dock能力） | 错误始终在状态行可见，展开显示失败索引/边/恢复动作，不要求先打开浮层才知道错误 |
| 非显然限制 | 命令BarButtonItem.SuperTip，内容为SuperTip.Items中的SuperTipHeaderItem/SuperTipItem | “发生了什么→影响→下一步”；半像素、域外、等待超时、Draining与取消用独立提示，禁止把关键命令只放提示里；普通WPF区域用同资源的标准ToolTip，不猜SuperTipControl |

官方候选 `DevExpress.Xpf.Editors.FlyoutControl` 页面实际落到Namespace，未得到该控件API证据，本规格采用已确认的Dock诊断面板，不猜Flyout命名空间/属性。§11.5使用本机公共XML核定具体属性；实际25.2.3只读行为仍须切片编译/WPF验收，公共文档及示例不冒充patch实测。

### 11.3 命令、状态、键盘和恢复

固定命令：刷新快照、映射预览、取消计算、查看原操作、复制诊断、恢复布局。刷新显式取得**新**宿主快照，不在旧请求中替换图；预览也是同一Submit/Wait协议，无生产保存。源/目标选择仅限宿主传入帧，路径缺失直接显示，不自动选任意相邻帧。

| 当前状态 | 命令/反馈 | 恢复 |
|---|---|---|
| 空/无图 | 预览禁用并显示“未加载坐标图” | 宿主加载明确图快照，不造演示成功 |
| Validating/Executing | 固定显示RequestId、版本、阶段；取消可见 | 点击取消发CancelAsync，不立即显示已停止 |
| Draining/Drain Unknown | 显示“正在等待计算停止”/“尚未确认停止”，原操作查询可用；新预览受限 | 保留服务/租约，禁止卸载；窗口可关闭投影但宿主继续跟踪 |
| WaitExpired | “等待已结束，计算状态待查询” | 查看原操作；不自动新RequestId |
| Completed | 图/表结果原序、单位与来源可见 | 用户检查/复制，由宿主保存/提交 |
| Rejected/Failed | 无可消费overlay；失败索引高亮与错误码/恢复动作 | 修正输入/资产后显式新请求，不覆盖旧结果 |

Tab顺序：源帧→目标帧→路径→预览→取消/查询→帧树→主区→结果表→属性→诊断。Enter仅执行当前明确聚焦命令；Ctrl+C复制当前选中值及单位/Ref；F5显式刷新；Esc只关闭局部菜单/弹层，不隐含取消计算。树/表方向键导航并联动，窗口焦点不跳转到错误弹窗；错误后聚焦对应诊断行，可用键盘返回命令栏。UIA须给稳定AutomationId（命令/树/表/状态）和自然三语Name，不用数据索引构造永久控件身份。

三语资源由宿主传Culture动态切换，无模块重复语言入口；全部列标题/状态/错误/提示/恢复文字本地化，不翻译Ref/hash/单位符号。示例固定资源：

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Preview | 映射预览 | 對映預覽 | Preview mapping |
| CancelOperation | 取消计算 | 取消計算 | Cancel calculation |
| QueryOperation | 查看原操作 | 查看原操作 | Check original operation |
| DomainViolation | 几何超出有效域 | 幾何超出有效範圍 | Geometry is outside the valid domain |
| DrainUnknown | 尚未确认停止，请查询原操作 | 尚未確認停止，請查詢原操作 | Stop is unconfirmed. Check the original operation. |
| NoPath | 找不到坐标路径，请检查帧和版本 | 找不到座標路徑，請檢查座標系與版本 | No coordinate path. Check frames and revisions. |

关闭控件仅取消观察、解除订阅、释放自身Display缓存；不取消计算/Stop服务/保存草稿。可选草稿编辑须宿主显式能力和权限投影，默认只读；保存调用§9宿主事务、失败保留草稿，不在模块放“应用到生产”命令。UI门须验证英文长文字、三语即时切换、键盘/UIA、状态时序、选中联动与Display不改canonical；当前未执行。


### 11.4 Inspector公开消费绑定、创建和关闭

冻结命名空间`Asun.Modules.CoordinateGeometry.Wpf`，项目为`net10.0-windows`、UseWPF=true，只引用本模块Core、本机DevExpress25.2.3及宿主已接收adapter；Core不反向引用。以下是本模块**自己的消费端口**，不假称其它模块已有这些成员。宿主的Viewport adapter负责将其已有只读view/资源映射到此端口；坐标模块不创建相机、ROI编辑器或HALCON显示窗口。现有`Asun.UI.Viewports.ViewportTransform`/`ViewportCoordinateOverlayRuntime`只用于Display、Vector2为float且含显示clamp/格式化，不能用于本模块double物理运算或回写canonical。其它模块`IViewportSession.DisposeAsync(timeout,ct)`由其实际Owner调用，本控件不取得该session关闭权。

```csharp
using System;
using System.Collections.Immutable;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using Asun.Modules.CoordinateGeometry;
namespace Asun.Modules.CoordinateGeometry.Wpf;
public sealed record InspectorLimits(long MaxVisibleItems, long MaxDisplayVertices,
    long MaxDisplayBytes, TimeSpan ObservationWaitBudget, TimeSpan CloseWaitBudget);
public sealed record InspectorSnapshot(ulong Generation, GraphSnapshot Graph,
    GeometryRequest? PreviewRequest, OperationSnapshot? Operation, AssetRef DisplayFrame,
    Matrix CanonicalToDisplay, AssetRef DisplayTransformRef);
public sealed record DisplayGeometry(ulong Generation, AssetRef SourceFrame, AssetRef DisplayFrame,
    AssetRef DisplayTransformRef, ImmutableArray<GeometryValue> Items, long? SelectedItemIndex,
    bool DiagnosticOnly);
public sealed record DisplayDrain(ulong Generation, DrainStatus Drain,
    long ActiveDisplayLeases, ErrorCode? Error);
public interface IInspectorDisplayPort
{
    FrameworkElement View { get; }
    ValueTask<DisplayDrain> PresentAsync(DisplayGeometry geometry, TimeSpan waitBudget,
        CancellationToken observationToken);
    ValueTask<DisplayDrain> ClearAsync(ulong generation, TimeSpan waitBudget,
        CancellationToken observationToken);
}
public sealed record InspectorOptions(string ConsumerId, ICoordinateGeometryService Service,
    IInspectorDisplayPort? Display, CultureInfo Culture, string HostThemeKey, InspectorLimits Limits);
public interface ICoordinateInspector
{
    FrameworkElement View { get; }
    ValueTask<DisplayDrain> BindAsync(InspectorSnapshot snapshot, CancellationToken waitToken);
    void SetCulture(CultureInfo culture);
    void SetHostTheme(string hostThemeKey);
    ValueTask<DisplayDrain> CloseAsync(TimeSpan waitBudget, CancellationToken waitToken);
}
public interface ICoordinateInspectorFactory
{
    ICoordinateInspector Create(InspectorOptions options);
}
```

公开实现类固定`CoordinateInspectorFactory : ICoordinateInspectorFactory`，无参构造；Create签名与接口相同，具体控件session类内部化。Create须在宿主Dispatcher线程，校验Culture仅zh-CN/zh-TW/en-US（资源可扩展）、非空ConsumerId/ThemeKey、所有limits正值且有限时间、Service非null；若Display.View已有别的parent则ArgumentException、不抢宿主控件。Create只创建本模块WPF值投影/布局，**没有接纳计算/订阅后台/显示句柄租约/生产读写**。Display=null时使用本模块普通WPF矢量绘制显示几何和域，影像入口显示“未提供图像视口”；不造演示影像或阻断只读几何Inspector。3D没有真实宿主显示能力时只显示三维数值表/域，不能用2D截图声称3D呈现已验。

BindAsync显式创建本控件观察epoch，Generation严格递增、same generation same snapshot幂等，same generation不同内容拒绝CG014。旧generation事件/迟到Present不得覆盖新projection；旧Display租约未清归还则禁止换到新Display/销毁image view。Snapshot绑定Graph/Frame/DisplayTransform/Operation.ServiceInstanceId须匹配options.Service；canonical→Display矩阵只用作显示值，display frame不写进物理Graph。Bind仅绘制/观察Query/Observe，不提交PreviewRequest；预览按钮才调用同服务Submit，取消按钮显式Cancel。Operation已终态也可只读显示，无required Frame/Operation时Empty/Stale按§11.3显示，不套旧结果。

Port Present/Clear由宿主DisplayOwner串行化同generation，waitToken只停止等待，DisplayDrain.Confirmed必须ActiveDisplayLeases=0且所有先前呈现工作不再访问本控件overlay缓冲；Unknown保留本session和其overlay缓存，不dispose宿主View，不自动关闭计算Service。Clear只撤销**本ConsumerId及generation图层**，不能清空其它宿主层；端口实例在Create前已绑定ConsumerId，所有输入必须匹配。失效/当前域外几何DiagnosticOnly=true并专门样式，不可冒充结果。MaxVisibleItems/Vertices/Bytes是显示限制，超限先显示明确截断计数和原结果引用，抽稀只影响Display不得重算canonical或丢失来源索引。

#### 11.4.1 权限和Viewport借用桥（复用已有公开成员）

Inspector是只读投影；宿主在Create/Bind及每次Present前核授权快照，至少要求Viewport `AuthorizationRequest.RequiredRight=ViewportRight.Read`、`Purpose`与用途一致、`AccessDomain`/`ExpiresAtUtc`有效，并把原`AuthorizationRevision`与`ContextRevision`绑定到DisplayGeneration。坐标Inspector不获得`EditDraft`/`Export`/生产提交权；即使上游Viewport端口存在Roi/IntentSink，也不把其能力投影为本模块命令。撤权事件按原`IAuthorizationPort.Changed`串行关新Present/Probe，撤销当前图层，保留旧结果为历史并显示权限恢复动作；未确认撤销/权限查询返回Unknown，不清除其它ConsumerId。

既有InspectorOptions没有权限字段，本轮**不改冻结签名**。Host提供实现同`ICoordinateGeometryService`的实例限定只读代理（仅Host adapter，不另一个计算服务）：ServiceInstanceId/BackendRef取原service，Submit只允许已核Read及Host本地批准Preview=true的此ConsumerId输入，Cancel只允许Host本地批准Cancel=true且ID属于该Consumer已接纳操作；失败返回Rejected/CG018或Unknown/CG018并在Host记录明确权限原因，不产生原计算/取消副作用。Query/Wait/Observe只投影此Consumer已登记RequestId；撤权后屏蔽结果内容，根内部仍有原service可查询/收尾。代理Stop只由根Owner调用，Inspector.Close仍无Stop权。代理不重新hash/改Budget/复写原结果，不静默转用另一service；HostCommandPolicy的Revision/ExpiresAtUtc/Preview/Cancel本地快照显式提供，不把Viewport.Read擅自提升为机器控制或质量权限。Display=null模式同样使用该权限代理；没有Viewport不等于没有权限门。

当宿主提供已有[viewport §3.6/4.6.1/10.6–7](../viewport/DEVELOPMENT-GUIDE.md)桥时，adapter只使用其公开`IViewportRootFactory`→`IViewportProcessRoot`→`IViewportFactory`→`IViewportControlBinding.BindAsync`、`IViewportUiBinding.Presentation/SetResourcesAsync/UnbindAsync`及`IViewportUiLifetimePort.AcquirePresenterAsync/RevokePresenterAsync`、`IViewportPresenterLease.ConfirmVisibleAsync/ReturnAsync`；不反射、不实现另一套Viewport session、不给坐标模块注入`ViewportRoot`内部对象。`ViewportUiBindingOptions.Lifetime`在C#语法上可省略，但本桥真实Bind前必须由Host传入同一Control/root的非null `IViewportUiLifetimePort`；缺失在Reserve/Dispatcher/IO之前拒绝，不选择隐藏renderer。`ViewportOptions`必须由Host完整提供`ConsumerId`、Frames/Coordinates/Authorization、明确`RequestedFeatures`、MaxDisplayBytes/MaxInFlightTiles和`ResourceAdmissionMode`；在线/生产与EvidenceReview使用`Required`并注入同Owner资源准入，离线noUI/replay才可显式`BudgetOnly`，不得按产品名猜模式。Presentation必须先取得同一实际Control的稳定`IViewportControlBinding.Presentation`并传入session/options；不能用另一个Control、旧Presentation或坐标模块自造入口。

桥接顺序固定：

1. Host先在§10.1根槽预留Viewport原Task/Presenter/bytes和独立cleanup槽，在同STA创建`control=new ViewportControl()`并取得其实际`control.Presentation`；再以同一Control/Dispatcher/root构造完整`viewportOptions`，`root=new ViewportRootFactory().Create(rootOptions)`→`session=root.CreateFactory().Create(viewportOptions)`→登记`((IViewportControlBinding)control).BindAsync(session,root,new ViewportUiBindingOptions(bindingId,false,completeResources,2s,Lifetime:viewportLifetime),ct)`原Task。`viewportLifetime`必须是同一Control/root的非null实际lifetime，`completeResources`必须是完整ViewportUiResources（见下文）；Value为runtime binding且Succeeded后才登记`session.AttachAsync(context,ct)`原Task。Created generation0仅装空UI，不能Bind等待Attach而Host又等待Bind；本桥OwnSession固定false，session仍由Host关闭。所有原task和Presenter由原Viewport root自动保留，外部原Dispatcher动作通过§4.6.1 ReserveExecution/StartOriginal登记，不自己伪造CallContext。root/limits/options/renderer/LifetimePort原实现按上游§10.7/11夹具或实际已批准Host组件完整注入，不另造new Renderer猜API；真实借用模式缺组件返回Unavailable，不以Script或Headless当实际画面。
2. Host局部`ReadonlyInspectorDisplayAdapter`实现原IInspectorDisplayPort，构造输入完整为ConsumerId、上述root/session/runtime binding/control、Dispatcher、原SourceBinding/ViewportContext、SourceFrame/DisplayFrame/DisplayTransformRef/CanonicalToDisplay、InspectorLimits、Host授权快照/CommandPolicy及已由其Owner持有的呈现状态回执。构造只本地校验/保存；View为原control，须无WPF parent，Inspector仅借用并挂载，不抢其它窗口的view。此adapter只服务一个ConsumerId；禁止用户自实现假IViewportUiBinding/Presenter lease。Present预检有界Items/Vertices/Bytes，SourceFrame/DisplayFrame/transform均匹配冻结绑定；已批准canonical→原source pixel显示关系逐项用于**显示**，绝不作为Core物理结果。
3. 确定无新曲线算法的首版image overlay消费为Segment2/Polyline2：保留item/vertex顺序和索引，按显示链转为完整`SourcePoint2D`列表（Segment恰两点、闭Polyline末点仅显示时复述首点），组`OverlayPayload(SourcePolyline,sourceId,coordinateRevision,geometryRevision,Geometry=empty,Polyline=points,LabelResourceKey="",SelectionPriority=0)`、`OverlayLayer(consumerId:item:index,ZOrder,Visible=true,Interactive=false,payload,sourceRevision)`；GeometryRevision是Host发布的显示绑定号，原GeometryBatch/Frame Ref另保留，不能把Hash或ulong强转为revision。其它圆/曲线/多洞/3D继续本Inspector表/已存在矢量能力或Host已有获批ROI/surface桥，明确unsupported overlay，不抽样冒精确映射、不增加本轮算法。每次`session.ApplyAsync(new SetLayersCommand(replacement),ct)`保留原Task；replacement合并已冻结其它Owner层，只替换/移除本ConsumerId前缀，Host串行协调层快照，若版本已变拒绝重取新context，不覆盖其它层。
4. Presentation feature由session内部经Host `IPresentationPort.CommitAsync`以真实BackendSubmissionReceipt和当前授权触发原Viewport §10.7 UI Lifetime AcquirePresenter/ConfirmVisible链；不是本坐标adapter直接调用虚构session.Acquire。Host若实现lifetime，`AcquirePresenterAsync`必须使用完整`ViewportPresenterSubmission`，保留原`PresenterLeaseRequest`、`PresentationRequest`、`SourceCall`及其Context/授权/修订，不保留旧签名备用重载。原Viewport root持有Presenter/Return/Dispatcher，Host保存完整PresentationReceipt，`VisibleConfirmed`仅作显示证据。`DisplayDrain.Confirmed/0`表示原Inspector overlay缓存已由Viewport深拷贝/封存、先前原Present/Dispatcher再不借用它；Viewport自身仍持有的Presenter/图像lease继续计原root，不要求为每次Present关闭整幅画面。若本缓存仍被借用则Pending/Unknown；不能因VisibleConfirmed或Dispatcher完成假签0。需要可见时还须匹配真实VisibleConfirmed，只有计划时明确不声称已可见。
5. 每次Present/Clear前复核ConsumerId/原revision/Inspector.Generation与实际Viewport.GetSnapshot().Generation/ContextRevision及授权；两generation用绑定表，不取整数相等冒同域。观察token只结束等待，原Apply/renderer Task仍持有。Clear使用同SetLayersCommand只移除本consumer/generation层，等原Apply/本层撤销及原缓存归还后才Confirmed，不调用不存在的session.Clear。Inspector.Close不Unbind/Dispose Host Viewport：先清自身overlay/观察→Confirmed后在Dispatcher将借用control从Inspector容器脱离但保留Host强引用→Host调用已保存runtime binding.UnbindAsync原Task→确认全部Presenter/revoke/Return退出→从所有slot外有限session.DisposeAsync/root.CloseAsync。若另有Owner仍借用同session/control则Host本次不关闭它，只归还自己的借用；OwnSession=false不是自动许可关闭共享session。Unknown/Dispatcher退出均保留原Owner/Task/lease/root，不签资源释放。

本adapter对同ConsumerId/generation的Clear只启动一条原过程，后续等待/Inspector.Close观察同原Task；Clear的执行清理token独立于传入observationToken，独立2s清理额度已在构造/呈现前根预留。撤权时不能靠重新调用受保护Apply取得新读取/呈现权：原Viewport root/UiBinding已armed的Control/Lifetime Revoke负责撤销旧显示，adapter等同原cleanup与本层缓存证据，未知返回Unknown；不由坐标模块调用新的Acquire/伪造CallContext。若同generation原Present仍在受控闩锁，Clear先关新Present门并保留它，迟到apply不复活关闭图层；只在原Owner确认旧/迟到borrow退出后签0。退出顺序固定为外层Host→Inspector原Clear及本缓存→Viewport原Control/Presenter→原Return→外层Session/root关闭，不在Clear中等Host.Close或Session.Dispose，不形成反向等待。

Viewport桥只提供显示授权/资源借用，不提供坐标计算、相机参数、ROI完整性或质量资格；`VisibleConfirmed`不等于几何/物理合格。线上ProductionDisplay/EvidenceReview的资源准入、权限和呈现实证仍由Viewport/宿主Owner掌握，离线Headless只验证协议，不冒真实画面或GPU释放。

原§11.3资源/命令/状态沿用；新增恢复文字用下表，所有实际标题/列/参数/状态/诊断/提示/UIA均以本模块既有资源键投影，动态SetCulture不改数值/hash。借用viewport的语言通过Host另调用`runtimeBinding.SetResourcesAsync(完整ViewportUiResources,finiteTimeout,ct)`并登记原Task；资源输入必须是viewport权威完整schema，`Revision=viewport-ui-text/1`且覆盖该版本全部必需键，不能传旧七键/旧revision，也不能把本模块Inspector字典冒充viewport目录；与Inspector.SetCulture分别按各Owner确认，不假称切一处自动切另一模块。缺必需资源保留原完整文化/主题并报宿主诊断，不显示MessageKey/英文异常作后备，Ref/参数标识保留原值。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| InspectorTitle | 坐标检查 | 座標檢查 | Coordinate inspector |
| RefreshSnapshot | 刷新快照 | 重新載入快照 | Refresh snapshot |
| CopyDiagnostic | 复制诊断 | 複製診斷 | Copy diagnostics |
| RestoreLayout | 恢复布局 | 還原版面 | Restore layout |
| NoImageViewport | 未提供图像视口 | 未提供影像視窗 | Image viewport is unavailable |
| PermissionLost | 权限已失效，请联系管理员 | 權限已失效，請聯絡管理員 | Access has expired. Contact an administrator. |
| CameraEvidenceUnavailable | 相机参数或用途证据不可用，请检查资产和用途 | 相機參數或用途證據無法使用，請檢查資產與用途 | Camera parameters or use evidence are unavailable. Check the asset and intended use. |
| UiCleanupUnknown | 显示资源尚未归还，请查看原操作 | 顯示資源尚未歸還，請查看原操作 | Display resources are still in use. Check the original operation. |

CloseAsync首次关闭立即禁止新Bind/命令，取消自己的Observe/Wait任务，解绑所有WPF/服务订阅，调用本Display层Clear并等确认；waitBudget/token到期返回Unknown，保留本session供再次Close等同一关闭过程。Display=null时所有本地projection任务结束后Confirmed/0；任何后台投影仍用缓存时不能Confirmed。Close不调用Service.Cancel/Stop、不Dispose backend/宿主image view，不保存草稿。服务任务仍由宿主运行和查询。只有Close Confirmed后宿主可将本Inspector.View从布局移除并释放本控件引用；清理未知时宿主可隐藏UI但保留其对象/lease供跟踪。所有View/Culture/Theme/Layout更新由Dispatcher投影，不能在UI线程.Result/.Wait。

本轮固定只读Inspector，§9草稿端口是宿主可选集成职责，**不在本控件公开API启用编辑/保存**；不存在待编码者另选Apply/保存行为。真实Viewport factory/options/session的映射、宿主ThemeKey的可用资源与25.2.3实际控件行为只阻断具体宿主适配/现场WPF验收，不阻断本模块本地公开消费协议。UI自身必需断言：Create零计算/句柄；Bind旧事件不覆盖；排序/三语不改hash；Close只解绑自身；Clear Unknown不丢缓存；两ConsumerId各层互不清除；1920×1080键盘/UIA/长文本与状态反馈。

本轮复核定位：§11.4原literal及factory/Bind/Close/语言入口已经完整，原声明和责任原样复用；新增只有§11.4.1的权限代理/Viewport准确消费桥、上游装空控件再Attach顺序与三语恢复资源，配合§10.1–2的构造前根/双Host/独立有限收尾。未给Inspector加新Options/语言选择器/权限权威/生产保存或新session类型。借用control已被其它parent使用则构造前拒绝，不修改用户窗口；完整版实际行为仍须真实WPF验证。

### 11.5 确定控件配置、宿主请求与显示精度

不改§11.4原ICoordinateInspector/Options/DisplayPort签名。布局使用本机公共XML已核定的`DevExpress.Xpf.Docking`、`.Grid`、`.PropertyGrid`和`.Bars/.Core`能力。Toolbar采用`BarManager.Bars`中的单条Bar，停靠到宿主明确的Top容器并设置`Bar.UseWholeRow=true`；六命令是BarButtonItem.Content/Command/SuperTip，Command使用本模块ICommand及CanExecute，不猜BarItem.IsEnabled属性。关键预览/取消/原查询一直可见，复制/恢复同栏，不放下拉隐藏。图像借用control放ContentControl，Close Confirmed后才解除parent。

| 控件 | 可直接照文设置的公共成员 | 绑定投影与约束 |
|---|---|---|
| DockLayoutManager/布局 | 主LayoutGroup水平，左/中/右LayoutPanel；中央内部垂直LayoutGroup含主区和逐点表。BaseLayoutItem.ItemWidth/ItemHeight按§11.1初值，AllowFloat=false、FloatOnDoubleClick=false；主区AllowClose=false | 命令/身份/状态放外层WPF Grid顶部/底部，不能Dock关闭。右属性/下表通过WPF ToggleButton改变本地Visibility，语义资源一致；个人布局只存尺寸/折叠，不序列化资产/请求/权限 |
| TreeListControl/TreeListView | `DataControlBase.AutoGenerateColumns=AutoGenerateColumnsMode.None`；TreeListView.TreeDerivationMode=Selfreference、KeyFieldName=NodeId、ParentFieldName=ParentNodeId、AllowEditing=false | 平铺ProjectionNode=(NodeId,ParentNodeId,Caption,RefText,EdgeRef?)，根ParentNodeId=null；每路径步骤/重复引用是有限叶，NodeId含本投影Generation但不用作永久AutomationId。显式Caption/RefText两列，不直接递归Graph |
| GridControl/TableView | `DataControlBase.AutoGenerateColumns=AutoGenerateColumnsMode.None`；TableView.AllowEditing=false、ShowGroupPanel=false，明确GridColumn.FieldName/Header/Width | 点表Row=(OriginalItemIndex,SourceText,TargetText,UnitText,StateText)，矩阵表Row=(RowIndex,C1,C2,C3,C4)按模型有效列；在结果引用外维护排序/筛选副本；键盘选择映原OriginalItemIndex，不重排batch |
| PropertyGridControl | ShowProperties=WithPropertyDefinitions；PropertyDefinitions逐项PropertyDefinition.Path/Header/IsReadOnly=true、AllowExpanding=Never | 只读Projection类仅具RefText/FrameText/UnitText/AxisText/DomainText/ModelText/SourceText/NumericText八项string属性；属性由资源Header定义，无内部服务/集合/异常堆栈。矩阵明细单独表，不让PropertyGrid自动展开 |
| SuperTip | BarItem.SuperTip=SuperTip；Items显式添加SuperTipHeaderItem和SuperTipItem，Content分别资源标题/解释 | 半像素/显示诊断限制提示采用§11.6固定资源；正文状态/恢复在可见状态行，不依赖tooltip。普通WPF标准ToolTip同文案 |
| 主题/排版 | 宿主ThemeKey通过已核ThemeManager.ThemeName附加属性应用到Inspector.View根；字号/色彩/图标继承Host主题资源 | 标题16DIP/正文13/数值13等宽、8DIP主间距/4DIP控件间距，命令最小高32DIP；这些是UI设计初值，不是设备规格。实际可用DIP和英文长度验收仍只1920×1080 |

PropertyDefinition.AllowExpanding使用类型`AllowExpandingMode`的`Never`，不向不存在的bool属性写false；该成员/enum以本机公共XML为准。没有动态选择新控件或待Flyout/Inspector模式。布局不出浮动窗，未验证的大图/3D呈现只显示准确Unavailable/TableOnly，不能以布局截图授验收。数字显示按当前Culture，复制诊断中的原值用InvariantCulture `G17`、Ref/hash原样；格式不进codec/数学。当前树/表显示行预约字节/数量，超限只保显示窗口及明确“显示{shown}/{total}”，完整结果仍原service权威，UI不另保存无限行缓存。

**宿主刷新/选择的缺失公开接线在此补齐。** 同Wpf程序集公开静态类`InspectorHostRequests`，只定义WPF routed events，不改既有factory/Options：

```csharp
// 同Asun.Modules.CoordinateGeometry.Wpf；使用§11.4已有using。
public sealed class InspectorSnapshotRequestEventArgs : RoutedEventArgs
{
    public string ConsumerId { get; }
    public ulong Generation { get; }
    public AssetRef? SourceFrame { get; }
    public AssetRef? TargetFrame { get; }
    public ImmutableArray<EdgeStep> ExplicitPath { get; }
    public InspectorSnapshotRequestEventArgs(RoutedEvent routedEvent, string consumerId,
        ulong generation, AssetRef? sourceFrame, AssetRef? targetFrame,
        ImmutableArray<EdgeStep> explicitPath);
}
public static class InspectorHostRequests
{
    public static readonly RoutedEvent SnapshotRequestedEvent;
}
```

以上是公开声明规格（构造实现按本段），不是本轮已编译源文件。SnapshotRequestedEvent通过`EventManager.RegisterRoutedEvent("SnapshotRequested",RoutingStrategy.Bubble,typeof(EventHandler<InspectorSnapshotRequestEventArgs>),typeof(InspectorHostRequests))`一次注册；Host以`inspector.View.AddHandler(InspectorHostRequests.SnapshotRequestedEvent,handler)`订阅，Close时Host RemoveHandler。F5/刷新按钮/源目标或路径选择只RaiseEvent一次，args记录现ConsumerId/Generation和所选原Frame Ref/显式path，尚未选完整时Ref为null/路径空；本Inspector不读取模型/IO、不分配新RequestId、不自动Submit。Host可用有限原Task异步取得完整新快照，重新核权限/字段，给严格新Generation及具名新PreviewRequest，再调用原BindAsync。返回旧Generation/已经Close的响应仅留诊断、不复活UI；观察未完成不再隐式刷新或填单位阵。宿主没有注册处理能力时刷新/选择命令CanExecute=false，保留可见说明HostRefreshUnavailable；不是运行失败后静默不响应。

预览只提交当前Snapshot.PreviewRequest原完整不可变值及原RequestId；连点观察同原receipt、已执行同快照复点为Duplicate，不在控件内拼新RequestWork/hash。要更换source/target/path/参数必须经过上述Host新snapshot，参数编辑/保存生产资产不属于本控件。选择联动由本控件Grid/Tree的OriginalItemIndex驱动DisplayGeometry.SelectedItemIndex；借用image中的图层Interactive=false，本Inspector不开放未定义的拾取回调。Host已有image拾取只作为Host自身选择投影，未经原索引/Generation映射不能改此结果表；缩放/平移/镜像仍Display，不改资产。

Display=null只使用BCL/WPF值图元：Point画标记、Segment/Polyline用StreamGeometry线段、Polygon Outer/Holes用FillRule.EvenOdd并保留闭环；Circle/Ellipse采用EllipseGeometry和现有2×2基的WPF Matrix显示变换，Arc/EllipticArc按原参数和sweep分成不超过π的ArcSegment显示片，切点/方向只为呈现不写canonical。RationalConic没有精确WPF原生图元时固定TableOnly与原系数/区间，不做未定义的采样近似；3D同原表模式，真实image/3D交Host获批显示端口。所有绘制先checked估计图元/顶点字节，并取消旧generation的投影；旧Dispatcher使用未结束保留缓存，仍按原Close两轴收尾。

UI实施验证：A/B独立STA复用§10.2，不增加工程；逐一核正常/空/执行/等停止/未知/撤权/完成/失败/超显示预算/TableOnly，六命令CanExecute、固定Tab/F5/Esc、Ctrl+C精度、英语截断及焦点、UIA固定`CG.Command.<key>/CG.Frames/CG.Geometry/CG.Results/CG.Properties/CG.Status`。同一view内snapshot刷新只引起一条新Host请求，旧generation不触原service；双Consumer层/权限互不污染。布局/视觉六项与功能/真实资源分别验收，未执行不能计通过。

### 11.6 完整必需三语资源与诊断投影规则

本节与§11.3/11.4.1既有key合并为一份本模块资源字典；不重复定义已有key。资源构造在Wpf内部，zh-CN/zh-TW/en-US全量覆盖以下keys和既有keys；SetCulture先核完整目标字典，原子替换投影，缺key保留旧文化并向Host报MissingResource，不能让开发者临时补英文。图表/属性/命令/UIA Name都用资源；Ref/hash/model参数裸名、X/Y/Z和单位符号是数据，保留原值。枚举/field标识不直接成为操作员文字；参数面板用下列Param标题+原字段标识+Unit/来源/生效值，通用NumericText先列Frame规则，再固定数字字段及§4 AlgorithmLimits，固定顺序不反射猜中文。

CG001–020的MessageKey固定为`Error.CGnnn`，下表覆盖§6全部恢复，不显示异常.Message。重复资源定义为构造错误；软件细分Diagnostic.MessageKey统一用`DiagnosticDetail`通用资源投影原安全Details，已知EmptyNoUncertaintyTarget/CovarianceSymmetrized/NumericallySemidefinite/BoundaryUncertain/NumericalNonConvergence加对应固定文字。它们不改ErrorCode、成功/失败或codec。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| SourceFrame | 源坐标系 | 來源座標系 | Source frame |
| TargetFrame | 目标坐标系 | 目標座標系 | Target frame |
| CoordinatePath | 坐标路径 | 座標路徑 | Coordinate path |
| OriginalItemIndex | 原项序号 | 原項序號 | Original item index |
| SourceValue | 源值 | 來源值 | Source value |
| TargetValue | 目标值 | 目標值 | Target value |
| Unit | 单位 | 單位 | Unit |
| State | 状态 | 狀態 | State |
| Identity | 身份 | 識別 | Identity |
| Axis | 坐标轴 | 座標軸 | Axes |
| ValidDomain | 有效域 | 有效範圍 | Valid domain |
| Model | 变换模型 | 轉換模型 | Transform model |
| Source | 来源 | 來源 | Source |
| Parameters | 参数 | 參數 | Parameters |
| Raw | 原始值 | 原始值 | Raw values |
| Canonical | 标准坐标 | 標準座標 | Canonical coordinates |
| Display | 显示坐标 | 顯示座標 | Display coordinates |
| NoGraph | 未加载坐标图 | 未載入座標圖 | No coordinate graph is loaded |
| Empty | 无几何项 | 無幾何項 | No geometry items |
| Stale | 快照已失效，请刷新 | 快照已失效，請重新載入 | Snapshot is stale. Refresh it. |
| Accepted | 计算已接纳 | 計算已受理 | Calculation accepted |
| Validating | 正在检查输入 | 正在檢查輸入 | Checking input |
| Executing | 正在计算 | 正在計算 | Calculating |
| Draining | 正在等待计算停止 | 正在等待計算停止 | Waiting for calculation to stop |
| Drained | 计算已停止，正在归还资源 | 計算已停止，正在歸還資源 | Calculation stopped. Releasing resources. |
| ResourcesReleased | 资源已归还 | 資源已歸還 | Resources released |
| Completed | 计算完成 | 計算完成 | Calculation complete |
| Rejected | 输入已拒绝，请查看诊断 | 輸入已拒絕，請查看診斷 | Input rejected. Check diagnostics. |
| Cancelled | 计算已取消 | 計算已取消 | Calculation cancelled |
| TimedOut | 计算超时，请查看原操作 | 計算逾時，請查看原操作 | Calculation timed out. Check the original operation. |
| Failed | 计算失败，请查看诊断 | 計算失敗，請查看診斷 | Calculation failed. Check diagnostics. |
| WaitExpired | 等待已结束，请查询原操作 | 等待已結束，請查詢原操作 | Waiting ended. Check the original operation. |
| WaitCancelled | 已停止等待，计算可能仍在运行 | 已停止等待，計算可能仍在執行 | Waiting cancelled. Calculation may still be running. |
| NotFound | 原实例中找不到此操作 | 原執行個體中找不到此操作 | Operation was not found in the original instance |
| HostRefreshUnavailable | 宿主未提供快照刷新 | 宿主未提供快照重新載入 | Host snapshot refresh is unavailable |
| TableOnly | 此几何仅显示数值 | 此幾何僅顯示數值 | Numeric view only for this geometry |
| DisplayCount | 显示{0}/{1}项，完整结果保留 | 顯示{0}/{1}項，完整結果保留 | Showing {0}/{1} items. Full result is retained. |
| DiagnosticDetail | 数值或来源说明，请查看明细 | 數值或來源說明，請查看明細 | Check the numeric and source details. |
| NotProvided | 未提供不确定度 | 未提供不確定度 | Uncertainty is not provided |
| NotEvaluated | 未评估不确定度 | 未評估不確定度 | Uncertainty is not evaluated |
| Propagated | 已传播输入不确定度 | 已傳播輸入不確定度 | Input uncertainty propagated |
| FirstOrderLocal | 仅局部一阶传播 | 僅局部一階傳播 | Local first order propagation only |
| EmptyNoUncertaintyTarget | 空输入没有传播目标 | 空輸入沒有傳播目標 | Empty input has no propagation target |
| CovarianceSymmetrized | 协方差仅在计算副本中对称化 | 共變異數僅在計算副本中對稱化 | Covariance was symmetrized in the calculation copy only |
| NumericallySemidefinite | 协方差在数值容差内，原值保留 | 共變異數在數值容差內，原值保留 | Covariance is within numeric tolerance. Original values are retained. |
| BoundaryUncertain | 无法可靠判定域边界 | 無法可靠判定範圍邊界 | Domain boundary cannot be determined reliably |
| NumericalNonConvergence | 数值求解未收敛，未返回结果 | 數值求解未收斂，未回傳結果 | Numeric solution did not converge. No result was returned. |
| Param.FrameRules | 逐坐标系数值规则 | 各座標系數值規則 | Numeric rules per frame |
| Param.AxisScales | 各轴数值尺度 | 各軸數值尺度 | Numeric scale per axis |
| Param.BoundaryGuard | 域边界保守带 | 範圍邊界保守帶 | Conservative domain boundary band |
| Param.MaximumCoordinateMagnitude | 坐标幅值上限 | 座標幅值上限 | Coordinate magnitude limit |
| Param.MaximumConditionNumber | 条件数上限 | 條件數上限 | Condition number limit |
| Param.MinimumDenominatorRatio | 局部分母安全比下限 | 局部分母安全比下限 | Minimum local denominator safety ratio |
| Param.OrthogonalityTolerance | 正交数值容差 | 正交數值容差 | Numeric orthogonality tolerance |
| Param.CovarianceTolerance | 协方差数值容差 | 共變異數數值容差 | Numeric covariance tolerance |
| Param.InverseResidualTolerance | 逆残差数值容差 | 逆殘差數值容差 | Numeric inverse residual tolerance |
| Param.AlgorithmLimits | 数值算法限额 | 數值演算法限額 | Numeric algorithm limits |
| Param.PathLimits | 路径搜索限额 | 路徑搜尋限額 | Path search limits |
| Param.RuntimeLimits | 运行资源限额 | 執行資源限額 | Runtime resource limits |
| Param.ExecutionBudget | 本次执行时限 | 本次執行時限 | Execution time budget |
| HalfPixelTip | 像素中心与角点约定不同，请核对来源 | 像素中心與角點約定不同，請核對來源 | Pixel center and corner conventions differ. Check the source. |
| DisplayOnlyTip | 缩放和镜像仅影响显示，物理结果不变 | 縮放與鏡像僅影響顯示，物理結果不變 | Zoom and mirror affect display only. Physical results stay unchanged. |
| CancelTip | 取消后须等待原计算停止和资源归还 | 取消後須等待原計算停止及資源歸還 | After cancellation, wait for calculation to stop and resources to be released. |
| MissingResource | 语言资源不完整，保留原语言 | 語言資源不完整，保留原語言 | Language resources are incomplete. Previous language is retained. |
| Error.CG001 | 输入格式无效，请修正后新建请求 | 輸入格式無效，請修正後建立新請求 | Invalid input format. Correct it and submit a new request. |
| Error.CG002 | 版本或引用不匹配，请绑定明确修订 | 版本或參照不符，請綁定明確修訂 | Revision or reference mismatch. Bind the exact revision. |
| Error.CG003 | 单位或维度不匹配，请检查坐标链 | 單位或維度不符，請檢查座標鏈 | Unit or dimension mismatch. Check the coordinate chain. |
| Error.CG004 | 几何超出有效域，请检查支持范围 | 幾何超出有效範圍，請檢查支援範圍 | Geometry is outside the valid domain. Check its support. |
| Error.CG005 | 变换不稳定或无效，请检查模型和数值策略 | 轉換不穩定或無效，請檢查模型與數值策略 | Transform is unstable or invalid. Check the model and numeric policy. |
| Error.CG006 | 缺少有效数值策略，请提供明确配置 | 缺少有效數值策略，請提供明確設定 | A valid numeric policy is required. Provide an explicit configuration. |
| Error.CG007 | 已超资源限额，请检查输入和预算 | 已超資源限額，請檢查輸入與預算 | Resource limit exceeded. Check input and budget. |
| Error.CG008 | 计算已取消，请查看原回执 | 計算已取消，請查看原回執 | Calculation cancelled. Check the original receipt. |
| Error.CG009 | 计算时限已到，请查看原回执 | 計算時限已到，請查看原回執 | Calculation deadline reached. Check the original receipt. |
| Error.CG010 | 执行失败，请保留诊断后处理 | 執行失敗，請保留診斷後處理 | Execution failed. Retain diagnostics before recovery. |
| Error.CG011 | 无法查询状态，请继续查询原实例 | 無法查詢狀態，請繼續查詢原執行個體 | Status is unavailable. Continue checking the original instance. |
| Error.CG012 | 服务已停止接纳，请等待旧实例归还资源 | 服務已停止受理，請等待舊執行個體歸還資源 | Service no longer accepts work. Wait for the old instance to release resources. |
| Error.CG013 | 尚未确认资源归还，请保留原实例 | 尚未確認資源歸還，請保留原執行個體 | Resource release is unconfirmed. Retain the original instance. |
| Error.CG014 | 请求身份冲突，请保留原请求并使用新身份 | 請求識別衝突，請保留原請求並使用新識別 | Request identity conflict. Retain the original request and use a new identity. |
| Error.CG015 | 找不到坐标路径，请更新坐标图 | 找不到座標路徑，請更新座標圖 | No coordinate path was found. Update the coordinate graph. |
| Error.CG016 | 坐标路径有冲突，请指定路径或更新坐标图 | 座標路徑有衝突，請指定路徑或更新座標圖 | Coordinate paths conflict. Specify a path or update the graph. |
| Error.CG017 | 后端不支持此模型，请检查能力声明 | 後端不支援此模型，請檢查能力宣告 | Backend does not support this model. Check its capabilities. |
| Error.CG018 | 模型或用途证据不可用，请检查明确资产 | 模型或用途證據無法使用，請檢查明確資產 | Model or use evidence is unavailable. Check the exact asset. |
| Error.CG019 | 不支持此几何表示，请明确选择可用表示 | 不支援此幾何表示，請明確選擇可用表示 | Geometry representation is unsupported. Explicitly select a supported representation. |
| Error.CG020 | 不确定度证据不足，请补齐输入和局部有效域 | 不確定度證據不足，請補齊輸入與局部有效範圍 | Uncertainty evidence is incomplete. Provide the input and local validity domain. |

模型名显示采用`Model`标题和原稳定type tag，单位符号按§3.1为px/nm/μm/mm/m/rad；不翻译成另一个身份。Raw/Canonical/Display层只改变投影视图；工作模式用原Host用途资源，不显示合格/PASS。参数明细中各AlgorithmLimits/Path/Runtime子项原标识可复制，标题资源采用相应Param组，单位固定counts/bytes/time并以`Unit`投影，不将未解释异常/内部对象直接呈现。

## 12. 合成数学反例与明确预期

下表全部是软件定义夹具，不能给客户精度/节拍赋值。数值策略的算法安全参数由测试夹具显式给出；物理验收另见§19。

| 反例 | 输入/操作 | 必须预期 |
|---|---|---|
| 组合 | (1,2)先平移(3,4)再scale2 | (8,12)；反序为(5,8)；结果差异抓出左/右乘错误 |
| SI/协方差 | x=1 mm，variance=0.01 mm²→μm→mm | x=1000 μm，variance=10000 μm²→原值；不得二次换算 |
| 半像素 | §8.1中心scale2，(2,3) | 合法两桥均(4,6)；错误直传得到(4.5,6.5) |
| crop/resize | crop原点(100,20)，resize extent s=2 | crop(0,0)→(100,20)；resize中心0→0.5，不是0 |
| 向量/法向 | A=diag(2,1)，v=n=(1,1)，任意平移 | v=(2,1)；单位n=(1/√5,2/√5)；平移无效 |
| 圆变形 | 单位圆经diag(2,1) | Ellipse基diag(2,1)；不能Circle半径1.5 |
| 显示/翻面 | Display镜像X与3D绕Yπ | det分别-1/+1；不得共享物理边或改变宿主稳定身份 |
| 多边形洞 | 外环方形[-2,2]²，洞[-0.5,0.5]²；线(-1,0)→(1,0) | 两端合法但线穿洞，CG004；只查顶点的实现失败 |
| 投影无限 | H第三行为(1,0,1)，线x∈[-2,0] | w=x+1跨0，CG005；不能仅映射端点成功 |
| 条件数 | A=diag(1,10^-12)，策略上限小于10^12 | det≠0仍CG005；不能默认伪逆 |
| 协方差相关 | y=x+t，Varx=Vart=1，Cov(x,t)=0.5 | Vary=3，不是独立假设的2；缺交叉块Required为CG020 |
| 未知同帧 | 不存在帧A，source=target=A | CG002/缺帧诊断，不返回identity |
| 多路径 | A→B→C与A→C，同精确图两条合法路径 | ResolveUnique CG016；显式路径分别可算，CheckConsistency仅证明指定probe |
| 搜索预算 | 有路径但超过MaxGraphVisits才可发现 | CG007，不能MissingPath/Completed；显式短路径按其自身预算可运行 |
| 局部场折叠 | 两个source位置映射同target，local det各处非零 | 不自动开逆；ProvidedInverse缺唯一性证据拒绝 |
| 平面/相机 | world点先camera←world；未知Z像素 | 前者可按§8投影，后者仅已声明平面路线可算，不返回猜测3D |
| 可选误差 | 几何可算，未提供covariance/线性化域 | Optional返回NotProvided/NotEvaluated，Required CG020；不能零不确定度 |

圆二次型可手算：`K=[[I,-c],[-cᵀ,cᵀc-r²]]`，Ellipse则用`Q=(B*Bᵀ)^-1`替换I并相应调整c项；projective `K'=H^-T*K*H^-1`，整体非零scale不改变曲线。几何表示比较必须按参数曲线/归一二次型等价，不逐元素要求原矩阵相同。矩阵缩放、环绕序、角区间均要独立反例，不能只靠随机图“看起来对”。

## 13. 分层验收矩阵与故障注入

所有断言同时检查结果与未发生的副作用；文档校验、合成数学、Mock/Simulator、真实库Golden、真实消费者和客户现场分别计门。Mock不能冒充HALCON排空或相机标定资格。

| 层/场景 | 输入与故障 | 可判定断言 |
|---|---|---|
| 单位/轴/数值Core | §12固定反例、不同单位/换轴、非有限/溢出/近奇异 | 值与独立手算一致、明确CG001/003/005，无二次比例/暗换轴 |
| 几何/域Core | box边界、polygon洞/自交、跨洞线、反射、圆→ellipse、projective跨无穷远 | 全几何域检查；结构/索引保留；不以点采样代替连续域证明 |
| 图Core | 空图/缺引用、同Ref不同内容、环、显式逆、两条路径、搜索限 | 无自动identity/latest；未搜完CG007；显式路径不受邻接加载顺序影响 |
| 协方差Core | 完整联合块、相关交叉项、非PSD、缺误差/导数、单位转换 | §3.4公式一致；Required拒绝、Optional明确缺失，无残差替代不确定度 |
| 正常生命周期 | 正常Map与ValidateGraph、空Items | 一次Accepted/唯一终态，ResourcesReleased在终态之前；空输入仍验证路径但无native点调用 |
| 接纳前拒绝 | token已取消、服务停止、版本/字节/并发/保留超限 | 无Accepted/资源记录/墓碑；原输入未被模块持有；正确短拒绝错误 |
| 接纳后拒绝 | 第n项域外、非法模型/Frame、Policy缺失 | Validating后Draining/释放/Rejected；无消费结果，首失败索引确定 |
| 重复/冲突 | 同ID同快照；同ID改一点但伪造相同声明hash | 前者一次计算/同回执；后者CG014、原状态/结果不变 |
| 并发 | 两请求不同图/Policy；一取消，另一正常 | 服务级额度不被请求提高，状态/序号/缓存隔离；无隐式队列 |
| 取消/期限竞争 | 在接纳前、验证中、边间、native前后、成功提交点注入 | 原因在一次线性化点冻结；终态后取消不改Completed；迟到结果不发布 |
| 等待/计算分离 | Wait token取消/WaitBudget到期，计算仍运行 | WaitCancelled/WaitExpired；计算状态不改，CancelAsync才发运算取消 |
| 排空未知 | 假端口仍使用缓冲、Dispose抛错、native未返回 | State Draining/Drain Unknown；不Drained/释放/终态，不卸载适配器 |
| 查询 | 已知活动、终态墓碑、确不存在、源读取故障 | 分别Found、Found、NotFound、Unknown；实例ID不可串用 |
| 关闭 | 活动中Stop，两个观察者等待，第一次等待到期 | 停止接纳不撤销、旧请求被跟踪；再次Stop等同批；Confirmed后才卸载 |
| 事件 | 订阅晚到、慢观察者、进度丢失、订阅取消/读取失败 | 生命周期重放和终态唯一；进度可有gap；观察者不阻塞/取消计算 |
| 后端 | ManagedCore与HALCON合法桥；native异常/模型不支持 | 后端固定，失败不静默换算；算子、输入hash、版本/资源可追溯 |
| LocalField | cell洞、grid边界、导数不连续、折叠/多根 | 只支持声明方向/点能力，缺逆唯一性拒绝，连续几何不采样伪认证 |
| 相机 | pose方向/单位错、已校正与原图混用、离面/未知Z/线扫模型 | 精确Frame/资产绑定，模型限制拒绝，不创造质量资格 |
| UI | 三语/长文本、键盘/UIA、选中/排序/筛选、Display镜像、Drain Unknown | 仅1920×1080基线；显示不改canonical，关闭投影不Stop宿主服务 |
| 两消费者 | §10同包同图，ROI UI与无UI计量分别独立引用 | 无Shell/私库/页面依赖，无跨消费者取消/配置污染，无隐式质量提交 |
| 版本/回退 | 固定旧快照在旧包重放，新包语义变化，不兼容主版本混用 | 旧输入/结果只读；明确拒绝不兼容；Drain后切换，回退不重算旧身份 |

测试的必要独立真值：组合/半像素/法向/单位/协方差用手算或固定外部参考；域洞/无限点用构造反例；图用已知路径集合；取消/期限用TimeProvider与受控端口闸门。不能用同一产品函数产生期望值再测试自己。随机覆盖须固定seed、记录失败夹具，不用随机成功替代边界断言。真实HALCON Golden必须与同一图/策略、合法桥和资源观测绑定；当前尚无该运行证据。


### 13.1 net10.0 BCL Exe的落点、真实命令与有限截止

按DEV-GOV-010 §3.1约定：唯一Core.Tests为`Microsoft.NET.Sdk`、TargetFramework=`net10.0`、OutputType=`Exe`、Nullable/ImplicitUsings=enable；仅ProjectReference本模块Core，使用BCL确定性断言/自定义TimeProvider/TaskCompletionSource异步闩锁，不引待选测试包。该工程此轮**尚未创建**；下列是实施接收后真实执行命令，不是本轮执行记录。仅修改允许工程，不为本次文档创建测试代码或临时工程。

命令从仓库根目录执行，以下工程路径均相对仓库根。外层启动器的`ProcessStartInfo.WorkingDirectory`显式设为本次检出的仓库根（`<repo-root>`由宿主/CI绑定），不固定本机目录或依赖继承的工作目录。

```powershell
dotnet build src/Modules/coordinate-geometry/Asun.Modules.CoordinateGeometry.Core/Asun.Modules.CoordinateGeometry.Core.csproj -c Release
dotnet run --project tests/Modules/coordinate-geometry/Asun.Modules.CoordinateGeometry.Core.Tests/Asun.Modules.CoordinateGeometry.Core.Tests.csproj -c Release -- --suite core-all --case-timeout-ms 10000 --run-timeout-ms 120000
```

Exe入口冻结参数：`--suite core-all`执行下面全部组，不接受生产阈值/真实硬件；`--case-timeout-ms`/`--run-timeout-ms`有限正int（必填）。错误参数/缺必需组exit2；断言失败、异常、未知Drain、任务未结束或任何必需skip exit1并打印case ID、seed、阶段/期望/实测与未确认资源；全部必需完成且归还exit0。一项失败仍在全局剩余预算内继续独立组以收集明确失败，不能因catch异常或只跑了一个组exit0。测试runner在每例截止到时取消其**测试控制任务**并记录failure，需按原service/port协议Drain；闩锁未解/清理不确认也failure，不能跳过直到“成功”。异步闩锁用RunContinuationsAsynchronously，不依赖sleep/timingrace。

外层构建/启动的有限进程截止也必须实设；例如PowerShell使用System.Diagnostics.ProcessStartInfo（UseShellExecute=false、ArgumentList逐项加参数）启动dotnet，每个build/run最多180000ms，stdout/stderr分别BeginRead/ReadToEndAsync避免管道阻塞；`WaitForExit(180000)==false`仅对该test process调用`Kill(entireProcessTree:true)`，标HARNESS-PROCESS-TIMEOUT且整次非零。这是测试runner隔离进程的硬截止，**不是生产native取消手段**；必须列出尚未确认的资源/样例，不宣称Drain成功。实际CI同样设置180s且保存退出码。不能用Start-Process可见窗口或dotnet test空执行代替。Core-test进程无设备/native，HALCON/WPF组另用其真实工程和更适用有限测试Profile接收，不能把mock证明移花到真实库。

| 必需组/ID前缀 | 固定断言（全组执行，不只首片） |
|---|---|
| CGT-API | §4.3全公开叶类型/enum范围、matrix shape/null/default、factory零IO/零工作、显式单位/域、hash二进制编码/-0/自Ref排除/拒绝NaN、无caller hash信任、两消费者无UI引用 |
| CGT-MATH | §12全部手算值；SVD重构/排序/U/V/双侧inverse/近限certificate拒绝，正向/逆/PlaneLift单位尺度还原与projective chart |
| CGT-DOMAIN | box Closed/Open/HalfOpen边界、exact近共线/反向orientation、collinearOverlap、zeroSegment、selfIntersect、线穿洞/区域包含域洞、ring winding与guard距离；整Plane到有限域拒绝 |
| CGT-CURVE | Circle→Ellipse、reflection弧参数、Conic D与K区分、W双根/跨0、安全带、circle相切Closed/Open、穿小洞、curve包含/恰在支持线、arc跨π/端点根；Sturm重根与零多项式，根/位长/系列预算耗尽拒绝 |
| CGT-DENOMAIN | §4.4 CGE-01–12全域分母证据、witness/来源/预算/两门区别；新增切片实施后加入core-all，不以旧四个Core接收冒E已执行 |
| CGT-GRAPH | exact帧/edge冲突、未知同帧、显式empty identity、环/双路、按ordinal确定性、ProvidedInverse/逆域、Unique未搜索完CG007、Probe仅见证非全域、未用模型端口不能阻全图结构验证 |
| CGT-COV | PSD rank-deficient/negative/zero pivot nonzero行、symmetrize诊断/原hash不改、S+τI仅诊断不clip；混合参数量纲/Jacobian/3的相关方差、路径重用同参数不双加、Required缺导数/局部域拒绝 |
| CGT-LIFECYCLE | 正常/空/接纳前短拒绝/接纳后错误；duplicate/不同内容相同hash冲突；并发固定限额/操作隔离；取消及deadline每检查点、terminal线性化race；WaitExpired/WaitCancelled不改计算 |
| CGT-DRAIN | native替身/Dispose失败、Found+Drain Unknown vs Lookup Unknown、进度合并/可靠terminal replay、慢subscriber不阻、重复Stop等待同批/查询墓碑/迟到结果隔离；有限截止内无资源未归还 |
| CGT-MODEL | BCL外部backend替身值协议：cell/洞/边界/解析J/折叠逆拒绝、Capabilities/不支持表示/证据和RemainingBudget、InvocationId/Drain一致；明确不是真HALCON/camera测试 |
| CGT-VERSION | 旧/新版本混用拒绝、hash规约/参数revision变更新身份、Stop/epoch轮转、old实例NotFound不能覆盖旧unknown、两个消费者Replay同值并发隔离 |

固定seed=`0x00720261009`只用于附加随机覆盖；全部固定case先运行并输出必需ID，不把随机seed当唯一真值。构造反例额外冻结：orientation点(0,0),(1,1),(1,1+2^-52)必须+1，交换前两点=-1；Sturm `f=(z-1)²*(z+2)`有两个distinct根且重数2/1，`z⁴+1`无实根，zeroPolynomial为overlap；PSD `[[1,1],[1,1]]`接受rank1，`[[0,1],[1,0]]`拒绝；trig t=0严格sin0/cos1；曲线相切不得用只看变号判无根。SVD/Jacobian代码不能自己生成期望，使用解析固定矩阵/几何与exact理性参考；finite difference只作**测试诊断**在远离chart/域边界时对解析导数交叉核对，不进入生产算法。

初始执行软件测试Profile固定MaxConcurrentOperations=2、MaxRetainedOperations=256、MaxItems=4096、MaxVertices=8192、MaxFrames=64、MaxEdges=128、MaxInputBytes/ResultBytes=16MiB、MaxWorkingBytes=64MiB、MaxExecutionBudget=2s（由受控TimeProvider推进），AlgorithmLimits=(128,65536,1000000,512,2048,256)。NumericPolicy正常组用每轴Scale=1、ConditionMax=10^8、DenominatorRatio=10^-8、OrthogonalityTolerance=10^-10、InverseResidualTolerance=10^-10、CovarianceTolerance=10^-12、BoundaryGuard=0、CoordinateMagnitude=10^6、PathDepth=64、Candidates=32、Visits=4096；边界组显式单字段变更（如ConditionMax=10^13验证近奇异certificate、guard=10^-6验证保守带、各budget调小制造耗尽），所有变化新Policy Ref。以上数字是**合成软件测试配置**，不默认生产参数、不宣称光学精度/节拍/客户验收。

### 13.2 CG-Halcon/CG-Wpf装配与双Host定向断言（未运行）

本轮只给随后允许切片的验证用途，复用原Core/数值/编码/Golden，不创建测试/报告。对应Halcon.Tests与Wpf.Tests工程均仍计划落点；fixture使用§10.1软件预算和§13.1有限runner语义，不把2s当真实吞吐或客户节拍。失败/skip/未知归还非零，Synthetic CAL/Viewport端口只证明消费协议，真实HALCON/WPF/资源门另报。

| ID | 定向输入/实际调用 | 必须断言 |
|---|---|---|
| CG-HOST-01 装配 | §8.3两Factory、原§11.4两InspectorFactory；空Cameras/null/未知cap/错Frame/越预算/parent冲突 | Create零IO/native/计算、拒绝无启动；限额耗尽在factory/Dispatcher/端口任务前拒绝，根有cleanup保留槽 |
| CG-HOST-02 只读解参 | 上游CAL §9.3.4完整Synthetic Read/codec/Store/资格，不调用solver；改format/hash/ExpectedSolvedRef/原模型/单位/Use | .010/.00002保持且不读initial/Reference；仅ResourcesReleased/Applicable成功，原Asset/string Revision/Device/q/watermark完整；LineScanRow0Projection不能用作plane；Unknown未伪造snapshot |
| CG-HOST-03 camera边界 | 各CameraRoute字段联合、反pose/非rigid/单位二次转换/crop未有链/原域外/水位过期/用途或曝光不符 | Create/调用前明确拒绝，不重新求解/射线备用/绕过域；真实plane/world/project依同已冻结§8算子Golden及独立样本，未知Z不造3D；Optional/Required不确定度沿原规则 |
| CG-HOST-04 两Host独立 | A/B矩阵真实backend同§10已接收值，A Cancel/Close/Profile/文化变动，B继续原Task | 两者(8,12)mm、原hash不变、无跨instance/ID污染；纯Managed与真实cv2分别执行，不以替身标HALCON通过 |
| CG-HOST-05 原Task恢复 | Read/Submit/native/Present/Dispatcher/Stop/Dispose受控闩锁迟到，观察token/截止到期、业务抛异常及cleanup同时异常 | 原Task/ID/Owner/依赖仍强持；只Query/等原过程，唯一Dispose/Clear链，迟到关门后不发布；原业务错误保留，2×2s未知不退根/不无限重试 |
| CG-HOST-06 STA/null-display | 两独立STA分别Create/Bind/SetCulture/SetHostTheme/Close；B另noUI模式 | 原§11.4成员准确调用，无隐藏窗口/noUI无Wpf引用；三语/完整键/UIA/键盘/1920×1080长文和状态可用；Bind不Submit，Close不Cancel/Stop服务 |
| CG-HOST-07 借用显示 | root/factory/ViewportControl.Bind空UI→Attach→本层SetLayers→真实Presentation→Clear→归借用→外层Unbind/Session.Dispose/root.Close | Context/权限/两generation绑定准确；本层原缓存0与上游Presenter借用分开，VisibleConfirmed不冒Drain；不抢Parent、不删B层、不Dispose共享session；借用生命周期由原Owner确认 |
| CG-HOST-08 撤权/退出 | 授权expiry/Changed在Submit/Present/Dispatcher入队后，Dispatcher提前shutdown、Root转交未确认、Clear/Return异常 | 禁新命令/投影、旧结果屏蔽且原操作仍恢复；无假无权限成功，无Detached/外层Task完成冒释放；移交未确认原根仍在，正常关闭先真实收敛再退Dispatcher |

Benchmark只增装配/参数Read/Host-root预留、overlay封存、Viewport实际可见、Clear/Return与根Pending强持的测点；原§14分位/失败/删失统计复用。记录两Host实际托管/native/显示/Presenter/上游资源账本两轴峰值、并发与处于未知的字节，逻辑ChargedBytes或ArrayPool.Return不当private bytes退款。没有消费者采纳目标标NotEvaluated，不编造误差/曝光/节拍门。

## 14. 参数、数值安全、运行预算与性能评价

### 14.1 三类策略分开

| 类别 | 参数/单位/范围与来源 | 缺失后的行为 |
|---|---|---|
| 软件数值安全 | §4 NumericPolicy；尺度按帧轴单位、条件数无量纲、齐次比无量纲、域guard为对应域单位、正交/协方差相对容差无量纲 | 必填字段/适用项缺失CG006；由Core技术Owner明确选择/测试，不等待客户节拍/精度 |
| 运行限额 | §4 RuntimeLimits + ExecutionBudget；items/vertices/frames/edges整数、bytes字节、时间TimeSpan | 构造服务时必须给定；缺失不启动；服务只拒绝超限，不自动抬限/排队/分块 |
| 物理/质量评价 | 标定支持域、平面/深度、全域路径一致性/线性化证据、客户精度/计量/性能目标 | 缺失仅阻断确实依赖该事实的物理切片；纯Core可运行；性能结果NotEvaluated，不填来源不明数值 |

所有Policy变更产生新Ref/hash、新RequestId；不能动态修改在途请求/生产参数。没有自动参数训练/建议引擎；UI只解释生效参数来源，不从历史成功数据自动放宽。

NumericPolicy中尺度、坐标幅值按每个实际帧声明；图的中间边也必须覆盖。BoundaryGuard为对应帧单位的保守不确定带，不是客户允收容差；数值上限/分母比/正交与PSD容差由技术Owner按double范围和固定反例冻结，公开物理精度不能反推“更宽松就合格”。曲线/多边形证明、SVD条件数与协方差固定路线和停止判据见§3.5–3.8；这些内部技术项已冻结，不交编码者临时选库/算法。

预算从接纳前封存预估开始管理：长度计数 checked，快照/工作缓冲/结果/图遍历结构/可靠生命周期回执分别预约；预约失败在分配前拒绝。无法准确界定上界的外部工作区必须由模型端口提供其资源预算及确认释放，缺失不准入。MaxResultBytes预估不足造成执行超限时CG007 Failed，已有诊断不当部分成功。System.OutOfMemoryException等进程级故障不能承诺可恢复；进程重启对原请求只报告外部未知，不推断成功或自动重放。

### 14.2 BenchmarkProfile

统计口径唯一按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)；本文不复制分位算法。Profile冻结模块/API/backend/资产/输入/数值策略hash、OS/CPU/runtime、输入负载、并发、冷/热/预热、测量次数/最低有效样本、有限deadline、资源上限、阶段测点、目标来源与失败处理。无已采纳性能目标只允许诊断测量并标NotEvaluated，**不阻断无关Core规格/实现接收**。

模块专属负载维度：2D/3D；点/线/曲线/多边形/洞/协方差；items/vertices；图frames/edges/深度/候选路径数/有环；Explicit/Unique/Consistency；输入/中间/目标域命中与拒绝；近奇异/近无限；空输入；后端、localfield网格/洞；相机模型；重复ID比例；并发/在途保留/epoch轮转；observer数量/进度频率。

测点：接纳封存/身份计算、图校验、路径、每边/域、native/模型端口、误差、结果构造、Draining、Drained、ResourcesReleased、端到端至释放；单独记录取消/到期→真实停止/归还及Wait时长，不把WaitExpired当计算结束。资源计数包括托管/私有字节、输入/结果/工作缓冲、native租约、遍历节点、回执/缓存水位。所有失败/超时/删失/未排空样本保留，Drain Unknown不判性能通过。长稳时长/吞吐和客户目标待消费者Profile采纳，不把24h或5s写为工程默认。

### 14.3 默认、建议与软件参数责任

**全范围裁决：本模块不含自动拟合、训练或生产参数推荐引擎。** 架构职责是消费已冻结坐标/参数并给数值与失败证据，拟合/标定/局部场发布分别由Alignment/Calibration/宿主坐标资产Owner负责；不能把用户对有边界自动参数的通用要求解释成必须新造一个调参模块。现有参数自动化为确定的单位/名称模板生成、参数合法性/资源预估与拒绝诊断，执行路径按显式模型/能力选定，结果不写生产配置。

| 参数族 | 默认/可用建议规则及来源 | 采用、过期和恢复 |
|---|---|---|
| Frame/模型/参数表 | 无隐式Frame、单位、pose/plane或模型；§3/4.3.1–2/8.4/9.1.1按显式模型生成Name/Unit/顺序模板；Scale逐项由Host技术配置给定 | 名称模板不含新参数值或质量结论；原Graph/Field/资产变更必须新Ref/精确封存，不能“自动修正”偏移/镜像/角点 |
| NumericPolicy | 必填，无factory默认。原§13.1正常/边界组是唯一合成软件基线，技术Owner可**显式复制并冻结**到自己的软件Profile；每轴Scale/guard/coordinate bound按实际Frame单位，不按相机像素值猜物理精度 | 新输入与Profile不匹配先CG006/003；证书/域/误差失败给原诊断，不放宽阈值救结果。不更新在途Policy；技术Owner批准的新值用新Ref/hash/RequestId |
| 相机/局部场参数 | CAL原已解tuple与§9.2.1绑定，不用InitialParameters；局部场节点/Base与完整§9.1.1参数表原样消费 | 当前资格水位/用途到期CG018；新读取/发布版本形成新epoch；没有自动TTL、重拟合或牛顿逆。允许无物理证据的Synthetic仅软件模式 |
| Runtime/Host/display | 必填限额；§10.1–2/13.1与§9.1.2均是具名软件Profile，不作生产节拍/资源默认。请求预算取原期限剩余与本入口上限较小者，不反向扩限 | byte/count预测失败或MaxWorking/结果不足CG007，显式由Host选更小输入或新批准Profile。显示抽稀只改变Projection，不改canonical；关闭额度独立且先预留 |
| 物理与生产验收 | 全无默认；精度/节拍/可见深度/有效域/标定与线性化质量取准确Owner Profile/证据 | 只有确实依赖这些事实的请求阻断；纯数学/单位/无图像Inspector继续软件验证。Profile缺性能目标只NotEvaluated，不编造达标数 |

说明性诊断可包含当前参数名/值/单位/来源、实际支持域/输入索引、失败安全边界与哪项需Owner批准，但不生成“建议放宽至X”的默认按钮。参数导出/保存/生产激活不属于Inspector，Host需要时走自己的编辑/批准事务；本地模型/Policy版本算法及§4.2 codec保持。软件参数技术Owner是IM-007，真实输入值/用途是消费者坐标资产Owner，性能目标是消费者BenchmarkProfile Owner，责任不能混交编码人员。

## 15. 诊断、审计与数据保留

操作证据最小集合：ServiceInstanceId/RequestId、输入hash、Graph/Frame/Edge Ref、路径方向、单位/像素/轴约定、NumericPolicy/Backend版本、阶段/错误、失败索引、取消原因、时钟/Drain/释放。QualityRef仅透传外部身份。日志不保存原图/客户目标/SDK句柄/任意异常栈中的秘密；需要详情由宿主明确受控诊断端口处理。

错误、身份/路径冲突、域拒绝、取消、Drain Unknown和终态不可静默采样；进度可合并。结果Store、审计保留期、跨进程回执由宿主Owner负责，模块不创建第二数据库。进程重启不能确认旧活动请求的资源或结果；宿主保留原Request/epoch的未知记录并按自己的恢复协议对账，新计算另用新ID。损坏缓存只停止使用该缓存并从已有不可变快照重新验证，不能改原资产hash。

## 16. 版本、发布与回退

区分本地API版本、数值/域算法版本、HALCON/适配版本、资产与NumericPolicy版本。改变单位/轴/半像素/模型/域边界、公开类型/枚举、必填字段、hash规约、错误含义、取消/Drain/结果语义均为破坏性版本，升主版本并拒绝静默混用；诊断性可选输出扩展仅在不改变消费者判断时升次版本。本文0.2替代未接收的0.1是设计稿修订，不宣称存在已发布兼容包。

交付包以真实消费者为用途，至少附公开契约、依赖/后端版本、已运行的对应Golden/资源记录、变更和回退说明；不提前堆无消费者包/报告。只有已经运行的检查才列结果。升级先停止接纳→Drain旧实例→取回回执→卸载旧adapter→加载已接收新包→固定夹具回放→新epoch；失败恢复旧包/旧资产。Drain Unknown时停止升级，保留旧运行资源。回退不重写历史坐标、输入hash、旧回执或质量事实。

## 17. 整模块功能覆盖与接收顺序

| 能力切片 | 实施章节/结果 | 真实消费者/验收 | 依赖门 |
|---|---|---|---|
| CG-Core-A 值/单位/矩形/affine点及操作协议 | §3.1–3.2/4/6–7/10 | ROI点与无UI计量点；§12组合/SI/生命周期/并发 | 本地literal类型/构造及身份/运行策略Owner接收，实际Core构建/测试另验 |
| CG-Core-B 图/路径/组合/逆、2D/3D向量法向/线段 | §3.3/3.5–3.6/5/12 | ROI工程frame链、计量法向/物理线 | 固定Jacobi/逆证书及有界路径已给，后续按CGT-MATH/GRAPH验证 |
| CG-Core-C polygon/洞/曲线/conic连续域 | §3.2–3.3/3.6–3.7/12 | ROI polygon与计量圆弧/ellipse | exact谓词/Sturm全域证明已给，后续CGT-DOMAIN/CURVE及真实Golden；不能缩成顶点样点 |
| CG-Core-D 协方差/相关块/局部传播 | §3.4/3.8/4.3/12 | 计量不确定度、定位结果误差 | PSD/联合AD已给；客户局部线性化有效性仍需外部证据 |
| CG-Core-E 通用逐run全域分母证据 | §4.4 | 定位用途桥、ROI投影/拼接预检 | 主控已接收六项文档规格，ModuleCoreImplementationReady（仅规格准备）；真实oracle/接线未执行 |
| CG-Halcon | §8/9.2.1/10.1–2/13.2 | 视觉点/ROI/Cross-FOV物理坐标 | 自有Factory/Options及Camera Read准确消费的新增确定指导内容已限定接收；仍PreparationIncomplete/NotReady，真实HALCON/CameraRead接线、库桥/异常/释放Golden、性能及物理资格未验，不授适配产品准入 |
| CG-External | §9.1.1–2/9.2.1 | 相机平面/3D投影/畸变/localfield消费者 | 公开快照/工厂/参数/算法/逆场配对与Drain已定；真实资产、用途/唯一性/线性化证据由外部坐标资产Owner提供，物理资格仅相关请求 |
| CG-Wpf | §11.4/11.4.1/10.1–2/13.2 | ROI/工程工具内嵌Inspector | 复用既有Inspector声明，新增权限/Viewport精确消费与双STA/noUI Host确定指导内容已限定接收；仍PreparationIncomplete/NotReady，真实Viewport接线、WPF/显示/资源、性能及物理资格未验，不授适配产品准入 |
| CG-Integration | §10/13/16 | 两消费者分别无私有依赖接入/Replay | C-03产品映射与提交Owner、真实资产/Golden/性能/物理客户值 |

上表保持整模块范围，不把未完成的Core-B/C/D笼统搬到“以后”或删掉。首片从A开始是工程顺序；文档内容和接收结论逐能力列明。不得因首片单测通过声称其它能力、整个模块或平台准入。

## 18. 实读来源、版本与可迁移边界

### 18.1 当前权威与历史原件

架构/治理按 [独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)、[模块独立性](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)、[实施级标准](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。正式产品映射入口是 [C-03候选](../../13-contract-candidates/CONTRACT-CANDIDATES.md)，候选不授予质量/提交权限。

已复用 [PKG-007](../../shared-modules/packages/PKG-007_Coordinates.md) 与 [SM-008](../../shared-modules/modules/SM-008_coordinates.md) 的数学/坐标来源，以及 [DEV-VIS-020](<../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>)、[DEV-VIS-021](<../../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md>)、[DEV-VIS-024](<../../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md>)、[DEV-VIS-025](<../../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md>)、[DEV-VIS-029](<../../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md>)、[DEV-MET-030](<../../shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md>)、[DEV-MET-031](<../../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md>) 和 [DEV-UI-040](<../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)。历史PKG/SM不覆盖本文新状态/错误/API。

AsunControl只读参考 [Vision_CameraCalib](../../references/project-snapshots/AsunControl/20261004/original/Vision_CameraCalib/) 与 [ROI](../../references/project-snapshots/AsunControl/20261004/original/ROI/)：可借鉴Row/Col转换、参数来源与释放流程；其.NET8 WinForms、字符串颜色、无版本二进制序列化、bool/null错误和持有HALCON对象的业务模型不移入本模块；没有重新扫描其内部或复制产品实现。本轮仅修正文档，原件保留。

### 18.2 实际源码与测试阅读

| 来源/锁定版本 | 实读原件、依赖/许可 | 采纳位置与局限 |
|---|---|---|
| transforms3d **0.4.2**，commit `6a43a98e3659d198ff6ce2c90d52ddef50fcf770` | [affines.py](https://github.com/matthew-brett/transforms3d/blob/6a43a98e3659d198ff6ce2c90d52ddef50fcf770/transforms3d/affines.py)、[test_affines.py](https://github.com/matthew-brett/transforms3d/blob/6a43a98e3659d198ff6ce2c90d52ddef50fcf770/transforms3d/tests/test_affines.py)、[LICENSE](https://github.com/matthew-brett/transforms3d/blob/6a43a98e3659d198ff6ce2c90d52ddef50fcf770/LICENSE)、pyproject；BSD-2-Clause（LICENSE另列第三方例外）；Python≥3.6、NumPy≥1.15、setuptools/versioneer构建 | compose的rotation·scale·shear和反射/重构测试思想用于§3/12/13；不引Python/NumPy运行依赖、不复制源码。decompose形成AᵀA会平方条件数，不能作稳定逆判据；随机测试seed未冻结，不当生产证据 |
| ROS2 geometry2 / **tf2 0.36.0**，commit `4a46a8f090df5bf436d80f35bd3285adee06a448` | [buffer_core.cpp](https://github.com/ros2/geometry2/blob/4a46a8f090df5bf436d80f35bd3285adee06a448/tf2/src/buffer_core.cpp)、[simple_tf2_core.cpp](https://github.com/ros2/geometry2/blob/4a46a8f090df5bf436d80f35bd3285adee06a448/tf2/test/simple_tf2_core.cpp)、[package.xml](https://github.com/ros2/geometry2/blob/4a46a8f090df5bf436d80f35bd3285adee06a448/tf2/package.xml)；package标BSD、source头为BSD-3-Clause；ROS/ament、builtin_interfaces、console_bridge_vendor、geometry_msgs、rcutils等，gtest测试 | source/target方向、非法帧/NaN、环限制、缺帧/时间越域与row-major covariance反例用于§3/5/13。tf2是树/时间缓存，不是本模块多路径图；source==target可对未知frame返回identity、TimePointZero选latest，两者明确不继承。不引ROS运行依赖 |
| Microsoft .NET取消官方资料 | [Cancellation in managed threads](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) | §7协作取消、请求取消不等于工作停止；不推导HALCON/native能硬取消 |

本轮只阅读源/测试，没有运行上游测试；commit固定链接为只读原件定位，不另建研究报告。2026-10-09所读原始字节SHA-256：

| 原件 | SHA-256 |
|---|---|
| transforms3d/affines.py | `98b89ba3810fa2fbb5223fb483f532b352660396d82486d015a1dc062367fffe` |
| transforms3d/tests/test_affines.py | `2f7ddd2ff97553dc7769d5965ec165c17a5dc9dde4a44ab92802076cf0a06c6f` |
| transforms3d/LICENSE | `4e3e3231390bbccc3ed0cd6d9896b2876579614b2c6dd73730e4fa34d59856d0` |
| tf2/src/buffer_core.cpp | `287d5aeab7e44c7172d0c2a9c629c6c2d3aa932fbf9686f344948d6a2862f725` |
| tf2/test/simple_tf2_core.cpp | `5ed942cd3a327e58465517130fb631e99df9697db8c90de3c3da3f41e852efcc` |
| tf2/package.xml | `6050bedc35e8ae2cdd4d37e2d1c3ec4476758e83691c228c5d2ea7011dc1fcbc` |

### 18.3 DevExpress与HALCON资料的证据限度

已通过官方浏览器正文核对V25.2的 [DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[TreeListControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListControl?v=25.2)、[GridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl?v=25.2)、[PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)。采纳对应区域/联动/提示见§11，程序集使用本机25.2.3；网页当前NuGet patch不改变本机基线，不下载替换依赖。官网代码例摘录有自动采集局限，不证明本控件只读/键盘/Dispatcher行为已经实测。当前无dxdocs工具，不把缺该工具列成依赖许可门。

§8链接的本地HALCON页面标题为Operator Reference / Version26.05.0.0；实际读取Description/Execution得到row/column、半像素、pose/Scale、镜头限制和线程属性。它们是算子语义证据；性能、句柄释放、C#封送和本机WPF仍须相应切片验证。没有重复核查AsunImage/DevExpress安装、授权或兼容性。


### 18.4 本轮新增数值源码/测试证据（只补缺口）

已有transforms3d/tf2、HALCON26.05和DevExpress25.2证据未重做。本轮仅针对原G-CG-NUMERIC、BCL与Inspector绑定缺口读取以下原件，不下载运行依赖、不拷贝源码、不执行上游测试。

| 锁定来源 | 实读源码/测试/元数据 | 采纳与限制 |
|---|---|---|
| Reference-LAPACK **3.12.1**, commit `6ec7f2bc4ecf4c4a93496aa2fa519575bc0e39ca` | [dgesvj.f](https://github.com/Reference-LAPACK/lapack/blob/6ec7f2bc4ecf4c4a93496aa2fa519575bc0e39ca/SRC/dgesvj.f)、[ddrvbd.f](https://github.com/Reference-LAPACK/lapack/blob/6ec7f2bc4ecf4c4a93496aa2fa519575bc0e39ca/TESTING/EIG/ddrvbd.f)、LICENSE；BSD-3-Clause，Fortran/BLAS例程依赖 | §3.5单侧Jacobi/归一内积/有界sweep、重构/正交/singular排序测试。原实现含30 sweep、block/band优化与缩放策略，本文小矩阵cyclic+128硬上限/显式Policy/证书不是逐行移植，LAPACK通过不证明本文C#性能/正确性；不引Fortran/BLAS包 |
| JTS **1.20.0**, commit `6e95fe82feb986a7aa657f4ffa406d8c290af509` | [CGAlgorithmsDD.java](https://github.com/locationtech/jts/blob/6e95fe82feb986a7aa657f4ffa406d8c290af509/modules/core/src/main/java/org/locationtech/jts/algorithm/CGAlgorithmsDD.java)、[OrientationIndexTest.java](https://github.com/locationtech/jts/blob/6e95fe82feb986a7aa657f4ffa406d8c290af509/modules/core/src/test/java/org/locationtech/jts/algorithm/OrientationIndexTest.java)、LICENSES；源头EPL2.0/EDL1.0，Java/JTS-DD及JUnit | §3.6/13.1 near-collinear/逆向orientation反例与filter后高精度思想；本模块v1明确exact BigInteger，不把DD≈106bit宣称任意binary64 exact，不引Java或JTS运行依赖；test中Java assert可能需启用，源码存在不等于所有断言已执行 |
| SymPy **1.14.0**, commit `16fa855354eb7bcabd3fe10993841e03b1382692` | [rootisolation.py](https://github.com/sympy/sympy/blob/16fa855354eb7bcabd3fe10993841e03b1382692/sympy/polys/rootisolation.py)、[test_rootisolation.py](https://github.com/sympy/sympy/blob/16fa855354eb7bcabd3fe10993841e03b1382692/sympy/polys/tests/test_rootisolation.py)、LICENSE；BSD-3-Clause（第三方条款另列），Python/mpmath/domain polynomial工具 | §3.7取Sturm square-free/负余式链、端点计数、重根/no-real-root测试。上游isolate主路线VAS continued fraction，本文固定Sturm有理二分，**不宣称复制了其root isolator**；不引Python/mpmath生产依赖 |
| Microsoft net10.0 BCL | [BigInteger](https://learn.microsoft.com/en-us/dotnet/api/system.numerics.biginteger?view=net-10.0)、[Math.BitIncrement](https://learn.microsoft.com/en-us/dotnet/api/system.math.bitincrement?view=net-10.0)正文 | §3.6任意精度整数及向外邻接double；BigInteger不等于无资源限，本模块所有位长/运算步骤必须计预算；BCL类存在不证明自制有理/根算法正确 |
| 跨模块只读绑定 | [viewport唯一指导§3.3/15.2](../viewport/DEVELOPMENT-GUIDE.md)冻结的 `Asun.UI.Viewports` 公开契约（`ViewportTransform`、`ViewportCoordinateOverlayRuntime`）；DEV-GOV-010 §3.1 的 BCL Exe 约定 | §11.4仅Display消费边界（float/clamp不用于物理）；viewport own Factory/Session/Dispose由其Owner掌握，不伪造公开WPF控件成员；§13.1冻结net10.0 BCL Exe，不用dotnet test空执行 |

原始字节SHA-256供commit原件追溯（不另造manifest）：dgesvj.f=`c606561e62f37ec1c6959ef8c0bc2fe92d4b3470be88d2c6c3e0b06ae1dbad87`；ddrvbd.f=`bd661e74835f7320b032a918b28c50b73c624bc7c2790f07e22a9d3635c07791`；CGAlgorithmsDD.java=`a124999a7521b8a1363e5e8000dd9b5b53e45b7cf5ab7cdac04a6fef770638a2`；OrientationIndexTest.java=`167f77c0ab38fdf8a46410ef8b053e0d88b2a505434527abfcaf70bb9789f6fd`；rootisolation.py=`40a098803e2430d06d48b6245229bc3171daee5a2e32d94ed2b8b02938974512`；test_rootisolation.py=`c7e9fe4fe0a89fef2985e94d6b4e413ecce40bf5025b50b4c803b0cfae7c23ad`。

## 19. 逐切片准入、具体剩余门与六项结论

### 19.1 实现落点与禁止路径

Core-A/B/C/D/E各次只修改唯一Core工程及其测试工程，不带HALCON/WPF/Persistence/Shell依赖；先读已有代码消费者/状态/测试再实施，不自动迁移/删除既有代码。Halcon切片仅修改接收后的`.Halcon`及对应测试；Wpf仅`.Wpf`及对应UI测试；共享文件/产品映射由主会话串行接收。外部来源/交付项目只读，不扫描AsunImage内部、不另建会话/子代理；本轮状态同步不执行这些后续实现。

本文已经决定单位/换基/域/模型/图算法/状态/Owner/操作流；以下未决按实际影响逐项阻断，不能让普通程序员临时猜补，也不要求客户物理值先挡全部Core：

| 门 | 具体缺口、责任与受影响切片 | 无关能力处理 |
|---|---|---|
| G-CG-API | §4.3 literal类型/enum/factory与摘要夹具已冻结，内部技术缺口关闭；主控已按六项接收CG-Core-A/B/C/D文档规格，不另留编码时选型 | 产品DTO/C-03仍独立接收；不冒充本轮已构建 |
| G-CG-NUMERIC | §3.5–3.8固定Jacobi+证书/稳定逆、exact谓词/交点/Sturm全域、PSD LDLᵀ/联合AD；有限预算/失败路线已冻结，内部技术缺口关闭 | 后续按CGT-MATH/DOMAIN/CURVE/COV执行验证，当前不是运行PASS |
| G-CG-CELL-RANGE | §4.4完整公共值/端口/factory与exact算法已闭合；主控于2026-10-10接收CG-Core-E六项文档规格，ModuleCoreImplementationReady（仅规格准备） | A/B/C/D既有接收不变；E数值oracle/真实ROI lease桥与consumer映射仍未执行，不证明Alignment其它Jacobian/条件/物理门 |
| G-CG-PORT | §9.1.1–2 localfield本地公开快照/工厂/配对/节点参数和camera §9.2.1公开消费已确定；剩余为真实来源封存、字段发布与资格证据，由各资产Owner提供 | 只阻确实依赖该来源的CG-External请求；不再把自己的类型/构造欠账列外门，纯软件场可独立验证 |
| G-CG-HALCON | §8.3/9.2.1/10.1–2已有装配指导限定内容接收保持；§8.4落实参数顺序/矩阵flatten/输出校验。实际C#封送/真实桥/异常释放Golden/性能未运行 | 不核查依赖许可、不把已解引用当params；真实writer/content/资格/pose/plane仅阻相应camera请求，矩阵桥和Core不重退 |
| G-CG-UI | §11.4既有literal/API保持，§11.4.1/10.1–2已有指导限定接收保持；现已明确viewport v0.2非null Lifetime、同Control.Presentation、完整资源schema、ViewportPresenterSubmission及原Unbind/lease观察；§11.5–6补确定控件配置/Host刷新/完整资源。真实主题/25.2.3/1920×1080和借用显示行为未验 | 没有未决定控件/刷新API；具体viewport/image/3D资源与实际呈现按受影响门验证，不阻Core及Display=null |
| G-CG-INTEGRATION | 正式C-03/State/Owner映射与两个真实消费者的版本化输入/回放未接收 | 本地API不冒充平台Schema；只阻断产品集成 |
| G-CG-PHYSICAL | 客户/设备提供真实相机/平面/深度/支持域、标定/计量资格、物理误差/性能目标及现场样本 | 无来源物理数值不编造；仅依赖它们的物理请求/验收受阻，无关Core不等 |

技术算法/公共类型已由本轮冻结，不包装成用户必须提供的外部门。剩余外部条件是客户/设备物理验收值、真实资产/样本、正式平台Owner映射和具体宿主适配；C#/真实库/WPF/性能验证是后续实施验收工作，不能反称算法未定。主控已分别接收CG-Core-A/B/C/D/E六项文档规格，按其明确结论同步为ModuleCoreImplementationReady（仅规格准备）；整体保持DesignReview/Prep，其它切片不据此提升。

### 19.2 DEV-GOV-010 §3.1六项准备结论

| 条件 | 文档准备结论（不等于执行验证） |
|---|---|
| 1 边界/依赖/第二消费者 | §1/2/10/17已固定ROI与无UI计量；Core-A/B/C/D、Halcon/External/Wpf均有实际消费计划与禁止路径 |
| 2 唯一Module API/单位/域/生命周期/版本/所有权 | §3.5–3.8/4.3/6–7/16为literal与固定数值规格；§11.4为Wpf自己公开端口。内部API/factory/数值待选缺口关闭 |
| 3 最小无UI宿主/端口 | §4.3 new CoordinateGeometryFactory().CreateManaged与§10调用；外部Backend明确注入、无隐藏窗口；§13.1 net10.0 Exe接入闭合，未实际构建 |
| 4 样例/测试 | §12/13/13.1覆盖整模块必需CGT-API至VERSION、race/Unknown/关闭/回退；BCL替身不冒充HALCON或现场 |
| 5 BenchmarkProfile | §14与共享统计入口固定；软件执行Profile/有限截止见§13.1，物理性能目标仍待消费者Profile，缺失NotEvaluated不阻无关Core |
| 6 工程/范围/最小调用 | binding/§10/13.1/17/19给唯一工程、真实dotnet build/run命令及六项分片表；本轮只改指导 |

逐切片六项文档准备矩阵：D=本地规格已具备；CG-Core-A/B/C/D/E的六项D已分别由主控接收并标ModuleCoreImplementationReady（仅规格准备）。其它切片的D仅表示本地规格，未自动授予相同状态。表内E=依赖外部正式映射/证据，仅阻相关集成，与切片名CG-Core-E不同。规格接收不等于代码或产品验收。

| 切片 | 1边界 | 2API/算法 | 3宿主 | 4断言 | 5性能方法 | 6落点 | 当前结论 |
|---|---|---|---|---|---|---|---|
| CG-Core-A | D | D §4.3/6–7 | D §10 | D CGT-API/LIFECYCLE/DRAIN | D §14 | D binding/13.1 | `ModuleCoreImplementationReady`（规格准备，主控已接收）；无客户物理阻断 |
| CG-Core-B | D | D §3.5–3.6/5 | D | D CGT-MATH/GRAPH | D | D | `ModuleCoreImplementationReady`（规格准备，主控已接收）；图/稳定逆/3D线与法向验证待实施 |
| CG-Core-C | D | D §3.6–3.7 | D | D CGT-DOMAIN/CURVE | D | D | `ModuleCoreImplementationReady`（规格准备，主控已接收）；Polygon/洞/曲线全域验证待实施 |
| CG-Core-D | D | D §3.8/4.3 | D | D CGT-COV | D | D | `ModuleCoreImplementationReady`（规格准备，主控已接收）；PSD/相关块/解析AD验证待实施，物理局部有效性E按请求绑定 |
| CG-Core-E | D职责/两消费者 | D §4.4.1–3 | D §4.4.4显式桥 | D CGE-01–12/CGT-DENOMAIN | D §4.4.5专属Profile/测点，沿§14统计 | D同Core/Exe工程 | `ModuleCoreImplementationReady`（仅规格准备，主控于2026-10-10接收）；真实oracle/ROI桥/消费接线未执行，不含Alignment其它用途门 |
| CG-Halcon | D | D §8.3–4/9.2.1自有装配/精确消费；实际C#封送E | D §10.1–2双Host/根恢复 | D §13.2；真实Golden E | D §13.2/14；真实测量E | D.Halcon及对应Tests | 已有装配限定接收保持，完整指导按§19.3自审收口；PreparationIncomplete/NotReady，真实HALCON/Read/pose/plane/资源/集成/现场门未验 |
| CG-External | D | D §9.1.1–2/9.2.1值/工厂/算法/配对/Drain | D明确注入及原双Host | D §9.1.2/13替身；真实资产E | D §9.1.2/14 | D本Core LocalFieldV1及原Tests | 完整软件指导按§19.3收口，不授代码准入；真实来源/物理域/逆唯一性及运行证据只阻相关请求 |
| CG-Wpf | D | D §11.4–6权限/借用桥/配置/资源（含v0.2 Lifetime/Presentation/Submission/schema/Unbind） | D §10.1–2双STA/noUI/根恢复；实际viewport E | D §11.5/13.2；实际WPF E | D显示预算/可见/资源两轴 | D.Wpf及对应Tests | 已有装配限定接收保持，完整指导按§19.3自审收口；PreparationIncomplete/NotReady，真实WPF/Viewport/主题/资源/运行资格未验 |
| CG-Integration | D | E C-03/提交Owner | E两个真实消费者 | E真实Replay/现场 | D方法，客户目标E | D产品由主任务 | 保持外部门，不造生产事实或放行 |

本文件整体继续`DesignReview/Prep`；CG-Core-A/B/C/D/E按既有接收结论为`ModuleCoreImplementationReady`（仅规格准备），既有接收不变。E保留完整witness、CheckEvidence、同步有界scratch及上游ROI完整性Owner，不证明Alignment其它Jacobian/条件/物理门。CG-Halcon/External/Wpf/Integration保留上表具体后续门，未提升为ImplementationSpecificationReady或生产准入。真实C#构建、BCL Exe、数值oracle、HALCON、WPF、性能及物理资格均未执行；精确有理手算与既有CGE-01～06独立复算不替代这些验证。当前完整文档准备按§19.3在本永久原会话自审和验证，总控只接收结论，不再将已有内容挂作等待总控复核的内部设计门。

### 19.3 当前全部批准范围的文档准备结论（2026-10-11）

**结论：当前架构定义的IM-007全部批准能力及既有使用场景，可决定的软件设计欠账已闭合；无剩余本模块内部算法/API/架构/控件选择待编码人员补猜。** 本结论是DEV-GOV-010 §4的文档完整性，不等于模块已实现、完整代码Ready、产品集成或运行/现场资格。本轮只补§8.4、§9.1.1–2、§9.3、§11.4.1、§11.5–6和§14.3实际缺口，并同步§19旧接收文字；§3/4既有Core、codec、数学Golden与既有自审/向量保持复用。

| 当前完整能力/场景 | 可实施正文与准备结论 | 尚需何种证据、谁负责 |
|---|---|---|
| 精确Frame/单位/方向/矩阵、像素中心/角点/crop/resize、Raw/Canonical/Display与顶底面 | §1–4.3/8.1/8.4/11.5；全部明确，模型名称/Scale/ScalarPath表§4.3.1–2 | 实际图像坐标来源/尺寸/物理基准由Host坐标资产Owner发布；Core数学/codec由IM-007后续实现验证 |
| 2D/3D identity/translation/rigid/affine/projective/PlaneLift，点/向量/法向/线/面/曲线/区域洞与局部一阶误差 | §3.3–3.8/4.3/5/12/13.1；已有Core A/B/C/D六项接收保持，不重审算法或Golden | IM-007执行C#/exact oracle/资源与反例测试；不需要客户事实才能验证纯数学，物理线性化范围归用途Owner |
| 图身份/注册校验/路径/组合/稳定逆、全域分母证据与ROI/定位/拼接预检 | §4.2–4.4/5–7/13；Core E完整witness/CheckEvidence等保持 | 上游ROI/定位/拼接原Owner对来源/用途/租约接线，IM-007对E运行oracle；注册仅值校验，持久发布归Host |
| HALCON矩阵/像素桥及相机平面/相机或世界投影/畸变 | §8.1–4/9.2.1/10.1–2/13.2；具体算子/参数/顺序/绑定/拒绝与释放确定 | IM-007实现真实cv2/C#封送/Golden/资源；CAL提供原solved writer/content/资格水位；Host资产Owner提供pixel/camera/world/plane/pose/用途/曝光/可见域 |
| 已封存Bilinear局部场/位移、有限点与锚点向量法向、解析节点误差、显式配对逆场 | §9.1.1–2/4.3/5/7；完整值/工厂/索引/边界/导数/配对/有限恢复与双消费者已定，无求场或自动逆 | IM-007实现软件field/router与原Tests；Host坐标资产Owner发布真实场/基准/节点协方差/唯一性和线性化证据。二维之外、无证逆/连续曲线认证属于明示不适用，不能自动采样 |
| 独立无UI调用、ROI与计量消费者、跨FOV/底面/卷料消费、重复/并发/取消/超时/失联/重启/升级回退 | §1/2/6–7/10/15–16/20–22；原根/原Task/ID/借用/独立cleanup与两消费者完整 | IM-007实施并执行协议/故障/资源测试；产品Owner绑定实际板面/单元/运动epoch及C-03，设备动作/质量处置/重启事实恢复不归坐标模块 |
| 可选Inspector、DevExpress精美布局、三语、键盘/UIA、参数诊断、权限和借用image/3D显示 | §11.1–6/10.2/13.2；控件/Host刷新请求、同Control.Presentation、非null Lifetime、完整`ViewportUiResources` schema、`ViewportPresenterSubmission`、只读与NullDisplay/TableOnly/Visible及Drain两轴确定 | IM-007真实WPF/1920×1080/三语/视觉/键盘/UIA；Viewport/Host Owner提供当前授权/Theme/资源/真实Presenter/GPU归还并由原Owner完成有限Unbind；它们不授坐标/测量资格 |
| 参数模板/默认与自动化边界、确定性版本和性能负载/判据 | §4.3.1–2/9.1.1/14.1–3/16；无隐式数值/自动放宽或生产推荐，软件Profile与物理目标分开 | IM-007确认软件技术Profile/性能测量；消费者BenchmarkProfile Owner冻结真实负载、样本计划/最低有效n/目标、客户/设备Owner提供物理接受事实 |

外门只包括：确实依赖的真实资产/资格/物理Profile、产品正式Owner/C-03与具体宿主输入，以及后续真实构建/算法/资源/WPF/性能/现场执行证据。自有公共类型/参数名称、算法、曲线/局部场支持边界、Host构造、默认/推荐规则、控件和恢复均不再列外部门。没有设备SDK、数据库写入或质量放行需求在本模块隐藏实现。门与消费者逐项关联，缺相机plane/可见性不阻矩阵Core/无camera HALCON/NullDisplay，缺真实Viewport不阻无UI及数值Inspector，缺生产性能目标只NotEvaluated。

本轮核验消费路径为：明确快照/参数→公开factory→原Submit/Map/Wait/Query→全部域/误差/资格门→原Task退出/归还→结果或可判定拒绝→Host消费/显示→独立Close/Stop/回退。局部场/模板/UI增量按各节固定反例及链接/围栏/类型/资源定向验证，不重算已接收Core。验证记录只在本文§23简述，不新建脚本/报告；完成后停止，不靠总控代做内容审核。

## 20. 宿主端到端走查

正常：宿主取得明确graph+Policy→封存→Submit接纳→Validate→固定路径→Map/域/误差→真实Drain/释放→Completed回执→宿主保存/消费。缺图/策略/模型返回精确错误，不用历史缓存或单位阵补空。参数修改形成新Policy/图Ref和新RequestId，旧请求/结果不变。

失败：第一个不可判定几何项全批拒绝→保留失败索引/路径/安全诊断→完成释放→Rejected/Failed→UI给下一恢复动作。用户修正输入后新请求，旧回执可查询；外部资产修订由Owner发布，控件不自动写回。等待到期→Query原ID，不发隐式重试。native仍在运行→Draining/Unknown→服务保持隔离→确认归还后终态；不能因为窗口消失或取消按钮按过就释放。

第二消费者：分别新服务实例/同包，独立资产/参数/语言投影；共同canonical输入得到等价值；一方错误/Close/Cancel不改变另一方；无UI消费者不加载WPF/Dispatcher/HALCON句柄。共享服务时只有共同宿主Stop，单控件无Stop权。

恢复/升级：已终态回执由宿主取回→Stop新接纳并排空→切包/新epoch→固定夹具Replay→启用；Unknown阻断卸载与复用，回退保留原资产/hash/消费者配置。客户现场门不使用本节合成值或截图替代。

## 21. 反向审查约束

数学视角逐能力检查：变换顺序/轴/中心角点/单位只定义一次；向量与点不同、法向逆转置；圆变形不冒充圆；线/曲线/区域全体域而非顶点；投影跨无穷远拒绝；逆唯一性不由det或局部Jacobian推导；协方差相关项不丢失；多路径预算耗尽不是无路径。

集成视角检查：接纳前没有操作墓碑；重复hash不能替代内容；服务限额不由请求抬高；wait取消不取消运算；取消请求不等于停止；排空和资源释放在终态前；Lifecycle可靠、Progress可合并；晚订阅能拿终态；Stop等待超时不撤销停止；版本/epoch不串用；控件关闭不销毁宿主资源；第二消费者不带私表/质量/页面/SDK。

这两种视角是文档自审的方法，非独立外部审核签字。§19记录主控已分别接收CG-Core-A/B/C/D/E文档规格，并与真实验证分开；这些Core的规格准入不推导整模块或其它切片Ready。

## 22. 不支持能力与边界裁决

禁止未知深度/翘曲自动恢复、局部场通用逆/补洞、3D实体/mesh布尔、图像插值/拼接编排、对应拟合/训练、质量/设备控制、UI自动保存生产参数、无限路径枚举和默认性能/物理阈值。不支持返回CG017/019而不是空成功；架构内已列能力不能用本节随意删除，按已冻结规格和§19逐切片接收实施。

跨模块正式合同/Owner及共享导航变化由主会话串行接收。本会话只交回本指导和明确缺口，不发送其它会话消息，不为复核/返修另建子会话，不修改模块索引或共享Contract。


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

## 23. 本轮修订与证据限度

2026-10-09：替代先前“首片等于整模块”的收窄叙述，统一v0.2形状/错误/状态；补齐图路径预算、连续域、圆/ellipse/conic、3D/局部模型、联合协方差；修正法向归一和半像素换基；分离软件数值安全、服务预算与客户物理门；细化只读Inspector、键盘/三语/恢复；记录锁commit源码/测试、官方26.05算子与DevExpress25.2证据。

此前v0.1错误编号、部分成功开关、默认5s、猜测wrapper调用、拟合求解器fallback和重复历史候选状态表已从活动规范移除，历史来源原件保留。没有改产品代码、共享权威、依赖版本或源证据文件。最终定向文档检查只验证本文件结构/链接/一致性；不宣称运行时或客户验收通过。

2026-10-09重启后接续：§3.5–3.8冻结稳定SVD/逆、exact orientation/intersection/Sturm曲线全域、PSD与联合Jacobian；§4.3冻结完整literal API/factory/Backend；§11.4固定Inspector公开消费绑定与Close回执；§13.1固定BCL Exe真实命令、必需组与有限截止；§19同步逐切片六项文档准备结论。只把内部可决定技术项关闭，保留客户物理/真实资产/正式平台和具体宿主集成门；未执行产品实现或运行验证。

2026-10-09主控接收同步：主控结合§3.5–3.8/4.3/13.1算法证书及§7/10/11.1–4/12/19–23续核，明确接收CG-Core-A/B/C/D六项文档规格；页首与§19统一为ModuleCoreImplementationReady（规格准备）。本轮未扩范围、未重审研究、未改产品代码；其它切片后续门与所有未执行运行验证保持。

2026-10-10定向跨模块闭包：只读alignment-2d最新H2/§4.14及D01–D04，新增§4.4 `CG-Core-E / DenominatorEvidenceV1`独立公开输入/四角witness/逐run界/精确门/factory/CheckEvidence/宿主桥/Test，区分全域MinAbs/MaxAbs与既有norm安全比。两轮有限自审完成：第一轮exact有理手算核对CGE-01–06/10；第二轮修正新chart与旧Pixel服务规则的冲突，明确bit摘要/版本/覆盖复核、预验证中断、null证据、scratch所有权与GC/ROI释放边界，并补E专属Profile。现有validate_docs及本文链接/新节表格/literal引用/接收状态定向检查通过，仅证明文档结构和本轮规格核对。主控随后通读§4.4并独立以精确有理数复算CGE-01～06，确认run极值、跨零、带孔异号、binary64 .1严格边界、affine单位与闭边触零一致，接收E六项文档规格为ModuleCoreImplementationReady（仅规格准备）；本永久会话仅同步页首/§17/§19/本轮及相关状态，不重审已接收内容。A/B/C/D接收不变，完整witness、CheckEvidence、同步有界scratch和上游ROI完整性Owner保持；不证明Alignment其它Jacobian/条件/物理门或真实运行。不创建工程、不改共享文件、不新建/派生会话，完成定向一致性检查后返回等待。

2026-10-11后续装配窄审：已有§4.3 CreateWithBackend/Map/Drain、§8.1–2路线及§11.4 Inspector literal/factory/Bind/Close/语言入口直接复用。真正补齐§8.3 HalconGeometryBackendFactory/Options/有限Invocation账本、§9.2.1 CAL Camera Read API 1已解参数/完整原件/pose/plane/单位/域/用途/当前水位桥、§10.1–2构造前Host根/原Task与ID恢复/双STA及第二消费者noUI调用、§11.4.1权限代理/借用Viewport公开装配/overlay与Presenter分账/三语恢复、§13.2针对这些增量的故障与性能测点。只读CAL §9.3/7.2C与Viewport §3.6/4.6.1/10.6–7，复用其研究/完整fixture；另读HALCON26.05 image_points_to_world_plane/project_3d_point/hom_mat3d_to_pose官方Description/Execution，后者只允许已验证rigid→type0，不重新求解/选算法，不扫描AsunImage内部。两轮有限自审：第一轮查公开字段/成员/链接及已接收Core/Inspector声明/旧Golden保留；第二轮查构造前额度、原Task/ID、同Close/Clear/Dispose过程、撤权/迟到/Dispatcher退出、无自等待及归还两轴，修正空控件Bind后Attach、可见与本缓存Drain分离、BorrowedViewport专属预算和nm显式中间frame。本文本地定向结构/一致性校验仅证明指导，本轮未建工程、写产品代码/测试/报告或执行真实Host/C#/HALCON/WPF/Golden/性能/物理资格。新增指导已在本轮永久原会话完成自审收口；CG-Core-A/B/C/D/E接收、§3/4算法/编码与Golden保持，CG-Halcon/Wpf/External/Integration仍不提升真实运行或生产准入。

2026-10-11完整范围收口：在不重审已接收Core/codec/旧Golden的前提下，补齐§8.4 HALCON 26.05参数封送和输出校验、§9.1.1–2 LocalFieldV1公开快照/工厂/插值导数/逆场配对/双消费者反例、§11.5–6本机DevExpress 25.2公共XML可定位控件组合/宿主刷新事件/NullDisplay图元边界/完整三语资源，以及§14.3默认/建议/自动化责任。实际读取的本机XML确认AutoGenerateColumnsMode.None、TreeList自引用字段、PropertyGrid WithPropertyDefinitions/AllowExpandingMode.Never/IsReadOnly、Dock布局及BarItem.SuperTip等成员；HALCON本地26.05页面确认projective/affine/pose/畸变的签名顺序与线扫限制。有限自审检查章节顺序、类型/参数/单位/索引、反例、Owner/恢复、真实门与无UI边界；本文件链接与代码围栏定向检查通过。未执行C#编译、真实HALCON/CameraRead/Viewport/WPF、Golden/Replay、性能或物理资格；§19.3的“可决定设计欠账已闭合”不改变这些运行门。

2026-10-11跨模块消费边界窄同步：依据motion-control §17.2及googol-motion-adapter的公开消费规则，补明本模块不实现Motion CoordinatePort、不猜`Kind`/Machine Start、不持运动权限或设备恢复，且只向上游提供版本化几何资产能力；依据viewport §10.6.1，补明借用Inspector必须使用同Control.Presentation、Bind前非null Lifetime、完整`ViewportUiResources`（`Revision=viewport-ui-text/1`）、`ViewportPresenterSubmission`及原Unbind/Presenter/lease有限观察。Core、算法、Golden、三语入口、Root/Close及整体`DesignReview/Prep`状态保持；未执行代码、真实WPF/Viewport或Motion运行验收。
