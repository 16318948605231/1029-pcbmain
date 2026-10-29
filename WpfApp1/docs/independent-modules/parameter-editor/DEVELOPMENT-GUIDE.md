# 通用参数编辑器独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2`

- **模块**：`parameter-editor`；独立模块编号：`IM-062`；历史映射：`PKG-051`。
- **版本**：`0.2.3-prep`；Core API：`v0.2` / WPF API：`v0.2-u1` 公开形状保持；§18.1 给出当前全部批准范围的文档准备结论。§3.2.1 Decimal/Pixel增量既有接收保持。
- **状态**：C1/C2 六项及 §3.5 完整 Golden 已由主控内容接收，`ModuleCoreImplementationReady`；U1 §11.5/11.6及§14/15/18相关指导已限定内容接收，真实WPF/UIA/产品资格仍 `PreparationIncomplete / NotReady`；0.2.2-prep Decimal/Pixel增量已获主控限定内容接收，既有接收保持；A1 实际消费者/交付资格未验。
- **日期**：2026-10-11（全部批准范围文档收口；既有研究/向量/接收复用）
- **技术基线**：Core 为 C# / .NET 10；可选 WPF + 本机 DevExpress 25.2.3。Core 不引用 AsunImage；视觉宿主通过相应视觉模块的公开端口使用 `ImageLibDotNet.cv2`。
- **消费者**：独立离线算法参数工具、独立设备参数工具；另可接配方编辑器和工程工具。两个消费者的实际接入验收见 §16。
- **事实 Owner**：Core 拥有编辑会话、参数草稿、校验、差异、撤销和操作关联；领域 Owner 拥有参数定义、外部配置、审批、设备实际值和质量事实。
- 模块级设计评审态：`DesignReview`（方案可评审）。§18.1「当前全部批准范围的文档准备结论」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本页是本模块唯一实现和复核依据，遵循独立模块架构、DEV-GOV-005/010 和 DEV-UI-040/043。平台 Contract/Schema 映射仍按其 Owner 采纳，不与模块值类型混用。本轮只完善文档；公开形状修正是未实现 v0.1 的替代设计，不声称已有客户端兼容，也不迁移参考项目。

## Core implementation binding

- 唯一 Core：`src/Modules/parameter-editor/Asun.Modules.ParameterEditor.Core/Asun.Modules.ParameterEditor.Core.csproj`，`net10.0`，namespace `Asun.Modules.ParameterEditor`；公开契约放同一程序集，不预拆第二个 Contracts DLL。
- 唯一 Core 测试：`tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Core.Tests/Asun.Modules.ParameterEditor.Core.Tests.csproj`。最小无 UI Host 和模拟端口作为该测试工程具名测试夹具，不能成为产品默认 Adapter。
- 可选 UI：`src/Modules/parameter-editor/Asun.Modules.ParameterEditor.Wpf/Asun.Modules.ParameterEditor.Wpf.csproj`；`net10.0-windows`、UseWPF；namespace `Asun.Modules.ParameterEditor.Wpf`。UI 测试及独立桌面 Host：`tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Wpf.Tests/Asun.Modules.ParameterEditor.Wpf.Tests.csproj`。上述工程尚未创建；共享 solution/引用由主任务串行接收。
- 后续允许写入仅上述四个精确目录，按 §18 明确切片授权；本轮只允许本页。禁止其它模块、产品 Shell/Domain/Integration、共享合同、用户配置、参考项目、`docs/references` 原件、AsunImage 内部和设备 SDK 实现。
- 产品代码开工前须绑定权威仓库/分支或获确认的可审计代码快照；本地无 Git 元数据不阻断文档。纯 Core 不等待客户阈值、HALCON 或 WPF 资格；通过六项文档条件后仍须主任务接收，不能凭本页自行开工。

## 1. 目标、职责与禁止边界

### 1.1 全部能力与数据流

1. 接收领域声明的动态强类型 Schema 和外部基线；冻结来源/版本/hash，不反射业务对象猜定义。
2. 无 UI 完成文本解析、单位投影、类型/范围/步长/文本/关联校验、字段状态、单改/原子批改/独立项部分修改、差异和 Undo/Redo。
3. 产生建议请求、不可变候选及采用前差异；显式采用只改草稿，算法建议由外部 Provider 产生。
4. 对精确草稿和输入引用发试算；保留执行、有效性、拒识和结果引用，不判生产质量。
5. 生成四态 Patch 意图，经注入 Apply Port 发给外部 Owner；支持原请求查询、明确成功后接收新基线、三方冲突和显式重基。
6. 提供无 UI 生命周期、类型化事件、操作查询和可选 WPF Inspector；UI 与脚本共享上述操作。

~~~text
Owner Schema/基线 → Core 草稿/校验/差异
                 → 推荐 Provider → 候选 → 人工采用 → 草稿
                 → Preview Adapter → 工程结果（不写生产事实）
                 → Patch → Apply Port → 外部 Owner CAS/查询
外部成功回执 → 显式接收基线；冲突 → 三方差异 → 显式选择
WPF / 无 UI Host → 同一 Core API
~~~

### 1.2 禁止边界

- 不拥有制程阈值、缺陷类别、质量规则、配方发布/激活、工单/板身份或设备安全流程。
- 不持私表、裸路径、SDK/HALCON handle、产品 ViewModel、静态可变缓存；不靠隐藏窗口、全局 Culture 或 Service Locator 初始化。
- 不把编辑成功、建议、试算完成、持久回执、设备 ACK、实际回读和质量 PASS 合并。
- 不自动填缺值、钳位、改阈值、选第一候选、重发未知写入或清除外部事实。
- 参数校验、差异、依赖和事务为非视觉功能，HALCON 不适用；视觉候选及 ROI 粗精算法由其模块权威冻结，§8.3 只规定消费边界。不得在参数编辑器维护第二份视觉路线。

### 1.3 Owner 与依赖

| 内容 | Owner | 本模块责任 |
|---|---|---|
| 定义/范围/单位/默认/依赖/敏感性 | 领域定义 Owner | 校验并冻结 |
| 草稿/代次/Undo/操作记录 | 本模块 session | 唯一写入、实例隔离 |
| 推荐方法及证据/模型 | 注入推荐 Provider | 关联、拒旧、显式采用 |
| 试算算法/原图/模型/原生租约 | Preview Adapter 及视觉 Owner | 不取得 native 所有权 |
| CAS/持久化/权限/设备/审批 | 外部 Owner 与 Apply Port | 意图、查询、回执验证 |
| 语言/主题/页面组合/布局持久化 | 宿主 | 提供可嵌入 UI，不建产品页面 |

Core 只依赖 .NET 10 BCL。WPF → Core + 安装的 DevExpress；宿主 Adapter → Core；Core 不反向引用 WPF、平台实现或其它模块业务流程。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.ParameterEditor.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"Core 只依赖 .NET 10 BCL"；WPF 控件切片单向引用 Core。

**Blazor/Web**：参数看板通过 gRPC/REST 查询；参数修改须走草稿→确认流程，不经浏览器直接写入生产配置（同 `configuration` §1A 的"Web 端只读"规则）。`Watch` 参数变更通知经 SignalR 推送到 Web 看板。

**AI 参数学习集成**：`ai-dataset-governance` §7.4.2（L2）记录工程师每次通过本模块的参数修改事件（`ParameterModificationEvent`），作为监督信号供 L2 分析；本模块负责记录修改事件并带来源标记（`Source`），`ai-dataset-governance` 负责分析。

**HALCON 不适用**：本模块是纯参数管理，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 构造、端口与有界资源

### 2.1 构造契约

以下及后续 C# 块为同一 namespace 下的声明片段；实现者不得从例子另造 API。所有传入集合必须深复制冻结，所有返回集合不得暴露内部可变实例。

~~~csharp
public sealed record PeResult<T>(
    bool Succeeded, T? Value, IReadOnlyList<EditorError> Errors);
public sealed record EditorError(
    string Code, ParameterKey? Key, string MessageResourceKey,
    string RecoveryResourceKey, string? DiagnosticRef);

public sealed record ParameterResourceBudget(
    int MaxParameterCount, int MaxTextChars, long MaxSchemaBytes,
    long MaxSnapshotBytes, int MaxDependencyNodes, int MaxDependencyDepth,
    int MaxBatchEntries, int MaxUndoEntries, long MaxHistoryBytes,
    int MaxPreviewQueueDepth, int MaxOperationRecords,
    int MaxPreviewItems, long MaxResultBytes,
    int MaxNotificationDepth, int MaxSuggestions);
public sealed record ParameterOperationPolicy(
    TimeSpan OperationTimeout, TimeSpan CloseTimeout);
public sealed record ParameterEditorOptions(
    ParameterResourceBudget ResourceBudget,
    ParameterOperationPolicy OperationPolicy);

public enum EditorAction { View, Edit, Preview, Recommend, Apply, Query }
public sealed record AccessQuery(
    SessionId SessionId, EditorAction Action,
    IReadOnlyList<ParameterKey> Keys, ContentRef Schema, string SnapshotSha256);
public sealed record AccessDecision(
    bool Allowed, DateTimeOffset ValidUntilUtc, CancellationToken Invalidated,
    string? ErrorCode);
public interface IParameterAccessPolicy {
    AccessDecision Check(AccessQuery query);
}
public interface IParameterEditorFactory {
    PeResult<IParameterEditorSession> Create(
        ParameterSchema schema, ParameterBaseline baseline,
        ParameterEditorOptions options, IParameterAccessPolicy access,
        TimeProvider timeProvider,
        IParameterPreviewExecutor? preview = null,
        IParameterRecommendationProvider? recommendation = null,
        IParameterApplyPort? apply = null);
    PeResult<IParameterEditorSession> Restore(
        ParameterSchema schema, EditorCheckpoint checkpoint,
        ParameterEditorOptions options, IParameterAccessPolicy access,
        TimeProvider timeProvider,
        IParameterPreviewExecutor? preview = null,
        IParameterRecommendationProvider? recommendation = null,
        IParameterApplyPort? apply = null);
}
~~~

实现类型 `ParameterEditorFactory` 为无参公开构造，实现上述 factory；不读环境/当前用户/产品/全局配置。Create 先验预算、Schema结构、规范摘要、基线结构/类型、View 权限，再返回 `Ready` 的 session；失败返回无 session 的 PeResult，不能构造类型或身份错误的可编辑实例。基线若缺Required/违反当前范围或关联，保留真实值并在Read/Full Validate中列错误，不补默认；所有后继编辑的完整候选必须Full有效，可一次Atomic修正全部问题。空 Schema 合法且为 Empty 投影，空批改/空 Patch 非成功。

`PeResult` 成功时 Value 非 null、Errors 为空；失败时 Value 为 null、Errors 至少一项。业务错误以此返回；不以异常文案作协议。端口抛异常转 `PE-9001`，仍排空。不可预料不变量失败为 `PE-9003` 并阻断新写；调用前已取消也返回类型化错误，不调用端口。

预算来自消费者 Profile；不提供默认数值。参数数、字节、表达式规模、批改、历史、结果和通知均先预检；MaxPreviewQueueDepth 允许 0（仅当前一个执行名额），MaxUndoEntries 允许 0（允许编辑但不存 Undo/Redo，Undo/Redo 返回 PE-1013）；其余为正且数值可表示。启用 Undo 时容量满拒绝新改动，需宿主显式开启新会话或批准新预算，不静默淘汰历史。Apply 每 session 最多一项未决，不排写队列，拒绝第二请求；建议与预览共用一个执行名额和有界等待队列，避免同实例全局 Drain 干扰其它操作。

十五项预算的计账单位不可互换：MaxParameterCount 包含全部定义（不只是可见行）；MaxTextChars 为每个字符串的 UTF-16 长度，包括 ID/resource key/Pattern；MaxSchemaBytes/MaxSnapshotBytes 为各完整规范载荷字节；MaxDependencyNodes/Depth 包含所有 AST 和显隐图遍历；MaxBatchEntries 为每批唯一 key 数；MaxUndoEntries 分别限制 Undo/Redo 栈条数，MaxHistoryBytes 是两个栈及保留操作的请求、结果、推荐候选、错误、回执和 checkpoint 临时输出的总逻辑载荷字节；共享不可变对象仍按每个逻辑引用载荷计账，不能借对象复用绕预算。MaxPreviewQueueDepth 是推荐/试算共同等待数；MaxOperationRecords 含全部活动/历史操作及查询的原记录；MaxPreviewItems/MaxResultBytes 分别限制完整单次结果条数/载荷，后者也适用于推荐与 Apply 回执；MaxNotificationDepth 限每订阅待交付数，另最多一项在执行回调；MaxSuggestions 限每推荐候选数。结果计入 MaxResultBytes 后仍计入 MaxHistoryBytes，不提前清掉候选来接纳下一请求；超限返回 PE-4003 并保留原 Task/借用与原 Apply 查询关联，绝不接收部分载荷。保留操作满时拒新操作；没有未声明的自动逐出机制。

TimeProvider 仅用于期限/计时，可在模拟 Host 注入测试时钟；不是系统时间写入权威。Core 异步工作使用 .NET 后台任务，不捕获 UI Dispatcher；不声明不存在的 scheduler 注入接口。预览防抖、自动试算和显示合并只属 §11 宿主策略。

### 2.2 权限与资源交接

AccessPolicy 是宿主绑定身份的同步、无阻塞当前决策端口；不接收调用者自报角色。Core 在锁外 Check，再在会话短锁内复核冻结的代次/生命周期和Invalidated；端口不得回入 session 或执行 IO。拒绝/异常/过期/失效token均 `PE-2002`。异步操作关联该token到停止请求，释放后解除注册；宿主撤权必须取消相应token，不能只等下次点击。每次读取、修改、采用、派发和结果披露重新检查；编辑权不含 Apply，推荐历史不能授予当前编辑权。

Core 的检查不证明远端授权原子性：实际推荐/试算/写入端口在其调用、持久化和披露边界独立核当前权限、来源及最早期限；不可把 AccessDecision 作为远端凭证。无当前 View 权时 Read/历史载荷/事件后读取返回无载荷，不删除原证据。单次 Read 披露全 Schema/草稿，必须核完整 Keys 的读权；不以过滤 UI 偷看其它字段。

factory 借用端口、不 Dispose 宿主共享端口；端口须支持按 OperationId 独立排空。Core 拥有自己的队列、CTS、不可变记录和订阅。跨所有路径遵循 Adapter 子借用先归还、父租约后归还；只有实际释放回执才可归还 Core 的操作输入引用。

Core 在所有异步派发前预留完整请求字节及 MaxResultBytes 响应空间，均计入 MaxHistoryBytes；名额/记录/字节任一不足不调用端口。响应复制前有限计数，合法后以实际字节替换预留；未知 Task 仍持预留，不能借 deadline 释放额度。宿主构造 Adapter 时绑定相同或更保守的 Profile 上限（必要时在 Create 返回后、首操作前按 SessionId 绑定）；端口先验输入/响应规模再分配图像/模型/候选，不因请求 DTO 没有预算字段就无界分配。端口自己的实际 Managed/Native/lease 上限仍在其 Profile/Owner，不把 Core 的逻辑字节预算当 native 测量。

## 3. 强类型参数、单位、依赖与规范编码

### 3.1 值与定义

~~~csharp
public readonly record struct ParameterKey(string Value);
public readonly record struct SessionId(Guid Value);
public readonly record struct OperationId(Guid Value);
public sealed record ContentRef(string Id, string Version, string Sha256);

public enum ParameterValueKind {
    Boolean, Int64, Decimal, Enum, Text, Duration, Angle, Length, Area, Ratio
}
public enum UnitCode {
    None, Count, Pixel, Decibel, Microsecond, Millisecond, Second,
    Degree, Millimetre, Micrometre, SquareMillimetre, SquareMicrometre, Percent
}
public abstract record ParameterValue {
    public sealed record Bool(bool Value) : ParameterValue;
    public sealed record Int64(long Value) : ParameterValue;
    public sealed record Decimal(decimal Value) : ParameterValue;
    public sealed record Enum(string Value) : ParameterValue;
    public sealed record Text(string Value) : ParameterValue;
    public sealed record DurationMicroseconds(long Value) : ParameterValue;
    public sealed record AngleDegrees(decimal Value) : ParameterValue;
    public sealed record LengthMillimetres(decimal Value) : ParameterValue;
    public sealed record AreaSquareMillimetres(decimal Value) : ParameterValue;
    public sealed record Ratio(decimal Value) : ParameterValue;
    public sealed record Null() : ParameterValue;
}
public enum ValueOrigin { Explicit, Default }
public sealed record ParameterEntry(ParameterValue Value, ValueOrigin Origin);
public sealed record Bound(decimal Value, bool Inclusive);
public sealed record NumericConstraint(
    Bound? Minimum, Bound? Maximum, decimal? Step, decimal StepOrigin);
public enum WhitespacePolicy { Preserve, RejectOuterWhitespace }
public sealed record TextConstraint(
    int MinUtf16Length, int MaxUtf16Length, WhitespacePolicy Whitespace,
    string? Pattern, TimeSpan? RegexTimeout);
public sealed record AllowedValue(
    string Value, string DisplayNameResourceKey, bool Retired);
public enum ApplyMode { OwnerDefined, OnStop, RecreateInstance }
public sealed record ParameterDefinition(
    ParameterKey Key, string DisplayNameResourceKey,
    string DescriptionResourceKey, string CategoryResourceKey, bool Advanced,
    ParameterValueKind ValueType, UnitCode Unit, UnitCode DisplayUnit,
    NumericConstraint? Numeric, TextConstraint? Text,
    ParameterValue? DefaultValue, bool Required, bool Nullable, bool ReadOnly,
    ApplyMode ApplyMode, IReadOnlyList<AllowedValue> AllowedValues,
    ParameterPredicate? VisibleWhen, ParameterPredicate? EditableWhen,
    string DefinitionVersion, ContentRef SourceRef);
public sealed record ParameterSchema(
    ContentRef Identity, string CanonicalizationVersion,
    IReadOnlyList<ParameterDefinition> Definitions,
    IReadOnlyList<ParameterConstraint> Constraints);
public sealed record ParameterSnapshot(
    ContentRef Schema, long Generation,
    IReadOnlyDictionary<ParameterKey, ParameterEntry> Entries,
    string ContentSha256);
public sealed record ParameterBaseline(
    ContentRef Owner, long Revision, ParameterSnapshot Snapshot);
~~~

Key 固定 ASCII `^[a-z][a-z0-9_.-]{0,127}$`，Ordinal 大小写敏感比较；显示名称不充当身份。ContentRef 的 Id/Version 非空、有界；Sha256 是 64 位小写十六进制，不能替代来源授权。Generation 是本地非负草稿代次；Revision 是外部非负版本，两者永不混用；任何加一耗尽都 `PE-1015`，不回绕。Owner/Schema/DefinitionVersion 分别记录。

DefaultValue 的 C# null 表示无默认；显式参数 null 为 `ParameterValue.Null`；Entries 不含 key 表示 Missing；空 Text 为第四种实际文本值。Required 拒 Missing；Nullable 控制显式 Null，Required+Nullable 允许显式 Null。ResetDefault 使用 Owner 的合法 DefaultValue 并标 Default，不表示删除；不允许从零值或 GUI Reset 猜默认。ReadOnly 禁止任何 Set/Remove/Reset，不受专家模式影响；ApplyMode 只交给外部 Owner，不触发设备。

数值类型必须有 Numeric（边界本身可空）；布尔/枚举/Text 的 Numeric 必须 null。布尔/枚举 Text 为 null；Text 必须有 TextConstraint，其长度上限还受预算。Enum 的 AllowedValues 非空、稳定值唯一；未知值拒绝，退役值允许保留原基线并告警，禁止新写或恢复为退役默认。默认必须通过定义完整校验。未知类型/单位/枚举拒绝，不保存为 Text 逃避约束。

Origin=Default必须有该Schema的合法DefaultValue且Entry.Value精确等于它；Set始终Explicit，ResetDefault才写Default，不允许Import/推荐通过Origin伪造默认。基线/恢复中的退役enum仅在未改key保留并Warning，修改为该退役值或Reset退役Default拒绝；Full不因其它字段改变把保留值误判新写，但新Schema的默认退役仍创建拒绝。Schema身份/来源相同的不可变定义不运行时改ReadOnly/Default；变化须新Schema/迁移。敏感字段不另增未声明flag：由当前View策略决定整个字段集合披露，不能读取再用UI隐藏冒充脱敏。

Int64/Duration 的 Minimum/Maximum/Step/StepOrigin 必须都是 long 可表示的整数；其它数值使用 decimal 精确算术。非 Enum 的 AllowedValues 必须为空；VisibleWhen/EditableWhen 缺省分别 True/True，再叠加 ReadOnly/权限。每个字段的编辑条件按最终完整候选求值，对实际变化 key 核权；未改的只读字段仍校验但不要求 Edit 权，支持只读前像参与约束。Nullable 字段与 Null 字面值等/不等是明确例外：Literal Null 的 Unit=None，只可与 Nullable 字段作 Equal/NotEqual；其余 Compare 必须同 kind/规范单位。条件引用 Missing/Null 的 Unknown 语义仍按 §3.3。

### 3.2 单位、解析与精度

| 类型 | 规范单位与存储 | 允许显示 | 准确规则 |
|---|---|---|---|
| Boolean / Enum / Text | None | None | bool 只接受 true/false；枚举只接受稳定值；显示翻译不能参与编码 |
| Int64 | None / Count / Pixel，long | 同规范单位 | 无浮点中转；最小/最大和步长须为整数；不能把 Pixel 当 mm |
| Decimal | None / Decibel / Pixel，decimal | 同规范单位 | 不接 NaN/Infinity，不作 double 比较；Pixel 是有理像素量，精确规则见 §3.2.1 |
| Ratio | None，decimal | None / Percent | 显式 % 投影乘100；0.72 与72%可逆，72 无%且显示None不能自动除100 |
| Duration | Microsecond，long | us / ms / s | 显示倍率1000/1,000,000；输入转us须整数且不溢出 |
| Angle | Degree，decimal | Degree | 不隐式 rad、wrap或归一化角度 |
| Length | Millimetre，decimal | mm / µm | 显示µm乘1000；负数是否允许由边界决定 |
| Area | SquareMillimetre，decimal | mm² / µm² | 显示µm²乘1,000,000；不从 Length 自动生成 Area |

Step > 0，以 StepOrigin 为格点原点：`(value-StepOrigin)/Step` 必须是精确整数；StepOrigin 默认也必须由定义显式给出，不以 minimum 推断。开/闭边界准确比较，min>max 或相等开界为 InvalidSchema。算术 overflow 拒绝，禁止钳位、隐藏舍入；显示舍入只是投影，重新提交显示舍入值是明确的新编辑。

上述“精确整数”是数学定义，所有数值kind统一使用 §3.2.1 的十进制系数/scale对齐和BigInteger余数判据，不以decimal除法的舍入结果决定格点。long类型先精确提升系数，不先在long/decimal中做可能溢出的差；合法long最小/最大范围与步长可检查，不因为中间差超过long而误拒。约束本身仍须符合声明类型和范围，数值没有跨kind隐式转换。

所有数值解析/显示单位转换也遵循精确有理数规则：有限token按显式culture语法取符号、十进制整数系数及scale，禁止指数/分组/货币/单位后缀；按 §3.2 的有理倍率换算（Ratio百分比÷100、时间ms/s×1000/1000000、长度µm÷1000、面积µm²÷1000000，其余倍率1）。先用有界BigInteger形成准确系数/分母，long目标须整除且在long范围；decimal目标去可消因子及尾零后须为scale≤28、96位系数可准确表示，否则PE-1003，不借decimal.TryParse或decimal除法静默舍入。Format以相反倍率生成有限十进制文本、显式culture小数点、无分组及精度丢失；显示字符串不要求先在decimal中容纳放大后的中间数（如decimal.MaxValue的Percent/µm投影），最终文本在消费边界仍受下段预算，过限PE-4003。文化名无效PE-1010；类型PE-1003、非法单位PE-1007、合法类型数值越界/非格点仍分别PE-1005/1006。共享这套内部纯算法，不扩公开codec入口、不改变§3.4规范值编码。

无 UI 解析入口由 `ParameterTextCodec`（无参公开构造）实现 `IParameterTextCodec.Parse(ParameterDefinition definition, string token, string cultureName, UnitCode inputUnit) → PeResult<ParameterValue>`，以及 `Format(ParameterDefinition definition, ParameterValue value, string cultureName, UnitCode displayUnit) → PeResult<string>`。允许受宿主支持的 cultureName，不改全局 Culture；数值禁止分组符、指数、货币、隐式单位后缀，按该 Culture 的小数点及显式 inputUnit 解析；整数使用符号+十进制整数。显示格式使用同 culture，无分组且保留可逆精度；紧凑舍入另属 UI 显示，不作编辑初值。Text 保留 Unicode 原串；拒孤立 surrogate/控制字符（换行仅 Text 定义明确允许的 Pattern 匹配），不静默 Trim/大小写/Unicode 归一化。空 token 不是 null/remove 指令。

预算接线不增加codec/Attach/Binding参数：创建session的Host保留ResourceBudget，调用Parse前核definition/token/cultureName等每字符串MaxTextChars及定义已准入，Format后在发布前核输出MaxTextChars。Inspector只能从公开session.Read取已准入定义，不能凭空读取不存在的session.Options；其私有token/粘贴/格式输出按§11.5已注册Root.MaximumRetainedBytes预检/预留（含全部缓冲）后才保留/解析/发布，Text还须符合定义的MaxUtf16Length；这些UI私有字符串未传Core，不冒称已核session的原token长度。进入CheckEdits/SetValues的规范值仍由Core按十五项预算核验。直接Attach兼容路径同样按§11.5登记Root，不能绕开UI预算。任一消费边界过限PE-4003，不进入编辑/显示。独立纯codec没有session/Profile，不能声称已检查调用者预算；其数值解析须流式检查语法、首末非零位置及有效scale，零和前后零不扩BigInteger，只在按上述已知10幂倍率确定目标可表示后构造有界系数，不能对任意长token先BigInteger.Parse再试溢出。计数checked；纯工具与ParameterCanonical一样不提供业务准入，不使用环境默认预算。

```csharp
public interface IParameterTextCodec {
    PeResult<ParameterValue> Parse(ParameterDefinition definition, string token,
                                  string cultureName, UnitCode inputUnit);
    PeResult<string> Format(ParameterDefinition definition, ParameterValue value,
                           string cultureName, UnitCode displayUnit);
}
```

Text Pattern 使用 .NET `RegexOptions.NonBacktracking | CultureInvariant`，Pattern 非空时 RegexTimeout 必须有限正值，要求Match.Success、Index=0且Length=整个token长度，不以子串匹配通过。结构不支持/超时 `PE-1010`；不回退无时限引擎。MinUtf16Length≥0，Max≥Min且不超MaxTextChars；非法Unicode先拒。nullable 和文本规范都使用同一无 UI 校验，不由控件掩盖。

### 3.2.1 Decimal/Pixel 加法组合与兼容规则

真实消费者为 measurement-workbench A.10 的 ImageEdgePair.SigmaPx：需要非整数像素量0.4/0.7/1.5，不能用现有Int64/Pixel整数化。本增量仅放开 `ValueType=Decimal、Unit=Pixel、DisplayUnit=Pixel`，值仍 `ParameterValue.Decimal`；没有新DTO、ValueKind、UnitCode或枚举序号。Pixel是像素尺度的数值单位，不是物理长度，不经标定转换mm/µm，不从图像缩放比例改变参数。不增加Decimal/Count/Millimetre/Micrometre/Degree等组合；Int64/Pixel、Decimal/None/Decibel和其它既有路线不变。

结构准入：Decimal/Pixel须有Numeric（Minimum/Maximum/Step可空，但Step存在必须>0，StepOrigin始终显式decimal），Text=null、AllowedValues为空；Required/Nullable/Default/ReadOnly/ApplyMode和显隐关联仍按§3.1–3.3。范围是Schema Owner声明，Pixel组合本身不硬编码HALCON范围/非负性/默认步长；本消费Sigma例使用闭区间[0.4,100]，其它像素参数的范围仍由其Owner给出。负值是否合法看定义，不因名字或Pixel自动钳位；sigma与原ROI半长等跨领域约束归工作台/算法Owner，不在PE复制HALCON算法或替代其Validator。

精度与校验：decimal存有限可表示有理数 `signed coefficient / 10^scale`，不是任意精度或任意分母的有理数。非整数无转long、无double中转；文本token先按§3.2 culture语法读取符号/十进制系数/scale，对去尾零后的数值核decimal可准确表示，超系数/scale拒绝PE-1003，不用decimal.TryParse成功但已舍入的值冒充精确输入。范围准确按开闭界比较；Step=null表示不约束格点而非推断默认步长。Step存在时分别取value、StepOrigin、Step的decimal系数/scale，用BCL BigInteger按共同scale对齐，判断 `(vInteger-originInteger) % stepInteger == 0`；禁止decimal除法舍入后判整数。所需整数位数有界于decimal范围，token消费预算按§3.2、Core值/AST按十五项预算先检查。非格点PE-1006、越界PE-1005；批改/默认/Undo/关联对最终候选按同一路径验证，不在UI补另一套Pixel规则。

Parse/Format唯一公开入口仍是IParameterTextCodec：Parse的inputUnit必须Pixel，Format的displayUnit必须Pixel，与definition.Unit/DisplayUnit精确匹配；Pixel↔Pixel比例恒1。合法输入保留0.4/0.7/1.5，格式按显式culture小数点无分组、可逆精度，单位由行标签或明确参数传递；`"0.7 px"`/`"0.7mm"`后缀仍不合法，不靠token猜单位。inputUnit/displayUnit=None、Count、Millimetre、Micrometre、Degree等任一跨单位，或者定义Decimal/Pixel却DisplayUnit=None，都PE-1007；不作无单位回退。未知unit/非法单位组合在创建session前拒绝，EditorError.Code为PE-1007（无session返回）；未知kind等其它结构错误仍PE-1001，不把所有InvalidSchema改码。编码纯工具仍按§3.4对非法结构抛ArgumentException。条件Compare仍要求同kind/规范单位；Decimal/Pixel与Int64/Pixel不能隐式提升，与Decimal/None不能因数值相同而比较。

一行完整无UI定义（唯一公开构造签名，放在`using Asun.Modules.ParameterEditor;`的Host中）：

~~~csharp
var sigmaDefinition = new ParameterDefinition(new ParameterKey("sigma_px"), "sigma.name", "sigma.help", "edge", false, ParameterValueKind.Decimal, UnitCode.Pixel, UnitCode.Pixel, new NumericConstraint(new Bound(0.4m, true), new Bound(100m, true), 0.1m, 0m), null, null, true, false, false, ApplyMode.OwnerDefined, Array.Empty<AllowedValue>(), null, null, "1", new ContentRef("sigma-fixture", "1", "beb8c3b5c2833f7b26b88e296148eb2f4929245206c7557d1d083c9b69df7f14"));
~~~

