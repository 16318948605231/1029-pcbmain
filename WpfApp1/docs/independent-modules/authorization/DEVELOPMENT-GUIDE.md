# 身份授权与审计端口独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`AU-C1, AU-C2, AU-C3`

- 模块：`IM-004 authorization`；历史映射：`PKG-004 / SM-004`
- 版本：`0.3.3-prep`；修订：2026-10-11
- 状态：AU-C1～C3 为 `ModuleCoreImplementationReady`（仅规格准备，主控于 2026-10-09 接收）；AU-W1 确定指导内容于 2026-10-11 限定接收，真实运行资格仍 `PreparationIncomplete / NotReady`；AU-I1 产品资格仍 `PreparationIncomplete / NotReady`，保持 `IntegrationBlocked`
- 永久会话：`01a10306-e37a-70b0-9389-81b79aed8bf7`
- 任务：`IM-REVIEW-20261009/authorization`
- 目标：C# / .NET 10 无 UI 核心；可选 WPF / DevExpress 25.2.3 授权原因投影
- 模块级设计评审态：`DesignReview`（方案可评审）。§12.4「当前架构全部批准范围的最终准备结论」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本页是本模块唯一实施正文。模块内 Contract v0.1、步骤和断言在本页冻结为本轮设计基线；主控已接收 AU-C1～C3 的 DEV-GOV-010 §3.1 六项文档规格，状态见 §12.3。这是核心规格准备接收，不是正式平台 C-01～C-08、产品集成批准或实现证据。技术选择不再全部挂在“以后由 Contract Owner 决定”：模块自身契约由本页定义，平台映射、生产凭证及宿主提交原子性分别保留准确的后续门。没有创建产品代码、执行外部测试或声称性能/生产通过。

本轮完整范围结论见 §12.4：复用已接收 Core/WPF 内容，仅补 §8.1～§8.4 的可信适配接线、提交/撤权协议、审计持久映射与宿主恢复。当前架构批准范围内的可决定软件设计已闭合；AU-I1 的真实来源绑定、实际实现和运行资格仍未关闭，不以此结论授予代码或产品准入。

## 1. 责任、调用方和依赖方向

### 1.1 完整能力

1. 校验**显式**租户、签发方、主体、会话、认证代次、宿主和用途，不从当前线程、窗口或全局账号取身份。
2. 对动作、资源、作用域、修订和用途执行默认拒绝的有界授权求值；明确区分允许、拒绝、输入无效和不能确定。
3. 在提交前获取当前权威快照重新评估；检查会话过期、撤权、策略换代、资源换代和审计写入条件。
4. 按权威策略支持独立第二主体复核：模块只检验两位受信参与者的授权条件，不取得人判或质量放行权。
5. 接收受信来源的失效通知，管理有限规则索引缓存；不缓存可直接提交的 Allowed 决策。
6. 提供授权决策审计、宿主操作结果审计、按原 AuditId 回查和未知结果恢复端口。
7. 提供请求状态查询、取消、请求级排空、实例停止排空、脱敏诊断与可选原因投影。

消费者 A 是生产应用的受控写命令入口；B 是独立复判工具的意见提交入口。两者使用同一 Core/测试契约和不同认证、策略、审计适配器。维护/工程工具以相同入口访问明确登记动作，不能通过”工程模式”默认获权。

### 1.2 排除项和信任边界

模块不实现登录、密码/MFA、账号库、证书/密钥管理、任意策略脚本、关系图授权服务；不解释产品/工单/板件、不作工艺判定、最终人判、质量放行、设备联锁、设备/MES动作或产品事实事务。资源引用是**授权对象**，不是领域对象。Core 不执行宿主回调中的业务副作用。

主体 ID、租户字符串、角色名、AuditReference 或旧 DecisionId 本身均不是凭证。宿主认证适配器通过 `IAuthorityPort` 在可信边界验证来源及当前状态；Core 信任的是被注入的端口响应，不信任 UI 或外部消息自报的”已认证”。跨进程宿主必须在服务端重新认证和核权，不把本地 DTO 当可传输 capability。

未登记动作、空 grant、未知用途/枚举、缺资源/租户或不可用端口均失败关闭。无隐式管理员、无默认批准、无工作站共享口令。生产事实保存成功不等于质量通过；拒绝授权也不改历史事实。

### 1.2A 新架构适配要点

**架构门禁**：`Asun.Authorization.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。Core 只依赖 .NET 10 BCL，可在任何宿主（包括 Blazor Server）中使用。

**Blazor/Web 宿主中的权限上下文**：当 Web 端（Blazor Server + SignalR）执行操作时，权限上下文必须由服务端传入，不从浏览器端取任何安全上下文：
- 浏览器通过 SignalR 发送操作请求时，附上 JWT/Bearer Token
- ASP.NET Core 服务端在 Hub 中验证 Token，提取 `PrincipalId`、`TenantId` 和 `SessionId`
- 调用本模块的 `EvaluateAsync(AuthorizationRequest)` 时使用从 Token 提取的明确身份
- 浏览器端不能自报”已认证”，服务端必须重新核权
- Web 端的只读查询（参数看板、历史记录）与写入操作（参数修改、配置发布）使用相同的授权检查路径

**三态仲裁中的授权**：`ai-inference` 的 `AutoResolved` 终态自动判定必须经授权检查：
- `AutoResolvedPolicy`（允许 AI 自动判定的策略）由本模块管理
- 每次 `AutoResolved` 写入生产事实前，调用 `EvaluateAsync(“ai.auto-resolve”, resourceRef)` 确认策略仍有效
- 人工介入（`NeedsHuman`）由 `human-review` 模块触发，同样需要授权校验复判人身份

### 1.3 组合和所有权

```text
认证/策略/审计的宿主可信适配器
       ↓ 显式构造端口与预算
Authorization.Core（Contracts + 求值 + 协调 + 请求管理）
       ↓ 只返回类型化结果
宿主自己的业务提交门/事务/设备端口
       ↓ 可选
Authorization.Wpf（脱敏结果、原因和恢复意图）
```

Core 仅依赖 .NET 10 BCL；不引用 WPF/DevExpress、产品 Shell/VM/私表、其它模块实现、HALCON 或 AsunImage。不把所有适配器机械拆 DLL；只有有真实发布消费者时建立对应发布单元。

本能力是非视觉事务。授权、二人复核、审计、撤权、恢复各操作均不适用 HALCON 26.05、`ImageLibDotNet.cv2`、图像 ROI、训练或备用算子路线；本轮未读取算子页或 AsunImage 签名，不作”已核对视觉 API”的声明。所谓弱信号/遮挡/退化在此对应身份信息缺失、权威响应不完整、断连与过期，处理见 §9。AsunControl 既有只读检索未定位同类授权能力，不能据视觉控件复用出授权实现。

## 2. 技术路线和来源（实读范围）

### 2.1 已确定路线

采用**显式资源授权 + 有界确切 grant 集合 + Deny 优先 + 缺省拒绝**。生产认证/策略可适配现成 ASP.NET Core 授权服务，端口须补足本模块的租户、当前会话、代次、审计和取消语义；Core 不引用 ASP.NET Core 框架。最小 Host 使用确定性内存权威端口与审计端口，明确标记为合成验证。

比较结论：仅按角色名授权不能阻止水平越权；构建 OPA/OpenFGA 类外部策略产品会引入额外策略语言、部署及一致性责任，本模块当前消费者不需要此范围。选择确切 grants 不是替代企业账号系统：角色/属性/关系映射由现有权威适配器完成。本模块只求值其受信、有限、确切结果，不运行任意表达式或把所有产品策略写入 Core。

### 2.2 固定研究证据与落点

| 来源（2026-10-09 实读） | 版本/依赖/许可 | 可复用内容、局限与正文落点 |
|---|---|---|
| [ASP.NET Core 源码树](https://github.com/dotnet/aspnetcore/tree/7387de91234d3ef751fa50b3d1bfede4130213ff/src/Security/Authorization) | `v10.0.0`，commit `7387de91234d3ef751fa50b3d1bfede4130213ff`；MIT；授权工程引用 Metadata、Logging.Abstractions、Diagnostics、Options | 全文读取 Core 的 DefaultAuthorizationService、DefaultAuthorizationEvaluator、AuthorizationHandlerContext、工程及 LICENSE；读取测试中 ExplicitFail、InvokeHandlersAfterFailure、PolicyThrowsWithNoRequirements、错误用户名案例。借鉴显式 user/resource/requirements、Fail 不可被后续 Succeed 覆盖、空 policy 非允许。§4/§5冻结 Deny 优先。该源码不提供本模块的租户隔离、实时撤权、deadline、审计或提交原子性；测试未运行，不直接复制框架工程。 |
| [OWASP Authorization Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/29994dd8a2e6f50fa3d5607b046b54d7c6945afd/cheatsheets/Authorization_Cheat_Sheet.md) | commit `29994dd8a2e6f50fa3d5607b046b54d7c6945afd`；已读该 commit 的 LICENSE.md：`CC-BY-SA-4.0`；文档引用，非产品代码依赖；本次实读字节 SHA-256 `2888ab0932fdb423d4bd683cb2a0f36e173192f127ed7ab3950269d27bb7ef46` | 实读 Least Privilege、Deny by Default、Every Request、ABAC/ReBAC/Multi-tenancy 和 Logging 章节。§3–§7采用显式租户/作用域、每请求检查和脱敏审计；不把文档中的通用性能比较当本模块实测。 |
| [Microsoft 资源授权](https://learn.microsoft.com/en-us/aspnet/core/security/authorization/resourcebased?view=aspnetcore-10.0)、[托管取消](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads) | 官方说明，访问日期 2026-10-09；非复制代码依赖 | 读取 imperative/resource-based 说明及 cooperative cancellation；§5/§7区分资源授权与页面可见性、取消等待与真实退出。响应中的网页“需授权”外壳不作为安全策略来源。 |
| [原 ReviewClaim 指导](../../references/project-snapshots/PCBA-AOI/20261006/review-claim-recovery/original/docs/40-development/50-ai-review/ReviewClaim安全与幂等恢复协议开发指导.md) | 只读内部原件；SHA-256 `c5fcfbf3b284fae0c65519324ff9219e0c35e9a3ea8bd25effdec3b591dd547a`；定向读取 §1–§7 与契约反例 | 采用“当前授权不由旧回执代替、普通日志不替代安全审计、秘密不入 VM、未知按原 ID 查”的通用边界；不迁入 Case/Board/设备、Held、token 加密、质量/认领流程或原项目验收声明。§6/§9/§10。 |
| [25.2.3 官方公共资料已有摘录](../../../.work/localization-public-surface-study-20260929/source.md)、[本地化接入正文](<../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md#localization-public-surface-method>) | 复用已绑定的官方随附 XML/公开元数据 25.2.3.0，非安装/授权核验 | 本次定向实读 Docking 的 Caption/Content、Core 的 BarItem.SuperTip/SuperTipItem.Content、Grid 的 RuntimeLocalizationStrings 公共 XML。在线 Grid/TableView/Dock/SuperTip 页面均 HTTP 403，无 dxdocs 可调用；据既有目标版本证据冻结 §10 的组合。Grid 表格绑定、Dock 和 SuperTip 实际呈现/内置文字覆盖仍是 WPF 切片编译/行为门，不以 403 认定不支持。 |

上表是来源证据，不是第二份实施正文。关键步骤和字段全部在本页，程序员无需从研究脚本补需求。无新下载快照或过程报告；引用原件保持只读。未运行上游测试，不依据竞品营销推导内部实现。

## 3. Module API Contract v0.1：唯一公开形状

namespace 唯一为 `Asun.Modules.Authorization`。以下 C# 定义是主控已接收的 AU-C1～C3 模块级精确签名，不是现成 API；实现应将同名类型落在 §12 的唯一 Core 工程，不另外生成候选 DTO。集合使用 `ImmutableArray<T>`；接纳前深复制并校验，禁止传可变 ClaimsPrincipal、SDK 对象或 Dictionary 作为认证上下文。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
namespace Asun.Modules.Authorization;

public enum UseKind { Read = 1, Mutate = 2 }
public enum ParticipantRole { Primary = 1, Approver = 2 }
public enum TechnicalAccess { ReadOperation = 1, CancelOperation = 2, AppendHostOutcome = 3, ObserveOperation = 4 }
public enum GrantEffect { Permit = 1, Deny = 2 }
public enum PolicyOutcome { Allowed = 1, Denied = 2, Invalid = 3, Indeterminate = 4 }
public enum CommitEligibility { Blocked = 1, EligibleAtEvaluation = 2 }
public enum AuthorityStatus { Active = 1, Revoked = 2, Expired = 3, Missing = 4, Unavailable = 5 }
public enum AuditStatus { NotRequired = 1, Persisted = 2, Rejected = 3, Unknown = 4, Conflict = 5 }
public enum AuditPhase { Authorization = 1, HostOutcome = 2 }
public enum HostOutcome { Succeeded = 1, Rejected = 2, Unknown = 3, CancelledBeforeDispatch = 4 }
public enum CallStatus { Rejected = 1, Pending = 2, Completed = 3, HistoricalReplay = 4 }
public enum OperationState {
    Accepted = 1, Evaluating = 2, AuditPending = 3,
    Draining = 4, DrainUnknown = 5, Drained = 6, ResourcesReleased = 7,
    Completed = 8, Cancelled = 9, TimedOut = 10, Failed = 11
}
public enum ServiceState { Ready = 1, Draining = 2, DrainUnknown = 3, Stopped = 4 }
public enum StopStatus { Stopped = 1, DrainUnknown = 2 }
public enum ChangeKind { Subject = 1, Policy = 2, Tenant = 3, Resource = 4 }
public enum EventKind {
    Accepted = 1, Evaluated = 2, AuditObserved = 3, CancelRequested = 4,
    Draining = 5, DrainUnknown = 6, Drained = 7, ResourcesReleased = 8,
    OperationCompleted = 9, AuthorityInvalidated = 10, Stopped = 11
}
public enum AuthError {
    None = 0, InvalidInput = 1001, VersionConflict = 1002, SessionExpired = 1003,
    ScopeViolation = 1004, PolicyUnavailable = 1005, PolicyRejected = 1006,
    StaleDecision = 1007, DeadlineExceeded = 1008, Cancelled = 1009,
    Draining = 1010, AuditUnavailable = 1011, AuditConflict = 1012,
    AdapterFault = 1013, ResourceLimit = 1014, AuthorityChanged = 1015,
    ApprovalRequired = 1016, RequestConflict = 1017, NotFound = 1018,
    NotSupported = 1019, DrainUnknown = 1020, SubscriberFault = 3002, InternalFault = 9001
}

public sealed record AuthorizationContext(
    string TenantId, string IssuerId, string SubjectId, string SessionId,
    long AuthEpoch, string HostId);
public sealed record ActionRef(string Id, long Revision);
public sealed record ResourceRef(
    string TenantId, string Type, string Id, long Revision, string ScopeId);
public sealed record PolicyRef(string Id, long Revision, string Sha256);
public sealed record AuthorizationRequest(
    Guid RequestId, Guid CorrelationId, AuthorizationContext Context,
    ActionRef Action, ResourceRef Resource, UseKind Use,
    PolicyRef ExpectedPolicy, string PurposeCode, DateTimeOffset CreatedAtUtc,
    DateTimeOffset DeadlineUtc, AuthorizationContext? Approver);
public sealed record Grant(
    string Id, GrantEffect Effect, ParticipantRole Role, string SubjectId,
    ActionRef Action, ResourceRef Resource, UseKind Use, string PurposeCode,
    DateTimeOffset ValidUntilUtc);
public sealed record AuthoritySnapshot(
    AuthorizationContext Context, ParticipantRole Role, PolicyRef Policy,
    Guid AuthorityDomainId, long Generation, string SnapshotId,
    DateTimeOffset ObservedAtUtc, DateTimeOffset ValidUntilUtc, bool RequiresDistinctApprover,
    ImmutableArray<Grant> Grants);
public sealed record AuthorityReply(
    AuthorityStatus Status, AuthoritySnapshot? Snapshot, AuthError Error);
public sealed record RecheckRequest(Guid PreviousRequestId, AuthorizationRequest Current);
public sealed record AuthorityEvidence(
    ParticipantRole Role, AuthorizationContext Context, PolicyRef Policy,
    Guid AuthorityDomainId, long Generation, string SnapshotId);
public sealed record MatchedGrant(ParticipantRole Role, string Id);
public sealed record PureDecision(
    PolicyOutcome Outcome, AuthError Error, ImmutableArray<MatchedGrant> MatchedGrants,
    PolicyRef? ExpectedPolicy, AuthorityEvidence? PrimaryAuthority,
    AuthorityEvidence? ApproverAuthority, DateTimeOffset? ValidUntilUtc);
public sealed record AuditKey(string TenantId, Guid AuditId);
public sealed record AuditRecord(
    AuditKey Key, Guid RequestId, Guid CorrelationId, AuditPhase Phase,
    AuthorizationContext Actor, AuthorizationContext? Approver,
    ImmutableArray<MatchedGrant> MatchedGrants, ActionRef Action, ResourceRef Resource,
    UseKind Use, string PurposeCode, PolicyRef ExpectedPolicy,
    AuthorityEvidence? PrimaryAuthority, AuthorityEvidence? ApproverAuthority,
    PolicyOutcome PolicyOutcome, HostOutcome? HostOutcome,
    string? HostReceiptRef, DateTimeOffset OccurredAtUtc);
public sealed record AuditReceipt(
    AuditKey Key, AuditStatus Status, string? Reference, AuthError Error);
public sealed record AuditLookupResult(AuditReceipt Receipt, AuditRecord? Record);
public sealed record AuthorizationDecision(
    Guid RequestId, PureDecision Policy, CommitEligibility Eligibility,
    AuditReceipt Audit, bool IsHistorical, AuthError GateError);
public sealed record OperationProgress(
    Guid RequestId, OperationState State, AuthorizationDecision? Decision,
    AuditReceipt? Audit, AuthError Error);
public sealed record CallResult(
    Guid RequestId, CallStatus Status, OperationProgress? Progress, AuthError Error);
public sealed record AuthorityChange(
    string TenantId, Guid AuthorityDomainId, long Generation, ChangeKind Kind,
    string? SubjectId, ResourceRef? Resource);
public sealed record AuthorizationEvent(
    long Sequence, Guid? RequestId, string TenantId, EventKind Kind, AuthError Error,
    AuthorityChange? Change);
public sealed record SubscriptionReply(AuthError Error, IDisposable? Subscription);
public sealed record StopResult(
    StopStatus Status, ImmutableArray<Guid> PendingRequestIds,
    int PendingAuxiliaryCalls, bool PendingNotificationCallback, AuthError Error);
public sealed record OperationOutcomeRequest(
    Guid RequestId, AuthorizationContext Context, DateTimeOffset CreatedAtUtc,
    DateTimeOffset DeadlineUtc, AuditRecord Record);
public sealed record AuthorityAccessRequest(
    AuthorizationContext Context, TechnicalAccess Access, Guid OriginalRequestId,
    AuthorizationContext? OriginalActor, ActionRef? Action, ResourceRef? Resource);
public sealed record AuthorizationProfile(
    string Id, long Revision, string Sha256,
    int MaxIdentifierUtf8Bytes, int MaxGrants, int MaxConcurrentOperations,
    int MaxRetainedOperations, int MaxRuleCacheEntries, int MaxSubscribers,
    int MaxNotificationQueue, int MaxAuditRecordUtf8Bytes,
    TimeSpan MaxRequestDuration, TimeSpan MaxSnapshotAge,
    TimeSpan RetainedOperationDuration, TimeSpan ShutdownBudget);

public interface IAuthorityPort {
    ValueTask<AuthorityReply> ReadAsync(
        AuthorizationRequest request, ParticipantRole role, CancellationToken cancellation);
    ValueTask<AuthError> ValidateAccessAsync(
        AuthorityAccessRequest request, CancellationToken cancellation);
}
public interface IAuditPort {
    ValueTask<AuditReceipt> AppendAsync(
        AuthorizationContext context, AuditRecord record, CancellationToken cancellation);
    ValueTask<AuditLookupResult> FindAsync(
        AuthorizationContext context, AuditKey key, CancellationToken cancellation);
}
// 精确当前域/代次再次验证；不能使用一次旧 ReadAsync 结果冒充当前状态。
public interface IAuthorityFence {
    ValueTask<AuthError> ValidateCurrentAsync(
        AuthorizationRequest request, PureDecision decision, CancellationToken cancellation);
}
public interface IAuthorizationPort {
    ServiceState State { get; }
    ValueTask<CallResult> AuthorizeAsync(AuthorizationRequest request, CancellationToken cancellation);
    ValueTask<CallResult> RecheckAsync(RecheckRequest request, CancellationToken cancellation);
    ValueTask<CallResult> RecordOutcomeAsync(OperationOutcomeRequest request, CancellationToken cancellation);
    ValueTask<CallResult> GetOperationAsync(
        AuthorizationContext context, Guid requestId, CancellationToken cancellation);
    ValueTask<AuditLookupResult> FindAuditAsync(
        AuthorizationContext context, AuditKey key, CancellationToken cancellation);
    ValueTask<AuthError> CancelAsync(
        AuthorizationContext context, Guid requestId, CancellationToken observationCancellation);
    AuthError ApplyChange(AuthorityChange change);
    ValueTask<SubscriptionReply> SubscribeAsync(
        AuthorizationContext context, Guid requestId,
        Action<AuthorizationEvent> observer, CancellationToken observationCancellation);
    ValueTask<StopResult> StopAndDrainAsync(CancellationToken observationCancellation);
}
public interface IAuthorizationEvaluator {
    public PureDecision Evaluate(AuthorizationProfile profile, AuthorizationRequest request,
        AuthoritySnapshot primary, AuthoritySnapshot? approver, DateTimeOffset nowUtc);
}
// 由实现创建；构造形状唯一，无默认端口/全局 ServiceLocator。
// public AuthorizationService(AuthorizationProfile profile, IAuthorityPort authority,
//     IAuthorityFence fence, IAuditPort audit, TimeProvider timeProvider);
```

