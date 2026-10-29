# 通用界面样式与语义控件（PKG-050）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`S1, S2`

- 独立模块编号：`IM-061`

- **文档 ID**：`PKG-050-DG`
- **版本**：`0.5.2-prep`
- **状态**：`DesignReview / Prep`
- **更新时间**：2026-10-12
- **原责任分组**：`SM-025 Presentation`
- **规划消费者**：平台 WPF 宿主、独立测量工具宿主（第二消费者）
- **技术基线**：C# / .NET 10 / WPF / DevExpress 25.2.3；语言默认 `zh-CN`、`zh-TW`、`en-US`

本文是 PKG-050 的唯一实施指导。它定义一个可以脱离 PCB 检测平台被其它视觉项目引用的 Core、可选 WPF/DevExpress 适配器和测试边界。本文给出唯一 Module API Contract v0.2、逐切片六项内容自审与§14.2整模块文档结论；本永久原会话负责内容审核、修复和验证，总控只调度及登记状态，不再将等待总控内容审核作为文档完成门。实际实施仍须另行授权，本文没有宣称已实现、已构建、已通过生产验收。

## 1. 目标、职责与禁止边界

### 1.1 负责的能力

PKG-050 负责把宿主提供的语义状态、命令、文本、主题和布局意图呈现为一致、可访问、可测试的控件行为：

1. Design Token：颜色、间距、字号、圆角、边框、图标尺寸、焦点和状态语义；浅色工程主题与深色影像主题共享语义 Token。
2. 语义控件：状态徽标/横幅、进度与取消、空状态、错误展示、命令面、导航项、结果摘要、差异提示和可访问编辑容器。
3. 交互原语：键盘导航、焦点恢复、UI Automation、SuperTip、确认/撤销意图呈现、忙碌与禁用状态、可见错误和恢复入口。
4. 布局规则：影像/结果/属性的工作台区域、Dock/Document/Inspector 的组合约束、最小可用区域、DPI 和三语长度处理。
5. 语言和主题的宿主接入面：模块提供实例级切换和通知，不创建全局语言状态，不在模块内放语言选择器。
6. 与 DevExpress 的薄适配：将 Core 的语义模型映射到匹配版本的 WPF 控件；控件选择、绑定和样式集中在适配器，核心能力不依赖 WPF 或 DevExpress。

### 1.2 明确不负责的能力

下列事实和决策必须留在调用方或其原 Owner：

- PCB、SPI、AOI、点胶、涂覆、钻孔或其它制程的目标关联、检测流程、工艺参数、判定阈值、质量放行、复判结论和设备副作用。
- 配方、程序、数据库表、身份权限事实、提交/回执、设备 SDK 句柄、图像帧所有权、HALCON 句柄和 AsunImage 算法执行。
- 视觉算法、量测、ROI 几何、缺陷推理、原始结果、AI 建议或任何 PASS/FAIL 事实。该模块即使显示状态，也只显示调用方给出的投影。
- 全局单例、Service Locator、隐式 Dispatcher、自动扫描/下载资源、隐藏窗口初始化、自动写文件或自行发现设备。
- 通过颜色、图标或控件禁用状态偷偷表达安全许可；权限和动作授权由宿主提供并在控件中显式展示。

Core 不引用产品 Shell、ViewModel、私表、制程程序集或 AsunImage。影像区域只组合viewport/宿主的只读控件slot，不持HALCON句柄。本包是主题/状态/布局/标识/命令意图的呈现能力，HALCON/AsunImage算子研究不适用；不声称核对了无关operator/封装签名，未来视觉功能接回原视觉模块，不扩入本包。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.DesignSystem.Core`（Token/主题值层）不得引用 `System.Windows.*`；只有 `Asun.Modules.DesignSystem.Wpf` 可引用 WPF/DevExpress，Core 不得反向引用。§1 已明确"Core 不引用产品 Shell、ViewModel、制程程序集或 AsunImage"。

**Blazor/Web**：设计系统 Token 通过独立 JSON 导出供 Blazor 组件消费；WPF Token 与 Web Token 共用相同语义值，不独立维护两套颜色体系；主题切换经服务端 Token 推送，不由浏览器自行重算。

**AI/HALCON 不适用**：设计系统是纯 UI 呈现能力，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 交付形态、依赖方向与第二消费者

### 2.1 发布单元

按真实职责拆为以下可独立构建、测试和发布的单元；精确工程/namespace 见附录；下表是职责名，不创建泛化适配器项目：

| 单元 | 允许依赖 | 公开内容 | 禁止内容 |
|---|---|---|---|
| `DesignSystem.Core` | BCL、批准的 Contract 类型 | 不依赖 UI 的 Token、语义状态、命令意图、校验、错误、生命周期和快照（§3） | WPF、DevExpress、产品 VM、数据库、设备/图像句柄 |
| `DesignSystem.Wpf` | Core、WPF、PKG-003 语言适配接口 | `FrameworkElement`/模板、键盘/UIA、Dispatcher 调度、主题资源桥 | 业务路由、全局语言、持久化、制程判定 |
| `DesignSystem.DevExpress` | Core、Wpf、已冻结的 DevExpress 25.2.3 | Grid/Tree/Dock/Layout/Bars/Editors/SuperTip 的映射和版本隔离 | 直接依赖页面 VM、私有列定义、设备命令 |
| `DesignSystem.Adapters.*` | Core；具体适配目标 | 语言、诊断、导航、图像/结果只读投影的显式适配 | 偷取全局服务、暴露 SDK 句柄、修改事实 |

适配器只向内依赖 Core，宿主组合所有外部服务。若某适配器需要不同 UI 技术栈，新增适配器，不修改 Core 的语义合同。

### 2.2 两个真实消费者

**消费者 A：平台 WPF 宿主。** 组合生产、编程和复判页面，提供命令权限、当前目标只读投影、语言/主题上下文、诊断导航和取消信号。页面 VM 保留在宿主。

**消费者 B：独立测量工具宿主。** 无需平台 Shell、PCB 数据库或制程程序集，只加载 Core + WPF/DevExpress 适配器，以文件/内存的通用测量摘要驱动状态、错误和宿主参数草稿的呈现。它必须能使用不同配置来源、不同导航策略和模拟执行器，且相同 Core 输入得到相同语义输出。

验收时断开平台宿主引用，消费者 B 仍须能构建、启动、切换语言/主题、提交一个模拟命令、取消并关闭；不能为消费者 B 修改 Core。

## 3. Module API Contract v0.2：唯一 Core 契约

本节是当前唯一模块 API；取代旧 v0.1 的候选代码形状，附录只登记切片与绑定，不另列 API。namespace 固定 `Asun.Modules.DesignSystem`。以下是待实现的公开签名/字段规格，不是已存在 API，也不声称片段已经编译。Core `net10.0` 只用 BCL，包括 `System.Collections.Immutable`。集合一律 `ImmutableArray<T>`，拒绝 default，空集合用 Empty；DTO 不借用可变数组/字典。键 Ordinal、大小写敏感；ID/修订/资源键非空，字符串长度与集合数量受必传 Budget 限制。

### 3.1 值、单位、错误与资源上限

不为 DIP/ms 引入未定义包装器：字段后缀写单位，使用 `double` 的尺寸/比例必须有限。DIP 是 WPF 逻辑像素；颜色是 sRGB ARGB 字节。`FontSizeDip=8..72`、其它尺寸 `0..4096`、圆角 `0..32`；这些是通用呈现技术域，不是客户物理阈值。ms 使用 TimeSpan，操作与观察期限为 `>0..24h`，不采用 0/无限期限。未知进度为 `double? Progress=null`，有值域为 `0..1`；不能转成 100%。

```csharp
public readonly record struct ArgbColor(byte A, byte R, byte G, byte B);
public sealed record ErrorInfo(string Code, string MessageKey, string TraceId,
    bool Retryable, ImmutableArray<string> FieldPaths);
public sealed record ValidationResult<T>(bool IsValid, T? Value, ErrorInfo? Error);
public sealed record ResourceBudget(int MaxKeyChars, int MaxTextChars,
    int MaxTokens, int MaxLayoutRegions, int MaxAutomationNodes,
    int MaxPendingCommands, int MaxActiveCommands, int MaxCommandRecords,
    int MaxEvents, int MaxEventReadCount, long MaxSnapshotBytes);
```

预算各值为正；`MaxActiveCommands<=MaxPendingCommands<=MaxCommandRecords`，`MaxEventReadCount<=MaxEvents`，乘法/累加 checked。全部由宿主/诊断 Profile 显式给出，无隐含256/64/16MiB“生产默认”。SnapshotBytes 为下述规范编码字节数，不是进程内存估算；受 MaxSnapshotBytes 的 envelope 在任何大集合复制之前预检，累计 UTF-8 计数与数量先做有界遍历。无法支持规模返回 `DS-RESOURCE-002`，不会截断主题或关键状态。单元测试使用 §8 的合成预算，客户性能仍由 §10 采纳。规范计数与Golden编码无需写文件：按record声明字段顺序，int/enum为有符号little-endian 4字节、long为有符号little-endian 8字节、double为IEEE754 little-endian 8字节（-0规范化+0），bool为0/1一字节；nullable double为0/1存在标志，存在再写8字节；string为有符号4字节UTF-8字节长度+严格UTF-8内容，null仅写长度=-1，拒绝未配对代理项，不进行Unicode归一化；array为4字节条数+元素。具名集合按稳定键Ordinal排序，Colors/Spacing按枚举整数排序，Required IDs按string Ordinal，Shortcut按Scope整数/ScopeId/Gesture排序，Layout按RegionId、Nodes/字体/图标按Id、ApprovedResources按ResourceKey排序。Theme/State/Layout/Automation/Shortcut分别计完整编码，TokenPolicy按同规则计；checked累计，不能只算可见字符串。MaxTokens计Colors+Spacing+Typography+Icons总项数；Policy每个集合也受MaxTokens，字符串元数据受MaxTextChars。

成功 `Error=null, Value!=null`；失败 `Value=null, Error!=null`。null API 对象、非法 Budget/TimeSpan 是 ArgumentException 系列编程错误；格式错误/重复键/过期修订/范围错误是 typed result；OOM/进程崩溃不能 catch 后返回成功。MaxKeyChars限制ID/资源键/TraceId，MaxTextChars限制描述、SourceRef/LicenseMetadata等文字，SHA固定64字符且不受较小MaxKeyChars截断；FieldPaths条数受MaxTokens、每项受MaxTextChars。Snapshot发布失败不创建半套快照。错误仅含 §5 稳定码、可读资源 MessageKey、脱敏 TraceId/字段路径，不以异常堆栈代替操作文字。

### 3.2 Token、资源和主题

```csharp
public enum SemanticColor { Surface, SurfaceRaised, TextPrimary, TextSecondary,
    Focus, Accent, Success, Warning, Error, Unknown, Disabled }
public enum SpacingToken { Xs, Sm, Md, Lg, Xl, Xxl }
public sealed record ColorToken(SemanticColor Key, ArgbColor Value);
public sealed record SpaceToken(SpacingToken Key, double Dip);
public sealed record TypographySpec(string Id, string FontResourceKey,
    double FontSizeDip, int Weight);
public sealed record IconSpec(string Id, string ResourceKey, double SizeDip,
    string Sha256, string SourceRef, string LicenseMetadata);
public sealed record ResourceIdentity(string ResourceKey, string Sha256);
public sealed record ThemeSnapshot(string ThemeId, long Revision,
    ImmutableArray<ColorToken> Colors, ImmutableArray<SpaceToken> Spacing,
    ImmutableArray<TypographySpec> Typography, ImmutableArray<IconSpec> Icons,
    double CornerRadiusDip, double BorderWidthDip, double FocusWidthDip);
public sealed record TokenPolicy(string Revision,
    ImmutableArray<string> RequiredTypographyIds, ImmutableArray<string> RequiredIconIds,
    ImmutableArray<ResourceIdentity> ApprovedResources);
public static class DesignValidator {
    public static ValidationResult<ThemeSnapshot> ValidateTheme(
        ThemeSnapshot input, TokenPolicy policy, ResourceBudget budget);
    public static ValidationResult<StateProjection> ValidateStateProjection(
        StateProjection input, ResourceBudget budget);
    public static ValidationResult<LayoutSnapshot> ValidateLayout(
        LayoutSnapshot input, ImmutableArray<string> allowedRegions, ResourceBudget budget);
    public static ValidationResult<AutomationCatalog> ValidateAutomationCatalog(
        AutomationCatalog input, ResourceBudget budget);
    public static ValidationResult<ShortcutCatalog> ValidateShortcuts(
        ShortcutCatalog input, ResourceBudget budget);
}
```

Colors/Spacing 必须各枚举值恰好一个，不允许未知枚举。Typography/Icon ID 唯一，满足 Policy 必需项，字体/图标资源键必须在 ApprovedResources；该目录ResourceKey唯一、SHA格式合法；必需ID目录不重复。Sha256 为64位小写十六进制且精确匹配。字体 Weight=100..900、100倍数，尺寸按 §3.1；FocusWidthDip>0。颜色负责语义，`Success` 不决定 PASS。首版主题的 Surface/SurfaceRaised/TextPrimary/TextSecondary/Focus/Accent 必须不透明；状态/禁用色可透明，但不能用透明色作为正文或关键焦点。文本与两种 Surface 以 sRGB 相对亮度比 `(Lmax+0.05)/(Lmin+0.05)` 校验，TextPrimary/TextSecondary>=4.5，Focus/Accent>=3；sRGB通道先除255，<=0.04045时除12.92，否则 `((c+0.055)/1.055)^2.4`；L=0.2126R+0.7152G+0.0722B。依据 WCAG 2.2 SC1.4.3/1.4.11，仅冻结 token 验证，真实控件对比/高对比模式仍需UI资格。影像像素不参与主题计算。

资源包由宿主提供批准的 manifest/资源目录；Core 不读文件、不运行 XAML、不解析任意 SVG。图标来源/许可元数据用于资产溯源；不重做已批准 DevExpress/AsunImage 授权审查。Token catalog生成器无批准消费计划，不属于当前模块范围，不作为本轮待办/准入阻断；快照/已批准资源由宿主提供，输入格式和资源清单见§6.6。主题校验失败保留活动快照；主题发布是在 Session 门内换一个不可变引用，不保证多控件 UI 原子刷新。

### 3.3 状态、布局、Automation 与快捷键投影

```csharp
public enum ViewState { Ready, Busy, Empty, Stale, Blocked,
    RecoverableError, PermissionDenied, Completed }
public sealed record StateProjection(string ContextId, long Epoch, long Revision,
    ViewState State, string TitleKey, string DetailKey,
    string? RecoveryCommandId, double? Progress, string? EvidenceRef);
public sealed record LayoutRegion(string RegionId, bool Visible,
    double WidthDip, double HeightDip, string? SelectedItemKey);
public sealed record LayoutSnapshot(int SchemaVersion, long Revision,
    ImmutableArray<LayoutRegion> Regions);
public sealed record AutomationNode(string Id, string? ParentId,
    string NameKey, string HelpKey);
public sealed record AutomationCatalog(ImmutableArray<AutomationNode> Nodes);
public enum ShortcutScope { Global, Workspace, Page, Dialog }
public sealed record ShortcutSpec(ShortcutScope Scope, string ScopeId,
    string Gesture, string CommandId, bool RequiresConfirmation);
public sealed record ShortcutCatalog(ImmutableArray<ShortcutSpec> Items);
```

ContextId 非空、Epoch/Revision正；ViewState合法、TitleKey/DetailKey必填，恢复动作仅接受宿主已登记命令。EvidenceRef是上游引用，不验证图像/质量。布局 SchemaVersion=1，Revision正；RegionId唯一且来自allowedRegions；Visible区域宽高>0，隐藏区域可0，所有尺寸不超过4096。allowedRegions本身禁止default/重复/非法key，长度<=MaxLayoutRegions；允许多根Automation树（ParentId=null），每节点独立NameKey/HelpKey必填。恢复布局不恢复领域/设备状态；持久化/hash/CAS由宿主做，Core只校验已解码快照。布局不保存 HWND、控件类型名、对象图或图像引用。

AutomationId满足 `[A-Za-z0-9_.-]+`，全实例catalog唯一；ParentId须存在且树无环。动态行键从宿主稳定项ID构造：先将原ID UTF-8 bytes编码为小写hex，接到固定region前缀（如 `result.row.626f6172642d37`）；不得用数组索引/本地化文本/随机GUID。超长编码拒绝并要求宿主提供合法稳定ID，不能截断制造碰撞。同一个业务项跨排序/筛选保持ID；A/B scope加不同固定前缀。

Gesture使用规范字符串（例如 `Ctrl+O`、`Shift+F6`），顺序 Ctrl/Alt/Shift/Win + 单个字母/数字/F1..F24/Enter/Escape/Space/Delete；大小写和保留系统组合由WPF解析入口统一规范化，Core仅接收已规范化值（非规范大小写/未知key拒绝DS-ARG-001，不自行纠正）；每 `(Scope,ScopeId,Gesture)` 唯一，全局组合不能与子scope同手势冲突。Core允许规范Ctrl/Alt/Shift/Win（各至多一次）但拒绝Alt+F4、Alt+Tab、Ctrl+Alt+Delete和所有Win组合，保留系统关闭/任务切换；ScopeId非空，Global时固定global。其它Workspace/Page/Dialog各由宿主显式互斥激活，Core不猜父子树；宿主不得同时激活有相同Gesture的多个非Global scope。IME/文本编辑、模态、拖拽、连按抑制与焦点恢复由WPF处理，不能由Core推断当前窗口。危险命令必须有确认；它不获得设备停止/质量权限。

### 3.4 类型化命令端口、结果与查询

命令是通用意图转发：Schema参数的单位/业务校验在宿主注册的 typed port，Core不造参数编辑器、设备动作或数据库事务。调用方实现的参数须不可变；注册端口必须复制任何外部可变字段。高风险授权/确认、业务幂等键、质量事实和持久化始终留在调用方。

```csharp
public interface ICommandArguments { }
public sealed record CommandSchema(string CommandId, string Revision,
    string? ConcurrencyKey, bool RequiresConfirmation);
public sealed record CommandRequest<T>(string RequestId, string ContextId,
    long Epoch, long ContextRevision, string SchemaRevision, T Arguments,
    TimeSpan ExecutionTimeout) where T : ICommandArguments;
public enum CommandTerminalState { Applied, Rejected, Cancelled, TimedOut, Failed, Unknown }
public enum RequestState { Queued, Running, Draining, Completed }
public sealed record CommandOutcome(string RequestId, CommandTerminalState State,
    ErrorInfo? Error, string? FactReference);
public sealed record ExecutionReceipt(CommandTerminalState State,
    ErrorInfo? Error, string? FactReference, bool ResourcesReleased);
public interface ICommandPort<T> where T : ICommandArguments {
    CommandSchema Schema { get; }
    ValidationResult<T> ValidateArguments(T arguments);
    bool SameArguments(T left, T right);
    ValidationResult<T> CheckAuthority(CommandRequest<T> request);
    ValueTask<ExecutionReceipt> ExecuteAsync(CommandRequest<T> request, CancellationToken ct);
}
public sealed record Admission(string RequestId, bool Accepted, bool Reused, ErrorInfo? Error);
public sealed record RequestQuery(bool Found, RequestState? State,
    CommandOutcome? Outcome, bool ResourcesReleased);
public enum DrainStatus { Drained, NotDrained, WaitCancelled }
public sealed record DrainResult(DrainStatus Status, int PendingRequests,
    int OutstandingPortCalls, int SynchronousPortCalls, int OutstandingCancellationCalls, ErrorInfo? Error);
