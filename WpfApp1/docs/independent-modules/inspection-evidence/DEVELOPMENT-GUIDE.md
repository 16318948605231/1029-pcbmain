# 检测证据与存储独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`G1-Core`

- 模块 ID：`IM-015`（现有来源：`PKG-040`）
- 模块键：`inspection-evidence`
- 版本：`0.3.5-prep`（定向对齐IM066 0.3.1-prep启动注册快照、同事务epoch与关闭接线；原完整范围准备结论及G1/技术桥接收保持）
- 状态：G1-Core 文档规格 `ModuleCoreImplementationReady`；G2-T1/G3-T1 技术桥指导已获主控限定内容接收，未标记 `ModuleCoreImplementationReady` 或 `ImplementationSpecificationReady`；G2/G3 与整模块产品准入仍为 `PreparationIncomplete/DesignReview`。
- 日期：2026-10-11
- 规划消费者：生产提交、回放证据、复判证据查看；第二消费者验收至少包含一个生产提交宿主和一个独立回放/复判宿主。
- 技术基线：C# / .NET 10；可选 WPF + DevExpress 25.2.3 投影；视觉输入如需解码只经 `ImageLibDotNet` 公共接口，目标 HALCON 26.05。

本页是脱离本平台也可接入的实施金标准。模块的最终目标职责仍包括结果事实提交、证据引用、回执/Manifest、保持与定向证据读取，不负责通用数据集查询、分页、快照、聚合或导出。数据库事务和文件存储由独立的 `IM-066 storage-database`（`PKG-041`）提供；本模块不拥有数据库连接池或生产对象存储根目录；可选Wpf仅拥有§15.1明确的本实例私有解码临时目录。当前首个可准入切片只允许无副作用的校验、计划和状态语义；事实提交、证据持久化、产品 Owner 映射、回执发布、租约/保持和定向存储读取均属于后续独立提交门，不能通过把它们命名为 adapter 来绕过 Core 准入。`C-01`～`C-08`、`FS-004`、`DEV-PLT-012` 的正式字段、枚举、Owner、权限和性能 Profile 获批准后，按对应门语义绑定；本页未宣称接口、后端、耐久、WPF 或生产资格已经实现。通用 Query/Export 由 `IM-045 query`（`PKG-042`）独占。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Core/Asun.Modules.InspectionEvidence.Core.csproj`；namespace：`Asun.Modules.InspectionEvidence`。预定测试工程：`tests/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Core.Tests/Asun.Modules.InspectionEvidence.Core.Tests.csproj`。上述项目尚未创建。
- 本轮文档写入范围仅本文件。未来 Gate-1 实现允许范围仅上述 Core 和测试工程目录，不能由本轮修订自动开工；后续包落点和各自允许范围见 §15.1，不挤入 Core。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 首个 Core 禁止依赖或执行：证据暂存/提交实现、对象或数据库写入、文件封口/发布、回执/Manifest 持久化、outbox、租约/保持、产品 Owner 映射、质量事实写入和任何设备/外部协议副作用。后续提交门的暂存/封口步骤只能由唯一 `CommitAsync` 内部编排，且必须独立准入，不能作为本 Core 的隐藏实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前状态：G1-Core 文档规格已于 2026-10-11 由主控按 DEV-GOV-010 §3.1 六项逐项接收，标记为 `ModuleCoreImplementationReady`。正式实现任务和代码基线绑定另行安排，本次不创建工程；事实提交/持久化门另行完成 `ImplementationSpecificationReady` 和对应 Owner/存储/恢复接收。本绑定不是实现、集成或资格通过声明。

### 首个 Core 与后续提交门

| 门 | 可实现范围 | 真实输入/输出 | 明确禁止 | 准入状态 |
|---|---|---|---|---|
| `Gate-1 Pure Core` | 规范化请求校验、证据关系/字节预算计划、幂等键冲突计划、取消/超时/排空状态语义和错误分类 | 输入为不可变描述、Profile、版本目录和只读 operation snapshot；输出为 `ValidationResult`、`StagePlan`、`CommitPlan`、`OperationStatus` 或错误分类；不产生外部副作用 | 事实写入、对象/数据库写入、租约、保持、Manifest/Receipt 发布、Owner 映射、outbox、设备/网络动作 | `ModuleCoreImplementationReady`；文档规格已接收，未实现或运行验证 |
| `Gate-2 Evidence Submission` | 依据上游 Owner 冻结的事实与映射执行 Stage/Seal/Publish/Commit、保存证据、生成 Manifest/Receipt、恢复未知操作和外发意图 | 上游生产/质量 Owner 提供冻结事实和 `CommitIdentity`；IM-066 提供受控存储端口；输出提交回执、Manifest、持久化状态和诊断 | 不得把 Gate-2 的事实写入、持久化或 Owner 映射折回 Gate-1，也不得仅改名为 adapter 取得 Gate-1 准入 | 后续独立门，未准入 |
| `Gate-3 Directed Read/Retention` | 精确 Manifest/对象读取、完整性核验、读取租约、保持/GC 协调和第二消费者接入 | 由授权 Owner 签发的精确身份/用途/版本；输出只读对象、完整性报告、租约和保持状态 | 通用查询/导出、按 latest 猜测、修改生产事实或质量放行 | 后续独立门，未准入 |

这三个门共同构成模块最终职责，但不是同一个 Core 切片。Gate-1 通过也不授权 Gate-2/3；Gate-2/3 的适配器只是技术边界，不能改变其事实写入和持久化性质。

### 上游契约与最小调用链

| 顺序 | 上游 Owner/接口 | 提供给 IM-015 的内容 | IM-015 的权限与输出 |
|---|---|---|---|
| 1. 身份与运行绑定 | C-01 身份/运行 Owner；C-02/C-03 资产、方法与版本 Owner | 完整作用域、尝试/位置来源、程序/方法/标定/模型/参数 revision 与 hash | Gate-1 仅校验引用完整性；不创建或补写产品身份 |
| 2. 事实冻结与提交授权 | C-04 生产/质量事实 Owner，C-05/C-06 授权/State Owner | 冻结的事实载荷、`CommitIdentity`、允许保存的状态、权限/用途令牌与撤回代次 | Gate-1 仅返回字段/来源校验和提交计划；Gate-2 按批准边界原样提交，不改判 |
| 3. 准入 Core | `IInspectionEvidenceCore` | 不可变请求描述、Profile、版本目录、只读 operation snapshot | 无副作用地返回 Validate/Plan/Status；不读写产品 Store，不接管流 |
| 4. 后续证据提交 | Gate-2 `IInspectionEvidenceSubmission` + IM-066 `IObjectStore`/事务能力 + 诊断/时钟端口 | 由宿主提供的流、预算、持久化和诊断端口；精确权限 | 流式核验字节、封口/持久化、登记关系/Receipt/outbox；结果未知按原身份查询 |
| 5. 追溯读取与保持 | Gate-3 `IManifestReceiptAdapter`/`IEvidenceReadAdapter` + C-05/C-06 授权 + C-07 数据主权/保持 Owner | 精确 Manifest/对象版本、读取用途和 Hold/保留策略 | 定向读取、校验和租约；查询/分页/导出另走 IM-045 |
| 6. 外部投影/交付 | IM-045 query、IM-046 integration-transport、生产/复判宿主 | 本模块公开的回执/证据引用及已批准投影/外发用途 | IM-015 不执行通用 Query/Export，不把网络 ACK 写成事实成功 |

最小调用链为：上游 Owner 冻结身份/版本/事实和权限 → Gate-1 Pure Core 纯校验并生成计划 → Gate-2（单独准入后）通过 IM-066 持久化能力保存字节并原子登记事实/回执/Manifest → 宿主按原提交身份处理未知结果 → Gate-3（单独准入后）按精确身份授权读取/保持 → IM-045 或外部宿主消费只读投影。C-01～C-08 的实际接口名和字段仍以其批准契约为准；本表说明依赖方向和最小信息，不新造替代合同。当前 Core 不需要 Gate-2/3 的存储或产品 Owner 运行时注入。

## 1. 目标与边界

### 1.1 模块职责

模块最终目标态提供以下稳定能力；其中首个可准入 Core 只覆盖第 1 项中的纯校验/计划部分及第 4 项中的纯状态语义，带有持久化或产品事实副作用的部分属于后续独立门：

1. 接受调用方已经计算出的有类型事实和证据引用，校验身份、版本、作用域、单位、完整性和授权前置条件。
2. 以流式方式接纳证据字节，计算保存字节的长度和摘要，完成格式尾部、封口、耐久和不可变发布。
3. 在同一已批准的结果事务边界内登记不可变事实、逻辑证据关系、回执和可靠外发意图。
4. 用同一提交身份提供幂等状态/回执读取、恢复扫描和未知结果解析；Core 首先只计算幂等/恢复状态，提交门再读取权威回执并执行恢复。
5. 为已知 `CommitIdentity`、`EvidenceManifest` 和单个对象提供定向只读读取、完整性校验和读取租约；不注册通用数据集或查询语法。
6. 按持久保持根、读取租约和保留政策协调读取、备份和垃圾回收；无法证明安全回收时保持对象。

### 1.2 明确禁止

- 不识别 PCB、PCBA、SPI、AOI、点胶、涂覆或任何制程目标，不创建目标/板/工单关系。
- 不计算、重算或解释视觉算法、量测、缺陷、规则、质量分母、最终质量放行或机器决定。
- 不改变 `InspectionFact`、`RuleEvaluation`、`InspectionDecision`、`MachineDecision` 的内容和质量状态；合法 `NG`、`Unknown`、`Invalid`、`NotMeasured` 可按策略保存，保存成功不等于质量通过。
- 不发相机、灯、运动、PLC、返修、出板或其它设备命令，不取得设备 SDK 句柄。
- 不根据 `latest`、文件名、相似图、当前页面、条码或时间近似补齐身份和证据。
- 不把 blob 哈希相同当成两次曝光、两个 FOV 或两个物理对象；物理去重不能合并逻辑证据关联。
- 不暴露万能 SQL、任意表名、绝对路径、连接串、数据库句柄、`IQueryable`、通用条件树、UI `Grid` 或 ViewModel 写入口；不得复制 `IM-045` 的 Query/Export 端口。
- 不把 UI、报表、缓存、AI、网络 ACK 或本地 outbox ACK 当作事实 Owner 或质量放行依据。

调用方负责流程顺序、目标关联、工艺解释、规则和质量判定、复判意见、报告语义、设备副作用、通用检索和外部协议。Gate-1 只返回计划/校验/状态值；后续门才返回模块自身持有的事实、证据、技术回执以及按明确身份取得的定向证据资料。调用方不得把 Gate-1 的 `Valid`、`Planned` 或 `CommittedCandidate` 解释为事实已提交、质量通过或设备动作已完成。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.InspectionEvidence.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"不把 UI、报表、缓存、AI 当作事实 Owner"，Core 是纯事实写入/查询模块。

**Blazor/Web**：证据浏览是 Web 端 P0 优先需求。证据图像/3D 点云通过 HTTP Range 分片加载；证据 `EvidenceRef` 引用不内联，浏览器只拿引用再按需下载；服务端按 `ObjectRef`+hash 校验字节完整性。§1 已明确"不暴露万能 SQL 或任意表名"——Web 端只通过模块公开投影端口查询。

**AI 三态仲裁与证据**：AI 推理的 `AutoResolved` 终态须在审计轨迹中附完整 `ArbitrationEvidence`，该证据包通过本模块写入；本模块是三态仲裁审计链的存储方，不执行仲裁逻辑。

**HALCON 不适用**：本模块是纯证据存储/查询模块，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 分层、Owner 与依赖

```text
生产/回放/复判应用
    └─ 唯一事实提交命令、定向读取端口、权限和领域投影
IM-015 Gate-1 Pure Core
    ├─ 证据校验、规范化和提交/恢复计划
    ├─ 幂等、取消、超时、排空的纯状态语义
    └─ 不产生产品事实、对象或数据库副作用
IM-015 Gate-2/3 后续独立门
    ├─ 事实提交、证据封口/发布、回执/Manifest 与未知恢复
    ├─ 定向读取、完整性、租约、保持和 GC 协调
    └─ 通过显式端口接入 IM-066、授权、诊断和对象存储
适配器
    ├─ 对象存储或文件适配器（字节、封口、发布、保持）
    ├─ 事务/元数据存储适配器（结果、引用、回执、outbox）
    ├─ 权限、诊断、时钟适配器
    └─ 可选 ImageLibDotNet 解码/预览适配器
```

Owner 必须在宿主装配表中唯一指定：

| 事实/动作 | Owner | 本模块权限 |
|---|---|---|
| 实体、尝试、面别、范围、因果关系 | 身份/运行 Owner（C-01） | 只读校验和保存引用 |
| 程序、方法、标定、模型、参数版本 | 资产/运行 Owner（C-02/C-03） | 只读校验和保存引用 |
| 事实内容、状态、规则结果、机器/人工决定及业务写授权 | 原生产/质量 Owner（C-04） | 唯一事实 Owner；Gate-1 只校验/计划。Gate-2 仅在 C-04 明确授权的合同边界内，经唯一 `CommitAsync` 命令提交冻结载荷，不改判、不另建事实 |
| 证据对象、Manifest、逻辑关联 | IM-015（Gate-2/3） | 后续门生成保存字节摘要、维护关系和保持；Gate-1 不拥有写权 |
| 事实提交编排与结果回执 | IM-015 Gate-2 的唯一宿主入口 `IInspectionEvidenceSubmission.CommitAsync`；C-04 保留事实 Owner | IM-015 只执行 C-04 授权的冻结提交；暂存/封口/发布是该命令内部步骤，不另设宿主可调用的提交入口 |
| 事务、元数据、对象字节与耐久机制 | IM-066 `storage-database` | 仅提供受控存储/事务能力；不拥有或改写 C-04 事实，不暴露给产品宿主作为旁路提交入口 |
| 回执、Manifest、outbox 意图 | IM-015 Gate-2；相关字段/事实语义由 C-04 与批准合同约束 | 仅在唯一 `CommitAsync` 流程内登记；adapter 不得绕过该入口或自行发布生产事实 |
| 通用查询、数据集、快照、导出用途 | `IM-045 query` / 应用 Owner（C-05/C-08） | 本模块不得注册或执行 |
| 回执、Manifest、单对象定向读取 | IM-015 | 只读校验、租约和完整性回报 |
| 设备、质量放行、复判、处置 | 对应应用/设备 Owner | 本模块无权 |

Gate-1 仅接收纯校验/计划所需的不可变描述和只读 Profile/目录，不装配存储或产品 Owner 运行时服务。Gate-2/3 获独立准入后，才可通过构造函数或显式装配接入其所需的授权、IM-066 受控对象/事务端口、诊断、时钟和版本目录。禁止静态全局容器、隐藏窗口初始化和运行时从容器动态取得未登记服务。

## 3. 公共输入与输出契约

以下字段分Owner执行：C-01/C-04/C-07业务事实、身份和政策按其批准合同映射；IM-015拥有的通用证据关系/Manifest/技术回执/根采用附录B.3/B.4/B.6唯一模块契约。模块封套不另定义业务事实Schema、不改旧产品canonical；不能因业务Owner尚未给字段而推迟模块自己的公开字段/编码。

### 3.0 首个 Pure Core 的输入与输出

Gate-1 只接收可复制的不可变描述，不接收 `Stream`、数据库连接、对象存储句柄、产品 ViewModel 或厂商类型。唯一代码形状见附录 B：`EvidenceRequest` 描述证据；`CommitDescription` 描述冻结提交；Gate-2 的 `CommitRequest` 才附带事实封套和流源。Profile、版本目录、证据关系、取消 token、显式经过时间和只读 `OperationSnapshot` 都是输入值，不由 Core 读取时钟或外部服务。输出只允许字段/来源/范围校验结果、`StagePlan`、`CommitPlan`、`OperationStatus` 和错误分类。计划不创建暂存、实算保存字节 hash、登记事实、取得租约或发布回执；后续提交门必须复核实际字节和权威持久状态。

Gate-1 的通过条件是“请求可以按规则继续”，不是“证据已保存”或“提交已成功”。任何需要读取或改变外部状态的能力，包括证据暂存、`CommitAsync`、对象封口/发布、事务提交、Manifest/Receipt 写入和定向对象读取，都不属于首个 Pure Core。

### 3.1 提交输入

本节及其后的 `CommitReceipt`、`EvidenceManifest`、`OutboxIntent` 语义属于 Gate-2/3 后续独立门。它们描述模块最终职责和上游接入所需的边界，不构成首个 Pure Core 的实现授权。

| 语义 | 类型约束 | 单位/范围/默认 | 校验与来源 |
|---|---|---|---|
| `CalculationIdentity` | 非空稳定 ID + 版本/摘要 | 字符串 1..256；无默认 | 由原计算 Owner 生成；不得用 `OperationId` 代替 |
| `CommitIdentity` | 非空稳定提交键 + 作用域 | 字符串 1..256；同作用域唯一 | C-04；首次副作用前冻结 |
| `OperationId` | 追踪 ID | 字符串 1..256；每次调用生成或由宿主传入 | 仅诊断关联，不是事实主键 |
| 事实载荷 | 已批准的强类型事实/状态 | 数值必须有限；枚举来自版本目录 | C-04/原领域 Owner；模块不重算 |
| `EvidenceDescriptor` | 逻辑对象 ID、角色、作用域、媒体类型、长度、字节摘要、来源绑定 | 长度 `0..MaxObjectBytes`；默认上限由 Profile 注入，不写代码常量 | 逻辑关联与物理 blob 分开；路径由适配器生成 |
| `EvidenceStream` | `IEvidenceContentSource`；按逻辑 ID 绑定 | 分块 `1..Profile.MaxChunkBytes` 字节；默认由 Profile | 获准接纳后才打开；宿主拥有 source，模块拥有其新打开的独占流，见 §6 |
| 版本/引用 | ID + revision + content hash | hash 必须为批准算法的固定长度；无 `latest` | C-01/C-02/C-03；缺失阻断 |
| 预期状态 | 可选 CAS 版本/修订 | 正整数；未提供只可表示已批准的新建，不授权覆盖 | 零行由领域解释为冲突/不存在/无权，不能默认成功 |
| 取消/预算 | `CancellationToken` + `OperationBudget` | 总期限 `>0`；默认由宿主 Profile | 总期限包含排队、I/O、提交、回执查询和清理余量 |

证据摘要覆盖实际保存字节。编码、压缩、加密改变字节时，原始内容摘要、保存字节摘要和语义输入摘要必须分开；不能以对象名、URI 或调用方自报摘要替代实算。长度、摘要、媒体类型、角色和源绑定必须在封口前后逐项核对。

哈希域和规范化规则必须显式命名并随版本记录。请求/幂等规范化载荷、语义事实、原始输入字节、实际保存字节、Manifest、Receipt、查询/读取证明属于不同域；相同十六进制长度或相同数值不表示跨域相等。只有在域、算法、版本和 canonical 规则全部相同且由对应 Owner 批准时才可比较；不得从对象 ID、URI、文件名或另一域摘要推导目标摘要。调用方自报摘要只能作为比较值，Gate-2/3 必须按实际字节或规范化内容重算；Gate-1 只校验声明的域/格式和已知引用，不冻结尚未批准的 canonical 规则。

**默认值规则：** 本页未给出经批准 Profile 的数字默认值。凡表中标为“由 Profile 注入”的上限、超时、TTL、队列、并发、保留和重试次数，运行时默认语义为 `ProfileRequired`：缺少有效 Profile 时返回 `IEV-CAP-006` 或 `IEV-BUDGET-012`，禁止写入隐藏常量、无限值或按后端默认值运行。单位、范围和默认值一旦由 C-04/C-07/Profile 冻结，必须随版本和摘要记录。

### 3.2 提交输出

| 语义 | 内容 |
|---|---|
| `CommitReceipt` | `CommitIdentity`、事实/修订身份、服务生成的回执 ID、提交状态、最终载荷摘要、Manifest 摘要、提交时间（UTC）和读取权限投影 |
| `EvidenceManifest` | 不可变逻辑对象、角色、作用域、保存定位摘要、媒体类型、长度、字节摘要、保持类别、来源/派生关系 |
| `CommitOutcome` | 本地枚举见附录 B；产品枚举按 C-04 显式映射，不另设 CommitStatus |
| `OutboxIntent` | 外发用途、事件身份、规范化载荷摘要、投递代次/状态；网络发送由外部交付 Owner 执行 |
| `IntegrityReport` | 每个对象和关系的检查结果、缺项、坏摘要、作用域错绑和可恢复建议 |

同一 `CommitIdentity`：同一规范化载荷返回原回执；不同载荷返回冲突且不覆盖旧事实；仍处理中返回原操作状态；响应丢失先按同身份查询，不能生成新事实。服务生成的对象 ID、回执 ID 和最终 Manifest 摘要不得要求调用方在 Begin 阶段预先填写。

Gate-2 在取得暂存额度、打开输入流或创建对象前，必须先在当前授权允许的范围内，按 `CommitIdentity`、作用域和域分离的规范化请求摘要解析原操作。相同身份/摘要只返回首次结果或原处理中状态；相同身份而摘要不同必须冲突，返回原结果仍须核对当前披露权限。传输消息身份、诊断 `OperationId` 和业务 `CommitIdentity` 不得互相替代；解析失败或结果未知时不得创建替代暂存、换键重写或把新操作当作恢复。内部恢复步骤需按原持久状态和批准协议接续，不重放整个提交流程。

### 3.3 定向读取输入与输出

本模块只接受已知身份的定向读取，不接受数据集、条件树、排序、分页、快照、聚合或导出请求。通用检索必须转交 `IM-045 query`；`IM-045` 通过已登记投影读取本模块发布的事实或证据引用。

| 输入 | 约束 |
|---|---|
| `CommitIdentity` / 回执 ID | 必须完整、带作用域和版本；未知身份返回 `NotFound` 或 `PermissionDenied`，不得按时间或 `latest` 猜测 |
| `EvidenceObjectId + ManifestRevision` | 只读取 Manifest 指定的不可变对象版本；对象 ID 不能替代逻辑来源绑定 |
| `AccessContext` | 引用宿主授权绑定，授权端口在当前观察点复核用途、主体、作用域、字段/对象范围和撤回代次；客户端布尔值无效 |
| `OperationBudget` | 最大字节、读取期限、并发和保持期限由批准 Profile 注入；缺失时拒绝，不使用隐藏默认值 |
| `EvidenceReadMode` | `MetadataOnly/VerifyBeforeDelivery/StreamingVerify`，行为见 §7.3.1；不得以预览缩略图代替原始校验 |

输出必须带原始身份、Manifest/对象修订、保存字节长度和摘要、完整性状态、授权观察点、读取代次、租约及明确的 `NotFound`/`PermissionDenied`/`Corrupt` 原因。它不返回通用行集、游标、快照、总数或导出文件；需要这些能力时由 `IM-045` 负责。

Gate-3 的流式定向读取必须在取得 lease 前、每个 range/块读取前、异步 I/O 返回后以及向调用方交付前复核同一精确目标和当前授权绑定（主体、会话、租户、用途、范围、policy、Commit/Manifest/Object/version/hash/range，以及批准合同适用的 endpoint/selection generation）。期限取原请求预算、当前授权及租约期限中的最早值，续读不得重置原请求预算。撤权、到期、目标或端点代次变化、短读、越界或摘要不符必须取消后续交付并真实排空；缓存字节、父对象可见或客户端 `Approved` 标志不能延长授权。只回收本次拥有且已排空的资源，不声称可召回已交付的字节。

Manifest 引用的嵌套 metadata、坐标变换、父对象或派生关系是独立的精确读取目标；父对象字节可见不自动授予嵌套引用的读取权。嵌套目标缺失、错版本、不可见或损坏时返回明确的 `Unavailable`/`PermissionDenied`/`Corrupt`，不得省略后伪装完整、按同 hash 替换或递归绕过授权。

### 3.4 现场追溯证据类型

模块可以接收以下四类不可变证据。它们共用 `EvidenceDescriptor`、来源绑定、保存字节摘要和保持/读取协议，但不能混成一个万能结果对象。

| 类型 | 最小追溯内容 | 允许的来源 | 不能推断 |
|---|---|---|---|
| `AcquisitionEvidence` | 采集/观察身份、点位或视场序号、通道/照明角色、采集时间及源帧字节 | 相机/采集适配器 | 未保存的曝光、真实硬件状态或质量 PASS |
| `DerivedImageEvidence` | 派生类型、父对象 ID 列表及顺序、变换/拼接/编码版本、输出摘要 | 图像/显示适配器 | 派生图可替代任一源帧或可用于重新判定 |
| `InspectionResultEvidence` | 调用方冻结的结果事实、工具/方法版本、来源对象 ID、来源位置列表、错误/Unknown 状态 | 算法/结果 Owner | 模块可重算算法、补全缺失目标或改变最终决定 |
| `FieldDiagnosticEvidence` | UTC 时间、原始时钟/时区信息、阶段、方向、操作名、尝试序号、状态码、可重试性、耗时、消息和请求/响应摘要 | 宿主诊断/现场支持适配器 | 网络 ACK 等于业务成功、日志缺失等于未发生、日志内容等于生产事实 |

四类对象均必须有稳定逻辑 ID、`sourceBinding`、内容长度和保存字节 hash。对象之间用明确的 `derivedFrom`/`supports` 关系表达，不能仅按文件名、相邻时间或目录推断。诊断日志是可追溯的外部观察，不取得结果事实、权限、质量或设备动作的写权。

当上游 Owner 提供一个由多个 FOV、帧组或其它来源共同支撑的逻辑检查项/结果关系时，证据闭包必须保留其批准的关系版本/hash、全部来源身份、原顺序、代次和缺项原因；重复通知不能新增逻辑关系，本模块不得自行排序、去重或修改上游冻结载荷。模块只校验、保存和回读该关系，不计算必检覆盖或替代上游归集。整板拼图或像素覆盖完整不能推断检查完成；乱序通知、不同 attempt 或缺必需来源不得被合并成 PASS、完整或第二次检查。

## 4. 同步、异步与事件顺序

### 4.1 同步与异步边界

仅 Gate-1 的纯计算提供同步入口。所有可能涉及存储、授权或租约的提交、恢复查询、读取及关闭均使用附录 B 的异步接口；不提供 `.Result`、同步包装或第二套 `GetCommitStatus/ReadEvidence` 入口。异步结果不依赖 UI SynchronizationContext，宿主自行切回显示线程。每个调用拥有独立请求代次、预算和 scope，不共享“当前读取”。

### 4.2 观察与回执

Gate-1 不发事件、不调外部回调。Gate-2/3 可由构造选项注入 `IProgress<OperationEvent>`；事件字段为操作诊断 ID、提交/读取身份、请求代次、实例 epoch、单调序号、阶段、累计字节、错误键及资源状态。回调在锁和事务外执行；慢/异常订阅者由有界通知队列隔离，诊断通知可丢弃并计数。事件不是持久事实；UI 按身份和代次消费，最终状态仍从明确响应/权威查询取得。不提供允许订阅者继续提交或修改事实的事件。

### 4.3 提交事件顺序

事件是语义事件，不是要求新增事件 Schema。顺序必须满足：

```text
Accepted
  -> IdentityValidated
  -> EvidenceStreaming
  -> EvidenceSealed
  -> EvidenceDurable
  -> ManifestValidated
  -> CommitPersisting
  -> Committed | Rejected | Unknown
  -> ReceiptAvailable
  -> OutboxPending (可选)
  -> OutboxDelivered/DeadLetter (由交付 Owner)
