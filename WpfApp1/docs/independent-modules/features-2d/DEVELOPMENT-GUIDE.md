# features-2d：二维边缘轮廓与特征开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1a, C1b, C1c`

- 模块 ID：`IM-025`；来源：`PKG-021`
- 状态：C1a / C1b / C1c 为 `ModuleCoreImplementationReady`（仅规格准备，2026-10-10主控接收）；A1/W1公开装配、消费者及Host补全确定指导已限定内容接收（2026-10-11）；当前全部批准范围的可决定软件设计已闭合，文档准备完成（§17.1，原会话自审）；真实HALCON/WPF/资源/运行/性能/现场资格未提升，其它代码切片仍按 `DesignReview / Prep` 及后续授权/验收进入；本轮：`IM-REVIEW-20261009/features-2d`
- 技术基线：C# / .NET 10，HALCON 26.05经AsunImage的`ImageLibDotNet.cv2`；可选WPF / DevExpress 25.2.3
- 本页是本模块唯一实施入口。Module API Contract v0.2见附录A；平台C-02/03/04映射仍由原Owner采纳。本次只完善规格，不表示产品代码、真实视觉、UI、性能或生产通过。全部批准范围覆盖见§17.1；本模块完整三语资源已在§8.4.1～5闭合，最后的viewport Presenter公开接线已按0.3.4-prep在§8.7.1消费并关闭。文档内部设计闭合与产品代码/真实运行/生产准入分别判断。

## 1. 目标与边界

### 1.1 职责与非目标

接收不可变图像、有效域、观察角色、二维采样计划与方法Profile，执行有向亚像素测边/边对、灰度或颜色XLD边界、分段、单一支撑上线/圆/椭圆拟合，输出原始观察、几何候选、支撑/残差/退化/截断与生命周期证据；提供离线有限参数建议及可选嵌入UI。形状能力指上述几何形状与轮廓证据，不把模板匹配/Blob/区域分类混入本契约。

目标身份、全局关联、被测量定义、工艺阈值、质量放行、复判、报表、设备与持久化事实归宿主。元件/孔/边/引脚等名称不进入Core业务枚举。无Pass/Fail，无隐式AI、学习/训练、增强、补边、自动fallback或静默参数变更；残差/幅值/分数不是合格概率或测量不确定度。SDK句柄、HObject/HTuple、产品页面/VM/私表/全局可变状态不穿Core。

### 1.2 消费者与数据所有者

| 消费者/真实复用计划 | 输入与输出 | 保留责任 |
|---|---|---|
| 孔/开口工具 | 局部有向边/边对，显式关联的圆/椭圆支撑 | 孔身份、哪侧/中心定义、孔径/开口被测量及缺口政策 |
| 板边/引脚工具 | 有序轮廓、线段/弧与原索引 | 外形/针序/网络、拼板关系、物理端点与尺寸规则 |
| 元件/外观工具 | 封装局部边/几何候选 | 元件身份、姿态/缺陷解释、人工复判和放行 |

宿主拥有Frame/Support/Profile/标定及资格来源；本模块拥有单operation的临时计算、队列与释放账；结果复制为托管值，持久化仍由宿主。帧/坐标源以租约保护在用数据至归还，不能在过期/断连时销毁仍被native读的缓冲。

### 1.3 唯一工程与允许路径

根namespace `Asun.Modules.Features2D`；ImageLib/UI子namespace为`.ImageLib`、`.Ui.Wpf`。工程尚未创建，本轮仅改本页；下列是获实现授权后的唯一落点，不授权创建空工程。

| 切片 | 唯一代码/测试工程（仓库相对路径） |
|---|---|
| C1a：值对象/校验/资格与结果不变量；C1b：服务/端口/调度/资源；C1c：离线建议 | `src/Modules/features-2d/Asun.Modules.Features2D.Core/Asun.Modules.Features2D.Core.csproj`；`tests/Modules/features-2d/Asun.Modules.Features2D.Core.Tests/Asun.Modules.Features2D.Core.Tests.csproj` |
| H1：两消费者与最小无UI装配 | 复用上述Core.Tests的BCL Exe，`--host hole`、`--host board-edge`；不再建第二个同义harness |
| A1：真实HALCON路线适配 | `src/Modules/features-2d/Asun.Modules.Features2D.ImageLib/Asun.Modules.Features2D.ImageLib.csproj`；`tests/Modules/features-2d/Asun.Modules.Features2D.ImageLib.Tests/Asun.Modules.Features2D.ImageLib.Tests.csproj` |
| U1：可选嵌入UI | `src/Modules/features-2d/Asun.Modules.Features2D.Ui.Wpf/Asun.Modules.Features2D.Ui.Wpf.csproj`；`tests/Modules/features-2d/Asun.Modules.Features2D.Ui.Wpf.TestHost/Asun.Modules.Features2D.Ui.Wpf.TestHost.csproj` |

Core为Microsoft.NET.Sdk/net10.0类库，仅BCL；Core.Tests为同SDK/net10.0/OutputType=Exe，只ProjectReference Core，无待选测试包。模拟端口与两adapter在此唯一测试工程，不发模拟生产DLL。A1为net10.0-windows，使用用户既有AsunImage；U1为net10.0-windows/UseWPF=true，本机DevExpress25.2.3引用，不从NuGet下载。Core不引用WPF/DevExpress/AsunImage/设备/产品Shell；ImageLib与UI可选独立DLL，UI不负责核心初始化。禁止修改其它模块、共享文件、产品、登记、AsunImage内部、参考项目/原件。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Features2D.Core` 与 `Asun.Modules.Features2D.ImageLib` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.Features2D.Ui.Wpf` 可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1.3 的 C1a/C1b/C1c 切片（仅 BCL）因此可在无 WPF、无 HALCON runtime、无 AsunImage 程序集的宿主中完整运行，H1 的两消费者最小无 UI 装配即该门禁的验收面。

**Blazor/Web 宿主中的特征与测量预览**：Web 端需要"在图上标出测出的边/圆/椭圆并给出残差"时，服务端调用 Core/A1 的同一套执行入口取得原始观察、几何候选、支撑/残差/退化/截断证据，再投影为浏览器标记。约束：
- 浏览器端只渲染标记与数值，不重算亚像素边缘、不自行拟合圆/椭圆、不解释残差；几何事实只有本模块一个来源
- §1.1 的"残差/幅值/分数不是合格概率或测量不确定度"在 Web 投影中同样成立：前端不得把残差或分数显示为 Pass/Fail 或公差合格
- 本模块**不**提供无 UI 的"Web 专用简化 API"；Web 宿主消费的就是 §1.3 已冻结的 Core 端口与 A1 适配，二者只有一套算法
- 宿主拥有 Profile 与资格来源（§1.2）；前端不得自选采样计划或方法 Profile

**AI 推理 Tiling 适配**：本模块与 `ai-inference` 是**互补而非替代**关系——AI 出缺陷候选、传统特征出确定性几何，规则链在宿主侧仲裁。适配约束：
- AI 候选需要精确定位/测边时，由宿主把候选 ROI 交本模块做几何观测；本模块**不**为 AI 候选重新设计采样计划，也不引入隐式 AI/学习/训练（§1.1 禁止项）
- 本模块的测边/拟合运算在大图上按 `roi-geometry` 提供的裁切区域执行；本模块不自行裁切、不实现 `RequestTileAsync`、不持有 tile 租约
- 落在裁切区外的目标不因"AI 看见了"而被本模块补测；边界不足时如实产出退化/截断证据，不补边

**HALCON 备选交叉验证适用性**：本模块是 2D 视觉链中双跑 CI 的**亚像素精度落点**，是整链最容易出现"两路都跑通、但差一个亚像素"的一环。约束：
- 有向亚像素测边、灰度/颜色 XLD 边界、分段、单一支撑上线/圆/椭圆拟合在 HALCON A1 路线与一条纯托管参照路线上按**同一 Golden 数据集**双跑：边缘点位、轮廓顶点序、拟合参数（中心、半径、角度）、支撑与残差、退化/截断标志逐项比对，差值超容差即 CI 失败并产出差异报告
- **已知的必然差异，不得抹平**：HALCON 的 `edges_sub_pix`、灰度/颜色 XLD 提取、`fit_circle`/`fit_ellipse`/`fit_line` 使用其自身的边缘模型、采样策略、搜索范围与收敛判据（§2.2 已核对的 26.05 语义），托管参照**不可能**逐位复现。因此双跑门禁按项分三类：
  - **强门禁**（可精确复算）：退化/截断/失败标志、支撑点数、顶点数量与顶点**序**关系、轮廓拓扑
  - **容差门禁**（容差按项分别冻结）：边缘位置、拟合中心/半径/角度、截距——容差以像素域冻结并**逐指标**声明，不用单一 eps 覆盖全部
  - **仅诊断**（聚合/实现相关）：残差统计量、支撑域面积、幅值分布——两路实现不同即差异，标注来源，不作失败判据
- §1.1 的"无隐式 fallback 或静默参数变更"在双跑中同样成立：双跑 CI **不得**用"取两路较优结果"或"以差值较小者为发布值"来规避失败；两路差异必须定位到具体算子语义或实现缺陷
- HALCON 仍是生产路线；托管参照只作交叉验证与降级保险，不作发布依据。**第三方独立 oracle 在本仓固定 OpenCV 快照（commit `a0cda081f8d769f40ab2f4904738b4787b44d07c`）中不覆盖本模块核心方法**：该快照只含 `imgproc`（templmatch/connectedcomponents）、`geometry` 与 `stitching`，没有亚像素测边、XLD 轮廓提取或圆/椭圆拟合的对应实现（见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)）。因此本模块双跑**只有"HALCON vs 自建托管参照"两路**，托管参照必须逐算子语义自证（对齐 §2.2 已核对的 26.05 语义），不得把"无第三方 oracle"当成可放宽容差的理由；不引入 OpenCV runtime 或平行生产算法
- 本模块明确**不含**模板匹配/Blob/区域分类（§1.1 末句），双跑范围不得把 `templmatch`/`connectedComponents` 拉进本模块门禁——那些属 `segmentation` 与其它模块

## 2. 依赖、权威与方法选择

### 2.1 单一权威和数据流

遵循用户当前指令→批准架构/指导/契约→项目规则→通用规则→外部参考。[独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)规定职责，[DEV-VIS-025](../../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md)提供公共观察语义；本页冻结模块具体方法、API与接入，不建立第二套平台Schema。共享指导旧“封装可能不提供算子”表述不覆盖用户HALCON26.05全算子基线，跨文件交主控接收。

图像帧/坐标/ROI能力经附录A端口接入，不依赖其私有实现；计量与全局assignment为消费者可选后续，不是本模块硬依赖。数据流：纯Validate→元数据支撑/版本/额度预检→接纳/排队→额度/frame/coordinate/job租约→原观察与索引→分段/局部唯一关联→逐点映射→单primitive拟合与资格→复制封口→真实排空/逆序释放→唯一结果→宿主计量/关联/判定。

### 2.2 HALCON26.05固定派发

全部算子直接经ImageLibDotNet.cv2，不查封装内部、不直引halcondotnet/HOperatorSet，不安排安装/授权/兼容性核验。以下是operator算法顺序，不冒充编译确认的C#重载；只有实际参数类型/重载/封送歧义才查公共签名。

| ID/场景 | 固定主路线与输出 | 候选比较/分支与限制 |
|---|---|---|
| E1 单边/多边 | gen_measure_rectangle2→measure_pos→close_measure；位置/有符号幅值/N−1相邻距离 | 完整近直边卡尺投影；XLD弯曲边不是相同输出定义；Select明确First/Last/All，不挑最近名义边 |
| E2 明暗带 | measure_pairs；N对/N对内/max(N−1,0)对间距；预登记PairDiagnostics才额外measure_pos(all,all) | 不手工配两峰；空pair无法区分无边/单侧边；diagnostic独立原索引，不能当失败fallback |
| C1 灰度边界 | edges_sub_pix(canny)→get_contour_xld→query_contour_attribs_xld/get_contour_attrib_xld | Lanser等递归Alpha意义不同，Sobel_fast属性/定位不同；当前固定CPU Canny，不声称最快 |
| C2 颜色边界 | 三通道平面→edges_color_sub_pix(canny)，其余同C1 | 灰度化可能丢等亮异色边；不自动RGB→Gray，不承担颜色分类、色环或极性识别 |
| F1 线 | 可选segment_contours_xld(lines)→fit_line_contour_xld(regression) | 显式RobustTukey用tukey；lines_gauss是脊线中心/宽度，不替代边界线 |
| F2 圆/弧 | 可选segment_contours_xld(lines_circles)，cont_approx=1→fit_circle_contour_xld(geometric) | RobustTukey用geotukey；algebraic目标不同；不按低残差换法，短弧/混源拒有效几何 |
| F3 椭圆/弧 | 可选segment_contours_xld(lines_ellipses)，cont_approx=0→fit_ellipse_contour_xld(geometric) | RobustTukey用geotukey；fitzgibbon/voss/focpoints目标不同；Radius2=0/返回线拒绝 |

Primitive固定None/Line/Circle/Ellipse；分段标记不能替宿主改类型。None返回原轮廓/边；已有连续单一支撑时Segmentation=None直接拟合。图像内分段后经非等距映射可能不再是同一primitive，仍按目标空间资格拒绝，不能只变圆心/端点。复合角点/矩形/两边夹角/孔宽由消费者组合，不偷偷扩大公共量测职责。

Metrology为独立对象/实例量测责任，不进入本Route；legacy请求F2D-002，不称AsunImage缺算子。当前所有上述能力均保留规划，C1/A1分层不删能力授Ready。

### 2.3 离线参数建议

Features2DRecommender接收固定BaseRequest、有限ParameterCandidate、独立标注的校准/验证样本和EvaluationPolicy。只允许Caliper Sigma/Threshold，Canny Alpha/Low/High及分段距离变化；方向/ROI/Transition/Select/Interpolation/Primitive/拟合方法/坐标不参与优化。

1. 校验真值来源/坐标/单位/hash，校准/验证SampleId不交叠，最终资格留出集不参与。MaxEvaluations精确定义为子Execute次数；每组合×全部校准和验证样本数checked超过MaxEvaluations则整体Abstained，不只跑前几项称最优。
2. CandidateKey、SampleId按Ordinal顺序；每次生成新OperationId/AttemptId与新Profile hash，独立执行原冻结路线，不改BaseProfile。
3. 在各work内建误差≤MatchTolerance允许图；每连通分量只有一个truth、一个candidate、一条边才唯一命中；冲突truth记miss、candidate记extra和ambiguous，不解最近邻/最小距离分配。pair以两端同一pair真值匹配，不交换方向。
4. L=wMiss·miss/denominator+wExtra·extra/denominator+wError·mean(error/MatchTolerance)，denominator=max(1,requested)。权重有限非负且和>0，正样本requested>0且matched>0；缺真值/正样本全零匹配不补0，组合不合格。明确标注NegativeConfirmed的负样本允许Truth.Empty：requested=0，用denominator=1只计extra，MeanError=null/无适用误差，误差项为0且不得声称精度为0。校准/验证各至少有一个正样本，不能全负样本推荐。结构/来源/原生/资格错误、截断/不完整/资源超门淘汰组合；合法NoCandidate及多解不是技术故障，依真值计miss/extra，但正样本全部未匹配仍不合格。
5. 校准/验证各以requested加权汇总L；验证集miss/extra/error/资源均过Policy门后，按(校准L,Key)唯一推荐。全部不合格/超预算/来源不足Abstained。报告全部组合/样本/work计数、误差、参数、资源/时间与拒绝原因，不以低拟合残差替精度。
6. 宿主仅在BaseProfile hash仍一致时显式采用为新Draft，再按生产资格审批。取消/超时不返回推荐；已派发计算先进入同一排空/Owner流程。无训练权重、现场学习或生产写入。

误差定义与完整DTO见A.4；性能另按§12同输入比较。pair/单边、灰度/颜色、普通/鲁棒分别报告，不拼成“最佳算子”排名。

## 3. 请求、坐标、参数与输出

### 3.1 不可变输入和合法组合

完整类型唯一见附录A。ImmutableArray必须非default；ID非空、各slot/window/group全局唯一，有限数值/已知enum；零计划拒绝，合法算子零响应才NoCandidate。

| Route | 必需/互斥 |
|---|---|
| MeasurePos/MeasurePairs | Slots非空、Windows为空、Caliper非空/Xld=null；Primitive=None时FitGroups为空；拟合需显式group与观察选择 |
| Xld/ColorXld | Windows非空、Slots/FitGroups为空、Xld非空/Caliper=null；每window计算矩形和资格内区完整 |
| Primitive=None | Fit/Qualification=null；返回原证据，不假造几何 |
| 非None | Fit/Qualification非空，点数下限线2/圆3/椭圆5；参数完整、方法资格引用有效 |
| 目标空间输出 | MapAsset/坐标资格非空，单位/轴/手性明确；逐点映射，域外只拒相应group，不换latest/默认标定 |

Frame Mono8/Mono16/MonoFloat32对应byte/uint2/real，C2用Rgb8Planar/Rgb16Planar，顺序R/G/B，LittleEndian。StrideBytes≥width×每像素字节，PlaneBytes=checked(stride×height)，总长=checked(PlaneBytes×channels)，租约Data长度精确相同。hash包含每行padding原字节；native紧凑副本另诊断，不改Frame身份。float的所有参与支撑像素须有限。C2通道/颜色适用性、采集/曝光/白平衡归宿主资格，不以显示拉伸归一化分析值。

Support.Runs为排序(row,start)的无重叠闭区间像素，必须在同Frame范围且hash对应；空/越界拒绝。校验只读元数据，不提前读取Frame。实际lease复核布局/版本/hash/当前性；来源失效F2D-018。

### 3.2 几何、支撑和方向

Point2D(A,B)：Image A=row/B=column，整数像素中心；Target轴/单位/手性来自Coordinates。SearchV是单位有向搜索轴（长度误差≤1e−6，API数值校验非客户精度），U=(−V.B,V.A)是投影轴；不归一化非法输入。卡尺HALCON major axis=V，Length1=SearchHalfLengthPx，Length2=ProjectionHalfLengthPx，phi=atan2(−V.A,V.B)。模块先按floor(value+0.5)把非负Image中心确定到整数EffectiveOrigin，再把该整数传gen_measure_rectangle2（明确的模块规则，避开native半整数tie未说明行为）；保留请求Origin与EffectiveOrigin，不把小数中心当测量精度。

DescribeSupport依方法资格返回实际采样/插值参与像素包络；bilinear/bicubic至少1/2像素边距，nearest检查实际采样像素。Core逐row-run检查完全包含；measure忽略domain，不能靠reduce_domain去掉无效岛，也不凭3Sigma臆造精确像素贡献域。XLD计算窗口必须全有效，资格内区与计算域分开；边界轮廓BoundaryLimited，保留原点而不是裁断后称完整。无资格影响范围/保守工作集上界只拒该work，不能猜。

XLD response=梯度模，angle=相对row轴的右侧法向，edge_direction相对column轴且非遍历方向；三者分别可空/状态，不填0，不冒充measure有符号幅值。输出原序/parent/segment；反向/闭环起点唯一连续对应才给OriginalIndex，重复坐标多解则Unknown，不能nearest强配。拟合端点/StartPhi/EndPhi只是原首尾投影，非物理断口。

目标拟合先Map全部有效点（同序/单位/长度），再调用同一HALCON固定fit；不只映射输出模型。原始边/对距始终Image px；Target距离另由映射点计算。当前候选不提供目标法向/业务世界极性；宿主若要法向须消费自己的已资格Jacobian（切向Jt、法向J⁻ᵀn）。Coverage只卡尺组以唯一成功slot/计划slot计；XLD另给角覆盖/最大缺弧，不拿内区面积当点覆盖率。

### 3.3 参数有效域

| 字段 | 有效域、来源与变更 |
|---|---|
| SigmaPx/ThresholdNative | Sigma∈[0.4,100]且≤0.5×SearchHalfLengthPx（每slot）；Threshold∈[1,255]为原生尺度，不是生产统一阈值，0无效 |
| Transition/Selection | E1 Positive/Negative/All；E2另可PositiveStrongest/NegativeStrongest/AllStrongest；Selection All/First/Last。Strongest属Transition，不属Select |
| Interpolation | Nearest/Bilinear/Bicubic显式给值；改动重建包络/job，不用旧中心缓存 |
| Canny | Alpha>0，0<Low≤High，有限；Canny Alpha增大平滑增强，不套递归滤波相反意义；灰度/彩色分别资格 |
| Segmentation | None或按primitive映射Lines/LinesCircles/LinesEllipses，SmoothCont固定0；Dist1/Dist2≥0，混合模式Dist2≤Dist1，Lines的Dist2固定0 |
| Fit | Standard=线regression/圆椭圆geometric；RobustTukey=线tukey/圆椭圆geotukey；MaxNumPoints=−1、ClippingEndPoints=0，无抽稀/删端点；Iterations≥0、ClippingFactor>0、MaxClosureDistance≥0 |
| Fit忽略参数 | 普通线与圆、robust圆/椭圆忽略Iterations；椭圆geometric用Iterations，voss未选但占位200；不以Iterations承诺deadline |
| Qualification | MinPoints/Span/Rank、最大缺slot/连续缺slot、MinCoverageRad/MaxGapRad/MaxAxisRatio/NearCircleRelativeGap、残差与4次稳定性上限全部有来源；无资格可继续原边/轮廓诊断，不造默认 |
| Budget/Options | 全部上限显式正数，Queue可0；并发初始1，取服务/请求较小值，不按CPU核数；deadline/借用期限取最早，含排队 |

MaxFitGroups限定group总数；MaxContourPoints为本请求累计保留的original+segment点数（重复副本分别计）；MaxCandidatesPerWork在E1计边、E2计pair与预登记diagnostic边总数、XLD计original/segment轮廓及primitive总数，计数不挑分数，超限按完整项原序停止。native返回点/tuple在适配器复制前检查，若单项放不下返回该work的Truncated和已有完整项，不把巨量托管数组交Core后才发现。MaxResultBytes使用A.2固定逻辑字节计数，不宣称等于CLR heap；工作集预留包含native输入、临时图/句柄、全原轮廓/属性/分段/映射/拟合及托管副本。无法证明单native段容量则执行前拒绝；真实峰值越已资格额度Faulted。达到输出点/候选/字节上限按完整contour/work原子停止、Truncated，不抽稀伪称全集，不在native访问中强杀资源。

### 3.4 结果和归约

保留全部计划WorkId及未执行项、原边/对/距离、原轮廓/分段映射、primitive及证据、原因、Receipt。CandidateId=work/parent/segment/primitive，索引基于当次返回，不声称跨帧身份；比较先核输入/Profile/backend hash。

Validity与ExecutionStatus两层：Completed不等于每candidate有效，更非Pass。Exhaustive表示冻结入口未截断且Select=All，不证明物理全集。终态优先：致命backend/完整性/释放/来源失效→Faulted；计算封口前取消→Cancelled；期限→TimedOut；截断→Truncated；存在有效/诊断观察→Completed；只有歧义→Ambiguous；全部合法空→NoCandidate；全部支撑/资格拒绝→Rejected。每work原因保留；无候选/失败/部分/未执行不能压成同一空数组。

## 4. 生命周期、重复与资源恢复

### 4.1 构造、入口与身份

Features2DService的唯一公开构造见A.3，显式注入frame/backend/mapper/resources/TimeProvider/Options，不用factory/service locator隐藏依赖；ImageLib装配入口见§7。Validate纯元数据；ExecuteAsync是唯一执行入口。GetOperation/Cancel/DrainAsync/CloseAsync/RetryReleasesAsync为明确查询/恢复，不暴露SDK对象。

同服务同OperationId同digest复用在途Task/终态，不再执行、不延长首次deadline；重复调用token只取消其等待，首次token才控制operation。不同digest第二次Rejected/F2D-016，不改变原记录。预检失败ID不占活动账；接纳ID按有界保留策略存档，活跃不逐出，满则接纳前拒绝。已逐出/重启/新实例须宿主用新ID，不承诺跨进程exactly-once。等待取消用Task.WaitAsync，不冒充取消native。

### 4.1.1 UTC接纳与单调执行截止（C1b；推荐共用）

时间类型与有效域固定：所有Deadline均为`DateTimeOffset`且Offset=TimeSpan.Zero（UTC）；默认值/MinValue/MaxValue及输入解析中的NaN/Infinity/“无限”哨兵均非法F2D-001。此.NET类型本身没有无穷值，JSON/宿主解析不能把无效时间改成MaxValue继续执行。新请求接纳时，Budget/Frame/Coordinates三个Deadline各须在当前接纳UTC之后，checked剩余时长满足`0 < remaining <= TimeSpan.FromHours(24)`；任一过期/相等在副作用前Rejected/F2D-011，超24h/无法相减/时间类型非法Rejected/F2D-001。Image目标的坐标借用虽不启用，该字段仍必须满足相同元数据时间域，不留无限哨兵。推荐Deadline按相同24h域；它的每个子请求还受各自来源Deadline与父推荐单调停止意图约束，不能因重新派发延長原推荐。

接纳Owner临界区内、在RequestAccepted/排队/Reserve/Acquire/Open之前，先记录`t0=TimeProvider.GetTimestamp()`，紧接着`u0=TimeProvider.GetUtcNow()`；前置结构/支撑描述均无资源副作用。要求TimestampFrequency>0、u0为有效UTC。计算`remaining=min(Budget.DeadlineUtc,Frame.BorrowDeadlineUtc,Coordinates.BorrowDeadlineUtc)-u0`，固定保存(t0,u0,remaining)，同时将u0写Receipt.AcceptedUtc。两次读取不是原子快照；timestamp先取的间隔只保守缩短可用时间，不补偿/延長。每个时间值相减、时长与附加字节预算均checked，失败在接纳前拒绝。

运行、排队、派发和计算封口只检查`elapsed=TimeProvider.GetElapsedTime(t0,TimeProvider.GetTimestamp())`与冻结remaining；`elapsed >= remaining`即TimedOut意图，含排队。elapsed必须非负且不小于该operation上次观测值；时钟提供者违反单调约定F2D-015/Faulted，不继续有效计算。以该TimeProvider.CreateTimer安排有限唤醒，回调到达仍以GetElapsedTime重核；不能仅用UTC相减、Task.Delay默认系统钟或睡眠轮询决定执行截止。定时器/取消意图也归原operation Owner，结束后解除，不能后台遗忘。

墙钟回拨/前跳都不重算remaining、不重置t0、不延長或缩短**执行deadline**。来源当前性仍在各阶段/封口前由RequireCurrent核对：传入`currentnessUtc=max(u0+elapsed,TimeProvider.GetUtcNow(),previousCurrentnessUtc)`（加法checked），并存回非递减值；因此回拨不能使租约“重新有效”，前跳可由提供者提早判借用过期/撤销而F2D-018，但不是把执行remaining改写了。更不能用该currentness时间重新续租。租约失效后仍保留在用数据保护至真实排空/归还；期间仅禁止有效结果，不能强制释放native。TimeProvider异常/时间加法溢出视完整性错误F2D-015并走Owner排空，非假成功。

同ID已准入且digest相同的重复调用直接复用首次(t0,u0,remaining)/Task；不以新的Deadline/墙钟重新接纳，不因第一次已到截止点就给第二次另起运算。时间格式/哨兵仍须元数据校验，重复合法日期可以不晚于当前墙钟，但不会延長原截止。Drain/Close/Retry/Wait的timeout有效域为`0 <= timeout <= 24h`，TimeSpan.InfiniteTimeSpan/负值/MaxValue/溢出拒绝；它们各以调用当次GetTimestamp+GetElapsedTime冻结自己的有限等待，不改operation执行截止或释放Task，waitCancellation只结束该次等待。

### 4.2 状态和释放

OperationPhase=Validating/Queued/Running/Draining/Terminal；Accepted、DrainCompleted、ResourcesReleased是事件，非第二套终态。接纳前拒绝无native无租约，结果Rejected；队列满F2D-009。已接纳Queued→Running（实际开始）→Draining→真实native及受控内部回调退出→逆序释放→ResourcesReleased→唯一Terminal。Queue取消也走空资源排空，不发虚假ExecutionStarted。

获取顺序：工作集额度→frame→Target coordinate→job；释放job→coordinate→frame→额度。native任务退出（正常/异常/取消）才表明不再用租约；RequestCancel仅意图。停止派发新work，保留在途owner/lease。释放失败或释放任务未返回时保持Draining，执行Task仍pending、不发ResourcesReleased；更低层依赖不先释放。Retry只重试已结束且失败的同一项，不重复启动仍在途Dispose；成功项不再释放。所有提供者必须幂等释放且失败可保留重试对象。恢复后最终仍Faulted/F2D-013，不把清理恢复变计算成功。

封口在Owner锁中核cancel/deadline/frame与coordinate RequireCurrent，复制完整托管结果；之后取消不改计算意图，释放故障仍优先Faulted。来源失效不换latest，原保护义务延续至归还。所有native资源归job，Core只持opaque接口；服务Dispose不销毁宿主依赖。

### 4.3 有限等待、关闭与事件

DrainAsync(timeout,waitToken)观察调用时已接纳集合，timeout有限≥0（0立即），Drained仅集合全终态；持续新请求不改变该次集合。Close立即停接纳、请求本实例活动/队列取消，再有限等待；DrainUnknown仅一次等待结果，非ExecutionStatus。未知或失败释放期间宿主保留服务/账/依赖，可以继续查询/Retry/Close，不能因UI隐藏丢Owner。关闭后F2D-017，不能Reset/Reopen。DisposeAsync不启动无限等待：仅已Drained可成功；未Drained抛Features2DPortException(ResourceFailure)，保留Owner和对象，调用者须先有限Close/恢复。此异常不表示已销毁。

每service事件经有界串行调度，OperationId/Generation/单调Sequence/UTC/work/error。顺序：RequestReceived→ValidationCompleted→Rejected，或Accepted→实际ExecutionStarted→work/progress→可选cancel/timeout→DrainStarted→DrainCompleted→ResourcesReleased→Terminal。native/Owner锁外投递，不等待用户IProgress回调；慢/抛异常/重入不能阻清理。进度可合并，非进度满队列时记投递缺口，GetOperation/Receipt保全部生命周期权威；不承诺无限队列或无法实现的必达回调。终态后无进度，旧generation不得覆盖新请求。事件比例按预登记work数单调，取消不将未执行计完成。

## 5. 错误、线程与所有权

ErrorCode数值n对应F2D-nnn，DetailKey为本模块三语资源key，调用者按enum处理。固定DetailKey集合为F2D.001～F2D.019及F2D.Limit.{Candidates,Points,ResultBytes,WorkingSet,Queue}；native长诊断不塞DTO，写宿主日志引用，不能无界增长。

| 编号 | 语义/恢复 |
|---|---|
| 001 InvalidRequest | 空/非法身份、数值、计划；修正新请求 |
| 002 UnsupportedCapability | 不属本API（legacy Metrology/脊线等）或backend路线不匹配；不是封装缺算子 |
| 003 FrameUnavailable | 指定来源/租约不可得；重新获取正确输入，不换latest |
| 004 SupportInvalid | 岛/边距/参与包络不完整；拒相应work，重建计划/来源 |
| 005 CoordinateInvalid | 单位/域/标定不适用；不输出有效目标几何 |
| 006 NoCandidate | 冻结路线合法零返回，非物理无边证明 |
| 007 AmbiguousAssociation | 多个局部解释；保留原观察，宿主决策 |
| 008 DegenerateFit | 点/秩/覆盖/模型/稳定性不足；留证据 |
| 009 BudgetExceeded | 接纳超结构/容量拒绝；输出截断留已完整证据 |
| 010 Cancelled / 011 TimedOut | 请求取消/期限；待真实排空/归还 |
| 012 NativeFailure | 后端异常/非法返回，留阶段/原诊断 |
| 013 ResourceFailure | 获取/释放/峰值故障；原Owner恢复，不重复仍在途释放 |
| 014 VersionMismatch | 引用/hash/契约/backend不符，不读旧缓存 |
| 015 InternalInvariant | 基数/索引/有限性/状态不变量破坏，拒结果 |
| 016 IdentityConflict | 同OperationId不同内容，原任务不受影响 |
| 017 ServiceClosed | 关闭中/后拒接纳；恢复排空后新实例 |
| 018 SourceInvalidated | 租约撤销/过期/断连，禁止封口有效结果，原租约排空后归还 |
| 019 RecommendationAbstained | 缺真值/范围/预算/验证合格组合，不改生产值 |

服务有有界队列/并发/保留与事件容量，单job仅一个native调用在途；并发slot需各自job和额度，不能共用可变测量handle。Core无可变静态状态。A/B服务可共享只读提供者，不Dispose彼此依赖。宿主控制UI Dispatcher；算法无隐藏窗口/Dispatcher依赖。

Open部分失败必须返回可追踪Job与Error（A.3），不能把资源丢在异常后；frame/coordinate/reserve获取若未交回租约，提供者负责保有未交付的失败Owner，其Acquire任务不能以“失败”遗失资源。模块不重连相机/设备、不越权清源。

## 6. 逐方法执行与两轮反例

### 6.1 提取与分段

E1/E2依次验证半长/方向/尺度/插值→DescribeSupport与逐run包含→借用当前帧/额度→固定native参数→tuple基数/有限性→复制原序/距离→close_measure。t=0,1,3,4夹具E1三相邻距1/2/1，E2两对内1/1、对间2。E2 diagnostic先预登记，不建立猜测的pair↔diagnostic原索引；只在唯一位置/极性一致且距离≤MatchTolerancePx时另输出关联。

C1/C2逐Window原分辨率裁剪（整数offset记录）→CPU Canny→原点与三属性→回加offset→可选分段→原索引映射→内区/边界资格→逐点目标映射→单primitive。裁剪不改通道/位深；窗口内部无效岛拒绝，不填洞/reduce_domain掩盖。合法无轮廓NoCandidate，多轮廓保留至原子输出上限。

SmoothCont=0；小于3px或6点的原轮廓原样复制，不当分段成功。读取cont_approx（−1线/1圆弧/0椭圆弧），不符请求只给原轮廓/NotAvailable，不用else猜圆。每parent单独分段，不跨parent/window拼点。允许反向/闭环起点的唯一连续映射，重复坐标多解则Unknown；无原索引不声称完整原点覆盖/被删集合已证明。

### 6.2 显式拟合支撑

卡尺FitGroup.SlotIds固定顺序，Observation为Edge/PairFirst/PairSecond/PairCenter。E1仅Edge，E2仅三个Pair选项，Center=(First+Second)/2是宿主显式定义的几何候选点、非独立实测边。每slot必须恰有一个所选响应；多边/多pair整group Ambiguous，不取最高幅值/最近名义点。缺slot仅按Qualification.MaxMissingSlots/MaxConsecutiveMissingSlots允许受限拟合并留完整分母；所有slot仍在Work结果。

XLD每候选仅一个连续原轮廓/segment；RequiredInnerRect外有点则BoundaryLimited，不裁去这些点拼成“完整”。边界受限候选最多InsufficientSupport，原轮廓可诊断。已关联的无分段单primitive也遵守同规则。

拟合前有限/不同点数/MinSpan与中心化scatter检查；按最大跨度尺度归一防大坐标平方溢出。lambdaMax=0拒绝；Circle/Ellipse须lambdaMin/lambdaMax≥MinRankRatio；Line只要求非零span，不以二维满秩拒真直线。重复点保留证据，不计作更多不同点。FitInput按完整原序构造gen_contour_polygon_xld，主fit与四次挑战均同一固定方法，无抽稀/删端点。

### 6.3 输出模型、残差和稳定性

| 类型 | 固定证据与有效资格 |
|---|---|
| Line | Begin/End为原首尾投影，另给全部点最小/最大支撑投影；Nr/Nc单位法向，方程A·Nr+B·Nc−Dist=0；标准符号Nr>0或Nr=0且Nc≥0，三者同号翻转；无业务材料法向 |
| Circle | center/r>0/Start/EndPhi/PointOrder；signed δ=norm(p−c)−r；有序角度解包计算覆盖/最大缺弧，不能拿拟合输出2π填缺口 |
| Ellipse | Radius1≥Radius2>0，Phi沿HALCON坐标约定，与输出A/B轴声明一起保存；geometric距离用dist_ellipse_contour_xld(MaxNumPoints=−1,ClippingEndPoints=0)全输入点MeanAbs/MaxAbs；RMS/逐点残差本版NotProvided，不能假造单点XLD支持 |

Line signed δ=A·Nr+B·Nc−Dist；线/圆RMS=sqrt(mean(δ²))、MeanAbs/MaxAbs同单位，按完整InputPoints复算。Ellipse以native官方全点距离统计核资格，不以代数距离/bisec近似冒称正交距离。robust内部权重未公开时BackendInliers=null；本版不提供native被剔除点，DiagnosticExcluded仅线/圆按MaxAbsoluteResidual标诊断，不删原点，Ellipse为空+NotProvided。

模型角坐标固定：circle theta=atan2(−(A−centerA),B−centerB)；ellipse q1=−sin(phi)·dA+cos(phi)·dB，q2=−cos(phi)·dA−sin(phi)·dB，theta=atan2(q2/b,q1/a)。Target也是以其A/B数值代入HALCON row/column槽的同一数学约定，不能偷偷改角符号。圆/椭圆按顺序点相对模型参数角解包，闭环才计末首段；相邻差用(−π,π]规范，若恰π则方向不唯一/InsufficientSupport；Coverage为已观测连续角跨度≤2π，MaxGap为最大相邻角差及未闭合缺弧max(0,2π−跨度)。闭环重复首点只作闭合证据不双计；来源断点不能拼。MinCoverage/MaxGap/MaxAxisRatio来自方法资格，不是工艺放行。近圆(a−b)/a≤NearCircleRelativeGap则轴角null/NotApplicable，不把轴角跳变当缺陷。

四次挑战：原有序点i分别加±StabilityDelta·(−1)^i到A或B，独立A+/A−/B+/B−，不累计；同方法fit，比较圆中心/r、椭圆中心/a/b/可观测轴角、线无向角与Dist和支撑投影变化。角差周期π；线比较前若trial法向与基准点积<0，同翻trial Nr/Nc/Dist，使符号连续，再算Dist差（序列化标准符号不是敏感性门）；中心/端点/半轴/Dist变化取绝对或欧氏长度，全部≤MaxParameterDelta方有效。挑战失败保留原fit但InsufficientSupport。最小反例(−1,h),(0,0),(1,h)：r=(1+h²)/(2h)，h=.010/.011均零残差，r差约4.545；低残差不证明短弧稳定。该有限挑战不是计量不确定度；Uncertainty始终NotProvided。