```

注册时每CommandId唯一、总端口数不超过MaxTokens；Schema字段受MaxKeyChars，空ConcurrencyKey字符串拒绝，null才表示无key；RequiresConfirmation不由Core呈现回执代替宿主授权。Schema.Revision/ConcurrencyKey不可变。ValidateArguments必须先按相同宿主Budget检查参数数量/编码字节/字符串，再返回不可变规范副本；Core保存该Value而不是外部原引用。SameArguments/CheckAuthority/ValidateArguments必须短、确定且无副作用；CheckAuthority成功必须返回相同Arguments而不得修改参数；异常拒绝DS-INTERNAL-001，不接纳。首次请求接纳前ct已取消返回Rejected/DS-CANCEL-001，既有同内容重投不注册其ct、不改变原操作。SchemaRevision须精确匹配，ContextId/Epoch/ContextRevision须匹配Session当前投影向量；入队/启动时均检查，同步原子比较之后才能接纳/开始。同键串行FIFO；空ConcurrencyKey可并行至MaxActiveCommands。同Schema只接受精确T，不用object字典猜转换。预检参数与权限必须短/同步且无副作用；进队前和实际启动前重查权限（授权来自原Owner，不依赖UI禁用状态），启动拒绝也是已接纳请求的Rejected终态。queued期限从接纳起算含排队等待；取消与期限同时发生时同门第一次标记的stop原因固定，receipt Applied/Unknown事实优先，未应用receipt Cancelled依该原因映射Cancelled或TimedOut；Error使用相应DS-CANCEL-001/DS-CMD-003。Rejected/Cancelled/TimedOut/Failed/Unknown必须Error非null，FactReference仅port原Owner事实引用，不能由UI生成。Core调用端口不持Session锁，端口异常成为DS-INTERNAL-001，不展开用户堆栈。

`ExecuteAsync` 返回前必须停止全部子任务/回调并释放端口资源；正常返回 `ResourcesReleased=true`，Applied时Error=null，失败/未知需Error。取消只要求端口合作退出；期限到达不强杀Task，也不抢释放资源。若端口仍未返回，查询为Draining/ResourcesReleased=false，无Outcome；待真实返回后才记录终态。返回false/无效receipt/异常违约无法证明释放，保持Draining并报DS-RESOURCE-001：阻断该Session关闭与该端口再接纳，宿主诊断/隔离原Owner，不伪造terminal或自动重放。合规端口必须将异常在自己的finally释放后转换为失败receipt；Core不从异常猜资源归还。

同RequestId、同CommandId和精确请求内容（不含调用等待ct）复用原记录且不再执行；内容比较包含epoch/context/schema/timeout，Arguments由typed SameArguments逐字段比较，不能用GetHashCode代替。相同ID不同内容DS-INPUT-001。历史记录仅淘汰已Completed且ResourcesReleased的FIFO；在途不淘汰，容量满无可淘汰项接纳前拒绝。淘汰后Query.Found=false，不宣称跨重启恰好一次；调用方禁止盲用旧ID重试副作用，转原Owner查询。Core不承担批量业务事务，批量投影保留逐项Outcome，失败不能把整体显示成全成功。

### 3.5 Session、事件读取与实例隔离

```csharp
public enum SessionState { Ready, Draining, Disposed }
public enum DesignEventKind { SnapshotPublished, StateChanged, CommandAccepted,
    CommandRejected, CommandStarted, ProgressChanged, Drained,
    ResourcesReleased, CommandCompleted, ErrorReported }
public sealed record DesignEvent(long Sequence, long MonotonicTimestamp, string InstanceId, string ContextId,
    long Epoch, DesignEventKind Kind, string? RequestId,
    StateProjection? Projection, CommandOutcome? Outcome, ErrorInfo? Error);
public sealed record EventCursor(string InstanceId, long AfterSequence);
public sealed record SessionUsage(int PendingRequests, int ActivePortCalls, int SynchronousPortCalls, int OutstandingCancellationCalls,
    int RetainedCommandRecords, int EventRecords, long CurrentSnapshotBytes);
public sealed record EventPage(bool CursorExpired, EventCursor NextCursor,
    ImmutableArray<DesignEvent> Events);