`AuthorizationEvaluator` 是实现 `IAuthorizationEvaluator` 的无状态 sealed class，公开无参构造器；接口声明不代表本轮已存在实现。`AuthorizationService` 实现 `IAuthorizationPort`，依赖全是宿主借用对象。构造器必须检查空值和 Profile；失败抛 `ArgumentException`，不创建工作线程/订阅。构造成功即 Ready，无隐藏窗口初始化。无同步阻塞 IO 的 Authorize；同步能力通过纯 `Evaluate` 提供。

### 3.1 单位、范围、存在性与默认值

- 所有 ID 大小写敏感，Ordinal 比较；不得 Trim/大小写转换后猜别名。非空、禁止控制字符、禁止未配对 UTF-16 代理项；按 UTF-8 实际字节数检查，最大为 Profile 的 MaxIdentifierUtf8Bytes。租户、签发方、ScopeId、HostId 都无缺省值。
- RequestId/CorrelationId/AuditId/AuthorityDomainId 必须非 Guid.Empty；所有 revision、AuthEpoch、Generation 为 Int64 且 ≥1，不转 double，不把版本字符串作字典序比较；hash 必须 64 位小写十六进制 SHA-256。
- DateTimeOffset 必須 Offset=0；不使用 DateTime.Now/本机时区补值。CreatedAtUtc ≤ now < DeadlineUtc；期限减创建时间 >0 且 ≤ MaxRequestDuration；`now == expiry` 已过期，不能加隐式宽限。
- Grants 非 default，允许空：空合法集合得到 Denied，绝非“空规则全部满足”。每个参与者内 ID 重复（即使内容相同）为 InvalidInput；不同 role 的同名 ID 不合并，以 MatchedGrant(Role, Id) 区分。未知 effect/role/use 为 Invalid，不能忽略后继续允许。两方 Grants.Length 合计及 MatchedGrants.Length 均 ≤ MaxGrants；加法用有界检查，不先复制超限集合。
- 所有 Max* 个数/字节预算必须 ≥1；MaxRuleCacheEntries 可为 0（禁用）；所有 TimeSpan 必须有限 >0，MaxSnapshotAge 不能超过 MaxRequestDuration；没有自动 250 ms、64 并发、5 s 或性能达标默认值。
- Use 必填 Read/Mutate，两者 PurposeCode 均必填。Grant.PurposeCode 与请求精确相等；用途/Use 是受信适配器登记动作的属性，ReadAsync 必须核对宿主命令入口映射，不能信任客户端改为 Read 或另一用途来跳过审计/复核。Mutate 必须持久 Authorization 审计、当前代次再校验。Read 也需策略许可；本版 Read 审计 NotRequired，宿主如要求所有读取持久审计，适配/配置扩展须版本化后接收。
- 第二主体无默认；要求来自权威 Snapshot.RequiresDistinctApprover。缺失返回 ApprovalRequired；Primary/Approver 必须同 TenantId/IssuerId/HostId、不同 SubjectId，不能一个主体两个 session 冒充二人复核。
- 不要求复核时传入 Approver 为 InvalidInput，不读第二端口；RequiresDistinctApprover 仅以 Primary 为权威，Approver 快照必须同一要求，矛盾为 AdapterFault。Grant.Role 必须等于所属快照 Role，Grant.SubjectId 等于该快照主体；超出者为 AdapterFault，不能把跨主体 grants 当未匹配静默忽略。
- Profile 的数值是宿主显式资源和时间预算，不是客户物理阈值。文档中的测试数值只在命名的合成 Profile 使用。
- PureDecision.ExpectedPolicy 是请求期望，不代表已观察权威；合法请求必填，非法/空请求无法校验时可 null。PrimaryAuthority/ApproverAuthority 仅从已通过结构、Context、role 和范围校验的实际快照填写；无有效快照为 null，不造 Guid.Empty、代次或“默认策略”。期望与实际策略不符时保留实际 evidence，但结果 Indeterminate/VersionConflict；双方不一致分别保留，不伪造一个公共代次。Allowed 必须有 primary evidence；若要求复核还须 approver evidence，且两者域/代次/政策一致。
- AuditRecord 所有字符串按同一 UTF-8 字节上限检查；MatchedGrants 数量 ≤ MaxGrants。MaxAuditRecordUtf8Bytes 的 Core 预算为全部字符串 UTF-8 字节数之和（含 Actor/Approver/ExpectedPolicy/evidence/匹配 ID）加固定值字段预算 512 字节，Append 前计算；不是实际 wire/store 大小，适配器仍有自己的编码上限。本版不接受任意 payload、扩展对象或原始异常文本。合法但权威不可达的拒绝审计使用请求 ExpectedPolicy 和 null evidence，不捏造观察值。
- `AuditReceipt.Persisted` 必须有非空稳定 Reference 且 Key 完全一致；NotRequired 无 Reference，仅用于本版 Read；其它状态无成功引用。AuthorityReply Active 必須 Snapshot 非空且 Error=None；其它 Status 不含可被误用的 Snapshot。违反此表为 AdapterFault。
- `EligibleAtEvaluation` 表示求值时间满足模块授权/审计条件，**不是可独立兑换的提交票据**；HistoricalReplay、Read、取消/过期、审计非 Persisted 均为 Blocked。业务副作用只能经 §5.3 的宿主实际提交门。

### 3.2 错误、终态与版本

AuthError 数值在模块 v0.1 固定；文案由 UI 资源映射。None 仅用于明确成功；未知错误不默许。范围/权限/过期为 Denied，格式/未定义枚举为 Invalid，权威不可达/未完整/版本未知为 Indeterminate。已有明确 Deny 时不因另一适配器故障转 Allowed。

AuthorityReply 非 Active 的唯一映射：Revoked→Denied/PolicyRejected，Expired→Denied/SessionExpired，Missing→Denied/ScopeViolation，Unavailable→Indeterminate/PolicyUnavailable；Error 必须为此映射，不符为 AdapterFault。Active 响应结构非法为 Indeterminate/AdapterFault；纯 Evaluate 外部输入格式非法为 Invalid/InvalidInput。请求已超过 deadline 是 TimedOut/DeadlineExceeded，不冒充格式错误；未接纳时 CallResult.Rejected，接纳后按 §7 排空，Gate 均 Blocked。

`AUTH-1014 ResourceLimit` 专用于预算拒绝，不能再混用 Draining。NotFound 只表示本次查询未找到本地保留记录或原审计记录，**不证明远端操作未执行**。认证信息不符的查询返回 ScopeViolation，不披露记录是否存在。Cancel 为请求取消，不是远端回滚。NotSupported 用于跨租户授权、通用角色编辑、秘密恢复、任意策略表达式或 SDK 强制中止等本版未支持项。

Core 的程序集 SemVer 与 Contract major 分开。改变身份比较/取消/错误/生命周期/审计含义、删除字段、新默认批准均破坏兼容；增加 optional 字段也需确认旧消费者不会误允许。传输/持久化映射归后续 Integration，不能宣称当前 record 等于正式平台 Schema。

## 4. 主求值路线（同步纯 Core）

输入必须是本请求匹配的**受信权威快照**。可供 Replay/单测直接调用纯 Evaluate，但外部传入快照不能跳过 §5 的服务端认证而用于生产。

处理顺序固定：

1. 结构校验 Profile、请求、primary/approver、预算、枚举和 UTC；无效返回 Invalid。对超大 grants 先检查 Length，禁止先建立无界索引。
2. 校验 Context 的六字段与请求完全相等；Resource.TenantId 必须等于 Context.TenantId。Policy 必须等于 ExpectedPolicy 三字段，Snapshot.Role 必须对应参与者。超域 Denied；缺/冲突版本 Indeterminate/VersionConflict。
3. 检查当前 UTC、请求期限、权威有效期和 snapshot 年龄：ObservedAtUtc ≤ now，ValidUntilUtc > now，now−ObservedAtUtc ≤ MaxSnapshotAge；未来采集时间、倒置区间无效。ObservedAtUtc 是 IAuthorityPort 的权威采集时间，不能由客户端请求的 CreatedAtUtc 替代。所有 grant 有效期单独检查。
4. 在有界 grant 集合里按 SubjectId、Role、Action（ID+revision）、Resource（全部字段）、Use、PurposeCode **完全匹配**；无 wildcard、前缀、最近目标、最高置信或 UI 选中回退。
5. 匹配的未过期 Deny 任一个存在则 Denied/PolicyRejected；否则至少一个匹配 Permit 才 Allowed；无匹配、全过期和空集合为 Denied/PolicyRejected。MatchedGrants 只含决定结果的未过期匹配项：拒绝时列 Deny，允许时列 Permit；按 Role 数值后 Id Ordinal 排序，结果稳定；多 Permit 可全部列出，不挑“最佳授权”。结构/范围/版本无效时匹配集合为空。二人合并时任一明确 Deny 优先，列已观察的匹配 Deny；否则缺证据/故障为 Indeterminate，缺第二身份为 Denied/ApprovalRequired。
6. primary 要求独立复核时，检查第二 Context 并对 approver 执行同样规则；任一参与者 Deny 优先于另一方 Allow。两位都 Allowed 才合并 Allowed；两 Snapshot 必须同 AuthorityDomainId/Generation/Policy，不能把先后两个不同代次拼成批准。
7. Allowed.ValidUntilUtc = 请求 deadline、参与者 snapshot expiry、匹配 Permit expiry 的最小值；因 Deny/Invalid/Indeterminate 未允许时为 null。多 Permit 保守取最小 expiry，不延长授权。
8. 输出纯结果、ExpectedPolicy 和分角色实际 AuthorityEvidence，存在性按 §3.1。纯 Evaluate 无 IO、线程、取消/native 排空、审计或业务副作用；不发 Draining 或实例事件。内存所有权完全留托管栈/不可变集合。

资源修订是权威映射输入，不能仅信客户端自报。IAuthorityPort 在读快照时验证资源存在/修订/租户；不存在或不能证明返回 Missing/Unavailable。Core 不建立资源主库。

## 5. 服务路线、撤权和缓存一致性

### 5.1 单请求完整执行

1. 预检请求/Profile/实例状态，校验 RequestId 唯一键 `(TenantId, IssuerId, SubjectId, SessionId, AuthEpoch, HostId, RequestId)`；失败返回 CallResult Rejected 无 Progress，不发执行终态。所有 query/cancel/subscribe/recheck 均使用相同完整键，不能先按 Guid 查全局表再泄露存在性。
2. 原子登记不可变请求，检查 MaxConcurrentOperations/MaxRetainedOperations；接纳后 Accepted。若满且所有条目在途，ResourceLimit，不淘汰在途请求。
3. 通过 authority.ReadAsync 获取 Primary 当前快照；按权威要求读取 Approver。端口身份核验失败/撤销/过期不得查询缓存兜底；用 §4 求值。
4. Read 返回纯结果 + AuditStatus.NotRequired，Eligibility.Blocked。Mutate 的结构合法请求即使被拒绝也尝试记录 Authorization 审计；不把输入凭证/错误原文写入记录。非法输入仅有有界脱敏诊断。
5. Mutation 的 Pure Allowed 只有在审计 Persisted 后再通过 fence.ValidateCurrentAsync 才能给 EligibleAtEvaluation；fence 必须校验当前参与者会话、tenant/issuer/host、资源修订、domain/generation/policy 和 expiry，不只比缓存 TTL。
6. 审计 Unknown/Rejected/Conflict 为 GateError AuditUnavailable/AuditConflict，PolicyOutcome 可仍为 Allowed，但 Eligibility 必须 Blocked。fence 失败则 GateError AuthorityChanged/SessionExpired/StaleDecision 等且 Blocked。这是策略结果与可继续条件两个正交字段；宿主不得只看 PolicyOutcome。
7. 逻辑结果产生后，本请求等待它拥有的 authority/fence/audit 真实调用退出、响应流由适配器归还，再走请求级 Drained→ResourcesReleased→唯一终态；不等待其它请求或实例 Stop。请求清理后实例仍 Ready，可接收下一个请求。
8. 超时/取消先通知请求级取消；观测等待可提前返回 Pending，Progress 为当前在途状态（等待取消退出时为 Draining/DrainUnknown）。所有在途 Progress.Decision 必须 null；终态前不得消费临时 Allowed。只有资源退出后才发布 Cancelled/TimedOut/Completed/Failed。Cancelled/TimedOut/Failed 如保留已求值 Decision，Eligibility 必须 Blocked，GateError 为终止原因；没有求值则 Decision null。CallResult.Error 与 Progress.Error 返回终止原因，Completed 可携带策略/审计失败，并不等于批准。

最终 GateError 优先级为终止原因→审计非持久/冲突→fence错误→纯策略错误；成功 Mutate 的 Eligible 和合法 Allowed Read 的 Blocked/NotRequired 为 None。查询终态 CallStatus=HistoricalReplay，保持原 Error/回执，IsHistorical=true、Blocked、GateError=StaleDecision（原策略错误仍在 PureDecision.Error）；在途查询为 Pending/Decision=null，不存在或越权为 Rejected/Progress=null。AuditRecord.Authorization.OccurredAtUtc 在生成原记录时取一次 UTC；重试保留同一不可变记录，不随重试时间改字段。

发布唯一终态时再次检查取消、monotonic deadline 及 Allowed.ValidUntilUtc；排空期间已过期必须 TimedOut/Blocked，不能把 fence 时尚有效的结果延至排空后继续 Eligible。终态写入与取消标记在 operation 内串行线性化，终态后 Cancel=None 只表示已结束，不改原历史；终态前 Cancel=None 只表示已受理取消，不能声称资源退出。入参 cancellation 接纳前已取消则 Rejected/Cancelled，无 Accepted。

### 5.2 缓存、重复、通知缺口和参数变更

**冻结缓存只缓存有界 grant 索引，不缓存 Allow 票据。** 每次 Authorize/Recheck 都读取当前权威。键完整绑定 tenant、issuer、subject、session、AuthEpoch、host、参与者 role、authority domain/generation、policy id/revision/hash、snapshot ID 与资源修订；若一项缺失不命中。MaxRuleCacheEntries=0 完全禁用；LRU 只能淘汰不被当前请求使用的托管索引；无 frame/native 租约。

同键命中前，逐字段比较缓存保存的完整不可变快照（含用途、有效期、ObservedAtUtc、复核要求和所有 grants；grant 顺序按 role/ID 规范排序）。同 SnapshotId/域/代次却内容不同为 AdapterFault，清除此键并 Gate Blocked；不能直接取旧索引覆盖新内容。可信适配器重新采集时间或修改内容须发新 SnapshotId；不新增未定义 canonical JSON/hash 协议。

缓存满且所有项正在使用时不新增缓存，当前请求仅保留自己的临时有界索引并在 ResourcesReleased 释放；不扩 LRU 容量、不淘汰活跃项。合成热索引测试注入逐字段相同的已冻结快照，冷索引测试使用新 SnapshotId；不能用默认每次刷新 SnapshotId 的 SeedPermit 路径声称测到了缓存命中。

失效通知是性能提示，不能成为唯一撤权保障。ApplyChange 只能移除缓存，永不授予权限；受信来源按 `TenantId+AuthorityDomainId` 单调 Generation。旧代无效通知诊断后忽略；跳号/断流使该域索引清空，下一请求必须读当前权威。新 domain 不与旧 generation 比数值大小。通知到达且 old response 迟到时，不能把旧索引重新放回缓存，fence 不通过，Gate Blocked。