### 6.4 大图与优化

主性能路线为宿主已定位的原分辨率局部窗口/显式卡尺。粗定位/金字塔可由宿主提供定位来源与回映射生成精测计划，模块不内建全板搜索；缩略图仅显示，不作实测。比较全帧与局部时固定输出内区与真值，覆盖ROI外强边、边距细线、旋转/相位/offset，未证明边界等价不能宣称完全相同。

不自动tile后merge轮廓；跨FOV边界由宿主来源完整性编排，单复合Frame须有精确像素/有效域/坐标来源。缓存键含Frame布局/hash、Profile/Method/backend/坐标版本与完整几何；不热换或重用旧来源。峰值包含全部原轮廓/属性/分段副本、Map点和主+四次挑战；每work及时释放，不能先均匀抽样假称完整。弱边/噪声/遮挡先核有效支撑与方法最小特征宽度资格，Alpha/Sigma增大可能抹细节，不能失败后放宽门限。

### 6.5 两轮有限反例自审落点

第一轮算法反例：半长/全长混用、V反向、E2单侧边、RGB等亮异色、XLD重复坐标/多parent、短弧零残差、椭圆零轴/近圆、非等距物理拟合。分别以§3、§6.1–6.4及T01–T08锁定拒绝/原证据，不依赖“看起来正确”的图或第一候选。

第二轮外部接入反例：同ID改内容、队列取消、native迟到、来源撤销、部分Open失败、Dispose未返回、Retry重复启动、事件回调阻塞、关闭期间新请求、回执满、建议全零匹配/过期、UI旧代次/权限撤销。以§4–5、§7–9、A.3–A.4和T09–T22闭合；保留原Owner/Task与有限观察，不填0、不提前还Frame、不让模拟变生产证据。本节记录规格审查，不声称运行了实现测试。

## 7. 端口、装配与版本

附录A是唯一端口。Core负责纯校验/队列/支撑包含/唯一关联/映射顺序/资格/归约/建议；ImageLib负责元数据DescribeSupport、固定提取/分段、固定HALCON拟合/椭圆距离与native资源。backend不直接决定ValidCandidate，Core复核原始基数/资格。

DescribeSupport无native/图像副作用，依MethodAsset给每work参与run、EffectiveOrigin和保守working-set字节；没有资格就显式work错误。ImageLib内部HObject/HTuple生命周期不泄漏。窗口内区资格/容量Rule算法见A.3，输入参数来自明确Rule而不是编写者临时猜。Open返回BackendOpenResult，成功Job非空/Error=null；无资源失败Job=null/Error非空；部分资源失败Job非空/Error非空，Core登记后Draining。已有job的Extract/Fit异常不能遗失该job。

生产装配类型固定`Asun.Modules.Features2D.ImageLib.ImageLibFeatures2DBackend`，唯一构造为`ImageLibFeatures2DBackend(BackendQualification qualification)`；qualification为A.3纯托管资格数据（边界影响域/资源上界由目标方法资格建立，不由用户随意填），无native初始化副作用。其Descriptor.Version必须与Profile.RequiredBackendVersion一致。服务以`new Features2DService(frames,backend,mapper,resources,TimeProvider.System,options)`构造；不另设未定义factory。所有dependencies归调用宿主，服务只释放自己借用的job/leases。

### 7.1 A1：AsunImage适配器的确定装配

A1沿用§7与A.3的唯一构造，不增加factory/options/session公开类型。装配入口为`new ImageLibFeatures2DBackend(qualification)`；它保存纯托管、深度不可变的资格和Descriptor，不拥有native对象、第二调度队列或应用级静态状态。并发/事件/缓存options只有Core `ServiceOptions`；输入、支撑与单请求额度仍在`Features2DRequest`。本模块的执行session就是Core service的operation Owner及其`IFeatures2DJob`，不是另一个需要宿主猜测关闭方法的服务。

宿主装配顺序：创建自己拥有或借用的`IFrameSource`、`ICoordinateMapper`、`IWorkingSetSource`→提供已冻结的`BackendQualification`→创建上述backend→显式创建合法`ServiceOptions`→`new Features2DService(frames, backend, mapper, resources, timeProvider, options)`→可选`new Features2DRecommender(service, timeProvider)`。两个宿主各自执行这条链（§9.2）；生产timeProvider为`TimeProvider.System`，模拟使用§9.1受控实例。service构造快照Descriptor，Validate核Profile/backend/资格精确版本；backend无需另设Dispose/Close，全部native生命周期归job。服务真正Drained后才Dispose service，再按宿主本身所有权关闭源；借用源不关闭。

Owner边界：Core operation强持全部Acquire/Open/Extract/Fit/Dispose原Task、job引用、frame/coordinate/working-set lease和计算封口责任；job持有本次Open产生的native图像/measure/XLD/tuple及每work的中间对象；提供者继续拥有底层源、坐标事实和资源额度。单job同一时刻一个native调用；并发slot按§5分别Open独立job并预留额度，不共享可变handle。后台调用由已接纳operation追踪，不启动脱离Owner的线程。RequestCancel只记录协作取消意图；超时/取消/native异常都先等待实际访问退出，再复制结果/释放；迟到job或lease先登记，之后job(s)→coordinate→frame→额度逆序归还。native handle、HObject、HTuple和任何SDK对象不穿Core，也不附在Result/Event/Exception公开DTO中。释放失败或未知保留同一Owner/对象/原Task，禁止重建服务或重新提交以绕过未完成归还。

`DescribeSupport`必须在Open前完成；没有A1真实资格、边界影响域或native峰值证据的Rule不提供生产支持，模拟backend的Descriptor.IsSimulation=true（qualification没有模拟字段，不造该字段）。`OpenAsync`成功/无资源失败/部分失败严格沿A.3的Job/Error三种组合；Extract/Fit失败由Core保留原job并排空，不假称Fit返回job。ImageLib只经公开`ImageLibDotNet.cv2`调用§2.2路线；不猜AsunImage类型/重载/封送，不扫描内部、不重审算子覆盖。仅具体C#签名确有歧义时查公开签名或消费编译；未解决只阻对应调用的A1准入，不阻Core/其它已确定路线，不用空实现或运行时假成功填门。

### 7.2 W1上游视口公开桥（沿用U1切片）

本轮W1指§1.3既有U1的公开装配/消费者补充，不新增切片/工程。只读依据为[viewport §3.3/4.6/10.6/15.2](../viewport/DEVELOPMENT-GUIDE.md)及[ROI附录A.6](../roi-geometry/DEVELOPMENT-GUIDE.md)。宿主从`IViewportProcessRoot.CreateFactory()`取得`IViewportFactory`，调用`Create(ViewportOptions)`；显式提供`ConsumerId`、`AccessMode`、`RequestedFeatures`、`IFramePort`、`ICoordinatePort`、`IAuthorizationPort`、`MaxDisplayBytes`、`MaxInFlightTiles`和`ResourceAdmissionMode`。RequestedFeatures必含Navigation；真实WPF另显式启用Presentation并注入相应port/backend，Probe/ROI按能力传入，不能仅因port非null就授能力。在线/生产或共享池使用Required和真实ResourceAdmission；仅明确离线显示可用BudgetOnly，不自动降级。端口/预算/root由宿主拥有，Editor只借用A.5的`IFeatures2DViewport`投影桥，不引用上游私有VM、GPU/native handle或私有端口。

装配顺序：root→factory→无参`ViewportControl`→同控件的backend/lifetime/presentation端口→session（Create无资源，Presentation接同Control.Presentation或Host直接转发器）→`IViewportControlBinding.BindAsync(session, root, ViewportUiBindingOptions, ct)`安装空控件并保存原Task/返回binding（显式Lifetime与UI ExecutionBudget）→`session.AttachAsync(ViewportContext(Sources, Layers, Authorization, Language, Version, ContextRevision, InitialView), ct)`一次→成功后创建宿主私有`IFeatures2DViewport`桥→无参Features2DEditor并Attach A.5 binding。先Bind后Attach避免Presenter互等；Attach失败/取消的session不复用，先按原回执排空。空Sources是空视口，不能改为可测帧；原Task、cleanup及事件均由各自root/宿主保留，不以显示成功证明算法结果。WPF Assembly Contract v0.2的精确消费见§8.7.1；Core API版本不变。

桥绑定完整Frame.Asset/Generation、源Descriptor/SourceRevision、坐标引用、AttachmentId/Epoch与viewport显示Generation；本地token关联原值，不截断其它模块修订。Show只在Dispatcher做有界投影入队，不阻塞等待native/呈现；桥按viewport原root任务槽规则持有Apply/Dispatcher原Task及payload，直到已确认不再呈现/访问。来源切换用`UpdateAsync`全量上下文、只读层替换用`ApplyAsync(SetLayersCommand)`、探针用`ProbeAsync`，关闭用有限`DisposeAsync(timeout, ct)`；不存在借Editor.Close关闭上游的通道。SetLayersCommand是全量Replacement，不是按层增删；同session的宿主串行层投影Owner按每binding独立LayerId集合合成完整Replacement，Clear只去掉本集合并保其它集合，拒绝ID冲突/过期显示代。聚合账只是有界显示投影，不是第二事实库；各Apply原Task/失败回执保留，不能并发读改写丢B层。

叠加只用公开`OverlayLayer/OverlayPayload`的SourcePolyline/Label及已确认ROI投影：原轮廓/slot方向/窗口边界按源整数中心(column,row)保原有序点，LayerId显式关联WorkId/CandidateId，不能用数组序号当事实身份。Support缺口只绘原run/原Owner mask，不将包围框作为Full；几何模型显示采样只是投影，不回流拟合点/测量。桥的SelectionChanged由对应稳定ID产生，不调用Core算法；数值结果仍完整。`IRoiPort`已确认有HitTestAsync/ValidateDraftAsync/CreateCommitCandidateAsync，`RoiGeometrySnapshot`保ObjectId/Kind/Revision/Center/Width/Height/AngleRadians/Rings/GeometryAssetRevision；它是上游扁平投影，不能重建完整ROI事实。默认Features2D桥ReadOnly且不启RoiEditing；宿主需要编辑时另接ROI原Owner的公开桥，明确EditableDraft+RoiEditing+当次权限。精确转换/签名或形状不能保真时只拒对应编辑能力，不造ROI类型、复制解算或把Preview当生产数据。

`OwnSession=false`时viewport binding.Unbind只撤本UI借用/订阅/呈现，不关闭共享session；`OwnSession=true`才由创建宿主在所有UI scope真实完成后、slot外调用同一session.DisposeAsync。Features2DEditor既不拥有viewport session，也不拥有Features2D service；未知关闭必须保留两边原Owner，详见§8.5，不能因窗口Unloaded推断已归还。

Module API Contract=0.2；0.x期间Minor变化也要消费者显式接受。字段/单位/状态/资源语义改变修订本指导与版本、跑受影响回归；不是用候选平台Schema替代Core。输入/Profile/Method/backend/标定同operation固定，不热换；升级双读同输入新attempt、旧结果只读，回退选旧包保留新诊断。未知版本F2D-014，不静默反序列化默认值。

### 7.3 A1：CPU 导入、窗口偏移与原生资源实施顺序

本节补§7.1的内部实现，不新增公开类型或算法。依据26.05官方 [gen_image1](../../../halcon算子手册/operators/gen_image1.html)、[append_channel](../../../halcon算子手册/operators/append_channel.html)、[crop_part](../../../halcon算子手册/operators/crop_part.html)、[count_obj](../../../halcon算子手册/operators/count_obj.html)、[select_obj](../../../halcon算子手册/operators/select_obj.html)及§15.2已有提取/拟合页面；直接经cv2使用。所有步骤在operation追踪的后台任务内执行，不能在Dispatcher执行native或释放。

1. Open先创建本次私有job资源账，再核frame.Frame与请求完整引用、Data精确长度和全部字节hash；RequireCurrent不替代hash。计算RowBytes=checked(width×bytesPerSample)、PlaneBytes=checked(stride×height)、CompactBytes=checked(RowBytes×height)。Mono为一plane、RGB为R/G/B三plane；不把planar数据传成interleaved，不改位深/强度。额度须同时覆盖原Data借用、紧凑暂存、native各plane/组合/裁剪和后续结果，不只算最终图像。
2. 每plane按源偏移checked(plane×PlaneBytes+row×stride)复制恰好RowBytes到本plane紧凑buffer；padding不进入HALCON，但仍在原Frame摘要中。分配前核Array.MaxLength及预留额度，checked溢出是F2D-009；合法预算下实际分配失败为F2D-012/013并排空，不假称预检成功即不会OOM。MonoFloat32参与支撑内非有限值拒绝，域外值不变成有效支撑。
3. 紧凑buffer以受控pin保到cv2.gen_image1真实返回/抛出；Type依次byte/uint2/real，传实际IntPtr，不截成int32，不传指针变量地址。gen_image1新建HALCON存储，返回后才解pin和退暂存份额；调用pending时不因取消解pin。RGB逐plane导入后按R→G→B用append_channel组合，组合只是matrix引用，不是像素深拷贝。每个返回iconic立即入账，全部相关对象保持到最后使用退出；不使用gen_image1_extern或copy_obj宣称深拷贝。
4. E1/E2使用完整原分辨率图像和§3.2整数EffectiveOrigin，gen_measure_rectangle2的Width/Height为该图实际尺寸；V/半长/phi/插值按固定映射。MeasureHandle交付即登记，调用固定measure后先核tuple基数/有限性/容量，再复制托管值；close_measure成功才将该handle标已关闭。控制tuple本身Dispose不替代close_measure；关闭失败保原handle和释放账，不再Extract同work。
5. XLD每ComputeRect调用crop_part(Row,Column,Width,Height)，先确认矩形完整在原图且RequiredRuns已覆盖，不能接受其越图自动裁域语义。Local(row,col)仅在变成源图证据时加一次(RowOffset,ColumnOffset)；属性值不加offset，segment到original的对应在同一坐标空间建立。每parent用count_obj确认数量、select_obj按1基索引逐个选取；select_obj也只是引用。原/分段点和属性逐项容量核对后复制，不能先复制无界tuple；父、selected、segment对象分别入账。目标Map输入为回加offset后的源整数中心坐标。
6. FitInput已在所选GeometryContext中；gen_contour_polygon_xld使用A→Row/B→Col，不再加图像offset，不因Target单位再缩放。主拟合及四挑战分别建本次contour/tuple，固定§2.2/§6路线；原始支撑不被robust权重或挑战覆盖。输出几何及椭圆距离复制完成后，释放本次临时对象；job仍是最后兜底Owner。
7. 释放按依赖逆序：控制结果tuple/拟合及分段selected/iconic→measure显式close→裁剪/组合图→导入plane；仅已成功释放项移出账。每步幂等检查本地完成标记，异常不跳过其它可安全释放项，失败项保留原对象供同job重试。native调用未退出时任何依赖均不可销毁。Open零资源失败返回(null,error)，部分失败返回(job,error)；Core先登记该job再排空，不把部分Open异常变成遗失资源的throw。完成后仍按A.3归coordinate/frame/额度，不能把gen_image1拷贝成功当源lease已归还。

有限反例复用T02/T09/T12/T13/T15：stride大于RowBytes的同像素帧保持不同原hash；RGB三plane次序不能互换；crop(100,100)内点(20,10)只回源(120,110)一次；select_obj首项为1；第二plane导入失败仍交原job；取消发生在gen_image1返回前保持pin；close_measure失败不由tuple析构伪报已释放。上述为实施断言，未执行真实HALCON。

### 7.4 图像、ROI 与坐标的精确消费桥

消费桥是宿主实例私有adapter，分别实现A.3已有端口；不新建事实服务或第二算法库。上游只读依据为[image-frame §4.3/4.4/19.1](../image-frame/DEVELOPMENT-GUIDE.md)、[roi-geometry附录A.4](../roi-geometry/DEVELOPMENT-GUIDE.md)、[coordinate-geometry §4.3](../coordinate-geometry/DEVELOPMENT-GUIDE.md)。Core v0.2、图像Resources v0.1、ROI v0.3和坐标v0.2是各自契约版本，不互相替换。

**图像。** 宿主绑定表在执行前封存完整FrameKey(Guid,ulong)、SourceId/SourceRevision、CoordinateReference、选中plane/通道顺序、元数据/有效域、F.FrameRef和采集资格；绑定表是有界引用映射，不取latest，不把ulong修订截成long Generation。Generation由本宿主独立输入代给出，并保完整来源修订。Acquire以新Guid RequestId调用原IFrameService.ReadAsync(new FrameReadRequest(RequestId,ConsumerId,Key,PlaneIndices,new PixelWindow(0,0,width,height),0,RejectMissingSupport,ExactSamples,剩余期限),ct)，保存ServiceEpoch/原Task。重复Read只回receipt而Slice=null，不能据此生成第二lease。

拿到Slice后核SourceKey/SourcePlaneIndices/CoreWindow/ActualWindow/Layout/Metadata和额度；仅完整level0、原尺寸、所选标量强度通道可接本版。用TryOpenReadScope在同scope中逐行CopyRow，目的Span长度恰等源RowBytes；scope.Dispose在复制退出的finally执行，禁止泄漏源Memory或指针。上游CopyRow不提供padding，因此本桥**不能复原任意原stride bytes hash**：宿主在形成F.FrameRef前明确封存紧凑派生快照，StrideBytes=width×bytesPerSample，Data为所选通道R/G/B的独立planar连续字节，Asset.Sha256对其真实全部字节计算；源引用/域/通道映射保绑定中。若原输入要求原padding身份，则只接确能提供那些原字节的原Owner端口，拒绝用补0伪造同hash。源交错多通道仅做声明布局的逐标量无损拆plane，不能颜色变换/归一化；未知布局、Float64、物理Height或Scale/Bias非1/0不在本桥当前强度输入域。

派生快照和Source binding在宿主既有输入额度内先建成，CopyRow不是隐藏在Core未预留阶段的无界分配。实际执行Acquire交该不可变Data及其独立源borrow，原source lease保持至本F.lease真实Dispose；Dispose先封新访问并等所有本地scope/native退出，再启动一次原ReleaseAsync(有限观察期限)并留Task。仅LeaseClosed=true、Error=None、Drain=Drained确认本borrow归还；StorageReleased=false可合法。pending保同lease，既有释放Task退出后才可同lease幂等重新观察；异常/未知不销账。QueryOperation原epoch/id的NotFound不证明没执行；未交付资源责任由原提供者继续保留。

**Support。** 宿主从ROI原Owner取得指定Frame的RasterizedRegion lease，MaterializeAsync(new RoiMaterializationRequest(新OperationId,已预留MaxBytes,原MonotonicDeadline),ct)后须Completed、IsTerminal、ResourcesReleased且无错误；否则保原materialize/lease，用QueryMaterialization/DrainAsync继续观察，不从opaque GeometryAssetRevision猜runs。Grid须与源Frame一致：Width/Height相同、Origin=(0,0)、StepX=StepY=1、单位Pixel整数中心，Physical先经原坐标/ROI路线显式投影，不能改Grid标签完成变换。

物化RoiRun.EndColumn与F.PixelRun.EndColumn均为**闭端**，本桥不加1。image-frame的DomainRow.EndXExclusive则是半开，非空段转换为闭端须checked(EndXExclusive−1)，Full域明确展开本帧行宽，Empty域直接拒绝。宿主显式选择对象集合，投影为同Frame合法row-run并规范排序、合并重叠/相邻段，保原ObjectIndex/ROI资产出处在binding；这只是离散集合规范化，不做ROI布尔或栅格化算法。与图像全部选中plane有效域作交集，不取有效域并集；§3/A.3再核每work完整支撑包含。Support.Asset.Sha256只对最终规范run的`row,start,end\n`真实UTF8字节计算，不沿用ROI opaque资产hash。空交集在执行前F2D-004，不称算子NoCandidate。Materialize临时ResourcesReleased不证明原ROI lease归还；宿主完成托管快照后仍按原Owner确认该lease排空，未知保留，不能关闭借用Backend/Core。

**目标坐标。** Image目标不Acquire坐标lease。Target adapter绑定MapAsset/Qualification到原完整GraphSnapshot、Source/Target Frame、ExplicitPath、NumericPolicy、BackendRef和有效期限；不从短AssetRef现场补路径，不能偷偷ResolveUniquePath。输入F.Point2D(A=row,B=column)依源Frame明确轴序构造原Point2Value；ImageColumnRow的Point2=(x=B,y=A)，其它轴序显式映射，不能一律交换。整数中心不补0.5，Target只按其声明轴顺序回F.A/B，单位换算归原坐标服务。

每次Map批次产生新且留账的RequestId，GeometryBatch含原有序Point2Value及NoCovariance，调用GeometryRequest("0.2",RequestId,new MapWork(Graph,Source,Target,Path,Batch,NumericPolicy),剩余ExecutionBudget)。原NumericPolicy若要求完整误差而本批次无协方差则明确拒绝，不降级它。Submit Accepted/Duplicate后沿同ServiceInstanceId/id WaitAsync/QueryAsync，只有Found、Completed、Drain=Confirmed及MappedResult完整批次、Graph/Path/Policy/Backend/Source/Target匹配才返；点数/类型/序/有限性/域/轴/单位全部核，整批拒绝不收部分点。CG域/不支持映射F2D-005，来源已撤F2D-018，超时/取消保持F2D-011/010，资源未知F2D-013；DetailKey保原CG诊断定位。

A.3的Map是同步，不能在UI、事件回调、服务锁或上游坐标service自己的执行线程调用。Core operation后台调用该adapter时，adapter创建并登记一个async协调Task，内部全部await使用ConfigureAwait(false)，不捕获调用SynchronizationContext；同步入口只在有界等待预算内等待这唯一Task，不在Dispatcher用.Result。到期/取消只提交一次原CancelAsync并抛对应PortException；**协调Task与原Submit/Wait/Query/Cancel都仍由coordinate lease强持**，DisposeAsync等该批次终态且Drain=Confirmed后才完成，pending保原lease供A.3释放重试。Acquire收到的本operation cancellation登记到lease，取消只定向其原IDs；RequireCurrent校验封存上下文期限/撤销，不调用阻塞IO。没有原Drain确认不能让Dispose完成，不调用共享StopAndDrainAsync，不以新ID重跑未知Map。一个lease一次Map，批次数/结果缓存受请求点数与工作集预算限制；同步等待也计端到端和取消时延，不声称无等待。此桥不复制坐标求解器，公开Core签名保持不变。

有限反例复用T02/T10/T12/T15/T18：源ulong修订大于long.MaxValue仍精确绑定；原stride128与compact100不能沿用hash；ROI闭端[3,5]仍三个像素，空ROI拒绝；Grid非单位/非原点不隐式采样；Map到期后上游Query Unknown必须让coordinate Dispose仍pending；两个共享坐标消费者只取消自身ID。均为软件契约检查，真实上游/算法未运行。

同步桥恢复的明确步骤：Map启动协调Task前先将批次id与全部引用登记在lease账，协调器在独立后台执行上下文开始异步调用，所有原ValueTask只AsTask一次；同步入口以单调剩余预算有限等待，不在上游service调度槽内阻塞自身。Map返回/抛出仅结束本次调用，原Task退出后仍以原operation查询排空。lease.DisposeAsync封Map入口，按每批次原id顺序有限QueryAsync/WaitAsync，Completed/Rejected/Cancelled/TimedOut/Failed均需Drain=Confirmed才清该项；未知/NotFound或观察到期抛F2D-013并保原id/对象/原Task，供Core同lease重试。原查询/取消Task若尚pending先等它，不能并发重复发查询以制造新Owner；原Task已退出才允许下一次有限观察。一个Dispose调用不用后台无限轮询，整个释放未知期间额度和lease责任继续保留；恢复后结果仍按原取消/故障事实封口。此步骤不增加公开Cancel/MapAsync或共享Stop方法。

### 7.5 参数建议的宿主输入与新 Draft 采用

§2.3/A.4是唯一候选评价算法，本节只补输入和操作，不改变loss/分母/唯一图匹配。候选由宿主预先提供有限ParameterCandidate列表及来源；模块不从直方图、曝光或扫描范围暗生候选，不做AI/无限搜索。每项只能替换Caliper/Xld，Primitive/Method/Plan/Fit/Qualification/坐标保持样本原值；同route必须恰有适用参数，其它null，Key唯一且按Ordinal。宿主按明确批准的有限值组合生成时，先checked组合数和全部候选/样本预算，再逐候选调用与Execute相同Validate及DescribeSupport；非法Sigma/Threshold、Canny阈值次序、路线不适用或方法资格域不支持在派发前标明字段/原因，不clamp或换路线。

合法变化严格限§2.3的Sigma/Threshold、Alpha/Low/High和分段距离；ParameterCandidate虽携带完整Caliper/Xld，Transition/Selection/Interpolation/Segmentation模式等未批准变化字段须等原值，不能因DTO能表示就扩大搜索。

校准/验证均非空且各至少一个正样本、样本身份及Frame完整引用不交叉，标注来源独立；同帧不同裁剪或代号不能冒作独立验证。TruthKind/单位一致，真实负样本明确NegativeConfirmed，不把未标注当负例。没有可提供完整真值的任务保持普通执行，建议Abstained；参数和真值不足不能产生“最佳参数”。候选执行次数=候选数×(校准数+验证数)，受MaxEvaluations/MaxResultBytes/工作集/原期限门；只允许全有限组合完成后按A.4推荐。

Editor在宿主SetRecommendationRequest后显示候选Key及差异、校准/验证用途、缺失/额外/歧义计数、MeanError与单位、资源/错误、Eligible及拒绝原因；null MeanError/Loss显示未评估，不能填0或绿色通过。用现有TreeList/PropertyGrid/Chart投影，不增加另一个优化器。采用命令仅在Recommended、CanEdit+CanRecommend、原attachment/epoch/BaseProfile hash和当前Draft全部匹配时可用；它仅把Recommended替换参数及A.4新Profile身份写成新Draft，并走同Validate、增加localUiRevision、清旧采用资格，需另点执行。宿主保存/激活另走自己的Owner，本控件无自动保存/生产更新。撤权、源/参数变化、建议取消/失败或旧结果都禁采用并保原原因；恢复上次Draft仅恢复本地编辑值，不重发未知执行。

解释用“校准误差较小，验证门通过”并列实际数据；不能说“最优”“保证检测”或把残差当置信概率。复用§8.3/8.4三语和权限状态；已有资源需覆盖本节计数/差异/拒绝/采用任务，缺资源按绑定校验拒绝，不回显英文异常。建议时延/子任务释放和数据真值分别验收，不用成功推荐证明节拍或客户准确性。

## 8. 可选高级嵌入 UI

### 8.1 任务流与真实控件

类型`Asun.Modules.Features2D.Ui.Wpf.Features2DEditor`为独立WPF控件，公开装配/权限/代次见A.5；无静态宿主/隐藏窗口。宿主提供frame/plan/Profile、服务、已有公共影像视口接点、主题/语言和权限；运行profile不可编辑，Draft独立，激活生产/持久化归宿主。

流程：加载当前输入→查有效域/来源→编辑Draft→校验→执行→逐work/候选证据→宿主关联/量测。离线建议另经带真值样本→比较全部组合→显式采用新Draft；base hash变化拒采用。“校验/执行/取消/查看证据/恢复上次草稿”清楚可见，无质量判定或设备命令。

唯一1920×1080验证视口；记录扣任务栏、窗口边框/标题/状态后的client，布局按client比例，不改显示设置/另测分辨率矩阵。DockLayoutManager+LayoutGroup/LayoutPanel：顶约56DIP身份/revision/状态/主命令，底约28DIP阶段/排空，中央影像约60%、左计划16%、右参数/证据24%；辅助栏最小宽度/滚动/折叠，先缩辅助栏，图像和取消命令不被遮。统一宿主主题、留白/字号/状态色/图例，不能只以能用代替设计完成。

| 控件 | 绑定与联动 |
|---|---|
| TreeListControl/TreeListView | ItemsSource为work/candidate投影，KeyFieldName/ParentFieldName为稳定ID；多列状态/数量/来源，虚拟化与筛选不改执行分母 |
| PropertyGridControl | SelectedObject为托管Draft；CellValueChanged经同一Validate，字段错误与摘要同步；基础常显/高级资格折叠，Ignored/NotApplicable参数只读不造假旋钮 |
| 宿主公共影像视口 | 原帧、support、slot/V、计算窗/内区、原轮廓/候选分层；树↔叠加双向选择/定位，不改原点/坐标；显示LOD只减渲染，详情/结果保全 |
| ChartControl/XYDiagram2D | Series.DataSource/ArgumentDataMember/ValueDataMember绑定实际response/残差；无真实剖面不造灰度曲线，ellipse仅均值/max则统计卡 |
| SuperTip | HeaderItem/Item/Separator，非Bar用SuperTipControl放Control.ToolTip；说明单位/范围/来源/恢复，关键命令常显不藏菜单 |

以上API来自已读25.2官方页§15.2，未核实的Flyout类型不用于规格。布局保存/恢复由宿主用户设置；布局损坏恢复默认并保留Draft，保存失败不改计算状态。长ID/hash显示缩略、可复制全文；数值列单位常显，提示可读完整值，内容滚动不溢出。

### 8.2 代次、权限与关闭

Attach(binding)携带AttachmentId/Epoch与服务/权限/视口；同一控件仅一个binding。每次Attach或替换Draft增加控件内部localUiRevision（不是Identity.Generation，后者仍等Frame.Generation），所有进度/选择/建议回执先比较attachment epoch+operation ID+input/profile hash，旧回执只留原日志，不覆盖新画面。宿主不复用已Detach epoch。Run生成Guid.NewGuid().ToString("N")新OperationId/AttemptId，保留Frame.Generation/ConsumerAdapterId，不能沿用Draft旧OperationId。权限CanEdit/CanRun/CanRecommend/CanViewEvidence来自binding；UpdatePermissions撤销编辑/运行只禁新命令、不篡改已启动运算，撤销View清空可见证据、保留Owner。取消是对自己运行任务的恢复动作，运行后即使Run撤销也保持可用。

DetachAsync(timeout)立刻禁新命令、取消本控件operation，有限等它排空；服务借用且可能有其它消费者，不能调用共享service.Close或Dispose。DrainUnknown时控件/binding继续保有Owner，宿主保留控件或移交A.5的DetachTicket给自己的关闭管理器；不Unloaded就释放native。ticket.Query/Wait/Retry只作用于本控件操作，不能取消别人。成功detach才移除回调/overlay与借用binding；没有UI也可使用同样查询恢复。服务总关闭由创建宿主单独按§4完成。

### 8.3 键盘与三语

Tab按身份→树→影像→基础参数→主命令→证据；Enter仅执行焦点命令，数值编辑中不启动；Escape退出编辑/选择，不隐式cancel native；Ctrl+Enter校验通过且有Run权限时执行，Ctrl+C复制选中完整值。UIA名称/焦点可见与状态图例同步。SetCulture动态切换不丢Draft/焦点/选择/展开/运行快照；算法序列化始终InvariantCulture，无模块全局语言入口。

| zh-CN | zh-TW | en-US |
|---|---|---|
| 校验 / 执行 / 取消 | 驗證 / 執行 / 取消 | Validate / Run / Cancel |
| 原始证据 / 参数来源 | 原始證據 / 參數來源 | Raw evidence / Parameter source |
| 无候选 / 多个候选，需确认 | 無候選 / 多個候選，需確認 | No candidate / Multiple candidates; review required |
| 支撑不足 / 结果已截断 | 支撐不足 / 結果已截斷 | Insufficient support / Results truncated |
| 正在排空 / 尚未确认结束，请继续等待 | 正在排空 / 尚未確認結束，請繼續等待 | Draining / Completion unconfirmed; keep waiting |
| 释放失败，请重试释放 | 釋放失敗，請重試釋放 | Release failed; retry release |
| 参数已更新，请重新建议 | 參數已更新，請重新建議 | Parameters changed; run recommendation again |
| 权限已变更 | 權限已變更 | Permissions changed |

错误按ErrorCode映射自然短三语资源，带work和下一步；native细节仅诊断页，不以“智能优化成功”夸大。真实WPF验收包括上述操作、DPI、长英文/三语、主题对比/键盘/UIA/代次/权限与关闭；文档本轮不建原型。

### 8.4 错误与状态资源基线

F2D.001～019的默认用户文本如下（WorkId单独列，native长错误不拼入主提示）。F2D.Limit.*复用009并附本地化上限名称；不得直接把enum/资源key显示给操作者。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| 001 | 输入无效，请检查标记项 | 輸入無效，請檢查標記項 | Invalid input; check marked fields |
| 002 | 不支持此请求，请选择已支持的方法 | 不支援此請求，請選擇已支援的方法 | Request unsupported; select a supported method |
| 003 | 图像不可用，请重新加载指定图像 | 影像無法使用，請重新載入指定影像 | Image unavailable; reload the specified image |
| 004 | 采样区域不完整，请调整采样计划 | 取樣區域不完整，請調整取樣計畫 | Sampling area incomplete; revise the plan |
| 005 | 坐标映射无效，请检查标定和单位 | 座標映射無效，請檢查校正與單位 | Invalid coordinate mapping; check calibration and units |
| 006 | 未找到候选，请检查图像和参数 | 找不到候選，請檢查影像與參數 | No candidate found; check image and parameters |
| 007 | 存在多个解释，请查看原始证据 | 存在多個解釋，請查看原始證據 | Multiple interpretations; review raw evidence |
| 008 | 拟合支撑不足，请检查轮廓和覆盖范围 | 擬合支撐不足，請檢查輪廓與涵蓋範圍 | Insufficient fit support; check contour and coverage |
| 009 | 已达处理上限，请查看截断项 | 已達處理上限，請查看截斷項 | Processing limit reached; review truncated items |
| 010 | 已请求取消，正在等待资源归还 | 已要求取消，正在等待資源歸還 | Cancellation requested; waiting for resource return |
| 011 | 已超时，正在等待运算结束 | 已逾時，正在等待運算結束 | Timed out; waiting for execution to finish |
| 012 | 视觉运算失败，请查看诊断后重试 | 視覺運算失敗，請查看診斷後重試 | Vision execution failed; review diagnostics before retrying |
| 013 | 资源处理失败，请查看排空状态 | 資源處理失敗，請查看排空狀態 | Resource handling failed; check drain status |
| 014 | 输入版本不一致，请重新加载同版数据 | 輸入版本不一致，請重新載入同版資料 | Input versions differ; reload matching data |
| 015 | 结果结构异常，请保留诊断并联系维护人员 | 結果結構異常，請保留診斷並聯絡維護人員 | Invalid result structure; retain diagnostics and contact maintenance |
| 016 | 请求编号已用于其它内容，请新建请求 | 請求編號已用於其他內容，請建立新請求 | Request ID has different content; create a new request |
| 017 | 服务正在关闭，请等待排空完成 | 服務正在關閉，請等待排空完成 | Service closing; wait for draining to finish |
| 018 | 输入已失效，请等待排空后重新加载 | 輸入已失效，請等待排空後重新載入 | Input invalidated; wait for draining, then reload |
| 019 | 无可用建议，请检查样本、真值和范围 | 無可用建議，請檢查樣本、真值與範圍 | No recommendation; check samples, ground truth and ranges |

010/011终态已资源释放时分别用“已取消/已超时；资源已归还”“已取消/已逾時；資源已歸還”“Cancelled/Timed out; resources returned”，不继续显示正在等待。013重试清理成功后仍显示运算失败但资源已归还，不把故障改成功。Phase与结果状态资源：校验中/驗證中/Validating，排队中/排隊中/Queued，运行中/執行中/Running，正在排空/正在排空/Draining，已完成/已完成/Completed，已拒绝/已拒絕/Rejected；其余空/歧义/截断/取消/超时/失败复用对应词条。

完整标题/命令/参数/结果/状态/提示/错误/恢复资源由本模块在§8.4.1～8.4.5冻结，不再让宿主或viewport补本模块词条。单位px/rad/mm原符号、Invariant保存与本地化显示分离。

### 8.4.1 本模块完整资源目录与语言切换

以下各表的key统一加`F2D.`前缀；§8.4的001～019原key保持，不另建错误体系。它们是Features2DEditor同版可选UI DLL自身的完整三语资源基线，实施时直接转入该UI工程的三份嵌入资源（zh-CN/zh-TW/en-US），无需宿主提供字典、viewport资源包、资源factory或全局语言服务。本轮只写指导，不生成资源文件。Core只回稳定错误/证据key，禁止含WPF资源加载；Editor读取自身资源，两个STA实例各自Culture，不共享可变current culture。本文是文字唯一权威，历史§8.3简表仍作操作示例，不作为第二词表。

Attach/SetCulture先在本实例内构造完整候选资源/格式快照，核本节所有key与001～019、占位符集合、已用枚举映射，再在Dispatcher一次替换；缺键/格式不合法不部分换字、不以英文异常/enum填空，保旧资源及Draft/焦点/选择/正在执行的输入与Owner。首次Attach缺资源则拒绝且不启动Execute/Recommend/视口工作；没有旧资源时抛技术ArgumentException由宿主显示它自己的绑定错误。非法culture同A.5拒绝；支持文化扩展须在本UI资源目录注册完整快照并同步声明，不修改业务算法。宿主只传Culture/Theme并单独给viewport自己的ViewportUiResources；两控件分别保回执，不将本模块缺键移交viewport。