public sealed class DesignSession : IAsyncDisposable {
    public DesignSession(string instanceId, string contextId, long epoch,
        long contextRevision, ThemeSnapshot theme, TokenPolicy policy,
        ResourceBudget budget, TimeProvider timeProvider);
    public SessionState State { get; }
    public ThemeSnapshot CurrentTheme { get; }
    public StateProjection? CurrentProjection { get; }
    public SessionUsage GetUsage();
    public void Register<T>(ICommandPort<T> port) where T : ICommandArguments;
    public ValidationResult<ThemeSnapshot> PublishTheme(ThemeSnapshot theme);
    public ValidationResult<StateProjection> PublishState(StateProjection projection);
    public Admission Submit<T>(string commandId, CommandRequest<T> request,
        CancellationToken cancellation) where T : ICommandArguments;
    public RequestQuery Query(string requestId);
    public EventPage ReadEvents(EventCursor cursor, int maxCount);
    public ValueTask<DrainResult> CloseAsync(TimeSpan observationTimeout, CancellationToken ct);
    public ValueTask DisposeAsync();
}
```

InstanceId由宿主为每个新Session分配不复用值（可GUID字符串）；不得在重启/回退时重用旧ID。构造参数立即校验/复制、初态Ready，无隐式UI/IO；instanceId/contextId/epoch/contextRevision/budget/timeProvider结构非法为ArgumentException；Theme/Policy内容校验失败为ArgumentException且没有已创建Session/隐藏任务，不需要异步factory。构造成功取得唯一Session所有权，端口仅借用，不由Session Dispose；首次Submit尝试在门内封闭注册目录，后续Register为InvalidOperationException。TimeProvider由宿主注入，期限用单调timestamp，UTC仅用于宿主日志；不以系统时间跳变延长预算。Epoch在Session内固定；目标切换创建新Session（旧Session继续真实排空），实例context/epoch/selection不可被迟到结果覆盖。PublishState必须匹配实例context/epoch且Revision不小于活动revision，同revision内容不同拒绝；Projection接受后更新活动ContextRevision；尚无投影时用构造contextRevision；相同快照重发NoChange（返回原Value，不发新事件）。PublishTheme仅接受Revision递增或同revision相同内容，不允许回退覆盖；版本回退在新实例加载旧包/快照，不伪造递增。

事件通道采用有界环形记录与显式 `ReadEvents`，**不提供任意 IObserver/async回调订阅**；宿主可用自己的可撤销UI订阅桥轮询。所有事件在短锁内用注入TimeProvider.GetTimestamp记录MonotonicTimestamp、分配Sequence并append，不调用外部代码；进度/状态不是质量事实。终态以Query中的唯一记录为权威，事件是投影；环满覆盖最旧事件时ReadEvents明确CursorExpired，消费者先Query/读取CurrentTheme与CurrentProjection再重建投影，不能静默把终态丢失当作成功。cursor.AfterSequence>=0、maxCount=1..MaxEventReadCount；未来cursor或InstanceId不匹配为ArgumentException，cursor只在同实例有效。PendingRequests计Queued/Running/Draining请求，ActivePortCalls计真正未退出ExecuteAsync，SynchronousPortCalls与OutstandingCancellationCalls另列；不把同一请求这些阶段相加当总请求数。每个Command事件RequestId非空；RequestQuery.Found=false时State/Outcome=null、ResourcesReleased=false，不能解释成已释放；Found时State!=null、仅Completed可有Outcome且ResourcesReleased=true。DrainResult.Drained所有四个计数均0/Error=null，NotDrained/WaitCancelled有Error和真实原计数。Accepted/Started/Drained/ResourcesReleased无Outcome，Completed携唯一Outcome；Rejected/ErrorReported携Error；SnapshotPublished无request/payload，消费者读CurrentTheme；StateChanged/ProgressChanged携Projection，均保持同instance/context/epoch。PublishState仅Progress变化时发ProgressChanged，其它字段变化（含同时Progress变化）只发StateChanged；同输入不发重复事件。Sequence/Revision checked，不能回绕。每次事件追加之前必须保留已接纳请求的结束序列容量（每请求三个尾事件），剩余容量不足时拒绝新Submit/Publish并报DS-STATE-001；保留数独立计，错误事件也不能花掉尾事件slot，末端诊断由typed result返回不再append。不在已接纳后因Sequence耗尽丢失尾事件。GetUsage在同门取得一致计数；CurrentSnapshotBytes为Theme+CurrentProjection之规范字节数（无Projection为0）；两对象各<=MaxSnapshotBytes，合计checked不超过2倍。历史/事件总保留编码量须各依对象MaxSnapshotBytes与记录数量有界，不声称等于实际工作集。端口不持事件payload/Session租约，观察者慢不阻塞命令或关闭，也不会形成CommandCompleted回调等待自身退出的循环。

## 4. 生命周期、取消、排空与线程

### 4.1 Session 与请求分离

Session为Ready→Draining→Disposed，单个请求为Queued→Running→Draining→Completed；无需执行/资源的队列取消可直接Completed。请求结束/取消不改变Ready Session。Close开始后Submit返回Admission(false,false,DS-STATE-001)、Publish返回失败ValidationResult(DS-STATE-001)，Register抛InvalidOperationException；仍可Query/ReadEvents/GetUsage；无副作用重复Close/Dispose幂等。Close接纳前ct取消仅返回WaitCancelled、不开始关闭；关闭开始后ct只取消该次观察，不撤销关闭事实。DisposeAsync共享同一个真实关闭Task、开始关闭且等待真实排空，不因await using离栈转移Owner；无无限测试等待：测试使用外层有限截止，现场若端口未归还保持隔离，不能称Disposed。

### 4.2 请求顺序与未知

预检拒绝仅CommandRejected，无CommandAccepted/Started/ResourcesReleased；已接纳序列为CommandAccepted→CommandStarted（队列取消可省略）→ProgressChanged/StateChanged（可零次）→Drained→ResourcesReleased→CommandCompleted。终态写入Query与追加三个完成事件在同门下线性化；无端口资源也确认空资源集。Drained必须同时确认端口真实退出、本请求取消Task及timer/registration回调真实归还，不等待宿主消费事件；ResourcesReleased之后唯一Outcome可查询。停止未确认时只有ErrorReported/Draining，不发三个完成事件。

单请求ct/期限到达使队列取消或running协作停止。已Applied的结果优先保留Applied（取消晚到不能倒改事实）；已停止且未应用的取消为Cancelled，期限触发停止为TimedOut；副作用不确定但资源已归还为Unknown。业务超时不等于等待超时，Close观察超时只返回NotDrained。端口仍未退出或返回释放违约时永远不能推断Unknown为已释放；需要原Owner提供新的事实/解除隔离，当前Session不能据此伪闭合。

### 4.3 并发与所有权

同步ValidateArguments/SameArguments/CheckAuthority也先在门内预留调用slot（SynchronousPortCalls+ActivePortCalls不超过MaxActiveCommands）；无slot接纳前DS-RESOURCE-002，重复调用也不得无界借用。锁外完成后finally归还slot，重进门核对Ready/向量/record再提交，Close必须计入这些已开始的同步调用。启动检查保留本请求active slot，避免二次占位；Close超时不销毁仍执行同步方法的port。Core短锁仅维护目录/队列/快照/序列，无锁内port调用或CancellationTokenSource.Cancel（它可同步调用用户注册回调）；快照化受影响CTS后锁外调用CancelAsync，保存每请求至多一个原取消Task并计OutstandingCancellationCalls，ct回调只能短标记/调度，不能await/锁内Wait；恶意/慢回调不能拖住Close观察，但原Task未退出计未排空，不提前Dispose CTS。执行期限由TimeProvider.CreateTimer/单调elapsed驱动，每在途请求最多一个timer，真实退出后Dispose timer/registration；权限/校验/执行由port承担，不捕获UI SynchronizationContext。两个Session共享不可变资源值但各有独立队列/epoch/预算/取消/事件环。Token/文本是复制的不可变数据；端口仅借用请求、拥有自己的执行资源；图像/HALCON/设备句柄从不进入Core。观察者无Core租约，不计入Close排空；WPF surface的Dispatcher执行/订阅/模板资源由WPF层自己排空，不能把Core关闭当作全部窗口关闭。

### 4.4 关闭与回退

Close在短门内关闭接纳→锁外安排queued/running取消→等待已预留同步调用、取消Task与合规receipt退出→清理可释放队列/活动引用→Disposed；在途/未释放记录保留供诊断，不提前淘汰或GC转移责任。等待取消/超时返回PendingRequests/OutstandingPortCalls/SynchronousPortCalls/OutstandingCancellationCalls和DS-CANCEL-001；再次Close观察同一关闭进程，不重新执行取消副作用。模块无native强杀机制。回退必须先真实排空，再由宿主恢复旧程序集/资源，创建新实例；未知业务结果查原Owner，禁止重放历史UI命令。

## 5. 错误码与可观测性

错误码采用稳定前缀、可本地化显示键与工程诊断分离。错误对象唯一字段见§3.1（Code/MessageKey/TraceId/Retryable/FieldPaths）；实例/context/epoch/request关联由DesignEvent/Query提供，Severity/原始异常仅宿主诊断投影，不再定义另一套错误DTO。

| 错误码 | 语义 | 重试/恢复 |
|---|---|---|
| `DS-ARG-001` | 必填参数缺失、类型/范围/单位错误 | 修正输入后重新校验 |
| `DS-INPUT-001` | 输入键、revision、资源或上下文存在歧义/冲突 | 保留旧快照，重新读取权威并明确选择 |
| `DS-THEME-001` | Token 缺失、重复、对比度或资源版本不合格 | 保留旧主题，修复资源后重新发布 |
| `DS-LOCALE-001` | 语言包/参数签名/回退链不完整 | 保留旧语言，联系资源 Owner |
| `DS-CMD-001` | 未注册命令或未知参数 | 读取能力后重新提交 |
| `DS-CMD-002` | 当前上下文/权限不允许 | 按宿主权限流程处理，不自动重试 |
| `DS-CMD-003` | 执行超时 | 查询调用方事实；未知结果不得重放副作用 |
| `DS-CANCEL-001` | 已请求取消但仍在排空 | 等待排空，不重复提交同一请求 |
| `DS-RESOURCE-002` | 队列、记录、快照、事件或参数超过显式预算 | 回压、拆批或调整已采纳Profile后重试 |
| `DS-PERSIST-001` | 持久化 revision/hash 冲突或 CAS 失败 | 重新读取并合并/放弃草稿，不覆盖新版本 |
| `DS-VERSION-001` | Core、适配器、资源或 Contract 版本不兼容 | 阻断装载，按发布回退流程恢复 |
| `DS-EVENT-001` | 事件序列/epoch 不连续 | 丢弃过期投影并请求新快照 |
| `DS-EVENT-002` | WPF宿主订阅桥/事件处理异常（Core无任意观察回调） | 宿主隔离/退订桥并查询权威结果 |
| `DS-UIA-001` | 关键元素缺少稳定 AutomationId/键盘路径 | 阻断 UI 验收 |
| `DS-RESOURCE-001` | 关闭/切换后资源未归还 | 阻断发布，保留诊断快照 |
| `DS-STATE-001` | 生命周期或状态转移非法 | 修正调用顺序，实例不可继续执行 |
| `DS-INTERNAL-001` | 未分类内部错误 | 进入 RecoverableError/诊断，不显示堆栈 |

日志和指标由宿主读取结构化事件/Query并适配PKG-005；Core不调用任意外部诊断回调、不自行写文件。至少观测：实例数、主题发布成功率、命令拒绝/取消/超时/未知数、事件cursor丢窗数、排空时长、端口违约数、未释放port数、UIA缺失数；语言呈现指标由localization提供。日志不得记录原图、口令、权限凭据或本地化文本作为主键。

## 6. WPF/DevExpress 控件与操作合同

### 6.1 通用呈现，明确原 Owner

命名空间 `Asun.Modules.DesignSystem.Wpf`，控件公共继承为WPF `Control`，不暴露DevExpress类型。所有控件有无参构造器且构造不启动任务/隐藏窗口。公共依赖属性及事件如下；默认是无输入/Empty，不臆造恢复命令。控件输入只读，事件只输出意图，由宿主调用§3的统一入口。所有上述控件共同依赖属性ContextId:string、Epoch/Revision:long（初值空/0则禁止动作）、AutomationCatalog:AutomationCatalog?、AutomationPrefix:string；宿主仅绑定合法§3.3输入，模板内部不从视觉树猜身份。

| 控件 | 唯一公共输入/输出 | 行为及非目标 |
|---|---|---|
| SemanticStateBadge / SemanticStateBanner | Projection:StateProjection?、TitleText/DetailText:string；RecoveryRequested:EventHandler<CommandIntentEventArgs> | State+图形+文字，未知不显示合格；没有恢复ID就不显示可点击恢复 |
| CommandSurface | CommandId/Text/DisabledReason:string、IsEnabled/IsPending/RequiresConfirmation:bool；Invoked:EventHandler<CommandIntentEventArgs> | 关键命令可见，Pending禁重复；确认/授权由宿主，控件不执行port |
| ProgressSurface | Progress:double?、StageText:string、CanCancel/IsDraining:bool；CancelRequested:EventHandler<CommandIntentEventArgs> | null为不确定进度，Draining显示正在结束；取消意图与停止回执不同 |
| ErrorPresenter | Error:ErrorInfo?、MessageText/RecoveryText:string、RecoveryCommandId:string?；RecoveryRequested:EventHandler<CommandIntentEventArgs> | 错误/影响/恢复可读，不以堆栈/tooltip隐藏关键动作 |
| NavigationSurface | Items:ImmutableArray<NavigationItem>、SelectedId:string?；SelectionRequested:EventHandler<SelectionIntentEventArgs> | ID唯一、父节点存在无环；切换只发意图，实际选择由宿主新revision回写 |
| AccessibleEditorHost | Content:object?、LabelText/HelpText/ValidationText:string、FieldId:string | 仅包装宿主/parameter-editor控件、错误和UIA；不拥有schema/validator/draft/undo/提交 |

`CommandIntentEventArgs` 只读字段 CommandId/ContextId:string、Epoch/Revision:long；`SelectionIntentEventArgs` 只读字段 ItemId/ContextId:string、Epoch/Revision:long；`NavigationItem` 为 `sealed record NavigationItem(string Id, string? ParentId, string TitleText, bool IsEnabled, string DisabledReason)`，string字段受宿主Budget。事件在所属Dispatcher发出，控件不持用户回调锁，宿主回调应短且不得同步等待关闭。文本来自实例语言surface，不能以标题当ID。模板内部AutomationId必须引用§3.3 catalog；宿主填写控件上下文，缺少上下文时禁止动作。

Grid/Tree/Chart/PropertyGrid/Dock 是已冻结供应商控件的组合和样式用法，不新增6个同义业务组件：服务端分页/筛选由数据Owner；降采样/SPC由statistics；步骤/checkpoint/resume与报警历史由宿主；证据hash验证/资源所有权由原Owner；typed draft/undo/递归校验由parameter-editor。DesignSystem只消费它们的只读投影与错误。measurement-workbench仍是独立模块，负责其工作台会话与领域组合，不由本模块替代。

§1.1中的结果摘要、差异提示、空状态和确认/撤销意图均由上表控件组合，不另设未定义Control：摘要/差异使用host提供的只读标题/明细加StateBanner，空状态使用StateBanner的Empty投影，确认/撤销使用CommandSurface的明确CommandId/Text与host确认/原Owner操作。摘要值和差异由host提供，模块不计算差异、不持undo历史；需丰富内容时由AccessibleEditorHost借用明确Content。因而这些能力沿相同context、文字/UIA、事件Gate和生命周期验收，没有隐含第七套API。

### 6.1.1 实际模板组成与固定视觉 Token

S3实现位置为Wpf工程 `Themes/Generic.xaml` 与模块语义Control/AutomationPeer；这是后续实施落点，本轮不创建文件。模板全部由编译程序集装载，不接运行时XAML字符串；Control自己无业务线程。S3只用WPF ToolTip承载相同标题/操作/限制/恢复文字；S4在Bars或明确支持的DevExpress目标上呈现SuperTip，宿主把同一语言文本绑定到实际目标。通用Wpf控件不实例化SuperTip或引用DevExpress，也不以SuperTip反向依赖S4。TemplateBinding绑定§6.1已定义依赖属性，所有动作调用事件意图而非Execute端口。可编辑宿主Content使用ContentPresenter，不能复制parameter-editor validator。固定首版呈现Token（宿主可通过新的完整ThemeSnapshot覆盖颜色/spacing/字号，但不得丢必需项）：

| Token / 状态 | 工程浅色 | 影像深色 / 公共尺寸 |
|---|---|---|
| Surface / SurfaceRaised | #FFFFFF / #F5F7FA | #151A21 / #202833 |
| TextPrimary / TextSecondary | #202124 / #4B5563 | #F2F4F7 / #BCC5D1 |
| Focus / Accent | #005EA2 / #005EA2 | #75BFFF / #75BFFF |
| Success / Warning / Error | #167D3E / #8A5700 / #B42318 | #77DD9A / #FFD166 / #FF9A9A |
| Unknown / Disabled | #6B7280 / #9CA3AF | #B4BEC9 / #6C7787 |
| Spacing Xs..Xxl | 4 / 8 / 12 / 16 / 24 / 32 DIP | 相同；正文14、辅助12、标题18 DIP；Weight400/400/600 |
| 几何 | Corner=4、Border=1、FocusWidth=2 DIP | MinHitHeight=32、MinHitWidth=32、主按钮MinWidth=88、icon16/20 DIP、状态徽标高24、工具条高40、状态栏高28 |
| hover / pressed / disabled | 背景Accent与Surface以sRGB通道线性值按0.08/0.16混合（四舍五入至byte，A=255） | 相同算法；disabled文字取Disabled但原因仍用TextSecondary，Opacity保持1；不以透明度隐藏关键原因 |

颜色A全255，深浅字体/焦点按§3.2同一公式验证，控件所有文字至少正文对比4.5；Icon只辅助状态，禁用颜色不独自编码权限。系统高对比模式（SystemParameters.HighContrast）用SystemColors相应刷替换本scope刷，保留文字/轮廓/Automation语义，不改全局资源；宿主资源目录显式记录此覆盖，正常ThemeId仍保留。字体 `font.system` 实际font-list定义见§6.6，不猜系统一定已安装；动效仅非关键hover100ms，可由减少动画政策关为0，错误/取消/禁用立即更新。

| 语义控件 | 命名模板部件与层级 | 状态/三语/键盘与Automation |
|---|---|---|
| StateBadge/Banner | Border→Grid：PART_StateIcon(16DIP)、PART_Title(TextBlock)、Banner另有PART_Detail及PART_Recovery(Button)，badge不挤入详情 | Projection=null→Empty；Busy为进度环形辅助+文字，不旋转整控件；Ready/Completed仅描述显示状态；Error/Denied有固定原因行。Title/Detail换行不裁关键文本，Recovery null隐藏不留假按钮 |
| CommandSurface | Border→Button PART_Invoke→横StackPanel(PART_Icon+PART_Text)，下方TextBlock PART_DisabledReason，SuperTip含标题/操作/限制/恢复 | Pending按钮disabled并显示进行中；RequiresConfirmation显示警示图标但由host确认。IsEnabled沿WPF继承属性（不重复注册同名DP）；Enter/Space产生一次Invoked，鼠标/键盘走同一gate，context无效不触发 |
| ProgressSurface | Grid→PART_Stage、ProgressBar PART_Bar、Button PART_Cancel、TextBlock PART_Drain | null→IsIndeterminate=true；0..1映射0..100。CanCancel=false仍显示原因文案，draining时不显示伪100%；Escape不自动取消；CancelCommandId:string共同输入，默认空禁止CancelRequested |
| ErrorPresenter | Border→PART_SeverityIcon、PART_Message、PART_Recovery(Button)、PART_Code(TextBlock) | 字段错误旁保留简洁文字，trace仅工程诊断SuperTip；RecoveryCommandId为空隐藏，屏幕阅读器Name含错误和恢复标题，不读堆栈 |
| NavigationSurface | TreeView PART_Nodes→TreeViewItem模板Icon/Text/DisabledReason，空内容PART_Empty；Items为宿主已解码稳定树 | 上下/Home/End/左右操作WPF树，Enter发SelectionRequested，actual SelectedId由host回写。节点名称可换行，搜索/分页由host；树结构变化按ID恢复焦点，失去项回树根而不选下一索引 |
| AccessibleEditorHost | Grid：PART_Label、PART_Editor(ContentPresenter)、PART_Validation、PART_Help | Label与Content中明确输入元素关联，宿主FieldId稳定，错误Name/Help更新；Tab进入实际编辑器，IME/paste不经过本模块新解析器，undo/apply来自原Owner |

模板触发器优先级：Disabled/无context > Pending/Draining > Error/Denied > Focused > Pressed > Hover > Ready；状态事实来自Projection/host bool，不能由动画结束改变。每个Control的OnApplyTemplate先解绑旧Button/Loaded等处理再绑定新部件，任一必需PART缺失给DS-UIA-001/诊断并禁该动作；不得保留两次Click订阅。事件与Automation Invoke调用同一短Gate校验(context/epoch/revision、IsEnabled、Pending、命令键)；异常转宿主诊断，不在控件弹隐式MessageBox。

### 6.1.2 固定三语词条与受控 region/Automation 映射

本模块只提供待实施资源目录的词条内容/键，实际Load/CreateScope/Resolve/Present沿localization指导。ResourceKey.ModuleId=`design-system`；以下key均PlainText/零参数，无第二套语言Core。业务单位/对象/具体原因由原Owner单独key提供；缺关键词条不得静默显示资源键。

| Key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| state.ready / state.busy | 就绪 / 处理中 | 就緒 / 處理中 | Ready / Processing |
| state.empty / state.stale | 无数据 / 数据已过期 | 無資料 / 資料已過期 | No data / Data is stale |
| state.blocked / state.denied | 当前不可用 / 无操作权限 | 目前無法使用 / 無操作權限 | Unavailable / Permission required |
| state.error / state.completed | 操作失败 / 已完成 | 操作失敗 / 已完成 | Operation failed / Completed |
| command.open / command.cancel | 打开 / 取消 | 開啟 / 取消 | Open / Cancel |
| command.diagnostics / command.resetLayout | 诊断 / 恢复布局 | 診斷 / 還原版面配置 | Diagnostics / Reset layout |
| progress.draining / progress.unknown | 正在结束 / 正在处理 | 正在結束 / 正在處理 | Finishing / Processing |
| error.recover / error.check | 重试 / 查看诊断 | 重試 / 查看診斷 | Retry / View diagnostics |
| column.object / column.value / column.unit / column.status | 对象 / 数值 / 单位 / 状态 | 物件 / 數值 / 單位 / 狀態 | Object / Value / Unit / Status |
| region.image / region.inspector / region.results / region.trend | 影像 / 属性 / 结果 / 趋势 | 影像 / 屬性 / 結果 / 趨勢 | Image / Properties / Results / Trend |
| help.cancel / help.resetLayout | 请求取消，结束后可继续。 / 恢复窗口布局，数据不变。 | 請求取消，結束後可繼續。 / 還原視窗配置，資料不變。 | Request cancellation. Continue after it finishes. / Restore the window layout. Data is preserved. |
| disabled.pending / disabled.permission | 等待当前操作结束。 / 联系管理员获取权限。 | 等待目前操作結束。 / 聯絡管理員取得權限。 | Wait for the current operation. / Contact an administrator for access. |

默认 `state.<name>.detail`（name=ready/busy/empty/stale/blocked/denied/error/completed）三语文字依次是：可开始操作。/等待处理完成。/选择对象或载入数据。/刷新数据后继续。/查看原因后继续。/联系管理员获取权限。/查看诊断和恢复操作。/可进行下一操作。；繁体对应可開始操作。/等待處理完成。/選擇物件或載入資料。/重新整理資料後繼續。/查看原因後繼續。/聯絡管理員取得權限。/查看診斷及復原操作。/可進行下一操作。；英文依次Ready for an action./Wait for processing to finish./Select an object or load data./Refresh the data to continue./Check the reason to continue./Contact an administrator for access./View diagnostics and recovery actions./Continue with the next action.。宿主有更精确原因时绑定其领域key，不能把这组通用提示作为设备恢复授权。

模块ErrorInfo.MessageKey统一用 `error.input`、`error.theme`、`error.locale`、`error.command`、`error.timeout`、`error.resource`、`error.layout`、`error.state`、`error.internal`九个零参数key，§5码按前缀ARG/INPUT→input、THEME→theme、LOCALE→locale、CMD001/002→command、CMD003/CANCEL→timeout、RESOURCE/EVENT/UIA→resource、PERSIST/VERSION→layout、STATE→state、INTERNAL→internal。三语分别为“输入无效 / 輸入無效 / Invalid input”“主题未应用 / 主題未套用 / Theme was not applied”“部分文字未更新 / 部分文字未更新 / Some text is unchanged”“操作未执行 / 操作未執行 / Operation was not started”“操作尚未结束 / 操作尚未結束 / Operation is still finishing”“资源未就绪 / 資源未就緒 / Resources are not ready”“布局未恢复 / 版面配置未還原 / Layout was not restored”“当前不可操作 / 目前無法操作 / Action is unavailable”“操作失败 / 操作失敗 / Operation failed”；详细影响/Trace/字段路径通过显式诊断目标显示，不把内容拼到resource key。

追加资源的detail/help key必须在同三语闭包中登记；同一个key不可因按钮位置另造翻译。模糊error不能一律显示可重试，Recovery仅按host给的command；code对应错误不自行决定恢复权。

| 固定region / 宿主前缀 | 实际目标 / 文本入口 | AutomationID后缀 / Pattern / 归属 |
|---|---|---|
| shell / A=`a`，B=`b` | host root Title；身份TextBlock；SemanticStateBanner Title/Detail | `.root` Window(仅hostPeer)，`.identity` Text，`.state` Status；Title/Detail由对应key更新，核心context不随语言变 |
| commands | CommandSurface Text/DisabledReason；BarItem.Content/SuperTipItem.Content | `.commands.open`/`.cancel`/`.diagnostics`/`.resetLayout` Button/Invoke；关键按钮由固定目标字典绑定，不扫描VisualTree |
| image | 上游viewport slot的Caption，域图像由原控件Owner | `.image` Pane；只验caption/导航到该区，图像pixels/ROI Peer由原模块覆盖 |
| inspector | AccessibleEditorHost Label/Help/Validation，host Content实际editor | `.inspector` Pane、`.field.<UTF8hex FieldId>` Group；子editor自身Value pattern；不得由容器假冒Value或向私表反射 |
| results | Grid column.Header、TableView.RuntimeLocalizationStrings支持NoRecords/NoRecordsFound/GridGroupPanelText及宿主summary模板 | `.results` DataGrid；行`.row.<hex RowId>`、列`.cell.<hex ColumnId>`，columnIds=object/value/unit/status；Grid内置Peer原Owner，已验证支持前不承诺完整原生过滤器覆盖 |
| trend（B） | Chart轴/图例标题由host已编译目标与source/unit文本投影 | `.trend` Pane；点对应文本列表`.point.<hex PointId>`提供ItemContainer/Selection，图表只读不假冒计量值写入 |
| inspector-float-01 / commands-popup-01 | 明确登记实际浮动root或Popup.Child，主题scope与语言surface一对一 | `.floating.inspector` Pane、`.popup.commands` Menu；父rootId显式为a.root/b.root，owner关闭只影响该实例 |

上述是Host默认受控表，AutomationCatalog每实例完整列出实际创建项，静态Nodes+动态row/cell/point计数受§6.7 UiBudget；仅当前虚拟化可见行/点Peer登记，item身份稳定，越限拒绝注册/提示缩小显示，不为10万行建全部UIA节点。Grid大数据源本身不是AutomationCatalog，当前可见node≤预算。模板PART装饰图标不暴露可操作Peer；Button.Name=当前简洁文本，HelpText=明确禁用原因/恢复；Help更新不能重置AutomationID。

实例语言surface注册清单严格等于这个表实际受控文字目标：模块控件自有Title/Text等可用宿主实现短 `ILocalizationSurface.PresentAsync` 批处理Resolve（非新语言Core），Grid用已有GridLocalizationSurface，Bars/Dock/摘要模板用localization §7.2已有NativeTextSurface/INativeTextHost及raw合同。每surface RequiredKeys来自此表，身份/context在登记对象中，不从默认DataContext猜；Prepare先Resolve全部零参数key，IsCurrent检查后同Dispatcher逐setter；错误返回实际已更新region列表/Failed，不声称跨控件原子回滚。活动IME/Content未更换，只更新文字属性。

### 6.2 1920×1080 组合与视觉任务流

屏幕基线固定1920×1080，工作区扣除任务栏、窗口边框、标题栏、状态栏；按当前OS实际DPI将物理工作区换算为DIP。只用这一视口，不改显示设置/分辨率，不另跑矩阵。宿主PageContract负责实际区域尺寸/数据，模块设计规则如下：

1. 上方紧凑命令区：身份/当前对象→主动作→取消/诊断；次要命令可用BarSplitButtonItem+PopupMenu。危险/取消动作不能收进仅鼠标可达菜单。
2. 中央DocumentGroup预留上游视口slot，不处理图像；一个按任务选择内容的Inspector放侧边，避免同时铺满参数、状态和证据。结果区按任务Dock/折叠，默认布局复位始终可达。
3. 层级：对象/结果主字级，参数/辅助说明次字级；空、过期、未知、错误用文字和图形，不能红绿独占。间距使用Xs/Sm/Md/Lg/Xl/Xxl，参考catalog为4/8/12/16/24/32 DIP；正文/辅助/标题字号建议14/12/18 DIP，焦点轮廓2 DIP、图标16/20 DIP。它们是可覆盖设计token，不是机台性能值。
4. 狭窄有效工作区先将次要Inspector/结果切为tab或渐进显示，保留影像slot、身份、状态、主动作、取消；不缩小关键文字/单位来硬塞。长英文允许次要说明换行/滚动，关键命令不省略且可键盘到达。
5. Tab顺序状态→对象→结果→下一动作；F6在已登记区域间循环，Escape关闭自有popup/取消编辑意图但不自动取消设备任务。焦点按稳定ID恢复；活动IME/数字输入不换模板/重建VM；失去目标的旧事件按context/epoch拒绝。

视觉品质单独验收：统一主题/边界/字级、三语长度、图标语义、hover/pressed/disabled/focus、无白色闪烁、Dock拖动/复位、结果联动和恢复位置。功能可用不能替代设计验收；动画只用于非关键过渡，尊重系统减少动画，不延迟错误/取消。

#### 6.2.1 影像 viewport slot 的责任边界

`image` 是宿主注入的 `FrameworkElement`/`ContentControl` slot。DesignSystem 只负责区域身份、Caption、布局可见性、键盘/UIA 区域入口和带 `ContextId/Epoch/Revision` 的导航意图；不构造或绑定 `ViewportControl`，不调用 `IViewportControlBinding.BindAsync`、`ViewportRendererFactory.Create`、`Attach`、`Commit`、`Revoke`、`Unbind`、`Lifetime` 或任何 frame/surface lease，也不持有 HALCON、GPU、窗口句柄或 viewport session。slot 为空、失效或未获授权时显示本模块的 `Empty/Stale/Blocked` 投影，不能自行创建替代视口或把空 slot 解释为影像已清屏。

生产宿主若实际装配 viewport，必须在宿主自己的 root/STA/owner 链中按 [viewport 0.3.5-prep §10.6–10.9](../viewport/DEVELOPMENT-GUIDE.md#106-公开bindingunbind与presenter借用) 的 `ViewportControl`、Assembly Contract v0.2、资源 Catalog、原 Task/lease、有限 Unbind 和晚到 Return 规则完成装配，再把已拥有的控件注入本 slot；viewport 的绑定、渲染和资源回收资格属于 viewport 原模块/宿主验收。本模块的 UI fixture 只使用宿主提供的占位或已绑定控件，不把 viewport 装配纳入 S3/S4 的直接实现依赖；若某宿主没有实际 viewport 消费，该路径对本模块记为 `NotApplicable`。结果表到影像的联动只发宿主 coordinator 可消费的目标 ID/导航意图，不能在本模块内补造 viewport API。

### 6.3 25.2.3 控件/API 落点

以下成员已按本机对应25.2.3官方XML核对；使用本机程序集，不下载、改版本或做依赖授权核验。程序集位于 `C:/Program Files/DevExpress 25.2/Components/Offline Packages/<package>/25.2.3/lib/net8.0-windows`。WPF编译绑定及行为验收仍是后续门。

| 任务 | 控件/精确入口 | 使用边界 |
|---|---|---|
| 实例主题 | Core包 `DevExpress.Xpf.Core.ThemeManager.SetThemeName(DependencyObject,string)`、ThemeChanged | 对root设置，不写ApplicationThemeName；浮动/弹出区显式登记根 |
| 工作台 | Docking包 DockLayoutManager、LayoutGroup、LayoutPanel、DocumentGroup | host注入Content/Caption，不吞领域布局Owner；只消费校验区域 |
| 布局保存/恢复 | DockLayoutManager.SaveLayoutToStream(Stream)、RestoreLayoutFromStream(Stream) | XML文档明确不可信反序列化风险；仅宿主可信大小/hash/版本 envelope，先读至有界隔离流；不从任意文件/URI装载 |
| 结果表/树 | Grid包 GridControl.View→TableView/TreeListView；TableView.AllowPerPixelScrolling | 稳定Item键与只读数据源，虚拟化实际验证，禁止每行绑定全量高速事件 |
| 通用参数容器 | PropertyGrid包 PropertyGridControl.SelectedObject | 只给parameter-editor/host批准模型；不通过反射自动暴露私表/SDK属性 |
| 趋势 | Charts包 ChartControl | 只接收上游已筛选/降采样投影及source/version/unit，不计算SPC |
| 命令/提示 | Core包BarManager、BarItem.Command/Content/SuperTip，SuperTip.Items、SuperTipItem.Content | BarItem绑定宿主ICommand，已完成查询回到Core；关键错误与取消始终可见 |

原生过滤、summary、日历弹窗的运行本地化覆盖不因主控件setter成功而推定；准确路径复用 [localization §7.2](../localization/DEVELOPMENT-GUIDE.md#72-2523-实例接入)。不写 BarsLocalizer.Active/GridControlLocalizer.Active 等全局状态，也不重复造本模块LocaleContext。

#### 6.3.1 两Host的具体供应商组合与联动

Grid采用DataControlBase.ItemsSource绑定UiFixture.Rows的不可变源，GridControl.View=new TableView，四个GridColumn的ColumnBase.FieldName固定ObjectId/DisplayValue/Unit/State，source/version/revision仅在显式详情/诊断显示（不藏入权限逻辑）。每列的Header用§6.1.2现语言目标，显示量格式来自host FormatProfile（decimal G或F0..12合法值，fixture固定F0），不能依赖线程CurrentCulture；State列用SemanticStateBadge绑定该行只读投影，不将ViewState当质量PASS。TableView.AllowPerPixelScrolling=true，固定行高度32 DIP，按Grid自身虚拟化加载可见行，禁止外套无限高度ScrollViewer关闭虚拟化。PropertyGrid仅绑定批准的模拟字段对象，读写/验证/草稿仍host或parameter-editor，不反射UiRow附加私表。

B趋势ChartControl.Diagram=XYDiagram2D，Series使用LineSeries2D；Series.DataSource绑定host已批准显示窗（最多2000可见点）的 `ChartPointProjection(Id,ArgumentUtc:DateTime,Value:double,Unit,SourceRef,SourceVersion)`，ArgumentUtc由fixture.TimestampTicks构造UTC DateTime（先验ticks合法），Series.ArgumentDataMember=ArgumentUtc、ValueDataMember=Value、ArgumentScaleType=DateTime、DisplayName由语言目标给出。数据本体仍完整1000/100000点用于负载/身份，显示窗是host显式[StartIndex,Count]切片，不计算/声称降采样极值保真；window越界拒绝，不拿数组索引当PointId。轴单位/原始source在可访问文字列表与标题明示，不能从科学色带或图形推量测结论。原生图表Peer不保证逐点读屏，受控文本列表提供同ID/同值定位。

结果选择→Inspector详细属性/影像slot导航意图/趋势点定位的链全部带ContextId/Epoch/RowId或PointId：事件先验当前host向量、确认稳定ID仍存在→生成短SelectionIntent→host只读投影→控件回写SelectedId；联动写入者唯一host coordinator，禁止Grid/Chart各自双向订阅形成反馈循环（originId+revision重复意图直接忽略）。影像定位只发上游viewport意图，不调用HALCON/ROI算法；结果对象失效时选中项清空并显示Stale/原因，不跳到同索引另一对象。Popup次要命令用BarSplitButtonItem.PopupControl=已登记PopupMenu，关键Cancel/Diagnostics/ResetLayout保持工具栏可见；Dropdown打开不产生业务命令。

该小节新用成员仍来自本机25.2.3定向XML：DataControlBase.ItemsSource、ColumnBase.FieldName（Grid.Core），ChartControl.Diagram、XYDiagram2D/LineSeries2D、Series.DataSource/ArgumentDataMember/ValueDataMember/ArgumentScaleType/DisplayName（Charts），BarSplitButtonItem.PopupControl（Core/Bars）。实际实现仍需编译/交互/虚拟化验证，不因本机API存在免本项目资格。

### 6.4 主题与语言：发布、应用、回退分离

Core发布不可变ThemeSnapshot；WPF每个区域独立应用。计划WPF API（签名规格）如下：

```csharp
public enum ThemeApplyStatus { Applied, Closed, Rejected, Failed, Superseded, NotDrained, WaitCancelled }
public sealed record ThemeMapping(string ThemeId, string DevExpressThemeName);
public sealed record ThemeApplyReceipt(string RegionId, long? Revision,
    ThemeApplyStatus Status, bool CallbackExited, bool MayBePartiallyApplied, ErrorInfo? Error);
