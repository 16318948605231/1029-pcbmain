# 条码与二维码识别独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`Core, Simulator`

- 模块键：`barcode`；模块编号：`IM-027`；来源：`PKG-023`
- 版本：`0.2.5-prep`；状态：逐切片（2026-10-11 主控接收基线保持；2026-10-12 原会话补闭 Model Profile/复合证据及 Viewport producer/选择/Clear 消费规格，并完成限定自审。Core/Simulator 为 `ModuleCoreImplementationReady`；新增扩展、HALCON decoder、Training/Worker、WPF 保持 `PreparationIncomplete / NotReady`，会话 `needs-revision` 不在本页擅改；四项软件设计欠账关闭结果见 §16.1，未声明实现、编译或运行/生产资格通过）
- 目标运行基线：C# / .NET 10；视觉适配器使用 `ImageLibDotNet` 公共接口；目标 HALCON 26.05
- 规划消费者：本平台、标签检测、物流和其他视觉项目。首个真实视觉消费者接入前必须完成本页契约采纳、受影响 C# 绑定确认和代表性 Golden 验证。
- 唯一职责 Owner：条码观察与解码能力模块；身份、工艺、质量放行和设备动作不在本模块写入。
- 模块级设计评审态：`DesignReview`（方案可评审）。§16.1「全部批准范围的本轮自审与剩余资格」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

## Core implementation binding

首个纯 Core 切片绑定仓库相对路径 `src/Modules/barcode/Asun.Modules.Barcode.Core/Asun.Modules.Barcode.Core.csproj`、测试工程 `tests/Modules/barcode/Asun.Modules.Barcode.Core.Tests/Asun.Modules.Barcode.Core.Tests.csproj`，根命名空间固定为 `Asun.Modules.Barcode`。本页尚未创建这些工程；后续代码任务仅允许对应工程及测试目录写入，本轮仅修订本指导并做定向文档自审，不创建工程。主控于2026-10-11回读 §9.1–9.3 两个自足BCL Host/Simulator构造、Factory前有界槽、原Task/lease闭包、三轴cleanup/错误保留、同ID查询及同根确认移交，并按附录B.2接收 Core/Simulator 六项文档规格为 `ModuleCoreImplementationReady`；这只是该切片实现准备，不是已经授权本轮写代码或运行验证通过。HALCON/AsunImage适配器、训练worker、WPF控件和宿主集成保留各自门；不得修改其它模块、产品项目、AsunImage内部或只读参考快照。

## 1. 目的和边界

本模块将一幅已取得的图像或 ROI 转换为**可追溯的条码观察**：码制、候选位置、原始字节（后端可提供时）、引擎原始字符串、编码/ECI 标记、解码状态、有限尝试记录和适用的印制质量原始量。1D 与 2D 是同一模块内的两个解码适配能力。独立 Training Adapter 是本模块必须覆盖的另一条能力路线，具有独立 operation、模型 epoch 和训练回执，不混入 Core decode 请求或结果。

模块不拥有以下事实或决策：

- 不生成或修改板、标签、物流包裹、工单、批次、面别、目标或 `BoardRun` 身份；`PKG-037`/应用负责解析观察并提交身份。
- 不把期待字符串、GS1 料号/批次、客户协议、重复码政策或页面选择传入算法以“选出最像”的结果。
- 不做产品/制程缺陷判定、质量放行、复判结论、报告提交、数据库写入、MES 事务、相机曝光、灯光或运动控制。
- 不把解码成功、CRC/校验通过、纠错等级或单项质量数值当作 `PASS`；质量标准适用性和放行策略由调用应用持有。
- 不在公共核心保留 HALCON `HObject`、`HHandle`、`HTuple` 或其他 native 句柄；句柄只能存在于适配器租约内。
- 不自动拼接 Structured Append，不按文本或 IoU 猜测物理码去重，不因结果数量达到期待值而证明搜索穷尽。

调用方负责目标全集、调用顺序、重采策略、身份关联、GS1/客户语义解释、质量政策、人工复判、事实提交及任何设备副作用。模块可返回“未知、候选、未完成、质量不可计算”等状态，调用方不得将其压成空字符串、零分或成功。

### 1.1 Owner 与 Authority

| 事实/动作 | 唯一 Owner | 本模块权限 |
|---|---|---|
| 图像帧、ROI、坐标/标定 | 采集/图像/几何模块或宿主 | 只读借用，保存引用，不改帧 |
| 模型、参数、适配器租约 | barcode 模块 | 创建、配置、复制结果、排空和释放；不把句柄交给宿主 |
| 解码观察、候选、raw/质量原值 | barcode 模块 | 本模块唯一生成；结果不可变，失败也留状态 |
| 板/标签/包裹身份与 GS1 业务字段 | 身份模块/调用应用 | 解析、冲突处置和提交；barcode 不写入 |
| 制程判定、质量放行、人工意见 | 对应工艺/质量 Owner | 只消费观察与质量资格；barcode 无判定权 |
| 相机、灯光、运动、MES、报告和数据库 | 设备/集成/应用 Owner | barcode 不调用、不持有、不重试副作用 |

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Barcode.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有可选 WPF 控件切片可引用，Core 不得反向引用。

**Blazor/Web**：解码结果通过 gRPC/REST 查询；证据图像通过 HTTP Range 分片加载；浏览器不重新解码。

**AI Tiling**：条码解码与 AI 缺陷检测是并行路线；本模块不持有推理 tile 租约。三态仲裁的 `NeedsSampling` 采样帧可包含解码失败帧，由 `ai-dataset-governance` 处理。

**HALCON 双跑**：`find_bar_code`/`find_data_code` 与 ZXing.Net（Apache-2.0）作为独立对照路线双跑；两路识别率/拒识率逐码制比对，边界/噪声样本的差异标为仅诊断。

## 2. 架构和可替换端口

```text
视觉应用/工具宿主
  └─ Barcode.Core（无 UI、无产品状态）
       ├─ IBarcodeDecoderAdapter（HALCON/AsunImage 或受控离线适配器）
       ├─ IBarcodeInputProvider / IBarcodeInputLease（输入像素、ROI、坐标来源）
       └─ 不可变模型 bytes/manifest（可选，由宿主传入；不读私有路径）
```

Core 只依赖稳定的请求、结果、取消和诊断契约。HALCON/AsunImage 适配器负责模型创建、参数设置、`find_bar_code`/`find_data_code_2d`、结果查询和 native 资源释放；其他后端只能作为显式注册的对照或离线适配器，不能改变 Core 的字节层次、状态语义或错误码。

### 2.1 HALCON 优先和 API 证据

开发时先查仓库内 HALCON 26.05 手册：

- [`create_bar_code_model`](../../../halcon算子手册/operators/create_bar_code_model.html)、[`find_bar_code`](../../../halcon算子手册/operators/find_bar_code.html)、[`get_bar_code_result`](../../../halcon算子手册/operators/get_bar_code_result.html)、[`get_bar_code_object`](../../../halcon算子手册/operators/get_bar_code_object.html)、[`query_bar_code_params`](../../../halcon算子手册/operators/query_bar_code_params.html)。
- [`create_data_code_2d_model`](../../../halcon算子手册/operators/create_data_code_2d_model.html)、[`find_data_code_2d`](../../../halcon算子手册/operators/find_data_code_2d.html)、[`get_data_code_2d_results`](../../../halcon算子手册/operators/get_data_code_2d_results.html)、[`get_data_code_2d_objects`](../../../halcon算子手册/operators/get_data_code_2d_objects.html)、[`query_data_code_2d_params`](../../../halcon算子手册/operators/query_data_code_2d_params.html)。

平台通过 `using ImageLibDotNet;` 与 `cv2` 调用 HALCON 26.05 算子。用户已确认该 operator set 完整可用，不再核验“封装是否包含算子”，不另接 `HOperatorSet`/`halcondotnet.dll`，不扫描 AsunImage 内部。算子语义和参数以本地 26.05 手册为准；只有具体 C# 参数类型、重载或封送方式存在歧义时，才查公共签名或在消费项目编译确认。历史 `HBarCode`/`HDataCode2D` 形状不作为当前实施入口。

**必须区分码制内部数据与解码载荷。** HALCON 26.05 的 [`get_bar_code_result`](../../../halcon算子手册/operators/get_bar_code_result.html) 中，`decoded_data` 是字节值 tuple，与 `decoded_strings` 对应高层数据；`decoded_reference` 是码制专属 reference 数据，可能含起止/校验字符、解码表索引及 GS1 DataBar linkage flag，不是通用 payload bytes。引擎文本只作显示投影，不得回编码成身份字节。二维 [`get_data_code_2d_results`](../../../halcon算子手册/operators/get_data_code_2d_results.html) 的 `raw_coded_data` 是可能仍含错误且包含纠错字的码制数据，`corr_coded_data` 是纠错后但仍按该码制编码的数据；二者都不是应用 payload，不能写进 `RawPayload.Bytes`。二维 `decoded_data` 是解码后的数据字/字符 tuple，手册说明其解释随 Latin-1/ASCII 及 QR/Micro QR 的 JIS8/Shift JIS、QR 的 GB2312 等模式而变，Kanji 还可能拆成字节；只有当冻结 Profile 明确字符/ECI 解释，且目标适配器 Golden 证明逐字节无损时，才能形成业务 payload。否则保留具名引擎结果/文本和原 tuple 的诊断摘要，将 `RawPayload.Availability` 置为 `Unsupported` 或 `Unknown`；不得用 `raw_coded_data`、`corr_coded_data`、`DecodedDataStrings` 或猜测的 UTF-8 替代身份字节。质量/纠错结果不弥补 payload 不可用。

HALCON 码制列表、结果 tuple 长度、特殊值、`aborted` 和质量结果族均以目标版本手册及公开绑定为准。`query_*_params` 只查询参数/结果名，不等于全部码制枚举。未绑定的 raw byte、结果族或标准等级返回 `Unavailable/Unsupported`，不能以字符串回编码或固定下标补齐。

### 2.2 HALCON 26.05 码制覆盖闭包（实现必做）

“HALCON 支持的所有类型”必须按 26.05 手册页面完整登记，不能只覆盖常见 QR/Data Matrix，也不能把 GS1 数据语义误当成另一套物理码制。实现发布时在能力目录逐项标记 `Supported / UnsupportedByAdapter / Unverified`，注明 26.05 的精确 `CodeType`、创建模型的类型名、适用参数、raw/质量结果族、Golden 样本和拒绝原因；`Unverified` 不得展示成已支持。清单依据本地 26.05 页面：[`find_bar_code`](../../../halcon算子手册/operators/find_bar_code.html)、[`create_data_code_2d_model`](../../../halcon算子手册/operators/create_data_code_2d_model.html)、[`find_data_code_2d`](../../../halcon算子手册/operators/find_data_code_2d.html)。

| 能力族 | 26.05 手册明确列出的类型/变体 | 实施约束 |
|---|---|---|
| 1D 标准 | `2/5 Industrial`、`2/5 Interleaved`、`Codabar`、`Code 39`、`Code 93`、`Code 128`、`MSI`、`PharmaCode`、`EAN-8`、`EAN-8 Add-On 2/5`、`EAN-13`、`EAN-13 Add-On 2/5`、`UPC-A`、`UPC-A Add-On 2/5`、`UPC-E`、`UPC-E Add-On 2/5` | 以手册精确字符串作白名单；PharmaCode 正反向可能返回两个合法观察；校验字符配置影响可读性/结果，必须成为参数快照。 |
| 1D GS1 DataBar | `GS1-128`、`GS1 DataBar Omnidir`、`GS1 DataBar Truncated`、`GS1 DataBar Stacked`、`GS1 DataBar Stacked Omnidir`、`GS1 DataBar Limited`、`GS1 DataBar Expanded`、`GS1 DataBar Expanded Stacked` | 记录复合码组件和 GS1 解析/语法状态；不把码制识别等同业务字段校验。 |
| 2D 标准 | `Data Matrix ECC 200`、`QR Code`、`Micro QR Code`、`PDF417`、`Aztec Code`、`DotCode` | 一次一个 `symbol_type`；类型专属的尺寸、模块、对比度和参数训练能力需按手册矩阵配置，不允许共用一套泛化参数。PDF417 的 module width/aspect 和行列约束独立登记。 |
| 2D GS1 | `GS1 DataMatrix`、`GS1 QR Code`、`GS1 Aztec Code`、`GS1 DotCode` | HALCON 会执行对应 GS1 格式约束；与标准类型分别列能力。其 AI 存在性检查不等于完整客户/业务语义验证。 |

上述清单是“HALCON 26.05 手册支持范围”，不是当前 adapter 已通过所有码制的映射与 Golden 验证。每个条目必须有“模型创建、参数读取/设置、执行、解码原始结果、质量结果（若该类适用）、取消/释放”的独立核对状态。实现者需对不适用项明确写 `NotApplicable`，不可留空造成误读。新增 HALCON 版本时生成新能力快照，不能静默扩展旧模块能力。

质量评估必须与解码覆盖分开建表：码制 × HALCON 26.05 可用质量结果族/`persistence` 条件 × 对应标准版本/应用条件 × 是否有经认可的 Golden。分数原值、标签、特殊值和缺失条件保留；手册没有给某种码制/质量标准的正式等级时标 `NotApplicable/Unsupported`，不从别的码制移植评级。HALCON 内置质量数值不自动等价于 DPM/ISO/SEMI 认证或产品放行。

## 3. 无 UI 公共契约（设计候选）

本节为 Module API Contract v0.2 的内存边界，命名空间统一为 `Asun.Modules.Barcode`；产品 Schema 映射和持久化格式仍由宿主采纳。所有集合保留输入/返回顺序，接纳时深复制；返回的 `ReadOnlyMemory<byte>` 必须拥有独立 backing storage，不向调用方暴露可写数组。下列代码是待实现的契约声明，不是已编译程序。

### 3.1 输入

| 类型/字段 | 单位、范围、默认值 | 约束 |
|---|---|---|
| `BarcodeRequest.RequestId` | 非空 `Guid`；无默认 | 调用方生成并在所有事件中回传；重试不复用不同业务事实的 ID |
| `InputFrameRef.FrameId` | 非空外部帧引用；无默认 | 只读引用，不由模块创建或覆盖帧 |
| `InputFrameRef.Width/Height` | `px`，`>0`；无默认 | 与适配器图像一致；溢出或零尺寸拒绝 |
| `InputFrameRef.PixelFormat` | 明确枚举，如 `Gray8/Gray16/Rgb8`；无默认 | 不接受未知格式；转换必须记录派生来源 |
| `SearchDomain` | 图像坐标 `px`；矩形/轮廓/全域 | 不假设 ROI 含完整静区；坐标系、crop/旋转/缩放链必须带引用 |
| `SymbologyAllowList` | 1D/2D 名称集合；必须非空；由配置显式复制，禁止隐式“全部” | 生产白名单；工程宽搜需显式模式和预算 |
| `ModelParameters` | 码制专属 typed 参数；默认取已发布配置快照 | 不在运行中共享可变实例；具体 HALCON 参数须经 `query_*` 与范围校验 |
| `EncodingPolicy` | `PreserveRaw`（默认）、允许的已知编码列表 | 不因 UI 语言改变；未知编码只给派生预览，不改原字节 |
| `QualityRequest` | `Disabled` 或标准/版本/结果族/条件快照 | 无标准、像素尺度、静区或原始成像条件时返回不可计算 |
| `AttemptPlan` | 有序有限项；默认最多 1 次 | 每项定义输入、参数、用途、时限和终止条件；不按期待值追加 |
| `ResourceBudget` | `DeadlineMs` `1..600000`（默认由宿主 Profile 提供，不在 Core 写死）；候选数、raw 字节、native 内存和派生像素均为非负整数 | 总执行预算覆盖排队、模型租用、预处理和查询；清理另用 drain window；不重置截止时间 |
| `TraceContext` | 非空链路/宿主/版本信息；无业务敏感原文要求 | 诊断引用不包含未经授权的 payload |

Core v0.2 仅定义 decode-only operation；训练计划、训练样本和训练 worker 不属于 `BarcodeRequest` 或 Core 生命周期。本模块仍必须覆盖独立的 `IBarcodeTrainingAdapter` 路线：由宿主显式授权/策略触发，使用独立训练 operation、worker、模型 epoch 和回执；decoder adapter 不隐式触发训练，训练结果不自动放行、不静默改变活动参数或模型。

1D 选项应使用 `Code 128`、`GS1-128`、`EAN-13` 等手册固定字符串；`auto` 不称“全部支持”，且不能隐式包含手册明确排除的类型。2D 模型一次固定一个 symbol type；`Data Matrix ECC 200`、`QR Code`、`Micro QR Code`、`PDF417`、`Aztec Code`、`DotCode` 及 GS1 变体的可用性逐项登记。

生产解码和训练候选都必须显式绑定完整的码制专属参数快照。下列参数只列 HALCON 26.05 手册/工程候选，不能因“推荐默认”省略 Profile 字段或形成客户资格；训练 adapter 使用独立 TrainingProfile，仅实际 C# 类型/封送歧义需要绑定确认。

| 参数 | 单位/范围 | 默认 |
|---|---|---|
| 1D `element_size_min/max` | `px`，`0 < min ≤ max`；实际上下限由 26.05 查询结果决定 | `2.0/8.0 px`（候选，需 Golden 校准） |
| 1D `num_scanlines` | 条，`0`=后端自动，正整数受预算限制 | `0` |
| 1D `orientation_tol` | HALCON 单位为度，0..90；Core 用 rad 并显式转换 | 后端默认 90° 对应 π/2 rad，必须写入快照 |
| 1D `persistence` | `0/1`，按质量/中间量需要 | `0`；需要 ISO 质量时按码制启用 `1` |
| 1D `stop_after_result_num` | 条，`0`=不以数量提前停止；正整数为上限 | `0` |
| 2D `module_size_min/max` | `px/module`，`0 < min ≤ max`，上限由手册/查询决定 | `4/20 px`（候选） |
| 2D `polarity` | `dark_on_light/light_on_dark/any` | `dark_on_light` |
| 2D `mirrored` | `no/yes/any` | `no` |
| 2D `string_encoding` | 后端支持的编码名 | HALCON 值 `utf8` 仅作引擎文本投影，不覆盖 raw |
| 2D `discard_undecoded_candidates` | `yes/no` | `no`；必须保全候选时不可设 `yes` |
| 2D `persistence` | 由质量结果族决定 | 普通解码 `-1/0` 按手册；不得统一强制 |

本表仅保留候选值的来源，唯一有效域、typed key、跨字段条件和 HALCON 映射见 §3.2.1；没有请求快照时不自动采用这些候选值。纯值错误由 Validate 拒绝；仅能在 adapter 接纳后确认的能力差异按 §7.1 返回 `BARCODE.PARAM.UNSUPPORTED` 并排空，不能静默改成另一个值或伪称预检已发现。

### 3.2 结果

```csharp
public sealed record BarcodeObservation(
    string ObservationId,
    Guid RequestId,
    ObservationState State,
    SymbologyInfo Symbology,
    RawPayload Raw,
    EngineText EngineText,
    GeometryEvidence Geometry,
    CandidateEvidence Candidates,
    IReadOnlyList<QualityMetric> Quality,
    AttemptEvidence Attempt,
    AdapterEvidence Adapter,
    IReadOnlyList<BarcodeIssue> Issues);

public sealed record BarcodeResult(
    Guid RequestId,
    IReadOnlyList<BarcodeObservation> Observations,
    IReadOnlyList<BarcodeIssue> Issues,
    bool IsComplete,
    string ResultRevision, IReadOnlyList<BarcodeAdapterAttempt> Attempts,
    BarcodeRequestSnapshot RequestSnapshot);

public sealed record BarcodeRequestSnapshot(Guid RequestId, InputFrameRef Input,
    SearchDomain SearchDomain, IReadOnlyList<string> SymbologyAllowList,
    ModelParameters ModelParameters, EncodingPolicy EncodingPolicy,
    QualityRequest QualityRequest, AttemptPlan AttemptPlan,
    ResourceBudget ResourceBudget, TraceContext TraceContext);
public sealed record BarcodeRequest(
    Guid RequestId,
    InputFrameRef Input,
    IBarcodeInputProvider InputProvider,
    SearchDomain SearchDomain,
    IReadOnlyList<string> SymbologyAllowList,
    ModelParameters ModelParameters,
    EncodingPolicy EncodingPolicy,
    QualityRequest QualityRequest,
    AttemptPlan AttemptPlan,
    ResourceBudget ResourceBudget,
    TraceContext TraceContext);

public sealed record InputFrameRef(
    string FrameId, int Width, int Height, PixelFormat PixelFormat,
    string CoordinateRevision, string PixelSha256);
public enum PixelFormat { Gray8, Gray16, Rgb8 }
public enum CoordinateFrameKind { ImagePixels, RoiPixels }
public sealed record CoordinateFrame(string Id, CoordinateFrameKind Kind, string Revision);
public abstract record SearchDomainShape
{
    private SearchDomainShape() { }
    public sealed record FullFrame : SearchDomainShape;
    public sealed record AxisAlignedRectangle(PixelPoint Origin, PositivePixelSize Size) : SearchDomainShape;
    public sealed record RotatedRectangle(PixelPoint Center, PositivePixelSize Size, AngleRadians Rotation) : SearchDomainShape;
    public sealed record Polygon(IReadOnlyList<PixelPoint> Vertices) : SearchDomainShape;
}
public sealed record PixelPoint(double X, double Y);
public sealed record PositivePixelSize(double Width, double Height);
public sealed record AngleRadians(double Value);
public abstract record CoordinateTransform
{
    private CoordinateTransform() { }
    public sealed record Identity : CoordinateTransform;
    public sealed record Affine(double M11, double M12, double M21, double M22, double OffsetX, double OffsetY) : CoordinateTransform;
}
public sealed record SearchDomain(string DomainId, CoordinateFrame Frame,
    SearchDomainShape Shape, CoordinateTransform Transform);
public enum ModelParameterKey { ElementSizeMin, ElementSizeMax, ModuleSizeMin, ModuleSizeMax, ModuleWidthMin, ModuleWidthMax, ModuleAspectMin, ModuleAspectMax, NumScanlines, OrientationToleranceRadians, Persistence, StopAfterResultCount, Polarity, Mirrored, StringEncoding, PreserveUndecodedCandidates }
public abstract record ModelParameter
{
    private ModelParameter() { }
    public sealed record Integer(ModelParameterKey Key, long Value) : ModelParameter;
    public sealed record PositiveDouble(ModelParameterKey Key, double Value) : ModelParameter;
    public sealed record NonNegativeDouble(ModelParameterKey Key, double Value) : ModelParameter;
    public sealed record Boolean(ModelParameterKey Key, bool Value) : ModelParameter;
    public sealed record Polarity(ModelParameterKey Key, PolarityValue Value) : ModelParameter;
    public sealed record Mirrored(ModelParameterKey Key, MirrorMode Value) : ModelParameter;
    public sealed record Encoding(ModelParameterKey Key, BarcodeEncoding Value) : ModelParameter;
    public sealed record Persistence(ModelParameterKey Key, PersistenceMode Value) : ModelParameter;
}
public enum PersistenceMode { DecodedOnly = -1, Temporary = 0, Persistent = 1 }
public enum PolarityValue { DarkOnLight, LightOnDark, Any }
public enum MirrorMode { No, Yes, Any }
public enum BarcodeEncoding { Utf8, Latin1, ShiftJis, Eci, Unknown }
public sealed record ModelParameters(string Revision, IReadOnlyList<ModelParameter> Values,
    ModelAsset? Asset = null);
public enum EncodingPolicyKind { PreserveRawOnly, PreserveRawAndKnownText }
public sealed record EncodingPolicy(EncodingPolicyKind Kind, IReadOnlyList<BarcodeEncoding> AllowedEncodings);
public enum QualityStandard { Iso15415, Iso15416, Iso29158, SemiT10_0701, Other }
public sealed record QualityConditions(string Revision, string OriginalFrameSha256,
    double? PixelsPerMillimeter, string? CalibrationRevision,
    string? IlluminationReference, string? ApertureReference, bool QuietZoneVerified);
public sealed record QualityRequest(bool Enabled, QualityStandard? Standard,
    string? StandardRevision, IReadOnlyList<string> ResultFamilies,
    QualityConditions? Conditions);
public enum AttemptPurpose { ProductionDecode, EngineeringExploration }
public enum AttemptStopRule { AfterAttempt, AfterAnyDecodedObservation }
public enum DerivedInputKind { Original, InvertGray8, RgbToGray8, Gray16ScaleToGray8 }
public sealed record DerivedInputPlan(DerivedInputKind Kind);
public sealed record BarcodeAttempt(string AttemptId, string Symbology,
    SearchDomain Domain, ModelParameters Parameters, DerivedInputPlan InputPlan,
    AttemptPurpose Purpose, long TimeoutMs, AttemptStopRule StopRule);
public sealed record AttemptPlan(IReadOnlyList<BarcodeAttempt> Attempts, int MaxAttempts);
public sealed record ResourceBudget(long DeadlineMs, long MaxRawBytes,
    long MaxNativeBytes, int MaxCandidates, long MaxInputBytes,
    long MaxDerivedPixels, long MaxQualityBytes, long MaxResultBytes);
public sealed record TraceContext(string TraceId, string HostRevision);

public interface IBarcodeInputProvider
{
    ValueTask<IBarcodeInputLease> AcquireAsync(InputFrameRef input,
        SearchDomain domain, CancellationToken operationCancellationToken);
}
public interface IBarcodeInputLease : IAsyncDisposable
{
    InputFrameRef Frame { get; }
    BarcodePixelBuffer Pixels { get; }
    SearchDomain Domain { get; }
}
public sealed record BarcodePixelBuffer(ReadOnlyMemory<byte> Bytes, int Width, int Height, int StrideBytes, PixelFormat PixelFormat);

public interface IBarcodeDecoderAdapter
{
    ValueTask<BarcodeAdapterCapabilities> GetCapabilitiesAsync(
        CancellationToken capabilityCancellationToken);
    ValueTask<BarcodeAdapterAttempt> ExecuteAttemptAsync(
        BarcodeRequest request, BarcodeAttempt attempt, IBarcodeInputLease inputLease,
        CancellationToken operationCancellationToken);
    ValueTask<BarcodeDrainReceipt> DrainAsync(
        Guid requestId, CancellationToken drainCancellationToken);
}
public enum AdapterThreading { DedicatedSerializedWorker, IndependentWorkers }
public sealed record BarcodeAdapterCapabilities(string AdapterRevision,
    IReadOnlyList<string> SupportedSymbologies, AdapterThreading Threading,
    int MaxConcurrentCalls, int MaxQueuedCalls);
public sealed record BarcodeAdapterAttempt(IReadOnlyList<BarcodeObservation> Observations,
    CandidateEvidence Candidates, IReadOnlyList<BarcodeIssue> Issues,
    AttemptEvidence Evidence, bool NativeCallDrained, string AdapterRevision);
public sealed record BarcodeDrainReceipt(bool NativeCallDrained,
    bool AdapterResourcesReleased, string? DiagnosticId);

public interface IBarcodeTrainingAdapter
{
    ValueTask<BarcodeTrainingCapabilities> GetCapabilitiesAsync(CancellationToken token);
    BarcodeValidation ValidateTraining(BarcodeTrainingRequest request);
    ValueTask<BarcodeTrainingReceipt> TrainAsync(BarcodeTrainingRequest request,
        CancellationToken operationCancellationToken = default,
        CancellationToken waitCancellationToken = default);
    ValueTask<BarcodeTrainingLookup> QueryTrainingAsync(Guid trainingRequestId,
        CancellationToken readCancellationToken = default);
    IAsyncEnumerable<BarcodeTrainingEvent> ReadTrainingEventsAsync(Guid trainingRequestId,
        long afterSequence, CancellationToken observerCancellationToken = default);
    ValueTask<BarcodeTrainingCancelReceipt> CancelTrainingAsync(Guid trainingRequestId,
        string reasonCode, CancellationToken callCancellationToken = default);
    ValueTask<BarcodeAcknowledgeReceipt> AcknowledgeTrainingAsync(Guid trainingRequestId,
        long terminalSequence, CancellationToken callCancellationToken = default);
    ValueTask<BarcodeCloseReceipt> CloseTrainingAsync(CancellationToken waitCancellationToken = default);
}
public sealed record BarcodeTrainingCapabilities(string AdapterRevision,
    IReadOnlyList<string> SupportedSymbologies, bool SupportsIsolatedWorker,
    bool SupportsVerifiableHardStop);
public enum TrainingPurpose { OfflineCandidate, ProductionNoReadFallback }
public enum TrainingTarget { ElementSize, ModuleSize }
public sealed record ModelAsset(string Revision, string Sha256, ReadOnlyMemory<byte> Bytes);
public sealed record TrainingAuthorization(string PolicyRevision, string AuthorizedBy,
    string ReasonCode, bool AllowProductionNoReadFallback);
public sealed record TrainingProfile(string Revision, TrainingPurpose Purpose,
    TrainingTarget Target, int MaxSamples, int MaxTrainFindsPerSample,
    int MaxFreshReads, ResourceBudget Budget, long DrainWindowMs);
public sealed record TrainingGroundTruth(string Id, string Symbology,
    ReadOnlyMemory<byte> PayloadBytes, string EvidenceSha256);
public sealed record TrainingSampleRef(string SampleId, InputFrameRef Input,
    SearchDomain Domain, string ExpectedSymbology, TrainingGroundTruth? GroundTruth);
public sealed record TrainingGoldenCase(string CaseId, TrainingSampleRef Input,
    bool ExpectedDecoded, IReadOnlyList<TrainingGroundTruth> ExpectedPayloads);
public sealed record TrainingGoldenPlan(string Revision, string ManifestSha256,
    IReadOnlyList<TrainingGoldenCase> Cases);
public sealed record SourceDecodeEvidence(Guid RequestId, BarcodeTerminalState TerminalState,
    string FrameSha256, string DomainId, string Symbology, string ModelEpoch,
    string ReceiptDigest, bool ResourcesReleased, BarcodeExecutionReceipt Receipt);
public sealed record BarcodeTrainingRequest(Guid TrainingRequestId,
    Guid? SourceDecodeRequestId, string SourceModelEpoch, string Symbology,
    ModelAsset BaseModel, ModelParameters BaseParameters,
    TrainingAuthorization Authorization, TrainingProfile Profile,
    IReadOnlyList<TrainingSampleRef> Samples, TrainingSampleRef FreshReadInput,
    TrainingGoldenPlan? GoldenPlan, QualityRequest QualityRequest,
    SourceDecodeEvidence? SourceDecode, IBarcodeInputProvider InputProvider,
    TraceContext TraceContext);
public enum BarcodeTrainingOutcome
{
    CompletedWithCandidate, CompletedWithAdvice, NoSuccessfulSample,
    InvalidOutputRejected, FalseDecodeRejected, ParameterReadbackFailed,
    ModelIntegrityFailed, GoldenValidationFailed, Cancelled, BudgetExceeded,
    AdapterError, ResourceError
}
public enum BarcodeTrainingState
{
    Accepted, Preparing, Training, Validating, FreshRead, CancellationRequested, Draining,
    Drained, ResourcesReleased, Terminal, DrainUnknown
}
public enum TrainingSampleState { NotRun, Decoded, NoRead, InvalidOutput, FalseDecode, Error }
public enum VerificationState { NotEvaluated, Passed, Failed, Unsupported }
public sealed record TrainingSampleResult(string SampleId, string FrameId,
    TrainingSampleState State, string? OutputHash, string? DiagnosticId);
public sealed record TrainingModelEvidence(string Epoch, string ModelSha256,
    ModelParameters Parameters, string ParametersSha256,
    IReadOnlyList<string> TrainedGeneralNames, IReadOnlyList<string> TrainedSpecificNames);
public sealed record TrainingGoldenEvidence(string ManifestSha256,
    VerificationState State, IReadOnlyList<string> FailedCaseIds);
public sealed record BarcodeTrainingReceipt(Guid TrainingRequestId,
    BarcodeAcceptanceState Acceptance, BarcodeRequestRejection? Rejection,
    BarcodeTrainingState? State, BarcodeTrainingOutcome? Outcome,
    TrainingModelEvidence? Before, TrainingModelEvidence? After,
    IReadOnlyList<TrainingSampleResult> Samples,
    IReadOnlyList<BarcodeObservation> FreshReadObservations,
    TrainingGoldenEvidence? Golden, VerificationState QualityEligibility,
    ModelAsset? CandidateAsset, bool CandidatePersisted, bool CandidateRegisterable,
    bool ActivityModelChanged, bool ResourcesReleased, long? TerminalSequence,
    IReadOnlyList<string> DiagnosticIds);
public sealed record BarcodeTrainingSnapshot(BarcodeTrainingReceipt Receipt,
    long LastSequence, bool PayloadReleased, string? ResultDigest);
public abstract record BarcodeTrainingLookup
{
    private BarcodeTrainingLookup() { }
    public sealed record Found(BarcodeTrainingSnapshot Snapshot) : BarcodeTrainingLookup;
    public sealed record Unknown(Guid TrainingRequestId, string DiagnosticId) : BarcodeTrainingLookup;
}
public sealed record BarcodeTrainingEvent(Guid TrainingRequestId, long Sequence,
    BarcodeTrainingState State, string? SampleId, string? ModelEpoch,
    BarcodeTrainingSnapshot Snapshot, DateTimeOffset TimestampUtc,
    BarcodeEventHistoryGap? HistoryGap);
public sealed record BarcodeTrainingCancelReceipt(Guid TrainingRequestId,
    BarcodeCancelState State, BarcodeTrainingState? StateAfterRequest,
    string? DiagnosticId);
```

本节 DTO 的数值和所有权闭包如下。`Validate` 拒绝 NaN/Infinity、负零、非正尺寸、polygon 少于三点、自交 polygon、奇异仿射变换及参数类型不符；不得将形状、参数或状态改为无约束 dictionary。

```csharp
public enum ObservationState { Decoded, Undecoded, Incomplete, Error }
public sealed record SymbologyInfo(string RequestedType, string? DetectedType,
    string? AimIdentifier, bool IsGs1);
public enum BackendEvidence { Native, Replay, Simulator }
public sealed record AdapterEvidence(string AdapterRevision, string BackendVersion,
    string AsunImageVersion, BackendEvidence Evidence);
public enum AttemptEnd { Completed, StoppedByPlan, Budget, Cancelled, Error }
public sealed record AttemptEvidence(string AttemptId, int AttemptIndex,
    string? ModelEpoch, string InputSha256, string DomainId, string ParameterRevision,
    AttemptPurpose Purpose, AttemptEnd End, double ElapsedMs,
    long PeakNativeBytes, long DerivedPixels);
public enum IssueSeverity { Information, Warning, Error }
public sealed record BarcodeIssue(string Code, IssueSeverity Severity,
    string? AttemptId, string? ObservationId, string? ModelEpoch,
    string Stage, string DiagnosticId, bool MayRetryWithNewInput);
public enum RawAvailability { Available, Unavailable, Unsupported, Unknown }
public enum PayloadSource { BackendBytes, BackendTextOnly, Replay, Unknown }
public enum PayloadUnit { Bytes }
public sealed record EciAssignment(int? Value, bool IsPresent);
public sealed record Gs1Fnc1Marker(bool IsPresent, bool IsValidated);
public sealed record RawPayload(RawAvailability Availability, ReadOnlyMemory<byte>? Bytes,
    int ByteLength, PayloadUnit Unit, BarcodeEncoding Encoding, EciAssignment Eci,
    Gs1Fnc1Marker Gs1Fnc1, PayloadSource Source);
public sealed record EngineText(string? Value, bool IsDerived, PayloadSource Source);
public enum GeometryKind { Symbol, Candidate, SearchDomain, Unknown }
public enum GeometrySource { BackendRegion, BackendContour, ConfiguredDomain, DerivedProjection }
public sealed record GeometryEvidence(GeometryKind Kind, CoordinateFrame Frame,
    CoordinateFrame TargetFrame, CoordinateTransform Transform,
    SearchDomainShape Shape, GeometrySource Source);
public enum CandidateDecodeState { Decoded, Undecoded, BackendVisible }
public enum CandidateCompleteness { Complete, Incomplete, Unknown }
public enum CandidateStopReason { Exhausted, Budget, Cancelled, BackendLimit, Unknown }
public sealed record BarcodeCandidate(string CandidateId, CandidateDecodeState State,
    GeometryEvidence? Geometry, string? ObservationId, string BackendStatus);
public sealed record CandidateEvidence(CandidateCompleteness Completeness,
    CandidateStopReason StopReason, IReadOnlyList<BarcodeCandidate> Candidates);
public enum QualityState { NotRequested, Measured, NotApplicable, MissingCondition, Unsupported, FormatError, Incomplete, Error }
public enum MetricValueKind { Integer, Real, Missing }
public enum QualityMissingReason { None, NotRequested, StandardNotApplicable,
    ConditionMissing, BackendUnsupported, BackendNA, PartialResult, InvalidLayout, BackendError }
public enum QualityMetricKey { OverallGrade, Decode, Contrast, Modulation, Defects, Decodability, AxialNonuniformity, GridNonuniformity, UnusedErrorCorrection, PrintGrowth, SymbolContrast, Unknown }
public sealed record QualityMetric(QualityState State, QualityStandard? Standard,
    string? StandardRevision, QualityMetricKey MetricKey, MetricValueKind ValueKind,
    long? IntegerValue, double? RealValue, string ResultFamily, string RawLabel,
    int TupleIndex, string? RawSpecialValue, QualityMissingReason MissingReason,
    string InputSha256, string? ConditionsRevision);
```

- 像素内存为逐行自顶向下；`StrideBytes > 0` 且不小于 `Width × bytesPerPixel`；checked 运算验证 `Bytes.Length ≥ (Height-1)×StrideBytes+rowBytes`，额外尾部不参与图像。Gray16 为无符号 little-endian，RGB 为交织 R/G/B。`PixelSha256` 为无 padding 的有效像素按行拼接后 SHA-256；provider 返回的尺寸/格式/hash/坐标 revision 必须精确匹配引用，租约结束前冻结内存。实际不符为接纳后 `BARCODE.INPUT.FORMAT`，保留空结果并排空，不伪造预检拒绝。
- 坐标 `X=column`、`Y=row`，左上像素中心为 `(0,0)`，单位 px。矩形大小为边长，旋转为图像坐标中顺时针弧度；polygon 顺序保留，逻辑闭合但不重复首点。仿射约定 `x'=M11*x+M12*y+OffsetX`、`y'=M21*x+M22*y+OffsetY`；SearchDomain.Transform 从 Domain.Frame 映射到请求原始 ImagePixels，Geometry.Transform 从 Frame 到 TargetFrame。变换后域必须在原始图像有效边界内；不静默裁切或放宽域。
- `Raw.Available` 时 bytes 非 null、长度精确且单位 Bytes；其它 availability 时 bytes 为 null、ByteLength=0。payload 可以包含 NUL，空字符串与无 payload 分别表达。二维 decoded_data 的代码单位未获逐字节解释证明时仍为 Unsupported/Unknown，不能截断到 byte。ECI 缺失与未知值分开；只保留后端明确给出的 FNC1/GS1 证据。
- 每个候选独立保存 decoded/undecoded 状态；一个成功观察不得代表所有候选成功。Result 增加下述 `Attempts` 汇总，确保“有候选但零观察”也保留分母证据。`Complete` 仅表示批准搜索域与计划内后端证据复制完整；不证明真实目标全集或整帧搜索穷尽，目标数量由宿主另记。
- 质量保留结果族、原 label、tuple index、输入和条件 revision；未知 label 映射 Unknown 但仍保留原 label/原值。Integer/Real/Missing 恰有对应值；`N/A` 保留 RawSpecialValue 与 BackendNA，不改成零；手册允许的负值（如 print growth）原样保留。`-1` 若该结果族定义为无法计算则 State=Incomplete、MissingReason=PartialResult 并保留原数值/RawSpecialValue=-1；不能把另一族合法负值按该规则处理。未知 tuple 布局为 FormatError，解码内容不因此丢失。正式质量资格与解码成功分开。

### 3.2.1 有限计划、参数与预算

每个 `BarcodeAttempt` 恰好一个手册精确码制，必须属于非空白名单；ID 在请求内唯一，索引从零开始。`Attempts.Count = MaxAttempts > 0`，不得超过 reader Profile 上限。请求 `ModelParameters` 是首项同一码制的基线，首项 Parameters 必须相等；后续项是完整替换快照，不隐式合并。不同 2D 码制必须使用各自完整参数及独立模型。各 attempt Domain 是请求 SearchDomain 的子集；只允许在请求原帧上按计划派生，不能链式使用上次增强结果。`TimeoutMs` 为正且不大于总 DeadlineMs；实际可用时间取该值与总 deadline 剩余值的较小者。所有转换、排队、find、查询计入总 deadline；到期停止新增工作，清理使用独立有限 drain window，超窗保持 DrainUnknown，不承诺物理释放恰在 deadline 内。

| ModelParameterKey | 唯一值类型/单位 | 有效域及 HALCON 映射 |
|---|---|---|
| ElementSizeMin/Max | PositiveDouble，px | 1D min∈[0.6,64]、max∈[1,256] 且 min≤max；同一 set 调用设置两者，避免中间一致性调整；`element_size_min/max` |
| ModuleSizeMin/Max | PositiveDouble，px/module | 2D 除 PDF417，min∈[1,100]、max∈[2,100] 且 min≤max；`module_size_min/max` |
| ModuleWidthMin/Max、ModuleAspectMin/Max | PositiveDouble，px 或无量纲 | PDF417 width min∈[1,100]、max∈[2,100]，aspect 两值∈[0.5,20]，分别 min≤max；`module_width_min/max`、`module_aspect_min/max` |
| NumScanlines | Integer，条 | 1D，≥0，0 自动；`num_scanlines` |
| StopAfterResultCount | Integer，个 | 1D≥0，0 不按数量提前停止；2D 必需且≥1，作为 find 的 GenParam 显式传入，禁止漏传而默认只读一条；达到上限标 BackendLimit/Incomplete |
| OrientationToleranceRadians | NonNegativeDouble，rad | 1D，Core∈[0,π/2] rad，adapter 显式 `degrees=radians×180/π` 映射 orientation_tol∈[0,90]，禁止把 rad 直接传入度参数 |
| Persistence | Persistence enum | 1D 仅 Temporary/Persistent；2D 三值；不将 DecodedOnly 映射给 1D |
| Polarity、Mirrored | 对应 enum | 2D，按手册映射 dark_on_light/light_on_dark/any、no/yes/any |
| StringEncoding | Encoding enum | 2D Utf8→utf8、Latin1→latin1、ShiftJis→shiftjis；Eci/Unknown 不得作为设置值 |
| PreserveUndecodedCandidates | Boolean | 2D true→discard_undecoded_candidates=no，false→yes |

重复 key、错误值子类型、码制不适用、范围无证据或跨字段冲突拒绝，不能静默取后值。首个 HALCON 切片只实现本表参数；完整码制/专属参数能力按 §2.2 分批验证，不声称表外参数或所有码制已完成。训练仅 ElementSize（1D min/max）或 ModuleSize（2D min/max，PDF417 为 width/aspect）这两个显式目标，禁止隐式 train all；新增训练目标先修订此契约。

HALCON find 只接收 Gray8。Original 仅接受 Gray8；RgbToGray8 使用 `cv2.rgb1_to_gray`；Gray16ScaleToGray8 使用 `cv2.scale_image_max`；InvertGray8 使用 `cv2.invert_image`。后两种为解码派生，不能用于原始印制质量评级。转换在完整原帧上先执行，再 reduce_domain；不得让不同 ROI 改变 Gray16 拉伸 extrema。常量 Gray16 的转换以 26.05 行为/Golden 确认，无法确定或超出 Profile 时返回参数不支持而不自写量化。没有匹配的显式转换项时拒绝 Gray16/Rgb8，不自动量化、缩放、裁切或改变相机。ROI 用 `cv2.reduce_domain` 保留原图坐标；2D 偶有域外结果时保留观察并附 `BARCODE.RESULT.OUTSIDE_DOMAIN`，标为工程候选，禁止静默当作 ROI 内读数；本切片不引入几何相交近似过滤。

Budget 各字节/像素/候选上限为非负 checked 整数，DeadlineMs 为 1..600000；0 代表不允许该类输出或分配，不代表无限。MaxInputBytes 覆盖取得的像素；MaxDerivedPixels 为各派生图像像素数累计；MaxRawBytes/MaxQualityBytes/MaxResultBytes 为请求累计复制量（UTF-8 文本字节及数组元素实际载荷，元数据上限由 Profile 另控）；MaxNativeBytes 为适配器受控分配水位，无法测量的 native 分配必须明确记 Unknown，不能声称硬上限已证明。预算不足不截断 payload/tuple 伪造完整结果；保留先前完整观察并返回 BudgetExceeded/Incomplete。

QualityRequest.Disabled 时 Standard/Revision/Conditions 为空、ResultFamilies 为空；Enabled 时 Standard/Revision/ResultFamilies 必需，Other 必须由已批准 Profile 定义结果族，否则 Unsupported。Conditions 缺失不拒绝 decode，逐项返回 MissingCondition；不在增强输入计算评级。HALCON 26.05 的 2D ISO15415 对应手册 ISO/IEC15415:2024，适用于除 DotCode 的页面列明码制；ISO29158 仅按 Data Matrix ECC200/Aztec/QR/MicroQR 家族查询；SEMI T10 仅 Data Matrix。1D ISO15416 需 persistence=1；2D persistence=-1 只允许 Data Matrix 的手册可用评级，其它类型不能借用。metric tuple 必须与该族 labels 对齐；不创建跨标准总分或用纠错等级填质量。Requested StandardRevision 与后端固定实现标准不符时 Unsupported，不能伪装使用新/旧标准。完整标准资格仍是宿主真实计量门。

ObservationId 固定为 RequestId 小写 N 格式 + / + AttemptId + / + 返回零基索引；CandidateId 类似但加 /candidate/，这些 ID 仅是本 operation 证据键，不承诺物理码跨帧 identity。AttemptId 仅 ASCII 字母/数字/_/-，1..64 字符。每个观察 Attempt/Adapter 必须与所在 attempt 汇总一致，RequestId 必须原样回传；adapter 不能返回别的请求内容。Core 检查错 ID/错长为 ResultFormatError，保留已合法复制部分。Result.IsComplete 表示本请求计划按停止规则结束且返回证据复制完整，AfterAnyDecodedObservation 仅对 State=Decoded 且无域外问题的读数触发；跳过后项需在汇总留 StoppedByPlan（Observation/Candidate 为空、ModelEpoch=null、ElapsedMs=0、NativeCallDrained=true，未创建 native）；不会把未执行后项伪称已搜。达到 stop_after_result_num、后端候选内部上限、timeout 或未知查询布局不得宣称 CandidateCompleteness.Complete；未知域外读数 ObservationState=Incomplete 并带问题。

### 3.3A 独立 Training Adapter 契约

训练是本模块必须交付的独立切片，Core decode 不隐式训练。宿主显式注入训练 adapter，取得能力后调用 `ValidateTraining → TrainAsync → 查询/续读 → 宿主保存回执 → AcknowledgeTrainingAsync`。训练 adapter 使用与 Core 相同的接纳、预留容量、深复制、取消意图、等待取消、单调序号、墓碑和关闭规则，账本空间独立；不得借用 decoder operation 改写原结果。

| 用途 | 必需输入与资格 | 输出与注册边界 |
|---|---|---|
| OfflineCandidate | SourceDecodeRequestId 可空；固定一个码制、非空有序样本；每个样本有逐字节 ground truth；非空 GoldenPlan 包含正/负/边界样本及独立真值；BaseModel hash 与 SourceModelEpoch/参数 manifest 匹配；FreshReadInput 明确冻结 | 通过读回、hash、所有 Golden 与 fresh read 后才返回 CompletedWithCandidate；CandidateAsset 是训练已关闭、重新读取验证过的隔离序列化副本；模块不写文件、不注册模型 |
| ProductionNoReadFallback | SourceDecodeRequestId 必需且宿主持久账本证明原解码已为 CompletedNoRead；Authorization 允许该政策；SourceDecodeEvidence.Receipt 为宿主保存的完整原始 BarcodeExecutionReceipt；按 §4.1 复算并匹配 ReceiptDigest/Receipt.ResultDigest，且 Acceptance=Accepted、State=Terminal、TerminalState=CompletedNoRead、ResourcesReleased=true，其 Result.RequestSnapshot 的帧 hash、完整域投影与 FreshReadInput 精确匹配，单一码制与源 epoch 匹配 BaseModel/SourceModelEpoch；每个源 decode 最多一次训练接纳，由宿主持久账本跨实例保证 | 一次训练 pass 和最多一次 fresh read；生产训练Samples恰1且同FreshReadInput/原单码ROI，不能追加其它帧；有真值则比较；所有成功的生产保底均只返回候选建议 CompletedWithAdvice；CandidateRegisterable=false、CandidateAsset=null、CandidatePersisted=false，临时候选必须销毁；宿主决定后续重采/人工处理，不改原 NoRead |

GroundTruth 是受控训练/Golden 的真值，按码制与 bytes 的无序多重集合匹配，重复码按数量保留，不允许按文本选出“符合期待”的一条。训练输入每个样本恰含一个受控目标，输出零条为 NoRead，多条/码制不符为 InvalidOutput；有真值且 raw 不可得时无法比较，拒绝候选；bytes 不符为 FalseDecode。生产无真值只标 NotEvaluated，不能描述为已证实正确。训练 adapter 不做 GS1 业务核对、身份或质量放行。

固定顺序：校验/冻结/接纳 → 在独立可终止 worker 从 BaseModel 复制新 epoch（生产/训练参数 Asset 若非空必须与 BaseModel 一致） → 读取并记录 Before 参数/hash → 对固定样本按输入序各最多一次 train-mode find → 每次检查输出和真值 → 读回 After 参数 → 退出训练模式 → 序列化并在隔离实例读回校验 → FreshReadInput 上一次普通 find（必须 Gray8；其它格式须由宿主提供有来源的冻结 Gray8 帧） → OfflineCandidate 的固定 Golden 逐项普通 find → 复制证据 → 排空/清理/释放租约 → 封存唯一终态。MaxTrainFindsPerSample=1、MaxFreshReads=1 是硬条件，不能由 bool 绕过；Golden find 不属于 fresh read，数量恰为计划 case 数且单独记账，预算包括它们。取消/失败后剩余样本为 NotRun，不能宣称所有 N 个样本均执行过。任何中间步骤失败停止后续训练和验证，不重跑、不补样本、不扩训练范围。

HALCON 训练可在已有训练范围内得到相同参数，因此“参数未变化”只记录 Before/After 相同，不单独拒绝。仍须验证非空合法读出、read-back、模型完整性和受控真值；byte-identical 的合法候选标记为无新修订建议，宿主无需注册。训练后的序列化模型 hash 不保证确定性，也不要求与训练前不同；比较的是保存/读回的内容完整性和参数/行为，不将两个独立序列化流必然相等当作引擎保证。ParametersSha256 统一使用 §4.1 的 `barcode-parameters-jcs-v1`，替换本页上轮自定义 little-endian 参数字节规则；不存在已发布本模块资产，禁止据此重算其它模块或旧客户资产。即使 hash 相同也记录完整 Before/After，不用 hash 替代参数读回。

训练期间 HALCON timeout 被忽略；1D abort 在 train mode 亦可能被忽略。因此 isolated worker 与可验证硬停是所有训练用途的必需条件，不能由 Profile 关闭。worker 输入必须为独立进程内可安全释放的副本，不把宿主 native 句柄跨进程传递。训练 adapter 拥有 provider lease，worker 借用受控副本；只有 native/worker 退出、候选句柄/像素副本释放、adapter 归还所有输入 lease 后，才可 `ResourcesReleased=true`。隔离本身不等于释放，进程退出也不自动证明宿主 lease 已归还。无法证明任一项为非终态 DrainUnknown，Outcome=null、TerminalSequence=null、CandidateRegisterable=false；只能查询/续读原 operation。

训练 adapter 在A完整接收/验证 OutputsComplete 后锁内封存执行原因；worker 在此之前自行宣称完成不抹掉A已接受的cancel/deadline。worker结果草稿含失败原因，A追加自己的取消/预算事实按§5.3归约；晚到ResultManifest不能恢复成功。训练状态正常为 Accepted→Preparing→Training→Validating→FreshRead→Validating（离线 Golden）→Draining→Drained→ResourcesReleased→Terminal；取消时先发 CancellationRequested 状态并记录取消意图，不启动下一样本，随后同一清理链。Outcome 只在 Terminal 非空；接纳前拒绝 Acceptance=Rejected、State/Outcome/TerminalSequence=null，有 Rejection 且不创建账本。TrainAsync 等待取消只停止等待；operation token 或 CancelTrainingAsync 触发同一幂等取消。ReadTrainingEventsAsync 从 afterSequence 后回放冻结 snapshot，再等待新事件，到 Terminal/DrainUnknown 结束本次有限观察；未知 ID 抛 KeyNotFoundException，取消 UnknownOperation，ack 使用相同的 BarcodeAcknowledgeState。history gap 是合成控制消息，不占用新 operation 序号。ack 后清除样本、模型 bytes、fresh read 和完整事件，只保留终态摘要/墓碑；Snapshot.Receipt 保留身份、终态序号及资源状态，重载字段为空。

CandidatePersisted 固定 false：本模块只返回候选 bytes，由宿主保存到临时位置、核验 hash 后原子替换。QualityEligibility=Passed 仅表示请求评级所需条件完整、质量族布局有效且取得原值，不表示等级达标；质量关闭时为 NotEvaluated。CandidateRegisterable 只表示离线技术证据完整，必须同时满足 ResourcesReleased、Outcome=CompletedWithCandidate、Golden=Passed、所有真值匹配、QualityEligibility=Passed 或在无评级需求时明确 NotEvaluated；它不是生产注册/放行许可。启用了评级请求而条件不足/不适用/质量布局错误时技术资格不成立。质量接收阈值仍由宿主持有，模块不判断客户质量通过。ActivityModelChanged 永远 false；原模型 bytes、epoch、参数和原 decode 结果不变。生产 fresh read 的每个 observation 另带新训练 RequestId/候选 epoch，宿主必须显示“训练候选”。

| 失败 | 终态 Outcome（已释放时） | 保留与恢复 |
|---|---|---|
| 第一个样本 NoRead/输出为空 | NoSuccessfulSample | 样本 NoRead、后续 NotRun；无 fresh read；销毁候选 |
| 多条输出/码制不符/tuple 非法 | InvalidOutputRejected | 输出摘要与错误；不任选一条继续 |
| 真值 bytes 不符 | FalseDecodeRejected | 不匹配证据；不改真值、不重跑 |
| 参数读回/保存读回不符 | ParameterReadbackFailed / ModelIntegrityFailed | Before/After、hash 和诊断；保持原活动模型 |
| fresh read 或 Golden 不符 | 真值bytes不符为FalseDecodeRejected；缺读数/资格不足为GoldenValidationFailed，优先级见§5.3 | case/输入/结果引用；不返回可注册资产 |
| 总预算到达、native 异常、资源异常 | BudgetExceeded / AdapterError / ResourceError | 部分证据；仅确认释放后封存 |
| 取消 | Cancelled | 样本逐项状态；活动模型不变 |
| 停止/释放未确认 | 无 Outcome，DrainUnknown | 隔离原 worker/epoch，查询与续读；不得再次启动保底 |

worker IPC 工程规格固定于 §7.5，算子实参固定于 §7.4.1；训练 benchmark、真实 worker 构建/封送和 HALCON train/fresh read/Golden 是后续验证门。本页冻结上述行为，不伪造已编译的 `cv2` C# 重载。只有出现类型/封送歧义才查公共签名，不重新审查算子覆盖或用户确定依赖。

### 3.3 质量与身份分层

模块只交出 `Decoded`、`QualityMeasured` 等视觉事实。以下是调用方后续独立层：

```text
RawPayload/EngineText → 应用解析（GS1/客户规则）
                     → IdentityResolutionReceipt（PKG-037）
                     → 工艺/质量规则
                     → InspectionFact/放行（原 Owner）
```

期待串不能进入模块的候选排序；同一内容的两个不相交位置是两个观察；同一位置的冲突读数全部保留，交给身份 Owner 处理。

## 4. 执行入口和事件顺序

本节的公共类型、方法和生命周期构成 `Barcode.Core` 唯一的 Module API Contract v0.2。它只冻结可复用 Core、Simulator 和显式适配端口，不采纳平台条码身份、质量放行、产品 Schema 或业务持久化字段；接口变更须修订本唯一指导并提升 Contract 主/次版本，不允许实现者自行造第二套 Core DTO。

通过纯校验后，Core 提供两个语义相同的执行入口：

```csharp
public sealed record BarcodeReaderProfile(string Revision, int MaxActiveOperations,
    int MaxUnacknowledgedOperations, int MaxAcknowledgedTombstones,
    int MaxAttemptsPerOperation, int MaxCandidatesPerAttempt,
    int MaxEventRecordsPerOperation, long MaxBufferedResultBytes,
    long MaxManagedBytes, long MaxNativeBytes, long DrainWindowMs);
public enum BarcodeCloseState { Closed, DrainUnknown }
public sealed record BarcodeCloseReceipt(BarcodeCloseState State,
    IReadOnlyList<Guid> UnreleasedOperationIds, IReadOnlyList<string> DiagnosticIds);
// 冻结的公开构造：BarcodeReader(BarcodeReaderProfile profile)；尚未实现。
// BarcodeReader : IBarcodeReader；无默认单例、无隐藏存储与后台设备初始化。
public interface IBarcodeReader
{
BarcodeValidation Validate(BarcodeRequest request);
ValueTask<BarcodeExecutionReceipt> ExecuteAsync(
    BarcodeRequest request,
    IBarcodeDecoderAdapter decoderAdapter,
    IProgress<BarcodeProgress>? progress = null,
    CancellationToken operationCancellationToken = default,
    CancellationToken waitCancellationToken = default);
IAsyncEnumerable<BarcodeEvent> ExecuteEventsAsync(
    BarcodeRequest request,
    IBarcodeDecoderAdapter decoderAdapter,
    CancellationToken operationCancellationToken = default,
    CancellationToken observerCancellationToken = default);
ValueTask<BarcodeOperationLookup> QueryOperationAsync(
    Guid requestId,
    CancellationToken readCancellationToken = default);
IAsyncEnumerable<BarcodeEvent> ReadEventsAsync(
    Guid requestId,
    long afterSequence,
    CancellationToken readCancellationToken = default);
ValueTask<BarcodeCancelReceipt> CancelOperationAsync(
    Guid requestId,
    string reasonCode,
    CancellationToken callCancellationToken = default);
ValueTask<BarcodeAcknowledgeReceipt> AcknowledgeAndReleaseAsync(
    Guid requestId,
    long terminalSequence,
    CancellationToken callCancellationToken = default);
ValueTask<BarcodeCloseReceipt> CloseAsync(CancellationToken waitCancellationToken = default);
}

```

`IBarcodeInputProvider` 也必须由宿主显式注入到 `BarcodeRequest`；Core 只能调用该 provider 获取像素和 ROI，禁止按 `FrameId` 查询服务、服务定位器、环境变量、私有数据库路径或隐藏 UI 状态。`AcquireAsync` 成功返回后，Core 成为 `IBarcodeInputLease` 的活动 owner；适配器只读借用每项 lease，不得释放、保存或跨 attempt 继续使用。Core 必须在 adapter/native 调用确认 `Drained` 且 AdapterResourcesReleased 后最后释放 lease。成功、取消、异常、`DrainUnknown` 及 worker 隔离路径都必须记录 lease 的释放或隔离回执；释放未知时不得复用帧或启动第二个 operation。

`IBarcodeDecoderAdapter` 必须由宿主显式注入，并在模块实例生命周期内保持单一所有权；Core 不从服务定位器、环境变量或隐藏 UI 获取适配器。适配器只返回已深复制的 `BarcodeObservation` 和可验证的排空/资源回执，不能把 HALCON/native 句柄泄漏到 Core。以下类型是该入口的固定公共形状：

```csharp
public sealed record BarcodeValidation(bool IsValid,
    IReadOnlyList<string> ErrorCodes, string? DiagnosticId);
public abstract record BarcodeEvent(Guid RequestId, long Sequence);
public sealed record BarcodeProgress(Guid RequestId, long Sequence, string Stage,
    int? AttemptIndex, double? Fraction) : BarcodeEvent(RequestId, Sequence);
public sealed record BarcodeRequestRejected(Guid RequestId, string ErrorCode,
    string DiagnosticId) : BarcodeEvent(RequestId, 1);
public sealed record BarcodeStateChanged(Guid RequestId, long Sequence,
    BarcodeExecutionState State, string? AttemptId, string? ModelEpoch,
    string? LocalCode, DateTimeOffset TimestampUtc) : BarcodeEvent(RequestId, Sequence);
public sealed record BarcodeResultReady(Guid RequestId, long Sequence,
    BarcodeResult Result) : BarcodeEvent(RequestId, Sequence);
public sealed record BarcodeDrainUnknown(Guid RequestId, long Sequence,
    string LastKnownStage, string? IsolatedWorkerId,
    IReadOnlyList<string> DiagnosticIds) : BarcodeEvent(RequestId, Sequence);
public sealed record BarcodeOperationCompleted(Guid RequestId, long Sequence,
    BarcodeTerminalState TerminalState, string? ResultDigest,
    IReadOnlyList<string> DiagnosticIds, DateTimeOffset TimestampUtc, long ResultSequence)
    : BarcodeEvent(RequestId, Sequence);
public sealed record BarcodeEventHistoryGap(Guid RequestId, long Sequence,
    long FirstAvailableSequence, long LastReleasedSequence)
    : BarcodeEvent(RequestId, Sequence);
```

公开记录的唯一形状如下；枚举值是候选 Contract 的封闭集合，所有事件载荷与快照深不可变：

```csharp
public enum BarcodeExecutionState
{
    Accepted, Executing, CancellationRequested, Draining, Drained,
    ResourcesReleased, DrainUnknown, Terminal
}

public enum BarcodeTerminalState
{
    CompletedWithReads, CompletedNoRead, CompletedWithCandidates,
    BudgetExceeded, Cancelled, AdapterError, ResultFormatError, ResourceError
}

public enum BarcodeAcceptanceState { Accepted, Rejected }

public sealed record BarcodeRequestRejection(
    Guid RequestId,
    string ErrorCode,
    string DiagnosticId);

public sealed record BarcodeExecutionReceipt(
    Guid RequestId,
    BarcodeAcceptanceState Acceptance,
    BarcodeExecutionState? State,
    bool ResourcesReleased,
    BarcodeResult? Result,
    BarcodeTerminalState? TerminalState,
    long? ResultSequence,
    long? TerminalSequence,
    BarcodeRequestRejection? Rejection, string? ResultDigest = null);

public sealed record BarcodeOperationSnapshot(
    Guid RequestId,
    BarcodeExecutionState State,
    long LastSequence,
    bool ResourcesReleased,
    BarcodeResult? Result,
    BarcodeTerminalState? TerminalState,
    long? ResultSequence,
    long? TerminalSequence,
    bool PayloadReleased,
    string? ResultDigest);

public enum BarcodeAcknowledgeState
{
    Released, AlreadyReleased, NotTerminal, DrainUnknown,
    TerminalSequenceMismatch, UnknownOperation
}

public sealed record BarcodeAcknowledgeReceipt(
    Guid RequestId,
    BarcodeAcknowledgeState State,
    long? ConfirmedTerminalSequence,
    bool PayloadReleased,
    string? DiagnosticId);

public enum BarcodeCancelState
{
    Requested, AlreadyRequested, UnknownOperation, ExecutionSealed, AlreadyTerminal, DrainUnknown
}

public sealed record BarcodeCancelReceipt(
    Guid RequestId, BarcodeCancelState State, long? Sequence,
    string? DiagnosticId);

public abstract record BarcodeOperationLookup
{
    private BarcodeOperationLookup() { }
    public sealed record Found(BarcodeOperationSnapshot Snapshot) : BarcodeOperationLookup;
    public sealed record Unknown(Guid RequestId, string DiagnosticId) : BarcodeOperationLookup;
}
```

`Validate` 是纯校验，不创建 native 资源；无效请求不进入执行。`ExecuteAsync` 与 `ExecuteEventsAsync` 是对同一个 `RequestId` 的两种启动/消费方式，只能选一种启动一次。接纳前拒绝以 `Acceptance=Rejected`、`State=null`、`ResourcesReleased=false` 和单一 `Rejection` 返回，不生成运行结果/终态序号。已接纳 operation 必须创建深不可变的 `BarcodeResult` 对象，即使没有成功读数也保留空观察、attempt 候选和错误；完整执行且无候选的正常 NoRead 可为 IsComplete=true，错误/预算/取消导致证据不全才为 false；确认释放后以 `State=Terminal`、`ResourcesReleased=true` 返回该结果、唯一 `TerminalState` 和相应序号。若有限排空窗口结束仍不能确认释放，则以 `State=DrainUnknown`、`ResourcesReleased=false` 返回当前已复制的 `BarcodeResult`（`IsComplete` 可为 false）和诊断，`TerminalState`/`TerminalSequence` 为空。该回执不是终态；宿主只能查询/续读原 operation，不能重跑。事件模式对已接纳请求发出 `BarcodeResultReady(RequestId, Sequence, Result)`（结果对象已深复制，`IsComplete` 反映证据是否完整）和唯一终态事件 `BarcodeOperationCompleted(RequestId, Sequence, TerminalState, ResultDigest, ...)` 后结束枚举；若进入 `DrainUnknown`，发出 `BarcodeDrainUnknown` 后结束本次有限观察，无 `ResourcesReleased` 或终态事件，后续由 `ReadEventsAsync` 续读。接纳前拒绝只发一条 `BarcodeRequestRejected` 后结束。已接纳失败也必须返回含稳定错误和部分观察的完整 `BarcodeResult` 对象，不可用异常丢掉已复制证据。`Result` 是深不可变且已脱离 native 句柄的 `BarcodeResult`，不能只有摘要或 replay 引用。观察者取消事件枚举只结束该观察者，不取消或重启 operation。

`ExecuteAsync` 的 `operationCancellationToken` 只表达取消 operation 的意图；`waitCancellationToken` 只取消调用方等待，不取消后台 operation。`ExecuteEventsAsync` 的 `observerCancellationToken` 只结束当前观察者；`ReadEventsAsync` 的 `readCancellationToken` 只取消事件读取。调用方必须通过 `CancelOperationAsync` 请求 operation 取消；该调用本身的 `callCancellationToken` 只取消等待取消回执，不撤销已接受的取消请求。取消回执状态闭合为 `Requested`、`AlreadyRequested`、`UnknownOperation`、`ExecutionSealed`、`AlreadyTerminal` 和 `DrainUnknown`。

当 `operationCancellationToken` 在接纳后触发时，Core 将其视为一次幂等的 operation cancel request，并按同一排空状态机处理；它不等价于线程中断，也不证明 native 已停止。`waitCancellationToken` 或 observer/read token 的触发不得改变该 operation 的状态、排空责任或结果保留。

接纳前 operation token 已取消时启动入口返回 `BarcodeRequestRejected(BARCODE.CANCEL.BEFORE_ACCEPT)`，不创建 operation；CancelOperationAsync 对未登记 ID 返回 UnknownOperation，不推断其从未接纳；执行封存前接纳的取消按 `CancellationRequested → Draining → Drained → ResourcesReleased` 闭合，唯一终态按 §5.3 归约（无更高原因才 Cancelled）。重复取消幂等返回 `AlreadyRequested`，不得重复发起 native abort。若排空无法确认，返回 `DrainUnknown`，不得创建第二个 operation、不得自动重试；宿主只能查询/续读原 `RequestId`。 

所有 operation 事件序号从 1 单调递增且不复用，并带 `Guid RequestId` 和不可变载荷；有模型上下文的状态/尝试事件带 `ModelEpoch`，接纳前拒绝、进度、结果载荷和历史间隙按各自载荷关联请求或结果，不伪造模型 epoch。`ReadEventsAsync(requestId, afterSequence)` 只续读仍保留的事件；历史正文已确认释放或游标落在缺失区间时，必须先给 `BarcodeEventHistoryGap(RequestId, Sequence, FirstAvailableSequence, LastReleasedSequence)`，不能伪装成连续日志。`QueryOperationAsync` 返回闭合的 `BarcodeOperationLookup`：`Found(snapshot)` 或 `Unknown(requestId, diagnosticId)`。当前实例保留的已确认释放墓碑仍返回 `Found(snapshot)`，其中 `Result=null`、`PayloadReleased=true`，并保留终态、摘要和序号；只有查无记录、进程重启/不可达或状态不完整时才返回 `Unknown`。`Unknown` 不代表未接纳，也不得据此重试原请求。预检验证失败和接纳前容量拒绝通过原调用结果/单条 `BarcodeRequestRejected` 明确报告，不创建已接纳 operation；查询接口不推断或保存“从未接纳”事实。

`BarcodeOperationSnapshot` 必须包含上述完整形状。`AcknowledgeAndReleaseAsync` 的宿主顺序固定为：先收到完整结果和唯一终态，按业务 Owner 规则持久化两者及 `RequestId`/序号/摘要，确认提交回执后，再用原 `RequestId` 和精确 `TerminalSequence` 确认释放。若宿主提交结果未知，先查询宿主自己的提交回执和本模块原 operation，不得盲目 ack 或重跑。ack 仅在唯一终态已发布、`ResourcesReleased=true` 且序号匹配时，原子清除完整结果与事件正文、释放保留容量并留下本实例内的轻量终态去重墓碑；相同序号重复 ack 返回 `AlreadyReleased`，不得重复删除/释放。其它结果使用 `NotTerminal`、`DrainUnknown`、`TerminalSequenceMismatch` 或 `UnknownOperation` 明确表达，均不释放 payload。墓碑受有界上限约束，达到上限后拒绝新接纳，直到安全轮换已排空的模块实例；不得静默逐出墓碑后仍声称可以去重。轮换/进程重启后旧 RequestId 查询为 `Unknown`，跨进程幂等由宿主持久账本保证。ack 后快照只保留终态摘要，`Result=null`、`PayloadReleased=true`；事件续读返回 history-gap 标记。

模块 Profile 必须冻结 `MaxActiveOperations`、`MaxUnacknowledgedOperations`、`MaxAcknowledgedTombstones`、`MaxAttemptsPerOperation`、`MaxCandidatesPerAttempt`、`MaxEventRecordsPerOperation`、`MaxBufferedResultBytes` 和总 native/托管内存上限。接纳前一次性预留该请求最坏情况下的关键事件/终态记录与结果字节额度；进度事件可合并，关键状态、每次尝试结果、`BarcodeResultReady` 和唯一终态不得丢弃。若无法预留或任一并发/容量上限已满，在借用图像帧或创建 native 资源前返回 `Acceptance=Rejected`、`BARCODE.OPERATION.CAPACITY`。未确认的已接纳记录不能因 TTL 或内存压力被静默驱逐。宿主持久化完整结果和唯一终态并成功 ack 后，模块释放大结果和事件正文，仅保留受限的轻量 RequestId/终态墓碑以阻止本实例内重复接纳；墓碑上限已满时停止新接纳，直到所有操作真实排空并安全轮换实例，不能静默逐出后继续声称可去重。实例轮换/进程退出会清除本地查询证据；旧 RequestId 随后为 `Unknown`。宿主必须在 dispatch 前持久化 RequestId/输入身份并作为跨进程幂等权威；任何 Unknown 均不得盲目重执行。

Profile 各计数上限必须正数、内存上限非负、DrainWindowMs∈[1,600000]；最坏关键事件预留至少 `6×MaxAttempts+11`（checked），进度不另分配关键序号。DrainUnknown 只在首次转换发一次；同状态的查询不增加事件，恢复只继续 Drained/ResourcesReleased/Terminal，不循环重复关键状态。reader 关键事件容量不足接纳前拒绝，不在结果出现后才删除证据。

接纳在 reader 内原子化：同一 RequestId 任何第二次启动（无论参数相同或不同、正在运行、DrainUnknown、终态或已 ack）都返回接纳前 BARCODE.OPERATION.DUPLICATE，不再执行 native；宿主用 Query/Read 恢复。不同 RequestId 的并发必须使用独立模型，不超过 reader/adapter 较小上限；队列等待计入 deadline。ExecuteEventsAsync 是 lazy：首次 MoveNextAsync 才冻结/接纳，未枚举不创建 operation；同一 enumerable 再次枚举触发重复拒绝。observer 在接纳前已取消时仅结束观察，不接纳；接纳后的 Dispose/读取取消不改变 operation。ExecuteAsync 等待取消抛 OperationCanceledException，只取消等待；调用方按已知 ID Query，不能由异常断言未接纳。ReadEventsAsync 未知 ID 抛 KeyNotFoundException；afterSequence<0 或大于 LastSequence 抛 ArgumentOutOfRangeException；只在已发布 Terminal/DrainUnknown 的有限边界结束。history gap 为控制消息，Sequence=已释放末序号，不新分配或重用 operation 事件序号。

CloseAsync 首次调用原子停止新接纳（BARCODE.OPERATION.CLOSED），向运行 operation 请求一次取消，等待至 Profile.DrainWindowMs；Closed 只表示执行资源均已释放，未 ack 的结果/墓碑仍可查询/ack。DrainUnknown 返回未释放 ID，reader 保持关闭接纳且继续原账本恢复；重复 Close 幂等，不丢结果、不清空配置或强制释放。等待 token 只停止等待，关闭流程继续。纯 Core 不负责进程强杀；训练 worker 硬停由训练 adapter 实现并给证据。宿主最终持久化/ack 后才丢弃实例。

异步入口可以从 WPF Dispatcher 或其它线程调用。入口在返回控制权前只允许执行有界的契约校验、接纳和调度准备；HALCON/native 调用不得在调用方线程、捕获的 `SynchronizationContext` 或 UI Dispatcher 上执行。Core 和适配器不得同步等待 UI 回调，不得用内部 `Task.Run` 掩盖未声明的阻塞；native 工作由适配器声明并实现的专用调度/串行策略承载，适配器需公开并发能力、线程亲和性和排队上限。Core 的异步延续不得要求 UI 上下文。进度/事件先复制为不可变载荷，经有界队列异步交付；观察者抛错或变慢不得阻塞 native 工作或改变操作终态。UI 消费者自行将展示更新投递到 Dispatcher。`IProgress<BarcodeProgress>` 实现必须是非阻塞接收端；观察者异常只记诊断，不得改写解码结果。

事件只报告过程，不替代最终结果或提交回执，顺序固定如下。对已接纳请求，唯一 `BarcodeOperationCompleted` 必须在 `ResourcesReleased` 之后发布；`BarcodeResultReady` 可在排空前发布，因为其结果已经深复制并与 native 资源脱离。

1. BarcodeStateChanged(Accepted) 表示接纳；`InputValidated` 等阶段使用下述唯一 BarcodeStageEvent，不再隐含未定义事件类型。
2. 每项依次发 InputValidated→ModelLeased→AttemptStarted→CandidatesCaptured→QualityCaptured→AttemptFinished；未到达的阶段不伪造成功事件，错误由 AttemptFinished/BarcodeIssue 表达。进度可合并，关键阶段各一次。
3. 所有已复制执行结果发布 BarcodeResultReady；正常 NoRead 也发布空 Observations 和非空 Attempts；清理故障可按 §5.3 发布唯一修订，终态引用最后 ResultSequence。
4. BarcodeStateChanged(Draining)→确认 native/回调退出→BarcodeStateChanged(Drained)→适配器清理完成→Core 归还输入 lease→BarcodeStateChanged(ResourcesReleased)。
5. BarcodeOperationCompleted 是唯一终态事件；快照原子成为 Terminal，不再另发 Terminal 状态事件。失败/取消/预算亦须经过同一释放链。DrainUnknown 则发 BarcodeDrainUnknown，Outcome 未封存，本次有限观察结束；后续只能从原账本续读。

```csharp
public enum BarcodeStage { InputValidated, ModelLeased, AttemptStarted,
    CandidatesCaptured, QualityCaptured, AttemptFinished }
public sealed record BarcodeStageEvent(Guid RequestId, long Sequence,
    BarcodeStage Stage, string AttemptId, string? ModelEpoch,
    AttemptEvidence? Evidence, IReadOnlyList<string> DiagnosticIds,
    DateTimeOffset TimestampUtc) : BarcodeEvent(RequestId, Sequence);
```

StageEvent 是过程摘要，候选/质量完整载荷只存于最终结果和 attempt 汇总；各个阶段不复制多套 payload。无模型阶段 ModelEpoch=null；候选为空也发 CandidatesCaptured，质量未请求也发 QualityCaptured（结果标 NotRequested）。Core 不产生训练状态事件。只有真实的 AdapterResourcesReleased 与全部输入 lease DisposeAsync 完成，Core 才能发布 ResourcesReleased，适配器 drain 的 bool 不替代 Core 的释放证明。

发生配置错误、输入错误或模型创建失败时，已接纳请求仍须经过 `Draining → Drained → ResourcesReleased`，再发送唯一终态；未接纳且无资源的预检拒绝走有明确拒绝原因的短路径，不伪造执行事件。执行封存前被接纳的取消请求必须先收到 `CancellationRequested`，再等待适配器确认 native 调用退出；不能先释放仍被 native 使用的图像或句柄。若 drain deadline 到期仍无法确认退出，operation 保持非终态 `DrainUnknown`，查询快照标记 `ResourcesReleased=false`，事件流发布 `BarcodeDrainUnknown(RequestId, Sequence, LastKnownStage, IsolatedWorkerId?, DiagnosticIds)` 并停止本次有限观察；不得发送 `ResourcesReleased`、`Cancelled` 或终态事件。原 operation 仍可由 `QueryOperationAsync` 查询，后续观察用 `ReadEventsAsync` 按最后序号续读。仅当适配器后来证明 native 已退出并完成资源归还，才能继续 `Drained → ResourcesReleased → 唯一终态`；若宿主硬隔离/终止 worker，必须先有可验证进程退出回执且输入租约/句柄所有者确认真实归还，再推进释放状态；只有隔离而无归还证明继续 DrainUnknown。迟到事件带原 `RequestId`/`ModelEpoch` 和序号，宿主负责丢弃过期界面投影，但不得丢弃诊断证据。

### 4.1 回执与参数摘要的唯一 JCS 投影

真实消费者有两个：宿主持久化/查询时核对同一 operation 完整回执；训练 adapter 核对 ProductionNoReadFallback 的 SourceDecodeEvidence。它不是生产正确性、身份、授权证明或数字签名。复用项目已采纳的 [RFC 8785 JCS 规则](../../shared-modules/packages/PKG-033_ModelAssets.md)与 [model-assets 参数投影原则](../model-assets/DEVELOPMENT-GUIDE.md#42-声明性参数与技术投影)，仅定义 barcode 的独立投影/规则 ID，不把条码结果冒作 model-core-jcs-v1 资产。

摘要统一表示为 `ruleId:sha256:lowerHex64`，算法输入为 RFC 8785 规范 UTF-8 字节，无 BOM/空白/末尾换行。使用经 RFC §3/附录 B 验证的 JCS 实现，普通 JsonSerializer 输出不称 canonical。对象属性按未转义 UTF-16 无符号码元递归排序；数组从投影阶段规定顺序，JCS 不排序数组。拒绝重复键、孤立 surrogate、未知 enum、NaN/Infinity 和负零；double 是有限 binary64、严格按 JCS ECMAScript 数字规则，不用文化格式、不写舍入字符串，不做 NFC/NFD。Int32 使用 JSON number；Int64（序号、字节数、长预算）统一无加号/前导零的十进制字符串；Guid 是小写 N 格式；enum 是本页 C# 精确成员名。所有可空字段显式 null，空集合 `[]`、空文本 `""` 与 null 不等价；必需字段缺失拒绝，不用默认补齐。

字段名固定为声明中的 PascalCase（root 的 rule/contract/content 为小写）；所有 record 递归输出其全部声明字段，除表中显式排除项，不能自动省 null/忽略新字段。抽象 union 加固定 `$type`=公开嵌套成员名（如 SearchDomainShape.Polygon、ModelParameter.PositiveDouble、CoordinateTransform.Affine），包含该成员全部字段；不写程序集限定名。ModelParameter.Value 类型按自身子类型决定，Integer 用 Int64 字符串，enum 字符串，bool JSON bool。所有 bytes/ReadOnlyMemory<byte>（含 ModelAsset.Bytes、Raw.Bytes、真值）投影为 `{LengthBytes:规范Int64字符串,Sha256:原字节lowerHex64}`，null 仍 null；像素不重复放进结果，通过 Input.PixelSha256 和完整尺寸/格式/坐标绑定。原 bytes 必须另由宿主保留才能复验。各个 Sha256 引用严格 lowerHex64，不接受大小写折叠。

| 规则 ID / content 闭集字段 | 输入与排除 / 数组顺序 |
|---|---|
| barcode-parameters-jcs-v1；content={Values} | ModelParameters.Values 按 ModelParameterKey 精确成员名的 ordinal UTF-16 顺序；重复 Key 拒绝。排除 Revision/Asset，每条保留类型/Key/Value；单位由 Contract v0.2 固定 |
| barcode-decode-receipt-jcs-v1；content={RequestId,State,ResourcesReleased,Result,TerminalState,ResultSequence,TerminalSequence} | 仅 Accepted 且 Terminal/ResourcesReleased=true 的完整回执；Result 所有字段进入，含 RequestSnapshot、Attempts/Observations/Issues、ResultRevision。排除 Acceptance/Rejection（固定 Accepted/null）、ResultDigest/事件 TimestampUtc/诊断 sink 实现；Result 内 DiagnosticId、耗时/水位、TraceContext 等既有字段仍包含 |
| barcode-training-receipt-jcs-v1；content={Receipt} | 仅 Accepted Terminal 且已释放的完整训练回执；Receipt 全部字段进入，含 Before/After、样本、fresh read、Golden、候选 asset 引用与布尔；不含 Snapshot.LastSequence/PayloadReleased/ResultDigest 或事件时间；DiagnosticIds 保序 |

训练 TrainingSampleResult.OutputHash 若非null，固定 lowerHex64 的 SHA-256，输入为 `{rule:"barcode-sample-output-jcs-v1",contract:"barcode-api-v0.2",content:{Observations:该次样本已安全复制观察数组}}` 的 JCS字节；该值只核同一输出，不代替逐字节真值。未执行/输出非法未安全复制时为null，合法空输出可对空数组生成hash。

每个 root 恰为 `{rule:规则ID,contract:"barcode-api-v0.2",content:上述对象}`。SymbologyAllowList 为集合，投影前 ordinal UTF-16 升序且重复拒绝；ModelParameters.Values 按 Key 排序；TrainingModelEvidence.TrainedGeneralNames/TrainedSpecificNames也是集合，ordinal UTF-16排序且拒重复；其余数组均按原输入/后端复制顺序保留，含 Attempts、Observations、Candidates、Quality、Issues、polygon 顶点、ResultFamilies、AllowedEncodings、Golden failed cases、Diagnostics。排序只作用投影，不改 DTO 展示/执行顺序；执行顺序来自 AttemptPlan。包含实际耗时意味着两次独立运行可有不同摘要，不作识别等价摘要。重复 bytes 引用按各位置保留，不依赖 serializer 引用去重。

ResultDigest 在 ResourcesReleased 后，唯一终态序号已预留且 ResultSequence/Result/TerminalState 固定时生成，随 BarcodeOperationCompleted/ExecutionReceipt/快照同值发布；BarcodeOperationCompleted.ResultSequence 必须指向最后ResultReady，宿主按其核对本地快照，缺该序号则Query/Read恢复而不提交；终态事件 TimestampUtc 不参与，避免摘要环。Rejected/进行中/DrainUnknown 时为空，不用部分结果算终态摘要。训练同样预留 TerminalSequence 后计算 Receipt 摘要，存 Snapshot.ResultDigest。ack 后保留原摘要，不从已清空 payload 重算；宿主持久化完整回执与原 bytes 后才 ack。摘要输入验证失败归入结构错误：adapter返回边界先验证每条record，非法Observation/候选/metric不进入结果，仅保留合法先前记录与Core产生的 BARCODE.RESULT.CARDINALITY/诊断ID，attempt计为Error/Incomplete；非法native文本只保存raw诊断摘要hash，不转成另一个payload。请求本身的非法数值/Unicode在接纳前拒绝。因此失败回执仍由受信、可JCS编码的DTO构成；不能发布成功或无效摘要。

Result.RequestSnapshot 是接纳深冻结request删去InputProvider后的唯一值投影，RequestId等于Result/Receipt.RequestId；所有字段来自实际执行计划，不在结束时用最新配置重建。Core/Simulator由Core构造该快照，adapter不能写入。CandidateModelEpoch 由A接纳时生成非空Guid小写N字符串，独立于SourceModelEpoch，worker收到后只回传该值；Begin.Request不新增源API字段，Begin.Body另增加 CandidateModelEpoch 与 Frames 必需键。Before.Epoch=SourceModelEpoch，After.Epoch=该candidate，fresh read与IPC Stage的epoch必须匹配。

SourceDecodeEvidence 内嵌完整 Receipt，adapter 复算并比较 Receipt.ResultDigest 与外层 ReceiptDigest，逐项核对外层 RequestId/状态/资源/帧/域/单一码制/epoch；SourceDecodeRequestId 相同。仅一个生产码制、各 attempt 均该码制、无工程宽搜、原完整 NoRead 且无质量/格式/预算等错误才允许保底；完整 SearchDomain 的 JCS 投影与 FreshReadInput.Domain 相同，不仅比较 DomainId。BaseModel.Sha256 对应原 RequestSnapshot.ModelParameters.Asset.Sha256；原模型必须显式有 Asset，否则拒绝关联训练，不猜运行时默认模型。摘要不证明合法授权，权限仍由注入宿主策略保证，不查询其它模块数据库。

新增字段/enum/单位/集合顺序须升对应摘要 rule ID；旧规则只用于原样复验，不重算旧身份。v0.2.1 是准备稿补缺，不改其它模块已发布规则。参数顺序变化不改参数摘要，attempt/候选顺序变化改回执摘要；null/空、模型 hash、raw 改位均可判别。测试复用 RFC 的 UTF-16/整数形属性/浮点/非法 Unicode 用例，并验证 ack 前后摘要一致及 SourceDecodeEvidence 篡改拒绝。

## 5. 状态和错误码

### 5.1 顶层状态

| 状态 | 语义 |
|---|---|
| `Accepted` | 接纳完成，预算和请求快照已冻结 |
| `Executing` | 至少一次尝试运行中 |
| `CancellationRequested` | 已请求取消，native 调用尚未确认退出 |
| `Draining` | 不再启动新尝试，等待 native、回调和复制结束 |
| `Drained` | native 与回调已退出，资源尚未全部归还 |
| `ResourcesReleased` | native 资源、缓冲与输入租约已确认归还；仍等待唯一终态封存 |
| `Terminal` | 唯一 `BarcodeTerminalState` 已封存；结果和终态序号可查询 |
| `DrainUnknown` | native 执行/释放结果无法确定的非终态；资源状态未知，保持隔离并按原 RequestId 查询；禁止当作失败后自动重试 |

`BarcodeTerminalState` 是执行结果分类，与生命周期状态分开：`CompletedWithReads`、`CompletedNoRead`、`CompletedWithCandidates`、`BudgetExceeded`、`Cancelled`、`AdapterError`、`ResultFormatError`、`ResourceError`。`InvalidInput` 和容量拒绝发生在接纳前，通过 `BarcodeRequestRejection` 返回；不创建 operation、native 资源或终态事件。`ResourceError` 只有在 `ResourcesReleased=true` 后才能成为唯一终态，否则保持 `DrainUnknown`。

质量状态与顶层状态并列：`NotRequested`、`Measured`、`NotApplicable`、`MissingCondition`、`Unsupported`、`FormatError`、`Incomplete`、`Error`。`Decoded` 不等于 `QualityMeasured`，低质量不等于 `CompletedNoRead`。

### 5.2 稳定错误码

错误码采用稳定字符串，新增只能追加，不能复用旧含义：

| 错误码 | 含义和调用方动作 |
|---|---|
| `BARCODE.INPUT.EMPTY` | 空图像/空域；修正输入，不重试同一引用 |
| `BARCODE.INPUT.FORMAT` | 像素格式、尺寸或 stride 不支持 |
| `BARCODE.INPUT.DOMAIN` | ROI 越界或变换链不完整；静区不足只影响可读性/质量条件，不伪称坐标非法 |
| `BARCODE.PARAM.INVALID` | 数值、交叉约束或枚举非法 |
| `BARCODE.PARAM.UNSUPPORTED` | 本 adapter 尚未实现或验证该码制、参数或结果族；保留明确原因，不自动改参数 |
| `BARCODE.OPERATION.DUPLICATE` / `BARCODE.OPERATION.CLOSED` | 重复 ID/已开始关闭；不接纳、不启动 native，查询原请求或更换已排空实例 |
| `BARCODE.CANCEL.BEFORE_ACCEPT` | operation token 接纳前已取消；不创建 operation |
| `BARCODE.RESULT.OUTSIDE_DOMAIN` | 后端返回域外符号；保留工程候选，宿主不能当作 ROI 内读数 |
| `BARCODE.OPERATION.CAPACITY` | 接纳前无法预留关键事件/结果容量或并发上限已满；拒绝请求，不借用图像/创建 native 资源 |
| `BARCODE.MODEL.CREATE` / `BARCODE.MODEL.CONFIGURE` | 模型创建或参数读回失败；隔离租约 |
| `BARCODE.BACKEND.CALL` | 后端调用异常；记录原错误摘要，不能清空结果 |
| `BARCODE.BACKEND.ABORTED` | 后端报告显式 abort；结合释放确认映射为 `Cancelled`，未确认时保持 `DrainUnknown` |
| `BARCODE.BACKEND.TIMEOUT` | 后端/总 deadline 超时；保留已复制观察；释放确认后为 `BudgetExceeded`，否则保持 `DrainUnknown` |
| `BARCODE.RESULT.CARDINALITY` | 字符串、区域、handle 或 label 数量不一致 |
| `BARCODE.RESULT.RAW_UNAVAILABLE` | 后端无 raw byte；不得从字符串回编码 |
| `BARCODE.RESULT.QUALITY_UNAVAILABLE` | 质量结果名/条件不可得；解码内容可单独保留 |
| `BARCODE.BUDGET.EXCEEDED` | 预算到达；不降级为成功 |
| `BARCODE.CANCEL.REQUESTED` / `BARCODE.CANCEL.DRAINING` | 已请求取消/仍在排空；调用方等待 `ResourcesReleased`，超出排空窗口则查询原 operation 并保持 `DrainUnknown` |
| `BARCODE.RESOURCE.OOM` / `BARCODE.RESOURCE.LEAK` | 内存或清理失败；释放确认后才可为 `ResourceError`，否则保持 `DrainUnknown` 并隔离适配器实例 |
| `BARCODE.WORKER.STARTUP` / `BARCODE.WORKER.PROTOCOL` / `BARCODE.WORKER.TRANSPORT` | 发布hash/Job/握手失败、非法版本/序号/消息、断pipe/短读；仅收集安全证据，停止原worker，释放确认后AdapterError |
| `BARCODE.WORKER.OUTPUT_INTEGRITY` | 输出blob或结构校验失败；模型bytes为ModelIntegrityFailed，其它结构为InvalidOutputRejected；不得接纳资产 |
| `BARCODE.WORKER.EXIT_UNKNOWN` | process退出/Job零活动进程/host lease归还任一未确认；非终态DrainUnknown，查原operation |
| `BARCODE.TRAIN.NO_SAMPLE` | 训练样本无成功读出；空结果不抛异常也必须显式记录，资源释放确认后训练 Outcome=NoSuccessfulSample（不属于 decode 终态） |
| `BARCODE.TRAIN.FALSE_DECODE` | 训练样本出现误读；本 pass 停止、后续样本 NotRun；不更新生产模型 |
| `BARCODE.TRAIN.TIMEOUT_UNSUPPORTED` | 训练期间 timeout 被忽略/禁用，当前宿主无法硬中断；生产恢复拒绝 |
| `BARCODE.TRAIN.VALIDATION_FAILED` | 训练后参数读回、模型 hash 或 Golden 验证失败；销毁副本并回退 |
| `BARCODE.TRAIN.HARD_STOP_UNKNOWN` | Training Adapter worker/native 未能在 drain window 内确认停止时隔离 worker/模型，在进程退出和租约/句柄归还未确认前保持非终态 `DrainUnknown` |
| `BARCODE.EPOCH.STALE` | 迟到结果属于旧模型/上下文；只记录，不覆盖新结果 |
| `BARCODE.UNKNOWN` | 作用范围未知；转人工/诊断，禁止盲重试 |

错误包含 `RequestId`、`AttemptId`、`modelEpoch`、阶段、是否可重试、已复制结果数和资源状态。禁止把异常消息直接展示给操作员；UI 由宿主根据本地化资源映射简洁提示。

对已接纳 operation，模型、后端、结果格式和预算错误只有在 `ResourcesReleased=true` 后才能封存为对应 `AdapterError`、`ResultFormatError` 或 `BudgetExceeded` 等终态；释放未确认时一律保持非终态 `DrainUnknown`，错误码与已复制观察继续保留。预检输入/参数/容量错误仍走接纳前 `BarcodeRequestRejected` 短路径。

### 5.3 多原因归约、完整性与封存时点

所有原因原样保留在 Issues/训练样本/DiagnosticIds，不因只有一个 terminal enum 丢掉其它原因。每个 operation 有受同步保护的原因集合；已接纳后首个取消或 deadline 在锁内记录停止意图，停止新增工作。结果归约只在真实资源释放后封存一次；ResourcesReleased 前遇到未知 native/worker/lease 状态均优先是非终态 DrainUnknown，TerminalState/Outcome/TerminalSequence/Digest 为空。DrainUnknown 不是成功、取消或失败 terminal，不参与下列排序。接纳前拒绝也不参与。

| 路线 | 已确认释放后的优先级（左侧高于右侧） |
|---|---|
| Decode | ResourceError > ResultFormatError > AdapterError > BudgetExceeded > Cancelled > CompletedWithReads > CompletedWithCandidates > CompletedNoRead |
| Training | ResourceError > FalseDecodeRejected > InvalidOutputRejected > ModelIntegrityFailed > ParameterReadbackFailed > AdapterError > BudgetExceeded > Cancelled > GoldenValidationFailed > NoSuccessfulSample > CompletedWithCandidate / CompletedWithAdvice |

ResourceError 是实际分配失败、释放曾报错且经恢复证明已释放等事实；仅 MaxNativeBytes 等预算达到是 BudgetExceeded，不当作 OOM。模型创建/配置/后验 provider 输入异常是 AdapterError，错 tuple/ID/摘要/原始返回结构是 ResultFormatError。质量条件不足/不适用/不支持/质量族 FormatError 只附质量 Issues，不抹掉已经解码的读数，也不提升为 decode ResultFormatError（仅质量族结构受影响）；若错长破坏观察索引绑定则是 ResultFormatError。Decode 不接收真值/期待串，不能标“误读终态”；已解码但宿主真值不符是宿主独立决定，原 decode terminal 不被改写。训练样本/fresh read/Golden 有真值不符都记录 FalseDecodeRejected；格式非法用 InvalidOutputRejected，不把误读降为普通 NoRead/Golden 失败。GoldenValidationFailed 表示缺预期读数、额外码数量或资格条件未完整，不替代已发现 FalseDecode。

Cancelled 的事实是停止意图在执行证据封存之前被接受且确实阻止该 operation 后续执行；仅 observer/wait token 取消或执行证据已经封存后才到达的 UI 取消不改变已固定的执行分类；CancelOperationAsync/CancelTrainingAsync 此时返回 ExecutionSealed（资源仍可能排空中），不伪造 AlreadyTerminal、不发 CancellationRequested、不再abort。已发布终态才 AlreadyTerminal；若释放未知则 DrainUnknown 优先。Core 在最后一次 attempt 复制完成（或失败停止）时，锁内固定执行原因/停止规则，记录 ResultReady；后续清理可新增 ResourceError，但迟到取消/deadline 只记录诊断，不把早已完整完成的 find 改成 Cancelled/BudgetExceeded。执行截止点到达且尚未封存时记录 BudgetExceeded；后台停止的 native abort 响应只确认既有 cancel/deadline 原因，不新增 AdapterError。无宿主停止意图的 backend aborted 为 AdapterError。若取消和 deadline 都在执行封存前发生，BudgetExceeded 优先；已出现格式错误又取消为 ResultFormatError；读出后遇到 OOM且最终释放确认为 ResourceError，读数仍保留。

`IsComplete` 的唯一语义是“批准计划按停止规则结束且所需解码/候选证据完整复制”，不是生产 PASS，也不是整图真实全集。满足：所有已执行 attempt 结果合法且完整、剩余项只因已批准 AfterAnyDecodedObservation 跳过并有 StoppedByPlan 汇总、所有输出范围/索引有效、无 cancel/deadline/backend/预算/结构/资源故障。CandidateCompleteness=Unknown/Incomplete、域外结果、内部候选/数量停止上限均令 IsComplete=false；单独 NotRequested/MissingCondition/Unsupported 质量状态不改 decode IsComplete，Quality 自己表示完整性。正常完整 NoRead 可 true；“有读数但后项超时”是 BudgetExceeded+IsComplete=false；先固定完整结果、后清理 ResourceError 也须将最终 Result.IsComplete=false，并给新 ResultReady 修订：同 operation ResultRevision 为本 operation 十进制序号字符串，从 "1" 到可选 "2"，严格递增，终态 ResultSequence 指向最后修订，旧已复制快照保持原样。最多一次执行 ResultReady 加一次清理故障修订；恢复释放不新增结果，关键事件预留加 1。宿主必须等待终态并以对应 ResultSequence 的完整 Result 提交，早期 ResultReady 不能先当最终事实。

训练 CandidateRegisterable 只有 CompletedWithCandidate 且 §3.3A 全条件齐备；其它 outcome（含取消/预算/任何失败）均 false、CandidateAsset=null。已经安全复制的 Before/After、sample、fresh read 与质量证据保留，不能因最终取消清空。NoSuccessfulSample 在本合同还包含 pass 遇到 NoRead 被停止的候选失败：即使此前有成功样本仍不允许部分候选冒充整组训练通过，每个未执行样本明确 NotRun。训练 fresh read 为零条时 GoldenValidationFailed（成功训练仍未产生预期读数），不是 CompletedWithAdvice。

合成断言：find 错长与 cancel 并发且释放成功→ResultFormatError；train 发现误读与 deadline 并发→FalseDecodeRejected；两者资源未释放→DrainUnknown、无终态。native 已返回/清理失败但隔离未证明归还→DrainUnknown；恢复后清理曾失败→ResourceError。执行完成/ResultReady 后收到 cancel、正常清理→保留 Completed*；早期读数/质量仍可见，终态前不能触发注册或身份提交。多线程竞争以锁内执行封存/停止意图序号为可判定先后，不依墙钟猜测。

## 6. 处理流程和资源生命周期

1. **冻结请求**：复制参数快照、码制白名单、质量标准、尝试计划、预算和语言无关的诊断标签。
2. **校验并获取输入 lease**：验证图像引用、像素格式、域完整性、坐标链和预算整数溢出；每项通过冻结请求中的 `InputProvider.AcquireAsync(request.Input, attempt.Domain, token)` 获取 `IBarcodeInputLease`，不按 `FrameId` 另行查找，也不修改原图。接纳前失败不创建 lease。
3. **租用模型**：按后端版本、码制、特定参数、预处理、质量/诊断选项和资产修订建立隔离键；同一可变模型同一时刻只允许一个 Owner 写入。
4. **有限搜索**：优先已知码制和完整 ROI；增强、极性、尺度或备用路线必须来自冻结计划，并为每项记录新输入/派生来源。
5. **复制证据**：在结果租约有效期间按实际返回基数复制 strings、raw/ECI、码制、方向、几何、候选和诊断；2D opaque handle 不按数值排序，1D tuple 与 region 按同一返回索引绑定。
6. **读取质量**：只在标准、版本、像素/静区/成像条件满足时查询批准结果；保存原 label、值类型和特殊值。
7. **结束与清理**：停止新消费者→等待调用/abort 排空→复制允许的诊断→适配器确认 `Drained`→释放结果对象/派生图→适配器归还健康模型或清理实例并确认 AdapterResourcesReleased→Core 最后释放输入 lease。Core 不向外暴露 native handle；任一路径无法确认排空或 lease 归还都保持 `DrainUnknown` 并隔离。

取消、超时和异常均走同一清理路径。HALCON 26.05 手册中 timeout/abort 的返回状态须由适配器映射；abort 通过 cv2 的 set_*_param(..., abort, ...) 表达停止意图，是否退出以原调用真实返回和手册 aborted 结果确认，不把 abort 请求返回当作调用已结束；类型歧义只查公共签名，不猜 P/Invoke。Core v0.2 不执行训练或自动调参；Training Adapter 必须按第 3.3A 的隔离 worker、硬中断和排空契约单独准入，不能由调用方 Profile 绕过。

排空是一个可观测的子状态机：`Running → CancellationRequested/DeadlineReached → Draining → ResultsCopiedOrAbandoned → Drained → ResourcesReleased → Terminal`。`Draining` 期间禁止 clear model、归还图像租约或开始同一模型的新请求；若 native 未确认退出，保持非终态 `DrainUnknown`，而不是发布 `Cancelled`。排空超过宿主允许的关闭窗口时，隔离整个适配器实例并保留诊断，不能强制释放仍被 native 使用的对象。模块实例继续回答原 operation 的快照和事件续读；超出实例生命周期的查询返回 `Unknown`，由宿主执行隔离恢复，不得用新 RequestId 重试来掩盖旧操作。

线程规则：同一 reader 的账本/接纳/取消/查询支持并发且同步保护；不向请求共享可变结果状态；每个并行请求使用独立适配器租约和参数快照。宿主可从 UI 线程发起异步请求；Core/适配器不得在 UI Dispatcher 执行 HALCON/native 工作，也不得捕获宿主的 `SynchronizationContext`。进度和事件以不可变载荷异步交付，UI 展示由宿主自行投递到 Dispatcher。模型切换采用新 `modelEpoch`，旧 epoch 排空后才释放；结果/事件带 epoch 防止覆盖新请求。

## 7. 适配器实现要求

### 7.1 HALCON/AsunImage 适配器

- 通过 `ImageLibDotNet.cv2` 调用 26.05 目标算子；仅实际 C# 类型/重载/封送歧义查公共签名，用户确定的算子覆盖和依赖直接使用。
- `ExecuteAttemptAsync` 接收 Core 持有的 `IBarcodeInputLease`，只读访问其像素/ROI，不得另行取图。
- 1D 路线使用 `create_bar_code_model`/`find_bar_code` 及对应 `get_bar_code_result`/`get_bar_code_object`；2D 路线使用 `create_data_code_2d_model`/`find_data_code_2d` 及对应 results/objects。手册算子名称不直接暴露给 Core。
- 适配器先查询可用参数/结果名，返回类型按手册与实际 tuple 验证，建立能力目录；查询结果不作为本次候选已存在的证明。
- 适配器逐项核对成功 region、字符串、handle、候选和质量 tuple 的基数；错长立即返回 `BARCODE.RESULT.CARDINALITY`。
- 输入图像/ROI 只通过 Core 传入的 `IBarcodeInputLease` 只读借用；适配器不得释放、保存或转交 lease，不得改变调用方帧、全局系统字典、灯光或设备状态。Core 仅在 native 调用确认 `Drained` 后最后释放 lease。
- native 异常保留后端错误号和阶段，但不泄漏句柄值或敏感原文；清理失败使实例不健康，不能放回池。

`ExecuteAttemptAsync` 的异步等待须有界：native 在预算内退出时，adapter 在同一模型租约内完成结果/质量查询并复制，再返回 NativeCallDrained=true；若 native 尚未退出且调用观察窗口结束，则返回空或已安全复制的部分观察、Incomplete 候选和 timeout/cancel 问题，NativeCallDrained=false，后台执行单元仍持有原租约。不得将运行中的 native 模型并发查询或释放，也不得把未返回的 native 调用栈留在 UI 线程。返回后 Core 只能 DrainAsync 原 RequestId；adapter 不再给该次尝试追加观察，迟到 native 输出作诊断后弃置，不能追加解码观察；清理故障的最终完整性修订仅按 §5.3 执行。DrainAsync 使用 Profile 的独立 drain deadline；token 只停止等待，不释放正在使用的资源。后续调用仍查询同一内部 operation，不重新执行 find；最终 native 返回后由 adapter 清理再返回 NativeCallDrained=true/AdapterResourcesReleased=true。Core 的输入 lease 仍最后归还。该规则允许有限回执与迟到资源恢复，不把“异步返回”误认成 native 已停止。

能力发现由宿主显式调用 GetCapabilitiesAsync，Core 执行时再次读取 adapter 的冻结能力快照；不使用全局缓存或猜码制。Validate 只验证本页纯语法/交叉条件；adapter-only 能力/真实像素错误若接纳后才发现，结果附稳定问题并经正常排空链到 AdapterError/ResultFormatError，不伪造接纳前拒绝。非 native 的 Simulator 遵守同一有限回执/账本语义。

### 7.2 离线回放适配器

回放适配器只读取经过授权的图像、参数和已保存后端返回快照；能验证契约映射、取消/排空和结果投影，但不能冒充 HALCON 识别率、质量资格或实机性能。回放输出必须标记 `BackendEvidence=Replay`，不得写入生产事实。

首版公开构造冻结如下，位于 Core 的 `Asun.Modules.Barcode` 命名空间；不是另一种视觉算法或新的文件格式。持久化/解密/资产权限由宿主完成，constructor 只接受已解码的完整值快照，不读取路径/网络/数据库。以下为声明摘录，接口实现体省略，未编译。

```csharp
public sealed record BarcodeReplayCase(BarcodeRequestSnapshot Request,
    BarcodeAttempt Attempt, BarcodeAdapterAttempt AttemptResult);
public sealed class ReplayDecoderAdapter : IBarcodeDecoderAdapter
{
    public ReplayDecoderAdapter(IReadOnlyList<BarcodeReplayCase> cases,
        int maxCases, long maxRetainedBytes);
    // IBarcodeDecoderAdapter members follow §3, no additional Execute/Train method.
}
```

构造预检 cases 非空、maxCases 为 1..65536、maxRetainedBytes 为正，cases.Count≤maxCases；checked 计算完整请求/观察/候选/raw/文本/质量/几何快照的保留载荷和索引容量再深复制，超过限额抛 ArgumentException，不先复制后报容量。字节、字符串与数组载荷按 §3 预算规则计费，CLR 对象头另列宿主基线，不假称精确 RSS。每例键为 `(Request.RequestId,Attempt.AttemptId)`，不可重复；Attempt 必须逐字段等于 Request.AttemptPlan 对应项，全部结果通过 §3/4.1 的结构/ID/Unicode/摘要可编码验证。只接受 NativeCallDrained=true 的已完成快照；不把尚未封存/待资源释放的历史 operation 当作当前活动 native。构造无 Acquire、无后台工作，非法输入同步拒绝。

能力固定 AdapterRevision=`barcode-replay-v1`、Threading=IndependentWorkers、MaxConcurrentCalls=1、MaxQueuedCalls=1，SupportedSymbologies 为 catalog 中精确码制的去重 ordinal 列表，仅表示可回放这些 case，不是已识别该码制。执行核原 RequestId/AttemptId、去掉 provider 的整个 RequestSnapshot 逐字段等价（包括原像素hash/坐标/完整域/参数/model asset/hash/预算/编码/质量/TraceContext），并核实际传入 lease；不只比较文字/帧名，不选“最近”的 case。无匹配或内容失配返回空、Incomplete/AttemptEnd.Error 与 BARCODE.PARAM.UNSUPPORTED，不能另启 HALCON 或猜读数。

匹配后独立复制已保存的合法记录，保持原观察/候选顺序和关联 ID；AdapterEvidence.Evidence=Replay、AdapterRevision=barcode-replay-v1，BackendVersion/AsunImageVersion 保留原记录的来源版本，Raw.Available 时 Source=Replay。ElapsedMs 记录本次回放实际时间、PeakNativeBytes=0、DerivedPixels=0；历史 HALCON 耗时/水位仅留宿主保存原件，不投影为本次性能。原输入、模型 epoch、raw/几何/质量值和缺失状态不改，不能把源 Unsupported raw 升级可用。Core 根据同一 request 生成自己的 RequestSnapshot/事件/回执，Replay 不伪造过去的 Core 终态或资源事实。

每个 catalog 键至多登记一次原执行 Task；并发同键仅观察同一原 Task，冲突拒绝，不重复复制。已接纳工作总数受 catalog 和 maxRetainedBytes 上限；结果复制也计原 request 结果预算。执行/取消在 Core 的原 deadline 内观察，期间取消不改变已封存快照；DrainAsync 只等本次记录复制 Task 实际退出，成功才 NativeCallDrained/AdapterResourcesReleased=true，没有 native 资源也不能把尚在读 lease 的 managed 工作算已归还。输入 lease 仍由 Core 释放。其它未执行键查询为无活动资源，不伪造历史硬件 drain。

§12 的回放用例沿 Core.Tests 同一入口验证完整键匹配、改一个像素hash/ROI/参数/model hash拒绝、未知case不fallback、NUL/重复码/未知质量标签原样保留、Replay标记和独立bytes、取消/原Task/有限Drain。它不替代 Halcon.Tests、Training.Tests 或真实 Viewer 验证；该增量的规格状态单列在附录B.2，不扩大此前 Core/Simulator 接收范围。

### 7.3 可选其他后端

ZXing-C++ 等只作失败边界、字节/ECI层次和测试对照；当前不作为生产运行依赖。若未来获批，适配器必须保持同一 `RawPayload`/状态契约，记录后端版本、许可证、输入差异和互认限制，不得把其纠错等级映射为 ISO 质量等级。

### 7.4 具体算法路线、备用、训练和恢复

| 路线 | 输入与参数来源 | 处理顺序 | 输出 | 触发的备用/恢复 | 可判定验收 |
|---|---|---|---|---|---|
| 1D 已知码制 | 原始 Gray8 帧/完整搜索域；`SymbologyAllowList`、`create_bar_code_model` 参数快照、26.05 `query_bar_code_params` 能力目录 | 校验域与像素支持 → 租用独占条码模型 → 设置已冻结 generic/specific 参数 → `find_bar_code` → 按同索引复制 region/string → 在结果租约内读取 `get_bar_code_result`（含 `decoded_data`、`aborted`、质量族）及必要 object → 释放 | 每个成功符号的 raw/原文/码制/几何/质量状态；候选和 abort 摘要 | 未读且预算仍足：只执行 `AttemptPlan` 中下一项（例如已批准的极性/尺度/ROI）；不因期待值追加。参数/结果错长隔离模型并返回 `BARCODE.RESULT.CARDINALITY` | 固定 Golden 的 region/string/raw 索引一一对应；`aborted` 与顶层状态一致；预算到达不宣称穷尽 |
| 2D 已知类型 | 原始帧/ROI；一次一个 symbol type；`create_data_code_2d_model` 参数快照及 `query_data_code_2d_params` 结果名目录 | 校验模块尺寸/极性/镜像/静区 → 租用独占模型 → `find_data_code_2d` → 按返回顺序复制 XLD、opaque `ResultHandles`、decoded strings → 用真实 handle 查询 `get_data_code_2d_results`（general 与 candidate-specific 分开）/objects → 释放 | raw/编码标记、handle 关联、候选/未解码统计、质量 tuple 和条件状态 | 未读且计划允许：切换到已批准参数或另一独立模型实例；不可按 handle 数值排序、不可把 `candidate_num` 当全域证明 | 非递增 handle、可变 tuple 和 `aborted/result_num/candidate_num` 反例均保持正确绑定；合法未知 label 映射 Unknown 并保原值，基数/类型非法才是 FormatError |
| 2D 工程宽搜 | 明确标记 `EngineeringExploration`；有限码制集合、较宽搜索参数和更高预算 | 先按优先级逐模型运行，每次独立租约；记录每个模型的输入、候选和终止原因；不启用隐式训练 | 多模型观察集合，`Completeness=Unknown` 除非应用另有覆盖证明 | 只允许调用方在离线/工程工具触发；生产 Profile 必须拒绝宽搜或显式审批 | 同一输入重复运行产生同样的模型顺序和停止条件；结果不得写生产身份 |
| 训练 adapter | §3.3A 固定用途、BaseModel、真值/Golden、FreshReadInput 与隔离预算 | 独立 operation → 有序样本一次 train find → 输出/真值检查 → read-back/退出训练/隔离保存读回 → 一次 fresh read → 离线 Golden → 排空释放 | 独立训练回执保留 Before/After、样本、fresh read、Golden 与资源证据；生产只作临时建议 | 空/非法/误读/读回/Golden 失败停止后续；无硬停能力接纳前拒绝，释放未知 DrainUnknown | 一次 pass；每样本≤1；fresh read≤1；无静默活动模型变更；隔离不冒充释放 |
| 退化图像 | 原始帧和质量前置结果；备用路线需在 `AttemptPlan` 冻结 | 先记录噪声/遮挡/对比不足 → 只运行批准的增强/反相/尺度派生 → 每次派生带输入引用和预算 → 解码 → 质量只对满足原始成像条件的输入计算 | 派生观察与原图观察分开；质量缺条件时 `MissingCondition/Unsupported` | 备用路线耗尽返回 `CompletedNoRead`/`CompletedWithCandidates` 或 `BudgetExceeded`；不得循环直到读到期待值 | 原图质量与增强图读数不会互相覆盖；所有派生尝试可重放 |

参数来源顺序固定为：宿主 Profile → 已发布模型/参数 manifest → 后端 `query_*` 能力与范围 → 请求快照。旧 AsunControl 的 `All` 重试、自动 Train fallback、INI 默认值不属于生产默认策略。模型/参数设置、find、结果复制、质量读取和清理必须处于同一租约；find 正在修改模型状态时禁止并发 set/read/clear。

训练路线必须覆盖：HALCON 26.05 的一次 pass、每样本一次 train-mode `find`、最多一次 fresh read、空结果/false decode 检查、参数 read-back、模型 hash、Golden 验证、隔离临时 epoch、timeout 被忽略时的 worker 硬中断以及 `DrainUnknown` 处理。它们不进入 `BarcodeRequest`、`BarcodeObservation` 或 decoder adapter 事件，而由本节定义的 `IBarcodeTrainingAdapter` 独立 operation 承载；若无法验证停止与排空能力，训练 operation 必须拒绝或进入 `DrainUnknown`，不得创建第二个 operation。

不支持或本轮明确不承诺：未经公开绑定的 raw byte/ECI 还原、任意 GS1 语法/词典校验、未知重叠码物理去重、跨帧自动拼装 Structured Append、自动选择期待字符串、用 ZXing/纠错等级补 ISO 质量、正式 DPM/SEMI/ISO 资格、隐式/循环/无界生产训练和硬件曝光闭环。一次显式 Profile 授权的隔离 NoRead 保底只按上述硬中断条件执行；无法验证停止与排空能力时拒绝。遇到不支持条件返回 `BARCODE.PARAM.UNSUPPORTED` 或对应质量状态，并保留已取得的视觉观察。

### 7.4.1 TrainingTarget 与 HALCON 26.05 逐项调用

以下是 HDevelop 算子实参语义表，不是未经编译的 C# 重载示例。全部经 `ImageLibDotNet.cv2`，顺序、空 tuple、字符串值按表绑定；只有 C# 控制 tuple、pointer/IntPtr、结果对象释放存在类型歧义时查公共签名，不扫描内部或检查是否包含。使用独占隔离模型，只在 find 真正返回后 query/get/set/serialize/clear，唯一例外为手册允许的跨线程 abort。

| 阶段 | ElementSize + 1D | ModuleSize + 2D（含 PDF417） |
|---|---|---|
| 从 BaseModel 建 candidate | `create_serialized_item_ptr(Pointer,Size,'true',Item)`；`deserialize_bar_code_model(Item,Model)`；clear Item；在无find运行时 `set_bar_code_param(Model,'train','~all')` 明确关闭train（不改数值）；不能把get(train)的已训练名字当作训练仍在运行 | 同样创建 Item；`deserialize_data_code_2d_model(Item,Model)`；clear Item；`get_data_code_2d_param(Model,'symbol_type',Type)` 必须精确等于 request.Symbology |
| 配置/Before | 先读取 BaseParameters 对应 general/specific 当前值，匹配 manifest 后才设置本次固定非训练参数；`query_bar_code_params(Model,'general',NamesGen)` 与 `...,'specific',NamesSpec` 分组；general 用 `get_bar_code_param(Model,NamesGen,Values)`，specific 用 `get_bar_code_param_specific(Model,Symbology,NamesSpec,Values)`。仅本页 parameter key 对应项进入 Before，不靠 query 返回顺序绑定 | `get_data_code_2d_param(Model,Names,Values)`，Names 来自本页已设置 key 的精确名称，包括一般码 module_size_min/max 或 PDF417 module_width_min/max、module_aspect_min/max；比较 BaseParameters；stop_after_result_num 是 find 选项，不经 get_data_code_2d_param 查询，按已冻结请求值记录，其他固定设置后读回 Before；After.Parameters.Asset=null |
| 开启训练 | `set_bar_code_param(Model,['train','train'],['element_size_min','element_size_max'])` 恰一次；不使用 all，不重复设置 target 参数 | 不调用 set(train)；每次 find 的 GenParamName=['train']、GenParamValue=['module_size']。PDF417 同一 module_size train 目标包含 width/aspect，禁止传不存在的泛化 module_size 参数 |
| 固定样本一次 find | 对完整 Gray8 创建域 `reduce_domain`；`find_bar_code(ImageReduced,Regions,Model,Symbology,Strings)`；检查 Regions/Strings 基数、type/raw/真值；不能靠 stop_after_result_num=1 掩盖多码训练，BaseParameters 中该参数必须显式=0，先读回并核对，训练前不静默改值，并在 Samples 域只允许受控单目标 | `find_data_code_2d(ImageReduced,XLDs,Model,['train'],['module_size'],Handles,Strings)`；训练按手册通常只读一个样本目标，故固定单目标 ROI；XLD/handle/string 恰一且码制/raw/真值有效才能进入下一样本。多目标训练集不能使用此合同 |
| 训练参数 After | `query_bar_code_params(Model,'trained_general',Names)`→`get_bar_code_param`；`...,'trained_specific',Names`→`get_bar_code_param_specific(Model,Symbology,Names,Values)`。Before也查询 trained_general/trained_specific 并保留到同名数组；After按名称绑定。当前 ElementSize target 的 element_size_min/max 是 general（手册示例明确）；两目标必须出现在After general，不可新增 target 外 trained 名称。Base的历史 trained 名称允许保留，不能因为存在历史训练就拒绝；但任何历史/非target参数若无法以本页typed Key读取并比较，则当前有限切片不支持该Base资产，接纳后ParameterReadbackFailed，不编造read-back。Before/After Key/type/单位一一映射，TrainingModelEvidence.Parameters.Asset=null，模型归其 ModelSha256 引用，不能让After参数还挂旧BaseModel资产 | `get_data_code_2d_param(Model,['module_size_min','module_size_max'],Values)`；PDF417 改为四项 width/aspect；查询其余已配置 key，确认只有允许 target 改变，未训练参数保持。2D TrainedGeneralNames/TrainedSpecificNames固定空数组（不是伪造HALCON查询训练状态）；目标由TrainingProfile.Target及实际参数读回证明。参数未变化仍合法，按 §3.3A 验证行为 |
| 退出训练 | 读回后 `set_bar_code_param(Model,'train','~all')`，以 set 调用成功且后续普通 find 无再次 set(train) 保证退出；get(train) 返回已训练参数名而不是活动训练开关，不能要求其空tuple；不在训练中直接 set 已训练数值，以免重置历史 | 训练只对该次 find 的 train 选项生效；普通后续 find **不传 train**。不使用 default_parameters 重置、不调用 trained='all' 冒充退出（trained 只控制下次训练扩展策略） |
| 保存/读回 | `serialize_bar_code_model(Model,Item)`→`get_serialized_item_ptr(Item,Pointer,Size)`，在 Item 活跃时深复制 Size bytes 并计算 raw SHA-256，clear Item；由复制 bytes 再 create_serialized_item_ptr(...,'true',VerifyItem)→`deserialize_bar_code_model(VerifyItem,VerifyModel)`，clear VerifyItem；Before/After 逐项读回核对，清理训练 Model | 同序 `serialize_data_code_2d_model` / `deserialize_data_code_2d_model`，重新查询 symbol_type 与 target/非 target 全部已配置 key；原 bytes hash 与传输 hash 匹配，不要求新 serialize 产生相同流 |
| fresh read | 对 VerifyModel 固定普通参数，`find_bar_code(FreshImageReduced,Regions,VerifyModel,Symbology,Strings)` 一次，无 train 状态；按同索引 get_bar_code_result(...,index,'decoded_data',...) 及所请求质量族；证据复制后不再调用 fresh read | `find_data_code_2d(FreshImageReduced,XLDs,VerifyModel,['stop_after_result_num'],[批准普通参数值],Handles,Strings)` 一次，禁止 train；所用普通值必须≥1并纳入 read-back快照，不能靠默认值偷换；真实 handle 查询 decoded_data/质量族，禁止按 handle 排序 |
| Golden/清理 | 每个冻结 case 用普通 find 一次，读回快照相同；`clear_bar_code_model` 清理 VerifyModel/任何其它隔离副本，iconic 对象按已批准 AsunImage 公共释放规则归还 | 同样无 train 普通 find；`clear_data_code_2d_model` 清理所有模型。所有 serialized item 以 `clear_serialized_item` 清理，不能把残留 handle 带出 worker |

离线 fresh input 必须有单目标 GroundTruth；普通2D stop_after_result_num 请求值必须≥2且≥所有Golden case预期数量+1，用于可观察额外结果，值仍受候选预算约束；不能恰取预期数量后称没有额外结果。达到该上限统一视为不完整验证并拒绝候选。Golden 是否“无码”的真值来自冻结受控case，不把后端无候选当作物理全集证明。1D训练Sample域内潜在误读风险仍由固定真值和Golden发现，训练前设置之外不在pass中补调参。

序列化 pointer 只在当前 worker 进程使用，大小为正且在 §7.5 限额内，checked 转 int 后分配。输入 bytes 固定/ pin 在 create_serialized_item_ptr(...,'true') 调用期间；Copy=true 成功后 serialized item 自有副本，可解除 pin。get_serialized_item_ptr 不转移所有权，必须在 clear Item 前完成复制；Pointer 从不进入 Core DTO/IPC/日志。失败 finally 按仍已取得的对象逆序归还；不能在 native 未退出时执行 finally clear。1D query_general/specific 本地手册区别是行为证据，不重新检查 wrapper 覆盖。

依据：[query_bar_code_params](../../../halcon算子手册/operators/query_bar_code_params.html)、[get_bar_code_param](../../../halcon算子手册/operators/get_bar_code_param.html)、[get_bar_code_param_specific](../../../halcon算子手册/operators/get_bar_code_param_specific.html)、[set_bar_code_param](../../../halcon算子手册/operators/set_bar_code_param.html)、[find_data_code_2d](../../../halcon算子手册/operators/find_data_code_2d.html)、[get_data_code_2d_param](../../../halcon算子手册/operators/get_data_code_2d_param.html)、[serialize_bar_code_model](../../../halcon算子手册/operators/serialize_bar_code_model.html)、[deserialize_bar_code_model](../../../halcon算子手册/operators/deserialize_bar_code_model.html)、[serialize_data_code_2d_model](../../../halcon算子手册/operators/serialize_data_code_2d_model.html)、[deserialize_data_code_2d_model](../../../halcon算子手册/operators/deserialize_data_code_2d_model.html)、[create_serialized_item_ptr](../../../halcon算子手册/operators/create_serialized_item_ptr.html)、[get_serialized_item_ptr](../../../halcon算子手册/operators/get_serialized_item_ptr.html)、[clear_serialized_item](../../../halcon算子手册/operators/clear_serialized_item.html)。

### 7.5 Training worker IPC v1（工程规格已冻结）

仅适用于 Training/Worker 切片，Core 不直接启动进程。每个已接纳 TrainingRequestId 创建一个 worker 进程/Job/双向本地 pipe，不池化、不跨 operation 复用、不自动重启；worker 不读宿主路径、数据库、配置或设备。adapter 是唯一 owner，worker 只收冻结值和独立 bytes。`BarcodeTrainingAdapter` 位于 Asun.Modules.Barcode.Training，构造固定为 `(BarcodeReaderProfile retentionProfile, BarcodeWorkerHostOptions workerOptions)`；公开 Training API 实现 §3.3A。Options 不进入 Core，其 record 字段如下：

```csharp
public sealed record BarcodeWorkerHostOptions(string WorkerExeAbsolutePath,
    string WorkerExeSha256, string AdapterRevision, string AsunImageVersion,
    string HalconVersion, int MaxConcurrentWorkers,
    BarcodeWorkerIpcLimits Limits);
public sealed record BarcodeWorkerIpcLimits(int MaxJsonBytes, int MaxChunkBytes,
    long MaxModelBytes, long MaxFrameBytes, long MaxInputTotalBytes,
    long MaxOutputTotalBytes, int MaxBlobs, int MaxMessagesPerDirection,
    long MaxJobMemoryBytes, long StartupTimeoutMs, long TransferIdleTimeoutMs,
    long ExitWaitMs);
```

HostOptions 必须绑定宿主发布目录内已存在 exe 绝对路径与 hash，启动前逐字节核对，不接受 request 提供的 executable/path/命令行。工作目录为该发布目录，worker 不主动落盘；native 运行依赖使用宿主已确定 AsunImage/26.05，不安装/下载。环境只传启动必需系统/运行依赖值，不传业务秘密或 payload；URL/网络/跨主机 IPC 不支持。MaxConcurrentWorkers≥1 且不超过 retentionProfile.MaxActiveOperations；不可用容量接纳前拒绝。下列 ceiling 是 v1 协议分配安全上限，不是客户节拍/性能指标；Profile 可以更低但不能调高绕过协议。

| 长度/容量（分配前 checked 校验） | v1 硬 ceiling 与实际取值 |
|---|---|
| 单 JSON / 单 binary chunk | 各 1,048,576 byte；Options 值 1..该上限；总单消息≤32+两个上限；无压缩，禁止压缩炸弹/反序列化类型名称 |
| 单模型 / 单帧 | model≤268,435,456 byte；frame≤67,108,864 byte；Width/Height各1..65,535且乘积不超过frame限额；非零，实际再取相应 request ResourceBudget 剩余值的 min |
| 传输总输入 / 总输出 | input≤536,870,912 byte；output≤67,108,864 byte；包含每个 message header/JSON/blob 的累计 wire byte，0 不允许；输出并受 MaxResultBytes/RawBytes/QualityBytes 约束 |
| 样本/Golden/资产数 | Samples≤256、Golden cases≤256（Profile.MaxSamples 不能超过256），生产保底Samples固定1、blobs≤1,024；fresh input 可与样本相同物理 blob，但所有引用明确；单 worker 一次 request |
| 消息/对象结构 | 每方向≤4,096 messages，Options 正数不超 ceiling；JSON 深度≤32，每个 string UTF-8≤16,384 byte，数组元素≤65,536（语义更小上限优先）；禁止重复键/未知字段 |
| Job 内存 | Options.MaxJobMemoryBytes 必需正且由已采纳软件资源Profile设定，不进行不受Job限制的探测启动；与请求 MaxNativeBytes 分别控制/观测，不能把进程 private bytes 当 native 精确水位 |
| 时间 | StartupTimeoutMs、TransferIdleTimeoutMs、ExitWaitMs 必需1..60,000 ms；各阶段取其与 operation deadline 剩余值的 min。deadline 后 drain/hard-stop/exit/lease 归还总等待不超过 request/retention 较小 DrainWindowMs；没有“默认永不超时” |

**启动与访问控制。** adapter 生成 cryptographic 256-bit nonce、128-bit 随机 pipe suffix，命名 `asun.barcode.training.v1.{adapterPid}.{suffix}`（仅 [a-z0-9.]）；在创建子进程前用 CreateNamedPipeW 建本地双向 byte-mode pipe：openMode=PIPE_ACCESS_DUPLEX|FILE_FLAG_OVERLAPPED|FILE_FLAG_FIRST_PIPE_INSTANCE，pipeMode=PIPE_TYPE_BYTE|PIPE_READMODE_BYTE|PIPE_WAIT|PIPE_REJECT_REMOTE_CLIENTS，nMaxInstances=1，in/out buffer=65,536 byte。SECURITY_ATTRIBUTES 不可继承、DACL 仅当前宿主 logon SID；client权利固定 FILE_READ_DATA/FILE_WRITE_DATA/FILE_READ_ATTRIBUTES/FILE_WRITE_ATTRIBUTES/SYNCHRONIZE，不授予 FILE_CREATE_PIPE_INSTANCE，不使用 Everyone/Anonymous。将 SafePipeHandle 交异步 NamedPipeServerStream/PipeStream 管理一次所有权；不混用默认可远程连接构造与 CurrentUserOnly 冒充完整限制。用 GetNamedPipeClientProcessId/GetNamedPipeServerProcessId 核对客户端 PID=本次 worker PID、服务端 PID=预期 adapter PID，通过 ImpersonateNamedPipeClient/OpenThreadToken 取得 client logon SID后在finally立即RevertToSelf，并核对启动 nonce，不能只凭可猜 pipe 名。无这些能力/核对失败则不 Ready、不开始 native，不降级开放管道。

进程启动固定 Win32 CreateProcessW（绝对 lpApplicationName、正确引用参数、bInheritHandles=false、CREATE_SUSPENDED|CREATE_NO_WINDOW）；为本 operation 建 Job 并设 JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE、JOB_OBJECT_LIMIT_ACTIVE_PROCESS=1 和 JobMemory limit，AssignProcessToJobObject 成功后才 ResumeThread。job 分配/限制设置失败：不 resume，终止 suspended worker并等退出、关闭持有句柄，以 AdapterError 或未确认退出 DrainUnknown 结束；不在 Job 外运行 HALCON。宿主/worker 原生线程/句柄互不传递，worker 不启动子进程。worker 命令行仅 pipe 名/协议 version/预期 adapter PID，nonce 只从已通过 SID/PID 验证的 pipe challenge 传；没有 nonce 不执行 Begin。将这些 Windows 公共 API 实现在 Training 内窄 interop 层，不另造可复用进程框架；签名按官方文档/实施时的 narrow dotnet-pinvoke 技能处理。

**消息帧。** 固定32-byte header，little-endian 只用于传输 framing（不用于内容摘要）：offset 0..3 ASCII BCTW；4 UInt16 Major=1；6 UInt16 Minor=0；8 UInt16 Kind；10 UInt16 Flags=0；12 UInt64 Sequence（每方向从1连续，≤Int64.MaxValue）；20 UInt32 JsonLength；24 UInt32 BlobLength；28 UInt32 Reserved=0。读取恰32 byte 后先校验 magic/version/kind/flags/长度/累计限额，再分配 payload，EOF/短读即 TransportError。后续恰 JsonLength 的 canonical JCS UTF-8 与 BlobLength 原 bytes；除了 Chunk，BlobLength=0。JsonLength>0，每个消息 JSON 顶层恰 `{OperationId,Body}`，OperationId=TrainingRequestId 小写 N（握手阶段用拟定同一 ID）。每个 Kind.Body 闭集如下；Int64/Guid/enum/null/union 编码沿 §4.1，bytes 在 JSON 不直接插 base64，统一 BlobRef，metadata 自身也计入 wire 额度。消息解析不接受 CLR `$type` 动态实例化，union 仅使用本页白名单分支。

| Kind 数值/方向/顺序 | Body 唯一字段与处理 |
|---|---|
| 1 Hello，W→A，首消息 | {Major,Minor,WorkerPid,AdapterPid,WorkerExeSha256,AdapterRevision,AsunImageVersion,HalconVersion}；版本精确一致，本机实际版本/hash读回，不接受“兼容最新” |
| 2 Challenge，A→W | {Nonce}（32 byte lowercase hex64）；W 核 pipe 服务端 PID后保存，不写日志 |
| 3 Ready，W→A | {Nonce} 回显；A核全部版本/PID/SID/nonce才允许上传；不含图像/模型句柄 |
| 4 Begin，A→W，恰一次 | {Request,Blobs,CandidateModelEpoch,Frames}；Request 为完整 BarcodeTrainingRequest 值快照，删 InputProvider（宿主端口，不可序列化），删 SourceDecode.Receipt 全文（A已按§4.1验证），保留 SourceDecode 其余字段；所有 byte 字段替换 BlobRef={BlobId}（null仍null），唯一字符串引用不得增加路径/指针。Blobs为去重描述数组，描述字段 {BlobId,Role,LengthBytes,Sha256}，Role=Model/Frame/Payload，ID 为 b0000..b1023；输入 blobs 以首引用顺序编号（Model先，Samples输入顺序，再FreshRead，再Golden输入顺序，再各真值payload），复用必须原长度/hash相同。Frames为数组，条目恰{Frame,BlobId}，Frame是完整InputFrameRef，按首次输入引用順序；每个Sample/FreshRead/Golden.Input精确匹配一项，FrameId同值而hash/revision/尺寸不同拒绝，未声明/未引用Frame或Blob拒绝 |
| 5 Chunk，双向 | {BlobId,OffsetBytes} + raw blob chunk；只能对应已声明 blob，offset从0连续、chunk>0且≤上限，不允许交错同一 blob/重复/重叠/缺口；一个 blob完成再下一个。接收最终累计长度/hash校验后才能消费，不信任描述 hash |
| 6 InputsComplete，A→W | {InputManifestDigest}，rule=barcode-worker-input-jcs-v1，JCS content 为完整 Begin.Body（包含 BlobRef描述，无nonce/pipe/PID），sha256格式沿§4.1；全部输入完成且匹配后W才进入native |
| 7 InputsVerified，W→A | {InputManifestDigest,InputBlobCount}；确认W持有独立副本，A不转移自己的 lease 所有权。上传过程中也不能借W提前执行 |
| 8 Stage，W→A | {State,SampleId,ModelEpoch,SampleResult}；仅 Preparing/Training/Validating/FreshRead/Draining，可空值显式null；SampleResult为本页TrainingSampleResult。每个样本结果恰一次，阶段每次转换一次，不发送大快照/像素或高频进度；A分配自己的operation事件序号 |
| 9 Cancel，A→W | {ReasonCode} 非空限长；恰一次意图，重复调用在A幂等合并；W控制线程可调用手册允许abort，停止新增sample/Golden，不能先clear；不依赖native线程处理读pipe |
| 10 CancelAccepted，W→A | {NativeExitConfirmed}；false只确认意图，true也不替代最终Drained/进程退出/lease归还；不能作为Terminal |
| 11 ResultManifest，W→A | {Receipt,Blobs,FailureReasons}；Receipt为本页训练回执的执行证据草稿：Acceptance=Accepted、Rejection=null、State=Draining、Outcome=null、ResourcesReleased=false、TerminalSequence=null、CandidateRegisterable=false；CandidateAsset可含离线候选blob供A核验，生产固定null；其余Before/After/sample/fresh/Golden/quality/diagnostics完整。Blobs描述同Begin。FailureReasons 数组精确为 §5.3 已发生的 BarcodeTrainingOutcome 非成功成员（无失败为空），按首次锁内事实记录顺序且无重复；A按事实再归约，不直接采纳worker成功terminal |
| 12 OutputsComplete，W→A | {OutputManifestDigest}，barcode-worker-output-jcs-v1 对ResultManifest.Body完整JCS；全部output chunk已验证、metadata合法后A接收安全证据；无输出blob也须该消息 |
| 13 Drained，W→A | {NativeCallsExited,NativeObjectsReleased,InputCopiesReleased}，必须三true；发出前不再query/find、所有模型/iconic/serialized items clear，W复制的输入bytes已归还（输出blob仍允许待A确认） |
| 14 ResultAccepted，A→W | {OutputManifestDigest}；仅完成接收/hash/格式验证后发送，W清除待确认输出bytes、关闭pipe、正常exit0；不是生产采用/账本ack |
| 15 Fault，W→A | {Code,Stage,DiagnosticId}；无native指针/敏感payload/堆栈全文；只表示执行/协议错误，W清理并尝试Drained后退出非0，A仍必须验证退出与lease归还 |

Training关键事件最坏预留至少 `2×Samples.Count+2×GoldenCases.Count+16`（checked）；W Stage只报告有界阶段/样本，A查询不追加event。候选/输出blob先预留结果与传输容量再复制，不能占用最后唯一terminal记录；若Profile事件/结果容量不足，A在进程启动/Acquire之前拒绝。Begin之后发现超限不截断成功回执，按§5.3结束并保留已复制证据。输出ResultManifest元数据超单JSON上限直接作为BudgetExceeded停止，不另造未定义metadata分块协议。

Begin 的 frame传输是 provider lease有效像素按行去padding的紧密Gray8独立bytes，描述 LengthBytes=width×height、hash=Input.PixelSha256。帧/ROI绑定仍在每个 TrainingSampleRef；同hash而尺寸/格式不同不可合并，模型与payload不同Role不可合并。全部sample/fresh/Golden只允许Gray8，各自FrameSha匹配；W pin其已核长度/hash的紧密bytes，仅在 `cv2.gen_image1(Image,'byte',Width,Height,PixelPointer)` 调用期间保持地址有效且不截断64-bit pointer；手册明确HALCON复制矩阵，成功后解除pin，图像留到native退出后按公共释放规则归还；不接受外部HObject/地址。BaseModel 与候选传输为 HALCON serialize_* 输出原bytes，不经文字编码；真值payload用独立Payload blob，含NUL/长度/空payload（空blob仅Payload允许，零长度无Chunk但要校验空SHA256）。Source Receipt 由A验证，不让worker伪造宿主持久事实。所有输入累计在A Acquire/复制前检查额度，W再次独立检查，OOM归ResourceError，不重试。

**完整正常闭环。** A接纳/预留账本→Job内启动/握手→逐一Acquire输入lease并冻结复制（A保留lease ownership及释放清单）→Begin/Chunks/InputsComplete→InputsVerified→单pass/read-back/普通fresh/Golden→ResultManifest/Chunks/OutputsComplete（结果已脱离native）→Drained→A核格式/hash并保存不可变草稿→ResultAccepted→W退出→A以保留的进程句柄等待signaled、GetExitCodeProcess确认exit code、Job Accounting确认ActiveProcesses=0→A释放全部宿主lease/复制缓冲/pipe/job/process/thread句柄→ResourcesReleased→§5.3归约/§4.1生成最终摘要/唯一terminal。每个lease清单有FrameId/租约对象/Acquire成功标记/Dispose完成标记；Acquire失败只处置已经成功取得的项；Dispose异常后只能由该provider明确确认归还，不能假定一次重调Dispose即已成功。A必须保留原operation以便Query/Read恢复。

**超时、取消、故障闭环。** 从接纳起的同一deadline覆盖启动、上传、native、输出验证；连续I/O无进展超过TransferIdleTimeoutMs或非法消息/PID/断pipe是AdapterError，输入/输出模型hash错误为ModelIntegrityFailed、其它输出hash/tuple/消息DTO错误为InvalidOutputRejected；预算超限BudgetExceeded。A先停止新增上传/工作，在pipe可用时发一次Cancel；W有独立控制读线程且不持有native执行锁，尝试abort但不声称训练已停。drain window内未收到真实退出/清理证明或取消后仍在native：A显式TerminateJobObject退出代码0xE0000001，再等待process signaled与Job ActiveProcesses=0。正常退出、非0退出、硬停都必须A finally归还全部已取得lease；仅关闭pipe/收到Drained/TerminateJobObject返回成功都不算释放完成。worker退出证据与宿主lease两门齐备才ResourcesReleased；原执行原因保留，正常cancel硬停为Cancelled/deadline硬停为BudgetExceeded，异常transport先发生则AdapterError，清理错误按§5.3优先。退出或任一Dispose未确认→DrainUnknown，保留Job/process/lease清单与未释放ID，不再次启动worker。后续查询只重查退出/归还，不再次发送Begin/find。A崩溃由KILL_ON_JOB_CLOSE终止worker，跨进程账本归宿主；重启查询原ID为Unknown，不能由新A盲目重跑。

证据与测试必须覆盖：Hello hash错、拒远程/错SID/错PID、短header/错version/长度overflow、重复Begin/Chunk重叠/hash错、上传取消、native不响应abort、Result已到但Drained未到、W退出但host lease失败、读取者取消、A进程崩溃、Job配置失败/句柄回收。独立Host只传本页公开值即可正常执行，只有Training内部依Windows管道/Job；两worker并发用不同Job/pipe/nonce/epoch，各自失败不清理另一项。IPC ceiling/握手规则不是已实测的安全、硬停或性能证明；实现后用真实进程与失败注入验证，不能用Simulator代替。

官方依据：[NamedPipeServerStream](https://learn.microsoft.com/en-us/dotnet/api/system.io.pipes.namedpipeserverstream.-ctor?view=net-10.0)、[Named Pipe Security and Access Rights](https://learn.microsoft.com/en-us/windows/win32/ipc/named-pipe-security-and-access-rights)、[Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects)。另读取 [CreateNamedPipeW](https://learn.microsoft.com/en-us/windows/win32/api/namedpipeapi/nf-namedpipeapi-createnamedpipew)、[GetNamedPipeClientProcessId](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getnamedpipeclientprocessid)、[CreateProcessW](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw)、[TerminateJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject) 的具体参数/限制，以及 [gen_image1](../../../halcon算子手册/operators/gen_image1.html) 的复制/地址生命周期。本轮只读取与缺口有关的语义；Windows窄interop的精确签名按这些API与实施技能核对，不扫描视觉封装。

### 7.6 普通解码与质量结果的确定映射

本节补充 §7.1/7.4 的实施顺序，不改 Core DTO、JCS 投影或已接收的 Core 状态机。以下名称均是 HALCON 26.05 算子实参，经 `ImageLibDotNet.cv2` 调用；不是未经编译的 C# 重载。

1. 在本 attempt 剩余预算内验证独立输入 lease 的尺寸、stride、格式、有效像素 hash 和坐标。Gray8 逐行只复制有效像素到受控紧凑缓冲，按 §7.5 已冻结的 `gen_image1` 复制/短期 pin 路线建本进程 native 图；其它批准格式只走 §3.2.1 的显式转换。ROI 使用 `reduce_domain`，不 crop，不改左上原点。预留源、紧凑副本、派生图和结果复制的并存容量；训练的跨进程复制规则不能被普通 decoder 的同进程路径替代。
2. 独占模型设置完整已冻结参数后执行一次 find。find、结果/质量读取、几何复制均用同一单调递减 deadline；不为每个查询重新计时。find 未退出时只保留 operation/模型/输入关联，走 §7.1 Drain，禁止查询或 clear。晚到 find 输出不新增观察。
3. 按下面的后端关联表构造观察和候选，先核 cardinality/类型，再复制到独立 managed backing；取得一条完整记录才交给 Core。预算不足保留先前完整项及 Incomplete，不截断 bytes、标签或坐标后声称完整。
4. 质量只读取请求的、当前码制适用且原始条件完整的族。标签与值同一 model/find/候选作用域读取并逐项配对，不能缓存另一符号的标签布局。质量错误只影响质量/完整性与对应问题，不抹掉已合法解码内容。
5. 成功、异常和取消均逆序清理实际取得的 native/tuple/派生副本；确认 native 不再读输入后 adapter 才报告 drained，Core 最后归还其输入 lease。adapter 不自行 Dispose Core 的 lease。

| 后端关联 | 唯一读取和顺序 | DTO 映射及拒绝条件 |
|---|---|---|
| 1D 成功符号 | `find_bar_code` 的 Regions/Strings 同序；逐零基索引读取 `get_bar_code_result(Model,i,'decoded_types',...)`、`...,'decoded_data',...`；需要独立符号域时 `get_bar_code_object(...,Model,'all','symbol_regions')` | region/string/type 一一对应；decoded_types 恰一个字符串，decoded_data 每项为 0..255 的整数，原样复制为 bytes，禁止用字符串回编码。不同位置同内容保留不同观察；PharmaCode 的合法双方向不按文本去重 |
| 1D 所有候选 | `get_bar_code_object(...,Model,'all','candidate_regions')`；手册定义 m 个候选中的前 n 个与成功符号同序，后 m−n 个为未解码候选 | 核 m≥n，前 n 个建立对应 ObservationId；后项 State=Undecoded。候选 region 与成功 symbol region 含义不同，分别保留，不用成功域覆盖所有候选。persistence 不满足所需对象读取时不能伪称候选完整 |
| 2D 成功符号 | `find_data_code_2d` 返回的 XLD/ResultHandles/Strings 按原顺序逐项绑定；用每个真实 handle 读 `decoded_data`/`status`，码制来自该独占模型的 symbol_type | handle 只作本次内部查找键，不排序、不转业务 ID、不写日志；raw 按 §2.1 的字符/ECI 证明规则决定 Available 或 Unsupported/Unknown，不一概强转 byte |
| 2D 全部候选 | `get_data_code_2d_results(Model,'all_candidates','handle',...)` 得候选顺序；`all_results`、`all_undecoded`、`all_aborted` 分组核成功/未解/中止关联；每 handle 读取 status 与 `get_data_code_2d_objects(...,Model,handle,'candidate_xld')` | 成功组与 find 的 handles 集合相符但观察顺序仍用 find；候选顺序用 all_candidates；同一 handle 不重复造物理码。不存在 `symbol_xld` 结果名；不把 candidate_xld 冒作已解码成功证据。aborted 项保原 BackendStatus，候选状态 BackendVisible，并按实际 abort 原因标 Incomplete |
| 2D 汇总 | general 的 `result_num/candidate_num/undecoded_num/aborted_num/aborted` 与本次取得的组/输出交叉核对 | 错长/重复 handle/无法关联为 BARCODE.RESULT.CARDINALITY；触及停止上限、discard_undecoded_candidates=yes 或证据族不可用时，不宣称全部候选已复制。后端计数不是物理目标真值 |

几何只用于位置投影，首版固定采用 HALCON 包围区域，不把多条 XLD 临时连接为 polygon。1D 先用 `area_center` 确认单个 symbol/candidate region 非空，再 `smallest_rectangle1` 读取 row1/col1/row2/col2 像素中心，转换为 AxisAlignedRectangle(Origin=(col1−0.5,row1−0.5),Size=(col2−col1+1,row2−row1+1))，标 GeometrySource.BackendRegion。2D 对单候选的 `candidate_xld` 先用 `get_contour_xld` 确认点数>0、Row/Col等长且有限，再 `smallest_rectangle1_xld`，AxisAlignedRectangle 的 Origin=(col1,row1)、Size=(col2−col1,row2−row1)，两边须>0，标 BackendContour。XLD几何已是连续坐标，不照搬region的±0.5和+1。empty region/contour或退化边界不得接受算子默认全零位置；观察几何非法按BARCODE.RESULT.CARDINALITY保问题，不制造 `(0,0)`。

这些 Shape 明示为包围矩形，不称精确符号轮廓；原精细区域/轮廓如保留诊断须有受控引用并计预算，不泄漏native句柄。包围框不是 ROI 内含证明，域外判定仍按 §3.2.1，不以包围框近似相交过滤读数。ROI本身仍保完整原矩形/旋转/多边形，不因显示框路线缩减搜索域。各阶段不改 set_system 的全局空对象行为。

1D `get_bar_code_result(Model,'all','aborted',...)` 恰一个整数：0正常结束，1为timeout，2为显式abort；分别映Completed、BARCODE.BACKEND.TIMEOUT、BARCODE.BACKEND.ABORTED，再按§5.3结合本方已接纳原因与资源轴归约。其它值为结果格式错误，不能默认正常。2D aborted与候选组同样仅描述该次后端搜索，不证明operation已清理。

| 请求标准及固定版本 | 26.05 精确结果族 | 标签与值绑定 |
|---|---|---|
| Iso15416 / `2016` | `quality_isoiec15416`、`quality_isoiec15416_float_grades`、`quality_isoiec15416_values` | 同一有效成功索引读取 `quality_isoiec15416_labels`；三族分别保留 ResultFamily。float_grades 保留一位小数原 real；整数等级不代替 float；raw values 不是等级。需 persistence=1；linear/composite 布局不同，不能假设固定长度 |
| Iso15415 / `2024` | `quality_isoiec15415`、`quality_isoiec15415_values` | 该模型 general 的 `quality_isoiec15415_labels` 对应本候选 grades/values；values 与 grades 同序但不可计算项可为 N/A。适用码制和 persistence 按 §3.2.1，DotCode 不借此评级 |
| Iso29158 / `2025` | `quality_isoiec29158`、`quality_isoiec29158_values` | general 的 `quality_isoiec29158_labels`；限手册支持的 Data Matrix ECC200/Aztec/QR/MicroQR 家族，GS1 变体先绑定对应物理类型资格。不得猜用 `quality_aimdpm_*` 或 `quality_isoiec_tr_29158` |
| SemiT10_0701 / `0701` | `quality_semi_t10_values` | Data Matrix 的 general `quality_semi_t10_labels`；保留原测量值，不由模块计算另一标准总分；标准资格仍由宿主计量链确认 |

上述 StandardRevision 是本模块的固定版本 token，采用该族时精确匹配；不得接受任意描述文字后假称相同版本。请求 ResultFamilies 是上述族的明确有序子集，label 查询由 adapter 内部配套，不把 label tuple 本身当分数；不提供逐模块/逐扫描线/中间质量数组的隐式扩展。请求未支持族返回 Unsupported，不回填另一族。空结果在未成功解码时为 NotApplicable/Incomplete，不能给零等级。

`QualityMetric` 的唯一身份为 `(ResultFamily,TupleIndex,RawLabel)`；MetricKey 只是检索投影，不用它去重。标签保留原字符串；匹配时仅将 ASCII A–Z 转小写并把连续空格/下划线/连字符归成单个下划线，禁止翻译、模糊匹配或删除其它字符。规范 token `overall_quality/overall_grade`→OverallGrade，`decode`→Decode，`contrast`→Contrast，`symbol_contrast`→SymbolContrast，`modulation`→Modulation，`defects`→Defects，`decodability`→Decodability，`axial_nonuniformity`→AxialNonuniformity，`grid_nonuniformity`→GridNonuniformity，`unused_error_correction`→UnusedErrorCorrection，`print_growth`→PrintGrowth；其它均 Unknown 并保原值。linear/composite 分项不能因带 overall 字样混成唯一总分。合法未知标签不是 FormatError；错基数、非标量、非法数值/Unicode 才按 §3/4.1 拒绝。N/A、族特有 −1 和合法负 print growth 按 §3 原规则分别表达。

验收追加至 §12 同一 Halcon.Tests 入口：n=2/m=4 的 1D 候选关联、2D handles 非递增、aborted 与未解分组、labels 多一项、未知合法 label、三个质量标准版本失配、N/A/−1/负值，以及 find 迟到时查询次数=0。这里没有运行 HALCON 或生成 Golden。

依据沿用 §2.1/7.4.1 及本地 [`get_bar_code_object`](../../../halcon算子手册/operators/get_bar_code_object.html)、[`get_data_code_2d_objects`](../../../halcon算子手册/operators/get_data_code_2d_objects.html)、[`get_bar_code_result`](../../../halcon算子手册/operators/get_bar_code_result.html)、[`get_data_code_2d_results`](../../../halcon算子手册/operators/get_data_code_2d_results.html)、[`area_center`](../../../halcon算子手册/operators/area_center.html)、[`smallest_rectangle1`](../../../halcon算子手册/operators/smallest_rectangle1.html)、[`get_contour_xld`](../../../halcon算子手册/operators/get_contour_xld.html)、[`smallest_rectangle1_xld`](../../../halcon算子手册/operators/smallest_rectangle1_xld.html)；2026-10-12 定向读取结果族、标签、候选顺序、几何和标准版次，不重复审查 wrapper 算子覆盖。

### 7.7 参数建议的唯一闭环

当前自动参数能力只由 §3.3A/7.4.1 的 TrainingTarget 承载：1D ElementSize、2D ModuleSize（PDF417 为 width/aspect）。不另启用一条隐藏搜索器，不按期待字符串挑选参数。宿主离线调用或原完整 NoRead 的一次显式授权保底，均使用独立 TrainingRequestId 和有限 worker；decoder 事件不混入训练阶段。

建议就是训练回执的 Before/After 差异及 FreshRead/Golden 证据，不新增第二套 recommendation DTO/事实库。UI 按 typed key 展示旧值、新值、单位、来源样本/ROI/hash、源 epoch、候选 epoch、后端/适配器版本、目标、用途、质量条件和验证状态；未知原因显示“未验证”，不编造置信分数。模型 bytes 的 hash 与参数 JCS hash 分别保留，不能互换。

离线候选只有 §3.3A 全部资格成立才可由原模型 Owner 显式注册；注册入口不在 barcode 内。Owner 注册前重新核源 epoch、原 BaseModel hash、Profile/授权/样本/Golden 修订仍与本次回执一致；已过期时拒绝采用，不能自动 rebase 或再训练。参数无变化按 §3.3A 保留原合法回执；byte-identical 且行为相同不要求发布新修订。ProductionNoReadFallback 永远只给建议，临时资产销毁、CandidateAsset=null、ActivityModelChanged=false，原 NoRead 不改写。

验收使用同一 Training.Tests：无授权无 worker；两个不同 TrainingRequestId 竞争同源 NoRead 仅一次接纳；同 ID 查询不重 train；stale 源 epoch 不采用；no-op 不自动发布；取消/硬停/释放未知不形成可注册建议。跨实例“一次保底”去重账与最终采用仍由宿主策略/模型 Owner 持有，模块不暗建持久库。

### 7.8 HALCON Model Profile v0.1：逐码制配置与复合证据（BC-D1）

本节关闭 BC-D1 的软件定义欠账。**不修改已接收 Core API v0.2 的 ModelParameterKey、BarcodeRequest、BarcodeObservation、事件、状态或 barcode-*-jcs-v1。** 新增的是可选的 Model Profile v0.1 和 Supplemental Evidence v0.1；它们明确选用 HALCON26.05，独立随 HALCON 包/可选 Core 扩展发布，不把新能力冒作旧 Core 已接收范围。原少量 typed Key 仍用于通用 decode/训练目标；表外码制参数在准备阶段冻结进模型资产及完整公开 Profile，生产只加载同资产和核值，不在 find 中补猜。

#### 7.8.1 有界值、准备入口和默认来源

以下目标声明的值类型放在 Core 的 `Asun.Modules.Barcode.Extensions`；只依赖 Core/BCL，不含 native/WPF/数据库。HALCON 服务类位于 `Asun.Modules.Barcode.Halcon`。声明摘录省略实现体，未编译。

```csharp
public abstract record NativeParameterAtom
{
    private NativeParameterAtom() { }
    public sealed record Integer(long Value) : NativeParameterAtom;
    public sealed record Real(double Value) : NativeParameterAtom;
    public sealed record Text(string Value) : NativeParameterAtom;
}
public enum NativeParameterScope { General, Symbology, FindOption, TrainingHistory }
public sealed record FrozenNativeParameter(NativeParameterScope Scope, string Name,
    IReadOnlyList<NativeParameterAtom> Values);
public enum CheckCharacterPolicy { EngineDefault, Absent, Present, Preserved }
public enum CompositeMode { None, CcAB }
public enum QuietZonePolicy { EngineDefault, Disabled, Standard, Tolerant, Modules }
public sealed record OneDTypeSettings(CheckCharacterPolicy CheckCharacter,
    CompositeMode Composite, int MinCodeLength, int MaxCodeLength,
    int MinIdenticalScanlines, bool ElementSizeVariable, bool MajorityVoting,
    double OrientationRadians, QuietZonePolicy QuietZone, int? QuietZoneModules,
    bool StrictStartStop);
public enum DataMatrixShape { Any, Square, Rectangle }
public abstract record TwoDSymbolSettings
{
    private TwoDSymbolSettings() { }
    public sealed record DataMatrix(int RowsMin,int RowsMax,int ColsMin,int ColsMax,
        DataMatrixShape Shape) : TwoDSymbolSettings;
    public sealed record Qr(int VersionMin,int VersionMax) : TwoDSymbolSettings;
    public sealed record MicroQr(int VersionMin,int VersionMax) : TwoDSymbolSettings;
    public sealed record Pdf417(int RowsMin,int RowsMax,int ColsMin,int ColsMax) : TwoDSymbolSettings;
    public sealed record Aztec(int SizeMin,int SizeMax) : TwoDSymbolSettings;
    public sealed record DotCode(int RowsMin,int RowsMax,int ColsMin,int ColsMax) : TwoDSymbolSettings;
}
public sealed record BarcodeModelProfile(string ContractVersion,string Revision,
    string Symbology,string BackendVersion,ModelParameters CoreParameters,
    OneDTypeSettings? OneD,TwoDSymbolSettings? TwoD,int? ContrastMin,
    IReadOnlyList<FrozenNativeParameter> FrozenParameters,ModelAsset Asset,
    string ProfileDigest);
public sealed record BarcodeModelPreparationRequest(Guid RequestId,string Revision,
    string Symbology,ModelParameters CoreParameters,OneDTypeSettings? OneD,
    TwoDSymbolSettings? TwoD,int? ContrastMin,ResourceBudget Budget);
public sealed record BarcodeModelPreparationReceipt(Guid RequestId,
    BarcodeAcceptanceState Acceptance,BarcodeModelProfile? Profile,
    bool ResourcesReleased,IReadOnlyList<BarcodeIssue> Issues);
public sealed class BarcodeHalconModelPreparation
{
    public BarcodeHalconModelPreparation(BarcodeReaderProfile retentionProfile);
    public Task<BarcodeModelPreparationReceipt> PrepareAsync(
        BarcodeModelPreparationRequest request,CancellationToken operationToken=default,
        CancellationToken waitToken=default);
    public Task<BarcodeModelPreparationReceipt?> QueryAsync(Guid requestId,
        CancellationToken waitToken=default);
    public Task<BarcodeAcknowledgeReceipt> AcknowledgeAsync(Guid requestId,
        CancellationToken waitToken=default);
    public Task<BarcodeCloseReceipt> CloseAsync(CancellationToken waitToken=default);
}
```

Profile.ContractVersion 精确 `barcode-halcon-model-profile/1`，BackendVersion 精确 HALCON `26.05`，Revision为宿主给的非空版本（UTF-8≤128）；准备RequestId非空。Prepare不读取图像、不训练、不获取provider、不注册/覆盖生产模型；它只在本模块独占串行native执行单元新建/设置/读回/序列化模型。retentionProfile沿§4已有正容量/并发/事件与保留/关闭预算，至少预留一个独立cleanup槽；prepare原Task、模型、serialized item及bytes先登记后操作。重复同ID/同完整字段共享原任务和记录，异内容拒绝；wait取消仅停止等待，operation取消关后续工作并清理。native/set/serialize未真实退出时有限回执Profile=null、ResourcesReleased=false并保原operation，Query只观察原Task，不再次Prepare。只有所有native/item/复制工作退出才可返回Profile或终态失败；ack前调用方保存完整Profile/Asset，未释放不得ack；准备ack返回BarcodeAcknowledgeReceipt.ConfirmedTerminalSequence=null（准备不发Core事件），同ID保已确认墓碑，不造Core terminalSequence。Close只有限观察同根关闭链，不在task中等自身，未确认时继续留账。这个纯配置路线不执行find/train，无训练硬停或IPC新增模式；native调用违约永久不返只能保持未知，不能在该线程外clear。

默认来源唯一为：**准备时在26.05新模型读出的标准基线→宿主本请求显式值→全部读回/冻结→序列化及独立反序列化读回**。1D `create_bar_code_model([],[],M)`；2D `create_data_code_2d_model(精确Symbology,['default_parameters'],['standard_recognition'],M)`，禁止增强/最大模式的隐式fallback。本节参数具有明确constructor字段，非null必填；EngineDefault只允许CheckCharacter/QuietZone，在Prepare读出精确实际值后成为FrozenParameters，生产没有EngineDefault分支。CoreParameters.Asset在Prepare必须null，Values覆盖§3.2.1对该码制适用的完整显式参数；新增资产由Prepare输出，不能假定宿主旧blob完整。输入旧已发布资产直接消费另见本节decoder规则，不通过Prepare重建以免丢历史训练。

所有通用Key、OneD/TwoD及Contrast在Prepare前纯值校验；数组/原文/atoms有限且合法JCS。FrozenParameters是只读结果，不是允许调用方任意传 HALCON 参数的dictionary。1D查询general/specific后按**每个名字单独**get（避免train等多值tuple混长），general用get_bar_code_param，specific用get_bar_code_param_specific(M,Symbology,Name)；另以get_bar_code_param(M,'train')单独读取历史名字tuple，记General/train；query_bar_code_params(M,'trained_general')及'trained_specific'返回的名字集合分别记TrainingHistory/trained_general、trained_specific，不把它们当get参数或活动开关。2D query_data_code_2d_params(M,'get_model_params')后逐名get_data_code_2d_param，记General；其'trained' query只列该码制可训练参数、非当前训练历史，不作为After变化或伪造历史字段。2D额外冻结FindOption/stop_after_result_num为Core.StopAfterResultCount的单个Integer；不经get_data_code_2d_param查询，读取模型核对时只比较General，FindOption独立同请求逐值核对。1D不重复添加同名FindOption。query返回的是该类型精确可读全集，排序Ordinal后冻结Scope/Name/完整Values；同名不同scope保留，未知新增名字不被删除，但生产包只接26.05同集合/类型/值。无效/不可读参数拒绝准备，不把它丢弃变“不重要”。每模型≤512参数、每tuple≤512 atoms、总atoms≤8192，Name ASCII 1..128、单Text UTF-8≤4096、完整参数载荷≤1MiB且受request MaxResultBytes；达到上限在分配/复制前拒绝。atom类型/tuple长度是公开形状，Integer/Real不互转，有限double拒负零；序列化模型bytes受MaxRawBytes/MaxNativeBytes和int容器界限。

模型只能由独占lease设置。普通数值先同时设置min/max对，1D的specific字段用set_bar_code_param_specific(M,Symbology,Names,Values)，通用element_size等按其general路由；查读回若引擎发生关联调整，必须与请求全部显式约束一致，否则Prepare失败，不能悄悄采用adjust后的更宽值。1D在准备序列化前显式set train=~all关闭活动训练，历史名字仍原样冻结。2D先设置size/version范围，最后设置DataMatrix Shape，再读回全部范围与shape；冲突失败，不循环set。最后按§7.4.1序列化/独立反序列化核完整参数快照及symbol_type、clear两个模型/item；blob不要求重新serialize产生同hash，实际输出bytes/hash必须一致。Profile.CoreParameters是完整实际通用Values、Revision同Profile.Revision且Asset=输出Asset；其ProfileDigest按下文独立规则绑定表外参数和实际blob；Asset.Revision=请求Revision。

#### 7.8.2 1D逐码制与参数域

每个§2.2的精确1D字符串都使用同一OneDTypeSettings形状，适用性按下表决定，未适用字段必须为中性值（false/0/None/EngineDefault），不靠“HALCON忽略”接受误配置。全部码制保留查询实际默认、get/set/执行/raw/质量/释放的独立资格；software profile冻结不等于码制Golden通过。

| 精确码制组 | 参数与默认来源 / 受支持变化 |
|---|---|
| `2/5 Industrial`、`2/5 Interleaved` | 标准baseline的min_code_length=3、min_identical_scanlines=2；其余类型分别0、0。允许显式长度/一致扫描线值；check_char EngineDefault读为absent，也可Absent/Present/Preserved；不能把这两个码制的默认套给其它类型 |
| `Codabar`、`Code 39` | optional checksum同上；长度/quiet zone/扫描线/方向可配置。Code32不是新物理码制，不在本模块隐式转换Code39业务内容 |
| `Code 93`、`Code 128`、`GS1-128` | checksum按26.05基线读回，Mandatory的Code128/GS1-128禁止Absent/Preserved改强制校验语义，仅EngineDefault或Present；StrictStartStop仅Code128/GS1-128适用，true→low、false→high。其它类型StrictStartStop必须false，不设置该参数 |
| `MSI`、`PharmaCode` | 精确单类型find，不放入auto；check_char仅EngineDefault按模型读回，不移植Code39可选校验法。PharmaCode保双向观察，原码制域不做身份去重 |
| `EAN-8`、`EAN-13`、`UPC-A`、`UPC-E`及各 `Add-On 2` / `Add-On 5` 精确变体 | mandatory checksum按模型实际规则，EngineDefault/Present；附加码仍独立精确CodeType，EngineText有分隔不切字符串制造组件bytes。Composite=None；不把Add-On当GS1 CC-A/B |
| `GS1 DataBar Omnidir`、`Truncated`、`Stacked`、`Stacked Omnidir`、`Limited`、`Expanded`、`Expanded Stacked`（均带完整`GS1 DataBar `前缀） | Composite允许None/CC-A/B；默认None显式设置。check_char只EngineDefault/Present且读回绑定该类型；linkage按下文。Stacked/Stacked Omnidir/Expanded Stacked禁MajorityVoting=true；num_scanlines=0的模型自动数通常20/20/55，其它单行通常10，保0及后端行为，不改成这些常数 |

ElementSizeVariable只有Code128/GS1-128/GS1 DataBar Limited/Expanded/Expanded Stacked可true，其它false且不设置。MajorityVoting只非stacked可true，固定general set majority_voting；模型每profile只一个码制，不污染另一类型。MinCodeLength为0..2147483647（2/5有效默认3但宿主仍可明确0），MaxCodeLength为1..2147483647且min≤max；MinIdenticalScanlines为0..65536，NumScanlines沿Core且≤65536，非零num必须≥min_identical；实际scanline消耗计原预算。OrientationRadians∈[−π/2,π/2]→degrees，OrientationTolerance沿Core；QuietZone Disabled→false、Standard→true、Tolerant→tolerant、Modules要求QuietZoneModules为1..65536→同整数；其它policy的Modules=null。QuietZone仅解码扫描线约束，不证明QualityConditions.QuietZoneVerified。MinCodeLength/MaxCodeLength是后端读取范围，不能用它隐藏额外读数后声称已找到物理全集。

CheckCharacterPolicy的枚举仅映射absent/present/preserved；EngineDefault从新模型get_bar_code_param_specific读取，不从本表样例猜Mandatory列的实际输出。其它general搜索参数（barcode_width/height、contrast等）不开放第二个任意编辑字典，其26.05标准baseline全部冻结；已有资产中的值全部读回，参数高级UI可只读查看。未来明确新增编辑字段才扩此Profile版本，所有HALCON可支持码制通过各自完整baseline解码不要求把每个引擎开关都变成操作员参数。

#### 7.8.3 2D逐类型尺寸/专属参数

每个2D profile恰一个与精确Symbology匹配的TwoDSymbolSettings，OneD=null；1D则TwoD/ContrastMin=null。所有2D ContrastMin为1..255（灰度差），映contrast_min；Core所需module/polarity/mirror/encoding/persistence/candidate字段仍显式且优先§3.2.1。symbol_type不可编辑，GS1类型由create精确类型冻结，不能把普通模型改IsGs1=true冒GS1模型。StringEncoding只§3.2.1三种明确投影，不启auto/locale。train等控制参数不成为输入字段。

| 精确类型 | settings与纯值域 / 固定26.05标准来源 |
|---|---|
| Data Matrix ECC 200 / GS1 DataMatrix | DataMatrix：rows端点为8..144偶数，cols为10..144偶数，min≤max；Shape Any/Square/Rectangle。Square要求rows/cols区间相同且≥10；Rectangle要求rowsMax≤26且colsMin≥18，实际合法尺寸由26.05模型确认。显式设row/col后shape并核全部读回，不能把引擎关联调整当请求同值。标准起点rows8..144、cols10..144、shape读新模型；不开放symbol_size别名避免同一尺寸两种写权 |
| QR Code / GS1 QR Code | Qr version1..40、min≤max，映version_min/max；相应size=17+4v，Model1自身只至14，不凭v>14断言Model1可读，模型自动支持的变体仍按26.05。标准version1..40；不同时设symbol_size别名 |
| Micro QR Code | MicroQr version1..4、min≤max，size=9+2v；标准1..4；不以完整QR的version/模块尺寸外推 |
| PDF417 | Pdf417 rows3..90、cols1..30（列单位codeword，不是像素/module），min≤max；标准baseline rows5..45、cols1..20。Core必须使用module_width/aspect而非module_size；完整/Compact均由同26.05类型识别，不造compact type字符串 |
| Aztec Code / GS1 Aztec Code | Aztec size11..151、min≤max；标准11..151。Compact/full/rune能力在同类型后端核，不能把范围中的每整数称合法符号尺寸；引擎实际读回与Golden决定该变体能力 |
| DotCode / GS1 DotCode | DotCode rows4..998且偶数、cols5..999且奇数、min≤max；标准rows4..998、cols5..999。Contrast/Polarity等仍该模型baseline，模块尺度用Core min/max，不借用DataMatrix质量资格 |

上述标准数值只是手册明确来源，Prepare永远读完整实际baseline并记录；宿主不得省略显式settings后在生产运行时补常数。无高对比/镜像/大尺度客户事实时，保持候选/未验证，不静默切enhanced/maximum。全部查询其它get_model_params字段（如finder/对比度容忍、边界、纠错及搜索级别）的默认原值冻结并公开只读；默认模式选定后不留给首次实现者挑选。未来HALCON版本不同即拒本profile，重新准备/批准新版本，不修改旧资产。

#### 7.8.4 生产消费与Supplemental Evidence v0.1

新增HALCON adapter构造重载为 `HalconBarcodeDecoderAdapter(BarcodeReaderProfile profile,BarcodeAdapterCapabilities enabledCapabilities,IReadOnlyList<BarcodeModelProfile> modelProfiles)`；原两参构造及其少量参数decode行为保持，只承诺§3.2.1子集。三参modelProfiles深冻结且≤retentionProfile可保留槽/总字节，每条ProfileDigest、Asset.Sha256/bytes和CoreParameters.Asset一致；键为精确 `(Symbology,Revision,Asset.Sha256)`，唯一且BackendVersion=26.05。实际request/attempt必须逐字段等于该Profile.CoreParameters，含资产；不存在或相同Revision不同值拒绝而非找latest。Profile/Asset在adapter生命周期内不可替换。

消费从原blob反序列化独占模型，查询同完整FrozenParameters并逐字段核对，然后仅覆盖本attempt剩余timeout（日志记录EffectiveTimeoutMs，不写回Profile）；1D在find前固定set_bar_code_param(M,'train','~all')关闭活动训练；get的train历史tuple不是活动开关，禁训练设置后再次确认历史/非timeout快照不漂移；2D普通find不传train，find StopAfterResultCount用已冻结选项。其它数字/枚举不在生产set中重试修正。原参数snapshot/模型profile身份与每条候选同租约采集；namespace/DTO不泄漏native handle。timeout单调递减，清理沿§7.1，不改变Core资源Owner。

以下扩展值/查询接口位于 `Asun.Modules.Barcode.Extensions`；三参HALCON adapter同时实现它，Host必须显式传引用，不通过反射/静态服务发现。它只附加证据，不能执行find、训练、写身份或修改Core回执。

```csharp
public enum ComponentPresence { NotApplicable, NotRequested, Absent,
    Decoded, ExpectedButUnread, Unknown, Error }
public sealed record BarcodeCompositeEvidence(string ObservationId,string AttemptId,
    string ProfileDigest,CompositeMode RequestedMode,bool? LinkageFlag,
    ComponentPresence Presence,RawPayload PrimaryDecodedData,
    IReadOnlyList<long> LinearReferenceCodes,RawPayload CompositeBytes,
    EngineText CompositeText,IReadOnlyList<string> Issues);
public sealed record BarcodeSupplementalEvidence(Guid RequestId,string ContractVersion,
    IReadOnlyList<string> ProfileDigests,
    IReadOnlyList<BarcodeModelProfile> ModelProfiles,
    IReadOnlyList<BarcodeCompositeEvidence> Components,bool CopyComplete,
    bool ResourcesReleased,string EvidenceDigest);
public interface IBarcodeSupplementalEvidenceSource
{
    Task<BarcodeSupplementalEvidence?> QueryEvidenceAsync(Guid requestId,
        CancellationToken waitToken=default);
    Task<BarcodeAcknowledgeReceipt> AcknowledgeEvidenceAsync(Guid requestId,
        string evidenceDigest,CancellationToken waitToken=default);
}
```

每个已接纳request在首次native工作前预留扩展记录/组件/迟到结果/返回槽，容量沿同readerProfile且完整复制量计request MaxResultBytes/MaxRawBytes；不能解完后才为扩展找无界字典。Query未知ID=null，不执行；复制中可返回CopyComplete=false且ResourcesReleased=false的原不可变快照，EvidenceDigest按实际已复制内容生成，不伪造终态。释放未知保原ID/nativeTask/Input关联，Query不得去运行中模型读。Core与该source共同引用同nativeoperation资源事实，source不另Return Core input；只有native/supplement复制/模型清理退出才ResourcesReleased=true。读回执和证据都已保存后Host分别ack；ackEvidence需CopyComplete+ResourcesReleased及当前digest匹配，否则拒绝，清重payload仅保ID/digest/释放墓碑；Core ack不自动清这份证据，反向也不成立，容量满拒新。保留期过期仅回收已经确认释放且已确认消费/到期政策允许的payload，不遗忘运行资源。

**同索引关系而非字符串拼接。** 每个1D成功Observation（包括非GS1）恰一组件记录，ObservationId/AttemptId按原Core真实输出键；2D无复合记录。PrimaryDecodedData逐值等于该CoreObservation.Raw，是后端decoded_data的高层bytes，保它的实际语义，不把它命名为“保证只有linear”的字节串。LinearReferenceCodes只来自同索引decoded_reference的整数tuple，不转换码表索引/数字为bytes，也不把其中linkage当payload的一字节。CompositeBytes只来自同索引composite_reference，每项0..255整数深复制；CompositeText只来自composite_strings，不用它回编码填bytes。无人工期待值筛选、不按文本/位置猜父子关联、不向CoreObservation.Raw追加逗号/GS/组件，不将find的组合显示字符串拆成两个raw。该记录保存同租约来源、Model Profile、观察键和后端原值，宿主可按原解码图像证据复验。

GS1 DataBar家族decoded_reference首项必须0/1形成LinkageFlag，其余原reference仍全部保留；缺tuple/非法首项为Unknown/Error及BARCODE.RESULT.CARDINALITY，不猜false。非该家族LinkageFlag=null、Presence=NotApplicable、CompositeBytes.Availability=Unavailable；模式None则Presence=NotRequested，**即使linkage=1也不声称不存在组件**。只有CC-A/B才查询composite_reference/strings：非空合法bytes→Decoded（如果linkage明确0同时报不一致/Error，不采用复合业务内容）；linkage=0且成功查询为空→Absent；linkage=1且为空、结果不可得或手册status_id含1005→ExpectedButUnread；linkage未知且空→Unknown。查询异常/Error不是无码；一条解码线性读数仍保持Core原状态/bytes，组件不足不能提升完整复合资格。

CompositeBytes.Available对应真实tuple可用且非空；其它Presence且无bytes时Availability分别为Unavailable（Absent/NotRequested/NotApplicable/ExpectedButUnread）、Unknown或Unsupported（明确后端不提供族），Bytes=null/ByteLength=0，Source=BackendBytes或Unknown；Encoding=Unknown、Eci.IsPresent=false、Gs1Fnc1仅用后端明确证据不从ASCII29猜验证成功。组件未知/失败Issues列精确稳定BARCODE.RESULT.RAW_UNAVAILABLE、BARCODE.RESULT.CARDINALITY、BARCODE.BACKEND.CALL，保Diagnostic引用。status_id在persistence允许时辅助保1005；不能要求persistence不足时空status就证明Absent。组件几何未获独立公开对象时不制造单独框，沿父symbol位置查看两份载荷；质量linear/composite各分项按§7.6同有效handle标签保留，不能复制overall到组件当认证等级。

**训练不扩大target。** 原§3.3A有限typed训练切片不自动接纳这里的Profile。新增Training Adapter Profile v0.1的构造重载 `BarcodeTrainingAdapter(BarcodeReaderProfile retentionProfile,BarcodeProfileWorkerOptions workerOptions,IReadOnlyList<BarcodeModelProfile> modelProfiles)`：按BaseModel hash/Symbology/BaseParameters精确匹配同Profile，Before/After仍原DTO，仅通用target参数进入typed Before/After；worker读完整native baseline对比，除目标element/module字段及其训练历史名字外全部不变，type-specific/check_char/composite/size/encoding均不变。完整训练前后FrozenParameters作为worker ResultManifest附加`ModelProfileEvidence`（协议Version=2，与旧Version=1 worker绝不混接；配置/握手声明2），内容为ContractVersion、BaseProfileDigest、Before/After原参数列表，digest按下一段；同§7.5的帧/blob/消息限额和验证规则，新增字段是版本2闭集字段，不另改老IPC或JCS。A验证完整列表后把candidate Asset/After target与保留specific配置形成新Profile供Host保存，原TrainingReceipt.CandidateRegisterable不替代这份Profile资格；新增source查询通过同IBarcodeSupplementalEvidenceSource记录本训练ID/ProfileDigests以及完整Before/Candidate ModelProfiles（按先Before后Candidate顺序），Components空；生产保底只保Before Profile，临时Candidate不对外交付。production fallback仍禁止持久候选/活动模型改变，完整临时Profile也销毁。原NoRead/训练预算/worker硬停/lease规则不变。

三参训练adapter也实现IBarcodeSupplementalEvidenceSource。训练和解码若同时装配，Host私有SupplementalRouter按根预登记的ID→Decode/Training Owner映射转发唯一原source（两个Owner不得登记相同ID），只包装/留原Task，不查询两个source后猜来源；只启一个功能则直接传同adapter source。

Profile训练的精确v2追加形状为：`BarcodeProfileWorkerOptions(BarcodeWorkerHostOptions Worker,ushort Major,ushort Minor)`，Major=2/Minor=0必填，该Options类型位于Asun.Modules.Barcode.Training，不放Core扩展；其余exe/hash/Job/容量/time字段完整沿§7.5的既有BarcodeWorkerHostOptions，不存在BarcodeTrainingWorkerOptions。worker pipe前缀改`asun.barcode.training.v2.`，header offset4/6与Hello固定2/0；A和W发布包必须明确支持2，不能自动降为v1。其他Kind编号/flags/sequence/32-byte长度/nonce/PID/SID/权限与硬停规则全保持。Begin.Body v2为原四字段再加`ModelProfile`，内容为完整Profile（Asset.Bytes仍引用与BaseModel同一已声明Model BlobRef，不重复上传），W核ProfileDigest/BaseModel.Sha256/Symbology/CoreParameters完整相同并在反序列化后核全部FrozenParameters才可train。

ResultManifest.Body v2为原Receipt/Blobs/FailureReasons再加`ModelProfileEvidence`；其唯一形状是 `{ContractVersion,BaseProfileDigest,Before,After}`，ContractVersion=`barcode-halcon-profile-training/1`，Before/After是完整有序FrozenNativeParameter列表（含general/specific/train历史），Before/After均可null：未读到完整native基线时Before=null，未读到完整训练后模型时After=null；已读到的完整列表保留，不用空数组冒充未读取；可注册候选要求两者非null。InputsComplete/InputsVerified用`barcode-worker-input-jcs-v2`对完整v2 Begin.Body，OutputsComplete/ResultAccepted用`barcode-worker-output-jcs-v2`对完整v2 ResultManifest.Body；这些独立rule直接复用§4.1 JCS规则，不修改旧v1任何预像。单JSON/总wire上限保持，Profile列表超单JSON则接纳前拒绝/后端异常失败，不另启元数据分块。任何未知字段/错version/digest不完整拒收，W清理退出仍照§7.5。A生成新Candidate Profile时Before与输入FrozenParameters精确一致，After只允许element/module目标值和1D对应的General/train、TrainingHistory集合新增该目标名字；1D目标字段可由General转为Symbology（自动训练的真实分类），其它字段Scope/类型/tuple/值不变，历史里非target名字不得增删。2D没有训练历史增量，FindOption恒定（无伪造trained_general字段），其余同值；Candidate Profile的Revision精确取原Receipt.CandidateAsset.Revision，CoreParameters.Revision同值、Values取已核的Receipt.After.Parameters.Values、Asset为原CandidateAsset，OneD/TwoD/Contrast仍原设置；Revision非空/长度合法才交付。After取得新asset/hash与通用参数后重新计算新ProfileDigest，完整ModelProfiles通过扩展source给Host。所有新增值先核总atoms/bytes预算，不让完整配置证据挤掉最后cleanup/terminal槽。

#### 7.8.5 摘要、兼容、UI与反例

独立规则 `barcode-halcon-model-profile-jcs-v1` 投影root={rule,contract,content}，contract=`barcode-halcon-model-profile/1`，content是BarcodeModelProfile全部字段**除ProfileDigest**。CoreParameters递归沿§4.1声明字段/bytes长度hash规则；FrozenParameters按Scope精确枚举名、Name的Ordinal排序，Values保持原tuple顺序/atom类型，Name唯一于同scope；普通参数Values保持tuple顺序，唯General/train与TrainingHistory两项是名字集合，冻结前Ordinal排序且拒重；参数载荷上限以{FrozenParameters:完整列表}的规范JCS UTF-8字节数计，并连同asset/profile/组件及元数据计入累计MaxResultBytes。bytes引用sha/长度；NativeParameterAtom与OneD/TwoD union的$type分别为NativeParameterAtom.Integer/Real/Text、TwoDSymbolSettings.DataMatrix/Qr/MicroQr/Pdf417/Aztec/DotCode，沿§4.1规则，枚举精确名，Int64字符串、有限double沿RFC8785。**它不替换barcode-parameters-jcs-v1**；Core的参数摘要未覆盖这些扩展本就不得拿它证明全部native配置。

`barcode-supplemental-evidence-jcs-v1` 同结构，contract=`barcode-supplemental-evidence/1`，content为BarcodeSupplementalEvidence全部字段除EvidenceDigest；解码ProfileDigests按实际attempt顺序去重首次保留，训练按Before后Candidate且同digest去重首次保留（失败/生产保底仅Before）；ModelProfiles同Digest顺序且包含每个完整Profile（重复Digest不再重复交付），Components按原attempt/观察顺序，LinearReferenceCodes按原tuple且Int64字符串，Raw/bytes沿§4.1。旧CoreReceipt.ResultDigest仍原样；Host保存Envelope={原完整CoreReceipt,SupplementalEvidence,所有被引用ModelProfiles}，逐项核RequestId/ObservationId/AttemptId/Asset/ProfileDigest与原request对应，核自己的完整保存成功后再分别ack。新blob不迁移旧v1摘要；旧profile缺失只能按旧adapter子集能力，不凭资产hash补造组件或完整配置证据。unknown ContractVersion/Major拒绝，不从“有新增字段”自动降级，未来改变枚举/字段/atom或组件解释升独立contract/rule版本；旧向量、客户原模型与Core接收保持。

Workbench Binding追加可选 `IBarcodeSupplementalEvidenceSource? SupplementalEvidence = null`（Core扩展接口，不引用HALCON实现）。需展示组件/完整native配置的Host必须显式传该三参adapter的source引用；旧两参decoder可null并明确“无组件证据”，不显示复合完整标记。该新增可选参数属Barcode WPF Port v0.5，原v0.4语言方法保持。控件收到已复制Core回执后由登记代理有界Query同ID，显示父观察的“主解码数据/线性参考值/复合组件”、Presence、linkage、两份Hex和Profile完整只读参数；不拼成一个身份值、不自动ack。Query在native未退出只显示已复制快照/未确认状态，不接着get native。资源/语言/selection均不重执行；ReceiptAvailable原Decode/Training事件不改，新证据作为同ID详情只读投影，Host保存/ack由原责任承担。没有source时禁用相关详情并给具体原因，不把解码成功画作完整复合成功。

新增断言归既有Halcon.Tests/Training.Tests/Wpf.Tests，不新建报告/工程：每个§2.2精确类型至少Prepare→独立deserialize参数完整一致→一次普通find→清理；2/5默认3/2与其它0/0不同；Code128设Absent拒绝、Code39 Preserved保原校验策略；GS1-128设CC-A/B拒绝、GS1 DataBar允许；stacked voting拒绝；DotCode奇偶、PDF417列单位、DataMatrix关联set导致不符拒绝；未知参数/版本/重复profile/单atom变化改变新digest，旧CoreDigest/向量不改。复合反例为linkage0+空=Absent、linkage1+空/1005=ExpectedButUnread、None+linkage1=NotRequested、真实composite `[48,0,49]`保NUL、同文字两个symbol各关联各自index、非法byte/错tuple拒绝，绝不从display字符串重编码。训练只能目标改变，任何check_char/size/composite/非target漂移拒候选；版本1/2 worker混接无训练。Query/两个ack任一失败保原数据与资源，晚到结果不新Acquire。全部为可判定实施计划，本轮未运行native/worker/WPF或复算此前有效向量。

依据复用§2/7.4.1/7.6、既有固定研究，并定向读取26.05 [`query_bar_code_params`](../../../halcon算子手册/operators/query_bar_code_params.html)、[`get_bar_code_param_specific`](../../../halcon算子手册/operators/get_bar_code_param_specific.html)、[`set_bar_code_param_specific`](../../../halcon算子手册/operators/set_bar_code_param_specific.html)、[`set_bar_code_param`](../../../halcon算子手册/operators/set_bar_code_param.html)、[`query_data_code_2d_params`](../../../halcon算子手册/operators/query_data_code_2d_params.html)、[`create_data_code_2d_model`](../../../halcon算子手册/operators/create_data_code_2d_model.html)、[`set_data_code_2d_param`](../../../halcon算子手册/operators/set_data_code_2d_param.html)、[`get_bar_code_result`](../../../halcon算子手册/operators/get_bar_code_result.html)。不查AsunImage内部，不重复核已确定算子覆盖/依赖。

## 8. 可选 UI 契约（Barcode Workbench PageContract v0.5）

可选 `Asun.Modules.Barcode.Wpf.dll` 仅为同一 Core/Training 操作的投影。独立标签工具与物流工具都能引用，不依赖平台 Shell、数据库或产品 ViewModel。角色为操作员（执行固定 Profile、查看原图、取消、查看原因）和工程师（编辑宿主授权的参数副本、提交宿主校验、离线训练）；授权由宿主提供，UI 不自建账户或质量权限。没有“放行/MES/提交身份”命令。生产 NoRead 保底由宿主政策显式触发，不让操作员通过按钮绕过训练授权。

### 8.1 布局、控件与联动

只在一个固定 1920×1080 屏幕验证视口验收，扣除任务栏、外框、标题栏和状态栏，记录实际 client bounds/DPI；不更改显示设置或扩展分辨率矩阵。初始 client 布局：顶部命令区 48 DIP、底部状态 28 DIP，中间 `DockLayoutManager` 的水平 LayoutGroup：图像区约 65%、右侧观察区约 35%；图像最小宽 600 DIP，右区最小宽 360 DIP，窄 client 按最小约束产生显式滚动而不隐藏执行/取消。比例是布局初值，不是图像或质量参数。恢复布局只恢复此控件范围，不影响宿主工作台。

| 区域/任务 | 实施控件与内容 | 状态与验收 |
|---|---|---|
| 图像/身份上下文 | LayoutPanel + §8.2.1 的 ImageSession.View（宿主通过 ImageFactory 显式创建）；只显示 FrameId、来源/原始或派生、ROI、候选/符号框；保持像素纵横比，原图/适合窗口按钮常驻 | 选中结果按 ObservationId/CandidateId 定位框；选中框选中 grid 行。无几何时只选行并显示“无位置”，不画虚假框；不从当前页面偷取图像 |
| 结果列表 | GridControl + TableView，ItemsSource 为只读快照；列：序号、码制、解码状态、文本预览、raw 可用性、质量状态、原因；支持排序/过滤和 UI virtualization | 默认按 attempt/后端顺序；排序不改变结果对象。重复内容保留多行；训练候选、Replay、Simulator 有文字标记，不能仅用颜色区分 |
| 证据详情 | 右侧详情页签：字节 Hex/长度、引擎原文、派生预览、候选、质量原值、诊断；质量 GridControl 保留 label/index/value/state/条件引用 | Hex 可横向滚动，NUL 显示转义；未知编码不乱码替换后伪称 raw；N/A 原样显示；复制 payload 命令需宿主显式授权，默认只复制诊断 ID |
| 高级参数 | 右侧折叠 LayoutPanel + PropertyGridControl.SelectedObject 绑定 typed 编辑副本；显式 property definitions，只列 §3.2.1 key 和预算；搜索参数；应用前同一 Validate | 工程师授权后可编辑；运行中只读，不改在用请求。切换码制先换该码制完整快照；取消编辑丢弃副本，不回写模型；非法项就地提示，不自动修正 |
| 训练证据 | 工程师离线页签：样本/真值引用、Before/After 参数、fresh read、Golden case、worker/资源状态；调用同一训练端口 | 无固定输入、授权或硬停能力时禁用启动并给具体原因；取消后显示原 operation，DrainUnknown 时仅“查询状态/查看诊断”，不重新训练 |
| 命令/提示 | 执行、取消、查看原图常驻；高级设置折叠，布局恢复与复制诊断为次级命令；不以 DropDownButton 隐藏取消 | BarItem 用 SuperTip；普通 WPF 控件 ToolTip 包 SuperTipControl。提示写清限制和恢复，如“只停止等待不会停止读码，请使用取消” |

采用宿主 DevExpress 25.2.3 主题/字体/图标资源；禁止控件私自改全局主题。统一 8 DIP 间距、标题/正文/状态三级层级，图像背景和 overlay 保持对比；状态同时有短文字和图标。只对展开/选中反馈使用宿主允许的短过渡，不用动画表达执行进度或延缓取消。百分比未知显示阶段与耗时，不编造进度。事件先更新只读快照，Dispatcher 只投影最新进度；关键状态/最终证据不合并丢失，grid 行与 overlay 按 ID 增量更新，不重建整张图。

### 8.2 公开接入与生命周期

WPF 根命名空间 `Asun.Modules.Barcode.Wpf`；公开控件 `BarcodeWorkbenchControl : System.Windows.Controls.Control`。公开接入方法固定为 `void Bind(BarcodeWorkbenchBinding binding)`、`void SetLanguage(System.Globalization.CultureInfo culture)`、`void Unbind()` 和 `ValueTask<BarcodeImageCloseReceipt> CloseImageAsync(CancellationToken waitCancellationToken = default)`；公开 `event EventHandler<BarcodeWorkbenchReceiptEventArgs>? ReceiptAvailable` 只通知已复制的 decode/training 回执。唯一公开 Binding/Permissions/ReceiptEventArgs 形状在 §8.2.1 声明，不另造产品 ViewModel；控件不持久化或 ack。

Bind 不创建模型、不读图、不训练，只在 Dispatcher 创建无资源 ImageSession 并挂接 View；操作时才由宿主工厂取得深冻结请求。ViewModel 仅存编辑副本/选中 ID/事件游标。Unbind/Unloaded 停止 UI observer、解除订阅并发起独立影像会话排空，不 cancel、ack、dispose 宿主 reader/decoder/training adapter；后台原 operation 与查询责任仍在宿主。显示资源未确认释放时控件保留关闭任务、会话和回执，宿主通过 CloseImageAsync 续等，不因移除 View 丢弃清理责任。关闭宿主时显式调用 reader/训练 Close 及 CloseImageAsync，分别处理各自 DrainUnknown；UI 不能先关窗口再当作资源已归还。宿主独占执行实例生命周期与持久化，控件仅拥有由本次 ImageFactory.Create 返回的显示会话。

### 8.2.1 影像窗口最小消费绑定（Barcode WPF Port v0.5）

显示、导航、命中与真实 native/GPU 排空的唯一能力权威是 [Viewport 指导 §3.3、§3.5、§3.6、§4.2、§6、§9、§10.6、§15.2](../viewport/DEVELOPMENT-GUIDE.md)，帧/像素/租约 Owner 见 [image-frame 指导](../image-frame/DEVELOPMENT-GUIDE.md)。本节只冻结 barcode 的消费端口，不复制 renderer、命中算法、ROI 几何编辑或帧库。上游现已给出完整端口与进程根/可选 WPF 绑定，不再把上轮“Session DTO 尚未冻结”作为当前缺口。生产适配按上游当前公开契约实施，不能把上游接收当本模块桥接编译或真实呈现已通过。barcode.Wpf 只消费本节 ImageFactory，不按 FrameId 查询平台服务、不依赖本平台窗口；§8.4 的端口夹具只验证装配/关闭，不伪造公共 Viewer 显示能力。

以下是契约签名摘录（EventArgs 构造函数省略实现体，并非可直接编译的源码），全部位于 `Asun.Modules.Barcode.Wpf`，引用 Core 的公开值类型；WPF 类型只留在此 DLL。集合在调用边界深复制，回执不可变。

```csharp
public sealed record BarcodeWorkbenchPermissions(bool CanExecute,
    bool CanEditParameters, bool CanTrainOffline, bool CanCopyPayload);
public sealed record BarcodeWorkbenchBinding(IBarcodeReader Reader,
    IBarcodeDecoderAdapter DecoderAdapter, Func<BarcodeRequest> CreateRequestSnapshot,
    Func<BarcodeRequest, CoordinateFrame> CreateImageFrameSnapshot,
    BarcodeWorkbenchPermissions Permissions, IBarcodeImageFactory ImageFactory,
    BarcodeImageOptions ImageOptions, IBarcodeTrainingAdapter? TrainingAdapter = null,
    Func<BarcodeTrainingRequest>? CreateTrainingSnapshot = null,
    Asun.Modules.Barcode.Extensions.IBarcodeSupplementalEvidenceSource?
        SupplementalEvidence = null);
public sealed class BarcodeWorkbenchReceiptEventArgs : EventArgs
{
    public BarcodeExecutionReceipt? Decode { get; }
    public BarcodeTrainingReceipt? Training { get; }
    public BarcodeWorkbenchReceiptEventArgs(BarcodeExecutionReceipt? decode,
        BarcodeTrainingReceipt? training);
}
public sealed record BarcodeImageOptions(string ConsumerId, long MaxDisplayBytes,
    int MaxOverlays, long OperationTimeoutMs, long DrainWindowMs);
public interface IBarcodeImageFactory
{
    IBarcodeImageSession Create(BarcodeImageOptions options);
}
public enum BarcodeImageKind { Original, Derived, TrainingCandidate, Replay, Simulator }
public enum BarcodeOverlayKind { SearchDomain, Symbol, UndecodedCandidate }
public sealed record BarcodeImageOverlay(string EvidenceId, BarcodeOverlayKind Kind,
    GeometryEvidence Geometry);
public sealed record BarcodeImageSnapshot(Guid RequestId, long Generation,
    InputFrameRef Input, IBarcodeInputProvider InputProvider, CoordinateFrame ImageFrame,
    SearchDomain SearchDomain,
    BarcodeImageKind Kind, IReadOnlyList<BarcodeImageOverlay> Overlays,
    string? SelectedEvidenceId);
public enum BarcodeImageViewMode { Fit, OneToOnePhysicalPixel }
public enum BarcodeImageOutcome { Presented, Selected, Cleared, Rejected,
    Cancelled, TimedOut, Closed, DrainUnknown }
public sealed record BarcodeImageReceipt(Guid RequestId, long Generation,
    BarcodeImageOutcome Outcome, string? SelectedEvidenceId,
    IReadOnlyList<string> ErrorCodes, IReadOnlyList<string> DiagnosticIds);
public sealed class BarcodeImageSelectionEventArgs : EventArgs
{
    public Guid RequestId { get; }
    public long Generation { get; }
    public string EvidenceId { get; }
    public BarcodeImageSelectionEventArgs(Guid requestId, long generation,
        string evidenceId);
}
public sealed record BarcodeImageCloseReceipt(bool Drained, bool WaitCancelled,
    IReadOnlyList<string> PendingResourceIds, IReadOnlyList<string> DiagnosticIds);
public sealed record BarcodeImageLanguageReceipt(string Language, bool Applied,
    IReadOnlyList<string> ErrorCodes, IReadOnlyList<string> DiagnosticIds);
public interface IBarcodeImageSession
{
    System.Windows.FrameworkElement View { get; }
    event EventHandler<BarcodeImageSelectionEventArgs>? SelectionChanged;
    ValueTask<BarcodeImageReceipt> PresentAsync(BarcodeImageSnapshot snapshot,
        CancellationToken operationCancellationToken = default,
        CancellationToken waitCancellationToken = default);
    ValueTask<BarcodeImageReceipt> SelectAsync(Guid requestId, long generation,
        string? evidenceId, CancellationToken waitCancellationToken = default);
    ValueTask<BarcodeImageReceipt> SetViewModeAsync(Guid requestId, long generation,
        BarcodeImageViewMode mode, CancellationToken waitCancellationToken = default);
    ValueTask<BarcodeImageLanguageReceipt> SetLanguageAsync(
        System.Globalization.CultureInfo culture,
        CancellationToken waitCancellationToken = default);
    ValueTask<BarcodeImageReceipt> ClearAsync(CancellationToken waitCancellationToken = default);
    ValueTask<BarcodeImageCloseReceipt> CloseAsync(CancellationToken waitCancellationToken = default);
}
```

**创建与资源。** Create 仅在所属 WPF Dispatcher 校验 options 并返回独占 session/View，不 IO、不 Acquire、不创建 native 影像、无后台执行。ConsumerId 非空；MaxDisplayBytes 正且由宿主显示预算提供，MaxOverlays 为 1..65536，OperationTimeoutMs/DrainWindowMs 为 1..600000；底层获准控件有更小硬界限时在 Create 明确拒绝，不 clamp。Binding 必需 Reader/DecoderAdapter/请求工厂/Permissions/ImageFactory/ImageOptions 非 null；训练 adapter 与训练工厂恰好同时提供或同时为空。Create/Bind 配置非法抛 ArgumentException/ArgumentNullException，取得的 session 若后续挂载失败仍须 Close。一个 session.View 只挂一次且不能被另一 host 共用；Bind 已绑定或旧 ImageSession 未 Drained 时抛 InvalidOperationException，不替换并泄漏旧资源。

CreateImageFrameSnapshot也必需非null；Workbench冻结request后恰调用一次此纯工厂并冻结其CoordinateFrame，校验ImagePixels/非空Id/与Input.CoordinateRevision一致后才执行/显示。不在Run中从当前页面/FrameId猜坐标；Frame工厂异常按预执行输入错误可见报告且不调用Execute。该字段补闭v0.2.2 ImageSnapshot已有ImageFrame的来源，不改解码/训练DTO或JCS规则；v0.3已明确该字段，v0.4追加显示会话的SetLanguageAsync/回执；v0.5再在Binding尾部增加可选SupplementalEvidence，旧必需构造不变。尚无已发布WPF调用方；实现者和Host私有Probe须同步新增方法，不能声称二进制兼容。原图用这个快照，派生显示须有其来源Owner提供的明确目标坐标。

Bind/Unbind/SetLanguage、View 的挂载/移除及 SelectionChanged/ReceiptAvailable 均在所属 Dispatcher；错误线程同步入口抛 InvalidOperationException，不偷偷创建第二 Dispatcher。session 的异步操作与 CloseImageAsync 可从任意线程调用，内部串行接纳并向同一 Dispatcher 投影，不让宿主同步阻塞 UI。从未 Bind 或上一 session 已 Drained 时 CloseImageAsync 返回 Drained=true、WaitCancelled=false、空 PendingResourceIds/DiagnosticIds，不创建新 session。ReceiptEventArgs 恰一 Decode/Training 非 null；SelectionEventArgs 只允许非空 RequestId、正 Generation、已存在的非空 EvidenceId。

session 通过 snapshot.InputProvider.AcquireAsync(Input,SearchDomain,token) **独立取得显示 lease**，不能借用 decoder 的活动 lease。输入像素格式、stride、hash 和坐标按 §3 验证；显示后端不支持该格式时 Rejected+BARCODE.INPUT.FORMAT，不隐式量化 Gray16 或回读原图路径。显示如需拷贝，只用批准公共影像能力并记录自身 MaxDisplayBytes，源像素保持只读；不能在 barcode 内写平行 renderer。显示 session 拥有独立 lease/native 上传/复制/overlay 资源，成功、切换、取消、失败、Clear/Close 均在真实渲染调用/fence 完成后归还。adapter 未证明已深复制时保留源 lease 到该显示退出；已经复制且后台无借用时可提前归还源 lease，但仍持有的显示资源必须等真实 drain。Core 与显示两套 lease 计数分开；归还显示 lease 不证明 decoder 释放，反之亦然。

**呈现与世代。** Workbench 每次显示更新分配 session 内正 long Generation（checked，从1严格递增、不复用）；RequestId 为该观察所属原 ID。PresentAsync 冻结 snapshot、校验容量/当前世代后才 Acquire；原图显示源必须精确等于请求 Input/域，不能把派生图换名成原图。最小绑定只要求原始图+投影结果；若宿主显示 Derived，须提供明确的新 Input/provider/变换，无法取得就 Rejected，不由显示端重做读码预处理。TrainingCandidate/Replay/Simulator 按 Result.Adapter/训练回执标记，不拿普通图像标题隐藏来源。一次 session 至多一个 Present 正在执行，下一项先取消并排空旧显示更新；旧释放未确认则 DrainUnknown，不能并发复用 backing。世代换到B时先撤销A的命中/标题/overlay，再提交B；失败可留A只读旧图但明显显示旧FrameId，禁用A的结果联动，不以B身份响应A图。Presented 必须表示当前图像及匹配overlay实际已呈现（adapter以该控件唯一呈现完成证据为准），不以属性赋值或Dispatcher回调当作可见。

**ROI 与叠加。** 本最小端口是只读 ROI/结果投影，GeometryEvidence.Frame→TargetFrame.Transform 使用 §3 唯一公式，TargetFrame 必须为当前原图坐标 revision；变换不完整拒绝该层并保留结构化问题，不猜映射/IoU。SearchDomain 作为独立 SearchDomain overlay，EvidenceId=`domain/`+DomainId；Symbol/Candidate overlay 直接引用原 ObservationId/CandidateId，不能用 grid 行号替代。polygon/旋转矩形按已有几何形状提供，若 renderer 不支持该形状明示 Rejected，不在 barcode 写近似图形或命中算法。无位置候选不创建 overlay。超 MaxOverlays 拒绝整次投影，不能截掉候选后称完整。高级参数中的 ROI 修改仍是宿主显式配置副本经同一 Validate 后生成新 request；本端口不提供 ROI 编辑/提交权，现有 Viewer 的编辑模式也必须关闭，避免隐藏入口改动 SearchDomain。

SelectAsync/SetViewModeAsync 只接受当前 RequestId/Generation，旧值返回 Rejected+BARCODE.EPOCH.STALE，不执行图像动作；null选择清除高亮但不清原图。未知 EvidenceId 拒绝，已知无几何的结果只选grid，控件不调用图像定位。Select 只高亮/聚焦同一 evidence，不执行读码/改ROI；SelectionChanged 来自既有公共控件真实命中，带稳定ID和原世代；Workbench核对当前世代后选择grid行。程序发起Select与返回同ID事件幂等，不循环触发；同文字多位置仍不同ID。Fit 保持纵横比；OneToOnePhysicalPixel 依现有 Viewport DPI 规则，源1 pixel映射1物理屏幕pixel，不把1 DIP当1 pixel。无图/无几何只显示明确状态，不造框。

snapshot 必须有非空 RequestId、正 Generation、唯一非空 overlay EvidenceId；SelectedEvidenceId 为 null 或精确属于可选结果 Overlays，重复 ID/未知选择在 Acquire 前 Rejected+BARCODE.PARAM.INVALID。ImageFrame 是宿主/坐标 Owner 对该 Input 显式提供的原始像素坐标身份：Kind=ImagePixels、Id 非空、Revision 精确等于 Input.CoordinateRevision，不把 FrameId 猜成坐标 Id；Geometry.TargetFrame 必须逐字段等于 ImageFrame。SearchDomain.Transform 以 ImageFrame 为目标，SearchDomain overlay 用其 Shape/Frame/Transform 和相同 ImageFrame 构造 GeometryEvidence，不是结果行且不可选择。跨 attempt 的派生框只在 §3 变换链完整时投影，不凭图像尺寸相同认为同坐标。控制回执 Clear 在无活动图时用 Guid.Empty/Generation=0，有图时用被清除图身份；Present/Select/SetViewMode 的回执保留其调用身份，即使被拒绝，不能伪称当前帧。Select 成功为 Selected，SetViewMode 成功仅在匹配图实际完成重呈现后为 Presented；关闭后新操作为 Closed。参数/未知选择用 BARCODE.PARAM.INVALID，格式/域/容量/过期/后端/释放错误分别复用 §5.2 的 BARCODE.INPUT.FORMAT、BARCODE.INPUT.DOMAIN、BARCODE.OPERATION.CAPACITY、BARCODE.EPOCH.STALE、BARCODE.BACKEND.CALL、BARCODE.RESOURCE.LEAK；诊断 ID 由显示 adapter 生成，不拼用户 payload。

**取消与关闭。** Present 的 operation token 停止该显示工作（不取消reader），wait token仅停止等待；其它方法 token仅停止等待，已开始的Clear/Close继续。所有操作有限等待由ImageOptions.OperationTimeoutMs控制，清理独立DrainWindowMs；UI不 `.Wait()`/`.Result`，adapter的native/上传不阻塞Dispatcher。Clear撤销命中/显示、清理本session旧图像及叠加的全部借用/任务，空场景与受控UI/renderer基线可留在原root计费供下次Present（§8.7），但不关闭接纳；旧图真实释放且空画面确认才Cleared，否则DrainUnknown且禁止新Present。Close首次原子关闭接纳，撤销View交互/事件并排空所有显示资源；Drained只在显示lease、native/上传与叠加/复制资源全部真实归还时true。等待超时返回Drained=false+PendingResourceIds，wait token取消返回WaitCancelled=true且清理继续；后续Close共享原过程，不重开session。session/View被移出视觉树不等于Closed或Drained。Unbind/Unloaded发起Close保留任务；CloseImageAsync始终可在Unbind后等待同一session，最终Drained才释放引用/允许再次Bind，不能静默捕获关闭异常后忘记session。ReceiptAvailable只发布解码/训练完整回执，显示错误不改raw/算法terminal；关闭两个系统分别核对回执。

外部宿主的完整装配入口与有限退出见 §8.4/9.1–9.3；不保留依赖未构造 hostImageFactory/hostCreateRequest/恢复服务的平行示例。

标签Host与物流Host分别提供自己的ImageFactory/provider/预算，不引用本平台VM/私表；一个关闭不影响另一个。§12/附录B的WPF Exe必须断言独立Create、无隐藏图像、ROI/overlay正确、双向稳定ID联动、迟到世代拒绝、Unloaded续等、decoder与display独立lease归还及真实呈现；端口模拟只能证明消费语义，真实Viewer适配与GPU/native/WPF可见性仍独立验证。

### 8.3 键盘、三语与恢复

Tab 顺序：执行→取消→查看原图→结果 grid→详情→高级参数；Ctrl+Enter 在输入已验证且空闲时执行一次，重复按键不生成新 ID；Esc 在运行中请求一次取消，不直接关闭宿主。方向键选择行并联动图像，Enter 打开证据详情；错误把焦点放到首个非法参数，完成不抢走操作者焦点。UIA 提供控件名称、列标题、状态、禁用原因，屏幕阅读器可读；三语切换保留输入、选中行、游标和未 ack 回执，不重跑算法。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Command.Execute / Cancel / Original | 执行 / 取消 / 查看原图 | 執行 / 取消 / 檢視原圖 | Run / Cancel / Original image |
| State.Decoded / NoRead | 已解码 / 未读出 | 已解碼 / 未讀出 | Decoded / No read |
| State.Candidate / QualityMissing | 有候选未解码 / 质量条件不足 | 有候選未解碼 / 品質條件不足 | Undecoded candidates / Quality conditions missing |
| State.Draining / DrainUnknown | 正在释放资源 / 资源状态未确认，请查询 | 正在釋放資源 / 資源狀態未確認，請查詢 | Releasing resources / Resource state unknown; query status |
| Evidence.Raw / Derived / Training | 原始字节 / 派生预览 / 训练候选 | 原始位元組 / 衍生預覽 / 訓練候選 | Raw bytes / Derived preview / Training candidate |

全部标题、列、参数名/单位、提示、错误和恢复文案使用可扩展资源键；enum、raw、frame ID、错误键和 hash 不翻译。模块随包提供这三种默认资源，宿主可覆盖并调用 SetLanguage，不在控件重复加语言入口。异常只显示稳定错误对应的短句和诊断 ID，native 消息保留受控诊断。运行中禁用参数应用/再次执行，取消可用；DrainUnknown 禁止重跑，只显示查询和诊断。恢复依赖原 RequestId/训练 ID，不用清空页面制造新事实。

Workbench.SetLanguage 仍是 Dispatcher 上的同步投影入口，先验证 culture/本模块完整资源，再登记当前 ImageSession.SetLanguageAsync 的原 ValueTask.AsTask（只转换一次），异步观察，不同步阻塞 Dispatcher。显示会话初始语言默认 zh-CN，Bind 后必须把 Workbench 当前语言投给它，不能依赖机器 CurrentUICulture。显示会话尚未真正 Bind Viewport 时只冻结完整资源、不 IO；已 Bind 时沿 §8.5 的同一 uiBinding.SetResourcesAsync。失败保持该显示会话原完整资源，LanguageReceipt.Applied=false，Workbench 显示短原因和诊断 ID，不谎称显示区已切换。所有语言调用串行，同一时刻至多一项，最多保留一个尚未启动的最新待投影 culture；被取代的未启动项 Applied=false、BARCODE.EPOCH.STALE，不改变业务/像素/选择/执行游标。已接纳原调用和关闭责任仍保留，不能合并掉未退出的 Task。Close 期间新语言请求 Applied=false、BARCODE.OPERATION.CLOSED；等待取消仅停止观察。Probe 的同名方法只更新其三语端口提示并返回真实 Applied，不增加像素或Fake呈现。

验收必须在真实 WPF 控件上完成：两最小宿主加载、键盘/UIA、三语长标签、固定 1920×1080 client 记录、选中联动、100% 原图像素坐标、运行中语言切换、observer 取消、Unloaded、DrainUnknown 和关闭恢复。大量候选按 Profile 上限测量绑定/滚动/Dispatcher 延迟与托管内存；UI 指标不混入 HALCON 性能。本轮未运行 WPF，不称布局或响应通过。

### 8.4 两个 STA 装配规格、登记代理与退出接线

目标源文件 `tests/Modules/barcode/Asun.Modules.Barcode.Wpf.Tests/BarcodeStaHosts.cs`；是附录B同一net10.0-windows/UseWPF=true/BCL Exe 的两入口 `--host label` / `--host logistics`，不另建产品或修改工程。每个入口独立进程一个 Application，`[STAThread] static int Main(string[] args)`，Application.ShutdownMode=OnExplicitShutdown；不能在一个进程创建两个Application，也不把async Main当STA。主线程先创建 §9.2 根并Reserve、再创建对应 §9.1 fixture、登记代理、BarcodeWorkbenchControl、Window；root是Application实例字段，slot是Window生命周期字段，任何Factory/Bind故障都进入相同最外收尾。窗口使用本机当前DPI下固定1920×1080物理验证视口，客户区扣除任务栏、边框、标题/状态栏，不改屏幕设置。资源/布局按 §8.1，不以空TextBlock替代真实Workbench。

| 装配项 | LabelStaHost | LogisticsStaHost |
|---|---|---|
| Core输入 | root.Reserve("label",§9.1固定A ID)→Fixtures.CreateLabel(slot)，Code 128、000123 | root.Reserve("logistics",§9.1固定B ID)→Fixtures.CreateLogistics(slot)，Data Matrix ECC 200、LOT-0007 |
| Binding | Reader=slot.WrapReader(f.Reader)，DecoderAdapter=f.Decoder，CreateRequestSnapshot=()=>f.Request，CreateImageFrameSnapshot=r=>f.ImageFrame（校验r.Input==f.Request.Input），Permissions=new(true,false,false,true) | 相同形状但完全独立的B实例/provider/ID；两Host都不允许修改参数/训练 |
| ImageFactory | slot.WrapImageFactory(new ProbeImageFactory(slot))，ImageOptions=new("label-display",1048576,16,500,500) | 独立 ProbeImageFactory，ImageOptions=new("logistics-display",1048576,16,500,500) |
| 训练 | TrainingAdapter/CreateTrainingSnapshot均null；核心解码仍完整可用 | 同左；真实训练装配用 §7.5 显式构造，不能由选择此Host隐式开启 |
| 控件/语言 | slot.Own(new BarcodeWorkbenchControl())→Bind完整Binding→Window.Content安装 | 同左；资源分别A/B，不跨窗口共用control/image session |

两入口的构造片段如下；所有变量均在本段/§9.1/9.2提供构造，不依赖外部host.*。`ProbeImageFactory`语义紧接本段，slot的三个代理入口也在本节固定。App的root/slot/control/window/原closing controller字段在返回控件前保存，以下片段是其OnStartup在所属STA上执行的装配正文，非已运行证据：

```csharp
// [STAThread] Main仅接受--host label或--host logistics；其它参数退出3。
// new Application { ShutdownMode = ShutdownMode.OnExplicitShutdown }后在Startup调用：
bool logistics = args.SequenceEqual(new[] { "--host", "logistics" });
bool label = args.SequenceEqual(new[] { "--host", "label" });
if (!label && !logistics) throw new ArgumentException("host arguments");
var root = new BarcodeHostRoot(new BarcodeHostRootOptions(2,64,16,32,16777216), TimeProvider.System);
var id = Guid.Parse(logistics ? "22222222-2222-2222-2222-222222222222"
    : "11111111-1111-1111-1111-111111111111");
var slot = root.Reserve(logistics ? "logistics" : "label", id);
// 实际OnStartup从Reserve起即在try/finally/controller保护下，不能构造完才注册收尾。
var f = logistics ? Fixtures.CreateLogistics(slot) : Fixtures.CreateLabel(slot);
var reader = slot.WrapReader(f.Reader);
var probe = slot.Own(new ProbeImageFactory(slot));
var images = slot.WrapImageFactory(probe);
var workbench = slot.Own(new Asun.Modules.Barcode.Wpf.BarcodeWorkbenchControl());
workbench.Bind(new Asun.Modules.Barcode.Wpf.BarcodeWorkbenchBinding(reader, f.Decoder,
    () => f.Request, r => r.Input == f.Request.Input ? f.ImageFrame
        : throw new ArgumentException("fixture coordinate mismatch"), new(true,false,false,true), images,
    new(logistics ? "logistics-display" : "label-display", 1048576,16,500,500), null,null));
var culture = System.Globalization.CultureInfo.GetCultureInfo("zh-CN");
workbench.SetLanguage(culture);
var languages = new System.Windows.Controls.ComboBox {
    ItemsSource = new[] { "zh-CN", "zh-TW", "en-US" }, SelectedItem = "zh-CN" };
var content = new System.Windows.Controls.DockPanel();
System.Windows.Controls.DockPanel.SetDock(languages, System.Windows.Controls.Dock.Top);
content.Children.Add(languages); content.Children.Add(workbench);
var window = slot.Own(new System.Windows.Window { Content = content });
languages.SelectionChanged += (_, _) => {
    try {
        var next = System.Globalization.CultureInfo.GetCultureInfo((string)languages.SelectedItem);
        workbench.SetLanguage(next);
        window.Title = next.Name == "zh-CN" ? "条码验证" : next.Name == "zh-TW" ? "條碼驗證" : "Barcode verification";
    } catch (Exception error) { slot.RecordBusiness(error); } // 外层App触发一次关闭controller
};
// App字段强持全部对象；随后接下述Closing/语言/ReceiptAvailable，最后Show。
```

这两个Host是**真实STA/Window/Workbench装配规格**，本轮不启动。ProbeImageFactory是以下完整语义的Host私有端口验证实现，不是生产Viewer：`internal sealed class ProbeImageFactory : IBarcodeImageFactory`，构造 `ProbeImageFactory(BarcodeHostSlot slot)`，语言只由返回session的 `SetLanguageAsync` 投影；Create在当前Dispatcher创建并Own `ProbeImageSession(options,slot)`，每工厂最多一个session，Create重复拒绝而非替换。session.View是只读Border+TextBlock，明确显示三语“影像端口验证，不显示图像 / 影像連接埠驗證，不顯示影像 / Image port check; no image display”。它不Acquire、不绘像素、不画ROI、不声称Presented；PresentAsync校验 §8.2.1 后返回 Rejected+BARCODE.PARAM.UNSUPPORTED，保留原身份和诊断 `barcode-host/image-not-rendered`，Select/SetViewMode同样拒绝；Clear返回Cleared（Guid.Empty/0），Close原子关闭返回Drained=true且空pending，关闭后操作Closed；SelectionChanged不发假命中。未持有资源故Close可立即确认，与真实Viewer未知释放完全不同。session.SetLanguageAsync在同Dispatcher更新其提示及诊断三语，§8.3列的Workbench资源仍由真实DLL加载。Probe只验外部Host无需Shell能Bind、解码回执/语言/关闭，**不能覆盖图像呈现/独立display lease的必需真实验证项**。

`WrapReader(IBarcodeReader inner)` / `WrapTraining(IBarcodeTrainingAdapter inner)` / `WrapImageFactory(IBarcodeImageFactory inner)` 是 §9.2 slot 的Host私有同步构造入口，返回原接口代理（不新增产品API）。纯 Validate立即转发；每项异步API发前使用slot.Start/StartVoid登记同一底层原Task，原ValueTask.AsTask一次，返回由同一原Task构造的ValueTask，不以有限Observe包装Task替换它；ExecuteAsync/TrainAsync迟到回执先Save再交给UI。AsyncEnumerable由显式包装enumerator实现，第一次MoveNext才接纳，MoveNext/DisposeAsync的原Task各登记并序号去重，取消只停观察，不漏掉原operation/游标。reader Close/训练Close/图片Close按原Owner和cleanup轴共用逻辑关闭键；不同调用者等待投影可独立取消，不能因关闭代理而清内层Task。训练内部原worker/Job/pipe/hostlease仍由inner强持至真实归还，代理不接管SDK句柄。

ImageFactory代理预留对象/return槽后Create，**返回之前**Own原session、其原View、包装session；若返回/挂载异常原session仍可恢复Close。包装session所有Present/Select/SetViewMode/SetLanguage/Clear/Close原Task及Input/provider/snapshot先登记，原View只借给Workbench；Close真实Drained才能解引用，其实未Acquire的Probe例外由其明确零资源证明。真实公共影像适配内部必须沿上游公开 `ViewportRootFactory→root.CreateFactory→session` 和 `ViewportControl.BindAsync(session,root,ViewportUiBindingOptions)`，OwnSession=true，保留上游root/session/uiBinding/原Bind/Unbind/DisposeTask；Create仍只无资源同步构造Control/session，真正Bind/Attach发生在首次Present且原Task先入两根；把本节consumer预算传入上游Root/Options，不创建第二renderer。SourceId/Revision/ImageFrame/ROI/overlay稳定ID从BarcodeImageSnapshot确定映射，不从frame ID猜坐标；readonly绑定只Read、Navigate/Select，禁EditDraft。映射失败用BARCODE.INPUT.DOMAIN/PARAM.UNSUPPORTED明确拒绝，后端VisibleConfirmed/Presenter fence才能返回Presented，不能让Probe成为HALCON后备。创建具体上游依赖时遵循其 §3.3/3.5/3.6/10.6，无影像/权限/后端依赖的空装配可验证，但真实Present必须提供上游必需发布端口；这是确定桥接义务，不是“首次开发选择任意Viewer”。

**命令和三语。** Workbench的运行入口由真实控件Ctrl+Enter/Execute命令完成，调用代理同Core；两Host请求工厂恰返回其唯一冻结请求，第一次完成后禁重复Run，同一ID查询/ack/恢复依原合同；不能在每次按键Guid.NewGuid绕过一次执行。外层Host的Language ComboBox三个CultureInfo值为zh-CN/zh-TW/en-US，默认zh-CN；SelectionChanged在同Dispatcher调用 `workbench.SetLanguage(culture)`，更新Host标题/关闭状态/Probe提示，语言不重Bind、不Execute、不变Frame/参数/游标/选中ID。每次只一个Dispatcher投递任务，保留实际DispatcherOperation.Task，失去窗口后未执行的投影撤销，已执行/迟到的引用仍由槽强持，Dispatcher完成不代表GPU归还。ReceiptAvailable处理器只通知同slot的保存协调路径，不在事件内另发重复ack。没有SupplementalEvidence时沿原SaveDecode/SaveTraining及精确terminalSequence确认；存在source时按下面扩展保存链执行，observer事件故障记录BusinessErrors不阻止根收尾。

**扩展证据登记与保存（Port v0.5）。** slot另提供Host私有纯构造WrapSupplemental(IBarcodeSupplementalEvidenceSource inner)，每次QueryEvidenceAsync/AcknowledgeEvidenceAsync发前登记原Task，迟到快照先按(ID,EvidenceDigest)深保存；不启动decode/train，也不清Core payload。绑定传同adapter的包装source。SaveDecode/SaveTraining先保存原完整回执，再有界Query同Decode/Training ID；一个Query未退出不重开，null/CopyComplete=false/ResourcesReleased=false时保留原回执和查询状态，两个ack均不发。source返回完整已释放证据后，按§7.8.5逐字段/digest核对，保存Envelope及其中所有原bytes/Profile；本Host用有界内存账本，生产由已有持久化Owner确认完整保存，未知提交不ack。随后登记一次原Core AcknowledgeAndReleaseAsync(ID,terminalSequence)/训练AcknowledgeTrainingAsync以及一次AcknowledgeEvidenceAsync(ID,完整保存的EvidenceDigest)；两项各存原Task/回执，不把一项成功当另一项成功，不用已清payload重算摘要。已成功项不重发，未知项只观察原Task/查询原墓碑；明确可重试时只用原ID/序号/digest。UI详情查询与保存协调复用同一有界记录，不生成无界poll；关闭时保留未保存或未确认项，不因Unbind丢失证据或后台Owner。

**关闭接线（同一实现用于两个Host）。** Window.Closing先检查私有allowFinalClose：只有最终资源屏障确认后由Application设true时才不取消；否则设置e.Cancel=true，slot.CloseBusinessAdmission并禁Run/编辑，首次发一次原关闭controller Task登记为 `ui-close-controller`，以后只观察同controller，不能async void等待链散落Window事件。该controller依次在独立try块有限观察：(1) Dispatcher上Unbind撤observer/发起显示Close；(2) reader.CloseAsync；(3) 如果已构造则training.CloseTrainingAsync；(4) workbench.CloseImageAsync；(5) 原枚举Dispose/Dispatcher/迟到接收完成检查；前一异常不跳后项，各轴原Task复用、500ms独立观察，最多3次自动观察，原业务错误保留。controller自身还在运行时不参与自己TryRetire的屏障；它结束后，由Main/Application持有的完成接收路径检查其真实结束，不能在controller里等待自己完成。

controller的最外finally先确认PromoteForRecovery，转交异常/拒绝只RecordCleanup、不throw覆盖原业务错误，原根槽仍存在。还有Pending则保持Application/Dispatcher与根存活，Window显示 §8.3资源未知/查询状态；可取消未执行投影、撤交互，但不能先Shutdown、丢root或强制GC。恢复按钮只对原ID Query并有限续等原Close，不Run/Train新动作。三轴均确认、所有原Task/observer/Dispatcher及lease账本归零且完整回执已保存ack后，完成接收路径安排最后Dispatcher关闭Window；这一最终Window.Close投递Task同样登记，完成后在Application层TryRetire，再显式 Application.Shutdown(汇总码)。Main从app.Run返回后读根状态/错误确定最终int，不能在try预先return 0；退出投递自身不计进关资源的自等待，最后原Task结束的Main仍验证它，故不把“允许关闭”当退净。Window.Unloaded只发幂等Unbind请求，不能触发重复reader/训练关闭。意外初始化/Bind/语言事件故障也走上述controller，所有已Own部分对象由槽按类型找回并清理，不依赖局部fixture变量赋值成功。

定向断言ID：BARCODE.WPF.8.4.STA_A/B、Language、CloseDuringDecode、BindThrow、LateDispatcher、IndependentCleanup、HandoffRetained；分别验证实际STA属性/Dispatcher、两个Host零隐藏依赖、三语不改请求、Execute原Task先登记、Unbind/执行/训练/显示任一fault仍观察其它轴、窗口不以资源未知退出、确认接管才离栈。图像真实呈现/ROI联动/独立display lease另外以 §8.2.1/12 的真实Viewer用例ID验收；不跑本轮UI，也不把端口Probe结果当此门通过。

### 8.5 Viewport 0.3.5-prep / WPF Assembly Contract v0.2 消费绑定

本节是 barcode 的消费要求；上游根、OwnSession、Close 和 renderer 的唯一权威仍是 [Viewport §10.6～10.9、§15.2.1～15.2.3](../viewport/DEVELOPMENT-GUIDE.md)。不在 barcode 重写 renderer、创建平行 native 窗口或重新审核上游生命周期。§8.4 的 ImageFactory 代理仍用于登记本方资源，不能用其 Probe 代替以下真实装配。

**确定装配顺序。** ImageFactory.Create 仅冻结配置、在同一 Dispatcher 构造无参 `Asun.UI.Viewports.Wpf.ViewportControl` 和显示会话；同一显示会话拥有独立 viewport root/session/renderer/UI binding，不与另一个 barcode Host 共享。首次 Present 前宿主显式提供原始源的完整 SourceBinding、Frames/Coordinates/Authorization 端口、原授权快照、Limits、资源准入及冻结 Profile；缺一项拒绝，不从全局容器或 FrameId 找默认服务。先由本方根预留并保存各对象，再依次构造 `new ViewportRootFactory().Create(ViewportRootOptions)` → `ViewportRendererFactory.Create(control,root,rendererOptions)` → `root.CreateFactory().Create(ViewportOptions)`；Create 不取得像素/开 native 窗口。

上游 Options 必须是 ReadOnly、Navigation|Presentation（只读稳定对象选择走公开选择命令），RoiEditing/Probe/Surface3D 均不申请，Roi/Surface/Probe 为空。Frames/Coordinates/Authorization、Limits 和显示/工作/清理预算均显式给出，Backend=rendererPorts.Backend，BackendPolicy=该 rendererOptions.Policy，**Presentation=同 control.Presentation**。取得 Presentation 在 Create session 之前合法；它是该控件稳定的无资源转发器，不能 new 另一 presentation port 或转发到另一个 binding。ProductionDisplay/EvidenceReview 使用 Required 准入及非空真实 IViewportResourceAdmission；只有已声明离线且无共享物理池的工程装配才可 BudgetOnly，不能用它绕过资源/授权失败。

然后取得完整资源并调用该实际 control 的 `BindAsync(session,root,new ViewportUiBindingOptions(bindingId,true,resources,cleanupBudget,Lifetime:rendererPorts.Lifetime,ExecutionBudget:uiBudget),ct)`。`OwnSession=true` 保持。Lifetime 必须非 null，Backend/Lifetime 来自同一次 renderer factory、同 control/root/Dispatcher，不能交叉混用或共享另一个尚未收敛 binding 的 renderer。原 Bind Task 在启动前有预留、返回后立即保存；成功 Value 保存为唯一 uiBinding，失败 Value/原 Task/部分对象仍由根保留。Bind 只 InstallEmpty，不取 Presenter；成功后才一次 `session.AttachAsync(context,ct)`，不出现 Bind 等 Attach、Attach 又等 Bind 的循环。后续全量替换走同 session.UpdateAsync；Clear/Close 按下方处理，不新 Bind 逃避旧清理。

**来源与坐标消费。** `BarcodeImageSnapshot.Input/InputProvider/ImageFrame/SearchDomain` 仍是唯一原始显示输入；display 必须独立 Acquire，不能借 decoder lease。上游内置 renderer 只认 §15.2.2 image-frame Adapter 私有 payload；不能把 BarcodePixelBuffer 包成任意 IFramePayload 后声称可显示。路线固定为独立 barcode display lease → image-frame `IFrameService.PublishCopyAsync(CopyPublishRequest)` 的受控行复制 → 同一已发布 FrameDescriptor/FrameKey 的上游 §15.2.2 IFramePort → 内置 renderer。原 provider lease 至少持有到 Publish 的原操作实际退出并确认 OperationResourcesReleased；观察到期/DrainUnknown 时用原 ServiceEpoch/RequestId QueryOperation，不重新 Publish 或提前归还。源服务/adapter 如由宿主借用不由 barcode 关闭；barcode 只 Retire 自己发布的确切 key，并等自己的全部借用归还。该路线的本方公开构造、实际producer及Register/Remove消费闭包见§8.6，限定自审结论见§16.1；目标规格明确不等于已提供可编译桥接。

映射采用有界不可变 binding：保留原 InputFrameRef、完整发布 FrameDescriptor、原 ImageFrame、像素 hash 和完整 SearchDomain。Gray8→UInt8 单通道、Gray16→UInt16 little-endian、Rgb8→UInt8 RGB interleaved；不隐式拆/合通道或量化；布局、半开有效域、层中心和原 lease 的 Return 沿上游 §15.2.2。SourceId/SourceRevision 是宿主明确给出的稳定 token 并关联完整原 FrameKey，不以文件名推测；每个新发布 key 必须新绑定。同 token 异内容拒绝。barcode 的 string CoordinateRevision 以有界一一映射关联 viewport 的非负 long token，保存完整原文字和上游坐标引用；不 parse/截断/hash成 long，不因字符串为“1”就当上游 revision=1。DisplayGeneration 与 barcode Generation 分轴登记，不能强转后混用；上游生成变化时保原调用/原映射拒绝迟到。

只读 overlay 使用 `OverlayLayer`/`OverlayPayload` 的 `RoiGeometry`，一个 evidence 对应一个 StableObjectId，分别保原 SourceRevision、CoordinateRevision、GeometryRevision 和 EvidenceId；geometry revision 采用本次冻结显示投影的有界 token，不写 ROI 文档。SearchDomain 层不可交互，符号/候选层仅允许选择；只读 rectangle/rotated rectangle/polygon 逐值映射到公开 RoiGeometrySnapshot，禁止用 Label 层代几何或线框 renderer。坐标转换复用 coordinate port 的显式图/identity binding；不在 barcode 另写命中、近似裁切或物理坐标转换。缺合法 shape/变换/预算拒绝该投影，保错误与原输入。真实画布命中通过上游 SelectCommand 的 PointerSample/候选结果关联稳定 ID，核原 display generation 后回传原 EvidenceId；**SelectCommand 只有 SelectionRequest(PointerSample,CandidateLimit)，不接受 StableObjectId**，不能伪造“按ID选择”重载或用中心点命中代替 grid 指定对象。grid→指定框高亮/聚焦的真实公开接线仍按 §16.1 单列。显示模式用 SetViewCommand，1:1 依上游物理像素语义。没有源 ROI 编辑权，不产生任何 EditDraft/CommitIntent。

**完整呈现出处。** 内置 lifetime 消费 `ViewportPresenterSubmission(Request,Presentation,SourceCall)`，其中 Presentation 是原 `PresentationRequest(BackendSubmissionReceipt,ExpectedAuthorization,ContextRevision)`，SourceCall 是原 root 签发调用；不是只传 PresentationId/Generation，也不构造 fake call。同 control.Presentation 的 Commit 转发同 uiBinding，并保完整原提交/授权/上下文；同键同内容必须返回同一 OriginalCommit Task，同键异内容拒绝016，旧代005/撤权/关门先拒绝且 Acquire=0。Acquire/Confirm 的 child 剩余预算取与原 Commit 剩余的 min，不在阶段切换时重新给满时限。

barcode 通过 **同 uiBinding.GetPresentations()** 关联完整 `OriginalCommit/OriginalAcquire/OriginalConfirm/PresenterIdentity/OriginalRevoke/OriginalReturn/Cleanup` 观测；这里只借观测快照，不取得 PresenterLease 然后由 Host 再 Return。原 Task 与租约由上游 root 强持，本方只登记其出处和有限观察。容量满拒绝新呈现，未归还项不驱逐。PresentationReceipt 必须身份/两种 generation 匹配且 VisibleConfirmed=true 才将本方 outcome 置 Presented；Dispatcher 完成、后端 Submit 成功或单纯 Commit Task 完成均不够。未确认可见保留错误/未决资源并返回 TimedOut/Rejected，不能回 Presented。

**资源与三语。** 资源从 `ViewportUiResourceCatalog.Get(language)` 的成功 Value 取完整快照，Revision 精确等于 `ViewportUiResourceCatalog.SchemaId = "viewport-ui-text/1"`；校验覆盖全部 RequiredKeys 后才 Bind/SetResources。barcode 额外几何标签显式增加 `Barcode.Layer.SearchDomain`、`Barcode.Layer.Symbol`、`Barcode.Layer.UndecodedCandidate`，分别为“读码区域 / 讀碼區域 / Read area”、“已解码符号 / 已解碼符號 / Decoded symbol”、“未解码候选 / 未解碼候選 / Undecoded candidate”，只作标签，不携 payload。保留上游全部键，不用七键 fixture 替代。扩展 keys≤1024，key 1..128 UTF-16、value 1..1024，完整 UTF-8≤1MiB，拒 NUL/大小写碰撞和未经 schema 允许的 placeholder。自定义语言须完整满足同 schema；缺键或非法文本拒绝整次切换并保旧完整资源。

§8.3 的 SetLanguageAsync 在同 binding 调 `SetResourcesAsync(resources,剩余操作预算,ct)`，保存原 Task；不重新 Bind，不取像素、不解码，不改业务 revision。成功才 Applied=true，失败保旧完整显示语言；不可把 Workbench 文字已变当 Viewport 已变。追加标签是本方资源，不覆盖上游错误/恢复文案。UIA 的 Viewport Name/HelpText 由上游完整资源更新，barcode 自身 UIA/状态仍由本模块资源投影。

Profile 必须覆盖源/旧新显示/Presenter/渲染 baseline/UI metadata/完整资源/可见确认读回的同时存活峰值，并显式传 ExecutionBudget；不能把 §8.4 Probe 的 1MiB 当真实窗口预算。独立软件真实 Viewer 验证沿上游 Synthetic Profile：64MiB MaxDisplayBytes、64MiB UI、ExecutionBudget=(67108864,32,32)、root=(独立id,2,256,128,268435456,2s,2)、两个呈现槽，renderer baseline/raster 仍按上游 Profile 显式给出；超预算拒绝而不自动扩额。这些仅软件保护上限，1920×1080固定验证视口不变，不是客户性能目标或HALCON内部分配上界。

**有限 Unbind、Clear 与晚到 Return。** Clear 的本方契约仍为撤销当前交互/画面并确认当前呈现/源借用归还，清理未知保持同 binding/原 tasks，禁止新 Present，不以改 Image.Source=null 当 Cleared。上游当前 IViewportSession 未公开 ClearAsync，也不能把 Dispose 当成保持可接纳的 Clear；“清空 Context.Sources 是否合法及如何重 Attach”不能猜，具体调用闭包按 §16.1 保留。Close 已有确定入口：关本方接纳并调用同 uiBinding.UnbindAsync(剩余清理预算,独立清理token)，仅有限观察。UiUnbindReceipt.Detached 不能代 Drained；OwnSession=true 的原 session.Dispose 在上游 UI Control 退出后、slot 外触发并持有，不能由 UI worker 等自身。原 session 已收敛后本方根再于外层有限调用 root.CloseAsync；不另建 Root/Close Owner，也不反复 Dispose 源服务。任何观察超时/cancel 均保留原任务、对象、ID与容量。

Acquire 晚于 Unbind/观察结束、或失败 Value 仍带 lease 时，上游 root extractor 先登记实际 lease，再由同 lifetime Owner 沿 Revoke→确认 callbacks quiesced/references detached→同 ReturnId Return；Return 未真实确认先 QueryReturn 同 ID，不重复析构，不靠 Window.Close/GC 归还。barcode 持有同 ImageSession/根关联至实际 Drained 或 §9.2 的明确接管；不能因控件移除、GetPresentations 当前没有 Value 或等待 wrapper 完成删账。

§12/B.1 的同一 Wpf.Tests 追加定向断言：Lifetime=null/跨Control/root拒绝且无Acquire；Bind先empty后Attach；同Commit原Task精确相同；Submission/SourceCall/授权/ContextRevision完整传递；缺任一 RequiredKey保旧语言；语言原任务晚到；Acquire/Confirm闩锁后Close、失败带lease和迟到Return；只Return一次且Query同ID；只读ROI/双向稳定ID/物理1:1；真实可见确认及独立lease归还。Probe只覆盖装配，不抵消真实源/Viewer输入缺失。尚未编译或执行这些断言。

### 8.6 Barcode Viewport Factory v0.1：本方公开源桥（BC-U1）

本节关闭BC-U1的软件设计，包含本方工厂、源发布/读取/Remove/Retire、原Task/lease/预算和双Host装配；实际生产者消费Viewport原Owner已新增§15.2.2.1公开入口，不另审Root/Close。下列本方接口由其Host适配到上游公开工厂。Wpf只引用Core/Extensions、image-frame Core/Resources及Viewport Core/Wpf/ImageFrame公开程序集；不引用平台Shell/私表。未来文件唯一位于附录B的Barcode.Wpf工程与同Wpf.Tests，当前不创建。

目标namespace=`Asun.Modules.Barcode.Wpf`，源服务引用显式取`Asun.Modules.ImageFrame.Resources`，Viewport类型取`Asun.UI.Viewports`/`Asun.UI.Viewports.Wpf`。声明摘录，未编译。

```csharp
public sealed record BarcodeViewportFactoryProfile(
    string ProfileId,string Revision,Guid BindingId,
    Asun.Modules.ImageFrame.Resources.ResourceLimits SourceLimits,
    Asun.UI.Viewports.ImageFrame.ViewportImageFrameSourceOptions SourceOptions,
    Asun.UI.Viewports.ViewportRootOptions RootOptions,
    Asun.UI.Viewports.ViewportLimits ViewportLimits,
    Asun.UI.Viewports.Wpf.ViewportRendererOptions RendererOptions,
    Asun.UI.Viewports.Wpf.ViewportUiExecutionBudget UiBudget,
    Asun.UI.Viewports.ResourceAdmissionMode AdmissionMode,
    int TileWidth,int TileHeight,int MaxInFlightTiles,long MaxBridgeBytes,
    int MaxTrackedOperations,int MaxCoordinateBindings);
public sealed record BarcodeViewportSourceBinding(
    Guid BindingId,string PublishedBindingId,
    Asun.Modules.ImageFrame.Resources.FrameDescriptor PublishedFrame,
    InputFrameRef OriginalInput,CoordinateFrame ImageFrame,
    Asun.UI.Viewports.SourceId SourceId,
    Asun.UI.Viewports.CoordinateRevision CoordinateRevision,
    Asun.UI.Viewports.ImageSourceDescriptor ImageDescriptor,
    string ViewportConsumerId);
public sealed record BarcodeViewportSourcePorts(
    Asun.UI.Viewports.IFramePort Frames,
    Asun.UI.Viewports.ICoordinatePort Coordinates,
    Asun.UI.Viewports.ImageFrame.IViewportImageFrameSource Source);
public interface IBarcodeViewportPublishedSourceFactory
{
    BarcodeViewportSourcePorts Create(BarcodeViewportSourceBinding binding,
        Asun.Modules.ImageFrame.Resources.IFrameService source,
        Asun.UI.Viewports.IViewportProcessRoot root);
}
public sealed record BarcodeViewportFactoryPorts(
    Asun.Modules.ImageFrame.Resources.IFrameServiceFactory Frames,
    Asun.Modules.ImageFrame.Core.IManagedLayoutValidator LayoutValidator,
    IBarcodeViewportPublishedSourceFactory PublishedSources,
    Asun.UI.Viewports.IAuthorizationPort Authorization,
    Func<BarcodeImageSnapshot,Asun.UI.Viewports.AuthorizationSnapshot>
        CreateAuthorizationSnapshot,
    Asun.UI.Viewports.IViewportResourceAdmission? ResourceAdmission,
    TimeProvider Time);
public sealed class BarcodeViewportImageFactory : IBarcodeImageFactory
{
    public BarcodeViewportImageFactory(BarcodeViewportFactoryProfile profile,
        BarcodeViewportFactoryPorts ports);
    public IBarcodeImageSession Create(BarcodeImageOptions options);
}
```

constructor纯值验证/深冻结，不Create服务/Acquire/启动Task；ProfileId/Revision UTF-8非空≤128、BindingId非空且由Host纯构造显式传入，所有ports必需非null（Required时ResourceAdmission必需，BudgetOnly时为空）；SourceLimits/RootOptions/ViewportLimits/UI/renderer按原上游完整校验；SourceOptions.ConsumerId精确为本session的viewportConsumer，MaxBindings至少2且≤SourceLimits.MaxFrames，MaxRetainedMetadataBytes正且≤MaxBridgeBytes。TileWidth/Height为1..4096、MaxInFlightTiles正且≤ViewportLimits.MaxPlanTiles，MaxTrackedOperations为1..65536、MaxCoordinateBindings为1..65536且≥SourceOptions.MaxBindings、MaxBridgeBytes正；MaxBridgeBytes覆盖bridge自身强持的source/行复制/描述/原Task元数据，不能拿源逻辑bytes充当viewport原物理allocation。预算任何一项缺失或关系非法同步ArgumentException，不创建空SourceOwner补值。

Create在所属Dispatcher校验§8.2.1 options，ConsumerId与该profile已登记的publish/viewport consumer对应；构造独立空session/View/Control及有界ledger，无native/像素/后台任务。每个factory最多一个未关闭显示session，不能被两个Host同时用；下一次Create只能在原session完整Drained且它独占的frame service/root关闭后。profile内root id与本次binding身份由constructor确定，同名独立root仍不是同实例。创建过程每取得对象立刻由§8.4本方根/slot登记，再交Workbench；失败同根收尾，不靠调用方成功拿到返回值才有Owner。

PublishedSources.Create是**明确注入的源生产者适配端口**：输入同公开IFrameService实例、已发布不可变Descriptor/完整Barcode输入坐标和实际viewport root；同步返回同生产者的Frames/Coordinates及Source引用（仅供Register/Remove元数据生命周期），无IO/lease/native，不Install/Bind renderer、不创建第二root。Frames必须产生Viewport §15.2.2的同image-frame消费路径私有payload，使内置renderer可识别；Coordinates按完整显式同像素frame/identity绑定（跨frame则使用坐标Owner公开图/路径），不能伪造原frame revision。实现者不允许自造任意IFramePayload或查反射类型名。实际Host私有实现固定为PublishedSourceAdapter，constructor纯冻结profile.SourceOptions及有界ledger。首次Create收到本方已Own的同source/root，调用公开 `Asun.UI.Viewports.ImageFrame.ViewportImageFrameSourceFactory.Create(source,root,profile.SourceOptions)`，核PortResult.Succeeded且Value非null，立即保该IViewportImageFrameSource；此工厂纯构造，不启动Read。之后同session每次Create都必须传相同source/root实例，只复用原producer，不重新创建Frames或更换已冻结Options。调用 `producer.Register(new ViewportPublishedFrameBinding(binding.PublishedBindingId,binding.PublishedFrame,binding.ImageDescriptor,ImmutableArray.Create(0),binding.PublishedFrame.CoordinateReference))`，核Succeeded及Value恰原PublishedBindingId，才返回BarcodeViewportSourcePorts(producer.Frames,producer.Coordinates,producer)。失败保原entry/发布holder并收尾，不临时自造payload。首次成功注册后才以同Frames/Coordinates创建session/同Control renderer、Bind并Attach；后续Register→同session.Update。首次Publish可以先于Bind，二者无循环依赖。所有跨像素frame变换仍使用独立坐标Owner公开端口；本工厂两个合成Host只用上游明确同PixelSpace的identity。原producer未移除entry或原Task未排空不得换source/root；全部移除且本显示session/root关闭后可对下一独立session重新纯构造，不遗忘旧Owner。

#### 8.6.1 独占发布、逐行复制与原Task责任

每显示session第一次Present才用注入FramesFactory.Create(SourceLimits,LayoutValidator,Time,null)取得独占IFrameService，保存原instance/ServiceEpoch；FrameServiceFactory/ManagedLayoutValidator均用上游公开无参构造，factory错误/Service=null拒绝并留诊断。该service只是本session的不可变显示副本Owner，不替换或关闭宿主provider/decoder。SourceLimits两个consumer的ID为options.ConsumerId+`/publish`和+`/viewport`（合成值须≤128 UTF8）；前者发布、后者read；两者额度与服务总额度事先给全，不动态登记消费者。

Present入口先冻结snapshot并预留一整次Acquire/Publish/Attach-or-Update/返回/Retire及失败清理槽；计入所有并存native/CPU/旧新metadata。为独立display借用调用snapshot.InputProvider.AcquireAsync，ValueTask一次AsTask保存为原Acquire；成功lease先Own再核完整Frame/Domain/Pixels/hash。Acquire晚到/失败已取得lease仍同本方slot捕获，不因观察超时忽略。与decoder的lease完全不同，由此session负责Dispose且保原DisposeTask。源数据有效域是完整原图，SearchDomain是overlay/读码ROI，**不把ROI之外原图像素标缺失**。

FrameKey=(本session首次生成并保存的Guid,checked正ulong发布序号)，每次新像素请求递增，不把BarcodeInput.FrameId parse成Guid。相同RequestId/Generation/完整Input及overlay的幂等重复返回原PresentTask，不再Acquire/Publish；同键不同内容拒绝。BindingId固定为profile.BindingId，PublishedBindingId=BindingId小写N+"/"+发布序号无前导零十进制（UTF8≤128）；每个新key都有不同PublishedBindingId和完整冻结binding，不复用旧entry指向新FrameKey；SourceId=`barcode/`+BindingId小写N，SourceRevision="frame/"+发布序号无前导零十进制（UTF8≤128），保原FrameKey/完整Input字段/hash/coord对应表。ImageFrame string revision与viewport CoordinateRevision保持§8.5的有界bijection，同原完整ImageFrame不重复分配token，同token异内容拒绝，耗尽拒新并保旧清理，不回绕。一个session至多一个当前published frame及一个尚待失败/替换Retire的frame；旧源未真实归还禁止下一项，避免无限叠加。

紧凑布局唯一映射为一个plane：Gray8 UInt8/8-bit/1/SinglePlane/Intensity、Gray16 UInt16/16-bit/1/SinglePlane/Intensity、Rgb8 UInt8/8-bit/3/Interleaved/Intensity。ByteOrder=LittleEndian、OffsetBytes=0、RowBytes=checked(width*bpp)、StrideBytes=RowBytes、AccessibleBytes=checked(height*RowBytes)、DeclaredBufferBytes同总数；Domain.Full/空Rows。PlaneMetadata.Unit=`1`、Scale=1、Bias=0、ValidDomain.Full、InvalidReason=""，Channels分别`["Gray"]`或`["R","G","B"]`，Interleaved的Intensity只表示数值plane，颜色顺序唯一由Metadata.Channels=[R,G,B]声明；ColorR/G/B只适用于单通道，不能用于此三通道plane。不拆三plane、改顺序或做颜色转换。调用上游LayoutValidator.Validate确认完整布局/FrameBudget；格式、尺寸、checked溢出或预算拒绝时未Publish/native。

私有`BarcodeInputRows : IFrameInputRows`仅借该独立display lease.Pixels，构造校验plane0/width/height/bpp/stride/有效bytes；CopyRow要求planeIndex=0、y有效、destination长度恰RowBytes，然后按checked y*原Stride复制那一行有效字节（不复制padding），同步返回FrameError.None，禁止保存Span/异步写/修改源。每行源都在lease有效期内冻结；Core像素hash按有效行拼接再次核，逐行复制hash与OriginalInput.PixelSha256精确一致。SourceRow退出才可归还lease，不因Publish观察已超时使用finally提前Dispose。

先预留原PublishTask和成功/失败/迟到来源责任，生成新Publish RequestId，构造CopyPublishRequest(RequestId,publishConsumer,FrameDescriptor,rows,剩余operationTime)并AsTask一次保存。FrameDescriptor.SourceId/SourceRevision为以上显式token，CoordinateReference=PixelSpace=`barcode-pixel/`+profile.BindingId小写N+"/"+坐标token无前导零十进制（≤128）；有界表保存原ImageFrame.Id/Revision/完整内容与此PixelSpace一一对应，不截断长原文，不是业务FrameId的伪事实；返回Descriptor/Layout/Metadata逐字段与请求及规范化紧凑值一致。Publish成功且Receipt.Phase=Completed、Error=None、Drain=Drained、OperationResourcesReleased=true才采用发布；否则不Attach/Acquire源，有限QueryOperation(原ServiceEpoch,原RequestId)继续同operation。QueryFound但无Frame时不重发Publish来取返回对象；原PublishTask仍保留至完成，以它的真实Frame作为唯一发布值，查询只证实责任/阶段。

Publish真实退出且OperationResourcesReleased=true后，才能Dispose独立provider lease并等原Dispose实际退出；这只证明源借用归还，新的storage仍由frame service发布holder持有。provider Dispose异常/未知把本方显示DrainUnknown，保原lease/epoch/Task，不能因为服务已复制就假称原provider释放。将原lease退出和新发布holder分两轴登记；随后构造BarcodeViewportSourceBinding并调用同PublishedSources.Create，端口结果/原引用立即保存，失败也要Retire该新key并收尾。

#### 8.6.2 显示读取、descriptor与回收

ImageSourceDescriptor.WidthPx/HeightPx/ChannelCount/BitsPerSample/Signed与已发布layout精确对应，Channels为Ordinal只读集合{Gray}或{R,G,B}；集合本身不表示顺序，RGB读取顺序仍以原Metadata.Channels列表为准、Convention=CenterInteger；CoordinateRevision为上节从1开始checked递增的正long token。ValidityDomain.Boundary按viewport源半开约定(0,0,W,H)、FullBoundaryValid=true、MaskAssetRevision=null，Revision绑定SourceRevision；唯一level0为原尺寸、TileWidth/Height取profile，LevelCenterToSourceCenter=identity、MaxDecodedTileBytes=checked(tileWidth*tileHeight*bpp)（尾块实际更小）。Levels只这一个，不造pyramid/量化/整幅bitmap；DecodeRevision绑定profile.Revision+源hash，Statistics=null；初版不读取整图补统计。Gray8的InitialView.Lut显式LutWindow(0,255,"display-range/uint8/1")、Gray16用(0,65535,"display-range/uint16/1")，这是手动格式范围而非测得extrema/自动建议，RGB8用原RGB三通道显示；自动LUT只接受源Owner另行提供的完整同修订统计，不拿null当可自动选窗。源role=Primary，Timing=null，CorrelationId=原RequestId小写N。ViewState初值Fit2D(控件实际client DIP,实际DPI)，canvas未正面积拒本次呈现、不改成窗口外框尺寸。

Viewport源端口只用该service.ReadAsync(FrameReadRequest)，PlaneIndices=[0]、ConsumerId=viewportConsumer、原FrameKey、tile checked CoreWindow、halo与Boundary/Intent按§15.2.2；每新借用新RequestId。原ReadTask由**原viewport root签发child**保存，lease先由上游extractor登记再采用，失败Value也捕获。source lease.ReadScope/CopyRow使用上游CPU scope，退出后同ReturnId映原lease.ReleaseAsync(剩余清理预算).AsTask（无ct），真实LeaseClosed/ErrorNone/DrainDrained才Returned；StorageReleased=false合法，因为发布holder还在。QueryReturn只读同原记录，原Release未退出不重发；若上游允许幂等有限再次观察Release，沿原scope/ReturnId/cleanup次数，不创建第二lease。barcode本方不再对该viewport借用直接Release/Dispose，避免两个Owner各归还一次。

原图第一次按§8.5创建同control/root/renderer/session→Bind empty→Attach；替换先撤旧交互，以同session.UpdateAsync新完整Context/来源/overlay，原UpdateTask先登记，不能将旧source贴新RequestId标题。每个OriginalCommit/Acquire/Confirm/Return留同binding轨迹；新呈现证据匹配且VisibleConfirmed=true才能Presented。显示失败时撤本次交互、保明确旧图身份/错误；只在旧presenter/source scope真实quiesced/return且已解除旧Context引用之后，调用同producer.Remove(旧PublishedBindingId)并核Succeeded/返回原ID，再Retire旧FrameKey，不能在UpdateTask观察结束就删除旧图storage。

Retire唯一为本显示service.RetireAsync(原key,剩余cleanupBudget)，ValueTask一次AsTask，保存epoch/key/原Task/DrainReceipt。Draining/Unknown时同key有限Retire再观察按上游幂等契约、次数受root cleanupBudget；不Publish旧key、不强制clear数组。Release/Retire完成只证明本方borrow/发布holder归还，最后service.CloseAsync有限回执需ResourcesReleased=true/StateDrained/OutstandingLeaseIds空、所有本方tasks退出，然后原service.DisposeAsync一次，不能Dispose共享provider或别人frame service。Close过程顺序是同uiBinding.Unbind→原session.Dispose实际退出→viewport root.Close→所有source借用确认return→producer.Remove每个已解除Context的原PublishedBindingId成功→Retire本方剩余key→独占frame service.Close/Dispose→本方ledger退出；Clear按§8.7消费上游§4.7.1合法空更新/同session新Present，不走上述Close链。任何阶段观察超时或ct取消只停本观察，独立清理继续；无剩余预算回DrainUnknown+真实pending IDs，关闭Window或UI Unloaded不代归还。

#### 8.6.3 两个独立Host、预算与失败断言

两个真实Viewer Host均复用§9.1自足provider/固定请求/原ImageFrame和§9.2本方根，但替换§8.4 Probe；灰图仍明确Simulator/Synthetic，不用于实际码制Golden。工厂纯构造不得暗中寻找viewer/source/授权。以下是完整本方构造值与流程，PublishedSources使用上文PublishedSourceAdapter→ViewportImageFrameSourceFactory公开路线，构造/注册/移除输入全部明确；不留给客户或未来实现者选择私有payload。

| 字段/构造 | Label Viewer Host A | Logistics Viewer Host B |
|---|---|---|
| session/consumer | `label-display`，rootId=`barcode-label-viewport`；独立Guid bindingA | `logistics-display`，rootId=`barcode-logistics-viewport`；独立Guid bindingB，不借A对象 |
| FrameBudget | BudgetLimit(268435456,67108864,10000,1000,"barcode-ui-software","1","barcode-label-view","1") | 同上只ProfileId=`barcode-logistics-view`；合成软件上限 |
| SourceLimits | ResourceLimits(上项BudgetLimit,134217728,0,0,0,2,2,0,128,60s,2s,[ConsumerLimit("label-display/publish",67108864,2,1,0),ConsumerLimit("label-display/viewport",67108864,16,2,0)]) | 完全独立实例和两个logisticsConsumer，余同；publish+read逻辑计费不冒RSS |
| 上游root/limits | ViewportRootOptions(rootId,2,256,128,268435456,2s,2)；ViewportLimits(2,32,4096,64,32,128,1048576,1,64) | 同数不同rootId；MaxSources=2覆盖替换期间旧/新来源，不动态扩额 |
| renderer/UI | ViewportRendererOptions(OfflineRasterOnly,0,67108864,2,2s)、UiBudget(67108864,32,32) | 相同离线测试路线；两Host均OfflineViewing，不冒生产Purpose |
| SourceOptions | new ViewportImageFrameSourceOptions("label-display/viewport",2,1048576) | 独立实例，ConsumerId="logistics-display/viewport"，其余同 |
| 本方Profile | BarcodeViewportFactoryProfile("barcode-label-view","1",bindingA,以上SourceLimits/SourceOptions/Root/Limits/Renderer/UI,BudgetOnly,256,256,4,134217728,128,128) | ProfileId改logistics、BindingId=bindingB，其他值独立；MaxBridgeBytes本方元数据/源reserve，失败硬拒绝 |
| ports | Frames=new FrameServiceFactory()；LayoutValidator=new ManagedLayoutValidator()；PublishedSources=new PublishedSourceAdapter(以上SourceOptions)；Authorization=下面同HostFixtureAuthorization；CreateAuthorizationSnapshot=同Fixture；ResourceAdmission=null；Time=TimeProvider.System | 逐对象独立，不共用session/控件/ledger/事件 |
| ImageOptions | new("label-display",67108864,16,2000,2000) | new("logistics-display",67108864,16,2000,2000) |

上表Limits.MaxSources的最终构造固定为2（包含替换旧/新同时引用），无需另列可选值。RGB tile峰值用bpp=3算，不用Gray8预算偷算；控件1920×1080实际client、源tile staging、双缓冲/当前scene/读回至少16WH及旧新并存按§8.5核64MiB UI/Raster上限，超界拒绝而非扩大预算。16×16Gray8 provider Publish峰值是256目的+16 scratch及source256受控借用、描述/Task基线；FrameService以自己的allocation ledger计实际，barcode只计自己的同时强持/复制上界，重复引用同数组不当两份物理退款。生产Host把Policy=HalconRequired、Admission=Required并注入真实Owner/预算/授权，真实native baseline数字来自其已采纳显示Profile，不能把此离线0 native误用生产。

两个Host的私有FixtureAuthorization实现公开IAuthorizationPort，constructor纯冻结OwnerId=`barcode-label-auth`或`barcode-logistics-auth`、Revision=`synthetic-auth-1`、Purpose=OfflineViewing、Rights=Read、AccessDomain=该ConsumerId、ExpiresAtUtc为Host启动Time.GetUtcNow()+5min；创建时保存完整snapshot，CreateAuthorizationSnapshot只在原Input/RequestId精确匹配本fixture时返回同原值，不从图片制造新授权。CheckAsync先核request.Expected全部字段精确同值且未过期/未撤销，RequiredRight只能Read、source集合恰constructor由同profile.BindingId形成的单一SourceId（barcode/加小写N；两个Host分别固定bindingA/bindingB，无后续注册入口），call须本root当前签发且剩余budget正；返回同快照成功或明确拒绝，无IO/隐藏共享权限。Changed由同Host显式撤权测试发新Revision/None Rights，不刷新旧期限来让失败通过；上线版本的权限来自原Owner，不用此fixture。

Host具体顺序为本方root.Reserve→Fixtures.CreateLabel/CreateLogistics→own上述FrameServiceFactory/ManagedLayoutValidator/FixtureAuthorization/PublishedSources→own `new BarcodeViewportImageFactory(profile,new BarcodeViewportFactoryPorts(...))`→slot.WrapImageFactory→new BarcodeWorkbenchBinding(Reader代理、Decoder、request工厂、ImageFrame工厂、原权限、该factory、ImageOptions，training均null，SupplementalEvidence可null)→Bind真实Workbench→SetLanguage原三语入口→执行/等待Core/Present→保存Core及可选Supplement→分别ack→正常关闭沿§8.4/8.6.2。各值有确定constructor/来源，真实producer由公开工厂构造并产生内置renderer识别的payload。将来实现缺失或必需case未运行记MissingInput/NotRun，不能转Probe为Passed；CPU模拟只证明读取/资源桥，不代真实renderer呈现。

新增同Wpf.Tests断言为：row padding不发布/hash只算有效像素；RGB/Gray16保持样本类型/渠道；Acquire晚到先登记一次Dispose；Publish等待超时source不Dispose、Query原epoch/ID不重新Publish；Publish成功后provider归还但frame holder仍有；原Read失败带lease捕获、scope退出后单Return、StorageReleased=false允许；Update失败旧源不提前Retire；同frame key重复/错元数据拒绝；容量不足Acquire/Publish/Bind次数0；两个Host source/viewport root/lease各独立；Close/Retire/Dispose任一未知保pending，关闭A不影响B。这些是可实施断言，真实producer/Register/Remove及VisibleConfirmed按同入口验证，未执行C#或WPF。

### 8.7 稳定ID选择与Clear→新Present的精确消费（BC-U2/U3）

只读消费 [Viewport §4.5.1/4.7.1](../viewport/DEVELOPMENT-GUIDE.md) 本次原Owner新增公开规格，未实施。Barcode Port v0.5形状不再增加接口；这两个流程共用§8.5/8.6原root/session/binding。以下只确定本方映射，不重审上游Root/Close。

**实际采用增量的窄兼容。** 本方明确采用Viewport 0.3.5-prep的OverlaySelection/1、EmptyUpdate/1，以及可选image-frame源适配Assembly Contract v0.1；基础ApiVersion保持(0,1)，WPF Assembly Contract保持v0.2，资源schema viewport-ui-text/1保持。实现时只同步本方实际调用/处理的SelectOverlayObjectCommand、OverlayObjectSelectionRequest、ViewportReceipt.ObjectSelection、UpdateReceipt.EmptyTransition、ViewportSnapshot.EmptyTransition及ViewportEventArgs.ObjectSelection/ViewportEventKind.ObjectSelectionChanged；保留原Session/EventRaised、Root/OwnSession/Close签名与旧指针选择分支。不声称新增record构造元数据、Deconstruct或穷尽enum switch具有二进制兼容：本方目标源码/Host和内置renderer须引用同一受影响发布版本编译，事件switch新增明确分支，未知enum不按旧成功事件处理。内置renderer负责BackendScene.ObjectSelection和可信空scene，本方不自建backend；后续若显式注入自有backend，缺这两项应明确拒绝/未确认，不能伪VisibleConfirmed。没有采用这些增量的其它消费者（含variation）不在本页扩范围，不改其指导或重派全审。

**BC-U2，指定结果的只读选择。** Present建立有界不可变映射：每个可选Symbol/Candidate EvidenceId关联当前SourceId/SourceRevision/CoordinateRevision、实际OverlayPayload.GeometryRevision、LayerId及ObjectId。RoiGeometry取该已验证payload中唯一ObjectId；SourcePolyline必须ObjectId=该LayerId（上游定义），并由该LayerId反向关联原EvidenceId；不能假设所有payload的ObjectId等于EvidenceId。SearchDomain层不可交互、不进入可选表。映射与真实已提交overlay同源，容量≤ImageOptions.MaxOverlays；同字节/同中心的两个结果仍不同EvidenceId/完整对象键。清图/撤权/换源先撤该表；选择不重新执行find或获取provider。

SelectAsync先核barcode RequestId/Generation恰当前已呈现图及evidenceId已知，然后取当前viewport snapshot的ContextRevision和DisplayGeneration（两代号分轴，不能以barcode generation代填）。冻结非空OperationId及完整request，预留原ApplyTask/迟到/事件槽，实际调用：

```csharp
var target = evidenceId is null ? null : mappedOverlayObjectRef;
var request = new Asun.UI.Viewports.OverlayObjectSelectionRequest(
    operationId, currentViewportContextRevision, currentViewportGeneration,
    target, FocusIfAvailable: target is not null);
Task<Asun.UI.Viewports.ViewportResult<Asun.UI.Viewports.ViewportReceipt>> originalSelect = viewportSession.ApplyAsync(
    new Asun.UI.Viewports.SelectOverlayObjectCommand(request), CancellationToken.None);
```

该摘录参数来自本节冻结映射/当前公开snapshot，目标Task返回类型必须与上游ApplyAsync一致；本方保存底层原Task，不将wait超时包装Task当它。不向上游转发本方wait token；用其原Options/根预算约束工作，waitCancellation只停本方有限观察；选择已接纳则跟踪原OperationId到真实退出/呈现，超时不得当成Selected或盲发另一ID。上游拒绝不变本方选中值，错代映BARCODE.EPOCH.STALE，未知/错ID映BARCODE.PARAM.INVALID，后端/资源沿§5.2。成功要求ViewportResult.Succeeded且Value非null、Error=null，再核Value这个ViewportReceipt无Error、ObjectSelection.Target逐字段等于请求、ContextRevision及输出Generation是当前原操作结果，非null时Focus=Applied且Presentation属于本次submission/代且VisibleConfirmed=true；null时Focus=NotRequested并核同样的真实呈现。随后才Selected并投影原SelectedEvidenceId，不拿旧Presentation或Focus=Unavailable冒充聚焦。明确缺几何的grid记录保持表格选中，控件只发target=null取消旧高亮，不创建框、不宣称聚焦；若旧高亮清除未知，显示该错误而非继续保留错框。

订阅原viewportSession.EventRaised，按e.Kind==ViewportEventKind.ObjectSelectionChanged分支读取e.ObjectSelection（必需非null）；ObjectSelectionChanged是新增enum值，不是第二个独立事件。先按同session/ScopeKind/OperationId/事件Sequence及当前viewport Generation核通知。Target=null先撤视口高亮；撤权的该通知允许SourceRevision为空、CoordinateRevision为default，不要求旧源字段，也不回填旧对象来通过检查。Target非null才检查其完整Source/Layer/源及坐标/几何修订、输出Generation和OperationId，经同映射回原EvidenceId。程序Select的同OperationId事件只确认，不回发Select；图上指针选择仍消费原SelectCommand/SelectionResult，经完整对象键选择grid，不能只按文字或最近中心。上游Target=null只撤视口高亮，本方BarcodeImageSelectionEventArgs要求非空ID，故不伪造空ID事件；Workbench从本方Select/Clear回执或失效状态投影null，grid事实由Host维护。迟到旧键事件丢弃投影但原Task/资源继续收尾。原等待或迟到查询得到的输出generation更新本方viewport轴，不改变barcode图generation。

**BC-U3，保持接纳的Clear。** 无图且从未创建source/root/native时立即Cleared(Guid.Empty,0)，没有隐藏Attach。已有图时保存被清图RequestId/Generation，封本方Present/选择接纳并撤命中；只用当前viewport ContextRevision构造Sources=[]、Layers=[]、原Authorization/Language/ApiVersion(0,1)、checked revision+1、原有限View的完整ViewportContext，再调用原session.UpdateAsync(new ViewportUpdate(baseRevision,replacement),CancellationToken.None)。预留并保存原UpdateTask和本方clear identity，不能Unbind/Dispose/第二Attach，也不能用正在更新前的baseRevision清除后来新图。相同在途Clear共享原过程；Clear与Present/Select按本方接纳门串行，不合并或重跑。

从原Update的Succeeded且非null Value.EmptyTransition（Value类型为UpdateReceipt），或GetSnapshot().EmptyTransition取得公开Asun.UI.Viewports.EmptyTransitionReceipt；后一条允许原有限Update已超时/取消后观察迟到完成，要求snapshot.State=Empty，且两条均精确匹配**同原空更新**的OperationId、ContextRevision/Generation。只有PreviousPresentationsRevoked、PreviousSourceBorrowsReturned、PreviousWorkQuiesced均true、PreviousCleanup真实Drained、BlankPresentation是本次空scene且VisibleConfirmed=true，才可判viewport已清。snapshot查询只观察同原记录，不能新发空更新作为查询；GetSnapshot()是同步纯观察，不创建QueryTask/重启工作，采用它仍核同原空更新身份。随后同producer.Remove旧PublishedBindingId核Succeeded及原ID，再对本方旧published key按§8.6.2 Retire并核其原Task/真实发布holder归还，provider/bridge旧任务也退出，才清旧像素binding/选择表并返回Cleared(被清图ID/Generation)。空UI场景/renderer受控baseline与独占空FrameService留在原root供下次Present；它们不再借旧像素/overlay，仍计预算，Clear不声称关闭控件或退款全部native/UI基线。关闭A不碰B/宿主provider。

清理或Blank确认未知、Retire未知、等待超时均保原Clear/Update/Retire/lease及pending identity，返回DrainUnknown；wait取消只停等待，原独立清理继续。禁止新Present/选择/换源逃账，只允许原GetSnapshot/原Task有限恢复或Close。迟到满足全部条件时同Clear转为确认，不发第二空更新。首次Present若在Attach之前失败，所有已Own的Acquire/Publish/entry/root仍按本方ledger收尾，不假造current Context/BlankPresentation。完全无资源时Clear可立即确认；已有部分资源但尚未成功Attach时Clear返回明确Rejected+BARCODE.BACKEND.CALL并保诊断，调用方执行Close完成原部分对象清理后才创建新的独立显示session，不以伪Clear复活失败session。

Clear已确认后，新Present以新的barcode正Generation、新FrameKey/binding记录发布；仍同viewport session/control/root，调用UpdateAsync，baseRevision取确认的空context，newRevision=base+1，**不再Attach、不重Bind**。新Read授权/预算逐项重核，原空Presenter由上游同Owner撤回；源已撤权时新Present拒绝而Clear保持成功。

可判定反例归既有Wpf.Tests：完全重叠A/B按B完整键只高亮B；null只清选择不清图；无几何只选grid并撤旧框；旧Source/Coordinate/Geometry/Context/Generation拒绝且不Acquire；迟到选择不选新版对象；当前Clear→同session新Present不再Attach；空图真实呈现未知、旧Return或Retire任一未知拒新；撤权允许安全清屏但禁止新非空显示；相同Clear不增代/重复Return。实际Apply/Update编译、呈现和资源故障验证仍未执行。

## 9. 从空宿主装配与进程根收尾

### 9.1 两个自足无 UI 输入与公共构造

下面源形状位于未来 Core.Tests 的 `BarcodeHostFixtures.cs`，Wpf.Tests 以 Compile Link 复用该源文件（不引用另一 Exe、不复制第二套 Core）。命名空间 `Barcode.HostFixtures` 仅是验证 Host，非模块 DLL 的产品 API。两入口 `CreateLabel(slot)` / `CreateLogistics(slot)` 都只依赖 BCL、本页公开 Core、显式传入的 §9.2 根槽；不读路径、配置、环境变量、Shell 或全局 provider。16×16 合成灰图没有真实符号，预置输出全部标 Simulator，只证明构造/协议。第二消费者的文本解析各留其宿主；Core 不获得标签/物流判定权。

Core 公开构造 `BarcodeReader(BarcodeReaderProfile)`、`SimulatorDecoderAdapter(BarcodeSimulatorScenario)`；公开 `BarcodeSimulatorScenario(BarcodeAdapterAttempt AttemptResult, bool WaitForCancel, bool HoldDrainUntilReleased)` 是 sealed record，`SimulatorDecoderAdapter : IBarcodeDecoderAdapter` 提供 `void ReleaseDrain()`。这三个入口均纯构造、深冻结、不 Acquire、不启动后台工作。首版Simulator能力固定为Code 128/Data Matrix ECC 200两种**协议模拟**、IndependentWorkers、MaxConcurrentCalls=1、MaxQueuedCalls=1、AdapterRevision="barcode-simulator-v1"，空观察的NoRead模板同样有确定能力；不宣称其它码制或真实识别支持，无默认HALCON模型/服务发现。Execute 在自己的有界RequestId账本先登记原执行任务，再基于模板逐字段复制：原请求ID、实际AttemptId/Index/InputSha256/DomainId/ParameterRevision/Purpose，观察/候选按各自输入顺序映射ID为 `<RequestId:N>/a<Index>/o<ordinal>` / `.../c<ordinal>`，候选ObservationId同时映射对应原观察，不能全部写o0/c0或丢多结果；模板geometry坐标/域必须与本次输入精确匹配，未知变换拒绝，不猜映射；保留Simulator标记，不把模板ID当另一请求。WaitForCancel=true等待可控闩锁或本attempt deadline，超時返回Budget/Incomplete，不无限await用户取消；HoldDrainUntilReleased=true时NativeCallDrained=false，DrainAsync有限观察闩锁，ReleaseDrain只解除此模拟屏障。两bool=false时Normal完整回执与drain都已确认，无native资源；仅取消等待不得打开闩锁或消失账本。

以下 provider 是完整的 Host 私有测试实现；它不是新帧库。内存在构造时复制，Acquire 只接受本次精确 frame/domain、最多4个独立 lease；源 bytes 由槽持有，lease 由实际 Acquire 的 reader/display 拥有，Dispose 幂等归还计数。真实 provider 不得用本例即时 Dispose 替代其真实 native/fence 释放。

```csharp
using System.Security.Cryptography;
using System.Text;
using Asun.Modules.Barcode;
namespace Barcode.HostFixtures;

internal sealed class FixtureInputProvider : IBarcodeInputProvider
{
    private readonly object gate = new();
    private readonly byte[] pixels;
    private readonly InputFrameRef frame;
    private readonly SearchDomain domain;
    private int leases;
    public int ActiveLeases { get { lock (gate) return leases; } }
    public FixtureInputProvider(byte[] pixels, InputFrameRef frame, SearchDomain domain)
    {
        if (pixels.Length != 256 || frame.Width != 16 || frame.Height != 16
            || frame.PixelFormat != PixelFormat.Gray8
            || Convert.ToHexString(SHA256.HashData(pixels)).ToLowerInvariant() != frame.PixelSha256)
            throw new ArgumentException("fixture frame mismatch");
        this.pixels = (byte[])pixels.Clone(); this.frame = frame; this.domain = domain;
    }
    public ValueTask<IBarcodeInputLease> AcquireAsync(InputFrameRef input,
        SearchDomain requestedDomain, CancellationToken token)
    {
        token.ThrowIfCancellationRequested();
        // 两fixture均FullFrame/Identity，record相等就是其全部域字段相等。
        if (input != frame || requestedDomain != domain)
            throw new ArgumentException("fixture input mismatch");
        lock (gate)
        {
            if (leases == 4) throw new InvalidOperationException("fixture lease capacity");
            var lease = new Lease(this); leases++; // 无异步间隙，先登记再交付
            return ValueTask.FromResult<IBarcodeInputLease>(lease);
        }
    }
    private sealed class Lease : IBarcodeInputLease
    {
        private readonly FixtureInputProvider owner;
        private int returned;
        public Lease(FixtureInputProvider owner) { this.owner = owner; }
        public InputFrameRef Frame => owner.frame;
        public SearchDomain Domain => owner.domain;
        public BarcodePixelBuffer Pixels => new(owner.pixels, 16, 16, 16, PixelFormat.Gray8);
        public ValueTask DisposeAsync()
        {
            if (Interlocked.Exchange(ref returned, 1) == 0)
                lock (owner.gate) owner.leases--;
            return ValueTask.CompletedTask;
        }
    }
}

internal sealed record Fixture(IBarcodeReader Reader, SimulatorDecoderAdapter Decoder,
    FixtureInputProvider Provider, BarcodeRequest Request, CoordinateFrame ImageFrame);
internal static class Fixtures
{
    public static Fixture CreateLabel(BarcodeHostSlot slot) => Create(slot, false);
    public static Fixture CreateLogistics(BarcodeHostSlot slot) => Create(slot, true);
    private static Fixture Create(BarcodeHostSlot slot, bool twoDimensional)
    {
        string name = twoDimensional ? "logistics" : "label";
        string symbology = twoDimensional ? "Data Matrix ECC 200" : "Code 128";
        Guid id = twoDimensional ? Guid.Parse("22222222-2222-2222-2222-222222222222")
            : Guid.Parse("11111111-1111-1111-1111-111111111111");
        byte[] pixels = Enumerable.Repeat((byte)128, 256).ToArray();
        byte[] payload = Encoding.ASCII.GetBytes(twoDimensional ? "LOT-0007" : "000123");
        var frame = new InputFrameRef(name+"-frame", 16, 16, PixelFormat.Gray8,
            "coord-v1", Convert.ToHexString(SHA256.HashData(pixels)).ToLowerInvariant());
        var imageFrame = new CoordinateFrame(name+"-pixels", CoordinateFrameKind.ImagePixels, "coord-v1");
        var domain = new SearchDomain("full", imageFrame, new SearchDomainShape.FullFrame(),
            new CoordinateTransform.Identity());
        var provider = slot.Own(new FixtureInputProvider(pixels, frame, domain));
        ModelParameter[] values = twoDimensional ? new ModelParameter[] {
            new ModelParameter.PositiveDouble(ModelParameterKey.ModuleSizeMin, 2),
            new ModelParameter.PositiveDouble(ModelParameterKey.ModuleSizeMax, 8),
            new ModelParameter.Integer(ModelParameterKey.StopAfterResultCount, 4),
            new ModelParameter.Persistence(ModelParameterKey.Persistence, PersistenceMode.Persistent),
            new ModelParameter.Polarity(ModelParameterKey.Polarity, PolarityValue.DarkOnLight),
            new ModelParameter.Mirrored(ModelParameterKey.Mirrored, MirrorMode.No),
            new ModelParameter.Encoding(ModelParameterKey.StringEncoding, BarcodeEncoding.Utf8),
            new ModelParameter.Boolean(ModelParameterKey.PreserveUndecodedCandidates, true)
        } : new ModelParameter[] {
            new ModelParameter.PositiveDouble(ModelParameterKey.ElementSizeMin, 1),
            new ModelParameter.PositiveDouble(ModelParameterKey.ElementSizeMax, 8),
            new ModelParameter.Integer(ModelParameterKey.NumScanlines, 0),
            new ModelParameter.NonNegativeDouble(ModelParameterKey.OrientationToleranceRadians, 0),
            new ModelParameter.Integer(ModelParameterKey.StopAfterResultCount, 0),
            new ModelParameter.Persistence(ModelParameterKey.Persistence, PersistenceMode.Persistent)
        };
        var parameters = new ModelParameters(name+"-params-v1", values, null);
        var budget = new ResourceBudget(1000, 256, 1048576, 4, 256, 256, 0, 65536);
        var attempt = new BarcodeAttempt("normal", symbology, domain, parameters,
            new DerivedInputPlan(DerivedInputKind.Original), AttemptPurpose.ProductionDecode,
            1000, AttemptStopRule.AfterAttempt);
        var request = new BarcodeRequest(id, frame, provider, domain, new[] { symbology },
            parameters, new EncodingPolicy(EncodingPolicyKind.PreserveRawOnly, Array.Empty<BarcodeEncoding>()),
            new QualityRequest(false, null, null, Array.Empty<string>(), null),
            new AttemptPlan(new[] { attempt }, 1), budget, new TraceContext(name+"-trace", "fixture-v1"));
        var geometry = new GeometryEvidence(GeometryKind.Symbol, imageFrame, imageFrame,
            new CoordinateTransform.Identity(),
            new SearchDomainShape.AxisAlignedRectangle(new PixelPoint(2, 2), new PositivePixelSize(12, 12)),
            GeometrySource.BackendRegion);
        var candidates = new CandidateEvidence(CandidateCompleteness.Complete, CandidateStopReason.Exhausted,
            new[] { new BarcodeCandidate("template/c0", CandidateDecodeState.Decoded,
                geometry, "template/o0", "Simulator") });
        var evidence = new AttemptEvidence("normal", 0, "sim-model-v1", frame.PixelSha256,
            domain.DomainId, parameters.Revision, AttemptPurpose.ProductionDecode, AttemptEnd.Completed, 0, 0, 0);
        var observation = new BarcodeObservation("template/o0", id, ObservationState.Decoded,
            new SymbologyInfo(symbology, symbology, null, false),
            new RawPayload(RawAvailability.Available, payload, payload.Length, PayloadUnit.Bytes,
                BarcodeEncoding.Utf8, new EciAssignment(null, false), new Gs1Fnc1Marker(false, false),
                PayloadSource.BackendBytes),
            new EngineText(null, false, PayloadSource.Unknown), geometry, candidates,
            Array.Empty<QualityMetric>(), evidence,
            new AdapterEvidence("barcode-simulator-v1", "sim-v1", "not-used", BackendEvidence.Simulator),
            Array.Empty<BarcodeIssue>());
        var decoder = slot.Own(new SimulatorDecoderAdapter(new BarcodeSimulatorScenario(
            new BarcodeAdapterAttempt(new[] { observation }, candidates, Array.Empty<BarcodeIssue>(),
                evidence, true, "barcode-simulator-v1"), false, false)));
        var profile = new BarcodeReaderProfile(name+"-reader-v1", 1, 2, 8, 1, 4, 32,
            262144, 4194304, 1048576, 500);
        var reader = slot.Own<IBarcodeReader>(new BarcodeReader(profile));
        slot.Own(request); // reader执行前已经强持Input/provider/域/参数/预算/身份
        return slot.Own(new Fixture(reader, decoder, provider, request, imageFrame));
    }
}
```

Asset=null 是上述新建解码模型的明确输入，不把未知训练模型填成空 bytes。真实 HALCON 切片公开 `Asun.Modules.Barcode.Halcon.HalconBarcodeDecoderAdapter(BarcodeReaderProfile profile, BarcodeAdapterCapabilities enabledCapabilities)`，实现 IBarcodeDecoderAdapter，构造纯校验/复制、无 native 工作；enabledCapabilities 来自该发布包已验证的码制目录（AdapterRevision 与版本固定、线程/并发界限按 §7.1），不从系统环境猜测“全部支持”。两实际 Host 可把已登记 Simulator 换成该构造并输入其已验证目录，不改 Core 参数/请求。训练构造仍按 §7.5 的 BarcodeTrainingAdapter(retentionProfile,workerOptions)，BaseModel/样本/真值/Golden 与授权显式传入 §3.3A，未提供真实资产时不得用合成灰图创建假训练成功；不扩大训练目标。

### 9.2 Factory 前有界根槽、原 Task 与确认接管

`BarcodeHostRoot` / `BarcodeHostSlot` / `BarcodeHostTask<T>` / `BarcodeHostHandoff` 全部是上述 Host 源文件中的 internal 类型，不发布通用进程框架，也不让 Core/其它 DLL 引用 Host。以下是唯一目标签名摘录（省略类实现体，不冒充已编译源码）；两无 UI Host 与两 STA Host 必须按这些签名/算法实现其同一测试根，不用日志或隐藏静态字典替代。

```csharp
internal sealed record BarcodeHostRootOptions(int MaxHosts, int MaxTasksPerHost,
    int CleanupReservedTasksPerHost, int MaxObjectsPerHost, long MaxBytesPerHost);
internal sealed record BarcodeHostHandoff(Guid RootId, Guid SlotId, long Revision, bool Accepted);
// BarcodeHostRoot(BarcodeHostRootOptions options, TimeProvider clock)
// BarcodeHostSlot Reserve(string hostId, Guid originalRequestId)
// bool HasPending { get; }
// IReadOnlyList<BarcodeHostSlot> Pending { get; }
// 根由Main/Application字段持有，不能实现自动Dispose/终结器强清槽。
// BarcodeHostSlot成员：
// void CloseBusinessAdmission() // 不封已预留cleanup槽
// T Own<T>(T instance) where T : class
// BarcodeHostTask<T> Start<T>(string role, Guid requestId, bool cleanup,
//     Func<Task<T>> start)
// BarcodeHostTask<bool> StartVoid(string role, Guid requestId, bool cleanup,
//     Func<Task> start)
// Task<T> ObserveAsync<T>(BarcodeHostTask<T> call, TimeSpan budget, CancellationToken waitToken)
// void SaveDecode(BarcodeExecutionReceipt receipt)
// void SaveTraining(BarcodeTrainingReceipt receipt)
// void RecordBusiness(Exception error)
// void RecordCleanup(string role, Exception error)
// BarcodeHostHandoff PromoteForRecovery()
// bool TryRetire(bool executionClosed, bool trainingClosed, bool displayDrained, int inputLeases)
// IBarcodeReader WrapReader(IBarcodeReader inner)
// IBarcodeTrainingAdapter WrapTraining(IBarcodeTrainingAdapter inner)
// Asun.Modules.Barcode.Wpf.IBarcodeImageFactory WrapImageFactory(
//     Asun.Modules.Barcode.Wpf.IBarcodeImageFactory inner) // 仅WPF Host源，Core.Tests不编译此成员
// WrapReader/WrapTraining/WrapImageFactory见§8.4，各返回原公开接口的登记代理。
// BarcodeHostTask<T>：Guid RequestId；string Role；Task<T> Original；
// IReadOnlyList<Exception> BusinessErrors/CleanupErrors在slot有界保存。
```

**预留。** Main 在任何 fixture/provider/reader/adapter/factory/Control 之前构造 `new BarcodeHostRoot(new BarcodeHostRootOptions(2,64,16,32,16777216), TimeProvider.System)`，为A/B各 Reserve(hostId,原RequestId)，根总引用预算≤33,554,432 bytes。MaxHosts=2、每槽最多64个原调用记录（其中16保底cleanup）、32对象槽、16MiB强持预算，计输入/深拷贝/结果/显示旧新代/原Task元数据/有界错误。验证 Host 每槽最多8次业务请求，超额明确拒绝且不发新执行；不淘汰未完任务/墓碑来维持无限刷新。Start/Own 先 checked 预检槽/额度，容量满抛 InvalidOperationException 且委托调用0次；Reserve 在同一锁占完整配额，空名/空ID/重复宿主拒绝。对象槽不足在对象纯构造前预留其 Own 位置；本页各 constructor 纯托管失败没有外部资源，实际 Factory/Bind 的配额必须先占，不“先取得再发现登记满”。所有引用预算是宿主逻辑上限，实际 native/共享 backing仍按原 Owner 计费，不能拿 Host 空列表替代实际资源零。

根Options值全部正、MaxHosts≤1024、MaxTasksPerHost≤4096、16≤CleanupReservedTasksPerHost<MaxTasksPerHost、MaxObjectsPerHost≤4096、MaxBytesPerHost≤long.MaxValue/MaxHosts，非法constructor零动作抛ArgumentException。固定Host每槽计预留：reader托管≤4MiB、其结果账本≤256KiB、native借用≤1MiB、display≤1MiB、Host结果副本≤1MiB、64个调用记录及32对象引用/错误辅助≤1MiB，共8,650,752 bytes，低于16MiB。误以整份Profile额度加两次结果/每个引用重复计backing不得偷减真实占用；此数只证明本Host安全上限，不当native性能实测。错误列表每组≤16个ExceptionDispatchInfo+稳定诊断，超额置ErrorOverflow且保留首/最新有界摘要、停止业务准入，不无限堆错误。§8.4模块影像代理/WPF特有成员位于Wpf.Tests同名partial类扩展源，Core.Tests的共享Host源码无WPF using/引用。

CloseBusinessAdmission与Promote原子停止业务Start，已预留的cleanup/迟到接收/原查询仍可走恢复轴；Root满不新Reserve，无“无限恢复新任务”例外。成功TryRetire之后root保留每Host≤16KiB的最终退出摘要（原ID/退出码/错误码/资源确认），不保重资源、不能丢错误导致最终Main判0；退净后的未知原生产ID查询仍由该Host已持久回执Owner处理，测试内存不能宣称跨进程去重。

**调用与迟到。** Start 的(role,requestId)是本槽唯一键，重复只返回同一 BarcodeHostTask，不再次执行委托。先留调用/借用输入/cleanup位置，再调用一次 start 并立即保存原 Task，才允许 Observe；ValueTask 仅在该委托内 AsTask 一次，禁止重复消费。同步抛错保存为本调用失败Task及业务/cleanup错误，不回滚成“未发生”；异步 fault消耗其 Exception，但原 Task 仍强持。StartVoid既存原 void Task再保存完成映射，映射不替代原 Task。Observe 用有限 TimeSpan(1..600000ms)及单调时钟/Task.WaitAsync观察，超时/取消不取消登记或归还像素；原执行 token与wait token分开。根持有每个返回资源的原Task、完成接收路径和实际返回实例；provider Acquire成功但调用方观察已离开时，Core/display仍按原调用归还。工厂/Create与Dispatcher Bind在**交付前**先Own实际Session/Control；迟到创建/呈现按原RequestId/Generation登记，关门后不投影到新页，仍走同一有限cleanup，不另找第二Session。Completion接收只登记/记录，不在完成回调做无界Dispose或重新执行。

role含明确方法/发生序号，重复await/同一次cleanup继续用原role；新的一次只读Query仅在前次原Query已完成后取query/attempt1..3，不把已完成快照永远重用成最新，也不为未完Query堆新Task。不同方法/类型不得复用同key：冲突Start在调用前拒绝，业务Execute/Train每原ID至多一次，Query/cleanup递增的是**观察调用序号**而非业务身份。枚举MoveNext同样最多32个调用记录或对应预留事件上限，超过容量停止观察并转根恢复，不截断后宣称终态齐全。

**收尾三轴。** Decode用 reader.CloseAsync，Training用 CloseTrainingAsync（含原worker Job/pipe/副本/host lease），Display用 ImageSession.CloseAsync/Workbench.CloseImageAsync，各保留一次当前原关闭Task，观察预算各500ms、独立未链接业务取消的cleanup token；三者依次 try/catch/finally，前一 fault/到期也必须启动其余轴，不共享一个已取消token，不覆盖原业务Exception。500ms只保护首版Host观察，不宣称 native 恰在500ms退出。失败记录CleanupErrors，业务原异常用ExceptionDispatchInfo保留，不在finally throw/return掩盖它；退出码统一在finally之后确定（资源未知4，业务失败1，正常0）。Start原Close未结束时只能Observe同Task；原Close返回DrainUnknown以后才允许下一次500ms Close观察，新role=`cleanup-axis/attempt1..3`、仍同逻辑关闭/原身份，每轴最多3次自动观察；用完仍保留槽并暂停新准入。任一 lease.DisposeAsync 原Task也先登记、有限观察，未完成不能再Dispose，归还fault不认为ActiveLeases=0；无 await using/无期限Dispose/长sleep兜底。

**原身份和退槽。** 异常或观察到期只能 QueryOperationAsync(原RequestId)/QueryTrainingAsync(原TrainingRequestId)或 ReadEvents/ReadTrainingEvents按原游标；查询本身 Start并有界观察，pending Query不另开Query。Unknown保持事实未知，不生成新Request/TrainingId盲重跑/重训。reader/adapter内部账本强持模型/native原任务/输入租约；根强持reader/provider/训练adapter（因而原worker/Job/pipe及借用链），不能只留下错误字符串。SaveDecode/SaveTraining在本Host内存账本保存完整不可变回执，再ack精确终态序号；生产持久化另外由调用方已有事务Owner提供，提交未知不能ack。

底层Core/Training/display的每个Acquire/ExecuteAttempt/native/Drain/lease.Dispose原调用也必须先预留到各自operation账本，再保存原Task（ValueTask.AsTask一次）后有限等待；不因外层Execute有限返回而丢这些叶Task。每个Acquire最多一lease，晚到成功先登记lease再排空/归还；观察到期不另Acquire，归还在native/borrow真退出之后且原Dispose pending只续等。叶Task/lease数量受reader Profile、训练 §7.5 Samples/Golden/Blobs 和display MaxOverlays/单Present上限；接纳前按最坏调用链预留包括清理槽/bytes，零额度不调用端口。provider抛错、Dispose卡住/抛错分别形成原operation资源未知与诊断，不能把Task fault当释放回执。该规则是既有各账本实施义务，Core不引用Host根类型。

离栈前在最外finally调用 PromoteForRecovery：root锁内把**同一槽**从CallOwner改成ProcessRecoveryOwner，含原Task/全量对象/请求/结果/游标/错误/保留配额，递增revision并回传精确RootId/SlotId/revision Accepted=true；不移动到另一个未构造服务、不解除任何根引用、不伪称Drained。容量已在Reserve保留，正确实现此转交不需要临时争抢新槽；若内部转交异常/未确认，原槽仍保留且Main/Application不得退出，不能结束进程假装以后续等。真实退槽须同时：所有原执行/Query/Close/Dispose/Dispatcher/订阅Task与完成接收路径已退出、所有已接纳终态receipt复制/ack完成（接纳前Rejected仅存拒绝、不ack）、执行Closed、训练Closed（未构造时true）、显示Drained（无UI时true）、实际ActiveLeases=0、无仍被借用bytes/worker/句柄/视图。仅当这些可判定证明满足，TryRetire才删重引用/退配额，轻量已ack墓碑由reader生命周期规则保持到实例安全退出。Task fault/Window消失/转交ACK单独都不能满足该证明。

### 9.3 无 UI 正常、异常与恢复入口

完整入口构造先root、再Reserve、再fixture；这段接入代码依赖 §9.1/9.2 已精确定义的Host类型，非现有编译或运行证据。A/B各执行一次自己的请求，固定 GUID只用于该独立测试实例；同实例不能用它启动第二次。Main持有root直至两槽退净；有Pending时在有界恢复观察后返回给还活着的进程恢复循环，不从Main return/Environment.Exit，让未释放资源随进程消失。

```csharp
var root = new BarcodeHostRoot(new BarcodeHostRootOptions(2, 64, 16, 32, 16777216), TimeProvider.System);
var slotA = root.Reserve("label", Guid.Parse("11111111-1111-1111-1111-111111111111"));
var slotB = root.Reserve("logistics", Guid.Parse("22222222-2222-2222-2222-222222222222"));
// 每次调用都在RunHost自己的try内构造fixture，构造/Validate故障也必须进入finally。
await RunHost(slotA, Fixtures.CreateLabel);
await RunHost(slotB, Fixtures.CreateLogistics);
// 此处只在!root.HasPending且两Host结果正常时才能退出0；Pending保持进程恢复Owner。

static async Task RunHost(BarcodeHostSlot slot, Func<BarcodeHostSlot, Fixture> create)
{
    Fixture? fixture = null;
    bool executionClosed = false;
    try
    {
        fixture = create(slot);
        var request = fixture.Request;
        if (!fixture.Reader.Validate(request).IsValid) throw new InvalidOperationException("fixture invalid");
        var call = slot.Start("decode", request.RequestId, false,
            () => fixture.Reader.ExecuteAsync(request, fixture.Decoder).AsTask());
        var receipt = await slot.ObserveAsync(call, TimeSpan.FromMilliseconds(2000), CancellationToken.None);
        slot.SaveDecode(receipt); // 本Host内存持有完整回执，不写生产事实
        if (receipt.Acceptance != BarcodeAcceptanceState.Accepted || !receipt.ResourcesReleased
            || receipt.TerminalState != BarcodeTerminalState.CompletedWithReads
            || receipt.TerminalSequence is not long terminalSequence)
            throw new InvalidOperationException("fixture result incomplete");
        var ack = slot.Start("ack", request.RequestId, false,
            () => fixture.Reader.AcknowledgeAndReleaseAsync(request.RequestId, terminalSequence).AsTask());
        var acknowledged = await slot.ObserveAsync(ack, TimeSpan.FromMilliseconds(500), CancellationToken.None);
        if (acknowledged.State is not (BarcodeAcknowledgeState.Released or BarcodeAcknowledgeState.AlreadyReleased))
            throw new InvalidOperationException("fixture ack unknown");
    }
    catch (Exception error) { slot.RecordBusiness(error); }
    finally
    {
        try
        {
            if (fixture is not null)
            {
                var close = slot.Start("cleanup-decode/attempt1", fixture.Request.RequestId, true,
                    () => fixture.Reader.CloseAsync().AsTask());
                var closed = await slot.ObserveAsync(close, TimeSpan.FromMilliseconds(500), CancellationToken.None);
                executionClosed = closed.State == BarcodeCloseState.Closed;
            }
            else executionClosed = true; // 仅没有构造reader；部分已Own对象仍受TryRetire真实检查
        }
        catch (Exception error) { slot.RecordCleanup("decode", error); }
        finally
        {
            try
            {
                var transfer = slot.PromoteForRecovery(); // 原槽已在进程根持有，不临时搬走
                if (transfer.Accepted)
                    slot.TryRetire(executionClosed, true, true, fixture?.Provider.ActiveLeases ?? 0);
                else slot.RecordCleanup("handoff", new InvalidOperationException("host ownership not accepted"));
            }
            catch (Exception error) { slot.RecordCleanup("handoff", error); }
            // 未确认时根仍持有原CallOwner槽，进程入口阻止退出，不能finally抛覆盖业务错误。
        }
    }
}
```

RunHost catches只记录原业务错误，进程入口最后从slot汇总决定退出码，不在try return常量后让finally“修改退出码”。fixture未完成赋值但已Own部分对象时，TryRetire检查槽内对象类型/原调用而非只信示例bool；例如reader已构造而尾部fixture封装抛错，RecoveryOwner仍须取该Own reader执行原Close，不允许executionClosed=true清槽。实际转交机制为预留槽的同根CAS；转交实现故障是保留/阻止进程退出的宿主故障，不抛它覆盖原业务错误，入口记录两组错误并保留原槽。

恢复每轮只观察未结束的原Task或已经返回DrainUnknown的原关闭/原ID查询，轮间由用户明确恢复/正常事件唤醒，不无界轮询。迟到真实终态先Save同ID再精确ack，迟到Close真Closed且provider实际零才TryRetire；旧结果不写新UI。训练轴恢复保留TrainingRequestId、源NoRead完整回执与once账本，始终 QueryTraining/ReadTrainingEvents原ID，拒绝以更换TrainingId解决未知；显示按原session与Generation Close，不以新的窗口/Factory掩盖原lease。

## 10. 正常、边界和失败案例

| 场景 | 模块必须返回 | 禁止行为 |
|---|---|---|
| 1D `00 12`，引擎文本 `12` | raw 长度 2、前导零层次和派生文本分开 | 回编码成 `31 32` 或丢前导零 |
| 同一 ROI 两个不相交位置均为 `0012` | 两个 observation，各自几何/attempt | 按字符串去重为一个 |
| 同一位置两次读数冲突 | 两次观察、冲突原因、原顺序 | 按期待值、质量高低选胜者 |
| 一个成功码、一个不可解候选 | 成功读数 + candidate evidence + 未完成/歧义 | 只返回成功码并声称无其他码 |
| 2D handle `[41,7]` 与两字符串 | 按后端返回顺序绑定，不按 handle 数值排序 | 重排导致字符串错配 |
| `grade=-1`、`N/A`、growth `-0.2` | 保留原族、类型、状态和值 | 统一改为 0 或过滤负数 |
| 可解但缺标准/像素/静区条件 | `Decoded` + `Quality=MissingCondition/Unsupported` | 显示正式质量等级 |
| 增强图可读、原图质量不合格 | 增强观察标派生；原质量事实不变 | 用增强结果覆盖原质量 |
| timeout/abort 只返回一条 | 已返回证据 + 释放确认后的 `BudgetExceeded`/`Cancelled`；未确认排空则为非终态 `DrainUnknown` + 完整性未知 | 当作整图无其他码 |
| A 请求完成后 B 迟到 | B 带旧 request/epoch；宿主不覆盖 A | 以事件到达顺序改 UI/身份 |
| 模型清理失败或 OOM | 资源释放确认后为 `ResourceError`；未确认释放则为非终态 `DrainUnknown`，实例隔离，诊断可查 | 把实例放回池继续使用 |
| Structured Append 缺片/重复索引 | 保留每片原观察，合成状态 `Incomplete` | 自动拼接成完整身份 |

### 10.1 两种实施视角的反例（均为合成契约用例）

| 视角/输入 | 逐步结果与验收断言 |
|---|---|
| 实施者：同一图中 A 已解码、B 不可解；另位置 C 与 A 内容相同 | adapter 返回 A/C 两 Observation 与 A/B/C 三 Candidate，B.State=Undecoded；不按文本去重；Result.Attempts 保留三者，CompletedWithReads；Quality 未请求不填零分 |
| 实施者：零读数、两个候选、所有计划完整执行 | Observations 空、Attempts 的 Candidates 两项；CompletedWithCandidates、IsComplete=true；不压成无码。后端搜索不完整则 IsComplete=false/候选完整性 Unknown |
| 实施者：2D ResultHandles=[17,3]，strings=[A,B] | 用返回索引绑定而不是 handle 排序；17→A、3→B；handle 只在 adapter 内，返回稳定 opaque CandidateId，不暴露 native 可调用句柄 |
| 实施者：input 4×3 Gray16，StrideBytes=10，仅 27 bytes | 最低有效长度 28，provider 后验失败 BARCODE.INPUT.FORMAT；不越界读取。28 bytes 仍须显式 Gray16ScaleToGray8，否则拒绝转换；质量不在该派生图评级 |
| 集成人：观察者取消后重复 Execute 同一 RequestId | 后台 operation 保持；重复接纳拒绝 DUPLICATE，native 调用计数仍为一；Query/Read 返回原结果；只有精确终态序号 ack 才释放 payload |
| 集成人：两个线程同时接纳同一 ID，另两个不同 ID | 同 ID 恰一个接纳；不同 ID 使用独立模型，受最小并发/容量限制；完成观察与串行基线相同，无参数/epoch 串扰 |
| 集成人：Close 发生在 native find 中且超过 drain window | 停止接纳、取消意图一次；Close=DrainUnknown，原资源不归还、无终态；native 后来退出并真实释放才补发 Drained/ResourcesReleased/唯一终态；Close 不清空未 ack 结果 |
| 集成人：宿主保存终态后回执丢失/ack 序号错误 | 先查宿主持久回执；错误序号 ack=TerminalSequenceMismatch、payload 保留；准确重复 ack=AlreadyReleased，不重复提交事实 |
| 工程师：已 trained 的相同范围样本再次训练成功 | Before/After 数值相同合法；真值/读回/fresh read/Golden 仍检查，不为制造变化扩大范围；原活动模型不变，候选可标无新修订 |
| 操作员：NoRead 保底 worker 已隔离但未退出 | 显示资源状态未确认；Outcome=null、无可注册资产、无第二次训练；只有查询与诊断；不能以关闭控件消除原 operation |
| 空宿主：仅引用Core公开契约，持久化终态与raw bytes后ack，再构造原SourceDecodeEvidence | 摘要复算同值，RequestSnapshot完整且无provider；缺Receipt全文/hash/Asset则关联训练拒绝，不回查产品DB/隐藏Shell；升级新rule不重算旧回执 |
| 空宿主：参数Values重排、TraceContext不同、candidate数组顺序不同 | 参数摘要不变；TraceContext或candidate顺序改变回执摘要；null/空、非法Unicode/NaN有明确定义；不同独立运行耗时可导致摘要不同，不宣称语义等价 |
| 并发失败：worker1误读又deadline，worker2正常返回；worker1宿主lease Dispose失败 | worker1 DrainUnknown，无terminal/asset；worker2独立释放并完成，不被共享Job/pipe误杀；worker1恢复真实归还后按ResourceError优先，仍保留误读/deadline原因 |
| 并发失败：取消与最后ResultReady争用，完成后才Cancel | 锁内取消先接受且阻止继续则归约取消/更高原因；执行封存先发生则ExecutionSealed，清理完成后保留Completed*；不能用墙钟/观察者取消推断 |
| 传输失败：ResultManifest到达但输出chunk hash错/Drained缺失/worker退出 | 不接纳候选资产，复制合法诊断，终止/等待退出并真实归还lease；两门缺一DrainUnknown，无重新启动；退出已确认且释放成功按结构/transport原因归约 |
| 集成人：升级版本回放 raw 或质量 label 不同 | 保留两套带版本结果，阻断新 manifest 切换；对原 ID 查询，不用新版本覆盖旧事实；按旧包/旧模型回退 |

## 11. 第二轮场景驱动复审

下表重新按反例推导每条运行链。每行必须能从输入、参数来源、处理顺序和结果状态闭合到恢复动作；未满足断言即保持 `DesignReview`，不得以“有读数”代替验收。

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态和错误 | 恢复动作 | 可判定验收 |
|---|---|---|---|---|---|
| 正常配置/执行 | 完整帧、合法 ROI、已发布 manifest、白名单码制、有限预算 | `Validate` → 能力查询 → 模型租约 → find → 复制所有返回 → 可选质量 → 清理 | `CompletedWithReads`；质量独立为 `Measured/NotRequested` | 仅按调用方业务继续；模块不提交身份 | 同一输入/版本回放时 raw、索引、码制和状态一致 |
| 空输入 | null/空图、零宽高、空 domain | `Validate` 在接纳前拒绝，不创建 operation 或 native 模型 | `Acceptance=Rejected`，含 `BARCODE.INPUT.EMPTY/FORMAT`；事件入口只发一条 `BarcodeRequestRejected` | 调用方提供新帧；不重试同一引用 | 无 native 分配、`AttemptStarted`、结果事件、资源释放事件或终态事件 |
| 部分成功 | D 个目标中只有 k 个成功，另有不可解候选或超时 | 固定 D；复制成功和不可解候选；检查 abort/预算 | `CompletedWithReads` 或 `CompletedWithCandidates`；完整性 `Unknown` | 由应用决定重采/人工；模块不删除 D-k | D、k、候选和终止原因都可查询，k 不被改写为 D |
| 歧义/错误输入 | 两个相同内容位置、同位置冲突、tuple/handle 错长、ROI 截断 | 保留物理观察；在绑定点核 cardinality；错误不左移 | 双观察或 `ResultFormatError` + `BARCODE.RESULT.CARDINALITY` | 隔离请求/模型，按原输入诊断；不择优、不补空串 | 内容相同仍有两个位置；错长请求无“成功”结果 |
| 超大输入 | 超大图、多 tile、派生像素可能超过预算 | 先做尺寸/整数溢出和容量估算；按批准 tile 顺序处理；每 tile 单独租约 | `BudgetExceeded` 或分片结果带 `Completeness=Unknown` | 调用方缩小 ROI/分批；不能静默降采样后给质量通过 | 峰值内存和累计像素不超过预算；未处理 tile 显式可见 |
| 高并发 | N 个请求、同码制、同模型 manifest | 每请求独立适配器/模型租约；限流队列；禁止共享可变 native handle | 接纳前容量已满返回 `Acceptance=Rejected` + `BARCODE.OPERATION.CAPACITY`；已接纳 operation 超预算/资源故障才分别为 `BudgetExceeded`/`ResourceError` | 背压、拒绝新请求、隔离不健康实例；不跨请求重用结果 | 并发结果与串行基线逐项一致；无 epoch/参数串扰 |
| 噪声/遮挡/退化 | 原图质量前置低、局部遮挡、反光、模糊 | 记录前置缺陷 → 只执行冻结备用增强/极性/尺度 → 每次复制证据 → 原图质量单独评估 | 可读但质量 `MissingCondition`，或 `CompletedNoRead/WithCandidates` | 用完计划即停；由宿主决定重采；不循环直到期待值 | 增强观察带派生引用，不能覆盖原质量；每次尝试可重放 |
| 训练候选 | Core 无训练输入；宿主使用独立 `BarcodeTrainingRequest`、固定样本、训练授权和独立预算 | Training Adapter 按本指导执行一次 pass、read-back、候选 fresh read、Golden 和隔离回退；不调用 Core request 以改变其结果 | 独立训练回执，不混入 decode observation/operation；活动模型/参数保持不变 | 正常 NoRead 可形成隔离候选；失败、取消或无法硬停分别返回确定 outcome/state，宿主不得注册或放行 | 训练 operation 与 decode operation 可按源 RequestId 关联但状态、epoch、资源和幂等完全独立 |
| 取消/超时/native 排空 | queue、find、result query、cleanup 任一阶段收到 token/deadline | 发停止意图 → `Draining` → 复制可安全结果 → `Drained` → `ResourcesReleased` → 唯一终态 | 释放确认后按 §5.3 为 Cancelled/BudgetExceeded 或更高错误；未确认排空时为非终态 `DrainUnknown` | 等待真实资源归还；超窗隔离实例；不得提前 clear | 取消期间无 use-after-free；迟到事件不能覆盖新 epoch；终态必在资源释放后 |
| 资源上限/OOM | 候选、raw、quality tuple 或 native memory 达上限 | 每阶段检查额度；超额立即停止新消费者并保留已复制部分 | 资源释放确认后为 `ResourceError`/`BudgetExceeded`，否则为非终态 `DrainUnknown`，完整性未知 | 丢弃未复制诊断、隔离实例、保留健康模型；不能截断冒充完整 | 资源释放可观测；下一个请求不读到上个请求结果 |
| 持久化/修订 | 模型文件、参数 manifest、质量标准或 adapter 版本变化 | 读入临时实例 → 校验 hash/版本 → 查询并读回关键参数 → Golden replay → 切换 epoch | 通过后模型租约标记 `Prepared`；读回/Golden 失败为 `BARCODE.MODEL.CONFIGURE`，若清理/释放未确认则保持 `DrainUnknown` | 保留旧 epoch；新实例销毁；禁止半加载模型进入池 | 文件 hash 相同也记录运行版本；切换前后旧结果不被覆盖 |
| 升级/回退 | Core/adapter/HALCON 版本或契约主版本变化 | Replay/Shadow 双跑 → 比较 raw/cardinality/status/quality → 明确切换点 | 差异进入升级阻断；回退沿原 request 查询 | 停止新提交，切旧包；不得用新版本重读覆盖旧事实 | 回退后旧 Golden 与旧状态一致；差异有可追溯 manifest |
| 无 UI 调用 | 最小 console/service 宿主、无 `Window`/ViewModel | `Validate` + `ExecuteAsync`/事件流；宿主自己保存 replay 引用 | 只返回不可变结果和诊断事件 | 宿主处理身份/业务；模块不要求隐藏 UI 初始化 | 删除 UI 依赖仍可构建/运行契约测试 |
| 可选 UI | WPF 宿主、三语资源、1920×1080 | UI 调同一 Validate 和异步执行入口（`ExecuteAsync` 或 `ExecuteEventsAsync`）；显示 raw/派生层和状态；取消等待排空 | 投影 `ResultReady`；无“放行/提交/期待值重试” | 控件 Unloaded 撤observer并发起显示Close，保留未排空Owner；宿主分别关闭执行/显示并处理排空；错误显示恢复动作 | 键盘/语言切换不改输入或 payload；无第二事实 |
| 第二消费者 | 物流标签/箱码工具，独立 Profile、身份和资源 | 仅复用 Core/adapter；按自身目标与 attempt 调用 | 同一状态/错误/raw 契约；物流应用自行解析 GS1 | 物流业务失败不改 Core；可独立回退 | 不引用本平台页面/私表，能独立回放和升级 |
| 长期运行 | 数小时/数万请求、周期换模型、诊断 sink 变慢 | 周期健康检查、租约计数、队列背压、定期 manifest 轮换；诊断异步限流 | 无泄漏；sink 故障只丢诊断，不改结果；健康状态可查询 | 重建不健康实例；保留最近错误和水位；不自动重置业务事实 | soak 后 native/托管内存回到基线附近，句柄/租约计数归零，迟到事件可归属 |

### 11.1 第二轮复审结论

- **正常链闭合**：参数只来自 Profile/manifest/后端能力查询，请求冻结后按单一租约执行，结果复制后才脱离 native。
- **失败不降级**：空输入、错长、部分成功、候选截断、质量缺条件、取消未排空和作用范围未知都有显式状态；均不得生成 PASS、身份或设备命令。
- **算法路线具体**：1D 使用 cv2 的 `find_bar_code` 与对应结果查询；2D 使用 cv2 的 `find_data_code_2d` 与真实 candidate handle 查询；搜索备用只来自冻结 `AttemptPlan`。Core v0.2 是 decode-only；训练由本指导冻结的独立 Training Adapter 路线承载，具体 C# 类型/重载/封送有歧义时核实公共签名。
- **长期运行闭环**：限流、epoch、健康实例、租约计数、诊断背压和 soak 验收均属于模块运行时职责；业务事实仍由宿主持有。

### 11.2 DZ-XVision 场景吸收与边界

本节把 `DZ-XVision` 只读快照中的现场链路转译为本模块可验证的场景约束。快照是旧 `.NET Framework 4.7.2 WinForms` 项目，使用旧版 AsunImage/DevExpress；下列内容区分“现场观察”“平台推断”和“未验证”，不改变本页既有 Owner、状态或错误码。

#### 11.2.1 统一 1D/2D 处理链

1D 和 2D 均按同一生命周期执行：

```text
输入帧/ROI
  → 图像预处理引用（可选派生帧）
  → 定位变换引用（可选坐标链）
  → ROI/搜索域校验
  → 码制模型解码（ImageLibDotNet.cv2 的 1D 或 2D 算子）
  → 复制原始结果、候选和区域证据
  → 写入有序诊断事件
  → 按排空状态清理 native 与派生资源
```

预处理和定位只产生带来源的只读引用，不修改调用方原图。1D 的 region/string 与 2D 的 XLD、opaque handle、结果 tuple 必须在同一结果租约内按返回顺序绑定；复制完成前不得释放图像或模型。该链路是对第 6 节的场景化约束，不允许宿主跳过结果复制直接保留 native 对象。

#### 11.2.2 有界尝试和参数保底

- 预处理、极性、尺度、定位和码制参数只能来自冻结的 `AttemptPlan`；每个尝试记录输入帧/派生帧、ROI、参数 hash、用途、序号和剩余预算。
- 预处理失败、定位失败、ROI 无效、后端异常和空结果分别记录；不能把它们压成同一 `CompletedNoRead` 或空字符串，也不能以异常消息替代结构化原因。
- 有限保底可以切换批准的 ROI、极性、尺度或独立模型实例；达到次数、时间、候选、内存或输出上限立即停止。
- 期待字符串、工单、板/包裹身份、MES 响应、结果数量或放行策略都不能追加尝试，也不能参与候选排序。旧项目中的固定内容比较留在应用层。
- 定位源不可用时返回 `PositionUnavailable` 或对应稳定错误；不得把总览图、上一次定位或应用缓存坐标冒充当前帧定位。

#### 11.2.3 区域证据和图像来源

每个观察至少区分以下区域引用：配置搜索域、定位后的实际搜索域、成功符号区域、不可解/错误候选区域、坐标变换链和来源帧。错误区域投影只能作为证据投影，必须标明是配置 ROI 推导还是后端返回区域；不能把它当作真实解码区域。

快照显示总览图用于显示/回放，视觉工具实际使用每个产品、每个点位的普通光或 UV 图像；点位缺图或 UV 数量不一致属于宿主输入完整性错误。模块只接收明确的 `InputFrameRef`，不读取产品总览图、私有数据库路径或应用当前选中点位。

#### 11.2.4 Unknown 和未读原因

结果和诊断至少能表达下列互斥或可组合原因；映射到现有顶层状态和稳定错误码时保留原始原因：

`InputMissing`、`PreprocessFailed`、`PositionUnavailable`、`DomainInvalid`、`NoCandidate`、`CandidateUndecoded`、`BackendError`、`Timeout`、`CancelledDraining`、`ResultFormatError`、`ResourceLimit`、`PersistenceLoadFailed`、`QualityUnavailable`。

`NoCandidate` 表示后端在批准搜索域内没有可见候选，不能宣称整帧没有码；`CandidateUndecoded` 表示存在候选但未成功解码；`CancelledDraining` 表示停止意图已发出但 native 尚未完成排空；`PersistenceLoadFailed` 表示模型/参数/版本清单未通过完整性检查。原因不可由 UI 文本反推，必须由结构化结果提供。

#### 11.2.5 结果日志分层

诊断事件和结果日志至少包含：`RequestId`、`AttemptId`、`ObservationId`、输入帧引用及 hash、配置/实际 ROI 引用、坐标变换摘要、尝试序号、参数/模型/适配器版本及 hash、后端状态、raw/derived 标记、错误原因、阶段耗时、候选/结果计数、native/托管资源水位和排空耗时。日志是诊断证据，不是身份、质量或放行事实。

原始码字节、引擎字符串、派生文本、GS1/客户解析字段和质量结果必须分层保存。应用层可按权限保存 payload 或图像引用；模块默认只保存 hash/引用和必要摘要，不把 MES、工单或身份字段写入日志。结果日志写入失败不得改变已复制观察，也不得阻塞资源排空。

#### 11.2.6 持久化与回放

- 模型、参数、ROI、质量条件和适配器版本组成不可变 manifest；宿主写入采用临时文件、hash 校验后原子替换，模块不持有文件系统写入权限。宿主传入 ModelParameters.Asset 的 bytes/revision/hash，adapter 在临时实例中校验版本、hash 和关键参数读回，任一失败返回 `PersistenceLoadFailed`/`BARCODE.MODEL.CONFIGURE`，不得加载半成品。
- 每次回放保存输入帧引用、来源区域/变换、参数和模型 manifest、尝试顺序以及 raw/derived 结果来源；回放结果标记 `BackendEvidence=Replay`，不写生产事实。
- 不采用快照中的旧项目路径、INI/私有数据库、当前页面状态或结果上传结构作为 Core 契约；应用可在自己的适配层转换，但必须保留原始引用和版本。
- 总览图、普通光/UV 选择、产品/点位身份和 JSON 结果文件属于宿主投影；模块只提供可回放的观察和诊断数据。

#### 11.2.7 现场观察、平台推断和未验证

| 分类 | 本轮吸收 | 约束 |
|---|---|---|
| 现场观察 | `DZXVision.cs` 中存在图像预处理、SModel/NModel/Mark 定位、`deCode_Run`、1D/2D 结果遍历、空字符串失败分支、应用层日志/结果上传；`ToolBarCode.cs`/`ToolDataCode.cs` 支持 ROI、预处理、区域结果和错误区域投影；`ProductImageLayout.cs` 按产品/点位管理普通光与 UV 图像；`ProductResultStore.cs` 分开保存图像和 JSON；`CodeScanning.cs` 有线程、串口、`TON`/`NR` 未读响应及停止等待日志。 | 仅抽取输入完整性、区域证据、失败记录、来源和排空场景；身份、MES、页面、串口协议和上传仍由宿主/外部采集模块负责。 |
| 平台推断 | 上述链路可由 `AttemptPlan`、`InputFrameRef`、区域/坐标引用、结构化诊断和 `ResourcesReleased` 事件表达。 | 必须通过本模块契约测试和代表性 Golden 验证；不能把旧调用顺序视为新适配器 API。 |
| 未验证 | 快照不能证明 HALCON 26.05、当前 `ImageLibDotNet` 签名、线程/abort 语义、性能、质量等级或生产资格；也未验证旧路径的所有边界输入。 | 实现提交时按第 2、7、12、13 节重新核对；未验证项保持 `Unverified`，不得写成支持或通过。 |

## 12. 测试和验收矩阵

文档状态下以下是实施门，不是已通过结果。每条测试记录模块版本、后端版本、图像/模型资产 hash、输入参数、结果摘要、资源和耗时。验证工程的唯一执行方式、退出码及进程内外截止见附录 B.1；本矩阵不另选测试框架。

| 类别 | 最小场景 | 可判定断言 |
|---|---|---|
| 契约校验 | 空图、零尺寸、错格式、越界 ROI、非法 min/max、未知码制 | `Validate` 拒绝，错误码稳定，未创建 native 资源 |
| 原始保全 | NUL、前导零、非 UTF-8、Latin-1/UTF-8 派生、GS/FNC1/HRI | bytes、长度、编码、派生文本可逐层还原，语言切换不改 bytes |
| 1D 映射 | simple/复合、多个 region、候选与成功 region | 每个返回索引与实际字符串/类型/位置绑定，错长显式失败 |
| 2D 映射 | Data Matrix/QR/PDF417、opaque handles 非递增、可变结果 tuple | 不按 handle 排序；结果族和 label 逐项匹配；尾项不丢 |
| 码制边界 | 允许集、`auto`、PharmaCode 双值、GS1 变体、未知类型 | 能力目录明确支持/未验证/不支持；不称 auto 为全集 |
| 候选与分母 | 可解+不可解、同内容双位置、重叠/截断 ROI | 候选证据和固定目标分母保留；不做未批准去重/穷尽宣称 |
| 质量 | persistence 路线、`N/A`、`-1`、负 growth、DotCode 排除、SEMI 变长 | 按结果族保留原值和状态；质量缺失不抹掉解码 |
| 精确结果族/版本 | §7.6 的 15416/2016、15415/2024、29158/2025、SEMI/0701；未知合法label与错长 | 仅用手册精确族；未知label保原值并映Unknown，错长才FormatError；grade/raw值分开，版本不符Unsupported |
| 训练反例 | 空结果不抛异常、多结果/错码制、false decode、参数未变化、read-back/Golden 失败 | 空/非法/误读拒绝候选；参数未变化只记录；失败后剩余 NotRun；活动模型不变 |
| 训练 NoRead 保底 | 原 decode CompletedNoRead、宿主授权、同一冻结输入/码制、有限预算/隔离 worker 有效 | 独立 operation 一次 pass、每样本≤1、fresh read≤1；候选观察有训练标签；不返回持久资产、不修改原 NoRead/活动模型 |
| 训练取消/无法硬停 | train、验证或 fresh read 中取消、deadline、内存/样本预算超限；HALCON timeout 不能确认停止 | 可确认退出则 `Draining → Drained → ResourcesReleased → §5.3归约`；无法确认则 `DrainUnknown`，隔离 worker/lease/epoch，不注册、不重跑 |
| 取消/超时 | 排队中、native 运行中、查询中、清理中取消；deadline | 状态顺序正确；先排空再释放；迟到结果不覆盖新 epoch |
| 资源/并发 | 两独立请求、同模型切换、池实例污染、OOM/清理异常 | 无跨请求句柄/参数串扰；不健康实例隔离；资源最终可观测 |
| 回放 | 固定输入/参数/后端快照重放 | 输出与快照层次一致；标记 Replay，不写生产事实 |
| 两消费者 | 标签宿主和物流宿主各一条无 UI 链 | 同一核心 API 可接入；业务解析/身份/放行均留宿主 |
| 空Host/根Owner | §9.1–9.3 两自足构造、构造半途失败、Acquire/Execute/Query/ack/Close/Dispose挂起或fault、业务+cleanup双错、迟到lease/结果 | 根预留不足Factory/调用0次；保原Task/RequestId/borrow；三轴独立有限观察、业务错误不覆盖；确认接管不假Drained，所有实际Task/lease收敛才退槽 |
| STA装配/退出 | §8.4 Label/Logistics的Bind/语言/Closing/Unloaded/原Task回执 | 真实STA/Dispatcher/Workbench无Shell；同IDRun一次，三语不重执行；Probe明确不呈现；未知显示/worker保持根与Dispatcher，不Shutdown丢资源 |
| Viewport Assembly v0.2 | §8.5 Lifetime/同Control.Presentation/同binding/完整资源/Submission/原Task/晚到lease | null或错Owner无Acquire；重复Commit同Task；完整SourceCall/授权/上下文不丢；失败带lease先登记；同Owner Revoke→同ReturnId Return/Query；缺键保旧语言。§8.6/8.7已闭合桥接定义；实际实现或必需输入缺失仍记MissingInput/NotRun，不能靠Probe通过 |
| 真实视觉资格 | 每个批准码制的 Golden、损坏/模糊/反光/静区、标准件 | 仅在完成真实成像和标准程序后登记资格；文档不能代替现场验收 |

最小逻辑测试不得被描述为识别率、MSA 或生产通过。真实质量门需独立的标准件、照明/镜头/像素尺度、校准、Profile 和现场证据。

## 13. 性能、容量和可观测性

性能验收的统一 `BenchmarkProfile` 结构、nearest-rank 统计和失败样本处理按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 执行。本模块 decode Profile 必须冻结码制/图像尺寸与位深/通道、ROI 像素数、候选上限、模型与参数修订、冷建模或热执行、并发/队列负载、有限 deadline、候选/raw/派生像素/native 内存上限及阶段测点；Training Adapter 另有独立训练 Profile，必须冻结样本 hash、一次 pass、fresh-read 上限、worker/模型 epoch、资源上限和阶段测点，不得混入热解码分布。测点覆盖端到端接纳至 `ResourcesReleased`、排队、模型租用/创建、预处理、解码/训练、结果与质量复制、native 排空和输入 lease 归还。冷/热、码制、图像规模、Profile、后端和并发不同的样本分开统计；阈值只来自已采纳的消费者/客户 Profile，缺失时结果为 `NotEvaluated`。

结构化日志至少包含：`RequestId`、`AttemptId`、`ObservationId`、`modelEpoch`、模块版本、后端与 HALCON/AsunImage 版本、模型/参数 hash、输入帧 hash、域摘要、阶段、状态、错误码、候选/结果计数、质量族、耗时、内存、取消/超时标记。默认不记录完整 payload、敏感物流文本或图像；审计需要时由宿主按权限保存引用。

指标和事件是诊断投影，不能成为身份或质量事实。指标上报失败不得改变识别结果；诊断 sink 阻塞不得阻塞 native 资源排空。

### 13.1 可执行负载与测量步骤

BenchmarkProfile 是宿主/测试负载清单，不新增 Core 运行接口；以消费者采纳的不可变 record/配置承载，以下字段必须齐全，缺一不执行验收。计数/阈值为 Profile 输入，不由开发者从本页候选参数推导。

| 字段组 | 类型/约束 |
|---|---|
| ProfileId/Revision/Consumer/ThresholdSource | 非空字符串；阈值来源为批准文档/客户 Profile 引用；无来源诊断测量统一 NotEvaluated |
| Module/Adapter/Runtime/Assets | 版本及 SHA-256；包括 Core、HALCON/AsunImage、参数、模型、每帧有效像素、域、真值清单、机器 CPU/RAM/OS/电源模式 |
| Samples/Order/OutcomeTruth | 固定有序 case 清单；每项请求/输入/hash/期望结构状态；区分正常读数、NoRead、候选、格式错误、取消、预算、DrainUnknown；不按成功结果挑样本 |
| WarmupCount/MeasureCount/MinimumCompletedCount | 非负/正/正整数，MinimumCompletedCount≤MeasureCount；诊断与验收分别采纳，缺失不临时编造数量 |
| Mode/Concurrency/QueueDepth/ArrivalSchedule | 冷建模或热执行分开；并发≥1、队列≥0，固定到达顺序/间隔；受 reader/adapter 较小上限约束 |
| RequestBudget/ReaderProfile/TrainingProfile | 引用 §3/§4 精确值；训练另记 sample count、Golden count、worker 副本字节与启动/终止耗时 |
| Targets | 可空的 P50/P95/P99、取消到排空/归还、峰值 native/managed/private bytes、漏释放数/错误率；每一项独立有来源/单位；未知资源不得判通过 |

执行顺序：①验证 Profile 与资产 hash，建两个最小 Host 之一；②冷路径每个样本新建 adapter/model，热路径先按 WarmupCount 运行并真实 drain/ack；③按固定清单与到达计划执行 MeasureCount 个独立 ID，Stopwatch 单调时钟记接纳、排队、provider/转换、model、find、结果/质量复制、Draining、Drained、AdapterResourcesReleased、lease Dispose、ResourcesReleased、终态和 ack；④记录每项结构结果/错误/是否删失与资源终态，失败/NoRead 也保留；⑤依 DEV-GOV-010 唯一统计口径输出 n、P50/P95/P99 和另列失败/未排空项；⑥逐目标比较，任一资源释放未知为不得通过，目标缺失 NotEvaluated。结果写入现有测试/benchmark 输出，不为文档修订生成空报告。

资源采样使用 adapter 的受控计数及进程 private bytes/GC managed bytes；worker 与宿主分别计数，采样间隔由 Profile 冻结，同时记录已知分配峰值，不能把离散采样最大值冒充真实所有 native 峰值。取消用固定阶段触发，记录 cancel→native 返回→adapter 释放→lease 归还，不能只测 token 回调。路线比较仅在已授权代表图上用同一资产/真值比较原图完整 ROI 与批准派生/工程全域路线，记录误读/未读、端到端与资源；本页不预判哪条最快。主路线始终是批准 ROI/码制，广搜只作工程显式计划，比较结果不自动扩生产范围。

## 14. 版本、兼容、发布和回退

### 14.1 版本键

结果快照绑定：模块契约版本、Core/Adapter 版本、HALCON 26.05 运行时版本、AsunImage 程序集版本、码制/参数快照、模型资产 hash、质量标准/版本、输入帧/坐标引用和语言无关原始值。仅模型文件 hash 相同不等于运行行为相同；迁移需重跑代表 Golden。

契约采用向后兼容优先：新增字段可选并保留未知字段；不得重解释旧状态、错误码、raw 单位或质量 label。删除/改单位/改变默认码制须升主版本并提供双读/回退策略。适配器能力目录以 `Supported/Unverified/Unsupported` 分列，不因升级自动升格。

### 14.2 发布门

发布包包含 Core、获准适配器、公开依赖清单、契约/错误码版本、模型和参数 manifest、变更记录、许可证/NOTICE（若引入第三方）、回放 Golden、性能基线、已知限制和回退包。发布前至少完成：

1. API/Schema/状态/错误码兼容检查；
2. 1D、Data Matrix、QR 最小无 UI 链和字节/索引/取消/资源测试；
3. 来料标签宿主和物流宿主的第二消费者接入演练；
4. 真实视觉资格单独登记，不以模拟/单测替代；
5. 在 1920×1080 基线下（若交付 UI）完成三语布局与取消/错误恢复检查。

### 14.3 回退和迁移

宿主保留旧 Core/Adapter/模型/参数 manifest 及回放引用；升级先在 Replay/Shadow 运行，再按 Profile 切换。发现结果格式、raw、候选基数、质量族或资源行为变化时，停止新提交，按原 `RequestId` 查询回执，切回旧版本；不得用新版本重读覆盖旧事实。模型迁移需新 `modelEpoch`，旧 epoch 排空并保留原证据后再下线。

## 15. 第二消费者接入断言

第二消费者以物流标签/箱码工具为例，不共享本平台页面或数据库：

1. 只引用 Core 契约和 HALCON/AsunImage 适配器，显式注入自己的 `IBarcodeInputProvider`，提供 Profile、目标/attempt 身份和本地化资源。
2. 能在无生产 Shell 的最小宿主中通过异步执行入口调用，同一请求同时保留 raw/engine text/几何/质量状态。
3. 由物流应用解析 GS1、核对包装层级和提交业务事实；条码模块不接收订单期待值，不发送 MES 或设备命令。
4. 可用回放适配器验证取消、超时、错长、双位置和版本回退；真实设备/标签资格单独签核。
5. 物流宿主发生字段或政策差异时，通过自己的适配器和解析层处理，不改 Core、不复制第二套条码算法。

该断言成立后，本模块才可声称具备独立复用消费者；标签检测和本平台的页面、流程、质量规则仍各自负责。

## 16. 已知限制、待决项和自审

当前未完成或需 Contract Owner 决定的事项：

- AsunImage/DevExpress 是已确定依赖，不构成安装、兼容或许可证门。本模块尚未实现 native 异常映射、可观测资源水位、worker IPC 和需要时的 C# 类型/封送绑定；这些仅影响 HALCON/训练切片。
- 各客户 Profile 的码制白名单、像素尺度、标准版本、曝光/光照、质量接收等级、目标分母和真实节拍未提供；本页默认值不能替代这些事实。
- GS1 语法、ECI 词典、SEMI T10-0701、ISO 15415/15416/29158 的完整标准资格和测量链不由模块编造；正式评级需要标准件和实机证据。
- 多符号归属、跨帧/跨 tile 去重、Structured Append 拼装、物流/板身份冲突和无条码替代策略属于调用方/身份 Owner。
- 当前未运行 HALCON、AsunImage、ZXing、WPF、硬件、现场 Golden 或性能基准；本页不声称实现或生产通过。

自审断言：

- 本页只定义视觉观察、资源和适配边界，没有写入 PCB、SPI、AOI、点胶或涂覆判定。
- 期待值、身份、工艺解释、质量放行和设备副作用均明确留给调用方及原 Owner。
- 1D/2D 原始字节、候选基数、句柄顺序、特殊质量值、取消/超时/迟到结果和资源排空均有可判定语义。
- 无 UI 核心先于可选控件；UI 只是同一执行入口的投影，不建立隐藏事实。
- 文档状态按附录B.2分别记录：Core/Simulator六项规格已接收为 `ModuleCoreImplementationReady`，其余切片指导增量限定内容接收且保持 `PreparationIncomplete / NotReady`；研究、示例或 AsunControl旧代码均不描述为本模块实现。

2026-10-11只作两种有限内容走查：实现者按 §9.1正常构造→Validate/Execute/Save/ack→§9.3独立Close；在构造半途/原Task迟到/业务+cleanup双故障分支，§9.2仍保原槽/ID/borrow并确认移交，恢复不重执行。外部消费者只按 §9.1公开reader/Simulator/参数/provider和 §8.4完整Binding/坐标工厂/STA/三语/Closing装配，不需隐藏Shell或服务；Probe明确拒绝图像呈现，真实Viewer桥接和lease/fence另验。此结论是正文一致性走查，没有执行C#、UI或资源故障注入；六项状态与门见附录B.2。

### 16.1 全部批准范围的本轮自审与剩余资格（2026-10-12）

本轮在永久原会话完成BC-D1及BC-U1/U2/U3的**软件规格闭合与限定自审**；所需Viewport公开producer、ID选择及合法空更新已从原Owner唯一指导读到并消费，不再登记为待上游决定。没有创建工程、产品实现或测试代码；既有Core/Simulator v0.2接收保持，新增Core.Extensions/Model Profile/Supplemental Evidence、IPC v2与WPF Port v0.5均不自动扩展该接收范围。整模块仍不声明ImplementationSpecificationReady，受影响切片保持PreparationIncomplete / NotReady；会话登记状态由总控维护，本页不写共享登记、不等待总控代做模块内容审核。

| 批准能力 / 原欠账 | 本方已关闭的软件定义及唯一位置 | 准入与未执行资格 |
|---|---|---|
| Core输入/状态/事件/取消/ack/根及双无UI消费者 | §3～6/9/附录B；既有接收保持 | 只有此前Core/Simulator为ModuleCoreImplementationReady；未build/run |
| BC-D1：全码制专属配置、完整native快照、复合载荷 | §7.8；明确typed settings/适用域/标准baseline、独立准备与deserialize核值、扩展查询/两ack、原index关联、两个新摘要、受控训练v2和兼容 | 软件定义已关闭；Profile/Extensions/IPC v2仅本轮自审，未独立提升Ready；真实各码制/封送/Golden/native/worker资源门未执行 |
| 普通decode、质量、受控训练/NoRead一次保底、参数建议、Replay | §7.2/7.4～7.7；有限路由、质量族/版本/未知标签、建议stale/no-op确定 | 原受限接收保持，Replay增量不冒HALCON资格；真实样本/质量/训练/性能另验 |
| BC-U1：真实显示源公开装配 | §8.5/8.6；本方独占源及逐行Publish、显式SourceOptions/BindingId/逐帧PublishedBindingId、ViewportImageFrameSourceFactory.Create→Register→稳定Frames/Coordinates→Remove→Retire；双Host完整预算 | 生产者输入已到达，消费定义已关闭；源码/真实Viewer/原Read/Return/峰值/关闭未运行，Probe不代呈现 |
| BC-U2：指定结果高亮与聚焦 | §8.7；SelectOverlayObjectCommand/完整对象键/Context及代号，Focus=Applied且本次VisibleConfirmed才Selected；null与无几何保真 | 软件定义已关闭；重叠/旧代/事件回声/焦点与真实呈现断言待实现验证 |
| BC-U3：Clear→新Present | §8.7；Update空Context、EmptyTransition三轴/空画面/旧Remove及Retire确认后Cleared；同session后续Update，不再Attach/Bind | 软件定义已关闭；Clear未知拒新、撤权安全清屏、迟到恢复/资源与实际空画面未运行 |
| Workbench/双Host/三语/发布和第二消费者 | §8.1～8.4、§13～15/B；Port v0.5保存代理、原Task/两ack/根及1920×1080基线保持 | 真实WPF/UIA/键盘/三语/布局、持久化Owner接入、客户负载及生产集成未验 |

限定自审逐链回读：Prepare校验→创建→read-back/序列化→独立deserialize→清理→保存/ack；Profile精确索引→decode→同index组件→完整Supplement→宿主Envelope/两个ack；训练v2核Before/After→仅target变化→Candidate Profile或生产临时候选销毁；显示独立Acquire→Publish→Register/Attach或Update→原Read/scope/Return→Remove/Retire→同根Close；选择完整键/本次聚焦呈现；空Update→旧scope三轴及Blank确认→Remove/Retire→同session新Update。正常、拒绝、取消/观察超时、迟到、容量/摘要/版本错误和恢复均保原操作/Owner，不以新ID绕未知。

本次修正的自审矛盾已写回正文：RGB Interleaved不使用单通道ColorR，颜色次序只取Metadata.Channels；替换容量直接MaxSources=2；每帧登记ID独立于固定SourceId；灰度无统计使用显式手动格式LUT，不猜extrema；producer Remove与源Retire分轴；1D运行态参数分类和训练历史区分，2D find选项不经模型get；ApplyAsync实际返回ViewportResult、GetSnapshot同步观察；扩展Profile排序、完整保存及两个独立ack闭合。旧Core字段、事件与barcode-*-jcs-v1保持，不重算此前有效向量。

本页定向校验已通过：复用tools/validate_docs.py的targets规则核70处本地引用存在、代码围栏配对；新增公开record字段无重复、版本/旧欠账状态一致，Viewport producer/ID选择/EmptyTransition及Apply真实返回类型和image-frame通道规则对照一致。独立核RGB 256×256 tile为196608 bytes、16×16 Gray8为256 bytes、1920×1080双场景16WH下界为66355200 bytes（还须额外核tile/元数据/实际client，不宣称64MiB一定足够），标识在ulong/long上界仍≤128 UTF8。新增流程/反例已限定回读；收到上游0.3.5-prep完成通知后，仅按§20.5再核本方已采用的能力/回执字段/事件兼容，明确EventRaised新增enum分支及撤权空目标通知，不重做D1/U1/U2/U3正文或扩大其它消费者范围；只核本页，不运行仓库全审。C# build/run、HALCON/AsunImage、worker/Job、WPF/UIA、Golden、性能、HIL、质量/计量与现场均未执行；文档自审不冒充这些门通过。没有新建脚本、报告、证据清单、会话/fork/子代理，未给其它会话发消息，未修改共享文件或上游模块。

## 17. 依据和来源

### 17.1 PCBA-AOI 质量闭环与训练路线

只读复核 [一维码与二维码读码指导](../../references/project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/一维码与二维码读码开发指导.md) 后，本页冻结“主参数尝试 → 质量/候选诊断 → 宿主授权的独立训练/重建保底”的闭集顺序：

- 生产请求必须固定码制、ROI、尝试预算和输入帧 revision；Core 不接受训练计划，不静默修改 reader/model。
- 结果保留原始字节、解码文本、候选数量、质量分项和拒识原因，调用方再决定期待值核对、物流身份或质量放行。
- 一维码、二维码和质量评定失败分别表达；缺少质量标准时返回 `MissingCondition`/`NotRequested`，不能以成功解码推导印制质量 PASS。
- Training Adapter 必须检查空输出、记录参数变化、模型 hash、适用码制、隔离 epoch、一次 pass、fresh read、硬中断和 drain；本页冻结路线和验收边界，具体 C# 类型/重载/封送有歧义时才核对公共签名。

上述闭环来自跨项目经验，不迁入客户码制白名单、默认阈值、生产页面或 MES 规则。

- [`PKG-023_CodeReading`](../../shared-modules/packages/PKG-023_CodeReading.md)：模块范围、两个消费者和字节/质量边界。
- [`DEV-VIS-021B`](../../shared-modules/guidance/03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md)：HALCON 优先、结果保全、有限尝试、质量结果族和 1D/2D 反例。
- [`DEV-VIS-020`](<../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>)：Vision Contract、AsunImage 公共边界和 native 资源规则。
- [`PKG-037_Identity`](../../shared-modules/packages/PKG-037_Identity.md)：观察到身份解析的交接与冲突保全。
- [`INDEPENDENT-MODULE-ARCHITECTURE`](../INDEPENDENT-MODULE-ARCHITECTURE.md)：独立模块准入、契约、Owner、版本和目录约束。
- 仓库 [`halcon算子手册/operators`](../../../halcon算子手册/operators)：HALCON 26.05 operator reference；只作为算子行为核对依据，不视为 `ImageLibDotNet` 签名。
- 本轮训练语义直接核对 [`set_bar_code_param`](../../../halcon算子手册/operators/set_bar_code_param.html)、[`set_data_code_2d_param`](../../../halcon算子手册/operators/set_data_code_2d_param.html)、[`write_bar_code_model`](../../../halcon算子手册/operators/write_bar_code_model.html) 和 [`write_data_code_2d_model`](../../../halcon算子手册/operators/write_data_code_2d_model.html)：训练样本必须检查输出；无法读出时可为空且不抛异常；训练期间 timeout 可能被忽略/禁用；模型持久化只在隔离副本验证后由宿主注册。该证据冻结行为边界，不替代 `ImageLibDotNet` C# 签名核对。
- 只读参考：`../../references/project-snapshots/AsunControl/20261004/original/Vision_BarCode`、`Vision_DataCode` 及其中的历史调用资料。旧配置默认值、WinForms 控件、自动训练和多策略重试不是本模块批准 API；仅用于识别场景和需避免的边界。
- 只读现场快照入口：[`DZ-XVision/20261004/README.md`](../../references/project-snapshots/DZ-XVision/20261004/README.md)、[`source-manifest.json`](../../references/project-snapshots/DZ-XVision/20261004/source-manifest.json)；来源树 SHA-256：`a3649338762b234537d185d18496fcd438ba91eafd06b8d817ebee4c5a5ceae8`，捕获日期 `2026-10-04`。相关文件包括 `original/DZ-XVision/DZXVision.cs`、`Tools/ToolBarCode.cs`、`Tools/ToolDataCode.cs`、`Runtime/BarcodeInbox.cs`、`Runtime/ProductImageLayout.cs`、`Runtime/ProductResultStore.cs`、`Runtime/ProductInspectionResultCollector.cs`、`Runtime/InspectionContexts.cs` 和 `CodeScanning.cs`。
- 快照的“现场观察/平台推断/未验证”边界见第 11.2.7 节：快照为旧 `.NET Framework 4.7.2 WinForms` 项目，引用 AsunImage 24.11、DevExpress 24.1 及设备/MES 依赖，仅用于提取场景和故障恢复经验；不证明本平台 .NET 10、HALCON 26.05、当前 AsunImage 公共签名、性能或生产资格，也不构成代码迁移授权。

### 17.2 固定源码与官方 UI API 依据

复用 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md) 已保留的 ZXing-C++ v3.1.1，commit `287c85df6f961c8efbfb5ffd736cd9457b8b890e`，Apache-2.0。实际读取下列固定源码/测试，而非依赖 README 或识别率宣传：

| 原件 | 本次可迁移结论与限制 |
|---|---|
| [ReadBarcode.cpp](../../references/open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/core/src/ReadBarcode.cpp) | 检查格式/空输入、有界图像金字塔、反相与结果数量停止；默认 tryHarder/Rotate/Invert/Downscale 较宽，按 maxSymbols 提前返回、按重叠过滤 error result，不证明完整候选。平台吸收显式尝试/预算与完整性语义，不复制隐藏搜索或去重 |
| [ODCode128ReaderTest.cpp](../../references/open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/test/unit/oned/ODCode128ReaderTest.cpp) | SymbologyIdentifier 中 plain/GS1/AIM、双 FNC1 与 HRI、ReaderInit/FNC3、ISO8859_1 用例证明文本投影与控制标记必须分层；仅迁移测试思想，不推断 HALCON 结果相同 |
| [TestReaderMain.cpp](../../references/open-source/zxing-cpp_zxing-cpp/287c85df6f961c8efbfb5ffd736cd9457b8b890e/test/blackbox/TestReaderMain.cpp) | 单图入口依环境设置 format/rotation/fast，并输出文本；不能作为本平台固定 Profile 或字节/ISO 质量证据；采用固定输入/参数清单替代隐式环境状态 |

ReadBarcode.cpp SHA-256 `3ebcb0d930512323dd9558653346d267c869c2acd255d922384529e6b9b852b6`，ODCode128ReaderTest.cpp SHA-256 `c9ea909704c680f41f48f0de44d3d0755268c194dd98ebe666dfd476575cd7f2`；完整来源/依赖 hash 沿用 REF-002，不另建 manifest。依赖核对为 C++20/Threads、可选 writer Zint 和测试 gtest；本任务不引入 ZXing 运行依赖。它不提供本模块认可的 ISO/DPM 评级，也不能替代 AsunImage。

本轮无可用 dxdocs MCP，已直接读取 DevExpress 官方 25.2 页面：[DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[GridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl?v=25.2)、[TableView](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TableView?v=25.2)、[PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)。依据限于 25.2 控件/程序集及 ItemsSource、View、SelectedObject、SuperTipControl 的公开用途；网站可能展示 25.2 后续补丁的包号，本项目固定使用已安装 25.2.3，不下载或升级。WPF 真实加载、布局、键盘和性能留对应切片验证。

2026-10-11 Host窄闭直接读取官方 [.NET 10 Task.WaitAsync](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0)、[ValueTask.AsTask](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1.astask?view=net-10.0)、[WPF ShutdownMode](https://learn.microsoft.com/en-us/dotnet/api/system.windows.application.shutdownmode?view=windowsdesktop-10.0)、[Window.Closing](https://learn.microsoft.com/en-us/dotnet/api/system.windows.window.closing?view=windowsdesktop-10.0)、[WPF Threading Model](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/advanced/threading-model)：WaitAsync返回等待Task可能不是原实例，超时异常只证明等待到期；AsTask只在首次消费处转换；OnExplicitShutdown须显式Shutdown；Closing可取消窗口关闭；Dispatcher原投递需异步观察，UI同步Task.Wait会死锁。这些只冻结原Task/有限观察/显式退出语义，不证明本文未实施的C#或WPF运行通过。Viewport当前上游§3.5/3.6/10.6已给公开端口/根Owner/UI绑定，按该唯一指导引用，不重审其算法。

## 附录 A：模块核心 API Contract v0.2（核心候选契约；逐切片准入）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.2` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- 适配器按 HALCON 26.05 手册实施并经 ImageLibDotNet.cv2 调用；具体 C# 类型/重载/封送歧义只阻断受影响适配器绑定切片，不阻断可替换的 Core、Simulator 和契约测试。
- 本附录不单独授予准入，实际逐切片接收见附录B.2。Core/Simulator已由主控按 DEV-GOV-010 §3.1 六项接收为 `ModuleCoreImplementationReady`；其它切片不因本附录存在、公开构造或指导限定内容接收而升格，仍保留对应实现/运行/集成与生产门。


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

## 附录 B：实施切片、最小宿主与六项门

本轮仅写本指导。以下是后续获准切片的唯一工程落点，不是创建授权或实现完成声明。一个模块仍在登记永久会话内由一个 Owner 串行推进；不得派生模块子会话。

| 切片/真实消费者 | 唯一代码工程（仓库相对路径） | 唯一验证工程与准入依赖 |
|---|---|---|
| Core + Simulator；标签/物流无 UI Host | src/Modules/barcode/Asun.Modules.Barcode.Core/Asun.Modules.Barcode.Core.csproj；net10.0，namespace Asun.Modules.Barcode | tests/Modules/barcode/Asun.Modules.Barcode.Core.Tests/Asun.Modules.Barcode.Core.Tests.csproj；provider/decoder 测试替身及最小 Host A/B 同工程，§10/§12/§13；无 WPF/HALCON/数据库 |
| HALCON decoder；标签读码 | src/Modules/barcode/Asun.Modules.Barcode.Halcon/Asun.Modules.Barcode.Halcon.csproj；net10.0-windows，namespace Asun.Modules.Barcode.Halcon | tests/Modules/barcode/Asun.Modules.Barcode.Halcon.Tests/Asun.Modules.Barcode.Halcon.Tests.csproj；引用 Core 与用户已有 AsunImage，真实输入/码制/质量映射 Golden 与资源门 |
| 独立训练与隔离 worker；工程离线/宿主 NoRead 保底 | src/Modules/barcode/Asun.Modules.Barcode.Training/Asun.Modules.Barcode.Training.csproj（net10.0-windows）；src/Modules/barcode/Asun.Modules.Barcode.Training.Worker/Asun.Modules.Barcode.Training.Worker.csproj（net10.0-windows exe） | tests/Modules/barcode/Asun.Modules.Barcode.Training.Tests/Asun.Modules.Barcode.Training.Tests.csproj；namespace 同工程名；引用 Core/Halcon；worker IPC、启动/硬停、模型 bytes 与结果传输按 §7.5 固定版本/消息布局/上限/访问控制实现并验证，不以线程取消替代 |
| 可选 WPF；标签/物流 Workbench | src/Modules/barcode/Asun.Modules.Barcode.Wpf/Asun.Modules.Barcode.Wpf.csproj；net10.0-windows，UseWPF=true | tests/Modules/barcode/Asun.Modules.Barcode.Wpf.Tests/Asun.Modules.Barcode.Wpf.Tests.csproj；引用受测 Wpf/Core、本机 DevExpress 25.2.3及image-frame Core/Resources、Viewport Core/Wpf/ImageFrame公开包；§8.4两个STA Host编译链接§9.1/9.2同源夹具与WPF代理扩展；生产影像桥按上游当前公開Viewport端口，Probe不代真实Viewer；宿主注入decoder/可选训练；无训练时完整可用 |

依赖方向为 Wpf→Core/Viewport Core/Wpf/ImageFrame/image-frame Core/Resources、Training→Core/Halcon、Worker→Core/Halcon、Halcon→Core/AsunImage；Core 不反向引用任何实现或 UI。可选 DLL 按切片独立构建/测试/版本/发布，不将 worker exe 描述为 DLL。禁止写其它模块、产品工程、原件、AsunImage 内部及共享登记/入口；产品接入单独批准。现有工程如与该落点冲突先由主任务确认，不能覆盖或删除用户代码。

最小 Host A（标签）与 Host B（物流）的唯一自足输入/公开Simulator、provider、reader/参数/预算构造及有限收尾在 §9.1–9.3；同源供 §8.4 两STA Host引用，不在附录复制第二个形状。固定合成例与真实码制/质量/模型资格严格分开。无产品页、Shell/DB或第二业务模块才能运行的隐藏前置。

### B.1 唯一验证入口与有限截止

沿用 DEV-GOV-010 §3.1 的 BCL Exe 约定。四个验证工程均为 Microsoft.NET.Sdk、OutputType=Exe、Nullable/ImplicitUsings=enable，不引入测试 NuGet 包，也不把框架选择留到首次开发。Core.Tests 为 net10.0，仅引用受测 Core 与 BCL；Halcon.Tests/Training.Tests 为 net10.0-windows，引用对应受测工程及已确定的依赖；Wpf.Tests 为 net10.0-windows、UseWPF=true，STA 入口运行真实 Dispatcher，异步完成后显式退出 Dispatcher。断言由 BCL 实现，Core 的时间/取消/并发用固定时钟和可控异步闩锁，不用长 sleep 推测调度。`dotnet test` 不执行这些 Exe，其无报错不能代替下列 run。

以下命令在仓库根执行，是获准实现后的验证计划；本轮未创建工程，也未执行构建或产品验证。每条命令独立监督，前一构建非零时停止对应 run，不继续宣称已测试。

```powershell
dotnet build src/Modules/barcode/Asun.Modules.Barcode.Core/Asun.Modules.Barcode.Core.csproj -c Release
dotnet run --project tests/Modules/barcode/Asun.Modules.Barcode.Core.Tests/Asun.Modules.Barcode.Core.Tests.csproj -c Release
```

```powershell
dotnet build src/Modules/barcode/Asun.Modules.Barcode.Halcon/Asun.Modules.Barcode.Halcon.csproj -c Release
dotnet run --project tests/Modules/barcode/Asun.Modules.Barcode.Halcon.Tests/Asun.Modules.Barcode.Halcon.Tests.csproj -c Release
```

```powershell
dotnet build src/Modules/barcode/Asun.Modules.Barcode.Training/Asun.Modules.Barcode.Training.csproj -c Release
dotnet build src/Modules/barcode/Asun.Modules.Barcode.Training.Worker/Asun.Modules.Barcode.Training.Worker.csproj -c Release
dotnet run --project tests/Modules/barcode/Asun.Modules.Barcode.Training.Tests/Asun.Modules.Barcode.Training.Tests.csproj -c Release
```

```powershell
dotnet build src/Modules/barcode/Asun.Modules.Barcode.Wpf/Asun.Modules.Barcode.Wpf.csproj -c Release
dotnet run --project tests/Modules/barcode/Asun.Modules.Barcode.Wpf.Tests/Asun.Modules.Barcode.Wpf.Tests.csproj -c Release
```

无参数入口执行该工程绑定的全部必需场景，不能只跑一个正常样例。Core 覆盖 §10.1/12 的纯值、摘要、状态、异常、并发/取消/ack/关闭及两无 UI Host；Halcon 覆盖 §7/12 的真实 decoder/质量/raw/几何/资源与批准 Golden；Training 覆盖 §4.1/5.3/7.4.1/7.5/12 的真实 worker IPC、身份/限额/完整性/退出/Job/lease 和训练读回/Golden；Wpf 覆盖 §8 的两外部 Host、影像端口正常/失败/迟到/关闭、独立 display lease，以及真实 WPF、键盘/UIA、三语、1920×1080 和公共 Viewer 呈现。必需场景均以 `BARCODE.<CORE|HALCON|TRAINING|WPF>.<章节>.<场景名>` 稳定唯一 ID 列入入口的固定清单，输出逐项 Passed/Failed/TimedOut/MissingInput/NotRun 及汇总；清单与实际完成 ID 集合精确相等且全部 Passed、资源确认归还才退出 0。

退出码固定：1=断言/未处理异常，2=用例或套件截止，3=必需输入/批准 Profile/Golden/真实适配缺失或必需项未运行，4=测试自有资源未确认排空；同时存在时优先 4、2、3、1。失败可继续不依赖它的场景，但未完成、跳过、fixture 缺失都不能退出 0。模拟端口断言与真实后端/Viewer 断言分别列 ID，模拟通过不能抵消真实项缺失；现场标准资格不属于软件 Exe 通过结论。Benchmark 复用 §13 已采纳 Profile 单独执行；未提供客户目标时记录 NotEvaluated，不把软件验证截止当性能合格阈值。

| 验证工程 | 单用例进程内截止 | 套件进程内总截止 | 外层 run 进程截止（含构建） |
|---|---|---|---|
| Core.Tests | 10 s | 120 s | 180 s |
| Halcon.Tests | 120 s | 900 s | 1020 s |
| Training.Tests | 180 s | 1200 s | 1320 s |
| Wpf.Tests | 30 s | 600 s | 720 s |

这些是首版软件验证保护预算，均用单调时钟，从各用例/套件开始计时，清理计入总截止；不是客户节拍或算法性能目标。每次独立 build 的外层截止为 300 s。入口对所有 await/闩锁设有限截止，超时不依赖被测 token 生效；触发后请求测试自有 operation 取消并在剩余预算内核对真实 drain，无法退出由外层处理。不得用 Task.WhenAny 的超时分支冒充被测任务结束。

外层执行者按上述命令用 .NET ProcessStartInfo（UseShellExecute=false、ArgumentList 分项、仓库根 WorkingDirectory）启动其独占子进程，异步排空 stdout/stderr，并用独立单调截止监督 WaitForExitAsync；不能只靠 harness 自己计时。超时固定记录 `BARCODE.<切片>.HARNESS.OUTER_TIMEOUT`、非零结果，调用该自有 Process.Kill(entireProcessTree:true)，另给 10 s 等待退出并核对已登记测试 worker 的退出/Job 零活动进程。监督者仅能终止本次测试拥有的进程树/§7.5 Job，不按进程名批量杀 HALCON/dotnet/其它宿主。杀进程异常或仍未确认退出记录资源未知并保留其 PID/Job/Owner 继续恢复；不能记录 PASS、释放仍被借用的像素、立即重跑或强制忘记资源。外层超时即使稍后退出 0 仍失败，run 未真实退出或输出缺必需 ID 也失败；正常结束原样检查 ExitCode 与完整汇总。本节只冻结监督行为，不新增公共进程模块、脚本或报告。

### B.2 逐切片六项内容结论

| 切片 | ①边界/消费者 | ②契约/状态/资源 | ③空宿主 | ④可判定异常/并发 | ⑤性能方法/阈值 | ⑥唯一落点 | 当前接收结论 |
|---|---|---|---|---|---|---|---|
| Core/Simulator | §1/2/15稳定 | §3/4/4.1/5.3、§9.2原Task/lease闭包 | §9.1/9.3两自足无UI构造 | §10.1/12、§9.2/9.3根容量/异常/迟到/确认移交 | §13方法固定，真实目标由消费者Profile采纳 | 本页顶部/附录B，§9测试源固定 | 2026-10-11主控接收六项文档规格：ModuleCoreImplementationReady；未创建工程、未实际build/run或资源故障验证，不代表运行/产品/生产准入；既有接收范围保持 |
| Core中的Replay增量 | §7.2只回放冻结case | §7.2公开构造/容量/全值匹配/Replay证据/原Task与Drain | 同§9.1两Host仅显式替换adapter并注入已保存完整case；不读外部路径 | §7.2/12/B.1同Core.Tests入口、错hash/域/参数/ID/取消/独立bytes | §13方法复用；回放计时不冒原HALCON性能 | 附录B同Core/Core.Tests，无新工程/测试框架 | 2026-10-12原会话增量规格自审；PreparationIncomplete / NotReady，不自动扩展2026-10-11 Core/Simulator接收范围；未实现/运行 |
| HALCON decoder | §2/7纯观察 | §7.1/7.4/7.6/7.8完整Profile/结果族/复合/资源、§9.1公开构造；BC-D1定义关闭 | §9.1同Host显式替换adapter，无Shell | §12 tuple/raw/质量/abort/释放、§9.2叶Task/Dispose | 同资产ROI/派生比较，阈值待Profile | 附录B Halcon/Test固定 | 2026-10-11公开构造/有限恢复指导增量限定内容接收，HALCON26.05路线保持；PreparationIncomplete / NotReady；真实C#封送、Golden、资源及性能未验证 |
| Training/Worker | §3.3A独立operation | §4.1/5.3/7.4.1/7.5/7.7/7.8冻结摘要、IPC v1/v2、完整Profile/硬停/建议 | §7.5构造/Request/Options，§9.2独立训练cleanup，无UI/DB | §12真值/取消/传输/Job/lease，§9.2同ID查询/原worker强持 | §13+IPC计数/Job/取消测点，客户目标待采纳 | 附录B Training/Worker/Test固定 | 2026-10-11公开构造/有限恢复指导增量限定内容接收，既有受控独立训练/NoRead一次保底保持；PreparationIncomplete / NotReady；真实封送、worker硬停/Job、lease归还、Golden及性能未验证 |
| 可选WPF | §8角色/宿主权限 | §8.2/8.2.1 Port v0.5、显式ImageFrame/扩展source、§8.4登记代理/§9.2根、§8.5～8.7 Assembly/producer/选择/Clear；BC-U1/U2/U3定义关闭 | §8.4两个STA完整Binding与同源§9.1，不依赖产品VM | §8.4/12/B.1语言/关闭/独立cleanup、迟到/lease/确认移交 | §8/13绑定/滚动/Dispatcher负载；不混native | 附录B Wpf/Test、§8.4 Host源 | 2026-10-11公开装配/根Owner指导限定内容接收；PreparationIncomplete / NotReady；Probe不能覆盖显示验收，真实Viewer桥接/呈现、WPF/UIA/三语/退出/布局与性能未验证 |

上表2026-10-11行保持已有内容接收结论；2026-10-12新增/修订是本原会话的规格自审，完整范围与未关闭责任以§16.1为准。六项不是编译/测试通过计数。仅此前Core/Simulator范围为ModuleCoreImplementationReady；Replay/Model Profile/Supplemental Evidence/IPC v2/Port v0.5等新增内容不自动扩展该接收范围。本轮不创建工程、不派发实现、不提升运行/生产资格，不等待总控代审模块内容。

整模块仍未取得ImplementationSpecificationReady或运行/生产准入；0.2.5-prep的BC-D1/BC-U1/U2/U3软件定义及本方限定自审已闭合，§16.1准确分开新增规格、既有接收和未执行运行门；不把这些新增自审自动标为Ready或整模块准入。此前已确认的解码、受控独立训练/NoRead一次保底与HALCON26.05路线保持。Core/Simulator规格接收不关闭真实封送、worker硬停/Job与lease归还、HALCON Golden/资源、Viewer桥接/呈现、WPF/UIA/三语/退出/布局、性能、质量标准或现场门。客户阈值、正式质量标准/成像与现场资格单列外部门，不把已决定的构造/cleanup/Owner语义转交客户；对应外部门不阻断无设备纯Core。共享文件/其它模块不在本轮允许范围。

仅外部事实/证据可关闭的门：消费者真实节拍/负载与阈值来源、固定生产/坏样本及合法真值、印制质量标准件/成像尺度/照明/计量资格、真实工况与现场验收。它们分别影响性能达标/码制资格/质量资格/生产集成，不要求为纯Core编造数值。真实worker退出/Job隔离/宿主lease归还、C#公共绑定编译、Golden执行和WPF验收是后续实现验证，不是未决定的IPC/摘要/终态工程设计；AsunImage/DevExpress安装、版本适配与授权不列为门。