每个静态标题/按钮/列名/参数显示名/枚举值/状态/图例/空态/SuperTip/UIA Name取下表，禁止直接反射成员名或ToString(enum)。原ID/资产修订/hash/路径/坐标轴名称/来源标识是原值，不翻译；显示在本地化列名下，长值可复制全文。任意宿主ObservationRole、TargetUnit与AxisA/B只作为声明的原标签/单位，不推断工艺含义。UIA AutomationId固定为资源key对应的ASCII控件ID，Name取当前语言；参数各行用`F2D.Field.<leaf>`，主命令用`F2D.Command.<leaf>`，换语言不换AutomationId。超长诊断原文不进主提示，技术详情受权限在诊断区显示。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title.Editor | 二维特征 | 二維特徵 | 2D features |
| Title.Plan | 采样计划 | 取樣計畫 | Sampling plan |
| Title.Parameters | 参数 | 參數 | Parameters |
| Title.Basic | 基础参数 | 基本參數 | Basic parameters |
| Title.Advanced | 高级参数 | 進階參數 | Advanced parameters |
| Title.Evidence | 原始证据 | 原始證據 | Raw evidence |
| Title.Geometry | 几何候选 | 幾何候選 | Geometry candidates |
| Title.Residual | 残差 | 殘差 | Residuals |
| Title.Support | 有效支撑 | 有效支撐 | Valid support |
| Title.Recommendation | 参数建议 | 參數建議 | Parameter recommendation |
| Title.Calibration | 校准样本 | 校準樣本 | Calibration samples |
| Title.Validation | 验证样本 | 驗證樣本 | Validation samples |
| Title.Diagnostics | 诊断 | 診斷 | Diagnostics |
| Title.Recovery | 关闭与恢复 | 關閉與復原 | Close and recovery |
| Title.Version | 来源与版本 | 來源與版本 | Sources and versions |
| Command.Validate | 校验 | 驗證 | Validate |
| Command.Run | 执行 | 執行 | Run |
| Command.Cancel | 取消 | 取消 | Cancel |
| Command.Evidence | 查看证据 | 檢視證據 | View evidence |
| Command.Recommend | 生成建议 | 產生建議 | Recommend parameters |
| Command.Adopt | 采用为新草稿 | 採用為新草稿 | Adopt as new draft |
| Command.RestoreDraft | 恢复上次草稿 | 還原上次草稿 | Restore previous draft |
| Command.Query | 查看排空状态 | 檢視排空狀態 | Check drain status |
| Command.Wait | 继续等待 | 繼續等待 | Keep waiting |
| Command.RetryRelease | 重试释放 | 重試釋放 | Retry release |
| Command.RetryClose | 重试关闭 | 重試關閉 | Retry close |
| Command.Copy | 复制完整值 | 複製完整值 | Copy full value |
| Command.Locate | 定位到图像 | 定位至影像 | Locate in image |
| Command.Close | 关闭 | 關閉 | Close |
| Layer.Frame | 原图 | 原圖 | Source image |
| Layer.Support | 有效区域 | 有效區域 | Valid region |
| Layer.Slots | 卡尺与搜索方向 | 卡尺與搜尋方向 | Calipers and search directions |
| Layer.Windows | 计算窗口 | 計算視窗 | Compute windows |
| Layer.Inner | 资格内区 | 資格內區 | Qualified inner region |
| Layer.Contours | 原始轮廓 | 原始輪廓 | Original contours |
| Layer.Segments | 分段轮廓 | 分段輪廓 | Contour segments |
| Layer.Candidates | 候选支撑点 | 候選支撐點 | Candidate support points |
| Empty.Input | 未加载输入 | 未載入輸入 | No input loaded |
| Empty.Selection | 请选择采样项或候选 | 請選擇取樣項目或候選 | Select a work item or candidate |
| Empty.Evidence | 没有可显示的证据 | 沒有可顯示的證據 | No evidence to display |
| Empty.Profile | 未提供参数来源 | 未提供參數來源 | Parameter source not provided |
| Empty.Recommendation | 未生成建议 | 尚未產生建議 | No recommendation generated |

### 8.4.2 参数、身份、预算与结果字段

本表key=`Field.<leaf>`。绑定列列出A.1～A.4的字段或确定UI投影；同语义字段复用同key。A/B在Image为行/列，在Target使用绑定轴的原名，标题采用AxisA/AxisB并显示原单位，不把所有Target坐标叫行列。`Source/Frame/Support/Profile/Method/Map/Qualification`的AssetRef展开均复用Id/Revision/Hash。计划/参数可编辑性仍由§8权限及§3参数域确定；表内名称不授予字段编辑权。

| leaf／绑定 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Id／所有稳定Id | 编号 | 編號 | ID |
| Revision／AssetRef.Revision | 修订 | 修訂 | Revision |
| Hash／Sha256、RequestDigest | 摘要 | 摘要 | Digest |
| Source／来源资产、SourceId | 来源 | 來源 | Source |
| Frame／FrameAsset | 图像来源 | 影像來源 | Image source |
| SupportAsset／SupportAsset | 区域来源 | 區域來源 | Region source |
| Profile／ProfileAsset、BaseProfile | 参数来源 | 參數來源 | Parameter source |
| Method／MethodAsset、BackendMethod | 方法 | 方法 | Method |
| Map／MapAsset | 坐标映射来源 | 座標映射來源 | Coordinate mapping source |
| Qualification／Qualification、MethodQualification、AcquisitionQualification | 资格来源 | 資格來源 | Qualification source |
| OperationId／OperationId | 请求编号 | 請求編號 | Request ID |
| AttemptId／AttemptId | 本次执行编号 | 本次執行編號 | Attempt ID |
| Generation／Generation | 输入代次 | 輸入代次 | Input generation |
| Consumer／ConsumerAdapterId | 消费者 | 使用端 | Consumer |
| WorkId／WorkId、SlotIds | 采样项 | 取樣項目 | Work item |
| CandidateId／候选Id、Key | 候选编号 | 候選編號 | Candidate ID |
| Width／Width、MaxComputeWidth | 宽度 | 寬度 | Width |
| Height／Height、MaxComputeHeight | 高度 | 高度 | Height |
| Layout／Layout、RequiredLayout | 像素布局 | 像素配置 | Pixel layout |
| Stride／StrideBytes | 行步长 | 列步距 | Row stride |
| BorrowDeadline／BorrowDeadlineUtc | 借用截止时间 | 借用截止時間 | Borrow deadline |
| Route／SamplingPlan.Route | 提取路线 | 擷取方式 | Extraction route |
| Primitive／Primitive、Kind | 几何类型 | 幾何類型 | Geometry type |
| Origin／CaliperSlot.Origin | 请求中心 | 請求中心 | Requested center |
| EffectiveOrigin／EffectiveOrigin | 实际采样中心 | 實際取樣中心 | Effective sampling center |
| Row／Point2D.A、PixelRect.Row、PixelRun.Row（Image） | 行 | 列 | Row |
| Column／Point2D.B、PixelRect.Column、StartColumn/EndColumn（Image） | 列 | 行 | Column |
| StartColumn／PixelRun.StartColumn | 起始列 | 起始行 | Start column |
| EndColumn／PixelRun.EndColumn | 结束列（含） | 結束行（含） | End column (inclusive) |
| SearchDirection／SearchV | 搜索方向 | 搜尋方向 | Search direction |
| SearchHalf／SearchHalfLengthPx | 搜索半长 | 搜尋半長 | Search half-length |
| ProjectionHalf／ProjectionHalfLengthPx | 投影半长 | 投影半長 | Projection half-length |
| ObservationRole／ObservationRole | 观察角色 | 觀察角色 | Observation role |
| ComputeRect／ComputeRect | 计算矩形 | 計算矩形 | Compute rectangle |
| InnerRect／QualifiedInnerRect | 资格内区 | 資格內區 | Qualified inner region |
| Observation／FitGroup.Observation | 拟合点来源 | 擬合點來源 | Fit point source |
| Sigma／SigmaPx、MinSigmaOrAlpha/MaxSigmaOrAlpha（卡尺） | 平滑尺度 | 平滑尺度 | Smoothing scale |
| Threshold／ThresholdNative | 最低边缘幅值 | 最低邊緣幅值 | Minimum edge amplitude |
| Transition／Transition | 边缘极性 | 邊緣極性 | Edge polarity |
| Selection／Selection | 响应选择 | 響應選擇 | Response selection |
| Interpolation／Interpolation | 插值 | 內插 | Interpolation |
| PairDiagnostics／PairDiagnostics | 边对诊断 | 邊對診斷 | Pair diagnostics |
| MatchTolerance／MatchTolerancePx、Policy.MatchTolerance | 匹配容差 | 配對容差 | Match tolerance |
| Alpha／Alpha、MinSigmaOrAlpha/MaxSigmaOrAlpha（XLD） | Canny 平滑尺度 | Canny 平滑尺度 | Canny smoothing scale |
| Low／Low | 低阈值 | 低閾值 | Low threshold |
| High／High | 高阈值 | 高閾值 | High threshold |
| Segmentation／Segmentation | 分段模式 | 分段模式 | Segmentation mode |
| MaxLineDist1／MaxLineDist1Px | 分段距离一 | 分段距離一 | Segmentation distance 1 |
| MaxLineDist2／MaxLineDist2Px | 分段距离二 | 分段距離二 | Segmentation distance 2 |
| FitPolicy／Fit.Policy | 拟合策略 | 擬合策略 | Fit policy |
| Iterations／Iterations | 迭代次数 | 迭代次數 | Iterations |
| Clipping／ClippingFactor | 鲁棒截断系数 | 強健截斷係數 | Robust clipping factor |
| Closure／MaxClosureDistance | 最大闭合距离 | 最大閉合距離 | Maximum closure distance |
| MinPoints／MinPoints | 最少不同点数 | 最少相異點數 | Minimum distinct points |
| MinSpan／MinSpan | 最小跨度 | 最小跨度 | Minimum span |
| MinRankRatio／MinRankRatio | 最小秩比 | 最小秩比 | Minimum rank ratio |
| MissingSlots／MaxMissingSlots、MissingSlotIds | 缺失卡尺 | 缺失卡尺 | Missing calipers |
| ConsecutiveMissing／MaxConsecutiveMissingSlots | 最大连续缺失数 | 最大連續缺失數 | Maximum consecutive missing count |
| Coverage／MinCoverageRad、AngularCoverageRad | 角覆盖范围 | 角涵蓋範圍 | Angular coverage |
| ArcGap／MaxGapRad、MaxAngularGapRad | 最大缺弧 | 最大缺弧 | Maximum arc gap |
| AxisRatio／MaxAxisRatio | 最大轴比 | 最大軸比 | Maximum axis ratio |
| NearCircle／NearCircleRelativeGap | 近圆相对轴差 | 近圓相對軸差 | Near-circle relative axis gap |
| MeanResidual／MeanAbsolute、MaxMeanAbsoluteResidual | 平均绝对残差 | 平均絕對殘差 | Mean absolute residual |
| MaxResidual／MaxAbsolute、MaxAbsoluteResidual | 最大绝对残差 | 最大絕對殘差 | Maximum absolute residual |
| RmsResidual／Rms、MaxRmsResidual | 均方根残差 | 均方根殘差 | RMS residual |
| StabilityDelta／StabilityDelta | 稳定性扰动量 | 穩定性擾動量 | Stability perturbation |
| CenterDelta／MaxParameterDelta.CenterOrEndpoint | 中心或端点变化上限 | 中心或端點變化上限 | Center or endpoint change limit |
| RadiusDelta／MaxParameterDelta.RadiusOrAxis | 半径或轴长变化上限 | 半徑或軸長變化上限 | Radius or axis change limit |
| AngleDelta／MaxParameterDelta.AngleRad | 角度变化上限 | 角度變化上限 | Angle change limit |
| LineDistDelta／MaxParameterDelta.LineDist | 线距变化上限 | 線距變化上限 | Line distance change limit |
| FeatureWidth／MinimumFeatureWidthPx | 最小特征宽度 | 最小特徵寬度 | Minimum feature width |
| IndexTolerance／OriginalIndexTolerancePx | 原始索引容差 | 原始索引容差 | Original index tolerance |
| CoordinateSpace／Target、Context.Space | 坐标空间 | 座標空間 | Coordinate space |
| Unit／TargetUnit、Context.Unit | 单位 | 單位 | Unit |
| AxisA／AxisA | 轴 A | 軸 A | Axis A |
| AxisB／AxisB | 轴 B | 軸 B | Axis B |
| Handedness／Handedness | 轴系手性 | 軸系手性 | Axis handedness |
| Deadline／DeadlineUtc | 执行截止时间 | 執行截止時間 | Execution deadline |
| MaxSlots／MaxSlots | 卡尺数上限 | 卡尺數上限 | Caliper count limit |
| MaxWindows／MaxWindows | 窗口数上限 | 視窗數上限 | Window count limit |
| MaxFitGroups／MaxFitGroups | 拟合组数上限 | 擬合群組數上限 | Fit group count limit |
| MaxCandidates／MaxCandidatesPerWork | 单项候选数上限 | 單項候選數上限 | Candidates per work limit |
| MaxPoints／MaxContourPoints、MaxNativePoints | 点数上限 | 點數上限 | Point count limit |
| MaxResultBytes／MaxResultBytes | 结果字节上限 | 結果位元組上限 | Result byte limit |
| MaxWorkingBytes／MaxWorkingSetBytes | 工作集字节上限 | 工作集位元組上限 | Working-set byte limit |
| MaxConcurrentSlots／MaxConcurrentSlots | 并发采样数上限 | 並行取樣數上限 | Concurrent work limit |
| QueueLimit／MaxQueuedOperations | 排队数上限 | 排隊數上限 | Queue limit |
| OperationLimit／MaxConcurrentOperations | 并发请求数上限 | 並行請求數上限 | Concurrent request limit |
| RetentionLimit／MaxRetainedOperations | 回执保留数上限 | 回執保留數上限 | Retained receipt limit |
| RetainedBytes／MaxRetainedResultBytes | 保留结果字节上限 | 保留結果位元組上限 | Retained result byte limit |
| EventQueue／EventQueueCapacity | 事件队列上限 | 事件佇列上限 | Event queue limit |
| BoundaryInset／QualifiedBoundaryInsetPx | 边界留量 | 邊界餘量 | Boundary inset |
| FixedNativeBytes／FixedNativeBytes | 原生固定字节预算 | 原生固定位元組預算 | Fixed native byte budget |
| BytesPerPixel／NativeBytesPerPixel | 每像素原生字节预算 | 每像素原生位元組預算 | Native bytes per pixel |
| BytesPerPoint／NativeBytesPerPoint | 每点原生字节预算 | 每點原生位元組預算 | Native bytes per point |
| NativeIndex／NativeIndex | 原生响应索引 | 原生響應索引 | Native response index |
| SearchPosition／SearchPositionPx | 搜索轴位置 | 搜尋軸位置 | Search-axis position |
| NativePairIndex／NativePairIndex | 原生边对索引 | 原生邊對索引 | Native pair index |
| IntraDistance／IntraDistancePx | 对内距离 | 對內距離 | Within-pair distance |
| InterDistance／InterDistancePx | 对间距离 | 對間距離 | Between-pair distance |
| FirstPairIndex／FirstPairIndex | 前一边对索引 | 前一邊對索引 | First pair index |
| SecondPairIndex／SecondPairIndex | 后一边对索引 | 後一邊對索引 | Second pair index |
| PairIndex／PairIndex | 边对索引 | 邊對索引 | Pair index |
| IsFirst／IsFirst | 是否第一条边 | 是否第一條邊 | Is first edge |
| DiagnosticEdgeIndex／DiagnosticEdgeIndex | 诊断边索引 | 診斷邊索引 | Diagnostic edge index |
| OriginalIndex／OriginalIndex、SourceIndex | 原始索引 | 原始索引 | Original index |
| LocalIndex／LocalIndex | 局部索引 | 局部索引 | Local index |
| ParentIndex／ParentIndex | 原轮廓索引 | 原輪廓索引 | Parent contour index |
| SegmentIndex／SegmentIndex | 分段索引 | 分段索引 | Segment index |
| ImagePoint／ImagePoint | 图像点 | 影像點 | Image point |
| FitPoint／FitPointValue、InputPoints | 拟合点 | 擬合點 | Fit point |
| Amplitude／SignedAmplitude | 有符号幅值 | 帶正負號幅值 | Signed amplitude |
| Response／Response | 梯度模 | 梯度大小 | Gradient magnitude |
| Angle／AngleRad | 边缘法向角 | 邊緣法向角 | Edge normal angle |
| EdgeDirection／EdgeDirectionRad | 边缘方向角 | 邊緣方向角 | Edge direction angle |
| Distance／DistancePx、Dist | 距离 | 距離 | Distance |
| First／First、FirstIndex | 第一条边 | 第一條邊 | First edge |
| Second／Second、SecondIndex | 第二条边 | 第二條邊 | Second edge |
| Center／Center | 中心 | 中心 | Center |
| Radius／Radius | 半径 | 半徑 | Radius |
| Radius1／Radius1 | 长半轴 | 長半軸 | Semi-major axis |
| Radius2／Radius2 | 短半轴 | 短半軸 | Semi-minor axis |
| NativePhi／NativePhiRad | 原生椭圆轴角 | 原生橢圓軸角 | Native ellipse axis angle |
| AxisAngle／ObservableAxisAngleRad | 可观察轴角 | 可觀察軸角 | Observable axis angle |
| StartPhi／StartPhiRad | 起始参数角 | 起始參數角 | Start parameter angle |
| EndPhi／EndPhiRad | 结束参数角 | 結束參數角 | End parameter angle |
| PointOrder／PointOrder | 点序方向 | 點序方向 | Point order |
| Begin／BeginProjection | 首点投影 | 首點投影 | First-point projection |
| End／EndProjection | 尾点投影 | 尾點投影 | Last-point projection |
| MinProjection／MinSupportProjection | 支撑最小投影 | 支撐最小投影 | Minimum support projection |
| MaxProjection／MaxSupportProjection | 支撑最大投影 | 支撐最大投影 | Maximum support projection |
| NormalA／Nr | 法向 A 分量 | 法向 A 分量 | Normal A component |
| NormalB／Nc | 法向 B 分量 | 法向 B 分量 | Normal B component |
| SignedResidual／SignedPerPoint | 逐点有符号残差 | 逐點帶正負號殘差 | Signed residual per point |
| Metric／MetricKey | 距离度量 | 距離度量 | Distance metric |
| Inliers／BackendInliers | 后端内点索引 | 後端內點索引 | Backend inlier indices |
| Excluded／DiagnosticExcluded、DiagnosticExclusionState | 诊断排除点 | 診斷排除點 | Diagnostic excluded points |
| StabilityTrial／TrialId、Stability | 稳定性检查 | 穩定性檢查 | Stability check |
| ObservedDelta／ObservedDelta | 实际参数变化 | 實際參數變化 | Observed parameter change |
| RankRatio／RankRatio | 秩比 | 秩比 | Rank ratio |
| PlannedSlots／PlannedSlots | 计划卡尺数 | 計畫卡尺數 | Planned calipers |
| ObservedSlots／UniqueObservedSlots | 唯一响应卡尺数 | 唯一響應卡尺數 | Calipers with unique responses |
| SlotCoverage／SlotCoverage | 卡尺覆盖率 | 卡尺涵蓋率 | Caliper coverage |
| BoundaryLimited／BoundaryLimited | 边界受限 | 邊界受限 | Boundary limited |
| Uncertainty／Uncertainty | 测量不确定度 | 量測不確定度 | Measurement uncertainty |
| Status／Status、Phase、Validity | 状态 | 狀態 | Status |
| Exhaustive／Exhaustive | 响应是否完整 | 響應是否完整 | Exhaustive response |
| ClosedContour／IsClosed | 轮廓是否闭合 | 輪廓是否閉合 | Closed contour |
| ContourType／ContApprox | 分段类型 | 分段類型 | Segment type |
| OriginalMapping／OriginalMapping、DiagnosticLinks | 原始对应 | 原始對應 | Original association |
| PendingReleases／PendingReleases | 待归还项数 | 待歸還項目數 | Pending returns |
| PendingOperations／PendingOperationIds | 未结束请求 | 未結束請求 | Pending requests |
| Error／Errors、Code | 错误 | 錯誤 | Error |
| Detail／DetailKey | 原因 | 原因 | Reason |
| ModuleVersion／ModuleVersion、ContractMajor/Minor | 模块与契约版本 | 模組與契約版本 | Module and contract version |
| BackendVersion／BackendVersion、RequiredBackendVersion | 后端版本 | 後端版本 | Backend version |
| RuntimeVersion／RuntimeVersion | 运行库版本 | 執行階段版本 | Runtime version |
| Simulation／IsSimulation | 模拟结果 | 模擬結果 | Simulation result |
| AcceptedUtc／AcceptedUtc | 接纳时间 | 接納時間 | Accepted at |
| TerminalUtc／TerminalUtc、Utc | 结束时间 | 結束時間 | Finished at |
| Released／ResourcesReleased | 资源是否归还 | 資源是否歸還 | Resources returned |
| ManagedPeak／PeakManagedBytes | 托管负载峰值 | 受控負載峰值 | Managed payload peak |
| NativePeak／PeakNativeBytes | 原生负载峰值 | 原生負載峰值 | Native payload peak |
| ResultBytes／LogicalResultBytes | 结果逻辑字节数 | 結果邏輯位元組數 | Logical result bytes |
| DroppedEvents／DroppedEventCount | 丢弃投影事件数 | 捨棄投影事件數 | Dropped projection events |
| Duration／Duration、Timings | 耗时 | 耗時 | Duration |
| Stage／StageKey | 阶段 | 階段 | Stage |
| Sequence／Sequence | 事件序号 | 事件序號 | Event sequence |
| Progress／Progress | 进度 | 進度 | Progress |
| SampleId／SampleId、RecommendationSample.Id | 样本编号 | 樣本編號 | Sample ID |
| AnnotationSource／AnnotationSource、TruthSource | 真值来源 | 真值來源 | Ground-truth source |
| TruthKind／TruthKind | 真值类型 | 真值類型 | Ground-truth type |
| Negative／NegativeConfirmed | 已确认负样本 | 已確認負樣本 | Confirmed negative sample |
| LineSpan／LineEvaluationSpan | 线角度评价跨度 | 線角度評估跨度 | Line angle evaluation span |
| IsValidation／IsValidation | 验证样本标记 | 驗證樣本標記 | Validation sample flag |
| Requested／Requested | 真值数 | 真值數 | Ground-truth count |
| Matched／Matched | 唯一匹配数 | 唯一配對數 | Unique match count |
| Missed／Missed | 缺失数 | 缺失數 | Miss count |
| Extra／Extra | 额外候选数 | 額外候選數 | Extra candidate count |
| Ambiguous／Ambiguous | 歧义组数 | 歧義群組數 | Ambiguous group count |
| MeanError／MeanError | 平均匹配误差 | 平均配對誤差 | Mean match error |
| Loss／Loss | 评价损失 | 評估損失 | Evaluation loss |
| CalibrationLoss／CalibrationLoss | 校准损失 | 校準損失 | Calibration loss |
| ValidationLoss／ValidationLoss | 验证损失 | 驗證損失 | Validation loss |
| Eligible／Eligible | 是否通过建议门 | 是否通過建議門檻 | Recommendation eligibility |
| MissWeight／MissWeight | 缺失权重 | 缺失權重 | Miss weight |
| ExtraWeight／ExtraWeight | 额外候选权重 | 額外候選權重 | Extra candidate weight |
| ErrorWeight／ErrorWeight | 误差权重 | 誤差權重 | Error weight |
| MissRate／MaxMissRate | 缺失率上限 | 缺失率上限 | Miss rate limit |
| ExtraRate／MaxExtraRate | 额外候选率上限 | 額外候選率上限 | Extra rate limit |
| MaxMeanError／MaxMeanError | 平均误差上限 | 平均誤差上限 | Mean error limit |
| MaxEvaluations／MaxEvaluations | 子执行次数上限 | 子執行次數上限 | Child execution limit |
| RecommendationId／RecommendationRequest.Id | 建议编号 | 建議編號 | Recommendation ID |
| ParameterDiff／候选与基础参数差异 | 参数差异 | 參數差異 | Parameter differences |
| Reason／拒绝或失效原因投影 | 拒绝原因 | 拒絕原因 | Rejection reason |
| BaseValue／差异原值 | 原值 | 原值 | Original value |
| CandidateValue／差异候选值 | 候选值 | 候選值 | Candidate value |

采用/恢复/取消等命令不展示不可编辑的服务EventScheduler或TimeProvider对象，资格Rule和ServiceOptions只在高级诊断用上述字段投影；不存在“其它DTO字段由编码者临时命名”的扩展口。未来增加用户可见字段须先补本表和三语映射。实际ParameterDelta的子项可复用CenterDelta/RadiusDelta/AngleDelta/LineDistDelta，但实际值列用ObservedDelta标题，不能把实测delta标成上限。

### 8.4.3 枚举、证据、阶段与建议状态

key=`Value.<leaf>`；绑定列中的每个enum/string值必须精确映射，不按字符串前缀或大小写猜。bool复用Yes/No；null数值按ScalarEvidence状态显示，普通缺失引用用NotProvided，绝不显示0。所有未定义enum在Validate拒绝，UI显示Invalid+001而不是传播整数为正常值。

| leaf／绑定值 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Yes／true | 是 | 是 | Yes |
| No／false | 否 | 否 | No |
| MeasurePos／Route.MeasurePos | 有向测边 | 有向測邊 | Directed edge measurement |
| MeasurePairs／Route.MeasurePairs | 有向边对 | 有向邊對 | Directed edge pairs |
| Xld／Route.Xld | 灰度轮廓 | 灰階輪廓 | Grayscale contours |
| ColorXld／Route.ColorXld | 彩色轮廓 | 彩色輪廓 | Color contours |
| None／Primitive.None、Segmentation.None | 无 | 無 | None |
| Line／Primitive.Line、ContApprox=-1 | 线 | 線 | Line |
| Circle／Primitive.Circle、ContApprox=1 | 圆或圆弧 | 圓或圓弧 | Circle or circular arc |
| Ellipse／Primitive.Ellipse、ContApprox=0 | 椭圆或椭圆弧 | 橢圓或橢圓弧 | Ellipse or elliptic arc |
| Mono8／PixelLayout.Mono8 | 单通道 8 位 | 單通道 8 位 | Single-channel 8-bit |
| Mono16／PixelLayout.Mono16 | 单通道 16 位 | 單通道 16 位 | Single-channel 16-bit |
| MonoFloat32／PixelLayout.MonoFloat32 | 单通道 32 位浮点 | 單通道 32 位浮點 | Single-channel 32-bit float |
| Rgb8Planar／PixelLayout.Rgb8Planar | RGB 分平面 8 位 | RGB 分平面 8 位 | Planar RGB 8-bit |
| Rgb16Planar／PixelLayout.Rgb16Planar | RGB 分平面 16 位 | RGB 分平面 16 位 | Planar RGB 16-bit |
| Image／CoordinateSpace.Image | 图像空间 | 影像空間 | Image space |
| Target／CoordinateSpace.Target | 目标空间 | 目標空間 | Target space |
| Right／AxisHandedness.Right | 右手系 | 右手座標系 | Right-handed |
| Left／AxisHandedness.Left | 左手系 | 左手座標系 | Left-handed |
| ImageRaster／AxisHandedness.ImageRaster | 图像行列轴系 | 影像列行軸系 | Image row-column axes |
| Nearest／Interpolation.Nearest | 最近邻 | 最近鄰 | Nearest neighbor |
| Bilinear／Interpolation.Bilinear | 双线性 | 雙線性 | Bilinear |
| Bicubic／Interpolation.Bicubic | 双三次 | 雙三次 | Bicubic |
| Positive／Transition.Positive | 暗到亮 | 暗至亮 | Dark to bright |
| Negative／Transition.Negative | 亮到暗 | 亮至暗 | Bright to dark |
| All／Transition.All、Selection.All | 全部 | 全部 | All |
| PositiveStrongest／Transition.PositiveStrongest | 最强暗到亮边对 | 最強暗至亮邊對 | Strongest dark-to-bright pair |
| NegativeStrongest／Transition.NegativeStrongest | 最强亮到暗边对 | 最強亮至暗邊對 | Strongest bright-to-dark pair |
| AllStrongest／Transition.AllStrongest | 全部极性最强边对 | 全部極性最強邊對 | Strongest pair for either polarity |
| First／Selection.First、FitObservation.PairFirst | 第一条 | 第一條 | First |
| Last／Selection.Last | 最后一条 | 最後一條 | Last |
| PairSecond／FitObservation.PairSecond | 边对第二条边 | 邊對第二條邊 | Second edge of pair |
| PairCenter／FitObservation.PairCenter | 边对中心（派生点） | 邊對中心（衍生點） | Pair center (derived point) |
| Edge／FitObservation.Edge、TruthKind.Edge | 单边 | 單邊 | Edge |
| Pair／TruthKind.Pair | 边对 | 邊對 | Edge pair |
| Primitive／TruthKind.Primitive | 几何候选 | 幾何候選 | Geometry candidate |
| Lines／Segmentation.Lines | 线分段 | 線分段 | Line segments |
| LinesCircles／Segmentation.LinesCircles | 线与圆弧分段 | 線與圓弧分段 | Line and circular-arc segments |
| LinesEllipses／Segmentation.LinesEllipses | 线与椭圆弧分段 | 線與橢圓弧分段 | Line and elliptic-arc segments |
| Standard／FitPolicy.Standard | 标准拟合 | 標準擬合 | Standard fit |
| RobustTukey／FitPolicy.RobustTukey | Tukey 鲁棒拟合 | Tukey 強健擬合 | Robust Tukey fit |
| Provided／EvidenceState.Provided | 已提供 | 已提供 | Provided |
| NotProvided／EvidenceState.NotProvided | 未提供 | 未提供 | Not provided |
| Applicable／参数使用状态 | 适用 | 適用 | Applicable |
| NotApplicable／EvidenceState.NotApplicable | 不适用 | 不適用 | Not applicable |
| Unknown／EvidenceState.Unknown、MappingState.Unknown、DrainStatus.DrainUnknown | 尚未确认 | 尚未確認 | Unconfirmed |
| Exact／MappingState.Exact | 唯一对应 | 唯一對應 | Exact association |
| NotStarted／未执行work或phase | 未开始 | 尚未開始 | Not started |
| Validating／校验phase | 校验中 | 驗證中 | Validating |
| Queued／排队phase | 排队中 | 排隊中 | Queued |
| Running／运行phase | 运行中 | 執行中 | Running |
| Draining／OperationPhase/RecommendationPhase.Draining | 正在排空 | 正在排空 | Draining |
| Completed／完成状态 | 已完成 | 已完成 | Completed |
| Rejected／拒绝状态 | 已拒绝 | 已拒絕 | Rejected |
| Cancelled／已结束取消 | 已取消 | 已取消 | Cancelled |
| TimedOut／已结束超时 | 已超时 | 已逾時 | Timed out |
| Faulted／故障状态 | 失败 | 失敗 | Failed |
| Empty／WorkStatus.Empty、ExecutionStatus.NoCandidate | 无候选 | 無候選 | No candidate |
| Ambiguous／歧义状态 | 存在歧义 | 存在歧義 | Ambiguous |
| Truncated／截断状态 | 结果已截断 | 結果已截斷 | Results truncated |
| ValidCandidate／CandidateValidity.ValidCandidate | 有效几何候选 | 有效幾何候選 | Valid geometry candidate |
| InsufficientSupport／CandidateValidity.InsufficientSupport | 支撑不足 | 支撐不足 | Insufficient support |
| InvalidGeometry／CandidateValidity.InvalidGeometry | 几何无效 | 幾何無效 | Invalid geometry |
| NotAvailable／CandidateValidity.NotAvailable | 未提供模型 | 未提供模型 | Model unavailable |
| Unstable／稳定性诊断原因，非新增CandidateValidity | 稳定性未通过 | 穩定性未通過 | Stability check failed |
| Drained／DrainStatus.Drained | 已排空 | 已排空 | Drained |
| Terminal／phase.Terminal | 已结束 | 已結束 | Finished |
| Recommended／RecommendationStatus.Recommended | 有可用建议 | 有可用建議 | Recommendation available |
| Abstained／RecommendationStatus.Abstained | 无可用建议 | 無可用建議 | No recommendation available |
| Eligible／CandidateEvaluation.Eligible=true | 通过建议门 | 通過建議門檻 | Recommendation gates passed |
| Ineligible／CandidateEvaluation.Eligible=false | 未通过建议门 | 未通過建議門檻 | Recommendation gates failed |
| Unmeasured／性能未测 | 未测量 | 未量測 | Unmeasured |
| NotEvaluated／未评估或MeanError/Loss不适用 | 未评估 | 未評估 | Not evaluated |
| ReadOnly／只读权限投影 | 只读 | 唯讀 | Read only |
| Draft／本地草稿 | 草稿 | 草稿 | Draft |
| Ignored／固定路线忽略参数 | 本方法不使用 | 此方法不使用 | Not used by this method |
| PreviousInput／旧输入证据 | 旧输入结果 | 舊輸入結果 | Result from previous input |
| Released／真实归还 | 资源已归还 | 資源已歸還 | Resources returned |
| FailedReleased／故障后真实归还 | 运算失败；资源已归还 | 運算失敗；資源已歸還 | Execution failed; resources returned |
| PositiveOrder／PointOrder="positive" | 正向点序 | 正向點序 | Positive point order |
| NegativeOrder／PointOrder="negative" | 反向点序 | 反向點序 | Negative point order |
| RequestReceived／EventKind.RequestReceived | 已收到请求 | 已收到請求 | Request received |
| ValidationCompleted／EventKind.ValidationCompleted | 校验已完成 | 驗證已完成 | Validation completed |
| RequestRejected／EventKind.RequestRejected | 请求已拒绝 | 請求已拒絕 | Request rejected |
| RequestAccepted／EventKind.RequestAccepted | 请求已接纳 | 請求已接納 | Request accepted |
| ExecutionStarted／EventKind.ExecutionStarted | 运算已开始 | 運算已開始 | Execution started |
| WorkCompleted／EventKind.WorkCompleted | 采样项已完成 | 取樣項目已完成 | Work item completed |
| Progress／EventKind.Progress | 正在处理 | 正在處理 | Processing |
| CancellationRequested／EventKind.CancellationRequested | 已请求取消 | 已要求取消 | Cancellation requested |
| TimeoutReached／EventKind.TimeoutReached | 已达到期限 | 已達到期限 | Deadline reached |
| DrainStarted／EventKind.DrainStarted | 已开始排空 | 已開始排空 | Draining started |
| DrainCompleted／EventKind.DrainCompleted | 排空已完成 | 排空已完成 | Draining completed |
| ResourcesReleased／EventKind.ResourcesReleased | 资源已归还 | 資源已歸還 | Resources returned |
| Invalid／未知或非法值投影 | 无效 | 無效 | Invalid |
| StageValidate／Validate | 输入校验 | 輸入驗證 | Input validation |
| StageSupport／DescribeSupport及包含检查 | 支撑检查 | 支撐檢查 | Support check |
| StageAcquire／额度/frame/coordinate/job获取 | 获取资源 | 取得資源 | Resource acquisition |
| StageExtract／提取及属性复制 | 提取原始观察 | 擷取原始觀察 | Raw observation extraction |
| StageSegment／分段与原索引 | 轮廓分段与对应 | 輪廓分段與對應 | Contour segmentation and association |
| StageMap／逐点Map | 支撑点映射 | 支撐點映射 | Support point mapping |
| StageQualify／资格检查 | 资格检查 | 資格檢查 | Qualification check |
| StageFit／主Fit | 几何拟合 | 幾何擬合 | Geometry fit |
| StageStability／四挑战 | 稳定性检查 | 穩定性檢查 | Stability check |
| StageSeal／结果复制封口 | 结果封存 | 結果封存 | Result sealing |
| StageReturn／native退出及lease释放 | 退出与资源归还 | 結束與資源歸還 | Exit and resource return |
| StageOther／未知stage诊断 | 其它诊断阶段 | 其他診斷階段 | Other diagnostic stage |

EventKind与OperationPhase按上表精确投影，不向操作者显示Task/事件成员名；需要技术排查时原token另列在Diagnostics并保上下文。MetricKey仅支持本指导固定线/圆正交绝对距离与椭圆正交距离路线；显示Title.Residual+对应Value.Line/Circle/Ellipse，不将未知MetricKey翻译为“精确距离”。阶段测点按产生该StageTiming的固定流程绑定StageValidate～StageReturn，不猜StageKey字符串；外部未知stage用StageOther，技术token单独可复制。

### 8.4.4 提示、校验与建议解释