public sealed class WpfThemeScope : IAsyncDisposable {
    public WpfThemeScope(string regionId, FrameworkElement root, Dispatcher dispatcher,
        ImmutableArray<ThemeMapping> mappings, TokenPolicy policy, ResourceBudget budget,
        DesignAssetManifest assets, UiBudget uiBudget, TimeProvider timeProvider);
    public ValueTask<ThemeApplyReceipt> ApplyAsync(ThemeSnapshot theme,
        TimeSpan observationTimeout, CancellationToken ct);
    public ThemeApplyReceipt Query(long revision);
    public ValueTask<ThemeApplyReceipt> CloseAsync(TimeSpan observationTimeout, CancellationToken ct);
    public ValueTask DisposeAsync();
}
```

此主题桥因调用ThemeManager，namespace/工程为Asun.Modules.DesignSystem.DevExpress（S4），通用控件仍在Wpf（S3）；禁止Wpf项目反向引用DevExpress项目。root.Dispatcher须等于注入dispatcher，在其线程构造。Mapping由宿主显式给实际已安装主题名，重复ThemeId拒绝，条数<=MaxTokens；policy/budget/timeProvider必传且构造不调用setter。每root只能登记一个自有scope，宿主装配表拒绝重复root，模块不扫描visual tree。compiled模板/资源由模块程序集提供；每root一份ResourceDictionary，资源键 `Asun.Design.<SemanticColor>`、`Asun.Design.Spacing.<SpacingToken>`、`Asun.Design.Typography.<Id>`、`Asun.Design.Icon.<Id>`；禁止改Application.Resources/全局静态主题。Typography键细分 `.FontFamily/.FontSize/.FontWeight`，Icon键细分 `.Source/.Size`；颜色为冻结SolidColorBrush，spacing/dimension为double，字体为FontFamily/FontWeight，图标为宿主已批准ImageSource。宿主先在root资源目录登记TokenPolicy批准资源，WPF只通过root.TryFindResource解析这些明确键并验证目标类型，未知/缺失资源拒绝；不从URI或XAML文本加载。先校验构造完整新字典（批准资源key/hash）、保存旧字典/主题名→Dispatcher.InvokeAsync执行短投影→只对本scope根替换自有字典并SetThemeName→回执记录实际region。外部词典不移除、不复制；owner关闭才撤销自有引用。

同scope最多一个executing+一个queued新主题，旧queued revision被新revision替代时Superseded，不执行setter；入口同步ValidateTheme(policy,budget)，失败Rejected。每scope仅保留MaxCommandRecords个revision记录，记录绑定完整theme内容；同revision同内容共用原Task（重复ct仅观察、不取消原切换），不同内容Rejected/DS-INPUT-001，淘汰或未知revision由Query返回Rejected/DS-INPUT-001，不重放。新主题必须revision递增；开始后在每一步检查scope资格/关闭。Apply接纳前ct已取消返回WaitCancelled/CallbackExited=true而不排队；接纳后超时/等待取消只停止观察，若callback未退出返回NotDrained/WaitCancelled并CallbackExited=false，且MayBePartiallyApplied保守为true（除确认尚未进setter才false）；资源仍被原任务持有，Close保留踪迹并可重复观察。任意第三方setter开始后抛错不能宣称可原子回滚，回执Failed/MayBePartiallyApplied=true；尝试恢复旧自有字典/主题，恢复失败保持受影响region禁接新切换并显式诊断，不能报告Applied。成功为CallbackExited=true、MayBePartiallyApplied=false；Query执行中返回NotDrained/CallbackExited=false，已退出记录返回原逻辑结果与当前退出标志；Superseded逻辑结果不会被迟到setter修改为Applied。Close回执Revision为最后成功theme修订（无则null），正常排空回Closed、CallbackExited=true且不宣称切换；失败前未启动setter为Rejected/MayBePartiallyApplied=false。恢复成功也保留Failed原结果。Close接纳前ct取消不开始关闭，仅WaitCancelled；接纳后Close永久停止接纳，取消queued DispatcherOperation仅在确认未执行时释放；executing真实退出后异步还原原ThemeName/撤自有字典（root仍存活时），host销毁root须在退出后。Restore未确认Close返回NotDrained，Query及Dispose保留原Task/root；独立观察期限用TimeProvider/线程池，不依赖被堵Dispatcher。共享Dispatcher阻塞时只能期限观察，不保证A/B响应隔离。

语言直接消费 `Asun.Modules.Localization.ILocalizationSurface/PresentationContext/SurfaceReceipt` 与其WpfSurfaceScheduler、GridLocalizationSurface、NativeTextSurface，构造/格式/缺词/fallback/回执/排空以 [localization §3–7](../localization/DEVELOPMENT-GUIDE.md) 为唯一权威。宿主注册本模块控件的Title/Detail/Text/SuperTip等真实目标；未登记或无公开入口的native区域NotSupported。禁止全局Culture修改、从DataContext/焦点推导scope；Core Applied与逐区域Applied分开。语言切换保留运行任务/单位/草稿/选择，格式显示与编辑解析/持久化分开；不在模块UI再放语言选择器。

### 6.5 键盘、UIA 与窗口资源

每个关键动作、禁用原因、状态、结果单元格拥有稳定AutomationId/Name/HelpText。控件用WPF AutomationPeer；树、按钮、值编辑沿相应pattern，不把装饰图标伪成可操作元素。Loaded/Unloaded幂等绑/退订，宿主负责可撤销轮询桥；模板替换不能重复绑定。窗口HWND/provider由宿主组合根拥有：仅在实际返回过provider的窗口WM_DESTROY中按微软文档调用 `UiaReturnRawElementProvider(hwnd,0,0,NULL)`，取消关闭、页面Unload和主题切换不触发。普通UserControl无native清理，模块不删除HWND、不关全局UIA。是否需要此桥由宿主provider拥有情况决定，不能与WPF既有桥重复清理；具体P/Invoke绑定不属于本Core。

### 6.6 宿主资源清单 schema、可信主题与根登记

没有真实批准消费方的Token catalog生成器不属于当前模块交付，不创建tooling工程；资源提供是两个宿主组合根职责。模块发布编译模板/语义控件，宿主提供按下表的 `DesignAssetManifest`；Core只消费TokenPolicy/ThemeSnapshot，不能运行manifest里的代码/类型名。JSON属性使用表中camelCase，C# DTO用对应PascalCase，枚举JSON用表中case-sensitive名称，数字不接受字符串/null替代；清单为JSON schemaId=`asun.design.assets`、schemaVersion=1、UTF-8严格编码，不超过min(1MiB,UiBudget.MaxManifestBytes)、深度≤8、无重复/未知字段、无类型元数据、所有字符串限制按§6.7；解码使用System.Text.Json标准类型，拒绝注释/尾逗号/重复key，不允许外部URI或动态XAML。

| 字段（精确类型） | 约束/来源 |
|---|---|
| schemaId:string / schemaVersion:int / manifestId:string / revision:long | 固定schemaId/版本1，manifestId稳定，revision正；不同revision不能沿用不同内容的同hash |
| targetFramework:string / vendorVersion:string / moduleContract:string | 固定net10.0-windows / 25.2.3 / v0.2；这是本模块发布绑定，不做依赖安装/授权核验 |
| policy:TokenPolicy | §3.2全部字段；唯一批准资源/必需Token闭包，两theme均按此policy校验，WpfThemeScope传入policy须逐字段一致 |
| assets:AssetEntry[] | ResourceKey:string、Kind:FontList或Icon、CompiledResourceKey:string、ContentSha256:string、SourceRef:string、OwnerRef:string、LicenseMetadata:string。数量≤MaxAssets、resource/compiled键唯一且受MaxKeyChars；sha为真实已批准资产完整bytes的64小写hex；Source/Owner/License为有界追溯文字，不同名查找任意类型 |
| themes:ThemeAssetEntry[] | ThemeId:string（EngineeringLight/ImageDark）、Snapshot:ThemeSnapshot（§3的全部字段）、DevExpressThemeName:string、TemplateResourceKey:string、TemplateSha256:string；两theme恰好各一个，Policy一致且资源齐全；模板key固定design.templates.v1 |
| fontLists:FontListEntry[] | ResourceKey:string、Families:string[]（顺序是fallback优先级）、DefinitionSha256:string；定义bytes为无BOM UTF8 family名字用LF连接且最后LF，DefinitionSha绑定这些定义bytes，不谎称等于系统font文件SHA |
| localeSourceRef:string / localeCatalogHash:string | 沿localization公开CatalogRevision/资源格式提供三语目录真实引用与hash；这里只登记身份，不嵌另一套language schema |

`font.system`首版有界font-list为 `Microsoft YaHei UI`、`Microsoft JhengHei UI`、`Segoe UI`，按此顺序供WPF FontFamily fallback；实际字体存在/三语glyph不足则诊断并由宿主换受批准font-list新修订，不假装合成字串证明字形覆盖。模板Body/Caption/Title依该key。实际font-list definition bytes的SHA与AssetEntry.ContentSha匹配；FontList对象来自已经批准的host compiled资源，不能从清单SourceRef作为文件路径打开。

Icon清单最小必需ID：ready、busy、empty、stale、blocked、error、denied、completed、open、cancel、diagnostics、resetLayout、recover、unknown、warning；每ID是宿主/模块已有合法来源提供的16/20 DIP编译DrawingImage（SourceRef/OwnerRef/许可元数据明确），IconSpec.ResourceKey=`icon.<id>`。部件引用这些资源，不能使用私有复制SVG path或随机占位。缺图标/模板资源时拒绝scope准备但Core主题值校验不受依赖安装阻断。真正asset bytes与编译模板原件bytes的hash在实现构建时计算并写发布清单，本文不造生产hash；§8合成hash/Golden只用于软件fixture。

主题映射首版允许清单绑定 `EngineeringLight→Theme.Office2019WhiteName`、`ImageDark→Theme.Office2019BlackName`；这两个公开字段已按本机25.2.3 Core XML核对。实现取字段值，不自己拼写供应商主题字符串、不访问全局Active；两Host可通过新manifest显式选择其它批准主题，变更须完整校验映射/模板/资源且记录真实基线。宿主从发布包的已批准目录提供manifest及对应不可变资源对象，不从网页/未知文件获得“自带hash的可信清单”；信任锚是宿主批准的包版本/manifest hash，不是攻击者提供sha。digest不等于授权，ApprovalRef由宿主装配签认/包信任流程提供，模块不产生审批或质量放行。

计划S3的 `DesignAssetManifest`、`AssetEntry`、`ThemeAssetEntry`、`FontListEntry` DTO按上表字段（数组改ImmutableArray，default拒绝）位于Asun.Modules.DesignSystem.Wpf。`AssetManifestReader.Parse(ReadOnlyMemory<byte> utf8, UiBudget budget):ValidationResult<DesignAssetManifest>`只复制有界输入/校验schema/重复/hash语法/闭包，不开文件；`VerifyResources(DesignAssetManifest manifest, ImmutableArray<ApprovedAsset> resources, UiBudget budget):ValidationResult<DesignAssetManifest>` 的ApprovedAsset为sealed record(ResourceKey:string,Kind:AssetKind,Bytes:ImmutableArray<byte>,CompiledResourceKey:string)，只以已批准有界原始bytes计算SHA。资源actual WPF对象绑定仍由host在Dispatcher完成并核定类型，Reader不偷偷打开assembly/创建控件。AssetKind唯一FontList/Icon/Template，未知拒绝；模板entry不混在fontLists而通过themes.Template资源加入批准目录。

`VerifyResources`逐项建立唯一闭包：每个theme的TemplateResourceKey精确匹配一个Kind=Template的ApprovedAsset，完整bytes SHA等于TemplateSha256；每个font-list精确匹配一个Kind=FontList资源，定义bytes/hash与AssetEntry一致；每个IconSpec通过ResourceKey精确匹配Kind=Icon的AssetEntry/ApprovedAsset，IconSpec.Sha256与ContentSha256一致，后两者的CompiledResourceKey一致。ApprovedAsset目录的ResourceKey唯一，模板可被两theme共同引用，但同key不同bytes/kind拒绝；所有条目总数计入MaxAssets。每条Bytes禁止default且非空；所有原bytes的checked累加与单条大小均不超过UiBudget.MaxManifestBytes（诊断为1MiB，与manifest JSON独立计），宿主在加载原bytes前先按批准包长度报价核限，Reader在复制/hash前再核限，超额DS-RESOURCE-002；不得用条目数量掩盖无界DrawingImage/模板原件。编译模板是模块发布的Generic.xaml原件，实际加载仍由模块程序集的编译资源完成；其SHA证明发布原件身份，不作为运行时XAML输入。资源对象的发布身份与原bytes由宿主批准包绑定，Reader不从同名ImageSource反推hash，也不以root上碰巧存在的资源替代批准对象。缺模板、错Kind或任何digest不符在scope构造/任何setter之前拒绝DS-THEME-001，保留原root资源和主题。

根登记由进程UiHostRootTable在Host槽内明确建 `RegionRegistration`（测试/宿主自有，不增加模块Root API）：RegionId/HostId/ParentRegionId:string、Epoch:long、Root:FrameworkElement、Dispatcher、Ownership=BorrowedHostRoot、CoreContextId、ThemeScope?/LocalizationSubscriptionToken?、OriginalApplyTask?/OriginalCloseTask?/RestoreTask?、State=Reserved/Ready/Closing/Retained/Released。先校验MaxRegions/MaxThemeRoots并预留entry，再创建/借用root，立即Attach，再构造ThemeScope/语言surface；失败所有已Attach引用有Owner。每host默认shell、commands、image、inspector、results及B.trend登记同host主root的明确子region；ThemeScope只为主root与实际脱离资源继承的floating/popup root各一个，不给每个子region重复SetThemeName。

浮动窗/Popup不靠供应商内部扫描：host在自己布局/弹出UI创建路径将实际浮动content根/Popup.Child以`inspector-float-01`/`commands-popup-01`登记，ParentRegionId=shell且同Host/Epoch/Dispatcher核对；未知供应商内部弹窗返回NotSupported、不称全覆盖。Popup关闭先禁止新增意图→取消queued呈现→等待原主题/语言callback退出→退订→撤自有词典→释放entry；尚未退出保持Retained，不能在Popup.IsOpen=false时清Owner。浮动回Dock同理，旧entry在退出后释放；新根使用新entry身份，不能迟到复用原entry写新对象。每root主题scope/语言surface只有一个写入Owner，宿主其它代码不直接改同一已登记目标。

S3的AssetManifestReader为static class；Parse和VerifyResources均为公开static方法，AssetKind为public enum(FontList,Icon,Template)；DTO字段顺序就是上表行内顺序（manifestId/revision等依行次），不可另增未定义字典。WpfThemeScope构造器追加必传 `DesignAssetManifest assets, UiBudget uiBudget`（在timeProvider前），接收已经AssetManifestReader/VerifyResources通过的清单及批准对象，ThemeMapping只取assets.themes闭包。实例也校验signature字段/预算一致，不把任意同key资源认为可信；root.TryFindResource拿到的对象类型与host批准登记一致才用。没有manifest没有partial scope/隐藏Dispatcher任务。Dispose不销毁借用root或包资源，resources对象由host在所有scope真实归还后释放。

### 6.7 Vendor layout envelope、CAS、保存/恢复与可信迁移

S4公开实现 `Asun.Modules.DesignSystem.DevExpress.LayoutSession`；供应商类型只出现在本适配器构造层，本Core契约/S1不变。宿主提供已批准LayoutDefinition与IO端口，模块不直接写文件/数据库。不可变DTO及端口签名规格：

```csharp
public sealed record UiBudget(int MaxManifestBytes, int MaxAssets, int MaxRegions,
    int MaxThemeRoots, int MaxVisibleAutomationNodes, int MaxDataRows, int MaxDisplayPoints,
    int MaxLayoutBytes, int MaxUiOperations, int MaxRetainedOperations, int MaxTextChars);
public sealed record LayoutDefinition(string Id, long Revision, string ProfileId,
    ImmutableArray<string> RegionIds, LayoutSnapshot DefaultLayout);
public interface ILayoutProjectionHost {
    ValidationResult<LayoutSnapshot> Capture(LayoutDefinition definition);
    ValidationResult<LayoutSnapshot> ResetToDefault(LayoutDefinition definition);
}
public sealed record VendorLayoutEnvelope(int SchemaVersion, string ProfileId,
    string DefinitionId, long DefinitionRevision, long StoreRevision, string VendorVersion,
    LayoutSnapshot Regions, ImmutableArray<byte> VendorBytes, string VendorSha256);
public sealed record LayoutReadReceipt(bool Found, bool Trusted, VendorLayoutEnvelope? Value, ErrorInfo? Error);
public enum LayoutStoreStatus { Applied, Conflict, Rejected, Unknown }
public sealed record LayoutWriteReceipt(LayoutStoreStatus Status, long? StoreRevision,
    bool ResourcesReleased, ErrorInfo? Error);
public interface ITrustedLayoutStore {
    ValueTask<LayoutReadReceipt> ReadAsync(string profileId, int maxEnvelopeBytes, CancellationToken ct);
    ValueTask<LayoutWriteReceipt> CompareExchangeAsync(string operationId, string profileId,
        long expectedRevision, VendorLayoutEnvelope next, CancellationToken ct);
    ValueTask<LayoutWriteReceipt> QueryWriteAsync(string operationId, CancellationToken ct);
}
public enum LayoutOperationStatus { Pending, Applied, Closed, ResetToDefault, Rejected, Conflict, Failed, Unknown, NotDrained, WaitCancelled }
public sealed record LayoutReceipt(string OperationId, LayoutOperationStatus Status,
    long? StoreRevision, bool CallbackExited, bool ResourcesReleased, ErrorInfo? Error);