同完整键同内容的在途重复返回 Pending 和当前 Progress（Decision null）；终态重复返回 HistoricalReplay，复制结果标 IsHistorical=true、Eligibility=Blocked。内容比较为所有定义字段逐项相等，不用普通 JSON hash 猜 canonical；同键异内容 RequestConflict。旧请求查询/回放不是当前授权，新提交必须新 RequestId + Recheck；每次授权审计独立绑定其 RequestId，已存在的审计 Key 和宿主业务幂等键不因此重建。RetainedOperationDuration 后可删除已终态索引，过期旧请求返回 DeadlineExceeded（原 DeadlineUtc 已过期），不当新请求执行；Core 重启无持久决策 Store，恢复审计查原 AuditId。保留时间必须 ≥ MaxRequestDuration，防止仍有效请求已淘汰后被当新请求接纳。重启后宿主不重发旧业务/授权请求，只查询原审计、恢复同 Key 结果追加；重新授权是明确新意图且新 RequestId。Core 的内存去重不承诺跨重启/跨实例业务 exactly-once，业务幂等及待审计意图持久化归宿主，不能由空查询推断可重做业务。

Profile 不在线原地改；新 profile revision/hash 建新实例并重新验参数，旧代排空。策略变更由 authority 提供新版本；不自动换 ExpectedPolicy 的 latest，不把旧 Subject Context 改成新代。

### 5.3 Recheck 和真正的提交边界

Recheck.Current 必须是新 RequestId，PreviousRequestId 指向同租户、同会话/主体、同动作/资源/用途的前次请求。原记录只用于关联；实际 Context、Policy、Deadline、权威必须重新读。换资源/主体/策略期望应作新的独立授权，不伪称重核同一意图。若旧记录已淘汰，NotFound，允许重新 Authorize；不能据 NotFound 推断业务未执行。

反例：Recheck 在 t1 返回 Eligible，撤权 t2，宿主 t3 提交。模块返回值不能覆盖 t2。**实际业务 CommitOwner 必须在自己的提交线性化点核对当前 authority fence**；与撤权按其权威协议/CAS/事务边界协调，先于撤权线性化的提交允许保留事实，后于撤权的提交拒绝。跨服务两次 RPC 不等于原子检查，宿主若没有可证明的 fence 协议，该生产写切片保持 IntegrationBlocked。Core 不因此引入业务提交 delegate、长持全局锁或设备控制。

已提交后撤权不改原业务/审计事实；查询要当前读取授权。审计失败也不能把业务成功改成“未提交”或重新执行。原契约若无法关闭这一边界，主会话只暂停相关宿主集成，纯 Core/Simulator 仍可验证本页求值、失效和 Gate 行为。

## 6. 审计、部分成功、恢复和多租户隔离

### 6.1 持久化路线

Core 只生成/传递不可变 AuditRecord。IAuditPort 拥有真实 durable store，AppendAsync(context, record, ct) 的 context 是本次已认证追加者，Record.Actor 是历史业务主体，两者不可混为一人。端口必须按当前 context 核追加权，并满足 `TenantId+AuditId` 唯一原子幂等：同键同字段返回原回执，同键异字段 Conflict；须校验追加者/Actor/Resource/Key 各租户一致。不能以日志、内存排队、HTTP ACK、文件存在或截断输出当 Persisted。

Authorization 审计的 AuditId=RequestId（一请求一条）；HostOutcome 由宿主提供非空独立 AuditId。RequestId 指向原授权，CorrelationId 关联宿主操作；Phase 决定 HostOutcome/HostReceiptRef 存在性：Authorization 两字段必须 null；HostOutcome 必有枚举，HostReceiptRef 可空（Unknown 可查），内容只含稳定非秘密引用，不填业务对象。

RecordOutcomeAsync 不重新运行业务。它校验 OperationOutcomeRequest 的新 RequestId、当前 Context/UTC 期限及 Record.Phase=HostOutcome，Record.RequestId 指向原授权。先由 authority.ValidateAccessAsync(AppendHostOutcome) 验当前来源权限（OriginalActor/Action/Resource 从候选记录提供，尚未可信），再按原 AuditKey(Record.Actor.TenantId, Record.RequestId) 调 audit.FindAsync 当前核读取权并取回完整持久 Authorization 记录。无论内存是否存在都以该原记录校验主体/复核者/MatchedGrants/动作/资源/Use/PurposeCode/ExpectedPolicy/双方 evidence/CorrelationId 精确一致，且原 PolicyOutcome=Allowed；原审计不存在、Unknown、冲突或格式不合法一律不追加。历史 Allowed 只用于关联结果，不恢复提交资格。随后以当前 Context 调 AppendAsync；允许原业务主体已失去写权、当前来源仍有追加/读取权限的恢复，否则 ScopeViolation。重启后的这条同 Key 路径是完整 Core 恢复能力，不依赖未定义 adapter 方法；真实凭证/存储/宿主待审计意图另在 AU-I1 验收。记录该结果本身有新 request 生命周期，Decision=null，Progress.Audit 为 HostOutcome 回执，不再生成 Authorization 审计递归或修改原决策。

FindAsync/FindAuditAsync 返回 AuditLookupResult：Persisted 必带完整不可变原 Record、匹配 Key 和稳定 Reference，且记录通过 §3.1 结构/预算校验；其它状态 Record=null。合法未找到返回 Receipt.Status=Unknown、Error=NotFound，不证明未提交；查询失败为 Unknown/AuditUnavailable，越权为 Rejected/ScopeViolation；矛盾响应 AdapterFault/Blocked。Find 没有副作用，不为未知记录分配新 ID。HostOutcome.Record.OccurredAtUtc 是原事实时间，可早于当前 CreatedAtUtc，但必须 UTC 且 ≤ now；恢复不改原时间/内容来制造新幂等键。

原业务提交与 HostOutcome 审计不承诺跨服务原子：宿主的事务必须持久保留同一业务 operation 的待审计意图，随后按原 AuditId 交本端口。模块不建生产 Outbox，不删除业务事实。断网/磁盘满/应答丢失是审计 Unknown，查询原 Key；一次 Find 未找到也不证明原 Append 未完成，Unknown 回执保持并由适配器恢复。自动重试仅允许相同 Key+全部相同内容且适配器声明幂等；无幂等端口不自动重试。

没有 BatchAuthorize/BatchRecord 的公开入口。多项由宿主调用单项并保留每项结果；部分成功是宿主聚合投影，不新增整体提交状态或虚构“批量通知持久化”。本模块不在超预算时偷偷拆批。

### 6.2 查询、隔离与保留

技术查找的存在性门固定两步，不能凭内存“找得到”就改变未认证响应：先用 OriginalActor/Action/Resource 全 null 调 ValidateAccessAsync，证明当前 Context 有该 Access 的自身请求命名空间权限；未授权一律 ScopeViolation。通过后才按完整键找记录；无记录此时才 NotFound；有记录再填原三字段做对象级当前授权。不允许三个可空字段部分填写。Cancel/Subscribe 同样执行两步；返回 Subscription 不代表权限永久有效，后续 dispatch 做对象级核权。AppendHostOutcome 的候选原三字段全非 null，仅为待核内容，必须再由审计原记录证实。

GetOperation/CancelAsync 必须给显式 Context，先核与原记录六字段一致，再调用 authority.ValidateAccessAsync(ReadOperation/CancelOperation) 验当前主体/会话；不能仅用 Guid 查全局字典。该技术授权不是 ReadAsync 的业务 grant 求值，不要求保留已经撤销的原业务写权限，但须现时技术读取/取消权限。查询/取消内部调用按 Profile MaxRequestDuration 有界，取消只停止查询等待，不取消原 operation；只有 CancelAsync 已获技术授权才请求原 operation 取消。鉴权失败的存在性不披露。FindAudit 将当前 Context 和精确 Key 交审计端口，适配器独立验证当前读取权；换 session 后历史读取只能走正式审计端口，不在 Core 自动恢复写权限。查询终态的 Decision 始终复制为 IsHistorical=true/Eligibility.Blocked；查询不会刷新提交授权。

一实例可服务多个租户，但所有 request 表、audit key、cache、invalidations 与 query/cancel 都绑定 tenant；预算既有全实例上限，也不能靠全局 currentTenant 复用连接。生产适配器在连接/行级隔离或 scoped store 边界实现同一不变量；未知/跨租户立即 ScopeViolation。本版不支持跨租户代理/委托；需新版本正式契约后才能增加。

内存请求索引有 count+duration 上限；只回收已 ResourcesReleased 的终态条目。AuditStore 的保留由宿主治理，此指导不设置客户保留天数。长期运行应避免把 subject/requestId 作为无限基数 metric 标签；metric 只使用固定 error/phase/use，敏感关联进入受控日志而非 UI/普通 telemetry。

## 7. 生命周期、线程和事件

### 7.1 状态分层

- 实例：Ready → Draining → Stopped；未确认退出为 DrainUnknown，后续真实退出再恢复排空并 Stopped。不存在全实例 Evaluating，不能一请求结束就 Stopped。
- 请求：Accepted → Evaluating →（AuditPending）→ Draining → Drained → ResourcesReleased → Completed/Cancelled/TimedOut/Failed。纯 Evaluate 不属于服务 request 生命周期，无需制造这些事件。
- 逻辑策略 Allowed 与资源完成无关；请求返回 Pending/DrainUnknown 不交 Decision。审计业务结果 Unknown 可在本地 IO 已退出后作为正常“已结束但结果未知”的回执保留；区别于资源排空未知。
- 接纳前 Rejected 不生成 Accepted/Drained/OperationCompleted；超大输入在复制/解析前拒绝，原输入始终属调用方。
- 重复/观测 query 不重新制造业务终态；最终 OperationCompleted 只发布一次，关联最终 Progress。

### 7.2 线程、取消和停止

直接异步 await 端口，不必强制线程池，不使用 Task.Run 包裹阻塞 SDK 掩盖超时。适配器必须自己安排线程/IO，返回 ValueTask 完成表示本次调用退出并归还内部临时资源；不把仍有回调的任务标为完成。纯计算在有界 grant 间检查请求取消/预算；单纯 Evaluate 同步执行，不承诺强制抢占。

已接纳调用的 cancellation 同时请求本 operation 取消并停止该调用的观测等待；若尚未退出返回 Pending，无授权结果。重复同 ID 的第二观测者取消仅取消自己的等待，需显式 CancelAsync 才取消唯一 operation。GetOperation/FindAudit/CancelAsync 和 Stop 的 observationCancellation 只取消当前观察，不回滚业务或恢复实例 Ready。CancelAsync 不允许撤销其它主体的 operation；技术验证仍在途时不能声称已取消原请求。

Stop 已启动后观察取消返回 StopStatus.DrainUnknown/Error.Cancelled 和当前未退出计数，关闭流程继续；重复 Stop 共用同一流程，不重复发取消或生成停止事件。观察者（含重复调用/Stop）并发数单独以 MaxConcurrentOperations 有界，超限 ResourceLimit，不新建无限等待任务；此预算不占执行 owner 槽，避免等待耗尽槽导致排空死锁。

请求期限用 TimeProvider 单调 elapsed 限制耗时，同时 UTC 用于身份/策略期限；UTC 回拨不延长 elapsed deadline，检测 authority epoch/domain 异常时 Gate Blocked。跨服务只比较 UTC/受信代次，不比较本机 monotonic ticks。

StopAndDrainAsync 原子拒新请求及新外部技术 IO，取消/排空所有本实例在途工作，等待通知 dispatch 调用退出。关闭预算来自 Profile.ShutdownBudget。超预算返回 StopResult.DrainUnknown、PendingRequestIds（本实例不同 Context 的同名 Guid 去重，只作计数/恢复提示，不能据此调用查询）、PendingAuxiliaryCalls 和 PendingNotificationCallback；Core 保留输入/端口调用资源，不能假 Stopped/Dispose 或 Task.Abort。Draining/DrainUnknown 时 GetOperation/Cancel/Find/Subscribe 返回 Draining，不启动额外权威 IO、不输出未经当前核权的历史记录；调用方可继续观察既有调用和重复 Stop，恢复后从新 Ready 实例核权查审计。依赖端口属宿主，Core **不 Dispose 宿主共享端口**，只归还其取得的本次租约和注销自己订阅。只有 Stopped 后宿主才可释放借用端口；旧 worker 不响应可由宿主隔离进程，但不能冒确认排空。

所有外部调用必须归属于一个资源 owner：业务 operation（含其 read/find/append/fence）或辅助调用（GetOperation、FindAudit、Cancel 技术核权、Subscribe 初始核权、每次 dispatch 核权）。MaxConcurrentOperations 是两类 owner 的合计在途上限，业务 owner 内端口顺序 await，不再嵌套占槽；辅助调用无槽则 ResourceLimit，通知核权无槽时丢该投影事件留 sequence 缺口。辅助调用有限期限=MaxRequestDuration，从接纳起用单调 elapsed；超时/观察取消后可给调用方错误，但 owner/槽、输入和借用资源仍保留至底层真实退出，不占 MaxRetainedOperations、不产生业务终态。GetOperation/Subscribe 未完成核权返回 Rejected/DeadlineExceeded 或 Cancelled 且不含记录/订阅；Cancel 返回相同错误且不取消业务；Find 返回 Unknown/DeadlineExceeded 或 Cancelled、Record=null。Stop 不占此槽，也不启动外部 IO，必须包括全部 owner、正在运行的回调及自身队列；任何一项未退出都不能 Stopped。重复请求的纯观察等待不新增端口 owner，但等待者数量也以 MaxConcurrentOperations 有界，满时 ResourceLimit。

### 7.3 事件合同

State/ApplyChange/Stop 只暴露给创建实例的可信宿主生命周期 Owner，不作为远程客户端可调用管理 API；若跨进程暴露，由宿主另核管理权限。本版不新增管理员 grant 或隐式身份。订阅 slot 在初始核权前有界预留，核权失败/超时即禁止事件并退订；若外部核权尚未退出，其辅助 owner 仍须保留至真实退出。Dispose 幂等，不排空已进入的回调；该回调资源仍归 dispatch，不能据退订数为0就 Stopped。

SubscribeAsync 接收显式 Context+requestId，以 authority.ValidateAccessAsync(ObserveOperation) 验当前权限后返回 SubscriptionReply；成功仅有 Error=None 和非空 IDisposable。订阅只收到该请求/同租户的事件，不能暴露别人的 RequestId/SubjectId/ResourceRef；AuthorityInvalidated 的 Change 只给本请求关联的租户/domain/generation（SubjectId/Resource 留 null）。每次派发前用原 Context 调 ValidateAccessAsync(ObserveOperation)，时间预算不超过 MaxRequestDuration；无法证明时停止交付并注销，通知不替代每次查询授权。此检查属于投影 dispatch，不阻塞授权 IO；其未退出调用计入实例 Stop 排空。不存在全实例公开无身份事件总线。失败返回 Error 且无订阅，订阅前漏过的状态直接 query，不重演业务。

每实例 Sequence 单调 Int64，事件含租户/RequestId，禁止凭证、原 grant 内容和业务实体。顺序：Accepted → Evaluated（逻辑，非可提交）→ AuditObserved（如有）→ Draining → Drained → ResourcesReleased → OperationCompleted。AuthorityInvalidated 可穿插，有域代次通知和 §5.2 检查；事件不是决策权威，返回/query 的不可变 Progress 才是权威。

订阅者异常捕获为 SubscriberFault，不改结果。有限 MaxNotificationQueue 满时合并/舍弃投影通知并保留 sequence 缺口，消费者重新 GetOperation；正式回执在 query/持久审计端口，不要求无界“不丢事件”队列。退订丢弃后续队列项，已进入回调不能强行中断。每实例一个串行投影 dispatch，一个慢回调不可阻塞授权 IO；若回调永不返回，Stop 的 dispatch 排空为 DrainUnknown，该 UI 边界未完成不能放弃对象或新建全局线程补偿。

## 8. 无 UI 最小 Host 与两个消费者

Core/test 项目位置见 §12。公开类型全部在 §3，不依赖“requestIds.Next/Factory.Create/CreateProfileCandidate”等不存在的辅助 API。下例是正式签名的**接线示例**；InMemoryAuthority/MemoryAudit 为测试工程待实现的契约夹具，不能当生产认证。示例未编译。

```csharp
var profile = new AuthorizationProfile("synthetic-v1", 1, new string('b', 64),
    256, 128, 4, 32, 8, 4, 32, 4096,
    TimeSpan.FromSeconds(2), TimeSpan.FromSeconds(1),
    TimeSpan.FromMinutes(1), TimeSpan.FromSeconds(2)); // 仅测试，无客户默认值
var clock = new ManualTimeProvider(
    new DateTimeOffset(2026, 10, 9, 0, 0, 0, TimeSpan.Zero)); // 测试夹具
var authority = new InMemoryAuthority(clock, generation: 7);   // IAuthorityPort + IAuthorityFence
var audit = new MemoryAudit();                               // IAuditPort
IAuthorizationPort core = new AuthorizationService(profile, authority, authority, audit, clock);
var context = new AuthorizationContext("tenant-a", "issuer-1", "alice", "s1", 3, "host-a");
var resource = new ResourceRef("tenant-a", "document", "r1", 1, "scope-1");
var policy = new PolicyRef("policy-1", 1, new string('a', 64));
authority.SeedPermit(context, new ActionRef("document.write", 1), resource, policy,
    UseKind.Mutate, "edit", "permit-1", clock.GetUtcNow().AddSeconds(2));
// SeedPermit 明确绑定用途/当前域/代次/primary/有效期，无默认所有动作批准。
var request = new AuthorizationRequest(Guid.NewGuid(), Guid.NewGuid(), context,
    new ActionRef("document.write", 1), resource, UseKind.Mutate, policy, "edit",
    clock.GetUtcNow(), clock.GetUtcNow().AddSeconds(2), null);
CallResult first = await core.AuthorizeAsync(request, CancellationToken.None);
// Pending 时只 GetOperation，不提交；Completed 才能读取最终 Decision。
// 本正常例端口立即完成：first.Status=Completed，Policy.Allowed、Audit.Persisted；
// first.Progress.Decision.Eligibility=EligibleAtEvaluation，实例仍 Ready。
var recheck = new RecheckRequest(request.RequestId, request with {
    RequestId = Guid.NewGuid(), CreatedAtUtc = clock.GetUtcNow(),
    DeadlineUtc = clock.GetUtcNow().AddSeconds(2)
});
CallResult current = await core.RecheckAsync(recheck, CancellationToken.None);
// 宿主仍须在自己的实际提交点核当前 fence (§5.3)，不能直接执行这里省略的业务。
// 若宿主已提交，按同 operation 的稳定 HostReceiptRef+AuditId 调 RecordOutcomeAsync。
// 关闭 UI 不停止服务；结束整个 Host 时 StopAndDrain，Stopped 后才释放借用端口。
StopResult closed = await core.StopAndDrainAsync(CancellationToken.None);
// 正常例 closed.Status=Stopped，PendingRequestIds 空、辅助数0、回调false。
```

