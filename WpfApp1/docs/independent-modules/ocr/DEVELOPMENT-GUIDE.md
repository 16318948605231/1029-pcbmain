# OCR 文字识别与 OCV 独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, C2-R, C3`

- 模块：`IM-028 / ocr`（来源 `PKG-024`）
- 文档状态：`DesignReview/Prep`（本文件是设计基线，不表示已实现、已测试或生产通过）
- 版本：`0.6.1-prep`；完整范围收口保持，2026-10-12仅补viewport 0.3.5消费接线；维护范围：本目录
- 主控内容复核：2026-10-11，已回读0.5.0-prep增量并接收C2/C2-R的DEV-GOV-010 §3.1六项文档规格为ModuleCoreImplementationReady（仅规格准备）；2026-10-10的纯值C1/C3接收保持。H/W根槽与借用映射增量限定内容接收，原HALCON工厂/native排空/保存Unknown边界确认保持；未授整H/W、I/P或生产准入。
- 技术基线：C#、.NET 10；视觉后端优先 HALCON 26.05，经 `ImageLibDotNet` 公共接口适配
- 规划消费者：丝印文字工具、标签文字工具、字符质量/工程工具。至少两个消费者必须在集成阶段使用同一核心契约完成接入验收。

本模块提供文字区域检测、文字识读、候选排序、原读证据和独立字形核对（OCV）原语。调用方拥有目标与任务身份、期待文本来源、工艺解释、目标关联、质量放行、复判、报告、持久化和设备动作。模块返回观察与证据，永远不把“读到了文字”转换成产品 PASS。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/ocr/Asun.Modules.Ocr.Core/Asun.Modules.Ocr.Core.csproj`；namespace：`Asun.Modules.Ocr`。预定测试工程：`tests/Modules/ocr/Asun.Modules.Ocr.Core.Tests/Asun.Modules.Ocr.Core.Tests.csproj`。上述项目尚未创建。
- 当前文档任务只允许修改本文件。未来 Core 获准后仅修改上述 Core/测试目录；HALCON/WPF 及其验证工程唯一落点见 §16.1，仍须逐切片授权，不在当前任务创建。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 整模块仍为 `PreparationIncomplete`。OCR-C1/C3纯值六项规格接收保持；主控于2026-10-11接收OCR-C2/C2-R六项文档规格，四个Core切片均为 `ModuleCoreImplementationReady`（仅规格准备）。H/W根槽与借用映射仅限定内容接收，整H/W及I/P资格保持各精确门。协议Empty/Refused不证明真实OCR准确率；精确范围见§16，不表示代码、运行或资格通过。

## 1. 职责、禁止边界与所有权

### 1.1 模块负责

1. 在明确的图像/ROI/有效域和方法快照上执行检测或识读。
2. 返回每个输入目标的原始字符串、候选、几何框、分数语义、支持域、拒识原因和版本谱系。
3. 对字形参考执行 OCV 比较，返回原生 Quality、是否可计算及证据；OCV 与内容识读是两个结果。
4. 管理本模块后端租约、模型快照、取消、超时、排空、资源释放和诊断事件。
5. 提供离线ROI候选和有限参数比较建议，不改生产配方。
6. 以稳定错误码和状态机表达无效输入、低信、歧义、资源不足、超时、取消和未知结果。

### 1.2 模块明确不负责

- 不读取或生成 BOM、PCB/PCBA 对象、元件身份、工单、面别、坐标目标、期待字符串或制程规则。
- 不决定字符是否缺陷、标签是否合格、质量是否放行、是否返修、是否重拍或是否触发设备。
- 不将期待值、字典或历史结果注入识别解码；期待值只能在调用方的独立比较步骤进入。
- 不拥有数据库、产品 ViewModel、页面导航、全局语言/主题状态、报告提交或 `MachineDecision`。
- 不把条码解码、尺寸计量、位置偏移、完整性/缺笔判定伪装成 OCR；不以 OCR 结果替代 OCV。
- 不公开 HALCON 句柄、`HTuple`、Paddle Tensor、Python 对象或 SDK 地址给核心调用者。
- 不扫描、修改或优化 AsunImage 内部；不假设未核对的 HALCON/C# 签名。

事实所有权固定为：模块持有识读/OCV 观测和候选证据；调用方持有目标、期待、比较、工艺和质量事实；证据仓/提交模块持有持久事实。新模型/成像/识读参数必须创建新 operation；新期待只重做宿主比较，无需重跑 OCR，不能改写已封存结果。

### 1.3 完整批准能力与适用边界

本表覆盖IM-028“丝印、标签、字符和文本质量工具”的当前范围；不是只以已接收Core代替Adapter/UI设计。正文所称文本质量包括原读拒识/歧义、支持及独立OCV观察，工艺缺陷阈值与放行仍归消费者。

| 能力/真实使用场景 | 唯一执行路径 | 不适用或不能证明的结论 |
|---|---|---|
| 固定单字/字符序列、固定字库 | §2.3/8.2 MLP单区或分割序列，显式字高/极性/字符表、每位top-N与拒识 | 不把连接域自动当完整字符；无资格字体、粘连/断笔不能用期待补齐 |
| 单行、多行及未知文字区域 | Deep Recognition只接紧单词；Detection/Auto返回独立词框与line_index；传统TextModel按原行结果，§8.2 | 不拼接无行证据的任意段落，不跨tile补字；传统auto≥2字、manual≥3字 |
| 中/英/繁体及其它模型实际字符域 | Unicode scalar保序；语言只是UI资源，模型字表/Blank/mapping与资格另绑定，§2.2/3.6/8.2 | zh-CN/zh-TW/en-US UI不表示模型必会读三类文字；组合符、竖排、连写及双向排版只在真实模型资格内，首版不做Unicode重排/纠错 |
| 复杂背景、反光、点阵、倾斜 | 有资格Deep；传统manual显式imprinted/dotprint；固定DirectionDeg/ROI角；§8.2配置与拒识 | 无泛用去背景/去反光/OOD模型；未声明成像域不提交，不能高置信即PASS；180°/镜像不由alignment猜测 |
| 未知字、O/0、I/1与拒识 | 原native winner/top-N、字符域检查、低信与MLP拒识标记，§2/3/8.2 | 字表内错误高分不保证拒识；错误接受必须在留出集/H/P暴露，不补概率或假未知字检测 |
| 字形/印字质量 | §2.4/8.2 OCV good pattern独立推理，Quality与OCR结果并列 | 不以OCR读对排除缺笔；不以OCV数值授产品判定 |
| ROI与有限参数推荐 | §2.5/3.5/9.7；宿主冻结离散候选，同样本完整分母、资源/E2E约束，建议可解释且过期 | 不生产在线搜索/训练/静默Apply；缺Profile为NotEvaluated，无隐藏优化器 |
| 字库/模型生命周期、训练与推理 | §2.4/8.3/14；只消费exact封存资产，生产者训练/读回/挑战/发布与用途资格分权 | 不把训练放IOcrEngine，不根据新字符自动扩最后一层；外部Paddle仅固定来源对照，未批准不建生产后端 |
| 无UI服务、事件、证据控件与恢复 | §3～9/10；同Core、原任务根Owner、双消费者、三语/权限/图表联动与有限关闭 | 不依赖隐藏窗口；独立控件无产品导航、持久提交、设备或质量放行权 |

生产Profile由消费者在接入时冻结字体/脚本/字符集、样本尺寸/字高/方向、成像族、允许错读/拒识与OCV阈值、时延及资源目标。软件范围/方法与拒绝分支由本指导决定；未知物理值不以“后续选算法/控件/接口”掩盖内部设计欠账。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Ocr.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"不依赖隐藏窗口"，Core 在无 WPF 宿主中完整运行。

**Blazor/Web**：OCR 识别结果通过 gRPC/REST 查询；证据图像通过 HTTP Range 分片加载；浏览器不重新执行 OCR。

**AI 推理集成**：本模块保留专用 Deep OCR 能力（`ai-inference` §1 已明确"专用 Deep OCR 执行/文本语义仍归 OCR 能力"）；通用 ONNX 模型推理走 `ai-inference`。三态仲裁的 `NeedsSampling` 采样帧可包含 OCR 难例，由 `ai-dataset-governance` 处理。

**HALCON 双跑**：`find_text`/`get_textline` 与 PP-OCRv5（Apache-2.0，ONNX Runtime 推理）作为独立对照路线双跑；两路字符准确率逐测试集比对；PP-OCRv5 由 `ai-inference` 的 ONNX Runtime 推理，本模块不直接引入 PaddleOCR 依赖。

## 2. 依赖与算法路线

### 2.1 固定后端边界与选路

HALCON 26.05 的 operator set 经 `using ImageLibDotNet;` 和 `cv2` 调用，算子名不变。AsunImage 是已确定依赖，不再核验“是否包含某算子”，不另接 `HOperatorSet`、`MVTec.HalconDotNet` 或 `halcondotnet.dll`。只在具体 C# 参数类型、重载或封送有歧义时查公开签名或消费项目编译；不扫描封装内部。Core 不引用视觉程序集，独立适配器承担像素转换、算子调用和私有对象释放。

| 场景/前置 | 冻结路线 | 拒识与限制 |
|---|---|---|
| 紧裁单词、已发布识别模型 | Deep OCR `recognition` | 输入必须是 byte 的 1/3 通道；模型字符域、背景和 alignment 资格须匹配；不拼接任意多行 |
| 未知文字位置 | Deep OCR `detection` | 只返回框，不生成 RawText 或 Recognizing 阶段；检测不到仅为 Empty，不证明目标不存在 |
| 同图检测并识读 | Deep OCR `auto` | detection/recognition 证据分开；每输入图像一个结果 dictionary，不能按缺项左移 |
| 单字符、固定字符区域 | 明确分割后 `do_ocr_single_class_mlp`；批量 winner 可用 `do_ocr_multi_class_mlp` | 区域序列来自显式分割；单字符不走 `find_text` 主路；需要字符 top-N 时使用 single 路线 |
| 近水平文字行分割 | `create_text_model_reader` → `set_text_model_param` → `find_text` → 读取结果 | auto 至少 2 字符，manual 至少 3 字符；auto 绑定 CNN/MLP，manual 明确字高/字宽；不是任意布局检测器 |
| 已训练字形参考 | `traind_ocv_proj` 产生版本资产，推理 `do_ocv_simple` | 相对大小/形状应相近；`adaptAngle` 未实现，旋转必须是显式预处理；OCV 与 OCR 分开 |
| 批准的外部识读适配器 | 固定运行时、模型、字典和解码契约 | 仅离线对照/后续接入切片；PaddleOCR 不自动成为生产依赖 |

本地依据为 HALCON Operator Reference **26.05.0.0**，路径见 §17。路线由方法快照冻结，不根据期待字符串自动改选。`RoutePolicyId` 是引用和追溯身份，不是未定义的动态策略插件；每个 operation 只执行一个路线，备用/重试由宿主使用新 operation 编排并保留旧结果。

### 2.2 Deep OCR 原读、几何与字符候选

1. `auto/detection` 中单通道转三通道、缩放和补边；`recognition` 中三通道转单通道。转换、裁图、正反变换、合成像素和有效支持进入输入谱系。Gray16→byte 的范围、饱和和舍入必须来自 PreprocessProfile，不可照搬 Gray8 参数。
2. `words` 的 `row/col/phi/length1/length2` 是算子原输入坐标；`word_boxes_on_image` 是预处理图坐标，`word_boxes_on_score_maps` 又是另一域。适配器先保存域与变换，再统一为请求 Frame 坐标的四角 `PixelPoint`；HALCON row→Y、column→X、phi radians→度，不把不同域混用。
3. softmax confidence 未校准，只标 `EngineNative`，不同后端/模型不可直接比较。`recognition_num_char_candidates` 是字符位置 top-N，不是整词 top-N。Deep OCR 通常只产生一个 native word winner；不能笛卡尔组合字符候选冒称模型词候选。
4. `recognition_alphabet_internal` 首符号 Blank **U+2800**，不是普通空格。word 不输出 Blank，字符候选仍可能含它；字符计数排除 Blank 但保留普通空格。资产保存完整顺序、Blank和mapping。native推理原读路线要求实际HALCON alphabet mapping恒等；§3 ModelSnapshot.MappingId/MappedSymbols为原读之后的独立派生规则，不是修改native解码的请求。O→0、删除或其它非恒等mapping只能为带MappingId的派生观察。不能把已改写 word 反推为未经映射原读。
5. alphabet 长度变化会调整/随机初始化最后一层，必须重训并生成新资产；相同集合换顺序也不能当兼容更新。alignment 先读 `recognition_alignment_available`，资格需覆盖真实背景；它不是通用镜像/180°纠正。
6. detection 输入尺寸按官方 32 倍数规则处理，记录实际尺寸；这不是性能硬目标。tiling 可减少整图缩小，但必须检查接缝截断、重叠重复和支持损失；不声称无损。v0.2 不自动合并跨 tile 词，疑似重复保留关系并 ReviewRequired。

### 2.3 传统分割、方向与原读保真

- `find_text` 要求近水平文字。读取 `get_text_result('class')`/`class_line` 会把 rejection class 换成 second best；必须用带 rank 的 `['class',0]` 或 `['class_line',line,0]` 保留拒识，再读取对应 confidence 和区域。`HTextResult` 结束时按真实 `clear_text_result` 边界清理，Text Model 用 `clear_text_model`；不得用 GC 代替排空。
- 固定字符分割：按 Profile 指定暗字/亮字→显式 threshold 或 auto_threshold→connection→按已采纳字高/字宽/面积界筛选→按冻结阅读方向排序→逐字符分类。粘连、断字、区域数量冲突或域不足为 ReviewRequired，不能为凑长度删区/补字。`auto_threshold` 基于直方图极小值和 Gaussian Sigma，适合近均匀灰度区；uint2 的 Sigma 使用虚拟 256 直方图而 float 使用原灰度，不跨类型复制。
- `text_line_orientation` 输出 radians，暗字亮背景假设；官方单行建议搜索区间 [-π/4,π/4] 不是平台默认值。亮字反相需 Profile 明确；该算子不判镜像或 180°阅读方向。v0.2 DirectionDeg 为宿主冻结输入，不作运行时无界方向搜索。
- `do_ocr_multi_class_mlp` 只给逐字符 winner，需要 top-N 时逐区调用 `do_ocr_single_class_mlp`。拒识符号独立标记，不能替换为次优后报 Read。
- `do_ocr_word_mlp` 的 Expression/lexicon、NumAlternatives/NumCorrections 可纠正文本，Score 是组合惩罚，不是逐字置信或词概率。生产原读路线先用无纠正分类；表达式/字典输出属于宿主独立建议，v0.2 Core 不执行语法纠错。

### 2.4 OCV 与离线训练

OCV 输入含真实 ROI、参考资产、PatternName、四项 adaptation 和 ThresholdMode。`Quality ∈ [0,1]`，**1 表示无故障，0 表示很大故障**，不是概率。Threshold≥0 使用错误像素比例路径，Threshold<0 使用尺寸归一化误差和路径；符号与模式必须一致。默认 10 仅为官方资料事实，不是生产参数。v0.2 `AdaptAngle` 固定 false，非法请求预检拒绝；OCR 内容读对不改变 OCV 观察。

训练不属于生产 `IOcrEngine`，不新增运行时 train 开关。资产 Owner 按已批准数据集→分组/防泄漏→训练→留出评估→导出→fresh read→Golden/Replay→资格发布管理 Deep OCR 组件、传统分类器和 OCV good pattern。传统 MLP 可查 `create_ocr_class_mlp/trainf_ocr_class_mlp`；Deep OCR 的训练 procedure 与 operator 必须分清，本地资料没有 `train_dl_model` 算子页，不能发明调用。训练中断或读回不符保持候选，不能覆盖现有资产。新 alphabet、Blank、映射、预处理或运行时生成新闭包；上线前比较同样本错误接受/拒识、P50/P95/P99、峰值资源与恢复。

### 2.5 ROI 与参数智能推荐：有限建议，不自动应用

真实消费者为丝印/标签工具的离线配方调试。宿主提供标注样本、原始支持、候选 Profile、允许参数离散集合和总预算；生产 operation 不启动搜索、训练或自调参。

1. 未知位置先按冻结 detection Profile 检测；每个有效词框按给定 margin 生成候选 ROI。越界/支持不足候选拒绝，不裁掉字符后报有效；重叠/接缝候选保持独立并标歧义。已有 ROI 时只用宿主提供的有限几何候选，不复制 ROI 模块编辑/坐标 Owner。
2. 候选按 CandidateId ordinal 固定顺序，在同一版本样本集上用 §4 入口执行；同一样本所有候选共享原图、标注和支持，禁止使用样本期待值改变识读/解码。
3. 先检查已采纳评价 Profile 的错误接受、拒识、支持完整、资源和尾延迟约束；缺约束时只返回 `NotEvaluated`，不能选“最好生产参数”。合格候选按错误接受数、拒识数、完整 E2E P95、CandidateId 顺序排序；所有约束和排序观察保留，不能只挑成功样本。
4. 返回建议的 ROI/Profile、每样本 operation/hash、未读/失败/删失计数和选择理由。fingerprint 绑定样本集/标注/Frame/ROI/Profile/资产/runtime/预算；任何变化使建议 stale。空候选、全部失败、超时或 native 未排空时没有可采纳 winner。
5. 宿主工程师审阅→生成新配方草稿→固定留出集 Replay/Shadow→批准新 revision，才能用于新生产 operation。控件只能发 §10 的候选选择事件，不能 Apply 到活动参数。

v0.2 首片只做契约；整模块按 §16 切片交付检测/识读/OCV、推荐计划和离线编排，后续切片不能绕过同一IOcrEngine和资源/取消语义。

## 3. 唯一公共契约：Value API v0.2 / C2 Service API v0.3

本节是模块自身 API，不要求平台 C-02～C-08 全部采纳才可审查纯 Core。平台映射、持久化格式和产品 Owner 仍由相应权威接收。以下为**待实现声明**，不代表已经编译；namespace 固定 `Asun.Modules.Ocr`，使用 .NET 的 `System`、`System.Collections.Generic`、`System.Threading`、`System.Threading.Tasks`。输入/输出集合在边界深复制成只读集合，不把调用方可变集合保存为事实。

### 3.1 图像、ROI、资产与参数

```csharp
public enum OcrMode { Detection, Recognition, Auto }
public enum OcrBackend { HalconDeepOcr, HalconClassic, ExternalApproved }
public enum PixelFormat { Gray8, Gray16, Rgb24, Bgr24 }
public enum ClassicRoute { SegmentedCharacters, TextModelAuto, TextModelManual }
public enum OcvThresholdMode { ErrorPixelRatio, NormalizedErrorSum }
public readonly record struct PixelPoint(double X, double Y);
public sealed record OcrImageRef(string FrameId, string BufferLeaseId,
    PixelFormat Format, int WidthPx, int HeightPx, int StrideBytes,
    string CoordinateRef, string ContentSha256);
public sealed record OcrRoi(string RoiId, double XPx, double YPx,
    double WidthPx, double HeightPx, double AngleDeg, string CoordinateRef,
    IReadOnlyList<PixelPoint> ValidSupportPolygon);
public sealed record AssetRef(string Role, string AssetId, string Sha256, long ByteLength);
public sealed record ModelSnapshot(string AssetId, string ManifestSha256,
    string QualificationRef, IReadOnlyList<AssetRef> Files,
    IReadOnlyList<string> OrderedSymbols, string? BlankSymbol,
    string? MappingId, IReadOnlyList<string> MappedSymbols);
public sealed record PreprocessProfile(string ProfileId, string Sha256,
    double? Gray16Min, double? Gray16Max, bool Invert,
    double DirectionDeg, string Revision);
public sealed record DeepOcrProfile(int DetectionWidthPx, int DetectionHeightPx,
    bool Tiling, int TilingOverlapPx, bool RecognitionAlignment,
    string Runtime, string DeviceId);
public enum ReadingDirection { LeftToRight, RightToLeft }
public sealed record ClassicOcrProfile(ClassicRoute Route, bool DarkOnLight,
    bool UseAutoThreshold, double ThresholdMin, double ThresholdMax,
    double AutoThresholdSigma, double MinAreaPx2, double MaxAreaPx2,
    double MinCharWidthPx, double MaxCharWidthPx,
    double MinCharHeightPx, double MaxCharHeightPx);
public sealed record OperationBudget(int DeadlineMs, int MaxPixels,
    int MaxRois, int MaxWordsPerRoi, int MaxCharacters, int CharacterTopN, int MaxTiles,
    long MaxWorkingBytes, long MaxEvidenceBytes, int MaxMetadataUtf8Bytes);
public sealed record OcrMethodProfile(string ProfileId, string Revision,
    OcrMode Mode, OcrBackend Backend, ModelSnapshot Model,
    PreprocessProfile Preprocess, DeepOcrProfile? Deep,
    ClassicOcrProfile? Classic, string RoutePolicyId, ReadingDirection ReadingDirection,
    IReadOnlyList<string> AllowedScalars, double? MinEngineScore,
    OperationBudget Budget);
public sealed record OcrRequest(string OperationId, string IdempotencyKey,
    OcrImageRef Image, IReadOnlyList<OcrRoi> Rois, OcrMethodProfile Method);
public sealed record OcvProfile(string ProfileId, string Revision,
    ModelSnapshot Reference, string PatternName, PreprocessProfile Preprocess,
    bool AdaptPosition, bool AdaptSize, bool AdaptGray, bool AdaptAngle,
    OcvThresholdMode ThresholdMode, double Threshold, OperationBudget Budget);
public sealed record OcvRequest(string OperationId, string IdempotencyKey,
    OcrImageRef Image, OcrRoi Roi, OcvProfile Method);
```

几何唯一 ID 为 `RoiId`；旧来源 RegionId 由宿主显式映射，不能生成第二套核心身份。像素坐标原点左上，X 向右、Y 向下；ROI 中心为 `(X+Width/2,Y+Height/2)`，AngleDeg表示图像坐标顺时针旋转，输入必须已在[-180,180)；不静默取模后复用hash。Preprocess.DirectionDeg同域。宽高>0，四角及有效支持多边形均在原 Frame 域；支持是 ROI 内单个凸多边形（连续闭边、首点不重复，允许共线顶点但不允许自交/重复顶点）；有孔/不连通/非凸域由宿主拆分，不拿 bounding box 冒称支持。像素中心合法域为 [0,WidthPx-1]×[0,HeightPx-1]，本版矩形四角以几何边界 [0,WidthPx]×[0,HeightPx] 校验；用几何交集映射到像素中心，不能把边界点当额外像素。v0.2 不含投影/标定对象，外部定位变换后的 Frame 由宿主提供并保留父图谱系。

结构校验冻结如下，数值目标仍 `TargetPending`。所有enum值必须定义，引用/集合/元素不得null（声明?字段除外），枚举只用一次稳定快照。Method必须具备非空QualificationRef；Deep Recognition/Auto与classic有非空AllowedScalars/OrderedSymbols，Detection可空；OCV二者字表相关为空。所有字符串长度和列表数量的canonical UTF-8总量受Budget.MaxMetadataUtf8Bytes限制（正整数、不超过adapter能力）；Submit在深复制前先按已知Count/有限字节计数拒绝明显超限，不先序列化巨大输入后才查预算。Budget.MaxCharacters限原读scalar，不能兼作ID/文件名/字表的长度上限。

| 字段 | 校验与来源 | 失败 |
|---|---|---|
| ID/Revision/CoordinateRef | 非空，ordinal 区分大小写，禁止前后空白；RoiId 唯一，坐标引用须等于 Frame | INPUT-001/003 |
| hash/Files | SHA-256 小写 64 hex；Role 唯一、ByteLength>0，Role 按 §3.6 组成闭包；ManifestSha256 对资产描述计算，不含自身值；不得 latest | ASSET-001 |
| 图像 | checked 计算 width×bytesPerPixel≤stride，stride×height≤Array.MaxLength 且≤int.MaxValue；Gray16 为 little-endian unsigned，RGB/BGR interleaved；hash 包含所有 stride 字节（含 padding） | INPUT-002 |
| ROI/支持 | 有限数、正宽高、旋转后四角在域内，凸支持多边形≥3点且面积>0、所有点在 ROI 闭矩形内；不静默 clip | INPUT-003 |
| Budget | 计数/字节/deadline 正整数，不能超过 engine 总预算或 adapter capability；先 checked 防溢出 | METHOD-001/RESOURCE-001 |
| Preprocess | Gray16 必有有限 Min<Max；截到范围，线性映射到0..255，四舍五入 midpoint away from zero；其它格式两字段 null；BGR→RGB/单通道转换显式记谱系 | METHOD-001 |
| Deep/Classic | Deep 后端恰有 Deep，Classic 后端恰有 Classic；External 两者均 null，必须批准 adapter；Classic 不支持 Detection/Auto | METHOD-001/ADAPTER-001 |
| Deep 尺寸/alignment | 尺寸>0按32倍数向上取整且不越预算（checked）；Recognition-only不把此参数用于改变裁图字形比例；原Frame和实际预处理画布像素数均checked且≤MaxPixels/capability；tiling overlap非负且小于实际两边长；alignment 须能力声明 | METHOD-001 |
| Classic | 灰度/面积/宽高范围有限且上下界合法；Sigma>0；DarkOnLight指显式Invert之后的图像极性；TextModelAuto/Manual 的最少字符前置由 §2.3 检查 | METHOD-001/QUALITY-002 |
| 字符/score | AllowedScalars 每项恰一个 Unicode scalar，唯一；长度以 Unicode scalar 计，不做 NFC/大小写规范化，非法 surrogate 为结构失败；分数 null 或适配器声明范围内有限数 | METHOD-001/RESULT-001 |
| 原读/映射 | OrderedSymbols 包含所有模型符号；MappingId=null 时 MappedSymbols 为空，非空时等长；native模型实际mapping必须恒等；ModelSnapshot中的post-read非恒等规则供独立派生（MappedSymbols每项为空或一个合法scalar） | METHOD-001 |
| OCV | PatternName 非空，AdaptAngle=false；ThresholdMode/阈值符号一致；Reference 的文件/hash及参考资格完整 | METHOD-001/OCV-001 |

v0.2不内建模糊/反光/OOD检测器，也不猜未声明质量阈值；QualityChecking检查真实支持与可用像素，ObservationChecking检查字符域、拒识与MinEngineScore。采集是否属于模型资格成像域由宿主资格Owner在提交前确认，可组合image-quality模块的公开观察；物理OOD高softmax不能由本模块保证检出。退化样本必须在真实H/P评价中暴露误接受，未知资格域不能因字符域内高分当通过。

post-read映射在原读冻结后逐Unicode scalar按OrderedSymbols→MappedSymbols执行，不在表内的scalar保留，空目标为删除，不映射native Blank/拒识位置、不用期待值或词典；非恒等规则存在时输出MappedObservation，原读/原生score/拒识状态不改变。它不参与原读字符域/MinEngineScore校验或默认推荐评价。

字符域、长度是观察校验；业务格式、期待比较、词典纠错归宿主。输出域外/超长不修改原文，item 为 ReviewRequired。后端无字符分数时 `ScoreKind=None/Value=null`，不得补 1；MinEngineScore 只能作用于声明可阈值化的同后端分数域，不能用于 detection/OCV 或缺分数路线。

### 3.2 原读、检测、OCV 与证据

```csharp
public enum OcrOutcome { Detected, Read, Empty, Rejected, Ambiguous, ReviewRequired, NotRun }
public enum OcvOutcome { Computed, NotComputed }
public enum ScoreKind { None, EngineNative, CalibratedForProfile }
public sealed record EngineScore(double? Value, ScoreKind Kind, string Meaning,
    string? CalibrationSha256);
public sealed record CharacterCandidate(int PositionIndex, int Rank, string Symbol,
    bool IsBlank, bool IsRejection, EngineScore Score);
public sealed record MappedObservation(string MappingId, string Text);
public sealed record OcrWordObservation(string WordId, string? RawText,
    IReadOnlyList<PixelPoint> BoxOnFrame, int BackendOrdinal, int? LineOrdinal, EngineScore Score,
    IReadOnlyList<CharacterCandidate> CharacterCandidates,
    MappedObservation? Mapped, bool SupportComplete,
    IReadOnlyList<string> RelatedWordIds);
public sealed record OcrItemResult(string RoiId, OcrOutcome Outcome,
    IReadOnlyList<OcrWordObservation> Words, string ReadingOrder,
    string? RejectReason, string EvidenceRef);
public sealed record OcvObservation(string RoiId, OcvOutcome Outcome,
    double? Quality, OcvThresholdMode ThresholdMode, double Threshold,
    string ReferenceManifestSha256, string? RejectReason, string EvidenceRef);
public sealed record EvidenceBlob(string Role, string MediaType,
    string Sha256, ReadOnlyMemory<byte> Bytes);
public sealed record OcrEvidence(string EvidenceRef, string ContentSha256,
    string FrameSha256, string ProfileSha256,
    IReadOnlyList<EvidenceBlob> Blobs);
public sealed record OcrResponse(string OperationId, OcrMode Mode, string RequestSha256,
    string MethodSnapshotSha256, IReadOnlyList<OcrItemResult> Items,
    OcrEvidence Evidence);
public sealed record OcvResponse(string OperationId, string RequestSha256,
    string MethodSnapshotSha256, OcvObservation Observation, OcrEvidence Evidence);
public sealed record OcrError(string Code, string Stage, bool Retryable,
    string OperationId, string? CauseRef, string MessageKey);
```

`Detection` 中 RawText=null、CharacterCandidates 为空，Words 仅框；可定位完整框的 item 为 Detected，显示“检测到文字”；不能产生 Read。无框为 Empty。Recognition/Auto 的 RawText 保存未纠正原读；空串不是未执行。每 ROI 恰一 item，多个词用 Words，WordId 按该 ROI 的稳定排序 ordinal 编号，字符候选 PositionIndex 为后端解码位置（含Blank/拒识位置），rank 从0开始且不跨位置拼词；它不是 RawText 的UTF-16索引或必然一一对应的scalar索引。RawText长度独立按Unicode scalar统计。有可复核 LineOrdinal 时按其 ordinal、中心X（ReadingDirection=RightToLeft 时反向）、BackendOrdinal排序；无行证据按中心Y、中心X、BackendOrdinal作展示顺序并标 ReadingOrder=Unresolved、多词为 Ambiguous。单词 ReadingOrder=SingleWord。不把该顺序当产品目标关联。

每响应Mode必须等于请求Mode。检测框、字符拒识、空结果、低信和无分数分别表示。Read 只说明获得观察，不是质量通过；OCV Computed 只表示数值可计算，宿主再用其质量 Profile 判字形。不提供 OCV 的 Rejected=产品缺陷。失败/取消/超时属 operation，不塞进 OcrOutcome。

EvidenceRef 为 `ocr:sha256:<ContentSha256>`，是完整内存证据身份，不是落盘凭证。Blobs 持有响应即可读取，不依赖Frame/native。byte Memory 在创建时独立复制、此后不暴露可写数组；adapter、宿主不得用MemoryMarshal等获取并修改底层内存，测试故意改原租约不得污染响应。

证据至少有四类：`request.json`（§3.4请求canonical投影，包含完整Frame/ROI/Method及资产描述）、`frame.raw`（完整stride字节）、`trace.json`（§3.6闭合谱系）、`observation.json`（§3.2观察，排除EvidenceRef/OperationId）。裁图/转换图按 `derived/<ordinal>.raw` 放入，trace引用role/hash。Blobs.Role唯一，媒体类型明确；每blob SHA-256精确核对。ContentSha256只hash canonical descriptor `{ContractVersion:"ocr-evidence/0.2",FrameSha256,ProfileSha256,Blobs:[{Role,MediaType,Sha256,ByteLength}]}`，Blobs按Role ordinal排序；不含ContentSha256/EvidenceRef自身、不含运行/时间/epoch/期待值、不重复hash任意内存地址。各item.EvidenceRef和OCV.EvidenceRef填相同聚合EvidenceRef，避免结果blob自引用。完整响应深复制后计算聚合，再填回引用。

证据空间先reserve，frame+derived+json超MaxEvidenceBytes不发布伪完整响应，operation Failed且Ocr/Ocv可为null，保留Errors与输入hash供宿主处理。失败过程中无法构造闭合证据的部分观察不伪装成可回放响应。native不承诺跨硬件逐字节相同，Replay比较原读/状态/几何语义和允许误差，禁止无依据承诺模型输出完全确定。Sensitive像素/文本不写普通日志。

### 3.3 生命周期 DTO

```csharp
public enum OperationKind { Ocr, Ocv }
public enum AdmissionKind { Accepted, Existing, Rejected }
public enum LookupKind { Found, Unknown }
public enum OperationState { Queued, Acquiring, QualityChecking, Detecting,
    Recognizing, DetectingAndRecognizing, Verifying, Ordering, ObservationChecking,
    CancelRequested, Draining, Quarantined, Completed, Failed, Cancelled, TimedOut }
public enum StopReason { None, Cancel, Deadline, Shutdown, Failure }
public enum WaitKind { Terminal, BudgetElapsed, ObserverCancelled, Unknown }
public enum DrainKind { Drained, Pending, ObserverCancelled }
public sealed record OperationSnapshot(string OperationId, string EngineEpoch,
    OperationKind Kind, string RequestSha256, string MethodSnapshotSha256,
    OperationState State, StopReason StopReason, bool ResourcesReleased,
    OcrResponse? Ocr, OcvResponse? Ocv, IReadOnlyList<OcrError> Errors,
    long Sequence, double QueueMs, double ExecuteMs, double DrainMs);
public sealed record AdmissionReceipt(AdmissionKind Kind,
    OperationSnapshot? Snapshot, IReadOnlyList<OcrError> Errors);
public sealed record LookupReceipt(LookupKind Kind, OperationSnapshot? Snapshot);
public sealed record WaitReceipt(WaitKind Kind, LookupReceipt Current);
public sealed record CancelReceipt(bool Found, bool CancelAccepted, LookupReceipt Current);
public sealed record DrainReceipt(DrainKind Kind,
    IReadOnlyList<OperationSnapshot> Pending, long RetainedBytes);
public sealed record OcrRuntimeOptions(int MaxQueued, int MaxActive,
    int MaxOperations, long MaxWorkingBytes, long MaxRetainedEvidenceBytes,
    int MaxEventsPerOperation);
public enum OcrEventKind { RequestReceived, Validating, RequestRejected,
    RequestAccepted, StageChanged, CancelRequested, DeadlineExceeded,
    DrainStarted, Quarantined, Drained, ResourcesReleased, Terminal, Diagnostic }
public sealed record OcrEvent(string OperationId, string EngineEpoch, long Sequence,
    DateTimeOffset TimestampUtc, string MethodSnapshotSha256,
    OcrEventKind Kind, OperationState? State, string? RoiId, string? Code);
