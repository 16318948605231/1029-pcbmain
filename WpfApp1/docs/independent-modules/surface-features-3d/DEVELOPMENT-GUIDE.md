# surface-features-3d 三维表面特征与拓扑开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`SF-C1, SF-C2`

- 模块 ID：`IM-034`；来源：`PKG-031`
- 状态：SF-C1、SF-C2 `ModuleCoreImplementationReady`（仅规格准备，主控2026-10-10接收）；SF-A1/SF-W1新增指导内容限定接收（主控2026-10-11），切片仍 `PreparationIncomplete / NotReady`；不授予纯CoreReady或真实运行/生产资格
- 指导版本：`0.5.0-prep`
- 复审记录：场景与外部消费者双视角复审（2026-10-09）；保留 2026-10-04 的场景断言
- 技术基线：C# / .NET 10；核心可脱离 WPF 运行；HALCON 目标运行时 26.05；通过 `ImageLibDotNet` 公共接口使用 AsunImage
- 规划消费者：高度与参考面工具、通用 3D 量测工具、连接器几何工具、焊料/表面候选工具
- 当前结论：全部当前批准范围与本轮明确需求的可决定软件设计已闭合，定位见§18；SF-C1/C2原接收保持，外围/描述/建议切片仍PreparationIncomplete。文档准备完成不等于代码、真实运行或生产Ready

本文的模块局部设计以附录 A 为具体类型与调用基线，正文说明处理与验收；平台 Contract/Schema/State/Owner 的映射仍由原 Owner 串行采纳。主控已按DEV-GOV-010 §3.1接收SF-C1（快照/校验/身份/服务生命周期/冻结端口下受控测试Host）与SF-C2（纯索引Topology）为 `ModuleCoreImplementationReady`，仅表示规格准备，不表示代码已实现、测试已运行或产品/生产准入；本轮不写代码。不得另造平行DTO、状态机或事实库。

## 1. 职责与禁止边界

### 1.1 模块职责

模块接收已经采集并声明坐标、单位和有效域的单个 3D 表面对象，返回不可变的几何候选和逐点/逐面的来源映射。能力包括：

1. 有效点筛选、属性阈选、裁切和显式采样；
2. 法向估计及法向有效性报告；
3. primitive 候选拟合（由调用者指定允许类型）；
4. 连通组件提取；
5. 三角化、边界/洞/截面支撑信息；
6. 在独占工作模型上计算点到表面的距离属性，并读回映射；
7. 输出输入快照、实际方法、质量、资源和诊断证据。

### 1.2 明确禁止

- 不拥有双模型或多模型配准；配准由 `PKG-060/IM-033 registration-3d` 负责。
- 不定义参考面是否适合某个产品、工艺或量测；参考面资格由 `PKG-029` 负责。
- 不定义高度、面积、体积、公差、缺陷类别、PASS/FAIL、质量放行或人工复判；具体量测由 `PKG-030`，工艺与质量由调用方负责。
- 不执行采集、运动、光源、设备命令、数据库提交、报告发布或 MES 通讯。
- 不把 PCB、PCBA、SPI、AOI、点胶、涂覆、连接器料号、焊料规则写入核心类型或默认值。
- 不把显示 mesh、平滑结果、非空句柄、score 或单次拟合成功当作生产事实。
- 不读取或修改 AsunImage 内部；不从 ServiceLocator、产品 ViewModel、私有表或隐藏窗口取得依赖。

调用方负责流程顺序、目标关联、配方和工艺解释、质量放行、持久化、设备副作用以及最终事实 Owner。模块只返回其拥有的几何事实和明确的 `Unknown/Rejected` 原因。

### 1.3 本模块实现文件绑定

首个纯 Core 切片绑定仓库相对路径 `src/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Core/Asun.Modules.SurfaceFeatures3D.Core.csproj`、唯一测试工程 `tests/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Core.Tests/Asun.Modules.SurfaceFeatures3D.Core.Tests.csproj`，根命名空间为 `Asun.Modules.SurfaceFeatures3D`。Core 用 `Microsoft.NET.Sdk/net10.0`；测试用同 SDK/TFM、`OutputType=Exe`，只引用该 Core 和 .NET BCL（含 System.Collections.Immutable），无测试 NuGet 包、WPF、HALCON、设备或数据库。工程尚未创建。本轮仅改本文，不据本节获得工程写权限；后续获准的 SF-C1/SF-C2 也只允许这两个目录，不改共享 solution/build/项目引用。HALCON 适配器、WPF 与宿主集成另准入。

未来验证命令固定为 `dotnet build src/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Core/Asun.Modules.SurfaceFeatures3D.Core.csproj -c Release` 和 `dotnet run --project tests/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Core.Tests/Asun.Modules.SurfaceFeatures3D.Core.Tests.csproj -c Release`；不是 `dotnet test`。入口覆盖 §12.1 的适用断言；失败、未完成、必需项跳过为非零并输出 case ID。受控Core固定wall-clock期限为每case **10s**、整suite **120s**、外层进程watchdog **180s**；包含业务与cleanup观察时间，每case内部各次等待共享剩余10s，不能每次重置。虚拟TimeProvider只驱动模块deadline/取消场景，wall watchdog使用TimeProvider.System/单调计时，不能推进虚拟时钟代替实际退出。未闭合或资源Unknown不许返回0；180s触发强止仅为测试进程遏制，记录删失/Unknown及非零，不称成功归还。这些是受控Core测试限额，不是生产SLA；性能Profile仍按§13由消费者提供。Benchmark仍用该Exe的 `--benchmark <Profile路径>`，不另建工程。本次不创建Profile/测试文件或运行上述不存在工程。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.SurfaceFeatures3D.Core` 与 `Asun.Modules.SurfaceFeatures3D.Halcon` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.SurfaceFeatures3D.Wpf`（可选控件）可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。SF-C1/SF-C2（仅 BCL）为这条门禁的天然验证面，可在无 WPF、无 HALCON runtime、无 AsunImage 程序集的宿主中完整运行。

**Blazor/Web 宿主中的 3D 特征展示**：Web 端需要"展示 primitive 拟合结果、法向分布、连通组件统计与点到面距离"时，服务端调用 Core 取得不可变几何候选与逐点来源映射，再投影到浏览器。约束：
- 浏览器端只渲染标记与数值，不重新执行 `fit_primitives_object_model_3d`、不自行估计法向、不重新分割连通组件
- §1.2 的"不把显示 mesh、平滑结果或单次拟合成功当作生产事实"在 Web 投影中同样成立：前端不得把 primitive 候选直接显示为已确认的产品几何
- primitive 类型（`plane/sphere/cylinder`）和拟合残差随结果一起投影，浏览器不推断 `all` 模式下 HALCON 选择了哪种 primitive（§1.1 与 §6 已核对：`all` 只返回 HALCON 认定最小二次残差的一种，不保留竞争候选）

**AI 推理 Tiling 适配**：本模块的几何特征（法向、曲率、primitive 参数）可作为 `ai-inference` 3D 异常检测的辅助输入，但本模块不参与推理分块编排。适配约束：
- 推理所需的 tile 由 `surface-data` 的表面快照驱动，本模块不实现 `RequestTileAsync`，不持有推理 tile 租约
- 三态仲裁对本模块输出的几何特征"异常"判定只作观察，不覆写已发布的 primitive 候选事实

**HALCON 备选交叉验证适用性（表面特征链）**：本模块已有 Open3D oracle（`PointCloudSegmentation.cpp`/`PointCloud.cpp`，见 §17 已读证据）。约束：
- `fit_primitives_object_model_3d`（`plane/sphere/cylinder`）在 HALCON 路线与托管参照路线上按**同一 Golden 数据集**双跑：拟合参数（平面法向/中心/截距、球心/半径、圆柱轴/半径）、内点数、残差（单位已核：`primitive_rms` 是 quadratic residual，非标准 RMS，见 §17 已读 26.05 `fit_primitives_object_model_3d.html` SHA-256 `ae7ac101f3f1...`）逐项比对，差值超容差即 CI 失败
- **已知的必然差异，不得抹平**：
  - `all` 模式只返回 HALCON 认定最小残差的一种；托管参照须对三种分别拟合再取最小，两路的"最小"判定可能不同；双跑门禁只对**单类型请求**（`plane`/`sphere`/`cylinder`）设门禁，`all` 模式的结果标为仅诊断
  - `surface_normals_object_model_3d` 使用 PCA 估计法向；PCA 法向方向有符号歧义，托管参照须按相同定向规则（`invert_normals` 语义，见 §6 已核对 `surface_normals_object_model_3d.html`）修正，不得假定两路方向自动一致
- **Open3D oracle 在本模块的具体落点**：
  - `PointCloudSegmentation.cpp`（SHA-256 `44487a05...`）的 `GetPlaneFromPoints`（最大余子式法向）：支撑"HALCON plane 拟合的法向定义需要独立验证"，两者算法不同，故不用 Open3D 值直接替换 HALCON 值
  - `PointCloud.cpp`（SHA-256 `9d31ff09...`）的 `EstimateNormals`（PCA）：支撑"法向退化时 Open3D 回填旧值/+Z 方向"这一已知限制，用于设计拒绝/边界反例
  - Open3D 测试中 `SegmentPlane/Deterministic`（`tests/geometry/PointCloud.cpp` SHA-256 `b8041cb7...`）：支撑"固定随机种子下平面拟合可重复"这条不变量，与 §1.1 第 7 条"模块提供可回放所需的操作状态"对齐
- HALCON 仍是生产路线；Open3D 仅作语义参照，不引入生产依赖

## 2. 架构、依赖与适配边界

```text
视觉工具/检测应用/回放宿主
        | 公开 SurfaceFeature 请求、取消、结果
        v
surface-features-3d Core（无 UI、无产品依赖）
        | 端口：I3dSurfaceBackend、IMemoryAdmission/IResourceLease、IDiagnosticsSink
        v
AsunImage.ImageLibDotNet / HALCON 26.05 适配器
```

表面数据、坐标几何和帧资源（`PKG-027/007/006`）经宿主映射为本模块局部深冻结 `SurfaceSnapshot`，不引用其私有实现。宿主在上游 lease 有效期间复制并 Create 快照，再归还上游 lease；031 不留产品帧/SDK handle。内存预约 lease 注入本模块，native 工作模型只由 backend 创建与释放；具体 Owner 见附录 A.4。

### 2.1 后端适配器

`I3dSurfaceBackend` 的模块局部端口形状见附录 A；真实 HALCON 适配切片尚未准入。适配器必须：

- 将 `SurfaceSnapshot` 映射为独占的 `HObjectModel3D` 工作句柄；原始句柄不跨 Core 边界；
- 将候选操作映射到目标 HALCON 26.05 的官方算子，并在启动时报告能力版本；
- 读回实际对象类型、点/面数量、扩展属性、有限性和源索引，不用“调用无异常”推断成功；
- 对会修改对象扩展属性的操作（例如 `distance_object_model_3d`）只在本请求的私有工作模型上调用；
- 适配器未提供取消传播时，返回 `CancelRequested` 后继续排空，不能提前释放 native 句柄；
- 把 native 异常、错误号和缺失能力映射为稳定模块错误码，并保留原始诊断文本。

### 2.2 HALCON/AsunImage 路线核对

目标运行时固定为 HALCON 26.05。项目内入口为 [`halcon算子手册/operators`](../../../halcon算子手册/operators/)，页面标题为 `HALCON Operator Reference 26.05.0.0`。AsunImage 是该版本薄封装，全部算子通过 `ImageLibDotNet.cv2` 调用；不重复核验“封装是否包含”，不直接引用 `HOperatorSet/halcondotnet.dll`。下表以算子语义定义适配，不把历史实例方法拼写当作公开 C# 签名。仅实际参数类型、重载或封送有歧义时查公共签名或消费编译，不读内部：

| 能力 | HALCON 算子（均经cv2） | 语义/约束（非C#签名声明） |
|---|---|---|
| 属性筛选 | `select_points_object_model_3d` | 多条件取交集；裁切后核拓扑与源映射 |
| 采样 | `sample_object_model_3d` | fast按3D间距、accurate系按邻域、xyz_mapping按像素、furthest_point按目标点数，不混量纲 |
| 法向 | `surface_normals_object_model_3d` | 原XYZ不变；零/非有限法向无效，不填+Z |
| 平滑 | `smooth_object_model_3d` | method只有mls/xyz_mapping/xyz_mapping_compute_normals，派生坐标不替原始 |
| primitive | `fit_primitives_object_model_3d` | cylinder/sphere/plane/all；all只返回一种；对象可能无primitive |
| 连通 | `connection_object_model_3d` | distance_3d/angle/distance_mapping/mesh/lines，参数与前置按§4.2 |
| 三角化 | `triangulate_object_model_3d` | polygon→polygon_triangulation；规则mapping→xyz_mapping；无mapping合资格法向→greedy，否则拒绝。information不是质量；首发无implicit |
| 距离 | `distance_object_model_3d` | 会写 From 对象扩展属性；必须使用私有工作模型 |
| 映射/转换 | `object_model_3d_to_xyz`、`xyz_to_object_model_3d` | 2D mapping 与物理点云不可混用 |
| 统计/显示 | `get_object_model_3d_params`、`render/disp` | 显示和查询只作投影，不能替代质量证据 |

目标页面未定义的参数/返回属性不得猜测；本模块未开放或前置不足的组合为 `CapabilityUnavailable`。中断传播必须通过真实适配验收确认；无法传播时采用等待 native 返回的排空语义，不把它解释为算子缺失。

### 2.3 本轮公共边界复核结论

适配器经 `cv2` 使用下表 HALCON 算子，并用 `copy_object_model_3d/clear_object_model_3d` 或公共资源能力管理私有工作对象。C# 拼写/重载只在消费编译确有歧义时定位；不设置依赖安装、适配版本或许可证准入待办。因而：

1. Core 不向调用方暴露 `HObjectModel3D`，适配器内部负责 `Clone`/工作副本、`Dispose` 和属性读回；
2. `distance_object_model_3d` 把距离写入 From 对象扩展属性，必须以独占副本隔离；每请求使用不同工作对象，不共享 `&distance`；不依赖未经消费编译确认的 C# 返回类型；
3. `TriangulateObjectModel3d` 的 `out information` 是算法信息，不等于质量/封闭性/可量测资格；`FitPrimitivesObjectModel3d` 返回对象可能为空 primitive，必须再用 `GetObjectModel3dParams` 检查；
4. HALCON 页面说明若算子支持取消/超时/中断，不代表当前 C# 封装已自动传播。适配器必须通过目标运行时可验证的控制边界接入，无法确认时只能提供“请求取消后排空”的保守语义。

本轮核对的 26.05 页面为：`halcon算子手册/operators/select_points_object_model_3d.html`、`sample_object_model_3d.html`、`surface_normals_object_model_3d.html`、`smooth_object_model_3d.html`、`fit_primitives_object_model_3d.html`、`connection_object_model_3d.html`、`triangulate_object_model_3d.html`、`distance_object_model_3d.html`、`prepare_object_model_3d.html` 和 `get_object_model_3d_params.html`。这些页面是算法语义依据，不是对本模块已实现或已通过实机验证的声明。

## 3. 数据契约（候选，待原 Owner 采纳）

### 3.1 `SurfaceSnapshot`

输入必须是附录 A 的深冻结快照，至少包含：

| 字段 | 类型/单位 | 约束 |
|---|---|---|
| `SurfaceId` | 非空稳定标识 | 与源文件/帧/版本绑定；不使用 native handle 作为身份 |
| `Revision` | `long > 0` | 同一身份的内容修订，计算开始后不可变 |
| `ContentHash` | SHA-256 小写64位 | 模块 Snapshot factory 对局部规范内容计算；上游hash另存 EvidenceRef，不假定序列化相同 |
| `CoordinateFrame` | 非空 frame 标识 | 变换方向由调用方声明；本模块不估计配准 |
| `LengthUnit` | 枚举 `Meter/Millimeter/Micrometer` | 一个快照只能有一个物理长度单位；单位转换须记录来源 |
| `X/Y/Z` | `double` 序列 | 长度相同；仅允许有限值进入有效点集；原始无效点保留原因 |
| `Validity` | 位集/掩码 | 与原始点一一对应；无效不以 Z=0 替代 |
| `SourceIndex` | `int >= 0` 序列 | 派生点必须保留贡献索引或明确 `MappingUnavailable` |
| `Triangles/Polygons/Edges` | 稳定索引集合，可空 | 缺面不能当作可量体积拓扑；洞和断边单列 |
| `AcquisitionRef/CalibrationRef` | 版本+hash 引用，可选 | 若调用用途要求标定而引用缺失，结果只能 `NotEvaluated` |

点、法向、扩展属性和面索引由输入校验一次性检查。`Validity=false` 的原始 XYZ 可含 NaN/Inf，保留原因并在进入 native 前排除；`Validity=true` 的非有限坐标拒绝 `S3D-004`。有效零坐标合法。Source 空顶点/全无效为 `S3D-006`；Distance 的 Primitive Target 可仅含 primitive 无顶点。“仅 polygon”指有顶点和 polygon 索引但无 triangles。原始 SourceIndex 非负且唯一；不同源索引的重合坐标合法，不能隐式去重。派生点贡献列表可在输出间复用源索引；派生 Geometry.SourceIndex 为本派生版本唯一局部索引，真实来源在 SourceMapping，不把它假装原始索引。面/边引用无效点不能送 native；裁切面缺失必须计数。

快照还含独立 NormalValidity、逐点属性、规则 MappingRow/Column/Size、来源域及连续支撑 EvidenceRef。mapping 数量同点数、有效像素唯一且在范围；缺 mapping 不重建虚假组织关系。反光/遮挡原因由上游输入，不从 Z 推断。冻结 factory 克隆全部序列及嵌套属性，不信任外部可写缓冲；布局形状和 import hash 比较见附录 A.1。

### 3.1.1 单位与坐标闭合

托管输入与结果使用快照单位；native模型换米比例Meter=1、Millimeter=1e-3、Micrometer=1e-6。长度参数同换算，法向/pixel/无量纲不变；输出长度乘逆比例，溢出/下溢成非法正参数拒绝S3D-004。native_rms未确定单位保持NativeUnknown不换，见A.3。面积/体积不输出。角度逐参数映射；mls_abs_sigma/greedy fixed radius的native值为米。Distance Target同frame、各自换米；无Pose字段，不自行配准。宿主先通过坐标模块生成同frame新快照与证据。

### 3.2 `SurfaceFeatureRequest`

模块局部形状如下；`Operation` 不另作字段，由参数的具体类型唯一决定，防止操作与参数冲突。完整定义见附录 A：

```csharp
public sealed record SurfaceFeatureRequest(
    string RequestId,
    SurfaceSnapshot Surface,
    SurfaceFeatureParameters Parameters,
    TimeSpan Timeout,
    ResourceBudget Budget,
    SurfacePurpose Purpose,
    string ContractRevision,
    string ProfileRevision);
```

`Purpose` 仅描述调用用途（`DatumCandidate/MeasurementSupport/DisplayDerived`），不得携带产品判定。取消 token 只从执行入口传入，不序列化在请求中。CalculationIdentity 的唯一编码见 A.1，不使用反射或文化相关格式。首发不缓存结果；相同身份不同 RequestId 可显式重复运行，不承诺 native 字节一致。同实例 RequestId 不可重用直到关闭，重复 `S3D-015`。快照深冻结；本模块不订阅产品当前修订、不擅自标旧结果过期，宿主按revision丢弃迟到投影。

### 3.3 参数单位、范围、默认值

以下是实现前必须冻结的安全候选范围。默认值不是生产工艺默认值；若没有 Profile 来源，宿主必须显式传入并在结果中回显。

| 参数 | 类型/单位 | 候选范围与默认 | 适用操作 |
|---|---|---|---|
| `AttributeMin/Max` | `double`，属性原单位 | 有限值且 `min <= max`；无默认 | 属性筛选 |
| `SamplingMethod` | 枚举 | `Fast/FastComputeNormals/Accurate/AccurateUseNormals/XyzMapping/XyzMappingComputeNormals/FurthestPoint/FurthestPointComputeNormals`；无隐式默认 | 采样 |
| `SamplingDistance` | `double`，方法定义的长度或像素 | `>0`，上限由 `Budget.MaxOutputPoints` 和 Profile 冻结；无默认 | 采样 |
| `NormalMethod` | 枚举 | `Mls/Triangles/XyzMapping`；无默认 | 法向 |
| `SmoothMethod` | 枚举 | 仅 `Mls/XyzMapping/XyzMappingComputeNormals`；无默认；不支持 `Median` 别名 | 平滑 |
| `PrimitiveKind` | 单值枚举 | 仅 `Plane/Sphere/Cylinder/All`；不拟合 Line/Point；无默认 | 拟合 |
| `FitAlgorithm` | 枚举/字符串 | 仅 `LeastSquares/LeastSquaresHuber/LeastSquaresTukey`；无默认；plane 三种算法结果按 HALCON 页面相同处理 | 拟合 |
| `ConnectionFeature` | 枚举 | 仅 `Distance3D/Angle/DistanceMapping/Mesh/Lines`；无默认 | 连通 |
| `ConnectionValue` | nullable double，3D距离为输入长度、mapping为pixel、角度rad | 距离 `>0`，Angle `0<value<=π`，Mesh/Lines 必须null；无默认 | 连通 |
| `TriangulationMethod` | 枚举 | 仅 `PolygonTriangulation/XyzMapping/Greedy`；须等于 §4.1 由输入绑定的方法；首发无 Implicit | 三角化 |
| 保孔策略 | 固定行为 | `xyz_mapping_max_area_holes=0`；greedy 关闭补洞/形态学/小面删除；无开放的 false 选项 | 三角化/截面 |
| `MaxDistance` | `double`，输入长度单位 | `0` 表示不截断；`>0` 产生截断语义，不能当实测值 | 距离 |
| `Timeout` | `TimeSpan` | `>0` 且不超过宿主预算；默认无模块默认，由宿主传入 | 全部 |
| `MaxInputPoints/MaxOutputPoints/MaxFaces` | `int` | `>0`；默认来自 `ResourceBudget`，缺失即拒绝 | 全部 |

`connection` angle 使用 rad；greedy orient/latitude 使用 degree。像素参数仅用于 mapping 路线；FurthestPoint 使用正整数目标点数，不能塞入 SamplingDistance。MLS sigma 用附录 A 的二选一强类型：绝对长度或相对无量纲值，同时给出拒绝。参数规范化结果（含固定 generic 参数和实际方法）写入结果；未知参数/跨方法参数拒绝，不透传任意字典。范围是算法校验，不是工艺阈值；各方法的必填值与唯一映射见 §4.2。

## 4. 操作语义与处理顺序

每个请求都执行以下固定顺序，任何阶段失败都返回显式终态：

1. **Validate**：检查契约版本、来源 hash、单位/坐标、有限性、索引、预算、能力和取消状态。
2. **Capture**：捕获深冻结输入的 ID/revision/hash、方法/参数、后端与证据引用；获得内存预约lease。
3. **Prepare**：克隆或创建独占 native 工作模型，建立源索引映射；不得修改输入快照。
4. **InputDomain**：仅压缩无效点并建立工作下标到原SourceIndex映射；Select请求执行显式条件，其他请求不偷偷裁切或滤波。
5. **Derive**：仅执行请求参数指定的一个操作；处理链由调用方使用独立请求/派生快照组合，每派生版本有父身份和映射。
6. **Inspect**：读取实际点/面数、属性、模型类型、法向有限性、洞/边界、残差和覆盖；不以非空结果代表成功。
7. **Freeze**：构造不可变结果和证据，写入 `CalculationIdentity`、资源峰值、阶段耗时和停止原因。
8. **Release**：native 调用真正返回后释放工作模型、索引和租约；取消不跳过排空。

滤波、平滑和采样永远生成新版本。合法零坐标不能被删除；零法向不能归一化为 NaN 或默认 +Z。三角化只能连接有观测支撑的邻域，不跨无效孔洞、断面或不相连组件补面。primitive 结果必须包含实际类型、参数、支撑点索引、残差和退化原因。

### 4.1 具体路线、备用路线与不支持条件

| 操作 | 首选路线 | 备用/降级条件 | 必须拒绝或标记不支持 |
|---|---|---|---|
| 属性筛选/裁切 | `select_points_object_model_3d`；首发按 `point_coord_*`、`point_normal_*` 或登记逐点属性，多个条件取交集 | 邻域阈选/统计去离群不在首发DTO；以后独立冻结 `neighbor_distance/num_neighbors` 定义才可开放 | 未声明属性、长度不符；把第K距离当K均距；把 `num_neighbors_fast` 当精确半径规则 |
| 点采样 | `fast` 保留按输入顺序的代表点；需要抗局部密度变化时选 `accurate`；有法向约束时选 `accurate_use_normals` | 有 XYZ mapping 且目标是图像域降采样时选 `xyz_mapping`；仅需固定点数时选 `furthest_point` | 把 `xyz_mapping` 的像素步长解释为 mm；派生点无贡献映射却用于精密量测 |
| 法向 | `surface_normals_object_model_3d`：规则点云优先 `xyz_mapping`，三角面优先 `triangles`，非规则点云选 `mls` | 法向稀疏/零向量时返回 `InsufficientSupport`，可由宿主重新采样或改变独立参数后重算；不自动改方向 | 不存在可用邻域/面；将 MLS 的 `force_inwards` 当作产品上方向；以零向量归一化补值 |
| 平滑 | `smooth_object_model_3d` 的 `mls` 适合非规则点集；有 mapping 时用 `xyz_mapping` 或 `xyz_mapping_compute_normals` | 只为显示可使用派生平滑；量测支撑须保留原始版本并由调用方选择 | 使用未列出的 `Median` 方法；无 mapping 调用 xyz_mapping；以平滑结果覆盖实测高度 |
| primitive | `fit_primitives_object_model_3d`，显式 `primitive_type=plane/sphere/cylinder/all`；输入须是调用方声明的单 primitive 支撑域 | `all` 只返回最小二次残差的一种，不保留未返回的竞争结果。需比较三种时调用方提交三个单类型请求；plane 的 Huber/Tukey 与 least_squares 相同 | 以点数门代替空间可观察性；无 primitive 仍判成功；捏造未返回的 inlier、竞争候选或置信度；拟合 Line/Point |
| 连通组件 | `connection_object_model_3d`：请求显式指定 `mesh`、`distance_mapping`、`distance_3d`、`angle` 或 `lines`，并声明该路线所需的输入属性/前置派生结果 | 首选属性缺失时以 `S3D-005 CapabilityUnavailable` 拒绝当前请求；若需另一特征，调用方必须提交新的请求、`ProfileRevision` 和 `CalculationIdentity`，不得在运行中切换 | 角度范围不在 0..π；用 `mesh` 处理无三角化点云；把组件数当作目标关联或工艺关系 |
| 三角化 | 已有 polygon 固定 `polygon_triangulation`；带 2D mapping 的组织化深度图固定 `xyz_mapping`；无 mapping 的非组织点云仅在法向资格已满足时固定 `greedy`，否则拒绝 | 不进行运行时方法切换、自动降采样重试或噪声失败后换算法；调用方可显式产生新的输入/Profile revision 后另行请求 | 首发不支持 `implicit`；不得跨遮挡补面、默认补洞或将三角化结果自动视为量测资格 |
| 距离属性 | 请求明确 ExactLinear/ExactKdTree/ExactPrimitive，点/三角分别映射linear/kd-tree，primitive为直接解析求距，不传不适用搜索method；voxel仅显式ApproximateVoxel | 首发预建仅本请求Target工作对象，归还时清理；无跨请求缓存/方法切换 | MaxDistance>0到界值不进入精确统计；signed不支持组合拒绝；共享From写 &distance拒绝 |

训练路线：本模块无训练参数、模型资产或学习后端。噪声/遮挡/退化通过输入资格、采样/法向/拓扑路线和明确回退处理；若未来引入学习式补洞或特征分类，必须拆到 AI 模块并经新的能力、证据和 Owner 审核，不能把“训练”塞入 031。

资源恢复约束：`greedy` 的邻域预取会按 `O(k*n)` 增加内存，超过预算时停止并返回资源错误；不得静默关闭预取、换低资源方法、先 `fast` 采样或重试以改变拓扑语义。精确 `kd-tree` 的预建/失败由请求显式决定；不切换成近似 `voxel`。`voxel` 距离结构只服务明确标记的近似请求，失败即失败。

### 4.2 逐方法参数绑定与反例

下表定义首发支持面。所有业务参数由请求显式给出；标为固定的 generic 值由适配器展开并回显。HALCON 手册 suggested 值不是生产默认；未列入的参数先修订本指导再开放。范围检查还须满足 Budget 与版本能力。