该SourceRef摘要是严格UTF8字面`pe-decimal-pixel-fixture-v1`的SHA-256，仅为可构造示例；step=0.1是示例Schema的显式选择，无默认值（DefaultValue=null），不能当生产自动填充。宿主把该定义纳入原ParameterSchema，按§3.4算完整Schema身份；Baseline.Entries显式从真实原Profile取得`ParameterEntry(new ParameterValue.Decimal(...), ValueOrigin.Explicit)`，按原Snapshot编码算摘要，再用已接收Factory.Create。SetValue传同类型和ExpectedGeneration，TextCodec.Parse先返回精确类型值，CheckEdits/SetValues仍作范围/格点/权限/Full校验；解析成功不等于草稿提交成功。真实double算法输入与decimal的双向保真及Profile/ROI资格由measurement-workbench原Owner冻结，此PE增量不猜其桥。

| 必需反例（Core.Tests/TextAndUnitTests 与 SchemaAndCanonicalTests 既有组内） | 输入与预期 |
|---|---|
| 正常非整数 | 上述定义+Decimal(0.4m)/0.7m/1.5m均通过Full校验；分别Parse("0.4"/"0.7"/"1.5","en-US",Pixel)并Format(...,"en-US",Pixel)准确往返；无整数化或隐藏舍入 |
| 范围/开闭界 | 0.4与100合法；0.3、100.1为PE-1005；仅将Minimum改(0.4,false)时0.4拒绝而0.7仍合法；非法min>max仍InvalidSchema |
| 格点 | Step=0.1、Origin=0时0.45为PE-1006；仅改Origin=0.05时0.45合法且0.4非格点；Step=null时0.45合法；Step=0或负数结构拒绝，无草稿/历史改变 |
| 精度/显示文化 | 0.7000与0.7同规范值/旧G29表示；已可表示的decimal边界不经double；`"0.70000000000000000000000000001"`不可准确表示时PE-1003，不能舍入成0.7；按culture显式小数点往返，分组/指数/单位后缀拒绝 |
| 跨单位/类型 | Decimal/Pixel显示或输入mm/µm/None/Count皆PE-1007；Decimal/mm、Decimal/Degree、Decimal/Count仍非法；Int64(1)/Pixel仍合法但不能接受Decimal(0.7)，类型不符PE-1003；同类型跨单位Compare结构拒绝 |
| 兼容性/事务 | 旧None/Decibel/Int64-Pixel及其它合法Schema的规范字节与hash完全不变，§3.5四Golden长度/hash不变；新组合不重标旧Schema/请求；任一越界/步长/权限拒绝使Atomic草稿generation/Undo全不变 |

公开兼容规则：CanonicalizationVersion仍pe-v2-tlv1，`Decimal`叶标签/Invariant G29数值字节、`Pixel`枚举名称、DTO字段序和所有既有编码工具签名不改，不插入枚举值、不改旧codec字节。只有显式增加本组合的**新**Schema产生自己的新hash；不能把旧Int64定义换Decimal却保旧Identity，也不在运行session偷偷升级定义（定义变更仍按§10迁移）。旧实现若只懂先前组合应保原Schema字节并明确PE-1007/不支持，不把新值当Int64或None降级；接入者以本0.2.2-prep限定增量获接收的支持能力再启用新Schema，不能仅以相同DTO/pe-v2-tlv1断言旧实现支持。没有已实现二进制兼容性通过结论。

本次两轮有限自审已分别核：实现者按类型/单位准入→精确parse→范围/格点→同Core Full/事务/format走通；外部消费者用上行公开定义→原Schema/hash/Baseline/Create/SetValue组合，并核PE-1007边界和既有编码不变。0.2.2-prep Decimal/Pixel增量已获主控限定内容接收；不重新审查或降低C1/C2/U1已接收范围，不宣称编译/运行/HALCON/工作台实际接线通过。

### 3.3 无脚本依赖与关联校验

~~~csharp
public enum CompareOperator { Equal, NotEqual, Less, LessOrEqual, Greater, GreaterOrEqual }
public abstract record ParameterOperand {
    public sealed record Field(ParameterKey Key) : ParameterOperand;
    public sealed record Literal(ParameterValue Value, UnitCode Unit) : ParameterOperand;
}
public abstract record ParameterPredicate {
    public sealed record Constant(bool Value) : ParameterPredicate;
    public sealed record Exists(ParameterKey Key) : ParameterPredicate;
    public sealed record IsNull(ParameterKey Key) : ParameterPredicate;
    public sealed record Compare(ParameterOperand Left, CompareOperator Operator,
                                 ParameterOperand Right) : ParameterPredicate;
    public sealed record Not(ParameterPredicate Inner) : ParameterPredicate;
    public sealed record All(IReadOnlyList<ParameterPredicate> Terms) : ParameterPredicate;
    public sealed record Any(IReadOnlyList<ParameterPredicate> Terms) : ParameterPredicate;
}
public enum PredicateState { True, False, Unknown }
public enum IssueSeverity { Warning, Error }
public sealed record ParameterConstraint(
    string RuleId, ParameterPredicate When, ParameterPredicate Assertion,
    IReadOnlyList<ParameterKey> AffectedKeys,
    IssueSeverity Severity, string MessageResourceKey, string RecoveryResourceKey);
public sealed record ParameterFieldState(
    ParameterKey Key, PredicateState Visible, PredicateState Editable,
    IReadOnlyList<ValidationIssue> Issues);
public sealed record ValidationIssue(
    string Code, ParameterKey? Key, string? RuleId, IssueSeverity Severity,
    string MessageResourceKey, string RecoveryResourceKey);
public enum ValidationMode { Full, ChangedOnly }
public sealed record ValidationReport(
    long Generation, string SnapshotSha256, ContentRef Schema,
    ValidationMode Mode, bool IsValid, IReadOnlyList<ValidationIssue> Issues);
~~~

Predicate AST 为数据、无 delegates/反射/任意字符串表达式。Compare 只允许同 kind/规范单位；布尔/枚举/Text/Null 仅等/不等，不比较 Text 大小；排序比较 Missing/Null 为 Unknown，Equal 对两个显式 Null 为 True，任一 Missing 为 Unknown。Exists 区分 Missing 与显式 Null；IsNull 对 Missing 为 Unknown。Not Unknown=Unknown；All 有 False 即False，否则有Unknown即Unknown；Any 有True即True，否则有Unknown即Unknown；All/Any空集 InvalidSchema。不能把 Unknown 当 false 自动隐藏参数。

创建时检依赖引用、AST数/深度、重复 RuleId 和可见/可编辑图环；图边从引用字段指向被控制字段，自引用和环 `PE-1004`。CrossConstraint 是同一候选快照的断言，互相引用的比较不当作显隐图环。Editable 还受ReadOnly和当前权限限制；Visible=False保留原值，仍执行 Required/类型/范围，领域要忽略约束须显式 When。Unknown 显示阻断理由，不能删值。When=False 时该关联约束不适用，Unknown时Error；Assertion Unknown 为错误，不能由Warning降级。ChangedOnly检查编辑集合的传递显隐影响及相交约束；Preview/Patch/Apply始终Full，不以局部绿色获得提交资格。

### 3.4 不可变快照和规范编码

实现使用深冻结值和集合；record 本身不保证深不可变。所有请求/响应/回调均按预算冻结，外部随后改输入不能改变 hash。`ParameterCanonical` 为公开静态纯工具：`byte[] EncodeSchema(ParameterSchema schema)`、`byte[] EncodeSnapshot(ParameterSnapshot snapshot)`、`byte[] EncodePatch(PatchIntent intent)`、`string Sha256(byte[] bytes)`；Encode 遇非法结构抛 ArgumentException（调用边界转PE-1001），不访问Store。Hash使用SHA-256小写hex。

这里的结构拒绝不等于Full业务校验：EncodeSnapshot只持Schema引用，不能从引用查外部定义；它编码结构合法的Missing、显式Null及已准确表示的强类型值，即使该基线/CheckEdits候选存在Required/范围/格点/关联Error也可生成准确内容身份。未知派生叶、非法Unicode/枚举/引用/集合结构仍拒绝；字段与Schema匹配及Origin/默认关系在factory/候选校验边界核。不得把Full.IsValid作为所有Snapshot编码的前置，否则§2允许的真实非法基线和§4演练无法读取/定位。CreatePatch/派发/提交仍必须Full有效，不因存在hash得到资格。

编码冻结为 `pe-v2-tlv1`：开头严格 UTF8 字符串域 `pe-schema-v2` / `pe-snapshot-v2` / `pe-patch-v2`；以下依声明字段顺序。字符串=uint32 little-endian UTF8字节长度+无BOM严格UTF8；不规范化Unicode；bool=1字节0/1；nullable=1字节0/1后值；long=8字节little-endian；decimal=InvariantCulture `G29`字符串（等值尾零/-0规范到同表示）；enum=声明名称字符串；列表=uint32 count+逐项；Guid=小写D格式字符串。禁止float/double。所有domain、长度和内容参与hash，字段名不编码，顺序即协议。

Schema 按声明顺序编码 Identity.Id/Version（跳过自身Sha256）、CanonicalizationVersion、按Key Ordinal排序的完整Definitions、按RuleId排序的Constraints；各record递归按声明顺序，AST/Value先编码叶类型名称再字段。AllowedValues按稳定Value排序，AffectedKeys排序唯一，All/Any保留声明序（虽逻辑可交换，不改来源身份）。Schema.Identity.Sha256须等EncodeSchema的hash。Snapshot只编码Schema三元组、按Key排序的Entries（含Origin和Value）；Generation不参与内容hash，Undo回到相同值可同hash但代次不同。Baseline Owner/Revision不是内容但必须进入Patch请求身份。

封闭编码细节：int（长度外的 MaximumCandidates 等）为 int32 little-endian，uint32长度/数量先检查溢出；Nullable<T> 和可空引用均为一字节存在位再递归值，非空引用不加存在位。记录/ParameterKey 不加类型标签；仅 ParameterValue/Operand/Predicate 的派生叶按声明名称（如 Ratio、Field、Compare）加字符串标签，再按字段序递归。Dictionary 先 uint32 count，再按 Ordinal key 写 key/value。请求内嵌 Snapshot 为 Generation long、ContentSha256字符串、uint32规范Snapshot字节数及 EncodeSnapshot 字节；内嵌 Schema 为 Identity.Sha256字符串、uint32字节数及 EncodeSchema 字节。Baseline 按 Owner 三元组、Revision long、上述内嵌 Snapshot 写入。ValidationReport 写全部声明字段（含 Generation/hash/Schema/Mode/IsValid/Issues），不能只写 Mode/Issues。

请求身份固定为三条，禁止重复包域、Session 或 Schema：① EncodePatch 为域 pe-patch-v2 后按 PatchIntent 字段序全部编码，跳过末尾 RequestSha256；Changes 按 key 排序，Before/After 用可空 ParameterEntry；其 RequestSha256 = Sha256(EncodePatch)，ApplyIntentRequest.Timeout 不产生第二身份，OperationContext 和 ApplyReceipt 的 RequestSha256 均等原 Patch 摘要。修改 Timeout 不能再次派发同一原操作，只可查询。② Preview/Recommendation 为域 pe-preview-v2 / pe-recommendation-v2 + SessionId + 当前 Schema 三元组 + 请求 record 所有字段（仅一次）+ 当前内嵌 Snapshot；输入/证据字典按 key 排序。③ 输入集合摘要为域 pe-inputs-v2 + uint32 count + 排序 key/ContentRef 三元组；Checkpoint 按 §10.2。EffectiveDeadline/RequestEpoch 是本地执行观测，均不加到上述请求 hash；其值不能作为远端授权凭证。时间为 UTC ticks long，TimeSpan 为 ticks long。

Payload预算按真实字节计账，不按字符数代替。旧canonical载荷不重新计算新身份；协议版本不支持即保留原件并拒绝。§3.5 给出完整 Schema/Snapshot/Patch Golden；实现仍须补同值不同代次、decimal尾零、Missing/Null/Default、三语/非法Unicode和前像hash反例，不能只对最终摘要自比。Full报告只有Generation/hash匹配才使用。

集合/AST输入先用迭代有界遍历做节点/深度/精确编码字节计数，checked 累加，检测对象引用环和未知派生类型，再深冻结/编码；不得先完整序列化超大或循环图才查预算。计数和复制遍历均按上限+1停止，不能相信集合 Count 或任意 IEnumerable 已有限；调用方不得并发修改，遍历异常/两遍不一致拒绝，不重试猜值。Core 只发布复制所得只读字典/列表/深冻结 AST；外部保留原 List/Dictionary 再改不改变草稿。纯 ParameterCanonical 工具无 Profile，不提供业务准入保证；消费边界须先完成上述检查才调用它。单位、resource key、ID、文本、数组数量及规范字节总量均受现有预算；不另设无来源默认限值。

传入集合须是有限、同步、无阻塞的内存集合，不把访问器/枚举器当执行代码或 IO 扩展点。响应计账用同 TLV 规则：PreviewResult/RecommendationResult/ApplyReceipt 分别以 pe-preview-result-v2 / pe-recommendation-result-v2 / pe-apply-receipt-v2 域及完整 record 字段序编码；其中 RequestSha256 是原请求引用，必须编码，不跳过。EditorError/ValidationIssue/OperationContext/UndoEntry 按声明序，事件/操作元数据分别用 pe-event-v2 / pe-operation-v2。MaxHistoryBytes 包含完整保留 OperationView 的逻辑载荷（已有结果内嵌只计一次）、Undo/Redo 和 checkpoint 输出；队列里的输入/响应预留也计入；同步读返回复制的临时 Schema/Snapshot 至少分别受对应上限，不把实例内 retained 与调用方持有的投影字节混为实际进程内存。实际托管堆/native/订阅 Task 由 §15 测量。

### 3.5 独立完整 canonical Golden（规范证据，不是产品运行结果）

下列字段独立按 §3.4 构建，未调用产品 Encode；长度和 SHA-256 已用 BCL 之外的独立字节拼接/标准 SHA-256 复算，未来 C# 必须分别断言完整 hex、长度和摘要，不能 Encode 后把自己的输出当 expected。此处仅文档字节核对，不声称 C# 编译/Golden 测试运行。格式块可换行，读 expected 时只去除 ASCII 空白，不重新排序或转 Unicode。

完整公开输入：Schema.Identity=(schema.golden,2,下表 Schema SHA)，CanonicalizationVersion=pe-v2-tlv1；Definitions 恰一项，按 ParameterDefinition 字段序为 Key=ratio、DisplayNameResourceKey=ratio.name、DescriptionResourceKey=ratio.help、CategoryResourceKey=parameters、Advanced=false、ValueType=Ratio、Unit=None、DisplayUnit=Percent、Numeric=(Minimum=(0,true),Maximum=(1,true),Step=0.01,StepOrigin=0)、Text=null、DefaultValue=Ratio(0.5)、Required=true、Nullable=false、ReadOnly=false、ApplyMode=OwnerDefined、AllowedValues=[]、VisibleWhen=null、EditableWhen=null、DefinitionVersion=1、SourceRef=(definitions,1,64个d)，Constraints=[]。外部 Owner=(owner.golden,1,64个e)，Revision=7。BeforeSnapshot=(该 Schema 三元组,Generation=0,{ratio:Ratio(0.5)/Explicit},BeforeSnapshot SHA)；ProposedSnapshot=(同 Schema,Generation=1,{ratio:Ratio(0.72)/Explicit},ProposedSnapshot SHA)。

完整 Patch：SessionId=11111111-1111-1111-1111-111111111111，OperationId=22222222-2222-2222-2222-222222222222，IdempotencyKey=golden-key，Scope=golden，Before 为上述 Owner/Revision/BeforeSnapshot，Proposed 为上述 ProposedSnapshot，Changes=[(ratio,Ratio(0.5)/Explicit,Ratio(0.72)/Explicit,None)]，Validation=(Generation=1,ProposedSnapshot SHA,Schema 三元组,Full,true,[])，RequestSha256=下表 Patch SHA。d/e 来源 hash 仅编码夹具引用，不证明来源真实性。编码工具只跳过当前对象自身摘要字段；构造 Schema/Snapshot 身份时允许该对象摘要字段为约定的64个零占位，先计算规范字节再回填摘要，之后所有消费边界必须拒绝零占位和不相等摘要；其它引用摘要始终须合法。

| 完整域 | 字节数 | SHA-256 |
|---|---:|---|
| Schema | 305 | `ddce494783db701bd58b740a6324b834d861e0322a70ba6428fc9e578c930fc8` |
| BeforeSnapshot | 149 | `c35a1c8c94385c17a0f014ffa920bb4cbfd0507c908a86d9fe4bdf2d58603989` |
| ProposedSnapshot | 150 | `8c4ec9075d5e5bc5f630ea98b8789a08a87351c2aa7676d60b7fea35fe34e3ff` |
| Patch | 934 | `0354206ca4ddc69d547968d92e54da0f3c5c76f76cfd38794ad226773ba9a53e` |

Schema 全字节：

~~~text
0c00000070652d736368656d612d76320d000000736368656d612e676f6c64656e01000000320a00000070652d76322d
746c76310100000005000000726174696f0a000000726174696f2e6e616d650a000000726174696f2e68656c700a0000
00706172616d65746572730005000000526174696f040000004e6f6e650700000050657263656e740101010000003001
010100000031010104000000302e30310100000030000105000000526174696f03000000302e350100000c0000004f77
6e6572446566696e656400000000000001000000310b000000646566696e6974696f6e73010000003140000000646464
646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464646464
6464646464646464646464646400000000
~~~

BeforeSnapshot 全字节：

~~~text
0e00000070652d736e617073686f742d76320d000000736368656d612e676f6c64656e01000000324000000064646365
343934373833646237303162643538623734306136333234623833346438363165303332326137306261363432386663
3965353738633933306663380100000005000000726174696f05000000526174696f03000000302e3508000000457870
6c69636974
~~~

ProposedSnapshot 全字节：

~~~text
0e00000070652d736e617073686f742d76320d000000736368656d612e676f6c64656e01000000324000000064646365
343934373833646237303162643538623734306136333234623833346438363165303332326137306261363432386663
3965353738633933306663380100000005000000726174696f05000000526174696f04000000302e3732080000004578
706c69636974
~~~

Patch 全字节：

~~~text
0b00000070652d70617463682d76322400000031313131313131312d313131312d313131312d313131312d3131313131
313131313131312400000032323232323232322d323232322d323232322d323232322d3232323232323232323232320a
000000676f6c64656e2d6b657906000000676f6c64656e0c0000006f776e65722e676f6c64656e010000003140000000
656565656565656565656565656565656565656565656565656565656565656565656565656565656565656565656565
656565656565656565656565656565650700000000000000000000000000000040000000633335613163386339343338
356331376130663031346666613932306262346362666430353037633930386138366439666534626466326435383630
33393839950000000e00000070652d736e617073686f742d76320d000000736368656d612e676f6c64656e0100000032
400000006464636534393437383364623730316264353862373430613633323462383334643836316530333232613730
62613634323866633965353738633933306663380100000005000000726174696f05000000526174696f03000000302e
35080000004578706c696369740100000000000000400000003863346563393037356435653562633566363330656139
3862383738396130386138373335316332616137363736643630623766656133356665333465336666960000000e0000
0070652d736e617073686f742d76320d000000736368656d612e676f6c64656e01000000324000000064646365343934
373833646237303162643538623734306136333234623833346438363165303332326137306261363432386663396535
3738633933306663380100000005000000726174696f05000000526174696f04000000302e3732080000004578706c69
6369740100000005000000726174696f0105000000526174696f03000000302e35080000004578706c69636974010500
0000526174696f04000000302e3732080000004578706c69636974040000004e6f6e6501000000000000004000000038
633465633930373564356535626335663633306561393862383738396130386138373335316332616137363736643630
6237666561333566653334653366660d000000736368656d612e676f6c64656e01000000324000000064646365343934
373833646237303162643538623734306136333234623833346438363165303332326137306261363432386663396535
3738633933306663380400000046756c6c0100000000
~~~

还必须核：BeforeSnapshot 改 Generation=9 规范字节仍相同，但内嵌 Snapshot/完整 Patch 不同；0.7200 与0.72为同规范值；Changes 前像被换、Owner/Revision/Scope/IdempotencyKey 任一变更均改变 Patch hash。另用 §12 十字段 fixture 作 Missing/Null/空 Text/ResetDefault 三语载荷、Unknown 类型/孤立 surrogate/有环 AST 拒绝反例；非法输入不应有“合法 Golden”。本节不增加产品 API、不依赖一次性脚本作为实施权威。

## 4. 会话、编辑、Patch和公共入口

### 4.1 同一核心 API

~~~csharp
public enum SessionState { Ready, Closing, DrainUnknown, Closed, Faulted }
public enum EditOrigin { User, Import, Migration, Recommendation, Undo, Redo }
public enum EditStatus { Unchanged, Applied, Partial }
public enum BatchMode { Atomic, IndependentPartial }
public enum EditAction { Set, Remove, ResetDefault }
public sealed record ParameterEdit(
    ParameterKey Key, EditAction Action, ParameterValue? Value);
public sealed record EditBatch(
    long ExpectedGeneration, IReadOnlyList<ParameterEdit> Edits,
    BatchMode Mode, EditOrigin Origin);
public sealed record EditResult(
    EditStatus Status, long Generation,
    IReadOnlyList<ParameterKey> AppliedKeys, IReadOnlyList<ValidationIssue> Issues);
public sealed record EditAssessment(
    long ExpectedGeneration, ParameterSnapshot Proposed, ParameterDiff Diff,
    IReadOnlyList<ParameterKey> ApplicableKeys, IReadOnlyList<ValidationIssue> Issues);
public sealed record ParameterChange(
    ParameterKey Key, ParameterEntry? Before, ParameterEntry? After, UnitCode Unit);
public sealed record ParameterDiff(
    string BeforeSha256, string AfterSha256, IReadOnlyList<ParameterChange> Changes);
public sealed record EditorView(
    ParameterSchema Schema, ParameterBaseline Baseline, ParameterSnapshot Draft,
    bool IsDirty, int UndoCount, int RedoCount,
    IReadOnlyList<ParameterFieldState> Fields);

public sealed record PatchOptions(
    long ExpectedGeneration, OperationId OperationId, string IdempotencyKey,
    string Scope);
public sealed record PatchIntent(
    SessionId SessionId, OperationId OperationId, string IdempotencyKey, string Scope,
    ParameterBaseline Before, ParameterSnapshot Proposed,
    IReadOnlyList<ParameterChange> Changes, ValidationReport Validation,
    string RequestSha256);
public sealed record ParameterMergeConflict(
    ParameterKey Key, ParameterEntry? Base, ParameterEntry? Local, ParameterEntry? Current);
public sealed record RebasePlan(
    long ExpectedGeneration, ParameterBaseline Before, ParameterBaseline Current,
    ParameterSnapshot Local, IReadOnlyList<ParameterMergeConflict> Conflicts);
public enum MergeChoice { KeepLocal, TakeCurrent }
public sealed record RebaseResolution(ParameterKey Key, MergeChoice Choice);

public interface IParameterEditorSession : IAsyncDisposable {
    SessionId Id { get; }
    SessionState State { get; }
    PeResult<EditorView> Read();
    PeResult<ValidationReport> Validate(ValidationMode mode = ValidationMode.Full);
    PeResult<ParameterDiff> Diff();
    PeResult<EditAssessment> CheckEdits(EditBatch batch);
    PeResult<EditResult> SetValues(EditBatch batch);
    PeResult<EditResult> SetValue(ParameterKey key, ParameterValue value,
                                long expectedGeneration, EditOrigin origin);
    PeResult<EditResult> Undo(long expectedGeneration);
    PeResult<EditResult> Redo(long expectedGeneration);
    PeResult<EditResult> DiscardChanges(long expectedGeneration);
    PeResult<PatchIntent> CreatePatch(PatchOptions options);
    PeResult<RebasePlan> PlanRebase(ParameterBaseline current, long expectedGeneration);
    PeResult<EditResult> Rebase(RebasePlan plan, IReadOnlyList<RebaseResolution> resolutions);
    PeResult<EditResult> AdoptAppliedBaseline(ApplyReceipt receipt, long expectedGeneration);
    ValueTask<PeResult<OperationView>> PreviewAsync(PreviewRequest request,
                                      CancellationToken cancellationToken = default);
    ValueTask<PeResult<OperationView>> RecommendAsync(RecommendationRequest request,
                                      CancellationToken cancellationToken = default);
    PeResult<EditResult> AcceptSuggestion(OperationId operationId, string candidateId,
                                          long expectedGeneration);
    ValueTask<PeResult<OperationView>> RequestApplyAsync(ApplyIntentRequest request,
                                      CancellationToken cancellationToken = default);
    ValueTask<PeResult<ApplyReceipt>> ResolveApplyAsync(PatchIntent original,
                      TimeSpan timeout, CancellationToken cancellationToken = default);
    PeResult<EditorCheckpoint> ExportCheckpoint();
    PeResult<OperationView> GetOperation(OperationId operationId);
    PeResult<bool> Cancel(OperationId operationId);
    IDisposable Subscribe(IParameterEditorObserver observer);
    ValueTask<DrainReceipt> DrainAsync(TimeSpan timeout,
                                      CancellationToken cancellationToken = default);
    ValueTask<DrainReceipt> CloseAsync(TimeSpan timeout,
                                      CancellationToken cancellationToken = default);
}
~~~

Read 是冻结投影，不暴露裸Draft属性绕过View。同步方法只做有界内存操作，不等待设备；大Schema调用者放后台并显示Busy。CheckEdits为无修改演练，返回候选、diff、适用key和问题，不生成Undo/事件；候选Generation为预计下一代（无变化仍当前代），提交仍使用Assessment.ExpectedGeneration且再次校验，不能把预计代次当当前代。SetValue等价单项Atomic SetValues。所有修改带ExpectedGeneration；并发命令只有匹配者接纳，另一项 `PE-2001`。同值/同Origin修改为Unchanged，不消费代次/Undo；Undo/Redo会递增代次，不回到历史代次。Discard只退回本session baseline的值，一条可撤销修改，不回滚外部事实。

Discard 的目标也执行 Full/当前 Edit 权/可编辑条件；若基线仍有初始 MissingRequired/关联错误则拒绝，可关闭会话保原件，不能用 Discard 绕过完整候选有效性。Undo/Redo 对原本非法的历史前像同样拒绝，仍保留历史与错误，不自动修正。

CheckEdits 的“可演练失败”与 PeResult 调用失败必须分开：预算/结构/未知key/重复key/代次/权限/生命周期拒绝返回失败Value=null；可以有界构造的Atomic候选若范围/格点/Required/关联不合法，返回成功EditAssessment（Proposed保完整候选、Diff为前像差、ApplicableKeys=[]、Issues带Errors），表示演练完成而非可提交。IndependentPartial仅独立字段演练，通过key组成Proposed/ApplicableKeys、失败项留Issues；全拒也可演练成功但ApplicableKeys为空，SetValues必须返回失败不修改。ApplicableKeys只列真正改变的可采用key，无变化返回空、Proposed.Generation=当前；检查结果不缓存授权。SetValues重新验证同原ExpectedGeneration，任何Atomic Error即失败，不把Assessment.Succeeded当提交资格。

### 4.2 四态 Patch、基线与冲突

Set的Value非C#null（显式Null须ParameterValue.Null）；Remove/ResetDefault的Value必须C#null。每批key唯一，空批 `PE-1013`；Remove拒Required，Reset无默认 `PE-1014`。Patch Changes的Before/After null表示Missing；After.Origin=Default表示恢复默认；不出现的Key是未改。scope/幂等键为非空有界宿主语义，不能增加权限；含完整Before Owner/Revision/hash、Proposed代次/Schema/hash、四态变化和Full Validation。空diff不创建“0项成功”Patch。Core重算请求hash，不信任调用者伪改Validation。

外部Applied回执不自动覆盖草稿：AdoptAppliedBaseline仅接受同session已验证的原操作Applied回执、Before与Patch完全一致、After含Proposed精确内容、当前仍同代次且无未决操作；成功更新baseline并清Undo/Redo（历史基线已变），草稿代次+1，显示无需再保存；旧/Partial/Unknown回执不得采用。检测或读回结果仍由Owner解释，不把Applied当设备当前值或质量事实。

PlanRebase只允许同Owner身份、同Schema/hash/canonical、较新Revision；同Revision异内容拒绝。逐key三方比较含Origin/Missing/Null：Local=Base取Current，Current=Base取Local，Local=Current取该值，否则列冲突。Rebase须完整且仅一次给出所有冲突的KeepLocal/TakeCurrent，不混合字段碎片；重新核原generation、Before和Current，Full校验合并结果，原子替换baseline/草稿、generation+1并清历史。失败不改任何状态。来源真实性由宿主核验，hash不能授予rebase权；定义变更只能走§10迁移。Pending/Unknown Apply时禁止Rebase/Adopt/Discard和再写；先Resolve原操作，不能换latest掩盖未知。

RebasePlan为公开数据，不能信任调用者修改的Local/Conflicts：Rebase先核Plan.Before等当前session基线、Plan.Local等当前草稿（含generation/content/Schema）、Current完整来源/hash/Revision，内部重新按上段逐key生成唯一冲突集合，与Plan.Conflicts完整逐值相等才接纳Resolutions。选择需key唯一且恰覆盖冲突，无多余/遗漏；错plan PE-2001、非法选择PE-1016。无冲突较新基线也可Rebase，仍generation+1/清历史；同Revision且同内容没有新基线，返回PE-2001，不造一次成功更版。Adopt也内部核原operation回执/端口身份，外部不能构造同形DTO制造Applied资格。旧revision来源的真实新Profile/配方保存仍由领域Owner签发，PE不制造该事实。

## 5. 校验、关联、批改和撤销

固定顺序：Schema/预算 → token及规范单位 → Required/Nullable/类型/边界/格点/枚举/Text → 显隐和编辑条件 → 当前Edit权限/只读 → 完整候选的关联约束 → 历史预算及ExpectedGeneration → 一次提交。错误按Key、RuleId、Code稳定排序；问题带定位、严重性、资源键、恢复键，不包含敏感原值。Full报告绑定generation/hash/Schema；建议、Preview、CreatePatch、Apply重新Full校验，不仅看曾有IsValid。