key=`Tip/Validation/Recommendation.<leaf>`；SuperTip标题取对应Field/Command/Title，正文取本表，恢复操作必须是当前权限下可执行命令。占位符只有下表命名字段，替换值是本地化显示值；不把原HTML/异常当格式串。范围依据§3和当前Profile显示，不由翻译层改值/单位。涉及手性、HALCON角度和资格的精确算法继续以原章节为准。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Tip.Run | 先校验草稿。执行使用本次输入快照，不更新生产参数。 | 先驗證草稿。執行使用本次輸入快照，不更新生產參數。 | Validate the draft first. This run uses an input snapshot and does not update production parameters. |
| Tip.Cancel | 只取消本次请求。运算退出并归还资源前仍显示排空状态。 | 只取消本次請求。運算結束並歸還資源前仍顯示排空狀態。 | Cancel this request only. Draining continues until execution ends and resources are returned. |
| Tip.Evidence | 查看原点、来源、支撑和错误。显示层不会改变结果。 | 檢視原始點、來源、支撐與錯誤。顯示圖層不會變更結果。 | Review original points, sources, support and errors. Display layers do not change results. |
| Tip.Sigma | 卡尺平滑尺度，单位 px；允许范围 {min}～{max}，且不超过每条搜索半长的一半。 | 卡尺平滑尺度，單位 px；允許範圍 {min}～{max}，且不超過每條搜尋半長的一半。 | Caliper smoothing scale in px. Allowed range: {min} to {max}, also at most half each search half-length. |
| Tip.Threshold | 按原图强度设置幅值阈值，范围 {min}～{max}。显示亮度不改变分析值。 | 依原圖強度設定幅值閾值，範圍 {min}～{max}。顯示亮度不會變更分析值。 | Set the amplitude threshold in source intensity units, from {min} to {max}. Display brightness does not change analysis values. |
| Tip.Direction | 极性沿箭头搜索方向定义。反转箭头会改变暗到亮与亮到暗的含义。 | 極性依箭頭搜尋方向定義。反轉箭頭會改變暗至亮與亮至暗的含義。 | Polarity follows the search arrow. Reversing it changes dark-to-bright and bright-to-dark polarity. |
| Tip.Origin | 请求中心按已批准规则取到整数采样中心；两者均保留。 | 請求中心依已批准規則取整為取樣中心；兩者均保留。 | The sampling center is rounded by the approved rule. Both requested and effective centers are retained. |
| Tip.Interpolation | 改插值须重算完整采样支撑。不能跨无效区域取样。 | 變更內插須重算完整取樣支撐。不能跨無效區域取樣。 | Changing interpolation requires recalculating full sampling support. Invalid regions cannot supply samples. |
| Tip.Pairs | 第一条和第二条边按有向响应保留，中心是两边平均得到的派生点。 | 第一條與第二條邊依有向響應保留，中心是兩邊平均得到的衍生點。 | First and second edges retain their directed order. Their midpoint is a derived point. |
| Tip.Canny | Canny 平滑尺度须大于 0；低阈值须大于 0 且不大于高阈值。 | Canny 平滑尺度須大於 0；低閾值須大於 0 且不大於高閾值。 | Canny smoothing must be positive. The low threshold must be positive and no greater than the high threshold. |
| Tip.Window | 计算窗口必须全有效；资格内区用于检查边界影响，不裁掉原轮廓点。 | 計算視窗必須完全有效；資格內區用於檢查邊界影響，不裁掉原輪廓點。 | The compute window must be fully valid. The qualified inner region checks boundary effects without trimming original points. |
| Tip.Segmentation | 每条原轮廓独立分段，不合并不同轮廓；分段保留原始对应状态。 | 每條原輪廓獨立分段，不合併不同輪廓；分段保留原始對應狀態。 | Segment each original contour separately. Keep the original association status for each segment. |
| Tip.Fit | 使用明确支撑和固定方法；残差小不代表尺寸合格或不确定度已评估。 | 使用明確支撐與固定方法；殘差小不代表尺寸合格或不確定度已評估。 | Use explicit support and a fixed method. Small residuals do not establish dimensional acceptance or evaluated uncertainty. |
| Tip.Iterations | 本方法对该参数的使用状态：{state}。迭代次数不保证按时结束。 | 此方法對該參數的使用狀態：{state}。迭代次數不保證按時結束。 | Parameter usage for this method: {state}. Iteration count does not guarantee completion time. |
| Tip.Robust | 鲁棒拟合不删除原始点；未提供内点索引时显示未提供。 | 強健擬合不刪除原始點；未提供內點索引時顯示未提供。 | Robust fitting retains original points. Missing inlier indices are shown as not provided. |
| Tip.Target | 先将全部支撑点映射到声明坐标，再拟合。原始边距仍为图像 px。 | 先將全部支撐點映射至宣告座標，再擬合。原始邊距仍為影像 px。 | Map all support points to the declared coordinates before fitting. Original edge distances remain in image px. |
| Tip.Qualification | 使用来源 {source} 的已冻结资格值。没有资格时只能查看原始观察。 | 使用來源 {source} 的已凍結資格值。沒有資格時只能檢視原始觀察。 | Use frozen qualification values from {source}. Without qualification, only raw observations are available. |
| Tip.Limit | 超过 {limit} 时停止完整项输出并标记截断，不抽稀点集。 | 超過 {limit} 時停止完整項目輸出並標示截斷，不減少點集取樣。 | At {limit}, stop at a complete item and mark truncation. Do not subsample points. |
| Tip.Resource | 负载字节不是整个进程内存；原生峰值未完整观测时显示未提供。 | 負載位元組不是整個程序記憶體；原生峰值未完整觀測時顯示未提供。 | Payload bytes are not total process memory. Native peak is not provided when observation is incomplete. |
| Tip.Native | 超时和取消只停止派发；正在运行的原生调用仍由原请求持有，实际退出后归还资源。 | 逾時與取消只停止派發；執行中的原生呼叫仍由原請求持有，實際結束後歸還資源。 | Timeout and cancellation stop further dispatch. The original request retains a running native call until it exits and resources are returned. |
| Tip.Recommend | 只比较已提供的有限参数候选。校准选取、验证检查；缺独立真值时不提供建议。 | 只比較已提供的有限參數候選。校準選取、驗證檢查；缺少獨立真值時不提供建議。 | Compare only the supplied finite candidates. Calibration selects; validation checks. Independent ground truth is required. |
| Tip.Adopt | 只采用为新草稿；来源或权限变化后不可采用，生产激活由宿主处理。 | 只採用為新草稿；來源或權限變更後不可採用，生產啟用由宿主處理。 | Adopt only as a new draft. Source or permission changes invalidate adoption. The host controls production activation. |
| Tip.Restore | 恢复本地编辑值，不重新提交旧请求，不改变正在运行的快照。 | 還原本機編輯值，不重新提交舊請求，不變更執行中的快照。 | Restore local edits without resubmitting an old request or changing a running snapshot. |
| Tip.Recovery | 等待或重试只作用于本控件请求。尚未确认归还时保留恢复入口。 | 等待或重試只作用於本控制項請求。尚未確認歸還時保留復原入口。 | Wait or retry only this control's requests. Keep recovery available until return is confirmed. |
| Tip.Parameter | {field}；单位：{unit}；允许值：{range}；来源：{source}；使用状态：{usage}。 | {field}；單位：{unit}；允許值：{range}；來源：{source}；使用狀態：{usage}。 | {field}; unit: {unit}; allowed values: {range}; source: {source}; usage: {usage}. |
| Tip.Source | 绑定指定来源与修订，不自动切换到最新数据。摘要可复制完整值。 | 繫結指定來源與修訂，不自動切換至最新資料。摘要可複製完整值。 | Bind the specified source and revision without switching to latest data. The full digest can be copied. |
| Tip.ReadOnly | 此值是运行快照或结果，只供查看；编辑草稿不会改写它。 | 此值是執行快照或結果，僅供檢視；編輯草稿不會改寫它。 | This value belongs to a run snapshot or result and is read only. Draft edits do not overwrite it. |
| Tip.DrainStatus | 只在原任务已退出且借用真实归还后显示已排空；取消等待不结束清理。 | 只在原任務已結束且借用確實歸還後顯示已排空；取消等待不結束清理。 | Drained requires original tasks to exit and borrows to be returned. Cancelling a wait does not end cleanup. |
| Validation.NoBound | 来源未给上限 | 來源未提供上限 | No source-defined upper bound |
| Validation.Unspecified | 未声明 | 未宣告 | Not declared |
| Validation.Required | {field}未提供，请补齐输入。 | 未提供{field}，請補齊輸入。 | {field} is required. Complete the input. |
| Validation.Finite | {field}必须为有限数值。 | {field}必須為有限數值。 | {field} must be finite. |
| Validation.Range | {field}须在 {min}～{max} 范围内。 | {field}須在 {min}～{max} 範圍內。 | {field} must be between {min} and {max}. |
| Validation.Positive | {field}须大于 0。 | {field}須大於 0。 | {field} must be greater than zero. |
| Validation.NonNegative | {field}不得小于 0。 | {field}不得小於 0。 | {field} must not be negative. |
| Validation.UniqueId | 编号重复，请检查采样项、候选和样本。 | 編號重複，請檢查取樣項目、候選與樣本。 | Duplicate ID; check work items, candidates and samples. |
| Validation.Layout | 通道、位深或字节布局不匹配，请检查图像来源。 | 通道、位元深度或位元組配置不符，請檢查影像來源。 | Channels, bit depth or byte layout differ. Check the image source. |
| Validation.Direction | 搜索方向须为单位向量，请检查两个分量。 | 搜尋方向須為單位向量，請檢查兩個分量。 | Search direction must be a unit vector. Check both components. |
| Validation.Rectangle | 矩形须在原图内；资格内区须在计算矩形内。 | 矩形須在原圖內；資格內區須在計算矩形內。 | The rectangle must lie inside the source image. The qualified inner region must lie inside the compute rectangle. |
| Validation.Support | 有效区域未覆盖全部采样支撑，请调整计划。 | 有效區域未涵蓋全部取樣支撐，請調整計畫。 | The valid region does not cover all sampling support. Revise the plan. |
| Validation.Route | 参数组合不适用于所选路线，请检查标记项。 | 參數組合不適用於所選方式，請檢查標記項目。 | This parameter combination does not apply to the selected route. Check marked fields. |
| Validation.Canny | 阈值须满足 0 < 低阈值 ≤ 高阈值。 | 閾值須滿足 0 < 低閾值 ≤ 高閾值。 | Thresholds must satisfy 0 < low ≤ high. |
| Validation.Segmentation | 分段模式或距离不匹配，请检查几何类型及距离一、二。 | 分段模式或距離不符，請檢查幾何類型與距離一、二。 | Segmentation mode or distances differ. Check the geometry type and distances 1 and 2. |
| Validation.Version | 来源版本不匹配，请重新加载指定修订。 | 來源版本不符，請重新載入指定修訂。 | Source versions differ. Reload the specified revisions. |
| Validation.Deadline | 截止时间已到，原请求不延长期限；排空后再发新请求。 | 截止時間已到，原請求不延長期限；排空後再發新請求。 | The deadline has passed. The original deadline is not extended. Drain before submitting a new request. |
| Validation.Budget | {field}不足，需 {required}，可用 {available}。 | {field}不足，需 {required}，可用 {available}。 | Insufficient {field}: required {required}, available {available}. |
| Validation.Truth | 校准和验证各需独立正样本；缺失标注不作负样本。 | 校準與驗證各需獨立正樣本；缺少標註不視為負樣本。 | Calibration and validation each require independent positive samples. Missing annotations are not negative samples. |
| Validation.Candidate | 候选只可修改批准的平滑尺度、阈值和分段距离。 | 候選只可變更批准的平滑尺度、閾值與分段距離。 | Candidates may change only approved smoothing scales, thresholds and segmentation distances. |
| Validation.ResourceText | 本控件语言资源不完整，已保留原语言。 | 此控制項語言資源不完整，已保留原語言。 | This control's language resources are incomplete. The previous language is retained. |
| Validation.Binding | 控件仍有未结束请求，请查看排空状态后再绑定。 | 控制項仍有未結束請求，請檢視排空狀態後再繫結。 | The control still has pending requests. Check drain status before binding again. |
| Recommendation.Explanation | 校准损失 {calibration}；验证损失 {validation}；按校准损失及候选编号选取。 | 校準損失 {calibration}；驗證損失 {validation}；依校準損失及候選編號選取。 | Calibration loss: {calibration}; validation loss: {validation}. Selection uses calibration loss, then candidate ID. |
| Recommendation.Passed | 验证门通过。请查看缺失、额外候选和误差后决定是否采用。 | 驗證門檻通過。請檢視缺失、額外候選與誤差後決定是否採用。 | Validation gates passed. Review misses, extra candidates and errors before adopting. |
| Recommendation.ZeroMatch | 正样本无唯一匹配，此候选不可采用；误差和损失未评估。 | 正樣本無唯一配對，此候選不可採用；誤差與損失未評估。 | No unique match in a positive sample. This candidate cannot be adopted; error and loss are not evaluated. |
| Recommendation.Negative | 已确认负样本；误差不适用，额外候选仍计入评价。 | 已確認負樣本；誤差不適用，額外候選仍計入評估。 | Confirmed negative sample. Error is not applicable; extra candidates still count. |
| Recommendation.NoTruth | 缺少独立真值或验证样本，未生成建议。 | 缺少獨立真值或驗證樣本，未產生建議。 | No recommendation generated: independent ground truth or validation samples are missing. |
| Recommendation.GateFailed | 此候选未通过 {gate}，不能采用。 | 此候選未通過 {gate}，不能採用。 | This candidate failed {gate} and cannot be adopted. |
| Recommendation.Stale | 输入或参数已变更，请重新生成建议。 | 輸入或參數已變更，請重新產生建議。 | Input or parameters changed. Generate a new recommendation. |
| Recommendation.Adopted | 已生成新草稿，请校验后执行。 | 已產生新草稿，請驗證後執行。 | New draft created. Validate before running. |
| Recommendation.NoPermission | 当前无采用权限，建议保留为只读。 | 目前無採用權限，建議保留為唯讀。 | Adoption is not permitted. The recommendation remains read only. |

所有纯Validate错误按最具体规则选上表Validation key，汇总仍为001；端口/runtime错误用§8.4的001～019，原DetailKey只用于定位和诊断，不能要求用户识别它。F2D.Limit.*各上限绑定§8.4.2字段名称+009/Validation.Budget，资源单位统一显示B或明确IEC换算KiB/MiB，保原byte值可复制。Gate占位符只取Field.MissRate/ExtraRate/MaxMeanError/MaxWorkingBytes/MaxResultBytes或Validation key的本地化名称；不能打印未知英语gate token。频繁同因错误在状态区合并投影，不丢原结果/错误账。

F2D-009在接纳前拒绝时没有截断输出，正文使用Validation.Budget及真实required/available字段，不误用“查看截断项”；只有实际work.Truncated才显示§8.4的009及对应完整停止位置。012可新请求重试须先真实排空；尚未归还时只给Recovery.Pending/Query/Wait/RetryRelease，不能按通用“重试”自动再Execute。原错误码、WorkId及归还状态始终保留。

每个可编辑参数必有Tip.Parameter通用完整提示；range取§3/A.1当前有效域、已冻结资格域及计划限制的交集，字符串按同一文化显示，不由UI新建限制。无正式上界显示Validation.NoBound而非编造max；unit无量纲用“1”，不适用用Value.NotApplicable；source取已绑定AssetRef原值，未声明用Validation.Unspecified；usage取Value.Applicable/NotApplicable/Ignored的当前状态。Caliper/Xld/Fit/Profile/Qualification字段另加上表对应专用Tip；预算/并发/保留字段加Tip.Limit+Resource，身份/版本加Tip.Source，所有运行和结果字段加Tip.ReadOnly，排空/资源归还字段加Tip.DrainStatus，建议评价字段加Tip.Recommend。本规则给每个显示字段确定提示，无需程序员补写。许可/草稿/候选均不能改变允许域。

### 8.4.5 恢复、权限、关闭与文字验收

恢复只改变等待/草稿/显示，不改原请求事实；Command.RetryRelease在原释放Task退出且失败后才可启动同对象重试，pending只能Command.Wait/Query。共享service/viewport不授总关闭权。下表key=`Recovery/Permission.<leaf>`，用于状态区、恢复Button SuperTip和只在确有选择时的提示框；不增加权限确认流程或默认“强制退出”命令。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Recovery.Pending | 尚未确认结束，请继续等待或查看排空状态。 | 尚未確認結束，請繼續等待或檢視排空狀態。 | Completion is unconfirmed. Keep waiting or check drain status. |
| Recovery.ReleaseFailed | 释放失败，请重试释放；原请求和资源仍由关闭管理器持有。 | 釋放失敗，請重試釋放；原請求與資源仍由關閉管理器持有。 | Release failed. Retry release; the close manager still retains the original request and resources. |
| Recovery.ClosePending | 窗口尚未关闭，资源仍在使用。请保留此窗口并查看排空状态。 | 視窗尚未關閉，資源仍在使用。請保留此視窗並檢視排空狀態。 | The window is still open because resources remain in use. Keep it open and check drain status. |
| Recovery.Transferred | 关闭责任已转交宿主管理器；资源归还仍未确认。 | 關閉責任已移交宿主管理器；資源歸還仍未確認。 | Close responsibility was transferred to the host manager. Resource return is still unconfirmed. |
| Recovery.CancelledReleased | 已取消；资源已归还。 | 已取消；資源已歸還。 | Cancelled; resources returned. |
| Recovery.TimedOutReleased | 已超时；资源已归还。 | 已逾時；資源已歸還。 | Timed out; resources returned. |
| Recovery.FailedReleased | 运算失败；资源已归还。请保留诊断后检查输入。 | 運算失敗；資源已歸還。請保留診斷後檢查輸入。 | Execution failed; resources returned. Retain diagnostics and check the input. |
| Recovery.Reload | 排空后重新加载指定图像、参数及坐标来源，再发新请求。 | 排空後重新載入指定影像、參數與座標來源，再發新請求。 | After draining, reload the specified image, parameters and coordinate sources, then submit a new request. |
| Recovery.PreviousInput | 结果属于旧输入，仅供查看；不能采用到当前草稿。 | 結果屬於舊輸入，僅供檢視；不能採用至目前草稿。 | This result belongs to previous input. It is for viewing only and cannot be adopted into the current draft. |
| Recovery.WaitCancelled | 已停止本次等待；原运算和资源归还仍继续。 | 已停止本次等待；原運算與資源歸還仍繼續。 | This wait was cancelled. Original execution and resource return continue. |
| Recovery.OverlayFailed | 图层未更新，请查看显示诊断；计算结果仍保留。 | 圖層未更新，請檢視顯示診斷；計算結果仍保留。 | Layers were not updated. Check display diagnostics; calculation results are retained. |
| Recovery.LayoutReset | 布局无法恢复，已使用默认布局；草稿仍保留。 | 版面無法還原，已使用預設版面；草稿仍保留。 | The layout could not be restored. The default layout is used; the draft is retained. |
| Recovery.SaveFailed | 宿主保存失败，计算结果未改变。请查看宿主保存状态。 | 宿主儲存失敗，計算結果未變更。請檢視宿主儲存狀態。 | Host save failed. Calculation results are unchanged. Check the host save status. |
| Recovery.Theme | 主题不可用，已使用宿主默认主题。 | 主題無法使用，已使用宿主預設主題。 | Theme unavailable. The host's default theme is used. |
| Recovery.Resources | 本控件语言切换失败，已保留原文字；请联系维护人员。 | 此控制項語言切換失敗，已保留原文字；請聯絡維護人員。 | This control's language change failed. Previous text is retained; contact maintenance. |
| Permission.Edit | 当前无编辑权限，草稿只读。 | 目前無編輯權限，草稿唯讀。 | Editing is not permitted. The draft is read only. |
| Permission.Run | 当前无执行权限，不能发新请求；已开始请求可取消。 | 目前無執行權限，不能發新請求；已開始的請求可取消。 | Running is not permitted. No new request can start; an existing request can still be cancelled. |
| Permission.Recommend | 当前无建议权限，不能开始参数建议。 | 目前無建議權限，不能開始參數建議。 | Parameter recommendation is not permitted. |
| Permission.Evidence | 当前无证据查看权限，已隐藏证据；资源清理仍继续。 | 目前無證據檢視權限，已隱藏證據；資源清理仍繼續。 | Evidence viewing is not permitted. Evidence is hidden; resource cleanup continues. |
| Permission.Changed | 权限已变更，请检查可用命令。 | 權限已變更，請檢查可用命令。 | Permissions changed. Check available commands. |

文字自审的可判定断言：本节标题/参数/DTO投影、全部公开enum映射、19个错误及终态恢复、所有按钮/空态/提示均有三语；每行无空格占位条目，各语言占位符集合相等；状态必须以真实Receipt.ResourcesReleased和原Task为准，不因翻译把Draining变已归还。动态切换zh-CN→zh-TW→en-US不改Draft/请求摘要/OperationId/期限/权限，不触发图像读取或新Execute；两个STA可保持不同语言，缺键保旧完整快照。语言长度验证复用原1920×1080基线与T18/T20～22，不造新工程或测试矩阵。上述文档检查不能冒充真实WPF布局、UIA或三语运行通过。

### 8.5 W1：公开装配、源切换与根Owner

公开构造仍为A.5的无参`new Features2DEditor()`；宿主先按§7.1创建service及本binding专用recommender，再按§7.2绑定公共ViewportControl/桥，最后`editor.Attach(new EditorBinding(attachmentId, epoch, service, recommender, bridge, draft, permissions, culture, themeName))`。服务可与其它消费者共享，recommender的单在途账只分配给本binding，不能把别人的建议任务混入Detach。Culture/Theme由宿主传，`SetCulture`与viewport binding的`SetResourcesAsync(ViewportUiResources, timeout, ct)`使用同一次宿主语言快照；失败保留各自真实回执/可恢复状态，不静默称全部切换成功。

控件内部Presenter只投影A.5托管值、保存订阅和本次输入快照，不持有SDK或决定质量。Run/Recommend在调用前登记OperationId/RecommendationId与输入、原Task和取消Owner；progress/ResultAvailable/RecommendationAvailable是可缺投影，事实查询回A.3/A.4。事件处理在Dispatcher且不阻Owner清理；投影容量使用本请求上限及viewport Limits，超限提示显示未覆盖范围，不能截掉原结果后称完整证据。桥.Show/Clear是同步投影入口，真正Apply/呈现清理由桥的原root任务与宿主强持；Clear只撤本桥图层，不清其它消费者图层或原帧源。

当前binding的结果接收键为AttachmentId/Epoch+OperationId+Frame.Asset(完整引用)/Generation+Profile.Asset(完整引用)+localUiRevision，建议另核RecommendationId/base Profile hash。运行中替换同源Draft只更新草稿/增加localUiRevision，原运行保留原快照，结果可保留为旧输入证据而不能覆盖当前树/属性/叠加；再次运行必须新ID。来自桥的选择事件还核源与当前层绑定，不把旧候选选择应用到新输入。权限撤销CanViewEvidence立即停止新Show、撤本叠加/选中证据并拒迟到可见回调，仍保留原Task/lease；Run/Recommend撤销禁新请求，取消/恢复入口继续可用。DraftChanged和ResultAvailable不提交Profile、质量或持久化事实。

A.5的EditorOverlay/EditorSelection不携带operation或epoch字段，保持公开形状不变：Editor在调用Show前核完整接收键；每次Attach宿主创建专用桥实例，并在桥私有的有界层binding内冻结本次epoch/源/显示代及稳定ID映射。SelectionChanged送出前按当次显示代复核、Dispatcher回调后再核仍为同桥/同binding；旧桥封口后不投递选择，不能在宿主外给DTO暗加字段。桥Show接收的是连续源中心坐标（允许亚像素），不得将测边/拟合点取整；整数中心仅指原帧坐标约定。

源切换指Frame.Asset/Generation、Support或坐标来源改变；不借`ReplaceDraft`直接跨源。宿主先禁新命令/使旧展示键失效→Detach旧Editor并取消其推荐与执行→有限Wait/Retry至所有原Task/lease真实Drained→桥撤本层/退出本次Apply/Dispatcher/呈现借用→对仍可复用的viewport session调用UpdateAsync全量新context（其失败/Unknown保旧Owner，不当新源Ready）→以严格递增epoch重新Attach新Draft。`ReplaceDraft`仅接受同Frame/Support/Coordinates来源的参数/计划草稿变更；跨源抛InvalidOperationException且不改原binding。旧源排空未知时保留关闭管理器/恢复入口，不开放新源Run；不释放在用Frame，也不改用户源或服务全局状态。

关闭窗口时Closing先取消本次物理关闭、封命令，Dispatcher继续工作，调用并保存原`DetachAsync` Task（ValueTask只AsTask一次）。Drained才进入桥撤层→viewport binding.UnbindAsync→宿主按OwnSession及自身service所有权有限关闭；未知/异常时宿主关闭管理器持有editor/binding/bridge/Window与Dispatcher、DetachTicket、原Execute/Recommend/Detach/Apply/Unbind/Dispose Task、源借用及释放账。ticket接收只是Owner转移，不是Drained；本UI回调在转移时封投影，物理解除及Clear完成仍由ticket/宿主追踪，不能等待未完成native时解除其底层引用。Query/Wait/Retry只恢复本操作，service总Close只由创建宿主在其它消费者退出后调用。

EditorDetachResult/Ticket的Drained只确认Editor自持Execute/Recommend、租约与订阅责任已收敛，包含同步Clear投影入口已调用；它不证明桥的异步Apply/呈现归还或viewport binding已Unbound。宿主必须再等桥原root/UI scope及UnbindReceipt的实际收敛回执；不能仅等DetachResult就关Dispatcher。桥无新增Core公共关闭API，它的生命周期由创建宿主与上游公开root/binding控制。

DrainUnknown期间允许宿主诊断入口有限查询/重试；原释放Task仍pending只等同一Task，已失败且退出才幂等重试同对象。迟到结果先归原Owner完成释放，再核接收键，失配留原诊断并丢投影；清理恢复后原Faulted/Cancelled/TimedOut结论不改成功。窗口/Dispatcher只在Editor、桥UI scope、自己拥有的session/service及源归还均确认后关闭；借用service/session的其它消费者仍可运行。不能用Dispatcher shutdown、Unloaded、超时回执或Process退出补写资源已释放。

### 8.6 W1：两个独立STA宿主的验收定位

复用§1.3唯一U1 TestHost，不新建工程/报告。后续同一个WPF Exe提供`--host engineering`（特征工程工具，孔/开口输入）与`--host embedding`（独立可嵌入控件示例，板边输入）两个入口；分别启动独立进程，每进程一个STA主线程/Dispatcher/Application和独立Frame/Profile/坐标/权限/ID/关闭Owner，串行验证固定1920×1080视口。embedding是无UI视觉项目的**可选外部WPF消费示例**，不是让无UI项目引用WPF；无UI工程本身只按§9.2调用Core/ImageLib。两入口都用§7.1→§7.2→A.5公开装配，不靠隐藏窗口初始化。

每个STA入口分别验证：正常校验/执行与树↔叠加↔属性/图表联动；空候选显示原诊断；取消不结束B消费者；同源改Draft旧结果不可覆盖；源切换直到旧Owner真实排空才开放Run；窗口关闭与在途推荐；Detach/桥Unbind超时后Query/Retry及迟到恢复。另以同一session/service的双binding、OwnSession=false验证关闭A仍可查询/运行B（各Editor专用recommender），只能移除A层/订阅/呈现借用。OwnSession=true只在创建宿主的UI scope完成后从slot外有限Close；失败/未知保原Task与根Owner，不能强关共享实例。

验收分视觉与行为：DevExpress25.2.3既有DockLayoutManager、TreeListControl/TreeListView、PropertyGridControl、ChartControl/XYDiagram2D、SuperTip按§8.1；图像优先、真实响应/残差、长ID/hash可读复制、取消常显；三语zh-CN/zh-TW/en-US经宿主动态切换，保Draft/焦点/选择。记录实际client/DPI及键盘/UIA/撤权/恢复状态，不改屏幕设置、不跑额外分辨率矩阵。测试定位复用T16/U1（W1）并按T11～13的真实适配路径验证取消/释放，推荐关闭另覆盖T19的相关行为；不以截图、BCL模拟或单STA入口代替双宿主真实WPF。本轮只完成上述规格，未创建TestHost、编译或运行。

两个入口的实际全字段装配与有界Owner分别在§8.7～8.10；本节入口名称/验收定位不单独充当Host已完整的证据。

### 8.7 两入口共用的私有HostOwner与夹具实施卡

本节及§8.8～8.9是**既有TestHost内的正式语义代码/私有实现卡**，不是新增产品Root API或已编译代码。`F`表示`Asun.Modules.Features2D`，`E`表示其`.Ui.Wpf`，`V`表示`Asun.UI.Viewports`，`W`表示其`.Wpf`；名字冲突的PixelRect/PixelLayout明确用namespace别名。私有类只放§1.3的原Tests/TestHost，各工程不引用另一个测试工程；无UI Tests使用相同输入构造规则和非WPF Owner部分。默认软件Host沿§9.1的hole/board-edge完整模拟输入，不能把全0原帧和脚本输出当真实HALCON证据。`ImageLibFeatures2DBackend(真实qualification)`的A1消费仍沿§7.1；这里只替换backend和相应真实输入/版本，其余Owner/公开调用链不换，不以sim-1资格给生产backend装配。

**调用前的进程槽。** 私有`HostOwner`具有`static readonly HostOwner?[] Slots = new HostOwner?[3]`及锁；这只是测试进程根，非模块静态服务。`HostOwner.Register(string hostId, int maxTasks, int maxObjects, long maxPayloadBytes, TimeSpan attemptBudget, int maxAttempts)`先验证正数/唯一ID/空槽，原子登记Owner再返回；无容量抛测试失败且不调用任何factory/源。两个独立进程各占1槽；同进程共享测试最多creator+A+B三槽，不能覆盖Unknown旧槽。固定本例值为Tasks=128、Objects=64、Payload=512MiB、每组件每次2s、两次有限尝试；24个Task槽及16个对象槽专用于关闭/归还，普通工作不占。预算是软件fixture上限，不是native/进程RSS强限或性能目标。

| 私有字段/成员 | 必须构造或执行的确定行为 |
|---|---|
| 固定字段 | HostId、SlotIndex、MaxTasks/MaxObjects/MaxPayloadBytes/AttemptBudget/MaxAttempts、Stopwatch单调起点；AdmissionClosed/AllowPhysicalClose；对象表、输入表、任务表、操作ID表、关闭步骤表、FirstBusinessError、最多32条CleanupErrors及DroppedCleanupErrorCount。对象表保存Reference identity、所属/借用、宿主实例和依赖；输入表保存Request/Frame原bytes/hash、Profile/Support/坐标完整引用、epoch/local revision、context及来源token映射。Application/Window/Dispatcher/root/session/control/binding/editor/bridge/fixture/service/recommender/CTS/委托全部强持；不以Task名字代替原对象。 |
| `T New<T>(string key, Func<T> construct)` | 在锁下先占对象/输入额度并登记Constructing，再在锁外调用一次construct，无资源的backend/Control构造据实标Lazy；返回后在同槽存原对象。同步构造抛错记录FirstBusinessError、保既有对象并标该槽构造失败，不能删除其它责任。factory自身不得抛错遗失已创建资源；root有资源后所有调用走Start。纯函数编码/helper在本槽内受字节预算，不另开工作。 |
| `Task<T> Start<T>(string key, Func<Task<T>> call)`及Task无值重载 | 调用前预留本任务、最大1个迟到交付对象及恢复槽，登记Starting；释放锁后只调用一次，立即保存**原Task**，返回该原Task。取得ValueTask的call只AsTask一次。OriginalTask/身份/依赖/原输入、Started/Completed/Fault、迟到结果及释放证据留在表；包装WaitAsync不是原Task。同步call抛错归原业务/清理账，不把构造或调用当已无资源；迟到成功binding/lease由同记录接管。没有空槽/额度不执行call。 |
| `StartControl<T>(key, Func<Task<T>>)`及无值重载、`NewControl<T>(key, Func<T>)` | 登记/原Task保持规则与Start/New相同，但只用预留控制额度，业务门封闭后仍可登记既有组件的Detach/Wait/Retry/Unbind/Close/Return及有限观察。NewControl仅允许单个恢复Window/按钮/委托或已登记迟到结果责任；不准创建新fixture/factory/session/业务operation。普通New/Start不能借此绕关闭门；所有§8.10清理调用均经StartControl，构造失败后的恢复Window经NewControl，容量不足保原Owner而不先调用。 |
| `Task<T> Observe<T>(Task<T> original)` | 只对original做2s单调有限WaitAsync，观察Task也占控制槽；超时/取消只记本观察，不删除original或重发操作。actual Task/lease未归还仍计容量；成功/失败回执复制进有界步骤状态；原业务错误只第一次设置，不被finally覆盖。 |
| `Task BeginClose()` / `Task RetryClose()` | 在Dispatcher入口封新工作/回调，登记CloseAttempt原协调Task再执行§8.10；首次重复BeginClose共享在途协调Task。Retry只在该协调Task已返回且次数<2时创建新的有限观察，不启动第二个pending Dispose/Detach/Apply。协调者不计入自己需等待的资源worker集合；无UI没有Dispatcher时用同规则在调用线程进入。 |
| `PinWindow(Window w, Dispatcher d)` | 保存w/d及所有Closing/Loaded/SizeChanged/ResultAvailable委托；Closing设e.Cancel=true（AllowPhysicalClose=false时）并调用BeginClose，不在事件上async void长等。关闭恢复入口调用RetryClose；Window.Close只在§8.10确认后置AllowPhysicalClose=true再调用，接着Application.Shutdown，Dispatcher最后退出。 |
| `RecordResult(Features2DResult r)` / `RecordBusinessFailure(Exception ex)` | 保存完整托管结果/首个错误及输入身份；超过结果预算只拒本次可见交付并保原结果Owner，不能写PASS。已记录业务失败时cleanup异常追加CleanupErrors；退出码业务失败或cleanup Unknown均非零。 |
| `TryRemove()` | 只有全部构造/原任务已退出、每借用已确认归还、UI委托/呈现已撤、本宿主拥有的root/session/service关闭确认、Window实际Closed及Dispatcher退出可确认才在锁中清本槽；运行期间成功退出准备只标ReadyToRemove，最终由Main在Application.Run返回后确认删除。Unknown保槽/对象/原Task/诊断并拒第三次自动重试；只在明确恢复动作后继续有限观察，不后台循环。 |

**已定义的私有输入构造，不留BuildFixture。** `new HostFixture(HostOwner owner, string kind, TimeProvider clock)`先被owner.New登记；kind只接受hole/board-edge。构造只分配640×480个0字节（307200 bytes），按§9.1一次构造所有下列字段；没有设备/文件/Dispatcher工作。Asset构造私有`A(id,bytes)`固定Revision="fixture-1"、Sha256=lowercase SHA256(bytes)，UTF8严格无BOM；Support字节为480行`row,0,639\n`，末端闭列遵A.1；Frame的Asset用全部原bytes。Method/FitQualification的资产内容分别是A.1规范编码的该表字段值（Qualification.Asset位置写N排自引用）；Profile按A.4同样Asset位置写N取完整规范hash；不以名称hash代替内容hash。

fixture字段固定`Bytes/Clock/Request/Qualification/CoreFrames/CoreCoordinates/CoreResources/ScriptBackend`；后三源可由HostFixture分别显式实现A.3端口，ScriptBackend为私有独立对象。Request所有字段构造如下，均来自§9.1，不补生产默认：

- Identity=(kind+"/run-1",kind+"/run-1",1,kind)；Frame=(A(kind+"/frame",Bytes),1,640,480,Mono8,640,clock.GetUtcNow()+60s,A(kind+"/acquisition",UTF8("fixture-only")))；Support=(A(kind+"/support",上述runs字节),Frame.Asset,480条PixelRun(row,0,639))。
- hole Slots顺序ID=s0/s1/s2/s3；Origin及V逐项用§9.1表，半长8/2、role=reflection-edge；Groups=[FitGroup("circle-0",[s0,s1,s2,s3],Edge)]、Windows=Empty，Plan=(MeasurePos,Circle,Slots,Windows,Groups)。board-edge Slots/Groups=Empty，Windows=[AnalysisWindow("line-0",F.PixelRect(100,100,128,128),F.PixelRect(108,108,112,112),"outer-edge")]，Plan=(Xld,Line,Slots,Windows,Groups)。
- Caliper/Xld/Fit/FitQualification及ParameterDeltaLimits全部按§9.1两列原值逐字段构造；Profile=(完整hash Asset,MethodAsset,"sim-1",0,2,Mono8,2,.000001,相应Caliper,相应Xld,Fit,FitQualification)。Coordinates=(Image,"px","row","column",ImageRaster,null,null,clock.GetUtcNow()+60s)。Budget=(clock.GetUtcNow()+60s,256,16,16,64,4096,4194304,67108864,1)。三个期限同一次构造取now，不在等待/重试时延长。
- Qualification=(A(kind+"/backend-qualification",完整Methods规范字节),"sim-1","simulation",[MethodQualificationRule(MethodAsset,Plan.Route,Mono8,.4,2,2,640,480,8,4096,1048576,32,256)])；CoreServiceOptions=(8,1,1,16,67108864,64,TaskScheduler.Default)。该Rule只喂私有ScriptBackend；ImageLib生产qualification不用它。

夹具端口不是未定义外部factory；必需实现及默认正常结果如下，取消/失败脚本只是既有T闩锁注入：

| 私有端口/对象 | 构造、正常输出及归还行为 |
|---|---|
| CoreFrames / CoreCoordinates / CoreResources | Frame Acquire仅核完整Frame/hash/generation和期限并交新的lease(Data=fixture.Bytes)；每次借用ID独立，Dispose只归该borrow。Coordinates=Image默认不会Acquire；Target专用case按§9.1仿射，批次Map同长度/顺序。Reserve实际ReservedBytes=requested且累计≤64MiB，超限F2D-013；ObserveUsage/Peak按A.3，不计虚构native字节；Dispose幂等归原额度，失败保原对象。源关闭为私有fixture.CloseBorrowers：只封新借用、等待已登记借用/资源账为空，不Dispose别人的fixture或借用源。 |
| ScriptBackend / ScriptJob | Descriptor=("sim-1","simulation",true,[MeasurePos,Xld],[Circle,Line])；DescribeSupport按A.3固定Rule公式，Open成功返回(new ScriptJob(request,frame,resources),null)，无隐藏native对象。Extract(hole各slot)为RawWorkResult(该ID,true,有效整数Origin,[EdgeObservation(0,原Origin,20,0)],其余6个数组Empty,Errors.Empty)；board为一个parent=0/segment=-1原Contour与segment=0/ContApprox=-1（线），IsClosed=false/OriginalMapping=Exact、§9.1六点逐点Local/OriginalIndex=0..5，Response=20、AngleRad=0、EdgeDirectionRad=0均Provided，EffectiveOrigin=null，其余观察数组Empty。Fit(hole)返回CircleGeometry(input.Context,(240,300),40,0,1.5π,"positive")/Method="geometric"；Fit(board)返回LineGeometry(input.Context,(120,110),(120,210),(120,110),(120,210),1,0,120)/Method="regression"；Ellipse distances=null/Errors.Empty，五次主/挑战按该脚本同值，不能称真实fit。job取消保Task，Dispose幂等且模拟资源真实归还后完成。 |
| FixtureViewportPorts(owner,fixture,viewportControl,dispatcher) | 此私有构造无源获取；同时显式实现V.IFramePort/ICoordinatePort/IAuthorizationPort/IViewportBackendFactory/IPresentationPort，只挂本fixture及本Control所属Dispatcher；Roi/Surface/Probe/IntentSink均不实现、不注入、不申请功能。其CPU payload是私有FixtureFramePayload(Bytes)，非HObject。Frame请求核SourceId=kind、SourceRevision=Frame.Asset.Sha256、CoordinateRevision=1、level0/tile(0,0)/decode=kind+"/decode-1"/AccessDomain=kind+"/offline"；返回V.PixelLayout(640,480,1,640,UInt8,true,true)、V.PixelRect(0,0,640,480)、AffineMap2D(1,0,0,1,0,0)、新LeaseIdentity(owner.HostId,新lease ID,fixture原allocation ID,307200,kind,原hash,call.Generation)。Return/Query同ReturnId，借用已退出才Returned；不同borrow不互相Dispose。 |
| 坐标/授权 | Map只接受已绑定revision=1及明确source-center→source-center，返回CoordinateResult(原Revision,原ToSpace,Pixel,原有序Points,全true)；其它转换Rejected且无Value，不能假标定。Auth固定OwnerId=hostId+"/auth"/Revision="a1"/Purpose=OfflineViewing/Read/AccessDomain=kind+"/offline"/expiry=TimeProvider.System.GetUtcNow()+60s；Check核请求源列表、权利、同完整Expected和实际UTC期限，成功PortResult(Succeeded,该快照,null)，撤权Changed发新revision并使迟到Commit失效。 |
| BackendFactory / Presentation | BackendPolicy=OfflineRasterOnly，factory CreateAsync在root所登记调用内交新私有FixtureRasterBackend，Capabilities=(OfflineRaster2D,1,true,true,false,true,false,"fixture-raster-1")；仅真实WPF CPU WriteableBitmap/叠加呈现本fixture，不调用HALCON。Submit核scene来源/代/授权和layout，root持Frame借用，产生唯一SubmissionId/PresentationId，保存该scene与原receipt的有界可信关联，返回匹配generation/backendgeneration=1、VisibleConfirmed=false。FixtureViewportPorts实现IPresentationPort.CommitAsync/RevokeAsync仅直接return本vc的IViewportControlBinding.Presentation.CommitAsync(request,call,ct)/RevokeAsync(request,call,ct)，不async包装、不自行Acquire或造true回执；同binding内部按§8.7.1核原submission/授权并追踪Presenter。Backend.Revoke与Lifetime.RevokePresenterAsync分别等本backend/presenter实际引用退出，勿在Lifetime中回调facade.Revoke形成递归。Close沿同清理回CleanupSnapshot，未知保root原任务/lease，不强造Drained。 |