| 操作/参数形状（附录 A） | 绑定与校验 | 输出与关键反例 |
|---|---|---|
| `SelectParameters` | 非空条件集合；多条件取交集。首发仅 XYZ、已有效法向分量及已登记逐点属性，名称/单位与快照一致；闭区间 min≤max。首发不开放字符串拼出的统计去离群器 | 返回原坐标、原 source index、剔除原因，重建点索引并删除引用被剔点的面/边。属性无效值不参与阈选；条件空不是“全选” |
| `SampleParameters` | method 必填；Fast/Accurate 系为正长度；XyzMapping 系为正像素步长；FurthestPoint 系为正整数点数。`accurate_use_normals` 需输入有效法向；compute_normals 类结果仍需法向有效性复查 | Fast 顺序敏感、Accurate 派生位置、FurthestPoint 子集三者不能冒充固定体素。HALCON 未公开精确贡献的路线返回 `MappingUnavailable`，不得以最近点伪造贡献；MeasurementSupport/DatumCandidate 用途拒绝该结果 |
| `NormalsParameters` | method=`Mls/Triangles/XyzMapping` 与输入匹配，不能在执行中选择。MLS 必填 k≥3、order∈{1,2,3}、正 sigma（绝对/相对互斥）、force_inwards；Triangles 不带 MLS 值，XyzMapping 需规则 mapping。MLS 参数按 smooth 页面映射 `mls_kNN/order/abs_sigma/relative_sigma/force_inwards` | XYZ/source index 不变；零/非有限法向无效。原始点有效不等于法向有效。`force_inwards` 仅算法方向，不能授产品上方向 |
| `SmoothParameters` | MLS 同上；mapping 平滑显式 filter=`Median/MedianSeparate`、奇数正 width/height；Median 必须正方形，拒绝偶数，不让 native 默默加一。Method=`XyzMapping` 或 `XyzMappingComputeNormals`；不把 Median 当 Method | 新坐标/新派生 revision，原坐标不变。反光缺点不因邻域平滑变有效；输出保留原有效域交集，不赋补测资格；支持跨断面时见 §4.3 |
| `FitParameters` | 单 PrimitiveKind 与 FitAlgorithm 必填；sphere/cylinder/all 要显式 `0<MinRadius≤MaxRadius`（输入长度单位）；plane 不允许 radius 值。固定 `output_point_coord=true`，有 mapping 时 `output_xyz_mapping=true`；其余 native 默认从 26.05 能力快照锁定并回显，不以手册默认半径过滤工业小目标 | plane 为 Hessian 参数、sphere 为中心+半径、cylinder 为中心+单位轴+半径，保留实际原始参数/extent/rms 与单位。支撑是送入拟合的域，不假称 robust inlier。无 primitive→Insufficient；`all` 实际只返一种 |
| `ConnectParameters` | Distance3D 的正长度换米；Angle 的 (0,π] rad 需合资格法向；DistanceMapping 的正距离为像素、需 mapping；Mesh/Lines 的 Value=null，需相应拓扑。不能把 mapping 距离写成 mm | 组件是几何连通事实；输出各组件 source indices，计入未分配点。组件顺序用最小原 source index 固定，不依 native handle/输出顺序 |
| `TriangulateParameters` | Method 与 §4.1 绑定一致；polygon 无其他参数；mapping 显式非零 ViewDirection 与 MaxViewAngleRad∈(0,π/2]，native 数值按页面 `rad(…)` 的弧度表达；greedy 只开放 fixed 正 Radius（换米），k≥3、OrientToleranceDegrees/LatitudeToleranceDegrees∈(0,90]、VerticalRadiusFactor≥0、OrientationConsistent/FixFlips/PrefetchNeighbors 显式传入 | 固定 `xyz_mapping_max_area_holes=0`、mapping/greedy `output_all_points=false` 并读 `original_point_indices`。greedy 固定 `hole_filling=false`、`mesh_erosion=0`、`mesh_dilation=0`、`remove_small_surfaces=false`、`suppress_timeout_error=false`、`information=verbose`，timeout 取剩余 deadline（秒）；不允许超时中间 mesh 变 Completed |
| `TopologyParameters` | 只消费已存在的 triangle 索引；原始 polygon 要先显式三角化。纯 Core 用无向边 `(minIndex,maxIndex)` 的面关联统计，方向信息保留每面有向边；不改几何 | 关联1面为边界边，2面检查相反方向，>2面为非流形；退化/重复面单列。边界图每节点度2才输出闭合环，度1为开放链、分叉为 Ambiguous。闭合环不自动称“洞”，缺测洞与外轮廓分类仅由 mapping/输入域提供，不猜实体内外 |
| `SectionParameters` | 已有 triangle mesh；PlaneOrigin（输入单位）、PlaneNormal非零有限，经A.2确定正交基再由cv2转换平面pose，z轴等于Normal。不拟合平面、不隐式三角化 | `intersect_plane_object_model_3d`→读 XYZ/lines；返回线段与支撑 mesh hash、平面，不自动连接容差缺口。空交线是 `Completed+Complete/NoIntersection`；相切、共面三角与多重顶点线保留退化说明；未经资格的源面映射标 Unavailable，不编造 source face |
| `DistanceParameters` | 显式 Target 快照同 frame，TargetKind=`Points/Triangles/Primitive`，不使用 distance_to=auto；ExactLinear 支持点/三角，ExactKdTree 支持点/三角（目标预建绑定hash），ExactPrimitive 仅 primitive；ApproximateVoxel 仅点/三角且 Approximate=true，不得与 signed 点点组合。原始 polygon 须先显式三角化，不触发隐式面变换 | signed 需有效且方向有证据的目标法向/面/primitive；开放面符号不等于闭实体内外。对支持的方法固定 store_closest_index=true，voxel 不支持映射；输出每值 `Exact/Approximate/AtLimit/Invalid` 与目标索引。MaxDistance>0 且值达界时保守标 AtLimit，即使恰等界也不纳入精确统计；不输出量测公差或聚合结论 |

HALCON 26.05 的 `xyz_mapping_max_view_angle` 说明以 degree 描述几何区间，而示例/默认用 `rad(60/85/90)`；本模块字段明确为弧度并将数值原样作为 generic 参数，以 0 与 90°视角边界的适配 Golden 验证，避免误把 90 数值传入。缺该验证不宣称 mapping 适配已通过。

### 4.3 邻域尺度、ROI 支撑、孔洞与分块

ROI 是可见输出域；邻域运算的支撑域是显式选定的输入快照，两者分别回显。首发请求不内置操作链：调用方先选域形成新快照，再请求采样/法向/平滑/三角化。核心不会自动“筛选→平滑→法向”。MLS 的 kNN 可跨远距离/台阶，不因 k 小而保证物理半径；不能承诺任意孔边/断面安全。MeasurementSupport/DatumCandidate 的邻域请求必须由调用方先提供连续独立支撑域及资格引用，否则拒绝 `S3D-006`；DisplayDerived 允许派生显示，但结果保持 `NotEvaluated` 用途资格并标明可能跨断面。不得把 native 的成功回填点扩大为观测域。

法向尺度、采样尺度、拟合域和三角半径分别冻结，不从显示 LOD 推导算法参数。对峰值、薄壁、反光缺测、阶梯和孔边以同一原始域比较：有效点/有效法向分母、来源可追溯、峰值保留与跨接面，而非只比 RMS。存在无效孔洞或未知断面时，即使关闭补洞仍不保证 greedy 不跨接；调用方给出独立组件域分别执行，未知连续性结果不得为几何 `Complete`。mapping 的三角边还须在已声明有效域内有邻接支撑；不根据外轮廓凸包授完整性。

首发不开放分块执行、全局自动 kNN、跨块连通合并或并行 native 分片。超大输入按预算拒绝；调用方裁成多个请求只能得到局部结果，不能冒充全局组件/闭环。未来分块切片须明确全局索引、固定半径 halo 或全局kNN、核心区唯一 Owner、跨块面与边去重、孔边不跨接、结果合并顺序与整云对照，先修指导再编码。

曲率边界：normal入口未承诺主曲率属性，segment内部曲率不冒公共输出。已接收Core Contract0.3仍不增加ComputeCurvature；本轮明确需求的规则物理高度图局部曲率由附录D独立Analysis公开入口冻结，使用HALCON二次曲面拟合及明确微分几何转换。无合资格规则物理网格的任意散点/mesh曲率拒绝，不用PCA比率、法向夹角或primitive半径倒数替代。高度描述是显式轴/平面有向几何场，计量/参考资格仍归原Owner。

生产执行仍只接受显式Profile；参数建议独立入口、有限候选、精确评价/拒答与显式采纳规则见D.4，不静默调参或称“最佳”。建议不修改冻结请求，采纳须由宿主创建新ProfileRevision/RequestId。没有客户目标只返回未评价，不把建议转为生产参数。

## 5. API、同步/异步和事件

附录 A 定义模块局部类型。同步与异步入口共享校验和核心路径；取消来自方法参数，Timeout 从接纳时起按单调时钟计算，覆盖校验/获取租约/运行/排空，不能以墙钟调整重置：

```csharp
SurfaceFeatureResult Execute(SurfaceFeatureRequest request,
    CancellationToken cancellation = default);
ValueTask<SurfaceFeatureResult> ExecuteAsync(
    SurfaceFeatureRequest request,
    IProgress<SurfaceFeatureProgress>? progress = null,
    CancellationToken cancellation = default);
ValueTask<DrainReport> DrainAsync(TimeSpan waitBudget,
    CancellationToken waitCancellation = default);
ValueTask<DrainReport> CloseAsync(TimeSpan waitBudget,
    CancellationToken waitCancellation = default);
CapabilityReport GetCapabilities();
ValidationReport Validate(SurfaceFeatureRequest request);
```

同步入口只用于可阻塞线程，不在UI线程执行。Core全部await不捕获宿主SynchronizationContext；同步入口阻塞同一核心路径。backend自行管理所需native工作线程与亲和性，Run不得同步占住调用方UI线程；不把STA/Dispatcher要求传回Core。宿主不假定通知线程；共享backend须支持并发私有工作对象，不能依赖调用者恰好串行。

### 5.1 事件顺序

事件是通知，不是结果权威。每个事件携带 `RequestId`、`CalculationIdentity`、源 `Revision` 和单调 `EventSequence`：

正常通知顺序为 `Accepted -> Validated -> Started -> (StageChanged|Progress)* -> Draining -> Drained -> ResourcesReleased -> Completed|Failed|Cancelled|TimedOut`；已接纳校验拒绝为 `Accepted -> Validated -> Draining -> Drained -> ResourcesReleased -> Rejected`；Started前取消同样闭合空资源。接纳前Busy/Closing/Duplicate拒绝不发Accepted。释放未知唯一分支见 A.3。

单一通知入口为 `IProgress<SurfaceFeatureProgress>`，无另套Core CLR事件；通知有顺序号、终态权威为result/DrainReport。Drained指native及内部backend回调退出，不含宿主Dispatcher显示通知；ResourcesReleased表示工作句柄/索引/buffer/内存预约已归还，不等于消费者释放快照/返回payload。宿主按EventSequence/RequestId/Revision丢弃旧投影。

通知在独立投递路径串行调用 Report，计算线程不等待用户代码；异常记录，慢通知不能拖住 native/释放。该请求结果返回可早于 UI 实际显示终态，迟到投影不是排空未完成。用户回调不得同步调用 Execute/Drain/Close/Dispose 等阻塞同实例操作；检测重入返回 `S3D-013`，不得形成“回调等 Close，Close 等回调”的死锁。关闭后在途通知不访问已卸载视图；宿主解除关联，保留不可变诊断摘要。

通知存储有界：每请求最多32个非Progress生命周期记录，StageChanged/Progress各保留最新一项；排队不留Snapshot/payload/native。停止投递时终态仍在result可取，不保证已Detached订阅者收到；Dispose不等用户Report退出。回调执行上下文用AsyncLocal标重入，Execute返回Rejected/S3D-013，Drain/Close返回Unknown（不改变服务接纳状态），Dispose抛InvalidOperationException；诊断记录回调重入，不进行同步等待。IDiagnosticsSink同样隔离投递，只允许best-effort不可阻塞执行线程。

## 6. 状态、错误码与恢复

### 6.1 计算状态

模块局部状态只表达计算生命周期，不映射质量结论：

正常路径为 `Created -> Validating -> Running -> Draining -> Drained -> ResourcesReleased -> Completed`；校验/能力拒绝为 `Created -> Validating -> Draining -> Drained -> ResourcesReleased -> Rejected`；运行中取消/超时为 `Running -> CancelRequested -> Draining -> Drained -> ResourcesReleased -> Cancelled|TimedOut`；native 异常为 `Running -> FailedPendingDrain -> Draining -> Drained -> ResourcesReleased -> Failed`。若失败发生在 native 调用前，仍须发出 `Drained` 事实以闭合已取得的租约；`ResourcesReleased` 只能在所有权归还确认后发出。

`Completed` 仍可 `Quality=Insufficient/Unknown`；它不授生产资格。Timeout/token 触发只记录停止意图；`TimedOut/Cancelled` 只能在 `ResourcesReleased` 后成为请求终态，Execute Task 在此之前不提前返回/抛 token 异常。无法中断时可超过 Timeout 才返回，宿主用有界 DrainReport 显示仍在排空。最先观察到的取消/超时原因锁定，其他错误作次要诊断；释放失败优先为 Failed，不能宣称已释放。重启没有进程内结果查询库，宿主把未闭合请求标 Unknown，不能伪造可恢复的持久 operation 查询。

### 6.2 稳定错误码（候选）

| 错误码 | 语义 | 调用方动作 |
|---|---|---|
| `S3D-001 InvalidRequest` | 缺字段、范围或契约不匹配 | 修正请求，不重试同一错误 |
| `S3D-002 SourceUnavailable` | 宿主导入来源/原件不可用（Core不执行文件IO） | 宿主重新获取后Create新快照 |
| `S3D-003 UnitOrFrameMismatch` | 单位/坐标系不一致 | 由坐标 Owner 转换或拒绝 |
| `S3D-004 NonFiniteOrIndexCorrupt` | NaN/Inf、长度/索引损坏 | 保留原诊断，禁止补零 |
| `S3D-005 CapabilityUnavailable` | 目标后端/版本不支持方法 | 选择已批准路线或返回未评价 |
| `S3D-006 InsufficientSupport` | 点、面、邻域、覆盖或可观察性不足 | 返回缺口与分母，不冒充成功 |
| `S3D-007 NativeError` | HALCON/AsunImage调用或资源归还失败 | 先确认归还；仅确认后新RequestId显式重试，Unknown禁止重用 |
| `S3D-008 BudgetExceeded` | 点/面/内存/时间预算超限 | 停止后排空；禁止静默降精度 |
| `S3D-009 CancelRequested` | 调用方请求取消 | 返回取消与排空事实 |
| `S3D-010 TimedOut` | 超过deadline | 等原Task/有限Drain，不消费中间结果；无持久查询库 |
| `S3D-011 MappingUnavailable` | 派生点/面无法追溯源索引 | 仅允许显示用途，量测用途拒绝 |
| `S3D-012 TopologyAmbiguous` | 洞、断边、非流形或方向不明确 | 返回候选和限制，交给调用方决策 |
| `S3D-013 ResourceBusy` | 句柄/租约或并发额度不可用 | 等待、排队或由宿主退避 |
| `S3D-014 StaleRevision` | 支撑声明Source.Identity不匹配，或宿主投影过期；Core不查活动修订 | 修正声明关联或宿主丢弃旧投影，不覆盖新修订 |
| `S3D-015 DuplicateRequestId` | 同实例重用请求标识 | 用新的 RequestId 显式重算，不自动重放 |
| `S3D-016 ServiceClosing` | 关闭已封住接纳入口 | 等旧实例排空，另建显式实例 |

未知错误必须保留原生错误号/文本和阶段；不得将异常、取消、超时、缺支持合并为 `false`。

## 7. 取消、超时、排空、线程和资源

- `CancellationToken` 只表达取消请求；适配器必须确认 HALCON 26.05 的中断传播。无法中断时，状态为 `CancelRequested/Draining`，等待 native 返回后释放。
- 超时停止本请求后续阶段；仍运行时本实例Busy，不释放native使用句柄。返回Closed/Unknown前禁止摧毁借用backend，资源确认释放后服务可接纳新ID；仅Close永久封接纳。
- 一个 native 工作模型同一时间只有一个 Owner；输入快照可并行读取，扩展属性写入必须在私有副本执行。
- 结果对象为不可变托管数据；native 句柄不得暴露到 Core、UI 或调用方缓存。
- 预算包含保留的输入点、输出点、面、贡献映射、法向、拓扑、native模型与读回峰值；超限 `S3D-008`，不减采样或删目标。返回的托管 payload 已脱离工作资源，消费者负责其后续保留与持久存储预算。
- 订阅、初始化、执行、取消、排空任一步失败，只释放已取得的资源；实例可重复关闭且关闭幂等。
- 默认不使用可变静态缓存。缓存键必须包含源 hash、参数规范化结果、后端能力版本和 ContractRevision；淘汰不改变已完成结果。

### 7.1 接纳、Close 与硬资源边界

首发一服务单请求无队列；并发即时Rejected/S3D-013。宿主显式排队计队列时间，多服务共享内存接纳端口。Validate纯预检；Execute在锁内先Closing→重复ID→Busy→ID容量检查，未接纳失败不占RequestId；接纳后登记ID/再验证/取得内存预约。无资源路径仍闭合空集Drained/ResourcesReleased。

`DrainAsync` 仅等待调用瞬间在途请求；其间新接纳不包含在这次等待。Close原子封接纳并请求取消在途，再等排空。waitBudget有限正，超时或waitCancellation只停止等待→Pending，不释放native/预约、不改变请求终态。Close幂等；backend/memory的Owner始终宿主。DisposeAsync调用Close并等待真实排空，不强制释放native中对象；页面可先解除投影，由宿主生命周期管理器保留service直到Dispose结束。

Budget 含点/面/贡献索引总数、Managed/Native/临时树与峰值估计。适配器在分配前报告 Estimate（含 O(k*n) greedy 邻居列表、两表面复制和读回峰值），Core 通过 `IMemoryAdmission` 获得字节预约，实际峰值须记录。HALCON 不可中断的单次分配没有本模块可保证的硬进程内上限；估计不是硬隔离。请求 `RequireHardMemoryLimit=true` 而后端无证据的限额执行边界时在 native 前拒绝 `S3D-005`，不得把定时监视工作集当硬上限。普通预算超限停止后续阶段并排空；不得声称 OOM/进程崩溃后可自动回收或恢复结果。独立 worker 隔离不是首发隐含能力，须另行准入。

Freeze 先构造不持 lease/native 的托管 payload；释放全部资源后补齐诊断与资源终态，才发布 result。失败/取消/超时 payload=null，仅诊断含阶段计数，不能把中间 mesh 当可消费结果。释放失败结果为 Failed、ResourcesReleased=false、DrainReport=Unknown，并将实例封闭；不能复用不确定资源。诊断 sink 为 best-effort 非阻塞副作用，不拥有几何事实或数据库事务。

## 8. 输出契约

候选 `SurfaceFeatureResult` 至少包含：

| 区域 | 必填内容 |
|---|---|
| 身份 | RequestId、CalculationIdentity、SurfaceId/Revision/Hash、Purpose |
| 执行 | Operation（由 `Parameters` 判定）、实际方法/参数、HALCON/AsunImage 能力版本、开始/结束/排空时间 |
| 几何 | 点/面/组件/primitive/法向/截面结果及单位、坐标系、有限性 |
| 来源 | 每个派生点/面到源索引的映射；缺失时 `MappingUnavailable` |
| 质量 | `Complete/Insufficient/Unknown`、支持域、排除/剔除计数、洞/断边/退化、残差分布 |
| 诊断 | 阶段耗时、峰值资源、错误码、native 原始号、停止原因、可重试性 |
| 状态 | `Completed/Rejected/Failed/Cancelled/TimedOut` 与 `Drained/ResourcesReleased`；释放失败明确为 Unknown |

结果不包含工艺上下限、板级 PASS/FAIL、放行意见、设备动作或提交回执。调用方若要保存事实，必须创建自己的 `CommitIdentity` 并沿原 Owner 的提交协议处理；本模块没有提交权。

## 9. 可选 UI 契约

UI 是可选 `Asun.Modules.SurfaceFeatures3D.Wpf`，核心 DLL 不引用 WPF。控件公开 `SurfaceFeatures3DControl` 和 `SurfaceFeatures3DControlFactory.Create(ISurfaceFeatures3DService service, IUiTextCatalog text, SurfaceFeatures3DViewOptions options)`；宿主注入服务、权限判定、语言目录和视口投影端口。控件不持有 native 句柄、产品数据库连接或质量权限。

实现使用本机 DevExpress 25.2.3 的 `DevExpress.Xpf.Docking.DockLayoutManager`/`LayoutPanel`/`LayoutGroup`、`DevExpress.Xpf.PropertyGrid.PropertyGridControl.SelectedObject`、`DevExpress.Xpf.Grid.TreeListControl` 与 `DevExpress.Xpf.Core.SuperTip`/`SuperTipItem`；本机 XML 文档确认程序集文件版本 `25.2.3.0`。这些是 UI 切片的绑定依据，真实 WPF 行为和 UIA 尚未执行。

- 1920x1080 客户区固定三区：左 `280px` 来源树，中心 `*` 影像/点云，右 `360px` 参数与证据；底部 `96px` 状态/命令，DockLayoutManager 不允许拖动改变最小宽度。窗口缩放只在两列 `min/max` 约束内工作，窄于 1360px 时参数区进入同一 DockLayout 的可见 Tab，不能覆盖中心图像。
- 左区显示表面/派生代次、frame、unit、hash 前12位、有效/法向/三角支持计数和域；选择节点只改变投影，不改变冻结请求。中心显示原始与派生图层，至少提供 `Original/Derived/Normals/Topology/Section` 独占图层、LOD 仅显示，不改变算法输入；悬停显示 source index、有效性、组件/边界/洞标签。
- 右区以 operation 分组编辑已冻结 `SurfaceFeatureParameters`，每字段显示单位、范围、来源 `ProfileRevision`、当前草稿值与实际规范化值。PropertyGrid 的 `SelectedObject` 只绑定不可变草稿副本；冲突字段在编辑时显示错误，`Validate` 失败禁止预览。能力不支持显示原因与受影响切片。
- 底部显示状态、阶段、进度、有效分母、排除原因、残差/洞/边界摘要和 RequestId；命令只有 `预览`、`取消`、`丢弃草稿`、`导出证据`。预览按钮在权限端口返回 `CanExecute=true` 且校验通过时可用；取消只对当前代次有效；导出证据导出不可变结果摘要，不导出 native handle/产品数据库事实。没有自动放行、自动改标定、自动换方法命令。
- 高级联动：左区新 revision 立即使右区草稿和中心旧结果显示 `Stale`，预览结果按 RequestId/Revision 绑定；更改 method 清空不适用参数并显示重算原因；能力缺口、资源估计和时间预算联动更新，不能自动修正。TreeList 选中组件/边界只高亮对应 source index，不修改输入。
- 键盘/权限：`Ctrl+Enter` 预览，`Esc` 取消当前预览，`Ctrl+Backspace` 丢弃草稿，`Ctrl+Shift+E` 导出证据；Tab 顺序为来源→图层→参数→状态→命令，焦点不可落入禁用命令。宿主授权端口决定编辑/导出权限；无权限仍可浏览，不隐藏错误。
- 三语资源覆盖标题、字段、单位、状态、错误、恢复和 SuperTip。默认 `zh-CN`，由宿主在控件外切换；`zh-TW` 与 `en-US` 长文本需在 1920x1080 截图/自动 UIA 树验收中无截断。SuperTip 只解释单位、边界、排空和恢复，不能藏关键失败。
- 卸载顺序固定为：标记页面 Detached 并解除视图关联→取消控件当前请求→有界等该请求结果→释放控件投影。服务属于宿主，卸载控件不 Close/Dispose 借用服务；宿主关闭独占服务时才执行 `CloseAsync`，Pending/Unknown 交宿主生命周期管理器保留直到真实排空。回调不触碰 Detached 视图，慢回调不阻塞 Core。具体挂接、代次与投影端口见附录 A.6。

## 10. 无 UI 接入示例（模块局部 API 形状；未宣称已编译）

```csharp
using Asun.Modules.SurfaceFeatures3D;

// consumer A: backend/memory 是宿主注入的 A.4 端口，非窗口或设备 SDK。
static async ValueTask<HostCallReport> CandidateForReferenceAsync(
    HostRetentionRegistry host, I3dSurfaceBackend backend,
    IMemoryAdmission memory, TimeProvider clock,
    SurfaceSnapshot segmentedPlaneSupport, SupportDeclaration primitiveSupportRef, ResourceBudget budget,
    TimeSpan deadline, string profileRevision, HostObservationBudgets observation,
    CancellationToken cancellation)
{
    var request = new SurfaceFeatureRequest("A-1", segmentedPlaneSupport,
        new FitParameters(PrimitiveKind.Plane, FitAlgorithm.LeastSquares, null,
            primitiveSupportRef),
        deadline, budget, SurfacePurpose.DatumCandidate,
        SurfaceFeatures3DServiceFactory.ContractRevision, profileRevision);
    return await ExecuteOwnedAsync(host, backend, memory, clock,
        request, observation, cancellation);
    // 返回 plane 候选，不替 reference-surface 决定资格。
}

// consumer B: 已有 triangle mesh，Topology 完全托管；backend 可为 null。
static async ValueTask<HostCallReport> ConnectorTopologyAsync(
    HostRetentionRegistry host, IMemoryAdmission memory,
    TimeProvider clock, SurfaceSnapshot mesh,
    ResourceBudget budget, TimeSpan deadline, string profileRevision,
    HostObservationBudgets observation, CancellationToken cancellation)
{
    var request = new SurfaceFeatureRequest("B-1", mesh,
        new TopologyParameters(), deadline, budget, SurfacePurpose.MeasurementSupport,
        SurfaceFeatures3DServiceFactory.ContractRevision, profileRevision);
    return await ExecuteOwnedAsync(host, null, memory, clock,
        request, observation, cancellation);
    // 返回边/链/组件证据，不替连接器产品定义对象关联或缺陷。
}
```

模块类型与签名见附录A，Host类型仅为本节确定的消费者保活约定，不新增Core API。示例接收真实snapshot/budget/Profile，不提供假HALCON构造。Core Exe对A用受控backend核协议，B执行真实托管拓扑；真实primitive正确性另验。两个Host都不使用局部await using隐式退出，因为有限观察超时或Dispose抛异常不能让外层栈丢失Owner。模块Dispose真实等待排空语义保持A.4，不Dispose借用backend/memory。

### 10.1 factory前保留宿主强持槽与有限清理观察

`HostRetentionRegistry` 是进程级宿主根持有对象，不是Core全局静态服务；容量固定、只有原Host写Owner，不能在业务函数局部创建或在返回报告时析构。宿主关闭仍有Pending/Unknown槽时不能正常摧毁registry/借用端口或报告已清理。新调用先确认容量，失败在factory前拒绝；槽位一旦创建，不因函数return/throw、wait超时、callback迟到或转交请求而自动删除。以下为同一Exe/消费者中的BCL语义代码形状，未编译，不创建新的产品工程。

| 宿主局部类型/方法 | 确定内容与行为 |
|---|---|
| `HostObservationBudgets` | `ExecuteWait/CloseWait/DisposeWait:TimeSpan`，各有限正；生产由宿主给定。`Remaining(phaseBudget):TimeSpan` 按启动观察时的System单调时钟返回min(phaseBudget,累计剩余观察预算)，耗尽返回Zero。受控case从case起点累计，不能超过§1.3的10s，业务与finally不重新起表 |
| `HostCallReport` | `Result:SurfaceFeatureResult?`、`ExitCode:int`、`RetainedSlotId:string?`、`BusinessErrors/CleanupErrors:ImmutableArray<string>`；0仅业务Completed且资源确认归还，其他非零，Unknown必须非零 |
| `HostRetentionRegistry.TryReserve(SurfaceFeatureRequest request, I3dSurfaceBackend? backend, IMemoryAdmission memory, TimeProvider clock, out HostRetentionSlot slot, out HostCallReport rejected):bool` | factory前原子占预分配有限槽，立即强持RequestId/request/snapshot、backend/memory/clock；成功slot有效，rejected不读。已满返回false与非零rejected（slot不读），不创建service/Task；拒接原调用者仍持有端口。Service赋值为槽内无副作用强引用写入，不触发回调或另建容器 |
| `HostRetentionSlot` | 保存 `Service:ISurfaceFeatures3DService?`、原 `ExecuteTask:Task<SurfaceFeatureResult>?`、`CloseTask:Task<DrainReport>?`、`DisposeTask:Task?`、业务/cleanup错误、观察结果及资源状态；保存Task只调用ValueTask.AsTask一次，之后等待同一Task，不留只有weak reference/回调闭包 |
| `StartExecute/StartClose/StartDispose` | 在槽锁内最多启动各一次，调用相应现有API并立即存AsTask；同步throw存Task.FromException及对应错误，禁止丢弃Task。Close调用 `CloseAsync(closeWait,CancellationToken.None)`，Execute保留业务token；Dispose调用 `DisposeAsync()` 无中止token、不改变真实排空。已有在途Dispose只返回原Task，不能第二次启动 |
| `RecordBusinessError/RecordCleanupError/RecordBusiness/RecordClose/RecordDispose` | 分别保存业务结果或观察异常/cleanup观察，不把cleanup失败覆盖业务错误、不将WaitAsync超时记成底层Task已终止。迟到结果由原槽串行观察原Task与flags；不创建另一个Execute |
| `HostRetentionRegistry.FinishObservation(slot):HostCallReport` | 仅在finally全部观察完成后判退出码。释放槽须原Execute已返回且Drained/ResourcesReleased=true、原Close为Drained/ResourcesReleased、原Dispose成功、无任何资源Unknown；factory失败且Service=null/无Task/无资源时可释放空槽。业务Failed/Cancelled/TimedOut即使资源归还也非零；cleanup观察超时/throw非零，资源未证实时RetainedSlotId非null |

```csharp
// 两个消费者共同的宿主层顺序；不改模块公开API。
static async ValueTask<HostCallReport> ExecuteOwnedAsync(
    HostRetentionRegistry host, I3dSurfaceBackend? backend,
    IMemoryAdmission memory, TimeProvider clock, SurfaceFeatureRequest request,
    HostObservationBudgets observation, CancellationToken cancellation)
{
    // factory前拒接：未创建service，原调用者继续拥有端口。
    if (!host.TryReserve(request, backend, memory, clock, out var slot, out var rejected))
        return rejected;
    try
    {
        slot.Service = SurfaceFeatures3DServiceFactory.Create(
            backend, memory, clock, new SurfaceFeatures3DServiceOptions(128));
        var originalExecute = slot.StartExecute(cancellation);
        var result = await originalExecute.WaitAsync(
            observation.Remaining(observation.ExecuteWait),
            TimeProvider.System, CancellationToken.None);
        slot.RecordBusiness(result);
    }
    catch (Exception error) { slot.RecordBusinessError(error); }
    finally
    {
        if (slot.Service is not null)
        {
            try
            {
                var originalClose = slot.StartClose(observation.CloseWait);
                var closed = await originalClose.WaitAsync(
                    observation.Remaining(observation.CloseWait),
                    TimeProvider.System, CancellationToken.None);
                slot.RecordClose(closed);
            }
            catch (Exception error) { slot.RecordCleanupError("Close", error); }
            // Close超时/throw仍观察一次原Dispose；原Task永久留槽，不二次启动。
            try
            {
                var originalDispose = slot.StartDispose();
                await originalDispose.WaitAsync(
                    observation.Remaining(observation.DisposeWait),
                    TimeProvider.System, CancellationToken.None);
                slot.RecordDispose();
            }
            catch (Exception error) { slot.RecordCleanupError("Dispose", error); }
        }
    }
    return host.FinishObservation(slot); // finally后才定码，不能先return业务成功。
}
```