```

规则：

1. `EvidenceStreaming` 期间取消只停止后续读取，并保持/隔离已写暂存，直到写入和编码真正结束。
2. `EvidenceDurable` 之前不得让结果事实可见；对象已存在不等于本次发布完成。
3. `Committed` 表示结果、逻辑引用、回执和外发意图在批准边界内已登记，不表示网络送达、质量放行或设备应用。
4. `Unknown` 表示提交可能已经发生但当前无法证明；必须保留原身份和保持根，恢复查询不得盲重跑。
5. 通知可重复、迟到或丢失；消费者按事件身份/业务身份去重，不能以通知到达决定事实存在。

定向读取事件顺序为 `ReadAccepted -> AuthorizationChecked -> ManifestResolved -> LeaseAcquired -> BytesVerified/MetadataRead -> ReadDraining -> ReadDrained -> ResourcesReleased -> ReadClosed`。撤权、Manifest 代次变化或租约失效必须在字节交付前阻断；旧请求迟到不得覆盖新请求代次。通用查询的事件、游标和快照由 `IM-045` 定义。

## 5. 状态、错误码与恢复语义

### 5.1 状态

| 状态 | 含义 | 允许动作 |
|---|---|---|
| `Ready` | 请求、权限、版本、预算和最小证据条件通过 | 开始阶段操作 |
| `Busy` | 正在流式、封口、提交或定向读取 | 仅允许已定义取消/状态查询 |
| `Blocked` | 缺少身份、引用、能力、权限、证据策略或容量 | 修正前置条件后重建请求 |
| `RecoverableError` | 失败可按原身份恢复或有限重试 | 查询原操作，按预算恢复 |
| `Rejected` | 输入、摘要、版本、唯一约束或作用域冲突 | 不重试同载荷，不改写事实 |
| `Unknown` | 发送/提交结果无法证明 | 保持引用，查询权威回执 |
| `Corrupt` | 对象、Manifest 或关系完整性失败 | 隔离、恢复原件或标记历史受损 |
| `Completed` | 本次提交或定向读取已达到其定义终态，且资源已归还 | 只读回执 |
| `CancelledPendingDrain` | 调用方停止等待，内部资源尚未排空 | 等待 `Drained` 或查询状态 |
| `DrainUnknown` | 关闭期限到达，尚不能证明底层执行退出 | 保留资源隔离与恢复记录；只允许观察/继续关闭 |
| `Drained` | 本调用的 I/O、连接、reader 和回调均已退出 | 进入资源归还阶段 |
| `ResourcesReleased` | 本调用拥有的 lease、缓冲、临时文件和额度已归还 | 可关闭实例或发布 operation 终态 |

`Completed` 不表示检测 PASS；`Committed` 不表示质量放行；`Drained` 不表示未知事务已回滚。

### 5.2 错误码语义

错误码是跨门的错误分类候选映射，正式代码值须绑定 C-04/C-06/C-07，不能与应用业务错误混用。Gate-1 只能产生本地输入/引用校验、预算计划和基于只读快照的冲突候选；授权判定、保存字节摘要、存储故障、持久状态、回执未知及实际读取完整性只能由获准的 Gate-2/3 端口报告，不能伪装为 Pure Core 结果。

| 码 | 可报告门 | 语义 | 调用方动作 |
|---|---|---|---|
| `IEV-VAL-001` | Gate-1 | 必填字段/范围/单位/时间非法 | 修正请求；不重试原载荷 |
| `IEV-IDENTITY-002` | Gate-1 校验；Gate-2 按批准绑定复核 | 身份、作用域、版本或来源错绑 | 交原 Owner；不得猜测替换 |
| `IEV-HASH-003` | Gate-1 仅限声明值间的纯校验；保存字节核验属 Gate-2/3 | 长度/字节摘要/Manifest 摘要不符 | 隔离对象，拒绝发布 |
| `IEV-CONFLICT-004` | Gate-1 仅能报告只读快照中的冲突候选；权威唯一性/CAS 属 Gate-2 | 同键不同载荷、CAS 零行或唯一约束冲突 | 查询原身份并交 Owner；不换键绕过 |
| `IEV-AUTH-005` | Gate-1 仅解释 PermissionDenied 快照；Gate-2/3 真实授权 | 无写权、定向读权或授权已撤回 | Core不做授权；后续门重新取得批准权限，不靠UI隐藏 |
| `IEV-CAP-006` | Gate-1 Profile/目录校验；Gate-2/3 运行能力 | Profile 缺失，或存储适配器能力、版本、格式不支持 | 返回 `Blocked`；不自动降级 |
| `IEV-STORE-007` | Gate-2/3 | 连接、事务、对象存储、磁盘或耐久失败 | 按阶段恢复；保留原件与诊断 |
| `IEV-TIMEOUT-008` | Gate-1 仅限纯计算预算；外部操作属 Gate-2/3 | 本次等待预算耗尽，执行结果可能未知 | 外部提交先按原身份查询；不把超时翻译为回滚 |
| `IEV-CANCEL-009` | Gate-1 纯计算中断；Gate-2/3 真实取消 | 调用方取消；后续门内部仍可能排空 | Gate-1 无外部资源；后续门继续跟踪清理 |
| `IEV-CORRUPT-010` | Gate-1 仅非法快照形状；Gate-2/3 真实完整性 | 快照结构不一致，或已保存对象不可读/校验失败 | Core 仅报告候选；真实对象隔离，不以缩略图替代原件 |
| `IEV-READ-011` | Gate-3 | Manifest/对象修订、读取租约或来源代次失效 | 重新取得明确版本和租约；不回退到相似对象 |
| `IEV-BUDGET-012` | Gate-1 计划；Gate-2/3 执行 | 对象字节、读取期限、队列、临时盘或内存超限 | 缩小请求或申请批准 Profile；Pure Core 不声称已取得运行时额度 |
| `IEV-UNKNOWN-013` | Gate-2 | 技术边界无法确定提交/发布结果 | 保持根，按原身份恢复 |

异常必须携带 `OperationId`、阶段、是否已发送/提交、资源排空状态、可重试性和恢复建议；不得把秘密、连接串、客户数据或任意 SQL 写入诊断。

## 6. 取消、超时、线程、资源与排空

1. 取消 token 只表达调用方不再等待，不自动撤销已发出的提交、已发布对象或已登记事实。
2. 超时分为排队、连接、对象读取、写入/编码、封口/flush、事务 commit 和回执读取；总预算预留清理时间。`WaitAsync` 超时不等于底层命令停止。
3. 取消后停止新阶段，等待当前编码器、FileStream、reader、事务和驱动取消路径结束；不得并发在仍运行的命令上发送 rollback，也不得将未确认连接归还池。
4. 所有资源遵循拥有者释放：宿主拥有 `IEvidenceContentSource`；模块在幂等解析及接纳后调用其 `OpenReadAsync`，返回流必须是从 offset 0 开始的新独占只读流，其所有权在返回时交给模块。模块负责成功/失败/取消后真实排空再释放；source 不能返回仍被宿主使用的共享流。模块创建的暂存、哈希、缓冲、lease、连接、事务、reader 和派生预览由模块释放；共享数据源和适配器由宿主释放，模块不关闭共享池。
5. 线程模型：核心不依赖 UI 线程；同一个连接、事务、reader 和提交 scope 不跨线程并发使用；适配器声明线程安全性。需要并行上传/读取时，每个 worker 使用独立 scope 和有界队列。
6. 排空顺序：停止接收新请求 → 取消等待者 → 观察在途 I/O/事务 → 取得已提交/未知终态 → 释放 reader/命令/事务 → 关闭或隔离坏连接 → 发出 `Drained` → 释放对象 lease/临时文件 → 归还并发额度 → 发出 `ResourcesReleased`；随后才发布 operation 终态。
7. 页面关闭只取消本页读取 scope，不关闭全局对象池；提交未知时保留原恢复记录，不能因窗口关闭删除对象或 outbox。
8. 队列必须有最大长度、字节预算和背压策略。队列满返回 `IEV-BUDGET-012` 或明确等待，不无限创建 Task、线程、连接或缓存。

### 6.1 实例关闭与共享资源

实例生命周期固定为 `Open -> Closing -> Closed`，未排空为 `Closing/DrainUnknown`。`CloseAsync` 原子停止接纳本实例新请求，关闭本实例读 lease 并请求取消本实例工作；不撤销持久提交、不删除 Unknown 根、不停止其它实例或宿主共享恢复服务。关闭期限与运行 token 分离，来自 `CloseOptions`；期限到达返回 `DrainUnknown` 和本实例残留操作 ID，不谎报 `Closed`。底层后续退出仍由实例跟踪并归还资源，宿主可以再次 `CloseAsync` 观察；各次关闭共享同一关闭任务，不重复释放。

`DisposeAsync` 使用构造时冻结的有限关闭预算：已 `Closed` 则幂等返回；未能排空则抛 `EvidenceDrainIncompleteException`（仅本地生命周期错误，带 CloseReport），不把仍在运行的资源交回池。宿主记录该实例仍在隔离，继续观察；不能以 Dispose 返回/抛出证明事务回滚。业务 `Unknown` 与资源状态独立：I/O 已退出并释放时实例可以 `Closed`，但原提交仍为 `Unknown`，持久恢复根由存储保留，另一个实例可按原身份只读查询。双实例共享存储时，唯一键、epoch/CAS 与根协调在存储边界完成；实例内锁不能证明跨实例唯一性。

### 6.2 构造前的有限宿主根与迟到资源

本节仅服务G2/G3已有Runtime/读取生命周期，不给G1创建外部资源或新增持久写入切片。Runtime构造器是同步无副作用入口，**无异步Factory**；在构造中只检dependencies/options值，不订阅Authority、不调用Store/Clock/Binding、不启动Task。首个被接纳操作才订阅/调用端口，先将借用依赖及实例登记进下述进程根；构造失败实例未创建，宿主仍持有自己的Store/Authority。若以后新增异步Factory必须先修本节，不能把异步工作藏进构造器或把迟到实例丢掉。

唯一公开宿主根为Runtime包的`public sealed class EvidenceHostRoot`，构造器`public EvidenceHostRoot(EvidenceHostRootOptions options)`；Options是`public sealed record EvidenceHostRootOptions(int MaxInstances,int MaxTrackedTasks,int MaxTrackedLeases,long MaxBorrowedBytes,TimeSpan CleanupDeadline)`，计数/字节上限正且checked、期限正有限，无默认。根由服务进程组合根拥有，**不是全局static、页面局部变量或本模块持久事实Owner**；进程启动时构造并持有到最终收尾。超容量先返回IEV-BUDGET-012、无新构造/调用。

| 公开入口/值类型 | 顺序与所有权 |
|---|---|
| `RootReservationResult TryReserve(EvidenceRuntimeDependencies dependencies, EvidenceRuntimeOptions options)` | 先占实例/依赖引用槽，result=`EvidenceHostReservation? Reservation/ImmutableArray<ValidationIssue> Issues`；失败无Reservation，options/dependencies与Runtime构造相同，不能以还未构造绕过配额。成功Reservation强持借用依赖，但不Dispose宿主Store |
| `void EvidenceHostReservation.Attach(IInspectionEvidenceRuntime runtime)` | 构造成功立即同步Attach一次，核为对应依赖/选项的新实例，重复/跨根Attach拒绝。无实例的构造失败用`AbortBeforeAttach()`，只退自己空槽；Attach后不能Abort释放活实例 |
| `TaskReservationResult EvidenceHostReservation.TryReserveTask(HostOperationIdentity identity,long borrowedBytes,int leaseSlots,TimeSpan observationBudget)` | 在任何Commit/Read/Recover/Retain/Close异步调用前占Task/借用字节/可能迟到lease槽；byte/lease申请≥0、总量checked且≤根上限，Read预留至少1lease槽，内存source按实持缓冲计账，不能用文件length伪装驻留量。observationBudget正有限且≤原请求剩余期限，根用Stopwatch单调计时从预约时起冻结截止，Track/Accept/重等不重置。HostOperationIdentity字段`Kind:string/Identity:ScopedId?/OriginalDigest:DigestValue?/OperationId:string/RequestGeneration:long`，按原请求记录；result=`EvidenceHostTaskSlot? Slot/ImmutableArray<ValidationIssue> Issues`。失败不调用端口 |
| `public void EvidenceHostTaskSlot.Track<T,TRequest>(Task<T> originalTask,TRequest borrowedRequest)` | 强持原已定义请求/source/options，非公共提交payload，禁止object/dynamic提交重载。ValueTask转AsTask仅一次，立即Track，不先WaitAsync/丢原Task。根观察成功/异常/取消及迟到lease/result；同步调用抛异常尚无Task时`AbortBeforeTrack()`退空槽并保留原错误 |
| `RootDrainResult EvidenceHostReservation.Observe()` | 无I/O的当前根状态：`RootState State/ImmutableArray<HostOperationIdentity> Pending/ImmutableArray<ValidationIssue> Issues`；Pending不可凭等待到期清空。RootState=`Owned/Draining/Released/TransferPending/Transferred` |
| `ValueTask<RootDrainResult> EvidenceHostReservation.CleanupAsync(CancellationToken cleanupToken)` | 停接纳，独立于业务token创建一次固定CleanupDeadline，关闭本实例与未交付/迟到lease，等真正ResourcesReleased；到期仍Draining/保留槽和原Task/输入流借用，后台观察继续。原业务异常与Cleanup问题分别保留，不在finally覆盖业务失败或返回成功 |
| `RootTransferResult EvidenceHostRoot.Transfer(EvidenceHostReservation reservation, EvidenceHostRoot target)` | 目标在自己有限槽中原子接纳原实例/Task/借用/lease/原操作身份后返回`bool Accepted/string? AcknowledgementId/Issues`。Accepted必须有ack；源核ack后才Transferred退源槽，目标成为唯一资源Owner；拒绝/超额/未知保持源Owned，不能先Release再移交。没有合法目标就由原进程根继续观察 |

RootReservation/TaskSlot为public sealed class，仅根创建、无public无参构造、**不以IDisposable自动释放活槽**；`AbortBeforeAttach/AbortBeforeTrack`只用于确定无实例/Task的失败路径。完成Task可能仍返回Active/DrainUnknown或lease，不能凭Task.IsCompleted释放槽；root只在实际资源Released且全部chunk/lease已归还、Borrowed引用结束使用时退槽。本地根不需要持久化/API自报byte值当证据，实际计账由Host可信装配完成，超额拒绝并保留在途。Runtime内部每个Store I/O也先占有界operation槽并强持原Task/输入/租约；宿主Task结束不能丢内部I/O。UI关页后root继续持有Reader/显示lease回调直到真实清理。

`RootReservationResult/TaskReservationResult/RootDrainResult/RootTransferResult`均public sealed record，构造参数名/顺序如表、没有默认值；失败Issues非空且结果Reservation/Slot为空。根只能转移自己持有的reservation，跨实例Attach/未知来源返回IEV-VAL-001；`AbortBeforeAttach/AbortBeforeTrack`重复调用仅在同已空tombstone幂等，无活资源不承诺撤销。Attach核new实例的Dependencies/Options是TryReserve时同一不可变配置；Runtime内部可向根提供不可变装配标识，不向产品请求暴露Store引用。移交只在同进程两个根之间按稳定reservation身份原子交接，ack与原身份绑定；无网络/进程恢复移交API。

TryReserve仅支持本模块具体新构造Runtime实例，Attach不接受未知其它实现进行隐式扫描；传入其它实现返回IEV-VAL-001并保留宿主自己的实例，不调用Dispose。Track的T/TRequest只允许运行端口对应组合（CommitResult/CommitRequest、CommitRecoveryResult/CommitRecoveryRequest、EvidenceReadResult/EvidenceReadRequest、RetentionResult/RetentionRequest或RetentionQuery、CloseReport/CloseOptions），不反射任意object找身份/资源。组合不符先拒绝IEV-VAL-001，不接管已产生Task；宿主必须预约/调用匹配端口并在同步失败时Abort空槽，不能先运行未知Task后交给根兜底。

读取Task迟到返回lease：未交付的lease由根关闭；已交付的lease由调用者使用/归还，根保留强引用并观察本模块释放通知，不二次读取/并发Dispose正在消费的chunk。迟到CommitReceipt只是按当前权限的原结果候选，不能送旧页面或新operation；Unknown只按原CommitIdentity/request digest/Kind/ResponseVersion查询。cleanup结束但原事实仍Unknown时可Released资源槽，**持久Unknown根仍由Store保留**；恢复由新实例+新当前权限+有限恢复预算按原身份执行，不让关闭的旧实例自动重提交。进程关闭时若无法Released/获确认移交，明确未排空并保留持久恢复身份，不能宣称资源已归还。

TaskSlot另外公开`void DetachWaiter()`与`ValidationResult AcceptLease(IEvidenceReadLease lease)`：Detach标记等待者不再消费/页面失效，不丢Task/身份；有效等待者取得原ReadResult后立即AcceptLease，核返回的同一lease/root/代次，只接受一次，拒绝跨请求/已Detach/正在Cleanup交付。原Task返回lease时，有效等待者在原观察预算内尚未Accept，根只强持不先Dispose；预算到达/Detach/Cleanup后仍未Accept才关闭迟到lease。Accept后调用者借用读/Dispose权，root保留最终Owner。Accept/Detach/迟到continuation在root有界锁下线性化，不让两方同时交付/清理。lease公开`ResourceState ObserveResources()`（无I/O），只在自己的I/O/回调/chunk/保持真正Released时返回ResourcesReleased，root才退lease槽，不以Integrity代替。Task结束但Runtime内部I/O未知时槽保留到本实例CloseReport明确Released，或确认移交；资源观察在有限cleanup内执行，后台完成不解除仍使用的chunk。此接口仅补原读取资源观察，不写事实。

上述根是纯进程Host协调，不执行生产事实写入、设备命令、GC或远程移交协议。Runtime正式mapping未接收时只用合同假端口验证根保留/迟到释放；真实Store/授权/跨进程崩溃恢复门仅阻相关G2/G3，G1公开构造与§9.1完全不依赖此根。

## 7. 后续门：持久化、定向读取与回收实现顺序（Gate-2/3）

本节只定义通过独立准入后的 Gate-2/3 处理约束。唯一宿主事实提交入口为 `IInspectionEvidenceSubmission.CommitAsync`；它可在内部按以下阶段编排，但 `Stage`、`Seal`、`Publish`、事务登记或 adapter 调用均不得另行暴露为可绕过该入口的事实提交命令。对象和事务实现由 IM-066 提供，C-04 保持事实 Owner；此处不扩展 IM-066 或 IM-045 的职责。

### 7.1 Stage/Seal/Publish

1. 校验身份、用途、权限、对象数量/字节预算和存储能力；适配器生成受控暂存定位，拒绝任意路径、越界路径和覆盖请求。
2. 按连续偏移接收分块，逐块核对可选块摘要，累计实际长度和保存字节摘要；错 offset、重复不同内容和超限立即拒绝。
3. 完成压缩/加密/索引尾部后再 flush；封口前对象不可被正式读取或被 `IM-045` 投影引用。
4. 核对媒体类型、长度、摘要、来源绑定、角色、作用域、Manifest 关系和传递依赖。未知来源、`latest`、循环关系和缺项停在缺口，不补零或补相似文件。
5. 以适配器证明的原子可见边界发布；跨卷复制必须在目标暂存中重新核对摘要和耐久，不能把 `File.Move` 当作跨存储原子操作。
6. 取得持久保持根后才进入结果事务。保存合法失败结果；保存失败不显示“已完成”。

本模块不重编码、压缩或加密宿主输入；Contents 必须已经是 Encoding 指定的最终逻辑保存字节，采用每对象独立 `IncrementalHash.CreateHash(SHA256)`，每个正长度读取 AppendData，准确 EOF 后才 GetHashAndReset/Dispose。模块封口核的是同一字节域、累计长度和实际摘要，旧 hash 实例不能跨对象复用。后端透明加密/容器校验属 IM-066 的物理存储域，不能拿其密文摘要替代本模块回读逻辑对象字节摘要。若未来要求本模块重编码，须另修订本指导并冻结原输入/编码后/物理域，不在本版内部任选变换。

### 7.2 Commit/Receipt/Recovery

短事务内登记不可变事实、逻辑证据引用/清单、回执、原操作结果和可靠 outbox 意图。大图传输、外部 RPC、设备动作和算法重算不放进事务重试回调。

Gate-2 的只读恢复查询必须按原操作种类、响应版本及原请求身份/摘要解析对应持久响应，再核对同一次提交的事实修订、Receipt、Manifest 和对象关系。不允许宽松地将 Receipt 反序列化为 session/operation snapshot 后以默认字段报告 `Completed`，也不允许凭回执字段存在、首条匹配或对象文件存在证明完成。缺字段、错类型、跨作用域或关系不一致按原因返回 `Rejected`/`Corrupt`/`Unknown` 并保留原恢复线索；查询本身不重发提交、不填造缺字段。只有原提交响应及其关联状态完整一致时才返回对应原结果。

恢复按故障窗口区分：

| 故障窗口 | 对外语义 | 恢复 |
|---|---|---|
| 接纳前/上传中 | 未完成 | 原操作查到后才续传；不补成成功 |
| 封口后/发布前 | 未提交，可能有暂存 | 核对暂存、发布或隔离清理 |
| 对象已持久/事务前 | 未提交或未知 | 保持对象，按原身份恢复或确认终结后回收 |
| 提交已完成/响应丢失 | `Committed` 可查询 | 同键返回原回执，不重算、不新 ID |
| 提交/通知后崩溃 | 事实已提交，投递未知 | outbox 重发；消费者去重 |
| 已提交对象损坏 | 历史事实保留，读取失败 | 标记损坏并按恢复来源修复，不改摘要 |

### 7.3 定向读取、保持、读取租约与 GC

恢复/回执读取使用附录 B 的完整 CommitRecoveryRequest，不能只凭回执 ID 省略原请求绑定；Manifest 读取使用已授权的不可变版本。对象读取先解析 Manifest、复核用途和撤回代次，再取得精确对象 lease，按三种明确模式处理。结果带实际摘要、长度、修订和完整性状态；不能按“最近一条”、最大 ID、文件名或当前页面补齐对象。

`IM-015` 不建立查询快照、游标、聚合或导出工件。宿主需要条件检索、分页、固定总体或 CSV/XLSX 时，必须通过 `IM-045` 的注册投影/导出端口；`IM-045` 只能消费本模块公开的 Manifest/回执引用，不能取得本模块写权。

保持根至少包括已提交结果、未知操作、活动写入、定向读取/预览、备份和调查 Hold。读取先取得确切对象版本的 lease，实际 I/O 在锁外但保护持续到最后一次读取；区间读取不代表全对象已校验。

GC 必须在与新引用/读取预约共同协调的版本边界重新检查所有根，再隔离和删除；没有共同协调能力时停止受影响 GC。删除结果未知时保持隔离，不立即重发删除或解除保持。模块不按年龄、最后访问时间或两次扫描自行决定业务保留。

### 7.3.1 三种读取模式与字节终检

`MetadataOnly` 只返回当前授权的关系/声明元数据，Integrity=NotChecked；不读对象字节、不报告 FullVerified。必需嵌套引用不可见时整个依赖闭包返回 PermissionDenied/Incomplete；独立源图不依赖的可选详情失败可隔离，不能删掉必需父项后宣称完整。

`VerifyBeforeDelivery` 用于 Replay 和对原始完整性的强要求：按闭包先取得全部精确对象的保护，检查必需父字节/关系，再将目标完整字节流入模块私有、不可修改的有界暂存；逐段 SHA-256、累计长度和 EOF 通过后才返回 lease。本版暂存固定为有界托管内存，额度取MaxVerificationSpoolBytes与原MaxBufferedBytes剩余的较小值，完整目标不能容纳则在Open前Blocked，无自动磁盘spill或降级StreamingVerify；IM-066现有公开端口未定义无持久副作用的私有spool，因此不能留给实施者猜临时文件API。交付读取的是此次已核验的同一私有快照，不在核验后重新从未受控原路径读取；暂存/保护持续到 lease 与最后 chunk 释放。父闭包字节顺序核验/释放，只保留目标私有快照；累计核验字节、对象数和图深度仍在同一预算内，不能为闭包无限读父对象。撤权时停止交付、排空并清理暂存，不声称撤回已交付字节。较大图的托管额度由消费者Profile提供，超出本范围不能自动开存储写能力。

`StreamingVerify` 用于低延迟查看：分块交付同时累计目标长度/hash，期间 Integrity=Verifying，消费者不得在 EOF 前当作完整 Replay 输入。整对象在准确 EOF、完整长度/hash/闭包通过后 FullVerified；range 只完成指定区间且保持 PartialUnverified，即使区间 hash 与全对象摘要同值也不能升级。range 当前不提供块 Merkle 证明，不新增未定义块摘要 API。结尾出现损坏时返回 IEV-CORRUPT-010/Mismatch，UI 清除当前代次受影响像素；已消费数据不假称可召回。

底层 Stream.ReadAsync 返回 `0<n<buffer.Length` 时继续累计，不把一次短块当损坏/EOF；正长度读取返回0且累计未到声明末尾才是截短错误，到达声明末尾后还须确认没有多余字节（range 不越界窥读）。ReadChunkAsync 的唯一末块约定为**数据块与 EOF 分离**：每个成功数据块 Bytes 非空、IsEnd=false、Issues为空，包括最后一块；最后数据块释放后，下一调用完成终检并返回 Bytes为空、IsEnd=true、Issues为空的独立 EOF 块，OffsetBytes等于实际交付区间末端（整对象为对象长度）。成功空对象直接返回该EOF块；range完成不代表全对象FullVerified。终检失败只返回 Bytes为空、IsEnd=false、Issues非空的错误块，绝不返回EOF；禁止 Bytes非空与IsEnd=true的组合及成功空数据块。每次最多一个未释放chunk，未释放时下一ReadChunk返回IEV-BUDGET-012、零新I/O；EOF/错误块也必须Dispose。已EOF/失败关闭后的调用幂等返回原终态，不再次读。chunk.Dispose仅归还其缓冲；lease排空须等全部chunk归还，超时DrainUnknown，不能回收宿主仍用的内存。

### 7.3.2 保留决定与未知根

读取保护是技术 lease，生产/未知/备份/调查根是持久引用，不能用 lease TTL 到期删除后者。C-07 提供明确 RetentionDecision（Hold/ReleaseHold），本模块唯一 ApplyRetentionAsync 仅登记批准决定及精确对象闭包，QueryRetentionAsync 仅读同决定身份/摘要的原回执；不决定天数/法律保持、不执行物理 GC。ReleaseHold 只解除该决定指定的保持根，不碰生产、Unknown、备份或其它 Owner 根；同决定 ID/摘要返回原回执、异摘要冲突，未知不重发解除。失去当前权限不向调用者披露原保持范围，内部 GC 仍承认根。

IM-066 的根协调器必须在登记新引用、取得读取保护与 GC 最终复核/隔离之间提供同一协调边界。本模块提供自己持久根的版本化读取投影，协调 epoch 不完整/Unknown/旧 resolver 无法全量枚举时拒绝受影响 GC，不能以两次扫描或年龄代替证明。恢复 journal 在服务新写前核查；对未发送登记且源流不支持重开/续传的上传，确认未提交后隔离暂存，宿主以原身份重投完整流；本接口不承诺公开续传。内部可从已核块接续，但须从持久状态取得原源版本/offset，不能凭新请求字节拼接旧未知操作。

### 7.4 DZ-XVision 现场追溯采纳边界

DZ-XVision 的现场保存经验只用于补充证据图的约束，不迁移其目录、字段、数据库或业务编排。平台接纳时按逻辑身份和 `sourceBinding` 建立以下角色：

1. **原始点位图（`AcquisitionEvidence`）**：每个点位/视场的源帧是独立不可变对象。普通光、UV 或其它通道必须使用不同的通道/照明角色和来源绑定；通道角色、点位序号、采集尝试和实际保存字节都要进入 Manifest。相同字节可以由多个逻辑关系引用，但不能把它们合并为一次曝光或一个点位。
2. **派生行图与总览图（`DerivedImageEvidence`）**：产品行图、总览图或用于显示的拼接图只能作为派生证据保存。Manifest 必须列出父对象 ID、父对象顺序、布局/变换参数摘要、拼接或编码版本、输出长度和保存字节 hash；父对象缺失、顺序不完整或版本无法核验时，派生对象不得发布为完整证据。总览图不能作为视觉工具的源输入，也不能替代任一原始点位图。
3. **可选通道和缺失表达**：普通光/UV 等可选通道不得用空字节、相邻点位或其它通道填充。缺失可选证据要在 Manifest 中以正式缺项/Unknown 关系表达，并保留缺失原因和来源尝试；必需源图缺失、错绑或损坏则阻止依赖该图的结果可见。读取方必须区分 `MissingOptional`、`MissingRequired`、`SourceCorrupt`、`DerivedIncomplete` 和 `PermissionDenied`，不能回退到相似对象或“最近一张”。
4. **读取闭包**：读取派生图时先解析全部父子关系，再按各父对象的精确版本取得 lease；任一必需父对象不能核验，派生读取返回不完整/损坏状态而不是只交付可用片段。读取原始点位图、派生图、结果事实和错误证据必须使用各自的逻辑身份，不能以同名文件或共享 blob 摘要替代身份。

上述规则只定义证据保存和读取语义。图像拼接、通道配准、源图选择和质量解释仍由上游 Owner 冻结并随派生关系记录；本模块不重算、不补齐，也不把派生显示结果写成检测输入。

## 8. 适配器契约与版本兼容

### 8.1 后续提交门适配器最小能力（Gate-2/3）

| 适配器 | 必须提供 | 禁止泄漏 |
|---|---|---|
| `IObjectStoreAdapter` | 暂存、分块写、封口、摘要/长度核验、flush/耐久证明、不可变发布、读取 lease、版本化删除 | 本机绝对路径、SDK 句柄、驱动类型 |
| `IMetadataTransactionAdapter` | 受限连接 scope、参数化命令、CAS、提交/回滚/未知状态读取、Schema 能力、迁移诊断 | 任意 SQL、表名、连接串、万能 CRUD |
| `IAuthorizationPort` | 按用途/范围/对象/字段/定向读取动作检查授权和撤回代次 | 客户端 `Approved` 布尔量作为权限 |
| `IManifestReceiptAdapter` | 按完整身份读取回执/Manifest、版本核验、权限观察点和恢复状态 | 通用条件、`latest`、跨事实猜测 |
| `IEvidenceReadAdapter` | 按 Manifest 版本取得读取 lease，流式读取并核长度/摘要/完整性 | 查询投影、导出编码、任意路径或 native 句柄 |
| `IDiagnosticsPort` | 结构化阶段、耗时、计数、资源水位和错误关联 | 秘密、原始大图、敏感数据 |
| 宿主诊断证据映射（可选） | 接纳宿主已封存的诊断记录/批次，经同一 CommitAsync 保存，不另开追加写入口 | 实时诊断总线、业务事务、外部 ACK 或生产事实写权 |
| `IImageEvidenceAdapter`（可选） | 按明确 media/编码解码或预览，返回独立 lease 和完整性状态 | 把 native 对象写入持久契约 |

宿主诊断证据映射只提供已整理、封存的不可变批次，不接管 live diagnostics，不新增本模块日志追加 API。每条记录拥有独立事件身份；相同字节可物理共享，但不可合并事件/逻辑记录。记录 schema/canonical 由诊断 Owner 定义，至少含原时钟/时区、规范 UTC、单调接收时间（若有）、阶段、方向、操作名、尝试序号、关联 OperationId/CommitIdentity（如有）、状态码、可重试性、耗时、请求/响应摘要和缺失标记。宿主映射先计算记录/批次摘要并核连续性，IM-015 再计算实际保存字节摘要；两域不互证。封存后只读，不再追加修改同对象。

适配器必须在接纳前执行敏感字段脱敏和长度/字段预算检查，保留“已脱敏”及规则版本，不能把完整请求、响应、秘密、令牌或客户隐私写入证据。时钟倒退、重复尝试、响应缺失或接收顺序异常要作为记录状态保留，不得静默重排成成功流程。写入失败只降低现场追溯能力并生成结构化缺失诊断，不改变已经提交的生产事实、结果状态、权限或设备动作；若该日志是正式必需证据，提交策略由上游 Contract 明确阻断，不能由适配器自行改判。诊断模块继续负责实时查看、告警和采样，本端口只负责需要长期保存的证据封存与按精确身份读取。

### 8.2 无产品宿主的装配及 IM-066 映射

Gate-1唯一公开实现在namespace **`Asun.Modules.InspectionEvidence`** 中声明为 **`public sealed class InspectionEvidenceCore : IInspectionEvidenceCore`**，唯一构造器为 **`public InspectionEvidenceCore()`**。该构造器公开、同步、无参数、无外部初始化、无配置读取，不创建Task/线程/native/lease；不存在必须先调用的Factory/Initialize/CreateScope。四个实现方法公开签名与附录B的接口逐字一致，实例可直接向IInspectionEvidenceCore赋值。无可变实例状态/静态服务，不提供Dispose，不调用注入服务。同实例/双实例并发纯调用结果一致；上下文是每调用不可变值，null/非法输入走typed Issues。公开类/构造是待实施Core合同，不是已存在DLL的声明；完整消费入口见§9.1。

后续 runtime 类为 `Asun.Modules.InspectionEvidence.Runtime.InspectionEvidenceRuntime`，构造器固定为 `(EvidenceRuntimeDependencies dependencies, EvidenceRuntimeOptions options)`；装配失败抛 `EvidenceInitializationException`（Fault 为 ValidationIssue，不携带敏感异常），不产生存储副作用。dependencies 字段：宿主拥有的 `IStorageDatabase Store`、本模块 `IInspectionEvidenceAuthority Authority`、`IInspectionEvidenceBinding Binding`、`.NET TimeProvider Clock`、可空 `IProgress<OperationEvent> Observer`。Store 类型直接来自 IM-066 的 `Asun.Platform.StorageDatabase.Contracts`；Runtime 包引用 Contracts与用于StorageRequestHasher的IM-066 Runtime，本模块 Core 不引用。Options 字段为 `ValidationProfile Profile`、`CatalogSnapshot Catalog`、`OperationBudget DefaultBudget`、`TimeSpan DefaultCloseTimeout`、`TimeSpan ObjectProtectionTtl`、`int MaxNotificationEntries`、`long MaxVerificationSpoolBytes`、`VersionReference BindingVersion`、`EvidenceStorageBridgeOptions StorageBridge`（B.5），全为非空、正值、有限且受总 Profile 约束，无代码默认常量。Binding构造与Runtime Options必须引用同一StorageBridge版本/hash与逐字段内容，冲突初始化失败。TTL 续期只在原截止前、当前授权且底层版本 CAS 成功时进行，不把 Unknown 持久根变成有限 TTL。

`IInspectionEvidenceAuthority.CheckAsync(AccessCheck, CancellationToken)` 返回 ValueTask<AccessDecision>。AccessCheck 字段为 `Access:AccessContext/Action:EvidenceAction/CommitIdentity:ScopedId?/RequestDigest:DigestValue?/Evidence:EvidenceReference?/RetentionDecisionIdentity:ScopedId?/RetentionDecisionDigest:DigestValue?/Range:ByteRange?/RequestGeneration:long/ExpectedStamp:AuthorizationStamp?`；Action=`Commit/Recover/Read/Retain`，按动作恰一身份分支（Commit/Recover必有提交及摘要；Read必有Evidence，generation>0；Retain必有决定身份/摘要），非Read的generation=0。AccessDecision字段 Allowed:bool、Stamp?、Issues；Allowed只有服务器端口可生成且附 Stamp（`Reference:ScopedId/RevocationGeneration:long/ExpiresUtc:DateTimeOffset/PolicyVersion:VersionReference`），拒绝无Stamp，不披露存在性。授权端口在受信任实现内取得主体/端点/权限，不由请求传委托；持久登记前、I/O后/交付前复核相同Stamp绑定，失效阻断新阶段。

Authority同时公开 `event EventHandler<AuthorizationInvalidatedEventArgs> Invalidated`；args仅 `Reference:ScopedId/ObservedGeneration:long/ReasonKey:string`，不含权限秘密。Runtime在首授权前订阅，取得Stamp后重查代次，避免订阅竞争；已显示图像的lease继续存活并监视授权到期/Invalidated，不在EOF后解除保护。通知只代表实际观察到失效，不能承诺远程撤权尚未传播就已回收显示。UI在解码后及Dispatcher交付前调用lease.CheckDeliveryAsync，收到通知/到期即时清该代次敏感像素并CancelRead；授权变更生效点由C-06合同约束，未接收传播保证时不声明生产撤权时延达标。此本地通知/守卫契约已定，不以按钮隐藏代替权限。

`IInspectionEvidenceBinding` 是宿主启动时提供的受控映射，不是运行请求 delegate，公开成员仅 `Version:VersionReference`、`ValueTask<BindingCommandResult> EncodeAsync(BindingInput, CancellationToken)`、`BindingDecodedResult Decode(BindingResponse)`。BindingInput为附录B.4的封闭分支，按kind恰一载荷；Encode失败无Command，成功Command含注册Binding/受控参数/技术身份/References。Read仅用于受限ReadAsync，Write仅用于ExecuteTransactionAsync。Decode核原ResultSchema/ResultBytes/References和预期kind/identity/digest，返回封闭typed原回执/Metadata/保持回执/RootPage；错Schema、缺字段、身份/关系不符返回Corrupt Issues。转换代码在Runtime消费层，本模块通用Manifest/Receipt/Root codec采用B.6，C-04/C-07只提供原业务事实/决定validator及业务mutation映射，不让Core猜产品字段。请求/事实按原Owner域、Manifest/Receipt按所属模块codec分别核验；未注册返回IEV-CAP-006，禁止宽松反序列化。

| 本模块步骤 | IM-066 已定义的受控公共入口 | 必须断言 |
|---|---|---|
| 幂等解析/竞争接纳 | `OpenSessionAsync` → `IStorageSession.ReadAsync(RegisteredReadRequest)`；需要原操作保留时执行已注册 ReserveCommit 事务 | 同 scope/CommitIdentity 唯一，原 kind/schema/digest 先解析；同键败者不开 source。Reserve 只登记恢复状态，不公开结果事实 |
| 字节暂存与封口 | `FileObjects.StageAndSealFileAsync(FileObjectRequest, Stream, token)` → QueryOperationAsync/GetTaskStatusAsync | 使用原技术操作身份；对 StorageTaskStatus 观察到实际封口/发布/耐久回执后才继续；Unknown 不从路径存在推断成功 |
| 保持保护 | `AcquireRetentionHoldAsync` → `IObjectRetentionLease.RenewAsync/ReleaseAsync` | 实际代次 CAS；所有必需父/子取得保护；生产/未知根另经批准引用协调器持久登记，不只靠 lease |
| 权威登记 | 注册 FinalizeCommit 的 `ExecuteTransactionAsync`；原存储操作 QueryOperationAsync 回读 | 同事务登记 C-04 冻结事实、Manifest、Receipt、原响应、可选 outbox 和根；事实仍归 C-04。对象先持久，无对象事务大图 I/O |
| 精确读取/核验 | 注册 ResolveEvidence 的 ReadAsync → `FileObjects.OpenReadAsync/VerifyAsync` | 存储 Stream 只在本模块 lease 内使用；外部消费者只获受控 chunk，权限/字节守卫在本模块且存储授权仍执行 |
| 保持与根投影 | 注册 ApplyRetention/ResolveRetention/ListRoots；IM-066 `IStorageOwnerReferenceResolver` 绑定 | 同保持决定幂等；RootPage 有 SnapshotId、ReferenceEpoch、非重复序号及 Complete；Unknown/incomplete 不授 GC 资格 |
| 释放/关闭 | `IStorageSession.ReleaseAsync`、对象/保持 lease ReleaseAsync；`Diagnostics.GetResourceStatusAsync` | 资源句柄/epoch 只在 Runtime 适配层，跟踪 Released；DrainUnknown 保留隔离；不 Dispose 宿主共享 Store |

此表复用 IM-066 当前公开规格，不将 §8.1 的能力标签变成第二套存储 API，也不修改 IM-066。模块 owned 的技术命令封套、身份、预算和响应匹配见§8.4/B.5，两个完整协议Fake Host见§9.3；这部分技术桥指导已于2026-10-11获主控限定内容接收，接收范围见§17.3，不提升实现准入状态。正式Owner codec、注册事务与ReferenceResolver采纳仍是跨模块工程交接门，不能统称客户外部门。物理 GC、备份恢复由 IM-066 实施；本模块只维护自己持久根和定向读取。

### 8.3 兼容规则

- 读取旧版本必须通过显式版本适配器和迁移计划；不以同名字段或“默认值”掩盖单位、枚举、来源或 null 语义变化。
- 删除字段、改变单位、改变 hash 覆盖范围、排序比较器、状态含义、保持策略或错误可重试性属于合同变更，必须提高主版本或取得正式兼容决策。
- 新字段可在兼容窗口中可选读取，但写入方不得向旧消费者发送其无法验证的必需字段。
- 迁移前核库身份、源/目标 Schema、变换 hash、空间/时间预算和可逆性；缺库、未知版本、迁移记录损坏时不自动建空库、不降级生产写。
- 组件包、适配器和数据 Schema 分别记录版本、摘要、运行时、后端能力、许可证通知和回退包；回退只切换到已验证兼容版本，不能删除新版本已产生的事实。

### 8.4 G2-T1 / G3-T1 技术消费桥（指导内容限定接收，未获实现准入）

本节直接消费 [IM-066 唯一指导](../storage-database/DEVELOPMENT-GUIDE.md) `0.3.0-prep` 的§§6/6.1–6.3与§7.1.1–7.1.2；C0/C1已接收，A1/A2/A3真实资格未接收。不复制SQL、数据库私表、RootCoordinator实现或上游Hasher。复用§16.1既有.NET10 Stream/IncrementalHash/协作取消及固定restic源码依据，不重复研究。本节新增的是Runtime内技术适配及测试夹具，**不是C-04/C-07业务Schema采纳、生产提交授权或持久耐久证明**。G1六项接收保持；G2-T1/G3-T1确定技术桥指导已于2026-10-11获主控限定内容接收，范围为§8.4、§9.3完整两Fake Host及收尾、B.5技术codec/身份/目录/恢复、§12.3/13.2/17.3。该接收不标记ModuleCoreImplementationReady或ImplementationSpecificationReady，G2/G3及两技术片仍为`PreparationIncomplete/DesignReview`；正式codec/注册事务/root采纳、授权接线、真实IM-066运行及介质耐久仍按§16.2对应门关闭。ProtocolFake不代表耐久或业务事实资格。

#### 8.4.1 公开构造、注册与封闭命令

唯一技术适配实现为`public sealed class RegisteredInspectionEvidenceBinding : IInspectionEvidenceBinding`，namespace `Asun.Modules.InspectionEvidence.Runtime`，公开同步构造器`RegisteredInspectionEvidenceBinding(IEvidenceBindingCodec codec, EvidenceStorageBridgeOptions options)`。构造只校验有限不可变目录/版本，零IO/Task/订阅；codec/options由Host持有，不由Binding Dispose。B.5给出全部公开字段/签名。codec是受信任启动映射，产品包由C-04/C-07接收；本轮仅有§9.3协议夹具codec。请求不能携带codec、SQL、delegate、CLR类型或新注册项。

`BindingInput/BindingDecodedResult`是public abstract record，B.4各输入/结果是public sealed record；字段表按左到右顺序为公开主构造器，省略Context均展开为`BindingContext Context`，省略Description均为`CommitDescription Description`。`BindingCommandMode={Read,Write}`；所有结果Issues是`ImmutableArray<ValidationIssue>`，无默认值。`BindingCommandResult(BindingCommand? Command, ImmutableArray<ValidationIssue> Issues)`成功恰一Command且Issues空，失败Command=null且Issues非空。不用record/ImmutableArray默认Equals比较语义，Versions按集合逐字段比较，其它有序数组保留原顺序。

| 输入 → Kind | Mode / 输出分支 | 请求构造和精确匹配 |
|---|---|---|
| ReserveCommitInput → ReserveCommit | Write / ReservedBindingResult | 正式canonical/当前权限先核；References=Empty，输入无source。唯一事务固定原reservation及全部对象技术操作身份；重放返回原分配，竞争败者不打开源 |
| FinalizeCommitInput → FinalizeCommit | Write / CommitBindingResult | References为实际封口对象及全部已解析必需父对象闭包，按IM-066 ObjectKey确定性排序、重复Key拒绝（两个逻辑身份共享字节仍各保留逻辑关系）；输入包含原冻结事实/关系，不重排业务数组 |
| ResolveCommitInput → ResolveCommit | Read / CommitBindingResult | 按原EvidenceCommit/ResponseVersion/逻辑身份/请求digest，只读取得原mutation索引及原响应，不能生成新reservation/技术identity或调用事务 |
| ResolveEvidenceInput → ResolveEvidence | Read / EvidenceBindingResult | 精确Receipt/Manifest/LogicalId/Object与完整闭包；只读取登记参数，不把Reference按latest或文件路径替换 |
| ApplyRetentionInput → ApplyRetention | Write / RetentionBindingResult | 当前授权+C-07已冻结决定及完整精确闭包；References与决定相同；只有该决定根可改变，不删Unknown/生产/备份根 |
| ResolveRetentionInput → ResolveRetention | Read / RetentionBindingResult | 原决定identity/digest，查询不得重做Hold/ReleaseHold |
| ListRootsInput → ListRoots | Read / RootBindingResult | 不可变SnapshotId/ReferenceEpoch、连续NextSequence及页字节/数量界；未知/缺页返回Incomplete，不授GC；首次与后续页不能混合 |

`EncodeAsync`在原截止内调用无IO的codec.MakePayload，核exact registered payload CLR type、InputSchema/codec/BindingDescriptor全部VersionRef字段，再由codec对应IStoragePayloadCodec.Encode得到canonical bytes并深拷贝；其GetReferences须与上表实际技术Objects逐字段相同。不得把payload摘要当完整请求摘要。BindingDescriptor的OwnerKey/Kind/Purpose/PermissionKey/隔离/行数/命令数/重试值来自启动目录，Context不能降低。Write构成RegisteredTransactionRequest后调用**IM-066 StorageRequestHasher.Compute(request, descriptor, canonicalBytes, options.InputLimits)**，填原技术identity的PayloadHash；Runtime/Store会再次计算。Read构成RegisteredReadRequest，**不制造durable identity、Write参数或事务hash**。Encode方法虽然异步签名，但codec同步无IO；取消前返回typed取消，无半命令。

技术OperationId/IdempotencyKey与诊断OperationId分离。首次Write由本Binding根据`LogicalScope/LogicalId/Kind/Slot`产生稳定技术键，详见B.5；不能用随机Guid、当前时间、实例epoch或刷新后的权限Stamp产生重试身份。技术完整Scope/Store/Generation/Owner/OperationId/IdempotencyKey/PayloadHash在原提交的受控reservation/索引内保留；ObjectReservation.Operation同样保留。恢复读取返回这些原身份，查询只能调用`Store.QueryOperationAsync(new OperationQuery(currentContext, originalIdentity), token)`，不自行猜Mutation表、串联数据库NotFound/文件NotFound或新造QueryMutation API。

#### 8.4.2 原响应、预算与副作用边界

1. Context映射按B.5的精确LogicalScope+Access.AuthorizationReference启动项，得到StorageScope/StoreRef/CallerRef。`CallerRef`不是权限凭据；本模块Authority与Store IStorageAuthority仍分别检查当前动作。Stamp失效返回PermissionDenied，不查询存在性。全字段Scope/Store/Generation必须与identity/对象一致；无路由为IEV-CAP-006，不用当前窗口/静态全局补齐。
2. 用Clock.GetTimestamp冻结接纳与阶段截止。每次存储调用的ExecutionBudget=min(原Total剩余、当前阶段Io剩余、StorageMaxOperationTime)，WaitBudget=min(该ExecutionBudget、StorageWaitBudget)；≤0不发送新effect。Binding先使用Context.RemainingIoBudget形成临时CallContext，Runtime在发送前再扣除Encode/队列耗时，with更新等待/执行预算（不影响语义hash），不得发送过期命令。等待观察、响应解码、权限复核和重试都不刷新截止。Cleanup是独立有限预算，只排空/释放/观察原任务，不能借cleanup新增Reserve/Finalize/保持改变。
3. Write使用Store.OpenSessionAsync与对应注册ExecuteTransactionAsync；Read只用session.ReadAsync。Open/Read/Release等无TaskHandle的ValueTask一律仅一次AsTask，原Task先进入有界内部槽，成功迟到的session/lease立即接管后关闭；外层WaitAsync超时不能丢原Task。已接纳Write返回TaskHandle时，保存原Identity+Handle，按原instance查询GetTaskStatusAsync；Unknown再按原identity的QueryOperationAsync，只读恢复不重新execute。
4. BindingResponse持有**原ExpectedInput和ExpectedCommand**；Read为OwnerReadResult字段且无StoredOperation/TaskStatus；Write必须以原StorageTaskStatus/OperationRecord解码，不能拿只读bytes冒充事务。核完整identity、Kind、Binding/InputSchema/ResultSchema/codec、original digest、References闭包及响应分支，ResultBytes有界深拷贝，拒绝尾部/缺字段/错schema。TaskStatus的Identity/Result身份须一致；Committed TechnicalCommitReceipt.State+ResultSchema/Bytes正确不自动是业务Committed，还须codec.Decode得到同一次完整CommitReceipt及关系。Reserved的技术Committed仅表示reservation登记成功。
5. Task=null且RequestRejected返回原typed Fault，无任务；已接纳非Completed仅观察，不报告资源Released。Completed仅证明上游该任务清理已结束，Outcome仍由Record/Receipt决定；Record Unknown与本实例ResourcesReleased可并存。没有Record/权限/route不可确认、ResultExpired或旧writer未知都不得转NotFound/新提交。按原响应Schema解码旧版本，目录缺旧codec为IEV-CAP-006，不能降级到当前codec。
6. Binding Decode发生纯校验，无Store/文件/权限IO；Runtime在Decode后再次当前权限核验才向消费者披露。故障按§5本地码映射：InvalidInput→IEV-VAL-001，UnsupportedVersion/ResultExpired→IEV-CAP-006，PermissionDenied→IEV-AUTH-005，Conflict→IEV-CONFLICT-004，CapacityExceeded/ResourceBusy→IEV-BUDGET-012，字节IntegrityFailed→IEV-HASH-003（结构损坏为IEV-CORRUPT-010），CommitUnknown→IEV-UNKNOWN-013，DrainIncomplete→资源DrainUnknown并保留IEV-STORE-007，Unavailable→IEV-STORE-007，Cancelled→IEV-CANCEL-009，TimedOut→IEV-TIMEOUT-008。InstanceMismatch属于IEV-IDENTITY-002，租约失效为IEV-READ-011，维护类故障不进入本消费桥。CleanupIssues与PrimaryIssues独立，绝不覆盖主错或把Unknown改Rejected。

#### 8.4.3 源字节封口、持久根与TTL

ReservedBindingResult必须给出已登记的原ObjectReservation后才打开对应IEvidenceContentSource。新独占源Stream所有权按§6移交本Runtime；调用StageAndSealFileAsync时**对Store只是借用**，Stage原Task/后端读取尚未结束不得Dispose源，也不能在UI finally关闭。每对象用有界只读CountingHashStream包装此同一流，限制checked Int64实际读数、只核正长读取，正长度请求读返回0才EOF（count=0调用不触发EOF）；禁止Seek/Write，所有Read/ReadAsync经过同一累计/IncrementalHash，不第二次并发读取或重开。数据限制min(描述长度、Profile MaxObjectBytes、原Budget剩余字节)，累计到声明末尾后的下次正长Read仅借同一source作一次1byte探测：0确认EOF，多余byte立即完整性失败且不送Store/hash作合法内容；该1byte缓冲/IO纳入原预算及预约（不是range窥读）。截短/多余/hash错不生成SealedEvidence。

FileObjectRequest包含原Context、ObjectReservation.Operation/Key、描述MediaType、启动FormatMap中与Encoding **完整version/hash**对应的Format、ExpectedBytes与StoredBytes SHA-256。模块借用包装Stream给IM-066，观察Stage的StorageTaskStatus/GetTaskStatus与原OperationQuery，只有完整FileObjectReceipt Identity/Key/Object/Format/Bytes/hash匹配、DurabilityProfile精确等于FormatMap.DurabilityProfile且State=SealedDurable、上游task资源实际释放、包装流也完成EOF/hash核验才产生SealedEvidence。SealedNotDurable/Unknown/只查到对象Metadata均不得Finalize。Stage Fault主错优先，源Dispose或hash器清理失败单列CleanupIssues。模块不重编码，不以物理密文摘要替代StoredBytes域；fake的SealedDurable只是软件标签，无介质资格。

持久保护消费上游§6.3：Write封口前由Store建立durable PendingPublication，后续Finalize的Publish协调边界才将pending转为正式持久引用。Runtime须核封口回执及原mutation观察，不直接调用IM-066内部Coordinator.Preserve/Reconcile；真正RootCoordinator及产品引用提取器由Owner接收。Finalize前**重新核当前权限、完整对象保存字节hash/长度（FileObjects.VerifyAsync及原Verify identity查询）、描述/关系/事实canonical**；不是仅在Reserve前检查一次。若不能证明publication保护，不提交结果可见，保留原恢复身份/根为Unknown，不以短TTL填缺口。

AcquireRetentionHoldAsync用于上传后到事务、读取及显示的短期技术保护，Ttl=min(ObjectProtectionTtl、原剩余期限、已采纳Store租约上限)，不替代PendingPublication/Committed/Unknown/Investigation/Backup持久根。Renew只在原deadline前、当前权限、同ResourceHandle/ExpectedVersion CAS；Hold/Renew没有durable route/OperationRecord，**只用lease.GetStatusAsync或Diagnostics.GetResourceStatusAsync观察**，不得拿其identity作QueryOperation。ApplyRetention/ReleaseHold是注册业务决定事务，与短TTL ReleaseAsync完全不同；后者释放本次lease，不删任何持久根。所有lease Release/Dispose原Task在有界槽内至Released，无确认不回收槽。

ListRoots转IStorageOwnerReferenceResolver只输出已解析ObjectRef的完整一致snapshot：SnapshotId/ReferenceEpoch始终相同，EntityId/EntityVersion由正式Owner投影，不能用技术key代造业务版本。EvidenceRoot.ReservedKey尚无ObjectRef时，PendingPublication/活动写入由Store协调器保护；若真实协调边界未接收或根无法全部表达，resolver返回Fault/Incomplete并阻GC，**不能略掉ReservedKey后Complete=true**。本轮Fake仅在封闭技术目录中证明此拒绝与根保留，不宣称真实resolver接入完成。

#### 8.4.4 定向读取完整性与资格证据

ResolveEvidence返回Metadata及精确References，全部必需父子单独授权/核身份。FileReadRequest Offset=0/Count=Object.Bytes为全读（空对象Count=0合法）；range按checked边界且绝不越界探测。借来的IFileObjectReadLease.Content只在本Runtime内读取，外部只得到EvidenceChunk；小于buffer的正长读取继续。VerifyBeforeDelivery先在MaxVerificationSpoolBytes与MaxBufferedBytes之内私有暂存全内容，准确EOF/长度/hash及必需闭包全部通过、FileObjects.VerifyAsync核原对象、交付前再次权限/hash后才交lease；读过首块或上游Verified标签本身不能替代模块实际核验。spool超限拒绝，不能静默改StreamingVerify。

StreamingVerify保持§7.3.1最后非空数据块与下一独立空EOF；全对象EOF终检前Integrity=Verifying，range始终PartialUnverified，无论上游Verify是否通过；后者可作为另一个全对象观察，不改变已交付range语义。撤权/尾部损坏/超期停止交付，返回空非EOF错误块；已交字节不可召回，显示lease仍监视Stamp/代次并调用CheckDeliveryAsync。MetadataOnly不开字节流、不宣称FullVerified。任何闭包缺失不得删除父项后伪装完整。

技术验收输出冻结为B.5 `EvidenceBridgeObservation`，由Runtime.Tests Host记录于测试进程内，正式产品审计另归Owner。它含原技术mutation/Task/资源状态、预期/实际字节hash/长度、授权观察代次、Phase与主错/cleanup错，**不含PASS/质量放行、令牌、SQL、路径或图像**；Fake、真实软件集成、介质/现场EvidenceClass必须分开。本轮只定义形状，不创建报告文件或声称测量。

## 9. 无 UI 最小调用顺序

### 9.1 G1 的两个完整无 UI Host

下列一个完整C#源块包含两个独立Host类、唯一Exe入口及共享的**合成夹具构造代码**。两Host各调用Build，分别创建新Core、Catalog、Profile、请求及快照，不共享运行实例或全局状态；共享代码只减少重复字段，不是产品C-04/Runtime封装。获准实施后此代码在唯一Core.Tests内运行，不创建额外Host工程。只引用.NET10 BCL和Core；所有模块类型的公开构造约定见B.1，代码无待替换变量/外部文件/窗口/设备/数据库/授权服务。规范预期供实施者编译后核验，本轮没有实际DLL/build/run证据。

夹具字节仅是测试中声明摘要的来源，媒体为非图像`application/octet-stream`，诊断/结果两个角色保留不同SourceId；这是纯描述检查，不证明日志格式/实际保存内容。资产、事实、请求和Receipt的合成摘要使用分离Synthetic域，仅检格式/比较，不能冒充产品批准canonical。

```csharp
using System;
using System.Collections.Immutable;
using System.Linq;
using System.Security.Cryptography;
using System.Threading;
using Asun.Modules.InspectionEvidence;