夹具必须在唯一测试 Host 内定义，不是隐含产品 API：`ManualTimeProvider(DateTimeOffset utc)` 重写 GetUtcNow/GetTimestamp/TimestampFrequency/CreateTimer，频率=TimeSpan.TicksPerSecond；`Advance(TimeSpan positive)` 同步推进 UTC、单调 ticks 并触发到期 timer，禁止真实 Sleep。`InMemoryAuthority(TimeProvider clock, long generation)` 使用固定测试域 `11111111-1111-1111-1111-111111111111`，只接受 Seed 过的六维 Context；`void SeedPermit(AuthorizationContext context, ActionRef action, ResourceRef resource, PolicyRef policy, UseKind use, string purposeCode, string grantId, DateTimeOffset validUntilUtc)` 生成 Primary 单 Permit、RequiresDistinctApprover=false、ObservedAtUtc=读取时 clock UTC、新 SnapshotId；仅精确登记的动作/用途/资源能 Active，技术权限按单独 seed 记录核准。MemoryAudit 用 tenant+AuditId 原子字典逐字段幂等，Find 返回完整原 Record；是合成软件端口，不证明 durability。两夹具提供计数及 TaskCompletionSource barrier，并可注入明确的 AuthorityReply/AuditReceipt，不隐藏默认许可。

失败最小顺序：阻塞 read→取消原调用→返回 Pending/Decision=null→GetOperation 当前核权可见 Draining→释放 barrier→请求真实退出、ResourcesReleased→Cancelled/Blocked；此时服务仍 Ready。若 audit 应答丢失但 IO 已退出，Completed+Audit.Unknown/Blocked→FindAuditAsync 原 Key→Persisted 原记录，仅恢复审计状态，不恢复提交资格。重启结果追加顺序：新 Context→RecordOutcomeAsync→当前追加核权→Find 原 Authorization 记录及当前读权→精确关联→同 HostOutcome AuditId Append→查询同回执。正常/失败 Host 最终都 Stop；阻塞 read/技术核权/回调不退出时只能 DrainUnknown，解除后重复 Stop 才 Stopped。

消费者 A（ProductionPortHost）：显式操作员 Context、资源 revision、Mutate；模拟业务 gate 在 fence 更新下序列化检查。验收撤权前/后提交两个线性化方向。消费者 B（ReviewToolHost）：同程序集，另一 issuer/tenant/session 和审计实现，通用 action `review.opinion.append`；宿主自己持意见事务，不引用 A 的 VM/私表，核心不含机判、质量放行或设备动作。

两个消费者均在唯一测试工程内作为不同 fixture/console test host 函数运行，不为文档创建空工程。两 Host 可在同进程并行；Context、通知、语言/取消和保留互不污染。生产 auth/account 服务/真实 audit store 的接入验收单独关闭。

### 8.1 可信适配器与凭证绑定：宿主内部接线

本节补足 AU-I1 的软件接线，不改变 §3 的公开 Core API，也不新增登录系统、通用认证 SDK 或适配器 DLL。以下表和步骤是宿主侧实施协议；不将其当成某个尚未查阅的供应商 API。真正认证/存储客户端的公开签名由选定消费者接入任务核对，不能猜接口或在 Core 中放秘密。

| 宿主内部输入/Owner | 精确内容、校验与用途 |
|---|---|
| 路由绑定；宿主组合根 | 不可变键 `(TenantId, IssuerId, HostId)`，值为借用的 `IAuthorityPort`、`IAuthorityFence`、`IAuditPort` 及该路由的受信会话来源。键逐字段 Ordinal；重复、空值或不能证明三端口属于同一权威路由时构造失败。DTO 不提供端点、连接串、凭证别名或租户库名；不得按请求拼 URL/SQL/文件路径。 |
| 受信会话绑定；认证 Owner | 键为完整六维 Context，值保留认证 Owner 已验证的会话来源引用、当前有效期和撤销状态。引用只在宿主可信层；凭证原文不进入 Core/VM/审计/telemetry。登记只能由成功认证路径执行，外部请求不能自登记；角色名称和已有 Context 不构成登记依据。每次调用用该来源检查当前状态，初次登记或一次旧 token 验证不代替当前撤权。 |
| 命令绑定；宿主命令 Owner | 精确 `ActionRef(Id,Revision)` 对应唯一 `Use`、`PurposeCode`、允许的资源 Type/ScopeId 及二人策略来源。来自受信版本化命令注册，不从 UI/消息改写。Resource.Id/Revision/TenantId 由领域资源 Owner 当前解析，再与请求逐字段核对；没有匹配项即拒绝，不按角色猜命令。 |
| 技术权限绑定；认证/策略 Owner | 分别登记 §3 的四种 `TechnicalAccess` 和审计 Append/Find 权限。自身请求命名空间核权与对象级核权按 §6.2 两步执行；历史读/结果追加可与原业务写权限分离，但不能由旧 Actor 或旧 Allowed 推导。审计端口自行重复当前身份及对象权限校验。 |
| 宿主预算；消费者 Profile Owner | 必填正 Int32：`MaxRouteBindings`、`MaxVerifiedSessions`、`MaxCommandBindings`、`MaxPendingAuditIntents`；必填正 Int64：`MaxPendingAuditIntentBytes`；必填有限正 TimeSpan：`HostShutdownBudget`。这些是宿主配置输入，不增加 Core Profile 字段。字节上限指待审计意图实际持久编码字节；接入时按所选存储编码计数，超限不先拷贝/排队。示例值只属合成 Host，生产无隐含默认值。 |

宿主适配入口按以下顺序执行，组合根创建的端口只能借给该可信根及其 Core：

1. 在有界路由中按三字段精确找端口，再用完整六维 Context 找受信会话；找不到或字段不符按 §3.2 返回 Missing/ScopeViolation，不调用其它路由。不因不同租户 SubjectId 相同而借用连接或凭证。Primary 与 Approver 分别绑定自己的已认证会话，不能用主调用者凭证生成第二人的 Active 快照。
2. 向绑定的当前会话来源核 expiry/revocation/AuthEpoch、签发方和 Host；撤销/过期/失联按 §3.2 返回 Revoked/Expired/Unavailable。过期条目在确认无在途借用后移除，不能淘汰仍在调用的条目以绕过预算；额度满时拒绝新的会话绑定。重新认证产生新 Context，旧 Context 不原地改成新代。
3. `ReadAsync` 核命令/用途/读写与资源 Owner 的当前映射，再读取该绑定的当前权威；快照转换逐项对应 §3 的 Context/Role/Policy/Domain/Generation/时间/Grants。缺字段、未知枚举、溢出、跨域 grant、同代矛盾都失败关闭，不从客户端补字段。ObservedAtUtc 来自受信采集，不能用请求创建时间或本机“刷新”重包装旧数据。
4. `ValidateAccessAsync`、`ValidateCurrentAsync` 和审计调用也执行步骤1–2；不能仅在 Authorize 时验凭证。`ValidateCurrentAsync` 按 §5.1 校验全部参与者/evidence/资源/expiry；它仍是观察核验，不承担 §8.2 的实际业务提交事务。通知只接组合根绑定的受信源，转交 ApplyChange；公开消息不能直接调用管理入口。
5. 每个适配器返回的 ValueTask 完成前必须关闭本次流/响应和归还会话借用；取消只请求退出，不将仍占用底层 IO 的调用改成完成。底层异常按阶段映射 PolicyUnavailable/AuditUnavailable，响应矛盾为 AdapterFault；取消异常仅在确已退出后表示 Cancelled。具体 provider 的异常分类表在其实际接入任务补充，不改变本节状态语义。

同进程可任意调用对象的方法者处于同一可信边界；不能把本地端口对象交给未受信插件后声称 DTO 核对足以隔离。远程服务或未受信进程在自己的服务端重新认证，使用其受信组合根生成/校验 Context；不得传输本地端口、会话来源引用或把 Context 当 bearer capability。此限制不扩大 Core 为通用认证产品。

### 8.2 实际 CommitOwner：首版提交与撤权协议

§5.3 的原子性在宿主侧按本节确定实施，不留给程序员任选“检查一次再写”。首版受控写路径使用**同一权威事务边界中的当前授权状态与业务提交**：当前会话状态/有效期、domain/generation/policy、资源修订及业务幂等记录由实际 CommitOwner 读取并参与同一串行化提交；撤权/换代写入同一权威状态并与提交串行化。该状态必须是作出撤权决定的权威，不能是异步镜像、通知缓存或定时刷新表。

本模块不建这些领域表，也不公开业务 delegate。实际消费者采用的存储/权威协议必须证明以下原子语义；无法做到同一事务边界的远程策略服务、设备或旧系统，本版相应写路径维持 IntegrationBlocked，不用额外 RPC、锁住客户端或 TTL 代替协议。跨系统扩展需在受影响消费者指导定义权威协议后接入，不声称设备动作与数据库事务天然原子。

实际提交步骤固定：

1. 宿主保存本次最终授权请求及 Completed 决策；只接收非 Historical、Policy=Allowed、Audit=Persisted、Eligibility=EligibleAtEvaluation、GateError=None 的 Mutate。保存的是最后一次新 RequestId（包括 Recheck.Current）的完整 evidence，不用更早请求的审计拼当前决策。客户端不选择 commit 后端。
2. 宿主在受信命令映射下持有已经校验的业务意图、原业务 operation ID 和版本；payload/幂等身份归业务 Owner。首次dispatch之前在受控持久store记恢复锚点（业务ID/不可变意图、原授权Key和预留结果AuditId），状态为PendingBusinessQuery并占待恢复容量；失败则不得dispatch。该锚点不是成功事实或HostOutcome审计，进程在commit响应丢失后死亡仍可找回原业务ID。进入业务事务后先按当前身份核对恢复/读取此 operation 的权限，再查该业务 ID。已有同意图终态只返回历史原回执、不得再副作用；异意图同 ID 冲突；未确认结果只允许原 ID 查询。这个历史分支不把旧授权恢复成当前写权限。
3. 无既有结果时，在该事务内锁定或等价串行化核对上述当前权威状态、双方六维 Context/代次/策略、资源全部字段，并以条件核验/业务写入点受信 UTC 再核请求/会话/授权 expiry 和当前取消条件。要求第二主体时两人都核。任何不符则拒绝并不写业务，不能静默改资源 revision、Policy 或 Context；重新授权是新明确意图。
4. 在同一串行临界区执行一次被映射的领域提交，并在同一事务持久保存业务 ID/稳定回执以及 §8.3 的完整待审计意图；任一写入失败则整个业务事务不提交，预先保存的恢复锚点仍保留。待审计容量须在事务内预留/核限，超预算不能先提交业务后才发现无法留证。本协议将最终成功事务内的条件核验/业务写入点作为共同线性化点，当前授权状态的锁/等价隔离保留至事务确认；若rollback则没有成功业务线性化点。UTC必须在该受保护点取值，不能使用入队或事务开始时间；之后durable确认/响应返回较晚不把原事实改成另一时点。提供者无法证明这一个共同点就不得启用生产写。
5. 业务事务成功之后才调用 RecordOutcome；审计未知不重复步骤4、不回写业务为失败。提交响应丢失或提交异常不能确定 rollback 时，宿主返回业务结果 Unknown、保存原业务 ID并查领域 CommitOwner；取消/超时亦不能据异常推断未提交。业务结果和审计回执始终两轴保存。

撤权先线性化则步骤3/4不允许业务事实；提交先线性化则保留原事实，后续读取和新的提交按新权威核权。源策略服务有自己的独立撤权线性化点时，宿主事务仅比较本地旧 Generation 不满足本节。真实协议与部署证明由消费者 CommitOwner 提供；协议的失败关闭、比较字段、幂等与恢复算法已在此确定。

上面的新写入口不用于恢复重做；恢复路径直接以当前技术读取身份查询原业务ID，不要求重新Authorize/Recheck，也不生成新的Eligible。原授权已过期时仍可在有权读取的情况下确认历史业务事实；查询所得历史回执不进入步骤4。

§8 合成 Host 只需在 `InMemoryAuthority` 内增加一个共享串行临界区：Seed/撤权/换代和模拟 CommitOwner 全部使用同一区，业务次数与原 operation 回执只在通过上述当前核验后更新。`TaskCompletionSource` 在入区前安排两个线性化方向，禁止在锁内 await 外部 IO；这只证明软件次序，不证明真实数据库或设备原子性。两 Host 使用各自权威临界区，不放全局静态锁。

### 8.3 Audit Owner、持久映射与原意图恢复

`IAuditPort` 的 Owner 是审计事实提交者，生产 CommitOwner 的 Owner 是业务事实及待审计意图提交者，认证 Owner 只管当前凭证/技术权限。日志、UI和 Core 内存表都不是上述持久事实的替代。适配器按本节固定逻辑存储映射；实际数据库/文件 provider 的 API、部署与真实 durability 在选定产品接入时核对，不建立第二套公共 Audit DTO。

| 逻辑持久映射 | 写入/读取规则 |
|---|---|
| 身份与唯一性 | 主键是 §3 的 `(Key.TenantId, Key.AuditId)`；额外独立唯一稳定 Reference 在首次原子提交时形成并保存，不能在每次 Find 时新生成。字符串按 Ordinal 保真，数据库使用等价区分大小写的键/比较或精确字节键，不能受默认 collation 折叠。 |
| 完整原记录 | §3 `AuditRecord` 的每个字段逐项持久化，包括 Actor/Approver、ExpectedPolicy、两份可空 evidence、MatchedGrants、所有枚举/UTC/可空字段；Int64 不经浮点，Guid 无空值，UTC 不改本地时间。MatchedGrants输入须已按 Role/Id 规范次序且无重复，按原样保存；不静默排序异内容，不把 null/evidence 缺失补成零代次。未定义枚举和缺失字段拒绝。 |
| 结构与关联 | Authorization 的 AuditId=RequestId，HostOutcome 的独立 AuditId、关联 RequestId/CorrelationId、Phase 与字段存在性按 §6.1。所有租户一致；HostOutcome 必须与已持久原 Authorization 精确关联且原 PolicyOutcome=Allowed。端口对直接调用也校验这些条件，不能依赖“总是从 Core 来”允许绕过。 |
| 原子 Append | 当前追加权限校验与追加在端口权威提交边界执行；认证来源失联/撤权不能用预检成功兜底。按主键原子 insert-if-absent；已存在逐字段比较全部规范记录，相同返回原 Persisted/Reference，任何不同 Conflict/AuditConflict；不覆盖旧行、不用普通 JSON/hash 代替字段比较。首次提交的 Reference 与记录一起持久。 |
| Find | 先核当前读取权，再按完整 Key 读取一致的原记录和 Reference；无权不披露存在性。完整、匹配且结构合法才 Persisted/Error=None；缺记录 Unknown/NotFound，连接/恢复不确定 Unknown/AuditUnavailable，损坏/矛盾 Unknown/AdapterFault，Record=null；拒绝读取 Rejected/ScopeViolation。Find 不分配 ID、不改记录。 |
| durable 回执 | 只有所选 provider 已完成其声明的持久提交并满足产品采纳的故障恢复策略才 Persisted。提交结果不明一律 Unknown；同 Key 查询或相同记录重试得到原 Reference。编码/物理 Schema 版本由 adapter 发布绑定，迁移保留原字段/Reference和唯一性；不宣称本逻辑表已经是平台 C-01～C-08 wire schema。 |

Core 的 audit bytes 预算仍是 §3.1 的字符串和+512；上表不把该值冒充 provider 实际存储大小。实际编码可逆保留表中全部字段，并另按宿主字节上限限制；本模块没有要求签发或跨进程传输的 canonical byte token，故不新增无消费者的二进制 codec/hash 协议。

宿主待审计意图是业务事务保存的不可变完整 HostOutcome Record（含独立 AuditId、原最终授权 RequestId、CorrelationId、原事实 UTC和稳定 HostReceiptRef），附业务 operation ID、对应授权原 Key、原业务回执、状态及实际编码大小。结果追加入口只从CommitOwner的受控持久意图读取Record，不能接受UI上传的Succeeded或把HostReceiptRef字符串当业务证明；拥有读取/追加技术权也不获得创建业务成功事实的权力。Succeeded 只能来自确认业务成功的事务；未知业务结果不得猜成 Succeeded。每个已确认业务终态对应一个稳定结果 AuditId；重复发送不改 Record 的内容或时间。若已有独立 Unknown 观察记录，后来确认结果必须用新的结果记录 ID，保留原观察事实；不得用同 Key 覆盖 Unknown。

恢复状态固定为 `PendingAudit → Sending → Persisted`；发送结果 Unknown 返回 PendingAudit 并保留全部原字段，Conflict/越权/原关联损坏进入 `NeedsAttention`，不自动丢弃或换 Key。业务 Unknown 单独归 `PendingBusinessQuery`，从提交前的持久锚点向 CommitOwner 查原业务 ID，确认终态并原子保存相应完整意图后才发送结果审计；查无记录仍是未知，不走重新执行业务分支。原Authorization已Allowed且持久、但在宿主提交门确认拒绝/提交前取消时可形成相应Rejected/CancelledBeforeDispatch结果记录；原授权被拒绝不走HostOutcome，遵循§6.1。重启时 Sending 按原 Key 查询，不能据进程死亡认为未发送。人工恢复NeedsAttention须先修复来源/权限并核对原内容，再以CAS恢复PendingAudit/PendingBusinessQuery，不能改ID或原事实。

恢复次序：

1. 新 Ready 根使用当前已认证的恢复身份，核该租户待审计意图读取权；从已持久意图取得完整原 Key/Record，不能靠 UI 或旧 Actor 恢复凭证。旧业务写权撤销不阻断具当前读取/追加技术权的恢复者；若无这些权，保持 NeedsAttention，不能以系统账号隐式绕过。
2. 先 FindAuditAsync 当前 Context + 原 HostOutcome Key。完整 Persisted 且 Record 全字段相同→只将该意图标 Persisted；不同记录/Conflict/AdapterFault→NeedsAttention。Unknown/NotFound 不证明未写，可在确认端口具本节原子幂等后发送原 Record；其它 Unknown 先保留并按有界消费者重试计划回查，不能热循环。
3. 发送时用新的 `OperationOutcomeRequest.RequestId` 和当前 UTC期限，Record 保持原样；调用 §6.1 的当前追加核权→查原 Authorization及读权→精确关联→同 Key Append。服务请求 ID 与持久 AuditId 分开：新的服务调用不生成新的业务/结果审计身份。
4. Pending/调用观察取消时保存原 Task、新服务 RequestId和原 Record；原 Task 退出前不启动同一意图第二次发送。终态 Persisted 核对回执后原子标完成；发送后响应丢失或宿主标完成失败，下次仍按同 Key回查，最多得到原 Reference。允许多个恢复者时由业务 store 对意图 CAS 领取，未释放或租约失效后的迟到发送仍由审计 Key 幂等保护。

重试次数、间隔、单次期限和保留期限由消费者 Profile 显式采纳；无自动无限重试、容量扩张或超期删除。只有审计已确认且满足宿主治理保留规则才可回收持久意图；业务和审计 Unknown、NeedsAttention 不能为了容量腾空而删除。读取权限撤销立即停止呈现敏感原记录，保留受控根/持久 store 中的原身份供有权恢复，不把原记录复制进普通日志。

