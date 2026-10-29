# 图像畸变校正独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, S1`

- 模块键：`image-rectification`
- 文档 ID：`IM-022`（现有来源：`PKG-016`）
- 版本：`0.2.1-prep`；模块契约：`0.2.0`（公开DTO与canonical/2不变，尚未实施）
- 状态：逐片接收；C1/C2/S1 为 `ModuleCoreImplementationReady`（仅规格准备）；C6 内容已接收，仍为 `PreparationIncomplete/NotReady`；C3/C4/C5 公开装配指导内容限定接收，真实 native/Store 与运行资格仍为 `PreparationIncomplete/NotReady`
- 日期：2026-10-11（全部批准范围的软件设计与文档准备收口，见§19.3；未实施）
- 技术基线：C# / .NET 10；模块核心无 UI；视觉适配通过 `ImageLibDotNet` 公共边界使用 HALCON 26.05
- 规划消费者：识别、定位、拼接、计量（本指导以独立视觉工具作为示例消费者）；全部批准范围可决定软件设计已闭合，文档准备结论见§19.3，未授整模块代码或运行资格
- 模块级设计评审态：`DesignReview`（方案可评审）。§19.3「全部批准范围的文档准备结论」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本文是本模块的唯一实施指导。模块契约 0.2.0 由 §4、§6、§10 和附录 A 共同定义，公开类型均位于 `Asun.Modules.ImageRectification`（WPF 控件为子命名空间 `.Wpf`）。平台 Contract/Schema 映射是产品接入的另门，不阻断模块内 Core、模拟器及端口规格。本文规划完整图像、点、轮廓、显式窗口、缓存和可选 WPF 能力；首片只限定实施顺序。主控已逐项接收 C1/C2 的 DEV-GOV-010 §3.1 六项规格，两片为 `ModuleCoreImplementationReady`，仅表示规格准备。S1 的 DEV-GOV-010 §3.1 六项文档规格已由主控内容回读接收，为 `ModuleCoreImplementationReady`（仅规格准备），见 §19.2。C6 可选控件指导内容已接收，真实 WPF/产品资格未关闭，仍为 `PreparationIncomplete/NotReady`；C3/C4/C5 公开 factory/options/Session 及确定 wrapper 装配指导内容限定接收，真实 native/Store 与运行资格仍为 `PreparationIncomplete/NotReady`，窗口及产品门不提升。逐片结论见 §19.1/19.2，不表示代码、HALCON、标准件、性能、现场或生产验收通过。

## 1. 目的和边界

### 1.1 负责的能力

模块把带有明确相机/传感配置和标定资产的图像坐标，转换为无畸变目标坐标。核心能力包括：

1. 校验帧布局、来源修订、标定资产闭包和目标输出布局。
2. 按资产和布局生成、验证并缓存畸变映射。
3. 对整幅图像执行受控重采样；对少量点、点集和 XLD 轮廓提供不生成整图的路径。
4. 传播输入有效域、插值支撑域、输出有效域和坐标换基说明。
5. 返回可回放的输入快照、算法/适配器版本、映射身份、质量元数据和明确的失败原因。
6. 支持同步调用和异步取消/超时调用；在 native 工作真实结束后排空并释放资源。

### 1.2 禁止的能力

模块不负责标定采样和资格决定（由 `PKG-015`/`DEV-MET-030` 负责），不负责板姿态注册、目标关联、拼接拓扑、工艺解释、质量判定、放行、报告提交、设备动作、权限审批或业务数据库。它不把“校正成功”解释成测量合格，也不把低重投影误差解释成物理精度合格。

核心不得引用产品 Shell、ViewModel、私有数据库表、工单/配方类型、设备 SDK、隐藏窗口初始化或全局可变“当前标定”。显示镜像、屏幕缩放和编辑焦点不进入物理映射；三维高度、透视整平、平场和颜色校准不由本模块隐式完成。

### 1.3 本模块实现文件绑定

首个纯 Core 切片绑定仓库相对路径 `src/Modules/image-rectification/Asun.Modules.ImageRectification.Core/Asun.Modules.ImageRectification.Core.csproj`、测试工程 `tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj`，根命名空间固定为 `Asun.Modules.ImageRectification`。工程尚未创建；本指导只允许该 Core 与测试工程路径写入。HALCON/AsunImage 适配器、WPF、宿主集成和发布配置须另行准入。禁止修改其他模块、产品项目、AsunImage 内部或只读参考快照。

本首片只覆盖纯托管的请求/布局/坐标值校验、点和轮廓的坐标约定换基、冻结输入、预算和错误构造及契约测试。它不求解径向畸变，不把换基结果称作校正结果，不创建 HALCON map、不执行重采样、不持有运行期 lease。后续切片完成点/XLD 后端、整图/显式目标窗口、缓存和 WPF；整模块能力没有因首片边界缩减。各工程和准入见 §19。

### 1.4 独立交付形态

发布单元由以下部分组成：

| 单元 | 内容 | 依赖边界 |
|---|---|---|
| `Rectification.Core` | 参数校验、请求快照、状态、坐标/域语义、缓存键、结果和错误 | 只依赖公共契约、取消、诊断和帧租约接口 |
| `Rectification.AsunImage` | HALCON 26.05 适配、原生对象租约、映射创建/执行 | 只引用已安装的 `ImageLibDotNet` 公共类型；不向上泄漏 `HObject` |
| `Rectification.Wpf`（可选） | 网格/前后对比/域和失败原因投影 | 引用 Core 和宿主提供的语言、主题、帧投影；不执行另一套算法 |
| `Rectification.Adapters`（可选） | CalibrationAsset、Frame、存储或回放差异适配 | 端口化；无产品私有类型进入 Core |

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ImageRectification.Core`、`Asun.Modules.ImageRectification.AsunImage`、`Asun.Modules.ImageRectification.Native` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.ImageRectification.Wpf` 可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1.3 首片（纯托管的请求/布局/坐标值校验与换基）是这条门禁的天然验证面。

**Blazor/Web 宿主中的坐标校正查询**：Web 端最常见的诉求是"把屏幕上的点换算到校正后目标坐标"。本模块对此提供**不需要整图重采样**的路径，约束：
- 点/点集/XLD 的坐标换基走 Core 的纯托管路径（或后续切片的少量点后端），可在 Blazor Server 宿主中直接调用，不创建 HALCON map、不做整图重采样
- 整幅图像的校正结果由服务端按 tile 粒度发布，浏览器只渲染标记与叠加层，不在浏览器端重算畸变映射
- 映射身份（资产修订、相机/传感器配置修订、输出布局）必须随结果一起投影到浏览器；资产变更后必须重新解析，旧映射不得静默复用

**AI 推理 Tiling 适配**：本模块是 `ai-inference` 分块推理的**几何前置于校路**，但本模块不参与分块编排。适配约束：
- 推理 tile 的坐标逆变换由 `coordinate-geometry` 负责，**本模块不与之争抢逆变换 Owner**；本模块的职责是把"输入图坐标 ↔ 目标坐标"这一段定死，供 `coordinate-geometry` 组合使用
- 校正（重采样）必须在推理**之前**完成并发布为派生平面，推理侧不再对 tile 做隐式去畸变，否则同一像素在两段链路得到不同几何
- 分块边界的插值支撑域（§1.1 第 4 项）不足由本模块在发布时如实标注，不在推理侧补边；补边会改变有效域与坐标语义

**HALCON 备选交叉验证适用性**：本模块是 2D 视觉链中双跑 CI 的**几何语义落点**，且是本链中"映射实现差异最容易被误读为精度差异"的一环。约束：
- 径向畸变模型（k1/k2/k3、中心、比例）、映射生成与重采样在 HALCON 路线与一条纯托管参照路线上按**同一 Golden 数据集**双跑：映射点、点集换基结果、重投影误差、有效域/支撑域传播逐项比对，差值超容差即 CI 失败并产出差异报告
- **已知的必然差异，不得抹平**：HALCON 的 `gen_radial_distortion_map`/`map_image`/`change_radial_distortion_points` 使用其自身的插值核与量化，托管参照不可能逐位复现插值结果。因此**双跑只对"模型与坐标语义"设门禁**（点集换基、畸变模型求值、映射身份、域传播），**不对重采样像素值设容差门禁**；像素级差异登记为诊断并标注"插值实现差异"。**第三方 oracle 覆盖有限**：本仓固定 OpenCV 快照（commit `a0cda081f8d769f40ab2f4904738b4787b44d07c`）只含 `geometry`/`imgproc`/`stitching`，**不含** `undistort`/`calib3d`（见 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)），故本模块双跑为"HALCON vs 自建托管参照"两路；托管参照须按 §2 已读 HALCON 语义逐项自证，"无第三方 oracle"不得作为放宽容差的理由
- §1.2 的"不把低重投影误差解释成物理精度合格"在双跑中同样成立：双跑一致只证明两路实现自洽，不证明标定资产合格，也不证明现场精度
- 映射缓存键必须包含资产修订与布局修订；双跑 CI 不得因缓存命中而跳过实际映射计算，否则门禁失效
- HALCON 仍是生产路线；托管参照只作交叉验证与降级保险，不作发布依据，不引入 OpenCV 平行生产算法

## 2. 权威依赖和资料边界

实现前按以下顺序读取并绑定：

