# 开发文档体系总入口

> 本页是**文档体系本身**的总入口：说明有哪些文档族、各自职责与权威级别、怎么按问题找到唯一权威、以及哪些目录是历史索引。
> 它是**导航与说明**，不定义任何可实施语义。任何实现细节以对应分区的唯一权威文件为准。

- 文档 ID：`DOC-ENTRY-001`
- 版本：`0.1.0`；日期：2026-10-29
- 状态：`DesignReview` — 导航说明，非实施准入
- 配套：[平台架构与简介](PLATFORM-ARCHITECTURE.md)（全景与分层）、[项目入口](../PROJECT_ENTRY.md)（状态与进度）

---

## 0. 三层阅读法

| 层 | 文件 | 回答什么 |
|---|---|---|
| **我该做什么** | [AGENTS.md](../AGENTS.md) | 工程规则：能做什么、不能做什么、谁写哪里 |
| **项目现在什么状态** | [PROJECT_ENTRY.md](../PROJECT_ENTRY.md) → [PROJECT_PROGRESS.md](../PROJECT_PROGRESS.md) → [TASK-PLAN.md](../TASK-PLAN.md) | 阶段、进度、任务拆分与逐项状态 |
| **技术上怎么设计** | [PLATFORM-ARCHITECTURE.md](PLATFORM-ARCHITECTURE.md) | 分层、能力构成、数据模型、运行链、竞品关系 |
| **文档在哪、哪份是权威** | **本页** | 文档族、职责边界、检索路径 |

> 接续一个新会话：先读 `AGENTS.md` → `PROJECT_ENTRY.md` → 本页 → 目标分区权威。
> **不要靠聊天摘要判断当前工作**（AGENTS.md §1）。

---

## 1. 文档体系全貌

### 1.1 规模（实测）

| 分区 | 份数 | 行数 | 性质 |
|---|---|---|---|
| `docs/independent-modules/` | 54 | 93,380 | **核心**：52 份模块指导（平均 1790 行，最长 3276 行） |
| `docs/process-guides/` | 194 | 36,539 | 23 PG + 制程公共指导 + 69 份 FS 中的 44 份 + 11 份制程 UI-PCS + 87 份设备规格 |
| `docs/shared-modules/` | 184 | 29,975 | 28 SM + 62 PKG + 91 份公共指导（含 25 份 FS、15 份公共 UI-PCS）+ 索引 |
| `docs/09-development-plan/` | 20 | 7,118 | 实施顺序、依赖 DAG、任务模板、文档地图 |
| `docs/references/` | 15 | 7,517 | 官方资料、GitHub 基线、竞品证据映射、用户心得 |
| `docs/00-baseline/` | 11 | 3,529 | 平台设计基线、权威来源、外部门、历史架构源（2,992 行为历史架构原文） |
| `docs/13-contract-candidates/` | 2 | 800 | 精确 Contract/Schema/State/Owner 候选 |
| `docs/01-governance/` | 15 | 987 | **治理规则**（DEV-GOV-001…015） |
| `docs/10-audit/` | 16 | 325 | 对抗式审计**结论简报**（每份约 20 行，非详报） |
| `docs/01-validation/` + 10 个历史索引目录 | 11 | 262 | 位置索引与历史 Smoke 注册表（见 §3.2） |
| `docs/README.md` | 1 | 37 | 议题导航 |
| **docs/ 合计** | **523** | **180,469** | 不含 MASTER 汇编产物 |

`docs/MASTER_ALL_DOCUMENTS.md` 是**便捷汇编产物**（由 `tools/build_master.py` 生成，`.gitignore` 排除，不进版本库），**不是权威**。

> **计数陷阱**：5 份 DEV 文档的原始文件名含 `/`（如 `DEV-UI-042_视觉/3D工作区与ROI交互开发指导.md`），在 Git/Windows 上表现为**目录**。按 `find -name` 统计的文件名计数会漏掉它们——本表按实际文件递归统计。

### 1.2 ID 命名空间

