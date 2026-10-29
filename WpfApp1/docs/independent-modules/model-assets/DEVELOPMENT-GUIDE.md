# 模型资产版本与解析模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`PureCoreContractOnly`

- 模块 ID：`IM-014`；模块键：`model-assets`；对应来源：`PKG-033`
- 版本：`0.3.1-prep`；状态：`DesignReview / Prep`；日期：2026-10-11
- 规划消费者：2D 匹配、OCR、AI 推理与工程工具；可选只读资产工作区
- 首片准入：`PureCoreContractOnly / ModuleCoreImplementationReady`（仅规格准备，2026-10-10 主控逐项接收）；持久化、格式读取、用途证据和副作用服务均不进入首片。
- 本文是本目录唯一实施指导；上述工程绑定不是本轮创建或实现授权。
- 兼容平台基线：C# / .NET 10；视觉读取由格式生产者经 `ImageLibDotNet` 公共能力适配；目标 HALCON 为 26.05。

本文可以脱离 PCB 检测平台作为模型资产 Core 契约的接入基线。首片只定义无 I/O、无持久化、无 native、无事件订阅的不可变类型、结构校验、依赖图校验和内容引用/摘要投影。完整模块的 Service、Store 边界、租约、格式读回、用途撤回和导出执行链见 §5A–16，独立工程和逐切片接收见 §18；本轮设计合同不是平台集成批准。当前不得标记为已实现、功能验证通过或生产通过。

## 1. 阅读顺序与权威