internal static class CoreHostFixture
{
    public static (CoreContext Context, CommitDescription Description,
        OperationSnapshot Snapshot) Build(string scope)
    {
        ScopedId Id(string value) => new(scope, value);
        DigestValue Digest(string domain, string canonical, byte[] bytes) =>
            new(domain, "SHA-256", canonical,
                Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant());
        VersionReference Asset(string value, byte marker) => new(Id(value), 1,
            Digest("SyntheticAsset/v1", "SyntheticBytes/v1", new byte[] { marker }));
        var catalogVersion = Asset("catalog-1", 1);
        var profileVersion = Asset("profile-1", 2);
        var method = Asset("method-1", 3);
        var calibration = Asset("calibration-1", 4);
        var encoding = Asset("encoding-1", 5);
        var calculation = Asset("calculation-1", 6);
        var catalog = new CatalogSnapshot(
            Version: catalogVersion,
            DigestRules: ImmutableArray.Create(
                new DigestRule("StoredBytes/v1", "SHA-256", "ByteSequence/v1", 64),
                new DigestRule("SyntheticAsset/v1", "SHA-256", "SyntheticBytes/v1", 64),
                new DigestRule("SyntheticFact/v1", "SHA-256", "SyntheticBytes/v1", 64),
                new DigestRule("SyntheticRequest/v1", "SHA-256", "SyntheticBytes/v1", 64),
                new DigestRule("SyntheticManifest/v1", "SHA-256", "SyntheticBytes/v1", 64),
                new DigestRule("SyntheticReceipt/v1", "SHA-256", "SyntheticBytes/v1", 64)),
            References: ImmutableArray.Create(catalogVersion, profileVersion,
                method, calibration, encoding, calculation),
            FactContracts: ImmutableArray.Create(new ContractKey("SyntheticFact", "v1")),
            ResponseContracts: ImmutableArray.Create(new ContractKey("EvidenceCommit", "v1")),
            MediaRoles: ImmutableArray.Create(
                new MediaRoleRule("application/octet-stream", EvidenceRole.Diagnostic, false, false),
                new MediaRoleRule("application/octet-stream", EvidenceRole.ResultArtifact, false, false)),
            Relations: ImmutableArray.Create(new RelationRule("supports", false,
                ImmutableArray.Create(EvidenceRole.ResultArtifact),
                ImmutableArray.Create(EvidenceRole.Diagnostic))),
            ChannelKeys: ImmutableArray<string>.Empty,
            ReasonKeys: ImmutableArray.Create("optional_missing"),
            PixelTypeKeys: ImmutableArray<string>.Empty);
        var sourceA = new SourceBinding(SourceKind.Diagnostic, Id("event-a"),
            null, null, null, null, new DateTimeOffset(2026, 10, 11, 0, 0, 0, TimeSpan.Zero),
            ImmutableArray.Create(method, calibration));
        var sourceB = sourceA with { SourceId = Id("event-b") };
        var sourceSummary = new SourceBinding(SourceKind.Fact, calculation.Id,
            null, null, null, null, null, ImmutableArray.Create(method, calibration));
        var logA = new EvidenceDescriptor(Id("log-a"), EvidenceRole.Diagnostic,
            "application/octet-stream", 3,
            Digest("StoredBytes/v1", "ByteSequence/v1", new byte[] { 1, 2, 3 }),
            sourceA, encoding, null);
        var logB = logA with { LogicalId = Id("log-b"), Source = sourceB };
        var summary = new EvidenceDescriptor(Id("summary"), EvidenceRole.ResultArtifact,
            "application/octet-stream", 2,
            Digest("StoredBytes/v1", "ByteSequence/v1", new byte[] { 4, 5 }),
            sourceSummary, encoding, null);
        // RequiredItem独立分配并反序，验证Versions按内容集合比较。
        var requiredSource = sourceA with { Versions = ImmutableArray.Create(calibration, method) };
        var profile = new ValidationProfile(
            Version: profileVersion, MaxObjects: 4, MaxAbsences: 4, MaxLinks: 8,
            MaxGraphDepth: 4, MaxReferences: 64, MaxCatalogEntries: 64,
            MaxObjectBytes: 8, MaxTotalBytes: 16, MaxChunkBytes: 4,
            RequiredRoles: ImmutableArray.Create(EvidenceRole.Diagnostic),
            RequiredItems: ImmutableArray.Create(
                new RequiredEvidenceItem(logA.LogicalId, logA.Role, requiredSource)),
            RequiredVersionIds: ImmutableArray.Create(method.Id, calibration.Id),
            AllowEmptyEvidence: false);
        var evidence = new EvidenceRequest(scope,
            ImmutableArray.Create(summary, logB, logA),
            ImmutableArray.Create(
                new EvidenceLink(summary.LogicalId, logA.LogicalId, null, 0, "supports", null),
                new EvidenceLink(summary.LogicalId, logB.LogicalId, null, 1, "supports", null)),
            ImmutableArray<EvidenceAbsence>.Empty,
            ImmutableArray<VersionReference>.Empty);
        var fact = new FactReference(calculation, "SyntheticFact", "v1",
            Digest("SyntheticFact/v1", "SyntheticBytes/v1", new byte[] { 7 }));
        var description = new CommitDescription(Id("commit-1"), fact, evidence,
            Digest("SyntheticRequest/v1", "SyntheticBytes/v1", new byte[] { 8 }),
            null, profileVersion);
        var snapshot = new OperationSnapshot(description.Identity, "EvidenceCommit", "v1",
            null, CommitOutcome.NotFound, null, ResourceState.NotStarted);
        var context = new CoreContext(profile, catalog, TimeSpan.FromSeconds(1), TimeSpan.Zero);
        return (context, description, snapshot);
    }

    public static void Require(bool condition, string id)
    {
        if (!condition) throw new InvalidOperationException(id);
    }
    public static bool Has(ImmutableArray<ValidationIssue> issues, string code) =>
        issues.Any(issue => issue.Code == code);
}

internal static class ProductionPlanHost
{
    public static void Run()
    {
        var (context, description, snapshot) = CoreHostFixture.Build("host-production");
        IInspectionEvidenceCore core = new InspectionEvidenceCore();
        var token = CancellationToken.None;
        var valid = core.Validate(description.Evidence, context, token);
        var stage = core.PlanStage(description.Evidence, context, token);
        var plan = core.PlanCommit(description, snapshot, context, token);
        var status = core.EvaluateOperation(snapshot, context, token);
        CoreHostFixture.Require(valid.IsValid && valid.Issues.IsEmpty, "H1.Valid");
        CoreHostFixture.Require(stage.Issues.IsEmpty && stage.TotalDeclaredBytes == 8 &&
            stage.Entries.Select(e => e.LogicalId.Value).SequenceEqual(
                new[] { "log-a", "log-b", "summary" }) &&
            stage.Entries[2].ParentIds.Select(id => id.Value).SequenceEqual(
                new[] { "log-a", "log-b" }), "H1.Stage");
        CoreHostFixture.Require(plan.Issues.IsEmpty && plan.Action == CommitPlanAction.NewCandidate &&
            plan.Stage is not null, "H1.NewCandidate");
        CoreHostFixture.Require(status.Issues.IsEmpty && status.CandidateOutcome == CommitOutcome.NotFound &&
            status.Resources == ResourceState.NotStarted, "H1.SnapshotOnly");
        var changedSource = description.Evidence.Descriptors[2].Source with
            { SourceId = new ScopedId("host-production", "wrong-event") };
        var invalid = description.Evidence with { Descriptors =
            description.Evidence.Descriptors.SetItem(2,
                description.Evidence.Descriptors[2] with { Source = changedSource }) };
        var rejected = core.PlanStage(invalid, context, token);
        CoreHostFixture.Require(CoreHostFixture.Has(rejected.Issues, "IEV-IDENTITY-002") &&
            rejected.Entries.IsEmpty && rejected.TotalDeclaredBytes == 0, "H1.SourceMismatch");
        // 原描述/上下文没有被改写；恢复为同一纯计算输入，不重试任何写入。
        CoreHostFixture.Require(core.PlanStage(description.Evidence, context, token).Issues.IsEmpty,
            "H1.CorrectInput");
        var expired = context with { Elapsed = context.Budget };
        var timedOut = core.PlanStage(description.Evidence, expired, token);
        CoreHostFixture.Require(CoreHostFixture.Has(timedOut.Issues, "IEV-TIMEOUT-008") &&
            timedOut.Entries.IsEmpty && timedOut.TotalDeclaredBytes == 0, "H1.Elapsed");
        using var cancellation = new CancellationTokenSource();
        cancellation.Cancel();
        var cancelled = core.PlanStage(description.Evidence, context, cancellation.Token);
        CoreHostFixture.Require(CoreHostFixture.Has(cancelled.Issues, "IEV-CANCEL-009") &&
            cancelled.Entries.IsEmpty && cancelled.TotalDeclaredBytes == 0, "H1.Cancelled");
    }
}

internal static class ReplayDescriptionHost
{
    public static void Run()
    {
        var (context, description, initial) = CoreHostFixture.Build("host-replay");
        IInspectionEvidenceCore core = new InspectionEvidenceCore();
        var token = CancellationToken.None;
        var unknown = initial with { Outcome = CommitOutcome.Unknown,
            RequestDigest = description.RequestDigest, Resources = ResourceState.ResourcesReleased };
        var observed = core.EvaluateOperation(unknown, context, token);
        var queryPlan = core.PlanCommit(description, unknown, context, token);
        CoreHostFixture.Require(observed.Issues.IsEmpty && observed.CandidateOutcome == CommitOutcome.Unknown &&
            observed.Resources == ResourceState.ResourcesReleased && observed.Recovery == RecoveryAction.QueryOriginal &&
            queryPlan.Action == CommitPlanAction.QueryRequired && queryPlan.Stage is null,
            "H2.UnknownNotCommitted");
        var receipt = new ReceiptReference(new ScopedId("host-replay", "receipt-1"),
            description.Identity, 1, description.RequestDigest,
            new DigestValue("SyntheticManifest/v1", "SHA-256", "SyntheticBytes/v1", new string('a', 64)),
            new DigestValue("SyntheticReceipt/v1", "SHA-256", "SyntheticBytes/v1", new string('b', 64)));
        var suppliedCommitted = unknown with { Outcome = CommitOutcome.Committed, Receipt = receipt };
        var replay = core.PlanCommit(description, suppliedCommitted, context, token);
        CoreHostFixture.Require(replay.Issues.IsEmpty && replay.Action == CommitPlanAction.ReplayCandidate &&
            replay.Stage is null, "H2.ProvidedSnapshotCandidate");
        var conflictDescription = description with { RequestDigest =
            description.RequestDigest with { Hex = new string('c', 64) } };
        var conflict = core.PlanCommit(conflictDescription, suppliedCommitted, context, token);
        CoreHostFixture.Require(conflict.Action == CommitPlanAction.ConflictCandidate && conflict.Stage is null &&
            CoreHostFixture.Has(conflict.Issues, "IEV-CONFLICT-004"), "H2.SameIdDifferentDigest");
        var wrongCatalog = context.Catalog with { ResponseContracts =
            ImmutableArray.Create(new ContractKey("OtherOperation", "v1")) };
        var wrongContext = context with { Catalog = wrongCatalog };
        var wrongPlan = core.PlanCommit(description, initial, wrongContext, token);
        var wrongStatus = core.EvaluateOperation(initial, wrongContext, token);
        CoreHostFixture.Require(wrongPlan.Action == CommitPlanAction.Blocked && wrongPlan.Stage is null &&
            CoreHostFixture.Has(wrongPlan.Issues, "IEV-CAP-006") &&
            CoreHostFixture.Has(wrongStatus.Issues, "IEV-CAP-006"), "H2.FullContractKey");
        CoreHostFixture.Require(core.PlanCommit(description, initial, context, token).Action ==
            CommitPlanAction.NewCandidate, "H2.RestoreCatalog");
    }
}

internal static class Program
{
    public static int Main()
    {
        int failures = 0;
        try { ProductionPlanHost.Run(); } catch (Exception ex) { ++failures; Console.Error.WriteLine(ex.Message); }
        try { ReplayDescriptionHost.Run(); } catch (Exception ex) { ++failures; Console.Error.WriteLine(ex.Message); }
        return failures == 0 ? 0 : 1;
    }
}
```

H1精确预期为Valid、父先子后总8字节的**声明计划**、NewCandidate及NotFound输入快照；SourceMismatch为IEV-IDENTITY-002且无半计划；恢复正确描述得到原计划；Elapsed≥Budget/预取消返回对应错误和空计划。H2的Unknown+ResourcesReleased保持Unknown/QueryOriginal；人工提供Committed快照只能得到ReplayCandidate，未核真实Receipt或字节；异摘要冲突，不创建新Stage；OtherOperation/v1不能命中EvidenceCommit/v1，修回目录后NewCandidate。两Host无外部I/O/native/后台Task，局部托管值自然离栈/回收；CTS只在H1由using释放，不创建Close/DrainUnknown流程来证明G1排空。整个Exe仍沿§12.1有限进程截止执行，未完成不返回成功。

### 9.2 后续门的提交与读取顺序

以下仅为**带显式输入参数的消费函数**，不能作为G1的Host或G2/G3正式映射已完成证据。实例由§8.2构造并在§6.2进程根下持有；参数必须来自已批准产品codec/授权绑定，未绑定只阻相应后续门。

```csharp
static async System.Threading.Tasks.Task ConsumeLaterGateAsync(
    IInspectionEvidenceRuntime runtime, CommitRequest request,
    AccessContext recoveryAccess, OperationBudget recoveryBudget,
    string expectedResponseVersion, EvidenceReadRequest read,
    Action<ReadOnlyMemory<byte>> consumeBytes,
    Action<ImmutableArray<ValidationIssue>> reportReadFailure,
    CancellationToken token)
{
CommitResult result = await runtime.CommitAsync(request, token);
if (result.Outcome == CommitOutcome.Unknown)
{
    var recovery = new CommitRecoveryRequest(request.Description.Identity,
        request.Description.RequestDigest, "EvidenceCommit", expectedResponseVersion,
        recoveryAccess, recoveryBudget, request.OperationId);
    // token若已取消/到期，不在此隐式刷新它；进程根另开有限恢复观察并保留原身份。
    CommitRecoveryResult recovered = await runtime.QueryOperationAsync(recovery, token);
    // 只有 recovered.Outcome == Committed 且原回执关系一致才能呈现已提交。
}

// Gate-3：read 是精确 Manifest/逻辑对象引用、读取模式、授权、代次和有限预算。
EvidenceReadResult opened = await runtime.ReadAsync(read, token);
if (opened.Lease is { } lease)
{
    await using (lease)
    {
        while (true)
        {
            using EvidenceChunk chunk = await lease.ReadChunkAsync(read.MaxChunkBytes, token);
            if (!chunk.Issues.IsEmpty) { reportReadFailure(chunk.Issues); break; }
            // EOF 是单独的空块；最后数据块 IsEnd=false，必须先消费并释放。
            if (chunk.IsEnd) break;
            // 在 chunk Dispose 前消费；每次交付仍由 lease 检查权限和期限。
            consumeBytes(chunk.Bytes);
        }
        IntegrityReport integrity = lease.Integrity;
        // 未达 FullVerified 的流不能被消费者当作已验证的 Replay 输入。
    }
}
// lease异常/迟到资源由Runtime根继续持有；函数离栈不证明已释放。
// 实例关闭统一在§6.2的独立有限cleanup中进行，业务token不作cleanup token。
}
```

接入方处理同键重放/冲突、取消/超时/响应丢失、磁盘满、摘要错误及重启，不能把catch转PASS、文件存在转Committed或UI关闭当撤销。`consumeBytes/reportReadFailure`是显式传入的宿主消费/投影回调，锁外调用且异常须由原Task观察，不是模块假API，也不能绕过读取守卫/提交边界。

### 9.3 两个从空Host装配的协议Fake消费者

以下为**未编译的完整Host规格源块**，位于唯一Runtime.Tests Exe；using显式引用Core/Runtime及本测试程序集内B.5协议夹具。`CoreHostFixture`类的完整源已在§9.1，实施时仅把该BCL夹具类（含Build/Require/Has）原样放入Runtime.Tests，不复制其Program/其它Host入口（不引用Core.Tests Exe、不改变G1的实现/测试源）；本段其余代码全部如下。Factory/Create及所有类型/方法均为B.5待实施公开合同，没有省略外部Store/权限/codec/配置或待替换变量。两Host分别Build不同Scope/Factory/Store/Auth/根/Runtime，只有不可变测试构造函数共享；不引用Shell、业务Schema、WPF、native、真实数据库或磁盘。

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Runtime.ExceptionServices;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.InspectionEvidence;
using Asun.Modules.InspectionEvidence.Runtime;
using Asun.Modules.InspectionEvidence.ProtocolFixtures;

internal static class ProtocolHost
{
    public static EvidenceProtocolFakeRig Build(string scope)
    {
        var (core, description, _) = CoreHostFixture.Build(scope);
        var version = new VersionReference(new ScopedId(scope, "protocol-fixture"), 1,
            new DigestValue("SyntheticAsset/v1", "SHA-256", "SyntheticBytes/v1",
                Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(
                    "IM015-PROTOCOL-1/fixture"))).ToLowerInvariant()));
        var options = new EvidenceProtocolFakeOptions(version,
            TimeSpan.FromSeconds(10), TimeSpan.FromSeconds(1),
            TimeSpan.FromSeconds(1), TimeSpan.FromSeconds(5),
            TimeSpan.FromSeconds(120), 16, 8, 1024 * 1024,
            65536, 131072, 64, 4);
        var sources = description.Evidence.Descriptors.Select(d =>
            new ProtocolSourceBytes(d.LogicalId,
                d.LogicalId.Value == "summary"
                    ? ImmutableArray.Create<byte>(4, 5)
                    : ImmutableArray.Create<byte>(1, 2, 3), 1)).ToImmutableArray();
        var fixture = new EvidenceProtocolFixture(core, description,
            new FrozenFactEnvelope(description.Fact, ImmutableArray.Create<byte>(7)),
            sources, new AccessContext(new ScopedId(scope, "fixture-auth"),
                "test-evidence", 0));
        return new EvidenceProtocolFakeFactory(options).Create(fixture);
    }

    public static (IInspectionEvidenceRuntime Runtime, EvidenceHostReservation Reservation)
        Attach(EvidenceProtocolFakeRig rig)
    {
        var reserved = rig.Root.TryReserve(rig.Dependencies, rig.RuntimeOptions);
        CoreHostFixture.Require(reserved.Reservation is not null &&
            reserved.Issues.IsEmpty, "P.Attach.Reserve");
        var owner = reserved.Reservation!;
        InspectionEvidenceRuntime runtime;
        try { runtime = new InspectionEvidenceRuntime(rig.Dependencies, rig.RuntimeOptions); }
        catch { owner.AbortBeforeAttach(); throw; }
        rig.HoldConstructed(owner, runtime); // Attach前fixture有限槽强持，异常仍由rig收尾
        owner.Attach(runtime);
        return (runtime, owner);
    }

    public static async Task<T> Run<T, TRequest>(EvidenceHostReservation owner,
        HostOperationIdentity identity, TRequest request, long borrowedBytes,
        int leaseSlots, TimeSpan wait, Func<ValueTask<T>> call, CancellationToken observer)
    {
        var reserved = owner.TryReserveTask(identity, borrowedBytes, leaseSlots, wait);
        CoreHostFixture.Require(reserved.Slot is not null && reserved.Issues.IsEmpty,
            "P.Task.Reserve");
        var slot = reserved.Slot!;
        Task<T> original;
        try { original = call().AsTask(); } // 一次AsTask；还没Task的同步失败只退空槽
        catch { slot.AbortBeforeTrack(); throw; }
        slot.Track(original, request); // 原Task、request/source在等待前强持
        try { return await original.WaitAsync(wait, observer); }
        catch { slot.DetachWaiter(); throw; } // Owner继续持有，finally不能关借用source
    }

    public static HostOperationIdentity CommitId(CommitRequest request) =>
        new("Commit", request.Description.Identity, request.Description.RequestDigest,
            request.OperationId, 0);
    public static HostOperationIdentity RecoveryId(CommitRecoveryRequest request) =>
        new("Recover", request.Identity, request.OriginalRequestDigest, request.OperationId, 0);
    public static HostOperationIdentity ReadId(EvidenceReadRequest request) =>
        new("Read", request.Reference.LogicalId, request.Reference.Receipt.RequestDigest,
            request.OperationId, request.RequestGeneration);

    public static async Task Consume(IEvidenceReadLease lease, EvidenceHostTaskSlot slot,
        EvidenceReadRequest request, byte[] expected, bool requireFull, CancellationToken token)
    {
        CoreHostFixture.Require(slot.AcceptLease(lease).IsValid, "P.Read.AcceptSameLease");
        var output = new List<byte>(expected.Length);
        Exception? primary = null;
        Exception? cleanup = null;
        try {
            while (true) {
                // lease自身有界操作槽/root已强持；每块原Task只消费一次。
                Task<EvidenceChunk> original = lease.ReadChunkAsync(request.MaxChunkBytes, token).AsTask();
                using EvidenceChunk chunk = await original;
                CoreHostFixture.Require(chunk.Issues.IsEmpty, "P.Read.NoIssues");
                if (chunk.IsEnd) {
                    CoreHostFixture.Require(chunk.Bytes.IsEmpty &&
                        chunk.OffsetBytes == expected.Length, "P.Read.SeparateEOF");
                    break;
                }
                CoreHostFixture.Require(!chunk.Bytes.IsEmpty &&
                    chunk.OffsetBytes == output.Count, "P.Read.DataOffset");
                output.AddRange(chunk.Bytes.ToArray());
            }
            CoreHostFixture.Require(output.SequenceEqual(expected), "P.Read.ExactBytes");
            CoreHostFixture.Require(!requireFull ||
                lease.Integrity.State == IntegrityState.FullVerified, "P.Read.FullHashClosure");
        } catch (Exception ex) { primary = ex; }
        // 不使用已取消业务token；Dispose有lease原Budget.Drain，root观察其原Task。
        try { await lease.DisposeAsync(); } catch (Exception ex) { cleanup = ex; }
        // lease/root已记录CleanupIssues；主错保持原栈，清理错不能覆盖它。
        if (primary is not null) ExceptionDispatchInfo.Capture(primary).Throw();
        if (cleanup is not null) ExceptionDispatchInfo.Capture(cleanup).Throw();
    }
}

internal static class SubmissionProtocolHost
{
    public static async Task Run(EvidenceProtocolFakeRig rig, CancellationToken suite)
    {
        var (runtime, owner) = ProtocolHost.Attach(rig);
        var request = rig.Commit; // Factory已经按ProtocolCanonical重算本夹具请求域
        var wait = rig.RuntimeOptions.StorageBridge.StorageWaitBudget;
        rig.SetFault(EvidenceProtocolFault.DropFinalizeResponse);
        var unknown = await ProtocolHost.Run(owner, ProtocolHost.CommitId(request),
            request, 262144, 0, wait, () => runtime.CommitAsync(request, suite), suite);
        CoreHostFixture.Require(unknown.Outcome == CommitOutcome.Unknown &&
            unknown.Receipt is null, "P1.ResponseLost.Unknown");
        var before = rig.Observe();
        CoreHostFixture.Require(before.SourceOpens == 3 && before.StageCalls == 3 &&
            before.FinalizeWrites == 1 && before.UnknownRoots > 0,
            "P1.OriginalWrites.RootPreserved");
        var recovery = rig.Recovery;
        var unresolved = await ProtocolHost.Run(owner, ProtocolHost.RecoveryId(recovery),
            recovery, 262144, 0, wait, () => runtime.QueryOperationAsync(recovery, suite), suite);
        CoreHostFixture.Require(unresolved.Outcome == CommitOutcome.Unknown &&
            rig.Observe().FinalizeWrites == 1, "P1.QueryNeverResubmits");
        rig.RevealOriginal(); // 只恢复原ledger可见，不补交事务
        var (second, secondOwner) = ProtocolHost.Attach(rig); // 新实例，原Store/codec精确恢复
        var recovered = await ProtocolHost.Run(secondOwner, ProtocolHost.RecoveryId(recovery),
            recovery, 262144, 0, wait, () => second.QueryOperationAsync(recovery, suite), suite);
        CoreHostFixture.Require(recovered.Outcome == CommitOutcome.Committed &&
            recovered.Receipt?.Reference.RequestDigest.Hex == request.Description.RequestDigest.Hex,
            "P1.OriginalReceipt");
        var replay1 = ProtocolHost.Run(owner, ProtocolHost.CommitId(request), request, 262144, 0,
            wait, () => runtime.CommitAsync(request, suite), suite);
        var replay2 = ProtocolHost.Run(secondOwner, ProtocolHost.CommitId(request), request, 262144, 0,
            wait, () => second.CommitAsync(request, suite), suite);
        var repeats = await Task.WhenAll(replay1, replay2);
        CoreHostFixture.Require(repeats.All(r => r.Outcome == CommitOutcome.Committed) &&
            rig.Observe().SourceOpens == 3 && rig.Observe().FinalizeWrites == 1,
            "P1.ConcurrentReplay.NoSecondSource");
        var malformed = request with { Fact = request.Fact with {
            Payload = ImmutableArray.Create<byte>(99) } };
        var bad = await ProtocolHost.Run(owner, ProtocolHost.CommitId(malformed), malformed, 262144, 0,
            wait, () => runtime.CommitAsync(malformed, suite), suite);
        CoreHostFixture.Require(bad.Outcome == CommitOutcome.Rejected &&
            rig.Observe().SourceOpens == 3, "P1.BadFact.NoIO");
    }
}

internal static class ReplayProtocolHost
{
    public static async Task Run(EvidenceProtocolFakeRig rig, CancellationToken suite)
    {
        rig.SeedCommitted(); // 合成技术状态，从空独立rig生成；不是执行产品生产提交
        var (runtime, owner) = ProtocolHost.Attach(rig);
        var read = rig.Read with { Mode = EvidenceReadMode.VerifyBeforeDelivery };
        var wait = rig.RuntimeOptions.StorageBridge.StorageWaitBudget;
        // Read需要AcceptLease，显式保存其预约/原Task；不使用会丢slot的Run辅助。
        async Task<EvidenceReadResult> Open(EvidenceReadRequest request, EvidenceProtocolFault fault)
        {
            rig.SetFault(fault);
            var reserved = owner.TryReserveTask(ProtocolHost.ReadId(request),
                rig.RuntimeOptions.MaxVerificationSpoolBytes, 1, wait);
            CoreHostFixture.Require(reserved.Slot is not null, "P2.Read.Reserve");
            var slot = reserved.Slot!;
            Task<EvidenceReadResult> original;
            try { original = runtime.ReadAsync(request, suite).AsTask(); }
            catch { slot.AbortBeforeTrack(); throw; }
            slot.Track(original, request);
            EvidenceReadResult result;
            try { result = await original.WaitAsync(wait, suite); }
            catch { slot.DetachWaiter(); throw; }
            if (result.Lease is { } lease)
                await ProtocolHost.Consume(lease, slot, request, new byte[] { 1, 2, 3 },
                    true, suite);
            return result;
        }
        var good = await Open(read, EvidenceProtocolFault.None);
        CoreHostFixture.Require(good.Status == EvidenceReadStatus.Opened &&
            good.Integrity.State == IntegrityState.FullVerified, "P2.Normal.Verified");
        var bad = await Open(read with { RequestGeneration = 2 }, EvidenceProtocolFault.TailCorrupt);
        CoreHostFixture.Require(bad.Status == EvidenceReadStatus.Corrupt && bad.Lease is null,
            "P2.TailCorrupt.NoDelivery");
        var denied = await Open(read with { RequestGeneration = 3 },
            EvidenceProtocolFault.RevokeBeforeDelivery);
        CoreHostFixture.Require(denied.Status == EvidenceReadStatus.PermissionDenied &&
            denied.Lease is null, "P2.RevokeAfterIO.NoDelivery");
        rig.Reauthorize(); // 明确新授权、新request；旧lease不可复活
        var fresh = rig.Read with { Mode = EvidenceReadMode.VerifyBeforeDelivery,
            RequestGeneration = 4 };
        var recovered = await Open(fresh, EvidenceProtocolFault.None);
        CoreHostFixture.Require(recovered.Status == EvidenceReadStatus.Opened &&
            rig.Observe().SourceOpens == 0 && rig.Observe().FinalizeWrites == 0,
            "P2.ReadRecovery.NoWrites");
        var hold = rig.Canonicalize(new RetentionRequest(
            new ScopedId(fresh.Reference.LogicalId.ScopeId, "decision-hold"),
            RetentionAction.Hold, fresh.Reference.Receipt.RequestDigest,
            rig.RuntimeOptions.Profile.Version, ImmutableArray.Create(fresh.Reference),
            null, rig.Dependencies.Clock.GetUtcNow().AddMinutes(1), fresh.Access,
            fresh.Budget, "protocol-hold")); // Policy/分钟仅本合成夹具，不是客户保留值
        var held = await ProtocolHost.Run(owner,
            new HostOperationIdentity("Retain", hold.DecisionIdentity, hold.DecisionDigest,
                hold.OperationId, 0), hold, 262144, 0, wait,
            () => runtime.ApplyRetentionAsync(hold, suite), suite);
        CoreHostFixture.Require(held.Outcome == CommitOutcome.Committed &&
            held.Receipt is not null && !held.Receipt.IsReleased, "P2.Hold.Registered");
        var query = new RetentionQuery(hold.DecisionIdentity, hold.DecisionDigest,
            fresh.Access, fresh.Budget, "protocol-hold-query");
        var queried = await ProtocolHost.Run(owner,
            new HostOperationIdentity("RetainQuery", query.DecisionIdentity,
                query.OriginalDecisionDigest, query.OperationId, 0), query, 262144, 0, wait,
            () => runtime.QueryRetentionAsync(query, suite), suite);
        CoreHostFixture.Require(queried.Receipt?.HoldId == held.Receipt!.HoldId &&
            rig.Observe().RetentionWrites == 1, "P2.HoldQuery.NoWrite");
        var release = rig.Canonicalize(hold with {
            DecisionIdentity = new ScopedId(hold.DecisionIdentity.ScopeId, "decision-release"),
            Decision = RetentionAction.ReleaseHold, ExistingHoldId = held.Receipt!.HoldId,
            HoldUntilUtc = null, OperationId = "protocol-release" });
        var released = await ProtocolHost.Run(owner,
            new HostOperationIdentity("Retain", release.DecisionIdentity, release.DecisionDigest,
                release.OperationId, 0), release, 262144, 0, wait,
            () => runtime.ApplyRetentionAsync(release, suite), suite);
        CoreHostFixture.Require(released.Receipt is { IsReleased: true } &&
            rig.Observe().RetentionWrites == 2 && rig.Observe().CommittedRoots > 0,
            "P2.ReleaseOnlyDecisionRoot");
    }
}

internal static class ProtocolProgram
{
    public static async Task<int> Main()
    {
        using var suite = new CancellationTokenSource(TimeSpan.FromSeconds(60));
        var rigs = new List<EvidenceProtocolFakeRig>(2); // suite根强持，不能在catch删除
        int failures = 0;
        foreach (bool submission in new[] { true, false }) {
            EvidenceProtocolFakeRig? rig = null;
            Exception? primary = null;
            RootDrainResult? cleanup = null;
            Exception? cleanupError = null;
            try {
                rig = ProtocolHost.Build(submission ? "protocol-write" : "protocol-read");
                rigs.Add(rig); // Factory同步零IO，第一次异步调用前已有suite强根
                if (submission) await SubmissionProtocolHost.Run(rig, suite.Token);
                else await ReplayProtocolHost.Run(rig, suite.Token);
            } catch (Exception ex) { primary = ex; }
            finally {
                if (rig is not null) {
                    rig.ReleaseBarriers(); // 异常也解除仅此Fake闩锁，实际IO无此测试捷径
                    try { cleanup = await rig.CloseAsync(CancellationToken.None); }
                    catch (Exception ex) { cleanupError = ex; }
                }
            }
            if (primary is not null || cleanupError is not null || rig is null ||
                cleanup?.State != RootState.Released ||
                rig.Observe().ActiveTasks != 0 || rig.Observe().ActiveLeases != 0 ||
                rig.Observe().RetainedBytes != 0) {
                ++failures;
                Console.Error.WriteLine(submission ? "P1 未完成" : "P2 未完成");
                if (primary is not null) Console.Error.WriteLine(primary.GetType().Name);
                if (cleanupError is not null) Console.Error.WriteLine("清理：" + cleanupError.GetType().Name);
                // rigs仍保留未Released实例/原Task，外层watchdog只判未完成，不判成功。
            }
        }
        return failures == 0 ? 0 : 1;
    }
}
```

