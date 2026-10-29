# 平台权威来源采纳与缺口边界

- 文档 ID：`GATE-001`；版本：`1.2.0`；日期：2026-09-28；状态：`DesignReview`
- 职责：记录外部权威来源、平台适用范围、缺口和关闭证据；不定义第二套Schema/Owner/状态/事件。
- 唯一入口：[PROJECT_ENTRY](../../PROJECT_ENTRY.md)。实际受影响切片见[开放条件](OPEN-GATES.md)。

## 1. 本轮核对结论

旧准备包引用了AOI仓库的权威路径，却未将适用契约接入本平台。2026-09-27核对后，来源已按REF-008保存为本地只读参考；2026-09-28重新核对下列10项，原件副本与既有来源清单的SHA-256全部一致，未修改AOI项目或归档原件。文件可读不等于平台已批准，未将这些副本放入正式contracts路径。**本仓库无远端配置，不虚构远端 commit、权限或 CI 状态**（2026-10-28 审核更正：原文写作"无本地 Git"，与当前仓库有 Git 元数据的事实不符）。

旧文中“任何未解析文件均阻断所有开发”“DEV-PLT-002缺失不得决定拆分”不再作为全平台总门。用户已授权本平台架构/模块规划，本平台DEV-GOV-005负责独立性规范。生产字段、状态、设备副作用等仍只在对应正式契约批准后实施，门槛没有因设计进度降低。

## 2. 逐项来源与处理

第二列保留旧准备包路径用于来源定位，不是要求重建AOI目录。第三列“未接入”仅表示未正式采纳；10项本地副本均已存在并由§3直接链接。四份来源指导应对照本平台已有权威，不复制另一份活动规范；六项契约/目录仍需逐字段采纳。

| 标识 | 原准备包预期平台路径/来源 | 本地现状 | 平台采用方式与影响 |
|---|---|---|---|
| DEV-ARC-005 | `docs/40-development/00-standards/权威状态角色消息与判定所有权规范.md` | 平台未接入；AOI源文件存在 | 状态/Owner/角色：已读身份、机判、复判、处置分权部分；AOI命名与角色审批不直接继承。平台需逐工序确认Owner/状态，之后在唯一契约位置采纳。 |
| DEV-PLT-001 | `docs/40-development/00-standards/AsunVisionPlatform架构与模块目录.md` | 平台未接入；AOI源文件存在 | 模块边界：已读目标/边界和架构概述。公共视觉与AOI应用分开可借鉴；既定命名空间、部署和模块数不复制为平台决定。对应本平台PLATFORM-DESIGN-001、SM目录。 |
| DEV-PLT-002 | `docs/40-development/00-standards/可复用模块独立性与UI分离标准.md` | 平台未接入；AOI源文件存在 | 独立性/UI分离：已读§1–3及交付边界。可引用/构建/测试/发布/集成原则已由本平台DEV-GOV-005维护；不再把未复制该外部文档当作禁止本平台规划拆分的总阻断。 |
| DEV-DAT-002 | `docs/40-development/70-operations/维护健康备份升级开发指导.md` | 平台未接入；AOI源文件存在 | 维护/备份/升级：已读目标、健康接口与恢复边界。AOI签名/SCM/硬件假设不自动移植；本平台SM-005/028定义职责，现场RPO/RTO和存储方案未冻结。 |
| contracts/v1/schema/events-catalog.schema.json | `contracts/v1/schema/events-catalog.schema.json` | 平台未接入；AOI源文件存在 | 事件结构：已解析根required/properties/$defs。来源$id为AOI域；目录的producer、transactionBoundary、outboxOwner须平台逐项确认，不能只改前缀。 |
| contracts/v1/catalog/events.v1.json | `contracts/v1/catalog/events.v1.json` | 平台未接入；AOI源文件存在 | 事件目录：已解析catalogVersion=1.2.0及事件生产/消费/去重/事务字段；MotionGateway/Orchestrator等为AOI事实，平台未采纳具体枚举。 |
| contracts/v1/schema/cross-module-flow-registry.schema.json | `contracts/v1/schema/cross-module-flow-registry.schema.json` | 平台未接入；AOI源文件存在 | 跨模块流程：已解析根字段；sourceDocumentId固定DEV-STD-006并依赖多个AOI目录，须审查依赖闭包及平台适用性。PLATFORM-FLOW-001不替代该Schema。 |
| contracts/v1/schema/recipe-manifest.schema.json | `contracts/v1/schema/recipe-manifest.schema.json` | 平台未接入；AOI源文件存在 | 程序与Runtime：已解析必需字段，含boardModel/libraries/decisionGraph/审批和能力等。平台使用既有C候选做差异评审，不新增平行Recipe模型。 |
| contracts/v1/schema/evidence-manifest.schema.json | `contracts/v1/schema/evidence-manifest.schema.json` | 平台未接入；AOI源文件存在 | 证据/提交：已解析必需字段及定义入口，含boardRun/resultCommit/machineDecision/replay/回执。提交与回放职责可参考，具体字段和事务协议未批准。 |
| contracts/v1/schema/plugin-manifest.schema.json | `contracts/v1/schema/plugin-manifest.schema.json` | 平台未接入；AOI源文件存在 | 插件声明：已解析根结构，含能力、签名、sandboxPolicy/resourceBudget；字段存在不证明隔离。普通独立DLL不自动等于需动态插件管理。 |