Validate(ChangedOnly)无隐式“上次按钮选择”：变更集合固定为当前Draft与本session Baseline按值+Origin/Missing计算的Diff.Keys。遍历该集合的显隐可编辑反向影响闭包，再检查与闭包相交的所有关联约束和相关字段；检查报告Mode=ChangedOnly，即使无Issues也只表示该集合未发现错误。空集合返回局部空报告，不清初始Full错误；不可替代Full。Full.IsValid为无Error（Warning不使false），关联When/Assertion的Unknown按§3.3总是Error；字段Visible/Editable=Unknown投影需明确原因，未改不可编辑字段保值，实际修改仅在Editable=True且有当前Edit权时允许。Required/类型/单位默认校验不因隐藏关闭。

Atomic先在冻结前像构造完整候选；允许同时修正两个关联字段（如low/high），不把每字段中间态当最终错误。任一校验/权限/预算/代次失败，草稿、代次、Undo/Redo均不变。成功只递增一次generation、生成一个完整before/after撤销记录，清Redo；一次Undo/Redo恢复整批。UI预览集合必须等实际集合，筛选/折叠不改变已选key，无读权不显示前像。

IndependentPartial只对既不参与显隐依赖、也不参与任一关联约束的独立字段允许；否则 `PE-1012` 要求Atomic。独立项按key排序验证，通过集合仍对完整候选Full校验，成功一次形成草稿和一条Undo，返回Partial及逐项拒绝；全部采用为Applied，全拒返回失败，无成功集合不得称Partial。此规则防“挑合法子集”产生关联破坏。初始snapshot固有Required/关联问题可在Read中显示；修改后完整候选必须有效，不能留未修缺值自动补默认。

撤销/重做仍核当前Schema、预算、来源及Edit权限/可编辑条件（对完整目标快照），新只读或权限撤回不绕过；历史仍保留，可恢复授权后再执行。显示文本/排序/折叠/语言、CheckEdits、验证、试算、读取详情不生成Undo；推荐明确采用才走Atomic Edit。差异比较规范值+Origin，不因显示舍入相同隐藏实际变化。

## 6. 异步操作、事件、期限与排空

### 6.1 正交操作契约

~~~csharp
public enum OperationKind { Preview, Recommendation, Apply }
public enum OperationPhase {
    Accepted, Queued, Running, CancelRequested, Draining, DrainUnknown, ResourcesReleased
}
public enum OperationOutcome { Completed, Rejected, Cancelled, TimedOut, Failed, Unknown }
public enum StopReason { None, UserCancel, Deadline, AccessRevoked, AdapterFault }
public sealed record OperationContext(
    SessionId SessionId, OperationId OperationId, long RequestEpoch,
    long DraftGeneration, string SnapshotSha256, string RequestSha256,
    DateTimeOffset EffectiveDeadlineUtc);
public sealed record OperationProgress(OperationId OperationId, decimal? Fraction,
                                       string MessageResourceKey);
public sealed record OperationView(
    OperationContext Context, OperationKind Kind, long RecordVersion,
    OperationPhase Phase, StopReason StopReason, OperationOutcome? Outcome,
    bool HistoryOnly, bool QueryInFlight,
    PreviewResult? Preview, RecommendationResult? Recommendation,
    ApplyReceipt? Apply, IReadOnlyList<EditorError> Errors);
public enum DrainState { Released, Unknown }
public sealed record AdapterDrainReceipt(
    OperationId OperationId, bool ExecutionStopped, bool ResourcesReleased,
    IReadOnlyList<EditorError> Errors);
public sealed record DrainReceipt(
    DrainState State, IReadOnlyList<OperationId> UnreleasedOperations,
    IReadOnlyList<OperationId> UnresolvedApplies, IReadOnlyList<EditorError> Errors);
public enum EditorEventKind {
    SessionOpened, DraftChanged, ValidationCompleted, OperationAccepted,
    OperationQueued, OperationStarted, StopRequested, Draining, DrainUnknown,
    ResourcesReleased, OperationCompleted, ApplyResolved, SessionClosed, SubscriptionFaulted
}
public sealed record ParameterEditorEvent(
    SessionId SessionId, long Sequence, long DraftGeneration, DateTimeOffset AtUtc,
    EditorEventKind Kind, OperationId? OperationId, long? OperationRecordVersion,
    string? ErrorCode);
public interface IParameterEditorObserver {
    void OnEvent(ParameterEditorEvent notification);
}
~~~

OperationId为非空Guid，由宿主产生，不是“递增ID”；RequestEpoch是Core分配的非负单调long。SameId+相同请求hash返回原记录，不再次调端口；SameId异正文 `PE-2005`。不同Id复用Apply幂等键也必须对比完全原请求，不能构造第二次写入。一个操作的结果字段只允许其Kind对应的一项；Outcome仅ResourcesReleased后非null，DrainUnknown不预告已取消/已失败；无接纳记录的校验/预算拒绝用PeResult失败，不假造执行终态。

重复查找先于新请求代次/队列/Full接纳校验，但仍核当前View/相应行动权再披露原记录：同OperationId请求的结构及预算可预检，用原记录冻结的Schema/Snapshot而非当前Draft重算请求hash，含全部原request字段，完全一致才返回原RecordVersion；草稿后来改变不会把原调用误判一次新派发。相同ID异正文始终PE-2005，不据新schema忽略差异。不同ID同Apply幂等键拒PE-2005（新ID已使Patch正文不同），要求使用原Patch/原OperationId查询，不分配新epoch/排队。成功Query只更新原外部回执，不重新调算法或发布第二终态。

Preview/Recommend/ApplyAsync在接纳时登记operation并冻结输入，锁外执行；调用等待受同一总deadline，队列耗时计入。截止/取消先通知停止，保留实际Task和Adapter关联并开始Drain；如果尚未释放，可返回成功的OperationView但Phase=Draining/DrainUnknown、Outcome=null。这里成功只表示记录可读，不能当业务完成。GetOperation读取最新RecordVersion；操作排空后唯一发布Outcome。恢复排空重复查询不再执行算法。

Core在接纳及实际派发前核完整Schema/draft/current access，EffectiveDeadlineUtc取请求Timeout、OperationPolicy.OperationTimeout、当前授权ValidUntil的最早值；请求Timeout有限正值且不超过策略。超时不能续原请求，查询原Apply使用新的当前Query授权和查询期限，不改原操作期限。无Data/Input/Profile时拒接，不按默认样本或latest填充。

只要草稿generation/hash、输入引用、Profile或当前来源不再对应，结果标HistoryOnly；新操作或编辑不默认取消旧操作，但旧结果永不覆盖新代。纯语言/显示单位/排序不改变hash、不产生新epoch。当前读权撤回时不发布载荷；对非相同hash也相同generation的伪结果拒绝。UI选槽只投影指定操作，不能由“最后完成者”抢当前显示。

Outcome映射固定：正常Preview（含有效拒识/多候选事实）及Recommendation/Abstained为Completed；端口执行错误为Failed；预派发拒绝为Rejected。已登记停止理由的Preview/Recommendation即使晚返有效结果，也只历史化，按原Cancel/Deadline在释放后为Cancelled/TimedOut，撤权为Rejected。Apply按已验证回执State映射：Applied/Pending/Partial为Completed（仅本地调用完成），Rejected为Rejected，Unknown为Unknown；停止/断连后无回执为Unknown。取消后若Owner返回精确Applied事实，必须保留Applied并按Completed呈现，不能谎报已撤销。停止原因与远端事实分列。

### 6.2 事件顺序和订阅

~~~text
OperationAccepted → OperationQueued（如排队） → OperationStarted
→ StopRequested（可选） → Draining → DrainUnknown（如未确认）
→ ResourcesReleased → OperationCompleted（唯一Outcome）
ApplyResolved只更新原外部回执；不重复OperationCompleted
SessionClosed为最后关闭屏障通知；其回调也退出后才置Closed/返回Released
~~~

验证为同步动作，只发ValidationCompleted，不把session强改Validating；UI的Busy属于投影。Sequence严格单调且无回绕；事件不带参数值/结果载荷，读取另核权限。Subscribe返回幂等IDisposable，退订不取消业务、不关闭session。Core不持锁调用观察者；独立有界通知队列按Sequence交付，progress只作为可合并投影。观察者抛错 `PE-9002`，隔离该订阅并保留权威操作；队列满则停该订阅并报告诊断，调用者Read/GetOperation补同步，不能无界缓冲或因显示拥塞回滚正式操作。

Observer必须短、非阻塞，不允许同步回入修改。无法强行终止已执行的用户回调：关闭超时仍保留回调Task/Owner、DrainUnknown，不能宣称已退订即已排空。后台线程不是Observer不阻塞的证明；通知/业务Task分别计账。

每订阅一个串行 worker；注册时先预留 MaxNotificationDepth 的有界槽及计入 MaxHistoryBytes 的记录空间，已满拒订阅（Subscribe 抛含 PE-4003 的 InvalidOperationException，不创建订阅）。单次 OnEvent 在当前有限 OperationPolicy.OperationTimeout 观察窗口内结束才确认该项交付；到期停止接纳该订阅的新通知、解除后续派发，保留原 worker/Observer/事件强引用，报告 PE-9002。到期不再开另一个 worker 补送。迟到退出后归还该执行槽；退订幂等且只停止新交付。Subscribe 是唯一返回 IDisposable 的同步例外；业务失败仍按 PeResult。Root/Close 必须观察真实 worker 完成，不能用队列已空作 ACK。

### 6.3 Session生命周期与取消

SessionState仅Ready/Closing/DrainUnknown/Closed/Faulted；Dirty、Validating、Previewing、Applying是投影或operation状态，不能写入另一个不一致enum。Ready允许无编辑直接Full Validate和显式Preview；只读不等于免校验。Apply未决时冻结修改和第二Apply；Preview/Recommend运行时允许后继编辑使原结果HistoryOnly。

Cancel对于Queued直接移除并确认未调端口，随后Released/Cancelled；对于Running仅请求CTS停止，按Adapter实际结束及排空确定终态。调用者token取消同此规则。Apply一旦交给Owner，取消/断连不能证明远端没写；无完整回执为Apply.Unknown，只有Owner明确无副作用拒绝才能Rejected，不能伪报已撤销。Cancel对未知Id返回PE-2006，已释放操作返回false，不取消已产生的远端事实。

DrainAsync不发起新业务，等待本session接纳的推荐/预览/Apply、当前Query、通知及Adapter借用排空；失败/超时返回Unknown、列未释放operation并置DrainUnknown，仍允许GetOperation/Drain/Close和有权原Apply查询，禁止新编辑/执行。成功后非Closing会话恢复Ready，但外部Pending/Unknown写门仍保持。

CloseAsync先转Closing、拒绝新写/执行，发取消，排空业务/查询/借用及已有通知；仍在订阅者的 SessionClosed 是最后关闭屏障通知（不授权回入/发新业务），其回调退出后退订、释放Core可释放状态、转Closed。已退订者不补发该通知。调用者取消仅取消本次等待，不把关闭进行中的任务遗弃；可以对同一session再次Close/Drain。DisposeAsync使用显式CloseTimeout调用Close，未排空抛含PE-4002的异常且保留引用供宿主重试，不在finally清空Owner。Closed只保留有界operation元数据墓碑，禁止重新编辑/派发；不证明远端Unknown已解决。DrainReceipt列UnresolvedApplies，宿主保留原持久请求并使用Apply Port做冷恢复；查询能力和原请求不能依赖已销毁UI。

## 7. 失败、投影与恢复

| UI投影 | 条件 | 安全主动作 |
|---|---|---|
| Ready | 无错误、无活动操作；可有未验证的初始草稿 | 验证 |
| Busy | 排队/执行/查询/Closing/排空 | 查看进度；允许时取消 |
| Empty | 空Schema或无编辑字段 | 查看来源/关闭 |
| Stale | generation/hash/输入/来源已变 | 验证后显式试算 |
| Blocked | 定义/能力/依赖/预算不齐；Unknown写门 | 查看缺口或查询原操作 |
| RecoverableError | 原草稿保留的可修正错误 | 定位字段/修正/排空 |
| PermissionDenied | 当前权限拒绝 | 请求权限/退出 |
| Completed | 本地操作Released且有Outcome/原外部回执 | 查看结果；不显示已放行 |

错误码为本模块稳定v0.2键，平台error-codes映射另采纳。不得用原始异常/中文文案/布尔成功代替：

| 键 | 拒绝或失败事实 | 保留与恢复 |
|---|---|---|
| PE-1001 | InvalidSchema：key/类型/结构/hash非法 | 原输入由宿主保留；修定义后新建 |
| PE-1002 / 1003 | UnknownParameter / TypeMismatch | 拒该编辑，不转字符串/0 |
| PE-1004 | DependencyCycle | 定位引用链，不自动断边 |
| PE-1005 / 1006 | OutOfRange / StepViolation | 保留UI token；显式修改，不钳位 |
| PE-1007 / 1008 / 1009 | UnsupportedUnit / ReadOnly / MissingRequired | 不补值、不越权；修来源 |
| PE-1010 / 1011 | InvalidText或RegexTimeout / SchemaVersionMismatch | 原件不改；不降级解析 |
| PE-1012 / 1013 / 1014 | CoupledPartial / EmptySelection / NoDefault | 改Atomic、选择字段、取消恢复默认 |
| PE-1015 / 1016 | VersionExhausted / ConstraintFailed | 不回绕/放宽；定位关联问题 |
| PE-2001 / 2002 | Generation或BaselineConflict / PermissionDenied | 保草稿；三方差异或重授权 |
| PE-2003 / 2004 | ApplyRejected / ApplyUnknown | 原请求查询；不换key重发 |
| PE-2005 / 2006 | IdempotencyConflict / OperationNotFound | 保原请求；不把NotFound当允许重写 |
| PE-2007 / 2008 | SessionClosed / ApplyUnresolved | 不重建掩盖；先查原请求 |
| PE-3001 / 3002 | PreviewUnavailable / PreviewInputInvalid | 缺端口仅禁该功能；修输入 |
| PE-3003 / 3004 / 3005 | Deadline / CancelRequested / HistoryOnly | 排空确认前无终态；迟到只历史 |
| PE-3101 / 3102 | RecommendationUnavailable / SuggestionStale | 不猜参数；重新请求或保原值 |
| PE-4001 / 4002 / 4003 | QueueFull / DrainUnknown / ResourceLimit | 背压/排空/显式批准Profile，不截断 |
| PE-9001 / 9002 / 9003 | AdapterFailure / ObserverFailure / InternalInvariant | 分离显示/端口故障，保实际Owner |
| PE-9004 | ReceiptInvalid（错ID/hash/字段/预算/枚举） | 不接收结果/基线；保原操作供查询 |

所有调用路径含成功、拒绝、取消、deadline、释放失败和Unknown；退订、视图卸载、Close不能转写外部状态。原Apply的Pending/Unknown优先阻断写门，不能让RecoverableError中的“重试”按钮默认再次Apply。

### 7.1 模块内置三语错误与恢复资源

Core不返回本地化文字，稳定模块错误的MessageResourceKey固定为`pe.error.<Code>`（如pe.error.PE-1005）、RecoveryResourceKey用下表pe.recovery.*。宿主定义/约束/Provider原因仍由其IEditorTextResources解析；WPF先解析本模块内置zh-CN/zh-TW/en-US资源，再调用宿主资源，不让测试Host短回退覆盖内置错误。Key/RuleId定位配在文字外，不拼参数原值/堆栈。界面可以显示稳定Code作诊断，不能把资源键当主提示。每个listed Code必须有下述三语；同一RecoveryKey不另造同义字符串。

| Code | zh-CN | zh-TW | en-US | RecoveryKey后缀 |
|---|---|---|---|---|
| PE-1001 | 参数定义无效。 | 參數定義無效。 | Parameter definition is invalid. | source |
| PE-1002 | 参数不存在。 | 參數不存在。 | Parameter was not found. | source |
| PE-1003 | 值的类型或精度不符。 | 值的類型或精度不符。 | Value type or precision does not match. | edit |
| PE-1004 | 参数依赖成环。 | 參數相依形成循環。 | Parameter dependencies form a cycle. | source |
| PE-1005 | 值超出范围。 | 值超出範圍。 | Value is outside the range. | edit |
| PE-1006 | 值不符合步长。 | 值不符合步長。 | Value does not match the step. | edit |
| PE-1007 | 不支持该单位。 | 不支援此單位。 | This unit is unsupported. | source |
| PE-1008 | 参数只读。 | 參數唯讀。 | Parameter is read-only. | access |
| PE-1009 | 必填参数缺值。 | 必填參數缺值。 | A required value is missing. | edit |
| PE-1010 | 文本或格式无效。 | 文字或格式無效。 | Text or format is invalid. | edit |
| PE-1011 | 参数版本不匹配。 | 參數版本不符。 | Parameter version does not match. | source |
| PE-1012 | 关联参数须一起修改。 | 關聯參數須一起修改。 | Edit related parameters together. | atomic |
| PE-1013 | 没有可执行的更改。 | 沒有可執行的變更。 | No changes are available. | select |
| PE-1014 | 没有默认值。 | 沒有預設值。 | No default value is defined. | edit |
| PE-1015 | 版本计数已用尽。 | 版本計數已用盡。 | Version counter is exhausted. | source |
| PE-1016 | 参数条件未满足。 | 參數條件未滿足。 | Parameter constraints are not met. | edit |
| PE-2001 | 草稿或基线已改变。 | 草稿或基準已變更。 | Draft or baseline has changed. | read |
| PE-2002 | 当前权限不足。 | 目前權限不足。 | Current access is denied. | access |
| PE-2003 | 应用被拒绝。 | 套用遭拒絕。 | Apply was rejected. | receipt |
| PE-2004 | 应用结果未确认。 | 套用結果未確認。 | Apply result is unconfirmed. | query |
| PE-2005 | 操作身份冲突。 | 作業識別衝突。 | Operation identity conflicts. | query |
| PE-2006 | 找不到原操作。 | 找不到原作業。 | Original operation was not found. | query |
| PE-2007 | 编辑会话已关闭。 | 編輯工作階段已關閉。 | Editor session is closed. | source |
| PE-2008 | 原应用尚未解决。 | 原套用尚未解決。 | Original apply is unresolved. | query |
| PE-3001 | 试算未连接。 | 試算未連接。 | Preview is not connected. | connect |
| PE-3002 | 试算输入无效。 | 試算輸入無效。 | Preview input is invalid. | source |
| PE-3003 | 操作已到截止时间。 | 作業已達截止時間。 | Operation deadline was reached. | drain |
| PE-3004 | 已请求取消。 | 已要求取消。 | Cancellation was requested. | drain |
| PE-3005 | 结果仅供历史查看。 | 結果僅供歷史檢視。 | Result is for history only. | refresh |
| PE-3101 | 建议未连接。 | 建議未連接。 | Suggestion provider is not connected. | connect |
| PE-3102 | 建议已过期。 | 建議已過期。 | Suggestion is stale. | refresh |
| PE-4001 | 等待队列已满。 | 等候佇列已滿。 | Waiting queue is full. | drain |
| PE-4002 | 资源归还未确认。 | 資源歸還未確認。 | Resource release is unconfirmed. | drain |
| PE-4003 | 资源预算不足。 | 資源預算不足。 | Resource budget is insufficient. | budget |
| PE-9001 | 外部端口调用失败。 | 外部端口呼叫失敗。 | External port call failed. | drain |
| PE-9002 | 通知回调失败或阻塞。 | 通知回呼失敗或阻塞。 | Notification callback failed or stalled. | drain |
| PE-9003 | 编辑器内部状态错误。 | 編輯器內部狀態錯誤。 | Editor internal state is invalid. | support |
| PE-9004 | 回执不匹配或无效。 | 回執不符或無效。 | Receipt does not match or is invalid. | query |

| pe.recovery后缀 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| source | 核对来源与定义后重开。 | 核對來源與定義後重開。 | Check the source and definition, then reopen. |
| edit | 按范围和条件修改值。 | 依範圍與條件修改值。 | Edit the value to meet its range and constraints. |
| access | 核对权限与只读条件。 | 核對權限與唯讀條件。 | Check access and read-only conditions. |
| atomic | 选择关联字段，原子批改。 | 選取關聯欄位，整批修改。 | Select related fields and apply an atomic batch. |
| select | 选择更改或查看历史。 | 選取變更或檢視歷史。 | Select changes or inspect history. |
| read | 重新读取并核对差异。 | 重新讀取並核對差異。 | Read again and review the differences. |
| receipt | 查看原回执与拒绝原因。 | 檢視原回執與拒絕原因。 | Inspect the original receipt and rejection reason. |
| query | 查询原请求，勿重复应用。 | 查詢原要求，勿重複套用。 | Query the original request; do not apply again. |
| connect | 由宿主连接对应端口。 | 由宿主連接對應端口。 | Connect the corresponding port in the host. |
| drain | 等待原操作结束并归还资源。 | 等待原作業結束並歸還資源。 | Wait for the original operation and resource release. |
| refresh | 核对来源后重新请求。 | 核對來源後重新要求。 | Check the source, then request a new result. |
| budget | 归还资源或采用已批准预算。 | 歸還資源或採用已核准預算。 | Release resources or use an approved budget. |
| support | 停止新操作，保留会话和诊断。 | 停止新作業，保留工作階段與診斷。 | Stop new work and retain the session and diagnostics. |

§7八态与§11命令/单位标签用同局部资源体系：Busy“处理中／處理中／Working”、Empty“无参数／無參數／No parameters”、Stale“结果已过期／結果已過期／Result is stale”、Blocked“无法继续／無法繼續／Cannot continue”、PermissionDenied“权限不足／權限不足／Access denied”、RecoverableError“需要修正／需要修正／Needs correction”、Ready“可编辑／可編輯／Ready to edit”（当前无Edit权用“只读／唯讀／Read-only”）、Completed“操作已结束／作業已結束／Operation finished”；具体原因/安全主动作仍按§7，Completed不得改“已通过”。单位符号px、µs/ms/s、mm/µm、mm²/µm²、°、%、dB、计数均显式同§3映射，不从翻译标签推单位。显示来源、范围、关联定位和恢复说明的SuperTip同呈现revision更新。§14三语验证覆盖全部内置Code/RecoveryKey/状态/命令/单位；外部资源缺失显示已有短回退并诊断，不伪造领域解释。

## 8. 推荐、试算与应用的独立端口

### 8.1 Preview

~~~csharp
public sealed record PreviewRequest(
    OperationId OperationId, long ExpectedGeneration, ContentRef Profile,
    IReadOnlyDictionary<string, ContentRef> Inputs, TimeSpan Timeout);
public enum PreviewValidity {
    Unknown, Valid, Invalid, NotObservable, Ambiguous, Rejected, Unsupported
}
public sealed record PreviewItem(
    string ItemId, ParameterValue? Value, UnitCode Unit, PreviewValidity Validity,
    string ReasonResourceKey, ContentRef? Evidence);
public sealed record ResourceObservation(
    long ManagedBytes, long NativeBytes, int ActiveLeases);
public sealed record PreviewResult(
    OperationId OperationId, string RequestSha256, string SnapshotSha256,
    ContentRef Profile, string InputsSha256, ContentRef? ResultRef,
    IReadOnlyList<PreviewItem> Items, ContentRef Adapter,
    TimeSpan Elapsed, ResourceObservation? Resources,
    IReadOnlyList<EditorError> Errors);
public interface IParameterPreviewExecutor {
    ValueTask<PreviewResult> ExecuteAsync(
        PreviewRequest request, ParameterSnapshot snapshot, OperationContext context,
        IProgress<OperationProgress> progress, CancellationToken cancellationToken);
    ValueTask<AdapterDrainReceipt> DrainAsync(
        OperationId operationId, CancellationToken cancellationToken);
}
~~~

Core冻结自己的Snapshot交给Adapter，不允许调用者把另一snapshot塞入请求。Inputs非空、key唯一有界；InputsSha256是同TLV域 `pe-inputs-v2` +按key排序三元组引用的hash。Profile与Adapter为精确版本/hash，不接受latest。所有返回引用/ID/hash/枚举、深冻结和字节预算先验，Value种类与Unit配对按§3.2；Valid须有Value或明确Evidence，非Valid数值不冒充有效零；Partial逐项保留，不由Core重新判NG/OK。

无Adapter `PE-3001`，不使编辑器整体不可用。Adapter响应前失败或响应未知仍必须按operation Drain；资源观察null=未测量，不拒绝本来有效的无观测结果。预算不是测量；Resources本身不是释放回执。任何ResultRef仅原证据位置，不赋读权。

Preview Adapter 在开始取图/模型前登记原 OperationId 的 lease owner 和实际 Execute Task；原图/模型父租约、子视图和 native 输出各有独立引用及清理动作。单次 Drain 的观察期限取 Core 此次传入 token（Core 用独立 cleanup CTS，有限 CloseTimeout，不复用已取消业务 token）；到期返回 ResourcesReleased=false 或结束本次等待，保留尚未结束的原清理 Task，不重复启动释放。下一次 Drain 观察同一 Task，失败已结束的清理动作才可按 Owner 的幂等边界重试；一个失败不阻止其它独立子资源释放。父租约只有全部子 ACK 后归还。ResultRef 所指持久证据归证据 Owner，不等同活动 lease。未知资源的字节不能写0；若 Adapter 无法满足请求预算/释放契约须在实际借用前拒绝。

### 8.2 Recommendation

~~~csharp
public sealed record RecommendationRequest(
    OperationId OperationId, long ExpectedGeneration, ContentRef Profile,
    IReadOnlyDictionary<string, ContentRef> Evidence,
    int MaximumCandidates, TimeSpan Timeout);
public enum RecommendationState { Candidates, Abstained }
public sealed record ParameterSuggestion(
    string CandidateId, IReadOnlyList<ParameterEdit> Edits,
    string ReasonResourceKey, decimal? Confidence, ContentRef Evidence);
public sealed record RecommendationResult(
    OperationId OperationId, string RequestSha256, string SnapshotSha256,
    ContentRef Profile, RecommendationState State,
    IReadOnlyList<ParameterSuggestion> Candidates, ContentRef Provider,
    string ReasonResourceKey);
public interface IParameterRecommendationProvider {
    ValueTask<RecommendationResult> RecommendAsync(
        RecommendationRequest request, ParameterSchema schema,
        ParameterSnapshot snapshot, OperationContext context,
        IProgress<OperationProgress> progress, CancellationToken cancellationToken);
    ValueTask<AdapterDrainReceipt> DrainAsync(
        OperationId operationId, CancellationToken cancellationToken);
}
~~~

推荐输入Profile/证据/Schema/草稿/预算固定，同一Provider版本应声明可复现方法及seed（需要时作为Profile固定字段）；Core不搜索阈值、训练模型或计算概率。MaximumCandidates须1..MaxSuggestions，证据非空；没有真实来源/弱信号/退化/遮挡/多解无可确认策略时Provider返回Abstained、Candidates空、原因非空，保原值，不借缺Confidence生成0。Candidates状态必须非空、CandidateId唯一；Confidence若提供为[0,1]且其语义由ProviderProfile明确，无定义则null；不由匹配score推概率。

每候选Edits使用与CheckEdits Atomic相同的纯候选构造/完整校验算法，但前像必须是原operation冻结的Schema/Snapshot，不直接调用当前session的公开CheckEdits去验证迟到候选。含只读/超限/耦合错误即该推荐响应非法，不裁掉失败候选制造全合法集合；Edits不得为空、MaximumCandidates也限制实际响应数。结果只进入原operation。AcceptSuggestion只能选择当前同generation/hash/来源的原operation已释放成功候选，重新核Edit权限、完整前像和所有约束，再一次Atomic修改/Undo；不自动Preview/Apply。多候选必须明确选ID，不取第一/最高confidence。来源失效或编辑后 `PE-3102`，重新建议不重绑旧候选。

权限与“来源仍当前”的具体接线复用§2的IParameterAccessPolicy，不另造隐藏current-source API：宿主策略绑定本session精确Schema/输入/Profile/provider来源上下文，已知来源替换或失效时取消此前AccessDecision.Invalidated并拒该旧session后继Recommend/Preview/采用/Apply。端口在派发/披露时独立核实际精确来源，禁止根据Id取latest。同session开始新请求，若Profile/Inputs/Evidence引用与某原请求不相等，Core把那项原结果标HistoryOnly；纯外部失效若宿主未通知，Core不能从hash自知真实世界已变，Host必须停止该工具或新建准确来源session。历史合法候选仍可按当前View权查看，但任何采纳重新核当前策略；不能把来源刷新缺口转给算法猜。Provider的确定性算法/seed/拒识阈值归其所属模块Profile与指导；本模块自动参数职责是请求/限额/关联/解释引用/显式采用，不承担通用优化器/训练/阈值搜索。

Provider 按 operation 保留实际 Task 与临时证据借用，Drain 遵循 §8.1 同一有限观察/失败重试规则。Core 在接纳时先为 MaxResultBytes 的响应空间计入 MaxHistoryBytes 预留，再调用 Provider；响应到达后做有限计数/冻结，释放多余预留，完整候选载荷一直计入历史直至 session 真关闭。取消/过期的迟到响应仍先限额核验：可保合法历史候选但不能采用；超限只保预算内错误元数据及原请求身份，不复制超大集合。拒识结果也占记录/字节预算，不能无界保留“空建议”。

### 8.3 视觉消费路线与HALCON适用性

Core无图像算子，不能从参数类型决定分割、匹配、读码路线。原v0.1中的Mean/Gauss与区域/形状/条码模板属于外部算法设计且夹带未冻结签名，现以真实模块公开结果替代；不删除视觉试算能力、不缩小整模块，只取消重复算法权威。Adapter通过其所属模块的唯一指导冻结算法、ROI粗精域、模型、拒识、备用和推荐；在这里绑定Profile/Inputs/ResultRef：

| 消费者 | 真实输入/输出 | 本模块拒错断言 |
|---|---|---|
| 分割参数工具 | segmentation Profile + 原图/ROI引用 → 原区域证据与有效性 | 弱信号/全掩膜不补0；阈值改变使原结果HistoryOnly |
| 定位参数工具 | alignment-2d/model-assets Profile + 样本/模型 → 全候选/姿态证据 | 遮挡/退化/多候选保持Ambiguous/NotObservable，不降低score |
| 读码参数工具 | barcode Profile + 原ROI/图 → 原始内容及候选证据 | NoRead/多码不自动修字符串；不能把建议应用为身份事实 |

HALCON 26.05本地资料的职责核对见§17.3：reduce_domain只改定义域、dyn_threshold/threshold受图像与阈值语义约束，find_shape_model的score/候选不是概率，find_bar_code的空读不证明PASS。它们均由 `ImageLibDotNet.cv2` 经各视觉模块调用；不再审查“封装是否包含算子”，不另接HOperatorSet/halcondotnet.dll，不扫描内部。只在真实C#重载/类型/封送有歧义时查公开签名；具体消费者编译/同样本正确性及P50/P95/P99/峰值资源是外部适配切片门，本模块没有“最快”结论或默认物理阈值。

### 8.4 Apply、查询和外部成功