1. 独立模块准入：[INDEPENDENT-MODULE-ARCHITECTURE.md](../INDEPENDENT-MODULE-ARCHITECTURE.md)。
2. 包来源：[PKG-016_Rectification.md](../../shared-modules/packages/PKG-016_Rectification.md)。
3. 帧资源：[PKG-006_Frames.md](../../shared-modules/packages/PKG-006_Frames.md) 和 `DEV-VIS-022`。
4. 坐标换基：[PKG-007_Coordinates.md#coordinate-math](../../shared-modules/packages/PKG-007_Coordinates.md#coordinate-math)。
5. 标定资格：[PKG-015_Calibration.md](../../shared-modules/packages/PKG-015_Calibration.md) 和 `DEV-MET-030`。
6. 契约/状态/Owner 规则：[DEV-CONTRACT-002](../../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md)、`DEV-GOV-004`、`DEV-GOV-005`。
7. 交接语义：[INTERFACE-MAP.md#foundation-handoffs](../../shared-modules/INTERFACE-MAP.md#foundation-handoffs)。

本模块不新建产品 Schema、业务状态机或提交 Store。本页公开类型是模块自身唯一契约；§3 定义模块资源 Owner，外部帧、标定资格和业务事实保持原 Owner。宿主适配器将外部已批准契约映射为这些不可变值，产品映射未接收只阻断相应产品接入，不要求所有模块 Core 先获得平台 Owner 采纳。

### 2.1 HALCON 和 AsunImage 核对记录

目标运行时为 HALCON 26.05，所有算子通过 `ImageLibDotNet.cv2` 使用。算子存在性已经由项目基线确定，不再作为准入门；语义、参数顺序、坐标、线程和内存限制按本项目手册。仅实际 C# 参数类型、重载或封送有歧义时查公开签名或消费项目编译，不扫描封装内部、不另接 `HOperatorSet` 或 `halcondotnet.dll`。

首发整图路线为面阵径向校正：`cv2.gen_radial_distortion_map` 的 `MapType='bilinear'` 生成五通道 map，再经 §5.3 的逐像素内存安全与有效域处理，调用 `cv2.map_image(Image, Map, out ImageMapped)`。`map_image` 没有插值字符串参数，插值由 map 类型决定。Nearest、bicubic、`coord_map_sub_pix`、GPU/OpenCL、任意/网格 map 和 `change_radial_distortion_image` 不是失败 fallback。点/XLD 分别用 `cv2.change_radial_distortion_points`、`cv2.change_radial_distortion_contours_xld`；支持面阵相机，线阵不属于首发方法资格。

消费入口与职责如下；AsunControl 旧入口仅作历史分层证据，不是平台调用方式：

| 能力 | `ImageLibDotNet.cv2` 算子 | 使用限制 |
|---|---|---|
| 生成径向映射 | `gen_radial_distortion_map` | 输出参数定义目标尺寸；五通道双线性结构和邻域检查见 §5.3 |
| 映射重采样 | `map_image` | 不检查输入边界；必须先使全部 map cell 内存安全 |
| 点校正 | `change_radial_distortion_points` | source→target 前向变换；保序、有限值和目标域检查 |
| XLD 校正 | `change_radial_distortion_contours_xld` | contour 的所有点前向变换；保留轮廓边界和闭合标记 |
| 输出窗口参数 | `tuple_replace` | 完整目标参数由资产指定；按已知模型字段位置调整主点与尺寸，不临时改变畸变/尺度 |
| map 类型检查 | `get_image_type`、`count_channels`、`access_channel` | int4/int8 索引通道，四个 uint2 权重通道；不靠文件扩展名判类型 |
| 非首发候选 | `change_radial_distortion_image`、`gen_arbitrary_distortion_map`、`gen_grid_rectification_map` | 比较/限制见 §5.2，不作为自动退路 |

Core 不直接调用 cv2。适配器提交核对的是真实 C# 调用形状和本模块输入输出/资源验收，不核验 AsunImage 的存在性、兼容性或授权。

本轮核对的 HALCON 26.05 页面为：[`gen_radial_distortion_map`](../../../halcon算子手册/operators/gen_radial_distortion_map.html)、[`map_image`](../../../halcon算子手册/operators/map_image.html)、[`change_radial_distortion_image`](../../../halcon算子手册/operators/change_radial_distortion_image.html)、[`change_radial_distortion_points`](../../../halcon算子手册/operators/change_radial_distortion_points.html)、[`change_radial_distortion_contours_xld`](../../../halcon算子手册/operators/change_radial_distortion_contours_xld.html)、[`gen_arbitrary_distortion_map`](../../../halcon算子手册/operators/gen_arbitrary_distortion_map.html) 和 [`gen_grid_rectification_map`](../../../halcon算子手册/operators/gen_grid_rectification_map.html)。页面标题固定为 `HALCON Operator Reference / Version 26.05.0.0`。页面明确：`gen_radial_distortion_map` 只适用于面阵相机；`map_image` 不检查映射坐标是否落在输入图像内，双线性插值还必须保证右、下和右下邻点存在，否则可能崩溃；`map_image` 对 `bilinear`/`coord_map_sub_pix` 可内部并行，计算设备只支持 `coord_map_sub_pix`；点校正对使用透视镜头的线阵相机不适用。适配器必须把这些限制变成入口拒绝或能力声明，不能以 domain 标记代替内存边界检查。

### 2.2 只读同类资料的可借鉴点与限制

只读检查了项目内 [AsunControl 参考快照](../../references/project-snapshots/AsunControl/20261004/README.md) 中的标定相关旧实现。可借鉴的分层是“相机参数 → corrected camera params → map → image/point/contour 三类入口”和 `IDisposable` 资源清理。目标算子经cv2完整覆盖已确定；只有实际C#参数类型、重载或封送歧义才查公开签名或消费编译，不把旧入口核对变成封装覆盖门。不能照搬旧实现的可变字符串错误状态、无帧 stride/domain/ROI 修订验证、加载 map 后直接置为 initialized、无资产资格闭包/哈希、无取消/超时/排空、原生对象直接作为业务输出、失败时用空或旧值继续执行。该资料是研究输入，不是本模块 API 或生产证据。

2026-10-09 对大图内存和映射方向的研究实际读取了 OpenCV **4.12.0 / commit `49486f61fb25722cbcf586b7f4320921d46fb38e`** 的 [undistort.dispatch.cpp](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/src/undistort.dispatch.cpp)、[test_undistort.cpp](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/test/test_undistort.cpp)、[CMakeLists.txt](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/modules/calib3d/CMakeLists.txt) 和 [LICENSE](https://github.com/opencv/opencv/blob/49486f61fb25722cbcf586b7f4320921d46fb38e/LICENSE)。Apache-2.0；calib3d 依赖 imgproc/features2d/flann，相关 CMake 还处理可选 LAPACK。仅吸收思想，不引入 OpenCV/C++/其依赖或复制代码。

- `undistort` 源码约 L300–330 以条带构图，并以 `Ar(1,2)=v0-y` 保留全图目标坐标：用于 §5.4 的目标窗口主点偏移和预算设计。它仍持有整个 source/destination，不证明按需源读取或超大虚拟图已解决。
- `initUndistortRectifyMap` 从目标反查源，点路径另行前向变换；`test_undistort.cpp` 的 `Calib3d_UndistortPoints/inputShape`、`Calib3d_InitUndistortRectifyMap/accuracy` 和图像 remap 校验说明应分别验证载荷形状、方向与像素。落点为 §9、§13；测试被读取，未在本机运行，不能作 HALCON 精度证明。
- 固定点 map、OpenCV 的归一化点/迭代模型、`BORDER_CONSTANT` 与 HALCON 五通道 map 不等价，不能照搬参数、量化误差、公差或零填充。生产继续使用 HALCON 26.05；没有同样本比较，不声称所选路线最快。

2026-10-06 已核对的只读 AOI 图像校正来源（`H:\docs\40-development\41-vision-platform\03-calibration-imaging\图像校正开发指导.md`，SHA-256 `551e841fbba68f1381cd92a66b99928825672117d20aa846a98b2c8eb51a631f`，版本 HALCON 24.11）仅吸收两段变换独立身份及资产闭包、缓存 retained bytes 的风险线索。标定求解、运动、全局拼接、辐射/颜色、3D、来源产品 UI/数据库和 24.11 API 不成为本模块事实；不重写来源或来源 manifest。

## 3. 数据流和所有权

```text
FrameLease(只读) + CalibrationAssetSnapshot(不可变)
        + RectificationRequest(冻结)
        ↓ Core 校验/生成 CacheKey
  AsunImage Adapter（唯一持有 native map/image）
        ↓
RectifiedFrameLease 或 Point/Contour Result + ValidityDomain + Trace
        ↓
识别 / 定位 / 拼接 / 计量宿主（自行做目标关联和业务判断）
```

输入帧由 `PKG-006` Owner 持有。模块只取得只读 lease，不写源 buffer，不把 padding 或尾部旧数据导出。标定资产由 `PKG-015` Owner 发布；模块只消费不可变的完整快照和当前资格回读结果，不激活、撤销或修改资产。映射缓存可共享不可变内容，但缓存键必须完整，不能隐藏“当前标定”全局变量。map 的持久化、manifest、保留和清理由缓存/存储适配器 Owner 负责，Core 只消费已验证的缓存回执，不承担业务提交。输出是派生资源；原始帧和派生帧各自有 lease，最后一个实际使用者完成后才释放。

整图路径和按点路径的选择由调用方在请求中明确，模块不得根据业务名称猜测。点/轮廓路径只返回坐标和域元数据，不自动产生整图；整图路径保留原始来源引用，不能以显示预览代替测量输入。

## 4. 模块契约 0.2.0：强类型输入和输出

以下 C# 形状及附录 A 的字段表是唯一模块公开契约。集合在接纳前防御复制为不可变快照；不得用 `Dictionary<string,object>`、自由状态字符串或裸 native 对象绕过语义。产品序列化映射另行接收，模块 canonical 编码见附录 A.4。

### 4.1 基础值对象

```csharp
public readonly record struct PixelSize(int Width, int Height);
public readonly record struct PixelPoint(double Row, double Column);
public readonly record struct PixelRect(int Row, int Column, int Height, int Width);
public readonly record struct RevisionId(string Value);
public readonly record struct ContentHash(string Algorithm, string Hex);
public readonly record struct InputFrameDescriptor(
    FrameSnapshotId Frame,
    RevisionId Revision,
    PixelSize Size,
    PixelCoordinateConvention Convention,
    ContentHash LayoutHash,
    ContentHash FrameHash,
    ContentHash CaptureScopeHash,
    ValidityDomain Domain,
    IReadOnlyList<PlaneLayout> Planes);
public readonly record struct TargetGeometry(
    PixelSize FullSize,
    PixelPoint PrincipalPoint,
    PixelCoordinateConvention Convention,
    PixelRect OutputWindow)
{
    public static TargetGeometry SameSizeCenterPixels(PixelSize size) =>
        new(size,
            new PixelPoint((size.Height - 1) / 2.0, (size.Width - 1) / 2.0),
            PixelCoordinateConvention.CenterRowColumn,
            new PixelRect(0, 0, size.Height, size.Width));
}
public readonly record struct RectificationBudget(
    long MaxOutputBytes,
    long MaxWorkingBytes,
    long MaxNativeBytes,
    long MaxCacheBytes,
    int MaxConcurrentOperations,
    int ProbeBatchPoints,
    int MaxDomainSegments);

public abstract record RectificationInput(InputFrameDescriptor Frame)
{
    public sealed record Image(InputFrameDescriptor Frame) : RectificationInput(Frame);
    public sealed record Point(InputFrameDescriptor Frame, PixelPoint Value) : RectificationInput(Frame);
    public sealed record Points(
        InputFrameDescriptor Frame,
        IReadOnlyList<PixelPoint> Values,
        PointBatchPolicy Policy) : RectificationInput(Frame);
    public sealed record Contour(
        InputFrameDescriptor Frame,
        IReadOnlyList<PixelPoint> Vertices,
        IReadOnlyList<int> SegmentStarts,
        IReadOnlyList<bool> Closed) : RectificationInput(Frame);
}
```

约束：Width/Height为正Int32并不超过显式CoreLimits.MaxDimension；这是宿主声明的工程处理能力，不是固定物理范围。Row/Column必须为有限值，坐标是否允许半像素由PixelCoordinateConvention明确。PixelRect必须位于所属source/target画布内，端点checked Int64验证。删除未进入任何请求/资产端口、没有消费者的PhysicalScale草案类型及其任意µm/px阈值；目标物理尺度由标定资产Owner的CamParamOut与资格Scope确定，本模块不得自行放宽或改变，物理有效范围属于Owner事实，不作为复制/hash所需的软件容量门。

### 4.2 帧、资产和输出约定

| 类型/字段 | 单位/范围 | 默认值与验证 |
|---|---|---|
| `FrameSnapshotId` | 非空稳定 ID | 无默认；同 ID 不同内容拒绝 |
| `FrameRevision` | `RevisionId` | 无默认；必须和 lease 一致 |
| `PixelSize` | px，`1..CoreLimits.MaxDimension` | 无默认；与每plane布局一致，backend可另有更小能力上限 |
| `PixelFormat` | 已登记枚举 | 无默认；不支持格式在 native 前拒绝 |
| `StrideBytes` | Int64 byte，可负，不为0（单行可0） | 所有乘加checked Int64；native能力更小则R0010，不先转Int32 |
| `Origin` | 父帧 px | 默认 `(0,0)` 仅适用于明确全幅输入；ROI 必须带真实起点 |
| `InputDomain` | 规范半开行段见A.4 | Unknown/缺失在所有校正路径R0009；原图诊断不能伪装为校正结果 |
| `CalibrationAssetId/Revision/Hash` | 非空 | 无默认；缺任一项拒绝 |
| `CalibrationScope` | 相机、镜头、传感模式、分辨率、ROI、binning、温度/期限等已登记键 | 无默认；每个敏感条件必须有明确值或 `Unknown`，不能用 latest |
| `TargetGeometry` | 完整目标Size/PrincipalPoint/坐标约定/显式OutputWindow | 与资产CamParamOut一致；窗口位于FullSize内，不默选物理尺度 |
| `Interpolation` | 首发唯一值 `Bilinear` | 固定 `Bilinear`；字段只用于结果 provenance，不允许请求选择其它值 |
| `BoundaryPolicy` | `RejectIfUnsupported / ConservativeValidDomain` | 请求必须显式选择；显示填充不属于计算 API，UI 可另建无量测资格的显示层 |
| `OutputDomainPolicy` | 首发固定 `InputDomainIntersectionAndKernelSupport` | 不作为自由枚举；输出域是输入有效域与双线性核安全支撑域的交集 |
| `CachePolicy` | `Disabled / ReadThrough / RequireHit` | API显式提供；新草稿推荐ReadThrough，RequireHit未命中返回显式错误 |
| `Timeout` | `TimeSpan`，`1 ms..24 h` | 默认由宿主 Profile；核心不无限等待 |
| `MaxOutputBytes` | 正 `Int64`，byte | 无推算默认，宿主显式提供；输入小图、点集、RGB、多平面或大输出不能用“2倍输入”猜预算 |
| `RectificationBudget` | 输出、工作、native、缓存 byte 上限；并发数和 probe 点数为正整数 | 每个上限由宿主 Profile 显式提供；预占失败返回 `R0011`，不以 OOM 作为正常控制流 |

`InputDomain`、map 结构和适用域必须分开：domain 表示已知有效来源，map 的每个输出像素还需检查插值核引用的所有输入邻域。无效、未采样、越界和填充值不能统一编码为 0。

`TargetGeometry.OutputWindow` 是完整目标画布中的半开窗口，必须位于 `FullSize` 内；全图必须显式传入 `(0,0,FullSize.Height,FullSize.Width)`。`SourceWindow` 在 Core 端口中以 `PixelRect` 表示，并通过 `FrameWindowSnapshot` 回传父帧原点、revision、hash 和实际可用域。`RectificationBudget` 的每个上限都必须为正数，`ProbeBatchPoints` 为正数且只限制分批计算，不改变结果顺序或目标范围。`RectificationInput` 的四个变体分别绑定 `Image`、单点、非空点集和分段轮廓；`Operation` 与变体必须一一匹配，不能用空字段表达另一种载荷。

超大帧的窗口读取由后续适配器提供以下最小端口；Core 只依赖该端口，不依赖磁盘、数据库或产品帧实现：

```csharp
public interface IFrameSource
{
    ValueTask<FrameWindowReadResult> AcquireWindowAsync(
        FrameSnapshotId parentFrame,
        RevisionId parentRevision,
        ContentHash parentHash,
        PixelRect sourceWindow,
        long maxHeldBytes,
        TimeSpan timeout,
        CancellationToken cancellationToken);
}
public sealed record FrameWindowReadResult(IFrameWindowLease? Lease, RectificationError? Error);

public interface IFrameWindowLease : IAsyncDisposable
{
    FrameWindowSnapshot Snapshot { get; }
    void CopyRow(int planeIndex, int localRow, Memory<byte> destination);
}
public sealed record FrameWindowSnapshot(
    FrameSnapshotId ParentFrame, RevisionId ParentRevision, ContentHash ParentHash,
    PixelRect SourceWindow, InputFrameDescriptor Layout, ValidityDomain Domain,
    IReadOnlyList<PlaneLayout> Planes);
```

AcquireWindowAsync的maxHeldBytes为本次剩余已预约输入额度，必须为正；timeout取当前请求剩余期限且为1ms..24h。端口先求实际allocation容量再预约/读取，超过上限R0011，不先读取再等引擎发现超限；共享整帧按保留父allocation容量报账。复制跨tile窗口同时存活的源tile、目的窗口及scratch都计入该额度；失败或期限到达先结束本次IO再返回。FrameWindowReadResult 成功时 Lease 非空且 Error=null，失败时 Lease=null 且 Error 非空。IFrameWindowLease.Snapshot 报告实际窗口、父帧身份/hash/revision、plane 布局及窗口域；不足/截断/断连为 R0020，revision/hash 错配为 R0003，非法布局为 R0002。不返回最近窗口。CopyRow的plane/row是Snapshot局部坐标；Snapshot.Planes要求Offset=0、Stride=RowBytes、AccessibleBytes为逻辑局部容量（不表示有可直接取的整块buffer），AllocationBytes仍报实际分配/父buffer容量，AllocationId相同只计一次。源原layout可负stride，读端口按冻结源布局复制，不把padding计入行。成功租约仅在存活期CopyRow，destination长度必须恰等于该plane.RowBytes；行号越界/lease关闭报明确异常，native适配器捕获为R0002/R0020并安全排空；不把整块虚拟帧压入Int32长度的ReadOnlyMemory。失败路径由端口归还已取得资源。

### 4.3 请求与结果

```csharp
public enum RectificationOperation { Image, Point, Points, Contour }
public enum PixelCoordinateConvention { CenterRowColumn, CenterColumnRow, CornerRowColumn }
public enum PointBatchPolicy { AllOrNothing }
public enum RectificationTerminalState { Completed, Rejected, Failed, Cancelled, TimedOut }

public sealed record RectificationRequest(
    string RequestId,
    RectificationOperation Operation,
    FrameSnapshotId SourceFrame,
    RevisionId SourceFrameRevision,
    CalibrationAssetRef Calibration,
    TargetGeometry Target,
    RectificationOptions Options,
    RectificationInput Input,
    RectificationBudget Budget,
    TimeSpan Timeout,
    CancellationToken CancellationToken);

public sealed record RectificationResult(
    string RequestId,
    RectificationTerminalState State,
    RectifiedPayload? Payload,
    ValidityDomain? Domain,
    CoordinateMappingDescriptor? Mapping,
    RectificationTrace Trace,
    RectificationError? Error);
```

`RequestId` 在实例 epoch 内唯一：重复提交拒绝，原操作通过 `GetStatusAsync` 查询；业务历史回放由宿主按原输入/版本创建新请求，不把同 ID 重跑称作幂等。`SourceFrameRevision`、输入 hash、资产 revision/hash、Target、Options、Budget、点/轮廓数组在接纳时冻结。`Input.Frame.Frame` 必须等于 `SourceFrame`，`Input.Frame.Revision` 必须等于 `SourceFrameRevision`。`Input` 与 `Operation` 必须匹配：Image 没有点载荷；Point 恰为1点；Points 非空点集；Contour 非空分段轮廓。点/轮廓只需帧布局/域元数据，不取像素lease；非Image的Planes可为空，但Size/FrameHash/CaptureScopeHash/Domain必填，Image至少1个plane。`AllOrNothing` 为首发唯一点批策略；不删坏点或改变对应顺序。结果仅 `Completed` 有 `Payload/Domain/Mapping`，其它终态三者为 null；失败诊断只能进入 Trace。

`Payload` 在工作资源真实排空后才移交结果 Owner。`ResourcesReleased` 指本操作输入/native/工作 map lease、请求IO/资格观察器和临时资源已归还，不含独立封存待移交的结果像素/坐标/域内存或仍由 cache Owner 持有的不可变缓存。发布失败时引擎释放该候选，成功后结果 Owner 必须独立 Dispose；事件不携带 Payload。详见附录 A.3，消除“全部输出释放后才返回图”的矛盾。

`CoordinateMappingDescriptor` 的完整字段在A.4；Source/Target包含frame、中心/corner约定、源/目标窗口原点尺寸；Direction、插值/边界、域规则/域hash和可空map hash及算法/适配器版本均显式记录。它不包含可变 native handle。

## 5. 参数验证和处理步骤

固定顺序如下。步骤1–5和资源预约失败不调用 native；步骤6若需创建 map，已经进入 native，后续拒绝/取消必须排空。不能把 map 生成描述为纯预检或让其异常走未接纳短路径。

1. 校验请求 ID、操作类型、取消状态、超时和宿主能力版本。
2. 冻结InputFrameDescriptor纯元数据，验证各plane尺寸/format/offset/stride/rowBytes/声明buffer长度和规范域；checked计算首末字节，拒绝溢出/负stride越界/padding/非支持编码/来源revision错配。不取得像素lease；实际读取在Accepted和窗口计划后。
3. 读取标定资产 snapshot；验证内容 hash、相机模型、输入分辨率/ROI/binning、目标相机参数、适用 scope、资格状态和失效/撤销修订。相机/镜头、焦点、工作距离、温度等来自实际冻结观测，Unknown 不能与任何 scope 匹配。证书和板描述的受控引用属于资格闭包，由资产 Owner 签发，本模块不登记板、不反推板参数、不作资格批准。多个可用候选不能按 latest/低RMSE选一个，调用方须给精确引用，否则 R0004；候选、过期、撤销或 Unknown 拒绝运行资格。
4. 验证 row/column 与像素中心/corner 约定。跨 HALCON 的桥按 `PKG-007` 公式显式换基；不得仅按参数名猜 x/y，也不得重复补半像素。
5. 冻结请求/资产/Options的CalculationIdentity和预算预检。显式窗口的最终source窗口/局部参数只能在Accepted后由§5.4确定，完整map key此后才能生成和查缓存；点/XLD无map key。
6. 预约初始完整峰值预算/并发permit后Accepted；订阅并回读资格屏障；图像按§5.4生成WindowPlan并按真实allocation补充预约，不足先排空再R0011。取得精确source lease、生成完整key并查/造map，按§5.3全cell验证，冻结本次map/domain/资格和预算摘要；cache hit不重用旧资格/preflight。native前再检查取消、deadline和资格闩锁，不热换身份。
7. 执行点/轮廓变换或整图重采样。优先按点/轮廓路径满足少量坐标需求；整图只在调用方请求 `Image` 时执行。取消检查只在安全边界进行，native 未确认结束前不释放输入或 map。
8. 计算输出 domain 和 trace；整图结果与原始来源保持父坐标映射。输出 quality 记录有效像素比例、被收缩边界、插值策略、域外数量和输入质量，不产生业务 PASS/NG。
9. 封存候选结果不通知消费者；进入Draining并确认native真实完成→按A.6完成发布前资格回读IO和本请求资格观察器收尾→确认全部请求工作结束后Drained→归还输入/native/回读工作资源→ResourcesReleased→本地发布闩锁比较→ResultPublished/Completed。回读撤销/Unknown则安全释放候选后Rejected/R0005；取消/期限到达按原原因终态。任一请求工作排空无证据则DrainUnknown，ExecuteAsync仍未完成，任何载荷隔离。

对于透视/姿态/平场等其它变换，调用方必须先调用对应模块并明确组合顺序。若组合多次采样，只有在同一量测定义、域和边界证明通过后才能实现融合 map；省一次采样不能成为改变坐标意义的理由。

### 5.1 标定靶与无标定边界

畸变校正 map 不是从任意图像“自动拉直”出来的。生产路线必须消费 `calibration-assets` 已发布、未撤销且对相机型号/镜头/分辨率/ROI/binning/焦距状态适用的资产；资产生成阶段需要物理参考靶观测。面阵相机默认参考靶为带证书的 HALCON 标准矩形圆点板（`gen_caltab`/`find_calib_object` 链）；棋盘格只有在已验证的角点观测适配和对应资格 Profile 下才可用，不能假设 `find_calib_object` 直接支持普通棋盘格。圆点阵、AprilTag、线阵/远心/3D 专用靶按标定资产模块的 `CalibrationTargetKind` 和方法资格选择，不互相代替。

标定板不需要出现在每张运行帧中；运行校正读取被冻结的资格资产。资产缺失、资格未知/撤销、布局越域、硬件/光学配置变更时，默认拒绝校正。当前契约不提供DiagnosticOnly校正请求；离线模拟和原图预览只能独立标识为诊断，不得用单位映射、身份变换、最近资产或“看起来已拉直”的图作为校正成功。原图只读保留，失败时调用方可重新显示原图，但该显示回退不得被算法消费者误作校正输出。

### 5.2 具体算法路线、备用路线和禁止的“训练”

| 路线 | 适用输入与参数来源 | 固定处理顺序 | 失败/备用条件 | 验收断言 |
|---|---|---|---|---|
| A：已资格径向校正（首发唯一整图路线） | `PKG-015` 发布的 `CamParamIn/CamParamOut`、面阵相机模型、帧尺寸/ROI；插值固定 `bilinear` | 校验模型和布局→`GenRadialDistortionMap`→验证 map 结构及每个输出采样的四邻点边界→`cv2.map_image(Image,Map,out ImageMapped)`→传播安全有效域 | 参数/布局不符：`R0005/R0006`；map/邻域不安全：`R0008/R0009`；不切换到其他整图算子/插值 | 同一 map key 冷/热结果一致；所有输出采样邻域可访问；边缘 domain 只收缩不越界 |
| B：点/点集校正 | 已绑定 `CamParamIn/CamParamOut` 和 source row/column；点顺序、中心/corner 由请求声明 | 校验长度/有限值/坐标约定→`ChangeRadialDistortionPoints`→逐点检查目标域→按 `PointBatchPolicy` 发布 | 空点集：`R0001`；长度不一致：`R0001`；线阵透视镜头：`R0010`；部分点越域按唯一 AllOrNothing 返回 `R0009` | 不生成整图；输出顺序和输入一一对应；中心点换基反例可检出 |
| C：XLD轮廓校正 | 托管顶点/SegmentStarts/Closed+源身份；适配器内部构造XLD | 规范载荷/源域支撑→cv2.change_radial_distortion_contours_xld→输出顺序/闭合/域检查→排空→发布 | 任一段或点无效R0009；不返回半条或自动删点；native失败R0014 | 保持分段与采样点身份；不宣称未采样连续曲线精度 |
| D：任意/网格 map | 首发不支持 | 无 | 返回 `UnsupportedCapability`；不得切到它作为径向失败 fallback | 后续如需开放，按独立方法修订冻结 map schema、算子签名、插值、边界、安全域和 Golden |

路线 A 是首发唯一整图生产路线；B/C 保持独立的点/XLD 几何路线。`radial_distortion_self_calibration`、相机标定求解、噪声点剔除、网格拟合、机器学习训练、参数搜索和自动选择模型不属于本模块。它们由 `PKG-015`/资格 Owner 或外部离线工具完成，输入本模块的只能是不可变、带 revision/hash/适用条件的资产。未装配该后端时返回R0010（完整算子覆盖已确定，无需重复核验），不把其它算子、插值或显示填充偷偷当 fallback。

候选比较的技术决定：固定相机参数、多帧整图采用生成一次 map 后复用；少量坐标采用点/XLD 路线，避免帧复制和整图输出。`change_radial_distortion_image` 每次重算且缺少独立 map 预检入口，故不作生产退路。`coord_map_sub_pix` 可在计算设备运行，但需要另一套内存边界/设备上限/数值 Golden，当前不开放；nearest 会改变亚像素插值语义；网格/任意 map 没有本模块已批准模型资格。这些为机制比较，不是本机速度排名。弱信号、噪声、遮挡和饱和只影响输入质量/有效域，不触发重新估计参数或“修好图像”；参数/模型退化交回资格 Owner。

参数推荐仅可无 UI 调用 `RecommendExecution`（附录 A.2）：根据冻结布局、目标窗口、Budget 和 backend capabilities，给出整图能否预约、可用窗口上界及确定性拒绝原因。不得推荐或修改 CamParam、插值、物理阈值、InputDomain、资格范围；生产执行仍消费宿主显式冻结的窗口和预算。推荐版本/输入hash/计算字节数进入摘要，不在线搜索参数，也不把建议自动替换进请求。ROI 路线省的是输出/工作 map 规模，不证明缺陷检测、ROI 覆盖或量测正确。

### 5.3 双线性 map 的内存安全与计算有效域

HALCON 26.05 五通道 map：第一通道为 `int4`（仅实际 XL 能力允许时为 `int8`）的源左上邻点线性索引，2–5通道为 `uint2` 的左上、右上、左下、右下权重（0..65535）。`get_image_type` 只报第一通道，须 `access_channel` 后逐通道核对。输入 native 图为明确导入的紧凑行序矩阵，索引宽度用该矩阵 Width，不用宿主 byte stride。packed/负 stride 输入先逐行复制到紧凑图；原始布局和复制成本仍记录，不能把 padding 当像素。

1. 对目标的**全部** cell（包括未来无效域）检查索引/权重结构。源至少为2×2；`r=index/W`、`c=index%W`，checked 验证 `index>=0`、`0<=r<H-1`、`0<=c<W-1`，不能仅检查 `index+W+1 < W*H`，否则最后一列会跨行。生成器产生的合法权重原样保留，不重新归一化；缓存内容以生成 schema/hash 验证，禁止外部自造任意权重 map。
2. 计算 `Valid(p)=MemorySafe(p) && InputDomain` 同时包含四邻点 && 资产支持域包含此样本；权重为0也不豁免邻域检查。InputDomain 采用像素中心集合；bilinear 的连续支撑与离散域不能混同。空结果域 R0009。
3. `RejectIfUnsupported`：目标存在无效 cell 即拒绝，若已生成 native map 仍走排空。`ConservativeValidDomain`：保留请求的输出尺寸/原点，不裁掉坐标；建立操作私有 **SafeExecutionMap**，无效 cell 替换为内存合法锚点 `(r,c)=(0,0)` 与权重 `[65535,0,0,0]`，但其 validity 始终为 false。使用 `copy_image` 取得各通道物理副本后才改写；用 `get_image_pointer1` 在适配器私有对象作用域内批量访问，遵守公开指针寿命、64位不截断，不反射或修改封装。重组用 `append_channel`，保留组成通道 Owner 到映射排空；不得用 `copy_obj` 浅拷贝改共享 map。
4. 重新扫描 SafeExecutionMap 的**全部** cell，全部内存安全后才能 `map_image`。不能靠 `reduce_domain/change_domain`、输出 mask 或“只消费有效像素”避免 native 越界；校验失败 R0008，不调用 map_image。只有语义有效 cell 可用于算法；无效位置的存储值是无意义的哨兵采样，结果必须与 validity 同消费，不能当有效填洞/原图回退。
5. Trace 分别记录资产 map hash、私有安全 map hash、输出有效域 hash、验证算法版本、无效数和工作副本字节。保守处理不改资产和 cache，也不扩大域；输入/缓存可被另一实例读取。运行后 native 输出复制到有界、结果 Owner 持有的托管像素/域，再排空所有 native 对象。

官方依据补充：[`copy_image`](../../../halcon算子手册/operators/copy_image.html) 明确物理复制各通道；[`get_image_pointer1`](../../../halcon算子手册/operators/get_image_pointer1.html) 明确指针仅随对象存活及浅引用共享写风险；[`append_channel`](../../../halcon算子手册/operators/append_channel.html) 不分配新像素矩阵。修改 map 是内存安全适配，不是并行视觉算法。首个 native 切片验收必须覆盖无效域中越界索引、最后一列、1×N、zero-weight越界、cache 冷热、双实例及取消；没有这组真实验收不能仅凭 mask 宣称安全。

### 5.4 超大帧、显式输出窗口与源窗口

`TargetGeometry` 始终携带完整目标画布和 `OutputWindow`（目标画布中的半开矩形）。全图是显式 `OutputWindow=(0,0,FullHeight,FullWidth)`；输出像素 `(r,c)` 对应完整目标 `(r+Window.Row,c+Window.Column)`。本模块不选择扫描顺序、不补缺 tile、不找缝、不做融合/全局注册；宿主 mosaic/viewport 组合窗口并拥有完整性。

整图能满足 backend 的尺寸、线性索引和峰值预算时用 A；不满足时返回 R0011/R0010，**不自动变成部分成功**。宿主另发明确窗口请求。大图虚拟帧通过 `IFrameSource.AcquireWindowAsync` 读精确 source 窗口，后端不要求拼成全图，Core 不引用磁盘/数据库实现。

窗口处理固定为：

1. 用冻结的完整 `CamParamOut` 和 `CamParamIn` 对目标窗口每个像素中心执行反向坐标计算（`change_radial_distortion_points` 将参数对调）；分批上限来自 `ProbeBatchPoints`，扫描全部目标 cell 而不是四角估计。非线性映射的极值可能在中间。计算范围使用 checked Int64；非有限、非单值/资产未确认支持域、失配即拒绝，不猜 inverse 或外推。
2. 对全部内存可用候选样本求四邻点集合的最小 source 包围矩形，包含右/下支撑邻点；这就是 halo 的来源，不能固定“输出边缘加1像素”替代。若无可用样本 R0009。源窗口过大或超过 backend 能力 R0011/R0010，宿主可重新请求更小目标窗口；不是偷偷降分辨率。
3. `AcquireWindowAsync` 取得精确窗口及 parent ID/revision/hash/domain；不足、断连、截断或读到新 revision 不用最近窗口，R0002/R0003/R0020。窗口只读、作用域内有效，归还不销毁虚拟帧。硬件 ROI/binning 必须原资产适用；此处是同一冻结帧的内存裁窗，不是更换相机配置。
4. 源窗口局部参数：`CxInLocal=CxIn-SourceWindow.Column`、`CyInLocal=CyIn-SourceWindow.Row`，尺寸改为源窗口；目标局部参数同理按 OutputWindow 偏移 Cx/Cy 和尺寸。模型、畸变系数、焦距/放大率、Sx/Sy 保持资产值。按 [`Calibration`](../../../halcon算子手册/operators/toc_calibration.html) 的模型参数位置及 [`tuple_replace`](../../../halcon算子手册/operators/tuple_replace.html) 写新 tuple；禁止裸数组猜索引。未知模型布局 R0010。生成局部 bilinear map，再按 §5.3 校验；不足的邻域拒绝，不自动用另一个 source lease 补拼。
5. 全图和每个窗口使用相同完整目标模型、插值和资产闭包。cache key 额外含完整 target、OutputWindow、SourceWindow、parent source布局、局部参数hash和schema；窗口局部 map 不能用于另一个窗口。输出 domain 是局部集合，Mapping 保留 target/source 双原点，消费者换到父坐标后再处理。

首发支持的资产模型为 `area_scan_division`、`area_scan_polynomial` 及对应 `area_scan_telecentric_division/polynomial`；不包含 tilt、线阵和 arbitrary map。division 数值序列为 `[Focus或Magnification,Kappa,Sx,Sy,Cx,Cy,Width,Height]`，polynomial 为 `[Focus或Magnification,K1,K2,K3,P1,P2,Sx,Sy,Cx,Cy,Width,Height]`，前缀为模型字符串；Focus/Sx/Sy 为米，Magnification 无量纲，Cx/Cy/Width/Height 为 px，其余参数单位按该模型官方定义由资产保留，不能统一标成 px。Core 仅检有限值/长度/正尺度，资格 Owner 负责模型物理有效性。完整无畸变 target 系数须为零，不能只改Kappa后留下P1/P2。

窗口是径向 A 的同模型执行方式，不是路线 D 或世界平面投影。已有批准资产只描述到无畸变相机平面；要求物理投影/产品坐标时由坐标/配准/mosaic 的公开映射先定义，不在本模块偷偷叠 homography。跨 FOV 原始身份不同，即使尺寸相同也不能合成一个校正 source。

验收采用同一冻结 source/target 的整图与不重叠窗口，逐像素比较共同有效域、坐标链和 seam 邻域。允许数值差由方法资格 Profile 明确，未采纳只能报差异、不能判通过；预算窗口、源窗口遗漏中间极值、1px窗、边缘窗口、窗口乱序/重复、新revision、跨实例取消必须有反例。超大虚拟源只对准入后的窗口适配切片验收，不要求 Core/点路径先获得整图。

### 5.5 生产适配器逐步装配、像素与轮廓导出

本节补齐C3/C4/C5的可决定软件步骤，复用A.7的公开工厂与原端口，不新增模型或产品接口。HALCON调用名为operator语义顺序；C#输出/tuple/指针经`ImageLibDotNet.cv2`公共类型表达，只有实际重载或封送歧义才在消费工程确认。不得把下面的顺序规格写成未经编译的成功示例。

| 阶段 | 固定实施规则与失败边界 |
|---|---|
| 资产参数与单位 | 按§5.4四种模型，CameraModel作为tuple首项，CamParamIn/Out为其后8或12个数值；Width/Height必须是精确正整数，且分别等完整Source.Size与Target.FullSize，主点等按Target.Convention规范化为CenterRowColumn的Target.PrincipalPoint。Focus/Magnification、Sx/Sy正且有限；Out全部畸变系数为0。输入/输出模型必须相同，不把透视模型与远心模型互换。输入保持Owner已批准系数，不根据图像重算。参数字符串/数值混合tuple顺序与单位沿HALCON26.05 Calibration手册，裁窗仅改主点与Width/Height；不能把米换成毫米再传算子 |
| 计划/预算 | 按§5.4逐目标中心反查，完成原Plan任务后才取得单一source lease。RequestId在同一个backend Session生命周期内唯一，因为ObserveDrain仅按该ID查原任务；共享Session的不同Engine也须用不同ID，同ID第二作业R0018且不启动native。每个Session原任务表/已用ID有界，占用MaxActiveRequests和CoreLimits.MaxTraceEvents的墓碑槽，槽满R0011不忘掉原身份。Session版本是部署固定值，不在请求中自由选择 |
| plane导入 | 对Snapshot.Planes按plane顺序、各plane内部channel顺序逐一处理，类型固定Byte→byte、UInt16→uint2、Int16→int2、Float32→real。每行CopyRow到精确RowBytes的已预约缓冲；Channels>1按像素内channel升序解交织为单通道紧凑矩阵，不做RGB转换、灰度化、gamma或alpha预乘。使用gen_image1(Type,SW,SH,有效指针)生成私有复制图；输入缓冲固定/pin仅持续至该原调用真实返回。HALCON自行复制像素后才能解除pin/归还scratch；不使用gen_image1_extern的回调所有权路线。原始padding/负stride由源端口处理，不能导入pad或把源指针留给native |
| map导入/导出 | 新map按gen_radial_distortion_map生成；缓存map先核A.5 key/schema/hash/长度，再逐通道gen_image_const(Type,OW,OH)创建私有矩阵，get_image_pointer1核type/尺寸后完整写入little-endian索引/权重，append_channel组成五通道map。int4/int8/uint2都用此统一路线；gen_image1不支持int8，禁止强转成int4。HALCON指针只在私有对象存活期、worker线程内使用，x64不截断，所有写入之前核checked字节容量；没有未初始化cell进入map_image。生成map的导出按access_channel→copy_image→get_image_pointer1逐通道复制，Core MapContent只含托管独立bytes，不含句柄。append_channel不分配像素矩阵，组成通道Owner保留到最后一次使用真实结束 |
| map执行/结果 | 真实全cell检查、私有SafeExecutionMap及复检严格按§5.3。同一安全map顺序map_image每个私有输入channel；get_image_pointer1核输出类型/尺寸，按原plane格式重新交织写入已经预约的独立ImagePayload数组。plane数、channel数/顺序和像素格式与输入完全一致，源/输出域为所有参与plane与资产支撑的交集。Float32在有效域内出现NaN/Infinity为R0002（源）或R0014（输出），无效位置不赋计量意义。任何一channel失败全请求无Payload，不移交前几个channel。最后释放本次native输入/输出/map/tuple及输入lease，再走A.6发布屏障 |
| 点/点集 | 先NormalizeCoordinates到CenterRowColumn，按输入Index顺序建立Row/Column double tuple，调用change_radial_distortion_points(Row,Column,CamParamIn,CamParamOut)。输出两tuple长度必须恰n且全有限，逐点核完整目标/OutputWindow和来源/资产支撑，再换回Target.Convention并保持顺序。输出数值仍是完整目标画布坐标；只有Image像素/域数组局部化，不能给点结果重复减OutputWindow原点。点/点集无帧读取、无map/灰度插值、无“每米像素”的隐式单位换算 |
| 分段XLD | 逐原SegmentStarts确定每段，不跨段连接。每段gen_contour_polygon_xld(Row,Column)，Closed=true时仅在适配器临时序列末尾追加首点一次表示闭合；开放段不追加。按段单独change_radial_distortion_contours_xld→get_contour_xld，输出顶点数必须是原n（开放）或n+1（显式闭合），核追加末点与首点一致后只去掉适配器自己追加的最后一点，保存原Closed/SegmentStarts。输入本身首末坐标相等不推断闭合、也不去重。全顶点与所有源线段按A.4保守域规则检查；任何段错误整批R0009/R0014，无平滑、拟合、补点或重采样。临时闭合端点与tuple/XLD开销在CoordinateBufferBounds中明确覆盖，不改C1/C2既有预算示例 |

plane数据以本Windows x64小端数值读取，HALCON输入/输出Type保持原样；本模块不改变位深，不以显示窗宽/窗位或调色值替代计算像素。Output Layout每plane Offset=0、Stride=RowBytes=输出宽×Channels×格式字节数，AccessibleBytes为实际数组长度，AllocationBytes报告实际保留容量，每独立数组新AllocationId；输出域在窗口局部坐标，Mapping保留两个原点和完整模型身份。点/轮廓数值保持完整目标坐标；Domain仍按A.4投影到OutputWindow局部，检查/显示须经Mapping和窗口原点换回完整目标。非Image的AllOrNothing证明本批点/源线段的支持性，不能拿其Domain包络当整幅重采样图的全cell证明。

图像预算预检继续用A.2的确定性建议，不把建议当真实allocation证明。运行预算分两次闭合：接纳前预约目标托管输出、原map+安全map、域/trace/元数据和probe缓冲；Plan完成后、Acquire前把source窗口紧凑scratch、单channel native输入/输出、五map通道/导出副本、源端口同时持有的parent/tile容量及HALCON声明scratch计入峰值，再调用Acquire(maxHeldBytes)。port的额度同时覆盖source tile与目的缓冲，返回实际容量后复核；超额先等原任务退出再归还，R0011无后续Run。按channel串行会同时保留完整托管结果，不能只算一个输出channel；cache miss的map封存/Publish克隆与生成map共存，hit也有导入和SafeExecutionMap副本，不把热命中算成零工作空间。

LimitsDeclaration为该部署适配器冻结的能力上界：图像宽高、索引范围、native/working/map池、FixedScratchBytes和C3 CoordinateBufferBounds全部有真实消费编译与资源验证责任。未知变量内存不得填0或由用户猜系数；相应能力不开放，C1/C2/S1不受影响。native验收在相同方法/版本与声明最大负载上确认这些界限，未通过是本模块适配实现/资源运行门，不能冒称客户外部门；没有该证据不授native运行资格。模块不调用set_system改变宿主全局并行/分配参数；模块并发permit与HALCON内部并行分别计峰值，不用“reentrant”推断无限并发安全。

官方26.05补充依据：[gen_image1](../../../halcon算子手册/operators/gen_image1.html)（复制输入存储/指针限制）、[gen_image_const](../../../halcon算子手册/operators/gen_image_const.html)（int8仅64位，完整写入私有图）、[gen_contour_polygon_xld](../../../halcon算子手册/operators/gen_contour_polygon_xld.html)与[get_contour_xld](../../../halcon算子手册/operators/get_contour_xld.html)（按原顶点构造/导出）。get_image_pointer1/copy_image/append_channel的寿命与共享写约束直接复用§5.3；未运行这些算子，不将文档依据记成native通过。

### 5.6 自动选择、透视边界与插值误差验收

自动选择只有“已声明用途对应方法”和“预算候选”两层：Image→唯一径向bilinear A，Point/Points→B，Contour→C；不根据像素、缺陷、噪声或坐标数量猜用途，不把Points偷改Image。自动窗口候选按A.2枚举宽度/单调二分高度，最大面积、并列宽者、保持请求左上锚点；候选与InputHash/RecommendationVersion绑定，输入/预算/版本变化立即失效。UI只显示建议及解释，由操作者/Host显式形成新草稿/新请求；没有批准的CamParam/目标尺度/资格不推荐模型或资产。上界超尺寸/索引能力为R0010，算术/额度超限R0011，不返回负估值或零大小候选；ConservativeValidDomain不允许推荐偷偷扩大域。无UI与UI均调用同一RecommendExecution，不增加另一参数搜索器。

透视镜头的成像模型不等于“透视整平”：本模块只把径向畸变CameraPixel映到CorrectedPixel。CorrectedPixel→Plane/ProductFrame的透视、平面/高度、单位和资格由[coordinate-geometry §8](../coordinate-geometry/DEVELOPMENT-GUIDE.md#8-halcon-2605--asunimage-视觉路线)原Owner定义；本模块不消费homography/plane-pose、不会自动选world-plane/任意map。业务链先去畸变、再用准确绑定此无畸变相机参数的公开坐标边变换；不能将原有含畸变相机边用于CorrectedPixel再次去畸变，也不能对未校正的CameraPixel直接套无畸变边。世界投影、融合map、多次采样的复合误差批准在原Owner/宿主，本模块当前没有融合API，不把误差小当作范围扩展。

误差分四项分别验收，不能把“看起来直”或标定RMSE合成一个精度承诺：①原资格资产及适用范围的物理残差（资产/qualification Owner）；②点/轮廓正反方向、坐标换基与局部/父坐标的软件数值误差（本模块C3/C5）；③bilinear坐标/权重量化、灰度计算与位深舍入（本模块C4）；④再次投影/拼接与下游测量的不确定度（对应坐标/mosaic/计量Owner）。本模块不输出臆测的µm精度或把bilinear权重分辨率当物理误差。

图像数值验收使用本测试工程中的独立参考，生产仍仅HALCON路线：对每有效目标中心先用同一冻结参数独立获得反查source坐标，再以double计算四支撑的理想bilinear值与精确读取map权重的`g_map=Σ(w_i/65535)*v_i`；分别比较“理想值→map权重值”和“map权重值→native输出”。不在生产重算/归一化生成器权重；参考不调原native输出以迎合期望。权重量化解释界限为`max(abs(v_i))*Σabs(w_i/65535-α_i)`，它只解释本cell的灰度差上界，还须另计像素类型舍入/浮点与实现误差，不宣称HALCON确实达到该总界限。实际允许偏差按方法资格/消费者Profile，整数/Float32分别记录MaxAbs与RMSE及有效sample数；空有效sample拒绝，不拿无效哨兵计算均值。缺方法容差只能NotEvaluated，不能临时加1灰度让测试过关。

下游识别/定位可直接使用点路径，避免由重采样像素重新定位带来的额外误差；拼接/计量如消费派生图，必须同时消费Domain、Mapping和原资格闭包。支持域有洞、饱和/低信号、采样不足、边界外推或光学状态变化按明确域/资格拒绝，不能调用自动模型搜索修好输入。缓存复用只省生成，不省支撑检查、当前资格和输出Owner；超大图每显式窗独立证明，整图/窗差、seam和逐点正反差是不同指标。

### 5.7 C5原帧、资格与Store的确定消费接线

本模块C5不是另一套帧资源服务或数据库。Core只引用自己的IFrameSource/ICalibrationSnapshotPort/IQualificationBarrierPort/IMapStore，宿主可按下列明确字段映射接入现有公开Owner；A.7 Store wrapper的验证/原Task/回执/关闭是本模块确定实现，不再留给后续开发者设计。源buffer/资产签发/文件事务仍在原Owner，不能复制其私有表、Retire全部源或在校正侧捏造来源hash。

接入[image-frame公开资源与tile契约](../image-frame/DEVELOPMENT-GUIDE.md)时，Host构造有界冻结对应表：本模块FrameSnapshotId/Revision/FrameHash/LayoutHash/CaptureScopeHash→原FrameKey(Guid Id,ulong Revision)、原ServiceEpoch、准确源Descriptor、ConsumerId及既有plane索引序列。完整frame内容hash由原来源发布权威提供，像素不必重复全帧扫描；普通FrameDescriptor没有内容hash字段，不从Key/SourceRevision拼假hash。对应表缺失/修订失配R0003；origin、单位、plane角色/scale/bias/Channels和域也在对应表冻结，不从最近帧推断。表数量/文本/容量按CoreLimits和宿主根预约，SourceKey变更需新输入，不热改既有表。

Acquire的PixelRect(Row,Column,Height,Width)准确映到image-frame PixelWindow(X=Column,Y=Row,Width,Height)，read Halo=0（本模块Plan已包含四邻halo）、Intent=ExactSamples、level=0，plane索引严格升序且保持原索引映射。图像已有ConservativeValidDomain需要保留域洞，因此边界选择ClipAndMarkInvalid并要求ActualWindow仍等本次精确窗口；不让上游Clip悄悄缩source，真实缺样/裁短R0020。source scale/bias为语义元数据，本模块只保留原标量，非强度/彩色plane若其语义需单位变换必须由外部明确前处理，不能在校正中乘bias或混合高度plane。浮点/通道/窗口上限与source原能力都核验；非零LOD/缩略图不得伪装原像素。

上游ReadAsync/ReadTileAsync原Guid RequestId在调用前由Host进程根有界登记到本次校正Acquire与原ServiceEpoch，成功ReadResult.Slice非空且OperationResourcesReleased=true；Empty可仍持lease，不能当null或零成本。响应仍Unknown/资源未结束时保留原Task/OperationLookup原身份和预算，校正Acquire保持未完成，直到原完成证据到达再移交或归还。获取slice后核SourceKey/ActualWindow/SourcePlaneIndices/Allocations与冻结对应表，按AllocationId汇总真实CPU/native/gpu/源scratch held容量，不只报窗口面积；本路线只接受可CopyRow的CPU exact samples，native/GPU源须由其Owner先显式转为已批准CPU来源。

本模块的window lease内部独占所取得的上游slice与read scope。每CopyRow通过TryOpenReadScope取本次scope，在同一同步作用域复制精确字节，再Dispose此scope；不把scope交native或UI、不与未结束scope并发释放slice。源有负stride或padding仍只返回标量行；上游错误精确映为R0002/R0003/R0020，任何异常不返回未验证像素。window.DisposeAsync单次登记上游ReleaseAsync的原回执Task，有限观察不能令它完成；LeaseClosed且Drain=Drained、所有自己scope退出才证明本window租约归还。StorageReleased=false可能只因其它消费者仍持父allocation，不强制Retire或要求整个source销毁；自己的held charge归还与全局物理allocation存活分开。错误/FrameDrainException继续强持原slice/scope/Task，按原leaseId恢复，不第二Read或强制释放。image-frame Owner的QueryOperation/Release/Close语义只按其唯一指导调用。

资产端口的适配只映射已发布asset准确Id/revision/hash、四种模型完整CamParam、scope定义与支持域；本模块引用hash是外部受控资产身份，不按A.4重新生成外部hash。Read原Owner验证内容完整性和来源，Qualification按A.6的实际CaptureScopeHash/水位/时间消费，Watch保留原通知Asset/epoch/revision/gap。资格回读不能只读最近缓存；实现缺失就R0005，不把依赖暂缺改成Qualified。Store Owner准确执行A.5的PublishId/key/contenthash/query/NotFound确定性与耐久规则；A.7 wrapper不创建数据库，也不在ReadThrough失败时把原Owner未知事务忘掉。Source/资产/资格/Store各自的生产配置由现有Owner提供，但这里的参数映射、等待、错误和租约交付顺序已经确定。

## 6. 同步、异步、事件和状态

### 6.1 入口语义

运行Core（C2及以后）的入口，完整接口见A.4：

```csharp
RectificationResult Execute(RectificationRequest request);
ValueTask<RectificationResult> ExecuteAsync(
    RectificationRequest request,
    IProgress<RectificationProgress>? progress = null);
ValueTask<DrainResult> DrainAsync(TimeSpan timeout, CancellationToken cancellationToken);
```

`Execute` 不能阻塞 UI 线程；同步入口仅适用于宿主明确提供的后台线程或纯托管按点/轮廓计算。`ExecuteAsync` 不改变结果语义。首个纯 Core 切片无 native 执行、native/frame lease 或 map cache，其并发限额只约束 Core 实例内的托管计算；AsunImage 适配器的线程和资源限制属于后续独立切片。调用方不可并发修改同一请求或输入 lease。
`ExecuteAsync` 只有在请求进入安全终态后才完成；进入 `DrainUnknown` 时保持未完成，宿主只能通过状态/事件观察排空恢复，不能把 `R0015` 包装成 `RectificationResult` 或提交给任何消费者。`DrainAsync` 的超时只报告排空仍未证明，不得因此释放资源或制造终态。

### 6.2 状态

```text
Created → Validating → Accepted → WaitingForMap → Running → Publishing → Draining → Drained → ResourcesReleased → ResultPublished → Completed
Validating → Rejected/Failed（未接纳、无工作资源短路径）
             Running/WaitingForMap → CancelRequested → Draining → Drained → ResourcesReleased → Cancelled
             Running/WaitingForMap → DeadlineReached → Draining → Drained → ResourcesReleased → TimedOut
关闭前：Accepting → Quiescing → Draining → Drained → ResourcesReleased → Closed
             Draining → DrainUnknown（非终态、资源隔离）→ Draining（取得真实排空证据后）
```

`Completed` 只表示模块在安全排空并释放请求工作资源后产出了符合契约的派生结果；不代表业务合格。`Rejected` 表示输入/能力/资格前置条件不满足；`Failed` 表示执行或资源错误；`Cancelled`/`TimedOut` 表示没有发布成功载荷且已完成排空。`DrainUnknown` 不是 `RectificationTerminalState` 成员、不是错误终态，也不是可返回的 `RectificationResult.State`：它表示无法证明native、请求IO或观察器已结束，必须隔离仍可能访问资源的worker/lease，禁止发布 `ResultPublished`、禁止返回或消费 `Payload`，也禁止发出 `ResourcesReleased`。只有取得真实排空证据后，才能回到 `Draining`，再进入 `Drained → ResourcesReleased`，最后按原始原因进入 `Cancelled`、`TimedOut`、`Rejected` 或 `Failed`；在证据未取得前，该请求保持非终态。

`Draining` 包含native等待、发布前资格回读和请求观察器收尾。`Drained` 必须证明native、全部请求IO、观察循环及回调均已结束，此后不得启动新的请求IO；它不表示对象已Dispose。无法证明任一请求工作结束同样进入DrainUnknown，不能仅凭native返回发Drained。

首个纯 Core 切片只提供 ValidateRequest、FreezeInput、NormalizeCoordinates 和预算校验，不调用 ExecuteAsync，不返回 RectificationResult 或校正 Payload；换基返回 CoordinateNormalizationResult。C2 的模拟服务和后续 native 服务统一经过 Draining → Drained → ResourcesReleased；仅当无任何工作lease/IO/观察器时这三步是有证据的空步骤。取消检查点为接纳前、每个 ProbeBatchPoints 批次边界和发布前；期限用注入 TimeProvider 的单调时钟。后端缺失为 R0010，不把换基称作 Completed 校正。

### 6.3 事件顺序

事件Stage/Kind精确枚举见A.4。事件均携带 `RequestId`、实例 epoch、状态 revision 和时间戳；事件线程为模块后台通知线程，宿主负责切回 UI。

```text
Validated → Accepted → MapStarted/MapHit → OperationStarted
         → Progress* → OperationFinished → Draining
         → Drained → ResourcesReleased → ResultPublished → Terminal
         ↘ DrainUnknown（非终态、无 ResultPublished/Payload、资源保持隔离）
```

`OperationFinished` 只表示 native 调用或托管计算返回，不能使结果可消费。`ResultPublished` 必须发生在 `Drained` 和 `ResourcesReleased` 之后，且只针对最终会进入 `Completed` 的成功结果；已接纳失败先记 ExecutionFaulted，再 Draining；释放后才发 Rejected/Failed/Cancelled/TimedOut 终态。无法确认排空时只发 `DrainUnknown` 非终态并隔离资源；在该状态下不得发 `ResultPublished`、`Terminal` 或释放仍可能被 native 使用的 lease。只有排空证据恢复后才能发 `Drained`、`ResourcesReleased` 和对应终态。`Progress` 可合并、可丢弃；`ResultPublished` 和 `Terminal` 不可用进度替代。订阅者抛异常必须被隔离并记录诊断，不得阻塞 native 或修改终态。退订后迟到事件按 `RequestId + epoch` 丢弃。

接纳前的 `Rejected`（包括 layout、资格、预算、能力和重复 `RequestId`）不发 `MapStarted`、`OperationStarted`、`Draining` 或 `ResourcesReleased`，也不占用 native 资源；它只能返回拒绝结果和诊断。接纳前资产/资格IO也须结束并归还其临时资源才可返回拒绝；其等待超时不证明IO完成。`Accepted` 之后无论 map 创建、执行、复制还是发布前失败，都必须先发 `Draining`，取得全部请求工作真实排空证据后依次发 `Drained → ResourcesReleased → Terminal`。OperationFinished和后端局部DrainResult不替代请求级Drained。任何事件只携带身份、状态 revision、时间和诊断摘要，不携带 `Payload`、可变 map 或 frame lease。

## 7. 取消、超时、线程和资源

- 取消请求只阻止新工作并触发适配器安全停止；不声称 native 已停止。超时也不是强制释放信号。
- 先停止接收→发取消→等待HALCON/适配器及全部请求IO完成或可验证同步凭据→结束本请求资格观察器/回调并排空队列→Drained→释放map、临时图、帧lease和请求工作资源。无法在期限内证明任一工作结束时进入 `DrainUnknown/R0015` 非终态；隔离仍可能被native/IO/回调访问的worker和内存，禁止返回结果、发布成功载荷或强制归还悬空buffer。只有取得全部真实排空证据后才可继续释放；此状态对首个无native/IO的C1切片不适用。
- map 缓存内容不可变且按完整 key 共享；缓存命中不绕过当前资格检查。缓存有数量和字节上限，生成失败归还预占预算，淘汰不影响仍持有 lease 的任务。
- native 对象只在 `Rectification.AsunImage` 适配层创建和释放；Core、WPF、调用方不持有 `HObject/HImage/HTuple`。同一 native handle 不在多个并发任务间可变共享。
- `DisposeAsync`/关闭流程先进入 `Quiescing`，拒绝新请求，等待在途任务安全终态；进入 `DrainUnknown` 的任务保持隔离和非终态，不得因窗口关闭发出 `Closed`、释放 native/frame lease 或清理其资源。重复 Dispose 幂等；关闭后的新请求返回 `ModuleClosed`，未解决的排空任务仍由恢复 Owner 处理。
- 线程亲和性、HALCON全局初始化和 GPU/CPU 资源由适配器能力声明；本指导不假设可任意跨线程迁移或无限并行。

## 8. 错误码和恢复语义

错误码是稳定机器可读标识；本表不替代平台统一错误 Schema，正式编号接收时需映射到原 Owner。

| 错误码 | 语义 | 调用方处理 |
|---|---|---|
| `R0001 InvalidRequest` | ID、枚举、预算或必填字段非法 | 修正请求；不可重试同一无效载荷 |
| `R0002 FrameLayoutInvalid` | 尺寸/format/stride/offset/访问范围不合法 | 重新发布合法帧；不要调用 native |
| `R0003 FrameRevisionMismatch` | lease 与请求 revision 不一致 | 丢弃旧请求，重新绑定当前帧 |
| `R0004 CalibrationMissing` | 缺少资产、revision 或 hash | 由资产 Owner 提供完整闭包 |
| `R0005 CalibrationNotQualified` | 候选/过期/撤销/Unknown/条件越域 | 转资格流程或拒绝；不自动降级 |
| `R0006 LayoutNotApplicable` | 分辨率、ROI、binning、相机模型不匹配 | 生成新 map 或选择适配资产 |
| `R0007 CoordinateConventionMismatch` | row/column、center/corner、方向或单位不明 | 补齐坐标声明；不得猜测 |
| `R0008 MapInvalid` | map hash/结构/尺寸/邻域验证失败 | 删除该缓存项并重建；仍失败则人工处理 |
| `R0009 DomainInsufficient` | 输出存在未知/越界/插值支撑不足 | 收缩域、补充输入或拒绝量测 |
| `R0010 UnsupportedOperation` | 适配器不支持该格式/操作/边界策略 | 选择已登记能力；不能静默切算法 |
| `R0011 ResourceLimit` | 输出字节、缓存或并发额度不足 | 背压、缩小明确窗口；重新提交使用新 RequestId |
| `R0012 Cancelled` | 已取消且资源已排空 | 保留取消证据；不产生成功载荷 |
| `R0013 Timeout` | 达到预算并进入排空 | 只有排空证据成立后才返回 `TimedOut`；否则保持 `DrainUnknown` 非终态 |
| `R0014 NativeExecutionFailed` | AsunImage/HALCON 执行异常 | 记录适配器/算子/输入快照；不以 fallback 掩盖失败 |
| `R0015 DrainUnknown` | 无法证明native、请求IO或观察器已结束；仅作非终态状态/诊断标记 | 不返回 `RectificationResult`，不发布/消费 `Payload`，不发 `ResourcesReleased`；隔离资源并等待真实排空证据 |
| `R0016 ModuleClosed` | 实例已关闭或停止接收 | 创建新实例或等待宿主生命周期 |
| `R0017 VersionIncompatible` | 模块契约、资产或 map schema 不兼容 | 走显式迁移/回退；不可忽略版本字段 |
| `R0018 DuplicateRequest` | 当前实例 epoch 已使用该 RequestId | 查询原 epoch，不重跑；历史回放使用新 ID |
| `R0019 StatusUnavailable` | 查询未知 ID、错误 epoch、低于查询水位或已淘汰 | 按附录 A.2 的 QueryCode 处理，不创建任务 |
| `R0021 CacheMiss` | RequireHit 未命中完整 key | 以新请求选择 ReadThrough 或 Disabled |
| `R0022 CacheStoreFailed` | 缓存发布失败或远端回执未知 | 查询原 PublishId；不以 native 错误掩盖 IO 结果 |
| `R0020 SourceWindowUnavailable` | 虚拟帧不足/截断/断连或CopyRow不可用 | 端口不提供最近窗口；revision/hash错配单独R0003；宿主重新绑定或显式缩窗 |

同一 RequestId 不重新提交；使用 GetStatusAsync 查询原 epoch。历史重放用新 ID，可保留同一 CalculationIdentity；DrainUnknown 未解决前不重跑同一计算闭包。模块不提交业务事实。缓存 PublishId 的幂等与 Execute RequestId 的禁止重复分别定义。

## 9. 坐标、映射和有效域规则

平台数学以 `(u,v)=(column,row)` 的像素中心列向量为语义；HALCON 适配器可能使用 `(row,column)` 和 corner 约定，必须按 `PKG-007` 的 `S`/`C` 换基公式显式转换。中心点缩放反例 `(u,v)=(2,3)` 放大二倍应得到 `(4,6)`；漏掉半像素会得到 `(4.5,6.5)`，该反例必须进入测试。

映射方向必须写清 `source → target`。原始图域传播至少执行：

1. 将输出像素的映射坐标计算到 source。
2. 按所选插值核检查所有支撑邻点都在 source 可访问范围和 `InputDomain` 内。
3. 对不满足条件的输出点标记无效或按策略收缩 domain；`FillForDisplay` 只能生成显示派生层，不能供识别、定位、拼接或计量的正式计算。
4. 记录有效比例、边界收缩、域洞和输入来源；不把未知点写成 0，也不把 domain 忽略的算子当作安全证明。

本模块的畸变映射只表达 `CameraPixel → CorrectedPixel`。若调用链还需转换到产品坐标，必须由对应配准/坐标 Owner 提供独立的 `CorrectedPixel → ProductFrame` 变换；组合映射时仍须保留各阶段的方向、artifact 身份和版本，不能折叠成失去来源的裸矩阵，也不能把机台绝对位置直接当作 `ProductFrame`。畸变校正通过不代表产品坐标变换有效。

map key唯一字段见A.5，绑定parent布局/ROI/binning、完整资产身份、source/target窗口、局部参数hash及schema/算法/后端版本。几何map不含本次source像素hash/域，因同布局资产可复用；SafeExecutionMap及Domain每次按冻结Input.Domain重新派生，provenance必须含source内容hash。旧map不能因宽高相同跨窗口/配置复用。

## 10. 可选 WPF/UI 契约

### 10.1 消费者、公开控件和所有权

识别/定位工具只嵌入点/轮廓结果投影；拼接/计量工具嵌入图像与窗口对比。两者使用同一个RectificationControl，不增加模块主页、产品导航或业务放行页面。控件仅可选，所有校验/计算仍为Core公开接口。控件工程为net10.0-windows/WPF，只引用Core、本机DevExpress25.2.3和宿主注入的只读预览端口；不引用AsunImage/native类型。

```csharp
public enum BindingCode { Bound, AlreadyBound, InvalidBinding, Unbound, PendingDrain, Cancelled, Closed }
public sealed record RectificationBinding(
    string BindingId, IRectificationEngine Engine, RectificationRequest InitialDraft,
    IRectificationPreviewPort Preview, IRectificationLanguagePort Language,
    RectificationUiPermissions Permissions, long Epoch);
public sealed record RectificationUiPermissions(bool CanEditDraft, bool CanExecute, bool CanOfferCandidate);
public sealed record BindingResult(BindingCode Code, IReadOnlyList<string> PendingRequests, RectificationError? Error);
public sealed record CandidateOffer(string BindingId, string RequestId, long Epoch,
    ContentHash FrozenDraftHash, RectificationResult Result);
public enum CandidateOfferCode { Accepted, Rejected, Stale }
public interface IRectificationPreviewPort
{
    long MaxRetainedBytes { get; }
    ValueTask<PreviewPairResult> OpenAsync(PreviewQuery query, CancellationToken token);
    ValueTask<CandidateOfferCode> OfferAsync(CandidateOffer candidate, CancellationToken token);
    ValueTask<PreviewProjectionResult> ProjectAsync(PreviewProjectionQuery query, CancellationToken token);
}
public interface IRectificationLanguagePort
{
    string CultureName { get; }
    string GetText(string resourceKey);
    event EventHandler CultureChanged;
}
// namespace Asun.Modules.ImageRectification.Wpf
public sealed class RectificationControl : System.Windows.Controls.UserControl
{
    public ValueTask<BindingResult> BindAsync(RectificationBinding binding, CancellationToken token);
    public ValueTask<BindingResult> UnbindAsync(TimeSpan timeout, CancellationToken token);
    public ValueTask<BindingResult> CloseAsync(TimeSpan timeout, CancellationToken token);
    public ValidationResult UpdateDraft(RectificationRequest draft);
    public void UpdatePermissions(RectificationUiPermissions permissions);
}
```

PreviewProjectionQuery=(BindingId:string,RequestId:string,Epoch:long,MapHash:ContentHash?,Point:PixelPoint,Direction:PreviewProjectionDirection)；PreviewProjectionDirection=SourceToCorrected/CorrectedToSource；PreviewProjectionResult=(Point:PixelPoint?,IsValid:bool,Error:RectificationError?)，无映射/越域时Point=null、IsValid=false，方向/版本错配Error=R0007/R0003。Host投影端口复用该冻结结果的map或通过同一Core点路径计算，禁止另写UI视觉算法；点/XLD的MapHash为null则以Trace.Identity校验。有限查询deadline沿用当前草稿Timeout，不得阻塞Dispatcher。

PreviewQuery=(BindingId:string,RequestId:string,Epoch:long,Source:InputFrameDescriptor,Result:RectificationResult?,OutputWindow:PixelRect,MaxHeldBytes:long)；PreviewPairResult=(Source:IPreviewLease?,Corrected:IPreviewLease?,Error:RectificationError?)。IPreviewLease:IAsyncDisposable公开Projection:System.Windows.Media.ImageSource、FrameHash:ContentHash、Window:PixelRect、Domain:ValidityDomain、IsDisplayOnly:bool、AllocationId:Guid、AllocationBytes:long；图像由宿主已有视口/帧显示适配器提供，控件不写第二套视觉算法。Preview.MaxRetainedBytes必须为正且预先预约；MaxHeldBytes为本次剩余预览额度，端口在分配前按Source/Corrected/工作副本同时存活实际容量核对，超额返回R0011且不启动IO；allocation相同Id只计一次，关闭/Dispose未完成不减额度。原图可单独成功，未Completed时Corrected=null；校正预览必须匹配RequestId/epoch/sourcehash/maphash和窗口，否则不显示为当前结果。显示填洞仅IsDisplayOnly层，叠加清楚纹理且禁止应用为计算输入。

Bind仅在未绑定/未Closed时接受非空BindingId、epoch与Engine一致的输入；重复相同BindingId/引擎/epoch返回AlreadyBound且不重复订阅，不同绑定先Unbind。共享Engine和注入端口均借用，控件绝不Dispose它们；仅持有自己发起的请求ID、预览lease和事件/语言订阅。权限是宿主投影，宿主以Dispatcher上的UpdatePermissions传入完整新权限快照；权限变化立即禁用相应命令并使旧候选不可应用，宿主OfferAsync再次检查业务权限。

Bind/Unbind/Close/UpdateDraft在控件Dispatcher调用，异步IO/native只通过Core后台执行，不把Wait阻塞Dispatcher；Timeout取1ms..24h，非法值InvalidBinding/R0001。取消绑定等待返回Cancelled，保留原绑定状态；Unbind/Close等待取消只取消等待，不释放未排空资源。

Unbind依次锁住新命令→取消本控件预览IO/自有执行请求→有限等待这些请求安全终态→释放预览lease/解除观察和语言订阅→清草稿与当前候选。未排空返回PendingDrain+原ID，保留绑定恢复入口与引擎Owner关联，不声明Unbound；token只取消等待。Close先同样Unbind，完成后Closed；PendingDrain时保持“排空状态未确认”，不声明Closed、不释放native/输入资源。WPF卸载按下一段作有确认的根Owner移交，不能因不可见使其完成。重新显示按原BindingId/epoch查询原ID；不重提交。多个控件共用Engine时只处理自身请求，不调用全局Drain或Dispose。

绑定前宿主为本Binding在§11.2式进程根中预约控件恢复槽与明确byte额度：至少覆盖InitialDraft的Limits.MaxManagedBytes、尚可持有的一份Budget.MaxOutputBytes、预览端口声明的两lease峰值与原Task/诊断容量；超额Bind返回InvalidBinding/R0011，不先读预览。预览端口必须报告真实lease/allocation上界；Unknown不启动预览（Core无UI执行不受阻）。控件每次Open/Project/Offer/Execute及结果/preview Dispose前在槽内登记单次AsTask和强引用，再作有限观察。Unloaded在Dispatcher先禁命令/停止自有新请求，建立移交包（BindingId/epoch/草稿、借用Engine、全部原Task、Result/Payload、Source/Corrected preview lease与各自Dispose Task、取消源、已预约bytes）；宿主同一root门完整登记并回ACK后，控件才清本地强引用/解除UI事件，宿主槽接住迟到结果/迟到preview并在借用消费者真实结束后各Dispose一次。未ACK仍在原绑定根持有包，返回PendingDrain并保留预算；不能只写RequestId给恢复者，也不能退订视为lease释放。共享Engine归宿主既有Engine根，不在控件恢复支路Dispose；已Accepted的Offer长期结果移交另需对同一Result/Payload/预算确认，回执超时保留原Offer Task和原Owner，查询/原Task回执确认前不重复Offer或Dispose，避免双释放。控件Invisible/Unloaded不准减预算；只有所有原任务退出、lease/候选Dispose成功或接收ACK完成后才归还对应额度。UI-R05补移交无ACK/满根槽/迟到preview/consumer未结束/preview Dispose失败断言；本轮未运行WPF。

该恢复ACK由WPF内部BindingRoots登记门实现，属于宿主嵌入控件的私有生命周期实现，不新增公开RootOwner/恢复协议。BindingRoots为进程寿命强引用表，最多8个活跃/恢复绑定；成功BindAsync之前先登记控件对象与完整Binding/bytes，Bound即初始接收确认，槽满InvalidBinding/R0011且不启动任务。每个Task/lease/result先写该根再有限等待，因此卸载移交仍在同一根中原子更新RootStage=Recovering并回内部ACK；Host已有进程根强持控件/BindingRoots服务至所有绑定安全完结。Bind/Unbind调用结束、控件离开视觉树不删除该根；无ACK/故障槽保持控件对象及内部任务字段，清本地引用必须以根包已强持为前提。恢复只关闭本绑定lease/候选，不关闭共享Engine或端口。宿主维护循环按原BindingId调用已有CloseAsync作有限观察，不创建替代控件/重复请求，完成后才释放Host控件强引用。

### 10.2 参数、预览、应用和恢复

| 动作 | 输入/启用条件 | Core/宿主责任与反馈 |
|---|---|---|
| 校验 | 已绑定、权限可读、草稿完整 | ValidateRequest+RecommendExecution；字段错误内联显示单位/合法范围，不改已资格CamParam |
| 编辑参数 | CanEditDraft，非排空未知 | 只编辑Operation的合法载荷、OutputWindow、Boundary/Cache/Budget/Timeout；来源身份、资产revision、完整目标模型/尺度为只读。UpdateDraft只在完整副本合法时替换草稿；非法副本仍可显示输入错误但不可执行 |
| 预览/执行 | CanExecute、校验通过、无本控件排空未知 | 冻结草稿hash并生成新RequestId，走同一ExecuteAsync，不静默另选算法。Image结果可预览；Points/Contour以表和覆盖层投影，不生成整图 |
| 取消 | 当前自有请求未终态 | 发token取消，显示CancelRequested/Draining；按钮不表示已完成；成功发布前的取消阻止Offer |
| 应用候选 | CanOfferCandidate、当前Completed、草稿hash未变、来源/资产/权限仍有效 | 仅调用宿主OfferAsync；宿主负责保存配置或消费派生结果并重核资格，不提交产品PASS/放行。Accepted后结果Owner由宿主接管；Rejected/Stale时控件保留只读候选供诊断 |
| 恢复草稿 | 非执行中的只读冻结快照存在 | 恢复最近一次显式已接收草稿；只恢复参数，不重跑、不激活资产、不恢复旧资格 |
| 恢复布局 | 已绑定 | 宿主保存的同schema布局恢复失败则恢复默认面板组合；不得丢失取消/状态命令 |
| 重试 | 原请求已安全终态，必要输入已修正 | 新ID、新冻结草稿；DrainUnknown只能查询原请求，不能“重试成功”掩盖未释放资源 |

运行中改参只生成下一次草稿，现有请求保持冻结闭包；旧结果到达可放入历史摘要，但草稿hash不同即标“参数已更改”，禁用应用。QualificationNotice撤销/过期/失联，立即清当前候选可应用标记，显示“标定资格不可用”，原图仍可看，候选不变生产事实。普通Progress不抢焦点；正式状态/错误按revision顺序处理。事件不含Payload，控件仅从自己的ExecuteAsync返回取得结果；无订阅者执行也能完成。

### 10.3 紧凑DevExpress组合与联动

复用本轮已读DevExpress25.2官方文档：[`DockLayoutManager`](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager)、[`GridControl`](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl)、[`PropertyGridControl`](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl)、[`SuperTip`](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip)。25.2.3本机程序集直接引用；已有资料证明docking/布局恢复、数据绑定/虚拟列表、property绑定编辑器与SuperTip可组合，本轮不重复下载安装或核许可证。API实际映射若有版本歧义再查dxdocs（本会话未提供该工具时复用官方资料），不能据文档称真实WPF验证通过。

DockLayoutManager内主图和对比图同组，参数面板置右侧，诊断Grid置底部可折叠；核心身份/状态/取消常驻顶栏和底部状态行，不藏入浮动窗或菜单。正常图像模式默认原图/校正左右对比，共用缩放比例，但中心坐标通过带版本Mapping转换；映射无效则取消联动并提示“当前位置无有效映射”，不能把同屏坐标当同物理点。点/轮廓模式主图只显示来源与候选覆盖，Grid按原输入Index保序；选一行高亮对应点/轮廓，选域诊断行高亮域洞，不改变有效域。map网格是诊断覆盖开关，禁用区域纹理与图例始终可辨。

PropertyGrid只绑定独立Draft对象，只读来源/资格信息与可编辑窗口/预算分组展示；高级预算折叠，执行前内联摘要显示完整/窗口规模和预算拒绝原因。Grid绑定不可变摘要集合，启用虚拟化和筛选，身份/Index固定可见；筛选只是显示，不删源点或回写结果。SuperTip由资源键生成标题、单位、边界与恢复动作，不显示整段native异常；错误详情展开才显示诊断键/算子版本。

默认主题由宿主提供；采用8px布局步长、同一字体层级和图标线宽，状态不只靠颜色：运行文字+图标、无效域纹理、失败诊断键并列。当前选择与过期候选明确区分。布局schema为rectification-ui/1，恢复只白名单内面板ID，坏schema回默认布局，禁止外来布局执行命令。该控件内没有全局语言/主题切换入口。

### 10.4 三语、1920×1080和验收断言

只使用固定1920×1080验证视口，不改系统显示设置，不运行390/1500或其他分辨率矩阵；扣除任务栏、边框、宿主标题和状态行后分配可用client区域。默认主图区占剩余宽度70%、右参数30%，诊断展开占client高度22%，顶栏/底栏均48 DIP，面板折叠时释放给图像；这些是默认控件布局值，不能挤掉状态或取消。当前OS DPI按实际记录，WPF采用DIP，长英文用换行/面板滚动处理，不截断关键身份/错误，不缩成难读字号。

键盘顺序固定：来源摘要→操作/输入→窗口字段→校验→执行→取消→应用候选→图像→结果Grid→诊断。F6在参数/图像/结果/诊断之间循环，Esc只取消本控件任务并保留焦点，Ctrl+Enter仅在执行可用且编辑器已提交合法值时执行；Enter在Grid/PropertyGrid保持其普通编辑含义。运行与语言切换不抢焦点，错误时定位首个错误字段，关闭回宿主触发控件焦点。

UIA的AutomationId固定BindingId、SourceFrame、CalibrationRevision、Operation、OutputWindow、Validate、Execute、Cancel、OfferCandidate、RestoreDraft、RestoreLayout、State、ValidDomain、ErrorCode；面板/列表按职责公开Selection/Table/Value等适用模式，图像覆盖提供文本等价（输入Index、坐标、域内状态），无假可编辑模式。LanguagePort接受zh-CN/zh-TW/en-US并动态刷新所有标签/标题/枚举/错误/诊断/恢复/SuperTip/AutomationName；状态如“排空状态未确认 / 排空狀態未確認 / Resource drain unconfirmed”，动作如“应用候选 / 套用候選 / Apply candidate”。内部key、hash和单位不随语言变。

UI-R01：三语切换保留草稿/选中行/焦点/运行ID，关键命令可见无重叠。UI-R02：固定视口和当前DPI下原图/校正/域纹理可辨，主题统一、层级清楚、图标/间距一致；功能与视觉两项各自验收。UI-R03：全键盘完成校验→执行→取消→查询→恢复，UIA读取真实状态和错误。UI-R04：改参/撤销/迟到/双控件共享引擎时旧结果不应用、不取消另一消费者。UI-R05：Close超时显示PendingDrain，再获排空证据可Unbound/Closed；Display lease释放且native所有权不泄漏。UI-R06：布局坏schema/预览失败/SuperTip长英文有明确恢复，无隐藏初始化或自动参数替换。这些是将来真实WPF断言，本轮未执行。

### 10.5 实际控件接线、图像操作和语言资源

本轮补查DevExpress官方网页返回403；没有dxdocs可调用，改读本机`C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`的Docking/PropertyGrid/Grid/Core同名`DevExpress.Xpf.*.v25.2.xml`公共文档，Docking程序集FileVersion=25.2.3.0。这只确定下面公开成员及组件组合，不检查授权、不证明真实WPF行为。已有效的§10.3官方资料直接复用，不下载依赖。

| 区域 | 实际组合与绑定方式 |
|---|---|
| 布局 | 顶层WPF Grid固定顶栏/底栏，中央DockLayoutManager.LayoutRoot为LayoutGroup。主图组水平分为Source/Corrected两个LayoutPanel，右Parameters、底Results/Diagnostics；LayoutGroup.Orientation及BaseLayoutItem.ItemWidth明确布局方向/宽度。各panel用稳定Name（WPF Name）、BaseLayoutItem.Caption语言绑定，主图/状态相关项AllowClose=false/AllowFloat=false，取消按钮在外层顶栏；可折叠面板不得带走状态命令 |
| 参数 | PropertyGridControl.SelectedObject绑定控件私有DraftEditor，不直接改RectificationRequest/资产。DraftEditor仅私有UI投影，路径字段由本表与§10.2白名单定义，不能反向扩展Core DTO。ShowProperties=ShowPropertiesMode.WithPropertyDefinitions，只显式PropertyDefinitions；PropertyDefinitionBase.Path指定Operation/OutputWindow.*等已批准字段，Header绑定语言键，IsReadOnly由CanEditDraft/只读来源决定。输入留在editor，失焦或显式校验后生成完整副本，唯一ValidateRequest/UpdateDraft决定能否替换；没有可见字段暗改CamParam。高级Budget/Timeout与Cache单独折叠，合法范围按CoreLimits与当前Profile投影，不用PropertyGrid默认数值推物理值 |
| 结果与诊断 | GridControl.ItemsSource绑定本控件有界只读行集合，DataControlBase.CurrentItem与图上Index双向选择；GridColumn.FieldName绑定稳定Index/坐标/状态字段，BaseColumn.Header语言绑定，BaseColumn.Fixed固定Index，TableView继承的DataViewBase.AllowEditing=false。筛选/排序只是显示投影，底层Index保持原顺序，批量选中不删除点/轮廓、不触发重跑。虚拟化只减少视觉树，不降低实际结果内存预算 |
| 图像 | 宿主IPreviewLease.Projection为只读WPF ImageSource；本控件用Image+clip容器与Canvas诊断覆盖，只有屏幕ScaleTransform/TranslateTransform，不能生成计算map。鼠标滚轮围绕光标缩放，拖拽平移，双击适应窗口；工具栏适应/1:1/联动/有效域开关一直可达。1:1是1源像素→1DIP的显示比例，当前DPI下不冒充物理尺寸；图上坐标转回完整像素中心后才ProjectAsync。左右pan/zoom事件防回环，每视图变更仅发一次联动查询，前一原Task未结束不继续排队 |
| SuperTip | 使用Core.SuperTip.Items及SuperTipItem.Content，作为WPF ToolTip内容绑定到相应命令/参数；标题、单位、限制和恢复动作来自同一资源表。不假设不存在的SuperTipService方法，不把长native异常当提示正文。读取权限不足/预算拒绝/域无效均有可见短说明；重要命令不藏菜单 |
| 保存/恢复布局 | DockLayoutManager.SaveLayoutToStream/RestoreLayoutFromStream仅用于宿主本进程保存、同组件版本的可信bytes，外层先验证rectification-ui/1与白名单panel Names及有界长度。调用前冻结当前panel配置，恢复异常时重建本节默认布局，取消/身份栏始终外置。不加载外来/用户任意XML；官方文档明确反序列化风险，不把白名单外的原始布局传给Restore。模块无产品配置写入，保存地点/权限由宿主决定 |

Preview.ProjectAsync有明确的来源闭包：宿主预览适配器持有原冻结请求/资产引用和只读资格，不靠全局current asset。SourceToCorrected使用原CamParamIn→Out，CorrectedToSource只用原Out→In，并按相应完整画布/支撑域检查；采用同一26.05点映射语义或coordinate-geometry已经公开且精确绑定此相机参数的边，不从量化map任意反演。输入Point按Direction为对应画布的CenterRowColumn，成功输出同约定的另一个完整画布坐标；控件只做视图像素中心/窗口原点换基。尚无该适配能力则IsValid=false/Point=null/R0010，关闭联动并显示具体短说明，不能假联动。无法恢复的preview IO/Dispose仍走BindingRoots原Task收尾，图像拖动和卸载不减lease预算。

状态与语言资源的完整覆盖规则：控件资源命名空间`rectification.*`，下面suffix前统一加该前缀；标题/字段/动作/状态/枚举/错误/SuperTip/AutomationName全部按此资源投影，Code/hash/版本/单位值保持原样。模块WPF程序集内保留三份默认资源，LanguagePort.GetText可提供宿主术语覆盖；未知键/空串回落模块同culture默认，未知culture回落zh-CN并保留原任务，不在控件放语言切换器。表中英文与繁体按原词义，数字编辑按CultureName解析有限值，canonical身份和诊断数值保持InvariantCulture，语言切换不能改参数位模式。CultureChanged在Dispatcher刷新文本/列头/提示/UIA，保留草稿、选择、焦点和原任务；不更新运行期快照。

| suffix/使用对象 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title | 畸变校正 | 畸變校正 | Distortion correction |
| Source / Corrected | 原图 / 校正图 | 原圖 / 校正圖 | Source / Corrected |
| Parameters / Results / Diagnostics | 参数 / 结果 / 诊断 | 參數 / 結果 / 診斷 | Parameters / Results / Diagnostics |
| Validate / Execute / Cancel | 校验 / 执行 / 取消 | 檢查 / 執行 / 取消 | Validate / Run / Cancel |
| OfferCandidate / RestoreDraft / RestoreLayout | 应用候选 / 恢复参数 / 恢复布局 | 套用候選 / 還原參數 / 還原版面 | Apply candidate / Restore parameters / Restore layout |
| QueryOriginal / Retry | 查询原请求 / 重试 | 查詢原請求 / 重試 | Query original request / Retry |
| Fit / ActualSize / LinkViews / ShowDomain | 适应窗口 / 1:1 / 联动 / 有效域 | 符合視窗 / 1:1 / 連動 / 有效區域 | Fit / 1:1 / Link views / Valid domain |
| Field.SourceFrame / Field.Revision / Field.Asset | 来源帧 / 修订 / 标定资产 | 來源影像 / 修訂 / 校正資產 | Source frame / Revision / Calibration asset |
| Field.Operation / Field.OutputWindow / Field.Row / Field.Column | 操作 / 输出窗口 / 行 / 列 | 操作 / 輸出視窗 / 列座標 / 行座標 | Operation / Output window / Row / Column |
| Field.Width / Field.Height / Field.Index / Field.Coordinate | 宽 / 高 / 序号 / 坐标 | 寬 / 高 / 序號 / 座標 | Width / Height / Index / Coordinate |
| Field.Boundary / Field.Cache / Field.Timeout | 边界策略 / 缓存 / 超时 | 邊界策略 / 快取 / 逾時 | Boundary policy / Cache / Timeout |
| Field.Budget / Field.OutputBytes / Field.WorkingBytes / Field.NativeBytes / Field.CacheBytes | 预算 / 输出内存 / 工作内存 / 原生内存 / 缓存内存 | 預算 / 輸出記憶體 / 工作記憶體 / 原生記憶體 / 快取記憶體 | Budget / Output memory / Working memory / Native memory / Cache memory |
| Field.Concurrent / Field.ProbeBatch / Field.DomainSegments | 并发上限 / 探测批量 / 域段上限 | 並行上限 / 探測批量 / 區域段數上限 | Concurrency limit / Probe batch / Domain segment limit |
| Field.ValidDomain / Field.Qualification / Field.Version / Field.ErrorCode | 有效域 / 标定资格 / 版本 / 错误码 | 有效區域 / 校正資格 / 版本 / 錯誤碼 | Valid domain / Qualification / Version / Error code |
| Image / Point / Points / Contour | 图像 / 单点 / 点集 / 轮廓 | 影像 / 單點 / 點集 / 輪廓 | Image / Point / Points / Contour |
| Byte / UInt16 / Int16 / Float32 | 8位无符号 / 16位无符号 / 16位有符号 / 32位浮点 | 8位無符號 / 16位無符號 / 16位有符號 / 32位浮點 | Unsigned 8-bit / Unsigned 16-bit / Signed 16-bit / Float 32-bit |
| CenterRowColumn / CenterColumnRow / CornerRowColumn | 像素中心，行列 / 像素中心，列行 / 像素角点，行列 | 像素中心，列行座標 / 像素中心，行列座標 / 像素角點，列行座標 | Pixel center, row-column / Pixel center, column-row / Pixel corner, row-column |
| RejectIfUnsupported / ConservativeValidDomain | 域不足则拒绝 / 保留尺寸并标记无效域 | 區域不足時拒絕 / 保留尺寸並標示無效區域 | Reject unsupported domain / Keep size and mark invalid domain |
| Disabled / ReadThrough / RequireHit | 不使用缓存 / 读缓存并写入 / 必须命中缓存 | 不使用快取 / 讀取並寫入快取 / 必須命中快取 | Cache disabled / Read and populate cache / Cache hit required |
| Bilinear / AllOrNothing | 双线性 / 整批成功或拒绝 | 雙線性 / 整批成功或拒絕 | Bilinear / All or nothing |
| Full / Empty / RowSegments / Unknown | 全域 / 空域 / 行段域 / 未知 | 完整區域 / 空區域 / 列段區域 / 未知 | Full domain / Empty domain / Row segments / Unknown |
| Qualified / Suspended / Revoked / Expired | 有效 / 已暂停 / 已撤销 / 已过期 | 有效 / 已暫停 / 已撤銷 / 已過期 | Qualified / Suspended / Revoked / Expired |
| Created / Validating / Validated / Accepted | 已创建 / 正在校验 / 已校验 / 已接纳 | 已建立 / 檢查中 / 已檢查 / 已受理 | Created / Validating / Validated / Accepted |
| WaitingForMap / MapStarted / MapHit | 等待映射 / 正在生成映射 / 已读取缓存 | 等待映射 / 產生映射中 / 已讀取快取 | Waiting for map / Generating map / Cache hit |
| Running / Publishing / OperationStarted / OperationFinished | 正在计算 / 正在封存 / 计算已开始 / 计算已返回 | 計算中 / 封存中 / 計算已開始 / 計算已返回 | Running / Sealing result / Operation started / Operation returned |
| CancelRequested / DeadlineReached | 正在取消 / 已到超时期限 | 取消中 / 已到逾時期限 | Cancelling / Deadline reached |
| Draining / DrainUnknown / Drained | 正在排空 / 排空状态未确认 / 已排空 | 排空中 / 排空狀態未確認 / 已排空 | Draining / Resource drain unconfirmed / Drained |
| ResourcesReleased / ResultPublished / Terminal | 工作资源已归还 / 候选已返回 / 请求已结束 | 工作資源已歸還 / 候選已返回 / 請求已結束 | Working resources released / Candidate returned / Request ended |
| Completed / Rejected / Failed / ExecutionFaulted / Cancelled / TimedOut | 已完成 / 已拒绝 / 失败 / 计算异常 / 已取消 / 已超时 | 已完成 / 已拒絕 / 失敗 / 計算異常 / 已取消 / 已逾時 | Completed / Rejected / Failed / Execution fault / Cancelled / Timed out |
| Accepting / Quiescing / Closed | 可接收请求 / 正在关闭 / 已关闭 | 可受理請求 / 關閉中 / 已關閉 | Accepting requests / Closing / Closed |
| Bound / AlreadyBound / InvalidBinding / Unbound / PendingDrain | 已绑定 / 已绑定 / 绑定无效 / 已解绑 / 等待排空 | 已繫結 / 已繫結 / 繫結無效 / 已解除繫結 / 等待排空 | Bound / Already bound / Invalid binding / Unbound / Drain pending |
| Stale / DraftChanged / QualificationUnavailable / MappingUnavailable / PermissionDenied | 候选已过期 / 参数已更改 / 标定资格不可用 / 当前位置无有效映射 / 无操作权限 | 候選已過期 / 參數已變更 / 校正資格不可用 / 此位置無有效映射 / 無操作權限 | Candidate is stale / Parameters changed / Qualification unavailable / No valid mapping here / Permission denied |
| Query.Found / Query.UnknownRequest / Query.EpochMismatch / Query.RevisionNotReached / Query.Evicted / Query.InvalidQuery / Query.ModuleClosed | 已找到 / 未知请求 / 实例不匹配 / 状态修订未到达 / 状态已淘汰 / 查询无效 / 实例已关闭 | 已找到 / 未知請求 / 執行個體不符 / 狀態修訂尚未到達 / 狀態已移除 / 查詢無效 / 執行個體已關閉 | Found / Unknown request / Instance mismatch / State revision not reached / State evicted / Invalid query / Instance closed |
| Store.Found / Store.NotFound / Store.Published / Store.Invalidated / Store.Conflict / Store.Unknown / Store.Failed | 缓存命中 / 缓存未命中 / 缓存已发布 / 缓存已失效 / 回执冲突 / 回执未确认 / 缓存操作失败 | 快取命中 / 快取未命中 / 快取已發布 / 快取已失效 / 回執衝突 / 回執未確認 / 快取操作失敗 | Cache hit / Cache miss / Cache published / Cache invalidated / Receipt conflict / Receipt unconfirmed / Cache operation failed |
| Advice / AdviceUnavailable / NotEvaluated / DisplayOnly | 预算建议 / 无可用建议 / 尚未评价 / 仅供显示 | 預算建議 / 無可用建議 / 尚未評估 / 僅供顯示 | Budget suggestion / No suggestion available / Not evaluated / Display only |
| Tip.Window / Tip.Budget / Tip.Apply / Tip.Close | 窗口使用完整目标坐标，不改变物理尺度。 / 超过预算时缩小明确窗口或调整宿主额度。 / 仅移交候选，宿主仍须核对资格。 / 未排空时保留原任务，查询后继续关闭。 | 視窗使用完整目標座標，不改變物理尺度。 / 超出預算時縮小明確視窗或調整主機額度。 / 僅移交候選，主機仍須核對資格。 / 尚未排空時保留原工作，查詢後繼續關閉。 | Windows use full target coordinates; physical scale stays fixed. / Reduce the explicit window or revise the host budget. / Transfers a candidate; the host must check qualification. / Keep the original task until drained, then continue closing. |

表中以`/`并列的suffix与文字按同一顺序一一展开成独立资源，不将斜线组合显示为一个标签。Field.SourceWindow/PrincipalPoint/Scope/DomainHash/MapHash/ValidRatio/OutputDomain分别为“源窗口/主点/适用范围/域摘要/映射摘要/有效比例/输出域”、“來源視窗/主點/適用範圍/區域摘要/映射摘要/有效比例/輸出區域”、“Source window/Principal point/Scope/Domain hash/Map hash/Valid ratio/Output domain”；InputDomainIntersectionAndKernelSupport枚举文案为“来源域与插值支撑交集/來源區域與插值支援交集/Source domain and interpolation support intersection”。Field.Row/Column在繁体采用明确“列座標/行座標”，值旁固定显示`row/column`机器轴名避免地区用语换轴；不会随语言交换数值。查询Cancelled/TimedOut、候选Accepted/Rejected复用同名通用suffix；事件StateChanged只显示对应Stage的资源，不另造状态。所有Direction/Mapping标签显示“相机像素→校正像素 / 相機像素→校正像素 / Camera pixel→corrected pixel”，Preview方向用Source/Corrected组合箭头。单位`px/byte/ms`与`row/column`为不变技术记号，SuperTip正文使用本表自然语言。

每个Error.MessageKey固定`rectification.Error.Rxxxx`；正文与恢复用下表一条自然语句，字段和DiagnosticKey另外显示（未知诊断key保留机器标识并用Diagnostics标题，不直译native异常）。不添加编号外的“成功但有误差”错误类型。

| 错误资源 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Error.R0001 | 请求无效，修正标出的字段。 | 請求無效，請修正標示欄位。 | Invalid request. Correct the marked fields. |
| Error.R0002 | 帧布局无效，重新绑定合法来源。 | 影像配置無效，重新繫結有效來源。 | Invalid frame layout. Bind a valid source. |
| Error.R0003 | 来源修订不匹配，重新绑定当前帧。 | 來源修訂不符，重新繫結目前影像。 | Source revision mismatch. Bind the current frame. |
| Error.R0004 | 缺少标定资产，提供准确引用。 | 缺少校正資產，提供正確引用。 | Calibration asset missing. Provide its exact reference. |
| Error.R0005 | 标定资格不可用，核对资格状态。 | 校正資格無效，核對資格狀態。 | Qualification unavailable. Check its status. |
| Error.R0006 | 当前布局不适用，核对资产范围。 | 目前配置不適用，核對資產範圍。 | Layout is outside the asset scope. Check the asset. |
| Error.R0007 | 坐标约定不匹配，核对轴与原点。 | 座標慣例不符，核對軸向與原點。 | Coordinate convention mismatch. Check axes and origin. |
| Error.R0008 | 映射无效，隔离原缓存后重新生成。 | 映射無效，隔離原快取後重新產生。 | Invalid map. Isolate the cached entry before regeneration. |
| Error.R0009 | 有效域不足，缩小窗口或补充来源。 | 有效區域不足，縮小視窗或補齊來源。 | Insufficient valid domain. Reduce the window or supply the source. |
| Error.R0010 | 当前适配器不支持此操作。 | 目前配接器不支援此操作。 | This adapter does not support the operation. |
| Error.R0011 | 资源额度不足，缩小窗口或调整额度。 | 資源額度不足，縮小視窗或調整額度。 | Resource limit reached. Reduce the window or revise the budget. |
| Error.R0012 | 操作已取消，核对原请求状态。 | 操作已取消，核對原請求狀態。 | Operation cancelled. Check the original request status. |
| Error.R0013 | 请求已超时，等待原任务安全排空。 | 請求已逾時，等待原工作安全排空。 | Request timed out. Wait for the original task to drain. |
| Error.R0014 | 计算失败，查看诊断后重试。 | 計算失敗，檢視診斷後重試。 | Calculation failed. Check diagnostics before retrying. |
| Error.R0015 | 排空状态未确认，查询原请求。 | 排空狀態未確認，查詢原請求。 | Resource drain unconfirmed. Query the original request. |
| Error.R0016 | 实例正在关闭或已关闭。 | 執行個體正在關閉或已關閉。 | The instance is closing or closed. |
| Error.R0017 | 版本不兼容，使用明确的迁移或回退。 | 版本不相容，使用明確的移轉或回復方案。 | Version incompatible. Use an explicit migration or rollback. |
| Error.R0018 | 请求已提交，查询原实例和请求。 | 請求已提交，查詢原執行個體與請求。 | Request already submitted. Query the original instance and request. |
| Error.R0019 | 无法读取请求状态，核对原请求身份。 | 無法讀取請求狀態，核對原請求識別。 | Request status unavailable. Check the original request identity. |
| Error.R0020 | 来源窗口不可用，补齐原帧或缩小窗口。 | 來源視窗無法使用，補齊原影像或縮小視窗。 | Source window unavailable. Supply the frame or reduce the window. |
| Error.R0021 | 所需缓存未命中，显式改为读写缓存。 | 所需快取未命中，明確改為讀寫快取。 | Required cache entry missing. Explicitly choose read and populate. |
| Error.R0022 | 缓存回执失败或未确认，查询原发布ID。 | 快取回執失敗或未確認，查詢原發布ID。 | Cache receipt failed or unconfirmed. Query the original publish ID. |

UI构造规格：RectificationControl公开无参数构造只创建控件/本节默认布局/模块资源，不启动Engine、IO、资格或语言全局服务；先构造宿主根、原Engine/Preview/Language，再BindAsync。UI-R01～06的两个独立STA Host分别采用识别点/轮廓与拼接图像/窗口输入，完整DTO直接复用§11的相应软件Host，Preview fake只返标DisplayOnly的确定图像/覆盖，所有原调用/lease/binding恢复根归harness；真实宿主Preview/Project接线在同一Wpf.Acceptance另验，不把fake画面当真实视觉/资格。布局与三语表在无产品Shell时也必须可实例化与操作；窗口标题关闭先Close有限观察，PendingDrain时维护根继续持有控件和原任务。

## 11. 无 UI 最小调用示例

### 11.1 两个独立合成Program与完整输入

两个Host在§13.1同一BCL Exe内以--host A/--host B运行于不同进程，不共享实例/全局current asset；harness私有HostSample/ProcessRoots不是新增模块API。A为识别工具Points，B为定位工具Contour；C1均只验证/冻结/换基，C2只用BCL确定性Simulator验证生命周期。整图/窗口第二消费者仍按C4/C5验收，不拿合成点Host证明图像正确性。以下ProgramA/ProgramB为二选一入口，harness用--host分发相同Main，不需要外部draft/inputPoints或服务定位器。

```csharp
internal static class ProgramA
{
    public static Task<int> Main(string[] args) => HostSample.RunAsync("A", args);
}
internal static class ProgramB
{
    public static Task<int> Main(string[] args) => HostSample.RunAsync("B", args);
}
internal static class SyntheticInput
{
    internal static readonly CoreLimits Limits = new(
        100000, 128, 16, 4, 64, 128, 512, 8192, 65536, 1048576, 128, 1024);
    internal static RectificationRequest Create(string host, CancellationToken token)
    {
        if (host is not ("A" or "B")) throw new ArgumentException(nameof(host));
        ContentHash h = new("sha256", new string('0', 64)); // 合成Owner引用
        PixelSize size = new(2, 3);
        ValidityDomain full = new(size, DomainKind.Full, Array.Empty<RowSegment>(), null,
            new ContentHash("sha256", "4bc8b7692cf990b4dc58c597d5b62bf8773f78af2e394bb3340b63ea88e8165c"));
        FrameSnapshotId frame = new("synthetic-" + host);
        RevisionId revision = new("1");
        InputFrameDescriptor source = new(frame, revision, size,
            PixelCoordinateConvention.CenterRowColumn, h, h, h, full,
            Array.Empty<PlaneLayout>());
        RectificationInput input = host == "A"
            ? new RectificationInput.Points(source,
                new PixelPoint[] { new(1, 0.5) }, PointBatchPolicy.AllOrNothing)
            : new RectificationInput.Contour(source,
                new PixelPoint[] { new(0.5, 0.25), new(1.5, 0.75) },
                new int[] { 0 }, new bool[] { false });
        return new("request-" + host, host == "A" ? RectificationOperation.Points
            : RectificationOperation.Contour, frame, revision,
            new CalibrationAssetRef("synthetic-asset-" + host, revision, h),
            TargetGeometry.SameSizeCenterPixels(size),
            new RectificationOptions(Interpolation.Bilinear,
                BoundaryPolicy.RejectIfUnsupported,
                OutputDomainPolicy.InputDomainIntersectionAndKernelSupport, CachePolicy.Disabled),
            input, new RectificationBudget(65536, 1048576, 262144, 65536, 1, 16, 64),
            TimeSpan.FromSeconds(1), token);
    }
}
```

h的全零hex仅为合成端口声明的受控引用，真实端口不能绕过来源hash验证。Full域hash为A.4.2固定Golden；asset支持同域、无图像plane。目标主点为(1,0.5)，两个Host的source/asset ID与RequestId不同且不热换。后续生产Host必须注入真实来源/资格，不能把下表synthetic/identity当HALCON算法。

### 11.2 有界观察与进程根Owner

ProcessRoots是harness私有、进程寿命强持的有界槽表：固定2槽、每槽2MiB managed恢复额度（含两Host输入/限额/端口/Task/诊断/结果容量），在Factory或任何工作前原子Reserve，容量不足不调用Factory，报R0011。槽中保留输入、取消源、借用端口、Limits/epoch、原Factory/Execute/consumer/Payload.Dispose/Drain/Engine.Dispose Task和Engine/Result对象，不用弱引用或仅RequestId；结果迟到时仍由该槽接收。Factory前已有槽；FactoryTask=Task.Run只包同步构造且必须在任务内先把Engine存入槽再完成Task，不能Task返回Engine后由过期调用栈来接住。每个ValueTask只转换一次AsTask并原样登记，所有重观察使用同一Task；禁止第二次调用Execute/Dispose替代遗失的Task。

以下HostSample为完整调用顺序；ProcessRoots/RootSlot的私有实现固定在下表，不暴露公共恢复接口，不把未定义宿主逻辑留作外门。所有阶段观察使用独立墙钟上限500ms（工作原期限仍1s）；恢复泵可在后台等待原Task真实结束，但Host Main/窗口关闭只作有限观察，不随泵无限await。内部5s/30s与外部Runner期限按§13.1继续有效。

```csharp
internal static class HostSample
{
    internal static async Task<int> RunAsync(string host, string[] args)
    {
        string slice = args.Length == 1 ? args[0] : ""; // runner分发后只传C1/C2
        if (slice is not ("C1" or "C2")) return 2;
        RootSlot? root = ProcessRoots.TryReserve(host, bytes: 2097152);
        if (root is null) return 11;
        int code = 0;
        try
        {
            root.Request = SyntheticInput.Create(host, root.Stop.Token);
            if (slice == "C1")
            {
                // 同步Core资源限额先验，bounded Task观察不强杀线程。
                root.CoreTask = Task.Run(() => RunCore(root.Request));
                if (!await Observe(root.CoreTask)) code = 124;
                else code = await root.CoreTask;
            }
            else
            {
                root.Ports = new SyntheticPorts(root.Request); // 下表的BCL端口
                root.FactoryTask = Task.Run(() =>
                {
                    root.Engine = RectificationEngineFactory.Create(
                        new EngineOptions(host == "A" ? 1 : 2, 8, 8, 64,
                            TimeProvider.System, SyntheticInput.Limits),
                        root.Ports, root.Ports, root.Ports, root.Ports, null);
                    return root.Engine;
                });
                if (!await Observe(root.FactoryTask)) code = 124;
                else
                {
                    IRectificationEngine engine = await root.FactoryTask;
                    root.ExecuteTask = engine.ExecuteAsync(root.Request).AsTask();
                    if (!await Observe(root.ExecuteTask)) code = 124;
                    else
                    {
                        root.Result = await root.ExecuteTask;
                        if (root.Result.State != RectificationTerminalState.Completed) code = 3;
                        else
                        {
                            root.ConsumerTask = Task.Run(() => UseDerived(root.Result, host));
                            if (!await Observe(root.ConsumerTask)) code = 124;
                            else await root.ConsumerTask;
                        }
                    }
                }
            }
        }
        catch (Exception ex) { root.RecordBusiness(ex); code = 1; }
        finally
        {
            // 这些私有方法捕获自己的异常，不覆盖业务异常/非零code。
            root.RequestStopAndStartRecovery();
            bool accepted = ProcessRoots.ConfirmRecovery(root); // 同一进程根槽接收确认
            if (!accepted) { root.RecordCleanup("RootTransferNotAcknowledged"); if (code == 0) code = 1; }
            bool cleaned = await Observe(root.RecoveryTask);
            if (!cleaned && code == 0) code = 124;
            if (root.HasCleanupFailure && code == 0) code = 1;
            // 只有恢复泵核定完成才能释放槽；本方法不清引用/不Dispose Stop。
        }
        return code;
    }
    private static int RunCore(RectificationRequest request)
    {
        var check = RectificationCore.ValidateRequest(request, SyntheticInput.Limits);
        if (!check.IsValid) return 3;
        var frozen = RectificationCore.FreezeInput(request, "no-backend/1",
            "coordinate-normalization/1", SyntheticInput.Limits);
        IReadOnlyList<PixelPoint> points = frozen.Request.Input switch
        {
            RectificationInput.Points p => p.Values,
            RectificationInput.Contour c => c.Vertices,
            _ => throw new InvalidOperationException()
        };
        var corner = RectificationCore.NormalizeCoordinates(points,
            PixelCoordinateConvention.CenterRowColumn, PixelCoordinateConvention.CornerRowColumn,
            SyntheticInput.Limits);
        if (corner.Error is not null) return 3;
        var back = RectificationCore.NormalizeCoordinates(corner.Points,
            PixelCoordinateConvention.CornerRowColumn, PixelCoordinateConvention.CenterRowColumn,
            SyntheticInput.Limits);
        if (back.Error is not null || !points.SequenceEqual(back.Points)) return 3;
        return 0; // 仅换基，不产RectificationResult/资格
    }
    private static void UseDerived(RectificationResult result, string host)
    {
        if (result.State != RectificationTerminalState.Completed || result.Payload is null
            || result.Domain is null || result.Mapping is null) throw new InvalidOperationException();
        if (host == "A" && result.Payload is not PointsPayload) throw new InvalidOperationException();
        if (host == "B" && result.Payload is not ContourPayload) throw new InvalidOperationException();
        // 借用到此调用退出；结果不保存到产品事实，不保留native/像素句柄。
    }
    internal static async Task<bool> Observe(Task original)
    {
        try { return ReferenceEquals(await Task.WhenAny(original, Task.Delay(500)), original); }
        catch { return false; } // 观察失败也不能释放原Task根
    }
}
```

| 私有类型/方法 | 唯一实现步骤、输出及异常边界 |
|---|---|
| ProcessRoots.TryReserve / ConfirmRecovery | 用lock保护两个预分配槽，按host独立占用，先核byte预约再登记root；ConfirmRecovery在同一门核对root对象/槽号/预算/RecoveryTask均已强持，置Acknowledged并TransferAck.TrySetResult(true)返回true。失败保留原槽/所有引用，不能调用方离栈即Release；槽满拒绝新Host，只有Recover真实安全完结释放 |
| RootSlot字段 | Request:RectificationRequest；Stop:CancellationTokenSource；StopTask:Task?；Ports:SyntheticPorts?；Engine:IRectificationEngine?；Result:RectificationResult?；CoreTask:Task<int>?；FactoryTask:Task<IRectificationEngine>?；ExecuteTask:Task<RectificationResult>?；ConsumerTask:Task?；PayloadDisposeTask:Task?；DrainTask:Task<DrainResult>?；EngineDisposeTask:Task?；RecoveryTask:Task；RecoveryChildren:固定两项Task数组；TransferAck:TaskCompletionSource<bool>（RunContinuationsAsynchronously）；BusinessException:Exception?；CleanupFailures:有界最多8项摘要；Acknowledged/RecoveryStarted/DisposeStarted与槽号/预约字节。表中RootSlot字段在示例中以同名gate property暴露，getter/setter及Task/对象写入和移交状态用同一root lock，可见性不能靠字段读取运气 |
| RecordBusiness / RecordCleanup | 首个业务Exception保留原对象；cleanup错误按独立列表登记（满则累计省略计数，不分配新文本），不throw、不改业务码；两者分别输出。禁止finally throw覆盖原错误 |
| RequestStopAndStartRecovery | 用门保证只执行一次。先登记StopTask=Task.Run(() => Stop.CancelAsync())，不在Host/Dispatcher同步Cancel而被未知回调阻塞；启动并登记RecoveryTask=Task.Run(RecoverAsync)，方法自身不得throw；若调度失败，同步记录cleanup并保留槽，不伪造成功Task或释放引用，恢复Owner在进程维护循环重试启动同一根，不重做Factory/Execute。ConfirmRecovery必须确认真实恢复任务已登记，失败Main返回非零 |
| RecoverAsync第一阶段 | 先等待CoreTask或FactoryTask原对象真实退出并记录其失败；Factory迟到返回时Engine已在槽中，不能丢。同步Factory抛错不调用Execute；Factory只允许有界纯构造/验证、不发native/IO、不订阅Watch，失败须内部同步清理已创建私有资源、不Dispose借用端口。否则须先修Factory契约而非靠超时抹掉半构造Engine |
| RecoverAsync引擎cleanup支路 | Engine存在时只调用一次DrainAsync(500ms,CancellationToken.None).AsTask登记DrainTask；同步调用异常捕获。独立启动Engine.DisposeAsync().AsTask登记EngineDisposeTask，同步异常也独立捕获，不能Drain抛错跳过Dispose；Dispose须在同一Engine幂等关闭门内与Execute并发安全。观察到Drain StillDraining只记诊断，根预算仍持有；Dispose未结束一直强持。cleanup支路不等待consumer结果才启动 |
| RecoverAsync结果cleanup支路 | ExecuteTask若存在则等待原Task真实结束，将迟到Result存入槽；只有在已登记ConsumerTask真实结束后，才能对非空Payload调用一次DisposeAsync().AsTask。原业务consumer失败独立登记，不妨碍Payload cleanup；Dispose失败/同步抛错保留Result/Payload和原Task并记录故障，不重复Dispose，不声称释放，需要Owner故障处置。没有成功结果不构造Payload |
| RecoverAsync完成门 | 两支路并行（两个Task也保存在槽Recovery children中），await两者及原StopTask的取消回调真实退出并记录所有失败；Payload.Dispose成功、Engine.Dispose成功、全部原Task已观察且无在用/未知资源、await TransferAck.Task取得true后才Dispose Stop/释放输入和借用端口引用并归还槽预算。失败cleanup保留故障槽与对象/预算，恢复Task可结束报告Failure但不回收槽；进程Maintenance根继续可查询该槽。有限Observe返回false或Main返回绝不是完成门 |

长期产品Host不得在Main/窗口退出后直接结束进程而丢恢复根：进程服务仍运行，保留故障/未知槽并提供恢复动作，停机先排空这些根。这里Runner只在纯BCL Simulator/C1测试中可Kill超期子进程并记失败；真实native/IO/设备进程不得用Kill、进程退出或OS回收当作ResourcesReleased证据。消费者要长期拥有结果时须在借用退出后，由接收者原子登记同一Result/Payload/Dispose Task及预算并回ACK；未ACK仍由原根拥有，不双方Dispose。示例不作长期结果移交，只作恢复根确认与借用消费。

### 11.3 SyntheticPorts的封闭模拟行为

SyntheticPorts仅harness私有，构造参数是已构造request，实现IFrameSource/ICalibrationSnapshotPort/IQualificationBarrierPort/IRectificationBackend四端口；无文件/设备/native/Store，不依赖外部服务。构造只保存小型合成数据，端口按下表返回，全部ValueTask均被引擎单次AsTask/await；正常Watch必须在专用token取消时结束。TaskCompletionSource闩锁仅在§13.1对应故障模式启用，且仍由根强持。

| 端口成员 | 正常A/B值与完整输出规则 |
|---|---|
| Backend.Capabilities | BackendId=synthetic，Version=simulator/1；PixelFormats={Byte}，MaxImageSize=(100000,100000)，MaxLinearIndex=Int64.MaxValue，MaxWorkingBytes=1048576、MaxNativeBytes=262144、MaxMapBytes=65536、FixedScratchBytes=64、MaxConcurrentOperations=1；SupportsImage=false、SupportsPoints/Contours=true、SupportsSourceWindows=false；CoordinateBuffers=(coordinate-buffers/1,128,16,64,8,16,4,12,40,0)。此为合成算术能力，不是HALCON数据 |
| Assets.ReadAsync | 精确Id/revision/hash匹配request才CalibrationReadResult(new CalibrationAssetSnapshot(request.Calibration,"synthetic-identity/1",[1d],[1d],request.Input.Frame.CaptureScopeHash,request.Input.Frame.Domain),null)，否则(null,R0003)。synthetic模型只由此Simulator支持，真实模型能力拒绝它 |
| Qualification.ReadAsync / WatchAsync | 固定Watermark=(synthetic-owner,epoch-1,1,测试TimeProvider.GetUtcNow(),该时间+1h)，Scope和Domain取request，Qualified；minimum非空需同authority/epoch且revision<=1，否则(null,R0005)。Read成功不遗留IO。Watch先发此Qualified通知，再等待专用token的无限delay（受根Owner观察，不在Main等），收到取消后正常退出/Dispose，无底层未结束IO；故障模式锁住MoveNext/Dispose/回调并按A.6隔离 |
| Frames.AcquireWindowAsync / Backend.PlanWindowAsync / PrepareMapAsync | 正常点/轮廓绝不调用；误调用时返回对应失败结果Lease/Plan/Map/Safety=null、Error=R0010、Drain=Drained，无分配，调用数用于断言。不增加任何未定义Frames成员 |
| Backend.RunAsync | 检查frame/map/plan全部null、身份/数量/域/取消和期限；成功按冻结载荷逐值独立复制至PointsPayload或ContourPayload（保留SegmentStarts/Closed），Domain为同Full，Mapping=(request.Input.Frame,request.Target,null,CameraPixelToCorrectedPixel,Bilinear,request.Options.Boundary,request.Options.OutputDomain,domain.Hash,null,"synthetic-identity/1","simulator/1")，Map=null/Error=null/Drain=(Drained,[],0)。这只是模拟恒等候选，Engine仍须A.6屏障；不叫HALCON校正。失败Payload/Domain/Mapping/Map=null和稳定Error/真实Drain，不能泄露部分结果 |
| Backend.ObserveDrainAsync | 正常(Drained,[],0)；闩锁未结束(StillDraining,[原RequestId],持有字节)，不释放对象；闩锁打开只使原作业完成，不新建Run |

两个Host均从上述公开DTO构造至调用/消费/归还，真实业务范围不进入Core；C1不实例化SyntheticPorts或Factory，C2不调用HALCON或提供物理验收。最小调用链和失败行为不得被旧await using示例覆盖。

### 11.4 S1两个从空Host装配的图像协议链

S1公开端口/工厂唯一见A.7，软件模拟行为见A.8；工程与六项准入见§19.2，S1六项文档规格已由主控内容回读接收为ModuleCoreImplementationReady（仅规格准备）；完整A/B Host尚未编译或运行。Host A验证整块2×2派生像素消费；Host B验证显式右侧窗口及原PublishId回执恢复。它们分别启动独立进程，只借用Core和Simulator DLL；无HALCON/AsunImage、数据库、设备、WPF或隐藏窗口。结果是协议fixture，不求真实畸变、不证明HALCON map安全、光学精度或业务资格。A/B在S1与§11.1的C1/C2合成Host分别构造，不修改已接收的C1/C2案例。

```csharp
// Program入口解析 --host A/B 后调用 RunS1Async；非法参数非零。
static async Task<int> RunS1Async(string host)
{
    if (host is not ("A" or "B")) return 2;
    S1Root? root = S1ProcessRoots.TryReserve(host, maxHeldBytes: 8388608);
    if (root is null) return 11; // Factory前有界进程根，规则复用§11.2
    int code = 0;
    try
    {
        var limits = new CoreLimits(16, 128, 16, 4, 64, 128, 512,
            8192, 65536, 1048576, 128, 1024);
        var h0 = new ContentHash("sha256", new string('0', 64));
        var pixels = host == "A"
            ? new byte[] { 10,20,30,40,50,60,70,80,90 }
            : new byte[] { 11,21,31,41,51,61,71,81,91 };
        var pixelHash = new ContentHash("sha256", host == "A"
            ? "a51f9a0b6ea3523acf4697ac74fc8e3653ae8cbe1abf58adffb069e1f5e8c2e5"
            : "0e5439fb87db2313da5cdf70ebccfc91846a1c2e12a08d1e877000fac23f1bdc");
        var full = new ValidityDomain(new PixelSize(3,3), DomainKind.Full,
            Array.Empty<RowSegment>(), null, new ContentHash("sha256",
            "f7ec6d05bea186b77811fbd63cf7b9882ca5c891c15622149290f041d28fd431"));
        var frameId = new FrameSnapshotId("S1-frame-" + host);
        var rev = new RevisionId("1");
        var plane = new PlaneLayout(PixelFormat.Byte, 1, 0, 3, 3, 9,
            Guid.Parse("00000000-0000-0000-0000-000000000001"), 9, full);
        var source = new InputFrameDescriptor(frameId, rev, new PixelSize(3,3),
            PixelCoordinateConvention.CenterRowColumn, h0, pixelHash, h0, full,
            new PlaneLayout[] { plane });
        var assetRef = new CalibrationAssetRef("S1-asset-" + host, rev, h0);
        var asset = new CalibrationAssetSnapshot(assetRef, "synthetic-protocol/1",
            new double[] { 3,3 }, new double[] { 2,2 }, h0, full);
        DateTimeOffset now = new(2026,10,11,0,0,0,TimeSpan.Zero);
        var time = new FixtureTimeProvider(now); // harness私有固定UTC+可推进单调时钟
        var qualified = new QualificationSnapshot(assetRef, QualificationState.Qualified,
            new AuthorityWatermark("S1-authority-" + host,"epoch-1",1,now,now.AddHours(1)),
            h0, full); // 仅合成签发者，不能接入生产Owner
        var target = new TargetGeometry(new PixelSize(2,2),new PixelPoint(0.5,0.5),
            PixelCoordinateConvention.CenterRowColumn,
            host == "A" ? new PixelRect(0,0,2,2) : new PixelRect(0,1,2,1));
        root.Request = new RectificationRequest("S1-request-" + host,
            RectificationOperation.Image,frameId,rev,assetRef,target,
            new RectificationOptions(Interpolation.Bilinear,BoundaryPolicy.RejectIfUnsupported,
                OutputDomainPolicy.InputDomainIntersectionAndKernelSupport,CachePolicy.ReadThrough),
            new RectificationInput.Image(source),
            new RectificationBudget(65536,1048576,262144,262144,1,16,64),
            TimeSpan.FromSeconds(1),root.Stop.Token);
        root.FrameFixture = new SimulatorFrame(source, new ReadOnlyMemory<byte>[] { pixels });
        root.AssetFixture = new SimulatorAsset(asset,qualified);
        var backendOptions = new SimulatorBackendOptions(limits,16,128,1048576,4);
        var storeOptions = new MemoryMapStoreOptions(limits,262144,8,16,2,65536,
            TimeSpan.FromMinutes(5));
        var simOptions = new RectificationSimulatorOptions(backendOptions,storeOptions,
            4,1048576,16,32,time);
        root.SimulatorFactoryTask = Task.Run(() =>
        {
            root.Simulator = RectificationSimulatorFactory.Create(simOptions,
                new SimulatorFrame[] { root.FrameFixture },
                new SimulatorAsset[] { root.AssetFixture });
            return root.Simulator; // 写根后才完成原Task
        });
        if (!await S1Observe(root.SimulatorFactoryTask)) throw new S1ObservationExpired();
        var sim = await root.SimulatorFactoryTask;
        if (host == "B")
        {
            var installed = sim.Control.Install(new SimulationFaultRule(SimulationOperation.PublishMap,
                "*",SimulationFault.LoseReceiptAfterCommit,null));
            if (!installed.IsValid) throw new InvalidOperationException(installed.Error?.Code);
        }
        root.EngineFactoryTask = Task.Run(() =>
        {
            root.Engine = RectificationEngineFactory.Create(
                new EngineOptions(host=="A"?11:12,16,16,64,time,limits),
                sim.Frames,sim.Assets,sim.Qualification,sim.Backend,sim.MapStore);
            return root.Engine;
        });
        if (!await S1Observe(root.EngineFactoryTask)) throw new S1ObservationExpired();
        root.ExecuteTask = (await root.EngineFactoryTask).ExecuteAsync(root.Request).AsTask();
        if (!await S1Observe(root.ExecuteTask)) throw new S1ObservationExpired();
        root.Result = await root.ExecuteTask;
        root.ConsumerTask = Task.Run(() => ConsumeFixture(root.Result,host));
        if (!await S1Observe(root.ConsumerTask)) throw new S1ObservationExpired();
        await root.ConsumerTask;
        // B必须查询Engine登记的原PublishId；未知回执不是新Execute。
        if (host == "B")
        {
            root.PublishStatusTask = sim.Control.GetSnapshotAsync(TimeSpan.FromMilliseconds(100),
                CancellationToken.None).AsTask();
            if (!await S1Observe(root.PublishStatusTask)) throw new S1ObservationExpired();
            var status = await root.PublishStatusTask;
            if (status.Publications.Count != 1) throw new InvalidOperationException();
            root.Publication = status.Publications[0]; // 含原PublishId/key/hash，先强持
            root.QueryPublishTask = sim.MapStore.QueryPublishAsync(root.Publication.PublishId,
                TimeSpan.FromMilliseconds(100),CancellationToken.None).AsTask();
            if (!await S1Observe(root.QueryPublishTask)) throw new S1ObservationExpired();
            var receipt = await root.QueryPublishTask;
            if (receipt.Code != StoreCode.Published || receipt.CommittedHash != root.Publication.ContentHash)
                throw new InvalidOperationException();
        }
    }
    catch (S1ObservationExpired ex) { root.RecordObservation(ex); code=124; }
    catch (Exception ex) { root.RecordBusiness(ex); code=1; }
    finally
    {
        root.RequestStopAndStartRecovery(); // 同§11.2，CancelAsync Task也强持
        if (!S1ProcessRoots.ConfirmRecovery(root) && code==0) code=1;
        if (!await S1Observe(root.RecoveryTask) && code==0) code=124;
        if (root.HasCleanupFailure && code==0) code=1;
    }
    return code;
}
static Task<bool> S1Observe(Task original) => HostSample.Observe(original); // 固定500ms观察
internal sealed class S1ObservationExpired : TimeoutException { }
static void ConsumeFixture(RectificationResult result,string host)
{
    if (result.State != RectificationTerminalState.Completed || result.Payload is not ImagePayload image
        || result.Domain is null || result.Mapping is null) throw new InvalidOperationException();
    byte[] expected = host=="A" ? new byte[]{10,20,40,50} : new byte[]{21,51};
    if (image.Planes.Count!=1 || !image.Planes[0].Span.SequenceEqual(expected)
        || result.Trace.Identity?.BackendVersion!="simulator/1") throw new InvalidOperationException();
    // 仅借用，到Task返回后由根Dispose一次；不写业务/计量/质量事实。
}
```

两个Host为独立入口完整顺序规格，不宣称此文片段已编译。FixtureTimeProvider为harness私有TimeProvider子类：GetUtcNow取起始UTC+推进量，TimestampFrequency=TimeSpan.TicksPerSecond，GetTimestamp取同一推进量ticks；Advance(TimeSpan非负)只由测试门调用，实际观察用墙钟Task.Delay避免测试时钟停滞。正常Host不推进，故资产/资格有效；超时case明确Advance到1s以后。全零asset/layout/scope仅为合成引用，Factory核精确引用与raw plane SHA-256、域规范hash；真实来源端口不能接受这种fixture。

FixtureTimeProvider同时覆盖CreateTimer/ITimer，不能继承真实墙钟timer后宣称Advance已触发deadline。harness预占最多32个timer槽及其回调Task/状态字节；初始不启动外部timer，Advance在锁内推进UTC/单调时间并收集到期timer，在锁外调度原callback、强持Task且记录异常。每timer最多一个在途callback，周期timer一次Advance只投递一次到期通知并把next due推进到当前时间以后，不按跨过的周期数创建无界Task；Change/Dispose与到期登记使用同一锁，DisposeAsync还须等已进入的原callback真实退出，后续不得回调已关闭timer。零dueTime按同一有界调度处理，Timeout.InfiniteTimeSpan表示停用，负的其它值拒绝；实际用例只用非周期deadline timer。Engine请求deadline/取消闩锁由同一TimeProvider推进，原callback退出前Stop/根不能归还；正常Host不Advance，墙钟Observe始终使用独立Task.Delay。timer实现是harness私有，没有模块公开API或生产时间权威。

S1Root复用§11.2全部强持/ACK/异常分离规则，另以gate property保存SimulatorFactoryTask、EngineFactoryTask、IRectificationSimulator、SimulatorFrame/Asset、Publication、PublishStatusTask、QueryPublishTask、SimulatorDisposeTask以及最多16个原Store/lease Dispose Task；RecordObservation只记录有界观察到期摘要，不丢根、不冒充业务执行失败。Host操作开始后的所有分支经finally再走末尾单出口，退出码在finally后统一计算，cleanup异常不覆盖业务错。根在Factory前8MiB预约，两个静态预分配槽、每个Host一个；包含sim全部retained/cache、每操作reservation、输入fixture/结果/诊断/Task和Simulator.Dispose Task；超额拒绝新根/新operation。新增Factory同步异常也由根捕获，不允许绕过原EngineFactoryTask再造引擎。

恢复泵的三个独立支路为：①Engine Drain/Dispose（不Dispose借用端口）；②原Execute/consumer真实结束后Payload.Dispose一次，查询原receipt或丢弃已完成读候选的独立托管引用；③原sim/engine工厂与全部query/lease操作结束后Simulator.Dispose。③只能在Engine.Dispose真实成功、原Execute及Store操作不再持端口后开始；不能在①未知排空时关sim使Watch/native模拟worker消失。Query返回Unknown或观察超期，保留原PublishId/Key/ContentHash/MapContent和Task/额度，只有限查询原ID；任何查询本身也必须真实结束才能启动下一次，见A.8.3。不因Result已Completed删除未决receipt根；Host正常A直到全部工作/独立结果及bundle释放才回根预算，B另等原receipt确知。receipt与Execute两个身份不混用。结果迟到、query迟到、lease迟到由同根唯一接收并归还；observer断开不是完成证据。

## 12. 正常、边界和失败案例

| 场景 | 输入 | 必须结果 |
|---|---|---|
| 正常热map | 同一合格资产/布局、当前输入和四邻支撑均有效 | Completed；独立派生像素/domain/trace，原帧可读；cache hit仍重新资格/域校验 |
| 点路径 | 20 个合法中心像素点 | 不生成整图；返回同序点和逐点有效标记 |
| 负 stride | 合法倒序行且访问范围可证明 | 适配器按支持情况行复制或接受；输出不含 padding |
| 奇数 ROI | ROI 起点非零，map 目标尺寸相同 | key 含起点；不能命中全幅旧 map；父坐标可回溯 |
| 边缘邻域 | 双线性缺右/下邻点 | Reject策略R0009；Conservative策略保留尺寸并无效标记/安全哨兵；1×N无法安全锚定R0009 |
| 低残差但条件失效 | 资产 RMSE 低但镜头/分辨率变更 | `R0005/R0006`；不输出可量测资格 |
| 资产撤销在途 | 冻结asset运行中收到Revoked/gap/权威Unknown | 按A.6立即禁止发布并请求停止，native安全排空后Rejected/R0005，未知排空仍非终态 |
| map hash 错误 | 文件存在但内容或布局不匹配 | `R0008`，缓存项不可使用；保留诊断 |
| 取消迟到 | native 仍执行时收到取消 | `Draining`，结束前保持 lease；若无法证明结束则进入 `DrainUnknown/R0015` 非终态；取得证据后才最终 `Cancelled` |
| 两实例并发 | A、B 使用相同固定双线性算法，但不同帧/标定/目标尺寸 | 缓存键和结果互不串扰；trace 含各自来源闭包；Nearest 请求在 Validate 阶段拒绝 |
| 显示填洞 | 仅预览需要填充越界区 | 只生成显示派生层；正式结果保留 `DomainInsufficient` |
| 适配器异常 | AsunImage 抛出 native 异常 | `R0014`；释放成功取得的资源，不自动切换未验证算子 |

## 13. 测试矩阵和验收断言

测试必须使用原始帧、标定资产、布局、坐标约定和版本快照；Mock 只验证端口控制流，不能冒充 HALCON/现场证据。

| 层级 | 测试内容 | 通过断言 |
|---|---|---|
| 契约 | 必填字段、范围、单位、枚举、默认值、序列化版本 | 非法值在 native 前稳定得到同一错误码 |
| 布局 | 正/负 stride、padding、offset、最小负值、乘加溢出、多 plane | 可访问范围精确验证；不读 padding/尾部 |
| 坐标 | 中心/corner、row/column 换基、crop、旋转/缩放、逆映射 | 已知算例和 round-trip 在 Profile 容差内；半像素反例失败可检出 |
| map | 冷生成、热命中、旧 revision、hash/尺寸损坏、邻域越界 | key 完整；损坏和不适用不命中成功路径 |
| 域 | 空洞、局部缺失、边缘核支撑、整图/点路径 | 输出域保守；未知不变 0；显示填充不取得量测资格 |
| 执行 | image/point/points/contour、空输入、全域和 ROI | 结果顺序、来源、单位和有效性可追溯 |
| 并发 | 双实例、同实例排队、慢订阅者、缓存竞争 | 无共享可变状态；事件不丢正式结果；无死锁 |
| 取消 | waiting、map generation、native running、publish 前取消 | 取消不发布成功载荷；真实结束前不释放资源 |
| 超时/恢复 | 超时、进程重启、排空成功/未知、回执丢失 | 排空成功后才是 `TimedOut`；`DrainUnknown/R0015` 始终非终态、无成功载荷且资源隔离；不盲重试不同身份 |
| 资格 | 资产缺失、过期、撤销、scope 越域、输入模式变化 | 明确 `R0004/R0005/R0006`；不以低 RMSE绕过 |
| 适配器 | HALCON26.05经cv2的点/XLD/map语义、线程和异常 | 不核算子覆盖；仅实际类型/重载/封送歧义查公共签名，真实验收独立 |
| 两个消费者 | 识别/定位按点，拼接/计量整图 | 同一 Core 结果语义一致；宿主业务不进入模块 |
| UI（若交付） | 三语、固定1920×1080视口、键盘、UIA、卸载/取消 | 按§10.4验证；不增加其它分辨率矩阵，UI不改变Core结果或生命周期 |

最小 Golden 集合应包含中心、四角、边缘高畸变、ROI 偏置、不同格式、有效域洞、反光/低质量和标定失效变体。每个 Golden 绑定输入 hash、资产 hash、目标 HALCON/AsunImage 版本、参数、期望有效域和数值容差；没有真实标准件时只报告软件断言，不宣称物理精度。

### 13.1 唯一Core BCL harness与执行门

C1/C2均使用§1.3绑定的唯一测试工程 `tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj`，它同时是最小无UI宿主。规划工程形状为Microsoft.NET.Sdk / net10.0 / OutputType=Exe / Nullable与ImplicitUsings开启；唯一ProjectReference是§1.3的Core.csproj，依赖仅.NET BCL，不引入待选测试包。DEV-GOV-010 §3.1 冻结的 BCL Exe 约定只复用执行约定，不修改它。运行入口必须显式列举下表case ID，模拟后端是该harness内部可控端口，不宣称HALCON精度。

| Case ID / 切片 | 必需输入与可判定断言 |
|---|---|
| IR-C1-01 | Points=(Row2,Column3)，CenterRowColumn→CornerRowColumn=(2.5,3.5)，再回到原点；CenterColumnRow交换为(3,2)，不发生畸变求解 |
| IR-C1-02 | 2×2 Byte plane：offset2,stride=-2,rowBytes2,accessible4合法；offset1同stride为R0002；checked溢出、padding、非法枚举均native调用数0 |
| IR-C1-03 | 8×4 RowSegments含第2行[0,2)与[4,8)，裁窗(row1,col1,height2,width5)得到局部第1行[0,1)、[3,5)；Unknown为R0009，域洞不扩大全域 |
| IR-C1-04 | SourceFrame/revision/hash与Input不符、空点/非法段/非有限坐标、负预算、窗口越界分别按首错稳定返回；freeze后修改原数组不改snapshot/hash |
| IR-C1-05 | 相同内容canonical hash一致，预算不改几何map身份但改变UI草稿hash，RequestId/token不改三类hash；asset revision、source/target窗口或schema不同则key不同；0.2字段类型/编码规则与A.4声明一致 |
| IR-C1-06 | 输入100000×100000输出窗口16×16不分配全图；建议不改请求；A.2点例(O,W,N)=(608,1232,304) byte，轮廓例=(650,1364,384)，各额度恰等于估值通过、分别减1为R0011；点路径不查map/不按图像面积计费，未知缓冲界限或数量超能力R0010、乘加溢出R0011 |
| IR-C1-07 | A/B两个完整SyntheticInput的C1 Program均从构造运行至换基round-trip；Normalize/Validate/Freeze分别数量或累计域段超Limits、checked容量超限时在复制/hash前R0011；任意自定义IReadOnlyList拒绝R0001且其索引未访问；无Factory/Execute/native/IO；维度按显式MaxDimension而非机械100000裁决 |
| IR-C1-08 | 严格UTF-16/UTF-8：孤立surrogate、Cc/Cf、首尾空白、非法ContentHash拒绝；每字段/累计text/canonical容量恰限允许、+1超限；é与e+组合符不同Ordinal引用、大小写ID不同；无Trim/NFC合并 |
| IR-C1-09 | A.4.2固定73byte域与402byte Host A Input的完整hex/SHA-256均一致；Expected为字面量和独立字段拼接，不用被测codec生成；存在bit、empty/null、-0/+0、嵌套引用hash和自hash排除逐一断言；RequestId/token不改Input/Calculation/UI，预算改UI不改map |
| IR-C2-01 | 闩锁阻塞backend：同ID第二次R0018且调用数仍1；Unknown/EpochMismatch/RevisionNotReached/Evicted查询返回精确码且Snapshot=null；Found无Payload |
| IR-C2-02 | 撤销发生在native前、候选后、资格回读中、观察器关闭中、发布门前各一次，均无ResultPublished；回读Qualified但观察结束水位更高也R0005；已接纳资源和候选各释放一次后Rejected/R0005；仅新revision且旧仍Qualified不热换旧asset |
| IR-C2-03 | 分别阻塞native、资格回读IO、Watch的MoveNext/DisposeAsync/回调结束闩锁，取消/超时后无法证明完成→DrainUnknown，ExecuteAsync未完成且Drained/ResourcesReleased/Terminal均未发、release计数0；仅全部真实完成闩锁打开后release=1和原取消/超时终态，候选释放一次；WaitAsync超时不当IO结束证据 |
| IR-C2-04 | 空native计算仍等待资格回读和本请求观察器完成后Draining→Drained→ResourcesReleased→ResultPublished；Drained之后请求IO调用数不增；正常关闭观察器不造撤销，共享Owner观察器和其它请求不被Dispose；订阅者抛错/退订不破坏终态；晚epoch和旧revision事件被UI消费者丢弃 |
| IR-C2-05 | 16×16目标窗源支撑跨两个tile：精确parent/hash成功；缺中间tileR0020，新revisionR0003；窗口乱序/重复只给各自结果，不声称mosaic完整 |
| IR-C2-06 | 断言PlanWindowAsync→PrepareMapAsync→RunAsync的顺序；结构损坏不得Run，缓存命中也Prepare；域洞覆盖一双线性邻点，Reject策略失败；Conservative策略安全map全cell合法但该点无效；最后列/1×N/zero-weight越界仍拒绝或安全改写，模拟仅验控制流 |
| IR-C2-07 | Store内容成功索引失败/丢回执→Unknown，只查询原PublishId；同PublishId不同hashConflict；RequireHit缺项R0021；ReadThrough写失败不污染已有可验证计算 |
| IR-C2-08 | 无资格/失联/epoch变化/通知gap→R0005且禁止发布；Close等待未排空不Closed；恢复证据只使原请求终态不创建新计算 |
| IR-C2-09 | 两消费者A点/B图同时，同实例或双实例分别验证，取消A不释放B的输入/map，结果域/资产/hash独立；改参后旧结果不应用 |
| IR-C2-10 | schema升级、损坏key/hash、旧模型字段缺失拒绝；停止新请求→排空→兼容包回退，原DrainUnknown不中途变完成 |
| IR-C2-11 | A/B Host分别Factory前根槽已强持input/ports/byte预约；满槽拒绝且Factory调用数0；同步Factory异常保留原错、不调用Execute、构造局部清理一次、不Dispose借用端口；Factory迟到Engine先写根槽，不能丢给已离栈调用方 |
| IR-C2-12 | consumer业务异常+Payload.Dispose或Engine.Dispose失败同次注入：业务错及cleanup错分别保留、Main非零，Drain失败也启动Engine.Dispose独立支路；失败槽保留Result/Payload/Task/预算，原ValueTask仅AsTask一次、Dispose调用数1；finally不得覆盖业务错误 |
| IR-C2-13 | A/B分别Execute观察到期后迟到Completed、consumer未结束、Payload.Dispose闩锁未退出：恢复槽有ACK且强持原Task/输入/结果，未到完成门release=0；consumer真实结束后迟到Payload释放一次；失ACK或根维护故障不能清原槽引用/预算或声称Closed |
| IR-C2-14 | A/B各一次底层资格Watch违约不退出：Host Main/cleanup观察有限返回124、根Recovery仍强持Engine/Execute/Watch与预算，真实打开原闩锁前无成功载荷/ResourcesReleased；之后恢复同一Task至原终态/归还；不用Kill作为资源释放证据，双Host互不Dispose对方资源 |
| IR-HARNESS-01 | 将必需case标Skip、未完成闩锁、断言失败、内部截止到期分别运行runner故障模式，父runner确认退出非零并带原Case ID；零执行不返回0 |

每个case墙钟截止5s，整套内部截止30s，外层Core run进程截止60s，构建截止180s；这些只为确定性软件harness停止值，不是客户性能目标。用固定TimeProvider推进作业Deadline，并用可控制TaskCompletionSource闩锁模拟并发；外层/内部墙钟防止测试时钟停滞挂死。case 5s未完成标TimedOut；suite到期列出全部未完成case，返回非零。Required IDs只能按显式C1或C2 slice清单执行，参数未知非零；某slice未实现、任何必需Skip/NotRun/Failure/Timeout、异常或列表为空均非零。0仅在所选slice全部必需断言实际执行并通过；C1通过不覆盖C2/native/UI。

在仓库根运行的未来命令（本轮不创建工程、不执行）：
```powershell
dotnet build src/Modules/image-rectification/Asun.Modules.ImageRectification.Core/Asun.Modules.ImageRectification.Core.csproj -c Release
dotnet build tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj -c Release --no-build -- --slice C1 --host A --case-deadline-ms 5000 --suite-deadline-ms 30000
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj -c Release --no-build -- --slice C1 --host B --case-deadline-ms 5000 --suite-deadline-ms 30000
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj -c Release --no-build -- --slice C2 --host A --case-deadline-ms 5000 --suite-deadline-ms 30000
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj -c Release --no-build -- --slice C2 --host B --case-deadline-ms 5000 --suite-deadline-ms 30000
```

每条命令必须由有限进程runner执行：ProcessStartInfo.FileName="dotnet"，UseShellExecute=false、CreateNoWindow=true，ArgumentList逐项加入上述参数；构建WaitForExit(180000)，run WaitForExit(60000)，未结束记对应IR-BUILD或IR-SUITE/TimedOut并返回124，Core harness可Kill(entireProcessTree:true)，不将kill称作排空证据。其ExitCode必须传回门禁；构建非零不继续run。stdout/stderr异步排空，不能阻塞测试进程。此退出协议仅适用无native的Core harness；native/WPF/HIL另有安全隔离资格计划，不用强杀证明资源释放。`dotnet test`不执行这些Exe，不把空执行成功当验证。正式性能、HALCON实际内存越界、安全map像素、窗口seam和真实WPF交互仍需后续切片实测。

### 13.2 S1公开Simulator与Store协议harness

S1单独使用§19.2绑定Simulator.dll和Simulator.Tests的BCL Exe，不修改C1/C2必需case或Core.Tests入口；harness中的S1ProcessRoots/S1Root和FixtureTimeProvider不是模块公开DTO。runner分发--slice S1 --host A/B（缺值/未知值非零），每Host必须实际执行下表全部case（每case内部重新构造有界bundle、完整fixture和根，允许明确换RequestId）；case ID和预期不能由模拟器自己返回PASS。所有操作输出、result bytes、receipt/hash、调用数及root存活在harness侧独立断言；不以协议模拟证明真实校正数值或HALCON map安全。

| Case ID | 必需输入、可执行断言及准确边界 |
|---|---|
| IR-S1-01 | 从空Host A/B按§11.4完整构造，A SourceWindow=(0,0,3,3)/输出[10,20,40,50]、B=(0,1,3,2)/输出[21,51]；ImagePayload尺寸/Full域/Mapping父坐标、BackendVersion=simulator/1、NativePeakBytes=0。所有factory/Execute/consumer/独立Dispose后root字节归还，Borrowed Engine不关Store或Frames |
| IR-S1-02 | Clone前数量/文本/wire/actual allocation预算超限R0011，非法options/R0001、模型/格式/R0010；超MaxOperations/并发或MaxReceipts满时mutation调用数0，不无限排队、不忘掉已用ID。改变原pixels/DTO数组不改冻结fixture/结果；失配rawSHA/revision拒绝 |
| IR-S1-03 | Plan→Acquire→Read/Prepare→Run→资格Read/Watch结束→Drained→ResourcesReleased顺序；cache miss只Publish一次，cache hit仍Prepare且不Publish，不跳过资格；RequireHit missR0021且Prepare/Run均0。点/轮廓protocol恒等变体不查Map/Acquire，不变更已接收C1/C2断言 |
| IR-S1-04 | protocol-key与halcon-key任一schema/Backend/Algorithm混用R0017或R0008、Run=0；无论hash正确都不接生产Store。InvalidMapStructure/错误maphash/越界plane长度不得提供成功Safety，Run=0。验证仅fixture字节与控制流，不报告HALCON安全通过 |
| IR-S1-05 | B窗口逻辑6byte、held parent9byte，lease实际容量及元数据开销在Acquire前计费，重复同allocation只计一次；CopyRow返回窗口原byte不padding；MissingFrame R0020/ChangedRevision R0003；候选/lease不同时归同Owner，不让Run悬空读取 |
| IR-S1-06 | LoseReceiptAfterCommit→Unknown/R0022且HasLiveOperation=false、原Publish count1；ReadThrough独立图像仍可Completed，unknown key在恢复确认前不可作为hit；控制快照GetRecovery找到原ID，Query原ID→Published/exact hash，未新Publish/Execute；receipt预算不在结果Completed时消失 |
| IR-S1-07 | Publish hold+Host观察超时：底层仍活→HasLiveOperation=true/DrainUnknown，Execute未结束、ResourcesReleased/Terminal/Payload均无，输入/map/Task/预算强持；ReleaseGate后按原取消/deadline终态，ID不换。上一Query hold未结束只重观察原Task，不发并行重复Query |
| IR-S1-08 | FailBeforeEffect确认IO退出→Query原ID NotFound→Host显式同ID同hash重试一次成功；同ID不同key/hashConflict；最大8次有限Query仍Unknown则Pending根/预算仍在，下一动作继续查原ID，不把Unknown变NotFound，不用另Request掩盖副作用 |
| IR-S1-09 | 同key两个request并发、独立bundle/共享Store分别验证；Invalidate(expectedHash)一致移索引、不同Conflict，原已复制MapContent与Result仍可读；索引/receipt引用blob不按MaxIdle清掉，失回执不得淘汰；Store Dispose不让活IO/读clone消失 |
| IR-S1-10 | Run/资格Read/WatchMoveNext/WatchDispose/FrameLeaseDispose各hold一次，先cancel/Advance(1s)/Close有限观察；未打开原gate不得ResourcesReleased/归还请求预算或租约根，Watch串行dispose；ReleaseGate幂等仅完成原Task。SimulatorDispose hold单独断言bundle/root预算仍在；Engine此时允许已经Closed/ResourcesReleased，Simulator仍不得完成Dispose，解除各自原gate后再独立收尾 |
| IR-S1-11 | Simulator/Engine Factory同步throw及factory迟到、consumer业务错误+Payload cleanup委托/Simulator.Dispose错误同次（注入位置见表后）：根在Factory前，错误分开保留，不覆盖业务错；Engine cleanup异常仍启动独立Payload cleanup，Session在Engine仍借用时不Dispose；原ValueTask只AsTask一次，不靠第二次Dispose忘掉失败Task |
| IR-S1-12 | Host只观察到期、接收ACK丢失、late Execute或late lease/Read clone：原Task/输入/map/result/lease强持；consumer结束后late Payload.Dispose调用一次，lease完成后归预算，未ACK不删原根。cancel到来若先于发布门没有late成功，发布提交后才允许late Completed闭包不改写 |
| IR-S1-13 | module/options/schema升级拒绝未知值；Engine epoch变化不把旧请求当新ID恢复，Store PublishId身份独立；停止新请求→收原Task/receipt→独立关闭→新实例，旧根未确定不能声称回退成功；不以Simulator成功提升C3/C4/C5/WPF资格 |
| IR-S1-14 | 快照最大records/text/实际bytes有界、Revision单调，Control规则/gate满拒绝、重复release幂等、错Operation/fault R0001；Skip/零case/未完成闩锁/断言错分别故障模式非零，stdout列case ID，原恢复根隔离计数和未执行backend清楚可读 |

统一finite runner沿§13.1：case5s、每个Host suite30s、外层run60s、build180s；harness止值不是性能目标。故障gate由测试父Owner在独立闩锁任务中观察到断言后释放，固定TimeProvider只推进请求/TTL，观察墙钟真实走；case结束若root恢复尚未知必须非零并保留根至父Runner处理，不用Kill当真实归还。协议S1完全BCL才允许超期子进程Kill且记失败，无原native或DB资源；实际C3/C5进程不适用。--case-deadline-ms/--suite-deadline-ms仅接受明确正值且不超过上述冻结上限，不经参数放宽挂死等待；结果0仅在A/B所选Host全部必需ID真实完成、所有资源root/receipt已安全处置。对应用能力无外部门，生产样本/耐久/光学门另列。

IR-S1-09共享Store变体在每个Host case内创建两个Engine并注入同一bundle.MapStore；两请求使用同一冻结asset/目标/窗口/layout以得到同key，RequestId和Engine epoch各不相同。bundle根显式登记两个借用者，二者均关闭且原Store操作结束后才调用bundle.Dispose，不用两个Host正常fixture的不同asset假装同key冲突。两个独立bundle变体各自独立Dispose。

IR-S1-11的Factory迟到、consumer及cleanup异常由harness私有单次委托闩锁注入，不给模块增加产品故障入口。Factory malformed-options异常调用真实factory；迟到在返回写根后、原FactoryTask完成前等待harness gate。consumer异常在借用过程中抛出；Payload cleanup委托先登记并单次调用原Payload.DisposeAsync().AsTask，在其真实退出后故意抛测试异常，根分别保留原Dispose Task与委托Task并记录已释放证据，不能伪称真实Payload.Dispose失败。Simulator cleanup委托同样只在原Dispose完成后抛测试异常；测试必须断言原Dispose成功与委托失败分别存在，不报告未注入的真实释放失败通过。真实Dispose失败的隔离规则仍按§11.2，但S1公开故障API不提供不可恢复的释放失败。失败槽保持至父Runner核对后按已知资源证据处理，不重复Dispose；未释放资源的真实失败持续隔离且非零。Engine cleanup异常沿§11.2私有委托验证独立支路，不通过更改Engine/Simulator原返回值制造PASS。

从仓库根执行的未来命令（本轮不创建工程、不运行）：
```powershell
dotnet build src/Modules/image-rectification/Asun.Modules.ImageRectification.Simulator/Asun.Modules.ImageRectification.Simulator.csproj -c Release
dotnet build tests/Modules/image-rectification/Asun.Modules.ImageRectification.Simulator.Tests/Asun.Modules.ImageRectification.Simulator.Tests.csproj -c Release
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Simulator.Tests/Asun.Modules.ImageRectification.Simulator.Tests.csproj -c Release --no-build -- --slice S1 --host A --case-deadline-ms 5000 --suite-deadline-ms 30000
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Simulator.Tests/Asun.Modules.ImageRectification.Simulator.Tests.csproj -c Release --no-build -- --slice S1 --host B --case-deadline-ms 5000 --suite-deadline-ms 30000
```

benchmark诊断按§14及DEV-GOV-010统计口径：fixture A/B、Points/Contour/Image、cold miss/warm hit、CachePolicy Disabled/ReadThrough/RequireHit、1/2并发、delayed consumer、Unknown/hold/invalidate、small quota、不同窗口分组；每profile冻结Options/输入hash/schema/后端版本/时间推进和allocation上限。测点为Factory预约/构造、Plan/Acquire、copy bytes及held parent容量、Prepare/Read/Publish/Query、资格回读/Watch收尾、consumer/结果Dispose、Engine/Session Dispose、pending receipt隔离字节，端到端Accepted→ResourcesReleased并另计Terminal、原副作用回执确知。记录nearest-rank P50/P95/P99和n、失败/删失/unknown root，不用fixture NativePeak=0证明真实HALCON资源。测量次数/预热/延迟阈值取实际消费者BenchmarkProfile，未采纳时NotEvaluated；Root quotas与5s等是软件安全界限，不造客户节拍或生产达标。

### 13.3 C3/C4/C5与WPF的独立实施验收计划

本节是同模块后续工程的必需计划，不标为已执行。C3/C4只在§19 Native.Acceptance中执行，C5在Adapters.Acceptance，UI仍在Wpf.Acceptance；Core/S1既有case、73/402byte规范向量与预算反例直接复用，不重复重建，不以本文新增数学期望冒充native测量。工程/方法未实现、原task未退出、必要case跳过或profile缺失都不得给出该运行门PASS。

Native两个Host从空进程沿§11.4同一根/Factory/Engine/Execute/Consumer/独立cleanup顺序装配；将synthetic-protocol资产/backend/store换为真实AsunImage工厂与本测试工程私有、可控的frame/asset/qualification端口，不改变Core API。两Host的raw像素/hash/来源revision沿§11.4：A=[10,20,30,40,50,60,70,80,90]，B=[11,21,31,41,51,61,71,81,91]；CameraModel=area_scan_division，CamParamIn=CamParamOut=[0.01,0,0.00001,0.00001,1,1,3,3]（Focus/Sx/Sy为m、Kappa为0），Target.FullSize=3×3/PrincipalPoint=(1,1)/CenterRowColumn，A OutputWindow=(0,0,2,2)、B=(0,1,2,1)。asset引用为各自独立Native-A/Native-B，rawHash由既有常量核验；测试资格为明确的synthetic authority与已冻结scope/3×3 Full域，不能接生产。CachePolicy=Disabled，Store=null，backend只开已声明Byte Image/SourceWindows，Coordinates能力本例可为null；输入到consumer均独立，不共享map/native/Dispose权。

每Host显式提供自己的CoreLimits与工程预算，复用S1的小输入Limits及8MiB根，native/working池按该验收环境冻结的LimitsDeclaration提供，不填未验证的HALCON开销。若工程声明不足、未知或本机实际超过，必需case失败/NotEvaluated，不能为了跑例放宽契约。factory同步验证/局部清理、原native Task、frame lease/Store Query、consumer/result/Backend Session/Engine Dispose均在Factory前已有根中单次登记；Engine关闭后再独立关闭backend Session，frame/asset端口Owner最后关闭。观察到期Main非零而恢复根仍在，真实native进程不Kill作为释放证据。正常像素期望A=[10,20,40,50]、B=[21,51]，Size=2×2/1×2、域Full、Mapping保留Target完整3×3与窗口原点；这是零畸变整数中心的数学期望，真实operator结果必须另测，不能用S1代替。

| 必需ID | 输入/反例与判定断言 |
|---|---|
| IR-N-01 | 上述Native A/B整数中心identity；结果像素/plane类型/channel次序、完整坐标和局部域逐项一致，源码输入不修改，原frame/map/native清理后result仍可读；result.Dispose后访问失败，不把图像未产生当PASS |
| IR-N-02 | 四种§5.4模型分别用资产冻结的参数范围，验证points/XLD原序、显式Closed临时末点去除、open首末相同不误闭合、分段不连接、有限值与全批拒绝。零畸变正向点与换基用解析identity；非零畸变正反差由已采纳方法Profile判，不能从调用成功推精度 |
| IR-N-03 | 真实HALCON生成map和缓存round-trip int4/已声明int8与四uint2；五通道/字节长度/key/hash完全匹配，私有重建后全cell校验才Run。int8用gen_image_const，不截断索引/指针；没有XL真实声明时int8 case为能力拒绝用例，不声称int8运行通过 |
| IR-N-04 | 最后一列、1×N、zero-weight越界、有效域洞、全部无效/Unknown；Reject策略无成功payload，Conservative私有改写所有无效cell且有效域不扩大，原缓存跨实例不变，map_image前每cell安全。危险map只测试构造/校验，禁止故意把非法指针送进算子 |
| IR-N-05 | Byte/UInt16/Int16/Float32、1～4channel、多plane、负stride源、row padding、RGB独立值和alpha；源端口仅CopyRow精确逻辑行，native导入解交织/导出重新交织不换channel/位深。Float32有效域NaN/Infinity拒绝；任何channel失败整批无输出 |
| IR-N-06 | 共同源/目标完整模型的整图与不重叠/1px/边缘窗，比较共同有效域与seam、source四邻halo/中部极值、窗口父坐标。数值差/灰度权重量化按§5.6分项，不能拿某窗口正确替代全部窗口覆盖；跨FOV/新revision/缺tile/外推明确拒绝 |
| IR-N-07 | 实际native/probe/copy/资格回读/观察器/lease归还各安全边界取消/超时，已在native不强制Dispose；任何真实work未结束维持DrainUnknown和原Task/预算。原结束后按原原因收尾，原Task不换、不再生成map；双Session取消A不影响B |
| IR-N-08 | 冷/热缓存、最大已声明规模、双实例/模块并发×HALCON内部并行、长稳和迟到消费；统计managed/native/cache/源held容量，确认LimitsDeclaration变量/固定界限，超界归资源门失败。CPU线程/系统设置保持宿主值，P50/P95/P99与最低n/目标沿Profile |
| IR-A-01 | C5真实wrapper在原Owner端口已有正确key/schema/hash的正常/坏内容/发布失回执、活IO/明确NotFound、sameID同hash一次显式重试和不同hashConflict；GetRecovery原ID可找，Unknown不可命中、不无界重查，不依赖snapshot恢复已Dispose的副作用 |
| IR-A-02 | 同一冻结父frame跨tile精确source租约、缺tile/新revision/错误布局、whole-parent held容量及复制峰值；真实Read/lease Dispose迟到有原Owner，消费者只取同帧原像素、不融合。source端口真实接线和支持域不可由模拟证书替代 |
| IR-A-03 | 原Owner返回/异常前本地IO/回调确已退出；远端回执Unknown与本地HasLiveOperation分开。关闭仍可Query原ID，原Dispose等待Unknown确知且新mutation拒绝；业务错误/cleanup错误分轴，receipt/tombstone容量满不忘ID重新执行 |
| IR-A-04 | 持久Owner原Published/NotFound确定性、写入/flush/内容hash/原子索引、进程恢复与孤立内容隔离按Owner正式契约检验；本模块wrapper无DB、目录或flush实现，不篡改业务事实。Owner未提供原证据则持久资格NotReady，不能用Memory模拟替代 |

WPF UI-R01～06补充精确断言：PropertyGrid未提交非法值不触发Core、culture切换不改变参数bits、Grid筛选不改Index或结果、1:1/fit与pan/zoom只改显示；联动缺Project能力时关闭且IsValid=false；资源表覆盖§8全部22个错误与实际枚举/字段/提示/UIA，无裸MessageKey或native异常代替恢复。外来布局不传RestoreLayoutFromStream，可信旧schema异常回默认；固定1920×1080/current DPI下校验、执行、取消及状态一直可見。两个独立STA Host和同Engine双控件分别验证，真实预览/排空证据另测。

这些harness命令从仓库根指向§19同一既有规划工程：Native.Acceptance的`--slice C3 --host A/B`与`--slice C4 --host A/B`分别执行适用IR-N，Adapters.Acceptance的`--slice C5 --host A/B`执行IR-A与IR-N-06的端口侧断言，Wpf.Acceptance的`--host A/B`执行UI-R。每个参数组合必需ID固定列举、未知slice非零，复用§13.1的stdout列ID和有限观察规则；原native挂起保留长期恢复Owner而非强杀通过。纯数学/合成控制case的5s/30s stop值可复用；真实native/UI/持久IO的case/suite/外层观察期限从该环境已采纳的有限Profile提供，缺少时NotEvaluated，不把客户节拍、HALCON停止语义或释放上限编成5s。运行资格要求所有适用断言真实执行且全部原资源已安全处置。

Native/Adapter/UI未来命令的确切入口示例（仓库根；先构建§19对应工程且非零不运行，本轮未执行）：

```powershell
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Native.Acceptance/Asun.Modules.ImageRectification.Native.Acceptance.csproj -c Release --no-build -- --slice C3 --host A
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Native.Acceptance/Asun.Modules.ImageRectification.Native.Acceptance.csproj -c Release --no-build -- --slice C4 --host B
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Adapters.Acceptance/Asun.Modules.ImageRectification.Adapters.Acceptance.csproj -c Release --no-build -- --slice C5 --host A
dotnet run --project tests/Modules/image-rectification/Asun.Modules.ImageRectification.Wpf.Acceptance/Asun.Modules.ImageRectification.Wpf.Acceptance.csproj -c Release --no-build -- --host B
```

每slice还必须按相同入口交换A/B各一次，不能只执行例示Host；环境Profile的原内容/hash在harness启动摘要中冻结并验证有限值，无有效Profile则非零/NotEvaluated，不读产品Shell或隐式最新配置。所有Native/Adapters原根和状态在进程维护服务中可恢复，外层到期只报告观察失败，不把命令进程消失当释放；两STA Host在同一固定1920×1080验证viewport先后验证，不新增分辨率矩阵。

## 14. 性能和资源预算

`BenchmarkProfile` 的公共样本计划、时钟、失败处理与阈值语义按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 冻结。本模块专属维度包括具体帧宽高/像素格式/stride/ROI、径向资产与 map key revision、冷生成或缓存命中、插值路线、有效域比例、点/XLD 数量、缓存状态、慢消费者/双实例/并发负载、`MaxOutputBytes`/缓存/native 内存上限及资源预算；资源上限由消费者按宿主容量提供。本模块不预设毫秒、点数倍数或 payload 目标。

本模块测点覆盖端到端至安全终态（分别记录ResourcesReleased和发布门耗时）、map生成/校验/缓存、native映射、边界/有效域检查、复制、发布前资格回读、请求观察器/回调收尾、取消至全部工作真实结束、lease归还和峰值资源；冷生成与热命中、整图/点/XLD、不同尺寸/ROI和并发分别分组。分位算法、失败/删失样本、真实排空和目标缺失时的判定统一按 DEV-GOV-010 §3.1 执行。

负向/压力矩阵必须覆盖冷/热、慢消费者、双实例、缓存满、负 stride、取消和低内存。若 Profile 无法满足，宿主应拒绝该规模或提交新请求；模块不能静默降低插值质量、域要求或目标精度。

## 15. 可观测性

每次请求生成结构化 trace，至少包含：`RequestId`、实例 epoch、操作、输入 frame ID/revision/hash、资产 ID/revision/hash/scope、完整 cache key hash、适配器和算法版本、HALCON 版本声明、线程/设备、输入/输出尺寸与 stride 摘要、插值/边界/域策略、状态时间线、native 调用耗时、队列等待、复制字节、峰值资源、有效像素比例、域外/无效数量、错误码和排空结果。日志不能写入完整图像或敏感路径，原始证据由调用方按其 Owner 保存。

指标建议：`rectification_requests_total{operation,state,error_code}`、`map_cache_hit_ratio`、`rectification_duration_ms{stage}`、`invalid_domain_ratio`、`native_inflight`、`buffer_bytes_in_use`、`drain_duration_ms`、`drain_unknown_total`。指标和诊断是只读投影，不能作为业务事实或放行条件。

## 16. 版本兼容、发布和回退

- 契约采用独立 Major/Minor/Patch；新增可选字段和诊断不破坏同 Major；改变坐标、单位、map 方向、默认插值、域语义、资源所有权或错误终态必须升 Major。
- `RectificationCacheKey` 始终含算法/适配器版本和 map schema version。旧 map 不能因 hash 正确就在新 schema 下复用；迁移器必须读旧内容、完整验证、写新内容并产生新 hash，失败则拒绝使用。
- CalibrationAsset 的版本、资格和内容 hash 由 `PKG-015` Owner 管理。模块发布只能声明支持的资产模型/版本范围，不能自动激活或转换未经批准的资产。
- AsunImage/HALCON 适配器按能力矩阵声明支持的像素格式、mapType、线程和边界；目标运行库不满足能力时返回 `R0017/R0010`。不在运行时扫描内部、下载替代库或偷偷切换算子。
- 发布包包含 Core、适配器、公开契约、能力清单、变更记录、测试/Golden 版本、依赖版本和回退说明。回退先停止新请求→排空/隔离在途资源→恢复上一兼容包和上一 map schema→重新验证资产 scope；不能以替换 DLL 复活已撤销资格。
- 只有在新版本通过契约、布局、坐标、取消/排空、两个消费者和适用 Benchmark 后，宿主才可把新版本作为候选；当前逐片规格接收状态见 §19.1，不代替版本运行资格。

## 17. 第二消费者接入和责任分割

### 17.1 识别/定位工具的按点消费者

工具提供合法点集及其 source frame/坐标声明，请求 `Points` 或 `Contour`。模块返回同序坐标、逐项有效性、映射描述和 trace。定位工具自行把校正坐标关联到目标、计算姿态或决定候选；模块不保存目标 ID、不选择唯一候选、不判断定位成功。

### 17.2 拼接/计量工具的整图消费者

工具提供 tile/整图帧和输出几何，按 `Image` 请求派生帧。模块返回父坐标映射、有效域和租约，工具自行处理重叠拓扑、缝合、量测对象、单位和资格。校正图的存在不表示拼接完整或量测合格；计量工具必须保留原始图和校正 trace 作为证据关联。

两个消费者应在同一 Core 包上运行而不修改核心；它们可以使用各自独立的输出尺寸和已资格资产，首发插值固定为 bilinear，缓存键和实例状态必须隔离。接入验收至少证明：按点不生成整图、整图有效域不被显示填充扩大、两个实例取消互不影响、同一源 revision 可回溯到相同资产闭包。

## 18. 场景驱动架构复审

本节按怀疑式反例重走运行链。每个场景都必须能从输入快照、参数来源和处理顺序推导出唯一的状态/错误、恢复动作和验收断言；只写“调用 HALCON 后返回”不算闭环。除非特别说明，参数来源为宿主冻结的 `RectificationRequest`、`PKG-006` 帧 lease、`PKG-015` 资格资产和已登记的运行 Profile。

### 18.1 正常配置、空输入和部分成功

| 场景 | 输入与参数来源 | 处理顺序 | 输出/状态/错误 | 恢复和可判定验收 |
|---|---|---|---|---|
| 合格径向整图 | 面阵帧；资产 scope、`CamParamIn/Out` 和 mapType 来自资格快照；输出尺寸来自 TargetGeometry | layout→资格→cache key→map 结构/邻域→`MapImage`→domain→publish | `Completed`，派生帧 lease、mapping、trace | 同一输入/资产/Options 重放得到同一尺寸、映射 hash 和有效域；原帧可继续被其它消费者读取 |
| 合法按点 | 非空且等长 row/column；中心/corner 和 batch policy 来自请求 | finite/范围→坐标桥→点算子→逐点域检查→publish | `Completed`；不生成整图 | 输入顺序和输出顺序相同；没有隐藏图像分配；第二次执行不改变第一次结果 |
| 空点集/空轮廓 | `Points.Count=0` 或 XLD 无对象 | 在 native 前验证 | `Rejected/R0001`，无原生资源 | 调用方修正目标集合；不得返回空成功或把空集合视为“全部通过” |
| 部分点越域 | 批次含合法点和域外点；唯一 AllOrNothing | 变换候选→逐点域判断→排空→拒绝 | Rejected/R0009，无 Payload/Domain/Mapping | 不删坏点、不返回半条轮廓；AllowPartial/未知枚举在接纳前 R0001 |

### 18.2 歧义、错误输入和不支持能力

| 场景 | 输入与参数来源 | 处理顺序 | 输出/状态/错误 | 恢复和可判定验收 |
|---|---|---|---|---|
| 坐标约定歧义 | source 声明 row/column 与请求 center/corner 不一致或缺失 | 先比对 Frame/Target/asset 声明，再调用任何算子 | `Rejected/R0007` | 补齐唯一坐标声明后重试；同一缩放反例不能出现半像素偏移 |
| 帧/资产版本错配 | ROI、分辨率、binning、镜头或 hash 与资格 scope 不符 | layout→scope 比较→不读旧 map | `Rejected/R0003/R0005/R0006` | 重新获取匹配资产或新 map；不能用“宽高相同”放行 |
| 映射类型歧义 | map 通道数、semantic type、输出尺寸与 Options 不一致 | manifest/schema→map 内容→邻域检查 | `Rejected/R0008` | 由 cache Owner 删除/隔离损坏项；不得把一通道 map 当双线性 map |
| 线阵透视、双目或世界平面请求 | 请求要求 `gen_radial_distortion_map` 处理线阵透视，或要求 stereo/world-plane rectification | capability check 在 map 生成前执行 | `Rejected/R0010` | 转交定位/标定/3D 专用模块；本模块不做降级变换 |
| 非法参数/恶意输入 | NaN/Infinity、负尺寸、溢出 stride、超大超时、未知枚举、重复 RequestId | 强类型解析和 checked 范围验证→不占 native 资源 | `Rejected/R0001/R0002` | 记录拒绝原因和 request hash；不会因异常输入改变缓存或全局状态 |

### 18.3 超大输入、高并发、噪声/遮挡和退化

| 场景 | 输入与参数来源 | 处理顺序 | 输出/状态/错误 | 恢复和可判定验收 |
|---|---|---|---|---|
| 超大图/超大 ROI | 尺寸接近上限，`MaxOutputBytes` 和宿主预算已冻结 | 先计算 payload/缓存/临时 map 上限→预占预算→再生成/执行 | 预算不足 `Rejected/R0011`；不以 OOM 作为正常控制流 | 调用方缩小明确 ROI、分块或排队；预算预占失败不留下 map/lease |
| 高并发双消费者 | 识别按点与拼接整图同时请求同一源 frame；每个有独立 epoch | 每任务独立 request/lease；只共享不可变 map；限流和背压 | 可分别 `Completed`、`Cancelled` 或 `R0011`；不共享可变输出 | 取消识别不释放拼接仍持有的 frame；峰值内存、队列等待和租约归还可观测 |
| 噪声/反光/遮挡 | 图像质量低但几何 map 合法；质量分级来自输入 Frame/上游质量模块 | 本模块只检查布局/domain/asset，不从灰度重新估计畸变；按域执行 | 几何可能 `Completed`，质量元数据保留输入等级；不生成业务 PASS/NG | 下游若要求质量门，由下游拒绝；模块不能因“看起来噪声”偷偷重训或切换算法 |
| 退化标定/奇异映射 | map 局部折叠、极大位移、非单调网格或输出有效域为空 | map 几何/有限值/单调性/域覆盖检查→再执行 | `Rejected/R0008/R0009` | 标定 Owner 重新资格或撤销资产；不能通过裁掉失败区域宣称整图成功，除非请求明确允许并返回保守域 |

### 18.4 取消、超时、native 排空和资源上限

| 场景 | 输入与参数来源 | 处理顺序 | 输出/状态/错误 | 恢复和可判定验收 |
|---|---|---|---|---|
| map 生成中取消 | `CancellationToken` 在 `WaitingForMap` 或 map 生成阶段触发 | 停止新工作→适配器取消→等待 map native 完成→有证据时释放临时 map/预算 | 已排空 `Cancelled/R0012`；无法证明结束则进入 `DrainUnknown/R0015` 非终态 | `DrainUnknown` 时隔离 worker/内存并报警；不得发布结果、释放 lease、把旧 map 标成新 map 或立即复用同一 native handle |
| `MapImage` 执行中超时 | deadline 到达，native 仍可能读取 frame/map | 记录 timeout→发取消→等待同步凭据→排空 | 有排空证据才是 `TimedOut/R0013`；否则 `DrainUnknown/R0015` 非终态，无成功 payload | `DrainUnknown` 时重试必须查询/等待原 request；旧结果不能覆盖新 epoch；资源仍在用时禁止强制释放 |
| 关闭/窗口卸载 | 宿主停止接收，存在多个在途任务和 UI read lease | `Quiescing`→取消新任务→在途 drain→撤订阅→释放显示 lease | 已安全排空的请求才可进入 `Closed/R0016`；未排空保持 `DrainUnknown`，不发 `Closed` | 进程重启恢复由宿主/适配器 Owner 处理；不能用窗口关闭证明 native 已停止或资源已释放 |
| 资源达到上限 | map、frame、native内存或并发 permit 用尽 | 接纳前拒绝，保留已使用 ID | Rejected/R0011 | 释放后新 RequestId 重放；无孤儿 allocation |

### 18.5 持久化、版本修订、升级和回退

| 场景 | 输入与参数来源 | 处理顺序 | 输出/状态/错误 | 恢复和可判定验收 |
|---|---|---|---|---|
| map 持久化成功 | map 内容、schema、cache key、依赖资产 hash 和能力版本组成 manifest | 写临时内容→完成写入并校验 hash/尺寸/schema→原子发布 manifest→读回验证 | `Completed`（缓存可用）；持久化回执属于缓存 Owner，不是业务提交 | 重启后只接受完整 manifest+内容；任何缺块/hash/schema 不符返回 `R0008` 并重建，不能读“latest”猜测 |
| 内容写入成功、manifest/索引失败 | 独立PublishId绑定key/hash | 临时内容不进cache；QueryPublishAsync查原回执 | Unknown/Failed+R0022；ReadThrough可保留已通过资格的计算结果但记录缓存失败 | 仅回执NotFound才同PublishId重试；不把缓存失败记nativeR0014 |
| 资格资产修订/撤销 | 固定asset revision与q0/q1；通知新revision或撤销旧revision | 新revision不热换；撤销/epoch改变/gap先禁发布再排空 | 安全释放后Rejected/R0005；排空未知不返回 | 旧Completed不改写，宿主消费重新确认当前资格 |
| 向后兼容升级 | Core minor、adapter patch 或 map schema minor 变化 | 能力协商→读取旧 manifest→显式迁移或重新生成→双版本回放比较 | 不兼容为 `R0017`；兼容才允许新请求 | 迁移失败保持旧包可回退；旧 map 不因 hash 正确自动跨 schema 使用 |
| 回退 | 新版本出现错误或不满足 Profile | 停新请求→排空/隔离→恢复上一包/上一 schema→重新验证 asset scope | 回退过程可观测；在途 `DrainUnknown` 不冒充旧版本成功，也不提前释放资源 | 只有排空证据成立且隔离资源仍由恢复 Owner 负责时，才可完成回退；至少一组 Golden、取消/排空和两个消费者回放通过后才恢复接收 |

### 18.6 无 UI、可选 UI、第二消费者和长期运行

| 场景 | 输入与参数来源 | 处理顺序 | 输出/状态/错误 | 恢复和可判定验收 |
|---|---|---|---|---|
| 无 UI 回放 | 文件/Replay 适配器提供不可变 frame、asset、Options 和 input hash | 完全走 Core 校验→适配器→结果 trace；不创建窗口 | 与生产调用同一终态和错误码 | 移除 WPF/DevExpress 引用仍可构建最小宿主；结果与 UI 路径一致 |
| 可选 WPF 预览 | UI 只读结果、域、版本和失败原因；语言/主题由宿主注入 | UI 命令调用 Core 同一校验；预览 lease 独立；关闭按 drain 流程 | UI 只投影状态；不新增业务状态或判定 | 键盘/UIA/三语和 1920×1080 视口可用；卸载不泄漏 lease；无订阅者核心仍完成 |
| 第二消费者：识别/定位 | 少量点/轮廓、候选目标由消费者持有 | 使用 B/C 路线；模块不读取目标表、不分配目标 ID | 返回几何结果、域和 trace；消费者自行做匹配/姿态/拒识 | 不产生整图；两个实例参数互不串；迟到结果按 request epoch 丢弃 |
| 第二消费者：拼接/计量 | 显式窗口/原图、父坐标及overlap由消费者持有 | 使用A，D不支持；返回派生托管像素/父坐标/域 | 不声明拼接完整或量测合格 | 域洞不填补、source/asset/key可回溯 |
| 长期运行/缓存压力 | 连续任务、资产轮换、周期取消、慢消费者、磁盘满或临时目录不可写 | 有界 cache/queue；定期能力和资格回读；统计 lease/bytes/DrainUnknown | 单任务终态不污染后续；资源超限 `R0011`；`DrainUnknown` 不计为终态，隔离资源必须持续可追踪；持久化失败可恢复 | soak 运行观察句柄/内存/线程/缓存增长；进程重启后无孤儿 map；无静态当前标定 |

本节的“噪声/遮挡”只作为输入质量和域语义，不能扩展为在线训练或工艺解释；“长期运行”只验证资源和版本生命周期，不能把统计稳定性当作计量资格。所有场景的业务放行、目标关联、设备动作和提交回执仍由调用方 Owner 负责。

## 19. 实施切片和准入门

模块契约0.2.0是Core唯一规格，模块资源Owner见§3/附录A；平台Contract/产品Owner采纳仅属于产品映射与业务消费门。首个C1不削减整模块规划。C1/C2六项规格已由主控接收，逐片状态见§19.1；S1六项文档规格已接收为ModuleCoreImplementationReady，见§19.2；C3/C4/C5公开装配指导内容限定接收，真实native/Store与运行资格仍PreparationIncomplete/NotReady。本轮仅同步接收状态，不创建或实施下列工程。

| 切片 | 完整功能/消费者 | 唯一代码工程（仓库相对） | 唯一验收工程（仓库相对） |
|---|---|---|---|
| C1 | 请求/布局/规范域、冻结、预算和坐标换基，两个无UI工具均可调用 | src/Modules/image-rectification/Asun.Modules.ImageRectification.Core/Asun.Modules.ImageRectification.Core.csproj | tests/Modules/image-rectification/Asun.Modules.ImageRectification.Core.Tests/Asun.Modules.ImageRectification.Core.Tests.csproj |
| C2 | 同一Core内运行协调、状态查询、资格屏障、取消/排空、map schema/缓存端口；模拟点/图两个消费者 | 同C1 Core，唯一根命名空间Asun.Modules.ImageRectification | 同C1 BCL Exe，以--slice C2执行IR-C2必需项 |
| C3 | HALCON点/XLD，识别/定位无需整图 | src/Modules/image-rectification/Asun.Modules.ImageRectification.AsunImage/Asun.Modules.ImageRectification.AsunImage.csproj | tests/Modules/image-rectification/Asun.Modules.ImageRectification.Native.Acceptance/Asun.Modules.ImageRectification.Native.Acceptance.csproj |
| C4 | 径向bilinear map、全cell安全及域传播、整图，拼接/计量派生像素 | 同C3 AsunImage，native不泄漏Core | 同C3 Native.Acceptance，真实Golden/资源/取消门 |
| C5 | 虚拟源/精确source窗口、Store读写/回执、allocation预约，mosaic显式窗口消费者 | src/Modules/image-rectification/Asun.Modules.ImageRectification.Adapters/Asun.Modules.ImageRectification.Adapters.csproj | tests/Modules/image-rectification/Asun.Modules.ImageRectification.Adapters.Acceptance/Asun.Modules.ImageRectification.Adapters.Acceptance.csproj |
| C6 | 两类工具嵌入同一可选控件，参数/预览/候选移交与恢复 | src/Modules/image-rectification/Asun.Modules.ImageRectification.Wpf/Asun.Modules.ImageRectification.Wpf.csproj | tests/Modules/image-rectification/Asun.Modules.ImageRectification.Wpf.Acceptance/Asun.Modules.ImageRectification.Wpf.Acceptance.csproj |

C1/C2为net10.0，仅BCL；C3/C4直接引用现有AsunImage经cv2执行26.05算子；C5调用宿主公开帧/Store端口；C6为net10.0-windows/WPF引用本机DevExpress25.2.3。Native/Adapters验收规划为net10.0 Exe，Wpf验收为net10.0-windows/WPF Exe；精确样本/hardware/场景由后续验收切片绑定，不声称这些工程已存在。根模块工程目录和对应tests目录为未来准入切片允许路径，共享文件/其它模块/产品项目/AsunImage内部/只读来源全部禁止；新增共享引用必须原Owner接入，不在模块侧改共享契约。本轮只有指导可写。

最小调用顺序：C1以CoreLimits作无大分配预检→ValidateRequest→FreezeInput(显式backend/algorithm版本、Limits)→NormalizeCoordinates(...,Limits)；C2先根槽预约→factory注入端口→登记原Execute Task→有限GetStatusAsync/结果观察→consumer借用结束→独立Payload/Drain/Engine.Dispose cleanup→根接收确认与安全完成门；native图像遵循§5+附录A.5/A.6；可选控件Bind→草稿校验→预览→宿主Offer→Unbind/Close。外部端口不得用隐藏窗口初始化。

### 19.1 DEV-GOV-010 §3.1 六项规格位置

| 条件 | 唯一规格位置 | 本轮规格结论/适用范围 |
|---|---|---|
| 1. 边界、非目标、依赖及第二消费者 | §1、§3、§17；§19切片表 | 完整图/点/轮廓/窗口/缓存/UI规划保留，识别/定位与拼接/计量为真实复用计划 |
| 2. 当前模块API、事件/状态、单位/域、错误/取消/排空、版本/所有权 | §4、§6–9、§16、附录A.1–A.6；WPF见§10 | State/QueryCode封闭，map/域/窗口/资格/Owner由模块唯一指导冻结；平台映射另门 |
| 3. 无UI最小宿主与注入端口 | §1.3、§13.1、附录A.4 factory及A.5/A.6 | C1/C2的net10.0 BCL Exe最小Host已定位；外部适配不迫使Core猜API |
| 4. 正常/边界/错误/重复/并发/取消/超时/关闭/回退及判定断言 | §12/13/18、§13.1 IR-C1/IR-C2/IR-HARNESS IDs；§10.4 UI-R IDs | harness实际执行协议与必需ID明确；模拟控制流与真实HALCON/UI验收分开 |
| 5. BenchmarkProfile维度/测点/资源/分位/失败来源 | §14、附录A.2预算、DEV-GOV-010 §3.1统计口径 | 测量方法冻结；未提供消费者性能/物理目标只能NotEvaluated；软件测试截止不当性能目标 |
| 6. 唯一工程/测试路径、允许/禁止及调用顺序 | §1.3、§13.1命令、§19表和调用顺序 | 各切片唯一工程规划和最小运行协议明确；产品映射/真实样本/本机资格只影响对应后续门 |

2026-10-10，主控原会话 `01a1020f-126c-7242-97f9-0f50b4cd3553` 已回读 §4/6–10/11/13/14/19/附录A并逐项接收 C1/C2 上述六项规格。主控按独立字段重建完整402 byte Host A Input，全文hex/SHA一致；此前73 byte Domain及点/轮廓预算保持一致。这些是规范编码与预算规格核对，不是C#实现或图像Golden运行证据。

| 切片 | 主控接收结论 | 当前状态与仍保留的门 |
|---|---|---|
| C1 | DEV-GOV-010 §3.1 六项规格已逐项接收 | `ModuleCoreImplementationReady`，仅规格准备；工程构建、C1 harness及性能运行尚未执行 |
| C2 | DEV-GOV-010 §3.1 六项规格已逐项接收 | `ModuleCoreImplementationReady`，仅规格准备；BCL Simulator/双Host/恢复harness运行尚未执行，不获得生产资格 |
| C6 | 公开绑定、预览预算、内部BindingRoots移交/恢复、布局和三语指导内容已接收 | `PreparationIncomplete/NotReady`；真实WPF、产品接线及资格门未关闭 |
| C3/C4/C5 | 公开factory/options/Session及确定wrapper装配指导内容限定接收 | 真实native/Store与运行资格仍为 `PreparationIncomplete/NotReady`；窗口、样本及产品门继续按对应切片验收，不继承C1/C2/S1状态 |

本结论只接收相应规格范围，不标记整模块全面就绪。工程未创建/未构建不是“所有Core必须等产品Owner采纳”的设计门；实施后的编译、harness、图像Golden、性能和UI资格另行执行并记录真实结果。本轮不开始代码开发，结束后等待明确任务。

### 19.2 S1软件协议模拟切片的六项文档规格（已接收）

S1是同一独立模块已有C3/C4/C5的无真实HALCON/DB软件模拟装配切片，不新增独立模块/会话，不把C3/C4/C5真实能力替换为Simulator。2026-10-11，主控原会话 `01a1020f-126c-7242-97f9-0f50b4cd3553` 已内容回读A.7/A.8、§11.4完整A/B图像协议Host、§13.2与本节，并按DEV-GOV-010 §3.1六项文档规格接收S1为 `ModuleCoreImplementationReady`（仅规格准备）。本轮主控只做新S1内容回读，无新增独立向量重建或运行通过证据；没有实现/编译/harness或真实验收。C3/C4/C5公开factory/options/Session及确定wrapper装配指导内容限定接收，真实native/Store与运行资格仍为 `PreparationIncomplete/NotReady`。C1/C2既有ModuleCoreImplementationReady及C6限定内容接收不退回也不自动扩大。

| DEV-GOV-010 §3.1条件 | S1唯一规格与验收范围 |
|---|---|
| 1. 边界/非目标/依赖/第二消费者 | §11.4整窗Host A与显式窗口Host B，A.7/A.8 BCL端口和Memory store；只有protocol控制流，无光学/物理/耐久/WPF/产品事实/设备命令，依赖仅Core/BCL |
| 2. 当前API/状态/单位/Owner/版本 | A.7公开factories/options/Session/Store recovery，A.8控制DTO、模拟schema和故障规则，复用§4/6–9/A.1–A.6；count/byte/times/强持/lease/发布与Execute分离，生产schema拒绝fixture，不另造几何/质量判定 |
| 3. 两个最小无UI Host | §11.4完整DTO构造、逐Factory根登记、原Execute/consumer/Store Query、独立cleanup与ACK；A/B独立进程无外部draft/数据库/原生环境，软件模拟不依赖客户物理事实 |
| 4. 可判定正常/错误/重复/并发/取消/恢复/回退 | §13.2 IR-S1-01～14所有必需case、有限Runner和迟到原Task/unknown receipt恢复；独立expected字节、root计数/版本/hash/调用顺序，必需Skip/未完成非零 |
| 5. BenchmarkProfile/资源/失败来源 | §13.2诊断负载/阶段/根与receipt资源、§14/DEV-GOV-010统计口径；无阈值则NotEvaluated，模拟时间/内存不冒真实资源及客户目标 |
| 6. 唯一工程/测试/允许禁止/顺序 | 下表工程/namespace及§13.2仓库根相对命令；构造原Factory根→Engine借用→原Execute/查询→借用消费→独立result/Engine/Store/Bundle收尾→receipt确知/ACK→释放根。API和真实装配未决分别按C3/C4/C5门记录 |

| 项 | 唯一落点与形状 |
|---|---|
| S1代码DLL | src/Modules/image-rectification/Asun.Modules.ImageRectification.Simulator/Asun.Modules.ImageRectification.Simulator.csproj；Microsoft.NET.Sdk/net10.0/Nullable/ImplicitUsings；唯一ProjectReference为§1.3的Core.csproj，仅BCL；根namespace Asun.Modules.ImageRectification.Simulator |
| S1测试/两个Host | tests/Modules/image-rectification/Asun.Modules.ImageRectification.Simulator.Tests/Asun.Modules.ImageRectification.Simulator.Tests.csproj；Microsoft.NET.Sdk/net10.0/OutputType=Exe/Nullable/ImplicitUsings；只ProjectReference上述Simulator和Core；--host A/B两个进程，harness私有根/固定时钟同一tests工程 |
| Module Core装配类型 | A.7 Core session/options/recovery DTO定义补回§1.3既有Core.csproj/Asun.Modules.ImageRectification，唯一契约正文，不在Simulator定义第二份IRectificationBackend/IMapStore/Engine/Result；实际修改Core代码须另授实现任务 |
| 后续C3/C4与C5工厂 | AsunImageRectificationBackendFactory及AsunImage实现只落§19的AsunImage工程；RectificationMapStoreAdapterFactory只落§19的Adapters工程，引用Core与已注入Owner port不直接造DB；真实工厂/适配编译、资源和耐久门仍未执行，不纳S1测试工程引用 |
| 允许与禁止 | 未来S1实现只本表Simulator/Tests及明确A.7 Core装配类型范围，一写入Owner；禁止共享/其它模块/产品/原件/AsunImage内部/WPF/真实DB或下载依赖。本轮仅本DEVELOPMENT-GUIDE.md可写，不创建工程或脚本/新报告 |

精确后续门：C3为实际cv2点/XLD参数绑定（仅实质类型/重载歧义才查看公开签名/消费编译）、tuple/XLD有界分配、真实结束与结果/域Golden；C4为既有§5.3真实全部cell/私有SafeExecutionMap/native指针与输出/资源/取消资格和§5.4反查窗口同样本seam；C5为真实IFrameSource父revision/hash/跨tile租约/actual allocation、真实Store Owner的原PublishId/commit NotFound确定性、原IO排空、崩溃重启/flush/索引原子耐久证据及宿主精确接线。以上不因S1或factory构造提升，不把可决定的factory/options/receipt/query装配欠账转写为客户门。产品真实资产/物理范围/授权/提交事务、代表图像/performance/HIL仍按§21；AsunImage/DevExpress直接使用，不新增安装/兼容性/授权核验。

### 19.3 全部批准范围的文档准备结论（2026-10-11）

本永久原会话复用了既有固定源码/26.05资料、自审、C1/C2/S1有效规范向量与先前接收，本轮只补实际缺口；执行、内容审核、修复与定向文档验证均在本原会话完成，总控只调度与接收状态。按DEV-GOV-010十二项要求，当前全部批准范围的**可决定软件设计已闭合，文档准备完成**；没有另留算法、API、codec、适配器Owner/原任务、推荐或UI决定让后续开发者猜。该结论是文档准备结论，不给整模块或C3/C4/C5/C6新增代码Ready/运行资格，也不因少量Core接收省略后续能力设计。

| 全部批准能力/消费者 | 金标准唯一章节与准备结论 |
|---|---|
| 通用契约/冻结/布局/域/坐标与hash | §4/5/9、A.1–A.6：字段、单位、half-open/中心换基、首错、canonical/2和已有效Golden确定；物理资产hash保持原Owner身份，不重算改名 |
| 四种面阵模型的径向点/点集/XLD；识别与定位 | §5.2/5.4/5.5/5.6：具体cv2路线、参数来源/单位、分段/闭合/保序、全批拒绝、范围与误差确定；不要求生成整图，不负责求解标定或训练 |
| 完整图/显式窗口、映射缓存与有效域；拼接/计量 | §5.3–5.7、A.5/A.7：全cell安全、私有安全map、最小四邻源窗口、导入/导出/多plane/channel、Store事务与原ID恢复、域/坐标/资格/输出Owner确定；不自动分块或证明mosaic覆盖 |
| 超大虚拟源与帧/资格/持久Owner消费 | §4.2/5.7/A.6/A.7：准确参数桥、CPU exact样本、真实held容量、scope/lease/原IO与晚回执、独立关闭确定；本模块不另造帧服务、DB表/索引服务或资格批准 |
| 自动方法与参数建议 | §5.6/A.2：Operation派发唯一已批准路线、预算候选/排序/hash/失效/显式采用确定；不搜索模型、修改资产/插值/物理阈值、静默改生产参数 |
| 无UI双Host/公开Simulator与恢复 | §11/13.1/13.2/19.2、A.7/A.8：完整DTO/Factory前根、原Task/独立result和Session收尾、两级Unknown及有限查询确定；协议schema/Backend/Algorithm隔离，软件模拟不是生产资格 |
| 可嵌入WPF、三语和恢复 | §10.1–10.5：DevExpress25.2.3具体组件/公共属性、图像操作/联动、权限/键盘/UIA、默认布局/可信恢复/资源表及BindingRoots确定；无隐藏窗口/全局语言入口/另套视觉算法 |
| 正确性/性能/资源/交付 | §12–18、§13.3/19/21：正常/反例、原有效Golden、真实native两个Host、软件/Owner/窗口/误差/资源/UI适用断言、Profile负载/测点/失败判据与唯一工程路径确定；没有客户数值时NotEvaluated，不替实际运行 |

透视整平、世界坐标、标定求解/资格签发、任意/网格/tilt/线阵/GPU、融合map、辐射/颜色、运动、拼接拓扑、质量放行/设备命令都不在本模块当前批准范围；准确边界及有消费者的组合Owner见§1/5.6/17，不以“全模块”措辞新开功能。所有软件范围的工程实现与真实编译仍由本模块实施切片负责；不得把HALCON overload消费编译、变量内存界限验证或WPF真实接线写成等客户替模块设计。

剩余项只有按Owner取得的外部事实与实际实现/运行证据，精确责任见§21。批准资产/物理支持域/方法容差/客户节拍等外部事实缺失不阻断无关Core；未知native资源/Store结束证据阻断确实依赖它的运行门。不等待总控内容复核，不新增过程报告，不以文档完成代替测试或扩大本轮代码授权。

## 20. 自审清单（第二轮）

- [x] 仅定义独立校正能力；未写入制程判定、目标关联、质量放行或设备副作用。
- [x] 明确 Core、AsunImage 适配器、可选 WPF 和存储/回放适配边界。
- [x] 给出输入/输出、单位、范围、显式参数与草稿建议、同步/异步入口、事件顺序、状态和错误语义；不由默认建议改变运行请求。
- [x] 覆盖取消、超时、native 真实结束、资源租约、线程、缓存和关闭排空。
- [x] 明确 HALCON 26.05/`ImageLibDotNet` 核对要求；没有猜测未确认签名或把 AsunImage 内部当作依赖。
- [x] 包含无 UI 示例、可选 UI 契约、正常/边界/失败案例、测试矩阵、性能预算、可观测性、兼容/发布/回退和第二消费者。
- [x] 已按场景复审正常、空/部分成功、歧义/错误、超大/并发、噪声/遮挡/退化、取消/超时/排空、资源上限、持久化、版本修订、升级/回退、无 UI、UI、第二消费者和长期运行。
- [x] 已明确径向A、点B、轮廓C的唯一生产路线及D任意/网格的明确不支持；透视整平、训练、标定求解、世界平面、双目或线阵不在批准范围，没有隐藏fallback。
- [x] 已引用并核对 HALCON 26.05 operator pages 和 ImageLibDotNet 公共边界；未把算子页面或旧项目代码写成已验证生产实现。
- [x] 本轮按全部批准范围完成两轮定向内容自审：正常输入→实际operator/adapter→独立输出Owner，域不足/取消→原Task/lease/receipt恢复，空Host→Factory→关闭，以及UI编辑/联动/权限/语言/卸载。补充§5.5–5.7、§10.5、§13.3和§19.3/21；原有效研究/向量复用，不重审已接收片或创建过程材料。
- [x] 文档为0.2.1-prep、Module API仍0.2.0，C1/C2/S1文档规格已接收为ModuleCoreImplementationReady（仅规格准备）；C3/C4/C5公开装配内容限定接收，真实native/Store与运行资格仍PreparationIncomplete/NotReady；C6旧内容接收及运行/产品门保持，状态见§19.1/19.2。新S1只内容回读，无新增独立向量重建/运行通过声称。

## 21. 技术设计收口与外部门

本轮技术设计已在唯一指导自行冻结：有效域规范行段见A.4；派生map/Store归属、原子发布/回执及保留见A.5；撤销/快照/本地发布屏障见A.6；source窗口/halo/跨tile端口复用§5.4并由A.5精确定义；状态查询见A.2；控件生命周期/联动见§10；Core测试执行约定见§13.1。这些不再登记成等用户裁决项，AllowPartial和自动分块当前不支持，不作为隐含fallback。

接收范围：C1/C2规格及C6控件指导旧接收保持，见§19.1；本轮S1六项文档规格经原主会话内容回读接收为ModuleCoreImplementationReady（仅规格准备），见§19.2；C3/C4/C5公开装配指导内容限定接收，真实native/Store与运行资格仍PreparationIncomplete/NotReady，不再登记为等待本轮内容接收。产品具体字段/序列化适配、业务提交事务和宿主现有viewport实现的接入仍由真实接入切片补入本指导，不能在没有消费项目事实时编造。新的tilt/线阵/arbitrary map/GPU等能力不在当前批准范围；若新范围获批再修订唯一契约。

全部可决定软件设计的收口见§19.3。剩余外部事实与未执行证据按准确Owner分别处理，不把可设计的算法/codec/UI留成“客户待定”：

| 剩余项 | 准确Owner/提供内容 | 仅阻断的门 |
|---|---|---|
| 生产标定与资格事实 | calibration-assets/qualification原Owner提供准确Id/revision/hash、四种模型CamParam、物理支持域、配置/环境、有效期/权威水位、撤销和方法误差/不确定度Profile | C3/C4/C5的真实用途资格与下游消费；不阻断已确定Core拒绝/预算/规范编码 |
| 生产帧与窗口证据 | image-frame/source原Owner提供冻结来源内容hash/布局/actual allocations、准确tile/revision和CPU exact读取能力；宿主提供代表性原图、域洞/低质量/缺tile与独立真值 | 实际C5接线/Golden、C4全图与窗/seam；不能用S1或零畸变小例替代 |
| 物理/数值与性能目标 | 方法资格Owner和真实消费者提供灰度/点/轮廓/窗差与seam允许值、误差解释范围；宿主Profile提供尺寸/格式/并发/预热/最低n/deadline、P50/P95/P99/峰值/soak阈值与来源 | 相应算法与性能判定；目标缺失只NotEvaluated，模块不编造合格值 |
| 持久事务结束与耐久证据 | storage/MapStore原Owner提供原PublishId、确定Published/NotFound或Unknown、原本地IO退出、flush/hash/索引原子性、崩溃恢复；本模块实施者按A.7与IR-A验证wrapper | 真实Store/恢复/耐久资格；Memory只证明协议，不替外部事务 |
| 产品接入与投影 | 宿主产品Owner提供准确批准字段、权限/事务、显示源与原资产绑定的Preview/Project、主题/语言覆盖和配置储存；具体消息/参数/lease语义按本指导已定 | 该产品集成/输出长期Owner/应用候选接收，不改变模块API或授质量放行 |
| 本模块实际实现与native资源 | 本模块原会话实施者消费编译真实cv2参数/封送、完成C3/C4/C5代码与IR-N/IR-A、以部署负载确认LimitsDeclaration/变量内存、真实取消/排空及资源归还 | native/Adapter构建和运行资格，属于本模块未执行工程证据，不是等客户设计或封装覆盖/授权审查 |
| 真实WPF交付 | 本模块原会话实施者按§10与UI-R执行两STA Host、真实Preview、三语、固定1920×1080/current DPI、键盘/UIA/视觉和PendingDrain；宿主负责自己的显示/权限事实 | C6真实UI与宿主接线资格；文字/控件/布局/恢复设计已在本指导闭合 |

本轮未编码、未运行dotnet build/run/native/WPF，未取得性能、Golden、HIL、计量或生产结果。

## HALCON 26.05 算子资料入口

实现图像校正节点使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 的26.05语义；HALCON完整算子集已确定经cv2调用。不扫描内部、不核覆盖、不把一般公共签名核查设成门；仅具体类型、重载或封送歧义查公共签名或消费工程编译。

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

## 附录 A：唯一 Module API Contract 0.2.0（逐切片接收）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。每个切片只实施其绑定范围内已明确的公开类型、方法、事件、错误键、状态、参数和代码形状；本附录不把整图/native规格并入C1实施范围，也不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract 0.2.0` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- C1实现范围和路径以§1.3为准；整模块按§19 C1–C6规划。本附录中的 HALCON/native、整图执行、map cache、WPF 和宿主集成接口均为后续切片规格，不得由附录措辞扩大其授权。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- HALCON26.05完整算子集经cv2调用已确定。适配实现按本地手册执行；仅具体C#类型/重载/封送歧义查公共签名或消费编译。真实HALCON/WPF资格阻断对应切片，产品Contract/Owner采纳不阻断模块Core。
- 本附录不独立声明准入状态。具体Core切片须按DEV-GOV-010 §3.1六项条件在本永久原会话完成内容审核/修复/文档验证，明确范围、命名空间、唯一工程/测试及路径后记录结论；总控只接收状态、不代做模块内容审核。此前C1/C2/S1接收保持，当前状态见§19.1/19.2；全部批准范围的文档准备结论见§19.3，不由本附录授整模块代码或运行资格。

### A.1 `DrainUnknown` 不变量

以下规则属于核心状态和资源语义，任何 Core、Simulator 或适配器实现都必须保持一致：

- `DrainUnknown` 是排空过程中的非终态，不得加入 `RectificationTerminalState`，不得作为 `RectificationResult.State` 返回，也不得被业务 Owner 当作失败、取消或成功终态提交。
- 进入 `DrainUnknown` 后，`ExecuteAsync` 保持未完成；不得发出 `ResultPublished`、成功 `Payload`、消费者回调或 `Terminal`。此前未发布的逻辑结果必须丢弃或留在隔离区，不得由 trace、缓存命中或重试包装成可消费成功结果。
- 进入 `DrainUnknown` 后，仍可能被native、请求IO或观察回调访问的frame lease、map、临时图、worker、观察器和预算保持持有或隔离；不得发出 `ResourcesReleased`，不得因超时、窗口关闭、进程回退或 UI 退订提前释放。
- 只有取得全部请求工作可验证的完成证据后，状态才能回到 `Draining`，再依次发出 `Drained`、`ResourcesReleased`，最后按原始取消、超时、资格/域拒绝或执行失败原因发出对应终态。native完成不能替代资格IO和观察器完成证据。证据未取得时，状态持续为非终态并由恢复 Owner 追踪。
- `R0015` 仅是 `DrainUnknown` 的机器可读状态/诊断键；它不能单独完成请求，也不能把资源未释放解释为安全关闭。任何 UI、回放、指标和发布/回退流程都必须保留这一不变量。

### A.2 预算建议和精确状态查询

以下类型属于唯一模块契约，建议和查询均不创建 map 或 frame lease。

```csharp
public enum RectificationStage
{
    Created, Validating, Accepted, WaitingForMap, Running, Publishing,
    CancelRequested, DeadlineReached, Draining, DrainUnknown, Drained,
    ResourcesReleased, ResultPublished, Completed, Rejected, Failed, Cancelled, TimedOut
}
public enum ModuleLifecycle { Accepting, Quiescing, Closed }
public enum StatusQueryCode
{
    Found, UnknownRequest, EpochMismatch, RevisionNotReached, Evicted,
    InvalidQuery, Cancelled, TimedOut, ModuleClosed
}
public sealed record StatusQuery(
    string RequestId, long Epoch, long MinimumStateRevision, TimeSpan Timeout);
public sealed record RectificationStatusSnapshot(
    string RequestId, long Epoch, RectificationStage State, long StateRevision,
    DateTimeOffset ObservedAtUtc, bool IsTerminal,
    RectificationError? Error, RectificationTrace Trace);
public sealed record StatusQueryResult(
    StatusQueryCode Code, RectificationStatusSnapshot? Snapshot,
    long ActualEpoch, RectificationError? Error);
public sealed record BackendCapabilities(
    string BackendId, string Version, IReadOnlySet<PixelFormat> PixelFormats,
    PixelSize MaxImageSize, long MaxLinearIndex, long MaxWorkingBytes,
    long MaxNativeBytes, long MaxMapBytes, long FixedScratchBytes,
    int MaxConcurrentOperations, bool SupportsImage, bool SupportsPoints,
    bool SupportsContours, bool SupportsSourceWindows,
    CoordinateBufferBounds? CoordinateBuffers);
public sealed record CoordinateBufferBounds(
    string Version, long MaxPoints, int MaxContours,
    long ManagedFixedBytes, long ManagedBytesPerPoint,
    long ManagedBytesPerContour, long ManagedBytesPerDomainSegment,
    long NativeBytesPerPoint, long NativeBytesPerContour,
    long NativeBytesPerDomainSegment);
public sealed record ExecutionRecommendation(
    bool WholeOutputWithinBudget, PixelRect? SuggestedBudgetWindow,
    long EstimatedOutputBytes, long EstimatedWorkingBytes,
    RectificationError? Error, ContentHash InputHash, string RecommendationVersion);
```

唯一方法为 `ExecutionRecommendation RecommendExecution(RectificationRequest request, BackendCapabilities capabilities)` 和 `ValueTask<StatusQueryResult> GetStatusAsync(StatusQuery query, CancellationToken token)`，均属于 IRectificationEngine。查询在本次有限期限内读取原子快照，不等到作业结束。StateRevision从1单调递增；每个新状态或重要通知在引擎门内先更新快照，再以同revision发通知，后台通知/重传不另增revision；IsTerminal仅对五个终态为true。DrainUnknown始终false，Error可为R0015，不产生Result。

查询首错：非空ID/epoch>=1/minRevision>=0/Timeout为1ms..24h → token/deadline → epoch → ID → retained状态 → MinimumStateRevision。Found唯一允许Snapshot非空且Error=null；其它码Snapshot=null，Error非空：Unknown/EpochMismatch/RevisionNotReached/Evicted为R0019，InvalidQuery为R0001，Cancelled/TimedOut为R0012/R0013，ModuleClosed为R0016。RevisionNotReached不伪造更新或触发任务。Closed实例仍可查询保留终态；未知ID为ModuleClosed。Lifetime内已使用ID墓碑不删；StatusCapacity个快照按终态完成FIFO顺序淘汰，活跃/DrainUnknown不淘汰。RequestCapacity达到上限时R0011，不忘掉ID再运行。宿主创建时分配正epoch，重建必须新epoch；迟到事件按RequestId+Epoch+StateRevision过滤。

RecommendExecution版本固定budget-window/2。非Image分支不查map、不取得像素、不求图像窗口，也不以MaxImageSize/MaxLinearIndex或图像面积限制点载荷；来源/目标尺寸和域仍按契约校验。Point的n=1，Points的n=Values.Count，Contour的n=Vertices.Count、c=SegmentStarts.Count=Closed.Count，其它点操作c=0。坐标每点16 byte，段起点每项4 byte、闭合标志每项1 byte；逻辑载荷P=16n+5c。输出必须保留全部n/c及顺序，不能靠ProbeBatchPoints、分批或删点减少结果预算。

CoordinateBuffers.Version固定coordinate-buffers/1；后端按自身Version声明总峰值的保守界限，所有byte系数为非负Int64，MaxPoints/MaxContours为正且数组元素数还须<=Int32.MaxValue。ManagedFixedBytes覆盖请求、资产/资格快照、结果对象、数组头/对齐、hash/trace、IO/观察器等固定托管开销；三个ManagedBytesPer字段覆盖随点、轮廓、域段增长的全部额外分配，包括换基副本、row/column转换数组、输入/输出转换同时存活、canonical序列化缓冲、域复制和容器容量余量。FixedScratchBytes在此分支仅表示固定native开销；三个NativeBytesPer字段覆盖随数量增长且同时存活的输入/输出tuple、XLD对象、导出缓冲及native域等。不能用固定scratch替代可变tuple/XLD界限；未知界限必须CoordinateBuffers=null，不能填写猜测系数或以0表示未知。C1/C2模拟能力可给确定的合成界限，但不作为HALCON内存实测。

D=min(Budget.MaxDomainSegments,EngineOptions.MaxDomainSegments,CoreLimits.MaxDomainSegments)为全部请求域行段的总预约数，包含冻结来源/plane/资产/资格域、交集/工作/结果域，各副本分别计数；Full/Empty/Unknown零段但对象开销仍计固定项。EvaluateBudget无EngineOptions参数时以min(Budget.MaxDomainSegments,limits.MaxDomainSegments)为D，Engine用收紧后的Budget调用同一算法；实际总段数超过D即R0011，不以交集缩小绕过原始元数据额度。非Image预算统一checked Int64计算：

```text
P = 16*n + 5*c
M = ManagedFixedBytes + n*ManagedBytesPerPoint
    + c*ManagedBytesPerContour + D*ManagedBytesPerDomainSegment
N = FixedScratchBytes + n*NativeBytesPerPoint
    + c*NativeBytesPerContour + D*NativeBytesPerDomainSegment
O = P + 12*D + M
W = 2*P + 12*D + M + N
```

O是保守结果allocation预约（将全部域段和全部额外托管开销M计入结果上界，也覆盖结果池容量余量），EstimatedOutputBytes=O；W是冻结输入与独立输出候选共存、转换/元数据缓冲与native同时存活的总峰值，EstimatedWorkingBytes=W；N另外与min(Budget.MaxNativeBytes,Backend.MaxNativeBytes)比较，W与两侧MaxWorkingBytes比较，O与Budget.MaxOutputBytes比较，恰等于上限允许。O/W分别与自己的上限比较，不相加重复预约。调用方拥有且模块不保留的原始输入不占本请求预约；模块冻结后不保留原集合，任何保留原allocation的实现须另外预约其实际容量。逻辑P/12D不等于实际分配：池容量、额外副本、对齐和实际allocation全部由上述界限覆盖，分配前按实际容量复核预约；不足时R0011，不先分配再等待OOM。冻结前先无副本计数并预检，不能先复制大集合才发现额度不足。点路径无map/cache预约。能力缺失、未知/非法能力声明或数量超过后端/数组上限R0010；所有预算乘加溢出或超过额度R0011，非法请求预算仍按首错R0001。非Image的SuggestedBudgetWindow始终null，WholeOutputWithinBudget仅当上述预算全部满足为true，仍不证明资格成立；溢出时两估值均long.MaxValue、Error=R0011，不返回负值。

IR-C1-06合成数值固定n=20、D=4、ManagedFixedBytes=64、ManagedBytesPerPoint=8、ManagedBytesPerContour=16、ManagedBytesPerDomainSegment=4、FixedScratchBytes=64、NativeBytesPerPoint=12、NativeBytesPerContour=40、NativeBytesPerDomainSegment=0。Points(c=0)的(P,M,N,O,W)=(320,240,304,608,1232) byte；Contour(c=2、每段10点)为(330,272,384,650,1364) byte。这些是预算算术样例，不是HALCON实际开销或客户性能目标。

Image分支沿用原窗口算法：checked求N=输出像素数、按plane格式求payload字节，原map为N×(index字节4或8+四权重8)，预算计原map与安全map两份、native输出与托管结果、域最坏N段×12 byte、FixedScratchBytes和ProbeBatchPoints点缓冲。峰值还计读端口报告的实际allocation容量；共享整帧不能按小窗口面积降低保留成本。取宿主/后端各上限最小值比较。若整个请求超限，以请求左上为锚枚举合法宽度1..请求宽度，对每宽按单调字节公式二分最大高度，选最大面积，并列选宽者；均不可行窗口=null/R0011。SuggestedBudgetWindow只为预算候选，不改请求、不预约、不保证source窗口或几何资格；调用方显式新请求后仍执行§5.4逐像素探测。Image不要求CoordinateBuffers非空，其native/实际allocation界限由图像后端切片声明。

撤销/过期/资格Unknown接纳前为Rejected/R0005，接纳后阻止发布并排空，安全释放后Rejected/R0005。DrainUnknown查询可显示隔离资源计数，无载荷。历史Completed保持原闭包；重新应用由宿主重核当前资格。重复ID返回R0018，原任务不变。

### A.3 结果和资源 Owner 不变量

- `RectificationResult.Payload`、`Domain` 和 `Mapping` 只在 `Completed` 同时非空；`Rejected`、`Failed`、`Cancelled` 和 `TimedOut` 必须为 null。
- `ResultPublished` 事件只通知结果身份、版本和摘要；结果 Owner 通过自己的ExecuteAsync返回取得独立托管payload。事件订阅者不拥有工作 map、输入 frame lease 或临时 native 对象。
- `ResourcesReleased` 证明输入/native/map/请求IO和观察器工作资源已归还，不证明独立封存结果payload已释放；发布成功后结果Owner的Dispose与cache Owner的retained bytes由各自生命周期负责。发布门拒绝、取消、超时或失败时，引擎须在Terminal及ExecuteAsync返回前释放独立候选一次，不将其转交消费者。
- 取消、超时、失败和窗口关闭均先完成全部请求工作排空，再释放其工作资源；排空未知时所有可能被native/IO/回调访问的对象继续由恢复Owner隔离和追踪。外部共享Owner的全局订阅不属于本请求可Dispose资源。


### A.4 有效域、布局和运行 Core 的精确字段

以下表与§4的C#声明同为契约0.2.0，不是另一个DTO来源。括号按顺序列出全部公开字段；集合防御复制后只读。

| 类型 | 精确字段/枚举 |
|---|---|
| FrameSnapshotId / CalibrationAssetRef | FrameSnapshotId(Value:string)；CalibrationAssetRef(Id:string,Revision:RevisionId,Hash:ContentHash)；均非空 |
| PixelFormat / PlaneLayout | PixelFormat=Byte/UInt16/Int16/Float32；PlaneLayout(Format:PixelFormat,Channels:int,OffsetBytes:long,StrideBytes:long,RowBytes:long,AccessibleBytes:long,AllocationId:Guid,AllocationBytes:long,Domain:ValidityDomain)；Channels=1..4，格式由backend声明，浮点有效域内非有限拒绝 |
| DomainKind / RowSegment | DomainKind=Unknown/Full/Empty/RowSegments；RowSegment(Row:int,ColumnStart:int,ColumnEndExclusive:int) |
| ValidityDomain | (Size:PixelSize,Kind:DomainKind,Rows:IReadOnlyList<RowSegment>,ReasonKey:string?,Hash:ContentHash) |
| BoundaryPolicy / CachePolicy | BoundaryPolicy=RejectIfUnsupported/ConservativeValidDomain；CachePolicy=Disabled/ReadThrough/RequireHit |
| Interpolation / OutputDomainPolicy | Interpolation=Bilinear；OutputDomainPolicy=InputDomainIntersectionAndKernelSupport；唯一枚举值，未知值拒绝 |
| RectificationOptions | (Interpolation:Interpolation,Boundary:BoundaryPolicy,OutputDomain:OutputDomainPolicy,Cache:CachePolicy)；DefaultBilinearConservativeDomain仅为显式便利构造(Bilinear,ConservativeValidDomain,InputDomainIntersectionAndKernelSupport,ReadThrough) |
| CalculationIdentity | (ContractVersion:string,InputHash:ContentHash,Asset:CalibrationAssetRef,TargetHash:ContentHash,OptionsHash:ContentHash,BackendVersion:string,AlgorithmVersion:string) |
| FrozenRectificationInput | (Request:RectificationRequest,Identity:CalculationIdentity,FrozenAtUtc:DateTimeOffset)；CancellationToken不序列化，输入集合已复制 |
| RectificationError | (Code:string,MessageKey:string,Field:string?,DiagnosticKey:string?)；Code仅§8登记码，文字由语言资源投影 |
| ValidationResult | (IsValid:bool,Error:RectificationError?)；合法Error=null，非法Error非空 |
| CoordinateNormalizationResult | (Points:IReadOnlyList<PixelPoint>,Convention:PixelCoordinateConvention,Error:RectificationError?)；成功保序，不含校正/资格语义；失败点数组为空 |
| EngineOptions | (Epoch:long,RequestCapacity:int,StatusCapacity:int,MaxDomainSegments:int,TimeProvider:TimeProvider,Limits:CoreLimits)；正数；TimeProvider可注入固定测试时钟，Limits非空且按A.4.1冻结 |
| DrainCode / DrainResult | DrainCode=Drained/StillDraining/Cancelled；DrainResult(Code:DrainCode,OutstandingRequests:IReadOnlyList<string>,IsolatedBytes:long)；StillDraining不释放在用资源 |
| RectificationEventKind | Validated/Accepted/MapStarted/MapHit/OperationStarted/OperationFinished/ExecutionFaulted/StateChanged/ResultPublished/Terminal；Kind是通知类型，Stage是当前RectificationStage，不混为一套状态 |
| RectificationProgress / RectificationEvent | Progress(RequestId:string,Epoch:long,StateRevision:long,CompletedUnits:long,TotalUnits:long?,MessageKey:string)；Event(RequestId:string,Epoch:long,StateRevision:long,Stage:RectificationStage,Kind:RectificationEventKind,OccurredAtUtc:DateTimeOffset,Error:RectificationError?) |
| RectificationTrace | (Identity:CalculationIdentity?,Stages:IReadOnlyList<RectificationEvent>,SourceWindow:PixelRect?,OutputWindow:PixelRect,MapHash:ContentHash?,SafeMapHash:ContentHash?,DomainHash:ContentHash?,Authority:QualificationSnapshot?,OutputBytes:long,WorkingPeakBytes:long,NativePeakBytes:long,CacheRetainedBytes:long,IsolatedBytes:long,DiagnosticKeys:IReadOnlyList<string>) |
| CoordinateMappingDescriptor | (Source:InputFrameDescriptor,Target:TargetGeometry,SourceWindow:PixelRect?,Direction:MappingDirection,Interpolation:Interpolation,Boundary:BoundaryPolicy,OutputDomain:OutputDomainPolicy,DomainHash:ContentHash,MapHash:ContentHash?,AlgorithmVersion:string,AdapterVersion:string)；MappingDirection=CameraPixelToCorrectedPixel |
| RectifiedPayload | 抽象IAsyncDisposable，ImagePayload(Planes:IReadOnlyList<ReadOnlyMemory<byte>>,Layouts:IReadOnlyList<PlaneLayout>)、PointsPayload(Points:IReadOnlyList<PixelPoint>)、ContourPayload(Vertices:IReadOnlyList<PixelPoint>,SegmentStarts:IReadOnlyList<int>,Closed:IReadOnlyList<bool>)三变体；数据均由结果Owner独立持有，Dispose后访问抛ObjectDisposedException |

InputFrameDescriptor的FrameHash是源快照内容身份，CaptureScopeHash是宿主实际相机/镜头/读出ROI/binning/环境配置的canonical身份，LayoutHash包含尺寸/plane布局/ROI/binning；三者不相互替代。Contour.Closed长度等于SegmentStarts.Count；首段start=0，后续严格递增且在Vertices内，每段至少2点，Closed段至少3点。不通过重复首末点猜闭合。Target.PrincipalPoint必须与资产CamParamOut匹配，SameSizeCenterPixels只在资产也定义相同完整目标时可用，不据此重新选择物理尺度。Budget.MaxDomainSegments:int（正），与EngineOptions取小者；计原域、交集域及工作域全部段数后预占，不用交集缩小绕过输入元数据额度。

域规范复用image-frame半开行段语义：[image-frame §4.4](../image-frame/DEVELOPMENT-GUIDE.md)。本模块只定义无像素所有权的值投影，适配器将外部DomainDescriptor转换，不修改来源。Full/Empty/Unknown的Rows为空；RowSegments非空，按Row再ColumnStart排序，同一行段不得重叠或相邻，邻段合并；0<=row<H、0<=start<end<=W。明确覆盖全部画布时规范化为Full，零段为Empty；Unknown不能转Full，所有生产计算路径R0009。Missing ReasonKey的Empty/有洞域拒绝，元数据、hash不一致R0001。裁窗先与窗口相交，再减Row/Column；源/资产/plane域取交集，不取并集、不填洞。结果域在OutputWindow局部坐标，Mapping保留父原点。图像有效性检查仍按§5.3四邻点支撑；点整数中心检查该样本，非整数点检查包围四中心和资产支持域。轮廓逐顶点并按每条源线段四支撑邻点的最小包围矩形做保守域包含检查：逐行要求该矩形的完整半开列段由规范InputDomain和资产域共同覆盖，有洞即R0009；Closed还检查末顶点到首顶点的段，不在线剔除/重新采样。此规则可保守拒绝矩形内不在线段上的域洞，不能扩大来源有效性；输出仅HALCON采样顶点定义的分段曲线，不承诺未采样连续曲线的物理精度。

UI FrozenDraftHash编码全部来源/载荷/Target/Options/Budget/Timeout和契约版本，仅排除RequestId/token；因此预算或窗口改参也使旧候选不可应用。模块InputHash/CalculationIdentity编码输入及几何/运行版本，map key仅编码A.5声明的字段，不把源像素hash混入可跨帧复用的map。

canonical编码采用下方A.4.2的rectification-canonical/2。本模块0.2.0仍未发布；本次替换有歧义的/1草案，不宣称旧持久化内容兼容。禁止隐式NFC转换身份；所有标识/引用使用Ordinal比较与原始严格UTF-8编码，规范等价但原始标量不同的字符串是不同身份。

Core C1静态入口位于public static class RectificationCore，公开签名统一为下方A.4.1；C2 RecommendExecution直接调用其EvaluateBudget并传EngineOptions.Limits。中心row/column是canonical，CornerRowColumn→中心每轴减0.5，反向加0.5，CenterColumnRow只交换两个分量；换基不是畸变算子。C1仅执行§5中的纯值检查，不读资产/资格端口、不取像素或维护RequestId注册表；重复ID/资格屏障由C2执行。首错先做无大分配的容量/文本预检，再按ID/枚举/期限/必填→载荷/来源匹配→尺寸/plane→domain→target/坐标声明→预算/版本语义验证，§5的IO步骤不在C1伪造成功。checked计算最终访问字节：stride>=0末行offset+(H-1)stride，stride<0最小offset+(H-1)stride；两端加rowBytes后均在accessible内。Plane.RowBytes=Width×Channels×格式字节且不含padding。

### A.4.1 同步Core限额与文本边界

```csharp
public sealed record CoreLimits(
    int MaxDimension, int MaxPoints, int MaxContours, int MaxPlanes,
    int MaxDomainSegments, int MaxTextChars, int MaxTextUtf8Bytes,
    long MaxTotalTextUtf8Bytes, long MaxCanonicalBytes,
    long MaxManagedBytes, int MaxTraceEvents, int MaxParameterValues);
public static class RectificationCore
{
    public static ValidationResult ValidateRequest(RectificationRequest request, CoreLimits limits);
    public static FrozenRectificationInput FreezeInput(RectificationRequest request,
        string backendVersion, string algorithmVersion, CoreLimits limits);
    public static CoordinateNormalizationResult NormalizeCoordinates(
        IReadOnlyList<PixelPoint> points, PixelCoordinateConvention source,
        PixelCoordinateConvention target, CoreLimits limits);
    public static ExecutionRecommendation EvaluateBudget(RectificationRequest request,
        BackendCapabilities capabilities, CoreLimits limits);
}
```

EngineOptions追加Limits:CoreLimits（非空）；RectificationBinding借用Engine已冻结限额，控件不另建宽松限额。所有限额显式正数，无无限默认或隐式放宽；MaxCanonicalBytes/MaxManagedBytes为工程容量，单一托管数组还须满足Array.MaxLength与元素字节乘积的实际可分配范围。MaxDimension可为100000或其它正Int32，不能拿它或像素面积限制无图像点路径。Normalize要求非空输入，按MaxPoints和MaxManagedBytes校验，不依赖不存在的request；返回失败时Points为空，Error为R0001（非法限额/枚举/文本）或R0011（数量/容量/checked溢出），不部分换基。Freeze非法输入抛ArgumentException并携同一错误Code；不得先ToArray/Normalize/hash再校验。EvaluateBudget限额失败同样返回无成功建议及稳定错误，不调用native。

预检顺序固定：先检查null/限额标量和集合Count（输入仅支持精确runtime类型T[]/List<T>（不接受子类）或本Core创建、内部持有数组的FrozenList<T>，不接受可包裹任意IList的外部ReadOnlyCollection，拒绝任意自定义IReadOnlyList、延迟枚举器R0001）；逐集合检查MaxPoints/MaxContours/MaxPlanes和全部域段累计上限、checked逻辑容量，再扫描至多MaxTextChars字符/有限个字段做严格UTF-16合法性和UTF-8字节计数。禁止不受控属性getter/枚举器参与同步入口，调用期间调用方不得并发修改集合；冻结后只读副本。Normalize至少预占两份16n逻辑坐标（输入防御副本+输出），每个实际数组容量、对齐和头开销再计入MaxManagedBytes；同一方向也不返回可变原集合。Freeze/Validate先算A.4.2精确wire总长，再比较MaxCanonicalBytes，增量hash用固定4096 byte scratch（分配前也占MaxManagedBytes），不创建整份canonical byte[]；对象/数组/字符串实际容量由Core实现的有界allocation预约器在分配前计入MaxManagedBytes，逻辑字节不能冒充实际容量。平台执行路径还须按A.2预约W/O/N，不能拿CoreLimits替代运行预算。Validate不复制集合、不生成hash；扫描时间受数量/字符/段数界限约束。Trace以MaxTraceEvents为硬容量，进度可合并；不可丢的最终状态槽在接纳前预约，不能靠无限事件列表逃过限额。

所有ID/Revision/BindingId/PublishId/AuthorityId/Epoch/版本/资源键/ReasonKey采用严格Unicode标量：拒绝未配对surrogate、U+0000、Unicode类别Cc/Cf（含换行、BOM、方向控制）以及首尾Unicode空白；必填不空、不Trim、不大小写折叠、不NFC/NFD转换。先按UTF-16长度MaxTextChars拒绝，再用严格UTF8Encoding(false,true).GetByteCount计每字段与累计字节，超限R0011、非法文本R0001；拒绝文本不写原文日志。ContentHash.Algorithm唯一小写字面量sha256，Hex恰64个[0-9a-f] ASCII，不接受大写、前缀、空格或替代Unicode；hash对象作为引用时必须验证两字段。可空文本null和空字符串不同，空字符串只在明确允许的诊断内容中合法（仍受容量约束），身份/版本/键不允许空。资产CamParamIn/Out各Count<=MaxParameterValues、诊断集合Count<=MaxTraceEvents，外部端口回执也按同一Limits逐项预检；未知相机模型在模型能力门拒绝，不为其分配无界参数数组。

### A.4.2 逐类型规范编码及固定Golden

所有规范hash均SHA-256；字节流前缀为长度前置字符串rectification-canonical/2，再写长度前置domain标签。I32/I64均有符号little-endian；TimeSpan为I64 ticks；Double为有限IEEE754 little-endian，-0写+0；Bool为单byte 00/01。String为I32严格UTF-8字节长+原始字节（无BOM/无规范化）；Enum写其本指导稳定ASCII名称的String，不能写底层数字。Nullable任意类型先单byte 00（后无数据）或01（后为值）；List先I64数量再按既有次序写元素，禁止排序点/轮廓/plane。域Rows须先通过规范顺序校验，不能以排序悄悄修复非法输入；IReadOnlySet能力声明若需诊断编码按稳定枚举名Ordinal排序，但不进入几何身份。ContentHash嵌入编码为String(Algorithm)+String(Hex)，不是裸32 byte。Guid仅PlaneLayout.AllocationId的诊断序列化用RFC4122网络字节序16 byte；它和AllocationBytes/AccessibleBytes等分配事实不进入可跨帧的几何map key。DateTimeOffset诊断编码为UTC ticks I64，水位/时间不是几何参数。

| 类型/identity domain | 写入字段顺序（嵌套类型递归使用本表） | 自hash与排除 |
|---|---|---|
| PixelSize / PixelPoint / PixelRect | Width,Height / Row,Column / Row,Column,Height,Width | 无；前两尺寸I32、点Double、矩形I32 |
| RevisionId / FrameSnapshotId / CalibrationAssetRef | Value / Value / Id,Revision,Hash | 不排除被引用Hash |
| ValidityDomain（domain=validity-domain） | Size,Kind,Rows(Row,ColumnStart,ColumnEndExclusive),Nullable(ReasonKey) | 仅排除本对象Hash；嵌入其它对象也写这些字段 |
| PlaneLayout | Format,Channels,OffsetBytes,StrideBytes,RowBytes,AccessibleBytes,AllocationId,AllocationBytes,Domain | 仅Input/UI投影使用；字段类型按A.4；不把allocation用于map |
| InputFrameDescriptor | Frame,Revision,Size,Convention,LayoutHash,FrameHash,CaptureScopeHash,Domain,Planes | 引用hash保留；仅输入闭包，无像素buffer |
| TargetGeometry（domain=target） | FullSize,PrincipalPoint,Convention,OutputWindow | 无 |
| 局部相机参数（domain=camera-parameters） | String(CameraModel),List<double>(按该模型公开参数序的局部CamParam) | 无自hash；LocalInputParametersHash/LocalOutputParametersHash分别取已按§5.4偏移的输入/输出参数，不能hash原参数冒充局部参数 |
| RectificationOptions（domain=options） | Interpolation,Boundary,OutputDomain,Cache | Cache参与计算/UI；map只取其三项几何Options |
| RectificationInput（domain=input） | String(变体名Image/Point/Points/Contour),Frame；其后Image无字段，Point:Value，Points:Values,Policy，Contour:Vertices,SegmentStarts,Closed | 不含RequestId/Timeout/token/Budget；帧与载荷次序不改 |
| CalculationIdentity（domain=calculation） | ContractVersion,InputHash,Asset,TargetHash,OptionsHash,BackendVersion,AlgorithmVersion | 引用hash均写；无资格快照/时间/RequestId/预算 |
| RectificationBudget | MaxOutputBytes,MaxWorkingBytes,MaxNativeBytes,MaxCacheBytes(I64),MaxConcurrentOperations,ProbeBatchPoints,MaxDomainSegments(I32) | 仅UI身份 |
| FrozenDraftHash（domain=ui-draft） | String(0.2.0),Operation,SourceFrame,SourceFrameRevision,Calibration,Target,Options,Input,Budget,Timeout | 仅排除RequestId/CancellationToken；预算或期限变则草稿hash变 |
| RectificationCacheKey（domain=map-key） | 按A.5声明序：SchemaVersion至BackendVersion全部字段 | 不加像素hash/域/资格水位/预算/RequestId/token；不得把自生成map hash纳入key |
| MapContent（domain=map-content） | Key,IndexType,OutputSize,List<byte>(IndexPlane),List<List<byte>>(WeightPlanes) | 排除本对象ContentHash；byte列表仍I64长度，每byte原样 |

只有表中标domain的对象作为独立hash根时加一次前缀/domain；嵌套对象仅写字段，不再加前缀。FrozenRectificationInput.Identity.InputHash=hash(domain=input,Request.Input)，TargetHash/OptionsHash分别取对应domain；冻结时间不hash。其它结果/事件/Trace/资格DTO不是几何hash根，不隐式创造identity codec；诊断导出按A.4字段顺序与上述基础编码并标独立diagnostic版本。LayoutHash/FrameHash/CaptureScopeHash/资产内容Hash为来源Owner给出的引用，模块不替Owner重新定义其内容域。输入哈希用于Calculation，不等于请求、UI或map身份。RequestId变不会改变上述hash（也不会改变FrozenDraftHash）；先前IR-C1-05中将RequestId算入UI的歧义按此修正。算法/后端版本只进入Calculation或map键，不从进程当前版本隐式取值。

Golden固定为最小合法ValidityDomain：Size=(Width=2,Height=3)，Kind=Full，Rows=[]，ReasonKey=null。使用domain=validity-domain；Hash字段任意合法引用均不参与自身digest。完整规范字段与字节见下方固定值；Expected必须来自此字面量，不能调用被测codec生成。另验00与01、ReasonKey=null与非空、é(U+00E9)与e+U+0301的Ordinal身份不同，后两严格UTF-8分别c3a9与65cc81且不得合并；含孤立surrogate拒绝，不产生hash。

固定字段独立拼接（依次为prefix、domain、Size、Kind、Rows.Count、ReasonKey存在byte）：
```text
1900000072656374696669636174696f6e2d63616e6f6e6963616c2f32
0f00000076616c69646974792d646f6d61696e
0200000003000000
0400000046756c6c
0000000000000000
00
完整hex（73 bytes）：
1900000072656374696669636174696f6e2d63616e6f6e6963616c2f320f00000076616c69646974792d646f6d61696e02000000030000000400000046756c6c000000000000000000
SHA-256：4bc8b7692cf990b4dc58c597d5b62bf8773f78af2e394bb3340b63ea88e8165c
```

第二个完整输入Golden为§11.1 Host A的RectificationInput.Points（仅Input根，无RequestId/Budget/Timeout）；402 bytes，InputHash为9a7688236035f3279e1882417d8d95ff18ca37df861073014ae3fb3fef16bd5b。以下逐行分别是prefix、domain、变体、Frame ID、revision、Size、Convention、三个引用hash、Domain、Planes.Count、Values.Count与点值、Policy；连接所有行即完整规范字节，不省略或重新调用codec生成Expected。零hash为合成引用，域自Hash字段不写入。
```text
1900000072656374696669636174696f6e2d63616e6f6e6963616c2f32
05000000696e707574
06000000506f696e7473
0b00000073796e7468657469632d41
0100000031
0200000003000000
0f00000043656e746572526f77436f6c756d6e
060000007368613235364000000030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030
060000007368613235364000000030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030
060000007368613235364000000030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030
02000000030000000400000046756c6c000000000000000000
0000000000000000
0100000000000000000000000000f03f000000000000e03f
0c000000416c6c4f724e6f7468696e67
```

C2唯一实例入口：
```csharp
public interface IRectificationEngine : IAsyncDisposable
{
    CoreLimits Limits { get; }
    ValueTask<RectificationResult> ExecuteAsync(
        RectificationRequest request, IProgress<RectificationProgress>? progress = null);
    RectificationResult Execute(RectificationRequest request);
    ExecutionRecommendation RecommendExecution(RectificationRequest request, BackendCapabilities capabilities);
    ValueTask<StatusQueryResult> GetStatusAsync(StatusQuery query, CancellationToken token);
    ValueTask<DrainResult> DrainAsync(TimeSpan timeout, CancellationToken token);
    event EventHandler<RectificationEvent> StateChanged;
}
```
Limits返回EngineOptions中防御冻结的不可变CoreLimits，不允许调用方动态放宽。Execute是后台线程专用的同一ExecuteAsync语义；DisposeAsync等待本实例安全Closed，重复幂等，不受UI退订影响。DrainAsync只停止接收并观察，token取消只取消等待，返回Cancelled+在途身份；不取消排空证据，不冒充Closed。Engine创建唯一签名为 `IRectificationEngine RectificationEngineFactory.Create(EngineOptions options, IFrameSource frames, ICalibrationSnapshotPort assets, IQualificationBarrierPort qualification, IRectificationBackend backend, IMapStore? mapStore)`；Factory按§11.2纯有界构造且失败同步清局部资源，借用端口不被Factory释放。Core/模拟后端不引用WPF或native程序集。

### A.5 map归属、持久化与窗口端口

map属于本模块的派生计算内容，CalibrationAssetSnapshot不内嵌可变map、不拥有缓存；资产只提供不可变相机参数和支持域。asset既有map引用只作为来源诊断，不直接绕过本模块生成/验证。Core拥有完整key、schema和验证规则；Store适配器拥有字节IO、原子提交、引用计数/保留；native cache属于后端实例，每项不可变，只允许读lease。结果、输入、缓存分别计allocation，不按消费者数重复计物理容量。

```csharp
public enum MapIndexType { Int32, Int64 }
public sealed record RectificationCacheKey(
    string SchemaVersion, CalibrationAssetRef Asset, ContentHash SourceLayoutHash,
    PixelSize ParentSourceSize, PixelRect SourceWindow, TargetGeometry Target,
    ContentHash LocalInputParametersHash, ContentHash LocalOutputParametersHash,
    Interpolation Interpolation, BoundaryPolicy Boundary,
    OutputDomainPolicy OutputDomain, string AlgorithmVersion, string BackendVersion);
public sealed record MapContent(
    RectificationCacheKey Key, MapIndexType IndexType, PixelSize OutputSize,
    ReadOnlyMemory<byte> IndexPlane, IReadOnlyList<ReadOnlyMemory<byte>> WeightPlanes,
    ContentHash ContentHash);
public enum StoreCode { Found, NotFound, Published, Invalidated, Conflict, Unknown, Failed }
public sealed record MapStoreResult(
    StoreCode Code, MapContent? Content, ContentHash? CommittedHash,
    RectificationError? Error);
public interface IMapStore
{
    ValueTask<MapStoreResult> ReadAsync(RectificationCacheKey key, TimeSpan timeout, CancellationToken token);
    ValueTask<MapStoreResult> PublishAsync(string publishId, MapContent content, TimeSpan timeout, CancellationToken token);
    ValueTask<MapStoreResult> QueryPublishAsync(string publishId, TimeSpan timeout, CancellationToken token);
    ValueTask<MapStoreResult> InvalidateAsync(RectificationCacheKey key, ContentHash expectedHash, TimeSpan timeout, CancellationToken token);
}
public sealed record WindowPlan(
    FrameSnapshotId ParentFrame, RevisionId ParentRevision, ContentHash ParentHash,
    TargetGeometry Target, PixelRect SourceWindow, ContentHash InputParametersHash,
    ContentHash OutputParametersHash, long ProbeCount, long EstimatedWorkingBytes);
public sealed record WindowPlanResult(
    WindowPlan? Plan, RectificationError? Error, DrainResult Drain);
public sealed record MapSafetySummary(
    long TotalCells, long UnsafeCells, long InvalidStructureCells,
    ContentHash MapHash, string ValidatorVersion);
public sealed record MapPreparationResult(
    MapContent? Map, MapSafetySummary? Safety,
    RectificationError? Error, DrainResult Drain);
public interface IRectificationBackend
{
    BackendCapabilities Capabilities { get; }
    ValueTask<WindowPlanResult> PlanWindowAsync(
        FrozenRectificationInput input, CalibrationAssetSnapshot asset,
        CancellationToken token);
    ValueTask<MapPreparationResult> PrepareMapAsync(
        FrozenRectificationInput input, CalibrationAssetSnapshot asset,
        WindowPlan plan, MapContent? cached, CancellationToken token);
    ValueTask<BackendOperationResult> RunAsync(
        FrozenRectificationInput input, CalibrationAssetSnapshot asset,
        WindowPlan? plan, IFrameWindowLease? frame, MapContent? map,
        CancellationToken token);
    ValueTask<DrainResult> ObserveDrainAsync(string requestId, TimeSpan timeout, CancellationToken token);
}
```

MapPreparationResult成功Map/Safety非空、Error=null、Drain.Code=Drained；Safety.TotalCells恰为目标窗口面积，InvalidStructureCells必须0，MapHash等于Map.ContentHash。UnsafeCells按§5.3计源最后行/列、负/越界索引；Reject策略非0即R0009，Conservative策略可保留原map待私有安全改写，不能直接执行。失败Map/Safety=null且Error非空；StillDraining隔离原工作，Error=R0015且不进入Run。PrepareMapAsync创建或重建经过schema/hash验证的原map，先扫描全部cell并报告结构/边界；RunAsync取得frame实际域后按§5.3派生私有SafeExecutionMap，再次全cell验证后才map_image。仅Core元数据检查不替代native索引/权重检查。cached非空仍核内容，不修改共享map。

BackendOperationResult(Payload:RectifiedPayload?,Domain:ValidityDomain?,Mapping:CoordinateMappingDescriptor?,Map:MapContent?,Error:RectificationError?,Drain:DrainResult)只给引擎内部候选，不通知消费者；成功时前三项同时非空、Error=null/Drain=Drained，点/XLD的Map=null；失败前三项和Map均null/Error非空；StillDraining无任何候选、Error=R0015。Drain=StillDraining时返回给内部Owner并隔离，ExecuteAsync继续未完成。Run/Plan的native作业须在Accepted后，未结束不会让token或异常释放对象；PlanWindowAsync是§5.4的HALCON反向探测，属于native生命周期。点/XLD路径不传frame/map，不取像素lease。模拟后端的结果标BackendVersion=simulator/1，绝不用于资格。

MapContent是引擎拥有的不可变托管内容快照，ReadAsync必须复制或移交独立内存，不能返回随IO租约失效的buffer；Store不泄漏自己的读lease。缓存淘汰只移除索引，活动引擎持有内容直到drain，托管allocation按实际容量计费。每个持久plane/output plane必须可由ReadOnlyMemory<byte>表示（Length为Int32），超上限R0010，宿主显式更小OutputWindow；超大source仍逐行读，不强制全帧托管。

生产Map schema固定halcon-bilinear/1（S1隔离的protocol schema仅见A.8）：N=H×W；索引plane精确4N或8N byte，WeightPlanes恰4项每项2N byte，little-endian逻辑逐像素布局；生成后copy_image/get_image_pointer1读取，持久化不存HObject/native地址，不接受宿主自造map。加载核key/schema/hash/类型/长度/权重与生成规范，再§5.3全cell边界检查。原map可含越界但不可执行；SafeExecutionMap在本次操作内派生，不写回Store。Int64/Int32选型及支持范围由backend能力准确声明；预算用checked Int64，native构造前再校backend上限。

持久化固定步骤：预约编码字节 → 由生成map封存MapContent与hash → PublishId绑定完整key+hash → 写不可见临时内容并flush → 验hash/长度 → 原子发布key到内容hash索引 → 读回内容和manifest一致才Published。Found的Content非空；Published的CommittedHash非空且等于请求hash；NotFound无内容且非错误；Conflict/Unknown/Failed无可用内容且Error非空。相同PublishId/相同内容返回原回执，不同内容Conflict/R0022，不能覆盖。发布响应丢失返回Unknown/R0022，只查询原PublishId；确认NotFound后才允许同ID重试，内容成功索引失败不成为缓存命中。Invalidate成功为Invalidated+CommittedHash=expectedHash+Error=null，已不存在为NotFound，期望hash冲突为Conflict/R0022；Invalidate以expectedHash CAS隔离损坏项，禁止删正在读的blob。Store保留当前索引或有读lease的内容；零引用旧内容按宿主CacheRetention(MaxBytes:long,MaxEntries:int,MaxIdle:TimeSpan)回收，仅删Store自己写的内容，不清理源/用户目录。参数均显式正值。ReadThrough的写失败记录Trace并禁用该缓存项，但只要计算和资格有效可Completed；RequireHit不创建/写map，缺项R0021。缓存持久化没有业务提交权。

窗口链复用§5.4：Accepted/预算预约 → 订阅资格水位 → PlanWindowAsync逐目标中心反查源，ProbeBatchPoints分批 → 求四邻点最小矩形 → 以真实allocation重核预约 → AcquireWindowAsync精确父帧/hash/revision → 校验回执/域 → 局部主点偏移和尺寸 → 本窗口key查缓存 → PrepareMapAsync全cell预检 → RunAsync派生/复检SafeExecutionMap → map_image → 结果拷贝 → native排空 → 发布前资格回读IO结束 → 工作资源归还 → 本地发布闩锁。source探测本身也记native峰值和取消期限，不把它称作pre-native校验。Plan/Prepare/Run共用冻结请求的单调截止，每个批次及native调用前检查剩余时间；不因进入新阶段重置Timeout。

跨tile需求通过一个AcquireWindowAsync交付精确source矩形。宿主image-frame适配器负责从同一冻结父帧revision的多个tile装配真实原像素，不重采样/融合/补洞；报各plane有效域和实际allocation容量，缺tile失败R0020，不偷偷拼最近帧。halo是反向四支撑邻点并集，不能按输出固定+1；不另外暴露跨tile native handle。WindowPlanResult成功Plan非空/Error=null/Drain.Code=Drained；失败Plan=null/Error非空；无法证明探测native结束时Drain.Code=StillDraining/Error=R0015，Engine转DrainUnknown并查询ObserveDrainAsync，不能释放该worker/probe内存。计划和租约父hash/revision/key不一致R0003；一个source窗口不足则拒绝该请求，宿主新ID显式缩小窗口。不同输出窗口使用独立map和租约，乱序/重复不证明mosaic完整；父坐标、缝隙、覆盖检查由mosaic消费者负责。

### A.6 资产快照、撤销与发布屏障

技术行为固定fail-closed，ScopeHash在QualificationSnapshot中表示本次实际CaptureScopeHash的适用性计算，资产ScopeHash是批准范围定义hash；范围可包含多个实际配置，不要求两个hash数值相等。QualificationPort以输入CaptureScopeHash绑定实际冻结观测并由原Owner验证asset范围。未知相机/ROI/binning/环境字段不能只hash Unknown而当合法配置。Watermark authority/epoch非空，Revision>=1，ObservedAtUtc<=当前UTC<ValidUntilUtc；资格端口负责确认权威时间有效性，模块仅以注入TimeProvider检查快照过期，不从本机时钟状态猜资格。不要求用户选择“继续旧资格或取消”。资格决定仍由外部Owner签发，本模块只读，不能自行撤销资产或签发资格。

```csharp
public enum QualificationState { Qualified, Suspended, Revoked, Expired, Unknown }
public sealed record AuthorityWatermark(
    string AuthorityId, string Epoch, long Revision, DateTimeOffset ObservedAtUtc, DateTimeOffset ValidUntilUtc);
public sealed record QualificationSnapshot(
    CalibrationAssetRef Asset, QualificationState State,
    AuthorityWatermark Watermark, ContentHash ScopeHash, ValidityDomain SupportedDomain);
public sealed record CalibrationAssetSnapshot(
    CalibrationAssetRef Reference, string CameraModel,
    IReadOnlyList<double> CamParamIn, IReadOnlyList<double> CamParamOut,
    ContentHash ScopeHash, ValidityDomain SupportedDomain);
public sealed record CalibrationReadResult(CalibrationAssetSnapshot? Asset, RectificationError? Error);
public interface ICalibrationSnapshotPort
{
    ValueTask<CalibrationReadResult> ReadAsync(
        CalibrationAssetRef reference, TimeSpan timeout, CancellationToken token);
}
public sealed record QualificationReadResult(QualificationSnapshot? Snapshot, RectificationError? Error);
public sealed record QualificationNotice(AuthorityWatermark Watermark, CalibrationAssetRef Asset,
    QualificationState State, bool HasGap);
public interface IQualificationBarrierPort
{
    ValueTask<QualificationReadResult> ReadAsync(
        CalibrationAssetRef asset, ContentHash scopeHash,
        AuthorityWatermark? minimum, TimeSpan timeout, CancellationToken token);
    IAsyncEnumerable<QualificationNotice> WatchAsync(
        AuthorityWatermark after, CancellationToken token);
}
```

成功资产/资格回读其快照非空、Error=null，失败快照null/Error非空。Read必须查权威，不能返回最近Qualified缓存；Unknown、过期、不可达、scope/hash失配均R0005。Watermark有效时间由外部权威提供，不造TTL。启动先读完整资产和资格q0（Read的scopeHash来自Input.Frame.CaptureScopeHash），接纳后Watch(q0)，再回读q1（>=q0），进入native前确认未过期/未断订阅；Watch断连、HasGap、epoch变化或撤销立即设置禁止发布闩锁，发安全停止请求，等待真实排空。新的asset revision不热换旧计算；旧asset仍Qualified且无撤销时旧闭包可完成。

发布固定顺序：候选封存 → 进入Draining并确认native真实完成 → 权威Read(minimum=已观察最大水位，使用本次剩余期限)并确认回读IO结束 → 停止本请求Watch并等待观察循环/枚举器/回调真实结束 → Drained → 归还全部请求工作资源并发ResourcesReleased → 在引擎同一门内复核回读水位/有效期及保留的本地撤销、取消、deadline闩锁 → ResultPublished/Completed。native完成或BackendOperationResult.Drain=Drained仅证明该后端局部作业完成，不能提前发布请求级Drained；Drained之后不能再回读、重订阅或补做任何请求IO。

每个Accepted请求拥有独立Watch枚举器、观察循环和停止token；宿主端口可复用全局连接，但模块只关闭本请求观察器。回读期间Watch继续接收通知；回读结束后在引擎门内标记ClosingWatch，再取消观察器专用token，等待在途MoveNextAsync返回、观察循环结束、DisposeAsync完成及已进入的通知回调退出。关闭由观察循环Owner串行执行，不与未结束MoveNextAsync并发DisposeAsync。主动关闭的正常取消/枚举结束不制造断连闩锁；此前撤销/gap/epoch变化和关闭期间实际收到的异常或撤销仍须记录，不因关闭清零。端口完成DisposeAsync须保证本请求不再收到回调；只解除本请求绑定，不能Dispose共享Owner订阅或影响其它请求。结束后保留不带资源句柄的最大水位、资格快照和禁止发布闩锁供本地门比较；迟到回调若仍可能执行说明观察器未排空，按DrainUnknown隔离，不能用UI退订丢弃事件代替此证明。

发布门要求回读Qualified、精确asset/hash/scope和有效期符合，authority/epoch与最终观察水位一致、回读revision>=观察结束最大revision且禁止发布闩锁未置位。回读之后出现更高通知水位即使仍Qualified，也保守Rejected/R0005，不在Drained后再次IO或循环追赶。资格Unknown/撤销/回读错误安全排空后Rejected/R0005；取消或deadline已到按其原始原因Cancelled/TimedOut。已禁止发布时不启动新的资格回读，只收尾既有IO/观察器。最终门拒绝须释放独立候选后才发Terminal；成功移交后取消不能改写Completed。

资产/资格ReadAsync的timeout/token要求端口停止并等待本次底层IO及回调真实退出后才返回错误；正常返回也是完成证据。Watch停止/Dispose同样需要真实结束证据，适配器不得用Task.WaitAsync超时、停止等待、异常包装或丢弃通知伪造完成。剩余期限不足1ms时不发新Read，置deadline闩锁并收尾；如果端口违约或有限等待结束而底层IO/观察器仍存活，引擎保持原Task/枚举器/worker和其内存预算，进入DrainUnknown，ExecuteAsync未完成且不发Drained/ResourcesReleased/Terminal。恢复Owner继续观察原任务直到真实退出，不能重试产生另一个未知作业。Read错误只有在无存活工作后才可安全Rejected；请求期限约束工作/发布，不能用它强制释放未结束资源。

此屏障证明“结果在所记录资格快照下生成”，不声称与远端撤销发生原子事务。Snapshot水位、scope、检查时间进入Trace；资格在发布后变化，模块不改历史事实，但控件禁用应用并通知宿主重新解析。宿主业务提交/量测消费必须在自己的权威事务重核资格，不能把模块Completed当永久放行。外部端口通知无法提供水位/缺口语义时不开放生产执行，模拟器可验证拒绝路径。

### A.7 C3/C4/C5与S1唯一公开装配

本节补齐已有IRectificationEngine/IRectificationBackend/IMapStore装配，不另造执行结果、状态机、map几何算法或业务协议。新增类型在未发布Module API Contract 0.2.0草案中逐片扩展；C1/C2已接收字段/方法仍原样，C6接收保持。Session表示实例资源Owner，可单独Dispose；Engine继续借用注入端口，只有工厂调用者/进程根持有Session的Dispose权。IMapStore现有调用不要求更换为Session（外部宿主仍可提供纯借用端口）。真实native与durable IO门不由工厂构造通过代替。

```csharp
// 以下接口/值对象在Core程序集、Asun.Modules.ImageRectification命名空间。
public interface IRectificationBackendSession : IRectificationBackend, IAsyncDisposable { }
public sealed record MapPublicationStatus(string PublishId, RectificationCacheKey Key,
    ContentHash ContentHash, StoreCode Code, bool HasLiveOperation);
public sealed record MapStoreRecoverySnapshot(long Revision, long RetainedBytes,
    IReadOnlyList<MapPublicationStatus> Publications);
public interface IMapStoreSession : IMapStore, IAsyncDisposable
{
    ValueTask<MapStoreRecoverySnapshot> GetRecoveryAsync(TimeSpan timeout, CancellationToken token);
}
public sealed record AsunImageBackendOptions(
    CoreLimits Limits, BackendCapabilities LimitsDeclaration,
    MapIndexType ImageMapIndexType, int MaxActiveRequests,
    int MaxRetainedMaps, long MaxRetainedMapBytes);
public sealed record MapStoreAdapterOptions(
    CoreLimits Limits, long MaxOperationBytes, int MaxConcurrentOperations,
    int MaxRetainedReceipts, long MaxReceiptBytes, TimeSpan MaximumCallTimeout);

// Asun.Modules.ImageRectification.AsunImage；C3/C4程序集。
public static class AsunImageRectificationBackendFactory
{
    public static IRectificationBackendSession Create(AsunImageBackendOptions options);
}
// Asun.Modules.ImageRectification.Adapters；C5程序集。
public static class RectificationMapStoreAdapterFactory
{
    public static IMapStoreSession Create(MapStoreAdapterOptions options, IMapStore ownerPort);
}

// 以下全部在Asun.Modules.ImageRectification.Simulator独立BCL DLL。
public sealed record SimulatorBackendOptions(
    CoreLimits Limits, int MaxImageDimension, int MaxPoints,
    long MaxWorkingBytes, int MaxActiveRequests);
public sealed record MemoryMapStoreOptions(
    CoreLimits Limits, long MaxRetainedBytes, int MaxEntries, int MaxReceipts,
    int MaxConcurrentOperations, long MaxOperationBytes, TimeSpan MaxIdle);
public sealed record RectificationSimulatorOptions(
    SimulatorBackendOptions Backend, MemoryMapStoreOptions Store,
    int MaxFrameLeases, long MaxFrameHeldBytes, int MaxOperations,
    int MaxFaultRules, TimeProvider TimeProvider);
public sealed record SimulatorFrame(InputFrameDescriptor Descriptor,
    IReadOnlyList<ReadOnlyMemory<byte>> Planes);
public sealed record SimulatorAsset(CalibrationAssetSnapshot Asset,
    QualificationSnapshot Qualification);
public interface IRectificationSimulator : IAsyncDisposable
{
    IFrameSource Frames { get; }
    ICalibrationSnapshotPort Assets { get; }
    IQualificationBarrierPort Qualification { get; }
    IRectificationBackend Backend { get; }
    IMapStore MapStore { get; }
    IRectificationSimulationControl Control { get; }
}
public static class RectificationSimulatorFactory
{
    public static IRectificationSimulator Create(RectificationSimulatorOptions options,
        IReadOnlyList<SimulatorFrame> frames, IReadOnlyList<SimulatorAsset> assets);
}
public static class RectificationMemoryMapStoreFactory
{
    public static IMapStoreSession Create(MemoryMapStoreOptions options, TimeProvider timeProvider);
}
```

| 装配 | 明确选型、参数、失败、Owner与关闭 |
|---|---|
| AsunImageRectificationBackendFactory（C3/C4） | Create只做bounded纯值验证/防御冻结、预分配有限状态/资源预约器，不调用cv2/IO、不注册本次Watch、不创建native handle，失败ArgumentException携R0001/R0010/R0011并同步清私有局部资源。LimitsDeclaration.BackendId=asunimage-halcon-26.05、Version由适配包显式版本给定，PixelFormats只能现§4 PixelFormat能力子集；C3可SupportsImage=false、C4才开放Image/SourceWindows。int4/int8由显式ImageMapIndexType决定，Int64须已确认XL处理范围，不能以名称猜支持；不具对应能力R0010，不自动换类型/算子。声明上限为宿主工程能力，tuple/XLD/native/map变量内存按A.2/C4实际allocation在分配前预约；真实包尚无有界声明不能开放该能力，不阻断S1。不存在Factory授权/许可证/安装核验 |
| C3/C4 Session运行与取消 | MaxActiveRequests、MaxRetainedMaps、MaxRetainedMapBytes正数，permit与checked预约在Engine Accepted之后、native前检查；超限R0011，无额外无界等待队列。每请求独立native Owner/epoch/request身份、一个作业原Task、多阶段共用原deadline，固定在该worker线程内持/用/释放cv2对象；线程跨用/复制规则沿§7与既有26.05证据。按照§5.2/5.3/5.4原算法调用cv2，不列新路线。Session.Dispose停止新Plan/Prepare/Run并等原作业及native实际完成，再释放私有retained map缓存；未知保持原Task/资源，不返回完成。不能Dispose输入frame或宿主ownerPort；本次frame只是借用至真实完成，由Engine结束后释放。worker故障保留资源诊断，ObserveDrainAsync只观察原Task不新造作业 |
| RectificationMapStoreAdapterFactory（C5） | ownerPort是宿主已批准IMapStore消费适配器，负责其文件对象/索引事务与耐久语义；本模块factory只冻结options/借用该端口，明确输入不是DB连接串/SQL/私有表/SDK。MaxOperationBytes/MaxReceiptBytes为正，MaxRetainedReceipts/并发正数，MaximumCallTimeout=1ms..24h；本次IO取min调用剩余/该上限。Factory前进程根先预约wrapper构造/收尾空间及强持ownerPort；同步失败只清wrapper私有资源，不调用ownerPort.Dispose |
| C5 wrapper实施顺序 | ValidateKey/schema/传入hash/text/count与精确wire长度→预约operation clone/hash scratch和receipt槽→在登记原Task后调用ownerPort同一个Read/Publish/Query/Invalidate→返回值逐字段验证→移交独立MapContent/receipt或稳定错误。实际内容hash/schema不符R0008，超容量R0011；不把响应Unknown转Published/Found、不代Owner生成耐久承诺。wrapper不改变原PublishId/key/content hash，不私下重试，不拼DB事务。Read返回MapContent独立副本/移交，不能让Owner读lease暴露Core；内存转交原返回Task时归调用方预算，不在Store缓存失效时消失 |
| Store Session关闭（C5或Memory） | MaxConcurrentOperations达到上限先R0011无副作用，不等待无限队列；有界receipt槽在mutation前预约，已用ID墓碑在实例存活期不删，MaxReceipts满拒绝新ID而非忘掉再执行。Dispose停止新Read/Publish/Invalidate（Failed/R0016），但允许原ID的QueryPublish和GetRecovery继续恢复；原Dispose任务等待全部原IO/返回回调退出、进行中的读取内存移交及Unknown回执确知，再释放私有缓存/receipt，借用外部Owner不Dispose。原Read/Publish/Query仍在途时dispose等待，不用响应timeout证明结束。Unknown已结束IO仍保留receipt恢复责任和byte额度；Host确认原ID结果后可关实例，未确认且无持续根不可停止进程 |
| RectificationSimulatorFactory（S1） | 只有公开DTO，逐个frame/asset/plane在复制前按Limits/count/byte caps核验，冻结fixture为私有副本（输入ReadOnlyMemory不可继续被Host修改影响运行）。帧/资产集合各1..MaxOperations，唯一Ordinal Id/revision/hash闭包，plane实际raw bytes SHA需等FrameHash；source固定Byte单通道正紧凑，Full域hash一致，模型唯一synthetic-protocol/1与CamParamIn=[3,3]/CamParamOut=[2,2]。Factory不启动工作/Watch或外部IO。Options.Maximum字节/数量全部正值，非法ArgumentException/R0001，超内存R0011，模型/格式不支持R0010；未定义设备/目录无入口。bundle唯一Owner持四端口及内部MemoryMapStore，端口不单独Dispose；Engine只是借用。Memory工厂独立使用时另由Host根持IMapStoreSession，不能与bundle共持Dispose权 |
| SimulatorSession关闭 | DisposeAsync单次任务幂等停止所有新frame/asset/read/watch/backend/control mutation（ReleaseGate/读取诊断及原ID QueryPublish只为原工作的恢复允许）；等待全部原operation/watch/已发frame lease及候选不再被端口使用，并确认Unknown原ID回执，才释放私有fixture/cache/receipt；关闭期间仍可查原ID，转交ACK仅改变持有Owner，不解决回执也不使原Dispose完成。Engine.Dispose必须真实先完成，结果独立消费/归还可以并行；不关闭尚在借用的frame、不能把sim Dispose触发强退当Drained。Dispose失败/未完成原Task及bundle继续由Host根隔离。多个Engine借同bundle须全部安全关闭，故Host root登记借用计数；本节两个Host各一bundle无跨进程共享 |

C5的ownerPort每个原Task返回或抛错必须证明本次借用MapContent/读取buffer的本地IO、回调与访问已退出；不能用WaitAsync超时包装伪造此证据。远端提交结果仍未知时可返回Unknown，但它只转交原PublishId的回执恢复责任，Owner仍持其远端事务与恢复资料，不再借用wrapper请求buffer；这是原Store端口的消费约束，wrapper不能从Code=Unknown自行推断底层排空。原Task未退出就保留HasLiveOperation=true/原Task/Owner及预算；C5接入须验证此约束，违约Owner按未知根隔离，不加第二份任务或耐久契约。确认的receipt只保留ID/key/hash/确定结果墓碑，完整blob引用在无索引、读者和Unknown责任后可释放，不能为了忘掉ID重用mutation。

限额不是新的物理阈值。真实C3/C4工厂的公开形状和C5的端口wrapper可按本指导确定，尚未编译的具体cv2参数/重载仅在出现实质歧义时查公共签名或消费编译，复用既有官方算子语义，不重复核验封装覆盖。S1/C5 wrapper为非视觉事务，不应交给HALCON处理Store幂等或恢复；无新算法研究需求。

### A.8 S1有界公开Simulator、协议map与Store回执

#### A.8.1 控制API与确定性假端口

```csharp
// 命名空间Asun.Modules.ImageRectification.Simulator。
public enum SimulationOperation
{
    AcquireFrame, ReadAsset, ReadQualification, WatchMoveNext, WatchDispose,
    PlanWindow, PrepareMap, Run, ObserveDrain, ReadMap, PublishMap,
    QueryPublish, InvalidateMap, FrameLeaseDispose, SimulatorDispose
}
public enum SimulationFault
{
    None, HoldUntilReleased, LoseReceiptAfterCommit, FailBeforeEffect,
    MissingFrame, ChangedRevision, InvalidMapStructure, QualificationGap
}
public sealed record SimulationFaultRule(SimulationOperation Operation,
    string CorrelationId, SimulationFault Fault, string? GateId);
public sealed record SimulationSnapshot(long Revision, int InFlightOperations,
    int ActiveFrameLeases, long WorkingBytes, long RetainedBytes,
    IReadOnlyList<MapPublicationStatus> Publications,
    IReadOnlyDictionary<SimulationOperation,long> CallCounts);
public interface IRectificationSimulationControl
{
    ValidationResult Install(SimulationFaultRule rule);
    ValidationResult ReleaseGate(string gateId);
    ValueTask<SimulationSnapshot> GetSnapshotAsync(TimeSpan timeout, CancellationToken token);
}
```

Control不进入任何计算几何身份，不具有生产设备或资格写权限。Install在门内一次消耗规则槽并冻结；CorrelationId为RequestId（Plan/Prepare/Run/ObserveDrain）、ParentFrame.Value（Acquire/leaseDispose）、CalibrationAssetRef.Id（Asset/Qualification/Watch）、PublishId（Publish/Query）、hash(domain=map-key)的Hex（Read/Invalidate）或固定instance（SimulatorDispose）；*仅表示这一Operation的下一次调用，不是无限规则。operation与fault不匹配R0001：LoseReceiptAfterCommit只PublishMap，MissingFrame/ChangedRevision只AcquireFrame，InvalidMapStructure只PrepareMap，QualificationGap只WatchMoveNext；FailBeforeEffect只允许AcquireFrame/ReadAsset/ReadQualification/PlanWindow/PrepareMap/Run/ReadMap/PublishMap/QueryPublish/InvalidateMap，不允许ObserveDrain、Watch及两个Dispose操作；HoldUntilReleased只带非空唯一GateId，其它fault的GateId必须null。数量超MaxFaultRules、gate槽或字节额度R0011，重复gate ID/对同一次调用冲突R0001，不动态改已开始的operation。Install必须在目标调用前；精确匹配优先，*次之，同优先重复拒绝。No fault普通执行；未使用规则仍占槽至bundle结束，不能无限循环安装。

ReleaseGate只打开原gate的TaskCompletionSource（RunContinuationsAsynchronously），不新发请求、不改变Operation/Backend身份/资格事实；同ID重复release幂等，Unknown R0019。每个operation开始先按MaxOperations和byte预算预约、登记原Task/输入/使用资源，再读控制规则。HoldUntilReleased故意模拟违约底层不响应token/期限的存活工作，有限调用方不得假定其结束；原Task被Simulator内部根和Host包强持，释放gate才检查原取消/deadline并走原终态。ObserveDrain/Control查询不是底层动作重试；调用计数按真实端口调用递增不按进度变更。WatchMoveNext的正常静默等待不消耗不断增长的通知列表，最多一条在途；WatchDispose gate须先等MoveNext退出再等待原Dispose，沿A.6串行关闭。FrameLeaseDispose gate保留像素/预算直到原Task退出。

GetSnapshotAsync使用与Engine相同有限timeout范围并原子冻结当前快照，集合数量<=MaxOperations/MaxReceipts/15种Operation，文本受CoreLimits；每次诊断读也有operation额度，必须单次AsTask保存到Host根。非法参数以ArgumentException/R0001通知，取消/期限通过OperationCanceledException/TimeoutException，不返回伪造零计数；snapshot不带payload/native/frame lease。WorkingBytes包含仍存活原Task/临时clone/lease work，RetainedBytes包含fixture/map/receipt及故障隔离根，统计allocation一次，不拿逻辑像素尺寸掩盖副本。规则/gate/operation/receipt均有count与实际byte上限，容量满不隐式淘汰未知/活跃项。Publications复用Core的MapPublicationStatus，不另造平行Store回执DTO。

FailBeforeEffect在原任务真实退出后返回各端口既有失败形状，无成功值或未提交副作用：Acquire为Lease=null/R0020，Asset为Asset=null/R0003，Qualification为Snapshot=null/R0005，Plan/Prepare/Run的成功字段全null、Error=R0014、Drain=Drained，Store为Failed/Content=null/CommittedHash=null/R0022。Query失败不更改原Publish状态；Publish失败仅记录NotCommitted。HoldUntilReleased在原gate打开后才检查原取消/期限；已到期或已取消的Read/计算返回各接口既有R0012/R0013失败形状且仅在本次工作结束后Drained，Store返回Failed/R0012或R0013且不提交。FrameLeaseDispose/WatchDispose/SimulatorDispose是必须完成的释放，无调用期限或工作取消令牌，不因请求早已取消而跳过释放；gate解除后真实释放一次才原Task成功。清理gate不被cancel打开。None不修改正常路径，MissingFrame只返回null/R0020，ChangedRevision只返回null/R0003，不发带错误身份的有效lease。

S1构造限额统一在任何clone/字典扩容前核验：Options、Limits、TimeProvider和全部fixture非空；所有count/byte上限为显式正值，MaxIdle为1ms..24h；Backend/Store的CoreLimits逐字段相同，MaxImageDimension为3..Limits.MaxDimension，MaxPoints<=Limits.MaxPoints，MaxActiveRequests/MaxFrameLeases/Store.MaxConcurrentOperations<=MaxOperations，MaxFaultRules<=Limits.MaxTraceEvents。集合只接受A.4.1规定的精确T[]、List<T>或Core FrozenList<T>；拒绝自定义集合时不调用其Count/getter/枚举器。Frame planes、资产相机参数、域段、规则文本和map集合均先核count/text/精确wire/实际分配容量，再复制、hash和冻结；托管对象、数组头/对齐、字典容量、Task/规则/gate/结果/诊断副本都计入预约，不能只数像素或plane逻辑长度。Host的8MiB根包含这些全部容量，Options中的各额度是子限额，不能逐项各花8MiB；原Task未退出或lease/receipt未确知不归还相应容量。memory不足或checked溢出R0011，非法标量/集合R0001，且无半构造bundle移交。独立Memory工厂采用同样Limits/MaxIdle/容量规则，不需要额外frame/backend参数。

S1资产与资格是Factory防御冻结的协议fixture，不能接入生产Owner。每个SimulatorAsset的Asset.Reference必须和Qualification.Asset逐字段完全相等（Id、Revision、ContentHash），Asset.CameraModel/CamParamIn/CamParamOut精确符合A.7，双方SupportedDomain为同一3×3 Full规范域；fixture ScopeHash精确一致，本fixture不模拟生产适用范围的包含运算。资格只接受Qualified、非空AuthorityId/Epoch、Revision>=1且ObservedAtUtc<=TimeProvider.GetUtcNow()<ValidUntilUtc；Factory逐字段检查，没有隐式默认TTL、自动续期或资格签发。每个AuthorityId/Epoch只能绑定一个资产，Watch仅带watermark也能唯一定位；重复绑定为R0001。

Assets.ReadAsync精确查冻结reference，不存在或hash/revision失配返回Asset=null/R0003；正常返回完整Asset/Error=null。Qualification.ReadAsync核精确asset、ScopeHash与支持域；minimum非空必须同AuthorityId/Epoch且minimum.Revision<=fixture.Revision，再核当前UTC有效期，任何未知、scope/minimum/时间失配返回Snapshot=null/R0005；正常返回原冻结Snapshot/Error=null，不能用最近Qualified缓存替代回读。WatchAsync只接受匹配fixture的after AuthorityId/Epoch和不高于fixture的revision，非法入口以R0005错误终止；正常先交付一条该Qualified/HasGap=false通知，再保持单一可由专用token正常结束的静默MoveNext等待。QualificationGap规则在其匹配的第一次MoveNext只交付一次相同水位/资产、HasGap=true的通知；随后静默至取消，不修改fixture事实或伪造更高revision。每枚举器拥有独立停止和关闭任务，遵循A.6的MoveNext退出后串行Dispose；取消、失效、hold和late回调不能被伪装为正常结束。

#### A.8.2 Image fixture与生产隔离

Backend.Capabilities固定BackendId=rectification-protocol-simulator、Version=simulator/1；PixelFormats={Byte}、MaxImageSize=(options.MaxImageDimension,options.MaxImageDimension)、MaxLinearIndex=Int32.MaxValue、MaxWorkingBytes=options.MaxWorkingBytes、MaxNativeBytes=同一值的有界合成预约、MaxMapBytes=min(Store.MaxRetainedBytes,options.MaxWorkingBytes)、FixedScratchBytes=64、MaxConcurrentOperations=MaxActiveRequests；SupportsImage/Points/Contours/SourceWindows=true；CoordinateBuffers=(coordinate-buffers/1,MaxPoints,min(MaxPoints,Limits.MaxContours),64,8,16,4,12,40,0)。S1期望NativePeakBytes=0；这是尚未运行的协议模拟断言，不代表真实HALCON资源。合成额度仅用于走预算控制流。点/轮廓沿§11.3恒等fixture规则，返回simulator/1，不追加AsunImage路线。

图像模拟只接受本节3×3 Byte源、2×2完整目标、CenterRowColumn和Full域、RejectIfUnsupported/Bilinear/既有OutputDomainPolicy，OutputWindow必须正半开且在2×2内。其它模型/格式/目标R0010，空/Unknown/有洞域R0009，来源hash/revision错配R0003；不尝试把模拟扩为任意校正算法。PlanWindow的fixture选择将输出窗(R,C,H,W)映射到SourceWindow=(R,C,H+1,W+1)，是显式协议数据选择而非光学反向求解。InputParametersHash按既有camera-parameters域写synthetic-protocol/1和List<double>[SourceWindow.Width,SourceWindow.Height,SourceWindow.Row,SourceWindow.Column]，OutputParametersHash同理写输出窗；ProbeCount=H×W，EstimatedWorkingBytes为经预算预约的fixture工作界限。WindowPlan父ID/rev/hash/Target严格回传，原Task完成才Drain=Drained。

Engine构造map key时仅当BackendId/Version=rectification-protocol-simulator/simulator/1且精确synthetic-protocol/1资产，才选择SchemaVersion=rectification-protocol-map/1、AlgorithmVersion=synthetic-protocol/1、BackendVersion=simulator/1；真实AsunImage仍唯一halcon-bilinear/1，绝不接受protocol schema。此是已有C2端口的显式模拟装配分支，不增加生产请求里的“跳过校验”开关。协议map不是halcon-bilinear/1外部自造map；schema/Backend/Algorithm身份三处隔离，不能写生产Store namespace或以相同key复用。S1 Memory/模拟backend只接受protocol schema，C5 real wrapper只接受halcon-bilinear/1；跨schema R0017/R0008，不以hash正确放宽。原§5.3/5.4算法和真实HALCON资格要求不变。

PrepareMap用fixture源窗口局部宽SW，目标cell局部(r,c)写Int32 index=r*SW+c，四个uint16权重依次[65535,0,0,0]，每plane逻辑长度与A.5格式相同但schema不同。A整窗index=[0,1,3,4]、B右窗index=[0,2]；权重/索引由Simulator自身固定生成，Host不可上传任意native map。MapContent hash沿现canonical/2 map-content域，key包含schema，不产生第二codec；Safety=(目标cell数,0,0,该MapHash,"protocol-fixture/1")仅声明fixture结构，由Engine要求ValidatorVersion与模拟身份匹配。cached仍核其key/hash/精确plane长度、固定fixture字节，损坏不Run；InvalidMapStructure fault写一错误长度并以R0008失败，不能携成功Safety。协议检查不证明HALCON结构/指针/四邻访问安全。

Run从原IFrameWindowLease.CopyRow读取固定fixture源row，每目标cell复制对应左上源Byte进独立ImagePayload，输出A=[10,20,40,50]，B=[21,51]；不作真实bilinear插值或畸变求解，不从map任意索引访存。Domain为输出窗局部Full，Mapping保留完整Source/Target、SourceWindow和protocol MapHash，算法/适配版本为synthetic-protocol/1/simulator/1，Result.Trace.Identity显式同版本。输出plane为Offset0/Stride=RowBytes=输出Width、Accessible=实际logical字节且独立AllocationId/Bytes，Full域hash用已有domain codec；所有native handle为空且NativePeakBytes=0，不虚构HALCON结果。

AcquireWindow逐行投影冻结3×3raw fixture；A源窗3×3，B源窗(0,1,3,2)。成功lease布局Size=窗口Width/Height、ParentFrame/rev/hash不变，帧layout源/目标域按既有规范值投影；CopyRow只复制窗口逻辑行字节不导出padding。若保留整个冻结9 byte parent array而没有复制，Snapshot.Planes.AllocationId必须parent Id、AllocationBytes=9（同父allocation共享只计一次），Offset0/Stride=局部rowBytes/AccessibleBytes=局部logical；不能按B的6 byte报告保留成本；元数据/lease对象实际开销也计MaxFrameHeldBytes。成功lease由Engine Owner独立Dispose，失败且任务真实已结束由端口清局部资源。lease在cancel/Run挂起期间不提前释放；模拟源不替换最近帧/不融合tile。SimulatorFrame constructor/Factory冻结copy后其parent实际容量和Guid绑定内部独立allocation，Snapshot回报真实Id而不是沿用输入可变array的虚假Id；源Descriptor身份不因此热换，layout诊断区分原metadata与held窗口allocation。

#### A.8.3 MemoryMapStore事务、Unknown与原Task根

MemoryMapStore只模拟原IMapStore的内容/key/hash回执和幂等状态，无磁盘/DB/网络、无耐久承诺；StoreOptions.MaxEntries、MaxReceipts、MaxRetainedBytes、MaxOperationBytes、MaxConcurrentOperations与MaxIdle均显式正值，创建仅空有界字典和预约器。MaxIdle以注入TimeProvider单调时间计算：新operation前惰性淘汰超过MaxIdle的零引用旧blob；当前索引/blob和未知receipt引用不可淘汰，空间仍不够R0011，不能为通过删除被读内容。图像ReadThrough cache报retained容量；读clone与engine map另计Owner额度。单次Publish/Read操作预检协议schema/完整key hash/ContentHash、wire总长、plane长度、byte实际容量；copy前checked预约，超限R0011不调用mutation。MapContent普通不可变托管值不新增Dispose接口，IO原Task退出时移交独立数组到调用方根/Engine mapOwner；调用方释放引用并归还自己的预约，不会释放Store内部副本。

| 操作 | 正常/故障原子步骤与返回 |
|---|---|
| ReadAsync | key不存在或该key仍有调用者未确认的Unknown receipt时NotFound/Content=null/Error=null（只表示不可命中，不能据此推断原Publish未提交）；内部commit不绕过隔离，必须原ID Query返回Published/exact hash后才允许命中。可命中时先为独立clone预约operation内存、复制元数据/planes并核hash，再Found(Content非空,CommittedHash=null,Error=null)。Store内部数组不作为返回memory；原Task未完成clone仍Store work根，响应到达Task后由caller根持有。超期/取消也先结束真实clone访问才失败；hold fault则不返回伪造失败 |
| PublishAsync | mutation前为原PublishId永久receipt槽、完整key/content clone、blob/索引预约；receipt内部状态固定Pending/Committed/NotCommitted：同ID同key/hash在Pending返回Unknown、不再mutation，在Committed返回其原已观察回执（未确认失回执仍Unknown）；在NotCommitted先返回原Failed，只有原Task退出且Query已确认NotFound后，Host显式同ID同key/hash允许重试一次并复用原槽。不同key或hash始终Conflict/R0022。门内先封存invisible内容再原子更新key索引和receipt Committed（纯内存不叫flush），正常Published(CommittedHash等输入hash,Content=null,Error=null)。LoseReceiptAfterCommit完成IO与commit后返回Unknown/R0022而记录内部Committed；Host仍Query同ID，不第二Publish。FailBeforeEffect在已结束work后返回Failed/R0022并记确定NotCommitted；Query该ID为NotFound允许同ID、同key/hash显式重试。HoldUntilReleased固定在任何mutation之前，仅释放原gate后才检查原deadline/取消并决定原操作，不能在hold期间新Publish同ID |
| QueryPublishAsync | 原receipt内部Committed→Published+CommittedHash，并将调用者观察Code更新为Published、解除该原ID的Unknown命中隔离；确定NotCommitted或未登记→NotFound；原底层Publish/commit仍在途且无法判定→Unknown/R0022；不存在内容输出。已确定receipt不因响应被查询就忘掉ID。返回Unknown本身不表示原Publish Task或IO结束，按根登记分别追踪；同ID下一Query只在上一Query真正结束后发起 |
| InvalidateAsync | 门内expectedHash与现索引hash相等则移除索引→Invalidated+CommittedHash，已不存在NotFound；不等Conflict/R0022。旧blob只有内部读/未知receipt引用数0且无索引才可回收，不改正在返回的独立MapContent。临时准备失败清自己的预约，不影响已验证map |

Engine调用Store mutation前先在Engine恢复根登记PublishId/Key/ContentHash/不可变MapContent、原Publish Task和预算；PublishId格式固定ir-map-{Epoch十进制}-{RequestId}（长度/UTF8先预检与receipt额度核对，超限R0011不发IO），不依赖裸时间/随机碰撞。一个Execute只有一个map publish槽，同ID重新Execute仍R0018；RequireHit不Publish。原Publish返回Unknown且底层真实IO结束时，ReadThrough仍可按现A.5发布已验证的独立候选，但缓存未知不允许当hit；Engine另外在实例私有恢复根持续持receipt/bytes，Control.Publications只提供诊断，消费者可有限Query原ID确认。unknown receipt尚未确认，不能把map/root预算降为0或丢掉StoreSession；它是独立缓存恢复责任，不谎称仍native在执行。若Publish本身仍在途（调用方只是观察超时），请求工作未排空→DrainUnknown且Execute不完成、不发ResourcesReleased；这与IO已结束丢receipt不同。

内存/IO异常时只清已证明安全的私有work；原任务存在则隔离不终态。所有Publish/Query调用单次ValueTask.AsTask，原Task和MapContent在root登记后才有限等待；未知情况下保持一个原Publish，不重复mutation或换ID。恢复观察政策为最多8次原IDQuery、每次观察<=100ms、指数调度间隔10/20/40/80/160/320/500/500ms（由host timer任务调度，不阻塞UI），上一QueryTask未结束则只重观察不新Query；达到8次仍Unknown保留root/receipt预算、返回安全Pending诊断，不能伪造NotFound/Failed或unregister。Query Published以exact hash确认才清Unknown标志；Query NotFound只在原Publish Task已退出/owner确定无提交时可对同ID同content显式重试一次，先预约原重试Task，不新Execute/不换ID。同ID不同内容永远Conflict；自动重试不是内部默认行为。外部真实Store无法证明NotFound的确定性时仍Unknown，不用Memory模拟的结果冒充耐久证据。

Engine自身Dispose可以在IO已全部退出后完成资源关闭；独立未确认receipt根须先被Host恢复根完整接收ACK，Store/MapContent/原Query Task预算仍在那里，不随Engine字段清理丢失。S1 bundle.Dispose只能在原receipt确知后完成；若Host已将bundle/receipt/原Dispose与Query Task整体ACK转交进程根，仍只有限观察未完成Dispose，继续用该原Session查原ID，不把移交当回执解决或资源释放。示例两个Host在同一root确认/解决，不要求新增公开业务协议；真实C5接入也遵守同样根Owner条件。任何Published/Completed只表示各自的协议结果，不能变为产品PASS或质量放行。

IMapStoreSession.GetRecoveryAsync是原Store Session的有限原子读取（与Control.GetSnapshot相同错误/期限/容量规则），供真实C5 Host及独立Memory Host找到原PublishId；不是重新提交/批准的命令。每记录含冻结的Key/Hash和调用者最后观察Code、HasLiveOperation；内部commit但LoseReceipt的Code仍Unknown直到Query得到Published，不能靠诊断内部状态把未知变成功。Code/HasLiveOperation分别更新，Unknown+true保持任务资源、Unknown+false保持已结束IO的独立receipt责任；publications按PublishId.Ordinal排序，最大MaxRetainedReceipts/MaxReceipts，文本/快照实际字节<=MaxReceiptBytes或Memory保留限额，超额拒绝新的mutation，不丢未知记录。GetRecovery/Control回执是独立不可变元数据，没有liveTask/native句柄；Session本身私有根仍强持原Task、待确认MapContent、借用Owner及预算，Host最初Factory前根已经接收该Session。确认移交ACK核的是完整Session对象及这组既有原Task字段/额度，并不要求从诊断快照取得Task或随Engine字段销毁。Engine→Store调用时Session先登记原mutation/clone责任才发IO；因此Engine.Dispose在IO确已退出后完成不会丢Store内部原receipt。直到原ID确定或Host进程服务继续持该Session，才能处理Store关闭，不得关Session再指望snapshot恢复副作用。
