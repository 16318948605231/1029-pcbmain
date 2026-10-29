# 受控 AI 推理执行（ai-inference）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`Core/Simulator v0.3`

- 模块 ID：`IM-047`；来源指导：`PKG-052`；状态：`DesignReview / Prep`
- 切片准入：Core/Simulator v0.3 为 `ModuleCoreImplementationReady`（规格准备，2026-10-09 主会话接收）；实现、测试执行、性能与生产资格未通过。
- 版本：`0.5.1-prep`；日期：`2026-10-12`（完整批准范围收口；Core API v0.3 / Canonical v1 不变）
- HALCON Adapter 补充：`Adapter API v0.1`，`2026-10-11`；附录 C 的确定 HALCON Adapter/原Owner桥/公开装配指导内容已由主会话限定接收；真实交接、编译/运行与资格仍未验证，不改变已接收 Core/Simulator v0.3。
- 规划消费者：缺陷候选、OCR 对照、工程辅助及其他视觉项目。
- 技术基线：C# / .NET 10；HALCON 26.05 能力经 `ImageLibDotNet` 公共边界使用；AsunImage 与 DevExpress 按平台已定依赖直接使用。
- 本页是 ai-inference 独立接入的唯一指导。它不批准平台候选 Schema、状态、错误码、Owner、用途资格或生产配置；既有权威仍由各自 Owner 管理。

## 1. 目的与职责

模块接收已经授权且版本固定的模型执行闭包、图像/张量输入和有界执行配置，执行预处理绑定、模型装载、批次推理、类型化后处理和拒识，返回带实际来源、完整性、时间及资源信息的中性候选结果。核心能力必须可由无 UI 的 .NET 宿主调用。

调用应用负责调用顺序、输入与目标关联、期待值解释、工艺规则、必检/缺项政策、质量判定、证据事实提交和全部设备副作用。模块不得写入机器判定、PASS/FAIL、质量放行、生产状态或设备命令；不得包含 PCB、SPI、AOI、点胶、涂覆等制程分支、枚举、阈值或目标语义。

模型训练、真值治理、验证方案、模型发布/撤回和候选/影子/建议/自动化资格归 AI 治理及用途 Owner。推理模块不得选择 `latest` 模型或自行授权用途。已有专用 Deep OCR 执行/文本语义仍归 OCR 能力；只有经任务选型批准的通用模型计算或外部 OCR 对照才接入本模块，原文、语法和期待值比较由调用方处理。

## 1A. 三态仲裁架构（Confidence-Gated Arbitration）

### 1A.1 设计动机

竞品（Koh Young AI Solver、Mirtec Smart Learning）的 AI 已在检测主链路直接参与判定，检出率比纯规则链高约 15%。如果本平台 AI 永远只做"建议"角色，在产线检出率上永远追不上。但完全放权给 AI 又缺少审计安全和工艺可控性。

三态仲裁解决这个矛盾：AI 可以直接产出判定，但必须在审计轨迹里留下完整证据、模型版本、置信度和特征图；规则链与 AI 冲突时强制转人工，不"谁赢谁算"。

### 1A.2 三态定义

推理结果经置信度门限和规则链交叉验证后产出三态终值之一：

| 终态 | 条件 | 处理 |
|---|---|---|
| `AutoResolved` | AI 置信度 ≥ 用途 Profile 的 `autoResolveThreshold` **且** AI 判定与规则链判定一致 | 自动判定。推理模块在结果中附 `VerdictKind=AutoResolved`、实际模型版本、置信度、特征图引用和规则链指纹。审计轨迹完整可追溯。 |
| `NeedsHuman` | AI 置信度 ≥ `autoResolveThreshold` **但** AI 判定与规则链判定冲突 | 转人工复判（`human-review` 模块）。推理模块不决定最终判定，只产出冲突证据包。 |
| `NeedsSampling` | AI 置信度 < `autoResolveThreshold` 或判定为分布外（OOD score > ood_threshold） | 主动学习采样。结果不参与判定，但输入样本进入 `ai-dataset-governance` 的采样队列，用于后续模型迭代。 |

### 1A.3 仲裁流程

```
输入证据 → 检测链（规则 + HALCON + AI 推理）
                ↓
   AI 推理输出 { verdict, confidence, evidence, explanation, oodScore }
                ↓
   置信度门限 + 规则链交叉验证：
     高置信 + 与规则链一致   → AutoResolved（自动判定，完整审计）
     高置信 + 与规则链冲突   → NeedsHuman → human-review
     低置信 / 分布外         → NeedsSampling（主动学习采样）
                ↓
   人工结论 → 回流为训练标签（ai-dataset-governance）
```

### 1A.4 实现边界

- **推理模块只产 `VerdictKind` 枚举和证据包**，不直接写入质量判定、不调用 `human-review`、不写生产参数。终态消费由调用方（宿主/产品层）按 `VerdictKind` 分发。
- `autoResolveThreshold` 由用途 Profile 定义，不由推理模块自行设定；阈值变更须经批准并绑定试产证据。
- 仲裁的"规则链"是调用方传入的 `RuleChainVerdict`（Pass/Fail/None），推理模块不自己运行规则链。
- 证据包（`ArbitrationEvidence`）包含：模型版本 hash、置信度数值、特征图引用（可选）、规则链指纹、冲突原因（如有）、时间戳和资源消耗。
- `NeedsSampling` 的样本引用写入 `ai-dataset-governance` 的 `ActiveLearningQueue`，推理模块只产引用不复制数据。
- 本模块不维护人工结论回流逻辑；回流由 `ai-dataset-governance` 模块按 ModelCard 和采样策略处理。

### 1A.5 数据结构

```csharp
/// <summary>
/// 仲裁终态。推理模块产此终态，调用方按终态分发。
/// </summary>
public enum ArbitrationVerdict
{
    /// <summary>AI 高置信且与规则链一致——自动判定。</summary>
    AutoResolved,
    /// <summary>AI 高置信但与规则链冲突——转人工复判。</summary>
    NeedsHuman,
    /// <summary>AI 低置信或分布外——主动学习采样，不参与判定。</summary>
    NeedsSampling
}

/// <summary>
/// 仲裁证据包。附在推理结果中，完整可审计。
/// </summary>
public sealed record ArbitrationEvidence(
    ArbitrationVerdict Verdict,
    string ModelVersionHash,
    double Confidence,
    double? OodScore,
    string? ExplanationRef,
    string RuleChainFingerprint,
    string? ConflictReason,
    DateTimeOffset TimestampUtc,
    long ElapsedMicroseconds);
```

### 1A.6 与竞品的对标差距

| 对标项 | Koh Young AI Solver | Mirtec Smart Learning | 本平台三态仲裁 |
|---|---|---|---|
| AI 在主链路 | 是（CNN 嵌入主链路） | 是 | 是（AutoResolved 终态直接判定） |
| 冲突处理 | 不公开 | 不公开 | 显式 NeedsHuman，强制人工，不谁赢谁算 |
| 主动学习 | 不公开 | 部分（Smart Learning） | NeedsSampling → ai-dataset-governance 闭环 |
| 审计轨迹 | 不公开 | 不公开 | 完整：模型版本/置信度/特征图/规则链指纹/时间/资源 |
| 参数自动调优 | 不公开 | 是（减少 90% 人工调参） | 由 L1-L4 参数学习层处理（见 ai-dataset-governance 指导） |

## 1B. 新架构适配要点

本模块的 §1A 已是三态仲裁架构（内容性），本节补充面向新平台架构的适配约束。

**架构门禁**：`Asun.Modules.AiInference.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"核心能力必须可由无 UI 的 .NET 宿主调用"，Core 在无 WPF 宿主中完整运行。CI 架构测试扫描程序集引用，违反即构建失败。

**Blazor/Web**：Web 端展示推理候选、置信度分布和三态仲裁结果（`AutoResolved`/`NeedsSampling`/`NeedsHuman` 占比与趋势）；推理执行在服务端，浏览器不加载模型、不执行 ONNX Runtime。模型制品通过 HTTP Range 分片下载；实时推理流经 SignalR 推送候选摘要而非原始图像。§1 已明确"不得选择 `latest` 模型或自行授权用途"——Web 端不得提供"使用最新模型"按钮。

**AI 推理 Tiling**：本模块是 Tiling 机制的**拥有者**（§2.3B.4），不是它的消费者。约束：
- tile 切分由本模块在服务端按 ROI + 内存预算执行，浏览器不参与切分，也不自行裁切上传图像
- tile 租约由本模块持有并在推理完成后归还 `image-frame`；不得在 Web 端缓存 tile 延长租约
- 跨 tile 的全局判定（如 PCB 级缺陷）在本模块内完成后再推送摘要，不把逐 tile 结论暴露为产品级结论

**HALCON 双跑**：本模块是 HALCON 备选双跑 CI 的**对比基准方**，不是 HALCON 路线的一方。约束：
- 传统 HALCON 视觉路线（`features-2d`、`variation-inspection`、`alignment-2d` 等）与本模块的 AI 路线**并行**，两路都产出候选，由宿主侧合并后进行三态仲裁；两路对同一缺陷的响应不同是**预期语义差异**，不是双跑失败
- 本模块自身的 ONNX 路线与第三方参考实现（如 anomalib PatchCore 的官方实现）双跑时，IoU/召回率设容差门禁；§1A 已明确"固定 seed 不是复现证明"，非确定性须在结果中标注

## 2. 部署边界、依赖与适配器

建议交付为可单独引用、构建、测试、版本化和发布的核心类库；可选适配器程序集独立版本化。独立 DLL 不要求独立进程。隔离 worker 仅在部署决策明确进程边界、IPC、崩溃恢复、租约与额外延迟/内存预算后采用。

依赖端口限定为：

| 端口 | 输入/输出 | Owner 边界 |
|---|---|---|
| 模型资产解析器 | 精确资产引用 → 冻结内容闭包及内容保持租约 | 资产模块持有解析/完整性；推理模块不得取 latest 或自行更改已封存资产 |
| 图像/张量输入源 | 类型化输入描述及只读租约 → 有界可读数据 | 调用方/图像模块持输入事实；推理模块按约定读取并在实际最后使用后释放租约 |
| 执行预算端口（必需） | CPU、native、GPU、队列、内存及 deadline 预约 → 预算租约/拒绝 | 外层执行资源 Owner 统一预算；独立宿主也须显式提供有界本地实现 |
| 推理后端适配器 | 冻结模型、输入和设置 → 原始类型化输出及实际运行回执 | 具体适配器封装 HALCON/AsunImage 或经批准的其他公开后端，不向核心泄露 SDK 句柄 |
| 任务 codec（必需） | 冻结任务定义及原始输出 → 校验、后处理与规范载荷 | 只实施已绑定的中性任务规范；不拥有用途授权、质量规则或 SDK 句柄 |
| 用途检查端口（必需） | 请求身份与用途引用 → 允许/拒绝及诊断 | 外部用途 Owner 持资格；Core 在执行及结果披露前检查，不自行批准 |
| 诊断接收器（可选） | 结构化生命周期事件 → 观察者 | 不得回调重入核心锁或影响推理结果 |

证据/结果提交是宿主外接面，不是 Core 端口；宿主取得最终内存结果后自行调用原 Owner 并查询提交回执。每个装配根显式注册 A.4 的六个必需端口；缺少端口或无效 options 按 A.4 在工厂创建时抛参数异常，不创建引擎。请求引用未知或未登记的适配路线返回 `Rejected/AdapterNotReady`。`NotReady` 仅是宿主准备状态，不属于 Core 状态枚举或错误码；请求须返回本指导定义的具体终态和诊断。核心不得直接访问产品数据库、WPF/WinForms ViewModel、全局变量、私有结果 Store 或硬件 SDK。

### 2.1 HALCON 与 AsunImage 能力选择

每种任务变体先查仓库 `halcon算子手册\operators` 中 HALCON 26.05 对应算子说明及限制，确认已有 `apply_dl_model`、`optimize_dl_model_for_inference`、模型参数/设备查询和任务专用输出处理路线。HALCON 26.05 全部算子经 `ImageLibDotNet.cv2` 调用，不重复核验封装是否包含算子，不另接 `HOperatorSet` 或 `halcondotnet.dll`；仅有实际 C# 参数类型、重载或封送歧义时查公共签名/消费工程编译。不得读取、反编译或修改 AsunImage 内部。

已定向确认的 AsunImage 公共表面包括 `HDlModel` 的读取、`ApplyDlModel(HDict[], HTuple)`、参数读写和释放成员，`HDlClassifier.ApplyDlClassifier(HImage)`，`HDlModelOcr.ApplyDeepOcr(HImage, string)`，`HDict`、`HImage`、`HDlDevice`、`HComputeDevice` 等公共类型。此列仅说明已见到的公开包装存在，不构成本模块最终 API，也不保证线程、超时、设备设置、资源排空或 HALCON 26.05 具体行为。实施者按本机目标版本官方资料验证算法、并发和资源真实行为；公开成员列举不构成依赖准入或算子存在性门，只有实际 C# 调用歧义才核签名；不得从名称推导参数语义、默认值或可取消性。Deep OCR 既有语义继续由专用 OCR 能力持有。

如需引入其他推理后端，先在本指导对应修订中说明 HALCON/AsunImage 已有路线的具体缺口、外部公开接口与固定版本/commit、依赖及许可证元数据、冻结样本上的输出偏差/尾延迟/峰值资源比较和部署限制。候选路线不自动成为产品依赖。

只读核对的 [`AsunControl` 快照](../../references/project-snapshots/AsunControl/20261004/original) 同类资料包括旧版 Variation Model 参数/结果/比较类：其中可借鉴显式参数对象、结果对象 `Dispose`、阶段完成事件和大图裁切坐标恢复的关注点；其 .NET 8/WinForms、字符串错误、可变公开参数、`bool Success` 汇总、固定线程默认值和领域结果结构不作为本模块契约。本文改为版本化闭包、机器可读错误、显式终态/缺项、取消排空和外部资源 Owner，避免把历史实现的隐含假设带入独立模块。

### 2.2 已核对的 HALCON 26.05 路线与选择门

本轮核对的本地目标版本页面及公开签名如下。页面存在不等于本模块已经运行或完成资格验证；实现时仍须对输入字典键、输出字典键、错误、线程和资源行为做目标环境测试。

| 能力 | HALCON 26.05 页面/签名 | 进入本模块的条件 | 备用/恢复路线 |
|---|---|---|---|
| 通用模型装载与执行 | `read_dl_model` → `get/set_dl_model_param` → `apply_dl_model`；AsunImage 对应 `HDlModel(string) / ReadDlModel / GetDlModelParam / SetDlModelParam / ApplyDlModel(HDict[], HTuple)` | 模型闭包、DLSample 字典、输出清单和任务适配器已冻结；先核读取参数和实际后端，再执行 | 仅使用用途 Profile 预先批准的同模型 CPU/另一设备/精度变体；不因失败临时改 batch、输入尺寸或阈值 |
| 推理优化/精度变体 | `optimize_dl_model_for_inference(DLModelHandle, DLDeviceHandle, Precision, DLSamples, GenParam, DLModelHandleConverted, ConversionReport)`；AsunImage 有两个 `OptimizeDlModelForInference` 重载 | 转换报告、同样本数值/拒识/资源比较合格，并把派生模型作为新资产/新闭包 | 转换失败回原模型；转换成功但报告未核或输出不等价时不得运行生产用途 |
| 输入变换 | `transform_dl_sample_batch(TransformPipeline, DLSampleBatch)` | TransformPipeline 版本、顺序、shape、插值、mask 传播与训练输入同源且可重建 | 只可退回已批准的原始输入变体；不能省略变换或用显示图替代 |
| 热图/解释投影 | `gen_dl_model_heatmap(DLModelHandle, DLSample, HeatmapMethod, TargetClasses, GenParam, DLResult)` | 任务明确允许解释输出，热图仅作为模型响应投影，资源与输出上限已预约 | 热图生成失败仍保留主推理结果并标 `ExplanationNotProvided`；不得用文字生成器补解释 |
| 设备发现/查询 | `query_available_dl_devices(GenParamName, GenParamValue)`、`get/set_dl_device_param`；AsunImage `HDlDevice.QueryAvailableDlDevices/GetDlDeviceParam/SetDlDeviceParam` | 仅查询和核对实际设备/运行时；设备空闲和预算仍由外层资源 Owner 预约 | 无设备时返回 `BackendUnavailable`；不得把 GPU 0、设备名称或查询成功当作可运行许可 |
| 模型释放 | `clear_dl_model`；AsunImage `ClearDlModel`/确定性 Dispose | 活动调用、输出借用和内容租约全部排空后才清理 | 排空未知时隔离实例/进程，不直接清理可能仍被 native 使用的句柄 |

路线选择固定为：先判断 HALCON 26.05 是否覆盖任务和输出；覆盖则优先 AsunImage 公共适配器；不覆盖时记录缺口，再比较已登记的外部适配器。外部适配器必须提供独立输入/输出 schema、版本/commit、许可证、取消/资源边界和回退路线；没有这些证据时返回 `Rejected/AdapterNotReady`，不允许“先接再补文档”。训练算子（包括 `train_dl_model_batch`）不属于本模块适配路线；训练、checkpoint 恢复、模型选择和发布由调用应用协调各自 Owner，本模块只接收新建且已封存的精确模型闭包。

### 2.3 按任务类型的具体适配路线

| 任务类型 | 首选路线 | 后处理/证据要求 | 备用与明确不支持 |
|---|---|---|---|
| 单标签分类 | 已冻结分类模型时使用 `read_dl_model` + `apply_dl_model`；若资产明确是 HALCON DL classifier，可用 `HDlClassifier.ApplyDlClassifier(HImage)` | 核类表、score 语义、完整/截断分布和拒识；不默认 softmax 或把最高类当业务结论；分类解释仅按 §2.5 独立执行 | 只能切换批准的同模型后端/精度或由宿主走确定性替代；不在本模块重写 SVM/LUT 等经典分类器 |
| 多标签分类 | 通用 `apply_dl_model`，按输出字段解析每类分数 | 保留未返回类与阈值版本，多标签不强制和为 1 | 无已批准替代则返回拒识；不将缺类填 0 后交给调用方当事实 |
| 目标检测/实例分割 | 通用 `apply_dl_model`；检测/实例分割模型的输入输出字典和 NMS/掩码定义随模型闭包 | 先校验输出结构/类/坐标，再按模型定义做反坐标、NMS、tile 合并；记录抑制和截断来源 | 同模型批准的 CPU/GPU/精度变体；不把二维候选推成内部缺陷或物理尺寸 |
| 语义分割/异常热图 | `apply_dl_model` 直接返回分割/异常任务输出；不调用分类解释算子替代 | 概率/类别网格、有效域、padding、tile 覆盖和输出版本独立记录；热图不是因果解释或量测 | 必需图缺失属于输出不完整/失败，不能以解释可选为由忽略；不以 `max` 跨 tile 伪造全局异常，不由本模块编写 variation/计量替代算法 |
| Embedding/相似度 | `apply_dl_model` 获取已声明维度和数值语义的向量 | 记录模型/归一化/度量版本和输入身份；向量结果只作对照候选 | 不跨模型直接比较、不作身份认证/设备命令；无资格时仅返回原始向量或拒识 |
| OCR 对照 | 只有通用模型闭包和用途批准时走 `apply_dl_model`/已登记外部适配器；专用 `HDlModelOcr.ApplyDeepOcr` 仍归 OCR 模块 | 返回原读/框/分数及模型版本；字符词典、语法、期待值比较由调用方 | 没有对照资格则 `AdapterNotReady`；不在本模块训练字符模型、规范化文本或决定内容正确 |

每条首选路线都必须有”输出结构完整但候选为零”和”输出结构无效/不完整”两个不同测试。备用路线只在表中条件成立时由调用方显式选择，且生成新的 attempt/ref；本核心永不自动把备用路线结果覆盖主路线结果。

表中旧 `HDlClassifier`、外部适配器及 `transform_dl_sample_batch` 是能力比较/备选来源，不是已批准首版的第二执行实现。当前产品适配范围唯一为附录 C 的 `read_dl_model → apply_dl_model` 主链，旧 classifier/专用 Deep OCR 不自动转入；需要扩展先修订本指导、输入输出与验证切片。参数推荐、训练、优化/精度转换由离线资产及用途 Owner 完成，本模块只显式执行冻结变体，不提供搜索、推荐或生产参数写入 API。Core 的可合批端口与相应 Simulator 反例保留；首版真实 HALCON 装配严格不跨请求合批，不因 Core 能表达该能力而启用。

### 2.3B ONNX Runtime 推理路线（第二适配器，与 HALCON 适配器并列）

#### 2.3B.1 设计动机与定位

HALCON 26.05 的深度学习支持成熟，但有以下场景 ONNX Runtime 优势更明显：
- 需要使用 RT-DETR、anomalib PatchCore、EfficientAD 等 HALCON 未原生支持的架构
- 工控机为 Intel CPU + 核显，ONNX Runtime OpenVINO EP 通常比 HALCON 快 1.5-3×
- 训练侧用 PyTorch/anomalib，ONNX 是天然的标准导出格式，避免额外转换

本路线与 HALCON 适配器**并列**，不替代。每个推理请求按模型闭包的 `InferenceBackend` 字段选路由，一个宿主可同时装载两个适配器。

#### 2.3B.2 三路 EP（Execution Provider）选择策略

| EP | 适用硬件 | 性能特征 | 选择条件 |
|---|---|---|---|
| **CPU EP** | 任意 | 稳定，延迟稍高 | 默认；无 GPU 或 GPU 显存不足时 |
| **CUDA EP** | NVIDIA GPU | P95 延迟降低 50-70% | 用途 Profile 允许 GPU；`query_available_dl_devices` 确认可用 |
| **OpenVINO EP** | Intel CPU/核显 | 在 Intel 平台通常最快 | 检测到 Intel iGPU/CPU；`IntelHardwarePresent=true` |

**EP 探测顺序**（每次宿主启动时执行一次，结果缓存）：
1. 尝试初始化 CUDA EP → 成功且 `GpuMemory >= minGpuMemoryMb` → 选 CUDA EP
2. 否则尝试 OpenVINO EP → 成功 → 选 OpenVINO EP
3. 否则回退 CPU EP

探测失败不是错误，只是降级；每次降级记录诊断事件。EP 选择结果写入模型实例的 `ActiveEp` 字段，不可在推理中途切换。

```csharp
public enum OnnxExecutionProvider { Cpu, Cuda, OpenVino }

public sealed record OnnxAdapterOptions(
    OnnxExecutionProvider PreferredEp,
    int MinGpuMemoryMb = 2048,
    int IntraOpNumThreads = 0,      // 0 = 让 ORT 自动选择
    int InterOpNumThreads = 0,
    bool EnableMemoryPattern = true,
    bool EnableCpuMemArena = true);
```

#### 2.3B.3 推荐模型及许可证

| 缺陷类型 | 推荐模型 | 许可证 | 说明 |
|---|---|---|---|
| 外观异常（划痕/氧化/污染） | **PatchCore**（anomalib） | Apache-2.0 ✅ | 无监督异常检测；无需大量标注；工控最优解 |
| 外观异常（更快推理） | **EfficientAD**（anomalib） | Apache-2.0 ✅ | 轻量；工控机 CPU 可实时 |
| 桥连/偏移/缺件/错件 | **RT-DETR**（百度/PaddleDetection） | Apache-2.0 ✅ | 无 NMS；精度接近 YOLO11；商用无风险 |
| 极性/型号分类 | **ConvNeXt-Tiny / EfficientNetV2-S** | Apache-2.0 ✅ | 轻量；适合工控机 |
| 字符识别 | **PP-OCRv5**（PaddleOCR 3.x） | Apache-2.0 ✅ | 优先走 `ocr` 模块；OCR 对照场景才接入本模块 |

> ⚠️ **YOLO 系列（Ultralytics）= AGPL-3.0**，闭源部署有传染风险。本平台统一用 RT-DETR 或 YOLOX（Apache-2.0）替代，禁止直接引入 AGPL 模型。

**anomalib PatchCore 的 ONNX 导出步骤**（记录于 `ai-dataset-governance` 指导，此处只列调用方要求）：
- 导出时固定 `batch_size=1`，`image_size` 与训练时相同
- 导出后用留出集验证 ONNX 输出与 PyTorch 输出数值等价（最大差 < 1e-4）
- ModelCard 记录 `onnxOpset`、`anomalyMapShape`、`normalizationMean/Std`

#### 2.3B.4 Tiling（大图分块推理）

工业相机分辨率可达 20000×30000，直接输入模型会爆内存。标准做法是 Tiling + ROI 级推理：

```
原图（大）
  ↓ roi-geometry 模块产出 ROI 坐标列表
  ↓ image-frame 模块产出 tile 张量（按 ROI 裁切 + resize）
  ↓ ai-inference 模块对每个 tile 推理
  ↓ 结果合并（NMS / grid-merge / anomaly-map 拼接）
  ↓ 逆变换回原图坐标（coordinate-geometry 模块）
```

**推理模块的边界**：
- 只处理已切好的 tile 张量，不自行裁切大图
- 坐标逆变换由 `coordinate-geometry` 模块完成，不在推理模块内计算
- 结果合并策略（NMS/grid-merge）由用途 Profile 的 `tileMode` 指定

#### 2.3B.5 C# 调用骨架

```csharp
// ONNX Runtime 推理适配器接口（与 HALCON 适配器共用 IInferenceAdapter）
public interface IInferenceAdapter
{
    OnnxExecutionProvider ActiveEp { get; }

    Task<RawInferenceOutput> RunAsync(
        ImmutableArray<TensorInput> inputs,
        CancellationToken ct);

    ValueTask DisposeAsync();
}

// ONNX Runtime 实现（实际在 Asun.Modules.AiInference.OnnxAdapter 程序集）
internal sealed class OnnxInferenceAdapter : IInferenceAdapter
{
    private readonly InferenceSession _session;   // Microsoft.ML.OnnxRuntime
    public OnnxExecutionProvider ActiveEp { get; }

    public OnnxInferenceAdapter(string modelPath, OnnxAdapterOptions options)
    {
        var sessionOptions = BuildSessionOptions(options, out var ep);
        _session = new InferenceSession(modelPath, sessionOptions);
        ActiveEp = ep;
    }

    public async Task<RawInferenceOutput> RunAsync(
        ImmutableArray<TensorInput> inputs,
        CancellationToken ct)
    {
        // 1. 构建 OrtValue 输入
        // 2. 在线程池上异步运行 _session.Run(...)
        // 3. 转换输出为 RawInferenceOutput
        // 4. 所有 OrtValue 在使用后确定性 Dispose
        throw new NotImplementedException(“按 §8 样例实现”);
    }

    private static SessionOptions BuildSessionOptions(
        OnnxAdapterOptions options,
        out OnnxExecutionProvider activeEp)
    {
        var so = new SessionOptions();
        so.IntraOpNumThreads = options.IntraOpNumThreads;
        so.InterOpNumThreads = options.InterOpNumThreads;
        so.EnableMemoryPattern = options.EnableMemoryPattern;
        so.EnableCpuMemArena = options.EnableCpuMemArena;

        // EP 探测：依序尝试，失败则降级
        if (options.PreferredEp == OnnxExecutionProvider.Cuda)
        {
            try
            {
                so.AppendExecutionProvider_CUDA();
                activeEp = OnnxExecutionProvider.Cuda;
                return so;
            }
            catch { /* 降级 */ }
        }
        if (options.PreferredEp is OnnxExecutionProvider.OpenVino
                                or OnnxExecutionProvider.Cuda)
        {
            try
            {
                so.AppendExecutionProvider_OpenVINO();
                activeEp = OnnxExecutionProvider.OpenVino;
                return so;
            }
            catch { /* 降级 */ }
        }
        activeEp = OnnxExecutionProvider.Cpu;
        return so;
    }