~~~csharp
public enum ApplyState { Pending, Rejected, Applied, Partial, Unknown }
public sealed record ApplyItemReceipt(
    ParameterKey Key, ApplyState State, string? ErrorCode, ContentRef? Evidence);
public sealed record ApplyReceipt(
    OperationId OperationId, string RequestSha256, ApplyState State,
    ParameterBaseline Before, ParameterBaseline? After,
    IReadOnlyList<ApplyItemReceipt> Items, ContentRef? OwnerReceipt,
    string? ErrorCode);
public sealed record ApplyIntentRequest(PatchIntent Intent, TimeSpan Timeout);
public interface IParameterApplyPort {
    ValueTask<ApplyReceipt> ApplyAsync(
        ApplyIntentRequest request, OperationContext context,
        CancellationToken cancellationToken);
    ValueTask<ApplyReceipt> QueryAsync(
        PatchIntent original, OperationContext queryContext,
        CancellationToken cancellationToken);
    ValueTask<AdapterDrainReceipt> DrainAsync(
        OperationId operationId, CancellationToken cancellationToken);
}
~~~

RequestApply核同session、未决写门、原Patch前像/generation/hash、当前Apply权限和Full校验；端口缺失只禁Apply。Owner负责在副作用前持久原完整请求、CAS/幂等键及可查询回执；不支持持久原请求+Query的宿主不得接实际Apply。远端不确定性不由Core内存operation map解决。

Applied必须具备OwnerReceipt、相同Owner、Before精确Patch.Before、After.Revision高于Before且After完整内容等Proposed、逐项覆盖ChangedKeys且无失败/遗漏；版本步进由外部Owner合同决定，Core不猜+1。Partial必须逐项完整列出，After若有只能是Owner真实完整快照，不把Proposed作实际值；不能Adopt为全成功。Rejected须明确无接受/无副作用的Owner原因。Pending/Unknown、回执错误、传输失败、超时/取消后缺证据均阻断新写。设备ACK不能升Applied，After不证明设备ReadBack。

Partial逐项若仍有Pending/Unknown，其外部写门继续未决、DrainReceipt.UnresolvedApplies含原ID，只Query。只有Owner确认所有ChangedKeys各项为Applied/Rejected（无未决）且有完整实际After才能作为终结Partial：不允许AdoptAppliedBaseline，但可明确PlanRebase/Rebase这份实际After（Revision必须较新）或关闭后用该真实基线Create，让操作者重新决定剩余差异；不自动Apply剩余项。缺实际After保Unknown门并要求Owner查询/人工恢复。已验证Applied或无副作用Rejected不能被随后NotFound/Unknown/Pending降级；同原请求冲突的终结事实PE-9004并保最后确认事实和诊断，交Owner核真，不据坏回执再写。终结Partial的逐项状态同样不能反向回Pending，新Revision另属新请求。

ResolveApplyAsync返回 `PeResult<ApplyReceipt>`，接收原完整Patch，仅读原operation、key和RequestSha256，不调用Apply。Query使用新的当前Query授权及有限期限，context仍绑定原操作/epoch/request摘要，EffectiveDeadline仅为本次查询期限。查询一次在途，QueryInFlight可见；超时/NotFound/Denied仍保原Pending/Unknown，不换ID重发。Query客户端Task/借用也纳入排空；更新原记录的Apply投影并递增RecordVersion、发ApplyResolved，不第二次发布原dispatch终态。冷恢复由宿主读原持久请求直调同端口Query，完成后显式创建新session；不得重建当前baseline后凭latest猜原操作成功。

Apply/Query 各次本地调用都保实际原 Task；停止等待后迟到回执仍按原 OperationId/Patch hash/Before 和完整预算核验后更新原记录，不先用 Unknown 终结原 Task。Query 仍在途时拒第二查询，不能不断 timeout 生成新 Task。PE-9004 回执保预算内诊断但不复制非法正文，也不释放未知写门；原持久请求及查询证据由 Owner 持有。Applied/Rejected 是外部事实，发布载荷仍核当前 View/Query 权；撤权只阻止披露，不删除后来已确认事实。Closed 前待本地所有调用排空，Closed 后 Root 凭原 Patch、原端口和新的 Query 授权直接 QueryAsync，不再通过关闭 session；Query 的 context 保原 SessionId/OperationId/epoch/generation/hash，只重算有限 EffectiveDeadline。该冷查询也须 Root 槽持原 Task、独立 Drain/有限等待，未知时不释放槽；没有收到真实最终回执不发新的 Apply。

## 9. 并发、释放失败与线程

- 会话短锁串行校验提交、generation、Undo及operation注册；不可跨await/端口/Observer持锁。字段输入、候选、Schema和结果先按预算冻结，再校验；发布前复核当前性。两session不共享任何可变值/取消/语言事实。
- Preview和Recommend串行共用执行名额，等待队列显式有界。Apply只有一个未决且要求其它执行已排空，反向在Apply未决时不启动推荐/试算；新编辑可使在途预览过期，但不能写正在Apply的前像。QueueFull不丢已接纳正式结果。
- Adapter Execute抛异常之前也可能已持资源；Core按原OperationId继续调用Drain，Adapter保留未交回Owner。只要Task未退出或释放失败，就保持DrainUnknown和名额，禁止再次调用Execute“顺带清理”。
- 每次 Adapter Drain 的 cleanup CTS 独立于原业务 CTS，期限不超过本次 Close/Drain 剩余时间和 CloseTimeout；保实际清理 Task，观察到期不遗弃，不再并行调同一 operation Drain。一次 Core Drain 可以有限等待已有清理、收集各独立 ACK；真实 Execute/Query/Observer Task 与 Adapter 两个 true ACK 同时满足才发 ResourcesReleased。等待期限用 TimeProvider 的单调计时，UTC 只用于绑定外部截止；原任务晚返不会重置总操作期限。
- Drain必须明确ExecutionStopped和ResourcesReleased皆true，且Core观察到实际执行/查询Task退出，才转Released；DTO零计数不替代证明。子借用未释放不得提前放父；清理某项失败仍清理其它独立项，保未确认引用供原Owner重试。
- 取消token/Task.WaitAsync只停止请求或等待，不强杀HALCON/SDK/Observer；不Task.Run之后忽略未完成Task、不用线程中止。等待deadline只影响等待结果，Core追踪同一后台任务直至真实退出。
- UI用Dispatcher呈现冻结投影，CPU全量校验/Hash/大diff由后台调用相同Core；虚拟化不减少实际校验集合，合并显示不改变正式事件/记录。
- Closed墓碑在MaxOperationRecords内保留；运行中记录及未决Apply不淘汰。容量满拒新操作 `PE-4003`，宿主不能删除未知记录假报释放；业务持久历史归Owner，不新增第二Store。

## 10. 迁移、发布与回退

### 10.1 模块与数据版本

程序集SemVer；本未实现v0.1→v0.2的签名更正只作为新实现基线，不假造旧客户端适配结果。Schema、Definition、canonical、Provider/Adapter、外部Owner版本分别绑定；同major不改变已发布的字段/单位/四态/生命周期意义。未知必填类型/enum/version拒绝；Core不扩Opaque写通道。

### 10.2 纯迁移与草稿恢复

~~~csharp
public sealed record ParameterMigrationRequest(
    ParameterSchema OldSchema, ParameterBaseline OldBaseline,
    ParameterSnapshot OldDraft, ParameterSchema NewSchema, ContentRef MigrationPlan);
public sealed record ParameterMigrationResult(
    ParameterSnapshot Candidate,
    ContentRef MigrationPlan, IReadOnlyList<ValidationIssue> Warnings);
public interface IParameterMigrationAdapter {
    PeResult<ParameterMigrationResult> Migrate(ParameterMigrationRequest request);
}
~~~

迁移为宿主显式提供的纯同步、无IO函数；Plan逐字段声明旧新key/type/unit/默认及丢失处理，由领域Owner批准，不由Core猜。输出Candidate再次按新Schema Full校验、来源及规范hash核验，失败保留原Schema/基线/草稿，禁止外部激活。迁移函数只生成候选，不制造NewBaseline/Owner版本：宿主必须从Owner取得真实的新Schema基线后Create新session，再把Candidate差异显式Atomic导入；Owner未提供映射基线时只保候选，不发Apply。不改正在运行的session，不继承旧验证/操作/权限或自动Apply。Schema或来源变化与原ApplyUnknown冲突时先Query原请求，不能拿迁移后Patch替原键。

Core不存文件/JSON/Undo journal。保存可恢复编辑状态时由宿主Owner保管原Schema、基线、草稿、历史前后像及原顺序；无UI恢复入口为§2声明的 `IParameterEditorFactory.Restore(ParameterSchema schema, EditorCheckpoint checkpoint, ...)`。Checkpoint契约为：

~~~csharp
public sealed record UndoEntry(
    ParameterSnapshot Before, ParameterSnapshot After, EditOrigin Origin);
public sealed record EditorCheckpoint(
    ContentRef Schema, ParameterBaseline Baseline, ParameterSnapshot Draft,
    IReadOnlyList<UndoEntry> Undo, IReadOnlyList<UndoEntry> Redo, string Sha256);
~~~

session公开 `PeResult<EditorCheckpoint> ExportCheckpoint()`，核当前完整View权及字节预算，只在无活动operation、无Pending/Unknown Apply时允许；导出不改变编辑。Checkpoint TLV域 `pe-checkpoint-v2`，依字段序（跳过Sha256），栈从底到顶。Restore的完整Schema由宿主显式提供，逐项比checkpoint.Schema、Baseline/Draft的三元组；沿§3.4内嵌Snapshot规则编码。checkpoint不是授权/设备状态，旧导出也不证明后来没有Apply；宿主恢复前必须核当前Owner与原未决请求，Unknown先查询，基线已变只允许显式三方重基，不直接宣称草稿仍当前。

Restore验证hash、Schema身份、每历史合法值/来源/预算、相邻Undo.After内容=下一Before、Undo顶After=Draft、Redo顶Before=Draft及反序可连；代次只是记录旧编辑链，恢复session另分配Id且从checkpoint.Draft.Generation开始，后继修改继续+1。无变更的校验/显示不插入历史；历史不足/篡改拒绝，不猜顺序不清原件。重开不恢复建议/试算有效性或执行权，不重跑操作。持久checkpoint不是生产配置Owner；崩溃发生在Apply未决时只能先用Owner原请求恢复，禁止用checkpoint遗漏它。

### 10.3 独立发布与回退

Core包只有模块DLL/XML API、错误资源键/协议说明及相应已运行验收引用；WPF包另含本机DevExpress既定引用/资源和Host。不预造多套发布报告或下载替换控件。构建/测试可按精确csproj独立执行，不需产品Shell/平台私表；真实消费者适配在各宿主。

回退前停止准入、排空本session；本地Undo/Discard只退草稿，不撤已提交Owner事实。外部回退另由Owner形成新CAS版本及当前权限，不通过“恢复默认”按钮代替。旧二进制不懂pe-v2-tlv1则拒新checkpoint/Schema并保原字节，不能重hash或跳过未知字段；旧已签客户基线仍由原Owner读，不由本模块覆盖。

## 11. 可选 WPF / DevExpress专业参数 Inspector

### 11.1 操作者、任务流和布局

本UI为嵌入式Inspector，不复制平台Shell或测量工作台。工程员：选择宿主对象 → 搜索参数 → 单改/批改 → 看关联错误/diff → 验证 → 建议或试算 → 明确采用候选 → 重新验证 → 交Owner应用；维护员：读当前/请求值 → 只改获权字段 → 看ApplyMode → 验证 → 应用/查询原请求。显示、编辑、推荐、执行、应用权限分别可见，不把“可显示图像”推导成可执行。

冻结默认布局为：顶部44 DIP对象标题/短状态，搜索及“常用/全部/已改/问题”过滤；中部PropertyGrid或参数矩阵；底部32 DIP状态栏+固定命令条。主区至少占Inspector客户区70%，详情/差异默认折叠，打开时不盖正在编辑行。标准Inspector宽360–480 DIP、最小320；标题/状态可两行，单位列保留，名称最长可换行并有SuperTip，不靠省略隐藏错误。这是布局设计数值，不是算法或性能门槛。

宿主提供图像时，1920×1080固定验证viewport扣除taskbar/边框/title/status后量实际客户区；图像默认可见面积≥60%、专注≥80%，Inspector/树可停靠或按需浮出，保持原图完整比例不裁图凑面积。无图像的设备工具使用全宽参数矩阵，不凭空造影像窗。PropertyGrid/矩阵/差异/问题用同一session，切页不复制状态。宿主拥有DockLayoutManager，模块不嵌套第二个Dock容器；布局持久化由宿主带模块/Schema版本保存，提供“恢复布局”，保留旧配置。

视觉层级：标题16 DIP semibold、正文/参数14 DIP、次要说明12 DIP，4/8/12/16 DIP间距，普通行最小28 DIP。继承宿主既定DevExpress主题，不设置ApplicationThemeName或全局Culture；状态颜色同时带文字/图标，错误不能只有红框。动画仅面板/选择提示，跟随宿主减少动效设置，不改布局尺寸、不延迟命令、不中断输入。验证视觉品质与键盘可用性分别验收，不用截图宣称完成。

### 11.2 25.2公开控件组合与动态参数路线

| 任务 | 已核公开入口 | 具体用法及限制 |
|---|---|---|
| 单对象动态参数 | PropertyGridControl.SelectedObject、PropertyDefinitions/PropertyDefinitionsSource、SelectedPropertyPath、ShowSearchBox、ShowCategories | 使用本UI私有ICustomTypeDescriptor投影；只生成领域明确字段，不反射产品对象 |
| 定义与编辑器 | PropertyDefinitionBase.Path/Header/Description/IsReadOnly；PropertyDefinition.EditSettings/CellTemplate/PostOnEditValueChanged | 名称/单位/来源/错误分层；禁自动即时提交每个滑块事件；动态ReadOnly取Core字段状态 |
| 拒非法输入 | PropertyGridControl.ValidateCell；ValidateCellEventArgs.NewValue/IsValid/ErrorContent | 调Parse+CheckEdits，校验回调不改Core；参数setter也不直接写草稿 |
| 批改/差异/问题 | GridControl + TableView；GridViewBase.ValidateCell；TreeListControl及选择事件 | 明确稳定key选择、前/后值、类型/单位、适用/拒绝/影响数；不用SelectedObjects自动逐对象写 |
| 数值/枚举/文本 | SpinEditSettings / ComboBoxEditSettings / CheckEditSettings / TextEditSettings / TrackBarEditSettings | 映射类型；超2^53的long绝不经double滑块，使用精确文本解析；枚举value/display分离 |
| 次要动作及提示 | DevExpress.Xpf.Editors.Flyout.FlyoutControl；SuperTip；BarManager/Bar.IsStatusBar | 来源/范围/恢复说明按需展开；验证/试算/应用/取消留常驻，不藏关键动作 |
| 比较与联动 | ChartControl（仅已有可比较的有效数字结果） | 原数值按相同单位/输入/Profile分组；图/行按ItemId联动，不插值造测值、不自算质量排名 |
| 宿主工作区 | DockLayoutManager/LayoutGroup/LayoutPanel；ThemeManager.SetThemeName | 宿主停靠/主题，Inspector仅局部主题和请求布局恢复；不改全局窗口 |

本机25.2随附官方XML实读依据和hash见§17.3；本会话无dxdocs/匹配WPF技能可调用，官网403不解释成不支持。未读到的属性不写XAML猜测。表中是公开名称及文档支持的用途，尚未执行WPF/UIA/渲染或量测虚拟化性能。

主路线冻结为 `ICustomTypeDescriptor + PropertyDescriptor` 的UI投影，避免Runtime Reflection.Emit、任意JSON属性反射和Shell ViewModel泄漏。descriptor类型从ParameterDefinition取得，不从当前Value.GetType推（Missing/Null不能抛错）；Key含点/连字符时用稳定 `p000001` 顺序descriptor名到原Key的一对一映射，不能把Key当嵌套Path。排序/语言改变不重建身份映射；Schema切换才换完整投影。Browsable/Category/DisplayName/ReadOnly仅UI元数据，最终Core重新校验；GetProperties(Attribute[])须过滤请求的属性，空集合的GetDefaultProperty返回null，不取第0项。

descriptor.SetValue只更新私有编辑缓冲；ValidateCell先Parse/CheckEdits验证整个候选；一次编辑确认后唯一调用Core SetValues。拒绝/并发冲突重新Read映射原值且保留待修token，UI不显示假成功。内置Reset菜单改为明确Core ResetDefault/Remove语义，无默认时禁用；禁止沿用示例的“上一次值”回退。undo/redo、建议采用和批量paste均走Core，不在descriptor维护第二套历史。

基本/高级由定义Advanced控制，搜索可发现高级字段并显式展开；隐藏≠忽略校验。关联错误展开定位相关行并说明受哪个字段影响，Unknown显示阻断而不是把字段消失。大Schema只给PropertyGrid当前类别的完整授权投影，类别树和矩阵虚拟化；不宣称PropertyGrid任意动态描述器均原生虚拟化。切类别先确认/保留当前buffer，无效值不自动提交；全量校验仍涵盖全部定义。整字段选择列表与过滤可见列表分开，批改前显示实际key数和排除原因。

### 11.3 公共接入、三语与编辑缓冲

WPF唯一公开控件 `ParameterEditorControl : System.Windows.Controls.UserControl`，无参构造。它提供：

~~~csharp
public sealed record HostPreviewInteractionPolicy(
    bool AutoPreview, TimeSpan? Debounce, bool MergeEdits);
public sealed record InspectorOptions(
    string AutomationIdPrefix, HostPreviewInteractionPolicy? PreviewPolicy);
public sealed record EditorPresentation(
    string ResourceCulture, string FormatCulture, string ThemeName, long Revision);
public interface IEditorTextResources {
    string Resolve(string resourceKey, string resourceCulture);
}
public interface IInspectorCommandBinding {
    PeResult<PreviewRequest> CreatePreviewRequest(EditorView current);
    PeResult<RecommendationRequest> CreateRecommendationRequest(EditorView current);
    PeResult<PatchOptions> CreatePatchOptions(EditorView current);
    ValueTask<PeResult<bool>> RetainOriginalApplyAsync(
        PatchIntent original, CancellationToken cancellationToken);
    TimeSpan ApplyTimeout { get; }
    TimeSpan QueryTimeout { get; }
}
// 以下为ParameterEditorControl的公开成员签名，位于Wpf namespace：
// IInspectorCommandBinding? CommandBinding { get; set; }
// PeResult<bool> Attach(IParameterEditorSession session, InspectorOptions options,
//                      IEditorTextResources resources, EditorPresentation presentation);
// ValueTask<PeResult<bool>> SetPresentationAsync(EditorPresentation presentation,
//                      CancellationToken cancellationToken = default);
// ValueTask DetachAsync(CancellationToken cancellationToken = default);
~~~

Attach只借用已有session、核Read和当前权限、创建UI投影及Subscribe，不Create新session、不改baseline、不自动推荐/Preview/Apply；重复Attach同实例幂等，另实例先Detach；Closed/撤权/来源失效拒绝。不重放过期Open、不延长旧截止、不恢复未知写权限。Detach取消自身投影读取、等UI回调结束后退订，不Close宿主session、不归还外部native资源；无隐藏窗口初始化。宿主必须在该控件Dispatcher调用呈现入口；异步读取在后台，发布前核presentation revision/选择generation/session，迟到不得换回旧值。

SetPresentationAsync仅更新局部资源/格式/ThemeName；ResourceCulture支持zh-CN/zh-TW/en-US并可扩，FormatCulture显式给出；不改CurrentCulture/CurrentUICulture/全局主题。缺资源按en-US→中性短标签回退并诊断，不铺内部key。处于IME/数值输入时保留原token、selection和启动编辑时的解析culture/unit，待确认/取消后使用新格式；不能切语言把 `1,5` 重解成15。在途操作的Schema/Profile/hash/期限不变，弹窗/菜单/SuperTip同修订更新。资源语言、数字显示、解析和持久编码分离，复用DEV-UI-040既有语言方法；无模块语言切换按钮。

CommandBinding 是 WPF 加法公开接线，不改既有 Create/SetValues/Attach/Detach 签名：未提供时仍完整编辑/校验/差异/撤销，推荐/试算/Apply 明确“未连接”，不猜 Profile/Inputs/Scope。提供时三项 Create 方法是无 IO、有限纯构造，输入为本次冻结 EditorView，生成新 OperationId、匹配当前 generation 和宿主精确引用；Core 再核全部权限/预算。Inspector 的建议/试算调用同 session API，当前 operation 选择槽只绑定返回 ID；建议列表→选候选→CheckEdits/diff→AcceptSuggestion→同 PropertyGrid 标记和 Chart 原结果联动，不再实现参数校验或业务规则。用户明确“应用”才 CreatePatch→RetainOriginalApplyAsync→收到成功 ACK→RequestApplyAsync；无 ACK/超时/Detach/代次变更均不派发。绑定者负责原请求持久化、CAS/Query Owner 接线；保留 ACK 不能表示设备执行完成。当前 Unknown 原 Patch 保在宿主 Owner，可按 QueryTimeout 只 Resolve 原请求。ApplyTimeout/QueryTimeout 有限正值并受 Core 策略；绑定变更只作用未来命令，不换旧操作 Owner。

卸载的准确调用形状：宿主先在有界 UI 根槽登记 control、session、CommandBinding、原 Retain/投影/Detach Task，再使用独立有限 cleanup CTS 调 DetachAsync，并对同一原 Task 做有限 WaitAsync。token/观察到期时保槽和控件，不把它放新窗口或再 Attach；只有真实 Detach Task 完成、Dispatcher 发布和绑定 ACK 回调全退出才解除 UI 槽，Core/端口仍归宿主。若关闭 Dispatcher 无法送达最终清理，报告 PE-4002 保槽，不能在后台伪造 Dispatcher ACK。随后重新 Attach 同 session 用当前 Read/权限/呈现修订；不重放 Retain/Apply。控件内部投影任务必须有界，Detach 停新读取、退订并排空原任务，等待取消只结束本次等待。宿主有限观察期限复用自己的 Profile（例如 §12 的 CloseTimeout），不在模块另设默认值。

默认无PreviewPolicy仅显式“试算”。AutoPreview=true要求Debounce有限非负、来自宿主Profile、完整验证及当前Preview授权；策略只安排外部调用，Core不存时长、不把150ms写默认。MergeEdits只合并UI待提交显示/拖动事务，不丢正式输入、错误、Undo及已接纳operation。拖动先缓冲，松开/Enter形成一批，Esc还原；预览即便自动也只算冻结候选，不自动Apply。

AutoPreview的“冻结候选”必须先由操作者完成一次编辑确认并成功SetValues成为当前Draft，再Full校验→Binding.CreatePreviewRequest(current)→PreviewAsync；不允许拿descriptor缓冲/CheckEdits.Proposed绕Core请求隐式试算另一个Snapshot。防抖只合并尚未接纳的最新待试算generation，之前已接纳任务仍各自按原ID排空/history；schema/source/权限失效或IME未结束不提交，不以自动触发恢复旧请求。无法合法提交则保token/错误、不发Preview；关闭/Unbind停止新自动任务，原任务归Root/SessionOwner。

### 11.4 键盘、批量交互与反馈

Tab/Shift+Tab按搜索→分类→字段→命令→状态；Ctrl+F搜索、F2/Enter编辑、Esc取消当前buffer/Flyout、Ctrl+Z/Ctrl+Y在非文本编辑时调用Core Undo/Redo（文本编辑中保留编辑器自身文本Undo，不能混用）；Ctrl+Enter执行当前可用验证主动作，不默认设备Apply。快捷键三语提示；AutomationId为prefix+稳定Key/操作ID，不用翻译或可见row index。IME组合文本未结束不触发试算/应用。

多行paste先隔离解析类型/单位/大小、CheckEdits，展示diff再明确确认；原子批改一次Undo，IndependentPartial须显式选择且遵守§5。不以SelectedObjects批量setter写多个草稿，跨对象/跨配方事务由宿主Owner实现。行内只显示单位、短原因和错误定位；来源、完整范围/ApplyMode及诊断放SuperTip/Flyout。关键错误常驻，不能仅悬停可见。

操作文字固定语义：

| zh-CN | zh-TW | en-US | 作用 |
|---|---|---|---|
| 验证 | 驗證 | Validate | Full校验，无写入 |
| 建议 | 建議 | Suggest | 请求候选，无自动采用 |
| 采用 | 採用 | Accept | 明确候选，仅改草稿 |
| 试算 | 試算 | Preview | 工程执行，不质量放行 |
| 应用 | 套用 | Apply | 外部Owner意图，显示其原回执 |
| 查询结果 | 查詢結果 | Check result | 原请求只读查询 |
| 恢复默认 | 還原預設值 | Reset default | 领域合法默认，一次草稿修改 |
| 排空中 | 等待作業結束 | Waiting to stop | 未确认资源归还 |
| 未提供 / 无效 | 未提供 / 無效 | Not provided / Invalid | 区分缺值、无效与有效0 |

Completed不推OK；Apply Pending/Unknown只给“查询结果”，禁再Apply。无值、无效、未观测分别显示，不填0/伪不确定度；有效零显示0。结果详情只读同ResultRef的原证据，核operation/Inputs/Profile/Schema/hash及当前权限；错绑/损坏/撤权/超限清旧详情，保仍有读权的原执行状态和短恢复提示，不裁失败项、不重算。Chart只显示原有效可比值；拒识/未执行单列，不从分母消失；Core不授样本标签或排名权。

### 11.5 U1 公开进程根、Binding、预算与确认交接

本节唯一定义 namespace `Asun.Modules.ParameterEditor.Wpf` 的加法 API。既有 `Attach/SetPresentationAsync/DetachAsync` 不改签名；独立/托管窗口采用公开 Binding 根路线。直接 Attach 的兼容入口仍须宿主用同根登记控件/任务，否则不是本 U1 验收 Host。Core 不引用这些类型。以下声明是实施规格，不是已编译类型：

~~~csharp
public readonly record struct InspectorSlotId(Guid Value);
public readonly record struct InspectorBindingId(Guid Value);
public enum InspectorSlotState {
    Reserved, Bound, Unbinding, Retained, Detached, TransferPending, Transferred, Released
}
public enum InspectorWorkKind { Binding, Presentation, Command, RetainApply, Detach, SessionHandoff }
public sealed record InspectorRootOptions(
    int MaximumSlots, int MaximumTasksPerSlot, long MaximumRetainedBytes,
    int MaximumErrorsPerSlot, TimeSpan ObservationTimeout, TimeSpan CleanupTimeout);
public sealed record InspectorSessionHandoff(
    InspectorBindingId BindingId, IParameterEditorSession Session);
public sealed record InspectorSessionAck(
    InspectorBindingId BindingId, SessionId SessionId, ContentRef Owner,
    bool Accepted, string? ErrorCode);
public interface IInspectorSessionOwner {
    ContentRef Identity { get; }
    ValueTask<InspectorSessionAck> AcceptAsync(
        InspectorSessionHandoff handoff, CancellationToken cancellationToken);
}
public sealed record InspectorBinding(
    InspectorBindingId Id, InspectorSlotId SlotId, InspectorProcessRoot Root,
    IParameterEditorSession Session, InspectorOptions Options,
    IEditorTextResources Resources, EditorPresentation Presentation,
    IInspectorCommandBinding? Commands, IInspectorSessionOwner SessionOwner,
    IReadOnlyList<EditorAction> AvailableActions);
public sealed record InspectorRootView(
    InspectorSlotId SlotId, InspectorBindingId? BindingId, SessionId? SessionId,
    InspectorSlotState State, long Revision, int UnfinishedTasks,
    long RetainedBytes, bool DispatcherStopped, bool SessionAckReceived,
    bool DiagnosticOverflow, IReadOnlyList<EditorError> BusinessErrors,
    IReadOnlyList<EditorError> CleanupErrors);
public sealed record InspectorUnbindReceipt(
    InspectorSlotId SlotId, InspectorBindingId? BindingId, long Revision,
    bool UiDetached, bool UiTasksStopped, bool SessionOwnerAccepted,
    bool ResourcesReleased, IReadOnlyList<EditorError> Errors);
public sealed record InspectorTransferAck(
    Guid TransferId, InspectorSlotId SlotId, long Revision,
    Guid SourceRootId, Guid DestinationRootId, bool Accepted, string? ErrorCode);
public sealed class InspectorTransfer {
    internal InspectorTransfer() { } // 仅本Wpf程序集Root内部创建，不开放空token构造。
}
// InspectorProcessRoot为公开sealed类，无环境/静态初始化：
// public InspectorProcessRoot(InspectorRootOptions options, TimeProvider timeProvider);
// public Guid Id { get; }
// public PeResult<InspectorSlotId> Reserve();
// public PeResult<InspectorRootView> Read(InspectorSlotId slotId);
// public PeResult<bool> Register(InspectorBinding binding, ParameterEditorControl control);
// public Task<T> StartOwnedAsync<T>(InspectorSlotId slotId, InspectorWorkKind kind,
//                  Func<CancellationToken, ValueTask<T>> start, CancellationToken token = default);
// public ValueTask<InspectorUnbindReceipt> UnbindAsync(InspectorSlotId slotId,
//                  CancellationToken token = default);
// public PeResult<InspectorTransfer> PrepareTransfer(InspectorSlotId slotId);
// public PeResult<InspectorTransferAck> AcceptTransfer(InspectorTransfer transfer);
// public PeResult<bool> CommitTransfer(InspectorTransferAck acknowledgement);
// public PeResult<bool> RejectTransfer(InspectorTransfer transfer);
// public IReadOnlyList<InspectorRootView> Retained { get; }
// ParameterEditorControl的加法公开成员（保留§11.3成员）：
// public ValueTask<PeResult<bool>> BindAsync(InspectorBinding binding,
//                  CancellationToken token = default);
// public ValueTask<InspectorUnbindReceipt> UnbindAsync(CancellationToken token = default);
// public ValueTask<PeResult<bool>> RefreshAccessAsync(CancellationToken token = default);
~~~

Root 为由 Application/启动 Host 强持的实例，无自动 IDisposable/无 Clear，不由窗口闭包唯一持有。Reserve 在 factory/控件构造前预留槽；没有槽不创建窗口/session/订阅。RootOptions 所有数值有限正值，两个 timeout 也有限正值；根槽/任务/错误数量与保留字节按 Profile 给出，不用 UI 虚拟化减额度。MaximumTasksPerSlot 含绑定工作、原 RetainApply、所有原 Dispatcher/读取/呈现/命令/Detach/Owner ACK Task；Root 抽象管理的 Unbind 观察等待不重复算业务 Task。每操作在调用 start/绑定者前登记槽和预算；预留失败时 StartOwnedAsync 返回已失败 Task（含 PE-4003 的 InvalidOperationException），start 调用数必须0。至少预留 Detach 和 SessionHandoff 各一条恢复通道，不让普通命令耗尽 cleanup 名额。根容量满拒新槽，释放后可重用根容量但永不重用 SlotId/BindingId。

