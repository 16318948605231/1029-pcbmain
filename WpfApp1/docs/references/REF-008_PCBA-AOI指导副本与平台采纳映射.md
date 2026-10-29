# PCBA AOI开发指导副本、逐份采纳与复核入口

- 文档 ID：`REF-008`；版本：`0.1.0`；日期：2026-09-27；状态：`ResearchMapping`

## 2026-10-06 H:\docs 全量来源目录与审阅状态

用户后来提供了正在研发的 PCBA 2D/3D AOI 文档树 `H:\docs`。133 个文件（132 份 Markdown 和 1 个备份 intake）已逐项记录原相对路径、字节数、SHA-256、初步分类和候选模块；全量入口见 [H:\docs 来源清单与分类说明](project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/README.md)，逐文件机器可读记录见 [source-manifest.json](project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)。清单建立后重新读取 H 盘原件，133/133 均存在且 SHA-256 一致。

本清单仍是来源目录，不是 133 份全文审查或采纳结论。本轮对 35 个当前未审/旧快照过期的模块候选来源完成了职责范围定向比较，涉及 30 个已登记模块；全部在登记的原会话完成，没有新建重复会话。29 份唯一指导有针对性修订，`viewport` 经核对已有适用内容且其余来源超出职责，因此未改指导。逐文件的模块结论、采纳/排除边界及唯一指导路径见 manifest 的 `semanticReviewNote` 和对应指导；这不表示来源全文已审。当前状态：78 项尚未语义复核，16 项沿用旧快照的有限复核，0 项旧快照过期，39 项为定向部分复核（本轮 35 项加既有 4 项）。这 78 项均无独立模块候选映射；当前所有候选模块来源至少已完成对应职责范围的有限/定向比较。

与 2026-09-27 来源清单按相对路径/hash 比较，128 项路径匹配中 68 项哈希一致、60 项不同，另有 5 项路径未匹配；旧清单来源根为 `F:\PCBA AOI`，因此此差异只描述文件对应关系，不推断两棵来源树完全相同。H 盘文档使用 HALCON 24.11；本平台使用 AsunImage / HALCON 26.05，任何算子与 API 结论均须以目标版本依据核验。模块后续复核和修订只能在 [模块索引](../independent-modules/MODULE-INDEX.md) 登记的永久原会话进行，不得新建重复或临时会话。

## 2026-10-04 外部项目增量复核入口

本轮新增的只读来源是用户提供的 PCBA 2D/3D AOI 指导和 AOI.Main PCB 光板检测指导；原项目不在本平台修改。选定文件及 SHA-256 清单分别见 [PCBA-AOI 2026-10-04 快照](project-snapshots/PCBA-AOI/20261004/README.md)、[AOI.Main 2026-10-04 快照](project-snapshots/AOI-Main/20261004/README.md) 和 [AsunControl 公共边界快照](project-snapshots/AsunControl/20261004/README.md)。AsunControl 只用于核对历史 `ImageLibDotNet` 公共面；平台运行基线仍是项目根目录 `AsunImage`、HALCON 26.05，不能把旧版本源码、WinForms/.NET 版本、默认参数或私有状态迁入契约。

本次已将可复用的工程事实回写到唯一独立模块指导：

| 来源 | 独立模块落点 | 采纳边界 |
|---|---|---|
| PCBA-AOI：性能/资源/坐标、2D/3D、模板/Mark、读码、OCR、视图/证据、回放、参数试验台 | `image-frame`、`viewport`、`camera-acquisition`、`roi-geometry`、`alignment-2d`、`model-assets`、`barcode`、`ocr`、`reconstruction-3d`、`registration-3d`、`surface-features-3d`、`reference-surface`、`metrology`、`inspection-evidence`、`replay`、`parameter-editor` | 只采纳稳定输入/输出、资源租约、训练/读回、有限备用、失败恢复和验收方法；产品编排、板件身份、质量放行、客户阈值和源项目“已完成”声明不采纳 |
| AOI.Main：原图/序列浏览、影像窗口交互、参数生产集成、线路/焊盘/孔检测闭环 | `image-frame`、`viewport`、`camera-acquisition`、`parameter-editor`、`measurement-workbench`、`metrology`、`features-2d`、`inspection-evidence` | 只采纳不可变原图、像素/序列身份、容量预检、草稿/发布隔离、证据谱系和检测器边界；旧 WinForms/.NET 版本、客户制程和默认值不采纳 |
| AsunControl：ROI、匹配、读码、标定、3D/结构光、变化模型公共源码 | `roi-geometry`、`alignment-2d`、`barcode`、`ocr`、`calibration-assets`、`structured-light`、`reconstruction-3d`、`surface-features-3d`、`variation-inspection` | 仅核对可见公共成员、资源释放和算法路线候选；具体签名、线程、取消、版本和性能必须以本机 AsunImage 26.05 公共程序集及实现测试重新确认 |

本节是来源与平台唯一指导的映射记录，不构成实现、编译、HALCON/WPF、性能、HIL、Golden 或生产资格通过；未采纳内容保留在只读快照中，不建立第二套活动指导。

## HALCON 版本隔离 — 2026-10-06

版本边界补充：用户明确 H:\docs 中引用的 HALCON 技术基线为 **24.11**；它在本平台只作为历史来源、场景和待查问题。本项目使用 AsunImage / HALCON **26.05**。源文档里的算子选择、参数默认值/范围、返回语义、线程/资源行为及 `ImageLibDotNet` 调用形状，只有经本地 [`halcon算子手册/operators`](../../halcon算子手册/operators/) 中对应的 26.05 页面与目标公共签名逐项复核后，才能成为本项目指导依据；不得按同名算子推定跨版本相同。

本次复核的来源分别按实际归档位置记录，不能把一份清单当作本轮所有来源的总表：标定和拼接两份原件见 [2026-10-06 标定/拼接清单](project-snapshots/PCBA-AOI/20261006/source-manifest.json)；新版光源指导见[光源来源快照及清单](project-snapshots/PCBA-AOI/20261006/acquisition-lighting-control/README.md)；条码、OCR/OCV、Mark 三份来源与既有 [2026-10-04 快照](project-snapshots/PCBA-AOI/20261004/README.md)中的对应文件逐字节相同，因此只保留一份副本，其来源路径、字节数和 SHA-256 仍由 2026-10-04 清单记录。本项目冻结使用 AsunImage / HALCON **26.05**。来源指导中的 HALCON 24.11/24.11.1 和 AsunImage 24.11 断言只用于发现应用场景、失效条件和待验证问题；算子选择、参数默认值/范围、返回语义、线程/资源行为及 `ImageLibDotNet` 调用形状均不能直接提升为本项目事实，必须按本地 [`halcon算子手册/operators`](../../halcon算子手册/operators/) 的 26.05 页面及公共签名分别复核。条码唯一指导已据 26.05 页面明确区分 1D 原始解码 byte tuple 与 2D 码字、纠错码字、解码字符层，禁止把 2D `raw_coded_data`/`corr_coded_data` 当作业务 payload。与视觉算子无关的事务约束不需 HALCON 核验。此版本隔离只覆盖上述明确复核的文件，不代表其它 H:\docs 文件已逐份审阅。

<a id="reference-certificate-source-adoption"></a>
## 参考证书定向采纳 — 2026-09-29