public sealed class LayoutSession : IAsyncDisposable {
    public LayoutSession(DockLayoutManager manager, Dispatcher dispatcher,
        LayoutDefinition definition, ILayoutProjectionHost projectionHost,
        ITrustedLayoutStore store, UiBudget budget, TimeProvider clock);
    public ValueTask<LayoutReceipt> SaveAsync(string operationId, long expectedStoreRevision,
        TimeSpan observationTimeout, CancellationToken ct);
    public ValueTask<LayoutReceipt> RestoreAsync(string operationId,
        TimeSpan observationTimeout, CancellationToken ct);
    public ValueTask<LayoutReceipt> ResetAsync(string operationId,
        TimeSpan observationTimeout, CancellationToken ct);
    public LayoutReceipt Query(string operationId);
    public ValueTask<LayoutReceipt> CloseAsync(TimeSpan observationTimeout, CancellationToken ct);
    public ValueTask DisposeAsync();
}
```

UiBudget位于Wpf命名空间（S3），Layout DTO/Session/port位于DevExpress（S4）以单向引用Wpf/Core；ManifestReader的预算使用同一个UiBudget，不能复制第二套。以上签名是计划API不是本机已存在API。UiBudget各正，MaxThemeRoots≤MaxRegions、MaxUiOperations=1（首版同manager串行）、MaxRetainedOperations≥1；每profile独立session/唯一manager Owner，构造manager.Dispatcher必须等于dispatcher且在该线程，构造不Restore。定义RegionIds唯一，ProfileId/Id稳定键、DefinitionRevision正，DefaultLayout通过§3 Layout校验且只含这些region；宿主现有Dock对象实例是借用，生命周期/数据Content属于宿主，模块只改变布局，不构造未知业务对象。

`projectionHost`是必传、仅借用的宿主端口，同namespace/工程为DevExpress。宿主构造它时保存regionId→实际Dock item的固定实例表、父子树/顺序/选中项和默认复位步骤；不得按Caption、VisualTree扫描或任意类型名查找。两个方法只由LayoutSession在该manager的Dispatcher回调内、无Session锁调用，短同步、无IO/异步子工作/设备副作用，不Dispose或重建借用Content。`Capture`按definition给每个region恰好一项：当前可见性、实际有限WidthDip/HeightDip、稳定SelectedItemKey；Snapshot.Revision=definition.Revision，隐藏项尺寸可0。它核对关键image/commands/identity/state未被隐藏、主动作可达、现有浮动根均在有效1920工作区，否则返回DS-PERSIST-001；不得把旧定义尺寸冒充实际capture。`ResetToDefault`按§10.2或宿主已批准PageContract的默认树移动这些已登记item，恢复宽高/可见性/选择，完成后调用同Capture并返回实际投影；DefaultLayout提供默认期望，不替代捕获，按当前工作区调整后的实际结果仍须完整合法。Session每次校验端口返回的完整LayoutSnapshot与RegionIds；异常/失败转Failed并保原错误与恢复错误，不宣称复位成功。Save或Restore回调中端口未退出也属于同一个原DispatcherTask，观察到期保持NotDrained并强持projectionHost/manager，Close不得先归还宿主映射。端口无独立隐藏任务，构造器只校验并保存引用，不调用复位。

默认Ui诊断预算固定：MaxManifestBytes=1048576、MaxAssets=64、MaxRegions=16、MaxThemeRoots=4、MaxVisibleAutomationNodes=256、MaxDataRows=100000、MaxDisplayPoints=100000、MaxLayoutBytes=1048576、MaxUiOperations=1、MaxRetainedOperations=32、MaxTextChars=512。是诊断/内存硬guard，不是客户吞吐；生产host可通过新的明确Profile给其它正数，不能默增。任何超额Manifest/Rows/Points/Layout/owner登记前DS-RESOURCE-002，无截断/半应用；重复operation同内容复用原Task，不同方法/expectedRevision/definition/profile为DS-INPUT-001，操作记录只淘汰资源已归还且callback已退出的FIFO，满且无可淘汰项拒绝。Query未知/已淘汰ID=Rejected/DS-INPUT-001，不以旧ID盲重放。

Envelope规范存储为strict UTF8 JSON字段顺序按DTO，SchemaVersion=2；JSON属性CamelCase、枚举字符串、Regions按§3字段、VendorBytes为base64 string而非JSON数字数组；ProfileId与Definition/Version必须一致，StoreRevision正，VendorVersion固定25.2.3，Regions.SchemaVersion固定Core v1，VendorBytes为base64有界完整SaveLayoutToStream输出，VendorSha为完整原bytes SHA-256。规范envelope整体字节/字段预算都检查，base64解码先算上限（checked、拒绝whitespace/非法padding）、再分配。Envelope自身不是安全证明：ITrustedLayoutStore.Trusted只允许宿主批准的本机/包自有持久化源且原件生成/完整性保护可证明，未知外部导入/仅自带hash文件不得Trusted；模块不提供“点击导入任意vendor XML”。store实现Read按传入maxEnvelopeBytes硬上限预检/有界读取，不能先分配无限envelope再靠适配器拒绝；MaxLayoutBytes同时限制完整envelope（base64开销含在内）与raw vendorbytes。Read返回前必须结束读取/归还IO；CompareExchange/QueryWrite完整退出且ResourcesReleased=true，异常/释放false与Unknown按Core类似保留原Task/IO Owner，不声称回滚。

CAS绑定：(ProfileId,StoreRevision)，初始expectedRevision=0只可创建不存在记录；next.StoreRevision=checked(expected+1)，包中DefinitionRev不代替StoreRevision。Conflict只读新storeRevision/DS-PERSIST-001、保留原UI与旧存储，不自动覆盖。CompareExchange的operationId由host唯一生成且绑定整个next内容；store Unknown只QueryWrite原ID直到确定，不再次Save生成另一payload，不自动重试写副作用。store归还但结果Unknown返回Unknown/ResourcesReleased=true（仅IO已退出），原写事实仍store Owner，不把UI显示成功当保存成功。

保存顺序：host冻结profile/definition/expectedRev与region选择（稳定ID）→Dispatcher短操作 `SaveLayoutToStream` 写入有界自定义Stream（超MaxLayoutBytes立即抛，不能先无限MemoryStream再截断）→在同次Dispatcher调用 `projectionHost.Capture(definition)` 并校验，得一致完整envelope→callback退出→hash/Base64/编码预算→锁外CompareExchange→回执。source/Content从不序列化为本模块事实，store调用不在UI线程堵住；失败不写新envelope。无法确认完整写入流时不生成可恢复hash。

恢复顺序：锁外Read→Found=false用已登记默认布局并ResetToDefault；Found但!Trusted或错误/hash/版本/大小/profile/definition/RegionId不符时，**不得调用**RestoreLayoutFromStream，保留诊断并用注册默认布局。VendorBytes.IsEmpty表示可信迁移/默认metadata-only，VendorSha256必须为SHA256(empty)=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855，直接ResetToDefault且不调用native；Save正常必须输出非空bytes。非空且验证通过才在Dispatcher使用隔离只读有界Stream调用 `RestoreLayoutFromStream`，随后调用 `projectionHost.Capture(definition)` 并校验关键region仍存在/主动作可达、浮动根均在1920工作区；无法核对或setter抛时Failed并执行默认复位（不声称vendor restore原子回滚）。默认复位唯一调用 `projectionHost.ResetToDefault(definition)`；宿主实现直接设置明确的LayoutGroup/Panel/DocumentGroup树、GridLength与IsClosed/选中document/区域可见性，不deserialize坏bytes、不静默保存覆盖。Reset只改UI，保存默认仍需要新的显式Save+CAS。

可信迁移仅支持历史envelope v1→v2：v1字段相同但VendorVersion可缺省且旧region名properties，只有Trusted=true且DefinitionId/Revision已在批准历史表、原VendorSha正确、profile一致时才纯函数迁移；properties→inspector，其它region名不变，重复/未知名拒绝。旧VendorVersion由原包锁定25.2.3且全部原生x:Name/结构/定义身份未变化才可保留vendorbytes；properties→inspector导致原生身份变化时无条件丢弃vendorbytes（只迁移已校验metadata），不能因版本相同就保留；无法证明版本或definition布局兼容时迁移同样丢弃vendorbytes，不调用native restore，使用新的注册默认树，保持原v1原件与旧rev，后续用户Save用CAS写v2新rev。禁止“猜XML节点改名”跨供应商版本；其它schema/vendor升级要求独立批准任务，本轮不扩大。迁移结果不是存储提交，CompareExchange仍校验原expectedRev；冲突不删原件，坏数据不覆写。

所有操作Observe期限由clock/独立Timer驱动；调用store/Dispatcher入队后保存原Task，期限/ct到期只返NotDrained/WaitCancelled（实际已退出则原结果），Query关联原operation；ResourcesReleased仅IO/stream/Dispatcher真实全部退出，CallbackExited单独报告UI回调。取消若setter尚未开始确认取消，可Rejected/回退；开始后不得强中断/释放stream，不以GC回收当结束。Close停止新增、等待原IO/queued/running callback/取消Task，资源未归还保留manager/stream/task/entry；重复Close观察同一关闭，Dispose共用原Task，host最后才销毁Dock/root。已退出正常Applied/Closed的Error=null；ResetToDefault因missing可Error=null，因损坏有原码，且两种都不能解释为存储写成功。Query已接纳但未退出返回Pending/CallbackExited与ResourcesReleased当前真实标记（不能因单回调结束就置两标记true），观测期限到达返回NotDrained而原记录继续Pending，外部ct停止等待为WaitCancelled、不撤销底层操作。仅资源全归还后写唯一logical result；Query未知为Rejected/DS-INPUT-001且两标记false。Close正常Status=Closed（仅关闭动作，StoreRevision=null），OperationId固定session.close（保留ID不可用于Save/Restore/Reset）；不得把这条回执作为布局保存成功。

## 7. 最小无 UI Host 与调用顺序

S1只引用Core：构造§8合成Budget/Policy/Theme→ValidateTheme→ValidateStateProjection→ValidateLayout/Automation/Shortcut→断言值/字段错误；没有Session、订阅、UI、文件、设备或取消任务。纯同步计算取消/超时/排空不适用，有限输入与外层测试截止控制运行，不伪造ResourcesReleased事件。

### 7.1 两个完整无 UI 入口、预登记与初次关闭恢复

两个Host在同一Core.Tests Exe中独立构造，互不引用产品/私表。以下测试自有类型不属于模块公共API；它们的构造/字段/方法是唯一测试实现规定，不靠注释暗示Owner。根 `new HostRootTable(2)` 在进程Main最外层创建并存活至两个Host收尾；主进程只创建一个根表，Host不得自建第二根表绕开2槽预算。

| 测试自有类型 | 构造/字段/方法、责任 |
|---|---|
| HostRootTable | `HostRootTable(int capacity)`只允许2；`HostSlot? TryReserve(string hostId)`短锁分配唯一hostId槽，满返回null；`void Release(HostSlot slot)`仅在该槽Cleanup=Released/不存在原未退出Task时清表；`ImmutableArray<HostSlot> Retained()`供进程恢复Owner逐槽观察。不自动Dispose任何在途对象 |
| HostSlot | 仅根表构造，HostId只读；Port:OpenPort?、Session:DesignSession?、RequestCancellation:CancellationTokenSource?、Latch:TaskCompletionSource<bool>?、CloseTask:Task<DrainResult>?、DisposeTask:Task?、CleanupTask:Task<HostCleanup>?、PortTask:Task<ExecutionReceipt>?；`AttachCancellation`/`AttachLatch`/`AttachPort`/`AttachSession`只接未占用对应字段、短锁非抛异常写入；参数构造成功立即登记，再调用下一构造器。`Retain()`标Retained并保持原对象/Task；字段赋值不能暗中替换原未退出Task |
| HostFixture | 不可变record(ThemeSnapshot Theme,TokenPolicy Policy,ResourceBudget Budget,TimeProvider Clock)；`FixtureFactory.Platform()`从§8.1只读测试配置常量复制，`FixtureFactory.Measurement()`从调用参数构造等价副本；两者TimeProvider.System，无文件/隐藏UI。单独故障测试使用MemoryTimeProvider（§9），不将其耗时当实测 |
| OpenPort | `OpenPort(ResourceBudget budget,TaskCompletionSource<bool> latch)`只保存借用值，无线程/IO/句柄，参数错误在分配内部资源前抛ArgumentException；typed Schema=(view.open,open-v1,open,false)，Validate/SameArguments/CheckAuthority严格沿§3.4；CheckAuthority成功返回原Arguments、拒绝返回DS-CMD-002；测试自有AuthorityAllowed:bool初始true、故障注入由根Owner在无副作用检查前设置false。`Task<ExecutionReceipt>? ExecutionTask`保留唯一实际ExecuteTask；`CompleteNormally()`将latch设true，`StopForCleanup()`设false，幂等TrySetResult。Execute wait协作ct，try/finally停止并归还本端口registration后返回true/Applied/fact-001或false/Cancelled/DS-CANCEL-001，ResourcesReleased=true；没有执行时ExecutionTask=null。`void Dispose()`仅在ExecutionTask空或已退出时释放本端口自有测试数据，不Dispose借用latch/Session |
| HostBusiness | `sealed record HostBusiness(string Status, CommandOutcome? Outcome, string? Error)`；Status=Completed/Rejected/Failed/NotStarted；异常转换Error=`ExceptionType:message`（测试日志，不能面向操作员）；已记录Outcome不因cleanup错误覆盖 |
| HostCleanup | `sealed record HostCleanup(string Status, string? Error)`；Status=Released/Retained；独立于业务结果，NotDrained/观察到期/关闭异常为Retained，实际计数与Task仍在HostSlot |
| HostResult | `sealed record HostResult(HostBusiness Business, HostCleanup Cleanup)`；进程退出码在所有finally与恢复之后由结果决定，业务未达到预期或Cleanup!=Released为2；无try内return丢弃finally更改 |

两实际入口及完整共用流（代码是待实施测试流程，不声称已build；所用模块签名仅§3，所用辅助类型已在上表定义）：

```csharp
Task<HostResult> RunPlatformAsync(HostRootTable roots) =>
    RunHostAsync(roots, "host-a-001", "board-7", 1, "board-7", FixtureFactory.Platform);
Task<HostResult> RunMeasurementAsync(HostRootTable roots) =>
    RunHostAsync(roots, "host-b-001", "part-8", 2, "part-8", FixtureFactory.Measurement);