Register 必须在同控件 Dispatcher 调用，核 slot=Reserved、Root 引用相同、binding.Id非空、SessionOwner/资源/Commands/Options/Presentation 完整、有界、同 Control 没有其它 binding、Read 当前权限以及合法呈现；一次性强持 Binding/Control/session/SessionOwner、当前 Dispatcher 和命令端口，检查控件属于同 Dispatcher。它只登记、不启动订阅。Register 参数冻结（Host 资源/权限/端口实例借用，内部数据全深复制）；readonly record 不保证 List 只读。Binding 的不可变身份、Options、Root、Session、SessionOwner、Commands 绑定后不能改指针。ResourceCulture/FormatCulture/ThemeName 的动态修订只走 SetPresentationAsync。Root.Read 是资源状态/短错误元数据，不披露参数；Retained 不输出私有 payload，不因资源状态给读值授权。

AvailableActions 是宿主按已注入端口/功能作出的显式可用性声明，不是权限；列表有限唯一、已定义enum且含View，Register深冻结。Commands=null不得声明Preview/Recommend/Apply；Preview/Recommend对应端口缺省的Host不声明这些动作，不用反射session内部推断。声明View/Edit也仍按当前Core实际权限/字段状态核；声明不含某动作时显示短“未连接”及恢复提示，不反复发请求试探功能。Query只有存在原Patch才可用，即使声明Query也不能构造新的Apply。内置Validate/Diff依当前View可用，Undo/Redo还核Core历史/当前Edit；Access刷新不得把Availability变成角色授权。

BindAsync 首先 Require Dispatcher、验证 Root 已 Register 该精确 Binding/Control；在有界槽登记原 Task 后，读当前 session/权限、创建 §11.2 单一投影和一个 Observer、按既有 Attach 的规则完成。失败/取消仍由同 Root 接收现有订阅、已排入 Dispatcher 的原 Task，状态 Retained；禁止 catch 后置 null 丢 Owner。外层只观察有限 ObservationTimeout；token取消/到期不证明 Bind 原 Task 结束，不允许另一个 Bind/Attach。直接 Attach 兼容路径也只能有一个有效附着；Bind 不能叠加第二订阅，内部最终复用同 Attach 实现。CommandBinding setter 在 Bound/Unbinding/Retained 下拒改（含 PE-2001 的 InvalidOperationException），只能未绑定时设置兼容路线；绑定路线以 binding.Commands 为唯一端口。卸载成功以后可为新 Binding 提供新端口，但未知旧写仍归旧 Owner。

StartOwnedAsync 先登记原 Task 身份、kind、token/CTS及有限预算再调用 start，捕获同步异常为失败 Task，不吞异常；保原业务错误为 BusinessErrors，不能被排空/投影异常覆盖。每槽除串行投影外同一时刻最多一个操作者命令；Projection 可合并待显示修订但已接纳正式命令/错误/回执不丢。RetainApply Task 未结束就不能第二 Retain/Apply；其请求首先由宿主 Owner 保留，再返回 ACK。字段状态、结果、图表、三语和权限刷新都调用同 Core，UI 不另维护校验或参数业务。Root.MaximumRetainedBytes 计 Binding/当前投影/输入缓冲/原请求和结果引用/有界错误及 Task登记元数据的逻辑编码字节；同时受 session十五项上限，原Task/外部native分别观测，不用逻辑0表示真实归零。预留后再复制/hash；过限不截断原错误/字段集合装成功，拒新工作并保根槽，DiagnosticOverflow=true。诊断超过 MaximumErrorsPerSlot 保既有有限错误、overflow标志及首个PE-4003，重复错误不无限堆叠。

Unbind 的固定步骤是：标 Unbinding、拒新输入/命令；发UI取消并停止新投影/退订；按原 Task 等待 Bind/Retain/Command/读取/Dispatcher发布真实结束；在同 Dispatcher 清 descriptor/表/图、解除事件和局部模板引用（无native清理）；同原 session 给 SessionOwner.AcceptAsync 发 InspectorSessionHandoff，收到含同 BindingId/SessionId/Owner.Identity 的 Accepted ACK 后才可解除 UI 的 session强持。SessionOwner 是原 Core/端口根或其授权接管根，不是“窗口已关”的标志；ACK仅表示该根强持既有session/原操作/端口和后续恢复责任，不证明 Core 已 Closed/远端Applied。UI不Close/Dispose session/共享Ports/Resources。成功 UiDetached/UiTasksStopped/SessionOwnerAccepted 全true才 ResourcesReleased=true、slot=Released；Root可移除该已确认槽的活动payload，保有界墓碑。空 Reserved（未 Register）Unbind 无创建回调即可释放；部分 Register/Bind失败也执行上述链。

已完成失败/取消的业务Task也算实际退出；Unbind观察其异常并记 BusinessErrors后继续独立清理，不以Task.WhenAll抛出跳过Detach/SessionHandoff。CleanupErrors只记实际清理步骤失败；收尾成功不能清除BusinessErrors，先前清理失败记录同样留诊断历史，但本次全部真ACK允许ResourcesReleased=true。Released不意味着本次业务成功，外层退出/测试仍核双轴。错误记录、Task异常和metadata只保有界代码，不无限保原Exception/敏感堆栈。

Unbind 原清理使用独立有限 CleanupTimeout CTS，原业务取消不取消清理；保存实际 Detach/Dispatcher/SessionHandoff Task。在 CleanupTimeout/外层 ObservationTimeout 到期时返回 ResourcesReleased=false、slot=Retained，原 Task/Control/Binding/Dispatcher/Owner仍在根；重试只观察未结束原 Task，不能再执行一次 Detach/ACK。已结束失败的独立步骤可在其声明幂等边界重试，其它已ACK步骤不重做。SessionOwner.AcceptAsync 对同BindingId/session必须幂等；同ID异session拒PE-2005，撤权不让真实Core资源无人保管。无法 Dispatcher.Invoke/队列不执行时报告 PE-4002并保持强持；绝不用 Task.Run 清 UI 伪造 Dispatcher ACK。只有回调真实晚退出/同ACK晚到达才更新原 Revision/状态，迟到不回写已解绑控件、不给新窗口套旧结果。UI原Apply因未知而未Resolved，仍由收到ACK的SessionOwner持原Patch Query，不在Unbind重发。

确认转交仅用于上级进程根接管，不能拿来清预算：PrepareTransfer 冻结原槽新准入（原在途仍受原Task），内部快照含RootId/SlotId/BindingId、单调revision、Control/Dispatcher/session/Commands/SessionOwner和全部实际原Task/恢复CTS/错误预算；该opaque token不序列化、不复制 Task。AcceptTransfer 在接收根预留足够槽/任务/字节/恢复通道后以同槽 payload/Task 强持并返回精确Ack；容量不够Accepted=false，原根继续持有。Accepted至Commit之间两根都强持但只有原根写状态/执行cleanup；CommitTransfer验证TransferId/两个RootId/同槽revision和接收ACK后，原根把唯一执行Owner切到接收根并置Transferred，Binding.Root 的内部当前路由随该token迁移（public Binding不另造session）。原根只在接收根实际接受确认后解除payload；重复Commit幂等，不把陈旧ACK接在新槽上。RejectTransfer只能撤未Accepted token，恢复原根执行；Accepted后不能单方丢接收引用，要用精确ACK完成或原两根共同确认拒收。transfer等待有限，超时仍原Owner；无新Root/窗口创建可替代确认。进程重启不序列化UI/Task，只按外部Core Owner原持久请求恢复。

### 11.6 两个可直接构造的 STA 验证 Host

以下完整 U1 Host 源文件位于未来 Wpf.Tests Exe，引用同一个 Core.Tests 内 §12 `ParameterEditor.HeadlessFixtures` 夹具源码（采用编译链接同一文件，不能引用/运行另一 Exe、复制第二参数业务）。§12已经完整定义 FixtureInput/FixtureInputs/FixtureAccess/FixtureApply/FixturePreview/FixtureRecommendation/ProcessRoot，Host不存在未构造输入。两个入口为 `--host algorithm` / `--host device`；参数之外不读环境身份/全局culture。所有引用是fixture，不代表真实样本/SDK/持久配置。测试用户只在当前窗口操作；开两个 Host 时分别调用两个入口的两进程或同测试入口顺序场景，均固定1920×1080验证视口，不改显示设置。

~~~csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Automation;
using Asun.Modules.ParameterEditor;
using Asun.Modules.ParameterEditor.Wpf;
using ParameterEditor.HeadlessFixtures;

namespace ParameterEditor.StaFixtures;

public sealed class StaSessionOwner : IInspectorSessionOwner {
    private readonly ProcessRoot coreRoot;
    private readonly ProcessRoot.Slot coreSlot;
    private InspectorBindingId? accepted;
    public ContentRef Identity { get; }
    public StaSessionOwner(ProcessRoot root, ProcessRoot.Slot slot, string name) {
        coreRoot = root; coreSlot = slot; Identity = FixtureInputs.Ref("sta.owner." + name);
    }
    public ValueTask<InspectorSessionAck> AcceptAsync(
        InspectorSessionHandoff handoff, CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        var same = ReferenceEquals(coreSlot.Session, handoff.Session)
            && coreRoot.Retained.Contains(coreSlot);
        if (accepted is not null && accepted.Value != handoff.BindingId) same = false;
        if (same) accepted = handoff.BindingId;
        return new(new InspectorSessionAck(handoff.BindingId, handoff.Session.Id,
            Identity, same, same ? null : "PE-2005"));
    }
}
public sealed class StaApply : IParameterApplyPort {
    private readonly ProcessRoot.Slot slot;
    public StaApply(ProcessRoot.Slot slot) { this.slot = slot; }
    public ValueTask<ApplyReceipt> ApplyAsync(ApplyIntentRequest r,
        OperationContext context, CancellationToken ct) {
        // 先交进程Core根保原关联，再调fixture端口；撤权/丢响应也有原Task身份。
        slot.OriginalContext = context;
        return slot.Apply.ApplyAsync(r, context, ct);
    }
    public ValueTask<ApplyReceipt> QueryAsync(PatchIntent original,
        OperationContext context, CancellationToken ct) => slot.Apply.QueryAsync(original, context, ct);
    public ValueTask<AdapterDrainReceipt> DrainAsync(OperationId id, CancellationToken ct) =>
        slot.Apply.DrainAsync(id, ct);
}
public sealed class StaCommands : IInspectorCommandBinding {
    private readonly FixtureInput input;
    private readonly ProcessRoot.Slot coreSlot;
    public StaCommands(FixtureInput input, ProcessRoot.Slot coreSlot) {
        this.input = input; this.coreSlot = coreSlot;
    }
    private static PeResult<T> Yes<T>(T value) => new(true, value, Array.Empty<EditorError>());
    public TimeSpan ApplyTimeout => input.Options.OperationPolicy.OperationTimeout;
    public TimeSpan QueryTimeout => input.Options.OperationPolicy.OperationTimeout;
    public PeResult<PreviewRequest> CreatePreviewRequest(EditorView current) =>
        Yes(new PreviewRequest(new OperationId(Guid.NewGuid()), current.Draft.Generation,
            input.Profile, input.Evidence, ApplyTimeout));
    public PeResult<RecommendationRequest> CreateRecommendationRequest(EditorView current) =>
        Yes(new RecommendationRequest(new OperationId(Guid.NewGuid()), current.Draft.Generation,
            input.Profile, input.Evidence, 1, ApplyTimeout));
    public PeResult<PatchOptions> CreatePatchOptions(EditorView current) =>
        Yes(new PatchOptions(current.Draft.Generation, new OperationId(Guid.NewGuid()),
            Guid.NewGuid().ToString("D"), input.Name + "-sta-fixture"));
    public ValueTask<PeResult<bool>> RetainOriginalApplyAsync(PatchIntent p, CancellationToken ct) {
        ct.ThrowIfCancellationRequested(); coreSlot.OriginalPatch = p; coreSlot.Apply.RetainOriginal(p);
        return new(Yes(true)); // 内存 fixture ACK；禁止当真实生产持久性证据。
    }
}
public sealed class StaTexts : IEditorTextResources {
    private readonly Dictionary<string, string[]> values = new(StringComparer.Ordinal);
    public StaTexts(FixtureInput input) {
        foreach (var d in input.Schema.Definitions) {
            var cn = d.Key.Value switch {
                "enabled" => "启用", "count" => "数量", "ratio" => "比例",
                "duration" => "时间", "length" => "长度", "mode" => "模式",
                "note" => "备注", "low" => "下限", "high" => "上限",
                "advanced" => "高级选项", _ => "参数"
            };
            var tw = d.Key.Value switch {
                "enabled" => "啟用", "count" => "數量", "ratio" => "比例",
                "duration" => "時間", "length" => "長度", "mode" => "模式",
                "note" => "備註", "low" => "下限", "high" => "上限",
                "advanced" => "進階選項", _ => "參數"
            };
            values[d.DisplayNameResourceKey] = new[] { cn, tw, d.Key.Value };
            values[d.DescriptionResourceKey] = new[] { "查看范围后输入。", "查看範圍後輸入。", "Check the range before editing." };
        }
        values["parameters"] = new[] { "参数", "參數", "Parameters" };
        values["range.order"] = new[] { "下限大于上限。", "下限大於上限。", "Lower limit exceeds upper limit." };
        values["range.fix"] = new[] { "一起修改上下限。", "一起修改上下限。", "Edit both limits together." };
        foreach (var mode in new[] { "a", "b", "stop", "run" })
            values["mode." + mode] = mode switch {
                "stop" => new[] { "停止", "停止", "Stop" },
                "run" => new[] { "运行", "執行", "Run" },
                _ => new[] { mode.ToUpperInvariant(), mode.ToUpperInvariant(), mode.ToUpperInvariant() }
            };
        values["fixture.suggest"] = new[] { "查看候选差异。", "查看候選差異。", "Review the candidate changes." };
        values["fixture.metric"] = new[] { "试算数值", "試算數值", "Preview value" };
    }
    public string Resolve(string key, string culture) {
        var index = culture switch { "zh-CN" => 0, "zh-TW" => 1, _ => 2 };
        if (values.TryGetValue(key, out var text)) return text[index];
        // 模块自己的命令/状态/PE错误内置三语资源由模块先解析；此为宿主未知key短回退。
        return index switch { 0 => "未提供说明", 1 => "未提供說明", _ => "Description unavailable" };
    }
}
public sealed class StaHost {
    private readonly Application app;
    private readonly string name;
    private readonly ProcessRoot coreRoot = new(1);
    private readonly InspectorProcessRoot uiRoot = new(new InspectorRootOptions(
        1, 12, 2097152, 32, TimeSpan.FromSeconds(3), TimeSpan.FromSeconds(2)), TimeProvider.System);
    private readonly InspectorProcessRoot takeoverRoot = new(new InspectorRootOptions(
        1, 12, 2097152, 32, TimeSpan.FromSeconds(3), TimeSpan.FromSeconds(2)), TimeProvider.System);
    private InspectorProcessRoot currentRoot;
    private InspectorSlotId slotId;
    private ProcessRoot.Slot? coreSlot;
    private StaApply? applyAdapter;
    private ParameterEditorControl? control;
    private Task? startupTask, shutdownTask;
    private Task<PeResult<bool>>? bindTask;
    private Task<InspectorUnbindReceipt>? unbindTask;
    private readonly List<string> business = new(), cleanup = new();
    private readonly Window window = new();
    private readonly TextBlock status = new() { TextWrapping = TextWrapping.Wrap, Margin = new Thickness(8) };
    private readonly Button finish = new() { Margin = new Thickness(8) };
    private readonly Button revoke = new() { Margin = new Thickness(8) };
    private readonly Button grant = new() { Margin = new Thickness(8) };
    private readonly Button transfer = new() { Margin = new Thickness(8) };
    private string culture = "zh-CN";
    private long presentationRevision;
    private bool presentationWaiting;
    private bool closingAllowed;
    public StaHost(Application app, string name) {
        this.app = app; this.name = name; currentRoot = uiRoot;
        app.ShutdownMode = ShutdownMode.OnExplicitShutdown; // 未ACK不让最后窗口关导致进程结束。
        // 只用1920×1080物理验证viewport，扣当前系统WorkArea，不改屏幕/DPI设置。
        window.Width = 1920; window.Height = 1080;
        window.WindowStartupLocation = WindowStartupLocation.Manual; window.Left = 0; window.Top = 0;
        window.SourceInitialized += (_, _) => {
            var source = PresentationSource.FromVisual(window);
            var scale = source?.CompositionTarget?.TransformToDevice ?? System.Windows.Media.Matrix.Identity;
            var area = SystemParameters.WorkArea;
            window.Left = area.Left; window.Top = area.Top;
            window.Width = Math.Min(1920d / scale.M11, area.Width);
            window.Height = Math.Min(1080d / scale.M22, area.Height);
            // WorkArea/外框/客户区量测各记录，较大物理桌面也不把窗口放大。
        };
        var shell = new DockPanel();
        var tools = new StackPanel { Orientation = Orientation.Horizontal };
        foreach (var language in new[] { "zh-CN", "zh-TW", "en-US" }) {
            var captured = language;
            var button = new Button { Content = language, Margin = new Thickness(8) };
            button.Click += async (_, _) => {
                try { await LanguageAsync(captured); } catch (Exception e) { Record(business, e.GetType().Name); ShowStatus(); }
            };
            tools.Children.Add(button);
        }
        revoke.Click += async (_, _) => { coreSlot?.Access.Revoke(); await RefreshAccessAsync(); };
        grant.Click += async (_, _) => { coreSlot?.Access.Grant(); await RefreshAccessAsync(); };
        transfer.Click += (_, _) => Transfer(); finish.Click += (_, _) => StartShutdown();
        tools.Children.Add(revoke); tools.Children.Add(grant); tools.Children.Add(transfer); tools.Children.Add(finish);
        DockPanel.SetDock(tools, Dock.Top); DockPanel.SetDock(status, Dock.Bottom);
        shell.Children.Add(tools); shell.Children.Add(status); window.Content = shell;
        AutomationProperties.SetAutomationId(window, "pe.sta." + name);
        window.Loaded += (_, _) => { startupTask ??= StartAsync(shell); };
        window.Closing += (_, e) => { if (!closingAllowed) { e.Cancel = true; StartShutdown(); } };
        ApplyLabels();
    }
    private static T Need<T>(PeResult<T> result) {
        if (!result.Succeeded) throw new InvalidOperationException(string.Join(",", result.Errors.Select(e => e.Code)));
        return result.Value!;
    }
    private static void Record(List<string> target, string code) {
        if (!target.Contains(code) && target.Count < 32) target.Add(code);
        // 32已含首个错误；失败日志饱和不会把既有失败变成功。
    }
    private async Task StartAsync(DockPanel shell) {
        try {
            slotId = Need(uiRoot.Reserve()); // 两根/所有窗口由StaHost/Application强持，先槽后factory。
            var input = name == "algorithm" ? FixtureInputs.Algorithm() : FixtureInputs.Device();
            coreSlot = coreRoot.Reserve(input);
            applyAdapter = new StaApply(coreSlot);
            coreSlot.Session = Need(new ParameterEditorFactory().Create(input.Schema, input.Baseline,
                input.Options, coreSlot.Access, coreSlot.Clock, coreSlot.Preview,
                coreSlot.Recommendation, applyAdapter));
            control = new ParameterEditorControl();
            var binding = new InspectorBinding(new InspectorBindingId(Guid.NewGuid()), slotId, uiRoot,
                coreSlot.Session, new InspectorOptions("pe.sta." + name, null),
                new StaTexts(input), new EditorPresentation(culture, culture, "Office2019Colorful", 0),
                new StaCommands(input, coreSlot), new StaSessionOwner(coreRoot, coreSlot, name),
                name == "algorithm"
                    ? new[] { EditorAction.View, EditorAction.Edit, EditorAction.Preview,
                              EditorAction.Recommend, EditorAction.Apply, EditorAction.Query }
                    : new[] { EditorAction.View, EditorAction.Edit, EditorAction.Apply, EditorAction.Query });
            Need(uiRoot.Register(binding, control));
            shell.Children.Add(control);
            bindTask = control.BindAsync(binding, CancellationToken.None).AsTask();
            Need(await bindTask.WaitAsync(TimeSpan.FromSeconds(3)));
        } catch (Exception e) { Record(business, e.GetType().Name); }
        finally { ShowStatus(); }
    }
    private async Task LanguageAsync(string selected) {
        if (control is null || bindTask is null || !bindTask.IsCompletedSuccessfully
            || !bindTask.Result.Succeeded || shutdownTask is { IsCompleted: false }
            || presentationWaiting) return;
        presentationWaiting = true;
        try {
            await currentRoot.StartOwnedAsync(slotId, InspectorWorkKind.Presentation, async ct => {
                var result = await control.SetPresentationAsync(new EditorPresentation(
                    selected, selected, "Office2019Colorful", ++presentationRevision), ct);
                return Need(result);
            }).WaitAsync(TimeSpan.FromSeconds(3));
            culture = selected; ApplyLabels();
        } catch (Exception e) {
            Record(business, e.GetType().Name); ShowStatus(); throw;
        } finally { presentationWaiting = false; }
    }
    private void ApplyLabels() {
        var en = culture == "en-US"; var tw = culture == "zh-TW";
        window.Title = en ? "Parameters" : tw ? "參數" : "参数";
        revoke.Content = en ? "Revoke access" : tw ? "撤銷權限" : "撤销权限";
        grant.Content = en ? "Grant access" : tw ? "恢復權限" : "恢复权限";
        transfer.Content = en ? "Transfer recovery" : tw ? "移交恢復" : "移交恢复";
        finish.Content = en ? "Close / retry" : tw ? "關閉／再試" : "关闭／重试";
    }
    private async Task RefreshAccessAsync() {
        try {
            if (control is not null && bindTask is { IsCompletedSuccessfully: true }
                && bindTask.Result.Succeeded && shutdownTask is not { IsCompleted: false }) {
                var result = await currentRoot.StartOwnedAsync(slotId, InspectorWorkKind.Presentation,
                    ct => control.RefreshAccessAsync(ct)).WaitAsync(TimeSpan.FromSeconds(3));
                // 撤权PE-2002是预期拒绝，控件已清值；未知/超时依旧保Task与原错误。
                if (!result.Succeeded && result.Errors.Any(e => e.Code != "PE-2002"))
                    Record(business, string.Join(",", result.Errors.Select(e => e.Code)));
            }
        } catch (Exception e) { Record(business, e.GetType().Name); }
        finally { ShowStatus(); }
    }
    private void ShowStatus() {
        var cn = culture == "zh-CN"; var tw = culture == "zh-TW";
        var retained = currentRoot.Retained.Count != 0 || coreRoot.Retained.Length != 0;
        status.Text = retained
            ? cn ? "作业仍由宿主管理。关闭未完成时重试。" : tw ? "作業仍由宿主管理。關閉未完成時再試。" : "Work is still owned by the host. Retry if closing is incomplete."
            : cn ? "资源已归还。" : tw ? "資源已歸還。" : "Resources released.";
        if (business.Count != 0 || cleanup.Count != 0)
            status.Text += cn ? " 原错误已保留。" : tw ? " 原錯誤已保留。" : "Original errors retained.";
    }
    private void Transfer() {
        try {
            if (startupTask is { IsCompleted: false } || shutdownTask is { IsCompleted: false }) return;
            var token = Need(currentRoot.PrepareTransfer(slotId));
            var destination = ReferenceEquals(currentRoot, uiRoot) ? takeoverRoot : uiRoot;
            var response = destination.AcceptTransfer(token);
            if (!response.Succeeded || !response.Value!.Accepted) {
                Need(currentRoot.RejectTransfer(token)); throw new InvalidOperationException("transfer rejected");
            }
            Need(currentRoot.CommitTransfer(response.Value));
            currentRoot = destination; // 同Slot/Control/Task，迁移后cleanup路由此根；不重Bind。
        } catch (Exception e) { Record(cleanup, e.GetType().Name); }
        ShowStatus();
    }
    private void StartShutdown() {
        if (shutdownTask is { IsCompleted: false }) return;
        shutdownTask = ShutdownAsync(); // 先记录任务；窗口取消关闭，方法返回不丢Host。
    }
    private async Task ShutdownAsync() {
        var uiReleased = false; var coreReleased = false;
        try {
            if (startupTask is not null) await startupTask.WaitAsync(TimeSpan.FromSeconds(3));
            if (slotId.Value != Guid.Empty) {
                if (unbindTask is null || unbindTask.IsCompleted)
                    unbindTask = currentRoot.UnbindAsync(slotId, CancellationToken.None).AsTask();
                var receipt = await unbindTask.WaitAsync(TimeSpan.FromSeconds(3));
                foreach (var e in receipt.Errors) Record(cleanup, e.Code);
                var original = currentRoot.Read(slotId);
                if (original.Succeeded) {
                    foreach (var e in original.Value!.BusinessErrors) Record(business, e.Code);
                    foreach (var e in original.Value.CleanupErrors) Record(cleanup, e.Code);
                    if (original.Value.DiagnosticOverflow) Record(cleanup, "PE-4003");
                }
                uiReleased = receipt.ResourcesReleased;
            } else uiReleased = true; // Reserve失败，没有创建UI资源。
            // UI SessionOwner ACK之后再关闭Core，永不把window.Close当Native/Core ACK。
            if (uiReleased)
                coreReleased = coreSlot is null || await coreRoot.CleanupAsync(coreSlot);
            if (uiReleased && !coreReleased && coreSlot is not null)
                coreReleased = await coreRoot.RecoverAsync(coreSlot); // 原session已Closed后的只Query路线。
        } catch (Exception e) { Record(cleanup, e.GetType().Name); }
        finally { ShowStatus(); } // 不覆盖business；正常和失败均确认下列真实根状态。
        if (uiReleased && coreReleased && currentRoot.Retained.Count == 0
            && coreRoot.Retained.Length == 0) {
            closingAllowed = true; window.Close();
            // 手工Host退出0只表示本次接线/资源链无错误，不代表§14全套测试通过。
            app.Shutdown(business.Count == 0 && cleanup.Count == 0 ? 0 : 1);
        }
        // 尚未ACK：不Shutdown，按钮再次观察同原Task；Host/两根留在Application.Run。
    }
    public void Show() => window.Show();
}
public static class Program {
    [STAThread]
    public static int Main(string[] args) {
        var name = args.Length == 2 && args[0] == "--host" ? args[1] : "";
        if (name != "algorithm" && name != "device") return 2;
        var app = new Application();
        var host = new StaHost(app, name); // app.Run未结束前Main强持host/两根/coreRoot。
        host.Show();
        var exit = app.Run();
        GC.KeepAlive(host); // 明确跨Run的进程根强持，不依赖JIT局部变量存活或窗口事件。
        return exit;
    }
}
~~~

此完整 Host 的边界：设备场景构造Duration/Length/Bool/Enum，无推荐/预览端口，Inspector显示“未连接”，其余编辑、批改、差异、验证、应用/原请求查询可用；算法场景构造十字段、关联、候选/preview端口。窗口按钮是测试宿主的权限/语言/根移交入口，模块本身不重复语言切换，不把 FixtureApply 内存ACK当耐久保存。两Host Schema/预算来自 §12，UI根(1槽/12Task/2MiB/32错误/3s观察/2s清理)全为测试值。正式根数值由消费者 Profile 冻结；语言修订原 Task 已根持有，即使外层WaitAsync到期也必须Unbind观察它。未确认UI归还不得提前CoreCleanup或shutdown；原错误仍使首轮运行非零，不因后来cleanup成功改记为首次通过。

公开 API 实施细节避免 Host 补猜：Root.UnbindAsync 可从同控件Dispatcher以外调用，内部只排入已登记原Dispatcher并保其Task；Control.UnbindAsync 委托当前根/同slot，不自行dispose外部Owner。Root内部唯一写入状态串行，任何异步端口都在锁外；AcceptTransfer/Commit和Unbind互斥，TransferPending拒新StartOwned/Bind/Unbind但仍观察实际已登记原Task。窗口权限撤回通过 §2 当前AccessPolicy/Invalidated及有权Read重新核对，UI清当前受限载荷并停止新命令，操作事实留Owner，不靠只把按钮灰掉；Grant仅fixture有授权恢复含义，真实授权不由控件发放。UIA root/field/command IDs 使用Options.AutomationIdPrefix+稳定key/operation，三语资源不参与身份，切语言焦点/buffer/IME行为按§11.3。复用§17.3已经核对的PropertyGrid/ValidateCell/EditSettings、Grid/TableView、Flyout/SuperTip/Chart及ThemeManager公开面，不新增未核实DevExpress属性。Host shell为BCL外壳；精美Inspector的实际控件/布局/联动由§11.1/11.2/11.4实施，不能用BCL测试按钮代替产品UI设计。

Root 每槽仅一个原 Unbind 工作项；公开 UnbindAsync 可以在截止返回 Retained 回执，但实际清理 Task 仍保在工作项。Host 下一次调用该方法只继续观察原项，直到它真实完成或已结束失败可重试；不能以外层 unbindTask.IsCompleted 意味内部 Detach 已结束。成功 Released 重复调用返回同 BindingId 的完整已确认回执，不再次 Accept/Dispose；Read 可以读有界墓碑。Retained 列表只列 Reserved/Bound/Unbinding/Retained/TransferPending 槽，Transferred/Released墓碑不算活动槽，destination AcceptTransfer 同 SlotId 优先替换该根旧 Transferred 墓碑，不减少活动预算；slot绑定身份永不重用。Commit 后控件公开 Unbind/呈现/命令路由当前根，原 Binding.Root 保留原创建身份并只作为转交路由锚，不能把“immutable Binding.Root指针”当当前执行Owner。Host根和接收根自身均由 Application强持。

权限刷新公开入口 RefreshAccessAsync 必须同 Dispatcher 调用，按同绑定session.Read和 §2 当前策略重新取完整投影；成功发布只更新权限/载荷，不改草稿/历史/操作/期限。无读权时返回PE-2002并清当前参数值/候选/结果详情，仅保允许显示的短状态和Root资源诊断；Edit/Preview/Recommend/Apply各命令仍由Core重新核权限。没有公开AccessPolicy token getter，控件不扫描session内部：Host身份来源撤权/恢复时主动调用RefreshAccessAsync，正在执行Core操作的Invalidated仍执行停止/排空链；Host失联无法刷新时下一Core.Read/命令会拒，不能保证已显示数据由Core替UI远程擦除。每次获焦/选择/呈现也重新Read；立即撤权披露清除由宿主身份事件驱动此公开入口。刷新使用同Root有限Presentation工作项，Unbind时保原Task，无新轮询默认时长。

