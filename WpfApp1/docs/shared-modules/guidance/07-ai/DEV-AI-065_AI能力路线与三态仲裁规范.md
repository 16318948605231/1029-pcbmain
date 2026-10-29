# AI能力路线与三态仲裁规范

> 文档 ID：`DEV-AI-065`；版本：`0.1.0-prep`；状态：`DesignReview`；日期：2026-10-25；适用范围：平台级 AI 能力路线、推理运行时选型与三态仲裁的平台侧规范。
>
> 本页是平台侧**路线与仲裁语义**的唯一入口，不是模型批准、算法批准、阈值批准、生产配置或质量放行授权。页面中的路线选择门、阈值来源、Owner 与证据要求均为可评审内容；精确 Contract/Schema、公共 API 签名、真实样本、Golden/Replay、性能与现场资格仍按各 Owner 继续推进。

## 1. 目的、范围与非目标

### 1.1 目的

平台 AI 能力对标 Koh Young AI Solver 与 Mirtec Smart Learning：在检测主链路直接参与判定，而不是永远只做"建议"角色。代价是必须把每一次自动判定变成可审计、可回放、可归因的工程事实。本页把三件事固定下来，使各模块指导不重复发明：

1. **能力路线**：什么类型的任务走哪条 AI/经典路线，用什么运行时。
2. **仲裁语义**：AI 判定在什么条件下可以自动生效、什么条件下强制转人工、什么条件下进入采样。
3. **平台边界**：训练侧、推理侧、治理侧、复判侧、Web 侧各自拥有什么、不拥有什么。

### 1.2 非目标

- 不新建 Schema、状态机、事实库、推理执行器或质量判定 Owner。
- 不定义平台候选 Schema 的字段级最终形态；字段归 Contract，公共 API 归对应模块指导。
- 不批准任何具体模型权重、阈值数值、用途资格或部署环境。
- 不重复 [DEV-AI-064](DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md) 的 72 项功能卡矩阵，也不重复 [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md) 的训练/部署/生命周期链。
- 不替代 [DEV-AI-061](DEV-AI-061_AI辅助复判开发指导.md) 的复判语义，不替代 [DEV-AI-063](DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md) 的统计验证方法。

## 2. 权威分层：每一层只有一个 Owner

平台级规范最容易失败的方式是"每个模块都写一份自己的 AI 说明"。下表固定归属；同一议题在别处出现时只能链接，不得重定义。

| 议题 | 唯一 Owner | 本页引用 |
|---|---|---|
| 三态仲裁的**实现**（枚举、证据包结构、推理侧产出） | [IM-047 ai-inference §1A](../../../independent-modules/ai-inference/DEVELOPMENT-GUIDE.md) | §4 给出平台语义约束，实现细节以该节为准 |
| 推理执行契约、EP 选择、批次、取消与排空 | [IM-047 ai-inference §2.3B](../../../independent-modules/ai-inference/DEVELOPMENT-GUIDE.md) | §3.5 只陈述平台选型结论 |
| 逐任务路线与数据分组（72 功能卡） | [DEV-AI-064](DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md) | §3.1 复用其路线代码 `C0/C1/C3D/OCR/STAT/ASSIST/QUERY` |
| 模型训练、发布/撤回、用途资格 | [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md) | §3.6 只声明分离原则 |
| 数据集、GroundTruth、划分、统计验证 | [DEV-AI-063](DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md) | §7 引用其分组与隔离要求 |
| 人工复判、意见、仲裁事务 | [IM-067 human-review](../../../independent-modules/human-review/DEVELOPMENT-GUIDE.md) | §4.3 只定义 `NeedsHuman` 的交接 |
| 人工结论回流与采样队列、L1-L4 闭环 | [IM-048 ai-dataset-governance §7.4](../../../independent-modules/ai-dataset-governance/DEVELOPMENT-GUIDE.md) | §5 引用其四层 Owner 划分 |
| 模型资产注册、哈希、canonical | [IM-014 model-assets](../../../independent-modules/model-assets/DEVELOPMENT-GUIDE.md) | §3.6 只声明制品寻址方式 |
| 参数编辑与人工采纳 | [IM-062 parameter-editor](../../../independent-modules/parameter-editor/DEVELOPMENT-GUIDE.md) | §5.2 定义 L2 的信号入口 |
| 工业协议、Web 端接口 | [IM-046 integration-transport](../../../independent-modules/integration-transport/DEVELOPMENT-GUIDE.md) | §6.3 定义 Web 端职责边界 |
| 视觉算法与算子选择 | [DEV-VIS-021](../03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md) | §3.2/§3.3 引用其路线门 |