1. 本指导定义本模块实施责任和附录 A 的 Pure Core v0.2 设计合同语义。
2. [独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)定义模块准入、依赖方向与第二消费者原则。
3. [PKG-033](../../shared-modules/packages/PKG-033_ModelAssets.md)是历史迁移来源；其新资产 JCS/旧协议保留决策在本页 §4/9 落实。当前独立模块实施权威是本页；PKG-033 已由主控收口为应用接入映射，不形成两份活动正文。
4. 平台字段、持久状态和业务写入权限以获批 Contract/Schema 与原 Owner 为准；首片不定义持久状态或业务写入。集成映射的候选语义见 [CONTRACT-CANDIDATES.md](../../13-contract-candidates/CONTRACT-CANDIDATES.md#model-assets-contract-semantics)。
5. 字节耐久、提交回执和 GC 协调依赖 [PKG-041](../../shared-modules/packages/PKG-041_Storage.md)；配置快照使用 [PKG-002](../../shared-modules/packages/PKG-002_Configuration.md) 已批准的公共边界。
6. Vision / HALCON 边界见 [DEV-VIS-020](../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision%20Contract与AsunImage边界开发指导.md)。算法生产和具体运行见022、024、015、026、052、053；参考库组合和程序采用仍分别归034、035。
7. UI 如获准建设，遵循 [UI-PCS-002](../../shared-modules/guidance/14-page-contracts/UI-PCS-002_Vision_Workspace.md#model-assets-workbench-ui) 与宿主 UI 规则；UI 不增加核心能力或改变事实。

若这些来源互相冲突，暂停受影响的接口/实现切片，由原 Owner 修订唯一权威后再继续。不能把本页的示例类型直接生成生产 DTO。

## 首片 Core implementation binding

- Core 唯一工程：`src/Modules/model-assets/Asun.Modules.ModelAssets.Core/Asun.Modules.ModelAssets.Core.csproj`；唯一测试工程：`tests/Modules/model-assets/Asun.Modules.ModelAssets.Core.Tests/Asun.Modules.ModelAssets.Core.Tests.csproj`；namespace：`Asun.Modules.ModelAssets`。两项目目前未创建。
- 获准首片仅可新增以上两个工程及其必要契约测试；明确禁止修改产品 Shell、其他模块、AsunImage 内部、客户项目和任何领域数据库表。首片只实现纯内存类型/校验/摘要投影，不读取文件、数据库、网络、HALCON、AsunImage 或 native。存储、格式适配、WPF 投影和真实模型验证属于后续独立切片。
- PureCore 当前准入状态：`ModuleCoreImplementationReady`（仅规格准备）。主控已按 DEV-GOV-010 §3.1 逐项接收 §2/3/4/5/9/11/13/14/16/17/18 与附录 A；四个同步静态纯值入口，无 I/O/native/生命周期，取消、超时和关闭不适用。Service S1 的软件协议、模拟 port、ToolHost 与有限 Root 六项文档规格已由主控于 2026-10-11 接收为 `ModuleCoreImplementationReady`（仅规格准备）。U1 公开装配/Owner 恢复及 SD Stage/Query/Read/Hold/Release 限定桥指导内容已接收；真实领域绑定、Store/Authority/Sink、安全物化、HALCON/旧格式、实际 WPF 与生产切片仍为 `PreparationIncomplete` 或对应后续门。本次接收不表示实现、编译、运行或验收通过。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ModelAssets.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已确认"首片只实现纯内存类型/校验/摘要投影，不读取 HALCON、AsunImage 或 native"。

**Blazor/Web**：模型版本目录通过 gRPC/REST 查询，浏览器只展示资产元数据（版本号/hash/状态）；模型二进制通过 HTTP Range 分片下载。模型发布/撤回走已授权维护接口，不经浏览器。

**AI 推理集成**：`ai-inference` 通过本模块注册的 `ModelAssetRef`（精确版本 hash）加载已封存模型，不允许取 `latest`（`ai-inference` §1 已明确"不得选择 latest 模型"）。本模块的 `ModelCard` 携带训练数据集指纹、指标和已知失效模式。

**HALCON 视觉路线**：本模块存储 HALCON 形状模型（`*.shm`）等资产，但不直接执行 HALCON 推理；HALCON 备选 CI 在消费资产的视觉模块中执行。

## 2. 职责与禁止边界

### 2.1 模块总体职责

以下是 `model-assets` 的长期模块范围，不是首片实现范围。首片只能执行 §2.2 和附录 A 的 Pure Core；本节列出的 Store、租约、真实读回、用途证据和异步生命周期能力，必须按 §2.3 分成后续切片并逐片重新准入。

- 接收模型资产清单、来源和精确依赖引用；以受限流和有界验证计算真实长度及内容摘要。
- 在原存储 Owner 提供的接口上协调不可变内容暂存、封存、幂等回执和持久保持；重复请求必须按原操作摘要恢复。
- 维护并解析精确的命名域、资产 ID、不可变 revision 和技术摘要；可变名称/标签/alias 只能用于查找，在选择边界冻结为精确引用。
- 对给定用途分别求运行闭包、重建来源闭包或验证证据闭包；报告闭包未完成、缺项、冲突、环和预算截断。
- 为字节读取及受控物化目录提供有生命周期的只读内容租约；与 PKG-041 协调，避免 GC 和读取竞态。
- 记录版本、格式、生产者修订、文件角色、长度/hash、精确依赖和已知的影响解释/装载语义。
- 将格式专用真实读取委托给登记的生产者验证/读取适配器。验证报告固定引用已封存核心，不回写核心制造摘要环。

### 2.2 首片 Pure Core 职责

首片只拥有以下纯函数事实：

- 不可变 `AssetIdentity`、`AssetRef`、`Digest`、文件角色/逻辑路径、依赖引用、参数语义快照和有界资源描述的构造与校验。
- 对调用方提供的摘要声明和已构造的内存引用执行有限、确定性的长度/摘要/角色/路径/依赖图校验；首片不读取原始字节、不打开路径、不读取流、不创建目录、不写 Store。
- 生成 `model-core-jcs-v1` 的类型化技术核心投影和摘要候选；旧规则只保留显式版本标识，不在首片自动迁移或重写旧身份。
- 返回不可变 `CoreValidationResult`、含可达节点/拓扑/旧引用状态的 `DependencyGraphResult` 和可明确失败的 `CoreProjectionResult`；错误统一嵌入 `CoreValidationResult`。结果不携带文件句柄、native对象、租约、事件订阅或持久回执。

首片输入只包含不可变清单、声明摘要、内容引用和依赖节点快照，不接收原始 byte span。流、文件路径、URI、存储连接、取消 token、deadline 和异步 worker 不属于首片入口。

### 2.3 完整模块切片与准入分离

本轮对以下全部能力给出执行/恢复规格和模块端口设计；它们不被首片排除后就视为完成。各切片工程和六项准入见 §18，真实上游映射、格式证据、WPF 和宿主接收仍分别关门：

1. `Storage/Seal`：staging、不可变封存、CAS、幂等 `OperationId`、Unknown 查询、GC/保持和恢复。
2. `ContentLease/Materialization`：流/目录物化、只读租约、并发等待者、取消/超时和真实排空。
3. `FormatAdapter/Readback`：HALCON 26.05、`ImageLibDotNet`、Shape/NCC/Deformable/Variation/Deep OCR/DL reader、参数读回和 challenge。
4. `UsageEvidence/Adoption`：用途授权、资格、程序采用、撤回和新鲜度；不由 Core 产生。
5. `Export/Import`：完整闭包导出、空目录导入、备份/迁移/回退及任何外部副作用。
6. `AsyncService/Events/UI`：异步调度、事件订阅/重放/退订、排空、可选 UI 和宿主集成。

后续切片可以消费首片纯类型和校验结果，但不得把后续能力偷偷实现到 Core 或扩展 Core 接口。

### 2.4 模块不得负责

- 不训练、微调、从native生成/导出模型或执行生产推理；技术资产包导出见§5A。Core/Service不设置推理设备、不缓存/释放native；格式adapter只在本次验证中按生产者运行快照设置/查询并释放自己的HALCON/GPU资源。
- 不定义或解释目标、ROI、板件/工单身份、制程参数或产品流程；不包含 PCB、SPI、AOI、点胶、涂覆等工艺判定。
- 不批准模型质量、具体用途、AI 阶段、程序采用/发布、激活、设备动作、返修或最终质量放行。
- 不把文件可读、摘要匹配、语法有效、验证报告存在、用途获准、程序采用和某次运行实际装载合并成一个 `Valid` / `Ready` 标志。
- 不拥有业务权限策略、私有数据库、训练数据权限或外部注册服务。宿主将当前授权证据/明确用途交入登记端口；拒绝授权仍由授权 Owner 作出。
- 不通过反射或服务定位器动态发现调用者；不跟随 `latest`、可变 URI、外部 alias 或机器缓存补齐运行依赖。
- 不把文件扩展名、参数 JSON 或通用 ZIP 检查冒充模型格式/语义验证；不因 hash 相同合并角色、身份、来源、用途或资格。

模块成功只表示所请求的资产操作在返回范围内完成。它不代表模型可用于任何生产用途。

## 3. 独立交付与依赖方向

```text
调用方 / 后续 Store、格式和用途切片
        │ 不可变清单、引用和参数语义
        ▼
首片 ModelAssets Pure Core
        ├── 类型/范围/路径/角色校验
        ├── 有界依赖图校验
        └── canonical 技术核心投影（纯内存）
        ⋯ 后续独立切片：Store、Lease、FormatAdapter、Evidence、Async/UI
```

首片不得依赖匹配、OCR、AI、产品 Shell、ViewModel、页面、数据库、HALCON 或任何适配器实现。后续切片依赖首片公开类型；首片不反向依赖后续端口。

首片可由命令行、服务、回放或测试宿主直接调用；不要求窗口初始化。格式未装配、存储不可用和用途未知均不在首片发生，后续切片必须通过显式端口处理。

## 4. Pure Core 数据合同与校验边界

本轮修订为模块设计合同 `v0.2`，替代本页旧 v0.1 的不完整形状；它不更改已封存资产、平台 Schema 或其他模块接口，也不代表实现获准。精确公开类型唯一见附录 A，本节定义其行为。Core 只接受不可变内存快照；不读原始文件/流，不执行格式查询，不登记持久事实。

### 4.1 身份、角色、路径和输入上限

- `AssetIdentity` 的命名域/ID/revision 均为不透明、非空、无控制字符的字符串；按 ordinal 精确相等，无大小写折叠、默认 revision 或 `latest` 特例。UTF-8 长度分别受 `CoreValidationProfile.MaxStringBytes` 限制。
- `Digest` 同时包含规则 ID、算法 ID、摘要原字节。新核心为 `model-core-jcs-v1`/`sha256`/32 byte；文件为 `raw-file-sha256-v1`/`sha256`/32 byte。旧规则可作为有界不透明引用保存，但没有登记旧验证器就不能验证或运行；不得用新投影判旧资产损坏。新旧摘要不裸拼接或相互比较。
- 文件唯一键是 `(Role, LogicalPath)`，**不是 Role 单字段**。同角色允许多分片；同物理文件可被多个角色引用，但其长度和文件摘要必须一致。主模型入口 `FormatDescriptor.Entrypoint` 是载入根内的 TargetPath，必须恰好对应一项 root Layout 映射，其 SourcePath/Role 定位一项 Required 文件。零文件/空入口拒绝；零字节主模型拒绝；可选空文件是否有意义由生产者格式描述决定，不得用空文件补必需项。
- `LogicalPath` 是逻辑字符串，并非机器路径。固定 `/` 分隔；拒绝空段、`.`、`..`、反斜杠、根路径/盘符/UNC、冒号/ADS、NUL/控制字符、Windows 禁用字符 `<>:"|?*`、段末空格/句点和设备名 CON/PRN/AUX/NUL/COM1–9/LPT1–9（含扩展名）。拒绝孤立 surrogate。不替换字符、不自动改名。
- 路径碰撞键为 NFC 检查副本加 `OrdinalIgnoreCase`；原字符串仍进入摘要，不做隐式归一化。不同原路径碰撞则拒绝，相同路径不同角色按上一条处理。每个文件/TargetPath 不能同时是另一文件的目录前缀（a 与 a/b 拒绝，按同碰撞键检查），角色文本非空、无控制字符、受MaxStringBytes，无隐式大小写折叠。**字符串校验不能识别符号链接、重解析点或 TOCTOU**，这些只由实际物化端口验证，Core 绝不宣称已证明文件系统安全。
- 所有 Profile 上限必填且正，长度/计数为 byte/项，图深度按边数；0 表示根深度，仅 `MaxDepth` 可为 0。Layout条目数也受MaxFiles约束。Profile 的 ID/revision 与限额用于校验和诊断，不进入技术内容摘要。限制在复制、分配和 checked 加法前核对；输入超限返回错误，不靠调用方预检或 OOM。输入仅接受已构造的不可变记录/ImmutableArray，不接 IEnumerable/流；公开记录构造器只赋值，不分配递归副本。四入口先迭代预检输入预算，再有界深复制为本次内部快照；输出同样独立复制。调用方构造自身输入的内存归调用方，本模块只保证入口后的有限占用。`ImmutableArray.IsDefault` 是缺失，Empty 是合法空集合。

入口预算顺序固定：先核 Profile→外层 counts→显式栈遍历所有字符串/值/文件/图节点并 checked 累加→复制→语义/图/投影。`MaxInputBytes` 是逻辑输入计费：每次出现字符串的严格 UTF-8 byte 数、每摘要 Bytes.Length、每数值/enum/bool 标量 8 byte、每集合元素槽 8 byte 相加；共享引用也按出现次数计，不含 CLR header，不冒充 RSS。MaxJsonNodes/Depth 对本次输入所有 Semantics/Constraints 合计；graph 候选节点（含不可达）总计费，节点/边计数含 root。循环 AST 或身份回环在复制前被检出，不无限遍历。CLR 额外开销由 §14 峰值测量/Service MaxResidentBytes 分别约束。Profile 本身非法时固定返回一项 MA-LIMIT-001，不使用其非法 MaxErrors 分配；空 manifest 为 MA-REQ-001。错误阶段顺序固定为 Profile→Envelope→Manifest→References→Graph→Canonical；同阶段按字段 ordinal 路径、码排序，截断后仍 Invalid。

### 4.2 声明性参数与技术投影

`AssetManifest` 必须包括 `Format`、`Producer`、`Semantics`、`Files`、`Dependencies`。旧形状只含身份/文件/依赖，遗漏输入通道、词表、预处理顺序和参数，已经废止。`Semantics` 固定 schema ID/revision/digest 与生产者声明字段；Core 核结构、类型、单位、范围表示和可解释状态，不能自行验证算法阈值或推断缺少的模型族字段。

`SemanticField` 的完整元组为 ID、Kind、Unit、Value、Status、SourceId/Revision、Stage、Constraints。Kind 闭集为 `Boolean/Int64/Binary64/Decimal/String/Enum/Sequence/Object`；Status 为 `Explicit/AutoResolved/NotCollected/Unsupported/QueryFailed/Cancelled`；Stage 为 `Build/Serialized/RuntimeRequirement`。有值状态只允许 Explicit/AutoResolved，其他状态 Value 必须是显式 null 并保留来源与原因于 Constraints。AutoResolved 是生产者的声明，不是 Core 新查询的事实。定义无默认、生产者默认或 Profile 默认的来源与实际值分开，不以默认冒充观察结果。

- Int64 在投影中统一为规范十进制字符串，范围为 Int64；Decimal 为无 `+`、指数、前导零、尾随小数零或 `-0` 的十进制字符串，零写 `0`，不能经 double。Binary64 为有限 double，输入负零在语义层拒绝；其 JCS 数字输出仍遵循 RFC（通用 JCS 的 -0 输出 0，两层不同）。
- 角度声明 `rad`/`deg`；物理长度声明单位；像素/行列/张量须在生产者 schema 中声明坐标约定、dtype/layout/shape/channel。Core 不转换单位/坐标。Range 用 lower/upper 和 inclusive 标志表达，有上/下界时类型必须同 Kind；无边界用显式 null，不用 Infinity。
- 字段集合按 ID 的 Unicode scalar value 序排序、ID 重复拒绝；Sequence 保序。Constraints 中的对象按 JCS 属性排序、数组始终保序；生产者须先把具有集合语义的数组按其 schema 元组规范化。单位Unit必须显式null或生产者schema的限长token，不允许空字符串，数值/boolean无量纲用null；未知 Kind/Stage/Status 拒绝；Core 不检查生产者 schema 内容，只返回声明结构有效；schema 是否完整/required字段是否齐全由生产者adapter核，缺schema证据不得称语义/用途已验证。
- 影响模型解释/装载的冻结要求，包括必要 RuntimeRequirement，进入技术投影；某次实际设备/精度/batch 配置及 challenge 引用以 RuntimeSnapshot 完整投影绑定 RequestDigest；读回 Observed 只属于报告，不回写请求。声明要求与实际结果不能互相覆盖。训练数据、父模型/生成方式可通过 RebuildSource 精确边声明；缺训练来源可以保存为历史技术资产，但不能报告可重训。

技术投影顶层字段闭集：`rule`, `format`, `producer`, `files`, `dependencies`, `semantics`。业务 Identity 与校验 Profile **在内容摘要外**，由存储 CAS 不可变绑定到内容摘要；相同技术内容可同摘要而不同身份，但不得合并用途/来源/采用。该决定仅适用于尚无实物的新模型资产；旧格式若把身份纳入原预像仍守原协议。格式子字段为 `family/id/revision/entrypoint/layout`；生产者为 `id/revision`；schema 为 `id/revision/digest/fields`。文件字段为 `role/path/required/lengthBytes/digest`；依赖为 `purpose/role/target`，target 包括 `namespace/id/revision/digest`；digest 对象为 `rule/algorithm/hex`，hex 为小写偶数十六进制。文件 lengthBytes 始终为十进制字符串。语义字段投影按前述完整元组，null 不省略；拒绝其他顶层字段，不能默默忽略后算新摘要。

JSON映射大小写固定：purpose/Kind/Status/Stage输出与本页C#枚举成员完全相同的字符串，不用数字enum或culture lower-case；semantics.fields条目固定键 `id/kind/unit/value/status/sourceId/sourceRevision/stage/constraints`。所有显式可空键写null，其他必需字段缺失拒绝。新规则的family/format/schema/producer字符串逐ordinal保留，未登记的格式声明仅表示技术描述，不获得格式支持结论。

Constraints闭集键为 `lower/upper/lowerInclusive/upperInclusive/defaultPolicy/defaultValue/defaultSourceId/defaultSourceRevision/elementKind/reason`，全部键显式存在；不适用值为null，inclusive为bool（无对应bound时false）。defaultPolicy闭集NoDefault/ProducerDeclared/ProfileDeclared，NoDefault的value/source均null；有值状态的reason=null，非有值状态reason必填；其他policy必须有同Kind值和来源ID/revision。sequence的elementKind为单一SemanticKind字符串，非sequence为null；非有值状态reason为非空限长文本。Int64/Decimal边界用同规范字符串，Binary64边界有限且非负零。sequence元素递归Object/Sequence结构由schema声明且受同一JSON预算，CanonicalNull不作sequence元素的Kind默认值；其他Constraints字段拒绝；算法专有复合约束放生产者具名Object语义字段，原样保序/进入digest，不解释执行。仅 Int64/Binary64/Decimal 允许 lower/upper；其他 Kind 的 bound=null、inclusive=false。数值 Value/default 必须落在已声明区间内。lower>upper、两端相等且任一端开拒绝；Int64 开端点按 checked ±1 核有效范围，Binary64 用 Math.BitIncrement/BitDecrement 核有限可达值。Decimal 指有界规范有限十进制字符串，不限定 System.Decimal 精度；按符号/整数长度/补齐小数位做精确比较，不经 double，任意不同有限十进制端点之间存在有限十进制数。字段词法/输出长度仍受 Profile 限制。

载入布局 `Format.Layout` 必填有界数组，按TargetPath的scalar顺序投影；entry键固定 `sourceAsset/role/sourcePath/targetPath`，sourceAsset=null表示root（不嵌自身digest，避免摘要环），否则是所选Runtime闭包的精确Ref。SourcePath和TargetPath均按§4.1路径规则；每个TargetPath唯一且无NFC/大小写碰撞。root入口Entrypoint按TargetPath定位，恰好一项指向root必需模型文件；所有 root.Required 文件和可达Runtime节点已声明的运行必需文件均有映射；optional只在Layout显式列出时物化，不能靠目录余项，Role/SourcePath实际属于对应节点，外部ref必须已列入Runtime边闭包，不能补目录余项。源同一文件可映射多个目标，但相同目标不可借“同hash”合并不同来源。Core清单验证root映射，Runtime Graph验证每个可达节点相对于该节点的跨节点映射；RebuildSource/ValidationEvidence 图不因未请求 Runtime 节点而报缺项，但不得用于格式装载。FormatReadback再次核已验证完整图再物化。读取外部weights的相对location必须由生产者给出此固定map；缺map/冲突拒绝而不是由程序员改文件名。该map进入technical digest。

新报告、资格、用途、程序采用、UI 标签、物理缓存路径、租约、更新时间、自身摘要均不进入核心。任何影响上述投影的文件/参数/依赖/schema 变化必须产生新 revision；仅 UI 标签或校验预算变化不改变技术摘要。

### 4.3 有界依赖图和确定性错误

旧 `ValidateDependencyGraph(manifest, limits)` 没有输入子节点，不能检查多跳闭包；修订为附录 A 的 `DependencyGraphInput`，调用方显式提供 root manifest 与所有候选节点，Core 不解析 Store。

1. 校验每个节点的精确 Ref/Manifest 身份一致、新核心摘要可复算且匹配；旧节点仅接受生产者能从原metadata无损提供的声明结构，结果列 `UnverifiedLegacyRefs`，不得称完整性通过；不能映射格式/语义字段时Core返回MA-CANON-001且Service报告Unsupported并保留原旧资产，不用默认值伪造新Manifest，旧verifier走原预像端口。节点唯一键为 Identity，重复快照拒绝，即使内容相同；同 Identity 不同 digest 冲突；Nodes 中出现 root.Identity 也属重复快照。DeclaredRootRef=null 时按新投影计算 root Ref；非 null 时先核 Identity，按新规则复算匹配或将已声明旧 root 列入 UnverifiedLegacyRefs。root 不靠自身依赖或 Layout 自引用定位。
2. 选择 `Runtime/RebuildSource/ValidationEvidence` 中请求的一类，沿同类边求可达图；其他类边保留于清单摘要但不跟随。边唯一键 `(purpose,role,target.Identity)`，完全重复也拒绝；同目标不同角色保留。缺任何可达目标拒绝；不得按 alias/缓存补齐。未可达节点不影响所选闭包语义，但输入计数/内存总量仍受限。
3. 按稳定边元组顺序做**显式栈**白/灰/黑 DFS，灰回边报 cycle 路径，黑节点共享不重复读。根/不同节点逻辑边全部计数。再按拓扑序计算从 root 到每节点的最长深度；不能因 diamond 的黑节点曾走短路径就漏检长路径深度。
4. 节点/边/深度/可达节点文件声明总 byte 全部有界；声明 byte 按节点文件条目计，不按 blob 去重，物理预算另算。任一超限整体 Invalid，不能返回截断闭包 Complete。Valid 图结果包含确定的可达 Ref、边和叶→根拓扑序，以及明确的未验证旧引用。
5. 错误只用附录 A.2 闭集，按阶段→字段路径→错误码稳定排序，最多 `MaxErrors`；额外错误设置 `ErrorsTruncated=true`，仍 Invalid。Core 无 timestamp/随机 DiagnosticId，诊断上下文只含精确身份、字段/依赖路径、预算项、声明与预期值；本地化由宿主处理。

## 5. Core 四入口、失败投影和最小 Host

公开签名与 DTO 只在附录 A 定义，不复制第二份。四入口全部纯内存、同步、可重入；未知规则、无效清单、引用冲突及投影超限都返回类型化失败。`CoreProjectionResult` 失败时 CanonicalBytes 为 Empty、Digest 为 null，不能只返回成功字段或抛异常字符串迫使调用方猜测。

固定顺序：ValidateManifest → ValidateContentReferences → ValidateDependencyGraph（需要所选闭包时）→ ProjectCanonicalCore。投影入口自身重做必需校验，不接受“调用方已校验”标记；校验 Profile 是显式参数。重复调用输入、文化和机器无关，结果相等；公开输入/输出数组在入口预算核对后有界防御复制，不暴露 backing buffer。仅语言展示受文化影响，摘要不变。

以下是**语义调用例**，Fixture 是测试数据构造器而非产品 API：

```csharp
var manifest = Fixture.NewNccManifest();  // 格式/语义/files/dependencies 全部显式
var profile = Fixture.CoreProfile();
var references = Fixture.DeclaredContentReferences(manifest);
var validated = ModelAssetCore.ValidateManifest(manifest, profile);
if (!validated.IsValid) return validated;
var paired = ModelAssetCore.ValidateContentReferences(manifest, references, profile);
if (!paired.IsValid) return paired;
var graph = ModelAssetCore.ValidateDependencyGraph(
    new DependencyGraphInput(manifest, Fixture.Nodes(), DependencyPurpose.Runtime, null), profile);
if (!graph.Validation.IsValid) return graph.Validation;
var projection = ModelAssetCore.ProjectCanonicalCore(manifest, references, profile);
// 只有 projection.Validation.IsValid 时读取 Digest；它还不是存储或用途资格。
```

无依赖 fixture：主入口 `model.ncm`，文件角色 `Model`，正长度与 32-byte 文件声明摘要，format/producer/schema 都为具名 revision，Format.Layout显式声明root Model/model.ncm→model.ncm，dependency 为 Empty；References 恰好匹配。节点为空时 Runtime 图只含 root。大规模和异常输入具体断言见 §11/13；这类合成 fixture 不证明 HALCON 文件可读。两个规划真实消费者是匹配工程工具与 OCR 工具，分别提供 NCC 和字符表/通道/预处理的声明清单；两个测试宿主不能代替真实消费者，但可先验证同一公开合同的无产品依赖性。

## 5A. 完整模块无 UI Service 设计合同 v0.3

这是完整模块的执行规格，不属于 Pure Core。模块自有 API/状态/Owner 在本页决定；映射到 storage-database、资格/授权和产品 Schema 的绑定仍是外部集成门，不能把下列本地端口当作上游已批准接口。当前没有产品实现；实现者不得从旧伪代码临时选另一接口或改变业务放行边界。

### 5A.1 公开服务和请求/结果字段

命名空间 `Asun.Modules.ModelAssets.Service`；Service 只依赖 Core、BCL 和显式端口，不引用平台私表、产品类型、WPF 或 HALCON。公开声明规格如下，所有异步操作预算与查询/释放身份见下表，不省略 token 参数；Token 不进入持久化 DTO。OperationCancelRequest/Query仅本实例Scope/Principal已装配权限，ExpectedRequestDigest不同MA-IDEM；首次CancelRequestId记录在原operation，重复观察同取消请求、不同CancelRequestId返回原取消观察而不再执行。取消等待不取消执行，RequestCancel才发worker停止请求；总budget到期同样合作停止、真实退出后才Cancelled/TimedOut，commit发出未确认仍Unknown。

```csharp
public interface IModelAssetService : IAsyncDisposable
{
    ModelAssetsSessionInfo SessionInfo { get; }
    ValueTask<ServiceResult<SealReceipt>> ImportAndSealAsync(AssetImportRequest request,
        ImmutableArray<ContentInput> inputs, CancellationToken cancellationToken);
    ValueTask<ServiceResult<SealReceipt>> RestoreLegacyAsync(LegacyRestoreRequest request,
        ImmutableArray<ContentInput> inputs, CancellationToken cancellationToken);
    ValueTask<ServiceResult<ResolvedClosure>> ResolveExactAsync(AssetResolveRequest request,
        CancellationToken cancellationToken);
    ValueTask<ServiceResult<IAssetContentLease>> AcquireContentLeaseAsync(ContentLeaseRequest request,
        CancellationToken cancellationToken);
    ValueTask<ServiceResult<ReadbackReport>> VerifyFormatAsync(ReadbackRequest request,
        CancellationToken cancellationToken);
    ValueTask<ServiceResult<ExportReceipt>> ExportClosureAsync(ExportRequest request,
        CancellationToken cancellationToken);
    ValueTask<OperationObservation> RequestCancelAsync(OperationCancelRequest request,
        CancellationToken waitToken);
    ValueTask<OperationObservation> QueryOperationAsync(OperationQuery request,
        CancellationToken cancellationToken);
    ValueTask<DrainObservation> DrainAsync(DrainRequest request, CancellationToken cancellationToken);
    ValueTask<ResourceObservation> QueryResourceAsync(ResourceQuery request,
        CancellationToken cancellationToken);
    ValueTask<ServiceSnapshotResult> QuerySnapshotAsync(ServiceSnapshotRequest request,
        CancellationToken cancellationToken);
    IAssetEventSubscription Subscribe(AssetEventCursor cursor, Action<AssetEvent> callback);
}
public interface IAssetContentLease : IAsyncDisposable
{
    string LeaseId { get; }
    ResolvedClosure Closure { get; }
    ValueTask<ServiceResult<ContentReadLease>> OpenFileAsync(ContentOpenRequest request,
        CancellationToken cancellationToken);
    ValueTask<ResourceObservation> ReleaseAsync(ResourceReleaseRequest request,
        CancellationToken cancellationToken);
}
public interface IAssetEventSubscription : IDisposable
{
    SubscriptionStatus Status { get; }
    long LastDeliveredSequence { get; }
}
```

下表解释上述公开字段；DTO声明唯一在附录B，DTO 为 sealed immutable record（CanonicalValue为封闭不可变class层次），集合 ImmutableArray，时间单位/缺省处理不能由实现者自行决定：

| 类型 | 必需字段/闭集 |
|---|---|
| `OperationBudget` | TotalTimeout:TimeSpan（正且有限，含排队/读取/校验/提交）；WaitTimeout:TimeSpan（正，控制调用方等待）；Limits:ServiceLimits；各值从具名 Profile 取得，不在例子中默认两分钟 |
| `OperationContext` | Scope:ModelAssetsScope、OperationId:string、RequestDigest:Digest、RequestEpoch:long>=0、ProfileId/Revision:string、Budget:OperationBudget；所有操作 ID 含宿主 owner 命名域，重试保持原 ID/摘要 |
| `ServiceLimits` | MaxFiles/Nodes/Edges/Depth、MaxSourceBytes/MaterializedBytes/CanonicalBytes、MaxResidentBytes、MaxConcurrentWorkers/Waiters/QueuedOperations/OpenLeases/Events、CoreProfile；byte/项单位，上限先预约，缺失拒绝 |
| `AssetImportRequest` | Context、Manifest、ExpectedAbsent:bool（v0.3 固定 true，不存在覆盖更新）、SourceSnapshot:SemanticSnapshot；Source 不改变技术语义时只作为注册来源，否则须进入 Manifest.Semantics/RebuildSource |
| `LegacyRestoreRequest` | Context、Legacy:LegacyAssetDescriptor、ExpectedAbsent（固定 true）；旧 verifier 核原 metadata/文件/Ref 后按原绑定 CAS 恢复，不创建新 JCS identity |
| `ContentInput` | Role、LogicalPath、DeclaredLengthBytes、DeclaredFileDigest、Source:IAssetContentSource；这是进程内装配参数而非持久DTO，Source 仅提供借用只读流，宿主显式装配；内容正文/stream/凭证不进入请求摘要或持久 DTO |
| `AssetResolveRequest` | Context、ExactRef、Purpose:DependencyPurpose、Access:AssetAccessRequest；不允许 alias/Latest 请求 |
| `AssetAccessRequest` | PrincipalRef、UsagePurpose:string、RequiredAction（ReadHistory/ReadForUse/Export）、ExpectedAuthorityRevision:string?；授权凭证由端口持有，不写 Manifest/log |
| `ResolvedClosure` | RootRef、Purpose、StoreViewId/Revision、GraphRefs/Edges、Files、Completeness（Complete/Incomplete/Unknown）、UnverifiedLegacyRefs；无 stream/native，只有 Complete 且旧验证已通过者才能装载 |
| `ContentLeaseRequest` | Context、Closure、Access；Service 重验精确闭包/StoreView，无信任“Complete=true”旗标 |
| `ContentOpenRequest` | Context、OwnerRef:AssetRef、Role、LogicalPath；只从本 lease 已有清单中打开；无任意路径/URI |
| `ContentReadLease` | ReadId、ActualLengthBytes、FileDigest、ReadOnlyStream:Stream、ReleaseAsync/DisposeAsync；流不可 seek 到未授权对象/写入，返回租约归调用方，父 lease 计入子读取保持 |
| `ReadbackRequest` | Context、LeaseId、AdapterId/Revision、RuntimeSnapshot:SemanticSnapshot、ChallengeRef:AssetRef?、Access；同 lease 需重借内部 reader pin，租约释放与读回并发按 §8A |
| `ExportRequest` | Context、RootRef、Purpose、Access、Sink:IAssetExportSink、ConflictPolicy（Reject）；不隐式导出训练图，不 overwrite/append，v0.3 只导出完整技术包 |
| `OperationCancelRequest` | 原OperationId/ExpectedRequestDigest、固定CancelRequestId、Budget→请求合作取消，不取消已确认提交；等待token只取消观察 |
| `OperationQuery` | OperationId、ExpectedRequestDigest、Budget；核 owner、保留期和原摘要，QueryStatus 仅 Found/NotFound/Unknown，进行中用 Found+Outcome.Pending 表示 |
| `DrainRequest` | StopOperationId、Budget；同服务唯一停止 ID，重复返回原观察；token 取消等待不取消停止任务 |
| `ResourceReleaseRequest/ResourceQuery` | ResourceId、ReleaseOperationId（Query 可缺）、Budget；用于 lease/read/materialization release，不用业务 operation 查询代替 |
| `ServiceSnapshotRequest/Result` | Budget→本ServiceInstanceId/LastSequence/全部保留Operation/Resource不可变观察或错误；同锁水位，不返回流/句柄、不分页伪全量 |
| `AssetEventCursor` | ServiceInstanceId、AfterSequence:long>=0；异实例或缺口返回 SnapshotRequired，不拼不同进程序列 |
| `AssetEvent` | ServiceInstanceId、Sequence、OperationId、RequestEpoch、精确 Ref?、Kind、OperationObservation、ResourceObservation?、UTC RecordedAt；事件没有业务写入权 |
| `ServiceResult<T>` | Observation、Value:T?、Evidence:ReadbackReport?、EvidenceMode、Errors:ImmutableArray<ModelAssetError>、OwnedResources:ImmutableArray<ResourceRef>；只有 Outcome=Succeeded 才有 Value；失败/Unknown读回仍可在Evidence保留报告，不混入成功Value；资源转交见 §6A |
| `OperationObservation` | QueryStatus（Found/NotFound/Unknown）、OperationId/RequestDigest/Epoch、ExecutionPhase、Outcome、OutcomeVersion、ResourceDisposition、PendingResourceIds、TransferredResourceIds、ReconciliationRefs、Errors、Progress:ProgressSnapshot?；查询返回同一权威快照 |
| `ResourceObservation` | QueryStatus（Found/NotFound/Unknown）、ResourceId、ReleaseOperationId?、State（Open/ReleaseRequested/Draining/DrainUnknown/Released）、PendingChildren、Errors；Released 仅在底层停止并归还后 |
| `DrainObservation` | StopOperationId、State（Draining/DrainUnknown/Drained/ResourcesReleased）、PendingOperations/Resources、Errors |
| `SealReceipt` | 精确 Ref、存储原回执引用、实际 files 长度/摘要、提交状态、操作摘要；只有 ConfirmedCommitted 且绑定一致才成功 |
| `ReadbackReport` | RequestDigest、Root/Graph 精确 Ref、Adapter/Runtime/Challenge 修订与摘要、逐项参数 Requested/Observed/Status、内容完整性、FormatReadback（Supported/Unsupported/Unknown/ReadbackFailed）、Challenge（NotRequested/Passed/Failed/Unknown）、限制和原报告存储引用（若宿主保存）；报告不回写核心 |
| `ExportReceipt` | 完整所选闭包清单/摘要、sink 原回执、操作摘要和 ConfirmedPublished 状态；0 缺项才 Complete；目标可见但回执未知为 Unknown |

Context.Scope 与 Options.Scope 精确相等；Access.PrincipalRef 必须等于实例绑定 PrincipalRef，Scope 不匹配在接纳前 MA-AUTH-001。查询/订阅/Release 无跨实例Scope切换入口；Context 的请求摘要由操作专属、版本化 JCS 投影产生：operation kind、目标 Identity/Ref、所有语义参数、来源/运行快照的完整类型化投影（不是仅 schema digest）、ChallengeRef、所选 Purpose/Access 的主体与用途引用、ExpectedAbsent、Profile revision、Sink 的稳定目标 ID 和冲突政策；排除 token、流对象、进程路径、日志时间和瞬时 WaitTimeout。TotalTimeout/资源 Profile 作为原意图要求绑定，恢复等待预算不重写原请求。操作请求规则为 `model-operation-jcs-v2`，不能拿 payload digest 代替。

### 5A.2 显式端口和能力协商

`ModelAssetsHost.Create(ModelAssetsOptions, ModelAssetsPorts, ModelAssetsHostSlot)` 固定公开声明见附录 B.3。options 显式冻结 ServiceInstanceId、Profile/ServiceLimits、格式/旧验证器白名单和有界保留策略；ports=Store、UsageAuthority、具名 FormatAdapters/LegacyVerifiers、TimeProvider、DiagnosticSink。ContentSource 和 ExportSink 在每次操作显式传入，稳定 SourceId/TargetId 纳入请求摘要，不另装一份全局 locator。Create 仅校验/装配，无 I/O/后台任务/窗口，失败为 CreateResult.Errors 且 Service=null；成功 Service 非 null。Core 无 factory。TimeProvider.GetTimestamp/GetElapsedTime 计时，GetUtcNow 仅证据记录；注入的测试时钟不能调系统时间。DiagnosticSink 只同步 TryWrite 有界条目，失败不改变资产事实。

| 本模块端口/方法 | 输入→输出不变量；资源 Owner |
|---|---|
| `IAssetContentSource.OpenReadAsync(ContentSourceRequest, token)` | 精确 SourceId/role/path、限额、context→借用流 lease（actual metadata 在读取后报告）；流只由 source 关闭，Service 使用期间 pin，故障/取消仍先等流读结束 |
| `IModelAssetStore.ReadSnapshotAsync(StoreReadRequest, token)` | exact RootRef/purpose/context→单一 ViewId 的清单/全部节点/旧协议原预像元数据；缺/不一致整体失败，不返回缓存拼接图 |
| `IModelAssetStore.StageAsync(StoreStageRequest, token)` | context + validated manifest +逐项内容源→StageReceipt（StageId、逐文件实读 length/hash、ResourceId、LegacyMetadata?）；受限流式写，不把请求声明当实读；Store 拥有暂存/原始字节 |
| `IModelAssetStore.OpenStagedContentAsync(StoreStagedContentRequest, token)` | StageReceipt+精确角色/path→已完整校验的暂存内容lease；用于旧metadata原预像验证，pin Stage防清理，关闭后才可释放Stage |
| `IModelAssetStore.CommitAsync(StoreCommitRequest, token)` | context + StageReceipt +完整待绑定 descriptor/dependency hold fences + ExpectedAbsent→StoreCommitReceipt（ConfirmedCommitted/ConfirmedNotCommitted/Conflict/Unknown、原回执、request digest）；字节耐久与身份绑定/依赖保持须协调，不能独立先写索引再保字节 |
| `IModelAssetStore.QueryAsync(StoreOperationQuery, token)` | 原 ID/digest→权威回执/保留期/确认水位；NotFound 不能单独证明未提交；Unknown 保持 Store reconciliation，禁止新 ID 重发 |
| `IModelAssetStore.AcquireHoldAsync(StoreHoldRequest, token)` | 精确闭包/ViewId+context→HoldReceipt（HoldId/Fence、保持状态）；和 GC 同一协调边界线性化，新引用/导出/native 在途都保护；影响索引不完整不删除 |
| `IModelAssetStore.OpenContentAsync(StoreContentRequest, token)` | HoldId/Fence+精确 file identity→存储只读 lease；实读长度/hash 对原 EOF，不透出私有连接/事务；离线缓存须同 exact key 且重新完整性核验 |
| `IModelAssetStore.MaterializeAsync(MaterializeRequest, token)` | HoldId/Fence+完整 files+预算→私有只读目录 lease（适配器私有路径、逐项实际校验结果）；空根、拒绝链接/重解析、安全打开和并发替换验证属于 Store/宿主实现 |
| `IModelAssetStore.ReleaseAsync/QueryResourceAsync` | 原 ResourceId/release ID/budget→§6A ResourceObservation；Unknown 不释放/复用；转交长期保持有耐久 journal，可在重启恢复，不只是进程引用计数 |
| `ILegacyDigestVerifier.VerifyAsync(LegacyVerifyRequest, token)` | ExactRef、原 Rule/Algorithm、原预像/内容 lease、预算→Verified/Unsupported/Unknown/Mismatch；只使用创建时规则，不能由 Core JCS 代替 |
| `IModelFormatAdapter.ReadBackAsync(FormatReadbackInput, token)` | 精确租约/私有物化目录、Format、runtime snapshot、challenge Ref、context→ReadbackReport；实际 native 资源私有，报告返回之前须确认释放；不暴露句柄或共享 native 到 ModelAssets |
| `IAssetUsageAuthority.AuthorizeAsync(AccessInput, token)` | exact Ref/闭包、principal、usage/action、预期 authority revision→UsagePermit（PermitId/Fence、有效期、RevocationPolicy、EvidenceRef）或 Denied/Unknown；Permit 不是 ModelAssets 的质量决定 |
| `IAssetUsageAuthority.ValidatePermitAsync/ReleasePermitAsync/QueryResourceAsync` | 同 PermitId/fence+action+context→Active/Revoked/Expired/Unknown 或 ResourceObservation；在交付流/格式加载/导出提交前重核，准入与撤回须可判先后，不靠 UI 缓存 |
| `IAssetExportSink.BeginAsync/PublishAsync/QueryAsync/AbortAsync` | 固定 TargetId、context、受限 package entries、完整 package digest、Reject 冲突→私有 staging writer/publish 回执或 Unknown；sink 拥有外部副作用，回执未知保留原 staging/journal；只 confirmed-not-published 才允许 Abort |

这些端口是本模块接入语义，方法/request/receipt精确声明唯一在附录B.3，本表仅解释不变量；上游 DTO 映射不在 Core 内实现。storage-database v0.3 的 C0/C1 公共Runtime端口已经接收，§5A.4按其公开DTO给出限定桥。模型身份绑定/完整引用目录等领域绑定及A1/A2真实耐久仍按具体门接通，不再把所有Integration笼统视为候选。可先用无产品表的内存 simulator 验证状态/竞态，不能因此报告字节耐久或 GC 安全已通过。

### 5A.3 固定执行链（全部能力）

1. **导入/封存**：纯预检/声明投影（计算待Stage的exact Ref，尚非实读证明）→登记原 OperationId/RequestDigest→预约内存/暂存/队列→受限流读 Stage（不信任声明）→全部列出文件实际校验，包括存在的 optional→以实读结果对照声明投影（任何不等失败，不重写请求）→全部显式依赖（三种Purpose）逐项exact snapshot/旧规则验证/持久引用保护→旧Restore使用OpenStagedContent重借暂存metadata/文件并按旧verifier核原Ref→ExpectedAbsent CAS Commit→查原回执→短时资源释放或 Unknown 保持转交耐久 reconciliation。不会覆盖同 revision；已有完全相同绑定按原回执返回。RestoreLegacy 同样流程，但 verifier 使用原 metadata/原文件和原 Rule；metadata 作为独立输入流，Core 新投影不参与旧摘要重算；未支持旧 verifier 拒绝 CAS，绝不转换后冒充原 Ref。不能因后来 readback 失败回滚/改写已 seal 核心。
2. **精确解析**：读同View snapshot→核Identity/规则/新投影及可无损旧结构→显式目的DFS/最长深度→按完整结构闭包取得临时StoreHold（尚未用途批准，UnverifiedLegacyRefs保留）→打开已raw长度/hash校验的旧metadata/文件→按旧verifier核原Ref→释放子读/临时hold→返回immutable closure。旧节点全部Verified后才Complete且UnverifiedLegacyRefs.Empty；原Core图结果仍表示结构验证，不改成旧字节证明。缺映射/不支持verifier/hold未知返回Failed或Unknown并保留原资源，不从另一View补。StoreHold是字节保护，可用于已完整结构且待旧规则验证的闭包，不需要用途质量批准；Service Acquire交付则另外须完整性及Access通过。Resolve不获得用途资格，虽持有临时读lease但无流交给caller。
3. **Acquire/Open**：预检 closure/Access→authority Permit→线性化 Store hold→预算内读/校验→必要时私有目录→交付前重验 Permit/fence→转交内容 lease。每个 OpenFile 单独 pin 父 lease 并核 role/path；caller 关闭父 lease 后禁止新 Open，已开的子读取等真实退出后再归还。
4. **格式验证**：重借内容 lease pin→重验 Access→按 §10 真实 fresh reader→runtime 显式设定/读回→若有 challenge 严格消费生产者方法/样本/阈值→native 真退出和释放→返回独立报告→释放 pin。无 challenge 仅 NotRequested，不能误标 Passed；默认只验证格式，不自动训练/推理生产流程。
5. **导出/空目录导入**：冻结用途所允许完整闭包/Source 范围→Permit/hold→清单/投影/原字节完整性→sink 私有 staging 流式写→包摘要/0缺项复核→交付前 Permit 重核→sink Publish（Reject）→原回执确认。导入包先做安全解包/上限校验，再逐资产走相同 ImportAndSeal；新包保持原精确引用，不把时间/压缩容器头当核心内容。v0.3 不提供 PartiallySucceeded 导出，批量宿主分别调用并列逐项结果。
   v0.2 技术包为受控目录流：根 `bundle.json`（`model-export-jcs-v1` JCS UTF-8）、`assets/a00000000/` 起的资产文件目录，以及旧协议专用 `metadata/a00000000.bin`。bundle 顶层唯一键 `rule/rootRef/purpose/assets`；每项唯一键 `index/ref/core/legacy/files`。assets 按 Identity 的 NamespaceId/AssetId/RevisionId **ordinal 三元组**排序，index 为8位十进制连续字符串（0起，超过99,999,999或 MaxNodes 拒绝）；ref 使用 §4.2 的 exact Ref JSON。新资产 core 为 §4.2 完整技术投影、legacy=null；旧资产 core=null、legacy=`metadataFormatId/metadataFormatRevision/path/lengthBytes/digest`，metadata 内容是创建时原 manifest/预像元数据**原字节**，不能把新结构投影当旧原预像。files 条目固定 `role/path/required/lengthBytes/digest/packagePath`，按(role,path) scalar 排序；packagePath=`assets/a<index>/<原LogicalPath>`。同 path 多 role 只写一次物理文件且清单保留全部 role，同节点不同描述拒绝。legacy path=`metadata/a<index>.bin`，其 digest 是原 metadata raw-file-sha256-v1；原 Rule/Algorithm/精确身份仍取 ref，真实 legacy verifier 使用该 metadata 和文件。所有其他字段拒绝，旧 descriptor 缺原 metadata 或 verifier 不支持时禁止 Complete 导出，不虚构 legacy metadata。

   bundle 不含自身摘要，PackageDigest=`model-export-jcs-v1`/sha256/SHA256(bundle JCS bytes)，绑定 metadata 和每个文件 length/hash；sink 回执绑定 PackageDigest。导入方有界严格解析 bundle，拒重复/未知 rule/非法索引/路径越界/包外来源/缺项/意外文件/摘要不匹配。压缩容器仅宿主封装，安全解包/展开预算在宿主边界，不能把ZIP头 hash冒充包摘要；包内路径不能重写。导出目录和 Format.Layout 是不同布局，不能把 packagePath 当 native 入口。**模块 v0.3 不提供 ZIP/包解析 API**：包预检/迭代导入由工程工具宿主执行此固定格式，再叶→根逐项调用 ImportAndSealAsync（新）或 RestoreLegacyAsync（已支持旧协议）。整个导入包不是原子事务：若后项失败，前项已 confirmed seal 保留并显示逐项原回执，下次同 ID 重试；根未确认不能声称整包已导入。此语义不等于部分闭包导出成功。

6. **退役/撤回/回退**：authority/程序 Owner 修改采用资格，ModelAssets 不改技术资产/旧报告，不主动删字节。新 Acquire/Export/Readback 重验 authority；在途按 §8A 处置。影响索引未知不能返回“0 使用者”。GC 归 Store，ModelAssets 提供真实引用/保持事实；没有删除 API。
7. **关闭/恢复**：固定 StopOperationId 原子停新接纳（Query/Release 仍开放）→取消可取消等待/worker→保留在途资源直到真实退出→查询/转交未知提交 reconciliation→全部 caller-owned lease 显式释放才 ResourcesReleased→Dispose。无硬件最小 Host 也走同一链。

最小 Service Host 的语义顺序为 Create(options,显式 ports,预留root slot)→ImportAndSeal→Query 原 Unknown（若有）→ResolveExact→Acquire→Open/Verify（各自释放借用）→父 lease.Release/QueryResource→Drain（同 StopOperationId 重查）→Dispose。输出报告交宿主保存/采用，不在 Host 例子里批准生产。多个匹配/OCR 宿主各持自己的 service instance、authority 证据与取消域；共享 Store 字节可以，不能共享可变 native 句柄/语言状态。

### 5A.4 storage-database v0.3 公开运行端口限定桥

只读依据：[IM-066 storage-database 唯一指导§6.1–6.5、§7.1、§12](../storage-database/DEVELOPMENT-GUIDE.md)。C0/C1已接收（仅Runtime+可控fake+托管维护+双Host规格），A1 PostgreSQL/A2文件/A3备份真实门保持。桥为本模块Service.StorageDatabase可选DLL，引用Core/Service、`Asun.Platform.StorageDatabase.Contracts`、Runtime（Hasher），无WPF/native/SD私表。桥只借用Host已创建的 `IStorageDatabase`，Host按SD§7.1.1先root Reserve再保留`IStorageRuntimeFactory.CreateAsync`原Task；桥不偷偷再建Runtime/配置resolver/连接。

```csharp
// namespace Asun.Modules.ModelAssets.StorageDatabase
using SD = Asun.Platform.StorageDatabase.Contracts;
public sealed record ModelAssetsStorageBinding(ModelAssetsScope Scope, string PrincipalRef, ServiceEvidenceMode EvidenceMode,
    SD.CallContext ControlContext, string StorageDomain, SD.VersionRef RawFormat,
    SD.StorageInputLimits InputLimits, SD.StorageBindingDescriptor? SnapshotBinding,
    SD.StorageBindingDescriptor? CommitBinding, TimeSpan HoldTtl,
    ModelAssetsCleanupProfile Cleanup);
public sealed record ModelAssetsStorageBridgePorts(SD.IStorageDatabase Runtime,
    IModelAssetTechnicalBinding? TechnicalBinding,
    SD.IStoragePayloadCodec? SnapshotCodec, SD.IStorageResultCodec? SnapshotResultCodec,
    SD.IStoragePayloadCodec? CommitCodec, SD.IStorageResultCodec? CommitResultCodec,
    IModelAssetMaterializer? Materializer, TimeProvider TimeProvider);
public sealed record ModelAssetsStorageBridgeResult(IModelAssetStore? Store,
    StoreCapabilitySnapshot Capabilities, ImmutableArray<ModelAssetError> Errors);
public static class ModelAssetsStorageBridge
{
    public static ModelAssetsStorageBridgeResult Create(ModelAssetsStorageBinding binding,
        ModelAssetsStorageBridgePorts ports, ModelAssetsHostSlot owner);
}
public interface IModelAssetTechnicalBinding
{
    SD.IOwnerStoragePayload EncodeSnapshot(StoreReadRequest request);
    SD.IOwnerStoragePayload EncodeCommit(StoreCommitRequest request,
        ImmutableArray<SD.ObjectRef> objects);
    StoreSnapshot DecodeSnapshot(SD.OwnerReadResult result);
    SealReceipt DecodeCommit(SD.TechnicalCommitReceipt result);
}
public interface IModelAssetMaterializer
{
    ValueTask<PortResult<IFormatMaterializationLease>> MaterializeAsync(
        MaterializeRequest request, IModelAssetStore contentStore, CancellationToken token);
    ValueTask<ResourceObservation> ReleaseAsync(ResourceReleaseRequest request, CancellationToken token);
    ValueTask<ResourceObservation> QueryResourceAsync(ResourceQuery request, CancellationToken token);
}
```

桥Create的EvidenceMode由可信Host部署绑定显式给定、与Options和实际已创建Runtime后端类型一致；不能从SD.FileState或FileDurability猜Simulation/Production。C1 fake只填Simulation，真实后端未验时不得写Production验证通过。桥Create核binding.Scope=Options.Scope、ControlContext.Scope.TenantId=Scope.TenantId、Store/Profile exact、OwnerKey=登记的Scope.OwnerKey、RawFormat/StorageDomain/TTL限额（TTL须在SD已解析Profile.MinLeaseTtl/MaxLeaseTtl内，由Host注入）；不把AssetNamespace强塞进SD的Site/Device，物理StorageScope五字段由Host明确注入，不填空/unknown。SD Caller.PrincipalId必须等于实例PrincipalRef，AuthorityContextId为可信授权上下文，不能由请求构造凭据。Unknown查询仍用原Store.Generation，不从当前配置替原Generation。每个operation/文件/helper的SD完整identity保存在桥root受管记录中；释放请求只换有限观察预算，不改原ID/hash。

| 本地能力 | 唯一公开SD调用/DTO/字段映射 | 可证明范围与不支持分支 |
|---|---|---|
| Stage | source.OpenReadAsync受限lease→`Runtime.FileObjects.StageAndSealFileAsync(FileObjectRequest, stream, ct)`；Key=(StoreId,Generation,TenantId,StorageDomain,ObjectId)，Format=RawFormat、MediaType=application/octet-stream、ExpectedBytes/FileHash来自声明 | 逐物理path只seal一次、同path角色receipt保留；不同role给相同path时Source选按(role,path)排序第一项且所有声明length/hash一致，其他source不另消费；Core同物理文件语义不被改；只有FileReceipt.State=SealedDurable才可ConfirmedDurable。SealedNotDurable/Unknown不封模型；不把文件已封口当Identity已绑定 |
| 原SD ID/hash | OperationId=`ma-stage-`+StageKeyHash小写hex（序号按role/path排序后unique path，0起）；OwnerKey=Scope.OwnerKey、IdempotencyKey同OperationId；ObjectId=`ma-`+StageKeyHash小写hex；StageKeyHash为桥同步有界JCS投影的SHA256，rule=`model-sd-stage-jcs-v1`，唯一键`rule/scope/storageScope/store/storageDomain/modelOperationId/modelRequestDigest/fileOrdinal`，fileOrdinal规范Int64字符串，其余沿B.4/SD固定投影；PayloadHash=`StorageRequestHasher.Compute(FileObjectRequest, InputLimits)` | 使用SD固定信封hash，绝不将ModelAssets RequestDigest裸塞PayloadHash。只使用StageRequest已传Context及桥固定SD binding，RequestDigest已经绑定原SourceSnapshot，不要求桥重建未传的完整Service请求bytes；相同request/ordinal稳定；不同Scope/Store/Generation不能混；Stage对象immutable，不以logical path当机器路径。metadata单独序号排在文件之后 |
| 原task/回执 | `GetTaskStatusAsync(TaskQuery)`查原TaskHandle直至ResourcesReleased/Completed，再用`QueryOperationAsync(OperationQuery)`取原FileObjectReceipt/ObjectRef；Task/完整OperationIdentity均root强持 | 等待取消不Dispose Source流，不换operation。NotFound/ResultExpired仍不证未提交；Identity/hash/Format/长度差异MA-IDEM/MA-HASH。Source在原StageTask退出后release |
| 已暂存/封存读取 | `FileObjects.VerifyAsync(FileVerificationRequest)`→完整Verified回执→`OpenReadAsync(FileReadRequest(Object,0,Object.Bytes))`→包为ContentReadLease，保存原IFileObjectReadLease | SD范围read本身不证整文件，Verify不可省；只读完整lease/file raw摘要符合后交付。OpenStagedContent从Stage记录的ObjectRef取，不读开发目录 |
| 临时hold | 对完整闭包逐unique ObjectRef→`AcquireRetentionHoldAsync(RetentionHoldRequest)`，Ttl=明确HoldTtl→保存IObjectRetentionLease/ResourceHandle/version，必要`RenewAsync(HoldRenewRequest)` CAS | 逐对象保持期间阻GC；取得失败先禁新并释放已取得项，未清理仍root持有。HoldReceipt.Fence是对该组ObjectRefs和SD实例resource handle/version的本地绑定标识，不伪称跨对象全局发布fence；不将TTL当自动资源归还 |
| Release/QueryResource | SD lease自己的`ReleaseAsync(SD.ResourceReleaseRequest)`，Identity保留同Scope/Store/Owner及固定release ID、Handle exact；hold `GetStatusAsync(SD.ResourceQuery)`；Session同自身Release，Task以原GetTaskStatus查 | SD.Open/Draining/DrainUnknown/Released逐状态映射，不强收Stream；读lease无独立Resource查询API时查询桥持有的原ReleaseTask/当前活跃读并保留Unknown，不能发明Runtime.QueryResourceAsync |
| ReadSnapshot | `OpenSessionAsync(SessionRequest(CallContext,OwnerKey,Query))`→`IStorageSession.ReadAsync(RegisteredReadRequest)`→TechnicalBinding.DecodeSnapshot→Release/Dispose原Session | 要求Host注册精确SnapshotBinding.Kind=Read/Purpose=Query/OwnerKey/codec/schema/result及完整单View快照语义。缺binding/codec则ExactSnapshot=false、ReadSnapshot MA-CAP；SD通用Read bytes不是模型图 |
| Identity CAS / dependencies | `IStorageSession.ExecuteTransactionAsync(RegisteredTransactionRequest)`，TechnicalBinding.EncodeCommit返回已注册typed payload；References=新对象+依赖所有ObjectRef的排序精确集合；Hasher.Compute(request,binding,codec canonical bytes,InputLimits) | CommitBinding必须Transaction/OwnerKey/Serializable、ExpectedAbsent原子CAS、同事务写原回执、完整ModelAssets引用目录/引用保护协调。相同Identity不同digest冲突，不last-wins；Committed且ResultSchema/DecodeCommit验证通过才SealReceipt。SD公开Runtime可承载，缺Owner的真实catalog/codec/SQL/resolver时IdentityCas/DurableDependencies=false且Commit MA-CAP；不推测私表 |
| Unknown / durable保护 | SD原operation Query回执/资源保持；只有SD原Owner已有durable route/journal/protection并明确回执可给ReconciliationRefs | 通用TaskHandle、RetentionHold不是跨重启ModelAssets闭包持久保护。SD ReferenceCoordinator在Runtime内部协调，`IStorageDatabase`未公开PreserveAsync；桥不得另借Runtime拥有的backend或发明Runtime.ReserveClosure/BindClosure。缺注册提交/引用闭包证据时DurableReconciliation=false，禁止假转交、资源仍root持有 |
| 安全Materialize | 显式IModelAssetMaterializer按Format.Layout，从上述内容lease复制独占目录，逐copy限byte/拒link/reparse/替换、原Entry校验后返回lease | SD API不直接公开目录物化，缺adapter时SafeMaterialization=false并Verify MA-CAP；Stage/Read正常不必等该门。本模块冻结软件mapper/lease协议，Windows/NAS安全打开与真实路径属于对应adapter验证 |

BridgePorts中的Snapshot/Commit payload/result codec必须与已注入SD目录中的exact Version/Schema/CLRType一致；缺任何该binding所需codec对应能力=false。桥先TechnicalBinding.Encode→使用显式payloadCodec.Encode(payload,InputLimits.MaxPayloadBytes)与GetReferences→比较完整精确ObjectRef集合→StorageRequestHasher.Compute→再向Session发送，收到ResultSchema/Bytes先显式resultCodec.Validate才Decode；不能在桥临时选另一个JSON/codec或调用SD私有resolver。TechnicalBinding 是本模块领域codec适配（纯同步、有界、无I/O），Host在注册的SD目录中提供，不是SD新接口。输入payload至少绑定Scope、原model OperationId/RequestDigest、ExpectedAbsent、StoredAssetDescriptor、全部ObjectRef和DependencyHolds；snapshot参数至少exactRoot/purpose/request/profile，结果完整StoreView/Assets；JSON/typed codec必须遵本页相应投影及附录C.1（byte/hash绑定），未知字段拒绝，不允许业务表名/SQL/任意JsonElement。SD IStoragePayloadCodec.Encode/GetReferences与ResultCodec.Validate在其目录exact CLR Type/VersionRef匹配，桥收到结果后再次Decode字段校验；注册包按附录C.1实现Schema/StatementCatalog/golden，未实际部署只阻断该Owner绑定。技术注册包的VersionRef revision为int、hash为Sha256（小写64hex），不把opaque AssetIdentity.RevisionId解析成int。

StageReceipt/hold/原SD身份记录只在桥受管字典，有界MaxRetainedResources/MaxResidentBytes；Stage已封文件可成为SD orphan候选，Stage失败不得立即物理Delete，GC只由SD Owner协调、宽限和完整目录执行。ModelAssets不调用CollectEligibleOrphans以“清理失败”；文件lease/hold尚在IO则继续Draining。桥的资源Release只归还取得的lease/Session，借用Runtime不Stop/Dispose。Runtime生命周期归Host独立cleanup plan；一个Runtime可供两桥读，但each Scope及authority/session限额独立。C1 fake桥验证软件映射，不冒称A1/A2的flush/rename/GC/物理耐久通过。

## 6A. 执行结果、租约交付和事件的独立状态

完整 Service 采用两维状态，不把 Task 返回、资源归还、存储提交与用途资格合成一个 Ready。旧“Acquire 成功也必须先释放全部租约”是错误合同，本轮明确修正。

### 6A.1 Operation/Resource 状态

- ExecutionPhase：`Accepted → Queued → Running → Draining → Settled`；Outcome：`Pending/Succeeded/Failed/Cancelled/TimedOut/Unknown`。预检拒绝ExecutionPhase=Rejected、Outcome=Failed、OutcomeVersion=0、QueryStatus=NotFound，资源列表空，不登记Accepted、不发业务生命周期事件；重复非法请求仍预检拒绝。Denied/Conflict/Unsupported/Rejected是§7A错误类别， typed Outcome均Failed（外部未知用Unknown），不臆造枚举成员。Accepted 不等于 durable。
- ResourceDisposition：`None/Draining/Released/Transferred/Reconciliation`；如果并存，以 Pending/Transferred/Reconciliation ID 列表完整表达。Transferred=调用方获得租约，Reconciliation=未知提交的保持已由 Store 耐久恢复任务接收。均**不等于 Released**。
- 无租约普通操作只有短时 stream/worker/native 退出且资源实际归还后才能 Settled。返回 lease 的 Acquire/OpenFile 成功在原子交付时 Settled+Transferred，资源继续归 caller；其完整使用时长从交付计到 lease Released 单独记录。Service 全关闭必须等所有 caller lease Released。
- token 或 WaitTimeout 在接纳后结束等待：方法返回当前观察（Value=null，Pending/Unknown、Pending IDs），任务仍有 Owner，通过 QueryOperation/QueryResource 继续。取消是请求，不能把正在运行的 reader 当 Cancelled；TotalTimeout 到期进入 Draining。提交可能已发生则 Outcome=Unknown；confirmed committed 即使随后 token 取消，最终仍是 Succeeded，不把已保存事实改 Cancelled。
- Acquire 的交付是唯一所有权转移点；交付前 wait/token 到期，新的 lease 由 Service 负责释放，调用方不能从 QueryObservation 拿到无主句柄。交付后调用方即使不再等待也必须保留并释放已返回的租约；已返回 task Value 的对象不重复交付给第二 waiter。同ID重复Acquire/Open仅返回原Observation及资源ID、Value=null/OwnedResources.Empty，不再次授予已转交对象；首次caller已丢结果则按原resource恢复Release，需新请求重新Acquire，不把查询当句柄恢复。
- Import/Export 的 Unknown 不因 `NotFound` 变失败。查询必须来自正确 authority/owner、幂等保留窗口和摘要一致；只有存储/sink 明确 `ConfirmedNotCommitted/ConfirmedNotPublished` 才可清理。Unknown 的 durable hold/journal 转交失败时保留进程恢复 Owner 和 Pending IDs，不能 Settled/关闭完成。
- ResourceRelease 同 ID 反复返回原状态，别的 release ID 返回 Conflict 并指向原 release；Stop 同服务一个 ID，后续 Stop 返回原 Stop。DisposeAsync 无新取消 token，在 ResourcesReleased 之前立即拒绝完成并保留查询能力，调用方必须先有限预算 Drain/Release 再查询。

接纳前同时预约 operation/resource/订阅槽和输入 byte，限额满拒新，不挤掉 Pending/Unknown/未释放资源。终态观察/Released 墓碑在 Options 的 ObservationRetention 后可删（UTC 回执保留声明与单调进程计时分开）；原 Store/Sink 幂等耐久记录不随之删除。过期查询只能 NotFound，不能证明无副作用；Unknown 仅耐久转交确认且超过查询保留策略后可删除进程投影，原 reconciliation ref 仍可查询。MaxRetainedOperations/Resources 和 MaxSubscriptions 必填，保留期内槽满即 MA-RES-001。OutcomeVersion 初值0，初次 Settled=1，对账每次确认变更递增，不复用版本；Progress 不改变 OutcomeVersion。

所有端口 await 都由 Service 同时观察 WaitTimeout/TotalTimeout/Drain budget，绝不把 token 当强制中断。端口未返回则返回有限当前观察并保留受限 pending task/资源 Owner；晚到的流/目录/permit/report 在原 operation 清理或原子交付，禁止失联 fire-and-forget。外部 adapter 返回 ResourcesReleased 的事实才清账；后台任务/闩锁计入 MaxConcurrentWorkers/MaxQueuedOperations。DisposeAsync 在尚未 ResourcesReleased 时立即以 InvalidOperationException 拒绝（内部无无限等待、无销毁查询 Owner），随后可继续有限 Drain/Query/Release；所有资源已归还后幂等完成，订阅晚到回调仅可带旧 instance/epoch。

### 6A.2 事件、订阅和迟到结果

事件种类为 Accepted、PhaseChanged、Progress、ResourceTransferred、ResourceReleased、OutcomeSettled、OutcomeReconciled、SnapshotRequired。序列单进程服务实例严格增加（从1起）；checked溢出前停止新接纳，订阅置SnapshotRequired并保留查询/释放，不能绕回0。同 Operation 的初次 OutcomeSettled 至多一次，PhaseChanged/Outcome 同一权威观察投影。Unknown转交耐久恢复后确认原提交，仅追加OutcomeVersion更高的OutcomeReconciled（Unknown→Succeeded或ConfirmedNotCommitted对应Failed），保留旧观察，不重复OutcomeSettled/执行副作用；查询返回最新版本。Acquiring 先交付 ResourceTransferred，再 OutcomeSettled；不是伪造 ResourceReleased。进度可合并，不在存储/native锁下调用订阅者。

订阅是有界串行通知队列，callback 只接不可变事件，不传 lease/native/流。慢订阅者超过容量时断开，订阅的公开Status显示SnapshotRequired（不靠已满队列再次推送才知缺口），通过 QuerySnapshotAsync 取得同实例 LastSequence/所有保留 Operation/Resource 后，从 AssetEventCursor(instance,LastSequence) 重订；若读取期间又超保留队列，仍显示SnapshotRequired并有限重查，不拼漏事件。不得无限保留所有事件或阻塞业务提交。权威终态/回执保存在查询 Owner 中，事件缺口不会丢掉事实。原“终态事件永不可丢”修订为“事实耐久且缺口可查询”，不能以有界队列作耐久证明。

callback 异常隔离、诊断限长；callback 不能调用同步 Wait/阻塞 UI。Dispose subscription 原子禁止后续 dispatch，正在调用的 callback 可结束，宿主按 ServiceInstanceId/epoch 拒绝其迟到投影；回调没有资产资源所以退订不取消其他业务或释放 content。服务停止后仍允许查询/释放到最后 resource Released，迟到旧 operation 只能更新自己的原 Ref，不改变新 revision/选择。

## 7A. Service 错误和安全恢复

Core 闭集见附录 A.2。完整 Service 在本地定义以下闭集，不擅自注册平台全局错误；每个错误含 Code、FieldPath、不可变 Context，另由宿主诊断接口记录原异常。

| 码 | 含义 | 状态/恢复 |
|---|---|---|
| `MA-FMT-001` | 未支持格式/reader/旧规则 verifier | Unsupported/Unknown，允许历史存档但不能装载；不换模型族 |
| `MA-FMT-002` | fresh read 或参数/challenge 断言失败 | ReadbackFailed，保留原资产/报告，交生产者处理 |
| `MA-CAS-001` | 已有同 Identity 不同 digest，或已存在不同绑定 | Conflict；新意图创建新 revision，不覆盖 |
| `MA-IDEM-001` | 同 OperationId 复用不同请求摘要 | Conflict；查询原操作，不自动新 ID |
| `MA-STORE-UNK-001` | 字节/绑定/外部 publish 回执未知 | Unknown；原 ID 查询，保持 journal/hold，不清理 |
| `MA-CANCEL-001` | 取消且真实退出完成，无已提交事实 | Cancelled；不等于撤回已 seal 内容 |
| `MA-TIME-001` | 总预算耗尽且真实退出完成，无未知提交 | TimedOut；纯读可新请求，持久操作先查询 |
| `MA-AUTH-001` | 用途/操作授权明确拒绝、撤回或过期 | Denied；不交付新流/导出，已运行按 §8A |
| `MA-AUTH-UNK-001` | authority 断连、新鲜度或撤回顺序无法确定 | Unknown；阻止需授权的新动作，不默认离线允许 |
| `MA-RES-001` | worker/缓存/lease/队列额度不足或代次冲突 | Rejected 或 Draining；不 OOM 兜底、不强收他人资源 |
| `MA-CAP-001` | 必需端口/能力未装配 | Rejected；指出具体 capability，不隐藏窗口补初始化 |
| `MA-DRAIN-001` | 资源释放或关闭预算到期且未确认 | DrainUnknown；保持 IDs，查询真实退出，不再接纳 |
| `MA-SIG-001` | detached签名非法/算法不支持/key不可信或过期 | 沿PackageSignatureStatus区分；要求签名的入口拒绝，重新提供可信证据，不改包内容 |
| `MA-SIG-UNK-001` | 信任快照/可靠UTC或key撤回状态未知 | Unknown；仅阻要求签名的入口，查询安全Owner原信任版本 |

错误上下文含原 Ref/Rule/Profile、阶段、读数/预算、Adapter、Authority revision、操作/资源 IDs；不含密钥、token、模型字节、训练内容、裸私表或任意路径。§7A中的MA-HASH/MA-PATH等简称分别指附录A.2已冻结对应完整Core错误码，不新增同义码。无新重试 ID 的自动恢复只能是原查询/同意图幂等接收；参数/目标/用途改变必为新意图，经旧操作恢复边界处理。

## 8A. 租约、撤回、取消与 Owner 闭合

### 8A.1 资源所有权和线程

| 资源 | 创建/当前 Owner | 停止/归还条件 |
|---|---|---|
| 不可变清单/摘要 | Core/调用方托管值 | 无关闭、无事件；不暴露 backing array |
| 输入只读流 | Source port | Service 借用 pin，实读线程退出后 Source lease release；Service 不擅自 Dispose 原调用方 stream |
| Stage/持久 dependency hold | Store | CAS 及 durable 回执确认后按原协议转长期保持；Unknown 转 reconciliation，不因用户取消删暂存 |
| content/目录 lease | Store 底层；交付前 Service、交付后 caller | 每个 child read/reader pin 真退出，caller release 才归还；TTL 不等于资源可删 |
| native model/GPU | 格式 adapter（每次 fresh read 私有） | 同 owner worker 等 reader/challenge 结束再清理；不进入 ModelAssets 公共结果 |
| 权限 Permit | authority，caller/service 借用 | 交付前/导出 publish 前重验，撤回不能伪装成物理排空；authority释放独立记录 |
| Export staging/sink receipt | Sink，Service持原 operation | Publish Unknown 查询/恢复，confirmed not-published 才 Abort；不擅覆盖外部目录 |
| 事件/语言/选择 | 各宿主订阅/投影 | 退订/epoch 切换不触发业务取消、生产放行或共享资源提前释放 |

单调 clock 计总预算，UTC 只用于证据有效时点记录；不同进程不能直接传 Stopwatch tick，端口传剩余 TimeSpan 和原 Budget identity。并发缓存 key 至少 `(exact Ref, purpose, role manifest, format adapter revision, 包含运行快照的request digest)`；相同 blob 去重不合并授权缓存/identity。缓存只有无 lease、无 worker、无 reconciliation 时可淘汰，额度先预约再创建。ReadbackRequest.Access.RequiredAction=ReadForUse（UsagePurpose明确FormatVerification或生产者已获准用途）；ExportRequest要求Export；Acquire/Open仅ReadHistory或ReadForUse，不能以Export许可冒充任意读权限。Resolve核Access但不自动获得生产资格。共享读取只合并只读字节；每 waiter 取消只移除自己的等待，最后 waiter 离开仍须等实读/native 停止。

格式 reader 优先在每 adapter 的有限专属 worker 上创建/运行/释放，以保守串行所有权支持 `clear_dl_model` 的 local scope；不能用 `Task.Run` 的每个 continuation 随机线程完成创建/清理。其他 reader 页标 reentrant 不证明同一可变 handle 可同时 set/clear。关闭父 lease 与 Verify/OpenFile 的 pin 建立必须线性化：关闭先发生拒绝新 pin，pin 先发生则等待该 pin 真退出后才 Released。

### 8A.2 用途撤回/断连和在途动作

ContentLease 是字节保护，不是永续用途批准。authority Permit 固定 Ref/用途/主体/action/fence/有效时点，提供 `DenyNewAndDrain/AllowCurrentUntilExpiry` 两种外部政策；本模块默认请求 DenyNewAndDrain，后一种只能使用原 authority 的明确返回，不自行延长有效期。Service 在交付/运行前建立 authority.Subscribe 的有界 Permit watch；原fence变Revoked/Expired或watch缺口SnapshotRequired立即禁新并对本worker请求停止，保留原Owner待退出。watch回调不得持业务锁，Service只排有限控制消息；无法建立实际撤回通知的adapter不得接DenyNewAndDrain生产用途，真实传输接收门不能用polling关闭。续期由 Service 重调用 Authorize 并核原 Ref/主体/用途、原租约代次，不能改资产引用；Service为每Permit建立受管到期观察（TimeProvider单调计时，ExpiresAtUtc差值在首次批准时冻结），到期请求禁新/合作停止；最多MaxOpenLeases/MaxQueuedOperations个timer，取消/释放时真实结束timer，事件不能静默漏过期。若 Store 需要 keepalive，用其原 hold 协议保持同 fence，续期失败停止新工作并保持已有 pin 至退出，不以 lease 超时强删。

- 新 Acquire/子 OpenFile/Readback/Export publish 前必须 ValidatePermit；ValidatePermit的Active返回是authority在同fence下授予这次具名action的接纳记录，与撤回在同authority协调边界有先后；只“先检查bool后独立执行”不满足FencedAdmission。返回原PermitId/action/Ref变化拒绝，Service持此action授予至使用/publish真退出；撤回后当前policy决定取消/等待，不能称撤回回滚已发publish。只有过期缓存、离线或断连则 Unknown，拒绝新动作。历史诊断读取也需单独 ReadHistory 权限，不能因生产用途撤回就默认保留查看权。
- DenyNewAndDrain 撤回后：关闭新读取/加载/导出→向本操作 worker 发停止请求→retain stream/目录/Store hold→真实退出后归还 native/content/Permit。adapter 不可中断就等待，不提前卸载/释放 GPU。已经 confirmed committed 的资产/导出不能被取消改失败；后续访问由 Owner 政策控制。
- 已获得原始流/native 并正在运行的消费者，必须由宿主负责遵循撤回 fence 和停止通知；ModelAssets 不能强收交出的 stream 或命令设备停机。未提供这种消费约束的 host 不得用于受撤回控制的生产用途，不能用周期性 polling 宣称原子撤回。
- 同字节两用途：撤回 OCR 用途不能删除匹配的持久历史引用，但不赋予匹配新的权限。Store GC 只有跨 Owner 引用目录完整、持久保持/运行/导出/备份/调查均关闭并在统一 fence 下复核，才可回收；影响索引/缓存“0”不是证明。

## 9. 新资产 JCS、旧资产原规则与版本迁移

### 9.1 唯一 canonical 路线和反例

新资产保持 `model-core-jcs-v1`，原始文件 SHA-256 针对 byte0→EOF 原字节；文件不做 JSON 规范化、换行/Unicode/解压容器重写。技术核心按 §4.2 类型化投影→字段语义/唯一键/上限→文件及依赖集合排序→直接 JCS UTF-8 bytes→SHA-256，不用普通 serializer 输出代替 JCS。

- 集合字段 files 按 `(role,path)`，dependencies 按 `(purpose,role,namespace,id,revision,rule,algorithm,hex)`，semantics.fields 按 ID；字符串分量按 **Unicode scalar value**，用 `Rune` 序列比较，不受 culture 影响，不拼接成有歧义的键。角色重复跨分片可合法，唯一元组重复拒绝。
- **JCS 对象属性按解码后的 UTF-16 unsigned code unit ordinal 排序**，递归执行；这与上条业务集合排序是两种不同规则。数字形键 `"10"` 在 `"2"` 前；emoji U+1F600 在 U+E000 前。不能先建 JS 对象再依其整数键枚举，也不能用 UTF-8/scalar 顺序替代 JCS 属性顺序。
- 数值使用 ECMAScript shortest round-trip binary64。选定移植 §17 固定的 WebPKI `es6numberserializer` 七文件完整调用闭包：`NumberToJson` 快速 dtoa，失败调用 `NumberDToA`；移植到 Core 内部命名空间，仅更改目标/可见性/必要适配，不重写数字算法、不用 `double.ToString`/STJ/替换 E 为 e。保留内部算法要求的 unchecked 位运算，不能因 DTO checked 规则随意改数值算法。
- JCS writer 自建有界 typed-tree traversal，只借鉴已核 C# reference 的 string escaping/ordinal 对象遍历，**不移植其无深度/输出预算的递归 JSON parser**。字符串输出 quote/backslash 与 U+0000–001F 按 RFC 转义（b/t/n/f/r 短转义、其余小写 `\u00xx`）；slash、HTML、非 ASCII 不多转义；拒绝孤立 surrogate，不隐式 NFC/NFD。输出无 BOM/空白/末尾换行。
- 属性重复在构造 AST 之前/构造器保存全部成员后校验，不能先落到 Dictionary 丢重复。入口 JSON 包解析使用严格 UTF-8、禁止注释/尾逗号、显式深度/大小限额和重复名检查；`Utf8JsonReader` 不自动替代对象栈重复检查。Core API 不接受原始 JSON 包。
- JCS 通用值层 NaN/Infinity 错误，-0→0；model-core 语义层 Binary64 的 -0 拒绝，Int64/Decimal 字符串遵 §4.2；每种数值都带 Kind/单位。时间若生产者声明进入语义，使用 schema 固定 UTC Z 精度，无法无损转换/缺时区/闰秒未定义就拒绝，不能采用本机时区或静默截断。
- 自身 digest/report/lease/Profile 不进预像。若字段、新含义、数组分类或精度规则改变，必须新投影 Rule/schema revision；不能仍使用 model-core-jcs-v1 并重写旧引用。新增无行为 UI 标签不影响技术摘要。

该路线依据 RFC/实读源码选择一致性，不宣称最快；性能与跨实现对照见 §13/14。生产不得调用 Python/Node 规范化进程。

### 9.2 旧规则、未知格式和迁移回退

读取 Ref 先分派 Rule/Algorithm：新核心按本页投影；旧核心由 `ILegacyDigestVerifier` 按创建时原预像/原算法；unknown rule→Unsupported/Unknown，可在有权限时保留原字节/原引用，但拒绝运行/完整闭包导出。不可把未知旧资产用 JCS 重算后宣布 Mismatch；旧 schema 的缺省/顺序/身份字段保持不变。

转换是生产者/迁移工具创建新 manifest/files、记录原 exact parent Ref/工具/参数/差异报告，产生新 revision；旧核心/报告不变，用户/程序 Owner 切换精确引用。转换失败不切 active revision。新旧模块并存窗口按消费者 Profile 明确；回退选择原模块/adapter/schema/ref/运行快照，不能把新 native handle 交旧 reader。

报告引用方向 `adoption/qualification → report → core → files/dependencies`，核心不反向引用本次报告；父模型的历史报告仅可作为 RebuildSource 来源，不能换名把本次报告绕回当前核心。新 readback 观察若必须成为解释语义，生成新核心，不追写旧摘要。Core图结构验证和旧协议真实字节验证必须分开显示。

## 10. HALCON 26.05 格式路线与训练边界

本模块不是视觉检测算法。清单/JCS/身份/CAS/依赖/授权/GC 不适用 HALCON；模型文件读回由生产者 adapter 经 `ImageLibDotNet.cv2` 使用全部 HALCON 26.05 算子，不重复核验存在性，不接 `HOperatorSet`/halcondotnet.dll，不读 AsunImage 内部。只有 C# overload/类型/封送歧义才查公共签名或消费者编译。

### 10.1 格式逐族主路线与资源退出

所有路线都先受控空目录物化完整必需闭包、对原文件实读 length/hash，再创建 fresh reader。绝对目录路径只在物化/adapter 内部传递，避免 HALCON 搜索 `$HALCONROOT/dl`/当前目录补包；模型扩展名只作提示。各模型逐项记录比较子集；以下不是跨族通用 GetAllParameters。

| 模型族 | 已实读 26.05 页面/固定主路线 | 分支/释放 |
|---|---|---|
| Shape | `read_shape_model`→`get_shape_model_params`；NumLevels/AngleStep/ScaleStep/MinContrast 按生产者 schema 查询、保留实际 auto 值；需要轮廓对照时 `get_shape_model_contours` | fresh 创建的 model 由 adapter 在使用完毕后 `clear_shape_model`；缺/不支持参数明确 Unsupported，不由 JSON 重建 |
| NCC | `read_ncc_model`→`get_ncc_model_params`（NumLevels/AngleStart/AngleExtent/AngleStep/Metric），与冻结创建声明对照 | `clear_ncc_model`；不因模型读成功就认定匹配稳定 |
| Deformable | `read_deformable_model`→`get_deformable_model_params`，只查询对应 calibrated/uncalibrated/local 族支持参数 | `clear_deformable_model`；cam_param/reference_pose 不默认存在，不换 Shape/NCC reader |
| Variation | `read_variation_model`；生产者指定可观察项，`get_variation_model` 可返回 ideal/variation image，另占有界 iconic 输出资源 | `clear_variation_model`，图像对象按 adapter 公开所有权释放；direct/prepare 后丢训练统计时不声称可恢复训练；不编造统一 threshold 查询 |
| Deep OCR | `read_deep_ocr`→生产者冻结的 `set_deep_ocr_param`/`get_deep_ocr_param`→字符/通道/运行快照对照；runtime 参数文件不持久化、读回默认 | Deep OCR handle 经官方通用 `clear_handle` 清理（不存在 `clear_deep_ocr` 算子）；同 owner worker 串行，不能同时 apply/set/clear |
| HALCON DL/可支持 ONNX | `read_dl_model`→`get_dl_model_param('min_version',生产者规定shape/type等)`；运行 device/runtime/precision/batch 等只设/读官方对该模型支持的项 | `clear_dl_model` 标为 **local scope**，须同创建 worker 清理；ONNX有版本/网络支持限制和转换，原文件读成功不等于后端等价 |
| 未登记格式/旧规则 | 保存原字节/来源、显式 Unknown/Unsupported；格式验证不启动未知 reader | 不换后端、不换旧模型、不从开发缓存补依赖；登记对应生产者 adapter 后才可验证 |

这些 read 页多为 reentrant/global/without internal parallelization，但 handle 状态可变；不能由此推导同一 handle 可并发。Shape/NCC 的 `serialize/deserialize_*` 是实质备用候选：可减少磁盘，但不提供跨族统一能力、不验证正式封存文件/外部闭包，也需要 serialized-item 所有权。本轮冻结**真实文件 fresh read**为验收主路线；内存 route 暂不作为资产封存验证替代，没有同样本实测不宣称更快。

### 10.2 生产者 challenge、弱信号与推荐参数

- ModelAssets 不接 ROI/图像质量输入、不设 MaxMatches/MinScore/曝光，不训练/prepare/微调/推理生产板件。ROI粗精路线、遮挡/多候选/低信号/拒识能力属于匹配/OCR/AI 的同样本比较；本模块接收其冻结 challenge 的方法/输入 Ref/期望/容差/预算，不能擅自挑检测路径。
- Challenge 可缺省为 NotRequested（格式读回仍单独有结论）；若某用途要求 challenge 而缺样本/真值，usage evidence 为 Unknown，不假定格式通过=用途通过。生产者 challenge 返回多候选/合法拒识时按其 Profile 判，不由资产层取最高分或空结果改 PASS。
- HALCON auto 创建参数的 Requested 与 AutoResolved 实际值分开保存，生产者通过上述可用 query 提供实值/Unsupported；资产层只校验有界类型/单位/来源，不运行参数搜索。参数编辑返回新候选，不能改变已 seal 核心或静默替换生产阈值。
- 同参数改值、预处理顺序、词表/类别表、通道 layout 或必要 runtime requirement 改变都改变新核心摘要；某次实际运行设置变化另改变包含运行快照的RequestDigest。只切显示语言/预算不改变核心身份。
- 训练与恢复由生产者/AI数据 Owner 判断：模型文件可装载≠拥有训练数据/optimizer/scheduler/AMP/random state；recovery 明确 Exact/Limited/Unavailable 与证据，缺源可历史保存但不能称可重训。同 seed/hash 不保证跨设备数值等价。

## 11. 两个审查视角的可执行反例

以下是设计断言和未来测试输入，不是已执行结果。视角一从“消费者获得的是哪个不可变内容/语义”逐能力推导；视角二从“谁仍在使用/有权使用资源”模拟竞态和故障。两表都覆盖整模块，不能用首片无 I/O 来豁免 Service。

### 11.1 内容/语义与外部接入视角

| 输入/变化 | 固定处理和期望输出 | 验收/恢复 |
|---|---|---|
| 空 manifest/文件/主入口；空依赖 | 缺主文件或零 byte 主文件 MA-REQ；明确无依赖图合法只含 root；catalog空结果是 Empty不是“无依赖” | 未接纳前不碰 Store/native；修正声明，不填默认文件 |
| 同 Role 两分片；同路径两 Role；相同 blob 两身份 | 允许多分片/多角色，唯一 `(role,path)` 保留；同路径实读描述相同；技术去重不合并业务绑定 | 对照所有条目/角色/Identity，不能将字典按 Role last-wins |
| Path `weights/../model.bin`、`CON.bin`、ADS、大小写/NFC碰撞 | Core词法拒绝；合法字符串下实际链接/替换由物化拒绝 | 纯字符串检查不冒充链接安全；unsafe root不交reader |
| Diamond A→B/A→C，B→D/C→D；长路径也到D | 共享节点但保留全部边；DFS检测灰回边+拓扑最长深度 | 深度按最长路径，不能黑节点跳过预算；超界整体Invalid |
| 同 Identity 两digest、重复节点/重复边、缺多跳节点 | MA-DEP；不选“第一个”/latest，不返回完整截断图 | 返回依赖路径，caller补完整同水位输入 |
| 词表顺序/输入通道/预处理步骤/threshold/shape改变 | 字段/schema/有序序列进入投影，生成新digest/revision | 原Ref/程序采用不漂移；budget/语言改变技术digest不变 |
| 大整数9007199254740993、decimal0.10、非有限/负零 | Int64字符串不经过double；Decimal规范0.1；Binary64非有限/负零语义拒绝 | 通用JCS -0向量仍输出0，区分两层测试 |
| 新JCS和旧规则同裸hash；旧规则不明 | Rule/Algorithm对象明确区分；新投影不重算旧预像 | Unknown旧资产历史保留，不能运行/Complete export |
| 超大weights/超深图/巨大参数数组/解压高展开比 | 入口复制前限额、checked、流式读、输出写前预算；不无限递归 | MA-LIMIT；报告预算项，不能OOM或截断假成功 |
| 格式fresh可读但参数QueryFailed/未保存runtime | 内容完整与FormatReadback/Runtime分别报告；Required观察失败 | 不能默认值补缺、复用旧handle；新报告保持原core |
| 模型challenge低信号/遮挡/多候选/合法拒识 | 向生产者challenge契约返回原证据，由其Profile判；未请求为NotRequested | ModelAssets不取最高分/降低阈值/质量PASS；样本缺门只影响对应用途 |
| 有模型无checkpoint/训练图/optimizer | 技术可历史保存，RebuildSource完整性单独Unknown/Unavailable | 不能声称可复训/Exact恢复，不阻断无关历史读取 |
| 导出漏字典/外部权重、空目录重导入 | 完整清单逐项校验→0缺项才Publish；fresh reader仅正式闭包 | 禁用开发目录/网络补包；缺项不PartialSucceeded |
| 两消费者匹配和OCR | 同Ref/规则/Service公共合同，各自RuntimeSnapshot/adapter/权限 | 不引用对方产品类型/私表，字符序列和匹配参数都稳定 |

### 11.2 并发/权限/资源 Owner 视角

| 对抗时间线 | 必须保持的结果 | 恢复断言 |
|---|---|---|
| 相同revision并发seal不同内容 | Store CAS仅一个绑定；另一Conflict，旧绑定不覆盖 | 查询原receipt，不偷偷新revision掩盖冲突 |
| 同OperationId相同/不同RequestDigest | 相同恢复原进度/receipt；不同MA-IDEM，无新副作用 | 不拿文件hash代替request hash |
| Commit发出→断连/token取消→Query NotFound | Unknown保持journal/hold，NotFound不证明未提交 | 同authority/owner/保留期重查，confirmed-not-committed才清理 |
| 两waiter共享读，A取消、B继续；最后waiter取消 | 各自取消域；共享IO退出前仍保持资源 | 无早释放；未退出时仍Draining，不假Cancel完成 |
| Acquire等待到期恰逢交付 | 单一原子交付边界：交付前Service释放，交付后caller拥有 | 每lease恰一个Owner；查询不复制租约对象 |
| Open/Verify pin先建立与父lease.Release竞争 | pin先赢则等其退出；Release先赢拒绝新pin | 子流/native退出后才父Released，查询列pending children |
| 读回native不支持抢占，deadline到期 | Draining保持目录/流/hold，专属创建线程清理 | Outcome不假TimedOut终态；真实退出后释放，不复用路径 |
| authority撤回/过期/断连与新Open/publish竞争 | 核Permit fence与接纳先后；拒新/停本操作按原政策 | 不强卸载handle，不删除旧资产；历史读取另核ReadHistory |
| StoreGC与新引用/lease并发 | 原Store协调边界取得hold并重核；不靠缓存计数 | 无共同fence时GCBlocked；索引unknown不认为0 |
| Stop与新请求/旧Release/Query竞争 | 接纳原子关闭，释放和查询继续；同Stop ID恢复 | caller lease未还不能ResourcesReleased；Dispose不销毁查询Owner |
| subscriber慢/抛错/退订/窗口关闭 | 有界投影队列、SnapshotRequired，业务状态不回滚 | 回调无lease，epoch丢旧投影；新窗口不受旧回调覆盖 |
| 旧reader升级/回退、迟到旧revision报告 | 原Ref/adapter/runtime绑定，旧结果写原报告 | 不改新revision/active，旧核心原规则验证保留 |
| 进程重启/长稳重复acquire-release | Store恢复原journal/operation；新ServiceInstanceId | 内存native不声称跨进程存活；hold/lease/临时目录/队列计数回基线或明确reconciliation |

## 12. 可选 Model Assets Workbench：精确修订查看与对照

可选 UI 是原架构已有范围，不凭本轮新增 UI 或批准其实现。Core/Service 无 UI 全部可用；只读工作区不拥有发布/激活/质量/删除权。既有 [UI-PCS-002 模型工作区](../../shared-modules/guidance/14-page-contracts/UI-PCS-002_Vision_Workspace.md#model-assets-workbench-ui) 的业务操作链复用，本节给本模块控件/Host的具体设计；跨共享 PageContract 同步由主会话处理。

### 12.1 Host API、任务流程和布局

控件候选 `Asun.Modules.ModelAssets.Wpf.ModelAssetsWorkbench`（WPF UserControl），宿主 `Bind(WorkbenchBinding)`→`SetCulture(CultureInfo)`→`UnbindAsync(WorkbenchWaitBudget, CancellationToken)`。Binding 必填 Service、只读 CatalogProjectionProvider、具名 Profile、宿主语言/主题、LayoutStore、CommandHost、权限投影；它们是公开 port，不接产品 ViewModel、私表或隐藏窗口。Catalog 查询/分页由宿主接已有 query 投影，资产模块不实现第二通用查询引擎。SelectionChanged/CompareRequested 只输出精确 Ref/选择epoch；所有业务命令调用同一Service，不能在 UI 另造 hash/资格判定。

操作者为工程人员和历史追溯人员；固定流程：搜索→选具体revision→看files/dependencies/语义/五维证据→选另一精确revision比较→按权限执行“验证格式”或“导出预览”→确认当前目标→执行/显示原operation→Unknown只“查询结果”。导入预览由宿主工具显示缺项/冲突/新增与复用字节/空间，提交为新technical资产，绝不自动生产采用；此只读控件不提交导入。退役/回退请求交宿主原Owner，不在此控件直接执行。

只验收1920×1080物理基线，计算实际工作区扣除任务栏/标题/边框；以下高度是内容区域 DIP，纵向主区用剩余空间，**不假定1080都能用于内容**。全宽顶部64 DIP 为检索/过滤与精确选择，底部40 DIP 为原操作/错误/恢复；中间Docking比例左24%修订catalog、中46%文件/依赖/差异、右30%语义/报告。中区树/差异上下初始60/40，允许拖分隔但关键错误区不关闭。宿主如果提供参考图，用同一viewport公共控件放可选预览tab，ModelAssets不自己造图像算法/句柄。

#### 12.1.1 控件公开接入合同（WPF切片设计声明）

namespace=`Asun.Modules.ModelAssets.Wpf`，构造器 `public ModelAssetsWorkbench()` 只创建控件/默认资源，无Service查询/隐藏窗口/设备初始化。公共方法/事件固定如下；不是DevExpress SDK签名。CatalogProvider/CommandHost/LayoutStore是Host port，由宿主装配，不得从Application.Current或static locator取得。UI只是投影，显示文化不改变Core摘要。

```csharp
public sealed record WorkbenchWaitBudget(TimeSpan WaitTimeout);
public sealed record WorkbenchProfile(string Id, string Revision, int PageSize, int MaxRows,
    int MaxDetailFields, int MaxPendingCommands, int MaxQueuedProjections,
    int MaxLayoutBytes, WorkbenchWaitBudget QueryBudget);
public sealed record WorkbenchPermission(string AuthorityRevision, bool CanRead,
    bool CanVerify, bool CanExport);
public sealed record WorkbenchBinding(IModelAssetService Service,
    ICatalogProjectionProvider CatalogProvider, IWorkbenchCommandHost CommandHost,
    IWorkbenchLayoutStore LayoutStore, WorkbenchProfile Profile, CultureInfo Culture,
    string ThemeKey, string UserScopeRef, WorkbenchPermission Permission);
public sealed record WorkbenchBindResult(bool Bound, long BindingEpoch,
    ImmutableArray<ModelAssetError> Errors);
public sealed record WorkbenchSelection(long BindingEpoch, long SelectionEpoch,
    AssetRef? Selected, AssetRef? CompareWith);
public sealed record WorkbenchUnbindObservation(bool Detached, long BindingEpoch,
    ImmutableArray<string> PendingOperationIds, ImmutableArray<string> PendingResourceIds,
    ImmutableArray<ModelAssetError> Errors);
// ModelAssetsWorkbench : UserControl 的公开成员声明，省略实现。
// WorkbenchBindResult Bind(WorkbenchBinding binding);
// void SetCulture(CultureInfo culture);
// void SetPermission(WorkbenchPermission permission);
// ValueTask<WorkbenchUnbindObservation> UnbindAsync(WorkbenchWaitBudget budget, CancellationToken token);
// event EventHandler<WorkbenchSelection> SelectionChanged;
// event EventHandler<WorkbenchSelection> CompareRequested;
public sealed record CatalogPageRequest(string QueryText, string? Cursor, int PageSize,
    long BindingEpoch, long SelectionEpoch, WorkbenchWaitBudget Budget);
public enum CatalogContentState { Unknown, Verified, Mismatch, UnverifiedLegacy }
public enum CatalogUsageState { Unknown, NotAdopted, ApprovedForPurpose, Revoked }
public sealed record CatalogRow(AssetRef Ref, string FormatId, string FormatRevision,
    CatalogContentState ContentState, CatalogUsageState UsageState,
    string UsagePurpose, string AuthorityRevision);
public sealed record CatalogPage(string ViewId, string ViewRevision, string AuthorityRevision,
    ImmutableArray<CatalogRow> Rows, string? NextCursor);
public sealed record CatalogPageResult(CatalogPage? Page, ImmutableArray<ModelAssetError> Errors);
public sealed record WorkbenchDetailRequest(AssetRef ExactRef, long BindingEpoch,
    long SelectionEpoch, string ExpectedAuthorityRevision, WorkbenchWaitBudget Budget);
public sealed record WorkbenchAssetDetail(StoredAssetDescriptor Asset, ResolvedClosure? Closure,
    ImmutableArray<ReadbackReport> Reports, string ViewId, string ViewRevision, string AuthorityRevision);
public sealed record WorkbenchDetailResult(WorkbenchAssetDetail? Detail, ImmutableArray<ModelAssetError> Errors);
public interface ICatalogProjectionProvider
{
    ValueTask<WorkbenchDetailResult> ReadDetailAsync(WorkbenchDetailRequest request, CancellationToken token);
    ValueTask<CatalogPageResult> QueryAsync(CatalogPageRequest request, CancellationToken token);
}
public sealed record WorkbenchLayoutRequest(string ProfileId, string ProfileRevision,
    string UserScopeRef, int MaxBytes, WorkbenchWaitBudget Budget);
public interface IWorkbenchLayoutStore
{
    ValueTask<ImmutableArray<byte>> LoadAsync(WorkbenchLayoutRequest request, CancellationToken token);
    ValueTask SaveAsync(WorkbenchLayoutRequest request, ImmutableArray<byte> trustedLayoutXml,
        CancellationToken token);
}
public enum WorkbenchCommandKind { VerifyFormat, PreviewExport, Export }
public sealed record WorkbenchCommandRequest(WorkbenchCommandKind Kind, AssetRef ExactRef,
    long BindingEpoch, long SelectionEpoch, string ExpectedAuthorityRevision,
    WorkbenchWaitBudget Budget, Digest? ConfirmedPreviewDigest);
public sealed record WorkbenchCommandResult(string? OperationId,
    OperationObservation? Observation, ReadbackReport? Readback, ExportReceipt? Export,
    WorkbenchExportPreview? Preview,
    ImmutableArray<ModelAssetError> Errors);
public sealed record WorkbenchOperationQuery(string OperationId, Digest ExpectedRequestDigest,
    long BindingEpoch, WorkbenchWaitBudget Budget);
public interface IWorkbenchCommandHost
{
    ValueTask<WorkbenchCommandResult> QueryAsync(WorkbenchOperationQuery request, CancellationToken token);
    ValueTask<WorkbenchCommandResult> CancelAsync(WorkbenchOperationQuery request, CancellationToken waitToken);
    ValueTask<WorkbenchCommandResult> ExecuteAsync(WorkbenchCommandRequest request, CancellationToken token);
    ValueTask<WorkbenchUnbindObservation> DetachAsync(long bindingEpoch,
        WorkbenchWaitBudget budget, CancellationToken token);
}
```

CatalogRow.ContentState/UsageState 是上述闭集投影，宿主提供本用途/AuthorityRevision证据；未知枚举拒绝，Unknown显示“状态未知/狀態未知/Unknown status”，不判Ready。ApprovedForPurpose仅显示具名UsagePurpose的原Owner批准，不能概括为资产通用质量PASS；AuthorityRevision与当前权限水位不一致时只显示Stale/Unknown。模块三语资源覆盖全部枚举与错误；UserScopeRef固定本人布局命名域，不以资产路径生成布局位置。query/cursor/ViewId字符串及每行Ref受Service CoreProfile.MaxStringBytes/MaxInputBytes，PageSize<=Profile.PageSize/MaxRows；缺水位/多次同key/分页重复拒投影。宿主给定query分页语义，控件不将Cursor当SQL或路径。

Bind须UI dispatcher线程调用、校验有限Profile/文化/权限，已Bound时拒绝再Bind；本实例BindingEpoch checked递增（溢出拒绝），每次选Ref/Compare/Permission变化SelectionEpoch递增。Provider异步结果必须同时匹配BindingEpoch/SelectionEpoch/AuthorityRevision才应用；权限撤回原子清空无权详情、取消本绑定等待，不影响其他Host。SetCulture只接受zh-CN/zh-TW/en-US及宿主已登记资源文化，未知文化返回中性en-US资源并保留Culture.Name诊断；全部本模块机器码须有三语资源，原异常不展示。主题由宿主应用，ThemeKey仅绑定识别，本模块不改全局DevExpress主题。

CommandHost冻结本用途Adapter/runtime/challenge/Access和Sink，所有Verify/Export最终调用§5A同一Service；UI不发任意路径/临时参数/隐式授权。Verify期间CommandHost独占Acquire所得父lease、Release/Query，不向UI交native/stream；Cancel/关闭只停止本绑定等待，已接纳任务/lease仍由CommandHost保留并经原Service查询/释放。导入预览/退役/生产采用不是此只读控件命令；宿主工具另使用同Service导入，禁止UI绕过权限。

Unbind先原子禁止dispatch/新命令，退订并取消本绑定等待→调用CommandHost.DetachAsync移交未决operation/resource IDs→清空投影→按有限budget返回。Detached=true只表明UI已脱离，未决资源仍由CommandHost/Service原Owner持有，不等于ResourcesReleased；无法确认接收时Detached=false且控件保留绑定可重试查询，不能Dispose摧毁Owner。迟到callback/provider任务只检查epoch后丢弃投影，CommandHost继续原operation恢复。窗口关闭由宿主先Unbind，窗口本身不Dispose共享Service/Store。XML布局仅LayoutStore提供受信任本人配置且byte上限/版本一致时Restore；加载失败回安全默认，保存失败只显示状态不阻断资产操作。

#### 12.1.2 公开工作区Factory与双STA关闭Owner

控件Bind/SetCulture/SetPermission/Unbind入口都在所属Dispatcher执行；所有同步port/getter无IO/有限，async调用先root登记原Task再观察，dispatcher不做哈希/物化/native。namespace=Wpf，具体factory如下（依赖Service/Core，DevExpress固定引用沿§12.2；未编译声明）：

```csharp
public sealed record WorkbenchUseProfile(string UsagePurpose, AdapterKey Adapter,
    SemanticSnapshot RuntimeSnapshot, AssetRef? ChallengeRef);
public sealed record WorkbenchHostOptions(ModelAssetsScope Scope, string PrincipalRef,
    WorkbenchProfile Profile, WorkbenchUseProfile Use, CultureInfo Culture,
    string ThemeKey, string UserScopeRef, WorkbenchPermission Permission,
    ModelAssetsCleanupProfile Cleanup, OperationBudget ServiceBudget);
public sealed record WorkbenchHostPorts(ICatalogProjectionProvider Catalog,
    IWorkbenchLayoutStore Layout, IAssetExportSink? ExportSink);
public sealed record WorkbenchExportPreview(AssetRef RootRef, DependencyPurpose Purpose,
    string TargetId, ExportConflictPolicy ConflictPolicy, ImmutableArray<ClosureFile> Files,
    long DeclaredBytes, Digest PreviewDigest, string StoreViewId, string StoreViewRevision);
public sealed record WorkbenchHostCreateResult(WorkbenchBinding? Binding,
    IWorkbenchCommandHost? CommandHost, ImmutableArray<ModelAssetError> Errors);
public static class ModelAssetsWorkbenchHost
{
    public static WorkbenchHostCreateResult Create(WorkbenchHostOptions options,
        IModelAssetService borrowedService, WorkbenchHostPorts ports, ModelAssetsHostSlot owner);
}
```

Factory仅装配：Scope/Principal/Profile与borrowedService.SessionInfo一致（服务Profile和UI Profile各具名、不能误当同一种Profile），确认root Slot.Scope、有限Service/Cleanup/UI budgets、Use.Adapter/RuntimeSnapshot完整；Catalog/Layout都必填且无隐藏单例，ExportSink可缺，此时CanExport投影false、Export/Preview明确MA-CAP，不假预览可发布。factory成功Binding使用本模块默认CommandHost，非宿主补猜接口；root事先Reserved并SetCleanupPlan含本CommandHost，构造抛错可由原plan处理，借用Service和ports不Dispose。同CommandHost只绑定一epoch，同实例不能跨Dispatcher/第二控件复用。

ReadDetail结果逐项exactRef/StoreView/AuthorityRevision核验，无权则null+MA-AUTH；未知raw旧descriptor显示历史未验证，不从产品全局cache补。Catalog query/cursor分页语义由其provider实现，但本模块输入/输出字段、MaxRows/Fields/Byte预算、错误与原Task Owner已冻结。模型明细PropertyGrid、TreeList、差异投影都由WorkbenchAssetDetail提供，不反射产品对象；Compare以同一Current selection epoch的两个detail并列，按Files(role,path)/Dependencies/semantics/Layout精确键比较，ordered数组逐index对照，不重算资产事实。不完整View只Stale/Unknown，不能显示“完全一致”。

默认CommandHost.Verify流程：从options冻结UsagePurpose/Adapter/Runtime/Challenge和principal→ResolveExact Runtime→Acquire ContentLease（即刻存本rootslot）→Verify→逐report/EvidenceMode显示→独立cleanup释放parent，保留operation/ref直到原结果确定；与Service相同投影helper生成原IDs/hash。PreviewExport流程：Resolve同目的、核Export authority→按完整files求checked总byte→freeze sink.TargetId/Reject/StoreView，用Service namespace唯一公开 `WorkbenchPreviewProjection.Project(AssetRef rootRef, DependencyPurpose purpose, string targetId, ExportConflictPolicy conflictPolicy, ResolvedClosure closure, CoreValidationProfile profile)`（返回RequestProjectionResult）生成model-workbench-preview-jcs-v1摘要；typed byte/复用Core internal writer仍只在Service，Wpf不加第二friend/public数值writer；preview顶层键固定 `rule/rootRef/purpose/targetId/conflictPolicy/storeViewId/storeViewRevision/files/declaredBytes`，file字段ownerRef+§4.2file，排序先owner Identity ordinal再(role,path)scalar，计数字符串、Ref/digest同Core规则；不含自身digest/时间/UI语言。仅preview计算，不调用Sink.Begin/Publish，不取得长时lease。

Export必须请求ConfirmedPreviewDigest非null且等当前相同Ref/selectionepoch/StoreView/TargetId/完整file preview；无预览/过期/selection/权限变化拒MA-REQ/MA-AUTH，不直接发布。默认CommandHost重新Resolve核同snapshot/重新Authority批准，再ProjectExport/ExportClosure。预览许可不是永久permit，Service在publish前重验fence；操作ID=`UserScopeRef/bindingEpoch/commandSequence/kind`，commandSequence checked递增，登记后Unknown只查同ID；切语言/窗口动作不新ID重发。同按钮双击同commandsequence合并有界waiter而非第二Publish。

所有Catalog/Layout/command异步Task、原Binding/Options/Service/ports/Preview/Source引用进入对应UI root槽；Unbind取消等待→默认CommandHost.DetachAsync原子停本epoch新command→触发独立cleanup释放它取得的parent/permit/watch→保留所有未归还Task与调用ID。Detached=true必须由root确认未决记录已在同进程默认CommandHost受管Owner内，控件投影可清空；不是只返回IDs而无人接管。Detached=false可关闭视图但宿主root不能丢失、可再查同epoch；Window.Closed不得Dispose共享Service。Detach和cleanup只一次，循环观察不二次Release/Dispose；错误并存Primary/Cleanup，不覆盖业务失败。

本地机器码三语后备文案固定如下，资源key使用完整机器码，错误上下文{assetRevision}/{operationId}等由已授权投影限长提供、绝不插裸路径/密钥：

| 机器码 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| MA-REQ-001 | 参数缺失或无效。检查输入。 | 參數缺漏或無效。檢查輸入。 | Missing or invalid input. Check the request. |
| MA-LIMIT-001 / MA-RES-001 | 超出限额。缩小范围或等待资源释放。 | 超出限額。縮小範圍或等候資源釋放。 | Limit reached. Reduce the scope or wait for resources to close. |
| MA-PATH-001 | 文件路径无效或冲突。修正清单。 | 檔案路徑無效或衝突。修正清單。 | Invalid or conflicting file path. Correct the manifest. |
| MA-HASH-001 / MA-CANON-001 | 内容声明不一致。核对文件与版本。 | 內容宣告不一致。核對檔案與版本。 | Content declarations do not match. Check the files and version. |
| MA-DEP-001 | 依赖缺失或冲突。补齐准确版本。 | 相依項缺漏或衝突。補齊確切版本。 | Missing or conflicting dependency. Supply the exact version. |
| MA-FMT-001 / MA-CAP-001 | 当前不支持此操作。检查适配器。 | 目前不支援此操作。檢查介接器。 | This operation is unavailable. Check the adapter. |
| MA-FMT-002 | 格式验证失败。查看读回报告。 | 格式驗證失敗。查看讀回報告。 | Format verification failed. View the readback report. |
| MA-CAS-001 | 此版本已绑定其他内容。使用新版本。 | 此版本已綁定其他內容。使用新版本。 | This revision is bound to other content. Use a new revision. |
| MA-IDEM-001 | 操作编号与原请求不符。查询原操作。 | 操作編號與原請求不符。查詢原操作。 | The operation ID does not match the original request. Check that operation. |
| MA-STORE-UNK-001 | 保存结果待确认。查询原操作。 | 儲存結果待確認。查詢原操作。 | Save result pending confirmation. Check the original operation. |
| MA-CANCEL-001 | 已请求停止。等待资源释放。 | 已要求停止。等候資源釋放。 | Stop requested. Wait for resources to close. |
| MA-TIME-001 | 等待已超时。查询原操作。 | 等候已逾時。查詢原操作。 | Waiting timed out. Check the original operation. |
| MA-AUTH-001 | 当前无权执行。检查用途权限。 | 目前無權執行。檢查用途權限。 | Permission denied. Check access for this use. |
| MA-AUTH-UNK-001 | 权限状态待确认。暂停新操作。 | 權限狀態待確認。暫停新操作。 | Permission status is unknown. Pause new operations. |
| MA-DRAIN-001 | 资源尚未释放。继续查询。 | 資源尚未釋放。繼續查詢。 | Resources are still open. Continue checking. |

三语装配：模块Wpf资源唯一内嵌 `Resources/Strings.zh-CN.resx` / `Resources/Strings.zh-TW.resx` / `Resources/Strings.en-US.resx`，build生成resource，neutral=en-US；键包含全部enum/命令/机器码，不用硬编码控件默认英文。UI资源provider每实例Culture，未知culture按en-US；不得修改CurrentCulture/CurrentUICulture或DevExpress全局language/static主题来切单实例。工作区控件及默认projection全部本地资源，DevExpress chrome采用Host启动时已经冻结的单一框架语言，可能在两Host保留同一种语言；需三语的filter/editor caption由本模块显式本地资源绑定，不宣称DevExpress全局字符串每实例自动切换。文化验证按具体caption键断言，不靠截图假通过。

双STA软件Host：主入口先为UI-A/UI-B各Reserve(root slot)/SetCleanupPlan→各新Thread/SetApartmentState(STA)→线程内建立Dispatcher/Window和new ModelAssetsWorkbench→各factory.Create→Bind返回epoch→Dispatcher.Run；启动Task在StartCall注册**先于Thread.Start**。A用zh-CN、B用en-US，分别绑定自己的CommandHost/Provider/Profile和Service；可以同Store但root slot/Service实例/Scope/permission/culture/selected Ref完全隔离。A中SetCulture(zh-TW)/rapid selection/Permission撤回不能影响B；A Detach/close不得触发B.stop/lease释放。所有控件/图标/布局应用在自己的Dispatcher，测试不向另一线程直接调用依赖对象。

关闭先在各Dispatcher.InvokeAsync中调用Unbind（async任务原Task被root强持）→后台ObserveCleanup有限→Unbind确认投影已detach才能Window.Close/BeginInvokeShutdown；Thread退出另有有限Join观察，未退出根槽保留原Thread/Dispatcher/task，不用Thread.Abort。若Dispatcher已停止/InvokeAsync失败，UI控件不可跨线程补Dispose；root默认CommandHost仍可在后台Detach/Close释放非UI资源，保留UI thread锚点直到实际退出；不会因为Window.Closed就Returned。Wpf.Tests用固定1920×1080 **一个**验证viewport先后呈现A/B窗口（计taskbar/title/status可用区），不同时拼成3840测试、不改物理显示设置。双STA用于接线/文化/隔离生命周期，真实呈现、DevExpress/DPI/UIA/键盘/性能仍待实施验证；公共装配合同不等它运行才存在。

### 12.2 已核对的25.2.3控件组合

本会话没有 dxdocs/匹配WPF技能。官方网页返回403，已实际读本机官方 XML 文档与对应dll版本25.2.3.0；不安装/下载替换依赖。只按下列核实类型/成员定控件，不从名称推导未经查阅属性。

| 区域/行为 | 控件/API与规格 |
|---|---|
| 可恢复停靠 | `DevExpress.Xpf.Docking.DockLayoutManager` + `LayoutGroup/LayoutPanel`；catalog/detail/report命名稳定。SaveLayoutToXml/RestoreLayoutFromXml由宿主LayoutStore调用；仅受信任本用户版本化布局，不直接反序列化导入资产XML；坏布局回安全默认，不改业务操作 |
| catalog/差异 | `DevExpress.Xpf.Grid.GridControl` + `TableView`，DataControlBase.ItemsSource/SelectedItem，DataViewBase.AllowEditing=false；固定列Identity/revision/格式/内容/用途，稳定Ref row key，必要差异按字段分组、排序/多选、显示新增/删除/改变标签 |
| 依赖图投影 | `DevExpress.Xpf.Grid.TreeListControl`，flatten到边路径节点，不把diamond折成只一个父节点；未展开子树延迟从当前closure投影加载，cycles只显示诊断路径不无限递归；点边联动右侧exact target与相关差异 |
| 语义/参数 | `DevExpress.Xpf.PropertyGrid.PropertyGridControl.SelectedObject` 绑定只读投影，PropertyDefinitionBase.IsReadOnly=true；按Format/输入输出/序列/参数来源分组，默认折叠高级项；不能编辑生产参数 |
| 预览与限制 | `DevExpress.Xpf.Editors.Flyout.FlyoutControl` 放导出范围/目标/冲突预览；取消/查询仍是固定可见命令。`DevExpress.Xpf.Core.SuperTip` + SuperTipHeaderItem/SuperTipItem解释限额/恢复，错误缺项不只藏tip |
| 视觉和联动 | 宿主统一主题/强调色；标题20 DIP、正文14、辅助12，8 DIP间距/16 DIP区内边距。错误/未知/已保存用文本+图标，不只颜色；只高亮差异值，缺文件标签就近关联依赖路径。无真实时序数据不造图表/仪表盘 |

Flow/键盘：Tab从Search→Revisions→Files/Dependencies→Compare→Action；Enter打开selected依赖；Ctrl+F检索；Esc先关浮层，独立“取消”命令经CommandHost.CancelAsync请求本operation合作停止；F5读取原选Ref/查询原operation，不能换latest。列长自动省略中间路径、SuperTip完整文本、复制exact Ref；长英文字段换行和列伸缩，不把主动作压出可视区。Tree/Grid异步只更新匹配selection epoch/current authority revision结果；切语言不重跑业务，模块不另放语言下拉。

### 12.3 状态/文案/性能与恢复

UI状态沿PageContract，Ready仅“已选技术资产可查看”不表示用途通过；Busy同时列阶段/已读byte/资源归属，Draining单独文案；Empty区分无选择/过滤无结果/无权查看；Stale维持精确旧选择带水位；Blocked显示依赖行+恢复；RecoverableError只给安全下一步；PermissionDenied清理无权详情且拒迟到返回；Completed表示保存/读回/导出具体完成。

三语资源示例：`模型资产/模型資產/Model assets`；`查看依赖/檢視相依項/View dependencies`；`验证格式/驗證格式/Verify format`；`查询结果/查詢結果/Check result`；`等待资源释放/等候資源釋放/Waiting for resources to close`；`用途已撤回/用途已撤回/Use approval revoked`；`保存结果待确认/儲存結果待確認/Save result pending confirmation`；`资产已保存，尚未用于生产/資產已儲存，尚未用於生產/Asset saved. Not in production use.`。错误给“哪份revision/发生什么/下一步/诊断码”，不展示原异常。

有界分页、按Ref稳定选择、虚拟化Grid/Tree、差异后台计算；dispatcher只应用有限批投影，操作进度可合并，终态通过查询对齐。不一次加载全库/全参数树、不在UI线程哈希/native读取。性能Profile分别测catalog首屏/滚动/差异展开/切语言/选择频繁切换的P95/P99、dispatcher长任务及投影行数；目标来自宿主Profile，缺值NotEvaluated。1920×1080真实WPF/三语/键盘/UIA/DPI行为与停靠恢复均未执行，不能用文档/截图宣称通过。

## 13. 测试矩阵、固定输入与判定

所有本节测试是实施计划，尚未执行。Core契约可先测，Service内存端口只证明软件协议，真实字节耐久/GC/授权/native/WPF另门；不要为文档复核创建产品测试。测试落点见 §18；复用既有来源向量，不另造一组无消费者报告。

| 层 | 必测断言 | 证据/失败处理 |
|---|---|---|
| Core不可变/确定性 | 修改构造 ImmutableArray 所用原数组不影响输入及输出；不同输出不共享可写 byte 缓冲；多个线程/zh-CN/zh-TW/en-US同投影字节和稳定错误 | 入口和输出防御复制，Profile计数先验；default和Empty分别测 |
| 路径/roles | CON/UNC/ADS/非法段/NFC与大小写碰撞；合法同Role多个path和同path多个Role | 只字符串检查，无重解析PASS；文件不一致MA-HASH |
| 语义/身份 | Format/Schema/通道/词表/参数改变digest；Identity/标签/Profile外部绑定不混进新核心 | 改变格式/语义产生新revision；旧协议不受新身份政策影响 |
| Graph | root无依赖/多跳缺项/环/diamond/重复边/同identity异hash；最长路径超限；多Purpose隔离 | graph实含节点；未验证旧refs显式列出；预算耗尽不Complete |
| JCS | RFC属性排序、原始Unicode、数字、null/空/缺省、有序数组、输出UTF8无BOM；重新canonical幂等 | RFC + WebPKI固定输入/输出逐byte，独立Trail-of-Bits/Node仅测试对照，不作生产依赖 |
| 原字节/协议 | byte0→EOF长度/hash；short read/extra trailing bytes/旧rule unknown/mismatch | 真Store读验证；JCS核心hash不冒充原文件hash |
| 封存/恢复 | 同ID同/异请求、revision CAS、所有optional已声明文件失败、Commit后断连、NotFound保留期过 | 无半封存；失败不删除Unknown资源，原ID回执查询 |
| Lease/authority | waiter隔离、parentRelease/childPin竞态、Acquire交付/timeout竞态、撤回fence/过期/断连/续期失败 | Owner唯一、拒新且真退出，Transferred不误Released |
| native/Challenge | 每模型fresh文件→支持参数query→可选challenge→owner线程清理；low signal/多候选由生产者判 | 实际ImageLibDotNet.cv2，clear_dl_model同创建线程；失败仍释放其余资源 |
| Export/迁移 | 完整闭包/Reject冲突、权限重核、publishUnknown、空目录导入、旧→新revision及回退 | 原sink查询；无开发缓存补项；无PartialComplete |
| 事件/关闭 | callback慢/抛异常、队列满SnapshotRequired、旧epoch、Stop重复、Query/Release仍开放、Dispose过早 | 权威可查询，服务关闭不得丢Owner，不能靠sleep证明退出 |
| 两消费者/长稳 | 同公共DLL的匹配/OCR、独立语言/取消/权限；周期性reader/Store失败/重启/缓存淘汰 | native/hold/目录/队列回基线或列明确reconciliation，禁止产品引用 |
| 可选WPF | 固定1920×1080三语长文本、键盘/UIA/停靠恢复、Unknown查询、权限清理和快速切选择 | 真控件行为/视觉分别验收；未做时保持未验证 |

### 13.0 Exe 固定用例 ID 与逐例输出

| ID | 固定输入→必需断言 |
|---|---|
| MC-01 | §5无依赖NCC清单→四入口Valid；root唯一、叶→根仅root；空/null/default分别按MA-REQ失败；失败projection为空/null |
| MC-02 | 同role两path合法、同path两role描述一致合法；不一致MA-HASH；CON.bin/NFC/大小写/父子文件路径冲突MA-PATH |
| MC-03 | 同技术清单只改Identity/Profile/culture→同byte/digest；改单参数/序列顺序/layout target→不同digest；值/schema/状态类型非法MA-CANON或MA-REQ |
| MC-04 | A→B/A→C、B→D/C→B→D→最长3；MaxDepth=2 Invalid，不漏diamond；缺D/环/重复节点/异digest分别MA-DEP |
| MC-05 | §13.1逐byte向量/固定上游golden→严格相等；通用-0为0，语义-0拒绝；duplicate属性、孤立surrogate拒绝 |
| MC-06 | MaxFiles/MaxInputBytes/MaxJsonNodes/MaxCanonicalBytes恰限成功、+1 Invalid；错误超MaxErrors截断但仍Invalid；无递归栈溢出 |
| MC-07 | 两线程及三culture同时四入口→字节/错误相同；两个匹配/OCR声明fixture仅公共DLL；纯Core取消/超时/关闭不适用，不虚构异步状态 |
| MC-08 | 新旧DeclaredRootRef分支；旧节点只列UnverifiedLegacyRefs；null root Layout不含自digest；Runtime依赖同path经不同TargetPath合法，缺/冲突映射失败；其他Purpose不误核缺Runtime |
| MS-01 | 正常seal/resolve/acquire/open/verify/export→原回执、0缺项、正确RequestDigest；同ID同请求无重复副作用、异请求MA-IDEM |
| MS-02 | Commit/Publish后断连，Query NotFound→Unknown且保持；耐久转交后Settled Unknown v1；后确认仅OutcomeReconciled v2，无第二OutcomeSettled |
| MS-03 | 两waiter A取消B继续；父Release与childPin分别先赢→Owner恰一、未退出不Released；Acquire晚返回未交付lease由Service清理 |
| MS-04 | 无法中止reader/端口无视token→有限观察Draining/DrainUnknown；晚到结果仍原Owner清理；真实退出后才Cancelled/TimedOut；已提交仍Succeeded |
| MS-05 | Permit撤回先/后fence、Expired、断连→拒新/按既定在途政策；OCR撤回不删除匹配引用，不能强收caller流 |
| MS-06 | callback阻塞/抛错/队列满→SnapshotRequired可直接读取，QuerySnapshot取同锁LastSequence重订且gap仍拒；停止新接纳而Query/Release可用；Dispose过早立即拒绝，最后Released才成功 |
| MS-07 | 新/已支持旧包导出；metadata原字节逐byte相同；非法索引/缺项/意外文件/同path不同描述/冲突Reject；导入第2项失败不回滚第1项，逐回执重试 |
| MS-08 | 超operation/resource/subscription保留额度→MA-RES，不挤掉未决；过期墓碑NotFound不证未提交；两个无UIHost取消/权限/语言域独立；有限关闭后计数回基线或明确耐久转交 |

所有 expected error 比较完整机器码（表格简称 MA-REQ 等均对应附录A/§7A 的 -001）；Schema 专有参数断言由格式生产者Profile提供，不能把上述合成协议结果当HALCON/存储耐久/用途资格通过。

#### 13.0.1 Service v0.3 与U1新增固定断言

既有MC-01～08及JCS/原Golden接收保持，不重审；S1 Exe `protocol`须执行原MS-01～08以及下列MS-09～16；U1 Exe `workbench-1920x1080`执行MW-01～06。任何case必需项缺失/未完成/超时非0，不用测试数量或返回报告当功能完成。

| ID | 实现者/空Host反例→可判定断言 |
|---|---|
| MS-09 | factory前MaxHosts/Anchors超限、Scope/Principal/Profile错配、未注册cleanup plan→MA-RES/MA-AUTH/MA-CAP，Source.Open/SD factory/effect调用计数0 |
| MS-10 | StartCall同步抛错、factory异步晚到、端口无视token→root先有原Task/ports/stream；等待到期关闭计数0，迟到Service/Runtime/lease入原slot再同plan清理；所有借用未返TryReturn=false |
| MS-11 | 原业务错误+第一个cleanup失败+第二个独立child成功→Primary不被覆盖，Cleanup保留顺序/截断；父DependsOn未退出子时不Dispose；Close重复Run/Dispose计数不增加 |
| MS-12 | RequestCancel和Commit/Publish同时发生→已confirmed成功不改Cancelled，已发未知保持原ID，Cancel等待不新operation；真实退出才OutcomeSettled，重复Cancel不二次effect |
| MS-13 | Simulation Mode进入Production Service/保存器、mode不一致report/receipt→Create/结果MA-CAP/MA-REQ；模拟结果明确Simulation。sameCore不同Scope operation-v2 digest不同、旧v1不补Scope |
| MS-14 | 双工具按§16.2 fault-free及每stage故障→完整链/全部lease真归还或列原reconciliation；OCR字典仍精确hash，M关闭不释放O，无对方产品DLL/静态状态 |
| MS-15 | SD桥用v0.3 Runtime+fake backend：Stage.ExpectedBytes/hash/Format/OperationIdentity与Hasher重算一致；Scope/Generation变化拒绝；范围read先Verify；hold/Release保持同ResourceHandle和版本 | 
| MS-16 | 缺CAS/持久目录/物化/legacy能力逐个故障→对应操作预检MA-CAP，禁止先Source/Stage后才发现不支持Commit；SD SealedNotDurable/Task未Released不模型成功；Query原ID零Seal/Execute/Publish调用；私有Runtime backend不外借 |
| MW-01 | 双STA factory/Bind/zh-CN与en-US，A切zh-TW/主题/selection→B文化/引用/operation不变，全部caption资源按对应实例，不改线程/全局culture |
| MW-02 | Catalog.Detail/分页晚到、Scope/View/AuthorityRevision错配、旧epoch→不更新新detail/权限；Ordered词表差异按index显示，空/未验证不是相等PASS |
| MW-03 | Preview无Sink/错ConfirmedPreviewDigest/目标变/新权限水位→MA-CAP/MA-REQ/MA-AUTH且Sink.Begin/Publish=0；正确确认先重新resolve/authority再唯一Publish |
| MW-04 | Query/Cancel/UI双击：原ID/hash不变，重复只观察，Query不隐式effect；格式慢/取消wait仍保留root原Task/lease至真实退出 |
| MW-05 | Unbind期间command晚到、CommandHost.Detach错误/未接管、Dispatcher已停止→root保留Owner/IDs和UI thread；不得跨STA Dispose控件/共享Service；再Observe不二次释放 |
| MW-06 | 一个固定1920×1080可用viewport先后检查两窗口长三语/键盘/UIA/DPI/停靠/恢复，Unbind→Window.Close→dispatcher shutdown→有限Join；Thread未退出则TryReturn=false，真实运行未执行就标未验证 |

Service bridge-contract套件执行MS-15～16完整子场景，引用SD已冻结Contracts/Runtime及test fake构造，不引用真实PG/FileSystem。未知suite/缺Profile/输入缺项退出非0。测试harness并发闩锁由fixture clock/barrier控制，60s外层进程防卡死，不把阻塞port在deadline后仍活着算成功。

### 13.1 必须锁定的 canonical 反例

- JCS对象 `{"2":0,"10":0}` 期望 `{"10":0,"2":0}`；含 U+1F600/U+E000 属性期望emoji先；业务集合相同字符对按scalar，U+E000先。两种比较器不得共用。
- RFC binary64位模式：`0000000000000001 → 5e-324`、`444b1ae4d6e2ef50 → 1e+21`、`3eb0c6f7a0b5ed8d → 0.000001`、`3eb0c6f7a0b5ed8c → 9.999999999999997e-7`、`8000000000000000 → 0`（JCS底层），而model语义入口该负零Invalid；NaN/±Infinity均错误。
- `{"a":null}`、`{}`、`{"a":""}`三个不同字节；输入两次解码同名 `a`/`\u0061` 拒绝，不允许Dictionary吞掉。字符串 NFC/NFD原字节保留不同，路径碰撞检查另拒绝歧义。
- 文件/依赖集合乱序重排不改变技术摘要；交换字符表/通道/预处理顺序必须改变摘要。Int64 `9007199254740992` 与 `9007199254740993` 的规范字符串摘要不同。
- 旧格式若含 Identity/时间/默认值，其原golden依旧通过原verifier；不能用本页新字段集合产生“新正确旧摘要”。

canonical底层26个RFC数字向量、上游六组输入/输出均逐byte比较；额外极值/随机有限binary64固定seed与数量按Profile明确，缺上游100M外部数据不能计通过。移植数字源码的fast/fallback都触达，double round-trip一致不等于JCS字节一致。所有失效结果同时核Scope/Resource dispositions。

## 14. BenchmarkProfile：计算、I/O和租约使用分别测量

统计口径唯一引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不另复制分位算法。每Profile锁input/hash/规则/schema/adapter/runtime版本，机器资源、并发/冷热/预热/采样数、最低有效样本、总/等待/退出预算、上限、目标来源；阈值由已采纳消费者Profile给出，未提供可诊断测量但NotEvaluated。

| 切片 | 负载维度与必记测点 | 有界资源/失败 |
|---|---|---|
| Core | files、role/path长度、semantic数/JSON深度/节点、graph depth/width/diamond、canonical byte和不同数字分支；ValidateManifest/Refs/Graph/Project分别及总耗时 | MaxFiles（也限制Layout条目）/StringBytes/SemanticFields/JsonDepth/JsonNodes/CanonicalBytes/Errors/GraphLimits；managed alloc/peak；超限Invalid |
| Seal/Resolve | payload文件/byte、重用率、依赖节点/用途、Store RTT、并发CAS、legacy占比；排队、hash、snapshot、hold、stage、commit/query | Stage/hold数量、disk/resident byte、workers/queue；Unknown/失败样本独立列，不能仅挑成功 |
| Lease/Readback | 冷/热物化、分片/字典、runtime/设备、并发waiter、reader初始化/查询/challenge、取消/撤回 | content/read/native/目录/Permit数量、CPU/GPU/native memory、总/退出预算；Draining未知不通过 |
| Export/Recovery | 所选closure大小、source权限、sink吞吐、外部publish/query、进程恢复水位 | 私有暂存/输出bytes、hold/journal；0缺项与原receipt确认，Unknown不假0延迟 |
| WPF可选 | catalog/树深/差异field/三语长度、快速选择频次；首屏、滚动、展开、语言切换、dispatcher批应用 | 显示行数/分页/事件队列预算；文字/状态和延迟目标由UI Profile冻结 |

Core测量由唯一Core.Tests Exe的 `--suite benchmark` 入口执行：按冻结Profile构造一次输入且不计fixture构造→预热→每样本分别计四入口及总链→校验结果→记录完全同步返回时长。Stopwatch.GetTimestamp/GetElapsedTime计时；GC.GetAllocatedBytesForCurrentThread差值只用于同步Core，进程WorkingSet64/PrivateMemorySize64分别记录本次采样峰值和基线（byte）；不得将其称native/GPU精确计数。Service异步使用显式operation/resource计数和进程采样，不沿线程allocation API相减。固定输入重复、每输出验证byte/hash、每样本有ordinal编号；数据由harness交已有验证结果消费方，不提前另造报告/JSON。BenchmarkProfile目标未获采纳时输出NotEvaluated，断言失败/资源未知返回非0；没有目标不得把exit0解释为性能达标。Core.Tests benchmark套件需要已采纳Profile，缺Profile非0并列缺项；不以本次文档输入猜阈值。

普通操作端到端接纳→真实resources Released；若有持久恢复保持转交，转交结果与未决hold另列，不能按“全释放”计通过。Acquire/OpenFile另记接纳→Transferred交付时延，以及Transferred→Released使用期；不能为获得低耗时先释放要交付的lease。报告关联精确Ref/operation/resource/adapter/profile和Outcome，模型字节/密钥不日志化。长稳按Profile周期注入失败/撤回/重启，核计数基线，不把内存GC测点代替Store回收。

## 15. 独立发布、兼容和回退

- 所有工程不导入平台Shell/私表/SDK，不靠产品初始化；Core净依赖BCL，Service显式port，format/WPF分别可选。固定项目根/target/reference见 §18。在空消费仓库单独build/test后再集成，不以平台sln能build证明独立。
- PureCore API仍v0.2，model-core-jcs-v1与原numeric/Golden接收保持；Service本轮v0.3新增Scope/根Owner/cleanup/EvidenceMode，operation rule改model-operation-jcs-v2，未部署v1若以后需重放必须用原v1 verifier，不将Scope补进旧预像。API/Contract/rule/format adapter分别版本化，禁止静默binary-breaking；v0.2替代尚无实现v0.1形状，已部署旧模块以后不能据本次修订无迁移替换。发布记录dll/hash/Contract/rule范围及对应测试/Profile引用，不额外复制事实台账。
- Core发布不附Store/native/UI依赖；Service发布具名端口映射范围；format记录HALCON26.05/AsunImage的既定引用和模型实测支持范围；WPF使用本机25.2.3直接程序集，三语资源随控件、语言由Host切换。无需AsunImage/DevExpress安装/授权/算子存在性门。
- 转换/迁移必须new revision+parent ref；程序采用Owner切引用，回退restore原dll/adapter/schema/ref/runtime，不覆盖旧文件/报告。未知旧格式保留不运行，不能改名或用新JCS重写旧ID。
- 停止/回退过程须Drain所有caller content/native/目录，Unknown提交仍由原Store journal持有；不得删除原资产、用户配置、正式测试或原始证据来使升级通过。

## 16. 最小 Host 与两个真实消费者接入

规划消费者冻结为**2D匹配工程工具**和**OCR工程工具**，二者真实引用共同Core/Service DLL，分别装配匹配与OCR格式adapter、授权和Store。可以调用不同family资产，不能要求OCR reader读取NCC文件，也不能将两个测试进程算成两个产品消费者。

匹配Host：无WPF→Shape/NCC/Deformable已创建字节及声明→seal→resolveRuntime→Acquire→production adapter fresh read/查询→可选匹配challenge→清理native→释放内容lease→查询/drain。模型创建/匹配参数推荐与运行目标都不进资产Service。

OCR Host：无WPF→hdo/字典/标签/通道/预处理精确清单→同链→显式runtime snapshot/set/query→可选OCR Golden challenge→清理handle/字典/物化→释放→drain。字符index保序；缺dictionary/运行快照不从匹配Host或全局缓存补。

两个Host须分别完成原ID幂等/Unknown恢复、取消/撤回/关闭、语言状态隔离、无对方程序集/产品数据库依赖、选旧revision后新label/alias不会漂移。初期Core tests以两种声明fixture验证公开合同，Service simulator可测同软件状态，但仍标记真实消费者适配/格式读回/耐久/WPF未测。

独立验证在实现后按 §18.1 的完整 build/run 命令执行；BCL Exe 不是 dotnet test 项目，不得为了本次文档任务创建空工程。消费者接收先审允许路径/产品事实不写入，再运行对应Core/Service/真实adapter测试；生产用途还须原Owner的资格/程序采用/现场Profile，不能从本模块成功结果推出。

### 16.1 两个完整无 UI Host（Service软件验收消费者）

规划真实消费者仍是匹配工程工具和OCR工程工具。本节是其同构无UI接入合同；C1假端口测试只是软件规格验证，不替代生产者/HALCON实测。公开ToolHost/Root声明唯一见B.5/B.6；消费者不能再造自己的隐藏生命周期。

| 装配/调用 | 匹配工具Host M | OCR工具Host O |
|---|---|---|
| 进程根 | Main先new ModelAssetsHostRoot(已采纳RootProfile,独立TimeProvider)；Reserve("match-tool",Scope)返回slot，再注册外层cleanup计划 | 同契约独立根/slot "ocr-tool"，不会Dispose M的Runtime、Service或语言状态 |
| Scope/身份 | Scope=(明确Tenant,匹配资产namespace,ModelAssets OwnerKey,实际AuthorityId)、Options.PrincipalRef=实际工程工具主体 | 允许同Tenant/namespace共享字节，也可独立namespace；不借M的主体/fence或静态Source；Scope不得来自UI输入 |
| 依赖 | Simulation软件测注册MemoryModelAssetStore、MemoryUsageAuthority、MockMatchFormat、MemoryExportSink、TimeProvider与DiagnosticSink；Production换成§5A.4限定桥/真实用途authority/匹配adapter；所有new纯装配无IO | MockOcrFormat或真实OCR adapter、OCR用途authority、字典/label文件source；接口完全相同，不引匹配产品程序集 |
| 输入 | 已创建Shape/NCC文件声明+schema/必需参数/Format.Layout；root模型role/path/positive长度/hash实值，sourceSnapshot完整；RuntimeSnapshot由匹配生产者提供 | hdo+必需字典/词表/通道/预处理序列，所有Files/Dependencies/Layout显式；schema/runtime由OCR生产者提供，字符序列保序 |
| 完整调用 | ToolHost.Create(options,ports,slot)→RunAsync(ModelAssetToolRequest固定RequestId,输入,AdapterKey,runtime,ChallengeRef,ReadForUse access,Sink,budget)→seal→resolve→Acquire→Verify→export→release→Drain→Dispose | 同完整链；不同AdapterKey和UsagePurpose，须分别核自己的Readback报告/root/runtime/RequestDigest，未请求challenge=NotRequested |
| 正常输出 | 原Seal/Readback/Export和Scope/operation IDs，EvidenceMode明确，Owner.Returned后Root.TryReturn=true；成功不是批准生产 | 同断言；原字典hash/内容、字符sequence、所用runtime/query结果完整；M/O互不覆盖结果 |
| 异常与恢复 | Create/Source.Open同步抛错或seal/verify/export失败→先记录Primary，finally Close独立cleanupBudget→若Unknown/DrainUnknown root保留→Recover原RequestId/SD完整ID；不自动新revision/id | OCR reader慢/字典Query失败/authority撤回触发同路径，readback evidence保留；不取M参数补默认，不强收reader |
| 正常/关闭Owner | 保留原Source/StageTask、SD.Runtime factoryTask、callerLease/根plan；ToolHost只清理其Service；外层plan最后Stop/Dispose本Host拥有SD.Runtime，借用共享Runtime只release自身Session/hold | 任一O关闭不让M父lease失效；共享SD只允许已有公共Runtime/协调Owner，仍不同Scope/会话/操作ID和root槽 |

MemoryModelAssetStore/MemoryUsageAuthority/MockFormat/MemoryExportSink为**Service.Tests内部**确定性实现；factory无外部依赖，按公开接口全能力Simulation返回，用可控异步闩锁决定每个阶段真实退出/晚到/Unknown；port没有假成功分支，资源计数/调用计数可被MS套件消费。既有本文工程绑定中simulator只在tests，不把假Store发布为生产DLL。new stream/source可用固定byte fixture，原文件hash由BCL SHA256计算；Production必须由调用方输入真实模型，不能拿abc fixture当HALCON模型。

从空Host实施步骤固定：只引用Core/ServiceDLL→构造显式Profile/Scope/ports→Root.Reserve→slot.SetCleanupPlan→ToolHost.Create→Project/Run→Recover（若未知）→Close→ObserveCleanup（有限次数）→TryReturn。所有实例构造签名已定义；若Host先创建SD Runtime，则使用SD指导已接收Factory签名及依赖，再桥.Create，原factory Task/root保持先于调用；不因runtime未交付就没有cleanup Owner。

### 16.2 空Host的软件Fixture装配（仅Service.Tests内部）

测试工厂唯一 `Asun.Modules.ModelAssets.Service.Tests.SimulationHostFactory.Create(ModelAssetsHostSlot owner, FixtureFamily family, SimulationFaultPlan faults)`；返回不可变 `SimulationHostFixture(Options, Ports, ToolRequest, Counters)`，family闭集Match/Ocr，faults是测试受控barrier/错误阶段/晚到/是否确定已提交，不来自产品请求。内部具体MemoryModelAssetStore/MemoryUsageAuthority/MockMatchFormat/MockOcrFormat/MemoryExportSink/MemoryContentSource由此一次实例化，无反射、native、UI、DB、文件/网络。各port的记录属于同root槽，Counter只读不可变快照含ActiveReads/Stages/Holds/Permits/Workers/OriginalTasks/Queued/Disposed，生成fixture先KeepAnchor再有界分配。Source每次Open提供只读MemoryStream lease（构造readonly），同ID重复接纳不重复消费。

确定性fixtures：Scope=(fixture-tenant,fixture-models,model-assets,fixture-authority)，principal=fixture-engineer，Owner已Reserved；Match Identity=(fixture-models,ncc-fixture,r1)，模型path=model.ncm、byte=ASCII abc；Ocr Identity=(fixture-models,ocr-fixture,r1)，path=ocr.hdo、byte=ASCII abc，dictionary.txt=ASCII `A\nB`（反斜杠n在这里指1个LF，3 byte）。文件raw SHA256由BCL按上述原bytes计算；Role=Model/Dictionary、Required=true、Format.Layout每source映射相同target、Entrypoint分别model.ncm/ocr.hdo、Dependencies.Empty。Format.Family分别fixture-ncc/fixture-ocr、Id=family、Revision=r1；Producer=(simulation,r1)。Schema=(fixture-schema,r1,SHA256(UTF8 `fixture-schema-v1`))；Semantics.Fields.Empty，RuntimeSnapshot同schema/Fields.Empty（真实模型的required参数由真实生产者schema提供，这些仅fake schema完整）。SourceSnapshot同schema且Fields.Empty；ChallengeRef=null，adapter为(mock-match,r1)/(mock-ocr,r1)，MockFormat核实际bytes/Ref/Layout/参数快照再返回ContentIntegrity.Verified、FormatReadback.Supported、Challenge.NotRequested、EvidenceMode.Simulation；不用abc宣称HALCON可读。

仅测试Profile值固定：CoreValidationProfile=(fixture-core,r1,MaxFiles32,MaxStringBytes1024,MaxSemanticFields64,MaxJsonDepth32,MaxJsonNodes4096,MaxInputBytes1048576,MaxCanonicalBytes1048576,MaxErrors16,GraphLimits(depth16,nodes64,edges128,declaredBytes4194304))。ServiceLimits沿CoreProfile，files32/nodes64/edges128/depth16/sourceBytes4194304/materializedBytes4194304/canonicalBytes1048576/residentBytes8388608/workers4/waiters8/queued8/openLeases16/events64/subscriptions4/retainedOperations64/retainedResources128。RootProfile maxIdBytes1024/hosts2/callsPerHost128/anchorsPerHost128/heldBytesPerHost16777216；Cleanup(execution30s,wait1s,attempts3,interval100ms,errors16)，OperationBudget(total10s,wait1s,上述limits)，Options.DefaultQueryBudget同预算、ObservationRetention=60s、Scope/Principal如上、Simulation、ServiceInstanceId=HostId/r1、ProfileId=fixture-service/Revision=r1、AllowedFormats只本family mock、AllowedLegacyRules.Empty、AllowedDependencyNamespaces.Empty。ToolRequest=RequestId=HostId/request-r1、ExpectedAbsent由Service固定true、Access=(fixture-engineer,fixture-match/fixture-ocr,ReadForUse,null)、ExportSink.TargetId=HostId/export-r1。

这些大小/时间是软件fixture边界、不是设备参数或性能达标阈值。fault-free运行唯一正常路径：预检→stage实读→CAS→Runtime resolve→授权/holds→fresh MockFormat→完整bundle staging→Reject publish→父lease/permit/hold归还→Drain/Dispose→root.TryReturn=true；所有counter归零，保留不可变receipt/技术内容不计活动resource。MockAuthority.FencedAdmission/RevocationWatch=true，通过受控CAS顺序而非sleep切换；MockStore.DurableDependencies/Reconciliation是Simulation协议事实，结果EvidenceMode禁止用于生产。Unknown fault plan必须明确原副作用已发生/未发生/仍未知；查询不消费source/发effect。

## 17. 来源核对、技术选择与复用边界

### 17.1 官方和先进实现的实际读取

已有研究复用 [REF-002 模型资产源码/测试](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#model-assets-research)、[canonical研究](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#model-canonical-readback-source-research)，不重跑无变化的全审。本轮联网读RFC8785与固定C#源码/验证程序，实读本地HALCON26.05相关描述/参数/线程/释放页和DevExpress官方XML；原件只读，未创建第二研究报告或源码快照。

| 来源/固定版本 | 本轮实读和采纳落点 | 强项、限制、依赖/许可 |
|---|---|---|
| [RFC8785](https://www.rfc-editor.org/rfc/rfc8785.txt)，§3.2.2.3/3.2.3及Appendix B；既有原件SHA256 `63d52294eb0e3f0014174288186d388b4ddbf2c67d1ce8af1d9726eb0c3ab240` | UTF16属性排序与ECMAScript数字→§4/9/13；既有严格Unicode/重复字段证据复用 | JCS不定义业务字段/数组集合/文件系统安全，不代替旧协议 |
| [cyberphone/json-canonicalization](https://github.com/cyberphone/json-canonicalization/tree/19d51d7fe467d4706a3ff08adf8a748f29fc21e0)，commit `19d51d7fe467d4706a3ff08adf8a748f29fc21e0` | 实读JsonCanonicalizer的Serialize/String/UTF8/Ordinal/duplicate Add、NumberToJson完整入口、number内部文件头/依赖、两个verify程序和weird输入/输出；§9固定移植numeric调用闭包，§13借鉴golden/二次canonical对照 | .NET源码netstandard2.0，number工程无PackageReference、BCL/Numerics/Diagnostics/Text；canonical工程只ProjectReference number。parser递归/全缓冲/缺预算，故不原样复制；verify-numbers依赖作者本地100M文件，缺数据不能声称通过。根Apache-2.0不覆盖全部源文件：NumberDToA为MPL-2.0+Lucent通知，Builder为MPL-2.0，Fast/Cached/Diy/Double为V8 BSD通知；实现按文件保留通知/义务，不因此阻断已授权设计 |
| Trail of Bits rfc8785.py commit `655cbe02b8761208e3f4cc49e879ab1e328a7dca`，版本0.1.4 | 复用REF-002中实际实现/测试/向量结论作独立校验观察器→§13 | Apache-2.0、运行依赖空，safe-int子集；已形成Dictionary后查不到重复名，无预算/取消。只测试对照，不引Python生产后端 |
| MLflow v3.3.2 commit `9e9abf26f8aa7b546610652fa2556e09f2a83cd2` | 本轮复读models_artifact_repo 45–79的仓库委托、test_sqlalchemy_store 1666–1709 alias测试；其他已核源码/许可/依赖沿REF-002→§5A/11/16 | 精确版本与可变alias分开、显式后端委托可借鉴；版本登记/source不证明字节不变，alias可迁移，测试不证明GC/耐久。Apache-2.0/Python后端生态，不引MLflow产品服务 |
| ONNX v1.19.0 commit `57b9c6a4f6eebb09ae1b34cfb632078518f72832` | 复读external_data_helper 42–79，test_external_data 748–806的路径断言→§4/5A/11/13 | 递归外部location/offset/length闭包思想可借鉴；所读读取函数没证明checksum/短读一致，0/缺失length分支不同，加载后external元数据清除。路径test不证明重解析TOCTOU。Apache-2.0、Python/native/动态requirements，版本/hash/许可详REF-002；不新接ONNX运行库 |
| [HALCON26.05本地官方算子](../../../halcon算子手册/operators/) | §10逐族read/query/set/clear、serialize/deserialize描述/线程；主要页read_dl/deep_ocr的runtime默认和clear_dl_model local scope | 固定文件fresh read主路线；不核验cv2是否有算子。没有实测同样本性能/native/工业准确率，不能称最快或通过 |
| 本机DevExpress25.2.3官方XML（下表） | Dock/Grid/TreeList/PropertyGrid/Flyout/SuperTip及相关成员→§12；对应Docking dll FileVersion25.2.3.0 | 官方网页带/不带version均403；本机官方文档替代网页，未做WPF渲染/行为测量。只记录使用依据，不做安装/兼容/授权门 |

C#原字节SHA-256（同固定commit，代码消费者为未来Core numerical writer和契约测试，不作为产品已实现证据）：

| 固定路径（相对上述GitHub根） | SHA-256 |
|---|---|
| `LICENSE` | `6821faaddedf2d78c95bb6d98b127e9e616097afd2f6bcc34389f000d13ab12d` |
| `dotnet/jsoncanonicalizer/JsonCanonicalizer.cs` | `234982a675b3d6ff12522bcbd823d3e6e0ccbe543029a6ff094da7401a844a29` |
| `dotnet/es6numberserializer/NumberToJson.cs` | `aecd29efdaa1a193e43d5535d4efeb294314b5cbd436c70a8399b6040a0b0f6a` |
| `dotnet/es6numberserializer/NumberDToA.cs` | `f6c215b6787efa3871cf581c08cd645520066704e5a78a9c02856d5c448688cb` |
| `dotnet/es6numberserializer/NumberFastDToA.cs` | `cbe35d5ed16acd05889d6fe9ffd052964cf06ffd831b13f21bfec61f6d548dc3` |
| `dotnet/es6numberserializer/NumberFastDToABuilder.cs` | `82b39967c220a5bed069b36839a7d7993e907a668cc03b356939fd3f79b3742a` |
| `dotnet/es6numberserializer/NumberCachedPowers.cs` | `659174e3f8b2a3c69435538bbf30fa8781a584a209f1a962cd5514a8c0d1fd79` |
| `dotnet/es6numberserializer/NumberDiyFp.cs` | `be3a14af2fec6086f234e3cf06a90edb98cbdbef58447432485b3cac1684c3b5` |
| `dotnet/es6numberserializer/NumberDoubleHelper.cs` | `898c6ceee1025af51ba6abdd2111bc24e209857a23d53601edf699db9a1612df` |
| `dotnet/verify-canonicalization/Program.cs` | `415c26add96f096a1725925976fd6b2e3da4b08b646a5c8e2f8074120c4ad1db` |
| `dotnet/verify-numbers/Program.cs` | `e8d665e7d9e7af8057d96d45614f1f16f3f6febef7f6a6a9655d6a12d2a8bd98` |
| `testdata/input/weird.json` / `testdata/output/weird.json` | `a3a905266bd4a49a969274ea69baa14ee0c4af0ead926d6fa2b7612b4af75387` / `6af595a9aa80110b964b4de3f82a05fa6ae7423005019bacfa2620dddc4e94d1` |

DevExpress官方XML位置为 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`，只读目标版本资料，不是模块可携带的运行依赖路径；部署由宿主直接引用已装程序集。

| XML文件 | SHA-256 |
|---|---|
| `DevExpress.Xpf.Core.v25.2.xml` | `cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196` |
| `DevExpress.Xpf.Docking.v25.2.xml` | `b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f` |
| `DevExpress.Xpf.Grid.v25.2.Core.xml` | `9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba` |
| `DevExpress.Xpf.Grid.v25.2.xml` | `7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd` |
| `DevExpress.Xpf.PropertyGrid.v25.2.xml` | `0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9` |

### 17.2 历史项目和竞品采纳的限制

- 复用 [REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#model-assets-research) 已读ScanSpection原PDF p60/61/64/65/67/68，hash `2b19ea19c2ce1ec93f9515217f1a51ae1b103057337e3d7b9f9efbec9d191187`：主文件+隐藏模板目录和中心库传播风险支持完整闭包/固定版本/独立恢复。其UI不证明内部哈希、事务或生产精度；不重复转换/复制原件。
- AsunControl只读快照 `../../references/project-snapshots/AsunControl/20261004/original/` 下Shape/NCC/Deformable/Variation文档和引擎沿前轮已核证据复用：领域引擎/参数/取消思想可借鉴，WinForms UI耦合、本地目录和bool/string错误不迁成公共Service。
- [AOI模板模型注册指导原件](../../references/project-snapshots/PCBA-AOI/20261004/original/docs/40-development/41-vision-platform/04-recognition/模板模型注册中心开发指导.md) 与AOI.Main来源保留：创建/训练/prepare/执行/保存/读回/challenge分别由生产者/资产/宿主负责，参数编辑是候选；不复制Shape/NCC/线路/焊盘命名或默认阈值，不直接迁旧API/WinForms事件。
- [AsunMeasure只读快照](../../references/project-snapshots/AsunMeasure/20261004/README.md) 的版本参数codec/不可变模型Core/冲突测试思想复用，不迁其搜索结果/页面/生产判断。以上历史来源不与本页并列为活动Module Contract。

### 17.3 本轮具体适配设计的定向官方依据（2026-10-11）

复用§17.1固定源码研究；只追加C.1–C.5真正新增的API依据，不下载产品依赖、不检查AsunImage/DevExpress授权。以下SHA256均是本轮HTTP原HTML bytes（页面可更新，hash标识此次读取），不是产品文件/构建证据。

| 官方原件 | 实读与设计落点 | SHA256/限制 |
|---|---|---|
| [.NET10 ECDsa.VerifyHash](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.ecdsa.verifyhash?view=net-10.0) | 实读ReadOnlySpan+DSASignatureFormat重载及错误边界→C.4 | `2761a40961ee7424d72fba02d5ee2a3b7e03a526564a8b94af096047ba8df297`；不定义业务subject或信任 |
| [.NET10 DSASignatureFormat](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.dsasignatureformat?view=net-10.0) | IEEE P1363固定长度与DER不同→C.4拒DER，不自动尝试多格式 | `56473fb93ae323776e023ce39ab97166a76955496681ae3d7ef4cb0a67646476` |
| [.NET10 ImportSubjectPublicKeyInfo](https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.asymmetricalgorithm.importsubjectpublickeyinfo?view=net-10.0) | DER SPKI及bytesRead核整段→C.4 | `7910c6b17fa31a8f14c5ea5ca30e6e893cdac30d69b1d5c6303cf67705de4f89`；key政策仍外部可信输入 |
| [CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew) | OPEN_REPARSE_POINT只最后组件且不可CREATE_ALWAYS；BACKUP_SEMANTICS目录、不绕ACL；无SHARE_DELETE阻rename→C.2 | `eb3d9c3bb97b71cfdc4c70c8144aabe5bc460f151463a5f1d2b8f04d55ca74ff`；字符串预检不是安全打开 |
| [GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew) | NORMALIZED+VOLUME_NAME_GUID、有限buffer/实际handle路径→C.2 | `2412fe4444c8b32ff8900b3820a9c8731a5a74bf9aa98265bf222bc9dddf7fcd`；需祖先guard/ACL，不能单次路径比较证明无竞态 |
| [GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex) | FileAttributeTagInfo/FileIdInfo→C.2身份/重解析检查 | `7c3b092fcb95180b91ff58f400b5dcfc87b8c574dbbc5f9bdfa60430478e4bd7`；不推断网络文件系统等价 |
| [MoveFileExW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw) | 不REPLACE/COPY、同volume目录rename及WRITE_THROUGH限制→C.3 | `2177bce27264c543b1767d2d9eb8914fe53485b37a53e9159a87d3894dcf78cd`；文档特别说明copy-delete的flush，未代替断电实测 |
| [FlushFileBuffers](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-flushfilebuffers) | 文件flush/缓存/卷管理员权限说明→C.2/C.3 | `e2fbb0c06c610943649a33b61a6766f31f4073ed87894052b77dd514eddc0e91`；不为了flush启用管理员整卷能力，不承诺驱动/硬件掉电安全 |

.NET10 BCL实现对照固定为[dotnet/runtime v10.0.0 commit 60629d14374c56f1cb51819049ad1fa529307f8d](https://github.com/dotnet/runtime/tree/60629d14374c56f1cb51819049ad1fa529307f8d)，实读`src/libraries/System.Security.Cryptography/src/System/Security/Cryptography/ECDsa.cs`的VerifyHash(signatureFormat)校验及VerifyHashCore委托（SHA256 `b696081dc22e362c8b1507b358e58abc4b44cb12b573c82fa37c483ad8807c8f`）、`tests/ECDsaTests.cs`的Array Sign/Verify委托/参数异常测试（`f8b666926412a54c5aab088f8b01ed3df4f2810f7631b1201a450d047f48c548`）、根LICENSE.TXT（`cfc21f5e8bd655ae997eec916138b707b1d290b83272c02a95c9f821b8c87310`，MIT/.NET Foundation）。采用现成BCL而非复制曲线算法；公共API强项是明确格式/委托/异常，不证明本模块subject/信任策略或本机crypto provider已测。未运行上游tests，也不拿该读取升级/替换已冻结.NET10运行环境。

C.5另实读本地HALCON26.05 `query_available_dl_devices/get_dl_device_param/get_system/get_image_size/count_channels/clear_handle`及§10 query/set参数表；固定id/type/name/ai2设备投影、version、尺寸/通道和通用handle规则。设备参数页不提供全球物理序号，不能把本机id当客户设备真值；get/set route不等于训练/推理资格。C.1直接复用[SD唯一指导§6.3/6.6/6.7.3](../storage-database/DEVELOPMENT-GUIDE.md)已冻结的Owner codec、registered SQL/公开PG codec、同事务reference epoch及resolver保护契约，不编造其Runtime方法或私有物理列。

## 18. 逐切片工程、六项准入和剩余集成门

### 18.1 唯一工程与可改范围

表中目录是**未来已授权实现的唯一落点**，本轮只改本指导；未创建工程、编写产品代码、安装包或更改共享入口。命名空间前缀由本页固定，不随宿主改名。

| 切片 | 唯一代码/测试工程（每目录各有同名.csproj） | namespace/依赖 |
|---|---|---|
| PureCore | `src/Modules/model-assets/Asun.Modules.ModelAssets.Core/`；`tests/Modules/model-assets/Asun.Modules.ModelAssets.Core.Tests/` | `Asun.Modules.ModelAssets`；net10.0/BCL，含内部来源数字writer和本合同 |
| Service/协议模拟 | `src/Modules/model-assets/Asun.Modules.ModelAssets.Service/`；`tests/Modules/model-assets/Asun.Modules.ModelAssets.Service.Tests/` | `Asun.Modules.ModelAssets.Service`；net10.0/Core/BCL/显式本模块ports；simulator只在tests，不新增业务Store |
| Store/Authority/Sink映射 | Service同工程中的 `Adapters/`，合同测试在Service.Tests；不另建每端口DLL；SD物化由StorageDatabase工程实现其IModelAssetMaterializer，不让Service反向引用SD桥 | 映射实现由宿主引用已采纳公共契约，禁止私表/连接/句柄泄漏；未接收前不编真实映射 |
| SD限定桥 | `src/Modules/model-assets/Asun.Modules.ModelAssets.StorageDatabase/`；`tests/Modules/model-assets/Asun.Modules.ModelAssets.StorageDatabase.Tests/` | `Asun.Modules.ModelAssets.StorageDatabase`；net10.0/Core/Service/SD.Contracts/SD.Runtime(Hasher)/SD.PostgreSql公共codec；C.1拥有im014 schema，不改SD私表/接口 |
| HALCON格式 | `src/Modules/model-assets/Asun.Modules.ModelAssets.Formats.Halcon/`；`tests/Modules/model-assets/Asun.Modules.ModelAssets.Formats.Halcon.Tests/` | `Asun.Modules.ModelAssets.Formats.Halcon`；net10.0/Core/Service/既定AsunImage，通过ImageLibDotNet.cv2 |
| 可选工作区 | `src/Modules/model-assets/Asun.Modules.ModelAssets.Wpf/`；`tests/Modules/model-assets/Asun.Modules.ModelAssets.Wpf.Tests/` | `Asun.Modules.ModelAssets.Wpf`；net10.0-windows/UseWPF=true/Core/Service/本机25.2.3直接references |

禁止全部切片写产品Shell/ViewModel、其他模块、客户代码、AsunImage内部、共享Contract/私表/原件、tools、AGENTS/架构/入口/进度/登记或skill。未来共享引用/方案装配由主会话串行接收，不由模块作者越权。独立工程不得靠上级平台Directory.Build.props/targets做产品初始化；明确自身target/nullable/references/资源，独立消费build验证；Core.Tests/Service.Tests 固定 Microsoft.NET.Sdk、net10.0、OutputType=Exe、Nullable=enable，仅 ProjectReference 受测工程与其公共依赖、BCL，无 Test SDK/xUnit/NUnit/MSTest/PackageReference；采用确定性断言、固定时钟和异步闩锁。HALCON/WPF 的 Tests 也是具名 Exe，分别引用既定 AsunImage/DevExpress，不借 Core Exe 声称真实验收。

构建/验证命令（未来实施后执行，当前不执行）：

```powershell
dotnet build src/Modules/model-assets/Asun.Modules.ModelAssets.Core/Asun.Modules.ModelAssets.Core.csproj -c Release
dotnet run --project tests/Modules/model-assets/Asun.Modules.ModelAssets.Core.Tests/Asun.Modules.ModelAssets.Core.Tests.csproj -c Release -- --suite contract
dotnet build src/Modules/model-assets/Asun.Modules.ModelAssets.Service/Asun.Modules.ModelAssets.Service.csproj -c Release
dotnet run --project tests/Modules/model-assets/Asun.Modules.ModelAssets.Service.Tests/Asun.Modules.ModelAssets.Service.Tests.csproj -c Release -- --suite protocol
dotnet build src/Modules/model-assets/Asun.Modules.ModelAssets.StorageDatabase/Asun.Modules.ModelAssets.StorageDatabase.csproj -c Release
dotnet run --project tests/Modules/model-assets/Asun.Modules.ModelAssets.StorageDatabase.Tests/Asun.Modules.ModelAssets.StorageDatabase.Tests.csproj -c Release -- --suite bridge-contract
```

Core Exe `contract` 执行 MC-01～08，Service Exe `protocol` 执行 MS-01～16；未知 suite/失败/必需项跳过/未完成返回非0，全部断言完成才0。每case由固定虚拟时钟和可控闩锁推进，外层进程60s超时返回非0（这是 harness 卡死保护，不是产品性能目标）；不靠 Sleep 或无限 await 判断排空。真实 Formats/Wpf.Tests 另分别 `dotnet run --project tests/Modules/model-assets/Asun.Modules.ModelAssets.Formats.Halcon.Tests/Asun.Modules.ModelAssets.Formats.Halcon.Tests.csproj -c Release -- --suite real-formats` 和对应 `Asun.Modules.ModelAssets.Wpf.Tests.csproj -c Release -- --suite workbench-1920x1080`；缺真实样本/Profile/既定程序集引用或UI任务接收时不执行、不报通过。

### 18.2 DEV-GOV-010 §3.1 六项准备结论

主控于 2026-10-10 对下表 PureCore 六项逐项内容接收，PureCore 为 `ModuleCoreImplementationReady`（仅规格准备）；表中“规格已接收”不是运行验收状态。Service S1 六项文档规格亦已由主控于 2026-10-11 独立接收为 `ModuleCoreImplementationReady`（仅规格准备，范围见§18.2.1）。U1 和 SD 限定桥指导内容已接收；真实适配/HALCON/WPF/生产仍保留 `PreparationIncomplete` 和对应门，不由 PureCore 或 S1 接收自动取得准入。

| 六项 | PureCore本轮规格/结论 | 完整模块切片影响 |
|---|---|---|
| 1 边界/第二消费者 | §2/3/16明确匹配+OCR真实复用计划，规格已接收（仅 PureCore） | Service/format共同计划；两个测试进程不是实际消费者验收 |
| 2 精确API/字段/Owner/版本 | 附录A v0.2+§4/9，graph节点/失败投影/immutable/digest不再由开发者补猜，规格已接收（仅 PureCore） | Service §5A–8A/附录B定义Scope/factory/端口/原Task根Owner/有限cleanup/结果/释放/请求投影；真实领域映射待Owner接入；WPF §12.1.1–12.1.2具体默认Host/双STA/关闭合同指导内容已接收，真实WPF验证门保留 |
| 3 无UI最小Host/适配 | §5/A，Core无Store/native/UI，规格已接收（仅 PureCore） | Service显式ports可模拟；Store耐久/Authority fence/Sink/legacy verifier具体映射阻断对应adapter，不阻断Core |
| 4 正常/异常/并发/回退/测试 | §11/13 MC-01～08/A固定断言，纯Core取消/关闭不适用已明示，规格已接收（仅 PureCore） | Service交付/取消/Unknown/撤回/关闭模拟与真实adapter逐层执行；未测试 |
| 5 可执行性能方法 | §14引用统一分位口径，输入/计数/测点/上限/缺目标NotEvaluated，规格已接收（仅 PureCore） | Store/native/lease/WPF实际Profile阈值和样本只影响各切片；无性能通过声明 |
| 6 唯一落点/允许禁止/最小顺序 | §18.1完整build/run+§5固定，规格已接收（仅 PureCore） | §5A.3/16真实Host接收、Formats/WPF各有唯一工程；本轮不授权产品实现 |

PureCore 六项规格已由主控逐条接收；后续发现受影响规格缺失时仍在本页修订，不据会话 accepted 或本次 Core 接收扩大范围。Service S1 的附录B.3–B.6、§16.1–16.2与MS-01～16软件规格已由主控接收，仅该范围为 ModuleCoreImplementationReady；后续实现仍需主控授权与可审计代码基线，**真实Store/Authority/Sink映射**只能在下面对应门关闭后；原“只要Core小就算完整模块好了”结论不成立。

### 18.2.1 Service软件切片 S1 与可选UI装配 U1 六项定位

S1定义为Service v0.3+根Owner/ToolHost+全部本地port的软件协议+Service.Tests确定性内存实现；不包括真实Store/Authority/Sink/HALCON或SD域注册/A1/A2资格。主控于2026-10-11已逐项内容接收S1的软件协议、模拟port、ToolHost与有限Root六项文档规格，**S1为ModuleCoreImplementationReady（仅规格准备）**，不代表编译或运行通过。U1的Wpf/默认CommandHost/双STA公开装配及Owner恢复指导内容已接收；其实际WPF/产品接线资格仍PreparationIncomplete，真实UI门另列。

| 六项 | S1局部确定位置/断言（六项规格已接收） | U1局部确定位置/断言（指导内容已接收） |
|---|---|---|
| 1 职责/两个消费者 | §2/3/16.1，匹配/OCR同DLL无UI链，禁止产品判定/私表 | §12.1.1–12.1.2，两个独立STA/Service/Provider/权限/语言域；可同Store |
| 2 factory/API/Scope/DTO/Owner/版本 | §5A–8A、B.3–B.6；Scope+EvidenceMode+operation-v2、每port原Task/能力/Cancel/Query/资源 | §12.1.1–12.1.2默认Factory/Detail/preview/command Query/Cancel/Unbind，resx三语、epoch/Dispatcher |
| 3 完整无UIHost/依赖与恢复 | §16.1/B.5/B.6，先Reserve/SetCleanupPlan再factory，原Task单次AsTask/强持/有限cleanup；Simulation factory见§16.2 | 双STA先root槽/Thread.Start前Task，窗口关闭后原CommandHost/Task存续，后台Detach不跨线程Dispose |
| 4 正常→错误→取消→Unknown/晚到→关闭 | §11/13 MS-01～16，Scope拒绝、权限fence、原ID/lease、异常并存/晚到接管；SD桥是限定能力 | §13 MW-01～06，双语言/双STA、preview确认/权限撤回、旧epoch、Dispatcher失败和关闭转交 |
| 5 Benchmark可执行测点/资源/来源 | §14 queue/worker/Source byte/Stage/holds/原Tasks/root Slots/cleanup；完整排空P50/P95/P99、缺目标NotEvaluated | §12.3/14固定1920×1080可用区/dispatcher、分页/语言/停靠/P95/P99；无客户值不虚构 |
| 6 唯一工程/Exe命令/允许禁止/调用顺序 | §18.1 Service.Tests BCL Exe protocol MS全部+bridge-contract，§5A.3/16.1/16.2 | §18.1 Wpf.Tests Exe workbench-1920x1080 MW全部；引用本机25.2.3，不写其他模块 |

主控已接收§5A.4基于SD公开DTO的Stage/Query/Read/Hold/Release限定桥指导内容（含显式payload/result codec与引用重算），后续实现按该限定范围执行；领域ModelAssets binding/codec/result/目录按附录C.1实现并注册后才能启用对应Snapshot/CAS/持久保护能力。缺Capability的真实路径必须在任何Source/SD/Sink副作用前拒绝，禁止“先seal文件再发现不能Commit”。SD C0/C1规格已接收不等于物理后端耐久接收；本S1接收同样不授A1/A2/HALCON/WPF/生产资格。

### 18.3 精确剩余规格与实现门

1. storage-database v0.3 C0/C1已接收；§5A.4限定公开桥，附录C.1现已定义本模块登记包、typed输入/结果codec、固定StatementCatalog、同事务CAS和完整根resolver。这些是IM-014内部实现/部署/验证门，不能转成客户待设计；未实现/注册仅拒对应ReadSnapshot/Commit/持久闭包。C.2定义Windows物化及缓存，未具实际安全证据仅拒所需Materialize。A1/A2实际能力归IM-066，具体介质/耐久拓扑/保留期值归部署Owner；不得造SD私表或未公开API。
2. Authority的许可/fence/watch/撤回映射与安全门在B.3/§8A及C.8定位；用途质量/程序采用的事实权仍由产品原Owner和IM-004授权Owner，不转给ModelAssets。C.3已定本地技术包Sink的工厂、独占stage/Reject发布、原journal/回执/重启Query及Unknown禁Abort；实现与物理发布/耐久验证由IM-014负责，部署Owner提供实际目标根。C.4已定detached签名验证，客户安全Owner只提供可信key/生效撤回及签名要求，软件算法不是外门。
3. Service软件状态/端口/Host/cleanup Profile已在B.3–B.6/§16.1–16.2确定；C.5补完整HALCON工厂/逐族最小schema/query/set白名单/Runtime设备描述/challenge接线。真实格式文件、旧创建事实、challenge方法/样本/真值及物理容差由模型生产者/客户验收Owner提供；本模块不把自身schema/worker软件设计留给客户。实际HALCON/Golden/误接受与拒绝/资源/性能/现场尚未验证，按格式与用途逐门接收，不阻通用Core。
4. 旧资产真实Rule/Algorithm/原golden待对应迁入项目提供；既有新JCS/PureCore数字闭包/原Golden接收保持、不重复移植研究；未知时保留不运行，不能发明旧verifier。新JCS路径无需等待全部旧格式资料。
5. U1公开装配/默认CommandHost/双STA/文化/有限Unbind与Owner恢复在§12.1.1–12.1.2已明确，指导内容已由主控接收；真实DevExpress/WPF 1920×1080、三语/键盘/UIA/停靠/DPI/性能与视觉验收尚未执行。未跑UI不表示公共接线未定义；本轮不建UI。
6. 派发代码前按入口规则绑定真实仓库/分支或批准快照；此目录无 Git 元数据不阻断文档规格接收。主控已完成 PKG-033/SM-015/目录/候选合同/计划与来源导航的共享收口，本页不再将其列为待办；历史原件保留。

## 19. 外部接入者自审与当前状态

按外部实现者从新资产构造→Core校验/图/投影→Service seal/Unknown→exact resolve→Acquire/Open/Verify→释放/撤回/Export→Drain/回退走查；两种审查视角的反例与对应类型/状态/测试逐项定位于正文，本轮全范围具体设计见附录C，剩余真实实现/外部输入门见 §18.3。修正了无图节点API、无format/semantic/Layout投影、Role唯一键误拒分片、纯字符串误认链接安全、仅成功投影、租约交付误称全释放、有限队列与不可丢事件矛盾、旧包丢失原预像、请求仅绑定schema而丢参数、无界观察/端口await、测试Host替代真实消费者及dotnet test未执行Exe等缺陷。本轮两轮有限自审分别按实现者正常→异常→恢复、外部空Host→完整装配→关闭走查，补齐Service Scope/Profile/EvidenceMode、SD公开端口限定桥、factory前root Slot/原Task强持/同步阻塞入口、独立cleanup/Primary与Cleanup并存、两个完整无UI ToolHost、默认UI factory/detail/preview/query/cancel/双STA/三语关闭Owner；均为文档推导，不是运行测试。PureCore数字闭包/原Golden与既有六项接收未重审或扩大。

2026-10-11 本轮继续仅编辑唯一指导，新增全批准范围附录C及两轮原会话自审；可决定软件设计欠账已按C.6收口，真正外部门Owner/影响亦在C.6唯一定位。未编译产品/移植数字源码/运行上游测试、真实PG/Store/Authority、Windows guard/Sink、HALCON、WPF、性能或现场验收；保留DesignReview/Prep；PureCore v0.2及S1原ModuleCoreImplementationReady六项规格接收保持，U1/SD限定桥原内容接收保持。附录A未修改；新增adapter/签名/根目录设计不自动取得运行或生产资格。定向结构/引用/范围检查在本原会话执行，不依赖总控代做模块内容审核；实际测试与正式切片开工仍按§18/C.6。

## 附录 A：Module API Contract v0.2 — Pure Core

这是已由主控逐项接收的 PureCore v0.2 规格合同，替代未实施的 v0.1。类型/签名只在此处维护，§4/5 定义行为；PureCore 为 `ModuleCoreImplementationReady`（仅规格准备），不包含 Service 或真实适配准入。不修改旧资产协议，不定义平台全局 DTO。下列代码是**公开声明规格**，省略构造校验/实现体，不冒充已编译示例。

命名空间 `Asun.Modules.ModelAssets`；全部集合为防御复制的 `ImmutableArray<T>`，不是只读接口包装 mutable List。CanonicalValue按具体类型与字段递归相等，数组/对象成员按声明顺序比较，CanonicalNumber按原binary64位模式比较（非法值不因此变合法）；所有含ImmutableArray的record须实现对应typed Equals/GetHashCode按内容比较，不采用ImmutableArray backing-array身份相等。HashCode只用于进程集合，不写入资产/请求digest；Digest规则/算法/原byte全部比较。UTF-8/字节计数都由 Profile 限定，错误内容不能无限增长。

```csharp
public sealed record AssetIdentity(string NamespaceId, string AssetId, string RevisionId);
public sealed record Digest(string RuleId, string Algorithm, ImmutableArray<byte> Bytes);
public sealed record AssetRef(AssetIdentity Identity, Digest Digest);
public sealed record ProducerDescriptor(string Id, string Revision);
public sealed record AssetLayoutEntry(AssetRef? SourceAsset, string Role, string SourcePath, string TargetPath);
public sealed record FormatDescriptor(string Family, string Id, string Revision, string Entrypoint,
    ImmutableArray<AssetLayoutEntry> Layout);
public sealed record AssetFileEntry(string Role, string LogicalPath, bool Required,
    long LengthBytes, Digest FileDigest);
public enum DependencyPurpose { Runtime, RebuildSource, ValidationEvidence }
public sealed record DependencyRef(DependencyPurpose Purpose, string Role, AssetRef Target);
public sealed record AssetContentReference(string Role, string LogicalPath, bool Required,
    long DeclaredLengthBytes, Digest DeclaredFileDigest);

// 封闭 JSON 值联合：构造器限制于本程序集；不接受 object/dynamic/任意 JsonElement。
public abstract class CanonicalValue : IEquatable<CanonicalValue>
{
    private protected CanonicalValue();
    public bool Equals(CanonicalValue? other);
    public override bool Equals(object? other);
    public override int GetHashCode();
}
public sealed class CanonicalNull : CanonicalValue
{
    public CanonicalNull();
}
public sealed class CanonicalBoolean : CanonicalValue
{
    public CanonicalBoolean(bool value);
    public bool Value { get; }
}
public sealed class CanonicalString : CanonicalValue
{
    public CanonicalString(string value);
    public string Value { get; }
}
public sealed class CanonicalNumber : CanonicalValue
{
    public CanonicalNumber(double value);
    public double Value { get; }
}
public sealed class CanonicalArray : CanonicalValue
{
    public CanonicalArray(ImmutableArray<CanonicalValue> items);
    public ImmutableArray<CanonicalValue> Items { get; }
}
public sealed record CanonicalProperty(string Name, CanonicalValue Value);
public sealed class CanonicalObject : CanonicalValue
{
    public CanonicalObject(ImmutableArray<CanonicalProperty> properties);
    public ImmutableArray<CanonicalProperty> Properties { get; }
}

public enum SemanticKind { Boolean, Int64, Binary64, Decimal, String, Enum, Sequence, Object }
public enum SemanticStatus { Explicit, AutoResolved, NotCollected, Unsupported, QueryFailed, Cancelled }
public enum ParameterStage { Build, Serialized, RuntimeRequirement }
public sealed record SemanticField(string Id, SemanticKind Kind, string? Unit,
    CanonicalValue? Value, SemanticStatus Status, string SourceId, string SourceRevision,
    ParameterStage Stage, CanonicalObject Constraints);
public sealed record SemanticSnapshot(string SchemaId, string SchemaRevision, Digest SchemaDigest,
    ImmutableArray<SemanticField> Fields);
public sealed record AssetManifest(AssetIdentity Identity, FormatDescriptor Format,
    ProducerDescriptor Producer, SemanticSnapshot Semantics,
    ImmutableArray<AssetFileEntry> Files, ImmutableArray<DependencyRef> Dependencies);

public sealed record DependencyGraphLimits(int MaxDepth, long MaxNodes, long MaxEdges,
    long MaxDeclaredBytes);
public sealed record CoreValidationProfile(string Id, string Revision, int MaxFiles,
    int MaxStringBytes, int MaxSemanticFields, int MaxJsonDepth, long MaxJsonNodes, long MaxInputBytes,
    long MaxCanonicalBytes, int MaxErrors, DependencyGraphLimits GraphLimits);
public sealed record AssetGraphNode(AssetRef Ref, AssetManifest Manifest);
public sealed record DependencyGraphInput(AssetManifest Root,
    ImmutableArray<AssetGraphNode> Nodes, DependencyPurpose Purpose, AssetRef? DeclaredRootRef);
public sealed record DependencyGraphEdge(AssetIdentity From, DependencyRef Dependency);
public sealed record ModelAssetError(string Code, string FieldPath,
    ImmutableArray<string> Context);
public sealed record CoreValidationResult(bool IsValid,
    ImmutableArray<ModelAssetError> Errors, bool ErrorsTruncated);
public sealed record DependencyGraphResult(CoreValidationResult Validation,
    ImmutableArray<AssetRef> ReachableRefs, ImmutableArray<DependencyGraphEdge> Edges,
    ImmutableArray<AssetIdentity> LeafFirstOrder, ImmutableArray<AssetRef> UnverifiedLegacyRefs);
public sealed record CoreProjectionResult(CoreValidationResult Validation,
    ImmutableArray<byte> CanonicalBytes, Digest? Digest,
    ImmutableArray<AssetContentReference> ContentReferences);

public static class ModelAssetCore
{
    public static CoreValidationResult ValidateManifest(AssetManifest manifest,
        CoreValidationProfile profile);
    public static CoreValidationResult ValidateContentReferences(AssetManifest manifest,
        ImmutableArray<AssetContentReference> references, CoreValidationProfile profile);
    public static DependencyGraphResult ValidateDependencyGraph(DependencyGraphInput input,
        CoreValidationProfile profile);
    public static CoreProjectionResult ProjectCanonicalCore(AssetManifest manifest,
        ImmutableArray<AssetContentReference> references, CoreValidationProfile profile);
}
```

### A.1 构造、输出和投影不变量

- 记录构造器只接不可变字段并赋值，非法/default 值统一在四入口返回错误；入口先限额后复制，不能先递归复制再校验。CanonicalValue 是 abstract class，唯一构造器为 private protected，仅同程序集六种 sealed 值类型可派生；不使用开放的abstract record/copy构造通道；不存在待选工厂或外部 JSON converter。Core 为 static 四入口，无 Initialize/factory/Dispose。
- Value 与 Kind 对应：Boolean→CanonicalBoolean；Int64/Decimal/String/Enum→CanonicalString（Int64/Decimal 另核规范数值词法）；Binary64→CanonicalNumber；Sequence→CanonicalArray；Object→CanonicalObject。序列 elementKind 在 Constraints 必填且每元素匹配；Range/default 等 Constraints 必须遵守 §4.2，不作为执行表达式或回调。
- schema digest 是生产者已冻结 schema 原字节的 `raw-file-sha256-v1` 摘要；Core 不读取 schema 文件，也不把声明当 schema 验证已完成。Source 字符串只作不可变来源标识，不接受 URI 下载。
- `CanonicalNull` 与成员缺失不同；SemanticField.Value 的 C# null 仅表示非有值观察状态并输出 JSON null；Explicit/AutoResolved 必须非 null 且符合 Kind，CanonicalNull 不能冒充有值。CanonicalArray.Items/CanonicalProperty.Value 中 C# null 一律拒绝；真正 JSON null 必须用 CanonicalNull，Constraints 的不适用键也用 CanonicalNull。丢字段拒绝。对象属性名解码后唯一，`a`/转义表示相同名称不能丢失重复；未知顶层字段由构造/解析边界拒绝。
- ReachableRefs 包含新 root 的计算引用或显式旧 DeclaredRootRef；LeafFirstOrder 同一拓扑层按身份 ordinal 元组稳定排序；失败 GraphResult 不提供 Complete 或可执行部分闭包，数组为空，错误 Context 保留定位路径。旧 Ref 声明进入 UnverifiedLegacyRefs 后，图结构可有效但字节/旧摘要完整性未验证。
- Validation.IsValid 当且仅当 Errors.Empty 且非 ErrorsTruncated；失败 Projection 的字节/内容引用为 Empty、Digest 为 null。成功返回完整字节，不返回被截断投影。Invalid 不含 native/Store/用途结果。
- `CoreValidationProfile` 没有 CancellationToken/deadline；同步纯函数只在有限输入下工作，无事件/Initialize/Dispose/隐藏窗口。Core 是库，不在模块里创建另一语言切换入口。

### A.2 错误闭集及恢复

| 码 | Core 含义 | 可判定结果/恢复 |
|---|---|---|
| `MA-REQ-001` | 缺字段/未知枚举/角色唯一键/语义类型或状态不一致 | Invalid；修正声明快照，不能默补默认 |
| `MA-LIMIT-001` | 输入/复制/图/错误/投影预算不满足或 checked 溢出 | Invalid；明确更换 Profile 或缩小请求，不能截断 |
| `MA-PATH-001` | 逻辑路径词法或碰撞 | Invalid；调用方创建新正确清单，Core 不改名 |
| `MA-HASH-001` | 声明摘要规则/长度非法，或内容引用与清单声明不等 | Invalid；只表示声明不一致，不声称实读文件损坏 |
| `MA-DEP-001` | 图缺节点/环/重复快照/同身份不同摘要 | Invalid；修复完整输入，不跟随 latest |
| `MA-CANON-001` | 新规则/schema 投影/JSON 值/数值/Unicode 非法，或未知新投影规则 | 无 Digest；按原协议处理旧资产，未知不得重算 |

`MA-FMT-* / MA-CAS-* / MA-IDEM-* / MA-STORE-UNK-* / MA-CANCEL-* / MA-TIME-* / MA-AUTH-* / MA-RES-*` 仅属 Service/适配切片。机器码→三语文本由宿主资源映射，不把异常堆栈公开。

## 附录 B：Service v0.3 的类型落点与端口接收

本附录把§5A表中的本模块公开字段落为明确C#声明，不创建第二共享Schema。namespace为 `Asun.Modules.ModelAssets.Service`；方法唯一在§5A.1，语义/单位/Owner见§5A–8A。以下本地 request/receipt/port 是设计声明，真实上游映射仍须§18.3接收。

```csharp
public sealed record OperationBudget(TimeSpan TotalTimeout, TimeSpan WaitTimeout, ServiceLimits Limits);
public sealed record ServiceLimits(int MaxFiles, long MaxNodes, long MaxEdges, int MaxDepth,
    long MaxSourceBytes, long MaxMaterializedBytes, long MaxCanonicalBytes, long MaxResidentBytes,
    int MaxConcurrentWorkers, int MaxWaiters, int MaxQueuedOperations, int MaxOpenLeases,
    int MaxEvents, int MaxSubscriptions, int MaxRetainedOperations, int MaxRetainedResources,
    CoreValidationProfile CoreProfile);
public sealed record OperationContext(ModelAssetsScope Scope, string OperationId, Digest RequestDigest, long RequestEpoch,
    string ProfileId, string ProfileRevision, OperationBudget Budget);
public enum AssetAccessAction { ReadHistory, ReadForUse, Export }
public sealed record AssetAccessRequest(string PrincipalRef, string UsagePurpose,
    AssetAccessAction RequiredAction, string? ExpectedAuthorityRevision);
public sealed record AssetImportRequest(OperationContext Context, AssetManifest Manifest,
    bool ExpectedAbsent, SemanticSnapshot SourceSnapshot);
public sealed record LegacyRestoreRequest(OperationContext Context, LegacyAssetDescriptor Legacy,
    bool ExpectedAbsent);
public sealed record ContentInput(string Role, string LogicalPath, long DeclaredLengthBytes,
    Digest DeclaredFileDigest, IAssetContentSource Source);
public sealed record AssetResolveRequest(OperationContext Context, AssetRef ExactRef,
    DependencyPurpose Purpose, AssetAccessRequest Access);
public enum ClosureCompleteness { Complete, Incomplete, Unknown }
public sealed record ResolvedClosure(AssetRef RootRef, DependencyPurpose Purpose,
    string StoreViewId, string StoreViewRevision, ImmutableArray<AssetRef> GraphRefs,
    ImmutableArray<DependencyGraphEdge> Edges, ImmutableArray<ClosureFile> Files,
    ClosureCompleteness Completeness, ImmutableArray<AssetRef> UnverifiedLegacyRefs);
public sealed record ClosureFile(AssetRef OwnerRef, AssetFileEntry Entry);
public sealed record ContentLeaseRequest(OperationContext Context, ResolvedClosure Closure,
    AssetAccessRequest Access);
public sealed record ContentOpenRequest(OperationContext Context, AssetRef OwnerRef, string Role, string LogicalPath);
public sealed record ReadbackRequest(OperationContext Context, string LeaseId,
    string AdapterId, string AdapterRevision, SemanticSnapshot RuntimeSnapshot,
    AssetRef? ChallengeRef, AssetAccessRequest Access);
public enum ExportConflictPolicy { Reject }
public sealed record ExportRequest(OperationContext Context, AssetRef RootRef,
    DependencyPurpose Purpose, AssetAccessRequest Access, IAssetExportSink Sink,
    ExportConflictPolicy ConflictPolicy);
public sealed record OperationCancelRequest(string OperationId, Digest ExpectedRequestDigest,
    string CancelRequestId, OperationBudget Budget);
public sealed record OperationQuery(string OperationId, Digest ExpectedRequestDigest,
    OperationBudget Budget);
public sealed record DrainRequest(string StopOperationId, OperationBudget Budget);
public sealed record ResourceReleaseRequest(string ResourceId, string ReleaseOperationId,
    OperationBudget Budget);
public sealed record ResourceQuery(string ResourceId, string? ReleaseOperationId,
    OperationBudget Budget);
public sealed record ServiceSnapshotRequest(OperationBudget Budget);
public sealed record ServiceSnapshot(string ServiceInstanceId, long LastSequence,
    ImmutableArray<OperationObservation> Operations, ImmutableArray<ResourceObservation> Resources);
public sealed record ServiceSnapshotResult(ServiceSnapshot? Snapshot, ImmutableArray<ModelAssetError> Errors);
public sealed record AssetEventCursor(string ServiceInstanceId, long AfterSequence);
public sealed record ProgressSnapshot(string Stage, long FilesProcessed, long BytesProcessed,
    long NodesProcessed, TimeSpan RemainingBudget);
public enum SubscriptionStatus { Active, SnapshotRequired, Disposed }
public enum ExecutionPhase { Rejected, Accepted, Queued, Running, Draining, Settled }
public enum OperationOutcome { Pending, Succeeded, Failed, Cancelled, TimedOut, Unknown }
public enum ResourceDisposition { None, Draining, Released, Transferred, Reconciliation }
public enum QueryStatus { Found, NotFound, Unknown }
public enum ResourceState { Open, ReleaseRequested, Draining, DrainUnknown, Released }
public enum DrainState { Draining, DrainUnknown, Drained, ResourcesReleased }
public sealed record ResourceRef(string ResourceId, string Kind, string OwnerRef);
public sealed record OperationObservation(string OperationId, Digest RequestDigest,
    long RequestEpoch, ExecutionPhase ExecutionPhase, OperationOutcome Outcome, long OutcomeVersion,
    ResourceDisposition ResourceDisposition, ImmutableArray<string> PendingResourceIds,
    ImmutableArray<string> TransferredResourceIds, ImmutableArray<string> ReconciliationRefs,
    ImmutableArray<ModelAssetError> Errors, QueryStatus QueryStatus, ProgressSnapshot? Progress);
public sealed record ResourceObservation(string ResourceId, string? ReleaseOperationId,
    ResourceState State, ImmutableArray<string> PendingChildren,
    ImmutableArray<ModelAssetError> Errors, QueryStatus QueryStatus);
public sealed record DrainObservation(string StopOperationId, DrainState State,
    ImmutableArray<string> PendingOperations, ImmutableArray<string> PendingResources,
    ImmutableArray<ModelAssetError> Errors);
public sealed record ServiceResult<T>(OperationObservation Observation, T? Value,
    ReadbackReport? Evidence, ServiceEvidenceMode EvidenceMode, ImmutableArray<ModelAssetError> Errors,
    ImmutableArray<ResourceRef> OwnedResources) where T : class;
public enum AssetEventKind { Accepted, PhaseChanged, Progress, ResourceTransferred,
    ResourceReleased, OutcomeSettled, OutcomeReconciled, SnapshotRequired }
public sealed record AssetEvent(string ServiceInstanceId, long Sequence, string OperationId,
    long RequestEpoch, AssetRef? Ref, AssetEventKind Kind, OperationObservation Observation,
    ResourceObservation? Resource, DateTimeOffset RecordedAtUtc);
public enum CommitStatus { ConfirmedCommitted, ConfirmedNotCommitted, Conflict, Unknown }
public sealed record StoredFileReceipt(ClosureFile File, long ActualLengthBytes,
    Digest ActualFileDigest, string ObjectReceiptRef, bool ConfirmedDurable);
public sealed record SealReceipt(AssetRef Ref, string StoreReceiptRef, ServiceEvidenceMode EvidenceMode,
    ImmutableArray<StoredFileReceipt> Files, CommitStatus CommitStatus, Digest RequestDigest);
public enum ContentIntegrity { Verified, Mismatch, Unknown, NotRequested }
public enum FormatReadback { Supported, Unsupported, Unknown, ReadbackFailed }
public enum ChallengeOutcome { NotRequested, Passed, Failed, Unknown }
public sealed record ParameterReadback(string ParameterId, CanonicalValue? Requested,
    CanonicalValue? Observed, SemanticStatus Status, string SourceId, string SourceRevision);
public sealed record ReadbackReport(AssetRef RootRef, ImmutableArray<AssetRef> GraphRefs, Digest RequestDigest,
    ServiceEvidenceMode EvidenceMode,
    string AdapterId, string AdapterRevision, SemanticSnapshot RuntimeSnapshot,
    AssetRef? ChallengeRef, ImmutableArray<ParameterReadback> Parameters,
    ContentIntegrity ContentIntegrity, FormatReadback FormatReadback,
    ChallengeOutcome Challenge, ImmutableArray<string> Limitations, string? ReportReceiptRef);
public enum ExportPublishStatus { ConfirmedPublished, ConfirmedNotPublished, Unknown }
public sealed record ExportReceipt(ResolvedClosure Closure, Digest PackageDigest, ServiceEvidenceMode EvidenceMode,
    string SinkReceiptRef, Digest RequestDigest, ExportPublishStatus PublishStatus);

public interface ContentReadLease : IAsyncDisposable
{
    string ReadId { get; }
    long ActualLengthBytes { get; }
    Digest FileDigest { get; }
    Stream ReadOnlyStream { get; }
    ValueTask<ResourceObservation> ReleaseAsync(ResourceReleaseRequest request,
        CancellationToken cancellationToken);
}
```

### B.1 结果、查询与租约细则

- QueryOperationAsync/QueryResourceAsync 返回 `QueryStatus=NotFound/Unknown` 时Operation/Resource值字段只是请求身份，不生成伪造运行结果：OperationOutcome=Unknown，ExecutionPhase不作为已存在证明，Pending/Transferred/receipt均空；UI先看QueryStatus。Found时才解释状态。不同owner的NotFound不能证明没副作用。
- 参数Readback.Status用§4的六个观察状态，unsupported/cancelled/queryfailed的Observed=null；Requested仍保留原快照，不被actual覆盖。RuntimeSnapshot/schema/ChallengeRef通过ReadbackReport.RequestDigest绑定原操作完整投影（包含快照和challenge引用）；不得只取schema digest代表实际runtime参数。ReportReceiptRef缺省null表示宿主尚未保存，不是报告无效或自动耐久。
- CommitStatus是本项资产的整包提交状态，ConfirmedDurable只表达该文件既定存储耐久回执；只有**全部已列文件耐久+identity/dependencies确认Committed**才SealReceipt成功。不能一项bool代替整包/质量批准；未知仍列原回执/资源。
- 成功Verify的Value必须是已获得的Report，不代表用途获准；发现reader/required参数/challenge错误时adapter PortResult.Value=null/PortResult.Evidence=报告，Service.Value=null但Service.Evidence保留报告，Outcome Failed/Unknown，资源按原Owner清理。完整Report没有challenge可NotRequested，不能Passed。
- Resolve/Snapshot的Files用 `(OwnerRef,role,path)` 唯一键；跨资产相同path不能撞平到根。OpenFile 对 root/依赖文件均须显式 OwnerRef，无默认 root；ContentOpenRequest固定含 `OwnerRef:AssetRef`。Materialization按Format.Layout的TargetPath创建独占空根，根入口和外部location相对关系由layout冻结，不能临时拍平/改名。映射冲突拒绝format读回/export。
- QuerySnapshot在同一状态锁复制权威观察和LastSequence，按OperationId/ResourceId ordinal排序；输入/输出受request预算和Options.Limits共同限制，无法返回完整保留集时Snapshot=null+MA-LIMIT-001，不伪分页Complete。只查询当前ServiceOwner保留范围，过期历史由原Store/Sink查，不获得更大权限。新实例不能续旧cursor，ServiceInstanceId由Host为每次Create唯一提供并记录。
- 事件订阅Status/LastDeliveredSequence须可无阻塞读取；Progress的精确阶段/已处理files/bytes/nodes、预算剩余为OperationObservation附加的不可变ProgressSnapshot，不把percent伪精度当结果。

### B.2 外部映射的类型接收门

§5A.2的Store/Source/Authority/Format/Sink语义必须使用附录B.3给定的本地request/receipt声明；其中hold fence、authority Permit、staging/publish和durable receipt的真实公开DTO不由ModelAssets替共享Owner冻结。本地Service S1软件六项规格已接收，模拟port按本地声明执行；SD已公开限定桥指导内容亦已接收，真实领域binding/Authority/Sink等接入仍按对应门，不能从C#类型名臆造生产SDK接口。真实接入逐条核：明确Snapshot/View稳定性、实读元数据、authority fence顺序、原operation幂等窗口、持久保持/reconciliation、资源Release/Query和新旧规则；每项缺失只阻断对应真实adapter，不把模拟值写进生产事实。


### B.3 本模块 factory 与端口声明

下列是本模块定义的端口，不是声称上游已有同名API。全体集合 immutable，所有输入先依 §4/5A 核 counts/string/byte/enum/budget；所有异步方法均带 token，端口无响应时仍由 Service 有限观察及保留 Owner。PortResult.Value 仅在 Succeeded 时非 null；Evidence:T? 可保留失败/Unknown时已取得的Readback/Commit/Sink报告或原回执，不是成功Value，未知Open/Acquire的lease不能放Evidence向外绕交付。失败/未知可保留 PendingResources/ReconciliationRefs；不得靠异常字符串表示 Unknown。非法装配只返回 CreateResult，端口抛错由 Service 捕获、限长诊断并按是否发出副作用区分 Failed/Unknown。Release 只停止并释放取得的本端口资源，不删除历史资产或已发布包。

```csharp
public sealed record ModelAssetsOptions(ModelAssetsScope Scope, string PrincipalRef,
    ServiceEvidenceMode EvidenceMode, string ServiceInstanceId, string ProfileId, string ProfileRevision,
    ServiceLimits Limits, OperationBudget DefaultQueryBudget, ModelAssetsCleanupProfile Cleanup,
    TimeSpan ObservationRetention,
    ImmutableArray<AdapterKey> AllowedFormats, ImmutableArray<string> AllowedLegacyRules,
    ImmutableArray<string> AllowedDependencyNamespaces);
public sealed record AdapterKey(string Id, string Revision);
public sealed record ModelAssetsPorts(IModelAssetStore Store, IAssetUsageAuthority UsageAuthority,
    ImmutableArray<IModelFormatAdapter> FormatAdapters,
    ImmutableArray<ILegacyDigestVerifier> LegacyVerifiers,
    TimeProvider TimeProvider, IModelAssetDiagnosticSink DiagnosticSink);
public sealed record ModelAssetsCreateResult(IModelAssetService? Service,
    ImmutableArray<ModelAssetError> Errors);
public static class ModelAssetsHost
{
    public static ModelAssetsCreateResult Create(ModelAssetsOptions options, ModelAssetsPorts ports, ModelAssetsHostSlot owner);
}
public interface IModelAssetDiagnosticSink
{
    bool TryWrite(ModelAssetError error);
}
public sealed record PortResult<T>(OperationOutcome Outcome, T? Value, T? Evidence,
    ImmutableArray<ModelAssetError> Errors, ImmutableArray<ResourceRef> PendingResources,
    ImmutableArray<string> ReconciliationRefs) where T : class;
public interface IAssetContentSource
{
    string SourceId { get; }
    ValueTask<PortResult<IAssetSourceReadLease>> OpenReadAsync(ContentSourceRequest request,
        CancellationToken cancellationToken);
    ValueTask<ResourceObservation> QueryResourceAsync(ResourceQuery request,
        CancellationToken cancellationToken);
}
public sealed record ContentSourceRequest(OperationContext Context, string SourceId,
    string Role, string LogicalPath, long MaxReadBytes);
public interface IAssetSourceReadLease : IAsyncDisposable
{
    string ResourceId { get; }
    Stream ReadOnlyStream { get; }
    ValueTask<ResourceObservation> ReleaseAsync(ResourceReleaseRequest request,
        CancellationToken cancellationToken);
}
public sealed record LegacyAssetDescriptor(AssetRef Ref, string MetadataFormatId,
    string MetadataFormatRevision, AssetContentReference Metadata,
    ImmutableArray<AssetFileEntry> Files, ImmutableArray<DependencyRef> Dependencies,
    AssetManifest? StructuralProjection);
public sealed record StoredAssetDescriptor(AssetRef Ref, AssetManifest? Core,
    LegacyAssetDescriptor? Legacy);
public sealed record StoreReadRequest(OperationContext Context, AssetRef RootRef,
    DependencyPurpose Purpose);
public sealed record StoreSnapshot(string ViewId, string ViewRevision, AssetRef RootRef,
    ImmutableArray<StoredAssetDescriptor> Assets);
public sealed record StoreStageRequest(OperationContext Context, StoredAssetDescriptor Asset,
    ImmutableArray<ContentInput> Inputs);
public sealed record StageReceipt(string StageId, string ResourceId,
    ImmutableArray<StoredFileReceipt> Files, StoredFileReceipt? LegacyMetadata);
public sealed record StoreStagedContentRequest(OperationContext Context, StageReceipt Stage,
    string Role, string LogicalPath);
public sealed record StoreCommitRequest(OperationContext Context, StoredAssetDescriptor Asset,
    StageReceipt Stage, ImmutableArray<HoldReceipt> DependencyHolds, bool ExpectedAbsent);
public sealed record StoreCommitReceipt(CommitStatus CommitStatus, SealReceipt? Receipt,
    ImmutableArray<string> ReconciliationRefs);
public sealed record StoreOperationQuery(string OperationId, Digest ExpectedRequestDigest,
    OperationBudget Budget);
public sealed record StoreQueryReceipt(QueryStatus QueryStatus, CommitStatus CommitStatus,
    SealReceipt? Receipt, DateTimeOffset? IdempotencyRetainedUntilUtc,
    ImmutableArray<string> ReconciliationRefs);
public enum HoldStatus { Held, Unknown }
public sealed record StoreHoldRequest(OperationContext Context, ResolvedClosure Closure);
public sealed record HoldReceipt(string HoldId, string Fence, string ResourceId,
    HoldStatus Status, string StoreViewId, string StoreViewRevision);
public sealed record StoreContentRequest(OperationContext Context, HoldReceipt Hold,
    ClosureFile File);
public sealed record MaterializeRequest(OperationContext Context, HoldReceipt Hold,
    ResolvedClosure Closure, FormatDescriptor RootFormat);
public interface IFormatMaterializationLease : IAsyncDisposable
{
    string ResourceId { get; }
    string EntrypointPath { get; }
    ImmutableArray<StoredFileReceipt> VerifiedFiles { get; }
    ValueTask<ResourceObservation> ReleaseAsync(ResourceReleaseRequest request,
        CancellationToken cancellationToken);
}
public interface IModelAssetStore
{
    StoreCapabilitySnapshot DescribeCapabilities();
    ValueTask<PortResult<StoreSnapshot>> ReadSnapshotAsync(StoreReadRequest request, CancellationToken token);
    ValueTask<PortResult<StageReceipt>> StageAsync(StoreStageRequest request, CancellationToken token);
    ValueTask<PortResult<ContentReadLease>> OpenStagedContentAsync(StoreStagedContentRequest request, CancellationToken token);
    ValueTask<PortResult<StoreCommitReceipt>> CommitAsync(StoreCommitRequest request, CancellationToken token);
    ValueTask<StoreQueryReceipt> QueryAsync(StoreOperationQuery request, CancellationToken token);
    ValueTask<PortResult<HoldReceipt>> AcquireHoldAsync(StoreHoldRequest request, CancellationToken token);
    ValueTask<PortResult<ContentReadLease>> OpenContentAsync(StoreContentRequest request, CancellationToken token);
    ValueTask<PortResult<IFormatMaterializationLease>> MaterializeAsync(MaterializeRequest request, CancellationToken token);
    ValueTask<ResourceObservation> ReleaseAsync(ResourceReleaseRequest request, CancellationToken token);
    ValueTask<ResourceObservation> QueryResourceAsync(ResourceQuery request, CancellationToken token);
}
public enum LegacyIntegrity { Verified, Unsupported, Unknown, Mismatch }
public sealed record LegacyVerifyRequest(OperationContext Context, LegacyAssetDescriptor Asset,
    ContentReadLease Metadata, ImmutableArray<ContentReadLease> Content);
public sealed record LegacyVerifyReport(AssetRef Ref, LegacyIntegrity Integrity,
    string VerifierId, string VerifierRevision);
public interface ILegacyDigestVerifier
{
    string RuleId { get; }
    string Algorithm { get; }
    string VerifierId { get; }
    string VerifierRevision { get; }
    ValueTask<PortResult<LegacyVerifyReport>> VerifyAsync(LegacyVerifyRequest request, CancellationToken token);
}
public sealed record FormatReadbackInput(OperationContext Context, ResolvedClosure Closure,
    FormatDescriptor Format, SemanticSnapshot RuntimeSnapshot, AssetRef? ChallengeRef,
    IFormatMaterializationLease Materialization);
public interface IModelFormatAdapter
{
    string AdapterId { get; }
    string AdapterRevision { get; }
    ValueTask<PortResult<ReadbackReport>> ReadBackAsync(FormatReadbackInput request, CancellationToken token);
    ValueTask<ResourceObservation> QueryResourceAsync(ResourceQuery request, CancellationToken token);
    ValueTask<ResourceObservation> ReleaseAsync(ResourceReleaseRequest request, CancellationToken token);
}
public enum RevocationPolicy { DenyNewAndDrain, AllowCurrentUntilExpiry }
public enum PermitStatus { Active, Denied, Revoked, Expired, Unknown }
public sealed record AccessInput(OperationContext Context, ResolvedClosure Closure, AssetAccessRequest Access);
public sealed record UsagePermit(string PermitId, string Fence, string AuthorityRevision,
    DateTimeOffset ExpiresAtUtc, RevocationPolicy RevocationPolicy, string EvidenceRef,
    AssetRef RootRef, string PrincipalRef, string UsagePurpose, AssetAccessAction Action);
public sealed record PermitReceipt(PermitStatus Status, UsagePermit? Permit);
public sealed record PermitChange(string PermitId, string Fence, string AuthorityRevision,
    PermitStatus Status);
public interface IUsagePermitWatch : IDisposable
{
    SubscriptionStatus Status { get; }
}
public sealed record PermitValidationRequest(OperationContext Context, UsagePermit Permit,
    AssetAccessRequest Access);
public interface IAssetUsageAuthority
{
    AuthorityCapabilitySnapshot DescribeCapabilities();
    IUsagePermitWatch Subscribe(UsagePermit permit, Action<PermitChange> callback);
    ValueTask<PortResult<PermitReceipt>> AuthorizeAsync(AccessInput request, CancellationToken token);
    ValueTask<PortResult<PermitReceipt>> ValidatePermitAsync(PermitValidationRequest request, CancellationToken token);
    ValueTask<ResourceObservation> ReleasePermitAsync(ResourceReleaseRequest request, CancellationToken token);
    ValueTask<ResourceObservation> QueryResourceAsync(ResourceQuery request, CancellationToken token);
}
public sealed record ExportBeginRequest(OperationContext Context, string TargetId,
    ExportConflictPolicy ConflictPolicy);
public sealed record ExportEntryRequest(OperationContext Context, string PackagePath,
    long LengthBytes, Digest FileDigest);
public sealed record ExportStageReceipt(string TargetId, string StageId, string ResourceId);
public interface IAssetExportSession
{
    ExportStageReceipt Stage { get; }
    ValueTask<PortResult<StoredFileReceipt>> WriteEntryAsync(ExportEntryRequest request,
        ContentReadLease content, CancellationToken token);
}
public sealed record ExportPublishRequest(OperationContext Context, ExportStageReceipt Stage,
    Digest PackageDigest, ResolvedClosure Closure, UsagePermit Permit);
public sealed record ExportSinkReceipt(ExportPublishStatus PublishStatus, ExportReceipt? Receipt,
    ImmutableArray<string> ReconciliationRefs);
public interface IAssetExportSink
{
    string TargetId { get; }
    ValueTask<PortResult<IAssetExportSession>> BeginAsync(ExportBeginRequest request, CancellationToken token);
    ValueTask<PortResult<ExportSinkReceipt>> PublishAsync(ExportPublishRequest request, CancellationToken token);
    ValueTask<PortResult<ExportSinkReceipt>> QueryAsync(OperationQuery request, CancellationToken token);
    ValueTask<ResourceObservation> AbortAsync(ResourceReleaseRequest request, CancellationToken token);
    ValueTask<ResourceObservation> QueryResourceAsync(ResourceQuery request, CancellationToken token);
}
```

- StoredAssetDescriptor.Core/Legacy 恰一非 null；新 Core Ref 按新投影复算，旧 Legacy.Ref 原样；StructuralProjection 可缺，此时只支持已批准历史保留/原规则验证，不构造伪完整 graph/载入/导出。兼容结构图由 Service 在原 metadata 已验证后明确传入 Core，DeclaredRootRef保留旧身份；旧 Core 校验不宣称旧文件已验证。Core graph 的旧节点映射仅使用能够无损满足结构的StructuralProjection，不能生成假schema/default/Layout。Metadata 为单独内容输入（固定角色 `LegacyMetadata`、逻辑路径 `original-manifest.bin`，不混入 Files）；Legacy.Files不得重复占用上述metadata专用(role,path)键；LegacyRestoreRequest 输入须含此项及全部 Files，metadata/file length/hash 分别核验。metadata 不是新 JCS，且其 raw hash 不能代替旧 Ref.Digest。
- Source lease 不宣称打开时知道实际 hash/length；Stage/读取到EOF后才生成 StoredFileReceipt。MaxReadBytes 限流且读至声明长度后须探查1 byte识别多余内容，额外探查计读取预算；无EOF/超长/short read均失败，不只截流后宣布完整。文件声明最大 long 值等于预算时无法预约额外探查槽则预检拒绝。Store OpenContent 的 ContentReadLease 只有完整 raw length/hash 已校验后才交付；hash未完成只在内部Pending任务，不交消费者。
- Materialization.EntrypointPath 仅 Store→Format 私有端口传递，不持久化、不出事件/报告；Core无真实路径。Store 以 root Format.Layout 物化映射，格式生产者须列足装载实际读取的全部文件，原 entrypoint 必须在独占空根内；不得给HALCON current dir/网络补依赖。目录lease本身归Service，adapter仅借用，native真正退出后才能释放；VerifiedFiles覆盖每个目标映射，实际copy多份按 MaxMaterializedBytes计。
- HoldReceipt/Fence、StageId/ResourceId 和 PermitId 的真实含义由对应Owner实现；ModelAssets不制造GC/质量fence。Permit只有Status=Active且非null有效；Validate必须固定root/principal/purpose/action，改变任何项是新请求。Import/Restore的写入授权在宿主可信服务装配边界，Service不暗授任意调用者注册权；平台导入命令权限另接原Owner。FormatReader的PendingResources只能指该adapter拥有的native/worker资源，物化/Store保持不转给adapter。
- ServiceLimits.MaxFiles在单操作中计所有文件角色项、legacy metadata和包bundle（物理同path可去重，但槽不去重），MaxSourceBytes计实际读/探查、MaxMaterializedBytes计每次实际目标copy；byte/string/output预算均先预约。Core.Tests可用 `InternalsVisibleTo("Asun.Modules.ModelAssets.Core.Tests")` 核底层JCS向量，除此与唯一Service无公开内部入口。
- ResourceRef.Kind闭集为 Stage/StoreHold/ContentLease/ContentRead/Materialization/Permit/PermitWatch/FormatWorker/ExportStage/Subscription；OwnerRef为命名的端口/ServiceInstanceId稳定Owner键，不是AssetRef。所有资源ID必须带owner域、非空限长，重复ID不同Owner拒绝；SourceRead属于ContentRead但Owner为SourceId。bundle写入的StoredFileReceipt.File固定RootRef、Role=Bundle、path=bundle.json，只用于包回执而不加入Manifest.Files。
- ExportSession仅借用读lease，不Dispose它；WriteEntry实际读至EOF与hash后回执，bundle bytes也通过同样受限内存读lease写入，不为bundle开放绕限捷径。sink负责private staging清理，confirmed publish后清理私有stage不得删除外部已发布内容；Unknown禁止Abort。session无用户可变外部路径，TargetId既定绑定由宿主装配，不通过原请求中的机器路径改目标。
- Service及root强持借用端口但不拥有其生命周期，只拥有自己取得的lease/pin/worker/订阅；Dispose不Dispose宿主共享Store/Authority/Sink。Options的DefaultQueryBudget用于不带OperationBudget的内部资源观察保护，不替代操作必填budget。Options.Limits 是本实例共同资源池上限；所有request.Context.ProfileId/Revision须匹配Options，request.Budget.Limits不能超过Options.Limits，各CoreProfile字段也须匹配其具名版本。并发操作的预约合计不得超过实例上限，单操作budget不是每个worker各有一整池。时间预算正且有限，WaitTimeout可大于TotalTimeout但方法观察会以先到者返回；后续OperationQuery用新观察预算不改原操作意图。所有白名单重复键/缺实例/MaxDepth<0/保留期<=0/非有限TimeSpan/超限ID拒Create；没有Format/legacy实例的白名单不接受，空白名单允许纯新资产历史存取，Verify明确MA-CAP。

### B.4 请求摘要的唯一字段投影

请求投影顶层仅 `rule/scope/kind/operationId/requestEpoch/profileId/profileRevision/totalTimeoutTicks/limits/payload`；scope固定键`tenantId/assetNamespace/ownerKey/authorityId`，逐ordinal保留字符串。rule=`model-operation-jcs-v2`；kind固定为下表字符串（不是含Async后缀的C#方法名）；epoch/TimeSpan.Ticks/byte/项计数用Int64规范字符串，枚举用原成员文本。limits包含ServiceLimits所有具名字段（camelCase）和CoreProfile全部字段/GraphLimits，包含其ID/revision；WaitTimeout、token、Context.RequestDigest本身排除。payload固定如下（可空键不省略）；Manifest固定键为`identity/core`（identity=`namespace/id/revision`，core为§4.2）；SemanticSnapshot为完整schema+fields投影，不能只取SchemaDigest。禁止未列字段。

| kind | payload 唯一键/规范值 |
|---|---|
| ImportAndSeal | manifest、expectedAbsent、sourceSnapshot、inputs；inputs按(role,path)scalar排序，每项role/path/lengthBytes/digest/sourceId，无流内容 |
| RestoreLegacy | legacy、expectedAbsent、inputs；legacy含ref/metadataFormatId/metadataFormatRevision/metadata/files/dependencies/structuralProjection，全部绑定原声明；输入排序同上 |
| ResolveExact | exactRef、purpose、access |
| AcquireContentLease | closure、access；closure含RootRef/Purpose/ViewId/Revision/完整GraphRefs/Edges/Files/Completeness/UnverifiedLegacyRefs，JSON键camelCase；GraphRefs含root且只出现一次，按Identity ordinal三元组，Edges先按From ordinal身份再按§9依赖scalar元组，Files先按OwnerRef.Identity ordinal三元组再按(role,path)scalar；UnverifiedLegacyRefs按Identity ordinal，完整Ref仍含digest |
| OpenFile | leaseId、ownerRef、role、logicalPath；leaseId由所属IAssetContentLease注入，不允许相同operation跨lease重放 |
| VerifyFormat | leaseId、adapterId、adapterRevision、runtimeSnapshot、challengeRef、access |
| ExportClosure | rootRef、purpose、access、targetId、conflictPolicy；targetId从请求Sink.TargetId固定读取一次 |

access键固定`principalRef/usagePurpose/requiredAction/expectedAuthorityRevision`；每个 SourceId/TargetId 在本次调用装配时复制并核同一实例不变，改源/目标绑定必须用新ID/新请求。查询/Drain/Release使用各自原ID+摘要核对，不制造业务操作摘要；Release同原ResourceId+ReleaseOperationId，其budget仅观察，不能因观察预算变化改幂等身份。

Core 的有界writer仅经 `InternalsVisibleTo("Asun.Modules.ModelAssets.Service")` 供该唯一Service程序集复用（生产签名若启用，发布配置须同步固定friend public key）；不新增公开通用JCS/数字接口，不调用独立Python/Node进程。

公开投影 helper `ModelAssetRequestProjection` 位于Service namespace，为同步纯函数；均返回下方的 RequestProjectionResult，失败bytes Empty/digest null。方法签名唯一在下方代码块，参数不可省略且profile来自request.Context.Budget.Limits.CoreProfile。计算时忽略请求Context.RequestDigest（构造未提交请求时可填合法32-byte占位），成功后调用方用生成Digest替换Context.RequestDigest再提交；Service同helper复算核相等，不能相信调用方已算。只读取SourceId/TargetId，不调用任何端口、stream或I/O。规则完整性/预算与JCS底层复用Core内部writer，不复刻数字算法。内容Source无法证明实际byte的差异由Stage完整性核验，不因稳定SourceId就省hash。TimeProvider/权限fence/Observations不进入原摘要。查询快照不生成业务请求摘要。结构投影或含义变化用新operation rule/API版本，不沿原ID重写意图。


```csharp
public sealed record RequestProjectionResult(CoreValidationResult Validation,
    ImmutableArray<byte> CanonicalBytes, Digest? Digest);
public static class ModelAssetRequestProjection
{
    public static RequestProjectionResult ProjectImport(AssetImportRequest request, ImmutableArray<ContentInput> inputs);
    public static RequestProjectionResult ProjectLegacyRestore(LegacyRestoreRequest request, ImmutableArray<ContentInput> inputs);
    public static RequestProjectionResult ProjectResolve(AssetResolveRequest request);
    public static RequestProjectionResult ProjectAcquire(ContentLeaseRequest request);
    public static RequestProjectionResult ProjectOpen(string leaseId, ContentOpenRequest request);
    public static RequestProjectionResult ProjectReadback(ReadbackRequest request);
    public static RequestProjectionResult ProjectExport(ExportRequest request);
}
```


### B.5 Service v0.3：Scope、能力及进程根 Owner

本节只补 Service 软件契约，不修改附录A/PureCore v0.2、model-core-jcs-v1、数字闭包及旧Golden。namespace=`Asun.Modules.ModelAssets.Service`。Profile 是宿主明确给定的有限配置，Options/CoreProfile/Source/Adapter/Store不能从窗口或全局设置读取。Scope所有字符串非空、UTF-8限长、ordinal匹配；Manifest root.NamespaceId必须等于Scope.AssetNamespace；外部依赖namespace仅可出现在Options.AllowedDependencyNamespaces白名单。AuthorityId/OwnerKey是装配身份，不代表凭证/批准；PrincipalRef固定为可信Host身份。Scope、operation rule、Profile修订同时绑定请求，不能在原Unknown ID上换租户/目标/版本。

```csharp
public sealed record ModelAssetsSessionInfo(ModelAssetsScope Scope, string PrincipalRef,
    string ServiceInstanceId, string ProfileId, string ProfileRevision, ServiceEvidenceMode EvidenceMode);
public sealed record ModelAssetsScope(string TenantId, string AssetNamespace,
    string OwnerKey, string AuthorityId);
public enum ServiceEvidenceMode { Simulation, Production }
public sealed record ModelAssetsCleanupProfile(TimeSpan ExecutionTimeout, TimeSpan WaitTimeout,
    int MaxQueryAttempts, TimeSpan QueryInterval, int MaxCleanupErrors);
public sealed record ModelAssetsRootProfile(int MaxIdBytes, int MaxHosts, int MaxCallsPerHost,
    int MaxAnchorsPerHost, long MaxHeldBytesPerHost, ModelAssetsCleanupProfile Cleanup);
public enum ModelAssetsHostState { Reserved, Attached, Closing, DrainUnknown, Returned }
public sealed record ModelAssetsRootObservation(string HostId, ModelAssetsScope Scope,
    ModelAssetsHostState State, ImmutableArray<string> PendingCallIds,
    ImmutableArray<string> PendingResourceIds, ModelAssetError? PrimaryError,
    ImmutableArray<ModelAssetError> CleanupErrors, bool CleanupErrorsTruncated);
public sealed record ModelAssetsReserveResult(ModelAssetsHostSlot? Slot,
    ImmutableArray<ModelAssetError> Errors);
public sealed class ModelAssetsHostRoot
{
    public ModelAssetsHostRoot(ModelAssetsRootProfile profile, TimeProvider timeProvider);
    public ModelAssetsReserveResult Reserve(string hostId, ModelAssetsScope scope);
    public ModelAssetsRootObservation Query(string hostId);
    public ValueTask<ModelAssetsRootObservation> ObserveCleanupAsync(string hostId,
        ModelAssetsCleanupProfile budget, CancellationToken waitToken);
    public bool TryReturn(string hostId);
}
public sealed class ModelAssetsHostSlot
{
    public string HostId { get; }
    public ModelAssetsScope Scope { get; }
    public Task<T> StartCall<T>(string callId, Func<ValueTask<T>> start);
    public void KeepAnchor(string anchorId, object borrowedAnchor, long retainedBytes);
    public void SetCleanupPlan(ImmutableArray<ModelAssetsHostCleanupStep> steps);
    public void NotePrimary(ModelAssetError error);
    public ValueTask<ModelAssetsRootObservation> CloseAsync(ModelAssetsCleanupProfile budget,
        CancellationToken waitToken);
}
public sealed record StoreCapabilitySnapshot(string ContractRevision,
    ServiceEvidenceMode EvidenceMode, bool ExactSnapshot, bool Stage,
    bool IdentityCas, bool DurableDependencies, bool ReadHold,
    bool SafeMaterialization, bool LegacyMetadata, bool DurableReconciliation);
public sealed record AuthorityCapabilitySnapshot(string AuthorityId,
    bool FencedAdmission, bool RevocationWatch, bool Renew);
```

IModelAssetStore补唯一同步 `StoreCapabilitySnapshot DescribeCapabilities()`；IAssetUsageAuthority补唯一同步 `AuthorityCapabilitySnapshot DescribeCapabilities()`。getter/Describe必须只读有限装配值、无I/O、无副作用、不得阻塞；真实能力失效在后续操作返回Unknown而非偷偷换端口。Create校验Scope/模式/能力/Profile→把Options/Ports/Service强持入预留slot→才交付Service，无后台task/窗口初始化。Simulation必须要求Store.EvidenceMode=Simulation，所有ServiceResult/Seal/Readback/Export的EvidenceMode跟随实例；模拟耐久标志只表示软件协议回执，不可保存为生产事实。Production不接受Simulation端口。空format/legacy白名单合法但相应Verify/Restore明确MA-CAP；ExactSnapshot/Stage/CAS/Dependencies/ReadHold/Materialize/Reconciliation按每操作最小需求预检，缺能力明确MA-CAP/MA-FMT，不能因为某真实桥不支持就创建第二Store。

Root在应用入口强持（显式实例、非static/global），**先Reserve再创建SD Runtime/Source/Store桥/Service/CommandHost**。Root构造非法Profile/clock抛ArgumentException且未创建任何worker；Query未知hostId抛KeyNotFoundException、TryReturn未知hostId=false，不生成伪Returned。Reserve先核host/Scope每个ID的严格UTF-8 byte≤RootProfile.MaxIdBytes、非空/无控制字符、scope枚举/slot/内存限额，重复HostId冲突，不驱逐未归还槽。KeepAnchor先预约byte/槽，成功后强持可信装配对象/流/ports/task上下文；object只供进程生命周期保持，不进入业务DTO、序列化、反射、参数执行或digest；retainedBytes是受限输入/流缓冲占用、需先验声明，不能填0规避已分配大buffer。Root自身不Dispose借用锚点，具体Close拥有者负责；任务、源流借用和依赖对象未清理不能移除锚点。

StartCall在root锁中先预约callId/记录开始、强持trusted start的输入闭包→释放锁→在MaxCallsPerHost/Service.MaxConcurrentWorkers有限执行槽创建受管dispatch Task并先登记→调用start（不在任何root/存储锁内）→只调用一次ValueTask.AsTask并保留**原Task**→受管dispatch接管晚到结果。公开返回Task是该dispatch结果任务，root同时保留dispatch与真实原portTask（不是WaitAsync包装），同步入口卡住时dispatch仍Pending可查询、输入/源stream/ports强持；不得用新无限线程/Thread.Abort“解决”。同步抛错也写原槽且仍触发清理。task在预留slot受管worker中创建，启动前slot已有owner；不得外部启动后才登记、不调用AsTask两次、不保存WaitAsync包装task代替原task。调用完成可取结果但回调仍须在root受管continuation中接管迟到Service/SD Runtime/lease；调用方法因token/等待timeout离栈，原Task/原Identity/ports/源Stream继续强持。MaxCallsPerHost只允许真实完成且结果资源已接管的槽复用；连续查询耗尽限额时拒绝，不能无限添加日志/task。内部Service worker采用同样的预登记原则，独立于公开等待Task，原operation/context/Source/Sink强持至副作用回执及所有子资源实际归还/耐久转交。

CloseAsync先对本slot正在执行的Service原OperationId调用RequestCancelAsync（固定CancelRequestId=HostId/cancel/原operation），不发新业务ID；已知Committed不改失败。CloseAsync首次原子封新Host调用（Query/Release/cleanup仍开放）并创建唯一受管cleanupTask；重复Close只观察同task。cleanup执行token独立于业务/waitToken，单调ExecutionTimeout固定；到期请求合作停止新的cleanup调用，但已发出的原Release/DisposeTask仍强持，State=DrainUnknown。WaitTimeout/waitToken仅停止本次观察，不清除根槽、不改已提交事实；ObserveCleanupAsync有限MaxQueryAttempts/QueryInterval，仅查同cleanup/资源，不重发effect或Dispose。预算无Infinite/<=0，QueryInterval>0，WaitTimeout<=ExecutionTimeout，MaxQueryAttempts/MaxCleanupErrors正且受Root Profile上限。

清理顺序：禁新→cancel本slot等待/reader执行请求→等原factory/业务task晚到资源接管→逐child read/format pin真实退出→每个caller lease/authority watch/permit单次Release及Query→Service.Drain(固定`HostId/stop`，独立cleanup budget)→所有ResourcesReleased后Service.DisposeAsync一次→宿主拥有的SD runtime/session/ports（若owns）单次有限观察stop/release/dispose；借用共享port不Dispose。每阶段独立try/catch/finally，后阶段仅在其依赖资源已安全退出时运行；某child失败不妨碍释放已独立退出的其他child，但禁止提前释放被其使用的父目录/hold。未有业务异常而仅取消/timeout时PrimaryError按MA-CANCEL-001/MA-TIME-001记录“等待已结束”观察，不拿它覆盖原OperationOutcome；PrimaryError首个业务异常永不被cleanup覆盖，CleanupErrors按发生顺序限长记录，截断仍DrainUnknown。Dispose fault/无限等待不是Returned证据，不重Dispose；查询/资源Released后才移除锚点。TryReturn仅在原Tasks全部观察、资源全部归还或确认移交耐久Owner、cleanup结束、无借用且模式/Owner一致时true，未决不能靠进程GC释放槽。

服务端Unknown持久转交必须明确：StoreCommitReceipt/ExportSinkReceipt的ReconciliationRefs只有原Owner已耐久登记并确认接管时才允许Settled Unknown+Reconciliation；本地task持续Draining不等于移交。不同Owner/错scope/仅接受通知/返回空ref拒转交。查询只读取既有原ID，若外部确认Known则追加OutcomeReconciled；需要写持久对账的工作只由原Store/Sink的受管Owner执行，QueryOperation不能暗触发写/effect。Host移交只交进程资源时root继续持原slot，不把内存Native资源称跨重启持久。软件Simulation提供显式可控回执/CAS/fence/迟到任务，不伪装客户现场。


### B.6 无 UI ToolHost 与唯一cleanup计划

以下namespace仍为Service，只依赖Core/BCL/本地ports，不引用匹配/OCR产品类或HALCON。两个消费者输入由其生产者提供已冻结Manifest/RuntimeSnapshot，Host不替它们补模型参数。公开装配与Owner使用相同Root/Profile，不依赖隐藏窗口。

```csharp
public sealed record HostCleanupContext(string HostId, ModelAssetsScope Scope,
    ModelAssetsCleanupProfile Budget);
public sealed record HostCleanupStepResult(bool Released,
    ImmutableArray<string> PendingResourceIds, ImmutableArray<ModelAssetError> Errors);
public interface IModelAssetsHostCleanupAction
{
    ValueTask<HostCleanupStepResult> RunAsync(HostCleanupContext context, CancellationToken executionToken);
}
public sealed record ModelAssetsHostCleanupStep(string StepId,
    ImmutableArray<string> DependsOn, IModelAssetsHostCleanupAction Action);
public sealed record ModelAssetToolRequest(string RequestId, AssetManifest Manifest,
    ImmutableArray<ContentInput> Inputs, SemanticSnapshot SourceSnapshot,
    AdapterKey Adapter, SemanticSnapshot RuntimeSnapshot, AssetRef? ChallengeRef,
    AssetAccessRequest Access, IAssetExportSink? ExportSink, OperationBudget Budget);
public sealed record ModelAssetToolResult(SealReceipt? Seal, ReadbackReport? Readback,
    ExportReceipt? Export, ImmutableArray<OperationObservation> Operations,
    ModelAssetsRootObservation Owner, ImmutableArray<ModelAssetError> Errors);
public sealed record ModelAssetToolCreateResult(ModelAssetToolHost? Host,
    ImmutableArray<ModelAssetError> Errors);
public sealed class ModelAssetToolHost
{
    public static ModelAssetToolCreateResult Create(ModelAssetsOptions options,
        ModelAssetsPorts ports, ModelAssetsHostSlot owner);
    public ValueTask<ModelAssetToolResult> RunAsync(ModelAssetToolRequest request,
        CancellationToken waitToken);
    public ValueTask<ModelAssetToolResult> RecoverAsync(string requestId,
        OperationBudget observationBudget, CancellationToken waitToken);
    public ValueTask<ModelAssetsRootObservation> CloseAsync(ModelAssetsCleanupProfile budget,
        CancellationToken waitToken);
}
```

ModelAssetsHostSlot.SetCleanupPlan公开签名唯一见B.5，在Reserve后、首个factory/call前只设置一次；未设置plan的StartCall或factory立即MA-CAP，且无副作用；校验StepId唯一、DAG无环/DependsOn存在、计数≤MaxCallsPerHost，action同步入口必须有限；若违反约定卡住，root受管dispatch任务仍强持，有限观察返回DrainUnknown，不在root锁等待、不假cleanup完成。ToolHost.Create在已预留HostLifetime的单步内部组装其Service/CallerLease/Format pin/Permit cleanup DAG并强持（属于原Step.Action私有受管状态，不再次调用SetCleanupPlan），**不调用Host已拥有SD Runtime的Dispose**；RootSlot已配外层plan时内部ToolHost作为预先登记HostLifetime action的一个受管步骤，不能覆盖外层计划。HostLifetime是tests/宿主的有限强持记录，保存原factory/业务/cleanup Tasks、Runtime/Service/CallerLease/Sources/实际 owns 标志和原IDs，action内在这些公开类型上调用明确Stop/Release/Query，不增加另一产品API。Host计划须在建Runtime前注册可引用“未创建/正在Create/已交付”的HostLifetime，失败路径仍可访问原Task。迟到Create结果先写HostLifetime，再触发相同plan，不能直接丢到线程池或被窗口GC收走。

plan动作只拥有自己的资源：Source读lease借用退出→调用方lease→Service.Drain/Dispose→桥自己的Session/hold→Host自有SD runtime.Stop/Dispose（仅owns=true），父步骤DependsOn所有使用它的child。每action的ValueTask单次转原Task，结果Released=true必须含实际释放事实，空PendingIds不作释放证明；抛错写CleanupErrors并阻该父步骤，独立child继续。同Close/Observe不再调用已发RunAsync，迟到结果只更新原step。超过ExecutionTimeout不启动新的依赖步骤、不取消正在排空的IO，不移除slot；Root独立观察直到原Tasks/资源全部已归还，原Disposed失败需明确资源事实查询后才可Returned。Root.TryReturn无stop/task不存在的推断通道。

ToolHost只支持一个RequestId的单条链在途；同Host第二不同RequestId在旧owner未归还前MA-RES，无静态共享cache。每条链OperationIds固定`<RequestId>/seal/resolve/acquire/verify/export`，Scope/Profile/RequestEpoch从Options和本链冻结（epoch=0，无UI选择），所有ID先核MaxStringBytes；不能截断/随机补ID。同RequestId不同manifest/Source/runtime/adapter/purpose/target拒MA-IDEM。链身份不等于资产digest；Recover只观察本Host已登记的原链与原Context，不能重做seal/export、换RuntimeGeneration、重取native/父lease。成功或confirmed失败关闭后重复Run只返回原结果投影，没有第二资源交付；Unknown原ID一直可Recover至ObservationRetention，过期NotFound不证明可重跑。

ToolRequest.Budget.TotalTimeout是整条链的单调deadline，不给每步重新一整份TotalTimeout；每步Context.TotalTimeout=该deadline剩余正TimeSpan并冻结其原投影，等待/恢复预算不改已登记Context。deadline已到禁止新业务步骤，只走独立Cleanup。Run固定步骤：先root强持request/inputs/Source/Sink→为seal构造带合法hash占位Context→ProjectImport并填Digest→root.StartCall一次发ImportAndSeal→Succeeded且SealReceipt绑定全部实际文件才进入Resolve(Runtime,Access)→按ProjectResolve冻结digest→完整resolve→ProjectAcquire/Acquire→将返回父lease即刻存HostLifetime并登记release步骤→ProjectReadback/Verify（runtime/challenge完整）→adapter报告/native真实退出→若ExportSink非null且Access有明确Export证据（重新Authorize），构造单独Export access、ProjectExport并发ExportClosure→父lease.Release及Query→ToolHost.Close执行原Service.Drain/Dispose→返回ModelAssetToolResult。Access.PrincipalRef必须Options.PrincipalRef；用于Verify的ReadForUse用途与Export用途相同但RequiredAction显式改变，授权仍由Authority判断。

任何步骤预检失败不进后步骤；Outcome Pending/Unknown或外层等待timeout只返回当前Operations/Owner，不跳转下一业务步骤、不取消已保存事实。Seal已confirmed而Verify失败时结果保留Seal、Readback evidence和PrimaryError，不删除资产；Export失败/Unknown保留原sink和originalContext/journal。Root cleanup以独立budget处理caller lease，不因waitToken已取消跳过finally；Run中的观察与Close中资源任务都使用原root槽。Run正常也不会关闭宿主借用Store/Authority/FormatAdapter；格式adapter每次worker/native自己的Release与Query由Service执行。

Service任务注册按OperationId/RequestDigest在同Scope接纳锁完成：在启动任何port调用前保留Context/ports/input、资源预约、deadline和原worker Task；重复同ID只附有界waiter观察，不第二启动。预检完成但factory同步抛异常也保留Slot并Close。等待结果只有一个Acquire waiter能获Value，其他观察只有IDs；ToolHost作为唯一caller建立自己的cleanup。ValueTask completion和wait timeout竞争由一次CAS决定交付，晚到未交付lease由worker自行Release并保留原Task直到Released。任何用户回调/diagnostic故障不影响此Owner。



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

## 附录 C：全批准范围的具体适配设计（v0.3.1）

本附录是§5A/9/10的实现细化，不改变PureCore v0.2、Service v0.3请求规则、附录A或既有Golden。模型技术登记、codec/SQL、根目录、物化、缓存、技术签名验证和格式adapter的软件设计由IM-014负责，不能列作客户或“未来Owner”设计门。这里的工厂均先验证有限不可变配置、预约root Slot；除显式Attach/异步操作外不做I/O、不启动窗口。所有实现/验证仍在本模块永久会话内，文档闭合不冒称代码已存在。

### C.1 本模块的SD登记包、数据形状与完整根目录

**登记包与启动次序。** 唯一落点为§18.1的StorageDatabase工程；不是SD新增能力。增加对SD.PostgreSql公共`IPostgreSqlBindingCodec`的引用仅用于固定Owner codec，不取得连接/backend。本模块schema固定`im014`，安装/迁移是Host部署步骤，经SD已批准迁移机制执行；bridge.Create不建表。`ModelAssetsStorageRegistration.Create(options,owner)`返回本模块登记描述、Snapshot/Commit/Roots及OriginInsert/OriginRead各一输入codec、result codec及PG codec、技术binding、reference resolver及根读取/恢复验证登记描述。options含Scope、SD完整StorageScope/Store合法配对Locations、OwnerKey、RawFormat、StorageDomain、Core/Service限额、AllowedDependencyNamespaces、MaxRootSnapshotEntries/Bytes、root页MaxEntries/Bytes、注册锁/语句timeout和cleanup，全部正且有限；Scope.OwnerKey必须与SD.OwnerRegistration一致。注册包另提供只读根Binding（下表第三项），不伪称BridgePorts有第三个字段。所有VersionRef revision固定1，hash为各schema/目录按本节JCS投影的SHA256，发布前由实际包生成并锁定，不填写空hash或用文档版本代替。

注册包先进入SD可信BindingCatalog/ReferenceCatalog，resolver起初Unattached（返回Unavailable，不返回空完整目录）；Host保留原Runtime Create Task，成功后调用登记包的`AttachRuntime(IStorageDatabase runtime)`一次，仅借用并核Scope/Store/登记版本/原实例；再创建桥和Service、最后开放操作。重复同实例Attach幂等，异实例Conflict；关闭先停模型新写/根读取接纳，等待原快照/Session，再停Runtime；resolver从不Dispose借用Runtime。CreateResult精确属性为`Package:ModelAssetsStorageRegistration?`和`Errors:ImmutableArray<ModelAssetError>`；options非法时Package=null。Package公开只读属性`TechnicalBinding/SnapshotBinding/CommitBinding/SnapshotCodec/SnapshotResultCodec/CommitCodec/CommitResultCodec/BindingCatalog/OwnerRegistration/ReferenceResolver`（类型分别按§5A.4和SD公开契约）；上述Create与AttachRuntime是本模块新声明，不是SD方法。

**不可变表与键。** Scope键展开为`tenant_id/site_id/line_id/station_id/device_id/store_id/generation/owner_key/asset_namespace`，均显式predicate；generation为非负bigint，其余受限非空text、COLLATE "C"，不折叠大小写。下列所有表FORCE RLS（tenant_id等于本事务app.tenant_id）、Host角色非Owner/非superuser/无BYPASSRLS；runtime无DDL、UPDATE/DELETE权。引用的scope/store/generation必须与注册范围完全一致。资产修订是opaque text，不转换int。

| 固定表/唯一键 | 列与不变量 | 写入/消费者 |
|---|---|---|
| `im014.asset`；PK=Scope键+asset_id+revision_id | `ref_bytes/descriptor_bytes/files_bytes/edges_bytes/receipt_bytes` bytea（各自严格有界JCS），`digest_rule/digest_algorithm` text、`digest_bytes` bytea、`sealed_epoch` bigint>0、`original_model_operation_id` text、`original_request_digest` bytea、`created_utc` timestamptz；新摘要32bytes，旧摘要遵原规则且受MaxString/输入预算 | Commit唯一写入；只INSERT，原receipt/Ref永不覆盖；created_utc只为登记诊断，不能参与原请求/核心hash；exact read及恢复验证消费 |
| `im014.asset_file`；PK=asset键+role+logical_path | `entry_bytes/object_bytes` bytea；object完整SD.ObjectRef；`is_legacy_metadata` boolean（metadata单独固定role/path）；FK asset；同物理path可多role但ObjectRef必须相同 | 与asset同事务INSERT；Open/完整根枚举/导出；物理ObjectKey不由路径猜 |
| `im014.asset_dependency`；PK=asset键+purpose+role+target_namespace+target_id+target_revision | `target_ref_bytes` bytea及目标Identity的全部列；FK目标asset全键（仅本登记Store/Scope、允许namespace）；purpose闭集三值；目标ref须按字节/结构精确相等 | 同事务INSERT全部显式边，不能只存Runtime或只存当前用途闭包；图读取/备份/GC消费 |

上述表定义就是本模块事实及完整引用目录；不写SD私有operation/authority/catalog表，也不依赖猜测`im066.owner_object_reference`物理列名。SD通过正式OwnerReferenceResolver读取本目录，已注册Transaction的References负责原提交发布保护；二者必须同时接通才DurableDependencies=true。资产无删除API，所有封存行永久作为根；因此sealed_epoch是追加区间起点，没有关闭区间/root_history或“退役即删根”逻辑。若以后批准技术资产删除/保留政策，须新版本定义关闭epoch和持久根历史，不能在本版暗加DELETE。Unknown事务按SD原route/receipt确认，不另事务补行、补引用或改epoch。

**封闭typed输入/结果。** 输入CLR类型为本工程`ModelAssetsSnapshotPayload`与`ModelAssetsCommitPayload`，均sealed record、实现SD.IOwnerStoragePayload；字段分别与StoreReadRequest、StoreCommitRequest及以下投影一一对应，构造只赋值、Encode才有界深拷贝。根resolver私有`ModelAssetsRootsPayload`按同样规则。Encode/GetReferences/Validate严格检查duplicate/unknown字段、IsDefault、UTF-8/深度/计数/总bytes、全部Ref以及scope/store；不能接JsonElement/任意字典。Service内部有界writer通过对本模块StorageDatabase/Formats.Halcon程序集的内部friend façade复用；不另移植数字算法、不新增公开通用JSON接口。

| schema ID（revision=1） | JCS顶层固定键；嵌套规则 | References/结果 |
|---|---|---|
| `im014.snapshot-input-v1` | `rule/scope/store/rootRef/purpose/modelOperationId/modelRequestDigest/maxNodes/maxEdges/maxBytes`；scope为完整SD五ID加model AssetNamespace/OwnerKey，store完整StoreRef；rule等于schema ID；计数规范Int64字符串 | GetReferences=Empty；结果`im014.snapshot-result-v1`键`rule/viewId/viewRevision/rootRef/assets/objects/fileBindings`，assets按Identity ordinal排序，objects按SD ObjectKey排序；fileBindings每项固定`ownerRef/role/path/isLegacyMetadata/object`（含旧metadata，按asset Identity Ordinal再role/path scalar），按对应asset_file原事实生成；descriptor为B.3 Core/Legacy恰一；不返回部分图 |
| `im014.commit-input-v1` | `rule/scope/store/modelOperationId/modelRequestDigest/expectedAbsent/descriptor/stage/dependencyHolds/files/dependencyRefs/objects`；expectedAbsent必须true；descriptor完整StoredAssetDescriptor；stage固定键`stageId/resourceId/files/legacyMetadata`，file固定`file/actualLengthBytes/actualFileDigest/objectReceiptRef/confirmedDurable`（file=ownerRef+entry）；dependencyHolds固定`holdId/fence/resourceId/status/storeViewId/storeViewRevision`，按HoldId ordinal排序；files每项`ownerRef/role/path/entry/object`（metadata另外isLegacyMetadata）；dependencyRefs覆盖全部三Purpose边的TargetRefs，排序/去重；objects覆盖新文件及全部依赖所存文件/metadata | GetReferences返回objects精确集合；结果`im014.commit-result-v1`键`rule/status/ref/receiptBytes`；status只Inserted/Existing/Conflict，Conflict的receiptBytes=null；Existing只能原完整技术绑定一致，保留原receipt |
| `im014.roots-input-v1` | `rule/scope/store/referenceEpoch/maxEntries/maxBytes/afterKey`；读OwnerRegistration中全部登记scope/store逐域，不只当前Service namespace；afterKey显式null或完整asset键+role/path的固定顺序JCS字符串数组（Scope五ID/storeId/generation规范Int64字符串/OwnerKey/namespace/id/revision/role/path），无分隔符拼接；SQL只按这些固定列解码并比较 | 根结果`im014.roots-result-v1`键`rule/referenceEpoch/entries/nextKey/complete`；entry为asset exact Ref+sealed_epoch+完整ObjectRef+role/path；恢复验证另核全descriptor/边/ObjectRef，不凭此窄投影声称恢复成功 |

digest投影仍用`rule/algorithm/hex`；SD.ObjectRef/StoreRef/VersionRef按SD固定canonical字段及枚举/数值编码，不擅自转换成model digest。CommitCodec重建Ref、files与objects集合，比较原StageReceipt（均ConfirmedDurable）与DependencyHolds及全部依赖对象。桥生成的StoredFileReceipt.ObjectReceiptRef固定为`ma-sdobject-v1:`+公开SD.ObjectRef规范bytes的无padding base64url，受MaxStringBytes/输入预算限制；TechnicalBinding同步严格解码并与objects集合exact比对，不读取桥可变字典/私有resolver。其它Store可用自己的回执格式，但此SD TechnicalBinding拒它。依赖对象的归属/原files由command0同事务读取并核并集，不能仅相信输入objects；这些原节点必须已有本Owner资产行。现有Store参数不传SourceSnapshot，因此登记只保存**原model RequestDigest**（它已经绑定SourceSnapshot），不凭空持久化原SourceSnapshot，也不从UI/Source/全局状态补；需要保留完整原请求的Host在原审计链保存其immutable请求，技术资产Store不新造来源事实权威。Stage/CommitRequest不增字段。旧Restore原Ref/metadata原字节规则保持。

**固定StatementCatalog与PG marshal。** ID分别`im014.snapshot-statements-v1`、`im014.commit-statements-v1`、`im014.roots-statements-v1`，以下是审核目录的固定SQL生成规则；参数值来自typed codec，SQL、表名、排序、函数、谓词不来自请求。部署迁移使用完全相同列/约束；完整SD Scope/Store/Owner键使用$1…$8，$9为root AssetNamespace（根枚举时为登记namespace白名单编码），后续参数如下。bytea仅有界技术metadata，不放图像/模型正文；PG公开类型只Text/Int64/Bytea/Boolean/UtcTimestamp。descriptor/source/receipt bytes不以PG jsonb二次规范化，按原bytea存取；短期用有界JSON文字参数的recordset只展开ID/计数/hex，不改变持久canonical bytes。

| binding/command | 固定语句及参数顺序 | result与限额 |
|---|---|---|
| Snapshot，Read/Query/RepeatableRead，一个Read命令 | 全键$1…$8，$9 root namespace，$10 root id Text、$11 revision Text、$12 exact ref Bytea、$13 purpose Text、$14 maxNodes+1 Int64。固定`SELECT ... FROM im014.read_snapshot_v1($1,...,$14,...)`，只读SECURITY INVOKER函数，按下段有界队列遍历；参数另绑定maxEdges/maxFiles/maxBytes，root才用$9 namespace限制，目标须在registration白名单并核同SD Scope/Store/Owner。返回descriptor/ref和同view的file/object/边原bytea hex投影；不使用UNION ALL或全图递归后才LIMIT | maxRows=maxNodes；截断、缺root/目标或合计bytes/边超限整体Fault；仍使用Core图验环/最长深度，不把UNION去重当图正确；返回列`asset_id Text/revision_id Text/ref_bytes Bytea/descriptor_bytes Bytea/files Text/dependencies Text` |
| Commit，Transaction/Transaction/Serializable，command0 Read | $10 asset id、$11 revision、$12 expected ref bytes、$13 dependency key/ref有界recordset Text。读取当前Identity及所有三Purpose exact dependencies `FOR KEY SHARE`，ORDER BY完整键；不存在根合法，缺目标/不同Ref拒绝，不临时补依赖 | maxRows=MaxEdges+1；返回`kind Text/ref_bytes Bytea/receipt_bytes Bytea/objects_bytes Bytea`，零目标可空；每个目标的原file/metadata对象集合由同事务核对objects |
| Commit command1 Mutation | 全键$1…$9，$10 asset id Text、$11 revision Text、$12 Ref Bytea、$13 descriptor Bytea、$14 files Bytea、$15 edges Bytea、$16 receipt Bytea、$17原operation Text、$18原request digest Bytea；created_utc在固定SQL用transaction_timestamp()取得，不由同步codec取墙钟。固定顶层`INSERT INTO im014.asset ... SELECT ... current_setting('app.im066_reference_epoch',true)::bigint ... WHERE NOT EXISTS(完整Scope/Store/Owner/namespace/id/revision原Identity) ON CONFLICT DO NOTHING`；AFTER INSERT trigger按本行已保存files_bytes/edges_bytes展开子表（见下段） | 实际AffectedRows精确0/1；禁止将RETURNING rows当RecordsAffected。Conflict并发不改旧行；所有写与SD技术receipt/head/发布保护同事务，E严格>0，不读Token.ReferenceEpoch作新E |
| Commit command2 Read | 全键+原asset id/revision；重读已封asset/ref/receipt及完整file/边；逐字段比较expected，返回原receipt或Conflict | maxRows=1，result codec在commit前验证；不一致返回Conflict业务结果且无本次Owner写入；bridge映射MA-IDEM/Conflict |
| Roots，Read/Query/RepeatableRead，一个Read命令 | 全键（namespace谓词覆盖OwnerRegistration全部白名单，不局限一个Service）+$10原ReferenceEpoch Int64、$11 afterKey Text（有界key编码）、$12 limit+1 Int64；`asset JOIN asset_file WHERE sealed_epoch<=$10 AND full_key>afterKey ORDER BY全键,role,path COLLATE "C" LIMIT $12` | 每页多读1项判next，entries从0计sequence；不能用空页推断全部scope/store完整。原token/cut不变；Owner枚举所有登记组合后才Complete |

Snapshot的`read_snapshot_v1`实现固定只读PL/pgSQL局部有界数组（无临时表/DDL/SECURITY DEFINER）：核精确root→FIFO frontier/visited Identity全三元组（含namespace，ordinal精确相等）→每次取一个节点，只读其asset及所选purpose目标行，LIMIT=min(剩余MaxEdges+1,注册MaxEdges+1)→在新增edge/visited/文件或原bytea输出前checked核MaxNodes/Edges/Files/总UTF8+metadata bytes→入队未访问目标。每次目标Ref exact核已存Ref、允许namespace；缺根/目标、反向同Identity不同Ref、任一限额或timeout整体错误，无半个成功快照。file/metadata子行读取同样LIMIT剩余额+1，先计octet_length再取bytes，不用无界json_agg；每条JSON传输只含固定已核列，decoder在发布StoreSnapshot前按.NET Identity Ordinal及Core的scalar角色/路径排序，PG COLLATE "C"仅物理读取顺序，不当成UTF16 Ordinal排序。visited去重只防遍历无限，Core仍独立判环/重复边/最长深度；函数可读取完有界圈并交Core拒绝。函数与其它读取在SD原RepeatableRead事务，语句timeout扣原deadline；不会在SQL循环为每步重置timeout/另借连接。此路线确保预算在遍历/聚合前核，不能用外层LIMIT冒称服务器未遍历全图。注册StatementCatalog只调用固定函数，部署包checksum绑定函数源码/shape，修改其路由必须新VersionRef。

Commit command1固定顶层INSERT，不使用末尾SELECT/RETURNING伪造RecordsAffected。迁移同时登记`AFTER INSERT FOR EACH ROW`触发器`im014.insert_asset_children_v1`；它从本行原规范files_bytes/edges_bytes用`convert_from(...,'UTF8')::jsonb`**仅提取**闭集固定列，原规范bytea仍保留，不从jsonb重算Ref。fields与上述codec相同、拒duplicate/unknown（codec已检、数据库按数组元素完整键/计数/约束再核），逐数组ordinal遍历，INSERT file/dependency子表，外键/unique/bytes约束拒遗漏或碰撞；所有目标Ref在同事务逐项核原bytea/结构一致。无外部IO、无修改SD GUC、无UPDATE/DELETE、无SECURITY DEFINER，运行角色仅本schema INSERT/SELECT及该trigger所需权限；任一子行失败整事务rollback。真实AffectedRows取顶层asset INSERT=0/1，子行计数由command2/result codec核，不混入Binding.Min/MaxAffectedRows。command0先核根/依赖后command1仅根缺失时写，command2对已有同技术Ref/descriptor/files/边返回原receipt，异值Conflict；不同SourceSnapshot或本次Stage对象不覆盖已有技术绑定，Existing继续引用原files/ObjectRef，当前Stage对象成为受保护的原orphan路径等待SD GC。Serializable及SD同authority锁防并发窗口，40001原身份Unknown/ConfirmedNotCommitted由SD回执区分，不自行创建第二事务补写。

桥在Snapshot resultCodec.Validate及TechnicalBinding.DecodeSnapshot成功后，按同一规范result bytes解析fileBindings并保存**有界View记录**：(ViewId/Revision,全部exact Ref和role/path→SD.ObjectRef)。这是明确桥资源状态，不是新增StoreSnapshot字段/隐藏native对象；MaxRetainedResources/MaxResidentBytes计完整映射，无法预约在返回snapshot前MA-RES，不交缺file映射的成功。HoldReceipt按该记录取得实际SD retention leases并pin该View，Open/Materialize仅用当前持有的原映射，文件对象解码不能从AssetRef/hash猜物理ObjectKey。无活跃lease的记录可淘汰；淘汰后Acquire同closure须重新ReadSnapshot验证View/全映射相同才恢复，否则原请求Unknown/Conflict，不能拼不同View。重启无需恢复临时View/lease，只按持久asset_file重读建立新View；原Unknown Commit另走Origin目录。OwnerReadResult.References必须与objects精确相等，fileBindings每项完整且全部descriptor文件/旧metadata覆盖，重复多role的物理ObjectRef须一致；缺项/额外对象/不同Store整体拒绝。

Snapshot/Roots的JSON传输仅用`encode(bytea,'hex')`等固定PG表达式输出原bytea hex；codec严格解码，重复行/多项/超bytes在构造StoreSnapshot前拒。Snapshot的ViewId为SHA256固定view subject的JCS bytes，小写hex；subject唯一键`rule/scope/store/rootRef/purpose/assets/objects/fileBindings/viewRevision/profileId/profileRevision`，rule=`model-store-view-jcs-v1`，明确排除结果自身viewId，避免摘要环；ViewRevision为同视图max(sealed_epoch)规范字符串（空root失败）；不能跨页混新view。Commit binding固定MinAffectedRows=0/MaxAffectedRows=1/MaxCommands=3/AllowEmptyBatch=false，Snapshot/Roots为0/0/1/false；MaxRetries=0（冲突/40001/40P01返回原身份给Host重查，不透明重发副作用），RetryDelay=TimeSpan.Zero；Lock/StatementTimeout从registration options取，扣原deadline。各command的maxRows/maxBytes由已冻结Profile计出，checked超SD限额在Create拒。Commit的ResultSchema/codec同时实现SD.IStorageResultCodec与本工程PG result codec，其EncodeResult严格验证command数/索引、0/1行、所有byte/hash、全文件/边集合及actual AffectedRows，不用Dictionary覆盖重复项。

**原模型操作到SD身份的耐久定位。** 桥的进程字典只是活跃原Task/lease强持，不能作为跨重启查询依据。本schema另有`im014.operation_origin`，PK=SD完整Scope/Store/Owner+model_namespace+model_operation_id+action_slot，列`model_request_digest` bytea、`action_kind` text、`downstream_identity_bytes` bytea、`downstream_request_bytes` bytea、`binding_version_bytes` bytea、`created_utc` timestamptz，均有界且INSERT后不可变；没有asset引用，不进入模型摘要/GC根。action_slot固定`stage/<ordinal>`、`verify/<ObjectKeyHash>`、`commit`，hold/session是临时资源而非新的可重发耐久效果；fileOrdinal同§5A.4。downstream_identity_bytes包含**原完整SD.OperationIdentity/PayloadHash**，request bytes为其既定canonical请求（不包含stream/秘密），用SD固定writer规则封闭解析。保存原ControlContext的scope/store/authority/principal版本Ref用于Host恢复核对，不保存凭证。origin表完整namespace可精确读，不靠当前Generation替原。

新增本工程私有`im014.origin-insert-v1`与`im014.origin-read-v1` registered binding/typed输入/结果/PGcodec一并进入BindingCatalog：Insert=Transaction/Transaction/Serializable、实际0/1行、MaxCommands=2、MaxRetries=0/AllowEmptyBatch=false；command0固定顶层`INSERT ... ON CONFLICT DO NOTHING`，参数$1…$9全键、$10modelOperationId Text、$11actionSlot Text、$12modelDigest Bytea、$13actionKind Text、$14downstreamIdentity Bytea、$15downstreamRequest Bytea、$16bindingVersion Bytea；command1固定Read同键重读bytes，所有列exact相等才Stored/Existing，异值Conflict。result键`rule/status/modelOperationId/actionSlot/modelRequestDigest/downstreamIdentity/downstreamRequest/bindingVersion`，rule=`im014.origin-result-v1`、status Stored/Existing/Conflict，冲突无成功body；GetReferences=Empty。Read=Read/Query/RepeatableRead、1命令，参数全键+modelOperationId+expectedModelDigest，ORDER BY action_slot COLLATE "C"，MaxRows按单操作MaxFiles+MaxNodes+2 checked有限上界、MaxResultBytes按Profile；越限整体失败，不漏slot后Complete。Read result键`rule/modelOperationId/modelRequestDigest/actions`，各action沿上述字段；任何已存model digest不同MA-IDEM。

在每个Stage/Verify/Commit外部动作前，桥先固定该动作完整SD请求和Hasher结果→注册OriginInsert→只有**已确认提交且原字段相等**才发送该动作。OriginInsert的SD幂等ID由modelScope/Store/modelOperationId/modelDigest/actionSlot/downstreamIdentity的有界JCS SHA256派生（`ma-origin-<hex>`），PayloadHash仍经StorageRequestHasher，不把下游PayloadHash拷给它；其自己的identity不写入自身payload，避免摘要环。OriginInsert Unknown先只读origin原键确认存在且完全匹配；不能在未确认前发下游效果。准备日志响应丢失的原Task仍root强持，日志只是确定意图而非证明动作已发送。

重启后的Store.QueryAsync在Host明确绑定**原**scope/store/generation及访问权后，先OriginRead→逐原下游OperationIdentity调用SD.QueryOperationAsync→Commit original receipt才可ConfirmedCommitted，原File receipt仅证明Stage；行存在不证明Commit已发送，NotFound/retention expired继续Unknown。Query只读原route/receipt，零重发Stage/Commit、零改Origin；不知道action已发与否时不能猜ConfirmedNotCommitted或另ID重试。confirmed Commit后原已封asset receipt定位与Origin必须同identity/digest，缺origin或不等为完整性故障。耐久定位读失败只阻该原操作恢复，不将对象或资源计为0；未启用此登记/原query保留期保证时DurableReconciliation=false，Service只能root保持Unknown，不能转交声称重启可恢复。DB origin保留至少原SD幂等/未知恢复保留期，本版无删除API；创建前计有限retention容量，容量不足先拒新接纳，不清未决条目腾位。旧未知记录由Owner维护批准后处理，不让默认Query做写入或设备动作。

**根resolver与恢复验证算法。** Open核OwnerKey、全部Scopes/Stores/目录版本及cut原ReferenceEpoch，未Attach/不支持cut拒；只借用已装配Runtime.Query session。在原屏障保护内，逐登记组合按full key keyset读Roots，将全部条目有界冻结成一个snapshot（MaxRootSnapshotEntries/Bytes含去重前角色项）；任一组合失败/溢出则无snapshot，已读Reader/Session真实释放后返回Fault。OwnerReferenceEntry.EntityId=`ma-`+SHA256资产身份固定`namespace/id/revision` JCShex，EntityVersion.id同EntityId/revision=1/hash=SHA256(full exact asset Ref JCS)；不把opaque revision截断。每资产每unique ObjectRef仅一根entry，排序按全asset键、SD ObjectKey，Sequence连续0起；旧metadata必须列出；ObjectRef属于原Store/Generation。Read(nextSequence)只按冻结数组返回有限页，不IO/重新取新cut，next必须合法且不跳过；最后Complete=true，即使最后为合法空页。Snapshot Dispose释放保留内存，Open原Task/Reader未退出不得销毁Runtime。原屏障是否仍有效由SD调用方每次重核，resolver不通过GUC/epoch最大值伪证物理guard。

恢复ReadValidation在隔离目标范围读取**全部**asset/file/edge，复算新Core技术Ref、检查旧原元数据及登记verifier能力、核所有显式目标存在且Ref一致、文件/metadata ObjectRef完整并实际Verify原字节；缺旧协议验证只使该恢复Owner验证Unknown，不能声称恢复成功。无副作用、不补表/修Ref/调用产品采用。所有asset永久根及完整边从同Owner目录冻结，GC/Backup安全不依赖某次Runtime purpose窄读；删除能力未批准，所以本版无需推测客户保留天数。

接入验收使用两个独立Service（匹配/OCR）各自Bridge/Authority、同合法Store；分别新seal/并发same identity same/different digest/三Purpose依赖/旧metadata/失联commit/重启原query/根cut读/GC竞态/隔离restore。逐回执检验原操作摘要、files/edges/object集合、E、AffectedRows与原receipt。缺schema部署/PG/物理flush证据是**内部实现验证门**，不是客户设计门；禁止在Stage前能力检查中把未注册包当完整登记。


### C.2 Windows安全物化与字节缓存

**工厂与配置。** 本版固定本地Windows/NTFS独占根、fresh copy主路线；不默认为NAS/SMB/FAT/共享临时目录，也不依赖磁盘缓存才能加载模型。StorageDatabase.Adapters公开`WindowsModelAssetMaterializer.Create(profile,rootSlot)`，结果为`Materializer:IModelAssetMaterializer? / Errors:ImmutableArray<ModelAssetError>`；profile字段`Id/Revision/RootId/TrustedRootPath/ExpectedVolumeGuid/ExpectedRootFileId/OwnerSid/MaxMaterializedBytes/MaxConcurrentGenerations/ChunkBytes/Cleanup`。路径仅受信任Host装配，不进入请求/事件；ExpectedRootFileId是NTFS FileIdInfo的16byte原值，VolumeGuid/OwnerSid来源部署，不由Core字符串推断。Create不打开根；第一次Materialize通过root.StartCall登记原打开Task，再核物理guard，失败保持能力不可用。profile所有限额受实例总预算；Root权限允许仅指定服务账户和受信任管理员，不能把普通操作者当写入者。没有实际介质/ACL/guard验证前SafeMaterialization不得报告已验。

1. 使用Win32 `CreateFileW`/`GetFileInformationByHandleEx`/`GetFinalPathNameByHandleW`的小范围P/Invoke适配，仅在本Windows adapter内；不把这些API放Core、HALCON封装或公共Contract。目录用OPEN_EXISTING+FILE_FLAG_BACKUP_SEMANTICS+FILE_FLAG_OPEN_REPARSE_POINT，逐路径ancestor打开检查FileAttributeTagInfo（任何reparse拒绝），读取FileIdInfo/Volume、保持handle直到本代退出；不启用backup特权绕ACL。`FILE_FLAG_OPEN_REPARSE_POINT`只控制最后组件，所以只查最终根不够。GetFinalPathNameByHandleW使用FILE_NAME_NORMALIZED|VOLUME_NAME_GUID，按目录分隔边界比较同volume/原Root file ID；拒绝异volume、文件ID变化、非目录、路径越根。各ancestor handle不给FILE_SHARE_DELETE，禁rename/delete；受信任根不得允许非服务主体新写/替换。空的最终根叶由部署预先创建，不让模块创建未知ancestor。
2. 本代目录名`g-`+SHA256(scope+原OperationId+RequestDigest+原ResourceId的有界JCS)hex；不把logical path直接拼根名。用CreateDirectoryW独占创建，已有同名目录不得当可复用空根，回原记录或Conflict；成功即注册root资源/cleanup。逐Layout的TargetPath先按§4.1全图校验，逐层创建目录并打开/保持同样guard。文件用CREATE_NEW（不使用CREATE_ALWAYS）、非共享写打开，逐chunk从原hold精确ContentReadLease复制到新文件；全部目标copy计bytes，hash/EOF/长度再核。不跟现有链接，不自动改名字/路径，写入失败不返回半成品entrypoint。
3. 所有writer Flush/真实Dispose后重新以GENERIC_READ+FILE_SHARE_READ打开每个目标文件，不给SHARE_WRITE/DELETE；检查file ID/final path/attributes及完整length/hash，再保持read guard直到HALCON worker/native全部退出。read guard允许native以只读共享打开；某reader要求写/删除则此路线Unsupported，不放宽guard。readonly attribute是提示而非安全证据；ACL+handle guard才构成已声明威胁边界。不对管理员、内核或同服务进程被攻陷承诺沙箱隔离；trusted roots是实现前提。
4. VerifiedFiles一项对应一个Layout目标（source ClosureFile仍保留精确角色/原path，重复source多copy按目标顺序列出），入口只返回该代已guard的绝对TargetPath。source read及临时stream真实退出后归还，native pin期间物化、hold、Permit均不释放。取消只能合作停止copy/等待，已进入HALCON不强杀线程；有限等待返回Pending/DrainUnknown、原worker/目录/handles保留。释放先禁新借用→等所有pin→释放file guards→从叶按本代已登记文件/目录逐项DeleteFile/RemoveDirectory→释放ancestor/root guards；不递归删除未知内容。不靠枚举目录猜哪些归本代，发现额外内容停止cleanup并报MA-PATH-001，原资源保留。
5. 临时物化不授耐久事实，重启后的残留目录先只读核本adapter私有journal（原scope/operation/digest/生成ID、登记路径及file IDs），没有匹配/缺登记/Unknown不删。原进程已退出只证明其native不再占用，不证明其它未决Store/Sink副作用；每代cleanup仍查询原Owner资源。一个RootId同一时刻只允许一个Host持独占lock file（CREATE_NEW/open exclusive+ACL），后启动返回Conflict；不会两进程扫描清理彼此的目录。

**缓存冻结为内存只读字节缓存，可关闭。** 默认profile.Enabled=false、无磁盘持久缓存、无native handle缓存。开启时由`ModelAssetsByteCache(profile,TimeProvider)`装配到本桥的OpenContent内部，不改变IModelAssetStore API；profile必填`Id/Revision/Enabled/MaxEntries/MaxBytes/MaxEntryBytes/IdleTimeout`，禁无限/负值（Enabled=false时仍填合法有限值，不靠0解释关闭），所有占用扣Service/Bridge MaxResidentBytes。Key=(完整SD.ObjectRef，完整raw Digest)，不可用alias/路径/RootRef代替；缓存只存**全读校验成功的不可变bytes**，不存permit、source stream、native、materialization path或“已获批准”标志。

命中仍先通过当次exact StoreView/hold/Permit接纳；在交付前重新length/hash核缓存bytes，失败逐Key移除并MA-HASH，不静默fallback掩盖损坏。borrow返回独立readonly stream wrapper并pin entry，禁止GetBuffer/公开可写Memory；调用者写/越界拒。父lease和其子read原释放规则不变。并发miss不合并带不同authority/operation的IO任务，每次请求仍有自己的原Task/hold；首个完成且无冲突者在锁内插入，其它完成者核相等后可复用不可变bytes或释放自身副本。预约先检查单entry、总bytes和MaxEntries；按`lastAccessStamp`升序、Key ordinal平局的LRU只淘汰pin=0条目，尚在IO/pin不动；全部pin或超预算则绕过缓存走原Store读，不排无界队列。构建临时bytes也计预算，无法容纳则用安全暂存/流route，不能为了缓存分配超过MaxResidentBytes的大数组。

TTL用TimeProvider单调timestamp，只在命中/插入/显式Trim做惰性过期，不为每entry启动timer；MaxEntries保证没有命中也有界。撤回禁止新命中和新读，但immutable byte条目不修改/不替换原Ref；旧pin遵§8A，归还后可淘汰。关闭先停止接纳→清pin=0→等真正read退出→清剩余bytes；Unknown保留root，不靠Clear字典假报归还。缓存命中/未命中报告按实测区分，不改变模型完整性、用途或durability结论。

### C.3 本地技术包发布Sink与原操作恢复

本版真实默认目标固定为受控本地NTFS目录包，不提供远程网络发布、ZIP解析或自动外发。`WindowsDirectoryAssetExportSink.Create(profile,rootSlot)`→`Sink:IAssetExportSink? / Errors`；profile含`TargetId/Id/Revision/TrustedTargetRoot/ExpectedVolumeGuid/ExpectedRootFileId/OwnerSid/JournalRoot/MaxEntries/MaxPackageBytes/MaxPendingPublishes/ChunkBytes/Cleanup`，路径只在Host装配，Root/Journal同C.2逐ancestor guard+ACL检查、两者同volume、不得位于某bundle内。TargetId稳定绑定物理目标与profile修订，换根必须换TargetId，不在原Unknown请求改路由。发布目录名`p-`+SHA256完整scope+TargetId+原model OperationId+RequestDigest的JCS bytes hex，不使用任意UI文件名；相同Ref另操作仍是另一明确目录，Sink不会改产品alias。

- Begin先登记原identity/完整请求摘要和目标root file ID→独占stage目录→私有journal写`Prepared`。journal是该sink技术恢复记录，不是模型核心或包文件；规范字段`rule/targetId/scope/operationId/requestDigest/stageId/stageFileId/finalName/entries/packageDigest/state/receipt`，rule=`model-directory-publish-jcs-v1`、nullable字段显式null。entries固定packagePath/length/hash/本代fileID，排序scalar；state闭集Prepared/Ready/PublishSent/Published/NotPublished/Unknown/Aborted。限MaxPendingPublishes，空间不足在写任何source前拒。写journal采用CREATE_NEW revision文件→FlushFileBuffers→关闭并guard核bytes，单独原head CAS/锁，不能overwrite旧记录；断电持久性以profile真实验收为准，未验不报告DurableReconciliation。
- WriteEntry检查原scope/ID/Stage、§5A.3全部packagePath/预算/碰撞，CREATE_NEW逐项受限写至EOF并核length/hash；同时角色映射同物理path不得重复写。bundle.json通过同有界流程，不能特殊放宽。所有source流只借用并在实际IO结束后归还。完整文件列表与bundle声明逐项相等、无余项，PackageDigest复算等于原请求，才可Ready；empty/partial/旧metadata缺失拒Publish。
- Publish持原单writer锁，重验原Permit（Service做最后validation，sink也核固定subject/有效期；许可fence生效仍归真实Authority）、root/Stage guards和package摘要→先durable `PublishSent` intent→释放妨碍rename的**stage/file**no-delete guards（保持父/根guard和独占ACL/单writer；原file IDs/摘要记录保留）→`MoveFileExW(stage,final,MOVEFILE_WRITE_THROUGH)`，不指定REPLACE_EXISTING/COPY_ALLOWED，同volume拒overwrite→打开final检查原stage目录fileID与全部文件identity/hash→写Published原receipt。成功至少证明可见和原内容确认；电源失效/目录元数据持久性须实测，不把WRITE_THROUGH当普遍断电保证。native物化目录不能当export staging，避免借用pins妨碍rename。
- 最终目标已存在时，只核原journal是否证明它就是本identity已发布且package一致；证明则原receipt，异identity/digest或不明来源Conflict，不接管、不删。rename返回错误/响应丢失/Published记录失败，只有同时证明stage仍原fileID存在、final不存在且原发布任务已真实退出、原journal未有Published才ConfirmedNotPublished；其余Unknown。Query只读原journal和原final/stage identity，不触发rename/补发布；可在确认final==原stage fileID+全bytes/package匹配后追加**确认回执**，不重发副作用。NotFound journal/final不能单独证未发布。
- Unknown保留stage/journal/原identity，禁止Abort；只有ConfirmedNotPublished且全部IO/borrow退出才按本代登记内容清stage，Abort幂等同ReleaseOperationId。不删已发布final；Service关闭不得强删未知发布。重启Host只按原TargetId/Profile/identity恢复Query，明确授权Resume发布必须由工程工具对原intent重新授权且原任务/锁已确定退出；本版IAssetExportSink没有Resume API，所以默认只核对/确认，不自动续发布。未能确认的Unknown交给目标维护Owner按原记录处理，不能用新ID绕开。

### C.4 技术包签名验证与信任边界

技术包签名是可选完整性/来源证据，不是程序采用、质量放行或模型训练；默认没有签名要求时状态NotRequested。本模块仅**验证**，不存私钥、不创建证书、不提供签名服务/网络取key/自动系统信任链。签名为宿主明确提供的detached envelope（在bundle目录之外保存/传递）；§5A.3包字段/PackageDigest与意外文件拒绝规则不变，不能偷偷在bundle加signature.json或把签名纳入自身摘要造成环。

Service工程新增纯托管`ModelAssetPackageSignature.Verify(input,profile,TimeProvider)`同步有界入口（无IO/后台）；input immutable字段`Scope/RootRef/Purpose/PackageDigest/EnvelopeBytes`，profile为`PolicyId/Revision/RequireSignature/MaxEnvelopeBytes/MaxKeys/MaxSpkiBytes/MaxPolicyBytes/TrustedKeys/MaxAge/AllowedClockSkew/TrustSnapshotId/TrustSnapshotExpiresAtUtc/ClockTrusted`；TrustedKeys每项`KeyId/SpkiBytes/SpkiSha256/NotBeforeUtc/NotAfterUtc/Revoked`。result字段`Status:PackageSignatureStatus/SubjectDigest:Digest?/KeyId:string?/PolicyId/PolicyRevision/VerifiedAtUtc/Errors`（Invalid/Unsupported/Untrusted/Expired/Missing统一MA-SIG-001+精确Status，Unknown用MA-SIG-UNK-001，Verified/NotRequested Errors.Empty），enum为NotRequested/Verified/Missing/Unsupported/Invalid/Untrusted/Expired/Unknown。无签名且Require=false=NotRequested；Require=true=Missing；失败不返回Verified。ClockTrusted=false、当前UTC越过TrustSnapshotExpiresAtUtc或policy/key来源不可信/无法确认撤回状态则Unknown，不能使用本机时间默认解决。

envelope唯一键`rule/algorithm/keyId/subject/signature`，rule=`model-package-signature-jcs-v1`、algorithm=`ecdsa-p256-sha256-p1363-v1`。subject唯一键`rule/scope/rootRef/purpose/packageDigest/keyId/signedAtUtc`，rule=`model-package-signature-subject-jcs-v1`；scope采用B.4完整ModelAssetsScope，Ref/digest/purpose沿原投影，signedAtUtc是UTC固定七位小数`yyyy-MM-ddTHH:mm:ss.fffffffZ`、InvariantCulture，keyId非空限长。signature为128字符小写hex（64byte r||s，IEEE P1363）；unknown/duplicate/非法Unicode、额外key、错subject、错误长度或算法均拒。subject JCS SHA256产生Digest(rule=subject rule,algorithm=sha256)；算法不对JSON原排版签名，签名envelope不含自身hash。

验证顺序固定：预算/shape→subject逐项等于input（含scope/Root/所选Purpose/原PackageDigest）→可信KeyId exact匹配唯一key、SpkiSha256 raw bytes匹配→用`ECDsa.Create()`+`ImportSubjectPublicKeyInfo`且bytesRead==全部SPKI长度→`ExportParameters(false)`核Curve.Oid.Value=`1.2.840.10045.3.1.7`、X/Y均32byte→有效期与revoked/MaxAge/clock skew（当前UTC及signedAtUtc均在key区间内；signedAtUtc不得超过当前UTC+skew、距当前时间不超过MaxAge；超过TrustSnapshotExpiresAtUtc=Unknown）→`VerifyHash(hash,signature,DSASignatureFormat.IeeeP1363FixedFieldConcatenation)`→Dispose原ECDsa。只用BCL .NET10已核API，不手写椭圆曲线；格式错误/CryptographicException=Invalid或Unsupported固定错误，不漏SPKI/内容；Verify=false=Invalid。无低S规范承诺（P1363签名本身不是对象身份，不用signature bytes做idempotency key）；需要另一算法须登记新algorithm/rule/公开向量，不能自动try RSA/DER。

工程工具Host在包预检后先Verify，再按Require策略决定是否进入逐asset导入；结果交原审计Owner，不回写核心、原SealReceipt或UsagePermit。验证通过也必须逐文件hash/旧原verifier/用途资格；签名未知只阻要求签名的包入口，不阻纯Core、已授权历史读取或无签名政策的离线模拟。可信Key/生效撤回、签名要求由客户信息安全Owner和用途Owner提供；算法/subject/错误/格式/Host调用顺序在本模块已定。


### C.5 HALCON格式Adapter的闭合工厂、schema和challenge接线

`Asun.Modules.ModelAssets.Formats.Halcon.HalconModelFormatAdapters.Create(profile,ports,rootSlot)`是唯一公开factory；result=`Adapters:ImmutableArray<IModelFormatAdapter>/Errors:ImmutableArray<ModelAssetError>`，失败Adapters.Empty。profile字段`Id/Revision/Formats/MaxWorkers/MaxQueuedCalls/MaxTupleElements/MaxObservedBytes/MaxIconicBytes/Cleanup`，Formats每项固定`AdapterKey/FormatId/FormatRevision/Family/SemanticSchemaId/Revision/Digest`；ports字段`TimeProvider/ChallengeExecutor:IModelAssetChallengeExecutor?/RuntimeDeviceResolver:IModelAssetRuntimeDeviceResolver?`，均借用。Create不调用HALCON/创native，登记root后每个ReadBack才预约专属有界worker；重复adapter键/schema版本拒。Family闭集Shape/Ncc/Deformable/Variation/DeepOcr/Dl/Onnx；同Family不根据扩展名猜子族，FormatId/Revision exact确定路由。工厂schema为本模块下表最小`im014.halcon.<family>.observables-v1`（revision=1），Digest是下表字段形状、route/单位/tuple类型的JCS SHA256；生产者模型创建仍由原消费者实现，实际值不是本指导伪造的客户数据。未知schema/额外需要执行的query/set拒Unsupported；新增参数需要本指导登记新schema/route，不能从输入字符串动态调用算子。

**统一输出编码。** 数值HTuple输出按**保序Sequence**写Canonical值（integer为规范Int64字符串，real为有限Binary64 JCS；不强制把tuple当标量，整数/实数混合按下表允许域逐项标记为有界Object `{kind,value}`）；字符串tuple同样保序，handle类型一律拒，所有数组/文本扣profile。single string的type/metric仍使用长度1的String Sequence，以免返回类型随模型变。角度单位rad、scale无量纲、图像尺寸px、范围image-value，其他null；不转换坐标/单位。Serialized最小字段声明SourceId=生产者、SourceRevision=原创建修订；observables统一SemanticKind.Sequence、Constraints.elementKind=Object，每个输出元素为上述kind/value闭集Object；Requested来自冻结manifest字段，Observed来自真实query，Status=Explicit或AutoResolved仅按已冻结声明来源，不通过“数值像auto”推断。缺declared observable允许历史保留但report limitation=`ParameterNotCollected`，无requested对比不得称语义一致；query不支持=Unsupported/null、异常=QueryFailed/null、取消=Cancelled/null，不改文件/清单补默认。

| Family/schema suffix | 固定query最小字段（每个ID=`serialized.<name>`） | 固定Runtime可写route；限制 |
|---|---|---|
| Shape / shape | `get_shape_model_params`全部返回值：num_levels/angle_start/angle_extent/angle_step/scale_min/scale_max/scale_step/metric/min_contrast；数值tuple Int64或Binary64、metric String | 无set；RuntimeSnapshot fields必须Empty；不调用find/训练；get_shape_model_contours只在额外已登记可视证据需求下使用，默认不分配轮廓 |
| Ncc / ncc | `get_ncc_model_params`全部返回值num_levels/angle_start/angle_extent/angle_step/metric；类型同上 | 无set，Runtime fields Empty；不调用find_ncc_model |
| Deformable / deformable | 一次一个具名`get_deformable_model_params`：model_type String、num_levels Int64、angle_start/angle_extent/angle_step Binary64、metric String、min_contrast Int64；calibrated类型另外cam_param（Int64/Binary64/String保序）、reference_pose（Int64/Binary64）；local/uncalibrated不得补calibrated字段 | 不做set/坐标变换；未知model_type或family字段不支持=Unsupported，不换reader；cam_param表示由生产者冻结，资产层不决定标定物理允差 |
| Variation / variation | read成功及`get_variation_model`返回ideal/variation image的width/height/channel投影（原images在worker私有且计MaxIconicBytes，获取尺寸/通道固定cv2.get_image_size/count_channels算子）；无训练统计/threshold查询 | Runtime fields Empty，不调用train/prepare；缺训练统计只能Limited/Unavailable，不能因两image存在称可重训 |
| DeepOcr / deep-ocr | `get_deep_ocr_param`：recognition_alphabet、recognition_alphabet_internal（String），recognition_alphabet_mapping（Int64），recognition_image_dimensions（Int64）；只核本模型实际包含的recognition组件，未含该组件标Unsupported | 只允许recognition_batch_size（正Int64）与deviceRef（受信任设备引用）；deviceRef经DeviceResolver给本worker私有handle→`set_deep_ocr_param('device',…)`，set后get device/recognition_batch_size及实际设备描述；禁alphabet/model/size/权重修改 |
| Dl / dl；Onnx / onnx | `get_dl_model_param`：type/min_version（String），image_width/image_height/image_num_channels（Int64），image_range_min/max（Int64/Binary64）、batch_size（Int64）；不适用image族的非图像网络该routeUnsupported，不能生成伪shape。ONNX仍经read_dl_model，无第二ONNX backend | 只允许batch_size（正Int64）、deviceRef；device解析→set_dl_model_param('device',…)，set后query device/batch_size、实际描述；precision只query可支持值，不set/转换网络/融合/optimize；其他Runtime fields拒 |

RuntimeSnapshot schema固定`im014.halcon.<family>.runtime-v1`（schema digest按上述闭集shape）；Shape/Ncc/Deformable/Variation fields.Empty，DeepOcr为`runtime.recognition_batch_size/runtime.deviceRef`，Dl/Onnx为`runtime.batch_size/runtime.deviceRef`，各项必填或明确NotCollected/null（此时只format-only不设设备、不执行challenge，报告RuntimeNotBound）。设置只有Explicit值，batch正且不超过Host已登记设备预算；不得默认CPU/GPU、静默fallback或在读回时改变生产权重。deviceRef是不透明稳定Host引用（String），**不是序号/裸句柄/可猜GPU名**。DeviceResolver公开`ResolveDescriptor(string deviceRef)`返回有界不可变`DeviceDescriptor(Id:string/Revision:string/Backend:string/DeviceId:CanonicalValue/DeviceType:string/DeviceName:string/RuntimeVersion:string/MaxBatchSize:int)`或无值+错误，接口结果固定`ModelAssetDeviceResolution(Descriptor?,Errors)`，无IO。adapter在原worker以`cv2.query_available_dl_devices`使用固定filter type=DeviceType枚举受MaxTupleElements限制的设备，逐个`get_dl_device_param`只query `ai2/id/type/name`；Backend必须等于ai2结果，DeviceId严格保序类型值相等，type/name exact；固定`get_system('version')`核HALCON实际runtime version等于Host冻结RuntimeVersion。恰好一项匹配才选，0项Unsupported、多项Conflict；不按序号取第一项或自动换backend。不把SDK句柄交Service/契约，也不将设备id/name冒称全球唯一物理序号；部署Owner确认描述的实际机器绑定。设备tuple和model查询返回的借用device引用均按公共tuple所有权归还，不对可能被HALCON共享的设备状态调用clear_handle/修改设备参数；只有fresh model本身按§10清理。具体C#参数类型仅公共签名/消费编译核，不扫AsunImage内部。DeviceResolver不获得训练/控制机台权。

worker过程固定：完整性/Format/schema/Layout预算→root登记原dispatch task→一条专属Thread创建fresh model→query序列化字段→在该线程设置已批准有限runtime→query实际runtime→释放native/临时tuple/iconic→等待原worker真实退出→必要时调用challenge executor。clear_dl_model和clear_handle均在原创建worker finally，全部失败/取消路径各资源一次清理；Primary与Cleanup异常分别保留。不用Task.Run跨线程续跑local-scope清理，不为每次参数get并行读取同handle。HALCON同步调用到期不Thread.Abort，不标Released；报告已可用但native仍未知时Outcome.Unknown/PendingResources保留原worker，不能返回成功Value。Serialized字段差异记录Failed/限制（FormatReadback仍表示文件支持状态），用途是否允许差异归producer/usage policy，不由资产层改阈值。

**Challenge无需泄漏native句柄。** `IModelAssetChallengeExecutor.ExecuteAsync(ModelAssetChallengeInput,CancellationToken)`→`PortResult<ModelAssetChallengeReport>`；input字段`Context/RootRef/GraphRefs/Format/RuntimeSnapshot/ChallengeRef/Materialization`，与原ReadbackInput exact一致；report字段`RootRef/ChallengeRef/MethodId/MethodRevision/ExpectedEvidenceDigest/ObservedEvidenceDigest/Outcome/Limitations/ReportReceiptRef`，Outcome沿ChallengeOutcome闭集。executor由匹配/OCR/AI生产者在Host显式构造，依赖包括其已登记challenge Store/真值/Profile/算法公开Service，而非静态locator；它按精确ChallengeRef消费已冻结样本/预处理/方法/容差、预算，不能请求资产模块选最高分或修改生产参数。Materialization只借用pin，executor**另建并释放自己的fresh native reader**，不取得前一个worker的handle；这次真实再读/执行/退出计同一总deadline及资源预算，可能更慢，不能在性能报告隐藏。返回前其native退出，未知则原executor worker/root强持、PendingResources明确Owner，Service不代清句柄。

ChallengeRef=null→NotRequested且不调用executor；有ref但缺executor/未登记方法/样本不完整→Unknown/MA-CAP，不能忽略后报Passed。executor report必须匹配原Root/ChallengeRef/Method修订及expected证据；Expectation是生产者冻结内容，本模块不发明物理容差。挑战结果属于报告和外部用途证据，不回写封存模型或获取设备/质量权限。实际query输出、真实格式golden、native峰值/cleanup及challenge的误接受/拒绝仍由Formats.Tests/生产者实际验证，不以schema设计闭合当算法通过。

### C.6 增量验收断言、反例与全范围结论

复用§13现有Exe/测试机制，不新建报告或脚本。将下列case加到既有对应suite；需要真实PG/Windows/HALCON的数据门按case明确，缺条件不得跳过后报整suite PASS。

| 用例 | 真实消费者/输入 | 明确判定 |
|---|---|---|
| MA-DB-01/02（bridge-contract） | 两Host并发同Identity同/异digest；一个Runtime依赖、一个RebuildSource、一个ValidationEvidence及旧metadata | exact不覆盖、原receipt/技术Ref不重写、三Purpose目标缺失拒；AffectedRows0/1与完整子表同事务、有界图遍历不依赖最终LIMIT，全部unique对象根可见 |
| MA-DB-03/04（真实PG增量） | commit响应丢失/进程退出、原Query；cut前后新asset、根分页中间失败/超预算 | 无另事务补receipt/引用、原ID可确认或Unknown；原cut不混新epoch，任何缺项/溢出无Complete，GC/Backup不把故障当零根 |
| MA-FS-01/02（Windows真实增量） | ancestor/junction/ADS/NFC碰撞/替换/同Root第二进程；pin在途取消与残留目录 | 副作用前拒不可信根；独占writer/read guard+fileID不变；原worker未退出不删代目录/不报Released，未知/额外文件不递归清理 |
| MA-CA-01（bridge-contract） | enabled/disabled、小预算、全pin、并发miss、篡改cache byte、authority撤回 | 只immutable bytes、预约不超预算、全pin绕缓存无无界等待；完整hash错拒绝不掩盖、权限每次重验、无native/permit缓存 |
| MA-EX-01/02（Windows真实增量） | stage未完成、同名异来源、rename后receipt失联、重启Query、Unknown Abort | partial拒publish、Reject不覆盖；原fileID/package核确认，不因目标可见假receipt；Unknown零Abort/自动rename，已发布final不删 |
| MA-SG-01（protocol） | .NET10 BCL产生独立测试P256 key/signature；subject wrong scope/root/purpose/hash/key/time、DER/长度错、撤回/缺policy | P1363正确才Verified，任何错误不授用途；签名不改变bundle/core hash、密钥不进入日志；测试key不冒称生产信任 |
| MA-HF-01/02（real-formats） | 每族真实已冻结样本、tuple/可选字段、错误runtime device、无/错challenge、local清理异常 | 只固定route，无未知set/网络转换；Requested/Observed分开、未请求非Passed；实际native真正归还/Unknown保留、creator线程清理 |

两轮有限自审：第一轮按实施者正常→重复/并发→预算/取消→Unknown/重启→cleanup逐链，检查登记能力必须在Stage前就绪、子Stage ID含父请求、原SD身份先耐久定位且无自引用、完整依赖根与cut、trigger真实行数、安全guard释放后rename窗口、签名自引用及缓存许可；第二轮按空匹配Host→OCR第二Host→公开依赖创建/Attach→无UI读取/格式/导出→双STA投影→有限关闭，检查SourceSnapshot不靠未传字段、Runtime先创建再resolver Attach、borrowed Runtime/Authority/Materialization归属、challenge另建native而不泄漏handle。自审是文档推导，不是编译/SQL执行/真实文件系统或HALCON测试；已接收Core数字闭包/原Golden不重复复核。

截至本版，**当前批准模块范围内可由IM-014决定的软件设计欠账已收口**：Core/S1、SD登记/codec/固定语句/完整根、Windows物化与本地Sink、只读缓存、detached签名验证、HALCON固定schema/worker/challenge端口、C.8权限与用途证据桥和可选U1均有唯一实施位置与可判定断言。没有把登记SQL/参数route/根历史/缓存算法转给客户；不新增训练、生产推理、资产删除、私钥签名服务、远程发布/ZIP API或程序/质量放行。新候选能力须另行批准，不拿“全范围”扩大边界。

| 真正外部输入/决定 | 精确Owner | 仅影响范围 |
|---|---|---|
| 用途证据、主体权限/即时撤回能力、程序采用与质量放行政策 | IM-004 authorization负责权限事实；匹配/ocr/ai-inference及其产品程序/质量Owner负责对应用途证据/采用，不由IM-014合并成质量决定 | Production Authority接入及该用途Acquire/Verify/Export；不阻Core/S1/技术登记 |
| 生产可信key/SPKI生效撤回、RequireSignature和可靠UTC源 | 客户信息安全Owner（Host安全部署责任人），包入口用途Owner批准签名要求 | 要求签名的真实包入口；不阻无此要求的技术路径 |
| 受信任根/ACL账户/NTFS volume及root fileID、数据库endpoint/角色/存储容量与耐久拓扑 | Host部署/运维Owner；IM-066负责数据库/物理文件后端实际能力，IM-014负责自身适配实现与验证 | 真实Store/物化/本地Publish耐久；部署值不代替软件实现 |
| 真实模型/旧规则原件与创建时golden、challenge样本/真值/物理容差、设备描述及用途性能/现场指标 | 模型原生产者（alignment-2d/ocr/ai-inference及迁入项目Owner）；客户工艺/质量/计量验收责任人提供不能从软件确定的物理值 | 对应格式/旧verifier/challenge、用途/性能/现场资格；不阻无关新JCS/纯Core |
| 权威仓库/分支或批准代码快照、下一实际代码切片授权 | 项目研发Owner/用户，按PROJECT_ENTRY开工边界 | 产品代码开工；本次文档收口不以无.git退回 |

**内部实现/验证门仍存在，不能伪称外部门或已通过。** 注册包/DDL/codec/SQL/resolver、真实Windows guard/journal/cache、BCL签名测试、HALCON adapter、Authority公共契约映射、WPF/UIA与各消费者接线均尚需实际实现、build/run/资源异常/恢复验证；本轮没有运行上述测试。PureCore v0.2及S1原六项规格接收保持；U1/SD限定桥原内容接收保持，新增C附录为本原会话完成的文档设计/自审，不自动扩大ModuleCoreImplementationReady到全部adapter，更不授整模块/生产资格。定向结构检查只能证明本文件的引用/声明/范围一致，不能代替产品验收。


### C.7 新增适配公开声明的唯一类型落点

下列代码块只落上述工厂/配置/端口的公开类型，不是产品实现。行为仍以C.1–C.6为准；所有ID/revision/path为string、bytes为ImmutableArray<byte>、计数/内存上限在此固定类型。新factory失败结果无实例/Adapters.Empty且Errors非空；配置无默认参数。注册包的payload类型与PGcodec实现为内部sealed类，按C.1公开SD接口交付，不另暴露连接或任意SQL入口。

```csharp
// namespace Asun.Modules.ModelAssets.StorageDatabase
// using SD = Asun.Platform.StorageDatabase.Contracts;
public sealed record ModelAssetsStorageLocation(SD.StorageScope Scope, SD.StoreRef Store);
public sealed record ModelAssetsStorageRegistrationOptions(ModelAssetsScope Scope,
    ImmutableArray<ModelAssetsStorageLocation> Locations, SD.VersionRef RawFormat,
    string StorageDomain, ServiceLimits Limits, ImmutableArray<string> AllowedDependencyNamespaces,
    int MaxRootSnapshotEntries, long MaxRootSnapshotBytes, int RootPageEntries, int RootPageBytes,
    TimeSpan ServerLockTimeout, TimeSpan ServerStatementTimeout, ModelAssetsCleanupProfile Cleanup);
public sealed record ModelAssetsStorageRegistrationResult(ModelAssetsStorageRegistration? Package,
    ImmutableArray<ModelAssetError> Errors);
public sealed class ModelAssetsStorageRegistration
{
    public static ModelAssetsStorageRegistrationResult Create(
        ModelAssetsStorageRegistrationOptions options, ModelAssetsHostSlot owner);
    public ImmutableArray<ModelAssetError> AttachRuntime(SD.IStorageDatabase runtime);
    public IModelAssetTechnicalBinding TechnicalBinding { get; }
    public SD.StorageBindingDescriptor SnapshotBinding { get; }
    public SD.StorageBindingDescriptor CommitBinding { get; }
    public SD.IStoragePayloadCodec SnapshotCodec { get; }
    public SD.IStorageResultCodec SnapshotResultCodec { get; }
    public SD.IStoragePayloadCodec CommitCodec { get; }
    public SD.IStorageResultCodec CommitResultCodec { get; }
    public SD.StorageBindingCatalog BindingCatalog { get; }
    public SD.StorageOwnerRegistration OwnerRegistration { get; }
    public SD.IStorageOwnerReferenceResolver ReferenceResolver { get; }
}
public sealed record WindowsModelAssetMaterializerProfile(string Id, string Revision,
    string RootId, string TrustedRootPath, string ExpectedVolumeGuid,
    ImmutableArray<byte> ExpectedRootFileId, string OwnerSid, long MaxMaterializedBytes,
    int MaxConcurrentGenerations, int ChunkBytes, ModelAssetsCleanupProfile Cleanup);
public sealed record WindowsModelAssetMaterializerResult(IModelAssetMaterializer? Materializer,
    ImmutableArray<ModelAssetError> Errors);
public static class WindowsModelAssetMaterializer
{
    public static WindowsModelAssetMaterializerResult Create(
        WindowsModelAssetMaterializerProfile profile, ModelAssetsHostSlot rootSlot);
}
```

registration.Locations明确限定合法Scope/Store组合（不作Scopes×Stores无条件笛卡尔积）；OwnerRegistration按这些组合生成公开Scopes/Stores去重数组，resolver逐Locations实际配对枚举。Runtime/Bridge必须属于其中组合；Locations非空、重复/错tenant/无匹配组合拒。Materializer的namespace为本StorageDatabase工程（C.2）；Stage/根登记只依赖公开SD，依赖方向不反转。C.2缓存是该工程内部`ModelAssetsByteCache`，profile为内部sealed不可变类型，字段类型Enabled:bool、MaxEntries:int、MaxBytes/MaxEntryBytes:long、IdleTimeout:TimeSpan，其余string；不增加公共缓存对象供宿主绕许可读取。

```csharp
// namespace Asun.Modules.ModelAssets.Service.Adapters
public sealed record WindowsDirectoryAssetExportProfile(string TargetId, string Id, string Revision,
    string TrustedTargetRoot, string ExpectedVolumeGuid, ImmutableArray<byte> ExpectedRootFileId,
    string OwnerSid, string JournalRoot, int MaxEntries, long MaxPackageBytes,
    int MaxPendingPublishes, int ChunkBytes, ModelAssetsCleanupProfile Cleanup);
public sealed record WindowsDirectoryAssetExportResult(IAssetExportSink? Sink,
    ImmutableArray<ModelAssetError> Errors);
public static class WindowsDirectoryAssetExportSink
{
    public static WindowsDirectoryAssetExportResult Create(
        WindowsDirectoryAssetExportProfile profile, ModelAssetsHostSlot rootSlot);
}
// namespace Asun.Modules.ModelAssets.Service
public enum PackageSignatureStatus { NotRequested, Verified, Missing, Unsupported,
    Invalid, Untrusted, Expired, Unknown }
public sealed record ModelAssetSignatureKey(string KeyId, ImmutableArray<byte> SpkiBytes,
    Digest SpkiSha256, DateTimeOffset NotBeforeUtc, DateTimeOffset NotAfterUtc, bool Revoked);
public sealed record ModelAssetSignatureProfile(string PolicyId, string Revision, bool RequireSignature,
    int MaxEnvelopeBytes, int MaxKeys, int MaxSpkiBytes, long MaxPolicyBytes,
    ImmutableArray<ModelAssetSignatureKey> TrustedKeys, TimeSpan MaxAge, TimeSpan AllowedClockSkew,
    string TrustSnapshotId, DateTimeOffset TrustSnapshotExpiresAtUtc, bool ClockTrusted);
public sealed record ModelAssetSignatureInput(ModelAssetsScope Scope, AssetRef RootRef,
    DependencyPurpose Purpose, Digest PackageDigest, ImmutableArray<byte> EnvelopeBytes);
public sealed record ModelAssetSignatureResult(PackageSignatureStatus Status, Digest? SubjectDigest,
    string? KeyId, string PolicyId, string PolicyRevision, DateTimeOffset VerifiedAtUtc,
    ImmutableArray<ModelAssetError> Errors);
public static class ModelAssetPackageSignature
{
    public static ModelAssetSignatureResult Verify(ModelAssetSignatureInput input,
        ModelAssetSignatureProfile profile, TimeProvider timeProvider);
}
```

signature Empty envelope为缺签名，IsDefault非法输入；SpkiSha256必须raw-file-sha256-v1/sha256/32byte，MaxPolicyBytes含全部key bytes/UTF8/槽计费且在复制前核。非可信时钟取不到UTC时VerifiedAtUtc为DateTimeOffset.MinValue诊断哨兵（Status必须Unknown，不能作为事实时间）；其他结果记录本次可信UTC，不用签名内时间作验证时间。Sink JournalRoot初始也验证fileID/volume：工厂异步首次打开锁定并在每条journal保存原身份，不以可变化路径认为同一journal。软件默认拒不支持Windows，不在非Windows加载P/Invoke。

```csharp
// namespace Asun.Modules.ModelAssets.Formats.Halcon
public enum HalconModelAssetFamily { Shape, Ncc, Deformable, Variation, DeepOcr, Dl, Onnx }
public sealed record HalconModelAssetFormat(AdapterKey Adapter, string FormatId,
    string FormatRevision, HalconModelAssetFamily Family, string SemanticSchemaId,
    string SemanticSchemaRevision, Digest SemanticSchemaDigest);
public sealed record HalconModelAssetAdapterProfile(string Id, string Revision,
    ImmutableArray<HalconModelAssetFormat> Formats, int MaxWorkers, int MaxQueuedCalls,
    int MaxTupleElements, long MaxObservedBytes, long MaxIconicBytes, ModelAssetsCleanupProfile Cleanup);
public sealed record HalconModelAssetAdapterPorts(TimeProvider TimeProvider,
    IModelAssetChallengeExecutor? ChallengeExecutor, IModelAssetRuntimeDeviceResolver? RuntimeDeviceResolver);
public sealed record HalconModelAssetAdapterResult(ImmutableArray<IModelFormatAdapter> Adapters,
    ImmutableArray<ModelAssetError> Errors);
public static class HalconModelFormatAdapters
{
    public static HalconModelAssetAdapterResult Create(HalconModelAssetAdapterProfile profile,
        HalconModelAssetAdapterPorts ports, ModelAssetsHostSlot rootSlot);
}
public sealed record ModelAssetDeviceDescriptor(string Id, string Revision, string Backend,
    CanonicalValue DeviceId, string DeviceType, string DeviceName, string RuntimeVersion, int MaxBatchSize);
public sealed record ModelAssetDeviceResolution(ModelAssetDeviceDescriptor? Descriptor,
    ImmutableArray<ModelAssetError> Errors);
public interface IModelAssetRuntimeDeviceResolver
{
    ModelAssetDeviceResolution ResolveDescriptor(string deviceRef);
}
public sealed record ModelAssetChallengeInput(OperationContext Context, AssetRef RootRef,
    ImmutableArray<AssetRef> GraphRefs, FormatDescriptor Format, SemanticSnapshot RuntimeSnapshot,
    AssetRef ChallengeRef, IFormatMaterializationLease Materialization);
public sealed record ModelAssetChallengeReport(AssetRef RootRef, AssetRef ChallengeRef,
    string MethodId, string MethodRevision, Digest ExpectedEvidenceDigest,
    Digest ObservedEvidenceDigest, ChallengeOutcome Outcome,
    ImmutableArray<string> Limitations, string? ReportReceiptRef);
public interface IModelAssetChallengeExecutor
{
    ValueTask<PortResult<ModelAssetChallengeReport>> ExecuteAsync(
        ModelAssetChallengeInput request, CancellationToken token);
}
```

C.5文本中的DeviceDescriptor是本声明`ModelAssetDeviceDescriptor`的简称，不能创建另一个同义契约；ModelAssetChallengeInput.ChallengeRef必非null，adapter在原请求null分支不构造此input。Challenge方法/schema/样本Ref已登记，executor输出digest只作证据摘要，不用它判程序采用；原Input预算、borrowed Materialization及worker resource规则不变。格式工厂不替代生产者实际算法的工厂，后者按其本模块永久会话指导实现。


### C.8 真实Authority的权限桥与用途证据分离

权限映射只读依据为[IM-004 authorization公开契约§3/§5.3/§8.1](../authorization/DEVELOPMENT-GUIDE.md)。Host的`IAssetUsageAuthority`适配实现遵本节固定接线，借用AU.IAuthorizationPort、AU.IAuthorityFence、受信主体Context与用途证据Provider；不把AU类型加入PureCore/S1公共API，不在模型Service暗创建认证/登录服务。用途证据Provider归原匹配/OCR/AI/程序Owner，输入必须是AccessInput完整scope/exact closure/principal/purpose/action，输出Approved/Denied/Unknown及其不可变EvidenceRef、Version、有效期和RevocationPolicy；技术资产adapter不能将AU Allowed当质量证据。Provider必须无UI调用并执行自己的真实Owner验证，不能接受调用方自报Approved。

Host绑定包含当前AU.AuthorizationContext、可信AU.PolicyRef、三ActionRef修订、ScopeId、PurposeCode目录、用途Provider、TimeProvider、MaxPermits/MaxCalls/MaxWatchEvents/PermitTtl和cleanup。TenantId/SubjectId分别匹配ModelAssetsScope.TenantId/PrincipalRef，Issuer/Session/AuthEpoch/Host来自原认证Owner，不从字符串主体生成凭据。目录版本由Host已批准命令注册冻结；binding值无缺省，未登记Policy/用途/主体拒Create。权限资源固定AU.ResourceRef.Type=`model-asset-closure`，Id=`ma-`+SHA256(scope+完整closure Root/GraphRefs/Purpose JCS)hex、Revision=1、ScopeId为可信Host固定范围；opaque AssetIdentity.RevisionId不转long。资源id不是credential，不使无Owner登记的资源获得权限。

| 本模块action | AU动作Id / Use / purpose | 额外用途条件 |
|---|---|---|
| ReadHistory | `model-assets.history.read` / Read / Host登记历史用途code | Provider可明确HistoryAllowed，不要求生产资格；仍有主体/对象读权限 |
| ReadForUse | `model-assets.use.read` / Read / Access.UsagePurpose映射的固定PurposeCode | Provider对该exact模型闭包/版本、用途及期限Approved；候选/Shadow/Advice/人工决定不能混为生产批准 |
| Export | `model-assets.package.export` / Mutate / Host登记导出用途code | AU当前写Eligibility+审计已确认且Provider允许该purpose/目标范围；本模块不通过导出产生程序采用 |

Authorize顺序：核本实例scope/principal/exact closure→取得原Owner用途证据→AU.AuthorizeAsync当前请求→核完整Decision→IAuthorityFence.ValidateCurrentAsync(request,PureDecision)→先预订/完成原AU.SubscribeAsync→建立local Permit/watch slot→返回Active。AU.AuthorizationRequest.RequestId/CorrelationId用Host在原model操作root记录的稳定Guid，生成一次后重试保持；它们不加入model核心、不由UI每次重建。CreatedAt/Deadline按原操作剩余单调budget换算可信UTC一次冻结，Approver仅受信绑定提供。Read只能使用非Historical、Policy.Allowed、GateError无错误、AuthorityEvidence当前且未到期的决策；不能因Read的Eligibility=Blocked（AU设计不授写）误拒合法只读。Export另要求Eligibility=EligibleAtEvaluation、Audit.Persisted且原回执匹配；任何Pending/HistoricalReplay/Indeterminate/审计Unknown均不产生Active Permit。Purpose provider Unknown也不降为HistoryAllowed。

PermitId/fence为本adapter原AU RequestId+精确AuthorityEvidence（Domain/Generation/SnapshotId/Policy）及Purpose证据版本的本地不可变绑定，不伪称数据库/设备fence；ExpiresAtUtc=min(AU决策有效期,用途证据有效期,Host有限PermitTtl)，EvidenceRef标明权限审计和用途证据两个独立来源，不能写质量PASS。Authorizations/原calls/watch先root登记，AU任务晚到仍被同slot观察；接口Subscribe为同步，因而在Authorize返回Permit前已完成上游异步Subscribe，后续Subscribe只附本地有界observer、即时返回当前Active/SnapshotRequired/Disposed；上游未订阅/缺口/断连不能先交成功Permit再补。

ValidatePermit每次核原Permit subject/fence/Scope/到期/用途证据最新版本，执行AU.RecheckAsync（新的明确授权RequestId，由原Permit slot逐验证ordinal生成并记录，有界MaxCalls）及当前IAuthorityFence；不把原GetOperation HistoricalReplay作为当前许可。等待取消不撤销/Dispose仍在执行的AU任务；真正请求取消按原AU.CancelAsync，原task仍强持。新权威版本不自动改原Permit.Fence，必须新Acquire建立新Permit；Denied/Revoked/Expired分别映射本模块状态，Unavailable/未知映射Unknown；Release只关闭本adapter所得订阅、permit及借用pins，绝不Stop/Dispose共享AU服务或改用途事实。

AU通知是失效提示而不是原子设备/业务提交权。序列缺口/乱域/断连→SnapshotRequired、local admission禁新、重新当前核权；旧Generation或迟到Allowed不恢复Active。默认桥**不宣称全局即时撤回**：AuthorityCapabilitySnapshot按B.3反映只有当前重核/订阅、不能远程原子动作的能力，严格即时策略在副作用前MA-CAP。AllowCurrentUntilExpiry仅在用途Owner明确允许时使用，DenyNewAndDrain按§8A停止本地新借用并合作排空；实际跨进程“撤回与新动作”的共同原子边界须由原Authority/Host提供同域guard，不能拿IAuthorityFence的一次返回当这种能力。该限制是已明确能力边界，不留给实现者猜测或客户补软件接口。

在§13既有Service.Tests protocol加MA-AU-01（可控公开AU端口）：Allowed read但写Eligibility Blocked仍合法历史读；权限Allowed而用途Unknown不产生生产Permit；订阅Pending不给Permit、HistoricalReplay不复用、Recheck变化/断连禁新；原AU任务/订阅在有限关闭前真退出，借用AU不Dispose。真实认证/审计/用途证据值归各事实Owner，mapper与资源协议由本节冻结；不以simulate许可证明真实权限或生产资格。


### C.9 兼容影响与既有消费者同步边界

本次不是全部“只补文字”：新增具体adapter/profile/schema/codec/工厂声明，并修正了SD Stage身份派生及导入依赖保持的执行要求。当前只有文档规格，未修改任何产品工程/消费者实现，不宣称已经有运行中的v0.3.0桥可迁移。

| 变更 | 兼容影响 | 需要同步的既有消费者/Owner |
|---|---|---|
| 附录A/PureCore四入口、模型核心JCS、旧原规则/Golden；原Service v0.3公开方法/DTO及operation-jcs-v2 | 原类型签名/单位/摘要与数字精度语义不变；没有重新规范旧资产 | Core/S1既有消费者无需修改；已有资格/历史模型不能重算为本版新模型 |
| SD Stage子operation/ObjectId改为显式model-sd-stage-jcs-v1投影（包含父OperationId/RequestDigest、Scope/Store） | 属桥的身份算法修正，不能用新算法查询/重发旧Unknown；原已seal对象/回执仍按旧完整identity读取 | IM-014自身StorageDatabase桥/其恢复Host同步；IM-066 storage-database公开API/DTO/Owner epoch语义不改，无须改其代码；主控只协调原会话接入确认 |
| 导入封存保护全部三Purpose显式依赖，C.1完整根/Origin耐久定位/同事务CAS | 注册前即检查全部显式目标；未满足RebuildSource/ValidationEvidence的技术资产不能按完整新封存成功。未给ModelAssets删除、质量/设备权；旧已seal资产不追改 | alignment-2d、ocr、ai-inference及工程导入Host在实际接入本版时提供全部声明依赖/旧metadata；无需改其公共算法DTO，不能把缺来源伪装成空依赖以通过新封存 |
| C.1/C.2/C.3/C.7新工厂/profile/固定注册包及只读缓存 | 是可选真实适配的新增装配合同；默认无持久/native缓存，原Store/Source/Authority/Sink端口签名不变；SD ObjectReceiptRef具体编码仅本SD桥使用 | 实际选择这些新adapter的匹配/OCR/AI/工程Host更新显式装配/Root/cleanup；未选择者无需改。replay、integration-transport、delivery-migration若仅消费既有AssetRef/技术bundle无需改其契约 |
| C.4 detached签名证据 | 不改变bundle.json/PackageDigest/模型Ref；签名在包外，验证不授用途/生产资格 | 要求签名的工程包入口Host及客户安全Owner登记信任/调用验证；普通技术bundle消费者无须改。未经批准不能给其它模块包schema加signature字段 |
| C.5新HALCONadapter schema/runtime白名单、challenge端口 | 新登记schema/adapter修订只约束选择该adapter的请求；不会改已seal producer schema/参数单位、自动值或数值容差。旧不同schema保留，不能静默换为新schema后假称读回一致 | alignment-2d/ocr/ai-inference的生产者接入Host同步真实Semantics/Runtime映射与ChallengeExecutor；需要变更其模块公开输入/输出时须回原永久会话修其指导，此处不代改/代审 |
| C.8权限与用途证据桥、默认不宣称全局即时撤回 | 只补明既有权限/用途分权及具体公开AU映射；不把历史Allowed变成当前Permit，不新增产品采用/质量权 | IM-004 authorization公开契约无需修改；实际Host接线需提供受信Context/Policy/Purpose证据及watch。U1公开装配/双STA/三语/预览摘要不变，无须消费者修改 |

实际接入升级先保留原binding/adapter/rule版本、原OperationIdentity/文件对象/journal/Profile及旧只读解析；Unknown按**原**版本查询，不自动以新StageKey重发、改ObjectReceiptRef、改Generation或清目录。新请求显式选择本版新注册包/adapter修订，须通过对应新增断言后才启用能力；不更改旧回执/原core hash/旧规则。此兼容说明供总控协调上述模块原会话，不授权派发新会话、跨模块改文件或总控代审核模块内容。