### 8.4 两宿主装配、有限收尾与新增断言

获准实现后仍使用 §12.1 唯一 Core.Tests 的两个 Host；本轮不新增工程/公开 Factory。两 Host 的受信接线分别为：A 的 route=`tenant-a/issuer-1/host-a`、session=`alice/s1/epoch3`、command=`document.write@1/Mutate/edit/document/scope-1`；B 的 route=`tenant-b/issuer-2/host-b`、session=`bob/s2/epoch4`、command=`review.opinion.append@1/Mutate/opinion/review-entry/scope-2`。各自 seed 当前 resource/policy、独立审计 store、业务 ID/receipt/待审计表和权威临界区；技术权限另按测试明确登记，无 seed 即拒绝。合成宿主预算为 route=2、sessions=4、commands=2、pending intents=4、实际编码 bytes=32768、HostShutdownBudget=2s，不成为生产默认值。

合成意图存储为可重新注入新Host的独立fixture对象，不随Core/Window释放；只模拟重启保留，不声称磁盘durability。为使字节预算可执行，fixture采用.NET10 BCL `System.Text.Json.JsonSerializer.SerializeToUtf8Bytes<T>(T value, JsonSerializerOptions? options)`、options=null、固定声明顺序的内部record：`Guid BusinessOperationId, AuditKey AuthorizationKey, Guid OutcomeAuditId, AuditRecord? Record, string? BusinessReceiptRef, int State`；State精确对应1=PendingBusinessQuery、2=PendingAudit、3=Sending、4=Persisted、5=NeedsAttention，其它整数拒绝。此BCL签名据本机Microsoft.NETCore.App.Ref/10.0.12的System.Text.Json.xml核对，未运行序列化。提交前Record/BusinessReceiptRef为null；业务确认后填完整值，原字段不改。以该完整记录实际序列化长度计入32768-byte总上限（加法checked），替换行按旧长度扣除/新长度加入，不只算AuditRecord；不以此默认JSON作身份hash/跨产品wire标准。生产provider仍按自己实际编码核限。先检查字段/集合数量和UTF-8预算（BusinessReceiptRef也受MaxIdentifierUtf8Bytes约束），因此只编码固定有界对象图；实际编码超限则不提交存储/业务事务，无任意payload或扩张预算。

空 Host 的步骤是：先校验 Core/宿主预算并在进程根预留**一个**本 Host 的 Owner 槽→安装不可变路由及已经验证的会话/命令来源→显式构造 §8 的借用端口/Core→Authorize/Recheck→按 §8.2 模拟提交及持久意图→按 §8.3 原 Key回查/结果追加。根槽创建在任何初始化 IO 前，强持全部借用端口、Core、原 Task/请求/业务 ID/AuditKey和观察者；构造失败也保留已开始 IO，先停止接纳并走同一有限收尾，不能因方法离栈丢弃 Owner。此根是宿主内部对象，不发布新的 Core Session。

整个 Host 退出（区别于 §10 的 Window 关闭）先拒新业务/新恢复发送并注销通知来源，发起 Core.StopAndDrain，同时请求取消宿主自身初始化/commit/query/recovery IO；这些宿主 IO不冒充 Core.PendingAuxiliaryCalls。在 HostShutdownBudget 内观察 **Core Stopped、宿主原 Task真实退出、通知回调退出**三个条件；全部满足才归还其借用资源并清根槽。任一未满足，保留根槽/原 Task和未决身份，以宿主 DrainUnknown 返回，独立有限再次观察不重复 commit/发送或清空持久意图。每Host宿主IO在途及收尾观察者分别以Core Profile.MaxConcurrentOperations有界，满时ResourceLimit；不启动无限观察者/后台补偿线程。通知源借用资源也要等其回调真正退出。共享端口的最后实际 Owner才 Dispose，Core和窗口不释放共享端口；cleanup 异常单独保存，不覆盖原业务/审计错误。

| 新增有限场景（复用 §9/§11，非已运行测试） | 可判定断言 |
|---|---|
| A DTO 冒充 B，或存在 Context但未验证来源 | A/B 均 ScopeViolation，错误路由端口调用数0；不登记新会话、不披露 B 原记录。 |
| 用 Primary来源读 Approver，命令 Mutate降为Read | 对应身份/映射拒绝；无 eligible/业务提交。独立已验证第二来源才进入原二人路线。 |
| 业务写已撤销但恢复者有当前读/追加权；随后撤销恢复权 | 前者只恢复同Key审计、业务次数不增；后者不读原正文、不追加，意图 NeedsAttention。 |
| Recheck后撤权/换代、事务提交点恰到expiry | 撤权先或提交点过期：业务次数0；提交先：原事实与待审计意图各1，后撤权不改历史。 |
| 业务commit成功但响应丢失后进程死亡；或事务未提交 | 前者新Host从提交前持久锚点按原业务ID查询、次数1；后者没有业务/成功意图，保留恢复锚点。未知分支不推断rollback、不再次执行。 |
| 业务写入与待审计意图任一失败、容量不足 | 业务事务均不提交；业务次数0，无成功回执/成功意图，无孤立成功业务；已保存锚点不删除。 |
| 同 AuditKey 原Record重发、任一字段不同 | 同内容同Reference且仅1原记录；不同内容Conflict，不覆盖。Actor/当前追加者分离但租户必须一致。 |
| 两恢复者领取、Sending重启、审计成功后标完成失败 | 原业务次数1，原结果审计只有1条/1Reference；按原Key查，不能重建AuditId。 |
| 初始化/commit/recovery或通知真实不退出，关闭一个Window | Window只停止呈现；整个Host收尾保留根/Task/Key与借用端口，DrainUnknown；退出确认前不能释放。 |

两轮自审限定新增接线：第一轮按 A/B 空宿主从身份来源、命令映射到业务/结果审计逐字段走通；第二轮按上表拒绝、迟到、撤权、响应丢失、重启及关闭反例核对不变量。测试工程 `HostContractTests`/`AuthorizationRaceTests`/`AuditRecoveryTests`/`LifecycleTests` 分别消费这些断言；实际 C#、provider、真实提交协议和运行未执行。已有 AU-C1～C3、AU-W1 接收不重新计审或撤回。

## 9. 两种审查视角、场景和可判定验收

### 9.1 外部接入实现者视角：求值和身份

SyntheticProfileV1 **仅为测试**：identifier bytes=256、grants=128、concurrent=4、retained=32、cache=8、subscribers=4、notification queue=32、audit bytes=4096、MaxRequestDuration=2s、MaxSnapshotAge=1s、retained duration=1min、shutdown=2s；profile ID/revision/hash 显式。authority domain=D1、Generation=7；UTC=t0；alice/s1/epoch3；r1/revision1；policy-1/rev1/hash=64 个 a。测试夹具时间可推进，不依赖 Thread.Sleep。不将上述值当客户节拍或默认部署值。

| 场景输入/参数来源 | 固定处理、输出/错误 | 恢复与断言 |
|---|---|---|
| 精确 Permit（来自 seed authority，不来自 request 自报） | 结构→受信上下文→作用域→匹配→Allowed；Mutate 审计成功及 fence 校验后 EligibleAtEvaluation | audit 恰一条原 Key；请求资源释放，实例仍 Ready；第二请求能完成 |
| null 请求、Guid.Empty、缺 tenant/session/purpose、非法代理项 | 预检 InvalidInput，未接纳，不调用外部 authority/audit | 修正后新请求；端口调用数=0，无执行事件；不写原密码/输入 |
| 空 Grants、未知 action、全部 Permit 已过期 | Denied/PolicyRejected 或 StaleDecision；不把空 AND 当 Allowed | 权威重新授予新政策后新请求；无默认 allow |
| 多 Permit + Deny（打乱顺序）、重复 Grant.Id | 有匹配 Deny 稳定 Denied；同 role 重复 ID InvalidInput；MatchedGrants 分 role 排序 | 任意排列结果语义相同；不得挑第一/最高分 Permit |
| 同 SubjectId 但 tenant/issuer/session/host/epoch 任一不同 | 请求/权威逐字段核对；ScopeViolation/SessionExpired | 注入合法当前身份；跨租户 query/cancel 不披露记录存在性 |
| resource tenant 错、revision1 请求但权威 revision2 | ScopeViolation/VersionConflict，Gate Blocked | 由宿主重新解析资源再新请求，不能最近资源补齐 |
| UTC 恰等 session/snapshot/grant expiry | SessionExpired/StaleDecision，不能缓存复用 | 重新认证/读取权威；无宽限，UTC 回拨不延长 elapsed |
| 第二主体缺失、同主体不同 session、第二方 Deny、代次不同 | ApprovalRequired/PolicyRejected/AuthorityChanged；双人许可同域同代才 Allowed | 当前权威两个不同主体重新核；复核不生成产品人判 |
| 弱信号、遮挡、退化等价：身份字段缺失/响应不完整/断连 | 无视觉路径；InvalidInput/AdapterFault/PolicyUnavailable；Indeterminate 不批准 | 当前端口恢复并新请求；禁止从旧 Allowed 或角色名称兜底 |
| 超过 MaxGrants、bytes、retained 或 concurrent | 先预算检查，不建立索引/复制巨对象；ResourceLimit/InvalidInput | 降低/等待；不自动拆批，峰值资源必须有界 |
| 改 Profile/Policy/hash 或改变请求内容但复用 ID | Profile 换新实例；ExpectedPolicy 不符拒；同键异内容 RequestConflict | 新明确版本请求；同 revision 异 hash 不默许 |
| 只改 PurposeCode/Use、第二角色同名 grant、合计超预算 | 未登记用途/读写映射拒绝；同名不同 role 保留两项；合计超限 ResourceLimit | 不能改用途绕过复核/审计；没有静默去重或增大预算 |
| authority 不可达或双方政策冲突 | 期望政策保留，缺失 evidence=null，冲突保留两方实际 evidence；Gate Blocked | 合法拒绝审计可持久，不伪造域/代次；审计成功不改变拒绝 |
| 同 SnapshotId/域/代次返回变更内容 | AdapterFault、清键、Gate Blocked | 换正确新 SnapshotId 后新请求；不能直接使用旧索引 |

### 9.2 并发/故障恢复视角：在途和长期运行

| 场景输入/参数来源 | 固定处理、输出/状态 | 恢复与断言 |
|---|---|---|
| 在 authority read 与 fence 之间撤权/通知跳代 | 清索引；fence 返回 AuthorityChanged，Policy 可能是旧 Allowed 但 Gate Blocked | Barrier 控制并发，旧响应不能回填新缓存；下一请求读当前权威 |
| Recheck 返回后提交前撤权 | 模块结果不宣称原子；Host gate 线性化核权 | 两个方向测试：撤权先则业务次数0；commit先则保留原事实，不能回写 |
| 同 ID 同内容双调用、同 ID 异内容 | 单 operation，同内容观测复用；历史重复 Gate Blocked，异内容 Conflict | authority/audit 一次；取消重复观测者不影响原 operation |
| audit Append 成功响应丢失，随后 Find 为空/旧会话重连 | Unknown 保留原 Key；不产生第二业务动作；查审计端口当前读权 | 相同 Key 恢复，最终同 Reference；空查询不得推断未提交 |
| 两项记录一 Persisted 一 Unknown | 单项返回原状态，无 batch 总成功 | 宿主只查询 Unknown 原 Key；已成功项不重写，全部明细保留 |
| 请求取消/超时，适配器仍占流且不退出 | Pending/DrainUnknown，Decision null；不得早放终态/资源 | 释放 Barrier 后 Drained→ResourcesReleased→Cancelled/TimedOut，终态一次 |
| fence校验后排空期间到达授权expiry | 最终发布时重新核UTC/elapsed，TimedOut/Blocked | 不能将清理前Eligible迟到发布；实际Host仍有独立commit fence |
| IO 已退出但远端审计结果 Unknown | 本地可排空并 Completed + audit.Unknown + Gate Blocked | 远端回查，不把 Unknown 当本地 native 未退出或成功 |
| 一请求排空、另一请求仍运行；整个服务关闭 | 前者可终态，实例仍 Ready；Stop 后拒新，服务排空所有在途 | 单请求不等实例停；超预算服务 DrainUnknown，后续退出才 Stopped |
| 订阅者抛异常/很慢/永不返回，队列满 | 抛错隔离、通知有缺口可 query；授权不被回调阻塞；无限阻塞会使 dispatch Stop DrainUnknown | 无无界队列或每次新线程；回调真实退出才归还 dispatch 所有权 |
| 端口断连/恢复、重启/升级/回退 | 所有决策缓存从空开始；历史审计原 Key 查；重启不延续写授权 | 当代认证后重核；恢复旧包不能恢复已撤销策略/会话 |
| 两 Host 相同 subject/resource/id，不同租户 | 命名空间完整隔离，audit key+context 独立 | B不能读取/取消A；任一 change 不清/更新另租户权威，不返回跨域数据 |
| 长稳重复连/退订、policy rotation、审计拒绝风暴 | 有限 retention/index/cache/dispatch；指标固定基数；无全局 current user | 运行 Profile 明确 duration/load，内存/句柄/线程/队列与未决计数无单调泄漏，未真实测不称长稳通过 |
| 无 UI、有 UI、三语/关闭一个窗口 | 同 Core 求值；语言只改投影，关闭仅 unsubscribe | 不重授权/重提交、不停止其它 Host；无订阅者仍完成请求 |
| Find/技术核权永不退出、Stop 超预算 | 调用方超时无秘密结果，辅助 owner/槽仍保留；Stop 辅助数>0、DrainUnknown | 真实退出才归还槽；不把无 RequestId 的 IO 漏出排空 |
| 重启后恢复 HostOutcome、读取越权/原记录损坏 | 查原完整 Authorization→关联；越权 ScopeViolation、损坏 AdapterFault，不 Append | 新实例可恢复同 Key；原证据不符/未确认一律不追加，更不重派业务 |

## 10. 可选 UI PageContract（后续 WPF 切片）

已有责任范围中的授权原因投影保留，不凭任务新增账号管理/大仪表盘。控件名 `AuthorizationStatusPanel`（Wpf namespace），任务是查看当前动作为何被拒/未确认、刷新当前授权或查询原审计；只向宿主发 `RefreshAuthorization` / `FindOriginalAudit` 两种意图，宿主提供显式 Context/Request/Key。不是“批准”按钮或自动业务重试。

### 10.1 布局和控件组合

控件公开形状冻结如下（全部在 `Asun.Modules.Authorization.Wpf`，引用 Core 的枚举和 AuditKey；不是已编译实现）。面板不持 IAuthorizationPort、Context、Request 或端口，宿主持这些对象并处理意图：

```csharp
public enum AuthorizationIntent { RefreshAuthorization = 1, FindOriginalAudit = 2 }
public sealed record AuthorizationPresentation(
    Guid RequestId, OperationState State, PolicyOutcome? Outcome,
    CommitEligibility Eligibility, AuditStatus? AuditStatus, AuthError Error,
    bool IsHistorical, AuditKey? OriginalAuditKey, string? AuditReference,
    string ActionLabelKey, string? VersionSummary, string? ScopeSummary,
    ImmutableArray<AuthError> Reasons, bool IsBusy);
public sealed class AuthorizationIntentEventArgs : EventArgs {
    public AuthorizationIntentEventArgs(AuthorizationIntent intent, Guid requestId, AuditKey? auditKey);
    public AuthorizationIntent Intent { get; }
    public Guid RequestId { get; }
    public AuditKey? AuditKey { get; }
}
public interface IAuthorizationTextSource {
    string GetText(string resourceKey, string cultureName);
}
// AuthorizationStatusPanel : System.Windows.Controls.UserControl
// public AuthorizationStatusPanel();  // 无 Core 操作、IO 或隐藏端口初始化
// public void SetPresentation(AuthorizationPresentation presentation,
//     int maxReasons, int maxIdentifierUtf8Bytes);
// public void SetLanguage(string cultureName, IAuthorizationTextSource texts);
// public event EventHandler<AuthorizationIntentEventArgs>? IntentRequested;
```

上述方法仅在实例 Dispatcher 线程调用，违例抛 InvalidOperationException；非法投影参数抛 ArgumentException，保留原非秘密关联、清旧许可/动作并显示 InvalidInput，不截断成许可。maxReasons/maxIdentifierUtf8Bytes 分别为宿主显式 Profile.MaxGrants/MaxIdentifierUtf8Bytes、均≥1；Reasons 非 default、每项已定义、长度≤maxReasons，重复错误去重排序。SetPresentation 深复制、清旧选择（相同 RequestId 时可保留）、不启动业务。只显示宿主已完成读取授权的脱敏投影；ActionLabelKey 必为宿主三语资源键，Version/Scope/Reference 按传入 UTF-8 字节预算及 §3.1 字符规则检查，不能含秘密，缺失显示空而非猜版本。SetLanguage 支持 zh-CN/zh-TW/en-US 和宿主新增资源齐全语言；缺键抛 ArgumentException 并保留原语言，不回退到 Exception.Message。语言变更不发意图、不重新核权。窗体关闭只由宿主 Dispose 本窗口订阅，控件不停止服务。

状态/唯一下一步优先级：先确定历史标签（IsHistorical 始终显示历史记录）；Draining/DrainUnknown 或 IsBusy→禁用动作；Audit.Unknown 且有 OriginalAuditKey→查询记录；其它非终态→显示待确认、无自动动作（宿主按原 request 查询进度）；当前终态 Allowed+NotRequired+Error.None→显示只读授权，无动作；当前 Allowed+Eligible+Persisted+Error.None→显示已授权，无提交按钮；其它终态→重新检查。历史不能显示当前已授权。投影矛盾（如历史Eligible、Cancelled/TimedOut/Failed却Eligible、Allowed+Eligible却无Persisted）按非法投影处理。FindOriginalAudit 必带原 Key；RefreshAuthorization 只带 RequestId 供宿主关联，新 Request/Context/期限由宿主生成，不能复用旧授权。Click 只发一次事件，宿主立即 SetPresentation(IsBusy=true) 去重；回调抛错由宿主处理，控件不重试。意图结果通过新投影显示，不伪造成功消息。首次 SetLanguage 前面板空且禁用意图；必须先设置语言再 SetPresentation，不引入默认账号或默认语言状态。

唯一验证基线物理屏幕 1920×1080；Host 窗口以可用客户区测量，扣 OS 任务栏、标题/边框/状态栏；不改显示设置、不另跑分辨率矩阵。嵌入面板客户区推荐 560×320 DIP 以上，由宿主提供尺寸。