public interface IOcrEventSink { bool TryPublish(OcrEvent value); }
```

AdmissionReceipt Accepted/Existing必须Snapshot非null、Rejected必须Snapshot=null且Errors非空；LookupReceipt Found非null/Unknown为null；Wait Terminal只配Found终态，Unknown只配Unknown，BudgetElapsed/ObserverCancelled配当前快照而不声称Terminal。Drain Drained必须Pending空、RetainedBytes=0（指活动working reserve，不含已封存response证据）；Pending/ObserverCancelled保留仍持有资源的snapshot。

终态仅 Completed/Failed/Cancelled/TimedOut；前置拒绝用 AdmissionReceipt，不登记 Invalid operation。Completed 可以包含 Read/Empty/ReviewRequired 混合 item；Detection不发Recognizing，Auto为组合DetectingAndRecognizing而非捏造native内部回调，OCV不发Detecting。`StopReason` 不等同终态。Found 终态 ResourcesReleased 必 true；Unknown 时 Snapshot=null，没有结果，不能当 Failed/Empty。Ocr/Ocv互斥且匹配OperationKind，Completed必有对应完整响应，Ocr.Completed不得含NotRun；非终态二者均null，只有终态才发布响应；Failed/Cancelled/TimedOut 可携完整已观察的部分响应，缺失 ROI 用 NotRun、缺失 OCV 用 NotComputed，不伪造原读。UI 必同时看运行状态和 item 观察。

### 3.4 核心入口与纯 Core 首片

```csharp
public interface IOcrEngine : IAsyncDisposable
{
    AdmissionReceipt Submit(OcrRequest request);
    AdmissionReceipt Submit(OcvRequest request);
    LookupReceipt Query(string operationId);
    OperationResourceLookup QueryResources(string engineEpoch, string operationId);
    ValueTask<WaitReceipt> WaitAsync(string operationId, TimeSpan waitBudget,
        CancellationToken observerCancellation = default);
    CancelReceipt RequestCancel(string operationId);
    ValueTask<DrainReceipt> StopAndDrainAsync(TimeSpan waitBudget,
        CancellationToken observerCancellation = default);
}
public sealed record ValidationResult(bool IsValid, IReadOnlyList<OcrError> Errors);
public interface IOcrContract
{
    ValidationResult Validate(OcrRequest request);
    ValidationResult Validate(OcvRequest request);
    string RequestSha256(OcrRequest request);
    string RequestSha256(OcvRequest request);
    string MethodSha256(OcrMethodProfile method);
    string MethodSha256(OcvProfile method);
}
```

计划实现类为 `OcrContract : IOcrContract`（无依赖）与 `OcrEngine : IOcrEngine`。后者构造依赖为§4.4的OcrProcessOwner/OwnerTicket与 §8 的 `IFrameLeaseProvider/IModelAssetResolver/IOcrAdapterFactory`、`OcrRuntimeOptions`、`TimeProvider` 和可空 IOcrEventSink；宿主拥有注入 provider/resolver/factory，engine 只拥有本次取得的 lease/worker，不 Dispose 宿主依赖。Options 无默认性能常数，所有整数/字节>0且MaxQueued≤MaxOperations、MaxActive≤factory.MaxWorkers/MaxOperations；MaxOperations 包含终态记录，容量满拒绝新请求而不驱逐未确认 operation。C2 Service v0.3 engine生命周期内不清空幂等表，记录/证据达上限先关闭、排空并由宿主归档，再新建 epoch。

C2唯一构造签名为 `public OcrEngine(OcrProcessOwner owner, OwnerTicket ticket, IFrameLeaseProvider frames, IModelAssetResolver assets, IOcrAdapterFactory adapters, OcrRuntimeOptions options, TimeProvider timeProvider, IOcrEventSink? events = null)`。owner/ticket必须已reserve并AttachSources且接口实例完全匹配；构造原子把factory/engine/clock/options绑定到原槽，不启动native。旧无Owner构造退役，不能创建离栈即失去资源Owner的服务；§8.1 H工厂本身签名/回滚保持。null依赖/非法Options/非法Capabilities抛ArgumentException，不启动worker。`OcrContract`公开无参构造；`OcrRecommendationEvaluator : IOcrRecommendationEvaluator`亦无依赖。

纯 Core 首片仅实现 IOcrContract、不可变值对象、结构校验和 fingerprint，不创建调度器/native/UI。空/非法请求先 Validate，非法请求的hash入口抛ArgumentException（message key Ocr.InvalidCanonicalInput），不返回空hash；Validate始终返回ValidationResult并对null定位INPUT-001；不把平台等待项带进纯值计算。

hash 用 SHA-256 小写 hex；canonical UTF-8 JSON 禁止缩进/BOM/尾换行，由 `Utf8JsonWriter` 固定按record声明顺序写字段，顶层包装依次为 `ContractVersion`（`ocr-api/0.2`）、`Kind`（`OcrRequest/OcvRequest/OcrMethod/OcvMethod`）、`Value`（投影对象）；enum 写固定名，null 显式写入，数值有限、-0归一为0；数组保留声明顺序，集合禁止重复。Request 排除 OperationId/IdempotencyKey，包含 Frame 元数据/内容hash、完整 ROI 和 Method；Method 包含全部参数及资产清单，不能只 hash ProfileId。字符串保留 Unicode 原值不规范化；合法字符串使用默认 .NET JSON escaping。Files 按 Role ordinal 排序后写入，AllowedScalars 按 scalar ordinal 排序；OrderedSymbols/MappedSymbols 保持原顺序。Preprocess.Sha256 是宿主预处理资产身份，不代替实际字段的 Method hash。同输入改期待值不影响 hash，改阈值/字表顺序必改变 hash。

### 3.5 推荐计划与评价合同

```csharp
public sealed record RoiProposalInput(OcrRequest DetectionRequest, OcrResponse Detection,
    IReadOnlyList<double> MarginsPx, int MaxCandidates);
public sealed record RoiProposal(string CandidateId, string SourceRoiId, string SourceWordId,
    double MarginPx, OcrRoi Roi);
public sealed record RoiProposalResult(IReadOnlyList<RoiProposal> Candidates,
    IReadOnlyList<string> Reasons);
public interface IOcrRoiRecommender { RoiProposalResult Propose(RoiProposalInput input); }
public sealed record RecommendationCandidate(string CandidateId,
    IReadOnlyList<OcrRoi> Rois, OcrMethodProfile Method);
public sealed record RecommendationTrial(string CandidateId, string SampleId,
    string OperationId, string EvidenceSha256, OperationState TerminalState,
    bool Drained, bool FalseAccept, bool Refused, bool SupportComplete,
    double? EndToEndMs, long PeakWorkingBytes);
public sealed record RecommendationLimits(int MaxFalseAccepts, int MaxRefusals,
    double MaxP95Ms, long MaxWorkingBytes, string EvaluationProfileId);
public sealed record RecommendationInput(string InputFingerprint,
    IReadOnlyList<string> SampleIds, IReadOnlyList<RecommendationCandidate> Candidates,
    IReadOnlyList<RecommendationTrial> Trials, RecommendationLimits? Limits);
public enum RecommendationOutcome { Suggested, NotEvaluated, NoEligibleCandidate }
public sealed record OcrRecommendation(RecommendationOutcome Outcome,
    string InputFingerprint, string? CandidateId, IReadOnlyList<string> Reasons);
public interface IOcrRecommendationEvaluator
{
    OcrRecommendation Evaluate(RecommendationInput input);
}
```

计划类 `OcrRoiRecommender/ OcrRecommendationEvaluator` 无参构造，无设备/模型/窗口依赖。Propose只消费已排空Mode=Detection响应（宿主核终态），先用OcrContract校验DetectionRequest、请求hash/响应Mode/FrameSha256必须完全匹配；源Frame和父ROI都从DetectionRequest取得，不解析未知外部ROI对象；MarginsPx为唯一有限非负集合，MaxCandidates>0。按RoiId/WordId ordinal、margin升序枚举；只接受SupportComplete、4角非退化矩形且无RelatedWordIds的word。使用原四角顺时针、首点为局部左上，局部边向量u/v；中心不变，每侧扩margin，角度atan2(u.Y,u.X)；用§3.1 ROI中心公式反求X/Y，验证新四角仍在原Frame和父ROI凸支持内。矩形校验采用单位边正交/对边平行，相对角容差64×2^-52；顶点重建误差上限64×2^-52×max(1,最大坐标绝对值,边长)，仅为浮点结构容差、不作为物理放行值；proposal由中心/u单位向量和其顺时针法向重建，支持/Frame界限仍严格检查且不加该容差扩域。方向/矩形不合法、边界或支持不足时拒绝该候选并返回 `roi:<RoiId>/<WordId>:<reason>`，不静默clip。CandidateId为canonical数组[RoiId,WordId,margin]的SHA-256小写hex（避免ID中/导致拼接冲突），候选的新RoiId等于CandidateId；不得使用产品元件身份。只有存在下一有效候选却受限未输出才返回ProposalLimitReached（恰好数量不算截断），不声称已穷尽。不同词重叠的候选保持独立，后续交宿主选择，不合并补全。

Evaluate结构错误（null/重复候选或样本/Trial引用不存在/非有限负耗时/负资源/非法hash/非终态）抛ArgumentException并给Ocr.InvalidRecommendationInput。每候选×每SampleId恰一Trial；缺组合、未排空、Failed/Cancelled/TimedOut、缺E2E、支持不足均令该候选不合格，不删分母；Drained必须对应ResourcesReleased。Trial中FalseAccept/Refused为宿主基于独立标注的评价事实，不把期待文本传入识读；字符域内错误Read可标FalseAccept=true而非拒识。Limits计数≥0，P95/字节>0，EvaluationProfileId非空；null时返回NotEvaluated，不选winner。合格候选按§2.5排序，用[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)统计；无合格返回NoEligibleCandidate，Reasons按CandidateId顺序明确缺组合/运行失败/阈值原因。InputFingerprint必须来自宿主覆盖样本/标注/候选/版本/评价Limits的闭包，模块验证64hex并原样回传；宿主重新计算不同即stale，不能用相同ID绕过。

推荐执行是**有限离线Host编排**，不用第二个native入口：一次Detection→Propose→宿主在同坐标/成像族样本上实例化有限candidate请求→按CandidateId、SampleId逐一Submit/Wait→保存每个ResourcesReleased的E2E和语义评价→Evaluate→工程师审阅。不同尺寸/定位的样本由宿主提供各自合法ROI，不把一个Frame的像素ROI跨域平移；有多种几何族时各族独立评价。总预算包括已尝试/未尝试分母；中止后剩余Trial缺失，不能保留先前“暂时最好”当最终建议。关闭时使用同一StopAndDrainAsync，无额外自动Apply或隐藏训练。此流程作为§9离线TestHost场景交付，算法功能并未以“后续选择”留空。

### 3.6 资产、谱系与输出约束的固定形状

```csharp
public readonly record struct Affine2D(double M11, double M12, double M13,
    double M21, double M22, double M23);
public sealed record ImageDerivation(string RoiId, string Role, string ParentRole,
    PixelFormat Format, int WidthPx, int HeightPx, int StrideBytes,
    string Sha256, Affine2D FrameToImage, Affine2D ImageToFrame,
    IReadOnlyList<PixelPoint> ValidSupportPolygon, string Step);
public sealed record RuntimeParameter(string Name, string Value);
public sealed record EvidenceTrace(string AdapterId, string AdapterVersion,
    string RuntimeVersion, string ModelManifestSha256, string PreprocessSha256,
    IReadOnlyList<OcrRoi> Rois, IReadOnlyList<ImageDerivation> Images,
    IReadOnlyList<string> ObservationCodes, IReadOnlyList<RuntimeParameter> ActualParameters);
```

Affine2D 的 x'=M11*x+M12*y+M13、y'=M21*x+M22*y+M23，有限、线性行列式非零；逆矩阵由同一double矩阵计算并以代表点/四角核对，不用“不同库各算一次”凑相同hash。源Role=`frame.raw`，ParentRole仅引用已出现role；裁图/旋转/缩放各一step，Step值为Crop/Rotate/Gray16ToByte/BgrToRgb/RgbToGray/Invert/Resize/Pad，像素转换不改变坐标时矩阵identity。Pad只扩尺寸不扩ValidSupportPolygon。ActualParameters保存实际read-back/runtime/device/模式/有效detection尺寸/tiling数量/转换参数，Name唯一ordinal排序、Value为不含客户文本的canonical标量字符串；不能查询的参数Value记为`NotQueryable`、请求值仍在request.json，不声称已核。trace.json按上述record声明顺序canonical写入，不含EvidenceRef、运行状态、时间或自身hash；Derived byte长精确stride×height。所有输出几何为Frame四角，不公开预处理图的框当原图框。

ModelSnapshot.ManifestSha256 是资产Owner描述文件身份；描述不含ManifestSha256自身。Files固定Role：Deep包含 `deep-ocr-model`、`charset`、`preprocess`、`runtime-profile`；classic包含 `classifier-mlp`、`charset`、`preprocess`、`runtime-profile`；ExternalApproved包含 `external-model`、`charset`、`preprocess`、`runtime-profile`（模型/CTC字典等实际闭包以同Role资产包提供，完整版本/字典顺序/blank索引/backend/decoder固定）；OCV包含 `ocv-reference`、`preprocess`、`runtime-profile`（字表为空、Blank/MappingId null）。`charset` UTF-8描述记录OrderedSymbols/Blank/MappingId/MappedSymbols顺序，`preprocess`绑定Preprocess.Sha256和规范参数，`runtime-profile`绑定后端/runtime/device和能力；不同asset由resolver映射，核心不打开文件或猜路径。各文件身份由asset Owner解析；core核每blob长度/hash且Snapshot完全匹配，请求Method hash包括所有描述字段。OCV.Reference无Backend字段，factory须OcvSupported；其Runtime在reference.runtime-profile中，不继承上一个OCR的device。

传统v0.2冻结MLP classifier（TextModelAuto亦使用MLP）；CNN/KNN/SVM为后续显式版本扩展，不能相同Role装另一分类器。Deep recognition-only资产不要求有detection组件，Detection不要求recognition组件，Auto需二者，worker加载后读回确认。Deep Alphabet Blank必须U+2800且位于首位；classic字表无Blank，拒识标记用CharacterCandidate.IsRejection，不冒称字母。External字符表按资产decoder的blank索引保持原顺序，BlankSymbol显式（可以是专用占位名称、不当Unicode文字），空格显式符号；与HALCON U+2800规则分别校验。源字典是符号顺序资产，业务lexicon不进入ModelSnapshot原读；非blank常规符号必须一个合法Unicode scalar，未知特殊类只能为声明的拒识符号。

EngineScore.Kind=None时Value=null、Meaning=`Unavailable`、CalibrationSha256=null；EngineNative须Value有限、Meaning对应§8能力，CalibrationSha256=null；CalibratedForProfile须已发布calibration hash/相同Profile，v0.2 HALCON适配器不生成这种分数。框4角顺时针且面积>0、WordId在ROI内唯一、BackendOrdinal≥0、LineOrdinal null或≥0；RelatedWordIds只能引用同ROI现有word；候选PositionIndex≥0且每位置rank连续，无字符候选能力时CharacterTopN只能1且不伪造多候选。只有模块ObservationChecking通过才能发布输入规范化后的只读响应；Rejected表示后端明确拒识，Empty表示已执行且无文字观察，NotRun仅表示本项没有执行证据。

## 4. 接纳、事件、查询与状态

### 4.1 接纳与幂等

Submit 同步仅做托管结构/能力/预算校验、深复制、hash、原子登记和有界队列入列；不加载模型、不调用 native、不在 UI 线程等待像素。键作用域为engine epoch内的IdempotencyKey；engine构造时生成Guid的32位小写N格式EngineEpoch，运行期间不变，不参与内容hash。先查键，再查 OperationId：同 key 同 hash 返回 Existing 原 snapshot（原 OperationId）；同 key 异 hash 为 OCR-IDEMPOTENCY-002；同 OperationId 不同 key/request 拒绝 OCR-IDEMPOTENCY-001。并发重复只接纳一次。拒绝请求不占登记容量、不取得 lease。

接纳按请求Budget保守reserve MaxWorkingBytes/MaxEvidenceBytes；各自累加额度分别不超过engine.MaxWorkingBytes/MaxRetainedEvidenceBytes，MaxWorkingBytes覆盖Frame/asset blob/裁图/native/GPU临时内存声明总量，MaxEvidenceBytes独立覆盖结果保留，不能一份算两次物理占用但必须分别有额度。实际native不可预估由worker保守声明/监控超限失败，不用“GC可回收”抵扣；未排空保留全部working reserve，终态释放working、retained evidence按实际blob字节计，释放未确认不腾额度。输入元数据/ROI/canonical深复制按MaxPixels/MaxRois/MaxCharacters/MaxOperations有界，Events每operation最多MaxEventsPerOperation且超限合并Diagnostic，不丢终态；IOcrEventSink实现必须立即有界入队，阻塞sink违反端口不得装入生产。

接纳时仅声明资源存在，执行 Acquiring 时实际 retain/read/hash 检查；宿主从 Submit 前至收到拒绝或最终 ResourcesReleased 前保留可 retain 的 Frame 引用。运行中模型闭包 immutable。任何匹配失败进入 Failed，不能临时用 latest。MaxActive 是并行 worker 数，单 operation 内按 ROI 顺序串行；factory 能力不足/预算无剩余时拒绝，不默认扩并发。

deadline 自 RequestAccepted 开始（含队列/取租约/执行），TimeProvider 单调时间判断。Query/RequestCancel 为内存操作；未知 ID 返回 Unknown（CancelReceipt Found=false、CancelAccepted=false），不重跑。RequestCancel对活动且StopReason=None原子冻结Cancel、停止后续stage并返回true；重复取消或已有Deadline/Failure/Shutdown为Found=true但CancelAccepted=false，保留先到原因。WaitAsync 的有限非负 waitBudget 只限制观察等待，0为快照；预算到返回 BudgetElapsed、observer token取消返回 ObserverCancelled，均不取消计算。Submit 请求本身不携 token，避免 token 生命周期污染幂等内容；执行取消显式 RequestCancel。

### 4.2 唯一事件顺序与终态

```text
RequestReceived → Validating → RequestRejected
                           | RequestAccepted → Queued → Acquiring
                           → QualityChecking
                           → Detecting (Detection) / Recognizing (Recognition)
                           / DetectingAndRecognizing (Auto) / Verifying (OCV)
                           （每ROI按请求顺序重复实际路线阶段）
                           → Ordering → ObservationChecking
                           → DrainStarted → Drained → ResourcesReleased → Terminal
cancel/deadline/failure: 已接纳 → 停止后续阶段 → DrainStarted
                        → [Quarantined 如排空/关闭等待预算到而仍未停]
                        → Drained → ResourcesReleased → 唯一 Terminal
```

前置拒绝无 Drained/Terminal；接纳后即使未调用 native，也有 DrainStarted/Drained/ResourcesReleased，表示已接纳资源账目闭合。Existing不另发RequestAccepted/阶段/终态，不创建新worker。前置RequestReceived/Validating/RequestRejected尚未登记，Sequence=0且不参与snapshot序列；非法OperationId用Errors.OperationId空串、不发该ID事件。接纳事件从Sequence=1开始；StageChanged 为阶段投影，已接纳Sequence在一个operation单调递增；Query snapshot 是状态来源，sink false/异常或丢通知不可改变结果，Errors合并一次OCR-DIAG-001；禁止递归调用失败sink报告sink失败。TimestampUtc 仅日志，deadline 用单调钟。QueueMs从Accepted到Acquiring；ExecuteMs从Acquiring到DrainStarted，DrainMs从DrainStarted到ResourcesReleased；尚未Acquiring即停止的队列任务，以DrainStarted作为队列结束、ExecuteMs=0；终态E2E等于三者之和，非终态是截至查询时的累计值。admission事件Method hash尚未知时固定空串；Structure非法时不伪造有效hash。

取消、deadline、failure 在运行 epoch 锁内先到先冻结 StopReason，终态分别 Cancelled/TimedOut/Failed；已有观察随部分响应保留。只有工作/迟到回调已退出、worker安全Dispose、所有lease归还后才能最终发布。普通Wait预算到只返回BudgetElapsed，不把正常运行改成Quarantined；已请求停止且排空/关闭等待预算到或释放失败时才Quarantined，不能提前释图或写 Cancelled。若 Terminal 已冻结，迟到取消为 CancelAccepted=false，不能改写 Completed。Completed 从不表示产品合格。

### 4.3 关闭和重启的可执行边界

StopAndDrainAsync 原子停止接收，对未终态 operation 请求 Shutdown，再在有限预算内等待；完整排空返回 Drained/Pending空，否则 Pending 含每个未退出 snapshot 和占用字节。observer取消只停止等待，停止接收/已请求取消仍有效。Shutdown 终结为 Cancelled，StopReason=Shutdown。未退出 native 对应 worker 隔离并继续计费，队列/租约容量不腾空给下一任务。再次 StopAndDrainAsync 查询同一关闭过程，不重复 Dispose。

DisposeAsync **不发起无界等待**（已登记engine归§4.4根槽清理，局部Host不得抢Dispose）：所有已接纳 operation 资源已释放时销毁 engine 托管状态；否则立即抛 InvalidOperationException（message key Ocr.DisposeDrainRequired），状态和租约保留，宿主必须继续 StopAndDrainAsync。不在 WPF 窗口 Close 的 finally 中盲目 await using 未排空 engine。宿主依赖必须晚于 engine 排空销毁；native 未返回不能用强制 Dispose 宣称释放。

engine 只提供进程内幂等/Query。重启后新 epoch 对原 ID 返回 Unknown；宿主以已持久 journal/证据回执恢复查询和防重放，缺回执不自动重跑。持久 Unknown 是宿主事务状态，不是新的 OcrOutcome/运行终态。此边界不假称模块拥有数据库或跨重启 exactly-once。成功Dispose原子关闭接纳/销毁状态，随后所有非Dispose入口抛ObjectDisposedException，重复Dispose无效返回；关闭但尚未Dispose时Submit返回Rejected/OCR-RUNTIME-001，其余查询/取消/等待可用。非法operationId或负/无限waitBudget抛ArgumentException；预算必须可由TimeProvider计时器表示，非法不发起关闭/取消/worker。

C2另外提供操作资源观测DTO（不进入C1/C3请求canonical）：

```csharp
public sealed record OperationResourceObservation(string EngineEpoch, string OperationId,
    long DeclaredWorkingUpperBoundBytes, long? ObservedPeakWorkingBytes,
    bool ObservationComplete, long RetainedEvidenceBytes);
public sealed record OperationResourceLookup(bool Found, OperationResourceObservation? Observation);
```

QueryResources必须核本engine原epoch/operation，未知Found=false/Observation=null。Declared是Budget而非实测；Observed只有adapter以§8 ReportWorkingBytes完整报告自己临时/native峰值并由engine合并已知frame/asset/证据处理临时分配后才ObservationComplete=true，未完整则false且Observed=null。ReportWorkingBytes表示adapter本次总临时/native工作字节，**不包含source驻留/借用原Frame和asset字节**；engine把自己的实际复制/处理工作计入，同时按载体去重计源借用逻辑hold，不用Declared充Observed。协议worker没有native、未作派生，明确ReportWorkingBytes(0,true)，其托管json/复制临时量由engine实际登记；生产native未可完整测量则如实Unavailable，不猜GPU峰值。实时不完整不可宣称资源资格，操作终态和资源观测独立。

### 4.4 C2 进程根 Owner：Factory 前槽、原任务、双轴与有限恢复

C1/C3纯值声明与 `ocr-api/0.2` canonical保持。以下为 **C2 Service API v0.3** 新增公开契约，namespace仍`Asun.Modules.Ocr`，不放入请求/Method hash；不是新产品事务Owner。`OcrProcessOwner`由进程入口创建并强持到最后一个槽Released，不放局部await using、静态全局或WPF窗口中。它自己无native、无文件/产品数据库；Factory/worker原任务和Frame/asset借用受它明确持有。

```csharp
public enum HostOutcome { NotStarted, Running, Completed, Failed, Cancelled, TimedOut }
public enum HostResources { Held, Draining, Unknown, Released }
public enum CleanupPhase { Operations, Engine, Sources }
public enum OwnedTaskState { Pending, Succeeded, Faulted, Cancelled }
public enum OwnerActionKind { Completed, BudgetElapsed, ObserverCancelled, Unknown }
public enum HandoffKind { Retained, Released, Rejected }
public sealed record ProcessOwnerLimits(int MaxSlots, int MaxTasks,
    long MaxHeldBytes, int MaxErrorsPerSlot);
public sealed record OwnerSlotLimits(int MaxOperations, int MaxTasks,
    long MaxWorkingBytes, long MaxEvidenceBytes, long MaxSourceBytes,
    int MaxReleaseAttempts);
public sealed record OwnerTicket(string ProcessEpoch, string SlotId, string HostId);
public sealed record HostFailure(string Code, string Stage, string? CauseRef);
public sealed record OwnedTaskView(string TaskId, string? EngineEpoch,
    string? OperationId, string Role, int Attempt, OwnedTaskState State);
public sealed record OwnerSlotSnapshot(OwnerTicket Ticket, string? EngineEpoch,
    HostOutcome Outcome, HostResources Resources, CleanupPhase? Phase,
    HostFailure? PrimaryFailure, IReadOnlyList<HostFailure> CleanupFailures,
    IReadOnlyList<OwnedTaskView> Tasks, long HeldBytes, long RetainedResultBytes, long Sequence);
public sealed record OwnerLookup(bool Found, OwnerSlotSnapshot? Snapshot);
public sealed record OwnerActionReceipt(OwnerActionKind Kind, OwnerLookup Current);
public sealed record OwnerHandoffReceipt(HandoffKind Kind, OwnerLookup Current);
public interface IOcrHostSources : IAsyncDisposable
{
    IFrameLeaseProvider Frames { get; }
    IModelAssetResolver Assets { get; }
    long RetainedBytes { get; }
}
public interface IOcrProcessOwner : IAsyncDisposable
{
    OwnerTicket Reserve(string hostId, OwnerSlotLimits limits);
    OwnerHandoffReceipt AttachSources(OwnerTicket ticket, IOcrHostSources sources);
    OwnerLookup Query(OwnerTicket ticket);
    OwnerLookup FindHost(string hostId);
    LookupReceipt QueryOperation(OwnerTicket ticket, string engineEpoch, string operationId);
    OperationResourceLookup QueryOperationResources(OwnerTicket ticket, string engineEpoch,
        string operationId);
    void RecordConsumerFailure(OwnerTicket ticket, HostFailure failure);
    void RecordCleanupFailure(OwnerTicket ticket, HostFailure failure);
    void RecordHostOutcome(OwnerTicket ticket, HostOutcome outcome);
    OwnerHandoffReceipt ConfirmRetention(OwnerTicket ticket);
    ValueTask<OwnerActionReceipt> CleanupAsync(OwnerTicket ticket, TimeSpan waitBudget,
        CancellationToken observerCancellation = default);
    ValueTask<OwnerActionReceipt> RecoverAsync(OwnerTicket ticket, TimeSpan waitBudget,
        CancellationToken observerCancellation = default);
}
```

唯一实现/构造为 `public sealed class OcrProcessOwner : IOcrProcessOwner`、`public OcrProcessOwner(ProcessOwnerLimits limits, TimeProvider timeProvider)`；所有计数/字节正数、clock非null，非法ArgumentException，根ProcessEpoch用Guid小写N格式。Reserve先原子核根slots/tasks/bytes容量，再登记SlotId（Guid N）、HostId（非空唯一）和limits，**成功才允许创建source/factory/engine或调任何async端口**。root有上限、每槽不驱逐或复用身份（包含Released墓碑）；额度不足抛InvalidOperationException/Ocr.OwnerCapacity，无Factory/Task/图像副作用。slots耗尽时宿主结束已排空Owner周期，不清未知槽腾位。进程入口把根对象保留在自身生命周期变量/容器，禁止函数返回后只留下无Owner的Task。

同root的clock必须与engine/runner的TimeProvider为同一实例；构造不匹配ArgumentException，禁止cleanup与执行预算落不同钟。slot保守预留 `MaxWorkingBytes+MaxEvidenceBytes+MaxSourceBytes`，分别涵盖原operation临时/native借用、engine结果、host source驻留，容量checked且总量不超root.MaxHeldBytes。每操作Budget≤slot和engine额度；同一实际buffer只计算一次物理字节（source驻留原图不再次记为lease复制，临时复制另记），逻辑hold/lease/任务槽分别计数，不能拿共享物理去重取消借用。root同时reserve task槽：`MaxTasks ≥ 16 + MaxOperations×(8+3×MaxReleaseAttempts)`（checked，包含dispatch/原acquire/factory/read/各Dispose及有限重试）；engine.MaxOperations≤slot.MaxOperations，events/元数据仍受§3/13限额。root.MaxTasks是所有槽task上限和，不在任务Pending时腾槽。错误列表按MaxErrorsPerSlot有界，首个主错误不可覆盖，多余清理错误合并计数；MaxReleaseAttempts≥1，所有恢复都有总次数上限。

AttachSources不调用Dispose/acquire，仅核sources非null、Frames/Assets非null、RetainedBytes≥0且≤MaxSourceBytes，原子把source实例强持。Retained回执后**source的整组生命周期所有权转根槽**；engine仍只借Frames/Assets，不抢Dispose宿主端口。Rejected无转移也不Dispose调用方源；调用方须保留源并处理自己的未转移资源，不能离栈丢失；示例协议source是无IO纯托管构造，失败可本地安全释放。实际有副作用source必须由其原Owner创建并交付已被原Owner持有的对象，Attach之前不启动本模块额外acquire；root只在转移确认后使用它。source.Dispose只在所有模块lease和worker已退出后，必须幂等、completion意味着确实释放，不把异常当成功。

**调用和任务登记步骤固定：**在slot内reserve该次调用的task/资源节点→登记将调度的dispatch Task（RunContinuationsAsynchronously，root强持）→在受控后台worker执行一次RetainAsync/AcquireAsync/CreateAsync/ReadAsync/VerifyAsync→若为ValueTask只AsTask一次，立即把**同一原Task**和输入借用/返回接收continuation登记到原节点→等待真实completion。同步抛错在该节点记录，Task尚未产生也保留已取得资源。dispatch创建/绑定先于执行，不在UI或Submit锁内调用可阻塞port；不允许`Task.WhenAny`/WaitAsync观察包装替代原Task。线程/Task并发受MaxActive/MaxTasks限制，不用无限Task.Run绕过MaxWorkers。root持有source、factory、engine、clock、request快照、Frame/asset lease、worker、ct源与每次原acquire/native/Dispose Task/迟到接收continuation；只有对应native/回调不再借用且释放确认才清引用。Task异常必须观察并记稳定code，不留UnobservedTaskException或遗弃Task。

取消或deadline只freeze§4.2 StopReason并请求合作取消，**不取消迟到接收continuation或cleanup自身**。cancel后Frame/asset/factory晚到成功对象先放入同节点，再停止新视觉阶段、反序清理；迟到失败记录Primary operation error并释放先前资源。若factory Create同步阻塞或返回原Task迟到，worker dispatch与source/原输入仍由root强持；scope离栈不使其失主。业务异常和资源有两轴：OperationSnapshot.StopReason/Errors及HostOutcome/PrimaryFailure保留第一次业务失败（代码HostConsumerFailed/HostCancelled/HostDeadline/HostConstructionFailed/HostMissingResourceObservation，Stage为Construction/Observation/Consumption/Recommendation）；HostResources与CleanupFailures表示排空/释放；该snapshot.Tasks只暴露TaskView、Role固定Dispatch/FrameAcquire/AssetAcquire/WorkerCreate/Read/Verify/WorkerRelease/AssetRelease/FrameRelease/EngineRelease/SourceRelease/Recommendation/Coordinator，不暴露Task、像素或native句柄。清理异常Code固定HostCleanupFailed，Stage为Operations/Engine/Sources，CauseRef脱敏；不能覆盖主错误或把业务Failed改成Resources Released。RecordHostOutcome仅登记Completed/Failed/Cancelled/TimedOut，不能改PrimaryFailure或Resources；`HostOutcome.TimedOut`可表示Host自身观察预算到，不等于OperationState.TimedOut（原计算是否deadline由其StopReason独立决定）；engine绑定时HostOutcome=Running、创建前NotStarted。没有消费错误则PrimaryFailure=null，operation失败仍在原OperationSnapshot，不重复发明一次识读事实；成功Dispose engine之前root深持其不可变最终快照/证据与epoch作墓碑（保留额度仍受slot.MaxEvidenceBytes），不先清engine登记后再尝试抄结果。

**有限cleanup与恢复：**CleanupAsync先检查有限非负预算，原子停止engine接收（不存在engine则跳过Operations/Engine），登记唯一cleanup原Task，再观察有限budget；顺序为Operations真实排空→engine.DisposeAsync（只在Drained）→sources.DisposeAsync。预算为零时同步返回已完成的ValueTask/当前receipt，只登记原清理任务，不在调用栈执行或等待端口；Released为Completed，未释放为BudgetElapsed，未知ticket为Unknown。该Task不链接业务/observer token。观察budget到Kind=BudgetElapsed、仍持资源即Draining；observer取消Kind=ObserverCancelled，只停止本次观察。最初失败不等待cleanup吞掉原消费异常；先RecordConsumerFailure再在finally用独立预算和CancellationToken.None调用Cleanup。operation的清理协调Task不因一个释放Task fault而遗弃其它节点，尝试清理无依赖且安全的其它已取得对象后在同一协调Task等待释放确认（不后台自动重试）；每个Dispose原Task只调用一次至真正结束；Pending不重复调用，fault/cancel保持Resources=Unknown（即使托管Task终结也未证明资源释放）。DrainPending/异常全部进入slot，不当终态。

RecoverAsync同一ticket/原Task查询：某资源节点的原Task仍Pending时只继续观察该节点；cleanup整体Task可能仍在等待原operation，此时应扫描其**子资源节点**，已完成faulted/cancelled且端口幂等、native借用已结束、还未达到MaxReleaseAttempts的释放节点，**显式Recover调用**才为同一资源登记下一次Dispose attempt，观察独立预算。不得重调原Read/Create/Acquire或新Submit；尝试耗尽保持Unknown，Kind=BudgetElapsed或Completed仅表示本次观察已结束，Resources仍Unknown，不能销毁根/源。每次恢复按operation接纳序号→反序资源取得序号选择至多一个满足条件的故障释放节点，总次数在slot账内；cleanup整体Pending不阻该子节点显式恢复，新的资源成功回执唤醒同一个原operation/cleanup协调Task，不能另造新operation结束资源账。同一ticket并发Cleanup/Recover只一个执行Owner，其余等待同一原Task，原错误不覆盖。native还借Frame时绝不通过Retry Dispose绕过借用。全部operation lease/native/worker与source确认归还后Resources=Released/HeldBytes=0（仅活动借用/source/native），RetainedResultBytes单独记录仍保留的最终证据字节，持续占MaxEvidenceBytes/root额度；保留ticket/epoch、最终operation和错误墓碑供Query，不能依据HostOutcome.Completed/Task.IsCompleted或NotFound推断释放。

FindHost只读原进程注册HostId→ticket，构造失败留原槽也可找；HostId未知返回Found=false，不另建服务。Query只读内存、原ProcessEpoch+SlotId匹配；未知ticket为Found=false，不抛成功/释放。QueryOperation核原slot EngineEpoch；不匹配/原进程重启返回Lookup.Unknown，不查询新engine替代旧事实；QueryOperationResources代理原epoch原资源观察，dispose后同墓碑保留；旧epoch原operation完整未被Dispose前保存在slot，成功Dispose后仍可查墓碑。重启跨进程恢复属于宿主journal，根进程内不宣称exactly-once。ConfirmRetention是离栈的确认点：已登记且resource/task/source仍被根持有返回Retained及同ticket/epoch；全部资源释放返回Released；未知/身份错返回Rejected。Host只在Retained/Released确认后返回业务结果/异常，Rejected必须继续在原根/入口保留引用并报Owner错误，不能finally静默弃置。ConfirmRetention不开始计算、不释放资源、不证明生产完成。

Dispose根不等待无界任务：任一slot资源非Released（包括reserve未装配的Held槽）立即InvalidOperationException/Ocr.OwnerDrainRequired且注册表保留；空slotCleanup可立即转Released。所有Released时可Dispose根、释放墓碑与RetainedResultBytes；重复Dispose幂等，之后非Dispose入口ObjectDisposedException。不在用户关窗/测试用例finally无条件Dispose未排空根。

## 5. 完整处理步骤与结果质量

1. Submit 校验、固定 hash、reserve 队列与最大资源，发 RequestAccepted。质量阈值/运行配置全部来自快照，无期待字段。
2. Acquiring retain Frame、读只读完整像素/hash，取得资产闭包，逐文件核 hash/字表顺序/资格，再创建单 operation worker。factory 失败也释放先前租约。
3. 建立请求 ROI→原图→适配器裁图/旋转/缩放/补边的可回放变换，支持域不扩大。预处理由 adapter 完成，字节复制和峰值预算按 operation 计；受限资源先停止而非截断。
4. 固定一次调用的 Deep/Classic/OCV 参数，读回可查询的实际参数，native 执行期间不 Set。每个 ROI 一项、每个图一结果 dictionary，结构不足为 OCR-RESULT-001，不移位填充。
5. 按 §2 解析未纠正原读和几何，保留拒识/字符top-N/原生score语义。Detection 无识读输出；OCV 返回质量与参考闭包。低信/后端明确拒识或字符域外/支持/行序冲突为 item ReviewRequired/Ambiguous（物理OOD门见§3.1），不改运行状态为 ReviewRequired。
6. ObservationChecking 只查字符域/长度/结构和同后端分数资格；格式/期待比较归宿主。过长完整原读仍保留，超过证据硬预算则 operation Failed、无伪完整内容。
7. 深复制完整证据和所有响应，销毁 adapter 临时字典/结果对象，等待 native/回调退出，Dispose worker，再释放资产/Frame；释放失败保持 Quarantined，资源账目未闭合不得 Terminal。
8. 发布一次终态 snapshot。宿主从 snapshot 保存证据/做内容比较/OCV质量判断/人工复核；保存或 MES 失败不能修改已经冻结的观察。

OCR视觉调用无内部重试或备用循环（§4.4显式幂等释放恢复不属于重跑识读）。宿主明确 Profile 的次数/资源/时间预算后，用新 OperationId/IdempotencyKey 执行已批准路线，记录 attempt 链；配置错误、业务不一致、低信/OOD不自动重试。native 未排空不能复用其 worker，不能把调用等待超时当已停止。

## 6. 稳定错误码与恢复

完整前缀为 OCR-；字段使用 §3.2 OcrError。MessageKey固定为 `Ocr.Error.<完整Code>`，Stage固定为Validation/Admission/Acquiring/QualityChecking/Detecting/Recognizing/DetectingAndRecognizing/Verifying/Ordering/ObservationChecking/Draining/Diagnostics之一；不把任意异常message当键。Code 不翻译，MessageKey 映射三语，CauseRef 不包含未脱敏 native 文本/像素。未知错误 fail closed，不能返回 Empty/Read。

| 错误码 | 语义/作用点 | 恢复 |
|---|---|---|
| OCR-INPUT-001 | 必填值/空ROI集/重复ID/hash格式 | 修正请求 |
| OCR-INPUT-002 | 像素格式、stride、尺寸/溢出 | 提供合法Frame |
| OCR-INPUT-003 | ROI/支持/坐标域非法 | 修正几何 |
| OCR-METHOD-001 | 模式、字符域、参数组合或预算非法 | 修正冻结Profile |
| OCR-ASSET-001 | 文件/字表/预处理缺失、hash/资格不符 | 修复闭包，新请求 |
| OCR-ADAPTER-001 | 路线/能力不支持或具体签名存在实现歧义 | 换批准路线；只阻断该适配切片 |
| OCR-ENGINE-001 | 后端调用失败 | 排空后按宿主预算新attempt |
| OCR-RESULT-001 | 输出数目/必需键/几何/score结构异常 | Failed，保留诊断 |
| OCR-RESULT-004 | 超长/候选/证据预算超限 | 超长观察ReviewRequired；无法保全证据Failed |
| OCR-QUALITY-001 | 不可观察、低信 | 复核或宿主重拍 |
| OCR-QUALITY-002 | OOD/拒识/行序/字符域/支持冲突 | 复核，不按期待改字 |
| OCR-OCV-001 | 参考/模式不可用 | NotComputed，修复参考 |
| OCR-RUNTIME-001 | engine已停止接收 | 原ID查询；宿主完成归档后新epoch |
| OCR-RESOURCE-001 | queue/working/retained/登记容量不足 | 等排空，或宿主归档后新epoch |
| OCR-TIMEOUT-001 | deadline到而执行未停 | 排空；Pending非终态 |
| OCR-CANCEL-001 | 明确请求取消 | 实际排空后Cancelled |
| OCR-IDEMPOTENCY-001 | OperationId重用冲突 | 修复身份生成 |
| OCR-IDEMPOTENCY-002 | 同key异hash | 不覆盖原operation |
| OCR-DIAG-001 | 诊断sink失败 | 从Query恢复投影，不改原读 |
| OCR-DRAIN-001 | native/回调/租约释放未确认 | 隔离/计费/继续查询 |
| OCR-INTERNAL-001 | 未分类内部异常 | Fail closed，附correlation |

item.RejectReason为表内稳定OCR错误码或null，ReadingOrder固定SingleWord/LeftToRight/RightToLeft/Unresolved；理由补充在trace.ObservationCodes，不把自由英文句子直接塞UI。推荐Reasons固定以 `roi:<RoiId>/<WordId>:<key>` 或 `candidate:<CandidateId>:<key>` 表示；key集合为InvalidGeometry/OutsideFrame/InsufficientSupport/RelatedWords/ProposalLimitReached/MissingTrial/NotDrained/ExecutionFailed/MissingTiming/FalseAcceptLimit/RefusalLimit/LatencyLimit/ResourceLimit/NoCandidates/NoSamples/NoLimits。UI按最后key映射 `Ocr.Reason.<key>`三语，ID仅作定位不翻译；结构错误抛异常的message键与§3.5一致。

Retryable=true 只给已确认可恢复的瞬时资源/运行故障，不赋予核心自动重试权。等待取消不是 OCR-CANCEL-001；宿主保存错误不占 OCR-INTERNAL-001，不伪装模块计算失败。

## 7. 所有权、线程、取消与释放

- 图像 provider 拥有原缓冲，RetainAsync 成功后返回独立模块lease；provider 可释放自己的引用，但必须确保 lease 在 DisposeAsync 前像素不可变/不回收。只读Memory不是安全证明，provider 必须履行此所有权。失败 acquire 无租约，成功后由核心恰一次Dispose。
- asset resolver 返回独立只读blob租约，model/OCV句柄由worker创建。每operation一个worker，禁止跨operation可变handle共享；可由factory内部池复用已排空、完整重置的对象，但公共语义不变。
- 成功/异常/取消/timeout均在同一清理路径，释放失败仍计费。HDict/HTextResult/临时HObject不跨adapter边界，不编造 clear_deep_ocr/clear_ocv 算子；按真实公开对象生命周期实现。
- CancellationToken 只合作式请求，adapter不得在native尚读取Memory时提前返回；不可抢占调用占用隔离worker直至真实返回。宿主超预算选维护/进程策略属部署决定，不能销毁仍使用的缓冲再继续同进程。
- 一个operation的事件/快照序列串行，独立operation可并行；native线程能力由factory显式声明，MaxActive不得超过声明，运行调参/热换模型禁止。外部sink在锁外调用，catch后诊断，不持UI Dispatcher锁。
- 新资产/profile只供新operation；停止旧epoch接收→原Owner槽有限cleanup/接管→排空→归档→销毁。UI关闭仅撤订阅，宿主runtime继续负责排空。core不启动隐藏窗口或读取全局语言/主题。

## 8. 自包含适配与资源端口

```csharp
public interface IFrameLease : IAsyncDisposable
{
    OcrImageRef Image { get; }
    ReadOnlyMemory<byte> Pixels { get; }
}
public interface IFrameLeaseProvider
{
    ValueTask<IFrameLease> RetainAsync(OcrImageRef image, CancellationToken ct);
}
public sealed record AssetBlob(AssetRef Identity, ReadOnlyMemory<byte> Bytes);
public interface IModelLease : IAsyncDisposable
{
    ModelSnapshot Snapshot { get; }
    IReadOnlyList<AssetBlob> Blobs { get; }
}
public interface IModelAssetResolver
{
    ValueTask<IModelLease> AcquireAsync(ModelSnapshot snapshot, CancellationToken ct);
}
public sealed record AdapterCapabilities(string AdapterId, string Version,
    string RuntimeVersion, IReadOnlyList<OcrBackend> Backends,
    IReadOnlyList<OcrMode> Modes, bool OcvSupported, bool CharacterCandidates,
    bool RecognitionAlignment, int MaxPixels, int MaxRois, int MaxWordsPerRoi,
    int MaxCharacters, int MaxCharacterTopN, int MaxTiles, int MaxWorkers,
    long MaxWorkingBytes, long MaxEvidenceBytes, int MaxMetadataUtf8Bytes,
    bool NativeCancellationSupported, string ScoreMeaning,
    double? ScoreMin, double? ScoreMax, bool HigherScoreIsBetter);