> 若本页与上表任一 Owner 的已批准内容冲突，以该 Owner 为准，并回到本页修订，不在本页建立第二套定义。

## 3. AI 能力路线

### 3.1 路线选择门

任何任务进入学习路线前必须同时满足：

1. 已有可测的 HALCON 经典基线，且已记录其失败模式；无基线不得以单一 AI 分数宣称改进。
2. 失败模式属于**开放缺陷**（外观随材料/光学变化）、候选排序、或文字困难；确定性的几何、标定、有效域与公差判定不走 AI。
3. 数据可按物理 GroupId（板/拼板/批次/设备/光学/时间）分组，且训练/调参/最终测试相互隔离。
4. 同一输入、同一坐标/有效域、同一缺陷尺度、同一拒识政策下的对照证据可复算。

选型结论记入 [DEV-AI-064](DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md) 的路线代码；本页不新增路线代码。

### 3.2 目标检测：RT-DETR

| 项 | 结论 |
|---|---|
| 定位 | 已知外观类别的目标检测。RT-DETR（Apache-2.0）作为平台默认目标检测路线。 |
| 适用 | 已知类别的缺陷目标（缺件、偏移、连锡、明显异物），有标注框可用。 |
| 不适用 | 类别未知但外观开放 → 走 §3.3 异常检测；纯几何/公差 → 走经典链。 |
| 训练侧 | PyTorch 训练，仓库外独立训练工程；平台仓库只接收 ONNX 制品。 |
| 输出 | 候选框 + 类别 + 置信度 + 可选掩码；不改写工艺公差，不直接产出质量放行。 |
| 证据 | 按缺陷尺寸与来源分层报 Recall/FA/Escape/拒识；报 P50/P95/P99 与显存峰值。 |
| 门槛 | 无标注或分组不成立时不得启用；低置信/OOD/超时/OOM 一律回退经典候选或人工未决。 |

### 3.3 异常检测：anomalib PatchCore

| 项 | 结论 |
|---|---|
| 定位 | 正常样本充分、异常开放的表面任务。PatchCore 为**固定源码的离线研究对象**，不自动成为产品依赖。 |
| 适用 | 外观未知、正常样本易得、训练成本需低的表面缺陷候选（如阻焊/涂覆异常）。 |
| 不适用 | 已知类别目标 → §3.2；内部不可见/遮挡/缺测区域 → 走确定性 3D 计量（§3.1 `C3D`）。 |
| 部署 | 经任务批准并完成离线部署验证后，才可作为推理制品进入 `ai-inference`。 |
| 输出 | 异常热图 + 分数 + 拒识原因；热图是候选证据，不是缺陷分类结论。 |
| 门槛 | 必须以正常库覆盖度报告误报分层；正常库缺失导致的误报不得记为算法精度。 |

### 3.4 OCR

文字任务沿用既有独立边界，不在 AI 能力路线内新建识读器：

- 主路线为传统 OCR 与 HALCON Deep OCR；PaddleOCR 仅在固定 commit 下作离线对照，不得默认引入外部运行时。
- 原始读数是**事实**；规范化、纠错、期待值比较、建议另存。
- 期待字段不能当图像真值；模型未覆盖字符、低置信、服务超时 → 拒识/回退/人工，不猜字符。
- 详见 [DEV-VIS-021A OCR与DeepOCR独立能力](../03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md)。

### 3.5 推理运行时：ONNX Runtime 三路 EP

平台推理运行时统一为 ONNX Runtime，三路 Execution Provider 由 [IM-047 ai-inference §2.3B](../../../independent-modules/ai-inference/DEVELOPMENT-GUIDE.md) 实现与探测，本页只固定平台选型意图。

| EP | 平台定位 | 选择条件 |
|---|---|---|
| CPU EP | 默认与兜底 | 无 GPU，或 GPU 显存不足，或其它 EP 探测失败 |
| OpenVINO EP | 工控机首选加速路径 | Intel CPU/核显平台；探测成功即选 |
| CUDA EP | 边缘/独立算力节点 | 用途 Profile 允许 GPU 且显存达标；探测成功即选 |

平台约束：