`ProtocolHost.Attach`只有构造new本身抛出且未返回实例才AbortBeforeAttach；已构造实例先由rig.HoldConstructed的有限槽强持，再Attach。Attach失败仍由rig关闭此对应实例，不以Pending空或throw判已释放，不扫描/关闭其它Host实例。成功Attach后两根指向同一资源Owner，rig只是suite强根，不重复Dispose。本Host及收尾指导已获主控限定内容接收，实际实现准入和后续代码任务另行接收，本轮无C#编译/运行证据。

正常全过程：P1授权/Resolve→Reserve→源Open→Stage至EOF/hash→短lease+PendingPublication→再次权限/Verify→Finalize→原响应；故障/恢复为响应遮蔽Unknown→原身份只读Unknown→解除遮蔽→新实例只读原Receipt→双实例幂等重放。P2独立Seed→Resolve精确关系→OpenRead/spool全核→再次权限→受控chunk/独立EOF→lease真实释放；尾部损坏/交付前撤权均零lease交付，新授权/代次重新读取原对象，零生产写入。factory-generated Fixture.Read只指向log-a，ObjectId=`object-log-a`、Revision=1/StoredBytes digest；其它两对象为object-log-b/object-summary，不以相同byte hash合并。Receipt Id=`receipt-commit-1`/Revision=1，Manifest Id=`manifest-commit-1`/Revision=1，UTC固定夹具起始；摘要域按B.5重新计算，各对象必须存完整描述/关系并匹配原logical身份。Host的262144byte预约是本合成夹具完整payload/result/输入/source/buffer闭包保留上界（64KiB输入+128KiB结果+8byte源+其余有限结构），不是仅按8byte源预约；Fake实际计账超过该上界立即失败，不能继续分配。Read的1MiB预约包含其原Task/请求/副本与spool，不另绕过根额度。

P1/P2是完整基本消费Host；其Main的0仅表示这两个流程成功，**不是整个技术切片验收通过**。§12.3故障suite独立入口也位于同Runtime.Tests Exe，通过命令行`--protocol-all`选择，默认跑两个Host；`--protocol-all`执行表中全部必需断言，任何未注册/未完成/跳过均非零，不能以Host的0替代完整suite。暂无实际测试入口，表内调用/预期是实施合同，不是已运行测试。

## 10. 可选 UI 契约（Gate-3 投影；Gate-2/3 后续范围）

UI 是投影，不是事实写者。可选控件只调用上述核心端口，不能直接持有数据库连接、文件路径或 native 句柄。推荐页面角色为 `Evidence Viewer`，命令仅表达意图：`OpenEvidence`、`NavigateGraph`、`OpenFrame`、`CompareAttempts`、`VerifyHash`。通用筛选、分页和导出按钮必须交由宿主调用 `IM-045`，不能伪装成 IM-015 能力。

必须支持 `Ready / Busy / Empty / Stale / Blocked / RecoverableError / PermissionDenied / Completed` 八态；每态显示当前身份、状态原因和一个安全的下一动作。`Committed` 与检测 `PASS` 分开显示；合法 `NG`/`Unknown` 可读但不授质量放行。需要条件检索或导出时，页面显示宿主/`IM-045` 返回的用途、范围、缺项和回执，不把当前证据页伪装成完整数据集。

WPF/DevExpress 接入要求：

- 后台读/解码/校验不阻塞 UI；旧请求迟到不得覆盖新选择，关闭后显示 `CancelledPendingDrain` 直到资源排空。
- 附加量测/解释投影必须绑定当前请求、选择代次及精确证据来源，不能凭自身 metadata 授予读取权。可选详情错绑时清除受影响详情并报告缺项；已独立通过授权和完整性校验的图像可保留，不把详情错误解释为图像无权或质量 PASS。共同撤权、换对象或关闭时同时清除旧像素和敏感详情，迟到回调只可清理其捕获代次，不得清除新显示或复活旧事实。
- 三语资源覆盖标题、状态、错误、恢复动作和权限原因；字段 ID、hash、CommitIdentity、ManifestRevision 不随语言变化。
- 提供稳定 `AutomationId`、键盘取消/证据导航/校验路径；只在固定 1920×1080 验证视口检查布局，扣除任务栏、窗口边框、标题栏和状态栏。DPI 和三语在同一视口检查，不改变用户显示设置、不运行其它分辨率矩阵；UI 隐藏按钮不承担权限控制。
- 页面不得提供修改原始机判、ROI、程序、质量放行或设备动作的入口；复判/处置导航交对应宿主。

### 10.1 Evidence Viewer 的实施卡

生产操作员按宿主已知回执打开证据；复判人员按宿主已授权对象定位和对照；维护人员可查完整性与诊断。权限由读取端口执行，角色名不产生隐含权限。模块控件不带全局检索、导出、提交、设备按钮或语言切换器。

| 区域/控件组合 | 内容与任务 | 操作与可判定状态 |
|---|---|---|
| 顶部固定身份条 + DevExpress Bars | 提交身份、尝试、原始/派生角色、Manifest revision；技术提交状态与上游质量状态分列 | `OpenFrame`、`VerifyHash`、`CancelRead` 直达；长 hash 可查看/按字段权限复制，不截断身份为相似名称 |
| `DockLayoutManager` + `LayoutGroup/LayoutPanel` | 左侧证据树、中央影像、右侧只读 Inspector；保存/复位仅布局状态 | 主影像和关键状态不可关闭；浮动/复位须回到视口，布局恢复不触发读取/提交 |
| `TreeListControl` | 仅已授权 Manifest 闭包，按原图、派生、缺项分组；不生成通用查询 | 选中逻辑 ID 发起新代次读取；同 blob 的不同 FOV 保持独立节点；禁止通过树展开泄露隐藏父项 |
| 中央宿主公共图像控件；对照用 `DocumentGroup` | 最大可用影像区；原图与派生预览明确标识；两次尝试并列 | 同源坐标/标定可证明时才同步缩放定位；无法证明时独立显示并给原因，不自行配准 |
| 右侧只读字段投影，可用 `PropertyGridControl` | 长度、摘要域、实际校验状态、来源/父项、编码/生成版本、租约状态 | `ReadOnly=true`，仅绑定允许公开字段的专用投影；禁止直接绑定领域对象或自动枚举隐藏属性 |
| DevExpress 状态栏 + `SuperTip` | 实际读取/核验进度、有限期限、缺项、诊断码、一个安全恢复动作 | Hash 不符显示“证据损坏，读取已停止”；无权显示“无读取权限”；未知提交显示“提交结果未知，查询原回执” |

采用本机官方 25.2 XML 已存在的类型，不从 NuGet 下载；XML 中 `PropertyGridControl.ReadOnly` 的 value 描述与属性语义有歧义，实现先用只读投影阻断 setter，并在真实 WPF 验证不可编辑。控件对象和命令只属于可选 UI 包，不进入 Core 公共 DTO。具体 XAML 属性/事件在 UI 切片编译时按匹配资料绑定，不能把未核实属性写成已可编译示例。

默认布局中央影像优先，左树和右 Inspector 可折叠但主命令/身份/错误始终可见；长英文说明换行，hash 单独用等宽字体。统一宿主主题/矢量图标/焦点样式，不给原像素施加主题色；加载显示真实阶段，不用循环动画假装进度。八态下一动作固定：Ready→打开选中证据；Busy→取消读取；Empty→返回宿主选择；Stale→重新取得精确引用；Blocked→查看缺项原因；RecoverableError→按原引用重新读取；PermissionDenied→返回宿主处理权限；Completed→查看核验结果。错误文本和恢复按钮均从资源取得。

确定布局值是模块设计默认，可由宿主保存布局覆盖而不改变证据/权限：顶部身份区两行共64 DIP、命令条32 DIP、底部状态28 DIP；左右默认240/280 DIP（min=180/220、max=320/360），中央取余量，边距8、控件间距4，字体沿宿主标准正文14 DIP/标题16 DIP、hash等宽12 DIP。在唯一1920×1080验证viewport扣OS非客户区后排版；若DPI/三语使中央宽不足800 DIP，右Inspector先折叠、左树可折叠，身份/错误/取消不隐藏，详情区滚动而不压缩图像；不改显示分辨率。PropertyGrid只读专用投影无setter，关闭editor进入点，复制字段仍按权限；Docking拖移只能在本控件边界复位，不能把图像移出可见域。命令图标沿宿主矢量资源，ToolTip三语，切换/恢复由已有端口执行，不另造提交动作。不会新增自动参数：byte/1或3channel/完整domain按§15.1 PreviewProfile；未知坐标/标定则两图独立pan/zoom，禁止自行联动配准。

Tab 顺序：主命令→证据树→影像→Inspector→状态恢复动作；方向键只导航树，Enter 打开，Esc 取消当前读取，校验使用可见按钮并绑定宿主批准快捷键。焦点框和 UIA 名称随状态/语言更新；切换对象先清旧敏感像素再加载。控件提供 `SetCulture(string cultureName)`（仅 zh-CN/zh-TW/en-US 当前支持，不支持时返回本地校验错误），切换本控件资源和格式不影响其它宿主、请求代次或证据身份。主题/文化变更在 Dispatcher 执行，不重新提交或延长授权。

真实 WPF 验收在同一 1920×1080 视口完成：八态、两实例不同语言、长身份/英文、树→图联动、浮窗恢复、鼠标与键盘连点、慢读取消、撤权清像素、迟到回调、可选详情失败、关闭排空。视觉评审与行为评审分别接收；当前无已批准高保真稿或实测 WPF 结论。

## 11. 正常、边界与失败案例

### 11.1 正常

1. 合法事实带完整引用，两个 FOV 引用相同字节但不同逻辑来源：保存一个不可变 blob、两条逻辑关系，提交回执可查。
2. 结果为合法 `NG` 或方法 `Invalid`，证据完整：正常提交并保留原状态，质量层自行决定后续。
3. 生产提交响应丢失：按原 `CommitIdentity` 查询得到原回执，不能二次计算。
4. 复判按已知 Manifest/对象版本读取证据：权限变更或租约失效时旧读取被拒绝，不能回退到相似对象。

### 11.2 边界

1. 空证据集合只有在 Owner 注册的最小证据策略允许时才可提交；否则 `Blocked`，不以空集合表示“无缺陷”。
2. `lengthBytes=0` 仅在媒体/角色明确允许空对象时接受；普通图像空流拒绝。
3. 正负数、零面积、空测量、null 和 `Unknown` 按领域语义保存；不把 null 改成 0，不把无效读数变成 PASS。
4. 大对象接近 Profile 上限时在接纳前拒绝或按批准分块；不写一半才发现磁盘/内存超限。
5. 两 FOV 的字节摘要相同仍需要两条来源绑定；一个 FOV 的同一帧重复两次不能填补另一个 FOV。
6. 证据读取只接受明确的 UTC 时间戳用于诊断；不接受“最近一条”“最近 24 小时”或本地时间推断对象身份。

### 11.3 失败与恢复

1. 上传中断：尾部暂存隔离，查询原操作后从已核块续传；不把可打开的 `.part` 发布。
2. 哈希/长度不符：`IEV-HASH-003`，拒绝发布并保留诊断；不覆盖同定位对象。
3. 同键异载荷：`IEV-CONFLICT-004`，返回原提交摘要和冲突信息；不换键“帮助成功”。
4. 磁盘满/对象存储不可用：受影响写入停止，已有事实可读；不删除旧证据、不降低耐久。
5. commit 超时/断网/取消/Dispose：确定尚未发送则Rejected+对应原因；可能已发出但未确认才Unknown并查原回执。关闭资源与提交结论分开，不直接报告回滚、不释放未知保持根。
6. 已提交对象损坏：事实和原摘要保留，读取返回 `IEV-CORRUPT-010`；不以缩略图、相似图或最新图替代。
7. GC 与读取/新引用竞争：读 lease 或新根胜出时撤销删除资格；无法共同协调时停 GC。
8. Manifest 修订或权限撤回：旧租约/读取代次拒绝，已经交付的字节不声称可召回；重新授权后按明确版本建立新读取。

## 11A. 第二轮场景驱动架构复审

本节是反例复审，不是测试通过记录。G1只绑定本地Module API/Profile/不可变目录；下表含外部动作的G2/G3场景才另外绑定正式Contract/Owner/适配能力。缺项只阻断依赖该项的切片，不用默认值/UI补齐，不要求G1等待所有产品Contract。

| 场景 | 输入与参数来源 | 必须顺序 | 输出、状态与错误 | 恢复动作与可判定验收 |
|---|---|---|---|---|
| 正常单次提交 | 冻结事实、`CalculationIdentity`、`CommitIdentity`、完整证据流、版本/hash 引用；容量/超时/保持来自 Profile | 授权与版本检查 → 有界接纳 → 流式 hash/长度 → 编码尾完成 → 封口/耐久 → Manifest 关系检查 → 结果事务 | `Committed` + 原回执/Manifest；不得附带质量放行或设备结果 | 同一输入回读字节、关系和回执摘要完全一致；生产消费者可按原身份查询 |
| 合法 `NG`/`Unknown`/`Invalid` | 原 Owner 已声明质量状态和原因，证据策略允许失败结果；不把失败状态当参数缺失 | 只做身份、完整性、最小证据和持久性检查，不重算质量 | 合法状态可 `Committed`；若证据缺失则 `Blocked`，不是改为 PASS | 质量层读取原状态；验收断言为“保存成功≠质量通过、保存失败≠算法 NG” |
| 空输入/空证据 | 空事实、空证据或零长度流；允许性来自 RequiredEvidenceSet、媒体/角色和正式 Contract | 先判定空是否为注册语义，再申请资源；禁止先写空对象后补元数据 | 合法空测量可保存；不允许的空证据 `IEV-VAL-001`/`Blocked`；零长度图像 `Rejected` | 不产生半成品或假“无缺陷”；测试必须区分未选择、确实无证据和缺必需证据 |
| 部分上传/多对象部分成功 | 多个逻辑对象，某一流在块 N 断开、另一个已封口；块大小、总字节、并发来自 Profile | 每对象独立暂存和摘要；整体提交前核所有必需对象与依赖；不得把已完成对象单独发布成同一结果 | 暂存可 `RecoverableError`；整体结果不可见；已封口对象保留 lease；不返回部分 `Committed` | 按原操作和连续 offset 续传；丢失/冲突块隔离。验收为“结果事务全有或全无，暂存可清理/续传且不重复计数” |
| 歧义/错误输入 | 同键异载荷、身份跨范围、未知 revision、NaN/Infinity、单位/坐标不符、循环证据关系、未知媒体/角色 | 先限制字节/深度/对象数，再做强类型校验和摘要比较；不得读取相似记录 | `IEV-IDENTITY-002`、`IEV-CONFLICT-004`、`IEV-VAL-001` 或 `IEV-HASH-003`；无外部副作用 | 返回可定位字段和 Owner；不换键、不回退 latest、不生成默认坐标/单位。验收为零业务写入 |
| 超大对象/高并发 | 对象接近 Profile 上限；多个生产提交、回放读取和 GC 并发；队列、内存、连接和临时盘预算均显式 | 先取得有界额度，再分块流式处理；写入/定向读取/GC 使用分用途配额和保留槽；同一连接不并发 reader | 超限 `IEV-BUDGET-012`；池耗尽/锁等待按阶段报告；同键并发只有一个权威提交，其余读取原操作 | 有界背压、无无限 Task/连接/内存；验收为峰值资源不越 Profile、并发回放不产生第二事实、读取不饿死回执恢复 |
| 噪声/遮挡/退化视觉证据 | 上游提供原始噪声图、遮挡图、低对比度图或算法失败状态；本模块不接收“看起来像”的替代图 | 按字节和来源保存；只校验声明的媒体/长度/hash；不调用算法判断图像质量 | 图像字节有效即可保存并携带上游质量/Unknown；字节损坏 `IEV-CORRUPT-010`；不将噪声转成算法 PASS/NG | 回放读到原始字节和原质量状态；验收为损坏只报不可读，绝不回退相似帧、缩略图或最新图 |
| 取消/超时/native 排空 | 取消可能发生在读取、hash、cv2预览、flush、commit或交付；预算含清理余量 | 停止新阶段 → 观察流/operator/命令 → 查询commit是否已发 → 释放operator创建的视觉对象/流/reader/连接 → 归还额度 | 取消/超时按IEV分类；已发未确认Unknown；期限到达仍运行DrainUnknown，真实退出才Drained | 不在运行命令上并发rollback，不把Dispose/WaitAsync当回滚；native无泄漏、坏连接不回池、原身份可恢复 |
| 资源上限/磁盘满/适配器失能 | Profile 缺失、磁盘水位超限、对象存储/事务能力降级、Schema 能力未知 | 接纳前检查能力和空间；写入中超过阈值停止新对象，保留正在提交的恢复根 | `IEV-CAP-006` 或 `IEV-STORE-007`；已有事实可读，未知提交保持 `Unknown` | 维护后按原身份继续/查询；不得删旧证据、降低耐久、自动建空库或把文件存在当成功 |
| 持久化崩溃/重启/长期运行 | 任何 Stage/Seal/Publish/Commit/Outbox/GC 窗口崩溃；长期运行存在旧 epoch、租约续期、孤儿暂存、索引重建 | 启动先停新写 → 读取持久操作/回执/保持/epoch → 隔离旧 worker → 重建 lease/索引 → 再开放服务 | 每个操作进入 `Committed`、`Rejected`、`Unknown` 或可恢复暂存；旧 epoch 不能覆盖新租约 | 用同一身份恢复；租约续期需代次 CAS；GC 等待扫描/重建完成。验收为重启不重复事实、不丢保持、不重发设备动作 |
| 持久化/版本修订 | 新旧 Contract/Schema、hash canonical、媒体编码或 Manifest 修订；旧事实仍在保留期 | 启动核源/目标版本和变换摘要 → 只读兼容窗口 → 双读/迁移验证 → 再允许新写；禁止同名字段猜测 | 不兼容返回 `IEV-CAP-006`/`IEV-READ-011`；旧回执仍按旧语义读 | 回退到已验证旧适配器而不删除新事实；验收为单位、枚举、hash、Manifest 和保持语义不被静默改变 |
| 升级/回退 | 新核心或适配器部署中存在在途提交、outbox 和旧对象租约 | 停止新写或隔离 → 排空/确认未知 → 切换兼容读层 → 再开放写入 | 回退期间只读或明确 `Blocked`；旧租约过期，不续用新语义 | 旧版本读取新事实仅在兼容矩阵允许时进行；验收为不重用 `CommitIdentity` 写不同载荷、不重发设备副作用 |
| 无 UI 调用 | 最小 .NET 宿主注入端口、Profile、取消 token 和持久适配器；无窗口/VM/全局状态 | 构造实例 → 提交/回执读取/对象读取 → 明确处理 Unknown/错误 → Dispose/等待 Drained | 返回强类型回执、Manifest、对象流或错误；同步入口不得绕过异步预算 | 两个独立宿主使用同一核心；验收为可离线单元/契约/故障测试，核心不引用 WPF/DevExpress |
| 可选 UI | 只读 Evidence Viewer 投影、当前请求代次、八态、三语资源、授权读取意图 | UI 发起对象读取意图 → 核心授权/预算/Manifest/lease → UI 丢弃迟到响应 → 关闭只取消自身读取 scope | `Busy/Blocked/Stale/RecoverableError/PermissionDenied` 等可操作；不显示“保存=PASS” | UIA、键盘、DPI、权限和关闭排空在真实 WPF 另验；验收为 UI 没有第二写入口 |
| 第二消费者/长期读取 | 回放/复判按同一 Manifest 读取原图、参数和历史尝试；不注册通用查询 | 先读权限和精确版本 → 取得对象 lease → 流式读取/校验 → 释放 lease；不写事实 | 缺项、权限、损坏、过期分别报告；不把空读取解释为无问题 | 回放结果能定位原对象和摘要；验收为第二消费者不改变生产事实，GC 等待读取 lease 后再决定 |

### 11A.1 部分成功和原子性裁决

“部分成功”只允许发生在可恢复的暂存、分块或派生预览阶段，不允许出现在权威结果提交阶段。一次提交的所有必需逻辑对象、Manifest 关系、结果事实、Receipt 和 outbox 意图必须满足正式事务边界后共同可见；任一必需项失败，结果不可见但已持久对象可作为恢复输入。可选对象缺失必须由正式证据策略标成缺项/Unknown，不能悄悄从必需集合删除。多个事实若不属于同一 CommitIdentity，必须由调用方拆成不同提交，不由模块猜测合并。

### 11A.2 视觉证据路线与不支持能力

本模块不是算法、训练或推理模块，不提供训练数据选择、模型备用路线、阈值切换或算法恢复。算法异常、噪声、遮挡和退化由上游以带版本的事实/质量状态表达；本模块只保证保存和回读。若宿主需要视觉证据解码，路线固定为：

1. **主路线：不解码的字节路线。** 直接接收宿主提供的原始/派生字节流，按媒体类型、长度、摘要和来源保存；这是唯一不依赖 HALCON 运行时的 Replay 保存路线。
2. **可选预览路线：HALCON 26.05 受控解码。** 已核本地 [read_image](../../../halcon算子手册/operators/read_image.html) 的格式/像素语义；适配器经 `ImageLibDotNet.cv2` 的对应 operator 读取受控位置中的已验证字节，返回独立显示 lease。`serialize_image`/`deserialize_image` 只允许同一受控运行时的内部传递，不作为永久预览格式或跨版本 Replay 格式；手册中的 HALCON 原生 C# 类签名不是本项目公共调用入口。取消/失败等待 operator 真实退出，再释放其创建的视觉对象；native 对象、tuple、serialized handle 和指针不进入公共 DTO、持久数据、事件或共享缓存。
3. **派生显示路线：** `cv2` 对应 [write_image](../../../halcon算子手册/operators/write_image.html) operator 可生成派生预览；主保存路线保持上游原字节，本模块不重编码原图。JPEG 有损且不能证明原始像素/域保真，不能替代原始 Replay；预览独立记 `DerivedPreview`、父来源、生成版本、格式、长度和保存字节摘要。内部预览优先复用宿主公共图像控件直接显示；必须持久预览时编码参数由版本化预览 Profile 冻结，不让实施者现场任选 JPEG/TIFF。路径由适配器内部生成，不接受任意宿主路径。

明确不支持：把 HALCON serialized handle 当跨版本长期格式；使用 JPEG 预览替代原始输入；在本模块内做去噪、补洞、遮挡推断、重配准、质量重判或训练/推理；根据文件扩展名猜测媒体语义；在 native 对象未排空时回收连接、缓冲或租约。若目标运行时/编码无法证明兼容，返回 `IEV-CAP-006` 或 `IEV-CORRUPT-010`，不自动换路线。

### 11A.3 仍需主会话裁决的架构问题

| 问题 | 当前可执行边界 | 必须由谁裁决 |
|---|---|---|
| 正式事实与模块封套的产品绑定 | 模块Manifest/Receipt/Root及注册由B.6定义；不复制 C-01～C-08 的私有事实 Schema | C-04 接收业务validator/原事实子mutation和同事务绑定；不阻断 Gate-1 |
| 跨对象存储与元数据事务的原子可见边界 | 对象先持久并取得保持，再公开结果；无法证明则 `Unknown`/不可见 | C-04/C-07 与选定存储适配 Owner |
| 产品 canonical 与部署编码/加密版本 | 原请求/事实canonical归C-04，模块Manifest/Receipt/Root codec归B.6；部署加密不得改变原摘要语义 | C-04/C-06 接收业务映射/权限及部署版本；不阻断模块封套/纯格式/图校验 |
| Manifest/对象定向读取路线 | 只能读取已发布的不可变版本；版本/lease 无法证明时拒绝 | C-04/C-07 与证据 Owner |
| 权限撤回与对象交付守卫的生效点 | 取得 lease 和交付字节前复核；不声称已披露字节可召回 | C-05/C-06/授权 Owner |
| 保留、GC、备份 Hold、RPO/RTO 和真实耐久 | 无共同协调或真实 Profile 时停 GC/不宣称耐久 | C-07/数据主权 Owner |
| 真实视觉预览验收 | serialized item 只允许运行时内部传递；跨版本长期保存已明确不支持 | 视觉适配器切片实际编译/读图/取消资源验收；不是 AsunImage 依赖准入 |

## 12. 测试与验收矩阵

文档阶段只定义断言，不声称已执行。Gate-1 仅执行无 UI 纯 Core 测试，证明相同输入产生相同校验/计划/状态、错误分类边界明确且没有任何外部副作用。真实存储适配测试、持久化恢复和生产/第二消费者接入测试属于 Gate-2/3 的独立准入与验收，不能作为 Gate-1 的隐含依赖或已完成证据。

| 类别 | 门 | 最小用例 | 通过断言 |
|---|---|---|---|
| Contract/Schema | Gate-1 | 缺字段、未知版本、单位/坐标错绑、非有限数、未知枚举 | 明确 `Blocked/Rejected`，无副作用 |
| Identity/Idempotency | Gate-1 计划；Gate-2 权威提交 | 只读快照下同键载荷比较；后续门覆盖并发、重启和持久唯一性 | Pure Core 仅输出计划/冲突候选；Gate-2 同键同载荷复用原回执、异载荷冲突且不重复事实 |
| Recovery before allocation | Gate-2 | 同键同载荷丢响应后重投、同键异载荷、原状态不可查询、权限撤回 | 解析原操作先于流/暂存/对象分配；恢复查询无新写入；异载荷冲突；未知保留原身份；未经当前授权不披露原结果 |
| Hash domains | Gate-1 声明校验；Gate-2/3 内容核验 | 请求、事实、保存字节、Manifest、Receipt 摘要同长度但错域/错版本，或同值被当作跨域证明 | 按批准域/算法/canonical 规则分别核验；拒绝替代摘要；Pure Core 不冒充实际字节核验 |
| Evidence bytes | Gate-2 | 分块错序、重复块、部分上传、压缩尾未结束、长度/hash 错 | 不发布半对象；摘要覆盖保存字节 |
| Commit windows | Gate-2 | 对象前、对象后事务前、commit 响应丢失、通知丢失 | 状态可查询；未知不误报回滚/成功 |
| Quality semantics | Gate-1 校验；Gate-2 保存 | PASS、NG、Unknown、Invalid、NotMeasured、缺 Replay 输入 | Gate-1 不改判；Gate-2 保存与质量放行分开，坏结果不被静默拒绝 |
| Storage fault | Gate-2/3 | 磁盘满、连接断开、锁等待、Schema 不兼容、备份失败 | 有界恢复；资源归还；保留恢复线索 |
| Recovery | Gate-2/3 | 崩溃扫描、孤立暂存、旧 epoch、重复通知、旧租约 ACK | 旧执行不能覆盖新代；原事实可回读 |
| Typed response recovery | Gate-2 | 提交丢响应后冷重开，Receipt 被错解为快照，错操作种类/版本/请求摘要，缺字段或跨作用域关联 | 返回完整一致的原响应；错误种类/缺字段不靠默认值完成；只读恢复不增加事实、对象或 outbox |
| Retention/GC | Gate-3 | 共享 blob、多逻辑引用、读取 lease、备份 Hold、扫描后新引用 | 未证明无根不删除；删除未知保持隔离 |
| Directed read | Gate-3 | 未知 Manifest、修订冲突、对象缺失、lease 失效、摘要错误 | 只按明确身份读取；区分 `NotFound`/`PermissionDenied`/`Corrupt`；不回退相似对象 |
| Read delivery guards | Gate-3 | 块前、I/O 后、交付前撤权/到期，端点或选择换代，短读/越界，缓存迟到 | 停止后续交付、按原期限取消并真实排空；缓存不延长授权，range 校验不宣称全对象校验，不召回已交付字节 |
| Nested reference visibility | Gate-3 | 原图可见但其变换/父对象 metadata 隐藏、错版本、同 hash 错对象或引用源失效 | 对嵌套目标独立精确授权；按原因返回权限/不可用/损坏，不泄露引用，不省略后报告完整 |
| Multiple source closure | Gate-1 关系校验；Gate-2/3 保存/回读 | 上游声明两贡献源但只具备 A、重复/乱序通知、跨 attempt，拼图完整但 B 缺失 | 保留原批准关系、顺序和缺项；重复通知不新增关系，不计算覆盖、不补最新来源，不把拼图完整当检查完成 |
| Field image roles | Gate-2/3 | 普通光/UV 角色错绑、点位序号重复、原始源图缺失或损坏 | 角色和来源绑定在封口前核对；错绑/必需缺失阻断依赖结果，可选缺失返回明确缺项；不以另一通道或相邻点位填充 |
| Derived image graph | Gate-2/3 | 派生行图父对象缺失、父顺序变化、拼接/编码版本或 hash 不符、总览图被当作算法输入 | 校验完整父对象闭包、顺序、变换/编码版本和摘要；不完整派生对象不可发布，读取返回 `DerivedIncomplete`/`Corrupt`；算法入口拒绝总览图角色 |
| Field diagnostics | Gate-2/3 | 时间倒退、相同内容的不同事件、重复尝试、响应缺失、脱敏前超限、追加写入失败 | 每个事件保留独立身份和记录/批次 hash；异常按原顺序封存并标记；失败不改生产事实，正式必需日志按 Contract 阻断；不得把日志 ACK 当业务成功 |
| Evidence identity isolation | Gate-2/3 | 原始点位图、派生图、结果事实、错误证据和现场日志内容相同或相近，但逻辑身份、事件身份或来源不同 | 读取必须分别按各自精确身份和 Manifest 版本定位；相同 blob/日志内容不能跨类型或跨事件合并、覆盖或互相回退 |
| Authorization | Gate-2/3 | 写/定向读权限撤回、盲审字段、旧 lease | 交付守卫复核；不泄露受限信息 |
| Resource | Gate-1 纯逻辑；Gate-2/3 资源集成 | Pure Core 双实例与确定性；后续门取消每阶段、页面关闭、连接池耗尽、reader 未结束 | Gate-1 无隐藏共享状态；后续门无泄漏、最终 `Drained` |
| Consumers | Gate-2/3 | 生产提交 + 复判/Replay 读取；质量查询只读 | 生产事实只经 `CommitAsync` 提交；两消费者使用同一回执/保持/权限语义；查询不改事实 |
| UI (可选) | Gate-3 | 八态、三语、DPI、键盘、迟到响应、UIA、权限；可选详情错绑、共同撤权及旧回调清除 | 页面只投影；详情错误隔离于合法图像；共同撤权清除像素和敏感详情，旧回调不影响新项；真实 WPF 行为另验 |

Golden/Replay 数据必须保存输入快照、RuntimeManifest、算法/参数/坐标/标定引用、证据摘要、预期回执和已知非确定性；合成数据必须标记，不能冒充现场资格。

### 12.1 Gate-1 BCL Exe 的断言与有限执行

沿 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门) 的已批准约定：Core 是 `Microsoft.NET.Sdk/net10.0` 类库；Core.Tests 是 `Microsoft.NET.Sdk/net10.0/OutputType=Exe`，只 ProjectReference Core 与 .NET BCL，nullable/implicit usings 启用。没有 xUnit/NUnit/MSTest 包选择门。测试入口逐 ID 执行全部必需断言、累计 failures，失败/未完成/必需跳过均非零；只有全部完成返回0。不要执行 dotnet test 后以空结果宣称通过。本轮工程尚未创建，以下是未来切片的验证计划，没有运行 build/run。

确定性合成夹具 `IEV-SYN-v1`：ScopeId=`scope-a`，提交=`commit-1`，原图 logical=`raw-1/raw-2`，派生=`preview-1`；三对象长度分别3/3/2字节，总8，raw-1/raw-2 声明相同 StoredBytes 摘要但 SourceId/PositionId 不同；preview 的父 Order=0/1 对应两原图。保存字节摘要可由 BCL SHA-256 针对 `{1,2,3}` 和 `{4,5}` 生成；Core 不实读它们。版本 catalog/profile revision 均1、每域声明独立 SHA-256/CanonicalVersion；合成请求域 `SyntheticRequest/v1` 的摘要只是格式/比较夹具，不冒充批准产品 canonical。Profile 为显式测试值：MaxObjects=4、MaxAbsences=4、MaxLinks=8、MaxGraphDepth=4、MaxReferences=32、MaxCatalogEntries=64、MaxObjectBytes=8、MaxTotalBytes=16、MaxChunkBytes=4，required Acquisition、源引用目录 complete；Budget=1秒、Elapsed=0。数值只用于合成断言，不是生产默认/性能目标。

| ID | 输入变体 | 必须断言 |
|---|---|---|
| C-01 | 合法夹具；另在只读第二宿主调用同方法 | Valid；Entries 父先子后、total=8，两源 logical 均保留；结果与宿主语言/实例无关 |
| C-02 | default 数组/null 顶层、空证据不允许；单长8及9、total16及17、checked long 溢出 | 边界值接受，越界 IEV-BUDGET-012；非法必填 IEV-VAL-001；失败无半计划 |
| C-03 | 同 logical 重复、同 hash 不同 logical、Unicode不同但相似 ID、错 scope | 重复拒绝；不同 logical 不合并；Ordinal 保留两种不同 Unicode；错 scope 身份错误，不 trim 修正 |
| C-04 | preview 缺父、父环、非连续 Order、外部父未登记/角色未解析、深度4和5 | 必需闭包声明错误拒绝；深度上限精确；外部声明可计划但不声称真实父完整；本地父无须预填服务 revision |
| C-05 | NotFound/同摘要 Committed/InProgress/Unknown/异摘要及 PermissionDenied 快照 | 分别 NewCandidate/ReplayCandidate/ObserveCandidate/QueryRequired/ConflictCandidate/Blocked；NotFound 不比较不存在摘要，PermissionDenied 不披露摘要 |
| C-06 | Committed 无 Receipt、Receipt 错域/请求/提交/Manifest；同 hex 跨域 | 候选 Corrupt，不反序列化默认完成；跨域不能互证；资源 Released 不将 Unknown 变成功 |
| C-07 | 预取消、循环中 token 取消、Elapsed=Budget；两个实例/同实例并发32次相同输入 | 取消 IEV-CANCEL-009+无计划；超时 IEV-TIMEOUT-008；并发结果结构相同、无共享当前对象/时钟；无存储/native/设备调用 |
| C-08 | 对非法输入按不同枚举构造顺序运行；旧 v0.1/未知规则目录 | Issues 有固定排序，未知合同/规范返回 IEV-CAP-006/VAL；不猜字段或自动降级，Core 无 Dispose/关闭资源门 |
| C-09 | RequiredItems与descriptor的Source分别用独立ImmutableArray创建相同版本内容；将版本顺序反转；分别缺项/多项/重复Id/修改revision或Digest域、算法、canonical、Hex；另改Source任一标量/可空字段 | 独立分配和纯重排均精确匹配；缺/多/重复/改版本或来源字段均拒绝，不用record/ImmutableArray默认Equals。相同引用对象不免除字段合法性检查，default数组仍非法 |
| C-10 | snapshot Kind=EvidenceCommit、ResponseVersion=v1；ResponseContracts仅有(OtherOperation,v1)，再补(EvidenceCommit,v1)；另未知Kind或同Kind错Version | 仅另一操作同版本时IEV-CAP-006且无新提交/回放计划；完整(EvidenceCommit,v1)登记才继续快照形状/摘要检查；未知Kind拒绝IEV-VAL-001，错Version不自动降级。PlanCommit与EvaluateOperation都执行完整键检查 |

预取消/显式Elapsed超时是确定性断言。Core中途取消与方法完成存在合法竞争，测试用并发启动闩锁和有界大图触发取消，只允许“完整确定结果”或“取消且无半计划”，不承诺未公开的中途闩锁点，也不添加外部测试回调API。Runtime的中途次序由假端口闩锁确定，不用Sleep证明。每例 harness 有5秒有限截止，并发组30秒总截止（仅测试控制上限）；任何后台任务未结束判非零且不能称排空。Core无外部 I/O，运行入口无法中断时由下述外层进程截止兜底，故障不能当成功。

未来获准后从仓库根执行以下 PowerShell，build 外层180秒、run外层120秒；每次只终止本次新创建的 dotnet 进程树，不清理目录或其它宿主进程。两条正式命令是 `dotnet build <Core> -c Release` 与 `dotnet run --project <Core.Tests> -c Release`，在外层有限封装内分别顺序执行：

```powershell
function Invoke-EvidenceCheck([string[]]$CheckArgs, [int]$DeadlineMs) {
    $checkProcess = Start-Process -FilePath 'dotnet' -ArgumentList $CheckArgs -WindowStyle Hidden -PassThru
    if (-not $checkProcess.WaitForExit($DeadlineMs)) {
        $checkProcess.Kill($true)
        throw 'inspection-evidence verification timed out'
    }
    if ($checkProcess.ExitCode -ne 0) { throw "inspection-evidence exit $($checkProcess.ExitCode)" }
}
Invoke-EvidenceCheck @('build', 'src/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Core/Asun.Modules.InspectionEvidence.Core.csproj', '-c', 'Release') 180000
Invoke-EvidenceCheck @('run', '--project', 'tests/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Core.Tests/Asun.Modules.InspectionEvidence.Core.Tests.csproj', '-c', 'Release') 120000
```

### 12.2 后续门故障注入与两消费者

Gate-2 Runtime.Tests 用同一 BCL Exe 控制闩锁和 IM-066 合同假端口：同键32次竞争只能一份 Reserve/事实/回执/outbox；败者源打开计数0；分别在 source open、每块、Seal 返回、保持登记、事务发出/返回、恢复 Decode、通知队列处中断。假端口可返回“已写但响应丢失”、WrongSchema、非 Committed 默认 Receipt、迟到旧 epoch、明确未发出，断言各窗口状态与 §§5–8 一致。持久实际唯一性、崩溃/冷重开和耐久另以 IM-066 真实注册绑定验证，不拿进程内 fake 证明数据库事务。

Gate-3 Runtime.Tests 覆盖短块继续/真截短/多余字节、range checked 溢出、全 hash 尾部失败、父项撤权、StreamingVerify 未终检、VerifyBeforeDelivery 暂存满、未释放 chunk 背压、两实例共享Store、一实例Close不影响另一实例、读取取消后假 I/O 尚未退出、Close期限到达/后续恢复、同保持决定幂等/异摘要/ReleaseHold未知。断言权限守卫在 I/O 前后和交付前、byte额度有限、资源与业务 Unknown 分列、无假 Closed、所有实际释放计数恰一次。

根协调断言`H-ROOT-01/02`仅属G2/G3：TryReserve容量满时构造计数0；构造同步失败Abort空槽不碰宿主Store；跟踪原Task后观察到期/业务异常仍保留Task/借用输入；迟到Read lease未Accept不交旧页面，Detach与Accept竞争恰一方取得交付/清理责任；CloseTask已完成但Resources未Released不退槽；末chunk未Dispose保持DrainUnknown。`H-ROOT-03`：移交目标容量不足/无ack源仍拥有；目标先强持/ack同身份后源才Transferred，迟到资源只由目标清理；cleanup异常不能覆盖原业务错误，后续真实Released才归还额度。`H-G1-01/02`绑定§9.1两个Host全部断言，包含无参公开构造、独立输入数组、timeout/cancel/输入恢复与Unknown不变；G1不使用HostRoot/Close来伪造native资源。