public enum AdapterStage { QualityChecking, Detecting, Recognizing, DetectingAndRecognizing, Verifying }
public interface IOcrAdapterProgress { void Report(string roiId, AdapterStage stage);
    void ReportWorkingBytes(long bytes, bool observationComplete); }
public sealed record AdapterInput(OcrRequest Request, IFrameLease Frame,
    IModelLease Assets, string MethodSnapshotSha256, IOcrAdapterProgress Progress);
public sealed record OcvAdapterInput(OcvRequest Request, IFrameLease Frame,
    IModelLease Assets, string MethodSnapshotSha256, IOcrAdapterProgress Progress);
public sealed record AdapterReadResult(IReadOnlyList<OcrItemResult> Items,
    OcrEvidence Evidence, IReadOnlyList<OcrError> Errors);
public sealed record OcvAdapterResult(OcvObservation Observation,
    OcrEvidence Evidence, IReadOnlyList<OcrError> Errors);
public interface IOcrAdapterWorker : IAsyncDisposable
{
    ValueTask<AdapterReadResult> ReadAsync(AdapterInput input, CancellationToken ct);
    ValueTask<OcvAdapterResult> VerifyAsync(OcvAdapterInput input, CancellationToken ct);
}
public interface IOcrAdapterFactory
{
    AdapterCapabilities Capabilities { get; }
    ValueTask<IOcrAdapterWorker> CreateAsync(CancellationToken ct);
}
```

同一factory只注册一个OcrBackend（Backends恰1），避免不同模型分数语义混入一个能力声明；OcvSupported可同时提供独立Quality路线，OCV不使用OCR ScoreMin/Max。Capabilities的各计数/字节必须>0；ScoreMin/Max均null表示无可阈值分数，否则两者有限且min≤max，ScoreMeaning非空。HALCON Deep softmax范围0..1且HigherScoreIsBetter=true；传统MLP按官方confidence语义，同样显式声明；未校准不叫概率。MinEngineScore在该闭域内，方向按HigherScoreIsBetter检查；无分数能力拒绝非null阈值。

Progress报告实际当前RoiId内已开始的阶段；core过滤未知/重复/回退/迟到报告，同一ROI阶段单调、ROI按请求顺序处理，operation.Sequence始终单调（不同ROI可重新进入同一路线阶段）；不由core在等待一个不可见native调用时伪造Detecting已完成。回调不传UI/native对象，必须在Read/Verify completion前结束，adapter清理不发新阶段。

所有port返回对象字段须与请求一致，图像Pixels长度恰stride×height、资产byte长度/hash精确匹配。worker每operation只调用一次Read或Verify，不重入；不支持返回OCR-ADAPTER-001。Read/Verify 的成功、fault或cancel completion **必须意味着所有native/回调已退出且不再读输入**；worker Dispose释放内部对象后才可归还Frame/Assets。adapter不能用Task.WhenAny把“观察超时”包装为调用completion；core有界Wait独立实现。若Dispose/租约释放未确认，保持Quarantined并查询，不把timeout返回当free证明。所有端口DisposeAsync必须幂等，成功完成才证明释放；失败保持资源所有权，StopAndDrainAsync重新观察同一个待完成释放任务；已faulted释放需要§4.4的显式RecoverAsync、有次数上限的幂等释放尝试，不无界自动重试或并行Dispose。不可恢复释放失败需宿主维护，不发布终态。租约成功释放不需要再次Dispose；重试观察失败的释放任务不会假称释放成功或再次启动native。

provider/resolver/factory应响应合作取消；若自身不可抢占也归同一隔离/计费规则，晚到的成功lease必须接管并清理，不能被遗弃的Task丢失。异常由core映射稳定错误，公共签名不露HTuple/HObject/SDK地址。

### 8.1 HALCON 适配器唯一公开装配

工程/程序集唯一为§16.1 `Asun.Modules.Ocr.HalconAdapter`，namespace=`Asun.Modules.Ocr.HalconAdapter`。本节是该适配程序集公开API，不改变§3 Core DTO/canonical；不能再以“适配工程未绑定”为缺口。公开配置如下（using Asun.Modules.Ocr）：

```csharp
public sealed record HalconAdapterOptions(OcrBackend Backend,
    OperationBudget Limits, int MaxWorkers);
```

公开工厂类准确为 `public sealed class AsunImageHalconAdapter : IOcrAdapterFactory`，构造为 `public AsunImageHalconAdapter(HalconAdapterOptions options)`，唯一公开成员是 `public AdapterCapabilities Capabilities { get; }` 和 `public ValueTask<IOcrAdapterWorker> CreateAsync(CancellationToken ct)`。不提供static Default/隐藏注册器/公开HALCON handle、第三套执行入口或生产模型加载开关；worker类及算子资源均internal。Core的OcrEngine仍只注入IOcrAdapterFactory，不引用该程序集。

构造只校验/深复制配置并生成只读能力，不加载模型、读文件、调用native或创建线程。options/limits null、Backend不是HalconDeepOcr/HalconClassic、计数/字节/DeadlineMs非正或checked溢出、MaxWorkers非正时抛ArgumentException（Ocr.InvalidHalconAdapterOptions），无部分注册/资源副作用。Limits作为该安装Profile的最大支持域，各请求Budget不得超过它；不是客户性能承诺。Capabilities映射：AdapterId=`AsunImageHalconAdapter/<Backend名>`、Version为本适配程序集发布版本、RuntimeVersion=`HALCON 26.05.0.0`（目标语义版本，运行实测值另存trace）；Backends仅options.Backend；Deep Modes为Detection/Recognition/Auto、Classic仅Recognition；OcvSupported=true、CharacterCandidates=true、RecognitionAlignment仅Deep为true、NativeCancellationSupported=false；所有Max字段由Limits/MaxWorkers一一映射。DeadlineMs不在AdapterCapabilities字段中，worker在加载native前额外检查请求DeadlineMs≤options.Limits.DeadlineMs；不满足METHOD-001且没有native分配，不默默缩短请求deadline。ScoreMeaning分别为DeepOcrSoftmaxUncalibrated/ClassicMlpConfidenceUncalibrated，ScoreMin=0/ScoreMax=1/HigherScoreIsBetter=true。能力声明不是资产资格：alignment/组件/字表/实际runtime在每次加载后read-back核对，不具备即拒绝该请求，不能静默换模型或开并行。

工厂不拥有provider/resolver、native池或活动worker，不实现IAsyncDisposable，不取得SDK全局所有权。CreateAsync首先检查ct，取消抛OperationCanceledException且未创建worker；成功返回新的、未加载模型的internal IOcrAdapterWorker，以受控托管完成ValueTask交付，不启动后台native。返回后取消由engine负责该worker清理，不能遗弃迟到对象。worker由本次engine operation唯一拥有，工厂不缓存/复用/在宿主关闭时抢Dispose它；MaxWorkers由engine Options.MaxActive和全局预算约束，多个engine共享同一factory时宿主为各engine分配额度，总MaxActive不得超过该factory配置。

**资源取得与失败回滚：**engine先持有Frame/model blob lease→Create空worker→Read/Verify校验快照/资产字节→按Route加载实际模型/OCV/reference/文本模型→设置/读回参数→建裁图/临时对象→执行→转换完整只读观察与trace。worker把每次成功分配立即登记，失败或合作取消停止后续分配；native仍在调用时不清图像。所有native/回调返回后，临时结果/字典/图像按反向取得顺序清理，再释放模型等内部对象；能安全清理的独立对象均尝试清理，单项失败不跳过其余项。内存输出在清理前深复制、不得携native地址。

安全清理已确认完成，才让Read/Verify成功、fault或cancel完成并由engine调用幂等DisposeAsync；Dispose成功后engine再归还资产/Frame lease。初始化中途失败也遵循同一路径，产生ENGINE-001/ASSET-001/ADAPTER-001中的对应诊断。**任何私有资源释放不确定时Read/Verify仍保持未完成**，worker保留资源账并在同一内部清理任务等待确认；engine有界Wait/StopAndDrain得到Pending/Quarantined、继续计费，不把抛异常当已排空证据。Dispose路径新发现释放失败同样非终态，记录DRAIN-001并保留资源；不重建worker自动重跑，也不以GC/强杀代替释放证明。工厂本身无失败后残留native，由worker回滚而非factory.Dispose掩盖。

装配Owner为丝印/标签宿主runtime，使用§9.6准确构造：进程root先Reserve→宿主取得/Attach有借用生命周期的source（提供Frame provider/model resolver）→创建HalconAdapterOptions及factory→以IOcrAdapterFactory和原OwnerTicket注入OcrEngine→明确Submit/查询→root独立有限Cleanup（内部StopAndDrain/Dispose engine/Dispose本次source借用）→ConfirmRetention后局部Host退出，root Released后再结束进程资源。建立engine之前失败，没有operation/native，可回滚本次宿主新建依赖（不Dispose借用依赖）；提交后失败或关闭Pending，宿主必须把engine及其依赖留在runtime继续管理，不能finally抢释。共享engine只有runtime Owner可关闭，卸载任一控件不能关闭共享服务。

适配器只用HALCON26.05经ImageLibDotNet.cv2；具体C#类型/重载确有歧义才定向查公共签名/编译，不核算子存在。批准外部adapter保持§8同端口和独立资产/分数规则；未批准Paddle不装入生产factory。当前仅冻结装配与回滚规格，真实模型/算子/排空验收未执行。

### 8.2 HALCON worker：字节、参数资产、逐路线与原读

本节补齐H的实现设计，不改已接收Value v0.2/C2 Service v0.3、§8.1工厂签名或原任务根。算子名均为26.05目标语义，经`cv2`调用；这些是处理顺序与参数规格，不冒称已编译C#封送示例。每worker单一受控线程串行处理请求ROI，所有model/tuple/image/result的native生命周期留在此线程；只读响应在离开前复制。Frame、assets、物化目录/permit直到原native与回调退出才释放。

**三个描述文件及codec。** H只接生产者明确选用的`ocr-halcon-assets/1`绑定；协议fixture文件保持原意，不送H。`charset` UTF-8 JSON固定`ContractVersion="ocr-charset/1",OrderedSymbols,BlankSymbol,MappingId,MappedSymbols`；`preprocess`固定`ContractVersion="ocr-preprocess/1",ProfileId,Gray16Min,Gray16Max,Invert,DirectionDeg,Revision`，排除Sha256自身。分别与§3.6模型/Preprocess字段逐项一致，Preprocess.Sha256必须等于该blob的raw SHA-256。`runtime-profile`固定`ContractVersion="ocr-halcon-runtime/1",Value`，Value按下方record声明顺序，所有nullable键显式null。对应资产raw hash/length进入既有Files/Method hash；新增内容只用于新资产修订，不重新规范旧文件或让纯值C1解析H codec。

```csharp
// namespace Asun.Modules.Ocr.HalconAdapter；只属于H，不加入Value请求声明。
public sealed record DeepDetectionRecipe(double MinCharacterScore, double MinLinkScore,
    double MinWordAreaPx2, double MinWordScore, bool SortByLine);
public sealed record TextAutoRecipe(double MinContrast, double MinStrokeWidthPx,
    double MaxStrokeWidthPx, bool AddFragments, bool SeparateTouchingChars,
    bool ReturnPunctuation, bool ReturnSeparators, bool DotPrint,
    bool TightDotSpacing, double MinDotCharacterGapPx, double MaxDotGapPx);
public sealed record TextManualRecipe(double CharacterHeightPx, double CharacterWidthPx,
    double StrokeWidthPx, double BaseLineTolerance, bool UppercaseOnly, bool DotPrint,
    bool Imprinted, bool EliminateHorizontalLines, bool ReturnPunctuation,
    bool ReturnSeparators, bool AddFragments, double MinFragmentAreaPx2);
public sealed record HalconRuntimeRecipe(string RuntimeVersion, string? DeviceRef,
    int? RecognitionBatchSize, string IntZooming, DeepDetectionRecipe? Detection,
    TextAutoRecipe? TextAuto, TextManualRecipe? TextManual);
public sealed record HalconRecipeDecodeResult(HalconRuntimeRecipe? Recipe,
    IReadOnlyList<OcrError> Errors);
public static class OcrHalconRecipeCodec
{
    public static HalconRecipeDecodeResult Decode(ReadOnlyMemory<byte> utf8,
        long maxBytes, int maxErrors);
    public static ReadOnlyMemory<byte> Encode(HalconRuntimeRecipe recipe, long maxBytes);
}
```

Codec采用BCL Utf8JsonReader/Writer，UTF-8严格、无BOM/注释/尾逗号、重复/未知/缺键拒绝；最大深度8，字节与错误数先核上限，不先复制超长bytes。Decode还要求原输入等于重编码的canonical bytes（同§3.4写数字、enum/string/null规则），坏输入Recipe=null、Errors非空（OCR-METHOD-001/Stage=Acquiring）；Encode非法/超预算抛ArgumentException，返回独立只读bytes。三份描述文件用相同严格结构/计费规则；charset/preprocess只产生内部解析值，不另开public DTO。所有数值有限：Detection三个score在[0,1]、面积>0；TextAuto contrast在[1,255]、stroke≥1且min≤max、最小字符gap≥0/最大dot gap≥1；Manual字高/宽/stroke>0、基线容差[0,1]、fragment面积≥1；IntZooming仅`true/false`，RuntimeVersion必须HALCON 26.05.0.0。Decode只核独立结构，路线组合在worker对照原请求校验：Deep Detection/Auto恰有Detection，Recognition为null；TextAuto/Manual分别恰有相应record，Segmented/Deep/OCV无Text配置。Deep.DeviceRef非空且与Deep.DeviceId一致、RecognitionBatchSize正（Detection-only为null），其它路线device/batch为null。由Profile/训练资格决定这些物理参数；公开默认只有显式拒绝，不能抄手册示例成生产值。

**像素与仿射。** 先核完整stride×height及hash；Gray8/Gray16按行复制去padding、Gray16读little-endian，在`gen_image1(byte/uint2)`调用全程pin准确地址；该算子复制存储，返回后才释放pin。RGB/BGR分离成三份无padding byte plane→三次gen_image1→compose3，BGR显式交换plane；不调用零复制gen_image1_extern，不泄漏指针。Gray16按§3.1线性截断和away-from-zero舍入得到byte，再建HALCON图；RGB需要灰度时`rgb1_to_gray`，显式Invert用`invert_image`。副本和native都计预算，失败也归原节点清理。

对于每ROI，令θ=(ROI.AngleDeg+Preprocess.DirectionDeg)·π/180，c为§3.1中心，u=(cosθ,sinθ)、v=(-sinθ,cosθ)，W=ceil(WidthPx)、H=ceil(HeightPx)，checked正整数且不越像素/字节限额。输出像素中心(i,j)对应Frame `p=c+u·((i+0.5)·WidthPx/W-WidthPx/2)+v·((j+0.5)·HeightPx/H-HeightPx/2)`。由此得到ImageToFrame及其唯一逆FrameToImage；Direction旋转后的四角/采样支持必须仍在Frame与原凸支持内，失败不填黑扩大有效域。HALCON矩阵以(row,column)而非(x,y)排列：若FrameToImage为§3.6的M，其tuple为`[M22,M21,M23,M12,M11,M13]`，再按官方像素中心补偿`hom_mat2d_translate(H,0.5,0.5)`→`hom_mat2d_translate_local(...,-0.5,-0.5)`→`affine_trans_image_size(...,'bilinear',W,H)`。先`get_system('int_zooming')`核等于recipe，不更改进程全局system参数；不一致拒H路线。支持检查覆盖双线性四邻像素的原有效域（零权重邻点可略），不靠reduce_domain阻止该算子读域外；域不足为QUALITY-001，禁止补零后当完整文字。trace记原矩阵、实际尺寸、所有复制/转换/裁图和ValidSupport，不把HALCON预处理图当Frame。

| 路线 | 固定算子/参数/结果顺序 | 冻结拒绝与证据 |
|---|---|---|
| Deep | §8.3已guard入口→read_deep_ocr→get_deep_ocr_param核需要的组件、alphabet_internal/mapping/alignment_available→按真实设备descriptor分别设置所需detection_device/recognition_device，recognition_batch_size/recognition_num_char_candidates/recognition_alignment；Detection/Auto显式set detection_image_size=[实际32倍数W,H]、detection_tiling/overlap、四项min_*、sort_by_line及orientation=`auto`→逐参数get回读（detection_image_dimensions仅get核[W,H,3]）→apply_deep_ocr(一ROI一图, mode)→get_dict_tuple/get_dict_object解析→复制输出→clear_dict、清image、clear_handle(fresh Deep模型) | 不set alphabet/mapping/model，不使用隐式HALCONROOT模型。words中row/col/phi/length1/length2才是该crop输入域；phi为数学正向，转换图像顺时针角需取负号后经ImageToFrame回到Frame。Recognition无框输出，用实际输入ROI框，标Geometry=InputRoi，不伪造定位。每图dictionary恰1，不按缺项移位 |
| SegmentedCharacters | 灰度byte→threshold或auto_threshold(显式Sigma)→connection→select_shape(area,width,height,'and',Profile上下限)→sort_region('upper_left','true','column')→逐select_obj/do_ocr_single_class_mlp(Num=CharacterTopN)；Num=1亦固定single，避免两份映射实现 | auto_threshold是多区间，不把所有区间union；逐区间`min_max_gray`（Percent=0）取区间灰度极值，仅全落在ThresholdMin/Max内者进入分割。多个非空合格区间各保留独立观察并Ambiguous，不按期待/最高分挑一个；零候选Empty。过滤计数入trace，不声称排除的小域必是噪声；边界字符/重叠矩形/不完整支持ReviewRequired |
| TextModelAuto | read_ocr_class_mlp→get_params_ocr_class_mlp/实际拒识资格核→create_text_model_reader('auto',该classifier)→显式set参数→find_text→get_text_result(num_lines/num_classes)→按line索引get_text_object(['line',i])、get_text_result(['class_line',i,rank]/['confidence_line',i,rank])→复制→clear_text_result/clear_text_model→clear_ocr_class_mlp | 每rank/region数匹配，actual num_classes小于请求时保留实际N，不复制rank；rank0拒识不取second-best替换。行少于2字ReviewRequired/QUALITY-002，非空分割不报Empty |
| TextModelManual | create_text_model_reader('manual',空classifier参数)→显式manual参数→find_text→get_text_result('manual_num_lines')→get_text_object(['manual_line',i])及get_text_object('manual_compensated_image')→每region在该增强图用独立已读MLP的do_ocr_single_class_mlp→清理同上 | manual不调用auto-only class_line接口；manual≥3字。未获得该最少行结构仍为ReviewRequired，无隐藏改用Deep |
| OCV | read_ocv(guard入口)→同ROI灰度byte/支持检查→do_ocv_simple(PatternName,AdaptPosition/Size/Angle=false/Gray,Threshold)→复制Quality/参考身份→close_ocv→清image | PatternName来自明确请求，不猜第一个pattern；算子拒不存在pattern→OCR-OCV-001/NotComputed。Quality有限且[0,1]，无识读候选；没有新训练副作用 |

TextAuto的Min/MaxCharHeight/Width由Classic四字段传入；polarity由DarkOnLight取dark_on_light/light_on_dark；MinContrast与stroke/dot各值来自recipe。`eliminate_border_blobs=false`，`add_fragments/return_punctuation/return_separators/dot_print/dot_print_tight_char_spacing`来自recipe，`separate_touching_chars`为true→`standard`、false→`false`（不引入enhanced外部support文件）；`text_line_structure/text_line_separators`为空、return_whole_line=true、num_classes=预算N。MinDotCharacterGapPx→dot_print_min_char_gap、MaxDotGapPx→dot_print_max_dot_gap；两值显式数值时HALCON忽略tight spacing，记录该事实，不声称三个参数都有独立效果。Manual映射唯一如下，bool传HALCON字符串true/false，不猜字段前缀。

| TextManualRecipe字段 | set_text_model_param名字 |
|---|---|
| CharacterHeightPx / CharacterWidthPx / StrokeWidthPx | manual_char_height / manual_char_width / manual_stroke_width |
| BaseLineTolerance / UppercaseOnly | manual_base_line_tolerance / manual_uppercase_only |
| DotPrint / Imprinted / EliminateHorizontalLines | manual_is_dotprint / manual_is_imprinted / manual_eliminate_horizontal_lines |
| ReturnPunctuation / ReturnSeparators / AddFragments / MinFragmentAreaPx2 | manual_return_punctuation / manual_return_separators / manual_add_fragments / manual_fragment_size_min |

BaseLineTolerance直接传无量纲比例（如0.15），不乘100，不取本例为默认。manual_polarity来自DarkOnLight，manual_eliminate_border_blobs=false，manual_max_line_num=MaxWordsPerRoi+1（checked探查额外行，超预算拒，不截掉最后一行），manual_text_line_structure为空、manual_persistence=true。逐get_text_model_param保存实际值；未写字段只有HALCON26.05文档明确不适用于本Mode的字段，不留版本漂移默认。模型配置全部在find_text前，执行期间不变。

**私有释放失败的恢复界限。** worker持有每项资源、释放调用原Task及确认状态。原释放仍Pending时只观察同任务；原调用已明确失败且不能证明对象仍有效/可安全再次clear时不重发clear，Read/Verify仍Pending，隔离原worker并继续计费。本版不提供重新生成HALCON handle或重建worker的恢复路径；§4.4 Recover只能恢复它已持有且允许幂等释放的公开任务，不能把未完成Read中的native未知对象变成已释放。没有原native完成/释放确认则保持Quarantined，由runtime Owner保留原节点，不能报告“已恢复”；其它独立安全资源仍尝试清理。该不可恢复分支也纳§12，不能以超时或GC结清。

**原读映射固定。** Deep Auto按word索引取char_candidates字典；Recognition直接取char_candidates tuple，不复刻CTC。每位置candidate/confidence等长，rank从0、score用DeepOcrSoftmaxUncalibrated；Blank标IsBlank且不当空格。HALCON没有提供native整词score时Word.Score=None/Unavailable，不用平均/最小字符分数冒充native word score；MinEngineScore逐非Blank rank0位置核，缺必需分数ReviewRequired，ComparisonRule=PerCharacterWinner写trace。MLP `U+001A`为native拒识符号（独立IsRejection=true），保留原rank0符号不注入次优，Word.Score亦None；MinEngineScore逐字符winner核。RawText为原行region序列的winner符号连接（拒识符号保留），不自动插入空格/删标点；RTL只反转同已证明行内region展示次序，不双向文本整形。只有分割字符各行垂直区间交集非空、横向区间互不重叠时才合成一个SingleWord；否则各字符独立词、LineOrdinal=null/ReadingOrder=Unresolved/Ambiguous，不能凭sort_region编造行归属。TextModel用原line_index/line序号，不按相同字串去重。

Deep框4角由c±(cosφ,-sinφ)·length1±(sinφ,cosφ)·length2构造，按局部左上开始顺时针，再经crop逆矩阵；长度/字段数/非有限/超预算均RESULT-001/004。Recognition InputRoi四角用§3原ROI（Direction属于内部旋正，不改外部目标身份），SupportComplete须同时满足实际采样支持。任何已有词框正面积重叠时分别保留、RelatedWordIds双向记录并Ambiguous；不按业务期待消歧。Deep tiling的计数按本26.05参数与输入尺寸上界预约：每维`1+ceil(max(0,inputSize-modelSize)/(modelSize-overlap))`，两维checked乘积≤MaxTiles；HALCON未公开逐tile来源时trace标TileSupportNotObservable，该模式结果最高ReviewRequired，不猜接缝支持或自动词融合。组件/字符域/运行版本/readback不符拒绝原请求，无备用路线；复杂背景/物理未知字的正确性以§12H/P真实样本验证，软件不能保证仅高softmax就检出OOD。

Classic几何统一以各字符region的smallest_rectangle1取得包含像素中心的闭区间，外边界为(col1-0.5,row1-0.5)至(col2+0.5,row2+0.5)，顺时针四角再经ImageToFrame；Text行/已证明SingleWord的框取同一行全部字符region的union1后按同法求框。这是实际分割支持的轴向包围框，不是字符笔画真值或原生词置信度。扩出的外边界缺有效支持时SupportComplete=false并ReviewRequired，不静默clip。Manual增强图作为derived新role记录完整bytes/hash/父裁图、identity几何及增强步骤，分类用该图；原frame/crop证据保留，不把增强图当未处理原图。各rank的N由实际返回长度保真，缺候选不复制rank0补齐。

### 8.3 model-assets 0.3.1 公开消费与HALCON物化桥

上游权威为[IM-014附录B/C.1～C.9](../model-assets/DEVELOPMENT-GUIDE.md#附录-c全批准范围的具体适配设计v031)。本节是OCR自己的mapper/Owner设计，Core不依赖上游类型，不改其Core/Service合同。桥放既有HalconAdapter DLL/测试工程的`Assets/`，namespace仍`Asun.Modules.Ocr.HalconAdapter`，单向引用`Asun.Modules.ModelAssets`及`.Service`；无新DLL、私有表/SDK或反射。以下为本轮待实现公开声明，MA/MAS分别是上述namespace别名；不把MA.AssetRef与§3的OCR.AssetRef当相同类型。

```csharp
public sealed record OcrAssetFileBinding(string OcrRole, MA.AssetRef OwnerRef,
    string Role, string LogicalPath);
public sealed record OcrModelAssetBinding(ModelSnapshot Snapshot, MA.AssetRef ExactRef,
    MA.FormatDescriptor Format, IReadOnlyList<OcrAssetFileBinding> Files);
public sealed record OcrAssetBridgeProfile(string Id, string Revision,
    MAS.ModelAssetsScope Scope, MAS.AssetAccessRequest Access, MAS.OperationBudget Budget,
    int MaxAcquires, int MaxFiles, long MaxResidentBytes, int MaxErrors);
public sealed record OcrAssetBridgePorts(MAS.IModelAssetService Service,
    MAS.IModelAssetStore Store, MAS.IAssetUsageAuthority Authority,
    MAS.ModelAssetsHostSlot RootSlot, TimeProvider Clock);