StartOwnedAsync 的 start 在调用者线程无锁启动（UI入口必须 Dispatcher）；Core异步读取内部转后台，呈现 Dispatcher排入任务计入同工作项。Control在一个 Root.StartOwnedAsync 已登记的 Presentation/Command scope 内加入自身子Task列表，不再注册第二工作项/重复同预算；没有外层scope的直接Control呈现入口由控件注册一次。未结束同一呈现槽时第二次呈现拒PE-4001，等待到期后也不能另开原Task；因此 Host.presentationWaiting 外层复位不允许控件无限堆积迟到任务。三语新修订只有成功发布后才更新宿主标题；原表单IME解析culture/unit不受语言按钮先后影响。

Root预算闭合细节：活动payload按 §3.4 TLV 的UTF8字符串长度前缀/标量/集合规则计逻辑字节，WPF对象/Task引用只记固定元数据（Guid ID、kind、revision、phase），实际内存另测；InspectorRootOptions、InspectorBinding数据投影、InspectorRootView/错误各按本节字段顺序，域分别pe-ui-options-v1/pe-ui-binding-v1/pe-ui-root-view-v1。不编码控制实例/Task/Delegate/Dispatcher地址、Session/Owner只记合法身份引用，绝不序列化UI来跨进程恢复。Task元数据预算先checked计数，再注册原Task；每slot最多一个Binding、一份当前投影、一份待发布最新投影、一份活跃输入buffer和一个原Apply请求，后者仍由其Owner持久，超限停止新工作保已有Owner。MaximumRetainedBytes是全根总额，MaximumErrorsPerSlot是两个错误轴总条数；完整派生集合/文本同时受Core十五项预算，集合复制前先有限计数。原CTS/注册在其Task真实退出后解除；Instance Resources/Commands/SessionOwner借用不Dispose。成功/已转交墓碑最多MaximumSlots条，按确认时间FIFO淘汰仅Released/Transferred元数据，活动/未知/待ACK不得淘汰；旧墓碑不再可读返回PE-2006，不能把删除元数据当资源释放。Control迁移时直接持当前执行Root，不依赖旧墓碑来找Owner；原Binding.Root仅来源身份，不能因墓碑满重建session。

转交的Revision为Prepare时固定的转交检查戳，Root.Read.Revision仍可因原Task迟到递增；Commit验证token保存的固定检查戳/尚未提交TransferId，不能因正在退出的原Task使已接收token永久不可提交。接收根在Commit前强持同一槽对象/原Task，原根是唯一状态写者，Commit在两根按RootId确定锁序的短锁内交执行Owner、当前槽内容和现Revision；不复制旧快照覆盖晚回执。陈旧Ack定义为已撤/已提交到其它根/TransferId或固定检查戳不匹配，重复同Ack已成功仍幂等。Reject只撤未Accepted转交；传输本身纯内存同步，不引入另一无限等候工作项，Host Transfer方法只处理一次明确响应。

运行命令（仅未来获准创建工程后）：

~~~powershell
dotnet build tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Wpf.Tests/Asun.Modules.ParameterEditor.Wpf.Tests.csproj -c Release
dotnet run --project tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Wpf.Tests/Asun.Modules.ParameterEditor.Wpf.Tests.csproj -c Release -- --host algorithm
dotnet run --project tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Wpf.Tests/Asun.Modules.ParameterEditor.Wpf.Tests.csproj -c Release -- --host device
~~~

两个交互Host的返回码只表示各自本次接线/资源链结果，不能当整套UI断言报告。正式 Wpf.Tests 的独立 --verify 模式由 §14 的确定用例入口驱动同公开方法及真实UIA，运行全部必需组、输出用例ID/双轴结果、未知/缺失/未完成/跳过均非零；只有全部断言且根ACK通过才0。--host模式未执行的必需项不得记为已通过；CI/主任务只接收 --verify 的测试回执，交互Host是接入验证消费者。未确认仍在Application服务运行的状态为Retained，监督进程到Profile截止记录非零/未排空，不能把手动杀进程记为释放。真正产品样本/设备/权限持久源和实际1920×1080呈现/DPI/三语/UIA/性能门未执行。

上块 Program 是完整 --host 消费入口；未来 Wpf.Tests 的最终 Program 在相同 Main 分派再增加 --verify → §14 场景驱动（其它参数返回2），不能把目前 --host 消费源码当自动测试已经实现。该驱动的步骤与退出规则由 §14 定义，编写断言/真实UIA驱动属于获准实现时的测试代码，不是待选框架/设计或客户外门。没有 --verify 实现就不能执行后声称该运行门通过。

## 12. 两个完整无 UI Host 与进程根 Owner

以下是未来 Core.Tests Exe 内的一个完整夹具源文件（namespace/using 同此块），全部输入、十五项预算、权限、端口、Observer 和根 Owner 均在正文构造；不依赖产品 Shell 或未给出的 schema 变量。它只验证软件接线，合成引用不是图像/设备/持久化事实；FixtureApply 的内存字典不能作为真实 Apply 授权。两个 Host 的入口是 HeadlessHosts.AlgorithmAsync/DeviceAsync，均只用 §2–8 的公开 Core API。所有阈值/期限是测试值，不是客户建议。测试入口先 new ProcessRoot(2)，再依次或交错调用这两个入口。

~~~csharp
using System;
using System.Collections.Generic;
using System.Collections.Concurrent;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.ParameterEditor;

namespace ParameterEditor.HeadlessFixtures;

public sealed record FixtureInput(
    string Name, ParameterSchema Schema, ParameterBaseline Baseline,
    ParameterEditorOptions Options, ContentRef Profile,
    IReadOnlyDictionary<string, ContentRef> Evidence);

public static class FixtureInputs {
    public static ContentRef Ref(string id) =>
        new(id, "fixture-1", ParameterCanonical.Sha256(Encoding.UTF8.GetBytes(id)));
    public static ParameterKey Key(string key) => new(key);
    public static ParameterDefinition Def(
        string key, ParameterValueKind kind, UnitCode unit, ParameterValue value,
        NumericConstraint? numeric = null, IReadOnlyList<AllowedValue>? allowed = null,
        bool required = true, bool nullable = false,
        ParameterPredicate? visible = null) =>
        new(Key(key), key + ".name", key + ".help", "parameters", false,
            kind, unit, unit, numeric,
            kind == ParameterValueKind.Text
                ? new TextConstraint(0, 64, WhitespacePolicy.Preserve, null, null) : null,
            value, required, nullable, false, ApplyMode.OwnerDefined,
            allowed ?? Array.Empty<AllowedValue>(), visible, null, "1", Ref("definitions"));
    public static NumericConstraint Range(decimal min, decimal max, decimal step) =>
        new(new Bound(min, true), new Bound(max, true), step, 0m);
    public static FixtureInput Algorithm() {
        var enabled = new ParameterPredicate.Compare(
            new ParameterOperand.Field(Key("enabled")), CompareOperator.Equal,
            new ParameterOperand.Literal(new ParameterValue.Bool(true), UnitCode.None));
        var defs = new[] {
            Def("enabled", ParameterValueKind.Boolean, UnitCode.None, new ParameterValue.Bool(true)),
            Def("count", ParameterValueKind.Int64, UnitCode.Count, new ParameterValue.Int64(3), Range(0, 100, 1)),
            Def("ratio", ParameterValueKind.Ratio, UnitCode.None, new ParameterValue.Ratio(.50m), Range(0, 1, .01m)),
            Def("duration", ParameterValueKind.Duration, UnitCode.Microsecond, new ParameterValue.DurationMicroseconds(1000), Range(0, 100000, 100)),
            Def("length", ParameterValueKind.Length, UnitCode.Millimetre, new ParameterValue.LengthMillimetres(1), Range(0, 10, .1m)),
            Def("mode", ParameterValueKind.Enum, UnitCode.None, new ParameterValue.Enum("a"),
                allowed: new[] { new AllowedValue("a", "mode.a", false), new AllowedValue("b", "mode.b", false) }),
            Def("note", ParameterValueKind.Text, UnitCode.None, new ParameterValue.Text("参数"), required: false, nullable: true),
            Def("low", ParameterValueKind.Decimal, UnitCode.None, new ParameterValue.Decimal(1), Range(0, 20, 1)),
            Def("high", ParameterValueKind.Decimal, UnitCode.None, new ParameterValue.Decimal(2), Range(0, 20, 1)),
            Def("advanced", ParameterValueKind.Boolean, UnitCode.None, new ParameterValue.Bool(false), visible: enabled)
        };
        var rule = new ParameterConstraint("low-high", new ParameterPredicate.Constant(true),
            new ParameterPredicate.Compare(new ParameterOperand.Field(Key("low")),
                CompareOperator.LessOrEqual, new ParameterOperand.Field(Key("high"))),
            new[] { Key("low"), Key("high") }, IssueSeverity.Error, "range.order", "range.fix");
        return Build("algorithm", defs, new[] { rule });
    }
    public static FixtureInput Device() => Build("device", new[] {
        Def("enabled", ParameterValueKind.Boolean, UnitCode.None, new ParameterValue.Bool(false)),
        Def("duration", ParameterValueKind.Duration, UnitCode.Microsecond, new ParameterValue.DurationMicroseconds(2000), Range(0, 100000, 100)),
        Def("length", ParameterValueKind.Length, UnitCode.Millimetre, new ParameterValue.LengthMillimetres(2), Range(0, 20, .1m)),
        Def("mode", ParameterValueKind.Enum, UnitCode.None, new ParameterValue.Enum("stop"),
            allowed: new[] { new AllowedValue("stop", "mode.stop", false), new AllowedValue("run", "mode.run", false) })
    }, Array.Empty<ParameterConstraint>());
    private static FixtureInput Build(string name, ParameterDefinition[] defs, ParameterConstraint[] rules) {
        var schema = new ParameterSchema(new ContentRef("schema." + name, "2", new string('0', 64)),
            "pe-v2-tlv1", defs, rules);
        schema = schema with { Identity = schema.Identity with {
            Sha256 = ParameterCanonical.Sha256(ParameterCanonical.EncodeSchema(schema)) } };
        // 夹具显式构造真实传入值；这不是 Core 自动补默认。
        var entries = defs.ToDictionary(d => d.Key,
            d => new ParameterEntry(d.DefaultValue!, ValueOrigin.Explicit));
        var snapshot = new ParameterSnapshot(schema.Identity, 0, entries, new string('0', 64));
        snapshot = snapshot with { ContentSha256 =
            ParameterCanonical.Sha256(ParameterCanonical.EncodeSnapshot(snapshot)) };
        var budget = new ParameterResourceBudget(
            16, 512, 65536, 65536, 128, 16, 16, 16, 1048576, 2, 32, 16, 65536, 16, 4);
        return new(name, schema, new ParameterBaseline(Ref("owner." + name), 7, snapshot),
            new ParameterEditorOptions(budget,
                new ParameterOperationPolicy(TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(1))),
            Ref("profile." + name),
            new Dictionary<string, ContentRef> { ["input"] = Ref("input." + name) });
    }
}

public sealed class FixtureAccess : IParameterAccessPolicy, IDisposable {
    private CancellationTokenSource revoked = new();
    private readonly TimeProvider clock;
    public FixtureAccess(TimeProvider clock) { this.clock = clock; }
    public void Revoke() => revoked.Cancel();
    // 只供顺序测试显式重新授权；旧取消 token 永不恢复。
    public void Grant() { revoked.Dispose(); revoked = new(); }
    public void Dispose() => revoked.Dispose();
    public AccessDecision Check(AccessQuery query) =>
        new(!revoked.IsCancellationRequested, clock.GetUtcNow().AddMinutes(1),
            revoked.Token, revoked.IsCancellationRequested ? "PE-2002" : null);
}
public sealed class FixtureObserver : IParameterEditorObserver {
    private long count;
    public long Count => Interlocked.Read(ref count);
    public void OnEvent(ParameterEditorEvent notification) => Interlocked.Increment(ref count);
}
public sealed class FixturePreview : IParameterPreviewExecutor {
    private readonly ConcurrentDictionary<OperationId, bool> stopped = new();
    public ValueTask<PreviewResult> ExecuteAsync(PreviewRequest r, ParameterSnapshot s,
        OperationContext c, IProgress<OperationProgress> progress, CancellationToken ct) {
        stopped[c.OperationId] = false;
        try {
            ct.ThrowIfCancellationRequested();
            // 原输入集合规范摘要，不是随便复用 SnapshotSha256。
            using var stream = new System.IO.MemoryStream();
            void Str(string v) {
                var bytes = Encoding.UTF8.GetBytes(v);
                var len = new byte[4];
                System.Buffers.Binary.BinaryPrimitives.WriteUInt32LittleEndian(len, checked((uint)bytes.Length));
                stream.Write(len); stream.Write(bytes);
            }
            Str("pe-inputs-v2");
            var count = new byte[4];
            System.Buffers.Binary.BinaryPrimitives.WriteUInt32LittleEndian(count, checked((uint)r.Inputs.Count));
            stream.Write(count);
            foreach (var pair in r.Inputs.OrderBy(p => p.Key, StringComparer.Ordinal)) {
                Str(pair.Key); Str(pair.Value.Id); Str(pair.Value.Version); Str(pair.Value.Sha256);
            }
            var result = new PreviewResult(c.OperationId, c.RequestSha256, s.ContentSha256,
                r.Profile, ParameterCanonical.Sha256(stream.ToArray()), FixtureInputs.Ref("fixture.result"),
                new[] { new PreviewItem("metric", new ParameterValue.Ratio(.5m), UnitCode.None,
                    PreviewValidity.Valid, "fixture.metric", FixtureInputs.Ref("fixture.evidence")) },
                FixtureInputs.Ref("fixture.preview"), TimeSpan.Zero,
                new ResourceObservation(0, 0, 0), Array.Empty<EditorError>());
            return new(result);
        } finally { stopped[c.OperationId] = true; }
    }
    public ValueTask<AdapterDrainReceipt> DrainAsync(OperationId id, CancellationToken ct) =>
        new(new AdapterDrainReceipt(id, !stopped.TryGetValue(id, out var done) || done,
            !stopped.TryGetValue(id, out done) || done, Array.Empty<EditorError>()));
}
public sealed class FixtureRecommendation : IParameterRecommendationProvider {
    public ValueTask<RecommendationResult> RecommendAsync(RecommendationRequest r, ParameterSchema schema,
        ParameterSnapshot s, OperationContext c, IProgress<OperationProgress> progress, CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        return new(new RecommendationResult(c.OperationId, c.RequestSha256, s.ContentSha256,
            r.Profile, RecommendationState.Candidates,
            new[] { new ParameterSuggestion("candidate-1",
                new[] { new ParameterEdit(FixtureInputs.Key("ratio"), EditAction.Set, new ParameterValue.Ratio(.75m)) },
                "fixture.suggest", null, r.Evidence["input"]) },
            FixtureInputs.Ref("fixture.provider"), "fixture.suggest"));
    }
    public ValueTask<AdapterDrainReceipt> DrainAsync(OperationId id, CancellationToken ct) =>
        new(new AdapterDrainReceipt(id, true, true, Array.Empty<EditorError>()));
}
public sealed class FixtureApply : IParameterApplyPort {
    private readonly object gate = new();
    private ParameterBaseline current;
    private readonly Dictionary<OperationId, PatchIntent> originals = new();
    private readonly Dictionary<OperationId, ApplyReceipt> receipts = new();
    public FixtureApply(ParameterBaseline baseline) { current = baseline; }
    public void RetainOriginal(PatchIntent patch) {
        lock (gate) {
            if (originals.TryGetValue(patch.OperationId, out var old) && old.RequestSha256 != patch.RequestSha256)
                throw new InvalidOperationException("fixture idempotency conflict");
            originals[patch.OperationId] = patch;
        }
    }
    public ValueTask<ApplyReceipt> ApplyAsync(ApplyIntentRequest r, OperationContext c, CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        lock (gate) {
            var p = r.Intent;
            if (!originals.TryGetValue(p.OperationId, out var original) || original.RequestSha256 != p.RequestSha256
                || c.RequestSha256 != p.RequestSha256) throw new InvalidOperationException("fixture original missing");
            if (receipts.TryGetValue(p.OperationId, out var known)) return new(known);
            var accepted = current.Owner == p.Before.Owner && current.Revision == p.Before.Revision
                && current.Snapshot.ContentSha256 == p.Before.Snapshot.ContentSha256;
            if (accepted) current = new(current.Owner, checked(current.Revision + 1), p.Proposed);
            var state = accepted ? ApplyState.Applied : ApplyState.Rejected;
            var receipt = new ApplyReceipt(p.OperationId, p.RequestSha256, state, p.Before,
                accepted ? current : null,
                p.Changes.Select(x => new ApplyItemReceipt(x.Key, state,
                    accepted ? null : "PE-2001", null)).ToArray(),
                FixtureInputs.Ref("fixture.owner-receipt"), accepted ? null : "PE-2001");
            receipts[p.OperationId] = receipt;
            return new(receipt);
        }
    }
    public ValueTask<ApplyReceipt> QueryAsync(PatchIntent original, OperationContext c, CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        lock (gate) {
            if (receipts.TryGetValue(original.OperationId, out var found)
                && found.RequestSha256 == original.RequestSha256) return new(found);
            return new(new ApplyReceipt(original.OperationId, original.RequestSha256, ApplyState.Unknown,
                original.Before, null, Array.Empty<ApplyItemReceipt>(), null, "PE-2004"));
        }
    }
    public ValueTask<AdapterDrainReceipt> DrainAsync(OperationId id, CancellationToken ct) =>
        new(new AdapterDrainReceipt(id, true, true, Array.Empty<EditorError>()));
}