按**文档 ID** 统计（`docs/` 下 523 份 md 中 362 份带文档 ID）。

| 家族 | 数量 | 含义 | 位置 |
|---|---|---|---|
| `FS-xxx` | 69 | 功能卡：逐功能的算法与处理链 | `*/guidance/12-function-specs/` |
| `PKG-xxx` | 62 | 能力包（迁移映射，**不是**独立模块数） | `shared-modules/packages/` |
| `DEV-DOM-xxx` | 29 | 领域指导（PCB/PCBA 工艺语义） | `*/guidance/06-domains/` |
| `SM-xxx` | 28 | 模块目录索引 | `shared-modules/modules/` |
| `UI-PCS-xxx` | 26 | 页面合同：职责、命令、八态、验收 | `*/guidance/14-page-contracts/` |
| `PG-xxx` | 23 | 制程包 | `process-guides/processes/` |
| `DEV-PLAN-xxx` | 17 | 研发计划、依赖 DAG、文档地图 | `09-development-plan/` |
| `AUD-xxx` | 16 | 审计结论简报 | `10-audit/` |
| `DEV-GOV-xxx` | 15 | 治理规则、门禁、变更控制 | `01-governance/` |
| `DEV-VIS-xxx` | 15 | 视觉公共指导 | `shared-modules/guidance/03-vision/` |
| `DEV-PLT-xxx` | 9 | 平台公共指导 | `shared-modules/guidance/02-platform/` |
| `DEV-UI-xxx` | 9 | UI 公共指导（040…048） | `shared-modules/guidance/05-ui/` |
| `DEV-AI-xxx` | 6 | AI 公共指导（060…065） | `shared-modules/guidance/07-ai/` |
| `DEV-MET-xxx` | 5 | 计量公共指导 | `*/guidance/04-metrology/` |
| `DEV-QLF-xxx` | 5 | 资格公共指导 | `shared-modules/guidance/08-qualification/` |
| `REF-xxx` | 8 | 外部参考与证据映射 | `references/` |
| `DEV-CONTRACT-xxx` | 2 | Contract/Schema/State/Owner 绑定 | `13-contract-candidates/` |
| `PLATFORM-*` / `ARCH-*` / `GATE-001` | 若干 | 平台级汇总与历史架构源 | `00-baseline/` 等 |

**`IM-xxx` 不是独立文档命名空间**——52 个独立模块的编号只出现在 `MODULE-INDEX.md` 与 7 份指导的头部；其文档 ID 是 `DEVELOPMENT-GUIDE.md`，按目录名定位（`docs/independent-modules/<模块键>/`）。

---

## 2. 权威层级

```
Architecture      边界、职责、关系
   ↓
Contract / Schema 数据结构、兼容与传输/持久化形状
   ↓
State / Owner     谁可以读/写/提交/激活
   ↓
Development Guide / FS   算法、流程、参数、UI、性能、异常、代码任务切片
   ↓
Test / Qualification      证明实现满足上述约束
```

**下层不得反向定义上层事实。** 发现冲突必须阻断并提交 ADR/Contract 变更（[DEV-GOV-002](01-governance/DEV-GOV-002_文档权威与变更控制.md)）。

| 权威级别 | 含义 | 例子 |
|---|---|---|
| **唯一权威** | 冲突时以其为准 | `DEV-UI-047` 色板、`DEV-AI-065` 三态语义、`DEV-VIS-021` 算子决策 |
| **分区权威** | 在其分区内唯一 | 52 份 IM 指导、23 份 PG、69 份 FS、26 份 UI-PCS |
| **索引 / 导航** | 只指路，不定义 | 本页、`docs/README.md`、DEV-PLAN-000、各 `SM-xxx` 目录页 |
| **汇编 / 历史** | 可读，非权威 | `MASTER_ALL_DOCUMENTS.md`、`docs/10-audit/` 简报、旧 DEV/FS 位置索引 |
| **外部参考** | 证据，不是规范 | `docs/references/`、竞品原件、HALCON 算子手册 |