public sealed class OcrModelAssetsResolver : IModelAssetResolver, IAsyncDisposable
{
    public OcrModelAssetsResolver(OcrAssetBridgeProfile profile,
        IReadOnlyList<OcrModelAssetBinding> bindings, OcrAssetBridgePorts ports);
    public ValueTask<IModelLease> AcquireAsync(ModelSnapshot snapshot, CancellationToken ct);
    public ValueTask DisposeAsync();
}
```

构造只校验深复制，不能I/O：profile/端口/各引用非null、所有上限正且checked；RootSlot.Scope/Service.SessionInfo.Scope相等，PrincipalRef匹配，Access.RequiredAction=ReadForUse，UsagePurpose由宿主冻结生产/Replay/Shadow/Advice目的，服务Production不能接Simulation。binding.Snapshot逐字段与OCR请求exact比对，不能靠AssetId/latest；文件OcrRole恰覆盖§3.6且无重复，映射的(ownerRef,role,path)均唯一，Format.Entrypoint必须由Layout中一个原文件确定；core文件role的实际raw length/hash等于该ClosureFile.Entry，MA.Digest必须`raw-file-sha256-v1/sha256`32bytes，其他rule不能剪hex冒OCR.ManifestSha256。Snapshot.ManifestSha256沿OCR资产描述身份保持；ExactRef是MA完整Ref，由宿主保留explicit映射，不把MA核心摘要直接当raw描述摘要。格式Layout/入口、组件文件扩展名由原producer Format冻结，不从用户路径猜reader。

每Acquire先在两个原根预留限额/节点，生成一次桥epoch（Guid N）+接纳ordinal的稳定操作身份，原节点存Context/RequestDigest/Ref/role，不以worker晚到新建替代身份。MA根先KeepAnchor本resolver/借用Service/Store/Authority及mapping→StartCall保存端口原Task（ValueTask只AsTask一次），OCR原根仍保存同一个Acquire返回Task与输入。跨根不是转移Owner后忘记原Task；晚到成功对象仍在原OCR节点接管。Acquire没有公开operation参数，因此内部ordinal身份由mapper只生成一次并随该原Task保持，不重新使用原Snapshot重复身份掩盖并发。

Host在构造桥之前Reserve原MA slot并一次SetCleanupPlan；plan的HostLifetime先保“未创建/构造中/已交付”的桥与全部原Task，关闭action只Dispose本Host拥有的桥、归还本Host借用，不Dispose共享Service/Store/Authority。构造成功先KeepAnchor一次桥及冻结mapping，retainedBytes计实际canonical mapping字节与已预约节点metadata；流/blob后续驻留由该锚点内有界账计入MaxResidentBytes及MA root预算，不每次请求追加不可撤anchor。MaxAcquires是该桥整个生命周期累计接纳上限，含已归还记录，根MaxCallsPerHost至少覆盖每Acquire的Resolve、Authority、Hold、逐文件Open、Materialize及各释放/查询调用的保守上界；不足在I/O前拒绝。达到容量后停止新接纳，待原租约全部Released再由Host归档、Dispose桥/原slot并建立新桥epoch；不在活跃桥清记录重用ordinal。DisposeAsync原子封接纳，等待其原Acquire及已交付lease按原Owner归还；没有使用者归还不能主动抢释，原Dispose Task保持Pending，由外层root有限观察。没有实际零资源确认不成功Dispose，重复调用观察同清理任务。两个根分别计自己的metadata/借用与本方实际bytes，共享bytes物理峰值按Owner去重，不能两边都填0。

resolver、挑战executor与MA reader若用同slot，由Host在第一个call前只设这一份覆盖全部自有对象的cleanup DAG；各组件不能覆盖或再次SetCleanupPlan。Acquire初始化中失败/取消时先对已取得的read/materialization/hold/watch/permit按同反序路径收尾；本内部原清理任务及迟到接收挂原MA/OCR节点。全部资源确认Released才允许Acquire fault/cancel完成；释放未知时Acquire原Task保持Pending而非抛错遗弃尚未交付的租约。已有借用不因MA outer Wait到期转移Owner。

1. `ResolveExactAsync(AssetResolveRequest)`：Purpose=Runtime；按`ModelAssetRequestProjection.ProjectResolve`计算完整RequestDigest后替换Context占位digest，合法才发；Outcome=Succeeded、Value非null、Completeness=Complete、UnverifiedLegacyRefs空、RootRef=原ExactRef才继续。StoreView/GraphRefs/Edges完整保存；HistoryAllowed不能作为ReadForUse许可。
2. 构造本次`ContentLeaseRequest(loadContext,原closure,Access)`，用`ModelAssetRequestProjection.ProjectAcquire`固定loadContext.RequestDigest；本桥实现这个读取意图的公开低层编排，不再向共享Service请求第二份Acquire lease。所有Authority/Hold/OpenContent/Materialize子步骤沿该原loadContext，callId是本MA root原节点的唯一子ordinal，不临时发明各端口业务摘要。`Authority.AuthorizeAsync(AccessInput)`→仅Active Permit且原subject/Scope/purpose/RootRef/期限/fence匹配；先`Subscribe`并核Active，回调只冻结阻止新借用/请求合作排空。Watch SnapshotRequired/Unknown/到期禁止新native使用，不改旧资格事实，不Dispose共享Authority。`DenyNewAndDrain`不提前释放native输入；严格即时撤回策略缺真实原子guard时MA-CAP，默认桥只按上游C.8声明当前重核+合作排空能力。
3. `Store.AcquireHoldAsync(StoreHoldRequest)`固定完整Runtime closure/View取得Held；全graph精确保持而非仅原模型文件。`Store.OpenContentAsync(StoreContentRequest)`每次带原Hold及原ClosureFile，取得已完成校验的ContentReadLease；按MaxResidentBytes/文件长度先reserve bytes，完整读至EOF再核长度/hash，最多探查额外1 byte且计预算。OCR.Blobs只投影其请求Files，底层全部依赖仍由Hold保护，不能为省资源删ValidationEvidence/RebuildSource声明或把GraphRefs拍平。
4. `Store.MaterializeAsync(MaterializeRequest(Context,Hold,Closure,原Format))`：只在Store.DescribeCapabilities()返回的StoreCapabilitySnapshot精确支持SafeMaterialization、ExactSnapshot/ReadHold且本部署已选择C.2安全adapter时调用；它在绑定Store内部使用`WindowsModelAssetMaterializer.Create(profile,rootSlot)`，OCR不另建临时目录、不重做安全guard/缓存。Value为IFormatMaterializationLease、VerifiedFiles完整实际hash/length/OwnerRef与Layout符合才保留。EntrypointPath只留本H程序集internal租约附加数据，worker读取该路径；没有物化且不能证明安全时ASSET-001，不落未经授权File.WriteAllBytes备用。MLP/OCV首版同一路物化，不增加另一文件安全实现。
5. 返回internal `OcrNativeModelLease : IModelLease`，公开Snapshot/Blobs仍§8，内部强持Permit/Watch/Hold/Materialization及全部原Task。§8.1H worker只接这一H租约来源；普通协议IModelLease只用于协议factory，送H时ADAPTER-001且不调用native。worker在读取与apply之前各以`ValidatePermitAsync`有限原Context重核（验证ordinal身份由原节点冻结），并核Watch未失效；native开始后撤权只请求合作停止后续ROI，不强杀。每模型一fresh read，无native模型缓存；C.2缓存仅上游可选只读bytes，命中仍取得当次许可/hold/物化，不复用“获准”状态。
6. Dispose租约只在native退出后：本方read流/原读取Task→Materialization.ReleaseAsync→Store.ReleaseAsync(Hold.ResourceId)→Watch.Dispose→Authority.ReleasePermitAsync；逐资源登记稳定ReleaseOperationId与原Task，None独立cleanup预算。每Release返回ResourceState.Released才退账，NotFound/Pending/Unknown不当Released；流仍读时不Dispose其父hold。已faulted幂等释放只沿§4.4有限Recover，MA根`ObserveCleanupAsync`观察原slot；不会Drain/Dispose共享Service/Store/Authority。两个根在真实Released/Returned前留入口强持，`OcrBorrowedHostSources.lifetimeLease`只归还本次宿主真实借用，不代关MA共享运行时。

Context.OperationId固定`ocr-assets/<桥epoch>/<接纳ordinal>/resolve`或`/load`，RequestEpoch=0，Scope/Profile/Budget取原profile；每新请求总deadline在首次Acquire登记时冻结，所有子等待取min(原剩余、WaitTimeout)，不因Resolve结束重新开全预算。原root存完整Context/请求与子call表；Query沿原OperationId/digest，Release沿原ResourceId/ReleaseOperationId，观察预算变化不改变身份。Stage/Import/Export不在生产resolver：训练/导入Host调用MA的ImportAndSeal时提供**全部三Purpose显式依赖及原SourceSnapshot**，不能由未传字段、UI、当前方法hash补猜SourceSnapshot。上游C.1 `model-sd-stage-jcs-v1`含父OperationId/RequestDigest/Scope/Store的Stage身份由MA桥负责，OCR只保存原完整回执/版本；旧Unknown按旧rule/identity查询，不以新Stage身份重发。新C.1登记/三Purpose保护对新封存生效，旧资产保留旧metadata/规则与读回路径。

**格式/设备/挑战的准确分权。** Deep选择上游C.5 DeepOcr reader，Serialized字段保序`recognition_alphabet/_internal/_mapping/_image_dimensions`按其Sequence schema；Runtime只`recognition_batch_size/deviceRef`，显式`ModelAssetDeviceDescriptor`经上游`ResolveDescriptor`及query_available_dl_devices/get_dl_device_param/get_system核唯一设备，DeviceId不是裸GPU序号。本OCR worker按同descriptor执行，不set旧`runtime`字符串或绕道另建ONNX。传统MLP与OCV不伪标MA DeepOcr family：其producer Format保持本OCR登记format/serialized schema，MA generic Store/物化可以消费，而C.5未提供这两种reader时不调用该格式adapter冒Supported；实际H read/get_params/close的验证由本节承担。

新封存MLP格式Family/Id均`ocr-halcon-mlp`、Revision=`1`、Entrypoint=`model.omc`；OCV均`ocr-halcon-ocv`、Revision=`1`、Entrypoint=`reference.ocv`。Layout每项SourceAsset取实际OwnerRef、Role取同原ClosureFile.Role、SourcePath取原LogicalPath，TargetPath分别模型入口/charset.json/preprocess.json/runtime-profile.json（OCV无charset）；内容bytes/hash不因重命名而变。Deep沿原生产者已冻结C.5 FormatId/Revision/Layout，不强改其资产修订。两种传统格式的Serialized/SemanticSnapshot仍由原生产者按封存时真实元数据提供，桥保原schema/字段/摘要；本版**不注册MA IModelFormatAdapter**或新MA schema，故MA技术readback必须Unsupported，不能填空schema假Supported。OCR-H自己的MLP get_params字表/拒识能力核对及OCV实际read/计算/close的证据沿OCR EvidenceTrace与挑战观察输出，不冒MA格式报告。旧格式/入口按原修订explicit binding读取，不批量重写旧资产；新Format/Layout只用于新封存与新binding。是否生产可用仍由原模型用途资格Owner决定。

需要正式技术读回时Host用MA `VerifyFormatAsync(ReadbackRequest)`、`ProjectReadback`绑定原AdapterKey修订/RuntimeSnapshot/ChallengeRef；该报告只证技术读回。挑战executor在同H的Assets目录，唯一公开形状如下；case目录由原数据/真值Owner准备并冻结后注入，构造不读Store或任意文件。MA.ModelAssetChallengeInput.ChallengeRef必非null；null在MA adapter分支直接NotRequested，不调用executor。

```csharp
public sealed record OcrAssetChallengeCase(string CaseId,
    OcrRequest? Ocr, OcvRequest? Ocv,
    OcrResponse? ExpectedOcr, OcvResponse? ExpectedOcv,
    double MaxCornerErrorPx, double MaxScoreError);
public sealed record OcrAssetChallengePlan(MA.AssetRef ChallengeRef,
    MA.AssetRef RootRef, IReadOnlyList<MA.AssetRef> GraphRefs,
    MA.FormatDescriptor Format, MA.SemanticSnapshot RuntimeSnapshot,
    string MethodId, string MethodRevision,
    IReadOnlyList<OcrAssetChallengeCase> Cases);
public sealed record OcrAssetChallengeProfile(string Id, string Revision,
    int MaxCalls, int MaxCases, long MaxCatalogBytes, int MaxErrors,
    TimeSpan WaitBudget, TimeSpan CleanupBudget);
public sealed class OcrModelAssetChallengeExecutor : MAS.IModelAssetChallengeExecutor
{
    public OcrModelAssetChallengeExecutor(OcrAssetChallengeProfile profile,
        IReadOnlyList<OcrAssetChallengePlan> catalog, IOcrEngine engine,
        OcrProcessOwner owner, OwnerTicket ticket,
        MAS.ModelAssetsHostSlot rootSlot, TimeProvider clock);
    public ValueTask<MAS.PortResult<MAS.ModelAssetChallengeReport>> ExecuteAsync(
        MAS.ModelAssetChallengeInput request, CancellationToken token);
}
```

所有上限正、时间有限、容差有限非负；catalog/plan/case深冻结、CaseId唯一且ordinal排序、ChallengeRef唯一，canonical内容与expected完整bytes先受MaxCatalogBytes/原根预算限制。每case恰一个请求及同类expected；用OcrContract验证、请求/方法/Frame/ROI/模型身份与expected绑定完整，Plan的Root/Graph/Format/Runtime与原映射一致。expected为真值Owner已批准观察及容差，不把一次待验native输出自动命名真值；OCV只比较Computed/Quality/参考身份，不判工艺PASS。ExpectedResponse的证据是原冻结真值证据，比较不要求其聚合EvidenceRef等于新运行证据。

构造核owner.Query(ticket).Snapshot非空且EngineEpoch非空，保存该原epoch；engine必须是该Host已在ticket绑定的同一实例（可信装配输入），每Submit回执epoch再核完全一致，不读取不存在的engine.EngineEpoch属性；clock取该Host原实例，原MA slot.Scope匹配用途Scope；Host在MA原slot的首call前已SetCleanupPlan并KeepAnchor executor/catalog（完整bytes计费）。每Execute通过该slot.StartCall一次登记内部ExecuteCore原Task及保守资源，再以ValueTask包同Task交MA调用者；OCR operation的任务登记由engine已批准Owner负责，不调用不存在的公开Owner.RegisterTask。MaxCalls含结束记录，call/task/catalog预算在调用前预约。先exact核Context.Scope等于原rootSlot.Scope、Context.ProfileId/ProfileRevision非空且保原父读回Profile（不当挑战Profile）、RootRef/GraphRefs（按完整identity/digest规范排序）、Format/Layout、RuntimeSnapshot与catalog，Materialization.VerifiedFiles/入口仍属于同原闭包；缺case/资格/预算返回Unknown/MA-CAP，无Submit。固定一次executorEpoch/call ordinal/case ordinal，生成`ocr-challenge/<epoch>/<call>/<case>`的OperationId和IdempotencyKey，替换模板身份而保持内容hash；同原Task不生成新身份重跑。IOcrEngine.Submit→按原ID有限Wait/Query；token只合作RequestCancel已接纳的本次cases，未尝试/拒绝/失败/取消/超时均保在完整分母。一个case退出资源Released后才开始下一个；外层Context总deadline不重开，以min(剩余,WaitBudget)等待，所有native完成与清理前Execute不成功完成。超过观察截止但原任务未排空时executor原Task保持Pending，MA/root有限观察Unknown并保原节点；不返回临时lease作Evidence。engine本身与Frame/MA source都由原宿主拥有，executor不Dispose它们。

fresh read通过生产engine既有resolver取得**新的**许可/hold/物化与worker；该resolver不调用VerifyFormatAsync，因此不会递归挑战。原MA输入Materialization仅借用且保留到Execute实际退出；新的物化租约由新operation归还，不能用一次归还替代两份Owner。全部再读/执行/退出成本计原Context及两个root实际资源，不共享native handle。

比较按CaseId、RoiId、WordId、PositionIndex/rank一一对应：数量、模式、Outcome、RawText（含Blank/拒识）、候选symbol/flag/ScoreKind/Meaning、LineOrdinal/ReadingOrder、SupportComplete/RelatedWordIds、映射和OCV参考/阈值模式都exact；每对应Frame角的欧氏距离≤MaxCornerErrorPx，每有限score/OCV Quality绝对差≤MaxScoreError，null必须同为null；非有限、缺项、额外项、错误/未完成case均不能Passed。禁止按期待重新匹配词或选最高分。期望与实际摘要分别hash `ocr-model-challenge-observation/1` canonical对象：ContractVersion、MethodId、MethodRevision、Cases（按CaseId，每项CaseId、Ocr的Mode/Items或Ocv的Observation，沿§3.2字段顺序但排除EvidenceRef、OperationId、聚合Evidence；未运行项显式null并记录运行Outcome）；各数值/string/null沿§3.4规则。MA.Digest.RuleId=`ocr-model-challenge-observation-v1`、Algorithm=`sha256`。摘要记录证据，判定用上述逐字段/容差比较；Passed仅所有case完成且Released并满足全部断言，已知不符Failed，缺证据Unknown。ReportReceiptRef=null直至原报告Owner耐久保存；MA PortResult成功只返回完整报告，失败报告放Evidence，PendingResources/ReconciliationRefs沿上游真实原资源/原Context填写，不伪造空资源证明。

可选C.4签名仅由工程包入口Host调用`ModelAssetPackageSignature.Verify`，使用C.7完整profile（信任快照/SpkiSha256/时间/预算/原Scope、Root、Purpose、PackageDigest）；RequireSignature=true只接受Verified，Unknown/缺签拒进入本次用途，结果与用途资格两笔证据。detached envelope不进OCR ModelSnapshot/既有MA bundle schema，不产生生产采用权限。C.8实际AU桥由上游负责，OCR提供当前成像/字库/用途Owner的可信用途证据；Candidates/Replay/Shadow不伪装生产Approved。本resolver不导入密钥/私钥、不重建签名算法或登录。

## 9. 两个从空进程构造的无 UI Host

### 9.1 公共协议模拟来源、工厂与时钟（C2）

这些为可发布的C2托管协议模拟能力，仍放唯一Core工程、namespace=`Asun.Modules.Ocr.Simulation`，测试consumer是Core.Tests中的两个无UI入口；**不调用HALCON、不分类、不伪造原读/词框/质量概率**，不得放生产注册表。H工厂仍§8.1唯一真实类型。以下是待实现的完整公开合同，非已编译声明。

```csharp
public enum ProtocolPoint { FrameAcquire, AssetAcquire, WorkerCreate, Compute,
    WorkerRelease, AssetRelease, FrameRelease, SourceRelease }
public enum ProtocolEffect { Immediate, Hold, FailOnce, Fail }
public sealed record ProtocolStep(string CallId, ProtocolPoint Point,
    ProtocolEffect Effect, bool IgnoreCancellation);
public sealed record ProtocolFrame(OcrImageRef Image, ReadOnlyMemory<byte> Pixels);
public sealed record ProtocolAsset(ModelSnapshot Snapshot, IReadOnlyList<AssetBlob> Blobs);
public sealed record ProtocolSourceLimits(int MaxFrames, int MaxAssets, long MaxBytes);
public sealed record ProtocolCounts(int FrameAcquires, int AssetAcquires,
    int WorkersCreated, int ComputeCalls, int WorkerReleases,
    int AssetReleases, int FrameReleases, int SourceReleases, int ActiveBorrows);
```

准确公开类/构造/成员：

- `OcrProtocolControl(IReadOnlyList<ProtocolStep> steps)`：深复制、CallId+Point唯一；`bool Release(string callId, ProtocolPoint point)`只打开已建Hold闩锁，未知false；`ProtocolCounts Snapshot()`只读计数。Hold使用TaskCompletionSource/RunContinuationsAsynchronously，不能阻塞shell/UI；FailOnce仅同CallId/Point首次抛InvalidOperationException/Ocr.ProtocolFault，后续显式释放恢复成功，Fail每次相同错误。IgnoreCancellation=true模拟不能抢占的**协议任务**，不声称真实native行为；默认无step为Immediate。
- `OcrProtocolClock(DateTimeOffset initialUtc) : TimeProvider`：`public void Advance(TimeSpan elapsed)`；override `public DateTimeOffset GetUtcNow()`、`public long GetTimestamp()`、`public long TimestampFrequency { get; }`、`public ITimer CreateTimer(TimerCallback callback, object? state, TimeSpan dueTime, TimeSpan period)`，返回100ns timestamp/frequency=10000000、elapsed非负有限且checked不溢出、不回退。timer实现BCL ITimer.Change/Dispose/DisposeAsync；dueTime/period只有非负或Timeout.InfiniteTimeSpan，period=0/Infinite一次性，dueTime=Infinite禁用，disposed Change=false，非法ArgumentOutOfRangeException；Advance依due timestamp和注册序号唤醒一次/周期回调，callback在锁外、异常保留到测试入口，不假造时间跃迁完成原Task。fixed UTC、无系统时间/窗口依赖；10秒单例/120秒harness墙钟兜底见§12。
- `OcrProtocolSource(IReadOnlyList<ProtocolFrame> frames, IReadOnlyList<ProtocolAsset> assets, ProtocolSourceLimits limits, OcrProtocolControl control) : IOcrHostSources`，同时实现IFrameLeaseProvider/IModelAssetResolver；`Frames/Assets`返回自己、RetainedBytes等于深复制后的frame/blob实际字节（按唯一字节载体，列表重复身份拒绝）。构造纯托管、容量/hash/长/唯一性先核，不acquire；失败无后台Task。两port按完整Image/Snapshot匹配，绝不按ID找latest。Frame acquire CallId=BufferLeaseId，Asset acquire CallId=ManifestSha256；各lease释放同CallId对应Point；sources释放CallId=`sources`。成功返回独立lease，ActiveBorrows++；release确认才--，source有ActiveBorrows则Dispose抛错，root按资源Unknown处置而非清buffer。所有Dispose幂等且release成功后不再计数/释放第二次。
- `OcrProtocolAdapterFactory(string factoryId, AdapterCapabilities capabilities, OcrProtocolControl control) : IOcrAdapterFactory`：校验/深复制、AdapterId必须`ProtocolOnly/<factoryId>`、RuntimeVersion=`ProtocolOnly`、NativeCancellationSupported=false；OcvSupported可true；构造无Task或lease。worker Create CallId=`<factoryId>/worker/<从1开始ordinal>`，ordinal只在真正Create调用时增加；Compute/WorkerRelease同CallId。返回internal protocol worker，root/engine唯一拥有，取消后迟到worker仍接管，不对同operation再Create。

协议Read按每请求ROI返回一个 `OcrItemResult(RoiId,Empty,Words空,SingleWord,RejectReason=null,EvidenceRef)`，**没有RawText或人工winner**；Detection也只Empty，Verify返回NotComputed/Quality=null/RejectReason=OCR-OCV-001且完整参考身份。Read以§3.4 canonical、原frame字节、EvidenceTrace（无派生图、ActualParameters仅Execution=ProtocolOnly、model/preprocess/request身份齐全）和空观察构造§3.2证据，含request.json/frame.raw/trace.json/observation.json；所有blob长度/hash可核，不传假的native score。它只是确认1ROI→1item、empty与not-run不同、真实资源持有/协议回执；不测算法正确率。native借用模拟为Compute未结束时对Frame.Pixels/Assets/worker强持，ActiveBorrows未释放，不在Wait到期放开。

### 9.2 完整固定输入（两Host共用的协议fixture）

下列函数只生成BCL字节/值对象，所有字段都有来源；`Snapshot.ManifestSha256`是本协议fixture的资产描述身份，fake字节不是模型，QualificationRef=`protocol-test-only`不代表客户资格。fixture完整声明在本节，不能靠未定义factory/To* extension或真实模型才能构造C2 Host。生成字段按英文API名，不使用产品事实；这些数值仅用于合同测试，非性能Profile。

```csharp
// namespace Asun.Modules.Ocr.Simulation；另外using System.Security.Cryptography/System.Text
public static (ProtocolFrame Frame, ProtocolAsset Asset, OcrMethodProfile Method)
    MakeProtocolFixture(string frameId)
{
    static string Hash(byte[] bytes) => Convert.ToHexStringLower(SHA256.HashData(bytes));
    byte[] pixels = new byte[64]; // 合法8x8 Gray8；协议不识读
    var image = new OcrImageRef(frameId, frameId + "/buffer", PixelFormat.Gray8,
        8, 8, 8, "frame-pixels", Hash(pixels));
    string[] roles = { "deep-ocr-model", "charset", "preprocess", "runtime-profile" };
    string[] texts = { "protocol-only/no-model", "protocol-only/Blank=U+2800;A",
        "protocol-only/no-preprocess", "protocol-only/no-runtime" };
    var files = new List<AssetRef>();
    var blobs = new List<AssetBlob>();
    for (int i = 0; i < roles.Length; ++i)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(texts[i]);
        var file = new AssetRef(roles[i], "protocol/" + roles[i], Hash(bytes), bytes.Length);
        files.Add(file);
        blobs.Add(new AssetBlob(file, bytes));
    }
    // 描述本协议字节闭包，不冒充HALCON模型Manifest
    byte[] manifest = Encoding.UTF8.GetBytes(string.Join("\n", files.Select(f =>
        f.Role + ":" + f.AssetId + ":" + f.Sha256 + ":" + f.ByteLength.ToString(System.Globalization.CultureInfo.InvariantCulture))));
    var model = new ModelSnapshot("protocol-model", Hash(manifest), "protocol-test-only",
        files, new[] { "\u2800", "A" }, "\u2800", null, Array.Empty<string>());
    var preprocess = new PreprocessProfile("protocol-preprocess", files[2].Sha256,
        null, null, false, 0, "1");
    var budget = new OperationBudget(1000, 4096, 2, 4, 16, 1, 4,
        1048576, 524288, 131072);
    var method = new OcrMethodProfile("protocol-profile", "1", OcrMode.Recognition,
        OcrBackend.HalconDeepOcr, model, preprocess,
        new DeepOcrProfile(32, 32, false, 0, false, "ProtocolOnly", "none"),
        null, "protocol/no-fallback", ReadingDirection.LeftToRight,
        new[] { "A" }, null, budget);
    return (new ProtocolFrame(image, pixels), new ProtocolAsset(model, blobs), method);
}
public static OcrRoi ProtocolRoi(string roiId) => new(roiId, 1, 1, 6, 6, 0,
    "frame-pixels", new[] { new PixelPoint(1,1), new PixelPoint(7,1),
        new PixelPoint(7,7), new PixelPoint(1,7) });
public static AdapterCapabilities ProtocolCapabilities(string factoryId) => new(
    "ProtocolOnly/" + factoryId, "0.3", "ProtocolOnly",
    new[] { OcrBackend.HalconDeepOcr },
    new[] { OcrMode.Detection, OcrMode.Recognition, OcrMode.Auto },
    true, true, false, 4096, 2, 4, 16, 1, 4, 1,
    1048576, 524288, 131072, false, "Unavailable", null, null, true);