public sealed record HostReport(string Name, IReadOnlyList<string> BusinessErrors,
    IReadOnlyList<string> CleanupErrors, bool Retained, bool DiagnosticOverflow = false) {
    public int ExitCode => BusinessErrors.Count == 0 && CleanupErrors.Count == 0
        && !Retained && !DiagnosticOverflow ? 0 : 1;
}
public sealed class ProcessRoot {
    public sealed class Slot {
        public readonly FixtureInput Input;
        public readonly TimeProvider Clock = TimeProvider.System;
        public readonly FixtureAccess Access;
        public readonly FixtureApply Apply;
        public readonly FixturePreview? Preview;
        public readonly FixtureRecommendation? Recommendation;
        public readonly FixtureObserver Observer = new();
        public IParameterEditorSession? Session;
        public IDisposable? Subscription;
        public Task? BusinessTask, OriginalCallTask;
        public Task<DrainReceipt>? CleanupTask;
        public PatchIntent? OriginalPatch;
        public OperationContext? OriginalContext;
        public Task<ApplyReceipt>? ColdQueryTask;
        public Task<AdapterDrainReceipt>? ColdDrainTask;
        public bool ColdQueryObserved;
        public ApplyReceipt? ColdReceipt;
        public readonly List<string> BusinessErrors = new(), CleanupErrors = new();
        public bool DiagnosticOverflow;
        public void RecordCleanup(string code) => Record(CleanupErrors, code);
        public void RecordBusiness(string code) => Record(BusinessErrors, code);
        private void Record(List<string> target, string code) {
            if (target.Contains(code)) return;
            if (code.Length > Input.Options.ResourceBudget.MaxTextChars
                || target.Count >= Input.Options.ResourceBudget.MaxOperationRecords) {
                DiagnosticOverflow = true; return;
            }
            target.Add(code);
        }
        public Slot(FixtureInput input) {
            Input = input; Access = new(Clock); Apply = new(input.Baseline);
            if (input.Name == "algorithm") { Preview = new(); Recommendation = new(); }
        }
    }
    private readonly object gate = new();
    private readonly int capacity;
    private readonly HashSet<Slot> owned = new();
    public ProcessRoot(int capacity) {
        if (capacity <= 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        this.capacity = capacity;
    }
    public Slot Reserve(FixtureInput input) {
        lock (gate) {
            if (owned.Count >= capacity) throw new InvalidOperationException("root capacity");
            var slot = new Slot(input); owned.Add(slot); return slot;
        }
    }
    public Slot[] Retained { get { lock (gate) return owned.ToArray(); } }
    // 只有本 Root 收到完整释放 ACK 才解除强持；调用者不能 Clear。
    public async Task<bool> CleanupAsync(Slot slot) {
        lock (gate) { if (!owned.Contains(slot)) return true; }
        try {
            slot.Subscription?.Dispose();
            if (slot.Session is null) { slot.Access.Dispose(); lock (gate) owned.Remove(slot); return true; }
            if (slot.CleanupTask is null || slot.CleanupTask.IsCompleted)
                slot.CleanupTask = CloseAndDisposeAsync(slot);
            var receipt = await slot.CleanupTask.WaitAsync(slot.Input.Options.OperationPolicy.CloseTimeout);
            foreach (var error in receipt.Errors) slot.RecordCleanup(error.Code);
            if (receipt.State != DrainState.Released || receipt.UnresolvedApplies.Count != 0
                || receipt.Errors.Count != 0 || slot.BusinessTask is { IsCompleted: false }
                || slot.OriginalCallTask is { IsCompleted: false }) return false;
            slot.Access.Dispose();
            lock (gate) owned.Remove(slot);
            return true;
        } catch (Exception e) { slot.RecordCleanup(e.GetType().Name); return false; }
    }
    private static async Task<DrainReceipt> CloseAndDisposeAsync(Slot slot) {
        // 独立有限 cleanup token，原业务已取消也执行；外层观察到期仍保本 Task。
        using var cleanup = new CancellationTokenSource(slot.Input.Options.OperationPolicy.CloseTimeout);
        if (slot.OriginalPatch is not null && slot.OriginalContext is null) {
            var operation = slot.Session!.GetOperation(slot.OriginalPatch.OperationId);
            if (operation.Succeeded) slot.OriginalContext = operation.Value!.Context;
        }
        var receipt = await slot.Session!.CloseAsync(
            slot.Input.Options.OperationPolicy.CloseTimeout, cleanup.Token);
        if (receipt.State == DrainState.Released) await slot.Session.DisposeAsync();
        return receipt;
    }
    // Fixture 的冷恢复：只 Query 原 Patch；不新建 session 或 Apply。
    // 同一 Slot 的 Cleanup/Recover 必须由启动 Host 串行调用。
    public async Task<bool> RecoverAsync(Slot slot) {
        lock (gate) { if (!owned.Contains(slot)) return true; }
        try {
            if (slot.Session?.State != SessionState.Closed) {
                if (await CleanupAsync(slot)) return true;
                if (slot.Session?.State != SessionState.Closed) return false;
            }
            if (slot.BusinessTask is { IsCompleted: false }
                || slot.OriginalCallTask is { IsCompleted: false }
                || slot.CleanupTask is { IsCompleted: false }) return false;
            var p = slot.OriginalPatch;
            var original = slot.OriginalContext;
            if (p is null || original is null) return false;
            var queryAccess = slot.Access.Check(new AccessQuery(p.SessionId, EditorAction.Query,
                p.Changes.Select(c => c.Key).ToArray(), p.Proposed.Schema, p.Proposed.ContentSha256));
            if (!queryAccess.Allowed || queryAccess.Invalidated.IsCancellationRequested
                || queryAccess.ValidUntilUtc <= slot.Clock.GetUtcNow()) return false;
            if (slot.ColdQueryTask is null) {
                var deadline = slot.Clock.GetUtcNow() + slot.Input.Options.OperationPolicy.OperationTimeout;
                if (queryAccess.ValidUntilUtc < deadline) deadline = queryAccess.ValidUntilUtc;
                var context = original with { EffectiveDeadlineUtc = deadline };
                // 本方法中 CTS 存活到原 Query Task 完成；调用方超时只保留 Task。
                slot.ColdQueryObserved = false;
                slot.ColdQueryTask = QueryOnceAsync(slot, p, context, queryAccess.Invalidated);
            }
            if (!slot.ColdQueryObserved) {
                try {
                    slot.ColdReceipt = await slot.ColdQueryTask.WaitAsync(
                        slot.Input.Options.OperationPolicy.OperationTimeout);
                    slot.ColdQueryObserved = true;
                } catch (TimeoutException e) when (!slot.ColdQueryTask.IsCompleted) {
                    slot.RecordCleanup(e.GetType().Name); return false;
                }
                catch (Exception e) {
                    if (!slot.ColdQueryTask.IsCompleted) throw;
                    slot.RecordCleanup(e.GetType().Name);
                    slot.ColdQueryObserved = true; slot.ColdReceipt = null;
                }
            }
            if (slot.ColdDrainTask is null)
                slot.ColdDrainTask = DrainColdAsync(slot, p.OperationId);
            var ack = await slot.ColdDrainTask.WaitAsync(slot.Input.Options.OperationPolicy.CloseTimeout);
            if (!ack.ExecutionStopped || !ack.ResourcesReleased || ack.OperationId != p.OperationId
                || ack.Errors.Count != 0) {
                foreach (var error in ack.Errors) slot.RecordCleanup(error.Code);
                slot.ColdDrainTask = null; return false; // 原 Drain 已完成失败，下次才重试。
            }
            // Query Task 和独立 Drain 均完成后，才允许以后另一次 Query；没有 Apply 重发。
            var receipt = slot.ColdReceipt;
            slot.ColdQueryTask = null; slot.ColdDrainTask = null;
            var viewAccess = slot.Access.Check(new AccessQuery(p.SessionId, EditorAction.View,
                slot.Input.Schema.Definitions.Select(d => d.Key).ToArray(),
                p.Proposed.Schema, p.Proposed.ContentSha256));
            if (!viewAccess.Allowed || viewAccess.Invalidated.IsCancellationRequested
                || viewAccess.ValidUntilUtc <= slot.Clock.GetUtcNow()) return false;
            // 固定 Fixture 的完整 Applied 回执核对；真实 Owner 另按 §8.4 核 Partial/Rejected。
            if (receipt is null || receipt.State != ApplyState.Applied
                || receipt.OperationId != p.OperationId || receipt.RequestSha256 != p.RequestSha256
                || receipt.OwnerReceipt != FixtureInputs.Ref("fixture.owner-receipt")
                || receipt.Before.Owner != p.Before.Owner || receipt.Before.Revision != p.Before.Revision
                || receipt.Before.Snapshot.ContentSha256 != p.Before.Snapshot.ContentSha256
                || receipt.Before.Snapshot.Generation != p.Before.Snapshot.Generation
                || !ParameterCanonical.EncodeSnapshot(receipt.Before.Snapshot).SequenceEqual(
                    ParameterCanonical.EncodeSnapshot(p.Before.Snapshot))
                || receipt.After is null || receipt.After.Owner != p.Before.Owner
                || receipt.After.Revision <= p.Before.Revision
                || receipt.After.Snapshot.Schema != p.Proposed.Schema
                || receipt.After.Snapshot.ContentSha256 != p.Proposed.ContentSha256
                || !ParameterCanonical.EncodeSnapshot(receipt.After.Snapshot).SequenceEqual(
                    ParameterCanonical.EncodeSnapshot(p.Proposed))
                || receipt.Items.Count != p.Changes.Count
                || receipt.Items.Select(i => i.Key).Distinct().Count() != p.Changes.Count
                || receipt.Items.Any(i => i.State != ApplyState.Applied || i.ErrorCode is not null)
                || p.Changes.Any(c => !receipt.Items.Any(i => i.Key == c.Key))) return false;
            slot.Access.Dispose();
            lock (gate) owned.Remove(slot); // 两轴旧错误保留，恢复 ACK 不改原首轮报告。
            return true;
        } catch (Exception e) {
            slot.RecordCleanup(e.GetType().Name);
            if (slot.ColdDrainTask is { IsCompleted: true }) slot.ColdDrainTask = null;
            return false;
        }
    }
    private static async Task<ApplyReceipt> QueryOnceAsync(Slot slot, PatchIntent p,
        OperationContext context, CancellationToken invalidated) {
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(invalidated);
        var remaining = context.EffectiveDeadlineUtc - slot.Clock.GetUtcNow();
        if (remaining <= TimeSpan.Zero) throw new TimeoutException();
        cts.CancelAfter(remaining);
        return await slot.Apply.QueryAsync(p, context, cts.Token);
    }
    private static async Task<AdapterDrainReceipt> DrainColdAsync(Slot slot, OperationId id) {
        using var cleanup = new CancellationTokenSource(slot.Input.Options.OperationPolicy.CloseTimeout);
        return await slot.Apply.DrainAsync(id, cleanup.Token);
    }
}
public static class HeadlessHosts {
    public static Task<HostReport> AlgorithmAsync(ProcessRoot root, CancellationToken ct) =>
        RunAsync(root, FixtureInputs.Algorithm(), ct);
    public static Task<HostReport> DeviceAsync(ProcessRoot root, CancellationToken ct) =>
        RunAsync(root, FixtureInputs.Device(), ct);
    private static T Need<T>(PeResult<T> result) {
        if (!result.Succeeded) throw new InvalidOperationException(
            string.Join(",", result.Errors.Select(e => e.Code)));
        return result.Value!;
    }
    private static async Task<OperationView> Released(
        ProcessRoot.Slot slot, PeResult<OperationView> result) {
        var view = Need(result);
        if (view.Phase != OperationPhase.ResourcesReleased) {
            var drain = await slot.Session!.DrainAsync(
                slot.Input.Options.OperationPolicy.CloseTimeout, CancellationToken.None);
            if (drain.State != DrainState.Released) throw new InvalidOperationException("PE-4002");
            view = Need(slot.Session.GetOperation(view.Context.OperationId));
        }
        if (view.Phase != OperationPhase.ResourcesReleased || view.Outcome != OperationOutcome.Completed)
            throw new InvalidOperationException("operation incomplete:" + view.Outcome);
        return view;
    }
    private static async Task<HostReport> RunAsync(ProcessRoot root, FixtureInput input, CancellationToken ct) {
        ProcessRoot.Slot slot;
        try { slot = root.Reserve(input); }
        catch (Exception e) { return new(input.Name, new[] { e.Message }, Array.Empty<string>(), false); }
        try {
            // Root 槽在 Factory 前存在；Factory 失败也走 finally。
            slot.Session = Need(new ParameterEditorFactory().Create(input.Schema, input.Baseline,
                input.Options, slot.Access, slot.Clock, slot.Preview, slot.Recommendation, slot.Apply));
            slot.Subscription = slot.Session.Subscribe(slot.Observer);
            slot.BusinessTask = BodyAsync(slot, ct);
            await slot.BusinessTask;
        } catch (Exception e) { slot.RecordBusiness(e.GetType().Name + ":" + e.Message); }
        finally { await root.CleanupAsync(slot); }
        return new(input.Name, slot.BusinessErrors.ToArray(), slot.CleanupErrors.ToArray(),
            root.Retained.Contains(slot), slot.DiagnosticOverflow);
    }
    private static async Task BodyAsync(ProcessRoot.Slot slot, CancellationToken ct) {
        var s = slot.Session!; var input = slot.Input;
        var initial = Need(s.Read()); var g = initial.Draft.Generation;
        ParameterEdit[] edits = input.Name == "algorithm" ? new[] {
            new ParameterEdit(FixtureInputs.Key("low"), EditAction.Set, new ParameterValue.Decimal(3)),
            new ParameterEdit(FixtureInputs.Key("high"), EditAction.Set, new ParameterValue.Decimal(4)),
            new ParameterEdit(FixtureInputs.Key("ratio"), EditAction.Set, new ParameterValue.Ratio(.72m))
        } : new[] {
            new ParameterEdit(FixtureInputs.Key("enabled"), EditAction.Set, new ParameterValue.Bool(true)),
            new ParameterEdit(FixtureInputs.Key("duration"), EditAction.Set, new ParameterValue.DurationMicroseconds(3000)),
            new ParameterEdit(FixtureInputs.Key("length"), EditAction.Set, new ParameterValue.LengthMillimetres(3)),
            new ParameterEdit(FixtureInputs.Key("mode"), EditAction.Set, new ParameterValue.Enum("run"))
        };
        var batch = new EditBatch(g, edits, BatchMode.Atomic, EditOrigin.User);
        Need(s.CheckEdits(batch)); Need(s.SetValues(batch));
        Need(s.Undo(Need(s.Read()).Draft.Generation));
        Need(s.Redo(Need(s.Read()).Draft.Generation));
        if (slot.Recommendation is not null) {
            var request = new RecommendationRequest(new OperationId(Guid.NewGuid()),
                Need(s.Read()).Draft.Generation, input.Profile, input.Evidence, 1,
                input.Options.OperationPolicy.OperationTimeout);
            var task = s.RecommendAsync(request, ct).AsTask(); slot.OriginalCallTask = task;
            var op = await Released(slot, await task);
            Need(s.AcceptSuggestion(op.Context.OperationId, "candidate-1", Need(s.Read()).Draft.Generation));
        }
        var valid = Need(s.Validate(ValidationMode.Full));
        if (!valid.IsValid) throw new InvalidOperationException("full validation failed");
        if (slot.Preview is not null) {
            var request = new PreviewRequest(new OperationId(Guid.NewGuid()), valid.Generation,
                input.Profile, input.Evidence, input.Options.OperationPolicy.OperationTimeout);
            var task = s.PreviewAsync(request, ct).AsTask(); slot.OriginalCallTask = task;
            await Released(slot, await task); // 未 Released 不允许下接 Apply。
        }
        var patch = Need(s.CreatePatch(new PatchOptions(valid.Generation,
            new OperationId(Guid.NewGuid()), Guid.NewGuid().ToString("D"), input.Name + "-fixture")));
        slot.OriginalPatch = patch; slot.Apply.RetainOriginal(patch);
        // 测试入口显式授权应用到夹具 Owner；生产入口必须来自操作者明确命令。
        var applyTask = s.RequestApplyAsync(new ApplyIntentRequest(
            patch, input.Options.OperationPolicy.OperationTimeout), ct).AsTask();
        slot.OriginalCallTask = applyTask;
        var applyOp = Need(await applyTask);
        slot.OriginalContext = applyOp.Context;
        if (applyOp.Phase != OperationPhase.ResourcesReleased) {
            var drain = await s.DrainAsync(input.Options.OperationPolicy.CloseTimeout, CancellationToken.None);
            if (drain.State != DrainState.Released) throw new InvalidOperationException("PE-4002");
            applyOp = Need(s.GetOperation(patch.OperationId));
        }
        var receipt = applyOp.Apply;
        if (receipt is null || receipt.State is ApplyState.Pending or ApplyState.Unknown) {
            var queryTask = s.ResolveApplyAsync(patch, input.Options.OperationPolicy.OperationTimeout, ct).AsTask();
            slot.OriginalCallTask = queryTask; receipt = Need(await queryTask);
        }
        if (receipt.State != ApplyState.Applied) throw new InvalidOperationException("apply:" + receipt.State);
        Need(s.AdoptAppliedBaseline(receipt, Need(s.Read()).Draft.Generation));
        if (Need(s.Read()).IsDirty) throw new InvalidOperationException("baseline not adopted");
    }
}
~~~

### 12.1 失败、有限收尾与迟到接续

固定 FixtureApply 只返回本夹具构造的有限不可变前像/回执，RecoverAsync 的编码核对不是不可信远端数据入口。真实冷恢复 Adapter 在返回前必须按 §2/3.4 的同十五项预算有限预检/深冻结，Root 再核完整结果限额及原 Patch 身份才编码/披露；没有该预算 binding 就拒冷查询，不先下载/复制超大回执。Root 的错误记录只保有限唯一代码/短原因，超出 MaxTextChars/MaxOperationRecords 设置 DiagnosticOverflow 且首轮非零；不存原参数或堆栈，也不无限累积同一 timeout。FixtureAccess.Grant 是测试显式重新授权，不复活旧 invalidation token；实际身份策略由宿主批准来源提供。

ProcessRoot 是进程级实例，由启动 Host 强持，不是静态全局；Retained 仅返回槽快照，没有 Clear。Root 同时绑定每槽的 session、端口、权限、Observer、原业务/调用/cleanup Task 和完整 Patch。观察到期/方法返回不移除槽；HostReport 的 BusinessErrors/CleanupErrors 两轴分别保留，cleanup 异常不覆盖首个业务异常。一次 Root Cleanup 观察最多 CloseTimeout；保留尚未结束的 CleanupTask，再次 Cleanup 只观察它，只有此前已结束的失败/Unknown 清理才能重试。真实 Task/所有 lease/Observer 已退出、Released ACK、无未决外部写和清理错误解决后才可移交/解除强持。示例中的错误列表故意使首轮验证非零；生产恢复需保留原错误记录并核本次 ACK，不能通过清空错误伪造首轮成功。

Root.Retained 非空时外层进程服务继续持 Root 和原端口，停止新准入；用户看到“等待作业结束”及“查询结果”，不能 Environment.Exit 或用方法离栈声称释放。一个根槽最多一个活动 CleanupTask，每个 session 预算各自限制，根容量2是双Host测试值。上级接管须先在其有界槽登记完整 Slot/Task/端口/原请求并返回接受 ACK，原 Root 收到 ACK 才解除本地持有；超限/拒收继续原 Owner，不把裸 session 丢到无界袋。实际超进程崩溃由外部 Owner 持久原请求和租约恢复机制处理，不声称本例内存可跨重启。

迟到恢复分三种：① Preview/Recommendation 原 Task/Drain 真完成后读原 OperationView，保持原 StopReason/HistoryOnly，不能采用陈旧候选；② 已关闭 session 的 Unknown Apply 只用 Slot.OriginalPatch/Apply.QueryAsync 和原 OperationContext 关联、新 Query 权/有限截止，保该 Task，并对同 OperationId 独立 Drain；Pending/NotFound/Denied 保槽，不重发；Applied/Rejected/完整 Partial 的外部回执先核 §8.4，再将真实新基线交新 Host，不能在 Closed session Adopt；③ Observer 晚退出仅归还执行槽，不重放事件/业务。迟到观察和重试都用独立有限 cleanup，不复用已取消业务 token。

为测试失败链，端口夹具的故障版本必须在同 Core.Tests 中按以下算法实现（不是隐藏产品 API）：按 OperationId 建有界 entry（原 Task、子/父 lease、停止位、TCS 闩锁），Execute/Recommend/Apply 只接纳一次；准备后抛错保 entry；Drain 分别尝试独立子清理，等待测试显式释放闩锁，再释放父并返回两个 true；第一次清理失败保 entry，第二次只重试已结束失败项；故意忽略 cancel 的 Execute 不在 Drain ACK 前标 stopped。Apply 故障模拟先持原请求→CAS 写 fixture baseline→丢响应，Query 返回同 hash 原回执。阻塞 Observer 用可释放闩锁，无回调退出就无 Closed。测试闩锁本身由进程 Root 强持，每用例独立有限观察，到期非零且保未结束 Task；不用 sleep/强杀证明软件排空。

### 12.2 Core Exe 执行约定与非零规则

Core.Tests 冻结为 Microsoft.NET.Sdk、net10.0、OutputType=Exe，只引用 Core 与 BCL，不引入待选测试包；§14 具名组为入口分派的用例 ID，而非 xUnit 属性。以后获准创建工程后从仓库根执行：

~~~powershell
dotnet build src/Modules/parameter-editor/Asun.Modules.ParameterEditor.Core/Asun.Modules.ParameterEditor.Core.csproj -c Release
dotnet run --project tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Core.Tests/Asun.Modules.ParameterEditor.Core.Tests.csproj -c Release
~~~

入口建立有界 ProcessRoot，运行两个 Host 和 §14 全部 Core 断言。每一用例有显式有限截止及可控闩锁；任一失败、未完成、Required 跳过、Retained 非空、cleanup 错误或真实排空未知返回非零并输出用例 ID/业务轴/清理轴。全部断言完成、所有槽收到真实 ACK 才0；使用命令行过滤的局部验证只报告对应范围，不能冒称全套通过。外层监督进程另用已采纳测试 Profile 的有限进程截止；被终止/超时非零，不能记录为资源已释放。dotnet test 不执行此 Exe，不作为 Core 验证。真实 WPF 专项 Host 在 Wpf.Tests 中沿 §11/14 的固定视口执行，其命令和门见 §14；本轮没有创建或运行以上工程。

## 13. 逐能力反例视角：结果、参数与边界

| 能力/输入 | 处理和期望 | 可判定断言 |
|---|---|---|
| 空Schema / Missing / Null / 空Text | 空Schema Empty；Missing Required失败；Required+Nullable显式Null合法；Text按最小长度 | 不从0推默认，不创建空Patch或启动端口 |
| 十字段正常修改与无编辑Validate | 初始Ready可Full Validate；改Ratio一次generation/Undo | View/CheckEdits不改草稿；无伪Dirty才能试算的前置 |
| decimal/整数/单位边界 | 0.72↔72%；1000us↔1ms；long溢出/超2^53经文本；开闭边界/非格点 | 规范值/hash不受显示舍入/culture影响；不经double |
| low/high同时改 | Atomic对完整候选验关联；独立partial对耦合字段拒绝 | 合法成对修改可接受，非法任一项草稿/栈全不变 |
| 动态关联、未知父项、成环 | 创建拒循环/悬空；运行Missing比较Unknown显示阻断 | 不暗藏/删参数，不执行脚本或替用户放宽规则 |
| 退役enum、无Default、ReadOnly | 可读旧enum告警；新写/Reset拒绝；专家不加权 | UI/API同错误；默认与上一次值分开 |
| 大规模及文本恶意 | 预算内按完整集校验；超边界拒绝；regex超时/非法Unicode拒绝 | 不截断假有效、不无界通知/历史、不阻塞UI线程 |
| 噪声/弱信号/遮挡/退化/空ROI | 外部Adapter返回Invalid/NotObservable/Rejected及原证据 | 不补数值、不重跑降阈值、不把空分割/NoRead当PASS |
| 多候选推荐/匹配 | 推荐保存全部候选、明确ID采用；匹配Ambiguous显示 | 不取首项/最大score作最终判定；Abstained保原值 |
| 参数改动/输入或Profile变动 | generation或引用改变使原结果HistoryOnly | 旧建议不可采用；同hash不同代次也不能复用为当前 |
| Undo/Redo/Discard/Reset | 精确before/after/Origin，当前权限及完整目标校验 | 草稿回退不影响Owner事实；一次批改一次Undo |
| CAS冲突/迁移 | 明确三方选择，Schema变更走纯计划 | 失败保原基线/草稿；不能用latest重投原键 |

数值例均为测试夹具。Core对信号/遮挡/ROI只消费公开状态，不据模拟输入“测出算法正确”；视觉Golden与物理质量由算法Owner验收。

## 13A. 生命周期与外部接入反例视角

| 外部实现者场景 | 保留/处理/安全恢复 | 验收断言 |
|---|---|---|
| 两session交错编辑/同session双写 | 复制冻结；ExpectedGeneration只接纳一项 | 不串值/CTS/文化，另一命令PE-2001 |
| 排队到截止/取消未派发 | 取消队列项、未调端口、Released后终态 | Execute计数0；队列时间属于总预算 |
| 在途取消/迟到/native未退出 | StopRequested→DrainUnknown，保Task/输入/Owner | 无提前Outcome/Closed/归还；迟到只原记录 |
| 准备失败+释放失败 | Drain可达未交回Owner，保持执行名额 | 第二Execute为0；重复Drain可释放，子先父后 |
| Apply断连/丢响应/错误回执 | 原请求已由Owner保存，Unknown写门 | 只Query原正文，NotFound不授权重发 |
| Close/Dispose期限/取消 | 本次等待可结束但工作继续受管；同session再Drain | 未退出回调不能归零；Dispose失败保引用 |
| 观察者异常/慢/队列满 | 隔离投影订阅；业务记录可读；真实回调排空 | 不回滚正式编辑，不无界缓存；关闭可Unknown |
| 已卸载UI再Attach/三语/IME | 原session、当前Read；旧截止不重放Open | 草稿/栈/操作不变，输入buffer文化不被重解 |
| Checkpoint坏hash/栈分叉/重复重开 | 从完整来源和栈链核验，拒歧义保原件 | 不猜Undo顺序、不恢复授权、不自动重跑 |
| Rebase缺选择/任一校验失败 | 不改before/draft/栈；成功一次更新并清旧栈 | 当前权限/Unknown写门不绕过，完整失败原子 |
| 升级/降级/canonical改变 | 不重hash旧源，未知版本拒；排空后替换DLL | 不撤外部事实、不导入未知生产字段 |
| 第二消费者缺推荐/视觉设备 | 对应按钮明确不可用，其余Core完整 | 不要求隐藏窗/产品Shell；不为填接口编造图像 |

### 13A.1 不支持的隐式能力

不自动反射配置为Schema、不执行任意表达式、不猜单位/阈值/权限、不用UI虚拟化缩减校验、不无条件“恰好一次”远端写入、不强杀native、不把单个资源计数0当系统归零、不从建议/工程结果生成质量决定。外部客户物理阈值只阻断相应Profile/设备动作，不阻断纯Core、无UIHost和端口模拟。

## 14. 测试落点与可执行验收

以下是后续实现需真实落到既定工程的测试职责，不是本轮创建的测试文件或运行结果：

| 唯一工程中的具名测试组 | 输入/风险 | 必须断言 |
|---|---|---|
| Core.Tests / SchemaAndCanonicalTests | 全类型、min=max开界、default非法、未知枚举、TLV/Unicode、hash错绑 | 拒绝发生在session/派发前；Golden精确字节；输入改集合不改变已冻结记录 |
| Core.Tests / TextAndUnitTests | long全域、decimal尾零、三文化、%/us/ms/µm、regex预算 | 同规范值同hash；解析显式culture/unit；非法token不填0 |
| Core.Tests / DependencyAndBatchTests | low/high、Unknown、显隐图环、5项2拒、partial耦合、Undo容量 | Atomic全不变或一次generation/Undo；partial不破关联；重复key/空集合拒 |
| Core.Tests / RebaseAndCheckpointTests | Base7→Current8、同版本异hash、冲突漏选、历史分叉、Null/Default | Full校验和原子替换；坏栈/来源拒；恢复后不重跑、不授权 |
| Core.Tests / SuggestionAndPreviewTests | 弱信号、多候选、Abstained、旧代次/同hash、错结果 | 原值/拒识保留、显式ID采用、无自动Apply；超限不裁失败项 |
| Core.Tests / OperationAndDrainTests | 队列满、截止、准备失败、释放失败、迟到、观察者异常/堵塞 | 真实Task结束+Drain才Outcome，Sequence/epoch/record正确，Owner不丢 |
| Core.Tests / ApplyRecoveryTests | CAS、response lost、Unknown/Pending/Partial、同key异正文、Query撤权 | Apply调用至多一次；Query不Apply；坏回执不Adopt；Unknown禁写 |
| Core.Tests / HeadlessEditorHostTests | 独立算法/设备夹具、缺可选端口、session并发、关闭 | 单独构建、不引用Shell/UI/SDK；全部Core能力无窗口 |
| Core.Tests / RootRecoveryAndLimitsTests | Factory前槽满、业务异常+cleanup异常、原查询迟到、订阅堵塞、结果/历史B与B+1 | 超限未派发/未复制；原Task与Owner在观察到期后可达；同operation cleanup/query不重叠；真实ACK前槽不回收；双轴非零 |
| Wpf.Tests / InspectorWorkflowTests | PropertyGrid、matrix、paste/IME、三语、长期附着 | Core/API相同错误，编辑确认恰一次、动态Null不抛、Key稳定 |
| Wpf.Tests / InspectorPresentationTests | 1920×1080固定视口、宿主图像/无图像、最长文本、Dock/主题/SuperTip/UIA | 实际客户区比例/焦点/工具提示可读；视觉与可用性分别记录 |
| Wpf.Tests / InspectorRootAndStaHostTests | §11.5两根/预算/原Task、§11.6两个完整STA Host、权限改变/转交 | Reserve先于factory；同期命令/呈现拒重叠；ACK前不丢payload；双错误轴；同Binding/Slot的迟到只更新原记录；两个Host无隐藏初始化 |

U1 --verify 的实施用例序列冻结如下，每项每Host用一个有限Profile截止，闩锁由进程测试Owner强持、主动释放而非sleep：

| 用例ID | 具体公开输入与步骤 | 唯一断言/恢复 |
|---|---|---|
| U1-STA-01 | §11.6 algorithm构造全十字段、两个Core端口、Binding+Actions；Validate/原子low/high批改/Undo/Redo→显式建议ID→试算原operation | PropertyGrid/Matrix/Diff/问题定位同Core；候选采用后再验证，preview原Item/chart选中联动；没有自动Apply |
| U1-STA-02 | device构造Duration/Length/Bool/Enum及无推荐/preview声明；矩阵批改→Validate→明确Apply→持久原请求fixtureACK→原回执 | 禁未连接动作，其余仍可用；Duration精确us/ms、Length精确mm/µm；Owner结果/请求值/实际回读不合成一态 |
| U1-LANG-03 | 两Host在zh-CN输入token/IME组合；并发Presentation原Task→zh-TW/en-US再改；未结束时第二呈现 | 单槽拒叠加；资源/标题/菜单/SuperTip状态更新，当前键盘focus/IME/token及解析culture仍原绑定；不改Corehash/undo/epoch |
| U1-ACCESS-04 | FixtureAccess.Revoke→RefreshAccessAsync；CurrentRead/Edit/Accept/Apply；之后旧token仍Cancelled，再Grant+Refresh | 无读权清原值/候选/详情；权限拒不派发，不把灰按钮当保护；恢复使用新决策，不重Bind/重放旧操作 |
| U1-ROOT-05 | Root(1槽,12Task,2MiB,32错误,3s观察,2s清理)先Reserve，第二Reserve；结果/缓冲字节B和B+1；堵Presentation回调 | 超限start/factory调用数0；原Task保同Root，投影等待到期不释放槽；真实回调退出才ACK，不裁完整字段假成功 |
| U1-STOP-06 | Bind准备后失败；业务错误+独立Detach清理失败；同slot Unbind到期；晚退出原Task→重复Unbind | 业务/清理两轴各保；未结束只观察原Task，失败已结束才幂等重试；UI真退出/OwnerACK前CoreRoot不Close；真实成功归还不清首轮失败 |
| U1-ACK-07 | SessionOwner.AcceptAsync门控，首轮超时；同BindingId收到晚ACK；wrongSession/Owner/AckError | 无真接受不归还；拒/错误继续原Root；真实ACK不Close外部session，仅把后续责任归CoreOwner；下一窗口不获旧授权 |
| U1-TRANSFER-08 | 槽Retained→PrepareTransfer→接收根满拒→Reject；释放空位后精确Accept+Commit，另提交错RootId/旧revision/重复ACK | 接收确认前源仍强持；错ACK不Commit；正确后唯一执行根；同原Control/Task不重Bind/Apply；源墓碑被淘汰不影响接收根恢复 |
| U1-LATE-09 | UI RetainApply已ACK→原Apply取消/丢响应→Unbind，CoreRoot仍原Patch/context/ports；关闭session后只Query→晚Applied | 未resolved保持Core根；Query不Apply，UiACK不证明远端无写；原回执只归原operation，不给新Binding套旧值 |
| U1-DPI-10 | 一个固定1920×1080物理viewport扣taskbar/边框/title/status；原系统DPI换算、长英文/三語及键盘/UIA | 量客户区/图像/Inspector比例，精美布局和可用性分别判；稳定prefix/key/operation，无额外分辨率矩阵、不改系统显示 |

未来测试 --verify 分派先构造独立STA/Dispatcher和与两个Host相同的公开输入/根，按上表驱动Core/Control方法及真实UIA；用例完成后必跑Unbind/CoreRoot cleanup并核全部原Task/ACK。测试方法返回双轴结果+用例ID，不直接在try中return成功覆盖finally；最终入口汇总所有必需组并按§12.2非零规则返回。表中FixtureApply真实持久/HIL不适用，fixture本身软件契约仍需执行。编写这些确定断言是实现工作，不以现场门替代任一内部用例。

Core 的精确 BCL Exe 命令及非零规则见 §12.2，不再使用 dotnet test。Wpf.Tests 为 net10.0-windows / OutputType=Exe / UseWPF，引用 Wpf/Core 和本机既定 DevExpress；入口以 STA+真实 WPF Dispatcher 打开一个固定1920×1080验证视口（计入任务栏/边框/标题/状态栏），只在获准 UI 切片执行：`dotnet build tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Wpf.Tests/Asun.Modules.ParameterEditor.Wpf.Tests.csproj -c Release`（传递构建Wpf/Core及测试），再 `dotnet run --project tests/Modules/parameter-editor/Asun.Modules.ParameterEditor.Wpf.Tests/Asun.Modules.ParameterEditor.Wpf.Tests.csproj -c Release -- --verify`。§11.6两个 --host 消费入口不代替此断言入口。任一要求未执行/未完成/失败、Dispatcher或Binding根槽未排空均非零；不能让无桌面环境跳过后返回0。Core 或 HTML 原型不代验 WPF。完整模块交付还须两个真实消费者及发布/迁移/回退；不以首片纯Core通过删除推荐、查询、UI和完整批改职责。

以下断言为前述组的必需项，入口不能把它们标 optional 跳过：正常批改 low=3/high=4 从旧1/2一次成功；只改low=3原子失败保持原hash/代次/Undo；显隐互引/自引拒 Create，跨约束互比不伪作环；Missing/Null/空Text/Default四态完整 before/after 与 Undo/Redo；Base revision7→Current8 三方同值/单方/双改冲突逐key，漏选择/同revision异hash全不变；改权限后 Set/Undo/Accept/Apply 均核当前权且未派发，撤权 token 保原Task直至释放；推荐在同hash不同代次、证据/Schema来源变更后 PE-3102，不能 UI 暗绑原候选。两个全构造Host、完整 §3.5 Golden 和 Root 双轴故障/迟到恢复分别执行，不用同一对象 hash 自比代替独立 expected。精确 long 超2^53 的编辑/格式/PropertyGrid 往返不能变值。

0.2.3-prep的定向断言落到上述现有组，不另建同义测试工程或向量协议：

| 既有测试组 | 精确输入与步骤 | 必须断言 |
|---|---|---|
| TextAndUnitTests / SchemaAndCanonicalTests | §3.2.1不可表示token、decimal.MaxValue的Percent/µm格式往返；Int64值long.MinValue、Step=1、Origin=long.MaxValue；Host的MaxTextChars和Inspector根缓冲预算各B与B+1 | token不舍入成0.7；可表示投影准确往返；极限差用精确余数合法；超消费预算PE-4003、不提交；纯codec/Inspector不虚构session.Options；业务无效但结构合法候选仍可编码定位；已有canonical Golden不变 |
| DependencyAndBatchTests | low/high旧1/2，CheckEdits Atomic仅low=3，再SetValues同集合；初始Required Missing且Draft=Baseline时ChangedOnly→Full；合法Reset/伪造Default Origin/retired枚举 | 演练成功但完整无效候选带Error、ApplicableKeys空；提交拒且原hash/代次/历史不变；空ChangedOnly不清Full错误、不供Apply；Default仅等领域合法默认，retired只保旧不新写 |
| RebaseAndCheckpointTests | 真实Plan后改Local/Before/冲突前像或增加/遗漏/重复选择；合法无冲突Current较新 | 篡改全部拒且不替换草稿/基线；有效无冲突显式Rebase一次更代并清历史，来源/权限仍核当前 |
| SuggestionAndPreviewTests | 推荐原冻结low/high=1/2，等待时当前合法编辑为5/6；原候选low=1.5，再返回；Source失效token取消但hash未变；请求最多1候选却响应2候选/空Edits | 原候选按1/2完整校验保历史，不能误按5/6拒合法响应，也不能采用到新代；失效来源不派发/不采用，不从hash猜新来源；超限/空编辑完整拒响应，不裁候选；AutoPreview仅确认提交后派发 |
| OperationAndDrainTests | 原Preview/Recommend被接纳后编辑Draft，再用同ID同原请求调用；同ID改Profile/Timeout或其它正文；Apply换ID复用原幂等key | 用原冻结Schema/Snapshot算同请求身份并返回原记录，端口调用数不增加；异正文或新ID复key PE-2005；不增epoch/排队，当前披露权限仍核 |
| ApplyRecoveryTests | Partial含Pending→查询所有项Applied/Rejected且完整实际After；已确认Applied/Rejected后晚到Unknown/NotFound，另给冲突终结回执 | 未决时禁写；终结Partial只显式重基真实After、不Adopt全成功/自动重发；晚未决不降级确认事实；冲突PE-9004并保确认事实/诊断，不假释放未知写 |
| InspectorWorkflowTests / InspectorPresentationTests | 逐项呈现§7.1全部38个Code、13个RecoveryKey、八态及§11全部命令/单位；zh-CN→zh-TW→en-US，宿主返回短回退/缺外部资源，撤View权 | 内置三语完整且不被Host回退覆盖，外部缺资源短回退并诊断；没有原值/堆栈/主提示资源键泄漏；IME/解析绑定不变；无权不披露原载荷 |

这些是后续实现验收断言。本轮正文及定向静态检查不表示上述测试、C#构建或真实WPF已经执行；不得用待定物理阈值跳过内部软件反例。

取消/并发测试用可控制屏障/显式触发释放，不靠sleep假定结束；FakeTimeProvider只验证deadline机制，真实线程/native排空另验。性能测试按§15受批准Profile执行，数据/机器/驱动/HALCON及控件版本固定。无批准Profile为NotEvaluated；Mock不证明客户/生产质量。

## 15. 性能计划、资源计账与诊断

目标全部 `TargetPending`；统计口径直接使用DEV-GOV-010 §3.1，不在模块再发明分位算法。每Profile显式提供输入Schema/hash、机器/runtime、工作负载/并发、冷/热和预热、测量次数/有效样本、deadline、各资源上限、时延/资源失败阈值来源；未采纳只能诊断测量 `NotEvaluated`。测点从接纳到ResourcesReleased，另量取消至真排空，失败/超时/删失/无效不静默删除。

| 模块负载维度 | 测点 | 有界失败与资源 |
|---|---|---|
| 参数数/类型/文本/AST数深/关联扇出 | Create、Parse、Full/ChangedOnly、字段状态重算 | SchemaBytes、AST节点/深度、PE-4003 |
| 一项/大批/耦合批、相同值、Undo/Redo深度 | CheckEdits、提交、diff、Undo/Redo、TLV/hash | SnapshotBytes、HistoryBytes、Undo条数，禁止默删历史 |
| 多session、preview/recommend混合、取消比例 | 队列等待、派发、result冻结、取消/排空尾部 | 有界队列、operation records、native借用分开，PE-4001 |
| Apply/Query断连、回执大小、未决持续 | 本地接纳/Port等待/Query/资源归还 | 远端事务耗时另Owner计账，不由Unknown算通过 |
| 动态类别/长文本/语言/IME/paste/切选 | 首次可用、键盘反馈、行创建、投影发布、UI线程占用 | 当前类别描述器/虚拟化/Chart点数受Profile，不猜fps |
| 开关控件/两消费者/恢复/坏载荷 | 订阅数、迟到丢弃、释放失败Owner、内存斜率 | 稳态和峰值；长稳时长/循环数由Profile而非来源固定 |

测试负载至少含预算B内、恰B、B+1，浅宽/深窄AST、密集关联、大批原子失败、多候选、通知堵塞、释放一次失败和两session。B来自测试/消费者Profile，不把10k字段/1000开关/72h当生产默认；Scale改变时记录实际完整输入，不能减少参数/候选凑时延。

每session/operation诊断：trace/session/operation、generation/epoch/recordVersion、Schema/Provider/Adapter版本hash、Snapshot/Request hash、queue depth、阶段、StopReason/Outcome、原Apply外部状态、解析/校验/派发/排空时间、Managed/Native/lease/notification/history字节及观测是否存在。不记敏感原值；错误映射资源键/恢复键，详细堆栈仅诊断。预算、实际观测和真实释放证据分列，Core自身0不代表Adapter或全系统0。复用宿主diagnostics端口的消费适配，不引入日志私表或全局logger作为Core必需初始化。

测点闭合：t0=接纳并登记原请求；t1=完整预算计数/冻结/hash结束；t2=校验/依赖/diff结束；t3=排队出队；t4=端口原Task开始/实际退出（分别记录）；t5=收到完整响应并核验冻结；t6=各子lease/父lease的真ACK；t7=所有通知worker及最后关闭屏障退出；ResourcesReleased 取相关原Task/查询/借用最后实际结束，不能拿等待deadline/零计数/响应到达代替。端到端以 t0→ResourcesReleased，Root 冷查询另记录新查询有限等待与原operation外部解析完成，不续原 t0。UI记录编辑确认→Core提交→Dispatcher发布→首次可用，另量取消→真实Drain及Detach→Dispatcher/Binding根ACK。推荐保留字节、响应预留、Observer执行/队列、原Query/cleanup Task数和根槽占用均记录峰值/稳态；某观察缺失记未测而非0。§3.5字节核对不属于性能样本。

## 16. 两个真实消费者与独立发布接入

### 16.1 独立离线算法工具

真实接入职责：Host读算法Owner Schema、精确配置基线/模型/样本；factory Create → 类型化编辑 → Validate/diff → 有输入时Preview → 有方法时Recommend → 明确ID采用 → Full验证 → Patch/Apply至算法配置Owner → Query/Adopt。preview消费segmentation/alignment/barcode等所属公开模块，Native由该Adapter保管。Core不能知板/缺陷/Recipe类型，工具可单独引用DLL启动；缺相机不妨碍离线真实样本，缺样本只隔离Preview不编造图。

验收使用至少Ratio+Int64/Pixel+Enum，复核低对比/空ROI、多候选、撤权/迟到、两次改参及CAS冲突；Schema范围和真实性能由算法Profile提供。通过合同和软件夹具不算真实算法精度门关闭。

### 16.2 独立设备参数工具

Host从设备能力的公开Adapter读声明与当前回读（请求/实际/不支持分列），提供Duration、Length、Bool、Enum Schema和具体ApplyMode；端口在设备安全Owner验证停机/互锁/权限后执行CAS及回读。Core校验不证明设备可达，不直接发灯光/运动/PLC。设备ACK/Applied/ReadBack分别由原Owner证据表达；无法确认时Unknown、只Query。推荐Provider可缺省，不能做未授权设备扫描或设置优化。

软件验收可用正式设备协议Simulator，实际SDK/HIL仅阻断该集成切片。工具关闭/重开仍能根据Owner原请求查询，不靠原窗口留全局句柄。设备Schema、资源预算、语言与算法Host同时不同，互不串状态；移除任一消费者引用仍能单独build Core/WPF。

两个真实Host分别由消费者Owner装配，不能由本模块临时创建产品页面；本轮仅冻结接入责任和无UI测试Host，尚未有真实接线/生产回读结果。独立交付需目标项目逐项证明同一Core程序集、不修改Core来塞领域逻辑、故障恢复、资源排空和回退；门见§18。

### 16.3 已消费 configuration U1 的精确影响（2026-10-10）

本轮保留 configuration 已消费的 Create/Restore、Read/Validate/CheckEdits/SetValue/SetValues、PlanRebase/Rebase 和 Attach/SetPresentationAsync/DetachAsync 签名，十五项 Budget 名称/顺序不变；WPF CommandBinding 是加法成员，既有仅编辑接线不用提供。Schema 的 hash 身份明确为 §3.4/3.5，本轮消除重复包裹歧义，不存在已实现二进制迁移。

历史定位：configuration 0.3.1-prep §10.3.1/DeviceVersionHost 曾把Int32/ms映为PE.Int64/Millisecond、Decimal/mm/um/deg映为PE.Decimal/物理单位，均违反本页原单位表并应PE-1007拒绝；当时Decimal合法组合为None/Decibel，后续§3.2.1仅加Pixel，没有放开物理单位。该桥接问题已由configuration原Owner在0.3.2-prep修正并获限定内容接收；当前[configuration指导](../configuration/DEVELOPMENT-GUIDE.md)为0.3.4-prep，完整范围结论见其§19.1，不能继续列为待退修项。

当前桥契约保持：Owner确认时间语义的Int32/ms使用DurationMicroseconds（checked ×1000，反向整除并核原类型范围）；Decimal/mm、um使用LengthMillimetres（mm直映、um精确÷1000），deg使用AngleDegrees；现值、Default、范围、Step及StepOrigin同步无损转换。量纲未知、溢出、不可准确表示或无法保持原整数格点则原字段只读，不做编辑替身。configuration保存回执不冒PE.ApplyReceipt，其正式Schema/来源/当前授权及真实STA接线仍由configuration/消费者Owner实施和验证。本轮只更新本页状态和消费边界，不改对方文件、不重审其Core或Golden；全部既有PE签名、十五项Budget及旧规范编码保持。

## 17. 外部资料与本次边界核对

- `PKG-051_ParameterEditor.md`：确定职责、规划消费者、无 UI 核心、快速拖参迟到隔离和双消费者验收。
- `INDEPENDENT-MODULE-ARCHITECTURE.md`：确定 IM-062、独立发布/测试、Core/WPF/Adapter 边界及禁止制程语义。
- `PKG-002_Configuration.md`：确定参数编辑器承载 UI，配置 Owner 承载定义、CAS、迁移和持久事实。
- `DEV-UI-040`、`DEV-UI-043`：确定 WPF/DevExpress 工作台、八态、差异/验证/发布分离、语言和 UIA 要求。
- `DEV-GOV-005`、`DEV-GOV-010`、`DEV-CONTRACT-002`：确定单一权威、状态/Owner/Schema 分离、取消排空、未知回执和实施级规格要求。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_Aligment2D_NCCModel\NccModelParameters.cs`、`Vision_CameraCalib\CalibrationParameters.cs`、`ROI\ShapePropertyForm.cs`：只读借鉴。其默认值/校验/INI/WinForms 事件混合方式可作为迁移输入，但不能原样成为本模块契约；特别是 `catch -> null`、文件路径直读、字符串化参数和 UI 直接修改对象均不满足本指导的失败可见、资源和 Owner 规则。
- `halcon算子手册\operators` 与 AsunImage `ImageLibDotNet` 公共边界：本模块无视觉算法路径，核对结论为不适用；需要视觉试算时由算法/视觉 Adapter 按 HALCON 26.05 公开资料另行冻结，不能在这里猜测签名或引用内部实现。

### 17.1 AOI.Main 统一参数中心与原子 Recipe 发布

只读复核 [检测参数生产集成指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-08-07-inspection-parameter-production-integration-design.md) 后，参数编辑器的宿主接入必须满足：

- 统一参数中心只消费各领域提供的参数定义/描述器；控件不直接写生产文件、算法实例或设备当前值。
- 草稿使用不可变快照；编辑、验证、保存草稿、发布和激活是不同操作。发布前完成身份、单位、范围、引用资产和跨字段约束检查。
- 规范序列化、SHA-256、临时文件写入、耐久化刷新、原子替换和回读核对必须形成完整回执；任何一步失败都保持原活动版本，不能把半文件标成发布成功。
- 并发发布按参数身份/CAS 串行化；检测请求冻结创建时的快照，后续 UI 修改只能影响下一次请求。草稿、已发布版本、设备 ACK 和质量放行不能合并为一个 `Success`。
- 导入、导出、校验、发布失败保留原始错误和损坏载荷供诊断；关闭/取消释放文件流、锁和事件订阅。

AOI 的模块名称、客户字段、配方目录和生产放行条件不进入 Core；条款只补强 `parameter-editor` 与配置/配方 Owner 的交接契约。

### 17.2 H:\docs 当前参数编辑器指导的职责内增量（2026-10-06）

只读来源：`H:\docs\40-development\41-vision-platform\05-engineering\视觉参数编辑器与算法试验台开发指导.md`；SHA-256：`14ed3fa9ac9737d2322ddc662efbf80f19f17ec3f9287a48b4630424862bddb3`。与[现有来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)的当前原件一致；2026-10-04 选定快照 hash 不同，不能用旧审查替代当前比较。本次只比较参数编辑职责，不接收来源的实现、测试或生产验收结论。

| 原件定位 | 可执行增量与正文落点 | 不迁入的范围 |
|---|---|---|
| §9.10.3 批量修改 | §5：冻结精确字段集、预览对账、原子修改一次 Undo/Redo；§14：拒绝后草稿和历史不变 | 多对象/共享库事务、样本真值、独立质量评价与产品发布 |
| §9.3.1、2026-09-28“编译准备失败的释放恢复” | §9：交回前失败仍保留 Owner、子先父后、原 Drain 可达恢复；§14：组合失败反例 | Program 编译、来源授权 DTO、产品租约接口及 journal |
| 2026-09-30“已打开参数会话的界面重新附着” | §11.3：同一 session 重新注入，不重放创建或副作用；§14：旧截止与当前权限反例 | 来源的 Get/Open API、持久恢复和宿主选项类型 |
| ENG01-RESULT-PROJECTION-02、§9.10.1–2、2026-09-30“文件试检结果与操作员提示修正” | §11.3：执行/结论/有效性分列、缺失非零、原结果只读投影、读取失败清旧；§14：展示反例 | AOI 检测项/量测 DTO、板级覆盖、统计/判定推导和领域结果库 |

现有类型校验、不可变快照、CAS/Unknown 查询、迟到隔离、单位和三语规则已覆盖，不重复迁入。来源的 Released/Draft 双模式及 Recipe/NPI 双 Owner 提交、五路照明映射、ROI/步骤 Program、候选库存、采检编排、3D工作台和客户质量机制仍归宿主或相应独立模块；其任务、会话、允许写入路径和验收状态不成为本平台授权。来源的时延、容量及长稳数值不进入 Core 默认或已批准目标，§15 保持 `TargetPending`。本次没有采纳具体视觉算法或 HALCON API，HALCON 26.05 算子核对对此增量不适用。

### 17.3 本轮官方资料、源码与实质决策（2026-10-09）

本节为本页§2–16的研究依据，原件只读，不新建报告/清单或下载运行依赖。精确commit/hash用于追溯已读范围，不表示执行过上游测试、WPF或工业验证。

**动态PropertyGrid与UI公开面。** 会话工具未提供dxdocs或匹配DevExpress技能；联网访问25.2官网[PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)、PropertyDefinition及ValidateCell页返回403，因此采用本机随附官方XML的完整member说明作为25.2公开API依据，无反射内部/安装/兼容/授权审查：

| 官方XML位置（均在 `C:\Program Files\DevExpress 25.2\Components\Bin\NetCore`） | SHA-256 | 已读能力/正文落点 |
|---|---|---|
| DevExpress.Xpf.PropertyGrid.v25.2.xml | `0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9` | SelectedObject/Definitions/Path/Header/IsReadOnly/EditSettings/ValidateCell及args/ShowProperties等，§11.2 |
| DevExpress.Xpf.Core.v25.2.xml | `cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196` | Editors.Settings、Editors.Flyout.FlyoutControl、SuperTip、Bar.IsStatusBar、ThemeManager.SetThemeName，§11 |
| DevExpress.Xpf.Grid.v25.2.xml | `7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd` | GridControl、GridViewBase.ValidateCell、TreeListControl及选择，§11.2/14 |
| DevExpress.Xpf.Docking.v25.2.xml | `b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f` | DockLayoutManager/LayoutGroup/LayoutPanel，宿主拥有布局，§11.1 |
| DevExpress.Xpf.Charts.v25.2.xml | `2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0` | ChartControl仅原可比数值投影，§11.2/11.4 |

DevExpress官方示例[动态属性源码](https://github.com/DevExpress-Examples/out-of-maintenance-how-to-edit-dynamic-properties-in-the-propertygridcontrol-t159965/tree/82d1432d5adb1dc16a2d4ad8798e4f1e411eab5f)固定22.2.2+分支commit `82d1432d5adb1dc16a2d4ad8798e4f1e411eab5f`。实读CS/PropertyGridWithDictionary的DictionaryWrapper.cs（SHA `75f31be2724e1da188786c6004e99dd5e541c53712b7c77c08df8bf97fced3dd`）、CustomPropertyDescriptor.cs（`7ea911ea3baec7c98dda410055c61f881e33609b20a4a8a95452b49c488f28c7`）、MainWindow.xaml/.cs、两csproj、LICENSE；固定树未见行为测试。旧.NET4.5.2/net6.0-windows和DevExpress22.2浮动包不迁入；LICENSE为as-is并指向产品EULA，不能标MIT。仅借鉴ICustomTypeDescriptor动态桥，§11.2修正样例GetProperties忽略过滤、GetDefaultProperty空第0项、按当前Value.GetType、IsReadOnly=false、字典直写、只存_oldValue等缺口；不复制其草稿/撤销实现。当前out-of-maintenance分支commit `a466ae740dc2970d9d006853340058e1816e202a`仅README声明过时，不当作有源码或25.2兼容证明。

**校验/关联实现比较。** 固定[FluentValidation v12.0.0](https://github.com/FluentValidation/FluentValidation/tree/5365d9294812c8a5c5a7f4d7447c9a65b79a025b)，annotated tag `d9c37242df71249f93bb097dcb7693a31b4d82ad`解引用commit `5365d9294812c8a5c5a7f4d7447c9a65b79a025b`。实读Internal/PropertyRule.cs的条件/dependent执行/取消片段（SHA `090f574ee863e8b8ae7a43c1fc1a78bd5f6e005abaadf798cc3dac20e26d3df3`）、PredicateValidator.cs委托调用（`f9e09f6751a5ae33aed2133b0793856b86ae1464d18d092f77ed7889f62fd84e`）、AbstractValidator.cs同步/异步分离（`2fe2a2bc3633b22939dcc1bb03384021322674b24cdf72a5cdbd58db46e7cc27`）及ConditionTests.cs的链条件/同步调异步拒绝断言（`a4cec13d0683fd5b731c50e2a830fbeffc2b0dbd7b8a962647817fe1f27c81ed`），未执行其测试。csproj目标net8，SourceLink/Framework.ReferenceAssemblies/SyncMethodGenerator为构建依赖；License.txt为Apache-2.0（`6d1d968fb225eca367cb7f0b8831ab012a35d92b547e945e17ef8e7b05c3e5cc`）。不引入该运行库，不把任意delegate/ValidatorOptions.Global作为Schema事实或权限入口。

采用其条件限定、字段级问题、同步/异步分离的思想；领域Validator delegate虽易写但不可作为可序列化、可审计动态Schema的通用表达式，也不自动闭合显隐依赖图。§3.3冻结无脚本AST、三值逻辑、引用图和Full提交校验；§5冻结完整候选原子校验，不照搬级联Stop掩掉其余错误。此选择基于本模块动态Schema、确定性与无额外依赖需求，不声称自写校验性能优于FluentValidation。

.NET10官方[ICustomTypeDescriptor](https://learn.microsoft.com/en-us/dotnet/api/system.componentmodel.icustomtypedescriptor?view=net-10.0)实读GetProperties两重载和GetPropertyOwner，支持动态描述器职责而非业务持久；[Task.WaitAsync](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0)描述的是任务完成/等待取消/截止，不证明底层执行停止，§6/9据此分离等待与实际Drain。以上网络页面为读取时文档，不把网页更新日期当运行时补丁版本。

**HALCON职责核对。** 实读项目内26.05.0.0算子页的Description/Signature/参数与相关语义，未扫描AsunImage、未核验算子覆盖、未执行算法或选出最快路线：

| 本地算子页 | SHA-256 | 本模块采纳的消费约束 |
|---|---|---|
| [reduce_domain](../../../halcon算子手册/operators/reduce_domain.html) | `36db6809bb11f45ad9c373fa8dfd54fb1f62ac27aaa63ba7d46338189c064fa7` | 定义域交集不改图像矩阵大小，显示裁剪不伪作算法输入 |
| [dyn_threshold](../../../halcon算子手册/operators/dyn_threshold.html) | `29a9e074c8b9fe264cb43af46350a1e91249690716ec7eee519e7c8a54be1b47` | 需要原图/局部阈值图与Offset/LightDark，不能由参数名称猜对应域 |
| [threshold](../../../halcon算子手册/operators/threshold.html) | `64d24dd2344832561b1b1c6ccaf24a8c84ef030cbe64cce5509434479f05bbc3` | 灰度区间/tuple输出语义归算法Owner，不把空区域当通过 |
| [find_shape_model](../../../halcon算子手册/operators/find_shape_model.html) | `82e669bd937133fbfd9b4e337ac4cbeb25505bd0a6f331de8bfd2956879cdcb7` | 原模型、Score/NumMatches及候选是匹配事实，不能由UI变成概率/单一PASS |
| [find_bar_code](../../../halcon算子手册/operators/find_bar_code.html) | `57b1906b755bfc2354ebd55f09d0d3c80851e789a68ab7696af0da43fe3149ef` | 原句柄/码制、字符串与区域属读码Owner；多码/未读不猜身份 |

参数Core、TLV、依赖、回退、权限与批改为非视觉，不引入算子平行实现。上述资料只补§8.3的输入/结果边界；各视觉模块承担具体主备路线、参数与推荐方法、真实C#歧义、Golden及同样本性能门。本页不复制上游完整算法规格。

## 18. 逐切片六项准备结论与后续门

0.2.2-prep Decimal/Pixel增量已获主控限定内容接收，仅增加 §3.2.1 合法组合及其反例；该增量的边界/真实消费者、公开兼容、无UI构造、反例、既有性能测点与Core落点分别见 §3.2.1、§14/15和Core implementation binding。原C1/C2/U1接收及四组完整Golden保持，不据新增组合宣称measurement-workbench实际接线/算法/运行资格已通过。

C1/C2 的六项和 §3.5 四组完整 Golden 已由主控内容接收，状态为 `ModuleCoreImplementationReady`，尚无实现/运行或产品资格结论。U1 §11.5公开Root/Binding/SessionHandoff/Transfer、§11.6两个完整STA Host及§14/15/18相关指导已由主控限定内容接收，真实WPF/UIA/产品资格仍 `PreparationIncomplete / NotReady`；A1 两个实际消费者及发布/回退仍待对应真实验收。以下定位按各切片使用，不以全模块 PreparationIncomplete 否定已接收 Core，也不以 Core 接收宣称 WPF 通过：

| DEV-GOV-010 §3.1条件 | 本页落点与本轮结论 | 仍需处理的具体门 |
|---|---|---|
| 1 稳定边界/复用 | §1/16，参数事实与领域事实分离，两个具体消费者流程 | 实际消费者Owner接线/验收不能由文档冒充 |
| 2 闭合模块API | §2–10和附录A：强类型/单位/AST/四态/事件/Unknown/Checkpoint，C1/C2 已接收 | U1 §11.5/11.6及相关定位已限定内容接收，运行门未关闭；平台正式合同映射另采纳 |
| 3 无UI独立构建 | Core binding、§2/12：net10 BCL、窄端口、最小Host | 已确认仓库/快照后才创建工程；真实SDK不阻断模拟Core |
| 4 完整反例 | §13能力视角、§13A生命周期、§14具名测试职责 | 后续实现需真实跑相应Core/Adapter/WPF测试，不把方案当已测 |
| 5 Benchmark计划 | §15明确负载/预算B与B+1/阶段/统计口径，目标TargetPending | 消费者数值Profile未采纳只NotEvaluated；不阻断不依赖物理值的Core |
| 6 精确落点/顺序 | Core binding、§12调用、§18切片顺序 | 共享solution/宿主/平台映射由主任务串行，不扩大本会话写权 |

切片顺序与完整范围：

1. **值/Schema/事务Core**：§2–5、10纯迁移/Checkpoint、13的解析/关联/批改/Undo/Rebase；同Core及Core.Tests，不含设备/图像IO。
2. **操作/推荐/预览/Apply交接Core**：§6–9、12/13A/14；包括当前权限、查询、排空、历史及响应丢失端口模拟；不把外部CAS、算法和SDK落进Core。首片完成不能代替这些完整能力。
3. **可选WPF Inspector**：§11公开接入、PropertyGrid/批改/联动/语言/IME/键盘/布局/长文本/真实1920×1080验收；已有25.2官方公开资料直接使用，剩余是本项目编译/行为门，不是控件库准入。
4. **两个真实消费者及发布/回退**：§16/10.3；产品Owner装配正式Schema/数据/当前授权/CAS回执/真实Adapter，客户/机台物理阈值/图像质量/HIL只隔离各依赖切片。设备厂商SDK具体实现当前不在本模块范围。

逐切片六项定位（C1/C2 已接收为 ModuleCoreImplementationReady；U1 本轮指导已限定内容接收、真实WPF/UIA/产品资格未验，A1 资格待验；不以代码运行门替代正文缺口）：

| 切片 | 1边界/真实消费 | 2公开契约/Owner | 3无UI或可选UI构造 | 4反例验收 | 5Benchmark | 6精确落点/顺序 |
|---|---|---|---|---|---|---|
| C1 值/Schema/事务/恢复 | §1、16两个工具 | §2–5、10及§3.5完整Golden | §12完整输入/Factory/Exe，不需SDK | §13/14值、环、四态、批改、三方和checkpoint | §15计数/冻结/校验/Undo/hash测点 | Core binding两个Core目录，先于C2 |
| C2 操作/端口/排空 | 工程建议/试算、Owner写入分离 | §6–9原Task/权限/回执/查询/预算ACK | §12两个完整Host及ProcessRoot冷恢复 | §13A/14双轴/取消/迟到/lease/Observer | §15 t0至实际释放、资源/候选预留/根槽 | 同Core两个目录，C1后，不写设备SDK |
| U1 可选Inspector（本轮指导限定内容接收） | §11.1/11.6双消费者任务/紧凑联动 | §11.3/11.5公开Binding/Root/SessionOwner/Transfer/权限刷新 | §11.6两个完整STA Host，§12完整Core输入；纯Core不引用UI | §14 U1-STA-01～U1-DPI-10/三语IME/键盘/UIA | §15呈现/编辑确认/Detach/转交真ACK、根Task/字节 | Wpf/Wpf.Tests两个精确目录；C1/C2已接收，真实WPF未验 |
| A1 两消费者/独立发布 | §16独立算法和设备工具 | §8.4外部Owner持久CAS/Query、§10回退 | §12双夹具可执行，真实Host由消费者装配 | §14双Host、§16真实数据/回读验收 | Profile采纳后同测点；缺阈值只NotEvaluated | 不扩大本轮写权；产品装配主控另授权 |

U1 既有指导已限定内容接收；configuration §16.3单位桥已由其原Owner修正并获限定内容接收，不再列为待退修；共享导航仅按实际影响串行同步，不扩大PE类型替外部领域解围。产品资格门另列：获准代码切片的C# build/Exe真实执行、真实WPF两轴验收、两个实际消费者接线/发布回退、批准数值性能Profile及实测。真正外门只有消费者Owner尚未提供的真实Schema/样本/模型与物理验收值、实际CAS/持久原请求/当前身份授权/证据权限，以及依设备切片的HIL/客户现场；缺它们不阻断C1/C2的独立托管测试，不将安装/版本/许可证作为门。

前轮U1两种有限自审：实现者从Reserve→Core factory→Register/Bind→三语/编辑/推荐/权限→原Patch/OwnerACK→有限Unbind/原Task→CoreOwner真接管链核对，补齐了业务失败仍清理、转交固定检查戳、原Unbind晚结束和错误双轴；外部消费者按§11.6两个完整STA输入从空宿主构造，复用§12已接收Core fixture，补齐Actions可用性、公开权限刷新、Root/Application强持/DPI换算/原Patch-context保管。既有Core签名、十五项Budget、四组Golden和单位表保持；configuration单位桥状态按§16.3更新。该U1指导已由主控限定内容接收，真实WPF/UIA/产品资格未提升；本轮没有C#构建、Exe/真实WPF/UIA、HALCON/AsunImage、Golden/Replay产品运行、性能、HIL或现场验收。

主会话串行事项：已接收C1/C2与四组完整Golden保持有效，前轮0.2.1-prep的U1根/Binding/双STA Host及相关六项定位已获限定内容接收，必要时同步共享导航/API映射；不改模块索引的会话映射、不按accepted自动开工。原来源§17.2的hash保持审阅时版本，不因本页修订重标其清单“全文已审”。

### 18.1 当前全部批准范围的文档准备结论（0.2.3-prep）

结论：按IM-062当前批准的完整参数编辑器职责，以下全部能力已有唯一实施章节、公开输入输出、处理顺序、Owner/权限、异常恢复和可判定的软件验收；本轮有限两视角复核后，本模块边界内没有仍需普通实现者猜定的可决定软件设计欠账。此结论包括C1/C2、可选U1及A1接入/独立发布职责，不以纯Core代替完整模块，也不把外部算法、配置事实或设备安全移入PE。实际消费者尚未接线/验收表示资格未证，并不表示PE的软件接入设计未定义。

| 全部批准能力 | 唯一实施与验收落点 | 后续Owner与动作 |
|---|---|---|
| 动态Schema、全部强类型/单位、精确Parse/Format、canonical身份 | §2、3.1–3.5；§14 SchemaAndCanonicalTests/TextAndUnitTests | PE实现者实施纯BCL算法及预算边界；领域Schema Owner提供真实定义/来源/单位/默认/范围，不从字段名猜 |
| Missing/Null/Explicit/Default编辑、事务、依赖、校验、差异、Undo/Redo | §3.1/3.3、4/5；§13/14 DependencyAndBatchTests | PE实现者执行完整候选与权限规则；Host绑定当前身份/来源，不能用灰按钮代替Core保护 |
| 三方冲突、Rebase、Checkpoint、纯迁移、版本/回退 | §4.2、10；§14 RebaseAndCheckpointTests、§16 | PE实现者实施历史/编码/恢复；配置/配方Owner批准真实迁移映射与回退基线，宿主保留旧配置/数据/持久原请求 |
| 自动参数建议请求、拒识/多候选、解释/证据与明确采用 | §6、8.2、11.3/11.4、16.1；§14 SuggestionAndPreviewTests | PE实施关联/限额/历史/显式采用；算法/视觉Provider Owner冻结真实不可变Profile/模型/样本、确定性/seed、建议算法和拒识/精度资格，不另建PE优化器 |
| 工程Preview及视觉消费、自动试算 | §8.1/8.3、11.3、16.1；§14/15 | PE实施原操作投影与确认后请求；视觉Adapter Owner接真实Input/Profile/ResultRef及资源借用，算法/同样本性能归其模块；复用§17.3证据，不重建第二份HALCON路线 |
| Patch、Apply、CAS交接、原Query、Unknown/Partial/迟到恢复 | §4.2、6、8.4、12/13A；§14 ApplyRecoveryTests | PE实施至多一次派发、回执核验和未决写门；配置/配方Owner实施真实CAS、耐久原请求/回执/查询与当前授权；设备安全Owner承担互锁、ACK/实际回读/HIL，厂商SDK不在本模块 |
| 错误/事件/三语、取消/期限、并发、预算、订阅/lease排空 | §2、6/7/7.1、9、12.1；§14/15 | PE实现者实施所有正常/失败/停止/晚返路径；端口Owner给真实Drain证据，Host提供预算/时钟/当前权限与来源失效通知；测试Owner执行反例和实际资源验证 |
| 完整可选DevExpress WPF Inspector、键盘/IME/批改/联动、Root/Binding/交接与双STA Host | §11.1–11.6、12、§14 U1用例/§15 | PE WPF实现者按已安装25.2.3公开API实施；消费者Host Owner绑定局部语言/主题/布局/Actions/原请求Owner；资格Owner执行真实WPF/UIA及唯一1920×1080视口，两轴分别验收 |
| 无UI调用、两消费者、独立DLL构建/测试/发布/集成 | Core binding、§10.3、12/12.2、16、18 | PE实现者按四个精确工程落点及授权切片构建/打包/测试；两个消费者Owner提供真实外部端口、数据、性能Profile及发布回退流程；交付/测试Owner承担现场和产品资格 |

本轮修补的是实际设计缝隙：精确十进制/单位转换及long极限余数；codec无Profile时的消费预算接线；Default/retired规则；CheckEdits演练与提交资格分离；ChangedOnly范围；Rebase公开plan防篡改；原ID冻结身份；推荐按原快照验而按当前来源/权限采用；Partial未决/终结及回执单调；确认后AutoPreview；全部38个错误和13个恢复键的三语映射。相应断言只加入§14现有测试组，§16.3将已修配置桥转为当前事实。未新增公开DTO/枚举/重载、编码域、产品工程、脚本或重复权威；§3.5四组Golden及既有Decimal/Pixel增量证据复用。

两种有限自审均在本永久会话完成：实现者沿定义/Parse→候选/Full→一次编辑→推荐/Preview→Patch/Apply/Query→取消/晚返/真Drain→显式重基/回退核正常与反例；外部消费者用§12无UI输入和§11.6两个STA Host从空宿主检查公开构造、端口可选性、当前View/来源、预算计账、原Task/Root唯一Owner和ACK交接。定向文档检查覆盖本地链接、标题/围栏、公开声明唯一性、示例分隔符/调用形状，以及既有Golden文本/长度/hash声明保留；这些是规格检查，不是C#编译/程序运行证明。

状态边界：C1/C2既有`ModuleCoreImplementationReady`与U1/Decimal-Pixel限定内容接收保持；本轮完整范围文档结论不自授整体`ImplementationSpecificationReady`，不提升真实U1/A1的`PreparationIncomplete / NotReady`，不授权自动开工。没有执行C# build/Exe、真实WPF/UIA、产品Golden/Replay、真实消费者接线、性能、HIL或客户现场验收。剩余具体门由上表Owner承接；真实物理验收值、数据/模型、外部身份/授权、耐久CAS/Query和设备安全事实仅阻断依赖它们的切片，不阻断无关Core工作。AsunImage/DevExpress安装、版本适配和许可核验不作为待办。主控只接收本结论状态并按实际需要串行同步共享导航/调度，不再以第二轮主控内容审核作为本模块文档收口前置；模块内容修订、复核和返修仍只在此永久会话。


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

## 附录 A：Module API Contract v0.2（唯一声明索引）

本附录索引唯一声明，不再复制第二份接口或用“附录优先”覆盖正文矛盾：

- namespace `Asun.Modules.ParameterEditor`：§2 PeResult/错误/资源/权限/factory；§3值/定义/AST/校验/规范编码；§4session/edit/diff/Patch/rebase；§6操作/事件/Drain；§8Preview/Recommendation/Apply端口；§10迁移/Checkpoint。
- `IParameterEditorFactory.Create/Restore`完整声明在§2；`IParameterEditorSession.ExportCheckpoint`在§4，Checkpoint数据在§10。叙述不添加隐式重载。
- `ResolveApplyAsync`返回 `ValueTask<PeResult<ApplyReceipt>>`，不是另一条Apply入口；Snapshot/Result/Receipt/Profile/Input引用全按§3/8核验；OperationOutcome与ApplyState不合并。
- namespace `Asun.Modules.ParameterEditor.Wpf`：§11.3公开控件、呈现接口及可选 `IInspectorCommandBinding`；§11.5 唯一 `InspectorProcessRoot/InspectorBinding/SessionHandoff/Transfer` 和 `BindAsync/UnbindAsync/RefreshAccessAsync` 加法公开面；§11.6完整两个STA消费者，Root借用session/Ports、ACK后交原Core Owner，不在UI复制参数业务。无UI Host不引用这一程序集。
- `ParameterCanonical`/`ParameterTextCodec`仅纯值工具；§3.2.1加法Decimal/Pixel仅扩大一个合法类型/单位组合，不改公开签名、枚举、pe-v2-tlv1或旧Golden；该增量已获主控限定内容接收；真实PE编译/运行、新Schema工作台消费和产品资格另验。不扫描AsunImage内部。HALCON26.05全部算子经cv2使用的既定事实不作为待检项，实际类型/封送歧义只隔离该Adapter。
- Core binding中的工程/测试工程、允许/禁止路径和§18六项为唯一准入位置。C1/C2 已主控接收为ModuleCoreImplementationReady；U1上述指导已限定内容接收，真实WPF/UIA/产品资格仍PreparationIncomplete/NotReady，A1 实际资格待验。任何切片都须另获实现授权，不以全文或历史accepted自动开工。
