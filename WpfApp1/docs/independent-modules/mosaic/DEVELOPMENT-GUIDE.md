# 多 FOV 拼接（mosaic）独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`M-C1, M-C2, M-C3, M-L1, M-LC, M-LM, M-LR`

- 模块 ID：`IM-023`
- 现有来源：`PKG-017`
- 中文名称：多 FOV 拼接
- 版本：`0.5.8-prep`
- 状态：`DesignReview`；M-C1/M-C2/M-C3、M-L1、M-LC、M-LM 与 M-LR 已接收状态保持；C.2/C.3、M-L2 限定接收保持；完整范围内部设计结论及D.5.1的v0.2装配保持，0.5.8-prep仅按viewport 0.3.5-prep同步实际CPU显示副本生产者、整图空Update/真实确认和后续Update（D.5.2）。实际适配、代码/运行、产品集成与物理资格仍 `PreparationIncomplete`
- 适用基线：C# / .NET 10；HALCON 26.05；通过 `ImageLibDotNet` 使用 AsunImage 公共边界
- 规划消费者：大板查看、拼接分析、跨 FOV 检测；第二消费者验收采用两种互不依赖的视觉宿主
- 本模块算法/公开契约的唯一当前实施正文为本文；平台接入与既有研究映射：[DEV-VIS-029](../../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md)。冲突不得由实现者任选，交主控串行修订映射。

本文是可脱离本检测平台接入的实现指导。它定义模块责任、公开语义、资源和验证边界，不代表代码已经实现、HALCON/AsunImage 适配已经通过、客户 Profile 已冻结或已取得生产资格。正式 DTO、序列化和 Owner 仍由[原候选合同](../../13-contract-candidates/CONTRACT-CANDIDATES.md#mosaic-contract-semantics)的原 Owner 串行采纳；本文不得成为第二份 Schema。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/mosaic/Asun.Modules.Mosaic.Core/Asun.Modules.Mosaic.Core.csproj`；namespace：`Asun.Modules.Mosaic`。预定测试工程：`tests/Modules/mosaic/Asun.Modules.Mosaic.Core.Tests/Asun.Modules.Mosaic.Core.Tests.csproj`。上述项目尚未创建。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 逐切片状态见 §16.1/C.7/D.8：此前 Core/只读软件规格及M-L2限定接收保持；本轮面阵Adapter、标定冷路径、自动建议和WPF指导由原会话自审收口。整模块仍在 `DesignReview`，实际适配/物理/UI运行及正式集成仍 `PreparationIncomplete`。本绑定不是代码已实现、真实适配、集成或生产资格通过声明，实际代码任务仍须明确授权及权威仓库绑定。
- 本轮只读消费增量 `M-LC / CameraRead API 1 → line row0` 的唯一规格在 C.8，状态 `ModuleCoreImplementationReady`（仅六项文档规格）；复用既定 Core API，接入组合工程/Tests 落点见 C.8.1，不在 Core 添加 calibration-assets 实现引用或改 v0.4 DTO。主控已接收该消费桥六项文档规格；真实writer/Store/Qualification/消费编译/LC运行/物理/性能门仍保留，实现仍须另行授权。
- `M-LM / Motion Read Bridge v0.1 → line motion evidence` 的消费规格仅见C.9，状态`ModuleCoreImplementationReady`（仅六项文档规格）；只读组合层消费motion-control 0.2.4-prep A.8，不改Core算法/DTO、上游MR codec或camera缺口，工程/双Host/预算/关闭边界见C.9。
- `M-LR / camera-acquisition C2-RF → line row facts` 的唯一消费规格见 C.10，状态 `ModuleCoreImplementationReady`（仅只读软件消费规格，主控已接收）；组合层通过 camera §20 唯一 producer/reader 消费 ledger snapshot、SourceRevision 和 rows；源typed payload仍由camera原root管理，不复制camera DTO/codec、不发设备命令。真实程序集、消费编译、运行、性能和物理资格仍未验。

## 1. 目标与边界

### 1.1 模块拥有的事实

模块拥有本模块的跨 FOV 拼接标定候选、验证证据与不可变资产内容，以及一次运行请求内的下列派生事实；用途资格决定、激活绑定和设备事实由相应外部 Owner 保留：

1. 原 FOV 的稳定身份、不可变输入引用和观察角色。
2. FOV 间有证据的稀疏关系图、连通分量和变换结果。
3. 每个变换的方向、适用域、残差、支持域和独立验证状态。
4. 虚拟大图目录、半开 tile 网格、LOD/halo、每个输出位置的源贡献和派生关系。
5. 可选显示辐射补偿/接缝结果及其保护冲突；显示结果与原图、检测支持、计量支持分开标记。
6. 本次请求的阶段进度、实际资源、取消/超时/失败原因和可查询的结果引用。

### 1.2 禁止模块拥有的事实

模块不得创建或修改板、子板、工单、制程目标、元件/焊点/开口/缺陷、工艺公差、重复缺陷归并、质量放行、机判 PASS、复判决定、采集触发、运动/光源/PLC 动作、私有数据库表、产品 ViewModel 或全局可变状态。

调用方负责调用顺序、目标关联、程序/配方、工艺解释、质量处置和一切设备副作用。模块输出 `GeometryUsable`、`DisplayUsable` 等用途资格，不输出产品结论。接缝平滑不增加覆盖，缺失 FOV 不等于良品，未知不转成失败或 PASS。

### 1.3 可独立交付边界

建议拆为同一发布包内的 Core、Frame/Coordinate 端口、Vision Adapter、可选 WPF 控件四层：

| 层 | 责任 | 禁止依赖 |
|---|---|---|
| Core | 请求校验、图规划、几何结果、虚拟目录、状态/错误 | HALCON 句柄、窗口、数据库、机台页面 |
| Frame/Coordinate 端口 | 借用 `PKG-006` 帧租约、使用 `PKG-007` 坐标合同 | 私有帧 DTO、隐式单位、显示坐标 |
| Vision Adapter | 在 `ImageLibDotNet` 公共边界核对算子和资源；保存 native 租约 | 将 `HObject`/句柄暴露到 Core/UI；扫描或修改 AsunImage 内部 |
| WPF 控件（可选） | 视口、来源拾取、接缝/原图对照、状态投影 | 自行计算几何、改变质量事实、隐藏关键错误 |

禁止以动态容器获取未登记服务；宿主显式注入每个端口及版本。没有 UI 也必须完整执行核心能力。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Mosaic.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"没有 UI 也必须完整执行核心能力"，Core 在无 WPF 宿主中完整运行。

**Blazor/Web**：拼接全板图按 tile 粒度通过 HTTP Range 分片加载；浏览器只渲染当前视口对应的 tile；坐标映射由 `coordinate-geometry` 服务端计算，浏览器不重写全局坐标变换（同 IM-007 §1A）。

**AI 推理 Tiling**：`ai-inference` §2.3B.4 的 Tiling 机制要求从全板图按 ROI 裁切 tile，本模块的多 FOV 拼接坐标链是这条裁切路径的前置步骤。本模块不持有推理 tile 租约。

**HALCON 双跑**：`bundle_adjust_mosaic` / 全局单应矩阵估计与托管参照路线双跑；对应点坐标残差设容差门禁，图像接缝质量仅诊断。已读 OpenCV 固定 commit `a0cda081` 的 `stitching/` 模块（见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)）仅作语义参照，不引入生产依赖。

## 2. 依赖、用途和数据流

### 2.1 能力依赖

- `PKG-006`：不可变原帧描述、有效域、只读 tile/帧租约和释放。
- `PKG-007`：坐标身份、单位、轴方向、像素中心约定、变换路径和有效域。
- `PKG-016`：已资格化的非线性校正/映射；017 不重复校正。
- `PKG-022`：已资格化的 Mark/轮廓/匹配候选；017 不训练或保存匹配模型。
- 原合同候选 `C-01/03/04/05/07`：身份、图、用途、目录、资源和回执语义。

上述依赖是端口/契约依赖，不要求 Core 引用制程工程或完整宿主。模块不得要求启动采集设备；离线文件、Replay、模拟端口是合法接入方式。

### 2.2 处理链

```text
固定请求/用途
  -> 校验 FOV 身份、帧布局、坐标与 Profile
  -> 固定不可变源描述，再按工作集借用只读租约
  -> 先验投影和空间索引
  -> 建立有物理重叠证据的稀疏图
  -> 受限匹配（必要时）与独立复核
  -> 全局几何求解/闭环检查
  -> 输出原图索引、支持域、变换和 Partial/Complete
  -> 可选显示补偿、保护接缝和 tile/LOD 派生
  -> 版本/权限复核、结果回执和资源归还
```

几何计算、显示融合、检测支持和计量支持是四个正交用途；一条路径完成不自动开放其它路径。

### 2.3 State / Owner / Authority

| 事实或动作 | 唯一 Owner | 本模块权限 | 交接规则 |
|---|---|---|---|
| 原帧内容、租约、解码和物理缓存 | `PKG-006`/帧适配器 | 只读借用 | 通过 lease；最后消费者归还后才回收 |
| 坐标 frame、单位、变换路径和标定适用域 | `PKG-007`/标定 Owner | 使用已登记路径，记录本次引用 | 不改标定、不填单位阵、不扩大域 |
| 采集时命令/反馈位姿、settled、轴 epoch、运动时间戳和温度 | `motion-control`/设备适配器 | 只消费带版本的反馈证据 | 不发运动命令、不改实际位姿；缺证据时阻断物理用途 |
| 跨 FOV 相机—载台/共同平面标定、工作区映射、运动误差地图和补偿修订 | `IM-023 mosaic` | 建立、验证、发布未资格内容，消费外部 Owner 已授予资格的精确资产 | 不在运行时学习、覆盖或扩大适用域；不把结果写回运动或 FOV 光学资产 |
| 单相机 FOV 光学资格 | `calibration-assets` 的 FOV 标定能力；按相机/工位独立发布内参、畸变校正和有效域资产 | 只解析精确身份匹配的资产 | 不推导跨 FOV 位姿或运动映射 |
| 跨 FOV 拼接标定 | `IM-023 mosaic` 的拼接标定能力；单独建立、资格化、修订和回退工作区/相机—运动关系资产 | 读写本模块的拼接候选/验证闭包，只读外部用途资格，解析 calibration-assets 的 FOV 输入 | 不并入 FOV 畸变资产，不在运行时训练或改写 |
| 匹配模型/候选与 native 句柄 | `PKG-022`/Vision Adapter | 只消费候选和结果 | 句柄留在 Adapter；Core 只收结构化证据 |
| 拼接请求生命周期、几何结果、虚拟目录和显示派生 | `IM-023` | 读写本次 attempt 的模块事实 | 终态按本指导；历史保存由宿主/原持久化 Owner 接管 |
| 工艺目标、缺陷关联、质量/放行和设备命令 | 调用宿主/工艺 Owner | 无权限 | 只能消费有明确用途资格的结果 |
| UI 选择、语言、权限和恢复动作 | UI 宿主 | 只投影、发起新请求 | 控件关闭不得释放其它消费者资源 |

模块状态（`Created` 至终态）只描述本次请求；宿主的任务、质量和设备状态不得映射为模块状态，也不得由模块反写。

## 3. 公开数据契约（候选，待原 Owner 采纳）

### 3.1 强类型值对象

实现必须用不可变强类型值对象，禁止用 `double`、`string` 或无单位数组代替下列语义。类型语义由本节和附录 A 定义；Core 切片获主接收后冻结为该模块公开面，平台映射仍待原 Owner 采纳。

| 类型 | 字段/单位 | 范围、默认或规则 |
|---|---|---|
| `MosaicRequestId` | `string Value` | 非空，长度 1..128；宿主生成且全局稳定 |
| `MosaicOperationId` | `Guid SessionEpoch, long Sequence` | epoch 非空、Sequence>0；宿主在实例内严格递增首次准入，重复/过期规则见 §9.1 和附录 A；不表示跨进程持久化 |
| `Revision` | `long Value` | `>=1`；请求、工程、算法和显示修订分别记录 |
| `FovId` | `string Value` | 非空，长度 1..128；同一请求内唯一，不以排序序号替代 |
| `FrameRef` | 帧 ID、字节 hash、尺寸、stride、像素类型、通道、方向、租约版本 | 宽/高正整数；stride >= 行字节；长度算术检查溢出；不设通用最大尺寸，由资源 Profile 限定 |
| `ObservationRole` | 面/层/通道/曝光/时间角色 | 默认 `Unknown`；未知只能诊断，不能进入强度融合 |
| `LengthUnit` | `Pixel`, `Micrometer`, `Millimeter`, `Meter` | 物理运算必须显式换算；默认无单位并拒绝 |
| `Point2` | `double Column`, `double Row` + `FrameId` | 有限值；像素中心约定由坐标合同提供，不在模块猜测 |
| `RectD` | `Min/Max`，半开 `[min,max)` | 有限且 max > min；不允许用负宽表示空域 |
| `TransformModel` | `Rigid`, `Similarity`, `Affine`, `Projective` | 必须由 Profile 显式给出；无通用默认，自由度扩大需批准 |
| `Transform2D` | 3x3 数值、source/target frame、revision、valid domain | 可逆且有限；条件数/行列式门由 Profile；不可逆拒绝 |
| `PriorTransform` | 变换、来源、误差包络、适用时间/空间域 | 无协方差时 `CovarianceAvailability=NotProvided`，不得填零 |
| `FovOpticalCalibrationRef` | machine/station/camera、camera kind、采集配置、asset ID/revision/hash、资格和有效域 | 仅解析单 FOV 内参/畸变校正；不得表达跨 FOV/运动关系 |
| `MosaicRegistrationRef` | mosaic 持有的 machine/station/axis group、相机组、共同 frame、asset ID/revision/hash、资格和工作区 | 独立于 FOV 光学引用；无完全匹配的版本闭包时物理用途拒绝 |
| `LineScanTimingEvidence` | line/row index、曝光时间域、时钟 epoch、扫描方向、实际反馈关联和来源 revision | 只在线扫路线要求时提供；缺行、跨 epoch 或映射不唯一时拒绝物理坐标 |
| `MatchObservation` | 源/目标 FOV、点/轮廓支持、候选索引、score、残差、方法版本 | score 不等协方差；支持不足/歧义/退化独立编码 |
| `MosaicProfile` | 几何模型、搜索、验证、输出用途、资源预算 | 必须包含来源/版本；无默认生产阈值 |
| `TileKey` | `Revision DirectoryRevision, uint Lod, long X/Y, MosaicPurpose Purpose, string Channel` | X/Y 为数学 floor；半开核心不重不漏；LOD 范围由源尺寸、整数安全范围和 Profile 决定 |
| `SourceContribution` | 源 FOV/区域、采样核、Mask、插值支持、来源角色 | 原值、派生值、显示值分开；空贡献不可伪造为黑色像素 |
| `ResourceBudget` | CPU ms、内存 bytes、逻辑读取 bytes、物理解码 bytes、tile 数与租约/句柄数 | 各预算正且有限；v0.3 Core 不开放 Unlimited；deadline 单独由 `DeadlineUtc` 提供 |
| `MotionPoseEvidence` | `q_cmd`、`q_enc`、方向、轴 epoch、settled 证据、运动/帧时间戳、温度 | 每个实际采集 FOV 至少一份；`q_cmd` 不能代替 `q_enc`；时间戳必须同一 epoch 且可关联曝光 |
| `MotionCompensationRef` | 基线连续注册模型之外的附加运动修正引用/修订、适用空间/方向/温度域、最大修正量、资格证据 | 只在基线空间场不能表达且该附加量已独立资格化时使用；不得重复补偿同一残差；越域、过期或方向不匹配拒绝物理用途 |
| `MotionResidual` | 先验与视觉修正的平移/角度/尺度残差、RMS/P95/P99/最大值、支持数 | 先验残差和视觉残差分开保存；优化 Error 不得冒充独立精度 |

### 3.2 请求字段

下面导航 MosaicRequest 的输入语义；字段名/类型/顺序唯一见 A.1，不能按本清单另外增加字段：

- `RequestId`、`OperationId`、`AttemptId`、`ParentRevision`、`AlgorithmRevision`、`ProfileId`、`Purpose`。
- `MachineId`、`StationId`、每个 FOV 的 `CameraId`/`CameraKind`/`AxisGroupId` 和采集配置身份；不可用只在本次请求内唯一的 `FovId` 替代设备身份。
- `ExpectedFovs`（计划全集）与 `ActualFovs`（本次实际源）两份稳定排序清单。
- 需要固定扫描/Tile 身份的请求，另提供完整 `TilePlan`：稳定 `TileId`、行列/目标区域、参考 frame 中的计划目标位置、计划运动位置和 `Capture/Skip` 意图。`TilePlan` 的顺序不等于运动/曝光顺序；每个条目按绝对坐标独立解析，不能靠前一帧或相邻步距推导。
- 每个 `FrameRef`、`ObservationRole`、原始方向、有效域、校正映射引用和获取时间域。
- 分开的 `FovOpticalCalibrationRef` 与 `MosaicRegistrationRef`，分别含 asset ID、revision、hash、资格状态、适用域和坐标路径；引用必须与对应相机/工位/轴组/采集配置精确匹配。不得只传一个无类型的 `CalibrationRef` 或裸矩阵。
- 连续位置计划另传宿主预解析的 `RegistrationPlanningSnapshot`（精确不可变内容、字段和资格消费快照），来源和空形状见附录 A.1。同步 Validate/Plan 不从引用做 IO；快照不能替代 Execute/GetTile 交付前的权威复核。
- 每个实际采集 FOV 的 `MotionPoseEvidence`：命令位姿 `q_cmd`、实际反馈位姿 `q_enc`、轴 epoch、运动方向、settled 状态及证据、触发/曝光/反馈时间戳、采集时温度；静态无运动输入必须显式声明 `NoMotion`，不得伪造编码器位姿。
- 可选 `MotionCompensationRef`；只表示基线连续拼接模型之外、不可与其空间残差重复的附加修正。其空间/方向/温度适用域、修订、证书和最大修正量必须随请求冻结，不能在运行中学习或覆盖。线扫请求还须绑定行/线时间戳、扫描方向、行频/速度域与时钟/编码器关联版本。
- 共同参考 frame、输出网格/原点/相位、tile 核心、halo、LOD 和通道策略。
- 先验路线、匹配路线、独立验证门、保护区、允许接缝区和可选显示方法。
- 绝对 `DeadlineUtc`、`ResourceBudget`、是否允许 `PartialDiagnostic`。请求取消令牌由调用方在单次 `ExecuteAsync` 调用中传入，不存入请求对象或持久化快照。

缺少用途、坐标单位、观察相容性、必需 FOV 政策或资源上限时，拒绝该用途；允许的诊断请求要显式声明 `DiagnosticOnly`。

### 3.3 输出字段

下面导航 MosaicResult 及其不可变子对象的输出语义；精确形状唯一见 A.1，不另外复制 DTO：

- `ExecutionStatus`、`GeometryStatusByComponent`、`CoverageCompleteness`、`PurposeEligibility`。
- 每个 FOV 的来源引用、变换、有效域、匹配/验证证据、缺口和拒绝原因。
- 精确使用的 FOV 光学校正资产和拼接注册资产身份/修订/hash/资格闭包；按 machine/station/camera/axis group 分列，不把多机台或多相机结果压成一个共享标定引用。
- 每个 FOV 的运动资格、`q_cmd/q_enc/q_img/q_comp`（适用时）、反馈与曝光时间差、settled 证据、运动残差和补偿修订；无运动证据时明确 `NoMotion`，不得填零。
- `TilePosePlan` 与 `ObservedFramePose` 分开列出：计划项包含稳定 `TileId`、计划位置、按适用拼接模型预测的计划 Pose、`Capture/Skip` 和域资格；实际图像项另含 FrameRef、曝光关联 `q_enc`、评估出的实际 Pose 与校正证据。被跳过项保留计划身份/位姿但没有 FrameRef、实际 `q_enc` 或观测图像；不能伪造一次曝光或把空白覆盖标成完整。
- 先验变换、视觉修正 `DeltaT_visual`、最终变换及其各自误差预算分开返回；记录运动资格状态（`Qualified/DisplayOnly/Rejected`）和拒绝原因。
- 稀疏图边、未连通分量、闭环残差、最大/分位残差、异常点计数和 `CovarianceAvailability`。
- 不可变 `VirtualMosaicManifest`：frame/transform/域/网格/LOD/halo/通道/方法/算法版本/权限作用域。
- 可选接缝结果：`SeamStatus`、保护冲突、来源标签、数值支持和显示派生引用。
- 资源账本：规划量、实际量、峰值并发、缓存命中、取消阶段、native 排空完成时间。
- `DiagnosticIds`、可观测字段、原始回执引用；结果正文不嵌入 HALCON handle。

`GeometryUsable` 只表示本用途几何证据满足门限，不代表覆盖完整或产品合格。`DisplayUsable` 只表示显示派生可渲染。`MeasurementUsable` 仅在另行资格化后可出现，默认 `NotQualified`。

## 4. 参数、范围与验证顺序

### 4.1 参数目录

以下是实现必须支持的参数类别。数值是安全的设计默认/候选范围，不是客户生产阈值；宿主必须用 Profile 覆盖并把实际值写入请求快照。

| 参数 | 类型/单位 | 候选默认 | 候选范围与验证 |
|---|---|---:|---|
| `RegistrationModel` | 枚举 | 无默认，Profile 必填 | 四类模型；依据运动/标定先验和可观测性冻结；扩大自由度需批准，退化拒绝 |
| `MaxPriorTranslation` | `Length` | 无默认，先验路线必填 | `>=0`；无先验时该字段不适用，不能填 0 冒充严格先验 |
| `MaxPriorRotation` | `Angle` | 无默认，先验路线必填 | `0..180 deg`；单位显式 |
| `MinOverlapArea` | `Area` | 无默认，匹配路线必填 | `>0` 才能启用图像重叠边；否则只允许独立先验 |
| `MinMatchSupport` | `Count` | 无默认，匹配路线必填 | `>=1`；按方法定义点/轮廓支持 |
| `MaxResidual` | `Length` | 未设置 | `>0`；按每点、RMS、P95、最大值分别给出 |
| `MaxClosureResidual` | `Length` | 未设置 | `>0`；不能以平均误差代替闭环门 |
| `IndependentValidation` | 枚举 | 无默认，按 Purpose/Profile 必填 | `Off/Diagnostic/RequiredForDetection/RequiredForMeasurement` |
| `TileCoreSize` | `uint px` | 无默认，Profile 必填 | 正整数且乘法/字节数不溢出；按算子工作集和峰值内存选值；相邻核心无重叠 |
| `Halo` | `uint px` | 无默认，由采样/滤波支撑推导 | 不小于实际核/插值依赖；预算不足拒绝路线，不截 halo |
| `Lod` | `uint` | 原生分辨率 `0` | 不大于源/目录可表示层级；不能为节省资源临时降低原请求用途 |
| `DisplayBlend` | 枚举 | `None` | 当前实现仅 `None/Stacking`；`Feather/NamedMultiBand` 为未批准方法，请求时返回 `MZ-026 UnsupportedMethod`，不静默换路线 |
| `PhaseAnchor` | `Point2` | 参考 frame 原点 | 由 Profile 冻结；tile 不得重置相位 |
| `MaxConcurrency` | `uint` | `1` | `1..PerformanceProfile.MaxConcurrency`；部署前必须冻结并绑定 CPU/内存/显存资源上限，不以运行时 CPU 数猜测 |
| `DeadlineUtc` | `DateTimeOffset` | 宿主必填 | 绝对 UTC 截止时刻；到期停止新准入并请求取消，不代表 native 已停止 |
| `MotionEvidencePolicy` | 枚举 | 无默认 | `Required/Optional/NoMotion`；移动采集的检测/计量用途只能为 `Required`；静态多相机输入可显式 `NoMotion`，但必须有与设备身份匹配的固定相机共同平面注册资格，不能用空反馈假装静态 |
| `MaxMotionResidual` | `Length/Angle` | 未设置 | 按平移、角度、尺度及 RMS/P95/P99/最大值分别由 Profile 提供；未设置不得开放物理用途 |
| `MaxTimestampSkew` | `TimeSpan` | 未设置 | 触发、曝光、反馈必须在同一 epoch；超限返回 `MZ-024`，不得按采集顺序猜位姿 |
| `SettledRequirement` | 枚举/时间 | 无默认 | `Required` 时必须有设备侧 settled 证据及采样时刻；只提供 sleep 时间不能替代 |
| `RegistrationSpatialModel` | 资产绑定模型版本 | 不允许请求运行时选择 | 注册资产声明全局基准变换、连续误差场类型、支持节点/有效 cell、边界、条件域和插值修订；XY 面阵采用 §5.2A.4 冻结的分量插值路线。请求不得临时更换模型、外推或插值矩阵 |

### 4.2 输入校验

按以下顺序执行，失败项不得被后续步骤覆盖：

1. 检查 request/attempt/revision/用途非空且版本可解析。
2. 检查 FOV、帧 hash、尺寸、stride、通道、方向和租约版本；同 ID 异 hash 拒绝。
3. 检查观察角色相容性；不同面、焦层、曝光或通道不得静默平均。
4. 检查坐标 frame、单位、像素中心/角点约定、校正引用和有效域。
5. 检查 Profile 与实际输入相容，确认预计 FOV 和实际 FOV 缺口政策。
6. 检查资源/整数溢出/输出画布上界；不先规划就分配整张大图。
7. 通过检查后固定源描述/hash/租约代次；只对当前边或 tile 的工作集获取源租约，按预算限制同时持有数量/字节数，用完立即归还。不为整板提前借全体像素；后续无法取得同代内容时返回来源错误，不能读 latest。

计划与实际源均为空时返回 `MZ-019`；非空完整 TilePlan 的全部 Skip 可执行计划诊断：无源租约/native、覆盖为零、`Partial` 且 Detection/Measurement 不可用。Capture 缺帧是 Missing，已有帧且有效像素全为背景是 Blank，二者不得与 Skip 混同。零尺寸帧、越界、重复归还、缺单位、不可逆变换、过期修订、冲突源和超过资源上限都返回明确错误。不存在“尽量拼出一张图”的隐式降级。

取得租约后、调用视觉算子前，再核对实际像素类型/通道/尺寸与 `FrameRef`，以及 ValidMask 的来源帧、修订、内容和有效像素数；同形状的另一帧 mask 不能替用。匹配证据按精确来源读取对应点与支持域，重算残差，不以字段非空、自报 hash 或聚合数字代替验证。缺失/篡改来源拒绝 `MZ-002/003/004`；对应点或独立复核不通过返回 `MZ-007/009`，清理已取得的租约。

## 5. 算法与 HALCON/AsunImage 路线

### 5.1 路线选择

1. **主路线：标定/运动先验**。仅当先验适用域、时间和坐标链明确，且独立验证满足 Profile 时采用；否则只发布原图目录/诊断，不虚构全局位置。
2. **受限备选：pair 匹配 + 全局 bundle adjustment**。前置为同一静态/相容观察层、合法重叠和 `PKG-022` 已验证的 pair 对应。用 `bundle_adjust_mosaic` 优化 Profile 指定的 Transformation，并以留出点/anchor 独立复核。退化、周期歧义、遮挡、预算耗尽或复核失败时，只回到先验路线发布诊断；无先验则失败/Partial。不得自动扩大模型或挑最大分量冒充完整。
3. **备用求解器边界**：HALCON 26.05 页面列有 `bundle_adjust_mosaic` 全局方法；本指导未批准第二个几何求解库或训练模型。公开适配失败时，允许新 attempt 使用有效先验路线或报告 adapter failure，不得静默切到 OpenCV/自写优化器。
4. **合成路线**：生产采用 D.3 固定网格、逆map、nearest 的按需tile；`gen_projective_mosaic/gen_bundle_adjusted_mosaic` 仅用于有界离线诊断且记录官方画布偏移。输出尺寸超预算时不调用全图算子；不存在从生产tile静默切全图或改变几何的备用分支。
5. **显示辐射候选**：当前 A.1 Profile 没有辐射参数，故本版不调用 `adjust_mosaic_images`，也不从 MethodId、资源预算或 UI 设置暗传参数。`standard/gold_standard` 仅保留为研究分支；若未来批准，先增加独立版本的显示请求、完整参数与派生身份再实施。饱和和图内不均匀照明不能由该算子补救。

### 5.2 拼接是否需要标定板，以及高速主备路线

**拼接不一概要求标定板。** 是否需要取决于输出坐标和用途，而不是“拼接”这个名称：

| 场景 | 是否需要标定板/标定资产 | 允许路线与限制 |
|---|---|---|
| 固定高度、近似平面、相机/工件由稳定 XY 运动覆盖，输出只用于大图浏览 | 不强制标定板 | 先用经过验证的运动/编码器坐标先验；显示坐标可为像素或任意局部 frame，明确 `DisplayOnly`。运动误差超出验证范围时不得假称全局几何可靠 |
| 需要跨 FOV 的产品/检测坐标、物理长度或与 CAD/设备坐标对齐 | 需要适用的 FOV 光学资产和 mosaic 拼接注册/运动资格；标定板/标准件用于建立和验证对应映射 | 可由 calibration-assets 的单相机模型、mosaic 的 camera-to-stage/平面注册和运动坐标组成完整链；各边都要有适用域、单位、修订和独立验证。棋盘格不是唯一靶型，按对应 Owner 的兼容路线选型 |
| 无可信运动先验，依赖图像重叠做局部配准 | 不必先有标定板才能形成像素域诊断拼接 | Pair matching + 全局优化只输出共同像素 frame/诊断；不自动给出 mm 或设备坐标。要转物理坐标需另有合格资产 |
| 非平面板、显著高度变化、视差、镜头/工件姿态变化 | 普通平面标定板和 2D 单应性不足 | 拆成分层/3D/受控姿态方案，需相应 3D 资格；不可用更多 2D 控制点掩盖视差 |

大图高速目标按三层执行，不能用“先全图合成再切块”作为生产默认：

1. **冷路径准备**：基于标定/运动先验投影 FOV footprint，只在实际重叠邻接处建立稀疏图和空间索引；避免 N 张图的全组合匹配。独立 anchor/健康检查属于标定、资格或明确的离线诊断，不成为生产每帧识别条件。
2. **热路径定位**：生产固定 `PriorOnly`，不识别圆点/角点，不匹配、不束调整、不做 `DeltaT_visual`。用虚拟 MosaicManifest + 空间索引，按请求区域只读取关联 FOV 和可见 tile；LOD 是 D.3 固定网格取样，不能声称额外滤波金字塔保真。共享解码/map/tile 缓存必须有界、以完整 hash/profile key 索引，latest-wins 仅限显示请求，不能丢弃检测输入。
3. **输出/融合**：几何和原图来源先封存；优先虚拟视图与按需 tile。确需导出时按固定 tile/halo 分块渲染，禁止无预算整图驻留。像素融合和 `adjust_mosaic_images` 属显示支路，默认不进入检测/计量热路径；多带融合不得作为高速或接缝掩盖的捷径。

性能验收必须分别测已知先验、局部匹配、全局优化、首 tile、随机 ROI、整板顺序扫描、冷/热缓存与取消排空；记录 FOV 数、重叠边数、图像尺寸、匹配点、tile/halo、并行度、读取放大率、峰值内存、P50/P95/P99。没有目标硬件 Profile 和真实输入尺寸时只能给测点，不得宣称“高速达标”。先验失败后仅可在新 attempt 使用已批准的图像匹配路线；匹配失败时保留独立分量/Partial/诊断，禁止退化成未标记的平移拼接、按采集顺序排列或单位阵。无标定且用途为物理检测/测量时必须拒绝；无标定但用途为浏览时可显示分离 FOV 或局部像素拼接，并显著保留 `DisplayOnly/Uncalibrated` 标记。

本模块运行时不训练；拼接标定具有独立的拟合/留出和资产生产流程（§5.2C），匹配模型训练仍属于 `PKG-022`。恢复仅能对冻结的输入 hash、Profile、算子/参数和源租约引用创建新 attempt。禁止在原 attempt 改变模型自由度、匹配路线、参考帧或融合算法。

### 5.2A 运动采集下的标定、误差补偿与资格（必选）

畸变校正、拼接几何标定和运动资格是三个不同层次。FOV 光学标定与拼接标定是两个独立的资产生产与资格边界：前者由 `calibration-assets` 只发布单相机成像模型/畸变校正及有效域；后者由本 `mosaic` 模块只发布跨 FOV 的共同 frame、工作区/相机—运动关系及独立误差资格。两类资产须独立建档、修订、资格化、发布和回退，不能合并成一个“标定通过”标志。`calibration-assets` 仅提供精确身份匹配的 FOV 资产和局部观测输入；跨 FOV 全局点号、拼接注册、扫描/运动轴误差及补偿由 mosaic 唯一拥有。本指导不新建第三个模块，也不改变架构登记。宿主按 machine、station、camera、axis group 和采集配置解析两类精确版本资产，并与 `motion-control` 的实际反馈共同组成运行时闭包。畸变校正不能提供 FOV 到共同 frame 的相对位姿，也不能证明载台实际到达命令位置。需要跨 FOV 的物理坐标、毫米量测或 CAD 对齐时，以上三类证据都必须适用。

#### 5.2A.1 标定资产身份和宿主组合

FOV 与拼接资产不得用裸矩阵或“最近可用”解析。`MosaicProfile` 与结果 `VirtualMosaicManifest` 至少记录两类资产的 asset ID、revision、content hash、资格状态、适用域和完整身份键。身份键包括 `MachineId`、`StationId`、`CameraId`、`CameraKind`（AreaScan/LineScan）、相机/镜头与传感器配置、分辨率/ROI/binning、工作距离或扫描配置、`AxisGroupId`、坐标 frame、标定靶修订和运动/触发配置中适用的字段。任何身份字段不一致、资产撤销/过期、资格闭包不完整或适用域外，必须在构图和 native 算法调用前拒绝物理用途；只有请求显式声明时可继续输出分离 FOV 或 `DisplayOnly` 结果。

拼接资格资产由 mosaic 独立持有，必须独立于用于拟合的样本保留留出样本、工作区覆盖、各 FOV 覆盖/重叠、轴方向/尺度、曝光—反馈时序、正反向和重复性、误差分布及未覆盖区域。其内容至少包括：全局基准变换及 frame/方向、每个误差场采样节点与有效 cell、插值方法/修订、各条件子域、测量不确定度和独立留出资格结果。资产声明的坐标路径必须显式给出每个变换的 source/target frame 和方向。多相机或多工位先分别取得 calibration-assets 的 FOV 资产和局部观测，再由 mosaic 建立并验证跨相机关系；宿主只能组合匹配的版本闭包。不同机台、工位、相机、轴组、镜头/采集配置或资格条件不匹配时不得复用模型或资格；但生产 Tile 间距、扫描顺序、ROI 子集和 Capture/Skip 计划本身不改变拼接标定身份，只要相机/运动敏感配置匹配且所有实际位置处于资产有效域。修改一个相机 FOV 资产不自动使其它相机合格，也不自动使 mosaic 拼接资格仍有效。

#### 5.2A.2 运动证据的最小闭包

对每一个参与几何输出的 FOV，适配器必须提供并冻结以下证据：

1. `q_cmd`：宿主下发的目标轴位姿；只用于诊断和先验来源标记。
2. `q_enc`：与曝光关联的实际反馈位姿，带轴 epoch、方向、采样时刻和单位；缺失时不能生成物理坐标先验。
3. `settled`：设备侧到位/稳定证据及其采样时刻、阈值和来源；固定等待时间不是等价证据。
4. 触发、曝光起止、反馈采样的时间戳和同一 epoch 标识；按 Profile 计算 `TimestampSkew`，不以 FOV 序号替代时间关联。
5. 采集时温度、运动方向、速度/加速度摘要和断连/重启 epoch；不能把跨 epoch 的反馈拼成一条轨迹。

模块内部可计算 `q_img`（由有效重叠 Mark/特征反算的图像锚点）和 `q_comp`（将基线注册误差场及适用的附加运动修正按冻结坐标链求值后的补偿位姿），但必须把 `q_cmd`、`q_enc`、`q_img`、`q_comp` 分栏返回。`q_img` 是本次观测修正，不得回写运动模块的实际位置；基线场由 `MosaicRegistrationRef` 提供，附加修正仅来自匹配的 `MotionCompensationRef`，不能在运行中自学习或重复应用同一误差。

#### 5.2A.3 面阵标定靶与资格路线

1. 单 FOV 光学标定先按其独立指导建立并资格化内参/畸变资产。带计量证书的 HALCON 矩形圆点板可走经资格化的 `find_calib_object` 路线；棋盘格只走显式的内角点观测适配与同样本留出对照，不得把“识别出角点”当资格。两条路线分别保存观测和误差，不混成同一拟合集或 artifact。
2. 跨 FOV 拼接标定由 mosaic 另行建立独立的 `MosaicRegistrationProfile/Artifact`。它消费 calibration-assets 提供的单相机/FOV 模型和局部靶标观测，可使用有证书的实心圆点平面板、其它有计量坐标的参考平面，及曝光关联的实际运动反馈；需覆盖工作区中心、边缘、角部、各相机 FOV 和真实重叠关系。不得只覆盖画布中心，也不得把单 FOV 内参当作拼接关系。
3. 拼接标定的拟合集与独立留出集按板位置/采集遍次分开；在留出组上验证正向、反向、重复回到同一点、适用速度和热状态，量化比例、正交/偏摆、回差、settle、触发延迟、编码器量化和温漂。具体阈值由 mosaic 资格 Profile 提供；缺阈值不得发布物理用途资格。
4. 由 mosaic 拼接标定 Owner 独立发布版本化工作区/运动误差地图，写明方向、温度/时间、插值边界、最大修正量和未知区域。地图越域、修订不匹配或方向未知时，模块只能保留显示/诊断结果。
5. 运行时宿主先解析匹配的 FOV 校正资产，mosaic 再解析本模块的拼接关系资产和运动闭包，将已批准变换投影至图索引/tile；生产热路径不计算 `DeltaT_visual`。有界视觉修正只在显式离线 `PairBundle` 诊断请求中研究，不能以低优化 Error 代替独立精度，不能回写生产先验。

#### 5.2A.4 无定位框实心周期圆点板

本路线针对全等、等间距、实心圆点周期阵列且没有 finder/定位框的板。它与 HALCON 标准带找向特征的矩形标定板不是同一种靶标；不得将该板伪装成 `.descr`/标准 `caltab` 输入给 `find_calib_object`，也不得因“找到很多圆”推断全局点号。

1. 参考靶资产固定点阵拓扑（行列数、行列间距/单位、圆直径、排列型式）、唯一物理原点、X/Y 正方向与手性、板面平面度、证书/hash、允许温度和稳定性。操作员在标定会话首帧明确确认原点和两轴方向；若板自身的 180°/镜像/方阵旋转对称仍使方向不唯一，必须补足能唯一确认方向的固定板坐标/安装测量/同步位置或可见锚点证据；编码是可选手段，纯圆点在证据闭包唯一时合法。不得由算法按最近邻、图像上下左右、FOV 顺序或机台命令方向猜身份。
2. 从每个局部视场的可见圆提取候选亚像素中心，并保留阈值/连通域/轮廓/拟合质量、饱和、反光、遮挡和边缘截断证据。局部观测消费 calibration-assets §7.1 的目标专用检测契约：受限分割、连通/形状筛选、亚像素轮廓和物理圆心投影。斜视下椭圆中心不等于物理圆心投影；本模块不复制该算法。局部观测方法/质量 Profile 未冻结时只阻断对应观测适配，显式输入的已验证离线点组和纯 Core 求值不受影响。
3. 先按局部网格拓扑生成多个可能的整数行列赋值，再以已确认原点/方向、同一板的重叠观测、板面坐标和每次曝光的实际 `q_enc` 联合消歧。只有唯一一致的全局赋值才能生成拟合样本；多解、退化或周期别名保留诊断并拒绝发布。严禁用采集顺序或近邻贪心补齐被遮挡的全局编号。
4. 采样计划覆盖工作区和多个 FOV 位置；专门包含视场边缘、部分圆被裁切、遮挡/缺点、低对比/反光、重复位置及往返方向。对每个拟合区 cell 记录有效圆数、索引覆盖、几何条件和曝光—编码器时差；其最低数量/分布门槛来自批准的 Profile，无通用常数。
5. 同一实心点阵可由 calibration-assets 提供局部圆心/靶标观测，由 mosaic 负责跨 FOV 全局点号关联、工作区拟合、运动误差和独立验证；只有独立留出观测、已知物理尺度、运动时空证据和相应用途域误差门均通过，才可输出验证通过的未资格内容。`MeasurementUsable` 还须外部 Owner 授予与该内容/验证绑定的资格，运行时逐次校验。板/采样/校正配置变化生成新资产修订，不覆盖旧证据。

**全工作区连续位置模型（生产基线）：** 拼接注册资产不能是“每个标定 FOV 一张固定矩阵”的列表。标定板在整个采样过程中须固定于工作台/共同参考 frame，板的实测坐标、平面度、安装和温度证据独立于平台误差保存；移动相机/平台按批准计划覆盖有效工作域。每个样本关联曝光时刻的实际 `q_enc`、坐标 frame、轴 epoch、方向、settled 和同步证据；`q_cmd` 只用于运动计划和偏差诊断，不能充当实际位置。

对于 `XY + 面阵相机` 的基线方法，资产冻结为 **全局基准变换 + 二维位置残差场**：先在拟合集上求从实际轴坐标到相机/产品共同 frame 的全局几何基准，再以经证书修正的板点坐标和局部观测建立各采样节点的残差 `ΔX/ΔY`。节点按版本化的工作域网格组织；在通过独立留出资格的有效矩形 cell 内，对每个残差标量分量使用固定的二维双线性插值，然后由插值后的参数重新构造位置 Pose。每条坐标链必须声明 source/target frame 和复合顺序；`MosaicRegistrationRef` 中的基线误差场恰好求值一次，`q_comp` 记录其结果及任何独立、互不重叠的附加运动修正，不能叠加另一张含义相同的误差图。禁止直接对 `3×3` 变换矩阵元素做平均/插值，也禁止在采样点之间选最近一张 FOV 矩阵代用。若 Profile 的独立验证证明还需补偿 `ΔTheta`、尺度或剪切，必须将其作为单独有单位/方向/边界的参数场加入新算法修订；不得自动增加自由度。双线性路线只适用于声明的 XY 面阵模型；线扫使用 §5.2A.6 的行时空模型，旋转轴/机器人等其它机构须有各自冻结并资格化的模型，不得套用 XY 假设。

网格节点是**空间误差采样点**，不是生产 Tile 清单。生产 FOV 的位置和步距可不同于标定采样网格；在资产有效域内任意位置均按绝对 `q_enc` 查询该场，生产路线或曝光序号不参与坐标计算。cell 仅在所需边界节点齐全、输入配置/方向/温度等条件匹配且独立资格覆盖该 cell 时有效；缺节点、孔洞、域外、越界或条件不匹配均拒绝物理用途，不能跨空 cell 插值或外推。若留出残差显示该采样密度不能支撑 cell 内误差界，必须补采/收窄有效域并产生新资产，不能以平滑外观或均值残差放行。

方向相关回差或温漂只有在数据证明可重复时才进入模型：以运动方向、温度/时间等显式条件分离经资格化的子场/配置；未经验证不在子场之间混合插值。多轴顺序、迟滞或线扫时间映射无法由该 XY 场观测时，拆为独立模型并验证完整变换链，不把标定板误差、平台误差和成像误差折叠成一个未解释矩阵。

无定位框周期圆点的全局点号遵循“位置先验只预测、圆点观测再确认”：先由已同步的实际 `q_enc` 和实测板坐标产生有界候选点/行列范围，再检测当前 FOV 圆心、建立局部格点拓扑，并与板的固定坐标、方向/手性、重叠观测和独立身份证据匹配。只有唯一映射可生成拟合样本。不得用 `q_cmd / Pitch` 直接断言点号，也不得因观察顺序连续而消除平移、旋转或镜像歧义；无法唯一确认时拒绝拟合和发布。稀疏编码锚点可用于身份闭包和断帧恢复，不承担圆心几何精度，纯圆点板仅在原点/方向和整个采样连接关系均可证实时才足够。
6. 对于大范围周期点阵，允许采用“密集实心圆点 + 稀疏编码身份锚点”的混合靶。圆点中心用于亚像素几何求解，编码锚点（可为 QR/Data Matrix/其它经验证的二维编码）只用于建立全局原点、行列方向、手性和跨遮挡/断帧的身份闭包；不得用编码边缘或解码成功替代圆心精度。编码不需要覆盖每个圆点，也不应在运行时每帧解码；采集计划必须保证每个连通组件可追溯到身份锚点，并用非共线锚点消除旋转/镜像多解。编码检测失败但圆点身份仍唯一时可继续诊断；身份不唯一时必须拒绝拟合和发布。

**连续求值的唯一数学规则：** 固定同一相机/条件的坐标链：`q=(Xenc,Yenc)` 是轴 frame 中有单位的实际反馈；`G0(q)` 给出共同平面内相机基准原点，`A` 是已注册且资格化的固定二维线性像素/局部平面到共同平面映射。校正像素点 `u` 先按其 FOV 资产、crop 和像素中心约定转换；基线为 `p=G0(q)+d(q)+A*u`。`d=(ΔX,ΔY)` 的定义是“参考实测位置减基准预测位置”，单位为共同平面的长度，不是编码器单位或原始像素。固定相机、移动工件等拓扑须在资产中用各自已冻结的方向/逆链表达，不自动改号。

矩形节点轴严格递增且每轴至少两个有限值；cell `[x0,x1]×[y0,y1]` 的四角均须齐全并属同一条件子场。令 `a=(Xenc-x0)/(x1-x0)`、`b=(Yenc-y0)/(y1-y0)`，每个分量按 `d=(1-a)(1-b)d00+a(1-b)d10+(1-a)b*d01+ab*d11` 求值。拒绝非有限输入、重复节点、非正间隔、四角缺项和非有效 cell；即使某缺角权重为零也不以三个角代替资格 cell。内部网格线用右/上侧 cell，外部最大边用最后一个 cell；选择出的 cell 无资格则拒绝，不绕到相邻有效 cell。有效边界点允许 `a/b=0/1`，域外不 clamp、不外推。返回节点 ID、权重、cell ID、条件 ID、版本、修正前后位置和该 cell 的独立误差界；权重不是置信度，也不能用节点均方误差线性混合充当 cell 资格。

同一方向/温度子场内共享边界节点必须相同，故数值连续；导数不承诺连续。方向是曝光前最后一段非零运动的受证据支持的 X/Y 方向组合及方法声明的迟滞条件。静止/反转后未知接近方向不得默认为正向；仅资产明确“不依赖方向”时可不要求方向。温度区间取半开，最终最大端闭合；重叠区无唯一选择时拒绝，不自动选择最近温度子场。请求输入敏感条件须在该域内，未测温不填零。条件分区与双线性空间插值是两件事，不跨条件子场插值。

**拟合顺序：** 先冻结靶证书/实测点表、共同 frame、FOV 资产、固定映射 A、同步、点号唯一证据及按完整采样遍次分组的 Fit/Holdout。D.4 已冻结从合格Local点、唯一PointId及固定A反算CommonOrigin的方法；不从椭圆中心/裸像素猜物理原点。全局基准在非共线位置组上通过 HALCON `vector_to_hom_mat2d` 的 affine 最小距离路线拟合轴 XY 到原点，至少三对且另检查 Profile 的条件/覆盖；物理 XY 不做像素半格修正。节点残差来自该条件/节点的重复原点观测减 G0，按稳定样本 ID 顺序算分量均值，并保留逐次残差、散布、数量及被拒原因；禁止运行时剔点直到合格。有效 cell 的资格只由未参与拟合/调参的内部、边界和往返留出组建立。拟合点数、散布、条件数、覆盖和 cell 误差上限全来自冻结 Profile；缺门限可保留候选，不产生资格。该路线不另引优化库，也不声称已运行 HALCON。

#### 5.2A.4A 30×20 mm FOV、500×500 mm 工作区的尺寸化起始 Profile

本节仅保留用户尺寸示例的选型推导，不构成默认 Profile、采购规格或验收指标；最终值必须绑定像素分辨率、运动误差、安装边界、温度域和用途 Profile。

标题中的尺寸和“起始 Profile”均为历史算例标识，不是一个已冻结或待自动采用的生产 Profile；所有数字都只用于说明推导，不能以本标题恢复示例采购参数。

1. 拼接靶有效图案必须覆盖实际采样计划的成像 footprint 并加安装/误差余量，取各 footprint 并集的包围范围。仅当 `500×500 mm` 指 FOV 中心移动包络时，才推导 `W >= 500+30+2M_x`、`H >= 500+20+2M_y`（mm）；若它指已成像工件区域，则不能再加一遍 FOV。约 `550×550 mm` 图案/`560×560 mm` 基板只是该前提下的候选示例；扫描包络和余量未经机械证据确认不得采购定版。
2. `1.5–2.5 mm` 间距、`2.0 mm`、圆直径为间距的 `0.3–0.5` 倍均仅为选型算例，不是推荐默认或采购范围。例中 30×20 mm 视场、2.0 mm 间距约对应 15×10 个圆心，550 mm 图案约对应 275×275 个点；实际可见点数受边界、遮挡和投影影响，这些数量不能证明支持充分。点距/点径须按真实 footprint、像素分辨率、曝光/景深、局部观测质量、全域证书和独立重复性验证写入真实 Profile，不由算例冻结。
3. 基板应是低热膨胀、长期稳定、可给出全域平面度和点心坐标证书的陶瓷、微晶玻璃、石英或 Invar 等方案；普通打印纸、铝板或未验证的大玻璃不能作为 500 mm 级计量靶。图案需低反光、高对比、圆度和点距可追溯，并记录温度、材料、板面坐标系、原点和手性。
4. 纯均匀圆点板只有在 `q_enc`、初始原点/方向和连续重叠路径均已资格化时才可用于物理拼接；它不能自行消除平移周期、180°/镜像和方阵旋转歧义。纯圆点路线已满足唯一身份证据时不要求额外编码；需改善断帧恢复时可评估上述混合靶：在四角、中心及采样路径的适当间隔布置少量唯一编码锚点，间距由“断帧/遮挡后仍能回到唯一身份”的 Profile 决定，不把二维码密度当作精度指标。
5. 这块大靶用于跨 FOV/运动拼接标定，不替代 `calibration-assets` 的单 FOV 内参/畸变靶。运行时不放置标定板；发布的拼接资产只消费已资格化的 FOV 光学资产、编码器反馈和运动补偿闭包。二维码/编码仅在建标定或身份恢复路径使用，不能把解码结果直接当作最终像素到毫米变换。

#### 5.2A.4B 现有产品、HALCON资源与采购结论（2026-10-06核查）

1. 本机 HALCON 26.05 参考页 [`gen_caltab`](../../../halcon算子手册/operators/gen_caltab.html) 明确支持矩形等间距圆点标定板，描述文件包含行列、点距、点径、板面坐标和三角形找向标记；[`create_caltab`](../../../halcon算子手册/operators/create_caltab.html) 支持带 finder pattern 的六边形圆点板。参考资源列出了 `caltab_800mm.descr`、`calplate_1200mm.cpd` 等大尺寸描述文件。这证明 HALCON 的圆点标定板模型可以覆盖本项目的 500 mm 工作区，但不证明某个文件对应的实体板已在现场校准，也不把无定位框点阵自动变成标准 `find_caltab` 输入。
2. [Geodetic Systems Targets](https://www.geodetic.com/targets) 的公开目录列出 3/6/12 mm 编码靶、单圆点靶、条带靶和 custom-made targets；其 [Strip Tape](https://www.geodetic.com/strip-tape/) 页面列出 2 mm 圆点、5 mm 点距以及多种更大点径/点距组合。这类产品适合作为身份/摄影测量靶标来源，不能直接当作本项目 550 mm 刚性计量板，除非供应商另行提供基板平面度、全域点心坐标、热稳定性和安装重复性证书。
3. [Max Levy/Attalon Custom Patterned 2D Optics](https://www.maxlevy.com/pages/custom-patterned-2d-optics) 明确提供 high precision grid and dot arrays、machine vision scales，并声明基板尺寸范围可达 3000 mm × 2000 mm，支持玻璃、陶瓷等基板。这证明 550～600 mm 级低热膨胀圆点阵列板具备定制加工路径；网页没有证明其现成产品包含二维码，也没有替代本项目的计量验收。
4. [Applied Image 的机器视觉标准件目录](https://www.appliedimage.com/product-category/robotic-machine-vision-standards/) 和 [定制测试靶页面](https://www.appliedimage.com/custom-designs/custom-test-targets-charts/) 证明点阵、畸变靶、网格板和定制靶可采购/定制；本次核查未确认一个公开型号同时满足“550 mm 级、密集圆点、唯一二维编码、全域计量证书”四项条件。
5. 采购路径结论仅为：**圆点阵列板和身份编码靶存在采购/定制来源；需要集成混合计量板时按定制件及全域实测证书管理**，不冻结具体尺寸、间距、点径或锚点密度。有效图案/基板尺寸由实际扫描 footprint 并集、机械安装/误差/温度域与重量/平面度约束确定；点距/点径由像素分辨率、投影和观测质量 Profile 确定；是否需要编码及锚点位置/密度由原点/方向唯一性和断帧恢复 Profile 确定。纯圆点证据闭包唯一时无需混合靶。整体板或分块方案按真实加工/运输/安装证据选择，分块拼装关系须独立测量入证书，不能以机械边缘推断几何连续。§4A及供应商目录的全部数值都只是算例或目录事实，不成为本项目采购指标。
6. 二维码、Data Matrix、AprilTag、ArUco 或摄影测量专用 coded target 的职责都是身份、方向、原点和断帧恢复；它们不承担最终亚像素几何。二维码密集板常用于多相机/摄影测量的全局点号与姿态识别，并非“二维码越多精度越高”。本模块只在建立标定资产或身份恢复路径解码，并以圆心观测、运动反馈和留出验证决定 `MeasurementUsable`；不得把解码成功率当拼接精度指标。

#### 5.2A.5 棋盘格兼容与交叉验证

棋盘格是独立的兼容观测路线：只将明确的内角点坐标、物理格距、角点身份、原点/行列方向和观测方法版本交给相应标定能力；不得送入仅接受 HALCON 标准圆点靶的 `find_calib_object` 路线。若用棋盘格交叉验证圆点板，必须使用同一坐标 frame、匹配的采集域和未参与拟合的物理检查点，分别产生两份独立结果，再比较全域误差、最大区域误差和不确定度。结果不得合并拟合、平均参数、共享资格状态或用一种靶标的通过抵消另一种失败。未完成适用域内对照时，棋盘格只可作为诊断，不得扩展圆点板资产的有效域。

#### 5.2A.6 线扫时空标定

线扫相机每一行（或设备给出的每个线曝光单元）都对应时间区间和运动位置，不得套用面阵静态 FOV 内参/单应性资产充当完整拼接模型。calibration-assets 只提供经其相机模型验证的线扫局部成像参数和行观测输入；mosaic 的独立拼接标定资产必须声明线触发/编码器时钟关系、行时间戳语义、扫描方向、行频、速度/加速度适用域、曝光/触发延迟、编码器插值方法、空间尺度和扫描轴/横向轴 frame；保存同步来源及独立留出误差。

线扫采样需覆盖批准速度范围、正反扫描、启停/加减速边界、时钟偏移/抖动、丢行或重复行挑战，并使用带已知二维几何/长度的平面靶或适用标准件验证行时序到空间位置映射。出现时间戳缺失、时钟 epoch 不同、反馈无法插值、速度越域、方向未知或丢行导致索引不唯一时，拒绝物理坐标资格；只允许保留原始线帧/诊断显示。线扫模型与面阵模型分别版本化，不能互相转换或借用畸变修正结果来掩盖时序误差。具体 HALCON 能力和参数仅按本地 26.05 参考与目标公共签名核对，不预设某个 area-scan operator 可处理线扫时序。

HALCON 26.05 的 [`camera_calibration`](../../../halcon算子手册/operators/camera_calibration.html)、[`calibrate_cameras`](../../../halcon算子手册/operators/calibrate_cameras.html)、[`find_calib_object`](../../../halcon算子手册/operators/find_calib_object.html)、[`image_points_to_world_plane`](../../../halcon算子手册/operators/image_points_to_world_plane.html) 和 [`image_to_world_plane`](../../../halcon算子手册/operators/image_to_world_plane.html) 页面用于核对其各自相机参数、标定数据、标准靶观测和平面投影语义。它们不替代线扫时序/轴同步资格，也不证明无 finder 周期圆点板可走标准 caltab 检测。调用仍只经 `ImageLibDotNet.cv2` 公共边界；本次指导不冻结未核实的 C# 重载或点检测算子。

共同 frame 的运行时变换由一次求值的注册模型产生：

```text
P(q_enc, conditions) = G0(q_enc) + d(q_enc, conditions)
T_prior = Translation(P) * RegisteredLocalToCommon * RectifiedPixelChain
T_final = DeltaT_visual(common <- common) * T_prior  (offline PairBundle diagnostic only; production PriorOnly uses T_final=T_prior)
```

`RectifiedPixelChain` 只做原帧/crop/光学校正到声明局部坐标；`RegisteredLocalToCommon` 只含固定注册关系，不再次包含 `G0/d`。首版只支持基线中的 G0/d，不支持基线之外的几何附加补偿：所有运行请求的 Compensation 必须 null，非 null 返回 MZ-026。保留 MotionCompensationRef 仅为识别并拒绝历史候选输入，不提供求值器/插件函数。方向回差和温度条件仅由基线的独立子场表达，不再叠加一次。禁止把 `q_comp` 再送回以 `q_enc` 为域的基线模型。`q_comp` 是公共 frame 的派生位置并保留 frame/unit，不能冒充轴反馈。视觉修正是共同 frame 左乘的有限修正，记录 source/target 和独立支持；没有视觉修正时明确 `NotApplied`，不伪造观测。先验、视觉、重采样、非平面和附加补偿分别记账。

**逐行时空规则：** 行证据保留原始稳定行 ID、曝光起止、曝光关联时刻定义和时钟映射修订；按资产固定为曝光中点（附录 C 首版）固定，不能由调用者临时换定义。同 epoch 编码器样本时间严格递增，行时刻只在相邻两个实际反馈时刻之间线性插值；超过 Profile 最大间隔、同步不确定度、速度/加速度域或曝光运动模糊界即拒绝该物理用途。重复时间不同位置、跨 epoch、逆向/回差条件不明和缺包不插值。缺行保留空间空洞，重复行只有 ID/hash/时序全相同才去重，不压缩行号/重算均匀步距。加减速仅在经留出验证的时空资产域内合法，不能用平均速度代替逐行反馈。线扫首版方法、前向/反算、增量 DTO、装配及逐片门固定于附录 C；v0.3 的 LineScanTimed 入口继续拒绝物理求值，不静默改变已接收的面阵 Core。

#### 5.2A.7 允许补偿与拒绝边界

| 可观测误差 | 允许补偿 | 立即拒绝或降级 |
|---|---|---|
| 稳定比例、偏置、轴间正交/偏摆 | 使用实际 `q_enc` 或版本化误差地图 | 位置/温度/方向越出地图，或修订不匹配 |
| 可重复正反向回差 | 按方向分开的地图并要求方向证据 | 方向未知、滞回不稳定、重复性超限 |
| 固定触发/曝光延迟 | 经资格化的时间偏移模型 | epoch 不同、延迟漂移、曝光与 settled 无关联 |
| 足够重叠且稳定的 Mark/纹理 | 显式离线 PairBundle 诊断的有界 `DeltaT_visual`；生产仍 PriorOnly | 周期歧义、支持退化、视觉与运动冲突超限；不热修生产变换 |
| 已验证低频热漂移 | 温度/时间分段模型 | 温度越域、随机漂移或未独立验证 |
| 随机振动、结构弹性、显著 Z 高差、板弯和视差 | 转入 3D/受控姿态专用路线 | 2D 平面模型不能解释时，禁止用更高自由度 2D 补偿 |

补偿只减少已测量且可重复的误差，不能把不可观测的运动伪装成高精度。拼接模块不发运动命令、不修改运动事实；`motion-control` 拥有实际位姿，`calibration-assets` 拥有单相机/FOV 光学资产，`mosaic` 拥有跨 FOV 拼接/运动误差资产并只在运行时消费自身及上游带修订和适用域的公开端口。

#### 5.2B 已资格标定资产的运行时消费

FOV 光学资产与局部靶标观测由 `calibration-assets` 的 FOV 能力提供；其职责边界见 [`calibration-assets` §7.2A FOV 局部几何与拼接责任边界](../calibration-assets/DEVELOPMENT-GUIDE.md#72a-fov-局部几何与拼接责任边界)。周期圆点板的跨 FOV 全局点号关联、工作区拟合、独立往返留出、运动误差和位置 cell 补采由 mosaic 自身的拼接标定流程负责。本模块运行时不重复识别圆点、不训练标定模型、不建立或修正 FOV 光学校正资产，也不把 `find_calib_object`、全图角点、NCC 或特征拼接作为缺失拼接资格资产的替代。

物理用途的每个**已采集** FOV 在进入几何构图前，必须解析精确匹配且已批准的 calibration-assets 单相机成像资产、本 mosaic 连续拼接注册资产和有效域，以及曝光关联实际 `q_enc` 与运动闭包；各自来源、版本和有效域进入结果 manifest。位置变换由 mosaic 拼接资产的全局基准和位置残差场求值，运动端口提供实际反馈，拼接模块再将批准的绝对 `ProductFrame` 变换投影到图索引与 tile。多相机结果逐相机保留 FOV 光学资产，并保留共享拼接关系及其相机组/轴组适用域；不把一个相机的矩阵复制给另一相机。禁止以相邻 FOV 的点阵外观、图像纹理、采集顺序、命令位置或相对步长补出缺失编号/变换。

计划中每个 Tile 的 Pose 身份与图像采集状态分离。宿主在采集前提交完整 TilePlan；mosaic 对每个轴 frame 中的计划输入位置（`EstimatedEncoderInput`，仅预测）查询拼接资产并返回独立的 `PlannedPose`、稳定 `TileId` 和有效域状态，扫描路径只规定执行顺序。若意图为 `Skip`，仍保留该 Tile 的行列/绝对位置/计划 Pose，不建立伪造的 FrameRef、曝光或实际反馈；它在覆盖结果中保持未采集空洞。若意图为 `Capture`，实际图像须以 FrameRef 和曝光关联 `q_enc` 匹配回原 TileId，返回 `ObservedFramePose`；偏离计划位姿时按实际反馈重新求值，并报告差异，不能按“第几张图”移位。非连续扫描、ROI 子集、倒序/蛇形路线和改变生产步距都按绝对位置关联；身份缺失或位置越域则拒绝相应物理用途，绝不压缩跳过项或用邻 tile 补洞。

计划的产品坐标目标不可直接送入以编码器 XY 为域的误差场。宿主须提供有来源的 `EstimatedEncoderInput` 与计划方向/条件，或精确版本的产品目标到轴计划坐标路径；后者也只产生预测。缺映射或方向不唯一时该 Tile 的 `PlannedPose=null`、状态为 `PredictionUnavailable`，保留 Tile 身份和原因，不阻断其它实际反馈完备的采集项。计划求值即使在有效 cell 内也只为 `Predicted`，不能成为 Observed/已到位/覆盖/物理用途证据。实际反馈越域时不套用计划合格结果。

圆点板、Mark 或产品纹理对运行时几何不是必需输入；某 FOV 没有可识别圆点或产品特征时，只要 mosaic 批准的拼接变换和运动闭包有效，仍按该 FOV 的来源 frame 生成 tile。反之，实际位置越域、mosaic 拼接误差地图或注册资产不适用、反馈缺失或不同步时，返回覆盖/资格错误并阻断依赖物理坐标的用途；仅在请求明确允许时保留 `DisplayOnly` 或分离原 FOV 诊断。未采集区域继续表示为空洞，不能用邻格变换、图像插值或接缝融合伪造覆盖。

位置/FOV 复用分别只消费 calibration-assets 已批准的单相机成像模型和 mosaic 已批准的连续拼接空间模型，按下表验证来源。不能将位置当作某个已采集 FOV 的矩阵 ID；资产在其验证有效域内按绝对位置评估，域外/无效 cell 不插值、不外推：

| 变化 | 本模块处理 | 必须保留的证据/拒绝条件 |
|---|---|---|
| 仅显示裁剪/导航窗口变化，采集配置不变 | 复用原 source transform，重建派生 tile/overlay | 保留原帧、有效域和变换修订；不能将显示缩放回写几何 |
| 采集 ROI 是同一成像配置下原帧的严格子窗口 | 通过坐标端口组合 crop origin 后派生变换 | 保存 crop origin/size，重新验证有效域、重叠和用途；缺 offset 拒绝 `MZ-004` |
| 分辨率、binning、像元尺寸、镜头/焦距、相机姿态或采集尺寸变化 | 分别解析对应的新 calibration-assets FOV 校正资产和 mosaic 拼接注册资产 | 任一没有适用资产时 `MZ-004`，不能只按宽高比缩放旧矩阵 |
| 命令步长/采集覆盖/扫描顺序改变 | 每个计划 Tile 按绝对目标位置求 `PlannedPose`；已采集 FOV 按曝光关联的实际 `q_enc` 求 `ObservedFramePose` | 标定采样网格和生产 Tile 网格无需一一对应；同相对步长不证明绝对位置相同，越域/无效 cell 不套邻格、不外推 |
| 仅曝光/照明/增益变化，几何链与运动模糊资格仍有效 | 几何可按原资格复用；显示辐射重新验证 | 不复用旧辐射派生/回执；光学、有效域或模糊条件变化仍须重新资格化 |

#### 5.2C 无 UI 拼接标定与资产生命周期

该能力不下发移动/拍照命令。宿主组织采样，模块消费冻结的组观测、实际反馈与局部光学资产，通过附录 A 的 `SolveCalibrationAsync -> ValidateCalibrationAsync -> PublishCalibrationAsync` 生产未资格内容。每一步由宿主显式调用；没有“拟合成功即发布/激活”。

1. 输入 `MosaicCalibrationRequest` 固定 OperationId/内容摘要、靶实测点表、板安装/原点/方向、相机和轴组身份、双资产依赖、方法、网格/条件分区、完整 Fit/Holdout 组和参数/预算。`PhysicalGroupId` 按采样遍次/安装/位置组织，同一组全部观测只能在同一分区；点号映射非唯一、相同曝光重复或反馈关联冲突在 native 前拒绝。
2. 求解只读取 Fit 组，按 §5.2A.4 的固定原点观测/基准/节点路线，输出 CandidateReady 或含拒绝原因的结果。拟合输出是候选，不含 Qualified/MeasurementUsable。缺 A/反算方法、局部观测或必要 Profile 时拒绝受影响路线，不让程序员选择模型自由度。
3. 验证使用预先固定的 Holdout 组与独立点/标准件，检查各条件 cell、共同相机关系、方向、同步、覆盖、最坏误差和用途界；有效域是逐 cell/条件结果，不能从边角通过推整域。验证结果只记录 evidence，不写候选内容或扩大域。更改网格、条件、拟合集或阈值生成新候选/hash 和验证操作。
4. 发布只接受完全匹配候选 hash/验证 hash 且未过期的闭包，通过显式 `IMosaicAssetPort` 原子发布不可变未资格内容。存储同发布 ID/同 hash 返回原回执；不同 hash 拒绝。断连/回执未知返回 `MZ-029`，保留原操作供 `QueryAssetPublishAsync` 回查，不自动重试写入或假称失败可重发。
5. 外部资格 Owner 决定允许用途/有效域并绑定资格修订；运行时 `ResolveAsync` 读取精确内容与资格，模块再核验，资格必须绑定该 hash 和验证证据。激活/撤销/回退由宿主显式治理，Core 不签发资格或操作设备。旧内容保留；新 FOV 光学修订、机械安装/时钟敏感配置变化需新闭包，不能就地改旧场。
6. Solve/Validate 的 native、租约和取消/排空与运行时同序；Publish 的外部提交可能在取消前已发生，取消后只能查询原回执，不宣布撤销不可变内容。提交未知与 native 排空未知分别记录；均不自动激活。未使用标定适配时 `CalibrationAdapter=null`，具名求解/验证入口返回 UnsupportedMethod，不影响纯 Core 计划/运行时消费。

该流程的内容 Owner 是 mosaic，存储端口仅负责内容/回执 IO；资格和机台动作是不同的权限边界，不由资产 Owner 隐式获得。

目标 HALCON 为 26.05；下表以项目内 26.05 Operator Reference 为算子语义依据。AsunImage 为薄封装，全部算子经 `ImageLibDotNet.cv2` 调用，不另接 `HOperatorSet`/`halcondotnet.dll`，不再检查封装是否包含算子。仅 C# 类型/重载或封送确有歧义时查公共签名或在消费工程编译确认，不检查内部：

| 目的 | 候选能力 | 必须保留的限制 |
|---|---|---|
| 成对匹配 | [`proj_match_points_ransac`](../../../halcon算子手册/operators/proj_match_points_ransac.html) | 从两图点集估计投影关系；由 `PKG-022` adapter 经 `cv2` 交付已验证 pair 对应。周期纹理/遮挡/弱纹理的歧义拒识，不只取 top-1 |
| 全局几何 | [`bundle_adjust_mosaic`](../../../halcon算子手册/operators/bundle_adjust_mosaic.html) | 输入 pair 索引/变换、对应点坐标和各 pair 对应数，输出每图矩阵、重建点和 Error；索引从 1 起。Error 是优化量，不是独立精度或协方差 |
| 已知变换合成 | [`gen_projective_mosaic`](../../../halcon算子手册/operators/gen_projective_mosaic.html) | 不负责匹配/求解；StartImage 定义参考平面，自动选输出原点，StackingOrder 决定覆盖次序；`TransformDomain=false` 忽略输入域；必须应用返回每图矩阵 |
| 已求解变换合成 | [`gen_bundle_adjusted_mosaic`](../../../halcon算子手册/operators/gen_bundle_adjusted_mosaic.html) | 只消费每图公共平面矩阵，不执行调整；自动选画布并返回 `TransMat2D`，必须回接画布坐标 |
| 辐射补偿（未来候选） | [`adjust_mosaic_images`](../../../halcon算子手册/operators/adjust_mosaic_images.html) | 仅记录HALCON限制，不是本版可执行入口；未来合同须先冻结byte输入/参数/派生身份。参考图保持不变，饱和不校正，图内不均匀照明不适用；gold_standard可能较慢 |
| 仿射重采样 | [`affine_trans_image_size`](../../../halcon算子手册/operators/affine_trans_image_size.html) | row/column、目标尺寸和裁切语义按 `PKG-007` 桥接，不推广至其它算子 |

上述辐射算子仅为未来方法依据，本版没有可执行辐射参数合同，禁止调用。未来切片须校验实际 byte 类型，不隐式截断 `uint2/int2/real`；算子只返回校正图，不返回 gain/offset/response/vignetting 系数，不伪造这些值。参数、独立显示派生身份、失败回退、量化验证和预算必须在新显示合同中闭合；不能让当前程序员补猜。

HALCON 页面将这些 mosaic/adjust 算子标为可从任意线程调用但不内部并行；这不证明共享 handle 可并发或有界可取消，实例默认串行，外层并发由 Profile 约束。算子语义核对不是调用、真实适配或性能验收。

Core 只消费抽象的 `IRegistrationAdapter`。Adapter 可在适配层持有 native 对象，必须把创建、使用、取消、排空和释放写入诊断；不得把原生对象塞入 DTO、缓存或 UI。

### 5.3 几何不变量

- 采用列向量候选约定 `p=(column,row,1)`；`H(j<-i)` 表示 i 到 j；实际公共合同冻结后不得在调用处变换方向。
- `G(i)=G(j)*H(j<-i)`；逆边显式求逆并独立检查有效域，不能转置或只改平移符号。
- crop/resize 先回到原帧再估计；中心对齐缩放采用 `x=x0+s*(u+0.5)-0.5`，若实际算子不同必须用 `PKG-007` 的精确映射。
- 相邻采集序号不是空间邻接；只有物理重叠证据或批准的独立 anchor 才能建边。
- 视觉图未连通不等于坐标未连通：各帧已有同一共同 frame 的独立合格绝对先验时，可同目录定位而无需纹理边；保留视觉组件和覆盖空洞。缺少共同先验的分量分别输出，不拼凑完整图。1 帧只建索引/适用先验，不调用至少两帧的全局求解。
- covariance 未实际计算时返回 `NotProvided`，不填零。
- 从同一不可变对应点 payload 重算 RMS/P95/max，并记录单位及 Profile 规定的分位算法；三者有限且非负，各自检查上限。长尾允许 RMS 大于 P95，不强制二者排序；max 必须不小于二者，优化 Error 不得替代这些观测量。

### 5.4 显示接缝和多带

本指导当前可实现的显示基线是原 FOV/虚拟 tile 与已知几何的有界合成；全图合成仅限准入估算通过的尺寸，overlap 用显式 stacking/稳定来源顺序，不做像素交叉融合。必须返回原值来源、有效域和覆盖次序。平滑、无可见接缝或单一来源标签都不能证明缺陷保持、覆盖或计量资格。

`DEV-VIS-029 §11.3–11.8` 的支持归一多带是方法候选，不是当前已验证 HALCON/AsunImage 能力；项目已核算子页未冻结该方法的生产适配与资格。第一实现不得自行声称支持多带/最优接缝/缺陷保持。若后续按已批准方法接入，必须固定全局标签/4 邻接分量、相位、核/层数/halo、保护域和累计资源；tile 不得重算标签或跳过扩展区源。没有逐值/来源/支持和最小缺陷对照前，该路线仅限显示研究，检测/计量请求拒绝 `MZ-017 UnsupportedPurpose`。

## 6. 无 UI API 与调用示例

以下示例表达唯一构造/API 形状和所有权。它是模块指导中的 Core 候选契约，不替代逐切片准入，也不冻结平台 Schema。

```csharp
await using IMosaicService module = MosaicModule.Create(new MosaicModuleOptions(
    sessionEpoch, framePort, coordinatePort, imageLibAdapter, assetPort,
    calibrationAdapter, diagnostics, clock, limits, progressSink));

// input 是宿主按附录 A 组装、冻结并保存的 MosaicRequestInput：
// PlanningSnapshot 来自宿主预解析的 exact artifact+qualification 或已保存的离线值；
// 同时包含逐帧 optical 引用、Expected/Actual/TilePlan、实际反馈、网格、用途、预算和 deadline。
MosaicRequest request = MosaicRequest.Create(input);

MosaicCallReply<MosaicResult> reply = await module.ExecuteAsync(request, cancellationToken);
if (reply.Observation == ObservationStatus.Returned && reply.Result is MosaicResult result
    && result.ExecutionStatus is ExecutionStatus.Completed or ExecutionStatus.Partial)
{
    foreach (var component in result.Components)
        logger.Record(component.Id, component.Status, component.Validation?.Bounds.Maximum);
}
```

宿主必须先保存输入引用和已预解析快照，再决定是否保存派生目录。只有 reply.Observation=Returned 且账本已确认内部归还，或 Query 已确认原操作排空后，才可释放宿主需保留至计算退出的引用；PendingDrain/WaitCancelled 的观察返回不代表 native 停止。取消只通过该次调用的令牌传入。结果必须通过 PurposeEligibility 判断，不以 Completed 推导检测或质量结论；没有 Result 时查询原 OperationId，不能重发同一 tile 或为未排空操作启动替代。

纯查询/取 tile 使用只读目录接口，不触发采集、不修改工程、不重新执行算法。查询找不到历史目录返回 `NotFound`，不自动查 latest 或重算。

## 7. 异步调用、进度与并发

### 7.1 唯一服务接口和取消

- 对外只有一个 `IMosaicService` 实例/入口；创建时显式注入 Frame、Coordinate、Registration 和 Diagnostics 端口。不得另建 `IMosaicBuilder`、第二个工厂或运行时执行别名。标定候选/验证/内容发布使用附录 A 的具名方法，与运行时执行分开。
- `Validate(request)`：纯校验，不能取得 native 句柄或持久化。
- `Plan(request)`：只读 RequestInput.PlanningSnapshot 的不可变字段与资格消费快照，做有界计划/资源估算；不借帧、不调用异步端口、不持有native。缺少必须快照的同步返回见 A.1，不能同步等待 ResolveAsync。
- `ExecuteAsync(request, cancellationToken)`：唯一运行时入口，返回 `MosaicCallReply<MosaicResult>`。在有限观察内排空完成才 Result 非空；未排空则 PendingDrain/WaitCancelled、Result=null，原操作仍可 Query/Drain，详见 §9.2。不提供同步 Execute 或 BuildAsync。
- 执行开始先检查令牌；若已取消，返回该 `OperationId` 的 `Cancelled` 结果且不进入输入校验/取租约。未取消时按校验、接纳顺序继续。
- `QueryAsync(operationId, cancellationToken)`：只读查询本服务实例已接纳操作的状态/终态，不启动重算；已接纳操作的终态在显式保留窗口内可查，超过窗口返回 `Expired`；只淘汰已清理的终态，容量满且不能淘汰时拒绝新准入 `MZ-010`，不存在或未接纳返回 `NotFound`，不查 latest。跨进程持久化由宿主/原 Owner 负责。
- `GetTileAsync(MosaicTileRequest, cancellationToken)`：只读派生查询，要求目录修订、用途和权限一致。
- `DrainAsync(deadlineUtc, cancellationToken)`：阻止新准入并等待本实例已接纳请求完成清理；该方法的令牌只取消调用方等待，不取消在途请求，也不得伪称 native 已停止或释放资源。
- `MosaicRequest` 不含 `CancellationToken`。取消令牌只属于调用者对一次执行的控制，不序列化、不复用到重试；新 attempt 使用新调用令牌。
- 取消是原操作结果语义：接纳前已取消可返回 Returned/Cancelled；接纳后取消先停止新工作，排空/内部归还后业务终态才为 Cancelled。调用等待可先返回 WaitCancelled（不是 Cancelled 业务结果），不得提前释放仍被端口/native占用的内存或租约。GetTile 只有 §9.2 的原子交付成功才转移输出租约。

### 7.2 进度投递和事件顺序

进度唯一通过构造选项中的可选 `IMosaicProgressSink` 端口投递；每条记录携带 `RequestId`、`AttemptId`、`Revision`、阶段、已处理/计划数量和单次执行内单调递增的 `Sequence`。无端口（`null`）或无订阅者时，计算照常进行，返回结果和 `QueryAsync` 仍可靠给出终态。顺序固定：

```text
RequestReceived
  -> InputValidated -> RequestAccepted
 -> PlanReady
 -> SourcesLeased
 -> GraphReady
 -> RegistrationStarted/Progress/Completed
 -> ValidationStarted/Completed
 -> GeometryStaged
 -> DisplayStarted/Progress/Completed (可选)
 -> (可选) ResultStaged
 -> ExecutionDraining
 -> ExecutionDrained
 -> ResourcesReleased
  -> RequestCompleted | RequestPartial | RequestCancelled | RequestTimedOut | RequestFailed | RequestUnknown
```

上述主序列适用于未在入口处取消且输入校验通过的请求；入口已取消时为 `RequestReceived -> RequestCancelled`，校验拒绝时为 `RequestReceived -> RequestRejected`。

SourcesLeased 是按工作集可重复的进度，不表示全部源同时持有。纯计划/全部 Skip 分支不发借用/native/显示阶段，只发其真实经过阶段。标定使用相同接纳/排空骨架，运行阶段分别为 CalibrationSolve/CalibrationValidate/ContentPublish，不伪造 runtime graph/tile。

通知实现必须使用有界队列和独立于算法/native 执行的派发工作者；生产线程只做有界、非等待式入队。队列满时允许合并同一请求/阶段的中间进度或丢弃旧进度，并递增可观测的丢弃计数。慢订阅者不得阻塞算法、native drain、资源释放或执行返回；不得为每条通知创建无界任务。订阅回调串行调用，抛出的异常隔离为诊断 `ProgressDeliveryFailed`，不能改变执行状态、取消状态、结果或租约所有权。若派发者永久阻塞或服务正在释放，待发进度和终态通知都可被丢弃；不以同步等待订阅者换取通知完整性。

业务 deadline/取消到达但 native/port/dispose 未排空时为 Draining/DrainUnknown，不先报告终态。仅观察时限先到而业务仍合法时，原操作可保持 Running；public 返回PendingDrain不改变业务结果，GetTile例外关闭交付门并请求停止。所有实际清理完成后才发 ExecutionDrained/ResourcesReleased 和唯一业务终态；已交付输出的Tile保持OutputHeld直至归还，不套runtime的无输出租约终态序列。接纳后CancelRequested只尽力通知；接纳前取消可Returned/Cancelled并仅RequestReceived→RequestCancelled，校验拒绝仅RequestReceived→RequestRejected。最终Cancelled从Returned.Result或Query读取，WaitCancelled/PendingDrain不是Cancelled结果。

事件是进度投影，不是事实写入；进度总数未知时使用 `null`，禁止编造百分比。消费者按 `(RequestId, AttemptId, Revision, Sequence)` 去重；revision 不同、序号不递增或已经观察到终态的迟到通知必须忽略并可记录诊断。`GeometryStaged` 仅表示内部候选就绪，不暴露可消费目录或取得耐久资格。撤权/修订/取消检查和真实清理完成后才返回成功结果。进度投递不承担 exactly-once 或终态持久化保证；`ExecuteAsync` 返回结果及服务实例显式保留窗口内的 `QueryAsync` 是终态权威，实例释放后状态留存/恢复由宿主/原 Owner 负责。

### 7.3 并发和实例隔离

同一实例内的 native handle 默认互斥；`reentrant` 算子不等于同一个句柄可共享。不同请求可并行，但每请求拥有独立租约、预算、诊断和取消域。禁止静态缓存当前板、当前 FOV、当前语言或当前结果。

## 8. 状态、错误码与恢复

### 8.1 状态

状态是请求生命周期，不是质量状态：

`Created -> Validating -> Planned -> Running -> Publishing -> Draining -> Drained -> ResourcesReleased -> Completed | Partial | Cancelled | TimedOut | Failed | Unknown`。

上式是运行时/标定无外借输出的业务顺序，Core ExecutionState.Terminal与ExecutionStatus中的六种业务结果分离。等待观察回执不是ExecutionState；DrainUnknown可在Draining中投影，Tile交付成功之后转OutputHeld而非Terminal，归还后Drained→ResourcesReleased→Terminal。内容发布Unknown只表示外部回执未知，IO真实退出后可记录Unknown结果，后续按原PublishId查询不会抹掉曾未知的观察事实。

- `Partial`：明确返回部分几何/诊断结果和缺口；不得消费为完整检测/计量。
- `Cancelled`：取消已请求、所有 native 已退出、暂存派生已撤销且租约已归还。宿主此前已持久化的事实保持原义。
- `TimedOut`：deadline 到达且全部 native 已退出、暂存输出已撤销、租约已归还后才是终态。deadline 到达至排空之间只处于 `Draining`；调用方等待超时不改变模块状态。
- `Unknown`：native 计算结果无法确定时须继续排空后再终结；宿主提交回执未知时由持久化 Owner 按原 `RequestId` 查询原操作，不盲重试或用新代覆盖。
- `Failed`：确定失败且已完成清理；保留输入和错误证据。

### 8.2 错误码

错误为稳定枚举加结构化上下文，禁止只返回本地化字符串。

| 错误码 | 语义 | 默认恢复 |
|---|---|---|
| `MZ-001 InvalidRequest` | 身份、用途、版本或参数缺失/非法 | 修正请求后新 attempt |
| `MZ-002 SourceConflict` | 同 FOV ID 不同内容/角色/修订冲突 | 重新选择唯一源 |
| `MZ-003 FrameLayoutInvalid` | 尺寸、stride、通道、容量或有效域越界 | 由 Frame 端口重新提供 |
| `MZ-004 CoordinateMismatch` | frame、单位、方向、裁切或校正链不相容 | 修正坐标合同/引用 |
| `MZ-005 MissingRequiredFov` | 计划必需源缺失 | 仅允许诊断 Partial；检测由宿主阻断 |
| `MZ-006 NoOverlapEvidence` | 没有合法重叠或 anchor | 保持独立分量，不强拼 |
| `MZ-007 MatchInsufficient` | 支持、分布、候选或相容性不足 | 按批准策略重跑或拒识 |
| `MZ-008 DegenerateTransform` | 模型退化、不可逆、条件数超限 | 降级仅在 Profile 明确时允许 |
| `MZ-009 IndependentValidationFailed` | 独立复核不通过/缺失 | 关闭依赖用途，保留诊断 |
| `MZ-010 ResourceBudgetExceeded` | 计划或实际超 CPU/内存/I/O/tile/deadline | 停止新增工作，返回未完成 |
| `MZ-011 NativeAdapterFailure` | AsunImage/HALCON 适配明确失败 | 排空并按原输入新 attempt |
| `MZ-012 NativeDrainPending` | 取消/超时后 native 仍占用 | 保持隔离资源，禁止返池 |
| `MZ-013 StaleRevision` | 迟到结果与当前修订不匹配 | 丢弃派生发布，保留诊断 |
| `MZ-014 CacheCorrupt` | 派生缓存校验失败 | 只重建派生项，不改原帧 |
| `MZ-015 PermissionMismatch` | 目录/源作用域不匹配 | 拒绝读取，不用 hash 绕过权限 |
| `MZ-016 CancelRequested` | 已收到取消但尚未排空 | 等真实退出后给 Cancelled |
| `MZ-017 UnsupportedPurpose` | 该结果未取得用途资格 | 调用方改用合格路线 |
| `MZ-018 NativeOutcomeUnknown` | native 输出可信性不可确定 | 隔离本次资源；排空后 Unknown，使用新 attempt 重算 |
| `MZ-019 EmptyInput` | 实际源与完整 TilePlan 均为空 | 校验拒绝；非空全部 Skip 按计划诊断，不报此错误 |
| `MZ-020 MotionPoseUnavailable` | 物理用途缺少与曝光关联的 `q_enc`/反馈时间戳 | 仅保留 DisplayOnly/像素域诊断；补齐反馈后新 attempt |
| `MZ-021 MotionQualificationMissing` | 运动未证明 settled、epoch、方向或适用资格 | 阻断 Detection/Measurement；由运动 Owner 完成资格后重试 |
| `MZ-022 MotionResidualExceeded` | 运动/视觉残差超 Profile 的平移、角度、尺度或分位门限 | 保留残差和原图；返回 Partial/Rejected，不放宽阈值 |
| `MZ-023 BacklashDirectionMismatch` | 回差补偿需要方向证据但方向缺失或与地图不符 | 不应用回差地图；物理用途拒绝，显示用途可保留局部结果 |
| `MZ-024 TimestampSkew` | 触发、曝光和反馈不在同一 epoch 或超最大时间偏差 | 不按序号猜位姿；修正同步后新 attempt |
| `MZ-025 PlanarModelInsufficient` | 高度变化、板弯、视差或结构弹性超出 2D 平面模型 | 转入 3D/受控姿态路线；禁止扩大 2D 自由度掩盖 |
| `MZ-026 UnsupportedMethod` | 显示/标定/行时空方法未冻结或没有适配 | 拒绝该路线，不换算法 |
| `MZ-027 RegistrationDomainInvalid` | 缺节点/无效 cell/条件域外或补偿语义重叠 | 收窄域或补采新资产；不外推 |
| `MZ-028 OperationConflict` | 同 OperationId 的 kind 或输入摘要不同 | 拒绝第二请求，不改变原操作 |
| `MZ-029 AssetPublishUnknown` | 内容存储发布回执未确定 | 按原发布 ID 查询，禁止盲重写/激活 |
| `MZ-030 PlanningSnapshotUnavailable` | 连续位置请求缺少/无法验证预解析快照 | 同步不做 IO；宿主预解析精确值后新请求 |
| `MZ-031 ObservationPendingDrain` | 有限观察已结束，原端口/资源排空尚未确认 | 返回无业务结果的观察回执；查原操作/继续Drain |

错误恢复要记录是否已取得源租约、是否已调用 native、是否已产生派生输出；任何未知结果不得默认为成功。`RequestUnknown` 不代表持久化操作状态，模块没有宿主数据库或正式证据库的写权限。

## 9. 取消、超时、排空和资源所有权

1. 规划阶段先检查取消、deadline 和剩余预算；不为已取消请求新增源/边/tile/层。
2. 运行中向 adapter 发出取消；若 HALCON/AsunImage 调用不支持有界取消，隔离在途资源和线程，等待真实返回。
3. 未排空前不得释放或复用输入缓冲、native handle、临时 tile、GPU 上传或写盘缓冲。
4. native/port/临时资源归还后只记录 InternalReleasedUtc；该 operation 没有已交付输出租约或其全部输出租约已真实归还后，才发 ResourcesReleased 和唯一终态。持有输出时保持OutputHeld；顺序唯一见 §9.2。
5. UI 关闭只解除该消费者订阅，不取消其它消费者持有的源租约。
6. 失败、取消、超时和异常路径均执行幂等 `DisposeAsync`；重复释放不得二次释放。
7. 结果发布前再次检查当前 revision、权限和取消；A 请求迟到不得覆盖 B 请求。

内存预算必须包含原/校正副本、特征/对应点、稀疏图与求解矩阵、tile/halo/Mask/权重/来源、金字塔、GPU、写盘与压缩缓冲以及并发峰值。`100000x100000 RGB byte` 仅像素即约 30 GB，禁止全画布默认分配。

### 9.1 有界租约、目录和查询寿命

- `FrameRef`/manifest 是内容引用，不是像素租约；源由宿主内容保留策略保障。每个工作集取得 `IFrameLease` 后验证窗口、stride、hash/代次、mask 同源并记账；map/重采样使用局部窗口时必须重建对应索引。`map_image` 不检查邻域越界，错误线性索引可能导致崩溃，不能将全图 map 原样套在子窗口。
- 源读取、缓存及 native 中间对象均有独立持有计数和字节账本，借用/释放在成功、错误、取消、超时路径成对；正常计算结束仅发布不可变目录引用，不把输入 lease 转给结果。后续 GetTile 是独立工作项，重新核验源/权限/修订/预算并借有限工作集；找不到历史源返回 NotFound，不重算 latest 或改历史目录。
- `GetTileAsync` 成功返回 `MosaicTileResult` 中唯一 `IMosaicTileLease`。其只读缓冲在 lease 释放前有效，调用方必须 await DisposeAsync，不能在释放后保留 Memory 使用；失败状态 lease 必须 null。同一租约释放幂等，两个消费者分别取 lease，UI detach 只归还本 UI 租约。
- `DrainAsync` 停止新执行/标定/tile 准入，等待所有已接纳工作（含 tile）及内部 native 和借用源释放；外部已交付 tile lease 单独计入 OutstandingOutputLeases。尚有调用方租约时不宣布整个服务 ResourcesReleased。`DisposeAsync` 同样停止准入并等待实际释放，不强收调用方仍使用的缓冲；宿主先释放 tile 再 Dispose 服务。等待超过期限返回 `DrainUnknown`/计数/原 OperationId，服务仍保持隔离，后续可再 Drain/Query，不伪造 Disposed。Dispose 无取消参数且不得声称有界完成。
- `DrainUnknown` 是排空未确认的非终态状态，来源为 native/port/dispose 或外部租约未归还；原工作由服务继续管理并可Query，public Execute 的有限观察可以先返回无Result回执。Unknown 仅在已确认内部资源释放但计算可信性仍未知时成为业务终态；两者不可互换。
- ServiceLimits 的全部精确字段见A.1，包含 MaxObservationWait/MaxPendingPortCalls/MaxRequestBytes；均正且有限。终态过期按固定时钟/LRU 淘汰，查询返回Expired/NotFound而不重执行；未实际释放的active/output/port记录不淘汰，长期事实由宿主保留。
- 同 OperationId+OperationKind+CanonicalInputDigest 同时重复只接入原操作，第二调用令牌只取消其等待，不改变原执行令牌；同 ID 异 kind/摘要返回 `MZ-028`。原始执行令牌控制原操作。过期 ID 不重新接纳，宿主必须生成新 OperationId；用实例 SessionEpoch 和递增 operation 序列记录已接纳边界，使过期判断无需无限墓碑集合。所有异步工作在此服务内使用此 ID 规则。

`GetTileAsync` 是租约交付的例外：同 OperationId 重复取 tile 返回 MZ-028，不再次交付第一次 lease。每个消费者/重取使用新 OperationId。Query 的 Tile 分支只返回 TileOperationMetadata/错误/ResourceLedger，不返回或延长lease；在途记录不淘汰，内部排空且输出lease归还后才进入可淘汰终态记录。QueryAsync/Validate/Plan 不申请新操作；外部 PublishId 回查使用新的 MosaicAssetPublishQueryRequest.OperationId，Kind=AssetPublishQuery，只读提交事实，但它的在途 IO/观察状态仍登记以供Query/Drain管理。
- 缓存键至少包含实例/权限作用域、源 hash/布局/窗口/mask、双资产及资格修订、条件/cell/补偿组件、方法/算法/Profile、manifest/grid/LOD/halo/channel/purpose。跨请求只共享不可变内容，不共享可变 native handle；命中仍检查资格/撤销/权限，缓存不是资格权威。损坏缓存只能重建派生项。


### 9.2 有限观察、迟到资源与输出交付

本节是所有异步服务方法/端口的一致规则。`None` token 不表示无限等待；`ServiceLimits.MaxObservationWait` 必须是正且有限的 TimeSpan。原操作的绝对业务截止点是请求 DeadlineUtc，public 方法本次观察截止为 `min(DeadlineUtc, Clock.GetUtcNow()+MaxObservationWait)`；利用注入 TimeProvider 的单调计时器等待剩余间隔，同时每阶段复核 UTC deadline，避免墙钟回拨无限延期。过期请求不接纳；原操作已接纳后的 token 取消或业务 deadline 到达请求停止新工作及在途取消。仅观察时长到达而业务deadline未到时，可先返回 PendingDrain、Result=null，原操作继续至自身deadline；“PendingDrain”表示终态/排空尚未可观察，不宣称一定发生业务超时。后续 Query/Drain 必须按原 ID 查看而不另开重复写/取图。

GetTile 有可转移输出，故观察先结束后立即关闭该operation的交付门并请求停止tile生产/取消端口，保留原任务排空，不让它继续生成无人可收的大buffer。其它无租约结果的Runtime/Solve/Validate可继续原操作，结果最终只在Query可见。Drain本次观察同样受min(显式deadline,当前+MaxObservationWait)限制，不取消其它operation；任何异步lease Dispose调用观察超限只记Pending，真实释放任务仍追踪。本轮不承诺强制终止不响应取消的外部代码。

**端口上下文：** FrameReadRequest、RegistrationReadRequest、CalibrationPublishRequest 和 MosaicAssetPublishQueryRequest 显式带 DeadlineUtc；RegistrationWork/TileRenderWork/Fit/Validate 继承其所属请求 deadline。服务传入独立的端口 CTS（业务取消/deadline），不能把已超时的 await 当成端口已返回。每次端口调用在调用前登记原 OperationId、call序号、kind、开始/观察截止和资源预算，加入 PendingPortCalls；调用结果/异常均由唯一有界清理工作者接收。不能 fire-and-forget 丢任务异常/lease；到达 MaxPendingPortCalls 拒绝新增 MZ-010，保留仍活动的原记录，不淘汰以凑名额。每次public观察等待有限，不给未退出端口资源返池，也不自动重试 Resolve/Acquire/Publish。

Frame/Asset/native 端口的 ValueTask 完成是该次内部临时资源实际清理或所有权已明确交接的契约，不是可提前抛取消的等待封装。服务观察方才能返回 PendingDrain。端口如有并行内部 IO，须在结果或异常前等全部结束；返回 lease/buffer 时只转移该对象的 Dispose 责任，内部 native/IO 已退出。服务观察超时仍保留一份 Completion/Dispose 观察，不多建轮询任务；迟到异常收集诊断，资源状态未知时不计 Released。

只读 QueryAsync 从本地registry返回快照，无外部 IO；registry短锁不 await，不因 native 持锁。Query token已取消仍返回当前元数据加 MZ-016，不取消原操作、不伪造 NotFound。外部 QueryAssetPublishAsync 使用具备permission/deadline的新操作请求，按有限观察包装；AssetPort.QueryPublishAsync 只能读原PublishId，不得隐式重新发布。宿主预解析 Plan 快照直接调用相同公开 AssetPort.ResolveAsync 时，宿主也须使用该 request 的有限deadline与可跟踪清理；最小 Host 可用已保存的离线 artifact+qualification，无需本服务新增准备入口。资产解析快照不含句柄/租约，迟到值可丢弃，但原端口 IO资源释放未确认仍记 PendingPortCalls。

**失败/晚到的清理：** Acquire 返回失败意味着端口已处理其临时租约；如果 Acquire 任务仍pending，服务不得将“尚无lease字段”解释为资源释放。它在观察后返回 FrameLeaseResult 的 lease时，服务清理工作者立即校验归属后 DisposeAsync，绝不继续算法或交调用方。RenderTile 返回成功时给的是 ITileBufferLease；在native退出前输入lease仍由Core保留，退出后先处理可释放输入，再由服务持有输出buffer，账本Delivery=ServiceOwned。Render迟到/取消/权限失效/manifest修订失配时buffer仅走Dispose，不发布输出。DisposeAsync本身可能pending，必须保留原call/字节占用并继续隔离；release receipt未确认前 Resources/InternalReleased 时间不填。资产内容发布 IO 若结果迟到为Published，原Publish操作记录该确切回执；先前观察的Unknown/WaitCancelled不撤销内容、不授资格，宿主再查原PublishId。

**GetTile输出的唯一交付点：** 在同一个服务内部锁内检查观察等待仍可接收、token未取消、Clock未越deadline、exact资格复核已完成且身份未变、输出配额有余；预留配额并包装一份IMosaicTileLease，以RunContinuationsAsynchronously完成源 TrySetResult(Returned/Available/该lease)。成功才在同锁内确认Delivery=Delivered/OutstandingOutputLeases++并解除ServiceOwned，失败则撤销预留且buffer仍由服务Dispose。成功完成即线性化点；锁内不得调用用户回调或await，等待者异步继续并通过同一锁更新registry，所以不能观察到漏记输出计数。超时/取消观察以同锁竞争 PendingDrain/WaitCancelled：其先成功则永不再交lease，服务释放；交付先成功则后来cancel不撤回/强收lease。调用方负责finally释放；若自行用外层WaitAsync丢弃本方法任务，仍须接收它最终Available并释放，不能以外层等待结束免除已发生的交付所有权。模块不使用WaitAsync后丢弃结果。Query不交lease；重复GetTile一律MZ-028。

内部native/临时源/迟到port资源释放后可以记录 InternalReleasedUtc，但已交付输出lease使operation State=OutputHeld、Availability=Active，AllOutputReleasedUtc=null，不能标全operation ResourcesReleased/终态或淘汰。lease释放确认后才填AllOutputReleased并进入可保留Terminal。公共Available交付是一项方法结果，不是全资源释放通知。未交付buffer的晚到清理则在其所有Dispose和port退出后置原操作Cancelled/TimedOut/Failed等确定业务终态。DrainReceipt.Drained 要求 ActiveOperations空、PendingPortCalls=0、OutstandingOutputLeases=0；有限观察/业务deadline到但任何port/native/dispose/output仍未释放，返回DrainUnknown计数，registry继续Query可见。DisposeAsync等待真实归还，本身不伪造有界完成。

**可判定反例（M-C2/M-C3）：** 用TimeProvider与异步闩锁执行，而非sleep猜顺序：(1) None token、Resolve不返回，MaxObservationWait后只得到PendingDrain，native/借帧调用0、原registry PendingPortCalls=1；随后迟到解析值不得推动已业务超时的operation。(2) None token的发布回查在deadline前不返回，回查只读调用计数1，返回无Result；解除闩锁后Query可读原回执且发布调用数0。(3) Acquire观察超时后才返回lease，public tile reply从未Available，service Dispose一次、再Drain才可Drained。(4) Render持有输入且卡住，超时不归还输入；native退出带buffer时输入/输出各只Dispose一次，迟到buffer从未交用户。(5) TrySetResult交付与取消屏障同时竞争，恰有一个观察结果：交付赢则一份用户lease/OutputHeld且cancel不Dispose它；取消赢则Result=null、service自己Dispose且输出交付计数0。(6) GetTile已Available但用户未Dispose，Query.Tile.Delivery=Delivered、OutstandingOutputLeases=1、DrainUnknown；用户释放后计数0、仅一次AllOutputReleased和Terminal。(7) Release任务不返回，Registry不淘汰该operation/不返池；有限Drain可以返回Unknown并保留资源。(8) 内容发布观察结束后迟到Published，Query仍以原PublishId/内容hash确认Published、资格签发0、写调用数1。

## 10. 持久化、修订和回执

Core 是纯计算/派生目录生产者，不直接写宿主数据库、正式证据库、配方或质量记录。`ResultStaged` 只表示不可变候选结果已交给调用方内存，不是提交或耐久回执。可选 tile cache 必须可丢弃、按完整派生身份寻址且不成为唯一事实源。

宿主持久化 adapter（由宿主选择并注入）按以下顺序执行：

1. 固定原 `RequestId`、attempt、parent revision、输入闭包 hash、Profile/算法/adapter 版本和 permission scope。
2. 将 Manifest/派生 tile 写入暂存位置，逐项校验长度/hash；原帧和旧 revision 不变。
3. 以显式 expected revision/CAS 发布 Manifest 与结果引用；提交操作身份稳定且可查询。
4. 超时/断连时状态为宿主持久层 `Unknown`；调用方必须查同一操作 ID，不重发另一个提交，不由 IM-023 猜测写入是否完成。
5. 只有明确成功回执后宿主才能暴露该 revision 为可读。提交失败时模块结果可作为临时诊断保留，但不得伪装耐久结果。

新参数、坐标链、源集合、用途或算法形成新 revision/attempt。禁止原位覆盖已引用 Manifest/tile；历史不可读时报告缺失，不用 latest 替代。升级回退由宿主重新指向兼容版本或新建回退 attempt，不删除原结果。

## 11. 可选 UI 契约

UI 是独立投影，可不随无 UI 包交付；完整模块规划包含 D.5 的 WPF 控件切片。控件只依赖 Core 公共契约，宿主显式注入 D.5 的文本/权限/显示窄端口、所属 Dispatcher、资源根和 `IMosaicService`；`IMosaicTextPort` 是本方接口，不冒称上游存在 `ILocalization`。语言桥使用 localization 的实际 Resolve/Subscribe/Detach，进度仍沿唯一 Core 端口投影。

最小工作台布局：影像主视口、FOV/分量树、来源与用途状态、接缝/残差详情、资源/进度和错误恢复区。默认显示原图/派生图明确标签；点选顺序为屏幕 -> canvas -> global -> 原 FOV，返回多源贡献、原值和派生值；落洞显示“无数据”。

局部质量热图必须来自有空间坐标、单位、输入/算法版本的实际质量证据；只有全局证据时只显示全局数值，没有证据时显示缺失，不合成局部热图。不适用的指标显示“不适用”，不能填零冒充测得零误差；当前失败/失效结果不能显示上次成功图而不标明历史身份。

必须支持：选择 FOV/分量、原图与派生图切换、接缝两侧原图对照、残差/支持域查看、暂停显示请求、取消当前宿主发起的执行调用、重新请求已授权 tile、键盘导航和高 DPI。隐藏高级参数采用渐进披露；不能隐藏缺源、Partial、Unknown、保护冲突或用途阻断。

控件不允许直接编辑变换、改变 Profile、修改输入帧或触发设备。任何“采用/保存/提交”由宿主权限和原 Owner 处理，模块只返回候选派生引用。

### 11.1 WPF 工作台任务与布局

消费者的三个角色为查看者（只读导航）、分析员（检查来源/残差/用途）、标定工程师（显式发起候选求解、验证、未资格内容发布）。资格授予/激活命令留宿主；模块没有按钮冒充放行。标定页先展示采样/身份/分区闭包，再显示各条件 cell 的留出诊断，最后展示候选与回执，不让“发布”跳过验证。无权限的动作给出宿主返回原因，不隐式改变 Profile。

仅使用固定 1920×1080 验证 viewport，扣除任务栏、窗口框/标题及宿主状态栏后按实际 client 区布局；不调整用户显示。初始内容宽度约 70% 给影像，左侧来源树约 15%、右侧详情约 15%；顶部单行关键命令，底部状态/资源一行，详情可收起但缺源/用途阻断/DrainUnknown 始终可见。比例是布局起点，WPF 实测须证明长英文/三语、OS DPI 和实际可用 client 内不截断关键命令；不以示例像素数证明布局通过。

控件组合使用已安装 25.2.3 的 `DockLayoutManager/LayoutPanel` 承载视口/树/详情，`TreeListControl/TreeListView` 展示 Tile→Observed FOV→source/组件身份，`PropertyGridControl` 只读展示冻结 Profile/资产，`SuperTip` 解释用途限制、越域和恢复。影像复用 viewport 模块，不用 Grid 复制像素显示算法。当前不存在 dxdocs 可调用工具；之前官方网页请求403，本轮复用并定向读取本机25.2.3离线XML，公开属性/控件装配在D.5。本轮未消费编译XAML或验证实际运行，真实WPF门保留。

选择树节点同步定位该 footprint、来源和残差，不修改 geometry；点击空洞显示计划 Tile/Skip 或 Missing 的准确原因。原图/派生切换保持相同共同位置与缩放，双源比较锁定同一坐标；无法比较时给原因。每次 tile 查询携带 generation/manifest revision，迟到结果释放其 lease 后忽略。浏览可 latest-wins，检测请求不丢输入。暂停只停止新显示查询，取消只作用本宿主发起的运行；DrainUnknown 显示占用与等待动作，不能让操作员直接重启算法复用资源。

键盘 Tab 按关键命令→来源树→影像→详情→恢复顺序；方向键移动树项、Enter 定位、Escape 退出局部拾取/弹出层，不直接取消设备或运行。恢复/取消命令提供可见按钮、焦点和 SuperTip；确认是否取消由宿主对具体 operation 呈现，模块不隐藏临界动作。语言/主题由宿主动态传入，模块不增加语言下拉入口。UIA 名称包含来源身份和状态，不能只靠颜色表达资格。

| 资源键/语义 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| PlannedPose | 计划位姿 | 計畫位姿 | Planned pose |
| ObservedPose | 实际位姿 | 實際位姿 | Observed pose |
| Skipped | 未采集（跳过） | 未擷取（略過） | Not captured (skipped) |
| Missing | 缺少图像 | 缺少影像 | Image missing |
| NoData | 无数据 | 無資料 | No data |
| DisplayOnly | 仅供查看 | 僅供檢視 | Display only |
| OutsideDomain | 位置超出标定范围 | 位置超出標定範圍 | Position outside calibration range |
| DrainUnknown | 资源释放未确认，请等待 | 資源釋放未確認，請等待 | Resource release unconfirmed. Wait. |
| PublishContent | 发布标定内容 | 發布標定內容 | Publish calibration content |

该表定义核心语义，所有参数/错误/诊断/恢复文字仍须资源化并使用相同自然术语；格式与单位随宿主文化投影，数值/坐标计算不随语言变化。验收分开记录布局/主题/图标品质、任务流/键盘/UIA/三语、tile 迟到/租约释放和资格可见性；当前均未执行。

## 12. 正常、边界和失败案例

| 场景 | 期望 |
|---|---|
| 两帧有有效重叠、先验在范围内 | 建一条有方向边，返回变换、支持域、残差和可消费用途 |
| 多 FOV 由载台扫描、`q_cmd` 与 `q_enc` 不同但反馈已与曝光关联 | 使用 `q_enc` 作为先验，保留命令—反馈残差；只有通过运动门限才开放物理用途 |
| 只有 `q_cmd`、没有实际编码器反馈或时间关联 | `MZ-020`；可返回 DisplayOnly/像素域诊断，不生成物理坐标 |
| 运动未提供 settled 证据或采集跨重启 epoch | `MZ-021`/`MZ-024`；不得按固定等待或采集序号猜位姿 |
| 正向与反向扫描同一点出现稳定可重复回差 | 按方向选择已资格化的基线 d 子场，仅一次求 P；反向证据缺失 MZ-023；Compensation 非 null 首版 MZ-026 |
| 运动残差超过 Profile 但图像重叠仍可匹配 | `MZ-022`；保留先验/视觉两套残差，不能用视觉结果掩盖超限运动 |
| 板面高度变化或板弯造成重叠边缘视差 | `MZ-025`；仅输出局部/显示诊断，转 3D 或受控姿态方案 |
| 只有一帧 | 返回原图索引和单分量诊断；不调用全局束调整 |
| 三帧形成闭环且一条边冲突 | 保留全部边和冲突；几何用途阻断或按批准策略分量化，不删除异常边后成功 |
| 预计 6 帧、实际 5 帧 | 返回缺口；若只允许诊断则 `Partial`，检测用途不可用 |
| 源 ID 相同但 hash 不同 | `MZ-002`，不按文件名或最后写入者选择 |
| 像素尺寸不同但无校正链 | `MZ-004`，不按图像尺寸比例猜缩放 |
| 周期纹理匹配低残差但分布退化 | `MZ-008`/`MZ-009`，不以低均值残差开放用途 |
| 接缝穿过保护区 | `SeamConflict`，保留原图和几何；不强行穿越 |
| 多源在 tile halo 有贡献、核心无直接源 | 按完整 halo 计算；来源解释保留邻域贡献 |
| 负坐标 tile | 使用数学 floor，核心半开且跨 tile 不重不漏 |
| 取消时 native 未返回 | `MZ-012` 和 `Draining/DrainUnknown`；资源保持隔离，不返池 |
| A 旧修订晚于 B 新修订返回 | 丢弃 A 派生发布，B 不被覆盖，保留 A 诊断 |
| 派生 tile 损坏、原图仍在 | 只重建该 tile；不修改原图/历史 Manifest |
| 观察角色为 Unknown | 可作原图诊断；禁止参与强度融合或检测支持 |

## 13. 测试矩阵与验收断言

<a id="121-契约数学"></a>

### 13.1 契约/数学

- 身份：重复 ID、异 hash、异 revision、计划/实际清单顺序变化。
- 布局：stride 大于/等于最小值、奇尺寸、负坐标、不同通道、Mask/无效值、容量溢出。
- 坐标：column/row 交换、中心/角点、crop、缩放、旋转、镜像、单位换算、不可逆和多路径冲突。
- 图：无边、单边、断开、闭环、重复无序边、周期退化、anchor 与重叠不一致。
- 输出：tile 边界、LOD 0..5、奇数画布、负相位、halo、空洞、孤岛、跨块 4 邻接分量。
- 来源反例：实际像素布局与描述不符、同形状 mask 跨帧/跨版本换绑、有效像素数或对应点/残差被篡改；必须在相关算子/用途发布前拒绝，已借租约正确归还。
- 残差反例：长尾 payload 使 RMS 大于 P95 时按各自门限判定，不误拒绝排序；伪造 max 小于 RMS/P95、非有限值或只检查 P95 放过 RMS 超限均拒绝。

<a id="122-生命周期资源"></a>

### 13.2 生命周期/资源

- 正常成功、Partial、明确失败、取消前/中/后、deadline、native 未排空、重启恢复、缓存损坏。
- A/B 修订迟到、重复通知、重复释放、UI detach 而另一消费者仍持租约。
- 统计源租约/逻辑读取/物理解码/缓存命中/峰值内存和 CPU 账本，验证预算超限不静默截断。
- 最小 Host：在无 WPF dispatcher/window 的进程中，通过唯一 `MosaicModule.Create(options)` 创建 `IMosaicService`，调用 `Validate -> Plan -> ExecuteAsync(request, token)`，检查 `PurposeEligibility` 并释放服务；同一 Host 查询操作终态、读取 tile，验证无静态 UI 初始化和无隐式持久化。
- 负向 API/通知：请求对象重复携带 `CancellationToken` 或调用 `BuildAsync`/同步 `Execute` 必须无法通过公开 API 编译；进度端口为 `null`、无订阅者时执行及终态查询仍成功；慢订阅者不能延迟算法、native drain、租约归还或执行返回；订阅者抛异常只产生 `ProgressDeliveryFailed` 诊断，不改变结果；队列满/迟到 revision/终态后通知可丢弃或忽略，中间进度不保证完整。

<a id="123-算法用途"></a>

### 13.3 算法/用途

- 先验路线与匹配路线在同一冻结输入上的精度、失败率、残差和资源对照。
- 三源交界、保护 ROI、反光/阴影/遮挡、轻微变形、不同曝光/焦层/通道隔离。
- 显示融合逐值/来源/支持对照；证明不了最小缺陷保持时只开放显示，不开放检测/计量。
- 运动资格：命令位姿与实际编码器位姿不同、反馈缺失、settled 缺失、触发/曝光/反馈时间戳偏差、跨重启 epoch、正向/反向回差、轴比例/正交误差、温漂和已验证误差地图越域。
- 运动补偿：`q_enc`、`q_img`、`q_comp` 与 `DeltaT_visual` 分离；补偿前后残差、独立留出点和闭环门分别验收；补偿不得改变原始运动事实。
- 平面适用性：平面标定板有效域内外、板弯/高度变化、显著视差和结构弹性；验证 2D 失败时返回 `MZ-025`，不得以更高自由度 2D 模型掩盖。
- 连续工作区模型：用未参与拟合的二维位置留出点检验各有效 cell 内部的 `ΔX/ΔY` 插值误差；包含 cell 边缘/内部、缺节点孔洞、边界和域外点。验证只在已资格 cell 输出 Pose，缺节点不得跨洞补值，域外不得外推；插值后的最终 Pose 必须由几何参数重建，禁止矩阵元素平均。更换生产 Tile 间距、扫描顺序、跳过项或 ROI 子集时，同一绝对位置仍须得到同一模型求值结果。
- 位置与图像分离：规划列表保留稳定 TileId、行列、绝对计划位置、PlannedPose 与 Capture/Skip；乱序/非连续采集按 TileId 和曝光实际 q_enc 回配。Skip 项没有 FrameRef/实际 q_enc/观察图像但仍保留计划 Pose 并计为空洞；Capture 项实际位置偏离计划时使用实际反馈重算 ObservedFramePose。禁止按采集序号压缩 Tile、把 Skip 改成已覆盖或用邻图生成空洞图像。
- 标定靶：无定位框实心周期圆点板的 180°/镜像/方阵旋转歧义、部分遮挡/缺点/边缘截断、圆心质量退化和非唯一全局 PointIndex；不能消歧时发布数为 0。棋盘格与圆点板须分别产出并在独立留出物理点上比较，禁止混拟合或互相抵消失败。
- 双资产闭包：FOV 光学校正与拼接注册分别变更、缺失、撤销、过期或 hash/适用域不匹配；每个反例在构图/native 调用前阻断物理用途，不能 fallback 到另一相机/工位资产。
- 多设备隔离：两机台、多工位、多个相机/轴组及一种配置变化；证明请求、缓存键、manifest 和结果均指向准确资产，错误复用必须拒绝。
- 线扫时空资格：正反向、速度边界、加减速、时钟偏移/抖动、缺失/重复行、epoch 断开、编码器插值越域；任何不唯一行位置均不能产生物理坐标资格，且不能回退为面阵静态模型。
- 复用：只改显示窗口、合法 crop 与错 crop origin、同一步长不同实际位置、binning/镜头/尺寸变化、越域 cell、曝光变化后复用旧辐射派生；分别按 §5.2B 处理，旧资产和原帧保持不变。
- 辐射：本版没有辐射请求合同，不调用 `adjust_mosaic_images`；尝试通过隐藏字段启用拒绝。未来批准切片再执行byte正例及非byte转换/系数边界断言。无质量空间证据时 UI 不生成热图，不适用不显示为零。

<a id="124-两消费者接收"></a>

### 13.4 两消费者接收

1. **大板查看宿主**：只消费虚拟目录、LOD/tile、来源拾取和 Partial/缺源显示；验证 UI 关闭不影响另一个消费者。
2. **拼接分析/跨 FOV 检测宿主**：无 UI 调用同一 Core；验证几何资格、原图回溯、保护冲突、取消和错误恢复；宿主自己决定目标关联与质量处置。

两者必须使用同一发布包、同一输入快照和同一错误语义；不得以某一产品页面截图或单元测试替代接收。真实客户样本、WPF 资格、HALCON native 取消和生产吞吐另设门禁。

<a id="125-第二轮场景驱动复审矩阵"></a>

### 13.5 第二轮场景驱动复审矩阵

每一行都是实现/集成验收场景。矩阵中的 Profile 值来源必须是宿主签名并版本化的 `MosaicProfile` 或适用的上游公共契约；若没有值，按表中策略拒绝用途，不由实现者补猜阈值。

| 场景/输入 | 参数来源 | 处理顺序 | 输出、状态/错误 | 恢复动作 | 可判定验收 |
|---|---|---|---|---|---|
| 正常：两帧、相容角色、适用先验、合法重叠 | Profile 指定先验路线、坐标/域和独立验证门；帧身份来自 006 | validate -> lease -> project supports -> graph -> verify -> manifest | 完整几何组件、原帧目录；Completed | 无需恢复；宿主另行提交候选结果 | 方向已知点映射误差在 Profile 容差内；原始 mask 缺口不增不减；输入租约最终归还 |
| 运动正常：多 FOV 有 `q_cmd/q_enc`、settled、同 epoch 时间戳，误差在域内 | `motion-control` 反馈端口、mosaic `MosaicRegistrationArtifact`、MosaicProfile 运动门 | validate motion closure -> check epoch/skew/settled -> compose prior；视觉残差只在显式离线 PairBundle 诊断 -> independent anchor | 生产每 FOV 返回运动资格与 `q_enc/q_comp`；离线诊断另记视觉残差，不能回写生产先验 | 运动证据缺项则新 attempt 补齐；不在本次静默猜测 | 反向/重复/温度样本均在 Profile 门内；先验与离线诊断闭环分别可追溯 |
| 运动缺闭包：只有 `q_cmd` 或反馈与曝光无法关联 | `MotionEvidencePolicy=Required`、最大时间偏差和 epoch 规则 | 在几何求解前拒绝物理用途；可保留原图索引 | Failed/Partial + `MZ-020` 或 `MZ-024`，`PurposeEligibility` 不含 Detection/Measurement | 补交 `q_enc`、epoch、时间戳后新 attempt；禁止按序号补位 | native 几何适配器调用数为 0 或仅诊断路径；没有伪造单位变换 |
| settled 缺失、方向未知或跨重启 epoch | 运动 Owner 的 settled/方向/epoch 合同 | 先做运动资格检查，再决定是否构图 | `MZ-021` 或 `MZ-023`；仅允许明确 DisplayOnly | 重新采集或完成运动资格；不套用默认回差图 | 输出明确缺项和来源；不把固定 sleep 当 settled，不跨 epoch 合并 |
| 正反向回差、比例/正交误差可重复且地图在适用域 | RegistrationField 基线的组件/方向/温度/空间域 | 校验基线 -> 一次求 P=G0+d -> 保留 q_enc 与派生位置 -> 独立复核 | 基线资格按用途判断；Compensation 非 null 恒 MZ-026 | 越域/版本不符则新 attempt 使用正确基线，不叠加附加地图 | 同一点正反向留出样本在门内；同组件不补两次 |
| 运动/视觉残差超限或两者冲突 | Profile 的平移/角度/尺度 P95/P99/最大门，独立 anchor | 不扩大模型、不放宽阈值；冻结诊断并阻断用途 | `MZ-022`，保留先验/视觉/闭环残差和冲突边 | 修正机械/同步/标定后新 attempt；必要时转显示诊断 | 超限样本不会产生 MeasurementUsable；没有用 bundle Error 替代独立精度 |
| 高度变化、板弯或视差超出平面模型 | mosaic 拼接资产的平面有效域、Profile 高度/视差门；FOV 局部模型来自 calibration-assets | 平面适用性检查 -> 失败即停止 2D 物理拼接 | `MZ-025`，转 3D/受控姿态或局部显示 | 由 3D/姿态 Owner 提供新资格资产 | 不通过时不扩大仿射/投影自由度，不伪造全局 mm 坐标 |
| 无 finder 实心周期圆点板出现对称多解或被遮挡后点号不唯一 | 靶标身份确认、点阵拓扑、曝光关联 `q_enc` 和批准的消歧规则 | 保留圆心候选 -> 枚举拓扑映射 -> 全局一致性/独立锚点检查 -> 多解即拒绝 | 诊断结果，不发布拼接注册资格；物理用途拒绝 | 补充有身份依据的观测后创建新标定会话/资产修订 | 最近邻、采集顺序或视觉上下左右不能决定点号；多解时拟合/发布调用数为 0 |
| 生产 FOV 位于标定采样节点之间，且其位置/条件落在已验证有效 cell | MosaicRegistrationArtifact 的全局基准、残差节点、插值修订和实际曝光关联 `q_enc` | 校验资产/方向/温度域 -> 求二维误差分量 -> 重建最终 Pose -> 独立域门 | 返回该绝对位置的 Pose 与插值支持节点；允许时可供物理用途 | 网格不支撑位置/条件时补采并发新资产或收窄域 | 标定采样间距与生产步距改变不改变同一绝对位置的求值；矩阵插值调用数为 0；越域求值拒绝 |
| Tile Plan 含跳过项并以非连续/倒序路线采集 | 稳定 TilePlan、绝对目标坐标、Capture/Skip 与帧-曝光-反馈关联合同 | 先生成全量计划 Pose -> 保留 Skip 项 -> 实际帧按 TileId 回配并用 q_enc 重算观察 Pose | Skip 项保留 TileId/PlannedPose 且标记未采集；采集项保留 FrameRef/ObservedFramePose；覆盖缺口明确 | 补拍使用原 TileId 或新 attempt 的稳定 tile revision；不压缩编号 | 随机改变采集顺序及删去任意 Capture 项后，其它 tile 的稳定身份/绝对 Pose 不变；Skip 不产生帧、不增加覆盖率 |
| 棋盘格用于兼容验证，但与实心圆点板的独立留出误差冲突 | 各自靶标修订、共同物理 frame、独立留出 Profile | 两路线分别求解/报告 -> 比较全域与最差区域 -> 冲突调查 | 不合并资产、不平均参数；争议域资格拒绝 | 检查靶标、相机或同步并重新独立采集 | 一条路线通过不能抵消另一条失败；原始两份证据保留 |
| 线扫曝光行缺时间戳、反馈 epoch 不同或速度越域 | 线扫时空资产、时钟/编码器端口、扫描 Profile | 先核验逐行时空关联 -> 失败即禁止物理变换/几何求解 | `MZ-020/024` 或适用资格错误；仅保留线帧诊断 | 修复同步或重新标定，新建 attempt | 不调用面阵静态映射作为 fallback；不插值跨 epoch 或猜缺行位置 |
| 同时请求不同工位/相机，某 FOV 误引用另一设备资产 | machine/station/camera/axis group 身份键及双资产 hash | 按每 FOV 完整身份解析 -> 校验域/修订 -> 任一不符即拒绝 | 对应 FOV 拒绝原因；不产生跨设备统一物理结果 | 提供正确资产并创建新 attempt | 改变一个身份键即可稳定触发拒绝；缓存命中也不得返回另一设备的资产 |
| 空输入：ActualFovs=0 且 TilePlan 为空 | API 固定规则，不取默认 Profile | 取租约/native 前拒绝 | `MZ-019 EmptyInput`；未接纳 | 补齐输入后新 attempt | native/lease 调用数为 0 |
| 全部 Skip：ActualFovs=0，非空完整 TilePlan | 固定 Tile 身份和模型域；诊断用途 | 纯计划求值，保留所有空洞 | `Partial`、覆盖 0；无观测 Pose/Frame；无检测/计量资格 | 显式补拍新 attempt | native/lease 调用数为 0，计划分母不缩小 |
| 部分成功：Expected 有必需缺源或视觉图断成多分量 | 预计清单及 Required 语义由宿主/原合同；诊断用途由请求声明 | 输入校验 -> 保留所有源 -> 分量求解 -> 计算 completeness | `Partial` + 缺失 FOV/未连接分量；依赖全局关系的 Purpose 不可用 | 宿主补源并新 attempt；不能只重命名最大分量 | 分母保持原预计全集；缺项显式；不得删分量后声称完整 |
| 歧义：周期纹理、多候选接近、低残差但几何退化 | PKG-022 的匹配策略、Profile 支持/退化/独立验证门 | 保留候选 -> 分布/条件检查 -> 不进入求解或标验证失败 | Failed/Partial + `MZ-007/008/009`；diagnostic only | 有批准先验时新 attempt 走先验路线；否则拒绝 | 候选改变、候选顺序变化不能静默改变选解；留出点/anchor 必须独立于拟合输入 |
| 错误输入：同 FovId 异 hash、缺单位、逆变换不存在或过期校正 | 006/007/016 公共合同和请求快照 | 身份/hash -> layout -> unit/frame/revision -> 域/逆映射验证 | Failed + `MZ-002/003/004`；不调用后续算子 | 修复来源链或产生新的输入 revision | 每类反例在第一次不变量处停止；未取得的租约释放；没有单位阵/猜尺度 |
| 超大输入：画布/矩阵/tile 乘加溢出或超预算 | Profile 的 max pixels、bytes、edges、features、tiles、deadline；硬件预算由宿主批准 | checked arithmetic -> sparse planning -> 全请求准入 -> 分批执行 | 计划拒绝或 Partial + `MZ-010`；无超预算新准入 | 宿主按批准 Profile 新建低负载诊断请求；检测义务不变 | 峰值和逻辑 I/O 不越预算；不分配全画布；溢出测试可重复触发并返回同错误 |
| 高并发：两个宿主请求同源，多个 tile 竞争 | Profile 并发上限、006 lease、每 adapter 的序列化策略 | 每请求独立预算/代次；共享只读租约；同 native 实例串行 | 各自 RequestId/revision/结果；超限请求排队或 `MZ-010` | 释放后排队继续；取消仅作用于对应 attempt | 无跨请求源混淆、双重释放/共享 handle 并发；资源和事件逐请求可归属 |
| 噪声/遮挡/弱纹理：pair 支持不足或分布集中 | PKG-022 方法/Profile 的 support、空间分布、遮挡门 | 检查适用域 -> 匹配 -> 支持分布 -> 先验交叉核验 -> 全局优化 | 明确 `MZ-007` 或 `MZ-009`，保留图像/候选诊断 | 只有既有有效先验时回到先验诊断；不扩大搜索/自由度自动重试 | 原始有效域和被遮挡支持可追溯；同一输入 Replay 产生一致状态及容差内几何 |
| 取消：排队前、纯规划中、native 调用中 | 调用方在单次执行中传入的 CancellationToken；取消/超时语义本指导 | 队列前检查 -> 规划间检查 -> native 发取消 -> 等真实 drain -> 撤销暂存 -> 归还 lease | 接纳前可即时 `Cancelled`；native 中 `Draining`，结束后 `Cancelled`；进度端口可尽力发送 `CancelRequested`，附 `MZ-016` 诊断 | drain 后允许新 attempt；取消不回滚宿主已提交事实 | 未 drain 时输入/输出缓冲仍有效；源回收发生在 native 退出后；取消不影响 B 请求；取消终态可从返回值/查询取得 |
| 超时：deadline 到但 native 不可中断 | Deadline 来自 Profile；native 实际停止能力来自 adapter 实测 | 到期停止新准入 -> 请求取消 -> 保持占用至返回 -> 丢弃未发布输出 -> 终态 | 先 `Draining`；真实退出并清理后 `TimedOut`；无法确认输出则 `Unknown/MZ-018` | 仅新 attempt；旧操作不盲重放/覆盖 | 测试用阻塞 adapter 可证明 deadline 不释放租约；终态前无 ResourcesReleased |
| 资源上限：内存/CPU/I/O/来源数/分量或磁盘预算用尽 | 版本化 ResourceBudget；物理解码/缓存账本来自 006 adapter | 规划完整请求成本 -> 每阶段准入前扣额度 -> 达限停止新工作 -> 排空 -> 保留部分诊断 | `Partial` 或 Failed + `MZ-010`，精确报告已完成阶段和剩余缺口 | 释放资源后由宿主显式发新请求；不自动降低 LOD/缩分母 | 每维账本有计划/实耗；用尽后新工作计数不增；没有负剩余或隐式截断 |
| 保存/回执未知：Manifest 暂存后宿主断连 | 原持久化 Owner 的操作 ID、CAS revision、hash/耐久策略 | IM-023 返回不可变结果 -> 宿主暂存校验 -> CAS commit -> 查询原操作回执 | 模块保持计算 Completed；宿主写入为 Unknown，不混成模块错误 | 按原 operation ID 查询；成功则收悉，明确未提交才可重新提交原幂等操作 | 断连前后只出现一个逻辑结果；原 Manifest/旧 revision 不变；不查 latest 猜测 |
| 版本/修订：算法参数或源 hash 改变、旧响应迟到 | SemVer、AlgorithmRevision、ParentRevision 和依赖快照 | 对照 schema/hash -> 建新 revision -> 发布前 CAS/当前代复核 | 新结果独立身份；旧响应 `MZ-013 StaleRevision` 丢弃发布 | 保留旧结果；新 revision 失败时按旧包新 attempt 回退 | A 晚于 B 完成不能覆盖 B；历史 bytes/hash 不变且按原 schema 可查询 |
| 无 UI 调用：Replay service/批处理宿主 | 构造函数显式注入 Core、006/007 端口、adapter、诊断 | Validate -> Plan -> ExecuteAsync -> 检查 PurposeEligibility -> 释放模块 | 同 UI 完全相同结果/状态/错误；无窗口线程 | 由调用方取消/重试/持久化；重试生成新 attempt | 在无 WPF dispatcher/window 的进程运行；无静态初始化依赖；所有租约释放 |
| 可选 UI：视口换 FOV、关闭/取消、A 请求晚到 | UI 宿主权限/语言/主题；`IMosaicService.GetTileAsync`、MosaicTileRequest 和 request generation | UI 只发查询 -> core adapter 产 tile -> generation check -> dispatcher 投影 | 显示来源/用途/缺口和明确状态；旧 tile 丢弃 | 控件 detach；其它消费者请求继续 | 关闭控件不取消另一宿主；迟到 tile 不覆盖当前 revision；三语文本不改核心参数 |
| 第二消费者/长期运行：两个独立应用轮换调用，反复读随机 tile | 同一包/API 版本；每宿主各自 Profile/权限；固定长期负载计划 | 并行接收 -> 每轮固定快照 -> 运行/取消/归还 -> 周期检查账本 | 同一契约行为；资源曲线稳定，历史引用可解释 | 超资源限流/拒绝新请求；重启从快照新 attempt 恢复 | 两消费者独立构建运行；至少按已批准持续时长/迭代数执行，无租约/句柄增长趋势或跨租户读取 |

该矩阵是拟验收合同，不声称这些场景已执行。性能场景的持续时长、数据规模、允许增长和 P95/P99 数值必须由真实 Profile 批准后补入该唯一指导。

## 14. 性能预算、可观测性和确定性

<a id="131-测量方法"></a>

### 14.1 测量方法

Profile 冻结后，分别测冷/热缓存、源数量/尺寸/通道、重叠边数、特征数、模型、tile/halo/LOD、并发和取消频度。拆分采集等待（若有）、几何、匹配、全局求解、首 tile、随机 ROI、显示、写盘和端到端的 P50/P95/P99；未冻结 Profile 不写“达标”。

至少记录：输入/算法/AsunImage/HALCON 版本、线程/硬件、边和 tile 处理顺序、实际参数、资源规划/消耗、峰值、缓存命中、取消阶段、native 排空、残差分布和缺口。浮点归约顺序、线程和硬件不同时不得宣称位级相同；若需可重复性，冻结顺序和容差。

<a id="132-诊断关联"></a>

`MosaicBenchmarkProfile` 是有消费者的版本化输入，不另建报告权威：含 ProfileId/revision/input hashes、AreaScan/LineScan/PlanOnly、相机/源数量与尺寸/通道/有效域、工作区和条件子场/节点/cell 数、边数/对应点/缺源/Blank/Skip 比例、方法/网格/tile/halo/LOD、顺序与随机 ROI 负载、线程/并发/取消频度、冷/热/预热计划、样本数/最低完整数、有限 deadline、内存/解码/逻辑读取/缓存/句柄/租约/输出保留上限及目标阈值来源。资源计数覆盖同服务重叠工作，不仅当前算法的局部变量。

测点固定为准入、源借用、先验/插值、pair、全局求解、独立验证、候选封口、首 tile/后续 tile、取消请求、native 退出和资源归还；标定另测观测准备/基准拟合/节点构造/留出/内容发布回执。统计和端到端/删失规则直接采用 DEV-GOV-010 §3.1，不复制另一套分位算法。纯 Core 使用冻结合成值对象测数学/规划/有界账本；这只能证明软件路径。适配与物理用途用真实冻结源和目标硬件另测。没有客户目标时为 `NotEvaluated`，可测量方法准备但不可写达标；native/资源排空未确认不得判通过。

### 14.2 诊断关联

每条日志、指标和事件带 `RequestId/AttemptId/Revision/FovId/ComponentId/TileKey/Purpose`（适用时）。禁止写入整帧像素、私有板号或产品判定作为模块必需日志。敏感来源采用宿主提供的脱敏 ID；原始证据引用走 `PKG-040/041` 等 Owner。

## 15. 版本、兼容、发布和回退

<a id="141-版本规则"></a>

### 15.1 版本规则

使用 SemVer；契约字段、单位、有效域、错误语义、资源所有权和状态转移属于兼容面。

- 增加可选字段/错误诊断：minor，旧消费者必须忽略未知字段但保留未知状态。
- 删除/改名字段、改变单位/默认、改变坐标方向、改变 tile/halo 语义或把错误转成功：major。
- 算法修订、算子实现、默认参数或融合方法变化：至少 minor，并生成新的 `AlgorithmRevision`/Manifest；不可原位改写历史派生结果。

<a id="142-发布内容"></a>

### 15.2 发布内容

独立包至少包括 Core 契约程序集、实现程序集、适配器接口、可选 WPF 控件程序集、XML 文档、变更记录、兼容矩阵、无 UI 示例和测试资产。AsunImage/DevExpress 由宿主按平台固定版本提供；本模块不复制内部 DLL、不下载或替换依赖。

发布前门禁：契约审查、公开 API 编译、双消费者接收、Golden/Replay、资源/取消/恢复、依赖版本记录、许可证和来源记录。当前文档状态不满足生产发布门禁。

<a id="143-回退"></a>

### 15.3 回退

保留上一模块版本、输入快照、算法/适配器版本、Manifest 和结果回执。升级失败时由宿主选择旧版本新 attempt；不得在同一 revision 原位改写。旧 Manifest 只读可查，旧结果不因新算法失败而删除；新版本不能读取不兼容字段后悄悄当默认值。

## 16. 实施步骤与准入门

1. 本模块 Core 按附录 A 与下表逐切片接收；正式平台集成前由原 Owner 冻结 C-01/03/04/05/07 的正式字段、序列化、状态和回执，不用产品合同尚未采纳阻断无副作用 Core。
2. 以原图索引/标定定位/Partial 为首个无 UI 切片，完成租约、坐标方向、错误和结果回溯。
3. 加入受限匹配、全局求解和独立验证；同一输入对照先验路线，记录失败和资源。
4. 最后加入显示接缝/多带、随机 tile、来源解释和可选 WPF 控件；检测/计量用途另行资格化。
5. 运行双消费者测试、Replay/Golden、native 取消和资源压力；通过后再由宿主申请具体客户 Profile。

具体 Core 切片按 DEV-GOV-010 §3.1 逐项接收，不能用附录存在代替准入。正式平台集成和生产资格仍依赖对应正式契约、真实取消/排空、两个消费者接收、客户性能/精度/最小缺陷及 WPF/实机/现场证据；不将封装是否包含算子或常规公共签名查阅列为依赖准入门。

### 16.1 六项准入逐切片矩阵

列 1～6 对应 DEV-GOV-010 §3.1 原编号。主控于 2026-10-09 接收M-C1/M-C2/M-C3六项软件规格的历史事实保持；只批准软件Core/模拟端口/契约断言，不证明代码、真实拟合、HALCON或物理用途通过。2026-10-11起整模块执行、内容自审和返修在永久原会话完成，总控只调度/接收状态。M-V1/M-U1本轮指导自审收口见D.8，运行/集成门仍按下表；附加补偿及未批准美缝方法仍NotSupported，不用Core接收推整模块生产资格。

2026-10-11 主控结合前轮已读 C.1–C.6 方法、全字段 fixture/API、测试/性能计划和工程落点，并回读 0.5.2-prep C.6.3/C.6.4 的异常/cleanup 两轴、构造前固定槽/NoWork、Native 承接及原实例恢复，接收 M-L1 六项文档规格为 `ModuleCoreImplementationReady`。M-L2 公开装配与 Owner 确定指导内容限定接收；实际 cv2 消费编译、真实 native、上游桥及物理资格仍 `PreparationIncomplete`。这次接收不包含实现、运行或性能/精度/生产达标结论；主控未独立重建 13406/13422-byte 新 request，不新增复算声明。

| 切片/真实消费者 | 1 边界/复用 | 2 唯一 API/单位/状态/资源 | 3 无 UI Host/端口 | 4 可执行断言 | 5 BenchmarkProfile | 6 工程/顺序/后续门 |
|---|---|---|---|---|---|---|
| M-C1 `ModuleCoreImplementationReady`：计划与连续 XY 求值；查看和分析宿主 | §1/5.2B；不生产图像/设备/质量事实 | A.1精确Request/Device/Profile/Field/Snapshot/Plan DTO与enum、§5.2A.4；纯托管 | Host预解析不可变Snapshot→Create(native adapters=null)→Validate→Plan；同步所有端口调用0，冻结Clock | 四角/边界、常数/线性恢复、条件/缺角；缺snapshot MZ-030与完整PredictionUnavailable；篡改candidate/validation digest拒绝；无IO；跳图身份不变 | §14.1的节点/cell/Tile、规划/checked预算，消费者Profile阈值 | 相同Core/Tests；主控已接收软件规格；生产权威复核不在同步Plan，实际精度/方向/HIL另门 |
| M-C2 `ModuleCoreImplementationReady`：虚拟目录/生命周期/tile 工作集；两个宿主 | §2/9.1/9.2；只读派生目录 | A.1精确ResourceLedger/CallReply/TileOperationMetadata与端口，A.2摘要 | 可控Frame/Asset/adapter；public有限观察不假排空；Query无IO | §9.2八反例；独立编码向量；ID冲突/过期；lease交付取消竞争；迟到buffer服务释放；Query不含lease；None token有限，输出未释放DrainUnknown | §14.1：pending IO/缓存/首tile/临时和输出资源、排空；模拟不证明native | 相同Core/Tests；预解析→Execute观察→Query原ID→GetTile→释放已交付lease→Drain→Dispose；实际端口另门 |
| M-C3 `ModuleCoreImplementationReady`：标定输入/候选/验证/未资格内容；标定与离线分析宿主 | §5.2C；资格/激活外部 | A.1精确组/分区/Grid/Profile/Candidate/Evidence/Publish DTO，A.2内容排self摘要，无循环 | Calibration/Asset模拟端口；具名方法CallReply/回查request有deadline，不移动/拍照 | 同组跨区/非唯一ID拒绝；Passed不资格；迟到Published原ID回查不重写；node支持不等验证/资格；独立digest投影 | §14.1组/节点/cell/拟合/留出/回执/pending IO，失败另列 | 相同Core/Tests；Solve/Validate/Publish分别观察→Query原操作→外部资格→Host Resolve快照；真实反算/样本另门 |
| M-V1 面阵Adapter/冷标定；指导内容原会话自审完成，运行/集成PreparationIncomplete | §5/D.1；生产PriorOnly，离线PairBundle诊断 | D.2公开装配/Mask/Pair端口，D.3 nearest，D.4点号/原点；A不变 | 两个独立Host；ImageLibDotNet只在适配层；原Task/根预登记 | D.8 AREA-01..05/CAL-01..02；无纹理、域/类型、取消/迟到/真实归还 | §14/D.2；同样本/冷热/全阶段/误接受拒绝/峰值，缺目标NotEvaluated | D.2唯一Adapter/Tests已绑定；常规公共重载消费编译仅影响具体调用；真实native/Golden/物理另门 |
| M-V2 线扫增量；线扫查看和分析宿主 | §5.2A.6/C.1–C.3；首行光学＋逐行平移 | C.4 v0.4 精确 DTO/端口，不借面阵光学 | C.6 两独立无 UI Host；同一工厂增量重载 | C.5/C.7 前反映射、缺重行、加速度/误差/epoch、折叠/多解、有限收尾 | C.7 行/列/三角面/候选对/权威读/输出/资源预算 | C.7 拆 M-L1 软件（ModuleCoreImplementationReady）、M-L2 HALCON（公开装配/Owner指导限定接收，实际适配PreparationIncomplete）、M-L3 物理集成（PreparationIncomplete） |
| M-U1 可选控件；指导内容原会话自审完成，运行/集成PreparationIncomplete | §11.1/D.5，权限/质量外部，不复制核心 | D.5 root/绑定/请求/显示/text端口；D.6完整三语 | 无UI Core独立；显式宿主viewport/localization桥，双STA各自根 | D.6/D.8 UI-01..02；固定1920×1080/宿主DPI/键盘/UIA、迟到/关停/原Task/语言；视觉另验 | 首可见tile/导航/UI阻塞、copybytes/lease峰值、原Task排空，阈值宿主Profile | D.5唯一Wpf/Tests及PageContract已绑定；本机XML不替消费编译/真实WPF；不阻断Core |

Core/Tests 的实际创建遵循唯一绑定；Tests 为 `Microsoft.NET.Sdk/net10.0/OutputType=Exe`，仅 BCL 与 Core 项目引用，固定时钟/确定性断言/有限异步闩锁，不另选测试包。受测构建命令 `dotnet build src/Modules/mosaic/Asun.Modules.Mosaic.Core/Asun.Modules.Mosaic.Core.csproj -c Release`；验证命令 `dotnet run --project tests/Modules/mosaic/Asun.Modules.Mosaic.Core.Tests/Asun.Modules.Mosaic.Core.Tests.csproj -c Release`。全部该切片必需断言完成才退出 0，失败/跳过/未结束为非零；外层有限进程截止点防止不可取消模拟任务冒充成功。本轮没有工程，未执行这些命令。

本轮可决定的面阵Adapter/冷标定/UI/自动建议工程语义见D；不改变已接收Core规格容纳隐藏字段。线扫v0.4固定于C，软件/适配/现场门分开；Core Ready不支持未批准匹配物理用途、多带/辐射或基线外补偿。后续实现或新范围依实际门在原会话继续，不再要求总控内容审核。客户Profile、证书/机械/同步实测和现场阈值不猜值，厂商SDK实现仍不在范围。

不能从公开资料确定的客户物理门不编数值；精确Owner与影响见D.8。局部观测引用原calibration-assets指导，物理原点反算/Adapter/WPF工程绑定本轮在D闭合，线扫模型与已接收切片沿C不变。真实消费编译、原Frame来源/光学资格、WPF桥、Golden/性能/HIL/计量/现场仍需实际验证；这些不是文档可决定的软件步骤欠账。

## 17. 参考与只读借鉴

- 连续规则研究（2026-10-09）：实际读取 SciPy `v1.16.2` 的 [`_rgi.py`](https://github.com/scipy/scipy/blob/v1.16.2/scipy/interpolate/_rgi.py) `_check_points`（18～37）、`_prepare_xi`（451～477）、`_evaluate_linear`（479～508），以及 [`test_rgi.py`](https://github.com/scipy/scipy/blob/v1.16.2/scipy/interpolate/tests/test_rgi.py) 的 linear_edges、out_of_bounds_extrap/fill、descending_points 与 invalid_points_order。`git ls-remote` 返回 tag 对象 `dd9a357d5945921310346226088ea8ab5c5356cc`；该对象不是已确认的解引用源码 commit（按此 SHA 请求 raw 返回404），所以复现以 tag 和逐文件 SHA-256 固定：源码 `602f16398f937a74795bd04d9f56a6df6092f4355e3b7f8e03070a139365bb29`，测试 `f926dd32e14c6206eaa1103a89026ba84ab9f96053c6026907c1103b1e3a350b`。已读 LICENSE.txt（BSD-3-Clause，hash `221e59f5e910fd7f94e44f0dac77436a11338c285c6346232e4a850a50da0e94`）和 pyproject.toml（hash `3f9c882e10cb29a2b4fbb59f7106fc1b7a749e6cf8c08ccd637231604dc7df7f`）：Python>=3.11、NumPy>=1.25.2,<2.6，构建 Meson/Cython/pybind11/Pythran。只借鉴四角权重、严格节点/边界及反例，不引 SciPy 运行依赖/复制源码。它允许 descending 和显式 extrapolation，本模块固定升序并禁止外推；它不提供无效cell/条件/物理资格，必须按本文加门，不能把其测试通过当本模块证据。
- 显示研究复用 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#mosaic-multiband-source-research) 固定 OpenCV `a0cda081f8d769f40ab2f4904738b4787b44d07c` 的 blenders/motion_estimators/matchers/stitcher 源码与 test_blenders/test_stitcher。该既有研究的转用优点为稳定全局相位/halo/源贡献及明确CPU工作集；全幅金字塔分配、PSNR和setTransform一致性测试不能证明最小缺陷保持/计量。Apache-2.0与旧文件通知及 imgproc/features/geometry/flann/可选CUDA依赖按原来源记录保留，不引 OpenCV runtime；当前仍只批准 stacking。
- HALCON 26.05 定向语义核对：`vector_to_hom_mat2d` 最少三对、超定最小距离；`vector_to_proj_hom_mat2d` 至少四对、真实协方差不是所有方法都有；`hom_mat2d_translate` 是 global frame；`map_image` 邻域越界不检查而可能崩溃；`gen_image_to_world_plane_map` 固定配置可复用map且物理 scale 单位按页声明，由校正模块提供。phase 候选已读 `phase_correlation_fft`（输入complex频域）、`fft_generic/rft_generic`（符号/归一化/反向宽度），只能形成研究候选；周期峰别名、constant/mask/符号/亚像素/独立精度与资源未比较，仍不批准生产纠偏。未执行算子/消费编译。
- DevExpress 公开说明读取依据：本机 `C:/Program Files/DevExpress 25.2/Components/Offline Packages/` 内 25.2.3 的 wpf.docking、wpf.grid.core、wpf.propertygrid、wpf.core 下 `lib/net8.0-windows/DevExpress.Xpf.*.v25.2.xml`；所核类型和限制见 §11.1。只读取官方 XML，不扫描 AsunImage 内部、不安装或更换依赖、不据此宣称 WPF/属性/部署运行通过。

- `PKG-017`：包职责、消费者和接入边界。
- `DEV-VIS-029 §8–15`：输入/输出用途、坐标图、HALCON 候选、多带、虚拟目录、生命周期、预算和双消费者。
- `SM-006`、`SM-008`：帧租约、有效域、单位、坐标方向和资源所有权。
- `CONTRACT-CANDIDATES.md#mosaic-contract-semantics`：原候选合同采纳项；正式类型仍由原 Owner 维护。
- 项目内 [HALCON operators](../../../halcon算子手册/operators) 与 `ImageLibDotNet.cv2` 公共边界：按 26.05 核对语义和参数；仅实际 C# 类型/重载或封送歧义查公共签名/消费工程编译，不检查内部或重复核验算子存在性。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_CameraCalib`：只读借鉴参数校验、结果对象、事件顺序和 `Dispose` 生命周期；旧 .NET/AsunImage 引用不作为本模块依赖。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_Aligment2D_NCCModel`：只读借鉴训练/搜索参数分离和异步入口组织；NCC 具体模型、签名和阈值不迁入本模块。
- 只读来源：[PCBA AOI 配准、拼接与补偿指导（原件快照）](../../references/project-snapshots/PCBA-AOI/20261006/original/docs/40-development/41-vision-platform/03-calibration-imaging/配准_拼接与补偿开发指导.md)，原路径 `H:\docs\40-development\41-vision-platform\03-calibration-imaging\配准_拼接与补偿开发指导.md`，SHA-256 `47e41e67c86fbb2d23957102661f200b8bc267e8f7b3f85468e5eeb3fd44e69d`。2026-10-06 按该 hash 复核全文与本模块职责：既有周期点阵身份、曝光关联反馈、拟合/留出隔离和运行时先验消费要求不重复吸收；新增采纳来源 §8.1.2 的 FOV 复用分类、§8/8.5 的 byte 辐射输入及真实校正图表达、§12 的残差重算规则、§3 的质量热图证据边界及 §15 对应反例，分别落实于本文 §4.2、§5.2B/5.3、§11、测试矩阵。来源基于 HALCON 24.11，具体算子限制以本地 26.05 页面核验。
- 用户参考只读快照：[500×500 FOV 拼接最终结论](../../references/user-notes/USER-003_500x500_FOV拼接最终结论_2026-10-06.md)，原路径 `H:\500x500_FOV拼接_最终结论.md`，SHA-256 `B4E1E924DCF56A723CA9701E31A89A154B09985AAD7A92428ECE1F99FD090FAF`。本模块采纳并细化的内容：固定标定板及计量实测几何；圆点索引由运动反馈预测、局部点阵确认；全局基准变换加连续二维残差场，生产任意有效位置按绝对反馈求值；标定采样网格与生产 Tile 网格解耦；Stage 先验支持空白 FOV；Tile Pose/计划身份与 Frame/采集顺序分离。插值冻结为有效 XY 面阵 cell 内对误差参数分量双线性插值并重建 Pose，禁止矩阵元素插值或域外外推。来源中的 FOV/工件尺寸、点距、移动步距、误差、耗时及硬件数值均只是示例，不进入本平台 Profile/验收；`Phase Correlation/FFT` 等路线未据本地 HALCON 26.05 手册和代表样本完成比较，故不采纳为生产路线。
- 来源其余内容：图/用途隔离、虚拟 tile、资源/取消、来源回溯、版本/恢复已有覆盖；P4 在线预览会话/共享预算协议、AOI 采检编排、私有持久化/CAS/签名库、原工程 API/验收结论不迁入；靶标/手眼建库与 3D 重建/参考面归原模块 Owner，NCC kernel 路线归 `PKG-022`，不在 mosaic 新建。seam/multi-band 自选方法和定点融合只作后续研究，不替换当前有界 stacking 基线；2 mm、0.05 px、300 ms、72 小时等来源项目数字不成为本平台参数或验收值。

## 18. 自审清单（本稿）

- [x] 核心能力可无 UI 调用；UI 只做投影。
- [x] 已明确原帧、坐标、匹配、校正和显示融合的端口边界。
- [x] 已区分几何、显示、检测、计量用途；未写入制程判定或放行。
- [x] 已给出强类型字段、单位、范围、候选默认值和缺省阻断规则。
- [x] 已给出唯一服务与具名运行时/标定入口、进度顺序、状态、错误码、取消、超时、排空、线程和资源所有权。
- [x] 已覆盖正常、边界、失败、双消费者、性能、可观测性、发布和回退。
- [x] 未把 HALCON 未核对签名或 AsunImage 内部当作公共 API。
- [x] 文档保持 `DesignReview`/`0.5.8-prep`；此前Core/线扫软件规格与M-L2限定接收保持；完整范围内部设计结论及D.5.1装配保持，本轮仅同步D.5.2的viewport显示副本生产者和Clear后Update。实际代码、适配、WPF运行、性能、设备和生产资格仍 `PreparationIncomplete`，没有声称已通过。

本清单只证明文档结构自审完成，不代表任何运行时测试、HALCON 适配、客户验收或生产资格已完成。

## 附录 A：模块核心 API Contract v0.3（Core 候选契约；逐切片准入）

已接收基础 Core 的契约版本标识为 `Module API Contract v0.3`（新增线扫面见附录 C 的 v0.4）；精确DTO、快照与有限观察回执形状不声明与历史 v0.1/v0.2 二进制或序列化兼容。当前无已发布本模块程序集，本轮没有迁移历史资产。

本节定义 Core 代码边界；准入只按 §16.1 逐切片记录，不能从契约存在推断其它切片获批。M-C1/M-C2/M-C3 的六项软件规格已获主控接收；平台 Schema 映射、序列化、Owner、生产资格和客户 Profile 仍由相应 Owner 冻结，本文不能成为第二份平台 Schema。公开类型/方法/事件/错误键/状态/参数/资源语义是获准范围内的唯一实施依据，不另造第二套 DTO、状态机或通知通道。

- 契约只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port；不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- v0.3基础公开服务面统一为 `IMosaicService`；`MosaicModule.Create(options)` 是唯一构造入口。附录 C 的 v0.4 专用增量继承此接口并用同名工厂重载，不能用它修改本节已接收字段。构造时注入 Core 端口和可选进度端口。不得暴露 `IMosaicBuilder`、`BuildAsync`、同步 `Execute` 或第二个服务工厂。
- `CancellationToken` 只出现在异步调用参数中，不属于 `MosaicRequest`、请求快照或结果持久化字段。每个新 attempt 由宿主传入自己的令牌。
- 进度端口只提供尽力通知。适配器按 §7.2 使用有界缓冲及独立派发；无订阅者、队列溢出、回调迟缓或异常均不能影响计算终态和资源排空。回调异常写 `ProgressDeliveryFailed` 诊断，不转成请求失败。
- 终态可靠读取方式是具名方法返回的 MosaicCallReply.Result（仅 Returned 非空），或保留窗口内 QueryAsync 的原操作结果；观察回执 PendingDrain/WaitCancelled 不是终态。通知不保证 exactly-once、完整中间进度或终态送达。
- 适配器按 HALCON 26.05 `halcon算子手册/operators` 的语义/参数经 `ImageLibDotNet.cv2` 调用；仅 C# 类型/重载或封送歧义查公共签名/消费工程编译，未解决歧义只影响具体调用切片，不重复核验封装是否包含算子，不影响无关 Core。
- 准入状态唯一见 §16.1：主控已按 DEV-GOV-010 §3.1 接收 M-C1/M-C2/M-C3 的职责、精确契约、无 UI Host、断言、Benchmark 方法和工程边界，标为 ModuleCoreImplementationReady；其余未接收切片保持 PreparationIncomplete。软件准入不意味着某个未冻结方法、native拟合/重采样、性能/现场验证完成。

```csharp
namespace Asun.Modules.Mosaic;

public interface IMosaicProgressSink
{
    ValueTask OnProgressAsync(MosaicProgress notification, CancellationToken dispatchCancellationToken);
}
public interface IMosaicService : IAsyncDisposable
{
    ValidationResult Validate(MosaicRequest request);
    MosaicPlan Plan(MosaicRequest request);
    ValueTask<MosaicCallReply<MosaicResult>> ExecuteAsync(MosaicRequest request, CancellationToken cancellationToken);
    ValueTask<MosaicCallReply<CalibrationSolveResult>> SolveCalibrationAsync(MosaicCalibrationRequest request, CancellationToken cancellationToken);
    ValueTask<MosaicCallReply<CalibrationValidationResult>> ValidateCalibrationAsync(CalibrationValidationRequest request, CancellationToken cancellationToken);
    ValueTask<MosaicCallReply<CalibrationPublishResult>> PublishCalibrationAsync(CalibrationPublishRequest request, CancellationToken cancellationToken);
    ValueTask<MosaicCallReply<CalibrationPublishResult>> QueryAssetPublishAsync(MosaicAssetPublishQueryRequest request, CancellationToken cancellationToken);
    ValueTask<MosaicOperationStatus> QueryAsync(MosaicOperationId operationId, CancellationToken cancellationToken);
    ValueTask<MosaicCallReply<MosaicTileResult>> GetTileAsync(MosaicTileRequest request, CancellationToken cancellationToken);
    ValueTask<DrainReceipt> DrainAsync(DateTimeOffset deadlineUtc, CancellationToken cancellationToken);
}
public interface IMosaicFramePort
{
    ValueTask<FrameLeaseResult> AcquireAsync(FrameReadRequest request, CancellationToken cancellationToken);
}
public interface IFrameLease : IAsyncDisposable
{
    FrameRef Source { get; }
    PixelRect Window { get; }
    ReadOnlyMemory<byte> Pixels { get; }
    long StrideBytes { get; }
    ContentDigest Digest { get; }
}
public interface IMosaicCoordinatePort
{
    ValidationResult ValidateChain(CoordinateChain chain);
    CoordinateMapResult MapPoints(CoordinateMapRequest request);
}
public interface IRegistrationAdapter
{
    ValueTask<RegistrationWorkResult> RegisterAsync(RegistrationWork request, CancellationToken cancellationToken);
    ValueTask<TileRenderResult> RenderTileAsync(TileRenderWork request, CancellationToken cancellationToken);
}
public interface IMosaicCalibrationAdapter
{
    ValueTask<CalibrationSolveResult> FitAsync(MosaicCalibrationRequest request, CancellationToken cancellationToken);
    ValueTask<CalibrationValidationResult> ValidateAsync(CalibrationValidationRequest request, CancellationToken cancellationToken);
}
public interface IMosaicAssetPort
{
    ValueTask<RegistrationReadResult> ResolveAsync(RegistrationReadRequest request, CancellationToken cancellationToken);
    ValueTask<CalibrationPublishResult> PublishUnqualifiedAsync(CalibrationPublishRequest request, CancellationToken cancellationToken);
    ValueTask<CalibrationPublishResult> QueryPublishAsync(MosaicAssetPublishQueryRequest request, CancellationToken cancellationToken);
}
public interface IMosaicDiagnostics
{
    bool TryWrite(MosaicDiagnostic diagnostic);
}
public interface IMosaicTileLease : IAsyncDisposable
{
    TileKey Key { get; }
    FrameRef Frame { get; }
    ReadOnlyMemory<byte> Pixels { get; }
    IReadOnlyList<SourceContribution> Contributions { get; }
}
```

`MosaicModule.Create(MosaicModuleOptions)` 返回唯一 `IMosaicService`。Options 是不可变值：`SessionEpoch:Guid`、`FramePort:IMosaicFramePort`、`CoordinatePort:IMosaicCoordinatePort`、`RegistrationAdapter:IRegistrationAdapter?`、`AssetPort:IMosaicAssetPort`、`CalibrationAdapter:IMosaicCalibrationAdapter?`、`Diagnostics:IMosaicDiagnostics`、`Clock:TimeProvider`、`ServiceLimits:ServiceLimits`、`ProgressSink:IMosaicProgressSink?`。只需要纯数学/计划时可不注入两个 native adapter，调用其特定方法返回 MZ-026，禁止隐藏窗口/设备初始化。Diagnostics 的 TryWrite 有界非阻塞；失败记账，不改变业务/清理。

### A.1 Core DTO 的精确形状和同步快照

本节替代旧 v0.2 的字段概述。以下为唯一字段名、类型和构造顺序，所有 public record 均不可变，集合防御性复制且非 null；没有隐含字段、扩展字典或“另含统计”。§3/4/5 解释字段语义，不能据其文字自行加 DTO 字段。平台事实以引用/消费快照映射进这些值，不反写上游资产。v0.3 不承载线扫物理求值；首版线扫增量精确契约见附录 C，独立协商 v0.4，不改本节字段/编码。基线之外附加补偿首版明确不支持；匹配观测生产未接收时返回 UnsupportedMethod，不要求 M-C1 补猜字段。

标识值类型 `MosaicRequestId/FovId/FrameId/AssetId/AssetPublishId/ConditionId/CellId/NodeId/PhysicalGroupId/TileId/PermissionScopeId/DiagnosticId/AttemptId/ProfileId/ComponentId/PointId/ExposureId` 的精确声明均为各自 `public readonly record struct Name(string Value)`；非空、UTF-8 字节长 1..128，不互换。字符串机器/工位/相机/轴/frame/方法/证据 ID 同限制；Diagnostic FieldPath/DetailKey 长度允许 0..512。ContentDigest 为小写 SHA-256 64 hex。所有下面声明均位于 `Asun.Modules.Mosaic`；`L<T>` 在本节是 `IReadOnlyList<T>` 的排版缩写，不是新运行库或可选类型。nullable 仅由 `?` 指定。读端口类型是独立消费 DTO，不泄漏数据库/SDK 类型。

```csharp
public readonly record struct ContentDigest(string Value);
public readonly record struct Revision(long Value);
public readonly record struct MosaicOperationId(Guid SessionEpoch, long Sequence);
public readonly record struct Length(double Value, LengthUnit Unit);
public readonly record struct Angle(double Radians);
public readonly record struct Area(double Value, LengthUnit AxisUnit);
public readonly record struct Point2(double Column, double Row, string Frame);
public readonly record struct PlanarPoint(Length X, Length Y, string Frame);
public readonly record struct AxisPosition(Length X, Length Y, string AxisFrame);
public readonly record struct PixelRect(long X, long Y, uint Width, uint Height);
public readonly record struct RectD(double MinX, double MinY, double MaxX, double MaxY, string Frame);
public readonly record struct Matrix3(double M11, double M12, double M13,
    double M21, double M22, double M23, double M31, double M32, double M33);
public record Transform2D(Matrix3 Matrix, string SourceFrame, string TargetFrame,
    Revision Revision, RectD ValidDomain);
public record CoordinateChain(Revision Revision, L<Transform2D> Edges);
public record ValueRef(string Id, Revision Revision, ContentDigest Digest);
public record DeviceCamera(string CameraId, CameraKind Kind, string AxisGroupId,
    ContentDigest AcquisitionConfiguration);
public record DeviceScope(string MachineId, string StationId, L<DeviceCamera> Cameras);
public record MaskRef(FrameId SourceFrame, Revision SourceRevision, ContentDigest Digest,
    ValueRef Storage, ulong ValidPixelCount);
public record FrameRef(FrameId Id, ContentDigest Digest, uint Width, uint Height,
    long StrideBytes, long CapacityBytes, PixelType PixelType, uint Channels,
    PixelLayout Layout, ImageOrientation Orientation, Revision LeaseRevision,
    PixelRect ValidWindow, MaskRef? Mask, ValueRef Storage, string PixelFrame);
public record ObservationRole(string Surface, string Layer, string Channel,
    string ExposureRole, string TimeRole, bool IsKnown);
public record FovOpticalCalibrationRef(AssetId Id, Revision Revision, ContentDigest Digest,
    string MachineId, string StationId, DeviceCamera Camera, ValueRef Qualification,
    ValueRef RectificationMap, PixelRect ValidWindow, CoordinateChain LocalChain);
public record MosaicRegistrationRef(AssetId Id, Revision Revision, ContentDigest Digest,
    DeviceScope Devices, string CommonFrame, Revision? QualificationRevision);
public record MotionCompensationRef(ValueRef Content, ValueRef Qualification,
    L<string> ResidualComponentIds, L<ConditionDomain> Conditions, Length MaxCorrection);
public record RegistrationConditions(ConditionId? ConditionId, AxisDirection XApproach,
    AxisDirection YApproach, double? TemperatureCelsius, Revision? TimingRevision,
    ContentDigest ConfigurationDigest);
public record ConditionDomain(ConditionId Id, ContentDigest ConfigurationDigest,
    AxisDirection XApproach, AxisDirection YApproach, double? MinTemperatureCelsius,
    double? MaxTemperatureCelsius, bool IncludeMaximum, Revision? TimingRevision);
public record ResidualNode(NodeId Id, ConditionId ConditionId, AxisPosition Position,
    PlanarPoint Delta, L<PhysicalGroupId> Groups, L<PlanarPoint> RepeatResiduals);
public record ErrorBounds(Length Rms, Length P95, Length P99, Length Maximum);
public record RegistrationCell(CellId Id, ConditionId ConditionId, NodeId N00,
    NodeId N10, NodeId N01, NodeId N11, bool IsSupported);
public record RegistrationField(Transform2D GlobalBasis, Transform2D RegisteredLocalToCommon,
    L<Length> AxisX, L<Length> AxisY, L<ResidualNode> Nodes, L<RegistrationCell> Cells,
    L<ConditionDomain> Conditions, L<string> ResidualComponentIds, Revision AlgorithmRevision);
public record CameraField(string CameraId, RegistrationField Field);
public record QualifiedCell(string CameraId, ConditionId ConditionId, CellId CellId,
    ErrorBounds Bounds, L<MosaicPurpose> Purposes);
public record MosaicQualificationRef(ValueRef Identity, string Issuer,
    ContentDigest ArtifactDigest, ContentDigest ValidationDigest, L<QualifiedCell> Cells,
    DateTimeOffset ValidFromUtc, DateTimeOffset ValidUntilUtc, bool Revoked,
    Revision AuthorityRevision);
public record RegistrationPlanningSnapshot(MosaicRegistrationRef Reference,
    MosaicRegistrationArtifact Artifact, MosaicQualificationRef Qualification,
    DateTimeOffset ObservedUtc, PermissionScopeId PermissionScopeId);
public record SettledEvidence(bool Settled, DateTimeOffset AtUtc,
    Length PositionTolerance, TimeSpan MinimumStableDuration, ValueRef Source);
public record MotionPoseEvidence(AxisPosition? Commanded, AxisPosition Encoder,
    Guid AxisEpoch, DateTimeOffset TriggerUtc, DateTimeOffset ExposureStartUtc,
    DateTimeOffset ExposureEndUtc, DateTimeOffset EncoderUtc,
    RegistrationConditions Conditions, SettledEvidence? Settled,
    double? SpeedMillimetersPerSecond, double? AccelerationMillimetersPerSecondSquared,
    ValueRef Source);
public record PriorTransform(Transform2D Transform, ErrorBounds Bounds,
    DateTimeOffset ValidFromUtc, DateTimeOffset ValidUntilUtc, ValueRef Source);
public record ExpectedFov(FovId Id, TileId? TileId, bool Required);
public record ActualFov(FovId Id, TileId? TileId, string CameraId, FrameRef Frame,
    ObservationRole Role, CoordinateChain PixelChain, FovOpticalCalibrationRef? Optical,
    MotionPoseEvidence? Motion, PriorTransform? StaticPrior);
public record TilePlanEntry(TileId TileId, long Row, long Column, string CameraId,
    PlanarPoint Target, AxisPosition? EstimatedEncoderInput,
    RegistrationConditions Conditions, CaptureIntent Intent);
public record MatchPolicy(string MethodId, Revision MethodRevision, Area MinimumOverlap,
    uint MinimumSupport, Length MaximumSearchTranslation, Angle MaximumSearchRotation);
public record MotionLimits(ErrorBounds Translation, Angle MaximumRotation,
    double MaximumRelativeScaleError, TimeSpan MaximumTimestampSkew,
    bool RequireSettled, TimeSpan MaximumEncoderGap,
    double MaximumSpeedMillimetersPerSecond,
    double MaximumAccelerationMillimetersPerSecondSquared);
public record OutputGrid(string CommonFrame, LengthUnit Unit, Point2 Origin,
    Length PixelStepX, Length PixelStepY, Point2 PhaseAnchor, uint TileCoreSize,
    uint Halo, uint MaximumLod, L<string> Channels);
public record MosaicProfile(ProfileId Id, Revision Revision, ValueRef Source,
    TransformModel RegistrationModel, RegistrationRoute Route,
    MotionEvidencePolicy MotionEvidencePolicy, MatchPolicy? Match,
    IndependentValidationPolicy IndependentValidation, ErrorBounds? ResidualLimits,
    Length? MaximumClosureResidual, MotionLimits? MotionLimits,
    Length? MaximumPriorTranslation, Angle? MaximumPriorRotation,
    DisplayBlend DisplayBlend, uint MaxConcurrency, bool AllowPartialDiagnostic,
    bool DiagnosticOnly, L<RectD> ProtectedRegions, L<RectD> AllowedSeamRegions,
    TimeSpan MaximumPlanningSnapshotAge);
public record ResourceBudget(long CpuMilliseconds, long MemoryBytes,
    long LogicalReadBytes, long DecodedBytes, ulong TileCount,
    uint MaxSourceLeases, uint MaxNativeHandles);
public record MosaicRequestInput(MosaicRequestId RequestId, MosaicOperationId OperationId,
    AttemptId AttemptId, Revision ParentRevision, Revision AlgorithmRevision,
    DeviceScope Devices, L<ExpectedFov> ExpectedFovs, L<ActualFov> ActualFovs,
    L<TilePlanEntry> TilePlan, MosaicRegistrationRef? Registration,
    RegistrationPlanningSnapshot? PlanningSnapshot, MotionCompensationRef? Compensation,
    MosaicProfile Profile, MosaicPurpose Purpose, OutputGrid Grid,
    PermissionScopeId PermissionScopeId, DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record MosaicRequest(MosaicRequestInput Input);
// 唯一 Create(MosaicRequestInput) 校验并防御性复制；直接构造亦执行相同结构校验。
public record MosaicError(MosaicErrorCode Code, string FieldPath,
    L<string> SourceIds, L<DiagnosticId> DiagnosticIds);
public record ValidationResult(bool IsValid, L<MosaicError> Errors);
public record PoseEvaluation(PlanarPoint? Position, Transform2D? Transform,
    PoseStatus Status, CellId? CellId, L<NodeId> NodeIds, L<double> Weights,
    ConditionId? ConditionId, L<MosaicError> Errors);
public record TilePosePlan(TileId TileId, CaptureIntent Intent, PlanarPoint Target,
    AxisPosition? EstimatedEncoderInput, PoseEvaluation Evaluation);
public record ObservedFramePose(TileId? TileId, FovId FovId, FrameRef Frame,
    MotionPoseEvidence? Motion, PoseEvaluation Evaluation);
public record SourceWorkset(uint Sequence, L<FovId> Sources,
    L<PixelRect> Windows, long EstimatedBytes);
public record ResourceLedger(long PlannedBytes, long CurrentBytes, long PeakBytes,
    long CpuMilliseconds, long LogicalReadBytes, long DecodedBytes,
    ulong TilesRendered, uint ActiveSourceLeases, uint OutstandingOutputLeases,
    uint NativeHandles, uint PendingPortCalls, uint PeakConcurrency,
    long CacheBytes, ulong CacheHits, ulong DroppedNotifications,
    string? CancellationStage, DateTimeOffset StartedUtc,
    DateTimeOffset? NativeDrainedUtc, DateTimeOffset? InternalReleasedUtc,
    DateTimeOffset? AllOutputReleasedUtc);
public record MosaicPlan(ValidationResult Validation, L<TilePosePlan> TilePoses,
    L<SourceWorkset> SourceWorksets, RectD? ProjectedBounds,
    ResourceLedger Resources, L<MosaicError> Errors);
public record ResidualEvidence(ErrorBounds Bounds, uint SupportCount,
    LengthUnit Unit, L<ValueRef> Sources, bool Independent);
public record MatchPoint(Point2 Source, Point2 Target);
public record MatchObservation(FovId Source, FovId Target, uint CandidateIndex,
    double Score, L<MatchPoint> Correspondences, ResidualEvidence Residual,
    string MethodId, Revision MethodRevision);
public record GeometryEdge(FovId Source, FovId Target, Transform2D Transform,
    MatchObservation? Match, ResidualEvidence? ClosureResidual);
public record FovGeometry(FovId FovId, Transform2D? Prior,
    Transform2D? VisualCorrection, Transform2D? Final, PoseEvaluation Pose,
    ResidualEvidence? PriorResidual, ResidualEvidence? VisualResidual,
    PlanarPoint? DerivedImagePosition, MotionQualification MotionQualification,
    CovarianceAvailability Covariance,
    L<MosaicError> Errors);
public record MosaicComponent(ComponentId Id, L<FovId> Sources,
    string? CommonFrame, GeometryStatus Status, L<FovGeometry> Geometry,
    L<GeometryEdge> Edges, ResidualEvidence? Validation);
public record CoverageReport(CoverageCompleteness Completeness, uint ExpectedCount,
    uint CapturedCount, L<FovId> Missing, L<TileId> Skipped, L<RectD> Holes);
public record PurposeDecision(MosaicPurpose Purpose, Eligibility Eligibility,
    L<MosaicError> Reasons);
public record SourceContribution(FovId Source, FrameRef Frame, PixelRect SourceWindow,
    RectD OutputSupport, SamplingKernel Kernel, MaskRef? Mask,
    ObservationRole Role, ContributionKind Kind, uint StackingOrder);
public record TileKey(Revision DirectoryRevision, uint Lod, long X, long Y,
    MosaicPurpose Purpose, string Channel);
public record MosaicManifestRef(string ManifestId, Revision Revision,
    ContentDigest Digest, PermissionScopeId PermissionScopeId);
public record VirtualMosaicManifest(MosaicManifestRef Reference, DeviceScope Devices,
    OutputGrid Grid, L<ActualFov> Sources, L<FovGeometry> Geometry,
    L<TilePosePlan> TilePoses, L<PurposeDecision> Purposes,
    RegistrationPlanningSnapshot? RegistrationSnapshot, MotionCompensationRef? Compensation,
    MosaicProfile Profile, Revision AlgorithmRevision, L<SourceContribution> Contributions);
public record SeamResult(SeamStatus Status, L<RectD> Conflicts,
    L<ValueRef> DisplaySources, L<SourceContribution> Contributions);
public record MosaicResult(MosaicRequestId RequestId, MosaicOperationId OperationId,
    AttemptId AttemptId, Revision AlgorithmRevision, ExecutionStatus ExecutionStatus,
    L<MosaicComponent> Components, CoverageReport Coverage,
    L<PurposeDecision> PurposeEligibility, L<TilePosePlan> TilePoses,
    L<ObservedFramePose> ObservedPoses, VirtualMosaicManifest? Manifest,
    SeamResult? Seam, ResourceLedger Resources, L<MosaicError> Errors);
public record MosaicTileRequest(MosaicOperationId OperationId, MosaicManifestRef Manifest,
    TileKey Key, PermissionScopeId PermissionScopeId, DateTimeOffset DeadlineUtc,
    ResourceBudget Budget);
public record MosaicTileResult(TileStatus Status, IMosaicTileLease? Lease,
    ResourceLedger Resources, L<MosaicError> Errors);
public record TileOperationMetadata(TileStatus? Status, OutputDeliveryState Delivery,
    TileKey Key, FrameRef? Frame, L<SourceContribution> Contributions);
public record MosaicOperationStatus(MosaicOperationId OperationId,
    OperationKind? Kind, QueryAvailability Availability, ExecutionState? State,
    MosaicResult? Runtime, CalibrationSolveResult? Solve,
    CalibrationValidationResult? Validation, CalibrationPublishResult? Publish,
    TileOperationMetadata? Tile, ResourceLedger? Resources, L<MosaicError> Errors);
public record DrainReceipt(DrainStatus Status, L<MosaicOperationId> ActiveOperations,
    uint PendingPortCalls, uint OutstandingOutputLeases, L<MosaicError> Errors);
public record ServiceLimits(uint MaxActiveOperations, uint MaxTerminalRecords,
    TimeSpan TerminalRetention, uint MaxOutstandingTileLeases, long MaxCachedBytes,
    uint NotificationCapacity, long MaxManifestBytes, TimeSpan MaxObservationWait,
    uint MaxPendingPortCalls, long MaxRequestBytes);
public record MosaicModuleOptions(Guid SessionEpoch, IMosaicFramePort FramePort,
    IMosaicCoordinatePort CoordinatePort, IRegistrationAdapter? RegistrationAdapter,
    IMosaicAssetPort AssetPort, IMosaicCalibrationAdapter? CalibrationAdapter,
    IMosaicDiagnostics Diagnostics, TimeProvider Clock, ServiceLimits ServiceLimits,
    IMosaicProgressSink? ProgressSink);
public record MosaicCallReply<T>(MosaicOperationId OperationId,
    ObservationStatus Observation, T? Result, ResourceLedger Resources,
    L<MosaicError> Errors) where T : class;
public record FrameReadRequest(FrameRef Source, PixelRect Window,
    PermissionScopeId PermissionScopeId, DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record FrameLeaseResult(IFrameLease? Lease, ResourceLedger Resources,
    L<MosaicError> Errors);
public record CoordinateMapRequest(CoordinateChain Chain, L<Point2> Points);
public record CoordinateMapResult(L<Point2> Points, L<MosaicError> Errors);
public record RegistrationWork(MosaicRequest Request, MosaicPlan Plan,
    L<IFrameLease> Leases);
public record RegistrationWorkResult(L<FovGeometry> Geometry,
    L<MatchObservation> Matches, ResourceLedger Resources, L<MosaicError> Errors);
public record TileRenderWork(MosaicTileRequest Request, VirtualMosaicManifest Manifest,
    L<IFrameLease> Leases);
public record TileRenderResult(ITileBufferLease? Buffer, ResourceLedger Resources,
    L<MosaicError> Errors);
public interface ITileBufferLease : IAsyncDisposable
{
    FrameRef Frame { get; }
    ReadOnlyMemory<byte> Pixels { get; }
    IReadOnlyList<SourceContribution> Contributions { get; }
}
public record CommonOriginObservation(PlanarPoint Position, ValueRef LocalMethod,
    L<PointId> PointIds, ErrorBounds Bounds);
public record ReferencePoint(PointId Id, PlanarPoint Position);
public record MosaicTargetReference(ValueRef Certificate, string CommonFrame,
    L<ReferencePoint> Points, ValueRef Installation, ValueRef OriginAndDirection,
    double TemperatureCelsius);
public record LocalPointObservation(PointId Id, Point2 Pixel, PlanarPoint Local,
    ValueRef Method, ErrorBounds Bounds);
public record MosaicObservationGroup(PhysicalGroupId Id, ExposureId ExposureId,
    string CameraId, FrameRef Frame, FovOpticalCalibrationRef Optical,
    L<LocalPointObservation> Points, MotionPoseEvidence Motion,
    CommonOriginObservation? CommonOrigin, NodeId? FitNodeId, ContentDigest Digest);
public record CalibrationPartition(Revision Revision,
    L<PhysicalGroupId> FitGroups, L<PhysicalGroupId> HoldoutGroups);
public record CameraBasis(string CameraId, Transform2D RegisteredLocalToCommon);
public record GridNodeSpec(NodeId Id, ConditionId ConditionId, AxisPosition Position);
public record GridCellSpec(CellId Id, ConditionId ConditionId,
    NodeId N00, NodeId N10, NodeId N01, NodeId N11);
public record RegistrationGridSpec(L<Length> AxisX, L<Length> AxisY,
    L<GridNodeSpec> Nodes, L<GridCellSpec> Cells, L<ConditionDomain> Conditions,
    L<CameraBasis> Cameras, L<string> ResidualComponentIds);
public record CalibrationPurposeLimits(MosaicPurpose Purpose, ErrorBounds Holdout,
    Length MaximumCorrection, Angle MaximumRotation, double MaximumRelativeScaleError);
public record MosaicCalibrationProfile(ProfileId Id, Revision Revision, ValueRef Source,
    Revision MethodRevision, L<CalibrationPurposeLimits> PurposeLimits,
    double MaxConditionNumber, uint MinGroupsPerNode, Length MaxNodeSpread,
    Length MaximumNodePositionDeviation,
    MotionLimits Motion, ValueRef LocalObservationMethod,
    ValueRef CommonOriginMethod, TimeSpan MaximumSnapshotAge);
public record MosaicCalibrationRequest(MosaicOperationId OperationId,
    AttemptId AttemptId, RegistrationMethod Method, DeviceScope Devices,
    MosaicTargetReference Reference, L<FovOpticalCalibrationRef> OpticalAssets,
    L<MosaicObservationGroup> Groups, CalibrationPartition Partition,
    RegistrationGridSpec Grid, MosaicCalibrationProfile Profile,
    PermissionScopeId PermissionScopeId, DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record NodeFitEvidence(string CameraId, NodeId NodeId,
    L<PhysicalGroupId> Groups, L<PlanarPoint> Residuals, ErrorBounds Spread);
public record MosaicRegistrationCandidate(AssetId Id, Revision Revision,
    ContentDigest Digest, RegistrationMethod Method, DeviceScope Devices,
    string CommonFrame, L<CameraField> Fields, L<FovOpticalCalibrationRef> OpticalAssets,
    MosaicTargetReference Reference, CalibrationPartition Partition, L<MosaicObservationGroup> Groups,
    MosaicCalibrationProfile Profile, L<NodeFitEvidence> FitEvidence,
    Revision AlgorithmRevision);
public record CalibrationSolveResult(MosaicOperationId OperationId, SolveStatus Status,
    MosaicRegistrationCandidate? Candidate, ResourceLedger Resources, L<MosaicError> Errors);
public record CalibrationValidationRequest(MosaicOperationId OperationId,
    MosaicRegistrationCandidate Candidate, L<MosaicObservationGroup> HoldoutGroups,
    MosaicCalibrationProfile Profile, PermissionScopeId PermissionScopeId,
    DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record CellValidation(string CameraId, ConditionId ConditionId, CellId CellId,
    L<PhysicalGroupId> Groups, ErrorBounds Bounds, L<CalibrationPurposeLimits> Limits,
    bool Passed, L<MosaicError> Errors);
public record MosaicValidationEvidence(ContentDigest Digest,
    ContentDigest CandidateDigest, ContentDigest PartitionDigest,
    L<CellValidation> Cells, bool Independent, DateTimeOffset CompletedUtc,
    ValueRef Method, L<MosaicError> Errors);
public record CalibrationValidationResult(MosaicOperationId OperationId,
    ValidationStatus Status, MosaicValidationEvidence? Evidence,
    ResourceLedger Resources, L<MosaicError> Errors);
public record CalibrationPublishRequest(MosaicOperationId OperationId,
    AssetPublishId PublishId, MosaicRegistrationCandidate Candidate,
    MosaicValidationEvidence Validation, PermissionScopeId PermissionScopeId,
    DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record MosaicAssetPublishQueryRequest(MosaicOperationId OperationId,
    AssetPublishId PublishId, PermissionScopeId PermissionScopeId,
    DateTimeOffset DeadlineUtc);
public record CalibrationPublishResult(AssetPublishId PublishId,
    AssetPublishStatus Status, MosaicRegistrationRef? ArtifactRef,
    bool QualificationIssued, L<MosaicError> Errors);
public record MosaicRegistrationArtifact(MosaicRegistrationCandidate Candidate,
    MosaicValidationEvidence Validation);
public record RegistrationReadRequest(MosaicRegistrationRef Reference,
    DeviceScope Devices, MosaicPurpose Purpose, PermissionScopeId PermissionScopeId,
    DateTimeOffset DeadlineUtc);
public record RegistrationReadResult(MosaicRegistrationArtifact? Artifact,
    MosaicQualificationRef? Qualification, ResourceLedger Resources, L<MosaicError> Errors);
public record MosaicProgress(MosaicOperationId OperationId,
    MosaicRequestId? RequestId, AttemptId? AttemptId, Revision Revision,
    ulong Sequence, string Stage, ulong Processed, ulong? Total);
public record MosaicDiagnostic(DiagnosticId Id, MosaicOperationId? OperationId,
    FovId? FovId, ComponentId? ComponentId, TileKey? TileKey,
    MosaicErrorCode Code, string FieldPath, string DetailKey,
    DateTimeOffset AtUtc, ResourceLedger? Resources);
```

枚举的精确整数值如下；未知整数一律结构拒绝，不按默认或“最近值”处理。MosaicErrorCode 为 MZ-001～031 按号码映射同名枚举成员；029=AssetPublishUnknown、030=PlanningSnapshotUnavailable、031=ObservationPendingDrain。下列紧凑写法 `Name: A=0,B=1` 等价于 C# `public enum Name { A=0,B=1 }`，不可自行调整顺序。

| enum | 精确值 |
|---|---|
| LengthUnit / TransformModel | `Pixel=0,Micrometer=1,Millimeter=2,Meter=3` / `Rigid=0,Similarity=1,Affine=2,Projective=3` |
| CameraKind / PixelType | `AreaScan=0,LineScan=1` / `Byte=0,UInt16=1,Int16=2,Float32=3` |
| PixelLayout / ImageOrientation | `Interleaved=0,Planar=1` / `Identity=0,Rotate90=1,Rotate180=2,Rotate270=3,MirrorX=4,MirrorY=5` |
| MosaicPurpose / RegistrationRoute | `GeometryDiagnostic=0,Display=1,Detection=2,Measurement=3` / `PriorOnly=0,PairBundle=1` |
| MotionEvidencePolicy / IndependentValidationPolicy | `Required=0,Optional=1,NoMotion=2` / `Off=0,Diagnostic=1,RequiredForDetection=2,RequiredForMeasurement=3` |
| DisplayBlend / RegistrationMethod | `None=0,Stacking=1,Feather=2,NamedMultiBand=3` / `AreaScanXyResidualGrid=0,LineScanTimed=1` |
| AxisDirection / CaptureIntent | `Positive=0,Negative=1,Unknown=2,NotRequired=3` / `Capture=0,Skip=1` |
| PoseStatus / CovarianceAvailability | `Predicted=0,Observed=1,PredictionUnavailable=2,Rejected=3` / `NotProvided=0` |
| MotionQualification | `Qualified=0,DisplayOnly=1,Rejected=2,NoMotion=3` |
| GeometryStatus / CoverageCompleteness | `Qualified=0,DiagnosticOnly=1,Rejected=2` / `Complete=0,Partial=1,Empty=2` |
| Eligibility / SeamStatus | `Usable=0,NotQualified=1,Rejected=2` / `NotApplied=0,Stacked=1,Conflict=2` |
| SamplingKernel / ContributionKind | `Nearest=0,Bilinear=1` / `Original=0,Resampled=1,Display=2` |
| ExecutionStatus / ExecutionState | `Completed=0,Partial=1,Cancelled=2,TimedOut=3,Failed=4,Unknown=5` / `Created=0,Validating=1,Planned=2,Running=3,Publishing=4,Draining=5,DrainUnknown=6,Drained=7,ResourcesReleased=8,Terminal=9,OutputHeld=10` |
| OperationKind / QueryAvailability | `Runtime=0,CalibrationSolve=1,CalibrationValidate=2,CalibrationPublish=3,Tile=4,AssetPublishQuery=5` / `Active=0,Terminal=1,NotFound=2,Expired=3` |
| TileStatus / OutputDeliveryState | `Available=0,NotFound=1,Rejected=2,Cancelled=3,TimedOut=4,Unknown=5` / `None=0,ServiceOwned=1,Delivered=2,Released=3` |
| SolveStatus / ValidationStatus | `CandidateReady=0,Rejected=1,Failed=2,Cancelled=3,TimedOut=4,Unknown=5` / `Passed=0,NotEvaluated=1,Rejected=2,Failed=3,Cancelled=4,TimedOut=5,Unknown=6` |
| AssetPublishStatus / DrainStatus | `Published=0,NotFound=1,Rejected=2,Unknown=3` / `Drained=0,WaitCancelled=1,DrainUnknown=2` |
| ObservationStatus | `Returned=0,PendingDrain=1,WaitCancelled=2` |

字段约束与空形状：

- Revision>=1；坐标/矩阵/质量指标有限，Length/Area 单位与 frame 声明一致；ResourceBudget 所有值正且有限，Core v0.3 不开放 Unlimited。FrameRef stride 对 interleaved 为一行多通道字节数、planar 为单通道一行，CapacityBytes>=StrideBytes*Height*(planar?Channels:1)，checked；像素大小 Byte=1/UInt16=2/Int16=2/Float32=4。ValidWindow 非空且在原帧内；Mask 的源 ID/revision 与帧一致且 ValidPixelCount<=窗口像素数；没有 mask 表示整个 ValidWindow 有效。Pixels 的 endian/type/layout 必须与描述一致，裁剪 lease 使用自身真实窗口 stride。
- DeviceScope Cameras 按 CameraId 唯一；跨轴组/相机使用各自完整 identity；Candidate.Fields 按 CameraId 唯一并覆盖声明相机，每相机Field不复制另一相机的A。Condition温度两端同时为空表示资格明确不依赖温度，否则均非空且Min<Max；最后最大端IncludeMaximum=true；NotRequired仅用于明确不依赖方向的子场。Cells四角N00/N10/N01/N11必须同ConditionId。Field.Cell.IsSupported只说明拟合集/节点足够，不是资格；实际有效cell需join Artifact.Validation.Cells 的Passed独立结果和Qualification.Cells的对应用途界。验证Digest只在Artifact.Validation/Qualification闭包中，不放Candidate.Field节点/cell内，避免验证绑定CandidateDigest却又被Candidate包含的摘要循环。Candidate内容在验证后不可改IsSupported/节点，否则生成新Candidate再验证。
- MosaicRequestInput.Purpose/Profile/Devices/Grid/Permission 和各集合始终存在。Profile.Route=PriorOnly 时 Match=null；PairBundle 时 Match 必填。Detection/Measurement 必有 ResidualLimits、MaximumClosureResidual 和适用 MotionLimits；NoMotion 的实际 FOV 必有 StaticPrior 而 Motion=null，移动采集则相反。Optional 只能诊断/显示；不伪造 motion=零。实际 Motion 是曝光对应实测，Tile 的 EstimatedEncoderInput 仍只是预测。Compensation!=null 首版恒返回 MZ-026，不存在可选插件/待程序员决定的求值方法；基线 G0/d 已包含批准组件，不重复补偿。v0.3 LineScanTimed 不求物理 Pose；线扫仅用附录 C 的 v0.4 专用入口。
- **同步资产来源：** 宿主先以公开AssetPort.ResolveAsync(RegistrationReadRequest)或已保存的精确离线artifact/qualification读取，校验hash闭包后构造RegistrationPlanningSnapshot放入Input。Snapshot.Artifact是不可变完整Candidate+Validation；实际数值路径为Artifact.Candidate.Fields，资格为Snapshot.Qualification。Reference必须与Candidate.Id/Revision/Digest/Devices/CommonFrame完全一致，Qualification.ArtifactDigest/ValidationDigest与两个重算内容摘要一致，Reference.QualificationRevision与Qualification.Identity.Revision一致。Validate/Plan不调用端口/不借帧/不堵塞IO，不猜latest。以Clock核对资格时域、Revoked、permission、配置/条件、node/cell与独立验证join；ObservedUtc不得未来，年龄不超Profile.MaximumPlanningSnapshotAge（正有限）。合法离线快照只支持预测，不授新的生产权限。
- Registration 需要求值而 PlanningSnapshot=null 时，Validate.IsValid=false、Errors 含 MZ-030；Plan 返回该 Validation、Errors，同一完整 TilePlan 的每项 Evaluation=PredictionUnavailable、数值/cell/condition=null，Nodes/Weights 空；SourceWorksets 空、ProjectedBounds=null、Resources 为零活动规划账本。没有 Registration 的显式像素诊断可按 ActualFov.StaticPrior 索引；需要连续位置的条目仍 PredictionUnavailable。结构非法（重复 ID/布局/参数）时 Plan 的 TilePoses 也空，避免输出被篡改计划。未解析快照与单条 EstimatedEncoderInput/方向未知不同：后者仅该条 PredictionUnavailable，其它合法条目仍求值。Plan 只得 Predicted，Observed 留执行。
- M-C1精确参数对应§4目录：ResidualLimits=RMS/P95/P99/max长度四门，MaximumPriorTranslation/Rotation为先验界，Match的Overlap/Support/Search为匹配界，Grid的TileCoreSize/Halo/MaximumLod/PhaseAnchor是网格参数。MaximumPlanningSnapshotAge、MaxObservationWait为软件有限时限，值由宿主Profile/ServiceLimits显式给定，不借例子默认。Optical=null仅合法于显式像素/分离图诊断，不开放物理用途；物理ActualFov须有自身Optical和对应asset闭包。GeometryDiagnostic可以无Global共frame，仅原始目录；Invalid未知ObservationRole不能融合。Profile.MaximumPlanningSnapshotAge和CalibrationProfile.MaximumSnapshotAge都是正有限，标定后者只用于验证证据CompletedUtc至发布的最大年龄（Publish取Candidate.Profile该字段），不是Native强制退出时限。
- Request Create做纯结构校验/防御复制并返回不可变值；纯业务校验失败由Validate/Plan的Errors表达。Grid PixelStepX/Y正、单位相同且与Unit一致；Origin/PhaseAnchor.Column/Row在声明共同frame的网格像素坐标，转换共同物理点时用显式PixelStep，不能将Point2的无量纲坐标误作mm。Transform.GlobalBasis只接受XY仿射(底行为0,0,1)，A为固定局部平面→共同平面合法链；M-C1不解投影/机器人自由度。
- Execute 接纳前以及结果/manifest交付前，用输入 Registration 的 exact ref 加 PermissionScopeId/Deadline 重新权威 Resolve；GetTile 对历史 manifest 的 exact RegistrationSnapshot.Reference 同样在借源前和输出 lease 交付前复核。当前资格 identity/digest/authority revision、content hash、设备、有效cell/条件/用途须与冻结快照一致；变化/撤销/过期/权限失效即拒绝 MZ-013/015/021，不在该 attempt 换新值。Resolve 不会补齐一个缺失 PlanningSnapshot 请求而静默绕过同步 Validate；宿主须显式重构新请求。快照失效/端口不可观察只影响异步执行的相应用途，离线数学结果仍标为预测，无生产授权。
- Plan 的工作集 Windows 与 Sources 等长且按相同次序；纯 Skip 无工作集。Field 数值推导不能用自报摘要当校验，内容摘要按 A.2 重算。连续场求值成功的Nodes/Weights恰四项；合法静态NoMotion/像素先验成功时两清单均空，不能伪造cell；Rejected/Unavailable 数值为空且 Nodes/Weights 空。ResourceLedger 全计数非负，StartedUtc 是接纳/纯计划时刻，未排空的三个 released 时刻为空；InternalReleased 不代表 AllOutputReleased。资源峰值包含 pending call/迟到候选与 output，零活动账本并非伪造“真实测得零误差”。
- MosaicResult仅终态；失败/取消/超时/Unknown Manifest=null、Seam=null，诊断Components/Errors可非空；纯计划Manifest也null。Coverage分母ExpectedCount保持原Expected全集；完整TilePlan请求要求每条Tile（含Skip）有唯一ExpectedFov.TileId，CapturedCount只计Actual中身份/数据有效的源，Skip不计。Geometry/coverage/Purpose独立，物理闭包缺失不得Detection/Measurement Usable。Manifest为null的失败结果不丢输入，宿主保存原Request；成功Motion/光学/资源通过Manifest.Sources/Geometry/RegistrationSnapshot回溯。q_img仅DerivedImagePosition的独立观测，未知null。
- MosaicCallReply.Result 仅 Observation=Returned 非空，PendingDrain/WaitCancelled 为空且保留 OperationId、Resources、Errors（含MZ-031）。Returned 是方法结果可观察，不等价于成功。Tile Available 唯一非空 lease；Query 的 TileOperationMetadata 绝无 lease/Memory，Kind=Tile 时 Tile 必填、Resources必填，State可能 OutputHeld，Availability=Active 直至该输出lease归还。其它Kind仅对应Runtime/Solve/Validation/Publish非空（AssetPublishQuery复用Publish结果字段）；执行中全结果为空而 Resources 非空。NotFound/Expired 时 Kind/State/各result/Tile/Resources全部null。
- 结构拒绝且未接纳仍返回Returned包装的该方法Rejected/Failed结果和零活动账本，Query为NotFound；它不伪造Running/Draining。Tile重复同ID拒绝不改原registry；Frame.Read/Asset.Resolve错误如实给Errors，public包装不抛出取消来绕过观察/资源语义。运行时同ID同摘要的附加等待者取消只结束自己的WaitCancelled，不请求原执行取消；首调用令牌控制原业务，两个等待者各自有限观察截止。
- Solve CandidateReady 唯一 Candidate 非空且所有 Fields 为未资格内容；无 CommonOrigin 时不尝试猜反算。Groups/Partition 固定完整组，FitNodeId 仅 Fit 组必填，Holdout为null；Fit组必须显式绑定FitNodeId，按Profile.MaximumNodePositionDeviation检查实际Encoder到指定node的XY分量差（同轴单位）；超限整组拒绝，不按最近格归组。节点残差是实测CommonOrigin减GlobalBasis在该实际Encoder的预测，按组稳定ID排序求分量均值并绑定到GridSpec该node坐标；位置偏差上界由Profile限制，其cell插值误差仍由独立Holdout证明，不能用残差均值掩盖采样位置散布。Candidate.AlgorithmRevision固定=request.Profile.MethodRevision。NodeId 可在不同相机共享但必须相机各自拟合。CalibrationPurposeLimits 明确用途各自门，无隐藏“还须”参数。Passed 的 Validation 唯一 Evidence非空；其它状态 Evidence可为诊断证据（只记录失败cell，Independent如实），不得据其内容发布。Publish只接独立Passed、Errors空的精确Candidate/Partition/Profile闭包，发布域仅Artifact.Validation.Cells中Passed=true的cell；其它失败cell可以作为诊断留在同artifact，不能放入Qualification.Cells或显示为有效，Published 唯一 ArtifactRef非空且 QualificationIssued 恒 false；Unknown/NotFound/Rejected Ref=null。允许发布的资格候选域来自验证 passed cell 子集，不推全工作区。
- RegistrationReadResult成功Artifact/Qualification非空、Errors空，要求ref.QualificationRevision非空且匹配；未资格Publish返回的ArtifactRef.QualificationRevision=null，不能直接用于生产Resolve。失败两对象null，Resources仍反映IO状态。FrameLeaseResult失败lease=null；TileRenderResult失败Buffer=null；成功退出后的buffer服务所有，用户从不收到ITileBufferLease。Content根self摘要排除规则见A.2，不递归删除依赖摘要。
- 权威AssetPort.Resolve的成功还须确认Artifact.Candidate.OpticalAssets全部精确引用的上游FOV资格当前适用且未撤销，配置/crop/依赖版本闭合；这是显式端口适配责任，不让同步Plan去读上游。任何依赖撤销或无法观察都不能返回成功已资格闭包。Core仍复核引用/内容/单位/用途，不把adapter单一bool当足够几何证据。FovGeometry.MotionQualification独立于组件GeometryStatus和覆盖，NoMotion不伪造速度/反馈/settled。

### A.2 可复算的 Core 编码与摘要

唯一规范名 `mosaic-core-bin-v1`。用于真实请求重复分类与本模块新内容 hash，不替代历史/平台已有摘要。编码是无BOM字节序列：固定头 `4d 5a 43 01`（ASCII MZC +版本字节01），随后一个 UInt32 LE 的入口标签 UTF-8 字节长、标签字节，再一个根值。record的字段顺序严格为 A.1 声明顺序（含明确加入的 MaximumPlanningSnapshotAge），不靠反射枚举顺序、文化或属性名排序。A.1中每个标识 wrapper也是单字段 record，未内联。

| 值 | 唯一字节编码 |
|---|---|
| null / bool | `00` / `01 00`(false) 或 `01 01`(true) |
| string / int32 / uint32 | `02 + u32字节长 +严格UTF-8` / `03+i32 LE` / `04+u32 LE` |
| int64 / uint64 / double | `05+i64 LE` / `06+u64 LE` / `07+IEEE754 binary64 LE`，-0编码+0，非有限拒绝 |
| DateTimeOffset / TimeSpan | `08+i64 LE UTC ticks相对1970-01-01T00:00:00Z` / `09+i64 LE Ticks`，精度100ns，不截毫秒；时间偏移先转UTC |
| Guid / enum | `0a+16字节`，按 `Guid.ToString("N")` 两hex一byte的文本顺序，不用ToByteArray混合端序 / `0b+类型名(string编码)+i32 LE显式枚举值` |
| record / list / set | `0c+类型名(string编码)+u32字段数+逐字段编码` / `0d+u32项数+按原顺序逐项编码` / `0e+u32项数+按完整元素编码字节逐字节无符号词典序排列后逐项编码` |
| 类型名/集合/nullability | 类型名为 A.1精确 Name，无namespace/程序集版本/泛型别名；nullable有值直接编码原值，无额外标签，null用00。list空为0d00000000，set空为0e00000000，不能用null代替；所有Length/Revision/ID都有record标签/自身字段；没有object运行时分支 |

每个L<T>默认list。以下按record类型/字段指定set，其余不得排序：DeviceScope.Cameras；RegistrationField.Nodes/Cells/Conditions/ResidualComponentIds；MosaicQualificationRef.Cells；QualifiedCell.Purposes；MosaicRequestInput.ExpectedFovs/ActualFovs/TilePlan；RegistrationGridSpec.Nodes/Cells/Conditions/Cameras/ResidualComponentIds；CalibrationPartition.FitGroups/HoldoutGroups；MosaicCalibrationRequest.OpticalAssets/Groups；MosaicCalibrationProfile.PurposeLimits；MosaicRegistrationCandidate.Fields/OpticalAssets/Groups/FitEvidence；CalibrationValidationRequest.HoldoutGroups；MosaicValidationEvidence.Cells；CellValidation.Groups/Limits；MosaicTargetReference.Points；MosaicObservationGroup.Points；CommonOriginObservation.PointIds。set按完整编码排序后字节重复或领域稳定ID重复均拒绝，不dedup。RepeatResiduals、拟合残差组对应数组、链Edges、工作集Sources/Windows、贡献覆盖顺序都是list。ResidualNode.Groups/RepeatResiduals、NodeFitEvidence.Groups/Residuals等长同序，绑定关系不丢。

根投影全部按 A.1字段类型递归编码，无 self hash/隐藏字段：
- Runtime 输入标签 `runtime`，根 MosaicRequestInput 的全部字段（含 OperationId、PlanningSnapshot、PermissionScopeId、DeadlineUtc、Budget）；MosaicRequest 只作为 Input wrapper，不额外编码。
- `calibration-solve` 根 MosaicCalibrationRequest；`calibration-validate` 根 CalibrationValidationRequest；`calibration-publish` 根 CalibrationPublishRequest；`tile` 根 MosaicTileRequest；`publish-query` 根 MosaicAssetPublishQueryRequest。均含本入口全部字段，外部取消令牌/通知/scheduler/Clock/service options不在根内。改变 deadline或预算/权限视为不同输入，不能同ID静默扩展预算；PublishId 的**存储幂等**键另为同PublishId+CandidateDigest+ValidationDigest，查询read attempt改变deadline不重写内容。
- 新内容标签 `observation-group` 根 MosaicObservationGroup 仅删根 Digest；`registration-candidate` 根 MosaicRegistrationCandidate 仅删根 Digest；`validation-evidence` 根 MosaicValidationEvidence 仅删根 Digest；`virtual-manifest` 根 VirtualMosaicManifest，其中 Reference 根子record删除 Digest，保留 ManifestId/Revision/PermissionScopeId，其余全部原字段。删字段后的record字段数减1，其它字段仍原序。所有嵌套FrameRef/ValueRef/依赖CandidateDigest/ValidationDigest/Qualification摘要都保留，不递归删除名为Digest的字段，不hash自己再回填。Qualification/content不同Owner的既有hash原样消费，不在此重算历史资格。
- 验证证据的 PartitionDigest 按标签 `calibration-partition` 和根 CalibrationPartition 的全部字段编码，再 SHA-256；Partition 无 self 字段，不省字段。Candidate.Reference 保留精确实测点表/安装证据完整输入，不能仅用一个不足以离线复核的ref代替；它的外部Certificate摘要原样保留。
- 编码长度/数量为UInt32且checked，总长度受ServiceLimits.MaxRequestBytes与Budget.MemoryBytes约束；超限在接纳/借帧前MZ-010。字符串不trim、不大小写折叠、不Unicode归一化；严格UTF-8拒绝未配对surrogate，零值wrapper非法，领域用显式单位，禁止为了摘要自动换mm/m。Digest本身是编码后SHA-256的小写hex。
- 无Budget的publish-query编码仅受ServiceLimits.MaxRequestBytes；它的IO占用受实例MaxPendingPortCalls与有限deadline。编码复算只检查结构/有限数值/格式，不读Clock、不检查时域资格；调用接纳另做deadline/资格。故固定的过期向量仍可编码，绝不等于可以执行。

独立向量（编码试验，不是产品测试）：按上表对真实 `publish-query` 请求编码，OperationId=(Guid `00000000-0000-0000-0000-000000000001`, Sequence=1)、PublishId="p"、PermissionScopeId="s"、DeadlineUtc=`1970-01-01T00:00:00Z`。输入只用于确定性编码断言，不作真实准入请求，deadline已过。完整hex与SHA-256见后面的向量行；第二实现须仅按本规范复算而非调用受测编码器生成期望。另须断言相同UTC不同offset相同、-0/+0同编码、list调序不同、set调序相同、set重复拒绝、根self字段改变不影响内容摘要而嵌套依赖digest改变必影响、同runtime deadline/预算/权限改变摘要必不同。

向量长186bytes，完整hex（下面三行拼接，无换行字节）：

```text
4d5a43010d0000007075626c6973682d71756572790c021e0000004d6f7361696341737365745075626c69736851756572795265717565737404000000
0c02110000004d6f736169634f7065726174696f6e4964020000000a000000000000000000000000000000010501000000000000000c020e00000041737365745075626c697368496401000000020100000070
0c02110000005065726d697373696f6e53636f7065496401000000020100000073080000000000000000
```

SHA-256=`04571fc83515306e24dfee3d50f2564dcfbd8ddcd6b2f04298bc826ad406dbff`。本轮仅用独立inline编码和标准SHA-256核对字节向量，不声明模块编码器/产品测试已执行。
adapter 异步返回意味着其本次 native 已退出并释放自己创建的 native 临时资源；它不得在仍占用输入时抛出 OperationCanceledException/返回取消完成。无法确认退出时保留未完成任务并通过资源状态投影 DrainUnknown；超时只是停止新工作和请求取消。所有端口禁止隐藏后台使用已归还缓冲，跨工作共享 native 必须由 adapter 明确串行计数。服务发布前重新解析资格/权限修订，失效即撤销候选返回；校验和消费不可能原子覆盖外部撤销，结果必须携带资格修订，宿主正式消费/提交前按自己的质量事务再次核验，不声称模块输出永久有效。

进度工作者有界串行 await 回调，请求/排空不等待用户回调；Dispose 清理算法与输出 lease 后取消通知派发，丢弃队列，不等待不响应取消的宿主回调。回调抛异常只写 ProgressDeliveryFailed。可靠终态是具名方法返回值与有界 Query，内容发布未知则回查 AssetPublishId。

## 附录 B：最小 Host 与接收断言

最小 Host 只引用 Core 公共契约及显式端口，不创建 WPF 窗口或 dispatcher；其执行形状与正文 §6 一致。两类独立宿主（大板查看、拼接分析/跨 FOV 检测）使用同一包版本、冻结输入和错误语义接收，不以示例代码或单测替代真实消费验收。

查看 Host先从公开端口或保存离线值取得精确artifact+qualification，组装PlanningSnapshot→固定权限/Clock/SessionEpoch/ServiceLimits→非空TilePlan（可全部Skip）→Validate/Plan（所有IO端口计数0）→Execute检查CallReply.Observation；无Result先Query原ID等待排空→有Result再检查覆盖/用途→GetTile检查观察回执，仅Returned/Available读取并finally归还lease→有限Drain检查零pending/零output→Dispose。没有图像不取tile；Missing/Skip定位计划身份，Blank保留实际覆盖。

分析 Host 使用同包但自己的实例/权限/预算→从原始采样组与公开 FOV 观测构造标定输入→Solve→Validate→显式 PublishUnqualified→原 PublishId 回查未知回执→由外部 Owner 授予资格后再解析精确引用→Execute→逐源/共同 frame/独立误差和覆盖检查→按宿主质量规则消费或阻断→归还 lease/Drain/Dispose。没有资格仍可离线分析候选，不能生成可计量结论；没有标定 adapter 时只消费已发布资产。同一资产输入变更必须建立新 candidate/revision，不回写旧内容。

两 Host 各自在无窗口 Exe 中独立构建；最小失败接收用同 ID 异摘要、全Skip/缺Capture、反馈越域、发布回执未知和持有输出lease后Drain验证。InternalReleasedUtc仅表示该operation的native/port/输入及临时buffer已释放；已交付输出仍持有时保持OutputHeld/Active，不发ResourcesReleased、不发布终态、不淘汰。输出全部真实归还后填AllOutputReleasedUtc，依 §9.2 的 Drained→ResourcesReleased→Terminal 唯一顺序推进。一个operation的ResourcesReleased也不代表其它operation或全服务已释放；全服务DrainReceipt.Drained要求零active、零pending port、零输出租约。

验收断言：

- 无 UI Host 可构造/释放服务、执行请求、查询终态和取 tile；无窗口线程、无隐藏初始化，也无模块私有持久化副作用。
- ProgressSink=null/无订阅者不阻断；Returned结果与Query终态相符，PendingDrain/WaitCancelled绝不冒充业务终态。同步Plan无Asset/Frame/native调用；缺/过期/篡改快照稳定拒绝，保持计划身份。
- 用可控慢订阅者阻塞通知派发时，计算线程、native 排空、`ResourcesReleased` 和执行返回不等待回调；通知缓冲有界且只合并/丢弃中间进度。
- 用抛异常订阅者验证诊断记录 `ProgressDeliveryFailed`，请求结果、取消和清理语义保持不变。
- 对 A/B 两个 attempt 人为制造乱序、重复、revision 不同及终态后迟到通知；宿主忽略无效通知，旧通知不能覆盖新终态。
- API 静态检查确认请求/快照不含取消令牌，且不存在 `IMosaicBuilder`、`BuildAsync`、同步 `Execute` 等第二种调用形式。

这些是实现时必须执行的断言，当前未运行。文档保持DesignReview；M-C1/M-C2/M-C3已获六项软件规格接收，状态ModuleCoreImplementationReady；真实适配/物理/UI及其它未接收方法仍PreparationIncomplete，不宣称整模块完成。

## 附录 C：首版线扫物理拼接增量（Module API Contract v0.4）

本附录冻结线扫方法与新增公开面，不修改 A.1 的 v0.3 构造顺序、A.2 标签/186-byte 向量或已接收 M-C1/M-C2/M-C3。v0.4 是显式协商的增量：保留旧接口，增加专用接口和同名工厂重载；旧请求不得附带扩展字典或把 LineScanTimed 参数包当成新请求。当前只提交文档规格，新增切片的主控接收/真实适配/现场资格分开记录于 C.7。

### C.1 官方依据、支持拓扑与禁止路线

方法固定名为 `FirstLineEncoderTranslationMeshV1`。依据为项目内 HALCON **26.05.0.0** 的 [Calibration 专业章节](../../../halcon算子手册/operators/toc_calibration.html) 中 Camera parameters、The Used 3D Camera Model 和 Further Limitations，以及 [image_points_to_world_plane](../../../halcon算子手册/operators/image_points_to_world_plane.html)、[project_3d_point](../../../halcon算子手册/operators/project_3d_point.html)。2026-10-11 直接核读本地正文及公式，并读取 [MVTec 同版官方章节](https://www.mvtec.com/doc/halcon/2605/en/toc_calibration.html)核对线扫物理假设。官方资料只作方法依据，不证明本项目精度；不依赖 README/营销/其它版本实现。

来源固定到本地 toc_calibration.html SHA-256=`2fc77e496a286bb9ae87ccad64a5f1ee57fa9e685e8d698e78178314db57ff56`；image_points_to_world_plane=`7077dae12f342048660e7d38659da59c6b7379d90561ee921cd62b22e77b4050`；project_3d_point=`75072695206dd30171a7c115b6a8329bd870bda37056f6158acf49d77cae18af`。资料权利人为 MVTec（页面 Copyright 1996–2026），本轮引用公式语义，未复制上游代码/新增运行库，不修改参考原件。官方在线同版章节用于专业正文复核，实施版本仍以这些本地原件为准。

| 已核官方事实 | 首版决策及限制 |
|---|---|
| HALCON 线扫模型假定相机相对物体直线恒速、姿态恒定、各标定图同运动向量；Vx/Vy/Vz 为相机 frame 的 meter/row；固定相机/移动物体等价于相反运动 | calibration-assets 的局部光学校准仍按其恒速路线完成。mosaic 只取首行光学截线，再以曝光关联实际编码器平移；不能对生产全图调用 row×V 后又加实际位移 |
| 线扫 pose 对应首图像行；投影公式含 `x-t*Vx, y-t*Vy, z-t*Vz`，最终 row=t | 令 row=t=0 消除运动项，得到固定传感器列到参考平面的截线。不是面阵单应性，也不是把 line 模型名换成 area 模型 |
| division 可解析反畸变；polynomial 反解迭代、线扫部分多项式项可观测性受限 | 首版仅 `line_scan_division` / `line_scan_telecentric_division`；polynomial、tilt、TDI/多线融合、滚动面阵、3D 曲面首版 MZ-026，不自动换法 |
| 单相机 telecentric 的 Vz 不可观测；z pose 的标定距离不代表实测距离 | telecentric Vz=0，参考平面 pose 的物理安装与平面适用性须独立证据；不从光学拟合推断板高或共同运动 |
| image_points_to_world_plane 以给定 world-in-camera pose 求视线与 z=0 交点；仅校准图像域内有效 | 原传感器 row=0、原 column（不加半像素）→参考平面，Scale='m'。视线平行平面/背面/域外拒绝；正反投影须在 Profile 数值门内 |

首版支持刚性平面、相机与平面间姿态/距离不随扫描改变、仅 XY 平移、同一连续扫描段单方向。可在批准速度/加速度域内改变行间距，不能在一个段内停滞、折返或跨方向子场；反向扫描是独立段及独立资格条件，不倒排像素或压缩行号。跨相机分别投影/资格后投到同一 common frame，不复制一条截线给另一相机。运行不识别角点/圆点/纹理，不匹配 FOV，不做视觉 DeltaT。建资产/独立验证可使用实测平面靶；生产无纹理仍可运行。

官方 pinhole 方程具体为 `m*u(ũ,pv)=x-t*Vx`、`m*v(ũ,pv)=y-t*Vy`、`m*Focus=z-t*Vz`，其中 `pv=-Sy*Cy`、`ũ=Sx*(column-Cx)`，u/v 是其光学反畸变函数，row=t。t=0 时视线方向为 `(u,v,Focus)`；telecentric 则 `u/Magnification=x-t*Vx`、`v/Magnification=y-t*Vy`，t=0 取固定平行视线。实际平面求交和畸变求值都交 HALCON，不在 Core 复制这些函数。此首行消项成立并不证明时变旋转/Z可用，首版的平面平移条件仍是硬门。

仅原方向、单通道 Byte、原始整幅行布局和 Nearest 输出在首版渲染范围；裁剪租约有明确 origin/stride，但源描述的 Width/Height、row/column 不改。其它像素格式/通道组合、binning/旋转镜像变换、LOD>0、halo>0、辐射/接缝/多带、附加 Compensation 首版均 MZ-026。该限制只针对本线扫增量，不缩小已接收的 v0.3 面阵能力。几何物理用途须独立授予；最近邻显示图本身不成为计量原图。

### C.2 首行截线、逐行时刻与实际位置

资产准备由 mosaic 标定 Owner 完成；上游光学参数只读。`LineGeometryDefinition` 的 `PlaneInCamera` 是参考编码器位置 q_ref 下 **reference plane → camera** 的刚体变换，平面 z=0、右手、米；`PlaneToCommon` 是该 reference plane → common 的固定刚体平面变换（不含运动，不允许投影/缩放自由度）。矩阵只含固定安装关系。相机移动/物体移动的符号由实测基线 G0 的轴→common 方向确定，不能由速度命令或 HALCON V 符号猜测。

1. ProjectLineTraceAsync 对 Optical 精确内容/资格做调用前和返回前权威核对，再经 cv2.image_points_to_world_plane，对 ValidWindow 内每个整数 column j 调用 row=0、Scale='m'，得到参考平面 b(j)。以固定 PlaneToCommon 变为 B(j)。原 CameraParam 的 V 保留，不设零以规避模型合法性；row=0 时运动项自然消失。经过 PlaneInCamera 和 cv2.project_3d_point 正投影，检查 row≈0、column≈j，记录逐列误差。有限值/在前方/交点及有效域均须通过。

   PlaneInCamera 由 `[R00,R01,R02,Tx,R10,R11,R12,Ty,R20,R21,R22,Tz]` 构造 HomMat3D，先核刚体再经 [hom_mat3d_to_pose](../../../halcon算子手册/operators/hom_mat3d_to_pose.html) 生成官方 type-code=0 pose；不猜 Euler 次序，也不让该算子的近似非刚体转换掩盖非法输入。光学 ValidWindow 必须涵盖参考 row0 和这些 columns，否则拒绝此trace定义。
2. trace 是不可变候选，保存每个整数 column 的 B(j)；不拟合任意函数。外部资格前不用于生产。独立靶/留出样本确认 TraceChordBound，覆盖每个整数列间的光学曲线相对弦段的最大误差；光学回投影残差不代替物理留出。首版每列一个 knot，禁止自适应减点或运行时改变间隔。首行 trace 无灰度、无源帧 lease。
3. LineScanArtifact 的 Motion 使用 §5.2A.4 的同一 `P(q)=G0(q)+d(q,conditions)` 数值方法/条件分区/四角双线性规则，新增 LineMotionField 只表达平移子场，不使用面阵 RegisteredLocalToCommon。资产在本模块线扫采样/留出流程中建立，不能把面阵注册资产改个方法 ID 使用；P(q_ref) 与 P(q_row) 必须同一相机、同一条件子场且均在批准 cell 内。
4. 时钟映射保留 source/target domain、epoch、frequency、正有理 scale、offset、有限 source 区间和最大误差。用 checked BigInteger 有理数先完成映射、起止求中点和差值，最后才换成相对秒数/插值权重 double；不得先把巨大绝对 tick 转 double。只在冻结的 TargetDomain/Epoch 内计算，不用 UTC/host arrival/采集序号代替曝光时间。
5. 首版时间定义唯一为曝光中点：`t_row=map((start+end)/2)+EffectiveDelay`。EffectiveDelay 是资产批准的有符号固定时偏，表示曝光时间戳到有效光学曝光的偏移，非临时搜索值；误差含 DelayUncertainty。曝光端点、偏移后的关联时刻和反馈都须在映射域内。T=映射后的曝光时长，t_row 只在相邻两条**实际**同源同 epoch 反馈之间插值：`q_row=(1-a)*q_k+a*q_(k+1)`，`a=(t_row-t_k)/(t_(k+1)-t_k)`。恰好命中反馈时直接用该实际 q；仍检验它两侧适用反馈间隔/误差域，端点缺一侧则该行不可用。
6. 连续行号 r 是原 FrameRef 的 row index，LineCounter 是同一无回卷段内来源可证明且可无损承载的计数，不等同于缓存 row index；mosaic 不展开设备计数。每条行身份包括稳定来源行引用、counter、曝光区间、原行字节 SHA-256。只有全部身份/内容/时序及 RowIndex 相同的重复传输记录可去重；同 ID 异内容 MZ-002，两个不同 row index 复用同一 counter/行引用拒绝。缺 row、counter 非相邻、曝光时刻无序、反馈 Sequence 断口不跨越补线。计数/Boot/Generation/epoch 不可猜回卷。

   当来源是 camera-acquisition C2-RF 时，以上事实只可经 camera §20 的唯一 producer/reader 消费原 ledger snapshot 与 `LineFactPage/LineFactQueryResult`；typed FullPayload/Read/Return仍由camera原root持有。mosaic不把SourceOrdinal/arrival/缓存下标转成r/LineCounter；RowIndexInBlock只有原Owner已证明与这份原FrameRef的行一一对应才可投影。UInt64 RawBits/epoch/wrap/reset/counter及association规则、曝光/clock、完整payload窗口/hash原值保真，精确限制见C.10；多块缺原Frame行映射时拒绝，不新造映射DTO。不能为适配long而截断/转double/跨域拼接/补默认值。

节点的物理前向结果固定为：

```text
W(j,r) = B(j) + P(q_row[r], condition) - P(q_ref, condition)
```

这只加一次实际平移差；B 含参考安装位置，不能再加一个绝对 P(q_ref)。Trace 的 PlaneToCommon 不含 G0/d；V 只参与光学校准和首行投影合法性，不再参与生产行位移。条件/温度变化跨子场、相机安装/Z/旋转改变即新资产/新段，未知平面有效性 MZ-025。生产点阵、圆径、步距或板尺寸均不是这里的默认参数。

**位置和时间门：** MaxFeedbackGap、MaxAxisSkew、MaxSynchronization、Min/MaxSpeed、MaxAcceleration、MaxExposure、MaxRowDisplacement、MinRowAdvance、EncoderResolution 和质量/物理误差预算均由获批 Profile/设备证据给值，本文不造阈值。首版要求反馈 XY 向量具有同一真实采样 tick；分轴不同 tick 不由 mosaic 拼成“同时 XY”，由上游提供可证明的共同采样向量，否则 MZ-020。回差方向依据实际 encoder increment 超过分辨率；未知/相反 MZ-023。速度/加速度的有限差分可发现违例，但不能证明采样间的物理上界；须有应用于本 run 的 DynamicsEvidence 及权威可核验的物理包络，不以命令/Profile 数字自证。

按轴平移 q 的米制欧氏范数，A 为本 run 批准的加速度上界、V 为速度上界、h 为相邻反馈时间、δ 为相机/反馈映射误差、行 TimestampUncertainty 和固定延迟误差之和，E_enc 为 encoder 误差界。L 为全批准 cell 上 P 的 Jacobian 二范数上界：逐 cell 用 G0 加双线性 d 的四角 Jacobian 求最大奇异值，取全域最大，运行时核不得超过资产 MaximumMotionJacobianNorm。误差门固定用保守上界相加（不假设独立而开方）：

```text
E_pose = L * (E_enc + A*h*h/8)
E_sync = L * (V*δ + A*δ*δ/2)
E_blur = L * (V*T/2 + A*T*T/8)
E_mesh = L * (A*DeltaRowTime*DeltaRowTime/8 + norm(q_next_row-q_row)/2)
E_total = E_optical + E_registration + E_chord + E_pose + E_sync + E_blur + E_mesh + E_numeric
```

每项不得超过 LineErrorLimits 对应项，sum<=Total；任何未知界/证据不适用也拒绝该行。E_registration 是相应批准 cell 的独立误差上界（包含方向/温度重复性），E_optical 是局部光学/参考安装的独立物理误差，E_chord 是截线分段近似界，E_numeric 是 Profile 已验证的浮点/矩阵/网格逆算界；不得当成零。上式 A*h²/8 是有加速度上界条件下线性位置插值的最坏误差，不证明硬件本身满足 A。Nearest 图的采样位移另外记录/受 MaxNearestDisplacement 限制，不将采样误差混进原像素几何残差。停止判定/settled 不适用连续扫描，不能从此插值推导 stopped/设备状态。

其中 h/DeltaRowTime 用含两端映射误差的最坏时间间隔，δ=相机映射误差+所选两反馈映射误差最大值+TimestampUncertainty+DelayUncertainty。E_mesh 的第一项覆盖相邻曝光间运动相对直线的偏差，第二项用 Lipschitz 上界覆盖 P 的非线性：`||P((1-a)q0+a*q1)-((1-a)P(q0)+a*P(q1))||<=2*L*a*(1-a)*||q1-q0||<=L*||q1-q0||/2`。这是保守固定式，不用程序员选择曲率拟合；物理资格不能省略这项。先检验各反馈/行之间的编码器线段及按插值/同步误差扩大的包络完全处于已资格 cell 并集，再取所穿 cell 最大 Registration 界与 Jacobian；包络出域拒绝，不靠端点在域内推出全段有效。每个面取两行各误差分量最大值、加其 E_mesh，保存在 LineMeshTriangle.Bounds，再检 Total/逐项门；仅精确节点时 Mesh=0有数学依据，不能为未知物理误差填0。

### C.3 固定网格、唯一反算、覆盖与原像素取样

固定网格仅由相邻整数列 j,j+1 和两条原行 r,r+1 构成；还须 LineCounter 相邻、全部时序/条件/误差门通过。四个节点 W00/W10/W01/W11 的对应源坐标是 (j,r)/(j+1,r)/(j,r+1)/(j+1,r+1)。按固定对角线 00→11 分成 `T0=(00,10,11)`、`T1=(00,11,01)`，TriangleId=(FovId,Row0,Column0,Half)，Half=0/1。不让 HALCON/实现者重新选对角线。

- 连续源位置的前向定义就是上述三角面上的重心插值，**不是**声称任意亚行曝光有精确 pose。整数节点满足 C.2；整数列之间的光学/亚行运动近似误差由 E_chord/E_pose/E_mesh 和独立 mesh 验证包络覆盖。没有两个合法相邻行时不生成面；一行可保留诊断点，不能扩大成一段面积。C2-RF来源还须通过C.10的原Frame行绑定、counter/clock/association域和payload窗口/hash适用门；source分页邻接或两条曝光原值存在均不代替这些门，跨缺行/epoch/规则段不生成面。
- 每个三角面的二维 Jacobian 行列式符号必须与该相机/扫描方向资产 ExpectedOrientation 一致，绝对二倍面积>=MinTriangleDoubleArea。扫描投影 `ScanDirection·(P(q_(r+1))-P(q_r))` >=MinRowAdvance 且位移<=MaxRowDisplacement；未知方向/停滞/折返/折叠拒绝本源物理几何。不同段不连面。
- 同一源的非邻接面有正面积重叠即非单射，MZ-027。用 common X 包围区间稳定排序、扫描活跃区间生成候选对，再用精确方向谓词求三角形交叠；MaxTopologyPairs 限定检查数，超预算 MZ-010，不能跳过检查。不同源间重叠允许，但不合并它们的姿态或验证事实。
- 反算点 p 时先用包围盒筛选，再在每个候选面求 `p=w0*W0+w1*W1+w2*W2, sum(w)=1`；其原坐标 `s=w0*S0+w1*S1+w2*S2`。二维行列式/包含/边界判断按输入 binary64 精确有理（BCL BigInteger 的 dyadic 值）计算，最后转 double 权重；不以 epsilon 扩大覆盖、不 snap 域外点。无面→Hole；仅共享边/节点且源坐标相同→按 TriangleId 最小者归属；非邻接候选/源位置不一致→Ambiguous 并 MZ-027，不 nearest triangle、不迭代猜 root。
- 源面外边界只到首末有效像素中心，闭集几何查询可命中边/节点，不外扩半像素；输出 tile 网格仍按 §4 半开核心。缺行两侧不连面、不外推。首版 source.Frame.Mask 必须 null，非 null MZ-026；行原 hash 未验证区域从输出支持中扣除；输出有效性是独立位图，不用灰度0表达 Hole。
- 多源同一点逐源独立反算；首版只允许固定 FovId.Ordinal 升序 stacking，取第一条有资格且源采样有效的记录，保留实际选择/被遮覆盖关系。若请求检测/计量不能覆盖整个所需区域，则相应用途 Rejected，不以显示 Partial 获得生产资格；局部几何查询可返回该点自身的有效结果。
- Nearest 选择 `floor(column+0.5), floor(row+0.5)`，只在本面的合法两行/两列以及原 FrameRef.ValidWindow 内选择；取整后超边界/缺行即无有效输出。保留分数坐标和采样位移。真实 map_image 前先校验全部线性索引，再以窗口内真实 origin/宽度重新线性化，不用 stride 字节数作 HALCON 像素宽度。未知输出点给安全索引0但位图无效，映射后将无效区域清零并扣除 domain；安全替值绝不增加覆盖。

HALCON 渲染首版仅用 [gen_image1](../../../halcon算子手册/operators/gen_image1.html)（拷贝紧凑 Byte 源窗口/Int4 nearest 索引 map）→[map_image](../../../halcon算子手册/operators/map_image.html) 一通道无插值→导出 module-owned buffer；map_image 不检查越界，checked 索引/窗口验证须在 native 前完成。若窗口像素索引不能装入 Int32 则按预算分块或 MZ-010，不切换未冻结 XL 路线。不对生产全图调用 gen_image_to_world_plane_map/image_to_world_plane 代替逐行映射。托管三角面是实际反馈时空组合，HALCON 无对应任意反馈网格算子；不平行重写光学畸变/视觉检测算子。

导出用 [get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html) 只读指针，确认 Byte/尺寸后拷贝到本操作 owned buffer；HALCON image 存活直到拷贝完成，指针不返回 Core/Host，也不原地改共享源。所有gen_image1输入按有限数组显式pin，调用拷贝完即可解pin；native对象各分支退出确认后释放，不使用extern长借存储。ValidityBits 按输出Frame.Width×Height逐行展开，低位先行（bit i为byte[i/8]的1<<(i%8)），长度ceil(pixelCount/8)、尾高位0；pixel buffer与位图共享同一lease寿命/预算，Query只投影metadata。输出Frame.Mask=null仅表示没有外部MaskRef，**不能**绕过ValidityBits当全图有效。

### C.4 增量公开 DTO、端口、工厂与身份

新增类型同 namespace `Asun.Modules.Mosaic`；L<T>、ValueRef、Length、Revision、FrameRef、FovOpticalCalibrationRef、ConditionDomain、ResidualNode、RegistrationCell、AxisPosition、Transform2D、Point2、PlanarPoint、OutputGrid、ResourceBudget、MosaicCallReply<T>、MosaicError、ResourceLedger、FrameReadRequest、TileKey、ITileBufferLease、IMosaicTileLease 和全部生命周期 enum **逐字复用 A.1**。以下是唯一构造字段顺序；集合非 null、不可变副本，所有有物理量的新增 double 名称明确米/秒，不能省略未知值而填零。

```csharp
public enum LineOpticalModel { PerspectiveDivision=0, TelecentricDivision=1 }
public enum LinePointStatus { Available=0, Hole=1, Ambiguous=2, Rejected=3 }
public enum LineOperationKind { Trace=0, Execute=1, Tile=2 }
public record UnitVector2(double X, double Y, string Frame);
public record RigidTransform3(string FromFrame, string ToFrame,
    L<double> RotationRowMajor, L<double> TranslationMeters);
public record LineDivisionParameters(LineOpticalModel Model, double? FocusMeter,
    double? Magnification, double KappaPerMeterSquared, double SxMeter,
    double SyMeter, double CxPixel, double CyPixel, uint ImageWidth,
    uint ImageHeight, double VxMeterPerRow, double VyMeterPerRow, double VzMeterPerRow);
public record LineMotionField(Transform2D GlobalBasis, L<Length> AxisX,
    L<Length> AxisY, L<ResidualNode> Nodes, L<RegistrationCell> Cells,
    L<ConditionDomain> Conditions, L<string> ResidualComponentIds,
    Revision AlgorithmRevision, double MaximumMotionJacobianNorm);
public record LineTimingPolicy(string TargetDomain, string TargetEpoch,
    long TargetFrequency, TimeSpan EffectiveDelay, TimeSpan DelayUncertainty);
public record LineErrorLimits(Length Optical, Length Registration, Length Chord,
    Length Pose, Length Synchronization, Length ExposureBlur, Length Mesh, Length Numeric, Length Total);
public record LineScanLimits(TimeSpan MaxFeedbackGap, TimeSpan MaxAxisSkew,
    TimeSpan MaxSynchronization, TimeSpan MaxExposure, double MinSpeedMetersPerSecond,
    double MaxSpeedMetersPerSecond, double MaxAccelerationMetersPerSecondSquared,
    Length EncoderResolution, Length MaxRowDisplacement, Length MinRowAdvance,
    Area MinTriangleDoubleArea, double MaxProjectionRoundTripPixels,
    double PoseOrthogonalityTolerance, Length MaxNearestDisplacement,
    LineErrorLimits Errors, TimeSpan MaxSnapshotAge, ulong MaxRows, ulong MaxTriangles, ulong MaxTopologyPairs);
public record LineGeometryDefinition(ValueRef Identity, DeviceScope Devices,
    string CameraId, FovOpticalCalibrationRef Optical, LineDivisionParameters Parameters,
    RigidTransform3 PlaneInCamera, Transform2D PlaneToCommon,
    AxisPosition ReferenceEncoder, LineMotionField Motion, ConditionId Condition,
    UnitVector2 ScanDirection, int ExpectedOrientation, LineTimingPolicy Timing,
    LineScanLimits Limits, ValueRef PlanarInstallationEvidence);
public record LineColumnPoint(long Column, PlanarPoint Common,
    double ProjectionRoundTripPixels);
public record LineTraceArtifact(ValueRef Identity, ValueRef Definition,
    L<LineColumnPoint> Columns);
public record LineScanArtifact(ValueRef Identity, LineGeometryDefinition Definition,
    LineTraceArtifact Trace, ValueRef IndependentValidation,
    Length OpticalBound, Length TraceChordBound, L<QualifiedCell> MotionCells);
public record LineScanQualification(ValueRef Identity, ValueRef Artifact,
    L<MosaicPurpose> Purposes, DateTimeOffset ValidFromUtc,
    DateTimeOffset ValidUntilUtc, bool Revoked, Revision AuthorityRevision);
public record LineScanSnapshot(LineScanArtifact Artifact,
    LineScanQualification Qualification, DateTimeOffset ObservedUtc,
    PermissionScopeId PermissionScopeId);
public record LineClockStamp(string Domain, string Epoch, long Tick, long Frequency);
public record LineClockMapping(ValueRef Identity, string SourceDomain,
    string SourceEpoch, string TargetDomain, string TargetEpoch,
    long ScaleNumerator, long ScaleDenominator, long OffsetTargetTicks,
    long MaximumErrorTargetTicks, long ValidSourceTickMin, long ValidSourceTickMax);
public record LineEncoderSample(long Sequence, string ControllerId,
    string BootId, long Generation, string DeviceReferenceRevision,
    string PositionVersionX, string PositionVersionY,
    AxisPosition Actual, LineClockStamp At, Length EncoderErrorBound,
    RegistrationConditions Conditions, ValueRef Source);
public record LineExposure(long RowIndex, string LineId, long LineCounter,
    ContentDigest RowDigest, LineClockStamp ExposureStart,
    LineClockStamp ExposureEnd, TimeSpan TimestampUncertainty, ValueRef Source);
public record LineTimingBundle(ValueRef Identity, L<LineClockMapping> Mappings,
    L<LineEncoderSample> Feedback, L<LineExposure> Rows, ValueRef DynamicsEvidence,
    double SpeedBoundMetersPerSecond, double AccelerationBoundMetersPerSecondSquared);
public record LineScanSource(FovId Id, DeviceCamera ActualCamera,
    FrameRef Frame, ObservationRole Role, LineScanSnapshot Snapshot, LineTimingBundle Timing);
public record LineScanRequest(MosaicOperationId OperationId, AttemptId AttemptId,
    Revision AlgorithmRevision, L<LineScanSource> Sources, MosaicPurpose Purpose,
    OutputGrid Grid, L<PixelRect> RequiredOutputWindows, PermissionScopeId PermissionScopeId,
    DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record LineTraceRequest(MosaicOperationId OperationId,
    LineGeometryDefinition Definition, PermissionScopeId PermissionScopeId,
    DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record LineTraceResult(LineTraceArtifact? Candidate,
    ResourceLedger Resources, L<MosaicError> Errors);
public record LineTriangleId(FovId Source, long Row0, long Column0, uint Half);
public record LineMeshVertex(long Row, long Column, PlanarPoint Common);
public record LineMeshTriangle(LineTriangleId Id, LineMeshVertex V0,
    LineMeshVertex V1, LineMeshVertex V2, LineErrorLimits Bounds);
public record LineRowEvaluation(FovId Source, long RowIndex, AxisPosition? InterpolatedActual,
    long? FeedbackSequence0, long? FeedbackSequence1, double? Weight1,
    PlanarPoint? Translation, LineErrorLimits? ActualErrorBounds, L<MosaicError> Errors);
public record LineScanPlan(ValidationResult Validation,
    L<LineRowEvaluation> Rows, ulong TriangleUpperBound,
    ResourceLedger Resources, L<MosaicError> Errors);
public record LineScanManifest(ValueRef Identity, LineScanRequest Request,
    L<LineMeshTriangle> Triangles, L<LineRowEvaluation> Rows);
public record LineScanResult(LineScanManifest? Manifest, CoverageReport Coverage,
    L<PurposeDecision> Purposes, ResourceLedger Resources, L<MosaicError> Errors);
public record LinePointRequest(ValueRef Manifest, FovId Source, PlanarPoint Common,
    PermissionScopeId PermissionScopeId);
public record LinePointResult(LinePointStatus Status, Point2? SourcePixel,
    LineTriangleId? Triangle, L<double> Weights, L<MosaicError> Errors);
public record LineScanTileRequest(MosaicOperationId OperationId,
    ValueRef Manifest, TileKey Key, PermissionScopeId PermissionScopeId,
    DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record LineScanOperationStatus(MosaicOperationId OperationId,
    LineOperationKind? Kind, QueryAvailability Availability, ExecutionState? State,
    LineTraceResult? Trace, LineScanResult? Runtime, TileOperationMetadata? Tile,
    ResourceLedger? Resources, L<MosaicError> Errors);
public record LineAuthorityRequest(LineScanSource Source,
    PermissionScopeId PermissionScopeId, MosaicPurpose Purpose,
    DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record LineAuthorityResult(LineScanSnapshot? Snapshot,
    ResourceLedger Resources, L<MosaicError> Errors);
public record LineOpticalAuthorityRequest(LineGeometryDefinition Definition,
    PermissionScopeId PermissionScopeId, DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public record LineOpticalAuthorityResult(bool ExactApplicable,
    ResourceLedger Resources, L<MosaicError> Errors);
public record LineTraceWork(LineTraceRequest Request);
public record LineRenderWork(LineScanTileRequest Request, LineScanManifest Manifest,
    L<IFrameLease> Leases);
public interface ILineScanTileLease : IMosaicTileLease
{
    ReadOnlyMemory<byte> ValidityBits { get; }
}
public interface ILineTileBufferLease : ITileBufferLease
{
    ReadOnlyMemory<byte> ValidityBits { get; }
}
public record LineTileRenderResult(ILineTileBufferLease? Buffer,
    ResourceLedger Resources, L<MosaicError> Errors);
public record LineScanTileResult(TileStatus Status, ILineScanTileLease? Lease,
    ResourceLedger Resources, L<MosaicError> Errors);
public interface ILineScanAuthorityPort
{
    ValueTask<LineAuthorityResult> ResolveAsync(LineAuthorityRequest request,
        CancellationToken cancellationToken);
    ValueTask<LineOpticalAuthorityResult> ResolveOpticalAsync(LineOpticalAuthorityRequest request,
        CancellationToken cancellationToken);
}
public interface ILineScanAdapter
{
    ValueTask<LineTraceResult> ProjectFirstLineAsync(LineTraceWork request,
        CancellationToken cancellationToken);
    ValueTask<LineTileRenderResult> RenderTileAsync(LineRenderWork request,
        CancellationToken cancellationToken);
}
public record MosaicModuleOptionsV04(MosaicModuleOptions Core,
    ILineScanAuthorityPort LineAuthority, ILineScanAdapter? LineAdapter);
public interface IMosaicServiceV04 : IMosaicService
{
    ValidationResult ValidateLineScan(LineScanRequest request);
    LineScanPlan PlanLineScan(LineScanRequest request);
    ValueTask<MosaicCallReply<LineTraceResult>> ProjectLineTraceAsync(
        LineTraceRequest request, CancellationToken cancellationToken);
    ValueTask<MosaicCallReply<LineScanResult>> ExecuteLineScanAsync(
        LineScanRequest request, CancellationToken cancellationToken);
    LinePointResult LocateLineScanPoint(LinePointRequest request);
    ValueTask<MosaicCallReply<LineScanTileResult>> GetLineScanTileAsync(
        LineScanTileRequest request, CancellationToken cancellationToken);
    ValueTask<LineScanOperationStatus> QueryLineScanAsync(
        MosaicOperationId operationId, CancellationToken cancellationToken);
}
```

`MosaicModule.Create(MosaicModuleOptionsV04 options)` 是同一个工厂的新重载，返回 IMosaicServiceV04；不是第二种 builder/Build API。v0.3 Create 重载和全部字段/方法不变，旧消费者不必迁移。Core.Options 的 SessionEpoch、Clock、ServiceLimits、FramePort、Diagnostics、ProgressSink 与所有新入口共用，不能另建隐藏时钟/资源根。LineAdapter=null 时纯 Validate/Plan/Execute 的托管几何仍可用；ProjectLineTrace/GetLineScanTile 稳定 MZ-026，无设备/窗口初始化。v0.3 RegistrationAdapter 不承接线扫调用。

### C.5 精确约束、身份投影及有限生命周期

- 物理内部统一米，输出按 Grid 明确换算；请求、资产、trace/mesh 的 frame 一致。LineDivisionParameters 精确对应官方 tuple：Perspective 为 `['line_scan_division',Focus,Kappa,Sx,Sy,Cx,Cy,Width,Height,Vx,Vy,Vz]`，Focus>0/Magnification=null；Telecentric 为 `['line_scan_telecentric_division',Magnification,Kappa,Sx,Sy,Cx,Cy,Width,Height,Vx,Vy,0]`，Magnification>0/Focus=null。Sx/Sy>0，Vy>0，尺寸正；先验光学单位/依赖/采集尺寸全部闭合，不篡改上游 tuple。Width 与 source Width 相同；光学校准 Height 是原校准图高度，不要求生产段 Height 相同，首行截线仍 row=0；生产行时序不扩大 optical column 域。
- PlaneInCamera 9 个旋转、3 个米制平移，正交/行列式≈+1 的容差为 PoseOrthogonalityTolerance；PlaneToCommon 2D 也只刚体，最后行为(0,0,1)，各输入有限。ScanDirection 在 common frame 单位模长（同容差），ExpectedOrientation 仅 -1/+1，与独立验证方向一致。ReferenceEncoder 与 Actual 为同一轴 frame；Motion.GlobalBasis 仅 affine；本定义中 Motion.Cells/N00等同 A.1 的定向四角规则，MotionCells 精确逐 camera/condition/cell 限定生产用途。
- Limits 的所有时长/长度/面积/上界正且有限，MinSpeed>=0且<=MaxSpeed；delay 可有符号，DelayUncertainty/TimestampUncertainty/MaximumErrorTargetTicks 允许0，但须有来源可证明，非未知默认。MinRowAdvance>0。LineErrorLimits 的八项之和<=Total。MaxRows/MaxTriangles/MaxTopologyPairs 正且 checked；产出前检查 Memory/CPU/TileCount/pending IO/native/缓存/输出全部实例预算。q/t/row 的外推均禁止。

- 必须检查源为 Identity/Byte/Channels=1、Frame.ValidWindow=原全幅(0,0,Width,Height)、Mask=null，所借子窗口仍以原row/column身份描述；Frame.Height<=MaxRows，trace覆盖全部光学批准列。RequiredOutputWindows 非空、矩形非空、同输出Grid像素frame，允许负X/Y，checked端点且不重叠；它们定义宿主本次**所需区域**，不是全无限common平面。Grid的CommonFrame/单位/步长/PhaseAnchor、Channels恰好一项且与所有Source.Role.Channel一致，MaxLod=0/Halo=0，Role未知拒绝。tile在这些窗口之外NotFound；部分相交tile只相交位置有效，TileKey.Lod/Channel/DirectoryRevision精确匹配。Manifest.Identity.Revision就是DirectoryRevision，算法版本只能本方法已发布revision，不根据新请求临时学习。
- ValidateLineScan 校验结构、全部digest闭包、快照有效性/相机/资格用途、时钟和预算；全局结构/epoch/配置/重复冲突失败即IsValid=false/所有rows不求值。缺失原行是合法不完整输入，Validate可有效，Plan为每个row给诊断并只建合法相邻面；局部反馈gap/误差越界同样不连面。未知run动态/平面/权威/方向、源折叠/非单射拒绝该源全部物理面，不能只删冲突面直到合格；其他源的合法面可保留作明确Partial，但Detection/Measurement的RequiredOutputWindows任何点不受支持则相应用途Rejected。
- Coverage预期/实得Source数量沿A.1；Missing列完全不可用源，其余缺行/边缘/采样无效输出按RequiredOutputWindows逐输出像素中心检测并投影成行内最大连续Hole矩形（高1输出pixel，经Grid换为common RectD），不以mesh包围盒证明覆盖。相邻Hole行不自动合并，数量/内存计入Manifest预算。每个Required窗口覆盖检查点数及tiles受Budget.TileCount/Memory/Cpu限制，预算不足MZ-010，不抽样假Complete。Coverage.Empty为无有效面；Complete要求全部所需点有有效原来源（nearest时还须实际源行hash验证，因此Execute仅几何覆盖Complete、Tile交付另做原字节门），否则Partial；Purposes只代表已验证几何资格，取原像素/正式提交仍核原帧与外部质量事务。没有执行字节校验不声称原图保存或图像数据已通过。
- Source.ActualCamera.Kind=LineScan且实际配置摘要/CameraId/AxisGroupId与Definition.Devices、Optical.Camera精确匹配；LineAuthorityRequest携带完整Source（包括原frame、timing mappings/samples/dynamics和精确snapshot），权威端口核每项来源归属/当前适用性，不能只核一个DynamicsEvidence布尔值。正式桥必须把Frame.Id/hash与这份实际采集配置证据绑定，调用方自填相等不能代替权威。
- LineScanQualification.Artifact必须精确指本Artifact.Identity，时间区间有效且未撤销，Purposes包含本用途；本Source.Definition.Devices与CameraId/Frame配置一一匹配。Artifact.MotionCells.Bounds给非空独立误差，其用途/camera/condition/cell与Motion的supported cells匹配，不接受节点拟合残差当资格；OpticalBound/TraceChordBound正且有限且不大于Limits对应项。定义引用、trace.Definition、Qualification artifact和请求Scope形成无环闭包，Core独立重算所有本模块content digest；外部引用按原Owner摘要验证。Definition.Motion.ResidualComponentIds只覆盖本基线组件，与上游已补偿坐标组件冲突MZ-027；实际Encoder不能换成ControllerCommand/CompensatedCommand。
- v0.4 profile 在本增量就是资产 Definition.Limits 与精确资格；request 不放可放宽它的第二套参数。Sources 非空、FovId/Frame.Id唯一，按 set 语义编码；一个 Source 一台相机，一段扫描，LineScanSnapshot.PermissionScopeId 与请求一致且 ObservedUtc 不能在未来，年龄受 Definition.Limits.MaxSnapshotAge 限定（只是预检快照年龄，不作为资格有效期）。执行仍精确权威复核；不以客户端快照声明 Qualified。构造 line 请求没有 nullable Compensation 字段，故不可表达任何附加补偿。
- Feedback 按 Sequence/原时间有序，Boot/Generation/controller/epoch/frame/基准版本不变，实际 XY 两轴 PositionVersion 均存在，Source 是运动公开证据，不是 commanded 值。Mappings source clock 精确覆盖所有 stamp；Target Domain/Epoch/Frequency 与 Definition.Timing 相同，scale>0/denominator>0；无相应 source frequency 的映射来源证据拒绝，不能猜单位。映射返回范围两端按不利方向纳入误差。Rows 保留原顺序，允许完全相同重传，规范化后按原 row index 有序；Timing.Identity 摘要在规范化**前**计算，以审计所有重传记录。

- LineEncoderSample.At是经设备/运动Owner证明的同时XY实际采样stamp（MaxAxisSkew只检查来源证据，不由mosaic合成异步轴）；DeviceReferenceRevision不可跨变更，PositionVersionX/Y可随实际采样更新但须保留各原版本。Sequences相邻差1且正，Generation>=0；Rows.RowIndex在[0,Frame.Height)、LineCounter非负严格硬件原序，曝光End>=Start且duration>0。同一counter映射到两个row/不同LineId拒绝；row缺口或counter增量>1使两侧不邻接。所有本bundle的Source/映射来源与Run Identity绑定，正式Read authority须核验它们和DynamicsEvidence相容，不能信用户填的SpeedBound/AccelerationBound。逐反馈有限差分速度、相邻割线速度差/半间隔加速度的发现值超过获批上界即MZ-022，未超过不自证物理上界。有效行的条件ID/配置/timingRevision/温度和两个反馈均落在Definition.Condition，不跨条件求值。
- LineEncoderSample.At是经设备/运动Owner证明的同时XY实际采样stamp（MaxAxisSkew只检查来源证据，不由mosaic合成异步轴）；DeviceReferenceRevision不可跨变更，PositionVersionX/Y可随实际采样更新但须保留各原版本。Sequences相邻差1且正，Generation>=0；Rows.RowIndex在[0,Frame.Height)、LineCounter非负严格硬件原序，曝光End>=Start且duration>0。同一counter映射到两个row/不同LineId拒绝；row缺口或counter增量>1使两侧不邻接。所有本bundle的Source/映射来源与Run Identity绑定，正式Read authority须核验它们和DynamicsEvidence相容，不能信用户填的SpeedBound/AccelerationBound。逐反馈有限差分速度、相邻割线速度差/半间隔加速度的发现值超过获批上界即MZ-022，未超过不自证物理上界。有效行的条件ID/配置/timingRevision/温度和两个反馈均落在Definition.Condition，不跨条件求值。

   C2-RF的BlockOrdinal/SourceOrdinal只确定原ledger读取顺序，不是r/连续性证明。缺行只消费原camera封口ExpectedRange/计数，未知范围保Unknown/null；跨wrap/reset/epoch/规则分段，同Frame无法表达分段就拒绝物理投影。曝光/关联/clock未知或UInt64不能无损承载时保原row诊断、阻断坐标，不以0.5px/名义频率/合成时刻/命令速度补齐。C.10解释保守适用边界，不改C.2几何公式/C.3固定网格。
- LineRowEvaluation 缺时间/反馈/误差资格时 InterpolatedActual/Translation/ActualErrorBounds=null，保留 RowIndex 与错误；合法权重有限在[0,1]，准确命中仍保留选定相邻反馈 ID。Translation=P(q_row)-P(q_ref)，不冒称运动实际坐标。LineScanPlan.Rows 按 request Sources 的 FovId.Ordinal 再 RowIndex 排列；每项携带显式 Source FovId，逐 Source 原 Frame 高度生成完整诊断槽（预算先检）；未提供曝光的 row 保留 MZ-020，不省略缺失行。
- 所有 Project/Execute/Tile 原 operation registry 共用 v0.3 Sequence/epoch/同ID同摘要复用与异摘要 MZ-028 规则，新入口标签隔离。QueryLineScan 无 IO/无 Memory/lease；只能查新 LineOperationKind 的类型结果，旧 QueryAsync 查 line ID 返回 MZ-026（不能伪装旧 Runtime），新 QueryLineScan 查旧 ID 同样 MZ-026。共有 Drain/Dispose 枚举整个 registry，任何 line pending Task/输入/native/临时/已交付输出均计入。
- LocateLineScanPoint 只读服务已持有的精确 manifest，无 IO；拒绝过期/淘汰/权限范围不属本实例的 ref，返回 Rejected。Available 必有 SourcePixel/Triangle、3 个权重且无错误；Hole/Ambiguous/Rejected 全部输出点/面 null、Weights 空，分别记录覆盖/歧义/拒绝原因。它是**既有 manifest 修订的几何查询**，不重新授生产资格；消费者正式取图/提交前要权威复核。同步 Validate/Plan 也不读 Asset/Frame/native/动态权限。

- Locate.PermissionScopeId与manifest/本实例原Scope一致，p.Frame/米制单位同common，FovId必须属Manifest；不允许传另一个Source域内点推邻源的坐标。重心权重只在真实面内计算，Requested用途不在资格则 Execute不提供该用途的manifest。LineScanTileResult Available时Lease非null/Errors空，其它状态Lease=null；LineTileRenderResult失败Buffer=null。LineScanOperationStatus NotFound/Expired时Kind/State/各Result/Resources=null，仅带查询错误；Active未获正式结果时对应Trace/Runtime/Tile=null，终态/OutputHeld按原registry投影，Trace/Runtime/Tile只允许一个分支，Tile metadata沿A.1并没有ValidityBits或Memory。Trace/Runtime失败的终态结果Resources必填，不假资源释放。
- Trace.Candidate 只在本次 native 退出、前后 optical 权威核对均通过时非 null；永远未资格。Native 退出但权威不明/失败时 Candidate=null、Errors 非空。LineScanResult.Manifest 只在至少一个有效面且精确权威/预算/用途复核通过后非 null；空输入预检拒绝，零面仅诊断/错误，不能生成面积为零的“完整图”。Coverage 的 expected/captured 以源描述计，行空洞/所有无效源另纳入 Missing/Holes；Empty/Partial 不报 Complete。
- ExecuteLineScan 先权威 Resolve 精确 artifact+qualification+DynamicsEvidence；返回值还须与请求内全闭包/hash/配置相等，并证明 Optical/PlanarInstallation/IndependentValidation/本 run 动态包络均当前适用，未知不能返回成功。再托管建面/唯一性/预算，交付 manifest 前再次同引用 Resolve；不自动 latest。此入口只生成几何目录，不借源帧。GetLineScanTile 在借帧前及输出交付前重做各相关权威复核，再 Acquire 所需 source 窗口；计算 RowDigest 时读取原完整行有效像素字节，不包括 stride padding，窗口不能覆盖整行则另外借整行做验证并计入预算。原字节 hash 不通过不给出有效 tile。
- 异步操作完全沿 §9.2：None token 也用 min(DeadlineUtc,now+MaxObservationWait) 的有限观察；未退出 Task/迟到buffer仍保留原 registry。PendingDrain/WaitCancelled Result=null；迟到 native/端口资源服务收尾。输出 ILineTileBufferLease adapter→service，仅 GetLineScanTile Returned/Available 经同锁 TrySetResult 才转换交付 ILineScanTileLease。输出未归还保持 OutputHeld/Active，InternalReleasedUtc 不等于 ResourcesReleased；Query/Drain 不偷 lease，Drained→ResourcesReleased→Terminal 顺序不变。行摘要不做隐藏后台读取。

编码沿用 A.2 `mosaic-core-bin-v1` 的值规则和头，**新根标签**为 `line04-trace`(LineTraceRequest)、`line04-execute`(LineScanRequest)、`line04-tile`(LineScanTileRequest)、`line04-geometry`(LineGeometryDefinition)、`line04-trace-content`(LineTraceArtifact)、`line04-artifact`(LineScanArtifact)、`line04-timing`(LineTimingBundle)、`line04-manifest`(LineScanManifest)。geometry/trace-content/artifact/timing/manifest 五个内容根只删自身 Identity.Digest，保留 Identity.Id/Revision 和其余嵌套 digest；manifest 包含完整 Request/row evaluations/mesh，不循环引用自己。Trace.Definition 指 geometry 的精确内容引用，Artifact 包含 definition/trace而不包含 Qualification，Qualification由外部 Owner 编码并指 artifact，request snapshot包二者，manifest仅指自己的独立身份；无循环自 hash。

LineMotionField 的 Nodes/Cells/Conditions/ResidualComponentIds、LineScanArtifact.MotionCells、Qualification.Purposes 与 request Sources 为 set（逐稳定 ID 不重复），其它全为 list，尤其 trace Columns、Timing.Mappings/Feedback/Rows、manifest Triangles/Rows 不排序。相同重复行留在原 Timing.Rows 编码中，不能先去重改变原意图。LineClockMapping.Identity 是上游历史 mapping 摘要原样引用，不按新格式重算它；Source/Rigid/Optical/Qualification 的原始 hash 也不改。新入口继承 byte length/strict UTF-8/非有限拒绝/时间及 GUID 规则；改变 row tick/clock mapping/Boot/原行hash/资格/预算/deadline 必改变本请求摘要。186-byte 旧向量保持不变。

Trace候选Identity.Id=`line-trace-`+该LineTraceRequest的line04-trace摘要，Revision=Definition.Identity.Revision；Manifest.Identity.Id=`line-manifest-`+该LineScanRequest的line04-execute摘要，Revision=request.AlgorithmRevision。Id长度不超过128，自身Digest按上述独立content投影计算。Definition/Artifact/Timing的Identity.Id/Revision由其原发布/采集Owner提供，Core仅核其content投影，不静默换Id；外部Qualification和ClockMapping沿各Owner身份，不改原摘要。

新值编码的独立fixture（仅编码测试，未构建模块）：标签`line04-clock-stamp`，根LineClockStamp=(Domain="d",Epoch="e",Tick=9007199254740993,Frequency=1000)。长度80 bytes；完整hex=`4d5a4301120000006c696e6530342d636c6f636b2d7374616d700c020e0000004c696e65436c6f636b5374616d700400000002010000006402010000006505010000000000200005e803000000000000`，SHA-256=`25ed5c3e1b070a3429fd411ce3f6036ed4349c3129820ac13d4ae365a54b2034`。此fixture不新增生产入口，不把tick先转double；接收者只按字段独立重建预像，不能调用受测encoder生成期望。

### C.6 两个完整无 UI Host 与最小装配

**查看 Host（离线线扫大图）**在自己的 Exe 内创建固定 TimeProvider、SessionEpoch、ServiceLimits、只读 FramePort、CoordinatePort、Diagnostics 和可空 ProgressSink→组成 v0.3 Core Options（RegistrationAdapter/CalibrationAdapter可null）→显式注入 LineAuthorityPort 与 LineAdapter/null→同名 Create(v0.4)→读入已资格完整 LineScanSnapshot、原始 source 描述、行曝光和 encoder/mapping/dynamics→用新 OperationId 构造 LineScanRequest→ValidateLineScan/PlanLineScan（所有 IO/native 计数0）→ExecuteLineScan 观察 Returned/Result 或 QueryLineScan 原 ID→有 manifest 后 Locate 验证节点/空洞→取 tile（真实/模拟 LineAdapter 必须注入），仅 Available 读取并 finally 归还→有限 Drain→Dispose。空洞/Rejected 不取灰度做覆盖，未知资格不自动诊断降级。保留原 source/hash/row ID；生产没有靶标图或纹理也可消费。

**分析 Host（线扫几何与原像素分析）**用自己的实例/权限/预算，同包只引用公开 API→先提供精确上游 Optical/解出的参数、参考平面实测安装、q_ref、线扫 Motion 子场和 Profile→ProjectLineTraceAsync（有光学 adapter；没有则仅消费已保存 trace）→Returned Candidate 明确未资格→通过宿主外部发布/资格 Owner 保存 C.4 完整 artifact/independent validation，并取得 LineScanQualification，不能从 Candidate 自行构造生产快照→解析精确 Snapshot→新 Execute→逐源 Locate→同时借原始 frame 给自己的分析能力，按 original source pixel 解释物理位置/误差→只消费 Purposes 明确允许的用途，不从最近邻显示图直接计量→归还自己与模块所有输出→原 ID QueryLineScan/有限 Drain/Dispose。发布/资格的耐久事务由原 Owner 接线，本增量不建立第二种 Store 或直接写上游。

本节下面的实施块替代泛称 fixture。规划位置唯一为原 Core.Tests 的 `LineScan/Hosts/`：`SyntheticLineFixture.cs`、`HostBinary.cs`、`SyntheticPorts.cs`、`LineViewHost.cs`、`LineAnalysisHost.cs`、`HostRecoveryRoot.cs`；这是后续实现的文件责任，不是本轮创建文件。两个Host由同一无窗口Exe的两个独立入口测试调用；各入口 new 自己的fixture/clock/ports/service/root，不共享可变静态状态。真实native类不进入Core.Tests。全部值、证据、资格应答都标为 **Synthetic/Simulation**，fake只证明软件协议，既不模拟真实光学投影，也不授予光学、动态、计量或生产资格。

#### C.6.1 全字段 Synthetic 夹具与两个实际 request

下述 C# 是未来测试Host实施正文，引用的产品类型全部来自 A.1/C.4 公共构造；没有产品私有 DTO、隐含 Profile 或泛型参数字典。`HostBinary` 是 C.6.2 的独立测试编码器；不调用受测模块编码器生成期望。`Ref` 是外部Synthetic证据的原始字节引用；本模块5种content用 `Seal` 的精确标签重算（不得把Ref占位摘要当成definition/trace/artifact/timing摘要）。fixture中不存在MosaicProfile字段；本线扫Profile就是Definition.Limits与Qualification，已经逐值给出。

```csharp
// LineScan/Hosts/SyntheticLineFixture.cs；仅BCL + Core；尚未创建/编译。
using System.Security.Cryptography;
using System.Text;
using Asun.Modules.Mosaic;

internal sealed class SyntheticLineFixture
{
    public static readonly DateTimeOffset T0 = new(2000, 1, 1, 0, 0, 0, TimeSpan.Zero);
    public Guid Epoch { get; }
    public byte[] OriginalBytes { get; } = [10, 20, 30, 40];
    public LineScanRequest Request { get; }
    public LineScanSource Source => Request.Sources.Single();
    public LineGeometryDefinition Definition => Source.Snapshot.Artifact.Definition;
    public ResourceBudget Budget => Request.Budget;
    public PermissionScopeId Scope => Request.PermissionScopeId;
    public static ContentDigest H(byte[] b) => new(Convert.ToHexStringLower(SHA256.HashData(b)));
    public static ValueRef Ref(string id) => new(id, new Revision(1), H(Encoding.UTF8.GetBytes("Synthetic:" + id)));
    public static Length M(double n) => new(n, LengthUnit.Meter);
    public static PlanarPoint P(double x, double y) => new(M(x), M(y), "common");
    public static AxisPosition Q(double x, double y) => new(M(x), M(y), "axis");
    public static ErrorBounds E(double n) => new(M(n), M(n), M(n), M(n));
    public static ValueRef Seal(string id, string label, object content) =>
        new(id, new Revision(1), HostBinary.Hash(label, content, removeSelfDigest: true));
    public SyntheticLineFixture(bool analysis)
    {
        Epoch = Guid.Parse(analysis ? "00000000-0000-0000-0000-000000000102"
                                   : "00000000-0000-0000-0000-000000000101");
        var scope = new PermissionScopeId(analysis ? "Synthetic-analysis" : "Synthetic-view");
        var purpose = analysis ? MosaicPurpose.GeometryDiagnostic : MosaicPurpose.Display;
        var camera = new DeviceCamera("camera", CameraKind.LineScan, "axes", Ref("configuration").Digest);
        var devices = new DeviceScope("Synthetic-machine", "station", [camera]);
        var optical = new FovOpticalCalibrationRef(new AssetId("Synthetic-optical"), new Revision(1),
            Ref("optical-content").Digest, devices.MachineId, devices.StationId, camera,
            Ref("optical-qualification"), Ref("optical-map"), new PixelRect(0, 0, 2, 2),
            new CoordinateChain(new Revision(1), [])); // empty local-chain; C.2 direct line model
        var domain = new ConditionDomain(new ConditionId("forward"), camera.AcquisitionConfiguration,
            AxisDirection.NotRequired, AxisDirection.Positive, 19, 21, true, new Revision(1));
        ResidualNode Node(string id, double x, double y) => new(new NodeId(id), domain.Id, Q(x,y), P(0,0),
            [new PhysicalGroupId(id+"-a"), new PhysicalGroupId(id+"-b")], [P(0,0), P(0,0)]);
        var commonDomain = new RectD(-0.01, -0.01, 0.01, 0.02, "common");
        var axisDomain = new RectD(-0.01, -0.01, 0.01, 0.02, "axis");
        var identity = new Matrix3(1,0,0, 0,1,0, 0,0,1);
        var motion = new LineMotionField(new Transform2D(identity,"axis","common",new Revision(1),axisDomain),
            [M(-0.01),M(0.01)], [M(-0.01),M(0.02)],
            [Node("n00",-0.01,-0.01),Node("n10",0.01,-0.01),
             Node("n01",-0.01,0.02),Node("n11",0.01,0.02)],
            [new RegistrationCell(new CellId("cell"),domain.Id,new NodeId("n00"),new NodeId("n10"),
                new NodeId("n01"),new NodeId("n11"),true)], [domain], ["Synthetic-stage"], new Revision(1), 1);
        var limits = new LineScanLimits(TimeSpan.FromMilliseconds(3), TimeSpan.FromMicroseconds(100),
            TimeSpan.FromMicroseconds(100), TimeSpan.FromMilliseconds(1), 0.1, 3, 10,
            M(0.000001), M(0.004), M(0.0001), new Area(1e-8,LengthUnit.Meter), 1e-6, 1e-9, M(0.002),
            new LineErrorLimits(M(1e-5),M(1e-5),M(1e-5),M(2e-5),M(1e-5),M(0.0004),
                M(0.0011),M(1e-8),M(0.0016)), TimeSpan.FromSeconds(10), 2, 2, 8);
        var definition = new LineGeometryDefinition(Ref("Synthetic-definition"),devices,"camera",optical,
            new LineDivisionParameters(LineOpticalModel.PerspectiveDivision,0.01,null,0,1e-5,1e-5,
                0,0,2,2,0,0.002,0),
            new RigidTransform3("plane","camera-frame",[1,0,0,0,1,0,0,0,1],[0,0,1]),
            new Transform2D(identity,"plane","common",new Revision(1),new RectD(-0.01,-0.01,0.01,0.02,"plane")),
            Q(0,0),motion,domain.Id,new UnitVector2(0,1,"common"),1,
            new LineTimingPolicy("scan-clock","scan-epoch",1_000_000,TimeSpan.Zero,TimeSpan.Zero),
            limits,Ref("Synthetic-plane-installation"));
        definition = definition with { Identity=Seal("Synthetic-definition","line04-geometry",definition) };
        var trace = new LineTraceArtifact(Ref("Synthetic-trace"),definition.Identity,
            [new LineColumnPoint(0,P(0,0),0),new LineColumnPoint(1,P(0.001,0),0)]);
        trace = trace with { Identity=Seal("Synthetic-trace","line04-trace-content",trace) };
        var qualifiedCell = new QualifiedCell("camera",domain.Id,new CellId("cell"),E(1e-6),[purpose]);
        var artifact = new LineScanArtifact(Ref("Synthetic-artifact"),definition,trace,
            Ref("Synthetic-independent-validation"),M(1e-6),M(1e-6),[qualifiedCell]);
        artifact = artifact with { Identity=Seal("Synthetic-artifact","line04-artifact",artifact) };
        // 外部fixture Owner预置响应；不是模块签发，不属于真实Published/Qualified事实。
        var qualification = new LineScanQualification(Ref("Synthetic-external-qualification"),artifact.Identity,
            [purpose],T0.AddSeconds(-1),T0.AddDays(1),false,new Revision(1));
        var snapshot = new LineScanSnapshot(artifact,qualification,T0,scope);
        var conditions = new RegistrationConditions(domain.Id,AxisDirection.NotRequired,AxisDirection.Positive,
            20,new Revision(1),camera.AcquisitionConfiguration);
        LineClockStamp Stamp(string d,long t) => new(d,d+"-epoch",t,1_000_000);
        LineClockMapping Mapping(string d) => new(Ref("Synthetic-map-"+d),d,d+"-epoch","scan-clock",
            "scan-epoch",1,1,0,0,0,2000);
        var feedback = new LineEncoderSample[] {
            new(1,"controller","boot",1,"reference", "x1","y1",Q(0,0),
                Stamp("motion-clock",0),M(1e-6),conditions,Ref("Synthetic-feedback-1")),
            new(2,"controller","boot",1,"reference", "x2","y2",Q(0,0.004),
                Stamp("motion-clock",2000),M(1e-6),conditions,Ref("Synthetic-feedback-2")) };
        var rows = new LineExposure[] {
            new(0,"line-a",50,H([10,20]),Stamp("camera-clock",400),Stamp("camera-clock",600),
                TimeSpan.Zero,Ref("Synthetic-row-a")),
            new(1,"line-b",51,H([30,40]),Stamp("camera-clock",1400),Stamp("camera-clock",1600),
                TimeSpan.Zero,Ref("Synthetic-row-b")) };
        var timing = new LineTimingBundle(Ref("Synthetic-timing"),
            [Mapping("camera-clock"),Mapping("motion-clock")],feedback,rows,
            Ref("Synthetic-run-dynamics"),2,10);
        timing = timing with { Identity=Seal("Synthetic-timing","line04-timing",timing) };
        var frame = new FrameRef(new FrameId("Synthetic-frame"),H(OriginalBytes),2,2,2,4,PixelType.Byte,1,
            PixelLayout.Interleaved,ImageOrientation.Identity,new Revision(1),new PixelRect(0,0,2,2),null,
            new ValueRef("Synthetic-frame-bytes",new Revision(1),H(OriginalBytes)),"sensor-pixel");
        var source = new LineScanSource(new FovId(analysis?"analysis-source":"view-source"),camera,frame,
            new ObservationRole("top","plane","gray","single","line-midpoint",true),snapshot,timing);
        var grid = new OutputGrid("common",LengthUnit.Meter,new Point2(0,0,"common"),M(0.00025),M(0.001),
            new Point2(0,0,"common"),2,0,0,["gray"]);
        Request = new LineScanRequest(new MosaicOperationId(Epoch,1),new AttemptId(analysis?"a-analysis":"a-view"),
            new Revision(1),[source],purpose,grid,[new PixelRect(1,2,2,1)],scope,T0.AddSeconds(5),
            new ResourceBudget(2000,16*1024*1024,1024*1024,1024*1024,8,4,8));
    }
}
```

两完整输入的差异仅上块 `analysis` 分支：Epoch末尾101/102、Scope、Purpose、FovId、AttemptId和随purpose变化的QualifiedCell/Qualification及其依赖digest。其它字段不得取默认；视图request明确是Display，分析request明确是GeometryDiagnostic。原帧digest按4个byte，行digest各2个byte；mapping/外部证据的SHA-256按精确UTF-8 `Synthetic:`+id；零原始光学回投影/重复残差只是解析fixture事实，物理误差门仍非零。GeometryDefinition.Identity和各完整闭包须独立重算，80-byte stamp和旧186-byte向量原样保留。

冻结的期望：Plan.Rows=2且误差为空，插值权重0.25/0.75，实际qY=0.001/0.003m；Execute有2个面、Coverage.Complete（只指所需的2个几何输出点）、几何用途Usable为fixture响应。RequiredOutputWindows只含输出像素(1,2)/(2,2)，common=(0.00025,0.002)/(0.0005,0.002)m；Locate首点→(0.25,0.5)、T1、权重(0.5,0.25,0.25)。TileKey=(rev1,lod0,x0,y1,purpose,"gray")的2×2核心为输出x0/1、y2/3，仅局部(1,0)有效：Pixels=[0,30,0,0]、ValidityBits=[0x02]；这里nearest行0.5按floor(+0.5)取原row1/col0=30，不把图像当计量真值。采样位移sqrt(0.00025²+0.001²)<0.002m。q_ref=0，不重复加运动；另一所需点在邻tile，可在覆盖验证中只做几何查询，Host不声称已保存所有图像字节。

八项 Limits 和=.00156001m<=Total .0016m；本fixture最坏面上 E_pose=.000006、E_blur=.00020005、E_mesh=.00100125、E_sync=0、其它Optical/Registration/Chord各.000001与Numeric=.00000001，相加=.00121031m，均在fixture门内。MaxTriangles=2、MaxTopologyPairs=8，空/非法/异epoch测试以明确 with 改字段生成，须重seal相应content而不是靠篡改摘要模拟合法坏输入。

#### C.6.2 独立规范投影与端口实施块

`HostBinary.Hash(label,value,removeSelfDigest=false)` 的完整算法固定如下（测试实现，不是新增产品codec API）：构造MemoryStream/BinaryWriter（UTF-8严格、无BOM、LittleEndian），写头4d5a4301/u32入口UTF-8长度/原入口字节；以A.2原值tag写根。其record schema是 **A.1/C.4每个声明的构造字段名字符串数组，逐字按声明顺序硬编码**，不调用GetProperties枚举顺序，也不调用产品encoder；按这份数组对公开 DTO 逐名GetProperty取得值。schema构建不得用运行时反射/属性排序猜测字段序。内容根removeSelfDigest=true时仅根Identity子ValueRef的字段数组由[Id,Revision,Digest]改为[Id,Revision]及字段数2；其它ValueRef仍3字段。把原Ref的占位Digest删掉，所以Seal前后的content预像相同。集合set字段精确列在C.5，按独立完整元素字节无符号词典序排序（重复拒绝），其余list原序；空不为null。Type.Name精确匹配schema；枚举type.Name和明确整数值，不内联wrapper。所有primitive tags、Guid文本顺序、100ns epoch UTC、TimeSpan.Ticks、-0/+0、UInt32 checked长度与非法UTF-8/非有限拒绝均逐字使用A.2。显式根投影分别为 `Hash("line04-execute", view.Request)` 与 `Hash("line04-execute", analysis.Request)`，不删OperationId/deadline/budget，不删nested digest。这两份构造输入本身就是完整规范投影的独立输入预期，不能用80-byte stamp替代完整request身份断言。

2026-10-11 只用标准库inline独立构造上块的全字段值及构造类型/tag、精确set规则、依赖图，从字段重建的预期如下；这是文档编码核对，没有调用产品encoder，没有C# build/test。完整预像可按C.6.1/A.2重建，不在正文堆叠13KB hex或辅助manifest。

| 消费者/完整投影 | bytes | SHA-256 |
|---|---:|---|
| view.Request，line04-execute | 13406 | `3ca6bce6c22085f0a3cd89b8a2f859e7745aa144aace29f975a8371f0032f2f6` |
| analysis.Request，line04-execute | 13422 | `c44394bbbe61e596f4c85213946272bcd6efab6c6ffeae5e4c45810dd08dcf8c` |
| 两Host共用definition，line04-geometry（只删Identity.Digest） | 以精确schema编码 | `d4fe517e2e4696eebe86b52c5a74a032960bafc09c7a2e4374b1e75b2de507e2` |
| 两Host共用trace，line04-trace-content（同上） | 以精确schema编码 | `8b24e795d570137236b0c7e0d5fa10829cf00d1d782611500b669298f3a7bcc9` |
| 两Host共用timing，line04-timing（同上） | 以精确schema编码 | `3662da2aa4ab45a4cc8aaff75f06ef03042ca4d6ac7cd30f6a80c2b558044845` |
| view artifact，line04-artifact（同上） | 以精确schema编码 | `36d8fcfe2801c46aa2ca01d4311e2b012a9127f6e0a76455939d96b7f528825f` |
| analysis artifact，line04-artifact（同上） | 以精确schema编码 | `4dc769ae8de301dcff16090e668ea24517874e88a0688d60962a7fe98b38e912` |

这张表的消费者是两个Host的输入身份/闭包断言与主控接收，不是另一套活动合同。Qualification/外部证据不重算成本模块content hash；这些Synthetic外部Ref的字节仅是固定fixture证据标记，Snapshot应答由该fixture独立Owner/Scope脚本绑定，不可当真实Published/Qualification序列化格式或上游SolvedParameters。两个Host独立fake权威不代表同一真实Owner允许同asset Id/revision覆盖内容。

`SyntheticPorts.cs` 必须提供以下本测试Host构造和操作（internal测试类，不发布进产品API）：

```csharp
internal enum SyntheticReply { Immediate, Gate, Revoke }
internal sealed record AuthorityStep(SyntheticReply Reply);
internal sealed record AdapterStep(SyntheticReply Reply);
// 各类成员的唯一实现行为见下表；不再让实施者另选SDK/模拟库。
internal sealed class SyntheticHostClock(DateTimeOffset initialUtc) : TimeProvider
{
    private readonly long start = System.Diagnostics.Stopwatch.GetTimestamp();
    public override DateTimeOffset GetUtcNow() => initialUtc +
        TimeSpan.FromSeconds((double)(System.Diagnostics.Stopwatch.GetTimestamp()-start)/TimestampFrequency);
    public override long GetTimestamp() => System.Diagnostics.Stopwatch.GetTimestamp();
    public override long TimestampFrequency => System.Diagnostics.Stopwatch.Frequency;
    // CreateTimer沿BCL TimeProvider默认有限timer；不冻结单调时间/不使超时永远不触发。
}
```

以下是future Tests类的**签名规格**（正文有意不填占位方法体；实现严格按下表），构造/脚本和所需成员均显式固定；并非宣称这些类已经存在。返回ValueTask的方法必须真的实现对应公共interface，不能用扩展方法/隐藏service locator拼装：

```csharp
internal sealed class SyntheticAuthority : ILineScanAuthorityPort
{
    public SyntheticAuthority(SyntheticLineFixture fixture, TimeProvider clock,
        IReadOnlyList<AuthorityStep> resolveSteps, IReadOnlyList<AuthorityStep> opticalSteps);
    public int ResolveCalls { get; }
    public int OpticalCalls { get; }
    public int PendingCount { get; }
    public bool CancellationRequested { get; }
    public void CompleteAll();
    public ValueTask<LineAuthorityResult> ResolveAsync(LineAuthorityRequest request, CancellationToken cancellationToken);
    public ValueTask<LineOpticalAuthorityResult> ResolveOpticalAsync(LineOpticalAuthorityRequest request, CancellationToken cancellationToken);
}
internal sealed class SyntheticFrames : IMosaicFramePort
{
    public SyntheticFrames(SyntheticLineFixture fixture, TimeProvider clock);
    public int Acquires { get; }
    public int ActiveLeases { get; }
    public ValueTask<FrameLeaseResult> AcquireAsync(FrameReadRequest request, CancellationToken cancellationToken);
}
internal sealed class SyntheticAdapter : ILineScanAdapter
{
    public SyntheticAdapter(SyntheticLineFixture fixture, TimeProvider clock, IReadOnlyList<AdapterStep> renderSteps);
    public int ProjectCalls { get; }
    public int RenderCalls { get; }
    public int PendingCount { get; }
    public int ActiveBuffers { get; }
    public int ReleasedBuffers { get; }
    public bool CancellationRequested { get; }
    public void CompleteAll();
    public ValueTask<LineTraceResult> ProjectFirstLineAsync(LineTraceWork request, CancellationToken cancellationToken);
    public ValueTask<LineTileRenderResult> RenderTileAsync(LineRenderWork request, CancellationToken cancellationToken);
}
internal sealed class HostRecoveryRoot
{
    public HostRecoveryRoot(int capacity, TimeProvider clock);
    public int RetainedCount { get; }
    public void Hold(string key, IMosaicServiceV04 service, SyntheticAuthority authority,
        SyntheticAdapter adapter, SyntheticFrames frames);
    public bool ConfirmAndRemove(string key, DrainReceipt receipt);
    public ValueTask<bool> ObserveLeaseReleaseAsync(IAsyncDisposable lease, DateTimeOffset deadlineUtc);
    public ValueTask<bool> TryRecoverAsync(string key, DateTimeOffset deadlineUtc, CancellationToken cancellationToken);
}
```

SyntheticUnusedCoordinates的public无参构造实现IMosaicCoordinatePort两方法；SyntheticUnusedAssets(TimeProvider clock)实现A.1的ResolveAsync/PublishUnqualifiedAsync/QueryPublishAsync三方法；两类另有`public int Calls {get;}`。SyntheticDiagnostics(int capacity)实现TryWrite和Drops，所有计数只读公开到测试，修改权保留类内。本节使用的SyntheticFrameLease和SyntheticBuffer均由对应fake构造并计数，不允许Host new后绕过fake资源根。

| 测试类/端口 | 精确行为和必须实现的查询/控制 |
|---|---|
| SyntheticAuthority : ILineScanAuthorityPort | 构造防御复制fixture与两脚本。Resolve/Optical各有独立Calls计数和Step索引，超脚本末项固定复用Immediate（不得随机）。Resolve核完整Source/Scope/Purpose/精确所有本模块content digest与fixture，失败Snapshot=null/MZ-013；Immediate返回fixture.Source.Snapshot/无error；Revoke返回null/MZ-015；Gate把原TCS<LineAuthorityResult>放Pending字典并保持Task不完成，令牌仅记CancellationRequested，不能删除原Task。公开internal `int ResolveCalls/OpticalCalls/PendingCount`、`void CompleteAll()`，Completes以原fixture Snapshot或ExactApplicable=true结束所有Gate，便于根Owner恢复。资源Ledger始终真实：PendingCount未零时pending不归零。Optical只核Definition精确内容及Synthetic光学引用，Immediate=ExactApplicable true；不从InitialParameters读解出值 |
| SyntheticFrames : IMosaicFramePort | Acquire校验FrameRef所有字段/Scope/窗口均属fixture，checked裁剪，把原4bytes按行复制到新compact byte[]，Source=原FrameRef、Window=实际窗口、StrideBytes=window.Width。IFrameLease.Digest=裁剪字节H；不是伪装全幅hash。测试实现 lease DisposeAsync 用Interlocked一次归还，不对重复Dispose减两次；释放后Pixels访问抛ObjectDisposedException。内部 `Acquires,ActiveLeases`可读；未知引用返回null/MZ-002。用全幅时4bytes、用整行时2bytes，不返回padding。预算与deadline先检，Ledger计真实字节/lease，无native |
| SyntheticAdapter : ILineScanAdapter | ProjectFirstLine检查定义精确相等，返回fixture.Artifact.Trace（候选未资格，不调用cv2）；Candidate的Id按C.5由本TraceRequest摘要派生，content重新seal。Render只支持该fixture正常manifest/上述TileKey，先检查输入lease字节窗口/linehash，再返回**独立**2×2 buffer [0,30,0,0]/bits02；不复制原帧假冒输出。render脚本Immediate直接返回，Gate保留TCS<LineTileRenderResult>与原LineRenderWork直到CompleteAll，忽略令牌完成仅记录取消；Revoke不是render分支，构造时拒绝。`ProjectCalls/RenderCalls/PendingCount/ActiveBuffers/ReleasedBuffers`与`CompleteAll()`可读控。Late buffer由service接收并释放，不能因为观察取消直接回收仍在Task里的buffer |
| SyntheticBuffer : ILineTileBufferLease | Frame=(Id="Synthetic-output",hash=H([0,30,0,0]),2×2,stride2/capacity4,Byte/1/Interleaved/Identity/rev1,ValidWindow全幅,Mask=null,Storage=ValueRef("Synthetic-output-bytes",rev1,H(output)),PixelFrame="output-pixel")。Contributions=[SourceContribution(fixture.FovId,原Frame,全幅源window,RectD(0.00025,0.002,0.0005,0.003,"common"),Nearest,null,原Role,Resampled,0)]；RectD只是该位的半开输出pixel cell，不把整个tile当支持。Pixels与ValidityBits保持防御副本，释放同一个owner计数/原Task后续不再访问；DisposeAsync幂等，ReleasedBuffers只增一次，不隐藏异步读取 |
| SyntheticUnusedCoordinates : IMosaicCoordinatePort | 两同步方法都先增加Calls再抛InvalidOperationException("unexpected coordinate port")，line纯geometry不得依赖此port；Host断言Calls=0 |
| SyntheticUnusedAssets : IMosaicAssetPort | Resolve/Publish/QueryPublish三异步方法同样计数后抛unexpected；line不得调用v0.3 AssetPort，Host断言Calls=0；不是用成功空artifact掩盖未接线 |
| SyntheticDiagnostics : IMosaicDiagnostics | 构造capacity>0；TryWrite将通知最多保存capacity，满则返回false，另Drops计数。无log IO/锁外回调/隐藏线程，不改请求或清理结论 |
| 每个fake的ResourceLedger | `PlannedBytes=CurrentBytes=实际当前受fake持有的byte数`、PeakBytes=记录峰值、CpuMilliseconds=本次Stopwatch经过ms、LogicalReadBytes/DecodedBytes=该实例真实累计byte数，TilesRendered=实际buffer数、ActiveSourceLeases/NativeHandles/PendingPortCalls等实计（fake NativeHandles=0有依据）；PeakConcurrency按活跃call计。StartedUtc=clock.GetUtcNow()，未完成Task时三个release时间null。资源退出后只给InternalReleasedUtc，AllOutputReleasedUtc由真实buffer归还确认；service在自己的总ledger合并，不用fake全零统计覆盖自身pending |

Gate用 `TaskCompletionSource<T>(RunContinuationsAsynchronously)`，锁内登记/出队，锁外TrySetResult；CompleteAll不得新建operation或第二buffer，Id相同重复调用复用原TCS。脚本仅模拟本地协议，不是真实撤权服务、相机、运动轨迹或光学资产。两Host测试根也须可接纳超时后的service/ports/adapter引用，具体收尾C.6.3；不存在“Gate一直不完成但finally把fixture丢掉”的测试PASS。

#### C.6.3 两个有限 Host 的执行与根Owner

`HostRecoveryRoot`构造capacity=4，每个Host创建自己的根。其 `Hold(string key, IMosaicServiceV04 service, SyntheticAuthority authority, SyntheticAdapter adapter, SyntheticFrames frames)` 在**调用前**登记强引用，重复key冲突拒绝，容量不足拒绝开工；`ConfirmAndRemove(key,DrainReceipt receipt)` 只在Drained/ActiveOperations空/PendingPortCalls=0/OutstandingOutputLeases=0，且对应fake PendingCount/ActiveBuffers/ActiveLeases全0、所有Dispose完成时移除。`RetainedCount`是实际持有service记录数，另有有限lease/DisposeTask字典；`TryRecoverAsync(key,DateTimeOffset deadlineUtc,CancellationToken ct)`先CompleteAll→观察已登记lease DisposeTasks→有限Drain→有限Dispose→最后再Drain/核fake零计数→ConfirmAndRemove；不能移除未完成Task。ObserveLeaseReleaseAsync先强持lease、只调用一次DisposeAsync并保存实际Task，再用 `.WaitAsync(remaining)`，Task正常完成才返回true且移除lease记录；超时/故障返回false并保留，故障不假归还。重复Observe查原Task，不新调用Dispose。Service.Dispose同样只调用一次/保存Task。每次最多恢复到给定deadline，不无限sleep/poll；窗口到期返回false，保持强引用并把测试结果标PendingRecovery（非PASS）。测试Exe还有单一外层10秒硬截止，只用来判fail，不能拿进程终止冒充归还。无自动创建第二service/换operation/重新render。

**清理与业务分轴：** ObserveLeaseReleaseAsync、TryRecoverAsync、ConfirmAndRemove、RemoveIfEmpty在这里都是有限且**不抛出**的清理路径：实际Dispose调用同步抛出、Task故障/取消、CompleteAll/Drain/Clock/回执读取错误、观察超时与负remaining都捕获到原根的预分配有界cleanup故障槽，返回false；不调用可能抛出的诊断/业务回调，不在finally里Require。不能把await失败转换为Drained。DisposeTask仍原样保存，故障不从资源字典删掉，未知回执不移根。TryRecover只有完整可信的原service/原key回执和全部真实零计数、原DisposeTask正常结束时才ConfirmAndRemove；Field/ID缺失、不同key、负计数、Drained与非零计数矛盾或回执不可观察都false/保留。下一次有限恢复可以凭新取得的完整可信证据确认，但不得改写历史cleanup故障或原业务异常。

两个Host以`ExceptionDispatchInfo? businessFailure`保存**第一条原业务异常及堆栈**；`cleanupOk`记录观察/恢复/根确认的独立结果，任何false保持该次cleanup失败事实。finally只做上述不抛清理和bool记账。退出先将businessFailure与cleanupOk两轴留在caller持有的原Root/真实Host Task（fixture故障槽），再优先`businessFailure.Throw()`；只有业务没有异常且cleanup失败时，才在finally之后抛清理断言。业务Failed不能因cleanup成功转PASS，业务成功+cleanup失败同样退出非零；两轴均成功才PASS。finally里的异常不得覆盖原业务失败，后续恢复不能重写exit。签名不新增产品方法/DTO，故障槽只是已有测试Root的实现状态。

下方`root.BusinessFailure`、`root.CleanupFailure`、`root.CleanupSucceeded`是`HostRecoveryRoot.cs`内已有测试根的internal存储字段，类型分别为`System.Runtime.ExceptionServices.ExceptionDispatchInfo?`、`Exception?`、`bool?`，构造时为null。它们只存引用/值，赋值不分配、不校验、不调用回调且不抛；前两项只保存首次故障，第三项记录本次Host清理结果，退出后冻结。Root内部捕获的首个cleanup异常也写入同一CleanupFailure，后方用`??=`补入参数求值/外层异常，不能用局部cleanupFailure为null推断没有故障。超时、无效回执等返回false但没有异常对象时，原因保留在原预分配故障槽；CleanupSucceeded=false仍独立成立。正常流程中的lease归还及finally后的资源/移根断言均计入cleanup轴。业务失败时原Root留在registry供caller读取；后续恢复只更新资源事实，不覆盖这三个历史结果。

**构造前置与槽预留：** Synthetic夹具/端口/Clock/Root构造和registry.Add只分配托管值/固定容量槽，不创建Task/Timer/订阅/后台派发/借帧/native或外部IO；registry容量与该Root的第一个组件槽在Add成功时已经预留。Host启动前由caller确认该registry为空且capacity>=1，Root(capacity=4)私有固定数组第0槽绑定本Host唯一key，Hold只将已创建实例引用提交到此槽，不在其内分配/重新竞争容量、不调用外部回调，预留有效时不抛/不拒绝。两个Host的Hold均在首个Validate/Plan/异步调用之前，不存在开工后容量失败路径。

本模块`MosaicModule.Create`两个重载及`AsunImageLineScanAdapter.Create`均为纯Options/依赖结构校验和惰性托管实例构造：成功前后均无作业/Task/Timer/进度worker/native/端口调用，首次实际服务调用才启动对应工作。参数非法或构造异常时没有租约、句柄、pending或任何外部副作用需要排空；局部托管数组不当作活动资源。不能在Create里先启动worker再抛，或让端口构造函数隐式借设备。因而下方service.Create在业务try之前失败时，caller取得的仍是原构造异常，cleanup轴是NoWork/无资源，而非伪造运行Drained；已登记的空Root由caller仅按空槽核对移除。若将来实现必须改变这个构造约束，需先修本指导，不能自行把带工作Create混入现块。

以下非generic辅助只消费Execute/Query的公开LineScanResult，不猜隐藏Clock或其它Result分支：

```csharp
private static async Task<LineScanResult> NeedResult(IMosaicServiceV04 service,
    MosaicCallReply<LineScanResult> reply, MosaicOperationId operationId,
    DateTimeOffset deadlineUtc, TimeProvider clock)
{
    if (reply.Observation==ObservationStatus.Returned && reply.Result!=null) return reply.Result;
    long began=clock.GetTimestamp();
    for (int i=0;i<64;i++)
    {
        var remaining=deadlineUtc-clock.GetUtcNow();
        if (remaining<=TimeSpan.Zero || clock.GetElapsedTime(began)>TimeSpan.FromSeconds(5))
            throw new TimeoutException("Synthetic Execute observation ended");
        var state=await service.QueryLineScanAsync(operationId,CancellationToken.None).AsTask().WaitAsync(remaining);
        if (state.Runtime!=null) return state.Runtime; // 失败也原样交给Host，不重发Execute。
        await Task.Delay(TimeSpan.FromMilliseconds(1),clock,CancellationToken.None).WaitAsync(remaining);
    }
    throw new TimeoutException("Synthetic query limit reached");
}
```

Tile reply非Returned没有可取lease，走原IDQuery/Recovery，不靠metadata重新获取输出。下面两个函数所用 `HostRecoveryRegistry` 由测试Exe caller各自new并传入，不能在Host函数内创建后无外部Owner持有。其构造`HostRecoveryRegistry(int capacity)`、`Add(HostRecoveryRoot root)`、`RemoveIfEmpty(HostRecoveryRoot root)`和只读`Roots`都在`HostRecoveryRoot.cs`实现：固定容量/锁内防重复存强引用；Remove只在root service+lease+DisposeTask字典全空时成功。上层必须保留正在运行的Host Task到它真实结束，WaitAsync超时不是删除Task许可。

```csharp
// LineScan/Hosts/LineViewHost.cs；没有UI/Dispatcher，所有待清理强引用先登记。
internal static async Task RunLineViewHostAsync(HostRecoveryRegistry registry)
{
    var f = new SyntheticLineFixture(analysis:false);
    var clock = new SyntheticHostClock(SyntheticLineFixture.T0);
    var root = new HostRecoveryRoot(4,clock);
    registry.Add(root);
    var frames = new SyntheticFrames(f,clock);
    var authority = new SyntheticAuthority(f,clock,[new(SyntheticReply.Immediate)],[new(SyntheticReply.Immediate)]);
    var adapter = new SyntheticAdapter(f,clock,[new(SyntheticReply.Immediate)]);
    var coordinates = new SyntheticUnusedCoordinates();
    var assets = new SyntheticUnusedAssets(clock);
    var limits = new ServiceLimits(4,16,TimeSpan.FromSeconds(10),4,1024*1024,
        8,1024*1024,TimeSpan.FromMilliseconds(20),8,1024*1024);
    var core = new MosaicModuleOptions(f.Epoch,frames,coordinates,null,assets,null,
        new SyntheticDiagnostics(16),clock,limits,null);
    var service = MosaicModule.Create(new MosaicModuleOptionsV04(core,authority,adapter));
    root.Hold("view",service,authority,adapter,frames);
    ILineScanTileLease? held = null;
    System.Runtime.ExceptionServices.ExceptionDispatchInfo? businessFailure = null;
    Exception? cleanupFailure = null;
    bool cleanupOk = true;
    try
    {
        var v = service.ValidateLineScan(f.Request); Require(v.IsValid && v.Errors.Count==0);
        var plan = service.PlanLineScan(f.Request);
        Require(plan.Validation.IsValid && plan.Rows.Count==2 && plan.TriangleUpperBound==2);
        Require(authority.ResolveCalls==0 && frames.Acquires==0 && adapter.ProjectCalls==0);
        var call = await service.ExecuteLineScanAsync(f.Request,CancellationToken.None);
        var result = await NeedResult(service,call,f.Request.OperationId,f.Request.DeadlineUtc,clock);
        Require(result.Manifest!=null && result.Manifest.Triangles.Count==2 && result.Errors.Count==0);
        var manifest = result.Manifest!;
        var point = service.LocateLineScanPoint(new LinePointRequest(manifest.Identity,f.Source.Id,
            SyntheticLineFixture.P(0.00025,0.002),f.Scope));
        Require(point.Status==LinePointStatus.Available && point.SourcePixel?.Frame=="sensor-pixel" &&
            Close(point.SourcePixel?.Column,0.25) && Close(point.SourcePixel?.Row,0.5));
        var state = await service.QueryLineScanAsync(f.Request.OperationId,CancellationToken.None);
        Require(state.Runtime?.Manifest?.Identity==manifest.Identity && authority.ResolveCalls==2);
        var tile = new LineScanTileRequest(new MosaicOperationId(f.Epoch,2),manifest.Identity,
            new TileKey(new Revision(1),0,0,1,f.Request.Purpose,"gray"),f.Scope,f.Request.DeadlineUtc,f.Budget);
        var reply = await service.GetLineScanTileAsync(tile,CancellationToken.None);
        Require(reply.Observation==ObservationStatus.Returned && reply.Result?.Status==TileStatus.Available);
        held = reply.Result!.Lease!;
        Require(held.Pixels.Span.SequenceEqual(new byte[]{0,30,0,0}) &&
            held.ValidityBits.Span.SequenceEqual(new byte[]{2}));
        // 消费完仍故意持有，证明Drain不偷归还输出；可靠Query不给出lease/Memory。
        var tileState = await service.QueryLineScanAsync(tile.OperationId,CancellationToken.None);
        Require(tileState.State==ExecutionState.OutputHeld && tileState.Tile?.Delivery==OutputDeliveryState.Delivered);
        var blocked = await service.DrainAsync(clock.GetUtcNow().AddMilliseconds(30),CancellationToken.None);
        Require(blocked.Status==DrainStatus.DrainUnknown && blocked.OutstandingOutputLeases==1);
        try
        {
            bool released = await root.ObserveLeaseReleaseAsync(held,clock.GetUtcNow().AddMilliseconds(200));
            cleanupOk &= released; if (released) held=null;
        }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
        Require(coordinates.Calls==0 && assets.Calls==0);
    }
    catch (Exception error)
    {
        businessFailure = System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(error);
    }
    finally
    {
        // 两项独立捕获，第一项失败不跳过第二项；clock/参数求值异常也不覆盖业务。
        try { if (held!=null) cleanupOk &= await root.ObserveLeaseReleaseAsync(held,clock.GetUtcNow().AddMilliseconds(200)); }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
        try { cleanupOk &= await root.TryRecoverAsync("view",clock.GetUtcNow().AddMilliseconds(500),CancellationToken.None); }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
    }
    // 资源断言和移根失败属于cleanup；原业务失败时保留Root供caller读取。
    try { Require(root.RetainedCount==0 && frames.ActiveLeases==0 && adapter.ActiveBuffers==0); }
    catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
    if (businessFailure==null && cleanupOk)
    {
        try { Require(registry.RemoveIfEmpty(root)); }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
    }
    root.BusinessFailure ??= businessFailure; root.CleanupFailure ??= cleanupFailure; root.CleanupSucceeded=cleanupOk;
    if (businessFailure!=null) businessFailure.Throw(); // 原异常/堆栈优先，cleanup证据仍在原根。
    Require(cleanupOk); // 仅在没有业务异常时，于finally外报告清理失败。
}
```

`Require(bool)`只在false时抛InvalidOperationException，测试Exe退出非零；`Close(double? actual,double expected)`固定为`actual.HasValue && double.IsFinite(actual.Value) && Math.Abs(actual.Value-expected)<=1e-12`，此容差只断言Synthetic算例的pixel/m数值，不改物理门。上例无论业务断言成功/抛异常均执行根恢复；Recover/真实零计数/移根任一不满足，cleanup轴失败且根仍挂在Exe级HostRoot集合中；已有业务异常仍优先原样抛出，否则finally外的Require报告清理失败。`ObserveLeaseReleaseAsync`和Recover共同保存实际DisposeTask，不能因为观察超时先设置held=null/移除根。

```csharp
// LineScan/Hosts/LineAnalysisHost.cs；独立Epoch/Scope/Source/所有可变端口和根。
internal static async Task RunLineAnalysisHostAsync(HostRecoveryRegistry registry)
{
    var f = new SyntheticLineFixture(analysis:true);
    var clock = new SyntheticHostClock(SyntheticLineFixture.T0);
    var root = new HostRecoveryRoot(4,clock);
    registry.Add(root);
    var frames = new SyntheticFrames(f,clock);
    var authority = new SyntheticAuthority(f,clock,[new(SyntheticReply.Immediate)],[new(SyntheticReply.Immediate)]);
    var adapter = new SyntheticAdapter(f,clock,[new(SyntheticReply.Gate)]);
    var coordinates = new SyntheticUnusedCoordinates();
    var assets = new SyntheticUnusedAssets(clock);
    var limits = new ServiceLimits(4,16,TimeSpan.FromSeconds(10),4,1024*1024,
        8,1024*1024,TimeSpan.FromMilliseconds(20),8,1024*1024);
    var service = MosaicModule.Create(new MosaicModuleOptionsV04(
        new MosaicModuleOptions(f.Epoch,frames,coordinates,null,assets,null,
            new SyntheticDiagnostics(16),clock,limits,null),authority,adapter));
    root.Hold("analysis",service,authority,adapter,frames);
    IFrameLease? original = null;
    System.Runtime.ExceptionServices.ExceptionDispatchInfo? businessFailure = null;
    Exception? cleanupFailure = null;
    bool cleanupOk = true;
    try
    {
        Require(service.ValidateLineScan(f.Request).IsValid);
        var plan = service.PlanLineScan(f.Request);
        Require(plan.Rows.Count==2 && plan.Rows.All(x=>x.Errors.Count==0));
        Require(authority.ResolveCalls==0 && frames.Acquires==0 && adapter.ProjectCalls==0);
        var call = await service.ExecuteLineScanAsync(f.Request,CancellationToken.None);
        var result = await NeedResult(service,call,f.Request.OperationId,f.Request.DeadlineUtc,clock);
        var manifest = result.Manifest!; Require(manifest!=null && result.Errors.Count==0);
        var point = service.LocateLineScanPoint(new LinePointRequest(manifest.Identity,f.Source.Id,
            SyntheticLineFixture.P(0.00025,0.002),f.Scope));
        Require(point.Status==LinePointStatus.Available && point.Triangle?.Half==1);
        // 独立消费原图，不从显示tile推计量：源row0/col0=10，定位p只是软件几何。
        var read = await frames.AcquireAsync(new FrameReadRequest(f.Source.Frame,new PixelRect(0,0,2,2),
            f.Scope,f.Request.DeadlineUtc,f.Budget),CancellationToken.None);
        original = read.Lease!; Require(original!=null && original.Pixels.Span[0]==10);
        try
        {
            bool released = await root.ObserveLeaseReleaseAsync(original,clock.GetUtcNow().AddMilliseconds(200));
            cleanupOk &= released; if (released) original=null;
        }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
        var state = await service.QueryLineScanAsync(f.Request.OperationId,CancellationToken.None);
        Require(state.Runtime?.Manifest?.Identity==manifest.Identity);
        var tile = new LineScanTileRequest(new MosaicOperationId(f.Epoch,2),manifest.Identity,
            new TileKey(new Revision(1),0,0,1,f.Request.Purpose,"gray"),f.Scope,f.Request.DeadlineUtc,f.Budget);
        using var cancel = new CancellationTokenSource();
        var observed = await service.GetLineScanTileAsync(tile,cancel.Token);
        Require(observed.Observation==ObservationStatus.PendingDrain && observed.Result==null && adapter.PendingCount==1);
        cancel.Cancel(); // 不创建第二GetTile；Gate假后端不结束，原owner仍持有work/输入。
        var blocked = await service.DrainAsync(clock.GetUtcNow().AddMilliseconds(30),CancellationToken.None);
        Require(blocked.Status==DrainStatus.DrainUnknown && root.RetainedCount==1 && frames.ActiveLeases>0);
        adapter.CompleteAll(); // 迟到buffer产生；观察已结束，无合法收件人，服务释放它。
        var drain = await service.DrainAsync(clock.GetUtcNow().AddMilliseconds(500),CancellationToken.None);
        Require(drain.Status==DrainStatus.Drained && adapter.ReleasedBuffers==1 && adapter.ActiveBuffers==0);
        var late = await service.QueryLineScanAsync(tile.OperationId,CancellationToken.None);
        Require(late.Tile?.Delivery!=OutputDeliveryState.Delivered && late.Resources?.OutstandingOutputLeases==0);
        Require(coordinates.Calls==0 && assets.Calls==0);
    }
    catch (Exception error)
    {
        businessFailure = System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(error);
    }
    finally
    {
        try { if (original!=null) cleanupOk &= await root.ObserveLeaseReleaseAsync(original,clock.GetUtcNow().AddMilliseconds(200)); }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
        try { cleanupOk &= await root.TryRecoverAsync("analysis",clock.GetUtcNow().AddMilliseconds(500),CancellationToken.None); }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
    }
    // 资源断言和移根失败属于cleanup；原业务失败时保留Root供caller读取。
    try { Require(root.RetainedCount==0 && frames.ActiveLeases==0 && adapter.PendingCount==0); }
    catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
    if (businessFailure==null && cleanupOk)
    {
        try { Require(registry.RemoveIfEmpty(root)); }
        catch (Exception error) { cleanupOk=false; cleanupFailure ??= error; }
    }
    root.BusinessFailure ??= businessFailure; root.CleanupFailure ??= cleanupFailure; root.CleanupSucceeded=cleanupOk;
    if (businessFailure!=null) businessFailure.Throw();
    Require(cleanupOk); // 仅在没有业务异常时，于finally外报告清理失败。
}
```

分析Host的Gate由脚本在Render登记时立即建TCS；即使CPU慢导致首观察为WaitCancelled/TimedOut，也不得把它判正常成功，而走根恢复并fail（不能扩时到无限）。正常期望PendingDrain不等于native真实已退出。额外撤权断言使用全新独立fixture/service：ResolveSteps=[Immediate,Revoke]，Execute.Manifest=null/Errors含MZ-015，Frame/native调用0；仍按同Root恢复。它是新的测试case，不在同operation换摘要重试；原两Host正常request仍完整/不可变。

测试Exe入口串行创建`viewRegistry=new HostRecoveryRegistry(1)`、`analysisRegistry=new HostRecoveryRegistry(1)`；启动每个Host前验证其registry容量可用，分别保存 `viewTask=RunLineViewHostAsync(viewRegistry)` 与 `analysisTask=RunLineAnalysisHostAsync(analysisRegistry)` 的真实Task，分别用WaitAsync(10s)观察并断言两个registry都空。任一超时/断言/Dispose失败退出码非零；调用方仍持有两个registry与Task，对Roots仅再做一次500ms有界TryRecover并核Task实际完成，不清空集合。失败后Task/根仍未退出时保留PendingRecovery记录和强引用于该Exe进程寿命，不用进程杀死作为归还证据；测试runner硬截止是fail用途，下一次测试不能继承这条未确认资源事实。

Exe对每个Host分别捕获原Task异常/观察超时并保存首个`ExceptionDispatchInfo`及非零exit事实，然后才做一次外层恢复；一项失败仍观察另一项。每个Root的deadline求值、TryRecover与空根移除分别独立try/catch，false或异常只记外层cleanup结果，不能抛出覆盖原异常、清空registry或把exit改回0。Host在Create前失败时，原Task保存构造异常，空Root没有组件/lease/DisposeTask；caller记录NoWork并仅用RemoveIfEmpty核空槽移除，不调用虚构service Drain。对仍运行的Host Task不移除其Root，即使快照暂时为空；外层恢复须串行接在Host真实结束之后，10秒观察超时而Task未完时保留根，不与Host finally并发释放。外层恢复后再读原Task与两轴，恢复成功不改变此前业务/cleanup失败历史。

#### C.6.4 M-L2 的确定公开构造、资源根与实际装配

下面的类/Options/Owner由本模块决定，属于M-L2 Adapter工程公共面，不是AsunImage封装API，不猜上游Solved字段。namespace `Asun.Modules.Mosaic.AsunImage`；引用Core及用户现有AsunImage程序集，**没有**halcondotnet直接引用/动态SDK探测。公共类只在首次具体call使用native，不初始化窗口/相机/轴或隐式静态模型。

```csharp
public enum AsunImageLineDrainState { Drained=0, DrainUnknown=1, WaitCancelled=2 }
public record AsunImageLineResources(bool Closing, uint ActiveCalls, uint PendingCalls,
    uint NativeHandles, long NativeBytes, uint OwnedBuffers, long OwnedBufferBytes,
    uint BorrowedSourceLeases, uint PendingBufferDisposals);
public record AsunImageLineDrainReceipt(AsunImageLineDrainState State,
    AsunImageLineResources Resources);
public record AsunImageLinePendingCall(Guid OwnerEpoch, long Sequence,
    Task Completion, string Reason);
public interface IAsunImageLineResourceOwner
{
    void Retain(AsunImageLineScanAdapter adapter, AsunImageLinePendingCall pending);
    void ConfirmReleased(Guid ownerEpoch, long sequence);
}
public record AsunImageLineScanAdapterOptions(Guid OwnerEpoch, uint MaxConcurrentCalls,
    uint MaxPendingCalls, uint MaxNativeHandles, long MaxNativeBytes,
    uint MaxOwnedBuffers, long MaxOwnedBufferBytes, TimeSpan MaxObservationWait, TimeProvider Clock,
    IMosaicDiagnostics Diagnostics, IAsunImageLineResourceOwner ResourceOwner);
public sealed class AsunImageLineScanAdapter : ILineScanAdapter, IAsyncDisposable
{
    public static AsunImageLineScanAdapter Create(AsunImageLineScanAdapterOptions options);
    public ValueTask<LineTraceResult> ProjectFirstLineAsync(LineTraceWork request, CancellationToken cancellationToken);
    public ValueTask<LineTileRenderResult> RenderTileAsync(LineRenderWork request, CancellationToken cancellationToken);
    public AsunImageLineResources ReadResources();
    public ValueTask<AsunImageLineDrainReceipt> DrainAsync(DateTimeOffset deadlineUtc, CancellationToken cancellationToken);
    public ValueTask DisposeAsync();
}
```

Options字段全必填，epoch非空/计数bytes正有限/同service Clock与Diagnostics；MaxConcurrentCalls<=MaxPendingCalls，首次native之前预留本call的预算和Owner槽，不接受隐含Unlimited。Owner.Retain必须有界、同步非阻塞且对已预留槽不抛、不拒绝；宿主须在开工前new固定容量根并保证容量>=MaxPendingCalls+所有未归还buffer处置任务。注册key=(OwnerEpoch,Sequence>0单调)，只保留确切adapter/真实Task，不从token推完成；Task字段只是本call及cleanup退出观察，不暴露SDK句柄/图像指针。退出且该call借用输入/native均释放后才ConfirmReleased；owned输出buffer还有自己的处置任务/计数，不能从call Task完成推出OwnedBuffers=0。

上述Owner槽由原NativeResourceRoot的预分配固定数组承接：本例16槽中0–7用于pending call、8–11用于buffer及其处置任务，其余保留；容量判断、唯一key/正Sequence分配、真实完成Task及记录构造均在借入输入/native开工之前完成。槽满或Sequence溢出在准入时拒绝，不启动工作。随后Retain只在原锁内向已预留槽提交确切adapter/pending强引用并发布占用标记；不增长字典、不分配、不做第二次容量竞争、不调用诊断/业务回调。第一次工作必须晚于登记，不能先启动再Retain；原Owner负责检查key与引用身份，未完全释放不复用槽。ConfirmReleased只对原key/原Task执行释放确认，错误key或未完Task保留槽且记录故障，不能删除其它记录；不能把Task fault/cancel单独当作资源已归还。pending记录与输出处置记录虽分槽，但均由同一个原Root承担并统一核零。

Project/Render沿C.1–C.3的既定cv2路径；方法的ValueTask只有native退出、临时句柄释放、borrowed input不再使用后才完成，不能因MaxObservationWait自行返回假Canceled，服务观察层负责PendingDrain。请求token/deadline只停止新阶段/请求取消，不强停线程。仍运行的Task从接纳时就在ResourceOwner登记，最大等待到期不丢。FrameLease只借，不由adapter.Dispose：由service在call实际退出后归还。Render成功的ILineTileBufferLease拥有copy出来的managed buffer/位图，native已释放；service持有并最终转交lease，buffer归还从OwnedBuffers扣除，DisposeAsync若异步未完也登记实际处置Task。超预算在借入/调用native前MZ-010，closing后新call MZ-001/FieldPath="Adapter.Closing"；异常先记录并清理真实native，再完成失败reply。ReadResources有界同步快照、不取句柄、未知释放保留计数。

Adapter.DrainAsync是**只观察**，不自动Closing；截止=min传入deadline,now+Options.MaxObservationWait。Drained要求ActiveCalls/PendingCalls/NativeHandles/NativeBytes/OwnedBuffers/OwnedBufferBytes/BorrowedSourceLeases/PendingBufferDisposals全部0；否则DrainUnknown，token只取消观察。DisposeAsync单次线性化Closing，停止准入/请求取消，有限等上述完全释放；未完返回后adapter及Task仍在宿主ResourceOwner/Root内，不冒称Drained。所有新fake/真实adapter不得用Thread.Abort、后台继续读已归还输入、每call覆盖全局mutable native handle或“Dispose成功==native停”。ResourceOwner不是设备停止/资格Owner。

实际无UI宿主的最小装配必须按以下完整次序（仅装配指导，不声明运行通过）：先new自己的TimeProvider/ServiceLimits/Diagnostics/有限NativeResourceRoot→取得真实FramePort/CoordinatePort/AssetPort及已接收的LineAuthority只读桥→创建`AsunImageLineScanAdapter.Create(new AsunImageLineScanAdapterOptions(ownerEpoch,1,8,16,64*1024*1024,4,16*1024*1024,TimeSpan.FromMilliseconds(250),clock,diagnostics,nativeRoot))`→`MosaicModule.Create(new MosaicModuleOptionsV04(new MosaicModuleOptions(sessionEpoch,framePort,coordinatePort,null,assetPort,null,diagnostics,clock,serviceLimits,null),lineAuthority,adapter))`。数字仅为显式装配算例/资源Profile，不能固定客户性能门；sessionEpoch/ownerEpoch由宿主各自明确生成，nativeRoot和serviceRoot均在调用前登记强引用。MaxOwnedBuffers=4同时约束输出对象数，不能只限制byte而创建无界小buffer；buffer处置记录预留在这4个槽内，超数MZ-010。

`NativeResourceRoot(int capacity)`是M-L2 Tests/真实Host根的具体构造，capacity=16覆盖上例8 pending+4 buffer处置槽；实现IAsunImageLineResourceOwner的两方法并公开internal只读`IReadOnlyList<AsunImageLinePendingCall> ReadPending()`。对应真实Host实施块：

```csharp
// 位于AsunImage.Tests/Hosts/NativeLineHost.cs或真实宿主组合根；不是Core依赖。
// 所有port只接受调用方已装配实例，上游实际桥没接好时不能调用本块。
internal static (IMosaicServiceV04 Service, AsunImageLineScanAdapter Adapter, NativeResourceRoot Root)
    CreateNativeLineHost(Guid sessionEpoch, Guid ownerEpoch, TimeProvider clock,
        IMosaicFramePort framePort, IMosaicCoordinatePort coordinatePort, IMosaicAssetPort assetPort,
        ILineScanAuthorityPort lineAuthority, IMosaicDiagnostics diagnostics,
        Action<AsunImageLineScanAdapter,NativeResourceRoot> retainBeforeServiceCreate)
{
    var root = new NativeResourceRoot(16);
    var adapter = AsunImageLineScanAdapter.Create(new AsunImageLineScanAdapterOptions(
        ownerEpoch,1,8,16,64*1024*1024,4,16*1024*1024,TimeSpan.FromMilliseconds(250),clock,diagnostics,root));
    retainBeforeServiceCreate(adapter,root); // 必须在开工前预留、不得抛出/拒绝。
    var limits = new ServiceLimits(4,16,TimeSpan.FromSeconds(10),4,1024*1024,
        8,1024*1024,TimeSpan.FromMilliseconds(250),8,1024*1024);
    var service = MosaicModule.Create(new MosaicModuleOptionsV04(
        new MosaicModuleOptions(sessionEpoch,framePort,coordinatePort,null,assetPort,null,
            diagnostics,clock,limits,null),lineAuthority,adapter));
    return (service,adapter,root); // caller根在第一条请求之前登记整个tuple。
}
```

如果service.Create失败，已创建adapter仍由retainBeforeServiceCreate挂在caller预先提供的资源恢复根中；异常向caller返回，caller有限恢复它，不能让tuple丢失。进入此块前须校验全部service/options/ports/保留槽，service建立后再补登记service。最后一个Action是同步非阻塞、不抛出/不拒绝的预留槽接收函数，不是任意业务回调；禁止让保留依赖service.Create成功。

原Owner承接规则固定如下：caller在调用CreateNativeLineHost前，已在自己的恢复根固定数组第0组件槽预留本Host的sessionEpoch/ownerEpoch和唯一key；该槽在factory返回或抛出后都由同一caller强持，禁止占用者替换。callback闭包也在factory之前构造，只捕获此原槽；callback将adapter/root强引用写入原槽并置已承接标记，不分配、校验、调用业务或竞争容量。它不是可由插件替换的Action；身份/容量/epoch校验均在factory之前完成。成功返回后caller只把service提交到同一预留组件槽，不新Add/换根；首个Validate/Plan/异步请求前必须断言槽内adapter/root与返回tuple分别ReferenceEquals，service引用相同，epoch/key仍为原预留值，ReadPending为空且ReadResources各活动计数为0。service.Create失败时，caller从原槽直接读取并核对已承接adapter/root、原epoch/key，保存构造异常，再有限恢复原实例；不得因没有tuple返回而删槽、重Create或换Owner。adapter.Create之前失败时该槽仍空，仅按NoWork核空槽；service.Create失败而已有惰性adapter时保留组件槽至原adapter清理完成/零资源核对，不把未开工误写为native Drained证据。这些槽/标记/断言属于既有Host根实现，不新增产品接口或模型。

NativeResourceRoot实施于真实宿主/Adapter.Tests的根Owner（不是新的持久化模块）：锁保护上述固定容量槽保存Retain的adapter/pending，ConfirmReleased仅匹配原key并在Completion实际结束且相应资源确认释放后移除。Host清理先归还自己持有tile/input→service.Drain/Dispose有界观察→adapter.Drain/Dispose有界观察→核service总ledger与adapter ReadResources及Root.Pendings均零→才移除两根。清理步骤各自有限且独立捕获异常，第一项失败不跳过其它安全观察；任何fault/cancel/无效回执/DrainUnknown均保留尚未确认的原实例/原Task/lease，业务异常与cleanup结果按C.6.3分轴。稍后以同实例同key继续有界恢复，不调用第二Create或重试原Render。真实cv2公共参数tuple/指针/内存拷贝的消费编译和HALCON运行仍分别是M-L2门；calibration-assets已解参数的Read/Decode桥仍由其Owner处理，不把本fixture里的解析params当Solved生产输入。

### C.7 逐片六项、算例、验证及精确剩余门

| 切片/当前状态 | 1 边界/真实消费者 | 2 精确公开契约 | 3 装配/无UI | 4 可执行验收断言 | 5 Benchmark | 6 工程/顺序/剩余门 |
|---|---|---|---|---|---|---|
| M-L1 托管线扫几何/目录/生命周期：`ModuleCoreImplementationReady` | 查看/分析Host；仅消费首行trace/实际反馈/权威，不设备动作 | C.2–C.5全部v0.4 DTO；同一 G0/d 与网格前反/身份/有限等待 | C.6.1–C.6.3全字段Synthetic夹具、两个完整request/脚本/有限Host/保留根；LineAdapter可null | 下述正常、边界、误差/权限/资源断言；物理未知不通过 | 行/列/面/候选对/原行hash/IO/CPU/峰值/排空，全部有界 | 原 Core/Tests，`LineScan/`子目录，先值/codec→时钟/行→mesh→authority/lifecycle→双Host；主控已接收六项文档规格；仅软件Core/模拟端口/契约断言准入，不代表代码或真实适配通过 |
| M-L2 首行HALCON投影与Nearest渲染：`PreparationIncomplete` | 同两个Host；唯一native边界 | ILineScanAdapter / LineTraceWork / LineRenderWork；前后权威和lease语义 | C.6.4 AsunImageLineScanAdapter.Create(精确Options)+显式ResourceOwner→Create(v0.4)；确定装配规格限定接收，无隐藏窗口 | 真实row0前反、透视/远心、负方向、边界/窗口/index、退出/迟到句柄 | 同代表图两model，各域正确性/误接受拒绝与P50/P95/P99/峰值；不凭官方推达标 | 预定`src/Modules/mosaic/Asun.Modules.Mosaic.AsunImage/Asun.Modules.Mosaic.AsunImage.csproj`、namespace `Asun.Modules.Mosaic.AsunImage`；tests同模块`Asun.Modules.Mosaic.AsunImage.Tests/`，仅其调用切片需公共重载消费编译/真实native测点；不扫描AsunImage内部 |
| M-L3 物理线扫资格/两宿主真实消费：`PreparationIncomplete` | 查看/分析实际采集域；宿主质量权威 | Exact LineScanArtifact/Qualification/TimingBundle，不加领域判定 | 上游公开只读桥/实际FramePort、两Host独立消费 | 实测平面、速度/加速度/同步/缺重行/温度/方向/空白靶挑战、独立留出与同坐标检查 | 客户实物/速度/曝光/线程/资源/最小缺陷/精度Profile与阈值来源 | 阈值/设备物理包络/标准件/正式资格和耐久接线为精确外门；不阻托管模拟工作 |
| M-LC 已解相机参数只读消费：`ModuleCoreImplementationReady` | C.8 查看首行准备/分析复核两个Host，仅消费CAL-CR | C.8.1 constructor/options/session及C.8.2严格11项/完整源快照，不改v0.4 | C.8.4独立Synthetic源端口/Reader/固定根槽 | C.8.3/C.8.5原Read/Stop/Dispose Task、stream/lease；Unknown/撤销/旧Ref/单位反例 | C.8.5冷/热Read/映射/复核/释放P50/P95/P99与源/本方峰值；无目标NotEvaluated | C.8.1组合DLL/Exe；六项文档规格已获主控接收，真实writer/端口/消费编译/LC运行/native/物理/性能/耐久门分别保留 |
| M-LM 同run运动证据只读消费：`ModuleCoreImplementationReady` | C.9查看/分析Host；只消费Actual XY/时钟/动态，不发设备命令 | C.9.1 port/options/采样事实、完整MR源DTO与既有LineEncoder/Mapping投影 | C.9.4全字段双Synthetic Host，原MotionRoot+本方固定根 | C.9.2–5缺包/版本/单位/不确定度/同run/迟到同桥Close恢复 | 双读/映射/有限Close P50/P95/P99、样本/字节/原Task/峰值；无目标NotEvaluated | C.9.1组合DLL/Exe，六项文档规格已获主控接收；真实源/精度/动态资格/消费编译/运行/性能保留；不猜camera C2-RF |
| M-LR camera C2-RF 原行事实只读消费：`ModuleCoreImplementationReady` | C.10 双无UI Host；只消费 camera 原 producer/ledger/page/row facts，拼接负责投影与几何，不发采集/运动/触发 | C.10.1–C.10.3 直接引用 camera §20 `LineFact*` 类型；原 payload 由 camera root 持有，frame-row map 是独立 Owner 证据，不复制 DTO/codec | C.10.5 Host-B/Host-X 上游 typed fixture、mosaic root 强持、原 Task/有限分页-CAS/Return/Close | C.10.2 连续性/缺行/跨域/未知曝光/资源；C.10.6 反例断言；原读写/返回/关闭 task 全部完成才交付 | 分页/行投影/producer read/Return/Close 的冷热 P50/P95/P99、rows/bytes/原Task/峰值/恢复；客户目标缺失为 NotEvaluated | 预定 `src/Modules/mosaic/Asun.Modules.Mosaic.CameraLineRead/` 与对应 Exe；六项文档规格已接收，仅限只读软件消费；真实 camera 程序集/消费编译/设备/物理/性能/耐久门保留 |
| 基线之外几何附加补偿：`NotSupported (first release)` | 无已证独立求值方法，不授权实现 | v0.3 Compensation!=null→MZ-026；v0.4不存在字段 | 两Host拒绝非法输入，无插件 | 已包含方向/温漂/比例组件不重复应用；拒绝非null | 不安排无消费者补偿benchmark | 不列“以后程序员补方法”或假现场门；扩展须新方法/新契约和独立证据 |

软件算例仅验证数学，不是客户门限：B(0)=(0,0)m、B(1)=(0.001,0)m，P(q)=q，q_ref=(0,0)m；实际反馈时间0/2ms的 qY=0/0.004m，行r=0/1的曝光中点0.5/1.5ms（各有区间内双反馈），q_rowY=0.001/0.003m。四节点分别 (0,0.001)/(0.001,0.001)/(0,0.003)/(0.001,0.003)m。点p=(0.00025,0.002)m在T1，权重(0.5,0.25,0.25)，反算 source=(0.25,0.5)；同面重做前向得到p。删去第二行/使counter不连续，两个面均消失，该p为Hole；不压缩索引重造面积。改变q_ref而保持同一个参考安装B时必须按差值移动，不能增加绝对位置两次。全部数值和额外误差容差仅用于fixture。

必须实现的断言：

- 透视/远心 division 各有已知 plane/column 的独立 oracle；首行用原line模型，不用area模型，不加0.5；整数节点与 C.2 一致、mesh前反一致、外边界/共享对角线唯一、背面/平行/非有限/反向翻转/非邻接重叠拒绝。换方向使用独立资产，Unknown不从命令推。
- 巨大tick（>2^53）、有理scale、不整除中点/offset、边界valid interval/uncertainty、UTC回拨、反馈/行乱序、缺包/跨Boot/Generation/epoch/position基准挑战；无extrapolation，未资格位置不出坐标。重复传输保持原摘要而求值只一次；异hash重复拒绝；缺行不会制造面。原Frame row与line counter故意不同，身份仍正确。
- h加倍时 A*h²/8 变四倍，δ/T/速度/加速度/encoder误差门逐项挑战；命令有速度/加速度但无DynamicsEvidence拒绝；Jacobian上界/资格cell缺项拒绝。没有E_numeric/optical/chord独立界不填0。Limits之外不静默放宽/平均速度补位。
- 两来源相同几何有固定 stacking/source provenance，改变输入list顺序不改变Sources set摘要或实际选择；source.Mask 非null/原行hash冲突、非法窗口stride/Int32溢出，native调用前拒绝。输出Hole位图不因安全索引0填充而增加覆盖；最近邻采样位移超门无有效输出。
- 旧v0.3请求/186-byte编码保持；line所有根依字段独立复算，新label不碰旧runtime。Trace→Artifact→Qualification→Request→Manifest闭包无循环；篡改嵌套digest、mapping、行tick/hash、预算/deadline拒绝/改变摘要；同operation跨旧/new入口冲突。
- Execute前后权威撤销/unknown、借帧前或交付前上游光学失效；第二读失败没有可用manifest/tile。None token有限；慢port/native/迟到buffer保留原根Owner；取消与TrySetResult竞争仅一个实际输出交付，未交付buffer服务归还。已交付lease不归还时OutputHeld/DrainUnknown，无ResourcesReleased/终态。Query无lease/Memory，Dispose不假确认native退出。

**最小充分剩余门：**

1. calibration-assets 0.3.1-prep §9.3 Camera Read API 1 / CAL-CR 六项指导已由主控接收，已解内容格式、Reader/Create/Read/State/Stop 与源 stream Owner 不再是缺失公开规格。mosaic 的精确只读消费桥见 C.8，M-LC六项指导已获主控接收；仍需双方消费编译、真实 writer/Store/ContentSource/Qualification 接线及各自资源/耐久验证。不能取 InitialParameters；mosaic 的 trace/平面/工作区/动态拼接资产仍由本模块 Owner 持有。
2. motion-control 0.2.4-prep附录A.8 Motion Read Bridge v0.1已获主控六项规格接收，持续Actual XY历史、原sequence/tick/PositionVersion、ClockMapping及同run动态包络的公开合同不再缺失。本方精确消费见C.9，M-LM六项文档规格已获主控接收；真实Adapter/Gateway、同tick采样、物理动态资格/精度事实和性能门仍保留。camera-acquisition C2-RF §20 已获主控限定内容接收；本方精确消费见 C.10，真实 producer/消费编译/运行/性能和物理资格仍保留。禁止mosaic发采集/运动/settled/trigger命令。
3. M-L2的本项目公共cv2参数tuple/指针拷贝/输出buffer归还调用须在其消费工程编译、真实HALCON运行检查；C.6.4公开AsunImageLineScanAdapter/Create/Options/Owner/真实Host装配为本模块确定内部门，本轮已冻结；剩余分别为本项目消费编译、真实HALCON运行和native/late-buffer归还证据，不再核“封装有没有算子”、安装/版本适配/授权。既有AsunImage/DevExpress直接使用，硬件厂商SDK实现不纳入本轮。
4. 实物PlaneInCamera/PlaneToCommon/q_ref/平面高度与安装重复性、独立光学/chord/cell误差、同步/动态包络及客户Profile数值须由可追溯测量/现场Owner提供，不能从模拟算例或图像看起来平滑推出。LineScanAuthorityPort必须在真实发布/资格Owner接线后证明上述引用当前有效；本轮定义消费形状，不伪称上游耐久/物理输出已有。

2026-10-11 本次0.5.2-prep窄收口有限两轮自审：第一轮核两Host的业务异常优先、正常归还/finally/收尾断言分轴、false/抛出/无效回执保根与Exe原exit保留；第二轮核Factory纯校验/NoWork、Hold开工前槽预留、Native原Owner固定槽承接及原实例有限恢复。C.1–C.5方法、C.6.1–C.6.2夹具/向量和附录A Core API以区段SHA-256与收口前基线核对不变；M-L1六项文档规格已获主控接收为ModuleCoreImplementationReady，M-C1/C2/C3接收保持。M-L2公开装配与Owner确定指导内容限定接收，消费编译/真实native/上游桥与物理资格仍PreparationIncomplete。保留0.5.1-prep已完成的Synthetic全字段构造/依赖摘要闭包、13406/13422-byte完整request规范长度/hash和独立有理数误差预算核对事实，本轮不重算向量。本轮定向检查本文件链接、表格列数、代码块/括号及版本一致性；未运行全仓validator，不修改共享文件，不创建产品工程。尚未执行 C# build/test、HALCON/AsunImage、真实WPF、运动/性能/HIL/计量/现场验收。

2026-10-11 / 0.5.2-prep 接收状态同步（历史）：该轮仅更新顶部/binding、C.7与自审状态，保留既有核对事实，未新增request复算或运行结论。随后已接收的calibration/motion消费分别在C.8/C.9，camera上游C2-RF已限定内容接收、本方已接收的只读软件消费规格仅见C.10；本历史状态不能覆盖当前顶部/C.7。

### C.8 Camera Read API 1 → 线扫首行已解参数只读桥（0.5.3-prep规格；六项文档已接收）

上游唯一依据是 [calibration-assets 0.3.1-prep §9.3](../calibration-assets/DEVELOPMENT-GUIDE.md#93-已解相机参数公开读取增量camera-read-api-1)，CAL-CR六项指导已由主控接收。这里只冻结本方公开组合、映射和消费验收，不修改上游、v0.3/v0.4 Core类型或已有向量，不重写CameraSolutionCodec/资产摘要/Reader。原M-L1准入和M-L2装配限定接收保持；主控于2026-10-11回读C.8完整合同、来源映射/资源证明、双Host、LC-01..07及落点/预算，接收M-LC为`ModuleCoreImplementationReady`（仅六项文档规格）。本桥不调用HALCON、求解、发布、设备或资格写入；两个真实消费者分别是线扫查看宿主的首行参数准备与线扫分析宿主的光学复核。

#### C.8.1 唯一公开组合与装配

组合DLL预定为`src/Modules/mosaic/Asun.Modules.Mosaic.CalibrationRead/Asun.Modules.Mosaic.CalibrationRead.csproj`，namespace=`Asun.Modules.Mosaic.CalibrationRead`，net10.0，仅引用mosaic Core和calibration-assets Core公开面。组合验收Exe预定为`tests/Modules/mosaic/Asun.Modules.Mosaic.CalibrationRead.Tests/Asun.Modules.Mosaic.CalibrationRead.Tests.csproj`，net10.0/OutputType=Exe/Microsoft.NET.Sdk，BCL及上述三工程引用；不改现有Core.Tests的BCL/Core绑定，不选新测试包。允许本切片获准后只在这两个组合目录写入；其它模块、共享合同、产品及AsunImage内部禁止写。没有新独立模块/会话；现阶段不创建工程。

以下`Ca`/`Cr`只是C# namespace alias，分别指`Asun.Modules.CalibrationAssets`和`Asun.Modules.CalibrationAssets.CameraRead`；`L<T>`仍只是IReadOnlyList<T>排版缩写。全部options非null、构造防御复制有界集合；没有反射、字典扩展字段或默认真实依赖。

```csharp
public record LineCameraOpticalBinding(FovOpticalCalibrationRef Optical,
    Ca.PublishedArtifactRef Asset, Ca.ContentRef SolvedParameters,
    Ca.QualifiedAssetRef Qualified, Ca.AuthorityWatermark Watermark,
    Ca.DeviceConfigurationSnapshot CalibrationDevice, Ca.OperatingDomain ApprovedDomain);
public record LineCameraReadBridgeOptions(Ca.CalibrationAssetsOptions ReaderOptions,
    Cr.CameraReadAdapters ReaderAdapters, LineCameraReadOwner Owner,
    uint MaxSessions, uint MaxReadsPerSession, TimeSpan MaxObservationWait,
    TimeSpan CleanupWaitLimit, long MaxResidentBytes,
    long ArtifactReadUpperBoundBytes, long SnapshotReservationBytes);
public record LineCameraReadSessionOptions(Guid SessionEpoch, LineCameraOpticalBinding Binding,
    Ca.DeviceConfigurationSnapshot ActualDevice, Ca.OperatingDomain ActualDomain,
    DateTimeOffset ExposureFrom, DateTimeOffset ExposureTo, PermissionScopeId PermissionScopeId,
    Ca.CalibrationExecutionBudget ReaderBudgetCeiling);
public record LineCameraReadValue(Cr.CameraParametersSnapshot Source,
    LineDivisionParameters Parameters, FovOpticalCalibrationRef Optical);
public record LineCameraReadReply(Ca.OperationId OperationId, Ca.ApplicabilityStatus Status,
    LineCameraReadValue? Value, Cr.CameraReadReply? SourceReply, bool SourceReleased,
    ResourceLedger Resources, L<MosaicError> Errors);
public sealed class LineCameraReadBridge : IAsyncDisposable
{
    public LineCameraReadBridge(LineCameraReadBridgeOptions options);
    public LineCameraReadSession OpenSession(LineCameraReadSessionOptions options);
    public ValueTask DisposeAsync();
}
public sealed class LineCameraReadSession : IAsyncDisposable
{
    public Guid SessionEpoch { get; }
    public ResourceLedger ReadResources();
    public ValueTask<LineCameraReadReply> ReadAsync(Ca.OperationId operationId,
        DateTimeOffset deadlineUtc, ResourceBudget remainingBudget, CancellationToken token);
    public Cr.CameraReadOperationState GetReadState(Ca.OperationId operationId);
    public ValueTask<LineOpticalAuthorityResult> ResolveOpticalAsync(
        LineOpticalAuthorityRequest request, CancellationToken token);
    public ValueTask<Ca.DrainResult> StopAsync(Ca.OperationId operationId,
        DateTimeOffset deadlineUtc, CancellationToken token);
    public ValueTask DisposeAsync();
}
public sealed class LineCameraReadOwner
{
    public LineCameraReadOwner(int capacity);
    public L<LineCameraReadSession> Sessions { get; }
    public ValueTask<bool> RecoverAsync(Guid sessionEpoch,
        DateTimeOffset deadlineUtc, CancellationToken token);
}
```

Bridge constructor只验证options并建立固定槽，不启动IO/订阅/Task/native；ReaderAdapters.Clock为唯一Clock，必须与两宿主、后续mosaic service同实例。MaxSessions/MaxReads正且受Owner容量/ReaderOptions.MaxRetainedOperations约束，MaxObservationWait正，CleanupWaitLimit正且<=ReaderOptions.StopWaitLimit<=30s。OpenSession在原Owner预留epoch槽及全部read/Stop/Dispose记录、总resident额度后，才用上游唯一`CameraParametersReader.Create(ReaderOptions,ReaderAdapters)`建立本session专属`Cr.ICameraParametersReader`；创建纯本地且失败NoWork。reader返回即不抛地提交到原槽，首次Read前根持有bridge/session/reader/全部借用adapters/options。根满、重复epoch、预算不足在Create/IO前拒绝；不能先Create再竞争容量。Bridge.Dispose只关闭本bridge准入并对已有session执行同一有限收尾，未确认根仍在caller的Owner中；不释放借用adapters。两个宿主使用不同bridge/session/reader/epoch/Owner，只读来源可引用同一内容，但不可共用可变Gate/脚本或Reader。

Binding由宿主既有光学投影Owner显式提供，**不是**bridge签发光学或扫描资格。Asset/Qualified/Watermark/Device/ApprovedDomain保持上游typed值；Optical是宿主已有本方引用，不能从SolvedParameters.Digest捏造Qualification.Digest或RectificationMap。映射限制：Optical.Id.Value=Asset.AssetId.Value，Optical.Digest=Asset.AssetDigest.Hex；AssetRevision仅支持正、无前导零、<=Int64.MaxValue的十进制原文本，严格转换后等Optical.Revision；不支持的非数字修订明确NotApplicable/MZ-026，不重新编号上游。Optical.Qualification.Id/Revision分别匹配Qualified.QualificationId及同样严格转换的QualificationRevision；它的Digest和RectificationMap/LocalChain由本方原Owner提供，bridge只检查与冻结Binding一致，不称其为上游资格hash/已生成校正map。完整Qualified/Watermark仍留在Source，不能靠本方ValueRef三个字段替代它们。Optical.Camera与session选定camera/Devices必须一致，AcquisitionConfiguration必须等`CameraSolutionCodec.ComputeDeviceDigest(ActualDevice).Hex`对应ContentDigest；不以DeviceFingerprint相同代替全部配置。无法确认本方资格/校正引用来源时不能用于真实接线，只允许明确标Synthetic的协议测试。

#### C.8.2 已解来源、严格参数表及Definition消费

每次Reader输入固定`CameraReadRequest("1",Binding.Asset,Binding.SolvedParameters,IntendedUse("LineScanRow0Projection",RevisionId("1")),ActualDevice,ActualDomain,ExposureFrom,ExposureTo,本次剩余ReaderBudget,原read OperationId)`；ExpectedSolvedParameters从冻结的原asset引用来，不能由另一个vector、InitialParameters或latest补换。只读成功须SourceReply.Completion=ResourcesReleased、Status=Applicable、Error=null、Snapshot非null；校验回写原OperationId，SourceReleased来自原Task结束和GetReadState的ResourcesReleased/无held，不能由Applicable推释放。

Snapshot.Asset/SolvedParameters/Qualified/Watermark/CalibrationDevice/ApprovedDomain与Binding逐字段精确相等；Qualified.Artifact=Snapshot.Asset，Solution.CalibrationDeviceDigest=上游公开ComputeDeviceDigest(CalibrationDevice)，ActualDevice的几何/域要求沿上游Reader。Method/ParameterRevision/ProducerId/ProducerRevision/RuntimeVersion已由Reader对原artifact核对，bridge保留原Solution不改写。ObservedAtUtc来自本次Reader，不得未来；当前clock在Watermark.ObservedAtUtc..ValidUntilUtc闭区间且曝光落在Qualified.QualifiedAtUtc..ValidUntilUtc（存在时）内。水位Authority/Epoch/Revision/有效窗改变，即使参数数值相同，本session也不换Binding：本次无Value/MZ-013，宿主结束原session后显式建新session。缺失/未知权威不返回ExactApplicable。

首版只接受已在C.2批准的`line_scan_division`与`line_scan_telecentric_division`两种完整原模型名，ordinal区分大小写；area_scan、polynomial等不猜路线，NotApplicable/MZ-026。原向量必须恰好11项，Name/Unit/索引如下，不靠name查找后排序纠错：

| 索引 | 透视Name / 远心Name | 原CameraParameterUnit | 本方LineDivisionParameters |
|---|---|---|---|
| 0 | Focus / Magnification | Meter / Dimensionless | FocusMeter / Magnification；另一项null |
| 1 | Kappa | PerMeterSquared | KappaPerMeterSquared |
| 2 | Sx | Meter | SxMeter |
| 3 | Sy | Meter | SyMeter |
| 4 | Cx | Pixel | CxPixel |
| 5 | Cy | Pixel | CyPixel |
| 6 | ImageWidth | Pixel | ImageWidth，有限正整数、checked uint |
| 7 | ImageHeight | Pixel | ImageHeight，有限正整数、checked uint |
| 8 | Vx | MeterPerRow | VxMeterPerRow |
| 9 | Vy | MeterPerRow | VyMeterPerRow |
| 10 | Vz | MeterPerRow | VzMeterPerRow；远心必须0 |

所有double有限、Focus/倍率/Sx/Sy/Vy正；保留Vx/Vz正负与-0数值语义，不自行取绝对值/归一方向/换单位。Width/Height同时核源CalibrationDevice；生产段行数不用于改已解Height。不得把m/s乘猜测的行周期写回V，不把ActualDomain.ScanSpeed的MeterPerSecond枚举混入CameraParameterUnit。Snapshot.Solution.Parameters是唯一数值来源；Source整个防御复制原Snapshot与参数list，保留原11项Model/Name/Unit/Value、SolvedParameters的format/revision/length/hash及Qualified/Watermark/批准域，不新增摘要根、codec或re-encode后宣称原bytes hash。

Read.Value仅为首行准备事实。宿主将Value.Parameters及原Optical显式放入一个新候选LineGeometryDefinition，PlaneInCamera/PlaneToCommon/ReferenceEncoder/Motion/Condition/ScanDirection/ExpectedOrientation/Timing/Limits/PlanarInstallationEvidence必须来自mosaic原Owner，不从相机参数解出；改Definition内容必须沿既有line04-geometry规则生成新Identity，既有Trace/Artifact/Qualification不能沿用为新内容资格。ResolveOpticalAsync先纯校验request.Definition.Optical/选定Devices.Camera/CameraId与本session匹配，且PermissionScopeId等session原Scope；随后以新原read ID执行上述Reader链，取得本次Value后才比较Definition.Parameters与本次映射逐字段相等，不能用上次缓存或初值预判。Definition参数不匹配返回ExactApplicable=false/MZ-013，不代替调用方修值。内部新read ID为首次准入时Guid.NewGuid产生的Ca.OperationId，加入原epoch固定槽/原Task，GetReadState和Recover均按此原ID；重观察不再生成。成功仅证明此次首行光学输入确切适用；不证明Plane安装、整幅扫描、运动场、Trace或Detection/Measurement资格。

拒绝时Value始终null，ExactApplicable=false且Errors非空；SourceReply若已真实返回则原样留存其Error/Findings/Diagnostic。上游NotApplicable→本方NotApplicable/MZ-015（CameraRead.Qualification）、Unknown/CAL-106→Unknown/MZ-030（CameraRead.Authority）；CAL-101→NotApplicable/MZ-026，CAL-108内容/引用失败→NotApplicable/MZ-013（CameraRead.SourceIntegrity），CAL-107→NotApplicable/MZ-028，CAL-112资源超限→NotApplicable/MZ-010。本方校验身份/水位/Definition参数不等→NotApplicable/MZ-013，模型不支持→MZ-026，原Name/Unit/非有限/尺寸非法→MZ-004；这不更改上游Error含义。未观察到原Read返回/DrainPending只报告Unknown/MZ-031与SourceReleased=false，不伪造上游Error或Released。其它未列异常保存原异常及Task，Unknown/MZ-030，不把内部故障升级为权限或native失败。

生产组合的既有ILineScanAuthorityPort.ResolveOpticalAsync直接调用本session同名方法，ResolveAsync仍由mosaic原发布/扫描资格只读Authority处理；Core执行前后、借帧/交付前仍用既定权威复核，不能缓存本桥一次Applicable跨整个scan。此处不引入新的扫描/运动Authority DTO。motion/camera公开桥未获主控接收前不接真实扫描。

#### C.8.3 剩余额度、原Task与源资源的有限清理

本方clock先记录单调接纳点/绝对deadline。每次新read的ReaderBudget.Deadline=min(ReaderBudgetCeiling.Deadline,原deadlineUtc-now,原本方单调剩余时间)，WaitLimit=min(ReaderBudgetCeiling.WaitLimit,MaxObservationWait,本次剩余)，不重置原作业时间；<=0在任何IO前MZ-010。MaxImageBytes=min(ceiling.MaxImageBytes,65536)，MaxResidentBytes=min(ceiling.MaxResidentBytes,实际已预留reader额度)，其余计数不超过ceiling且MaxConcurrentSolves=1。同ID重观察使用首次构造的完整CameraReadRequest/预算/Task，比较首次入参逐字段；改变deadline/remainingBudget等MZ-028，不重新构造随时间缩水的摘要或第二Read。

RemainingBudget是宿主已扣除之前阶段实耗的余额，不能传原整单预算当余额。ReadResources有界无IO，返回本session累计计费/实耗及当前资源；ReadReply/ResolveOptical.Resources也投影同一账本，重观察不二次计费。每新read在原Owner同时预留reader峰值与SnapshotReservationBytes；SnapshotReservationBytes覆盖保留源DTO、本方映射及固定记录，按有界字符串/11参数/8域维度核可容纳后才复制，不随结束自动忽略已保留快照。预算门：MemoryBytes至少涵盖reader预留峰值+snapshot余量；LogicalReadBytes至少涵盖ArtifactReadUpperBoundBytes+exactSolvedRef.ByteLength；DecodedBytes至少exactSolvedRef.ByteLength，MaxSourceLeases至少1（上游gate预约），CpuMilliseconds正并计入所有reader等待外的桥CPU，TileCount/MaxNativeHandles本桥实耗始终0。这些维度逐次扣额度，不以最终零活动反推没有实耗。源Reader原API没有CPU计数输出，本账本不伪造源CPU测量；它受原Reader执行Deadline/并发预算约束，目标适配的CPU测点与客户总CPU门仍需单独验证。

ArtifactReadUpperBoundBytes是宿主已绑定只读Store适配的单次逻辑读取上界，属于端口预算契约，不是从artifact hash或网络字节猜出的测量；真实Store需保证该界并给资源测点，无有效界拒绝本消费准入。本桥按此上界保守记LogicalReadBytes，stream按exactSolvedRef.ByteLength计费；实际磁盘/网络/native耗时仍由目标适配/性能门实测，不能把该计费值作为测得IO。源Reader用自己的ExecutionGate/MaxResidentBytes约束内部字节/streambuffer/解出快照；桥不会绕过Reader另OpenRead。上游Read已校验长度/EOF/hash/Decode，消费者不复制第二stream/codec。

每个epoch槽固定MaxReadsPerSession个read记录和各一个Stop/Dispose记录。预留成功后每个ValueTask只AsTask一次，原Read Task在首次调用返回时立即写入原槽，调用同步抛出也记录原异常；有限WaitAsync结束只报告SourceReleased=false/Status=Unknown/Value=null/MZ-031，原Task/Reader/adapters/额度全部保留，不新Read原ID。GetReadState在Reader存活时只是读原Reader.GetOperationState，无IO，不把UnknownOperation当Released；Dispose前把已核验的原ResourcesReleased状态防御复制到固定历史槽，Dispose后只读这些已确认历史值，不再调用已处置Reader，也不重建释放事实。纯值历史交给caller所有权，不携Task/stream/native；Root退槽核当前资源不等于清除已交付纯值记录。迟到成功若Host Closing/旧水位/取消，保留SourceReply用于对账但不再交付Value。fault/cancel Task也不单独证明stream/lease退出。

原Read Task已返回DrainPending时，同ID后续观察只查原GetReadState：仅Status=ResourcesReleased/HeldResources空/Final非null且Final.OperationId同原ID时，才把该**原Final**作为SourceReply重新核本方适用性；不能永久复用早到DrainPending，也不能重发Read。原Task fault/cancel或Final不完整仍保留故障/根，不能据一条正常状态覆盖原异常。所有SourceReleased判断还须原Task确已结束，Closing/已取消的Host不会接受迟到Value。

源ContentSource将OpenRead返回的stream唯一Dispose权交Reader ledger；桥/宿主绝不并发Dispose该stream。源Open/Read/Dispose原Task、借用Store/Qualifications/Gate和gate预约都由Reader原ledger保留到真实完成；原Read Task必须与GetReadState(ResourcesReleased/held空)相互核验。源ReadReply DrainPending即使读Task已返回也保留Reader；在独立有限恢复窗口只查询原ID，不重Read、不重Open、不释放借用端口。测试必须故意卡住迟到stream/read/Dispose/gate预约，核SourceReleased=false和根槽仍在。

生产Root只消费公开Reader原状态/原Task证明源释放，不猜Store/Stream/Gate新增ReadResources API；其内部资源由上游Reader Owner负责，独立测点由上述Synthetic端口或目标适配验收提供。没有可信公开ResourcesReleased证据时一直保留原Root，不以不可访问的内部计数假设零。ResourceLedger.ActiveSourceLeases是本桥持有的源执行/预约责任投影，不声称本桥拥有或直接释放stream。

Stop首次调用在同epoch登记一次原`reader.StopAsync(new DrainRequest(stopId,min(CleanupWaitLimit,剩余恢复窗口)),独立有限cleanup token).AsTask()`，不使用已取消业务token；后续恢复观察此原Stop Task/原read IDs，不同时第二Stop。Stop真实完成ResourcesReleased/Pending空、所有已登记read Task结束且各GetReadState ResourcesReleased/无held后，才登记一次原Reader.DisposeAsync Task；Dispose同步抛出/fault/cancel/超时均保根。只有上述Task正常结束、reader held空、源gate/stream测点释放、bridge快照已交接或释放且本方CurrentBytes/PendingPortCalls/ActiveSourceLeases全0，Owner才退原epoch槽。恢复窗口到期返回false，不无限poll；业务失败与cleanup两轴依C.6.3保存首异常/原栈及非零exit，cleanup成功不改历史失败。Owner.RecoverAsync包括deadline求值/原Stop/State/Dispose/回执核对均有限不抛，记录首cleanup异常/false原因；缺字段、错误ID/epoch、非零资源却Released等回执绝不退根。

公开session.StopAsync只在原Stop Task真实返回时返回其原DrainResult；观察期到而原Task未返时抛TimeoutException并保持原Stop记录，不构造一个冒充上游的Released/DrainUnknown回执。RecoverAsync捕获该观察异常并返回false。Stop返回DrainUnknown后后续窗口先看原read IDs，真实资源全释放时可确认原Stop ID的GetOperationState=ResourcesReleased/HeldResources空，再启动唯一Dispose；不因原Stop的历史DrainUnknown永久卡死，也不发第二Stop。Dispose退出前最后核源read/stop状态、自己任务与借用适配预约，快照记录释放原根所有权（已交付纯DTO由caller持有），才清空本方历史Task/SourceReply强引用；故障槽仍留历史结果。不能仅凭Dispose wrapper有界返回退槽。

Bridge.DisposeAsync与session.DisposeAsync均单次Closing/有界观察，不冒充资源完成；重复调用复用原处置Task，不启动第二释放。源端口只借，两个session关闭不销毁另一session依赖。caller在10秒外层观察截止后仍强持bridge/Owner/原Host Task；Host未真退出时不并发Recover，故障或PendingRecovery退出非零，不能通过杀进程证明归还。

#### C.8.4 两个完整Synthetic消费Host

新增`SyntheticCameraBridgeFixture(bool analysis)`仅位于组合Tests；不是上游公共API、不是引用上游私有测试类。其源内容/Store/Content/Qualification/Gate完整构造**直接采用上游§9.3.4全字段二维Synthetic表**（该表为源输入唯一权威，全部C/Put/Prepare/Artifact/envelope/dependency、ComputePrepared/Parameters/ArtifactDigest均按上游公开helper），在本组合Tests实现这些公开端口；不启动Joint、solver或真实Publish。各fixture有独立字典、门、clock、脚本与disposed计数；原bytes/hash按上游codec构造，不另造一套格式。以下本方表闭合所有新增字段，不能用C.6的2×2/不同Vy夹具替换本64×2来源。

| 本方fixture字段/属性 | 完整值及来源 |
|---|---|
| Clock/Epoch/Scope | Clock为独立SyntheticHostClock(T0)，T0=`2000-01-01T00:00:00Z`；Epoch查看=`00000000-0000-0000-0000-000000000301`、分析=`...0302`；Scope分别`Synthetic-camera-view`/`Synthetic-camera-analysis` |
| LineDevice / Domain / source solved | 原上游lineDevice/domain/published/exactSolvedRef；64×2、native布局、全ROI/binning1、曝光1000µs/gain0、工作距.25m/20°C/ScanSpeed.02m/s；solved为Focus=.010、Kappa0、Sx/Sy=.00001、Cx32/Cy0、Width64/Height2、Vx0/Vy.00002/Vz0；initial只Focus=.009、Vy.000018；十一项名称/单位沿C.8.2，不能补初值 |
| ExpectedQualified / Watermark | `QualifiedAssetRef(published,QualificationId("syn-line-q"),RevisionId("1"),T0-1day,T0+1day)`；`AuthorityWatermark("Synthetic","line-1",RevisionId("1"),T0,T0+1day)`；ApprovedDomain原Domain、CalibrationDevice原LineDevice；真实资格不存在，只有公开只读mock值 |
| Optical / Binding | camera=`DeviceCamera("camera",LineScan,"axes",ContentDigest(ComputeDeviceDigest(LineDevice).Hex))`；Optical=`FovOpticalCalibrationRef(AssetId(published.AssetId.Value),Revision(1),ContentDigest(published.AssetDigest.Hex),"Synthetic-machine","station",camera,ValueRef("syn-line-q",Revision(1),H(UTF8("Synthetic:optical-qualification"))),Ref("Synthetic-row0-map"),PixelRect(0,0,64,1),CoordinateChain(Revision(1),[]))`；H/Ref沿C.6 Synthetic纯值helper。此Qualification.Digest/map是本方Synthetic Owner标记，不是上游资格内容hash/真实map；Binding完整装入上述原Asset/Solved/Qualified/Watermark/Device/Domain |
| Options(owner) / SessionOptions | `LineCameraReadBridgeOptions(CalibrationAssetsOptions(2,64,1048576,1s,32,8),CameraReadAdapters(本fixture只读Store/Content/Qualification/Gate/Diagnostics/Clock),owner,2,8,200ms,500ms,4194304,1048576,65536)`；Gate总1MiB/并发1，Diagnostics64。session=`LineCameraReadSessionOptions(Epoch,Binding,LineDevice,Domain,T0,T0+1ms,Scope,CalibrationExecutionBudget(2s,3s,8,65536,128,1048576,1))`；数字为明确软件fixture额度，不是客户目标 |
| Remaining / Id(n) / source脚本 | 原流程额度=`ResourceBudget(10000,4194304,8388608,524288,1,1,1)`；Host创建session后显式`f.Session=session`，Remaining getter读session.ReadResources，CPU/LogicalReadBytes/DecodedBytes扣累计计费，MemoryBytes扣当前持有值，余下计数按原上限；非负检查，不重复传完整初始余额。Id(n)为Ca.OperationId，Guid=`00000000-0000-0000-0000-0000000004nn`（view）/`...0000000005nn`（analysis），n01..08固定两位。Read deadline=T0+2s。Qualified=false默认；设true返回上表Qualified；Revoked=true时同Asset/Use返回Revoked/null Qualified/原Device/Domain/Evidence/Watermark。故障用新fixture构造注入，不改已封存bytes |
| Definition(value) | 纯Synthetic候选：C.6.1的LineGeometryDefinition结构完整复制，但Devices=`DeviceScope(value.Optical.MachineId,value.Optical.StationId,[value.Optical.Camera])`、CameraId为该Camera.CameraId，Optical/Parameters换本Value；PlaneInCamera=`RigidTransform3("plane","line-camera0",identity9,[0,0,.25])`；Motion.Conditions中ConfigurationDigest换本Camera.AcquisitionConfiguration，其它plane/common/ReferenceEncoder/Motion节点/Condition/ScanDirection/Timing/Limits/安装证据仍本fixture Owner显式模拟；同既有line04-geometry/Seal重算新Identity。只用于ResolveOptical协议，**不**沿用旧Trace/Artifact/Qualification，不执行真实扫描/宣称旧限额验证了64列 |
| SourceIsClean | 本fixture的Open/read/Dispose/gate Tasks真实退出、stream DisposeCalls恰1且ActiveStreams=0、ActiveReservations=0、源Reader各原id ResourcesReleased/held空；不是只看本方return。正常每次Read有独立stream，多个Read则DisposeCalls等成功Open数，均逐实例一次 |

测试代码的`Require`/`Close`复用C.6.3，无新测试包。`CheckSolved(reply,f)`是本fixture内部纯断言：Applicable、Value/SourceReply非null、SourceReleased=true、Errors空；原Source.Asset/SolvedParameters/CalibrationDevice/Qualified/Watermark/ApprovedDomain逐字段等Binding，Model=`line_scan_division`且11项的Name/Unit/Value逐索引等表；Parameters等`LineDivisionParameters(PerspectiveDivision,.010,null,0,.00001,.00001,32,0,64,2,0,.00002,0)`，与initial不同；Optical逐字段等冻结Binding，不修改Source。调用者不得仅断言Focus而跳过其余项。

```csharp
// Consumers/CameraViewHost.cs；owner由Exe caller创建并始终强持。
internal static async Task RunCameraViewHostAsync(LineCameraReadOwner owner)
{
    var f = new SyntheticCameraBridgeFixture(analysis:false);
    var bridge = new LineCameraReadBridge(f.Options(owner));
    var session = bridge.OpenSession(f.SessionOptions);
    f.Session=session;
    System.Runtime.ExceptionServices.ExceptionDispatchInfo? businessFailure = null;
    bool cleanupOk = true;
    try
    {
        var unknown = await session.ReadAsync(f.Id(1),f.Deadline,f.Remaining,CancellationToken.None);
        Require(unknown.Status==Ca.ApplicabilityStatus.Unknown && unknown.Value==null && unknown.SourceReleased);
        f.Qualifications.DecisionAvailable=true; // 仅模拟外部Owner，session无资格写方法。
        var ready = await session.ReadAsync(f.Id(2),f.Deadline,f.Remaining,CancellationToken.None);
        CheckSolved(ready,f);
        var definition = f.Definition(ready.Value!);
        var check = await session.ResolveOpticalAsync(new LineOpticalAuthorityRequest(
            definition,f.Scope,f.Deadline,f.Remaining),CancellationToken.None);
        Require(check.ExactApplicable && check.Errors.Count==0);
        Require(f.NativeCalls==0 && f.FrameAcquires==0 && f.MotionCommands==0);
        f.Qualifications.Revoked=true;
        var revoked = await session.ReadAsync(f.Id(3),f.Deadline,f.Remaining,CancellationToken.None);
        Require(revoked.Status==Ca.ApplicabilityStatus.NotApplicable && revoked.Value==null);
        Require(session.GetReadState(f.Id(2)).Status==Ca.OperationExecutionStatus.ResourcesReleased);
    }
    catch (Exception error) { businessFailure=System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(error); }
    finally
    {
        try { cleanupOk &= await owner.RecoverAsync(f.Epoch,f.Clock.GetUtcNow().AddMilliseconds(500),CancellationToken.None); }
        catch (Exception error) { cleanupOk=false; f.RecordCleanup(error); }
        try { await bridge.DisposeAsync().AsTask().WaitAsync(TimeSpan.FromMilliseconds(500)); }
        catch (Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    }
    try { Require(owner.Sessions.Count==0 && f.SourceIsClean); }
    catch (Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    f.BusinessFailure=businessFailure; f.CleanupSucceeded=cleanupOk; // 预分配测试字段，不抛。
    if (businessFailure!=null) businessFailure.Throw();
    Require(cleanupOk);
}

// Consumers/CameraAnalysisHost.cs；与查看Host无可变对象/epoch/Scope共享。
internal static async Task RunCameraAnalysisHostAsync(LineCameraReadOwner owner)
{
    var f = new SyntheticCameraBridgeFixture(analysis:true);
    var bridge = new LineCameraReadBridge(f.Options(owner));
    var session = bridge.OpenSession(f.SessionOptions);
    f.Session=session;
    System.Runtime.ExceptionServices.ExceptionDispatchInfo? businessFailure = null;
    bool cleanupOk = true;
    try
    {
        f.Qualifications.DecisionAvailable=true;
        var originalRemaining=f.Remaining;
        var ready = await session.ReadAsync(f.Id(1),f.Deadline,originalRemaining,CancellationToken.None);
        CheckSolved(ready,f);
        var definition = f.Definition(ready.Value!);
        var wrongUnits = definition with { Parameters=definition.Parameters with { VyMeterPerRow=.02 } };
        var rejected = await session.ResolveOpticalAsync(new LineOpticalAuthorityRequest(
            wrongUnits,f.Scope,f.Deadline,f.Remaining),CancellationToken.None);
        Require(!rejected.ExactApplicable && rejected.Errors.Any(x=>x.Code==MosaicErrorCode.StaleRevision));
        var exact = await session.ResolveOpticalAsync(new LineOpticalAuthorityRequest(
            definition,f.Scope,f.Deadline,f.Remaining),CancellationToken.None);
        Require(exact.ExactApplicable && exact.Errors.Count==0);
        int readsBefore=f.Content.OpenCalls;
        var replay = await session.ReadAsync(f.Id(1),f.Deadline,originalRemaining,CancellationToken.None);
        CheckSolved(replay,f); Require(f.Content.OpenCalls==readsBefore);
        // 同ID改余额是冲突，不能再建Reader Read或更新原结果。
        var conflict = await session.ReadAsync(f.Id(1),f.Deadline,
            originalRemaining with { MemoryBytes=originalRemaining.MemoryBytes-1 },CancellationToken.None);
        Require(conflict.Value==null && conflict.Errors.Any(x=>x.Code==MosaicErrorCode.OperationConflict));
        Require(f.NativeCalls==0 && f.FrameAcquires==0 && f.MotionCommands==0);
    }
    catch (Exception error) { businessFailure=System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(error); }
    finally
    {
        try { cleanupOk &= await owner.RecoverAsync(f.Epoch,f.Clock.GetUtcNow().AddMilliseconds(500),CancellationToken.None); }
        catch (Exception error) { cleanupOk=false; f.RecordCleanup(error); }
        try { await bridge.DisposeAsync().AsTask().WaitAsync(TimeSpan.FromMilliseconds(500)); }
        catch (Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    }
    try { Require(owner.Sessions.Count==0 && f.SourceIsClean); }
    catch (Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    f.BusinessFailure=businessFailure; f.CleanupSucceeded=cleanupOk;
    if (businessFailure!=null) businessFailure.Throw();
    Require(cleanupOk);
}
```

Fixture上述内部方法/字段均在`SyntheticCameraBridgeFixture.cs`实现：Options只组原公开record，Definition只组完整纯值候选；RecordCleanup保首异常及有界故障槽，BusinessFailure/CleanupSucceeded是internal字段，无诊断回调。SourceIsClean按mock记录的原read IDs核session.GetReadState的已确认历史及源stream/gate测点，不从已Dispose Reader重新取状态。正常归还后stream DisposeCalls=OpenCalls（每个stream恰1），gate无预约，NativeCalls/FrameAcquires/MotionCommands为mock端口实际计数而非预填PASS。两个Host真实Task由Exe用独立Owner(capacity=2)分别保存/WaitAsync(10s)观察；构造/OpenSession在try前失败时按NoWork/自己预留的空槽处理保留原异常，不删除重复epoch属于其它session的槽，未真结束Task不能退根或并发恢复。业务成功后的零资源断言失败归入cleanup故障槽，不得把cleanup成功覆盖原业务失败；总exit依C.6.3两轴。Dispose观察超时由原Owner继续持原Bridge/Dispose Task，不能使用using自动丢Owner。

#### C.8.5 反例、两轮核对与精确剩余门

以下case每项用全新fixture/epoch/Owner，除明确重观察外不用旧id换输入。通过条件都包含有限退出或保留原根的可观察失败，模拟不冒充真实来源：

| 断言 | 精确注入与期望 |
|---|---|
| LC-01 双消费者/来源 | 上述完整Host均读solved而非initial；11项及全部源引用/Device/Qualified/Watermark/ApprovedDomain保留；关闭查看session不影响分析session，vector list防御复制；无native/Frame/运动调用 |
| LC-02 NotApplicable/Unknown/撤销 | 新session的ActualDomain.WorkingDistance=.26m而批准.25m→NotApplicable/Value=null；Qualified=false/权威断联→Unknown/Value=null；Revoked/Suspended/Expired、曝光超窗或Use不符→NotApplicable，不能沿用上次Applicable；Reader错误/Findings保留SourceReply，现场恢复由原Owner处理 |
| LC-03 旧Ref/水位/模型 | 新fixture绑定另一SolvedRef而Store仍原exactRef→上游CAL-108，本方无Value/MZ-013；旧AssetRevision/hash同样拒绝；Watermark epoch/revision变化但参数不变→MZ-013，不选latest；area/polynomial未知模型→MZ-026；不迁移旧format/重算旧资产 |
| LC-04 单位/顺序/尺寸 | 原bytes模型Vy仍MeterPerRow却误填.02以冒充m/s，Definition与本read不等→ExactApplicable=false/MZ-013；源vector Sx单位Pixel、V单位Meter、字段调序/重复/缺项/NaN/宽高非整数→Reader Decode拒绝/CAL-108→MZ-013，或本桥纯值核验拒绝/MZ-004，均无Value、不纠正；远心Vz!=0拒绝，Magnification映射另一nullable项，不能把Focus改名冒充 |
| LC-05 原Task/迟到资源 | 分别保持Content.Open、stream.Read、stream.Dispose、Gate.Reserve的原TCS；200ms观察后无Value/SourceReleased=false/MZ-031，Reader/getState与Owner仍持原ID/Task/stream/预约；500msRecover false且根保留。显式完成原闩锁后同实例有限Recover，只一次原Stop/Dispose/stream Dispose；故障/取消回执/错stop ID/未知state不退根，不重Open/Read/Reader.Create |
| LC-06 余额/取消/NoWork | 构造非法options、epoch槽满均IO=0/无活动资源；LogicalReadBytes小于ArtifactReadUpperBoundBytes+Solved.ByteLength、Memory小于预约或deadline到期→MZ-010/IO=0；同id重观察源读取一次，改预算MZ-028；token只取消观察/停止新阶段，原Reader取消请求不代替释放；业务先失败再cleanup抛/fault/false时原ExceptionDispatchInfo/exit不变 |
| LC-07 资格边界 | Camera Read Applicable仍不授整幅/运动/扫描/Detection/Measurement；未提供本方Plane/Trace/Artifact/动态资格时不执行扫描。生产资格内容变化仍走既定mosaic前后Authority复核，不把Row0 ApprovedDomain扩为工作区 |

LC-04的源单位反例在新fixture编码前输入上游CameraSolutionCodec.Encode，若其先拒绝则断言源拒绝且桥/native调用0；bridge的内部纯值映射/核验函数对同样坏snapshot直接做输入挑战，由组合Tests按正常内部可见性调用，不注入替代Reader/factory，不声称真实Reader允许坏单位。远心消费另用完整同名Magnification11项源Snapshot及明确对应Device模型/Optical binding，生产writer/数值仍单独验证，不用透视Fixture换Model字符串凑PASS。

远心正确纯值反例的完整变体：在上述源全字段fixture构造前令CameraModel=`line_scan_telecentric_division`、OpticalFingerprint/LensIdentity=`syn-line-telecentric-optic`/`syn-line-telecentric-lens`、MagnificationState=`0.5`，第0项为CameraParameter("Magnification",.5,Dimensionless)，其余10项值/单位与透视表完全相同，Vz=0，initial第0项.45/Vy.000018。solver参数类型仍LineScanCameraSolverParameters，CameraModel/EstimatedParameters改为该模型及{"magnification"}，所有观测DeviceDigest、Method/参数/Prepare/artifact/solved内容/envelope/Binding与原公开helpers一致重建，CalibrationDeviceDigest重算；原Domain/时窗/姿态/只读端口规则保持。仅软件格式/映射断言，期望`LineDivisionParameters(TelecentricDivision,null,.5,0,.00001,.00001,32,0,64,2,0,.00002,0)`；把Vz改为.00001或把第0项Name改Focus时拒绝。没有真实求解、透视资格复用或新物理路线。

实现验收命令为`dotnet build src/Modules/mosaic/Asun.Modules.Mosaic.CalibrationRead/Asun.Modules.Mosaic.CalibrationRead.csproj -c Release`及`dotnet run --project tests/Modules/mosaic/Asun.Modules.Mosaic.CalibrationRead.Tests/Asun.Modules.Mosaic.CalibrationRead.Tests.csproj -c Release`；全部LC-01..07必需断言且原资源归还才exit0，失败/跳过/PendingRecovery非零，当前未执行。性能沿§14.1：相同代表输入测冷/热Read、源Decode/Store/Qualification/stream release、桥映射/ResolveOptical端到端P50/P95/P99、源和本方峰值、排空延迟；分离源成本/本方成本，保留逻辑IO上界计费与真实测点区别。缺客户数值目标为NotEvaluated，不称最快/精度或达标。

精确剩余门：M-LC指导六项已接收，目标组合工程公开引用消费编译/实现与LC断言仍未执行；上游真实format writer/已发布内容闭包、耐久Store/ContentSource/Qualification和资源测点；M-L2实际cv2/native/迟到句柄；mosaic自身平面安装/Trace/独立验证/动态资格/客户Profile及性能/耐久/现场资格分别保留。CAL-CR/M-LC已接收不代表这些真实输出已存在。motion原只读桥0.2.4-prep已接收，本方消费增量见C.9且M-LM六项文档规格已接收。camera C2-RF §20 已接收，本方 C.10 只规定真实只读消费；camera writer/Store/设备、C2-RF消费编译/运行、原行 payload 与物理/性能/耐久资格仍未执行，不复制上游Owner或 DTO。

2026-10-11 / 0.5.3-prep 本轮有限两轮局部自审：第一轮核已接收Camera Read API 1的公开类型/调用、参数11项顺序/单位、完整Source身份/资格水位/批准域及两个Synthetic Host的剩余预算；第二轮核固定槽/NoWork、Read/Stop/Dispose原Task、迟到stream/预约的Reader Owner、cleanup异常优先级、原ID回查与有限恢复。局部结构/链接及本方record字段数量核对；C.1–C.5方法、C.6.1–C.6.4既有夹具/Host/native装配和附录A Core API的区段SHA-256保持。新增C.8消费指导待主控接收，原M-L1/M-L2限定接收状态不变；仅文档检查，不新增13406/13422-byte复算声明。未创建工程/脚本/新会话/子代理，未改上游或共享；未执行C#、HALCON/native、WPF、性能、真实设备、耐久或物理/现场验收。

2026-10-11 接收同步：主控已回读C.8并接收M-LC六项文档规格为ModuleCoreImplementationReady；前段“待接收”保留为0.5.3-prep交稿时历史，不覆盖当前顶部/C.7状态。未新增LC运行、source writer/Store/Qualification、消费编译或物理/性能通过声明。

### C.9 Motion Read Bridge v0.1 → 同run线扫运动证据（0.5.4-prep规格；六项文档已接收）

上游唯一合同是[motion-control 0.2.4-prep A.8](../motion-control/DEVELOPMENT-GUIDE.md#a8-motion-read-bridge-v01mosaic-只读连续反馈动态证据)，六项文档已接收；主控已回读本方C.9完整装配/映射/不确定度/来源引用、双Synthetic Host/双根原Task/有限Close及迟到恢复，并定向对照上游A.8，接收M-LM为`ModuleCoreImplementationReady`（仅六项文档规格准备）。复用C.1的实际平移/有理时钟/误差算法与上游MR-XY-01/MR-DY-01/MR-EV-01，不实现第二MR codec或重新求运动包络。桥的只读Close是读取scope的关闭，不是轴Stop/控制器安全停/settled或MotionSession.Close；所有设备写入口均不属于本消费。

#### C.9.1 本方公开端口、采样事实与唯一装配

组合DLL预定`src/Modules/mosaic/Asun.Modules.Mosaic.MotionRead/Asun.Modules.Mosaic.MotionRead.csproj`，namespace=`Asun.Modules.Mosaic.MotionRead`，net10.0，仅引用mosaic Core/motion-control Core公开面。组合Exe预定`tests/Modules/mosaic/Asun.Modules.Mosaic.MotionRead.Tests/Asun.Modules.Mosaic.MotionRead.Tests.csproj`，net10.0/OutputType=Exe/Microsoft.NET.Sdk，BCL和上述三工程引用；不改已接收Core.Tests或C.8工程/合同，不新增测试包。获准实现后只在这两个组合目录写；现在只补指导，不创建任何工程/源文件。`Mr`以下为namespace alias `Asun.Modules.MotionControl`，ImmutableArray为BCL不可变集合；所有集合防御复制/预算前置。

```csharp
public record LineMotionSampleFact(string SourceRecordId, long Sequence, Mr.ClockStamp Clock,
    string PositionVersionX, string PositionVersionY, RegistrationConditions? Conditions,
    Length? EncoderErrorBound, ValueRef? EncoderErrorEvidence, ValueRef? ConditionsEvidence);
public record LineMotionSamplingFacts(Mr.MotionReadIdentity Identity, string RunId,
    string DeviceReferenceRevision, string AuthorityId, Revision ProjectionRevision,
    ImmutableArray<LineMotionSampleFact> Samples);
public record LineMotionEvidencePortOptions(Guid PortEpoch, Mr.MotionReadBridge Bridge,
    Mr.IMotionReadRoot MotionRoot, Mr.IMotionClockMappingPort ClockMappings,
    Mr.MotionReadBridgeOptions SourceOptions, LineMotionEvidenceOwner Owner,
    TimeProvider Clock, uint MaxReads, long MaxResidentBytes,
    TimeSpan MaxObservationWait, TimeSpan CleanupBudget);
public record LineMotionEvidenceRequest(string XYReadId, string DynamicsReadId,
    Mr.MotionReadSelector Selector, long MaxSequence, int MaxSamples, long MaxBytes,
    string RunId, string ApplicabilityRevision,
    ImmutableArray<Mr.MotionDynamicsOrigin> AllowedOrigins, LineMotionSamplingFacts Facts,
    LineTimingPolicy TargetClock, DateTimeOffset DeadlineUtc, ResourceBudget RemainingBudget);
public record LineMotionEvidenceValue(Mr.MotionXYHistoryResult XY,
    Mr.MotionDynamicsResult Dynamics, LineClockMapping Mapping,
    ImmutableArray<LineEncoderSample> Feedback, ValueRef DynamicsReference,
    double SpeedBoundMetersPerSecond, double AccelerationBoundMetersPerSecondSquared,
    LineMotionSamplingFacts Facts, TimeSpan AddedTimestampUncertainty);
public record LineMotionEvidenceReply(bool Applicable, LineMotionEvidenceValue? Value,
    Mr.MotionXYHistoryResult? XY, Mr.MotionDynamicsResult? Dynamics,
    ResourceLedger Resources, L<MosaicError> Errors);
public sealed class LineMotionEvidencePort : IAsyncDisposable
{
    public LineMotionEvidencePort(LineMotionEvidencePortOptions options);
    public ValueTask<LineMotionEvidenceReply> ReadAsync(LineMotionEvidenceRequest request,
        CancellationToken token);
    public ResourceLedger ReadResources();
    public ValueTask<Mr.DrainResult> CloseAsync(DateTimeOffset deadlineUtc,
        CancellationToken token);
    public ValueTask DisposeAsync();
}
public sealed class LineMotionEvidenceOwner
{
    public LineMotionEvidenceOwner(int maxPorts, int maxOriginalTasks);
    public bool TryReserve(Guid portEpoch, Mr.MotionReadIdentity identity, Mr.IMotionReadRoot root);
    public void AttachBridge(Guid portEpoch, Mr.MotionReadBridge bridge);
    public int RetainedCount { get; }
    public ValueTask<bool> RecoverAsync(Guid portEpoch, DateTimeOffset deadlineUtc,
        CancellationToken token);
}
```

生产借用的MotionReadBridge必须由Motion原Owner/可信只读宿主提供，ExpectedIdentity/AllowedScope/Capability/原Root已冻结；不从mosaic临时扩轴/换Owner/改变来源。每个本方port使用专属只读bridge关闭scope；同一bridge不得同时给另一个活consumer，不能以本方Close取消别的会话。构造是纯校验/固定记录，无IO/运动/native。宿主的确定装配：new原IMotionReadRoot与LineMotionEvidenceOwner→本方Owner.TryReserve(epoch,identity,原root)→原root.TryReserveBridge(identity,limits)→Motion Owner调用上游唯一`new MotionReadBridge(new MotionReadBridgeDependencies(source,clockMappings,原root,time),new MotionReadBridgeOptions(identity,scope,limits))`→原root.AttachBridge→本方Owner.AttachBridge→new本方LineMotionEvidencePort(options)。两根及所有借用source/clock/selector/原Task一直在进程级caller强引用内，第一次读前已提交；TryReserve失败时原Bridge构造/Source调用0，Attach只向预留槽写确切引用/不抛/不分配。port constructor核其epoch/bridge/原root与预留槽ReferenceEquals，不能新建第二Motion桥作为恢复。

未构造出Motion bridge只允许原root.ConfirmBridgeReleased(identity,null)核从未Attach且无call后退空槽；已构造bridge而本方port失败时原Owner保留该确切bridge，按同实例只读Close/Dispose/原Root确认恢复，不把“无设备写”当删除根许可。本方Owner仅保管/观察；GetIdentity/Mapping/History/Dynamics原call槽及原source Task始终由上游IMotionReadRoot承担，不扫描内部或冒充它们的释放者。

SamplingFacts由原机台/采样精度与条件Owner提供只读的每sample事实，非本桥从Capability.PositionResolution/FollowingError/命令/数组索引推算。每项按SourceRecordId+原Sequence+完整Clock+PositionVersionX/Y与本次原sample精确关联；Identity/RunId/DeviceReferenceRevision一致，ProjectionRevision为本方投影修订，不冒充上游未提供的记录修订。Conditions必须有已核的ConditionId/实际方向/温度/TimingRevision/采集ConfigurationDigest及ConditionsEvidence；EncoderErrorBound必须有限非负米值且EncoderErrorEvidence非null/可追溯。unknown用null表达，无证据的0拒绝MZ-020/021；0仅在来源明确证明时可用。动态AuthorityId来自原证据，与Facts.AuthorityId必须精确匹配，但此相等仍不是本桥签资格。真实facts可用性/有效域由原Owner与既定LineAuthority前后复核，不能以caller自行拼相等替代。

#### C.9.2 Actual XY、时钟、动态及源引用的适用投影

Read先预检原identity/scope/selector/两轴/target域、facts结构/剩余预算；XY读取只调用上游`ReadSynchronizedXYAsync(selector,XYReadId,MaxSequence,MaxSamples,MaxBytes,剩余阶段TimeSpan,token)`。只有Available/IsComplete=true/Gaps空/Mapping非null/Failure=null且源Read.Resources.Released可核时，才在同run/selector/原Identity读`ReadRunDynamicsAsync(new MotionDynamicsReadRequest(DynamicsReadId,selector,RunId,ApplicabilityRevision,AllowedOrigins,MaxBytes,剩余阶段TimeSpan),token)`；XY部分/未知/迟到不启动Dynamics，不排序/补包/重采或自动换新read ID。Evidence是原`Mr.MotionDynamicsEvidence`，不换成另一种动态DTO。输出原XY/Dynamics DTO完整保留，RequestSha256/EvidenceSha256由上游已核的A.8.4原预像来，本桥不另编码MR请求或证据，也不把参数hash字符串再次hash。

| 本方输入/投影 | 精确来源与门 |
|---|---|
| 身份/采样 | XY.Identity、Dynamics.Identity、每sample.Identity均等SourceOptions.ExpectedIdentity；Controller/Boot/Generation/Source/Capability/contract/source clock与Selector相符，原ReadId不串；源Clock.Sequence=sample.Sequence>0，严格相邻，原SourceRecordId唯一，PositionVersionX/Y及DeviceReferenceRevision保留，不用list下标生成任何字段 |
| Actual / frame | 只从MotionSynchronizedXYSample.ActualX/Y（原RawAxisSample.EncoderActual）取值；Unit=Millimeter、有限，同Frame=明确原轴frame，AxisX/Y与Scope原序匹配。各分量仅除1000得到Length(Meter)，保留符号，非零换算成0/溢出拒绝MZ-004。不调用frame transform、不交换轴或从EncoderPositiveSign再翻号；原源已提供同tick/sequence合法实际坐标 |
| LineEncoderSample | Sequence/ControllerId/BootId/Generation/DeviceReferenceRevision/PositionVersionX/Y逐字取原sample；Actual=AxisPosition(mmX/1000,mmY/1000,sample.Frame.Value)；At=LineClockStamp(Clock.DomainId,Clock.Epoch,Clock.Tick,Clock.TickFrequency)。原Clock.Sequence与TimestampUncertainty仍保留完整XY及关联Facts，不因本方At无Sequence而丢来源；EncoderErrorBound/Conditions只取同key的已核Facts |
| Source ValueRef | Id=原SourceRecordId、Revision=Facts.ProjectionRevision、Digest=ContentDigest(XY.RequestSha256)。这是**原读取意图来源引用**，不是原记录正文hash/位置hash；未提供的record hash不能编造。完整原samples和原RequestSha256与投影一起交caller，既有line04-timing内容摘要仍覆盖实际坐标/版本/时钟。运行Authority凭原read闭包核源值，不能只核这个ValueRef |
| LineClockMapping | Id=原Mapping.MappingSha256（原64hex），Revision=Facts.ProjectionRevision（本方元数据），Digest=原MappingSha256；Source/Target domain/epoch、scale numerator/denominator、offset和valid source区间逐字复制。频率来自Selector.Range/原Clock，等TargetClock；ClockMappings.IsCurrent原mapping sha在映射与交付前均为true，变化MZ-024/013 |
| 时间不确定度 | 保留原mapping对象不修改；Δ=所有已用sample.TimestampUncertainty的最大值，非负且有源，AddedTimestampUncertainty=Δ。ProjectedMapping.MaximumErrorTargetTicks=原MaximumErrorTargetTicks+ceil(Δ.Ticks*TargetFrequency/TimeSpan.TicksPerSecond)，checked BigInteger/Int64，不向0截断；其Identity仍仅引用原上游mapping，**不是投影正文摘要**。原Mapping/Δ/投影全随Value保留，line04-timing覆盖扩大的保守误差。只扩大消费误差，不换scale/offset/原hash，不能解释为上游改了mapping；C.1 δ因此已包含反馈采样不确定度，不重复塞到row或DelayUncertainty |
| Dynamics / 区间 | 同RunId/ApplicabilityRevision/DeviceReferenceRevision/Authority、State=Confirmed且Origin在AllowedOrigins内、原EvidenceSha与正文由上游核；ApplicableRange同source/target域/epoch/frequency并覆盖本次读取/实际曝光关联需要的源区间。证据TimestampUncertainty单独保留，在适用域端点按ceil(uncertainty*SourceFrequency)收缩可用区间；收缩后不覆盖请求即MZ-024/021，不把来源标签当资格 |
| 标量速度/加速度界 | 上游MaxSpeedX/Y.Unit=Millimeter，字段量纲是mm/s；MaxAccelerationX/Y字段为mm/s²，正有限。C.1需要米制XY欧氏范数上界；本桥固定取保守L1界V=(MaxSpeedX+MaxSpeedY)/1000、A=(MaxAccelerationX+MaxAccelerationY)/1000，并在有限double结果上两次Math.BitIncrement向上保护换算/加和舍入；非有限/溢出拒绝。不能只取max轴值或实际Y差分，不能由Profile/commanded/settled生成包络 |
| Dynamics ValueRef | Id=原EvidenceId、Revision=Facts.ProjectionRevision、Digest=原EvidenceSha256，不重算本方证据hash；原Run/ApplicabilityRevision/Origin/State/Range/Authority/四个含单位原值全保留在Value.Dynamics.Evidence中，由原Owner判真实物理适用 |

Read.Applicable=true仅表示这组来源在本方投影协议上完整适用，Value非null/Errors空；Simulation/Replay允许两个软件Host的明确Origins，但不得用于物理Detection/Measurement。真实线扫还须Hardware来源、原Owner已认可的物理包络与精度facts以及原mosaic资格；ControllerPublished不是自动PhysicallyQualified，AllowedOrigins由宿主冻结，不在失败后增加Simulation。缺包/不同tick/PositionVersion缺失→MZ-020，Clock或不确定度越界→MZ-024，动态Unknown/Expired/Revoked/范围/Authority不符→MZ-021，旧Identity/run/ref/源修订变化→MZ-013，未支持历史/型号/来源→MZ-026。任何失败Value=null，原XY/Dynamics/Gaps/Failure及本方错误都保留，Unknown不能自动Display成功。

消费LineTimingBundle时仅从Value取feedback、映射、DynamicsReference/V/A，再与camera原Owner已核Rows、其它相机clock mappings一起按既有line04-timing封存新内容；不能沿用不同run/新tick内容的旧digest。不创建/索取camera C2-RF DTO，不从Motion sequence合成RowIndex/LineCounter/曝光/原字节hash。生产组合须在源记录可追溯保存/读取的闭包可用后接既定LineAuthority；Value不签Trace/安装/扫描资格，也不改变P(q)=G0+d及曝光中点插值方法。

#### C.9.3 剩余预算、双根与迟到同实例Close

SourceOptions.Limits与本方MaxReads/MaxResidentBytes/MaxObservationWait/CleanupBudget显式正且有限，MaxReads<=floor((上游MaxQueueDepth+MaxPendingReads)/2)保留容量（每pair占XY和DY），本方original Task槽至少3*MaxReads+2（read-pair/XY/DY/Close/Dispose），另强持上游root依赖；不按readId重复创建记录。RemainingBudget来自已扣前序CPU/逻辑IO/解出值和当前resident的宿主余额。每pair至少预留2*MaxBytes源结果/缓存余量及4096*MaxSamples bytes的fact+LineEncoder额外投影余量；源sample本体计入源MaxBytes，不重复声称小于任意常数。本方每项需复制/强持的额外UTF8值总量<=3072bytes、固定结构/数值/记录余量1024bytes，字符串同时满足双方既有ID上限；事实超此界在复制前拒绝，不截断/改名。可重用临时预约只有在原Task/后处理确认退出后归还，已交付纯值缓存的内存仍由其当前Owner记账。没有Frame/source-image租约、tile/native句柄，本桥这些实耗为0。

逻辑IO按XY/Dynamics各自MaxBytes上界计费，源适配必须保证此逻辑载荷界（真实SDK/网络物理IO另测），DecodedBytes按samples/facts映射有界载荷计费，不伪造文件字节测量。Memory/CPU/IO额度不足、MaxSamples/MaxSequence/MaxBytes越限或队列满，在Source调用前MZ-010。Read的单调总截止在首次接纳冻结；每阶段deadline=min(总剩余,SourceLimits.MaxObservationWait,本方MaxObservationWait)，queue/Identity/Mapping/History/Dynamics/交付共用剩余，不每阶段续命。到期停止新增阶段/交付并保留原Task；None token也有限。

同XYReadId/DynamicsReadId完整请求（含facts/targetClock/原deadline/remainingBudget）精确相等时只观察原pair Task/原结果，不再读源、不扣第二次额度；任一ID跨XY/DY/另pair或字段变化MZ-028，不造新codec来决定相等。首次阶段参数已冻结，重观察不重算随时间变化的source deadline或hash。ReadResources/Reply.Resources是本方累计计费和实际Task/当前持有投影，来源Read.Resources.Released只描述读临时资源，不代表桥可删。

本方ledger以短锁线性化首次准入、原ID占槽、Closing与Task登记，锁内不调用source/clock/诊断或等待；首次异步工作必须晚于槽和原不可变请求预留。Read映射/交付前重查Closing与当前mapping，取消/Closing胜出时不交付Value，owned源结果仍归原后处理核清理；不能在await后覆盖另一个read或回到Ready。Source ClockMappings只借，IsCurrent为已接收有界同步检查，异常保存原故障而不默认为当前。

上游每源调用仍按A.8.5 TryReserveCall→原ValueTask.AsTask一次/AttachTask→唯一后处理/ConfirmCall；本方固定槽另外持原XY/DY/整pair Task、原bridge/root/facts/options/clock，不只保存WaitAsync包装。调用同步抛错也保原异常；若端口在返回ValueTask前阻塞，预留槽/借用根仍在，不能以无Task删根。XY或Dynamics观察超时/取消回执归来，源原Task可能仍在运行：Value=null，PendingPortCalls保留，停在原stage不重发/不进入下一stage。原MotionRoot掌握源Task是否真退出，caller不通过本方Task.IsCompleted或普通Read.Resources.Released推源释放。

Close第一步只关闭本方准入/请求停止观察并作用到原专属ReadBridge。本方预留一个原CloseTask槽；调用`原bridge.CloseAsync(min(剩余窗口,本方CleanupBudget,SourceLimits.CleanupBudget),独立有限cleanup token).AsTask()`后只观察该实际Task，未结束不并发第二Close。已返回DrainUnknown而原source/后处理随后退出时，恢复在同epoch、同bridge/root/read IDs上再次Close（上游允许的有限再观察），记录新Close原Task，原诊断/失败保持；不新Bridge/Source/Read、不发Axis Stop。

仅原Close实返SessionId=ExpectedIdentity.SessionId、Drain=Drained/Resources=Released/IsReleased=true/PendingOperationIds空，且本方pair/XY/DY Tasks与上游原call后处理都完成，才首次登记原bridge.DisposeAsync Task；正常结束后用该原Close回执调用原MotionRoot.ConfirmBridgeReleased，返回true且本方记录/临时预约零才退本方epoch槽。只读值owned副本可交caller，不含运行Task/句柄；退根不改变其来源/历史失败。Close回执错误/unknown、Dispose fault/cancel/未结束或Confirm拒绝都保两根；不拿Read result或自造DrainResult替换Close证明。

公开port.CloseAsync只返回原bridge实际Close回执；观察窗口到而原Close Task尚未返时抛TimeoutException并保留原Task，不构造假源回执。port.DisposeAsync只线性化本方Closing并通过原Owner有限恢复；Owner直接观察原bridge.Close/Dispose Task，绝不递归调用port.DisposeAsync。恢复未确认时port.Dispose抛有限清理异常且保根；重复wrapper复用自己的原Task，后续恢复由Owner在新的有限窗口做同实例Close，不把wrapper返回/异常当源退出。

Owner.RecoverAsync至本次deadline有限且不抛，分别捕获Close求参/await/回执、Dispose、原root Confirm、本方退槽异常与false原因，不以cleanup覆盖原业务ExceptionDispatchInfo/exit。第二Close仅在上一原CloseTask真正结束且新恢复窗口开始后进行；失败保持原Root/借用Source/ClockMappings/完整facts强引用至caller生命周期，10秒外层观测/杀进程不是归还。生产借用Source/clock端口只能由其原Owner在所有源Task退出后按自身生命周期释放，mosaic不会Dispose其它MotionSession。

#### C.9.4 两个完整Synthetic消费Host与迟到恢复

组合Tests新增`SyntheticLineMotionFixture(bool analysis)`，源输入和测试端口完整采用上游A.8.6 ReadFixture/ReadPorts全字段实施正文，在本组合Tests实现其公开端口，不引用上游私有测试DLL。两个fixture的MotionReadIdentity分别b1/s1/o1、b2/s2/o2，c/k/generation1、SourceKind.Simulation、capability=64个a、contract=motion-read-bridge-v0.1；Scope=[X,Y]/GroupId=null、frame=axis，源d/e/1000Hz与target t/u/1000Hz、tick[0,2]。原记录rec-1/rec-2的Sequence1/2、Clock.Sequence1/2、ActualX=0mm，ActualY=0/.004mm、px1/py1→px1/py2、ref、Simultaneous=true、TimestampUncertainty=0。Raw/Feedback全部字段沿A.8.6，ControllerCommand/Target为空，不以静态PASS计数。Dynamics ev/run/rev/auth/ref，MaxSpeedX/Y=2mm/s、MaxAccelerationX/Y=10mm/s²、Simulation/Confirmed、原MR-EV正文hash。原有64a只是Synthetic能力输入，不能证明设备能力。

上游DeviceClock为独立MotionVirtualTimeProvider(T0)，记录形成后Advance(2ms)；sourceTime用它，期限Clock固定TimeProvider.System，不用Advance推动观察预算。ClockMappings为A.8.6的1000→1000 scale1/1、offset/error0、有界[0,2]、MappingSha=H(UTF8("Synthetic-map-d-to-t"))，只是原已定义的Synthetic mapping输入，非真实校准。Script/System独立闩锁及原IMotionReadRoot(1 bridge/8 call)按上游表；原Root/Script/Source/Mappings均被本方Owner调用前保存。

| 本方完整fixture字段/辅助 | 精确构造/唯一行为 |
|---|---|
| PortEpoch / facts | Guid查看=`00000000-0000-0000-0000-000000000601`、分析=`...0602`；Facts(identity,"run","ref","auth",Revision(1),[fact rec-1/1/Clock(d,e,0,1,1000)/px1/py1,fact rec-2/2/Clock(d,e,2,2,1000)/px1/py2])；各fact.Conditions=`RegistrationConditions(ConditionId("Synthetic-forward"),NotRequired,Positive,20,Revision(1),H(UTF8("Synthetic-configuration")))`，EncoderErrorBound=Length(1e-9,Meter)，两Evidence分别Ref("Synthetic-encoder-error")/Ref("Synthetic-condition")。这是明示模拟误差/条件，不取机器分辨率当精度；Ref/H复用本方C.6纯值helper |
| Request / InitialBudget | `LineMotionEvidenceRequest("xy1","dy1",原Selector,2,2,4096,"run","rev",[Simulation],Facts,LineTimingPolicy("t","u",1000,0s,0s),deadlineUtc=Clock.GetUtcNow()+1s,ResourceBudget(1000,1048576,16384,16384,1,1,1))`；Deadline创建一次，不重复重放重新now；Source每阶段250ms上限，故正常快速两读用MR-XY/MR-DY原176/186-byte参数。Source RequestSha由上游生成，fixture期望引用MR向量，不调用受测encoder造期望 |
| Source limits / Port options | 原MotionReadLimits(4096,4194304,2,8,250ms,1s)；`LineMotionEvidencePortOptions(PortEpoch,原bridge,原Root,Mappings,new MotionReadBridgeOptions(identity,scope,limits),owner,Clock,4,1048576,250ms,500ms)`；Owner由Exe caller构造(1 port,16 original task槽)，原Root负责源call槽，均固定容量 |
| OpenPort(owner) | 按C.9.1完整装配先owner.TryReserve、原Root.TryReserveBridge、new原MotionReadBridge/AttachBridge、owner.AttachBridge再new本方port。任一步失败保原借用根/已生成bridge，并由同owner处理；不是隐藏上游工厂，不使用static依赖。fixture.Session/Port引用仅存引用，不启动工作 |
| Check(value) | 全字段核原Identity/RequestSha/Run/rev/Evidence及Source sample/PositionVersion；Feedback两项Sequence1/2/tick0/2/频率1000，Y=0/4e-6m、X=0，EncoderErrorBound=1e-9m/Conditions原值；Mapping原sha/scale/range保留且零附加误差；DynamicsReference.Digest=原EvidenceSha。V/A等两次BitIncrement(.004)/两次BitIncrement(.02)，并>=.004/.02；不得期望原C.6的0/.004m |
| 插值消费 | 分析仅用C.1已核方法对两个实际位置在0.5/1.5ms求软件q_row，Y=1e-6/3e-6m；可在内部纯值helper按原BigInteger有理权重(1/4,3/4)断言，不修改算法/不生成camera行facts，不执行整幅/运动资格。C.6原2MHz/0.004m fixture和向量不改 |
| RecordCleanup / Root计数 | 测试internal有界故障槽/BusinessFailure/CleanupSucceeded复用C.6.3两轴；原Root ActiveBridgeCount/ActiveCallCount及所有原Task/后处理真退出才SourceIsClean。原任务包括History闩锁Task，不能只看port.Read Task；command调用计数保持实际mock0 |

ReadFixture的两种原MR请求/证据向量以[上游A.8.4](../motion-control/DEVELOPMENT-GUIDE.md#a84-xydynamics-请求与证据正文的精确预像)为唯一规范，不在本方复制hex/codec/改它的ID。View期望MR-XY-01 `176/c45f21a75eb127a312c88906376a31709d9abdbbd96b6286f127fdc6694ee903`、MR-DY-01 `186/14fea86c4b75282e597f9fc30d53bc58a114f6169e5130aec0fa0e3be7f44661`、MR-EV-01 `337/9e4921bc2b8c63a9853f3b69d3ccc015ce61c0503bf6d8a81cb872a34d918e77`；Analysis只改b2/s2/o2闭包，其新hash沿上游已定义实现检查变化，不新增“本轮独立复算”声明。pair总截止很短/人为Delay导致剩余阶段小于250ms时请求hash自然不同，不能拿向量期望误判；专门向量case用源公开直接读取固定250ms，normal consumer另外核原请求/剩余预算。

```csharp
// Consumers/LineMotionViewHost.cs；Owner在Exe入口强持。
internal static async Task RunLineMotionViewHostAsync(LineMotionEvidenceOwner owner)
{
    var f = new SyntheticLineMotionFixture(analysis:false);
    var port = f.OpenPort(owner);
    System.Runtime.ExceptionServices.ExceptionDispatchInfo? businessFailure = null;
    bool cleanupOk=true;
    try
    {
        var read = await port.ReadAsync(f.Request,CancellationToken.None);
        Require(read.Applicable && read.Value!=null && read.Errors.Count==0);
        f.Check(read.Value!);
        Require(read.Value!.Feedback[1].Actual.Y.Value==.000004);
        var repeat = await port.ReadAsync(f.Request,CancellationToken.None);
        Require(repeat.Applicable && f.Source.HistoryCalls==1 && f.Source.DynamicsCalls==1);
        Require(f.CommandCalls==0);
    }
    catch(Exception error) { businessFailure=System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(error); }
    finally
    {
        try { cleanupOk &= await owner.RecoverAsync(f.PortEpoch,f.Clock.GetUtcNow().AddMilliseconds(500),CancellationToken.None); }
        catch(Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    }
    try { Require(owner.RetainedCount==0 && f.SourceIsClean); }
    catch(Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    f.BusinessFailure=businessFailure; f.CleanupSucceeded=cleanupOk;
    if(businessFailure!=null) businessFailure.Throw();
    Require(cleanupOk);
}

// Consumers/LineMotionAnalysisHost.cs；独立b2/s2/o2/clock/source/root。
internal static async Task RunLineMotionAnalysisHostAsync(LineMotionEvidenceOwner owner)
{
    var f = new SyntheticLineMotionFixture(analysis:true);
    var port = f.OpenPort(owner);
    System.Runtime.ExceptionServices.ExceptionDispatchInfo? businessFailure = null;
    bool cleanupOk=true;
    try
    {
        var read = await port.ReadAsync(f.Request,CancellationToken.None);
        Require(read.Applicable && read.Value!=null); f.Check(read.Value!);
        // 已有C.1纯值数学，来源时刻为0/2ms；不是camera行交付或物理验收。
        var a=read.Value!.Feedback[0].Actual.Y.Value;
        var b=read.Value.Feedback[1].Actual.Y.Value;
        Require(Close(.75*a+.25*b,.000001) && Close(.25*a+.75*b,.000003));
        var conflict=await port.ReadAsync(f.Request with { RunId="other-run" },CancellationToken.None);
        Require(!conflict.Applicable && conflict.Value==null &&
            conflict.Errors.Any(x=>x.Code==MosaicErrorCode.OperationConflict));
        Require(f.Source.HistoryCalls==1 && f.Source.DynamicsCalls==1 && f.CommandCalls==0);
    }
    catch(Exception error) { businessFailure=System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(error); }
    finally
    {
        try { cleanupOk &= await owner.RecoverAsync(f.PortEpoch,f.Clock.GetUtcNow().AddMilliseconds(500),CancellationToken.None); }
        catch(Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    }
    try { Require(owner.RetainedCount==0 && f.SourceIsClean); }
    catch(Exception error) { cleanupOk=false; f.RecordCleanup(error); }
    f.BusinessFailure=businessFailure; f.CleanupSucceeded=cleanupOk;
    if(businessFailure!=null) businessFailure.Throw();
    Require(cleanupOk);
}
```

额外迟到恢复case在全新fixture/同一port中：调用OpenPort前Script.Arm("History")→保存原`Task<LineMotionEvidenceReply> read=port.ReadAsync(Request,callerCt).AsTask()`→独立1s WaitEntered→cancel caller/等250ms→Reply不可用且原Root.ActiveCallCount>0、History原Task未结束→owner.Recover(500ms)返回false并保原bridge/root/read/facts→Script.Release("History")只结束原闩锁→独立1s核源原Task和late-result processing真实完成→同owner/同epoch Recover(500ms)，同bridge再次Close后原Root Confirm通过才RetainedCount=0。原取消Reply不因释放变Applicable，不重新Read/换Source/Bridge，不续Dynamics阶段。Identity/ClockResolve/Dynamics闩锁分别作为独立case，同预留原根顺序。正常和这些case的Host Task由caller各自持Owner，外层WaitAsync(10s)只判fail，Host未真退出不并发恢复；suite有未确认根退出非零。

#### C.9.5 断言/Benchmark及精确剩余门

| 断言 | 输入与可判定结果 |
|---|---|
| LM-01 双Host/原Actual | C.9.4全字段两个Host，mm→m后原tick/sequence/PositionVersion/frame/Boot/Generation不变，MR DTO/向量来源原样；commanded值就算不同也不入投影；源无Actual或只Command→MZ-020/026、无Value |
| LM-02 同步/连续/版本 | 分轴异tick/sequence、SourceComplete=false、Gaps缺包/首尾不足、倒序/同ID异原字段、PositionVersion空、跨boot/generation/DeviceReferenceRevision→无Value，不排序补齐、不以数组index生成版本；原Gaps/Failure保留 |
| LM-03 单位/frame/精度facts | Degree轴/不同frame/非有限、除1000下溢为0→MZ-004；事实少一项/Clock或PositionVersion不等/无EncoderErrorEvidence或未知Conditions→MZ-020/021，不用Capability.PositionResolution/FollowingError推精度、不给0默认 |
| LM-04 时钟/不确定度 | 当前mapping失效/target域epochfrequency错/有理溢出或有效域不足→MZ-024；sample.TimestampUncertainty=1ms/1000Hz时只消费投影error增加1tick、原Mappingsha/error0与完整原sample仍保留；源Range/dynamic边界收缩后不足拒绝，不把1ms当1tick于其它frequency或丢至0 |
| LM-05 run/动态 | run/rev/Authority/原Evidence摘要变化、Unknown/Expired/Revoked/范围不覆盖、Simulation用于物理或origin不允许→MZ-021/013；标量V/A取保守两轴L1上界，不取Y-only/profile命令或差分。正确协议并不代表物理资格 |
| LM-06 余额/重观察 | MaxSamples/MaxBytes/原Task槽/源缓存或余额+1越界在Source前MZ-010；None token有限；重复pair返回同Task/结果、源各1次；改Run/budget/facts/target或跨XY/DY复用ID→MZ-028，不第二codec/不重读 |
| LM-07 迟到/Close | 上述四stage闩锁原Task、500ms失败/原根保留、受控Release后同bridgeClose恢复；错Session/非零pending却Released/Dispose故障/原Root Confirm拒绝不退槽；business先错且cleanup抛/false保原栈/exit，不能凭Read.Resources删根 |

性能沿§14.1对同代表数据测pair接纳/XY历史/映射/动态/投影/交付、取消至原source收敛及Close/Dispose的端到端冷/热P50/P95/P99和样本/字节/原Task/队列/托管峰值，虚拟Advance不当墙钟性能；目标缺失NotEvaluated，不称最快/达标。获准实现的验证命令为`dotnet build src/Modules/mosaic/Asun.Modules.Mosaic.MotionRead/Asun.Modules.Mosaic.MotionRead.csproj -c Release`与`dotnet run --project tests/Modules/mosaic/Asun.Modules.Mosaic.MotionRead.Tests/Asun.Modules.Mosaic.MotionRead.Tests.csproj -c Release`；LM-01..07、双Host/异常/归还全部完成才exit0，跳过/未结束/PendingRecovery非零，当前未执行。

M-LM六项文档规格已接收；剩余门分别为双方公开引用消费编译/真实实现和LM运行；原Motion Adapter/Gateway有界历史/同tick actual与PositionVersion完整源、真实时钟/采样精度facts/同run物理动态资格及耐久；原mosaic光学/Plane/Trace/扫描资格、native/客户Profile/性能/现场。M-LC六项接收、M-L1及M-L2限定接收保持。camera C2-RF上游§20已由主控限定内容接收；本方C.10/M-LR只读软件消费规格已接收，真实producer/消费编译/运行、逐行事实和物理/性能资格仍保留，不猜DTO或并行改上游。

2026-10-11 / 0.5.4-prep 本轮两轮有界局部自审：第一轮核MR公开工厂/接口/字段及176/186/337-byte向量引用、本方record构造顺序、Actual mm→m、原C.1插值、两轴保守V/A、时间不确定度ceil和Synthetic预算；第二轮核两个完整Host的真实调用/原ID重观察、调用前双根预留、原XY/DY/源Task/Close/Dispose保留与迟到同实例恢复、业务/cleanup两轴、状态和文档链接/结构。附录A Core API、C.1–C.5方法、C.6既有夹具/Host/native装配及C.8.1–4已接收消费API/Host的区段SHA-256保持。M-LC六项接收保持；截至本次状态同步，主控已接收M-LM六项文档规格为ModuleCoreImplementationReady；复用上游MR向量，本轮未重建其bytes/hash，也未新增既有13406/13422-byte复算声称。只改本指导，未创建工程/代码/测试/报告/脚本/会话/子代理；未执行C#、LM/LC产品运行、HALCON/native、WPF、性能、真实设备/精度/动态/耐久/物理或现场验收。

2026-10-11 本次仅同步M-LM规格接收状态：没有重建本方新编码向量，MR三向量以前复算事实保持，不新增实测声明。camera C2-RF上游§20已获主控限定内容接收，本方M-LR只读软件消费规格已接收；真实来源/时钟/encoder/dynamics、消费编译/LM/LC/LR运行、物理/性能/耐久资格仍未验。既有M-LC/M-L1及M-L2限定接收保持。

### C.10 Camera C2-RF → 线扫连续行只读消费（0.5.5-prep；ModuleCoreImplementationReady，仅只读软件消费规格）

唯一上游依据是 [camera-acquisition 0.4.2-prep §20](../camera-acquisition/DEVELOPMENT-GUIDE.md#20-c2-rf-线扫原行事实只读桥modulecoreimplementationready仅规格准备)，C2-RF 六项文档规格已获主控限定内容接收；主控已回读并接收本节 M-LR 六项文档规格为 `ModuleCoreImplementationReady`，范围仅为只读软件消费。C.2/C.3 为限定内容接收；C.4 Core DTO、C.6 夹具、C.8/C.9 接收保持。只读事实完整不等于 camera 设备、运动、标定或大图性能合格。

#### C.10.1 唯一装配、调用面与事实所有权

这是宿主组合层的只读消费，不新增独立模块、camera DTO/codec 或 Core 公共入口。获准实现的预定组合 DLL 为 `src/Modules/mosaic/Asun.Modules.Mosaic.CameraLineRead/Asun.Modules.Mosaic.CameraLineRead.csproj`，namespace=`Asun.Modules.Mosaic.CameraLineRead`、net10.0、Microsoft.NET.Sdk；测试 Exe 为 `tests/Modules/mosaic/Asun.Modules.Mosaic.CameraLineRead.Tests/Asun.Modules.Mosaic.CameraLineRead.Tests.csproj`，net10.0/OutputType=Exe，只用 BCL 和两方公开程序集。Core 原引用/接口不变；仅允许这两个目录，禁止 camera/motion/calibration/共享文件、产品工程、SDK 和 AsunImage 内部。现阶段不创建工程。

公开消费直接引用 `Asun.Pcb.Modules.CameraAcquisition.LineFacts` 的 `LineFactReaderFactory<TFrame>`、`LedgerBackedLineFactSource<TFrame>`、`ILineFactLedgerReadPort`、`ILineFactPayloadReadPort<TFrame>`、`ILineFactRootPort`、`ILineFactOwnerRecovery`、clock/ids/limits；其准确构造、record 顺序和方法只以 camera §20.2–3 为准。组合层私有 helper 接受原 factory、原 root/recovery、原 ReaderRequest、page size、剩余 ResourceBudget、总 deadline 和独立长期 Owner；结果保留原 CameraReply、Snapshot/Page/QueryResult 和本方诊断，不把运行对象放入 Core 请求。不造第二个 factory/reader API。

宿主在构造前强持 ledger/payload/source/root/recovery/clock/ids/limits，按 camera §20.6 精确顺序 `clock/ids/root/recovery/ledger/payload → LedgerBackedLineFactSource<TFrame> → LineFactReaderFactory<TFrame>` 装配。真实 ledger/payload 只能来自原采集 Owner 已保存内容，mosaic 不调用旧 IOperationLedger/ICameraFramePort 上不存在的方法，不抓 SDK、不开设备、不发 Trigger/运动/Stop。

reader 的 Page/Query **只有 LineFactRow 纯事实**，不返回 FullPayload 或 BorrowId；完整 `LineFactPayloadRow<TFrame>.FullPayload`、Window、实际 payload lease/Row 借用始终由 camera producer/root 强持。mosaic 不第二次直调 payload.ReadRow/ReturnRow，也不把事实页伪装为像素租约。producer 的每次 Read/Return/Open/Close 原 Task、完整 A<byte>、HashCoveredRanges、padding 与 closure 仍原值保真：page 中的 RawBytes 是该原 payload 经唯一 producer 得出的事实；摄取像素另外经既有 FramePort，二者的原来源绑定由原 Frame Owner 证明。

#### C.10.2 Snapshot、有限分页/CAS 与连续链

1. HostOwner 在 Create 前保存已传给 ids 的 RootId/ReaderId、Owner/session/capture/SourceRevision、factory 和本次 root 固定槽。只调用一次 `CreateAsync(original LineFactReaderRequest, token).AsTask()`；camera 内部 Reserve/Register/AttachOpen 将真正源 Open/ledger/payload 子 Task 纳入原 camera root。无 handle、同步抛错或迟到 success 也通过该原 root 恢复，不再次 Create/Open。
2. 成功 handle 直接实现 ILineFactReader，依次 `SnapshotAsync(LineFactSnapshotRequest)`、`ReadPageAsync(LineFactPageRequest)`；所有请求 ReaderId/ExpectedSourceRevision 固定。先核原 Binding/Owner/session/capture/SnapshotId/revision、Support、ImmutableContent、currentness、Integrity；Source=NotSupported 时不给成功零行/零缺行，payload.Open 必须为0。FixedSnapshot 不替成 latest；CurrentSource revision 变化或 Owner 撤销只诊断/清理旧根，不跨新 revision 拼图。
3. page 顺序来自 ledger BlockOrdinal/块内 SourceOrdinal，不由 frame key 字典序、RowIndex 或 arrival 排序。首 token=null；下一页只用原返回 token，page size/byte 上限/intent 固定，等待预算可以扣剩余。核 PageIntegrity 的原 CanonicalSha256 与 camera `LineFactCanonicalJsonWriter.WritePage` 正文 SHA-256；Query/Snapshot 用相应公开 Write 方法。不写第二个 codec，不用意图 hash 替换正文 hash，不补默认字段。DetailsTruncated/Partial/LimitReached 必须显式未完成，不伪 IsLast/Complete。
4. 同输入 token/intent 的缓存重放只重观察原回执，不再次 ReadRow/CAS、不重复插入 mosaic rows；缓存页的原 Resources 不能证明当前资源零。相同输入 token 持原页引用/正文 hash核相等，内容变更即拒绝；第一页不能重放，不自动重开。TokenConflict/Expired/ReplayCacheFull/RevisionChanged 返回原错误与本方诊断，不重签 token/续期/盲重试。token 不解析、不记录明文、不在 camera key/MAC/CAS 上建立第二权威。
5. camera 的 MissingRows.Value 只来自已封口 ledger 的 Confirmed ExpectedRange；范围未知为 null，不能以收到 counter 最大值补尾行。原 Counter UInt64/epoch/Boot/Wrap/Reset、CounterRuleRevision、AssociationRuleRevision、ArrivalOrdinal、Exposure 与 RawBytes 完整保存。跨 block 可继续同一 reader 的 source order，但相邻物理面须另核原帧行、同 epoch/rule/association 和邻接；不得把 source order 当连续性。相同域异 hash Conflict 拒绝该源；同 counter 不同域不计 Duplicate/Conflict。
6. 连续几何段在 epoch/boot/counter rule/association rule、wrap/reset/时钟域改变处中断。reader 可以保存多个域，Core v0.4 的单源却没有 segment 字段：同一原 Frame 跨这些边界时物理投影拒绝 MZ-026/024，保留全原事实；不能把不同域合进一份 TimingBundle。已有独立原 Frame/独立 Fov 描述且各自完整资格时才分别入各 Source，不裁掉坏行伪造新 Frame/资格。未知 Counter/Exposure/Association 保留 Unknown/Partial，不把零/空字符串/名义频率当事实。

camera 默认硬上限/8 Task(含2 cleanup)/4 borrow/8 cache pages/32MiB/177-byte token 直接按 §20.3/20.5 使用，不复制协议。mosaic 本次行/页/总字节同时受源限额、Frame.Height/MaxRows 和剩余 ResourceBudget；source 调用/复制前 checked 核完整 payload 与 canonical 较大者、缓存、映射/源纯值驻留的保守上界。fixture page至多4行/每reader65536 bytes；生产不以此常数估算每个 row。正常page必须有新rows推进；null/重复token、空页却非IsLast、返回总数超过原TotalRows/MaxRows均拒绝。正常分页调用数上界为MaxRows（最小每页1行），另只允许1次已有token的确定重放、1次原域Query；不循环Partial/LimitReached/ReplayCacheFull，不为凑齐行数开新reader。串行 read，归还/Confirm 后复用槽，保留纯值结果仍计本方内存，不堆无限已确认 Task/重放墓碑。逻辑 IO 上界与真实 IO 分测，None token 也取总 deadline/MaxObservationWait 的较小值；不每页重置总截止。

#### C.10.3 C.2/C.3 投影与大图/标定分界

原 RowIndexInBlock 是块内行号。最小兼容路径是 **原采集 Owner 已明确 block 对应这份原 FrameRef 且块行索引就是该 Frame 的 row**：核 frame key、block key、原 revision、Frame.Id/Digest/布局/采集配置和完整曝光来源，由现有 LineAuthority 精确验证。多 block 对应同一拼接 Frame 但没有 Owner 提供的公开原 row 映射时，只保留事实/MZ-026，不自行造映射 DTO/用累计块长度或 SourceOrdinal 计算 r。未知 RowIndex 不生成 LineExposure；缺失 r 仍由 Plan 产生诊断槽，不压缩索引。

现有 LineCounter 是非负 long；camera UInt64 原位仅在同一无 wrap/reset 段且 RawBits<=long.MaxValue 时 checked 无损转换。超界仅保留原事实/MZ-026，不做 Int64 重解释、转 double/decimal、减基址、展开 wrap 或造 counter。相邻增量检查必须 checked，恰好1还须原行相邻及时序合法；跨域不连 C.3 面。LineId 是宿主已保存的原行证据标识；不存在公开原 LineId 时可用宿主封口的只读行证据 ValueRef.Id 作为派生稳定引用，明确其不是硬件 LineId；身份须带原 Owner/capture/Snapshot/frame/block/row/revision，全等检查不只看 counter/hash。

DeviceTick64.Encoding=UnsignedUInt64 时仅 RawBits<=long.MaxValue 可投影；SignedInt64TwosComplement 可按其公开编码无损解释，Opaque/未知拒绝，原 RawBits/encoding 始终保存。Clock.Kind=Device、原 DomainId/Epoch/频率证据完整、FrequencyDenominator=1 且 numerator在正long范围，才形成同源 LineClockStamp；其它频率表示现有 Core 未承接，MZ-024，不重采样。start/end、duration>0、uncertainty、association均须 Confirmed且适用；Uncertainty只在编码可解为非负量时经 BigInteger 有理秒→TimeSpan tick向上取整(100ns)且 checked，其源不确定度原位保留，不能向下舍为0。未知曝光/PerBlock或PerCapture关联不足以证明逐行同run曝光时不输出 LineExposure，不从 trigger/encoder token 合成时间。C.2 原 Mapping/曝光中点/Delay/Actual XY/误差公式继续执行；原source stamp不先变target再交 Mapping二次转换。

RowDigest 只在 camera HashAlgorithm=SHA-256、Evidence/Integrity/Closure完整，且 Window.HashCoveredRanges 精确等于原 **整行有效 Byte 单通道像素**、Padding=NoPadding或ExcludedDefined、原 Frame Owner 已证明 FullPayload→Frame行布局和内容相等时，逐字符复用 RawBytes.Hash。PayloadLength/Offset、HashCoveredRanges、LengthBytes、Included/ExcludedRanges和closure均保留原事实；不把PayloadLength当LengthBytes。IncludedDefined padding/非像素窗口/裁切窗口/未知padding虽可在 camera 有效，本版 Mosaic RowDigest 语义不支持，MZ-026，不能把源hash改成去padding摘要或静默扩覆盖。C.5 tile依然单独借整行重算有效像素hash，失败不交tile；归还camera行不代表FramePort/native已经释放。

光学读参数 C.8、同run实际 XY C.9、原行 C.10 为独立事实输入。组合宿主仅在本条链资格完整时按既有 line04-timing 封存 TimingBundle，原 Source refs需在 host证据存储中可追溯；该耐久闭包尚未执行，不把内存页Hash当生产存储。C.2 trace/PlaneInCamera/PlaneToCommon/q_ref/P(q)、C.3 固定三角面/Nearest/tile、光学/安装/动态/独立留出资格不改。camera bytes/行顺序不证明运动坐标；0.5px软件残差/合成向量/平滑大图不证明拼接精度。Mosaic不运行HALCON角点补时间，也不获得采集/触发/质量放行权。

#### C.10.4 双根、原 Task 与有限收尾

mosaic HostOwner 的固定槽在构造前预留，持camera root/source/ports/factory/recovery/ids/clock和完整原请求，成功后补原handle；所有Host公共调用只AsTask一次，保存Create/Snapshot/Page/Query/Close和恢复的**原返回Task**及回执。源LedgerRead/PayloadOpen/PayloadRead/PayloadReturn/PayloadClose/SourceClose原Task由camera §20.3 Attach系列在start调用前闭包预登记、一次AsTask、自动Track成功对象；Host必须强持整个原root，不能只保存ID/WaitAsync。同根只有一个活动public读阶段，原Task未收敛时不新增page/query。任何同步抛错/无handle/迟到结果也走原root路径。

camera没有Reader.DisposeAsync/Stop接口，本消费不发Dispose/Stop或虚构方法。关闭只由原 `handle.CloseAsync(new LineFactCloseRequest(readerId,handle.LeaseId,rootId,budget),independentCleanupToken)` 启动，先封public读，producer依原Row Return→payload/source关闭收尾；未成功handle时直接使用原root和Recover，不造nullable LeaseId。CloseTask只调用一次，未结束只观察，Completed但cleanup未知则由原 ILineFactOwnerRecovery按原Task/阶段必要归还；不重复用户读或重新Create。Close内部不等自己的Task结束，RootCleanup在外层完成，避免自身死锁。

Host在独立有限窗口 `ReadRootAsync → GetTaskAsync/ObserveTaskAsync → RecoverAsync`；request字段/阶段直接按camera §20.2–3，无lease用null，已晚到lease只补原实际ID。先等原业务Task和producer原Row Return，确认payload/source lease真的Released、原borrow空、Task后处理已Confirm，然后 `Recover(Stage=ReleaseRoot)`。核原root释放回执/墓碑、SourceLeaseReleased/RootReleased、CountsComplete、实际borrow/task/计费全部对应；Close.ReaderClosed、IsClosed、NotFound/Expired或cached.Resources不能替代。DeviceStopped不是本只读桥的设备Stop授权或成功断言。

业务与cleanup首异常按C.6.3分轴，cleanup抛/fault/cancel/未知回执保原栈和非零exit；恢复false不删根。Mosaic纯值页归caller后仍由caller记账，不把源释放当owned值已消失。未归还源/迟到payload/Row/Return/Close任何一项，mosaic root一直持原camera root/Task/lease/对象，禁止给已封Host交迟到成功。有限窗口到期PendingRecovery，caller后续继续同槽，不能用杀进程证明归还。仅camera原root已确认Released且本方无活动调用/owned临时量后才退mosaic槽。

#### C.10.5 两个确定无 UI Host

组合Tests分别实现camera §20.6 SyntheticLedger/Payload/Root/Recovery/Clock/Ids的公开接口，不依赖camera私有测试DLL。**逐项使用上游完整 Host-B/Host-X typed fixture**：Owner/session/capture/SnapshotId/revision/RootId/ReaderId/lease/key/nonce/Block/ExpectedRange/Rows/FullPayload/Window/padding/曝光/association沿该表原值构造，不新造c/d或wrap例、不重建codec。两Host都实际走同一 LedgerBackedLineFactSource，测试payload内部计数观测原Return/Close，业务helper不直调它。

| Host | 固定消费步骤与断言 |
|---|---|
| LineRowViewHost / camera Host-B | 构造前Owner固定槽强持完整根；Create=(原B Owner/session/capture/rev-b-1,FixedSnapshot,4,65536,原10s/1s budget)；Snapshot原request；PageSize=2两页2/2；Query沿camera §20.6 B原域100..MaxUInt64。TotalRows=4/TotalBytes=24，MissingRows.Unknown/null；Row B/3 UInt64Max保真，FullPayload6/Window4/padding2由producer核并Return，public RawBytes/hash/closure原值。全部Exposure.Unknown/Partial，四行均不生成LineExposure/mesh，不建manifest、不伪调用Locate成功 |
| LineRowAnalysisHost / camera Host-X | 独立原X所有身份/根，Create同上代入X；PageSize=3两页3/1，跨块source order100,101,102,103不改；Query沿X明确boot-x-1/counter-x-1/100..103。TotalRows4/Bytes24，Missing/Duplicate/OutOfOrder/Conflict=0；块内RowIndex为0/1、0/1，绝不能改成全帧0..3。所有曝光未知，无LineExposure/物理mesh/Execute；分析返回完整原事实和缺曝光/原Frame映射诊断。另开全新fixture执行camera X“缺103”原变体，MissingRows=1，三行/18byte，不补尾行 |

Host实现顺序固定为预留mosaic槽→完整装配→保存一次Create原Task→成功Handle→Snapshot→Page1→Page2→保存一次第二页原token重放（相同页/hash/无Read/CAS增加，first page不能重放）→原Query→本方诊断/投影拒绝→finally原Close及外层Recover。所有等待取case真单调起点+10s、suite120s的剩余，外层180s仅失败观察；cleanup不每次刷新截止，注入ids/source的root参考在Create前保存。Close成功不直接删槽，finally核camera原root/producer所有Task、Row借用、Return、lease和mosaic临时账真实收敛。前步异常跳过后续business阶段，但finally仍有限执行；断言失败/跳过/未结束非零，业务失败不会因cleanup成功改exit0。

迟到反例分别对新B/X fixture的LedgerRead、PayloadOpen、PayloadRead、PayloadReturn、PayloadClose闩锁：同原case观察Pending→cancel等有限read reply→核mosaic槽、camera原Task/borrow非空→独立有限恢复未确认→解除**原**闩锁→同root/handle/TaskId Recover→Row恰好归还一次、Open不增加、Root Released才退槽；原取消/失败业务结果不升级成功。不并发host尚未退出的finally和外层Recover，不切换Factory/Source，不新增第二任务。

这两个Host只验证本次真实只读消费者的协议/资源/拒识。正向几何仍复用C.6既有完整Synthetic大图Host；原B/X未知曝光不满足C.2，不能借用C.6时刻/encoder替它“补正常”。真实可投影行/Frame映射/同run映射和原source耐久闭包是后续集成输入门，不以未执行实现冒充闭合。

#### C.10.6 反例、Benchmark与精确剩余门

| 断言 | 确定输入及预期 |
|---|---|
| LR-01 双Host/原payload | 原B/X流程；FullPayload6、hash覆盖4、Excluded[4,6)、TotalBytes24保真；不把public row当像素lease、不二次ReadRow。UnknownExposure时无物理面、无检测/计量资格；B UInt64Max无损保留且不进long |
| LR-02 缺行/乱序/重复冲突 | 逐项用camera §20.6 X缺103/Duplicate/Arrival2↔3/Conflict完整typed变体；缺103范围不变Missing=1，无范围Unknown；原arrival保留，排序页不抹乱序；同域异hash MZ-002/无几何，完全同重传仅原规范化，不改原正文摘要 |
| LR-03 epoch/rule/wrap/reset | camera X epoch/rule变体只在源ledger/payload/ExpectedRange同步；老域Query只100/101，另一域102/103，跨域不计冲突、不连面；Wrap/Reset未知/Confirmed均原位，不展开RawBits。同Frame多域无独立段表达拒绝，不造Frame或新资格 |
| LR-04 exposure/association/map | 原B/XUnknown字段永不填0；counter/clock未知、频率非整数、Opaque/超long tick、PerBlock不足、Frame/块行映射缺失→MZ-020/024/026。HashWindow/IncludedPadding虽camera有效却不合Core RowDigest→MZ-026，不改源hash；已有有效曝光路径必须全原source与C.2门，不允许用Synthetic数据补设备 |
| LR-05 revision/hash/CAS | FixedSnapshot旧rev原值；CurrentSource变化/Owner撤销拒绝、同row新rev冲突不混入；原Snapshot/Page/Query writer验证正文。旧token/intent/owner/clock epoch/到期/篡改拒绝；第二页同token replay无源read/CAS增加，同hash不同rows拒绝 |
| LR-06 有界账/原Task | 原limits+1、65536请求余额不足、source/canonical/copy/cache/Task预算耗尽→新增source调用前MZ-010，不截行/伪IsLast；None token仍有限，页/任务/缓存有界，不无限保留百万原Task；ledgerNotSupported payload.Open=0 |
| LR-07 归还/失败优先 | C.10.5五stage闩锁，原Task/root/borrow强持；ReturnUnknown/错误CloseID/非零资源假Released/Recover fault保两根，解除同闩锁有限恢复才释放。无Reader Dispose/设备Stop，失败保首栈/exit，不以观察Task完成或cached.Resources清零 |
| LR-08 两Owner隔离 | X拿B token/reader/SourceRevision/Owner或payload实例拒绝，不变B游标/根；B取消不Dispose X；原已released墓碑仅同identity可查，未知不是无资源；SDK/运动/Trigger调用实际计数均0 |

实施时 `dotnet build src/Modules/mosaic/Asun.Modules.Mosaic.CameraLineRead/Asun.Modules.Mosaic.CameraLineRead.csproj -c Release`、`dotnet run --project tests/Modules/mosaic/Asun.Modules.Mosaic.CameraLineRead.Tests/Asun.Modules.Mosaic.CameraLineRead.Tests.csproj -c Release`；LR-01..08/两个真实producer Host及实际归还全完成才exit0。当前未创建/执行。顺序为公开引用与纯请求/保留槽→唯一producer装配→snapshot/page正文/重放→分段与保守投影→双Host/反例→有限收尾/性能测点，不造新协议/设备后端。

沿§14.1分测冷/热Create/ledger snapshot/page/CAS replay/producer Read/完整FullPayload hash/Return/本方原事实保留与适用校验/Close/root release P50/P95/P99、rows/页/canonical与payload bytes、source及本方原Task/缓存/borrow/托管峰值、取消至真实归还/迟到恢复。源producer完整载荷/Return成本、本方纯值投影成本、C.2运动几何成本、C.3 Frame/tile/native成本分别记账；SyntheticClock Advance不是墙钟性能。缺客户目标/真实代表数据为NotEvaluated，不凭协议/hash、0.5px或向量证明精度/最快。

M-LR当前 **ModuleCoreImplementationReady（仅只读软件消费规格）**。外门仍为双方真实程序集/公开引用消费编译、原camera ledger/payload实际Producer/Frame Owner和配置/原帧行映射、曝光/clock/物理association、host源记录耐久、LR运行、真实运动/动态/标定平面/Trace独立验证、HALCON/native、大图拼接性能、耐久/HIL/计量/现场。上游C2-RF为限定内容接收；C.2/C.3同为限定内容接收；M-C1/C2/C3、M-L1/M-LC/M-LM及M-L2限定接收保持。本轮不提高任何真实运行/物理资格，不重建camera/MR/原Core向量。

2026-10-11 / 0.5.5-prep 有限两轮自审完成：第一轮直接比对camera §20的公开reader/producer/typed Task和B/X全字段fixture，修正把上游接收误写成本方接收、从public page索取FullPayload及虚构Reader Dispose/原帧行映射接口的问题；第二轮核source order/ExpectedRange/UInt64/clock/未知曝光、hash window与整行像素兼容、token/CAS有限推进、原Task/双根/迟到Return与Close、两Host拒识及LR-01..08、状态/链接/表格/围栏。定向结构检查和现有validate_docs.py通过，仅证明文档一致性；既有Core DTO/围栏、C.6/LC/LM Host与向量未修改，不新增向量复算声称。只修本指导，无新工程/代码/测试/报告/脚本/会话/子代理；未执行消费编译、LR/LC/LM运行、HALCON/native、WPF、性能、设备/运动/精度、耐久或物理/现场验收。


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

## 附录 D：整模块工程规格收口（0.5.6-prep）

本附录补齐面阵适配、标定冷路径、可选 UI、自动建议和整模块范围判断；不修改 A 的 v0.3/C 的 v0.4 DTO、编码、向量或已接收数学。本附录声明的公开类型是本模块后续工程的目标 API，**尚未创建或编译**；不冒称 AsunImage、viewport、localization 已存在这些成员。文档自审由 mosaic 永久原会话负责，总控只接收状态与转发依赖。

### D.1 完整能力与确定路线

| 输入/任务 | 固定处理 | 失败与能力边界 |
|---|---|---|
| 移动面阵；包括纯色、无圆点、无角点 FOV | 原光学链→曝光关联实际 XY→各相机 G0/d→共同坐标→按需原值 tile；生产 PriorOnly | 纹理不是前置；实际位置/方向/时钟/有效 cell 缺失不靠匹配补救 |
| 固定多相机、同一共同平面 | 显式 NoMotion，各相机自己的 StaticPrior/光学资产/注册资格，逐帧验证设备与配置身份 | 不注入零运动；不复制别的相机矩阵；不同板面/焦层/观察角色不融合 |
| 无资格的大板查看 | 明确 DisplayOnly 的像素域先验，或分离原 FOV 目录 | 不生成 mm/设备坐标或检测资格；无任何先验时不按采集序号排成大图 |
| 离线纹理配准分析 | 显式 PairBundle、固定模型/有限重叠工作集→已验证 pair→bundle→诊断 | 当前 MatchObservation 无 fit/holdout 分区合同，故不授独立物理用途；检测/计量仍 MZ-017/026。无先验且弱纹理则 MZ-007，不强拼 |
| 面阵标定/计量资格 | D.4 冷路径点号/原点→§5.2C 拟合、按物理组留出、逐相机/条件/cell证据→外部资格 Owner | Candidate、Passed、Published均不是资格/激活；证书、安装和物理阈值必须外部提供 |
| 线扫、变速、缺行、多相机扫描 | C.1–C.10；首行光学、逐曝光实际位置、固定三角网和唯一反算、nearest | 不套面阵单矩阵；不补未知曝光、行号、Frame映射、clock分段或源hash |
| 超大图/随机 ROI/顺序导出 | D.3 有界 tile，固定全局网格与来源顺序；只访问相交源窗口 | 不先拼整图；预算不足拒绝当前请求，不减少halo/改LOD/省覆盖检查 |
| 几何连续/接缝两侧分析 | 标定误差门、严格原支持、来源叠放及双侧原图对照 | 几何无洞不等于视觉无接缝；不会用平滑隐藏位移、缺陷或缺源 |
| 显示美缝、辐射、多带 | D.7 精确候选与批准边界；当前执行 None/Stacking | Feather/NamedMultiBand/辐射仍未批准，不以 UI 或预算传参启用；不承诺像素无缝 |
| 独立嵌入控件/语言/恢复 | D.5–D.6；同一无UI服务，两个独立宿主/Dispatcher/根 | 不控制相机/运动，不改配方、几何或质量事实；未释放资源继续保根 |

这张表覆盖当前 IM-023 的大板查看、拼接分析和跨 FOV 检测责任。跨 FOV 的缺陷、工艺测量、合并与放行由调用方自己的算法/领域处理；mosaic 只交付合格坐标、支持与原来源，不新增产品判定模型。2D平面无法解释的高度/视差转3D Owner，不在本模块扩大自由度。

### D.2 面阵 Adapter 的工程、公开装配与资源根

唯一规划工程 `src/Modules/mosaic/Asun.Modules.Mosaic.AsunImage/Asun.Modules.Mosaic.AsunImage.csproj`（与 C.7 的线扫适配工程共用），namespace `Asun.Modules.Mosaic.AsunImage`；唯一测试工程 `tests/Modules/mosaic/Asun.Modules.Mosaic.AsunImage.Tests/Asun.Modules.Mosaic.AsunImage.Tests.csproj`。工程引用 Core 与用户现有 AsunImage，不直引 halcondotnet，不扫描封装内部、不下载依赖。只能在这两个目录实现面阵适配/测试；其它模块、产品和上游原件禁止修改。目标 net10.0；测试为有有限截止点的 Exe，真实视觉用已授权代表集，模拟契约用确定性闩锁，二者结果分开。

```csharp
// 本模块的目标公开面；类型来自 Core，非 ImageLibDotNet 的签名。
namespace Asun.Modules.Mosaic.AsunImage;
public record AreaPairReadResult(IReadOnlyList<MatchObservation> Matches,
    ResourceLedger Resources, IReadOnlyList<MosaicError> Errors);
public interface IAreaPairObservationPort
{
    ValueTask<AreaPairReadResult> ReadAsync(RegistrationWork work, CancellationToken ct);
}
public record AreaMaskReadRequest(FrameRef Source, MaskRef Mask, PixelRect Window,
    PermissionScopeId PermissionScopeId, DateTimeOffset DeadlineUtc, ResourceBudget Budget);
public interface IAreaMaskLease : IAsyncDisposable
{
    MaskRef Source { get; }
    PixelRect Window { get; }
    long StrideBytes { get; }
    ReadOnlyMemory<byte> Pixels { get; }
}
public record AreaMaskReadResult(IAreaMaskLease? Lease,
    ResourceLedger Resources, IReadOnlyList<MosaicError> Errors);
public interface IAreaMaskReadPort
{
    ValueTask<AreaMaskReadResult> ReadAsync(AreaMaskReadRequest request, CancellationToken ct);
}
public record AreaAdapterResources(bool Closing, uint ActiveCalls, uint PendingPortCalls,
    uint NativeHandles, long NativeBytes, uint BorrowedInputs, uint MaskLeases,
    uint OwnedBuffers, long OwnedBufferBytes, uint PendingDisposals);
public record AreaAdapterDrainReceipt(DrainStatus Status, AreaAdapterResources Resources);
public record AreaPendingWork(Guid OwnerEpoch, long Sequence, Task Completion, string Reason);
public interface IAreaAdapterResourceOwner
{
    void Retain(AsunImageAreaMosaicAdapter adapter, AreaPendingWork pending);
    void ConfirmReleased(Guid ownerEpoch, long sequence);
}
public record AsunImageAreaAdapterOptions(Guid OwnerEpoch, uint MaxConcurrentCalls,
    uint MaxPendingCalls, uint MaxNativeHandles, long MaxNativeBytes,
    uint MaxOwnedBuffers, long MaxOwnedBufferBytes, TimeSpan MaxObservationWait,
    TimeProvider Clock, IMosaicDiagnostics Diagnostics, IMosaicCoordinatePort Coordinates,
    IAreaPairObservationPort? PairPort, IAreaMaskReadPort? MaskPort,
    IAreaAdapterResourceOwner ResourceOwner);
public sealed class AsunImageAreaMosaicAdapter : IRegistrationAdapter,
    IMosaicCalibrationAdapter, IAsyncDisposable
{
    public static AsunImageAreaMosaicAdapter Create(AsunImageAreaAdapterOptions options);
    public ValueTask<RegistrationWorkResult> RegisterAsync(RegistrationWork work, CancellationToken ct);
    public ValueTask<TileRenderResult> RenderTileAsync(TileRenderWork work, CancellationToken ct);
    public ValueTask<CalibrationSolveResult> FitAsync(MosaicCalibrationRequest request, CancellationToken ct);
    public ValueTask<CalibrationValidationResult> ValidateAsync(CalibrationValidationRequest request, CancellationToken ct);
    public AreaAdapterResources ReadResources();
    public ValueTask<AreaAdapterDrainReceipt> DrainAsync(DateTimeOffset deadlineUtc, CancellationToken ct);
    public ValueTask DisposeAsync();
}
```

Create仅验证正值/checked上限、非空OwnerEpoch和端口引用；无IO、native、窗口、设备或隐藏初始化。MaxConcurrentCalls<=MaxPendingCalls，Clock/Diagnostics/Coordinates与消费服务显式一致。宿主在开工前建立固定容量Owner槽：容量至少 MaxPendingCalls+MaxOwnedBuffers；call槽与buffer/处置槽分区，沿C.6.4的预留→原Task登记→开工→真实释放确认规则，不能把 line adapter 实例当 area adapter。槽满、序号溢出、关闭、新预算不足在借入/开工前拒绝。Retain只能向预留槽写原引用，同步非阻塞且不抛；资源根强持原adapter/Task/租约/处置任务，直到实际退出且全部借用归还。原Task fault/cancel、Drain观察超时、Dispose返回都不能自行清槽。

Register的PriorOnly分支只复核冻结规划及坐标端口，不做native识别；按ObservedFramePose形成 FovGeometry，VisualCorrection=null/VisualResidual=null/Covariance=NotProvided。不为Register提前借全体像素；已有service工作集租约只借用，不由adapter归还。PairBundle只在DiagnosticOnly=true且Purpose=GeometryDiagnostic/Display时接受；PairPort=null为MZ-026。端口仅能访问本work已准入的窗口/预算，先核Role/域/已知重叠，再交付A.1 MatchObservation；按来源ID和candidate稳定顺序检查支持、对应点/自报残差、有限搜索和冲突，构造官方1起索引，调用cv2.bundle_adjust_mosaic。平均Error不填独立证据；返回几何明确DiagnosticOnly，生产请求即使点数很多也拒绝。端口原Task与native工作都纳入同一call根，不另起失联任务或全组合匹配。

MaskPort只消费上游保存的精确mask值。窗口坐标为原帧pixel、内容为一字节0/1（非0/1拒绝）、stride>=Width，checked容量>=stride*Height；Source必须精确匹配请求Mask/原Frame/LeaseRevision/完整digest。读取者在交付前按原Owner格式核完整mask摘要和有效数，再借指定窗口，不能把裁剪窗口hash当完整maskhash。Mask!=null而端口未注入时MZ-026，不当全有效；来源不符MZ-002/003。Mask租约由adapter归还，原图租约由service在adapter真实退出后归还，二者Owner分开计数。迟到Mask lease仍进入原call finally归还，不因显示generation失效漏返。

Render成功只交付独立owned托管tile buffer，native临时对象和mask借用已经实际释放；buffer处置仍占原Owner槽，service只有一次输出交付权（§9.2）。其它分支先清理真实资源再结束原Task；未知继续保根。ReadResources不枚举句柄；Drained要求全部活动/占用计数为零。Drain到期返回DrainUnknown，token只取消观察；Dispose停止准入/请求取消后有限观察，不伪造native已停。恢复只在原实例/原Task上观察和归还，不new adapter替代仍占用实例。

最小装配次序：宿主clock/limits/diagnostics/原frame与coordinate端口/asset端口→自己的area资源根→Create(areaOptions)→MosaicModule.Create(A.1 Options，RegistrationAdapter和CalibrationAdapter都指该area实例)→解析精确snapshot→Validate/Plan→Execute或Solve/Validate/Publish→GetTile并finally归还→原service Drain→原adapter Drain→分别Dispose。service与adapter两根均确认空才释放宿主引用。查看Host只取Display原tile；分析Host按原Frame/SourceContribution交自己的检测/计量能力；每Host own sessionEpoch/ownerEpoch/根/预算，不共享可变static。具体资源数字沿调用方已采纳Profile，不从装配算例推导生产吞吐。

### D.3 面阵 tile、有效支持、LOD 与导出

本方法固定为面阵基线 `area-prior-nearest-v1`，AlgorithmRevision绑定此语义。当前采样一律Nearest，DisplayBlend仅None/Stacking；请求/manifest有Bilinear contribution时拒绝MZ-026，不从HALCON默认决定核。Nearest是原像素选择，不是物理精度保证；检测/计量优先原FOV与已资格坐标，不以重采样图替代原数据。Byte/UInt16/Int16/Float32按HALCON byte/uint2/int2/real原类型处理；同输出通道的所有贡献类型必须相同，通道数为1或3、Role相容，禁止隐式截断/跨曝光平均。其余类型/通道组合拒绝MZ-003/026。方向Identity以外只在显式坐标链已包含原方向变换时合法，内存仍原方向，不能再旋转一次。

1. 固定Grid的Origin为LOD0像素(0,0)中心的共同坐标，s=(PixelStepX,PixelStepY)换到Grid.Unit。TileKey.X/Y为该LOD的tile整数序号，core像素范围为[X*T,(X+1)*T)×[Y*T,(Y+1)*T)，T=TileCoreSize。Lod=l时，中心(i,j)对应common=(Origin.X+2^l*i*s.x,Origin.Y+2^l*j*s.y)。负tile/坐标用数学floor/checked，不能截断向0。PhaseAnchor是批准全局相位，不随tile改变；LOD原点复用Origin，方法不另加半格。不相容的frame/单位/phase拒绝，Detection/Measurement只接受Lod=0，显示LOD只作固定稀疏取样并标记，不能宣称抗混叠或缺陷保持。
2. 来源排序按完整稳定FovId UTF-8字节升序固定为StackingOrder；最大序号在上。None在一个输出中心同时有多个合法源时返回Seam.Conflict/MZ-026，不替它选源；Stacking在所有合法源中取最大序号。相容层与保护区先冻结；保护RectD是半开共同坐标域，选一个能完整支持该区全部输出中心的最高序号来源，不能每tile/每像素换源。无该来源为冲突，不跨源拼出“完整保护”；预算不足证明完整支持也拒绝。该方法没有插值权重/色调补偿或隐含seam优化。
3. 对core加Grid.Halo形成工作框，查询manifest冻结几何的保守footprint空间索引。四角/边包围仅用于找候选，实际覆盖由逐输出中心支持确定；projective分母跨零/不可逆/原valid域外拒绝该来源，不以bbox证明有数据。按逆Final求原pixel中心，坐标链含crop/方向/畸变时逐边逆求值，不能用光学校正矩阵假装非线性逆map。Core的CoordinateChain仅矩阵边；宿主必须预先给精确校正派生Frame及其公开链，或显式原光学映射端口的已批准派生。当前矩阵合同不能表达的原非线性映射返回MZ-026；不猜RectificationMap引用内容，也不将未经声明的已校正图冒充原帧。
4. nearest取n=floor(u+0.5)，再核n处于原ValidWindow、所借Window与原Mask有效域。恰好半格按此规则；不clamp到边缘，不以无效0像素作覆盖。反算和实际核支持均有效才建立source贡献；不同源均无支持的位置是NoData，Coverage/Holes保原义。尚未借到exact窗口或mask不能宣称像素支持已核。
5. 用合法取样点计算最小原整数窗口；请求当前tile的有限SourceWorkset，只借该窗口。索引估算若超MaxSourceLeases则按来源顺序流式读取/覆盖独立输出，并把逻辑读取、解码、map、源缓冲、mask、输出计入真实峰值；不能假设整个解码器只占窗口bytes。无法在预算内取得某必要窗口返回MZ-010，不能丢源再判完整。CPU/tiles/IO亦累计。输出core不重不漏，halo仅内部使用/不交付；本nearest方法自身滤波支撑为0，多给halo也不能扩大支持。
6. 通过cv2.gen_image1或gen_image_interleaved按实际布局/类型导入有限窗口，保强引用/必要pin至真实native退出。自定义map只编码上述坐标合同的反算索引，不实现另一种视觉配准算法：用gen_image1建立单通道int4线性nearest map，索引=localRow*windowWidth+localColumn，逐值checked且在原native输入内。无效输出先放安全索引0，另建严格有效region；全无效不调用native。不使用-1/越界索引。cv2.map_image后用有效region/reduce_domain明确裁去无效值；输入mask不能指望算子替本方检查。map_image官方明确不检查输入越界，错误索引可能崩溃，因此此预检不可省。int4容量不足则缩小经准入的窗口/工作块；若仍不满足MZ-010，不偷偷使用另一HALCON构建或int8。
7. 按固定来源次序将各map结果的有效支持写入同类型独立输出；native标量/通道布局与FrameRef逐项核对后复制托管buffer。用原source像素矩形与输出最大连续同源行段（高1，遇NoData/换源分段）形成SourceContribution，Kernel=Nearest，非恒等为Resampled，Mask保精确原ref，不把整个tile标单一来源。没有契约字段可放每像素标签时不得省掉这些段；段数/目录/输出预算不足拒绝，不以粗bbox冒充来源支持。输出Frame.ValidWindow为有限tile矩形；存在NoData时Mask非null精确标无数据区域，来源mask/输出mask不能混用。buffer槽同时拥有compact pixel bytes及同形0/1 mask bytes，Frame.Id/Storage.Id由原OwnerEpoch+槽Sequence确定，Revision=manifest.AlgorithmRevision；Frame.Digest与Storage.Digest为这些compact pixel原bytes的SHA-256，Mask.Digest/Storage为compact mask原bytes的SHA-256，ValidPixelCount实数1的个数。Frame总容量/stride/type/layout按真实buffer声明，不把NoData的内部0作为有效灰度。Storage是本进程owned buffer引用，不伪造磁盘路径或耐久发布；生命周期随lease，跨进程/持久化由宿主自己的Store另封存并保派生关系。当前tile消费者直接借Pixels并以完整贡献行段判支持；D.5显示桥按同段重建0/1显示mask复制到viewport自有buffer，不通过不存在的读输出mask方法或重新借原帧。在owned lease上没有二次Acquire权，释放后旧Storage不能再读取；Query同样不重交付。
8. 缓存键含manifest内容摘要/权限、完整TileKey、算法revision、原帧及maskhash/lease revision、Grid/Profile/几何来源。只缓存已封存派生；依源hash核损坏后重建本项，原帧不改。tile相邻边、负坐标、偶/奇尺寸与不同工作块分法必须逐值/支持/来源顺序等价。整板导出是宿主依相同目录按Y/X顺序取tile、逐个耐久写入并归还；导出器只在完整sink回执后公布文件引用，Unknown按原sink事务查询。mosaic不新造文件编码器/Store，导出不是服务全图API。

`gen_projective_mosaic/gen_bundle_adjusted_mosaic`只在有界离线诊断中使用，并记录官方返回TransMat2D、1起stacking索引与TransformDomain=true；算子自动画布/原点不一定等于Grid，不将其结果直接冒充tile。生产采用上面的固定map方法。`affine_trans_image_size`忽略输入domain、且图像矩阵采用(row,column)/角点原点，不能直接替换本中心坐标算法；中心/角点桥仍按§5。不得调用set_system改变全局int_zooming或默认线程设置。

### D.4 标定冷路径：全局点号、原点反算与候选验证

局部目标检测唯一在 calibration-assets §7.1/7.2A，不复制到mosaic。输入是已保存的局部Point/Pixel/Local及方法/质量/原图/曝光证据，局部质量不足先拒绝，不用“圆很多”替代资格。mosaic组合层只做身份关联与已有Local坐标的跨FOV几何。

周期板身份算法固定为有限候选消歧：按参考点表拓扑枚举与可见局部邻接相容的整数行列偏移/板对称方向，候选数及所有约束比较计入请求Cpu/Memory预算；不能在预算耗尽时返回当前最好。先核Reference.OriginAndDirection/Installation的精确板原点、两轴与手性证据，再核同物理板的重叠点一致性/原曝光实际运动的已知界。相同局部点不得绑定两个全局PointId，全局点也不得由同帧两个观测占用；未知图像顺序不作为约束。只有一个候选满足全部已提供证据才采用，0个为MZ-007/004，>1为MZ-007；完整候选与拒绝原因留诊断。不能拿待拟合的G0/d反过来证明自己的点号，不能把命令位置/最近邻残差当身份真值。断帧或失去跨组证据时重新提供原点/方向/安装或明确锚点；编码靶仅作身份信息，不替圆心计量。

已唯一关联后，LocalPointObservation.Id就是Reference.Points中唯一PointId；CameraBasis.RegisteredLocalToCommon必须与该相机身份/校正局部frame匹配。本基线将其线性部分记A，平移固定0（共同原点单独估计），2×2非退化，单位先显式统一。对每个点k算 `o_k = reference[k].Position - A*point[k].Local`，按PointId完整UTF-8顺序求二维算术均值o；**不再拟合旋转/尺度/剪切**。至少3个非共线已合格点，局部观测方法与Profile.LocalObservationMethod精确匹配；残差 `o_k-o`与Local/参考计量证据一起由冻结CommonOriginMethod产生ErrorBounds（RMS/P95/最大值/系统误差），没有证书误差或方法界不得填0。CommonOrigin.PointIds恰好为用到的点集，LocalMethod=Profile.CommonOriginMethod，Position=o；Group.Digest沿A.2 observation-group投影。这个反算是冷路径组装/校验规则，不新造生产点识别API，不根据q_enc直接填CommonOrigin。

FitAsync先验证组完整来源、point IDs、分区/曝光不跨fit/holdout，重新核CommonOrigin与上式一致后，按§5.2C用cv2.vector_to_hom_mat2d拟合实际XY→共同原点G0，再按稳定组ID/node归属求残差均值d。物理XY是数学(x,y)，不在此拟合中加图像0.5；图像局部Point到Local的半格桥只在上游公开链做一次。相机A独立、方向/温度分子场、四角和边界规则不变。MaxConditionNumber检查归一化设计矩阵条件数（BCL实现仅小矩阵数值检查，不替代HALCON拟合）；退化/预算超限拒绝，不提高自由度。

ValidateAsync使用完全未参与拟合的PhysicalGroupId/ExposureId，按相机/条件/cell求o_hat=G0(q_enc)+d(q_enc)，同时比较组原点及每个point的 `o_hat+A*Local` 与Reference.Points；按冻结PurposeLimits输出逐cell ErrorBounds/Passed，缺holdout点/证书/速度方向温度覆盖则NotEvaluated/Rejected。Fit与Holdout重复身份即拒绝，不能随机拆同曝光点作独立留出；不利用Holdout调参后仍称独立。Validate只形成MosaicValidationEvidence，不授资格。发布前完整Candidate/Partition/Validation摘要复算，外部Store/Qualification仍沿§10及原Owner，未知回执查原PublishId。标定异常、取消、迟到资源复用§9.2/D.2原Task根；不因取消拟合丢掉待确认发布事务。

合成说明：A=identity、参考三个点=(10,20),(11,20),(10,21)，Local=(0,0),(1,0),(0,1)，则三个o_k均(10,20)，原点o=(10,20)。任何一个点错关联到相邻周期点必须被身份/残差门拒绝；若原点/方向证据缺失，即使三个残差全0仍不能接受全局点号。此例只验证反算定义，不给真实误差阈值。

### D.5 可选 WPF 控件公开面与真实宿主装配

PageContract唯一实施位置是§11.1+D.5–D.6，不另建第二页。工程 `src/Modules/mosaic/Asun.Modules.Mosaic.Wpf/Asun.Modules.Mosaic.Wpf.csproj`，namespace `Asun.Modules.Mosaic.Wpf`；测试 `tests/Modules/mosaic/Asun.Modules.Mosaic.Wpf.Tests/Asun.Modules.Mosaic.Wpf.Tests.csproj`。两者net10.0-windows/UseWPF=true，测试OutputType=Exe；Wpf只引用Core和本机25.2.3 DevExpress WPF，不引用area/line adapter实现。viewport/localization组合桥放消费宿主，显式引用各自公开包，不把它们ViewModel/全局资源/句柄带进控件。上述两目录是UI切片唯一允许实现位置，其它模块/产品代码仅在另行授权的集成切片接线。

```csharp
// 本模块的目标公开面，尚未实现/编译；所有集合构造时防御性复制。
namespace Asun.Modules.Mosaic.Wpf;
public enum MosaicUiAction { Run=0, Solve=1, Validate=2, Publish=3 }
public record MosaicUiRequests(MosaicRequest? Run, MosaicCalibrationRequest? Solve,
    CalibrationValidationRequest? Validate, CalibrationPublishRequest? Publish);
public interface IMosaicUiRequestPort
{
    MosaicUiRequests Capture(MosaicUiAction action);
}
public record MosaicUiPermission(bool Allowed, string ReasonKey, long Revision);
public interface IMosaicUiPermissionPort
{
    MosaicUiPermission Check(MosaicUiAction action);
}
public record MosaicTextEntry(string Key, string Text);
public record MosaicTextSnapshot(string CultureName, long Revision,
    IReadOnlyList<MosaicTextEntry> Entries);
public interface IMosaicTextPort
{
    MosaicTextSnapshot Capture();
    event EventHandler? Changed;
}
public record MosaicPick(long Generation, Point2 CommonPoint, FovId? Source);
public record MosaicPresentation(long Generation, MosaicManifestRef Manifest,
    TileKey Key, FrameRef Frame, ReadOnlyMemory<byte> Pixels,
    IReadOnlyList<SourceContribution> Contributions);
public record MosaicPresentReceipt(bool Presented, IReadOnlyList<MosaicError> Errors);
public interface IMosaicUiDisplayPort
{
    System.Windows.UIElement View { get; }
    event EventHandler<MosaicPick>? Picked;
    ValueTask<MosaicPresentReceipt> PresentAsync(MosaicPresentation presentation, CancellationToken ct);
    ValueTask ClearAsync(CancellationToken ct);
}
public record MosaicUiBudget(uint MaxPendingTasks, uint MaxVisibleTiles,
    long MaxHeldTileBytes, uint MaxTreeRows, uint MaxTextCharacters,
    TimeSpan MaxObservationWait);
public record MosaicUiRootOptions(Guid OwnerEpoch, TimeProvider Clock,
    MosaicUiBudget Budget, IMosaicDiagnostics Diagnostics);
public record MosaicUiCleanup(bool Detached, bool Drained, bool WaitCancelled,
    uint PendingTasks, uint HeldLeases, IReadOnlyList<MosaicOperationId> PendingOperations,
    IReadOnlyList<MosaicError> Errors);
public sealed class MosaicUiRoot
{
    public static MosaicUiRoot Create(MosaicUiRootOptions options);
    public ValueTask<MosaicUiCleanup> TryRecoverAsync(DateTimeOffset deadlineUtc, CancellationToken ct);
}
public record MosaicControlOptions(string BindingId, IMosaicService Service,
    IMosaicUiDisplayPort Display, IMosaicTextPort Texts,
    IMosaicUiPermissionPort Permissions, IMosaicUiRequestPort Requests,
    System.Windows.Threading.Dispatcher Dispatcher, MosaicUiRoot Root);
public sealed class MosaicControl : System.Windows.Controls.Control
{
    public MosaicControl();
    public ValueTask<ValidationResult> BindAsync(MosaicControlOptions options, CancellationToken ct);
    public ValueTask<ValidationResult> ShowAsync(MosaicResult result, CancellationToken ct);
    public ValueTask<MosaicUiCleanup> UnbindAsync(DateTimeOffset deadlineUtc, CancellationToken ct);
}
```

Root/Control构造纯校验，无Application.Current、窗口、服务定位器、设备或IO。root epoch非空，budget每项正值/checked，时长有限；绑定ID UTF-8 1..128且一个root只承接一个binding，固定MaxPendingTasks槽/MaxVisibleTiles lease槽，不增长无界队列。Bind在所属Dispatcher校验Control/Display.View.Dispatcher与options.Dispatcher为同一实例，Texts.Capture必须完整覆盖D.6键且文化为宿主支持的已加载语言、Revision>0、无重复/空文本/超预算；权限错误/未绑定显示原因。绑定成功只是空UI安装，不伪造呈现或调用Run。重复同ID/同实例幂等，冲突拒绝MZ-028，不解绑旧实例迁就新请求；同View已被其它可视父级使用拒绝，不能把控件从别的宿主拆走。

IMosaicService始终借用，控件/root不Dispose或Drain别人service；宿主长期service资源根强持至自己的真实关闭。root强持options、控件、原DispatcherOperation.Task、display原Task、已发操作及处置原Task；登记先于任何异步/借用。每个操作ID和输入完全由Requests.Capture提供（纯同步读取已冻结宿主快照，不拍照/移动/存储），恰好对应action一个非null请求，其它为null；没有请求就显示“未提供输入”。Check在按钮与执行前各核一次；最终Frame/Asset端口仍自己复核权限，按钮允许不是授权凭证。Run/Solve/Validate/Publish沿Core唯一方法，有限观察PendingDrain后只查询原operation/原PublishId，不自动Capture新请求/重写发布。UI不生成资格/激活请求；Candidate/Passed/Published状态分开显示。

Show只接收本绑定作用域、可验证manifest与MosaicResult身份；清楚保留ExecutionStatus/用途/缺口，不能拿诊断结果当DetectionUsable。输入没有可用manifest时显示原FOV/原因，禁止将上次图继续标为当前成功。每次切换manifest/视图/选择增加checked generation；目录/输入不改变，只撤销旧显示准入。树按Tile→Observed FOV→来源/分量投影，超MaxTreeRows用有界分页/虚拟化，不截断后假装完整；缺源/Skipped/用途阻断始终在固定状态区。Details是显式只读投影，不把整个request反射为可编辑PropertyGrid。

IMosaicUiDisplayPort是宿主窄桥，不是viewport的新API。实际宿主按D.5.1完成既有v0.2预绑定，并按D.5.2把独立显示副本经认可源生产者接入viewport 0.3.5-prep；成功绑定的UIElement及窄桥再显式交给MosaicControl。Present只借本次Pixels至其**原Task真正退出**；副本先由image-frame发布Owner复制发布，再登记到冻结的同Frames实例，首次Attach一次、后续完整Update/Commit/实际可见确认，返回Presented=true仅当其真实呈现回执允许。false/异常/取消同样必须在不再读取原Pixels后结束原Task；不能“已排队”就返回。不允许桥把mosaic原lease长期塞viewport，也不把WPF属性赋值当可见回执。显示复制/原Task未退出，mosaic root继续强持tile；viewport自身copy/presenter/backend借用由其原root持有，Clear实际退出前不宣称该显示资源解除。

可见tile按Y/X稳定调度，MaxVisibleTiles/MaxHeldTileBytes与服务输出上限共同准入。取得tile后核Available、精确manifest/key/generation/frame/贡献身份，才Present；迟到/越代lease不显示但仍真实Dispose一次。呈现任务在等待截止后继续保原Task+lease，不能在finally提前返还仍在读的Pixels。真实退出后归还原lease；Dispose Task也先登记、有界观察，未知保根。generation最新胜只停止尚未开始的显示请求；检测/标定/发布及已接纳业务操作不丢。TileOperationMetadata无重交付权，Query不取第二份lease。

Pick仅接受当前generation/共同frame的合法点；按manifest原支持求全部SourceContribution，显示原值/来源与派生值区别，无源显示NoData。Display桥只转换屏幕/显示到common，不能制造原pixel/修正geometry。主视图与双侧原图锁同common位置，双侧显示以独立budget/lease槽计；不足时明确暂停对照，不抢占检测借用。UI导航不会改Grid、Profile、生产用途或设备命令。

关闭顺序：关闭binding准入/增加generation→解绑Picked/Changed/进度投影→请求取消本UI已发操作/排队任务→display.Clear原Task→等原Dispatcher与Present真实退出→归还tile/处置→查询已发Core操作确认本UI未交付输出/资源归还→返回MosaicUiCleanup。Observe截止=min传入deadline,now+MaxObservationWait，token只取消观察；Detached表示事件/界面已撤，与Drained不同。Unloaded只请求关闭，不当完成。TryRecover沿相同原root/Task/operation串行接续，不能与未退出Unbind/finally并发清理、不能重Present/重Execute。Drained必须tasks/leases/pending operations均0、Clear已真实完成；Dispatcher关闭/错误、未知呈现/归还留根，宿主仍保viewport及service原根。原业务失败、取消、观察超时不因清理成功改成成功。

DevExpress的精确控件组合沿§11.1；本机25.2.3 XML已核 `DockLayoutManager.LayoutRoot`、`LayoutGroup.Items`、`LayoutPanel.Control`、`PropertyGridControl.SelectedObject/ReadOnly`。布局用DockLayoutManager/LayoutGroup三个LayoutPanel，Control分别为借入View、TreeListControl、只读PropertyGrid；顶部可见普通命令，详情/状态固定，不为了视觉隐藏取消/恢复。TreeList ItemsSource/View/列模板必须在该25.2.3消费工程编译绑定，当前不猜其它版本属性名；初版用本方层级投影绑定普通列，禁止临时引入动态属性探测。控件模板/色彩/图标/排版与DevExpress宿主主题继承一致，geometry资格/Unknown/NoData不只靠色彩。官方XML是API依据，不是WPF运行证据。

#### D.5.1 viewport WPF v0.2 的实际宿主预绑定与有限归还（0.5.7-prep 窄同步）

依据仅为 [`viewport` 0.3.4-prep §10.6～10.9/10.6.1](../viewport/DEVELOPMENT-GUIDE.md#1061-v02兼容分类与消费者窄同步边界)。上游已明确 mosaic 是实际消费者；影响位于**宿主的预绑定装配与显示桥内部**，`IMosaicUiDisplayPort`、`MosaicControlOptions`、`MosaicPresentation`、`MosaicUiRoot` 及既有清理/三语契约不变。Core API、算法、Root/Close、lease Owner与向量不因此重开。以下为上游目标公开面的准确消费顺序，不是已有程序集/真实WPF运行证据；宿主须绑定对应 WPF Assembly Contract v0.2 包，不能用Core API版本推断UI成员存在。

1. 在目标STA/所属Dispatcher建立宿主有限Owner，保存同一 `new ViewportRootFactory().Create(ViewportRootOptions)` 返回的root，并取 `root.CreateFactory()`。构造 `Asun.UI.Viewports.Wpf.ViewportControl()`，强持其稳定 `IViewportControlBinding.Presentation`；它在Bind前不Acquire、不自动找session。root/limits/显示源、坐标、授权与真实资源准入仍由原宿主显式提供，不在mosaic新建另一套viewport Root或资格Owner。
2. 内置显示路线调用 `ViewportRendererFactory.Create(control, root, new ViewportRendererOptions(policy, nativeBytes, rasterBytes, pendingCount, cleanupBudget))`，检查 `Outcome=Succeeded` 且 `Value!=null` 后保存该 `ViewportRendererPorts`；以 **Value.Backend** 填 `ViewportOptions.Backend`、**Value.Lifetime** 填Bind的Lifetime，不能把Ports record当lifetime。factory用这些端口创建同root的session，`ViewportOptions.Presentation=control.Presentation`。若宿主保留自己的backend/lifetime，只按上游公开端口实现并显式登记同Control/root；不强制换renderer、不探测任意object payload。真实生产按原Profile/Required准入；离线Raster仅上游批准的离线用途，不能因权限/资源失败退到离线显示冒充生产。
3. 按宿主语言调用 `ViewportUiResourceCatalog.Get(language)`，检查Succeeded/非null才取完整快照；或提供上游 `RequiredKeys` 与实际图层 `LabelResourceKey` 全部覆盖的自定义完整快照。`ViewportUiResources.Revision` 精确为 `viewport-ui-text/1`，不能用旧七键或任意fixture revision。资源表/占位符/限额只以viewport §10.9为权威，不复制到mosaic三语表。未知culture的Get拒绝时停止预绑定，不隐式回退；合法扩展文化由宿主提供同schema完整包。
4. 保存原 `control.BindAsync(session, root, new ViewportUiBindingOptions(bindingId, ownSession, resources, cleanupBudget, Lifetime: lifetime, ExecutionBudget: uiBudget), ct)` Task，检查Succeeded/非null后保存其返回的**同一个** `IViewportUiBinding`。`lifetime`须来自步骤2的同Owner/同Control实例且非null；参数尾部在源码可省略不等于真实Bind允许null。ExecutionBudget为真正可选，但实际负载要按原Profile显式预留metadata/原Task/旧新代/presenter、tile复制和可见观察成本，不能以软件默认额度推实际可运行。Bind只安装空控件；完成之后才能 Attach，避免相互等待。成功后将该control作为Display.View、同宿主桥作为Display交给MosaicControl；本方options不增加Lifetime参数。此桥默认借用宿主session，`ownSession=false`时仅宿主最终关闭它；若原宿主明确选择true，沿上游scope外一次性Session关闭责任，不改变mosaic借用Service语义。

自有 `IViewportUiLifetimePort` 的 `AcquirePresenterAsync` 第一参数必须是新版 `ViewportPresenterSubmission`，保留其中 `Request`、完整原 `PresentationRequest` 和原 `SourceCall`；旧 `PresenterLeaseRequest` 不是保留重载。同session/root的授权、context/generation/backend及deadline仍由上游验证，宿主不能new一个提交回执/CallContext证明自己有呈现权。Confirm/Return/Revoke沿原Owner；若宿主实现Presentation代理，其Commit/Revoke必须直接返回 `control.Presentation.CommitAsync/RevokeAsync` 的**原Task**，不以async/wait包装替换它。mosaic的Present ValueTask仍是本方像素借用边界，不能冒称它就是viewport OriginalCommit。

显示桥先在自己的有界槽登记本次mosaic manifest/key/generation与原Present Task，按D.5.2经image-frame复制发布及公开CPU源生产者登记，保存原source/frame身份及其授权；没有第二次读取mosaic输出Storage/Acquire的权利。已绑定同session首次Attach一次，之后用完整Update，再由上游受信Submit→Commit→Confirm。只有完整原回执身份/授权/代次一致、Succeeded且VisibleConfirmed=true才返回 `MosaicPresentReceipt.Presented=true`；实际viewport可见观察沿上游§10.8，不能将Bind成功、属性赋值、flush或任意Rendering事件当true，也不在mosaic实现第二套可见性算法。复制、提交与清理必须沿同有限剩余deadline，不给每一步重新增加完整超时。

原runtime binding的 `GetPresentations()` 可供宿主恢复诊断关联 `OriginalCommit/OriginalAcquire/OriginalConfirm/OriginalRevoke/OriginalReturn`、PresenterIdentity及Cleanup；它仅返回有界观测快照，不把presenter lease交给mosaic，也不授重复提交/归还权。完全同提交重复调用由上游返回同原Task，冲突拒绝；观察Task结束不移除原根里的Task/lease。mosaic仍持自己的tile直到本方原Present真正退出且无组件继续读取其Pixels，再归还一次；viewport copy/presenter/source borrow沿viewport原root独立归还，不能以mosaic tile已返推viewport Drained。

Clear承担本Display专有viewport的整幅源/叠加清空，按D.5.2提交合法空Update并核实际EmptyTransition；原Revoke链是空Update内部旧代清理，不是单独完成清屏的证据，不额外Acquire旧源。最终关闭按D.5既有封门/撤订阅/取消/等待顺序，由宿主在slot worker之外观察原 `binding.UnbindAsync(remainingTimeout, ct)`；它只作有限观察，Detached/WaitCancelled/Task.IsCompleted不替Drained。Unbind与Core Revoke共用同原presentation清理记录，不能各clear/Return一次；Acquire晚到、失败Value带lease、handler尚未登记字段的lease仍由viewport原Task extractor/原root捕获，先原Owner Revoke确认CallbacksQuiesced+ReferencesDetached，再同ReturnId归还/查归还。观察截止后保原Bind/Dispatcher/Commit/Unbind/Return Task、binding/lifetime/root和借用预算，不new实例避开未知。原Unbind/worker未退出时不并发启动另一清理；后续有限恢复仍观察原链，已armed清理由原root继续。

同binding确认Drained之后，OwnSession=false的session由原宿主在worker之外有限Dispose，OwnSession=true由上游已登记scope外Owner触发/观察同一次Session关闭；随后原宿主在worker之外有限 `root.CloseAsync(timeout,ct)`，真实资源未确认就保根并封新接入。正常Window.Close晚于真实Unbind Drained；Dispatcher/OS先退出按原Unknown/保根路径，不能以父窗销毁当源/native归还。根外Close预算与UI Unbind剩余预算分别显式给出，不让UI worker等待自身。UI语言切换调用同binding.SetResourcesAsync完整快照，缺键/错schema/取消保持旧完整资源，不刷新像素、不改变mosaic输入/权限，mosaic自身文本仍由D.6原桥管理。

本轮兼容验收设计仅增量复用D.6双Host：核预绑定Lifetime=null或schema不完整在Reserve/Dispatcher前拒绝、正确同Owner装配成功才交Display、跨Control/root混用拒绝；同提交原Task幂等；原Acquire/Confirm/Return闩锁晚到且Unbind有限超时仍保根，解除同闩锁后只归还一次；A关控件不Dispose B/session/服务；缺可见回执不返回Presented=true。没有重审既有双STA全部场景或重算向量。本轮原会话完成这项宿主消费兼容自审后，**完整批准范围内部设计结论保持，无新增未闭合的软件设计项**；实际公开程序集消费编译、显示桥/真实WPF、native可见观察、原Task排空、性能及产品/现场资格门仍未执行，不以本文同步升级准备状态。

#### D.5.2 显示副本公开源、整图Clear与同session续显（0.5.8-prep 窄同步）

唯一上游依据为 [`viewport` 0.3.5-prep §15.2.2.1 公开CPU发布源](../viewport/DEVELOPMENT-GUIDE.md#15221-公开cpu发布源生产者与预装配bc-u1)、[§4.7.1 空Update](../viewport/DEVELOPMENT-GUIDE.md#471-合法空更新真实清屏与同session继续呈现bc-u3)及[§4.5.1 对象选择](../viewport/DEVELOPMENT-GUIDE.md#451-稳定对象id只读选择高亮与聚焦bc-u2)；复制发布准确签名引用 [image-frame §4.3 Module API Contract v0.1：进程内 CopyStorage/Lease](../image-frame/DEVELOPMENT-GUIDE.md)。上游公开CPU适配包Assembly Contract v0.1与`EmptyUpdate/1`是目标规格，未实现/未消费编译。D.5公开窄桥签名保持，D.5.1的Lifetime/Presentation/资源/Root/Close不重新设计。

**实际采用与权限边界。** 每个mosaic主视图/独立对照视图使用由宿主专门分配给本Display的session/control；没有其它Owner的Sources/Layers混在该Context。Clear是清空这个专有视图的所有图像与叠加，不能用于共享宿主图像或其它Owner层。最终Unbind/关闭仍沿D.5.1；本节只补保持接纳的空Update，不能Unbind后再Present复活session。现有Pick按common点查全部来源贡献、树选FOV定位及原图对照不承诺按ObjectId高亮，故**不调用**`SelectOverlayObjectCommand`、不新增选择层/事件/功能。若今后批准该功能，唯一入口为`session.ApplyAsync(new SelectOverlayObjectCommand(new OverlayObjectSelectionRequest(operationId,contextRevision,generation,target,focus)),ct)`；target须完整`OverlayObjectRef(SourceId,SourceRevision,CoordinateRevision,GeometryRevision,LayerId,ObjectId)`，不能将FovId/树行/像素中心冒充对象键；本轮只读其语义并确定不采用，不改Pick或贡献查询。

**源预装配只执行一次。** 宿主发布Owner显式提供已经由image-frame `FrameServiceFactory.Create(ResourceLimits,IManagedLayoutValidator,TimeProvider,IFrameEventSink?)`成功创建的 `Asun.Modules.ImageFrame.Resources.IFrameService`、其原ServiceEpoch，以及在原ResourceLimits.Consumers中预登记的独立publish/read ConsumerId。本桥借用该服务，不自动创建/Close它。D.5.1的root建立后、session Create前调用 `Asun.UI.Viewports.ImageFrame.ViewportImageFrameSourceFactory.Create(frameService,root,new ViewportImageFrameSourceOptions(readConsumerId,maxBindings,maxMetadataBytes))`；检查Succeeded/Value非null并强持返回的 `IViewportImageFrameSource`。D.5.1的ViewportOptions固定 `Frames=sourcePorts.Frames`，二维显示副本的局部pixel identity使用 `Coordinates=sourcePorts.Coordinates`；所有后续帧都Register到这**同一**producer，不替换已冻结Options.Frames/Coordinates、不逐帧重建factory/session/root。

工厂身份是原service实例+ServiceEpoch、原root实例和readConsumerId；逐帧登记身份另为BindingId及完整`SourceId+SourceRevision+CoordinateRevision+DecodeRevision`。FrameKey始终是image-frame的`FrameKey(Guid Id,ulong Revision)`，不强转为viewport长整数token、不用mosaic FrameId替它。发布Owner在预留槽内签发新的唯一FrameKey/Publish RequestId、有限BindingId、SourceRevision/DecodeRevision/正CoordinateRevision，保存它们与本次manifest完整引用/TileKey/mosaic generation/原FrameRef/贡献支持的不可变映射，字符串在上游长度限额内；epoch或token冲突拒绝，不能减基址/取latest。不同Host的工厂、service/root和帧键不可交叉使用，MaxBindings按旧新副本与未决清理并存预留，满额在复制/发布前拒绝。

**Pixels→认可生产者的完整处理。** 本方原Present Task开工前预留task、pixel复制、有效域行段、发布storage、读取借用、旧新代并存及UI/native预算。宿主在该Task内给image-frame的 `IFrameInputRows.CopyRow(int planeIndex,int y,Span<byte> destination)` 实现提供当前mosaic lease的精确只读Pixels，只处理plane0与合法y、destination长度恰为有效RowBytes；checked原stride/容量，不复制padding，不取第二个mosaic lease。`CopyPublishRequest(Guid requestId,string consumerId,FrameDescriptor descriptor,IFrameInputRows source,TimeSpan timeout)`包含这些冻结值，以 `frameService.PublishCopyAsync(request,ct)` 的原ValueTask一次AsTask登记进宿主原资源根；发布Owner保存完整receipt与原Source强引用，至 `Receipt.OperationResourcesReleased=true`且真实复制工作退出前不得释放输入mosaic tile。取消/观察超时后只查 `frameService.QueryOperation(原ServiceEpoch,原RequestId)`、保原Task，不用新ID重Publish，不拿NotFound/epoch改变当“未执行”。晚到成功副本不继续采用，仍由原发布Owner收回其key；未知发布资源继续占原槽。

FrameDescriptor精确来自该显示副本：Layout.Width/Height为有限tile FrameRef实际尺寸（checked可表示int），一个Interleaved plane、OffsetBytes=0、StrideBytes=RowBytes=Width*Channels*BytesPerSample、AccessibleBytes=DeclaredBufferBytes=RowBytes*Height、明确ByteOrder；不沿用带padding输入容量。Layout.Domain=Full只表存储矩形，Metadata恰一个、Scale=1/Bias=0、明确unit/channel解释；Metadata.ValidDomain是D.3全部合法贡献行段按TileKey/Grid投回本tile局部整数行后的并集（输出NoData段不加入），规范化为Full/Empty/RowSegments，不能以包围框代mask；无效原像素即使内部为0也不成Full。FrameDescriptor.SourceId/SourceRevision与后续ImageDescriptor逐值一致，CoordinateReference=显式唯一PixelSpace，其范围/单位是**该副本局部整数中心pixel**，与common物理坐标有区别。PixelSpace与原TileKey/Grid、crop/LOD中心映射保存到本桥已有坐标映射中；factory.Coordinates仅同PixelSpace identity，不伪装成物理标定。Display Pick按当前映射把局部中心投回D.3共同坐标，之后仍由mosaic原manifest求贡献。

该公开生产者首版只接Gray8/Gray16/RGB8：UInt8×1/UInt16×1/UInt8×3 Interleaved，原bytes/有效域保真，小端UInt16且RGB顺序须有宿主已冻结语义；未知RGB顺序、BigEndian、Int16/Float32、Planar或多plane在发布/登记前返回本方MZ-026/003，不能量化、换通道或将typed buffer当内置payload。D.3的原值/几何能力不因显示适配限制改变，受阻只影响此显示路线；不悄悄换backend或改原Frame/hash。无源统计时只允许宿主明确手动LUT，例如Gray8的0..255、Gray16的0..65535是格式显示范围而非实测extrema；RGB按明确颜色路线。没有明确显示政策则拒绝，不扫描整板/猜自动LUT。

发布成功须同时核 `PublishResult.Frame!=null`、`Receipt.ServiceEpoch/RequestId`为本原操作、`Phase=Completed/Error=None/OperationResourcesReleased=true`；OperationResourcesReleased只表示复制调用临时资源已归还，注册表storage仍持有。然后调用 `sourcePorts.Register(new ViewportPublishedFrameBinding(bindingId,published.Frame,imageDescriptor,ImmutableArray.Create(0),pixelSpace))`，检查Succeeded。ImageSourceDescriptor完整字段按viewport§4.2/15.2.2.1冻结：同source/revision与正coordinate token、实际W/H/通道/bit/signed=false、CenterInteger、明确Channels、完整Validity、唯一level0原尺寸/identity层中心映射、有限正tile/MaxDecodedTileBytes、DecodeRevision与Statistics（无原统计则null）；实际PixelLayout由源adapter读取返回，不加不存在的descriptor字段。全部与原Frame/Metadata/domain逐项相符。Validity.FullBoundaryValid仅整个半开边界有效时true，孔洞用原域引用；不把原源引用字符串当mask数据。同BindingId同完整内容幂等，同ID异内容拒绝；Register同步无读帧，但真实Read仍核原epoch/key/布局/域/权限与预算，Register成功不证明未发布key可读。

首次Register/Bind都成功才 `session.AttachAsync(完整Context,ct)` **一次**。每个非首次Present先Register新副本entry，再 `session.UpdateAsync(new ViewportUpdate(baseContextRevision,完整新Context),ct)`，原Task立即保存；replacement revision=checked(base+1)、同当前合法Authorization/Language/ApiVersion、当前View与完整Sources/Layers，不使用增量补丁。采用图块局部Sources，Role按D.5主/对照固定，未有原曝光时不造Timing；source/viewport代与mosaic显示generation分别保存/逐项核，不把它们数值相等当同身份。检查原Update与同代实际Commit/VisibleConfirmed才Present成功；旧base/撤权/预算/清理未知拒绝新采用。没有当前有效entry时保NoData/明确显示失败，不拿上次图作当前成功。

旧副本替换后，宿主观察同旧代原Revoke/借用Return/工作退出事实；只有旧Context引用解除、该entry所有Read原Task/未知operation/local scope与lease真实Returned，才 `sourcePorts.Remove(oldBindingId)`。015/Unknown保entry及metadata额度，不强删；Remove成功只解除adapter登记，不证明source池退款。之后由**原发布Owner**调用 `frameService.RetireAsync(oldFrameKey,remainingObservationTimeout)`，保存原ValueTask一次AsTask/回执，未知沿同key有限观察、保storage原根，不Close共享服务/不Retire其它Host的key。替换完成但清理未确认时保旧新两份预算，不能让无界换图超过MaxBindings/源frames/bytes。

**整图Clear的唯一实际入口。** 本Display已经完成一次Attach时，保存当前精确snapshot/baseContextRevision、当前Authorization/Language/View，以 `new ViewportContext(Array.Empty<SourceBinding>(),Array.Empty<OverlayLayer>(),currentAuthorization,currentLanguage,new ApiVersion(0,1),checked(baseRevision+1),currentView with { Profile=null })` 创建完整空替换；通过 `session.UpdateAsync(new ViewportUpdate(baseRevision,replacement),ct)` 保存原 `Task<ViewportResult<UpdateReceipt>>`。不调用并不存在的IViewportSession.ClearAsync、不以Source.Count=0/属性赋null替真实Clear，不在外层另发一遍Revoke。先关闭本桥旧显示准入、封旧代Pick与手势；空Update内部按上游原Owner逐项Revoke旧presentation/backend/presenter→等旧Submit/Acquire/Confirm/Dispatcher/CPU实际退出→同ReturnId归还源，再提交同新代空BackendScene并实际确认空画面。空场景不Acquire旧/新源；自己的空Presenter/UI基线仍可存活，不要求整个session/root清零或等待清理worker自身。未首次Attach的Display尚未接受来源，Clear只确认本桥无在途副本/借用且Bind空安装无源；不声称“旧图已真实清屏”，任何已有或未知Attach都走同原Attach/清理记录，不能再Attach覆盖它。

Clear正常完成必须核原Update Succeeded/值非null、`session.GetSnapshot().State=Empty`，以及同新ContextRevision/generation的 `UpdateReceipt.EmptyTransition`（或后来 `session.GetSnapshot().EmptyTransition`）：`PreviousPresentationsRevoked`、`PreviousSourceBorrowsReturned`、`PreviousWorkQuiesced`全true，`PreviousCleanup.State=Drained`，`BlankPresentation!=null/VisibleConfirmed=true`且是同本次空scene回执。原UI客户端被遮挡/不可读或迟到时不给确认，不伪造空画面；当前session空转移字段不能拿历史Clear证明新的清除。图像已经清屏与原storage退休分别记录，后者仍沿上段Remove/Retire；源borrow Returned不等StorageReleased，Retire未知继续保资源账与原root，不降低Cleanup为Drained。

本方 `ClearAsync(CancellationToken)` 的ValueTask正常完成**只在上述Clear确认及本次桥输入/临时工作不再使用后**；有限deadline从原UiBudget/Options取单调剩余额度，没有新public字段。原Empty Update待定/失败、空画面未确认则本方Clear报原取消/TimeoutException或InvalidOperationException失败，记录原VIEWPORT错误/实际Cleanup到原宿主根及mosaic诊断（不是因void无回执就默默成功）。观察结束后原Clear Update/Blank Commit/旧Revoke/Return及副本storage责任继续强持；下一Present在原同session空转移全部确认前拒绝，不通过新Attach/Bind/Retry/new session逃账。有限恢复只观察同原Task与GetSnapshot.EmptyTransition，不重新发空Update/归还；旧base Clear若接纳前拒绝则没有已开始清理，可以由宿主依据新snapshot明确重新请求新的Clear，不能悄悄清掉已换入的新图。关闭/撤权时安全空替换沿上游规则使用当前撤权快照、保持原Language/View且Profile=null，不取得新Read权。

Clear确认为Empty后，下一Present Register新key→`UpdateAsync(new ViewportUpdate(emptyContextRevision,完整非空Context且revision=empty+1),ct)`→核当前授权/预算→上游同Owner撤空Presenter并实际呈现；**不再Attach，不重Bind，不替换Frames**。Clear与换图接纳串行，相同空请求重放只观察同原Update Task、代次一次；其它并发非空请求Busy/旧代拒绝，不在Clear过程读新源。最终Unbind/Session/Root有限关闭及双Host隔离保持D.5.1，未知清理仍可沿原Owner关停路径收敛，不等空转移成功才启动已armed关闭。

本轮有限反例自审只覆盖实际增量：（1）私有buffer/未Publish成功descriptor或跨epoch/服务/register键拒绝内置payload，准确Register不替换冻结Frames；（2）PublishCopy晚到或Source.CopyRow闩锁未退出不返mosaic tile，原Task退出且OperationResourcesReleased后恰好归还，晚成功副本只Retire自己key；（3）旧lease/旧工作/旧Revoke任一未确认时Clear不正常完成、三个Previous不造true，新Present无Read；（4）旧scope全归还但BlankPresentation=false仍Clear失败，解除原真实确认条件后观察同EmptyTransition，不重Clear；（5）Empty确认后后续Update成功，Attach计数恒1、Frames引用不变，空Presenter先归还，旧entry Remove/Retire不冒source storage退款；（6）A清屏/移登记/退休不改B来源与service；预算不足、旧base或跨代回执均不能采用。验证计划复用D.6双Host/原闩锁，不生成新测试工程/报告，不重新审核算法/三语/Root/Close或复算向量。

2026-10-12 / 0.5.8-prep：原会话按上游§20.5的实际影响完成本节源生产者与EmptyUpdate消费内容自审，D.5/D.5.1旧泛指复制源/反复Attach/仅Revoke即Clear措辞已局部修正。**原完整批准范围内部设计闭合结论保持，本轮无未闭合设计欠项**；真实image-frame/viewport公开程序集消费编译、源生产者/发布/退休运行、真实空画面可见/晚到归还、WPF/native、性能及产品/现场门均未执行，状态不提升。

### D.6 三语文本、操作与两个 STA 宿主验收

语言桥以localization实际 `ILocalizationService.Resolve(scope,ResolveRequest)` 解析PlainText键、`Subscribe(scope,surface)`/`Detach(token)`跟随宿主已建立scope；换语言只由宿主 `RequestSwitchAsync` 发起。IMosaicTextPort保存同scope/同revision的不可变完整文本快照，Changed在目标Dispatcher通知；旧revision、部分解析失败保旧完整快照并显示宿主语言失败原因，不一半英文一半中文，不动CultureInfo.CurrentCulture/全局Resources。单位数值按宿主scope格式投影，几何/摘要不随语言改变。语言桥及viewport桥有各自原root，MosaicControl不替它们创建第二事实Owner。

下面是额外文本的唯一初版语义；§11.1既有9键复用，不重复。资源实现按表逐行落三语，Key前缀统一mosaic；参数/枚举显示只使用下面明确投影，不显示未本地化的反射属性。动态身份、数值/单位与MZ代码保持机器事实，禁止将它们当整句错误正文。

| Key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title | 大图拼接 | 大圖拼接 | Mosaic |
| Run | 开始拼接 | 開始拼接 | Build mosaic |
| Solve | 求解标定候选 | 求解標定候選 | Solve calibration candidate |
| Validate | 验证候选 | 驗證候選 | Validate candidate |
| Cancel | 取消当前任务 | 取消目前工作 | Cancel current task |
| Pause | 暂停显示 | 暫停顯示 | Pause display |
| Resume | 继续显示 | 繼續顯示 | Resume display |
| Refresh | 重新请求图块 | 重新請求圖塊 | Request tile again |
| Recover | 查询释放状态 | 查詢釋放狀態 | Check resource release |
| Original | 原图 | 原圖 | Source image |
| Derived | 派生图 | 衍生影像 | Derived image |
| Compare | 接缝两侧对照 | 接縫兩側對照 | Compare both sides |
| Sources | 图像来源 | 影像來源 | Image sources |
| Details | 来源与用途 | 來源與用途 | Sources and purpose |
| Resources | 资源占用 | 資源用量 | Resource use |
| InputMissing | 未提供输入 | 未提供輸入 | Input not provided |
| Historical | 历史结果 | 歷史結果 | Historical result |
| Candidate | 标定候选，尚未资格化 | 標定候選，尚未取得資格 | Calibration candidate, not qualified |
| Validated | 独立验证通过，尚未资格化 | 獨立驗證通過，尚未取得資格 | Independent validation passed, not qualified |
| Published | 标定内容已发布，尚未激活 | 標定內容已發布，尚未啟用 | Calibration content published, not activated |
| Partial | 结果不完整 | 結果不完整 | Incomplete result |
| NotApplicable | 不适用 | 不適用 | Not applicable |
| NotEvaluated | 未验证 | 未驗證 | Not evaluated |
| NoPermission | 无操作权限 | 無操作權限 | Action not permitted |
| Working | 处理中 | 處理中 | Processing |
| Draining | 正在释放资源 | 正在釋放資源 | Releasing resources |
| Released | 资源已释放 | 資源已釋放 | Resources released |
| Completed | 已完成 | 已完成 | Completed |
| Cancelled | 已取消 | 已取消 | Cancelled |
| TimedOut | 已超时 | 已逾時 | Timed out |
| Failed | 任务失败 | 工作失敗 | Task failed |
| Unknown | 结果未确认 | 結果未確認 | Outcome unconfirmed |
| Eligible | 用途已获资格 | 用途已取得資格 | Purpose qualified |
| Rejected | 用途受阻 | 用途受阻 | Purpose blocked |
| Display | 查看 | 檢視 | Display |
| Detection | 检测 | 檢測 | Detection |
| Measurement | 测量 | 量測 | Measurement |
| Diagnostic | 几何诊断 | 幾何診斷 | Geometry diagnostic |
| Profile | 参数版本 | 參數版本 | Profile revision |
| Method | 处理方法 | 處理方法 | Processing method |
| Purpose | 用途 | 用途 | Purpose |
| Identity | 来源标识 | 來源識別碼 | Source identity |
| Revision | 修订 | 修訂 | Revision |
| Geometry | 几何状态 | 幾何狀態 | Geometry status |
| Coverage | 覆盖状态 | 覆蓋狀態 | Coverage status |
| Residual | 独立残差 | 獨立殘差 | Independent residual |
| Support | 有效支持 | 有效支持 | Valid support |
| Lod | 显示层级 | 顯示層級 | Display level |
| Memory | 当前内存 | 目前記憶體 | Current memory |
| Pending | 待释放操作 | 待釋放操作 | Pending release |
| None | 无融合 | 無融合 | No blending |
| Stacking | 按来源叠放 | 依來源疊放 | Source stacking |
| PriorOnly | 标定与运动先验 | 標定與運動先驗 | Calibration and motion prior |
| PairBundle | 离线图像配准 | 離線影像配準 | Offline image registration |
| CompleteCoverage | 覆盖完整 | 覆蓋完整 | Complete coverage |
| EmptyCoverage | 无有效覆盖 | 無有效覆蓋 | No valid coverage |
| Uncalibrated | 未标定，仅供查看 | 未標定，僅供檢視 | Uncalibrated, display only |
| PauseTip | 停止新显示请求，检测继续 | 停止新顯示請求，檢測繼續 | Stop new display requests; detection continues |
| CancelTip | 只取消本控件发起的任务，等待资源释放 | 只取消本控制項發起的工作，等待資源釋放 | Cancel this control's task and wait for resource release |
| RecoverTip | 查询原任务，不重新执行 | 查詢原工作，不重新執行 | Query the original task without rerunning it |
| PublishTip | 只发布内容，不授予资格或激活 | 只發布內容，不授予資格或啟用 | Publish content without qualification or activation |

MZ错误正文资源按稳定号码定位；FieldPath/SourceIds/DiagnosticIds以可复制技术详情附在本地化正文之后。恢复按钮只在§8.2允许动作内提供，不能把以下一句正文当完整恢复策略。宿主权限ReasonKey必须能由同scope解析，否则以NoPermission显示、原原因码保诊断，不显示异常Message或未翻译键。

| Key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Error001 | 请求不完整或参数无效 | 請求不完整或參數無效 | Incomplete request or invalid parameters |
| Error002 | 图像来源冲突 | 影像來源衝突 | Image source conflict |
| Error003 | 图像布局或有效域无效 | 影像配置或有效範圍無效 | Invalid image layout or valid region |
| Error004 | 坐标或校正来源不匹配 | 座標或校正來源不符 | Coordinate or calibration source mismatch |
| Error005 | 缺少必需图像 | 缺少必要影像 | Required image missing |
| Error006 | 缺少有效重叠证据 | 缺少有效重疊證據 | Valid overlap evidence missing |
| Error007 | 图像对应不充分或不唯一 | 影像對應不足或不唯一 | Insufficient or ambiguous image correspondences |
| Error008 | 变换退化或不可逆 | 變換退化或無法反算 | Degenerate or noninvertible transform |
| Error009 | 独立验证缺失或未通过 | 獨立驗證缺少或未通過 | Independent validation missing or failed |
| Error010 | 请求超过资源预算 | 請求超過資源預算 | Request exceeds resource budget |
| Error011 | 图像适配处理失败 | 影像轉接處理失敗 | Image adapter processing failed |
| Error012 | 图像处理仍占用资源 | 影像處理仍占用資源 | Image processing still holds resources |
| Error013 | 结果修订已过期 | 結果修訂已過期 | Result revision expired |
| Error014 | 派生缓存校验失败 | 衍生快取驗證失敗 | Derived cache validation failed |
| Error015 | 来源权限范围不匹配 | 來源權限範圍不符 | Source permission scope mismatch |
| Error016 | 已请求取消，正在释放资源 | 已要求取消，正在釋放資源 | Cancellation requested; releasing resources |
| Error017 | 结果未获当前用途资格 | 結果未取得目前用途資格 | Result not qualified for this purpose |
| Error018 | 图像处理结果未确认 | 影像處理結果未確認 | Image processing outcome unconfirmed |
| Error019 | 未提供图像或采集计划 | 未提供影像或擷取計畫 | Images and capture plan not provided |
| Error020 | 缺少曝光关联实际位置 | 缺少曝光關聯實際位置 | Exposure-linked actual position missing |
| Error021 | 运动资格证据不完整 | 運動資格證據不完整 | Incomplete motion qualification evidence |
| Error022 | 运动或图像残差超限 | 運動或影像殘差超限 | Motion or image residual exceeds limit |
| Error023 | 运动接近方向不匹配 | 運動接近方向不符 | Motion approach direction mismatch |
| Error024 | 曝光与反馈时间不匹配 | 曝光與回授時間不符 | Exposure and feedback timing mismatch |
| Error025 | 输入超出平面模型范围 | 輸入超出平面模型範圍 | Input exceeds planar model range |
| Error026 | 当前方法尚不支持 | 目前方法尚未支援 | Method not supported |
| Error027 | 位置或条件超出标定范围 | 位置或條件超出標定範圍 | Position or conditions outside calibration range |
| Error028 | 操作标识与原请求冲突 | 操作識別碼與原請求衝突 | Operation identity conflicts with original request |
| Error029 | 标定发布回执未确认 | 標定發布回執未確認 | Calibration publication receipt unconfirmed |
| Error030 | 缺少有效规划快照 | 缺少有效規劃快照 | Valid planning snapshot missing |
| Error031 | 等待已结束，原操作仍未释放 | 等待已結束，原操作仍未釋放 | Wait ended; original operation has not released resources |

初版只读PropertyGrid展示Profile/Method/Purpose/Identity/Revision/Geometry/Coverage/Residual/Support/Lod/Memory/Pending这12项投影；标签与枚举均来自上述资源，NotProvided残差不填0。其它参数只由宿主高级参数页按其Owner指导展示；不把参数编辑器漏做为本模块职责。Tooltip按限制→影响→恢复动作排列。默认焦点/键盘和1920×1080唯一viewport沿§11.1；双侧对照收起后仍保来源、用途、空洞与未知状态，英文长度不通过省略关键动作解决。

**双STA fixture规划**：Wpf.Tests Exe内启动两个独立STA线程/Dispatcher，各自生成ViewHost与CalibrationHost、服务epoch/资源root、固定时钟/端口及自己的文本scope，创建真实MosaicControl和自己的ViewportControl（或只证明软件协议的明确FakeDisplayPort）。ViewHost Show合成含两个相交来源、一个Skip和一个Missing的result→原图/派生/对照/点选→断言来源、NoData/DisplayOnly可见→暂停只停新tile→关闭。CalibrationHost显式输入已分区groups→Solve→Validate→Publish→断言Candidate/Passed/Published三者不激活、不放行→取消与关闭。假显示用例不冒充viewport/WPF真正呈现测试。

分别注入：A的tile在B已换generation后迟到；Present原Task闩锁未开；lease.Dispose闩锁未开；语言Changed旧revision/错误Dispatcher；无权限/请求空；Dispatcher关停；PublishUnknown；未退出Query。每例核原Task/各根强引用、源lease不提前返还、错误作用域不读、不Dispose另一个service/viewport、相同binding重复幂等/冲突拒绝、解除原闩锁后同root有限恢复恰好归还一次。测试观察超时保原失败exit且继续观察另Host，未确认资源保持原根至进程寿命，不能kill进程当释放证据。真实UI仅用固定1920×1080验证viewport，不改显示设置、不跑其它分辨率矩阵；三语/宿主当前DPI、Tab/Enter/Escape、UIA名称、长文字、主题/图标/视觉品质与操作链分别验。首可见tile、随机导航、UI线程阻塞、copybytes、持有/迟到lease峰值与取消到真实释放沿§14.1；无客户阈值为NotEvaluated。

### D.7 自动参数建议与未批准美缝的精确边界

参数自动化只输出独立建议，不改输入、Profile/资产、配方、生产网格或用途资格。本版有两类可执行软件建议：tile/并发预算建议、缺乏拟合/留出覆盖的补采建议。没有证书/速度/精度/吞吐值时不估“最佳物理参数”；无特征FOV不建议降低支持数来匹配，更不以AI推位姿。原运行请求与建议分开保存，宿主明确采用后以新输入摘要/新operation/attempt重新Validate/Plan。

```csharp
// Core中的独立纯规划辅助面；不修改A.1服务/DTO，不授准入。
namespace Asun.Modules.Mosaic;
public enum MosaicAdviceStatus { Suggested=0, NotEvaluated=1, Rejected=2 }
public record AreaMemoryBound(ValueRef Evidence, long PerCallFixedBytes,
    long DecodePeakBytes, long NativeTemporaryBytes, long FixedCacheBytes);
public record MosaicAdviceRequest(MosaicRequest Request,
    IReadOnlyList<uint> CandidateTileCoreSizes, uint MaximumConcurrency,
    AreaMemoryBound? MemoryBound);
public record TileAdvice(uint TileCoreSize, uint Concurrency,
    long EstimatedPeakBytes, ulong EstimatedTileCount);
public record CalibrationSamplingNeed(string CameraId, ConditionId ConditionId,
    CellId CellId, IReadOnlyList<NodeId> Nodes, string ReasonKey);
public record MosaicAdviceResult(MosaicAdviceStatus Status, ContentDigest InputDigest,
    ValueRef? MemoryEvidence, TileAdvice? Tile,
    IReadOnlyList<CalibrationSamplingNeed> SamplingNeeds,
    IReadOnlyList<MosaicError> Errors);
public static class MosaicPlanningAdvisor
{
    public static MosaicAdviceResult Evaluate(MosaicAdviceRequest request);
}
```

输入先沿原Validate的结构/预算规则核，candidate sizes非空、正值、去重后按数值顺序（重复输入为MZ-001，不能静默dedup），MaximumConcurrency正且<=原Profile.MaxConcurrency；仅AreaScan/PriorOnly/nearest的已解析矩阵链。InputDigest沿A.2原runtime根投影，不自创codec；建议MemoryEvidence为经宿主提供、与当前解码/native版本和线程条件相符的实际资源上界证据，不是自动训练结果。MemoryBound四个byte界非负、checked且有实际来源，缺失为NotEvaluated/Tile=null，可仍报告已有快照的补采needs；不能根据OS空闲内存猜无证据界。Evaluate不借帧、不做IO/native、不按当前CPU数猜并发，纯计算CPU/内存受原Budget约束。

候选评估算法固定：对每个T只改变**建议对象**的core尺寸，halo/LOD/相位/原几何/采样政策保持原请求；对规划bounds的每个相交tile算其扩展输出面积a、当前来源及所需窗口最大像素bytes，整数溢出即拒绝。单call下界包含输出core typed bytes、4a的nearest map bytes、a的有效mask与a的来源索引（索引宽度按源数最小可表示uint且checked）、最大单源compact输入bytes；来源贡献按最坏每core像素一行段，依A.2对应record实际可变字段最大编码长度计入，不用平均段数估计省内存。再加MemoryBound.PerCallFixedBytes+DecodePeakBytes+NativeTemporaryBytes，得到W；实例峰值上界=`FixedCacheBytes + c*W + 原Service/宿主已承诺的输出保留上界`。最后一项没有在请求中表达，**本辅助器只建议单次请求：c<=MaximumConcurrency且输出保留上界固定为c个本候选tile的pixel+mask+贡献bytes**；宿主已有其它请求/输出时必须先从可用Budget扣其已预留量再调用，不能把结果当全实例无限共享预算。

枚举c=1..MaximumConcurrency，核峰值<=Budget.MemoryBytes、同时source leases/native handles不超Budget、总tiles<=TileCount、逻辑/解码读取上界<=对应Budget；CPU目标缺实测不判吞吐达标。过滤后按“预计tile数最小→并发最小→预计内存最小→T数值最小”选唯一建议；没有合格候选为Rejected/MZ-010，不能缩halo或改位深。候选枚举/逐tile工作亦累计CPU预算，超限拒绝全部建议、不返回已看过的局部最优。此规则优化请求分块/资源可行性，未证明最快；真正冷热/随机ROI/顺序扫描比较沿§14。

补采needs仅消费快照中的既有camera/condition/cell、节点支持与独立Validation/Qualification：缺任何四角拟合集数/支持则ReasonKey="FitSupportMissing"，缺独立Holdout/用途验证则"HoldoutMissing"，已验证失败则"ValidationFailed"；不为未知范围造新cell、温度区或方向事实。输出按camera/condition/cell稳定ID排序，Nodes是该cell原N00/N10/N01/N11；可以并列多个原因，不能合并事实。mosaic不发运动/采集命令，宿主标定Owner据该needs安排独立遍次/安全采样；失败残差图只给建议，不自动提高阶数或放宽门。

| 建议资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| AdviceCandidate | 参数建议，尚未采用 | 參數建議，尚未採用 | Parameter suggestion, not adopted |
| FitSupportMissing | 拟合采样不足 | 擬合取樣不足 | Insufficient fitting samples |
| HoldoutMissing | 缺少独立留出采样 | 缺少獨立保留取樣 | Independent holdout samples missing |
| ValidationFailed | 独立验证未通过 | 獨立驗證未通過 | Independent validation failed |

**美缝规划不遗漏：** 当前批准执行的None/Stacking已经有D.3全步骤，属于有界原值显示；不会宣传纯色图即“无缝算法通过”。几何缝偏差按资产独立误差门处理；亮度/颜色缝保留真实值、原图对照和来源。Feather、NamedMultiBand、adjust_mosaic_images属未批准显示候选，不是本版待程序员任选的实现。研究可复用DEV-VIS-029 §11.3–11.8固定核/标签/支持归一/全局相位/有限halo/按分量资源及原反例，官方HALCON和固定GitHub源码依据见§17；这些仅帮助未来选择，不能从本版Profile派生不存在的L/核/曝光参数。

若用户后续批准美缝切片，唯一Owner仍为mosaic原会话；须先在本指导增加独立显示Contract（具名方法/revision、核/层数、线性颜色、支持政策、保护/标签、量化、预算与派生身份），用HALCON经cv2完成明确算子等价桥并与None/Stacking在同代表图比较。具体验收必须包括常量/单源、孔洞/孤岛、负相位/奇尺寸、跨tile逐值支持一致、少halo反例、逐值保护覆盖、真实最小缺陷对照、取消迟到资源及峰值；未通过仍只允许原图/Stacking。此**后续范围批准门**不能被算作文档已支持多带，也不阻断当前批准的几何/原值/控件准备。当前没有已批准多带/辐射公开参数合同，不能将研究留成当前实现入口。

### D.8 本轮内容自审、验收断言与精确剩余 Owner

面阵适配/建议测试复用D.2唯一测试工程（纯建议另在Core.Tests相应目录）；UI复用D.5工程，不新增独立过程报告/脚本。下面断言是后续实现必须满足的验收设计，当前**没有执行代码/运行验收**。

| 断言ID | 可判定输入→预期 |
|---|---|
| AREA-01 无纹理/多相机 | 同合法先验下纯色与纹理Frame几何相同，PriorOnly匹配/native拟合调用0；相机A/B各自变换不能互换，NoMotion无feedback不造零反馈 |
| AREA-02 tile/负坐标/边缘 | identity及已知平移/crop取sample floor(u+0.5)；不同分块原值/有效支持/贡献相同；(-0.5)取0、(-0.5001)取-1后依域拒绝，不clamp；LOD不改变Origin |
| AREA-03 mask/stacking | Mask未知/不同源拒绝；相同输出点None冲突、Stacking取固定最高源；保护区无单源完整支持冲突；安全map索引永不越界，内部0不成覆盖 |
| AREA-04 类型/非线性 | byte/uint2/int2/real保原类型；异类型输出/隐式byte截断拒绝；未表达非线性原map拒绝，校正派生Frame精确公开链可消费；不篡改source hash |
| AREA-05 独立性/取消 | PairBundle物理用途拒绝；周期候选>1拒绝；native/MaskRead/Dispose迟到仍持原Task/租约，两Host互不清理；真实归还后同Owner退槽一次 |
| CAL-01 冷原点 | D.4三个点反算得到(10,20)，错号/缺方向证据不能因残差0通过；不把q_cmd填原点；同曝光跨Fit/Holdout拒绝 |
| CAL-02 资格/恢复 | 节点拟合足够但Holdout缺失为NotEvaluated；Passed/Published不激活；PublishUnknown回查原ID，不修改Candidate/hash或原业务失败 |
| ADV-01 有界建议 | 同请求/MemoryBound/候选集输出唯一相同建议，候选次序不影响排序；预算缺证据NotEvaluated，溢出/无可行候选拒绝；原输入/hash/生产参数不变 |
| UI-01..02 双Host | D.6两个独立STA正常链与全部闩锁/权限/语言/关停反例；原Task退出前不返tile，cleanup成功不改原失败；文本键完整且未知/资格可见 |

本版整模块**当前批准范围的可决定软件设计已在唯一指导定位**：面阵Core/线扫Core及只读消费沿已接收规格；面阵Adapter/冷标定原点/自动建议/可选UI与恢复在D.1–D.7补齐。它不是ImplementationSpecificationReady声明。M-V1/M-U1及新增建议辅助面为“指导内容自审完成、运行/集成未准入”，不得机械标ModuleCoreImplementationReady或宣称代码可运行。未批准的PairBundle物理用途、附加补偿、Feather/NamedMultiBand/辐射没有被偷偷扩大范围。

| 精确门 | 唯一责任/需要的证据 | 影响与未执行情况 |
|---|---|---|
| 代码仓库与实现授权 | 用户/代码仓库Owner提供权威仓库/分支或可审计快照与切片授权 | 本轮只修指导，未创建工程/代码/正式测试，未构建或运行 |
| native消费与真实验证 | mosaic原会话按D.2/C.6.4消费编译；ImageLibDotNet公共重载有歧义仅核对应调用 | area/line真实native、数据布局/map、取消、内存/性能/Golden未执行；不做依赖安装/授权审查 |
| FOV局部观测与校正源 | calibration-assets/实际Frame Owner提供精确公开观测、已资格光学/校正派生、原图来源 | 缺此仅阻断真实观测/物理tile；不阻断显式离线组和纯数学 |
| camera行/运动/时钟 | camera-acquisition原producer/Frame Owner、motion-control事实Owner提供真实配置、行映射/曝光、原payload归还与已验证时钟运动 | C.8–C.10拒投影边界保持；未执行LC/LM/LR运行/HIL，未知不补猜 |
| 靶/安装/物理阈值 | 客户标定/计量Owner给证书、安装/板面、速度方向温度域和精度/最小缺陷/吞吐Profile；资格Owner授予用途/激活 | 不从公开资料编造数值；当前无物理/计量/FAT/SAT资格 |
| UI/桥实际接线 | mosaic原会话实现控件；viewport/localization原会话持自己的公开面/资源根，消费宿主Owner做窄桥 | UI指导闭合，实际DevExpress/viewport/localization消费编译、真实WPF/双STA/三语/UIA/视觉/性能均未执行 |
| 产品Contract与耐久提交 | 原Contract/Schema、存储、质量及产品宿主Owner串行采纳/接线 | 不由mosaic写产品事实；导出sink、内容Store和现场正式接收未验 |
| 未批准显示/物理扩展 | 用户决定是否进入新范围；mosaic原会话补唯一新增合同/方法并验证 | 仍不支持Feather/NamedMultiBand/辐射/PairBundle物理用途/基线外补偿；无当前已批准设计欠账被伪装外门 |

本轮自审按正常→拒绝→取消/迟到→关闭/恢复→两个消费者→用途/生产门走查，复用已有§17研究、A/C公式和向量而不重算。结构校验只证明文档结构与引用，不替代以上任何代码、HALCON、WPF、性能、硬件或现场验收；本原会话完成收口后停止，不等待总控内容审核。