```

fixture函数放Core.Tests，ProtocolRoi/Capabilities亦测试入口静态函数（补using System.Linq）。公开Simulation类型见§9.1及§9.7的ProtocolEmptyJudge，fixtures不是产品API。ProtocolSource按该已声明fixture规则消费占位文件，不按HALCON反序列化；真实H resolver不得拿protocol-test-only资产加载。输入型别/请求hash仍§3唯一原合同不变。

### 9.3 Host A：丝印协议服务与消费异常的有限收尾

进程main先创建 `OcrProcessOwner(new ProcessOwnerLimits(4,512,33554432,32), clock)`，clock=`new OcrProtocolClock(new DateTimeOffset(2026,10,11,0,0,0,TimeSpan.Zero))`。该根变量保留到所有slot Released（若测试故意挂起，保留至fixture开启闩锁/有限Recover结束）；它不是以下函数的局部资源。下面返回的ticket供入口原槽查询，callback为同步Action，不引入未被Owner登记的异步消费Task。

```csharp
public static async ValueTask<(OwnerTicket Ticket, WaitReceipt? Wait,
    OwnerHandoffReceipt Handoff)> RunSilkscreenProtocolAsync(
    OcrProcessOwner process, OcrProtocolClock clock, Action<OcrResponse> consume)
{
    OwnerTicket ticket = process.Reserve("silkscreen-host", new OwnerSlotLimits(
        4, 96, 4194304, 2097152, 1048576, 2)); // 成功后才创建source/factory
    OcrEngine? engine = null;
    WaitReceipt? observed = null;
    string stage = "Construction";
    try
    {
        var fixture = MakeProtocolFixture("silkscreen-frame");
        var control = new OcrProtocolControl(Array.Empty<ProtocolStep>());
        var source = new OcrProtocolSource(new[] { fixture.Frame }, new[] { fixture.Asset },
            new ProtocolSourceLimits(1, 1, 1048576), control);
        OwnerHandoffReceipt attached = process.AttachSources(ticket, source);
        if (attached.Kind != HandoffKind.Retained)
            throw new InvalidOperationException("Ocr.SourceNotAttached");
        IOcrAdapterFactory factory = new OcrProtocolAdapterFactory(
            "silkscreen", ProtocolCapabilities("silkscreen"), control);
        engine = new OcrEngine(process, ticket, source.Frames, source.Assets, factory,
            new OcrRuntimeOptions(4,1,4,4194304,2097152,64), clock, null);
        var request = new OcrRequest("silkscreen-op-1", "silkscreen/attempt/1",
            fixture.Frame.Image, new[] { ProtocolRoi("silkscreen-roi") }, fixture.Method);
        stage = "Observation";
        AdmissionReceipt admission = engine.Submit(request);
        if (admission.Kind == AdmissionKind.Rejected)
            throw new InvalidOperationException(admission.Errors[0].Code);
        observed = await engine.WaitAsync(admission.Snapshot!.OperationId,
            TimeSpan.FromMilliseconds(50), CancellationToken.None);
        if (observed.Kind == WaitKind.Terminal &&
            observed.Current.Snapshot!.State == OperationState.Completed &&
            observed.Current.Snapshot.Ocr is { } result)
        {
            stage = "Consumption";
            consume(result); // 允许抛异常，原观测不变
        }
        HostOutcome outcome = observed.Kind != WaitKind.Terminal ? HostOutcome.TimedOut :
            observed.Current.Snapshot!.State switch
            {
                OperationState.Completed => HostOutcome.Completed,
                OperationState.Cancelled => HostOutcome.Cancelled,
                OperationState.TimedOut => HostOutcome.TimedOut,
                _ => HostOutcome.Failed
            };
        process.RecordHostOutcome(ticket, outcome);
    }
    catch (Exception ex)
    {
        process.RecordConsumerFailure(ticket,
            new HostFailure(ex is OperationCanceledException ? "HostCancelled" :
                stage == "Construction" ? "HostConstructionFailed" : "HostConsumerFailed",
                stage, ex.GetType().Name));
        process.RecordHostOutcome(ticket, ex is OperationCanceledException
            ? HostOutcome.Cancelled : HostOutcome.Failed);
    }
    finally
    {
        // 与业务token无关；即使观察到期/消费抛错也同一原Task有限清理
        try
        {
            await process.CleanupAsync(ticket, TimeSpan.FromMilliseconds(50), CancellationToken.None);
        }
        catch (Exception cleanupError)
        {
            process.RecordCleanupFailure(ticket,
                new HostFailure("HostCleanupFailed", "Operations", cleanupError.GetType().Name));
        }
    }
    OwnerHandoffReceipt handoff = process.ConfirmRetention(ticket);
    if (handoff.Kind == HandoffKind.Rejected)
        throw new InvalidOperationException("Ocr.OwnerRetentionNotConfirmed");
    return (ticket, observed, handoff);
}
```

正常消费只看Empty和trace=ProtocolOnly，不能按Empty判产品PASS。示例用stage区分Construction/Observation/Consumption，不把构造错误当OCR识读失败。Wait budget是clock的有限观察，main/fixture用Advance推进；没及时推进由§12墙钟防挂非零，不计native释放通过。Cleanup调用异常按片段独立捕获，保留主错误/恢复错误，不裸finally覆盖。Rejected attach source的本地所有权不能丢，精确出口见§9.5，不用未知原Task假dispose成功。

### 9.4 Host B：标签服务，迟到factory/native借用与原epoch恢复

完整输入/来源和limits同§9.2，本入口不同HostId/slot。关键路径为**协议WorkerCreate在取消后迟到**；control必须由source/factory/root持有，进程入口可Release；它不是真实SDK/HALCON验收。

1. `ticket=process.Reserve("label-host", new OwnerSlotLimits(4,96,4194304,2097152,1048576,2))`；root仍进程main的公开构造。
2. `fixture=MakeProtocolFixture("label-frame")`；`control=new OcrProtocolControl(new[]{new ProtocolStep("label/worker/1",ProtocolPoint.WorkerCreate,ProtocolEffect.Hold,true)})`；`source=new OcrProtocolSource(new[]{fixture.Frame},new[]{fixture.Asset},new ProtocolSourceLimits(1,1,1048576),control)`；AttachSources必须Retained。`factory=new OcrProtocolAdapterFactory("label",ProtocolCapabilities("label"),control)`。
3. 完整engine构造 `new OcrEngine(process,ticket,source.Frames,source.Assets,factory,new OcrRuntimeOptions(4,1,4,4194304,2097152,64),clock,null)`；完整request=`new OcrRequest("label-op-1","label/attempt/1",fixture.Frame.Image,new[]{ProtocolRoi("label-roi")},fixture.Method)`。Submit receipt原OperationId/EngineEpoch立即保留，拒绝不启动第二事实。
4. fixture等待control.Snapshot().WorkersCreated表明Create节点开始（计数在进入gate前增加），**有10秒墙钟上限**；`clock.Advance(TimeSpan.FromMilliseconds(1001))`使请求deadline到。`engine.WaitAsync(originalId,TimeSpan.Zero)`必BudgetElapsed/Found、非终态、StopReason.Deadline；主流程 outcome TimedOut。`process.CleanupAsync(ticket,TimeSpan.FromMilliseconds(25),CancellationToken.None)`由main再Advance25ms观察，Pending/BudgetElapsed也必须ConfirmRetention返回Retained再离栈。
5. 进程入口按 `(ticket.ProcessEpoch,ticket.SlotId,originalEngineEpoch,originalId)` 调用 `process.QueryOperation`，不能新engine重提。原Create Task/Frame/asset/source借用仍root强持，ComputeCalls=0；`control.Release("label/worker/1",ProtocolPoint.WorkerCreate)`后原Task晚到worker先登记再Dispose，绝不Read或重新Create。`process.RecoverAsync(ticket,TimeSpan.FromMilliseconds(50),CancellationToken.None)`观察同一清理，必要时clock.Advance50ms；Released后原operation TimedOut且资源无借用。测试控制poll/advance总墙钟上限10秒，未确认非零/资源Pending保留，不能无界wait。
6. 用仅替换ProtocolStep为 `( "label/worker/1", Compute, Hold, true )` 重放同场景，测试worker Read已开始、ActiveBorrows>0、原Frame/asset强持直到Release；资源账不因Wait超时归零。每variant新slot/HostId及新operation/key，原槽不覆盖。

Host B的准确同步装配函数在同一测试入口（调用Reserve之前不建source/factory）：

```csharp
public static (OwnerTicket Ticket, OcrProtocolControl Control, OcrEngine Engine,
    OcrRequest Request) BuildLabelProtocolHost(OcrProcessOwner process, OcrProtocolClock clock)
{
    OwnerTicket ticket = process.Reserve("label-host", new OwnerSlotLimits(
        4,96,4194304,2097152,1048576,2));
    try
    {
        var fixture = MakeProtocolFixture("label-frame");
        var control = new OcrProtocolControl(new[] { new ProtocolStep(
            "label/worker/1", ProtocolPoint.WorkerCreate, ProtocolEffect.Hold, true) });
        var source = new OcrProtocolSource(new[] { fixture.Frame }, new[] { fixture.Asset },
            new ProtocolSourceLimits(1,1,1048576), control);
        if (process.AttachSources(ticket,source).Kind != HandoffKind.Retained)
            throw new InvalidOperationException("Ocr.SourceNotAttached");
        IOcrAdapterFactory factory = new OcrProtocolAdapterFactory(
            "label", ProtocolCapabilities("label"), control);
        var engine = new OcrEngine(process,ticket,source.Frames,source.Assets,factory,
            new OcrRuntimeOptions(4,1,4,4194304,2097152,64),clock,null);
        var request = new OcrRequest("label-op-1","label/attempt/1",fixture.Frame.Image,
            new[] { ProtocolRoi("label-roi") },fixture.Method);
        if (process.ConfirmRetention(ticket).Kind != HandoffKind.Retained)
            throw new InvalidOperationException("Ocr.OwnerRetentionNotConfirmed");
        return (ticket,control,engine,request);
    }
    catch (Exception ex)
    {
        process.RecordConsumerFailure(ticket,
            new HostFailure("HostConstructionFailed","Construction",ex.GetType().Name));
        // 用0预算开始独立cleanup；ValueTask只转原Task一次，root已持有内部清理
        try
        {
            process.CleanupAsync(ticket,TimeSpan.Zero,CancellationToken.None).GetAwaiter().GetResult();
        }
        catch (Exception cleanupError)
        {
            process.RecordCleanupFailure(ticket,
                new HostFailure("HostCleanupFailed","Operations",cleanupError.GetType().Name));
        }
        if (process.ConfirmRetention(ticket).Kind == HandoffKind.Rejected)
            throw new InvalidOperationException("Ocr.OwnerRetentionNotConfirmed",ex);
        throw; // 原异常重新抛，root/ticket可由process.Query和入口登记定位
    }
}
```

0-budget CleanupAsync必须同步产生当前receipt、创建cleanup任务后不阻塞端口，GetResult仅用于这一个公开保证完成的ValueTask，不能用于任意native/Dispose Task。实际async观察/异常收尾继续§9.5；root在reserve时已登记HostId，构造失败即使caller尚未收到ticket，也可用下文公开 `FindHost(hostId)` 找原槽，不能再Reserve同HostId掩盖。协议Main必须finally捕获cleanup异常，不让示例catch里的清理错误覆盖原construction错误（片段已经独立catch并记清理轴，不覆盖原ex）。

Host B仍§9.5同一异常/独立有限finally/确认接管出口；模型/read阶段异常可由FailOnce/Fail脚本给出，Stage不使用真实HALCON错误。取消分支以RequestCancel代替推进deadline，只有释放确认后Cancelled。Query错epoch/slot返回Unknown，必须保留原身份，Unknown不创建第二operation。

### 9.5 两Host唯一异常与收尾模板

上面装配consumer都必须实现此控制流（不是可选教程）：reserve失败无槽/副作用，返回容量错误；成功reserve后 `stage=Construction`，本地source尚未Attach时由局部强持、构造纯托管只读，不调用port；Attach失败先在当前stack强持并进行独立有限本地Dispose观察，若未确认用原source创建Owner保留分支、不能在没有槽的finally丢对象。为消除此不闭合分支，公开Owner增加 `AttachSources` 的失败语义：对**有效本次ticket、尚未绑source、且source由本模块协议构造符合预算**不允许部分拒收，必须原子Retained；超预算/null/身份错误在开始Attach前Validate并仍未启动IO，协议源可直接释放纯托管引用。真实已带副作用源始终由其原Owner持有，AttachRejected只沿原Owner回执查询，本模块不抢管。若root无法分配metadata根槽，先Reserve必须失败，不等先建factory再挤槽。

engine绑定/Submit后stage=Observation；进入callback前stage=Consumption。业务取消捕获OperationCanceledException记录HostCancelled并请求原operation取消；其它异常记录首次HostFailure、停止新提交，原operation snapshot不改。**finally单独try/catch**：CleanupAsync独立预算+None，抛异常时调用 `process.RecordCleanupFailure(ticket,new HostFailure("HostCleanupFailed","Operations",cause))`（公开成员见下补充），保留主错误不throw覆盖；然后ConfirmRetention。消费异常可以作为返回OwnerSlotSnapshot.PrimaryFailure或保存后重新抛**原异常**（ExceptionDispatchInfo），但前提handoff Retained/Released；Unknown/Rejected不证明释放。未绑定engine的槽Cleanup跳过operation/engine、清sources；所有对象对归属已经有明确Owner，不需要客户事实。

`IOcrProcessOwner.RecordCleanupFailure`已在§4.4公开，只记录脱敏错误/Unknown资源轴，不释放、不替代PrimaryFailure。调用Query(ticket)拿原主错/清理错；任何finally异常都是清理轴，不能自称Owner接收失败就throw后丢root。非法ticket由进程入口的原根仍保留，必须返回明确NotRetained错误并继续持有入口引用，禁止成功结束进程/fixture；进程退出策略是实际部署门，不作为本软件漏引用的理由。

§9.3已按stage、取消错误类型、finally隔离和同一handoff表达完整控制流；片段的public函数是Core.Tests测试Host形状，不属于C1/C3纯值API。两个Host仍走同一公开服务/来源/工厂/limits/clock，不隐藏初始化、不读JSON配置环境变量/真实设备。

### 9.6 H 与 W 在原映射内的装配

公开借用source封装为 `public sealed class OcrBorrowedHostSources : IOcrHostSources`（Core），构造 `public OcrBorrowedHostSources(IFrameLeaseProvider frames, IModelAssetResolver assets, IAsyncDisposable lifetimeLease, long retainedBytes)`。必须非null且retainedBytes≥0，构造只强持不调IO；lifetimeLease是实际provider/asset Owner交付的独立借用租约，保证这两个端口和既有Frame/资产在租约成功Dispose前可用，不能拿一个空Dispose对象替代真实保证。Frames/Assets原样只读，source.Dispose只在模块lease全退出后Dispose这一借用租约，不销毁共享provider/resolver；其原Task由根记录，异常/迟到按资源Unknown。借用租约在构造/Attach前始终有上游原Owner强持，AttachRejected不许擅销原端口；实际lease获取及输入版本绑定是H/I的精确外部交接门，wrapper软件API本身已明确。

H工厂构造/worker回滚沿§8.1已确认文本；仅根槽挂接补为：进程Reserve→AttachSources（由H宿主实现IOcrHostSources，承接外部Frame/asset原Owner、RetainedBytes有界）→`IOcrAdapterFactory factory=new Asun.Modules.Ocr.HalconAdapter.AsunImageHalconAdapter(adapterOptions)`→`new OcrEngine(process,ticket,sources.Frames,sources.Assets,factory,runtimeOptions,timeProvider,events)`。H公开factory签名与HALCON路线未改；它无自己的隐式进程根。source中的外部借用必须有provider/resolver原Owner确认在root移交期间存活，sources.Dispose只释放本次宿主拥有的引用，不销毁他人共享SDK/source；真实端口绑定在I/H工程，不用协议Fake冒真。

W仍§10唯一`OcrEvidenceControl`公开输入/事件，在Wpf.TestHost `net10.0-windows/UseWPF` STA App入口创建根Owner（runtime层）与Window；窗口放真实OcrEvidenceControl，不以TextBlock替换影像控件，ImageContent消费宿主公开viewport或默认PNG预览（只能显示证据）。View由root QueryOperation的原snapshot和宿主保存投影经Dispatcher更新，generation/epoch检查、语言/主题/权限注入同§10；Closing只撤订阅，发独立有限Cleanup到原Owner，ConfirmRetention后允许窗口离栈，根留在App进程入口直至Released。H/W真实图像/控件资格仍单独门，不重做已确认Unknown保存边界。

### 9.7 推荐执行 Host 的公开操作（OCR-C2-R，不属于已接收纯值C3）

C3的Propose/Evaluate原合同及接收保持。本节将§3.5已有有限离线编排定位为 **C2-R**，同Core/Core.Tests，namespace `Asun.Modules.Ocr`；真实样本判断及资产来源接I。本版不增加参数自动搜索/训练/原生OCR路线，候选都是宿主明确提供的有限集合。先Detection操作→终态后调用纯值Propose取得提案→工程师/宿主冻结对应Recognition候选与样本请求→以下服务执行固定候选×样本→纯值Evaluate。

```csharp
public sealed record RecommendationCase(string CandidateId, string SampleId, OcrRequest Request);
public sealed record RecommendationRunLimits(int MaxCases, int TotalDeadlineMs, int ObserveSliceMs);
public sealed record RecommendationRunPlan(string RunId, string InputFingerprint,
    IReadOnlyList<string> SampleIds, IReadOnlyList<RecommendationCandidate> Candidates,
    IReadOnlyList<RecommendationCase> Cases, RecommendationLimits? EvaluationLimits,
    RecommendationRunLimits RunLimits);
public sealed record TrialJudgement(bool FalseAccept, bool Refused);
public interface IRecommendationTrialJudge
{
    TrialJudgement Judge(string candidateId, string sampleId, OcrResponse observation);
}
public enum RecommendationRunState { Running, Draining, Completed, Failed, Cancelled, TimedOut }
public sealed record RecommendationRunSnapshot(string RunId, string PlanSha256,
    OwnerTicket Ticket, string EngineEpoch, RecommendationRunState State,
    bool AcceptedOperationsReleased, IReadOnlyList<RecommendationTrial> Trials,
    OcrRecommendation? Recommendation, HostFailure? PrimaryFailure,
    IReadOnlyList<string> NotAttemptedCaseIds, long Sequence);
public sealed record RecommendationAdmission(bool Accepted, bool Existing,
    string RunId, string? PlanSha256, IReadOnlyList<OcrError> Errors);
public sealed record RecommendationLookup(bool Found, RecommendationRunSnapshot? Snapshot);
public sealed record RecommendationWait(OwnerActionKind Kind, RecommendationLookup Current);
public interface IOcrRecommendationHost
{
    RecommendationAdmission Start(RecommendationRunPlan plan);
    RecommendationLookup Query(string runId);
    ValueTask<RecommendationWait> WaitAsync(string runId, TimeSpan waitBudget,
        CancellationToken observerCancellation = default);
    bool RequestCancel(string runId);
}
```

唯一类/构造：`public sealed class OcrRecommendationHost : IOcrRecommendationHost`；`public OcrRecommendationHost(OcrProcessOwner owner, OwnerTicket ticket, IOcrEngine engine, IOcrRecommendationEvaluator evaluator, IRecommendationTrialJudge judge, TimeProvider clock)`。ticket须与engine原绑定同根槽/epoch，evaluator/clock/纯同步judge非null，非法ArgumentException/Ocr.InvalidRecommendationHost；没有dispatcher/存储。judge只在Read完成后做标注比较、不能改request/model/decoder，必须有界同步、无后台IO；真实dataset标注Owner保证它可信且资格独立（算法产出不是标注）。service与judge在Start之前原子注册到已reserve根槽、强持，Start中的运行dispatch原Task同§4.4先reserve/登记再执行，不在caller离栈后失主。

Start先按原slot.MaxOperations及每request元数据上限拒绝明显超限输入，再深复制并校验非空RunId/合法64hex InputFingerprint、唯一Sample/Candidate/Case、所有case OcrContract合法且Recognition/Auto（Detection需另先执行）、每Candidate×Sample恰一case、model/method与候选一致，再计算PlanSha256并查原run登记。已有同RunId同Plan立即返回Accepted=true/Existing=true及原PlanSha256，不重新检查当前剩余额度、case身份占用或启动任务；异Plan按下文拒绝。只有首次接纳才核case request.OperationId/key唯一且未用于该engine别的run、当前容量及source绑定。每sample ROI可因宿主显式定位不同，但RoiId顺序/目标数量必须与候选一致；不隐式跨Frame平移。MaxCases/TotalDeadlineMs/ObserveSliceMs>0、ObserveSliceMs≤TotalDeadlineMs、case数量≤MaxCases≤剩余engine/slot.MaxOperations。总体sample/frame和资产由Sources明确提供；budget保守覆盖全部input/结果，不在循环中放宽额度。非法Rejected/Accepted=false/Existing=false，错误用§6 INPUT/METHOD/RESOURCE，未启动后端。Start容量检查与运行登记原子完成；后续Submit仍按同engine接纳规则处理，宿主其它请求占用容量导致某case拒绝时，原run失败并保留未执行分母，不另建engine重试。

PlanSha256=§3.4同UTF8/排序/有限数规则的包装 `{ContractVersion:"ocr-recommendation-service/0.3",Kind:"Plan",Value:{InputFingerprint,SampleIds,Candidates,Cases,EvaluationLimits,RunLimits}}`；SampleIds/Candidates按ID ordinal，Cases按CandidateId/SampleId ordinal，每case Request保持完整OperationId/key及原请求字段（不同操作意图必不同Plan），RunId排除。nested Method/几何依原record字段，不用缺内容的候选IDhash。同RunId同Plan返回Existing原snapshot，同RunId异Plan拒绝IDEMPOTENCY-002；不在Unknown时重跑。每槽只允许一个runner run（service可重复Query/Wait），一个run的新revision需显式新slot/RunId，避免root/task/tombstone无界。不会抢关共享engine或另一业务operation。

首次接纳Accepted=true/Existing=false/Errors空；Existing同样Errors空；拒绝两者false、PlanSha256=null且Errors非空，既有run不被覆盖。CaseId固定为§3.4写法canonical数组`[CandidateId,SampleId]`的SHA-256小写hex，NotAttemptedCaseIds按对应CandidateId/SampleId顺序只列从未获得接纳receipt的case，不用带分隔符的ID拼接。已接纳却缺Trial的case仍在原Plan/operation账中，不混入未接纳分母。Query Found必须Snapshot非null；未知为false/null。run.Sequence从1开始，每次状态、Trial、错误或未执行分母改变原子增加；终态快照不可改写。Wait在run终态且AcceptedOperationsReleased时返回Completed/Found，否则预算到BudgetElapsed、观察取消ObserverCancelled、未知Unknown；Completed只证明本run操作已释放，不证明engine/source/root已Released。

运行在root控制Task内按CandidateId、SampleId顺序单个Submit→有界Wait/Query，使用receipt原epoch/ID；clock总deadline从Start接纳计，ObserveSlice只限制本次观察、不重提。全部原已接受operation的ResourcesReleased才记录Trial，其EndToEndMs=QueueMs+ExecuteMs+DrainMs，PeakWorkingBytes取engine.QueryResources原epoch/operation的完整ObservedPeakWorkingBytes；无完整资源观察则停止评价、PrimaryFailure=HostMissingResourceObservation（Stage=Recommendation），不以Declared预算填实测，不返回Suggested。缺分数Empty是Refused（fake判据下），Failed/Cancelled/TimedOut按真实terminal填Trial且不允许合格candidate；FalseAccept/Refused只从judge/确定未读分类来，不把score猜标签。Sample/输入hash、每case原epoch/ID、not-attempted完整留分母。

judge/Submit/Wait同步异常冻结PrimaryFailure（Stage=Recommendation），停止新case；catch/finally以独立资源/观察预算请求**仅本run已接纳未终态operation**取消，原Task/Frame仍root强持，runner不得关闭共有engine或清源。deadline/RequestCancel先到freeze TimedOut/Cancelled意图并停止新提交，不重判为Completed；state先Draining，**接纳operations全释放才终态**，未排空的run非终态不调用Evaluate。正常且完整组合才Evaluate并Completed；失败/中止不发布Suggested（Recommendation=null）、保留Trials/NotAttemptedCaseIds，不能用之前暂时最好当最终建议。内部任何清理失败另记root CleanupFailures、不覆盖PrimaryFailure；Wait预算到BudgetElapsed、observer取消ObserverCancelled，仅观察，不取消run；未知run Found=false/Unknown，无winner/不生成run。

root Cleanup停止run新接纳并请求当前run取消，再等runner原Task和accepted operation真实释放→engine/source按§4.4清理；运行服务Query在engine墓碑仍可定位原run结果，资料受root已reserve额度。RequestCancel返回true仅第一次活动run接受，重复/终态/未知false；Query原ticket在root上仍有效，错epoch按Unknown处理。有限恢复只用root.Recover观察/重试已faulted幂等释放，不自动Start/Submit新case。应用读取/导出Recommendation再次检查InputFingerprint及CurrentRecommendationFingerprint、权限/保存Unknown规则不变。

协议评价器准确声明为 `public sealed class ProtocolEmptyJudge : IRecommendationTrialJudge`，namespace=`Asun.Modules.Ocr.Simulation`；公开无参构造 `public ProtocolEmptyJudge()`，成员 `public TrialJudgement Judge(string candidateId, string sampleId, OcrResponse observation)`。输入非null、身份非空，且必须有至少一个item、所有item为Empty/Words空、trace.json的ActualParameters包含唯一Execution=ProtocolOnly，才返回`new TrialJudgement(false,true)`；其它输入抛InvalidOperationException/Ocr.ProtocolUnexpectedObservation。它只验证协议Empty分类，不提供实际标注/识读正确率或伪造Read。

完整双sample×双candidate输入如下，静态fixture仍放Core.Tests（using System.Linq/System.Text.Json/System.Security.Cryptography）：

```csharp
public static (IReadOnlyList<ProtocolFrame> Frames, ProtocolAsset Asset,
    RecommendationRunPlan Plan) MakeProtocolRecommendationFixture()
{
    var fixture1 = MakeProtocolFixture("label-sample-1");
    var fixture2 = MakeProtocolFixture("label-sample-2");
    string[] sampleIds = { "sample-1", "sample-2" };
    ProtocolFrame[] frames = { fixture1.Frame, fixture2.Frame };
    RecommendationCandidate[] candidates =
    {
        new("c1", new[] { ProtocolRoi("r") }, fixture1.Method),
        new("c2", new[] { ProtocolRoi("r") }, fixture1.Method)
    };
    var cases = new List<RecommendationCase>();
    foreach (var candidate in candidates)
        for (int i = 0; i < sampleIds.Length; ++i)
            cases.Add(new RecommendationCase(candidate.CandidateId, sampleIds[i],
                new OcrRequest("recommend-" + candidate.CandidateId + "-" + sampleIds[i],
                    "recommend/" + candidate.CandidateId + "/" + sampleIds[i],
                    frames[i].Image, candidate.Rois, candidate.Method)));
    var evaluation = new RecommendationLimits(0, 2, 1000, 1048576, "protocol-eval");
    var runLimits = new RecommendationRunLimits(4, 5000, 50);
    IOcrContract contract = new OcrContract();
    // 固定字段顺序的协议闭包；Request hash覆盖实际Frame/ROI/Method/资产字节身份。
    byte[] closure = JsonSerializer.SerializeToUtf8Bytes(new
    {
        ContractVersion = "ocr-protocol-evaluation/0.3",
        JudgeVersion = "ProtocolEmptyJudge/0.3",
        Cases = cases.Select(c => new
        {
            c.CandidateId, c.SampleId,
            RequestSha256 = contract.RequestSha256(c.Request),
            ExpectedClassification = "RefusedEmptyProtocolOnly"
        }).ToArray(),
        EvaluationLimits = evaluation,
        RunLimits = runLimits
    });
    string fingerprint = Convert.ToHexStringLower(SHA256.HashData(closure));
    var plan = new RecommendationRunPlan("protocol-run", fingerprint, sampleIds,
        candidates, cases, evaluation, runLimits);
    return (frames, fixture1.Asset, plan);
}
```

完整协议runner装配仍遵循Host A的Reserve→Attach→factory→engine及异常/finally控制流，不能在已经Cleanup的Host A实例上再Start：先`ticket=process.Reserve("recommendation-host",new OwnerSlotLimits(8,160,4194304,2097152,1048576,2))`，随后`fixture=MakeProtocolRecommendationFixture()`、`control=new OcrProtocolControl(Array.Empty<ProtocolStep>())`、`source=new OcrProtocolSource(fixture.Frames,new[]{fixture.Asset},new ProtocolSourceLimits(2,1,1048576),control)`；Attach必须Retained，`factory=new OcrProtocolAdapterFactory("recommendation",ProtocolCapabilities("recommendation"),control)`，`engine=new OcrEngine(process,ticket,source.Frames,source.Assets,factory,new OcrRuntimeOptions(8,1,8,4194304,2097152,64),clock,null)`。最后构造`new OcrRecommendationHost(process,ticket,engine,new OcrRecommendationEvaluator(),new ProtocolEmptyJudge(),clock)`，`Start(fixture.Plan)`→有限Wait/Query，main有限推进clock。四次Empty使各候选Refused=2、FalseAccept=0；只有实测完整且E2E/峰值满足本协议Limits时才可能Suggested并按既有排序选c1，超限则NoEligibleCandidate或运行失败，不硬写成功。任何异常/finally按Host A模板Cleanup/ConfirmRetention；协议结果不构成视觉通过。runner服务跟C2-R接收，纯值C3的Propose/Evaluate可独立运行不依赖此Host。

## 10. 可选证据控件与操作流

### 10.1 契约、角色和接入

`OcrEvidenceControl`是可嵌入WPF `UserControl`，namespace `Asun.Modules.Ocr.Wpf`，自有依赖属性如下；UI契约类型也仅在该程序集。

```csharp
public enum EvidenceSaveState { NotRequested, Saving, Saved, Failed, Unknown }
public enum SaveCommitKnowledge { NotSubmitted, Committed, ConfirmedNotCommitted, Unknown }
public enum SaveResourceState { Released, Pending, Unknown }
public enum SaveQueryState { NotQueried, Querying, ReceiptFound, NotFound, Failed }
public sealed record EvidenceSaveProjection(string IntentId, string AttemptId,
    string OriginEngineEpoch, string OriginOperationId, string EvidenceRef, SaveCommitKnowledge CommitKnowledge,
    SaveResourceState Resources, SaveQueryState QueryState, string? ReceiptRef);
public sealed record OcrUiSnapshot(long Generation, LookupKind Lookup,
    OperationSnapshot? Operation, OcrMode? Mode, EvidenceSaveState SaveState,
    EvidenceSaveProjection? Save, string? SaveErrorKey);
public sealed record OcrUiCommand(long Generation, string EngineEpoch,
    string OperationId, string? RoiId, string? EvidenceRef, string? CandidateId,
    string? InputFingerprint, string? SaveIntentId, string? SaveAttemptId);
```

输入为 `OcrUiSnapshot? View`、`byte[]? PreviewPng`、`string? SelectedRoiId`、`IReadOnlyList<RoiProposal> RoiProposals`、`OcrRecommendation? Recommendation`、`string? CurrentRecommendationFingerprint`、`object? ImageContent`、`string CultureName`、`string HostThemeName`、`bool CanCancel/CanRequestRetry/CanExport/CanQuerySave/CanSelectSuggestion`。PreviewPng深复制，只有显示作用；View一次更新代次/身份/查询/运行/保存状态，防止分别设置Lookup/Snapshot短暂错配。控件不解码算法像素或初始化模型。宿主外部viewport经ImageContent注入，控件模板 `PART_ImagePresenter`（ContentControl）绑定该属性；ImageContent=null时显示默认PNG预览。控件不销毁宿主传入viewport，只撤本地交互挂接，不依赖全局视口初始化。

公开CLR事件为 `event Action<OcrUiCommand>? CancelRequested, RetryRequested, ExportEvidenceRequested, QuerySaveRequested, RoiSelectionChanged, SuggestionSelected`。cancel/retry携OperationId；export还携EvidenceRef和宿主预建的SaveIntentId/SaveAttemptId且完整响应存在；QuerySaveRequested携原IntentId/AttemptId/EvidenceRef及Save.OriginEngineEpoch/OriginOperationId，宿主调用原存储Owner查询，绝不Submit；每次执行校验投影身份/hash与资源状态；selection携RoiId；suggestion携CandidateId及InputFingerprint（来自Recommendation）由宿主核对。事件同时携Generation/EngineEpoch，宿主执行前重新检查当前权限/operation/代次，拒绝迟到命令。未知View.Lookup时禁用cancel/export；非终态禁用retry；CurrentRecommendationFingerprint不等于Recommendation.InputFingerprint或为空、NotEvaluated建议均禁用候选选用。事件只因用户交互发出，宿主设置View/SelectedRoiId等不回发命令，防止双向绑定循环；SelectedRoiId必须存在于当前response，缺失清为null。CultureName未支持时由宿主本地化服务回退zh-CN并显示稳定语言诊断，不在控件改全局文化；资源键找不到不能泄露内部英文键作为操作文字。控件只发事件，无IOcrEngine调用、File IO、设备命令或生产Apply。

宿主在Dispatcher线程Apply最新View，后台回调先比generation和Sequence再投影；旧epoch/operation通知不覆盖新选择。操作员看图像/区域/原读/运行状态，复核员看候选和支持，工程师看只读参数与ROI建议；权限由宿主布尔值注入、执行处再核，隐藏面板不赋权。操作流为提交→观察→图表双向选择→展开证据→发复核/新attempt请求→宿主执行。保存状态与提交知识/资源状态独立显示，Save投影规则见§11B.5。CanExport只是权限，控件还必须核资源Released及NotSubmitted（原意图未发起）或ConfirmedNotCommitted（原尝试已由Owner证明未提交并排空）；Failed/Unknown/Pending绝不按“可重试”处理。CanQuerySave与原意图身份齐全时可发查询（即使当前OCR Lookup=Unknown）；命令使用Save中的原epoch/operation，不能换成新engine身份。Save非null时原epoch/operation/IntentId/AttemptId非空，EvidenceRef合法；有当前response时必须匹配其身份/证据，无当前response只可查询，不可export。Unknown保留原IntentId/AttemptId/EvidenceRef，不生成新意图或覆写原尝试。Saved只允许Committed且Released并有ReceiptRef，Committed+Pending显示“已提交，等待释放”，NotFound只显示“未查到回执”，不能显示“未保存”。违反投影组合禁用保存命令并显示恢复提示，不回写OCR状态。Unloaded撤订阅、清本地PNG/Flyout；宿主仍持runtime排空，不释放native。控件能卸载后重新挂接任一已存在snapshot，无隐式新提交。

### 10.2 1920×1080 构图与 DevExpress 25.2.3

使用本机DevExpress **25.2.3**，官方API依据为25.2文档，非真实编译/交互通过声明。嵌入宿主的固定1920×1080验证viewport，先扣除任务栏、边框、标题/状态栏，再把可用内容约60%宽给图像，右侧区域表/详情；底部一行放运行状态与主命令。局部布局可调但主命令始终可见；保存布局由宿主完成，失效layout恢复默认，不改显示设置。

| 部位 | 控件与具体使用 | 联动/状态 |
|---|---|---|
| 图像/表/详情工作区 | DockLayoutManager + LayoutGroup/LayoutPanel，消费宿主既有viewport公开投影 | 图像选框→SelectedRoiId→表定位；表选行→按§10.5.2完整对象键高亮对应RoiId区域框，不重新计算 |
| 区域与词 | GridControl.ItemsSource + TableView；固定RoiId/运行状态列，原读/原因/score meaning列可排序过滤，虚拟化 | 排序不改Words/RoiId或输入顺序；低信不用单一绿色/红色判断 |
| 方法/资产证据 | PropertyGridControl.SelectedObject绑定只读投影，类别/搜索 | 不绑定活动可写对象；生产profile禁止热改 |
| 候选/拒识细节 | DevExpress.Xpf.Editors.Flyout.FlyoutControl，PlacementTarget/IsOpen/StaysOpen显式控制 | Esc关闭；候选和恢复说明渐进展开，关键取消/复核不放Flyout |
| 工程诊断 | 可选ChartControl系列DataSource/ArgumentDataMember/ValueDataMember | 只画同后端分数或阶段耗时；图无数据明确空态，不跨模型概率对比 |
| 提示/主题 | bars/ribbon使用SuperTip；SimpleButton.ToolTip用SuperTipControl包装 | 限制/取消后等待说明三语；ThemeManager.ThemeName宿主注入，lightweight主题走LightweightThemeManager，不混用 |

统一字号/间距/图标/焦点样式，运行/质量/保存状态各占独立字段，不用一个“成功”图标覆盖三者。图像缩放平移不改变几何事实。选择缓存键为EngineEpoch+OperationId+RoiId；迟到旧operation更新丢弃，切换operation清选择与候选，不清native lease。短动效只用于展开/选中，取消和错误即时显示。

### 10.3 三语、键盘与恢复断言

全部标题/列/命令/参数/状态/原因/tooltip/错误资源覆盖zh-CN、zh-TW、en-US；宿主设置CultureName动态刷新，不在控件放语言入口。示例键：Ocr.Processing“正在处理／正在處理／Processing”；Ocr.Draining“等待释放／等待釋放／Waiting for release”；Ocr.ReviewRequired“需要复核／需要複核／Review required”；Ocr.Unknown“结果未确认／結果未確認／Unconfirmed”，恢复提示另取Ocr.TipOriginalTask。原生错误只显示稳定恢复文字和correlation，不直接翻译堆栈。

Tab按图像工具→区域表→详情→主命令，Enter确认选行，Esc关闭Flyout；按钮/区域有AutomationProperties.Name，动态状态按官方LiveSetting/LiveRegionChanged规则提供UIA通知。取消点击后只发一次请求，显示等待排空；TimedOut仅在资源释放后显示，Unknown不显示空串。权限撤销即更新Can*；Export失败是宿主保存状态，OCR原读不变；错误回调/查询NotFound不证明未提交或资源释放。保存未知命令显示“查询保存状态／查詢儲存狀態／Check save status”；提交未知提示“提交未确认，请查询原保存任务／提交未確認，請查詢原儲存工作／Submission unconfirmed. Check the original save task”。已确认未提交且已排空才显示“重新保存／重新儲存／Save again”，由宿主显式建立新AttemptId并保留原意图/证据。验证固定1920×1080中三语长度、真实WPF焦点/UIA/DPI/取消窗口关闭/多operation切换；不另跑其它分辨率矩阵。

### 10.4 证据控件实际组合、资源与完整交互

W设计由本原会话收口，不把PropertyGrid/PNG/viewport接线或三语文字留给实现者选。默认无参`OcrEvidenceControl()`只建控件与完整内置资源，无模型/任务。控件是只读证据投影，不新增可写参数面板、训练页或产品命令；参数建议仍显示冻结Profile与理由，经SuggestionSelected交宿主草稿，不在此控件改原值。

布局用§10.2已选DevExpress组合：DockLayoutManager根横向LayoutGroup，左LayoutPanel.ItemWidth=`3*`放PART_ImagePresenter，右`2*`放上下两个LayoutGroup（区域Grid `3*`、详情PropertyGrid `2*`）；底部在Dock外用WPF Grid固定一行身份/状态/命令，不能停靠隐藏。内容margin=8 DIP、控件间距=8、标题/命令高度32、正文14 DIP/小标题16 DIP，最小命令hit尺寸32×32，密度固定不以缩字解决英文长度。面板标题、列标题、数值单位与状态都来自本节Catalog；像素/度/ms/bytes按明确单位显示，空值用本地化“未提供”，不显示0。图像主区至少可用内容宽度55%，默认60%；右栏不足显示长文本则Wrap/虚拟滚动并可复制完整原读，横向滚动只限表/属性区，主命令不溢出底栏。受宿主标题/状态栏扣除后在1920×1080实测，不把1920当客户区宽。

Grid.ItemsSource是当前response的不可变显示行（RoiId、WordId、Outcome、RawText、ScoreMeaning、拒识/支持、LineOrdinal、只读原hash），`TableView.AllowEditing=false,ShowGroupPanel=false,NavigationStyle=Row,ShowIndicator=false`；每GridColumn.ReadOnly=true。Grid.SelectedItem连接本控件选中行；排序/过滤只作用于展示副本，所有命令仍携原RoiId/WordId所属operation；无词的Empty/NotRun也各保留一ROI行，不抹分母。PropertyGridControl.SelectedObject是只读描述对象、ReadOnly=true，显示分组为输入/方法/资产/结果/资源/保存，不把生产Method对象交可写editor。Flyout由本行“详情”SimpleButton启闭；公开PlacementTarget/IsOpen/StaysOpen，不额外使用未定义PopupMenu API。原读/保存/资源三状态行使用文字+图标，颜色只是辅助手段；待排空/未知用中性警示，无绿色PASS。

图像默认PNG为显示副本：编码producer取Evidence中与当前FrameSha256匹配的raw byte图，Gray16显示转换沿已冻结Preprocess（不是算法自动拉伸）；Wpf只用BitmapImage(CacheOption=OnLoad)从已深复制PreviewPng解码并Freeze，不持外部stream。PNG上限同时核bytes≤当前Method.MaxEvidenceBytes及解码像素≤MaxPixels，缺当前有效View/非法PNG只显示本地化图像错误并禁图像选择，不故障后留旧图当新身份。PNG默认等比例fit，滚轮缩放围绕指针、范围[0.1,16]倍fit，拖动平移/双击fit/Ctrl+0 fit/Ctrl+1一比一；从Frame坐标四角经同一显示矩阵画overlay，hit test用逆矩阵只命中实际可见完整ROI，重叠候选保留列表供Enter/键盘选，不靠绘制顺序自动选工艺目标。源Probe/计量不从PNG取值。若ImageContent非null，这些操作由实际viewport执行；控件不再叠第二套PNG手势/ROI编辑。

字符top-N按原PositionIndex/rank展示，Blank为“空白标记”（区别普通空格）、MLP拒识为“拒识”；原串中控制scalar使用`U+XXXX`转义显示并可复制原值（复制需宿主数据权限，未注入则只显示），不把控制字符当隐藏空字。图表选择同步原RoiId：用户选择才发RoiSelectionChanged，程序Apply不回发；operation/generation切换清本地选择、关闭Flyout和过期Suggestion，保持原root任务。默认只读展示不开放通用任意文本输入、文件picker或行删除。Chart只画当前同方法阶段ms与有限建议候选记录，无数据为空态；无完整资源实测不画虚构内存值。

PNG生产者在I/W Host从当前完整证据生成显示副本，PNG tEXt固定写FrameSha256/EngineEpoch/OperationId/Generation四项身份（hash/epoch为ASCII hex、OperationId为严格UTF-8的标准Base64、Generation为无前导零十进制long），不写原读/权限；它是可信Host装配标记，不是生产证据签名或源hash验证替代。控件View更换时先清旧PNG；PreviewPng setter在有界扫描IHDR/tEXt/CRC后核四项与当前View、Width/Height与原Frame相等，缺/重复/错身份拒绝，迟到旧PNG不留旧画面。IHDR宽高、decoded RGBA的checked 4WH及编码+解码+旧副本并存上界在BitmapImage分配前核源Method与Input.MaxUiBytes预算；累计chunk大小受输入长度，不读取外部文件或解压无界文本。默认不启用原串复制命令（现Can*没有复制授权），需要复制的宿主通过已授权证据导出/自己的数据权限入口实现，不在本控件猜CanCopy。Ctrl+1的1:1为固定直接显示命令，若它超出[0.1,16]倍fit的本控件显示边界则禁用并提示缩放范围，不能标1:1却实际clamp到其它比例。

```csharp
// namespace Asun.Modules.Ocr.Wpf；Assembly UI v0.2，Core值/Service版本不变。
public sealed record OcrUiResources(string CultureName, string Revision,
    IReadOnlyDictionary<string,string> Text);
