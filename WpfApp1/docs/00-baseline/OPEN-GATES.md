# 当前未决条件与影响范围

本页汇总需要后续冻结的条件，来源登记与采纳步骤仅维护在[GATE-001](REQUIRED-REPOSITORY-AUTHORITIES.md)。所有条件均不阻断已授权的架构/文档整理；不将等待设备或客户参数扩大为全平台停工。

| Gate | State | Impact | Handling |
|---|---|---|---|
| GATE-001 repository authority adoption | SOURCE_PINNED / ADOPTION_PENDING | 精确生产字段、Owner、状态、事件和提交事务的实现 | 10项归档来源hash一致；5份Schema结构与55个本地引用、36项事件实例已检查。来源可读与正式采纳分开；旧路径缺失不等于原件丢失，不复制AOI目录来制造通过 |
| C-01..C-08 exact approved Schema artifacts | CONTRACT_CANDIDATE | 各切片实际依赖的DTO/存储/传输字段 | 继续使用既有候选工作包；禁止临时生产Schema；已有草图不是批准 |
| D-01 首批产品与配置 | DECISION_REQUIRED | 首台机型、在线/离线、单/双面、2D/3D、产品族与目标负载 | 研究顺序已确认：钻孔/微孔→阻焊与终检→钢网→点胶/涂覆→插件与焊后；不等于已确定首台投产机型/交期 |
| D-02 部署和数据策略 | DECISION_REQUIRED | 单机/复判/中心工作站、离线、保留周期、容量、备份、恢复目标 | 架构以模块化单机装配为方案；网络与存储故障策略待产品决定 |
| D-03 角色与质量处置 | DECISION_REQUIRED | 程序发布、人工复判、返修/重检、最终放行和自动反馈 | 设计已分权；具体角色/状态/阈值不能默认继承AOI |
| D-04 质量与性能Profile | INPUT_REQUIRED | 精度/重复性、误报漏报、节拍、板/FOV/目标规模、Golden/MSA/HIL | 定义采样和测量点；数值和资格待产品/设备/质量输入，不能从竞品推导 |
| EXT-CAM 制造接入 | INPUT_REQUIRED | 外部解析器实际集成与目标映射 | 需要元素/层/坐标/单位/板面/版本、Region/XLD资源和序列化公共接口 |
| EXT-CONTROLS 控件接入 | DESIGN_REQUIRED | 现有.NET8 ROI与DeepSight接入.NET10宿主的工程方案 | 只读公共接口；独立宿主桥，不自动迁移控件；不转为AsunImage/DevExpress验证 |
| Hardware SDK contracts | DEFERRED | 具体相机/激光/运动/PLC适配和现场能力 | 保留端口和模拟；型号/协议/触发/互锁依设备资料 |
| Etched bare-board product | WAITING_USER_ASSET | 已完成线路检测产品内部与平台接入 | 等用户拷贝，当前不重做内部算法 |
| X-Ray/CT, ICT, FCT | ENTRY_ONLY | 后续设备族 | 只入口；既有细节作历史来源，本轮无新增详细方案 |
| AsunImage / DevExpress dependency admission | NOT_REQUIRED_BY_USER | 不构成依赖或授权阻断 | AsunImage与DevExpress25.2.3直接采用，不检查安装/兼容性/授权；项目自身行为仍按任务验收 |
| AsunImage project algorithm usage | TASK_SPECIFIC | 具体算法与公共API调用 | 查公共签名及适用官方资料，不猜算子；历史来源不改字冒充新验证 |
| CODE-BASE-01 既有 C# 脚手架移除 | CODEBASE_RESET_BY_USER | 仓库当前无任何已编译工程，`AsunVision.slnx` 不登记工程；各模块指导中的 `src/…`/`tests/…` 路径仅为获准切片时的落点约定 | 移除既有自动生成脚手架，因其公开 API 与依赖方向未与现行指导对齐；实现须严格按模块指导冻结的契约新建工程并登记入 slnx；不得复用已移除脚手架的公开 API，不得从历史状态文档推断完成度 |
| 独立模块纯托管 Core 测试入口 | FROZEN_BY_DEV-GOV-010 | Core/Simulator 的独立软件验证 | 采用 DEV-GOV-010 §3.1 的 net10.0、BCL Exe、固定时钟/闩锁和有限进程截止；唯一工程及 build/run 命令由各模块指导绑定，不再等待测试包选型。既有已冻结测试栈按本模块指导保留；HALCON/WPF/设备与现场资格分别验证 |