WPF fixture的bitmap上传及Presenter借用按viewport0.3.4-prep §10.7原Task/Work+Control登记；本Host卡只消费该公开链，不重复造renderer公共API。`FixtureViewportPorts`的同一私有对象还实现已公开`W.IViewportUiLifetimePort`（InstallEmpty/RemoveSubscriptionsAndVisuals/AcquirePresenterAsync/RevokePresenterAsync）：构造时保存vc、Dispatcher和有界Presenter记录表；InstallEmpty仅安装本Control的空呈现UI，Acquire签名为`Task<V.PortResult<W.IViewportPresenterLease>> AcquirePresenterAsync(W.ViewportPresenterSubmission submission, V.CallContext call, CancellationToken ct)`，其中submission保Request/原PresentationRequest/原SourceCall，call为root新签发child。先核本backend原Submit记录及原scene/bytes借用，再以原root槽创建私有FixturePresenterLease，不能用request.Id猜图像；Revoke先封该presentation再等待已有绘制/订阅/bitmap引用退出。FixturePresenterLease显式实现V.IViewportLease和W.IViewportPresenterLease；Identity按本Owner+presentation借用生成（字节含CPU bitmap真实缓冲），ConfirmVisibleAsync保持`PresenterLeaseRequest,CallContext,ct`公开签名，核request三种代号+冻结原输入/当前授权，并消费上游§10.8实际Raster观察步骤（原RenderTargetBitmap/本控件client读回/有限原Task、预算与失败分支），真实匹配才true；不能只看WritePixels、Rendering事件或Dispatcher完成。Return/Query沿原ReturnId与实际引用退出，unknown保记录，不把Task返回当可见/归还。此为原TestHost的有限CPU呈现fixture，生产HALCON renderer保持原门；lifetime通过Bind Options显式传`Lifetime: vp`，不调用Control私有方法或自造生产factory。

`FixtureViewportPorts.Resources`现在直接消费viewport0.3.4-prep §10.9已公开`W.ViewportUiResourceCatalog.Get("zh-CN")`：Host构造前预留资源输入额度并保存返回PortResult，仅Outcome=Succeeded且Value非null时使用该完整ViewportUiResources；核Revision等SchemaId=`viewport-ui-text/1`、Text精确覆盖RequiredKeys，拒绝/错误仍保原回执走有限关闭，不写旧`fixture-text-1`修订或猜七个键。语言切换用同Catalog.Get(目标culture)成功快照调用原binding.SetResourcesAsync，缺键按上游原子保旧规则。这里仅同步最后接线所需的已定义上游资源输入，不重写本模块§8.4完整三语。

**features-2d自己的资源与该字典分开且已闭合：** Editor在同UI DLL读取§8.4.1～5明确三语嵌入资源，宿主恢复Button按本指导Command.RetryClose/Recovery各词条在自己TestHost嵌入同文字，不借viewport的Recovery文本补本模块；元件/孔/板边命名仍由宿主自己的业务语言负责。Host同时调用Editor.SetCulture与viewport binding.SetResourcesAsync，保各自回执，不能把Editor已切换冒充整个viewport切换完成。原F2D-UP-UI-02把本模块完整词表移交viewport的处理撤回；本模块文字Owner始终是本原会话。

私有`FixtureOverlayBridge(owner, root, session, fixture, attachmentId, epoch)`显式实现E.IFeatures2DViewport：本fixture初层/全量Replacement账、WorkId/CandidateId对应LayerId表、当前generation和原Apply/Dispatcher/root reservation表皆由owner持有，maxLayers=32/maxPoints=4096；Show按§7.2/8.5封存源与结果键，Core ImagePoint(A=row,B=column)→V.SourcePoint2D(B,A)，不取整。每个work的Edges/Contours/Segments各生成独立SourcePolyline，Primitive显示只取其Evidence.InputPoints作为支撑层，不自行写圆/椭圆采样算法；候选模型/数值仍在Editor。每层完整构造`OverlayLayer(new StableObjectId(attachmentId+"/"+稳定work或candidate ID+"/"+层种类),zOrder,true,true,new OverlayPayload(SourcePolyline,new SourceId(kind),new CoordinateRevision(1),new GeometryRevision(1),[],原有序点,"",0),Frame.Asset.Sha256)`；无实际几何点不造空Polyline，空结果用无layer+原错误文字。Bridge.Apply由owner.Start保存**session.ApplyAsync(new SetLayersCommand(全量Replacement),ct)**原Task，且在启动前按viewport.ReserveExecution/BackendAdapter槽规则登记，root scope不等待自身Close。Clear只移本attachment层，保共享聚合账其它层；ClearAsync原Apply Task由私有owner步骤保存。该helper是明确的测试桥实现，不是扩充Core接口。

**原停点已关闭（F2D-UP-UI-01，定位§17.1）：** viewport0.3.4-prep §10.6～10.9现已公开同控件Presentation转发器、binding:IPresentationPort、Options.Lifetime/ExecutionBudget、ViewportPresenterSubmission和GetPresentations原Task观测。§8.7.1及两个Host入口按这些实际签名接入同Control/binding，无另一个Root/Close或内部回调。正常可见仍须真实观察确认；未知呈现或缺键拒绝并保Owner，不能以文档接线闭合替代实际运行。

### 8.7.1 同 Control/binding 的公开 Commit、Presenter 与归还接线

2026-10-11本轮只读viewport0.3.4-prep §10.6～10.9最新公开签名并复用原§3.3/3.6/4.6.1/11.2，不重审上游已验设计。Core API0.1与WPF Assembly Contract v0.2分别绑定，不替换本模块Core v0.2。HostOwner是§8.7/8.10自己的有界进程Owner，不替代ViewportRoot。下面各步全部用已公开接口，与§8.8/8.9/8.10同一链，不新增Root/Session/factory/Close/receipt类型。

| 消费操作与必需输入 | 当前公开入口及直接接法 | 必需输出/失败或迟到责任 |
|---|---|---|
| Factory前持Owner/额度 | HostOwner.Register先占槽；new ViewportRootFactory().Create(完整ViewportRootOptions)，保存原root；root.CreateFactory().Create(完整ViewportOptions) | 同runtime root/session，不以RootId文本替代实例；创建失败仍由Host记录错误并关闭已创建root |
| 空控件绑定 | new ViewportControl()→其稳定IViewportControlBinding.Presentation先接到Options.Presentation→Create session→BindAsync(session,root,ViewportUiBindingOptions,ct)，显式Lifetime:vp及ExecutionBudget，保原Bind Task；OwnSession显式，先Bind后Attach | PortResult<IViewportUiBinding>的Outcome/Value/Error全部核；失败Value若存在仍登记，超时pending Task晚回binding也进入同Host关闭账；constructor/facade无IO，Lifetime=null在Reserve/Dispatcher前拒绝 |
| 每次原Dispatcher/桥Apply登记 | root.ReserveExecution(绑定原session/当前Generation/已预留Work+Control额度)→reservation.Start(work,cleanup)；Work.StartOriginal只交原DispatcherOperation.Task或原session.ApplyAsync Task，extractLeases核实际结果 | Root-issued CallContext，原Task/lease由root强持；Reject不调用委托；Start前失败AbortBeforeStart，Started后只能RequestCleanup；不伪造scope，不把Wait wrapper当原Task |
| 源Attach/Update与只读层投影 | session.AttachAsync完整Context，UpdateAsync全量新Context，ApplyAsync SetLayersCommand完整Replacement，原Tasks沿Host/bridge/root登记 | Outcome/Error/Cleanup+实际显示代；失败/Unknown保原source/层账，不把计划完成当VisibleConfirmed；共享层聚合Owner串行 |
| 原backend提交及呈现请求 | IViewportBackend.SubmitAsync返回原BackendSubmissionReceipt；session调用Host IPresentationPort.CommitAsync(原PresentationRequest,原CallContext,ct)，Host直接return同vc.Presentation.CommitAsync(request,call,ct)，其转发同IViewportUiBinding:IPresentationPort | binding核同root/session签发SourceCall、原submission可信记录、ContextRevision/两代/ExpectedAuthorization全部字段及当前权限/期限；输出同binding PortResult<PresentationReceipt>，Host不新建receipt、不覆盖sourceCall/延长期限、不包装原Task |
| 控件内部Presenter寿命 | 同binding原reservation.Work.StartOriginal→ui=Options.Lifetime的AcquirePresenterAsync(ViewportPresenterSubmission(Request,Presentation,SourceCall),childCall,ct)→lease.ConfirmVisibleAsync(Request,childCall,ct)；Control沿RevokePresenterAsync→lease.ReturnAsync/QueryReturn同ReturnId | root提取失败Value/迟到Acquire lease，原Acquire/Confirm/Revoke/Return Task及lease强持；child剩余预算裁到原Commit剩余，真实匹配VisibleConfirmed才true；Host不另造reservation/Root，不在Lifetime回调facade造成自等待 |
| 本Editor退出 | editor.DetachAsync有限等待，DrainUnknown保同ticket及借用service，Query/Wait/Retry定向本IDs；桥撤本层保原Clear Apply | Editor Drained只证明本Execute/Recommend/UI订阅收敛，不证明viewport异步呈现/源已归还；原Task pending不重复调用Dispose |
| 原viewport UI scope退出 | binding.UnbindAsync(timeout,ct)，清理由原reservation.RequestCleanup及原Control.ObserveAsync负责；Host调用在slot外 | UiUnbindReceipt.Detached/Drained/WaitCancelled/Cleanup/Error分开核。OwnSession=false仅撤本binding，true才由已armed且slot外controller关闭同session；pending/Unknown不移除恢复Owner |
| Session/Root有限收尾 | 宿主创建者在所有借用binding退出后session.DisposeAsync(timeout,ct)，再root.CloseAsync(timeout,ct)，各原Task只启动并登记一次，后续用同实例有限观察 | DisposeReceipt.Drained/WaitCancelled/PendingResources/Error/Cleanup与RootCloseReceipt/RootSnapshot；CleanupState.OwnerAccepted和AcceptedTransferId只证明root确认接管，Drained仍false，不能删Host槽或关闭Dispatcher |
| 晚到/失败资源归还 | 原StartOriginal extractLeases保任何失败Value/迟到结果；原Return pending只等，真实返回后QueryReturn同ReturnId，有限次数耗尽仍root Pending/Unknown | 源borrow独立归还；A取消不释放B，Root/Host强持至实际退出。调用取消只停观察；重启/方法离栈不延续原Task责任，不报告归还 |

**原输入和原Task的确定绑定。** FixtureViewportPorts同时实现BackendFactory/Lifetime/Presentation，但三个端口面责任不同：backend保存Submit产生的scene/原receipt可信表；presentation仅直接转发同Control facade；Lifetime保存完整ViewportPresenterSubmission而不重建原SourceCall。Request.BindingId等本binding，Generation/BackendGeneration/PresentationId等Presentation.Submission；SourceCall是session调用Commit的原root-issued调用，Acquire参数childCall是binding的Work.StartOriginal新签发调用，两者不得互换。原ExpectedAuthorization/ContextRevision不从latest补写；Acquire及实际Dispatcher Confirm再核当前权限/期限。backend原frame/tile借用留到原Revoke/Close真正退出，Presenter另外持本UI buffer/scene引用，返回其本地borrow不能顺带Dispose共享源或service。

两个Host明确给`new ViewportUiExecutionBudget(67108864,32,32)`，从Host512MiB和原root256MiB账预留本binding64MiB及Work/Control槽；当前1920×1080固定验证viewport实际client W/H的bitmap/期望输出/读回按上游§10.8 checked(16×W×H)+tile staging+metadata计账，超限在获取前拒绝，不动态扩额。已定义实际Raster观察路线直接复用上游§10.8：保持原输出/原submission、只读本控件client、有界原Task/授权复核/匹配与不可见或未知拒绝；不只用Dispatcher完成、截图或fixture假回执宣称可见。软件64MiB/槽数不是客户性能/部署默认；实际产品Profile由其Owner给。

**Commit幂等与观测。** 同SubmissionId+PresentationId+generation/backend且输入完整一致，facade/binding返回同一个原Commit Task；同键异内容016且无新Acquire。Bind前/关门后的新Commit拒绝，无隐式Bind；Revoke清理仍沿原PresentationId路由原binding，不路由最新binding，不要求旧Read权限继续有效。Host通过原`h.ViewportBinding.GetPresentations()`取得有界ViewportUiPresentationTrace观测表，逐项保BindingId/原Presentation/SourceCall/OriginalCommit/Acquire/Confirm/PresenterIdentity/Revoke/Return/Cleanup；这都是runtime观测，不移交lease或序列化Task，不能从trace重新发Acquire或手动Return。root是原Task/lease的清理权威，Host只关联其Pending/原业务错误与本关闭步骤；未归还项不逐出，业务Commit结束不等ResourcesReleased。

**Unbind与晚到。** Commit接纳与Unbind封Work门串行；已接纳Acquire晚回、失败Value带lease或handler未赋值，root extractLeases仍捕获原对象，先原Owner Revoke→实际引用退出→同ReturnId Return/Query确认。原Acquire/Confirm/Return pending只等同原Task，不另发/重建lifetime；Confirm已返回false或超时仍须原清理收敛。Unbind观察取消/到期不丢trace/root Owner，继续用同binding.GetPresentations、原root快照及有限Unbind/Close观察；旧binding未Drained不得复用Lifetime或重Bind。同共享session两Control各自Lifetime/Presentation facade、各自trace和UI槽，OwnSession=false关A不清B，最后创建Owner才关session/root。OwnSession=true关闭同session仍由已armed slot外controller执行，Control不等自身或root.Close。原Root/Close合同不变，未确认归还不移除Host槽/关闭Dispatcher。

本次窄修实施反例复用既有T12/T13/T16/T18/T20～22和viewport VP-U03/VP-U04，不新增测试工程：①Bind前Commit或Lifetime=null拒绝且Acquire=0；②同输入重复Commit返回ReferenceEquals同Task，一次Acquire，异输入/跨Control/root/sourceCall/授权/ContextRevision拒绝；③Acquire晚到/失败Value有lease、Confirm已过期限、Unbind同时封门仍在trace/root保存原引用，不能true或早Return；④原Return pending重复关闭只有限观察原链，Unknown仍保Owner；⑤A关闭/B继续及不可见/实际读回不符均不假报通过。正常反例核完整ViewportPresenterSubmission字段、同原Task、真实receipt代/授权及归还；取消/超时分别核原业务结果和清理轴。此为本次指导定向自审及后续真实Host断言，未运行WPF/显示观察。

### 8.8 入口一：特征工程工具的完整STA装配

以下`HostOwner`/`HostFixture`/`FixtureViewportPorts`/`FixtureOverlayBridge`是§8.7精确定义的私有类；不存在BuildFixture或未定义辅助factory。两入口在各自STA Main先Register，再创建Application/fixture/root。时间：Core软件fixture使用初始UTC=2026-10-09的私有TimeProvider（GetUtcNow/单调timestamp/GetElapsedTime由harness原闩锁推进），viewport权限使用真实System UTC避免给上游固定过期期限；两者不相减。client尺寸/DPI在Window实际Loaded后读，不用下面Window外框代替client。

```csharp
// engineering: a separate [STAThread] process, namespace aliases F/E/V/W as above.
var h = HostOwner.Register("engineering",128,64,512L*1024*1024,
    TimeSpan.FromSeconds(2),2); // BEFORE Application/factories/frame work
try {
h.Dispatcher=h.New("dispatcher",()=>Dispatcher.CurrentDispatcher);
var app = h.New("app",()=>new Application { ShutdownMode=ShutdownMode.OnExplicitShutdown });
var clock = h.New("clock",()=>new FixtureTimeProvider(
    new DateTimeOffset(2026,10,9,0,0,0,TimeSpan.Zero)));
var f = h.New("fixture",()=>new HostFixture(h,"hole",clock));
var root = h.New("root",()=>new V.ViewportRootFactory().Create(new V.ViewportRootOptions(
    "engineering/root",2,256,128,256L*1024*1024,TimeSpan.FromSeconds(2),2)));
var factory = h.New("factory",()=>root.CreateFactory());
var vc = h.New("viewport",()=>new W.ViewportControl()); // lazy, no frame lease
var editor = h.New("editor",()=>new E.Features2DEditor()); // lazy
var window = h.New("window",()=>new Window {
    Title="特征工程工具", Width=1600, Height=900 }); // fit fixed viewport, §8.7 size policy
h.PinWindow(window,window.Dispatcher); // Closing/Closed installed BEFORE Show
var vp = h.New("ports",()=>new FixtureViewportPorts(h,f,vc,window.Dispatcher));
var session = h.New("session",()=>factory.Create(new V.ViewportOptions(
    ConsumerId:"engineering", AccessMode:V.ViewportAccessMode.ReadOnly,
    RequestedFeatures:V.ViewportFeature.Navigation|V.ViewportFeature.Presentation,
    Frames:vp, Coordinates:vp, Authorization:vp, MaxDisplayBytes:67108864,
    MaxInFlightTiles:1, ResourceAdmissionMode:V.ResourceAdmissionMode.BudgetOnly,
    DrainTimeout:TimeSpan.FromSeconds(2), OperationTimeout:TimeSpan.FromSeconds(2),
    Roi:null, Surface:null, Probe:null, Presentation:vp, ResourceAdmission:null,
    Limits:new V.ViewportLimits(2,32,4096,16,16,64,4096,1,4),
    BackendPolicy:V.BackendPolicy.OfflineRasterOnly, Backend:vp,
    IntentSink:null, UpdateThrottle:null)));
var service = h.New("service",()=>new F.Features2DService(f.CoreFrames,f.ScriptBackend,
    f.CoreCoordinates,f.CoreResources,clock,new F.ServiceOptions(8,1,1,16,67108864,64,TaskScheduler.Default)));
var rec = h.New("recommender",()=>new F.Features2DRecommender(service,clock));
var bridge = h.New("bridge",()=>new FixtureOverlayBridge(h,root,session,f,"engineering/editor",1));
// Window.Content: Grid two columns 3*:2*, vc then editor; recovery entry outside columns.
// h.InstallLayout is the precise private UI-only procedure below; no extra factory.
h.InstallLayout(window,vc,editor);
window.Loaded += (_,_) => h.Start("startup",async () => {
    var originalBind = h.Start("bind",()=>((W.IViewportControlBinding)vc).BindAsync(session,root,
        new W.ViewportUiBindingOptions("engineering/view",true,vp.Resources,TimeSpan.FromSeconds(2),8,1,
            Lifetime:vp,ExecutionBudget:new W.ViewportUiExecutionBudget(67108864,32,32)),
        CancellationToken.None));
    var bound = await h.Observe(originalBind);
    if(bound.Outcome!=V.PortOutcome.Succeeded || bound.Value is null)
        throw new InvalidOperationException("viewport-bind");
    h.ViewportBinding=bound.Value; // original task also captures a late binding
    var source = new V.ImageSourceDescriptor(new V.SourceId("hole"),640,480,1,8,false,
        V.PixelCoordinateConvention.CenterInteger,new V.CoordinateRevision(1),f.Request.Frame.Asset.Sha256,
        new HashSet<string>{"gray"},new V.ValidityDomain("engineering/frame",f.Request.Support.Asset.Sha256,
        new V.PixelRect(0,0,640,480),true,null),
        [new V.PyramidLevelPlanInput(0,640,480,640,480,new V.AffineMap2D(1,0,0,1,0,0),307200)],
        "hole/decode-1",new V.SourceStatistics(f.Request.Frame.Asset.Sha256,"hole/stat-1",
        new V.PixelRect(0,0,640,480),307200,0,0,0,true)); // constant gray, no feature claim
    var dpi=VisualTreeHelper.GetDpi(vc);
    var context = new V.ViewportContext([new V.SourceBinding(V.SourceRole.Primary,source,null,
        "hole/frame-group",Timing:null)],[],vp.Authorization,"zh-CN",new V.ApiVersion(0,1),0,
        V.ViewState.Fit2D(new V.DipSize(vc.ActualWidth,vc.ActualHeight),dpi.DpiScaleX,dpi.DpiScaleY));
    h.Context=context; // zero-size waits actual SizeChanged, does not attach invalid canvas
    var attached=await h.Observe(h.Start("attach",()=>session.AttachAsync(context,CancellationToken.None)));
    if(attached.Outcome!=V.OperationOutcome.Succeeded) throw new InvalidOperationException("viewport-attach");
    editor.Attach(new E.EditorBinding("engineering/editor",1,service,rec,bridge,f.Request,
        new E.EditorPermissions(true,true,true,true),"zh-CN",vp.ThemeName));
    h.EditorAttached=true;
    // Demonstrate the no-UI Core output; editor Run itself remains its normal public UI command.
    var result=await h.Observe(h.Start("execute",()=>service.ExecuteAsync(f.Request,null,h.OperationToken)));
    h.RecordResult(result);
    bridge.Show(new E.EditorOverlay(f.Request.Frame,result.Works,null));
    await h.Observe(bridge.ApplyStartedTask); // startup signal is NOT the Apply task
    var shown=await h.Observe(bridge.LastApplyTask); // retained original SetLayers task
    if(shown.Outcome!=V.OperationOutcome.Succeeded) throw new InvalidOperationException("overlay-apply");
}); // Start stores callback original Task, errors trigger BeginClose with first error preserved
window.Show(); h.ApplicationRunEntered=true; app.Run();
} catch(Exception ex) { h.RecordBusinessFailure(ex); h.FinishStartupFailure(); }
finally { h.AfterDispatcherExit(); } // §8.10: only confirms, never starts Dispatcher cleanup here
```

### 8.9 入口二：独立视觉项目的可选嵌入STA装配

此进程独立于engineering；无UI视觉项目本身不引用WPF。它的无UI入口只在Register/HostFixture/CoreServiceOptions后Start Execute并用§8.10的Core/源部分finally，输入kind=board-edge不变。以下是该项目外部可选WPF消费者，用OwnSession=false显示控件借用边界；创建session的这个host仍拥有最终session/root关闭，Editor/viewport binding不获得该权限。

```csharp
// embedding: independent [STAThread] process; same PRIVATE classes/cleanup card.
var h = HostOwner.Register("embedding",128,64,512L*1024*1024,TimeSpan.FromSeconds(2),2);
try {
h.Dispatcher=h.New("dispatcher",()=>Dispatcher.CurrentDispatcher);
var app=h.New("app",()=>new Application { ShutdownMode=ShutdownMode.OnExplicitShutdown });
var clock=h.New("clock",()=>new FixtureTimeProvider(new DateTimeOffset(2026,10,9,0,0,0,TimeSpan.Zero)));
var f=h.New("fixture",()=>new HostFixture(h,"board-edge",clock));
var root=h.New("root",()=>new V.ViewportRootFactory().Create(new V.ViewportRootOptions(
    "embedding/root",2,256,128,256L*1024*1024,TimeSpan.FromSeconds(2),2)));
var factory=h.New("factory",()=>root.CreateFactory());
var vc=h.New("viewport",()=>new W.ViewportControl());
var editor=h.New("editor",()=>new E.Features2DEditor());
var window=h.New("window",()=>new Window { Title="特征查看",Width=1600,Height=900 });
h.PinWindow(window,window.Dispatcher);
var vp=h.New("ports",()=>new FixtureViewportPorts(h,f,vc,window.Dispatcher));
var session=h.New("session",()=>factory.Create(new V.ViewportOptions(
    ConsumerId:"embedding",AccessMode:V.ViewportAccessMode.ReadOnly,
    RequestedFeatures:V.ViewportFeature.Navigation|V.ViewportFeature.Presentation,
    Frames:vp,Coordinates:vp,Authorization:vp,MaxDisplayBytes:67108864,MaxInFlightTiles:1,
    ResourceAdmissionMode:V.ResourceAdmissionMode.BudgetOnly,
    DrainTimeout:TimeSpan.FromSeconds(2),OperationTimeout:TimeSpan.FromSeconds(2),
    Roi:null,Surface:null,Probe:null,Presentation:vp,ResourceAdmission:null,
    Limits:new V.ViewportLimits(2,32,4096,16,16,64,4096,1,4),
    BackendPolicy:V.BackendPolicy.OfflineRasterOnly,Backend:vp,IntentSink:null,UpdateThrottle:null)));
var service=h.New("service",()=>new F.Features2DService(f.CoreFrames,f.ScriptBackend,
    f.CoreCoordinates,f.CoreResources,clock,new F.ServiceOptions(8,1,1,16,67108864,64,TaskScheduler.Default)));
var rec=h.New("recommender",()=>new F.Features2DRecommender(service,clock));
var bridge=h.New("bridge",()=>new FixtureOverlayBridge(h,root,session,f,"embedding/editor",1));
h.InstallLayout(window,vc,editor);
window.Loaded += (_,_)=>h.Start("startup",async ()=> {
    var originalBind=h.Start("bind",()=>((W.IViewportControlBinding)vc).BindAsync(session,root,
        new W.ViewportUiBindingOptions("embedding/view",false,vp.Resources,TimeSpan.FromSeconds(2),8,1,
            Lifetime:vp,ExecutionBudget:new W.ViewportUiExecutionBudget(67108864,32,32)),
        CancellationToken.None));
    var bound=await h.Observe(originalBind);
    if(bound.Outcome!=V.PortOutcome.Succeeded || bound.Value is null) throw new InvalidOperationException("viewport-bind");
    h.ViewportBinding=bound.Value;
    var source=new V.ImageSourceDescriptor(new V.SourceId("board-edge"),640,480,1,8,false,
        V.PixelCoordinateConvention.CenterInteger,new V.CoordinateRevision(1),f.Request.Frame.Asset.Sha256,
        new HashSet<string>{"gray"},new V.ValidityDomain("embedding/frame",f.Request.Support.Asset.Sha256,
        new V.PixelRect(0,0,640,480),true,null),
        [new V.PyramidLevelPlanInput(0,640,480,640,480,new V.AffineMap2D(1,0,0,1,0,0),307200)],
        "board-edge/decode-1",new V.SourceStatistics(f.Request.Frame.Asset.Sha256,"board-edge/stat-1",
        new V.PixelRect(0,0,640,480),307200,0,0,0,true));
    var dpi=VisualTreeHelper.GetDpi(vc);
    var context=new V.ViewportContext([new V.SourceBinding(V.SourceRole.Primary,source,null,
        "board-edge/frame-group",Timing:null)],[],vp.Authorization,"zh-CN",new V.ApiVersion(0,1),0,
        V.ViewState.Fit2D(new V.DipSize(vc.ActualWidth,vc.ActualHeight),dpi.DpiScaleX,dpi.DpiScaleY));
    h.Context=context;
    var attached=await h.Observe(h.Start("attach",()=>session.AttachAsync(context,CancellationToken.None)));
    if(attached.Outcome!=V.OperationOutcome.Succeeded) throw new InvalidOperationException("viewport-attach");
    editor.Attach(new E.EditorBinding("embedding/editor",1,service,rec,bridge,f.Request,
        new E.EditorPermissions(false,true,false,true),"zh-CN",vp.ThemeName));
    h.EditorAttached=true;
    var result=await h.Observe(h.Start("execute",()=>service.ExecuteAsync(f.Request,null,h.OperationToken)));
    h.RecordResult(result);
    bridge.Show(new E.EditorOverlay(f.Request.Frame,result.Works,null));
    await h.Observe(bridge.ApplyStartedTask);
    var shown=await h.Observe(bridge.LastApplyTask);
    if(shown.Outcome!=V.OperationOutcome.Succeeded) throw new InvalidOperationException("overlay-apply");
});
window.Show(); h.ApplicationRunEntered=true; app.Run();
} catch(Exception ex) { h.RecordBusinessFailure(ex); h.FinishStartupFailure(); }
finally { h.AfterDispatcherExit(); }
```

### 8.10 共用有限finally、同Ticket恢复和两轮Host断言

上面私有helpers补齐如下：FixtureTimeProvider以指定UTC/timestamp0建立，只由既有测试闩锁推进UTC/单调量，GetTimestamp等与§9.1相同；InstallLayout只在Dispatcher创建Grid两列3*:2*、把vc/editor分别放入、底行放本地化重试Button（Click委托调用RetryClose），保存所有视觉/委托，不创建Shell/隐藏窗口。窗口按当前DPI将固定1920×1080物理验证区扣任务栏/非客户区后限制MaxWidth/MaxHeight，1600×900仅请求外框DIP，不能超过该区；Loaded前设置限制，ActualWidth/Height为0时等待**一次**已登记SizeChanged原Task（2s），不Attach非法canvas。ThemeName取当前Application已安装DevExpress主题的不可变快照，不能传猜测主题名或修改系统主题。

FixtureTimeProvider唯一私有构造为`FixtureTimeProvider(DateTimeOffset initialUtc)`（上面不是无参调用），TimestampFrequency=TimeSpan.TicksPerSecond，GetTimestamp返回闩锁保护的elapsedTicks、GetUtcNow返回initialUtc+elapsedTicks；推进非负量并checked，不重写TimeProvider.GetElapsedTime的框架实现。应用、fixture、root等任意New/构造失败都由入口的外层catch转`FinishStartupFailure()`：原Dispatcher尚未ShutdownStarted/Finished时登记BeginClose原Task；若Application存在且未Run过则Run一次，ApplicationRunEntered=true后不得再次Application.Run，无Application或已进入Run但Dispatcher仍有效时仅泵当前Dispatcher。不存在第二Application；组件确认后InvokeShutdown，无对象/工作可清理直接ReadyToRemove。构造失败导致原Window未Show或尚未创建时，在已保留关闭对象槽内创建/显示**一个**明确的恢复Window（正文错误摘要+RetryClose按钮），PinWindow/Dispatcher照旧，非隐藏窗口；关闭未知保持原Owner/恢复入口，不能只离栈。Dispatcher已经退出则不Invoke/Run，不尝试创建恢复窗口，记录强制中断与全部未确认责任；Main finally的AfterDispatcherExit只确认实际退出状态，不承担异步清理、不删Unknown槽。

HostOwner还必有OperationCancellationSource（独立实例，OperationToken为其Token）、EditorAttached、ViewportBinding、Context、OriginalDetachTask、DetachTicket、OriginalClearApplyTask、OriginalUnbindTask、OriginalSessionDisposeTask、OriginalServiceCloseTask、OriginalServiceDisposeTask、OriginalRootCloseTask、每组件AttemptCount/LastReceipt/Confirmed标记、LoadedOnce/启动门及`LastApplyTask`引用（Bridge自己拥有，host任务表也登记）。New保存引用同时按key赋这些字段；任务结果提取在观察之前登记，因此迟到Bind成功仍能获得binding并关闭。Loaded事件只一次，重复Loaded不再启动；回调Task任一异常记录原业务失败、调用BeginClose，无未观察Task异常。ResultAvailable/RecommendationAvailable的原委托在Attach前登记，仅记录/比接收键；控件内部Execute/Recommend原Task归A.5 Editor/Ticket，host不从可丢事件猜Task。代码中的直调Execute用独立run-1，随后UI Run仍由控件生成新ID，不把二者混成同操作。

`HostOwner.Register`登记成功后在同槽创建并保存OperationCancellationSource（初始未取消）、ApplicationRunEntered=false/LoadedOnce=false，关闭标记全部未确认；Task表control保留不受业务门封闭影响。New的固定keys正对应上述字段及App/Dispatcher/Fixture/Root/Factory/Session/ViewportControl/Editor/Ports/Service/Recommender/Bridge/Window；记录容量及父依赖后才构造。Observe有`Task<T>`及无值`Task`两重载。Start("startup",callback)登记的正是Loaded callback的原Task，回调开始前检查LoadedOnce并原子置true，所有后续h.Start/New在AdmissionClosed时拒绝，防止Close后迟到Bind continuation再Attach；已经取得的Value先存Owner再抛关闭错误。PinWindow还保存Closed确认委托、约定仅AllowPhysicalClose时放行，不在Closing回调内同步Wait。

桥的原Apply启动细化为唯一私有`ApplyReplacement(OverlayLayer[] frozen)`：Host/层聚合账在调用前预留冻结payload；以当前session.GetSnapshot().Generation调用root.ReserveExecution(new ExecutionReservation(session,generation,BackendAdapter,1048576,4,8,2s,false))并保存reservation/原回执，Rejected不启动Apply。Start的Work委托内用Work.StartOriginal(generation,(call,token)=>session.ApplyAsync(new SetLayersCommand(frozen),token),_=>Array.Empty<IViewportLease>())，Host表同时保存这一**原Task**到LastApplyTask；Apply/内部引用由session/root自己的任务账承担。Work只等待本Apply结果，不等自己的Observe/session.Close；Control封该桥投影、等其已启动原Task退出并返回Pending的ExecutionObservation（CleanupState.Pending、空Pending、Error=null），最终root在worker真实退出后才判scope收敛。slot外Host请求该reservation.RequestCleanup并有限Observe，对成功/失败Apply都归还本scope预留；未知不释放payload/槽。Clear使用同路径的新有限控制请求；root已关接纳时不能Reserve来造清理，走先前armed reservation/binding.Unbind/root.Close的撤销事实，原scope/原Apply不得遗忘。LastApplyTask从Work真正开始取得；若未启动/拒绝，桥记录明确失败回执供Observe拒绝，不能返回null或伪完成Task代替原Apply。

桥公开给**本私有TestHost**的字段形状为`Task<bool> ApplyStartedTask`、`Task<V.ViewportResult<V.ViewportReceipt>> LastApplyTask`及原Reservation/Control/Work任务记录；Show调用前占槽创建`TaskCompletionSource<bool>(RunContinuationsAsynchronously)`并保存其Task，Work.StartOriginal登记原Apply后才TrySetResult(true)，拒绝/启动失败TrySetException且留原失败回执。Main先有限Observe这个启动信号，再有限Observe原LastApplyTask；它们是两个对象，信号结束不等Apply/资源结束，不把包装Task当原操作。Clear另用自己的信号/原Apply，不覆盖还pending的Show记录；最多一个本桥Show在途，下一Show只合并尚未启动的托管投影并回显遗漏，不能合并已started原Task。每个有界task条目在原Task已退出且关联payload/borrow/cleanup真正收敛后才能回收，原输入/最后回执由有限32条诊断/当前结果保留，不保无限完成Task历史。

Start到Work真正调用之间遇到换代/关闭时，桥同时保存reservation.Start返回的原worker Task；该Task拒绝/失败/退出且未取得原Apply，就在同记录TrySetException终结ApplyStartedTask，并标LastApply=NotStarted，无资源证据仍以root原回执为准。不让一个从未启动的信号永远pending，也不捏造成功Apply；清理使用StartControl，桥业务Show仍走普通Start的接纳门。

§8.8/8.9正常输出断言必须逐项检查：Validate可接受，result.Receipt.IsSimulation=true/ResourcesReleased=true且身份/hash与输入完全一致；hole的circle-0有ValidCandidate和(240,300)/40，board-edge的line-0有线Nr=1/Nc=0/Dist=120及六点原索引；viewport Attach/原Clear或Show Apply的Outcome=Succeeded、Cleanup状态、代/授权/图层来源一致；仅Presentation真实确认才称图层已显示。Default ScriptJob、CPU图像与Renderer均不证明A1方法资格。bridge.Show之后LastApplyTask必须非null且等于owner登记的那个原Task；无图层/超限也有明确空Replacement回执，不直接报成功。

`BeginClose`/`RetryClose`都从**所有viewport slot之外**执行下面同一语义finally；每个组件先占控制槽，自己的2s观察/错误账独立，不能一个异常跳过其它独立组件；MaxAttempts=2只限自动初次+一次显式恢复，不丢Owner：