    public async ValueTask DisposeAsync()
    {
        _session.Dispose();
        await Task.CompletedTask;
    }
}
```

#### 2.3B.6 NuGet 依赖

| 包 | 版本约束 | 用途 |
|---|---|---|
| `Microsoft.ML.OnnxRuntime` | ≥ 1.18.0，精确锁定 | CPU EP |
| `Microsoft.ML.OnnxRuntime.Gpu` | 与上同版本 | CUDA EP（可选，条件编译） |
| `Microsoft.ML.OnnxRuntime.Extensions` | 与上同版本 | 预处理算子扩展 |

精确版本在 `Directory.Packages.props` 中锁定，不用浮动范围。CUDA/OpenVINO EP 包通过条件编译 `$(EnableGpuEp)` 控制是否引入，避免工控机无 GPU 时部署包含无效 native 库。

### 2.4 模型训练、备用和恢复的准入

- **训练**：本模块只消费已封存的模型闭包；训练由外部数据/治理模块完成。训练交接必须包含数据集与真值版本、预处理/类表、随机性、训练配置、checkpoint、留出集指标、阈值/校准依据和导出/转换报告。缺一项只能 `ModelNotReady`，不能在推理时补训练。
- **备用模型/后端**：备用是事先批准的方法变体，必须绑定自己的模型/预处理/后处理/资格和实例 key。只有主路线明确返回可重试的 `BackendUnavailable`/`BudgetUnavailable` 且用途 Profile 允许时，调用方才可另建 attempt 使用备用；不得由核心静默切换。
- **恢复**：参数或模型错误先修订配置并生成新计算身份；native 失败保留原 attempt 和原始输出/错误，批准重算时生成新的计算身份；提交回执丢失只查询原操作。OOM、设备丢失或宿主崩溃先停止实例新准入并隔离，确认 native/进程终止后才释放资源。
- **不支持**：本模块不训练、不自动选模型、不做在线学习/continual learning、不把热图变成因果解释、不从 2D 候选推断 3D 或物理量、不把模型 score 转成质量判定，不提供隐式安全回退。

### 2.5 HALCON 26.05 的分支、固定参数与解释限制

所有下列算子均通过 `ImageLibDotNet.cv2`；本轮直接读取本项目对应 HTML 的 Description、Attention、参数与执行说明，不读取封装内部。主路线是精确 `.hdl` 模型 → 按闭包设置并读回运行配置 → `apply_dl_model` → 任务解码。HALCON 可导入的 ONNX 仍走同一路线；超出 `read_dl_model` 导入支持时才进入已登记外部后端。不得让开发者按模型扩展名临时切后端。

| 决策点 | 已核语义、主分支与参数 | 错误/备用与验收 |
|---|---|---|
| `.hdl`/ONNX 装载 | `read_dl_model` 支持两种格式；本地26.05页面规定 ONNX 保证范围到 opset 13、32-bit float tensor、图像输入4维；SoftMax结尾才自动识别 classifier，其余为 generic。模型读取后 runtime-specific 参数恢复默认，不能当原部署配置 | ONNX 超范围/不支持层不尝试改图或冒称可运行；按原注册外部适配路线单独验收。设置并读回 `type/image_width/image_height/image_num_channels/batch_size/device` 及实际 precision，不支持值返回 `AdapterNotReady` |
| 批次与峰值 | `apply_dl_model` 少于 `batch_size` 时补满，时间/模型内存仍按完整 batch；多于该值内部多批。Core 分组上限与配置 batch 分别记录，预算按 configured batch 估算 | 单 item 不按 1/batch 均摊显存；执行前检查临时/native/GPU 峰值。若短批也超预算拒绝，不热改 batch；比较单项/短批/满批及换同伴输出 |
| 输出清单 | `Outputs=[]` 返回该模型可用全部输出，不能用空清单保证小载荷；正式闭包声明必需输出名、shape/类型和上限。分类/多标签原生默认输出采用空 tuple 时，须完整校验并计预算 | 缺必需键、类表或关系失配是 `OutputSchemaMismatch/OutputAssociationLost`；合法零候选与空字典不同。AI² 输出层在优化前按页面要求设置 `is_inference_output` |
| 预处理 | `transform_dl_sample_batch` 可改尺寸/范围及数据增强；当前注释传播只支持 detection（含 instance segmentation）相关键。生产只用冻结的确定变换，不启用随机增强 | 不据该算子名称假设分类/语义 mask 自动传播；对应 mask 和逆变换由 §6.3 规范负责。resize/通道/数值范围改变不得现场修改模型权重 |
| 精度优化 | `optimize_dl_model_for_inference` 仅 AI²；支持值依设备，可包括 bfloat16/float32/float16/int8；代表性 calibration 数据、device GenParam 和 ConversionReport 归新闭包 | 优化在离线模型资产流程进行，不在 Infer 内运行；转换后可改参数受限，不现场修改架构/batch。手册10–20样本/类建议不迁为平台资格门。原模型与派生模型在同一挑战集比较阈值附近、弱信号和资源 |
| 分类解释 | `gen_dl_model_heatmap` 仅 classification 模型（不用于 generic/多标签/分割/异常图替代）；需 backward-pass 的训练级资源能力。允许 `grad_cam/guided_grad_cam`，target 单 class ID 或空 tuple=top class；方法、target 与 scaling 写入闭包 | 主推理输出与独立解释字典分开保存，不覆盖 DLResult。资源未预约、模型不支持或生成失败标 `ExplanationNotProvided`，保持主推理结果；解释不改变候选/拒识。热图不是分割或因果量测 |
| 异常/分割图 | anomaly 的图与整图 score、segmentation 的 `segmentation_image/segmentation_confidence` 来自 `apply_dl_model` 对应任务输出 | 不用分类 Grad-CAM 生成“异常量”；类别网格是 class ID，不当连续强度插值；有效域/未知像素单独编码 |
| 设备、预热与释放 | `query_available_dl_devices/get_dl_device_param` 是能力查询，不是空闲证明；先预算再设置实际设备。`runtime_init` 有条件限制，预热用冻结 shape/batch 的实际空生产副作用执行并记录是否完成 | 同一物理设备可能有多个接口 handle；以实际设备/runtime身份及外层预算控制。`clear_dl_model` 在该实例全部活动租约排空后执行，读回配置/预热成功不等于现场性能通过 |

粗精路线由任务 Owner 先用确定性定位产生有来源的 ROI，再由本模块按原分辨率域推理；没有可信 ROI 时只允许该闭包批准的全图或 tile 路线。低分/遮挡不自动缩图、扩 ROI、补纹理或放宽阈值；请求拒识由宿主选择补采/人工/已验证确定性方法。参数推荐属于离线用途/资产 Owner：仅枚举已允许的 shape/batch/precision 变体，固定数据与顺序，逐项报告输出差异、拒识、P50/P95/P99及峰值；未实测只返回 `NotEvaluated`，不自动发布。模型阈值/NMS/类表/预处理无模块全局经验默认。

## 3. 公开调用契约

本节的模块 Core 字段、方法和生命周期由附录 A 的 `Module API Contract v0.3` 统一冻结；它是无产品事实写入的模块级契约，Core/Simulator 六项文档规格已由主会话接收，达到 `ModuleCoreImplementationReady`（规格准备）。平台 C-01～C-08 映射、跨进程序列化、持久化 Schema、错误码传输编号、用途资格和生产 Profile 仍由外部 Owner 采纳。实现者不得把平台候选 DTO 反向塞入 Core，也不得另造第二套 Core DTO/状态机。

### 3.1 请求字段

| 字段 | 类型/单位 | 校验与范围 | 默认值/来源 |
|---|---|---|---|
| `requestId` | 不透明稳定字符串 | 必填；本实例生命周期内唯一；ordinal 大小写敏感比较，长度受 EngineOptions 限制 | 无默认；调用方生成 |
| `consumerId` | 不透明标识 | 必填；绑定调用方注册身份，不从 UI 文本推断 | 无默认 |
| `purpose` | 封闭版本化用途码 | 必填；只接受授权端口允许值；用途及资格由外部 Owner 决定 | 无默认 |
| `attemptRef` | 类型化身份引用 | 必填；保留原操作/计算尝试关联，不由图像摘要代替 | 无默认；调用方/运行 Owner 提供 |
| `modelRef` | 精确资产引用 + 内容摘要 | 必填；不可为空、不可解析 latest；整个依赖、类表和预/后处理闭包须可校验 | 无默认；资产 Owner 提供 |
| `taskKind` | 版本化字符串 token（分类、多标签、检测、语义/实例分割、异常、embedding 等） | 必填且必须与模型闭包输出契约相符；OCR 依 2.1 边界；Core 不用不可扩展的 C# 业务枚举代替闭包声明 | 无默认；资产闭包声明 |
| `inputs[]` | 有序item引用 | 数量 `1..MaxItems`；稳定 `itemId` 不重复；每项Values含明确Name、来源、像素/张量类型、shape、stride/layout、通道语义、ROI/有效域及坐标变换引用 | 无默认；`MaxItems` 由部署 Profile 明确，未配置不得接收 |
| `preprocessRef` | 版本化不可变规范引用 | 必须与模型闭包绑定；像素类型、位深、通道、范围、缩放/填充/插值均明确；数值有限 | 无默认，不运行隐式归一化 |
| `postprocessRef` | 版本化不可变规范引用 | 输出种类、score 语义、类表、阈值/NMS/合并/截断/拒识规则显式且与任务相符 | 无默认；未配置只允许原始诊断适配，不得产出可消费候选 |
| `backendPolicy` | 本 attempt 选定的后端/设备/精度/runtime 引用 | 仅一个显式路线；必须核实际配置与所选路线一致；禁止静默切换 | 无默认；用途 Profile 提供 |
| `batchPolicy.maxItems` | 整数，项 | `1..ConfiguredMaxBatch` 且不超过后端与内存预算；本请求上限受部署 Profile 限制 | 建议默认 `1`；更大值须 Profile 明确 |
| `batchPolicy.maxWait` | `TimeSpan`，毫秒 | `0..deadline余量`；单调时钟计时，不可超过请求 deadline 扣除已验证执行/后处理预留 | 默认 `0 ms`，即不为凑批等待 |
| `deadline` | 单调时钟截止 + 可诊断 UTC 对照时间 | 必填；剩余时间须大于 0；UTC 不用于超时判定 | 无默认；调用方传入剩余预算 |
| `resourceBudget` | 分维度字节/并发/时间上限 | 队列/CPU 并发为正数；输入、临时、输出/native/GPU 字节为非负有限上限（0 禁用该资源维度）；不得用一个总数互相抵扣 | 无默认；执行 Owner/部署 Profile 供给 |
| 取消信号 | `CancellationToken` 方法参数 | 每次调用独立；只表达本调用者取消，不作为请求 DTO 字段、共享实例或共批全局开关 | 调用方提供；取消能力受适配器真实支持约束 |
| `traceContext` | 可选追踪关联 | 有长度上限，不得含敏感图像/客户明文 | 默认无 |

上表不是阈值来源。任何模型阈值、缺陷尺寸、OOD、质量置信线或工业负载绝不设模块全局默认；由对应已验证任务 Profile 提供。没有 Profile 的字段不得用拍脑袋的数值填补，可定义明确部署必填项。整数维度/乘积使用 checked 算术；拒绝负维、溢出、非有限数、零元素（除非该任务规范明确声明空输入合法）和越预算输入。

### 3.2 输出字段

每个已接纳请求有一个最终结果。Core 固定传输附录 A 的 `InferenceResult`、`InferenceItemResult` 及其状态、摘要、完整性和诊断字段；每项保留 `itemId` 与原序号，任务 Schema 的候选/拒识载荷通过 `CanonicalOutput` 承载。实际后端、runtime、generation、configured/submitted batch及执行测量由 `Executions` 承载，Core 阶段测量由 `Observations` 承载；输入解释、实际预处理 shape/layout、有效域/坐标变换、缺项/截断明细由绑定的任务 Schema 承载，诊断不代替必需结构；“候选数组”只是该任务 Schema 的投影。预接纳拒绝没有实际后端或设备，附录 A 对应字段返回 `null`，而不是伪造 provider/device 字符串。

候选只表达模型输出，必须标明 taskKind 对应的数据形态、类别 ID/类表版本、分数数值和语义（概率/未校准 score/距离/异常量），以及适用的原图坐标或输出网格坐标。需要概率但未经校准时明确标为未校准；不适用的置信、OOD、解释字段用显式 NotProvided/NotApplicable，不伪造 0。低分或域外拒识是有效的模型结果；结构非法、NaN/Infinity、未知类别或坐标无法恢复属于执行失败。

合法零候选只允许在输入和输出结构有效、必需输出完整、支持域和方法范围满足、无截断/缺 tile、后处理成功时产生。空候选不等于良品或质量 PASS。

### 3.3 同步与异步入口

模块异步入口和完整签名由附录 A 冻结；本模块不提供同步推理入口，以免调用者把 native/GPU 工作放到 UI 或持锁线程。纯请求校验是无副作用同步操作。所有推理调用均复用相同的请求、结果和状态语义。

唯一签名见附录 A.1；端口及工厂签名见 A.4，不在正文复制第二套接口。

`Validate` 仅执行有界纯字段/引用校验，不读取图像、不载入模型、不预约执行资源。`InferAsync` 执行完整请求。`QueryAsync` 只查询本引擎实例已接纳的 operation；未知 ID 返回 `NotFound` 状态，不猜测为已完成。`DrainAsync` 的线性化点停止本实例接纳新工作；线性化点前已发出 `RequestAccepted` 的请求继续排空，之后的请求返回 `AdmissionStopped`，并返回逐请求排空回执。`DrainAsync` 的调用方取消只取消等待，不取消 operation 或提前释放资源。释放实例前必须等回执证明所有资源已归还。`DisposeAsync` 只允许在 Drain 完成后调用；提前调用返回 faulted `ValueTask` 并保留未排空资源，不得静默 Dispose native 句柄。

异步入口在接纳前完成纯参数校验和预算预约。预接纳错误返回 `Rejected` 结果；已接纳请求最终只产生一个终态 `InferenceResult`。传入 `InferAsync` 的 `CancellationToken` 只表达该 operation 的取消请求；token 不写入请求快照、输入、缓存 key 或结果事实。引擎在真实 native 排空后才返回 `Cancelled`/`TimedOut`。调用者若只想停止等待，应直接放弃等待而不取消该 token，operation 仍可通过 `QueryAsync` 查询并继续排空；`QueryAsync`/`DrainAsync` 的 token 只取消查询等待，不改变被查询 operation。其他预期的校验、后端、超时和排空错误不得以异常代替终态结果。异常只用于调用方违反 API 前置条件或宿主在接纳前发生的不可恢复故障，且此时不得伪造 operation 终态。本实例拒绝已登记的 requestId，返回调用级 `Rejected/DuplicateRequest`，不启动第二执行、不发送原 operation 的生命周期事件、不改原结果；预接纳拒绝的 ID 未登记，可在修正参数后再次提交；重读用 `QueryAsync`，新计算用新 ID。跨进程幂等由宿主 Owner 处理。事件是观察投影，不是结果真值或提交回执。

### 3.4 可信宿主、查询身份与用途检查边界

一个引擎实例只属于一个可信宿主安全主体/租户，构造时绑定 `EngineOptions.TrustedConsumer`，由宿主已认证装配根提供。Infer的Consumer必须ordinal逐字段等于该引用；PurposeGate接受的TrustedConsumer来自options，绝不来自调用方可改request/trace。引擎对象、Query/Drain引用和诊断端口只可交给该主体的可信代码；requestId不是凭证。多用户/多租户服务必须在宿主完成认证并为每个安全主体建立独占engine/gate/backend，不能把一个engine直接暴露成共享RPC。若需跨主体查询，须另立获批authority/查询上下文切片，本契约不声称支持。

Query对NotFound/非终态只返回可信宿主可见的安全状态，Result=null，不启动披露IO；DrainReceipt.Operations始终Result=null，只含安全状态/诊断，不能通过Drain绕过披露检查。Query仍只接requestId；它重新检查的是**同一可信主体的当前用途资格**，不识别任意新的调用者。已登记request不可变，Check同时携带构造绑定主体、原request、Execute/FinalDisclosure/QueryDisclosure阶段、实例单调CallId及本地deadline。撤权不改变原终态；Query返回原State/TerminalState、Result=null和PurposeNotAllowed。用途IO及关闭严格按 §5.2；不以token取消证明IO结束。

## 4. 状态、事件顺序与错误语义

状态语义分为两条路径：预接纳拒绝为 `Validating → Rejected`，不保留预算/队列 reservation，不取得模型、输入或 native 资源，也不发 `Draining/Drained` 事件；已接纳请求为 `Validating → WaitingForBudget → Queued → Preparing → Running → Postprocessing → Draining → Drained → ResourcesReleased → Completed | Partial | Rejected | Failed | Cancelled | TimedOut | ExecutionUnknown`。`ExecutionUnknown` 只有在 native/隔离 worker 已真实退出且资源已释放、但结果事实仍不可确定时才能作为终态；排空未完成期间只使用 `DrainPending` operation 状态，并通过 `CancelRequestedNativeRunning`/`TimedOutExecutionUnknown` 诊断观察，不发布终态结果。此为模块局部执行投影，不替代平台 Contract/State。

事件顺序：

1. 未接纳请求先发 `RequestReceived` → `RequestRejected` → `RequestTerminal`（参数错误带 `InvalidRequest`）；不取得模型、输入或 native 租约，临时预算/队列 reservation 在返回前归还，不伪造 `Draining/Drained/ResourcesReleased` 事件。该路径 `ResourcesReleased=true` 表示没有保留资源，不登记 operation。已登记 requestId 的重复调用仅返回调用诊断，不发送这些生命周期事件、不修改原 operation 或结果。
2. `RequestValidated`；校验通过后才进入接纳路径。
3. `RequestAccepted`；只在预算/队列名额已预约后发出。
4. `StageStarted`/`Progress`；进度可合并，阶段为等待、准备、输入绑定、执行、后处理、排空。
5. `ItemCompleted` 或 `ItemRejected`；带稳定 itemId 和原序号，可按 item 部分完成；无法可靠映射输出则整批失败。
6. `DrainStarted` → `Drained` → `ResourcesReleased`；`Drained` 证明本请求 native 已停止、请求级 native 输出/临时资源已归还且 backend lease 已成功 Dispose；随后输入/模型内容租约及预算全部归还才发 `ResourcesReleased`。实例缓存驻留由实例关闭尾段另外释放，不伪装成请求资源。
7. `RequestTerminal`；最后且恰好一次，携带终态、结果摘要/错误及排空标记。

诊断接收器OnEvent须有界非阻塞；Core以MaxDiagnosticEvents限制分发队列，满时可丢观察并保留受限InternalFailure诊断，结果/排空不得等待观察者完成。关闭时停止分发并丢弃余留观察；已进入的回调仅持不可变安全投影，不持native/lease，不以任意慢回调阻断backend释放。事件发送器不得在持有内部锁、持久写锁或原生资源锁时被调用；订阅者异常隔离并记录，不可改变调用结果。InferenceEvent.Sequence为实例内全局单调序号，StateRevision为已登记operation的单调修订；预接纳观察StateRevision=0，通过全局Sequence区分同ID的不同拒绝调用。事件传输可重复/丢失，消费者按实例身份、requestId、状态修订和序号去重；最终返回值或原 Owner 的提交回执才是事实来源。

错误使用本指导固定的稳定模块级分类和机器可读码；传输层前缀/数值映射由外部 Contract Owner 另行绑定。必须区分：`InvalidRequest`、`DuplicateRequest`、`EmptyInput`、`ModelNotFound`、`ModelIntegrityMismatch`、`ModelNotReady`、`PurposeNotAllowed`、`InputShapeMismatch`、`InputFormatUnsupported`、`InputQualityInsufficient`、`BudgetUnavailable`、`QueueFull`、`AdmissionStopped`、`DeadlineExceededBeforeStart`、`BackendUnavailable`、`BackendExecutionFailed`、`OutputSchemaMismatch`、`OutputNumericallyInvalid`、`OutputAssociationLost`、`PostprocessFailed`、`CancelledBeforeNative`、`CancelRequestedNativeRunning`、`TimedOutExecutionUnknown`、`ResourceDrainFailed`、`AdapterNotReady`、`ExplanationNotProvided`、`InternalFailure`。其中 `CancelRequestedNativeRunning`、`TimedOutExecutionUnknown` 是排空期间的诊断/观察码，不是终态错误；`CommitUnknown` 不属于本模块错误：提交端口的未知回执由外部 Owner 持有，不改变本模块 operation 状态或终态。错误包含是否可重试、实际阶段、请求/item 关联、公开安全诊断和内部相关 ID；重试属性不可单独授权重试。附录 A 的 `InferenceDiagnostic.Code` 使用这些 token；未知 token 只能作为 `InternalFailure` 的受控原生细节，不能由适配器自定义第二套业务错误码。

低置信拒识、未提供 OOD、必需输出缺项和截断分别是可识别结果语义或不完整结果，不混成程序异常，也不转成空候选成功。应用根据自身政策决定后续处置。`InferenceResult.ResourcesReleased=true` 是终态结果的必要条件；预接纳拒绝不保留资源，临时 reservation 已归还，按“无资源需释放”处理并置为 `true`。

## 5. 并发、取消、超时、资源和排空

backend.RequestCancel必须线程安全、有界非阻塞，仅登记/转交本请求的中断意图，不等待native结束；Drain/StopAndDrain的等待预算非负且禁止无限值，等待token只取消本次等待，重复调用共享原排空操作。默认每个可变后端模型实例串行执行；不同实例是否可并行取决于实例隔离和外层预算验证。HALCON reentrant 不代表同一个可变 handle 能任意并发调用。预处理只读不可变输入可并发，但必须受 worker/内存上限控制。UI 调用方只从宿主线程订阅投影，不把 Dispatcher 带入核心。

队列同时限制请求数、item 数、输入驻留字节、暂存张量字节和预计输出字节。先预约队列名额与声明的最坏资源额度再接纳入队；输入租约在接纳后的准备阶段取得，预约额度须覆盖其保持期，不提前读取图像；不得无限创建等待 Task。批次按闭包、预/后处理、任务、实际后端/精度、shape、用途隔离域和取消策略兼容。达到满批、等待上限、后续项不兼容或 deadline 不足时提交短批；禁止无限等凑批。

取消按以下阶段执行：

- 接纳前：返回 `Rejected/CancelledBeforeNative`，不保留资源；接纳后未运行：记录取消意图并走统一排空终态。
- 已排队未进入 native：在队列一致性边界移除该 request 的全部未开始 item，确认移除后释放其输入/预算。
- 已进入 native：调用适配器经证实支持的中断；若底层不可抢占，只记录取消请求并继续持有模型、输入、输出、设备及预算租约，直到 native 确认完成/停止或隔离进程退出。
- 后处理/提交：取消只影响尚未完成的本次计算观察。已交付给事实 Owner 的提交按其原回执查询，不撤销成功事实、不换键重跑。

公开取消粒度是 request（该请求全部 item），不提供未定义的逐 item token；取消 request A 不得中止共批 request B 或共享模型加载。Task 超时、`CancellationToken` 被触发、UI 关闭或等待者放弃都不证明 native 已停止。deadline 到期但执行仍不确定时，`QueryAsync` 返回可查询的 `DrainPending` operation 状态，并带 `TimedOutExecutionUnknown` 诊断；`InferAsync` 不发布结果，调用方可放弃等待而不取消该 token。operation 保持 `Draining/DrainPending`，不得发布 `ResourcesReleased` 或 `RequestTerminal`。只有原生调用真实退出，或隔离 worker/资源 Owner 提供可信释放证明后，才发 `Drained → ResourcesReleased`；结果未知时终态 `ExecutionUnknown`，已知超期/取消时分别 `TimedOut`/`Cancelled`。调用方取消 `QueryAsync`/`DrainAsync` 只取消查询等待，不改变被查询 operation。

资源所有权按成功、失败、取消、OOM、设备丢失和宿主关闭全路径定义。后处理不接收借用的 Span、HALCON/native 句柄或可被提前归还的池缓冲。释放顺序为：确认最后使用结束 → 释放请求原生输出/临时缓冲和backend lease → Drained → 归还输入/模型内容租约与 budget → ResourcesReleased → 递减活动调用 → 允许实例驱逐；失败保留未释放分量，不跳过释放证明。模型实例驱逐必须等待活动推理和输出借用全部排空。禁止依赖 finalizer 代替确定性释放。

### 5.1 调度、取消线性化与终态归约

Core 的 FIFO key 为接纳单调序号（同序不可能）；每实例可变模型串行，实例并行由预算限定。请求内 item 按 Sequence 从0连续、同ID唯一；队头兼容项形成批次，遇不兼容项或配置上限发短批，不扫描队尾无限跳过大请求。宿主可按用途分别创建引擎隔离 shadow 和在线负载，不在 Core 引入板/FOV优先级。backend 合并多个请求仅在同模型闭包、runtime/device/precision、shape/layout/optional输入集合、pre/post/schema/用途隔离域与取消能力相同且同伴替换不改变已验证结果时允许；无这项资格默认不跨请求合批，保留完整请求内批处理能力。

批次截止为 `min(首项进入组批时刻 + MaxWait, 最早请求 deadline - 该冻结负载的执行/后处理/排空预留)`；预留来自已采纳 runtime Profile，无可信预留时 MaxWait 必须为0并立即短批，不用过去平均时长猜P99。不延长请求 deadline；进入 native 前再次检查过期/撤权/代次。HALCON 配置 batch 的补满资源始终由 §2.5 计入，不把计划短批大小当真实模型内存。

取消在 Core 锁下首次登记意图，RequestCancel 在锁外调用；native completion 与取消/deadline只竞争终态意图，不竞争资源释放。先注册停止意图后尚未发布 terminal 的 request，其后成功输出不得变成 Completed；所有路径仍需排空。cancel 和 deadline 均发生时按最早单调时刻，完全同时按 deadline；terminal 已发布后取消不改事实。后端响应明确失败（NaN/错误schema/设备失败）保留失败诊断，不能被取消掩盖；存在真实执行而结果不可确定时最终 ExecutionUnknown 优先，其次 Failed，其次已登记的 TimedOut/Cancelled，其次结果归约。

结果归约：全部 item Completed 且完整且未截断为 Completed；完整的低信/OOD拒识 item 不是执行失败，允许保留结构有效的诊断载荷且标 Rejected，混合 Completed/Rejected 而全部处理完整仍为 Completed（下游须看逐项状态）；全部拒识为请求 Rejected 且 OutputComplete=true。可定位缺项/失败或截断而存在有效 item 为 Partial/OutputComplete=false；无法关联、结构坏或全无可用结果为 Failed。Missing/Unknown/Cancelled/Failed 不带可消费载荷，完成零候选须满足 §3.2。统一在 ResourcesReleased 后发布 terminal；事件 ItemCompleted 是暂存 item 投影，不允许下游提前放行。

取消前置 token 已取消且未接纳 → Rejected；已接纳但未运行 → Draining（无native即无需等待）→ Drained→ResourcesReleased→Cancelled；deadline已过且未接纳 → Rejected/DeadlineExceededBeforeStart；已接纳后超期 → 同一排空尾段→TimedOut。Draining 可进 DrainPending，再回 Draining/Drained；失败可从 Queued/Preparing/Running/Postprocessing 任一阶段跳 Draining，不能强行发未执行 Running/Postprocessing。ExecutionUnknown 仅为释放后的结果不确定，不作正在运行的状态名。

后端 Generation 由实例 adapter 管理且单调变代；输入与模型采用内容引用/租约身份，不另猜 DTO 中不存在的 input generation；Core 对 request ID +实际 Generation+闭包/raw schema核回执。断连/设备失效后的迟到原结果只更新原操作排空证明，不落入新generation/新attempt。无隔离进程真实退出证明时不重建并复用旧句柄；资源 Owner 的断连不等于释放。

### 5.2 用途检查 IO、查询与关闭的有限闭环

`PurposeCheckTimeout`必须有限且>0，`MaxConcurrentPurposeChecks`为正整数；均由装配根明确提供，无无限默认。Check/Stop/Dispose调用的同步前缀须有界非阻塞，及时交出ValueTask；异步IO不放在同步前缀。所有Check/Stop/Dispose的ValueTask仅消费一次，需要持续追踪时转换成Task并保存到实例Call表；表包括CallId（checked单调分配，溢出停止该实例新准入）、关联request、阶段、截止/取消意图、真实Task终止、回执采纳状态。Check不得火忘启动IO；返回成功/拒绝/异常前须结束该调用的transport IO及借用，或继续保持Task未完成。Call数及保留诊断受options上限；名额满时Execute/Final检查拒绝为BudgetUnavailable（执行仍按原终态归约），Query只返回无载荷状态与BudgetUnavailable，不堆无限等待。

| 路径 | 有限等待、取消、回执与保留 | 排空/恢复断言 |
|---|---|---|
| Execute/FinalDisclosure | Call在锁内登记后锁外启动，deadline=`min(request deadline, now+PurposeCheckTimeout)`；Core为其持独立CTS，operation取消/deadline只登记取消并请求该CTS。Final在Postprocessing末尾、DrainStarted之前完成并结束IO；错误/取消/超期仅抑制载荷时可不启动Final检查 | 超期/取消后不采纳迟到Valid；Check Task尚未真实完成则request=DrainPending，Infer不返回终态。无native也不能称资源已释放。最终IO结束才删活动Call、释放CTS并继续请求排空；PurposeCheckTimeout先于request deadline时，仅为PurposeNotAllowed检查失败并抑制载荷；request取消/deadline仍按§5.1原停止意图/错误归约，不伪造native TimedOut |
| QueryDisclosure | 仅Running实例可启动；单调deadline=`now+PurposeCheckTimeout`，不沿用已终态request的过期执行deadline。调用token取消只结束Query等待，向该Check CTS请求取消；不取消原operation | 等待取消可抛OperationCanceledException；查询超期返回原状态/Result=null及PurposeNotAllowed（Stage=QueryDisclosure，SafeArguments含Timeout），原终态不变。后台追踪真实Check结束；迟到授权不补发载荷、不覆盖更晚资格 |
| Drain线性化 | 同一锁停止Infer及新QueryDisclosure准入；取消全部query检查CTS，新Query只读无载荷本地状态、附AdmissionStopped；Drain不调用CheckAsync、不依赖新的网络授权 | 已接纳operation的Execute/Final属于request排空，允许在既有operation的截止内完成；在operation取消/过期时请求取消，不因Drain等待者token取消而偷偷取消执行。Query IO及请求IO都计实例活动Call，全部真实结束前AllOperationsDrained=false |
| 实例尾段 | Core确认所有operation不再需要新的Execute/Final（已做检查，或取消/过期/失败只需排空）后封闭gate新调用，在锁外调用gate.StopAndDrainAsync让transport主动abort尚挂起的Check；所有Check Task真实终止且CallsStopped/ResourcesReleased=true后才Dispose gate；后台尾段与backend关闭共享一份阶段状态，重入Drain只等待同一个阶段Task | Stop/Dispose返回false/fault或超出本次wait预算不算停止/释放。记录ResourceDrainFailed，保存未完成Task/未释放分量；下一Drain继续等待或对已fault的幂等阶段重试。未完成阶段不并发再发一次。创建时无请求也须执行gate关闭 |
| 回执采纳 | CallId+阶段+实例代次+原request身份匹配，且未过deadline/取消/关闭查询准入时才采纳Valid；Reject/异常保留受限诊断。端口异常映射PurposeNotAllowed+内部相关诊断；不默认允许 | Call取消是意图，回执丢失不证明IO结束。gate必须具备transport关闭/abort的可执行结束路径，Stop仅返回真实证明；若真实IO永不结束，有限Drain返回未排空并保留engine，宿主隔离可信worker/进程，不能靠重试次数归零或另建同域engine冒称恢复 |

gate Stop成功不能代替Core观察Check Task真实终止；若Check continuation仍未完成，不Dispose gate或删除Call。请求资源释放事件同时要求关联Execute/Final IO已结束、CTS归还；Query IO属于实例，不能把已完成request倒改为DrainPending。`DrainReceipt`没有operation也可能AllOperationsDrained=false，Diagnostics明确Stage=AuthorityShutdown及活动Call计数。调用者token取消Drain仅取消等待；后台仍追踪IO/native和尾段，Query关闭后不再触网。`DisposeAsync`仅在这全部成立后做幂等的本地实例释放；提前调用fault且保留引用。方法返回的有限等待不保证进程内任意坏transport能被强制终止，无法得到真实停止证明时唯一合法结果是未排空；这不是接受无限阻塞调用或假资源回收。

## 6. 模型实例、输入与输出处理

模型解析必须得到确定内容闭包：权重/模型及依赖、类表、预处理、后处理、输出定义、适用输入域、批准配置/用途引用。闭包中每个成员都须按精确身份和内容摘要验证；仅验证主模型文件或外层包摘要，不能替代对其引用依赖成员的完整性验证。模型文件可读不代表用途可用或运行配置有效。实例缓存键覆盖内容闭包、任务、实际后端/设备、精度、shape、batch 和所有影响实例行为的设置；不得只以权重哈希作为唯一键。

结果缓存是可选优化，不是本模块必需能力。若实现，缓存键必须覆盖输入内容身份及其布局/ROI/有效域/坐标解释、模型与输入输出 Schema、预处理/后处理、任务和所有影响数值结果的实际运行配置；任何身份或语义无法证明一致时按未命中处理。计算结果缓存只复用计算载荷，不替代 operation 查询/幂等回读、当前输入与用途授权检查、模型/输入租约、结果交接或证据提交，也不得把其他请求的 operation 身份或回执带入当前请求。缓存须有明确 Owner，并限制字节数、条目数和保留期；缓存命中仍须为当前请求形成独立关联和实际来源记录。

处理固定顺序：核输入租约/来源/shape/layout/位深/ROI/有效域 → 依模型定义做通道/位深/裁剪/resize/letterbox/归一化 → 记录变换链与 mask → 绑定模型实例及经批准后端 → 执行 → 核输出结构、逐项关联、类表、有限性、坐标系和完整性 → 执行版本固定的后处理 → 返回候选与运行回执。不能拿显示伪彩、自动对比度图或猜出的 RGB/BGR 次序当模型数值输入。

12/16 位输入不默认除以 255 或 clamp；mean/std、插值、半像素约定、padding、阈值和 NMS 次序均属于版本化预/后处理契约。每个 box/mask/heatmap 按其任务合同恢复原输入坐标；计量单位转换与标定不由模块擅自完成。

批次建立前锁定 itemId、原序号、输入位置与预期结果基数。每项输出必须按显式索引/关联返回；缺 B 不允许将 C 左移给 B；重复/未知 ID 不得通过字典覆盖。若后端只按序返回且缺项导致映射不确定，整批关联失败；可定位的单项坏输出可按合同返回 Partial 与明确缺项。类别排序、阈值相等、NMS 边界、候选上限与截断原因必须确定且版本化。

HALCON `apply_dl_model` 等输入字典、输出字典、参数/默认值按 26.05 手册及 §2.5/§6.3 冻结；实际模型成员键随精确闭包绑定。不能从仓库其他 HALCON 版本或方法名猜具体字段。AsunImage `HDict` 和 `HDlModel.ApplyDlModel` 的签名存在，不足以推导字典字段、取消、并发或线程语义。

### 6.1 场景驱动执行卡

以下场景是实现和架构复审的最小闭环。每一行都要求实现者在请求、诊断和结果中保留对应字段；“调用方处置”不等于模块可以省略错误或偷偷改变结果。除“空输入/参数错误”等预接纳拒绝外，场景中的每个已接纳请求均必须完成 `Draining → Drained → ResourcesReleased` 后才发布终态。

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态/错误 | 恢复动作与可判定验收 |
|---|---|---|---|---|
| 正常配置/执行 | 完整模型闭包、授权用途、合法 DLSample/ROI；shape、预后处理、backend、batch/deadline 来自用途 Profile | 纯字段校验 → 预约预算并接纳 → 核用途/模型闭包与输入 → 绑定/预热（若批准）→ 变换输入 → `apply_dl_model` → 核逐项输出 → 后处理/坐标恢复 → 生成结果 | `Completed`，含实际设备/精度/shape/batch、候选或合法零候选、阶段耗时；无业务 PASS/FAIL | 同输入单项与批准 batch 的结果在任务容差内且关联一致；请求租约归零（实例驻留另计），调用方自行解释候选 |
| 空输入 | `inputs=[]`、空图、零元素张量或只含无效域；来源仍须有 request/attempt | 在 native 前检查数量/元素/有效域；仅当任务 Profile 明确允许空任务才走专用空路径 | 默认 `Rejected/InvalidRequest`（`EmptyInput`）；不得调用 native、返回空候选成功或计入覆盖 | 调用方修正输入并新建计算身份；验收证明无模型实例/帧租约泄漏，空输入不形成质量事实 |
| 部分成功/缺项 | A/B/C 有序输入，后端只返回 A/C、某 item 输出坏或某 tile 缺失 | 锁定 itemId/ordinal → 执行 → 先核 generation/模型，再核输出数量和显式 ID → 区分可定位单项与整批关联不可信 | 可定位坏项返回 `Partial` + item 缺项/错误；无法确定映射返回 `OutputAssociationLost/Failed`；缺项不是零候选 | 宿主按必需/可选政策决定等待、重算或人工；验收断言 B 不被 C 替代、缺 tile 不标完整、成功项可追溯 |
| 歧义/错误输入 | RGB/BGR 不明、12/16 位却给 8 位规范、stride/shape/通道/坐标约定冲突、非有限参数 | 先比较输入描述与模型/预处理闭包；不猜布局、缩放、像素中心或 padding | `Rejected`：`InputFormatUnsupported/InputShapeMismatch/InvalidRequest`，定位字段；不产生候选 | 调用方提供新预处理修订和新计算身份；验收证明同字节不同解释不会命中同一结果缓存 |
| 超大输入/高并发 | 图像/tile/item 超过 MaxItems、输出/临时张量预算或同时到达大量兼容请求 | 先做 checked 尺寸/内存估算 → 预约有限队列/字节 → 按固定 tile 窗口或短批推进；超上限在 native 前拒绝 | `QueueFull/BudgetUnavailable/DeadlineExceededBeforeStart`；不得无限排队、隐式降分辨率、丢 tile 或静默拆成无记录的多个操作 | 宿主按批准策略延后/分流/新 attempt；验收覆盖峰值账、尾延迟、队列有界、每 tile 独立关联和缺口可见 |
| 噪声/遮挡/退化输入 | 输入质量诊断来自图像模块；遮挡、反光、模糊、曝光异常或有效域不足；质量阈值来自用途 Profile | 仍按正常预处理执行，记录质量/有效域；模型只输出其实际响应，不由核心修图或补全不可见区域 | 可能是合法低分/拒识/覆盖不足，或 `InputQualityInsufficient`（若 Profile 定义）；不是程序异常，也不转 PASS | 调用方按用途选择补采、人工或确定性替代；验收要求遮挡区不被填成背景，拒识与格式失败可区分 |
| 取消/超时/native 排空 | token 取消、deadline 到期、UI 关闭、共批 A 取消/B 继续；底层是否支持中断由适配器能力声明 | 按队列/native/后处理阶段执行取消；native 不可抢占时只记请求并保持租约；真实停止/完成后才排空 | 已接纳请求返回 `Cancelled`/`TimedOut` 终态前必须完成排空；排空期间仅返回 `CancelRequestedNativeRunning` 或 `TimedOutExecutionUnknown` 观察 | A 不影响 B；查询原 attempt 或隔离 worker；验收检查迟到结果不进新 generation、资源不提前归零、已提交事实不被抹除 |
| 资源达到上限/OOM/设备丢失 | CPU/native/GPU/输入保持/输出任一维达到 Profile 上限；设备查询来自 26.05 路线但空闲由资源 Owner 确认 | 停止实例新准入 → 保留在途关联和资源账 → 等待可信停止/进程退出 → 隔离坏实例 → 释放/重建新 generation | `BudgetUnavailable`、`BackendExecutionFailed` 或排空期间的 `DrainPending`/`ResourceDrainFailed` 观察；资源释放后才可发布 `Failed` 或 `ExecutionUnknown` 终态；禁止静默换精度/减 tile/重跑到成功 | 仅使用已批准备用方法并新 attempt；验收证明旧句柄不复用、旧结果不串入新代、峰值和释放顺序可观测 |
| 持久化/提交竞争 | 结果已生成但提交回执丢失、撤权、取消与提交锁竞争；提交端口由原 Owner 提供 | 推理模块先完成自身排空并发布唯一推理终态；调用方/提交 Owner 以原 operation/attempt 查询提交回执，不新建同义 operation | `CommitUnknown` 只属于外部提交观察；不改变已发布的推理 `Completed/Partial/Failed/...`，已提交成功不可被取消覆盖 | 调用方查原回执；验收同键同内容不重复写、未知不当成功、模块不复制 OperationStore/事实库 |
| 版本修订/缓存 | 模型、类表、预后处理、阈值、设备、精度、batch 或输入解释任一变化 | 计算影响闭包摘要 → 形成新 revision/实例 key → 旧代排空 → 新代装载/核读回 → 结果记录实际版本 | `Rejected/ModelNotReady` 或新 `Completed`；旧缓存只能在纯计算契约和当前权限均满足时复用，并产生新关联 | 验收同权重不同精度/类表/设备不复用错误资格；历史结果可读且不被覆盖，revision 可重放 |
| 升级/回退 | 新程序集/适配器/模型闭包与旧代并存；升级记录含兼容矩阵、校验和、迁移说明 | 先离线契约/挑战集 → 两宿主 Replay/Shadow → 停止新接纳 → 排空或隔离旧代 → 切换新代；失败按同序回退 | 新代不兼容为 `Rejected/AdapterNotReady`；回退中在途保持原状态，未知不假设已停止 | 验收旧结果仍可读取、旧代迟到不写新代、回退不删除模型/证据、不跨版本复用未验证缓存 |
| 无 UI 调用/长期运行 | 独立 .NET 宿主、无 Dispatcher/窗口；连续小时/天的有限请求和设备/模型代次 | 通过同一 `InferAsync`；周期性记录阶段/资源/代次；有界队列和定期释放；观察者故障隔离 | 每请求一个终态；长时资源斜率、句柄数、队列和取消延迟可观测；泄漏为 `InternalFailure/ResourceDrainFailed` | 用回放和真实适配器分别做长稳；验收重启/驱逐/取消后租约归零，UI 缺失不改变语义，未验证项标 Unknown |
| 可选 UI/第二消费者 | UI 仅投影诊断；第二宿主使用不同用途/参数但同一核心程序集 | UI 调用同一校验/异步入口 → 订阅可丢失事件 → 读最终结果；第二宿主独立注册适配器/语言/取消域 | UI 只能显示候选、拒识、缺项和恢复建议；两个宿主结果各自关联，配置不串扰 | 验收关闭 UI 仅撤观察、不释放仍在用 native；两宿主无私表/产品 VM/全局状态，领域规则留各自宿主 |

### 6.2 场景不变量

所有场景共同满足：一次输入解释变更产生新计算身份；一次已接纳请求只产生一个模块终态；任何缺项、未知状态、未排空资源或未核实的备用路线都不可被编码成空候选成功；模块返回候选不等于调用方已作质量决定。场景表中的“验收”是待实现断言，不是本轮测试结果。

### 6.3 任务规范、预处理与输出解码（完整能力切片）

模型闭包成员与名称按 §6.4 冻结，Descriptor显式列出named input/output和精确成员引用；preprocess/postprocess/raw-output-schema/output-schema/class-map的完整封闭字节结构在 §6.4–6.6，不再由任意“闭包规范”补猜。每成员 `Reference.Sha256` 是成员 bytes 的 SHA-256；模型根描述列举所有成员引用。各named value的 Source.Sha256 绑定本次实际 bytes（含声明padding），shape/stride/layout/ROI/valid-domain/变换作为独立解释绑定，不要求输入内容摘要等于上游证据摘要。Core 对二者分别核身份；最终输出 payload 为固定 task schema 的 UTF-8 JSON，拒绝重复键、未知必需版本、非有限数和超限数组；字段顺序与编码按 §6.4 的 Canonical JSON 规则，摘要对实际编码 bytes 计算。接口给 bytes 并非允许“float[]+任意字符串”弱契约。

**输入/参数有效域。** Shape 每维>0，rank在1..EngineOptions.MaxRank，Shape/ByteStrides长度相等；元素宽为1/2/4/2/4/8 byte对应A.1六种类型。ByteLength>0并等于租约长度；以 checked 64-bit算 `lastOffset=sum((shape[i]-1)*stride[i])+elementBytes`，必须<=ByteLength。stride为正，按stride升序验证非重叠块跨度（除长度1的轴），拒绝负stride/别名轴；不隐式复制越预算布局。Image 只接受闭包声明 HW/HWC/CHW；Tensor 按闭包的named axes，不将NCHW当宽高。ROI/有效域/变换有独立schema/hash，ROI是原输入坐标有限域且在边界内，明确 row/column，不接受显示屏坐标。UInt16的有效位数/黑白范围归预处理，无自动/255。

预处理 member 固定：输入类型/layout/channel顺序和源域、裁剪ROI、目标shape、resize模式、插值、padding value、数值映射/归一化及有效mask处理顺序。顺序是校验→只读裁剪→按指定通道排列→resize/letterbox→范围映射→归一化→写目标layout；各阶段输出预算与变换链记录。范围映射 `y=(x-sourceMin)*(targetMax-targetMin)/(sourceMax-sourceMin)+targetMin`，sourceMax>sourceMin；clamp只在规范明确时执行并诊断截断。normalization明确identity或逐通道 `(y-mean)/std`，std>0，禁止重复规范化。没有该member不做推理。模型只接已声明范围的有效像素；padding不进覆盖分母。

resize的目标到源像素中心按训练同源规范绑定：支持half-pixel `src=(dst+0.5)*sourceSize/targetSize-0.5` 或align-corners（单像素轴规则必须明确）；不猜另一种。letterbox冻结缩放、整数目标尺寸与上下左右padding，记录实际整数裁剪和变换，不用理想浮点比例恢复坐标。类别mask用nearest，数值图插值方式来自模型规范；有效mask采用规范声明的保守传播（只要参与数值插值的源点无效则目的点无效），未知不填背景。若实际训练规范不属于上述路线，则 codec 在该闭包未补具体算法前返回 AdapterNotReady，仅阻断对应任务。

| taskKind token / final schema 必需结构 | raw解码→校验→后处理主序与拒识 | 反例/验收 |
|---|---|---|
| `classification` / classMapRef、scores[{classId,value,scoreKind}]、distributionComplete、selectedClass?、rejection、ood | 按 class ID 关联，完整分布或top-K明确；原score保留，已校准概率另字段。稳定同分按class ID ordinal。按固定后处理阈值选择/拒识 | 2类scores相等且 threshold 相等按固定>=规则；缺类不补0；top-K不能称完整。OOD无能力=NotProvided，Profile要求却缺失为拒识 |
| `multi-label-classification` / 每类独立score及selectedClasses | 与类表一一关联→逐类校准/阈值→可多类/零类；不softmax、不强制sum=1 | 同一输入两类均超过各自阈值必须同时保留；未返回类为缺项不是阴性 |
| `detection`、`instance-segmentation` / candidates[{id,classId,score,geometry,mask?}]、coordinateRef、suppression、truncation | raw框/实例mask→有限/类/shape关联→逆坐标/有效域→固定NMS→tile合并→有界排序截断；已有native NMS须声明，禁止再隐式抑制 | axis-aligned几何用row/col边界和原坐标；旋转框用四角polygon不当轴框IoU。实例mask必须有对应candidate身份；多相邻/边缘/遮挡候选不能被默认第一个覆盖 |
| `segmentation` / gridShape、classIds、confidence?、validityMask、coordinateRef | 核每像素类别与shape→nearest逆变换类别、规范插值confidence→有效域→完整覆盖 | 2x2 grid的无效角保持Unknown，不填背景；零前景且完整有效才合法零候选；缺tile标Partial |
| `anomaly` / scoreMap、imageScore、scoreKind、validityMask、rejection | 解码实际模型图/整图score→固定域/阈值拒识→可选区域投影；不跨tile用max伪造整图score | 漂移/遮挡/OOD与高异常分数分别保留；不当生产NG/量测。全图score无定义的tile路线不输出替代全局值 |
| `embedding` / dimension、vector、normalizationRef、metricRef | 核维度/有限性→规范identity或L2归一化（norm=0拒识）→返回向量；相似度需要双方同模型/度量版本 | 零向量不能除零；不同模型向量即同维也不比较；不授权身份/设备动作 |
| `ocr-comparison` / rawText、symbols[{id,box,score}]、dictionaryRef | 通用模型raw解码→原文/框/字典关联→低信拒识；语言/期待值比较在OCR消费者 | raw低信不能被grammar替换为正确文本；专用Deep OCR不在本模块重复实施 |

scores标明 `Probability/UncalibratedScore/Distance/Anomaly`，校准仅采用闭包明确支持的identity、temperature-softmax（logits z，T>0，以减max的稳定softmax）或逐类Platt `1/(1+exp(-(a*z+b)))`，有限a/b；单标签概率全分布归一，多标签仅独立sigmoid。阈值来自用途Profile且与scoreKind绑定，概率阈值[0,1]，其它阈值有限且由规范声明域；>=接纳、<拒识，margin/OOD如需要须明确对应规范及阈值。未经批准不校准，不把最高raw score命名confidence；后处理改变须新revision。

axis-aligned Core NMS仅在声明为Core且不是native已执行时做：同类、score降序→同分classId/candidateId ordinal→面积有效框→交并比IoU，`IoU > nmsThreshold`抑制，阈值[0,1]；相等不抑制。tile合并先反坐标，固定tileId/候选身份，再按同一NMS规则，完整记录被抑制来源；rotated/mask NMS若任务需要则由该闭包指定已批准HALCON任务后处理和准确参数，不自动用轴框近似。candidate cap先排序再截断，WasTruncated=true且OutputComplete=false。置信/OOD/max候选/tile大小不在线搜索。

解释结果是独立可选字段，保存method、target class、scaling、模型/输入与变换身份，状态NotProvided/NotApplicable/Provided分开；归一热图颜色不代表概率或物理量。ExplanationNotProvided是警告，不将完整主结果降为Failed；解释内存同样受输出/native/GPU预算，不能为显示新增无限热图。拒识 item 可含原score/原因供诊断，但无可消费候选；§A.1中Completed才有可消费输出的规则继续有效。

### 6.4 Canonical schema v1：成员字节、字段与解析

本节是本模块唯一正式字节规范 `Asun.AiInference.Canonical/1`，不是交给资产/客户编写的任意 JSON Schema。下面花括号列**全部字段**；`?`表示值可为null而非字段可省略，`[]`为数组，`oneof`由明确kind选择。所有字段必需，不允许未知字段、缺字段、重复键、注释或尾逗号；tag/schema和大小写ordinal匹配。所有规范成员/envelope的`v`是整数1；其它版本返回AdapterNotReady（执行前），raw/final不匹配返回OutputSchemaMismatch。模型实际形状、类表、输出层名及训练参数是此固定结构的值，不是等待客户设计的字段。

**编码/解析。** UTF-8严格解码、无BOM；字符串须有效Unicode且已为NFC（不静默正规化身份），无未配对surrogate。对象key按ordinal排序，数组保留下面规定顺序；无空白，字符除控制符、双引号、反斜线外直接写UTF-8；双引号/反斜线写`\"/\\`，控制符固定小写`\u00xx`。整数十进制无前导零，0不用负号；非整数/数值字段按.NET 10 `double.ToString("R", InvariantCulture)`，`-0`正规成`0`，指数E正规小写e、去正号和指数前导零；禁止NaN/Infinity及decimal到double的溢出。解析按字段目标int32/int64/double检查完整范围，重编码后逐byte与输入相等才接受canonical（不先改写再核hash）。bool为true/false，null仅用于标?字段；二进制仅标准RFC4648 base64（带padding，无空白，decode→encode相等）。hash均小写64位hex，对实际bytes；规范成员Reference.SchemaId/SchemaVersion必须匹配envelope.schema/v。raw.Schema和final.OutputSchema引用的是ai.raw-definition/ai.output-definition，其定义明确绑定ai.raw-item/ai.final-item载荷，不混用定义与实例的schema ID；model/dependency原二进制不作JSON解析，只核精确hash/角色/公开模型装载。