---

## 3. 目录地图

### 3.1 活的目录（有实际内容）

```
docs/
├── PLATFORM-ARCHITECTURE.md      ← 平台架构与简介（全景总览）
├── README.md                     ← 开发文档导航（议题 → 权威位置）
├── independent-modules/          ← 52 个独立模块指导 + INDEPENDENT-MODULE-ARCHITECTURE + MODULE-INDEX
├── shared-modules/
│   ├── README.md                 ← 公共模块总目录
│   ├── MODULE-CATALOG.md         ← 迁移映射（旧 62 PKG ↔ 新模块）
│   ├── INTERFACE-MAP.md          ← 生产者/消费者与权威绑定索引
│   ├── modules/                  ← SM-xxx 模块目录页（索引层）
│   ├── packages/                 ← PKG-xxx 能力包
│   ├── guidance/                 ← 02-platform / 03-vision / 04-metrology / 05-ui /
│   │                                06-domains / 07-ai / 08-qualification /
│   │                                12-function-specs / 14-page-contracts
│   └── prototypes/               ← 交互评审原型（HTML，不作 WPF 证据）
├── process-guides/
│   ├── README.md                 ← 制程与机台总目录
│   ├── END-TO-END-FLOWS.md       ← 端到端运行链
│   ├── processes/                ← PG-001…PG-023
│   ├── guidance/                 ← 制程公共指导 / FS / UI-PCS
│   ├── device-specs/             ← 设备能力参考
│   └── prototypes/
├── 01-governance/                ← DEV-GOV-001…015
├── 09-development-plan/          ← DEV-PLAN-000…016
├── 13-contract-candidates/       ← 精确 Contract 候选
├── 00-baseline/                  ← 平台设计基线、权威来源、OPEN-GATES、历史架构源
├── 10-audit/                     ← 对抗式审计结论简报
├── references/                   ← 官方资料 / 开源 commit 基线 / 竞品证据映射 / 用户心得
└── MASTER_ALL_DOCUMENTS.md       ← 汇编产物（非权威，不进版本库）
```

### 3.2 历史索引目录（只留位置映射，不维护活动副本）

`docs/02-platform/`、`03-vision/`、`04-metrology/`、`05-ui/`、`06-domains/`、`07-ai/`、`08-qualification/`、`12-function-specs/`、`14-device-specs/`、`14-page-contracts/` 这 **10 个目录当前各只含 1 个 `README.md`**（合计 222 行），内容是"原文件 → 当前位置"的对照表。**活动指导一律在 `shared-modules/guidance/` 或 `process-guides/guidance/` 下。**

`docs/01-validation/SMOKE-REGISTRY.md` 是**代码时期的历史注册表**，40 行，所有条目的执行证据列均为 "Source registered; execution not claimed"。当前仓库为纯文档状态，**该表不反映任何运行证据**。

---

## 4. 按问题检索