- 顶部 36 DIP：状态图标+文字（状态始终可见）、动作摘要，右侧唯一安全下一动作。颜色不能唯一表达允许/拒绝；文本跟随状态。
- 中部在诊断展开时为70%宽的原因区、30%宽的版本/作用域及详细说明，折叠时原因区占满；非秘密版本/范围摘要仍可从底部摘要及SuperTip取得。原因以 DevExpress GridControl/TableView 只读行展示“原因/影响/下一步”，选择行联动右侧详细原因，不渲染原 grant/凭证。最多显示 Profile.MaxGrants 范围内的摘要，使用有界集合与行虚拟化，不另造分页服务，禁止 UI 全量数据库查询。
- 扩展诊断使用 DockLayoutManager 的内容面板嵌入，不浮动全局窗口；默认折叠。BaseLayoutItem.Caption/ContentItem.Content 显式实例绑定当前宿主语言；保留关闭后的选择和布局草稿，不持业务对象/秘密。
- 原请求/审计引用放底部 28 DIP 摘要带，可复制非秘密 Reference，审计内容仍须当前读取授权。版本摘要折行/省略 + DevExpress SuperTip（BarItem.SuperTip 或 SuperTipControl）显示完整脱敏内容；关键错误绝不仅藏在悬停提示。
- 禁止 PropertyGrid 直接编辑权限规则，TreeList/Chart/Flyout 若无真实任务不堆控件；不用“炫技”浮动动画遮住关键状态。只允许折叠/展开过渡，状态切换即刻可见，不把动画时长当授权期。

这里组合与公开内容绑定复用 §2.2 的目标版本资料，确定接线见 §10.3，两个 STA 宿主见 §10.4；未声称 WPF XAML 已编译。内置文字覆盖与虚拟化/DPI真实行为须按确定接线实际验证，不把内部装配推为外部门，也不把官网403改成普通 .NET 替代控件。

### 10.2 操作、三语与可用性

| 资源键 | zh-CN / zh-TW / en-US |
|---|---|
| auth.allowed | 已授权 / 已授權 / Authorized |
| auth.denied | 无权限 / 無權限 / Access denied |
| auth.pending | 待确认 / 待確認 / Pending |
| auth.expired | 会话已过期 / 工作階段已過期 / Session expired |
| auth.auditUnknown | 审计未确认 / 稽核未確認 / Audit pending |
| auth.refresh | 重新检查 / 重新檢查 / Check again |
| auth.findAudit | 查询记录 / 查詢紀錄 / Find record |
| auth.history | 历史记录 / 歷史紀錄 / Historical record |
| auth.readOnly | 只读授权 / 唯讀授權 / Read access |
| auth.reason / auth.impact / auth.next | 原因/影响/下一步 / 原因/影響/下一步 / Reason/Impact/Next step |
| auth.details / auth.reference | 诊断/记录引用 / 診斷/紀錄參照 / Diagnostics/Record reference |

所有 AuthError 的正文资源键为 `auth.error.<枚举名>`；以下三列是必须提供的 zh-CN/zh-TW/en-US 正文，不由异常文本生成：

| 枚举名 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| None | 检查完成 | 檢查完成 | Check complete |
| InvalidInput | 参数无效 | 參數無效 | Invalid input |
| VersionConflict | 版本不一致 | 版本不一致 | Version mismatch |
| SessionExpired | 会话已过期 | 工作階段已過期 | Session expired |
| ScopeViolation | 无权访问此范围 | 無權存取此範圍 | Scope access denied |
| PolicyUnavailable | 无法读取权限规则 | 無法讀取權限規則 | Policy unavailable |
| PolicyRejected | 无操作权限 | 無操作權限 | Action denied |
| StaleDecision | 授权已失效 | 授權已失效 | Authorization expired |
| DeadlineExceeded | 检查已超时 | 檢查已逾時 | Check timed out |
| Cancelled | 检查已取消 | 檢查已取消 | Check cancelled |
| Draining | 正在结束请求 | 正在結束請求 | Finishing requests |
| AuditUnavailable | 审计记录未确认 | 稽核紀錄未確認 | Audit unconfirmed |
| AuditConflict | 审计记录冲突 | 稽核紀錄衝突 | Audit conflict |
| AdapterFault | 权限服务响应无效 | 權限服務回應無效 | Invalid service response |
| ResourceLimit | 服务已达处理上限 | 服務已達處理上限 | Service limit reached |
| AuthorityChanged | 权限状态已变更 | 權限狀態已變更 | Authority changed |
| ApprovalRequired | 需要另一位授权人员复核 | 需要另一位授權人員覆核 | Second authorized reviewer required |
| RequestConflict | 请求编号重复且内容不同 | 請求編號重複且內容不同 | Request ID content conflict |
| NotFound | 未找到记录 | 未找到紀錄 | Record not found |
| NotSupported | 不支持此操作 | 不支援此操作 | Operation unsupported |
| DrainUnknown | 请求尚未确认退出 | 請求尚未確認退出 | Request exit unconfirmed |
| SubscriberFault | 状态通知失败 | 狀態通知失敗 | Status notification failed |
| InternalFault | 授权检查失败 | 授權檢查失敗 | Authorization check failed |

影响/恢复资源按以下分组，不遗漏错误：`auth.impact.blocked`=不能继续此操作/無法繼續此操作/Action blocked；`auth.impact.projection`=状态显示可能不完整/狀態顯示可能不完整/Status display may be incomplete（SubscriberFault）；`auth.impact.history`=记录不提供当前授权/紀錄不提供目前授權/Record grants no current authorization（历史及 NotFound）；None 当前成功无错误影响。下一步键：`auth.next.correct`=检查参数后重新检查/檢查參數後重新檢查/Correct input and check again（InvalidInput、RequestConflict）；`auth.next.signIn`=重新登录后检查/重新登入後檢查/Sign in and check again（SessionExpired）；`auth.next.contact`=联系管理员核对权限/聯絡管理員核對權限/Ask an administrator to verify access（ScopeViolation、PolicyRejected、ApprovalRequired、NotSupported）；`auth.next.find`=查询原记录，勿重复操作/查詢原紀錄，勿重複操作/Find the original record; do not repeat the action（AuditUnavailable、AuditConflict、NotFound）；`auth.next.wait`=等待请求退出/等待請求退出/Wait for the request to exit（Draining、DrainUnknown）；其它错误使用 `auth.next.check`=服务恢复后重新检查/服務恢復後重新檢查/Check again when the service recovers。资源提示是恢复说明，不增加第三个控件命令，不允许用户点击提示绕过两种意图或业务门。

Policy Allowed+Gate Blocked 不能显示单纯“已授权”，组合显示原因/下一步。所有 errors 与操作恢复映射固定 enum，不拿任意 Exception.Message 直接显示。语言由宿主注入只读投影资源+culture，Core 没有语言字段/切换器；生产主认证界面另由宿主提供。

Tab 顺序：安全下一动作→原因 Grid→诊断折叠→记录引用；Enter 仅执行焦点按钮，绝不触发产品提交；Esc 只关闭诊断，不取消业务。UIA AutomationId 依次 `Auth.NextAction`、`Auth.Reasons`、`Auth.Diagnostics`、`Auth.AuditReference`。忙状态禁止重复 refresh，Audit.Unknown 且有 Key 才提供“查询记录”，撤权清可写投影，保留非秘密原关联供恢复。英语最长文案允许换行，数字/ID按固定文化，不靠译文推回 enum。

刷新限流和刷新耗时从 WpfBenchmarkProfile 显式提供；测试完整展开、English长文本、键盘/UIA、同进程不同语言、慢事件、UI关闭及服务继续工作。尚无实际 WPF/DPI/性能资格，UI 切片保持后续门。

### 10.3 确定装配、DevExpress 实例绑定和文字覆盖

装配顺序唯一为：在宿主 STA/Dispatcher 创建 `new AuthorizationStatusPanel()` → 创建该实例的 `IAuthorizationTextSource` → `SetLanguage` → 用全部字段构造 `AuthorizationPresentation` → `SetPresentation(p, profile.MaxGrants, profile.MaxIdentifierUtf8Bytes)` → 显式 `IntentRequested += handler` → 放入本窗口 Content 并显示。公开形状仍只用 §10.1，不添加 Session、Root、Factory、Initialize/Dispose 或异步清理入口；面板本身没有外部 IO、timer、Core 订阅或后台任务。`SetPresentation` 替换当前纯投影，只有宿主可以调用 Core。

以下是面板内部一次性装配和每次投影的唯一绑定；内部行是私有展示数据，不增加公共 DTO。每行持有 `AuthError Code` 及从 §10.2 计算的 `string Reason/Impact/Next`，不持完整请求/Context/grant。语言更新可替换展示行，按 Code 恢复选择，不按译文反查身份。

| 实际实例/公开入口 | 确定值和更新方式 |
|---|---|
| `GridControl.ItemsSource`、`Columns`、`AutoGenerateColumns` | ItemsSource 为当前有界原因行集合；AutoGenerateColumns=`AutoGenerateColumnsMode.None`；显式三列 `GridColumn.FieldName`=`Reason/Impact/Next`，Header 分别取 `auth.reason/impact/next`。列宽按 2:2:3 分配，文字换行、顶部对齐；空原因不制造 None 错误行。 |
| `GridControl.View = new TableView()` | 实例属性 AllowEditing=false、AllowSorting=false、AllowGrouping=false、ShowGroupPanel=false、ShowAutoFilterRow=false、ShowTotalSummary=false、ShowIndicator=false、ShowSearchPanelMode=`ShowSearchPanelMode.Never`、NavigationStyle=`GridViewNavigationStyle.Row`、RowMinHeight=32；每列 AllowColumnFiltering=`DevExpress.Utils.DefaultBoolean.False`。SelectionMode=`MultiSelectMode.None`，不提供编辑/筛选/汇总/列选择器。 |
| `GridControl.SelectedItem` | TwoWay 绑定内部选中行；选择变化只更新右侧同 Code 的完整原因/影响/下一步和 SuperTip，不核权、不发意图。原因换代后旧 Code 不存在则清选中和详情；语言变化保留 Code/焦点/滚动位置，不能保留已不在集合的旧允许状态。 |
| `TableView.RuntimeLocalizationStrings` | 每个 view 独立 `new GridRuntimeStringCollection()`；加入 `new RuntimeStringIdInfo(GridControlRuntimeStringId.NoRecords, text)` 和 `NoRecordsFound`，text 均为 `auth.noReasons`；每次 SetLanguage 构造新集合一次赋值。禁止 `GridControlLocalizer.Active`、线程 Culture 或 Application.Resources。当前不启用 group/filter/search/summary 原生窗，故不存在这些窗的待翻译实施路径。 |
| Grid/Dock 原生菜单 | 在各实例的 `ShowGridMenu` / `DockLayoutManager.ShowingMenu` 事件内设 `e.Handled=true`，禁止原生布局/过滤/汇总菜单入口；不修改只读 Items，不扫描模板。右键与 Shift+F10 均不得弹出未登记菜单。这里关闭的是本面板无任务的菜单，不隐藏重新检查/查询记录/诊断等关键命令。 |
| `DockLayoutManager` → `LayoutGroup` → `LayoutPanel` | 仅本实例诊断区域，LayoutPanel.Content 为右侧详细说明；Caption=`auth.details`，AllowFloat/AllowDrag/AllowDock/AllowClose=false、ShowCloseButton/ShowPinButton=false，ShowCaption=true。由旁边自有诊断展开按钮切父容器 Visibility，默认 Collapsed；不创建 FloatGroup、原生 AutoHide 或第二窗口。语言只改 Caption/Content 中自有文字，选择与展开草稿留在该实例。 |
| 唯一下一动作与摘要 | DevExpress `SimpleButton.Content`/IsEnabled 取 §10.1 状态优先级；Click 同步发 IntentRequested。版本/作用域用自有 TextBlock，诊断用 Grid 联动的只读 TextBlock；非秘密引用用只读 TextBox 保留选择/复制，禁拼凭证或异常原文。 |
| DevExpress SuperTip | `new SuperTip()` 加 `SuperTipHeaderItem`/`SuperTipItem`，分别为当前动作/恢复说明和完整版本/范围；`new SuperTipControl { SuperTip = tip }` 给实际元素.ToolTip。每实例独立，在语言/投影更新时重建其有限 Items；不依赖 Popup 默认 DataContext/PatchDataContext。相同完整说明同时绑定 AutomationProperties.HelpText，不能只在悬停可读。 |

视觉实施沿宿主现有主题和字体，面板不写全局 ThemeManager：外沿12 DIP、同组4/跨组8 DIP，正文12–14 DIP，状态字14 DIP半粗，按钮最小高32 DIP、左右 padding12 DIP。顶部36 DIP/底部28 DIP是单行起始布局，采用 MinHeight+Auto 而非固定裁剪；长英文、换行或 DPI 导致增高时中部先让出高度，安全动作/状态不被覆盖。中部星号列默认7:3，诊断折叠时原因区占满；Grid 最小行高32且自动换行，保留行/键盘焦点细边框和交替行弱分隔。状态图形使用模块自有矢量 Geometry，允许/拒绝/未知各有不同形状及可见文字；只用宿主语义 Brush，不用颜色作唯一依据。没有新图标下载、自由浮窗或后台动效。

补充资源：`auth.noReasons`=无补充原因/無補充原因/No additional reasons；`auth.version`=版本/版本/Version；`auth.scope`=范围/範圍/Scope；`auth.action.production`=保存更改/儲存變更/Save changes；`auth.action.review`=提交意见/提交意見/Submit opinion。诊断展开/收起分别为 `auth.showDetails`=展开诊断/展開診斷/Show diagnostics、`auth.hideDetails`=收起诊断/收合診斷/Hide diagnostics；两个 Host 窗口标题键 `auth.host.production`=操作授权/操作授權/Action access、`auth.host.review`=记录恢复/紀錄復原/Record recovery。均进入同一实例 text source，新增文化须提供全部键。

`SetLanguage` 在同 Dispatcher 内先解析并校验 §10.2/本节全部键（含全部 AuthError、两种 action、可见列头/状态/提示/UIA），形成该次不可变文字快照后一次同步更新；任何键缺失/空值或 source 抛错都转换 ArgumentException，保留完整原语言，无半简繁混排。此调用不重新 SetPresentation、不调用 Core/Find、不增加意图；更新选中行说明时保留 Code，更新同一焦点元素，不换模板偷焦点。控件给语言相关元素设 `FrameworkElement.Language = XmlLanguage.GetLanguage(cultureName)`，不改进程/线程 Culture，ID/版本仍用不变格式。text source 是短时同步查词，禁止内部 IO/锁等待；违约慢查词会阻塞本 Dispatcher，不能伪称可取消，另一独立 STA Host 应仍响应。

UIA 显式用 `AutomationProperties.SetAutomationId/SetName/SetHelpText`：既有四 ID 保持，补 `Auth.Status`、`Auth.Action`、`Auth.Version`、`Auth.Scope`；状态 TextBlock 的 LiveSetting=Polite，Name 为本次组合状态，HelpText 为原因/下一步。Grid 三列 Header 及可见行 cell 文本均来自同一快照；单元格模板 TextBlock 从 Grid cell 的 `Value` 绑定文本，AutomationProperties.Name 同绑 Value，不能给所有虚拟行重复一个业务行 ID。右侧详情 Name/HelpText 包含选中 Code 对应自然文字；诊断按钮 Name 为当前展开/收起文字，引用框 Name=`auth.reference`、Value 为非秘密 Reference。自动化必须检查控件的实际 AutomationPeer 树和 Name/HelpText/Value，而不是只断言资源值；实际读屏通知/虚拟化后的行可达仍须运行验证。

上述新增入口于 2026-10-11 定向读取本机 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/` 官方 `DevExpress.Xpf.Grid.v25.2.Core.xml`、`DevExpress.Xpf.Grid.v25.2.xml`、`DevExpress.Xpf.Docking.v25.2.xml`、`DevExpress.Xpf.Core.v25.2.xml`，沿 §2.2 已绑定的25.2.3资料；FieldName 属 ColumnBase、Header 属 BaseColumn、ShowGroupPanel/AllowGrouping 属 GridViewBase，按真实继承入口使用。Grid/Dock 事件参数 Handled 的 public get/set 复用既有公开元数据 `public-signatures-4.json`；Runtime 字串与 SuperTip 用法复用 §2.2 固定官方示例。本轮另用 MetadataLoadContext 仅读公开签名，确认 GridCellData/EditGridCellData.Value 的公开 getter、非抽象 SimpleButton 的公开无参构造，程序集为25.2.3.0；未执行供应商控件或读取方法体。无 dxdocs 可调用；不重复抓取403页面、不核供应商授权、不读取内部。上述是明确实施路线，尚未编译或验证实际呈现。

### 10.4 两个独立 STA Host、意图接线和关闭

唯一 WPF 验证入口见 §12.1 的 Wpf.Tests；不是把 §8 的无 UI Host 改成依赖 WPF。下例是待实现的完整装配源形状，使用 §10.1 真实公开 API 和 .NET WPF API，未编译。`--host production` 与 `--host review` 是同一验证程序集的两个独立 STA 启动；前者消费受控写命令拒绝/重查投影，后者消费原审计未知/回查投影，两者各有窗口、资源快照、当前投影和委托。这里的值是显式 UI 合成夹具；捕获意图只验证面板边界，不把按钮测试伪装为认证/Find 成功。

测试资源基名固定 `Asun.Modules.Authorization.Wpf.Tests.AuthPanelStrings`，空中性清单 `AuthPanelStrings.resx` 和三个完整卫星资源 `AuthPanelStrings.zh-CN.resx`、`.zh-TW.resx`、`.en-US.resx` 在唯一 Wpf.Tests 中；每键逐字采用 §10.2/§10.3，中性清单不提供缺键兜底，不额外抄一套字符串到 C#。Host 的 text source 明确定义如下，构造时拷贝精确文化资源，不接受 ResourceManager 的父文化 fallback：

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Globalization;
using System.Linq;
using System.Resources;
using System.Threading;
using System.Windows;
using Asun.Modules.Authorization;
using Asun.Modules.Authorization.Wpf;

sealed class HostTextSource : IAuthorizationTextSource {
    readonly Dictionary<(string Culture, string Key), string> entries = new();
    public HostTextSource(ResourceManager resources) {
        string[] keys = ("allowed denied pending expired auditUnknown refresh findAudit history " +
            "readOnly reason impact next details reference noReasons version scope showDetails " +
            "hideDetails action.production action.review host.production host.review " +
            "impact.blocked impact.projection impact.history next.correct next.signIn " +
            "next.contact next.find next.wait next.check").Split(' ');
        foreach (string culture in new[] { "zh-CN", "zh-TW", "en-US" }) {
            var set = resources.GetResourceSet(CultureInfo.GetCultureInfo(culture), true, false)
                ?? throw new ArgumentException("Missing exact culture resources", nameof(resources));
            foreach (string key in keys.Select(k => "auth." + k)
                .Concat(Enum.GetNames<AuthError>().Select(n => "auth.error." + n))) {
                string value = set.GetString(key, false)
                    ?? throw new ArgumentException("Missing resource: " + key, nameof(resources));
                if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException("Empty resource", nameof(resources));
                entries.Add((culture, key), value);
            }
        }
    }
    public string GetText(string resourceKey, string cultureName) =>
        entries.TryGetValue((cultureName, resourceKey), out string? value) ? value :
        throw new ArgumentException("Missing resource: " + resourceKey, nameof(resourceKey));
}

static class AuthorizationPanelHosts {
    [STAThread]
    public static int Main(string[] args) {
        if (args.Length != 2 || args[0] != "--host" ||
            (args[1] != "production" && args[1] != "review")) return 2;
        if (Thread.CurrentThread.GetApartmentState() != ApartmentState.STA) return 2;
        bool review = args[1] == "review";
        var resources = new ResourceManager(
            "Asun.Modules.Authorization.Wpf.Tests.AuthPanelStrings", typeof(AuthorizationPanelHosts).Assembly);
        try {
        var texts = new HostTextSource(resources); // 每个Host自己的只读快照
        string culture = review ? "en-US" : "zh-CN";
        var panel = new AuthorizationStatusPanel(); // 不取得Core/服务/当前账号
        panel.SetLanguage(culture, texts);
        Guid requestId = Guid.Parse(review ? "22222222-2222-2222-2222-222222222222" :
            "11111111-1111-1111-1111-111111111111");
        AuditKey? originalKey = review ? new AuditKey("tenant-b", requestId) : null;
        var current = new AuthorizationPresentation(
            RequestId: requestId, State: OperationState.Completed,
            Outcome: review ? PolicyOutcome.Allowed : PolicyOutcome.Denied,
            Eligibility: CommitEligibility.Blocked,
            AuditStatus: review ? AuditStatus.Unknown : AuditStatus.Persisted,
            Error: review ? AuthError.AuditUnavailable : AuthError.PolicyRejected,
            IsHistorical: false, OriginalAuditKey: originalKey,
            AuditReference: review ? null : "test-audit-a",
            ActionLabelKey: review ? "auth.action.review" : "auth.action.production",
            VersionSummary: "policy-1 / 1", ScopeSummary: review ? "scope-b" : "scope-a",
            Reasons: ImmutableArray.Create(review ? AuthError.AuditUnavailable : AuthError.PolicyRejected),
            IsBusy: false);
        panel.SetPresentation(current, 128, 256); // §9 SyntheticProfileV1，不是生产默认
        var captured = new List<AuthorizationIntentEventArgs>();
        bool presenting = true;
        var expected = review ? AuthorizationIntent.FindOriginalAudit : AuthorizationIntent.RefreshAuthorization;
        EventHandler<AuthorizationIntentEventArgs> handler = (_, intent) => {
            if (!presenting || current.IsBusy || intent.RequestId != current.RequestId) return;
            if (intent.Intent != expected || intent.AuditKey != current.OriginalAuditKey) return;
            captured.Add(intent); // 夹具断言用；生产桥按下文发起原Task
            current = current with { IsBusy = true };
            panel.SetPresentation(current, 128, 256); // 在返回Click前去重
        };
        panel.IntentRequested += handler;
        var window = new Window {
            Title = texts.GetText(review ? "auth.host.review" : "auth.host.production", culture),
            Width = 840, Height = 520, Content = panel
        };
        window.Closing += (_, _) => {
            presenting = false;                 // 先停止所有后续呈现
            panel.IntentRequested -= handler;   // 同一Dispatcher对称退订
            window.Content = null;              // 不调用Core.Cancel/Stop，不丢originalKey
        };
        try {
            window.ShowDialog(); // 本STA消息泵；正式自动化通过UIA点击/切语言/关闭
            if (captured.Count != 1) return 1;
            return captured[0].Intent == expected && captured[0].RequestId == requestId &&
                captured[0].AuditKey == originalKey ? 0 : 1;
        }
        finally { panel.IntentRequested -= handler; }
        }
        finally { resources.ReleaseAllResources(); }
    }
}
```