- EP 探测在宿主启动时执行一次并缓存；探测失败是**降级**不是错误，但每次降级必须留诊断事件。
- EP 选择结果写入模型实例的 `ActiveEp`，推理中途不可切换。
- 模型实例的 EP、ORT 版本、算子集与输入 hash 共同构成制品身份；换 EP 需重跑对应 Profile 的性能记录。
- 工控机（Intel CPU + 核显）以 OpenVINO 为默认加速预期；CUDA 不作为工控机默认依赖。

### 3.6 训练/推理分离与制品寻址

- 训练侧独立仓库（PyTorch）；平台仓库**只放 ONNX 制品与推理代码**，不含训练流水线、数据集原始副本或权重更新逻辑。
- 制品经 [IM-014 model-assets](../../../independent-modules/model-assets/DEVELOPMENT-GUIDE.md) 注册：格式、来源、依赖闭包、哈希、canonical 与版本语义归该模块，本页不建第二模型仓库。
- 推理模块**不得选择 `latest` 模型**；绑定的是注册后的具体版本标识。模型撤回走 [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md) 的发布/撤回链，已在用实例的回退行为由该链规定。
- 模型转换、量化或重新导出后按**新资产**处理，不得冒称原 hash 或声称数值复现。

## 4. 三态仲裁平台规范

### 4.1 终态与判定条件

推理结果经置信度门限与规则链交叉验证后产出且仅产出三个终态之一：

| 终态 | 判定条件 | 平台语义 |
|---|---|---|
| `AutoResolved` | 置信度 ≥ 用途 Profile 的 `autoResolveThreshold` **且** AI 判定与规则链判定一致 | AI 判定直接生效，但必须附完整审计证据 |
| `NeedsHuman` | 置信度 ≥ 阈值 **且** AI 判定与规则链判定冲突 | 强制转人工；**不"谁赢谁算"**，AI 与规则链都不单独定案 |
| `NeedsSampling` | 置信度 < 阈值，或判定为分布外（OOD score > `oodThreshold`） | 不参与判定；样本引用进入主动学习队列 |

仲裁的三条不变量（平台级，任何实现必须满足）：

- **I1 确定性**：相同输入 + 相同用途 Profile + 相同模型版本 → 相同终态。终态是纯函数，不得依赖运行时序或隐藏状态。
- **I2 门限外置**：`autoResolveThreshold`、`oodThreshold` 由用途 Profile 定义并随 Profile 版本冻结，推理模块不得自行设定或自适应调整。
- **I3 失败闭合**：证据包缺任一必填字段、模型版本不可解析、规则链指纹缺失 → 不得判为 `AutoResolved`，降级为 `NeedsHuman`。

### 4.2 规则链的归属

仲裁所依据的"规则链判定"是**调用方传入**的 `RuleChainVerdict`（Pass/Fail/None）。推理模块不自己运行规则链，不对规则链结论负责，也不重算规则链。规则链本身的定义与执行归对应制程/规则 Owner。

因此平台上的仲裁是**宿主侧的分发动作**：`ai-inference` 产出终态与证据包，宿主按终态路由。平台不新增"仲裁器模块"。

### 4.3 分发表

| 终态 | 宿主动作 | 交接目标 | 本平台不做什么 |
|---|---|---|---|
| `AutoResolved` | 记录判定 + 写入审计轨迹 | 结果证据落到事实库（事实 Owner 持有） | 不做质量放行、不写生产参数 |
| `NeedsHuman` | 创建复判任务 | [IM-067 human-review](../../../independent-modules/human-review/DEVELOPMENT-GUIDE.md) 的领取与意见链 | 不重新执行 AI 推理，不代替人工下结论 |
| `NeedsSampling` | 登记采样引用 | [IM-048 ai-dataset-governance](../../../independent-modules/ai-dataset-governance/DEVELOPMENT-GUIDE.md) 的主动学习队列 | 不复制样本数据，不自建采样队列 |

人工结论回流到 `ai-dataset-governance` 的训练标签队列由该模块按 ModelCard 与采样策略处理，推理模块不维护回流逻辑。

### 4.4 审计轨迹最小字段

任何 `AutoResolved` 判定必须可回放出以下字段，缺任一项按 I3 降级：

模型版本标识与制品 hash、置信度数值、OOD 分数（如适用）、特征图/热图引用（如适用）、规则链指纹、冲突原因（如适用）、用途 Profile 标识与版本、阈值取值与来源、时间戳、资源消耗、终态枚举。

终态记录为**追加式**：重算产生新记录，不覆盖历史记录。同一工件、同一用途 Profile、同一模型版本下的终态必须幂等。

### 4.5 冲突语义