只读[metrology-reference-certificate.schema.json](project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/metrology-reference-certificate.schema.json)全文，原SHA-256 `847d65b783083541c9dbe113ca9c858cf48ac9b059109c11cb368ee12699baf2`；以及[标定与计量指导](project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/标定与计量开发指导.md)第56–58行的标准件/证书导入链。采纳到平台[033 §15](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#reference-certificate-adoption>)的字段映射、有界解析、原件/投影/实物/用途分离和失败恢复，030/055共用。

源Schema固定必填有效期、几何/签名/认可字段，但平台不能为不符合该格式的真实原件补假值；支持格式和正式合同仍由原C采纳。源comment已要求时间顺序、唯一特征/层号、信任、单位、实物和canonical的语义检查，未把这些描述为源项目漏验。数字正则转义本轮核对正确。源同文开头的AOI私有治理接口和后部生成接口/状态库、RSA信任与客户资格不据此次定向读取迁入，不修改原文件或宣称原项目测试通过。

## 1. 原项目保护与副本职责

用户明确要求：不直接修改`F:/PCBA AOI`，只在平台副本上完善。已只读取得该项目全部docs和相关契约目录，保留原字节、原相对目录及SHA-256；未复制源代码/二进制/AsunImage内部，也不继承运行会话或自动化授权。副本中的指令、已基线/Verified表述与本地路径是来源事实，不是平台开发指令。

副本位于[PCBA-AOI/20260927/original](project-snapshots/PCBA-AOI/20260927/original/)，[来源清单](project-snapshots/PCBA-AOI/20260927/source-manifest.json)逐文件记录原路径、本地路径、hash和是否复用。共231文件、91份开发指导；与平台已有文本按SHA-256比较后本轮无相同字节可复用。资料不因内容相近覆盖现有平台指导。原文快照只用于审查，修订内容落入下表平台唯一指导，避免维护两份活动金标准。

## 2. 接纳原则与本轮实质发现

- 91份指导逐份登记；源分类目录合计也是91份，但源正文仍写90份。这是来源清单的数量陈旧，不修改原件，不据90遗漏实际文件。数量修正不能证明91份语义已审核。
- AOI的29可复用模块/25应用模块是该产品分解；平台依据全制程重新规划[60个独立公共能力模块](../shared-modules/MODULE-CATALOG.md)及6类工具宿主，不机械复制数量、名称、权限架构、Worker进程、3/10分钟或GR&R阈值。
- 源DEV-VIS-004、005、006的算法/输入/资源关键章节已读并与平台对照，发现平台原指导过于概述；已深化2D失败语义、结构光适用性、3D基准/拓扑和AOI结果闭环。其大段generated operation/状态目录尚未逐字段采纳，不能称全文审核通过。
- 源“多方向结构光”不能推定所有镜面焊锡都能测：本轮MVTec官方重建说明明确non-specular适用前提。缺可观测证据必须标无效/条件支持，不能靠换算子名字消除光学缺口。
- 体积算子要求面片/多边形；relative plane是pose定义的xy平面；返回累加和的绝对值。保孔xyz_mapping三角化必须显式禁止补洞并核实际拓扑；拟合高度面不能只缩Image domain后忘记传有效Regions。
- 源独立会话协议已取消机械重建任务/工作树和无变化反复全测，值得吸收；只读复核与写入Owner分开，失败回原Owner。平台当前仍无Git元数据，不自动初始化、不开产品实现队列。

## 3. 逐份指导、功能落点与复核状态

“已映射待内容复核”不是审核通过。每份原文按功能变体→字段/Owner→算法/异常→UI/性能→消费者反向走查；在平台指导内修订后，更新此行的精确章节/残留问题。不得批量把复制状态改成Ready。

| 来源ID | 原文副本 | 来源分类 | 平台唯一完善位置 | 本轮状态 |
|---|---|---|---|---|
| `DEV-PLT-001` | [AsunVisionPlatform架构与模块目录](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/AsunVisionPlatform架构与模块目录.md>) | CrossCuttingStandard | [SM-001](<../shared-modules/modules/SM-001_composition.md>) | 已映射待内容复核 |
| `DEV-ARC-007` | [共享内存单消费者租约协议开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/共享内存单消费者租约协议开发指导.md>) | CrossCuttingStandard | [SM-006](<../shared-modules/modules/SM-006_frames.md>) | 已读全文；SPSC范围限制见§8，未采纳平台IPC |
| `DEV-ARC-001` | [功能模块分解与依赖矩阵](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/功能模块分解与依赖矩阵.md>) | CrossCuttingStandard | [DEV-PLAN-014](<../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md>) | 已映射待内容复核 |
| `DEV-PLT-002` | [可复用模块独立性与UI分离标准](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/可复用模块独立性与UI分离标准.md>) | CrossCuttingStandard | [DEV-GOV-005](<../01-governance/DEV-GOV-005_模块独立性与复用标准.md>) | 已映射待内容复核 |
| `DEV-OPS-001` | [可观测性与诊断开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/可观测性与诊断开发指导.md>) | ReusableModule | [SM-005](<../shared-modules/modules/SM-005_diagnostics.md>) | 已映射待内容复核 |
| `DEV-STD-003` | [坐标系统与数值黄金样例开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/坐标系统与数值黄金样例开发指导.md>) | CrossCuttingStandard | [SM-008](<../shared-modules/modules/SM-008_coordinates.md>) | 已读正文；坐标约定差异见§8，35源golden未执行 |
| `DEV-SEC-001` | [安全权限与审计开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/安全权限与审计开发指导.md>) | CrossCuttingStandard | [SM-004](<../shared-modules/modules/SM-004_authorization.md>) | 已映射待内容复核 |
| `DEV-SEC-002` | [工业网络安全与合规开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/工业网络安全与合规开发指导.md>) | CrossCuttingStandard | [DEV-PLT-016](<../shared-modules/guidance/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md>) | 已映射待内容复核 |
| `DEV-STD-007` | [应用功能模块全景与跨模块接口执行基线](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/应用功能模块全景与跨模块接口执行基线.md>) | CrossCuttingStandard | [DEV-PLAN-014](<../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md>) | 模块/分类总表已对照；语义catalog尚未全部采纳 |
| `DEV-STD-001` | [开发指导文档统一模板](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/开发指导文档统一模板.md>) | CrossCuttingStandard | [DEV-GOV-010](<../01-governance/DEV-GOV-010_实施级规格唯一标准.md>) | 已映射待内容复核 |
| `DEV-PERF-001` | [性能预算与并发流水线开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/性能预算与并发流水线开发指导.md>) | CrossCuttingStandard | [DEV-PLT-014](<../shared-modules/guidance/02-platform/DEV-PLT-014_性能预算与并发流水线开发指导.md>) | 已映射待内容复核 |
| `DEV-EXT-001` | [插件SDK与第三方扩展兼容开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/插件SDK与第三方扩展兼容开发指导.md>) | CrossCuttingStandard | [DEV-PLT-017](<../shared-modules/guidance/02-platform/DEV-PLT-017_插件SDK与扩展点开发指导.md>) | 已映射待内容复核 |
| `DEV-LOC-001` | [本地化与专业用户文案开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/本地化与专业用户文案开发指导.md>) | CrossCuttingStandard | [SM-003](<../shared-modules/modules/SM-003_localization.md>) | 已映射待内容复核 |
| `DEV-ARC-005` | [权威状态角色消息与判定所有权规范](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/权威状态角色消息与判定所有权规范.md>) | CrossCuttingStandard | [DEV-GOV-002](<../01-governance/DEV-GOV-002_文档权威与变更控制.md>) | 已映射待内容复核 |
| `DEV-ARC-002` | [核心数据契约与版本治理开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/核心数据契约与版本治理开发指导.md>) | CrossCuttingStandard | [DEV-GOV-004](<../01-governance/DEV-GOV-004_Contract_Schema_Validator开发标准.md>) | 已映射待内容复核 |
| `DEV-STD-006` | [模块功能语义与跨模块接口闭环审查基线](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/模块功能语义与跨模块接口闭环审查基线.md>) | CrossCuttingStandard | [DEV-GOV-005](<../01-governance/DEV-GOV-005_模块独立性与复用标准.md>) | 已映射待内容复核 |
| `DEV-STD-005` | [模块开发波次关键路径与集成节奏执行计划](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/模块开发波次关键路径与集成节奏执行计划.md>) | CrossCuttingStandard | [DEV-PLAN-001](<../09-development-plan/DEV-PLAN-001_研发实施步骤与并行开发计划.md>) | 已映射待内容复核 |
| `DEV-ARC-004` | [模块接口总表与契约清单](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/模块接口总表与契约清单.md>) | CrossCuttingStandard | [DEV-GOV-004](<../01-governance/DEV-GOV-004_Contract_Schema_Validator开发标准.md>) | 已映射待内容复核 |
| `DEV-STD-004` | [独立模块并行开发与会话交付协议](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/独立模块并行开发与会话交付协议.md>) | CrossCuttingStandard | [DEV-PLAN-002](<../09-development-plan/DEV-PLAN-002_功能与模块并行度矩阵.md>) | 会话/隔离/恢复条款已对照；AOI任务身份不继承 |
| `DEV-STD-008` | [真实交付路径与客户场景覆盖审查基线](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/真实交付路径与客户场景覆盖审查基线.md>) | CrossCuttingStandard | [DEV-GOV-008](<../01-governance/DEV-GOV-008_质量门禁与Acceptance标准.md>) | 已映射待内容复核 |
| `DEV-STD-002` | [资源生命周期与泄漏防护开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/资源生命周期与泄漏防护开发指导.md>) | CrossCuttingStandard | [SM-006](<../shared-modules/modules/SM-006_frames.md>) | 已映射待内容复核 |
| `DEV-ARC-003` | [进程通信与错误模型开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/进程通信与错误模型开发指导.md>) | CrossCuttingStandard | [DEV-PLT-013](<../shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md>) | 已映射待内容复核 |
| `DEV-STD-009` | [逐功能链路闭环审计与证据维护标准](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/逐功能链路闭环审计与证据维护标准.md>) | CrossCuttingStandard | [DEV-GOV-011](<../01-governance/DEV-GOV-011_质疑式反向审计与无已知缺口标准.md>) | 已映射待内容复核 |
| `DEV-UI-001` | [HMI壳与任务导航开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/10-ui/HMI壳与任务导航开发指导.md>) | ApplicationModule | [SM-001](<../shared-modules/modules/SM-001_composition.md>)、[DEV-UI-041](<../shared-modules/guidance/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md>) | 已映射待内容复核 |
| `DEV-UI-002` | [UI设计系统与高级控件开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/10-ui/UI设计系统与高级控件开发指导.md>) | ApplicationModule | [DEV-UI-040](<../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>) | 已映射待内容复核 |
| `DEV-UI-005` | [全页面PageContract与高保真交互规格](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/10-ui/全页面PageContract与高保真交互规格.md>) | ApplicationModule | [DEV-UI-041](<../shared-modules/guidance/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md>) | 已映射待内容复核 |
| `DEV-UI-004` | [生产驾驶舱与异常恢复开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/10-ui/生产驾驶舱与异常恢复开发指导.md>) | ApplicationModule | [DEV-UI-045](<../shared-modules/guidance/05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md>) | 已映射待内容复核 |
| `DEV-UI-003` | [统一板观察器与2D_3D视图开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/10-ui/统一板观察器与2D_3D视图开发指导.md>) | ApplicationModule | [DEV-UI-042](<../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md>) | 已映射待内容复核 |
| `DEV-NPI-002` | [BoardDataAdapter开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/20-product/BoardDataAdapter开发指导.md>) | ApplicationModule | [SM-014](<../shared-modules/modules/SM-014_manufacturing-input.md>)、[DEV-DOM-057A](<../process-guides/guidance/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md>) | 已映射待内容复核 |
| `DEV-NPI-001` | [NPI三分钟快速编程开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/20-product/NPI三分钟快速编程开发指导.md>) | ApplicationModule | [DEV-AI-062](<../shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md>) | 已映射待内容复核 |
| `DEV-LIB-001` | [元件封装检测库开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/20-product/元件封装检测库开发指导.md>) | ApplicationModule | [SM-015](<../shared-modules/modules/SM-015_reference-library.md>) | 主体及H11组合/真实来源段定向复核，见[范围与采纳](#library-adoption)；其余扩展待审 |
| `DEV-NPI-003` | [离线编程站与配方协作开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/20-product/离线编程站与配方协作开发指导.md>) | CrossCuttingStandard | [SM-016](<../shared-modules/modules/SM-016_program-package.md>)、[DEV-UI-043](<../shared-modules/guidance/05-ui/DEV-UI-043_Program/Recipe编程工作台开发指导.md>) | 主体关键链已复核；完整接口/扩展未全审，见本页runtime-adoption |
| `DEV-REC-001` | [配方版本审批发布开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/20-product/配方版本审批发布开发指导.md>) | ApplicationModule | [SM-016](<../shared-modules/modules/SM-016_program-package.md>) | 主体关键链已复核；完整接口/扩展未全审，见本页runtime-adoption |
| `DEV-RUN-002` | [实体板流复判处置与重检闭环开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/30-runtime/实体板流复判处置与重检闭环开发指导.md>) | ApplicationModule | [PG-023](<../process-guides/processes/PG-023_review-rework.md>)、[DEV-DOM-057D](<../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md>) | 复判/实体链主体已复核；生成接口未全审，见review-adoption |
| `DEV-RUN-001` | [板级编排状态机开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/30-runtime/板级编排状态机开发指导.md>) | ApplicationModule | [DEV-PLT-010](<../shared-modules/guidance/02-platform/DEV-PLT-010_BoardIdentity与BoardRun开发指导.md>)、[DEV-PLT-011](<../shared-modules/guidance/02-platform/DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md>) | 主体关键链已复核；完整接口/扩展未全审，见本页runtime-adoption |
| `DEV-VIS-004` | [2D检测器开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/2D检测器开发指导.md>) | ApplicationModule | [DEV-DOM-057B](<../process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md>)、[DEV-DOM-057C](<../process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md>) | 关键章节复核；2D语义已深化，generated合同待逐字段接纳 |
| `DEV-VIS-006` | [3D检测与量测开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/3D检测与量测开发指导.md>) | ApplicationModule | [DEV-DOM-057C](<../process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md>)、[DEV-MET-031](<../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md>) | 关键章节复核；基准/体积/域限制已补，量测族逐项继续 |
| `DEV-VIS-005` | [3D重建开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/3D重建开发指导.md>) | ApplicationModule | [DEV-VIS-027](<../shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md>) | 关键章节复核；结构光官方限制已补，合同/设备待细化 |
| `DEV-VIS-000` | [AsunImage项目引用与兼容性审计](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/AsunImage项目引用与兼容性审计.md>) | CompatibilityOrSelectionEvidence | [DEV-VIS-020](<../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>) | 已映射待内容复核 |
| `DEV-VIS-008` | [HALCON多候选选择证据开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/HALCON多候选选择证据开发指导.md>) | CompatibilityOrSelectionEvidence | [DEV-VIS-021](<../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md>)、[DEV-VIS-022A](<../shared-modules/guidance/03-vision/DEV-VIS-022A_HALCON版本验证与算法Benchmark开发指导.md>) | 已映射待内容复核 |
| `DEV-VIS-007` | [ImageLibBindingCatalog与类型化封装开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/ImageLibBindingCatalog与类型化封装开发指导.md>) | CompatibilityOrSelectionEvidence | [DEV-VIS-020](<../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>) | 已映射待内容复核 |
| `DEV-VIS-001` | [VisionHost_CSharp_ImageLibDotNet开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/VisionHost_CSharp_ImageLibDotNet开发指导.md>) | ApplicationModule | [SM-018](<../shared-modules/modules/SM-018_execution.md>)、[DEV-PLT-016](<../shared-modules/guidance/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md>) | 已映射待内容复核 |
| `DEV-VIS-003` | [标定与计量开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/标定与计量开发指导.md>) | ApplicationModule | [DEV-MET-030](<../shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md>)、[DEV-MET-033](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md>) | 已映射待内容复核 |
| `DEV-VIS-002` | [采集计划_FOV_路径调度开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/采集计划_FOV_路径调度开发指导.md>) | ApplicationModule | [DEV-MET-034](<../shared-modules/guidance/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md>) | 主体/规划及编辑恢复段定向复核，见[实际范围](#coverage-planning-adoption)；生成接口等未全审 |
| `DEV-PLT-FND-002` | [ROI几何与通用参数模型开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/01-foundation/ROI几何与通用参数模型开发指导.md>) | ReusableModule | [SM-010](<../shared-modules/modules/SM-010_roi-measurement.md>)、[DEV-VIS-024](<../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md>) | 已读§1–9及V2关键部分；生成接口未全审，采纳见§9 |
| `DEV-PLT-FND-001` | [视觉基础类型_坐标与资源租约开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/01-foundation/视觉基础类型_坐标与资源租约开发指导.md>) | ReusableModule | [SM-006](<../shared-modules/modules/SM-006_frames.md>)、[SM-008](<../shared-modules/modules/SM-008_coordinates.md>) | 已核§1–18；生成接口未全审，采纳范围见§8 |
| `DEV-PLT-FND-003` | [通用计量引擎开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/01-foundation/通用计量引擎开发指导.md>) | ReusableModule | [DEV-MET-031](<../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md>) | 已映射待内容复核 |
| `DEV-PLT-FND-004` | [高度图点云与3D基础开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/01-foundation/高度图点云与3D基础开发指导.md>) | ReusableModule | [SM-012](<../shared-modules/modules/SM-012_surface.md>) | §1–18及H11派生补充已读；平台数据/处理采纳见下文；生成接口等未全审 |
| `DEV-PLT-ACQ-006` | [FOV覆盖与路径规划开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/FOV覆盖与路径规划开发指导.md>) | ReusableModule | [SM-013](<../shared-modules/modules/SM-013_coverage.md>) | 主体/规划及编辑恢复段定向复核，见[实际范围](#coverage-planning-adoption)；生成接口等未全审 |
| `DEV-PLT-ACQ-002` | [光源控制抽象与照明配方开发指导](<project-snapshots/PCBA-AOI/20261006/acquisition-lighting-control/original/docs/40-development/41-vision-platform/02-acquisition/光源控制抽象与照明配方开发指导.md>) | ReusableModule | [lighting-control](<../independent-modules/lighting-control/DEVELOPMENT-GUIDE.md>)、[DEV-PLT-015](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) | 仅采纳步骤照明组合复制/粘贴的场景和验收约束；其它来源内容未据此提升为平台规范 |
| `DEV-PLT-ACQ-005` | [曝光光源自动优化开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/曝光光源自动优化开发指导.md>) | ReusableModule | [DEV-AI-062](<../shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md>)、[DEV-PLT-015](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) | §1–6.1及§7–18指定内容定向复核，见[范围](#imaging-optimization-adoption)；非全文/源实现审核 |
| `DEV-PLT-ACQ-001` | [相机采集抽象与诊断开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/相机采集抽象与诊断开发指导.md>) | ReusableModule | [DEV-PLT-015](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) | 已映射待内容复核 |
| `DEV-PLT-ACQ-007` | [结构光投影器抽象与图案时序开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/结构光投影器抽象与图案时序开发指导.md>) | ReusableModule | [DEV-PLT-015](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>)、[DEV-VIS-027](<../shared-modules/guidance/03-vision/DEV-VIS-027_3D HeightField与重建开发指导.md>) | 已映射待内容复核 |
| `DEV-PLT-ACQ-003` | [运动控制抽象与坐标运动开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/运动控制抽象与坐标运动开发指导.md>) | ReusableModule | [DEV-PLT-015](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) | 已映射待内容复核 |
| `DEV-PLT-ACQ-004` | [采集序列_同步与帧质量开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/采集序列_同步与帧质量开发指导.md>) | ReusableModule | [DEV-PLT-015](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) | 指定编排/质量指标章节定向复核，见[实际范围](#acquisition-quality-adoption)；非全文/源实现审计 |
| `DEV-PLT-CAL-002` | [图像校正开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/03-calibration-imaging/图像校正开发指导.md>) | ReusableModule | [DEV-MET-030](<../shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md>) | 已映射待内容复核 |
| `DEV-PLT-IMG-001` | [图像质量与预处理流水线开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/03-calibration-imaging/图像质量与预处理流水线开发指导.md>) | ReusableModule | [DEV-VIS-021C](<../shared-modules/guidance/03-vision/DEV-VIS-021C_图像通道与预处理独立能力开发指导.md>) | 指定编排/质量指标章节定向复核，见[实际范围](#acquisition-quality-adoption)；非全文/源实现审计 |
| `DEV-PLT-CAL-003` | [板弯与局部参考补偿开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/03-calibration-imaging/板弯与局部参考补偿开发指导.md>) | ReusableModule | [SM-012](<../shared-modules/modules/SM-012_surface.md>)、[DEV-MET-031](<../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md>) | 已映射待内容复核 |
| `DEV-PLT-CAL-001` | [标定Artifact与有效性开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/03-calibration-imaging/标定Artifact与有效性开发指导.md>) | ReusableModule | [SM-009](<../shared-modules/modules/SM-009_calibration.md>) | 已核§1–18及8.1；生成接口未全审，采纳范围见§8 |
| `DEV-PLT-IMG-002` | [配准_拼接与补偿开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/03-calibration-imaging/配准_拼接与补偿开发指导.md>) | ReusableModule | [DEV-VIS-029](<../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md>) | §8路线/8.1及8.1.1已读，8.1.2等部分复核；其余未全审，见下文 |
| `DEV-PLT-REC-006` | [Inspector插件与判定融合开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/04-recognition/Inspector插件与判定融合开发指导.md>) | ReusableModule | [SM-019](<../shared-modules/modules/SM-019_evaluation.md>)、[DEV-PLT-017](<../shared-modules/guidance/02-platform/DEV-PLT-017_插件SDK与扩展点开发指导.md>) | 已映射待内容复核 |
| `DEV-PLT-REC-001` | [Mark与通用定位开发指导](<project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/Mark与通用定位开发指导.md>) | ReusableModule | [alignment-2d](<../independent-modules/alignment-2d/DEVELOPMENT-GUIDE.md>) | 文件与本次 H:\docs 来源 SHA-256 一致；只采纳通用场景，具体签名以 26.05 手册及公共接口复核 |
| `DEV-PLT-REC-003` | [OCR与OCV开发指导](<project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/OCR与OCV开发指导.md>) | ReusableModule | [ocr](<../independent-modules/ocr/DEVELOPMENT-GUIDE.md>) | 文件与本次 H:\docs 来源 SHA-256 一致；活动路线依据本地 26.05 页面 |
| `DEV-PLT-REC-002` | [一维码与二维码读码开发指导](<project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/一维码与二维码读码开发指导.md>) | ReusableModule | [barcode](<../independent-modules/barcode/DEVELOPMENT-GUIDE.md>) | 文件与本次 H:\docs 来源 SHA-256 一致；活动路线依据本地 26.05 页面 |
| `DEV-PLT-REC-004` | [极性姿态与方向识别开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/04-recognition/极性姿态与方向识别开发指导.md>) | ReusableModule | [DEV-DOM-057B](<../process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md>)、[SM-011](<../shared-modules/modules/SM-011_vision-features.md>) | 已映射待内容复核 |
| `DEV-PLT-REC-005` | [模板模型注册中心开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/04-recognition/模板模型注册中心开发指导.md>) | ReusableModule | [SM-015](<../shared-modules/modules/SM-015_reference-library.md>) | 主体定向采纳；生成接口未全审，见model-assets-adoption |
| `DEV-PLT-ENG-002` | [2D_3D视图与证据渲染开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/05-engineering/2D_3D视图与证据渲染开发指导.md>) | ReusableModule | [SM-025](<../shared-modules/modules/SM-025_presentation.md>) | 已映射待内容复核 |
| `DEV-PLT-ENG-003` | [确定性回放_模拟器与性能诊断开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/05-engineering/确定性回放_模拟器与性能诊断开发指导.md>) | ReusableModule | [SM-021](<../shared-modules/modules/SM-021_replay.md>)、[DEV-PLT-014](<../shared-modules/guidance/02-platform/DEV-PLT-014_性能预算与并发流水线开发指导.md>) | Replay主体已复核；生成接口/其余扩展未全审，见replay-adoption |
| `DEV-PLT-ENG-001` | [视觉参数编辑器与算法试验台开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/05-engineering/视觉参数编辑器与算法试验台开发指导.md>) | ReusableModule | [DEV-UI-043](<../shared-modules/guidance/05-ui/DEV-UI-043_Program/Recipe编程工作台开发指导.md>) | 已映射待内容复核 |
| `DEV-AI-002` | [AI模型与数据治理开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/AI模型与数据治理开发指导.md>) | ApplicationModule | [DEV-AI-060](<../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md>)、[DEV-AI-063](<../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md>) | 已映射待内容复核 |
| `DEV-AI-001` | [AI设备端推理开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/AI设备端推理开发指导.md>) | ApplicationModule | [DEV-AI-060](<../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md>) | 指定章节内容已复核；执行落[052](../shared-modules/packages/PKG-052_Inference.md#inference-execution)，采纳范围见[本页](#inference-adoption) |
| `DEV-AI-003` | [AI辅助工程师与Copilot开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/AI辅助工程师与Copilot开发指导.md>) | CrossCuttingStandard | [SM-026](<../shared-modules/modules/SM-026_ai-assistance.md>) | 已映射待内容复核 |
| `DEV-REV-001` | [DefectViewer开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/DefectViewer开发指导.md>) | ApplicationModule | [DEV-UI-042](<../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md>)、[UI013](../shared-modules/guidance/14-page-contracts/UI-PCS-013_Evidence_Viewer.md)；复判宿主沿DEV-UI-044 | §1–5.4定向采纳，范围见[本轮记录](#viewer-adoption) |
| `DEV-REV-004` | [ReviewClaim安全与幂等恢复协议开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/ReviewClaim安全与幂等恢复协议开发指导.md>) | ApplicationModule | [SM-022](<../shared-modules/modules/SM-022_review.md>) | 复判/实体链主体已复核；生成接口未全审，见review-adoption |
| `DEV-REV-002` | [复判站与返修闭环开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/复判站与返修闭环开发指导.md>) | ApplicationModule | [PG-023](<../process-guides/processes/PG-023_review-rework.md>)、[SM-022](<../shared-modules/modules/SM-022_review.md>) | 复判核心/批量/返修关键段已复核；§6增量保留，全部扩展未全审；见review-adoption |
| `DEV-REV-003` | [机判_AI_人判融合开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/机判_AI_人判融合开发指导.md>) | ApplicationModule | [SM-019](<../shared-modules/modules/SM-019_evaluation.md>)、[DEV-AI-061](<../shared-modules/guidance/07-ai/DEV-AI-061_AI辅助复判开发指导.md>) | 已映射待内容复核 |
| `DEV-INT-001` | [MES_Hermes_CFX集成开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/60-data/MES_Hermes_CFX集成开发指导.md>) | ReusableModule | [SM-024](<../shared-modules/modules/SM-024_integration.md>) | 已映射待内容复核 |
| `DEV-SPC-001` | [SPC与过程控制开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/60-data/SPC与过程控制开发指导.md>) | ApplicationModule | [SM-023](<../shared-modules/modules/SM-023_quality.md>)、[DEV-DOM-058A](<../shared-modules/guidance/06-domains/DEV-DOM-058A_QualityControl SPC与分母定义开发指导.md>) | 已映射待内容复核 |
| `DEV-DAT-002` | [多存储RPO0提交协议开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/60-data/多存储RPO0提交协议开发指导.md>) | ModuleSupplement | [DEV-PLT-012](<../shared-modules/guidance/02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md>) | 提交/恢复关键段已复核；完整扩展未全审，见evidence-adoption |
| `DEV-DAT-004` | [工厂级数据网络与多站点治理开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/60-data/工厂级数据网络与多站点治理开发指导.md>) | CrossCuttingStandard | [DEV-PLT-018](<../shared-modules/guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md>) | 已映射待内容复核 |
| `DEV-DAT-001` | [数据服务与证据追溯开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/60-data/数据服务与证据追溯开发指导.md>) | ApplicationModule | [SM-020](<../shared-modules/modules/SM-020_result-evidence.md>) | 提交/恢复关键段已复核；完整扩展未全审，见evidence-adoption |
| `DEV-DAT-003` | [通用数据平台DLL开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/60-data/通用数据平台DLL开发指导.md>) | ReusableModule | [DEV-PLT-018](<../shared-modules/guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md>) | 提交/恢复关键段已复核；完整扩展未全审，见evidence-adoption |
| `DEV-OPS-003` | [Supervisor部署拓扑与本机安全开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/70-operations/Supervisor部署拓扑与本机安全开发指导.md>) | ModuleSupplement | [DEV-PLT-016](<../shared-modules/guidance/02-platform/DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md>) | 已映射待内容复核 |
| `DEV-OPS-002` | [维护健康备份升级开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/70-operations/维护健康备份升级开发指导.md>) | ReusableModule | [SM-028](<../shared-modules/modules/SM-028_delivery.md>) | 已映射待内容复核 |
| `DEV-TST-001` | [模拟器与确定性回放开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/80-quality/模拟器与确定性回放开发指导.md>) | QualityGate | [SM-021](<../shared-modules/modules/SM-021_replay.md>) | Replay主体已复核；生成接口/其余扩展未全审，见replay-adoption |
| `DEV-TST-003` | [统计验收与计量能力开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/80-quality/统计验收与计量能力开发指导.md>) | QualityGate | [SM-027](<../shared-modules/modules/SM-027_qualification.md>)、[DEV-MET-033](<../shared-modules/guidance/04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md>) | 已映射待内容复核 |
| `DEV-QLT-001` | [缺陷本体允收标准与质量经济开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/80-quality/缺陷本体允收标准与质量经济开发指导.md>) | CrossCuttingStandard | [SM-019](<../shared-modules/modules/SM-019_evaluation.md>) | 已映射待内容复核 |
| `DEV-TST-002` | [自动化测试与发布门禁开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/80-quality/自动化测试与发布门禁开发指导.md>) | QualityGate | [DEV-GOV-008](<../01-governance/DEV-GOV-008_质量门禁与Acceptance标准.md>) | 已映射待内容复核 |
| `DEV-TST-004` | [视觉数字孪生与Sim-to-Real开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/80-quality/视觉数字孪生与Sim-to-Real开发指导.md>) | CrossCuttingStandard | [DEV-AI-063](<../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md>) | 已映射待内容复核 |
| `DEV-HW-001` | [硬件SDK开发指导_待提供路径](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/90-hardware/硬件SDK开发指导_待提供路径.md>) | ExternalBlocked | [DEV-PLT-015](<../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md>) | 已映射待内容复核 |
| `DEV-HW-002` | [硬件资格FAT与SAT开发指导](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/90-hardware/硬件资格FAT与SAT开发指导.md>) | CrossCuttingStandard | [SM-027](<../shared-modules/modules/SM-027_qualification.md>) | 已映射待内容复核 |

## 4. 官方资料与真实阅读范围

本轮实际读取如下官方Description及相关参数限制，版本URL用于固定来源，不规定平台HALCON版本。源码研究复用REF-002已有固定OpenCV/PCL/Open3D等相关条目；本轮没有声称新增源码运行或工业对比。HALCON公共包装签名仍按受影响功能查公开接口，不扫描AsunImage内部。

| 官方资料 | 本地阅读文本 | SHA-256 |
|---|---|---|
| [reconstruct_surface_structured_light](https://www.mvtec.com/doc/halcon/2511/en/reconstruct_surface_structured_light.html) | [正文摘取](<official/halcon/20260927/reconstruct_surface_structured_light.txt>) | `ab8c34d07ef9731eee8879510210cdf979093287f3c1670ce02c583bddced992` |
| [create_structured_light_model](https://www.mvtec.com/doc/halcon/2511/en/create_structured_light_model.html) | [正文摘取](<official/halcon/20260927/create_structured_light_model.txt>) | `6017029ec521ae8ac7030789e97765ad6036885a8babc5c84bf163a82587aa14` |
| [decode_structured_light_pattern](https://www.mvtec.com/doc/halcon/2511/en/decode_structured_light_pattern.html) | [正文摘取](<official/halcon/20260927/decode_structured_light_pattern.txt>) | `b033872d2fae4c3032412e8bc7892cebf0fc96d954f6495e45e1ed1b9be4206f` |
| [volume_object_model_3d_relative_to_plane](https://www.mvtec.com/doc/halcon/2511/en/volume_object_model_3d_relative_to_plane.html) | [正文摘取](<official/halcon/20260927/volume_object_model_3d_relative_to_plane.txt>) | `57d5cd3b5bb24aa0666e2bb61b12c6ec386ba4c1659c14edd230d7b637ed751e` |
| [fit_surface_first_order](https://www.mvtec.com/doc/halcon/2511/en/fit_surface_first_order.html) | [正文摘取](<official/halcon/20260927/fit_surface_first_order.txt>) | `178d35540e4c14b21a7cffed80a4c9c2820cfb52f974046881eafec77059994d` |
| [triangulate_object_model_3d](https://www.mvtec.com/doc/halcon/2511/en/triangulate_object_model_3d.html) | [正文摘取](<official/halcon/20260927/triangulate_object_model_3d.txt>) | `5fd9417ff64796ee6e73e3e15f5ae4912e75483aa901f99c856d36aaf916bf29` |

当前工具无文档搜索连接器；本轮读取OpenAI官方sitemap及Codex multi-agent/agents-md页面均返回HTTP403，未取得正文。因此不以模型记忆编造并发上限、持久后台能力或自动创建规则；调度设计依据当前已暴露工具合同及项目写入隔离要求，产品文档相关事实保持待核实。这不阻断功能文档、模块分解和调度状态的设计。

## 5. 待复核的真实工作

91份原指导的具体功能/参数/状态/测试尚未全部逐条核完。按对应公共包和产品应用链分轮推进，每轮修复实际指导和关联消费者，不只增加报告。优先核坐标/资源/标定→2D/3D量测→程序/调度→结果/复判→UI/快编→数据/互联/部署；工艺专题研究顺序仍按用户此前决定。原件不变，平台修订有来源，最终可编码状态遵循DEV-GOV-010/011，而非源文件的成熟度声明。

<a id="aoi-increment-20260928"></a>
## 6. 源项目更新后的有界增量归档（2026-09-28）

初始231文件快照取得后，只读比较发现下面两份源文件继续变化。本轮只取得一次增量并按完整内容hash分目录保留；初始原件及来源清单不变，不连续追逐活跃项目。[增量清单](project-snapshots/PCBA-AOI/20260927/updates/20260928/source-manifest.json)记录原hash、新hash与各自采样时间。这个增量不是AOI全工程的一致事务快照。

| 增量原文 | SHA-256 | 读取/接纳范围 |
|---|---|---|
| [上机测试冲刺与竞品全量复核执行计划_2026-09-04.md](<project-snapshots/PCBA-AOI/20260927/updates/20260928/53d32b5504fd9061b442fad8f75d803e8ef72875cda40f8fac97195fd6b8435f/docs/30-plans/上机测试冲刺与竞品全量复核执行计划_2026-09-04.md>) | `53d32b5504fd9061b442fad8f75d803e8ef72875cda40f8fac97195fd6b8435f` | 只对照调度快照变化；不采纳其Goal/会话/自动化授权 |
| [复判站与返修闭环开发指导.md](<project-snapshots/PCBA-AOI/20260927/updates/20260928/a2bb729d2d7328541faca0d074c590cf0eb259fd7508fcd1c83da650c506461a/docs/40-development/50-ai-review/复判站与返修闭环开发指导.md>) | `a2bb729d2d7328541faca0d074c590cf0eb259fd7508fcd1c83da650c506461a` | 新增Office状态读取并发章节已读；仅把输入独立、同基准/期限、排空与最终当前性复核写入平台SM-022及两消费者 |

原DEV-REV-002的其余正文仍待逐条审核，不能因读过增量标全文通过；源文档中的实测/测试声明属于来源，不算本平台执行证据。

<a id="module-boundary-evidence"></a>
## 7. 模块边界的第二次核查

初稿56包补为59包的依据是功能/资源/生命周期差异，新增057轮廓采集、058通用I/O、059报警；不是为了凑更大的数量。前两包读取了现有DeepSight两份公共开发指导的指定章节，并原字节去重归档如下。未读取/修改控件实现、未扫描AsunImage内部、未验证外部依赖或授权。

| 来源指导 | 本地副本 | SHA-256 | 实际读取范围 |
|---|---|---|---|
| `02_项目组成与公共架构.md` | [原件](<project-snapshots/DeepSight/20260928/original/docs/development-guide/02_项目组成与公共架构.md>) | `9914fc52a5fa88c4ebb8f695b3b489962c0404b2b57aea450c3ef685315fc10e` | §1–5.1：Core/Wpf/Interop、会话、完整数据与预览、资源/副作用 |
| `01_SDK与算法覆盖矩阵.md` | [原件](<project-snapshots/DeepSight/20260928/original/docs/development-guide/01_SDK与算法覆盖矩阵.md>) | `4d79b0eec1c8e91e7ba802bba86982bb6bb167953593ad357670ac98675ed425` | §1–2.6：通信/采集/I/O能力分类及契约缺失限制 |

[来源清单](project-snapshots/DeepSight/20260928/source-manifest.json)固定来源；上述公共签名和覆盖数量是指导声明，未据此声称二进制实现已核或平台已接通。报警的官方/固定源码研究见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#alarm-source-research)。

核查也保留不拆的边界：安全PLC/急停不作为通用软件包能力；物料转运/夹具流程随产品；质量最终处置遵循原批准Owner，不能把统计/报警/人工确认作为新放行权威。具体拆合反例在[MODULE-CATALOG §6](../shared-modules/MODULE-CATALOG.md#boundary-derivation)。

<a id="foundation-adoption"></a>
## 8. 坐标、租约与标定的实质复核和平台落点

本轮只读20260927原始归档，不再次读取/修改活跃AOI项目。来源hash仍由原source-manifest维护；原文的“金标准”“已测”、固定循环/时长、版本、硬件或任务授权均不成为本平台证据。

| 已实际读到的原指导 | 平台采用/修订 | 明确不继承的部分 |
|---|---|---|
| DEV-STD-003全文正文，coordinates.v1.json的35项源例已解析 | [PKG-007 §6](../shared-modules/packages/PKG-007_Coordinates.md#coordinate-math)：列向量/组合方向、单位、中心/corner与HALCON换基、crop、几何类型/误差与3D域 | 固定板高翻Y/Z的Bottom约定不能应用所有制造来源；源golden需逐条判适用/改写/不适用，未执行其runner |
| DEV-ARC-007全文 | [DEV-VIS-022](<../shared-modules/guidance/03-vision/DEV-VIS-022_图像帧、Tile/Pyramid与Viewport开发指导.md#frame-resource-contract>)：超时不等于可回收、显式资源代与唯一归还、别名/边界复制 | 原协议是跨进程SPSC；固定256字节header、HMAC/token布局和角色不能直接作同进程多消费者协议 |
| DEV-PLT-FND-001 §1–18 | 同一帧指导及PKG-007：资源/坐标分开包，依赖正式契约；新增read scope、布局范围、mask与支撑域处理 | 后续生成接口/样例未全核，不复制源命名空间/API或源项目已测试声明 |
| DEV-PLT-CAL-001 §1–18含8.1 | [DEV-MET-030 §6–7](../shared-modules/guidance/04-metrology/DEV-MET-030_Calibration与标定资格开发指导.md#calibration-lifecycle)：独立验证/依赖闭包、CAS激活、固定引用与资格失效区别；同步FS-016/UI-PCS-007 | 固定底层版本、线程数、schema/encoding、1MiB等源限制未直接继承；方法实际公共签名/全部生成节仍待核 |

修复了FS-016和DEV-MET-030套用产品量测结果链的错误，标定输出回归资产/验证证据/资格引用，产品结果仍由量测与工艺链产生。数学来源由[HALCON官方和.NET源码研究](REF-002_GitHub_DevExpress与OpenSource研究基线.md#foundation-source-research)补强，平台只采用明确语义，不先造第二套生产Schema。此轮不是91份指导的全面通过。

<a id="roi-metrology-adoption"></a>
## 9. ROI与量测的公开来源和采纳边界

AOI的DEV-PLT-FND-002只读原快照：本轮读§1–9及V2相对ROI/恢复/投影关键部分，后续生成接口未全核；采纳几何/目标分离、显示不回写、批量原子、旧预览不覆盖、未知内容保留但不执行，落实DEV-VIS-024。源项目Protobuf/V2包布局、数值上限、原会话Owner与授权不迁入。

Asun_ROI原项目未改。选取9份公开资料原字节归档于[来源清单](project-snapshots/Asun-ROI/20260928/source-manifest.json)，包括公共API快照；未读取控件实现/AsunImage内部、未验证依赖/授权。归档不等于每份全文已审，范围逐项如下。

| 资料原件 | SHA-256 | 实际阅读/用途 |
|---|---|---|
| [README.md](<project-snapshots/Asun-ROI/20260928/original/README.md>) | `63f063dd30f38e01078229bb292560f52f9019a1ce79028fe40c71d1389d434a` | 前48行：产品/平台/边界声明，原Development Verified不作平台证据 |
| [PublicApi.Shipped.txt](<project-snapshots/Asun-ROI/20260928/original/PublicApi.Shipped.txt>) | `c96286de419a45b979608d32aba0cda29ba3c231c15c223336ce36d31f6c0d3e` | 定向查RoiEngineSession的CreateAsync、TryPostFrame、CreateMeasurementRequestAsync、ClaimMeasurementWorkItemAsync、ApplyMeasurementResultAsync、ShutdownAsync；其余未全面审读，也未核实际二进制 |
| [03_线性卡尺与Rake卡尺开发说明.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/03_ROI功能/03_线性卡尺与Rake卡尺开发说明.md>) | `4de58b38491d63950b55284e0d847de80df33b226f87b459648c7472f6533994` | 方向/参数/采样、请求/结果/应用/事件/失败章节及拟合段；来源数值/状态不直接继承 |
| [04_径向多边形V型与螺距卡尺开发说明.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/03_ROI功能/04_径向多边形V型与螺距卡尺开发说明.md>) | `5681869f77d73ac81093d8bcbfc011cacb42fecb92dde15cc806f299f4462625` | 前82行：闭环采样、拟合质量、Polygon/V/Pitch与缺项索引；后续未全审 |
| [07_Windows无窗口Session运行.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/04_工程能力/07_Windows无窗口Session运行.md>) | `d6119ce4f3569b828ce35626f144b7a55b559c754a4b6a68e26310419c3d67a0` | 完整公共说明：无Window运行、串行Session、FrameActivated/Presented区别、共享ShutdownCompletion；不继承依赖核验要求 |
| [01_HALCON互通开发说明.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/05_集成与验证/01_HALCON互通开发说明.md>) | `1546d065bb2c59cf83075cf00c4b70c0c645eabaef8fcc6da04b0c8b89b841e7` | §1–2部分声明、§4–8映射/运行/复用与§9/13路由节选；后续导入等未全审；版本/半长/阈值/句柄策略作适配差异输入 |
| [02_区域多边形与遮罩ROI开发说明.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/03_ROI功能/02_区域多边形与遮罩ROI开发说明.md>) | `972b0a1c4c9cb8c4202e0153990edab513124052286aa68fc4fc73e6cbc74ff9` | 类型、环/布尔/近似/空结果及资源事务节选；不复制fixed64内核或事务协议到平台 |
| [12_3D点云与高度图输入开发说明.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/03_ROI功能/12_3D点云与高度图输入开发说明.md>) | `186a401fde6210693aee388e0e3c10dd5fe5ef3b8c9277ee99f18c4ea4af5743` | §1–3.3：点云/高度图、source index、属性/有效性和P1边界；其后hash/队列等待核 |
| [15_3D滤波拟合与测量结果开发说明.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/03_ROI功能/15_3D滤波拟合与测量结果开发说明.md>) | `58fbe7356ea8423e8c7ecbaf3fa80af8c42759e7bebb1a4a4f43732414b0012f` | §1–3.1节选：执行输入、类型/源索引/滤波链与native-managed路由；其余拟合/体积细项待核 |

平台落点：[ROI几何/事务](<../shared-modules/guidance/03-vision/DEV-VIS-024_ROI与Inspection Target Selection开发指导.md#roi-editing-execution>)、[卡尺与拟合](../shared-modules/guidance/03-vision/DEV-VIS-025_2D边缘、轮廓与几何特征开发指导.md#edge-fit-pipeline)、[量值/结果](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#measurand-result-closure)、[表面载体](../shared-modules/packages/PKG-027_SurfaceData.md#surface-data-provenance)及SM-010公开入口映射。官方与GitHub对照见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#measurement-source-research)。

复用现有单DLL的公开能力不等于全部包已经物理独立。当前设计为平台责任/门面边界；交付后按需要提取/适配，沿原工程兼容任务接收同一个Session和资源Owner，禁止四个包复制四套Store。源控件的managed确定性路径有具体协议理由，平台仍逐方法HALCON优先评估；不把来源中的“没有单算子闭包”当永久禁止HALCON组合路线，也不本轮重写源算法。
<a id="surface-adoption"></a>
## 3D表面处理与配准的本轮采纳 — 2026-09-28

未重拷现有快照，未改原工程/归档原件。继续读取：AOI DEV-PLT-FND-004第1–129行（主体§1–18及H11派生/显示），DEV-PLT-IMG-002的§8开始、8.1/8.1.1和8.1.2部分，DEV-VIS-006的§2–3.2及接口段；ROI `15_3D滤波拟合与测量结果开发说明`补读§4–6、§7.2–7.3及§8，复读§3.1路由。未将这些文件的生成接口、所有方法/Pin详项或实际实现标为全审。

| 原文实质 | 平台采纳/修订 |
|---|---|
| AOI Surface不可变、Mask/XYZ/点/mesh分离、派生/LOD、读租约及显示高度映射 | 接入PKG-027与DEV-VIS-028；物理高度、显示色带、检测派生灰度分离，原生可变扩展属性使用独占工作模型 |
| AOI配准最低必要自由度、运动/标定先验、独立几何/显示融合 | DEV-VIS-029保留2D FOV；060独立3D位姿与图质量，不复制CoordinateGraph；阶段推进不等于执行优化 |
| ROI确定性voxel/邻域/filter证据、TLS/refit、引用基准与Result附件 | PKG-031复用公共协议；029补二维支撑/特征间隔/外推/物理参考；源Profile固定数值不是平台默认 |
| ROI点云volume仅按特定凸包栅格，凹/洞/P2能力受限；平面度/剖面有专属定义 | 不扩大为所有平台拓扑支持；DEV-MET-031明确LS残差极差不等于最小区域平面度，逐方法继续设计 |

ROI原策略中“没有单算子闭包”的managed理由只作协议差异；平台每方法仍先核HALCON组合与现有公开能力，不复制控件内部。官方证据已发现采样属性损失、全局score为邻居数、距离写入From/截断等，已修订相应指导；不继承源项目固定HALCON版本、依赖/授权核验、强制runtime探测及客户阈值。

060新增的依据是两个独立消费者及位姿/图生命周期，公共总数由59修订为60，未更改旧包ID。原“Register”职责由SM-012明确落至060；单表面031、参考029、被测量030、数据027仍各司其职。界面、精确签名/Owner、真实样本与生产误差没有因本轮文字完备而自动冻结。

来源文件hash沿原manifest复核；官方/源码归档及真实阅读范围见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#surface-source-research)。新增源码和文档均未运行，不据MIT/上游测试目录推定工业可用。


<a id="runtime-adoption"></a>
## 程序发布、离线协作与板级编排的采纳 — 2026-09-28

原20260927快照继续只读，不重复拷贝或追逐活跃客户工程。本轮实际阅读：DEV-REC-001的§4、5.1、7主体、8–14及§7.3/7.4（242–264行）；长UI/provider/checkpoint及生成接口仅部分定位，不宣称全文通过。DEV-RUN-001的§2–4、§5至5.3（145–180行）与§6–7恢复/资源段；双轨全部后续扩展未全核。DEV-NPI-003的§1–5.2（至54行）和离线闭包/迁移的相关摘要；后续远程会话细则未全审。recipe-manifest.schema.json完整读取，仅作为C-02差异输入。

| 来源核心 | 平台采纳/修订 | 不直接继承 |
|---|---|---|
| Recipe草稿typed操作、最终图一致、原CAS/回执、三方diff；相关Program/输入/照明同保存 | [PKG-035 §6](../shared-modules/packages/PKG-035_ProgramPackage.md#program-lifecycle)：原子批量、字段语义耦合、验证失效和候选hash分层 | 源API命名、canonical域、固定集合上限/保存周期、角色与工作树授权 |
| pin reservation、manifest、Recipe事务、pin commit与操作恢复 | [PKG-035 §7](../shared-modules/packages/PKG-035_ProgramPackage.md#publication-recovery)：持久保持确认先于发布可见；未知结果不回收；原Owner统一恢复 | 不把数据库事务后补pin当跨存储原子性，不借旧已实现声明免除窗口验证 |
| 发布标定要求、ResolveForDevice实际快照；发布/激活/运行分开 | FS-002/DEV-PLT-010和003/004/009页面同步，r1在途不被r2改写 | 强制签名、原role分离及runtime依赖核验不自动迁入，AsunImage/DevExpress仍按用户决定直接采用 |
| 显式DAG、阶段attempt、跨板隔离、重启查原operation/设备 | [DEV-PLT-011](<../shared-modules/guidance/02-platform/DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md#typed-execution-graph>)：图类型/required/分支/资源编译，计算尝试与生产尝试分开，等待与真正排空分开 | 固定运动→重建→AI等全链、双轨默认、设备安全语义及原数值不强制所有制程 |
| 离线确切对象批测、baseline/candidate、One Programming保留目标差异 | PKG-035§8、DEV-UI-043§8：源映射/选择分母、同质组、导入候选、完整性和现场资格分开 | 离线证据不冒充现场，不能为通用删必检/丢单位，不继承客户远程授权策略 |

原Schema的required calibrationRequirements/approvals/signatureRef等字段不自动成为所有平台模块的必填；正式平台采纳仍在原ContractCandidate完成，不新建第二Recipe模型。官方与固定源码补充见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#runtime-source-research)。这里只读指导/Schema，没有审计客户产品代码或运行其测试。


<a id="evidence-adoption"></a>
## 结果证据与通用存储的采纳 — 2026-09-28

原件不改、不重拷：DEV-DAT-002第11–139行（§1–13）；DEV-DAT-001第1–110行（主体到服务/读取合同）；DEV-DAT-003第125–179行（事务/Outbox/迁移/备份）。后两份其余方法/生成接口未全审。evidence-manifest.schema.json只读根required/properties及object、evidenceRequirement、Replay相关定义，未声称所有条件/签名规范全审。

采纳至[DEV-PLT-012](<../shared-modules/guidance/02-platform/DEV-PLT-012_Evidence Graph与Result Commit开发指导.md#evidence-commit-protocol>)与[PKG-041](../shared-modules/packages/PKG-041_Storage.md#storage-transactions-durability)：对象先可靠持久并保持、元数据/回执/外发意图同事务、最终proposal在服务生成引用后冻结、未知原ID查询、逻辑证据scope/count/传递依赖、坏结果与Replay缺项分开、读/备份保持及回收协调。FS-004已修正NG/Invalid不能保存的模板错误；UI-PCS-013区分存储成功和产品合格。

原方案中的本机SQLite、远端仅投影、固定canonical域/签名/角色、外部授权proof、设备路由及客户数值不直接迁入。原GC“72小时＋两次扫描”不能单独证明并发新增引用不被删，平台增加与引用/读取预约共同协调的必要条件；源文件原字节保留，未修改其协议或实现。

结果事务与处置/设备行为继续不同Owner/不同语义；040不再复制通用存储或MES发送器，041只技术持久化，047承担互联交付。所有来源实现/软件测试声明仅属于原项目，本平台没有运行原产品或数据库测试；官方与固定Git来源详见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#evidence-source-research)。

<a id="replay-adoption"></a>
## Replay与Golden研究的采纳 — 2026-09-28

复用只读快照，没有重拷源项目：DEV-PLT-ENG-003第1–103行主体、414–426行DebugBundle与原实现声明；DEV-TST-001第1–128行主体。其余生成接口/完整扩展未全审。evidence-manifest.schema.json定向解析replayInventory、replayAssessment及其中missingInputs结构；Exact/Tolerance/NonReproducible为原保存评估候选语义，不把DataService固定Owner及原签名协议直接批准为平台合同。

吸收到[DEV-QLF-070](<../shared-modules/guidance/08-qualification/DEV-QLF-070_Golden Sample与Replay开发指导.md#replay-execution>)、043/055和UI014：历史闭包/环境、合法切点、模拟/诊断与性能时间、无生产副作用、案例恢复、固定数据集/对比政策、只读诊断包。补充原文没有详定的有向容差/近零/非有限、身份全外连接、mask/拓扑/双向覆盖、禁止自动配准掩盖差异、质量阈值变化及Golden防泄漏/批准链。

未全量继承源项目的接口/状态/命名空间、签名/审批、72小时/7天/1000板等固定数值；原47+7测试和WPF截图声明仅属于原项目，本平台未运行。保存时Replay评估、当前依赖可用性和本次比较结果分开，历史评估不被重写；原版本不可执行可只读Explain，不能静默换新环境标Exact。

当前只补与复判的报告交接，没有声称完成DEV-REV系列完整复核。官方/源码及读取限制见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#replay-source-research)。原件字节按源manifest复核保留。

<a id="review-adoption"></a>
## 复判协议、返修与实体板流的采纳 — 2026-09-28

只读原归档：DEV-REV-004第1–81行完整主体；DEV-RUN-002第1–48、64–127行（第50–62段只作协议关系定位，未逐字采纳）；DEV-REV-002第11–38、44–52、389–419、423–444、457–498、520–550、564–584的关键语义。其余生成接口/大量历史扩展未全审；先前20260928增量继续只按§6既定读取范围，不重追源项目或重复复制。DEV-REV-001本轮只定位标题，未作全文采纳。

公共机制落在[PKG-044](../shared-modules/packages/PKG-044_Review.md#review-transaction-flow)：源事务/Claim代、历史操作恢复、秘密可恢复性、批量计划/逐项回执/未发送、纠正/盲审；工艺闭环落[DEV-DOM-057D](<../process-guides/guidance/06-domains/DEV-DOM-057D_AOI Review Rework与Disposition开发指导.md#aoi-review-closure>)和PG-023。UI005补列表/全景/2D/3D/意见及键盘防误判。FS063修正把人判当“新calculation identity”的模板路径，FS066保持处置投影。平台自审还补清PG023/FS063的历史读取与新写条件、UI005/AOI盲审可见范围、FS066多来源水位与缺口/历史处置分离；这些属于平台推演，不宣称源指导已有同等实现或已测试。

未迁入源SQLite、32字节/固定canonical加密方案、密钥提供者、固定签名期限/对象/队列容量、AOI角色或旧用户专项授权。源不同文档中Orchestrator/DataService分别作为业务/持久化/签发Owner，平台没有直接复制名字或另建权威；精确处置/授权组合须原契约采纳。源“严格优先层且持续高优先流量下普通项仍满足最大等待”缺容量前提，不能无条件成立；本平台已补过载/公平策略的适用限制。

源原件全部保留；新材料及竞品原页核读见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#review-source-research)。本平台未运行来源项目的RPC、数据库、WPF或设备测试；来源状态/成绩不继承。

<a id="arbitration-adoption"></a>
## 多轮仲裁的来源差异 — 2026-09-28

继续只读原归档：DEV-REV-002第423–444行重核Case/Claim/返修/仲裁主体，其他匹配行只用于定位前序、投影/盲审与非生产原授权；DEV-REV-003第1–115行核强制分层、人工意见/迟到及原Owner关系；源状态、固定签名/SQLite/枚举/客户数值不继承。`review.proto`实际读61–99、992–1016行，未声称全文件或所有依赖已审。

源指导只有仲裁意见引用/人员/策略/回执的概述，proto已读段提供主体/前序/回执和可见投影，但不能据此宣称多轮分配、冻结输入集、独立性与仲裁更正协议完整。平台在[PKG-044 §11](../shared-modules/packages/PKG-044_Review.md#review-rounds-arbitration)补问题/分配、有效前序/分母、盲审披露、仲裁事务与更正影响，并在§11.7登记回原契约采纳的差异；AOI/PG保留工艺语义。研究真值与生产处置不共用一个完成标记。

新的几何/多数反例和CVAT限制属于平台研究，不回写源指导，不继承源实现/测试成绩，也不修改原已归档字节。详见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#consensus-research)。

<a id="viewer-adoption"></a>
## 原图Viewer与既有ROI视口的采纳 — 2026-09-28

复用原归档，未重拷或修改客户项目/ROI原件。本轮读取DEV-REV-001《DefectViewer开发指导》1–115行（§1–5.4）；ROI PublicApi仅定向公开方法/事件、2D/3D快照和ChangeRequest/Receipt构造字段；无窗口Session公开说明定向确认FrameActivated与FramePresented、关闭排空区别。未读控件或AsunImage内部，没有运行源项目测试。

| 只读来源 | SHA-256 |
|---|---|
| [DefectViewer开发指导.md](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/50-ai-review/DefectViewer开发指导.md>) | `9bf1b1a54943841e908fb3b51c5413dad7e49efc6caff9f9ca74332741c8fa7c` |
| [PublicApi.Shipped.txt](<project-snapshots/Asun-ROI/20260928/original/PublicApi.Shipped.txt>) | `c96286de419a45b979608d32aba0cda29ba3c231c15c223336ce36d31f6c0d3e` |
| [07_Windows无窗口Session运行.md](<project-snapshots/Asun-ROI/20260928/original/docs/roi-control-spec/04_工程能力/07_Windows无窗口Session运行.md>) | `d6119ce4f3569b828ce35626f144b7a55b559c754a4b6a68e26310419c3d67a0` |

采纳到[DEV-UI-042](<../shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md#viewer-execution>)和[UI013](../shared-modules/guidance/14-page-contracts/UI-PCS-013_Evidence_Viewer.md#viewer-specific-operations)：只读Viewer/宿主写入分开、Actual/Reference显式角色、纯2D和零Item原图、完整hash与尺寸依据、缓存命中复核授权、显示变换与原坐标、同一解码Owner、借用scope不随页面释放、未装配导出与权限不足分开、三语不重发操作。

源WIC PNG/JPEG/BMP限定、32MiB/16384/16777216/64MiB数值、canonical域、具体类型和类构造者、APP-REV角色/Owner及源“已完成测试”不自动迁入平台。显示尺寸不提升生产元数据/补标/导出资格；平台既有006才拥有源解码/缓存，不能因源Viewer含decoder再复制一套。ROI公开签名只证明接口存在及字段，实际1:1、DPI/呈现顺序、read-only装配与资源线程语义仍由公开接入切片精确绑定。

旧只读证据页中“拖动ROI提交Command”和Accept/Reject/Defer快捷键泛化模板已修正；复判宿主若需补标走020/044当前授权和完整源绑定，UI013仍只读。显示适配按租约拥有native资源与页面不暴露句柄并不矛盾。原引用只支持设计采纳，不当平台WPF/HALCON/客户可用性验收。

<a id="library-adoption"></a>
## 元件封装参考库与AOI快编的采纳 — 2026-09-28

继续只读既有[DEV-LIB-001 v2.7原件](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/20-product/元件封装检测库开发指导.md>)；未回写原项目、未重拷。完整可见地读取1–120、139–186、216–253、849–858行；122–137、259–279等前次批量输出有截断，只定位不声称已完整复核。全篇后期附录/实际实现/公共API仍未全审。

采纳身份/Package/VisualSignature/Inspector/Acquisition/实例覆盖分层、硬身份约束先于视觉排序、每proposal最终匹配处置、精确闭包和适用性、同一变体全部必要子项、替代与混料区分、ExpectedPresence实例语义、阵列/Pin1/忽略保留及跨目标传播恢复。源后期明确ImageOnly不能变真实料号、Library与Recipe原回执身份不同，已融入公共机制。

公共唯一正文落[034 §6–12](../shared-modules/packages/PKG-034_ReferenceLibrary.md#reference-library-resolution)，源APP-LIB-01不是平台第二Owner；033处理字节/租约，035程序草稿，036编排。AOI专属来源对账、拼板/面/装配变体、针序/ROI/可见性及P0–P7落[057A](<../process-guides/guidance/06-domains/DEV-DOM-057A_AOI CAD PnP与Target自动生成开发指导.md#aoi-target-synthesis>)，UI012/020给具体操作，FS056消除通用模板误写生产事实的矛盾。

源`LibraryItemContent`、1.0/2.0序列化、固定十进制微米、权限名、HMI/注册表/锁/签名域、代码写权与源测试成绩不直接迁入；平台原C候选/GATE-001决定正式字段/canonical/兼容。也不迁入源机器/许可核验要求。源“已完成/通过”不代表本平台已实现。

新增OpenPnP/KiCad/PARMI比较与阅读范围见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#library-programming-research)。同值锁定、索引top-k不证明唯一、DNP与PnP缺行不同、影响水位非锁等为本轮平台补充推演；原件保留原版本/hash，不能回写成源已批准。

<a id="coverage-planning-adoption"></a>
## 覆盖/FOV规划的定向采纳 — 2026-09-28

复用原归档，未修改原项目或重拷：DEV-VIS-002 v2.2实际核读1–38、122–199、199–255（规划/需求/求解/运行/验证）；DEV-PLT-ACQ-006 v1.2核读1–58、85–120、135–143（领域分工/手工编辑/历史查询/H11）。初次批量读取其他范围有截断，不据此声称791/379行全篇、后续生成接口或源实现已经审完。

采纳观察需求与器件语义分开、usable FOV而非名义矩形、不可拆/多模态完整组、资源DAG/有向运动成本、独立原库存验证、只重排未执行任务、typed手动编辑/全局验证、保存未知查原回执及历史读回不重求解。公共机制落[018计算](../shared-modules/guidance/04-metrology/DEV-MET-034_Coverage与Sampling开发指导.md#coverage-sampling-implementation)、[019规划](../shared-modules/packages/PKG-019_ScanPlanning.md#scan-candidates-constraints)，工艺仍各自提供义务，程序采用由035。

源三分钟、4096/其它容量、锁/签名/租约/canonical字段、旧HALCON版本和角色/代码写权不迁入平台。源相同seed必同计划hash不直接采纳：并行/时间停止及多最优解要分别处理。源先复核外部授权再提交的文字不构成跨服务原子保证，平台最终判定时刻/撤销边界仍由原协议采纳；不复制其多套存储身份为新权威。

新增固定OR-Tools和HALCON资料使OPTIMAL的gap含义、NoOverlap/Cumulative零长度差异、空Region/非zip交集更明确；有限候选无解、采样失败保分母、撤销一帧重算交叠、半开资源区间等是平台补充推演，不回写成源项目已实现。来源及真实阅读/测试限制见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#coverage-planning-research)，源软件测试成绩不继承。

<a id="acquisition-quality-adoption"></a>
## 采集编排与图像质量的定向采纳 — 2026-09-28

本轮复用两份原归档，不重拷、不改源项目。ACQ-004 v1.2定向核81–96（曝光/原生照明映射）、185–234（挑战/共享观察/编译边界）、485–500（源质量桥）、580–606（指标/单位/域）；另读页首真实宿主/静态2D说明，初次批量输出其它范围截断，不声称全文/生成接口已核。IMG-001定向核12–38、86–111、115–153（领域/质量路线、原报告重复性、曝光、噪声/焦点/对比/方向），部分初次批量读取截断，未宣称全页后续条纹/颜色/处理Stage或源实现已审。

采纳：原照明step不等于采集节点、计划/Actual/原帧精确关联、静态模式显式不适用Motion、原报告的具名单位/尺度与缺失、原图与派生图分开、取消未停不返池、同帧重包不算独立重复。序列执行唯一落[DEV-PLT-015 §10–14](../shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md#acquisition-sequence-implementation)，质量指标落[IM-020 §18–24](../independent-modules/image-quality/DEVELOPMENT-GUIDE.md#image-quality-implementation)，014处理图仍在021C。

未迁入源合同名/canonical/角色/签名handle、固定byte单plane/测试板数/强制候选数、旧版本依赖核验或源成绩。源Acquisition.Contracts直接依赖ImageQuality.Contracts不直接覆盖本平台目录；当前由宿主连接012/013，无反向实现依赖。源sigma与localMean差标不确定度、弱方向导数推模糊轴均须修正：局部响应带倍率/纹理成分，候选分歧不是计量不确定度，方向纹理也可产生弱导数。

新增HALCON官方、Aravis固定源码/测试及Basler行为与竞品原页的实际范围见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#acquisition-quality-research)。未运行上游/平台/硬件，不以本轮研究声称源项目有已确认代码缺陷或替其改实现；这里只修本平台指导。

<a id="imaging-optimization-adoption"></a>
## 曝光/增益/光源优化的定向采纳 — 2026-09-28

复用ACQ005 v1.1原归档，定向读1–82（范围、UI/独立消费者、公开接口候选、历史/逐步骤关联）和130–188（流程、搜索、治理/预算、恢复与验收）。后续生成接口及中间文件信任/宿主签名实现未全审，初始大段输出被截断部分不算全文完成；没有读取原项目实现或改客户工程。

源指导显示优化已有独立Core/Ui及NPI/独立工作区两个消费者；平台原60包只在036快编正文笼统描述，不能满足独立试验台无需程序库的调用，因此新增[061](../shared-modules/packages/PKG-061_ImagingOptimization.md)。013仍给原指标，012实采由宿主桥接，036/035管理建议到草稿。没有迁入源API/私有Store、canonical/签名域或源任务/工作树授权。

保留有证据候选、Pareto、锁定、完整目标/实际设置、名义与扰动关联、重复物理帧不计独立样本、合法但低质量基线可改善、取消/迟到隔离和设备恢复。进一步补了有限惰性搜索/量化去重、联合电流与跨trial热窗口、auto结束非收敛、完整多曝光耦合、区间支配及保留集泄漏。源先验三分钟/72小时、五通道颜色、固定dB/百分比输入边界不能变平台常数；旧单组设置限制也不能被悄悄删除后假称已支持联合多曝光，平台需正式完整组合同。

061/062、UI012、AOI057A与钢网PG013、原C候选/交接/并行计划已同步。原件hash与原snapshot manifest由本轮定向检查核对；本轮文本和算例不继承源已基线/已实现/WPF验收成绩。

<a id="mosaic-adoption"></a>
## 配准、拼接与补偿的定向采纳 — 2026-09-28

复用原[IMG-002 v3.2](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/03-calibration-imaging/配准_拼接与补偿开发指导.md>), SHA-256 `298246e7218687ce1d71da1c39fe7dcb86e6b6debcaa6ebea460acd3fe54fdd4`。实际定向核§1–7的任务/模型/接口/首次执行与时序、§8/8.1/8.1.1/8.1.2、§8.2/8.5、§10、§12/多帧Review、§12.1及§15/15.1。精确本轮重读范围14–115、116–233、266–299、302–323、339–372；§9输出大段及408起生成接口未完整阅读，不宣称全指导/源实现已审。

采纳目标：输入先于输出/无自引用、受限几何与独立验证、真实先验与位置模型适用、几何/显示用途分开、保护ROI/多源来源、虚拟tile/资源、Unknown/取消排空与历史重开；全部写入平台唯一[029 §8–15](../shared-modules/guidance/03-vision/DEV-VIS-029_多FOV拼接与全局坐标开发指导.md#mosaic-implementation)。源GraphValidator仅组合锚路径/闭环的说明不能据Optimizing阶段名证明执行全局优化；本轮查HALCON束调整明确真实候选。

不搬源项目多Store/签名域/私有类型、定点1_000_000权重、固定72小时/10000板/10万次、旧runtime验证/版本、状态转换或历史native测试成绩。平台通过原033/035/041合同交接，不另造拼接存储/标定Owner。源“必需区域缺失则整个能力Invalid”细化为：保留Partial工程诊断，阻断受影响全量用途；源TransformsOnly计量限制保守沿用为当前优先路线，资格化测量网格须另有批准方法，未自动开放。

补足源未充分展开的两处：多带融合不能用feather同点权重解释；多源主索引只是导航，完整溯源仍需贡献/邻域/处理依赖。断视觉图但有合格共同先验与无定位分量分别表示。官方角点/row-column、自动画布平移、domain忽略等本轮来源见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#mosaic-research)。原件与客户交付工程未改。

<a id="matching-adoption"></a>
## Mark与通用定位的定向采纳 — 2026-09-28

原件[DEV-PLT-REC-001 v1.4](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/04-recognition/Mark与通用定位开发指导.md>)，SHA-256 `103e2eea2d065e174f5ec3f5284573ef63a1edafb873e14c9283cc46da8f560f`。实际定向读§1–9（12–69）、§12.1/12.2（83–104，补读完整）、§14/15（110–118）及H11（142–148）；前170行的大输出有截断，150起生成接口不称全文已审。未修改原件/交付项目、不继承源“已实现/已验收”的状态。

采纳到平台唯一[023 §7–14](../shared-modules/guidance/03-vision/DEV-VIS-023_定位、注册与Alignment开发指导.md#matching-implementation)：真实模型文件训练/重开、NCC与shape参数不能默降、score不充目标不确定度、原点/裁切/缩放、scope/父子失效、有限主备用/单deadline、特征到目标逆变换、未知停止、原回执/排空与两消费者。源`T_target←feature`先逆再复合，与平台列向量约定等价；不能只平移备用中心。

不迁源私有API/Store/签名域/权限实现、Gray8单帧/pixel首版限制、32slots/4features/128次/native并发1、固定工作区大小或已测成绩。平台默认同句柄互斥，独立模型并发按预算；恢复不持有设备端口。源首版多点相似要求3个非共线required slot是其Profile，不能变全部二维刚体数学门：本平台区分代数可观测/冗余/用途资格，二点可求刚体/相似但独立质量另验，仿射仍需非共线。

补足候选截断/抑制、对称等价、同次候选全局关联、有限惰性枚举及几何必要剪枝；先完成冻结几何消歧，多候选不直接等于终局歧义，终局歧义不可用备用消除。独立质量缺失仅阻依赖用途，工程诊断保留。UI002/012、钢网PG013、AOI057A、原C候选及计划014§26已对齐。来源与公开算子限制见[REF-002](REF-002_GitHub_DevExpress与OpenSource研究基线.md#matching-research)；模型/公共合同、全部变体与真实资格仍需继续。

<a id="model-assets-adoption"></a>
## 模型注册中心的定向采纳与边界修正 — 2026-09-28

原[DEV-PLT-REC-005 v1.1](<project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/04-recognition/模板模型注册中心开发指导.md>)，SHA-256 `aa922f4dd9d31b3f0162337a344cd803ea2058c57829ec221aa0fa2ac487adc3`。主体1–110已直接读，生成接口中117–171定向读；172后及生成大段未全审，不继承源已基线/实现/native/72小时成绩。未改源项目或副本。

源§7与§9列不同生命周期序列，§11令ModelCache持native而源模型治理又包含业务批准/激活；平台不照搬其两套状态机/私有签名/Store/端口。技术内容与依赖由IM-014，实际存储由存储Owner，native由实际算法适配者，领域库/程序/AI/标定资格仍原Owner。唯一技术正文为[IM-014](../independent-modules/model-assets/DEVELOPMENT-GUIDE.md)，[033](../shared-modules/packages/PKG-033_ModelAssets.md#model-assets-implementation)仅为应用映射。

保留精确ref、完整依赖、训练/验证来源、发布不改原字节、影响分析、原回执幂等/Unknown、导出权限/旧响应隔离、GC与在途租约、历史恢复。补核心内容先于验证报告的无环关系、运行/来源/验证三类用途闭包、外部权重与长度/路径、默认运行参数重开、并发读等待者取消、内容/native/持久保持分离、alias/source不承诺字节不变、空机重导入与备份恢复。

不迁源强制签名/四眼/授权系统、P0供应链或AsunImage版本准入、1000次/72小时固定阈值。报告/许可/部署制度按实际产品政策，AsunImage/DevExpress依用户决定直接采用；模型格式及实际输出验证属于本平台功能验收。旧代lease失效也不授权卸载仍在执行的native实例。模型转格式/按来源重建产新资产，不能冒称原hash或证明可数值复现。OCR/AI/匹配及033控件/计划§27已对齐，完整格式变体/精确合同/工艺资格与其余内部设计继续。

<a id="inference-adoption"></a>
## DEV-AI-001设备推理的指定章节复核（2026-09-28）

只读副本SHA-256 `82cbe0e44d4833314f8c0438a25d67ccd5bf297da4a847d41a864d1fbbbb1718`，对照原source-manifest保持不变。本轮读1–46、76–171和694–716；174–693生成接口未全文读取，不声称全篇/产品已复核或通过。

采纳：任务型输入/输出、HALCON优先、原物理/张量/Vision证据分域、预处理/反坐标、逐item批次与缺项、模型/输入资源租约、取消与native排空、回退须批准且实际可追溯、原双侧operation回读及当前读取权。晚补章节揭示提交锁等待可能挡住取消和治理重入风险，平台落实行为约束，精确权限/锁序交原Owner采纳。唯一技术正文[052](../shared-modules/packages/PKG-052_Inference.md#inference-execution)，060/SM026、AOI/PG021、UI014与计划014§28已同步。

不直接迁入：强制Aoi.AiHost独立Worker、外部模型默认ORT、源私有OperationStore/状态枚举/API/7199文件权限、源canonical兼容规定、签名/四眼制度、72小时/10000板数值、已有测试成绩及全生产批准。源§5把后处理变更关联MachineDecision revision，平台改为新方法/计算身份，是否生产revision仍由原Owner决定。源§7.3“fsync+替换”不覆盖041既有耐久边界；源首版不同预处理Unsupported保留为源限制，平台可做显式层级的方法比较而不冒充同张量比较。

没有修改交付项目或本副本，未新建生产事实、重复Schema/Owner或默认外部后端。剩余正式公共合同/实际HALCON公开桥、每任务模型数据/阈值、真实并发与部署/WPF验证按原指导继续。

<a id="aoi-component-solder-source-adoption"></a>
## 2D元件与3D量测的定向方法接收 — 2026-09-29

源[2D检测器开发指导](project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/2D检测器开发指导.md)由057B作者定向复读§1、§3.0–3.3、§3.5–6及多件/替代料/H11增量；采纳本体/电极/脚肩/脚端分开、单边估计、完整替代组、leveling不改高度和失败语义。平台唯一正文[057B执行方法](<../process-guides/guidance/06-domains/DEV-DOM-057B_AOI Component Pin Lead Polarity OCR开发指导.md#aoi-component-method>)进一步补固定见证域与三态界、独立参考不吞偏位、完整关联/候选抑制、形状对称与极性、稳定针序和视觉错料边界。

源[3D检测与量测开发指导](project-snapshots/PCBA-AOI/20260927/original/docs/40-development/40-vision/3D检测与量测开发指导.md)，SHA-256 `7eb370559f487749609cb645556791a0bf44f7a96bb23e6d84ac30bbc339c122`。本轮明确只读1–79行的检测器/输入/策略及本体方法起始，大输出后段截断不称全部实现段已审。平台[057C §6](<../process-guides/guidance/06-domains/DEV-DOM-057C_AOI Solder Joint与Pre_Post Reflow开发指导.md#aoi-solder-method-implementation>)结合竞品原件/官方说明补独立datum、本体模型量、脚上表面与底面间隙、D/W、焊料支持/分位/有限积分、局部桥/多视/前后对比，公共几何单一落在[031 §12](../shared-modules/guidance/04-metrology/DEV-MET-031_通用计量引擎开发指导.md#plane-height-offset-relations)。

两源的私有API/状态/SQLite或权限实现、硬件控制、默认阈值、旧技术版本与已有测试/资格成绩均不迁入。源字节/hash及实际范围见[元件读集](../../.work/aoi-component-method-20260929/sources.json)和[焊点读集](../../.work/aoi-solder-method-20260929/sources.json)；资料仍原位只读，不改客户项目或复制第二活动指导。新内容仍DocMapped/DesignReview，精确合同、公共API、真实材料/图像和工业资格按原Owner继续。