读取末块断言 `R-EOF-01`：合法合成对象 `{1,2,3,4,5}`、MaxChunkBytes=3，控制假端口分别返回3/2字节，经§9循环必须消费 `{1,2,3}` 和 `{4,5}` 两个IsEnd=false数据块，随后取得OffsetBytes=5的独立空EOF；消费恰5字节、不丢尾/重复。另以1/2/1/1短块划分取得同一字节串，不能要求底层每次填满maxBytes。字节数恰为chunk上限倍数时同样追加空EOF；合法空对象首块即空EOF；range Offset=1/Length=3只消费指定3字节，EOF Offset=4且PartialUnverified。`R-EOF-02`：尾部hash错/真截短/多余字节返回非EOF错误块；原终检前的StreamingVerify数据不能当完整结果；未释放最后数据块时下一调用返回背压、不得提前终检/发EOF，释放后才继续。重复EOF调用无新I/O，所有块Dispose恰一次；Bytes非空且IsEnd=true及空成功非EOF块属于契约违规，测试必须失败。

真实两消费者在 §15.1 各自宿主验收：生产宿主 C-04 冻结提交（包括合法NG），回放/复判宿主仅读取同 Receipt/Manifest/保存原字节；第二消费者启动无 UI、无产品 Shell、无设备SDK，不取得写端口。原图、派生、日志同字节也必须各按逻辑身份读；所有重启/撤权/损坏/GC竞争均复用本节断言。WPF/视觉切片另外真实运行，不计入 Core Exe 的资格。

### 12.3 G2-T1 / G3-T1 协议Fake可执行断言

唯一测试工程沿§15.1 Runtime.Tests（net10.0/BCL Exe）；`dotnet run --project tests/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Runtime.Tests/Asun.Modules.InspectionEvidence.Runtime.Tests.csproj -c Release -- --protocol-all`为后续实施后的完整技术suite入口，**本轮未执行**。§9.3两Host为默认基本流程；`--protocol-all`包括这两流程与下表全部case。用固定输入、可控闩锁及独立suite原Task，60秒进程内截止/外层有限watchdog；超时/必需项跳过非零，释放所有fake闩锁后仍未知仅报未完成。故障在确定协议点注入，不用概率sleep；Runtime真实逻辑+完整边界Fake，真实IM-066 C1另以原Factory集成。

| ID / 切片 | 正常→反例→恢复输入与公开动作 | 必须断言 |
|---|---|---|
| T-01 / G2-T1 | §9.3 P1全流程，三个源逐次最大1byte；同payload双实例重放 | Stage到独立EOF累计8byte，SourceOpens=3/FinalizeWrites=1；同技术key/hash原回执；并发初次两Runtime对同Commit开始（新rig、无Seed）也只能Reserve活跃epoch一个、开源3次 |
| T-02 / G2-T1 | 改Fact.Payload={99}；另用Canonicalize后的不同有效EvidenceRequest但同CommitIdentity | 前者摘要错零新IO；后者完整请求digest不同且同技术键冲突IEV-CONFLICT-004，不能换id/补源；修回原请求只读重放原Receipt |
| T-03 / G2-T1 | DropFinalizeResponse→Query原Unknown→RevealOriginal→新实例Query | 原Finalize仅一次；响应未知保持Pending/Unknown根，当前权限后原完整kind/schema/hash/Receipt关系才Committed；查询本身Reserve/Finalize/Stage计数不变 |
| T-04 / G2-T1 | WrongResultSchema注入Reserve或Finalize response；删原Mutation索引/换技术Kind/Reference hash | Decode Corrupt/Blocked、零新源/发布；保留原索引及根，不能Receipt当Reservation、旧版本按当前codec解或route NotFound当安全重试；恢复原codec再按原身份查询 |
| T-05 / G2-T1 | BlockedStage闩锁让source已借用、viewer取消或WaitBudget到；同时CleanupFailure | 原Stage Task/流/options/source保持根，槽及RetainedBytes不退；未实际I/O结束Source Dispose数不增；cleanup独立预算、主错仍取消/未知，cleanup另列；ReleaseBarriers后原Task真实EOF/退出、释放一次才Released |
| T-06 / G3-T1 | §9.3 P2 VerifyBeforeDelivery、TailCorrupt/RevokeBeforeDelivery、新Stamp/代次恢复 | 首次实际全长hash+父闭包核验，损坏/撤权无lease/字节交付；新授权Read仍零Reserve/Finalize；旧显示代次收到Invalidated不得复活 |
| T-07 / G3-T1 | 新rig Seed；StreamingVerify log-a，MaxChunk=1；保留最后chunk再调用；下一空EOF；另Range=(1,1)、MetadataOnly | 未Dispose chunk时IEV-BUDGET-012且Read IO计数不增；三非空IsEnd=false后独立空EOF offset3、FullVerified；range仅byte2/offset1→EOF offset2且PartialUnverified；Metadata不开流/Verify，不称FullVerified |
| T-08 / G3-T1 | LateReadLease暂停OpenRead返回；DetachWaiter/Cleanup先胜；ReleaseBarriers才返回成功lease | 迟到lease归原Root关闭，不交旧Host；原OpenTask/lease释放Task/依赖保持有限槽，直到真实Released；若Accept先胜Root不并发Dispose，consumer还chunk后再关闭；超容量请求零新I/O |
| T-09 / G3-T1 | §9.3 Hold→Query→Release决定；短TTL到期/实例Close；Hold.Renew版本错误；读中TTL失效 | 持久决定CAS唯一，Query零写；Release只解除该HoldId，Committed/Unknown/Pending根不消失；短TTL不是durable route，Hold身份QueryOperation被拒，资源查询可用；旧ExpectedVersion冲突，过期后零交付 |
| T-10 / 两片 | IncompleteRoots或ReservedKey无ObjectRef；ListRoots跨SnapshotId/epoch/跳页/重复 | Fault/Incomplete且Complete=false，GC资格Blocked，不能略ReservedKey；补全同snapshot精确ObjectRef/生产Owner版本后才完整技术投影；此Fake不执行物理GC、不授真实resolver资格 |
| T-11 / 两片 | checked字节溢出、spool>1MiB、catalog/payload/results超预算、未知format/route/codec、租约MinTtl大于剩余期限 | 接纳/阶段边界typed拒绝，零新effect，不能改Streaming/延deadline；异常释放已有资源，拒绝释放借用在途流；版本恢复只可新有限观察/原身份 |
| T-12 / 两片 | 主错+清理错并存，Close重复/跨epoch，根Transfer目标超额/成功ack | 主错不覆盖、cleanup列齐；失败/Unknown移交源继续Owner，成功目标先接纳全部原Task/借用/lease并ack再退源；跨epoch拒绝不假Released；最终临时资源0，持久Unknown仍Unknown |

T-02有效重canonical仅供测试：rig另外公开`CommitRequest Canonicalize(CommitRequest request)`，按B.5 ProtocolCommit重算Fact/Request语义（Fact不合法仍拒绝），重建Contents只能用调用方明示sources，不填缺项/改逻辑身份；本用例用原三源但改变一个合法Relation/可选absence，必须满足Core Profile，不能以非法输入失败代替同键异载荷冲突。T-04/T-10损坏用`SetFault`的精确扩展枚举`MissingMutation/WrongOperationKind/WrongObjectHash/ChangedRootSnapshot/DuplicateRootSequence`；Fake只在响应副本注入，不改原记录，恢复`None`查询原值。T-08闩锁通过Observe确认停在Phase后才Detach，不能猜时间。测试内部Phase信号Task在rig MaxTasks槽中，全部超额拒绝，ReleaseBarriers保证不会永远等待。

## 13. 性能、容量与可观测性

生产资源/期限由ValidationProfile及OperationBudget提供；性能验收目标来自 §13.1 的 BenchmarkProfile，本页不把未实测数字称为合格。每次基准必须记录：

- 负载：对象数量、总字节、单对象大小、分块大小、Manifest 关系数、并发、冷/热缓存、慢接收方。
- 延迟：接纳、首块、hash、封口、flush、对象发布、事务 commit、回执读取、Manifest 读取、首字节和完整性校验的 P50/P95/P99。
- 资源：峰值/稳态内存、临时盘、连接/reader/lease 数、队列长度、字节水位、CPU/IO、GC 保持量和取消到实际排空时间。
- 恢复：每个崩溃窗口的恢复时间、重复副作用计数、未知回执解析时间、RPO/RTO（仅在批准 Profile 和真实介质证据下报告）。

结构化诊断至少含 `OperationId`、`CommitIdentity`/`ManifestRevision`、请求代次、阶段、Owner/适配器版本、输入/输出摘要、对象数/字节、队列/资源水位、错误码、是否已发送/提交、取消时间和 `Drained` 时间。日志分级并脱敏；不要记录原始图像、秘密、完整客户标识或任意 SQL。指标和日志不能改变事实或触发隐含重试。

### 13.1 可执行 BenchmarkProfile

Profile 是独立基准输入：`Version/InputDigest/ModuleVersion/CatalogVersion/ValidationProfileVersion`、`Gate/Scenario`、`ObjectCount/LinkCount/GraphDepth/ReferenceCount/CatalogCount/TotalDeclaredBytes`、`ChunkBytes/ConcurrentCalls`、`CacheMode(Cold/Warm)/SlowConsumer`、`WarmupCount/MeasurementCount/MinimumValidSamples`、`PerCallDeadline/RunDeadline/DrainDeadline`、`MaxManagedBytes/MaxNativeBytes/MaxSpoolBytes/MaxConnections/MaxLeases/MaxQueueEntries`、可空 `TargetP50/P95/P99/TargetCancelDrain/TargetRecovery` 及各目标 `SourceReference`。计数/期限正且有限；warmup可0，其它样本数>0；Core 的外部资源上限为0并断言无分配，不给它假存储测点；runtime限制直接使用批准 Profile，缺必需预算拒测。目标缺少时只诊断 `NotEvaluated`。

Core 基准测 Validate/PlanStage/PlanCommit/EvaluateOperation 各方法接纳至返回，返回即无外部资源 ResourcesReleased；输入分小图/高边数/深链/大量版本目录，以及同实例/双实例并发，精确记录托管分配峰值和失败样本。不能将 TotalDeclaredBytes 的巨大声明称为已经搬运了大图。Runtime 基准从接纳到最后租约/chunk/reader/暂存/额度 ResourcesReleased，另测首块、各Stage、核验、事务、恢复和取消到排空；VerifyBeforeDelivery 计入完整闭包及私有暂存，StreamingVerify 计入慢消费持有缓冲的时间。WPF测选择到首幅已授权图像和关闭到实际释放，视口仍1920×1080。

统计方法、失败/超时/删失处理直接复用 DEV-GOV-010 §3.1，不复制另一个分位算法。所有未完成/排空未知样本单列且基准不能报告通过；预热、样本计划和目标只能由被采纳消费者 Profile 冻结。超额资源、重复权威写入、Unknown被改成功、GC误删、撤权后交付均立即失败，不以速度达标抵销。硬盘 RPO/RTO 与客户节拍/负载目标须真实介质/客户输入；测量方法已冻结、目标值待 Profile 采纳。本轮没有性能实测。

### 13.2 G2-T1 / G3-T1 技术桥测点

复用§13.1 BenchmarkProfile和DEV-GOV-010统计口径，增加`BindingVersion/StorageProfileVersion/CodecVersion/EvidenceClass`、命令/响应大小与根页数维度。G2-T1测接纳→Authorize/Resolve→Reserve→SourceOpen→实际EOF/hash→Stage资源Released→publication保护观察→Verify→再次授权→Finalize发送/原Receipt→全部源/lease/session/额度Released；分别记录Unknown首观察与原身份回查耗时。G3-T1测Resolve闭包→每父授权→OpenRead→首块→实际EOF/hash/Verify→交付守卫→全部chunk/lease/spool释放，三个模式、range/空对象、慢consumer/尾部损坏/撤权/迟到Close各独立scenario。

负载维度为对象1/3/Profile上限、每源最大正读1/MaxChunk、同字节不同逻辑来源、冷/热/双实例竞争、payload/result在limit边界、完整/未完成root页、原Task/lease槽及借用byte达到上限/超1。资源断言按选定Profile：ProtocolFake示例MaxRetainedBytes=1MiB、MaxTasks=16、MaxLeases=8、MaxSnapshots=4、MaxConcurrentIo=1；仅测试限额，不是客户性能目标。计量包括source借用实际内存+hash器+buffer+spool+canonical/result副本+通知/查询任务槽，根不能只按8byte数据申请而忽略输入图/后端Task闭包。超额接纳零新IO；DrainUnknown/未完成/删失保留，不判性能通过。Fake可证明软件计账/调用序，不证明真实I/O时延、耐久、RPO/RTO/native/WPF/现场。目标阈值仍待消费者Profile采纳，未采纳只NotEvaluated，本轮无benchmark执行。

## 14. HALCON/AsunImage 适用性核对

提交、哈希、授权、事务隔离和 Manifest 定位属于非视觉事务，HALCON 算子不适用。可选预览按 §11A.2 经 `ImageLibDotNet.cv2` 调用 HALCON 26.05 对应算子；不另接 HOperatorSet/halcondotnet.dll，不核验算子是否存在，不扫描/修改 AsunImage 内部。官方手册的 native C# 签名仅供语义参考，只有封送/重载有歧义时查公开签名或消费项目编译。本轮没有实施或运行视觉调用。预览只能作派生显示，不替代原始证据/Replay。

## 15. 发布、回退与第二消费者

发布包至少拆分核心契约/实现、存储适配器、可选预览适配器和可选 WPF 投影；`IM-045` 的 Query/Export 包独立发布，不作为本模块依赖。每包标记版本、目标运行时、Schema/Contract 兼容范围、依赖摘要、迁移脚本摘要和许可证通知。发布前必须有契约校验、故障注入、性能 Profile、恢复演练和两个消费者接入证据。

回退步骤：停止新写入或按 Owner 定义的兼容窗口隔离 → 排空/观察在途提交和 outbox → 切换到已验证旧适配器/核心版本 → 保留新版本产生的事实和回执 → 用只读兼容层按 Manifest/对象身份读取 → 记录受影响范围。不得删除新事实、重用旧 `CommitIdentity` 写不同载荷、把迁移失败自动降为旧 Schema 生产写或重发设备动作。

第二消费者验收固定为：

1. 生产宿主提交合法 PASS/NG/Unknown/未测，并在响应丢失、磁盘满、同键重放后查询原回执。
2. 独立回放/复判宿主用同一保存闭包按 Manifest/对象身份读取原图、参数和历史尝试，验证缺项、权限、lease 和摘要；通用检索/导出另由 `IM-045` 处理，它不能修改生产事实。

质量统计可作为第三只读消费者，但其固定总体、分母、统计方法和放行语义由 `IM-045` 与质量 Owner 持有；IM-015 只提供被引用的事实和证据。

### 15.1 独立包、代码落点与最小消费者

以下均为后续获准才创建的 `NewProjectRequired` 落点，本轮不创建工程。公共契约先保留在 Core（仅BCL纯值），不为了目录整齐额外拆一个空 Contracts DLL；形成实际独立消费者与版本生命周期后才另行评审拆包。

| 切片/唯一工程 | namespace/依赖 | 唯一测试/验收宿主与允许范围 |
|---|---|---|
| `G1-Core`：开头绑定的 `Asun.Modules.InspectionEvidence.Core.csproj` | `Asun.Modules.InspectionEvidence`；net10.0、仅BCL；附录 B.1/B.2 | 开头 Core.Tests BCL Exe；仅这两个目录；§9的Core调用作为最小宿主，不创建额外演示产品 |
| `G2-Submission` 与 `G3-ReadRetention`（含本轮`G2-T1/G3-T1`技术桥）：`src/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Runtime/Asun.Modules.InspectionEvidence.Runtime.csproj` | `Asun.Modules.InspectionEvidence.Runtime`；net10.0→Core、IM-066 Contracts与Runtime（仅消费公开StorageRequestHasher）；B.6正式PostgreSQL注册mapping另外引用IM066 PostgreSql公开IPostgreSqlBindingCodec（不取得连接/命令/后端句柄，namespace为Asun.Modules.InspectionEvidence.Runtime.PostgreSql）。此引用仅服务受信任注册包，不增加Runtime创建数据库或产品事实权；G1/T1既有接收范围不增加A1运行要求。同一包/Owner/工作树，G2-T1再G3-T1串行；不另建生产存储后端、不写Owner业务Schema | `tests/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Runtime.Tests/Asun.Modules.InspectionEvidence.Runtime.Tests.csproj`；BCL Exe引用Runtime/Core及其IM-066公开依赖，§9.3/12.3边界Fake仅在测试程序集，不引用私有上游Tests。仅Runtime/Runtime.Tests目录；共享Core如需修改须单独重新接收本地契约，不能顺带改 |
| `G3-PreviewUI`：`src/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Wpf/Asun.Modules.InspectionEvidence.Wpf.csproj` | `Asun.Modules.InspectionEvidence.Wpf`；net10.0-windows/UseWPF，Core公开读取契约、本机DevExpress25.2.3、既有ImageLibDotNet/公共视口；不直接引用Runtime存储依赖 | `tests/Modules/inspection-evidence/Asun.Modules.InspectionEvidence.Wpf.Tests/Asun.Modules.InspectionEvidence.Wpf.Tests.csproj`；真实WPF STA宿主，固定1920×1080；仅两Wpf目录。不创建产品Shell或HTML假页面充当桌面验收 |

Gate-2/3 两宿主验收可位于同 Runtime.Tests Exe 的独立 `ProductionConsumer/ReplayConsumer` 夹具：生产仅依赖提交/恢复端口，第二消费者仅依赖 Reader/Retention只读查询；不同对象实例、不同权限引用、不同配置，无共享静态全局状态，Core两调用宿主也分实例。正式客户宿主名称/代码路径在接入任务由用户指定，本页不假装已有产品。真实 IM-066 绑定夹具在独占测试库/对象根运行，绑定注册与root resolver由相关 Owner接收，不新增私表/万能SQL。

发布单元为 Core DLL、Runtime DLL、可选 Wpf DLL；预览以 Wpf 内私有适配器接入公共视口，不仅为一种图像格式另造DLL。Core公开 DTO 只用BCL，不暴露 WPF、DevExpress、IM-066、native对象或平台私表；Runtime装配公开Store引用只属于受信任宿主构造，不进入请求/事实DTO，产品操作消费者只持有最窄接口。包元数据记录本地API版本、依赖已批准版本/hash、mapping/codec/Schema版本、目标平台、资源字典和回退范围；不捏造依赖授权门。

`G3-PreviewUI` 可调用类为 `EvidenceViewerControl`，构造参数为 `IInspectionEvidenceReader reader, PreviewProfile previewProfile, string initialCultureName`；主题沿宿主资源继承，不通过全局服务定位器。对外成员固定为 `ValueTask<ViewerOpenResult> OpenAsync(EvidenceReadRequest, CancellationToken)`、`void CancelRead()`、`ValidationResult SetCulture(string)`、`ValueTask<CloseReport> CloseAsync(CloseOptions, CancellationToken)`，实现 IAsyncDisposable；没有Commit/Retention写入口。ViewerOpenResult字段为 `Status:EvidenceReadStatus/RequestGeneration:long/Integrity:IntegrityReport/Issues:ImmutableArray<ValidationIssue>/Resources:ResourceState`，不返回native像素句柄。Open按选择代次先验证读取、后台cv2解码、最后Dispatcher交付；换代/撤权旧像素不复活。DisposeAsync只关闭自身读取/视觉lease，不Dispose注入Reader或宿主池。

预览Profile为 immutable `PreviewProfile(VersionReference Version, long MaxDecodedPixels, long MaxDecodedBytes, int MaxWidth, int MaxHeight, TimeSpan DecodeDeadline)`，正有限且受页面预算；无默认。私有解码仅接收VerifyBeforeDelivery已核图像和受信任采集/生成Owner像素描述；本版显示支持登记的byte、1或3通道、完整矩形域图像，checked Width×Height为像素数，×Channels为逻辑像素字节数；其它有效图像仍可原字节保存/回放，但本预览返回IEV-CAP-006，不做归一化/补色。先核编码/声明/预算，cv2读取后以get_image_size/count_channels/get_image_type核实际。来源声明不是任意编码的解压硬保证；未登记/不可信压缩输入Blocked，不开通通用文件查看。实际native分配峰值（可能高于逻辑像素字节）、尺寸不符/超时在视觉切片验证，不能谎称分配前已证明压缩格式安全。显示不写永久预览；上游DerivedPreview按独立身份读，不替代源图。像素仅UI内部公共控件持有，core/runtime不新增BitmapSource/native句柄。token不能强杀operator，期限到达停止交付DrainUnknown，operator退出后释放。

**私有预览交付闭包：**以下为Wpf包内部实现，不新增Runtime/IM066临时盘接口，不把路径/native对象交给ViewModel或Core。一个控件仅一个解码worker；新选择先取消旧代次，旧worker真实退出/归还后才开始新解码，不以连点无限堆Task。原worker、请求、读取lease、临时文件及native对象在第一次异步调用前由控件有界强根登记；原任务单次观察，业务期限沿请求剩余Total与DecodeDeadline取小，清理用请求独立Drain，不刷新读取期限。

1. Open只接受`VerifyBeforeDelivery`/无Range；逐块复制到本实例私有临时文件，同时重算保存字节SHA-256/长度，到独立EOF后与原Metadata/Integrity精确相等。每chunk使用后Dispose，写入总量≤声明LengthBytes及原MaxBytes；文件只用于解码此次快照，不Stage/发布、不作为持久证据。目录固定在本运行身份`LocalApplicationData/Asun/InspectionEvidence/Preview/v1`下新建随机process/instance/generation子目录；路径不由请求或文件名提供，不跟随reparse point，不复用/覆盖已有项。CreateNew文件和目录仅运行身份及SYSTEM可读写，受控短后缀按已登记Encoding映射，不猜扩展名。每控件最多一文件且字节≤原MaxBytes；空间不足/权限设置失败先拒绝，不转公共temp。该本地目录是可选UI部署条件，既有Runtime有限内存核验路线不改变。
2. 文件写完成后关闭writer，保持禁止其它写入/删除的只读保护句柄到`cv2.read_image`及所有像素复制真实结束；传完整绝对文件名，避免HALCON相对目录搜索。解码前再次CheckDeliveryAsync。调用后`cv2.count_obj`必须为1，再`get_image_size/count_channels/get_image_type`与受信任ImageInfo精确匹配；以`get_domain`→`area_center`→`smallest_rectangle1`确认面积=checked Width×Height且边界=(0,0,Height-1,Width-1)。多页、alpha/TransparencyMask产生的非满域、尺寸/通道/类型不符均停止交付，不full_domain/归一化或选择第一页。所有算子经ImageLibDotNet.cv2，实际公共C#重载/tuple/释放按消费编译确认，不用HALCON原生类接口。
3. `byte/1`用`get_image_pointer1`取得只读第一通道，行主序按Width逐行复制为Gray8；`byte/3`按`access_channel`的1、2、3顺序分别取pointer，逐行复制并交错为Rgb24（原登记通道确认为R/G/B，未声明该顺序拒预览）。指针只在相应原图及通道对象存活期间使用，禁止写指针/传UI/捕获迟到回调；通道宽高/type均复核。stride=checked Width×Channels，buffer=checked stride×Height，须≤Int32.MaxValue及原MaxBufferedBytes/MaxDecodedBytes。整体预约还包括原已核验内存快照、临时复制行、native原图及WPF副本，不只计一个像素buffer；不足时Blocked，native实际峰值仍需实测。复制完先构造独立`BitmapSource`（Gray8/Rgb24，96dpi，原像素大小）并Freeze，后台对象释放真实结束后才允许Dispatcher使用，无resize/颜色推断。
4. 交付前再次CheckDeliveryAsync并核控件未关闭、相同RequestGeneration；订阅原lease.Invalidated直到图像清除，不以EOF表示永久显示权。失效/换代/Close在Dispatcher清该代次像素和详情；迟到只清自己资源。原图/通道/tuple退出→保护句柄关闭→删除本实例精确临时文件/空代次目录→归还额度，失败保留原Owner及CleanupIssues，不假Closed或并发删operator仍在读的文件。进程重启不递归清未知/旧目录，残留仅由部署维护Owner按无活进程与保留规则处理；预览错误不改变原证据/事实。原读取lease在显示守卫结束后Dispose；native没有实际退出时强持并报DrainUnknown。

上述算法依据HALCON26.05本地 [get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html)、[access_channel](../../../halcon算子手册/operators/access_channel.html)、[count_obj](../../../halcon算子手册/operators/count_obj.html)、[get_domain](../../../halcon算子手册/operators/get_domain.html)、[area_center](../../../halcon算子手册/operators/area_center.html)、[smallest_rectangle1](../../../halcon算子手册/operators/smallest_rectangle1.html)：pointer为行主序且生命期受原image限制；通道从1计；read_image可能返回多页tuple或mask域。新增UI验收断言为已核字节与临时文件一致、Gray8/Rgb24像素逐点一致、非满域/多页拒绝、复制中撤权/连点/关闭零迟到交付、迟到native/文件删除失败不假排空；只定义验收，本轮未执行。

UI资源示例（稳定键 `evidence.commit_unknown/evidence.corrupt/evidence.no_access`）：zh-CN“提交结果未知，查询原回执。”/“证据损坏，读取已停止。”/“无读取权限。”；zh-TW“提交結果未知，查詢原回執。”/“證據損壞，讀取已停止。”/“無讀取權限。”；en-US“Commit result unknown. Check the original receipt.”/“Evidence is damaged. Reading stopped.”/“Read access denied.”。身份/hash/错误键不翻译，动态切换仅投影，不能刷新预算或权限；语言缺资源按宿主语言服务契约回退并诊断，不显示内部resource key。

## 16. 研究依据与当前未决

本指导复用并约束以下既有资料，不复制其 Schema 或部署决定：

- `PKG-040_ResultEvidence.md`：证据提交、完整性、幂等、回执、保持和双消费者边界。
- `PKG-041_Storage.md`：受控事务、不可变对象、租约、GC、迁移和恢复语义。
- `PKG-042_Query.md`：仅用于确认通用查询职责归属 `IM-045`；不作为本模块实现范围。
- `SM-020_result-evidence.md`、`DEV-PLT-012_Evidence Graph与Result Commit开发指导.md`、`FS-004_Evidence_commit.md`：唯一 Owner、`IEvidenceCommitService` 语义、状态和验收基线。
- `UI-PCS-013_Evidence_Viewer.md`：可选只读页面、八态、命令和资源释放边界。
- `docs/references/project-snapshots/DZ-XVision/20261004/`（快照日期 `2026-10-04`，来源树 SHA-256：`a3649338762b234537d185d18496fcd438ba91eafd06b8d817ebee4c5a5ceae8`）：只读提取产品级原始点位图、普通光/UV 通道、派生行图/总览图、结果来源和现场通讯日志的追溯经验；不作为平台 API、数据库字段、旧目录结构、MES 事务或业务成功语义的迁移基线。
- `../../references/project-snapshots/AsunControl/20261004/original/ClassLibrary\C_SQLite.cs`：只读借鉴参数化、事务/备份和资源释放；其万能 SQL/表名/路径接口不采纳为平台公共 API。
- HALCON 26.05 本地 operator 手册：固定 §11A.2 的字节主路线和受控预览边界。`ImageLibDotNet.cv2` 使用项目已确定的全部 operator set；未检查 AsunImage 内部，未把手册原生类签名认定为消费接口。

### H:\docs 全量清单补充审查（2026-10-06）

本轮按 `docs/references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json` 定位并核对以下两份未完成全量审查来源；原件只读，SHA-256 与清单一致：

- `H:\docs\40-development\50-ai-review\DefectViewer开发指导.md`（`516ced0ea77acc41b038e789c06e7acb91583ef00bd017a24a16b6edccae1ecd`；来源位置：增量 `REV01-ANNOTATION-FACTS-03/r2`、§4、§5.5、§6/6.1）：其精确 descriptor 与迟到结果隔离已由本指导部分覆盖；增量采纳不同 hash 域不互证、可选详情错误与合法图像隔离、共同撤权清除全部敏感投影，以及上游多来源关系的闭包约束。排除 Viewer 页面布局、量测呈现 DTO、标注/复判 UI、WPF 状态、客户/竞品流程、REV 会话与产品代码 Owner；不把来源中的 `ViewerProjection`、`ItemDetails` 或应用端口迁入本模块 API。
- `H:\docs\40-development\60-data\数据服务与证据追溯开发指导.md`（`ce03205a54dad3821159fedf84d31e70ab6235446725a890cfa5f93994c7a8c6`；来源位置：§4/5.1、§11.2/11.4、generated `APP-IFC-DATA01-COMMIT`、末尾 `2026-10-01 Finalize原响应恢复修复`）：原幂等、耐久、精确读取和 GC 原则已有覆盖；增量采纳跨域摘要分别核验、幂等解析先于暂存/字节分配、逐块及返回前当前授权围栏、嵌套目标独立可见性，以及按原操作种类/响应版本恢复并核 Receipt/Manifest 关系。排除 `Aoi.DataService`/SQLite/CAS/容量/Outbox/Retention 具体实现、查询/分页/导出、远程协议、AOI 业务字段、Data DTO、服务器 locator 和其实现/测试/生产结论；这些仍由 IM-066、IM-045 或对应 Owner 管理。

上述采纳内容已抽象进本指导第 3 节和证据关系/读取约束，不引入 H:\docs 的 Schema、接口、路径、阈值或产品验收状态。H:\docs 中涉及 HALCON 24.11 的内容未作为视觉方法依据；本模块仍遵循 HALCON 26.05 与 `ImageLibDotNet` 公共边界。

### AOI.Main 原图、部分结果和原子导出补充

只读复核 [原图预览与保存指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-original-preview-and-save-design.md)、[连续采集序列指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-capture-sequence-browsing-design.md) 以及线路/焊盘/孔位闭环指导后，证据模块必须：

- 分离原始帧、缩略图、派生图、mask、算法结果和显示截图；每一项带父来源、尺寸/格式、坐标/标定 revision、参数/模型 hash 和生成回执。
- 批量或跨帧结果保留 `Completed`、`Partial`、`Incomplete`、`NotObservable`、`Failed` 的逐项原因；缺帧、缺标定和未启用能力不能被报告层改写成 `Missing` 或 PASS。
- 采纳文件/数据库写入的临时对象、完整性、耐久和原子可见原则；本模块提交未知按原 CommitIdentity/请求摘要查询，OperationId 只诊断。来源中的导出流程属于 IM-045，不迁入本模块。
- 保存上游在开始操作时冻结的原图版本；新到帧不能改变在途保存的字节。原图导出的不可变快照原则交给 IM-045；本模块读取/编码资源等待真实排空。

这些条款扩充通用证据和数据主权边界，不复制 AOI 的客户文件名、板件字段、报告列或 MES 事务。
- HALCON 26.05 页面：[read_image](../../../halcon算子手册/operators/read_image.html)、[write_image](../../../halcon算子手册/operators/write_image.html)、[serialize_image](../../../halcon算子手册/operators/serialize_image.html)、[deserialize_image](../../../halcon算子手册/operators/deserialize_image.html)。这些页面只用于确认算子输入输出和格式限制，不授权调用方传任意路径或把 native handle 持久化。

### 16.1 固定外部源码与官方行为依据