AI 与规则链冲突时，平台既不偏向 AI 也不偏向规则链，而是产出**冲突证据包**并强制人工：

- 冲突证据包必须同时保留 AI 判定（含置信度与特征图引用）与规则链判定（含规则链指纹），不允许只保留胜出一方。
- 不得以"重跑一次规则链"、"降低阈值重试"或"人工默认同意"的方式消解冲突。
- 人工对冲突的复判结论属人工事实，其回流标签由治理模块按采样策略决定是否进入训练集，不自动回灌。

## 5. 参数学习 L1-L4 接入

参数学习闭环的四层与各自 Owner 由 [IM-048 ai-dataset-governance §7.4](../../../independent-modules/ai-dataset-governance/DEVELOPMENT-GUIDE.md) 定义，本页只固定平台侧的接入约定：

### 5.1 四层与仲裁的关系

- `NeedsSampling` 是 L2 的**主要输入信号**：低置信与分布外样本正是需要补标注的样本。
- L1 离线参数搜索 → 产出建议 → 人工确认 → 生效。
- L2 从工程师修正挖监督信号 → 产出建议 → 人工确认 → 生效；**不自动改阈值**。
- L3 在线漂移监控 → 触发 L1 任务；触发需用途 Profile 明确允许。
- L4 新物料自适应闭环 → 试产验证 → 人工批准 → 生效。

### 5.2 L2 的信号入口

L2 的监督信号来自 [IM-062 parameter-editor](../../../independent-modules/parameter-editor/DEVELOPMENT-GUIDE.md) 记录的参数修改历史。这使"工程师改了什么"成为可挖的监督数据，是平台相对纯规则链的核心竞争力来源。平台约束：

- 建议与生产参数**物理隔离**，建议不得直接成为生效参数。
- 建议必须带可解释证据与拒绝/过期行为；无法解释的建议不得进入生效路径。
- 人工采纳与拒绝分别记录；采纳率与推翻率作为该闭环的效能指标。

### 5.3 与三态仲裁的边界

三态仲裁决定**这一次检测怎么处置**；L1-L4 决定**参数怎么长期改进**。二者不互相替代：仲裁不在线学习、不改阈值；参数学习不改变当次判定。

## 6. 部署拓扑与职责边界

### 6.1 三类部署位置

| 位置 | 职责 | 约束 |
|---|---|---|
| 工控机（产线侧） | 相机侧推理、低延迟候选产出、设备侧本地留证 | 以 OpenVINO/CPU EP 为主；本地制品存储；断网可用 |
| 边缘/独立算力节点 | 重模型（3D 计量辅助、异常检测、全板复核） | CUDA EP；批量吞吐优先；不直接驱动设备 |
| 服务端（无 UI Host） | 模型装载与预热、批次编排、训练侧编排 | 推理执行在服务端；核心能力可被无 UI 宿主调用 |

### 6.2 训练侧

训练执行在服务端的无 UI Host。训练侧仓库独立；训练任务、checkpoint 与导出链的治理归 [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md)。

### 6.3 Web 端（Blazor Server）

Web 端是**只读投影与标注入口**，不是推理位置：

- 浏览器不加载模型、不执行 ONNX Runtime、不持有模型制品。
- 服务端算几何与坐标，浏览器只渲染标记（坐标计算在服务端完成）。
- 推理候选摘要、置信度分布与三态占比/趋势经 SignalR 推送，**推候选摘要而非原始图像**。
- 模型制品经 HTTP Range 分片下载；大文件（图像/点云）不走超过约定阈值的单条 gRPC 消息。
- 人工标注前端是合法消费形态，但标注决策经授权 gRPC 接口提交并绑定 principal 令牌。
- Web 端**不得提供"使用最新模型"按钮**——模型绑定由版本化 Profile 决定。
- 浏览器不直接持有设备连接或 OPC UA 会话；所有协议连接由服务端创建和管理。

协议与端点注册的公共实现见 [IM-046 integration-transport](../../../independent-modules/integration-transport/DEVELOPMENT-GUIDE.md)。

### 6.4 架构门禁

所有核心库（`Asun.Platform.*`、`Asun.Vision.*`、`Asun.Metrology.*`、`Asun.Domain.*` 及独立模块 Core）禁止引用 `System.Windows.*` 与 `DevExpress.*`。这是 Web 层可选的前提，由架构测试强制保证。

## 7. 数据与证据门

### 7.1 数据分组与隔离