public sealed record OcrUiInputProjection(string EngineEpoch, long Generation,
    OcrRequest? Ocr, OcvRequest? Ocv, long MaxUiBytes);
public static class OcrUiResourceCatalog
{
    public static IReadOnlyList<string> RequiredKeys { get; }
    public static OcrUiResources Get(string cultureName);
}
```

UI v0.2新增依赖属性`OcrUiInputProjection? Input`，补足运行Snapshot不含原请求的显示边界。Host注入恰一个完整Ocr/Ocv请求的深冻结快照、原epoch/generation及已预约正MaxUiBytes；控件用OcrContract.Validate/RequestSha256/MethodSha256核等于当前View.Operation原身份/Kind/hash，epoch/generation也相等。Frame/ROI/Preprocess/预算/参数表/PNG全部从此Input取，不从OperationSnapshot猜不存在的Method字段或解析未定义helper。Input与View更新任一不匹配时清预览/overlay/参数，仅保运行诊断，待同代完整组合才恢复；不因Host先后赋值短暂显示旧图。UI bytes含Input元数据、复制PNG/解码图/行投影/资源/旧代并存，先reserve再复制；超预算保持错误空态。Input只供显示，不能使控件Submit/持有Frame native lease或修改原请求；缺Input时仍允许身份齐全的原保存状态查询。

内置三语由Catalog随Wpf DLL发布；新增依赖属性`OcrUiResources? TextResources`供宿主完整扩展语言快照。RequiredKeys取下表全部Ocr.键、§6全部完整错误码的Ocr.Error.<code>、下列参数/理由表的Ocr.Parameter.<field>/Ocr.Reason.<key>及补充状态表键，按Ordinal排序；不从所有public enum/DTO反射生成文字。PropertyGrid只显示这些显式描述字段，内部任务表/事件enum不直接作为PropertyGrid枚举editor，阶段状态用固定映射展示，避免同名enum键冲突。Get只接内置culture，未知ArgumentException/Ocr.UnknownCulture；控件CultureName未知且没有匹配扩展资源时取zh-CN并显示“语言资源不可用”，不改全局Culture。TextResources要求culture/revision非空、键集完整无空值/重复、单值≤256 Unicode scalar、总UTF-8≤262144bytes；超限/缺键保持原完整资源并显示内置资源错误，不泄漏key。动态切换只更新文字/格式，当前View/lease/保存知识不变；单位符号、ID、版本、RawText不翻译。对新语言使用宿主CultureName+同名完整快照，不重复放语言入口。

| 键（前缀Ocr.） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Image / Regions / Details / Method / Assets | 图像／区域／详情／方法／资产 | 影像／區域／詳細資料／方法／資產 | Image / Regions / Details / Method / Assets |
| RawText / Candidates / Support / Runtime / Save | 原读／候选／支持范围／运行／保存 | 原讀／候選／支持範圍／執行／儲存 | Raw text / Candidates / Support / Runtime / Save |
| Cancel / Retry / Export / QuerySave / SelectSuggestion | 取消／新建识读／保存证据／查询保存状态／选择建议 | 取消／新增識讀／儲存證據／查詢儲存狀態／選擇建議 | Cancel / New reading / Save evidence / Check save status / Select suggestion |
| Fit / OneToOne / UnknownCulture / ResourceMissing / ImageInvalid | 适应窗口／一比一／语言资源不可用／界面文字不可用／图像不可用 | 符合視窗／一比一／語言資源不可用／介面文字不可用／影像不可用 | Fit / 1:1 / Language unavailable / Text unavailable / Image unavailable |
| Empty / NotRun / Blank / Rejected / Missing / Stale | 未读到文字／未执行／空白标记／拒识／未提供／建议已过期 | 未讀到文字／未執行／空白標記／拒識／未提供／建議已過期 | No text read / Not run / Blank marker / Rejected / Unavailable / Suggestion expired |
| Read / Detected / Ambiguous / ReviewRequired / NotComputed | 已识读／已定位／结果有歧义／需要复核／未计算 | 已識讀／已定位／結果有歧義／需要複核／未計算 | Read / Located / Ambiguous / Review required / Not computed |
| Waiting / Completed / Failed / Cancelled / TimedOut / Unknown | 等待执行／已结束／执行失败／已取消／已超时／结果未确认 | 等待執行／已結束／執行失敗／已取消／已逾時／結果未確認 | Waiting / Finished / Failed / Cancelled / Timed out / Unconfirmed |
| Acquiring / Processing / Draining / Quarantined / ResourcesReleased | 正在取得输入／正在处理／等待释放／释放未确认／已释放 | 正在取得輸入／正在處理／等待釋放／釋放未確認／已釋放 | Acquiring input / Processing / Waiting for release / Release unconfirmed / Released |
| SaveNotSubmitted / SaveCommitted / SaveNotCommitted / SaveUnknown / ReceiptMissing | 尚未提交／已提交／确认未提交／提交未确认／未查到回执 | 尚未提交／已提交／確認未提交／提交未確認／未查到回執 | Not submitted / Submitted / Confirmed not submitted / Submission unconfirmed / Receipt not found |
| TipCancel / TipRetry / TipExport / TipQuery / TipSuggestion | 请求停止后仍需等待释放／新识读保留原结果／保存完整证据，失败时先查询／只查询原保存任务／仅选择建议，不修改生产参数 | 要求停止後仍須等待釋放／新識讀保留原結果／儲存完整證據，失敗時先查詢／只查詢原儲存工作／僅選擇建議，不修改生產參數 | Wait for release after cancelling / Keep the original result for a new reading / Save full evidence; check status after failure / Check the original save task / Select a suggestion; production settings stay unchanged |

State键精确映射：Queued→Waiting；Acquiring/QualityChecking→Acquiring；Detecting/Recognizing/DetectingAndRecognizing/Verifying/Ordering/ObservationChecking→Processing；内部子阶段仅留诊断code，不将enum名直接放状态栏；CancelRequested/Draining→Draining；Quarantined→Quarantined；终态用表中同名键，StopReason只另栏显示原因，不把Requested写终态。Host/Owner/推荐状态复用相同词义，NotEvaluated→“尚未评价／尚未評估／Not evaluated”，NoEligibleCandidate→“没有满足条件的候选／沒有符合條件的候選／No eligible candidate”，Suggested→“有建议待审阅／有建議待審閱／Suggestion for review”。所有错误码资源按§6的恢复动作映射：INPUT/METHOD→“输入或方法无效，请检查参数／輸入或方法無效，請檢查參數／Invalid input or method. Check settings”；ASSET/ADAPTER→“资产或后端不可用，请检查版本／資產或後端不可用，請檢查版本／Asset or backend unavailable. Check versions”；QUALITY/RESULT→“观察不完整，请复核输入与结果／觀察不完整，請複核輸入與結果／Incomplete observation. Review input and result”；DRAIN→§10.3等待/Unknown查询文字；RESOURCE→“资源不足，请等待原任务释放／資源不足，請等待原工作釋放／Insufficient resources. Wait for release”；IDEMPOTENCY→“任务身份冲突，请保留原任务并检查请求／工作識別衝突，請保留原工作並檢查要求／Task identity conflict. Keep the original task and check the request”；ENGINE/DIAG→“执行或通知失败，请查询原任务／執行或通知失敗，請查詢原工作／Execution or notification failed. Check the original task”。诊断详细页显示code/correlation，不翻译原异常或泄露像素/文本到日志。

参数显示键如下；并列字段按左右顺序一一对应三语文字，每一个字段产生独立键。未列出的协议元数据以已本地化“标识/版本/摘要”栏显示值，不把属性名自动展开为操作文字；本控件没有H程序集引用，recipe由Host投影到同字段名的只读描述行。

| field（前缀Ocr.Parameter.） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| WidthPx / HeightPx / StrideBytes / AngleDeg / DirectionDeg | 宽度／高度／行步长／区域角度／旋正角度 | 寬度／高度／列步長／區域角度／旋正角度 | Width / Height / Row stride / Region angle / Deskew angle |
| XPx / YPx / ValidSupportPolygon / Format / CoordinateRef | 左边位置／上边位置／有效支持／像素格式／坐标引用 | 左側位置／上側位置／有效支持／像素格式／座標引用 | Left position / Top position / Valid support / Pixel format / Coordinate reference |
| ProfileId / Revision / AssetId / QualificationRef / Sha256 | 配置标识／版本／资产标识／资格引用／摘要 | 設定識別／版本／資產識別／資格引用／摘要 | Profile ID / Revision / Asset ID / Qualification reference / Digest |
| Mode / Backend / Route / ReadingDirection / MinEngineScore | 模式／后端／路线／阅读方向／字符最低分数 | 模式／後端／路線／閱讀方向／字元最低分數 | Mode / Backend / Route / Reading direction / Minimum character score |
| OrderedSymbols / BlankSymbol / MappingId / MappedSymbols / AllowedScalars | 模型字符表／空白标记／映射标识／映射字符表／允许字符 | 模型字元表／空白標記／對應識別／對應字元表／允許字元 | Model alphabet / Blank symbol / Mapping ID / Mapped alphabet / Allowed characters |
| Gray16Min / Gray16Max / Invert / DarkOnLight / UseAutoThreshold | 16位灰度下限／16位灰度上限／反相／暗字亮底／自动阈值 | 16位灰階下限／16位灰階上限／反相／暗字亮底／自動閾值 | 16-bit gray minimum / 16-bit gray maximum / Invert / Dark on light / Automatic threshold |
| ThresholdMin / ThresholdMax / AutoThresholdSigma | 分割灰度下限／分割灰度上限／自动阈值Sigma | 分割灰階下限／分割灰階上限／自動閾值Sigma | Segmentation gray minimum / Segmentation gray maximum / Threshold sigma |
| MinAreaPx2 / MaxAreaPx2 / MinCharWidthPx / MaxCharWidthPx / MinCharHeightPx / MaxCharHeightPx | 最小面积／最大面积／最小字宽／最大字宽／最小字高／最大字高 | 最小面積／最大面積／最小字寬／最大字寬／最小字高／最大字高 | Minimum area / Maximum area / Minimum character width / Maximum character width / Minimum character height / Maximum character height |
| DetectionWidthPx / DetectionHeightPx / Tiling / TilingOverlapPx / RecognitionAlignment | 检测宽度／检测高度／分块／分块重叠／文字对齐 | 偵測寬度／偵測高度／分塊／分塊重疊／文字對齊 | Detection width / Detection height / Tiling / Tile overlap / Text alignment |
| Runtime / DeviceId / RuntimeVersion / DeviceRef / RecognitionBatchSize / IntZooming | 执行后端／设备标识／运行版本／设备引用／识读批量／整数缩放 | 執行後端／裝置識別／執行版本／裝置引用／識讀批次／整數縮放 | Runtime backend / Device ID / Runtime version / Device reference / Recognition batch size / Integer zooming |
| MinCharacterScore / MinLinkScore / MinWordAreaPx2 / MinWordScore | 检测字符最低分数／连接最低分数／最小词面积／检测词最低分数 | 偵測字元最低分數／連接最低分數／最小詞面積／偵測詞最低分數 | Minimum detection character score / Minimum link score / Minimum word area / Minimum detection word score |
| SortByLine / RoutePolicyId / RoiId / WordId / LineOrdinal / PositionIndex / Rank | 按行排序／路线规则／区域标识／词标识／行序号／字符位置／候选序号 | 依行排序／路線規則／區域識別／詞識別／行序號／字元位置／候選序號 | Sort by line / Route policy / Region ID / Word ID / Line index / Character position / Candidate rank |
| MinContrast / MinStrokeWidthPx / MaxStrokeWidthPx | 最小对比度／最小笔画宽度／最大笔画宽度 | 最小對比度／最小筆畫寬度／最大筆畫寬度 | Minimum contrast / Minimum stroke width / Maximum stroke width |
| AddFragments / SeparateTouchingChars / ReturnPunctuation / ReturnSeparators | 合并碎片／分离相连字符／保留标点／保留分隔符 | 合併碎片／分離相連字元／保留標點／保留分隔符 | Add fragments / Separate touching characters / Include punctuation / Include separators |
| DotPrint / TightDotSpacing / MinDotCharacterGapPx / MaxDotGapPx | 点阵字符／紧密点阵间距／点阵字间距下限／点间距上限 | 點陣字元／緊密點陣間距／點陣字間距下限／點間距上限 | Dot print / Tight dot spacing / Minimum dot-print character gap / Maximum dot gap |
| CharacterHeightPx / CharacterWidthPx / StrokeWidthPx / BaseLineTolerance | 字高／字宽／笔画宽度／基线偏差比例 | 字高／字寬／筆畫寬度／基線偏差比例 | Character height / Character width / Stroke width / Base-line tolerance ratio |
| UppercaseOnly / Imprinted / EliminateHorizontalLines / MinFragmentAreaPx2 | 仅大写和数字／压印字符／去除水平线／最小碎片面积 | 僅大寫與數字／壓印字元／去除水平線／最小碎片面積 | Uppercase and digits only / Imprinted characters / Remove horizontal lines / Minimum fragment area |
| PatternName / AdaptPosition / AdaptSize / AdaptGray / AdaptAngle / ThresholdMode / Threshold | 参考名称／位置适配／尺寸适配／灰度适配／角度适配／误差模式／误差阈值 | 參考名稱／位置適配／尺寸適配／灰階適配／角度適配／誤差模式／誤差閾值 | Pattern name / Position adaptation / Size adaptation / Gray adaptation / Angle adaptation / Error mode / Error threshold |
| DeadlineMs / MaxPixels / MaxRois / MaxWordsPerRoi / MaxCharacters / CharacterTopN / MaxTiles | 截止时间／像素上限／区域上限／每区词数上限／字符上限／每字候选数／分块上限 | 截止時間／像素上限／區域上限／每區詞數上限／字元上限／每字候選數／分塊上限 | Deadline / Pixel limit / Region limit / Words per region limit / Character limit / Candidates per character / Tile limit |
| MaxWorkingBytes / MaxEvidenceBytes / MaxMetadataUtf8Bytes | 工作字节上限／证据字节上限／元数据字节上限 | 工作位元組上限／證據位元組上限／中繼資料位元組上限 | Working byte limit / Evidence byte limit / Metadata byte limit |

补充静态状态/值资源（前缀Ocr.）：

| 键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| UnknownCulture / InvalidResources / ImageUnavailable / NotProvided | 语言资源不可用／语言资源不完整／图像不可用／未提供 | 語言資源不可用／語言資源不完整／影像不可用／未提供 | Language resources unavailable / Incomplete language resources / Image unavailable / Not provided |
| ZoomLimit / Input / Result / Resources / Phase | 缩放超出范围／输入／结果／资源／阶段 | 縮放超出範圍／輸入／結果／資源／階段 | Zoom outside range / Input / Result / Resources / Phase |
| TipOriginalTask | 请查询原任务，未确认前不要重新识读 | 請查詢原工作，未確認前不要重新識讀 | Check the original task before starting a new reading |
| Blank / Rejection / True / False | 空白标记／拒识／是／否 | 空白標記／拒識／是／否 | Blank symbol / Rejection / Yes / No |
| NotEvaluated / NoEligibleCandidate / Suggested | 尚未评价／没有满足条件的候选／有建议待审阅 | 尚未評估／沒有符合條件的候選／有建議待審閱 | Not evaluated / No eligible candidate / Suggestion for review |
| Identification / Version / Digest / Quality / Correlation | 标识／版本／摘要／质量数值／诊断标识 | 識別／版本／摘要／品質數值／診斷識別 | ID / Version / Digest / Quality value / Diagnostic ID |
| Detection / Recognition / Auto / HalconDeepOcr / HalconClassic / ExternalApproved | 文字检测／文字识读／检测及识读／HALCON深度文字／HALCON经典文字／已批准外部后端 | 文字偵測／文字識讀／偵測及識讀／HALCON深度文字／HALCON經典文字／已核准外部後端 | Text detection / Text recognition / Detection and recognition / HALCON Deep OCR / HALCON classic OCR / Approved external backend |
| SegmentedCharacters / TextModelAuto / TextModelManual / LeftToRight / RightToLeft / Unresolved / SingleWord | 分割字符／自动文本模型／手动文本模型／从左到右／从右到左／顺序未确定／单词 | 分割字元／自動文字模型／手動文字模型／從左到右／從右到左／順序未確定／單詞 | Segmented characters / Automatic text model / Manual text model / Left to right / Right to left / Order unresolved / Single word |
| ErrorPixelRatio / NormalizedErrorSum / EngineNative / CalibratedForProfile / None / NotRun / Computed | 错误像素比例／归一误差和／后端原生分数／配置校准分数／无／未执行／已计算 | 錯誤像素比例／正規化誤差和／後端原生分數／設定校準分數／無／未執行／已計算 | Error pixel ratio / Normalized error sum / Native engine score / Profile-calibrated score / None / Not run / Computed |
| SaveNotRequested / Saving / Saved / SaveFailed / SavePending / ReceiptFound / Querying | 尚未保存／正在保存／已保存／保存失败／等待保存资源释放／已查到回执／正在查询 | 尚未儲存／正在儲存／已儲存／儲存失敗／等待儲存資源釋放／已查到回執／正在查詢 | Not saved yet / Saving / Saved / Save failed / Waiting for save resources / Receipt found / Checking status |
| StopCancel / StopDeadline / StopShutdown / StopFailure | 请求取消／截止时间已到／服务正在关闭／执行出错 | 要求取消／截止時間已到／服務正在關閉／執行錯誤 | Cancellation requested / Deadline reached / Service closing / Execution failed |

理由资源（前缀Ocr.Reason.）：

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| InvalidGeometry / OutsideFrame / InsufficientSupport / RelatedWords | 几何无效／超出图像／支持范围不足／文字区域重叠 | 幾何無效／超出影像／支持範圍不足／文字區域重疊 | Invalid geometry / Outside image / Insufficient support / Overlapping text regions |
| ProposalLimitReached / MissingTrial / NotDrained / ExecutionFailed | 已达建议上限／缺少试验结果／尚未释放／执行失败 | 已達建議上限／缺少試驗結果／尚未釋放／執行失敗 | Proposal limit reached / Missing trial / Resources still in use / Execution failed |
| MissingTiming / FalseAcceptLimit / RefusalLimit / LatencyLimit / ResourceLimit | 缺少耗时数据／误接受超限／拒识超限／耗时超限／资源超限 | 缺少耗時資料／誤接受超限／拒識超限／耗時超限／資源超限 | Missing timing / False acceptance limit exceeded / Refusal limit exceeded / Latency limit exceeded / Resource limit exceeded |
| NoCandidates / NoSamples / NoLimits | 没有候选／没有样本／未设置验收上限 | 沒有候選／沒有樣本／未設定驗收上限 | No candidates / No samples / Acceptance limits not set |

错误表的全部Code逐项登记资源，OCV用“参考不可用，请检查参考版本／參考不可用，請檢查參考版本／Reference unavailable. Check its version”；RUNTIME用“服务已停止接收，请查询原任务／服務已停止接收，請查詢原工作／Service closed to new requests. Check the original task”；TIMEOUT/CANCEL使用StopDeadline/StopCancel并附Draining；INTERNAL沿ENGINE恢复文字。Raw score meaning中的官方后端标识作为证据值显示，旁边用EngineNative/CalibratedForProfile/None解释性质；不将未校准分数显示为概率。

键盘：图像Ctrl+0/Ctrl+1，表上下/Home/End/PageUp/PageDown，Enter选择原行，Space展开候选，Esc关闭Flyout；Tab沿§10.3唯一顺序，不拦宿主全局快捷键，快捷键执行同事件权限检查。取消/新识读/保存/查询/选择建议均SimpleButton常驻或精确禁用，不隐藏关键恢复命令。AutomationId为`Ocr.Image/Ocr.Regions/Ocr.Details/Ocr.Cancel/Ocr.Retry/Ocr.Export/Ocr.QuerySave/Ocr.SelectSuggestion`，Name/HelpText对应Catalog；UIA live通知只发生实际state或错误改变，限频并保最终状态，权限撤销立即封本控件命令。W UI资格按真STA测试，BCL catalog/PNG格式检查不冒称WPF已通过。

### 10.5 可选viewport WPF装配：Assembly v0.2窄消费

本控件没有直接viewport API依赖，`ImageContent`仍任意已装配只读影像UI。只有本指导规划的实际viewport Host才消费[viewport 0.3.5-prep §10.6～10.9](../viewport/DEVELOPMENT-GUIDE.md#106-公开bindingunbind与presenter借用)；PNG-only Host不适用该桥。此处只冻结显示组合，不重做§4.4原Root/Close，不给OCR图像编辑/计量/ROI事实Owner。可选接线留Wpf.TestHost/Integration.TestHost，不使Core或OcrEvidenceControl强制引用viewport DLL。

真实Host创建本STA的ViewportControl与有限IViewportProcessRoot→`ViewportRendererFactory.Create(该control,该root,显式ViewportRendererOptions)`检查Value/Errors→将Value.Backend传`ViewportOptions.Backend`、将**该control.Presentation**传`ViewportOptions.Presentation`→`root.CreateFactory().Create(options)`取得session→ViewportUiResourceCatalog.Get当前语言并核PortResult.Succeeded/Value非null的完整资源→`control.BindAsync(session,root,new ViewportUiBindingOptions(bindingId,false,resources,UiCleanupBudget,Lifetime:Value.Lifetime,ExecutionBudget:明确UI预算),ct)`。Bind原Task登记后才等待，返回同binding，OCR的ImageContent设置为该control；禁止用另一个control、另一root、旧backend或自造PresentationReceipt跨绑定。生产只读Host policy=HalconRequired；只有独立离线工程用途可明确OfflineRasterOnly，不因失败静默降级。

显示输入从宿主已提供的完整Frame/版本/坐标域和viewport公开源端口取得，匹配当前OCR.FrameSha256、EngineEpoch/OperationId/Generation；将OcrRoi/Word四角映射为viewport SourcePolyline/Label overlay，图像source角色和validity保持原Owner，Title含该operation身份而非产品判定。无图像源/完整display payload/资源预算时只显示诊断与PNG，不调用未定义的`CreateViewport/ToSource` helper或假造成功。内置renderer的CPU来源必须由§10.5.1公开源工厂生产认可payload，不能只按布局自行实现marker；自有Backend/Lifetime的既有成套路径保持；OCR不猜payload object内字段、不反射SDK/native地址。只申请ViewportFeature.Navigation|Presentation，RoiEditing不申请；表选区域框沿§10.5.2按稳定键命令，指针选择仍沿原Roi端口，不存在Selection枚举标志；图像选框回宿主SelectedRoiId，修改ROI仍去原ROI编辑Owner再新请求。

本版具体接入用原image-frame已发布的level0 CPU源及viewport §15.2.2.1 ViewportImageFrameSourceFactory，不从PreviewPng虚构source。Host输入是该Owner的完整已发布FrameDescriptor/ImageSourceDescriptor、借用IFrameService、原ServiceEpoch/已登记read ConsumerId、IAuthorizationPort、可选IRoiPort、已冻结ViewportLimits/资源准入/执行与关闭预算；这些是真实消费者端口，均借用且由原runtime Root保持。核descriptor.SourceRevision映射OCR FrameSha256、Width/Height/Channel/bit/Convention/CoordinateRevision/Validity及原源Owner注册完全一致；Gray16显示Lut沿Preprocess范围，RGB/BGR的通道解释沿已发布源，缺一致映射不Attach。OCR不创建image-frame生产源或替其计算修订。options.ConsumerId为本Host稳定ID、AccessMode=ReadOnly、Frames/Coordinates用§10.5.1同工厂稳定实例、Authorization用上述原实例、MaxDisplayBytes/MaxInFlightTiles/Limits/OperationTimeout/DrainTimeout均显式、Backend/Presentation用同Control、Roi仅原IRoiPort存在时传；无Probe/Surface/IntentSink，不申请编辑/采样能力。图像Selection只在原IRoiPort能保真映射同RoiId时调用，否则保留区域表选择并明确禁图像拾取；RequestedFeatures没有Selection成员。

Context只有一项`SourceBinding(Primary,原ImageSourceDescriptor,null,原operation关联ID,原SourceTiming或null)`；Sources不混新旧Frame。Context.Authorization为本Source原Scope的只读授权快照、Version取viewport已批准ApiVersion、ContextRevision由本Host有限long单调登记、Language为该binding语言、InitialView=`ViewState.Fit2D(实际CanvasDip,实际DpiX,实际DpiY)`并显式Lut。每个ROI和Word各建一条`OverlayLayer`：LayerId是SHA256(canonical [epoch,operation,kind,RoiId,WordId或null])的StableObjectId，ZOrder固定ROI=0/word=1，Visible=true、ROI层Interactive=true（只读ID高亮不依赖IRoiPort），Word层Interactive=false（本版公开selection只有RoiId，不新增词选择事件）；SourceRevision取同descriptor。Payload=`OverlayPayload(SourcePolyline,同SourceId,同CoordinateRevision,原GeometryRevision,Geometry.Empty,四角加首点闭合Polyline,空LabelResourceKey,固定SelectionPriority)`；Frame四角按(source x,y)逐值映SourcePoint2D，GeometryRevision由Host本次冻结投影登记，不冒原ROI文档修订。原ROI geometry Owner若已有对应revision优先用其原值。标签只使用已注册viewport资源键，不将RawText塞LabelResourceKey；本版原读文字在OCR表显示。context完整后保原AttachAsync Task→核receipt.ContextRevision/Generation与Sources.Presented；切换operation用完整ViewportUpdate(BaseContextRevision,Replacement)及原Update Task，不只换overlay。授权失效/源不符先撤旧呈现和命令再显示错误，原帧仍可见时不贴新身份。选中变化按§10.5.2公开命令仅改本显示层高亮，不写ROI事实；原operation失效后的实际画面撤除沿§10.5.3空更新，不以本地置null冒清图。

实际Commit/Revoke由该control.Presentation直接转发同binding，原Commit/Acquire/Confirm/Revoke/Return Task从`binding.GetPresentations()`观察并留root，禁止async wrapper替代原Task身份或把SourceCall交“最新”binding。Present确认只沿viewport原可见观察流程，WPF属性赋值不证明VisibleConfirmed；另列同binding成功/无可见证据、撤权/晚到、重复同Task/跨Control拒绝断言。Language切换调用同binding.SetResourcesAsync完整Catalog快照并保原Task，不在OCR翻译viewport键。

Closing顺序：封OCR UI新命令/撤本地订阅，发同binding.UnbindAsync独立有限预算+None，保存原Unbind Task/UiUnbindReceipt；Detached或观察到期不等Drained。未归还Presenter/晚到Acquire仍由原viewport根持有，原Revoke后同ReturnId归还；OwnSession=false不关共享session，Host自己拥有的session在本binding真实Drained后另走原session/root关闭。OCR runtime同时按§9.6独立Cleanup/ConfirmRetention，两根不能用彼此Released推断自身Released；不在Unloaded/Window.Close裸Dispose借用Frame或MA运行时。旧Unknown未归还不重新Bind换Owner，恢复查询同binding原Task/lease/授权/代次。

双STA消费者明确A丝印工程证据（新attempt/建议权限由宿主注入）与B标签只读复核（CanRequestRetry/CanSelectSuggestion=false），各自Control/Dispatcher/绑定/源lease/root，允许借同源Owner不同lease。1920×1080内串行验证三语、图表键盘、同operationoverlay、资源/UIA、Unbind晚到Return；关闭B不DisposeA或共享服务。UI预算从实际client的`16·W·H`显示读回峰值加scene/native/旧代并存/metadata推导，执行前checked核完整Root/UI Profile；不是复用1MiB协议额度或编造生产容量。上游公开声明尚未实现，实际native/WPF/呈现读回仍是运行资格门。

#### 10.5.1 内置renderer的公开CPU源生产者（viewport 0.3.5）

唯一源适配消费位置为[viewport §15.2.2.1](../viewport/DEVELOPMENT-GUIDE.md#15221-公开cpu发布源生产者与预装配bc-u1)，可选Host单向引用`Asun.UI.Viewports.ImageFrame`程序集/同名namespace，不把它加到OCR Core或证据控件必需依赖。以下是上游公开签名的调用形状，不在OCR声明第二源接口：

```csharp
// IF=Asun.Modules.ImageFrame.Resources; VP=Asun.UI.Viewports;
// VPIF=Asun.UI.Viewports.ImageFrame; values come from this Host's frozen inputs.
VP.PortResult<VPIF.IViewportImageFrameSource> sourceResult =
    VPIF.ViewportImageFrameSourceFactory.Create(publishedFrameService, root,
        new VPIF.ViewportImageFrameSourceOptions(readConsumerId,
            maxBindings, maxRetainedMetadataBytes));
// Succeeded + Value != null required before creating the session.
VPIF.IViewportImageFrameSource sourcePorts = sourceResult.Value!;
VP.PortResult<string> registered = sourcePorts.Register(
    new VPIF.ViewportPublishedFrameBinding(displayBindingId,
        publishedFrame, imageDescriptor, ImmutableArray.Create(0), pixelSpace));
// After replacement/empty transition and all original borrows have returned:
VP.PortResult<string> removed = sourcePorts.Remove(displayBindingId);
```

实际IF.IFrameService与它的ServiceEpoch由原发布Owner提供，必须先登记readConsumerId/额度；本Host在原viewport根强持该借用、sourcePorts及完整登记表。Create在session之前只做有限校验，不Publish/Read/订阅/取得源service所有权。sourceResult/registered/removed逐项核Outcome/Value/Error，不能在失败结果上用Value!；上例Value!仅代表已完成前一行注释的成功分支。工厂绑定的source实例/epoch、同root、readConsumerId是本显示接入的固定身份；逐帧displayBindingId、Frame.Key/Revision、SourceId/SourceRevision/CoordinateRevision/DecodeRevision是另一组完整键，不以工厂身份覆盖每帧身份，也不每次换图Create新Frames。

`options.Frames=sourcePorts.Frames`、`options.Coordinates=sourcePorts.Coordinates`在session创建时固定；只接同PixelSpace的2D identity坐标，Frame.CoordinateReference精确等于pixelSpace。不为此路线重建坐标图；非identity来源沿原坐标Owner显式ICoordinatePort路径，不拿本工厂Coordinates冒标定。每次Register前发布Owner已确认原Publish Completed/Error=None/OperationResourcesReleased，输入为它原完整FrameDescriptor，Image描述与该源/域/布局逐项匹配；不由OCR从文件名/PreviewPng造Frame.Key或重做PublishCopy。首版单plane索引0、level0、CenterInteger、identity层映射：Gray8=UInt8×1、Gray16=UInt16×1、RGB8=UInt8×3 Interleaved，原Validity不扩成Full。OCR BGR24原帧若没有已发布的合法RGB8显示源，不能改标签冒RGB；由原源Owner提供显式换通道的派生源/谱系，或沿既有PNG显示，禁止工厂暗换bytes。多层/Planar/多allocation等超首版域为007，不自行构造opaque payload交内置renderer。

换图采用同sourcePorts：Register新完整binding→核Succeeded→第一次才Attach，此后完整Update→观察旧原Task/同ReturnId归还与旧scope工作退出→Remove旧displayBindingId→只有原发布Owner按自身所有权Retire旧Frame.Key。Register相同ID相同内容幂等；同ID异内容/查找键歧义016，新旧SourceId+CoordinateRevision的PixelSpace必须一致。Remove时即使源lease计数暂为0、仍被当前Context引用也拒015；原Read/未知operation/scope/lease未归还保Pending/Unknown和登记容量，不以移除表项代归还或退款。共享源只Remove本方登记，不Retire其它Host的Frame、不Dispose共享service。MaxBindings覆盖当前/替换/仍未知旧entry，MaxRetainedMetadataBytes计完整冻结metadata并纳既有Host/root预算，登记满先拒新、不驱逐未知；每次实际读/复制/旧代并存沿原资源限额，不把metadata额度当图像峰值。

#### 10.5.2 表行指定框的完整稳定对象键

现公开`RoiSelectionChanged/SelectedRoiId`仅带RoiId；因此表行即使包含WordId，也高亮**该行对应的区域框**，词框仍是只读观察叠加，不把WordId塞CandidateId或新增词选择功能。Host在本次完整Context冻结时保存`(OCR epoch,operation,generation,RoiId)→OverlayObjectRef`映射：Target.SourceId/SourceRevision/CoordinateRevision取同imageDescriptor、GeometryRevision取该ROI层冻结值、LayerId取本节已定义SHA256键，SourcePolyline的ObjectId必须等于LayerId。每ROI一条Visible/Interactive区域层；无框/未支持的行只选表格并清高亮，不虚构中心点或调用指针HitTest。

准确公开类型/成员见[viewport §4.5.1](../viewport/DEVELOPMENT-GUIDE.md#451-稳定对象id只读选择高亮与聚焦bc-u2)：`OverlayObjectRef(SourceId,string SourceRevision,CoordinateRevision,GeometryRevision,StableObjectId LayerId,StableObjectId ObjectId)`、`OverlayObjectSelectionRequest(OperationId,long ExpectedContextRevision,DisplayGeneration ExpectedGeneration,OverlayObjectRef? Target,bool FocusIfAvailable)`；调用唯一为：

```csharp
Task<VP.ViewportResult<VP.ViewportReceipt>> originalSelect = session.ApplyAsync(
    new VP.SelectOverlayObjectCommand(new VP.OverlayObjectSelectionRequest(
        selectionOperationId, currentContextRevision, currentDisplayGeneration,
        exactTargetOrNull, false)), ct);
```

这里的viewport expected generation取同session当前snapshot，不能用OCR.UiSnapshot.Generation替代；两套代次在Host原映射中关联。selectionOperationId在用户动作接纳前一次生成并保存完整请求，重复同动作/内容只观察同原Task；同ID异目标不重发。本轮用途是高亮，FocusIfAvailable=false保原视图，不新增聚焦；Target=null时同样false，清选择不清图。预检同OCR epoch/operation/用户代、源revision、当前viewport ContextRevision/Generation、Read授权、Navigation与目标Visible/Interactive；通过ID入口不需要IRoiPort，指针图像选框仍沿原IRoiPort，不扩大编辑权限。重叠同中心ROI A/B必须按指定B完整键高亮B，不能按行号/最近框/中心模拟点击。

调用前预约并保存Apply原Task/完整请求至同Host/root；接纳后仅采用成功Value.ObjectSelection.Target=原Target、ContextRevision=原expected revision、Generation=同Value.Generation且仍为当前原session代的回执，输出viewport代登记一次，Geometry/ContextRevision不因选择改写。实际高亮可见还必须核本次ObjectSelection.Presentation及同新代VisibleConfirmed；缺呈现/失败/Unknown只保表行与诊断，不声称影像已高亮。成功ObjectSelectionChanged事件带同OperationId/回执，Host按operation去回声，程序更新SelectedRoiId不再发一次用户命令；撤权/删除/旧源修订的Target=null只撤当前匹配映射。迟到旧selection原Task仍观察/收尾，不覆盖新OCR选择或换图，不能拿旧事件重新选择新版本对象；原呈现Revoke/Return由同binding原链完成，不另抢释。

#### 10.5.3 失效显示的空更新与后续换图

本控件没有新Clear事件/API。本小节仅落实前文“源/授权/operation不符先撤旧呈现”的Host显示失效分支；普通有效换图保持完整非空Update，清一条高亮用Target=null，卸载保持原Unbind/Close。需要撤掉整幅失效源时采用[viewport §4.7.1](../viewport/DEVELOPMENT-GUIDE.md#471-合法空更新真实清屏与同session继续呈现bc-u3)的既有Update，不能只设ImageContent/SelectedRoiId=null后宣称真实空画面：

此分支只适用于已成功Attach且仍接纳的原session；Created尚未Attach没有旧源可清，首次Attach失败/取消的session沿原失败收尾，不用空Update将它恢复为可复用实例，也不重新Attach。

```csharp
var emptyContext = new VP.ViewportContext(Array.Empty<VP.SourceBinding>(),
    Array.Empty<VP.OverlayLayer>(), currentAuthorization, currentLanguage,
    new VP.ApiVersion(0,1), checked(baseRevision+1), currentView with { Profile = null });