1. 原子封Host普通工作/Loaded/编辑命令/桥Show，OperationCancellationSource.Cancel；保FirstBusinessError。若startup原Task仍pending，观察它2s（不等待本Close协调Task）；保构造门/迟到提取，之后不能再从它启动新Attach/Execute，已经调用的任务继续登记/清理。原Task未退出，所有可独立关闭的已建组件仍进入下列步骤。
2. Editor曾Attach时保存唯一`OriginalDetachTask = editor.DetachAsync(2s, CancellationToken.None).AsTask()`，不能每个Retry重复调用pending ValueTask；观察得到EditorDetachResult.DrainUnknown就保存**同一个**Ticket。恢复对该ticket调用Query及`WaitAsync(2s,None)`/`RetryReleasesAsync(2s,None)`，每个ValueTask只AsTask一次；推荐子ID每次从ticket.Query().Recommendation重读，推荐Task未terminal/尚在提交时保持Unknown。无EditorAttach不伪造ticket；直调Execute另在host任务表取消/等待/按ID Retry，不能认为EditorDetach会替它释放。
3. 桥封投影后调用原Clear对应`session.ApplyAsync(new SetLayersCommand(合成剩余层),None)`一次并存OriginalClearApplyTask，迟到结果只在原root/epoch账收敛；若session已关闭不能新Apply，走已有root撤销/Unbind回执而不报Clear成功。桥的Apply/Presenter未退出保原责任。同一个pending Clear不重发；明确失败且原Task退出后仅同epoch有界再次Clear，不启动新业务请求。
4. 已交付/迟到交付的ViewportBinding保存一次`UnbindAsync(2s,None)`原Task，pending只等；回执Drained=false允许其公开幂等Unbind做新有限观察，但保持同binding和所有旧Task。每次观察核§8.7.1的binding.GetPresentations原Commit/Acquire/Confirm/Revoke/Return/Cleanup与root Pending，晚到/失败Value的lease由root提取并归原Owner，Host不从trace取得lease二次Return。OwnSession=true由binding/root的slot外关闭controller负责，host查询其回执并在必要时同session.DisposeAsync(2s,None)观察**同一关闭过程**，不在Work/Control内等待session关闭。OwnSession=false不因此关闭session；只有Host自己是创建Owner且全部其它binding已退出才保存/观察OriginalSessionDisposeTask。同进程A关控件而B仍运行时禁止session.Dispose/root.Close，session/root责任仍由共享创建Owner保留。
5. 独立于viewport的Core service关闭继续执行，原Execute/推荐已请求取消；创建Owner保存`service.CloseAsync(2s,None).AsTask()`，共享借用Owner仅`WaitOperationsAsync(自己的IDs,2s,None)`及同IDs Retry，不调用Close/Dispose。pending只等原Task，原Task已返回DrainUnknown可用相同service有限Close/Retry观察原关闭过程；业务失败不被ResourcesReleased/清理成功改成Completed。只有Core实际Drained及原Execute/Recommend全部退出才保存一次`service.DisposeAsync().AsTask()`；Dispose失败保同实例，不跳到释放Core底层源。
6. root属于本Host且所有共享消费者都退出时，保存`root.CloseAsync(2s,None)`并观察；它可协调失败/迟到Bind及session清理，host不能等待缺失binding才永不关root。root与service是独立分支：一方失败仍尝试另一方，记录两者原错误；FixtureViewportPorts/HostFixture源归还依其自己的借用账，只有对应borrow真实无访问/已归还才能清，没有依赖的另一个fixture继续清。native未知/失败不得跳过依赖释放门。
7. 每步根据真实回执记录Confirmed；外层cleanup `try/catch`逐步保存CleanupErrors，不throw替换FirstBusinessError，不return提前跳过独立后续。最后检查原Task表（不含本协调观察者）全部退出、lease/Presenter/root scope归还、Editor/Ticket推荐与执行terminal、自己拥有的root/session/service各Confirmed，才解除原委托/视觉，置AllowPhysicalClose，Window.Close。OwnApplication/OwnDispatcher=true的创建Host随后Application.Shutdown；共享A/B只借用creator的Application/Dispatcher，不Shutdown/InvokeShutdown别人的线程。Application.Run返回后AfterDispatcherExit仅核Dispatcher/Closed、TryRemove；若被外部强制shutdown而未Confirmed，报告Unknown保槽/诊断，不从finally再Invoke已退出Dispatcher，不声称清理完成。

源切换复用同Owner，旧Frame/epoch输入另占槽保留：封旧代→同Ticket/定向取消排空→旧层Apply归还→`session.UpdateAsync(new ViewportUpdate(oldContextRevision, 完整新Context),None)`登记原Task。新输入构造按同HostFixture卡，第二个byte buffer第0字节置1以区分hash，Frame.Asset.Id=kind+"/frame-2"、Generation=2，Support.FrameAsset换新Frame、Profile/Method不变，Identity=(kind+"/run-2",同值,2,kind)，三个新deadline一次绑定；SourceId=kind+"/source-2"、SourceRevision=新Frame hash、统计Min=0/Max=1/Finite=307200，ContextRevision=old+1。FixtureViewportPorts不是固定只认初源的全局查表；owner在调用Update前有界登记**第二份不可变来源binding**（原Frame/Source/Decode/Support/授权关系），Acquire仍精确匹配该项，不用latest。Auth新Revision="a2"、AccessDomain=kind+"/offline-2"并显式覆盖source-2，旧借用归还不要求已失效Read权利，旧binding保至真实归还。Update失败/Unknown仍不Attach新Editor；成功重新构造本次桥、epoch=old+1、新Request/IDs/完整EditorBinding。只有旧所有引用已真实退出才回收旧输入/task槽，不在容量已满时启动source-2。源切换取消不关闭共享service/session，关闭链和恢复链都使用旧Owner账，不新建Owner逃避Unknown。

第一轮有限正常检查：两个独立进程从Register前无模块对象开始，分别跑完完整构造/Bind→Attach→Execute→Show，核原DTO全字段及公开成员签名、simulation标记/圆线结果/接收键、owner容量/调用前登记、Close正常各回执与最后退出/删除条件。第二轮最多覆盖六个交错：构造/Bind失败；startup/Acquire/Execute迟到；源切换Update未知；推荐进行中关闭；Editor或Unbind失败但service另一分支继续清；共享session/service下关A仍Run/Query B（两个OwnSession=false、不同LayerId/专用recommender，只有创建Owner最后关总服务）。各例初次2s+一次2s恢复，保原Task与同ticket，清理失败不覆盖原业务错误；只推演规格，不声称运行。真实Adapter/WPF/资源/性能/现场后门保持。

共享反例的接入也不留隐含Owner：在同一个测试进程由creator HostOwner先登记两个HostFixture(hole/board-edge)、一个组合只读来源端口（按完整Frame.Asset分别路由两项，CoreResources共享总64MiB，借用仍独立）、合并两项MethodQualificationRule的ScriptBackend及`ServiceOptions(8,2,1,16,67108864,64,TaskScheduler.Default)`，创建service。Viewport creator持唯一root/session/串行层聚合账，完整Context预先包含SourceBinding(Primary,holeSource,null,"hole/frame-group",null)和SourceBinding(Secondary,boardSource,null,"board-edge/frame-group",null)，两来源虽同原bytes hash仍分别有SourceId/Frame资产ID，完整Sources/授权快照冻结。A/B私有HostOwner登记所借creator/root/session/service/来源，不对它们New/Close；各自Control用新的BindingId、OwnSession=false，Editor专用recommender及epoch/LayerId，合成SetLayers在creator的同一个聚合账串行提交。A关闭只确认A的Editor/Ticket、层/Control原scope/Unbind及操作borrow已归还，再由creator确认A引用责任退出，B仍能Execute/GetOperation和保B层；creator只有B也确认退出后才执行§8.10总session/root/service关闭。两binding不分享同一个Control实例；关闭A不清Sources或整个聚合表、不让A的Finally关闭creator组件。creator借用确认是显式reference/Task归还记录，非方法返回/超时；未确认时A槽仍留账。

共享测试仅creator创建Application/STA Dispatcher，A/B Window在同Dispatcher且HostOwner的OwnApplication/OwnDispatcher=false；独立§8.8/8.9这两个标记为true。借用Dispatcher不要求它退出才确认A自己的scope结束：creator明确接受A原UI任务/委托均撤及引用已归还后，A.TryRemove才可删A槽；creator的槽仍保存共享实例与运行中的B直到自己的最终退出。无确认不得删除A槽；不能把“必须等Dispatcher整体退出”的独立Host条件错误套到关A留B并产生互等。

## 9. 无 UI 最小调用

所有公开类型见附录A，参数/输入由两个consumer fixture准备，不取生产默认值。唯一装配顺序：宿主创建frames/mapper/resources/backend与ServiceOptions（显式TaskScheduler.Default）→new Features2DService(...)→以下调用→有限Close/恢复→Drained后Dispose service→宿主再释放依赖。构造具体类签名见A.3，不是已存在实现。

```csharp
public static async Task<Features2DResult> RunOneAsync(
    IFeatures2DService service, Features2DRequest request,
    IProgress<Features2DEvent>? progress, CancellationToken operationCancellation)
{
    ValidationReport validation = service.Validate(request);
    if (!validation.IsAccepted)
        throw new ArgumentException(validation.Errors[0].Code.ToString(), nameof(request));
    Task<Features2DResult> execution =
        service.ExecuteAsync(request, progress, operationCancellation);
    return await execution;
}
```

返回成功Task只代表已封口并归还，消费者仍检查每Work和Validity。宿主如只等一段时间，用execution.WaitAsync(waitToken)，取消等待不撤销operation；保留execution与service查状态。关闭调用CloseAsync(finiteTimeout,waitToken)，DrainUnknown保留Owner，必要RetryReleasesAsync再Close；只有Drained后Dispose，不能在未知分支离开await using误称已销毁。回调是可缺的投影，查询和结果权威。

H1孔/开口adapter用E2/显式PairFirst或中心、或E1圆组；板边/引脚adapter用Xld线段，独立Profile/观察角色，组合候选由各adapter自行做；同一个Core.Tests Exe通过两个--host模式装配内存帧、已知仿射mapper、受控后端/额度/时钟，不引用产品/Shell/数据库。Receipt.IsSimulation=true。A取消/B继续、版本双读/回退、关闭未知→native返回→释放失败→同Owner重试→唯一Faulted由受控闩锁完成，不需要Thread.Sleep猜时序。

### 9.1 两个无UI fixture的精确默认值（仅模拟）

以下固定值仅用于H1/BCL Exe复现§10语义，不进入生产Profile。所有AssetRef测试内容先以SHA256.HashData(UTF8原文或Frame原字节)生成lowercase hash；ID为对应fixture名，Revision="fixture-1"，不用64个0假内容。Support每row覆盖0..639，按A.1规范求hash。Frame为640×480/Mono8/stride640/generation1，全0字节；受控模拟backend返回下表观察，不将空图说成真实边。Identity用各host名+唯一case ID，AttemptId同该case，ConsumerAdapterId分别hole/board-edge。

| 对象 | hole fixture | board-edge fixture |
|---|---|---|
| Plan | MeasurePos+Circle；4个slot依序中心(240,340),(280,300),(240,260),(200,300)，V依序(0,1),(1,0),(0,−1),(−1,0)；SearchHalf=8、ProjectionHalf=2，role="reflection-edge"；group="circle-0"，SlotIds按原序，Observation.Edge | Xld+Line；window="line-0"，ComputeRect=(100,100,128,128)，InnerRect=(108,108,112,112)，role="outer-edge"；空Slots/Groups |
| Caliper/Xld | Sigma=1、Threshold=15、Positive/All/Bilinear、PairDiagnostics=false、MatchTolerancePx=.01；Xld=null | Caliper=null；Alpha=1、Low=10、High=20、Lines、Dist1=.5/Dist2=0 |
| 模拟原始观察 | 每slot恰一个边在原中心，幅值20，search position=0，Edges.NativeIndex=0，相邻距空；正序4点圆center=(240,300),r=40 | 一个parent/segment，点(120,110),(120,130),(120,150),(120,170),(120,190),(120,210)，三属性Provided/有限，唯一原映射；线Nr=1,Nc=0,Dist=120；演练未知原映射时另case |
| Fit | Standard/Iterations=3/ClippingFactor=2/MaxClosureDistance=1；Circle geometric | 同Fit；Line regression |
| Qualification | MinPoints=4/MinSpan=1/Rank=.001/缺slot=0/连续缺=0/MinCoverage=3/MaxGap=2/MaxAxisRatio=10/NearCircle=.01/MeanAbs=.1/MaxAbs=.2/Rms=.1/StabilityDelta=.001 | MinPoints=2/MinSpan=1/Rank=.001/缺slot=0/连续缺=0/角覆盖0/Gap=2π/Ratio10/NearCircle=.01/MeanAbs=.1/MaxAbs=.2/Rms=.1/StabilityDelta=.001 |
| 四挑战允许差 | center/endpoint=.1、radius/axis=.1、angle=.01、lineDist=.1 | 同左；模拟Fit按trial提供与基准一致模型是接口/归约夹具，真实fit数值资格在A1另验 |

两者Coordinates=Image/px/row/column/ImageRaster，映射/资格资产null，不借coordinate；Profile.Contract=0.2，RequiredLayout=Mono8，MinimumFeatureWidthPx=2、OriginalIndexTolerancePx=.000001，RequiredBackendVersion="sim-1"。真实Method/FitQualification测试资产内容按各自表全字段规范保存于fixture，不临时生成资格阈值。

受控TimeProvider初始UTC=2026-10-09T00:00:00Z，三个Deadline=初始+60s；Budget MaxSlots=256/MaxWindows=16/MaxFitGroups=16/MaxCandidatesPerWork=64/MaxContourPoints=4096/ResultBytes=4MiB/WorkingSet=64MiB/MaxConcurrentSlots=1。Options Queued=8/ConcurrentOperations=1/ConcurrentSlots=1/Retained=16/RetainedResultBytes=64MiB/EventCapacity=64/TaskScheduler.Default；并发T11以显式新Options.ConcurrentOperations=2测试。模拟资格Rule的Sigma/Alpha范围=.4..2、MinFeatureWidth=2、MaxComputeWidth/Height=640/480、Inset=8、MaxNativePoints=4096、FixedNativeBytes=1MiB/NativeBytesPerPixel=32/NativeBytesPerPoint=256，所有资源提供者上限64MiB；按A.3公式不足时预检拒而非改预算。示例Deadline推进由测试控制，不墙钟sleep。

原始E1/E2四边基数case另用一个slot中心(240,300)/V=(0,1)/half8，E1返回t=0,1,3,4，E2用同几何Plan.MeasurePairs+Primitive.None/空Groups，Caliper.PairDiagnostics分别false/true，返回Pairs(0,1),(3,4)，不强塞hole圆group。Target映射测试单独以已知仿射A'=2A、B'=B、单位mm/Right和测试资产/mapper演练逐点行为，不把此数值当真实标定。

模拟Extract/主Fit/四trial均受测试闩锁控制，返正常值/非法基数/native异常/超时/释放失败由case ID显式注入；不要按线程调度时序猜结果。端口方法本身仍遵守释放幂等和真实异步任务退出的契约。

### 9.2 A1：两个真实复用消费者的无UI接入映射

两个消费计划沿用§1.2的职责，不新增产品事实或生产Profile。消费者A是**特征工程工具**：无UI命令/Replay入口从宿主提供的孔/开口Frame、Support和Plan/Profile调用Core/ImageLib，查看有向边/边对及圆/椭圆支撑，参数建议只输出新Draft候选。消费者B是**无UI视觉项目**：从宿主提供的板边/引脚帧、有序窗口/拟合计划读取线段/原轮廓结果，再交宿主关联/量测；本模块不编号针序或判质量。二者均显式注入§7.1依赖，不要求Shell、数据库、WPF、设备连接、service locator或隐藏容器。

每个host分别拥有Frame/Support/Profile/Coordinate来源绑定、ConsumerAdapterId（A=hole，B=board-edge）、新OperationId/AttemptId、原Execute Task、操作取消源和有限关闭Owner；时间预算由同一次TimeProvider接纳规则计算。帧/坐标资产由原Owner发布，消费绑定精确引用而不取latest。A/B创建不同service/backend及专用recommender；可以明确借用同一个只读frame/coordinate/resource提供者，仍各次Acquire/Reserve独立租约和释放责任。下表并发取消还以同一共享service的A/B操作验证隔离；该service仅由创建宿主总关闭，消费A退出只能定向Wait/Retry自己的ID。

| 情景 | 特征工程工具A | 无UI视觉项目B | Owner/结果断言与测试定位 |
|---|---|---|---|
| 正常执行 | 校验后保存原Task，消费边/边对及几何候选，保留Profile/Method引用 | 同样路径读取线/轮廓与原索引，交自身下游 | 两者用同一个Validate/Execute实现，Result只含托管值；T03～08、T15，真实样本另验 |
| 空候选/支撑不足/歧义 | 展示原work错误与全部支撑，建议不能假推荐 | 保留未观察/歧义，不补边或填0送量测 | 状态/分母/原索引不被消费层洗成PASS；T02～07 |
| A取消、B继续 | Cancel(A-id)或A原operation token仅取消A；等待原Task实际归还 | B原Task、源、lease与结果不变，继续完成 | 独立service与共享service两种接法各验证；A不能调用共享Close；T11/T12 |
| 源切换 | 封新派发、撤旧展示/建议采用资格，定向取消并排空A旧操作；新源新ID | 同样保B旧原Task直到归还，再接精确新资产/坐标 | 各host自增输入代，Generation仍用Frame.Generation，不能假造资产hash；T10/T13/T18 |
| 迟到结果/旧Profile | 原结果保为旧输入只读证据，禁止采用到新Draft | 不传入新板/新目标关联或质量流程 | 比较OperationId、Frame完整引用/Generation、Profile hash及host输入代；拒投影不丢释放账；T10/T18 |
| 有限关闭到期 | 独立service用Close，共享service仅Wait自己的IDs；保持原Task/Owner | 按相同边界关闭自己的操作，不清A或共享源 | DrainUnknown不Dispose service、不退出Owner；给宿主恢复查询入口，取消等待只结束观察；T09～13 |
| 释放失败/晚到恢复 | 对自己ID RetryReleasesAsync；原释放pending只等待 | 各自保原对象，同样有限恢复 | 全部释放完成后才交唯一terminal结果；恢复仍Faulted/F2D-013；T12/T13 |

无UI入口由宿主长期关闭管理器持有原服务/Task/lease责任，DrainUnknown只返回待处理ID及原错误，不自行启动失联后台重试。实际Frame/标定/目标Profile/Method资格与Golden取各消费者原Owner的获准输入；缺少客户资料只阻对应真实用途，不编生产默认。既有H1 `--host hole/board-edge`只使用§9.1夹具验证软件协议，不能冒充A1两客户消费验证；真实A1测试复用§1.3的ImageLib.Tests Exe，通过其两个host入口分别给定已获准输入及相同断言，不新增同义harness。纯Core接收状态不因此重审或提升A1资格。

这里的关闭管理器具体就是§8.7的私有HostOwner（不是待实现者自行设计的第三服务）：无UI hole/board-edge分别以Register→New HostFixture(相应kind/固定Clock)→New Features2DService(三个明确源、ScriptBackend、clock、§9.1 Options)→可选专用Recommender→Start("execute",ExecuteAsync)→Observe/RecordResult完成正常输出；finally先关闭接纳并按§8.10第1/2直调ID/5/6源分支执行有限关闭。没有Application/Window/Dispatcher/viewport字段，WPF步骤标NotCreated并跳过，非Drained伪回执；仅实际service/原任务/源borrow确认后TryRemove。Unknown保进程槽与有界Console诊断/显式RetryClose入口（不后台循环、不把返回main当已归还）；两入口各自输入/Task/取消Owner不依赖产品Shell。两个WPF全字段入口沿§8.8/8.9，但无UI项目无需引用它们的程序集。

## 10. 具体样例与预期

数值仅合成契约样例，不是HALCON精度/客户阈值。

| 输入/触发 | 必须输出/拒绝 |
|---|---|
| E1 t=0,1,3,4与4幅值；E2对(0,1)/(3,4) | 4边/3相邻1/2/1；2对/对内1/1/对间2，原索引保全 |
| E2空，无diagnostic计划 | NoCandidate+Empty pairs，不断言无物理边、不临时调用E1 |
| 一个slot跨无效岛，另一个完整 | 无效项Rejected/F2D-004且Extract未调用；另一项继续，全计划ID保留 |
| XLD重复坐标、多parent/闭环 | 不唯一映射Unknown，不跨parent拼轮廓，不nearest配原索引 |
| 线(0,0),(0,2),(0,4) | 可拟合Nr=1,Nc=0,Dist=0，不能以二维rank=0拒真线 |
| h=.010/.011短圆弧三点 | 零残差但r差约4.545，依稳定性/覆盖资格拒有效圆 |
| 椭圆Radius2=0或a≈b | 前者InvalidGeometry；后者几何独立资格，轴角NotApplicable |
| 同ID同digest/不同Threshold | 前者只一次backend，deadline不延长；后者F2D-016，原执行不变 |
| native未返且Close到期 | DrainUnknown，Execute pending，Frame/job仍持有 |
| job释放未返，用户连续Retry | 仅同一释放任务在途，不启动第二Dispose；失败后才允许重试 |
| 来源在封口前撤销 | F2D-018，无有效迟到结果；按原Owner排空归还，不换latest |
| 预算剩余放不下完整contour | 不复制半条/抽稀，Truncated并留完整已复制原证据和停止原因 |
| 建议0匹配/缺验证/多解/全部过门失败 | Abstained，无推荐无loss补0，BaseProfile不变 |
| UI换Epoch后旧结果到达/Run撤销 | 旧回执不覆盖当前；只禁新Run，当前Cancel/排空恢复可用 |

## 11. 唯一测试入口与断言

Core.Tests为BCL Exe：固定TimeProvider、可控制TaskCompletionSource闩锁、确定性assert与故障注入，无xUnit/NUnit/MSTest包。入口默认跑全部C1/H1适用断言；任一失败/未完成/必需项跳过返回非零并列T编号；仅全部完成为0。固定预算：每个T编号下的单独case从其开始起最多10秒实际wall elapsed，整个测试suite（含两个H1 adapter场景/清理）最多120秒，外部执行器从启动进程起最多180秒（含dotnet run启动/构建）。case/suite均用独立TimeProvider.System.GetTimestamp/GetElapsedTime或Stopwatch作wall watchdog，不能用被测虚拟TimeProvider代替；各自等于上限即失败且记录case ID/未完成Task/Owner。虚拟时钟推进只验证算法deadline/租约/排队，不消费或重置wall预算；外层180秒超时返回非零并保留输出，不能进程被终止仍报0。harness只模拟无硬件，可结束失败进程；此规则不授生产native强杀/释放许可。测试模拟端口必须在10/120秒内完成或明确故障退出，suite不能等待未知native无限挂起。dotnet test不会执行此Exe。

```powershell
dotnet build src/Modules/features-2d/Asun.Modules.Features2D.Core/Asun.Modules.Features2D.Core.csproj -c Release
dotnet run --project tests/Modules/features-2d/Asun.Modules.Features2D.Core.Tests/Asun.Modules.Features2D.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/features-2d/Asun.Modules.Features2D.Core.Tests/Asun.Modules.Features2D.Core.Tests.csproj -c Release -- --host hole
dotnet run --project tests/Modules/features-2d/Asun.Modules.Features2D.Core.Tests/Asun.Modules.Features2D.Core.Tests.csproj -c Release -- --host board-edge
```

以上为后续实现命令，本轮不创建工程/执行产品编译。A1绑定其同名Tests Exe（net10.0-windows、引用A1及BCL）以dotnet run --project该唯一csproj -c Release执行真实route样本；U1 TestHost为WPF Exe，以dotnet run --project该唯一csproj -c Release打开真实1920×1080验收，不能用Core harness代替。

补充消费入口仍用这些唯一工程：A1 Tests在原命令后分别传`-- --host hole`、`-- --host board-edge`，加载各自获准输入/资格（§9.2）；U1 TestHost分别传`-- --host engineering`、`-- --host embedding`，独立进程串行运行§8.6。没有真实资料时对应A1场景保持未验，不用§9.1模拟数据报通过。WPF恢复等待均为有限观察，未排空报告失败/未验并保留原Owner，不借Core的10秒模拟case预算强杀生产native。

| ID/切片 | 可判定断言 |
|---|---|
| T01/C1a | default/空ID/重复ID/非法enum/非有限/负长/stride溢出拒绝，backend调用数0；A.1.1固定F2D-D01全部hex=1046字节/hash硬断言、严格UTF8代理项/容量边界、−0与Deadline排除规则 |
| T02/C1a,b | 版本/hash/布局/单位不符F2D-014/005；租约source当前性不能取latest |
| T03/C1b,A1 | E1 N/N−1、符号/V反向与FirstLast，Exhaustive正确 |
| T04/C1b,A1 | E2 N/N/max(N−1,0)，空pair含义、diagnostic独立索引、显式侧选择不猜 |
| T05/C1b,A1 | 无效岛/边距/中心取整/计算窗与内区、RequiredRuns拒受影响work；measure无domain隔离 |
| T06/C1a,A1 | 三属性基数/角轴、闭环反向唯一映射/重复Unknown、多parent隔离、RGB等亮异色 |
| T07/C1a,A1 | 线rank、点不足/短弧/混源/零轴/近圆、4挑战独立原点，低残差不掩敏感性 |
| T08/C1b,A1 | Map每点同序/长度/单位、非等距与域外无效；Image不借coordinate |
| T09/C1a,b | legacy route拒绝不fallback；重复同digest只一次/不同内容冲突 |
| T10/C1b | 队列取消/native迟到/deadline封口竞争、§4.1.1墙钟回拨/前跳与来源当前性反例；冻结remaining不重算、DrainUnknown非终态、Frame未提前归还 |
| T11/C1b,H1 | A/B独立Profile/取消/代次/结果；服务不Dispose宿主共享依赖 |
| T12/C1b | 额度→frame→coordinate→job获取、逆序释放；失败不释放下层；未返不重复Dispose；成功项不重试，恢复仍Faulted |
| T13/C1b | 部分Open返回失败Job不遗失；RequireCurrent撤销拒封口；回调抛异常/阻塞/重入不阻排空 |
| T14/H1 | 两Console consumer adapter独立只引用Core，模拟标记、全错误/候选语义不变 |
| T15/A1 | 真实route普通/鲁棒各Golden/Replay、弱边/颜色/裁边/噪声与偏移，结构/数值差异按资格 |
| T16/U1（W1装配） | §7.2/§8.5～8.6/A.5双STA入口；三语/键盘/UIA/DPI/主题/树↔影像↔属性/图表、源切换/旧输入、取消/窗口关闭/建议子Task、Epoch迟到/撤权、DetachTicket/桥Unbind恢复、OwnSession=false关闭A不影响B |
| T17/C1b | Close停接纳、0观察/重复Close/Retry、Dispose未Drained抛且保Owner，新实例不复活旧ID |
| T18/C1c | checked组合预算、固定顺序、校准验证不重叠、唯一图匹配/多解惩罚、并列Key确定 |
| T19/C1c | 正样本0匹配无假loss/明确负样本只检extra、真值独立、建议取消先保Owner排空、Basehash变更拒采用 |
| T20/C1b,A1 | 点/候选/结果原子上限，native超资格峰值Faulted，未知峰值不填0 |
| T21/C1b,H1,A1 | 改版同输入双读新attempt/回退旧包、在途不热换/旧事实不覆盖 |
| T22/C1b,A1 | 满队列/回执/事件、活跃不逐出、GetOperation权威、长稳资源无无界增长 |

**T10的固定时间反例（每项独立case，wall预算仍10秒）。** 虚拟TimeProvider必须允许分别控制GetUtcNow与timestamp/timers，不把改UTC同时当timestamp推进；初始u0=2026-10-09T00:00:00Z/t0=0，frequency=1000Hz，三个Deadline=u0+10秒。
- 接纳后timestamp=9000，UTC回拨至u0−1小时：仍有1秒执行时间，currentnessUtc≥u0+9秒；timestamp=10000时不论UTC仍回拨，都请求TimedOut/Draining；native闩锁未释放前Execute pending、Frame未归还，解除闩锁后最终TimedOut（若无来源/释放故障）。
- 接纳后timestamp=1000，UTC前跳至u0+1小时：执行remaining仍10秒、elapsed仍1秒；受控lease.RequireCurrent必须发现传入UTC已越借用期，记录F2D-018并走Faulted排空，不声称execution deadline变成1秒。若测试只隔离纯执行时钟，无lease参与，则在timestamp=9999不TimedOut、10000才TimedOut。
- deadline=u0/过去、默认/Min/Max/非UTC、remaining>24h，均在接纳/Reserve/Acquire/Open前拒绝，副作用计数0；合法期限变换而同ID重复不重置t0/remaining。
- Clock.GetElapsedTime负值/回退，F2D-015关闭有效结果并保留Owner排空；不把墙钟倒退当负duration，也不能为过测试改回系统UTC。

测试输入/预期/上限随fixture固定于唯一工程，正式视觉资格绑定真实Frame/Profile/方法版本/hash，不以合成样本冒充现场。

## 12. Benchmark方法与可观测性

