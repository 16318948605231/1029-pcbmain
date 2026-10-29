# 开发文档导航

本目录是 [唯一项目入口](../PROJECT_ENTRY.md) 下的开发指导集合。当前先完善文档，再按批准范围实施；历史状态和原 220 份文档数量不代表本轮重新批准。

## 从哪读起

| 你要找什么 | 去哪里 |
|---|---|
| **平台全景**：分层、能力构成、数据模型、运行链、竞品关系 | **[PLATFORM-ARCHITECTURE.md](PLATFORM-ARCHITECTURE.md)** |
| **文档体系本身**：有哪些文档族、哪份是权威、怎么检索 | **[DOCUMENTATION-ENTRY.md](DOCUMENTATION-ENTRY.md)** |
| 阶段与进度 | [PROJECT_ENTRY.md](../PROJECT_ENTRY.md) → [PROJECT_PROGRESS.md](../PROJECT_PROGRESS.md) |
| 按议题查权威 | 下表 |

## 按议题查权威位置

| 查阅内容 | 现有权威位置 |
|---|---|---|
| 阶段与文档完成标准 | [DEV-GOV-001](01-governance/DEV-GOV-001_开发指导体系总则.md)、[DEV-GOV-008](01-governance/DEV-GOV-008_质量门禁与Acceptance标准.md) |
| 规则优先级与历史资料 | [DEV-GOV-002](01-governance/DEV-GOV-002_文档权威与变更控制.md)、[DEV-GOV-014](01-governance/DEV-GOV-014_活动基线与历史文档使用规则.md) |
| 独立 DLL / 控件 | [DEV-GOV-005](01-governance/DEV-GOV-005_模块独立性与复用标准.md) |
| 研究与竞品证据 | [DEV-GOV-006](01-governance/DEV-GOV-006_外部实现与GitHub研究标准.md) |
| Codex 任务、成本、并行与心得对应位置 | [DEV-GOV-007](01-governance/DEV-GOV-007_AI编码与自动化开发标准.md) |
| AsunImage / HALCON 使用边界 | [DEV-VIS-020](<shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>) |
| HALCON 26.05 算子资料 | [`halcon算子手册/operators`](../halcon算子手册/operators/) |
| 完全独立模块架构与逐项指导 | [52项候选及准入审查](independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md)、[会话登记](independent-modules/MODULE-INDEX.md) |
| 72 个功能卡的 AI 路线与数据证据 | [DEV-AI-064](<shared-modules/guidance/07-ai/DEV-AI-064_逐任务AI选型与证据矩阵开发指导.md>) |
| 平台级 AI 路线与三态仲裁语义 | [DEV-AI-065](<shared-modules/guidance/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md>) |
| 功能卡 Contract/Schema/State/Owner 绑定 | [DEV-CONTRACT-002](<13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md>) |
| UI、三语、提示、状态栏 | [DEV-UI-040](<shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>) |
| **色板、图标、排版、动效、无障碍、组件状态矩阵** | [DEV-UI-047](<shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md>) |
| **AI 三态结论、置信度与解释的界面呈现** | [DEV-UI-048](<shared-modules/guidance/05-ui/DEV-UI-048_AI结论的界面呈现规范.md>)、[DEV-AI-065](<shared-modules/guidance/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md>) |
| 页面规划与离线载图 | [DEV-UI-041](<shared-modules/guidance/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md>)、[DEV-UI-042](<shared-modules/guidance/05-ui/DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md>) |
| **一键编程流程、效率基线与衡量方法** | [DEV-AI-062](<shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md>)（P0–P7 流程与 §6.1 效率基线）、各 PG 的"快速编程专项"节 |
| **标准资产库、元件/模板匹配与继承** | [SM-015](<shared-modules/modules/SM-015_reference-library.md>)、[PKG-034 §6–12](<shared-modules/packages/PKG-034_ReferenceLibrary.md>)（匹配/继承/传播）、[PKG-036 §6](<shared-modules/packages/PKG-036_QuickProgramming.md>)（编排与写入交接） |
| **程序草稿、发布与激活** | [SM-016](<shared-modules/modules/SM-016_program-package.md>)、[PKG-035](<shared-modules/packages/PKG-035_ProgramPackage.md>) |
| 全部既有开发文档 | [DEV-PLAN-000 文档地图](09-development-plan/DEV-PLAN-000_开发指导文档地图.md) |

Master 是便于阅读的汇总，不是另一套权威。竞品和用户心得的原文留在 references，实际规范在上述对应指导中维护。

## 当前设计体系

- [平台设计基线](00-baseline/PLATFORM-DESIGN-BASELINE.md)：方向、边界、部署及成熟度。
- [公共独立模块](shared-modules/README.md)：通用软件/视觉及PCB/PCBA共享能力。
- [制程与机台指导](process-guides/README.md)：工艺专用功能、操作、恢复和验收；[设备细化](process-guides/device-specs/README.md)归属同一目录。
- [接口交接](shared-modules/INTERFACE-MAP.md)和[端到端链路](process-guides/END-TO-END-FLOWS.md)：资源/状态/事实责任及失败恢复。
- [权威来源与采纳](00-baseline/REQUIRED-REPOSITORY-AUTHORITIES.md)和[外部条件](00-baseline/OPEN-GATES.md)：事实不足时的明确边界。

SM/PG是DesignReview；迁移的原指导按DocMapped逐项绑定。原DEV/FS/Page ID不变，当前位置与原路径见文档地图；原02～08、12、14-page目录只留位置索引。原型/历史进度与资料归档不会自动变成当前生产授权。