- 训练/调参/最终测试按物理 GroupId 隔离；同一工件不跨集合。
- 正常库、缺陷实例、争议样本、不可见样本、无效域样本分层记录。
- 缺测、遮挡、反光、缺件单独标注，不从分母静默删除。

### 7.2 fail-closed 清单

部署缺件、hash 错误、模型版本不可解析、超时、OOM、OOD、EP 降级、证据缺字段 → 一律显式失败或降级为 `NeedsHuman`/`NeedsSampling`，**不得默认降级为 Success/OK，也不得默认按"合格"处理**。

### 7.3 证据最低要求

任何 AI 路线的验收证据至少包含：按缺陷规模/来源分层的 TP/FN/FP、Escape、拒识率、定位质量、P50/P95/P99（nearest-rank，记录 n）、峰值内存/GPU、取消与恢复行为。禁止只报 accuracy。分位口径统一用 [DEV-GOV-010 §3.1](../../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 规定的 nearest-rank，本页不复制分位算法。

### 7.4 影子与上线顺序

AI 能力上线沿 `Offline → Replay → Shadow → Advice → Automatic` 推进。`Automatic`（即 `AutoResolved` 生效）不是"准确率够高"就自动开启，还需：拒识路径可用、回退可用、权限与审计齐备、资源预算达标、版本快照固定、现场资格通过。每一级必须有退出条件，退出条件归 [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md)。

## 8. 状态、未决与接入导航

### 8.1 本页状态

- 本页状态 `DesignReview`：路线与仲裁语义可评审。
- 本页**不批准**任何模型、阈值、用途资格、部署环境或生产配置；这些仍按 [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md) 与 [DEV-AI-063](DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md) 推进。

### 8.2 未决项与阻断范围

| 未决项 | 阻断范围 | 承接方 |
|---|---|---|
| 平台候选 Schema 与终态字段的最终形态 | 阻断产品集成，不阻断核心实现 | Contract Owner |
| `autoResolveThreshold` / `oodThreshold` 的 Profile 数值 | 阻断 `AutoResolved` 生效 | 用途 Owner + [DEV-AI-063](DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md) |
| RT-DETR / PatchCore 的具体权重与许可证闭包 | 阻断对应制品注册 | [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md) / [IM-014 model-assets](../../../independent-modules/model-assets/DEVELOPMENT-GUIDE.md) |
| 真实样本、Golden/Replay、GR&R 与性能 Profile | 阻断资格结论 | [DEV-QLF-070](../../../shared-modules/guidance/08-qualification/DEV-QLF-070_Golden%20Sample与Replay开发指导.md)、[DEV-QLF-071](../../../shared-modules/guidance/08-qualification/DEV-QLF-071_Performance%20Benchmark与容量资格开发指导.md) |
| Web 端页面与 WPF 资格 | 阻断 Web 交付 | UI Owner / [DEV-UI-040](../../../shared-modules/guidance/05-ui/DEV-UI-040_WPF%2BDevExpress%20Design%20System开发指导.md) |

### 8.3 接入导航

| 我要做 | 去读 |
|---|---|
| 选某功能卡走哪条 AI 路线 | [DEV-AI-064](DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md) |
| 实现推理执行、EP 选择与批次 | [IM-047 ai-inference](../../../independent-modules/ai-inference/DEVELOPMENT-GUIDE.md) |
| 训练、导出、发布模型 | [DEV-AI-060](DEV-AI-060_AI运行治理开发指导.md) |
| 准备数据集与 GroundTruth | [DEV-AI-063](DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md) |
| 接收 `NeedsHuman` 并做人工复判 | [IM-067 human-review](../../../independent-modules/human-review/DEVELOPMENT-GUIDE.md) |
| 接收采样队列并跑 L1-L4 | [IM-048 ai-dataset-governance](../../../independent-modules/ai-dataset-governance/DEVELOPMENT-GUIDE.md) |
| 接入 OPC UA / MQTT / gRPC / Web | [IM-046 integration-transport](../../../independent-modules/integration-transport/DEVELOPMENT-GUIDE.md) |

### 8.4 与历史 ID 的关系

原 AOI 项目的 `DEV-AI-001`（AI设备端推理）与 `DEV-AI-002`（AI模型与数据治理）是**历史副本 ID**，已分别映射到 DEV-AI-060 与 DEV-AI-063，其采纳范围见 [REF-008](../../../references/REF-008_PCBA-AOI指导副本与平台采纳映射.md)。本页使用未占用的新 ID `DEV-AI-065`，不复用历史 ID，也不建立第二份推理执行指导。