有限等待只观察原Task，不取消/替换它；底层Dispose可仍在等待native，原槽继续强持service、原Execute/Close/Dispose Tasks、RequestId与借用端口。cleanup同步throw也留原失败Task，不能因catch后仅返回错误文字而丢失Owner。迟到Completed不直接删除槽；原Owner核全部归还事实后才释放，历史业务/cleanup错误分别保留，不把之前超时报告改成成功。

若转交宿主生命周期管理器，接收方必须明确确认同一槽ID、RequestId、service、原Tasks和backend/memory已强持且接管后续观察；确认前原Host持续持有。转交拒绝、回执丢失或未确认接收均不释放原槽、不靠“消息已发送”判接管；确认后只转移槽的强持Owner，槽仍保留且不释放容量，双方留关联记录。真正释放槽仍须归还确认。没有接收方时原Host持有并拒绝相关退出/端口销毁；Unknown不自动重试/强制归还。Remaining为Zero时只立即停止外层观察，StartClose仍传配置的正CloseWait、StartDispose仍启动并保存一次，不能以剩余时间零跳过真实清理。

## 11. 正常、边界和失败案例

| 场景 | 期望 |
|---|---|
| 有限点云，明确单位/坐标，三角化保孔 | 返回实际面数、洞/边界、源映射和方法；不宣称实体封闭 |
| `h=1,o=0`，点 `x=-0.1` 与 `x=0.1` | 固定体素思想反例的桶为 `-1/0`，不作为首发 HALCON Sampling 方法；没有 Voxel DTO，不复制另一套采样内核 |
| 同桶高度 `0,0,0.9 mm` | 派生质心 `0.3 mm` 不能证明原始最大高度；反例约束显示派生的消费边界，不承诺 HALCON accurate 必产生这个质心 |
| 仅法向计算 | 原始 XYZ 不变；零法向保持无效；不默认朝 +Z |
| 裁切后面引用合法 | 删除点后重新核面、洞和边界；越界面映射返回拒绝 |
| `all` primitive 拟合 | 读取实际类型/数量/参数；没有 plane 不能补造 plane |
| 点云无 faces 请求体积支撑 | 返回 `S3D-006 InsufficientSupport` 或 `S3D-012`；不从显示网格补面 |
| `MaxDistance=0.2 mm` | 超出范围的值标记截断/下界；不纳入精确 RMS、极值或公差 |
| 连通组件请求的前置属性缺失 | `S3D-005`；不换 `ConnectionFeature`；另一特征须新 ProfileRevision/CalculationIdentity |
| 有效点 NaN/Inf、长度属性用 pixel | `S3D-004` 或 `S3D-003`；Validity=false 的 NaN 保留原因但不送 native |
| 取消发生在 native 调用中 | `CancelRequested -> Draining -> Drained -> ResourcesReleased -> Cancelled`；排空前不释放句柄 |
| 宿主活动 revision 更新 | 旧计算快照仍合法；宿主把旧投影标 Stale，不覆盖新 revision；Core 不查询产品活动修订 |
| 两个实例写同名距离属性 | 各自私有工作模型，结果互不覆盖 |
| 适配器不支持 26.05 所需方法 | `S3D-005 CapabilityUnavailable`，不自动换算法或降低精度 |

### 11.1 第二轮场景驱动复审矩阵

下表把每个关键场景展开为可执行的输入、参数来源、处理顺序、输出、状态/错误、恢复和验收断言。`Profile` 指调用方冻结的输入/资源/精度配置；没有 Profile 时使用显式请求值，不使用产品或工艺隐含值。

| 场景 | 输入与参数来源 | 处理顺序 | 输出与状态/错误 | 恢复动作 | 可判定验收 |
|---|---|---|---|---|---|
| 正常配置/执行 | 有效点云或 mesh、单位/frame/hash；方法和 generic 参数来自能力清单+调用方 Profile；预算与 deadline 显式传入 | Validate→Capture→独占工作模型→选域→首选算子→读回类型/计数/映射→Freeze→Release | `Completed`，质量为 `Complete` 或明确 `Insufficient`；含实际方法、参数、映射和资源诊断 | 调用方消费候选并自行决定后续参考/量测 | 同一快照+参数重复运行在批准数值容差内，输入不被修改，句柄全释放 |
| 空输入/部分成功 | 0 点、全无效、点有但无 faces、部分区域有洞或面；支持门来自 Profile | Validate 有效计数→不调用不适用算子；部分域按原始分母执行→逐域收集 | 空输入 `Rejected/S3D-006`；部分支持 `Completed+Insufficient`；不补零、不把缺域删除 | 宿主补采/改用另一独立来源；不得用平滑或显示网格伪造缺失 | 结果含缺失原因、输入/保留/派生分母和域；无“完整成功”字样 |
| 歧义/错误输入 | 单位未知、frame 不一致、hash 缺失、属性长度不符、索引越界、参数冲突 | Validate 在 native 前失败；不创建工作句柄 | `Rejected`，分别为 `S3D-001/003/004/011`；原始诊断保留 | 修正来源或参数并生成新 `CalculationIdentity`；不重试同一坏请求 | native 调用计数为 0；同步/异步错误码一致；原快照字节不变 |
| 噪声/遮挡/退化 | 稀疏、重复、离群、遮挡层、共线/小弧、法向零向量；采样/邻域参数来自算法 Profile | 先显式筛选/采样→再法向→再 primitive/拓扑；逐阶段保留剔除和支持 | 可完成但 `Quality=Insufficient`，或 `S3D-006/S3D-012`；不把 robust fit 当资格 | 选择独立支撑域、调整已批准参数、补采或改回放；不自动扩大邻域、补洞或改坐标 | 峰值/边界/洞/退化样例的来源映射可追溯；误差/残差分母明确 |
| 超大输入/高并发 | 点/面接近或超过 Budget；多实例同源/不同源 | 每实例单请求即时接纳或拒绝→共享内存预约→私有模型；队列仅宿主所有 | 超限 `S3D-008`；Busy `S3D-013`；在途不被替换 | 宿主显式退避、新RequestId；首发无分块算法 | 两实例结果互不串扰；内存预约无法取得时不调用 native |
| 取消/超时/native 排空 | 任一阶段收到 token 取消或 deadline；适配器声明是否能传播 HALCON 中断 | 标记取消→停止后续派发→若可中断则请求 native 停止→等待返回→Draining→`Drained`→释放并归还资源→`ResourcesReleased` | `Cancelled/S3D-009` 或 `TimedOut/S3D-010`；无法中断时先 `Draining`，不返回部分完成 | 查询原 operation 状态；排空完成前不复用句柄、不启动同一资源的新任务 | native 返回前句柄保持有效；`Drained` 事件先于 `ResourcesReleased`；不产生可提交结果 |
| 资源上限/内存故障 | `MaxBytes/MaxFaces/MaxOutputPoints`、native 分配失败；greedy prefetch 或 voxel 结构可能放大内存 | 预估→分配→阶段监控→超限/异常立即停止后续→排空→释放 | `S3D-008` 或 `S3D-007`；结果标记未完成阶段和峰值 | 宿主降低并发或改用已批准低资源路线；不得自动换近似方法冒充同等精度 | 资源上限可在测试中强制触发；所有已取得租约释放且无双重释放 |
| 持久化/版本修订 | CalculationIdentity/源hash/方法/版本；持久化由宿主 Owner | 计算完成→宿主提交；丢回执查询宿主事务；本模块无持久查询库 | 不生成 CommitIdentity；固定快照旧结果可读，宿主判过期 | 宿主按自身提交协议处理；重算必须新RequestId | 相同身份不冒承诺缓存幂等；历史输入/结果不覆写，模块无提交副作用 |
| 升级/回退 | 旧结果、旧参数、旧能力快照；新包/后端候选版本 | 停止接收→排空旧代→保存诊断→能力兼容检查→Replay/Golden 对比→切换或回退 | 不兼容返回 `S3D-005`；回退保留旧结果和版本证据 | 回到上一兼容包，重新回放；由调用方决定是否重建业务事实 | 旧样本可读；破坏性契约升 Major；新算法不覆盖历史字节 |
| 无 UI 调用 | 无窗口/无 Dispatcher 的最小宿主；文件或内存 snapshot；诊断 sink 注入 | 构造后端→Validate→ExecuteAsync→等待结果→取消/Drain→Dispose | 与 UI 相同的结果、错误和事件语义；无隐藏初始化 | 失败只释放已取得资源；宿主可重启实例 | 无 UI 进程可运行；无 WPF/DevExpress 引用；无订阅者仍能完成 |
| 可选 UI | 宿主提供语言/主题/权限投影；参数草稿和显示 LOD；核心请求不变 | UI 编辑→核心 Validate→冻结快照→执行→按 RequestId 显示→关闭时取消/Drain | UI 只显示候选、缺口和状态，不显示质量放行；慢回调隔离 | 丢弃草稿或重新预览；旧预览不能应用到新 revision | 1920x1080 下三语关键状态可见；无 UI 与 UI 同请求结果一致 |
| 第二消费者/长期运行 | 高度工具与连接器/表面候选工具使用同一包；长时间循环请求、重启和配置切换 | 各宿主独立实例→同一核心路线→定期资源/延迟诊断→滚动升级 | 结果语义一致；实例、缓存、语言和取消隔离；长期运行不积累句柄 | 由宿主做背压、重启或回退；历史结果按版本保留 | 两个消费者无需改 Core；长稳运行后句柄/工作集回到基线；无跨请求属性污染 |

## 12. 测试与验收矩阵

文档阶段只定义验收断言，未执行以下测试。实现阶段至少建立独立 Core 测试、AsunImage 适配测试和两个消费者接入测试。

| 类别 | 最小案例 | 断言 |
|---|---|---|
| Contract | 缺 hash、单位未知、长度不等、索引越界 | 同步/异步得到相同错误码；无 native 资源泄漏 |
| 数值 | 平面、阶梯、斜面、负坐标、零坐标 | 单位/方向/有限性明确；允许误差来自冻结 Profile |
| 采样 | fast/accurate/xyz_mapping、源次序变化 | 方法语义不混；映射/派生标识准确 |
| 法向 | 平面、翻面、孔边、零向量 | 原点不变；有效法向与点有效性分离 |
| primitive | plane/cylinder/sphere、共线/少点/小弧 | 实际类型、退化、支撑和残差可追溯 |
| 拓扑 | 洞、断边、非流形、孤立组件 | 不跨洞补面；组件/边界/洞计数稳定 |
| 连通路线 | 请求特征所需属性存在/缺失 | 缺失在算子调用前拒绝；不会切换到另一特征；显式新 Profile 请求可选择不同路线 |
| 距离 | signed/unsigned、截断、无 closest index | 截断分类和映射符合能力；共享对象不被改写 |
| 并发 | 两实例、相同源、不同参数/语言 | 不串属性、缓存、取消、诊断或结果 |
| 取消/超时 | 各阶段取消、native 不可中断、超预算 | 先排空再释放；不把部分结果当完成 |
| 资源 | 大点云、面数上限、重复关闭、异常订阅者 | 分配前预算/预约生效，实际峰值另测；普通预约不冒硬native上限；正常路径归还恰好一次，Unknown隔离 |
| 回放 | 固定 source/params/backend 版本重复运行 | 结果在批准数值容差内；来源和实际参数一致 |
| 消费者 A | 高度/参考面工具消费 plane/normal/support | 只消费几何候选；参考资格由 A/029 决定 |
| 消费者 B | 连接器/焊料候选工具消费 component/topology | 只消费组件/拓扑证据；目标关联和工艺解释留 B |
| UI（如交付） | 无 UI 与控件相同请求；关闭/语言/窄窗 | 语义一致；无 hidden initialization；三语不截断关键状态 |

### 12.1 绑定 Exe 的有限反例与验收 ID

以下为实现断言规格，本轮未执行。C1用受控backend闩锁/固定TimeProvider验证Core；C2执行真实托管拓扑，模拟结果不作HALCON数值资格。受控Core默认每case10s、suite120s、外进程180s wall watchdog，均沿§1.3固定；从case起点计入factory、业务与finally全部观察，超时不重置累计预算。虚拟时钟只测模块deadline/状态，System单调wall-clock闩锁watchdog另测真实Task是否退出。任一超限/未完成/必需跳过/Unknown非零；180s测试进程止损不作native释放证据。性能Profile保持§13消费者值；两轮分别从操作样例与外部Owner查断言。

| ID/切片 | 明确输入或触发 | 必须成立的断言 |
|---|---|---|
| SF01/C1 | SourceIndex=[10,11]，Validity=[true,false]，Points=[(0,0,0),(NaN,0,0)]，无效原因Occluded；交换mask | 前者factory合法且native仅见一个点，源未改；后者S3D-004。重复索引拒绝，坐标重合但索引不同合法 |
| SF02/C1 | Create后改调用者原数组、属性/嵌套polygon；import改一bit后仍给旧hash | 原Snapshot/hash不变；import拒绝；属性排序hash稳定，点顺序改变hash；null与空串、-0与+0不被混成同编码 |
| SF03/C1 | 同geometry+参数不同RequestId；然后重用已接纳ID | 新ID实际执行且CalculationIdentity相同；重用S3D-015不调用backend；Busy拒绝未登记ID，可稍后重试 |
| SF04/C1 | 首请求占闩锁，第二请求并发；两个service共享memory余量不足 | 同实例S3D-013，第二backend调用0；共享预约不超限，释放后新ID可接纳；两实例取消/参数不串扰 |
| SF05/C1 | 预取消token/Started前取消/native占闩锁时取消 | 全为Cancelled而非throw OperationCanceledException；Started前native调用0；运行中task未提前完成，闩锁退出→Drained→Release→Cancelled，payload=null |
| SF06/C1 | TimeProvider推进deadline，backend不退出；Drain有限wait到期 | Drain=Pending并有原RequestId，资源仍Active；Execute仍pending；退出后TimedOut无payload；不得把stopRequested称native已中断 |
| SF07/C1 | Close占闩锁时调用、重复Close、新Execute；waitCancellation；Host有限Observe超时后Dispose仍在途 | Close封接纳S3D-016；wait只停观察不销毁backend。factory前有限槽、Service/RequestId/端口与原三Task强持可断言；重复观察Dispose引用相同且启动计数1。Host finally后非零、槽仍在；真实退出并收到三方归还确认才释放槽，不Dispose借用端口 |
| SF08/C1 | backend cleanup/Dispose抛异常、memory归还失败；Close观察throw；Late progress；转交拒绝/回执丢失 | Failed/Unknown无payload，预约不冒归还/封接纳；业务与cleanup错误都留存、finally完成后判码；Close失败仍保存并观察一次原Dispose失败Task。迟到失败/Unknown及拒接/未确认接收均保留原Host根与槽；不能只返回文字后丢Owner，不新开Dispose。Unknown必非零，旧progress不覆盖新投影 |
| SF09/C1 | Report throw或慢Report，Report中调用同步Close；无Report | Core可释放返回且诊断隔离；回调重入Close禁止阻塞（返回Unknown/S3D-013诊断）；无订阅也完成，不重复终态序号 |
| SF10/C1 | Method与参数错配、Angle无法向、mapping无mapping、Curvature/Implicit/任意参数字典 | native调用0，S3D-001/005按原因；不换方法/补参数；同样本的新Profile才可另请求 |
| SF11/C1+Adapter | 米/mm/um同物理点、radius和absolute sigma；角度deg/rad、pixel | Core传递规范值一致，结果恢复Source单位；mapping按pixel、不按长度缩放。真实cv2调用和输出数值必须由Adapter另验证 |
| SF12/C2 | 单三角(0,1,2)，再两三角(0,1,2),(0,2,3) | 首者3边、环[0,1,2]，后者4边环[0,1,2,3]，共享(0,2)相反方向无冲突；face component一个，索引/顺序固定 |
| SF13/C2 | (0,1,2),(0,1,3)；再加(0,1,4)；重复(2,1,0)、重复顶点(0,0,1) | 两面共享(0,1)同向记OrientationConflicts；三面记NonManifoldEdges；重复face/顶点逐原ID单列，不污染有效关联；GeometryQualification=NotEvaluated |
| SF14/C2 | 两片只共一顶点，孔边环/分叉；打乱面顺序 | 只共点不合face component，分叉path Ambiguous；不把每闭环称孔、不授体积资格。按本次原faceID稳定输出，重排输入有新hash不承诺旧faceIDs相同 |
| SF15/C1+Adapter | `all`返回sphere；fit无primitive；Smooth映射丢失；MaxDistance=0.2且值到界 | all只sphere，不补plane/竞争集；无primitive=Insufficient；精密用途缺映射S3D-011；达界AtLimit排除精确统计；真实拟合/距离数值另Golden |
| SF16/C1/C2 | 两消费者§10、backend=null、错误ContractRevision、升级关闭旧代；factory异常、有限槽已满、在途退出/转交未确认 | A只plane候选，B真实Topology无backend，版本错native0。满槽拒接在factory前、factory调用0，原调用者仍持端口；factorythrow无Service/资源则记录业务非零后finally可释放空槽。在途退出不能析构registry/端口；未确认转交原Host持续持有，确认只换Owner不释放槽，归还确认后释放；无数据库/放行分支 |
| SF17/Adapter | 三角孔洞/阶梯/反光、greedy超时、signed开放面 | 固定补洞关闭与verbose信息可查，超时无中间Completed；缺连续性标限制/Insufficient；符号不授实体内外。真实HALCON未验，不用C1模拟替代 |
| SF18/UI | 同进程双控件、草稿更新/撤权/Detached迟到、三语/IME/键盘 | 代次/语言/取消隔离，不取消借用service其他任务；旧结果Stale，无权限禁止Preview/Export；关闭Pending由宿主持有。真实1920x1080含任务栏/边框/DPI客户区验收，未执行 |

C1规则中模拟backend可以只返回固定payload验证协议，但不得实现假plane/采样算法或把固定payload称几何正确。C2不依赖外部客户公差；边/环是整型精确断言。Adapter真值/数值容差、原件输入与消费者Profile保持后续门。

## 13. 性能预算与可观测性

以下只定义可复现的测量样本桶和采集方法，不定义性能达标值。消费者 Profile、运行环境和验收目标尚未采纳，性能目标状态为 `TargetPending`；不得将本表的点数/面数范围、P50/P95/P99 或资源记录要求解释为通过门槛、默认 SLA 或生产预算。

| 测量样本桶 | 输入规模（样本设计） | 固定测量条件 | 目标状态 |
|---|---:|---|---|
| S | <=100k 点、<=200k 面 | 冷启动与热运行分别测量；记录 P50/P95/P99、峰值工作集、native/托管内存和排空时间 | `TargetPending` |
| M | 非S且<=1M 点、<=2M 面 | 热运行与并发度 1/宿主声明并发度分别测量；记录 P50/P95/P99、队列等待、峰值资源和取消排空 | `TargetPending` |
| L | >1M 点或 >2M 面 | 必须由消费者 Profile 指定上限、并发、超时和资源预算；记录分阶段延迟、峰值资源、错误/取消/超时比例 | `TargetPending` |

### 13.1 可复现测量协议（不构成达标门槛）

每个消费者在采纳 Profile 时冻结并记录：输入点/面分布、有效率、拓扑类型、方法与规范化参数、source hash、HALCON/AsunImage 能力版本、CPU/GPU/内存、线程/并发度、冷/热状态、数据预热方式、取消/超时策略和采样次数。S/M/L 只是跨消费者复现实验的样本分层，不是性能等级。

公共统计方法唯一引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)：接纳到ResourcesReleased的端到端时长、完整排空样本P50/P95/P99与n、取消到真实排空/归还、失败/超时/删失及资源终态分列；不在本页另定义分位算法。排空Unknown不得性能通过；目标缺失只能诊断测量为NotEvaluated，仍TargetPending。native不支持返回peak时标Unavailable，不填0，不只挑成功样本。

每次运行记录：请求/源 revision、方法和规范化参数、输入/输出点面数、有效/剔除/派生分母、阶段耗时、队列等待、native 与托管峰值、取消延迟、排空时长、后端版本、错误码和重试次数。日志不得写入完整点云或敏感产品资料；用 hash/摘要和可回放资产引用。指标按 operation、数据规模和冷/热分组，不把 UI 渲染时间混入算法时间。

### 13.2 唯一 Exe BenchmarkProfile 输入与执行

未来 `--benchmark <path>` 读取System.Text.Json文档，SchemaKey=`surface-features-3d.benchmark/0.3`；所有字段必填，未知/重复字段、缺失、无限deadline或缺hash拒绝非零。这里只冻结输入模式，不新增Profile文件。Source来自本模块局部快照（A.1规范hash校验），不能由测试随机生成点云冒充真实样本。

SourcePath/TargetPath内容为A.1规范二进制snapshot字节，import按前缀和定长/长度字段解码，拒绝负数集合长度/越界/尾部多字节，再Create并与Profile hash比对。这里只是Exe回放输入，不新增Core文件IO端口。Profile枚举按上述名称字符串区分大小写；Time为ms有限数，long资源为整数；参数抽象类用`$type`（如PhysicalSpacing/AbsoluteSigma）和record字段，null必须显式写；所有double有限且不接受JSON命名NaN。DistanceParameters.Target不在JSON内重复嵌完整surface，从TargetPath导入注入，并校验TargetKind。ThresholdSource为A.1 EvidenceRef；Targets数值都是非负有限ms/bytes，P分位目标单调；冷/热值仅Cold/Warm，环境记录CPU/OS/.NET/模块/后端版本与资源探针可用性。ControlledPort允许确定性合成样本但Mode必须保持ControlledPort，不能冒真实大云性能。

| JSON 字段（大小写固定） | 值与行为 |
|---|---|
| `ProfileId/Revision/SchemaKey/Mode` | 非空；Mode=`ManagedTopology/ControlledPort/HalconAdapter`；前两种不能写成真实HALCON性能 |
| `SourcePath/SourceHash/TargetPath/TargetHash` | path相对Profile目录解析；SourceHash为局部hash；Target无时两个null，有时都填；不改变原件 |
| `Parameters/Purpose/ContractRevision/BackendId/BackendVersion` | A.2具体parameter类型判别`$type`为类名，仅登记类型；parameter字段同record名；身份和单位校验；与所装后端不符即拒绝 |
| `Budget/DeadlineMs/OuterWatchdogMs` | Budget同A.2；两时间有限正值且外层watchdog大于deadline；watchdog触发未归还样本记删失Unknown，退出非零，不能生成通过 |
| `ConcurrentServices/ColdOrWarm/WarmupCount/MeasurementCount/MinimumDrainedCount` | 正并发，各服务单在途；冷/热分别测；样本数来自Profile，预热计数非负；测量数/最低有效数正且最低≤测量数，不填模块默认 |
| `InputValidity/TopologyClass/NormalSupport/MappingClass` | 从样本校验回显真实分类，不接受Profile声明替代输入事实；分层包括孔洞/反光无效/薄壁/阶梯/密度变化 |
| `ThresholdSource/Targets` | 缺客户目标时两者null→NotEvaluated；有则ThresholdSource为批准Profile版本+证据hash，Targets含P50/P95/P99、PeakBytes、CancelDrainMs，都是Profile值，不从样本桶生成 |

步骤为加载与校验→冻结身份/环境→按Profile预热→发新RequestId测量（宿主排队独立测）→记录Validate/Estimate/Reserve/Native/Readback/Freeze/Drain/Release阶段→按治理统计完整排空样本与失败类别→输出诊断到stdout。无目标且完整测量成功退出0仅表示诊断完成，结果字段Evaluation=NotEvaluated；任一资源Unknown/必需样本不足/实际目标未过退出非零。同样本HALCON候选对比同时记录来源/误拒/误接受或拒识、峰值/孔边/薄壁保持与性能，未执行不写优势倍数。

## 14. 版本、兼容、发布与回退

- 包采用语义版本；Contract/Schema、单位、坐标方向、状态/错误码、结果映射的破坏性变化升 Major。
- 新增可选方法/字段升 Minor；仅修复不改变结果语义的实现升 Patch，并记录 HALCON/AsunImage 版本。
- 结果包含 `ModuleVersion`、`ContractRevision`、`BackendCapabilityVersion` 和参数规范化快照；旧结果可读不等于可用于新计算。
- HALCON 26.05 实际参数映射/来源/停止能力随适配器锁定；C#重载或封送歧义只局部解决，不重审用户确定依赖。
- Core程序集固定 `Asun.Modules.SurfaceFeatures3D.Core`；HALCON Adapter和可选WPF的唯一工程、Host与发布路径已绑定附录B/C。版本0.4.0-prep补外围接线，不改已接收的Core Contract 0.3、算法支持面或SF-C1/C2状态；本轮不创建工程。
- 回退步骤：停止新任务→等待旧代 `Drained`→保留旧结果与诊断→切换到上一兼容包→用同一 Replay/Golden 重放→由调用方决定是否重新提交事实。禁止用新算法覆盖历史结果或把旧回执改写为新版本。
- 配置/参数升级必须产生新 revision；缺少迁移规则时拒绝加载，而不是猜测单位或默认值。

## 15. 第二消费者与独立交付验收

首个消费者可为任一高度/参考面工具，第二消费者必须是不同宿主、不同任务语义的连接器几何或焊料/表面候选工具。两者必须：

1. 只引用发布包和公开契约，不引用彼此页面、ViewModel、私表或设备 SDK；
2. 使用同一输入快照和相同方法时得到相同几何结果/证据语义；
3. 可分别取消、切换语言、关闭和重启，互不影响；
4. 分别验证正常、缺支持、取消、旧 revision、拓扑洞和资源超限；
5. 由各自调用方负责目标关联、工艺解释、质量判定和提交，031 不增加领域分支。

## 16. 待决项与准入门

本文可决定的模块局部规格已写入正文/附录；保持 `DesignReview/Prep`，是否接收为某Core切片Ready由主控按下表串行接收，不把全模块统一提升：

- 正式 Contract/Schema 字段、状态 Owner、错误码注册和 CalculationIdentity 绑定；
- 真实适配切片执行参数映射、属性读回、单位/来源及中断/排空验收；仅实际C#类型/重载歧义查公共签名，不核算子存在或依赖授权；
- 两个消费者的真实输入 Profile、单位/坐标/标定资格和性能目标；
- Golden/Replay 数据、洞/边界/峰值保持样例和数值容差；
- native资源/并发/取消排空实现与故障验收；结果回放存储属宿主，不把数据库准入绑纯Core；
- 可选 WPF 控件的真实 PageContract、UIA、三语和 1920x1080 验收。

任何缺失事实只阻断依赖该事实的切片。不得以 Mock、截图、非 26.05 页面、编译成功、空对象、显示 mesh 或单元测试代替现场计量、HIL、Golden 或生产资格。

### 16.1 六项条件逐切片结论（2026-10-10，主控已接收SF-C1/SF-C2规格）

SF-C1（快照/校验/身份/服务生命周期/冻结端口下受控测试Host）与SF-C2（纯索引Topology）六项规格已由主控回读接收，状态为 `ModuleCoreImplementationReady`。本表的接收仅是规格准备，不表示工程已创建、代码已实现、测试已运行；HALCON数值、可发布Simulator、WPF、平台映射及性能/现场资格均不包含在这两个切片。

| DEV-GOV-010 §3.1 条件 | SF-C1 | SF-C2 | 定位/后续门 |
|---|---|---|---|
| 1 职责/依赖/第二消费者 | 规格已接收 | 规格已接收 | §1–2、§10、§15；两消费者无UI方案，不声称真实接入完成 |
| 2 类型/签名/单位/Owner/资源/版本 | 规格已接收 | 规格已接收 | A.1–A.5、§3–8、§14；平台Schema映射仅产品集成门 |
| 3 无UI最小host/端口 | 规格已接收 | 规格已接收 | §10/10.1、A.4；C1受控backend、C2无backend，BCL Exe及Host强持 |
| 4 正常/失败/重复/并发/关闭/回退断言 | 规格已接收 | 规格已接收 | §12.1 SF01–16按切片；真实Adapter SF17和UI SF18后续 |
| 5 Benchmark方法/维度/预算/统计来源 | 方法已接收、TargetPending | 方法已接收、TargetPending | §13/治理唯一统计；无目标NotEvaluated，不编客户值 |
| 6 唯一代码/Exe测试/命令/允许禁止 | 规格已接收 | 规格已接收 | §1.3/§10；工程未创建、未构建运行；实际实现须另行正式派发，不由本状态同步自动开工 |

2026-10-11内部工程/接线规格已闭合到附录B（SF-A1）与C（SF-W1）：唯一工程/Exe、构造/options、资源Owner、双无UI/双STA Host、借用viewport映射与有限退出不再留“待设计”。这两个外围切片保持 `PreparationIncomplete / NotReady`，待主控内容接收及各自真实运行资格；不改SF-C1/C2的已接收六项。

准确剩余门按§16.2分类：来源贡献、Golden/连续支撑与数值容差逐方法验收；native_rms按B.4已冻结可知的原生诊断语义，数学归一/单位确认只阻该指标的物理统计用途；viewport场景发布与坐标/授权的真实宿主映射按C.2交接，控件/Adapter的工程与签名已定义；平台事实Owner、客户性能与现场资格仍分别验。没有产品构建、HALCON、真实WPF、性能、计量、HIL/FAT/SAT/现场验收结果，本文也没有可发布Simulator承诺。

### 16.2 外围切片六项定位与准确剩余门（2026-10-11）

主控已回读 `0.4.0-prep` 附录B/C及本节，限定接收SF-A1/SF-W1本轮新增指导内容；SF-C1/C2已接收的六项保持。本接收结论更新§16.1末段的“待主控内容接收”状态，不改变API、算法、参数、Golden或准入范围；外围切片仍 `PreparationIncomplete / NotReady`，不标纯CoreReady，也不提升真实HALCON/WPF/资源/现场资格。

| DEV-GOV-010 §3.1 条件 | SF-A1 HALCON Adapter定位 | SF-W1 可选WPF定位 |
|---|---|---|
| 1 职责/依赖/真实第二消费者 | §2/4/15、B.1/B.5；参考面候选与连接器显式三角化/截面两无UI Host | §9、C.1/C.4；参考面工具与连接器工具各自STA装配，同Core/viewport公开合同 |
| 2 类型/签名/单位/Owner/资源/版本 | A.1–4、B.2–4；构造/options/限额/Close/Dispose/来源和native_rms | A.6、C.2–3；ViewOptions、scene provider、borrow bridge、原Task与回执，不复制viewport合同 |
| 3 无UI最小Host/公开端口 | B.5明确factory前根槽、两个参数化Host和有限收尾；不初始化WPF | 业务路径仍用B.5/§10无UI；C.4另列两STA控件与ViewportControl装配，借用service/session/root |
| 4 正常/异常/恢复/重复/并发/关闭 | §12.1 SF11/15/17、B.3/B.6的HA01–08；Unknown不返还Owner | §12.1 SF18、C.3–5的WU01–08；旧代、CAS冲突、撤权、退出、资源刷新回执 |
| 5 Benchmark维度/预算/统计 | §13及B.6；真实HALCON Mode，完整排空统计，TargetPending | C.5；算法与显示/交互/退出分别计时，唯一1920×1080验证视口；TargetPending |
| 6 唯一工程/Exe/发布/命令/允许禁止 | B.1/B.6；未建工程、未执行命令 | C.1/C.5；未建工程、未执行命令 |