解析先核ByteLength/MaxTemporaryBytes/MaxOutputBytes（资源维按用途），使用有界UTF-8 reader深度32，每个身份/字段名string UTF-8字节<=MaxIdentityChars×4，OCR数据string用定义maxStringBytes且总量预算（trace按专限）、数组checked计数/乘积及内存额度，避免先无限DOM再查上限。数值数组先核shape乘积再分配。未知schema/role/name/type不允许通过字典扩展；需要新值域须修订本指导/version。解析后不可变DTO不保留JsonDocument/Span。canonical小型反例：输入`{"v":1,"schema":"x"}`因key非ordinal顺序拒绝；合法顺序为`{"schema":"x","v":1}`，仅作编码例不是允许schema=x。

通用类型：`Ref={owner,id,revision,schemaId,schemaVersion,sha256}`等价A.1的Reference，所有身份非空、有限长度；SchemaVersion在本规范固定string "1"，envelope.v为整数1。kind/elementType序列化为A.1枚举的精确名称（Image/Tensor、UInt8等），不用数字或未知枚举值；layout/targetLayout为HW/HWC/CHW或显式named Tensor layout。尺寸/计数/索引字段为int32（byte/shape输出额度允许int64），clamp/required/complete/truncated等标志为bool，其它数值参数为有限double；必须按本表域校验，不将JSON数值全读成double再猜类型。`Dims=[positive int64]`，rank在1..MaxRank（标量固定shape[1]）；`Axes=[string]`与Dims同长度且唯一。classId用不透明非空string；HALCON class_id精确整数转换为Invariant十进制string，不能以class name/数组位置代替。`Tensor={dtype,shape,axes,values}`，dtype=`i32/f64/u8/string`，values对应整型/有限double/0..255/string扁平数组，row-major，数量=checked product(shape)，i32为int32；零候选只允许N=0的slot，rank仍>0，不允许模型input的0维。SDK tuple/image均先复制此管理结构；image轴是[row,col]，多channel是[row,col,channel]，不把HALCON指针放base64。

| schema / role | 完整字段（除列出的结构不接受其它字段） | 关系/来源/解析 |
|---|---|---|
| `ai.manifest` / manifest | `{schema,v,model:Ref,taskKind,preprocess:Ref,postprocess:Ref,rawOutputSchema:Ref,outputSchema:Ref,classMap:Ref?,configuredBatchSize,inputs:[InputBinding],outputs:[OutputBinding],members:[MemberRef]}` | `InputBinding={name,preprocess:Ref,kind,elementType,shape,layout}`对应A.4；`OutputBinding={name,sourceKey,container,valueType,nativeShape,axes,shape,required}`对应A.4；`MemberRef={reference:Ref,role,name}`。成员按(role,name)ordinal排序且唯一；模型及全部依赖列入members，不列manifest自身，避免hash自引用。Descriptor.Manifest引用此bytes，ModelClosureSha256等于Manifest.Sha256；Descriptor其余字段必须与解析值完全相等 |
| `ai.preprocess` / preprocess | `{schema,v,inputs:[PreInput]}`；`PreInput={name,kind,elementType,layout,axes,channels:[string],sourceMin,sourceMax,targetMin,targetMax,roiMode,targetShape,targetLayout,resize,interpolation,pixelCenter,singleAxis,padding:[double],clamp,normalization,mean:[double],std:[double],validity}` | inputs与Descriptor.Inputs名/顺序一致；kind/elementType/layout同A.1；roiMode=`full/reference`；resize=`none/stretch/letterbox`；interpolation=`nearest/bilinear`；pixelCenter=`half-pixel/align-corners`；singleAxis=`center`；normalization=`identity/mean-std`；validity=`all-contributors-valid`；sourceMin/sourceMax/targetMin/targetMax均有限，sourceMax>sourceMin、targetMax>targetMin、std>0；padding使用源值域（letterbox先于范围映射）。identity时mean/std=[]；否则各长通道数（这里C是通道数，不是类表C）。padding长通道数且有限，channel名唯一且排列精确；Tensor无空间轴只允许none，shape不变。Image shape为HW/HWC/CHW且targetShape与binding相等 |
| `ai.postprocess` / postprocess | `{schema,v,taskKind,scoreKind,calibration,thresholds:[ClassThreshold],marginThreshold:double?,ood,geometry,nms,tile,candidateCap,embedding,ocr,explanation}` | `ClassThreshold={classId:string?,value:double}`，null仅无类别任务全局阈值；类任务按classId排序且精确覆盖classMap，不用经验默认；embedding thresholds=[]，OCR用minimumScore，anomaly仅一个null classId全局阈值。marginThreshold仅分类可设有限非负数，第一/二score差小于它为LowMargin拒识。`calibration={kind,temperature:double?,a:[double],b:[double]}`，kind=identity/temperature-softmax/platt；`ood={required,sourceName?,threshold?}`；`geometry={kind,coordinateInput?,minVisibleFraction}` kind=none/rectangle1/rectangle2；minVisibleFraction[0,1]，越域候选按固定阈值拒识，不悄悄裁框改变形状 |
| 上行续（不是第二schema） | `nms={owner,iouThreshold:double?,metric,classAgnostic,minNativeConfidence:double?,nativeCandidateCap:int?}`；`tile={mode,rows,cols,overlapRows,overlapCols,merge}`；`embedding={normalization,metric}`；`ocr={dictionary:Ref?,encoding,minimumScore?}`；`explanation={kind,targetClassId:string?,scaling,targetConvLayer:string?,useConvOnly:bool?}` | owner=none/core/backend；metric=axis-iou/rotated-iou/mask-iou，none时threshold/minNativeConfidence/nativeCandidateCap=null、classAgnostic=false；backend明确读回max_overlap/max_overlap_class_agnostic、min_confidence、max_num_detections与本字段及类无关策略一致，不能默用native默认；core同类axis-iou固定classAgnostic=false。tile.mode=none/fixed，none时4个尺寸为0/merge=none；fixed为正尺寸/非负重叠<尺寸，merge=nms/grid（分类/embedding/OCR/整图anomaly仅none；任务需要其它tile聚合必须先扩schema）。embedding.normalization=identity/l2，metric=none/cosine/euclidean。ocr.encoding=UTF-8。explanation.kind=none/grad_cam/guided_grad_cam，scaling=none/scale_after_relu/scale_before_relu/scale_without_relu，完全对应26.05 GenParam；targetConvLayer=null为手册最深有效卷积层，grad_cam的useConvOnly须bool，guided为null；不得用minmax别名猜算子参数。非适用结构仍全部字段存在，枚举none/identity、可空值null，不能塞业务阈值 |
| `ai.raw-definition` / raw-output-schema | `{schema,v,taskKind,profile,distribution,bindings:[OutputBinding],maxCandidates,maxGridElements,maxStringBytes}` | bindings与Descriptor.Outputs完整一致。container=`tuple/image/regions/tensor/text`，valueType对应Tensor dtype或`region`；distribution=`complete/top-k/not-applicable`，仅generic分类支持top-k，K<C标不完整，不当全类概率/成功覆盖。Shape允许-1仅命名轴N/T/K的动态候选/字符/截断类数，其它维正且从已读模型固定；N/T/K上限受maxCandidates，HW乘积受maxGridElements；无泛化JSON路径/表达式。sourceKey精确HALCON键或generic层名（仅分类解释允许本节固定nested路径），name为§6.5逻辑slot |
| `ai.output-definition` / output-schema | `{schema,v,taskKind,payloadSchema,maxCandidates,maxGridElements,maxStringBytes,scoreKind,coordinateInput?}` | payloadSchema固定`ai.final-item`，taskKind/scoreKind/coordinateInput与post一致，上限与raw额度相容；不是任意JSON schema文本。定义只给本节既定结构的参数，上限不能大于请求/实例预算 |
| `ai.class-map` / class-map | `{schema,v,classes:[{id,name}]}` | ordinal ID排序、id/name都唯一；分类/多标签/检测/实例/语义分割必需，其它为null（不伪造背景类）。标准HALCON任务读回class_ids/class_names须一一一致；generic无这些model参数时以manifest的类表绑定output轴，禁止造读回成功，schema名与模型属性不同不静默映射 |

每个InferenceContentMember显式Name。manifest role/name=`manifest/root`；模型binary及依赖role分别为`model`/`dependency`、name精确资产名；OCR字典role=`ocr-dictionary`/name=root且由post.ocr.dictionary引用、按ai.ocr-dictionary解析，不当二进制依赖忽略；preprocess/postprocess/raw-output-schema/output-schema/class-map的name=`root`且各仅一份（preprocess.inputs实现多输入，不偷偷放多份root）。Input/output bindings分别按name ordinal排序。RequiredOutputs严格等于Outputs中required=true的**逻辑name**列表；不是apply_dl_model的Outputs参数。后者由§6.5 profile确定，raw adapter核sourceKey→name→schema，不把名字同名当形状已匹配。

**预处理精确定义补足。** nearest用floor(x+0.5)并夹到源边界；bilinear用floor及四邻权重，边界按edge复制，其有效性仍查参与权重>0的源点。align-corners单目标像素取(sourceSize-1)/2；targetSize>1用dst*(sourceSize-1)/(targetSize-1)。letterbox比例=min(targetH/sourceH,targetW/sourceW)，整数newH/newW=max(1,floor(source×ratio+0.5))，余量前侧floor/2、后侧余下；记录实际尺寸。crop为引用的整数闭区间rectangle1，先裁再resize；不支持shape的clamp/layout/channel/位深变体返回AdapterNotReady，不随意近似。裁剪/resize不改变原身份；实际变换链由adapter写raw。

校准kind=identity时temperature=null/a=b=[]，temperature-softmax时temperature>0且a=b=[]，platt时temperature=null、a/b按classMap同序且各长C；scoreKind严格Probability/UncalibratedScore/Distance/Anomaly。candidateCap、maxCandidates/maxGridElements/maxStringBytes均正整数且受预算，合法N=0不表示上限=0；maxStringBytes专用于OCR全文/string tensor，覆盖字典字符串但不把客户全文限制误用MaxIdentityChars。norm和calibration中间量用double，Platt按t=a*z+b，t>=0时1/(1+exp(-t))、t<0时exp(t)/(1+exp(t))，避免溢出。阈值接纳方向固定>=；Distance的相似候选接纳改用<=须新版schema，不把方向留实现者选择。OCR greedy CTC在同一重复run内保留最高softmax score的time（同分最早），polygon取该time；UTF-8 rawText保留原读，不做grammar。

fixed tile仅检测/实例/分割允许；tile起点按row/col从0步进(size-overlap)，最后tile裁到原域边界且按preprocess规定padding，tileId按row-major从0，none只有tileId=0。每tile独立raw slots/prepared/batch；tile覆盖必须覆盖原ROI全部有效像素，不足则Partial。检测先逆坐标再已定NMS，ID=`itemId/tileId/originalIndex`；分割重叠像素固定选原图像素距tile中心的欧氏距离最小tile（同距较小tileId），不做未定义加权；选定tile无效则像素Unknown，不用其它tile补成事实。prepared.coordinateMatrix等于输入coordinate×crop平移×实际resize/letterbox逆变换；tensor非空间不参与。adapter以cv2区域算子将候选polygon在原域栅格化，计算与有效域交集的像素数/区域像素数并写raw.visibility；区域为空用0，Core只校验关联/有限[0,1]并按minVisibleFraction拒识，不直接引用cv2或在纯Core重复栅格化算法。

`Roi/ValidDomain/CoordinateTransform`解释成员分别为`ai.roi={schema,v,row1,col1,row2,col2}`（int32闭区间）、`ai.valid-domain={schema,v,shape:[H,W],bits:[0|1]}`及`ai.coordinate={schema,v,matrix:[9 double]}`，matrix为row/col齐次3×3、末行[0,0,1]且可逆。null表示全域/identity；所有空间输入须有HW轴，同一item多图坐标各自绑定，后处理coordinateInput明确唯一基准图。HALCON减domain须复制为同样mask；byte value映射先核mask，禁止把未知填背景。非空间Tensor的上述三个引用必须null。runtime Profile仍是Owner精确引用，但影响算子的device/precision/batch/输出/NMS参数须按此manifest/post读回一致，不因Profile自由文本改任务结构。

### 6.5 HALCON 26.05 sourceKey → named raw slot → final 路线