async Task<HostResult> RunHostAsync(HostRootTable roots, string hostId,
    string contextId, long epoch, string objectId, Func<HostFixture> fixtureFactory) {
    HostSlot? slot = roots.TryReserve(hostId); // 任何资源Factory前取得根槽
    if (slot is null)
        return new(new("NotStarted", null, "root-capacity"), new("Released", null));
    HostBusiness business = new("NotStarted", null, null);
    HostCleanup cleanup;
    try {
        var fixture = fixtureFactory(); // 取得槽后才调用Factory；失败时slot可直接Released
        var requestCancellation = new CancellationTokenSource();
        slot.AttachCancellation(requestCancellation); // 先登记，再构造latch/port
        var latch = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        slot.AttachLatch(latch);
        var port = new OpenPort(fixture.Budget, latch);
        slot.AttachPort(port); // 实际代码预登记，Session构造失败仍有Owner可清理port
        var session = new DesignSession(hostId, contextId, epoch, 1,
            fixture.Theme, fixture.Policy, fixture.Budget, fixture.Clock);
        slot.AttachSession(session); // 纯同步构造，不存在隐藏半Session的Task
        session.Register(port);
        var request = new CommandRequest<OpenArguments>("req-001", contextId, epoch, 1,
            "open-v1", new OpenArguments(objectId), TimeSpan.FromSeconds(2));
        var admission = session.Submit("view.open", request, requestCancellation.Token);
        if (!admission.Accepted)
            business = new("Rejected", null, admission.Error?.Code);
        else {
            port.CompleteNormally();
            // WaitCompletionAsync只轮询Query，最终以Query与实际port.Task均完成接受
            var outcome = await HostWait.WaitCompletionAsync(slot, "req-001", TimeSpan.FromSeconds(5));
            business = new("Completed", outcome, null);
        }
        _ = session.ReadEvents(new EventCursor(hostId, 0), 16);
    } catch (Exception error) {
        business = new("Failed", business.Outcome, error.GetType().Name + ":" + error.Message);
    } finally {
        // 初次Close可能从未发生；不只Retain后离栈。cleanup用独立期限/None token。
        cleanup = await HostOwner.ObserveCleanupAsync(roots, slot, TimeSpan.FromSeconds(5));
    }
    return new(business, cleanup);
}
```

`HostWait.WaitCompletionAsync(HostSlot,string requestId,TimeSpan observationTimeout):Task<CommandOutcome>`使用真实Stopwatch/Task.Delay(10ms)有界轮询，检查ExecutionTask（首次出现立即保存在slot.PortTask）、Query.Completed/ResourcesReleased；最终Outcome不得在port原Task未退出时接受。5s观察到期抛TimeoutException，不能取消/丢弃原port Task。fixture权限改拒绝/取消/超时/迟到按§8用独立测试注入，两个实际normal入口只走无副作用正常链。

`HostOwner.ObserveCleanupAsync(HostRootTable,HostSlot,TimeSpan):Task<HostCleanup>`是完整根恢复入口，进程Main首次finally和后续Retained恢复均调用它。它本身保证将所有非进程致命异常转为Cleanup(Retained,error)，不能从finally抛出覆盖Business；步骤固定：

1. 门内仅取得/创建该slot唯一 `CleanupTask`，已有尚未退出的CleanupTask只观察原Task，不复制执行；原CleanupTask已结束Retained后允许创建下一次有限恢复工作，里面仍只等原port/Dispose/IO Task或对已返回NotDrained的Close做新观察，不重启其底层操作。Cleanup工作不受business cancellation；外层以5s观察原工作，超时返回Retained并保留CleanupTask。观察返回不是资源释放。
2. 若已有Session而CloseTask为空，在业务失败/首次Close前场景**立即调用一次** `Session.CloseAsync(1s,CancellationToken.None).AsTask()`并保存在slot.CloseTask；已有原CloseTask则先观察它。原返回NotDrained后再发下一次CloseAsync仅观察同一关闭，不Submit/重建Session。Close调用异常保持Session/错误供诊断，不能假设Disposed。
3. 向本测试port调用StopForCleanup（无设备副作用的latch false），Queued已取消或未启动则无ExecutionTask；等待已执行原Task与Session.Close真实Drained。把“业务已Applied”保留原Outcome，cleanup不得倒改；取消stop标记也不证明端口退出。无Session但已有port时直接StopForCleanup并等待其实际Task（构造/注册前失败一般为空）。
4. 原Session真正Drained后，`slot.DisposeTask ??= Session.DisposeAsync().AsTask()`；未退出仅等原Task，不重造Task。然后确认原PortTask/port.ExecutionTask已退出、CTS取消registration已由Session释放，再Dispose借用port、宿主CTS，清latch引用。若Session从未成功构造则跳过其步骤，释放已预登记port/CTS/latch；若端口构造抛且slot.Port=null，仍释放已登记CTS/latch。
5. 在所有真实归还证据明确时工作只将Cleanup候选置Released；任何步骤未归还/异常将Cleanup置Retained和原错误链、slot保留所有强引用。CleanupTask本身退出后才允许结束/归还该slot；Release由Observe方法在await原Cleanup工作实际退出且Released之后做（外层RunHostAsync直接消费该方法结果），不在工作自身未退出时清表。初次业务错误与后续清理错误分别输出，根Owner只在Retained列表上恢复，不更换hostId绕过槽。

Main顺序 `var roots=new HostRootTable(2); var a=await RunPlatformAsync(roots); var b=await RunMeasurementAsync(roots);`，最后有限观察roots.Retained并重走上述Owner；测试实际并发用Task.WhenAll启动两个入口，不超过2槽。退出码在Main最末根据A/B各Business和Cleanup及根剩余计数决定；意外未归还非零，root不因退出码而自动清空。特意违约负例隔离子进程按§9退出2，不声称其Session已释放。故障断言必须包含：CTS构造后/port构造后/Session构造失败、Register或Submit抛、首次Close前异常、原Close观察到期、原Dispose未退出、迟到恢复以及A失败/B正常。

### 7.2 两个可选 UI Host 与恢复

真实UI Host采用同一Wpf.Tests工程，两种模式对应上面A/B，各有独立root、Context/Epoch、Core session、localization scope、Theme scope与slot；A生产摘要+视口slot+结果Grid+Inspector，B独立测量摘要+视口slot+参数容器+趋势投影，二者共用本模块控件/契约，不导入任何产品VM。

进程级 `UiHostRootTable(int capacity=2)`为测试/宿主自有；TryReserve(hostId)返回UiSlot?，满不构造，Release仅在全部root/STA/模块callback原Task已退出，Retained列表由进程Main恢复Owner持有。UiSlot扩展§7.1HostSlot，存Root/DispatcherThread?/FactoryTask?/CoreSession?/LanguageScope?/ThemeScope?/LayoutSession?/原Apply/Restore/Close/DisposeTask（每个模块独立字段）/RegionRegistration[]，所有构造先预留槽/entry后Attach；恢复方法ObserveCleanupAsync签名/业务与cleanup独立语义沿§7.1，步骤换为本节UI顺序。进程级表固定最多2个活跃slot，Factory前TryReserve；在所属STA创建root/Dispatcher/控件并立刻Attach，创建Core→注册port→创建localization scope/surfaces→创建DevExpress WpfThemeScope(regionId,root,dispatcher,mappings,policy,budget,assets,uiBudget,timeProvider)→构造host自有ILayoutProjectionHost实例表/默认步骤与ITrustedLayoutStore→创建LayoutSession(manager,dispatcher,definition,projectionHost,store,uiBudget,timeProvider)并立即Attach→Apply/订阅事件桥。root与Dispatcher由host拥有，模块仅借用；主题scope归属DevExpress工程，通用Wpf工程不反向依赖它。失败只清理已取得对象，不丢原异常/原Task。

默认Host固定1920×1080验证viewport、OS当前DPI；至少一轮A/B同Dispatcher检验实例隔离，阻塞试验再各自STA以检验两个scope资源不混。分别STA仍由进程表保留root/DispatcherThread/FactoryTask/ApplyTask/CloseTask/DisposeTask，不能在窗口Closed或函数return时离栈；不创建新会话或新产品工程来代替此测试Host。

关闭按顺序撤宿主新增动作/事件桥→关闭localization surface并等真实退出→Layout Close（原IO/Restore）→Theme Close（原Apply/主题Restore）→Core Close→各Dispose→仅在全部资源/回调实际归还后host关闭root/Dispatcher并Join STA、归还slot。任何步骤NotDrained/CallbackExited=false维持slot、窗口Owner与原Task，恢复入口只Query原revision或Layout原operationId/重复Close观察，任一已创建模块CloseTask为空时恢复Owner先调用其初次Close并登记原Task，再有限观察；FactoryTask未退出则保留root/DispatcherThread/FactoryTask，不创建第二root，禁止重建root覆盖未知scope。准备草稿/未知事实仍查原Owner，不重放UI命令。语言实际公开签名沿localization指导，不在本模块建第二套ILocalizationSurface/工厂。

## 8. 可判定样例与两个怀疑式复审视角

### 8.1 固定合成夹具

诊断Budget（Profile `DS-Core-Diagnostic-001/r1`）：MaxKeyChars=128、MaxTextChars=512、MaxTokens=128、MaxLayoutRegions=8、MaxAutomationNodes=128、MaxPendingCommands=8、MaxActiveCommands=2、MaxCommandRecords=32、MaxEvents=64、MaxEventReadCount=16、MaxSnapshotBytes=65536。只用于确定性软件断言/诊断测量，不是消费者生产容量或性能承诺。

ThemeId=EngineeringLight、Revision=1；颜色如下（A均255）：Surface=#FFFFFF、SurfaceRaised=#F5F7FA、TextPrimary=#202124、TextSecondary=#4B5563、Focus/Accent=#005EA2、Success=#167D3E、Warning=#8A5700、Error=#B42318、Unknown=#6B7280、Disabled=#9CA3AF；Spacing=4/8/12/16/24/32 DIP；Typography Body/Caption/Title=14/12/18 DIP、Weight=400/400/600、FontResourceKey=font.system；图标open/ResourceKey=icon.open/SizeDip=16；Corner=4、Border=1、FocusWidth=2。Policy.Revision=policy-r1，Policy必需Body/Caption/Title与open；ApprovedResources为font.system/SHA=64个1、icon.open/SHA=64个2，IconSpec Sha同后者、SourceRef=test-fixture、LicenseMetadata=synthetic-test。这些是合成manifest身份，不能用于真实资产发布/证明字体存在。

State为ContextId=view-17、Epoch=1、Revision=1、Ready、TitleKey=state.ready、DetailKey=state.ready.detail、RecoveryCommandId=null、Progress=null、EvidenceRef=null。Layout为SchemaVersion=1/Revision=1，allowedRegions=image/inspector/results：image(Visible=true,960×640 DIP)、inspector(true,320×640)、results(false,0×0)，SelectedItemKey=null；仅合成尺寸，不代表真实1920视口已验收。Automation为root/result.row.626f6172642d37（Parent=root）两节点，NameKey/HelpKey非空。Shortcut为Workspace/work-1/Ctrl+O/measurement.open/false。

### 8.2 实现者视角：能否在空 Host 得到唯一结果

| ID / 切片 | 输入/操作 | 唯一期望与恢复 |
|---|---|---|
| DS-S1-01 正常 | 上述Theme/State/Layout/Automation/Shortcut | 全部IsValid，Value为复制不可变快照，Error=null；无IO/UI/副作用 |
| DS-S1-02 空/缺失 | 空导航可由UIEmpty呈现；Theme空Colors；空LayoutRegions | Theme为DS-THEME-001；Layout允许空（无区域），空Automation允许；default集合为DS-ARG-001，不补猜主题 |
| DS-S1-03 范围/精确值 | Font=7、NaN尺寸、Progress=1.01、重复颜色、同ID两个图标、非法SHA | 返回范围/重复字段路径；不截断/夹紧；旧快照仍可用 |
| DS-S1-04 对比 | TextPrimary与Surface均白；Focus与Surface均白 | DS-THEME-001，指出颜色pair；不据单个颜色算质量 |
| DS-S1-05 稳定选择 | 两行原IDboard-7/board-8排序反转；重复NodeId；Parent环 | 排序后原ID不变；重复/环拒绝，不以数组索引选择另一对象 |
| DS-S1-06 容量 | 128→129个token或128→129个nodes；超SnapshotBytes；checked溢出 | 边界内可校验，超限DS-RESOURCE-002；不复制无限数据/越限分配 |
| DS-S1-07 重复/并发 | 同输入两次；两个线程用不同theme对象并行Validate | 结果等价，不改输入、不共享当前主题；纯函数无Session状态 |
| DS-S1-08 生命周期/版本 | 同步调用结束；LayoutVersion=2 | 同步无取消/排空不适用；未知布局版本DS-VERSION-001；回到宿主注册v1默认快照，不自动迁移 |
| DS-S2-01 正常 | OpenPort允许，闩锁release=true | Admission Accepted，port执行1次；Started→Drained→ResourcesReleased→Completed；Query Applied/true |
| DS-S2-02 预检/启动权限 | 缺参数；未注册命令；入队后权限改拒绝 | 预检仅Rejected且执行0次；启动权限拒绝为已接纳Rejected终态，执行0次、空资源已归还 |
| DS-S2-03 重复/冲突 | req-001同内容两次；同ID变ObjectId | Reused=true且执行1次；不同内容DS-INPUT-001，无第二次副作用；FIFO淘汰后Found=false不能盲重放 |
| DS-S2-04 并发/回压 | 同key两个闩锁port；不同key；8个pending后第9个 | 同key不同时running、FIFO；不同key不超过2 active；容量满先拒绝，无终态记录被提前淘汰 |
| DS-S2-05 取消/迟到 | queued取消；running取消但port暂未退出；Applied后取消 | queued无Started、Cancelled；running为Draining/false/无Outcome；release后Cancelled或Unknown；Applied不倒改 |
| DS-S2-06 超时/关闭 | 固定时钟到2s且闩锁未释放；Close观察1s | 不返回终态、不释放；Close NotDrained带在途计数；释放后重复Close Drained，Submit被拒绝；重复Dispose幂等 |
| DS-S2-07 端口违约 | port返回ResourcesReleased=false或抛异常 | DS-RESOURCE-001并隔离，不发Completed；负例在观察NotDrained/无终态后作为预期结果通过，测试夹具无外部资源；只可结束隔离测试子进程，不称Session已释放。意外未排空必须非零 |
| DS-S2-08 事件与epoch | 超64个事件慢读；旧epoch State；两Session相同requestID | CursorExpired显式；Query恢复当前终态；旧epoch拒绝DS-EVENT-001；两个实例独立，无回调自排空循环 |
| DS-S2-09 回退/长稳 | 正常Close后新实例用旧包；重复发布/关闭循环 | 原未知请求由原Owner查；无历史命令重放；活跃port/queue回0，history/event始终有界 |

### 8.3 操作与恢复视角：能否看清、取消、保持草稿并退出

| ID / 切片 | 反例 | 应呈现/恢复与验收断言 |
|---|---|---|
| DS-WPF-01 双scope主题 | A浅→深，B保持原主题；自有popup/Dock浮动根 | 仅登记A区域刷新，B不变；未登记区域不能宣称Applied，影像像素不改 |
| DS-WPF-02 局部失败 | Core发布成功，某区域setter抛异常/Dispatcher阻塞 | Failed或NotDrained明确标区域；保留可用旧区域/原任务，实际退出后CallbackExited=true；失败回滚不抹原错误 |
| DS-WPF-03 三语/编辑 | 同进程A zh-CN→zh-TW，B en-US；IME/ulong/decimal编辑中 | 复用localization/parameter-editor入口，草稿/单位/稳定ID/选择保持；不写全局Culture、不重开native窗冒充热更新 |
| DS-WPF-04 键盘/UIA | 排序后焦点、禁用恢复、危险组合连按、仅图标取消 | 稳定ID恢复、禁用原因可读、危险确认/重复抑制；关键动作键盘可达；窗口销毁清理不发生在取消关闭 |
| DS-WPF-05 关闭/资源 | Loaded/Unloaded循环、关闭中主题切换、setter未退出 | 退订不重复、拒绝新切换；回调未退出时不称Disposed；root仍由host拥有，模块只撤自有资源 |
| DS-WPF-06 退化证据 | 上游Stale/Blocked/噪声/遮挡标记 | 如实显示来源/原因/恢复意图，无HALCON/质量推断；不把Unknown显示合格 |
| DS-WPF-07 视觉/数据规模 | 固定1920×1080实际工作区、三语长文本、宿主大列表/趋势投影 | 实测焦点/命令/单位不截断，Inspector渐进显示、虚拟化稳定选择；趋势正确性/降采样由上游验收，本包只验显示映射 |

### 8.4 完整编码 Golden（合成，非发布资源）

本表按§3.1完整字段编码，SHA-256针对全部bytes（不对hex字符串取hash）。Theme/State为§8.1完整fixture；Policy.Revision固定policy-r1，RequiredTypography按Body/Caption/Title，RequiredIcon为open，ApprovedResources按font.system/icon.open。Color编码为enum Int32后A/R/G/B四字节；nullable Progress=null编码00。可判定断言：独立fixture字段重建字节与下表完整hex逐byte一致，长度/SHA相符，任意字段变更（含未显示SourceRef/metadata）应改变hash；不是仅截图或37字节子投影。校验测点依据本完整fixture，真实资产不得使用合成SHA。

- `StateGolden/r1`：77 bytes；SHA-256=`2ab4a9f1681afc738052547e96ea45035349b5f8c7271becbe83e95330f665f1`。

```text
07000000766965772d313701000000000000000100000000000000000000000b00000073746174652e72656164791200000073746174652e72656164792e64657461696cffffffff00ffffffff
```

- `ThemeGolden/r1`：468 bytes；SHA-256=`915649c7caf0d8dde3062b807da895b8480f1e90107a94cf70f1f16d1e4a61da`。

```text
10000000456e67696e656572696e674c6967687401000000000000000b00000000000000ffffffff01000000fff5f7fa02000000ff20212403000000ff4b556304000000ff005ea205000000ff005ea206000000ff167d3e07000000ff8a570008000000ffb4231809000000ff6b72800a000000ff9ca3af060000000000000000000000000010400100000000000000000020400200000000000000000028400300000000000000000030400400000000000000000038400500000000000000000040400300000004000000426f64790b000000666f6e742e73797374656d0000000000002c40900100000700000043617074696f6e0b000000666f6e742e73797374656d000000000000284090010000050000005469746c650b000000666f6e742e73797374656d00000000000032405802000001000000040000006f70656e0900000069636f6e2e6f70656e000000000000304040000000323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232320c000000746573742d666978747572650e00000073796e7468657469632d746573740000000000001040000000000000f03f0000000000000040
```

- `PolicyGolden/r1`：225 bytes；SHA-256=`d74e6d1b788e067c79e4d06ea213321fd3f3990408d706e6ea7242099bf13098`。

```text
09000000706f6c6963792d72310300000004000000426f64790700000043617074696f6e050000005469746c6501000000040000006f70656e020000000b000000666f6e742e73797374656d40000000313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131313131310900000069636f6e2e6f70656e4000000032323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232323232
```

### 8.6 本轮窄闭的 Host / UI / 资源 / 布局反例

| ID | 输入/故障位置 | 可判定输出/Owner/恢复（未执行测试） |
|---|---|---|
| DS-S2-H01 | FixtureFactory抛、CTS/latch/port先取得后Session构造因Theme非法抛 | 首个Factory前已有root槽；Business Failed，Cleanup只释放已登记对象；无Session则无伪Close，Port/CTS有实际Root，Released后slot=0 |
| DS-S2-H02 | Session构造成功Register/Submit阶段抛，CloseTask仍null | finally Owner创建且记录首次原CloseTask；原业务错误不被cleanup覆盖；port.StopForCleanup/原Task真实退出后Dispose原Session和host CTS，才能Released |
| DS-S2-H03 | Close NotDrained、Dispose未退出、原Cleanup观察5s到期 | Cleanup Retained，根列表保留原Task/Session/port；再次恢复只观察原未退出工作，迟到退出后Released；进程槽不超2、A Retained时B仍可占剩余槽 |
| DS-S3-01 | 不完整PART/错误Theme/Manifest缺icon.cancel或模板、错Kind、原bytes总额越限，未知JSON字段、重复ResourceKey/SHA变造 | control禁对应动作并诊断；Reader返回typed失败字段路径，scope构造前拒绝，无动态XAML/任意文件，保留旧模板/资源 |
| DS-S3-02 | A三语切换，B原语言，已活动IME/虚拟化滚动重排/无权限 | 原Content/草稿/ID/单位不变；Text/Name/Help/SuperTip按实际region回执；不重建editor或拿新索引串另一行，无权限不可触发 |
| DS-S3-03 | VisibleNodes 256→257、Rows 100000→100001、fixture SourceVersion变更 | 超限注册/编码前DS-RESOURCE-002；大源并不一次建10万UIA元素；变SourceVersion改变完整fixture hash，不能继续复用旧输入身份 |
| DS-S4-01 | Popup/floating创建后语言/theme构造失败，关闭时setter未退出 | Region预留/Attach先于scope；Owner记录原Task，Retained/root不销毁；重新观察真实退出后解除binding，只清该Host资源，不误清B |
| DS-S4-02 | envelope v2 valid but Trusted=false，或Sha/size/profile/version/definition/region不符 | native Restore调用计数0；明确ResetToDefault并保留diagnostic/原store，用户未Save时CAS次数0 |
| DS-S4-03 | 保存流超过1MiB/Read超过maxEnvelopeBytes、store CAS冲突/Unknown | 超流停止/拒绝，CAS0；Conflict保旧rev/DS-PERSIST-001；Unknown保持原operationId并QueryWrite，不能新payload重写 |
| DS-S4-04 | Trusted v1 properties→inspector，历史Vendor未知/旧region重复、迁移后CAS冲突 | 已批准v1 history且版本/原生item身份均未变化才可保持bytes；properties别名变化或Vendor未知只注册default、不反序列化；重复拒绝；Conflict不覆盖原v1且旧配置可查 |
| DS-S4-05 | Restore抛、Capture缺region/动作不可达/错误向量、ResetToDefault失败或未退出、IO或Dispatcher原Task未退出 | Failed记录原错误与恢复错误，callback/ResourcesReleased分开，NotDrained保留manager/stream/Owner，不能为关闭直接销毁root |
| DS-S4-06 | 同operationId同请求重入、不同expectedRevision/方法，记录FIFO满 | 同内容原Task只一次store/Dispatcher执行，不同内容DS-INPUT-001；只淘汰真实退出记录，满无可淘汰项DS-RESOURCE-002 |

v1可信迁移具体合成输入：ProfileId=DS-Wpf-Host-A-normal、DefinitionId=host-a-default/Revision=1，StoreRevision=7，Regions image/properties/results（三合法项），VendorVersion=25.2.3且可信历史表已绑定，迁移后schema=2、properties改inspector、VendorBytes=空、VendorSha=SHA256(empty)、expectedRevision仍7，显式Save时next.StoreRevision=8；Conflict若store已到8，则不得写9自动覆盖。这里没有虚构可反序列化的vendorXML/生产SHA，native roundtrip必须在实现后用真正SaveLayoutToStream输出验证。

### 8.5 算法适用性

本包无视觉算法；主题/状态/布局/UIA无需HALCON/AsunImage调用。噪声/遮挡只作上游只读证据，不实现滤波、测量、训练、模型或备用算法。不声称已核对无关operator/封装签名；未来视觉需求回原视觉模块，不扩大本包。

## 9. 验证工程、验收与运行资格

Core测试工程采用DEV-GOV-010 §3.1现有约定：Microsoft.NET.Sdk/net10.0/OutputType=Exe，只ProjectReference受测Core与BCL。入口执行当前实施切片对应§8全部用例，任一断言失败、未完成、必需项跳过返回非零并列用例ID。S2用可控制闩锁/TimeProvider实现（timer按固定timestamp推进，不用真实sleep竞态）；每用例有限截止5s、外层进程120s，两者仅合成测试保护，不是生产指标。意外超时/端口未返回须非零，不能Dispose永久等待后宣称通过。DS-S2-07预期端口违约作为隔离子进程负例：子进程输出DS-RESOURCE-001/NotDrained及原Owner记录并退出2；父harness只在这些预期值、没有Completed且外层截止内退出均吻合时通过该负例，不将子Session写成ResourcesReleased。预期未知仅属于明列负例，不能为其它必需正常路径放宽释放断言。

命令绑定见附录：build Core与run测试Exe，`dotnet test`不能替代这个入口。先验证S1，再S2；没有S2实施时不把S2标skip通过。WPF/DevExpress测试使用自己的真实WPF Host，不能以Core smoke、HTML、截图或模拟器替代行为资格。只在固定1920×1080验证视口和当前实际OS DPI上运行/记录；不改用户显示设置，不启动其它分辨率/DPI矩阵。

| 层级 | 必需证据 | 未执行的限制 |
|---|---|---|
| S1/S2 Core | §8用例、预算边界、两无UI装配、build/run实际退出码、§10原始测量 | 本轮仅指导，不声称构建/测试通过 |
| WPF/DX | 25.2.3实际编译、两Host主题/三语/键盘/UIA/编辑/关闭，§8.3、视觉品质独立确认 | setter/XML签名或模拟器不能证明真实控件/原生弹窗覆盖 |
| Package/布局 | 依赖/资源闭包、真实字体/图标hash、可信布局迁移/损坏回退、资源长期释放 | 不把合成hash用于发布、不因依赖已批准而省本项目验证 |
| 消费者与性能 | 平台Host与独立测量Host实际装配、采纳Profile、长稳/内存/排空/回退 | 诊断Profile目标缺失为NotEvaluated；不虚构机器节拍/生产结果 |

## 10. 性能预算与测量方法

本节冻结测量协议与测点，不设未经真实消费者采纳的性能达标值。每个不可变 BenchmarkProfile 必须记录唯一 ID/修订/hash、构建提交与 .NET/适配器/后端版本、OS 与 CPU/内存/存储/网络配置、带 hash 的输入集及规模分布、调用混合与并发/到达模型、队列与资源预算、时钟测点边界、故障注入点，以及 ColdSampleCount、WarmupIterationCount、MeasuredSampleCount 和各指标的验收目标/阈值来源。Profile 变更必须产生新修订，不得跨 Profile 合并数据。

冷测每个样本均从新进程/新模块实例开始，并清空模块自有缓存；OS 文件缓存、数据库缓存、外部服务和设备状态无法由模块清空时，必须记录其实际状态，使用隔离可重建夹具，不标称为冷。热测先按 Profile 固定次数执行预热，再按固定样本数测量；不使用自适应停止、只报最快值或丢弃慢样本。外部副作用操作使用可重建隔离夹具和唯一操作 ID。每个样本用单调时钟记录原始耗时；P50/P95/P99 的算法按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 计算，并同时报告样本数、单位和原始值。吞吐量使用 Profile 固定的观察窗口计算已完成且有效的操作数/时间，并单列拒绝、错误、重试和未完成项。

每轮同时记录 CPU、工作集/私有字节、托管分配与 GC、native/适配器缓冲、磁盘/网络 I/O、连接/句柄峰值，队列当前/峰值条数与字节、排队等待、积压变化、接受/拒绝/丢弃计数。排空时间从关闭新接纳开始，至在途操作、回调、IO/适配器资源全部实际归还结束；期限到达只记超时和未完成项，不得强杀后宣称排空。每项验收阈值必须引用消费者要求、正式 Contract/资源风险依据或已批准资格记录的稳定 ID；没有来源时写 TargetPending，只能报告测量结果，不得判定达标。协议/资源硬上限与性能目标分开，只有唯一权威中的必要性、数值和来源均已明确时才可作为硬上限，不从基准数据臆造上限。

### 10.1 可执行诊断 Profile（测试工程，不新增产品API）

测试夹具定义唯一不可变 `DesignBenchmarkProfile`（namespace Asun.Modules.DesignSystem.Tests），字段依序为：ProfileId/Revision/ContractVersion:string，InputThemeSha256/InputStateSha256/InputPolicySha256:string，Budget:ResourceBudget，SessionCount/ConcurrencyPerSession/ColdSampleCount/WarmupIterationCount/MeasuredSampleCount/MinimumCompleteSampleCount:int，SampleDeadline/RunDeadline/DrainObservationTimeout:TimeSpan，LoadCase:string，TargetSource:string?。SHA使用§8.4完整bytes，版本v0.2；整份Profile按§3.1规则编码（TimeSpan用Int64 ticks，null字符串-1），报告完整Profile hash，不只记录ProfileId。构建提交/快照、CPU/内存/OS/当前DPI/.NET实际runtime写为单独运行envelope元数据，不伪造环境值；同Profile不同环境不混合样本。

固定Profile `DS-Core-Diagnostic-001/r2`：§8.1Budget、§8.4三个完整输入hash；SessionCount=2、ConcurrencyPerSession=1、ColdSampleCount=10、WarmupIterationCount=20、MeasuredSampleCount=1000、MinimumCompleteSampleCount=1000（每Host分别、warm与cold分列）；SampleDeadline=5s、RunDeadline=120s、DrainObservationTimeout=1s、TargetSource=null。LoadCase逐表分别运行；每行独立Profile revision后缀 `-validate/-command/-queue/-fault`，预算相同。queue固定ConcurrencyPerSession=8与LoadCase=queue，同key和different-key另分修订；fault是确定性故障规格：ColdSampleCount=0、WarmupIterationCount=0、MeasuredSampleCount=20、MinimumCompleteSampleCount=20，用MemoryTimeProvider并标SyntheticTiming，不输出真实耗时分位。不能跨LoadCase合并P50/P95/P99。这些数值仅有界诊断计划，不是客户或生产性能达标阈值。

| LoadCase | 输入/到达模型与资源 | 精确测点/判定 |
|---|---|---|
| validate | 两无UIHost分别循环完整Theme/Policy/State，串行闭环；另按固定128 tokens/nodes容量变体验证；128变体固定保留11色+6间距+3字体+1图标，再增107个额外Typography（ID Extra000..Extra106、font.system、14 DIP/400），共128；129为再加Extra107，输入hash按完整字段重建且独立Profile记录 | API调用前timestamp→Validate返回后timestamp；纯计算资源已归还于返回，N/A native排空；每次结果与§8断言相符 |
| command | A/B各一个即时内存port，串行闭环：只有Query Completed/ResourcesReleased后才提交下一唯一ID；每100次发布一次递增State/Theme，20次重复请求分列 | Submit进入→接纳事件timestamp；CommandAccepted timestamp→ResourcesReleased timestamp为端到端；Started→ResourcesReleased为执行；误拒绝/Unknown单列 |
| queue | 每Session同key8次burst，第9次预期超限；固定顺序释放闩锁，只在第一请求Started后发剩余，两个Host同时；另不同key2并发独立LoadCase | queued=Accepted→Started；GetUsage队列峰值<=8、active+sync<=2、records<=32、events<=64；预期拒绝不是性能成功样本；每Host固定1000个burst并逐请求保存原测点（n是实际完整请求数，不把burst与请求混算） |
| fault | 每20次固定轮流：queued取消、running取消、execution 2s到期、Close 1s观察超时，有限闩锁在故障观察后由测试释放；旧epoch/游标过期/重复冲突单列；另违约资源false在隔离负例进程 | 取消时间→真实port退出→取消Task退出→ResourcesReleased；Close开始→全部计数归还；观察超时和未排空删失单列、不结束统计为PASS；违约不运行完整样本分位、不等待无限Dispose |

性能用System TimeProvider单调timestamp，测试确定性故障用MemoryTimeProvider并将该用例标SyntheticTiming（不得混入真实耗时分位）。Core事件timestamp取其发布原测点；不得把宿主轮询Query延迟当ResourcesReleased原时刻。同burst最长事件少于64，读取事件后保存本轮原值至测试有界数组；任何CursorExpired导致无法取全测点，该样本删失/非完整并列出，不猜时间。1000样本只保留预分配有界统计数组，历史request记录始终按§3容量淘汰，不为benchmark绕开预算。RunDeadline到达只终止观察/回报非零未完成，再按Owner槽真实收尾；隔离进程结束不是资源真实归还。

对port注册/参数大小边界、端口目录MaxTokens、同步port占位、取消原Task、有限CTS/timer、旧scope/epoch与不同语言输入分别记录预期拒绝/故障，不把它们默默删掉后只报成功样本。采样记录CPU/进程工作集/PrivateMemory/managed allocation+GC、GetUsage中pending/active/sync/cancellation/records/events/snapshot encoded bytes；BCL Process计数与GC.GetTotalAllocatedBytes只报告进程总量/区间增量，不归因成单请求allocation。

所有阈值来源：正确性/数量硬上限为§3/§8断言与显式Budget；测试5s/120s仅测试保护；实际时延/CPU/峰值内存/长稳阈值TargetPending，统计结果NotEvaluated，不能由1000次诊断测量自行冻结性能PASS。最低完整样本不足或任何排空未知时保留失败/删失与统计n，不声称达标。P50/P95/P99及端到端口径只采用DEV-GOV-010 §3.1，不复制第二套分位算法。

### 10.2 UI负载 fixture 完整格式、默认Host与测点

UI fixture是测试自有只读数据格式，不进入Core的产品DTO；只有显示输入/原Owner投影，不伪造设备测量/质量事实。`UiFixture` record字段依序为SchemaVersion:int=1、HostKind:string=A或B、Revision:long=1、Rows:ImmutableArray<UiRow>、Points:ImmutableArray<UiPoint>、SourceRef:string、SourceVersion:string。`UiRow`字段顺序为Id:string、ObjectId:string、DisplayValue:decimal、Unit:string、State:ViewState、Revision:long、SourceRef:string、SourceVersion:string；`UiPoint`为Id:string、TimestampTicks:long、DisplayValue:double（有限）、Unit:string、SourceRef:string、SourceVersion:string。集合按ID Ordinal编码；decimal按Decimal.GetBits的lo/mid/hi/flags四Int32小端完整编码（fixture只scale=0，zero为+0），double与string/array沿§3.1规则；内容定义/完整编码和UI模型的列/轴名均固定，不使用随机生成或共享mutable列表。输入hash对完整fixture bytes计算，不能只hash规模/前10行。

确定性生成：Normal为Rows=100、Points=1000；Pressure为Rows=100000、Points=100000，恰好§6.7诊断上限。row index i=0..N-1，ID=`row-`+i.ToString(D6,InvariantCulture)，ObjectId=`object-`+同D6，DisplayValue=decimal(i%100)（原整数，scale=0），Unit=mm，State循环Ready/Busy/Empty/Stale/Blocked/RecoverableError/PermissionDenied/Completed（enum i%8），Revision=1，SourceRef=synthetic.ui、SourceVersion=fixture-r1。point index j=0..M-1，ID=`point-`+D6，TimestampTicks=638712864000000000+j*10000000（UTC点时间，仅展示、非deadline）、DisplayValue=double(j%101)整数、Unit=mm、SourceRef/Version同row。Fixture.SourceRef=synthetic.ui、SourceVersion=fixture-r1；A/B仅HostKind不同，所有字段必须记录且比较。行/点是合成显示量，不声称来自测量或上游算法通过；压力图表只显示全量数据的宿主给定显示窗，不在本包降采样。

完整UI fixture Golden（全部记录、全部字段，不是前若干行子投影；合成数据，非真实生产输入）：

| Host/负载 | 完整规范bytes | SHA-256 |
|---|---|---|
| A/normal | 77555 | `7934347ce13c8834b7922c19bc15b31792c346cb6bb6153b4edcebfc3de3f2fd` |
| A/pressure | 16300055 | `1fe16088e46199fd2abc07af84c429890fd6b6f3a45aa0bd99f2ff5948829550` |
| B/normal | 77555 | `3a1c7f89e440ddd0c8ab7d08fd1581152aeaeae1165a63a79e36903b5e40069e` |
| B/pressure | 16300055 | `f14091aafae5280311fe24ce68de2f7c3e0870880186ccf06256c512578ab394` |

正常/压力均由上述公开字段生成规则唯一重建，不在正文写十余MiB hex或新建并列报告。测试必须逐字段独立重建整个fixture并比bytes长度/hash；改变Row/Point的SourceVersion、单位、HostKind等任何字段均改身份，不能只用N/M作为hash。64MiB夹具编码budget高于pressure完整bytes，但真正UI对象峰值内存另测，不能拿编码字节当实际进程占用。

先做数量/编码上限计数再构造ImmutableArray；row/point超MaxDataRows/MaxDisplayPoints拒绝DS-RESOURCE-002，decimal/时间/ID/source任一非法拒绝带path。Input bytes由benchmark的有界测试统计buf持有（完整压力fixture约数十MiB，单独Profile给MaxFixtureBytes=64MiB、checked写入stream），不借用Core MaxSnapshotBytes限制整个Grid数据源。只当前可见节点构造AutomationCatalog；UI Core Budget从§8.1复制并显式MaxAutomationNodes=256（其它Core数量仍原值），数据源不塞进Core主题/状态DTO。工艺数据ObjectId只有模拟列投影意义，不能重写质量State。

UI Profile唯一ID=DS-Wpf-Host-A-normal/r1、DS-Wpf-Host-B-normal/r1、对应pressure/r1；Contract=v0.2，输入按上述生成规则与§6.6manifest资产身份、模板资源hash、localization CatalogRevision一起记录，未创建实际发布资产时ManifestHash=NotBuilt、TemplateHash=NotBuilt，禁止合成SHA冒充正式资源。实际实施benchmark必须补算完整fixture bytes/hash和真实资源hash；输入生成规则本轮已冻结，不转成“以后决定数据字段”的待门。ColdSampleCount=5（新Host/root）、Warmup=5、Measured=100次主题/语言/复位循环，每轮deadline5s/关闭观察1s，UI整轮有限run=120s、独立cleanup=5s；超限/未排空未完成返回非零，真实Latency/内存目标TargetPending/NotEvaluated。

两默认PageContract（本模块测试Host规范，生产PageContract由宿主按产品事实扩展）固定：工作区宽高由1920×1080当前OS有效viewport扣边框/title/taskbar，换DIP；顶部40DIP命令栏、底部28DIP状态栏，center可用高度R。A Dock外层垂直LayoutGroup：center水平(image DocumentGroup+inspector LayoutPanel)，results在下方默认Height=min(220,R/3)；inspector Width=min(320,centerWidth/3)。B同树但results用Tab组results/trend，初始选results，参数Content由parameter-editor模拟控件slot而非私表。实际Dock项以构造时x:Name=regionId绑定明确实例映射，Caption用§6.1.2对应key；image/commands/identity/state不允许Close/Hide；inspector/results可关闭/浮动，工具栏ResetLayout永远可见。可用宽<1000DIP时inspector与results进入同侧tab不强压图像或主动作；可用高<600DIP时results折叠且快捷键/显示入口可达。生产更复杂树不被本Host自动授权。浮动位置按有效工作区clamp，offscreen恢复直接ResetDefault，不迁设备窗口。

语言/主题模式：每Host独立localization scope，A初始zh-CN+EngineeringLight、B初始en-US+ImageDark；按zh-CN→zh-TW→en-US→原语言顺序与Light→Dark→Light循环，scope.IsCurrent/Theme Query明确记录逐region结果；A换主题不能改变B，两个Host按同一受控表验AutomationName/Help/Text/SuperTip。供应商原生过滤/summary（日历若无控件不强建）必须实际打开才可计ActualRegions；未登记区域明确NotSupported，不拿宿主文字表证明其全部翻译。

测点：host资源加载、Core发布、每region Dispatcher开始→callback退出、观察回执返回、首屏可交互、Grid虚拟化滚动、语言/主题响应、Core/Language/Theme/Layout各自关闭排空；记录UI线程Dispatcher延迟、CPU/managed/native峰值、事件桥轮询/呈现合并、活跃region/subscription/root/DispatcherTask计数。Core/语言测量边界不混成一次原子UI成功。只固定1920×1080与当前DPI，不改用户显示设置或另跑矩阵；产品影像/算法/HALCON/设备节拍不在本UI fixture。

## 11. 版本兼容、发布、迁移与回退

采用语义版本：Core 公共类型/错误码/事件顺序的破坏性变化升 Major；新增可选字段、Token 或事件升 Minor；修复不改语义升 Patch。WPF/DevExpress 适配器的 DevExpress 主次版本绑定在包元数据中；适配器依赖范围在发布清单中显式冻结，符合该范围的升级无需联动；破坏性Core变更须更新适配器接入/清单，不承诺任意版本互兼容。

每个发布包必须携带：包版本、目标框架、依赖闭包、Contract 版本、Token/资源目录版本与 hash、支持的 DevExpress 版本、迁移脚本版本（如有）、构建提交和回退包引用。宿主启动时先检查兼容矩阵和资源闭包；不兼容时在启动诊断中明确缺项并阻断加载，不静默降级。

供应商/框架升级的门禁只验证本模块责任：先做公开 API/程序集快照，再做 Token/资源、绑定、命令状态、DPI/本地化、Automation 和资源生命周期回归，最后做两个消费者的视觉基线和性能对比。该门禁只在明确批准的升级任务中触发，不阻断当前已冻结的 DevExpress 25.2.3 切片。不得以构建成功推断升级安全，也不测试或重造 DevExpress 内部实现。视觉基线由明确批准的变更更新，普通 CI 只读比较；模块公开 API 不泄漏供应商类型，宿主可在模块边界外使用其它控件，但本模块提供的适配器只绑定依赖清单中的 25.2.3。

布局和资源迁移必须是纯函数或可回滚事务：读取旧快照 → 校验 → 生成新快照 → 试运行验证 → 原子替换。任何一步失败保留旧快照。回退顺序为停止新命令、排空、恢复旧程序集/资源/布局、健康检查、重新开放；未知命令结果需由原事实 Owner 查询，不能重放 UI 命令。

## 12. 实施顺序与准入使用

1. 本永久原会话按§14/§14.2完成当前全部批准能力的内容自审，总控仅登记状态；文档准备、逐切片准入与实际实施授权分别记录，不能由本页自审自动开工。
2. S1实现纯值/校验/布局与标识，按附录唯一工程及测试入口运行；不先加Session/UI依赖。
3. S2在同一Core实现typed注册/队列/查询/事件环/真实排空，先用两个无UI内存Host和闩锁验证全部S2断言；WPF未完成不阻断本纯Core切片。
4. S3/WPF主题模板/语义控件、S4/DevExpress布局和供应商控件映射分别编译与实测；正式语言接入复用localization契约，不依赖隐式全局上下文。
5. 最后由平台Host与独立测量Host串行集成、采纳真实PageContract/资源和Profile，完成视觉品质、三语/键盘/UIA、长稳、性能、布局回退与发布验收。

测试与性能发生在对应实现之后，是代码/发布资格门，不能倒写成“全部运行验证后才准许开始实现”。当前指导修订不创建项目、测试文件或产品代码，也不改变任何交付项目的版本/节奏。

## 13. 研究依据、来源与迁移限制

### 13.1 当前权威与既有来源复用

- [PKG-050职责页](../../shared-modules/packages/PKG-050_DesignSystem.md)、[DEV-UI-040](<../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)、[DEV-UI-046控件能力](../../shared-modules/guidance/05-ui/DEV-UI-046_DevExpress高阶能力使用矩阵.md)：职责/页面布局/三语/高阶交互输入，不复制第二套PageContract。本页§3是本模块Core API，语言实际入口仍以[localization](../localization/DEVELOPMENT-GUIDE.md)为唯一权威。
- AsunControl只读快照 `docs/references/project-snapshots/AsunControl/20261004/original/` 既有定向研究：ROI/HalconDrawControl.cs、DrawConfig.cs、DrawFinishEventArgs.cs、ShapeSerializer.cs 的typed事件/完成通知和旧数值控件交互只借思想。其WinForms线程/吞异常/无版本二进制/视觉对象持有/混合业务命令不复制。本轮不扫描AsunImage内部，也不重审无关参考代码。

| H:\docs来源（2026-10-06既有定位研究） | 原件SHA-256 | 本页实际采纳/排除 |
|---|---|---|
| `40-development/10-ui/UI设计系统与高级控件开发指导.md` | `396deb01ee00fd4c06bd9a8effece3c52c034a37f2876b06f8ab72b4b66e03b8` | 版本化Token/资源身份、文字+图形、shortcut作用域、UIA窗口边界、供应商显式升级门；§3/§6/§11。生成器没有批准消费者，不属当前范围，来源愿景不构成模块准入。typed递归validator/undo、降采样、任务checkpoint/报警事实回各原Owner，不再纳入本包 |
| `40-development/10-ui/全页面PageContract与高保真交互规格.md` | `78ab3c695a51c2b6ecd5817e9b87c255eace2a70b80340f706915d9d8bdd3e07` | 稳定AutomationId/context/revision、Unknown查原请求不换key重放、空/忙/过期/冲突/拒绝呈现，§3/§6/§8。AOI目录/BoardRun/配方/客户比例/工艺阈值/机器性能不迁入 |

原件保留于既有PCBA-AOI来源清单 `docs/references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json`；本表只记录本职责范围采纳，不声称整篇或当前原件已重新全审。HALCON24.11/来源客户验收不转为本平台26.05或本包运行证据。

### 13.2 DevExpress固定源码、测试与取舍（2026-10-10）

公开仓库 [DevExpress.Mvvm.Free](https://github.com/DevExpress/DevExpress.Mvvm.Free/tree/3558088c0fc337e701f2585c2a6ef0df88bef71f) 固定commit=`3558088c0fc337e701f2585c2a6ef0df88bef71f`（git ls-remote取得，按该commit读取codeload原件，无文件落库/依赖安装）；LICENSE为MIT。实际读源码/测试/工程：

| 原件路径（固定commit） | 观察及转用 | 限制 |
|---|---|---|
| [UI/Services/DispatcherService.cs](https://github.com/DevExpress/DevExpress.Mvvm.Free/blob/3558088c0fc337e701f2585c2a6ef0df88bef71f/DevExpress.Mvvm.UI/Services/DispatcherService.cs) L26–53 | 无延迟路径返回Dispatcher.BeginInvoke的Task；定时路径动作执行后SetResult。§6要求真实callback退出回执 | 延时动作异常未见finally保证SetResult，不把该timer照抄为取消/关闭实现；ServiceBase/隐式Dispatcher不移入Core |
| [DispatcherServiceTests.cs](https://github.com/DevExpress/DevExpress.Mvvm.Free/blob/3558088c0fc337e701f2585c2a6ef0df88bef71f/DevExpress.Mvvm.Tests/Services/DispatcherServiceTests.cs) L52–99 | 测试明确入队时动作尚未发生，等待/continuation后发生；§8.3加入Dispatcher阻塞/未退出反例 | 旧测试DoEvents/timing不是本平台热切换/排空证据，未执行上游测试 |
| [Native/AsyncCommandFactory.cs](https://github.com/DevExpress/DevExpress.Mvvm.Free/blob/3558088c0fc337e701f2585c2a6ef0df88bef71f/DevExpress.Mvvm/Native/AsyncCommandFactory.cs)、[DelegateCommandTests.cs](https://github.com/DevExpress/DevExpress.Mvvm.Free/blob/3558088c0fc337e701f2585c2a6ef0df88bef71f/DevExpress.Mvvm.Tests/DelegateCommandTests.cs) L523–841 | Factory显式参数与CanExecute/AllowMultipleExecution；CancelAndWaitTest在Cancel后IsExecuting仍true、任务退出后false，ExecuteAsync异常有faulted Task；§3–4/§8保留Pending/取消/释放差异 | 工厂reflection/Wait/全局CommandManager不移入Core；这些测试不证明设备停止或业务幂等，不把AsyncCommand当资源receipt |
| DevExpress.Mvvm.Wpf.NetCore.Desktop.Free.csproj / UI及测试对应csproj | net8.0-windows、WPF/WinForms、内部工程引用；测试NUnit3.13.0/Adapter3.17.0/TestSdk16.8.0及System.*依赖 | 只借行为/测试思想，不引入该包/测试栈，不更改本项目net10/BCL测试与已安装25.2.3 |

两条路线比较：直接沿MVVM命令/任意观察回调管理Core，依赖UI上下文且取消/关闭容易互等；采用本页typed port+Query+有界事件环，Core headless、结果/资源可查、慢观察者无排空权。选择后一条；代价是宿主须处理CursorExpired并重取快照、事件不是无限永久日志。UI命令仍可用本机DevExpress能力，不重复实现供应商ICommand内部。

### 13.3 官方 API 与显示标准

- 25.2.3本机官方XML来源：Core/ Grid / Docking / PropertyGrid / Charts对应 `Offline Packages/devexpress.wpf.<package>/25.2.3/lib/net8.0-windows/DevExpress.Xpf.*.v25.2.xml`；精确成员与约束已落§6.3，Theme Get/Set、Bars/Popup/超级提示、Dock/布局、Grid/Tree、PropertyGrid/Chart均定向查阅。当前没有dxdocs callable，DevExpress官网WPF页面2026-10-09访问403，不以403推断不支持，也不反编译供应商弥补。签名文档不等于真实WPF编译/热更新/关闭验证。
- 微软 [WPF Threading Model](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/advanced/threading-model)，2026-10-10访问200：Dispatcher.InvokeAsync/BeginInvoke排队，Task.Wait可能死锁；§4/§6规定显式Dispatcher/异步等待/真实callback退出。微软 [UiaReturnRawElementProvider](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationcoreapi/nf-uiautomationcoreapi-uiareturnrawelementprovider)，同日访问200：WM_DESTROY中清理窗口provider映射，落§6.5，普通UserControl不装native桥。
- W3C [WCAG 2.2 SC1.4.3](https://www.w3.org/TR/WCAG22/#contrast-minimum)、[SC1.4.11](https://www.w3.org/TR/WCAG22/#non-text-contrast)及relative-luminance定义，2026-10-10访问200；4.5/3对比及sRGB公式落§3.2。它只支持显示token规则，不证明实控件/DPI/屏幕读器验收。
- 复用已固定.NET源码证据：runtime v10.0.0 commit=`60629d14374c56f1cb51819049ad1fa529307f8d`、WPF v10.0.0 commit=`72ca82c7a0f57eb8d0168246468b9cc1a6c14a5a`，MIT；原件位于既有 `.work/localization-method-study-20260929/sources/`。本轮定向读ResourceManager源码/ResourceManagerTests/测试csproj、WPF工程文件，不重新下载或全审。资源查找测试含MissingManifestResourceException/显式culture/缺key，支持§6明确PKG-003资源Owner/缺词回执，不能用ambient文化保证实例隔离；其xUnit/RemoteExecutor/WPF内部依赖不迁入本Core。

上述资料是API/设计/测试思想证据，均未执行源项目测试，不推导本平台构建、性能、视觉算法或生产通过结论。

## 14. 逐切片 DEV-GOV-010 §3.1 最终内容自审与未关闭门

Owner统一为IM-061 design-system模块Owner；平台PageContract/事实与权限Owner为宿主，语言Owner为localization，字段/草稿Owner为parameter-editor，工作台会话Owner为measurement-workbench。共享文件由主会话串行接收，本会话不修改它们。本次2026-10-12已完成两个有限视角逐链走查与本页定向检查；仅声明正文可决定内容，不以结构检查替代六项内容判断。本页版本升级是已委托的技术规格修订，不把产品事实或客户物理指标冻结。

S1于2026-10-11已经主控按正文六项与完整77/468/225-byte Golden独立复算接收，状态 `ModuleCoreImplementationReady`（仅规格准备；未创建/运行产品工程）。主控随后回读0.5.0-prep，接收S2 Factory前根槽/port预登记、首次Close前异常、两轴有限恢复与公开两Host的六项规格，S2状态同步为 `ModuleCoreImplementationReady`；S1原接收保持。Core契约v0.2及Golden不变。

主控已限定接收S3/S4的§6.1–6.7、§7.1–7.2、§8.6、§10.2与本节指导内容：模板PART/三语/Automation受控region、manifest与批准资源、单向工程依赖、主题回执、布局CAS/原写Unknown查询/可信迁移、双STA与负载。主控独立按字段重建四组UI fixture，完整77555/16300055 bytes及全部SHA-256一致。该接收只涵盖指导规格，S3/S4仍 `PreparationIncomplete / NotReady`，不能提升为纯Core之外Ready；总体仍DesignReview/Prep，不自动授权产品编码。UI运行门与内部规格分开，现已决定模板组成/资源schema/目标region/布局/CAS/fixture，不再拿未运行UI掩盖内部欠账。

| 切片 | 1 边界/第二消费者 | 2 API/Owner/资源 | 3 最小Host/可调用 | 4 具体反例/恢复 | 5 Profile/预算/分位 | 6 工程/顺序/后续门 | 内容结论 |
|---|---|---|---|---|---|---|---|
| S1 Token/布局/状态/标识 | §1–2 | §3.1–3.3唯一v0.2 | §7纯BCL | §8.2 DS-S1-01..08 | §8.4/§10.1完整Golden与预算 | 附录唯一Core/test | 主控已接收ModuleCoreImplementationReady；本轮不重新改其字段/Golden |
| S2 typed意图Session/模拟port | §1–2/§3.4不承担设备/业务幂等 | §3.4–3.5/§4类型、错误、同步占位/CancelAsync/原Task及资源闭合 | §7.1实际A/B入口、Factory前2槽、CTS/port真正预登记、部分构造失败/初次Close恢复，B无Shell | §8.2/§8.6 S2关闭前异常/迟到/业务与cleanup分离 | §10.1确定性负载/有限deadline/数量/释放计数，TargetPending保留 | Core/Test同S1；后续实port事实权限和业务集成单独门 | 主控六项规格已接收ModuleCoreImplementationReady；仅规格准备，未build/run |
| S3 WPF语义模板/资源reader/region | §6.1参数/数据Owner与两Host | §6.1.1/6.1.2模板PART/DP/三语/Automation，§6.6manifest/Reader/ApprovedAssets，UiBudget位Wpf | §7.2真实Host准备链有界root；S1/S2不需UI；S3 reader无隐藏窗口，控件constructor无任务 | §8.3/8.6缺PART/IME/缺词/缺资源/循环bind/超预算/浮动关闭 | §10.2完整normal/pressure生成字段/编码/四个完整Golden hash、固定1920实际DPI | 附录Wpf/Host；Generic.xaml实施路径、资源manifest schema/ApprovedAssets、真实资产hash实施时计算 | 主控限定指导内容已接收；PreparationIncomplete / NotReady，真实WPF资格未通过，不标产品Ready |
| S4 DevExpress主题/布局/联动 | §6.3只映射，无语言/统计/领域事实Owner | §6.4/6.6主题构造/Query/回执/可信Mapping/root，§6.7显式projectionHost捕获/默认复位、完整layout envelope/CAS/store/迁移/恢复 | §7.2双Host引用本机25.2.3，显式manager/Dispatcher/store/root；core不受依赖安装阻断 | §8.3/8.6 trusted/hash/迁移冲突/CAS Unknown/恢复失败/关闭迟到 | §6.7有界stream/记录/region，§10.2完整负载与逐阶段测点，目标值NotEvaluated | 附录DevExpress/Host与允许路径；真实两Host UI/发布/回退另门 | 主控限定指导内容已接收；PreparationIncomplete / NotReady，未实际25.2.3编译/运行/性能 |

Token catalog生成器无批准消费方，明确不在本轮范围、不建工程、不以其缺失拖延S2/S3/S4；宿主已提供§6.6确定格式即可集成资源。本轮指导内容接收已同步；真正残余门：实施授权/权威代码基线，实施后真实资源与模板hash、实际build/run、三语/字形/IME/键盘/UIA/Native弹窗覆盖、双Host/长期排空/布局回退、消费者性能目标与现场用途验收。它们不能反推本轮发生过运行PASS。

### 14.1 最终自审关闭的缺陷与保留限制

- 接入实现者视角：删除sealed record继承冲突与未定义Dip/DurationMs/LocaleContext/泛化Payload；统一方法/字段/namespace/Owner，强类型port+明确单位，§7例子不再调用不存在的工厂。S2首次关闭前Owner恢复与S3/S4模板/资源/布局/负载在当前正文闭合；生成器无批准消费方，明确非本轮交付，不虚构待门。
- 桌面交互/恢复视角：Session/request状态分离，取消不关闭Session；事件环/Query代替任意外部回调，避免终态回调与排空自依赖；Core发布与WPF逐区域应用/退出分开，setter局部失败不能声称原子回退或完整本地化。
- 已移除字段validator/undo、趋势降采样、步骤恢复、报警生命周期和证据核验的重复Owner；禁止质量/设备权限进入呈现包。固定1920×1080当前实际DPI，不安排其它分辨率/DPI矩阵。
- 本轮仅修订本页，定向检查不等于API编译或运行资格。预算规范编码Golden、两个Owner槽/原Task、同步端口占位、CancelAsync真实退出和主题bridge依赖方向均已在正文闭合；本轮S2新增实际pre-Attach/初次Close/部分构造失败/业务-cleanup分离，S3/S4新增模板、三语、region、manifest、可信Mapping、布局CAS/迁移/有界stream与完整UI负载，两个有限视角沿正常与异常链走查，未见需实现者临时猜测的范围内字段/调用。实际Core build/run、真实.NET10/WPF/DevExpress、字体/图标、三语/IME/键盘/UIA、两产品Host、性能/长稳/发布回退均未执行；HALCON/设备/HIL对本包纯呈现Core不适用，产品宿主对应门另计。

### 14.2 整模块范围结论、Owner 与资格边界（2026-10-12）

当前批准能力包括 S1 Token/快照/布局值、S2 typed Session/命令意图/排空、S3 WPF 模板/资源/三语/UIA、S4 DevExpress 主题/布局/联动，以及两个消费者的 Host 装配规则。逐项回读 §1–§12、§6.2.1 的 viewport slot 边界、§6.6 的资源闭包、§6.7 的显式宿主布局捕获/默认复位/CAS/迁移、§7.1–§7.2 的正常/失败/关闭链和 §8.6/§10.2 的可判定负载后，**本模块目前没有可由软件设计者继续决定的欠账**：公开输入、输出、单位、Owner、失败状态、原 Task/资源责任和恢复路径均已冻结。影像 viewport 不属于本模块直接装配；实际消费时由宿主按 [viewport 0.3.5-prep §10.6–10.9](../viewport/DEVELOPMENT-GUIDE.md#106-公开bindingunbind与presenter借用) 完成，未消费时明确 `NotApplicable`，不会形成隐藏依赖或待猜 API。

剩余工作是实施和外部资格门，各有明确 Owner：

| Owner | 仍需完成的工作 | 本页状态 |
|---|---|---|
| IM-061 design-system 模块实现 Owner | 在获准工程内实现 Core/WPF/DevExpress，按本页入口、反例、Golden、有限关闭和第二消费者断言验证 | 代码/编译/运行未执行 |
| 平台与独立测量 Host Owner | 提供真实 PageContract、root/STA、viewport slot（如消费）、权限/事实投影、真实 Profile，并负责宿主级窗口与产品联动 | 本页仅冻结接线和模拟 Host |
| localization Owner | 提供 CatalogRevision、三语资源闭包、实际控件/native surface 回执和缺词恢复 | 未做真实资源加载/字形/IME验收 |
| DevExpress 适配器与发布 Owner | 绑定本机 25.2.3、编译模板/字体/图标、布局 store 与可信迁移，产出真实资源 hash 和回退包 | 未做真实编译、发布、回退 |
| parameter-editor / measurement-workbench / viewport 原 Owner | 继续拥有字段校验/草稿、工作台事实、viewport binding/renderer/lease；本模块只消费其显式投影或 slot | 本模块不代行其事实和资源责任 |

本轮修正资源模板的完整hash/Kind/原bytes有界闭包、manifest显式policy、S3 ToolTip/S4 SuperTip的单向依赖、布局projectionHost实际捕获/默认树复位和viewport外部slot边界；这些是范围内软件设计修复，未把内部设计欠账转给客户或设备。修订后按实现者正常链与桌面失败/恢复链两种视角回读。本轮自审只执行文档级检查：目标文件的章节/锚点/代码围栏/公开类型与调用名定向检索，资源与 viewport 边界逐字段回读，以及 `python tools/validate_docs.py` 的范围、链接、依赖 DAG 和消费者映射检查。旧 Core/UI Golden、已接收研究和向量未重复全算；未执行 C# 编译、WPF/DevExpress 运行、真实 manifest/font/icon hash、三语字形/IME/键盘/UIA、viewport renderer/GPU/HALCON、性能/长稳、布局 store 实写、现场/HIL/计量或生产验收。因此本页仍为 `DesignReview / Prep`；S1/S2 仅保持规格 `ModuleCoreImplementationReady`，S3/S4 与整模块不提升为实现或生产 Ready。


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

## 附录 A：切片绑定与最小工程（引用唯一 Module API Contract v0.2）

### Core implementation binding

- `NewProjectRequired`。唯一Core：`src/Modules/design-system/Asun.Modules.DesignSystem.Core/Asun.Modules.DesignSystem.Core.csproj`；namespace=`Asun.Modules.DesignSystem`；唯一Core测试：`tests/Modules/design-system/Asun.Modules.DesignSystem.Core.Tests/Asun.Modules.DesignSystem.Core.Tests.csproj`。项目尚未创建。
- Core为Microsoft.NET.Sdk/net10.0；测试同SDK/net10.0/OutputType=Exe，仅ProjectReference上述Core与BCL。S1/S2共享同一契约/工程，不创建另一份Core或第二套DTO。
- 获准S1/S2实施的允许范围仅上述Core和Core.Tests目录；禁止其它模块src/tests、产品Shell/Domain/Integration、AsunImage内部、只读来源/快照。共享Solution/build引用须主会话串行处理，不擅写。
- 构建命令：`dotnet build src/Modules/design-system/Asun.Modules.DesignSystem.Core/Asun.Modules.DesignSystem.Core.csproj -c Release`。
- 验证命令：`dotnet run --project tests/Modules/design-system/Asun.Modules.DesignSystem.Core.Tests/Asun.Modules.DesignSystem.Core.Tests.csproj -c Release`；以§9退出码/有限截止接受，不能用dotnet test空成功代替。
- 同一测试入口支持参数 `--slice S1` / `--slice S2` / `--benchmark DS-Core-Diagnostic-001`，无参数执行当前已实施的全部切片断言；未实施且未授权切片在输出声明NotImplemented，不能计PASS。S2参数隐含先验证S1，benchmark必须先全部已实施正确性通过，再逐LoadCase测量。运行示例：`dotnet run --project tests/Modules/design-system/Asun.Modules.DesignSystem.Core.Tests/Asun.Modules.DesignSystem.Core.Tests.csproj -c Release -- --benchmark DS-Core-Diagnostic-001`，不使用--no-build遗漏测试构建。
- 工程创建前绑定权威代码仓库/分支或批准可审计快照；当前本目录无Git不阻断文档修订，也不声称HEAD/构建通过。

### WPF / DevExpress 后续切片绑定

- S3唯一工程：`src/Modules/design-system/Asun.Modules.DesignSystem.Wpf/Asun.Modules.DesignSystem.Wpf.csproj`，namespace=`Asun.Modules.DesignSystem.Wpf`，net10.0-windows/UseWPF=true；引用本Core，语言接入按localization公开契约引用其对应Core/Wpf工程，不能复制其DTO。
- S4唯一工程：`src/Modules/design-system/Asun.Modules.DesignSystem.DevExpress/Asun.Modules.DesignSystem.DevExpress.csproj`，namespace=`Asun.Modules.DesignSystem.DevExpress`，net10.0-windows/UseWPF=true；引用本Core/Wpf和本机25.2.3对应程序集，不从NuGet下载。
- 真实UI测试Host：`tests/Modules/design-system/Asun.Modules.DesignSystem.Wpf.Tests/Asun.Modules.DesignSystem.Wpf.Tests.csproj`，net10.0-windows/UseWPF=true/OutputType=WinExe；同Host装配平台投影与独立测量投影两模式。模块UI实现路径仅上述Wpf/DevExpress与Wpf.Tests目录，待各自切片准入与明确实施授权后才可写入。
- 后续build命令分别使用上述Wpf/DevExpress工程 `dotnet build <工程> -c Release`；启动WPF验收Host使用 `dotnet run --project tests/Modules/design-system/Asun.Modules.DesignSystem.Wpf.Tests/Asun.Modules.DesignSystem.Wpf.Tests.csproj -c Release`，真实交互/资源/视觉验收按§6/§8.3/§9逐项记录，不把启动成功当完成。
- 当前状态：S1/S2六项规格已由主控接收，ModuleCoreImplementationReady（仅规格准备）；S3/S4限定指导内容已接收，真实WPF25.2.3/资源发布hash/字体图标/UIA/IME/性能与产品资格未运行，仍PreparationIncomplete/NotReady，不提升纯Core之外Ready；生成器不在当前范围。整模块文档结论见§14.2，不等待总控内容审核；状态登记、实施授权、实际构建/测试、产品集成与生产资格分开，不因登记accepted或链接检查通过而升级状态。