关闭条件必须写实际产物和决定：例如批准的Profile、签名/Schema版本、真实设备资料或验收结果。等待中的用户决定已列明影响，当前不请求逐项即时确认；下一轮选择机台或实施切片时只讨论其真正依赖项。C-02的具体来源差异与已执行反例见[PKG-035 §12](../shared-modules/packages/PKG-035_ProgramPackage.md#program-source-adoption)：原Schema能接受latest、同ID/版本不同hash和重复审批记录，但平台语义仍须拒绝浮动/冲突引用并按正式审批政策验收；这属于内部合同/Validator设计，不是等硬件才能查明的问题。

### 2026-10-28 文档阶段进展（不改变上表任何未决条件）

| 事项 | 结论 | 证据 |
|---|---|---|
| 文档门禁有效性 | 修复 CI 分支过滤（`main`→`master`，此前 push 到默认分支不触发 CI）与 587 项断链误报；新增 `validate_module_guides.py` 与负例测试 | [.github/workflows](../../.github/workflows/)、`tools/validate_module_guides.py` |
| 内容级审查 | 302 份文档完成逐项判定（52 独立模块 + 118 PG/FS/UI-PCS + 132 PKG/公共指导）：**51 份直接 Pass，1 份 Gap 已修**（`ai-dataset-governance` §7.4 数值无来源 → 改为 Profile 引用并新增 §7.4.6 字段契约） | [T2-REVIEW-LEDGER.md](../../T2-REVIEW-LEDGER.md) |
| 单一权威 | 132 份 PKG/公共指导**未发现同义第二套定义**；权威链闭合：PKG/公共指导 → 独立模块指导 → 附录 API Contract | 同上，T6 节 |
| 工程规则审核 | `AGENTS.md` 恢复 14 条被压缩删除的约束，修正架构门禁漏覆盖 141 个核心工程的问题；`PROJECT_ENTRY.md` / `PROJECT_PROGRESS.md` 修正失效事实断言 | [AGENTS-AUDIT-2026-10-28.md](../../AGENTS-AUDIT-2026-10-28.md)、[ENTRY-PROGRESS-AUDIT-2026-10-28.md](../../ENTRY-PROGRESS-AUDIT-2026-10-28.md) |
| 历史产物标注 | `INTEGRATION-CHECKPOINT-73501/73600` 所述实现已随 `c4e10cf` 移除，加状态声明防止被当作当前实现证据 | 两文件头部 |

**上表所有 Gate 状态不变。** 文档阶段收口只说明"指导内容足以让实现者不补做架构决定"，**不关闭**任何实现、运行、性能、计量或现场资格门；D-01～D-04 与 C-01～C-08 仍按上表处理。

## 本轮研究后需要补充的输入

来源覆盖详见[REF-007§4](../references/REF-007_未开发机台竞品研究与设计落点.md#4-本轮覆盖深度与需要补充的资料)。公开产品页/规格表已支持设计方向；完整专机操作手册、实际材料/工装/传感模态、客户标准版本/等级、真值样本及接受数值仍不充分。尤其透明膜厚、孔内质量、V槽残厚和压接接触不能由已有2D/单表面数据替代。

这些缺口只阻断对应功能的契约/生产资格冻结；不阻断当前独立模块与工艺设计。各PG新增§9起的细项是DesignReview，不因文档校验通过变成ImplementationReady。后续实施时按选定功能取得所需输入，不一次要求用户补齐全部机台资料。

## 逐功能实施卡后的精确准入（2026-09-27）

72项当前功能已具专项处理/操作/拟验收，28模块有逐操作接入，26页面有视觉与交互设计要求；状态仍为DesignReview/DocMapped。尚未完成的实现准入必须在原功能处关闭：

| 输入/产物 | 冻结责任边界 | 当前影响 |
|---|---|---|
| 正式Schema、公共端口签名、State/Commit/Disposition Owner | 既有GATE-001及C-01～C-08；[DEV-CONTRACT-002](../13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md) 已把72个功能卡做候选绑定，仍需架构/领域负责人逐切片采纳 | 不能让程序员根据语义卡新造生产DTO/Owner；未批准端口前示例仅为语义调用 |
| 具体HALCON算子参数到AsunImage/ROI公共入口的绑定 | 算法/接入实现切片，查公共文档/签名；不扫描封装内部 | 未核对的接口不能编造；不是AsunImage/DevExpress版本或授权准入 |
| 工艺参考、材料/孔型/胶型、可观测模态、接受值与真值样本 | 对应PG§8及产品/设备/质量输入 | 当前合成示例不冻结客户标准；只阻断依赖该值的功能或资格 |
| 页面专有命令/角色、最终视觉稿及真实WPF样页 | 各PageContract与PG页面增量 | 点胶/涂覆UI-PCS-022/023、插件/THT的UI-PCS-024/025均有专属设计及合成HTML定向检查；终装[UI-PCS-026](../process-guides/guidance/14-page-contracts/UI-PCS-026_Final_Assembly_Workbench.md)已有专属合成HTML交互原型。所有这些页仍需正式端口、完整功能、真实WPF及产品验收 |
| 负载、性能数值、最小分辨率/触屏条件、现场验证 | 对应产品Profile | 当前定义测点/场景，尚未实测达标；视觉候选尺寸不等于设备规格 |

上述未决不撤销四项要求，也不阻断可独立开展的指导细化。继续按已确认研究顺序推进并仅在依赖决定时集中讨论；不因为文档校验通过扩大为“普通程序员已能实现全部生产功能”。

## 内部设计欠账与完成判据（2026-09-27）

用户对全平台完整性提出复核。此前“本轮文档细化完成”只表示那一轮整理/修订结束，不能表示总体详细设计完成。现有72项功能分组和26份页面不是穷尽清单；功能表有链接、字段齐全、校验通过均不能证明内容足以直接实现。以下工作尚未完成，不属于必须等待用户提供资料才能开始的外部门禁。

| 内部工作 | 目前不足 | 必须在原指导内补齐的完成判据 |
|---|---|---|
| 功能全集与变体 | PG功能分组偏粗，子功能/模式/角色/选配和跨工序组合未系统穷举 | 逐制程列出正常/异常/离线/换线/恢复的可验收子功能；每项映射唯一指导，明确不支持或条件支持；不得机械拆文件充数 |
| 跨模块完整逻辑 | 有主链和局部异常，尚无完整的输入/状态/时序/权限/失败组合推演 | 对版本变更、取消、迟到、重启、部分提交、重试、资源耗尽等组合逐条走查；每步输入输出/所有权/回执可确定，矛盾回原权威修订 |
| 每机台快速编程 | DEV-AI-062/FS-068等提供通用生成链，不代表每个PG都有完整方案 | 逐PG定义制造资料齐备、金板/样图、同类程序变体等适用模式；输入核对→对象/库匹配→ROI/算法/参数候选→覆盖→试检→未决项→批准发布；列出人工介入、失败回退和编程时间/干预量衡量方法；不具备编程任务的工作站明确说明 |
| UI与操作优化 | 有页面类型、文字布局和设计Token候选，缺全量页面/弹窗/状态原型及任务验证 | 在既有页面权威中补角色/入口/导航/布局/命令矩阵、正常与错误状态的可评审原型；高频任务的步骤/时间/误操作/恢复对比；后续真实WPF验证，原型不冒充生产页面 |
| AI与学习算法 | 逐任务路线登记已形成，但真实方法/API/数据和资格仍未关闭 | [DEV-AI-064](../shared-modules/guidance/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md) 已逐项登记 72 个功能卡的经典基线、候选路线、数据/标注/划分、拒识、资源和验收证据；[DEV-AI-065](../shared-modules/guidance/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md) 已固定平台级路线门、RT-DETR/PatchCore/OCR 路线边界、ONNX Runtime 三路 EP 选型与三态仲裁语义；仍需按任务完成公共 API、真实样本、训练/评估、部署回退/漂移和质量 Owner 决定。 |
| 性能/智能性/鲁棒性 | 有指标名和通用原则，缺细化的数据搬运/关键路径/资源竞争方案 | 固定负载维度，分解采集/处理/提交/UI/网络预算与资源寿命；比较ROI/分层计算/复制/缓存/并行/GPU策略；把智能性落实为减少输入/定位异常/解释恢复，把鲁棒性落实为具体干扰与拒识矩阵；实测数值仍需目标环境 |
| 开源复用决策 | 已研究少量源码/测试，未形成全功能选型与集成验证 | 逐能力比较现有控件、HALCON/.NET/DevExpress已有能力、直接依赖、适配引入、可复用源码和仅借鉴；固定版本、具体文件/测试、许可证和部署代价，实际试验后判断优劣；AsunImage/DevExpress不重新核验准入或授权 |
| 国际竞品对标 | 公开资料和局部手册支持方向，缺完整任务/指标的可比证据 | 逐机台明确参考产品/配置/资料版本和证据类型；比较覆盖、编程/换线、误报漏报、计量、节拍、人工干预/恢复及维护成本；相同样本与条件下验证前不能宣称达到或超越 |

内部研究/设计可继续按已确认顺序推进。只在真正依赖客户产品范围、工艺接受值、目标硬件和真实样本的地方列外部输入；不能用这些外部门禁解释所有尚未完成的规格。已完成蚀刻光板线路内部、X-Ray/CT、ICT、FCT仍按既定暂缓范围处理。

每个功能收尾必须能从真实来源定位到设计选择、完整操作链、可实现契约、具体样例及验收方法；未完成项如实留在原指导中。软件实现和实机对标尚需独立验证；“无已知设计矛盾”也不是“保证永远完美”。


## 全量开发准备本轮收敛与继续项（2026-09-27）

开发顺序和多会话边界已从旧69项计划修订到当前SM/PG范围，详见DEV-PLAN-001/002/014/015；这是工程计划DesignReview，不是实现开工或生产资格。建议离线钻孔→钢网第二消费者→3D验证的顺序不需要先选定首台客户机型，也不替代D-01决定。无Git元数据只限制实际代码多工作树开工，不限制当前设计。

性能指导补齐具体数据/资源/挂起写入/取消和测量设计；快速编程现已覆盖全部23个PG并补入逐制程方法/数据/性能/UI/组合故障/准入附录。完整UI原型、逐任务AI/开源比较、详细契约/状态仍未完成；D-04真实数值也未关闭。C候选和历史计划错误的可实施状态已撤回，不能由文档校验通过再次提升。

为了减少返工，还需在原对应指导推演以下交叉问题：双面/拼板/层对/载具/卷段身份变化；模型/库/标定撤回对在途任务与旧回放的影响；跨设备时钟漂移和先后顺序；多工位/离线断网后的冲突与数据补传；证据留存/空间不足/备份恢复；跨版本配置和历史结果可读性；大批量批改/撤销/审批/激活边界；多屏/DPI/语言/权限切换；人员复判争用和返修后新尝试；取消/重启/部分提交/未知设备副作用的组合。它们分属SM/PG既有Owner，不另建同义总状态机。

正式接入前确需产品决定的是首机型与传感能力、部署与保存恢复、角色/质量处置、实际接受数值和样本。可自主完成的源码研究、候选比较、接口差异、故障推演和任务设计继续推进；不要求用户现在一次回答全部问题。

最新深化已覆盖全部23个PG的专项快编、AI/数据、性能、页面和组合失败附录，并补UI-PCS-022～026。插针/THT的HTML仅验证部分交互，终装HTML也不关闭页面全部命令、正式应用端口、实际WPF/图像资源与产品资格。共同公式和源码证据是设计输入，尚未完成全平台契约/公共API绑定、全量高保真UI、逐任务模型选型/训练/部署和相同工业样本对标；Goal仍覆盖这些内部工作。

## USER-002独立能力的当前状态

19项建议已映射公共目录并细化无UI核心/可选UI、职责/执行/异常/数值例/候选来源，沿28SM归属；不是全功能正式API或生产资格完成。数据库优先验证PostgreSQL/Npgsql但尚未采纳具体部署/版本；MES以独立互联中心规划，完整MES产品范围未扩大；设备接口/模拟可继续，实际SDK/厂商参数仍暂缓。全码制目录/质量适用表、既有测量控件无UI公开入口、候选实测比较、全部UI/合同/性能数值仍分别需关闭，不因研究源码或结构验证通过而提升资格。

## AOI副本与独立模块重规划的当前边界

用户要求19项仅作为思路输入。旧62个公共包/6类工具宿主是迁移索引；当前完全独立模块架构为52项候选，原51份逐项指导保持设计准备/核心开工门禁，新纳入的IM-068 alarms指导正在首次唯一会话编写。会话登记中的 `accepted` 仅表示文档设计接收，不代表 `ImplementationSpecificationReady`、代码实现或产品验收。每个代码切片仍按 DEV-GOV-010 核实正式契约/Owner、可调用公共 API、参数、代表样本、测试和验收；不要求52项同时关闭，也不能因文档或候选数量增加标Ready。真实阈值、具体传感器/SDK、客户样本/标准件和现场资格只阻断实际依赖它们的切片。

多FOV专项已把原概要落实为[029 §8–15](../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#mosaic-implementation)及钢网/AOI接入；后续[§11.3–11.8具名多带方法](../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#mosaic-multiband-method)已补合法标签/支持归一/相位/分量/来源，原分量总工作遗漏经独立复核在文档层关闭。该项不再笼统记作“完全没有算法步骤”。剩余内部工作是正式公开合同/源贡献表示、实际HALCON等价适配及缓冲实现方案、未覆盖的alpha/其它seam变体和完整UI任务；真实保真、峰值/吞吐及工艺资格按对应Profile/样本验收。图像数学与预算位置计数不证明生产通过；方法和接收详见[REF002](../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#mosaic-multiband-source-research)。

二维匹配已补[023 §7–14](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-implementation)、022边界、原C/计划§26与钢网/AOI/FPC消费；[scaled/aniso/planar/local方法](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-variants-method)已有具名训练/搜索/坐标/支持/资格步骤，活动字节接收按[当前进度](../../PROJECT_PROGRESS.md)记录。后续[LF-PL-AC-1方法](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-local-topology-method)已补全域闭片交集、同拓扑逆与完整ROI切片，并回接007/020/FPC/钢网及原C/计划，九文件独立限定接收。[024固定片精确数值](../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection%20Target%20Selection开发指导.md#roi-local-exact-numerics)及020/023/C消费已独立限定接收，.NET公共算术基础不再待选；位长、固定调度、同片逆与舍入边界已有方法，仍不覆盖递归有理布尔或真实资源/物理误差。剩余内部工作包括精确公共接口/资产表示、实际矩阵与local非零原点/扩边栅格适配、上述数值方法/有界索引与精确切片的实际接入、可选点/大候选关联优化、目标不确定度生产者及完整UI。UI002原跨样本/当前帧混淆P2经[退修独立复测](../../.work/vision-matching-ui-rework-independent-20260929/review.md)在固定HTML及023/C职责范围内关闭：历史报告不排本帧歧义，缺失/过期/异源/拟合复用和仍双解均阻断。该接收不关闭真实模型/观测、任意输入/多Mark、持久化或WPF，原失败保留。不能把已有方法步骤当上述实现资格已完成，也不能将它们全部列为等待用户。缺高级local资格仅阻相关用途，普通方法和原图链继续；自由度/阈值、真实精度/性能及同样本竞品验证仍由适用Profile/样本给依据。

OCR的[021A §15](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-decoding-association-method)、独立024包及PCB字符/AOI标记消费者已完成本批方法接收，具体版本与证据见[§0.67](../../PROJECT_PROGRESS.md#exact-numerics-ocr-method-reception-20260929)。三模式/基数、显式batch身份、具名CTC/分数和原读/mapping已有步骤；[§16外部几何/支持及有限分块方法](../shared-modules/guidance/03-vision/DEV-VIS-021A_OCR与DeepOCR独立能力开发指导.md#ocr-external-geometry-tiling-method)与PG006/057B/062/C/计划及FS061已独立限定接收（[§0.69](../../PROJECT_PROGRESS.md#ocr-geometry-consumer-reception-20260929)），包括一次恢复外围关系和已知完整单词直接识读旁路；实际ε/Δ、halo、支持/模型资格及未支持布局仍不能由方法例补证，原串Unicode/编辑距离及完整分母已写入[063 §14](../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md#ocr-text-evaluation-method)且独立限定接收；训练/checkpoint/导出方法见下段。剩余实际实现/后端Golden不能全部列为等客户。实际ImageLibDotNet绑定、后端输出/坐标/语言Golden、正式合同、真实数据/校准门、资源取消和WPF/工业资格尚未关闭。HALCON Deep OCR优先，Paddle仍须同样本比较后受控决定接入，有限方法例不证明识别效果。

同一OCR可选控件的[两宿主连续任务/HTML](../shared-modules/guidance/14-page-contracts/UI-PCS-002_Vision_Workspace.md#ocr-interactive-workflow)已独立限定接收（[§0.70](../../PROJECT_PROGRESS.md#ocr-ui-reception-code-study-20260929)），保留真实WPF/权限/保存和任意输入未验范围。条码[021B方法](../shared-modules/guidance/03-vision/DEV-VIS-021B_条码解码与印制质量独立能力开发指导.md#code-reading-evidence-method)/023及PG001/015/022、037/FS001、C/计划已独立限定接收（[§0.71](../../PROJECT_PROGRESS.md#code-reading-consumer-reception-20260929)），原数据层、typed质量、来源闭合与重采/重算边界已有步骤。GS1[037 §9内容方法](../shared-modules/packages/PKG-037_Identity.md#gs1-content-parsing-method)及PG001/PG022、FS001/C/计划已独立限定接收（[§0.72](../../PROJECT_PROGRESS.md#gs1-content-consumer-reception-20260929)）；入口/字段/词典回退/来源映射已有步骤，生产依赖、词典部署、格式政策与业务映射仍待原权威采纳，实际native/.NET/扫码尚未验证。双宿主条码UI作者已交回，独立自然复测受浏览器认证及替代自动化规则限制，独立静态审核已交回且标题P3已作最小静态修正，动态未验、未接收；实际公共封送、原生返回/取消、真实码图/标准件、持久身份绑定与WPF/性能未验证，不据文档宣称标准认证或完整身份链已实现。它们是内部准备工作，不全部等待客户。


[026 §16良品变化方法](../shared-modules/guidance/03-vision/DEV-VIS-026_2D分割、Blob与缺陷候选开发指导.md#variation-inspection-method)及PG006/PG022、033/063、C/计划已独立限定接收（[§0.73](../../PROJECT_PROGRESS.md#variation-inspection-consumer-reception-20260929)）。训练模式、阈值/两方向、D/I与完整R、污染/分组、运行/重建/证据闭包、同封存核心fresh读回及分块条件已有具体方法。正式公共绑定、native统计/类型与边界Golden、真实取消/保存/资源、两宿主控件/WPF及材料/缺陷同条件资格仍欠；不把文件可读或无差异当模型/产品通过。边缘及语言方法的后续状态见下一段；已采纳方法不自动成为全部DevExpress区域已实现。这些内部准备继续推进，不以缺客户阈值笼统阻断。

[025 §7有向提边与拟合方法](../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md#edges2d-association-method)及钻孔/钢网、030/FS039、C/计划已独立限定接收（[§0.74](../../PROJECT_PROGRESS.md#edges2d-consumer-reception-20260929)）。measure_pairs单边证据P2在活动修正文档层关闭；预登记诊断、完整profile、原采样/物理拟合/Metrology限制及固定图先后已有具体方法。公开适配/实际坐标world与scale、端点误差和完整支持、真实取消/资源、WPF与工艺精度/性能仍分别未验；未知原索引只限制依赖用途，不伪造slot或笼统阻断全部提边。独立语言方法的后续接收见下一段；公开UI入口仍逐项研究。

语言能力的唯一当前实施指导为 [IM-003 localization](../independent-modules/localization/DEVELOPMENT-GUIDE.md) §3–5/§7–13；PKG-003、SM-003 和 [040 §13](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md#localization-scope-method>)仅作责任/应用映射。独立资源格式、显式 fallback、typed format、快照、请求/呈现/排空已冻结，不再以旧 D1–D5 候选阻断全部 Core。供应商逐 ID 槽位/调用文化与原生窗口公开入口仍是相应 WPF 适配的设计门；真实 WPF、字体、IME、三语/UIA/DPI 和性能另行验收。产品 Schema、客户词条审批、发行信任、报告存储政策及消费者 Profile 只阻对应产品用途。逐切片接收以模块指导为准；历史文档接收不构成实现或生产证据。

[028参考面P/H/Q](../shared-modules/guidance/03-vision/DEV-VIS-028_3D对象模型、配准与表面分析开发指导.md#reference-surface-method)、029、[031有限signed积分](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#quadratic-reference-signed-integral)、030及SPI/点胶/FS/C/计划已独立限定接收（[§0.77](../../PROJECT_PROGRESS.md#reference-surface-method-reception-20260929)）；倾斜方向/面积P2在活动文档层关闭。[031有界归约](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#quadratic-reference-bounded-reduction)的固定合格三角域正负量、连续面积CDF/同域分位、二阶端点及预算/舍入/取消方法，现由[IM-036 metrology](../independent-modules/metrology/DEVELOPMENT-GUIDE.md)唯一指导维护。具体模块切片接收以当前指导和[进度§1.07](../../PROJECT_PROGRESS.md)为准；公共桥/native运行、数值与实际资源/性能、物理误差和材料用途、WPF及现场资格按受影响范围验收，不凭早期方法接收或过期暂停记录判断当前状态。当前 Goal active，沿永久模块会话继续完善内部可决定规格；未决保留不代表全平台已完成。

训练恢复与导出已补[060 §12](../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md#ai-training-export-method)/053及[开发顺序](../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md#training-text-evaluation-development-slices)，独立接收见[§0.68](../../PROJECT_PROGRESS.md#training-text-evaluation-reception-20260929)。完整安全边界、状态缺项、best与最终测试、导出语义翻转及数据用途已有具体方法。尚欠所选后端的全部必要状态公开保存/读取绑定、实际中断对照、完整保持/取消、模型/转换支持与源/派生真实Golden、工程UI和资源验收；不从seed、epoch或文件可读推exact恢复，不从小tensor误差推用途等价。实际训练数据、定位/分数资格、产品接受值与现场条件仍按对应Owner提供，不阻非依赖的拒绝/完整性流程设计。

模型资产实施唯一见[IM-014](../independent-modules/model-assets/DEVELOPMENT-GUIDE.md)，[033](../shared-modules/packages/PKG-033_ModelAssets.md#model-assets-implementation)保留应用映射；模型/OCR/AI、UI002和计划014§27消费同一指导。新资产RFC8785 `model-core-jcs-v1`的技术投影、数字移植闭包、集合/顺序、路径与预算已在§4/9/附录A冻结，旧资产按创建时规则校验；请求投影、Service factory/端口/资源与撤回规格见§5A–8A/附录B。PureCore及S1服务六项文档规格已由主控接收为ModuleCoreImplementationReady，U1装配恢复与SD限定注册桥指导内容已接收；具体范围以唯一指导为准。后续门是正式平台字段/Owner与真实Store/Authority/Sink映射、实际旧verifier/生产者格式schema/参数集、安全物化/耐久恢复、真实HALCON读回/Golden/性能、WPF1920×1080和现场资格。用途阈值、独立挑战、部署与在途政策依原Owner接收；模块规格接收不代替运行证据，能加载或保存不等于用途批准或生产采用。AsunImage/DevExpress依赖核验仍排除。

受控推理模块实施唯一见[IM-047](../independent-modules/ai-inference/DEVELOPMENT-GUIDE.md)，[052](../shared-modules/packages/PKG-052_Inference.md#inference-execution)及060、AOI/涂覆、UI014与计划014§28维护产品接入。Core/Simulator六项文档规格已接收；HALCON Adapter、原模型/帧Owner桥、公开装配与有限恢复的确定指导内容已限定接收。首版每请求加载模型，无模型或结果缓存、无跨请求组批，038负责应用外层预算；不得恢复历史缓存/组批候选为默认实现。模块公开API、权限披露、具名多输入输出、HALCON标准键及预后处理路线按唯一指导实施。真实模型/输入交接、目标运行能力、Adapter消费编译、后端数值/并发/资源、Golden/性能、真实WPF及产品/现场资格仍按受影响切片验收；各PG模型训练/选型属于对应应用与原模型Owner。模型/数据/工艺阈值、目标硬件资源和必需AI处置政策按受影响用途采纳；ORT/Triton是研究而非已选依赖。当前架构为52项独立模块，旧PKG仅作应用迁移映射。AsunImage/DevExpress核验不在待办。