以下字典键/类型来自26.05官方[Model数据字典](https://www.mvtec.com/doc/halcon/2605/en/toc_deeplearning_model.html)及项目`apply_dl_model`，本次只为未闭合的键定向核对，不重扫封装。全部算子经`ImageLibDotNet.cv2`。每item一个DLSample结果对应其ID/Sequence；HALCON输出数组必须恰好对应实际提交sample，不把补满项计成请求item。标准Image任务DLSample的`image`承载该item的唯一named image输入；generic按[create_dl_layer_input](../../../halcon算子手册/operators/create_dl_layer_input.html)的26.05公开语义以精确input layer name绑定多tensor，每itemValues名必须与manifest.inputs相等，不用多个image凑一个sample。generic Image转real图对象、Tensor转integer/real tuple；layer shape=[width,height,depth]，tuple按col最快、row其次、depth最慢排列，element总数必须相等；Core的named axes明确转换，禁止隐含allow_smaller_tuple补0。读取实际layer shape/is_inference_output/input_type（仅调用get，不新建训练网络）与manifest核对；constant层无request value且须资产闭包固定常量，region_to_bin为单独已定mask输入，不把整数tuple当region。

| raw-definition.profile / taskKind | HALCON sourceKey（标准字典键）与精确shape → 逻辑name | apply选择、final路线、缺失/错误 |
|---|---|---|
| `halcon.classification` / classification | classification_class_ids i32[C]→classIds；classification_class_names string[C]→classNames；classification_confidences f64[C]→scores，三者C相等且=classMap总数 | apply Outputs=[]；按ID关联全分布→校准/阈值→§6.6分类data。名称错/类重复/缺类为OutputSchemaMismatch；未选出的类不删除。OOD能力读回ood_available=true时登记ood_score/ood_threshold f64[1]→oodScore/oodThreshold，必须成对；依[fit_dl_out_of_distribution结果说明](../../../halcon算子手册/operators/fit_dl_out_of_distribution.html) score>threshold为域外，不用>=替代；本模块不调用fit训练；ood_result原生投影不当质量判定 |
| `halcon.multi-label` / multi-label-classification | class_ids/class_names/confidences分别i32/string/f64[C]→classIds/classNames/scores；selected_class_ids/selected_class_names/selected_confidences分别[N]→nativeSelectedIds/Names/Scores | apply Outputs=[]，全C分布必需；selected为native min_confidence投影，若登记required则三者同N、为全分布子集且score相等。Core按post.thresholds独立选择，不把selected取代全类分布 |
| `halcon.rectangle1` / detection、instance-segmentation | bbox_class_id i32[N]→classIds；bbox_class_name string[N]→classNames（可选）；bbox_confidence f64[N]→scores；bbox_row1/col1/row2/col2 f64[N]→row1/col1/row2/col2。实例另mask regions[N]→masks | apply Outputs=[]；所有必需tuple同N，N=0才可合法零检测。rectangle1坐标为pixel-center连续坐标，面积及IoU按连续边界差计算；保留原框，不暗加1。mask必须与box同序，逐region栅格化为 prepared HW的u8[N,H,W]（0/1），未知域另mask，不把HALCON region借用传Core |
| `halcon.rectangle2` / detection、instance-segmentation | bbox_class_id/bbox_confidence同上；bbox_row/col/phi/length1/length2 f64[N]→row/col/phi/length1/length2；mask同上 | apply Outputs=[]；length>0、角为radian，四角以HALCON rectangle2原坐标计算后逆变换，不能变轴框；NMS默认backend（model读回已配置），Core仅axis-iou；需要Core精确rotated/mask抑制先绑定本指导算法扩展，不静默近似 |
| `halcon.segmentation` / segmentation | segmentation_image image int HW→classGrid（i32[H,W]）；segmentation_confidence image real HW→confidenceGrid（f64[H,W]，按定义可选） | Outputs=['segmentation_image','segmentation_confidence']（confidence非必需时只前者）；HW等于模型准备shape，类别ID须合法；逆变换nearest/已定confidence插值→原图grid，invalid角保留null+validity=0；缺必需image失败，不作解释可选 |
| `halcon.anomaly` / anomaly | anomaly_image image real HW→scoreGrid；anomaly_score real→imageScore（f64[1]） | anomaly_detection Outputs=[]；gc_anomaly_detection profile固定outputs=[]或明确local/global：anomaly_image_local/global→scoreGrid及anomaly_score_local/global→imageScore，二者成对；combined按实际result的anomaly_image/anomaly_score，不能把Outputs选择token当结果键。分数未承诺概率，scoreKind=Anomaly；GC已冻结normalization参数需模型读回/Golden，不现场估计 |
| `halcon.generic` / embedding | sourceKey=模型实际inference output layer精确名，tensor f64[D]→vector，D>0；额外输入layer以manifest.inputs绑定 | 在资产阶段已设置/冻结输出层，apply Outputs按这些名字；读实际输出shape和类型后规范复制，保持每sample关联→identity/L2→vector。不存在通用“embedding”标准字典键，不伪造key或让Core猜维度 |
| `halcon.generic-ocr` / ocr-comparison | 精确named tensor层绑定logits f64[T,C]→logits；class-map以外的ocr dictionary `ai.ocr-dictionary`字符C及blankIndex；可选symbolGeometry f64[T,4]→symbolBoxes | 通用OCR对照走greedy CTC：逐time argmax（同分最小class index）→先合连续相同index再删blank，UTF-8逐字符拼接；score为保留time softmax最大值，不能当整词概率。geometry缺失显式NotProvided；专用ocr_recognition/Deep OCR的word/char_candidates不绕过OCR模块迁入 |
| `halcon.generic` / 其它六类已支持task | 输出层显式sourceKey→上面相同逻辑slot/shape；classification可logits f64[C]→scores且post声明temperature-softmax；多输入/多输出依manifest逐slot绑定 | 不假设generic具有标准task字典。Shape来自实际模型固定属性，schema本身仍本节固定。多个tensor保留独立name/axes，name唯一、必需集合齐全、样本轴由adapter剥离且记录，不按字节长度猜哪个是class/mask |

shape中C=classMap数、D/T/H/W由模型实际属性与输入准备shape绑定，N是实际候选数并允许0。HALCON的native class/score tuples绑定无batch轴；generic层若[Nbatch,...]须descriptor.outputs.axes明确首轴batch，adapter在真实submitted位置拆到item、raw tensor剥除batch轴（非1样本不得靠squeeze猜）。Shape含-1仅允许N/T/K候选动态轴，其正值和上限都在raw记录。额外output只有在bindings列为optional才允许；除固定逻辑slot外只允许aux:前缀的有界辅助tensor，校验但不参与任务结果；final.optionalOutputs记录Provided/NotProvided及tensor，不能拿aux替代scores。此处未知/重复key指canonical raw slot；标准apply Outputs=[]返回的未绑定原生键只由adapter有界释放，不自动升级为required或final数据。raw错类型/axis、越限、非法类别或shape不匹配均OutputSchemaMismatch；NaN/Infinity=OutputNumericallyInvalid；少sample导致身份映射不可信=OutputAssociationLost；可定位单item问题按 §5.1 Partial。逻辑slot的mask/geometry不允许后返回并无来源地挂到另一个候选。

分类解释optional slot逻辑name=explanationHeatmap，sourceKey仅允许`heatmap_<method>/heatmap_image_class_<id>`或guided的`heatmap_guided_grad_cam/guided_grad_cam_image_class_<id>`；这是预定义二级dictionary访问，不允许任意path表达式。targetClassId=null先选本次主分类最高类后记录实际id；调用gen_dl_model_heatmap新DLResult，不覆盖主结果，核返回同sample。image实际nativeShape读回[H,W]或[H,W,C]并与binding一致，转Tensor，仅填final.explanation；异常/无资源仍ExplanationNotProvided，不删除主结果。

OutputBinding.NativeShape为HALCON实际对象/tuple维，Shape/Axes为规范Tensor维；binding.axes与shape同rank、nativeShape与shape乘积相等（regions按N×HW计）；仅允许identity或列举的flatten/split：generic object图像的[row,col,channel]按col最快、row其次、channel最后的native顺序复制，vector/logits由明确axes重排（logits[T,C]的class为最快）。乘积必须相等，batch轴只在实际后端含该轴时剥离并由BatchEvidence证明，HALCON每sample dictionary本身无batch轴。NativeShape每维固定或已登记动态N/T/K；adapter同时核native与规范shape，不用同字节数替代shape匹配。其它reshape/axis约定不能任意发明，需在新profile增加明确排列，Core任务能力保持现有固定输出语义。

### 6.6 raw/final payload：封闭数据结构与完整性

`InferenceRawItem.Bytes`固定schema=`ai.raw-item`，v=1：`{schema,v,itemId,sequence,taskKind,profile,batches:[BatchEvidence],prepared:[PreparedInput],slots:[RawSlot],visibility:[CandidateVisibility],complete}`。`CandidateVisibility={tileId,candidateIndex,visibleFraction}`，检测/实例按(tileId,candidateIndex)序、每候选恰一项、fraction有限[0,1]；其它任务=[]，不由任意原生score冒充覆盖。`BatchEvidence={tileId,ordinal,configuredSize,submittedSize,itemPosition}`，ordinal从0、itemPosition在submittedSize内，configuredSize与manifest一致；每item只出现实际执行的内部批次。`PreparedInput={tileId,name,shape,layout,coordinateMatrix:[9 double]?,validity:[0|1]}`按(tileId,name)序；空间validity长HW、坐标从准备域映回原域，非空间matrix=null且validity=[]。`RawSlot={tileId,name,sourceKey,tensor:Tensor?,regions:[Tensor]?,text:string?}`按(tileId,逻辑name)序，只允许与binding.container对应的一种值：tuple/image/tensor为tensor，regions为regions且每Tensor为u8[H,W]，text为text。其它两值必须null（regions非选分支=null）；本v1不接任意record。每tile每个required slot一次；complete只在全必需结构/coverage可判且分布不是top-k时true，adapter的true不能跳过Core校验。native mask_probs可optional映射confidence tensor，未绑定不消费。

`CanonicalOutput`固定schema=`ai.final-item`，v=1：`{schema,v,itemId,sequence,taskKind,inputNames:[string],prepared:[PreparedInput],classMap:Ref?,complete,truncated,rejection:Rejection?,ood:OptionalScore,explanation:Explanation,optionalOutputs:[OptionalOutput],data:TaskData}`；inputNames按ordinal且等于该item.Values名；prepared同raw实际证据。`Rejection={reason,observed:double?,threshold:double?}`（reason只允许LowScore/Ood/InsufficientVisibleDomain/ZeroNorm/RequiredOodMissing/LowMargin）；`OptionalScore={state,value:double?,threshold:double?,isOutOfDistribution:bool?}`，state=Provided/NotProvided/NotApplicable，非Provided后三者null；Provided score/threshold有限，isOutOfDistribution严格score>threshold，阈值须与模型读回及post.ood一致。`OptionalOutput={tileId,name,state,tensor:Tensor?}`且state=Provided/NotProvided；`Explanation={state,method,targetClassId:string?,scaling,heatmap:Tensor?}`，只有Provided带热图，独立附属输出，不覆写主data。非成功item只可带供诊断的原score/拒识data，消费者以InferenceItemState=Completed作为可消费前提；Missing/Failed/Cancelled/Unknown载荷为空，不编码成零候选。

| taskKind | TaskData的全部字段与数量关系 |
|---|---|
| classification | `{scores:[Score],distributionComplete,selectedClassId:string?}`；`Score={classId,value,scoreKind,calibrated:double?}`按classId ordinal，distributionComplete与C覆盖一致；selected必须在scores和类表中 |
| multi-label-classification | `{scores:[Score],selectedClassIds:[string],distributionComplete}`；selected按classId ordinal，多个/零个合法，完整scores不能被nativeSelected代替 |
| detection / instance-segmentation | `{candidates:[Candidate],suppressed:[Suppression],coordinateInput}`；`Candidate={id,classId,score:Score,polygon:[[row,col]×4],mask:Tensor?}`，检测mask=null，实例必需；id=`itemId/tileId/原候选序号`按已定score排序仍保留原ID。`Suppression={removedId,retainedId,iou}`有限[0,1]；mask在coordinateInput原HW域，逆nearest且使用prepared对应validity，截断和无效区域均可见 |
| segmentation | `{shape:[H,W],classIds:[string?],confidence:[double?]?,validity:[0\|1],coordinateInput}`，全数组长HW，invalid处class/confidence=null；valid处类表合法，不填背景；confidence未提供整体null |
| anomaly | `{scoreMap:Tensor,imageScore:double,scoreKind,validity:[0\|1],coordinateInput}`，scoreMap f64[H,W]、validity长HW；invalid值只可作不可消费占位0且mask=0，不纳入阈值/区域/coverage；imageScore保留实际backend整图值，不由tile max冒造 |
| embedding | `{dimension,vector:[double],normalization,metric}`，dimension=D且vector长D、有限，l2零向量拒识；metric与模型版本留作同源对照 |
| ocr-comparison | `{rawText,symbols:[{id,text,score:double?,polygon:[[row,col]×4]?}],geometryState,dictionary:Ref}`；字符按greedy CTC保留的time排序；缺geometry显式NotProvided和polygon=null，不能凭字序估框；字典固定`ai.ocr-dictionary={schema,v,symbols:[string],blankIndex}`，symbols唯一且UTF-8合法、blankIndex在[0,C)，每time scoreKind=Probability仅单time softmax值 |

final输出再次按canonical编码/核schema/bytes预算并计算OutputSha256，输出定义hash和model manifest hash均保留；不接受codec另造字段或重命名schema。例：分类classMap IDs["0","1"]，raw classIds=[1,0]、scores=[0.8,0.2]，final按IDs["0","1"]重排且selectedClassId="1"；重复ID/长度不等拒绝，不能按第一个scores绑定类"0"。多tensor例：generic inputs=[image,metadata]，values两者名齐全；outputs scores[C]和aux:diagnostic[2]各自绑定，aux optional缺失只记NotProvided，不把aux[2]误当二类scores。模型开发者只填现有结构的真实layer/shape/参数与样本，不重做Core schema设计。

## 7. 兼容、配置与版本

公开 API 遵循语义化版本；正式程序集名称、包 ID、目标平台/RID、依赖版本、强名称/签名、序列化格式及支持矩阵在批准的发布记录冻结。当前项目目标 .NET 10；脱离平台接入的其他视觉项目按该模块实际目标框架兼容策略明确适配，不把平台 UI/私有类型带入核心。

请求、结果、模型闭包、预处理、后处理、适配器能力和运行回执分别带 schema/version。新增可选字段必须有明确缺省语义并通过旧客户端契约测试；改变数值含义、坐标约定、score 语义、item 关联、错误/状态或取消行为属于破坏性变化，提升主版本并提供迁移说明。未知未来字段不得默默忽略后继续生产用途；能力协商不匹配为 `Rejected/AdapterNotReady`。

运行配置不可变并随结果记录有效版本。任何变更模型、运行设备、精度、batch、输入解释、阈值或后处理规则都形成新的计算身份/配置修订。旧实例不热改；先建新 generation，验证后由宿主切换，新旧排空独立跟踪。

## 8. 无 UI 调用示例与两消费者验收

以下为模块 v0.3 的宿主调用形状；变量由宿主显式注册，不是现有代码或已执行示例。所有类型在附录 A 定义；authenticatedConsumer与数值上限由可信装配根提供，purposeGate/backend是该engine专属实例，不从request认领身份。示例禁止把应用判定塞入核心：

```csharp
InferenceEngineOptions engineOptions = new(
    MaxItems: maxItems, MaxRank: maxRank, MaxIdentityChars: maxIdentityChars,
    MaxTraceChars: maxTraceChars, MaxOperations: maxOperations,
    MaxDiagnosticEvents: maxDiagnosticEvents,
    MaxDiagnosticsPerOperation: maxDiagnosticsPerOperation,
    TrustedConsumer: authenticatedConsumer, PurposeCheckTimeout: purposeCheckTimeout,
    MaxConcurrentPurposeChecks: maxPurposeChecks, InstanceBudget: instanceBudget);
IAiInferenceEngine engine = AiInferenceEngineFactory.Create(
    engineOptions, new InferencePorts(modelResolver, inputProvider, budgetPort,
        backend, taskCodec, purposeGate, diagnostics), timeProvider);
var request = new InferenceRequest(
    RequestId: new InferenceRequestId(requestId),
    Consumer: authenticatedConsumer,
    Purpose: approvedPurpose,
    Attempt: attemptReference,
    Model: exactModelReference,
    TaskKind: "segmentation",
    Inputs: frozenInputs,
    Preprocess: exactPreprocessReference,
    Postprocess: exactPostprocessReference,
    BackendPolicy: approvedBackendPolicy,
    BatchPolicy: new InferenceBatchPolicy(MaxItems: 1, MaxWait: TimeSpan.Zero),
    MonotonicDeadlineTimestamp: deadlineTimestamp,
    DeadlineUtc: deadlineUtc,
    ResourceBudget: boundedBudget,
    TraceContext: null);

InferenceResult result;
try
{
    InferenceValidationResult validation = engine.Validate(request);
    result = await engine.InferAsync(request, cancellationToken); // 同一校验；拒绝为结构化结果
    InferenceOperationStatus query = await engine.QueryAsync(request.RequestId, CancellationToken.None);
    // Query.Result仅在已接纳终态且当前用途允许时非null；validation/query不是质量判定。
}
finally
{
    DrainReceipt drain = await engine.DrainAsync(
        new InferenceDrainRequest(drainWaitBudget), CancellationToken.None);
    if (drain.AllOperationsDrained) await engine.DisposeAsync();
    else KeepEngineForDrainRetry(engine, drain); // 宿主保留引用、查询和重试排空；不得 Dispose
}
// The caller correlates CanonicalOutput with its task schema and applies domain rules.
// Persisting evidence, machine decisions, release and device actions stay outside.
```

同一个无 WPF 核心必须由两个不同消费者完成接入验收，不能仅用两个测试名代替：

1. 缺陷候选消费者：调用方提供已绑定的图像/ROI/模型闭包，接收分类/分割/检测候选；调用方自行关联目标、结合确定性视觉证据并决定是否提交或复核。模块只返回候选和缺项/拒识。
2. OCR 对照或通用工程辅助消费者：分别由独立宿主注册合适的通用模型适配器，消费原帧/文本候选或工程候选；期待文本、字符语法、工程采用和产品流程由调用方负责。OCR 专用 Deep OCR 若复用既有专用能力，不得由本模块重复持有。

两宿主需证明相同核心程序集/契约可用，且不同参数、取消订阅、语言/诊断配置相互隔离；不得引用产品 VM、私表或依靠全局容器隐式初始化。

### 8.1 正常、边界与失败案例

| 情况 | 输入/触发 | 模块期望 |
|---|---|---|
| 正常单项 | 已授权模型闭包、合法 ROI、完整预/后处理规范、后端可用、单 item batch | 在 deadline 内完成；返回实际配置、候选/合法零候选、阶段耗时和完整来源；不产生外部副作用 |
| 正常短批 | 两个兼容 item，达到等待上限前未满 `maxItems` | 在等待上限或最早 deadline 前发短批；逐 item 返回稳定关联，不因未满批悬挂 |
| 边界输入 | 12 位图、非紧 stride、ROI 触及边界、padding 后输出、候选数达到上限 | 依据冻结规范转换并保留有效域；padding 不计覆盖；达到上限时显式标记截断，不能报告“无其他候选” |
| 边界并发 | A/B 共批，A 取消或 deadline 到期，B 仍可完成 | A 的取消/未知只作用于 A；B 保持原关联；共享 native/输入资源在最后使用后才释放 |
| 失败配置 | 模型 hash 不符、类表缺失、shape 不匹配、用途未授权 | `Rejected`，带 `ModelIntegrityMismatch/ModelNotReady/InputShapeMismatch/PurposeNotAllowed` 等具体诊断及字段定位；不创建或继续使用无效实例 |
| 失败运行 | native OOM、设备丢失、输出 NaN/重复 item、后处理关联丢失 | `Failed` 或 `ExecutionUnknown`，保留原 attempt 和资源诊断；禁止降分辨率、减 tile、换旧模型或填空候选继续生产 |
| 失败交接 | 提交响应丢失或取消与提交竞争 | 查询原操作/回执；不换 operation key 重跑，不以取消抹去已提交事实，未知保持 Unknown |

## 9. UI 适用性与宿主诊断投影

本模块交付 Core、Simulator 与后端适配器，无独立 UI、窗口、Dispatcher、主题或语言切换控件。当前无独立诊断控件消费者；本轮 WPF/DevExpress 25.2.3 控件/API、布局、截图及1920×1080 UI 验收不适用，不为满足审查凭空新增 UI 工程。宿主可按自己的 PageContract 展示不可变结果/状态，显示层不得调用 native 或拥有生产配置。

诊断仅返回稳定 `Code/MessageKey` 和参数，不返回拼接的用户文案。宿主语言资源覆盖 zh-CN/zh-TW/en-US，例如“推理已完成 / 推論已完成 / Inference complete”“正在释放资源 / 正在釋放資源 / Releasing resources”“输入格式不符 / 輸入格式不符 / Input format mismatch”；关闭页面只撤观察，取消操作须显式触发 request token。未来确有独立控件复用计划时先在本指导补任务流和 PageContract 后单独准入，不能把控件初始化变成 Core 前置。

## 10. 测试矩阵与验收

以下为实现阶段的必验矩阵，不表示已经执行：

| 类别 | 输入/触发 | 必须断言 |
|---|---|---|
| 参数 | 空模型、无用途、负维、乘积溢出、NaN、越界ROI、超限队列 | 拒绝并指出字段/错误类；未创建 native 资源 |
| 输入语义 | 同字节 RGB/BGR、8/12/16 位、不同 stride/shape/mask | 身份与预处理正确区分；禁止隐式缩放/布局猜测或错误缓存命中 |
| 模型闭包 | 缺依赖、hash不符、未知schema、无用途资格 | Rejected及具体ModelNotReady/ModelIntegrityMismatch/PurposeNotAllowed；不加载 latest、不运行未批准用途 |
| 输出 | 缺项/重复 item、NaN、未知类、错 shape、非法坐标、空合法输出 | 逐项关联正确；结构坏失败；合法零候选仅满足完整性约束才有效 |
| 后处理 | 阈值相等、NMS相等、边缘框、padding、tile seam、候选截断 | 稳定确定结果，原坐标/mask正确，截断不可伪装无候选 |
| 并发/批次 | 单 item、短批、满批、换同伴、不同 shape、热切换 | deadline 内进展；不兼容项分开；旧代结果不进新代；实例无未验证并发 |
| 取消/超时 | 排队前/后、native 中、共批单项取消、提交等待、关闭观察者 | 兄弟项不受影响；native 未结束不释放资源；已提交事实不被取消抹除 |
| 故障 | OOM、GPU lost、适配器崩溃、迟到回调、驱逐竞争 | 明确 Failed/Unknown；隔离旧实例；资源仅在真实最后使用结束后释放 |
| 观测/安全 | 事件订阅抛错、事件乱序/重复、敏感内容 | 推理不受观察者影响；request/item 可关联；日志无图像像素/秘密 |
| 多宿主 | 缺陷候选 + OCR 对照/工程辅助独立宿主 | 同一包无 UI 可调用；配置/取消/结果相互隔离；领域语义留宿主 |

### 10.1 两种反例视角和具体样例

本轮从两个独立视角逐能力走查：**数值/语义视角**查输入解释、完整域、类别关联、多候选、弱信号/遮挡、参数改变和模型输出；**外部宿主/执行视角**查契约闭合、租约、队列/并发、取消/超时/迟到、断连、关闭、版本回退及第二消费者。前者不能用Task完成代替输出正确，后者不能用正确数组代替资源已归还。以下全部为未来测试要求和合成边界样例，本轮未运行C#/HALCON测试。

| 未来测试文件/方法（工程归属见§10.2） | 输入与事件序列 | 必须断言 |
|---|---|---|
| `ContractTests.cs / ImageAndTensorDescriptors` | HW UInt8 shape[2,2]、strides[2,1]、bytes[10,20,30,40]；另F32向量[3,4] shape[2] stride[4] | 前者lastOffset=4，后者=8；Input.Values各Source内容hash核自身bytes，输入解释不混同；stride[1,1]别名、短buffer、负维、checked overflow拒绝 |
| `TaskCodecTests.cs / ClassificationAndAbstention` | 完整A/B分数0.2/0.8，校准identity/Probability；接纳阈值0.8；另遮挡或域外标拒识 | B在等号处被接纳；0.7999拒识；unknown class/NaN失败；拒识原因保留且无可消费候选；empty raw字典失败，合法零检测单独有效 |
| `TaskCodecTests.cs / GeometryAndTileCoverage` | 两个同类轴框IoU恰等阈值、同分；一个padding框；缺一个tile；旋转框 | 同分固定ID序，IoU等号不抑制；padding不成为有效像素；缺tilePartial；旋转框无已批准精确方法则拒绝，不按轴框近似 |
| `TaskCodecTests.cs / SegmentationEmbeddingAndText` | segmentation 2x2含Unknown角；embedding[3,4]与[0,0]；OCR原低信文本 | Unknown不填背景，L2=[0.6,0.8]（由fixture浮点容差断言）/零向量拒识；原文不被grammar改写；多标签独立两类可同时接纳 |
| `AdmissionTests.cs / LimitsDuplicateAndMutation` | 超MaxItems/队列/MaxOperations、CPU backend GPU budget=0，已接纳ID再次Infer，caller改变原builder | 上限拒绝且无第二Run；0表示禁用GPU而非无穷；ImmutableArray快照不随builder更改；Query同ID读原结果；重复不发第二组事件；预拒绝ID修正后可接纳；NotFound.Result=null |
| `CanonicalSchemaTests.cs / ParseAndBind` | canonical完整fixture（manifest/pre/post/raw/output/classes）；同bytes改成员Name、unknown字段、duplicate key、v=2、非NFC、0/1e0非canonical、NaN、shape overflow；standard与generic两个input/多个output | 定义与DTO逐字段相等、重编码byte一致；RequiredOutputs对应逻辑slot而非apply参数；错误不进native；未绑定/错shape输出失败，aux不替代score，全部role/hash核一致 |
| `TaskCodecTests.cs / HalconDictionaryRoutes` | 标准分类/多标签完整C；检测N=0与mask缺项；分割invalid角；gc local/global成对；embedding vector；OCR CTC [a,a,blank,a]；两个tile重叠 | 多标签selected不当全分布；mask同序不挪候选；OOD score等于threshold不是域外；热图nested key只附属；CTC得到aa且不grammar；tile中心选择确定/缺tilePartial。仅模拟字典bytes，真实HALCON另验 |
| `AuthorityTests.cs / ExclusiveConsumerAndQuery` | HostA/HostB各独占engine；A request冒用B consumer；原A完成后用途撤权；知道A requestId的B | consumer不匹配Rejected/PurposeNotAllowed且无端口IO；宿主不得向B暴露A engine；A Query撤权Result=null、原State/Terminal不变；不声称Core能识别没有上下文的RPC租户 |
| `AuthorityTests.cs / HangingIoAndDrain` | fake time下Execute/Final/Query挂起；token或deadline到、迟到Valid；Drain与Query竞争；gate Stop abort后Check真正返回；Stop/Dispose先fault再恢复 | 查询等待取消不结束原operation；挂起Call计入实例，不能AllOperationsDrained；关闭后无新Check、Query只无载荷状态；Stop可先abort而非等所有Check；Call真实结束后才释放CTS/gate；fault重试幂等且不重复pending Task；无Call也须关闭gate |
| `LifecycleTests.cs / EveryFailureStage` | purpose、resolver、第二input、Prepare、Run、codec、lease Dispose分别注入失败 | 各阶段只释放已获资源；Prepare失败不丢内部native；Run失败也必须Drain；释放失败保持DrainPending，资源账不提前归零，终态事件恰一次 |
| `LifecycleTests.cs / CancelSharedBatch` | request A/B可兼容合批；A native期间取消，B完成；adapter迟发A回调 | A为Cancelled且无可消费迟到结果，B原身份完成；共享资源最后使用后释放，不能重用RunOptions取消B；逐item没有公开token入口 |
| `LifecycleTests.cs / TimeoutAndUnknown` | deadline到期，adapter Drain首回false，后证实停止；另断连后真实worker退出但输出不可恢复 | 首次Query=DrainPending/Terminal=null/Result=null；后分别TimedOut、ExecutionUnknown；两者ResourcesReleased=true；无退出证明永久保留未知排空观察 |
| `LifecycleTests.cs / StopAndDisposeRace` | Drain与新Infer并发，Drain wait token取消，再次Drain；提前Dispose | 线性化前接纳全部排空，之后Rejected/AdmissionStopped；取消等待不恢复接纳；提前Dispose fault且保留资源；无operation时实例cache尾段仍须释放；backend独占归本engine，宿主其它端口不被Dispose；shutdown/Dispose失败需可重试且不发成功回执 |
| `VersionCacheTests.cs / IdentityAndRollback` | 同像素改layout/pre/post/runtime/用途/类表；可选缓存命中；旧代迟到；回退 | 变化不误命中；缓存hit标FromCache、原计算ID及原实测，当前native时长NotExecuted；旧代不串新代。外部备用新attempt/new request，不覆盖原失败 |
| `HostContractTests.cs / TwoIndependentConsumers` | HostA缺陷候选 HW图像分类/检测；HostB工程辅助 F32 embedding；各独立配置/授权/诊断/语言 | 相同Core程序集、无WPF/产品私表/native引用，HostA不释放HostB资源；第二host结果不作身份认证/放行。多标签/分割/异常/OCR各以其任务fixture覆盖，不用两个测试名冒充真实消费者接入 |
| `ResourceTests.cs / LongRunAndObserverFailure` | 有限请求数/代次循环，观察者抛错/缓慢，event队列满，输出持续保留达到实例上限 | 不忙等、不无限Task/事件/缓存；observer故障不改推理结果；满队列拒绝/丢观察有诊断，最终结果可Query；正常排空租约归零；长稳测量按Profile判，未测不称无泄漏 |

不让codec的mock接受任意bytes掩盖真实schema缺口：Core/Simulator使用上述完整fixture schemas；真实Adapter每种模型任务按§6.4–6.6固定schema填实际layer/shape/类表/训练参数及同样本Golden，不另设计raw/final schema，未提供仅阻断该任务适配，不改变已经冻结Core类型。两消费者的最小宿主分别在测试工程独立装配根构造 ports/options/timeProvider，每个engine绑定自己的TrustedConsumer、exclusive purposeGate/backend，先Validate→Infer→Query核Result→Drain（关闭后Query只能读无载荷状态）→Dispose；不从平台DI/静态容器读配置。后续真实宿主消费本程序集并注册自身公开适配器，不需要复制Core代码。

纯 Mock 不能替代后端输出格式、native 释放和实际双消费者接入验证。无适用硬件时，真实后端、GPU/驱动、工业样本与生产用途资格分别标为未验证，不冒称现场通过。

### 10.2 测试工程与执行命令

Core 与 Simulator 首版测试冻结为 `Microsoft.NET.Sdk`、`net10.0`、`OutputType=Exe` 的 BCL harness，沿用 DEV-GOV-010 §3.1 的仓库执行约定，不再留待实现时选择测试栈。两个唯一测试工程路径分别见 A.3 和 A.5；均无 `PackageReference`，Core.Tests 仅以 `ProjectReference` 引用本模块 Core，Simulator.Tests 仅引用本模块 Core 与 Simulator。断言为测试工程自身的方法，不使用 xUnit 属性或测试发现机制。

§10.1 的 `ContractTests`、`TaskCodecTests`、`CanonicalSchemaTests` 归 Core.Tests；`AdmissionTests`、`AuthorityTests`、`LifecycleTests`、`VersionCacheTests`、`HostContractTests`、`ResourceTests` 归 Simulator.Tests。各入口显式调用所属表中全部方法，表中的 `文件名/方法名` 是稳定用例 ID；每行的所有反例、事件序列和断言均须执行，不能只运行正常分支。Simulator 使用固定时钟、可控制异步闩锁及完整 schema fixtures；通过手动推进时钟和明确完成屏障验证真实软件生命周期，不用 sleep 或仅有 Task 完成证明数值、排空或归还成立。

以下命令从仓库根目录执行，适用于工程获准创建后的验证；本轮工程尚未创建，未运行这些命令：

```powershell
dotnet build src/Modules/ai-inference/Asun.Modules.AiInference.Core/Asun.Modules.AiInference.Core.csproj -c Release
dotnet build src/Modules/ai-inference/Asun.Modules.AiInference.Simulator/Asun.Modules.AiInference.Simulator.csproj -c Release
dotnet run --project tests/Modules/ai-inference/Asun.Modules.AiInference.Core.Tests/Asun.Modules.AiInference.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/ai-inference/Asun.Modules.AiInference.Simulator.Tests/Asun.Modules.AiInference.Simulator.Tests.csproj -c Release
```

每个用例另设 60 秒真实时间安全截止，执行器对每个测试工程设 600 秒外层进程超时；这是 harness 防挂起上限，不是推理节拍或性能验收值。用例超时须报告其 ID 并返回非零，外层超时须由执行器判失败，即使取消等待后任务仍未结束也不能返回成功。任一断言失败、未完成或必需项跳过均返回非零并列明用例 ID；只有所属全部用例完成通过才返回 0。`dotnet test` 不执行这些 Exe，不能用其无报错代替以上验证。

上述栈只覆盖纯托管 Core 与确定性 Simulator。A.5 的 HALCON Adapter 测试切片仍须绑定真实 ImageLibDotNet、模型/Golden、实际输出与 native 资源释放验证；本节不把模拟字典或 Core harness 当作真实 HALCON、GPU、进程隔离、性能或现场资格证据。

## 11. 性能预算与可观测性

对每个用途 Profile 记录负载（宽高、通道、位深、stride、ROI/tile、模型、后端、batch、并发和冷/热）、执行设备/软件版本、输入完整性与样本来源。预算分别给队列等待、预处理、host-device 传输、native 执行、后处理、总延迟、吞吐、CPU、托管/native/pinned/GPU 峰值、队列/输出保留和长时资源斜率；报告 P50/P95/P99、超时/拒绝/拒识与峰值。

没有客户/用途 Profile 数值时不宣称满足节拍或工业性能；实现验收先验证每阶段可测、有界、资源最终回收，目标值由用途 Owner 冻结。异步 GPU 需测真实完成时点，enqueue 时间不能作为推理延迟。模型量化、增加线程/实例/batch 或切换设备需在相同冻结样本上比较数值输出、阈值附近行为、拒识、尾延迟和资源。

结构化诊断至少包括 request/item/attempt 关联、闭包摘要、适配器与实际配置版本、状态修订、队列与阶段时长、候选计数/拒识/缺项/截断、资源测量范围、取消请求/真实结束/排空时间及稳定错误码。日志禁止记录原始图像、模型秘密或未授权客户字段；敏感关联用受控标识或摘要。

### 11.1 测点、预算与统计执行计划

每个 BenchmarkProfile 绑定 workload/schema/model/pre/post/runtime哈希、宽高/通道/位深/stride、ROI/tile与item数、configured/submitted batch、并发、冷装载/预热与热态、样本计划及资源限制。统计方法唯一引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不另设分位算法。阶段测点为接纳→Execute用途检查真实开始/结束→队列开始/结束→模型解析→input acquire→prepare/预处理→真实native开始/完成→解码后处理→FinalDisclosure真实结束→backend drain确认→input/model/budget归还→ResourcesReleased；端到端从接纳到ResourcesReleased，另记录请求取消到真实排空与最后归还、Query wait/authority IO真实结束及gate Stop/Dispose（后者instance scope）。排空未知、失败、超期和未读样本单列，不只统计成功请求。

`InferenceObservation` Measured才带有限非负value（真实0有效），NotExecuted/Unsupported必须null；Unit固定为`ms/bytes/count`对应指标，Scope为`request/instance/backend/device/calling-thread`，MethodVersion记录采集方法版本。单线程分配差不代表进程/native/GPU总峰值；共享批次真实延时不按item均分伪造单项实测，device peak明确是设备观察域而非单request费用。adapter报告配置batch/submitted item/generation与runtime；Core记录自己的队列、解码、资源归还，重叠阶段不相加冒充端到端。FromCache保留原计算来源，只能复制原计算的实测，不标本次真实推理；本次native observation为NotExecuted，缓存读取单独测量。

CI纯Core比较参数规模、并发和故障下的有界性、终态/租约不变量；HALCON Adapter在同一冻结图像集合比较whole/已定位ROI/tile、CPU/GPU/优化变体（只有已批准变体参与），包含弱信号、遮挡、密集目标、边缘及多模型代次；需同时报告输出偏差、误接受/拒绝、尾延迟和峰值。输入/输出/临时/native/GPU任一维越预算为失败，不用一维余量抵扣另一维；绝对峰值与长时斜率、句柄/队列都记录。样本数、预热数、容差/目标阈值与时窗由具体用途Profile采纳，缺失则NotEvaluated；无此证据不称最快/达到节拍。

## 12. 发布、回退与故障恢复

模块发布包应固定程序集/依赖版本、目标架构/RID、后端能力清单、模型闭包兼容范围、API/schema 主版本、校验和、构建来源、变更说明、已验证用例及明确未验证项。HALCON/AsunImage 适配器随对应部署环境提供，不在本模块任务中下载、改造或替换依赖。

升级顺序：离线构建与静态/契约测试 → 固定挑战集对比 → 两个无 UI 宿主接入 → 受控 Replay/Shadow → 按用途 Owner 批准后才可用于相应用途。每阶段明确输入版本、回退点与成功条件。模块不得自行推动用途升级。

回退恢复上一已验证程序集/适配器/运行配置和已绑定模型闭包；在途请求先停止新接纳并排空或隔离，旧 generation 不混入新 generation。未知运行不可通过启动旧 DLL 假设已停止；先按适配器/宿主可信边界查询或终止隔离进程，再释放仍被持有的资源。模型文件和历史证据不随软件回退删除。

## 13. 接入步骤与设计准入

1. 主会话已按 DEV-GOV-010 §3.1 接收 A.5 的 Core/Simulator v0.3 六项文档规格，状态为 `ModuleCoreImplementationReady`（规格准备）；实际开工仍须绑定权威代码仓库、分支及明确派发的精确切片。本轮仅收口指导，不进入实现。
2. 获准后先在 A.3/A.5 指定工程构建无 UI Core 和确定性 Simulator。按 A.1/A.4 冻结接口实现纯校验、接纳/查询、预算、并发、取消、失败、排空及实例关闭的完整生命周期；异常恢复属于首个闭环，不后置。
3. 用 §10.1 的任务 fixtures、fake time 和完成屏障核类型/数值/状态/资源不变量及两个独立装配根；模拟结果只证明软件契约，不证明真实 HALCON 或现场能力。
4. 对获批真实任务，资产/用途 Owner 提供精确模型闭包、训练同源预后处理、实际layer/key/shape值（标准task键已在§6.5冻结）、坐标事实、资格和负载 Profile；依 §2.5/§6.3 经 AsunImage 实现对应 Adapter，核公开调用与目标运行时行为。仅在 HALCON 存在具体缺口时评估固定版本外部后端。
5. 宿主接入 A.4 模块端口；平台 DTO/序列化、跨模块锁序、跨进程终止证明和事实提交仍由各自 Owner 映射，不复制其状态或 Store。两个真实无 UI 消费者各持自己的授权、模型、预算和结果关联；本模块没有 UI 交付切片。
6. 分切片运行 §10、§11 的实际验证，依已有交付流程记录结果与未验证项。真实 Adapter/Golden/性能及两消费者证据齐全后才评估用途准入，不把本文 DesignReview/Prep 改称实现或生产通过。

模块自有 DTO、端口、状态/事件、取消线性化、查询和资源释放顺序已在 A.1/A.4及§4–5冻结；这些常规 Core 技术决定不再列为外部 Owner 待裁决项。尚未提供的平台映射、真实模型layer/shape/训练参数与 Profile、实际 runtime 证据、其它 .NET/RID组合、真实第二宿主接入仅阻断对应集成或部署切片。外部 worker 及其跨进程协议是未批准可选范围，不是已接收 Core/Simulator 的规格缺口；这些条件不撤销 Core/Simulator 六项规格接收结论。

## 14. 自审

- 核心职责限定为模型推理执行及其输入绑定、输出完整性和资源生命周期；无训练、业务目标生成、质量规则或设备动作。
- 缺陷候选与 OCR/工程辅助只作为外部消费者示例，没有制程阈值、PCB/SPI/AOI/点胶/涂覆判定、私表或产品 VM 类型。
- HALCON 26.05/AsunImage 优先且不猜未确认签名；Deep OCR 专用能力留在原 OCR 边界。
- 无 UI 可调用为强制条件；UI、持久化和调用方业务逻辑都是可选外接面。
- 状态仍为 `DesignReview / Prep`；本文没有声称功能实现、测试执行、现场验证或生产资格。

## 15. 本轮复审结论与精确剩余门

本轮以数值/语义和外部宿主/执行两种反例视角走查 §6.1 全部场景，修订唯一指导。已关闭的规格缺陷：Image/Tensor及不可变集合/布局契约、明确端口和工厂、原始输出请求关联、结果查询、重复 ID 不产生第二终态、请求与实例两级排空/缓存关闭、取消/超期归约、任务预后处理及坐标/有效域、实际来源和分域测量、测试/工程落点；退修补入Canonical v1精确字段/解析、标准HALCON键/named多tensor绑定、可信宿主独占查询边界、authority IO有限等待/迟到/abort与Stop/Dispose恢复。HALCON 26.05 分支、分类解释限制和固定上游源码/测试的可移植思想已写入 §2.5/A.6；无 UI 的适用性见 §9。本轮没有产品实现、C# 编译或真实后端测试结论。

后续门按受影响切片区分：

1. **Core/Simulator 规格已接收**：2026-10-09，主会话 `01a1020f-126c-7242-97f9-0f50b4cd3553` 内容复核 §1–15及附录 A，接收 Core/Simulator v0.3 的 DEV-GOV-010 §3.1 六项文档规格，准入为 `ModuleCoreImplementationReady`（规格准备）。Canonical v1、named 多输入输出、HALCON 标准键、可信主体查询及有限等待/关闭/迟到回执规格均已接收；适用切片仅 A.3/A.5 的纯托管 Core 与确定性 Simulator（含 Core 公开适配端口契约），不包含真实 Adapter、外部 worker 或生产用途资格。实际开工仍须绑定权威代码基线并明确派发，不以本次接收声称已实现或验证。
2. **HALCON Adapter 指导内容限定接收**：2026-10-11，主会话 `01a1020f-126c-7242-97f9-0f50b4cd3553` 已回读 C.1–C.7 及 C.6.1，限定接收确定 HALCON Adapter/原Owner桥/公开装配指导：factory/options、ModelBinding、物化、能力/配置读回、单lane/预热、原Task与根保持、原Owner释放、两完整强类型无UI Host、当前披露及两轴有限Cleanup/Resume。不再列作客户设计欠账；此接收不是实际Adapter实现或资格通过。真实任务仍须精确模型/成员 hash、实际generic层名/shape、标准键读回、类表、训练同源 pre/post、坐标/有效域、用途资格及 Golden。缺失仅阻断该任务；不编造客户或训练事实。
3. **用途/性能门**：每个部署 Profile 采纳实际 CPU/GPU/native/内存、延迟/吞吐目标及样本/容差，实际测得后才判断达标。派生精度/备用模型由资产与用途 Owner 提供新闭包/转换及资格证据，推理模块不批准政策。
4. **平台/真实宿主接入门**：原 Owner 映射平台 DTO、Schema、错误码传输编号、跨模块锁序及提交回执；第二消费者提供真实输入、模型、授权和配置并独立接入。同一 Core 的两装配根是软件测试，不是已完成真实消费者验收。
5. **可选部署范围门**：外部后端需要具体 HALCON 能力缺口与批准版本/发布闭包；worker 需要获批 IPC、崩溃恢复和可信退出协议；其它目标框架/RID需单独兼容依据。未批准切片不自动实施，UI当前不适用。

本会话只维护本指导；跨文件入口、共享候选映射或进度由主会话处理。本次准入变更依据上述主会话接收结论，不由模块自审授予。实际模型属性/用途事实、HALCON/native/GPU、Golden、真实双消费者、性能和现场资格仍未验证；模块整体保留 `DesignReview / Prep`，规格准备不替代实现、性能、HIL或生产验收。

### 15.1 当前全部批准范围结论（2026-10-12，原永久会话）

以上主接收记录保留为原日期/版本的历史依据。本轮按现行规则由本模块原永久会话自行内容审核、修复和文档验证，不再等待总控代做内容复核，也不把自审升级为代码或资格接收。

全部当前批准范围为 A.5 的 Core、Simulator、附录 C 确定 HALCON Adapter/公开来源桥/无 UI 宿主装配指导。内部可决定软件设计已闭合：职责/Owner、全部中性任务、严格 codec、工厂及受控 Simulator、资源/并发/取消/恢复、预处理/输出、物化、工程/发布、测试与性能测点均有唯一实施位置。增量为 A.7 的可调用装配入口与夹具规则、C.3/C.4/C.5 的路径/区域/设备所有权细化及 C.8 的 model-assets 0.3.1-prep 精确消费关系；不修改已接收 DTO、数学算法、Canonical schema、旧样例或测试命令。没有以“未来 Owner 再设计”保留内部软件欠账。

| 精确外部门 / Owner | 必须交接或验证的内容 | 仅阻断范围 |
|---|---|---|
| 权威代码基线 / 平台仓库 Owner及派发者 | 当前无 Git 元数据；实现开工绑定可审计仓库/分支或用户确认代码快照及 A.3/A.5 切片 | 产品工程创建/修改；不阻断文档准备 |
| 模型与数据事实 / 模型生产者、model-assets 及输入 Owner | 精确成员/hash、实际模型属性/named层/shape/类表、训练同源 pre/post、真实坐标/有效域；C.8 的新格式映射只在实际选择时由生产者完成 | 缺交接的该模型/输入路线；不能捏造占位内容 |
| 当前执行/披露与用途 / authorization接入Host、AI治理及用途 Owner | 受信 principal/consumer、当前权限、用途证据/撤回策略；资产读权限不代替用途资格或结果披露 | 对应主体、用途及该次结果披露 |
| 真实环境/性能/Golden / Adapter实施者、部署Host及模型验证 Owner | 本项目编译、HALCON/native/GPU、读回/数值/释放、独立真实 A/B 消费、冷/热 P50/P95/P99及峰值；容差/目标从真实 Profile 交接 | 对应 Adapter/模型/环境的运行与达标声明；不是软件设计外包 |
| 客户/生产资格 / 客户工艺与质量 Owner、现场接入Host | 代表样本、漏检/误检与用途验收值、现场资源/操作/恢复和质量放行依据 | 对应生产用途；模块从不授予放行/设备权 |

已复用原固定研究、Core/Simulator六项及附录 C 既有两轮自审/向量；本轮新增规格再从公开类型/字段/限制和外部 Host/原 Task/失败/释放两个视角有限自审，并做围栏、类型唯一性、链接、上游消费与旧段落修改范围定向静态验证；原C#/PowerShell全部块拼接SHA-256仍为 `1f5c65484de3175cd7a934ecb99089e67c2e5e0e07b840e2edd14b40cc17bf9a`（排除A.7两个新增声明块），旧DTO/Host样例/命令未改。尚未创建产品/测试工程，未编译 C# 契约块，未运行 Core/Simulator/HALCON、Golden、真实双消费者、性能、WPF 或现场验证。无独立 UI/诊断控件消费者，不直接消费 viewport，viewport 0.3.4 装配及本模块 UI 1920×1080 验证为 NotApplicable。外部后端、worker、缓存、自动参数推荐和新增 UI 仍未批准，不列为当前内部欠账。

## HALCON 26.05 算子资料入口

实现 HALCON 深度学习推理适配时，使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 作为目标版本 26.05 的资料入口。本轮实际核对页面：

- `apply_dl_model.html`：`apply_dl_model( : : DLModelHandle, DLSampleBatch, Outputs : DLResultBatch)`。
- `read_dl_model.html`、`get_dl_model_param.html`、`set_dl_model_param.html`、`clear_dl_model.html`：模型装载、参数读写和清理。
- `optimize_dl_model_for_inference.html`：模型、设备、精度、样本和通用参数到转换模型及报告。
- `transform_dl_sample_batch.html`：变换管线到 DLSample 结果批次。
- `gen_dl_model_heatmap.html`：模型、单样本、热图方法、目标类和通用参数到解释结果。
- `query_available_dl_devices.html`、`get_dl_device_param.html`、`set_dl_device_param.html`：设备查询和参数边界。

这些页面和 `ImageLibDotNet` 公共签名只确定可核对的路线与参数形状，不替代目标运行时对字典键、默认值、线程、超时、中断、设备占用和资源排空的实测/资格证据。
## 附录 A：模块核心 API Contract v0.3（Core/Simulator 规格已接收；逐切片准入）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.3` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- 适配器按 HALCON 26.05 算子语义实现，经 `ImageLibDotNet.cv2` 使用既定依赖；实际 C# 参数歧义只影响对应调用，不阻断 Core/Simulator，也不重复核验算子是否存在。
- 准入状态：Core/Simulator v0.3 为 `ModuleCoreImplementationReady`（规格准备）；主会话接收依据和适用范围唯一见 §15。公开适配端口契约已接收，不代表真实 HALCON Adapter、模型/用途事实或部署资格已验证；实际开工按 A.3/A.5 精确范围另行派发。

### A.1 Core 公开类型与边界

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;

namespace Asun.Modules.AiInference;

public readonly record struct InferenceRequestId(string Value);
public readonly record struct InferenceItemId(string Value);
public readonly record struct InferenceStableReference(string Owner, string Id, string Revision);
public readonly record struct InferenceContentReference(
    InferenceStableReference Identity, string SchemaId, string SchemaVersion, string Sha256);
public enum InferenceInputKind { Image = 0, Tensor = 1 }
public enum InferenceElementType { UInt8 = 0, UInt16 = 1, Int32 = 2, Float16 = 3, Float32 = 4, Float64 = 5 }
public sealed record InferenceInputValueReference(
    string Name, InferenceContentReference Source,
    InferenceInputKind Kind, InferenceElementType ElementType,
    ImmutableArray<int> Shape, ImmutableArray<long> ByteStrides, long ByteLength,
    string Layout, string ChannelSemantics,
    InferenceContentReference? Roi, InferenceContentReference? ValidDomain,
    InferenceContentReference? CoordinateTransform);
public sealed record InferenceInputReference(
    InferenceItemId ItemId, int Sequence, ImmutableArray<InferenceInputValueReference> Values);
public sealed record InferenceBackendPolicy(
    string BackendId, string DeviceId, string Precision, InferenceContentReference RuntimeProfile);
public sealed record InferenceBatchPolicy(int MaxItems, TimeSpan MaxWait);
public sealed record InferenceResourceBudget(
    long MaxQueuedItems, long MaxInputBytes, long MaxTemporaryBytes, long MaxOutputBytes,
    int MaxCpuWorkers, long MaxNativeBytes, long MaxGpuBytes);
public sealed record InferenceRequest(
    InferenceRequestId RequestId, InferenceStableReference Consumer,
    InferenceStableReference Purpose, InferenceStableReference Attempt,
    InferenceContentReference Model, string TaskKind,
    ImmutableArray<InferenceInputReference> Inputs,
    InferenceContentReference Preprocess, InferenceContentReference Postprocess,
    InferenceBackendPolicy BackendPolicy, InferenceBatchPolicy BatchPolicy,
    long MonotonicDeadlineTimestamp, DateTimeOffset DeadlineUtc,
    InferenceResourceBudget ResourceBudget, string? TraceContext);
public enum InferenceValidationState { Valid = 0, Rejected = 1 }
public sealed record InferenceDiagnostic(
    string Code, string Field, string MessageKey, bool Retryable, string Stage,
    InferenceItemId? ItemId, ImmutableArray<string> SafeArguments);
public sealed record InferenceValidationResult(
    InferenceValidationState State, ImmutableArray<InferenceDiagnostic> Diagnostics);
public enum InferenceOperationState
{
    NotFound = 0, Validating = 1, WaitingForBudget = 2, Queued = 3,
    Preparing = 4, Running = 5, Postprocessing = 6, Draining = 7,
    DrainPending = 8, Drained = 9, ResourcesReleased = 10,
    Completed = 11, Partial = 12, Rejected = 13, Failed = 14,
    Cancelled = 15, TimedOut = 16, ExecutionUnknown = 17
}
public enum InferenceTerminalState
{
    Completed = 0, Partial = 1, Rejected = 2, Failed = 3,
    Cancelled = 4, TimedOut = 5, ExecutionUnknown = 6
}
public enum InferenceItemState
{
    Completed = 0, Rejected = 1, Failed = 2, Missing = 3, Cancelled = 4, Unknown = 5
}
public enum InferenceObservationState { Measured = 0, NotExecuted = 1, Unsupported = 2 }
public sealed record InferenceObservation(
    string Name, InferenceObservationState State, double? Value,
    string Unit, string Scope, string MethodVersion);
public sealed record InferenceExecutionEvidence(
    string Backend, string Device, string Precision, string RuntimeSha256, long Generation,
    int ConfiguredBatchSize, int SubmittedItems, bool FromCache,
    InferenceRequestId? OriginalComputation, ImmutableArray<InferenceObservation> Observations);
public sealed record InferenceItemResult(
    InferenceItemId ItemId, int Sequence, InferenceItemState State,
    InferenceContentReference OutputSchema, ImmutableArray<byte> CanonicalOutput,
    string OutputSha256, string? RejectionCode);
public sealed record InferenceResult(
    InferenceRequestId RequestId, InferenceTerminalState State,
    ImmutableArray<InferenceItemResult> Items, string? ActualBackend,
    string? ActualDevice, string? ActualPrecision, string ModelClosureSha256,
    bool OutputComplete, bool WasTruncated, bool ResourcesReleased,
    ImmutableArray<InferenceDiagnostic> Diagnostics, InferenceStableReference Attempt,
    InferenceContentReference Model, InferenceContentReference Preprocess,
    InferenceContentReference Postprocess, string TaskKind,
    ImmutableArray<InferenceExecutionEvidence> Executions,
    ImmutableArray<InferenceObservation> Observations);
public sealed record InferenceOperationStatus(
    InferenceRequestId RequestId, InferenceOperationState State, long StateRevision,
    bool NativeExecutionMayContinue, bool ResourcesReleased,
    InferenceTerminalState? TerminalState, ImmutableArray<InferenceDiagnostic> Diagnostics,
    InferenceResult? Result);
public sealed record InferenceDrainRequest(TimeSpan Timeout);
public sealed record DrainReceipt(
    bool InstanceStopped, bool AllOperationsDrained,
    ImmutableArray<InferenceOperationStatus> Operations, ImmutableArray<InferenceDiagnostic> Diagnostics);
public interface IAiInferenceEngine : IAsyncDisposable
{
    InferenceValidationResult Validate(InferenceRequest request);
    ValueTask<InferenceResult> InferAsync(InferenceRequest request, CancellationToken cancellationToken);
    ValueTask<InferenceOperationStatus> QueryAsync(InferenceRequestId requestId, CancellationToken cancellationToken);
    ValueTask<DrainReceipt> DrainAsync(InferenceDrainRequest request, CancellationToken cancellationToken);
}
```

`TaskKind`、输入类型、实际后端、精度和输出 Schema 必须由请求绑定的模型闭包逐项声明。`CanonicalOutput` 是有界、不可变的任务 Schema 编码；`InferenceItemState` 不是质量结论：`Missing/Unknown` 时载荷为空语义，`Completed` 才允许包含可消费输出。未知 Schema、缺少必需输出、关联丢失或摘要不符属于失败，不能作为可消费候选。预接纳拒绝的 `ActualBackend/ActualDevice/ActualPrecision` 为 `null`；实际执行发生时必须记录实际值；接纳后尚未装载/运行的失败或取消仍为 null，并诊断原因，不能将请求路线当实际执行。此 DTO 不包含产品结论、训练/资格决定、原始像素或 native 句柄。请求中的单调 deadline 只在同进程 Core API 内有效，不得跨进程序列化；跨进程调用须由宿主转换为剩余预算并在接收端重新绑定本地单调时间。

`InferenceInputReference` 标识一个item及其有序named Values；每个 `InferenceInputValueReference` 标识对应输入内容及布局。Values名须与Descriptor.Inputs一一匹配，禁止按位置猜多输入绑定。引擎实例通过显式注入的 `IInferenceInputProvider`、模型解析器和后端适配器取得有界只读租约；这些端口不得从静态状态、UI、产品 Store 或 Service Locator 查找。端口语义和签名在 A.4 冻结；真实 HALCON 实现在隔离适配器内经 `cv2` 调用。只有实际参数类型/重载歧义才核公共签名，算法/输出/资源行为按目标模型验证，不设封装存在性门。

### A.2 接口一致性与端口所有权

- 正文 §3.1 的请求字段按上方 DTO 一一归属；取消令牌仅为 `InferAsync`/查询/Drain 的调用参数，不进入请求快照。
- 正文 §3.2 的候选、拒识和输出完整性通过 `InferenceItemResult` 的任务 Schema、状态、拒识码及请求级终态表达；字节载荷必须满足固定 Schema、摘要、尺寸和有效域检查。
- 正文 §4 的事件是观察投影，不增加独立写操作。唯一执行/查询/关闭入口就是 `IAiInferenceEngine`，无平行的 `Infer` 同步入口；诊断观察者只能通过构造时注入端口接收事件，不能取得执行或提交权限。
- `IInferenceInputProvider`、模型解析器及执行后端属于构造时显式注入的适配端口。Core 拥有请求状态和执行结果；模型资产 Owner 拥有模型闭包，输入 Owner 拥有源数据，运行资源 Owner 拥有跨进程终止/排空证明，调用应用拥有质量/提交事实。
- DTO、schema、模块程序集和算法分别带独立版本；该 Core 合同修订固定为 `0.3`。兼容性和生产资格仍按正文 §7/Profile 处理。
- `InferenceOperationState` 是唯一 operation 生命周期枚举；已接纳 operation 的 `InferenceTerminalState` 只能在 `Drained` 和 `ResourcesReleased` 已成立后填充；预接纳 `Rejected` 按无资源短路径处理。`NativeExecutionMayContinue=true` 时不得填充终态；`ResourcesReleased=true` 时不得再返回可变 native 借用。
- `InferenceDiagnostic.Code` 使用正文错误 token。`CommitUnknown`、质量结论和设备回执不进入本模块 DTO。

`InferenceDrainRequest.Timeout` 是本次排空等待的单调预算；`DrainReceipt.InstanceStopped=true` 只表示引擎已停止接纳新请求，不表示隔离 worker/进程已经退出。`AllOperationsDrained=true` 须同时证明每个 operation 的 `ResourcesReleased=true`、全部authority Call真实结束/gate Stop及Dispose成功、backend.StopAndDrainAsync及backend Dispose成功和诊断尾段关闭，才允许释放引擎实例；超时回执 `AllOperationsDrained=false`，未排空 operation 为 `DrainPending` 并保持租约。`QueryAsync` 的 `NotFound` 只表示该引擎实例没有持有该 requestId，不表示历史 operation 已成功或失败。

### A.3 Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/ai-inference/Asun.Modules.AiInference.Core/Asun.Modules.AiInference.Core.csproj`；namespace：`Asun.Modules.AiInference`。预定测试工程：`tests/Modules/ai-inference/Asun.Modules.AiInference.Core.Tests/Asun.Modules.AiInference.Core.Tests.csproj`。上述项目尚未创建。
- 测试执行栈、用例归属、Release 构建/运行命令及失败退出规则唯一见 §10.2；Core.Tests 不引用 Simulator，需模拟端口生命周期的用例归 A.5 的 Simulator.Tests。
- Core 切片允许变更范围：仅上述 Core 和测试工程目录；Simulator/Adapter 的独立切片范围见 A.5；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前状态：Core/Simulator v0.3 的六项文档规格已接收，为 `ModuleCoreImplementationReady`（规格准备），依据见 §15；实际开工须确认权威代码基线并派发明确切片。本绑定不是实现、集成或资格通过声明。文档整体仍为 `DesignReview / Prep`。

### A.4 显式端口、装配和资源租约（唯一签名）

以下为模块自有公开契约形状；工厂方法体占位说明尚未实现，不构成现有代码或测试。端口不会包含 HALCON、WPF、数据库或产品业务类型。集合用 `ImmutableArray`，默认值视为无效，空集合语义逐字段规定；禁止用 `IReadOnlyList` 外壳包装可变数组后声称请求已冻结。

```csharp
// 与 A.1 相同 using 和 namespace；不是第二个命名空间。
public sealed record InferenceEngineOptions(
    int MaxItems, int MaxRank, int MaxIdentityChars, int MaxTraceChars,
    int MaxOperations, int MaxDiagnosticEvents, int MaxDiagnosticsPerOperation,
    InferenceStableReference TrustedConsumer, TimeSpan PurposeCheckTimeout,
    int MaxConcurrentPurposeChecks, InferenceResourceBudget InstanceBudget);
public sealed record InferencePortResult<T>(T? Value, ImmutableArray<InferenceDiagnostic> Diagnostics)
    where T : class;
public sealed record InferenceContentMember(
    InferenceContentReference Reference, string Role, string Name, ImmutableArray<byte> Bytes);
public sealed record InferenceInputBinding(
    string Name, InferenceContentReference Preprocess, InferenceInputKind Kind,
    InferenceElementType ElementType, ImmutableArray<int> Shape, string Layout);
public sealed record InferenceOutputBinding(
    string Name, string SourceKey, string Container, string ValueType,
    ImmutableArray<long> NativeShape, ImmutableArray<string> Axes,
    ImmutableArray<long> Shape, bool Required);
public sealed record InferenceModelDescriptor(
    InferenceContentReference Manifest, InferenceContentReference Model, string TaskKind,
    InferenceContentReference Preprocess, InferenceContentReference Postprocess,
    InferenceContentReference RawOutputSchema, InferenceContentReference OutputSchema,
    InferenceContentReference? ClassMap, ImmutableArray<InferenceInputBinding> Inputs,
    ImmutableArray<InferenceOutputBinding> Outputs,
    ImmutableArray<string> RequiredOutputs, int ConfiguredBatchSize);
public interface IInferenceModelLease : IAsyncDisposable
{
    InferenceModelDescriptor Descriptor { get; }
    ImmutableArray<InferenceContentMember> Members { get; }
}
public interface IInferenceModelResolver
{
    ValueTask<InferencePortResult<IInferenceModelLease>> ResolveAsync(
        InferenceRequest request, CancellationToken cancellationToken);
}
public interface IInferenceInputValueLease
{
    InferenceInputValueReference Reference { get; }
    ReadOnlyMemory<byte> Bytes { get; }
    ImmutableArray<InferenceContentMember> InterpretationMembers { get; }
}
public interface IInferenceInputLease : IAsyncDisposable
{
    InferenceInputReference Reference { get; }
    ImmutableArray<IInferenceInputValueLease> Values { get; }
}
public interface IInferenceInputProvider
{
    ValueTask<InferencePortResult<IInferenceInputLease>> AcquireAsync(
        InferenceInputReference input, CancellationToken cancellationToken);
}
public interface IInferenceBudgetLease : IDisposable { }
public interface IInferenceBudgetPort
{
    InferencePortResult<IInferenceBudgetLease> TryReserve(
        InferenceRequestId requestId, InferenceResourceBudget budget);
}
public enum InferencePurposeCheckKind { Execute = 0, FinalDisclosure = 1, QueryDisclosure = 2 }
public sealed record InferencePurposeCheck(
    long CallId, InferenceStableReference TrustedConsumer, InferenceRequest Request,
    InferencePurposeCheckKind Kind, long MonotonicDeadlineTimestamp);
public sealed record InferenceAuthorityDrainProof(
    bool CallsStopped, bool ResourcesReleased, ImmutableArray<InferenceDiagnostic> Diagnostics);
public interface IInferencePurposeGate : IAsyncDisposable
{
    ValueTask<InferenceValidationResult> CheckAsync(
        InferencePurposeCheck check, CancellationToken callCancellation);
    ValueTask<InferenceAuthorityDrainProof> StopAndDrainAsync(
        TimeSpan waitBudget, CancellationToken waitCancellation);
}
public sealed record InferenceRawItem(
    InferenceItemId ItemId, int Sequence, InferenceContentReference Schema,
    ImmutableArray<byte> Bytes);
public sealed record InferenceRawResult(
    InferenceRequestId RequestId, ImmutableArray<InferenceRawItem> Items, InferenceExecutionEvidence Execution,
    ImmutableArray<InferenceDiagnostic> Diagnostics);
public sealed record InferenceBackendDrainProof(
    bool ExecutionStopped, bool NativeResourcesReleased,
    ImmutableArray<InferenceDiagnostic> Diagnostics);
public interface IInferenceBackendLease : IAsyncDisposable
{
    ValueTask<InferencePortResult<InferenceRawResult>> RunAsync(CancellationToken operationCancellation);
    void RequestCancel();
    ValueTask<InferenceBackendDrainProof> DrainAsync(TimeSpan waitBudget, CancellationToken waitCancellation);
}
public interface IInferenceBackend : IAsyncDisposable
{
    string BackendId { get; }
    ValueTask<InferencePortResult<IInferenceBackendLease>> PrepareAsync(
        InferenceRequest request, IInferenceModelLease model,
        ImmutableArray<IInferenceInputLease> inputs, CancellationToken operationCancellation);
    ValueTask<InferenceBackendDrainProof> StopAndDrainAsync(
        TimeSpan waitBudget, CancellationToken waitCancellation);
}
public sealed record InferenceProcessedResult(
    ImmutableArray<InferenceItemResult> Items, bool OutputComplete, bool WasTruncated,
    ImmutableArray<InferenceDiagnostic> Diagnostics);
public interface IInferenceTaskCodec
{
    InferenceValidationResult ValidateDefinition(
        InferenceRequest request, InferenceModelDescriptor model,
        ImmutableArray<InferenceContentMember> members);
    InferencePortResult<InferenceProcessedResult> Process(
        InferenceRequest request, InferenceModelDescriptor model,
        ImmutableArray<InferenceContentMember> members, InferenceRawResult raw);
}
public enum InferenceEventKind
{
    RequestReceived, RequestValidated, RequestAccepted, RequestRejected,
    StageStarted, Progress, ItemCompleted, ItemRejected,
    DrainStarted, Drained, ResourcesReleased, RequestTerminal
}
public sealed record InferenceEvent(
    InferenceRequestId RequestId, long Sequence, long StateRevision, InferenceEventKind Kind,
    InferenceOperationState State, InferenceItemId? ItemId, InferenceTerminalState? Terminal,
    ImmutableArray<InferenceDiagnostic> Diagnostics);
public interface IInferenceDiagnosticsSink { void OnEvent(InferenceEvent value); }
public sealed record InferencePorts(
    IInferenceModelResolver ModelResolver, IInferenceInputProvider InputProvider,
    IInferenceBudgetPort Budget, IInferenceBackend Backend, IInferenceTaskCodec TaskCodec,
    IInferencePurposeGate PurposeGate, IInferenceDiagnosticsSink? Diagnostics);
public static class AiInferenceEngineFactory
{
    public static IAiInferenceEngine Create(
        InferenceEngineOptions options, InferencePorts ports, TimeProvider timeProvider)
        => throw new NotImplementedException("Contract shape; implementation not created");
}
```

装配必需端口为 resolver/input/budget/backend/codec/purpose；只有 diagnostics 可缺省。工厂不加载资产或 native，不触发窗口或静态初始化。null options/ports/timeProvider 或必需端口抛 ArgumentNullException；数值上限/预算越界抛 ArgumentOutOfRangeException；结构/组合不合法抛 ArgumentException（均给参数名），不返回 Core 结果或 NotReady 状态。数值规则按 §3.1，预算字节0表示禁用该维而非无限。返回 InferencePortResult 的端口失败用 `Value=null + 非空 Diagnostics`；成功 `Value!=null`，警告可随结果；绝不同时返回失败和可消费载荷。purpose/codec校验使用 InferenceValidationResult，Rejected须非空诊断，Valid可带警告；Drain返回其专用proof，不把false证明当成功。provider 抛异常映射 `InternalFailure`，Core 仍释放已经取得的租约；Prepare 失败/取消必须在该端口内部排空其尚未交接的 native 资源，不能丢失半构造句柄；尚未排空则Prepare不完成，Core在取消/deadline后显示DrainPending并保留操作，不将未完成Prepare误当没有资源。Run 错误不代表 stopped；调用方总是对已取得 backend lease 调 Drain。

成功创建引擎时工厂接收 backend 的独占生命周期所有权，一个 backend 对象只服务一个 engine；创建失败不移交所有权，由宿主恢复/释放。purpose gate同样每engine独占并移交生命周期（内部可由宿主按引用计数共享transport，不能停止其它engine）；resolver/input/budget/codec/diagnostics 为宿主所有，Core只归还其交出的 request lease，不 Dispose这些端口对象，不影响第二引擎。budget lease的Dispose为幂等、不抛异常的本地记账归还；TryReserve失败不得保留额度。其它lease/后端Dispose仅成功完成才是释放证明；失败须保留可重试所有权和已释放分量，不重新释放成功分量；无法恢复时保持DrainPending，由宿主隔离并提供可信退出/释放证明，不能靠重试次数假定成功。

InputLease.Values各自的InterpretationMembers包含该value的Roi/ValidDomain/CoordinateTransform引用的全部精确内容闭包及必要schema；缺省null引用表示原输入全域/identity，非null不得只给无法解析的hash。Core核每成员引用/hash，backend据实际内容绑定变换，不能另读产品Store。每个InputValueLease.Bytes只在其父InputLease租期有效且内容稳定；provider在最后使用结束前不得改写/返池/重映射，ReadOnlyMemory外壳本身不保证所有权。ValueLease没有独立Dispose，由父InputLease统一释放全部values；Core不得在父租约归还后继续使用；需要保留的数据先在预算内复制为ImmutableArray。所有ImmutableArray必须由独立冻结存储构造，禁止Marshal/Unsafe或保留可变底层别名。

raw.RequestId必须等于请求ID；raw schema须声明每item/内部batch实际准备后的shape/layout、配置batch与本次submitted对应关系、有效域和逆变换绑定，不能拿名义请求shape冒充实际输入。多个native批次在raw规范逐批关联，Execution.SubmittedItems为本请求实际提交item总数，configured batch固定，不均摊实测；缓存来源保留原计算身份及原实测。Core核raw关联后才解码，payload和最终输出摘要按实际不可变bytes计算。

| 阶段 | 调用/核验次序与 Owner | 失败、取消与线程边界 |
|---|---|---|
| 纯校验/接纳 | Core 使用注入 TimeProvider 单调域；在 Core 锁内先核可用身份并暂占 ID；字段校验通过后再暂占队列/实例额度，锁外调用有界非阻塞 Budget.TryReserve；回锁复核 deadline/取消/停止并原子登记 operation，才发 RequestAccepted | 暂占 ID 同样排斥竞争重复调用，重复不发生生命周期事件；失败撤销暂占并归还已预约 budget。停止接纳与最终登记在同一锁线性化；全部端口及观察者在锁外调用，不积累未计入队列的 Task |
| 模型/输入解析 | 接纳后 purpose 核用途 → model lease → 校验每成员 hash、任务/预后处理/schema、codec ValidateDefinition → 按 Sequence 获得输入 lease，核 Reference 和实际字节 | Core 为每 request 持有模型与输入；宿主只提供精确引用不提供 IsApproved。失败逐项逆序释放；不把文件/网络路径暴露到 Core DTO；重复内容/闭包允许共享只读底层但租约计数独立 |
| 执行准备 | 对全部输入和准备峰值已有额度后 Backend.Prepare；该 adapter 持 native 模型/DLSample/设备输出，Core 只持 lease 接口。Prepare 按冻结预处理和 runtime profile；禁止自行 train/optimize/改权重 | 操作取消可能仅为请求；adapter 不把 token 对象持久化。执行不得在 UI/内部锁线程；工作线程数量受 InstanceBudget 和请求上限共同约束 |
| 执行/后处理 | Run 只一次，原始输出复制成 managed immutable byte payload，SDK handle 不越端口。Core 核执行 provenance、raw schema/item关联，codec Process 执行 §6.3，拒绝超预算 payload | backend 可以内部合批，但必须保持每请求独立 lease/结果/取消域，按 §5.1 兼容与资源规则；共批未最后使用结束不能证明任一借用资源释放。codec 不读数据库/clock/授权/图像 SDK |
| 请求排空与归还 | Core 进入 Draining；backend lease.DrainAsync 有限等待，只有 ExecutionStopped 且 NativeResourcesReleased 为 true 才 Dispose backend lease并发 Drained；然后逆序 Dispose input/model 租约，归还 budget，发 ResourcesReleased | Drain可重复；native 不支持中断则保持 DrainPending。Dispose提前调用拒绝，释放失败保留未释放分量、租约及 ResourceDrainFailed，可再次Drain/重试释放；禁止终态和资源归零假象 |
| 实例关闭尾段 | gate新Check封闭/Stop及真实IO结束按§5.2执行（可先abort挂起检查）；全部请求归还后调backend.StopAndDrainAsync并Dispose backend；gate proof及Dispose成功、query Call归还、诊断分发尾段关闭后才AllOperationsDrained=true | 即使没有请求也要关闭实例缓存/常驻句柄。失败保持实例未排空和诊断，可重复Drain；不提前Dispose，不清理其它engine或宿主共享端口 |
| 终态/结果读取 | FinalDisclosure在Postprocessing末尾/DrainStarted前完成并排空其IO，之后归还完成才构造唯一结果；QueryDisclosure仅在实例尚接纳查询时启动，Result只在terminal非空且授权通过返回。撤权抑制载荷不删除执行/资源事实 | 不持内部锁跨权限/诊断回调；终态构造时拒绝披露返回 Rejected/PurposeNotAllowed、Items无可消费载荷、OutputComplete=false，ResourcesReleased仍须为true。Query只有终态载荷披露再核权限（关闭后不触网且Result=null）；撤权时保留原State/TerminalState和资源事实，Result=null并附PurposeNotAllowed，不改写已发布结果。外部提交完全由宿主调用，不在引擎内等待证据提交 |

接纳预算是请求声明的各维最坏预约，不是测得峰值；请求不得超过实例额度。模型/输入解析及后处理 bytes 计入对应 managed/native/GPU账；共享模型驻留额度由 backend owner 单独计入实例总账且不能用多个 request 重复记释放。后台排空不受调用者取消等待影响。模型缓存释放、adapter shutdown 按表中实例尾段执行；AllOperationsDrained 还须确认模型缓存/native驻留、authority IO/gate及诊断分发尾段关闭，否则不得 Dispose。backend缓存独立持有其需要的模型内容或引用计数，不能借用已归还的 request model/input lease。

Query 保留全部已登记 request 的终态结果直到实例 Drain/Dispose；MaxOperations 达到上限拒绝新请求，不能静默驱逐导致未知 ID 与历史完成混淆。该上限同时预算所有结果字节，实例结果总字节不得超过 InstanceBudget.MaxOutputBytes，不能仅限制单请求；需要长期服务时宿主按有界 generation 轮换并保存自己的结果。预接纳拒绝不登记 operation；RequestReceived/Rejected/Terminal 可观察，Query 不持该 ID。相同 ID 的调用先在锁内核验可用身份并暂占 ID，再发 RequestReceived；已暂占/登记的重复调用仅返回 DuplicateRequest，绝不发第二组 lifecycle 事件或改变原 operation。暂占拒绝后释放，已登记 ID 到实例释放前不复用。

### A.5 独立工程、发布与六项准备结论

本模块自身契约在v0.3作破坏性准备修订：新增named binding/manifest、可信consumer与purpose IO生命周期；v0.1/v0.2均无产品调用方或发布证据，不用兼容假定代替真实检查。以后公开发布后按SemVer维护major API，不能把本轮改动叫兼容新增。平台DTO/跨进程codec映射不进入Core。发布包包含API版本、依赖/RID、构建来源/hash、后端能力和schema支持、未验证项；Core单独net10.0且无Windows/UI/native包。不以AsunImage/DevExpress安装或授权核验作为开发门。

| 切片 / 唯一落点（均未创建） | 无UI/独立交付和验收范围 | 本轮规格准备与剩余门 |
|---|---|---|
| Core：A.3指定的预定 `.Core.csproj`、namespace `Asun.Modules.AiInference`；对应 `.Core.Tests.csproj` | contract/immutable数据、校验、接纳/队列/预算、状态/查询/事件、Canonical v1解析/codec、可信主体绑定与authority IO排空；程序集不引用HALCON/产品/UI；纯断言在对应测试工程，模拟生命周期归下一行，执行栈及命令见§10.2 | 六项文档规格已主接收，为ModuleCoreImplementationReady（规格准备）；实际开工须绑定权威代码基线并派发，尚未编译测试 |
| Simulator：`src/Modules/ai-inference/Asun.Modules.AiInference.Simulator/Asun.Modules.AiInference.Simulator.csproj`；namespace `.Simulation`；`tests/Modules/ai-inference/Asun.Modules.AiInference.Simulator.Tests/Asun.Modules.AiInference.Simulator.Tests.csproj` | 模块契约端口的确定性内存模型/输入/预算/用途/backend/codec，实现§10.1；fake time和手动完成屏障，无sleep仿native退出；测试归属、BCL Exe栈及命令见§10.2 | 六项文档规格与模拟scenario已主接收，为ModuleCoreImplementationReady（规格准备）；尚未执行，不需真实图像/客户阈值；结果不得作为HALCON准确率/资源/现场证据 |
| HALCON Adapter：`src/Modules/ai-inference/Asun.Modules.AiInference.Halcon/Asun.Modules.AiInference.Halcon.csproj`；namespace `.HalconAdapter`；对应 `tests/Modules/ai-inference/Asun.Modules.AiInference.Halcon.Tests/Asun.Modules.AiInference.Halcon.Tests.csproj` | Core端口+既定ImageLibDotNet.cv2；原Owner桥只消费ModelAssets Service/ImageFrame Resources公开能力；SDK句柄仅本adapter内部；唯一factory、绑定、两Host、原Task保持、算子与验证见附录C及§2.5/6.3 | 附录C确定Adapter/原Owner桥/公开装配指导内容已主限定接收；真实模型/输入交接、实际Capability、用途事实、编译/运行、HALCON/native/GPU、Golden、真实双宿主、性能与现场资格未验证；不影响Core/Simulator接收 |
| 外部后端 / worker / 结果缓存 / UI | 外部后端先记录实际HALCON导入缺口与批准发布闭包；worker须IPC/隔离退出协议；结果缓存可不实现；UI不是本轮模块交付 | 未批准新增依赖/远端服务/IPC；这些门不阻断Core及Simulator；无UI项NotApplicable |

允许后续获准实现范围是表中精确工程目录及其测试目录；本轮写入仅唯一指导。禁止其它模块、Shell/Domain/Integration、共享schema、src/tests公共设施、参考快照和AsunImage内部。没有新的正式工程基线前不生成代码；主会话独立处理跨文件入口或共享候选合同映射，本会话不扩写。

逐切片DEV-GOV-010六项结论：①职责/依赖方向/两个消费者计划明确；②v0.3类型/工厂/端口/事件/单位/拒识/失败、Canonical v1字段/解析/named多输入输出、可信宿主与IO所有权在A.1/A.4及§3.4/5.2/6.4–6.6闭合；③Core/Simulator无UI、SDK、平台存储的独立宿主成立于规格，尚未构建；④正常/边界/重复/并发/取消/关闭/回退断言见§10.1，确定测试栈、入口、命令和退出规则见§10.2，尚未执行；⑤Benchmark测点/统计引用/负载和预算已冻结，消费者性能数值只影响该Profile的达标门；⑥工程/测试/允许禁止路径/最小宿主顺序已冻结，真实模型/adapter/产品映射仍后续门。以上六项文档规格已由主会话接收，Core/Simulator v0.3 为 **ModuleCoreImplementationReady（规格准备）**，主接收依据见§15；整体仍DesignReview/Prep，不代表实现、测试执行、性能或生产通过。

### A.6 固定研究依据与采纳落点（2026-10-09）

复用 [REF-002 推理研究](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#inference-source-research) 的原字节与版本/依赖/许可证，未新增快照或重复报告。2026-10-09联网读取下列固定GitHub原件，SHA-256与归档一致；实际读源码和测试断言，未运行上游测试，未引入ORT/Triton运行时。其余原已读范围继续按REF-002精确边界复用，不称全仓审计。

| 固定来源 / 实际读取 | 可复用强项 → 本文落点 | 局限、许可与依赖 |
|---|---|---|
| ORT v1.22.1 commit `89746dc19a0a1ae59ebf4b16df9acab8f99f3925`：[RunOptions.shared.cs](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/src/Microsoft.ML.OnnxRuntime/RunOptions.shared.cs) 90–120；SHA256 `6a97577e8eb532408f6e2a44cd6baf5af0ffb3399d28a196ada500ced73e4b7e` | Terminate影响共享同对象的所有Run → §5.1 request取消域隔离与A.4 lease排空 | 取消flag不是native退出证明；MIT，C#依赖System.Memory/条件Tensors及native/EP闭包见REF-002，不作为平台默认后端 |
| 同commit [InferenceTest.cs](https://github.com/microsoft/onnxruntime/blob/89746dc19a0a1ae59ebf4b16df9acab8f99f3925/csharp/test/Microsoft.ML.OnnxRuntime.Tests.Common/InferenceTest.cs) 2059–2130；SHA256 `3def62502ba5e67d481061d331dd842d2d66e1f6b8e42d31278b15a521d94459`；本地RunOptions、OrtValueTests及csproj/许可复用 | 实际FP16数值断言及RunAsync单线程失败 → §10.1数据/线程/异常验证，不只测Task结束 | 测试不覆盖本平台所有借用、释放和共批取消；不照搬thread值为部署要求 |
| Triton core r25.08 commit `70b908ca74b27407ae7c33b26ef26401d50aa871`：[request_cancellation_test.cc](https://github.com/triton-inference-server/core/blob/70b908ca74b27407ae7c33b26ef26401d50aa871/src/test/request_cancellation_test.cc) 182–248；SHA256 `fc4f5e09a3a2a0889b46b8cd74fdd095c2286da2dfb199ea75d500d5711c253d`；本地scheduler_utils 76–150及dynamic_batch_scheduler 488–572 | equal shape/optional输入，有限短批和取消恢复 → §5.1兼容域/截止与§10.1故障屏障 | cancellation测试有response/release竞态FIXME和2秒sleep，不证明GPU释放；BSD-3-Clause；C++17/server依赖common、Boost、Protobuf、Threads/re2及按GPU开关CUDA；只借思想不移植服务 |

本次定向退修新增核对仅为未闭合的字典/多输入/解释键：26.05官方Model章节及classification/multi-label/instance/segmentation/anomaly章节；项目create_dl_layer_input（多named input与tuple布局）、fit_dl_out_of_distribution（ood_score/ood_threshold结果语义，只读说明不实施训练）、gen_dl_model_heatmap的nested键/GenParam。落点§6.5；标准键及Core schema不再是客户外部门，实际模型值/Golden仍需真实证据。复用此前固定GitHub源码/测试结论，无再次下载、研究报告或参考快照写入。

HALCON依据为项目26.05：[apply_dl_model](../../../halcon算子手册/operators/apply_dl_model.html)、[read_dl_model](../../../halcon算子手册/operators/read_dl_model.html)、[get_dl_model_param](../../../halcon算子手册/operators/get_dl_model_param.html)、[set_dl_model_param](../../../halcon算子手册/operators/set_dl_model_param.html)、[optimize_dl_model_for_inference](../../../halcon算子手册/operators/optimize_dl_model_for_inference.html)、[transform_dl_sample_batch](../../../halcon算子手册/operators/transform_dl_sample_batch.html)、[gen_dl_model_heatmap](../../../halcon算子手册/operators/gen_dl_model_heatmap.html)、[query_available_dl_devices](../../../halcon算子手册/operators/query_available_dl_devices.html)、[clear_dl_model](../../../halcon算子手册/operators/clear_dl_model.html)。本轮核对语义已写入§2.5；旧2511/24.11只作线索，不继承API/参数保证。像素半中心、NMS等是本模块冻结的数学规则，真实模型训练一致性仍需Golden；不声称实测最快。

H:来源复审结论延用2026-10-06已核的清单记录（不是本轮重读或新哈希）：AI设备端指导hash `34309c6b3005c3257a503c8c05acaf6081169896e4d34f9eea9959dabd0630e1`的成员完整性/可选缓存约束已在§6吸收；融合指导hash `70869c962de65c0ca76083cdd9faf2b214b48222e37848cf1a03aa20ec439bfb`仅支持AI候选不覆写测量/放行边界，Decision/人工/激活/整板编排不迁入。本轮不迁入来源项目验收结论。既有Viscom vConnect第2/3页原PDF研究按REF-002复用，只证明公开呈现/工程试验，不证明内部模型、吞吐或排空。模块无UI，无须新做竞品界面或DevExpress控件研究。

### A.7 Canonical codec 与 Simulator 的唯一公开装配

这是既有 Core/Simulator 职责的构造补充，Core API v0.3 与 Canonical v1 的类型/运算不变；未产生新产品实现。Core namespace 中增加以下唯一入口，返回无状态、可重入、无 IO/clock/授权/native 的 §6.4–6.6 实现；不需产品插件或自行实现 codec。所有解析/运算限额取当次 request/descriptor 和既有规范上限，ValidateDefinition 与 Process 使用同一解析器；Process 仍独立核完整定义/raw，不信任前次 Valid，不持有 caller bytes 或跨请求缓存。

新增两个factory/Simulator类型是未发布准备版的加法构造补充，不能沿用旧“v0.1/v0.2→v0.3”的破坏性迁移结论称所有历史版本兼容。Core API仍v0.3，Simulator首版程序集0.3.0；HALCON Adapter API0.1/程序集0.1.0不改签名，仅部署安全前置细化。文档0.5.0-prep的历史接收不追改为0.5.1运行接收。

```csharp
// namespace Asun.Modules.AiInference；using 同 A.1。
public static class CanonicalInferenceTaskCodecFactory
{
    public static IInferenceTaskCodec Create()
        => throw new NotImplementedException("Contract shape; implementation not created");
}
```

C.6 的 `published.CanonicalCodec` 和两个纯托管 Host 均由此入口创建并显式传入；多个 engine 可共享此纯无状态 codec。未知 schema/任务/role 按既有验证诊断拒绝，不能自行注册弱校验 fallback。

Simulator namespace 为 `Asun.Modules.AiInference.Simulation`，只引用本 Core/BCL。公开形状如下；夹具不是客户数据/资格或平台 schema，只有 Simulator.Tests 及独立软件 Host 消费。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.AiInference;
namespace Asun.Modules.AiInference.Simulation;

public sealed record InferenceSimulationOptions(
    int MaxFixtures, int MaxCalls, int MaxIdentityChars,
    long MaxRegisteredBytes, InferenceResourceBudget InstanceBudget);
public sealed record InferenceSimulationValue(
    InferenceInputValueReference Reference, ImmutableArray<byte> Bytes,
    ImmutableArray<InferenceContentMember> InterpretationMembers);
public sealed record InferenceSimulationFixture(
    InferenceRequest Request, InferenceModelDescriptor Model,
    ImmutableArray<InferenceContentMember> Members,
    ImmutableArray<InferenceSimulationValue> Values, InferenceRawResult Raw,
    string? SharedExecutionGroup);
public enum InferenceSimulationStage
{
    PurposeExecute, PurposeFinal, PurposeQuery, ModelResolve, InputAcquire,
    Prepare, Run, NativeRelease, BackendLeaseDispose, InputDispose, ModelDispose,
    BackendStop, BackendDispose, PurposeStop, PurposeDispose
}
public enum InferenceSimulationOutcome { Complete, Reject, Throw }
public sealed record InferenceSimulationCallKey(
    InferenceRequestId? RequestId, InferenceSimulationStage Stage,
    string Subject, int Ordinal);
public sealed record InferenceSimulationStep(
    InferenceSimulationCallKey Key, bool Hold,
    InferenceSimulationOutcome Outcome, ImmutableArray<InferenceDiagnostic> Diagnostics);
public sealed record InferenceSimulationCall(
    InferenceSimulationCallKey Key, bool Started, bool Completed, bool CancellationRequested);
public sealed record InferenceSimulationSnapshot(
    ImmutableArray<InferenceSimulationCall> Calls,
    int ModelLeases, int InputLeases, int BackendLeases, int BudgetLeases,
    bool BackendClosed, bool PurposeClosed);
public interface IInferenceSimulation : IAsyncDisposable
{
    InferencePorts Ports { get; }
    InferenceSimulationSnapshot Query();
    Task WaitUntilStartedAsync(InferenceSimulationCallKey key, CancellationToken waitCancellation);
    bool Complete(InferenceSimulationCallKey key);
}
public static class InferenceSimulationFactory
{
    public static IInferenceSimulation Create(
        InferenceSimulationOptions options,
        ImmutableArray<InferenceSimulationFixture> fixtures,
        ImmutableArray<InferenceSimulationStep> steps,
        IInferenceTaskCodec borrowedCanonicalCodec, TimeProvider timeProvider,
        IInferenceDiagnosticsSink? diagnostics)
        => throw new NotImplementedException("Contract shape; implementation not created");
}
```

| 装配/控制项 | 冻结行为、限额与反例 |
|---|---|
| Factory 与注册 | 无 IO/线程/运行调用；null 必需参数、非法数值/default数组/重复 fixture RequestId 或 step key 分别沿 A.4 参数异常。fixtures 非空且<=MaxFixtures，steps<=MaxCalls；字符串限 MaxIdentityChars；byte snapshots 含 raw/成员/输入/解释成员 checked 总和<=MaxRegisteredBytes；注册后独立冻结，不留 builder 别名。合法结构但错误 hash/schema/raw/descriptor 允许作为故障输入，由真实 Core/codec 拒绝，不能在工厂替它修正 |
| Fixture 寻址 | resolver/backend/purpose 按完整 RequestId 找 fixture，同时要求当次请求结构等于注册 Request（集合逐字段/元素比较，不使用ImmutableArray底层引用相等）；不按 Model hash 或 latest 找。InputProvider 按完整 InputReference 匹配；跨 fixture 的同 InputReference 注册在首版拒绝，避免无 requestId 的接口歧义；fixture.Values 按 Name/Source 与各 Input.Values 精确配对，同一Name不同Source允许分别配对。找不到使用 ModelNotReady/InputFormatUnsupported/PurposeNotAllowed/AdapterNotReady，Field指对应引用且SafeArguments含NotRegistered，不返回占位成功。生命周期反例通过 step，数值反例通过完整 fixture；codec 始终调用上面的真实实现 |
| CallKey 与记录 | request 阶段用原 RequestId；实例 Stop/Dispose 用 null。InputAcquire/InputDispose 的 Subject 为原 ItemId.Value，其余为非 null 空 string；Ordinal 是该三元组从0开始的调用序号，用于 Query/Drain或释放重试。每个已开始调用先原子登记固定 holder，再执行，无界限外 Task 不允许；MaxCalls 包含未开始的等待订阅与已开始记录，满时同步拒绝 InvalidOperationException，测试判失败。factory 为 backend/purpose Stop/Dispose 及每 lease 的释放保留控制额度，业务不得耗尽它们 |
| 闩锁与失败 | 无 step 默认立即 Complete。Hold=true 创建 RunContinuationsAsynchronously 的一次性 TCS；WaitUntilStarted 可在调用前登记，只观察开始；waitCancellation 只取消该订阅，不取消 port。Complete 在已开始且仍 Hold 的调用恰一次 true，未开始/未知/已完成 false；解除后兑现 step.Outcome。Reject 只用于返回验证/PortResult的阶段，必须非空既有诊断；Throw 固定 InvalidOperationException("Simulated port failure")；释放/Stop 的拒绝用 Throw，不伪 true。所有 Hold 不因合作 token 自动解除，CancellationRequested只记事实，用于迟到与挂起反例；测试必须显式解除并收尾 |
| 租约/预算 | 每次成功 Resolve/Acquire/Prepare 产生独立 lease并增加计数，只有真实 Dispose 成功递减；failed Dispose 保留该 lease，下一 Ordinal 重试，成功分量不重放。budget.TryReserve 使用 InstanceBudget 逐维 checked 预约、非阻塞；不满足返回 BudgetUnavailable，Dispose 幂等且不抛，只归还一次。模型/输入稳定内存持续到其 lease归还，backend借用而不归还父租约；Run只一次，Raw保持原fixture身份与摘要，不修错raw |
| 原 Task/Drain | Run原Task与NativeRelease holder分开；Prepare成功登记NativeRelease holder，Run真结束（含fault）才开始该step，Run未启动的取消在确定不再启动后开始。Run真结束/已封未启动、NativeRelease step真完成且无共享使用才返回 backend proof 两项true。Drain/Stop仅用注入 TimeProvider 的有限 waitBudget观察这些原holder，到期/取消等待返回false，不取消/丢失原Task。SharedExecutionGroup仅同factory显式等字符串的fixtures共享最后使用屏障；成功Prepare在锁内加入，第一次该组Drain封新成员，后到Prepare以AdapterNotReady拒绝。已加入成员Run/NativeRelease全部真结束前任何成员不能证明释放；每成员独立取消/结果，A取消不解除B。共批用例先等A/B的Run开始再取消A；它只模拟Core共批反例，不能开启附录C真实组批 |
| 关闭/所有权 | Ports.Backend与PurposeGate独占给一个engine，其它端口/codec/diagnostics仍归fixture Host；Core工厂失败由Host调用backend及gate原Stop/Dispose有限排空。simulation.Dispose只在BackendClosed/PurposeClosed且四类lease计数为0、全部已开始调用/等待订阅结束时成功，否则抛InvalidOperationException并保留引用。成功才撤注册byte引用，不再Dispose已移交端口。失败或观察取消后Host仍强持simulation和原engine/调用Task；测试不能靠Dispose把计数清0 |

实例关闭调用的控制槽在 factory 固定保留；每成功取得 lease 的 holder 同时保留其释放槽，保留量计入 MaxCalls，容量不足在获取前拒绝，不能成功获取后无空间归还。已结束失败释放只替换同一 holder 当前 Task，保留最后错误和 Ordinal；不积累重试 Task 历史。Query 返回独立冻结快照；记录是模拟软件事件，无 HALCON/GPU 实测观察值，fixture.Execution.Observations 仅用 NotExecuted/Unsupported，不能标 Measured。

steps的RequestId必须已登记，实例阶段必须null，Ordinal>=0，Subject遵表且能定位注册item；未知枚举、非法Reject阶段或default Diagnostics在factory拒绝。所有fixture的SharedExecutionGroup为null或有界非空string；注册request.BackendPolicy.BackendId固定 `simulation-v1`，正常Raw.Execution.Backend同值，其Device/Precision/RuntimeSha256仍显式fixture值；用于来源关联反例的raw错误允许保留，Core必须拒绝而非模拟器代修。每fixture的资源预算<=options.InstanceBudget；EngineOptions.TrustedConsumer与fixture.Request.Consumer一致，一个simulation只能服务同受信consumer的一个engine。没有新诊断码：factory找不到fixture使用上述既有码，人工steps只使用§3.3闭集码/既有MessageKey。PurposeStop先封Check并标记其合作取消，Check未真结束proof不得true；BackendStop同理先封Prepare再有限观察。PurposeClosed/BackendClosed只在对应Dispose成功且原调用/lease均已结束后设置，不以Stop调用完成代替释放。

早调用backend lease.Dispose而两项proof未true，或model/input Dispose仍有backend借用时抛InvalidOperationException，不消费释放step、不递减计数。Lease成功释放后重复Dispose幂等无新Call；失败重试使用下一Ordinal但同原holder。实例Stop/Drain预算到期/取消等待只返回false proof；其原Stop工作和已开始step保留，重复观察复用而不创建平行Stop/释放。只有原Stop已结束失败才按下一Ordinal恢复。Snapshot仅保每holder当前/最终记录，失败重试旧Task真结束后撤引用并保最后诊断，不假称每个重试有无限持久事件史。

§10.2 的 fake time 唯一放 Simulator.Tests 的 `ManualTimeProvider(DateTimeOffset initialUtc, int maxTimers, int maxCallbacksPerAdvance)`：后两项为正且Host令其等于simulation options.MaxCalls；timestamp=0、TimestampFrequency=TimeSpan.TicksPerSecond；GetUtcNow=初始UTC+推进量。Advance(TimeSpan delta)仅非负checked增量；CreateTimer按due timestamp/注册序稳定排程，计数<=maxTimers，回调锁外执行；一次性timer只触发一次，periodic按每个到期点推进并受maxCallbacksPerAdvance的单次Advance回调上限，超限立即用例失败，不静默漏回调。Change/Dispose从该队列原子撤销；dueTime/period仅接受非负或Timeout.InfiniteTimeSpan，period=0按BCL一次性语义，回调抛错即用例失败，创建/Change due=0在下一次Advance(TimeSpan.Zero)按序触发。没有真实sleep/后台timer。测试先WaitUntilStarted→Advance/Complete→await原Task→核Query与计数，不用轮询猜native完成。时钟是harness实现，不增加Core/平台公共clock接口。

两个最小软件 Host 各以 CanonicalInferenceTaskCodecFactory.Create→InferenceSimulationFactory.Create→AiInferenceEngineFactory.Create 显式装配；options.InstanceBudget与engine.InstanceBudget一致，可信身份取各fixture consumer，诊断可null。Validate→Infer→Query（当前披露）→Drain→engine.Dispose→simulation.Dispose；任一挂起按上述原holder恢复。A/B须不同simulation/backend/gate，时间可共用显式fake provider。现有§10.1所有正常/故障方法据此注册完整fixture与step，§10.2命令/退出上限不变；这只是可实施软件装配，不是真实双消费者/Golden证明。

## 附录 B：模块核心 API v0.3 入口说明

附录 A 是唯一 Core DTO、入口、状态和资源语义。附录 B 不重复定义类型，也不新增字段；它只说明适配切片的分层：

| 切片 | 允许依赖 | 不得依赖/输出 | 完成门 |
|---|---|---|---|
| Core | `IAiInferenceEngine`、不可变 DTO、校验、状态机、队列/预算抽象、诊断事件抽象 | HALCON/AsunImage 句柄、产品类型、WPF、数据库、质量结论 | 契约单测、状态/取消/排空模拟、资源账和第二宿主纯接口测试 |
| Simulator | Core + 确定性后端模拟器 | 真实 native 句柄、客户数据、设备命令 | 正常/边界/错误/迟到/重复/部分输出及长期运行仿真 |
| HALCON/AsunImage Adapter | Core 端口 + 目标消费项目公开 `ImageLibDotNet` + HALCON 26.05 页面 | 将 `HDlModel`/`HDict`/`HDlDevice` 泄露到 Core；自行改变模型/阈值/工艺语义 | 目标项目编译核对、同样本输出/资源/排空比较、错误映射和回退验证 |
| 宿主 UI（非模块交付） | Core 公开接口和诊断投影 | 直接持有 native、另造校验、修改生产配置或设备动作 | 由宿主 PageContract 验收；本模块 UI 不适用 |

`IInferenceInputProvider`、模型解析器、预算端口和后端适配器均由构造时显式注入；Core 不通过 Service Locator、静态缓存或隐藏窗口获取它们。适配器调用方的 `CancellationToken` 只允许成为取消请求输入，不得写入模型输入、结果摘要、缓存 key 或产品事实。附录 B 中 Core/Simulator v0.3 的规格准入按§15为 `ModuleCoreImplementationReady`；真实 HALCON Adapter 和宿主接入验证仍属后续范围，本轮不创建代码或批准真实部署。

适配器交接顺序固定为：Core 校验与预算预约 → Core 经 resolver/input provider 取得模型/输入只读租约并交给适配器借用 → 适配器准备实际后端配置 → 适配器执行并返回原始类型化输出与实际配置回执 → Core 校验关联/有限性/Schema 并执行后处理 → Core 在后处理末尾完成FinalDisclosure及真实IO → Core 请求适配器排空 → Core 在资源归还后发布唯一 `InferenceResult`。适配器只返回原始输出、阶段/设备事实和排空证明，不返回产品质量结论、不写提交事实、不创建第二 operation 状态机；Core 不读取或缓存 `HDlModel`、`HDict`、`HDlDevice` 等句柄。取消时 Core 可调用适配器的中断请求，但只有适配器确认停止或隔离 worker 提供可信退出证明，Core 才能进入 `Drained`。


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

## 附录 C：HALCON Adapter v0.1 公开装配与真实任务验证

本附录补齐既有 HALCON Adapter 切片的内部准备规格，**确定Adapter/原Owner桥/公开装配指导内容已主限定接收**；不重审或改变 `0.5.0-prep / Core API v0.3` 的 Canonical v1、named 输入输出、authority、状态/结果和资源归约。SDK/图像/设备句柄全部私有，唯一后端 ID 为 `halcon-2605-v1`；Adapter API 为 `0.1`，首版程序集版本为 `0.1.0`，公开发布后按 SemVer 管理。没有现有发布调用方，不虚构兼容迁移。首版每请求独立装载模型、无实例模型缓存、无计算结果缓存、不跨请求合批；完整请求内 batch/tile 与多 named 输入输出保留。外部 worker、UI、训练、转换优化、自动换设备/精度/后端不属于本附录。

主接收依据与范围见§15：2026-10-11回读C.1–C.7及C.6.1完整函数/双消费者调用后作内容限定接收。强类型tuple只作进程参数组，仍复用原C.7 Profile合同；原rootOptions、进程根与来源Owner保持。实际HALCON/native/GPU、模型/输入真实交接、编译/运行、Golden、性能/WPF/现场资格均未验证，相应运行/资格状态仍为 `PreparationIncomplete / NotReady`；未新增整Adapter的实现通过或ModuleCoreImplementationReady声明，原Core/Simulator六项规格接收不变。

### C.1 唯一公开工厂、来源与绑定类型

以下均为未来公开声明，非产品实现。程序集 namespace 为 `Asun.Modules.AiInference.HalconAdapter`；`MA` 为 `Asun.Modules.ModelAssets.Service`，`MAC` 为 `Asun.Modules.ModelAssets`，`IF` 为 `Asun.Modules.ImageFrame.Resources`。仅引用这些模块的公开 Core/Service/Resources 契约、推理 Core、BCL 与既定 AsunImage；不引用 ModelAssets Store 实现、ImageFrame HALCON/GPU 适配器、平台私表或 Shell。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.AiInference;
using MA = Asun.Modules.ModelAssets.Service;
using MAC = Asun.Modules.ModelAssets;
using IF = Asun.Modules.ImageFrame.Resources;
namespace Asun.Modules.AiInference.HalconAdapter;

public sealed record HalconHostRootOptions(
    int MaxSessions, int MaxCallsPerSession, int MaxIdChars,
    long MaxHeldBytesPerSession, TimeSpan MaxCleanupWait);
public sealed record HalconHostObservation(
    Guid SessionId, bool AdmissionClosed, bool ResourcesReleased,
    ImmutableArray<string> PendingCalls, ImmutableArray<InferenceDiagnostic> Diagnostics);
public interface IHalconHostSlot
{
    Guid SessionId { get; }
    void HoldPurposeGate(IInferencePurposeGate gate);
    Task<T> Start<T>(string callId, Func<CancellationToken, Task<T>> start,
        ImmutableArray<object> strongHolds, long heldBytes);
    void RequestCancel(string callId);
    void AttachEngine(IAiInferenceEngine engine);
    HalconHostObservation Query();
    ValueTask<HalconHostObservation> CleanupAsync(TimeSpan waitBudget, CancellationToken waitToken);
}
public interface IHalconHostRoot : IAsyncDisposable
{
    bool TryReserve(Guid sessionId, out IHalconHostSlot? slot);
    HalconHostObservation Query(Guid sessionId);
    ValueTask<HalconHostObservation> ResumeCleanupAsync(
        Guid sessionId, TimeSpan waitBudget, CancellationToken waitToken);
}
public static class HalconHostRootFactory
{
    public static IHalconHostRoot Create(HalconHostRootOptions options, TimeProvider timeProvider)
        => throw new NotImplementedException("Contract shape; implementation not created");
}
public sealed record HalconAssetMemberBinding(
    InferenceContentReference Reference, string Role, string Name,
    MAC.AssetRef OwnerAsset, string AssetRole, string LogicalPath);
public sealed record HalconModelAssetBinding(
    InferenceContentReference Manifest, MAC.AssetRef ExactRoot,
    ImmutableArray<HalconAssetMemberBinding> Members);
public sealed record HalconFrameValueBinding(
    InferenceInputValueReference Reference, IF.FrameKey Frame,
    ImmutableArray<int> PlaneIndices, IF.PixelWindow Window, string ExpectedUnit,
    ImmutableArray<InferenceContentMember> InterpretationMembers);
public sealed record HalconTensorValueBinding(
    InferenceInputValueReference Reference, ImmutableArray<byte> Bytes,
    ImmutableArray<InferenceContentMember> InterpretationMembers);
public sealed record HalconOwnerSourceOptions(
    MA.ModelAssetsScope Scope, string PrincipalRef, InferenceStableReference TrustedConsumer,
    string FrameConsumerId, string UsagePurpose, MA.OperationBudget AssetBudget, TimeSpan FrameReadBudget,
    int MaxSourceCalls, int MaxIdentityChars, long MaxResidentBytes);
public sealed record HalconOwnerSources(
    IInferenceModelResolver ModelResolver, IInferenceInputProvider InputProvider);
public static class HalconOwnerSourceFactory
{
    public static HalconOwnerSources Create(
        HalconOwnerSourceOptions options, MA.IModelAssetService borrowedAssets,
        IF.IFrameService borrowedFrames, ImmutableArray<HalconModelAssetBinding> models,
        ImmutableArray<HalconFrameValueBinding> frames,
        ImmutableArray<HalconTensorValueBinding> tensors,
        TimeProvider timeProvider, IHalconHostSlot owner)
        => throw new NotImplementedException("Contract shape; implementation not created");
}
public sealed record HalconModelFile(InferenceContentReference Member, string RelativePath);
public sealed record HalconModelBinding(
    InferenceContentReference Manifest, InferenceContentReference RuntimeProfile,
    ImmutableArray<byte> RuntimeProfileBytes, string Format, string Entrypoint,
    ImmutableArray<HalconModelFile> Files, InferenceResourceBudget RequiredBudget);
public sealed record HalconAdapterOptions(
    string ScratchRoot, int MaxBindings, int MaxOperations, int MaxIdentityChars,
    int MaxPendingPrepares, int MaxChunkPixels,
    long MaxMaterializedBytes, long MaxManagedBytes, long MaxOutputBytes,
    long MaxAccountedNativeBytes, long MaxGpuReservationBytes,
    TimeSpan NativeObservationBudget, TimeSpan CleanupObservationBudget);
public enum HalconReadState { Observed, Unsupported, QueryFailed, NotRequested }
public sealed record HalconParameterReadback(
    string Name, string ExpectedCanonicalJson, string? ObservedCanonicalJson, HalconReadState State);
public sealed record HalconCapabilityObservation(
    InferenceRequestId RequestId, long Generation, bool CanRun, bool WarmupCompleted,
    ImmutableArray<HalconParameterReadback> Readbacks,
    ImmutableArray<InferenceDiagnostic> Diagnostics);
public interface IHalconInferenceBackend : IInferenceBackend
{
    HalconCapabilityObservation? QueryCapability(InferenceRequestId requestId);
}
public sealed record HalconAdapterPorts(
    IHalconInferenceBackend Backend, IInferenceTaskCodec TaskCodec);
public static class HalconInferenceAdapterFactory
{
    public static HalconAdapterPorts Create(
        HalconAdapterOptions options, ImmutableArray<HalconModelBinding> bindings,
        IInferenceTaskCodec borrowedCanonicalCodec, TimeProvider timeProvider, IHalconHostSlot owner)
        => throw new NotImplementedException("Contract shape; implementation not created");
}
```

三个 Factory 均只做同步有界校验/不可变快照和 slot 登记，无文件/资产/图像/设备 IO、native、窗口或隐含预热。null 参数抛 `ArgumentNullException`；非正计数/等待、负字节上限抛 `ArgumentOutOfRangeException`；default 集合、重复身份/相对路径、错引用/hash/组合抛 `ArgumentException`，给参数名。空 frames/tensors 允许，但 inputs 使用未登记源即拒绝；models/bindings 必须非空，bindings.Length<=MaxBindings。所有注册集合/bytes 复制为独立不可变存储，注册 byte 总量含 RuntimeProfileBytes/tensor/解释成员，checked 累加<=MaxResidentBytes/MaxManagedBytes；Identity 限长按本工厂显式MaxIdentityChars，Host令其等于Core options.MaxIdentityChars。adapter.MaxOperations等于Core options.MaxOperations，MaxPendingPrepares<=MaxOperations；options各bytes同时限制本方受控payload，0为禁用维度。ScratchRoot 必须是宿主专属绝对目录，工厂不创建/清空；路径安全核验在 C.3。未知 Adapter API/runtime schema 在 native 前拒绝，不隐式迁移。

`HalconOwnerSourceFactory` 的计划实现分别为 `HalconModelAssetsResolver : IInferenceModelResolver`、`HalconFrameInputProvider : IInferenceInputProvider`；`HalconInferenceAdapterFactory` 返回 `HalconInferenceBackend : IHalconInferenceBackend` 与 `HalconInferenceTaskCodec : IInferenceTaskCodec`。codec 包装注入的 canonical codec：ValidateDefinition 先核本版支持路线/注册绑定再委托原校验，Process 完整委托原 codec；不得重写 §6.4–6.6、直接做 IO/native/授权或省略校验。InputProvider 只提供稳定 managed bytes/解释成员；图像 SDK 转换及 DLSample 生成仅在 backend 内。Core 成功 Create 后仅接管 backend/purposeGate；source wrappers、canonical codec、ModelAssets/ImageFrame/Budget 原服务仍归 Host，不在 backend.Close 中 Dispose。factory 结果在返回前由 slot 强持，Core factory 失败仍有原 Owner 清理；同一 backend 只装一个 engine。

### C.2 原 Owner → 模型/输入租约桥

ModelBinding 匹配键为 `(Manifest 完整引用, RuntimeProfile 完整引用)`；request.Model 对应 Descriptor.Model，须为 manifest 的模型 binary 引用，不能把 ModelAssets 根摘要、模型文件 hash 和 manifest 闭包 hash 当同一值。manifest bytes/成员/Descriptor 仍完全按 §6.4 构造和校验。`HalconModelAssetBinding` 是宿主获批发布交接时冻结的 root→各 inference member 映射，不是第二模型库；推理只消费，不 Import/Seal/Commit/VerifyFormat/批准用途。每 Member 的 OwnerAsset/AssetRole/LogicalPath 必须在同一个 Runtime ResolvedClosure.Files 中找到唯一匹配，length/hash 与 inference Reference 对实际文件相同；ModelAssets 的 root digest 是其原规则，不能改写成 Canonical manifest hash。

| 来源操作 | 固定接线、输出和释放证明 |
|---|---|
| 模型 Resolve | 按 exact binding 调原 `IModelAssetService.ResolveExactAsync(AssetResolveRequest)`，Purpose=Runtime，Access.PrincipalRef=装配PrincipalRef、UsagePurpose=装配用途、RequiredAction=ReadForUse，Scope=原SessionInfo.Scope。原 `ModelAssetRequestProjection.ProjectResolve` 冻结上下文摘要后只提交一次；仅 Succeeded/Complete、无 UnverifiedLegacyRefs、同 View 和完整文件映射才继续。缺模型=ModelNotFound，未知/未封存=ModelNotReady，权限拒绝=PurposeNotAllowed，不生成IsApproved |
| 内容保持/读入 | 同原 closure 调 `AcquireContentLeaseAsync(ContentLeaseRequest)`（`ProjectAcquire(request)`）；逐 Member `(role,name)` 顺序调用父lease.OpenFileAsync(ContentOpenRequest)（`ProjectOpen(parent.LeaseId, request)`）。原32-byte占位→原公开projection→填回Digest再提交，规则唯一复用ModelAssets `model-operation-jcs-v2`，不自行发明哈希。每步原Task/Context/服务/父子lease先登记；实读至EOF，检查声明/实际length/hash、累计bytes和C.1上限，构造 InferenceContentMember 与解析后的Descriptor。所需manifest也作为登记文件读取；缺/重复成员拒绝 |
| 模型 lease | 只交出 `IInferenceModelLease` 的不可变Descriptor/Members，不交路径、stream或SDK。文件实读与子释放确认后才能结束该源调用；父 `IAssetContentLease` 一直由返回model lease保持到Core Dispose。model lease.Dispose内部以原ReleaseOperationId调用ReleaseAsync/QueryResourceAsync确认Released，再Dispose父lease；Unknown/取消等待不完成Dispose，不让Core误清资源。部分失败/迟到父子lease走同原释放身份，Source服务不Dispose |
| 图像读取 | `FrameValueBinding` 精确绑定Source引用→FrameKey/Window/PlaneIndices/ExpectedUnit。每次Acquire内部先登记唯一Guid读取ID再调用 `IFrameService.ReadAsync(FrameReadRequest)`，ConsumerId=sourceOptions.FrameConsumerId、Halo=0、Boundary=RejectMissingSupport、Intent=ExactSamples；本端口只有input没有request deadline，内部总预算明确FrameReadBudget，从Acquire开始计单调时间，后续源读取用其剩余预算，Core通过原operation token提出取消，不猜另一个request上下文。必须同ServiceEpoch/原RequestId、成功Slice非null，SourceKey/window/planes与注册相同；不读显示图或GPU纹理 |
| 图像字节 | `TryOpenReadScope`→按原布局 CopyRow，逐plane实际Scalar/ByteOrder/Channels/域与注册解释核对。将已声明HW/HWC/CHW和正stride写入独立受控byte[]，padding清0、原大小端显式解码再写本版小端；不改变UInt16有效位含义。单数组<=0x7FEFFFFF且<=MaxResidentBytes，输入ByteLength还由Core核request.ResourceBudget.MaxInputBytes，超大输入拒绝而不截断。Metadata.Scale=1/Bias=0且Unit=ExpectedUnit，其他缩放/单位组合本版拒绝InputFormatUnsupported；若宿主提供已显式转换的新来源，须新Source身份/解释闭包，不自行换单位。mask交集与ROI/coordinate成员按§6.4，不能把Empty变Full；核最终Source.Sha256。全部 CopyRow 真结束后关scope，ReleaseAsync反复观察原slice直到LeaseClosed且Drain=Drained/Error=None，再Dispose并等真实结束；StorageReleased可为false（原发布/其它消费者仍持有），不能等待/释放无关消费者。图像帧发布事实归原服务，不Retire/Close共享FrameService |
| Tensor读取 | 精确Source注册 `HalconTensorValueBinding`，shape/strides/length/hash与Reference逐字段一致，冻结bytes在父InferenceInputLease有效期稳定；可同一item混合Frame和Tensor，多值名与manifest精确相等。未知源不Fallback到磁盘/网络；没有native pointer、外部工作或自报GPU fence入口 |
| Input lease | Frame深复制完成及源slice真实释放后才交付独立 managed InferenceInputLease；父统一保持所有values/interpretation members并在Core归还时释放自己的managed引用/额度。多值中途失败逆序释放已取得资源；若原Read/Copy/Release尚未结束，Acquire不完成，Core保持原Task/DrainPending。未交付迟到slice不返回caller，slot按原ID恢复/释放 |

`ProjectResolve/ProjectAcquire/ProjectOpen` 的参数和预算使用 [ModelAssets B.4](../model-assets/DEVELOPMENT-GUIDE.md#b4-请求摘要的唯一字段投影) 的原声明，禁止假造服务接口。源bridge内部上下文epoch/单调ID只分配一次，原失败/观察超期只查询原operation/resource；未知结果不以新ID再读。模型Resolve取得的原request deadline与AssetBudget.TotalTimeout之小作为整个模型链截止，后续Context用剩余预算生成各自原摘要，不在每步重置。Frame的端口局部总预算如上，恢复释放使用独立有限等待预算但不改原意图摘要。`HalconOwnerSourceOptions.TrustedConsumer` 必须等于engine options.TrustedConsumer；FrameConsumerId在Factory固定为该Identity的宿主登记值，不能从request认领。Source资格与Core用途检查分别属于原Owner与§5.2，不合并成隐含生产授权。父子lease使用完先以各自公开ReleaseAsync确认Released再Dispose；部分异常时这些原释放Task/ID仍由桥及slot保持。

原Source返回Pending/Unknown或Value=null时，桥保存原Observation/OwnedResources/原ID与摘要：ModelAssets用QueryOperation/QueryResource，Frame用QueryOperation原epoch/RequestId；只解释Found的权威状态，NotFound不证明退出。Query只给观察，不能凭LeaseId制造lease对象；若原Task最终返回可交付lease但等待/总截止已先到，只登记释放不补交付；若原Owner已经拒绝交付并持有迟到资源，等其原operation/OwnedResources释放后才结束本次源失败。没有结果重取端口时不捏造GetLease API，也不重新Acquire/Read；保持原Owner/根恢复。源取消明确调用原ModelAssets.RequestCancelAsync（原operation/digest及固定CancelRequestId），Frame沿原Read token提出意图；所有租约/使用真归还后才完成桥失败，失败不覆盖原运行错误。

### C.3 Runtime Profile、物化、能力读回与准备

RuntimeProfileBytes 是**adapter私有配置载荷**，在 Factory 显式注册，不加入Canonical v1的manifest.members/role集合，也不修改Core DTO。Reference.SchemaId=`ai.halcon-runtime`、SchemaVersion=`1`，Sha256=实际配置bytes；本载荷复用§6.4的严格UTF-8/NFC、字段排序和数值编码方法，完整字段仅 `{schema,v,adapterApi,halconVersion,device:{ai2,id,type,name},precision,configuredBatchSize,warmupRuns}`，schema=`ai.halcon-runtime`、v=1、adapterApi=`0.1`、halconVersion=`26.05`；device四字段非空string，ai2=`none/tensorrt/openvino`，type为实际设备读回token，id使用Invariant字符串，不使用句柄值；precision=`float32/float16/bfloat16/int8`，batch>0，warmupRuns=0或1。runtime profile的全部字段和Ref不可变，重复/未知字段拒绝。三个NMS参数/类无关策略及named shape/输出/pre/post只取既有manifest/postprocess，不另定义可冲突的runtime副本。

`InferenceBackendPolicy` 的BackendId必须为本版ID，DeviceId固定为`ai2 + ":" + type + ":" + id`，Precision等于profile；Descriptor.ConfiguredBatchSize与profile相等，request.BatchPolicy.MaxItems<=configuredBatchSize（tile/native子批最多该值），不热改batch。bindings.RequiredBudget 是每任务已明确的准备/完整configured batch/预热/解释/排空最坏预约声明；每维须不超过request.ResourceBudget及实例/adapter对应上限。0保持禁用含义，不能声明GPU=0却选GPU。Core调用Budget.TryReserve持原预约，backend不得重复预约同request或以实际短批偷减额度。真实模型runtime/scratch/GPU峰值仍需Profile实测，声明不冒充物理硬上限。

Prepare 每请求一个独占模型，无模型热替换或缓存。backend有且仅一个串行native执行lane；MaxPendingPrepares包含等lane/准备/运行/释放中的全部已登记lease，满即Value=null+QueueFull，不创建无限Task/线程。native调用不在UI、Core锁、回调线程运行；先登记原调用/强持输入和model lease再提交lane，内部所有同步cv2调用的原Task由backend holder持有，slot强持backend。该lane空闲时的准备次序固定如下：

| 步骤 | 唯一实施路线、能力读取和不支持处理 |
|---|---|
| 安全asset物化入口 | modelLease.Members→按binding.Files写独占 `ScratchRoot/sessionId/request序号` 新目录；不读开发目录/工作目录/HALCONROOT fallback。Format仅`hdl/onnx`，Entrypoint为该目录的精确相对路径，Files精确覆盖model/dependency二进制成员、role/name/ref/hash与manifest一致，成员各对应唯一RelativePath；禁止绝对/UNC/盘符/空段/dot/dotdot/链接/重解析/大小写路径碰撞，最终resolved path须在该私有根内。目录和每文件安全创建/打开，保持拒共享写/删的只读文件保持句柄，实写length/hash逐项核对后以绝对entrypoint调用read_dl_model。必要ONNX external_data保持原注册相对布局，不能整仓复制或下载权重。目录不是Store、不发布资产；native实际退出/clear后只清本次已登记私有文件，失败清理留Owner与诊断，禁止递归清未知路径 |
| 发现实际device | query_available_dl_devices→逐get_dl_device_param读ai2/id/type/name/precisions/inference_only；必须唯一匹配profile四元组，重复/零匹配拒绝BackendUnavailable，查询异常为BackendUnavailable/CapabilityNotObserved。ID只在接口内唯一；不选择GPU0或按显示name猜device，不set_dl_device_param修改共享设备。handle全部私有 |
| 模型属性 | read_dl_model→get_dl_model_param读取type/min_version/precision/precision_is_converted/input_dimensions/inference_outputs/batch_size及适用image_width/height/num_channels/class_ids/class_names/ood_available/instance_type/instance_segmentation。仅适用任务参数读取；可选ood缺能力记录Unsupported且按post.ood.required拒识/拒运行，必需属性无法读取即CanRun=false。Model类型必须匹配§6.5 profile；generic用layer_names和get_dl_model_layer_param读取每已登记input/output layer的shape/type及适用input_type/is_inference_output，不新建/改网络；constant输入核闭包常量，无request value |
| 设置与配置读回 | 模型precision仅读，必须精确等profile且device.precisions包含该值；不调用optimize/转换/set precision。未转换模型仅按已冻结configured batch设置batch_size，converted模型只核原batch且不改架构。set_dl_model_param(device)后读回device并重新核四元组；运行时runtime作为适用的原生读回记录，不用legacy runtime setter覆盖device。dimensions固定读回匹配manifest目标shape，不以set input_dimensions改模型。nativeNMS owner=backend时按post设置/读回max_overlap/max_overlap_class_agnostic/min_confidence/max_num_detections；标准检测/实例模型要求owner=backend，本版对其owner=core/none明确Unsupported，不把临时“关闭native NMS”的猜测留给实现者；generic输出未带native NMS且封存网络/输出定义可证明时才支持既有core axis-iou。class-map完整核对，generic无class参数记录NotRequested，不能造Observed |
| DLSample与必需输出 | 按C.4从named数据生成标准image或generic layer字典；标准Outputs及sourceKey→slot按§6.5，generic sourceKey均在实际inference_outputs并核shape/type。converted AI²所需is_inference_output必须在封存模型已设置；这里只get不set。缺一必需layer/type/输出支持在Run前拒AdapterNotReady，不能用aux顶替；调用后内容错按OutputSchemaMismatch/OutputAssociationLost |
| 预热 | warmupRuns=0明确WarmupCompleted=false/NotRequested；=1以当前已准备DLSample和同configured batch/outputs实际apply一次，完整检查基数/类型/输出且立即释放预热结果，成功后WarmupCompleted=true。预热不发业务item完成/候选，不替代正式Run，不把预热输出缓存复用。取消/期限先到不得再启动正式Run；原预热Task未结束保持租约和输入。runtime_init不作为成功证明：26.05对CPU、AI²或已set device无效，本版不依赖它 |

`QueryCapability` 只读本backend原request已取得的本地观察，不触发新IO，未Prepare返回null；只保留有界MaxOperations的同generation摘要，生命周期与engine一致，不驱逐未知原调用。Generation是backend接纳Prepare时checked递增的本实例代号，无溢出复用；相同request只Prepare/Run一次。Name封闭为上述原参数及`input:<name>:shape/type/input_type/const_val/keep_batch_size_const`、`output:<sourceKey>:shape/type/is_inference_output`、`device:ai2/id/type/name/precisions/inference_only`、`warmup`；ExpectedCanonicalJson/ObservedCanonicalJson是按§6.4基础编码的标量/数组/对象实际值，不含handle。Unsupported/QueryFailed/NotRequested的Observed必须null；Observed时不允许用Expected填冒读回。所有必需参数和schema/pre/post支持检查通过才CanRun=true，预热要求1还须实际结束。Execution.Backend/Device/Precision填实际读回值、Generation为原代、RuntimeSha256为已核RuntimeProfileBytes的hash；未真正Run不伪造本次执行证据，预热观察单列。此CanRun不是用途资格/准确率/生产验收。

Unsupported 是Adapter能力读回状态，**不新增Core错误码**。不支持本版路线/值域/必需属性、未有实际能力或无法承诺本任务准备预算，分别返回既有 `AdapterNotReady`（SafeArguments首项`Unsupported`或`CapabilityNotObserved`，Field指精确绑定字段），缺输入格式为InputFormatUnsupported、shape不等为InputShapeMismatch、预算不足为BudgetUnavailable；原生读取/执行异常映射BackendUnavailable/BackendExecutionFailed并保持原任务释放。Core接纳后Prepare失败仍按既有生命周期归约，不伪造预接纳Rejected事件，也不把Unsupported算Completed。可选解释失败只ExplanationNotProvided；必需输出绝不按可选处理。

#### C.3.1 私有物化根的具体安全实现

复用 model-assets 0.3.1-prep 附录 C.2 的 Windows/NTFS guard 思路；本 adapter 写自己已取得的稳定 managed成员，不调用未公开 Service.Materialize，不持有其私有 Store/SD hold/Permit。没有新增物化公共端口或存储权。实现仅在本 `.Halcon` 工程的私有 Win32 文件适配，Core及AsunImage不改变。

1. ScratchRoot 是部署Host预先创建的本账户专属空叶目录，固定本地 NTFS；首次Prepare先在原slot登记打开Task，再用 CreateFileW(OPEN_EXISTING、FILE_FLAG_BACKUP_SEMANTICS、FILE_FLAG_OPEN_REPARSE_POINT)逐ancestor打开，GetFileInformationByHandleEx(FileAttributeTagInfo/FileIdInfo)拒任意reparse并取16byte file ID，GetFinalPathNameByHandleW(FILE_NAME_NORMALIZED、VOLUME_NAME_GUID)核同volume及完整目录分隔边界。最终根不得由模块创建未知ancestor。首次成功将实际volume/file ID绑定本backend generation并强持guard，后来只复核原身份，不重新认领替换目录。用GetSecurityInfo检查根ACL：只允许当前进程受信服务SID、SYSTEM和本地Administrators写/删/改变ACL；未知可写ACE、无法判定ACL、NAS/SMB/FAT均拒AdapterNotReady，SafeArguments=UnsafeMaterializationRoot。受信Host及管理员属于信任边界，不宣称沙箱防御同进程被攻陷。
2. 根内固定独占lock文件用CREATE_NEW及无共享打开，已有文件拒Conflict（映射AdapterNotReady/RootInUse），不删除旧lock重试。本session/request序号目录用CreateDirectoryW独占创建，所有已创建目录/文件立即登记原holder；重复目录拒绝，不借历史残留。逐层目录按同guard核验并不给FILE_SHARE_DELETE，文件CREATE_NEW写入且不共享写/删，不以CREATE_ALWAYS覆盖。members按MaxChunkPixels×元素宽的checked有界块复制，总量<=MaxMaterializedBytes，核完整EOF/length/hash；取消停止后续复制，正在写的原Task仍须真结束。
3. 每个writer Flush及Dispose真结束后，以GENERIC_READ、FILE_SHARE_READ重新打开文件；不共享WRITE/DELETE，重新核file ID、最终路径、length/hash并保持至native/模型清理完成。只读attribute只作提示，ACL+guard是安全条件；HALCON reader若要求写/删则Unsupported，不放松guard。文件祖先及根guard跨全部native使用保持，入口仅为已核文件的绝对路径；ONNX外部成员只按注册布局，不允许runtime下载或根外fallback。
4. 同一backend的共享根guard/lock只在全部lease和lane真结束后归还；各lease先native/模型退出→关文件guard→按登记叶逐项DeleteFileW/RemoveDirectoryW→归还代目录guard。持有的no-share-delete目录需在其登记子项已清后关闭本目录guard再RemoveDirectoryW，父guard保持；失败保留成功分量及原holder。额外文件/改identity/不明残留停止该代cleanup并给ResourceDrainFailed，不递归删、不枚举猜归属。重启没有原可信登记时不自动清残留，由部署Host按原记录处置；不增加持久journal/自动恢复存储。

该根自绑定身份保证本代打开后不被普通非受信主体替换；若部署额外要求预指定物理卷/根file ID，由部署Host在把ScratchRoot交本factory前验证，不把首次观察当预指定介质证明。H-F01/H-L01/H-R01新增软件/真实路径反例：ancestor reparse、根换名/volume变化、未知写ACL、重复lock/代目录、copy取消/hash坏、writer尚未退出、reader要求写、额外叶与cleanup失败；SafeMaterialization未在目标NTFS真实验证前不声明已验。

### C.4 精确预处理与输出支持路线

首版图像源支持UInt8/UInt16/Int32/Float32的HW/HWC/CHW，显式通道数/顺序；Float16/Float64 Image返回InputFormatUnsupported，不通过隐式降精度接纳。generic Tensor支持A.1所有数值element type，按BCL显式小端读值（Half按IEEE binary16），先核有限性/shape后生成integer/real tuple，实际模型计算precision仍按读回；不把模型float32运算承诺为binary64保真。Tensor只支持已冻结none resize/相同shape，所有预处理与轴顺序由manifest绑定。超过HALCON input layer三维tuple布局可表示的rank/axes、region_to_bin输入、本版未定义的constant可变约定一律Unsupported，不猜reshape/补0。constant层仅读shape/input_type/const_val/keep_batch_size_const，核封存闭包固定值，不能出现在manifest.inputs/request.Values；其它actual输入名集合必须与manifest完全相等。

预处理固定实施§6.3/6.4的已有公式。本版为保证两种pixelCenter、edge复制、mask及单像素轴的同一语义，选**有界坐标采样**，不直接用zoom_image_size/transform_dl_sample_batch默认行为。逐通道从input lease按已声明stride复制紧凑源，pin仅在同步gen_image1真返回前保持（byte/uint2/int4/real）；HALCON返回独立matrix后解pin。每块<=MaxChunkPixels，在ROI内按冻结inverse坐标公式生成原图row/col，先夹到ROI边界；nearest显式floor(x+0.5)后get_grayval，bilinear用get_grayval_interpolated(...,'bilinear')，只读HALCON能力不另写视觉插值实现。逐块返回tuple后以确定double做range/clamp/mean-std（仅规范数值变换），有效域按真实贡献点权重>0检验，padding以源范围进入相同步骤；空间mask不得依赖这两个忽略domain的算子。图像目标值checked转float32，溢出/非有限拒绝，组装real单channel matrix再按声明顺序compose/append channel、set_dict_object；tuple路线set_dict_tuple。DLSample字典一sample一组所有named values；不把channel数当sample数。

该路线优先正确性，get_grayval手册明确有调用开销，不声称大图最快；块大小及各临时tuple/坐标/源/目的managed+native账在准备前checked估算，队列之外不得无限扩张。本版不改变进程set_system('int_zooming')；未来更快HALCON变换只有同一训练规范/有效域/边缘Golden对齐及同样本尾延迟/资源比较后才以新Adapter版本加入。矩阵/domain/object alias按私有allocation holder归属，set_dict_object是引用性object复制，不当深拷贝；原matrix和dict持有期间均不可改写，清dict后仍需Dispose单独取出的object副本。set_dict_tuple含handle只复制handle值，不移交其资源所有权。

| 支持范围 | 必须绑定、核值、后处理及明确拒绝 |
|---|---|
| classification / multi-label | 标准键全类数组/classMap按§6.5，原生置信与canonical codec校准/阈值分开。分类解释只独立gen_dl_model_heatmap，需actual inference_only=false及已预约训练级资源；无解释能力不阻主结果，OOD required却无actual能力不能冒充分布完整 |
| rectangle1/rectangle2 detection、instance | nativeNMS读回与post精确相等；core NMS仅现有axis-iou；需要未定义core rotated/mask算法时Unsupported。region/mask/geometry由cv2区域算子栅格化、有效域交集和visibility后复制§6.6 managed raw；N=0合法，少sample不补位 |
| segmentation / anomaly / gc-anomaly | 输出图必须实际HW/channel/type匹配，unknown有效域保留，tile仅现有支持task按固定grid/nms；GC local/global成对绑定，不以max图替整图score。未登记的新异常归一化/聚合、随机预处理、3D输入任务均Unsupported |
| generic embedding / OCR对照 /其它已登记task | named input layer与inference output sourceKey逐个读回，轴转换/多tensor/剥sample轴依§6.5；embedding和greedy CTC仅委托原codec，不复刻第二套算法。专用Deep OCR/DL classifier旧类型未走read_dl_model模型主链者不属本版factory，AdapterNotReady，不据§2.3备选自动跳转 |

原始输出全部按§6.4–6.6复制为immutable bytes后交给Core codec；HALCON返回sample基数必须=本次submitted（补满内部项不纳入），item/tile/batch序由准备清单固定。获取pointer只在私有object存活期同步复制，pointer/tuple/dict/device永不外传。全部输出数组/region栅格化前先核schema上限/shape乘积与request MaxOutputBytes；原生已生成但超限的对象仍保持到真实释放，事后拒绝不能称分配前上限。Native/GPU allocator与模型scratch无法由matrix尺寸精确报价，MaxAccountedNativeBytes仅控制本方矩阵/tuple payload，不是整个HALCON堆硬上限；真实峰值和RequiredBudget正确性另验，不伪造硬隔离。

区域实现固定为每候选独立处理：按§6.4逆变换得到原图四角后，以cv2.gen_region_polygon_filled生成完整polygon region（26.05对亚像素顶点先round，允许边缘像素偏差，Golden按此HALCON栅格语义核验；不是连续polygon面积或Core IoU）。原图边界用gen_rectangle1，原有效mask按row/col升序且end>=begin的连续run用gen_region_runs生成；空有效mask直接记录交集0，不生成未知空域。intersection逐候选与有效域/边界相交。分母是完整候选polygon region的像素面积，分子是上述交集面积；先count_obj核空对象，再对单region取get_region_runs，runs空直接面积0，非空才area_center取像素数，分母0固定visibility=0；不是把边界裁后面积当分母。不依赖全局set_system('store_empty_region'/'empty_region_result')，不更改进程全局开关。实例mask单个region经get_region_runs按row升序、含端点col范围填已预算u8[H,W]，只写边界内并保留candidate顺序；全部native region/tuple副本归私有holder释放。旋转框四角及连续Core NMS仍用已冻结公式；本路径只细化backend.visibility/mask，不改Canonical或替Core增加rotated/mask NMS。

上述窄查阅依据为26.05 [gen_region_polygon_filled](../../../halcon算子手册/operators/gen_region_polygon_filled.html)、[gen_rectangle1](../../../halcon算子手册/operators/gen_rectangle1.html)、[gen_region_runs](../../../halcon算子手册/operators/gen_region_runs.html)、[count_obj](../../../halcon算子手册/operators/count_obj.html)、[intersection](../../../halcon算子手册/operators/intersection.html)、[area_center](../../../halcon算子手册/operators/area_center.html)、[get_region_runs](../../../halcon算子手册/operators/get_region_runs.html)；get_region_runs只接单region，intersection会先联合第二对象集合，所以不把多个候选放第二集合以免串身份。

栅格前先核有限顶点、HALCON坐标可表示域和round后包围HW的checked乘积/run最坏长度及预算；超限OutputSchemaMismatch/BudgetUnavailable，不先分配大region或先裁框改变分母。无效/零面积几何按原规范拒识。区域同步段固定在同一原native Task的同一线程连续执行，不跨await：get_system('tsp_clip_region')保存原值→set_system('tsp_clip_region','false')并读回→完整polygon/有效run/交集及复制→finally在同线程恢复原值并读回。26.05的tsp_仅当前线程有效，不修改进程clip_region或其它线程；恢复失败保ResourceDrainFailed并停止该lane接纳，不能让复用线程带污染成功退出。查询/设置失败在生成区域前AdapterNotReady/CapabilityNotObserved；原Task仍走正常清理。官方 [get_system](../../../halcon算子手册/operators/get_system.html) 可读set_system全部参数， [set_system](../../../halcon算子手册/operators/set_system.html) 明确tsp_clip_region线程边界。H-P01/H-O01加入亚像素polygon、边界外顶点、空交集/空mask、同shape多候选、regions只接一个、面积0及thread-local恢复反例；这些冻结HALCON边缘行为不等于已测正确。

### C.5 原 Task、有限取消、排空与 Factory 前进程根

`HalconHostRootFactory.Create` 是同步纯托管根；由进程入口在任何Source/Adapter/Core factory之前创建并强持，TryReserve先占有界slot。不能将root作为方法局部await using，不能用窗口/方法栈/日志/弱引用充当Owner。SessionId非空且在进程根内不复用；满槽拒绝新建，ResourcesReleased前不归还槽。所有Start调用先在root锁内核callId非空/限长、holder数/heldBytes上限，登记callId/holder/CTS/strongHolds，再锁外调用start一次并保存其**原Task**；同步starter抛错也保留登记与已登记factory结果供清理。重复callId/同T和同强持意图/heldBytes返回原Task，不再调用delegate；类型/意图不等抛ArgumentException。strongHolds仅保存宿主服务、不可变请求、端口、租约与engine引用，禁止在此公开通道传native句柄；heldBytes为本调用保持的独立请求/结果/输入payload承诺上界，原服务对象自身堆不混算，重复引用由同holder预算保护，不把pin另算allocation。CTS/token不进入任何持久DTO。每slot保留原调用至session收尾，MaxCallsPerSession须在Start前检查，满则禁止新业务调用，不驱逐在途调用。

Root四个计数/字节上限均正、MaxCleanupWait有限且>0；每slot在业务接纳时同时预留一个cleanup holder，其字段按已登记factory组件/lease/原call的有限数量保存逐项释放Task和诊断，不占可被后续业务耗尽的容量。source/backend每次接纳在自身MaxSourceCalls/MaxPendingPrepares门内先保留对应固定清理记录，再开始资源获取；清理重试只替换已经真结束的失败Task，保留上一回执摘要，不累计无限原Task列表。Factory注册的byte快照也计入Root.MaxHeldBytesPerSession，超限在IO/native前拒绝；root不把调用方任意声明当实际进程RSS证明。Root.Resume/Cleanup waitBudget<=MaxCleanupWait，有adapter时同时<=CleanupObservationBudget；factory失败而尚无adapter时仍由root.MaxCleanupWait保证观察有限。Query unknown SessionId返回AdmissionClosed=true/ResourcesReleased=false/空PendingCalls及InvalidRequest，不造已释放墓碑；同进程已真实返回slot保留只读释放摘要至root.Dispose，SessionId不重用。root/slot.ResourcesReleased只说明本Owner的Task/使用/租约已归还和本方引用已撤，不表示其它Host服务或CLR堆已析构。

factory返回source/backend/codec之前slot登记强引用；Host以本slot的backend/gate调用Core工厂并AttachEngine，登记只允许一次，确认Core工厂成功所有权移交后slot不直接Dispose backend/gate。工厂失败/尚未AttachEngine时slot独自执行backend.StopAndDrain/Dispose及独占gate清理；共享Source服务只能归还本slot交出的lease，不能Dispose原Owner。purpose gate先由Host调用HoldPurposeGate注册，再传Core工厂；同对象重复保持幂等，不同对象/已Attach后替换拒绝，不在失败时丢失。Core factory已成功但Attach登记异常时，原engine必须立即保存在该slot的factory调用holder中，经engine.Drain/Dispose恢复，不能反向清理已移交的backend/gate。

backend内部Prepare/Run/解释/读回/物化/每项Dispose都登记原native/IO Task及强持资源；`ValueTask.AsTask()`只转一次，保存此Task。RequestCancel只改变原operation的取消意图，未开始调用可撤；本版不调用进程全局HALCON中断、不Thread.Abort、不Dispose正使用model，已经进入同步cv2原调用只能观察其真返回/异常，后续批次不再启动。手册声明apply支持interrupt不证明本封装token自动生效，不设“取消成功”能力。Run成功返回须所有正式native apply真返回、结果复制真结束；GPU仅提交/排队回执或Task.WaitAsync超期均不足。实际GPU route必须用已返回可读结果的同步HALCON apply作为执行完成点；不能证明时Value不成功、保持原Task与资源，绝不发Completed/Released。

lease.DrainAsync每次waitBudget为正且<=options.NativeObservationBudget，waitCancellation只结束观察；真实Run/预热/输出借用/释放未结束时proof至少一项false。顺序：封lease准入→请求合作取消→等原Prepare/Run/解释/复制→释放所有result取出object/tuple及result dict→DLSample dict与源/目的matrix→clear_dl_model→归还私有device对象（不reset物理设备）→私有文件/目录与保持句柄→确认全部dispose真实结束。仅全部true后lease.Dispose可成功；部分清理失败记录每分量，重试只处理未完成项，原业务错误与Cleanup诊断分开。Prepare尚未交lease失败采用同序内部清理，清理未结束Prepare原Task不结束，Core保持模型/input/budget原租约。StopAndDrain封新Prepare，排空全部lease和lane，再关闭lane尾段；重复Stop/Dispose只能复用/恢复原清理，不产生并发第二次释放。

Host调用Infer、Query、Drain及Dispose均经slot.Start保存原Task，以wait token/有限WaitAsync观察。超时捕获保留原request/callId/engine/backend/source调用和租约，Query读取原Core安全状态，调用slot.Query核原Task；不换request/attempt、不重新Run。slot.CleanupAsync以独立预算封Host业务入口、请求原Infer取消及Core.Drain一次；移交engine后gate abort/Stop严格由Core按§5.2推进，Host不并发越Owner直接Dispose gate/backend；在原Task真结束且AllOperationsDrained=true后才调用engine.Dispose并确认结束。清理等待/取消不使用已经取消的业务token，最大观察<=CleanupObservationBudget，调用者token只结束等待；未排空返回ResourcesReleased=false和PendingCalls，原错误不被cleanup异常覆盖。根通过ResumeCleanupAsync复查/恢复同slot和原释放身份；未完成不会因方法离栈、应用窗口关闭、GC或等待到期自动失去强持。

Resume可以重发**已真结束但失败且契约允许幂等重试**的Drain/Release/Dispose；原Task仍pending时只观察同Task。Start业务ID不变，cleanup重试在原cleanup holder登记attempt单调序号，不创建新业务意图。未来若需要把root移交进程监督Owner，先由接收方显式登记同session/原Task/租约并返回接管确认，确认前原root持续持有；本版不实现外部worker/进程死亡后的释放证明。进程退出前未排空必须报告未确认，不能用PID消失作native释放证据。Root.Dispose在存在未释放slot时拒绝并保留全部记录；只有所有slot.ResourcesReleased且最后调用/CTS/观察者尾段已结束才成功。

设备所有权澄清：上段“归还私有device对象”仅指本adapter持有的query返回tuple和非拥有引用；设备handle可能指向共享HALCON设备，绝不clear_handle、reset、set_dl_device_param或调用可能销毁共享设备的owning wrapper.Dispose。本版以cv2及私有tuple借用device，不构造拥有设备生命周期的HDlDevice；clear_dl_model只释放fresh模型。模型/所有native调用退出后才能释放tuple/wrapper引用；Capability记录实际id的原HALCON标量类型/值，不用handle或从runtime字符串猜类型。由此仍不获得设备控制权，原设备Owner不被本backend关闭。

### C.6 两个完整无 UI Host 配方

两个配方在 A.5 唯一 `.Halcon.Tests` 的独立装配根执行，HostA/HostB不同SessionId/TrustedConsumer/Purpose/预算/gate/adapter实例，原ModelAssets和Frame服务可由宿主显式共享，根各slot与lease独立。Core规范、源桥和HALCON端口同一DLL，无产品DI、窗口、静态Store、私表或设备命令。实际模型值从该Host的精确发布交接提供；表内符号指必需参数，未提供即该Host NotReady，不填合成值冒充客户模型。

| 顺序 | HostA：缺陷候选 Classification/Rectangle1 | HostB：工程辅助 generic 多输入 Embedding/OCR对照 |
|---|---|---|
| Factory前Owner与原服务 | 进程根Create→TryReserve(sessionA)；以公开ModelAssetsHost与FrameServiceFactory装配/取得原Owner服务，保留其原root；Budget端口、canonical codec、exclusive purpose gate、TimeProvider均显式注入 | 同根另slotB或另进程根；可借同service但不同Principal/Consumer映射，独立gate/预算/诊断；ModelAssets Scope/Principal必须等原SessionInfo，禁止从request冒认 |
| 必需模型参数 | 发布映射RootA→ManifestA/模型/类表/pre/post/raw/output及FilesA、RuntimeA bytes、RequiredBudgetA；Profile=`halcon.classification`或`halcon.rectangle1`，单named图目标H/W/C、实际device四元组/precision/batch明确 | RootB→ManifestB等完整成员/FilesB/RuntimeB；generic输入层例如`<实际图层名>`与`<实际辅助tensor层名>`，shape[W,H,D]、输入类型、所有输出层/NativeShape/Axes和向量或T/C字典完整，不能用示例名字当真实层 |
| 必需输入参数 | 原FrameKeyA/window/planes、unit/channels、typed source bytes hash、ROI/validDomain/coordinate精确注册；ClassMap/NMS/阈值从封存post取 | FrameKeyB及辅助tensor独立Source hash/strides/bytes/解释注册，同一item多named Values；embedding输出vector或OCR logits的dtype/axes/layer精确，不从byteLength推shape |
| 公开装配调用 | HalconOwnerSourceFactory.Create(sourceOptionsA, borrowedAssets, borrowedFrames, modelsA, framesA, tensorsA, time, slotA)→HalconInferenceAdapterFactory.Create(adapterOptionsA, bindingsA, canonicalCodec, time, slotA) | 相同两个factory用B注册，tensorsB可以非空；两边sourceOptions.TrustedConsumer各等engine options，不共享backend或purposeGate |
| Core factory | 先slot.HoldPurposeGate(purposeGate)，以 `InferencePorts(sources.ModelResolver,sources.InputProvider,budget,adapter.Backend,adapter.TaskCodec,purposeGate,diagnostics)` 在slot.Start的同步starter内调 AiInferenceEngineFactory.Create(options,ports,time)并以Task.FromResult保存原返回engine，再slot.AttachEngine；失败slot保留adapter/gate清理 | 同调用但独立装配根；不复制Core、不引用A配置，不创建隐藏窗口初始化 |
| 执行/读取 | 构造A.1完整request（model binary引用，runtime Ref精确，deadline同time单调域）→engine.Validate→slot.Start("infer/<id>", ct=>engine.InferAsync(request,ct).AsTask(), holds, heldBytes)；有限观察→slot.Start原Query→检查原State/Result、schema/hash/候选数值及adapter.QueryCapability原actual读回 | 同序，同一item Values使用模型inputs名集合；核named layers分别读回及raw→final变换，不把向量/文本候选升级为质量/身份决定；每Host独立结果语言投影/权限与撤权试验 |
| 到期/恢复/收尾 | 观察到期登记取消意图→保原Infer Task→Query同request→slot.CleanupAsync有限观察；未排空root.ResumeCleanupAsync，true且engine.Dispose真结束才归还本Host slot；原Frame/Asset服务仍由原Owner关闭 | A挂起不取消B/释放B模型或输入；B正常完成仍独立取结果并Drain/Dispose；B也有同原Task恢复路径，未知不换新attempt。最后原Owner仅在全部借用已回收后关共享服务 |

第一轮无native验证使用现有Simulator和受控闩锁覆盖这些接线/失败/迟到，但不得把它称为真实Host/Golden通过。真正的A/B消费模型与数据必须各在目标HALCON环境执行，保留各自己的原Owner回执/配置读回/输出/释放证明；两个测试类名或相同模拟port实例不算双真实消费者。

#### C.6.1 完整公开调用函数（仅指导样例）

下面的函数放在未来 `.Halcon.Tests` 的 Host fixture，不是新产品 API。`published` 是**进程内具名 ValueTuple 参数组**：所有元素复用 C.1/A.1/A.4 已公开类型，来自 C.7 的同一真实发布交接/Profile及原Owner；不是第二个Golden Profile schema，不序列化此tuple。模型/输入/实际设备或用途未交接时，不调用业务或返回既有 `AdapterNotReady` 加 `AiInference.Host.NotReady` 诊断；不造客户模型、FrameKey、hash、层名、shape、预算或阈值。canonicalCodec/budget/purposeGate/原资产与帧服务均为显式必需入参，只有diagnostics可null；purposeGate必须本session独占，根与原服务由进程Owner在调用前创建并一直强持。

`rootOptions` 必须是创建 `processRoot` 时使用的原参数，不能换一份更宽限额。函数只复制同一Core options及请求事实，deadline从本进程TimeProvider与明确ExecutionBudget建立，不沿用profile中的旧进程tick；ObservationBudget/cleanup等待独立于业务取消。返回的WorkErrors与CleanupErrors是两条诊断轴；不会以收尾异常替换原业务错误，也不会把root未排空解释为Core业务失败或已释放。

```csharp
using System;
using System.Collections.Immutable;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.AiInference;
using Asun.Modules.AiInference.HalconAdapter;
using MA = Asun.Modules.ModelAssets.Service;
using IF = Asun.Modules.ImageFrame.Resources;

static async Task<(
    InferenceResult? Result, InferenceOperationStatus? Query,
    InferenceValidationResult? Validation, HalconCapabilityObservation? Capability,
    HalconHostObservation? Cleanup, ImmutableArray<InferenceDiagnostic> WorkErrors,
    ImmutableArray<InferenceDiagnostic> CleanupErrors)> RunPublishedHalconHostAsync(
    IHalconHostRoot processRoot, HalconHostRootOptions rootOptions, TimeProvider timeProvider,
    (Guid SessionId, InferenceEngineOptions EngineOptions, HalconOwnerSourceOptions SourceOptions,
     HalconAdapterOptions AdapterOptions, MA.IModelAssetService Assets, IF.IFrameService Frames,
     ImmutableArray<HalconModelAssetBinding> AssetModels,
     ImmutableArray<HalconFrameValueBinding> FrameValues,
     ImmutableArray<HalconTensorValueBinding> TensorValues,
     ImmutableArray<HalconModelBinding> ModelBindings,
     IInferenceBudgetPort Budget, IInferenceTaskCodec CanonicalCodec,
     IInferencePurposeGate PurposeGate, IInferenceDiagnosticsSink? Diagnostics,
     InferenceRequest Request, TimeSpan ExecutionBudget, TimeSpan ObservationBudget,
     TimeSpan CleanupBudget, long HeldBytes) published,
    CancellationToken waitToken)
{
    IHalconHostSlot? slot = null;
    InferenceResult? disclosed = null;
    InferenceOperationStatus? query = null;
    InferenceValidationResult? validation = null;
    HalconCapabilityObservation? capability = null;
    HalconHostObservation? cleanup = null;
    var workErrors = ImmutableArray.CreateBuilder<InferenceDiagnostic>();
    var cleanupErrors = ImmutableArray.CreateBuilder<InferenceDiagnostic>();
    var engineBox = new StrongBox<IAiInferenceEngine?>(null);
    const string inferCallId = "host/infer";
    const string queryCallId = "host/query";
    bool inferStarted = false;
    bool queryStarted = false;
    string stage = "HostHandoff";
    // 最多一次Cleanup和一次Resume；该正预算在取得slot前校验。
    TimeSpan cleanupBudget = TimeSpan.Zero;

    InferenceDiagnostic Error(string code, string field, string key, string detail) =>
        new(code, field, key, false, stage, null, ImmutableArray.Create(detail));

    try
    {
        ArgumentNullException.ThrowIfNull(processRoot);
        ArgumentNullException.ThrowIfNull(rootOptions);
        ArgumentNullException.ThrowIfNull(timeProvider);
        ArgumentNullException.ThrowIfNull(published.EngineOptions);
        ArgumentNullException.ThrowIfNull(published.SourceOptions);
        ArgumentNullException.ThrowIfNull(published.AdapterOptions);
        ArgumentNullException.ThrowIfNull(published.Assets);
        ArgumentNullException.ThrowIfNull(published.Frames);
        ArgumentNullException.ThrowIfNull(published.Budget);
        ArgumentNullException.ThrowIfNull(published.CanonicalCodec);
        ArgumentNullException.ThrowIfNull(published.PurposeGate);
        if (published.Request is null || published.AssetModels.IsDefaultOrEmpty ||
            published.ModelBindings.IsDefaultOrEmpty || published.Request.Inputs.IsDefaultOrEmpty ||
            published.FrameValues.IsDefault || published.TensorValues.IsDefault ||
            (published.FrameValues.IsEmpty && published.TensorValues.IsEmpty) ||
            published.ModelBindings.Any(b => b is null || b.RuntimeProfileBytes.IsDefaultOrEmpty ||
                b.Files.IsDefaultOrEmpty))
        {
            workErrors.Add(Error("AdapterNotReady", "published", "AiInference.Host.NotReady",
                "MissingModelOrInputHandoff"));
        }
        else if (published.SessionId == Guid.Empty || published.ExecutionBudget <= TimeSpan.Zero ||
                 published.ObservationBudget <= TimeSpan.Zero || published.CleanupBudget <= TimeSpan.Zero ||
                 published.ObservationBudget > TimeSpan.FromSeconds(60) ||
                 published.CleanupBudget > TimeSpan.FromSeconds(60) ||
                 rootOptions.MaxCleanupWait <= TimeSpan.Zero ||
                 published.AdapterOptions.CleanupObservationBudget <= TimeSpan.Zero ||
                 published.HeldBytes < 0)
        {
            workErrors.Add(Error("InvalidRequest", "published", "AiInference.Host.InvalidArguments",
                "InvalidSessionOrWaitBudget"));
        }
        else
        {
            cleanupBudget = TimeSpan.FromTicks(Math.Min(published.CleanupBudget.Ticks,
                Math.Min(rootOptions.MaxCleanupWait.Ticks,
                    published.AdapterOptions.CleanupObservationBudget.Ticks)));
            if (published.SourceOptions.TrustedConsumer != published.EngineOptions.TrustedConsumer ||
                published.Request.Consumer != published.EngineOptions.TrustedConsumer ||
                published.SourceOptions.Scope != published.Assets.SessionInfo.Scope ||
                published.SourceOptions.PrincipalRef != published.Assets.SessionInfo.PrincipalRef ||
                published.SourceOptions.MaxIdentityChars != published.EngineOptions.MaxIdentityChars ||
                published.AdapterOptions.MaxIdentityChars != published.EngineOptions.MaxIdentityChars ||
                published.AdapterOptions.MaxOperations != published.EngineOptions.MaxOperations)
                throw new ArgumentException("Host binding differs from original owner/options", nameof(published));

            waitToken.ThrowIfCancellationRequested();
            stage = "HostReserve";
            if (!processRoot.TryReserve(published.SessionId, out slot) || slot is null)
            {
                workErrors.Add(Error("BudgetUnavailable", "SessionId", "AiInference.Host.RootUnavailable",
                    "NoOwnerSlot"));
            }
            else
            {
                // Gate在任何可能抛错的Source/Adapter/Core装配前先交根保持。
                slot.HoldPurposeGate(published.PurposeGate);
                stage = "HostFactories";
                HalconOwnerSources sources = HalconOwnerSourceFactory.Create(
                    published.SourceOptions, published.Assets, published.Frames,
                    published.AssetModels, published.FrameValues, published.TensorValues, timeProvider, slot);
                HalconAdapterPorts adapter = HalconInferenceAdapterFactory.Create(
                    published.AdapterOptions, published.ModelBindings,
                    published.CanonicalCodec, timeProvider, slot);
                InferenceEngineOptions supplied = published.EngineOptions;
                var options = new InferenceEngineOptions(
                    MaxItems: supplied.MaxItems, MaxRank: supplied.MaxRank,
                    MaxIdentityChars: supplied.MaxIdentityChars, MaxTraceChars: supplied.MaxTraceChars,
                    MaxOperations: supplied.MaxOperations, MaxDiagnosticEvents: supplied.MaxDiagnosticEvents,
                    MaxDiagnosticsPerOperation: supplied.MaxDiagnosticsPerOperation,
                    TrustedConsumer: supplied.TrustedConsumer, PurposeCheckTimeout: supplied.PurposeCheckTimeout,
                    MaxConcurrentPurposeChecks: supplied.MaxConcurrentPurposeChecks,
                    InstanceBudget: supplied.InstanceBudget);
                var ports = new InferencePorts(sources.ModelResolver, sources.InputProvider,
                    published.Budget, adapter.Backend, adapter.TaskCodec,
                    published.PurposeGate, published.Diagnostics);
                var factoryHolds = ImmutableArray.Create<object>(engineBox, options, ports,
                    sources, adapter, published.Assets, published.Frames, published.CanonicalCodec);
                Task<IAiInferenceEngine> originalCreate = slot.Start("host/core-create", _ =>
                {
                    IAiInferenceEngine created = AiInferenceEngineFactory.Create(options, ports, timeProvider);
                    engineBox.Value = created; // 原holder先保engine，再形成Task/Attach。
                    return Task.FromResult(created);
                }, factoryHolds, heldBytes: 0);
                // Create是同步有限纯装配；原Task已经登记，仍用有限观察。
                IAiInferenceEngine engine = await originalCreate
                    .WaitAsync(published.ObservationBudget, waitToken).ConfigureAwait(false);
                slot.AttachEngine(engine);

                InferenceRequest handoff = published.Request;
                long delta = checked((long)Math.Ceiling(
                    published.ExecutionBudget.TotalSeconds * timeProvider.TimestampFrequency));
                if (delta <= 0) throw new ArgumentOutOfRangeException(nameof(published.ExecutionBudget));
                var request = new InferenceRequest(
                    RequestId: handoff.RequestId, Consumer: handoff.Consumer, Purpose: handoff.Purpose,
                    Attempt: handoff.Attempt, Model: handoff.Model, TaskKind: handoff.TaskKind,
                    Inputs: handoff.Inputs, Preprocess: handoff.Preprocess, Postprocess: handoff.Postprocess,
                    BackendPolicy: handoff.BackendPolicy, BatchPolicy: handoff.BatchPolicy,
                    MonotonicDeadlineTimestamp: checked(timeProvider.GetTimestamp() + delta),
                    DeadlineUtc: timeProvider.GetUtcNow() + published.ExecutionBudget,
                    ResourceBudget: handoff.ResourceBudget, TraceContext: handoff.TraceContext);
                stage = "HostValidate";
                validation = engine.Validate(request);
                if (validation.State == InferenceValidationState.Rejected)
                {
                    workErrors.AddRange(validation.Diagnostics.Take(options.MaxDiagnosticsPerOperation));
                }
                else
                {
                    waitToken.ThrowIfCancellationRequested();
                    var operationHolds = ImmutableArray.Create<object>(engineBox, engine, request, sources, adapter);
                    stage = "HostInfer";
                    Task<InferenceResult> originalInfer = slot.Start(inferCallId,
                        ct => engine.InferAsync(request, ct).AsTask(), operationHolds, published.HeldBytes);
                    inferStarted = true;
                    InferenceResult observedInfer = await originalInfer
                        .WaitAsync(published.ObservationBudget, waitToken).ConfigureAwait(false);
                    // Core终态诊断保留；观察完成不替代当前QueryDisclosure。
                    if (observedInfer.State is not (InferenceTerminalState.Completed or InferenceTerminalState.Partial))
                        workErrors.AddRange(observedInfer.Diagnostics.Take(options.MaxDiagnosticsPerOperation));
                    if (observedInfer.Diagnostics.Any(d => d.Code is
                        "ModelNotFound" or "ModelNotReady" or "EmptyInput" or "AdapterNotReady"))
                        workErrors.Add(Error("AdapterNotReady", "published", "AiInference.Host.NotReady",
                            "ModelOrInputUnavailable"));
                    stage = "HostQuery";
                    Task<InferenceOperationStatus> originalQuery = slot.Start(queryCallId,
                        ct => engine.QueryAsync(request.RequestId, ct).AsTask(), operationHolds, heldBytes: 0);
                    queryStarted = true;
                    query = await originalQuery.WaitAsync(published.ObservationBudget, waitToken).ConfigureAwait(false);
                    disclosed = query.Result; // 撤权/披露失败为null，不能回填observedInfer。
                    if (query.Result is null)
                        workErrors.AddRange(query.Diagnostics.Take(options.MaxDiagnosticsPerOperation));
                    capability = adapter.Backend.QueryCapability(request.RequestId);
                }
            }
        }
    }
    catch (TimeoutException)
    {
        disclosed = null;
        workErrors.Add(Error("InternalFailure", "HostObservation", "AiInference.Host.ObservationExpired", "Timeout"));
    }
    catch (OperationCanceledException)
    {
        disclosed = null;
        workErrors.Add(Error("InternalFailure", "HostObservation", "AiInference.Host.WaitCancelled", "WaitCancelled"));
    }
    catch (Exception ex)
    {
        disclosed = null;
        workErrors.Add(Error(ex is ArgumentException or OverflowException ? "InvalidRequest" : "InternalFailure",
            "Host", "AiInference.Host.OperationFailed", ex.GetType().Name));
    }
    finally
    {
        // 所有资源/原Task仍归进程根；不能在此Dispose根、共享服务或已移交backend/gate。
        if (slot is not null)
        {
            stage = "HostCleanup";
            if (workErrors.Count != 0 || waitToken.IsCancellationRequested)
            {
                try
                {
                    if (queryStarted) slot.RequestCancel(queryCallId);
                    if (inferStarted) slot.RequestCancel(inferCallId);
                }
                catch (Exception ex)
                {
                    cleanupErrors.Add(Error("ResourceDrainFailed", "CancelIntent",
                        "AiInference.Host.CleanupFailed", ex.GetType().Name));
                }
            }
            try
            {
                Task<HalconHostObservation> originalCleanup =
                    slot.CleanupAsync(cleanupBudget, CancellationToken.None).AsTask();
                cleanup = await originalCleanup.WaitAsync(cleanupBudget, CancellationToken.None).ConfigureAwait(false);
                cleanupErrors.AddRange(cleanup.Diagnostics);
            }
            catch (Exception ex)
            {
                cleanupErrors.Add(Error("ResourceDrainFailed", "Cleanup",
                    "AiInference.Host.CleanupPending", ex.GetType().Name));
            }
            if (cleanup is null || !cleanup.ResourcesReleased)
            {
                try
                {
                    Task<HalconHostObservation> originalResume = processRoot
                        .ResumeCleanupAsync(published.SessionId, cleanupBudget, CancellationToken.None).AsTask();
                    cleanup = await originalResume.WaitAsync(cleanupBudget, CancellationToken.None).ConfigureAwait(false);
                    cleanupErrors.AddRange(cleanup.Diagnostics);
                }
                catch (Exception ex)
                {
                    cleanupErrors.Add(Error("ResourceDrainFailed", "ResumeCleanup",
                        "AiInference.Host.CleanupPending", ex.GetType().Name));
                }
            }
            try
            {
                cleanup = processRoot.Query(published.SessionId); // 本地原根观察，无新业务/权限IO。
            }
            catch (Exception ex)
            {
                cleanup = null; // 不能观察就不能证明释放。
                cleanupErrors.Add(Error("ResourceDrainFailed", "RootQuery",
                    "AiInference.Host.CleanupPending", ex.GetType().Name));
            }
            if (cleanup is not null && !cleanup.ResourcesReleased)
                cleanupErrors.Add(Error("ResourceDrainFailed", "RootResources",
                    "AiInference.Host.CleanupPending", "ReleaseUnconfirmed"));
        }
    }
    return (disclosed, query, validation, capability, cleanup,
        workErrors.ToImmutable(), cleanupErrors.ToImmutable());
}
```

`StrongBox<IAiInferenceEngine?>` 只是由原factory holder保持的进程内engine引用；不是持久DTO/native句柄。C.5的factory失败清理必须识别这个已登记box以及成功的原 `Task<IAiInferenceEngine>`：Create已成功而Attach/观察抛错时，用该engine.Drain/Dispose收尾，不把backend/gate仍视为未移交；Create真失败、box为空时才按未移交路径清理。source/backend factory本身的登记仍按C.1，不依赖这只box。Slot.CleanupAsync/Root.ResumeCleanupAsync在发出原清理前记录其原返回Task与各组件Task；样例的WaitAsync包装只限观察，不覆盖原任务。Resume遇到上次原Cleanup仍pending只复查该任务，不重复释放。函数最多两个独立cleanup等待；任一未确认就让进程Owner保持同root/session，稍后仍用公开ResumeCleanupAsync/Query继续原任务，不重发业务。

若业务观察到期，函数不返回迟到推理载荷；Query原Task也由slot保留，Core安全状态/迟到释放按原ID可恢复。root观察为null或ResourcesReleased=false时，调用方必须保留根和原Owner；不能因本函数返回就清根、退出Owner或宣称资源归还。这里没有等待所有shared Frame存储析构。`AiInference.Host.*`为宿主三语消息键：NotReady=“模型或输入未准备”、ObservationExpired=“等待结果超时”、WaitCancelled=“已停止等待”、CleanupPending=“资源仍在释放”、OperationFailed/CleanupFailed=“操作失败/资源释放失败”；不改Core机器码/终态。

两个消费者的实际调用如下；`twoPublishedProfiles[0/1]` 的元素就是上面函数的强类型参数组，由两份原C.7真实Profile和原Owner解包提供。没有额外HostProfile类、占位模型或未定义局部变量。两任务都先启动，WhenAll等待每个函数自己的有限收尾，不传新的共同取消token；每个工作/cleanup轴和根观察分别返回，不合并为PASS。

```csharp
// 同一Host fixture；沿用上一代码块的using。不是新的Profile文件格式。
static async Task<(
    InferenceResult? Result, InferenceOperationStatus? Query,
    InferenceValidationResult? Validation, HalconCapabilityObservation? Capability,
    HalconHostObservation? Cleanup, ImmutableArray<InferenceDiagnostic> WorkErrors,
    ImmutableArray<InferenceDiagnostic> CleanupErrors)[]> RunTwoPublishedConsumersAsync(
    IHalconHostRoot processRoot, HalconHostRootOptions rootOptions, TimeProvider timeProvider,
    ImmutableArray<(
        Guid SessionId, InferenceEngineOptions EngineOptions, HalconOwnerSourceOptions SourceOptions,
        HalconAdapterOptions AdapterOptions, MA.IModelAssetService Assets, IF.IFrameService Frames,
        ImmutableArray<HalconModelAssetBinding> AssetModels,
        ImmutableArray<HalconFrameValueBinding> FrameValues,
        ImmutableArray<HalconTensorValueBinding> TensorValues,
        ImmutableArray<HalconModelBinding> ModelBindings,
        IInferenceBudgetPort Budget, IInferenceTaskCodec CanonicalCodec,
        IInferencePurposeGate PurposeGate, IInferenceDiagnosticsSink? Diagnostics,
        InferenceRequest Request, TimeSpan ExecutionBudget, TimeSpan ObservationBudget,
        TimeSpan CleanupBudget, long HeldBytes)> twoPublishedProfiles,
    CancellationToken observeA, CancellationToken observeB)
{
    if (twoPublishedProfiles.IsDefault || twoPublishedProfiles.Length != 2)
        throw new ArgumentException("Exactly two explicit owner handoffs are required", nameof(twoPublishedProfiles));
    if (twoPublishedProfiles[0].SessionId == twoPublishedProfiles[1].SessionId ||
        ReferenceEquals(twoPublishedProfiles[0].PurposeGate, twoPublishedProfiles[1].PurposeGate))
        throw new ArgumentException("Each host requires its own session and gate", nameof(twoPublishedProfiles));
    if (twoPublishedProfiles[0].EngineOptions is not null && twoPublishedProfiles[1].EngineOptions is not null &&
        twoPublishedProfiles[0].EngineOptions.TrustedConsumer == twoPublishedProfiles[1].EngineOptions.TrustedConsumer)
        throw new ArgumentException("The two consumers must have distinct trusted bindings", nameof(twoPublishedProfiles));
    if (twoPublishedProfiles[0].Request is not null && twoPublishedProfiles[1].Request is not null &&
        (twoPublishedProfiles[0].Request.RequestId == twoPublishedProfiles[1].Request.RequestId ||
         twoPublishedProfiles[0].Request.Attempt == twoPublishedProfiles[1].Request.Attempt))
        throw new ArgumentException("Each consumer supplies its own original request and attempt", nameof(twoPublishedProfiles));
    var originalHostA = RunPublishedHalconHostAsync(
        processRoot, rootOptions, timeProvider, twoPublishedProfiles[0], observeA);
    var originalHostB = RunPublishedHalconHostAsync(
        processRoot, rootOptions, timeProvider, twoPublishedProfiles[1], observeB);
    return await Task.WhenAll(originalHostA, originalHostB).ConfigureAwait(false);
}
```

原Owner入口先以其保留的rootOptions/timeProvider调用 `HalconHostRootFactory.Create`，把所得root作为长生命周期字段传入，并保持RunTwoPublishedConsumersAsync原Task直到它真结束；该调用返回之后仍按每个Cleanup.ResourcesReleased决定是否继续保根/Resume，不设置方法局部await using。两个调用有不同SessionId、request/attempt、可信身份、purposeGate/adapter和预算；只有原资产/帧服务允许在明确登记的原权限域共享。HostA交接classification/rectangle1实际模型，HostB交接generic embedding/OCR对照实际多输入模型；缺其中任一真实交接就对该消费者NotReady，保留另一消费者能力，不构造占位ModelBinding。真实Profile的加载/可信发布与原Owner服务创建由已有公开Owner入口完成，函数据此显式组装options/ports/request，而不读取新Store或重复定义C.7的文件schema。上面60秒仅是C.7 fixture的单次观察安全截止，不是设备节拍或生产执行目标。

软件协议fixture仅用于H-F01/H-H01：以既有Simulator端口及真实C.1装配规格的受控替身覆盖factory失败、Validate拒绝、原Infer/Query闩锁、观察超期、Attach异常、cleanup/Resume迟到和A/B隔离；原任务未结束必须保根。两轮有限自审本段分别检查所有类型/参数/构造字段/返回值，以及factory失败所有权、原Task强持、当前披露、有限异常收尾与两轴诊断；未创建或运行fixture，未声称C#编译、真实HALCON或Golden通过。

### C.7 工程、Golden矩阵与六项定位

唯一工程/测试工程沿 A.5 `.Halcon.csproj/.Halcon.Tests.csproj`，目标 `net10.0-windows`、x64、无WPF/WinForms；直接引用现有AsunImage及本模块Core、ModelAssets Core/Service、ImageFrame Core/Resources公开工程。namespace按C.1；不直接引用halcondotnet、不安装/换DevExpress或查依赖授权。Halcon.Tests仍用Microsoft.NET.Sdk/BCL OutputType=Exe、无测试PackageReference，引用受测工程与上述公开契约，独立Root/Host fixtures和确定性断言；无native模式显式只验证adapter软件协议，不能全部退出0冒充真实必需Golden执行。正式HALCON模式由具名Host任务Profile显式提供模型/输入/期望/容差与资源目标，缺必需项返回非零并列用例ID+NotReady，其他任务不受影响；不自动生成任务数据、模型或容差。

```powershell
dotnet build src/Modules/ai-inference/Asun.Modules.AiInference.Halcon/Asun.Modules.AiInference.Halcon.csproj -c Release
dotnet run --project tests/Modules/ai-inference/Asun.Modules.AiInference.Halcon.Tests/Asun.Modules.AiInference.Halcon.Tests.csproj -c Release -- --mode software
dotnet run --project tests/Modules/ai-inference/Asun.Modules.AiInference.Halcon.Tests/Asun.Modules.AiInference.Halcon.Tests.csproj -c Release -- --mode halcon --profile '<精确Host任务Profile绝对路径>'
```

软件/真实模式各报告其全部矩阵项；dotnet test不执行此Exe。每用例60秒真实安全截止/每进程600秒外层上限沿§10.2，不作为现场节拍；Golden较长运行按任务拆有界场景，不能把pending任务或必需项skip记PASS。Profile唯一字段：`id/revision/mode/adapterApi/modelBindings/sourceBindings/request/expectedRaw/expectedFinal/numericTolerances/resourceTargets/caseIds`；model/source/request使用本附录与A.1封闭类型完整投影，expectedRaw/final是§6.6完整canonical bytes及各自hash。实际raw/final都先核自身bytes/hash及schema；与Golden比身份/维度/类表/完整性/拒识/关联精确相等，数值逐slot明示absolute/relative及拒识边界，容差验算`abs(actual-expected)<=absolute+relative*abs(expected)`，不能放宽类别/阈值判定或仅全局任意epsilon。声明容差时不再要求实际整个浮点payload hash等于Golden hash，两份原bytes/hash分别保留；无容差slot要求值精确相等。Profile为Host验证输入，非新模型Store/生产用途资格；准确运行映射参数变化用新revision。

| 用例ID / 两轮视角 | 必需输入与断言 / 模式 |
|---|---|
| H-F01 / Factory与端口 | 全参空Host装配、未知version/schema/duplicate/path/budget/root满、Core factory失败、共享服务不Dispose；无IO factory及强持槽先于所有调用；software必验 |
| H-S01 / 原Owner桥 | exact root/view/file映射、逐member真实EOF/hash、父子lease释放、原projection摘要、Read为ExactSamples、大小端/stride/域/padding/hash；source Read/Release挂起或迟到，Acquire/model Dispose不提前完成；software+halcon |
| H-C01 / 支持域反例 | 设备四元组零/重复匹配、precision/batch/shape/类表/NMS/required output不等、Unavailable/Unsupported/QueryFailed，optional解释/OOD区别，未converted即不转换；可控软件反例+每实际任务的halcon读回 |
| H-P01 / 预处理数值 | 每实际preprocess的nearest/bilinear、half-pixel/align-corners、单像素轴、边界/letterbox整数尺寸、12/16位范围、mask hole/padding、channel换序、mixed named inputs；完整prepared/raw/final与批准Golden对比，CPU/native浮点容差来自Profile，software坐标及halcon样本均验 |
| H-O01 / 完整任务与Golden | 每绑定profile正常、合法零候选/无效输出、多结果、阈值相等/近旁、遮挡/弱信号、NMS等号、OOD/解释、各task真实键/多tensor轴/关联/类表/GC local/global/CTC；完整expected raw/final、各自hash、逐slot容差及精确身份/完整性均核，halcon必验对应任务，不以预热输出当Run |
| H-B01 / 批次与准备 | 1/短批/满批、batch换同伴、多tile边界/覆盖、warmup=0/1真实结束、取消在排队/prepare/预热/Run间；ConfiguredBatch与Submitted分开，缺sample不补位；software屏障+halcon同样本 |
| H-L01 / 原Task与释放 | 物化/read/Prepare/apply/解释/输出copy/clear/model/Input/authority/Dispose各处fault或闩锁，观察超期/取消/迟到不释放或新Run；重复Drain/Release原身份、先fault后恢复只处理未释放分量，GPU仅提交绝非Completed/Released；software故障+halcon真实资源/GPU适用验证 |
| H-H01 / 双Host与恢复 | C.6两完整独立根同时A挂起/B完成、撤权、Core factory异常、无request关闭、root满/原Task强持/cleanup到期/接管确认、反复Resume；software协议与halcon两真实消费者均需各自证据 |
| H-R01 / 性能资源 | 按§11固定模型/shape/batch/device/pre/post/profile、冷装载与预热后P50/P95/P99、CPU/controlled native/实际native/GPU峰值、长稳及资源最终释放；实际任务目标与真实运行缺失仍未验证，不由software数字替代 |

Profile严格UTF-8/NFC、未知/重复字段拒绝、集合和值域按上列公开类型验证，Guid用小写D、bytes用带padding base64、枚举用精确成员名、整数范围按C#字段，禁止通用多态object反序列化。`sourceBindings`完整字段为`ownerOptions/models/frames/tensors`，`modelBindings`为C.1 HalconModelBinding数组，`resourceTargets`含Core/Adapter/Root的具名limits和§11目标（未知物理目标用null并报告未验证，不视为无限或0）；所有文件/登记内容从原Owner读取，profile不给Store连接/凭证。`request`只包含A.1的纯数据字段，排除MonotonicDeadlineTimestamp/DeadlineUtc，新增`executionTimeoutTicks`为正Int64；Harness装配时用注入TimeProvider建立本进程单调deadline/UTC观察时间，不复用上次进程tick。expectedRaw/final按request的显式IDs与本次prepared支持规范核对；实际运行/资源观察另归H-R01，不用冻结Golden时间伪造性能。任务列表caseIds非空、唯一、显式含本次mode的所有必需项，software未执行项标NotApplicable仅指native事实，不输出halcon通过。

本轮仅定向使用本地26.05手册：[get_dl_model_layer_param](../../../halcon算子手册/operators/get_dl_model_layer_param.html)、[create_dl_layer_input](../../../halcon算子手册/operators/create_dl_layer_input.html)、[get_dl_device_param](../../../halcon算子手册/operators/get_dl_device_param.html)、[gen_image1](../../../halcon算子手册/operators/gen_image1.html)、[get_grayval](../../../halcon算子手册/operators/get_grayval.html)、[get_grayval_interpolated](../../../halcon算子手册/operators/get_grayval_interpolated.html)、[set_dict_object](../../../halcon算子手册/operators/set_dict_object.html)、[set_dict_tuple](../../../halcon算子手册/operators/set_dict_tuple.html)、[get_dict_object](../../../halcon算子手册/operators/get_dict_object.html)、[get_dict_tuple](../../../halcon算子手册/operators/get_dict_tuple.html)、[compose3](../../../halcon算子手册/operators/compose3.html)、[append_channel](../../../halcon算子手册/operators/append_channel.html)，以及§2.5已有read/apply/get/set/clear/heatmap页面；affine_trans_image_size/zoom_image_size/deserialize_dl_model只用于界定默认坐标/边缘/序列化的限制，不选为本版隐含预处理或物化入口。复用A.6固定ORT/Triton版本与借鉴范围，不重新联网研究/复制运行时。原Owner语义直接读取ModelAssets B.4/B.5及ImageFrame §4.3，不复制其Store/发布/资源事实。

| DEV-GOV-010 §3.1 项 | HALCON Adapter 唯一规格位置 / 当前结论 |
|---|---|
| ①职责/消费者/依赖 | C.1/C.2/C.6，A.5精确独立工程，两Host和原ModelAssets/ImageFrame/Budget/用途Owner边界明确；指导内容已主限定接收 |
| ②类型/工厂/端口/单位/支持域/失败 | C.1公开形状、C.2物化源、C.3配置/Capability、C.4预后处理、C.5原Task/lease恢复；Core API v0.3不改，内部构造/资源契约指导内容已主限定接收 |
| ③无UI/空Host独立装配 | C.6/C.6.1完整A/B强类型函数及Factory前Root/原Owner桥指导内容已主限定接收，无隐藏初始化；真实原Owner/HALCON接线尚未运行 |
| ④测试/Golden/异常/关闭 | C.7 H-F01～H-R01，C.5原Task/迟到/有限cleanup，精确harness命令；矩阵未执行，任务Golden与物理数据为对应外部输入 |
| ⑤性能测点/预算/负载 | §11/C.3/C.4/C.7；控制payload预约与真实native/GPU峰值分域，模型预算/目标缺失仅对应任务资格未验 |
| ⑥工程/允许禁止/接入/外部门 | A.5/C.7精确落点，仅本模块HALCON工程和其测试目录属于未来获准切片；本轮只写指导，不创建代码。真实模型属性/用途、actual Capability、Golden/两真实Host/性能/现场保留真实门，不退回已接收Core/Simulator |

2026-10-11已完成两轮有限新增规格自审：第一轮从类型/值/算子/边界核对factory→exact closure→named shape→readback→raw→codec，补正原ProjectOpen参数、FrameConsumerId/限额、局部输入预算和明确NMS支持域；第二轮从外部Host/原Task/预算/借用/取消/失败/迟到/关闭核对root→原Owner→engine→cleanup/恢复，补正Frame lease自己的Drained与全局StorageReleased区别、原Owner未交付lease恢复、gate移交和Golden容差/hash关系。自审不是编译、HALCON执行、GPU完成证明、Golden、双真实消费者或生产资格；主会话已限定接收附录C确定指导内容，真实运行/交接与资格仍为 `PreparationIncomplete / NotReady`，Core/Simulator 的 `ModuleCoreImplementationReady` 不变。

### C.8 model-assets 0.3.1-prep 附录 C 的消费与兼容边界

本节直接消费 [model-assets 唯一指导](../model-assets/DEVELOPMENT-GUIDE.md)附录 C，其 Core/Service v0.3签名、旧JCS/Golden和 `model-operation-jcs-v2` 不变。C.2原 `ResolveExactAsync → AcquireContentLeaseAsync → IAssetContentLease.OpenFileAsync` 及 ProjectResolve/ProjectAcquire/ProjectOpen(parent.LeaseId,request)全部保留，不为本模块增加 SourceSnapshot、SD私表或存储事务。

| 上游具体变化 | 本模块唯一消费决定与 Owner |
|---|---|
| C.1 SD注册包/完整可信根/恢复 | 实际选择新存储桥时由原ModelAssets部署Host调用ModelAssetsStorageRegistration.Create、先注册SD可信catalog、保存原Runtime Create Task，成功后Package.AttachRuntime再装配Service。inference只借已经装配的公开Service和原root，不创建resolver/Store，不Attach或Dispose原runtime。原Store请求不含SourceSnapshot；Host保原审计请求、RequestDigest，不能由消费Ref反推/补造 |
| Stage身份修正 | model-sd-stage-jcs-v1的父OperationId/RequestDigest/Scope/Store投影仅IM-014桥实现；inference的request/attempt不替换它。旧Unknown保旧adapter/rule版本、原OperationIdentity/回执/Generation，由原资产Host恢复；不拿新StageKey重发、清目录或重算旧seal。源码装配升级与原未决操作并行隔离 |
| 新seal三Purpose依赖 | Runtime、RebuildSource、ValidationEvidence显式依赖均由模型生产者/工程导入Host完整交接并由资产Owner封存。本模块消费Runtime执行闭包，它不是全部存储GC根列表；不Import/Seal/Commit，也不因只需Runtime把其它Purpose伪空以通过seal。旧seal不追改；依赖未交接只阻断该新导入/封存任务 |
| C.2安全物化/C.3字节缓存 | 本adapter C.3.1复用安全guard原则，仍物化本方managed成员，不借上游IModelAssetMaterializer私有Store hold。上游缓存只实际选择的资产Host装配，默认Enabled=false，无native/持久缓存；上游byte命中仍当前exact/权限/length/hash，不是推理结果或模型实例cache的启用条件。首版inference两缓存仍关闭 |
| C.4 detached签名 | 仅要求签名的工程包入口Host及客户安全Owner调用上游验证。签名不改变bundle/PackageDigest/AssetRef，验证不授用途；普通推理读消费者无新增signature字段或授权判断 |
| C.5 HALCON格式与runtime | 只约束显式选择新Dl/Onnx format adapter的生产者请求；旧不同producer schema保原身份，不静默迁移。生产者必须提供实际Semantics与Runtime映射，下面字段关系冻结；本模块ai.inference-manifest/ai.halcon-runtime bytes不是ModelAssets SemanticSnapshot/RuntimeSnapshot，不直接转塞或改hash。模型root摘要、model binary hash和inference manifest hash分别保留，不互代 |
| C.8权限/用途桥 | 原资产Host用AU Context/Policy/action/fence/watch和用途Provider控制ReadForUse，精确scope/root/GraphRefs/principal/purpose证据Approved且当前Allowed；这只授本次资产读取。本Core仍按§5.2独立Execute/FinalDisclosure/QueryDisclosure，不从AssetLease存在推导生产用途或当前结果披露权。默认不宣称全局即时撤回；原AU Task/watch/root由资产Owner持有，推理只归还自己的租约 |

选择上游C.5 image Dl/Onnx路线的生产者Host，Semantics最小serialized observables为type/min_version/image_width/image_height/image_num_channels/image_range_min/image_range_max/batch_size的真实模型读回；每值按其schema的保序Sequence、元素 `{kind,value}` 编码，Int64为规范字符串，Binary64用JCS，string保原值。不得把tuple转标量或把推理classMap/manifest hash当semantic数字。非图像generic model不在这条image格式支持域，须保已有合法producer schema或返回上游Unsupported，不伪造image shape；不因此阻断本模块已支持的generic推理主链。

上游runtime schema为 `im014.halcon.dl.runtime-v1` / `im014.halcon.onnx.runtime-v1`，需执行/challenge时必需Explicit的runtime.batch_size正Int64及runtime.deviceRef不透明string；producer Host从已冻结推理RuntimeProfile的configuredBatchSize和显式注册deviceRef分别映射，deviceRef不得用设备显示名/句柄自动生成。其RuntimeDeviceResolver.ResolveDescriptor只查冻结登记，无IO；actual query ai2/id/type/name与get_system('version')由上游format执行Owner读取，id保原类型，描述符精确版本/Backend/DeviceType/Name/MaxBatchSize须相符。NotCollected只用于format-only，不用于challenge；precision仅读，不set/optimize。推理runtime profile中的device.id仍既有Invariant字符串匹配字段，跨schema映射必须从实际类型化读回构造，不能parse字符串猜原类型；值/类型不相符明确拒绝该producer映射。

本推理Adapter首版**不实现或冒充 ModelAssetChallengeExecutor**；其输入/报告不是InferenceRequest/Result，无授权可作资格证据的公共转换。无ChallengeRef上游NotRequested；有ref但Host未提供已登记ChallengeExecutor时保Unknown/MA-CAP，不能拿Simulator/热身或普通推理结果生成Approved报告。需要challenge的生产者/用途验证Host从上游公开ChallengeInput/Report契约提供独立受控执行：fresh模型/reader、原materialization借用与Task、报告前真释放、RootRef/ChallengeRef/MethodRevision/Expected与Observed digest/Outcome均按原证据，未知保原根。此能力属于上游格式/用途验证接入，未批准为本模块新公共能力；它不阻断普通已批准exact read推理的软件设计。

本轮同步只改本指导，不改上游Store/Source/Authority/Sink、Core DTO、operation身份或既有封存模型。原C.6发布交接Host如仅借既有Service/Frame服务，无新增导入/格式/签名调用；只有实际选择上游新增adapter的Owner入口更新对应注册/Root/cleanup。上述关系及A.7新增类型/参数、C.3.1失败guard、C.4空域/候选身份、C.5共享device引用已在本永久会话完成两轮有限自审；准入与未执行验证唯一见§15.1。