## 3. 固定来源与读取范围

最初读取日期2026-09-27，下列链接现指向已固定的本地副本，原始绝对路径保留于[来源清单](../references/project-snapshots/PCBA-AOI/20260927/source-manifest.json)。2026-09-28核对整个文件哈希后，使用本机jsonschema 4.26.0/referencing 0.37.0对5份Schema执行Draft 2020-12元Schema检查，检查55个本地$ref均可解析；未发现外部$ref或嵌套$id。36项事件目录按对应Schema并开启FormatChecker验证，未发现结构错误。这只验证来源结构/引用及该目录实例，不证明业务语义、其它实例、AOI实现或平台采纳；不得据此批准角色、事件Owner或生产行为。来源变化仍须差异审核，不自动更新批准状态。

复现命令为`python .work/schema-source-review-20260928/verify_source_schemas.py`（[脚本](../../.work/schema-source-review-20260928/verify_source_schemas.py)）。复核发现原Python环境未注册date-time检查器，不能仅构造FormatChecker就宣称时间格式已验证；本轮在该任务目录暂存rfc3339-validator 0.1.4后重新执行全部来源检查，并先断言合法时区值可接受、`not-a-timestamp`必须拒绝。暂存wheel的PyPI SHA-256为`24f6ec1eda14ef823da9e36ec7113124b39c04d50a4d3d3a3c2859577e7791fa`，未改变全局环境或平台产品依赖。脚本同时复现PKG-035的9项发布Schema对照及1项非法时间负对照；格式检查器缺失时直接失败，不静默跳过。