两 Host 的确定正常断言：A 点重新检查一次（再点不发第二意图），捕获 RefreshAuthorization+原 RequestId、AuditKey=null；B 点查询记录一次，捕获 FindOriginalAudit+完全相同 `AuditKey("tenant-b", requestId)`。关闭各窗口后 Count 不增、无 Core.Cancel/Stop、无其它 Host 的文字/状态变化。夹具必须先完成点击断言再由 UIA 关闭，未点击而手动关闭返回1；它不提供默认成功。另用两个明确 `Thread` 分别执行同一装配体（线程各 `SetApartmentState(ApartmentState.STA)`）验证同进程隔离，不能在一个 Dispatcher 上创建两个窗口冒充独立 STA。宿主主题由既有应用根注入，本控件不改变全局主题；纯验证 Host 可沿 DevExpress 当前实例默认主题渲染，不以此取得产品视觉资格。

真实宿主桥复用 §8 的显式 `AuthorizationService(profile, authority, fence, audit, timeProvider)` 和受信 Context/当前意图；不重复定义 Core API。以下顺序是该宿主必须实现的确定桥，不需要新模块生命周期：

1. 宿主模型独立持有当前请求、原 `AuditKey`、最后结果以及 `Task<CallResult>? authorizationTask` / `Task<AuditLookupResult>? findTask`。每个窗口只持当前纯投影、单个委托、`bool presenting` 和单调 `long projectionRevision`；这些是宿主局部字段，不作为模块 Session/Root。只有在本 Dispatcher 上确认 presenting、intent.RequestId 与当前投影相同、原 Key 完全相同且当前不 Busy 时接纳意图；同步先设置 Busy 再返回事件回调，最多一个原Task在途。不用 async void 丢失异常。
2. RefreshAuthorization 保留原意图的 Context/Action/Resource/Use/ExpectedPolicy/PurposeCode，取一次 `DateTimeOffset now = clock.GetUtcNow()`，用 `AuthorizationRequest nextRequest = request with { RequestId = Guid.NewGuid(), CreatedAtUtc = now, DeadlineUtc = now + profile.MaxRequestDuration }`，赋给 `authorizationTask = core.AuthorizeAsync(nextRequest, CancellationToken.None).AsTask()`，原请求仅作关联。派发前在同 Dispatcher 递增 projectionRevision、保存新请求和本次版本，把当前投影 RequestId 换为新ID、State=Accepted、Outcome=null、Eligibility=Blocked、AuditStatus=null、AuditReference=null、Reasons为空、Error=None、IsHistorical=false、IsBusy=true；新任务回执以此新ID/版本校验，不与旧ID混用。若原业务结果未确定，不触发自动刷新：先按原 Key 查记录。新授权审计 Key 属新 RequestId，只有无未决恢复项时才替换当前 OriginalAuditKey；宿主独立恢复模型不得覆盖尚待恢复的旧 Key。只允许 §10.1 定义的安全下一步。这里示例的 None 是明确继续观察策略，UI关闭不自动取消Core请求。
3. FindOriginalAudit 原样取模型中保存的 Key，赋给 `findTask = core.FindAuditAsync(currentContext, originalKey, CancellationToken.None).AsTask()`；currentContext 是本次受信读取身份，不从 panel/旧 Actor 恢复凭证。每次重复回查同 Key，Unknown/NotFound 不改 AuditId、不触发 Authorize/业务重做。回查 Persisted 仅更新历史审计/Reference，IsHistorical=true、Eligibility=Blocked；读到原 Allowed 也不显示当前已授权。回查越权清记录正文/成功投影，保留脱敏原 Key 供宿主有权恢复，绝不回退到旧全文。
4. 宿主异步方法先保留原 typed Task 和当次 RequestId/Key/模型版本，再 await 原Task（若用后台观察则 ConfigureAwait(false)）；同步派发抛错与Task异常均由宿主捕获，先记录到独立宿主模型，使用 InternalFault/Blocked 投影，不显示异常原文、不重新提交。然后用本窗口 `Dispatcher.InvokeAsync(Action)` 投递一个短呈现，执行内再次检查 presenting、投影版本、RequestId/Key；只有完全相同当前意图才 `SetPresentation`。版本落后、同ID旧进度或窗口已关闭仅记录结果，不写新窗口、不重建panel。Pending 只用 `core.GetOperationAsync(context, requestId, ct)` 继续查原请求，不把 Pending 转成最终许可；单窗口最多一个待处理查询和一个待执行呈现。基线不要求Core事件订阅；宿主已有事件则只作查询提示，重复提示合并，不按每个事件排无限 Dispatcher 工作项。
5. UI关闭在同 Dispatcher 顺序置 presenting=false、递增 projectionRevision、`IntentRequested -= handler`、移除 Content/停止呈现。宿主若原已有 `SubscribeAsync` 订阅，在此 Dispose 自己的 token；关闭后才返回的 SubscriptionReply 也须立即 Dispose 其 Subscription，不先交给新窗口，不据Dispose推断Core回调退出。已有异步呈现若尚未执行必须在进入时因版本失效而不写；若 Dispatcher 已关闭/投递被撤销，捕获 TaskCanceledException/InvalidOperationException，只标本次“未呈现”，原Task结果仍由宿主模型保留。窗口关闭不 Dispose 借用 Core、不取消原业务、不清 Context/Task/原 Key。宿主服务/业务Task的真正退出和排空继续遵守已接收 §5–§7，不能靠这里的纯 UI 退订推断业务资源已释放；若整个测试进程将退出，先由测试拥有者完成其受控 Task 和 §7 Stop，再退出进程，不把窗口关闭当测试清理成功。

宿主模型的Task/最后结果更新用短 `lock` 串行，只保存不可变业务技术结果，不把 panel/Window 放进持久恢复项。后台观察仅捕获宿主模型、Dispatcher和 `WeakReference<AuthorizationStatusPanel>`；短 Dispatcher Action 内 `TryGetTarget` 并再次校验本窗口版本，失效只跳过呈现，原Task不转交给UI树。`presenting/projectionRevision` 仅在所属 Dispatcher 上读写；后台不根据未同步 bool 猜窗口仍存活。宿主若允许取消 Closing，先决定 e.Cancel，确认接受关闭后才执行第5步；取消关闭不能先退订再让一个无反馈窗口继续显示。

结果到全字段投影的确定映射如下，仍只调用 §10.1 的构造器/SetPresentation，不增加隐式 converter API：RequestId=当次被接纳请求ID；State=Progress.State（Rejected 无Progress时用Failed表达该次UI失败，不能宣称Core已创建终态）；Outcome/Eligibility/IsHistorical 分别取 Decision.Policy.Outcome/Decision.Eligibility/Decision.IsHistorical，在 Decision=null 时为 null/Blocked/false；AuditStatus/Reference 取 Progress.Audit 或 Decision.Audit，未取得则null；Error 优先 CallResult.Error、Progress.Error、Decision.GateError、Decision.Policy.Error，均None才None；Reasons 是上述非None错误去重并按enum值排序；OriginalAuditKey 保留该次请求的审计恢复Key，若宿主还有更旧未决Key则作为独立恢复项保留，不能把旧Key误标为新请求审计。ActionLabelKey 取宿主登记的动作键，VersionSummary/ScopeSummary 取当次请求的 ExpectedPolicy/ScopeId 脱敏值；IsBusy 仅当该次原Task已返回且请求不再Pending时清false。历史查询强制IsHistorical=true、Blocked；Find结果保留原RequestId和原Key，State=Completed只表示查询观察结束，不能冒充业务Completed；审计状态/Reference取Lookup.Receipt，Outcome仅在有原Record时取原PolicyOutcome，版本/范围若无读取权清空。所有历史/回查投影都不能激活提交资格。

语言切换直接在当前 Dispatcher 调 `panel.SetLanguage("zh-TW", texts)` 或 `"en-US"`；只有成功后宿主把自己窗口 Title 改为同文化键。当前投影/Busy/RequestId/原 Key/Task 不变，不从语言变更启动第二次查询。语言版本和投影版本分别记录：旧任务回来的事实用**当前**语言文字投影，不把旧语言快照回写。必要引用只保留不可变非秘密值，已经关闭的 UI 树不得被宿主长期结果表持有。

### 10.5 两轮有限自审与实现验收断言

第一轮“空宿主从零装配”已按 §10.3→§10.4 检查：无参构造没有隐藏服务；精确资源集合可由正文逐键建立；两 Host 全字段投影和实际委托订退齐全；按钮只产生已定义意图；原Task、身份/审计Key和纯UI寿命分离。第二轮“异常/换语言/慢事件/关闭/新旧投影”已按下表走查，消除把内部装配推成外部门的缺口；这是指导自审，没有执行 WPF：

| 场景 | 必须执行的处理与可判定断言 |
|---|---|
| 三语缺键、source抛错、非法投影/错误Dispatcher | SetLanguage 保留原完整语言并 ArgumentException；非法投影按 §10.1 清许可，错线程 InvalidOperationException；不发意图、不调用Core。首屏资源缺失不显示可用按钮。 |
| A简体→繁体→英文，B英文不变 | 当前action/列头/状态/原因/诊断/提示/UIA和NoRecords两项完整更新；A的Code选择/焦点/Key/Busy不变，B文字与实例集合不变；CurrentCulture/CurrentUICulture不改。 |
| 连点/Enter重复、旧RequestId意图、旧Key事件 | 当前Busy在首个同步回调内置真，真实Core/Find调用计数≤1；过期意图丢弃，原Key不被新投影Key覆盖；Enter不提交业务。 |
| 慢Core/Find及事件风暴 | 原Task保持独立所有权；UI线程不Wait/Result；单窗口至多一个查询/呈现，事件可合并，另一STA仍可操作；原Task真实完成前不伪造审计成功。 |
| 回查Unknown→NotFound→Persisted、换会话越权 | 三次同原Key；前两次保留未确认，最后仅历史回执/Blocked；越权不展示原Record，无新AuditId、无重复业务。 |
| 窗口关闭先于任务完成/Dispatcher排队呈现 | 先停止呈现再退订；任务完成进入宿主模型，旧版本不写关闭或重新打开窗口；关闭A不Stop共享Core/B；原Task/原Key仍可由服务层恢复。 |
| 窗口关闭晚于一次短setter | 已完成的最后投影可见，退订后无新意图/呈现；setter结束才算该次呈现返回，不把已执行内容称撤回。 |
| 旧进度迟于新投影、新语言先于旧任务结果 | RequestId/Key/版本双检查挡旧进度；结果事实保持原身份、文字用当前语言；不恢复旧Eligible/旧Busy/旧选中原因。 |
| Grid/Dock/超长英文/UIA | 固定1920×1080客户区实测：关键动作/状态可读、细节联动/复制/Tab/Esc有效，右键/Shift+F10无原生菜单；NoRecords和实际AutomationPeer文本同语言；短setter不能代替真实布局/虚拟化/DPI验证。 |

实现验证必须从相同已构建 Wpf.Tests 分别运行 `--host production`、`--host review`，另执行同进程双STA隔离用例；测试进程有限观察到期返回非零并保留未完成任务身份，不创建无限后台补偿。WpfBenchmarkProfile 冻结最大Reasons=Profile.MaxGrants、空/单/上限原因、三语最长正文、切换次数、事件突发数量、Dispatcher排队/呈现时间及托管对象/订阅计数；阈值来自消费者Profile，缺阈值为NotEvaluated。真实 DevExpress25.2.3编译、内置文字/UIA树与读屏、1920×1080布局/DPI/性能和两个Host行为仍未执行；这些是AU-W1运行门，不是未定义内部API。生产签发/fence/审计durability/客户策略仍只在AU-I1关闭。主控于2026-10-11回读0.3.2-prep §10.3～§10.5及§12.1，已限定接收纯投影Panel的DevExpress实例接线、完整三语资源、两个独立STA Host、意图去重、原AuditKey恢复与Window寿命分离指导内容；不提升W1为CoreReady，真实运行资格保持PreparationIncomplete / NotReady。

## 11. 可执行测试和 BenchmarkProfile

### 11.1 唯一测试落点与断言

`tests/Modules/authorization/Asun.Modules.Authorization.Core.Tests` 使用仓库既有 BCL smoke Host 形状：TargetFramework=net10.0、OutputType=Exe，仅 ProjectReference 到本 Core，无新 NuGet。复用依据为既有 `tests/Asun.Vision.Contracts.Smoke` 的工程及退出码断言方式，不复用视觉契约。Program 调各测试组，收集失败，成功返回0、任一失败返回1；异步组逐项 await，未捕获异常也失败。唯一执行命令为 `dotnet run --project tests/Modules/authorization/Asun.Modules.Authorization.Core.Tests/Asun.Modules.Authorization.Core.Tests.csproj -c Release`；`dotnet test` 不执行此 Exe harness，不能把其无测试输出当 PASS。测试组名不是 xUnit API；定义以下消费者用途断言：

- `EvaluationTests`：§9.1 所有求值/边界；相同请求/快照/utc 重排 grant 不改变 Deny 优先结果。
- `TenantIsolationTests`：六维 Context、资源/Key租户、跨租户 query/cancel、新旧 epoch。
- `AuthorizationRaceTests`：TaskCompletionSource Barrier 安排 read→audit→fence→host commit 的撤权/资源换代；不靠 Sleep 猜顺序。
- `AuditRecoveryTests`：同 Key同内容、异内容、Unknown、成功应答丢失、空查、磁盘满注入、宿主业务已提交后审计拒绝。
- 上述组追加 §9 的用途/读写降级、跨role同名与合计预算、evidence缺失/冲突、同SnapshotId变内容、重启原记录关联；`LifecycleTests` 必覆盖辅助Find/核权不退出及发布终态前过期，断言在途owner/槽计数真正归零才Stopped。
- `LifecycleTests`：预检短拒绝、Pending、迟到、每请求/实例排空分离、重复 Cancel/Stop、订阅异常/阻塞/队列满；逐事件 Sequence/终态一次/资源计数。
- `HostContractTests`：ProductionPortHost/ReviewToolHost 同库不同端口，无 UI、无产品程序集；Core public assembly 不暴露 ClaimsPrincipal/SDK/WPF/平台类型。
- `CompatibilityTests`：Profile/snapshot/policy major/revision/hash、旧历史查询与新授权、升级回退空缓存；**回退不能恢复撤权授权**。

Pure Core 不模拟 native 图像资源/HIL；Simulator 只证明确定性软件路径。真实审计 durability、认证/策略服务、业务 fence 和授权安全红队/现场指标分别验收。正式平台 Schema映射未闭合不改变这些测试预期。

### 11.2 BenchmarkProfile

分位/端到端规则直接引用 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，不另定义 quantile。Profile 冻结请求/快照/Profile版本hash、合成或真实标志、动作/Use/tenant数量、grant数量、deny/permit比、索引冷/热、预热数/实测数/最低有效样本数、并发/批次、有限 deadline/shutdown、资源上限、目标来源与失败行为。

测点：预检、authority primary/approver、index构建/求值、audit append/find、fence、排队、取消到真实退出、请求 ResourcesReleased、服务Stop排空；每点使用同 TimeProvider monotonic elapsed。端到端统计不只测 Evaluate。资源计数包括在途/保留、cache、notification queue、订阅、适配器连接/流、managed bytes/GC/CPU、线程与未决数。