BenchmarkProfile公共时钟/样本/冷暖/预热/失败删失/P50/P95/P99口径唯一引用[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，本页只定义本模块负载/测点。目标由消费者Profile采纳；没目标NotEvaluated，没测Unmeasured，不造达标毫秒值。

Core BCL Exe同工程`--benchmark`模式：Mono8 640×480；slot=1/32/256；window=1×256²或4×128²；受控返回点=16/256/4096；并发1/2；normal/empty/truncated/cancel/release-failure均保留。每组Profile冻结输入hash/backend模拟标志、预热数/测量数/最低样本数、有限deadline、结果/工作集上限与阈值来源；参数缺失诊断或拒评，不自动按CPU调整。该模式只测Core调度/复制/归约，非native吞吐。

A1真实基准按消费者实际最大帧与代表样本（可包含8192²研究规模）、布局/stride/slot半长、window内外域、原轮廓/属性/分段/映射/四挑战点数、显式并发分组。同样本全帧/局部比较固定输出域/真值与拒识，不能缩图/抽稀暗改。正确性/误接受误拒/拒识覆盖/性能/资源分别判，未测路线不选“最快”。

测点：Validate、DescribeSupport/包含检查、排队、额度/frame/coordinate/job获取、逐work提取/属性复制/分段/原映射、逐点Map、资格、主fit/四挑战、结果复制封口、native退出、各lease释放。Duration用TimeProvider单调timestamp，UTC只关联；E2E由Accepted至ResourcesReleased，取消另记至真实native结束/全部归还。DrainUnknown/释放失败/超时单列，不能静默删掉判通过。

资源计数：native/托管峰值、job/measure/iconic、活动frame/coordinate/额度、队列/事件/保留账、逻辑结果字节；native未知null+NotProvided，不填0。Receipt最小记录输入/Profile/Method/坐标/backend/运行时版本/hash、模拟标志、时序/错误/终态释放。日志用稳定引用不自动保存客户原图，采样与持久化归宿主。

### 12.1 性能结果判法与目标 Owner

消费者采用的BenchmarkProfile须显式给目标来源/修订、负载域、冷/热、有效样本下限、有限case期限、P50/P95/P99上限、峰值资源上限及允许失败率；不另建本模块性能DTO或凭机器速度自动调值。正确性与资源释放先满足，才评价性能，模拟数据只对Core协议负载有效。native每方法资格的资源上界仍由A1实现/资格Owner用实测建立；客户节拍/精度由消费产品Owner采纳，二者不是同一个门。

| 观察 | 确定结果 | Owner/影响 |
|---|---|---|
| 尚未执行测量 | Unmeasured，不能产生分位或峰值 | 本模块实施/验证Owner；不退回既有Core规格接收 |
| 已测但缺目标、来源或最低有效样本 | NotEvaluated，保测量数据及原因，不报达标 | 消费产品Owner补采用Profile；样本不足由验证Owner补测 |
| 单case期限耗尽、native/释放Unknown、必需项未测或错误 | 该case失败/删失按GOV010保分母，不删快慢样本凑PASS | 本模块/实际源Owner保原任务，恢复后仍保原失败事实 |
| 全部必要准确性/真值/拒识/释放门满足、测量有效且每项采纳上限通过 | 只对该Profile和版本报告性能通过 | 本模块验证Owner；不扩到另一路线/尺寸/客户 |
| 任一必需指标超限或失败率超采纳限 | 性能失败，标超项/输入/阶段/恢复责任 | 本模块实现Owner修受影响热点，不能改算法/抽稀/缩图掩盖 |
| native峰值不可观测或真实UI可见未确认 | 对应资源/显示指标NotEvaluated；若是必要指标则验收不通过 | A1/native或viewport/WPF Owner；不能填0或用提交耗时代替 |

有限比较需保持同输入、输出域/支撑、方法版本与正确性门；取消从请求意图到native退出、再到全部归还分别统计。建议模式额外测候选/样本预检→全组合→评价→最后子operation资源归还，UI模式测执行结果→投影提交→真实可见及撤显示/归还，不只测快速按钮返回。未确认归还不能记完成E2E；原服务Task pending仍属未收敛。§11既有有限wall watchdog是软件测试预算，不是客户节拍。

## 13. 分层准入、发布与回退

C1a→C1b→C1c使用同Core工程按片接收，不造新独立模块；H1同BCL Exe双consumer接入。A1按E1/E2/C1/C2/F1/F2/F3及Standard/Robust独立真实资格接收，C#具体歧义仅阻相关调用，不重复算子能力/依赖审查；U1真实WPF另门。平台映射/Owner、客户真实Profile/标定/Golden/计量/性能/HIL/FAT/SAT是受影响产品门，不阻无产品写入Core规格准备。

独立包为Core及可选ImageLib/UI DLL、契约/方法/依赖版本与已有Host样例/回退说明，不提前堆无消费者交付包、不带产品私表/SDK/工艺。模块不写数据库/文件/草稿，不序列化native。Replay需要宿主持有精确输入/support/坐标/资格/Profile/backend hash与receipt；存失败不改计算状态，重启新ID重新取同版来源，不能缓存几何补造观察。新旧Replay/Shadow并列，新attempt、旧事实只读；回退选旧包，在途固定旧版本不热换，保留诊断。

第二消费者门证明独立无Shell运行、错误/歧义/缺口/截断语义保持、参数/取消/坐标/语言不串、独立升级无需第一消费者私表/页面。H1模拟证明接入结构，不能声称两个真实消费者/生产已验收。

## 14. DZ-XVision 可迁移经验与通用回放验收

本节只吸收快照中能够定位到源码的通用观察、参数语义和异常处理方式。快照来源为 `../../references/project-snapshots/DZ-XVision/20261004`，捕获日期 `2026-10-04`，原项目为 .NET Framework 4.7.2 WinForms，引用旧版 AsunImage 24.11 与 DevExpress 24.1；原始文件和树 hash 见 [`README.md`](../../references/project-snapshots/DZ-XVision/20261004/README.md) 与 [`source-manifest.json`](../../references/project-snapshots/DZ-XVision/20261004/source-manifest.json)。以下内容不把旧实现、默认值或页面流程提升为本平台生产契约。

本节的直接源码依据为：`../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/Tools/ToolBlob.cs`、`ToolShapeModel.cs`、`ToolMeasureLine.cs`，以及 `../../references/project-snapshots/DZ-XVision/20261004/original/ImageMeasure/ImageMeasure/Class/MeasureParams.cs`、`C_Measure.cs`、`line/Line.cs`、`line/LineResults.cs`、`ClassSerialize.cs` 和 `../../references/project-snapshots/DZ-XVision/20261004/original/HVision/TileImage.cs`。其中控件 DLL 的内部实现不在快照内，未将其未见字段当作事实。

### 14.1 可确认的宿主边界

- `ToolBlob`、`ToolShapeModel` 和 `ToolMeasureLine` 都由宿主提供测试图像，复制到控件后再显示；关闭或重载时显式清理 `HObject`，控件分别通过 `Control_Ini`/`Control_Dispose` 建立和释放资源。可迁移结论是：核心服务必须接收不可变帧引用，适配器拥有原生对象，关闭、取消和重配置都要经过同一排空协议。
- 三个工具都把 ROI 控件中的 `ROI_Data` 区域数组传给算法或图像预处理；区域可以为空或包含多个元素。平台输入必须携带有效域、边界截断和采样包络证据，不能只保存一个 UI ROI 名称。
- Blob 和测量线可选择 `SModel`/`NModel` 作为定位来源，形状模型工具以 `SModel` 名称保存和读取。这个名称和工具枚举属于旧产品编排；平台只接受调用方解析后的位姿、坐标上下文和 revision，不读取工具列表或私有全局状态。
- 预处理图像通过独立的 `ImageEff` 工具读取、生成并重新绑定到控件。平台应把预处理结果作为带 hash 的新帧/新 attempt 输入；失败时保留原始帧，不在模块内偷偷更换图像。
- `HVision/TileImage.cs` 按图像宽高、间隙和行列偏移拼接多帧，并在较新的分组入口中拒绝空数组、空图像、负间隙和非正尺寸；其中产品行输入与工装总览显示被明确区分。平台若接收拼接帧，必须保存每个源帧 ID、偏移、间隙和回映射，不能把总览拼图当作算法原图或丢失 tile 坐标。
- 保存/读取按工具名和目录组织，测量类另以二进制序列化保存 `measureList`。这些都是旧宿主的持久化实现；平台结果只能保存 schema、Profile、输入和标定引用，不能序列化 `HObject`、`HTuple`、Metrology 句柄或窗口状态。

### 14.2 Blob：可迁移观察与参数候选

快照能确认 Blob 工具的 ROI、定位来源、可选预处理图像、按名称保存/读取和控件资源生命周期；`Control_Blob` 的内部算法源码不在快照中，因此灰度阈值、连通域和形态学参数没有可核对的旧值。以下保留Blob历史迁移字段，不属于features-2d附录A或本次实现范围，由对应模块唯一指导决定采纳：

| 候选字段 | 单位/取值语义 | 来源与约束 |
|---|---|---|
| `ThresholdMode`、`Low`、`High` | 灰度值；单阈值或上下阈值 | 候选，不能从旧 UI 推断默认值；需记录极性/动态范围 |
| `Polarity` | `bright`、`dark` 或明确的双向模式 | 候选；失败后不得自动切换极性 |
| `Connectivity` | 4/8 邻域 | 候选；必须固定并写入回放 Profile |
| `Morphology` | 操作序列及像素半径/迭代次数 | 候选；无操作也要显式记录，禁止隐式去噪 |
| `FeatureFilters` | 面积 `px²`、周长 `px`、质心/外接框 `px`、圆度/长宽比无量纲 | 候选输出过滤，不是质量判定；保留原始候选和排除原因 |
| `MaxCandidates`、`Ordering` | 数量上限；稳定排序键 | 宿主资源预算；达到上限返回 `Truncated`，不补零或取第一个 |

通用输出至少应包含候选稳定 ID、原始连通域索引、区域/边界截断、面积、周长、质心、外接框、可选圆度/轴向、极性、阈值来源、支撑统计和排除原因。空 ROI、全图 ROI、全前景、全背景、边界截断、噪声孤岛、相邻区域合并和候选超限必须分别回放；`NoCandidate`、`InsufficientSupport`、`Ambiguous` 与 `Truncated` 不得映射为产品缺陷或 `Pass/Fail`。

### 14.3 形状/特征匹配：可迁移观察与参数候选

`ToolShapeModel` 明确使用单个 ROI 模式初始化 `Control_Aligment_ScaleShape`，以 `SModel` 名称保存/读取模型，并可在同一 ROI 上应用 `ImageEff` 预处理。快照没有该控件的匹配实现和参数公开定义，以下仅是模板匹配领域历史迁移候选，非本模块Profile/API；接入由对应模块Owner处理：

- 模板/轮廓来源及 revision、搜索 ROI 和有效域；模板不可用、hash 不符或 ROI 越界在执行前拒绝。
- 角度范围（明确弧度或角度）、尺度范围（无量纲）、最小分数、最大实例数、候选排序和遮挡/缺口政策；旧项目未提供可迁移默认值。
- 每个候选的平移、旋转、尺度、分数、支撑/遮挡比例、模板版本、搜索域和原始候选序号。分数只表示匹配证据，不是置信度、质量等级或放行依据。
- 无候选、低分候选、多候选近似并列、模板局部遮挡、尺度/角度超出、重复模板实例和候选超限必须保留候选集合与停止原因；合法并列返回 `Ambiguous`，不得按分数或坐标静默选一个。

形状模型与 Blob 的产品定位来源、工具名称、页面顺序和保存目录不能迁入核心；调用方把定位结果转换为 `CoordinateContext` 或独立观察角色后再执行。

### 14.4 测量线：旧 Metrology 实现的参数、结果和资源观察

`ImageMeasure/Class/MeasureParams.cs`、`C_Measure.cs`、`line/Line.cs` 和 `line/LineResults.cs` 可确认旧项目以 Metrology 实现测量线。此处只保留历史参数和结果结构作为迁移研究，不定义 features-2d 当前执行路线；legacy Metrology请求拒F2D-002，对象/实例量测归独立metrology模块，不因封装能力限制而暂缓。`ToolMeasureLine` 在加载时把相机 `PixelSize` 传给旧控件；以下参数都是像素或明确无量纲，旧 UI 数值只作为候选/边界观察，不是平台生产默认：

| 参数 | 单位/枚举 | 快照观察 |
|---|---|---|
| `RecWidth`、`RecHeight` | 测量矩形半宽/半长，`px`，实现注释要求不小于 1 | 作为卡尺/Metrology 搜索包络；必须记录有效域和越界 |
| `MeasureSigma`、`MeasureThreshold` | 平滑 sigma `px`；最小边缘幅值（灰度响应单位） | 旧类默认字段为 `1`、`15`，仅作来源记录；Profile 必须显式提供 |
| `MeasureTransition` | `positive`、`negative`、`all`、`uniform` | 极性不可在失败后自动改写 |
| `measureRecType`、`MeasureDistance`、`NumMeasures` | `Distance` 时中心距 `px`；`Number` 时卡尺数量 | 两条路线互斥；结果基数和计划分母都要保留 |
| `MinScore`、`DistanceThreshold` | 分数无量纲；离群距离 `px` | 分数不是质量概率；离群点必须单独输出 |
| `MeasureInterpolation`、`MaxNumIterations` | `bilinear`/`nearest_neighbor`/`bicubic`；迭代次数 | 作为实现参数写入 Profile，不从 UI 状态猜测 |
| `NumInstances`、`MeasureSelect` | 最大实例数；`first`/`last`/`all` | 有限搜索语义，不能提升为全集 |
| `ReferenceSystem`、对齐 `(X,Y,Angle)` | `[row, column, angle]`；图像坐标 `px` 与角度单位必须声明 | 重复设置参考系可能改变结果；每次执行绑定 immutable revision |

旧控件还观察到 UI 对 `MeasureDistance` 上限 500、`NumMeasures` 上限 5000，重置示例使用 sigma=1、矩形长度 15、离群阈值 5、`positive`、`first`、数量 100。这些值只作为旧现场调参线索，不能直接成为平台默认或验收阈值。

`LineResults` 的可迁移结果字段包括：起点/终点/中点、线长、相对 X/Y 轴角度、直线度、全部采样点、拟合点、离群点，以及测量矩形、结果轮廓、交叉标记和离群标记的证据引用。作为历史 Metrology 研究，空图像返回空输入错误；无 Metrology 参数返回无候选；异常点按 `DistanceThreshold` 分组后重新计算直线度。本模块不执行这些Metrology调用。`PixelSize` 必须由宿主以标定单位/px（例如 mm/px）提供并绑定 revision，不能使用旧字段的隐含单位。平台必须同时保留 image/world 坐标、原始行列顺序和点索引，避免旧实现中 `row`/`column` 与 `X`/`Y` 互换造成不可追溯结果。

资源方面，旧实现会在重建模型前清除 Metrology 句柄，在刷新结果前清理旧 `HObject`，批量删除测量时逐项清理结果对象；但 `SetImage` 直接保存传入图像引用，二进制序列化对象还可能携带原生字段。平台适配器必须明确借用/拥有关系，成功、取消、异常和重配置均在 native 返回后释放；原生句柄不进入 Contract、缓存或回放文件。

### 14.5 快照驱动的通用 Replay 断言

本表为对应Blob/匹配/Metrology Owner的历史迁移思路，不是features-2d新增执行能力或Core门；本模块断言唯一见§11。历史回放夹具应保存帧/有效域 hash、观察角色、Profile hash、标定/像素尺寸、模块和适配器版本、候选上限以及原始索引。每个结果都要保留 `attemptId`、状态、停止原因、支持证据、参数来源和资源释放确认。最低断言如下：

| 夹具 | 必须断言 |
|---|---|
| Blob 空 ROI、全背景、全前景、边界截断、噪声孤岛、相邻连通域 | Validate/Execute 状态可区分；面积/周长/框的单位和索引稳定；候选上限返回 `Truncated`，不自动调阈值或合并结果 |
| Blob 双极性和重复执行 | 极性写入结果；相同输入/Profile 结果结构稳定；切换极性只能生成新 attempt |
| 形状模板缺失、ROI 越界、遮挡、低分、多候选并列、实例超限 | 缺失/无候选/支撑不足/歧义/截断原因可追踪；候选不被分数排序静默压成一个 |
| 测量线单边、反向边、零对、少于最小支撑、超出矩形、离群点 | `measureRecType` 的计划分母和实际基数一致；端点方向、极性、采样点、拟合/离群集合可回放 |
| 测量线近共线/退化包络、非有限坐标、像素尺寸缺失、参考系重复设置 | 在 Validate 或拟合资格检查阶段返回 `InvalidGeometry`/`DegenerateFit`/`F2D-004`，不生成零长度或默认单位结果 |
| 取消、超时、原生迟到、第二 operation 并发 | 停止派发、原生返回、资源释放和终态顺序可观察；排空未知期间只返回 `DrainUnknown` 等待观察、保持未决并隔离资源；旧 generation 不覆盖新结果，A 的取消不影响 B |
| Metrology历史边界 | 本模块legacy请求F2D-002，不创建旧handle或fallback；对象量测由独立模块接收 |
| 旧二进制配置、版本/Hash 不符、回退 | 拒绝携带原生句柄或不匹配版本；同一输入生成新 attempt，旧结果只读并可比较，回退不改写历史 |

这些断言只验证视觉证据和资源协议；候选关联、对象身份、尺寸/角度的业务定义、缺陷分类、质量放行和设备动作仍由消费者负责。完成回放断言不等于 HALCON、计量、性能、HIL 或现场生产验收。

## 15. 参考与未决项

- [`PKG-021_Features2D.md`](../../shared-modules/packages/PKG-021_Features2D.md)：包职责、消费者和 P2 限制。
- [`DEV-VIS-025`](../../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md)：边缘、边对、XLD、拟合、支撑、取消和验收方法。
- [`DEV-VIS-020`](<../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>)：Vision Contract 与 `ImageLibDotNet` 边界。
- [`DEV-VIS-021`](../../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md)：HALCON 优先路线和替代条件。
- [`measure_pos`](../../../halcon算子手册/operators/measure_pos.html)、[`measure_pairs`](../../../halcon算子手册/operators/measure_pairs.html)、[`edges_sub_pix`](../../../halcon算子手册/operators/edges_sub_pix.html)、[`fit_circle_contour_xld`](../../../halcon算子手册/operators/fit_circle_contour_xld.html)、[`fit_ellipse_contour_xld`](../../../halcon算子手册/operators/fit_ellipse_contour_xld.html)、[`apply_metrology_model`](../../../halcon算子手册/operators/apply_metrology_model.html)、[`get_metrology_object_result`](../../../halcon算子手册/operators/get_metrology_object_result.html)：HALCON 26.05 本地算子页面；仅用于路线和参数语义核对。
- [`CONTRACT-CANDIDATES`](../../13-contract-candidates/CONTRACT-CANDIDATES.md)：C-02/03/04 几何、支持、来源和结果语义候选。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_Aligment2D_ShapeModel\开发文档.md`、`ROI\ROI开发文档.md`：只读借鉴了外部输入、异步/取消、UI 与资源释放的组织方式；其中旧版本参数、重试和句柄实现不自动迁入本模块。
- `../../references/project-snapshots/AsunControl/20261004/original/.github\copilot-instructions.md`：只读保留旧命名记录，当前固定ImageLibDotNet.cv2；只有实际类型/重载/封送歧义才查公共签名。

### 15.1 本轮来源定向复核（2026-10-06）

- `H:\docs\40-development\40-vision\2D检测器开发指导.md`（SHA-256 `84435fbe446ba21dccace13d8bdc08cb35fa8b38eeb424e69b529082f4272d9c`）：复核了边缘/轮廓候选、支撑与证据、坐标映射、取消排空和资源边界。其可跨模块的“候选生成、量测/拟合、证据保存、宿主判定分层”以及不可观测/部分结果/跨帧来源约束，已由本页第 1、3、5、6、10、12、16 节覆盖，本轮不新增重复契约。AOI 检测器编排、配方/权限/质量放行、跨 FOV 检查项归集、产品存储和客户阈值不属于本模块；来源中的旧 HALCON/API 结论也不替代本项目 HALCON 26.05 页面和 `ImageLibDotNet` 公共签名核对。
- `H:\docs\40-development\41-vision-platform\04-recognition\极性姿态与方向识别开发指导.md`（SHA-256 `b4b71569d07939b36f6cfaebdb08cf82a90cf45826abb8e9f919d09bd923eeaa`）：复核了不可观测、对称/镜像歧义、证据冲突、独立回放和资源排空语义。其极性/姿态特征融合、方向等价组、颜色/文字/学习策略、质量映射和生产判定属于 `PosePolarity` 领域；本模块只保留与现有 `CandidateValidity`、`SupportEvidence`、`FitEvidence` 和拒判/排空语义一致的边界，不把 `score`、残差或域内 confidence 迁移为概率或测量不确定度，也不新增融合权重或业务状态。

上述结论仅指2026-10-06两份H:\docs来源的定向复核；本次2026-10-09研究和10-10接续修订见§15.2，不重算或覆盖来源hash。

后续规格门：C1a/C1b/C1c已获主控规格接收，其余切片内容接收及平台Contract/领域Owner映射采纳仍按原门处理。外部验证门：A1真实调用/方法资格/释放与Golden、客户Profile/坐标适用域/计量/性能、U1真实WPF及产品现场。未决只阻相关片，不用虚构数值关闭，也不以平台合同未采纳阻无产品写入Core。跨文件DEV-VIS-025/架构旧能力与公共签名门交主控处理，本轮不改共享文件。

### 15.2 本次已保留研究与实际落点（2026-10-09；10-10复用）

HALCON26.05.0.0本地官方页面已实际读取（本次接续不重复全审）：
[gen_measure_rectangle2](../../../halcon算子手册/operators/gen_measure_rectangle2.html)、
[measure_pos](../../../halcon算子手册/operators/measure_pos.html)、
[measure_pairs](../../../halcon算子手册/operators/measure_pairs.html)、
[close_measure](../../../halcon算子手册/operators/close_measure.html)、
[edges_sub_pix](../../../halcon算子手册/operators/edges_sub_pix.html)、
[edges_color_sub_pix](../../../halcon算子手册/operators/edges_color_sub_pix.html)、
[get_contour_xld](../../../halcon算子手册/operators/get_contour_xld.html)、
[query_contour_attribs_xld](../../../halcon算子手册/operators/query_contour_attribs_xld.html)、
[get_contour_attrib_xld](../../../halcon算子手册/operators/get_contour_attrib_xld.html)、
[segment_contours_xld](../../../halcon算子手册/operators/segment_contours_xld.html)、
[get_contour_global_attrib_xld](../../../halcon算子手册/operators/get_contour_global_attrib_xld.html)、
[fit_line_contour_xld](../../../halcon算子手册/operators/fit_line_contour_xld.html)、
[fit_circle_contour_xld](../../../halcon算子手册/operators/fit_circle_contour_xld.html)、
[fit_ellipse_contour_xld](../../../halcon算子手册/operators/fit_ellipse_contour_xld.html)、
[dist_ellipse_contour_xld](../../../halcon算子手册/operators/dist_ellipse_contour_xld.html)、
[gen_contour_polygon_xld](../../../halcon算子手册/operators/gen_contour_polygon_xld.html)、
[crop_domain](../../../halcon算子手册/operators/crop_domain.html)、
[reduce_domain](../../../halcon算子手册/operators/reduce_domain.html)、
[lines_gauss](../../../halcon算子手册/operators/lines_gauss.html)。
采纳为§2固定方法，§3卡尺major axis/中心取整/Sigma/域/插值与XLD三属性，§6分段最低长度/点数、fit退化/ignored参数与正交距离，§12局部原分辨率/资源测点。reentrant不等于可共享可变句柄/取消ACK已完成；官方页面不是本项目真实准确率/性能证据。

DevExpress25.2官方页已通过浏览器读取（本机固定25.2.3，不下载替换）：
[DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、
[TreeListControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListControl?v=25.2)、
[TreeListView](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListView?v=25.2)、
[PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、
[ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)、
[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)。
实际核对Dock布局/恢复、TreeList键/父键、SelectedObject/CellValueChanged、series绑定、SuperTip组成与非Bar挂接，落§8；工具未暴露dxdocs或匹配WPF skill，直接读同版本官方页，不以此阻依赖准入。文档不证明本控件真实WPF/UIA/焦点/DPI已通过。

scikit-image固定commit `533b7694d2004ae84e49e2cfd0bcfc5f8e562f22`，已读取实际源码/测试：

| commit固定原件 | SHA-256 |
|---|---|
| [实际拟合 src/_skimage2/measure/fit.py](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/measure/fit.py) | `02a1f272deebf824034f473022fc8c791b55c30aa35ad0b8b92969efb56bcb4f` |
| [拟合测试 tests/skimage2/measure/test_fit.py](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/measure/test_fit.py) | `8e7c7e3d91c215a3cebd8923565f877972c6071493592a60f0ddaed099fa8896` |
| [实际Canny src/_skimage2/feature/_canny.py](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/feature/_canny.py) | `3ef21accea9c880eb5b8318b002620dcf41116ab88804f79cbd965b49d9101b5` |
| [Canny测试 tests/skimage2/feature/test_canny.py](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/tests/skimage2/feature/test_canny.py) | `0f60c17ac997eeecfde35008c29686852d798456352c9e8f28c922c44eada5f7` |
| [转发层 src/skimage/measure/fit.py](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/skimage/measure/fit.py) | `f81f605cf1473c10b33bcade378a15926f366ed6f187f87677f6318e3ccde129`，未把转发层当算法 |
| [LICENSE.txt](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/LICENSE.txt) | `611d3207504dcb4a808df209d2e7c9b4f2e89fe690f84735c0d548160966b527`，上述范围BSD-3-Clause |

该commit [pyproject.toml](https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/pyproject.toml)依赖numpy≥2.1、非emscripten scipy≥1.15、networkx等。强项：中心化/尺度/SVD与整数溢出/invalid input/data-model validity、零mask/边界测试；落§6.2与T01/T06/T07。限制：两点重合须额外显式拒绝；像素布尔Canny/mask边界不等价HALCON亚像素属性；RANSAC不是本版固定geotukey。不复制求解器、不引Python生产依赖，不用上游测试结果冒充本模块资格。

## 16. AOI.Main 线路/焊盘/孔位经验的公共化边界

只读复核 [线路检测闭环指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-27-m12-trace-inspection-software-closure-design.md)、[焊盘检测闭环指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-27-m13-pad-inspection-full-closure-design.md) 和 [孔位检测闭环指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-27-m15-hole-inspection-production-closure-design.md)，仅把可跨项目的算法纪律纳入本模块：

1. 目标/设计几何只能生成候选和测量窗口；最终特征必须来自当前图像、当前 mask、有效域和可追溯坐标，不能用模板外包框伪造实测。
2. 处理链分为输入验证、候选生成、定位/拟合、测量、证据保存和宿主判定；候选差分、连通域或颜色差异不能直接变成缺陷事实。
3. 结果保留方法、候选数、分数/残差、采样数、降级原因、跨帧状态和来源 revision；没有必需原图/颜色/标定时宿主可标Disabled/Unsupported；本Core按F2D-001/002/003/005拒绝，不新增同义状态。
4. 跨 tile/FOV/帧边界对象在宿主编排先进入 `PendingBoundary`，等相邻输入到齐后按稳定 ID、空间关系和重叠证据确定合并；缺帧、坐标变化或扫描结束仍不完整时保持 `Incomplete`，不能改写成 `Missing`。这些是宿主状态，不进入本Core枚举/跨window拼接。
5. 单特征失败的隔离与整次请求失败关闭分开定义；取消必须等待工作终结和资源排空，批量统计不得把跳过、未观测和失败压成一个计数。

M12/M13/M15 的制程缺陷名、工艺阈值、M19 规则、组件类型和生产放行全部留在应用层；公共模块只提供特征候选、几何/区域证据和确定性执行端口。

## 17. 逐切片六项定位、自审与当前状态

| DEV-GOV-010 §3.1条件 | 规格定位/C1a、C1b、C1c | 主控接收（2026-10-10；仅规格） |
|---|---|---|
| 1 职责/依赖/第二消费者 | §1–2，孔/开口与板边/引脚接入计划、Owner清楚 | 三切片已接收 |
| 2 完整唯一API | §3–7、附录A v0.2，类型/单位/错误/资源/版本；平台Schema仅映射 | 三切片已接收 |
| 3 无UI最小Host | §1.3/§7/§9/A.3，BCL直注入，不需产品Shell/库/设备 | 三切片已接收 |
| 4 正常与异常样例 | §6两轮有限反例、§10–11，重复/并发/取消/超时/关闭/释放/回退/建议 | 三切片已接收 |
| 5 Benchmark方法 | §12与DEV-GOV-010公共口径，负载/测点/资源/失败处理；目标待消费者Profile采纳 | 三切片已接收；未测性能 |
| 6 工程/边界/命令 | §1.3/§9/§11，唯一BCL Exe含H1，A1/U1/生产后续门分开 | 三切片已接收；未执行构建/测试 |

C1a=附录值类型/纯Validate、支撑/索引/秩/残差/结果不变量，**不实现HALCON拟合求解器或调度**；C1b=端口/服务/有限队列、幂等/lease Owner/关闭与模拟故障；C1c=有限组合建议与独立真值评价。每片在同工程串行接收，不创建新模块/会话。

两轮有限审查：第一轮算法输入/输出反例已落§6；第二轮Host/资源/UI/建议反例已落§4–9与A.3–A.5。定向校验只针对本指导：复用现有validate_docs.targets核本地链接；内存Roslyn检查附录A托管声明、UI接点与最小调用示例语义，不输出程序集。这些不是产品编译或实际服务行为测试。主控于2026-10-10沿完整内容审核及窄修复核，接收原范围C1a/C1b/C1c六项为`ModuleCoreImplementationReady`，仅表示规格准备，不扩大切片、不提升整模块。N/Adapter（A1）、WPF（U1）、集成、性能和现场门保持原级别；H1执行也未验。本轮未执行产品编译/BCL harness、真实HALCON、WPF、性能、Golden/计量/HIL或现场。

本次窄修补A.1.1固定字节向量与严格UTF8/容量边界、§4.1.1 UTC接纳→单调截止、§11固定10/120/180秒wall预算及T10墙钟反例；主控已回读并独立按全部字段手写encoder复算1046字节request及186字节Profile的完整字节/摘要一致（具体值见A.1.1）。协议复算不等于产品测试。C1a/b/c规格接收门已关闭；平台映射Owner采纳、真实方法资格参数/工作集边界与真实输入、A1调用/释放、消费者目标Profile/Golden/计量/性能、U1挂接/真实WPF及产品现场为后续受影响门，均未提升。无客户事实不编默认；旧共享指导/架构中的封装能力门交主控修订，本轮只同步本页状态，不自动实施或新开范围。

2026-10-11本轮补A1/W1公开装配与消费者规格：§7.1沿原backend构造/ServiceOptions/job Owner，§7.2沿viewport公开root/factory/Bind-before-Attach/ROI只读桥，§9.2两个无UI消费者，§8.5～8.6及A.5源切换/权限/迟到/DetachTicket/双STA关闭恢复，§11复用既有测试工程定位。主控已对照viewport精确公开入口限定接收这些确定A1/W1技术方向，并回读接收§8.7～8.10两完整STA入口、明确无UI入口复用、构造前有界HostOwner/原Task/完整ViewportContext和Overlay/同Ticket有限恢复/共享Owner关闭边界的Host补全确定指导；仅限定内容接收，不表示实现或真实资格通过。W1是原U1补充，不新增模块/切片；C1a/b/c已接收内容、Core/API v0.2字段、算法与canonical保持不变。两轮有界自审为正常装配和异常/源切换/迟到/共享会话关闭规格检查；本次只同步接收状态，未创建工程/代码/文件或运行实际Adapter/HALCON/WPF/资源/性能/Golden/计量/现场，不提升这些门。

### 17.1 当前全部批准范围的准备结论与准确剩余项

2026-10-11原会话按当前IM-025架构全部批准能力做两轮有限内容自审，覆盖孔/开口、板边/引脚、元件/外观的通用特征消费者。Blob、模板匹配、Metrology模型和工艺判定继续只是§14历史来源或其它Owner范围，不因名称扩大当前API。总控只调度/接收结论；本模块内容审核、修复和验证由此永久原会话完成，不等待总控代做内容审核。

| 当前批准能力 | 唯一实施定位 | 本轮软件设计结论/尚缺事项 |
|---|---|---|
| 有向边/边对及灰度/颜色XLD、分段与原索引 | §2.2/3/6/7.3、A.1～3 | 固定路线/参数/支撑/局部偏移/基数/容量/资源顺序明确；真实HALCON结果与资格未验 |
| 显式支撑线/圆/椭圆、Standard/RobustTukey、残差/退化/稳定性 | §6.2/6.3/7.3、A.2～3 | 不抽稀/不混parent/目标先逐点Map/四挑战明确；客户物理阈值/方法资格待其真实来源，算法设计不待选 |
| 大图、有效域、Frame/ROI/坐标接入与版本 | §3.1/6.4/7.4 | 紧凑派生身份、闭/开端、Grid/有效域交集、同步Map异步留账桥确定；真实上游绑定和部署额度由消费宿主实现/验证，不重新猜契约 |
| 生命周期/幂等/取消/排空/错误/结果事实 | §4～5、A.1.1/A.3 | 原Task/部分Open/迟到/同对象释放重试与UTC→单调固定；无设备/持久化权限，实际软件行为未执行 |
| 离线有限建议、解释与显式新Draft采用 | §2.3/7.5/8、A.4～5 | 有限候选/允许字段/校准验证/负样本/拒绝/失效/采用步骤确定；真值和真实效果由消费者/资格Owner提供并验证 |
| 无UI独立引用与两消费者Host | §1.3/7.1/9/11/13 | 唯一工程/公开构造/故障恢复/第二消费者断言明确；工程未创建、harness未运行 |
| 可选DevExpress嵌入UI、三语/键盘/代次/权限/双STA/恢复 | §7.2/8/A.5 | 本模块三语保持闭合；最后F2D-UP-UI-01已按viewport0.3.4-prep公开同Control.Presentation/binding/Lifetime/Submission/trace接入两个Host并关闭，Unbind与晚到归还明确；真实WPF/可见/资源验证仍未执行 |
| 性能、包发布/版本/回退/产品验收 | §11～13/12.1 | 测点/分母/有限截止/结果判法/Owner明确；无性能目标不冒PASS，运行/物理/现场门另验 |

前轮完整三语目录和确定提示/格式/动态切换规则已闭合，F2D-UP-UI-02由本原会话解决、撤回移交viewport文字Owner的说法。本轮按总控定向任务只消费viewport0.3.4-prep新增公开接线并关闭F2D-UP-UI-01，未重审或改写图像/Frame/ROI/坐标/建议/性能/三语/Core与向量范围。两个历史具体欠账现均关闭，不再作为等待软件设计的活动门。

| ID | 本轮状态及确定消费 | 准确Owner/关闭依据 |
|---|---|---|
| F2D-UP-UI-01（已关闭） | viewport0.3.4-prep §10.6～10.9已给IViewportControlBinding.Presentation、binding:IPresentationPort、Options.Lifetime/ExecutionBudget、ViewportPresenterSubmission/trace；本页§8.7.1/8.8/8.9/8.10按最新签名传Lifetime:vp、原Commit转同Control，冻结原submission/call/授权并追踪原Task/lease与有限归还 | 上游定义Owner为viewport永久原会话`01a10307-1727-7691-90fe-26ab71976b94`（已核[模块索引](../MODULE-INDEX.md)）；消费设计/窄修/反例验证由features-2d本原会话完成。同Control/binding+真实输入输出+同root持原Task/lease+Unbind/迟到归还断言闭合；不增Root/Close，不以实际运行未验反称接口未定 |
| F2D-UP-UI-02（已关闭，责任纠正） | features-2d自身标题/参数/结果/枚举/提示/错误/恢复完整三语与嵌入资源、逐实例切换/缺键原子拒绝已在§8.4.1～5固定；删除假设的“随DLL获取viewport资源快照”调用 | features-2d本永久原会话独立完成并自审，既有A.5公开形状不变；不让宿主/viewport补本模块词表，不以资源校验代替真实WPF运行 |

**当前IM-025全部批准范围的可决定内部软件设计已全部闭合，文档准备完成。** 无剩余本模块算法/API/架构/三语/控件装配/Owner/有限恢复待程序员补猜，F2D-UP-UI-01/02均已关闭。该结论是当前架构批准能力的开发指导完整性，不自动授予新产品代码任务或整模块ImplementationSpecificationReady/Integration/Production，不等于实现或实测。C1a/b/c已接收规格、A1/W1限定内容接收及所有真实运行门保持；本轮只改唯一指导、两个既有Host示例的Bind实参和准确消费文字，不修改上游/登记/其它模块/工程，不新增Root/Close/产品代码/测试或报告。

其余准确后续工作：features-2d实施Owner负责产品构建/正式测试、A1真实HALCON与native释放/峰值/边界资格、U1真实WPF/实际显示观察/原Task资源与1920×1080/UIA/三语运行；消费产品Owner负责Frame/Support/标定/Profile真实绑定、真实样本/独立真值及客户精度/节拍/Golden/计量/现场。必要的上游源/viewport运行问题由对应image-frame/ROI/coordinate/viewport原Owner处理；实际发布资源包/依赖版本与部署容量由发布/宿主Owner提供。它们是按既定指导实施、真实输入或验证工作，不是留待设计；外部事实只阻依赖它的实际用途。

第一轮正常全能力自审核图像/通道/坐标/support→固定提取/分段→拟合/资格→结果→建议→两Host及可选UI；第二轮反例核padding/hash、闭端/空ROI、offset、部分Open、native中取消、Map Unknown/Dispose pending、校准验证隔离、候选非法/过期采用、共享Owner/迟到/缺资源及性能删失。保护段/代码块未变；定向链接/结构/新增闭开端与偏移反例验证只作为文档证据。未运行产品工程、HALCON、WPF、性能或现场，不以本轮文档校验宣布运行通过。

前轮三语窄修自审和校验保持：字段/公开enum/事件/阶段、完整key/占位符、19个错误、真实归还文字与旧结果/两STA隔离规则，不重复全审。最后接线窄修按§8.7.1五组反例自审：同Control入口/原Submission与SourceCall、Lifetime及预算、幂等原Task/错输入拒绝、Unbind与晚到/失败Value保lease、未知Return及共享Owner隔离；只做适用公开签名/Host实参/链接结构和保护段定向验证。两个Host代码块仅追加已公开Lifetime/ExecutionBudget，全部Core/API/向量声明代码块保持；产品构建/HALCON/WPF/实际读回观察/性能/现场均未执行。总控只接收状态，不再等待内容复核。

最后接线定向文档验证通过：50个本地链接/章节与围栏有效；最新上游Presentation/Lifetime/Submission/trace公开成员及两Host具名实参一致；软件fixture预算的表示/预留关系有效，实际容量不足仍按预检拒绝。旧三个保护段、A1图像/Frame/ROI/坐标/建议完整段、三语目录及性能判法段hash不变；八个C#代码块中仅两Host Bind追加公开实参，撤去这两处增量后与原块完全一致，其余六块不变。此为文档内容与消费签名核对，不是C#编译、运行测试、可见证明或产品验收。


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

## 附录 A：Module API Contract v0.2

附录接收状态：2026-10-10主控接收原范围C1a/C1b/C1c为`ModuleCoreImplementationReady`（仅规格准备），契约仍为0.2；未修改API、算法或canonical。2026-10-11 A1/W1公开装配、A.5及§8.7～8.10 Host补全确定指导已限定内容接收；A.5仍为可选U1规格，真实HALCON/WPF/资源/运行、N/Adapter/集成/性能/现场门未提升，产品执行/测试未验。主控对A.1.1的1046字节request及186字节Profile进行了独立完整字段编码复算，字节与摘要一致。

以下为唯一托管公开类型形状，namespace `Asun.Modules.Features2D`；只用.NET BCL，未实现方法不在本轮写代码。可空表示明确未提供/不适用，须带EvidenceState或对应错误，不以0代替；ImmutableArray非default，合法空用Empty。所有ID/Key比较Ordinal。Contract=0.2，本版变更必须显式采纳；不是平台JSON Schema获批。

### A.1 身份、帧、计划与参数

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
namespace Asun.Modules.Features2D;

public readonly record struct AssetRef(string Id, string Revision, string Sha256);
public readonly record struct Point2D(double A, double B);
public readonly record struct Vector2D(double A, double B);
public readonly record struct PixelRun(int Row, int StartColumn, int EndColumn);
public readonly record struct PixelRect(int Row, int Column, int Width, int Height);
public enum RouteKind { MeasurePos=0, MeasurePairs=1, Xld=2, ColorXld=3 }
public enum PrimitiveKind { None=0, Line=1, Circle=2, Ellipse=3 }
public enum PixelLayout { Mono8=0, Mono16=1, MonoFloat32=2, Rgb8Planar=3, Rgb16Planar=4 }
public enum CoordinateSpace { Image=0, Target=1 }
public enum AxisHandedness { Right=0, Left=1, ImageRaster=2 }
public enum InterpolationKind { Nearest=0, Bilinear=1, Bicubic=2 }
public enum TransitionKind { Positive=0, Negative=1, All=2, PositiveStrongest=3, NegativeStrongest=4, AllStrongest=5 }
public enum SelectionKind { All=0, First=1, Last=2 }
public enum SegmentationMode { None=0, Lines=1, LinesCircles=2, LinesEllipses=3 }
public enum FitPolicy { Standard=0, RobustTukey=1 }
public enum FitObservation { Edge=0, PairFirst=1, PairSecond=2, PairCenter=3 }
public enum EvidenceState { Provided=0, NotProvided=1, NotApplicable=2, Unknown=3 }
public enum MappingState { Exact=0, Unknown=1 }
public enum ErrorCode {
    InvalidRequest=1, UnsupportedCapability=2, FrameUnavailable=3,
    SupportInvalid=4, CoordinateInvalid=5, NoCandidate=6, AmbiguousAssociation=7,
    DegenerateFit=8, BudgetExceeded=9, Cancelled=10, TimedOut=11,
    NativeFailure=12, ResourceFailure=13, VersionMismatch=14,
    InternalInvariant=15, IdentityConflict=16, ServiceClosed=17,
    SourceInvalidated=18, RecommendationAbstained=19
}
public sealed record Features2DError(ErrorCode Code, string? WorkId, string DetailKey);
public sealed class Features2DPortException : Exception {
    public ErrorCode Code { get; }
    public Features2DPortException(ErrorCode code, string diagnostic) : base(diagnostic) => Code=code;
}
public sealed record RequestIdentity(string OperationId, string AttemptId, long Generation, string ConsumerAdapterId);
public sealed record FrameRef(
    AssetRef Asset, long Generation, int Width, int Height, PixelLayout Layout,
    int StrideBytes, DateTimeOffset BorrowDeadlineUtc, AssetRef AcquisitionQualification);
public sealed record SupportRegionRef(AssetRef Asset, AssetRef FrameAsset, ImmutableArray<PixelRun> Runs);
public sealed record CaliperSlot(
    string Id, Point2D Origin, Vector2D SearchV, double SearchHalfLengthPx,
    double ProjectionHalfLengthPx, string ObservationRole);
public sealed record AnalysisWindow(
    string Id, PixelRect ComputeRect, PixelRect QualifiedInnerRect, string ObservationRole);
public sealed record FitGroup(string Id, ImmutableArray<string> SlotIds, FitObservation Observation);
public sealed record SamplingPlan(
    RouteKind Route, PrimitiveKind Primitive, ImmutableArray<CaliperSlot> Slots,
    ImmutableArray<AnalysisWindow> Windows, ImmutableArray<FitGroup> FitGroups);
public sealed record CaliperOptions(
    double SigmaPx, double ThresholdNative, TransitionKind Transition,
    SelectionKind Selection, InterpolationKind Interpolation,
    bool PairDiagnostics, double MatchTolerancePx);
public sealed record XldOptions(
    double Alpha, double Low, double High, SegmentationMode Segmentation,
    double MaxLineDist1Px, double MaxLineDist2Px);
public sealed record FitOptions(FitPolicy Policy, int Iterations, double ClippingFactor, double MaxClosureDistance);
public sealed record ParameterDeltaLimits(double CenterOrEndpoint, double RadiusOrAxis, double AngleRad, double LineDist);
public sealed record FitQualification(
    AssetRef Asset, int MinPoints, double MinSpan, double MinRankRatio,
    int MaxMissingSlots, int MaxConsecutiveMissingSlots,
    double MinCoverageRad, double MaxGapRad, double MaxAxisRatio,
    double NearCircleRelativeGap, double MaxMeanAbsoluteResidual,
    double MaxAbsoluteResidual, double? MaxRmsResidual, double StabilityDelta,
    ParameterDeltaLimits MaxParameterDelta);
public sealed record Features2DProfile(
    AssetRef Asset, AssetRef MethodAsset, string RequiredBackendVersion,
    int ContractMajor, int ContractMinor, PixelLayout RequiredLayout,
    double MinimumFeatureWidthPx, double OriginalIndexTolerancePx,
    CaliperOptions? Caliper, XldOptions? Xld, FitOptions? Fit,
    FitQualification? Qualification);
public sealed record CoordinateContext(
    CoordinateSpace Target, string TargetUnit, string AxisA, string AxisB,
    AxisHandedness Handedness, AssetRef? MapAsset, AssetRef? Qualification,
    DateTimeOffset BorrowDeadlineUtc);
public sealed record ExecutionBudget(
    DateTimeOffset DeadlineUtc, int MaxSlots, int MaxWindows, int MaxFitGroups,
    int MaxCandidatesPerWork, int MaxContourPoints, long MaxResultBytes,
    long MaxWorkingSetBytes, int MaxConcurrentSlots);
public sealed record Features2DRequest(
    RequestIdentity Identity, FrameRef Frame, SupportRegionRef Support,
    SamplingPlan Plan, Features2DProfile Profile, CoordinateContext Coordinates,
    ExecutionBudget Budget);
public sealed record ValidationReport(bool IsAccepted, ImmutableArray<Features2DError> Errors);
```

Asset.Id/Revision非空，Sha256为64hex，比较摘要忽略hex大小写，原文本输入统一lowercase进入digest；Generation≥0且Identity.Generation=Frame.Generation。Frame宽高/stride为正按§3.1 checked字节；PixelRect宽高>0、合法范围，QualifiedInnerRect包含于ComputeRect，所有run合法升序。Caliper.Origin必须在Image范围，参与包络仍须完整有效；非负中心取整按§3.2，Raw.EffectiveOrigin与SupportRequirement必须一致。Support hash规范为UTF8无BOM的十进制`row,start,end\n`（LF）；Frame hash为原租约全部字节。Profile/Method/坐标资格内容hash由对应提供者的规范资产承担，消费方验证精确引用，不用GetHashCode假hash。

RequestDigest为SHA256，覆盖除所有Deadline外的完整请求值（Identity含OperationId/AttemptId；deadline首次绑定不可延长）。固定规范：按A.1声明字段顺序递归，无字段名/空白；null为单字节N；record为R+int32字段数LE后各字段；数组为L+int32长度LE+各元素；string为S+int32 UTF8字节长度LE+原UTF8；int32/enum为I+4字节LE，int64为J+8字节LE，double为D+IEEE754 binary64 LE（−0规范+0，拒非有限），bool为T或F；DateTimeOffset为U+UTC ticks int64 LE，TimeSpan为V+ticks int64 LE；Asset.Sha256先lowercase。三个Deadline位置一律写N，不因排除导致拼接歧义。它只管本模块幂等，不替换来源资产摘要。

时间域/UTC接纳/单调截止唯一见§4.1.1，纯Validate检查格式和哨兵、不读取当前UTC；service在首次接纳Owner中检查剩余时长。三个Deadline虽在digest写N，仍不可跳过时间合法性校验。

### A.1.1 严格编码、容量与固定向量（C1a；F2D-D01）

协议继续使用A.1的R字段数、LE整数、逐字段值与三个Deadline写N，不添加字段/平台协议，不改成JCS。标签为单个ASCII字节；UTF8严格、无BOM，C#使用`new UTF8Encoding(false, true)`：先检查并调用GetByteCount，再有界编码/流式SHA256。合法代理项对编码为对应Unicode标量；孤立高/低代理项、反序代理项均在副作用前F2D-001，不能用U+FFFD替换后hash。字符串不trim、不做NFC/NFD/大小写转换（仅Asset.Sha256统一lowercase），Unicode组合形式不同即不同digest。

本模块当前容量固定：每string严格UTF8≤4096字节（含所有ID/role/unit/版本字段），每request全部string字段累计≤65536字节，重复引用在每个编码位置重复计数；数组/record字段计数均非负且≤Int32.MaxValue，长度前缀不能截断为uint/int16。单request规范编码总长≤16MiB且≤Budget.MaxWorkingSetBytes，checked int64累计计数；不能先分配超大缓冲再核预算。槽/窗口/group/点数与各Budget再分别校验；枚举固定int32、Generation和字节额度int64，checked乘积/求和溢出F2D-001，合法数值超过本模块容量F2D-009。编码器允许按流哈希，不要求一次int数组，但同样受总长上限；其它建议/结果DTO沿同编码时必须受自身已定义预算，string仍≤4096。校验错误结果不回显超长/非法字符串，相关身份仅保留已校验可编码值，未校验身份槽用固定合法诊断标识"invalid"且不得写进准入账，不能再触发无限分配。

**完整输入（全部值明确，合法简单E1，无native；不是生产参数）。** 受控接纳Utc=2026-10-09T00:00:00Z；Frame.BorrowDeadlineUtc、Coordinates.BorrowDeadlineUtc、Budget.DeadlineUtc全部为2026-10-09T00:01:00Z，规范编码中仍各写N。全部Asset.Revision="1"，Id为下表小写单字母。

| Asset.Id | 内容来源与SHA-256 |
|---|---|
| f | 16×16 Mono8全零帧，共256原字节，stride16；`5341e6b2646979a70e57653007a1f310169421ec9bdd9f1a5648f75ade005af1` |
| s | UTF8无BOM的七行`5,4,12\n`至`11,4,12\n`（row逐1递增，末行也LF）；`54c3ac4b881779b6aa6ed1df3e16ef11feafdaee3ac0d731711ed3c10b4ac11d` |
| q | UTF8单字母`q`（无LF），仅模拟采集资格来源；`8e35c2cd3bf6641bdb0e2050b76932cbb2e6034a0ddacc1d9bea82a6ba57f7cf` |
| m | UTF8单字母`m`（无LF），仅模拟方法资格来源；`62c66a7a5dd70c3146618063c344e531e6d4b59e379808443ce962b3abd63c5a` |
| p | 以下完整Profile规范内容，把仅顶层Asset字段写N避免自引用；`ded39021cd68a1a6cb97ee9040cce64c4560dbc479b3603a809d70cf77407d86` |

- Identity=(OperationId="o",AttemptId="a",Generation=1,ConsumerAdapterId="c")。
- Frame=(Asset=f,Generation=1,Width=16,Height=16,Layout=Mono8(0),StrideBytes=16,BorrowDeadlineUtc如上,AcquisitionQualification=q)。
- Support=(Asset=s,FrameAsset=f,Runs=[(5,4,12),(6,4,12),(7,4,12),(8,4,12),(9,4,12),(10,4,12),(11,4,12)])。
- Plan=(Route=MeasurePos(0),Primitive=None(0),Slots=[唯一slot],Windows=Empty,FitGroups=Empty)；slot=(Id="x",Origin=(8,8),SearchV=(0,1),SearchHalfLengthPx=2,ProjectionHalfLengthPx=1,ObservationRole="e")。
- Profile=(Asset=p,MethodAsset=m,RequiredBackendVersion="sim-1",ContractMajor=0,ContractMinor=2,RequiredLayout=Mono8(0),MinimumFeatureWidthPx=1,OriginalIndexTolerancePx=0,Caliper如下,Xld=null,Fit=null,Qualification=null)。
- Caliper=(SigmaPx=0.4,ThresholdNative=1,Transition=Positive(0),Selection=All(0),Interpolation=Bilinear(1),PairDiagnostics=false,MatchTolerancePx=0)。
- Coordinates=(Target=Image(0),TargetUnit="px",AxisA="row",AxisB="column",Handedness=ImageRaster(2),MapAsset=null,Qualification=null,BorrowDeadlineUtc如上)。
- Budget=(DeadlineUtc如上,MaxSlots=1,MaxWindows=1,MaxFitGroups=1,MaxCandidatesPerWork=4,MaxContourPoints=16,MaxResultBytes=4096,MaxWorkingSetBytes=1048576,MaxConcurrentSlots=1)。

p的来源规范内容完整hex如下，ASCII标签/所有字段按A.1顺序，不包含任何隐含JSON；长度=186字节：
```text
520c0000004e520300000053010000006d530100000031534000000036326336
3661376135646437306333313436363138303633633334346535333165366434
6235396533373938303834343363653936326233616264363363356153050000
0073696d2d3149000000004902000000490000000044000000000000f03f4400
000000000000005207000000449a9999999999d93f44000000000000f03f4900
00000049000000004901000000464400000000000000004e4e4e
```

Request顶层R字段数为7，开头`5207000000`。下表offset从0算，顶层头占[0,5)，各字段连续无padding：

| 字段 | 起始offset（byte） | 长度（byte） |
|---|---:|---:|
| Identity | 5 | 32 |
| Frame | 37 | 207 |
| Support | 244 | 322 |
| Plan | 566 | 111 |
| Profile | 677 | 271 |
| Coordinates | 948 | 44 |
| Budget | 992 | 54 |

**固定断言：编码总长1046字节，SHA-256=`f437326a097949d236d94d601fdd458678b5bc5fc8728a18b6f3a0af317fde72`。** 完整hex如下，各行仅为排版；解码须直接拼接所有hex字符，不计换行：
```text
5207000000520400000053010000006f5301000000614a010000000000000053
0100000063520800000052030000005301000000665301000000315340000000
3533343165366232363436393739613730653537363533303037613166333130
3136393432316563396264643966316135363438663735616465303035616631
4a010000000000000049100000004910000000490000000049100000004e5203
0000005301000000715301000000315340000000386533356332636433626636
3634316264623065323035306237363933326362623265363033346130646461
6363316439626561383261366261353766376366520300000052030000005301
0000007353010000003153400000003534633361633462383831373739623661
6136656431646633653136656631316665616664616565336163306437333137
3131656433633130623461633131645203000000530100000066530100000031
5340000000353334316536623236343639373961373065353736353330303761
3166333130313639343231656339626464396631613536343866373561646530
30356166314c07000000520300000049050000004904000000490c0000005203
00000049060000004904000000490c0000005203000000490700000049040000
00490c000000520300000049080000004904000000490c000000520300000049
090000004904000000490c0000005203000000490a0000004904000000490c00
00005203000000490b0000004904000000490c00000052050000004900000000
49000000004c0100000052060000005301000000785202000000440000000000
0020404400000000000020405202000000440000000000000000440000000000
00f03f44000000000000004044000000000000f03f5301000000654c00000000
4c00000000520c00000052030000005301000000705301000000315340000000
6465643339303231636436386131613663623937656539303430636365363463
3435363064626334373962333630336138303964373063663737343037643836
520300000053010000006d530100000031534000000036326336366137613564
6437306333313436363138303633633334346535333165366434623539653337
39383038343433636539363262336162643633633561530500000073696d2d31
49000000004902000000490000000044000000000000f03f4400000000000000
005207000000449a9999999999d93f44000000000000f03f4900000000490000
00004901000000464400000000000000004e4e4e520800000049000000005302
00000070785303000000726f775306000000636f6c756d6e49020000004e4e4e
52090000004e490100000049010000004901000000490400000049100000004a
00100000000000004a00001000000000004901000000
```

本次文档复算用一套类型树递归编码器与另一套按固定字段顺序手写拼接的独立编码器（不调用前者/不共用其树遍历），两者逐字节、总长、p内容摘要与request摘要一致；只作协议向量复核，不写编码产品代码、不冒充C1a实现测试已运行。后续T01必须将完整hex与长度/hash硬断言，不能只测“自己encode再自己decode相等”；deadline改变且仍合法不改digest，Threshold变化必须改digest，−0/+0编码相同，孤立代理项拒绝，4096/4097与累计65536/65537字节边界分别通过/拒绝。

Image目标固定px/row/column/ImageRaster且MapAsset/Qualification=null；Target必须单位非空、不同轴名、Right/Left及两个资产完整，所有输出阈值同TargetUnit。角rad，Image参数Px；MinSpan/StabilityDelta>0，0<MinRankRatio≤1，0≤MinCoverage/MaxGap≤2π，MaxAxisRatio≥1，NearCircleGap∈[0,1)，其它残差/参数变化上限有限≥0。缺slot上限≥0且小于各FitGroup计划数；XLD必须0，MaxMissing与MaxConsecutive均为0才表示不允许缺slot。Ellipse.MaxRmsResidual=null；Line/Circle可null表示不设RMS门，但MeanAbs/MaxAbs门必给。MinPoints不低数学下限，OriginalIndexTolerancePx≥0/MinimumFeatureWidthPx>0且随MethodAsset资格冻结。

FitGroup只引用存在Slots，各group内无重复SlotId，允许不同group显式复用slot（不重复Extract），按声明顺序拟合；ID与所有work不同。PairDiagnostics仅E2合法；E1 FitObservation.Edge，E2 PairFirst/Second/Center；未指定/未知值拒绝。Primitive=None要求Groups空/Fit与Qualification=null，XLD.None分段必须None；其余按§3合法组合校验。Route.Caliper不接受RGB，ColorXld只RGB，Xld只Mono。RequiredBackendVersion完全匹配注入Descriptor，不能默默fallback。MinimumFeatureWidth不是客户缺陷阈值。

### A.2 原证据、候选、事件与结果

```csharp
public enum WorkStatus { NotStarted=0, Completed=1, Empty=2, Rejected=3, Ambiguous=4, Truncated=5, Faulted=6 }
public enum CandidateValidity { ValidCandidate=0, InsufficientSupport=1, Ambiguous=2, InvalidGeometry=3, NotAvailable=4 }
public enum ExecutionStatus { Completed=0, NoCandidate=1, Ambiguous=2, Rejected=3, Truncated=4, Cancelled=5, TimedOut=6, Faulted=7 }
public enum OperationPhase { Validating=0, Queued=1, Running=2, Draining=3, Terminal=4 }
public enum DrainStatus { Drained=0, DrainUnknown=1 }
public enum EventKind {
    RequestReceived=0, ValidationCompleted=1, RequestRejected=2, RequestAccepted=3,
    ExecutionStarted=4, WorkCompleted=5, Progress=6, CancellationRequested=7,
    TimeoutReached=8, DrainStarted=9, DrainCompleted=10, ResourcesReleased=11, Terminal=12
}
public sealed record ScalarEvidence(double? Value, EvidenceState State);
public sealed record EdgeObservation(int NativeIndex, Point2D ImagePoint, double SignedAmplitude, double SearchPositionPx);
public sealed record EdgeDistance(int FirstIndex, int SecondIndex, double DistancePx);
public sealed record PairObservation(int NativePairIndex, EdgeObservation First, EdgeObservation Second, double IntraDistancePx);
public sealed record PairGap(int FirstPairIndex, int SecondPairIndex, double InterDistancePx);
public sealed record PairEdgeLink(int PairIndex, bool IsFirst, int? DiagnosticEdgeIndex, MappingState Mapping);
public sealed record ContourSample(
    int LocalIndex, int? OriginalIndex, Point2D ImagePoint,
    ScalarEvidence Response, ScalarEvidence AngleRad, ScalarEvidence EdgeDirectionRad);
public sealed record ContourObservation(
    int ParentIndex, int SegmentIndex, bool IsClosed, int? ContApprox,
    MappingState OriginalMapping, ImmutableArray<ContourSample> Samples);
public sealed record RawWorkResult(
    string WorkId, bool Exhaustive, Point2D? EffectiveOrigin,
    ImmutableArray<EdgeObservation> Edges, ImmutableArray<EdgeDistance> AdjacentDistances,
    ImmutableArray<PairObservation> Pairs, ImmutableArray<PairGap> InterPairDistances,
    ImmutableArray<PairEdgeLink> DiagnosticLinks,
    ImmutableArray<ContourObservation> OriginalContours,
    ImmutableArray<ContourObservation> Segments, ImmutableArray<Features2DError> Errors);
public sealed record SupportEvidence(
    int PlannedSlots, int UniqueObservedSlots, ScalarEvidence SlotCoverage,
    ScalarEvidence AngularCoverageRad, ScalarEvidence MaxAngularGapRad,
    ImmutableArray<string> MissingSlotIds, AssetRef MethodQualification, bool BoundaryLimited);
public sealed record GeometryContext(CoordinateSpace Space, string Unit, string AxisA, string AxisB, AxisHandedness Handedness);
public abstract record PrimitiveGeometry(GeometryContext Context);
public sealed record LineGeometry(
    GeometryContext Context, Point2D BeginProjection, Point2D EndProjection,
    Point2D MinSupportProjection, Point2D MaxSupportProjection,
    double Nr, double Nc, double Dist) : PrimitiveGeometry(Context);
public sealed record CircleGeometry(
    GeometryContext Context, Point2D Center, double Radius,
    double StartPhiRad, double EndPhiRad, string PointOrder) : PrimitiveGeometry(Context);
public sealed record EllipseGeometry(
    GeometryContext Context, Point2D Center, double Radius1, double Radius2,
    double NativePhiRad, ScalarEvidence ObservableAxisAngleRad,
    double StartPhiRad, double EndPhiRad, string PointOrder) : PrimitiveGeometry(Context);
public sealed record FitPoint(string SourceId, int SourceIndex, Point2D ImagePoint, Point2D FitPointValue);
public sealed record ResidualEvidence(
    double MeanAbsolute, double MaxAbsolute, ScalarEvidence Rms,
    ImmutableArray<double> SignedPerPoint, string MetricKey);
public sealed record StabilityTrial(string TrialId, bool Succeeded, ParameterDeltaLimits? ObservedDelta, ImmutableArray<Features2DError> Errors);
public sealed record FitEvidence(
    string BackendMethod, ImmutableArray<FitPoint> InputPoints,
    ImmutableArray<int>? BackendInliers, ImmutableArray<int> DiagnosticExcluded,
    EvidenceState DiagnosticExclusionState, ResidualEvidence Residual,
    ImmutableArray<StabilityTrial> Stability, ScalarEvidence RankRatio,
    SupportEvidence Support, ScalarEvidence Uncertainty);
public sealed record PrimitiveCandidate(
    string Id, string WorkId, int ParentIndex, int SegmentIndex,
    PrimitiveKind Kind, CandidateValidity Validity, PrimitiveGeometry? Geometry,
    FitEvidence? Evidence, ImmutableArray<Features2DError> Errors);
public sealed record WorkResult(
    string Id, WorkStatus Status, RawWorkResult? Raw,
    ImmutableArray<PrimitiveCandidate> Candidates, ImmutableArray<Features2DError> Errors);
public sealed record StageTiming(string StageKey, string? WorkId, TimeSpan Duration);
public sealed record OperationReceipt(
    RequestIdentity Identity, string RequestDigest, AssetRef FrameAsset,
    AssetRef SupportAsset, AssetRef ProfileAsset, AssetRef MethodAsset, AssetRef? MapAsset,
    string ModuleVersion, string BackendVersion, string RuntimeVersion, bool IsSimulation,
    DateTimeOffset? AcceptedUtc, DateTimeOffset TerminalUtc, bool ResourcesReleased,
    long PeakManagedBytes, long? PeakNativeBytes, long LogicalResultBytes,
    long DroppedEventCount, ImmutableArray<StageTiming> Timings);
public sealed record Features2DResult(
    ExecutionStatus Status, ImmutableArray<WorkResult> Works,
    ImmutableArray<Features2DError> Errors, OperationReceipt Receipt);
public sealed record Features2DEvent(
    string OperationId, long Generation, long Sequence, DateTimeOffset Utc,
    EventKind Kind, string? WorkId, double? Progress, Features2DError? Error);
public sealed record OperationSnapshot(
    string OperationId, OperationPhase Phase, ExecutionStatus? TerminalIntent,
    int PendingReleases, Features2DResult? FinalResult);
public sealed record DrainReport(DrainStatus Status, ImmutableArray<string> PendingOperationIds);
```

Works顺序=Slots或Windows声明序→FitGroups声明序；所有计划ID包含NotStarted。XLD候选按parent/segment原序，不按score重排。原Contours.SegmentIndex=−1，Segments从0且引用ParentIndex；原点本身OriginalIndex=LocalIndex/Exact，segment映射不唯一为null/Unknown，几何仅诊断且最多InsufficientSupport。短轮廓复制ContApprox可null，不能补类型。关闭点重复保留原证据，拟合资格单独检查。E2 Pair.First/Second NativeIndex为返回pair序号（通过IsFirst区分），不是diagnostic edge全局索引；DiagnosticLinks只给明确唯一对应，否则null/Unknown。

FitPoint保留SourceId(slot或window/parent/segment)、原SourceIndex、ImagePoint与FitPointValue；PairCenter为显式派生点仍标来源pair索引。线/圆SignedPerPoint长度等InputPoints，ellipse Empty/Rms.NotProvided。BackendInliers=null明确未提供；四挑战按A+/A−/B+/B−完整，有失败不得ValidCandidate。ScalarEvidence.Value仅Provided可非null且有限；其它状态必须null。原映射Unknown的XLD拟合候选最多InsufficientSupport，原segment点的几何可诊断。候选无有效模型可Geometry/Evidence=null+Errors，禁止填零几何。

MaxResultBytes采用同A.1规范编码的完整结果逻辑字节（数值固定宽度、string/数组前缀、record/null标记），Receipt中Timings/Errors/WorkId也计；StageTiming每work每固定stage最多1条、4个trial各1条，等待/Retry累计到原stage不新增无限条，重试次数仅宿主诊断计数；Receipt.LogicalResultBytes字段始终8字节，因此不循环变长。接纳时先估全部计划/最低receipt+NotStarted项能放下，否则F2D-009接纳前拒绝；保留在该最小容量内的停止错误最多每work一条+operation一条，其余诊断只计数/宿主日志。完整contour/work复制前checked估大小，放不下即Truncated，剩余项NotStarted并写上限原因，不无限堆错误字符串。PeakManagedBytes为操作内显式记账的托管payload峰值（含帧/数组/已知复制），不是CLR全堆实测；真实进程峰值在Benchmark外测另列，不能把此数声称实际CLR上限。Native未完整可测则null。Receipt.ResourcesReleased在实际全部归还后true，预检无资源Rejected也true且AcceptedUtc=null。

### A.3 端口、服务与后端资格

```csharp
public sealed record BackendDescriptor(
    string Version, string RuntimeVersion, bool IsSimulation,
    ImmutableArray<RouteKind> Routes, ImmutableArray<PrimitiveKind> Primitives);
public sealed record MethodQualificationRule(
    AssetRef MethodAsset, RouteKind Route, PixelLayout Layout,
    double MinSigmaOrAlpha, double MaxSigmaOrAlpha, double MinimumFeatureWidthPx,
    int MaxComputeWidth, int MaxComputeHeight, int QualifiedBoundaryInsetPx,
    int MaxNativePoints, long FixedNativeBytes, long NativeBytesPerPixel,
    long NativeBytesPerPoint);
public sealed record BackendQualification(
    AssetRef Asset, string BackendVersion, string RuntimeVersion,
    ImmutableArray<MethodQualificationRule> Methods);
public sealed record SupportRequirement(
    string WorkId, ImmutableArray<PixelRun> RequiredRuns, Point2D? EffectiveOrigin,
    long ConservativeWorkingSetBytes, AssetRef Qualification,
    ImmutableArray<Features2DError> Errors);
public sealed record FitInput(
    string WorkId, string TrialId, PrimitiveKind Primitive,
    ImmutableArray<Point2D> Points, GeometryContext Context, FitOptions Options);
public sealed record BackendFitResult(
    PrimitiveGeometry? Geometry, string Method, double? EllipseMeanAbsoluteDistance,
    double? EllipseMaxAbsoluteDistance, ImmutableArray<Features2DError> Errors);
public interface IFrameSource {
    ValueTask<IFrameLease> AcquireAsync(FrameRef frame, CancellationToken cancellation);
}
public interface IFrameLease : IAsyncDisposable {
    FrameRef Frame { get; }
    ReadOnlyMemory<byte> Data { get; }
    void RequireCurrent(DateTimeOffset utc);
}
public interface ICoordinateMapper {
    ValueTask<ICoordinateLease> AcquireAsync(CoordinateContext context, CancellationToken cancellation);
}
public interface ICoordinateLease : IAsyncDisposable {
    CoordinateContext Context { get; }
    void RequireCurrent(DateTimeOffset utc);
    ImmutableArray<Point2D> Map(ImmutableArray<Point2D> imagePoints);
}
public interface IWorkingSetSource {
    ValueTask<IWorkingSetLease> ReserveAsync(long bytes, CancellationToken cancellation);
}
public interface IWorkingSetLease : IAsyncDisposable {
    long ReservedBytes { get; }
    long PeakManagedBytes { get; }
    long? PeakNativeBytes { get; }
    void ObserveUsage(long managedPayloadBytes, long? nativeBytes);
}
public sealed record BackendOpenResult(IFeatures2DJob? Job, Features2DError? Error);
public interface IFeatures2DBackend {
    BackendDescriptor Descriptor { get; }
    ImmutableArray<SupportRequirement> DescribeSupport(Features2DRequest request);
    ValueTask<BackendOpenResult> OpenAsync(
        Features2DRequest request, IFrameLease frame, IWorkingSetLease resources,
        CancellationToken cancellation);
}
public interface IFeatures2DJob : IAsyncDisposable {
    ValueTask<RawWorkResult> ExtractAsync(string workId, CancellationToken cancellation);
    ValueTask<BackendFitResult> FitAsync(FitInput input, CancellationToken cancellation);
    void RequestCancel();
}
public sealed record ServiceOptions(
    int MaxQueuedOperations, int MaxConcurrentOperations, int MaxConcurrentSlots,
    int MaxRetainedOperations, long MaxRetainedResultBytes, int EventQueueCapacity, TaskScheduler EventScheduler);
public interface IFeatures2DService : IAsyncDisposable {
    BackendDescriptor Backend { get; }
    ValidationReport Validate(Features2DRequest request);
    Task<Features2DResult> ExecuteAsync(
        Features2DRequest request, IProgress<Features2DEvent>? progress,
        CancellationToken operationCancellation);
    OperationSnapshot? GetOperation(string operationId);
    bool Cancel(string operationId);
    ValueTask<DrainReport> WaitOperationsAsync(
        ImmutableArray<string> operationIds, TimeSpan timeout, CancellationToken waitCancellation);
    ValueTask<DrainReport> DrainAsync(TimeSpan timeout, CancellationToken waitCancellation);
    ValueTask<DrainReport> CloseAsync(TimeSpan timeout, CancellationToken waitCancellation);
    ValueTask<DrainReport> RetryReleasesAsync(
        ImmutableArray<string> operationIds, TimeSpan timeout, CancellationToken waitCancellation);
}
```

具体类`Features2DService : IFeatures2DService`唯一公开构造：
`Features2DService(IFrameSource frames, IFeatures2DBackend backend, ICoordinateMapper mapper, IWorkingSetSource resources, TimeProvider timeProvider, ServiceOptions options)`。构造不启动native；null/非法options抛ArgumentException；纯Validate与Execute前置使用同一函数，Descriptor在构造时复制为不可变快照，不通过动态getter读取native状态。所有DTO接纳后不可变，Core不需要隐藏窗口/平台容器。

Options并发/保留/保留结果字节/事件容量>0，Queued≥0；并发初始显式1。MaxRetainedOperations≥MaxConcurrentOperations+MaxQueuedOperations，单queue/active有界；终态保留按(TerminalUtc,OperationId)旧先出，活跃绝不逐出。接纳还须为该操作Budget.MaxResultBytes在Options.MaxRetainedResultBytes中预留终态缓存份额，超限先逐出旧terminal、仍不足则接纳前F2D-009；服务转terminal按实际逻辑bytes结算，借出结果由调用者拥有，模块缓存不重复复制。全部ID不符合元数据的请求仍返回Rejected结果（有错误，不借用），Execute仅未知程序异常可抛异常，不能throw取消伪装实际停止。重复ID等待token取消可以抛OperationCanceledException但原Task不变。RequestReceived前取消首次request也返回无资源Cancelled结果，不调用backend。

WaitOperationsAsync/Retry的operationIds非default、无重复；Empty表示空集合已Drained，不表示全服务；全服务IDs由宿主从自持OperationId传入或用Drain/Close。未知/已逐出ID不得当Drained，抛Features2DPortException(InvalidRequest)；ticket保留自己已取得terminal结果不依赖已逐出查询。所有timeout有限≥0，waitCancellation只结束等待。GetOperation未知返回null。Cancel仅找到非terminal且未计算封口时true，记录意图，非native已停。

DescribeSupport仅Slots/Windows各一项（FitGroups无图像采样要求），Errors非空只拒对应work；总资源预留=max并发work保守native峰值之和+本请求最大托管结果/输入/映射/挑战副本，checked且≤Budget.MaxWorkingSetBytes，否则接纳前拒绝。资格按MethodQualificationRule绑定MethodAsset/Route/Layout，Sigma或Alpha范围、最小特征宽度/最大窗口尺寸、原生点数上限与保守容量全部实际资格冻结；所有值有限，范围0<min≤max、尺寸/点数>0、Inset≥0、bytes≥0且合计>0。CalculateSupport固定：卡尺EffectiveOrigin按§3.2明确floor(value+0.5)，以该整数中心调用native，V/U四角外包框在各轴向外ceil并加nearest=1/bilinear=2/bicubic=3像素保守边距（覆盖§3.2最低插值边距与中心舍入，不称逐像素贡献证明）；逐行整段run，不以reduce_domain排岛。XLD RequiredRuns是ComputeRect全部像素，QualifiedInnerRect到计算边界每侧≥QualifiedBoundaryInsetPx；该Inset是方法已资格的输出边界范围，不从Alpha猜精确滤波核。Native预算=FixedNativeBytes+computeArea×NativeBytesPerPixel+MaxNativePoints×NativeBytesPerPoint，以checked算；同时预留原帧/托管结果/映射/挑战份额。A1真实峰值/边界等价证据缺失时不能提供通过资格的Rule；模拟Rule仅模拟标记。参数/尺度不在资格Methods中F2D-014/004，不猜上界，不把经样本建立的保守预留声称native硬分配限。资源ObserveUsage在各分配/阶段向IWorkingSetLease报告当前托管payload与可测native数，非负且checked；提供者跟踪最大/是否native观测完整，任一阶段未知则PeakNativeBytes=null。超ReservedBytes抛F2D-013并故障排空，不能释放在用对象；后台无法观测的native临时峰值按方法资格/外部Benchmark证据记录，不能冒称实时精确分配器。资源提供者Reserve返回实际ReservedBytes≥请求，系统总额度不足F2D-013，不假称强限native allocator。

获取Task/ValueTask均由operation Owner记录；请求取消/Close到期不丢掉仍在途Acquire/Open/Dispose。未完成获取将operation置Draining；晚到成功lease立即登记再逆序归还；晚到异常只有提供者保证没有未交付资源才可清理该获取项。无法保证的部分资源必须保留在提供者Owner并保持获取任务未终结，直到能交租约/可跟踪失败Job；不得throw后遗失。Open返回Job+Error是部分失败闭包，后续直接清理不Extract。仅RequestCancel只以线程安全标记记录意图，不同步调用可能阻塞的native取消/销毁，不新开无法追踪的后台任务；native任务返回/抛取消前必须已真实退出相关访问。

释放Owner账按job(s)→coordinate→frame→额度逐项，Dispose ValueTask转换Task只一次并保存；任务未返回时Retry仅等待；已失败任务重试幂等原对象，全部成功后F2D-013仍保持为最终错误。未知Owner不能另开后台重试再遗忘。服务Dispose未Drained明确抛且不释放依赖，Close/Wait/Retry有限，无线程强杀。源RequireCurrent在阶段与封口前核期限/版本/撤销，失败F2D-018；释放后不再访问。Map批量同长度/序/单位，域外F2D-005，Image目标不借coordinate。

### A.4 建议契约与评价

```csharp
public enum RecommendationStatus { Recommended=0, Abstained=1, Cancelled=2, TimedOut=3, Faulted=4 }
public enum TruthKind { Edge=0, Pair=1, Primitive=2 }
public sealed record TruthObservation(
    string Id, string WorkId, TruthKind Kind, Point2D First, Point2D? Second,
    PrimitiveGeometry? Geometry, double? LineEvaluationSpan, AssetRef TruthSource);
public sealed record RecommendationSample(string Id, Features2DRequest Request,
    AssetRef AnnotationSource, bool NegativeConfirmed, ImmutableArray<TruthObservation> Truth);
public sealed record ParameterCandidate(string Key, CaliperOptions? Caliper, XldOptions? Xld);
public sealed record EvaluationPolicy(
    double MatchTolerance, double MissWeight, double ExtraWeight, double ErrorWeight,
    double MaxMissRate, double MaxExtraRate, double MaxMeanError, long MaxWorkingSetBytes);
public sealed record RecommendationRequest(
    string Id, Features2DRequest BaseRequest, ImmutableArray<ParameterCandidate> Candidates,
    ImmutableArray<RecommendationSample> CalibrationSamples,
    ImmutableArray<RecommendationSample> ValidationSamples,
    EvaluationPolicy Policy, int MaxEvaluations, long MaxResultBytes, DateTimeOffset DeadlineUtc);
public sealed record WorkEvaluation(string WorkId, int Requested, int Matched,
    int Missed, int Extra, int Ambiguous, double? MeanError);
public sealed record SampleEvaluation(
    string CandidateKey, string SampleId, bool IsValidation,
    int Requested, int Matched, int Missed, int Extra, int Ambiguous,
    double? MeanError, double? Loss, ImmutableArray<WorkEvaluation> Works, Features2DResult Result);
public sealed record CandidateEvaluation(
    string Key, bool Eligible, double? CalibrationLoss, double? ValidationLoss,
    ImmutableArray<SampleEvaluation> Samples, ImmutableArray<Features2DError> Errors);
public sealed record RecommendationResult(
    RecommendationStatus Status, AssetRef BaseProfile, ParameterCandidate? Recommended,
    ImmutableArray<CandidateEvaluation> Evaluations, ImmutableArray<Features2DError> Errors);
public enum RecommendationPhase { Running=0, Draining=1, Terminal=2 }
public sealed record RecommendationSnapshot(string Id, RecommendationPhase Phase,
    ImmutableArray<string> PendingOperationIds, RecommendationResult? FinalResult);
public interface IFeatures2DRecommender {
    RecommendationSnapshot? GetRecommendation(string recommendationId);
    bool Cancel(string recommendationId);
    Task<RecommendationResult> RecommendAsync(
        RecommendationRequest request, IProgress<Features2DEvent>? progress,
        CancellationToken operationCancellation);
}
```

具体类构造`Features2DRecommender(IFeatures2DService service, TimeProvider timeProvider)`，不Dispose宿主service。仅一个Recommend在途，重复推荐ID同规范digest共Task、不同内容F2D-016；保持1条推荐在途/最后结果，超过则F2D-009，旧ID重用由宿主禁止。样本/真值/候选ID均唯一非空，真值WorkId存在且类型与该次请求输出一致。样本组合顺序执行；每次OperationId=`recommendationId/candidateKey/sampleId`（各段Uri.EscapeDataString），AttemptId同该ID，Generation仍取Frame。组合/profile变更对完整Profile（仅把顶层Asset字段写N以排除自引用，其它包括MethodAsset/Qualification均保留）按A.1规范生成hash；新Asset.Id=baseId+"/"+Uri.EscapeDataString(candidateKey)，Revision=hash，Sha256=hash，不沿用旧hash；样本须绑定真实Frame/Support/坐标/Method资格，新参数仍在方法已资格范围。

边误差=点欧氏距离（Image px）；pair=max(First误差,Second误差)，不能交换两端；primitive在同GeometryContext/类型匹配，line=max(|Dist差|,LineEvaluationSpan×angleDistanceπ)，circle=max(中心欧氏差,|r差|)，ellipse=max(中心差,|a差|,|b差|,truth.a×angleDistanceπ)，仅双方NearCircle不可观测时略角项。line先按§6.3单位化，再与truth法向点积对齐符号并同翻Dist，LineEvaluationSpan>0；真值独立来源且单位一致，不能从本次结果生成。RawContour本版不参与建议真值，XLD建议需Primitive；E2 diagnostic edges不算pair分母；若同时请求pair+Fit，建议一次固定TruthKind，禁止混单位/重复计数。

EvaluationPolicy.MatchTolerance>0，各rate∈[0,1]、MeanError≥0、working-set>0，权重非负和>0。每sample requested=truth数、denominator=max(1,requested)、matched唯一允许图边数，miss=未唯一truth、extra=未唯一candidate；Ambiguous为多解连通分量数。误差均值仅matched>0有效；正样本无匹配组合不合格，Loss=null；NegativeConfirmed=true要求Truth.Empty且AnnotationSource有效，合法负样本误差项为0但MeanError=null。正样本要求NegativeConfirmed=false、Truth非空且独立来源。每样本truth数不得超过计划输出work数×MaxCandidatesPerWork的checked上界，超限整体拒绝，不截断标注。全部工作完整/无技术或资格错误/无截断（允许F2D-006/007语义诊断），且MaxMissRate/MaxExtraRate/MaxMeanError/资源门通过才Eligible；以denominator加权汇总分别校准/验证Loss，所有rate与L均用同一denominator（负样本miss为0、extra/count），负样本不检MaxMeanError但必须过MaxExtraRate门。验证只作门/报告，按校准Loss再Key排序选唯一推荐。有限组合全跑完才可Recommended，任何来源/真值缺失整体Abstained，不用最终资格留出样本优化。

Recommend取消/期限停止派发并取消当前子operation，已派发Task待真实排空后返回非推荐状态；若native未结束，推荐Task仍pending，但子OperationId可由固定规则GetOperation，宿主持有service进行有限Wait/Close/Retry。GetRecommendation从推荐器自己的派发账返回实际已准入且未terminal的子OperationIds，不依赖可丢进度事件；正在提交尚未准入的子Task也保留在推荐器Owner中，Phase=Draining，待接纳/拒绝后归并。Cancel只作用本推荐及其已派发子请求，幂等、不取消service其它operation。GetRecommendation未知null，最后结果有界保留。不能只根据PendingOperationIds空就判推荐结束，必须Phase.Terminal且推荐Task完成。不在服务内再建隐藏Owner/释放队列。RecommendationRequest.MaxResultBytes>0；预检checked(组合数×各样本Budget.MaxResultBytes之和+评价元数据固定编码大小)须≤推荐MaxResultBytes，否则整体Abstained/F2D-019，不执行一半后丢评价。推荐结果总容量按同A.1逻辑编码≤该上限，组合×样本有界；Evaluation只引用已完成托管结果（所有权随子Execute结果转给推荐调用者），服务缓存份额单独受Options上限；二者不复制同一份数组，不在后台无界收集。BaseProfile过期只阻宿主采用，不改运行值。

### A.5 可选UI公开挂接（仅U1；Core无WPF）

以下接口形状在`Asun.Modules.Features2D.Ui.Wpf`，使用Core类型及BCL；已有公共视口通过实现此接点挂接，不依赖其私有VM/SDK。

```csharp
public sealed record EditorPermissions(bool CanEdit, bool CanRun, bool CanRecommend, bool CanViewEvidence);
public sealed record EditorSelection(string WorkId, string? CandidateId);
public sealed record EditorOverlay(FrameRef Frame, ImmutableArray<WorkResult> Works, EditorSelection? Selection);
public interface IFeatures2DViewport {
    void Show(EditorOverlay overlay);
    void Clear();
    event Action<EditorSelection>? SelectionChanged;
}
public sealed record EditorBinding(
    string AttachmentId, long Epoch, IFeatures2DService Service,
    IFeatures2DRecommender Recommender, IFeatures2DViewport Viewport,
    Features2DRequest Draft, EditorPermissions Permissions, string Culture, string ThemeName);
public sealed record EditorOwnerSnapshot(ImmutableArray<OperationSnapshot> Operations,
    RecommendationSnapshot? Recommendation);
public interface IFeatures2DDetachTicket {
    string AttachmentId { get; }
    long Epoch { get; }
    EditorOwnerSnapshot Query();
    ValueTask<DrainReport> WaitAsync(TimeSpan timeout, CancellationToken waitCancellation);
    ValueTask<DrainReport> RetryReleasesAsync(TimeSpan timeout, CancellationToken waitCancellation);
}
public sealed record EditorDetachResult(DrainStatus Status, IFeatures2DDetachTicket? Ticket);
```

`Features2DEditor`为WPF Control，公开无参构造；公开方法固定：
`void Attach(EditorBinding binding)`、
`void ReplaceDraft(Features2DRequest draft)`、
`void UpdatePermissions(EditorPermissions permissions)`、
`void SetRecommendationRequest(RecommendationRequest request)`、
`void SetCulture(string culture)`、
`ValueTask<EditorDetachResult> DetachAsync(TimeSpan timeout, CancellationToken waitCancellation)`；
事件`event Action<RecommendationResult>? RecommendationAvailable`、
`event Action<EditorSelection>? SelectionChanged`、
`event Action<Features2DRequest>? DraftChanged`、
`event Action<Features2DResult>? ResultAvailable`。
入口须在控件Dispatcher调用，async等待不阻Dispatcher；非法文化/epoch/null/未detach再次Attach抛ArgumentException/InvalidOperationException且不改原binding。源切换、同源ReplaceDraft、回执键、专用推荐器和根Owner关闭按§8.5；epoch须正数且每次重新Attach严格增加，ticket未Drained不得复用同控件再次Attach。Culture首版支持zh-CN/zh-TW/en-US，完整本模块文字由§8.4.1～5同UI DLL资源提供；新增文化先在此目录注册完整资源并同步支持声明，宿主只调用既有SetCulture，不需补词表或使用未定义的资源注入API。ThemeName按宿主现有主题，主题错误回宿主默认并诊断，不重设系统主题。

DetachResult.Drained时Ticket=null；未知Ticket非空，ticket持有本binding的operation Tasks、IDs、service借用引用、等待/失败释放账与本UI回调解除责任。Query返回活跃及自持终态，不依赖服务旧回执逐出；Wait/Retry只本IDs，借用service不能Close/Dispose共享依赖。票据由宿主接收后控件可移除视觉树，Owner仍唯一在ticket，重复Detach返回同ticket，不新建第二Owner。票据还持有本UI推荐Task/推荐器借用与RecommendationId；先Cancel推荐停止后续派发，再通过GetRecommendation取得当前PendingOperationIds定向Retry，提交尚未返回也保持未知，推荐Task与所有执行Task均完成/已释放才Drained；不能只等待启动时operation列表遗漏后续子请求。SetRecommendationRequest必须BaseRequest.Profile/Frame与当前Draft精确匹配、CanRecommend=true，失配拒绝且不改原输入；建议可用与采用由basehash和当前权限再核。票据Drained后解绑所有订阅/清overlay，不销毁宿主视口/服务；未知不得遗忘。权限/epoch/语言变化按§8，ResultAvailable是可缺投影，不能获得质量提交权。