- **DEV-ARC-005**：[权威状态角色消息与判定所有权规范.md](<../references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/权威状态角色消息与判定所有权规范.md>), 版本：1.1。SHA-256：`6c4a646eaace341fbd2a6c9fa139fd5b4997b60917e3d62d86f5f8410a78c1db`。
- **DEV-PLT-001**：[AsunVisionPlatform架构与模块目录.md](<../references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/AsunVisionPlatform架构与模块目录.md>), 版本：1.2。SHA-256：`7f7467d64e4ab374e2f648d94b98f6b331ed9554385f34352063b7108379e927`。
- **DEV-PLT-002**：[可复用模块独立性与UI分离标准.md](<../references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/00-standards/可复用模块独立性与UI分离标准.md>), 版本：1.4。SHA-256：`df8afb4a38924756ee6084af6812822959a6857c66065835616535a767434b93`。
- **DEV-DAT-002**：[维护健康备份升级开发指导.md](<../references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/70-operations/维护健康备份升级开发指导.md>), 版本：1.9。SHA-256：`bce05e9c4b5eadc91a6ce74fa20456fd1302627cb1431bb9c5a2b9ace02d9fd4`。
- **contracts/v1/schema/events-catalog.schema.json**：[events-catalog.schema.json](<../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/events-catalog.schema.json>), 版本：v1路径；具体内容按下列哈希。SHA-256：`c3c45f99e5c19c5e8316baca6a60da92f6a325bc92b2f17268ea622bdfd0f290`。
- **contracts/v1/catalog/events.v1.json**：[events.v1.json](<../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/catalog/events.v1.json>), 版本：1.2.0。SHA-256：`dfe12c0439ec3f21e04a5e4e38f592ee6539bee59515a1226bac4314826ac440`。
- **contracts/v1/schema/cross-module-flow-registry.schema.json**：[cross-module-flow-registry.schema.json](<../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/cross-module-flow-registry.schema.json>), 版本：v1路径；具体内容按下列哈希。SHA-256：`e121ceaa86188c7da550a9dea828d643279c8ee93a572e47c42360f22ada5e93`。
- **contracts/v1/schema/recipe-manifest.schema.json**：[recipe-manifest.schema.json](<../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/recipe-manifest.schema.json>), 版本：v1路径；具体内容按下列哈希。SHA-256：`016a8558756c0464d5545c5757bf2f5fd7bdca10f2b170816734f2809cb4b312`。
- **contracts/v1/schema/evidence-manifest.schema.json**：[evidence-manifest.schema.json](<../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/evidence-manifest.schema.json>), 版本：v1路径；具体内容按下列哈希。SHA-256：`981e1f71948e21bafe1f0c9b4e9a58411a7720346d6d12b11b84edf66882fcf1`。
- **contracts/v1/schema/plugin-manifest.schema.json**：[plugin-manifest.schema.json](<../references/project-snapshots/PCBA-AOI/20260927/original/contracts/v1/schema/plugin-manifest.schema.json>), 版本：v1路径；具体内容按下列哈希。SHA-256：`d518c2a411f6910263031ddcd084b128b8e18db2426955036fe2559c937cf4d6`。

## 4. 唯一契约的采纳步骤

1. 从当前模块/制程切片列出真正需要的字段、状态边和事件，定位上述来源及平台已有ContractCandidate；不要先全盘搬运。
2. 写清保留、删去、泛化和制程专用的差异，以及真实生产者/消费者、资源/事务边界。规则和参考源不能偷偷取得事实写权。
3. 对范围、Owner、角色、质量判定、设备副作用、发布/恢复策略等影响产品的差异提交用户/负责人决定；无依据项保持Candidate。
4. 批准后把唯一正式资产放入既定contracts位置，并在本表登记版本、哈希、消费者、Validator和兼容策略。替换或修订既有资产，不新建同义Schema绕过。
5. 只关闭被真实证据满足的切片门槛；DocMapped、来源存在、Schema可解析、实现通过与生产验收分别记载。

## 5. 当前可以继续的工作

文档细化、官方API查阅、公共签名映射、只读样例核对、无生产权威的数学/资源原型可按具体授权开展。当前用户任务仅设计文档，不据此自动实施代码。AsunImage/DevExpress不属于本门禁，不安排兼容性/安装/授权验证。硬件SDK实现、外部CAM实际接口与已完成光板项目按用户提供条件接入。

## 6. AOI来源已在平台保存，正式采纳仍逐切片

源docs及catalog/schema/proto/golden/compat已按REF-008保存只读快照；旧表“平台未接入”现在指未作为平台正式契约接纳，不再表示本地没有副本。原源路径/hash是当时读取记录，最新副本hash在来源清单；不可回填旧hash冒充同版本。公共包重新划分后逐项比较AOI字段/Owner/状态、产品专属性和所需改动，接纳进唯一平台Contract；复制不能解除本门。

`tools/validate_repository_authorities.py`现在分别报告来源哈希、旧预期路径是否存在和采纳未验证。当前结果为10项`SOURCE_PINNED`、0项路径解析失败、0项来源完整性错误；旧预期平台路径仍未出现，不因此新造同名文件。9项定向回归检查覆盖中文/空格路径、越界路径、缺失/被改原件、重复或损坏清单，以及“来源存在/平台文件存在均不等于采纳”；来源完整性错误返回非零，未采纳仍按既有文档阶段门槛报告。

下一步由原C-01～C-08 Owner按DEV-PLAN-016顺序接纳：先身份与冻结引用，再程序闭包、计算/评价、证据提交及复判。现有字段不能仅改AOI前缀就进入平台；强制审批、签名、部署、权限和产品角色需要明确差异与决定。PKG-037和PKG-040的来源对照只完善对应包的实施语义，不另建Schema，也不自动关闭GATE-001。