复用暂停前已经实际读取的 [restic v0.18.1](https://github.com/restic/restic/tree/7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423)，固定commit `7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423`；[LICENSE](https://github.com/restic/restic/blob/7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423/LICENSE) 为BSD-2-Clause；[go.mod](https://github.com/restic/restic/blob/7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423/go.mod) 目标Go1.23.0，依赖chunker0.4.0、klauspost/compress1.18.0、x/crypto0.41.0及云后端等；不引入这些依赖，不复制产品项目。已读源码/测试而非根据README推断：

| 固定来源位置 | 直接观察/可迁移结论 | 限制与本模块采用 |
|---|---|---|
| [checker.go](https://github.com/restic/restic/blob/7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423/internal/checker/checker.go) 的checkTree、Structure、ReadData/ReadPacks | 分别核结构引用与数据完整性，blob handle包含类型；引用跟踪需要协调锁 | 结构可读不证明实际字节正确；该checker明确省略部分size相加检查，不能照抄到证据。采用分层核验和类型/身份隔离，保留本模块严格长度/EOF/完整闭包 |
| [checker_test.go](https://github.com/restic/restic/blob/7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423/internal/checker/checker_test.go) 的TestMissingPack、TestModifiedIndex、TestCheckerModifiedData、TestCheckerBlobTypeConfusion | 测试覆盖缺包、摘要错位、首次损坏/部分损坏、同hash不同类型与并发树读取 | 重试后无错误的上游子例不是平台默认恢复资格。采用故障注入思想：原版本/摘要重新完整核验并保留初始诊断，禁止以“第二次能打开”抹掉损坏 |
| [repository/lock.go](https://github.com/restic/restic/blob/7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423/internal/repository/lock.go) 与 [lock_test.go](https://github.com/restic/restic/blob/7d0aa7f2e30546fba7c8f1c0bae4d6704e3d8423/internal/repository/lock_test.go) 的TestLockCancel/TestLockFailedRefresh/TestLockWaitCancel | 解锁/父取消/刷新失败使上下文取消；等待锁有截止 | 取消上下文仍不证明底层I/O真实退出，restic仓库锁不等于生产根协调。采用失效停止交付/有限等待测试；生产epoch/CAS/保持根协议仍按IM-066与本指导执行 |

本轮补查 .NET10 官方 [Stream.ReadAsync](https://learn.microsoft.com/en-us/dotnet/api/system.io.stream.readasync?view=net-10.0)、[协作取消](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)、[IncrementalHash](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.incrementalhash?view=net-10.0)（2026-10-09）：读返回值可小于缓冲长度，正长读取返回0才表示EOF；取消由监听者协作；AppendData累积实际字节、GetHashAndReset返回摘要并复位。落实在 §§6/7.1/7.3.1，不把一次短块或token取消当数据截断/真实排空。

DevExpress25.2官方网页尝试 [DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[TreeListControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListControl?v=25.2)、[SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2) 返回403；当前没有可调用dxdocs工具，未宣称已用。已核本机官方 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/` 的 Docking/Grid/PropertyGrid/Core `v25.2.xml`，类型DockLayoutManager/LayoutGroup/LayoutPanel/DocumentGroup、TreeListControl、PropertyGridControl/SelectedObject/ReadOnly、SuperTip均存在；这是§10.1控件选择依据，不是WPF实测或依赖授权审查。25.2.3程序集直接使用，具体XAML行为由可选UI切片验证。

### 16.2 门的精确分类

| 未接收/未验证事项 | 门类型与消费者 | 阻断范围 |
|---|---|---|
| G1正式实现任务与代码基线确认（G1文档规格已于2026-10-11接收） | 后续实现任务/代码基线绑定；不需要客户阈值/设备 | 本轮不创建G1工程，已接收规格不重审；不是“内部API未定义”的外部门 |
| G2-T1/G3-T1实现准入、代码任务/基线及后续编译/运行（技术桥指导已获限定内容接收） | 本模块内部工程门；§8.4/B.5拥有技术封套/身份/预算/原Task/完整性，§9.3/12.3/13.2拥有双Host/测试/测点；限定内容接收不等于六项实现准入，不是客户外部门 | 本次不开发两技术片、不创建工程；不阻断已接收G1；ModuleCoreImplementationReady/ImplementationSpecificationReady均未授予，正式Owner/授权/真实存储及耐久门保持 |
| C-04事实/request与C-07保持政策的业务validator、原事实子mutation/用途Profile与同事务采纳 | 内部跨模块产品输入/集成门；通用Manifest/Receipt/Root字段/编码、模块注册与root恢复已由B.6冻结，不能全部交给C-04/C-07。业务Payload canonical/合法值、真实FactRevision写回、法律保持决定及子mutation行数仍归原Owner，不是客户外部门 | 阻断对应G2产品事实写/实际业务保持及G3用途接入，不能阻断已定义的模块封套/根只读/技术测试准备；产品无法同事务参与则拒该生产绑定 |
| B.6模块持久封套/注册包/root resolver的代码准入及实际实现 | IM-015拥有；本原会话已补完整设计，§17.4记录文档审核结论；注册SQL/迁移/codecs/根read mapper需照本指导实现和验收，属于代码工作，不是假称客户提供模块表/算法 | 仅产品/后端集成与新增代码切片的正式开工门；本轮未创建工程、不自动提升Ready，既有G1/T1接收保持 |
| 当前授权Stamp和Invalidated传播/登记守卫在实际服务的生效点 | C-06授权交接/集成验收门；本地守卫方法/通知已在正文冻结 | 真实授权登记/字节显示的相应切片；不阻断Core或假端口故障规格 |
| IM-066当前RootCoordinator/事务/FileObjects公开规格的真实部署运行、物理guard/耐久/崩溃与storage参数 | 软件接口/装配规格复用IM066§6.3/6.6/6.7；IM066拥有协调与存储实现，部署Owner提供endpoint/root/凭据/物理证据，非本模块再选数据库/再设计根算法 | G2/G3真实持久化/GC/备份资格；未知/不完整根停GC，本模块通用设计不因未实测而降为再设计 |
| 客户保留政策、法律保持、实际负载/节拍、RPO/RTO、现场Golden | 真实客户/现场外部门，值由客户/数据主权/部署Owner提供，不造默认 | 保留释放、性能目标达标和现场资格；不阻断测量方法/Core/无硬件软件契约 |
| cv2预览的实际重载/类型消费、native资源峰值/取消，真实WPF布局/键盘/UIA/三语和高保真接收 | 可选工程/视觉/UI验收门；本地控件/流程/预算/接口已经冻结 | 仅G3-PreviewUI；不把AsunImage/DevExpress许可证或算子存在性列为门 |

设备命令/SDK、通用Query/Export、业务放行均不属于本模块范围，不能列为本模块“待实现外部门”。准入按切片记录：G1-Core文档规格已接收，G2/G3及整模块产品准入仍为PreparationIncomplete/DesignReview；未执行的真实构建/测试/性能/UI不能写通过。

## 17. 开发准入与自审清单

- [ ] 本模块只在 `docs/independent-modules/inspection-evidence/` 维护；无制程判定、设备动作、产品页面或私表依赖。
- [ ] C-01～C-08、FS-004、State/Owner/Authority 有唯一绑定；没有新增平行 Schema、状态机或事实库。
- [ ] 输入/输出字段的单位、范围、默认、版本、hash 覆盖域和 Owner 已由正式合同冻结。
- [ ] 同键同载荷、同键异载荷、Unknown、取消、超时、重启、通知重复和 GC 竞争均有可判定语义。
- [ ] 资源拥有者、线程模型、队列/字节预算、排空和坏连接处理已写入实现卡。
- [ ] 至少一个生产提交消费者和一个回放/复判只读消费者使用同一读取、保持和权限协议。
- [ ] 回执/Manifest 定向读取、对象 lease、摘要核验、撤权和 GC 闭包均有测试断言；通用查询/导出由 `IM-045` 验收。
- [ ] 原始点位图、普通光/UV 通道、派生行图/总览图和结果证据的角色、父子闭包、缺失/损坏语义与精确身份读取已覆盖；现场诊断记录按事件/批次 hash、脱敏、时钟来源和不可变封存验证，不能影响生产事实。
- [ ] P50/P95/P99、峰值资源、取消排空、恢复 RPO/RTO 仅在批准 Profile 和实测后报告。
- [ ] 可选 UI 只调用核心端口，八态、三语、UIA、DPI 和关闭释放有真实 WPF 验收计划。
- [ ] HALCON/AsunImage 仅按公共能力用于可选视觉解码；无猜测 API、无内部修改、无 native 持久化。
- [ ] 发布包、适配器、迁移和回退路径可单独版本化，旧事实可读且不重发设备副作用。

当前仅 Gate-1 Pure Core 文档规格标记为 `ModuleCoreImplementationReady`；Gate-2 Evidence Submission、Gate-3 Directed Read/Retention 与整模块产品准入仍为 `PreparationIncomplete/DesignReview`，未获 Core 或产品写入准入。本页没有实现、测试通过或生产验收结论。

### 17.1 DEV-GOV-010 §3.1 六项逐切片定位

下表 G1-Core 六项文档规格已于 2026-10-11 由主控逐项接收，状态为 `ModuleCoreImplementationReady`；该接收不代表代码或资格通过。G2/G3各列仅为规格定位，不代表正式交接或资格通过；有副作用的切片不能援引六项Core门直接获得产品写入授权，须额外满足正式ImplementationSpecificationReady和对应合同/Owner交接。G1作为纯Core独立接收，不与后续外部门捆绑。

| 六项 | G1-Core | G2-Submission | G3-ReadRetention | G3-PreviewUI |
|---|---|---|---|---|
| 1 边界/第二消费者 | §§1–2/15.1；生产描述计划与独立回放校验，无事实/持久写 | §§1–2/7.1–7.2/15；仅C-04冻结提交 | §§3.3/7.3–7.3.2/15；精确只读、C-07保持决定，不物理GC | §§10/10.1/15.1；只读模块控件，无提交/设备/全局检索 |
| 2 完整API/参数/事件/错误/所有权 | 附录B.1/B.2、§5、§8.3；ScopedId/图/快照/Profile/错误已定义，无事件/外部资源 | 附录B.3/B.4、§8.2/§§4–6；本地封套/绑定/授权/通知/关闭已定，模块codec见B.6；业务validator待原Owner接收 | 附录B.3/B.4、§§6–8；三模式、chunk背压、显示守卫、保持决定和根闭包已定 | §§10.1/15.1；Viewer接口/PreviewProfile/三语/代次/关闭已定；实际cv2与XAML消费在本切片编译 |
| 3 无UI最小Host | §8.2公开sealed实现/无参构造；§9.1两个完整BCL Host逐字段构造目录/Profile/描述/快照/Elapsed，无Shell/Store/native | §8.2显式构造、§6.2构造前有限根/原Task/迟到/确认移交，§9.2参数完整消费函数；业务validator/事实子mutation未接收仅阻对应生产绑定 | 同Runtime的Reader/Retention窄接口；§6.2 lease接纳/失效与ObserveResources；§9.2独立空EOF读取 | Wpf包必有UI，不把CoreHost冒充该项；读取/预览算法前置路径可后台调用，真实UI另验 |
| 4 正常/边界/故障/取消/并发/关闭/回退断言 | §§11/12.1 C-01～C-10/8.3；BCL Exe，无Core Dispose或假排空 | §§7.2/11A/12.2；竞争先解析、崩溃窗口、Decode错类型、Unknown、Dispose | §§7.3.1–7.3.2/12.2 R-EOF-01/02；短块/截短/range/撤权/关闭/chunk/GC/保持未知 | §§10.1/12/15.1；真实WPF八态/双语言实例/迟到/撤权/关闭；视觉峰值与operator排空另验 |
| 5 BenchmarkProfile/资源/目标来源 | §13.1纯计划规模/托管分配/并发；资源外部上限0、返回即Released；方法冻结、目标待采纳 | §13/13.1字节/队列/Stage/事务/恢复直到Released；真实目标独立 | §13.1父闭包/暂存/chunk慢消费/取消/资源；不删超时/未知样本 | §13.1选择→图/关闭释放，1920×1080；PreviewProfile limits，目标来自页面Profile |
| 6 工程/允许范围/测试/最小顺序 | 开头绑定与§§9.1/12.1/15.1；唯一Core/Core.Tests；完整Host与有限build/run计划 | §15.1Runtime/Runtime.Tests、§8.2映射、§6.2根、§9.2；与G3同包串行不改其它模块 | 同Runtime/Runtime.Tests，按G3批准后实现，§§6.2/7.3/9.2/12.2 | §15.1Wpf/Wpf.Tests本机依赖、真实STAHost；不改产品/共享/AsunImage内部 |

六项本地规格已定位并由主控接收，**G1-Core当前无待定义内部API/阈值/存储选型项**，文档规格为 `ModuleCoreImplementationReady`；正式实现任务/代码基线绑定另行安排。G2/G3通用封套/技术注册/root软件设计在B.6闭合，正式业务validator/原事实子mutation、用途Profile及当前授权接入仍按精确Owner交接；真实耐久/性能/客户保持/WPF分别是对应资格门。§16.2逐项列了阻断范围，不要求52模块一起开工。

### 17.2 两轮怀疑式内容自审（2026-10-09）

第一轮从外部集成人反推：从无参Core到冻结描述，再由受信任Host注入Runtime；逐项核新提交无预先对象revision、NotFound无原摘要、日志不能伪造曝光、缺required证据不能由客户端降为optional、同blob不合并身份、正式Receipt不可宽松解为Session、Reader不得泄漏原Stream、UI不得第二写入。结果已回写附录B、§§7–10/12/15；纯描述/含流请求已分离，正文与附录保留一套入口。原图/派生/诊断/保持完整职责均保留，没有以G1首片替代整模块规格。

第二轮从并发/崩溃/生命期反推：两实例同键竞争、源分配前丢响应、Seal/Finalize窗口、父闭包错序/错权、读取中撤权/EOF后显示、短块/截断、未释放chunk、Dispose deadline、Unknown根无Receipt、保持解除未知、GC扫描后新引用、旧callback及回退。结果已回写§§6/7.3/8.2/12.2/13.1与附录B.4：业务Unknown与资源Released独立，关闭只能停止本实例，source独占/晚释放，lease守卫覆盖显示交付，未知保持/root不漏枚举，不承诺无法公开证明的恢复/撤权即时性。

自审是内容走查，不能替代真实编译/测试。未执行产品代码、dotnet build/run、HALCON、WPF、介质崩溃、性能或现场验收；当时G1文档规格待主控接收，当前接收结果见§17.1，§16.2列明的G2/G3跨文件交接仍未完成。本轮不修改共享文件、不发消息到其它会话。

本次三项退修的第一轮定向自审按调用方执行§9：最后数据块先消费/Dispose，下一空EOF才退出；按RequiredItems对独立分配/重排Versions逐字段匹配；按完整ContractKey排除其它操作同版本命中。第二轮按反例核R-EOF-01/02与C-09/10：尾部损坏不发EOF、未释放末块不推进I/O、版本缺/多/重复或内容改变拒绝、未知Kind/同Kind错Version均无可执行计划。契约表、处理步骤、示例及断言已同步；这是内容自审，未运行Core/Runtime测试，当时G1待主控接收，当前G1文档规格已接收，G2/G3真实门不变。

2026-10-11本次窄修的视角一为实现者正常→异常→恢复：逐字段核§9.1目录/Profile/Source/关系/事实引用/请求/快照/Elapsed全部可从公开构造生成，H1源错绑/预算/取消无半计划，H2保持Unknown、冲突检查用内部一致的原Committed快照；计划不证明存储。视角二为外部消费者从空Host装配：公开sealed Core无参new、两独立Host无Runtime/C-04装配欠账；后续Runtime同步构造零I/O，先有限根预约、原Task一次AsTask、迟到lease接纳/清理竞争、独立cleanup和目标确认移交已在§6.2定义，不依赖页面finally及时退出。保留0.3.1的独立EOF、Versions无序逐字段与完整ContractKey；未执行C#编译/运行或G2/G3真实集成。该窄修自审时仍为PreparationIncomplete；当前主控已接收G1-Core文档规格为ModuleCoreImplementationReady，G2/G3与整模块产品准入仍为PreparationIncomplete/DesignReview。

### 17.3 本轮技术桥六项定位与两轮自审（2026-10-11）

| DEV-GOV-010 §3.1 | G2-T1技术提交桥（无生产资格） | G3-T1技术读取/保持桥（无生产资格） |
|---|---|---|
| 1 边界/第二消费者 | §8.4、§9.3 P1；无UI描述到受控命令/技术回执，P2独立Replay消费者 | §8.4.3–4、§9.3 P2；精确读取/短lease/技术保持决定协议，P1独立提交消费者 |
| 2 完整公开契约/所有权 | §8.2 Runtime构造、§8.4.1–3、B.4/B.5；Binding公开构造/封闭输入/命令/原响应、IM066原mutation/hash/预算、source转移后向Store借用 | 同一Runtime/B.5 Factory/options；三模式/EOF/当前授权/TTL与持久根区分、原Task/lease释放、保持事务/查询分离 |
| 3 空Host | §9.3完整P1/ProtocolHost/Program与B.5 Factory全部装配字段；独立Root/Store/Authority/codec | §9.3完整P2独立Build/Seed/Read/Hold/Query/Release/恢复；无产品Shell/私有DB/native；不是只有参数函数 |
| 4 正常/边界/取消/并发/故障/关闭/回退 | §12.3 T-01～05/10～12；同键竞争、原响应未知/原查询、迟到Stage/源、主错与cleanup并存、版本精准恢复 | §12.3 T-06～12；三模式/短读/独立EOF/尾损/撤权/迟到lease、保持CAS/根不完整阻GC、Close/移交 |
| 5 Benchmark/资源/目标 | §13.2全部阶段/实际byte/hash/原Task/root计账与Profile上限；失败/排空未知不判通过 | §13.2闭包/首块/完整hash/Verify/交付/释放及慢consumer/TTL；合成限额与真实性能目标分开 |
| 6 唯一工程/范围/最小顺序 | §15.1 Runtime/Runtime.Tests；§9.3 P1；后续先本技术桥再G3-T1，不改Core/共享/其它模块 | 同一包/唯一Owner串行；§9.3 P2、§12.3完整suite命令；Wpf/产品/真实根与真实存储均后续门 |

两切片确定技术桥指导已于2026-10-11获主控**限定内容接收**：§8.4、§9.3完整两Fake Host及收尾、B.5技术codec/身份/目录/恢复、§12.3/13.2及本节。**状态仍为PreparationIncomplete/DesignReview，未标记ModuleCoreImplementationReady或ImplementationSpecificationReady**；不是代码实现、运行通过、耐久或业务事实资格结论。G1已接收六项保持。正式C-04/C-07业务validator/原事实子mutation与保持政策采纳、C-06授权接线及实际生效是内部跨模块工程门；真实IM066运行、A1/A2、介质耐久与崩溃是技术部署资格门；客户保持/负载/节拍/物理验收仅影响其对应外部资格。任何内部命令/Host/算法仍有欠账时在此技术片退修，不转嫁为客户外门。

第一轮从实现者正常→异常→恢复走读：核BindingCommand Read无Identity/Write完整Hasher、BindingResponse绑定ExpectedCommand、原技术身份/Key稳定且无self-hash；修正错误码到§5既有值、补RemainingIoBudget避免编码刷新期限、Reserve分配Key后才形成Stage完整身份/Verify形成后保存。逐步从P1/P2空Host核公开构造/字段/source/独立root、权限/hash终检/EOF与短TTL，保持正式业务codec未被夹具采纳。

第二轮从外部集成与故障反推：核构造失败与Attach失败的Owner区别、原Task一次AsTask/迟到资源接管、独立cleanup不得覆盖主错、Unknown资源已释放仍保持持久根；核最后数据chunk释放后独立EOF、range不升级全验、ReservedKey无法全量映射时阻GC、旧Schema/操作kind不能宽松解码。核双Host无未传入Store/权限/codec/配置，测试完整suite与基本Host通过分开、源/响应副本实际内存纳入预约。以上是内容自审，未执行C# build/run、真实IM066、native/HALCON、WPF、性能、Golden或现场验收。

### 17.4 全部批准范围的设计准备结论（2026-10-11，0.3.4-prep）

本次只完善唯一指导，不开发产品代码、不新增工程/脚本/报告。已按实现者“构造→正常→失败→恢复”和集成人“注册→两消费者→并发/重启→关闭”两轮定向审核全部范围；补B.6模块封套/注册/root，以及§15.1已核字节到HALCON再到WPF的私有预览交付。第二轮修正Root多对象出生ID冲突、分页Sequence进入持久摘要、TotalBytes口径、Manifest每Item缺项与外部父Receipt覆盖，以及只读快照不能凭token字段证明实时物理资格。这些都是模块内部软件决定，已在正文冻结，不转嫁客户。

| 批准的职责/切片 | 本模块可决定的软件设计是否仍欠账 | 剩余项与唯一Owner；现有接收/准入保持 |
|---|---|---|
| G1-Core纯校验/图/计划/操作投影 | 无；B.1/B.2、§8.3/9.1/12.1/13.1完整，未重新设计 | 本模块：后续代码基线/实现任务与Core编译运行；六项接收及ModuleCoreImplementationReady保持，不代表实现 |
| G2-T1/G3-T1技术桥与双Fake Host | 无待选端口/身份/hash/有界Owner/恢复算法；§8.4/9.3、B.4/B.5、§12.3/13.2保持；§9.3仅纠正两处ScopeId属性名 | 本模块：正式实现准入/代码任务及完整suite；限定内容接收保持，未授ModuleCoreImplementationReady/ImplementationSpecificationReady；Fake不是耐久/生产证明 |
| G2提交、模块Manifest/Receipt封套与注册 | 无模块字段/编码/摘要/技术表/事务顺序欠账；B.6.1–3、§7.1/7.2规定唯一边界 | C-04：冻结业务canonical/validator、原事实子mutation/FactRevision与同事务采纳；本模块：SQL/迁移/codec实际实现验收；IM066：原事务/FileObjects实现；部署Owner：物理耐久。仅对应绑定受阻，整体G2仍PreparationIncomplete/DesignReview |
| G3定向读取、保持登记、root快照 | 无读取spool/EOF/授权/有界快照/根恢复算法欠账；§7.3、B.6.4规定零Query写和未解析根阻GC | C-07：用途/保持决定/法律政策；C-06：真实授权与失效传播；IM066：同ReferenceEpoch/协调guard与存储实现；本模块：root mapping/异常排空实现验收；客户/部署Owner：保持值、备份/GC/RPO/RTO资格。G3仍PreparationIncomplete/DesignReview |
| G3-PreviewUI可选只读控件/预览 | 无本模块任务流/布局/三语/私有文件/像素交付/代次与释放的待选方案；§10.1/15.1已冻结 | 本模块：cv2公共调用消费编译、真实native/WPF/UIA/键盘/三语/峰值与排空；宿主UI Owner：主题/高保真视觉接收；部署Owner：私有目录权限/介质；客户/用途Owner：代表编码/负载与性能目标。未实测不等于需再设计，也不提升准入 |

结论限于当前批准范围与现有输入：**本模块可自行决定的软件设计欠账已闭合；仍有原Owner的业务/权限/协调输入、正式开工接收、代码实现和运行/物理资格门**。不能把本结论写成全部合同获批或整模块Ready。Owner输入若改变既定边界，先修受影响唯一指导；仅实际C#重载/SQL/XAML表达与运行失败按本规格实现/修复，不重新选择算法、产品判定或默改验收。

本轮结构/围栏/表列宽/本文件本地链接、ScopeId属性与状态锚点检查通过；公开字段/注册类型闭包与摘要依赖完成内容走查。§9.1/12.3/B.5与本轮修改前摘要一致，§9.3还原两处ScopeId机械修正后亦一致，未扩大既有接收。两条Golden内存编码/显式解码/SHA-256重算一致，13个损坏反例拒绝，Key改变导致hash改变；结果见B.6.5。未执行C# build/run、产品/正式测试工程、真实IM066/SQL事务、HALCON/native读图、WPF、高保真视觉验收、性能、介质崩溃、HIL或现场验收。准入和实测仍按上述逐切片门记录，不等总控代做内容复核。

2026-10-11定向接线核对（0.3.5-prep）：只对照IM066 0.3.1-prep §6.3/6.7.3新增说明，补B.6.3启动不可变注册/禁止提前Open根、事务local E读取及Owner行数计账排除隐含上游技术SQL，补B.6.4第1项显式关闭顺序。§8.4.2第3项与B.6.3恢复段既有Query/Recovery分工一致，无需改动：领域Read只用Query窄读，原技术QueryOperation走上游Recovery保留池，查询零写、不续作；受管技术CAS不授本模块领域mutation。原§17.4完整范围准备结论、公开API/编码及G1/T1接收均保持，不新增设计外门或提升Ready；此次仅局部正文自审与结构/引用检查，不重复全审/向量复算/来源研究，未执行代码或运行验收。

## HALCON 26.05 算子资料入口

本模块保存和追溯检测证据，不重新执行视觉算法；涉及预览时使用项目内 [halcon算子手册/operators](../../../halcon算子手册/operators/) 的26.05资料，经 `ImageLibDotNet.cv2` 对应算子调用，只有 C# 重载/封送确有歧义时查公共签名。

## 附录 B：模块 API 分层入口

本附录与附录 A 合称 `Module API Contract v0.2`。下列为待实现接口形状，类型由后续字段表唯一定义；字段表是本地代码契约，不是产品序列化 Schema。Gate-1 类型可独立实现，Gate-2/3 字段映射仍需相关 Owner 接收。禁止在正文另造同义接口。

```csharp
// namespace Asun.Modules.InspectionEvidence
// Gate-1：输入、Profile、目录、快照均为不可变值。
public interface IInspectionEvidenceCore
{
    ValidationResult Validate(EvidenceRequest request, CoreContext context, CancellationToken token);
    StagePlan PlanStage(EvidenceRequest request, CoreContext context, CancellationToken token);
    CommitPlan PlanCommit(CommitDescription request, OperationSnapshot snapshot, CoreContext context, CancellationToken token);
    OperationStatus EvaluateOperation(OperationSnapshot snapshot, CoreContext context, CancellationToken token);
}

// Gate-2：唯一对宿主公开的事实提交命令；Stage/Seal/Publish 是其内部步骤。
public interface IInspectionEvidenceSubmission
{
    ValueTask<CommitResult> CommitAsync(CommitRequest request, CancellationToken token);
}

// Gate-2：完整提交身份 + 原请求摘要 + 当前授权；查询不产生写入。
public interface IInspectionEvidenceOperationReader
{
    ValueTask<CommitRecoveryResult> QueryOperationAsync(CommitRecoveryRequest request, CancellationToken token);
}

// Gate-3：打开受控读取租约，不暴露可绕过守卫的 Stream。
public interface IInspectionEvidenceReader
{
    ValueTask<EvidenceReadResult> ReadAsync(EvidenceReadRequest request, CancellationToken token);
}
public interface IEvidenceReadLease : IAsyncDisposable
{
    IntegrityReport Integrity { get; }
    ResourceState ObserveResources();
    event EventHandler<EvidenceReadInvalidatedEventArgs> Invalidated;
    ValueTask<ReadGuardResult> CheckDeliveryAsync(CancellationToken token);
    ValueTask<EvidenceChunk> ReadChunkAsync(int maxBytes, CancellationToken token);
}
public interface IEvidenceContentSource
{
    ValueTask<Stream> OpenReadAsync(CancellationToken token);
}
public interface IInspectionEvidenceRuntime : IInspectionEvidenceSubmission,
    IInspectionEvidenceOperationReader, IInspectionEvidenceReader,
    IInspectionEvidenceRetention, IAsyncDisposable
{
    ValueTask<CloseReport> CloseAsync(CloseOptions options, CancellationToken token);
}
public interface IInspectionEvidenceRetention
{
    ValueTask<RetentionResult> ApplyRetentionAsync(RetentionRequest request, CancellationToken token);
    ValueTask<RetentionResult> QueryRetentionAsync(RetentionQuery request, CancellationToken token);
}
```

### B.1 值类型、空值与单位

Gate-1 所有组合值采用不可变 record + `ImmutableArray<T>`；不接收可变 List/Dictionary，也不保留传入的可变缓冲。空数组与缺字段分开：default ImmutableArray 为非法；已初始化的空数组只在本节允许处合法。不得用可空对象省略必填信息。

**公开构造闭包：**本节/B.2的值记录全部定义为`public sealed record`，具有按对应字段表从左到右顺序排列、以表中PascalCase字段名命名参数的公开主构造器，生成同名get/init属性并支持C# `with`；不加默认参数、不执行外部初始化。斜杠字段展开为各独立参数：例如CatalogSnapshot的FactContracts、ResponseContracts各自一个ImmutableArray参数，Profile的各Max及Required数组分别一个参数。`ContractKey(string Key,string Version)`、`MediaRoleRule(string MediaType,EvidenceRole Role,bool AllowEmpty,bool IsImage)`、`RelationRule(string Key,bool RequiresTransform,ImmutableArray<EvidenceRole> AllowedChild,ImmutableArray<EvidenceRole> AllowedParent)`亦为独立public sealed record。枚举按表的成员名称定义。非法值可用于构造反例，校验在Core入口统一执行，不因构造器抛异常而丢失typed Issues；顶层/内部引用null也须拒绝，无隐藏默认资源。此约定使§9.1全部new/with调用有唯一匹配构造，无需实施者另选DTO初始化方式。B.3/B.4封闭基类/资源接口不据此改为纯record。

| 类型 | 完整字段/约束 |
|---|---|
| `ScopedId` | `ScopeId:string`、`Value:string`；各 1..256 个 Unicode 标量，无首尾空白、控制字符或无效代理项；不 trim、不折大小写/Unicode、不按路径解析；Ordinal 比较。ScopeId 由宿主身份 Owner 提供 |
| `DigestValue` | `Domain:string`、`Algorithm:string`、`CanonicalVersion:string`、`Hex:string`；前三项非空稳定键且各≤256；Hex 为非空小写偶数十六进制，长度须等于目录登记算法输出；不接受缺域/未知 canonical。模块实际保存字节摘要使用 SHA-256（64 字符、域 `StoredBytes/v1`、canonical `ByteSequence/v1`）；其它域规则只由 Owner/目录提供，不复用此域 |
| `VersionReference` | `Id:ScopedId`、`Revision:long`（>0）、`Digest:DigestValue`；不允许 latest。同 Id/revision 的不同摘要是冲突 |
| `SourceBinding` | `Kind:SourceKind`、`SourceId:ScopedId`、`AcquisitionId/AttemptId/PositionId:ScopedId?`、`ChannelId:string?`、`ObservedUtc:DateTimeOffset?`、`Versions:ImmutableArray<VersionReference>`；Kind=`Acquisition/Derived/Fact/Diagnostic`。Acquisition必须具备全部采集字段/ObservedUtc且ChannelId已登记；其余种类只按真实来源提供可空采集字段，不给日志伪造曝光。SourceId为原观察/生成/事实/事件身份；已提供时间offset0，不能拿接纳时刻补源时间。字段同scope；Versions是无序精确版本集合，同ScopedId只许一项（同Id不同revision/hash也拒绝），default非法；比较规则见下文，必需引用由Profile指定 |
| `EvidenceRole` | `Acquisition`、`DerivedImage`、`DerivedPreview`、`ResultArtifact`、`Diagnostic`；源图/派生不能互换；普通光/UV 是 SourceBinding.ChannelId，不能据此猜制程 |
| `EvidenceLink` | `ChildId:ScopedId`、`LocalParentId:ScopedId?`、`ExternalParent:VersionReference?`、`Order:int`（≥0）、`RelationKey:string`（目录登记）、`Transform:VersionReference?`；两个父字段必须恰一有值。新提交父对象只填 LocalParentId，其服务对象 revision 在发布后由模块解析；外部父使用精确版本。按 ChildId/RelationKey 分组的 Order 从0连续唯一；要求变换的关系不能缺 Transform |
| `EvidenceDescriptor` | `LogicalId:ScopedId`、`Role:EvidenceRole`、`MediaType:string`（目录白名单）、`DeclaredLengthBytes:long`（≥0）、`DeclaredStoredDigest:DigestValue`、`Source:SourceBinding`、`Encoding:VersionReference`、`ImageInfo:ImageDescription?`；已登记image媒体必有ImageInfo，其它媒体无该字段；零长由角色/媒体策略决定，图像拒绝；声明不是实际完整性证明 |
| `ImageDescription` | `Width/Height/Channels:int`（>0）、`PixelTypeKey:string`（媒体/编码目录登记）、`Domain:VersionReference?`；尺寸/类型由上游采集/生成Owner提供，完整像素域可无Domain，非满域须明确region版本。不定义转换/归一化；Core仅校验类型/声明和checked像素数，视觉适配器核真实内容 |
| `EvidenceAbsence` | `LogicalId:ScopedId`、`Role:EvidenceRole`、`Source:SourceBinding`、`ReasonKey:string`（目录登记）、`IsRequired:bool`；不得同时存在 descriptor 与 absence；必需缺项阻断计划/提交，可选缺项不自动删除关系 |
| `EvidenceRequest` | `ScopeId:string`、`Descriptors:ImmutableArray<EvidenceDescriptor>`、`Links:ImmutableArray<EvidenceLink>`、`Absences:ImmutableArray<EvidenceAbsence>`、`ExternalParents:ImmutableArray<VersionReference>`；外部父项必须显式列出精确版本，Core 仅校验声明，后续门核真实存在/授权/保持 |
| `FactReference` | `Calculation:VersionReference`、`FactContractKey:string`、`FactContractVersion:string`、`FactDigest:DigestValue`；键/版本须在目录中；Core 不解析事实数值/判定，不拿哈希证明事实语义合法，C-04 强类型映射负责有限数/单位/枚举验证 |
| `CommitDescription` | `Identity:ScopedId`（CommitIdentity）、`Fact:FactReference`、`Evidence:EvidenceRequest`、`RequestDigest:DigestValue`、`ExpectedRevision:long?`（有值>0）、`Profile:VersionReference`；作用域必须一致；请求摘要为上游按批准 canonical 冻结的比较值，Core 不计算/证明其内容 |
| `DigestRule` | `Domain:string`、`Algorithm:string`、`CanonicalVersion:string`、`HexCharacters:int`（正偶数）；三键唯一；只做批准规则声明校验，实际算法支持属于后续能力门 |
| `CatalogSnapshot` | `Version:VersionReference`、`DigestRules:ImmutableArray<DigestRule>`、`References:ImmutableArray<VersionReference>`、`FactContracts/ResponseContracts:ImmutableArray<ContractKey>`、`MediaRoles:ImmutableArray<MediaRoleRule>`、`Relations:ImmutableArray<RelationRule>`、`ChannelKeys/ReasonKeys/PixelTypeKeys:ImmutableArray<string>`；无重复键。`ContractKey` = Key/Version 两非空字符串；`MediaRoleRule` = MediaType:string、Role:EvidenceRole、AllowEmpty/IsImage:bool；`RelationRule` = Key:string、RequiresTransform:bool、AllowedChild/AllowedParent:ImmutableArray<EvidenceRole>`（非空）。引用精确匹配，不仅按 Id 查首项；外部父角色在 Gate-2/3 权威解析 |
| `ValidationProfile` | `Version:VersionReference`；`MaxObjects/MaxAbsences/MaxLinks/MaxGraphDepth/MaxReferences/MaxCatalogEntries:int`、`MaxObjectBytes/MaxTotalBytes:long`、`MaxChunkBytes:int`、`RequiredRoles:ImmutableArray<EvidenceRole>`、`RequiredItems:ImmutableArray<RequiredEvidenceItem>`、`RequiredVersionIds:ImmutableArray<ScopedId>`、`AllowEmptyEvidence:bool`；上限>0，object≤total、chunk≤object；数组非 default、required 数组可显式为空。RequiredItems来自C-04批准的当前scope/attempt最小证据集合，不由请求客户端自行减项，数量≤MaxObjects；Core仅校验此策略声明，不授策略变更权。目录总条目/请求全部嵌套引用计数分别受MaxCatalogEntries/MaxReferences约束；稳定键≤256 Unicode标量，媒体键≤256 ASCII。缺Profile拒绝 |
| `RequiredEvidenceItem` | `LogicalId:ScopedId`、`Role:EvidenceRole`、`Source:SourceBinding`；同Profile无重复、作用域与请求一致；每个必须按B.1逐字段/集合内容精确匹配descriptor，禁止用record默认Equals比较Source或ImmutableArray；其它通道/FOV/同字节/optional absence不能代替 |
| `CoreContext` | `Profile:ValidationProfile`、`Catalog:CatalogSnapshot`、`Budget:TimeSpan`（>0且有限）、`Elapsed:TimeSpan`（≥0）；Core 不自行取墙钟或等待。Elapsed≥Budget 返回超时；耗时中断由 token 提供，宿主需自行驱动截止 token |
| `OperationSnapshot` | `Identity:ScopedId`、`Kind:string`、`ResponseVersion:string`、`RequestDigest:DigestValue?`、`Outcome:CommitOutcome`、`Receipt:ReceiptReference?`、`Resources:ResourceState`；Kind只允许EvidenceCommit，必须用完整`ContractKey(Key=Kind, Version=ResponseVersion)`与ResponseContracts中同Key/同Version项Ordinal比较；仅其它操作版本字符串相同不算登记。未知Kind为IEV-VAL-001；已知Kind的完整键未登记为IEV-CAP-006。NotFound无原摘要/Receipt且Resources=NotStarted；PermissionDenied无原摘要/Receipt、不披露存在性；其它状态必有原摘要。Committed必有正确各摘要域的完整Receipt；非Committed不带Receipt。快照不是权威证明 |
| `ReceiptReference` | `Id:ScopedId`、`CommitIdentity:ScopedId`、`Revision:long`（>0）、`RequestDigest/ManifestDigest/ReceiptDigest:DigestValue`；域分离且作用域一致，指向不可变版本 |

`CommitOutcome` = `NotFound/InProgress/Committed/Rejected/Unknown/PermissionDenied/Corrupt`；`ResourceState` = `NotStarted/Active/CancelledPendingDrain/Drained/ResourcesReleased/DrainUnknown`。业务结果与资源状态是两个字段，不能用 Completed 覆盖 Unknown。错误分类固定为 §5 的稳定键；业务合同可映射代码值，但不能改变含义。

**SourceBinding精确相等：**先校验两侧值合法，逐一比较Kind、SourceId、可空AcquisitionId/AttemptId/PositionId、ChannelId、ObservedUtc；ScopedId比较ScopeId/Value的Ordinal内容，字符串Ordinal且null只等null，时间比较offset0的UTC ticks。Versions先校验每侧非default且Id唯一，再按ScopedId构建有界查找：项数相同且每个Id都有对应项，逐字段比较Id.ScopeId/Value、Revision及Digest.Domain/Algorithm/CanonicalVersion/Hex，字符串全部Ordinal。不得仅比Id/hash或以ImmutableArray引用Equals、Source record默认Equals判断；独立数组相同内容及重排内容相等，缺/多项或任一字段不同不等。无序集合只针对SourceBinding.Versions，不改变父关系Order、上游事实载荷或批准codec的canonical；比较不修改传入数组，不凭排序重算请求hash。

### B.2 Pure Core 结果与唯一处理顺序

| 返回类型 | 完整字段/含义 |
|---|---|
| `ValidationIssue` | `Code:string`（§5 稳定键）、`FieldPath:string`、`LogicalId:ScopedId?`、`Recovery:RecoveryAction`；不含敏感原值/异常消息 |
| `ValidationResult` | `Issues:ImmutableArray<ValidationIssue>`；`IsValid` 仅由 Issues.IsEmpty 派生，不得另存易冲突 bool |
| `StageEntry` | `LogicalId:ScopedId`、`DeclaredLengthBytes:long`、`ParentIds:ImmutableArray<ScopedId>`；只描述，不生成对象/暂存 ID |
| `StagePlan` | `Issues`、`Entries:ImmutableArray<StageEntry>`、`TotalDeclaredBytes:long`、`Profile/Catalog:VersionReference`；失败时 Entries 空、total 为 0，不能交付半计划 |
| `CommitPlan` | `Issues:ImmutableArray<ValidationIssue>`、`Identity:ScopedId?`、`RequestDigest:DigestValue?`、`Action:CommitPlanAction`、`Stage:StagePlan?`；非法输入不回显非法身份/摘要；非新提交无 Stage；Issues 非空时只可 Blocked 或有明确冲突问题的 ConflictCandidate |
| `OperationStatus` | `Issues:ImmutableArray<ValidationIssue>`、`Identity:ScopedId?`、`CandidateOutcome:CommitOutcome`、`Resources:ResourceState`、`Recovery:RecoveryAction`；非法输入不回显身份，始终是 ProvidedSnapshot 的纯解释，不包含真实持久成功证明 |

`CommitPlanAction` = `Blocked/NewCandidate/ReplayCandidate/ObserveCandidate/ConflictCandidate/QueryRequired`；`RecoveryAction` = `None/CorrectInput/QueryOriginal/WaitDrain/ObtainPermission/RestoreExactEvidence/ReviewConflict`。所有结果 Issues 均为非 default 数组，排序按 FieldPath、LogicalId、Code 的 Ordinal 顺序，不能随 HashSet 枚举顺序变化。

1. 先观察token；已取消返回单个IEV-CANCEL-009+None，无半计划（Core无自身外部资源，无需WaitDrain；EvaluateOperation的快照资源仍Unknown，见B.4末条），不抛取消丢结果。null顶层参数返回IEV-VAL-001；错误结果允许空Identity/RequestDigest。验证CoreContext/Profile/目录，再检查输入非default/必填；无效目录不继续解析请求。token在每个对象/边/引用循环观察，无无限递归。
2. 检查预算与数组规模上限，再检查 ID、作用域、角色、媒体、声明摘要、版本引用；以 checked long 累加长度和边计数，溢出与越界为 IEV-BUDGET-012。不得先分配超大副本再检查。
3. 校验逻辑ID唯一、来源绑定、required role/item/reference、absence冲突和空集合策略。RequiredItems每个LogicalId/Role/Source按B.1内容精确匹配；找到同LogicalId但Role/Source不匹配返回IEV-IDENTITY-002，找不到必需descriptor返回IEV-VAL-001；任一错误Stage空且total0。禁止record/ImmutableArray默认Equals。absence.IsRequired=false不能覆盖Profile要求；声明IsRequired=true也阻断缺项。RequiredRoles按实际descriptor检查，缺项不算角色。重复同logical拒绝，不靠同hash合并；同blob不同logical合法。
4. 建 child→local parent 图，ChildId 必须是实际 descriptor，local parent 只能来自本请求 descriptor，external parent 必须在 ExternalParents 精确登记；缺项不能当作存在的父节点。派生角色至少一条父边，Acquisition 不能冒充派生；关系角色/变换按 Relations 校验。使用有界迭代图遍历，检查连续顺序、循环及 MaxGraphDepth（单节点深度1，外部父为一层叶节点）。生成父先子后拓扑次序，同层 ScopedId 的 ScopeId/Value Ordinal 排序；ParentIds 按 RelationKey Ordinal、原 Order 顺序列出，不按 blob hash 排序。同父可被多子引用；Core 不声称外部父项完整。
5. `Validate`返回全部可定位问题；`PlanStage`用同一校验生成Entries/total，任何问题返回空计划。`PlanCommit`先校验CommitDescription、stage和snapshot身份/完整ContractKey(Kind,ResponseVersion)；`EvaluateOperation`同样先核完整键，不能仅搜索版本字符串。拒绝未知Kind/未登记完整键，不降为NotFound，不生成新提交/回放计划；错误按B.1确定。
6. 合法 snapshot 首先判 PermissionDenied→Blocked+IEV-AUTH-005（仅解释输入，不做授权）；NotFound→NewCandidate（没有原摘要可比）；其它状态再完整比较原请求摘要域/算法/canonical/值。同身份不同摘要→ConflictCandidate+IEV-CONFLICT-004；同摘要 Committed→ReplayCandidate；InProgress→ObserveCandidate；Unknown→QueryRequired；Rejected/Corrupt→Blocked+恢复。Conflict 不含 Stage；新建仍只是假设，后续门须权威解析/竞争。
7. `EvaluateOperation` 校验完整快照形状：Committed 缺 Receipt、Receipt 错身份/域/版本→Issues + Corrupt 候选；Unknown 永不变成 Committed；ResourcesReleased 仅表示资源；其余保持原候选结果和正确恢复动作。处理结束再次观察 token；取消/超时不产生半计划。

合法快照的Recovery固定：NotFound/Committed→None，InProgress/Unknown→QueryOriginal，PermissionDenied→ObtainPermission，Corrupt→RestoreExactEvidence，Rejected→CorrectInput；快照资源仍Active/CancelledPendingDrain/DrainUnknown且业务结果非Unknown时，资源等待建议WaitDrain优先于None/CorrectInput，不能改变CandidateOutcome。Unknown总保留QueryOriginal并按Resources显示资源观察需要。本规则只解释输入状态，不实际发查询。过期/取消Stage返回空Entries、total0；对应CommitPlan为Blocked、Stage=null。校验已确认的Error字段路径给稳定Issues，G1自身不生成OperationId/持久回执/保持根。

### B.3 Gate-2/3 的本地封套与返回类型

这些记录不冻结 C-04/C-07 私有事实字段/政策序列化；模块通用证据/回执/保持登记封套由B.6定义，业务Payload与DecisionDigest仍按原Owner合同验证，禁止将封套内容解释成质量放行权。

| 类型 | 必填字段、边界和失败语义 |
|---|---|
| `AccessContext` | `AuthorizationReference:ScopedId`、`PurposeKey:string`、`ObservedRevocationGeneration:long`（≥0）；引用非权限证明，授权端口按当前代次复核。不可含客户端 Approved bool、原始令牌或数据库句柄 |
| `OperationBudget` | `Profile:VersionReference`、`Total/Queue/Io/Drain:TimeSpan`（均>0有限，子阶段不得延长 Total）、`MaxBytes:long`、`MaxBufferedBytes:long`、`MaxQueueEntries/MaxConcurrentIo:int`（均>0）；构造接纳时以单调时钟形成固定截止点，重试/分页式分块不能刷新期限 |
| `FrozenFactEnvelope` | `Reference:FactReference`、`Payload:ImmutableArray<byte>`；由 C-04 受控映射生成，长度在接纳预算内，实际 digest 按批准合同计算，生产数值/枚举由 C-04 校验。模块只提交冻结载荷，无领域反序列化/改判权限 |
| `EvidenceContent` | `LogicalId:ScopedId`、`Source:IEvidenceContentSource`；与 descriptor 一一对应，无重复/多余源；缺项不用 source。source 不在持久合同中保存 |
| `CommitRequest` | `Description:CommitDescription`、`Fact:FrozenFactEnvelope`、`Contents:ImmutableArray<EvidenceContent>`、`Access:AccessContext`、`Budget:OperationBudget`、`OperationId:string`；Description 与 Fact 引用一致；OperationId 只诊断 |
| `CommitResult` | `Outcome:CommitOutcome`、`Receipt:CommitReceipt?`、`Issues`、`Resources:ResourceState`、`OperationId:string`；只有 Committed 才有已核原 Receipt；Unknown/InProgress 不交假回执，持久恢复独立于资源状态 |
| `CommitReceipt` | `Reference:ReceiptReference`、`FactRevision:VersionReference`、`Manifest:VersionReference`、`CommittedUtc:DateTimeOffset`（UTC offset 0）、`ResponseVersion:string`；身份/摘要全部相互绑定；不含 PASS、网络 ACK 或设备结果 |
| `CommitRecoveryRequest` | `Identity:ScopedId`、`OriginalRequestDigest:DigestValue`、`OperationKind:string`（EvidenceCommit）、`ExpectedResponseVersion:string`、`Access:AccessContext`、`Budget:OperationBudget`、`OperationId:string`；只按原身份恢复，当前授权先于存在性/冲突信息披露 |
| `CommitRecoveryResult` | `Outcome`、`Receipt?`、`Issues`、`Resources`、`OperationId`，约束同 CommitResult；返回原持久响应，不重发提交、不续传或推进 recovery journal |
| `EvidenceReference` | `Receipt:ReceiptReference`、`Manifest:VersionReference`、`LogicalId:ScopedId`、`Object:VersionReference`；四者须存在批准关系、作用域一致；定位不包含任意路径/URI |
| `EvidenceReadRequest` | `Reference:EvidenceReference`、`Access:AccessContext`、`Budget:OperationBudget`、`Mode:EvidenceReadMode`、`Range:ByteRange?`、`RequestGeneration:long`（>0）、`MaxChunkBytes:int`（>0且≤Profile）、`OperationId:string`；MetadataOnly 禁用 Range；VerifyBeforeDelivery 禁用 Range；StreamingVerify 可指定 Range |
| `ByteRange` | `OffsetBytes:long`（≥0）、`LengthBytes:long`（>0）；checked Offset+Length≤实际对象长度且≤读取 MaxBytes；不静默截断；无 range 表示全对象 |
| `EvidenceReadResult` | `Status:EvidenceReadStatus`、`Lease:IEvidenceReadLease?`、`Metadata:EvidenceMetadata?`、`Integrity:IntegrityReport`、`Issues`、`RequestGeneration`；成功的 MetadataOnly 无 lease；成功字节读取必须有 lease；其它状态无 lease/像素，并按字段权限抑制 metadata |
| `EvidenceMetadata` | `Reference:EvidenceReference/Role:EvidenceRole/MediaType:string/LengthBytes:long/StoredDigest:DigestValue/Source:SourceBinding/Encoding:VersionReference/ImageInfo:ImageDescription?/Parents:ImmutableArray<ResolvedEvidenceLink>/Absences:ImmutableArray<EvidenceAbsence>`；不得以剔除隐藏父项后声称完整 |
| `ResolvedEvidenceLink` | `Child:EvidenceReference/Parent:EvidenceReference/Order:int/RelationKey:string/Transform:VersionReference?`；每一父/子是已解析的精确不可变版本，范围/顺序/transform按原EvidenceLink核对，不暴露存储路径；全部对应目标独立授权 |
| `IntegrityReport` | `State:IntegrityState`、`Expected/ActualDigest:DigestValue?`、`Expected/ActualLengthBytes:long?`、`VerifiedRange:ByteRange?`、`ClosureComplete:bool`、`Issues`；FullVerified 必须完整长度/保存字节 hash 和必需闭包全部通过；其它状态不能据此重算/放行 |
| `EvidenceChunk : IDisposable` | `Bytes:ReadOnlyMemory<byte>`、`OffsetBytes:long`、`IsEnd:bool`、`Issues:ImmutableArray<ValidationIssue>`、`Resources:ResourceState`；唯一分离约定：成功数据块Bytes非空/IsEnd=false/Issues空，包括最后数据块；释放后下一调用终检通过才返回Bytes空/IsEnd=true/Issues空的独立EOF，OffsetBytes=交付区间末端。错误块Bytes空/IsEnd=false/Issues非空。禁止非空Bytes+IsEnd=true和空成功非EOF块；合法空对象直接EOF。每lease只许一个未释放chunk，所有块含EOF/错误均Dispose；Dispose后Bytes不可用、重复Dispose幂等 |
| `ReadGuardResult` | `Allowed:bool`、`RequestGeneration:long`、`Issues`；只重新检查该lease原目标/Stamp/代次/范围/期限，不申请新权限/延长期限；拒绝停止后续交付并触发Invalidated |
| `EvidenceReadInvalidatedEventArgs` | `RequestGeneration:long`、`OperationId:string`、`Code:string`；只允许原代次，事件锁外派发，订阅异常只诊断。leaseDispose后退订Authority、归还回调资源；页面不能清新代次 |
| `CloseOptions` | `DrainTimeout:TimeSpan`（>0有限）；不以等待者取消刷新原关闭期限 |
| `CloseReport` | `State:CloseState`、`Resources:ResourceState`、`RemainingOperationIds:ImmutableArray<string>`、`Issues`；Closed 必须 ResourcesReleased 且残留空；DrainUnknown 保留隔离，不能升级成功 |
| `RetentionRequest` | `DecisionIdentity:ScopedId`、`Decision:RetentionAction`（Hold/ReleaseHold）、`DecisionDigest:DigestValue`、`Policy:VersionReference`、`References:ImmutableArray<EvidenceReference>`（非空、无重复）、`ExistingHoldId:ScopedId?`、`HoldUntilUtc:DateTimeOffset?`、`Access:AccessContext`、`Budget:OperationBudget`、`OperationId:string`；Hold 无 ExistingHoldId，Until 缺省仅允许 C-07 已批准无期限政策；ReleaseHold 必须现存 HoldId，禁止改范围/附 Until。References 闭包和策略由 Owner 冻结，任何字段变更同决定键冲突 |
| `RetentionQuery` | `DecisionIdentity:ScopedId`、`OriginalDecisionDigest:DigestValue`、`Access:AccessContext`、`Budget:OperationBudget`、`OperationId:string`；当前授权在存在性披露前复核，不自动补保持/解除 |
| `RetentionResult` | `Outcome:CommitOutcome`、`Receipt:RetentionReceipt?`、`Issues`、`Resources`、`OperationId`；Committed 必须核原保持决定回执，其余无假 Receipt |
| `RetentionReceipt` | `DecisionIdentity:ScopedId`、`DecisionDigest:DigestValue`、`HoldId:ScopedId`、`Policy:VersionReference`、`References:ImmutableArray<EvidenceReference>`、`ReferenceEpoch:long`（≥0）、`HoldUntilUtc:DateTimeOffset?`、`IsReleased:bool`、`RecordedUtc:DateTimeOffset`（offset0） |

`EvidenceReadMode` = `MetadataOnly/VerifyBeforeDelivery/StreamingVerify`；`EvidenceReadStatus` = `Opened/MetadataAvailable/NotFound/PermissionDenied/Corrupt/Incomplete/Blocked/Cancelled/TimedOut`；`IntegrityState` = `NotChecked/Verifying/FullVerified/PartialUnverified/Mismatch/Incomplete`；`CloseState` = `Closed/DrainUnknown`。产品合同中的`EvidenceManifest`若存在，是本模块B.6 EvidenceManifestDocument的受控映射；通用关系、字段和持久封套以本模块为唯一权威，产品只绑定业务身份/事实/用途，不另造第二套模块Manifest。`OutboxIntent`仍由批准外发合同定义，不能从本地事件直接序列化为outbox；当前模块不提供默认Outbox Schema/交付动作，未批准意图不写outbox。

预期输入/权限/预算/存储失败返回 typed Issues，不泄露原始异常。CommitOutcome.Rejected 的 Issues 区分未发送的取消/超时/输入拒绝；可能已发送但无法证明只可 Unknown，不能用 Rejected 表示已回滚。接纳后调用方取消可提前观察 CancelledPendingDrain/Unknown，但后台追踪和保持继续；严重 CLR 故障无法承诺回执。IEvidenceReadLease 单实例串行 ReadChunkAsync；并发第二次在 I/O 前返回 IEV-VAL-001 的空错误 chunk。DisposeAsync 停止该 lease 后续交付并观察真实排空，有限期限来自 read Budget.Drain；未知抛 §6.1 的 EvidenceDrainIncompleteException，保留隔离。Runtime 查询类非法输入 Identity/OperationId 未有效时不回显原值，空诊断 ID 只用于接纳前错误，不能保存为空业务身份。

### B.4 Runtime 的装配类型闭包

本节类型仅在 Runtime 包，允许受信任Host引用 IM-066 Contracts；不进入 Core、事实/Manifest DTO或操作员事件。不存在 request.object/dynamic/Func 委托万能入口。§8.2 的 BindingInput/Decode 输出按下列封闭分支实现为 abstract record + sealed record 派生，新增分支须修订本指导。

| 类型/分支 | 唯一字段与约束 |
|---|---|
| `BindingContext` | `Access:AccessContext`、`Stamp:AuthorizationStamp`、`Budget:OperationBudget`、`OperationId:string`、`RemainingIoBudget:TimeSpan`；Runtime在调用Encode前从原单调截止计算，正有限且≤Budget.Io/Total剩余；Binding无Clock/IO，不自行重新开预算。Encode后发送前Runtime再次扣除编码耗时，Budget原值不变 |
| `ReserveCommitInput` | Context、Description:CommitDescription；在已核当前权限和正式请求canonical之后产生，不含输入source |
| `FinalizeCommitInput` | Context、Description、Fact:FrozenFactEnvelope、Reservation:CommitReservation、Objects:ImmutableArray<SealedEvidence>、Links/Absences（原EvidenceRequest的精确数组）；无新增产品字段，不接受计划当已保存对象 |
| `ResolveCommitInput` | Context、Request:CommitRecoveryRequest |
| `ResolveEvidenceInput` | Context、Request:EvidenceReadRequest |
| `ApplyRetentionInput/ResolveRetentionInput` | Context + 各自唯一 RetentionRequest/RetentionQuery，不混合两个种类 |
| `ListRootsInput` | Context、`SnapshotId:string?`（首次null）、`ExpectedReferenceEpoch:long?`（与Snapshot同时有值）、`NextSequence:long`（≥0）、`MaxEntries:int`（>0受Profile）；只列本Owner登记根，不是通用分页查询 |
| `CommitReservation` | `Identity:ScopedId`、`RequestDigest:DigestValue`、`Epoch:long`（>0）、`ObjectOperations:ImmutableArray<ObjectReservation>`、`Mutations:ImmutableArray<TechnicalMutationRef>`；并发CAS只有一个epoch活跃，同键重入只返回原分配；Objects数量/来源与Description一致。Mutations仅含已形成完整身份的原注册事务，不预填未来Finalize摘要 |
| `ObjectReservation` | `LogicalId:ScopedId`、IM-066 `OperationIdentity Operation`、`ObjectKey Key`、`OperationIdentity? VerificationOperation`；服务在源打开前固定Stage身份/Key，Verify在实际ObjectRef形成后按B.5补原完整身份，形成前null，不允许null查询；不要求调用者预知正式对象revision |
| `SealedEvidence` | `Descriptor:EvidenceDescriptor`、IM-066 `ObjectRef Object`、`ActualStoredDigest:DigestValue`、`ActualLengthBytes:long`、`StorageReceipt:FileObjectReceipt`；仅真实封口/发布回执，长度/hash/格式与原描述核对。Object在适配层映射为Core VersionReference，不泄漏存储句柄 |
| `BindingCommand` | `Kind:EvidenceBindingKind/Mode:BindingCommandMode`、IM-066 `CallContext Context/VersionRef Binding/StorageBindingDescriptor Descriptor/OperationIdentity? Identity/IOwnerStoragePayload Payload/ImmutableArray<byte> CanonicalPayload/ImmutableArray<ObjectRef> References`；Read的Identity=null，仅构成RegisteredReadRequest；Write的Identity非null，仅构成RegisteredTransactionRequest；精确目录生成、无任意SQL |
| `BindingResponse` | `ExpectedInput:BindingInput/ExpectedCommand:BindingCommand`、IM-066 `VersionRef? ResultSchema/ImmutableArray<byte> ResultBytes/ImmutableArray<ObjectRef> References/OperationRecord? StoredOperation/StorageTaskStatus? TaskStatus`；Read无StoredOperation/TaskStatus，Write保留原状态/身份；完整原操作种类/identity/schema/摘要都由Decode检查，CannotResolve返回typed Unknown/Corrupt，不默认Completed |
| `ReservedBindingResult` | `Outcome:CommitOutcome`、`Reservation:CommitReservation?`、`Receipt:CommitReceipt?`、Issues；获准新reservation为InProgress且有Reservation；原Committed仅有原Receipt；两者不得同时；Rejected/Unknown/PermissionDenied无假reservation |
| `CommitBindingResult/EvidenceBindingResult/RetentionBindingResult` | 构造依次为`CommitBindingResult(CommitRecoveryResult Result, ImmutableArray<TechnicalMutationRef> Mutations)`、`EvidenceBindingResult(EvidenceMetadata? Metadata, EvidenceReadStatus Status, ImmutableArray<ValidationIssue> Issues)`、`RetentionBindingResult(RetentionResult Result, ImmutableArray<TechnicalMutationRef> Mutations)`；仅技术桥增加原mutation投影，错预期分支Corrupt，不把Receipt解释为Reservation |
| `RootBindingResult` | `SnapshotId:string`、`ReferenceEpoch:long`（≥0）、`Entries:ImmutableArray<EvidenceRoot>`、`NextSequence:long?`、`Complete:bool`、Issues；每页序号严格连续、无重复，Complete才无NextSequence；未知根保留，不当缺根 |
| `EvidenceRoot` | `Sequence:long`、`RootId:ScopedId`、`Kind:EvidenceRootKind`（Committed/Unknown/ActiveWrite/Backup/Investigation）、`CommitIdentity:ScopedId?`、`Reference:EvidenceReference?`、IM-066 `ObjectRef? ProtectedObject/ObjectKey? ReservedKey`；三目标字段恰一有值。正式结果可见用Reference；已封口但未有Receipt用ProtectedObject；仍暂存且无正式revision用ReservedKey。Root只在Runtime适配层，不能以没有Receipt/object revision丢掉Unknown/活动写入根 |
| `OperationEvent` | `OperationId:string`、`CommitIdentity:ScopedId?`、`Evidence:EvidenceReference?`、`RequestGeneration:long`、`InstanceEpoch:string`、`Sequence:long`（>0）、`Stage:EvidenceStage`、`BytesProcessed:long`（≥0）、`Code:string?`、`Resources:ResourceState`；字段按当前权限脱敏，两个身份可用于不同种类，不包含原图或秘密 |

`IInspectionEvidenceBinding.EncodeAsync` 返回 `ValueTask<BindingCommandResult>`（`Command:BindingCommand?`、Issues）；失败无Command；`Decode` 返回上述封闭 `BindingDecodedResult` 派生分支。CommitReservation 的objects技术ID由注册Reserve在唯一事务内固定，source尚未打开；Binding不能在Encode方法自行读数据库或副作用，只生成已批准命令/codec值，外部调用由runtime预算编排。Root列表读取按不可变SnapshotId/epoch一致性服务IM-066 resolver，期限/页数/条目预算依同Context；不是IM-045用户查询。

`EvidenceStage`枚举固定为 §4.3 的提交/读取阶段加 `RetentionAccepted/RetentionPersisting/RetentionResolved/Closing/Closed`；outbox外投递状态只通过已授权投影观察，不由本模块重发设备/网络动作。资源终态和事件次序按 §§4–6，Sequence只在同一实例/操作单调，不能充当事实时间。

`EvidenceInitializationException.Fault:ValidationIssue`；`EvidenceDrainIncompleteException.Report:CloseReport`，两异常位于Runtime包、只携带安全本地数据。只读lease抛DrainIncomplete时Report残留自身OperationId，State=DrainUnknown；不暴露Store资源Handle。除这些生命周期异常外，可预期失败优先typed结果。内部实现错误需结构化诊断，不转PASS或将任意异常消息直接显示给操作员。

字段表中的`Issues`均为`ImmutableArray<ValidationIssue>`，`Resources`均为`ResourceState`，其余省略类型的同名字段严格复用B.1–B.4已定义类型；不能以object/dynamic代替。全部UTC时点offset为0，全部调用generation/epoch/序号按所属表范围验证，String键统一ScopedId的字符/长度约束，媒体类型另按ASCII规则。AuthorizationStamp.ExpiresUtc必须晚于当前接纳时钟；ObservedGeneration≥0；PolicyVersion必须精确目录绑定，Clock仅Runtime可读，Core只读显式Elapsed。

Core自身无外部资源，方法返回时本地临时集合可释放；这与OperationStatus.Resources的语义不同：后者仅解释所提供快照的外部操作资源状态，不能因Core调用返回而覆盖为ResourcesReleased。EvaluateOperation在取消/超时/快照形状尚未校验时只返回Issues、CandidateOutcome=Unknown、Resources=DrainUnknown，不虚构原操作已释放；在合法快照上按原Resources纯映射。Core测试须分别检查自身无外部资源与原快照未知资源仍未知。

### B.5 技术消费桥与协议夹具的公开形状

本节仅在Runtime及Runtime.Tests，不改变B.1/B.2或G1 Host。以下声明是待实施规格，**没有实际编译/运行结果**。using同附录B并增加`using S = Asun.Platform.StorageDatabase.Contracts;`；所有public sealed record具有所列公开主构造器，无默认参数，§8.2的EvidenceRuntimeDependencies/EvidenceRuntimeOptions也依其字段顺序公开主构造。接口和具体Binding在Runtime；协议Fake类型仅在Runtime.Tests的`Asun.Modules.InspectionEvidence.ProtocolFixtures`，供§9.3两消费者使用，**不发布产品Fake DLL、不实现第二套生产存储后端**。IM-066真实C1协调器/后端的集成测试另用其原Factory，不拿本边界Fake声称上游C1已执行。

```csharp
// namespace Asun.Modules.InspectionEvidence.Runtime
public enum EvidenceBindingKind {
    ReserveCommit, FinalizeCommit, ResolveCommit, ResolveEvidence,
    ApplyRetention, ResolveRetention, ListRoots
}
public sealed record EvidenceStorageRoute(string LogicalScope,
    ScopedId AuthorizationReference, S.StorageScope Scope, S.StoreRef Store,
    S.CallerRef Caller, string OwnerKey, string StorageDomain);
public sealed record EvidenceBindingRegistration(EvidenceBindingKind Kind,
    S.StorageBindingDescriptor Descriptor, S.IStoragePayloadCodec InputCodec,
    S.IStorageResultCodec ResultCodec);
public sealed record EvidenceFormatMap(VersionReference Encoding, S.VersionRef Format,
    S.VersionRef DurabilityProfile);
public sealed record EvidenceStorageBridgeOptions(VersionReference Version,
    ImmutableArray<EvidenceStorageRoute> Routes,
    ImmutableArray<EvidenceBindingRegistration> Registrations,
    ImmutableArray<EvidenceFormatMap> Formats, S.StorageInputLimits InputLimits,
    TimeSpan StorageMaxOperationTime, TimeSpan StorageWaitBudget,
    TimeSpan MinStorageLeaseTtl, TimeSpan MaxStorageLeaseTtl);
public interface IEvidenceBindingCodec {
    VersionReference Version { get; }
    S.IOwnerStoragePayload MakePayload(BindingInput input, int maxBytes);
    BindingDecodedResult Decode(BindingResponse response, int maxBytes);
}
public sealed record TechnicalMutationRef(EvidenceBindingKind Kind,
    S.OperationIdentity Identity, S.VersionRef Binding);
public enum EvidenceBridgeEvidenceClass { ProtocolFake, SoftwareIntegration, PhysicalQualification }
public sealed record EvidenceBridgeObservation(EvidenceBridgeEvidenceClass EvidenceClass,
    string HostId, string CaseId, string Phase, TechnicalMutationRef? Mutation,
    S.TaskHandle? StorageTask, ResourceState Resources, long ElapsedTicks,
    long? ExpectedBytes, long? ActualBytes, DigestValue? ExpectedDigest,
    DigestValue? ActualDigest, long AuthorizationGeneration,
    ImmutableArray<ValidationIssue> PrimaryIssues,
    ImmutableArray<ValidationIssue> CleanupIssues);
```

Options Routes/Registrations/Formats非default、无重复、总条目/字节受InputLimits与ValidationProfile双限；同Scope/授权引用唯一route，StorageDomain需在已采纳Store Profile内。七种Kind各恰一登记：三个Write为Reserve/Finalize/ApplyRetention，其余Read；Purpose/OwnerKey/输入输出Schema/codec全字段与Host注入Store目录相同。InputCodec.PayloadType exact等于MakePayload返回类型，不能基类/接口兼容匹配。技术映射格式、StatementCatalog、隔离/行数/Retry全部来自该受信任目录，不在请求临时填值；正式注册内容仍Owner交接。TimeSpan均有限正值，Wait≤MaxOperation，MinTtl≤MaxTtl；新阶段不能因MinTtl超过剩余预算而强行延长（拒绝）。InputLimits八项字段/范围复用IM-066§6.3，CanonicalPayload/ResultBytes/References同时受本模块预算。技术codec.Version必须与Options.Version及Runtime.BindingVersion精确对应，由构造核验。

**技术键唯一算法：**SHA-256输入为ASCII `IM015-TECH-ID-1`无终止byte，然后固定六个字符串：逻辑Scope、逻辑Id、Kind名称、SlotScope、SlotId、route.OwnerKey，每串为strict UTF8（拒非法代理）+little-endian Int32字节长度；键为`iev-`+64位小写hex。前三种Write用提交/决定逻辑Scope/Id、其EvidenceBindingKind名称，SlotScope/SlotId均为空；Stage/Verify用原提交逻辑Scope/Id、Kind字符串`Stage`/`Verify`、对象LogicalId.Scope/Value作为两独立slot字段，不串接斜杠。OperationId与IdempotencyKey都用该稳定键，诊断OperationId不进入键。Hold/Renew/Release为本实例控制身份，不能当durable mutation。同逻辑键变载荷得到同技术键、不同PayloadHash，Store报Conflict；Kind/对象槽不同则键不同。StoreId/Generation/StorageScope显式在完整OperationIdentity及IM066请求hash中，不在键hash重复编码；route改变后禁止把它当原操作恢复，原route/身份在reservation保留。SHA碰撞按内容冲突失败，不认同一对象。Stage/Verify完整PayloadHash仅用原FileObjectRequest/FileVerificationRequest调用IM066 Hasher计算，绝不使用此键hash充PayloadHash。

**原Mutation索引：**B.4的Mutations只保存**已经完整形成**的Reserve/Finalize/ApplyRetention原身份；Stage/Verify保存在ObjectReservation，构造参数顺序严格为`(LogicalId, Operation, Key, VerificationOperation)`。Reserve服务在分配固定Key后按声明ExpectedBytes/ExpectedHash/Format及原route形成Stage完整身份；实际ObjectRef形成后才计算原Verify身份，不能把待定hash写成已固定身份。Finalize身份在封口集合完成后计算，其Payload不包含自身mutation索引，避免自hash循环；实际响应/只读Resolve再投影该原身份。同一对象同语义Verify重放按原identity观察，不第二次执行；最后发布前必须取得该次实际验证已完成与当前授权/hash核对，不能用旧Verified标签冒充刚读取的字节。真实部署如要求重复物理Verify必须另冻结观察身份/保留规则，本技术片不暗加随机验证operation。该索引为Runtime消费投影，不另建平台事实表；正式Owner负责采纳其持久保存，Fake仅存封闭技术状态。Query按原完整身份，不因新预算/当前Caller变更改PayloadHash。索引缺失时逻辑恢复仍可返回Unknown，但不猜原技术操作或再发Write。

**Fake公开构造闭包（namespace ProtocolFixtures）：**

| 类型/公开成员 | 完整字段/行为 |
|---|---|
| EvidenceProtocolFakeOptions | `VersionReference Version/TimeSpan OperationLimit/TimeSpan WaitBudget/TimeSpan CleanupBudget/TimeSpan HoldTtl/TimeSpan AuthorityLifetime/int MaxTasks/int MaxLeases/long MaxRetainedBytes/int MaxPayloadBytes/int MaxResultBytes/int MaxReferences/int MaxSnapshots`；正有限，Wait≤Operation，TTL≤Operation，AuthorityLifetime覆盖两Host suite，计数checked；无默认值。均为合成测试值，不是生产Profile |
| EvidenceProtocolFixture | `CoreContext Core/CommitDescription Description/FrozenFactEnvelope Fact/ImmutableArray<ProtocolSourceBytes> Sources/AccessContext Access`；各字段逐项与目录核对，Description.RequestDigest以本节ProtocolCodec重算，旧§9.1纯描述SyntheticRequest不是canonical证明 |
| ProtocolSourceBytes | `ScopedId LogicalId/ImmutableArray<byte> Bytes/int MaxReadBytes`；bytes非default、与descriptor长度/StoredDigest一致，正MaxReadBytes≤Profile.MaxChunkBytes；每次Open新独占只读流，所有正读最多MaxReadBytes，0才EOF；不共享调用方数组 |
| EvidenceProtocolFakeFactory | `public EvidenceProtocolFakeFactory(EvidenceProtocolFakeOptions options)`；`public EvidenceProtocolFakeRig Create(EvidenceProtocolFixture fixture)`同步、零真实IO/线程，校验后创建全新Store/Authority/Binding/目录；失败EvidenceInitializationException，无活资源。Factory不持全局状态、不依赖其它Host |
| EvidenceProtocolFakeRig | public sealed class、仅Factory构造；只读`EvidenceRuntimeDependencies Dependencies/EvidenceRuntimeOptions RuntimeOptions/CommitRequest Commit/EvidenceReadRequest Read/CommitRecoveryRequest Recovery/EvidenceHostRoot Root`，读请求初始指向其合成预定精确Receipt/Object；尚未Seed/Commit时返回NotFound，不自动Seed。`void SeedCommitted()`仅在任何调用前，按同codec建立合成事实/对象/根；`void SetFault(EvidenceProtocolFault fault)`在下次相应协议点注入一次；`void ReleaseBarriers()`放开此rig所有闩锁并禁未来注入；`void RevealOriginal()`只解除查询遮蔽，不执行提交/恢复写；`void Reauthorize()`增加授权代次并签新Stamp，Host须新Access，原lease不复活 |
| rig的查询/收尾 | `void HoldConstructed(EvidenceHostReservation reservation, InspectionEvidenceRuntime runtime)`在对应已预约MaxInstances槽中强持构造成功实例，Attach前零IO；跨rig/重复/超额拒绝且保留原Owner。`RetentionRequest Canonicalize(RetentionRequest request)`纯计算本夹具决定digest，域ProtocolRetention/v1、canonical ProtocolCanonical/v1，SHA256输入为ASCII IM015-PROTOCOL-RETENTION-1+决定Identity/Action/Policy/References/ExistingHoldId/HoldUntilUtc按下述原语顺序，不含自身digest/Access/Budget/OperationId。`EvidenceProtocolCounters Observe()`无IO；`ValueTask<RootDrainResult> CloseAsync(CancellationToken cleanupToken)`以Options.CleanupBudget独立deadline关闭所有Root预约/本rig-owned Fake Store；原Task单次保存。到期保留rig/依赖/原Task/lease，不Dispose活Stream；重复Close观察同任务。Store只在全部本模块实例与内层资源Released后Dispose，原Primary与Cleanup分存。测试入口进程有限suite根强持所有rig直到Released或未完成报非零 |
| EvidenceProtocolCounters | `int SourceOpens/ReserveWrites/FinalizeWrites/RetentionWrites/StageCalls/VerifyCalls/ReadOpens/ReleasedStreams/ActiveTasks/ActiveLeases/ActiveSnapshots/PendingPublications/CommittedRoots/UnknownRoots/long RetainedBytes/long FakeStateBytes/ImmutableArray<EvidenceBridgeObservation> Observations`；构造按该序每项独立参数。RetainedBytes是Root/worker/lease仍在借用的动态资源额度，FakeStateBytes是夹具自己拥有的有界目录/ledger/byte库/观察记录，二者均非负且各≤MaxRetainedBytes；峰值总内存测二者之和，不能把释放引用等同GC内存归零。观察数组最多checked(MaxTasks×128)条，超额使测试失败，不静默丢断言 |
| EvidenceProtocolFault | enum `None/DropFinalizeResponse/HideOriginal/TailCorrupt/RevokeBeforeDelivery/LateReadLease/BlockedStage/CleanupFailure/IncompleteRoots/WrongResultSchema`；作用点和断言见§12.3，不传任意callback/无限sleep |

上述enum还包含§12.3明确的MissingMutation/WrongOperationKind/WrongObjectHash/ChangedRootSnapshot/DuplicateRootSequence；仅这些封闭分支。rig.Read/Commit/Recovery是只读getter投影：Reauthorize后Read.Access/Recovery.Access取得当前代次，原已交付request/lease仍绑定旧代次，不就地改旧值。Fake clock/权限/mapper均由rig显式创建并强持；Factory内构造`RegisteredInspectionEvidenceBinding(protocolCodec, storageBridge)`并注入Dependencies，不绕开本技术适配用另一套Binding。每个Encoding映射独立Format版本与`fixture-durability`技术Profile，Receipt.DurabilityProfile精确相同；该合成Profile不声明介质VerifiedDurable。

DropFinalizeResponse的公开观察是原Identity、原TaskHandle的Completed StorageTaskStatus，Result为State=Unknown/Commit.State=Unknown、原ResultSchema、空ResultBytes、无业务Receipt，Fault=CommitUnknown；后台原ledger仍是同一次Committed响应，遮蔽期间Query返回同原identity Unknown，Reveal后只读返回原记录。不能把响应丢失写成RequestRejected或新Task。其它错schema/损坏响应使本模块PrimaryIssues=Corrupt，可能已写时Outcome=Unknown（资源可以已Released），不能由解码失败宣称事务回滚/Rejected。故障计数及原mutation保留，查询不写修复记录。

Fake的route/ledger/对象/根目录总项数各≤MaxTasks，活snapshot≤MaxSnapshots，字节库/输出/观察记录总FakeStateBytes≤MaxRetainedBytes；满额拒绝新协议调用，不淘汰未决行。Close后RetainedBytes可为0，但FakeStateBytes及Unknown/Pending/Committed根仍可非零，Host不得要求它们清零来冒充排空；正式Store持久状态同样不属短期lease资源。进程结束前rig仍由suite根强持，FakeState只作合成证据，不声称跨进程持久。

Fake Rig Store实现IM-066 Contracts的IStorageDatabase/IStorageSession/FileObjects/lease接口，**仅模拟本模块边界**。StorageInputLimits=(256,MaxPayloadBytes,MaxResultBytes,MaxReferences,MaxReferences,MaxRetainedBytes,64,MaxPayloadBytes)；支持本测试七条注册Binding及FormatMap，OwnerKey=`im015-protocol-fixture`，StorageScope五字段=`LogicalScope/test-site/test-line/test-station/test-device`，StoreId=`fixture-store`、Generation=1；CallerRef=`fixture-principal/fixture-authority`，所有VersionRef Revision=1且hash=SHA256(strict UTF8 `IM015-PROTOCOL-1/`+对应唯一label)，本地VersionReference scope仍为LogicalScope。Domain=`fixture-bytes`。七descriptor Kind按上表；Purpose=Production（Write）/Query（Read），隔离Serializable（Write）/RepeatableRead（Read）；受控单命令、Min/MaxAffectedRows=1/1（Write）或0/0（Read）、MaxCommands=1、MaxRetries=0、RetryDelay/lock/statement预算为WaitBudget，AllowEmptyBatch=false。每个binding/input/result codec/statement/Format均用独立label版本/hash，注册只在Create一次；真实SQL不生成。Root/Format未知不支持，不用空默认放行。

Rig根Options=(2,MaxTasks,MaxLeases,MaxRetainedBytes,CleanupBudget)。DefaultBudget=(Core.Profile.Version,OperationLimit,WaitBudget,OperationLimit,CleanupBudget,Core.Profile.MaxTotalBytes,MaxRetainedBytes,MaxTasks,1)；Runtime.Options=(Core.Profile,Core.Catalog,DefaultBudget,CleanupBudget,HoldTtl,MaxTasks,MaxRetainedBytes,Version,StorageBridge)。AuthorityStamp绑定fixture.Access.AuthorizationReference及当前代次，起始UTC=2026-10-11T00:00:00Z、到期+AuthorityLifetime；TimeProvider用该UTC+单调Stopwatch，不以固定UTC延长预算；测试需要到期时只推进独立可控时钟，不改OS。Store权限映射只允许本rig Scope/Caller/Owner/对象，越界拒绝。rig不Dispose由Host仍持有的fixture输入（都是不可变BCL值）；新返回Stream由Runtime拥有，Store借用直到原Stage任务结束。

**ProtocolCodec仅是模拟codec，完整线格式：**输入magic为ASCII `IM015-PROTOCOL-INPUT-1`，result为`IM015-PROTOCOL-RESULT-1`；随后Kind Int32按上述枚举顺序0～6、LogicalScope字符串、对应B.4输入/结果各字段按该表左到右递归展开（按下段排除上下文/自身索引，不序列化BindingResponse的ExpectedInput/Command对象）。字符串strict UTF8+Int32 byte count（null禁止）；nullable为byte 0/1再值；bool byte0/1；enum Int32按本指导列序从0递增；Int32/Int64 little-endian；TimeSpan Int64 ticks；DateTimeOffset仅UTC以UtcTicks Int64；byte array/其它数组Int32 count+元素；ScopedId Scope/Value、DigestValue Domain/Algorithm/CanonicalVersion/Hex、VersionReference Id/Revision/Digest、所有存储记录按IM-066§6声明字段序。SourceBinding.Versions按Id.Scope/Value的Ordinal→Revision数值→Digest各string的Ordinal排序，其余业务数组保持顺序；技术ObjectRef集按上游ObjectKey排序且拒绝重复。default数组/null必填/负计数/超限/未知enum/尾部剩余byte均失败，解码前先限总byte及嵌套计数，禁止反射任意CLR类型。

该输入编码的**语义体**排除BindingContext整项（Access/Stamp/Budget/诊断OperationId/RemainingIoBudget），但包含其逻辑身份及所有实际输入内容；ReadRequest排除Access/Budget/OperationId/RequestGeneration/MaxChunkBytes/Mode/Range，仅在ResolveEvidence读取精确Metadata时使用四项Reference（模式/range是Runtime后续读守卫，不能被codec漏掉后用于别的动作）；ResolveCommit保留Identity/OriginalRequestDigest/OperationKind/ExpectedResponseVersion；Retention保留全部决定语义，排除Access/Budget/OperationId；ListRoots保留全部snapshot/sequence/limit。Fake MakePayload返回唯一`public sealed record EvidenceProtocolPayload(S.VersionRef Schema, EvidenceBindingKind Kind, ImmutableArray<byte> SemanticBytes, ImmutableArray<S.ObjectRef> Objects) : S.IOwnerStoragePayload`；其InputCodec编码Schema/Kind/SemanticBytes/Objects，用同规则GetReferences重解精确Objects。RequestDigest单独SHA256编码ASCII `IM015-PROTOCOL-COMMIT-1`+Description.Identity/Fact完整引用/原EvidenceRequest/ExpectedRevision nullable/Profile，排除Description.RequestDigest/Receipt快照；Fact.Payload={7}的SyntheticFact摘要按原SyntheticBytes；ManifestDigest对原描述+全部实际封口对象/关系/缺项编码、ReceiptDigest对原身份/请求digest/ManifestDigest/Fact修订/响应版本/UTC编码，不把自身hash放进输入。分别登记`ProtocolRequest/v1/ProtocolCanonical/v1`、`ProtocolManifest/v1/ProtocolCanonical/v1`、`ProtocolReceipt/v1/ProtocolCanonical/v1`、`ProtocolRetention/v1/ProtocolCanonical/v1`四项DigestRule。Factory在**新**fixture Catalog版本/hash增加它们（VersionRef label=`protocol-catalog`、References加入该新版本/fixture BindingVersion/Policy与Formats，合计受64项限额），不变更G1或传入Catalog原实例/版本；Options.Runtime.Catalog使用新快照。只有Fixture.Description.RequestDigest重算后才生成Commit/Recovery，持久对象VersionReference的Digest仍StoredBytes域，不改旧对象hash。

Fake解码不是按序号查私有对象令牌：有界完整解析上述字段，重新计算各域摘要、匹配预期Command/Input、重建public typed结果；异Schema/字节尾/Refs错/身份错均返回IEV-CORRUPT-010。技术store按完整OperationIdentity和PayloadHash维护有界route/ledger；同身份同payload查询原记录、异payload冲突，所有只读口零写。Reserve返回Epoch=1及固定对象Stage身份/Key；封口全读至真实EOF，stage模拟PendingPublication；Finalize模拟同一CAS原响应/根发布，DropFinalizeResponse保留原Committed record但对本次/遮蔽查询返回Unknown，Reveal只恢复可见。Retention也按原决定/digest唯一CAS；短TTL lease与持久根分表计数，Close只清短资源，Unknown/Pending/Committed根继续保留于rig技术状态直至测试进程结束，绝不以Close/TTL清零。SeedCommitted使用同codec、同源byte及同固定技术身份，不调用产品入口、不冒充真实生产。所有不相关维护API明确InvalidInput/UnsupportedVersion，测试不把它们算已验能力。

### B.6 模块拥有的证据封套、注册与根快照（本轮设计增量）

本轮定向核实发现：§2已将证据对象/关系/Manifest/技术回执归IM-015，但B.3把所有持久形状统称产品Schema、B.5只有ProtocolFake编码；真实根投影没有公开创建/一致读取闭包。这是**模块内部软件设计欠账**，本节补其唯一规格，不能转写客户外门。复用§16.1既有字节/取消/完整性依据及 [IM-066 当前指导§6.3/6.6/6.7](../storage-database/DEVELOPMENT-GUIDE.md) 的注册/事务/引用目录规格，不重审其接收范围、不改上游、不引入新后端。该增量不是§17.3此前限定接收的一部分；本原会话完成内容审核和文档验证后记录设计准备结论，代码准入状态不自动提升。

#### B.6.1 通用持久文档与Owner最窄输入

以下类型/接口位于现有Runtime namespace，公开sealed record主构造器按字段顺序，无默认；资源类型仅由各自工厂/方法创建。`S`仍为IM-066 Contracts。B.1/B.2、G1请求摘要声明及所有旧codec/domain均保持；本节编码是**模块持久封套v1**，不能重算旧事实、强迫产品改业务canonical或把ProtocolFake字节升级为正式格式。

| 模块文档 | 全部字段、默认/不适用与Owner |
|---|---|
| EvidenceManifestDocument | `VersionReference Version/ScopedId CommitIdentity/DigestValue OriginalRequestDigest/FactReference Fact/VersionReference ValidationProfile/ImmutableArray<EvidenceMetadata> Items/ImmutableArray<EvidenceAbsence> Absences/DateTimeOffset RecordedUtc`；Version.Digest覆盖下文ManifestBody，Id/Revision在body内而自身Digest除外。Items按LogicalId.ScopeId/Value Ordinal排序（只排序模块清单，不改Source/关系/业务载荷）；每个Item.Reference绑定同一receipt identity/manifest版本；hash preimage见下文，禁止自引用循环。Absences保留原顺序，必需缺项不发布 |
| EvidenceCommitDocument | `ScopedId Identity/DigestValue OriginalRequestDigest/string ResponseVersion/CommitOutcome Outcome/CommitReceipt? Receipt/ImmutableArray<TechnicalMutationRef> Mutations/ImmutableArray<ValidationIssue> Issues/DateTimeOffset RecordedUtc`；Committed才带Receipt，Unknown无假Receipt；仅已形成mutation投影，原输入不含此索引。该文档是原响应，不保存显示实例Resources、当前权限或诊断OperationId；资源状态在当前查询另行计算 |
| EvidenceRetentionDocument | `RetentionReceipt Receipt/ImmutableArray<TechnicalMutationRef> Mutations`；只登记上游批准Hold/ReleaseHold决定及完整闭包，Policy/Until/法律条件由C-07，模块不选天数；本封套字节hash不替代上游DecisionDigest |
| EvidenceRootProjection | `VersionReference RootVersion/EvidenceRoot Root/S.ObjectRef? ResolvedObject`；RootVersion是**本模块根投影修订**，不冒充生产Fact revision。Reference根在同一快照解析其精确ObjectRef；ProtectedObject直接逐字段相等；ReservedKey未封口时ResolvedObject=null，不当成零字节对象 |
| EvidenceRootSnapshotPage | `string SnapshotId/long ReferenceEpoch/long TotalEntries/long TotalBytes/long NextSequence/ImmutableArray<EvidenceRootProjection> Entries/long? FollowingSequence/bool Complete/ImmutableArray<ValidationIssue> Issues`；TotalEntries/Bytes指完整快照的root-object投影数/每条EvidenceRootProjection完整canonical字节之和（含完整RootVersion及Sequence，不含RootPage封套、页头、Entries计数或Issues；空集=0），不按物理hash去重；序号从0连续。Complete只表示全部保护根可表达且当前页协议有效，最后页由FollowingSequence=null辨认；不与B.4 RootBindingResult的末页Complete语义混用 |
| EvidenceDocumentLimits | `int MaxDocumentBytes/int MaxArrayEntries/int MaxDepth/int MaxStringBytes/long MaxTotalDocumentBytes`；全部正有限、MaxDocumentBytes<Int32.MaxValue且≤MaxTotalDocumentBytes，各自≤StorageInputLimits及本模块Profile/预算；超限先拒绝、没有隐藏默认 |
| IEvidenceBusinessValidator | `VersionReference Version`；`ValidationResult ValidateFact(FrozenFactEnvelope fact, EvidenceDocumentLimits limits)`、`ValidationResult ValidateRetention(RetentionRequest request, EvidenceDocumentLimits limits)`；由C-04/C-07受信任启动包提供，只做已批准业务格式/摘要/政策校验，零IO/SQL/设备动作、无产品返回改判。ValidateFact不能把原Payload修改为PASS，也不能凭hash声明事实单位有效 |
| EvidenceEnvelopeCodec | public sealed class实现IEvidenceBindingCodec，唯一公开构造`EvidenceEnvelopeCodec(IEvidenceBusinessValidator business, EvidenceDocumentLimits limits, VersionReference version)`；Version为该显式持久格式登记版本。MakePayload/Decode实现§8.4已接收七分支，各步骤/语义体排除规则沿B.5，**魔数/格式改为本节模块持久封套**；业务validator只验证Fact/Retention，不定义模块Manifest/Root字段 |

Codec另公开`ImmutableArray<byte> EncodeManifest(EvidenceManifestDocument document)`、`EvidenceManifestDocument DecodeManifest(ImmutableArray<byte> bytes)`、`ImmutableArray<byte> EncodeCommit(EvidenceCommitDocument document)`、`EvidenceCommitDocument DecodeCommit(ImmutableArray<byte> bytes)`、`ImmutableArray<byte> EncodeRetention(EvidenceRetentionDocument document)`、`EvidenceRetentionDocument DecodeRetention(ImmutableArray<byte> bytes)`、`ImmutableArray<byte> EncodeRoots(EvidenceRootSnapshotPage page)`、`EvidenceRootSnapshotPage DecodeRoots(ImmutableArray<byte> bytes)`，纯同步/零IO，错误抛ArgumentException（安全固定键），Runtime映射typed Issues，已发送且结果错仍Unknown/Corrupt，不谎称RolledBack。未注册business只阻Fact/Retention写及业务验证，不阻仅字节/模块封套解码和精确只读展示；此时构造可用已明确拒绝两写动作的validator，不能对它们返回Valid。

#### B.6.2 唯一编码、域与版本选择

封套为ASCII `IM015EV1`（8byte，无终止）+SchemaCode byte+PayloadLength little-endian Int32+payload；SchemaCode固定Input=1、ReservedResult=2、CommitDocument=3、EvidenceMetadata=4、RetentionDocument=5、Manifest=6、RootQuery=7、RootPage=8。Length必须等于剩余byte，负/超限/尾部/未知code立即拒绝；同一个魔数没有宽松字段扩展，新增字段升新格式/Schema引用并保留旧reader。各Schema固定字段序为上表及B.3/B.4，Input前置EvidenceBindingKind Int32后其语义体，ReservedResult按B.4，Metadata按B.3，RootQuery按B.6.4；无反射式运行类型分派。原语复用B.5已冻结strict UTF8/length、little-endian整数、null presence、array count、UTC ticks、SHA256 lowercase hex字符串；字段名称以B.1真实属性`ScopeId/CanonicalVersion/Hex`为准，**不是不存在的ScopedId.Scope**。嵌套数/深度在分配前累计checked，不接受重复键/default数组/无效枚举；Enum值按各字段表原列序从0，EvidenceBindingKind沿原0～6。ValidationIssue完整字段按B.1声明逐项编码，不能只编码错误码丢字段路径。每个有序数组原序保真，SourceBinding.Versions按Id.ScopeId/Value Ordinal→Revision数值→Digest各string Ordinal排序，编码前仍拒重复Id；ObjectRefs规范排序复用IM066 ObjectKey规则。业务Payload作为有限opaque byte array，**不解析/改canonical**，其FactDigest只由business validator按原C-04规则验证。

本模块新建技术摘要域`EvidenceEnvelope/v1`（canonical `IM015EV1`）、`EvidenceManifest/v1`（`IM015-MANIFEST-BODY-1`）、`EvidenceReceipt/v1`（`IM015-RECEIPT-BODY-1`）、`EvidenceRoot/v1`（`IM015-ROOT-BODY-1`），均SHA-256/64hex；只加入新Runtime Catalog版本与References，G1原目录/ProtocolFake/历史域不改。新记录按其明确format引用选codec，旧记录按其原格式/Schema选旧reader；未知旧reader拒绝，不能将magic相似视为兼容。本模块不再以“正式业务codec未给”推迟上述通用字段/编码决定。

**无自hash循环的唯一预像：**ManifestBody为ASCII `IM015-MANIFEST-BODY-1`+Manifest.Id/Revision+CommitIdentity+OriginalRequestDigest+Fact+ValidationProfile+按排序的每Item**描述体**+原Absences+RecordedUtc。描述体依次`LogicalId,Object:VersionReference,Role,MediaType,LengthBytes,StoredDigest,Source,Encoding,ImageInfo nullable,父项数组,该Item.Absences原数组`，父项依次Parent.LogicalId/Parent.Object/LocalParent bool/Parent.Manifest/外部Parent.Receipt nullable/Order/RelationKey/Transform nullable；LocalParent=true当且仅当父Manifest.Id/Revision等于本次且父LogicalId在本Items内，编码其Manifest只含Id/Revision且外部Receipt=null；LocalParent=false编码父Manifest完整版本/hash及完整Receipt。不得以同名Id隐去外部摘要；Child就是当前LogicalId不重复编码。所有本次Items.Reference中的Receipt各域、当前Manifest.Digest在该body**不出现**。先固定Manifest.Id/Revision与实际对象、关系后算manifest digest，再生成各Reference；ReceiptBody为ASCII `IM015-RECEIPT-BODY-1`+Receipt.Id/Revision+CommitIdentity+OriginalRequestDigest+ManifestDigest+FactRevision+ResponseVersion+CommittedUtc，除自身ReceiptDigest；完整CommitReceipt/Manifest封套仍保存所有交叉引用，解码各自可重建body重算，Runtime同时取得原Manifest/CommitDocument后才核两边一致；独立Manifest解码无FactRevision/CommittedUtc时不假称已核Receipt摘要。RootBody为ASCII `IM015-ROOT-BODY-1`+RootVersion.Id/Revision+Root字段除Sequence（按RootId/Kind/CommitIdentity/Reference/ProtectedObject/ReservedKey顺序）+ResolvedObject nullable（目标完整版本或Key不省略），不含RootVersion.Digest；Sequence仅为快照分页序号，不能改变持久root摘要。RequestDigest仍原Owner给出的批准canonical，不拿EvidenceEnvelope域替代。为ExternalParents无法解析完整EvidenceReference/ObjectRef时拒发布，不猜Scope/Manifest。

模块Manifest/Receipt/Root修订由注册事务同作用域固定：Manifest/Receipt以CommitIdentity作为不可变出生身份，Id为`manifest-`/`receipt-`+SHA256(ASCII `IM015-DOC-ID-1`+type字符串+CommitIdentity.ScopeId/Value，全部length-prefixed strict UTF8)。根另为`root-`+SHA256(ASCII `IM015-ROOT-ID-1`+purpose字符串+origin.ScopeId/Value+slot)，purpose固定commit或hold，origin分别为CommitIdentity或DecisionIdentity；commit的slot为LogicalId.ScopeId/Value，hold的slot为完整EvidenceReference canonical（含Receipt/Manifest/Object全部版本/hash及LogicalId），同LogicalId在不同尝试/Manifest的两条保持引用不得冲突；每个逻辑对象独立根，RootVersion.Id=Root.RootId且ScopeId=origin.ScopeId，不按Object hash去重。Kind状态变化不换出生Id；Hold映射Investigation根、Release只移除此Hold决定根，保留原commit及其它hold根；首Revision=1，同Commit同载荷重放不升revision；修改事实须新上游CommitIdentity，损坏不重写原digest。保持根状态变更只更新RootVersion.Revision的checked前一+1及新body/hash，并保留历史；Epoch不是修订号、实例重启不重置。原业务FactRevision来自唯一C-04写回响应，不从模块revision推断。

#### B.6.3 注册包、模块技术状态和事务边界

注册包的typed wrappers由Create内部唯一创建，不留未公开构造给Host猜测：七个私有`EnvelopeInputCodec`实例实现S.IStoragePayloadCodec，固定登记Version/Schema/Kind，PayloadType exact=EvidenceEnvelopePayload；Encode先核精确类型/Schema/Kind，再返回SchemaCode=1的封套，payload固定Schema完整S.VersionRef→Kind Int32→SemanticBytes length+bytes→Objects数组。SemanticBytes由本codec按B.5各分支语义体形成；不再于封套前额外重复Kind。GetReferences仅从该独立canonical解析Objects且核同Kind对应语义引用集合，不访问原调用方对象。第八个私有`RootInputCodec`固定PayloadType=EvidenceRootQueryPayload、SchemaCode=7及其字段序，GetReferences返回明确Empty（只读root查询不是对象写引用集合），不把Barrier.Keys伪造成已解析ObjectRefs。对应八个私有`EnvelopeResultCodec/RootResultCodec`实现S.IStorageResultCodec，按登记ResultSchema和固定分支解码/验证字节及限额，不以任何SchemaCode自动匹配错误Binding。Wrapper不拥有业务validator/Store。B.6.2中Input字段序以本段为唯一精化，其它Schema不变。

IM066 A1接入仍使用其原IPostgreSqlBindingCodec：本模块在既有Runtime包的PostgreSql namespace实现`EvidencePostgreSqlBindingCodec`，只消费Asun.Platform.StorageDatabase.PostgreSql公开注册接口，公开构造`EvidencePostgreSqlBindingCodec(EvidenceEnvelopeCodec codec, S.StorageBindingDescriptor binding, EvidenceDocumentLimits limits)`，零IO；Version=binding.InputCodec、InputSchema/ResultSchema逐字段匹配。GetParameters仅解码原canonical，按本节受信任StatementCatalog固定位置映射全作用域/技术identity/封套/对象键等有限BCL值；不能接受新SQL/产品delegate。EncodeResult验证命令序号、实际行数、exact列型和一个唯一有限response bytea，按本codec解码再原字节返回，不在客户端编码后补执行第二事务。Finalize在PostgreSQL**同一注册Mutation内**调用原事实子mutation取得FactRevision，使用本模块私有SQL纯编码函数生成Manifest/Receipt/完整响应并持久保存后返回同bytea；SQL函数严格实现B.6相同原语/字段/hash域，须以本节Golden和BCL codec逐字节互验，无IO/额外授权/自选业务规则。不能仅靠客户端EncodeResult生成尚未持久的receipt。八条mapping SQL/迁移是本模块后续实现，不称已创建/运行；C-04只提供原事实mutation，不设计模块SQL编码或技术表。

公开sealed class`EvidenceRegistrationPackage`只由`public static EvidenceRegistrationPackage Create(EvidenceEnvelopeCodec codec, EvidenceStorageBridgeOptions bridge, EvidenceRegistrationOptions options)`创建；字段只读`ImmutableArray<EvidenceBindingRegistration> Bindings/S.StorageBindingDescriptor RootReadBinding/ImmutableArray<S.IStoragePayloadCodec> InputCodecs/ImmutableArray<S.IStorageResultCodec> ResultCodecs/S.StorageOwnerRegistration Owner/S.IStorageOwnerReferenceResolver ReferenceResolver`。Options为公开record`EvidenceRegistrationOptions(VersionReference Version, S.StorageOwnerRegistration Owner, EvidenceDocumentLimits Limits, EvidenceRootResolverDependencies RootDependencies, EvidenceRootResolverOptions RootOptions)`；由构造在零IO下生成七条typed codec及独立第八条RootRead typed codec（不是增加EvidenceBindingKind，RootQuery与ListRoots原签名/Schema不混用），**Owner登记/Profile/StatementCatalog引用必须在启动时提供并逐字段匹配**，Create不安装Schema/SQL、不更改共享Store目录。RootReadBinding取RootOptions.ReadBinding，必须与七项Version不同，其InputCodec exact PayloadType为EvidenceRootQueryPayload；其ResultSchema唯一指本RootPage格式。其余七项exact PayloadType为本节`public sealed record EvidenceEnvelopePayload(S.VersionRef Schema, EvidenceBindingKind Kind, ImmutableArray<byte> SemanticBytes, ImmutableArray<S.ObjectRef> Objects) : S.IOwnerStoragePayload`，字段/References提取顺序沿B.5但不使用EvidenceProtocolPayload类型/魔数。InputCodecs/ResultCodecs含八项，核所有Version/Schema/类型及RootDependencies.Codec为传入同codec、Options Owner与RootOptions.Owner同值。Host将全部descriptor/codec并入IM066 ResolvedStorageConfiguration既有Catalog，把resolver并入ReferenceResolvers；拒重复Version/Owner、不能覆盖旧项。完整串序为Create package→装配上游可信配置/BackendFactory→由上游原Factory.CreateAsync创建Store→RootDependencies.StoreSlot.Attach(Store)→本模块Root.TryReserve→new Runtime/Attach→业务调用，关闭按B.6.4第1项的显式顺序，原Create任务/部分资源强持规则沿§6.2与IM066§7.1.1；本模块不在Runtime构造中创建Store。

**启动登记对齐IM066 0.3.1-prep §6.3：**package只生成固定不可变登记；上游Resolver返回后、BackendFactory之前，由IM066在原目录条目/字节限额内复制Profile/descriptor/Owner/Scope/Store/嵌套数组并建立本实例不可变索引。Host强持原codec/resolver/validator及其零IO、生命周期内不变的声明，不转移所有权，不热换目录或再次Resolve另一份配置。七个EvidenceEnvelopePayload按各Binding.Version定位后才核exact CLR type，不能按PayloadType跨Binding去重。package、Runtime/BackendFactory构造及启动只核resolver声明/Owner映射/技术Schema，**不调用ReferenceResolver.OpenAsync、不枚举根、不要求StoreSlot提前Attach**；原Factory成功后一次Attach才开放本模块调用。旧reader继续按原精确版本登记，不用当前codec覆盖；声明改变封闭失败，不重算历史hash。

模块技术元数据统一迁移到`im015`命名空间，**不是C-04事实表**；所有租户/Store/Generation/Owner全键沿IM066，不引用产品私表。具体SQL/迁移与registered mapping由本模块实现下列精确逻辑形状，不能要求产品Owner另设计模块表。存储物理选型仍IM066 PostgreSQL，不新选数据库。bytea仅有限元数据，不存原始图像。每字段型别：ID为strict UTF8有限text，完整Scope拆五ID，计数/revision/epoch为checked bigint非负，hash存32byte、VersionReference存完整id/revision/domain/algorithm/canonical/hash，UTC=timestamptz，enum=int+CHECK列序；所有外键覆盖全scope/store/generation/owner，不仅id。

| 模块表 / 全键后的唯一键 | 全部有效载荷/约束 | 唯一操作 |
|---|---|---|
| commit_claim / CommitIdentity；UK原Reserve技术OperationIdentity | original_request_digest全域、模块codec/Profile/Binding版本、claim_epoch>0、原Description canonical、原ObjectReservation canonical、Reserve mutation、状态、可空Finalize mutation、可空原commit_document、RecordedUtc | Reserve原子INSERT-if-absent；全请求逐字段/hash同才返回原值，异内容Conflict。旧writer/Unknown不能由expiry/new实例接管 |
| evidence_manifest / Manifest.Id+Revision；UK CommitIdentity | manifest_body_hash、完整manifest封套、完整对象引用集合；hash/关系正确，封口后不可变 | Finalize与业务事实/原响应/IM066 owner_object_reference在同一已授权事务发布 |
| evidence_response / CommitIdentity；UK Receipt.Id+Revision | response_version、完整EvidenceCommitDocument封套、原Reserve/Finalize identities；与claim/manifest关联一致，不能为Unknown伪造Receipt | Finalize同事务；查询只读取，不补行、不改状态；Unknown权威已确认的观察仍由原受管writer保存，普通Query不写 |
| retention_decision / DecisionIdentity；UK原ApplyRetention identity | original_decision_digest全域、原RetentionRequest语义体、EvidenceRetentionDocument、当前权限审计ref（非凭据） | 同键同决定只读重放；异决定Conflict；Hold只新增本决定根，Release只以原HoldId/原范围CAS释放其根，不移除其它根 |
| root_history / RootId+RootRevision；唯一(root_id,valid_from_epoch) | 完整EvidenceRootProjection、valid_from_epoch、nullable valid_to_epoch；各root最多一个当前版本，区间不重叠、半开[from,to) | claim/Finalize/Retention同事务追加旧to/新from；**epoch取同IM066引用协调边界实际ReferenceEpoch**，不能本模块自增另起epoch |

受信任StatementCatalog的固定输入/输出及执行顺序：Reserve参数=全作用域/原技术identity/Description封套/固定对象Key+Stage请求摘要；只变claim/root_history，结果是ReservedResult，不触业务事实。Finalize参数=原claim epoch/请求digest/实际ObjectRefs/Manifest与响应封套/冻结业务payload；先锁claim并比较原epoch/hash→核持久发布保护/对象封口/完整body hash→仅调用**C-04已登记的原事实mutation**写冻结payload并取得FactRevision→将此revision组成最终receipt/模块response→写manifest/response/claim状态与持久root/IM066 owner_object_reference→校验ResultCodec→commit。业务FactRevision在事务生成时才确定，不在客户端预造；receipt创建在同受信任注册包内用纯codec，不执行外部IO。`FinalizeCommitInput`不要求预知业务revision。SQL函数/语句目录的完整审核与部署作为代码实现/产品mapping验收输入，不以任意delegate扩展事务，也不另开放事实写入口；该原子边界若产品事实Store无法参与，拒该生产绑定，不能提交模块表后假称业务一起成功。

**同事务epoch接线对齐IM066 §6.7.3：**本模块Owner固定SQL只读取`current_setting('app.im066_reference_epoch',true)`并严格转正Int64；缺失/空/非正值拒绝整个写事务。该E由A1在原事务内按reference_authority→route/attempt→对象/引用技术行→Owner领域行的锁序重验双token/物理guard后checked分配e+1；包括References=Empty的Reserve/保持写均走此边界。本模块以同一个E关闭root_history旧区间、建立新区间并改变本Owner/完整Scope/Store的im066.owner_object_reference，不能使用token.ReferenceEpoch观测值、自增计数或客户端payload给新提交定界；不得改上游reference_authority/其它Owner引用/技术receipt。A1另以事务local GUC提供已核authority id/epoch/publish fence，Owner不得更改；GUC不是授权/fence证明，保护仍由原双token/guard/RLS保证。根、引用、原事实/响应及E同commit或rollback；Unknown不另开事务补根/响应/重分配E。普通Read、QueryOperation与Created=false重放不分配E，不能从Query池残留设置取得可写epoch。

Read绑定ResolveCommit/ResolveEvidence/ResolveRetention只读取上述精确全键+原版本/hash，Query用途/只读事务/零mutation；结果类型分别沿§8.4，行数/字节限以注入descriptor/Profile核定，不造默认。ApplyRetention依次核C-07决定→锁原Hold根→按原范围CAS→写decision/document/root_history/IM066引用改变→ResultCodec验证→commit。ListRoots沿B.6.4读取epoch历史，不将普通Query转GC许可。各写事务Min/MaxAffectedRows仅累计**本Binding StatementCatalog内各Mutation实际报告行数**，MaxCommands按本注册命令目录登记（不能沿Fake单行=1）；A1自己的epoch/route/技术receipt SQL由IM066按精确CAS行数另核，不能加到Owner命令计数或以隐含内层写替代实际命令行数，输入ObjectCount变化以已批准上限约束；不足/超额全事务回滚，真实命令目录/行数属于本模块注册实现验收，C-04只提供自身子mutation准确行数与合同版本。重试仍沿原identity/原描述、有限预算，仅已证明rollback且未消费source才可重试原事务；Unknown只观察，不重跑。

持久根恢复软件规则已可决定：新实例启动只读原claim/response/root_history及IM066原route/journal；已经Committed完整原response按原codec返回，不执行源/Finalize；Stage Unknown或Finalize Unknown保留Pending/Unknown/ReservedKey根。已确认对象SealedDurable、全部原身份可查、原写者已停止/fenced也**不让Query自动继续Finalize**。已接纳Stage/Finalize的Created=false只能观察原结果，本版不提供跨请求重新执行或交易续作；只读恢复返回InProgress/Unknown及原技术索引，宿主交原事实/保持Owner明确处置，不能生成新key绕过未知，也不能凭旧offset拼接新源。只有权威证明原请求未接纳、原writer不能迟到执行时，原CommitAsync重试仍先走正常Resolve/Reserve准入；未接纳证明是原Store路由/原结果与fencing共同结论，不是一次NotFound。IM066不支持Transaction/Stage ResumeMaintenance，不能调用它代替。source真实退出前不Dispose，Pending/Unknown/Committed根不被TTL/Close清除，原Task/流/lease/root有界Owner保持沿已接收规格；未知业务恢复处置内容归原Owner，此保守软件分支已冻结，不是留待实现者选恢复算法。

#### B.6.4 公开根resolver、有限全快照与恢复

公开类型如下，均在Runtime，仅服务可信Store/GC/备份组合，不进入操作员API，不扩展IM045通用Query。resolver不拥有注入Store或上游Coordinator，不执行GC/Preserve/Reconcile、事实或保持写。

```csharp
public sealed class EvidenceStoreSlot {
    public EvidenceStoreSlot(); // 同步无资源，仅受信任组合根持有
    public void Attach(S.IStorageDatabase store); // 仅一次、非null，不Dispose旧/新Store
}
public sealed record EvidenceRootResolverOptions(S.VersionRef Version,
    S.StorageOwnerRegistration Owner, S.VersionRef ReferenceCatalog,
    S.StorageBindingDescriptor ReadBinding, EvidenceDocumentLimits Documents,
    int MaxSnapshots, int MaxTrackedTasks, long MaxSnapshotBytes,
    int MaxTotalEntries, int MaxPages, TimeSpan OpenBudget, TimeSpan DrainBudget);
public sealed record EvidenceRootResolverDependencies(EvidenceStoreSlot StoreSlot,
    EvidenceEnvelopeCodec Codec, S.IStorageAuthority Authority, TimeProvider Clock);
public sealed class EvidenceRootReferenceResolver : S.IStorageOwnerReferenceResolver {
    public EvidenceRootReferenceResolver(EvidenceRootResolverDependencies dependencies,
        EvidenceRootResolverOptions options); // 零IO/Task/订阅
    public S.VersionRef Version { get; }
    public ValueTask<S.OwnerReferenceSnapshotResult> OpenAsync(
        S.OwnerReferenceSnapshotRequest request, CancellationToken ct);
    public ValueTask<CloseReport> CloseAsync(CloseOptions options, CancellationToken ct);
}
public sealed record EvidenceRootQueryPayload(S.VersionRef Schema,
    S.StorageOwnerRegistration Owner, S.VersionRef Catalog,
    S.StorageCoordinationToken Barrier, string? SnapshotId,
    long ExpectedReferenceEpoch, long NextSequence, int MaxEntries, int MaxBytes)
    : S.IOwnerStoragePayload;
```

Options所有VersionRef与注册Owner.ReferenceResolver/ReadBinding/ResultSchema/InputSchema精确匹配，Purpose=Query/Kind=Read，无缺省SQL/epoch；计数/字节/期限正有限，MaxTrackedTasks≥MaxSnapshots×2，Limits均≤Store/Profile；RootSnapshot的ProtocolFake库与本正式格式互不替换。SnapshotId固定`iev-roots-`+SHA256(ASCII `IM015-ROOT-SNAPSHOT-1`+Scope五ID+StoreId/Generation+OwnerKey+Catalog完整VersionRef+AuthorityEpoch+Fence+ReferenceEpoch，各原语沿B.5)，并保存完整预像比较；不只用epoch或数值更大认新authority。合法首次query SnapshotId=null/NextSequence=0，响应须等于该预像得到的id；后续query同id/ExpectedEpoch，从原FollowingSequence续，不查latest。RootQuery封套Schema=7，字段按上面主构造器左到右，所有Barrier字段按IM066原公共声明原序，token.Handle只定位此借用屏障，不是新权限。

1. 组合根先创建StoreSlot/resolver/package并登记到IM066 References；StoreFactory原任务成功返回后Attach(slot)再服务GC/备份。StoreSlot未Attach，Open返回Unavailable+null Snapshot，不返回空完整目录；工厂成功但Attach失败仍由原Host根持有Store并独立cleanup，不创建第二Runtime替代。resolver/Slot始终归Host；关闭固定为Host先停消费者及新维护接纳→关闭resolver接纳并观察原Open/session/task/snapshot全部排空→停本模块Runtime及上游Store/其backend→最后结束Host注册依赖生命周期。resolver不能反向Dispose共享Store；任何原借用/cleanup仍未知时继续强持同组Store/依赖/原Task，不因Dispose观察到期越过借用边界或换实例。
2. Open先在resolver自己的进程强根占MaxSnapshots/MaxTrackedTasks/MaxSnapshotBytes；root builder/原Store session Task/请求/依赖在**任何异步调用前**登记有界槽，ct取消或外WaitAsync不丢原Task。请求MaxEntries/Bytes与Options取更小值、同原OpenBudget单调截止；超额/正剩余不足拒绝零IO。所有后续页/授权/释放/解析均不能刷新budget，cleanup独立DrainBudget只观察/释放原Task。
3. 核Owner全字段/Scope/Store与Catalog登记、当前StoreAuthority对`evidence.roots.read`及原owner范围授权，失败不披露根；Barrier.Kind只允许上游已定义Gc/GcPlan/Backup/BackupCut，ReferenceCatalog/Stores/OwnerKeys/InstanceEpoch/AuthorityEpoch/fence/ReferenceEpoch及request范围完整匹配，token不能从产品请求传入。**上游协调调用者持有原有效lease到snapshot用完，负责真实物理guard/fence有效性**；resolver不能凭token字段自称此物理证明。注册root read在原协调边界检查当前reference_authority与token exact/保护域有效（只读，不续期/改fence），无法证明返回GcBlocked/CommitUnknown，不能将此检查退给客户或拿TTL当durable保护。
4. 以Store.OpenSessionAsync(Query)→ReadAsync(RegisteredReadRequest(context,ReadBinding.Version,rootPayload))读取根历史。CurrentContext来自request（预算扣实际耗时，Caller不换成高权限主体），不制造durable OperationIdentity。首次只读读取head/totals和第一页，历史谓词为from≤ExpectedEpoch且(to为null或ExpectedEpoch<to)；按RootId.ScopeId/Value Ordinal、RootVersion.Revision数值、ObjectKey完整序排序并分配连续0起Sequence。排序/全集由同一epoch root_history定义；**所有root写必须参加同Store参考epoch边界**，否则Incomplete。固定总数/字节在每页重复，且与完整canonical记录相符。记录变更保存历史版本到已绑定保留Profile窗口；窗口不足/历史删除/epoch失效仅ResultExpired/GcBlocked，不悄悄换新snapshot。
5. 每页OwnerReadResult.Schema/byte数/Refs先校验再DecodeRoots，Items≤page cap/MaxTotalEntries、总bytes≤MaxSnapshotBytes、page数≤MaxPages，序号/Following严格推进，不循环/重复/跳号；累计完整投影数/byte必须等于初始totals。Reference/ProtectedObject核精确ObjectRef，ReservedKey unresolved任何一项均Fault/Incomplete、不略项交空Snapshot。保守策略：只要存在无法表达的活动/Unknown reserved根，该scope GC/全闭包备份资格Blocked；普通保存/独立只读不被阻断。若后续上游公开保证足以证明reserved保护，可在原边界另修本规则，不能开发者自己忽略。
6. RootVersion.Digest按RootBody重算、Scope/ObjectKey/Bytes/hash/Format全字段核；同Object多个逻辑根保留多个OwnerReferenceEntry，Sequence仍连续，不按hash去重。输出EntityId=RootVersion.Id.Value、EntityVersion用S.VersionRef(Id=EntityId, Revision=checked int RootVersion.Revision, Hash=SHA256 RootBody)，超过Int32.MaxValue明示UnsupportedVersion，不溢出。该EntityVersion就是模块根版本，不冒充C-04修订。完整ObjectRef包含tenant/store/generation/domain；不能用仅ObjectId lookup。外部Reference解析失败，不得到完整GC/备份证明。
7. Open**先有限全物化**所有页并释放原session/reader，再返回S.IStorageOwnerReferenceSnapshot；不交半快照。快照public实现`EvidenceRootReferenceSnapshot`（仅resolver private/internal创建），实现原SnapshotId/ReferenceEpoch/ReadAsync(nextSequence,ct)/DisposeAsync，无新public ctor；read仅对本完整有界不可变数组按调用者原MaxEntries/Bytes切页、零Store IO。一次仅一page在途，nextSequence必须为0或上次唯一NextSequence，重读同sequence幂等同页；Complete=true只在末页、NextSequence=null，空完整目录首读Empty/Complete=true合法。最大page byte预算不能容一entry返回CapacityExceeded、不交空推进页；租借Coordinator token到期/ct失败返回对应Fault，不返回成功完整。每次交付前核当前Authority同owner范围；token字段不是实时有效性API，不声称仅凭字段已验证lease期限。上游协调调用者须先核其原lease.GetStatusAsync及物理guard有效再使用每页/执行GC或复制；本Snapshot不获取新lease/不延Open截止；期限覆盖由上游本次原协调lease保证，不能把完成全物化当永久GC授权。
8. 取消先赢则回收本次snapshot槽/session/原Task，实际清理结束才返回Cancelled/OCE；DrainBudget到期仍有原Task/资源则返回null Snapshot+CommitUnknown并由resolver强根保留，不能用取消完成判Released；成功先赢则交完整Snapshot给上游调用者，Dispose归还本槽。Close停止新Open、合作取消在途、按独立DrainBudget观察；未知保留原Task/Store借用，CloseReport=DrainUnknown，原业务Primary与Cleanup分开。Snapshot Dispose只退本module buffer/观察槽，不Dispose上游Coordinator lease；借用前者由上游自己释放，不能反转所有权。重新启动新resolver/Store only查询原不可变epoch/原route，不能清Unknown根或抢旧writer；完整snapshot未建成不能放行GC。Close不可凭session Release Task完成但Resources未知就称Released。

#### B.6.5 本轮反例、Golden与测点（仅文档验证）

下列仅为规范编码Golden，不是产品运行或真实存储证据。OWN-01的SnapshotId=`s`只验证codec结构，不是B.6.4屏障派生合法ID、不能当GC资格；OWN-02是hash预像，非完整RootPage，ReservedKey仍未解析且GC必须Blocked。

| Golden | 完整输入与长度 | 规范hex | SHA-256（64位小写hex） |
|---|---|---|---|
| OWN-01 | RootPage：SnapshotId=s，ReferenceEpoch/TotalEntries/TotalBytes/NextSequence=0，Entries/Issues显式Empty，FollowingSequence=null，Complete=true；60byte | `494d303135455631082f0000000100000073000000000000000000000000000000000000000000000000000000000000000000000000000100000000` | `4594752a3c749f080a592bd954a83ecbaee3200804302e8155637529fd4a7c43` |
| OWN-02 | RootBody：RootVersion.Id=s/r、Revision=1（不编码自身digest），RootId=s/r、Kind=ActiveWrite（2）、CommitIdentity=s/c、Reference/ProtectedObject=null、ReservedKey=(StoreId=x,Generation=1,Tenant=t,Domain=d,ObjectId=o)、ResolvedObject=null；Sequence不入hash；92byte | `494d3031352d524f4f542d424f44592d31010000007301000000720100000000000000010000007301000000720200000001010000007301000000630000010100000078010000000000000001000000740100000064010000006f00` | `c25fe8325fdbef45a7fb939690d3300897d9fd4caf164543fec71b73d945e0c6` |

本轮以内存原语编码/显式游标解码重新生成两条完整byte并计算hash；反例包括错magic/SchemaCode、长度±1/负值、截尾/加尾、非法null/bool/enum、改变Root.Key、分页Sequence变化不改变RootBody。全部按文档规则验证；未调用尚未实现的EvidenceEnvelopeCodec，不把此结果写成OWN-01～12产品suite通过。其它OWN case仍是后续实现断言，完整suite分母不可省略。

在已有Runtime.Tests范围追加待实施case，不创建文件/工程，不重跑已接收G1/ProtocolFake向量。`OWN-01`空RootPage与`OWN-02`未解析ActiveWrite RootBody规范byte向量见上表；两者附错Schema/尾部/长度/越界反例；`OWN-03`同输入 Source.Versions重排编码相同、父Order交换编码不同、业务Payload任一byte改变仅业务/输入域改变不能重算旧Fact身份；`OWN-04`Manifest→receipt依序生成再Decode，改本次父manifest digest/receipt hash/root hash必Corrupt，外部父版本不可省略；`OWN-05`注册same Kind两项/精确CLR type或Schema错、临时Codec版本替旧reader，Create零IO拒绝；`OWN-06`两独立Host沿§9.3分别用已注册EnvelopeCodec+业务validator合成夹具（SyntheticFact/Policy仅validator批准的测试域）执行同P1/P2，不用ProtocolFake codec冒充新持久格式；既有suite分母必须增加OWN-01～12，遗漏任何一个非零，不用基本Host0声称完成。

`OWN-07`root resolver未Attach→Unavailable，Attach后RootId两根指同Object→两条Entity，空目录→完整Empty；`OWN-08`第一页后并发root改变，原epoch历史仍同byte/total，epoch不保留/跨snapshot/缺页则Blocked，不能第二页最新值；`OWN-09`ReservedKey/未知ObjectRef/RootRevision超Int32/总byte或页数超限，零snapshot交付、GCBlocked；`OWN-10`root Open/Read/Release迟到与取消/cleanup错并存，有界Task/Store强持，Source及Store不在在途Dispose，ReleaseBarriers后真实归还而Unknown根仍存在；`OWN-11`Finalize原业务revision只在事务生成、写模块一半失败全部rollback，响应丢失原Query不补事实/行，普通恢复Query零写，原受管writer仅保存自身原任务真实结局、不重新执行未知交易；`OWN-12`Restart/readonly两独立消费者按旧Envelope格式读历史、未知格式Blocked，Close/TTL不删持久根，原GC/Backup屏障仍归调用者；无物理资格不报告GC或耐久通过。

Benchmark沿§13.1/13.2，不改统计口径：增加EnvelopeEncode/Decode（payload/数组/深度limit）、RootReserve→session→每页解析/hash/权限→全物化→session实际释放→Snapshot交付/最后Dispose，记录MaxSnapshots/TrackedTasks、完整缓冲+原Task/request/canonical/Metadata驻留bytes、第一/末页/并发epoch变化/ReservedKey失败/取消到真实排空。Root全物化的总metadata字节而非图像字节进入MaxSnapshotBytes，0root仍有header内存计账，超限先拒绝；SQL数据库snapshot/业务mutation/介质I/O耗时只有真实后端运行才可报告。目标沿Consumer Profile，未采纳NotEvaluated，未运行不声明数值达标。本节公开Factory、Options和全部失败/恢复规则均可在原唯一工程直接实现，不需程序员选择codec/root算法。


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

## 附录 A：模块核心 API Contract v0.2（逐切片准入）

本节定义本独立模块的分层核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不自动代表准入通过，当前G1-Core文档规格接收状态见§17.1。实现者不得另造第二套核心 DTO、状态机或错误语义。

- `Module API Contract v0.2` 的 Gate-1 只覆盖无产品事实写入的 Pure Core 和纯端口描述。当前 Gate-1 不授权文件/内存持久化模拟实现。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。Gate-2/3 的提交、持久化和定向读取接口是后续独立门，不因存在于本附录而获得 Gate-1 准入。
- `CommitAsync` 是 Gate-2 唯一对宿主公开的事实提交 API，不属于 Gate-1 `IInspectionEvidenceCore`。Stage/Seal/Publish 仅是该命令的内部编排步骤，不单独开放为提交入口。任何对象存储、数据库、回执、Manifest、租约、保持或产品 Owner 映射即使通过 adapter 注入，仍属于后续事实/持久化门，必须单独满足准入条件。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- 可选视觉适配器经 `ImageLibDotNet.cv2` 使用 HALCON 26.05 operator set；语义/格式查本地26.05手册，不逐项确认“是否包含算子”、不另接 HOperatorSet/halcondotnet.dll、不查看 AsunImage 内部。仅 C# 重载/封送有歧义时查公共签名或在消费项目编译；缺口只阻断受影响预览，不阻断字节 Core。
- 本附录的存在不自动授权实现，当前G1-Core文档规格已接收，状态以§17.1为准，其余切片仍按对应门接收。具体 Core 切片只有在本指导明确实现范围、命名空间、唯一代码/测试工程、允许/禁止路径，并逐项满足 DEV-GOV-010 §3.1 六项条件且由主任务接收后，才可标记为 `ModuleCoreImplementationReady`；否则保持 `PreparationIncomplete`。