两切片内部工程、公开构造、限额、消费装配和恢复观察规格已在本文给出并获主控限定内容接收；本轮不存在以“Host以后设计”代替这些事项的开放项。**SF-A1/SF-W1保持 `PreparationIncomplete / NotReady`**；内容接收不等于真实Adapter或WPF资格。未来发现具体C#重载/封送或布局差异只修受影响外围段，不重审已接收Core。

| 门类 | 准确未闭合事项 | 只阻断的范围 |
|---|---|---|
| 内部实现/编译 | B/C新增指导内容已限定接收；后续须正式派发Adapter/公共程序集接线实现，按唯一工程及HA/WU断言编译、运行。本文不声称代码或公共程序集消费编译已完成 | SF-A1/SF-W1实现与运行资格；SF-C1/C2规格接收保持，本轮不授权产品工程或代码写入 |
| 跨模块/宿主交接 | 实际surface-data→viewport源发布、来源贡献、精确SurfaceIdentity/CalculationIdentity与SourceBinding/overlay映射、原Owner场景发布、IM-007坐标及授权实际接线；平台Schema/事实Owner映射 | 使用该场景的可见呈现/高亮/产品集成。C.2的模块bridge已定义，缺映射明确拒绝；不阻纯计算 |
| 实际运行 | cv2参数/属性读回、单位往返、来源token与original_point_indices、不可中断排空/资源失败；逐方法Golden含孔洞/阶梯/薄壁与数值容差；B.4的统计辨别试验；真实viewport/DevExpress/WPF/UIA三语、双STA、安全退出与完整排空性能 | 对应方法/显示的运行资格。RMS数学归一未知仅阻其物理统计用途，原生诊断输出合同已闭合 |
| 客户/物理/生产 | 两消费者真实Profile及性能目标、连续支撑/标定与计量允差、生产事实提交、客户现场验收 | 相应计量/工艺/性能/生产用途；不把这些值编成通用Core默认 |

没有新增硬件SDK实现、可发布Simulator、自动生产算法链、implicit或SF-A1的worker隔离承诺；§4.2与Core Contract0.3支持面保持。本轮明确的几何描述/局部曲率与参数建议另由附录D冻结，不伪装为已接收Core操作；上游H隔离只在实际显式消费该上游端口时适用。

B.4的native_rms四步运行辨别门保留，只阻该原生指标的物理统计用途；不得凭名称开根或猜n归一。精确几何残差使用独立几何真值途径，不能用NativeUnknown原值替代。真正剩余是上述实现/公共程序集编译、来源贡献/原Owner场景发布与IM-007/授权实际接线、Golden/性能/WPF及客户物理资格，不再把本轮已接收指导内容列成待接收。

## 17. 依据与自审记录

本指导依据并保持边界一致的资料：

- `docs/independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md`（IM-034 准入与金标准章节）；
- `docs/shared-modules/packages/PKG-031_Features3D.md`（单表面职责、反例和 060 分界）；
- `docs/shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md`（采样、法向、primitive、拓扑和资源语义）；
- `docs/shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md`（高度场输入边界）；
- `docs/shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md`（量测与积分边界）；
- `docs/01-governance/DEV-GOV-005_模块独立性与复用标准.md`、`DEV-CONTRACT-002`（独立 DLL、事件、资源和 Owner 规则）；
- HALCON 26.05 官方算子页面：`halcon算子手册/operators/{select_points_object_model_3d,sample_object_model_3d,surface_normals_object_model_3d,smooth_object_model_3d,fit_primitives_object_model_3d,connection_object_model_3d,triangulate_object_model_3d,distance_object_model_3d,prepare_object_model_3d,get_object_model_3d_params}.html`；页面标题为 `26.05.0.0`，实现仍须通过适配器和目标运行时验证；
- `ImageLibDotNet` 目标引用的公共程序集、公开文档和适配器编译核对记录（不读取或依赖 AsunImage 源码树）。

### 17.1 本轮直接证据与迁移限制