负载至少覆盖空/1/上限/超限 grants，单租户/多租户，冷/热索引（无 Allow缓存），常规/撤权风暴/审计未知，concurrency1/上限/超限。跨产品 P50/P95/P99、资源与撤权延迟目标由正式消费者 Profile 采纳；缺目标只作诊断测量 `NotEvaluated`，删除旧无依据 5/10/15ms“候选指标”。超时/失败/排空未知不得剔除后报性能通过。长期 duration/增量率/稳态资源斜率在负载Profile显式，不把短跑当长期证据。

## 12. 唯一工程绑定、切片与六项准备结论

### 12.1 落点与允许/禁止路径

- Core：`src/Modules/authorization/Asun.Modules.Authorization.Core/Asun.Modules.Authorization.Core.csproj`；TargetFramework=`net10.0`；namespace=`Asun.Modules.Authorization`；契约随 Core 发布，不为形式创建空 Contracts。
- 唯一 Core 测试/两个最小 Host：`tests/Modules/authorization/Asun.Modules.Authorization.Core.Tests/Asun.Modules.Authorization.Core.Tests.csproj`。
- 可选 Wpf：`src/Modules/authorization/Asun.Modules.Authorization.Wpf/Asun.Modules.Authorization.Wpf.csproj`，`net10.0-windows`、UseWPF；namespace=`Asun.Modules.Authorization.Wpf`。ProjectReference 到本 Core；使用本机 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/` 的 `DevExpress.Data.v25.2.dll`、`DevExpress.Mvvm.v25.2.dll`、`DevExpress.Xpf.Core.v25.2.dll`、`DevExpress.Xpf.Grid.v25.2.Core.dll`、`DevExpress.Xpf.Grid.v25.2.dll`、`DevExpress.Xpf.Docking.v25.2.dll`（25.2.3），不从 NuGet 替换，不写全局主题。
- 唯一 WPF 双 Host 验证：`tests/Modules/authorization/Asun.Modules.Authorization.Wpf.Tests/Asun.Modules.Authorization.Wpf.Tests.csproj`，`net10.0-windows`、UseWPF=true、OutputType=Exe、RootNamespace=`Asun.Modules.Authorization.Wpf.Tests`，ProjectReference 到本 Core/Wpf；§10.4 源形状落 `AuthorizationPanelHosts.cs`，卫星资源基名按同节固定。实现获准后命令为 `dotnet run --project tests/Modules/authorization/Asun.Modules.Authorization.Wpf.Tests/Asun.Modules.Authorization.Wpf.Tests.csproj -c Release -- --host production` 及同命令 `--host review`；另按 §10.4 验同进程双STA。该切片须另行派发，不扩本次 Core允许路径；本轮不创建这些工程/资源。
- 当前上述模块工程目录不存在，本轮未创建工程；仓库既有平台客户端授权 Smoke 不等同此模块实现，不反向固定本页 Core。
- 获准 Core 代码任务只写指定 Core/test 两目录；其它模块、平台业务工程、客户项目、原件、AsunImage内部、shared Contract/入口/登记为禁止路径。解决方案/共享引用需主会话串行接收，不在模块内偷改。
- 本轮文档任务只改本 DEVELOPMENT-GUIDE.md，任何代码派发前另核权威源码快照/分支（当前无 .git）；本条不是未授权代码任务的开工许可。

### 12.2 全模块能力切片（不以首片代整模块）

| 切片 | 完整内容与本页依据 | 后续依赖门 |
|---|---|---|
| AU-C1 契约/纯求值 | §3/§4：所有公开值类型、校验、有界grant、空/多候选/二人复核/租户/expiry，§9.1测试 | 六项文档规格已接收；无需账号服务/视觉/产品Schema；实现与运行验证另行派发 |
| AU-C2 协调与实例 | §5/§7：全部异步端口、当前authority/fence、规则索引、Recheck、请求query/cancel、事件、Stop；§9.2生命周期/竞争 | 完整端口Simulator可先做；真实认证/fence协议后续Integration |
| AU-C3 审计与恢复 | §6：Append/Find完整原记录、HostOutcome、Unknown/Conflict、隔离/保留与两个Host软件链，含重启后的原Key关联恢复 | 软件恢复在Core定义；真实durability、当前来源追加/读取凭证、宿主事务Outbox及生产映射后续验收 |
| AU-W1 可选原因投影 | §10全部场景/控件/三语/键盘/UIA/关闭，无账号/质量页面 | 真实WPF25.2.3编译、内置文字/浮动与DPI、1920×1080行为/性能 |
| AU-I1 实际消费集成 | §8.1～§8.4可信端口/会话绑定、同权威事务提交fence、完整审计逻辑映射、原意图恢复/根Owner和双消费者；§13生产发布 | 当前来源/凭证及产品正式映射采纳、实际provider/提交协议实现、真实durability/安全/长稳/部署验证；软件步骤已定 |

AU-C1–C3 是完整独立服务 Core 的连续切片；不能只实现求值函数就宣称 authorization 全模块完成。AU-W1/AU-I1 的外部门不阻断纯 Core，反过来Simulator不关闭这些门。

### 12.3 DEV-GOV-010 §3.1 六项结论（核心规格准备已接收）

主控会话 `01a1020f-126c-7242-97f9-0f50b4cd3553` 于 2026-10-09 完成本轮唯一指导走查，接收 AU-C1～C3 的六项文档规格；本永久会话仅同步该接收结果，不重审、不修改契约或测试预期。三个切片状态均为 `ModuleCoreImplementationReady`（仅规格准备）。

| 项 | 本轮闭合位置 | 准入结论 |
|---|---|---|
| 1 稳定责任/第二消费者 | §1/§8，两个不同宿主及禁止副作用 | AU-C1～C3 文档规格已接收 |
| 2 精确namespace/API/单位/状态/资源/兼容 | §3–§7，一个Module API Contract，无第二候选签名 | 文本已定义；本轮未编译契约，不能据表宣称代码就绪 |
| 3 无UI最小Host/显式端口 | §1.3/§8，Core BCL、不依赖业务或视觉 | 接线与夹具规格明确，待获准构建验证 |
| 4 正常/边界/失败/并发/取消/迟到/关闭/回退 | §9/§11.1，Barrier与可判定错误/资源断言 | 测试计划已冻结，未运行 |
| 5 Benchmark/资源/P50/P95/P99/失败来源 | §11.2+DEV-GOV-010，显式Profile及未评价语义 | 测量方法已冻结，真实目标/测量未验 |
| 6 工程/test/路径/最小顺序/后续门 | §8/§12.1–2 | AU-C1～C3 工程/路径/顺序规格已接收；无.git代码审计快照和实际实现派发仍须主会话确认 |

AU-C1～C3 已逐项接收为 `ModuleCoreImplementationReady`（仅规格准备）；这不表示代码已实现或本轮已获代码任务。AU-W1 的§10.3～§10.5/§12.1确定指导内容已由主控限定接收，真实WPF/UIA/性能资格仍 `PreparationIncomplete / NotReady`；AU-I1 凭证/fence/审计/产品资格仍 `PreparationIncomplete / NotReady`，保持 `IntegrationBlocked`。平台 C-01～C-08 正式映射、生产适配器、UI、真实安全性能和现场资格均不因本表获得批准。

逐切片结论如下；“文本满足”只回答 §3.1 本轮六项准备要求。AU-C1～C3 已由主控接收，不把未执行编译/测试混为文档缺项；实际代码任务仍须另行派发。序号与上表一致：

| 切片 | 1 责任/消费者 | 2 API/状态 | 3 无UI Host | 4 可判定样例/测试 | 5 Benchmark | 6 工程/顺序/门 | 当前结论 |
|---|---|---|---|---|---|---|---|
| AU-C1 | §1/§8 文本满足 | §3/§4 文本满足 | §8 BCL求值/显式fixture满足 | §9.1/§11.1满足 | §11.2求值/索引测点满足，目标待Profile | §12.1满足 | ModuleCoreImplementationReady（仅规格准备）；主控六项接收，不等待真实账号或WPF |
| AU-C2 | §1/§8 文本满足 | §3/§5/§7满足，含辅助IO | §8端口+Barrier Host满足 | §9.2/§11.1满足 | §11.2排空/并发资源满足，目标待Profile | §12.1及先C1后C2满足 | ModuleCoreImplementationReady（仅规格准备）；主控六项接收，真实提交原子性只阻断AU-I1 |
| AU-C3 | §1/§6/§8满足 | §3/§6完整回查/恢复满足 | §8双Host及MemoryAudit满足 | §9.2/§11.1重启/未知断言满足 | §11.2append/find资源满足，目标待Profile | §12.1及先C1/C2后C3满足 | ModuleCoreImplementationReady（仅规格准备）；主控六项接收，durability及生产恢复证据属AU-I1 |
| AU-W1 | §10投影边界满足 | §10.1–3输入/意图/语言和实例绑定文本满足 | 不适用纯Core门：§10.4双STA Host消费纯投影控件 | §10.5两轮有限自审及行为断言明确，实测未执行 | §10/§11.2维度已定，消费者目标待采纳 | §12.1唯一Wpf.Tests/资源/命令已定，代码任务未获准 | 确定指导内容已由主控限定接收；真实运行资格PreparationIncomplete / NotReady，不授予ModuleCoreImplementationReady，真实25.2.3/WPF/1920×1080/UIA/性能仍未验 |
| AU-I1 | §1/§8消费者边界满足 | §3及§8.1–3软件协议/逻辑映射明确；生产来源/正式平台映射未采纳 | §8.4完整双Host装配/根Owner明确，不能替代生产 | §8.4新增场景及§9/§11断言已定；真实安全/恢复/长稳未验 | 方法明确；客户负载/阈值未采纳 | §12.1–2/§13后续门明确，实际provider落点随消费者采纳 | PreparationIncomplete / NotReady，保持IntegrationBlocked；软件设计闭合，不冒充真实凭证/fence/durability/产品资格 |

最小实现顺序为 AU-C1契约/纯求值→AU-C2 Simulator与协调/生命周期→AU-C3恢复及双Host；之后分别申请 AU-W1/AU-I1 已定义切片。Core 测试、编译、资源与诊断测量仍须在获准实现后执行。§8.1–4 已明确适配接线、实际CommitOwner原子协议、审计逻辑映射和持久意图恢复的软件设计，不能把其实现工作统称为客户外部门；真正外部事实/采纳与未执行运行资格按 §12.4 分开。不得重新核验AsunImage/DevExpress安装或许可。

### 12.4 当前架构全部批准范围的最终准备结论

2026-10-11，0.3.3-prep：本永久原会话完成全范围收口，**没有剩余可由本模块决定的软件设计欠账**。本结论覆盖 §1.1 七项能力、维护/工程消费者的同一路线、无UI及可选WPF、生产适配边界与异常恢复；不是仅宣布AU-W1最后任务结束。复用既有有效研究、Core六项接收及WPF自审/限定接收，不重复全审。新增 §8.1–4 已完成两轮有限文档自审；总控只接收本结论并串行维护共享状态，本轮不再等待总控内容复核。

| 全批准范围 | 软件设计结论与唯一位置 | 保持的资格状态 |
|---|---|---|
| AU-C1 授权/双人/默认拒绝 | §3–4/§8/§9.1/§11：输入、确切求值、参数、错误、两个消费者与验收明确；既有接收保持 | ModuleCoreImplementationReady，仅规格；未实现/运行 |
| AU-C2 当前核权/撤权/缓存/请求生命周期 | §5/§7/§9.2/§11：实际与期望权威、有限IO/通知/Stop、取消迟到及回退明确；既有接收保持 | ModuleCoreImplementationReady，仅规格；未实现/运行 |
| AU-C3 审计/回查/结果追加/隔离 | §6/§8/§9/§11：正交状态、完整原记录、原Key重启关联及技术权限明确；既有接收保持 | ModuleCoreImplementationReady，仅规格；真实durability不在Core接收内 |
| AU-W1 可选纯原因投影 | §10.1–5/§12.1：DevExpress25.2.3实例绑定、三语、UIA/键盘、双STA、意图/原Task/Window寿命和验证明确；限定内容接收保持 | PreparationIncomplete / NotReady；真实WPF资格未验 |
| AU-I1 可信适配和实际消费 | §8.1–4/§13：路由/会话/命令/技术权、提交/撤权线性化、完整审计映射/幂等、持久意图恢复及根Owner明确；没有把可决定设计推给客户 | PreparationIncomplete / NotReady，IntegrationBlocked；产品正式绑定和实际实现/运行未验 |

剩余项及 Owner 必须按下表处理，不用“代码未授权”免除Adapter/UI/恢复设计，也不把缺失运行证据改称文档欠账：

| 剩余项 | 明确 Owner与关闭依据 | 性质/影响 |
|---|---|---|
| 实际认证来源、凭证、当前撤权/二人策略与租户/资源映射 | 消费者认证/策略 Owner与领域资源 Owner提供受信来源和访问凭证，按 §8.1绑定；不扫描凭证或默认管理员 | 产品输入/外部事实，影响对应AU-I1路由；不阻断纯Core |
| 平台 C-01～C-08及实际provider/组合根采纳 | 平台Contract Owner和消费者工程 Owner，由总控协调原Owner串行采纳本页字段/协议并定位实际宿主工程、公开provider API及部署配置 | 产品正式采纳/实现任务；本模块不猜未知客户工程或另立公共Schema |
| 授权事务与真实CommitOwner协议、业务幂等/待审计意图 | 消费者CommitOwner实现 §8.2–3，与认证权威 Owner证明撤权共享线性化点，执行竞争/提交响应丢失/容量/恢复测试 | 已定设计的实现/运行证据；若实际权威不支持该原子协议，仅相关生产写路径IntegrationBlocked |
| 审计provider的原子唯一性/完整Find/持久恢复与保留 | AuditStore Owner实现 §8.3，产品数据治理 Owner采纳durability/保留策略；验证应答丢失、损坏、重启、隔离及原Reference | 实现/运行资格及消费者保留事实；内存夹具不关闭此门 |
| Core/双Host/适配/WPF代码与运行验证 | 本永久模块会话在另行授权的实施切片中执行，消费者原Owner负责其宿主工程；§11及§10.5断言不得跳过 | 当前未执行编译、Core/双Host、真实provider、安全/长稳，亦未执行WPF/UIA/三语/1920×1080行为验证 |
| 性能负载/目标、部署与现场采纳 | 消费者Profile Owner采纳§11.2负载/阈值；产品交付 Owner执行Golden/Replay、安全/故障恢复、性能及现场验收 | 无真实P50/P95/P99/资源/长稳/现场证据，缺目标NotEvaluated；不声明产品就绪 |

本能力不含视觉算法/native图像资源，HALCON/AsunImage/HIL视觉或设备算子验证不适用；与实际设备写命令的产品集成若另行批准，设备Owner按该产品要求验证，本页不取得设备/质量事实权限。上述准入状态不因完整范围文档闭合提升，不新派代码、不新建会话或子代理。

## 13. 发布、升级回退和待主会话串行处理

Core 包包含 API/版本及资源语义，程序集与Profile/hash、adapter版本声明可追溯；只在契约/并发/恢复/双Host测试和Profile验收后发布。升级先Stop拒新→保留未决request/audit key→真实排空→切新程序集/Profile→新权威会话→重核；不把未决业务重新派发。共享端口在旧实例Stopped前不可Dispose。

回退恢复原程序集/Profile**配置**而非原Allow缓存/已失效会话。Policy/authority必须仍是当前受信版本；回退到不可识别当前policy的旧程序失败关闭，不降级到旧已撤销策略。历史业务/审计仍按原格式读，不重新签发授权、不回写hash、不清原Key。无可读兼容路径时保留Unknown并人工对账，不能生产写恢复。

主会话需要串行处理的跨文件影响（本轮未写其它文件）：

1. 正文过去的“所有API等平台Schema批准”改为模块本页精确 Contract 与平台映射分门；共有 Contract如需引用本模块，只映射 §3，不复制 DTO/状态。
2. 其它指导如把授权 Completed 绑定**实例**整体排空，须按operation资源范围修正；常驻服务不应每次调用停整个实例。
3. 真实调用方如仅看 PolicyOutcome/旧 DecisionId 继续副作用，须改为有效 Gate+实际提交fence；相关生产集成未具此边界不可准入。
4. 实际审计端口必须具备tenant+AuditId幂等/查原回执及当前读取权；普通日志不代审计，业务已提交后审计未知须原operation恢复。
5. 生产 authority 的认证签发/策略来源、二人职责分离政策、存储保留和凭证属于具体消费者配置；字段已定义，无需开发者再发明 Core 契约。
6. AU-W1 的目标版本公开资料已有复用范围，真实Grid/Dock/SuperTip接线和内置三语/UIA仍未运行；不得据在线403或文档接收冒验收。


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

## 14. 本轮外部接入者自审范围

2026-10-11 的 0.3.3-prep 在已接收范围之外补 §8.1～§8.4，并在 §12.4给出全部批准范围结论。第一轮只按本页从A/B空宿主走完可信来源→显式Core→实际提交门→原意图审计；第二轮按冒名/降级/撤权/expiry/提交响应丢失/审计冲突/重启/迟到/关闭走查。修正“实际适配器设计都属外部门”的含混，补提交前持久恢复锚点、条件核验/写入共同线性化点、业务/审计两轴Owner及合成意图有界实际编码；旧Core签名/算法与WPF接收保持，不重新计算已接收范围。此次复用 §2来源，只新增本机.NET10官方XML中BCL序列化签名核对，无新增上游源码研究或供应商API声称；仅编辑本页，文档结构/链接和新增语义一致性按本轮会话检查，未创建或运行产品测试。

2026-10-11 的 0.3.2-prep 仅补 §10.3～§10.5 确定实例绑定、双STA Host全字段装配/意图订退、原Task与纯UI寿命分离、同Key恢复和旧投影/语言隔离，并同步 §12.1 Wpf.Tests 落点及 W1 未验结论。已完成空宿主、异常/语言/慢事件/关闭两个有限文档走查；AU-C1～C3 已接收规格及 Core/API/算法不重审、不修改。新增 API 证据仅本机官方 XML和公开元数据，无新下载资料或辅助报告。

已从求值接入和并发恢复两个视角复核本页 API→示例→状态→测试的同一顺序，修正默认批准/隐式身份、审计与授权混淆、实例级排空卡住单请求、伪原子撤权、无租户cache key、未定义查询、无界通知/保留、升级回退恢复旧授权和无依据性能默认值。0.3.1-prep 继续闭合六维请求键/用途、分角色实际权威证据及grant预算、同快照异内容、完整原审计读取/重启关联、技术核权存在性门及辅助IO排空、UI输入/意图/三语错误和BCL测试Host命令。只读研究及本页定向链接/结构检查记录在本会话回复，不建立第二清单或报告。

边界再次确认：本模块只持授权、请求和审计端口技术结果，不持工艺/质量/设备事实；二人授权不等于复判结论。无视觉算子路线，不读取/修改AsunImage内部。此次只是指导准备，未编译Module API/运行Core、WPF、HALCON、真实存储、性能、HIL或生产验收。