| 你要解决的问题 | 去哪里找（唯一维护位置） |
|---|---|
| 模块怎么实现 | `docs/independent-modules/<模块>/DEVELOPMENT-GUIDE.md` |
| 52 个模块是什么、依赖方向 | [INDEPENDENT-MODULE-ARCHITECTURE](independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md) |
| 模块的会话登记与状态 | [MODULE-INDEX](independent-modules/MODULE-INDEX.md) |
| 某工序怎么实现 | `docs/process-guides/processes/PG-xxx.md` |
| 某功能卡的算法链 | `*/guidance/12-function-specs/FS-xxx.md` |
| 页面职责、命令、八态、验收 | `*/guidance/14-page-contracts/UI-PCS-xxx.md` |
| 视觉算子怎么选 | [DEV-VIS-021](shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md) |
| AsunImage 边界 | [DEV-VIS-020](shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md) |
| 色板、图标、排版、动效、无障碍 | [DEV-UI-047](shared-modules/guidance/05-ui/DEV-UI-047_视觉设计系统规格.md) |
| AI 三态语义 | [DEV-AI-065](shared-modules/guidance/07-ai/DEV-AI-065_AI能力路线与三态仲裁规范.md) |
| AI 结论在界面怎么呈现 | [DEV-UI-048](shared-modules/guidance/05-ui/DEV-UI-048_AI结论的界面呈现规范.md) |
| 一键编程流程与效率基线 | [DEV-AI-062](shared-modules/guidance/07-ai/DEV-AI-062_自动编程与ProgramSynthesis开发指导.md) + 各 PG "快速编程专项"节 |
| 人因度量与基线 | [DEV-UI-045](shared-modules/guidance/05-ui/DEV-UI-045_操作员工作流简化与人因开发指导.md) + 各 PG "人因登记"节 |
| 实施准入标准 | [DEV-GOV-010](01-governance/DEV-GOV-010_实施级规格唯一标准.md) |
| 实施顺序与依赖 DAG | [DEV-PLAN-001](09-development-plan/DEV-PLAN-001_研发实施步骤与并行开发计划.md)、[DEV-PLAN-014](09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md) |
| 第一条可运行纵向链 | [DEV-PLAN-015](09-development-plan/DEV-PLAN-015_从仓库零点启动第一条可运行纵向切片.md) |
| 全部文档 ID → 当前位置 | [DEV-PLAN-000](09-development-plan/DEV-PLAN-000_开发指导文档地图.md) |
| 资源与状态谁负责 | [INTERFACE-MAP](shared-modules/INTERFACE-MAP.md) |
| 端到端链路与失败恢复 | [END-TO-END-FLOWS](process-guides/END-TO-END-FLOWS.md) |
| 缺失事实与外部门 | [OPEN-GATES](00-baseline/OPEN-GATES.md) |
| 外部资料、竞品证据、开源基线 | [references/](references/)、[REF-006](references/REF-006_制程与公共模块的竞品证据映射.md) |
| HALCON 算子语义 | [`halcon算子手册/operators`](../halcon算子手册/operators/)（2634 份） |

---

## 5. 质量门禁与自动校验

文档不是靠人读维护的，由 `tools/` 下的脚本持续校验，并已接入两个 GitHub Actions workflow。

| 脚本 | 校验什么 |
|---|---|
| `validate_docs.py` | 全域文档完整性：ID 唯一、链接可达、功能卡映射、DAG 无环、消费者映射 |
| `validate_module_guides.py` + `test_validate_module_guides.py` | 52 份模块指导的状态标记与 DEV-GOV-010 §3.1 必备元素；含负例（灵敏度测试） |
| `validate_ui_palette.py` + `test_validate_ui_palette.py` | DEV-UI-047 色板对比度（**从文档解析，不持副本**）；含负例 |
| `validate_ui_presentation.py` + `test_validate_ui_presentation.py` | DEV-UI-048 与 DEV-UI-047 / DEV-AI-065 / IM-047 的一致性；含负例 |
| `validate_human_factors_registration.py` | 23 PG + 26 UI-PCS + DEV-UI-045 §7 的人因登记完整性 |
| `validate_icon_accessibility_coverage.py` | 52 模块 + 26 UI-PCS 的图标可访问性覆盖 |
| `validate_page_contracts.py` | 页面合同结构与命令/对象绑定 |
| `validate_solution_layout.py` / `validate_wpf_shell.py` / `validate_function_bindings.py` | 解决方案布局、WPF 外壳与功能绑定 |
| `validate_repository_policy.py` / `validate_project_boundaries.py` / `validate_contract_candidates.py` | 仓库策略、项目边界、Contract 候选 |
| `validate_planning_crosslinks.py` / `validate_topic_index.py` / `validate_repository_authorities.py` | 计划交叉链接、议题导航、权威来源 |
| `validate_ci_prerequisites.py` | **CI 前置清单完整性**（当前 22 个脚本） |
| `build_master.py` / `version_baseline_audit.py` | 汇编产物生成、历史技术引用审计 |

**门禁的设计纪律**（来自实践教训）：