Task<VP.ViewportResult<VP.UpdateReceipt>> originalEmpty = session.UpdateAsync(
    new VP.ViewportUpdate(baseRevision, emptyContext), ct);
```

currentAuthorization/Language/View取同session当前已接受快照，撤权时保其原撤权快照，仅删source/layers，不顺便更新权利或做新读取；空replacement完整冻结并保存原Update Task/base/newRevision至同Host。接纳后旧交互/手势/选择封住，旧晚到只归还，原Presenter/backend Revoke→原Submit/Acquire/Confirm/Dispatcher/CPU scope退出→源lease同ReturnId实际Returned，不重复Return或Unbind同一资源。限额/单调总deadline与既有Control清理预算不重开；空scene只借显示基线/有界metadata，不能携原标题/像素/overlay/旧frame引用，源没有统计也不触发新LUT读取。

只有同空context/generation的EmptyTransition中PreviousPresentationsRevoked、PreviousSourceBorrowsReturned、PreviousWorkQuiesced全true，PreviousCleanup.State=CleanupState.Drained成立，且本WPF路径BlankPresentation.VisibleConfirmed=true，才确认旧画面已撤为空。PreviousWorkQuiesced只指旧有限内容scope，不等待本次Empty Task、整个session或长寿命binding worker，避免自等；Empty不代表共享源storage已释放或OCR原计算已排空。Return未确认、错误/取消/观察到期、空Presenter不可见都保原Task/entry/借用预算；只从原GetSnapshot().EmptyTransition有限观察晚到，拒新非空Update/Attach/selection/Retry绕过Unknown，不新建session/binding或重发新Clear。相同base/newRevision与完整replacement重复只取同原Task，冲突/旧base拒绝，不清后来新图。

同原空过渡最终确认后才Remove旧entry（还须工厂的Context使用/原读借用核对）；发布Owner自己的Retire另行确认，StorageReleased=false不否定本方Returned。后续同session调用完整`UpdateAsync(new ViewportUpdate(空ContextRevision,新完整Context),ct)`且新revision=空revision+1，新source先Register，新Read授权/源/预算重新校验；不再次Attach或Bind。安全清图不停止OCR engine，不改变原读/保存Unknown，也不关闭另一个STA或共享服务。

#### 10.5.4 本轮有限反例与文档自审

原W.04验收追加三组消费断言：A/B同源不同root/ConsumerId与逐帧完整key，Register换图始终同Frames/Coordinates，错epoch/Key/源域/BGR标签/metadata超限拒绝，Context活跃/late read/Return Unknown时Remove拒绝并留账；重叠区域A/B以完整键选B，无IRoiPort仍可只读ID高亮，旧Context/代/源/权限拒绝且无读取，Target=null清选择，重复同Task仅一次事件，UI无本次VisibleConfirmed不说高亮；空更新旧Revoke迟到、source Return未知、空画面无真实确认均不确认撤除/不读新帧，原快照晚到三项完成加Blank可见后才Empty，原同session恢复Update而非Attach。它们是已有W/I Host的可判定反例，不是本轮执行过的WPF/源运行证据。

本原会话定向自审仅回读viewport 0.3.5 §20.5所定位的§15.2.2.1/4.5.1/4.7.1公开声明及本方接线：工厂身份与Frame键分离、Stable Frames冻结、SourcePolyline.ObjectId=LayerId、现RoiId选择边界、原Task/lease/双代/资源、空过渡与Unknown恢复闭合；其它算法/三语/v0.2 Lifetime/Presentation/Root/Close/有效向量与历史接收复用。完整批准范围的软件设计闭合结论保持（§16.4）；真实实现/运行门不提升。

## 11. 正常、边界和失败案例

场景统一用§3 DTO；运行状态、item质量、保存事务分开。下表可直接转为§12的断言，不是已执行结果。

| 输入/触发 | 顺序与结果 | 恢复/禁止 |
|---|---|---|
| 有效单词ROI/模型 | Accepted→Acquiring→QualityChecking→Recognizing→Ordering→ObservationChecking→Drained→ResourcesReleased→Completed；item Read | 宿主独立比较；不写产品PASS |
| Detection有效词框 | Detecting→Ordering，不发Recognizing；item Detected、RawText=null | 交宿主关联；无框Empty不推断目标不存在 |
| 空ROI集合 | Rejected/INPUT-001，无lease/native | 修请求；不当合法空文字 |
| 3ROI分别可读、低信、无字 | 恰3item：Read/ReviewRequired/Empty；运行Completed、分母3 | 宿主复核；不汇总为1/1 |
| O/0、I/1混淆 | 保留winner和字符top-N，非恒等mapping独立来源 | 不按期待串改原读 |
| 缺笔但OCR读对 | OCR可Read，单独OCV Computed并保留Quality | 宿主字形质量判定；不以读对取消缺陷 |
| 重叠词、不可证明行序 | 全部词/关系、Ambiguous | 修定位或复核；不删不合期待的候选 |
| 越界/非凸支持/非法surrogate/stride溢出 | 接纳前稳定输入错误 | 不clip/补字/继续native |
| 模型文件缺失/hash错 | 接纳后Acquiring失败，清租约、Failed/ASSET-001 | 修闭包新请求，不用latest |
| deadline到而native未退出 | StopReason=Deadline、Draining/Quarantined、Wait BudgetElapsed；资源继续占用 | 原IDQuery；排空后TimedOut，之前不free/reuse |
| 已完成后迟到cancel | CancelAccepted=false、原终态不变 | 不回写Cancelled |
| 同key/hash、不同OperationId | Existing返回原operation，无第二worker | Host使用receipt的原ID |
| 同key异hash/同OperationId异key | IDEMPOTENCY-002/001、Rejected | 不覆盖登记 |
| 新epoch查询旧ID | Unknown、Snapshot=null | 宿主持久回执查询，不自动重跑 |
| 保存/MES失败或未知 | 提交知识/排空分别查询、OCR响应不变 | Unknown只查原意图；仅权威确认未提交且排空才显式新尝试，不重跑OCR |

## 11A. 两轮怀疑式内容自审与反例

### 11A.1 第一轮：成像、算法与结果保真

| 反例/输入 | 参数来源与处理 | 明确输出/验收 |
|---|---|---|
| 一字ROI提交TextModelAuto | 方法选择来自Profile；预检只能校结构，适配器见行少于2字时拒识，不静默用另一模型 | Rejected/ReviewRequired+QUALITY-002；单字必须SegmentedCharacters或资格Deep；不是空字 |
| TextModel拒识但second-best像期待值 | 带rank0读取class，保留拒识；期待不在request | 原拒识标记和候选保留、item Rejected；不能class无rank伪Read |
| Deep检测图有框，但未做识别 | Mode=Detection，读取框/score坐标域，不能解析不存在word | Detected/null RawText，无Recognizing事件 |
| 字符候选含Blank U+2800 | 位次保留，word不含Blank；unicode scalar和位置索引分开 | Blank不当空格，不组合字符top-N为词top-N |
| CTC序列A,A,Blank,A | 固定外部decoder先在时间序列去相邻重复，再删blank | 输出AA；先删Blank再去重所得A为失败反例，仅适用于CTC外部adapter，非HALCON内部重实现 |
| Gray16窄动态范围/亮字/反光 | Gray16范围/舍入、反相、阈值来自Profile；仅许可转换并记录谱系 | 禁止逐帧拉伸至“读对”；未观察支持/粘连/断字为ReviewRequired |
| 90°/180°/镜像输入 | DirectionDeg显式，text_line_orientation不判180°或镜像；alignment需模型真实资格 | 宿主资格域不符则不提交；已提交的明确拒识/字符域外为ReviewRequired，不声称高softmax可识别所有物理OOD；不偷偷多角度搜索或拼接结果 |
| 预处理词框当原图框 | trace中FrameToImage与ImageToFrame，分别保存算子输入域、预处理域、score-map域 | 输出4角均Frame坐标、同一ROI关系可回放；域不明RESULT-001 |
| OCV Threshold=-10但模式ErrorPixelRatio | Profile符号/模式预检拒绝；AdaptAngle=true也拒绝 | METHOD-001，不调用native；Quality=1/0含义不颠倒、不与OCRconfidence共门 |
| 重叠tile截断一个字但模型高分 | 有效支持检查优先，保留重复词关系 | ReviewRequired，不能高分抵消支持缺失 |
| 推荐候选只统计成功样本 | 每候选×样本完整Trial，超时/未排空/失败不可移除 | 无winner或NoEligibleCandidate；缺Limits为NotEvaluated |

2026-10-10定向第一轮反例：HALCON factory不能将Capabilities.alignment=true当具体模型alignment可用；原生模型加载后参数read-back失败，仍须清理已取得对象才fault完成，清理未确认必须保持Pending，不能抛异常后放Frame。工厂构造不加载模型、Create只交付空worker，完整资源装配及回滚在§8.1，同步§9 Host和H.03断言。

本轮修订落点为§2算法、§3输出/推荐/trace；训练和格式纠正分开，不把上游procedure/营销或模型存在当生产证据。

### 11A.2 第二轮：外部接入、并发、资源与恢复

| 反例/输入 | 处理/恢复 | 验收断言 |
|---|---|---|
| 两线程同时同key提交 | 登记与容量reserve同一临界区；后端尚未起也返回Existing | Accepted恰一次、Retain/Create恰一次，snapshot原ID稳定 |
| Wait取消、计算仍运行 | ObserverCancelled只停止等待；Frame、asset、worker仍属于operation | StopReason不变，取消观察不发CancelRequested，不use-after-free |
| deadline前native输出完但证据复制/释放未完 | deadline仍覆盖整个operation；StopReason在锁内冻结、释放完成才Terminal | TimedOut可以带完整部分观察，不能抢发Completed；E2E含排空 |
| acquire在cancel后迟到成功lease | 继续接管lease、跳过native、串行Dispose | 资源归还后Cancelled；不丢后台Task、不重新启动native |
| worker Dispose抛错或不返回 | 保留同一释放任务/资源账目、Quarantined；StopAndDrain Pending | 不发布终态、不腾额度、不再次并行Dispose；宿主维护 |
| sink拒收/抛错 | 锁外非阻塞TryPublish；记录DIAG-001，Query恢复投影 | 原读/Evidence hash不变，不递归写失败sink、诊断有界 |
| engine的证据/登记上限耗尽 | 不驱逐未确认/终态幂等事实，拒绝新请求，宿主排空归档后新epoch | 无内存无限增长、旧key不悄悄再执行 |
| 旧operation UI callback/权限变化 | Generation+epoch+ID+Sequence校验，执行处再核Can* | 不把旧原读/候选更新新图，不因按钮刚启用就越权 |
| View中Completed但item ReviewRequired | 运行/观察/保存三栏 | 不显示统一“合格”；OCV/期待/MES各由宿主定义 |
| evidence observation.json带EvidenceRef | 观察投影排除自身引用，descriptor只含blob身份/长 | hash不递归，无随机运行时间；改原读/像素必改内容hash |
| 保存写到一半重启/异常回调 | 原Intent/Attempt/hash查询；OCR和保存排空分别证明 | 半写/NotFound/回调异常不证明未提交；Unknown不新Submit，原读不变 |
| 无UIHost退出时await using挂起 | 显式有界StopAndDrain；Pending由runtime继续管理，Dispose拒绝未排空 | harness有限截止非零；不让UI关闭dispose输入 |

2026-10-10定向第二轮反例：存储已经Committed但通知callback抛错，SaveState=Failed仍不能新Submit；Unknown查询NotFound即使OCR已ResourcesReleased仍不能新保存；ConfirmedNotCommitted但存储资源Pending只能查原意图。只有最终未提交+资源Released且显式用户动作才分配新AttemptId。工厂Create成功后宿主初始化失败，若尚未Submit只回滚自己新建依赖；提交后任何Pending必须保留engine依赖，不从finally销毁。上述规则已同步§8.1/9/10/11B.5/12。

本轮修订落点为§3.2摘要、§4并发/关闭、§7/8迟到资源、§9回执示例、§10代次命令。自审确认外部绑定只通过公共DTO/端口；没有宿主数据库表、产品ViewModel、全局主题、SDK句柄或制程判定依赖。

### 11A.3 明确支持范围与版本扩展

本版支持HALCON Deep detection/recognition/auto、传统MLP分割/TextModel、OCV、ROI提案/有限参数评价、无UI与可选证据UI。**不支持**无界多行/曲线文字拼装、跨tile补字/融合、期待纠错、在线训练、强杀native后原实例复用、任意pixel容器/投影输入、外部未批准Python嵌入。功能拓展需新版本契约和相同失败/资源验收，不能一个布尔开关隐式开通。

### 11A.4 2026-10-11 两轮有限内容自审（仅新增C2/C2-R）

第一轮按实现者正常→异常→恢复检查：

| 路径反例 | 已同步的可执行决定 |
|---|---|
| Factory先启动、才发现进程root槽满 | §4.4 Reserve先于source/factory/dispatch；失败零port调用，root/tasks/字节有界；§9.3/9.4顺序一致 |
| Frame/asset acquire或factory调用观察已到期，原Task晚到对象 | 原dispatch/Task/continuation强持，晚到对象登记后反序清理；slot未Released不复用容量，ConfirmRetention后才离栈 |
| 消费回调抛异常，同时worker或source释放FailOnce | stage明确、PrimaryFailure保持HostConsumerFailed；清理错误在CleanupFailures，独立None token；Recover只显式重试幂等Dispose不重跑读取 |
| native/协议Compute未返回而cleanup观察结束 | Quarantined/原任务仍持输入；一个cleanup Task继续，恢复只观察，不能循环Dispose或把HostOutcome.TimedOut当计算终态 |
| 所有native已释放，但最终evidence仍留root Query | HeldBytes=0和RetainedResultBytes分账；Released不把保留结果内存当0，仍受已reserve证据/root限额 |
| 推荐judge抛错/资源峰值缺观测/某case取消 | run止新case、只取消自己的operation、原Task排空再终态；缺分母/未观测不造Trial/P95/峰值或返回旧winner |
| 推荐run完成占满登记后重复Start原Plan | 先查RunId/Plan，再核首次接纳的剩余额度；Existing不重Submit、不重判容量；fixture fingerprint覆盖实际request/资产与评价版本 |

第二轮按外部消费者从空Host沿公开签名检查：

| 路径反例 | 已同步的契约定位 |
|---|---|
| 无UI主进程没有factory/source/asset/时钟实例 | §9.1准确构造/port，§9.2所有Frame/资产/预算/Model/Deep/Profile字段，§9.3/9.4从Reserve起两个Host；协议不产人工RawText |
| 原构造未返回ticket，异常出口找不到Owner | root Reserve先登记HostId，FindHost返回原ticket；§9.4构造catch保留主错、cleanup双轴、0预算回执和handoff，不创建替代槽 |
| 标签Host错用新epoch查询旧operation | §4.4 QueryOperation/QueryOperationResources原ticket+EngineEpoch+ID，不匹配Unknown，原槽强持/墓碑不重Submit |
| “推荐执行以后接上”缺方法/操作身份 | §9.7 Start/Query/Wait/Cancel、完整PlanHash/Case/TrialJudge/Run snapshot、双sample×双候选fixture；C2-R同工程，C3纯值接收不扩大 |
| H/W只有抽象源或占位TextBlock | §9.6 OcrBorrowedHostSources完整构造/lifetimeLease，H原公开factory准确根槽注入；W真实OcrEvidenceControl+影像槽/PNG证据，STA/Closing接管，真实资格不冒Fake |

此轮没有重查HALCON算子/语言/原读/OCV质量规则、没有重写已接收C1/C3或§8.1H/保存Unknown结论。上述软件可决定构造/资源/退出欠账已正文闭合；真实外部lifetimeLease/Frame/asset/存储/视口实例映射按H/W/I各自交接，真实运行通过不能由本表代替。

## 11B. DZ-XVision 来源场景的唯一接入映射

来源快照只读，.NET Framework 4.7.2 WinForms/旧依赖不成为平台限制。本节保留稳定区域、定位谱系、有限恢复和事务隔离经验，不复刻旧工具/料号/MES/UI。

### 11B.1 稳定区域与配置增删改

宿主把来源RegionId映射为唯一RoiId，给出ROI/顺序/Profile/版本，Validate后Submit。新增/删除/重排只改变新请求hash，不左移历史响应；核心不提供产品配置编辑或差异数据库。验收：删第2区后新请求只有第1/3区，历史仍3item，ID绑定不变；重复ID为INPUT-001。

### 11B.2 定位来源、坐标变换与预处理

外部SModel/NModel类定位结果由宿主拥有。宿主完成产品目标→本次Frame ROI变换或提交已派生Frame，并在自己的证据链登记父图/位姿；模块只对当前Frame执行§3.6仿射裁剪/旋转/缩放trace，不读取产品定位类型。定位失败宿主不得提交伪ROI；模块发现支持/坐标域非法为INPUT-003。验收：输出框只属于Request.Image.CoordinateRef，宿主能沿自己的父链回原产品图；模块trace可逆，补边不扩支持。投影/标定资产不塞入OCR DTO。

### 11B.3 按错误类别的有限attempt

宿主根据获批重试Profile（次数/剩余时长/资源/批准路线）分类错误；Retryable只是建议。瞬时故障排空后创建新OperationId/IdempotencyKey，保留前次请求/hash/错误与response；attempt ID/链由宿主拥有，不是核心隐藏重试。低信、期待不符、遮挡、配置错误不自动循环。验收：native未停时旧worker绝不复用；提交重复key不会启动第二attempt；内容不一致不能靠重试覆盖历史。

### 11B.4 原图、派生图与结构化结果

模块生成完整内存OcrEvidence（Frame、derived、trace、observation），ResourcesReleased后响应仍可读取；宿主把这些blob和operation元数据写受控证据仓，选择JSON/存储Schema。EvidenceRef不等于保存成功，存储失败只改变宿主SaveState。验收：每blob核hash、派生图父链/矩阵可回放；宿主保存失败后同一response原读/hash不变，不重新执行OCR。

### 11B.5 原子保存、半写恢复与重启

临时文件/刷新/原子提交/数据库事务/提交标记和扫描恢复完全由宿主存储Owner实施。本模块没有存储路径/保存/跨重启journal端口；§10的EvidenceSaveProjection只投影宿主权威回执，不新定义存储事务。宿主保存意图绑定IntentId、AttemptId、原OperationId、EvidenceRef/content hash和目标；开始提交前持久登记该身份并防重放。回执必须匹配原身份/目标/内容，异常监听者、回调抛错、超时/取消或新epoch的OCR Unknown都不改变它。

| 权威提交知识 | 保存资源 | Host/控件动作 | 禁止 |
|---|---|---|---|
| NotSubmitted | Released | 仅原意图明确尚未调用存储提交时，可显式开始首次保存 | 把调用后异常/NotFound改成NotSubmitted |
| Committed | Released | 以匹配的ReceiptRef显示Saved；无需再次提交 | 为通知丢失生成新保存 |
| Committed | Pending/Unknown | 显示已提交/等待释放，查原意图资源回执 | 重复提交或释放仍在使用的buffer |
| Unknown | 任意状态 | 保留原IntentId/AttemptId/hash，只有限Query原存储Owner；到预算仍Unknown | 重发原Submit、换key试探、另建意图、覆盖旧记录 |
| ConfirmedNotCommitted | Pending/Unknown | 仅查询/等待原资源排空 | 因未提交就提前重用buffer/开启新尝试 |
| ConfirmedNotCommitted | Released | 宿主明确用户动作+权限核查后，为同一意图分配新AttemptId，保留原尝试和未提交/排空证明 | 自动循环重试、改证据/目标后沿用原意图 |

只有存储Owner的权威最终回执（其提交窗口已封闭，迟到旧尝试不能再提交）才能给ConfirmedNotCommitted；NotFound、查询失败、异常回调、文件暂不可见或应用自己的取消完成都不足。QueryState=NotFound/Failed时保留原CommitKnowledge（原Unknown仍Unknown），Resources独立按资源Owner回执更新；不能根据“本地任务结束”推断远端事务未提交。保存资源Released与OCR.ResourcesReleased是两笔账：OCR终态不会自动证明存储worker/IPC/远端提交已排空。查询同样有有限等待预算，超时不重发提交；卸载UI后宿主runtime继续持有存储意图/查询/资源。

EvidenceSaveState Failed表示执行/通知失败的展示标签，**不提供重试授权**；若失败时知识未知，显示Unknown并原意图Query，若已有Committed不回写未提交；Saved只映射Committed+Released+匹配ReceiptRef。NotRequested时Save可null；宿主预建Save投影后NotSubmitted+Released才允许首次export。SaveErrorKey只用于说明原因，不能取代知识/资源字段。QuerySaveRequested从旧代次到达时拒绝；有效命令只查询该Intent/Attempt，不取控件当前选择重拼身份。

重启恢复查询原持久回执：半写JSON不是完整response，不表明未提交；匹配已提交回执恢复原事实；未确认继续Unknown；权威未提交并排空才显式新尝试。测试属于I/W门，纯Core不假称原子磁盘/远端提交行为通过。OCR原读/Quality/evidence始终不因保存恢复而变化。

### 11B.6 冻结观察与外部事务隔离

OCR/OCV终态→宿主保存→期待比较/OCV质量解释/人工复判→外部报告/MES/设备事务，各自Owner和状态独立。后续期待变化只重建宿主比较；事务失败先核提交知识/排空；Unknown只查询原receipt，确认未提交且排空才显式新尝试，不改原读/Quality/证据。验收：无MES/产品对象可回放识读，两个消费者有不同质量解释仍能使用同一响应。

## 12. 可执行验证与验收矩阵

本轮只修文档，没有运行以下产品验证。目标不是测试数量，而是以下行为可判定；用例编号为唯一测试入口的断言consumer，不新增报告或脚本。

### 12.1 BCL Exe 与有限命令

Core工程 `Microsoft.NET.Sdk/net10.0` 类库；Core.Tests为 `Microsoft.NET.Sdk/net10.0/OutputType=Exe`、只ProjectReference受测Core与BCL，不新增NuGet测试包。遵循[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)。入口按 `--slice C1|C2|C2R|C3|all` 执行已实现切片的全部必要用例，未知slice或尚未交付slice非零；all有未交付必需项则非零，不能跳过后报通过。固定TimeProvider/可控制异步闩锁/明确释放门；无UIHost放同一Exe。任一断言失败、未完成、必须项被跳过都非零并列用例ID；不使用 `dotnet test` 的空执行。

未来获准实现时逐条执行，命令不得串成成功掩盖失败；本轮不执行：

```powershell
dotnet build src/Modules/ocr/Asun.Modules.Ocr.Core/Asun.Modules.Ocr.Core.csproj -c Release
dotnet run --project tests/Modules/ocr/Asun.Modules.Ocr.Core.Tests/Asun.Modules.Ocr.Core.Tests.csproj -c Release -- --slice C1
```

C2/C2R/C3把最后参数替换为对应slice；全Core交付后才用all。harness单例异步测试墙钟上限10秒、整次120秒，内部固定虚拟时间精确推进；这些是防挂的验证预算，不是产品性能目标。外层每个build/run进程上限300秒：执行者用带RedirectStandardOutput/RedirectStandardError的ProcessStartInfo（shell-free ArgumentList、WorkingDirectory=仓库根（由执行者定位，以含PROJECT_ENTRY.md的目录为准）），启动后并发ReadToEndAsync两流，WaitForExitAsync与300秒CancellationToken；到期Kill(entireProcessTree:true)并返回非零/Timeout，不能成功退出或默默漏用例。不写额外脚本，复用执行器提供的有限进程超时也可；PTY返回session并不自动满足截止，必须检查最终exit code。

### 12.2 逐切片断言

| ID/切片 | 输入/方法 | 必须观察的断言 |
|---|---|---|
| OCR.C1.01 正常 | Gray8小帧、完整资产身份、单凸支持ROI、有效Profile | Validate真、Request/Method hash稳定64hex；不调用provider/native |
| OCR.C1.02 空/非法 | null、空ROI、重复RoiId、NaN/Infinity、非法enum/surrogate、负尺寸/预算、stride溢出 | 各稳定错误、IsValid=false；hash入口抛ArgumentException，无空hash |
| OCR.C1.03 像素/几何 | padding/Gray16、旋转四角越界、支持在bbox内但ROI外 | 精确length与checked上限；非法拒绝，不clip；Geometry计算仅合同局部公式，不复制公共ROI编辑/变换能力 |
| OCR.C1.04 hash | 改OperationId/key；改阈值/字表顺序/ROI/blank；Files/AllowedScalars顺序变换 | 身份排除不改hash；语义变更必改；已声明无序字段排序后不改；有序Rois/字表变化必改 |
| OCR.C1.05 并发/版本 | 同一Contract实例多线程、多次深复制后改原List | 无共享可变状态、输出不污染；契约0.2 discriminator与未知版本不能当兼容 |
| OCR.C1.06 生命周期适用性 | 纯值计算无IO/native/窗口 | 没有假Cancel/Drain事件；取消/超时/关闭native不适用于C1，用harness外层截止保证终止 |
| OCR.C2.01 正常/部分 | fake一次读3ROI：Read/ReviewRequired/Empty | 一次接纳、3item、Completed不等于全Read；准确资源计数、零lease后Terminal |
| OCR.C2.02 幂等/并发 | 受控锁同时同key/hash、同key异hash、同ID异key | Accepted一次、Retain/Create一次；Existing原ID；冲突Rejected且不侵占额度 |
| OCR.C2.03 Wait/取消 | waitBudget=0/正有限/observer取消、随后显式RequestCancel | BudgetElapsed/ObserverCancelled不改变执行；显式取消才StopReason.Cancel；排空前无Terminal |
| OCR.C2.04 deadline/迟到 | 固定钟过deadline，fakeRead挂起，之后成功返回 | Quarantined资源计费、不复用；释放后TimedOut，迟到事件不污染新ID |
| OCR.C2.05 acquire/dispose | resolver或Frame迟到成功、worker Dispose失败/挂起 | 晚到lease接管、无native新执行；Pending保留账、未确认释放无Terminal；无二次并行Dispose |
| OCR.C2.06 关闭 | 活动/排队请求、StopAndDrain预算到/重复关闭/observer取消 | 禁止新接纳、Shutdown→Cancelled仅释放后；Pending可再查，未排空Dispose抛错，Drained后幂等Dispose |
| OCR.C2.07 证据/sink | hash自引用反例、源Memory复用、sink false/throw、预算满 | 证据无自引用、原Memory变更不污染；DIAG不改hash；受控额度拒绝无无限增长 |
| OCR.C2.08 版本/重启 | 换asset/profile、停止旧epoch、新engine查原ID | 旧operation完整不改；新hash/新worker；新epoch Unknown，不重跑 |
| OCR.C2.09 模式/结构 | fakeDetection词框、OCV Quality=0/1、字典缺键/NaN/ROI漏项 | Detection无RawText/Recognizing，Auto仅真实组合阶段；OCV语义独立；结构异常Failed非Empty，无无依据top-N |
| OCR.C2.10 根槽/容量 | root空Host，Reserve满slots/tasks/bytes、未知ticket、clock错实例 | Factory/Create/port调用均0；失败不清未知槽；真实task先reserve/登记后调度 |
| OCR.C2.11 原Task/迟到 | frame/asset/factory Hold IgnoreCancellation，cancel/deadline后晚到 | 原Task.AsTask一次、迟到对象被接管/清理；借用/源强持，Compute不重入、同epoch/ID Query |
| OCR.C2.12 独立cleanup | 主回调抛异常+observer取消/Wait到期 | 保留PrimaryFailure；cleanup None独立预算、原Task继续，finally异常只清理轴 |
| OCR.C2.13 有限恢复 | Worker/Frame/Asset/Source release FailOnce/Fail、重复Cleanup/Recover | Pending不重复Dispose；completed fault只有显式Recover有限尝试、次数耗尽Unknown；不再Read/Create/Acquire |
| OCR.C2.14 接管/离栈 | 方法/窗口返回、ConfirmRetention未知/原槽、构造失败尚无return ticket | Retained/Released才离栈；FindHost找原槽；SourceRejected无调用、原上游Owner持借用，不遗失资源 |
| OCR.C2.15 双Host | §9.3丝印empty+消费异常、§9.4标签late Create/Compute | 完整BCL构造无需HALCON/WPF；Empty不伪读、未释放Root.Dispose拒绝，原Source原factory同槽 |
| OCR.C2.16 结果/资源分账 | terminal后dispose engine/source、root Query墓碑、容量峰值 | 原epoch/operation可查；HeldBytes归0、RetainedResultBytes真实保留计入额度，Declared不充Observed |
| OCR.C2.17 shutdown/版本 | reserve空槽Cleanup、先dispose root、new engine查旧ID/错epoch | 空槽无native可Released，pending root不销毁；原epoch Unknown不重做事实；C1 hash保持 |
| OCR.C2R.01 Plan/幂等 | 双sample×双candidate完整/缺组合/重复key、登记满后重用原RunId/Plan、修改fixture像素/方法/评价Limits | Start只受控一次、PlanHash全字段、同Run/Plan仍Existing，冲突拒绝；改变输入闭包必改fingerprint；不隐含自动候选/训练 |
| OCR.C2R.02 原读与评价 | 协议4Empty、judge异常、Observed峰值缺失 | 拒识分母完整；没有伪Read/概率，缺测量不填预算为峰值，失败不返回Suggested |
| OCR.C2R.03 总deadline/取消 | 当前case Hold、run Wait observer取消、RequestCancel后晚到 | Wait不取消计算；run只停本runcases、原lease强持、全接纳operationReleased前Draining非终态 |
| OCR.C2R.04 异常/恢复 | rootCleanup+runner异常、旧epoch/RunId查询 | 业务/清理双轴，有限恢复只释原资源、不新Start，C3纯值Evaluate独立；原任务/NotAttempted分母保留 |
| OCR.C3.01 ROI候选 | 矩形四角、0/正margin、边界/支持/重叠/MaxCandidates | 稳定枚举、扩边不clip、拒绝原因/限制可判定，不跨Frame |
| OCR.C3.02 评价 | 等分候选、完整/缺Trial/失败/未排空、Limits null | 固定tie order；缺分母无winner；null NotEvaluated；false accept不可平均掉 |
| OCR.C3.03 stale/副作用 | 改dataset/profile/ROI/资产fingerprint、并发评价 | 纯值返回原fingerprint，宿主据其另做stale核对；无执行Host/训练/文件/active Apply，结果deep immutable |
| OCR.C3.04 生命周期适用性 | 纯值Propose/Evaluate无IO/native | 无fake Cancel/Drain；函数返回或结构错误异常，harness有限截止；实际离线执行软件属C2-R、真实接线属I |
| OCR.H.01 HALCON | 真实单字/多字、三语、反光/粘连/断字、Gray16/亮字/方向 | 固定Golden/模型/runtime，拒识不second-best，原读/支持/分数语义符合§2；Mock不算通过 |
| OCR.H.02 Deep/OCV | input/预处理/score-map三域、Blank/mapping、tile、Threshold正负/AdaptAngle | 坐标trace可逆、未校准不概率、质量方向正确、native非恒等原读拒绝、post-read映射独立保留；真实native取消/释放需实测 |
| OCR.H.03 装配/回滚 | §8.1 options/单factory/空worker、加载中途失败/取消/释放未知 | 构造无native，IOcrAdapterFactory唯一注入；rollback只释本次资源；未确认不完成/不free；共享runtime依赖不被误Dispose |
| OCR.H.04 codec/固定参数 | 三描述blob完整canonical；BOM/重复/未知/缺键/深度9/非法UTF-8/NaN/超bytes；所有Manual bool组合 | Decode坏值Recipe=null且错误有限；Encode往返原bytes不变；组合校验在worker；Manual逐项使用§8.2准确名字，dot spacing的被忽略项如实记录，基线0.15不变15；无生产默认 |
| OCR.H.05 像素/几何 | padding的Gray8、little-endian Gray16、RGB/BGR；0°/±90°/非整数尺寸/Direction；边界缺四邻 | 完整Frame hash先核；逐行去padding/通道正确，原支持不足拒绝；双矩阵往返在64×2^-52×max(1,坐标绝对值)结构误差内，不拿该误差放宽物理域；HALCON仅get dimensions而set image_size；默认裁图不凭padding补支持 |
| OCR.H.06 资产桥/双根 | 两Host各借相同MA服务不同lease；错closure/layout/hash、过期许可、materialize失败、晚到/未知Release、累计容量满 | 精确Resolve及原ProjectAcquire父摘要；全graph hold，生产前重核permit，旧native不抢释；未知两根留原Task、原ResourceId及字节账；关闭B不关A/共享服务；安全能力缺失拒绝，无本地临时文件备用 |
| OCR.H.07 挑战/双fresh read | 同真值计划：容差内/外、symbol/Blank/拒识/score意义篡改、缺case、取消、未尝试、原Materialization借用 | 完整分母；容差内Passed允许观察digest不同；容差外/已知不符Failed，缺证据Unknown；无native句柄共享，新operation全部Released后才完成；原物化借用不抢释，不递归VerifyFormat，不新ID重跑Unknown |
| OCR.H.08 完整能力/反例 | 单字、≥2字Auto/≥3字Manual、多行/多区域、符号表、复杂背景/反光/断字/点阵/倾斜/粘连/越字符域/空帧/多阈值候选、独立OCV | 各固定资格Golden保存字串/ROI数/顺序/拒识/支持/候选/OCV数值与容差；多区间/重叠保Ambiguous，不期待择优；Manual增强图有父谱系；高softmax OOD误接受必须报告，不能宣称保证检出；native clear无法确认时原Read不完成、Recover不重发未知clear |
| OCR.W.01 UI | 固定1920×1080，三语，权限/旧代次/Flyout/键盘/UIA/关闭 | 图表双向联动、可见主命令、无越权/旧结果/静默Apply；关闭不dispose native |
| OCR.W.02 保存命令 | Unknown/Committed+Pending/ConfirmedNotCommitted+Released、旧代次/异常监听 | Unknown仅QuerySaveRequested原身份；未提交且排空+权限+显式动作才新尝试；NotFound不开放export |
| OCR.W.03 资源/PNG/交互 | Catalog三语全部RequiredKeys及扩展语言；缺键/超限；错FramePNG/解码超像素；Empty无词/重叠/RTL/控制字符；固定1920×1080 | 完整三语不泄key/PascalCase；扩展完整快照切换不改View/原状态；只读PropertyGrid、表保分母；PNG原身份与完整预算、fit/zoom/pan同矩阵；ImageContent存在不叠手势；Tab/Enter/Esc/UIA与英文长度实测，无缺键假通过 |
| OCR.W.04 同viewport绑定/归还 | §10.5 A丝印工程/B标签只读双STA；错Control/root/Frame/授权/旧generation；晚到Presenter/Unbind | 同Control.Backend/Presentation/Lifetime及完整Context；VisibleConfirmed只取实际present/readback证据；无Roi port不调编辑/指针图像Selection，表行ID高亮仍可用；Get资源先核PortResult；原Commit/Revoke/Return/Unbind Task留同根，B关闭不影响A，两根独立Released，旧Unknown不新Bind逃账 |
| OCR.I.01 接入 | 丝印+标签独立Host、存储失败/半写/重启/期待改变 | §15同API、不同Owner，原读/hash不变；宿主事务独立恢复 |
| OCR.I.02 保存恢复 | 提交后callback抛错、Query NotFound/失败、OCR已释放但保存未排空、确认未提交 | 依据匹配权威回执更新知识/资源；Unknown不Submit，未提交待排空不重试；显式新AttemptId保留原意图/证据 |
| OCR.P.01 耐久/性能/现场 | §13已采纳Profile与真实样本 | 完整分母/真实资源排空、拒识/误接受与尾延迟资格；无Profile NotEvaluated |

HALCON/WPF等验证工程绑定§16.1；C1/C2/C3 fake只证明核心行为。Replay数据由asset/数据Owner提供并分设备/材料/字体/供应商/批次/环境；同产品/同采集不得同时进入训练和留出评估。实际物理错误接受、计量/现场值不能由文档编造。

## 13. BenchmarkProfile、资源与诊断

公共E2E、分位/完整分母、删失、样本/预热和NotEvaluated口径唯一引用[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不另定义算法。OCR E2E **RequestAccepted→ResourcesReleased**，队列/Acquiring/计算/证据复制/排空分别测；取消到真实资源释放另测。无最终排空样本不得判性能通过。

模块专属Profile冻结：Frame格式/尺寸/stride/真实支持/hash；每ROI面积/字数/语言/字符混淆/方向/退化分层；Mode/Deep尺寸/tiling/CharacterTopN/经典分割参数/OCV模式；模型/字表/Blank/runtime/device/hash；ROI/word/tile数量、batch和并发；冷加载/fresh read/热推理/asset换版；成功/无读/失败/超时/取消/排空未知比例；已采纳Profile的预热/样本/deadline/时延/CPU/GPU/native/内存/显存/long-run上限。所有目标数值仍 `TargetPending`，无目标只诊断、不达标。

C1测Validate/canonical/hash（无native，不伪造Accepted事件），输入量按ROI/字符表/文件数/stride元数据分层；C2测实际调度+协议资源/lease计数、原任务/Owner task槽/root HeldBytes/RetainedResultBytes/独立cleanup/接管等待和§4时间；C2R按candidate×sample/完整分母/Observed-Declared区别/全run真实排空测量；C3测margin×词框与candidate×sample组合；H/W/P分别实际测后端/控件/现场，不能把Fake耗时作为HALCON性能。

资源至少记录Frame/blob/derived/evidence复制字节、托管分配/GC、native对象/worker/lease活跃数、GPU峰值显存、CPU、queue/登记/事件深度、取消/Dispose等待和长稳斜率。Budget.MaxTiles限制实际tile枚举，超限RESULT-004不静默少跑；单驻留memory硬界限见§3，虚拟大图分片属于宿主输入能力，不把long当无限byte[]。worker按申请上限保守计入native/GPU，无已采纳上限不能注册并行生产route；本声明不要求审查AsunImage/DevExpress授权。

H另外分Resolve/用途许可/全闭包Hold/原bytes读取与校验/安全物化/缓存命中或未命中/native fresh read/参数readback/apply/挑战第二次fresh read/真实释放阶段；缓存不会抹掉许可与当次hold成本。跨MA/OCR计逻辑borrow分别保留，物理buffer按原Owner去重，源resident/copied/staging/evidence/native/旧代并存均入峰值。缺可观测native/GPU峰值只能NotEvaluated或Declared，不拿预约上限当Observed。W的E2E直到对应Frame/operation同binding可见确认及实际读回，含UI排队/上传/绘制/16WH读回与原generation撤销；未显示/失败/取消/Unknown全保分母，不只报最快成功样本。物理误接受/拒识目标、吞吐、P95/P99、并发及长稳时长由丝印/标签消费者各自PerformanceProfile采纳；未采纳不宣称达标。

诊断依§3事件、Errors和EvidenceTrace，有OperationId/epoch/请求与方法hash/后端版本/阶段/word数/score meaning/支持与错误原因。DIAG失败不改观测；每operation最多MaxEventsPerOperation，超过合并计数且保留资源/终态必要事件，sink自己用有界队列。Options.MaxEventsPerOperation至少24；每请求接纳时必须不小于 `24+8×request.Budget.MaxRois`（checked，OCV同取预算）保证阶段/结束事件位，不足请求METHOD-001；高频资源采样合并为阶段累计，不把诊断多次失败挤掉终态。native异常cause经脱敏，普通日志不写原图/敏感明文。没有消费者时不新增遥测报告文件。

## 14. 版本、发布与迁移

模块SemVer：原读/候选/字符位置/排序/分数/状态/错误/所有权/canonical变化为major；可选且不改变原语义的诊断为minor；bug修复不能假称资格自动延续。当前Value API/canonical **v0.2**、C2 Service API **v0.3**、指导 **0.6.1-prep** 均是规格版本，未发布程序集。

发布物按工程边界：Core不含视觉/UI、HalconAdapter依本机AsunImage、Wpf依本机DevExpress；每包含hash、.NET目标、公开API版本、依赖列表、能力、限制和适用验收；资产单独封存model/字表/Blank/mapping/preprocess/runtime/qualification及Golden，不把训练checkpoint当推理发布。依赖直接使用既有版本，不NuGet替换DevExpress/AsunImage。

Deep OCR模型文件不自动保存GPU/runtime/runtime_init；新worker加载后按runtime-profile设置并读回可查询参数，record实际值。新asset/Profile只作用于新operation；旧epoch停止接收→排空→保留证据→销毁。Replay旧资格基线→Shadow新旧版本（分别operation）→批准新revision，失败回退到仍有资格旧版本；保留新旧文件和回退路径。读回失败/hash不符fail closed，未知新字段/契约版本不得“尽量读取”成为生产事实。

## 15. 两个无 UI 消费者与外部接入自审

| 接入方 | 显式输入/调用 | 模块输出与宿主Owner |
|---|---|---|
| 丝印文字工具 | 帧provider、固定定位ROI、Classic/Deep Profile；有字形任务再Submit(OcvRequest) | 原读/字形Quality独立；宿主拥有丝印目标/缺笔质量和产品判定 |
| 标签文字工具 | 自己帧provider、Detection/Auto/已知单词ROI Profile，缺期待仍可纯读 | Words/原读/候选；标签模板/批次格式/期待来源/质量/打印设备归宿主 |

双方调用相同IOcrEngine Submit/Query/Wait/Cancel/StopAndDrain；各自resolver/factory/options，或宿主共享runtime但OperationId/key显式隔离。不在核心按consumer分支。对同样本同方法（Frame元数据/输入lease身份也一致），Fake确定性结果内容hash相同；真实HALCON对语义/已批准容差比较，不承诺跨硬件bitwise一致。一方期待改变/保存失败不改另一方观察或lease；一方关闭自己的控件不关闭共享runtime。

接入步骤：宿主按公开Frame/ROI/Profile适配→Validate→Submit并登记receipt原ID→有限Wait/Query→终态ResourcesReleased再读取/保存response→宿主期待/OCV质量比较→人工复核/独立外部事务。重试新attempt必须在旧资源排空或新独立worker/资源许可内，旧未知不自动重做事实。控件只消费§10View，命令经宿主身份/权限检查再调用engine；无UI不加载WPF。

外部接入自审：所有必需类型在§3/8、构造和异常闭合；无框架隐藏初始化/厂商句柄/产品对象；Frame与资产可retain/read/release；长期资源有额度；等待/关闭有有限回执；存储Owner与运行Unknown不混淆。真实产品Contract/Schema/证据仓适配需双方接收，当前不写跨模块契约、隐藏表或字段映射。

## 16. 逐切片准入与剩余门

### 16.1 唯一工程、范围与交付顺序

下列为规划工程，均未因本轮文档创建；namespace/依赖/消费者固定，真实仓库基线和派发授权由主控接收。

| 切片 | 唯一工程/测试落点（仓库相对路径） | 范围与准入后验收 |
|---|---|---|
| OCR-C1 | Core=`src/Modules/ocr/Asun.Modules.Ocr.Core/Asun.Modules.Ocr.Core.csproj`；Test=`tests/Modules/ocr/Asun.Modules.Ocr.Core.Tests/Asun.Modules.Ocr.Core.Tests.csproj` | namespace Asun.Modules.Ocr；§3.1～3.4/3.6被Contract使用的不可变值声明、结构校验与OcrContract/canonical，§12 C1；不实现IOcrEngine/IO端口、trace像素生成/native |
| OCR-C2 | 同一Core/Core.Tests（唯一Owner串行） | OcrEngine/§4～8 ports、§4.4 OcrProcessOwner/原Task/有限cleanup/Simulation及§9.1～9.6两个完整Host、§12 C2；软件可决定的装配/资源/恢复六项文档规格已由主控接收为ModuleCoreImplementationReady（仅规格准备）；无真实存储/native实现 |
| OCR-C2-R | 同一Core/Core.Tests | §9.7 OcrRecommendationHost/RunPlan/TrialJudge/Start-Query-Wait-Cancel/同Owner任务与分母；§12 C2R断言，有限候选执行Host；六项文档规格已由主控接收为ModuleCoreImplementationReady（仅规格准备），不含新增训练/算法 |
| OCR-C3 | 同一Core/Core.Tests | 仅OcrRoiRecommender/OcrRecommendationEvaluator的§3.5纯值候选/评价与§12 C3；不含Detection/Submit/Wait、实际采样或离线执行Host（软件属C2-R，真实接线属I） |
| OCR-H | `src/Modules/ocr/Asun.Modules.Ocr.HalconAdapter/Asun.Modules.Ocr.HalconAdapter.csproj`；`tests/Modules/ocr/Asun.Modules.Ocr.Halcon.Tests/Asun.Modules.Ocr.Halcon.Tests.csproj` | namespace Asun.Modules.Ocr.HalconAdapter；§8.1 HalconAdapterOptions/AsunImageHalconAdapter公开工厂及装配回滚；§8.2 recipe codec/五路线及§8.3模型资源桥/挑战executor；单向引用ModelAssets Core/Service、AsunImage cv2、§2所有已支持路线，真实H.01～08/native资源验证；BCL Exe带真实适配依赖 |
| OCR-W | `src/Modules/ocr/Asun.Modules.Ocr.Wpf/Asun.Modules.Ocr.Wpf.csproj`；`tests/Modules/ocr/Asun.Modules.Ocr.Wpf.TestHost/Asun.Modules.Ocr.Wpf.TestHost.csproj` | namespace Asun.Modules.Ocr.Wpf；net10.0-windows/UseWPF、installed DevExpress25.2.3+Core，§10.4资源/组合及W.01～04；§10.5可选接线只在TestHost引用viewport Core/Wpf/Asun.UI.Viewports.ImageFrame及原image-frame公开Core/Resources；无HALCON必需引用 |
| OCR-I/P | `tests/Modules/ocr/Asun.Modules.Ocr.Integration.TestHost/Asun.Modules.Ocr.Integration.TestHost.csproj` | 仅独立验证Host组合Core/HalconAdapter（UI场景才Wpf），两个消费者端口/实际离线推荐Host/真实存储及提交知识-排空/Replay/耐久/性能；产品集成改动另派发到产品Owner |

后续每工程分别用 `dotnet build <表中工程> -c Release`；H/Test和I/Test用 `dotnet run --project <表中测试> -c Release` 的Exe约定，必须按场景真正执行且必需项缺资产/跳过返回非零。W.TestHost在固定1920×1080开真实WPF并执行测试场景，不把build成功当UI通过。命令用§12外层有限截止，长稳另按采纳Profile有限时长设置总截止。禁止本轮创建工程、写tests/tools、改其它模块/共享/产品/来源/AsunImage；未来仅对应切片批准的表内目录可写，产品接线/跨模块Owner由主控分派。

顺序C1→C3（两者纯值）；C2/C2-R文档规格已接收，实际实现仍须派发并绑定代码基线；H→W/I的实际执行接线另行接收；H依Core端口，W可在Fake View下设计不等真实模型；H真实资格与W验收分开。生产P必须I真实消费者与已采纳Profile/真实数据完成。训练/数据/模型发布Owner接入先完成资产闭包，不自动在OCR建训练工程。

### 16.2 DEV-GOV-010 §3.1 六项逐项准备结论

| 门 | C1/C3纯值（既有接收保持） | C2运行服务（2026-10-11六项已接收） | C2-R推荐执行（2026-10-11六项已接收） |
|---|---|---|---|
| 1 边界/复用/禁止 | 已接收 | §1/15，丝印/标签同服务；§4.4无产品/设备权 | §3.5/9.7，有限候选、judge归标注Owner、无新增训练/搜索 |
| 2 唯一API/生命周期/资源 | 已接收，Value v0.2保持 | §3服务入口、§4.4全部Owner DTO/原Task/双轴，§8 ports/§9.1 Simulator，Service v0.3 | §9.7完整Plan/Case/Run快照/构造/Start-Query-Wait-Cancel/幂等与分母 |
| 3 从空无UI Host | 已接收 | §9.2完整字段、§9.3/9.4两个source/factory/clock/limits/request/cleanup Host | §9.7双sample×双candidate完整ProtocolEmptyJudge/RunPlan与调用，复用同根 |
| 4 正常→错误→恢复 | 已接收 | §11A.4/12 C2.10～17；原epoch/slot/Task、晚到、双轴、独立cleanup与接管 | §11A.4/12 C2R.01～04；judge异常/缺分母/总deadline/取消/旧RunId/原槽恢复 |
| 5 BenchmarkProfile | 已接收方法；目标待Profile | §13，queue/acquire/read/真实释放/接管/retained结果/task槽独立量；目标待Profile/NotEvaluated | §13有限case数/分母/真实E2E/全run排空，protocol保守资源上限不冒实测 |
| 6 工程/测试/范围/后续门 | 已接收 | §16.1同Core/Core.Tests/C2 BCL Exe/有限进程截止；H/W/I/P逐门 | §16.1同Core/Core.Tests，C2-R映射为--slice C2R；真实dataset/存储只阻I/P |

主控2026-10-10接收**纯值C1与C3六项规格**的结论保持；2026-10-11已回读0.5.0-prep增量§4.4、§8.1、§9.1～9.7、§16.1～16.3，接收**C2/C2-R六项文档规格**。四个Core切片均为 `ModuleCoreImplementationReady`（仅规格准备）；C1不含运行服务，C3不含离线执行Host。H/W根槽与借用映射增量限定内容接收，整H/W/I/P及整模块保持 `PreparationIncomplete`。协议Empty/Refused只验证协议和评价分母，不证明真实OCR准确率。不得将本次同步解释为实现授权、构建/测试完成或ImplementationSpecificationReady。H/W/I/P不套纯Core表冒充完成，当前指导给定实现步骤/契约，实际工程/模型/真实UI/Golden/性能/现场均未验证。

### 16.3 已冻结的本地决定与真实剩余门

已冻结：C2进程根Owner先reserve后factory/原任务与借用强持、有限独立清理/显式恢复/确认接管；C2-R有限推荐执行服务；OCR与OCV共享一个运行入口/资源调度，观察分开；业务Grammar/期待/lexicon归宿主；单operation一条路线，有限重试/备用由Host新attempt；Frame byte容器有硬界限；每operation独立worker；native不能提前completion；证据内存内容摘要无自引用、存储归宿主；Gray16转换和支持表示明确；推荐为有限Host编排/只读建议；UI为证据控件，无产品页/质量权。它们是用户委托下依据本地资料与来源冻结的技术决定，不再留“程序员任选/主会话再选”。

剩余门精确如下：

- C1/C3：纯值六项规格已由主控接收，ModuleCoreImplementationReady；后续绑定权威仓库/可审计基线并获实现派发后才build/BCL Exe。C3实际推荐执行Host明确定位C2-R（§9.7），不在该纯值接收内。
- C2/C2-R：§4.4/9公开构造、Factory前root/slot、原Task与迟到lease/native借用、双轴错误、独立有限cleanup/显式Recover、两个协议Host及推荐执行API的六项文档规格已于2026-10-11获主控接收，ModuleCoreImplementationReady（仅规格准备）；实际BCL build/run/协议资源验证未执行，后续绑定权威仓库/可审计基线并获实现派发后才执行。协议Empty/Refused不证明真实OCR准确率，真实HALCON/产品资格另按H/I/P门验收。
- H：§8.1工厂签名/构造/回滚与native/回调排空边界已由主控定向内容复核确认，本轮§9.6原映射内根槽/借用source公开挂接增量已获主控限定内容接收；此确认不接收H整切片，仍为PreparationIncomplete。真实HALCON26.05 assets/字符表/参考good pattern、实际签名类型有歧义时定向确认、同样本Golden/几何/质量/native排空/资源门保留；不核AsunImage算子存在，不审授权。
- W：§10/11B.5保存提交知识/原意图查询/排空投影及命令已由主控定向内容复核确认，本轮§9.6原Wpf.TestHost映射根Owner与借用/Closing接管增量已获主控限定内容接收；此确认不接收W整切片，仍为PreparationIncomplete。实际DevExpress25.2.3程序集调用/真实WPF三语、UIA、键盘、布局、代次/权限/关闭及宿主viewport挂接门保留。文档官方25.2依据不等25.2.3运行验收。
- I：双真实Host/产品Contract与Owner映射、实际Frame与资产端口、受控持久回执/重启防重放；跨模块接线由相应Owner与主控接收，不改共享文件。
- P：消费者采纳时延/资源/样本/物理错误接受/拒识/现场Profile、真实成像数据/部署与HIL/耐久（适用时）；缺这些只阻实际资格，不阻C1～C3。

### 16.4 全批准范围软件设计闭合结论（2026-10-12，原OCR会话）

**结论：本模块全部已批准OCR/OCV能力的软件设计已闭合。** 本结论在0.6.0-prep完成、0.6.1-prep窄同步后保持，是指导正文的文档阶段结论，不是新产品状态、实现授权或运行资格；不再把单个Core准备、局部H/W接收或文件结构检查当作完整范围结论。§1.3为本轮分母，未新增引擎、训练器、产品页、工艺放行或设备控制范围。Value/canonical v0.2及Service v0.3、既有C1/C3/C2/C2-R接收保持；整模块历史`PreparationIncomplete`与H/W/I/P未验资格不被本轮自审提升，也不表示仍有待程序员猜选的软件设计项。后续实现以本指导对应切片直接执行；外部输入只阻依赖它的真实适配/资格部分，不重新全审已接收Core。

| 完整能力或用户准则 | 唯一实施位置与闭合结果 |
|---|---|
| 单字/字库、单行/多行/区域、Unicode与字表、复杂成像、拒识/原读/候选、独立OCV | §1.3/2/3/5/8.2；五路线参数资产、像素/支持/原读/Geometry/score/拒绝及OCV语义已定。每请求一路线、无期待纠字/隐式改路线；复杂成像是否合资格由真实样本判定 |
| HALCON优先、效率与自动参数建议 | §2/8.2/9.7/12/13/17；26.05固定算子与exact参数/readback，有限推荐只建议，冷/热/fresh read/物化/双read/取消排空/可见端到端及完整分母。未测效率不编数，不再做重复研究 |
| 可独立模块/控件、无UI复用与外部接入 | §3/4.4/8.1～8.3/9/15/16.1；一个Core、一个H、一个可选W，稳定公开构造/端口、两个Host与双根原Task/借用/有限恢复；不泄产品页面、私有表或SDK handle |
| 来源复用、模型/训练/数据/用途权威 | §8.3/11B/17；既有HALCON/来源研究保留，MA精确Ref/闭包/用途/安全物化/技术挑战/签名与生产采纳分权。训练/封存/字库资格由原生产者提供，不创建第二资产库或把开源README当验收 |
| 精美且可用的DevExpress UI、语言/权限/恢复 | §10.1～10.5/11B.5/12 W；实际布局/只读Grid与PropertyGrid/联动/PNG预算/完整三语字段与理由、原保存Unknown查询、双STA同Control viewport接线、键盘/UIA和固定1920×1080验证已定 |
| 普通程序员可执行、异常恢复与可判定验收 | §3～13/16.1～16.3；数据/参数/Owner/路线/算子/状态/错误/预算/两消费者/原Task/测试工程及正常-失败-恢复断言一一落正文，不依赖聊天或.work；不要求开发者补做架构、算法和质量决定 |

**本原会话两轮有限自审。** 第一轮只审本轮完整能力增量：按手册核recipe键、Deep仅get的dimensions与可set的size、Manual准确映射/增强图/拒识、crop两矩阵/四邻支持、分割多候选、OCV/字符分数和挑战逐字段容差；发现的参数名、错误Stage及Decode组合边界已修。第二轮从消费者调用反查闭包：MA低层原ProjectAcquire意图/全hold/许可/物化/累计调用容量/原双根，挑战完整构造/样本与真值分权/第二fresh read/未完成分母，UI资源闭集/同Control.Backend/Presentation/Lifetime与完整Context/源租约/Unbind，以及native未知释放不可恢复分支。发现的不存在engine.EngineEpoch公开属性、viewport Selection枚举、资源Get结果未核与模糊参数文字均已改为已公开消费方法/显式表。已接收Core与原根/保存片复用，不全审来源、不修改其它模块、不等待主控代做内容审核。

剩余事项都有精确Owner与影响范围：

| 剩余门/输入 | Owner | 只影响的范围 |
|---|---|---|
| 权威代码仓库/可审计基线和实现派发 | 平台仓库Owner/用户调度 | 实际创建与修改工程；不影响当前完整文档结论 |
| 真实模型/MLP字库/OCV good pattern、成像域与真值/容差、训练资格及三Purpose封存材料 | 丝印/标签原模型生产者、数据真值Owner、用途资格Owner | 对应H route/挑战与其生产用途；不得伪造physical阈值，不阻Core/协议Host |
| 实际MA Store/Authority安全物化、同Scope用途许可及Frame/坐标/源租约 | MA/源模块实现Owner、丝印/标签runtime接入Owner | H资产消费及I实际数据接线；OCR自己的mapper设计已定，不要求上游替OCR写mapper，不改其指导 |
| 真实cv2公共参数封送、native正确性/内存/GPU/释放与资源确认 | OCR-H实现Owner及目标部署runtime Owner | 本模块H build/真实Golden/native/资源运行验收；无需依赖授权检查或AsunImage内部扫描 |
| 实际WPF/DevExpress25.2.3/API与UIA/三语/1920×1080、viewport真正Visible/Unbind | OCR-W实现Owner、原viewport运行Owner、消费者Host Owner | W和可选显示I；设计/API消费已闭合，PNG-only无viewport必要门 |
| 产品Contract与原保存Owner/journal回执、重启防重放和两个真实消费者 | 丝印/标签产品与持久化Owner | I集成/耐久；保存Unknown不能靠重新OCR解决 |
| 采纳的时延/资源/误接受/拒识/长稳/真实样本和现场部署要求 | 各消费者PerformanceProfile/质量与现场Owner | 对应P产品资格，未测仍TargetPending/NotEvaluated；Simulator/文档检查不代现场 |

内部软件设计欠项为零；上述真实资产、物理验收数值、实现/部署与运行观察保留为输入/验收门。本轮验证仅限指导的链接/结构、公开消费字段、资源表完整性及数学定向算例；未创建工程，未执行C#构建、真实HALCON/AsunImage、WPF/可见读回、Golden/性能/HIL或现场验收。

定向文档核验结果：复用validate_docs.targets检查本文全部本地链接，代码围栏配对、公开类型无重复；§10.4并列字段的三语项数逐项一致，全部recipe标量都有显示资源，§6完整错误码与§6理由闭集有对应恢复文字。§8.2的0°、±90°及37.25°非整数宽高采样正逆公式在§12 H.05结构误差内；这里只验数学公式。§3～7与§9已接收Core/Host文本hash和修订前一致；当前指导版本/工程引用/允许路径定向核对通过。未重算已接收canonical向量，不新建检查脚本/测试文件/报告，未全仓验证或以链接通过替代上述内容自审。


2026-10-12 viewport 0.3.5限定消费增量（0.6.1-prep）：§10.2表选框导航已定位§10.5.2完整稳定对象键；§10.5.1用公开ViewportImageFrameSourceFactory预装配/登记原已发布CPU源、保同Frames/Coordinates，§10.5.3只落实本Host原显示失效分支的完整空Update/EmptyTransition/旧源归还，未新增Clear命令或Word选择事件。§10.5.4给出有限消费反例并由本原会话自审；完整批准范围闭合结论保持，不等待主控内容审核。已对齐v0.2 Lifetime/Presentation、根与关闭、算法/三语/向量和既有规格接收均复用；实际源/WPF/高亮/真实空画面/资源排空运行门仍未验。本轮仅编辑本指导，定向检查新增公开签名/调用/fragment、同Task/完整键/代次/预算/Unknown恢复；不写工程/代码/报告/脚本、不改上游或共享文件。

## 17. 研究依据、采纳与局限

### 17.1 交付项目只读来源

[PCBA-AOI OCR与OCV指导](../../references/project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/OCR与OCV开发指导.md) 的原读/映射/期待/OCV分离、资产闭包、退化拒识和训练发布隔离采纳到§1～5；旧HALCON API/产品字符类别和放行规则不迁入。来源是设计经验，不是平台生产验证。

[DZ-XVision说明](../../references/project-snapshots/DZ-XVision/20261004/README.md) 与 [source-manifest](../../references/project-snapshots/DZ-XVision/20261004/source-manifest.json) 固定 treeSha256=`a3649338762b234537d185d18496fcd438ba91eafd06b8d817ebee4c5a5ceae8`。本轮复用先前已核的ToolOCR.cs、ToolPrintCheck.cs、DZXVision.cs、ProductInspectionOrchestrator.cs、ProductInspectionResultCollector.cs、ProductResultStore.cs、InspectionContexts.cs、CaptureTask.cs、HVision/TileImage.cs；稳定区域/定位谱系/有限attempt/原子保存需求/事务隔离落§11B。原图路径、静态参数、料号/ToolStr/MES/旧WinForms行为不迁入Core；持久事务只作宿主需求。

### 17.2 HALCON 26.05官方语义

唯一算子入口：[halcon算子手册/operators](../../../halcon算子手册/operators/)，版本26.05.0.0。已定向读正文，不以页面存在代替实际算法运行；operator均经ImageLibDotNet.cv2，无封装存在审查。

| 已读页面组（该目录下.html） | 采纳落点 | 局限/验证 |
|---|---|---|
| apply_deep_ocr、get_deep_ocr_param、set_deep_ocr_param、create/read/write_deep_ocr | mode/byte通道、坐标域、Blank/mapping、字符候选、tiling/alignment/runtime，§2.2/3/14 | 模型/dataset/真实成像仍需H/P，不声称默认模型覆盖客户字体 |
| create_text_model_reader、set_text_model_param、find_text、get_text_result/get_text_object、clear_text_result/clear_text_model | 最少字符/近水平、rank0拒识、生命周期，§2.3 | 不适合单字/任意布局；配置与拒识Golden需要真实样本 |
| do_ocr_single_class_mlp、do_ocr_multi_class_mlp、do_ocr_word_mlp | winner/字符top-N与纠正边界 | Word Score非概率，v0.2不走纠错原读 |
| threshold、auto_threshold、connection、select_shape、sort_region、text_line_orientation | 分割筛选/方向/极性/Sigma语义 | 手册不能提供客户字高/阈值，不填生产默认 |
| create_ocr_class_mlp、trainf_ocr_class_mlp、traind_ocv_proj、do_ocv_simple | 训练/推理隔离、OCV Quality/模式/angle，§2.4 | good pattern由asset Owner提供，不用OCR替代字形质量 |
| gen_image1、compose3、rgb1_to_gray、invert_image、affine_trans_image_size、hom_mat2d_translate/translate_local | §8.2逐行复制/通道、pin结束、row/column矩阵与半像素补偿 | 本轮定向读26.05原页；原有效域四邻不足拒绝，不改get_system观察到的int_zooming全局值 |
| set/get_deep_ocr_param、set/get_text_model_param、get_text_object/result、read/get_params_ocr_class_mlp、read_ocv/close_ocv、clear_dict/clear_handle | §8.2准确参数名、仅get dimensions、Manual增强图/各rank、fresh模型生命周期 | 本轮核手册修正字段；模型实际readback/释放仍须真实H，不发明clear_deep_ocr或将未确认native清理当成功 |

真实C#类型/重载歧义才查公开签名或消费项目编译，不扫描内部，不发明train_dl_model/clear_deep_ocr/clear_ocv操作。

### 17.3 PaddleOCR固定源码与实际测试研究

已有只读 [PaddleOCR快照](../../references/open-source/PaddleOCR/b03f46425e8ff4442b268ce449e3eef758146cd4/)，固定 [GitHub commit](https://github.com/PaddlePaddle/PaddleOCR/commit/b03f46425e8ff4442b268ce449e3eef758146cd4)，提交日期2026-06-11T11:27:04Z。此前核对远端与本地4文件逐字节相同，本轮直接复用，不新下载/安装/快照。

| 已读文件 | SHA-256 | 实质采纳/局限 |
|---|---|---|
| ppocr/postprocess/rec_postprocess.py | a5e5376514991656f7c7977f4a51ac61224ca6939f8ba41bc18e32ce9d15c872 | BaseRecLabelDecode在原时间序列去相邻重复后删blank；dict行序/空格显式；保留字符confidence均值，不是词概率 |
| tests/ppocr/test_rec_postprocess.py | 4e79c66d1e765a54763d38ef532be13c6984ac900694ffd21baf14baf6b43bbf | 德法重音/中文/下划线分词实际断言；不覆盖全部Blank/错dict/批次索引边界，补§11A/12反例；未运行上游测试 |
| pyproject.toml | 63e8bfa19e197e47649a95dad422bcb09c1d2959367cafd40b0a7f19e4452412 | Python≥3.8，paddlex[ocr-core]≥3.7.0,<3.8.0，PyYAML≥6、requests、aiohttp≥3.8、typing-extensions≥4.12；不能称无外部运行时 |
| LICENSE | 3840c5c0c61c294264d2dd77b8777be6ddd90121ef4e0e64abcd22edea581d6e | Apache-2.0仅源码，权重/训练数据/运行依赖各自来源不由源码许可代替 |

强项为解码步骤明确、字典/语言边界可观察、真实测试可读；限制为返回平均confidence、无probabilities时上游填1、测试覆盖不足和Python/Paddle依赖。外部adapter须无score时None，CTC反例AA明确；这些只迁移接口/测试思想，不抄算法替代HALCON，不批准Paddle生产引擎/模型，也不宣称上游测试通过。

### 17.4 DevExpress官方25.2依据

已读以下官方页面的25.2内容，使用本机25.2.3程序集：

- [DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)：LayoutGroup/LayoutPanel、布局停靠，落§10工作区。
- [GridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl?v=25.2)：ItemsSource/TableView、虚拟化、排序过滤/固定列，落区域表。
- [PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)：SelectedObject/类别/搜索，绑定只读投影而非生产可写参数。
- [FlyoutControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Editors.Flyout.FlyoutControl?v=25.2)：正确namespace、IsOpen/StaysOpen/PlacementTarget/FlyoutSettings、动效/动态UIA通知。
- [SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)：header/item/separator；bars/ribbon SuperTip、SimpleButton.ToolTip包装SuperTipControl。
- [ThemeManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.ThemeManager?v=25.2)：普通主题ThemeName；lightweight主题另用LightweightThemeManager。
- [ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)：DataSource/ArgumentDataMember/ValueDataMember，仅同后端诊断展示。

局限：官方能力不替代目标程序集编译/控件模板/键盘/UIA/1920×1080真实行为。主命令可见、图像优先、Flyout只展开证据/候选，不为视觉效果隐藏恢复；§10才是OCR唯一UI实现要求。

2026-10-12另定向读本机DevExpress25.2官方XML的DataViewBase.AllowEditing/NavigationStyle、DataControlBase.SelectedItem、ColumnBase.ReadOnly、GridViewBase.ShowGroupPanel、TableView.ShowIndicator、LayoutGroup.Orientation、BaseLayoutItem.ItemWidth/Height及PropertyGridControl.SelectedObject/ReadOnly；§10.4沿实际继承成员装配。本轮dxdocs端口未暴露，复用已读官方页面及匹配本机XML，不下载替换程序集；XML存在不证明真实25.2.3编译/模板/运行行为。


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

## 附录 A：Module API Contract（Value v0.2 / Service v0.3）的权威与切片映射

唯一公开声明在§3（值/请求/输出/生命周期/推荐/trace）、§4.4（进程根Owner/slot/原任务/有限恢复）、§8（资源/worker/progress端口、§8.1工厂/构造、§8.2参数codec及§8.3资产桥/挑战）、§9（协议source/clock/factory/两个Host及C2-R服务）、§10（可选WPF输入/保存知识与资源投影/事件）；附录不复制DTO。§4～7是唯一运行与错误语义，§9示例使用相同receipt，§11/12断言必须跟随它们。旧v0.1/OcrState/RunAsync/VerifyAsync/IOcvVerifier/GrammarChecking/RegionId核心类型已退役，不允许实现第二套入口或状态机。

C1只消费纯值IOcrContract；C2实现IOcrEngine、OcrProcessOwner及注入ports/Simulation；C2-R实现IOcrRecommendationHost有限执行；C3只实现无副作用ROI提案/评价；同入口有限离线执行Host软件明确属C2-R，真实数据/Owner接线属I；H实现真实HALCON worker；W独立投影UI；I/P完成真实接入/资格。Core不引用HALCON/WPF/DevExpress/产品数据库，H/W单向依赖Core；H的Assets桥另单向引用ModelAssets公开Core/Service，viewport可选引用只在W/I Host，不反向引用产品；可被两个宿主单独引用、构建、测试、发布，加载模块不要求先打开窗口。

文档版本0.6.1-prep；Value契约/canonical保持v0.2，C2 Service契约v0.3。整模块仍 `DesignReview/Prep` / `PreparationIncomplete`；C1/C3纯值范围2026-10-10六项接收保持，C2/C2-R于2026-10-11获主控六项文档规格接收，均为ModuleCoreImplementationReady（仅规格准备）。0.4.1-prep的HALCON工厂/worker回滚、native/回调排空及保存知识/Unknown查询边界确认保持；本轮H/W根槽与借用映射增量限定内容接收，不提升整H/W/I/P切片准入。协议Empty/Refused不证明真实OCR准确率。真实编译、OCR/HALCON、WPF、性能和现场门保持，本轮完整设计结论见§16.4，当前不启动实现。平台Schema/客户Profile/资格只有实际影响的切片关闭，不得以它们普遍阻断无UI Core，也不得以Core准入宣布整模块/产品/生产通过。