- HALCON 26.05 本地原文追加读取：[intersect_plane_object_model_3d](../../../halcon算子手册/operators/intersect_plane_object_model_3d.html)、[segment_object_model_3d](../../../halcon算子手册/operators/segment_object_model_3d.html)、[hom_mat3d_to_pose](../../../halcon算子手册/operators/hom_mat3d_to_pose.html) 与既有normal/smooth/triangulate/fit/get-params/distance/prepare。已落实：all只返最小残差一种；plane三算法相同；greedy默认hole_filling=40须关闭；xyz_mapping默认补洞须置0；不可取消时等待返回；内部curvature不冒公共输出；截面需平面pose且每相交三角产生线段。这是资料核对，不是算子执行验证。
- [Open3D固定快照](../../references/open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/)：commit `b6c5e196384ad71e75b6e6f9c5da22d046221f1d`，上游version.txt为 `0.20.0` 开发快照，非宣称已发布版本；MIT许可证原件已读。2026-10-09通过GitHub raw比对 `cpp/open3d/geometry/PointCloud.cpp`（SHA-256 `9d31ff094145e2be55d17b18da1ada84039522fc7878914c347c118ec5fb1ee1`）及 `cpp/tests/geometry/PointCloud.cpp`（`b8041cb7d6f5ad0a60e2ef136d580c1a8c21704cea7aeced1b3398fdbc7241b1`）与本地完全一致，读取VoxelDownSampleAndTrace/EstimateNormals测试与实现。本轮恢复复用该证据，不重新下载。
- 同commit线上读取 [EstimateNormals.cpp](https://github.com/isl-org/Open3D/blob/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/geometry/EstimateNormals.cpp) SHA-256 `dcb47fbb2d80a9683e85831ce80ad807b3e86680b8a2dadb17a15383a09f9755` 及version/dependency文件，未写参考原件。可迁移强项是固定坐标原点的floor桶、贡献索引保留、独立法向方向步骤和可读测试；限制是unordered_map输出次序、质心降低尖峰、EstimateNormals退化回填旧法向/+Z不满足本模块有效性，测试中covariance两项仍DISABLED/NotImplemented，不能当全面覆盖。依赖涉及C++、Eigen、nanoflann、TBB（并行法向）、Qhull/fmt及可选CUDA/GUI/Python；只借鉴边界/测试，不引入生产依赖、不复制平行采样/法向算法、不运行上游测试冒本模块资格。
- DevExpress官方在线docs访问HTTP403且本会话无dxdocs工具；已读本机 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/DevExpress.Xpf.{Docking,PropertyGrid,Grid,Core}.v25.2.xml` 的公开类型/属性说明和程序集FileVersion=25.2.3.0，形成§9所列控件绑定。没有核依赖授权、下载安装、修改版本或创建UI原型；真实布局/Dispatcher/IME/UIA仍待WPF切片。
- 2026-10-11读取26.05 [fit原文](../../../halcon算子手册/operators/fit_primitives_object_model_3d.html)（SHA-256 `ae7ac101f3f1b19054972070b29192a06ebff514d6d997bf7dae887a7377fa83`）与[get-params原文](../../../halcon算子手册/operators/get_object_model_3d_params.html)（`f2a7a313eb79f11d14e095af651301e47bd6e33118797890537189c62a1d70e6`），确认primitive_rms只有quadratic residual/length1与存在标记，没有开方/分母/物理单位公式；B.4据此冻结原生诊断。另读同版gen_object_model_3d_from_points与set_object_model_3d_attrib[_mod]的标准/扩展属性布局，对应B.3；只读取公开资料，不扫描AsunImage内部。
- 固定Open3D快照 [PointCloudSegmentation.cpp](../../references/open-source/isl-org_Open3D/b6c5e196384ad71e75b6e6f9c5da22d046221f1d/cpp/open3d/geometry/PointCloudSegmentation.cpp) SHA-256 `44487a05b6f3b70a4da2a856220638b60e4c483350572d098fc1ea4c073d7751`，直接读取EvaluateRANSACBasedOnDistance/GetPlaneFromPoints/SegmentPlane及既有PointCloud.cpp测试的SegmentPlane/Deterministic段；它明确自己的inlier RMSE，但不能证明HALCON同定义。版本/MIT/依赖沿既有固定证据，未新增算法依赖或冒上游测试已运行。
- C.2直接核[viewport唯一公开指导](../viewport/DEVELOPMENT-GUIDE.md)的Session/Context/SourceBinding/OverlayLayer/UiBinding与真实Control.BindAsync，保留OwnSession=false、Bind内部root reservation、原Task、Presented/cleanup回执和Unbind边界。DevExpress本机XML再次只确认AllowClose/AllowDrag、Orientation、SelectedObject与SuperTip；未读到的TreeList数据源/LayoutPanel.Content成员不冒确认。

### 17.2 两轮有限反例自审范围

2026-10-10第一轮按实际操作输入→参数→native/托管处理→输出走SF01/02/10–15，关闭无效NaN冲突、all竞争集误读、隐藏滤波/三角化、距离自动Target、保孔默认、SourceMapping冒充来源问题；第二轮按无UI消费者与页面挂接走SF03–09/16/18，关闭重复ID/Busy登记、等待取消与操作取消混用、页面借用service关闭、迟到代次、Unknown误归还、hash编码与旧示例冲突。这里是正文反例走查，不是已运行测试PASS；定向结构/API/示例/链接检查仅证明本指导一致性。

自审结论：本文未写入 PCB/PCBA/AOI/SPI/点胶/涂覆判定，未把配准、参考资格、量测或设备副作用纳入模块核心；所有计算结果、错误、取消、超时、资源排空和版本回退均可由无 UI 宿主表达；生产状态保持 `DesignReview/Prep`。

2026-10-11追加两轮有限自审，仅审SF-A1/SF-W1外围，不重审已接收Core。第一轮按正常输入→参数/限额→压紧组装→单算子→原生读回→异常→恢复检查HA01–08，修正原始总点数预算、估计系数悬空、RMS误单位、清理失败后的账本/预约保留；第二轮从没有产品Shell的消费者按签名逐步装配B.5/C.4，检查WU01–08，修正Connector截面参数入口、原SourceId/坐标/单位映射结构、Bind不可重复reserve、跨语言部分刷新、late bind与原Dispatcher/inner Task保留。两轮均是文档反例自审，不是运行PASS；实际编译/HALCON/WPF/资源故障/Golden/性能/客户验收未执行。

## 附录 A：Module API Contract 0.3（模块局部设计；逐切片准入）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片唯一实施依据；准入以§16.1主控逐切片接收为准，不以附录存在推断其它切片通过。实现者不得另造第二套核心DTO、状态机或错误语义。

- `Module API Contract 0.3` 覆盖纯 Core、受控模拟端口及可选 UI 接入形状，不把平台 C-01～C-08、客户工艺值、产品数据库字段或厂商类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- HALCON 26.05 经 `cv2` 使用；仅具体重载/参数封送歧义通过消费编译解决，不核算子存在或依赖授权。真实适配与 UI 验收不阻断已冻结的纯 Core 规格接收。
- 2026-10-10主控已接收SF-C1与SF-C2为 `ModuleCoreImplementationReady`，仅规格准备，范围与六项定位见§16.1；其余切片保持原后续门。该状态不代表真实HALCON Adapter、可发布Simulator（本文无此承诺）、WPF、平台映射、性能或现场资格通过，也不表示Core代码/测试已实现或执行。

### A.1 快照、工厂与规范身份

以下都是 `Asun.Modules.SurfaceFeatures3D` 中的模块局部类型。`ImmutableArray<T>` 不允许 default（可选集合用 Empty），嵌套集合同样深冻结；不得将只读接口包住可写数组冒充不可变。factory 是唯一快照构造入口，没有 public 构造器、set/init 或 native 属性。

```csharp
public readonly record struct Point3(double X, double Y, double Z);
public readonly record struct Vector3(double X, double Y, double Z);
public readonly record struct Triangle(int A, int B, int C);
public readonly record struct Edge(int A, int B);
public sealed record EvidenceRef(string Id, string Revision, string Sha256);
public sealed record SurfaceIdentity(string SurfaceId, long Revision, string ContentHash);
public sealed record SupportDeclaration(SurfaceIdentity Source, EvidenceRef Evidence);
public sealed record PointAttribute(string Name, string Unit,
    ImmutableArray<double> Values, ImmutableArray<bool> Validity);
public sealed record XyzMapping(int Width, int Height,
    ImmutableArray<int> Row, ImmutableArray<int> Column);
public sealed record PrimitiveData(PrimitiveKind Kind,
    ImmutableArray<double> Parameters, ImmutableArray<double> Extent);
public sealed record SurfaceSnapshotData(string SurfaceId, long Revision,
    string CoordinateFrame, LengthUnit LengthUnit, string DomainId,
    ImmutableArray<Point3> Points, ImmutableArray<bool> Validity,
    ImmutableArray<string?> InvalidReasons, ImmutableArray<int> SourceIndex,
    ImmutableArray<Vector3> Normals, ImmutableArray<bool> NormalValidity,
    ImmutableArray<Triangle> Triangles, ImmutableArray<ImmutableArray<int>> Polygons,
    ImmutableArray<Edge> Edges, ImmutableArray<PointAttribute> Attributes,
    XyzMapping? Mapping, PrimitiveData? Primitive,
    EvidenceRef? AcquisitionRef, EvidenceRef? CalibrationRef,
    EvidenceRef? ContinuousSupportRef);
public sealed record ValidationIssue(string Code, string Field, string ReasonKey);
public sealed record ValidationReport(bool IsAccepted, ImmutableArray<ValidationIssue> Issues);
public sealed record SnapshotCreateResult(SurfaceSnapshot? Snapshot, ValidationReport Validation);

// 签名约定：factory 的 Create 为静态方法；SurfaceSnapshot 属性只有 get。
// static SnapshotCreateResult SurfaceSnapshotFactory.Create(
//     SurfaceSnapshotData data, string? expectedContentHash = null);
// SurfaceSnapshot: SurfaceSnapshotData Data { get; }
//                  SurfaceIdentity Identity { get; }
```

Create 克隆 Data 全部集合，执行 §3.1 的结构/有效性检查并计算本模块 ContentHash；无效返回 Snapshot=null 与按 Field/Code ordinal 排序的所有 issue。expectedContentHash 仅用于同版本局部快照 import，一旦提供必须64位小写并匹配，失败 `S3D-004`；上游 EvidenceRef 的 hash 不拿来比较局部编码。点/属性有效时值必须有限；无效原因非空；NormalValidity=true 需点有效且法向有限、非零。Normals 与 NormalValidity 必须同时 Empty 或点数长度。重复 SourceIndex/属性名拒绝；重合坐标合法。Primitive.Kind 不允许 All，其 raw 参数必须符合本地 get-params 的 plane/sphere/cylinder 排列及长度4/4/7、半径为正；Extent 原始序列可 Empty，不解释成产品域。

Snapshot 可以暂存空几何（例如 primitive Target）；Execute 对 Source 检查至少一个有效点，TargetKind=Primitive 例外仅作用于 Target。Triangle/Edge 顶点下标范围和 polygon≥3 在 factory 验证；重复顶点/重复面不在 factory 隐藏删除，而作为 Topology 结构退化。面引用无效点时适配前筛除并统计。ContinuousSupportRef 只绑定调用者的连续支撑资格证据，不是本模块自授资格；不携带工艺判定或产品表键。

规范 hash 用 .NET BCL SHA-256。二进制前缀是 UTF-8 `surface-features-3d.snapshot/0.3`；字段按以上 Data 声明顺序写入，整数 Int32/Int64 小端，double 按 BitConverter.DoubleToInt64Bits 的原始位小端（包括无效点的 NaN、±0），bool 为0/1；枚举按 A.2 固定 ordinal 的 Int32；string 用 Int32 UTF-8 字节长度+字节，null 用长度-1；每集合 Int32 长度+按原序元素，nullable record 用0/1前缀再按声明顺序递归。Attributes 先按 Name ordinal 排序后冻结；其余点/面顺序是输入语义，不能为 hash 重排。factory 的 ContentHash 不含自身hash字段。EvidenceRef 的 Id/Revision/hash 均参与；本协议用于局部重放，不替平台序列化。

CalculationIdentity 前缀为 `surface-features-3d.calculation/0.3`，按 Source.Identity→Source.unit/frame→Target.Identity/unit/frame（没有为null）→具体参数类型名与声明顺序字段→固定参数列表→Purpose→ContractRevision→ProfileRevision→ModuleVersion→BackendId/CapabilityVersion 编码后 SHA-256。参数使用A.2深冻结原始强类型值（包括源单位、法向原向量），不以culture相关字符串或Reflection生成；固定参数按Name ordinal排序，类型bool/int/double/string以类型名+按A.1编码的值，语义单位另写入；剩余deadline不是固定几何参数。Topology backend固定 `managed-topology/0.3`，不随无关注入后端变化。无请求缓存；Budget/Timeout是执行边界单独诊断，不改变几何身份；native剩余timeout只停止，失败无payload。未完成规范化前拒绝的CalculationIdentity=null。

### A.2 强类型请求与方法参数

枚举名及值按每行所列顺序固定为 `0..n-1`，未知整数拒绝，不用文本别名。后续新增值只追加，改变既有含义升契约 Major。

| 类型 | 值（顺序固定） |
|---|---|
| LengthUnit | Meter, Millimeter, Micrometer |
| SurfacePurpose | DatumCandidate, MeasurementSupport, DisplayDerived |
| PrimitiveKind | Plane, Sphere, Cylinder, All |
| FitAlgorithm | LeastSquares, LeastSquaresHuber, LeastSquaresTukey |
| SamplingMethod | Fast, FastComputeNormals, Accurate, AccurateUseNormals, XyzMapping, XyzMappingComputeNormals, FurthestPoint, FurthestPointComputeNormals |
| NormalMethod | Mls, Triangles, XyzMapping |
| SmoothMethod | Mls, XyzMapping, XyzMappingComputeNormals |
| MappingFilter | Median, MedianSeparate |
| ConnectionFeature | Distance3D, Angle, DistanceMapping, Mesh, Lines |
| TriangulationMethod | PolygonTriangulation, XyzMapping, Greedy |
| DistanceTargetKind | Points, Triangles, Primitive |
| DistanceMethod | ExactLinear, ExactKdTree, ExactPrimitive, ApproximateVoxel |
| SurfaceExecutionStatus | Completed, Rejected, Failed, Cancelled, TimedOut |
| QualityState | Complete, Insufficient, Unknown |
| MappingState | Complete, Partial, Unavailable |
| DistanceValueKind | Exact, Approximate, AtLimit, Invalid |
| ResourceState | NoneAcquired, Active, Drained, ResourcesReleased, Unknown |
| DrainState | Drained, Pending, Unknown |
| NotificationKind | Accepted, Validated, Started, StageChanged, Progress, CancelRequested, Draining, Drained, ResourcesReleased, Completed, Rejected, Failed, Cancelled, TimedOut, ReleaseUnknown |

```csharp
public sealed record ResourceBudget(int MaxInputPoints, int MaxOutputPoints,
    int MaxFaces, long MaxContributions, long MaxBytes, bool RequireHardMemoryLimit);
public sealed record SurfaceFeatureRequest(string RequestId, SurfaceSnapshot Surface,
    SurfaceFeatureParameters Parameters, TimeSpan Timeout, ResourceBudget Budget,
    SurfacePurpose Purpose, string ContractRevision, string ProfileRevision);
public abstract record SurfaceFeatureParameters;
public sealed record AttributeRange(string Name, string Unit, double Min, double Max);
public sealed record SelectParameters(ImmutableArray<AttributeRange> Conditions)
    : SurfaceFeatureParameters;
public abstract record SamplingSize;
public sealed record PhysicalSpacing(double Length) : SamplingSize;
public sealed record PixelSpacing(double Pixels) : SamplingSize;
public sealed record PointCount(int Count) : SamplingSize;
public sealed record SampleParameters(SamplingMethod Method, SamplingSize Size)
    : SurfaceFeatureParameters;
public abstract record MlsSigma;
public sealed record AbsoluteSigma(double Length) : MlsSigma;
public sealed record RelativeSigma(double Factor) : MlsSigma;
public sealed record MlsOptions(int K, int Order, MlsSigma Sigma, bool ForceInwards);
public sealed record NormalsParameters(NormalMethod Method, MlsOptions? Mls)
    : SurfaceFeatureParameters;
public sealed record MappingSmoothOptions(MappingFilter Filter, int Width, int Height);
public sealed record SmoothParameters(SmoothMethod Method, MlsOptions? Mls,
    MappingSmoothOptions? Mapping) : SurfaceFeatureParameters;
public sealed record RadiusRange(double Min, double Max);
public sealed record FitParameters(PrimitiveKind Kind, FitAlgorithm Algorithm,
    RadiusRange? Radius, SupportDeclaration PrimitiveSupportRef) : SurfaceFeatureParameters;
public sealed record ConnectParameters(ConnectionFeature Feature, double? Value)
    : SurfaceFeatureParameters;
public sealed record GreedyTriangulationOptions(double Radius, int K,
    double OrientToleranceDegrees, double LatitudeToleranceDegrees,
    double VerticalRadiusFactor, bool OrientationConsistent,
    bool FixFlips, bool PrefetchNeighbors);
public sealed record MappingTriangulationOptions(Vector3 ViewDirection,
    double MaxViewAngleRad);
public sealed record TriangulateParameters(TriangulationMethod Method,
    GreedyTriangulationOptions? Greedy, MappingTriangulationOptions? Mapping)
    : SurfaceFeatureParameters;
public sealed record TopologyParameters() : SurfaceFeatureParameters;
public sealed record SectionParameters(Point3 PlaneOrigin, Vector3 PlaneNormal)
    : SurfaceFeatureParameters;
public sealed record DistanceParameters(SurfaceSnapshot Target,
    DistanceTargetKind TargetKind, DistanceMethod Method, bool Signed,
    double MaxDistance, bool Approximate) : SurfaceFeatureParameters;
```

DTO 不提供任何生产默认。标识/版本不得空白，不 Trim 后悄悄改身份；Timeout 有限正数，Budget 全正且数组/乘积 checked 防溢出，MaxInputPoints 覆盖 Source+Target 总点数、MaxFaces 覆盖请求持有/输出的三角/多边形总面数，MaxContributions 为映射总条目上限。引用型 null、ImmutableArray default、未列派生 parameter 类型、组合多余字段拒绝 `S3D-001`。Connect Angle 无法向、mapping 无mapping、primitive Target无primitive 皆在native前拒绝 `S3D-005`。Mls/Mapping/Greedy 按 Method 只能一个适用配置，禁止将不适用配置作为“忽略的字段”。固定 policy 在规范化参数中回显。

Fit的PrimitiveSupportRef是宿主声明该域对应单primitive的分割证据，Source必须逐字段等于请求Source.Identity；缺失S3D-006，不匹配S3D-014，不由Core再分割。Normal/MLS/Smooth/Greedy精密用途的ContinuousSupportRef必须非null且有版本/hash，所有EvidenceRef的Id/Revision非空、hash64小写；连续性文档与snapshot的物理关联由上游Owner负责，Core不读外部证据文件，引用本身随快照hash冻结。声明不保证工艺资格，不能以点数代替物理证据。Topology/Section/三角法向无有效triangle在native前S3D-005。source改变需新支持声明，Core只校验关联不评客户阈值。

Normalize 不估计建议参数：Length 按源单位换米；Distance Target 不同 LengthUnit 允许独立换米而 frame 必须相同，结果恢复 Source 单位。Direction/PlaneNormal 非零有限后按稳健范数显式归一化并回显；不把零向量填 +Z。Section 的平面位姿用最小绝对法向分量的坐标轴为 seed（tie=X→Y→Z），t=normalize(seed−n·dot(n,seed))、b=n×t，旋转列为(t,b,n)，translation=PlaneOrigin米；适配器经 `cv2.hom_mat3d_to_pose` 把3×4矩阵转plane pose，不能另接HOperatorSet。该算子属于现有26.05标准转换，不在纯Core执行。primitive返回参数保持官方 raw 序列并单位转换，不猜 Hessian 正负号或把 NativeRms 按名字当已资格测量统计。

### A.3 返回值、来源及生命周期摘要

```csharp
public sealed record SourceMapping(SurfaceIdentity Parent, MappingState State,
    ImmutableArray<ImmutableArray<int>> PointContributors,
    ImmutableArray<ImmutableArray<int>> FaceContributors,
    ImmutableArray<string> ReasonKeys);
public abstract record SurfaceFeaturePayload;
public sealed record SurfacePayload(SurfaceSnapshot Geometry, SourceMapping Mapping)
    : SurfaceFeaturePayload;
public sealed record PrimitivePayload(PrimitiveData Primitive,
    ImmutableArray<int> InputSupportIndices, double? NativeRms,
    string NativeRmsUnit, ImmutableArray<string> Limitations)
    : SurfaceFeaturePayload;
public sealed record ComponentData(ImmutableArray<int> SourceIndices);
public sealed record ComponentsPayload(ImmutableArray<ComponentData> Components,
    ImmutableArray<int> UnassignedIndices) : SurfaceFeaturePayload;
public sealed record BoundaryPath(ImmutableArray<int> VertexIndices,
    bool Closed, bool Ambiguous);
public sealed record TopologyPayload(ImmutableArray<Edge> BoundaryEdges,
    ImmutableArray<Edge> NonManifoldEdges, ImmutableArray<Edge> OrientationConflicts,
    ImmutableArray<int> RepeatedVertexFaces, ImmutableArray<int> DuplicateFaces,
    ImmutableArray<BoundaryPath> BoundaryPaths,
    ImmutableArray<ImmutableArray<int>> FaceComponents,
    string GeometryQualification) : SurfaceFeaturePayload;
public sealed record SectionPayload(Point3 PlaneOrigin, Vector3 PlaneNormal,
    SurfaceIdentity SourceMesh, ImmutableArray<Point3> Points,
    ImmutableArray<Edge> Lines, SourceMapping Mapping,
    bool NoIntersection, ImmutableArray<string> Limitations) : SurfaceFeaturePayload;
public sealed record DistanceSample(int SourceIndex, double? Value,
    DistanceValueKind Kind, int? ClosestTargetIndex);
public sealed record DistancePayload(SurfaceIdentity Target,
    ImmutableArray<DistanceSample> Samples, bool Signed,
    ImmutableArray<string> Limitations) : SurfaceFeaturePayload;
public sealed record SupportEvidence(int InputCount, int ValidCount, int OutputCount,
    int ExcludedCount, MappingState Mapping, QualityState Quality,
    bool UseQualificationEvaluated, ImmutableArray<string> ReasonKeys);
public sealed record EffectiveParameter(string Name, string Unit, string Value);
public sealed record ExecutionDiagnostics(string BackendId, string CapabilityVersion,
    string ModuleVersion, ImmutableArray<EffectiveParameter> EffectiveParameters,
    ImmutableArray<StageTiming> StageTimings,
    TimeSpan EndToEnd, TimeSpan DrainDuration, TimeSpan? CancelToDrain,
    long PeakManagedBytes, long? PeakNativeBytes, long ReservedBytes,
    ResourceState ResourceState, string? StopReason, string? NativeErrorCode,
    string? NativeErrorText, ImmutableArray<string> SecondaryErrors);
public sealed record StageTiming(string Stage, TimeSpan Duration);
public sealed record SurfaceFeatureResult(string RequestId, string? CalculationIdentity,
    SurfaceIdentity? Source, string? CoordinateFrame, LengthUnit? LengthUnit,
    SurfacePurpose? Purpose, string ContractRevision, string ProfileRevision,
    SurfaceExecutionStatus Status,
    SurfaceFeaturePayload? Payload, SupportEvidence Support,
    ImmutableArray<ValidationIssue> Issues, ExecutionDiagnostics Diagnostics,
    bool Drained, bool ResourcesReleased);
public sealed record SurfaceFeatureProgress(string RequestId,
    string? CalculationIdentity, long SourceRevision, long EventSequence,
    NotificationKind Kind, string Stage, double? Fraction, string? ReasonKey);
public sealed record DrainReport(DrainState State,
    ImmutableArray<string> OutstandingRequestIds, ResourceState ResourceState);
public sealed record MethodCapability(string Operation, string Method,
    bool CanInterrupt, bool HasHardMemoryLimit);
public sealed record CapabilityReport(string BackendId, string CapabilityVersion,
    string ContractRevision, ImmutableArray<MethodCapability> Methods);
```

SourceMapping 的每条贡献引用 Parent 的 SourceIndex，FaceContributors 引用父快照面的原始下标（triangles在前、polygons在后），不能用输出下标冒充；Complete 时列表长度覆盖全部输出点/面且每条非空、有序无重复。Partial/Unavailable 不给空列表伪装 Complete。identity/原生值已脱离handle；不支持读回的 native peak 用null，不能填0。NativeRmsUnit按B.4固定NativeUnknown，不得进入消费者精确统计；plane/cylinder/sphere的raw metadata按类型unit schema换算。

NativeRms保留native原值，NativeRmsUnit固定=`NativeUnknown`（已知是HALCON primitive_rms，未知的是物理归一与单位，非未知字段定义），Limitations含 `HalconPrimitiveQuadraticResidual/NativeInputMeter/PhysicalStatisticNotQualified`；读取规则和适用域见B.4，不按Source单位强行缩放、不进入精确统计，all选择由native自己完成。Primitive.Parameters：plane前三法向无量纲/第4长度，sphere四项长度，cylinder前三中心长度/中三轴无量纲/第7长度；Extent按官方类型长度属性换源单位，无资料对应时Empty+限制。Distance AtLimit对signed以abs(Value)比较MaxDistance；ClosestTargetIndex=-1映射null，primitive/voxel不支持closest时null，不伪造index0。

SupportEvidence.InputCount为Source总点数，ValidCount为Validity=true数量；OutputCount为Surface输出点数/Primitive个数/Components总分配点数/Topology参与face数/Section交点数/Distance样本条数，操作类型决定且在EffectiveParameters写CountKind；ExcludedCount仅计从原始Source点被排除数量，不用Input−Output（fit只有1primitive不会说其余点被丢弃）。孔洞/边界具体计数由TopologyPayload给出，不假称所有操作均有可读洞计数。StageTiming固定阶段Validate/Estimate/Reserve/Native/Readback/Freeze/Drain/Release，不适用为零并标说明；纯Core排空时间为托管任务退出到工作资源归还。Fraction/计时/单位/错误不以单bool合并。

成功payload型唯一：Select/Sample/Normals/Smooth/Triangulate→SurfacePayload；Fit→PrimitivePayload（没有primitive为 Completed+Insufficient、payload=null）；Connect→ComponentsPayload；Topology→TopologyPayload；Section→SectionPayload；Distance→DistancePayload。输入/能力拒绝、运行失败、取消和超时 payload=null；部分支持为 Completed+Insufficient 并保留原始分母。所有首发 UseQualificationEvaluated=false，本模块几何 Complete 不表示量测或生产资格。DisplayDerived 的贡献不可用必须显示限制；DatumCandidate/MeasurementSupport 遇必须贡献缺失拒绝 `S3D-011`，不发布候选。

进度 Fraction 只能null或[0,1]，原生无进度时用null，不造线性百分比。Accepted/Validated/Started/Draining/Drained/ResourcesReleased/终态顺序按 §5–7；重入/Closing/Duplicate/Busy等接纳前拒绝没有Accepted通知，返回NoneAcquired空资源已闭合结果。正常发布终态时 Drained/ResourcesReleased 均true；释放失败增加 ReleaseUnknown→Failed，flags如实为false/未知，任务可返回失败摘要但没有payload。这是“等待归还才成功”的异常分支，不能伪装终态已归还。

### A.4 服务 factory、端口及 Owner

```csharp
public interface ISurfaceFeatures3DService : IAsyncDisposable
{
    CapabilityReport GetCapabilities();
    ValidationReport Validate(SurfaceFeatureRequest request);
    SurfaceFeatureResult Execute(SurfaceFeatureRequest request,
        CancellationToken cancellation = default);
    ValueTask<SurfaceFeatureResult> ExecuteAsync(SurfaceFeatureRequest request,
        IProgress<SurfaceFeatureProgress>? progress = null,
        CancellationToken cancellation = default);
    ValueTask<DrainReport> DrainAsync(TimeSpan waitBudget,
        CancellationToken waitCancellation = default);
    ValueTask<DrainReport> CloseAsync(TimeSpan waitBudget,
        CancellationToken waitCancellation = default);
}
public sealed record SurfaceFeatures3DServiceOptions(int MaxRequestIds);
public static class SurfaceFeatures3DServiceFactory
{
    public const string ContractRevision = "surface-features-3d.core/0.3";
    // 设计签名；实现体由获准 SF-C1 编写，不是现存产品代码。
    // public static ISurfaceFeatures3DService Create(I3dSurfaceBackend? backend,
    //     IMemoryAdmission memory, TimeProvider clock,
    //     SurfaceFeatures3DServiceOptions options, IDiagnosticsSink? diagnostics = null);
}
public sealed record BackendEstimate(long ManagedBytes, long NativeBytes,
    long Contributions, bool HasHardMemoryLimit);
public sealed record BackendInvocation(string RequestId, SurfaceSnapshot Source,
    SurfaceFeatureParameters Parameters, ResourceBudget Budget,
    ImmutableArray<EffectiveParameter> EffectiveParameters,
    TimeSpan RemainingTime, string CalculationIdentity);
public sealed record BackendOutcome(SurfaceExecutionStatus Status,
    SurfaceFeaturePayload? Payload, SupportEvidence Support,
    ImmutableArray<ValidationIssue> Issues, bool NativeDrained,
    bool NativeResourcesReleased, long? PeakNativeBytes,
    ImmutableArray<StageTiming> StageTimings,
    string? NativeErrorCode, string? NativeErrorText);
public interface I3dSurfaceBackend
{
    CapabilityReport GetCapabilities();
    BackendEstimate Estimate(SurfaceSnapshot source, SurfaceFeatureParameters parameters);
    ValueTask<BackendOutcome> RunAsync(BackendInvocation invocation,
        IProgress<SurfaceFeatureProgress>? progress, CancellationToken stopRequested);
}
public interface IResourceLease : IDisposable { long Bytes { get; } }
public interface IMemoryAdmission { IResourceLease? TryReserve(long bytes); }
public interface IDiagnosticsSink { bool TryWrite(SurfaceFeatureResult result); }
```

Create 返回新实例、无hidden window/init；memory/clock/options不能为空，options.MaxRequestIds>0，构造配置错误抛 ArgumentException/ArgumentNullException（无取得资源），请求领域错误用result/ValidationReport。backend=null 只提供 managed Topology，其他操作在native前 `S3D-005`；native能力由backend快照与本指导支持面取交集，不反射猜能力。GetCapabilities 无副作用，服务生命周期内能力版本固定；变化必须新实例。TimeProvider 是 .NET BCL，native真实运行不以模拟时间证明性能。SF-C1 Exe 用自定义受控 TimeProvider+异步闩锁端口，按接口注入，无公开生产Simulator程序集或随机“仿真算法”承诺。

Factory/Snapshot设计签名即上述注释所列，不提供由实现者发明的额外构造或服务获取。输入控件/反序列化发现Curvature/Implicit操作名时在边界以S3D-005反馈未开放；Core没有对应DTO，未登记派生parameter对象按S3D-001处理。Validate不查询IMemoryAdmission当前余量，Estimate是独立接纳阶段；预检通过不保证下一执行能预约。ContractRevision必须完全匹配factory常量，模块发布ModuleVersion从本程序集固定AssemblyInformationalVersion取得，不由宿主传入改写。

Core拥有：私有生命周期、RequestId集合、计时器/stop token、通知记录与每次 TryReserve 获得的 lease。宿主拥有：backend实例、memory实例、输入快照及结果后续保留。backend拥有：每Run独占native模型/索引树/工作buffer并负责所有成功/失败/停止路径在 finally 清理；端口只交托管结果，Run返回不能仍有native在使用其参数。允许返回明确 NativeDrained/NativeResourcesReleased=false 的故障报告，禁止 `Task.WhenAny/WaitAsync` 先返并偷偷运行 native。端口 native exception必须转BackendOutcome；意外throw视为无法确认清理→Failed/ResourceState.Unknown，不根据throw假定finally成功。

Estimate 在native分配前无副作用返回checked非负预估；Core加输入保留、托管读回与贡献费用核budget，TryReserve无法取得为Busy，超过MaxBytes为BudgetExceeded。Estimate或TryReserve在未取得lease时throw→Failed/S3D-007且空资源归还事实，不能当已有native Unknown；已有lease后任何不确定归还才Unknown。Topology以checked `点输入字节+三角索引字节+3F边记录及关联表+边界路径+输出索引` 上界预估；.NET对象实际开销按实现统计，不能把仅3F×8当峰值。TryReserve的lease Dispose幂等；预约退还失败等同Unknown，保留实例隔离并封接纳。Core在NativeResourcesReleased=true后才归还预约；Unknown仍保留预约并交宿主，不吞异常。Dispose等待真实排空；已确认Unknown无法恢复则抛InvalidOperationException带未闭合ID，禁止摧毁借用backend。BackendOutcome阶段时长为nonnegative且仅Native/Readback/Drain/Release，Core合并自身Validate/Estimate/Reserve/Freeze，不重复累加端到端，不用StageTiming之和假称wall-clock。

Validate纯检查，Execute内重做必要检查防不匹配；一实例单在途无队列。RequestId登记有界，MaxRequestIds满拒绝 `S3D-008`，不淘汰ID再接受重复。同几何身份新RequestId为显式重算；Close永久封接纳，Drain只等待，waitCancellation只停止等待。Core控制RequestId/顺序号，backend progress只接受StageChanged/Progress并由Core重编号，不能由backend发布模块终态/释放事件。终态记录保存在返回result/诊断sink，UI投递晚于返回合法。

### A.5 托管拓扑算法与稳定顺序

SF-C2 只分析已给出的索引拓扑，是数据完整性/邻接分析，不替代 HALCON 三角化、视觉分割或连续曲率。先筛除含无效顶点的face并计数，保留原face ID；重复顶点面记RepeatedVertexFaces，按三下标排序键识别重复face（保留最小原ID，其余记DuplicateFaces），不让这些face参与关联计数。其他face各三条有向边附原face ID，按无向(min,max)键排序建关联：1个face→BoundaryEdges，2个face方向相同→OrientationConflicts，>2→NonManifoldEdges。邻接组件按共享有效边连通，不按仅共一个顶点合并；排序以最小原face ID，内部face ID升序。

边界图按节点度统计；每个边界连通子图度全为2时，从最小原顶点下标起、较小邻点先行，输出闭合环（首顶点只出现一次，Closed=true）；开放链在度1端点按较小者起，分叉图按最小未用边逐条生成path并标Ambiguous，不重复用边。所有输出边按(min,max)字典序，path按首顶点/序列ordinal排序。VertexIndices是当前Source顶点下标，经SourceIndex表回溯；原face IDs保持原下标。输出没有坐标容差合并，重复坐标仍不同顶点；结构连通不等于物理连续。共线/零面积、面自交、实体内外、外轮廓/洞及几何封闭资格不在纯索引算法授予，GeometryQualification固定 `NotEvaluated`；相关输入证据与Native检查另验。

### A.6 可选控件接入形状与双实例隔离

以下仅是 WPF 切片设计，不引入 Core/WPF循环引用，也不在文档阶段建原型。命名空间 `Asun.Modules.SurfaceFeatures3D.Wpf`，本基础控件只消费Core公开业务API；附录D.5分析控件另显式消费Halcon DLL的托管Analysis API，呈现依赖见C.1。控件 constructor私有、factory唯一；factory借用 service、text、授权和viewport实例，不拥有其Dispose。

| 公开类型/签名 | 确定语义 |
|---|---|
| `SurfaceFeatures3DControlFactory.Create(ISurfaceFeatures3DService service, IUiTextCatalog text, SurfaceFeatures3DViewOptions options): SurfaceFeatures3DControl` | 在宿主Dispatcher构造；options含 `InstanceId:string`、`Permission:ISurfaceFeatures3DPermission`、`Viewport:ISurfaceFeatures3DViewport`、`UiWaitBudget:TimeSpan`（有限正值），均非null；不取默认DataContext或全局主题 |
| `SurfaceFeatures3DControl.Attach(SurfaceSnapshot surface, string profileRevision, ResourceBudget budget, TimeSpan timeout): long` | Dispatcher调用，返回本实例递增Generation。新挂接先取消旧代次，不让旧结果覆盖新输入；已有运行服务仍Busy时预览不可用，不能强换请求 |
| `SetCulture(string culture): void` | 仅zh-CN/zh-TW/en-US或text明确登记语言，调用宿主提供 `IUiTextCatalog.Get(string key,string culture):string`；缺key拒绝该语言更新并保留前语言，不回显资源键 |
| `DetachAsync(TimeSpan waitBudget, CancellationToken waitCancellation=default): ValueTask<DrainReport>` | 只取消控件自己RequestId并撤销投影关联，等待自己的task；不调用借用service.Close。wait超时返回Pending，宿主接走task和服务，迟到通知丢弃；不可自动Disposal借用viewport/text |
| `ISurfaceFeatures3DPermission.Can(string command, SurfaceIdentity source): bool` | 命令仅Preview/EditParameters/ExportEvidence；执行前再查。撤权取消未完成Preview但不取消其他消费者；授权是宿主政策，不获得质量放行 |
| `ISurfaceFeatures3DViewport.Show(string instanceId,long generation,SurfaceSnapshot source,SurfaceFeatureResult? result,string layer):void`、`Highlight(string instanceId,long generation,ImmutableArray<int> sourceIndices):void`、`Clear(string instanceId,long generation):void` | Dispatcher投影且无native输入；generation旧则丢弃；layer仅Original/Derived/Normals/Topology/Section。显示取消/导出不直接控设备 |

控件状态是Empty/Editing/Running/Draining/Stale/Error/Detached，局部投影不作为Core事实。参数草稿、输入Generation、请求ID与通知Sequence实例隔离；编辑生成新草稿revision并让旧结果Stale，禁止采用旧结果。Preview冻结附录A请求，RequestId=`InstanceId:Generation:counter`，counter单调；运行中允许查看/编辑下一草稿但不重复运行。同进程两个控件用各自service/viewport/text实例；共享服务若Busy只反馈，不取消另一控件任务。导出发给宿主的明确事件 `EvidenceExportRequested(instanceId,generation,result)`，宿主拥有存储与审计，不在控件做数据库提交。

三语最小固定词条：Preview=`预览/預覽/Preview`，Cancel=`取消/取消/Cancel`，Discard=`丢弃草稿/捨棄草稿/Discard Draft`，Export=`导出证据/匯出證據/Export Evidence`，Draining=`正在结束计算/正在結束計算/Finishing Calculation`，Pending=`等待计算结束/等待計算結束/Waiting for Calculation`，Unknown=`资源状态不明/資源狀態不明/Resource State Unknown`，Stale=`输入已更新/輸入已更新/Input Updated`，MappingUnavailable=`来源映射缺失/來源對應缺失/Source Mapping Missing`。错误正文必须包含受影响operation与明确恢复，不显示“智能”“精准”“请耐心”等空泛文字。回收不确定时显示资源状态不明与宿主恢复动作，不显示可重新预览。

## 附录 B：SF-A1 HALCON Adapter公开接线与运行门

**接收状态（2026-10-11）：** 主控限定接收本轮新增的唯一Adapter/Exe、factory/options、Estimate非硬限、源/目标计账、固定HALCON顺序、native_rms原生诊断/NativeUnknown及双无UI Host原Owner指导内容。SF-A1仍 `PreparationIncomplete / NotReady`，不标纯CoreReady；Adapter/公共程序集编译、来源贡献、真实HALCON/资源/Golden/性能及客户物理资格未通过。B.4四步运行辨别门保留，仅阻该指标物理统计用途。

### B.1 唯一工程、依赖与发布边界

本附录补外围准备，保持Core Contract `surface-features-3d.core/0.3`；以下是设计签名，不是现存实现。后续获准SF-A1只写以下Adapter与测试目录，不改Core合同、WPF、共享工程、原件或AsunImage内部。本轮D/E的已规划描述、建议和消费桥也落在同外围工程，须按相应切片派发，不因目录共享混入SF-C1/C2。

| 项目 | 唯一落点/设置 |
|---|---|
| Adapter DLL | `src/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Halcon/Asun.Modules.SurfaceFeatures3D.Halcon.csproj`；namespace `Asun.Modules.SurfaceFeatures3D.Halcon` |
| 无UI Exe TestHost | `tests/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Halcon.Tests/Asun.Modules.SurfaceFeatures3D.Halcon.Tests.csproj`；同一Exe的 `--consumer reference/connector`、`--cases`、`--benchmark <path>`，不另造两个测试项目 |
| SDK/目标 | `Microsoft.NET.Sdk`、`net10.0-windows`、`PlatformTarget=x64`、`UseWPF=false`；Host `OutputType=Exe`。Core仍net10.0，不随Adapter改目标 |
| 引用 | DLL引用Core及用户既有AsunImage公共程序集；TestHost引用发布的Core/Adapter与BCL。程序集由既有依赖配置解析；不新接halcondotnet、不下载/换版/核授权，不创建依赖安装任务 |
| 发布 | `artifacts/modules/surface-features-3d/<ModuleVersion>/win-x64/halcon/`，含本模块Core/Adapter DLL、各自deps与XML公共说明；Host发布到同版本 `hosts/halcon-tests/`。ModuleVersion来自对应程序集，不拿指导版本冒发布版本 |

宿主部署继续使用已确定的AsunImage/HALCON 26.05；模块包不擅自复制替换宿主native运行时。WPF包另发C.1；无UI接入不携带WPF/DevExpress。回退沿§14：封接纳、真实排空、保留旧包/结果再切换，不在运行中覆盖DLL。

### B.2 公开构造、固定options与输入界面

```csharp
// namespace Asun.Modules.SurfaceFeatures3D.Halcon
public sealed record HalconSurfaceBackendOptions(
    int MaxInputPoints, int MaxOutputPoints, int MaxFaces,
    long MaxContributions, long MaxEstimatedBytes);
public static class HalconSurfaceBackendFactory
{
    // public static HalconSurfaceBackend Create(HalconSurfaceBackendOptions options);
}
public sealed class HalconSurfaceBackend : I3dSurfaceBackend, IAsyncDisposable
{
    // 无public constructor；唯一factory只作托管配置检查，不取得native资源。
    // public CapabilityReport GetCapabilities();
    // public BackendEstimate Estimate(SurfaceSnapshot source, SurfaceFeatureParameters parameters);
    // public ValueTask<BackendOutcome> RunAsync(BackendInvocation invocation,
    //     IProgress<SurfaceFeatureProgress>? progress, CancellationToken stopRequested);
    // public ValueTask<DrainReport> DrainAsync(TimeSpan waitBudget,
    //     CancellationToken waitCancellation = default);
    // public ValueTask<DrainReport> CloseAsync(TimeSpan waitBudget,
    //     CancellationToken waitCancellation = default);
    // public ValueTask DisposeAsync();
}
```

options各限额均为正、checked可表示；null/非法在factory抛ArgumentNullException/ArgumentException且无资源。限额由两个消费者显式给定，不设机器相关默认。factory每次返回新实例，能力快照固定；BackendId=`halcon-26.05/surface-features-3d`、CapabilityVersion=`sf-halcon/0.4`，模块程序集版本另记。GetCapabilities仅列§4.2可实施方法的交集；所有首发native方法 `CanInterrupt=false/HasHardMemoryLimit=false`，Topology不由Adapter重复实现。能力不按运行中异常悄悄增删；方法能力改变必须新实例/新能力版本。

只接受A.4 `BackendInvocation` 的托管快照和A.2强类型参数；Target已在DistanceParameters内，资源/超时/身份不能为空或任意字典。调用者正常经Core调用；直接端口消费也必须重查结构、按A.2将原参数/Source单位规范化并核EffectiveParameters、有效支撑、Contract方法支持面、限额和有限正RemainingTime，不能绕过Core验证。EffectiveParameters与规范参数不符拒绝 `S3D-001`，任何非法/不支持/关闭/Busy在native前返回对应Rejected、payload=null、NativeDrained/NativeResourcesReleased=true（指本次未取得资源，不冒其它在途请求归还）。预算取invocation和options逐项较小者；输入数含Source与Target原始总点数，面数含两者，不只核source或有效点；贡献数包括点与面父索引总项。`RequireHardMemoryLimit=true`一律 `S3D-005`，不把MaxEstimatedBytes命名为硬native限额。

Estimate纯托管、checked、不分配native/建树/查询工作集。本能力版本固定账本公式：n=Source+Target总点数，f=两输入总面数，e=两输入总边数，a=所有逐点属性存储项数，o=options.MaxOutputPoints，fo=options.MaxFaces，c=options.MaxContributions，g=greedy时Source有效点数×K（其它0），t=需prepare目标时Target有效点数（其它0）。ManagedBytes=`128*n+8*a+64*f+32*e+128*o+64*fo+8*c+16*g`；NativeBytes=`256*n+16*a+128*f+64*e+256*o+128*fo+16*g+128*t`；Contributions=c，HasHardMemoryLimit=false。系数是版本固定的准入估计，**不是官方native上界或实际CLR对象大小**；包含压紧表/两模型/读回/贡献/邻居/tree，Core另外计自身保留与预约。HA03对代表输入实测校核，不借估计宣称OOM隔离。checked(ManagedBytes+NativeBytes)超过request.MaxBytes/options.MaxEstimatedBytes或c超过request限额则native前拒绝；消费者应使Adapter各caps与对应request预算相容。实际PeakNativeBytes不可取得则null。返回后校验实际点/面/贡献与托管字节；超限无payload并清理，不截短为“成功”。

### B.3 native组装、处理、读回和资源Owner

一个Adapter实例最多一个Run，跨两个Core同时调用也无队列；用本实例原子接纳锁，第二调用返回 `S3D-013`，不以排队延长RemainingTime。native全部在非UI执行线程；每Run的原工作Task、RequestId/CalculationIdentity、参数快照、stop源和私有handle账本由Adapter强持到归还。Core拥有预约lease，Adapter只拥有本Run的native模型/tuple/树/buffer；Host拥有Adapter实例。禁止修改共享对象/调用进程级 `set_system`、改HALCON全局线程数，禁止把native对象交payload。

| 步骤 | 具体行为与不得隐含的变化 |
|---|---|
| 1 输入压紧 | 仅Validity=true点；按输入顺序建compactIndex→原输入下标→SourceIndex，XYZ按A.2换米。Target独立换米但frame同一。保留(0,0,0)，面/线只保留全部顶点有效者并显式计排除，不自动补面 |
| 2 私有模型 | 通过 `cv2.gen_object_model_3d_from_points` 构造本Run Source/Target。在私有模型以 `cv2.set_object_model_3d_attrib_mod` 写已有有效normal、triangles、polygons、lines、xyz_mapping及所需属性；只写官方标准属性和以`&`开头的扩展逐点属性 |
| 3 标准布局 | triangles每面3个compact下标；polygons/lines每项先count再下标。xyz_mapping依次width,height,n个row,n个column（总2n+2），只绑定压紧后同序点。部分无效法向/属性不写NaN入native；所选方法要求逐点值却有缺失时按§4校验拒绝或明确排除，不填0/+Z |
| 4 精确token | 用扩展点属性 `&sf_source_token` 存0..n-1的compact整数并 attached to points；在托管表回溯完整SourceIndex。不把hash/大业务身份塞double。subset/组件输出读取token时校验整数、范围、长度和唯一性；triangulate读取 `original_point_indices` 后同表回溯。normal/smooth点对应只有官方保序或已验证token保留才宣称Complete；生成位置无精确父贡献时Unavailable，不做最近邻猜测 |
| 5 单操作 | 按§4.1/4.2映射具体cv2算子、明示参数及固定generic值；A.2单位/section正交基不另算第二套。Distance只对本Run的显式Target做prepare/距离，不缓存跨请求句柄。Fit固定output_point_coord=true及存在mapping时output_xyz_mapping=true；不把robust输出点声称inlier |
| 6 读回 | 先读has属性/实际数量再按BCL受控容量分配数组；get-params读取XYZ/normal/索引/primitive等。返回Source单位，surface新revision和局部hash由A.1 factory产生；Extent只按官方类型长度换算，plane凸包不等观测域或孔完整性。所有payload按A.3唯一类型，实际缺贡献的精密用途 `S3D-011`，无primitive为Insufficient，native_rms见B.4 |
| 7 Freeze/清理 | freeze只产生脱离handle的深不可变托管数据；对本Run取得的每个模型/tuple及工作对象在finally释放。模型用cv2标准清理算子，tuple按既有公共资源接口释放；处理失败仍逐个清理，不因第一处throw跳过后续项。读回/清理异常分开诊断，不覆盖原native错误 |

§4.2的补洞关闭、输出all_points=false、greedy剩余timeout秒等原样冻结。有限RemainingTime从接纳起按TimeProvider.System单调消耗，包含组装/运行/读回/清理；业务超时触发stop后不启动下一算子。不支持中断的当前调用必须等真实返回，greedy原生timeout也不能当全流程中断保证。RunAsync不能用WaitAsync/WhenAny提前返Outcome；调用者观察超时只停止观察。清理成功后原Run才返Cancelled/TimedOut且无payload。资源失败返Failed且NativeResourcesReleased=false；未知则NativeDrained也不得猜true，Adapter封接纳、保留账本与原任务，Core按A.4保留预约。

Drain仅观察原Run，Close封接纳并请求本Run停止，两个方法的waitBudget须有限正，waitCancellation只停观察；到期返回Pending及原ID，已无法确认清理返回Unknown。无在途且全部归还返Drained/ResourcesReleased；Dispose无token且等真实Run/清理结束，已确认不可恢复Unknown则抛带原ID的InvalidOperationException。Close/Dispose幂等关联同一内部收尾任务；不再次clear已释放或状态不明的handle、不通过重建实例隐去Unknown。Host只在Core预约、Adapter账本和原Task均确认后丢强引用。

### B.4 NativeRms冻结：原生诊断与精确运行门

HALCON 26.05 `get_object_model_3d_params` 将primitive_rms定义为 **quadratic residual error**，length=1；has_primitive_rms仅声明存在。`fit_primitives_object_model_3d` 的least_squares最小化平方距离，Huber带权、Tukey抑制离群，plane三算法结果相同；all只返回native认定最小quadratic residual的一种。两页未给primitive_rms开方、除数n或权重和、m/m²单位公式，不能凭名称RMS推成标准根均方。

首发接口已闭合：先has_primitive_data；无primitive按A.3返回Insufficient，不构造PrimitivePayload。存在primitive时再has_primitive_rms；不存在→NativeRms=null并加 `NativeResidualAbsent`。存在且返回唯一有限非负数→NativeRms存该double原值，**NativeRmsUnit=`NativeUnknown`**，所有PrimitivePayload的Limitations都含 `HalconPrimitiveQuadraticResidual/NativeInputMeter/PhysicalStatisticNotQualified`。非法长度/负值/NaN/∞→Failed/S3D-007，无payload并清理；不能缺失填0、换Source单位、开方/平方/乘点数修正。primitive形状参数仍按A.3可知unit schema换源单位，与此未知统计单位分开。

UI原生值标签三语为 `原生残差（单位未确认）/原生殘差（單位未確認）/Native Residual (Unit Unconfirmed)`；缺失显示无值及原因。不得将其用于生产阈值、跨算法/样本评分、跨单位精确残差统计、计量合格或参考资格。all的内部选择由native完成；模块不自行用NativeRms重排候选或补竞争集。

专业源码仅提供比较界限：固定Open3D commit `b6c5e196384ad71e75b6e6f9c5da22d046221f1d` 的PointCloudSegmentation.cpp在EvaluateRANSACBasedOnDistance中用distance<threshold计inlier，累加distance²并 `sqrt(error/inlier_num)`，无inlier时返回0；其plane fitting与SegmentPlane测试并非HALCON统计定义。因此只借鉴“明确分母/入选域/空域”验收方法，不复制算法、不将Open3D数值同名替换此字段。

HA05真实运行辨别协议固定如下，未执行时每项结果为NotEvaluated：

1. 非零plane诊断fixture为8点 `(x,y,z)` 的笛卡尔积：x/y各取[-0.001,+0.001]米，z取[-0.0001,+0.0001]米，按x→y→z升序、SourceIndex=0..7、Validity全true，无mapping/面/法向。Plane/LeastSquares明确请求；数学真值plane z=0（法向正负等价），8个绝对几何残差各0.0001米。**候选**根均方=0.0001、均方=1e-8、平方和=8e-8，仅用来辨别，不声明哪个等HALCON原值。先核返回法向/偏移与该真值，再记录primitive_rms及n=8；零残差控制组用同四角z=0（n=4），只验零/存在性，不能独立辨别公式。fixture为软件合成诊断，不冒客户Golden/计量支撑。
2. 在同米单位下将同几何全部坐标与长度参数乘s=2，再逐点复制k=3（新SourceIndex），方法/排序/权重保持；记录原值比率与参数变化。长度型候选随s、平方型随s²；均值型重复点不变、和型可能随k；同时核相同物理输入的Meter/Millimeter/Micrometer规范化后结果一致。比率误差容限由数值Golden给出，不预填通过值。
3. 对sphere/cylinder重复缩放/重复试验，增加边界/离群组，分别用三种FitAlgorithm并记录收敛/选型/支撑；robust权重分母无法仅凭比例唯一判断时明确未确认。all返回实际类型另记，不混不同primitive残差。
4. 记录版本、输入hash、参数、原值、候选公式和排除证据；数值运行可排除候选，不能独立证明所有分布/稳健算法的公式。未来若消费者需要物理统计字段，须有26.05可核定义及适用域运行证据后修订唯一合同并接收；本轮不预造PhysicalRms字段或阻断普通原生诊断输出。

### B.5 两个无UI消费Host与原Owner保留

TestHost唯一参数入口为 `RunReferenceHostAsync(SurfaceSnapshot source, SupportDeclaration support, ResourceBudget budget, TimeSpan deadline, string profileRevision, HalconSurfaceBackendOptions adapterOptions, IMemoryAdmission memory, HostObservationBudgets observation, CancellationToken ct)` 与 `RunConnectorHostAsync(SurfaceSnapshot polygons, MappingTriangulationOptions? mapping, SectionParameters? section, ResourceBudget budget, TimeSpan deadline, string profileRevision, HalconSurfaceBackendOptions adapterOptions, IMemoryAdmission memory, HostObservationBudgets observation, CancellationToken ct)`，均返回§10.1的HostCallReport。它们是Exe局部方法，不是新模块公共服务；两入口都在参数装配中借用同一预建的进程级有限registry（Exe实例成员，不是局部变量/静态ServiceLocator）。fixture/真实输入由命令参数选择并验hash，不能在Host悄悄估参数。section=null明确第二步Topology，非null按传入plane参数执行Section；polygon与mapping路径多余options拒绝。

执行顺序固定：

1. 在Adapter factory前预留外围Owner槽（容量由Host显式给定），保存输入、options、memory及任务身份。槽满拒接非零，factory/执行次数0。槽内字段立即保存Adapter再创建Core，后者继续使用§10.1的有限service槽；没有Core槽时清理已构造但未运行的Adapter。两个registry的槽和原Task由进程根同时强持，不能只返回嵌套report后丢一个Owner。
2. `HalconSurfaceBackendFactory.Create(adapterOptions)` → `SurfaceFeatures3DServiceFactory.Create(adapter,memory,TimeProvider.System,new SurfaceFeatures3DServiceOptions(128))`。Reference Host提交§10的单次Plane/LeastSquares请求；support证据与Source身份一致，返回DatumCandidate及B.4限制，不作reference-surface资格。取消/超时使用同原请求，不能隐式重试。
3. Connector Host根据输入预选**唯一显式步骤**：有polygon用PolygonTriangulation；只有完整mapping且无polygon时用XyzMapping并要求mapping options；两种都没有拒绝，不自动greedy。第一请求DisplayDerived只作三角化；确认完整来源、有效支撑及新的不可变Geometry后，第二新RequestId以MeasurementSupport显式Topology（Core托管）或传入的Section。步骤由Host显式组织，Adapter一Run不带链；前步失败/缺精密来源则不发后步。两步共用尚未Close的独占Core，逐步保存原Execute任务，**不在第一步调用会立即Close的§10.1整段helper**；全部步骤结束才执行下述finally。目标孔边/截面只是几何支撑，不作连接器缺陷判定。
4. 每一步保存原Execute.AsTask一次并有限观察；观察到期停止新步骤，进入finally。Core原Close、Dispose沿§10.1各启动/保存一次，累计剩余观察预算，不覆盖业务错误。**须Core真实排空及预约归还后**再封/清理独占Adapter；即使Core Close观察失败也保存其原Dispose，未知保留双方，不因进入finally摧毁Adapter。
5. 外围槽新增保存Adapter原CloseTask/DisposeTask各一次；Adapter Close调用有限budget且None观察取消，Dispose等待真实收尾。finally完成后判码；0仅所有必要业务步骤Completed、允许的Support符合调用用途、原Core/Adapter任务与预约全部确认归还。Insufficient、必需跳过、任何观察超时/Unknown/清理throw均非零；原Owner保留直到迟到真实回执闭合。

两个Host同进程用独立Adapter/Core，memory可共享准入但不共享native模型。外围槽保存两步RequestId、CalculationIdentity、全部原业务/Close/Dispose Task、异常与借用端口；转交须目标明确接受这些身份与资源责任，拒接/回执缺失原Owner持续保留，不能只发“已移交”文本。有限观察后窗口/函数可结束，进程根不能结束；外进程watchdog遏制产生Unknown删失，不能报告资源释放。无需任何WPF窗口、静态HALCON初始化窗口或UI线程即可装配这两个Host。

### B.6 运行断言、命令与预算

以下是未来测试验收，不是本轮执行结果。HA普通有限fixture累计每case60s（含业务和finally）、suite600s、外进程720s；耗尽后记录未归还并非零，不用重置wait延长。真实Benchmark采用§13.2显式Profile watchdog/预算，不沿fixture假设生产时限。

| ID | 验收断言 |
|---|---|
| HA01 | 两无UI Host仅公开签名装配；factory前满槽拒接，发布DLL无WPF引用；Reference只返plane候选，Connector只有显式两步 |
| HA02 | XYZ三单位同物理输入、合法零点/无效mask、triangles/polygons/lines/mapping压紧读回正确；源hash不变，Target独立单位/同frame |
| HA03 | options/request限额越界、checked溢出、hard limit请求native调用0；greedy邻居/两模型费用纳估计；读回超限无payload且释放；实测峰值与预估分别记 |
| HA04 | 原token及original_point_indices精确回溯；误/缺token不造Complete；生成路线贡献缺失时精密用途拒绝，DisplayDerived带限制；孔洞关闭值可读诊断 |
| HA05 | B.4原值/缺失/非法读取分支与四步统计辨别；无资料不把NativeUnknown变成m，原生0不等无primitive；robust支撑不冒inlier |
| HA06 | stop前/中/剩余timeout、Close/Drain观察到期；不可中断原Task保持，真实返回/清理后才终态；第二Core共享AdapterBusy，不出现隐藏队列 |
| HA07 | 注入native/readback/单对象清理失败（仅测试内部故障点），后续清理仍执行，Core预约/双方账本Unknown保留；Close/Dispose只保存一次、不二次清handle、晚归还/拒接移交不丢Owner |
| HA08 | 真实SF11/15/17 Golden及两消费者取消/重启/回退，all只一种、无primitive Insufficient、距离AtLimit不入精确统计；所需真值/容差缺失该case非零未验，不用受控payload冒通过 |

命令固定：`dotnet build src/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Halcon/Asun.Modules.SurfaceFeatures3D.Halcon.csproj -c Release`；`dotnet run --project tests/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Halcon.Tests/Asun.Modules.SurfaceFeatures3D.Halcon.Tests.csproj -c Release -- --cases`；两消费者为同命令尾参数 `--consumer reference` 或 `--consumer connector` 并给已冻结输入/Profile，Benchmark为 `--benchmark <path>`。缺必要输入/目标方法Golden拒绝或NotEvaluated非通过；stdout只输出case/身份/状态/诊断，不创建第二活动报告。工程未建，本轮未运行命令。

## 附录 C：SF-W1 可选WPF装配、借用viewport与退出

**接收状态（2026-10-11）：** 主控限定接收本轮新增的公开ViewOptions、借用viewport bridge/provider、精确场景映射、原Task、双STA退出、三语及布局指导内容。SF-W1仍 `PreparationIncomplete / NotReady`，不标纯CoreReady；来源贡献/原Owner场景发布、IM-007/授权实际接线、公共程序集消费编译、真实WPF/UIA/资源/Golden/性能及客户现场资格未通过。SF-C1/C2六项接收保持。

### C.1 唯一工程与公开控件配置

| 项目 | 唯一落点/设置 |
|---|---|
| WPF DLL | `src/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Wpf/Asun.Modules.SurfaceFeatures3D.Wpf.csproj`；namespace `Asun.Modules.SurfaceFeatures3D.Wpf` |
| STA Exe TestHost | `tests/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Wpf.Tests/Asun.Modules.SurfaceFeatures3D.Wpf.Tests.csproj`；同Exe包含Reference/Connector两个独立STA Host |
| SDK/目标 | `Microsoft.NET.Sdk`、net10.0-windows、UseWPF=true、PlatformTarget=x64；Host OutputType=Exe；Core目标不变 |
| 引用 | WPF DLL直接引用Core、本机DevExpress 25.2.3 Docking/PropertyGrid/Grid/Core，及viewport公开 `Asun.UI.Viewports` 与 `src/Asun.UI.Viewports.Wpf/Asun.UI.Viewports.Wpf.csproj` 的程序集；只按viewport唯一指导实现的公开合同引用，不在本模块定义同名类型。Host真实后端需要时引用B.1 Adapter |
| 发布 | `artifacts/modules/surface-features-3d/<ModuleVersion>/win-x64/wpf/` 包含本模块Core/Wpf及公共说明；Host在同版本 `hosts/wpf-tests/`。viewport/DevExpress由宿主既有模块依赖提供，不私拷另一套实现/改版 |

新增工程写权限仍须正式派发，只限这两个目录；不改viewport/Core/共享工程/产品页面。控件factory/A.6签名保持，ViewOptions完整record固定如下（WPF局部配置，不进入Core）：

```csharp
public sealed record SurfaceFeatures3DViewOptions(
    string InstanceId, ISurfaceFeatures3DPermission Permission,
    ISurfaceFeatures3DViewport Viewport, TimeSpan UiWaitBudget,
    System.Windows.FrameworkElement ViewportContent);
```

ViewportContent是宿主创建的实际ViewportControl，在同Dispatcher且无其它视觉父节点；factory借用它装入中心区，不取得session/root所有权。InstanceId非空、所有依赖非null、budget有限正；factory在Dispatcher前校验，错误抛ArgumentException/ArgumentNullException且无任务。禁止给同一ViewportControl放入两个控件或跨Dispatcher；双实例各自Content/bridge。A.6的Show/Highlight/Clear仍是非阻塞投影facade，**void不代表呈现/归还**；确切任务观察由C.2的bridge提供。文本/参数/权限仍由A.6公共端口，不取产品DataContext。

### C.2 借用bridge的精确公开合同与场景交接

唯一viewport合同来源为 [viewport指导](../viewport/DEVELOPMENT-GUIDE.md) `0.3.4-prep §10.6～10.9/WPF Assembly Contract v0.2`。借用链使用 `ViewportControl.BindAsync(session,root,options,ct)`，其内部自行ReserveExecution/Start/登记真实Dispatcher与renderer任务；本模块不再重复reserve同一Bind。固定OwnSession=false；Lifetime必填非null并属于同Control/root，Resources.Revision精确viewport-ui-text/1且覆盖全部RequiredKeys，ExecutionBudget按实际Profile显式给定。bridge.Close/Dispose不调用借用session.Dispose/root.Close；Root/Close原合同不重审。

模块bridge承担绑定、身份核验、Attach/Update CAS、代次、资源刷新、有限观察和Unbind；宿主只提供已经由surface-data/viewport公开发布链得到的SourceBinding/overlay场景与授权/坐标事实，不由本模块重写LOD、拾取、法向或surface-data adapter。局部DTO/端口固定如下（namespace同C.1；viewport类型用其真实namespace，LengthUnit等同名冲突须显式限定）：

```csharp
public enum FeatureViewportLayer { Original, Derived, Normals, Topology, Section }
public sealed record FeatureSceneRequest(string InstanceId, long Generation,
    SurfaceSnapshot Source, SurfaceFeatureResult? Result, FeatureViewportLayer Layer);
public sealed record FeatureSceneSourceMap(
    SurfaceIdentity LocalIdentity, Asun.UI.Viewports.SourceId PublishedSource,
    string PublishedSurfaceRevision, Asun.UI.Viewports.CoordinateRevision Coordinates,
    string LocalFrame, LengthUnit LocalUnit, Asun.UI.Viewports.LengthUnit PublishedZUnit,
    EvidenceRef MappingEvidence);
public sealed record FeatureSceneBinding(
    SurfaceIdentity InputIdentity, string? CalculationIdentity,
    FeatureViewportLayer Layer, SurfaceIdentity DisplayedIdentity,
    ImmutableArray<FeatureSceneSourceMap> SourceMaps,
    Asun.UI.Viewports.ViewportContext Context,
    ImmutableArray<Asun.UI.Viewports.OverlayLayer> BaseLayers,
    ImmutableDictionary<int, ImmutableArray<Asun.UI.Viewports.OverlayLayer>> Highlights);
public sealed record FeatureSceneReply(FeatureSceneBinding? Binding, string? ErrorKey);
public interface IFeatureViewportSceneProvider
{
    Task<FeatureSceneReply> PrepareAsync(FeatureSceneRequest request, CancellationToken ct);
}
public sealed record FeatureViewportBridgeOptions(string InstanceId,
    int MaxTrackedOperations, int MaxHighlightKeys, int MaxSceneLayers,
    TimeSpan ObservationBudget);
public sealed record FeatureViewportObservation(string OperationId, long Generation,
    string Phase, bool Accepted, bool VisibleConfirmed, bool Drained,
    bool ResourcesReleased, string? ErrorKey);
public sealed record FeatureViewportCloseReport(bool Detached, DrainState State,
    ImmutableArray<string> OutstandingOperationIds, ImmutableArray<string> Errors);
public static class BorrowedFeatureViewportFactory
{
    // public static BorrowedFeatureViewport Create(
    //     Asun.UI.Viewports.IViewportSession session,
    //     Asun.UI.Viewports.IViewportProcessRoot root,
    //     Asun.UI.Viewports.Wpf.ViewportControl control,
    //     Asun.UI.Viewports.Wpf.ViewportUiBindingOptions bindingOptions,
    //     IFeatureViewportSceneProvider scenes, FeatureViewportBridgeOptions options);
}
public sealed class BorrowedFeatureViewport : ISurfaceFeatures3DViewport, IAsyncDisposable
{
    // factory唯一；Show/Highlight/Clear与A.6一致，无同步IO。
    // public Task<FeatureViewportObservation> BindAsync(CancellationToken ct = default);
    // public Task<FeatureViewportObservation> SetResourcesAsync(
    //     Asun.UI.Viewports.Wpf.ViewportUiResources resources, CancellationToken ct = default);
    // public ImmutableArray<FeatureViewportObservation> GetObservations();
    // public Task<FeatureViewportCloseReport> CloseAsync(TimeSpan waitBudget,
    //     CancellationToken waitCancellation = default);
    // public ValueTask DisposeAsync();
}
```

factory不取得呈现/native资源，检查control同Dispatcher、InstanceId/BindingId非空、OwnSession=false、Lifetime非null、资源schema/键完整、ExecutionBudget三个正值与root/session额度相容、清理/观察budget有限正、MaxTrackedOperations≥2（一个工作槽+专用收尾槽）、MaxHighlightKeys/MaxSceneLayers为正。缺Lifetime在Reserve/Dispatcher前拒绝，不选全局renderer。SceneReply深拷贝前核Highlights键数与总层数cap；native/显示字节另受viewport原预算/预约控制。Create前宿主预留C.4根槽，保存借用root/session/control/provider/Lifetime/backend/resources，Create后强持bridge。GetObservations返回深冻结摘要，OperationId=`InstanceId:ui:counter`；摘要不是原Task Owner。有限账本保存原Prepare/Bind/Attach/Update/SetResources/Dispatcher/Unbind及同binding.GetPresentations()的原Commit/Acquire/Confirm/Revoke/Return任务、场景与binding，lease由原binding/root持有，bridge不二次Return。同步throw存失败Task；异步启动前入槽，容量满/工作在途拒绝FeatureViewportBusy，无隐藏队列。收尾槽保留；原任务退出/借用归还证实才回收，不淘汰未决呈现记录。

SceneProvider必须无native/lease输出；只借用宿主已发布、寿命足以覆盖viewport Acquire/Return的源目录，Prepare取消也必须保存原Task观察。正常Reply恰有Binding、ErrorKey=null；失败Binding=null、明确本地错误键（例如FeatureSceneUnavailable）。为每个 `InputIdentity + CalculationIdentity + Layer` 精确提供映射，不能只用SurfaceId或revision猜。Original的CalculationIdentity=null、DisplayedIdentity=Source.Identity；Derived只接受Completed的SurfacePayload.Geometry；Normals/Topology/Section与结果类型相符，其DisplayedIdentity由确切发布模型映射证据声明。没有适用payload/场景拒绝，不拿原始图假装派生图。SourceMaps逐条声明局部身份/frame/unit→PublishedSource/PublishedSurfaceRevision/Coordinates/PublishedZUnit及MappingEvidence（A.1版本/hash要求）；bridge逐字段比较实际SourceBinding.Surface.SourceId/SurfaceRevision/CoordinateRevision/ZUnit，输入LocalFrame/Unit必须等Source或确切派生Geometry。一个展示身份恰有一个映射，每个Context surface均有对应声明；不同frame/单位转换只由MappingEvidence绑定的宿主公开坐标链负责，不凭枚举同名或ZUnit自推全XYZ比例。Context必须有与DisplayedIdentity相应的SurfaceSourceDescriptor，不能交空Context/2D占位；overlay来源版本也核该映射。证据资格未取得只能导航并标未评，不显示物理标尺或量测资格。

Highlights以原Input.SourceIndex为键，值是已投影到该场景坐标的明确OverlayLayer列表；缺source index或贡献不完整时不高亮并 `FeatureHighlightMappingUnavailable`，不按输出下标猜。BaseLayers和Highlights的LayerId必须互不冲突，SourceRevision匹配该场景；Highlight对输入索引去重升序，在基准Layers后确定性叠加对应层。Map/overlay由宿主使用viewport既有投影端口准备，bridge只组合/验证，不能以最近点造父贡献。Context及集合在接收时深冻结，不保留可写字典/数组；MappingEvidence是宿主声明与资格引用，不能由bridge自授物理正确性。Host真实发布/坐标授权映射是§16.2交接门，但provider接口、返回数据、拒绝与消费顺序已定义。

### C.3 可见回执、代次、三语与关闭顺序

1. 宿主在同Dispatcher保存原bridge.BindAsync；bridge立刻保存原control.BindAsync，固定OwnSession=false，成功只取返回IViewportUiBinding，不以control.Loaded证明绑定。Bind失败/观察到期保持未可用，原Bind仍在账本且不发Attach；若迟到绑定成功且已Close，立即进入原Unbind收尾。绑定类型/同root-session校验由viewport自身执行，不能用字符串伪造root归属。
2. Show核InstanceId/generation/layer，将A.6字符串映射到C.2枚举（其它拒绝）。Generation只接受本实例最新；进入Prepare前冻结Source/Result身份，Await原Task后重查代次/Detached/权限。授权过期/缺Read拒绝并交宿主刷新，不自行续期。来源更新使旧scene/results Stale；未获新SceneBinding不沿用旧Scene证明新数据可见。
3. 从session.GetSnapshot取真实ContextRevision/State：Created且本bridge未发Attach才用AttachAsync(scene.Context)，附着ContextRevision非负；Attach只允许一次，失败/取消的session仅可交Owner关闭，不能重试Attach。Ready/Empty或viewport明示允许更新的已附着状态才用UpdateAsync(new ViewportUpdate(snapshot.ContextRevision,replacement))；Attaching/Updating/Disposing/Draining/Drained/Disposed拒绝本次并观察原操作/交Owner恢复。replacement携完整Sources/Authorization/Language/Version/ViewState，ContextRevision=checked(旧revision+1)；场景模板revision不是CAS的权威。bridge限定借用session的UI场景发布为该Host指派的单写范围，其他writer更新导致Conflict，拒绝本次并取新snapshot展示恢复，不循环覆盖别人的场景。所有原Attach/Update Task即时登记；wait到期不重发，迟到原回执先解决。
4. Attach/Update的Succeeded/Presented还须与同binding.GetPresentations()中本次ContextRevision、SourceCall.Generation、Submission/PresentationId及backend代次关联；观察原Commit的PortResult.Value.VisibleConfirmed=true，才标FeatureViewportObservation.VisibleConfirmed。没有同binding真实呈现记录/原Commit未退出/可见证据不足，返回FeatureViewportNotVisible/Pending，不仅凭SourceStatus/属性赋值称可见。原Acquire接收完整ViewportPresenterSubmission(Request,Presentation,SourceCall)；binding保其原授权/身份，不能由Host自造PresentationRequest/CallContext补记录。trace中的PresenterIdentity只供观察，原lease仍由binding/root及同Owner Lifetime持有。旧代迟到回执存诊断不更新新控件；Partial/未知清理不冒成功。
5. Highlight只在当前scene已确认后用C.2组合overlay重新全量Update、保留当前Sources/授权/视图；Clear仅撤本模块highlight并恢复当前scene的BaseLayers，仍需原Update回执。丢弃派生结果时明确Show Original取得原始scene，不以Clear恢复未知原图。不关闭session、不删除其它Host图层；session并非本Host单写时拒绝，而非清空未知Context。Detached时先封Show/Highlight门，不启动新的普通scene更新；由Unbind撤本UI借用。
6. 控件三语切换由宿主调用A.6 SetCulture；先校验完整IUiTextCatalog及对应viewport资源，再启动bridge.SetResourcesAsync并保存原binding.SetResourcesAsync(resources,budget,ct)，成功后用真实BaseContextRevision全量Update Context.Language。两原回执均成功后才切本地控件完整资源并称已切换。部分成功时保留旧本地语言、标资源刷新未完成，**不能声称viewport仍是旧语言**；在原任务退出后保存一次恢复旧resources/旧Language的操作及其原回执，恢复失败/Pending由根保留混合状态，禁新语言刷新直到明确恢复/接管。没有scene时仅绑定资源回执成功即可，下一scene须同语言。不能覆盖另控件text/culture，缺key不回显键。所有字段/错误/限额/恢复/SuperTip用同语言资源；B.4原生残差限制同时覆盖三语。
7. close顺序为控件Detached/封新预览→取消控件自有请求并保存原Detach→bridge封Show/Highlight/资源刷新、请求Prepare/投影停止→保存一次binding.UnbindAsync(waitBudget,None)→并列观察原投影/Dispatcher与Unbind。**不能先等仍依赖Unbind触发Revoke/Return的Commit完成再发Unbind。** Unbind在slot worker外发起，原binding关门、撤引用并以同Owner Revoke→Return；Acquire晚到所得lease仍登记原slot，后续Revoke/Return或QueryReturn观察同ReturnId，不被新binding接走。Detach/Bind/Commit观察到期不省清理，Bind晚成功后即触发原Unbind。Detached/OwnerAccepted不等Drained；所有原任务退出、trace无未归还lease及真实Cleanup闭合才返回Drained/ResourcesReleased。
8. bridge.Close有界观察，超时Pending/取消只停观察；GetObservations含原OperationIds。Dispose无token，等原任务与原Unbind真实归还；不可恢复Unknown抛InvalidOperationException并保留根槽，不能卸掉正在执行的Dispatcher。借用service/session/root/provider/text都不由bridge或控件Dispose；最终宿主依次清独占Core/Adapter与自己持有的viewport session/root，沿各自公开Close/Dispose原Task，不把一边Drained冒另一边释放。

bridge局部错误键固定 `FeatureViewportBusy/FeatureSceneUnavailable/FeatureSceneIdentityMismatch/FeatureHighlightMappingUnavailable/FeatureViewportConflict/FeatureViewportPermissionDenied/FeatureViewportNotVisible/FeatureViewportPending/FeatureViewportCleanupUnknown/FeatureViewportResourcesRejected`，归C.1三语资源，不注册成新的Core S3D错误。正常拒绝/同步异常/观察到期均形成Observation，void facade不得丢异常或用fire-and-forget；账本有异常且根槽仍Owner。

### C.4 两个STA Host按公开签名装配与根Owner

两个消费Host在同一WPF Exe、各自STA Thread+Dispatcher运行，均使用1920×1080固定验证视口；不同线程不共享视觉对象。进程级有限根registry由启动主线程持有，**在线程启动/bridge factory前**预留含HostId/InstanceId的槽，容量显式给定；保存原Thread/Dispatcher/DispatcherOperation.Task与其inner Task、service/Adapter、session/root/provider/control/bridge、全部Detach/Close/Dispose/Unbind原Task/RequestId/OperationId。空Host装配不靠产品VM、私表或隐藏窗口，固定顺序如下：

| 顺序 | Reference STA Host | Connector STA Host |
|---|---|---|
| 1 外围服务 | 用B.5 Reference的独立Adapter/Core与memory/Profile；纯控件协议测试可显式受控backend，但标ControlledPort而非真实native | 用B.5 Connector的独立Adapter/Core；复用同公开DTO/配置，输入polygon/mapping支撑，不共享Reference native对象 |
| 2 同Control呈现与session | STA创建无参ViewportControl与宿主原root；ViewportRendererFactory.Create(viewportControl,root,new ViewportRendererOptions(HalconRequired,profileNativeBytes,profileRasterBytes,profilePendingCount,uiCleanupBudget))，核PortOutcome.Succeeded/Value非null。Create session前ViewportOptions.Presentation=viewportControl.Presentation、Backend=ports.Backend，申请Presentation功能，Source/Surface/坐标/授权/资源沿真实源Owner公开端口；所有输入Profile显式，不编物理阈值 | 同签名但自己的control/root/renderer及源，绝不交叉配Lifetime/Backend。两个source payload用viewport §15.2.5.1公开发布布局，其余payload不反射猜类型；显式不可显示时拒绝 |
| 3 完整资源与Bind | resources=ViewportUiResourceCatalog.Get(language).Value（先核Succeeded/非null，Revision=viewport-ui-text/1）；new ViewportUiBindingOptions("reference-view",false,resources,uiCleanupBudget,Lifetime:ports.Lifetime,ExecutionBudget:new ViewportUiExecutionBudget(profileUiBytes,profileWorkTasks,profileControlTasks))；BorrowedFeatureViewportFactory.Create(session,root,viewportControl,bindingOptions,scenes,new FeatureViewportBridgeOptions("reference-ui",4,maxHighlightKeys,maxSceneLayers,uiWaitBudget)) | 同签名，BindingId=connector-view、InstanceId=connector-ui；独立资源、renderer Lifetime和有限账本。不得沿旧四参Options省Lifetime，8MiB软件默认不冒实际3D容量 |
| 4 绑定与嵌入 | 根槽先存bridge和原BindAsync；确认bind成功后 `SurfaceFeatures3DControlFactory.Create(service,text,new SurfaceFeatures3DViewOptions("reference-ui",permission,bridge,uiWaitBudget,viewportControl))`，存control/原Dispatcher任务，再Attach真实snapshot/Profile/budget/deadline | 同构造替换connector-ui/相应输入；Attach选择Topology/显式三角化结果支撑，不能复制另一Host参数草稿 |
| 5 运行/资源 | 预览plane候选，观察结果与bridge scene回执；高亮支撑索引只用映射；三语切换记录原resource task | 显式三角化/Topology或Section结果只由其任务链消费，反例缺mapping禁止误高亮；两Host同时编辑/取消/切语互不影响 |
| 6 退出 | Window.Closing先取消直接关闭，启动并强持原Detach/bridge.Close，不在STA `.Wait/.Result`；有限观察报告Pending/Unknown交根槽后才可隐藏窗口 | 同顺序；独立任务未闭合不能Dispose别人的服务/窗口/根，不能关Dispatcher来“完成”原任务 |

STA入口创建Thread后先SetApartmentState(STA)再Start；使用一个Dispatcher.Run维持UI生命周期，finally若仍有Pending/Unknown将线程/Dispatcher和全部原任务交原根保留，不调用InvokeShutdown来截断。通过BeginInvoke/InvokeAsync跨线程创建/退出时，根同时保存实际DispatcherOperation.Task及其返回的inner async Task，两者皆须退出；保存仅wrapper等待Task不够。宿主UI预算到期只让观察返回，窗可先隐藏但Dispatcher/viewport借用仍由根保留。外部接管拒绝/无确认不停止线程或拆根；确认接管只变Owner，不等资源已归还。

控件本地Detach的DrainReport不代表viewport/Adapter释放；最终测试退出码在两Host各自finally清理观察结束后计算，0须必要业务与UI断言满足、原Core/Adapter/bridge/viewport资源归还、全部Dispatcher Task退出且线程已安全退出。相应viewport根自己CloseAsync/session Dispose原Task须由宿主按其合同确认，不能发明本模块替代回执。Unknown/未完成/必需跳过/异常为非零并保留Owner；外层进程遏制只记删失，不能把进程结束当软件恢复通过。

### C.5 布局、三语与运行验收

设计使用§9 DevExpress DockLayoutManager/LayoutGroup/LayoutPanel、PropertyGridControl.SelectedObject、TreeListControl与SuperTip；BaseLayoutItem.AllowClose/AllowDrag=false、LayoutGroup.Orientation控制三区。此次从本机Grid.v25.2.Core.xml核DataControlBase.ItemsSource，Docking.v25.2.xml核ContentItem.Content（LayoutPanel继承）、Grid.v25.2.xml核TreeListView.KeyFieldName/ParentFieldName：来源/结果树绑定有限不可变行(NodeId,ParentId,Caption,State)，KeyFieldName=NodeId/ParentFieldName=ParentId，不依赖产品VM；中心LayoutPanel.Content=借用ViewportContent。PropertyGrid绑定显式草稿对象，变更创建新的强类型参数副本；不编辑结果记录。状态/命令在图像外，主题/图标用宿主已安装DevExpress资源，语义色有文字，不放遮HWND的透明Canvas；渲染/拾取/airspace按viewport自身路线，不重复实现。

唯一屏幕验证基线为1920×1080，**不是假定有1920×1080客户区**：在更大物理屏幕固定此验证视口，扣除任务栏、窗口边框/标题/状态栏并记录实际client area/DPI；不改系统分辨率、不追加分辨率矩阵。§9三区宽度是理想布局约束，实际净区域按该基线测；影像优先、关键取消/错误/恢复不藏进tip。三语包括A.6词条、B.4原生残差限制、C.3全部局部错误、状态、单位/参数/权限与恢复。恢复文字明确“等待结束/保留资源/交宿主恢复”，Unknown禁止新预览；独立模块内不重复放语言切换按钮。

WU协议fixture累计每case90s、suite600s、外进程720s，业务/Dispatcher/cleanup共享累计剩余预算。三语布局/UIA人工与自动核对由同Host显式选择，不冒超时后截图为完成。测试预算只是止损，不是生产刷新/退出目标。

| ID | 断言 |
|---|---|
| WU01 | 两空STA Host按C.4公开签名构造，无产品VM/隐式窗口；OwnSession=false、两个control独立，core未引用WPF |
| WU02 | Bind原任务/Dispatcher与inner Task入根；满槽/Busy在异步启动前拒绝；重复不同session绑定拒绝，无重复ReserveExecution，无隐藏队列 |
| WU03 | scene精确身份/payload/frame/单位/授权/SourceBinding/overlay版本匹配；缺场景/映射拒绝，原数据未改；回执Presented缺失/Partial不能VisibleConfirmed |
| WU04 | 旧代结果/迟到Prepare、CAS冲突、其他writer、撤权/到期：新代不被覆盖，不自动retry或更新授权，未确认操作仍保留 |
| WU05 | Highlight按SourceIndex与映射，Clear只撤本Host图层，缺贡献不猜；Derived/Normals/Topology/Section分别实际呈现，不把Original冒派生 |
| WU06 | zh-CN/zh-TW/en-US完整文本/SuperTip/键盘/IME/UIA及实际净client area/DPI，无截断/关键命令丢失；资源刷新失败/Pending不称切换成功，另Host语言不变 |
| WU07 | 运行/Bind/Update/资源刷新中关闭、Detach观察失败、Unbind.Pending/Unknown/Dispatcher异常：两个独立cleanup都启动且原Tasks/root强持；late bind先解决再Unbind，不以WindowClosed/Detached作为Drained |
| WU08 | 双实例取消/编辑/退出隔离；清理错误不覆业务错误，最终原Core/Adapter/bridge/viewport/Dispatcher全部归还后才退出0；拒接接管持续原Owner、Dispose只启动一次 |
| WU09 | Lifetime=null/资源旧schema/缺RequiredKeys在Reserve前拒绝；同Control.Presentation从Bind前到原binding转发；同提交重复原Task相等、Acquire完整Submission、跨Control/root/授权拒绝；观察同binding trace关联可见而不再Acquire |
| WU10 | Acquire/Confirm晚到、Commit依赖收尾、撤权后Revoke、Return.Pending/晚归还：先启动Unbind避免自等待，原Task/lease/root保留，同ReturnId归还确认才退出；新Bind不能替原binding洗Unknown |

命令固定：`dotnet build src/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Wpf/Asun.Modules.SurfaceFeatures3D.Wpf.csproj -c Release`；`dotnet run --project tests/Modules/surface-features-3d/Asun.Modules.SurfaceFeatures3D.Wpf.Tests/Asun.Modules.SurfaceFeatures3D.Wpf.Tests.csproj -c Release -- --dual-sta`。实际依赖未实现/场景未交接时明确未验且非通过，不用空ViewportControl/受控backend代真实WPF资格。性能分别记录Core接纳→ResourcesReleased、scene提交→真实visible receipt、键盘交互、SetResources回执、取消→各端口排空/退出；完整样本统计沿§13/治理，生产目标仍TargetPending。本轮不创建工程或运行这些命令。

## 附录 D：几何描述、局部曲率与有界参数建议

### D.1 全范围定位、公开入口与非目标

本轮用户明确要求覆盖形状/异常/法线/曲率/高度及自动参数的可决定设计；本附录补局部几何描述与建议，不将未定义能力留给实现者。SF-D1（几何场/局部曲率）、SF-D2（有限参数建议）仍 `PreparationIncomplete`，不提升CoreReady。Core Contract0.3及SF-C1/C2完全保持，新增DTO/服务属于B.1同一Halcon DLL的 `Asun.Modules.SurfaceFeatures3D.Halcon.Analysis` namespace，唯一Exe也是B.1，命令追加 `--analysis-cases`；无新类库、模型、数据库或设备权限。可无UI调用，C的附加控件只投影同返回值。该程序集引用Core/BCL/既有AsunImage，不自研并行拟合或邻域搜索库。

几何形状由Plane/Sphere/Cylinder与索引拓扑/连通/截面表达；“异常”只指非有限、缺测、退化、非流形、来源不足及调用者明确几何参考的偏差场，不输出工艺缺陷类别或PASS/FAIL。自由曲面/任意CAD形状识别、训练补洞、曲率分割的内部统计不在本能力；任意散点/mesh没有合资格高度网格时不输出真实曲率，给CapabilityUnavailable，绝不退回法向夹角/PCA值。

```csharp
// Analysis namespace；以下为冻结目标签名，未实现。
public sealed record PhysicalHeightGrid(Point3 Origin, Vector3 ColumnDirection,
    Vector3 RowDirection, Vector3 HeightDirection, double ColumnPitch,
    double RowPitch, double CoordinateTolerance, double OrthogonalityTolerance,
    EvidenceRef CoordinateEvidence);
public sealed record AnalysisPrecision(string Id, string Revision,
    double MaxHeightRoundTripError, double MaximumSlope,
    double MaximumSecondDerivative,
    double NegativeDiscriminantTolerance, EvidenceRef Evidence);
public abstract record SurfaceAnalysisParameters;
public sealed record HeightFieldParameters(Point3 Origin, Vector3 PositiveDirection,
    EvidenceRef DirectionEvidence) : SurfaceAnalysisParameters;
public sealed record GridCurvatureParameters(PhysicalHeightGrid Grid,
    int WindowWidth, int WindowHeight, AnalysisPrecision Precision)
    : SurfaceAnalysisParameters;
public sealed record AdviceGate(double MaxAbsoluteReferenceDistance,
    double MinimumValidFraction, double MaximumNormalAngleRad,
    EvidenceRef ThresholdEvidence);
public sealed record AdviceCandidate(string Id, SurfaceFeatureParameters Parameters);
public sealed record AdviceParameters(ImmutableArray<AdviceCandidate> Candidates,
    SurfaceSnapshot? Reference, AdviceGate? Gate) : SurfaceAnalysisParameters;
public sealed record SurfaceAnalysisRequest(string RequestId, SurfaceSnapshot Source,
    SurfaceAnalysisParameters Parameters, ResourceBudget Budget, TimeSpan Timeout,
    SurfacePurpose Purpose, string ProfileRevision, string ContractRevision);
public sealed record GeometryFieldSample(int SourceIndex, double? Height,
    double? MinimumCurvature, double? MaximumCurvature,
    double? MeanCurvature, double? GaussianCurvature,
    ImmutableArray<int> SupportIndices, string? InvalidReason);
public sealed record AdviceCandidateResult(string Id, string CalculationIdentity,
    bool Eligible, double? MaximumReferenceDistance, double? NormalAngleRad,
    int ValidCount, int Denominator, ImmutableArray<string> Reasons);
public sealed record SurfaceAnalysisResult(string RequestId, string Identity,
    SurfaceIdentity Source, SurfaceExecutionStatus Status,
    ImmutableArray<GeometryFieldSample> Fields,
    ImmutableArray<AdviceCandidateResult> Candidates, string? SuggestedCandidateId,
    string HeightUnit, string CurvatureUnit, string GaussianUnit,
    SupportEvidence Support, ExecutionDiagnostics Diagnostics,
    ImmutableArray<ValidationIssue> Issues,
    bool Drained, bool ResourcesReleased);
public sealed record SurfaceAnalysisOptions(int MaxRequestIds, int MaxCandidates,
    int MaxWindowPixels, int MaxRetainedRows, int MaxIssues);
public static class SurfaceAnalysisFactory
{
    public const string ContractRevision = "surface-features-3d.analysis/0.1";
    // public static SurfaceAnalysisService Create(HalconSurfaceBackend backend,
    //     IMemoryAdmission memory, TimeProvider time, SurfaceAnalysisOptions options);
}
public sealed class SurfaceAnalysisService : IAsyncDisposable
{
    // public ValidationReport Validate(SurfaceAnalysisRequest request);
    // public ValueTask<SurfaceAnalysisResult> ExecuteAsync(SurfaceAnalysisRequest request,
    //     CancellationToken cancellation = default);
    // public ValueTask<DrainReport> DrainAsync(TimeSpan waitBudget,
    //     CancellationToken waitCancellation = default);
    // public ValueTask<DrainReport> CloseAsync(TimeSpan waitBudget,
    //     CancellationToken waitCancellation = default);
    // public ValueTask DisposeAsync();
}
```

factory唯一构造，无IO/资源；null/非正options抛配置异常。backend/memory/time借用不Dispose，服务拥有贯穿自身生命周期的一个私有Core编排实例（A.4 factory同borrowed backend/memory）与自己的请求槽、stop源/预约/native二次拟合账。私有Core的MaxRequestIds固定为checked(MaxRequestIds*MaxCandidates*3)，三项上界为候选操作及至多两个精确距离操作；乘积不可表示在factory即拒绝配置，不在运行时扩表。原Owner在factory前保有限根槽，保存Analysis原Execute/Close/Dispose及私有Core原Task；不能用局部await using隐藏Pending。单实例单在途、无队列、RequestId永久有界去重，满表拒S3D-008/重用015/Busy013/Closing016；校验纯同步，执行不占UI线程。Cancel/Timeout/Close只停下一步，当前native真返回、对象/tuple清理后返终态。复用B.3的资源失败封接纳/原Task保留，Dispose等待真实排空，Unknown抛且原根不丢。每次Execute结束只确认私有Core该请求排空，不Close/Dispose它；Analysis.Close封接纳并停在途，原Execute退出后才发私有Core.Close，Dispose再等待其原Dispose。借用backend由外部Host在两个服务排空后关闭；禁止互等或提前Dispose。私有Core归还状态未知则封Analysis接纳并保原根，不新建Core洗掉Unknown。

参数无客户默认：Timeout/Budget/Purpose按A.2；ProfileRevision/ContractRevision非空且版本精确。Analysis的Height/Curvature字段入口允许全无效源，返回全null/Insufficient且native调用0，以保留缺测槽；这只限定本新增Analysis字段入口，Core及Advice的无有效源仍拒S3D-006。Grid坐标/方向证据与Source单位/frame一致，Directions为显式单位正交右手基（Column×Row=Height），各dot/norm误差≤OrthogonalityTolerance（无量纲有限且0≤tol<1）；CoordinateTolerance独立为源长度有限≥0，pitch为源长度单位有限正数。WindowWidth/Height为≥3奇数，乘积≤MaxWindowPixels，至少覆盖3行3列且源mapping无重复row/col；CoordinateEvidence符合A.1。Precision的高度往返阈值为源长度有限≥0，MaximumSlope无量纲有限正、MaximumSecondDerivative为1/源长度有限正，判别式数值保护阈值有限≥0（1/源长度²，计算时换1/m²），Id/Revision及Evidence来自用途Profile，不从量测公差自动猜比例。

Identity按A.1编码原语，以UTF8前缀 `surface-features-3d.analysis/0.1`→Source.Identity→Source.Data.LengthUnit/CoordinateFrame→具体Parameters类名及以上声明字段（含Reference完整Identity而非再写全Source数据）→Purpose→ProfileRevision→ContractRevision→本程序集ModuleVersion→backend BackendId/CapabilityVersion固定顺序SHA-256；所有集合保序，Candidates按Id ordinal排序后冻结。Budget/剩余deadline只作执行诊断。拒绝且未规范化Identity为空字符串；不把参数类型反射或culture格式当编码。HeightUnit=`m/mm/um`，CurvatureUnit=`1/m,1/mm,1/um`，GaussianUnit对应`1/m^2,1/mm^2,1/um^2`；未产生对应字段时仍写其明确单位而非NativeUnknown。NativeRms不参与这些精确几何定义。

### D.2 高度/偏差场与缺测资格

HeightFieldParameters冻结唯一正方向n（稳健范数归一、结果诊断回显）与原点O：有效点的Height=dot(P−O,n)，保持输入单位、SourceIndex及单点SupportIndices=[SourceIndex]；无效点Height=null、其它字段null、InvalidReason保原原因，Unknown从E的sidecar不得升级Valid。它是有向坐标场，不是某产品“焊高/体积”。调用者参考Plane时把其点和Hessian单位法向显式转换为该参数，选择正方向由DirectionEvidence给出；模块不自动拟合或选“上”。几何偏差精确参考也可直接用§4.2显式Target的ExactPrimitive/ExactLinear输出，signed授权/AtLimit规则不变。

处理顺序为输入深冻结/预算→TryReserve→逐原输入下标checked遍历（取消/时限每块检查）→计算有限double字段→深冻结→归还预约→结果。有效计算非有限为S3D-004失败，整体无Fields；无有效点Insufficient，字段保null与有效分母。不裁除孔洞、不填0、不按显示LUT换单位。法线仍用§4.1/4.2的Normals，同一行可展示夹角/方向证据但不从Height反推未测法向。独立属性有效域保持A.1/E，不把位置有效等同属性或曲率有效。

### D.3 规则高度图局部曲率：HALCON拟合与物理转换

选择理由：HALCON26.05 `fit_surface_second_order` 已提供二次最小二乘，避免自行实现PCA/局部多项式拟合；官方surface_normals/get-params没有可读的有单位主曲率。当前路线仅适用于已校准、单值、完整矩形物理高度网格；无mapping、非等距/非正交网格、多层遮挡、任意散点、复杂mesh不自动栅格化。坐标Owner可另发布合资格网格，但新发布是新输入，不能洗原缺测。

对mapping的每个观测row/col，以O+col*ColumnPitch*ColumnDirection+row*RowPitch*RowDirection为基准，h=dot(P−O,HeightDirection)；P的两个横向投影须在原单位CoordinateTolerance内符合规则坐标，正交数值保护独立用OrthogonalityTolerance，不能混长/角单位。Grid的Origin对应mapping本地(0,0)，上游crop已在该Origin/坐标证据中处理，不再加一次父offset。按完整网格逐观测中心处理，输出顺序按Source输入下标，Mapping中缺槽就是缺测。

窗口必须完整在网格内且所有槽有效、均有连续支撑证据；边界/孔/无效/Unknown/未观测槽中心输出null曲率、原因 `CurvatureWindowIncomplete`，不缩窗、不跨洞、不镜像padding。只有完整窗口才使用h；窗口9点是软件可观察条件，不是物理光滑证明。ContinuousSupportRef不足时精密用途拒S3D-006，显示用途可返回NotEvaluated及限制；不把二维mask凸包当连续支撑。

具体每窗口顺序：

Analysis到B.2同实例backend的公开增量为 `ValueTask<GridPatchFitOutcome> FitGridPatchAsync(GridPatchInvocation invocation,CancellationToken stopRequested)`；与原RunAsync共用同一接纳门/native账本，不能两个端口并发占相同实例。Analysis namespace局部值 `GridPatchInvocation(string RequestId,string CalculationIdentity,int Width,int Height,ImmutableArray<float> HeightsMeter,ResourceBudget Budget,TimeSpan RemainingTime)` 和 `GridPatchFitOutcome(SurfaceExecutionStatus Status,ImmutableArray<double> Coefficients,ImmutableArray<ValidationIssue> Issues,bool NativeDrained,bool NativeResourcesReleased,ImmutableArray<StageTiming> StageTimings,string? NativeErrorCode,string? NativeErrorText)`；六个Coefficients依α/β/γ/δ/ε/ζ，失败Empty，按B.3原任务真实退出后返回。入口核全部shape/finite/单窗口cap/字节预算，拒绝不取native；现有Core不调用这个新增端口，不改变I3dSurfaceBackend或受控Core。

1. 把窗口高度换米，以中心h0作显式局部高度原点，q=h−h0→round-to-nearest-even float32；检查float有限与恢复原单位后的每槽误差≤Precision.MaxHeightRoundTripError。局部原点固定h0，是本算法声明的数值平移，写有效参数/身份，不从数据自适应选比例；超限拒S3D-004且无payload，不将double转换称无损。
2. 私有float[] pin→cv2的 `gen_image1('real',width,height,ptr)`（仅本窗口，HALCON复制后真实返回才unpin）→`gen_region_runs`完整rectangle行段（row=0..H−1，begin=0,end=W−1）→`fit_surface_second_order(region,image,'regression',0,2.0)`。算法固定regression，Iterations=0（该算法忽略）、ClippingFactor=2.0（API合法固定值，不是生产离群阈值）；不换Huber/Tukey、不偷偷平滑。**此算子忽略Image原domain，只看传入Regions**，所以不能靠ReduceDomain避免窗口缺测，步骤0完整性校验必需。
3. 官方法式为q=α(r−rc)²+β(c−cc)²+γ(r−rc)(c−cc)+δ(r−rc)+ε(c−cc)+ζ，rc/cc为region与整图交集中心，完整奇数窗口恰中心。六个tuple每个恰一个有限值；固定源坐标x沿Column、y沿Row，sx/sy为pitch换米：p=ε/sx、q'=δ/sy、a=2β/sx²、b=γ/(sx*sy)、c'=2α/sy²。核abs(p/q')≤MaximumSlope；a/b/c'换到1/源长度后abs≤MaximumSecondDerivative，溢出/坏值拒绝，不把β和α对错轴。
4. 相对于正HeightDirection法向，w=sqrt(1+p²+q'²)，H=((1+q'²)*a−2*p*q'*b+(1+p²)*c')/(2*w³)，K=(a*c'−b²)/w⁴；d=H²−K，d<−tol拒绝，−tol≤d<0仅作浮点保护clamp0并记 `CurvatureDiscriminantRounded`。kmin=H−sqrt(d)、kmax=H+sqrt(d)，单位1/m，K单位1/m²；回源单位分别乘源→米倍率与倍率²。更换正方向翻转H和k符号（k排序随之变），K不变；主曲率方向/置信度不在本输出，不猜特征向量。
5. SupportIndices为完整窗口所有原SourceIndex，排序去重；逐点来源是声明支撑而非拟合权重，不伪造平均权重。Height为中心原CPU高度，曲率来自局部拟合且标Derived，不能覆盖原XYZ/Normals/Origin。finally逐个Dispose本窗口image/region/tuple，原任务/lease退出再下一窗口；只同时持一个native窗口，仍无硬native memory声明。

缺测中心的null是字段未合格，结果Completed但Support.Quality=Insufficient并逐点记Issues；MaxIssues正且≤256，达限保前MaxIssues−1项与一项IssuesTruncated，Support始终计实际总无效数。Support.InputCount=总点数/ValidCount=原有效点数/OutputCount=成功字段数/ExcludedCount=原无效点数，UseQualificationEvaluated=false；任何曲率缺失不称Complete。输出行数≤MaxRetainedRows及Budget.MaxOutputPoints。原生拟合/清理失败或整体超时/取消均Fields=Empty/Candidates=Empty/SuggestedId=null；保留错误与资源轴，不将前半窗口发布给生产。预算计Source托管保留、全输出及n*WindowPixels贡献上界，超MaxContributions拒绝；托管新增估计=`256*n+8*n*WindowPixels+16*WindowPixels+4096+2048*MaxIssues`，native估计=`64*WindowPixels+65536`，若还调用B.2模型则另加其费用。GridPatch入口width*height同时≤backend.options.MaxInputPoints/MaxOutputPoints，Estimate不能冒硬native限；RequireHardMemoryLimit仍拒。窗口/候选固定计时Native/Readback/Freeze/Drain/Release，端到端不由阶段求和推算。

### D.4 参数建议：有限候选与拒答，不更改生产请求

AdviceParameters候选来自宿主批准的Profile（无模块生产默认），每Id非空唯一、总数≤MaxCandidates且≥1，参数只允许A.2的Fit单Plane、Normals或Smooth，**一候选一操作**；不接受All/自动链/任意Generic字典。Reference为显式同frame/单位可独立换米的合资格Plane primitive，Reference支持/方向证据必须完整。Gate的最大绝对参考距离为源长度有限>0，MinimumValidFraction∈(0,1]，MaximumNormalAngleRad∈(0,π]，阈值Evidence由用途Owner给出；缺Gate/Reference只返回未评价/无SuggestedCandidateId，不用NativeRms排名。

Reference/Gate可显式null表达缺外部评价输入，返回Completed+Support.Quality=Insufficient/UseQualificationEvaluated=false、SuggestedCandidateId=null、Issues含AdviceReferenceRequired/AdviceGateRequired且native调用0；不替用户补默认。非null却结构/版本错误仍Rejected。Candidates.Count同时≤MaxRetainedRows；返还的候选行按Id ordinal顺序，分母原Source有效点数，n=0拒S3D-006。正常建议Support.OutputCount=已评价候选数，其余字段按原Source点数，不把候选个数当点数剔除量。

执行次序固定：核Source/Reference与候选完整参数、有效域/连续支撑→按Id ordinal逐候选（有界且共享原Timeout，不每候选延长）→通过Analysis私有Core发显式新RequestId=`analysisId:candidateId`，预算含两模型和全部评价保留→观察原Execute直至真实释放→以明确几何距离评价。Fit Plane同时计算原始全部有效点到候选plane、到外部Reference的ExactPrimitive绝对距离，MaximumReferenceDistance取两组最大值（避免平移的自拟合残差0假通过），并核候选法向与Reference法向夹角。Normals用有效法向与Reference逐点夹角最大值、原点到Reference最大距离；Smooth用派生有效点到Reference的ExactPrimitive距离，核完整父贡献与原有效域。符号方向一致才用acos(clamp(dot,−1,1))，未获方向证据不通过abs(dot)忽略翻面。Distance请求固定MaxDistance=0/ExactPrimitive，不从截断样本算误差。

候选Eligible须结果资源已归还、完整来源/连续支撑、无预算/数值失败、ValidCount/原Source有效分母≥Gate比例、最大绝对距离≤Gate上限、法向角≤Gate；Smooth没有显式有效法向则该角评价未合格，不偷偷算法向（可由宿主另候选/显式预先Normals请求）。分母不可换成剔除后点数，空集不0分。所有满足候选中以最大参考距离升序→法向角升序→Id ordinal打破相等选择**一个建议Id**，不以一次速度测量/原生RMS/输出点数判“最佳”。没有通过候选则Abstain及逐候选原因；一个候选失败但清理已确认可以继续下个已声明候选，Unknown/取消/原Timeout耗尽停止全请求并保无建议终态。每个原Core/距离Task强持，其操作资源真实归还后才Analysis终态；私有Core的Close/Dispose仅在Analysis服务关闭时执行，按D.1。

上文新RequestId的`analysisId:candidateId`是角色说明，实际编码固定为`s3da-`+SHA256(A.1编码的UTF8前缀`surface-features-3d.advice-call/1`→外层RequestId→Candidate.Id→步骤字符串)。步骤只取`candidate`、`candidate-distance`、`reference-distance`；Fit至多三调用，Normals/Smooth至多两调用，不发隐式补法向操作。不得用几何Identity代替外层RequestId，否则同几何的第二次合法请求会误触永久去重。外层ID去重登记新增保留上界为`256+4*UTF8ByteCount(RequestId)+3*MaxCandidates*512`，checked纳入该请求Budget.MaxBytes并先由memory.TryReserve取得独立lease，拒接前无登记；成功接纳后的此lease保到服务Close和私有Core真实退出，不能随请求终态归还仍保留的ID费用。请求工作预约另算当前Source/结果/窗口与在途Core费用，嵌套预约和ID累计均受同memory总容量限制；预约退还未知仍封接纳保原根。有限id数量不等于无需计账。

没有可信Reference时禁止把自身拟合plane当自己的评价真值；样本用于软件/显示时标Synthetic/NotEvaluated。建议回执包括Source/hash、各候选CalculationIdentity/实际参数/版本、分母/误差/原因，完整候选参数仍由原request关联，不写回Profile。宿主可显式查看/比较/拒绝；采纳仅创建新ProfileRevision/请求，生产参数、量测事实、参考资格和设备命令均不由Analysis写。采纳后同样本Golden与不同代表样本Replay的泛化验证属用途Owner，不把单个样本建议冻结为已资格生产参数。

### D.5 双消费者、UI与可判定Golden

Reference Host在B.5的显式Reference输入上先获得plane候选，再用方向/支撑证据显式HeightFieldParameters或Normals；有真实规则网格时以GridCurvatureParameters看局部曲率。Connector Host独立实例用显式有孔高度网格及已有mesh拓扑，Height偏差/Curvature仅是几何候选，孔/边/异常分母与Topology并列，不变成连接器缺陷规则。两者各自Analysis/core/backend根与Profile，factory前有限槽/原Execute/Close/Dispose保留顺序沿B.5，先清Analysis自有Core/本native，再Core服务，再独占backend；不同Host不得互相关。Advice两Host各有明确Reference/Gate与有限候选集合，未提供物理Reference该用途拒答，不阻普通Topology。

可选WPF同工程C.1附加公开 `SurfaceAnalysisControlFactory.Create(SurfaceAnalysisService analysis,IUiTextCatalog text,SurfaceFeatures3DViewOptions view):SurfaceAnalysisControl`，唯一factory；控件公开 `Attach(SurfaceAnalysisRequest request):long`、`SetCulture(string):void`、`DetachAsync(TimeSpan,CancellationToken):ValueTask<DrainReport>`，借用Analysis与viewport。本WPF工程为此显式增加本模块Halcon DLL引用（只托管API，constructor无native），不改变Core目标。展示是结果表/曲率颜色图层与有限候选比较列表，底部计算/取消/导出证据；建议选择仅发公开事件 `Action<string,long,string,string>? SuggestionSelected`（InstanceId/Generation/CandidateId/AnalysisIdentity），按钮采用建议仅当前代Eligible且Permission.Can(EditParameters,Source)复核通过，不直接写Profile。控件借用服务不Close，只取消自己请求，Detached/语言/同binding规则沿C。

计算复用A.6的Preview权限，Ctrl+Enter计算、Esc取消自己的请求、Ctrl+Backspace丢弃草稿、Ctrl+Shift+E导出；执行/导出/采用前分别再核Preview/ExportEvidence/EditParameters。Attach只挂接并深冻结草稿，不启动计算；每次计算使用A.6实例/代次/counter生成新外层RequestId覆盖草稿ID，保原草稿ID作本地关联。编辑、新Attach或撤权令旧代次Stale，旧结果禁采用/导出；取消与排空恢复不因撤权禁用。分析控件公开 `Action<string,long,SurfaceAnalysisResult>? EvidenceExportRequested`，仅当前已完成、资源归还且权限通过的结果触发，宿主负责持久化。计算文字=`计算/計算/Calculate`、采用建议=`采用建议/採用建議/Use suggestion`，其余资源键/缺key/语言切换原Task规则沿C。

D显示公开增量在WPF namespace为 `FeatureAnalysisSceneRequest(string InstanceId,long Generation,SurfaceSnapshot Source,SurfaceAnalysisResult Result)`、`IFeatureAnalysisSceneProvider.PrepareAnalysisAsync(FeatureAnalysisSceneRequest request,CancellationToken ct):Task<FeatureSceneReply>`；provider实现方即C.2同一场景Owner的明确扩展，返回FeatureSceneBinding.Layer=Derived、CalculationIdentity=Result.Identity，DisplayedIdentity绑定准确原Source+派生overlay证据，SourceMaps保原坐标/单位，不为颜色场虚造mesh。`BorrowedFeatureViewport.ShowAnalysis(FeatureAnalysisSceneRequest request):void`直接入原有界账本，通过同scenes对象的显式IFeatureAnalysisSceneProvider调用；factory可仅提供C.2基础provider，D控件创建时则必须检查其支持此接口，否则FeatureSceneUnavailable且不挂接，不反射猜方法。AnalysisControl的view.Viewport须为该BorrowedFeatureViewport，避免void窄接口吞无消费者接线。场景完成仍走原同binding Attach/Update/trace/可见与Unbind；不得把分析结果硬转SurfaceFeatureResult。无UI使用Analysis不需要该provider。

曲率行文本为 `局部曲率/局部曲率/Local curvature`，限制 `窗口缺少有效点/視窗缺少有效點/Window has missing samples`，拒答 `没有合格建议/沒有合格建議/No eligible suggestion`，精度失败 `转换误差超限/轉換誤差超限/Conversion error exceeds limit`；单位/方向/输入hash/窗口物理大小与用途未评价始终可见。没有全模块“自动运行”或生产放行按钮，1920×1080净client验证保持C.5。

| 断言 | 具体软件输入/期望（不是客户资格或已执行结果） |
|---|---|
| AN01 Height | O=(0,0,1)mm，n=(0,0,1)，点Z=[0,1,3]→Height=[−1,0,2]mm；翻向→[1,0,−2]；Validity=false/Unknown字段null，不把0删掉 |
| AN02 曲率平面/碗 | 5×5中心row/col=2，pitch=1mm，完整Valid，z=0→内3×3H/K/k均0、边缘null；z=(x²+y²)/(2R)、R=10mm，中心H=kmin=kmax=0.1/mm，K=0.01/mm²（解析真值）；HALCON拟合误差/float往返分别核Profile容差 |
| AN03 混合/反向 | z=(x²−y²)/(2R)→中心H=0、K=−0.01/mm²、k=[−0.1,+0.1]/mm；交换row/column布局/pitch但保同物理表面应同结果。正向约定反转须提供相应重新绑定的右手Grid/row布局，H与k符号反转/K不变；仅翻HeightDirection使基左手则拒绝。z=x*y/R中心k=[−0.1,+0.1]/mm/H=0/K=−0.01，用非零γ校验b |
| AN04 有效域/映射 | 中心缺一个槽/Unknown/无连续证据、网格不正交/XY超容差、边界窗口不全、窗口>caps：相应字段null或native前拒绝，孔邻不拟合；gen_region_runs仅完整窗口，fit忽略domain反例必测 |
| AN05 浮点/资源 | q米转float超阈、非有限输出/判别式越负限、清理失败/取消超时/原Task晚返：不消费Fields，原图/tuple/lease保到真实退出；有限wait不能证明释放 |
| AN06 Advice | 两Plane/Normals候选同分由Id ordinal选择；一候选翻面/缺精密来源/剔点造成分母假升高→不Eligible；Reference/阈值缺失→无建议；NativeRms很小但几何偏差超限仍拒，不自行开根 |
| AN07 双Host/UI | 两独立Analysis、不同单位/window/gate；同实例连续两个不同RequestId且同几何/候选均可执行，内部ID不重复且未提前Close；双STA取消/语言隔离、撤权/键盘，选择建议只发明确事件、旧generation禁采纳/导出，原Owner链闭合才退出0 |

AN矩阵沿B.6有限case/suite/watchdog；如实际负载使限额不足须显式新软件Profile，不能在等候中扩时。Benchmark新增维度window W/H、完整窗口数/缺测比例、n*window贡献、float误差门、候选数与每操作类型；记录每窗口/候选native/评价、整体接纳→资源归还P50/P95/P99、峰值、失败/删失与取消排空，目标来源仍消费者Profile/TargetPending。NativeRms四步辨别是B.4独立门，不是AN02精确几何真值的前提。

## 附录 E：surface-data消费、输入封套与无损重开

### E.1 明确版本/调用面及Int64来源边界

依赖固定 [surface-data 0.6.0-prep](../surface-data/DEVELOPMENT-GUIDE.md) 的Core0.4/Contribution0.1；本模块不重审C1–C5算法，不复制byte读取、坐标求解、CSR父值算法。B.1 DLL额外直接引用上游Core/需要的Adapters公共包，本地映射类型放 `Asun.Modules.SurfaceFeatures3D.Halcon.Import`；同B.1 Exe追加 `--import-cases`，没有新工程。纯SF-C1/C2仍BCL、不受桥部署阻断。

当前SF-A1直接以CPU double XYZ经cv2.gen_object_model_3d_from_points组装，不调用上游H的SurfaceImageLibFactory或FilterAsync；viewport内置渲染也不是本模块H调用。因此H1行为变化不要求在此主算法暗插worker/H1。**宿主显式选上游H预筛的真实链**按E.3给出精确装配/精度拒绝；不把H的进程硬限转称SF-A1硬native限。本模块保持首发不支持RequireHardMemoryLimit的SF-A1，不能绕H隔离借字面相似作保证。

公开局部输入/sidecar与factory固定为：

```csharp
// namespace ...Halcon.Import；SD是Asun.Modules.SurfaceData的类型别名。
public sealed record ImportField(string FieldId, string AttributeName, string Unit);
public sealed record ImportNormals(string XField, string YField, string ZField,
    EvidenceRef DirectionEvidence);
public sealed record SurfaceImportRequest(SD.SurfaceDescriptor Descriptor,
    SD.ResourceBudget ReadBudget, SD.FrameReference TargetFrame,
    SD.MappingReference? Transform, ulong Generation,
    string LocalSurfaceId, long LocalRevision, string DomainId,
    ImmutableArray<ImportField> Attributes, ImportNormals? Normals,
    SurfacePurpose Purpose, EvidenceRef? UseQualification);
public sealed record ImportedSourceRow(int LocalSourceIndex, long CarrierOrdinal,
    SD.SurfaceKey Root, long RootIndex, SD.SampleState State, uint Reason,
    int OriginId);
public sealed record ImportedFeatureSurface(SurfaceSnapshot Snapshot,
    SD.SurfaceSnapshotMetadata Metadata, ImmutableArray<ImportedSourceRow> Rows,
    SD.FrameReference Frame, SD.MappingReference? Mapping,
    SurfacePurpose Purpose, EvidenceRef? UseQualification);
public sealed record SurfaceImportReply(ImportedFeatureSurface? Surface,
    ImmutableArray<ValidationIssue> Issues, bool Drained, bool ResourcesReleased);
public sealed record SurfaceImportLimits(int MaxPoints, int MaxFaces,
    int MaxAttributes, long MaxRetainedBytes, TimeSpan ObservationBudget);
public static class SurfaceFeaturesDataBridgeFactory
{
    // public static SurfaceFeaturesDataBridge Create(SD.ISurfaceDataService service,
    //     SD.SurfaceMetadataLimits metadataLimits, SurfaceImportLimits limits);
}
public sealed class SurfaceFeaturesDataBridge : IAsyncDisposable
{
    // public ValueTask<SurfaceImportReply> ImportAsync(SurfaceImportRequest request,
    //     CancellationToken cancellation = default);
    // public ValueTask<DrainReport> CloseAsync(TimeSpan waitBudget,
    //     CancellationToken waitCancellation = default);
    // public ValueTask DisposeAsync();
}
```

以上SD书写为文档类型限定，实际C#用各SD类型全名或明确using alias，不编造namespace对象。所有Input/限额/DTO先校验深冻结；factory只托管配置检查，借用service不Close；桥最多一个Import、无队列。LocalId/rev/domain遵A.1，Generation正ulong、原上游SurfaceKey.Revision原样留sidecar（不强转long）。点面数须各≤limits且int可表示；属性名/字段Id唯一，标量Vertex字段，Unit与上游Encoding.UnitId精确相等；Normals3列无量纲且相同domain，DirectionEvidence精确版/hash，逐点状态各自检查，不靠位置mask代替。本地SourceIndex**固定0..n−1**，它是本地载体地址；RootIndex保持Int64不转double/不cast int；原carrier/Root/Origin关系保在Rows+Metadata，不声称本地int就是真实根索引。来自不同Root的同数值也不同身份。

### E.2 完整读链、有效域和资格

1. 外部Host在factory前预留有限根槽，保存借用service、request/metadataLimits/源Owner、返回bridge与原Import/Close/Dispose及上游operation.Completion。点/面/属性暂存、后续深冻结与metadata编码都计MaxRetainedBytes；预估新增托管账=`256*n+64*f+32*n*a+2*metadataLimits.MaxMetadataBytes+65536`，再加两个ReadBudget已批准ResidentUpperBound（读取不同时仍保vertex暂存，不能省账），checked超限native/源调用前拒S3D-008，不填0省lease费用。
2. 构造上游SurfaceReadRequest：完整Vertex域Range=(Vertex,Ordinal,0,VertexCount,null,AllowEmpty:true)，Selection=PreserveAll、ReadCoordinates=true、TargetFrame/Transform取显式输入，FieldIds为明确属性/Normals列；用service.Plan核计划/预算→StartRead(request,bridge内部有界ISurfaceBlockConsumer,ct)。返回StartResult.Operation非null才保存原Completion，失败无操作不造Released。OnBlock同步仅拷贝受限Ordinals/SourceIndices/Positions/字段packed值与State/Reason/Origin到预留缓冲，Span不跨await，不调用Completion/Close等待自身。
3. 点顺序按原CarrierOrdinal升序恢复全域，计数完整、不重复、不丢Invalid/Unknown槽；只有Completion.Outcome=Completed、DeliveredItems=原请求数、Operation资源真实归还后采用。Receipt.Integrity=FullBuffers才允许用途声明为精密支撑；RequestedBytes只保持原范围验证等级。PointCloud/Mesh XYZ来自上游CPU Positions；HeightField XY必须上游Grid.Mapping经IM-007显式映射，crop父offset仅该链处理一次，本地XyzMapping用local row/col。FrameReference.Id/Revision/Unit保sidecar，本地CoordinateFrame精确为Frame.Id+"@"+Revision无前导零十进制（上游Id不允许@）；不猜世界坐标。单位枚举逐项显式m/mm/um映射，不用int ordinal cast。
4. 如果TriangleMesh，另发完整Face域、Selection=PreserveAll/ReadCoordinates=false的新Generation/operation，同冻结Descriptor（Source.Owner保证不可变修订），FieldIds恰TriangleIndices；读取UInt32/UInt64三分量raw（结构列scale1/bias0），真实ordinal落0..n−1且int可表示才Triangle。Face原序不改、重复/退化保留给Topology；Vertex/Face任何一步失败整Import暂存失效，不返回前半Snapshot。点云/HeightField不隐式三角化。
5. 本地Validity=State==Valid；Invalid/Unknown分别InvalidReasons=`SourceInvalid:<reason>`/`SourceUnknown:<reason>`，源0 reason仍保unknown类别不补Valid。无效CPU NaN保raw位，A.1允许无效NaN而有效非有限拒绝；正常有效0/负Z保留。Attributes按上游ValueEncoding.Scale/Bias/ByteOrder读物理double并保独立Validity；无效value保原解码位，不能借位置合法抬属性。Normals各状态均Valid且向量有限非零才NormalValidity，零值无效不填+Z。
6. 用SD.SurfaceMetadataCodec.Encode(new SurfaceSnapshotMetadata(new SurfaceSet(明确局部manifestId,正revision,[原Descriptor]),Empty贡献或宿主准确同Carrier贡献),metadataLimits)获取有界metadata信封/hash，原descriptor/Origin不可变存入sidecar。manifestId固定=Descriptor.Key.Id、revision=Key.Revision，仅单层选择，不暗合多层；贡献若实际需要则由调用者先按C5公开端口取得/验证完整descriptor，不能自行编父权重。当前Import公开request未带Contribution时Metadata.Contributions=Empty，源Origin有派生/多父仅保声明，**不宣称贡献完整**；精密用途需UseQualification引用原Owner已核的精确贡献/支撑资格，否则拒S3D-011。不从Origin.HasExactParentIndex或C5协议通过自授算法真值。
7. Snapshot.AcquisitionRef固定EvidenceRef(Key.Id,Key.Revision无前导零十进制,metadata信封SHA-256)，仅协议定位，非真实性资格；ContinuousSupportRef只由Host显式提供，Importer不自动把一般UseQualification当该证据。创建A.1 Snapshot时因此ContinuousSupportRef=null，需要邻域精密请求的Host使用新的SnapshotData与明确连续证据重新Create并取得新hash。Frame/Calibration/Qualification事实由原Owner提供，不从方法名造CalibrationRef。原Index/Origin/理由在Rows保留；属性及法线原字段的三态/Reason/Origin由Metadata绑定的原RawBuffer保留，本地bool仅表示本字段可用，不能据此恢复Unknown和Invalid的区别。source Snapshot只提供几何层、不冒损失前的客户量值。
8. 返回前全部上游operation原Task退出、暂存工作资源归还；bridge自己的snapshot/sidecar交Host持有。Import的原Task不可提前终态；观察到期返回等待摘要在Close，仍保桥/上游operation/缓冲。Close封接纳、对自己两个operation RequestCancel、观察原Completion，不调用借用service.Close；Dispose等真实退出，资源Unknown保根不重新Start。异常不覆盖原读错误，Core/Analysis仅在成功Import且用途资格/连续性条件分别满足后发请求。

结果映射回上游：Core SourceMapping.Parent必须等ImportedSnapshot.Identity，逐local SourceIndex查Rows取得精确(Root,RootIndex,CarrierOrdinal)；派生多贡献保列表，不将平均权重/唯一根强编。FaceContributors先按原本地face ID映回Descriptor的FaceIndices/CarrierFaceOrdinal，根face Int64通过显式上游Face读取保留；若宿主未保face根sidecar（本导入Rows只vertex），只回原carrier face ordinal并明确RootFaceUnavailable，不能以vertex根当face根。Topology结构结果可单独使用，物理用途按缺失程度拒绝，DisplayDerived可显示限制。

### E.3 可选上游H与metadata格式注册/回退

实际Host若在Import之前显式调用SD H：先通过C1–C5读取并持有CPU副本→用真实部署 `SD.NativeRuntimeBinding(绝对WorkerExecutable,WorkerSha256,AsunImageSha256,WorkerCommitLimitBytes,MaxWireBytes,new NativeAccuracyPolicy(id,revision,maxError))`→`Asun.Modules.SurfaceData.ImageLib.SurfaceImageLibFactory.Create(adapterBudget,TimeProvider.System,runtime)`→FilterAsync(NativePointInput,显式CoordinateInterval集合,ct)，保存原ValueTask.AsTask一次到有限进程根。运行绑定hash/commit/wire与源副本预算由发布/用途Profile显式提供；旧两参数Create非空native会BudgetUnavailable，不能补个空runtime绕过。

H1 OrganizedGrid固定米制float32图，maxError为原输入单位、有限≥0且来自精度Profile；0是要求精确往返，不是无损默认。H2 double tuple也核单位往返；H3所选slots必须与原CPU闭区间集合一致。只采用Completed/ResourcesReleased=true及当前generation的Output.SelectedSlots（原input int槽）/CPU Positions；原Ordinal/Root仍从输入Int64旁表回溯。超精度/边界不一致/资源未知全链拒绝，不放宽maxError、不静默换H2，不用native量化值盖原Source高度。选点产生新Descriptor/域/hash/来源由原数据Producer发布后重新Import；不能直接拿旧metadata修mask洗新几何。H的worker/process/pipe/job与上游lease分别保原Owner，Kill请求不冒退出，H退出也不证明Source service已关闭。

若宿主采用SD新metadata codec，注册链固定 `SurfaceAdaptersFactory.CreateMetadataFormatValidator(metadataVersionRef,metadataLimits)`、`CreateRawBufferFormatValidator(rawVersionRef,maxBufferBytes,readChunkBytes)`，准确加入IM-066 `ResolvedStorageConfiguration.FormatValidators` **在其Runtime创建前**；Id=`surface-metadata`/`surface-raw-buffer`、Revision1、Hash由实际格式发布包提供，Format整条比对，不造本轮二进制hash。原buffer独立hash/ObjectRef/raw长度，metadata不含lease/native/task。未知schema/缺validator/旧manifest不能自动ignore或迁写；保旧包/旧对象/旧格式注册表，显式退出新runtime并真实归还后回退对应旧包与旧对象引用，新的Store Runtime不能拿旧epoch接原事务。未采用SD codec的SF-C1/BCL Snapshot测试与既有宿主不被强迫迁移存储格式。

### E.4 本模块快照封套codec、边界和重开

Benchmark/两个离线消费Host的局部输入文件已有A.1/§13.2规范二进制，必须有确定decoder，不能让实现者从示例猜序列化。纯Snapshot的基础读写不改其0.3编码；E的Import封套还须保Int64/来源/元数据，因此使用单独的 `surface-features-3d.import/1`，不把同名Snapshot字节升级改写。公开在Import namespace：

```csharp
public sealed record FeatureCodecLimits(int MaxBytes,int MaxPoints,int MaxFaces,
    int MaxAttributes,int MaxStringBytes,long MaxResidentBytes);
public sealed record FeatureEncodeReply(ImmutableArray<byte> Bytes,
    ImmutableArray<ValidationIssue> Issues);
public sealed record FeatureDecodeReply(ImportedFeatureSurface? Surface,
    ImmutableArray<ValidationIssue> Issues);
public static class FeatureSurfaceCodec
{
    // public static FeatureEncodeReply Encode(ImportedFeatureSurface value,
    //     FeatureCodecLimits limits, SD.SurfaceMetadataLimits upstreamLimits);
    // public static FeatureDecodeReply Decode(ReadOnlySpan<byte> bytes,
    //     FeatureCodecLimits limits, SD.SurfaceMetadataLimits upstreamLimits);
}
```

无factory/IO/native/自动类型反射。限额各正且checked可表示；错误返回空bytes/null Surface+issues不发布半对象。信封按顺序：8-byte ASCII `S3DIMPT1`、UInt32LE版本1、UInt32LE bodyLength、body、32-byte SHA256（前缀/长度/body全部）；整包≤MaxBytes。body为UInt32LE A.1完整Snapshot字节长度+原字节→UInt32LE SD完整metadata信封长度+原字节→Rows（Int32LE count、各record声明顺序：local int/carrier Int64/Root.Id与ulong revision/RootIndex Int64/State byte/Reason uint/OriginId int）→Frame.Id/rev ulong/上游LengthUnit Int32→Mapping(nullable Id/rev ulong)→Purpose Int32→UseQualification(nullable EvidenceRef)。字符串用A.1 Int32LE UTF8长度（null只nullable字段），UTF8严格拒坏字节/超MaxStringBytes；集合不default。Snapshot不含自己的hash字段，Decode经A.1 factory重算；原SD metadata bytes经上游Decode核schema/hash/limits，不能对其按A.1另解。state byte严格0/1/2，枚举逐上游约定，unknown拒绝。所有root/ordinal long无浮点转换。

分配前cursor先check长度/count≤对应quota/剩余最小element字节、递归深度固定≤16、无尾部多余字节；SHA不等拒S3D-004，未知版本S3D-001。Rows.Count恰Snapshot点数，LocalSourceIndex与Snapshot.SourceIndex逐项相等且0..n−1、CarrierOrdinal按顺序覆盖0..n−1、Root等对应Descriptor.VertexIndices.Root；Geometry点/面长度与Metadata单层Descriptor相容。Snapshot单位须逐项对应Frame.Unit且等Descriptor.Unit，CoordinateFrame须精确等E.2的Frame.Id@Revision；Frame不同于原Descriptor.Frame时Mapping必须非null且由原坐标Owner绑定该转换，不能把转换后的Frame硬校成原Frame或凭Mapping字符串证明转换真实性。State决定Snapshot.Validity，OriginId在Origins内、Reason原值保留，Snapshot.InvalidReasons逐项按E.2生成规则核对，UseQualification的nullable EvidenceRef按A.1编码/验证。DeclaredField的RootIndex/State控制列实值**不能仅由metadata验证**；离线Decode只保持原信封声明，重开精密用途还须原Owner可信完整bytes验证/资格或重读C1–C5逐值比对。不把SHA合法当来源真实性。新增驻留账为两套Snapshot/sidecar托管费用（E.2公式）+2*MaxBytes+upstreamLimits.MaxResidentBytes+65536，超MaxResidentBytes先拒；OOM非隐含成功。

重开顺序：发布Owner准确ObjectRef/文件hash→有界读完整信封→Decode→核用途版本/frame/qualification及RawBuffer引用→无nativeSnapshot回放→新请求执行→真实释放后采用。结果不持久化运行Task/旧根/旧Execute完成回执或恢复质量状态。生产存储如选本格式，Id=surface-features-3d-import/Revision1；公开 `FeatureSurfaceCodec.CreateFormatValidator(SDC.VersionRef format,FeatureCodecLimits limits,SD.SurfaceMetadataLimits upstreamLimits):SDC.IStorageObjectFormatValidator`，SDC明确为 `Asun.Platform.StorageDatabase.Contracts`，Halcon DLL为此只引用其Contracts程序集不引用Runtime/数据库实现。validator的Format精确同传入VersionRef；ValueTask ValidateAsync(Stream,long bytes,CancellationToken)只读恰declared bytes≤MaxBytes→Decode，失败抛InvalidDataException，短读补至恰bytes、提前0拒绝；不保/Dispose借用stream、不seek/外部IO。配置准确加入同Runtime FormatValidators，原Owner拥有ObjectRef/事务与版/hash，模块不StageAndSeal/写库；未使用该格式不增运行时存储服务依赖。

| 断言 | 明确期望 |
|---|---|
| IM01 | 上游RootIndex=9007199254740993、CarrierOrdinal=0→本地SourceIndex0、sidecar仍该Int64，Root不同但数字同不合并；重开及映射不变，不经double |
| IM02 | Valid z=0/负高保值；Unknown/Invalid仍两种理由及Origin，独立属性Unknown不因XYZ Valid变Valid；HF非零crop只由Grid/CG链处理一次 |
| IM03 | Vertex/Face读取乱序块正确恢复、duplicate/missing ordinal/坏index/不同revision失败；一读取消/短读/消费者throw整体不采用，RootFace未保存不假造根face |
| IM04 | H1 real边界量化超Profile/闭区间进出不等→Integrity拒绝；runtime/hash缺或旧两参factory拒绝；Kill尚未退出/上游lease晚归还分别保根，未用H主线不新增H dependency |
| IM05 | Snapshot/import信封字段逐项Encode→Decode→Encode bytes相等，Int64/−0/Invalid NaN位与原SD metadata保留；未知版/尾字节/长度越quota/校验hash错/合法hash但Root不匹配均拒绝，无半对象 |
| IM06 | 两离线消费者用同包公开bridge/codec，一为参考工具一为连接器几何；只读格式注册在Runtime前冻结、旧包/对象回退不重写源；缺Store/来源资格只阻真实持久化/精密用途 |

IM case沿B.6有限预算和原Owner观察规则；上游HF-A/B/P/Q及577-byte有效向量仅复用，不重算/复制第二份权威。独立大Root/Unknown/codec损坏是本消费新增断言，不冒上游Golden已运行或本codec已实现。

### E.5 SF-A1固定readback身份、保孔和单位补足

实际C#使用 `using cv2 = ImageLibDotNet.Cv2;`（surface-data §17.1已给公开类型/版本证据），B/§4中的snake_case为HALCON算子名，调用时用该public Cv2对应公开方法/tuple资源形状；仅确切重载/封送歧义核签名，不去AsunImage内部找源码。B.3每个成功out立刻登记，对象模型clear真实退出后才Dispose承载tuple，tuple Dispose不等clear对象模型。

输入normal/select/smooth输出按精确token或官方保序回散原索引；Normals/Smooth保留完整原槽，Invalid/Unknown旧XYZ与理由不改、NormalValidity=false；合法原点仍有效。Select/subset采样/triangulation仅输出原实际subset，SourceIndex经token回溯；位置新生成/父映射未知的sample输出SourceIndex=输出局部ordinal，SourceMapping.Unavailable及DisplayDerived限制，不拿该编号当原根。生成面FaceContributors必须实际公开或Producer记录贡献，只有顶点token不能推完整面父关系；本模块不重新求上游贡献权重。

派生snapshot的SurfaceId固定=`s3d-`+CalculationIdentity、Revision=1（每次不同几何身份另id；同几何重复RequestId规则仍A.4），DomainId继承显式源域但不获新连续性资格；任何改坐标/域/采样/面结果ContinuousSupportRef=null，需要精密后步则原Owner用确切新支撑资格重新Create而产生新hash。Normals坐标/域未变可保原连续证据。SupportEvidence分母原Source总点数/有效点数不变；Attributes仅精确可映射的值保独立Validity，丢属性给明确限制，不填0。

mapping三角化除native补洞关闭，还在读回按实际original_point_indices→输入row/col过滤：每三角三个不同观测槽，row跨度=1且col跨度=1，恰同一相邻2×2格三个有效槽才保留；不跨多pixel缺口、未知槽或非相邻区域。保留原face顺序与native信息，诊断ExcludedFaces；这一必要有效域验收不授客户连续面资格。greedy关闭补洞仍可能跨空间断面，精密输入必须独立连续组件域/证据，无法证明时拒绝或Insufficient，不按输出闭环授完整性。

Fit所有首发generic冻结§4.2已列primitive_type/fitting_algorithm/min_radius/max_radius/output_point_coord/output_xyz_mapping；其他手册参数不透传，HALCON26.05原生固定默认的语义随BackendCapability版本锁定，不由开发者自选robust clipping。Primitive参数/Extent可知单位按A.3，NativeRms仍B.4四步运行门。Section source face来源未公开时保持Unavailable；C.2只显示有明确scene投影的结果，不造parent face。Distance原MaxDistance/AtLimit/ClosestTargetIndex−1与精确目标限定保持；建议不读取截断值作精确评价。


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

## 18. 当前全部批准范围的文档准备结论与剩余Owner

### 18.1 全范围覆盖与可决定设计结论（2026-10-12）

**当前IM-034架构完整范围及本轮明确的高度/局部曲率/参数建议需求，可决定的软件设计已闭合，文档准备完成；没有需后续开发者临时补猜的内部算法/API/架构欠账。** 本结论由本永久原会话执行内容审核、修复与定向验证，不等待总控内容复核；总控只接收状态。SF-C1/C2既有六项与A.1–A.5规范保持，SF-A1/W1既有限定内容接收保持，新增D/E为外围明确规格；不自行提升为整模块ModuleCoreImplementationReady或ImplementationSpecificationReady。

| 批准能力/真实使用场景 | 唯一实施位置 | 可直接照文实施的范围与不适用条件 |
|---|---|---|
| 单表面XYZ/规则高度/已有mesh输入、属性筛选/裁切 | §1–4、A.1–2、B.3、E.1–2 | 强类型快照/逐字段读链、单位/坐标/有效域、Root旁表；不把灰度当高度、不猜多层/物理frame |
| 采样/平滑/法线与方向 | §4.1–3、A.2、B.2–3、E.5 | 固定HALCON候选/参数适用支撑/来源回读；不改源/补洞/把inwards当产品上方向，缺精密贡献拒绝 |
| 形状primitive/连通/三角化/拓扑/截面/距离 | §2/4/8、A.3–5、B.3–6、E.5 | 单次显式操作、保孔/索引/符号/AtLimit、两个真实消费者；不提供配准、参考资格、缺陷分类或工艺放行 |
| 高度、局部曲率及几何异常场 | D.1–3/D.5 | 显式轴/plane高度、正交规则物理网格曲率/窗口与精度门、完整支撑/null/几何真值；任意散点/mesh曲率无此输入则明确不支持，不伪装PCA统计 |
| native_rms与精确几何残差 | A.3/B.4/D.2–4 | 原生诊断NativeUnknown及四步辨别门；独立几何参考距离/解析曲率真值不依赖原生统计单位 |
| 自动参数/建议/显式采纳 | D.1/D.4–5 | 有界候选、外部Reference/Gate、稳定评价与拒答、版本/过期、宿主新Profile；不训练/静默改生产值或自选参考面 |
| 原Owner/线程/取消超时/资源和恢复 | §5–7/10.1、A.4、B.3/5、C.3–4、D.1、E.2–3 | factory前有限根/原Task与借用资源/双轴错误/真实排空/晚到归还；不以观察到期或进程结束冒释放；SF-A1无硬native限承诺 |
| 独立WPF/紧凑工作台/三语/权限/键盘/显示 | §9/A.6、C.1–5/D.5 | DevExpress实际成员与固定布局、同Control Presentation/Lifetime v0.2完整Submission/资源schema、双STA与独立退出；控件无事实/设备权限，全部业务仍无UI可调 |
| surface-data/坐标/来源资格/可选H与格式 | E.1–4 | SD0.6.0消费桥、Int64根/Unknown、精度Profile/运行绑定及格式启动注册/回退；不重审C1–C5、不自动插H、不恢复丢失float精度 |
| 编码/身份/发布/回放与回退 | A.1/§13–14、B.1/C.1、D.1/E.4–5 | Core0.3保持、新Analysis0.1/import1独立版本、唯一工程/Exe与命令、有限decoder/重开；不持久Task/lease或新建产品数据库事实 |
| 正确性/性能/双消费者与测试计划 | §11–13、B.4–6/C.4–5/D.5/E.4 | 正常/缺测/坏输入/重复/并发/取消/晚返/资源Unknown/升级反例、解析Golden、负载/完整排空统计与目标来源；未运行项不称PASS |

本轮把当前用户明确的局部曲率/建议纳入独立外围合同，而不篡改已收Core或将未开放任意自由曲面识别强行开工。曲率的HALCON拟合路线、算法数学、float误差和ROI窗口缺测规则已定；实际Profile、真实视觉容差和运行证据仍是资格输入。局部软件numeric fixture只消除公式/单位/索引歧义，不替客户验收。

### 18.2 证据复用与两轮有限自审

既有HALCON26.05 normal/smooth/sample/fit/triangulate/connection/distance/section/get-params、固定Open3D实现/测试/版本/MIT与两无UI/双STA自审沿§17复用，未重审Core、重算旧Golden或重新下载上游源码。此次实际缺口的增量证据为：

- [fit_surface_second_order 26.05原文](../../../halcon算子手册/operators/fit_surface_second_order.html)，SHA256=`27061bb508cca843bca31758cf230ce220b1bd6390f4f3c5dc49e572a021f6c9`：读取内嵌SVG公式/完整参数/输入real范围与忽略Image domain警告；α/β对应row/column平方、γ混合项、δ/ε一次项已按物理pitch转换，未从算子名推曲率。
- [gen_image1](../../../halcon算子手册/operators/gen_image1.html) SHA256=`d268da1562bab640cc506296c1684eaa643f97b84b705d3c9cf47bbdd5c019c3` 与 [gen_region_runs](../../../halcon算子手册/operators/gen_region_runs.html) SHA256=`8f7f1845b85bc1873e1507f815f2153d956b6b7561fcdde61396dde4a3b2f203`：只为新增局部窗口的复制/pin/64bit地址/有序行段边界读取，不改上游HALCON桥。GetGrayval/SetGrayval/ReduceDomain资料已排除逐像素native循环/共享图改写/用domain隐藏缺测的做法。
- [MathWorld Mean Curvature](https://mathworld.wolfram.com/MeanCurvature.html) 与 [Gaussian Curvature](https://mathworld.wolfram.com/GaussianCurvature.html)，2026-10-11直接读取图式alt的Monge graph、H/K与H²−K关系。仅用公开数学定义转换HALCON拟合系数，不引入新算法库/商业依赖；固定Open3D证据继续用于来源、方向/退化和RMS语义界限，不假借上游源码证明本新增曲率实现已通过。
- [surface-data](../surface-data/DEVELOPMENT-GUIDE.md)0.6.0-prep §3/16–18与 [viewport](../viewport/DEVELOPMENT-GUIDE.md)0.3.4-prep §10.6–10.9定向消费签名/行为核对；[storage-database](../storage-database/DEVELOPMENT-GUIDE.md)Contracts namespace/Format validator/启动注册核对。没有修改上游、重开其Core/Root/Close或执行它们的测试。
- 本机DevExpress25.2.3 XML的DataControlBase.ItemsSource、ContentItem.Content及TreeListView.KeyFieldName/ParentFieldName补足C.5，版本/依赖按用户确定直接使用，未下载/替换/核许可。

第一轮以实现者正常→异常→恢复走新增局部曲率/Advice/Import/codec：核窗口与原域、metric单位、γ混合项、右手方向、float roundtrip、最坏贡献/预约、返回合法但支撑不足、NativeRms不参与精确指标、清理晚返及版本回退。修正长/角容限混用、导数上限单位、null建议门、分母/截断评价、Int64根索引/Face根边界、元数据不能验证未读取raw真实性。

第二轮以没有产品Shell的两个消费者按公开factory签名装配：Control→同root renderer.Backend/Lifetime→session.Options.Presentation→完整Catalog/ExecutionBudget→bridge→分析控件/精确scene→同binding trace→原Unbind/Revoke/Return；同时核无UIAnalysis/Importer原Task与借用service关闭边界。修正Commit等待收尾自锁、late Acquire根账、Analysis结果不能硬转Core结果、私有Core生命周期、存储Contracts namespace与Runtime前格式注册。复用已接收Core向量，不派生会话/脚本/报告。自审是规格验证，不是产品执行PASS。

2026-10-12最终定向验证已执行：A.1–A.5规范文本SHA256仍为`ac1df0587d8c50b412c9f3c47d6d8ecf098999aa7e266ee5ae569d162cd4ca59`，上述三份HALCON原文hash匹配；本文本地链接、代码围栏、表格列及AN01–07/IM01–06/WU01–10唯一编号检查通过。仅内存算术核对平面/碗/鞍面/混合导数、非等pitch与行列互换、m/mm/um换算、Height示例、Int64及IEEE原始位、封套前缀/长度/hash原语通过；未运行产品decoder或HALCON拟合。现有`python tools/validate_docs.py`通过导航/DAG/消费者映射结构检查，不提供语义完整性或准入证明。私有Core改为服务生命周期持有，请求结束仅排空；内部调用ID以外层RequestId隔离并显式限定/计账，连续两次请求和撤权键盘已补到AN07，运行断言仍未执行。

### 18.3 精确剩余项与责任Owner

| 剩余事项 | Owner/输入 | 只阻断的用途与当前状态 |
|---|---|---|
| 正式实现、公共程序集消费编译/封送、全部软件断言 | 本模块永久原会话，按B/C/D/E唯一工程切片正式派发；真实Cv2/DevExpress/viewport等引用由对应发布包提供 | 未写代码/未建工程/未build。它是待执行验证工作，非未定义软件设计；不把文档结论称实现Ready |
| 实际C1–C5源/Int64/贡献/Origin、连续支撑及原Owner发布 | surface-data/数据Producer与宿主Source/Scene Owner；精确Descriptor/RawBuffer/贡献证据及发布修订 | 无精密贡献/连续性只拒相应精密用途，DisplayDerived明示限制，普通托管Topology不受阻；C5协议通过非算法物理真值 |
| 坐标/物理Grid/正方向/授权及真实scene绑定 | IM-007坐标资产Owner、宿主授权Owner、viewport原发布Owner；冻结Frame/Grid/原变换证据/Authorization/SourceBinding | 真实曲率/物理标尺/有向距离/可见呈现资格；不能编造pitch、最大转换误差或续期权限 |
| 可选SD H运行部署/精度与新存储格式 | 仅显式H消费Host的部署Owner发布worker/hash/commit，使用Owner批准Accuracy；格式发布Owner给VersionRef/hash、宿主IM-066配置Owner在Runtime前注册 | 未调用H/未用codec路径不受影响；H1 real不能默认无损，codec Decode不等原值/工艺资格 |
| native_rms统计归一/单位辨别 | 本模块运行Owner按B.4四步；物理统计消费者给适用域与可核官方定义 | 只阻该字段物理统计用途；NativeUnknown诊断与独立几何残差/局部曲率公式准备不受阻 |
| 真实HALCON/WPF/renderer/lease/资源故障恢复/Golden/性能 | 本模块实现及各公开依赖实际运行Owner，冻结软件/消费者Profile、真实输入/真值/数值容差/目标环境 | 全部尚未执行；AN/IM/WU/HA的合成断言与文档检查不能替真实后端/GPU/计量/长稳 |
| 真实客户物理允差/参考资格/工艺与生产 | 两真实消费者的用途/质量/客户Owner与reference-surface/metrology原Owner | 未指定客户Profile/现场证据，TargetPending或NotEvaluated；无模块质量放行/设备副作用权，不阻无关Core准备 |

当前没有“再由Host决定算法/架构/内部API”的待办；上表缺失值只限制确实依赖的运行/用途，不能把它们改成通用默认。文档准备结论不删除、改写或降级原DEV-GOV-010门禁；正式代码准入、真实运行/集成、客户/生产资格继续分别记录。