1. **校验器不得持有文档副本**——色板校验器初版把色值硬编码在脚本里，改坏文档只会报"值不在文档中"而非"对比度不足"。改为**从文档解析**后才成为真检查。
2. **校验器必须有负例测试**——`test_*.py` 用故障注入证明它能抓到问题，而不是"看似通过"。
3. **改文档后必须跑完整门禁**，不是只跑新增那一个。批量改动尤其如此。

---

## 6. 外部参考与证据纪律

### 6.1 参考资料分布

| 位置 | 内容 | 是否进版本库 |
|---|---|---|
| `docs/references/official/` | 10 类官方资料（HALCON、OPC UA、DevExpress、NIST、PostgreSQL、Windows…） | 是 |
| `docs/references/open-source/` | **31 个开源项目，按固定 commit SHA 归档并含 LICENSE** | 是 |
| `docs/references/user-notes/` | 3 份用户心得与研究结论 | 是 |
| `docs/references/competitors/` | 竞品原件 PDF（按 SHA-256 去重） | **否**（`.gitignore` 排除，本地保留） |
| `docs/references/project-snapshots/` | 交付项目快照 | **否**（同上） |

### 6.2 引用纪律

- 竞品研究必须区分**直接观察 / 推断 / 未知**，引用原件位置、页码与版本；营销、截图与模拟数据**不能证明**内部算法或生产能力。
- 外部实现只作**证据不作权威**；复制代码须定位来源/版本、确认许可、核对目标框架，并通过本模块编译、Golden/Replay 与异常/资源验收。
- 缺失的领域事实、阈值、坐标、单位、设备行为与验收值记为**待决项**，不编造。

---

## 7. 已完成的成熟度与当前状态

| 阶段 | 状态 | 依据 |
|---|---|---|
| 文档内容级审查 | **完成** | 302 份逐项判定（51 Pass + 1 Gap 已修），见 [T2-REVIEW-LEDGER.md](../T2-REVIEW-LEDGER.md) |
| 对抗式审计 | **完成** | 16 份结论简报（AUD-060…075），含审计器自身的故障注入测试 |
| 质量提升 P1–P5 | **完成** | 视觉设计系统、效率基线、AI 呈现规范、人因契约、图标可访问性全覆盖 |
| 规则精简 | **完成** | AGENTS.md 去冗余并统一标点 |
| 代码实现 | **未开始** | 仓库为纯文档状态；`src/`、`tests/` 既有脚手架已整体移除 |

> **文档数量、Master、Registry 与审计 PASS 不等于当前范围全部获批。** 草案、待确认、批准、实现、测试与生产验收分别记录。

---

## 8. 维护本页的规则

1. **本页只做导航与说明**——新增可实施语义时写进对应分区权威，本页只加链接。
2. **规模数字需实测**——更新时重新统计，不凭印象。
3. **历史索引目录不复活**——活动指导一律写在 `shared-modules/guidance/` 或 `process-guides/guidance/`。
4. **新增文档族必须同时**：登记 ID 前缀与数量、说明职责与权威级别、接入 `validate_docs.py` 覆盖范围。
5. **本页与 [PLATFORM-ARCHITECTURE.md](PLATFORM-ARCHITECTURE.md) 分工**：架构页讲"系统长什么样"，本页讲"文档怎么组织"。

---

## 9. 自审

| 检查 | 结论 |
|---|---|
| 是否新造权威？ | 否。本页只做导航与说明；§2 明确各级权威的既有归属 |
| 数字是否实测？ | 是。§1.1 规模、§1.2 命名空间数量均由命令统计得出 |
| 历史目录是否如实标注？ | 是。§3.2 明确区分活目录与位置索引；`SMOKE-REGISTRY` 明确标为历史、不反映运行证据 |
| 是否重复其它文件内容？ | 否。功能职责、架构语义、规则均只给链接 |
| 与既有导航是否冲突？ | 否。本页是 `docs/README.md` 的**上位体系说明**（README 按议题查，本页按体系查），两者一致 |
