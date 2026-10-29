# IM-068 alarms 报警生命周期开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`AL-C0, AL-C1`

- 指导版本 `1.0.0-prep.7`；唯一 Module API Contract `1.0.0`（未实施草案，本轮补齐完整范围规格）；2026-10-12。
- 永久唯一会话 `01a12765-2d8e-7510-9dcb-e71cfadffa3b`，已核对 [模块索引](../MODULE-INDEX.md) 登记为本会话；不改共享文件、不新会话/fork/子代理。
- **前次主控限定接收仅保职责/生命周期方向；本轮codec、Host、顺序、分页、AL-S1、AL-W1及完整范围缺口已在本会话完成两轮自审，完整范围文档结论见§13。** 逐切片状态按§12/§13评估；规格就绪不表示代码、数据库或WPF已实施。
- C# / .NET10，namespace根 **Asun.Modules.Alarms**，Core仅BCL，无WPF/产品Shell/VM/私表/SDK/HALCON/AsunImage/OPC UA运行库。
- 本阶段只写本指导；未建产品/测试工程，未编译、运行、测性能、验真实后端/WPF/HIL/现场。
- 模块级设计评审态：`DesignReview`（方案可评审）。§13「完整批准范围的文档准备结论」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

## 1. 任务、切片与边界

两个真实消费者：机台运行/维护宿主；独立MES互联/存储服务宿主。二者都从设备/采集/互联原Owner接收条件，使用同一无UI合同。模块只拥有定义登记、报警发生、清除证据、人工确认/备注、抑制/搁置、审计和幂等回执。条件判据、来源连接真值、严重度政策、Stop/Reset/Retry/Continue、互锁、工艺与质量放行归原Owner。本模块只记录外部动作回执，不执行动作。ERROR日志不得自动变报警；diagnostics不拥有生命周期。HALCON不适用于报警事务。

权威：用户决定→独立架构§3/7.1→本页已接收合同→项目规则→来源。PKG-059/SM-005是迁移来源，旧路径/状态不继承；六项门唯一按DEV-GOV-010§3.1。

| 切片 | 唯一工程（待后续授权创建） | 范围/状态 |
|---|---|---|
| AL-C0 | `src/Modules/alarms/Asun.Modules.Alarms.Core/Asun.Modules.Alarms.Core.csproj` | 校验、codec、身份、纯reducer、窗口；ModuleCoreImplementationReady（规格） |
| AL-C1 | 同Core工程，仅BCL | Factory/Runtime/注入持久端口/授权/原Task/订阅/关闭；ModuleCoreImplementationReady（规格） |
| AL-S1 | `src/Modules/alarms/Asun.Modules.Alarms.Storage/Asun.Modules.Alarms.Storage.csproj` | Core+IM066公开合同/Runtime，领域绑定桥；PreparationIncomplete，真实后端未验 |
| AL-W1 | `src/Modules/alarms/Asun.Modules.Alarms.Wpf/Asun.Modules.Alarms.Wpf.csproj` | net10.0-windows/WPF、Core、本机DevExpress25.2.3；PreparationIncomplete，真实UI未验 |

Core唯一Smoke工程：`tests/Modules/alarms/Asun.Modules.Alarms.Core.Smoke/Asun.Modules.Alarms.Core.Smoke.csproj`。S1/W1后续分别为同级`Asun.Modules.Alarms.Storage.Smoke/…csproj`、`Asun.Modules.Alarms.Wpf.Smoke/…csproj`。未来仅允许本指导和上述精确工程；当前仅本指导。禁止其它模块、共享入口/schema/配置、交付项目、原始资料/正式测试/工作树、AsunImage/DevExpress安装与版本。无通用SQL/查询DSL、任意脚本条件、无限重试、自动删历史、隐藏全局状态或设备副作用。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Alarms.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；只有 `Asun.Modules.Alarms.Wpf` 可引用 WPF/DevExpress，Core 不得反向引用。

**Blazor/Web**：报警中心是 Web 端 P0 优先需求（实时告警推送）。报警事件通过 SignalR 实时推送；报警确认/抑制操作经已授权维护接口，带 principal 令牌，不经浏览器直接修改报警状态。§1 已明确"宿主负责严重度政策、条件判据"——Web 端只展示和确认，不自行设置报警条件。

**AI 三态仲裁与报警**：AI 推理的 `NeedsHuman`（人工介入）可触发本模块的报警事件（通知值班工程师）；本模块是事件驱动的，不主动调用 `ai-inference`；三态仲裁后的 `NeedsHuman` 事件由宿主路由到本模块。

**HALCON 不适用**：报警是事件管理事务，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 唯一状态与处理算法

### 2.1 活动、确认、当前性分别表达

Occurrence.IsActive=true直到权威Inactive清除；AckState独立。Required/Optional的新发生均Unacknowledged，Disabled为NotRequired（不伪称人工确认）。Optional仅允许宿主不立即确认，仍保留未确认事项。清除不确认，确认不清除/复位/继续/放行。清除未确认仍待办；再发生新ID，旧确认仅作用于旧ID。同条件最多一个未清除发生，额度内多个清除未确认发生全部保留，不覆盖为计数。

Source.Currentity=Current/Stale/Disconnected/Unknown，HistoryComplete另列。Unknown/断连/缺口/坏质量/TTL/重启/抑制/UI筛选都不把IsActive改false。页面必须同时显示“活动”和“来源未知/缺口”。重复Active/心跳只更新source watermark，不增发生数、不提高occurrence处理Revision，避免轮询导致确认CAS风暴。

### 2.2 定义和绑定

定义`(Id,Version)`不可变追加；同内容重放NoChange，异内容DefinitionConflict。旧发生固定旧版本。ConditionKey=`(DefinitionKey,SourceId,InstanceId)`是一条独立序列流；同设备多个条件不能误用设备总序号。绑定的 `ConditionKey.Definition` 必须等于 `ConditionBinding.Definition`。变更需ExpectedBindingRevision，且无活动、无gap、无有效抑制；不清旧发生/回执，不隐含Inactive。

### 2.3 epoch/顺序/重复/gap的固定顺序

本段所有比较使用**提交前快照**。设 preEpoch、preHighest、preApplied 和 preGap；本地 candidate 不先写回最高序号。每个被接纳观察（包括已授权拒绝）有原身份回执，不能只保最后hash。

1. 校验绑定/来源权限并查原ledger；同身份同hash返回原回执，异hashIdentityConflict，过保证期IdentityExpired。低epoch为EpochStale。epoch相同且 `sequence<=preHighest` 而ledger无该身份为OutOfOrder，不改watermark/真值；ledger不完整则RecoveryUncertain，不能冒充新请求。
2. 新源用候选 `(epoch=input.Epoch, highest=0, applied=0, RequiresSnapshot=true)`；高epoch用相同候选并记ContinuityLost、HistoryComplete=false，旧活动不清。冷重启**同epoch保留原highest/applied**，只将RequiresSnapshot=true、Currentity=Unknown；不得归零重放已处理序列。
3. 以候选highest计算expected=`checked(highest+1)`；若sequence>expected，新增精确MissingRange(epoch,expected,sequence-1)。新缺失范围与旧开放范围取有序并集，不把已接受序号也标为缺失；SourceState的GapFrom/Through只给这个并集的包络。历史GapFact不可删，迟到拒绝不会把开放缺口补齐。
4. **先分支判断AuthoritativeSnapshot，再更新highest**：合法快照须sequence>候选highest且CoversThrough>=sequence-1。它将旧开放缺口和本次新缺口闭合、RequiresSnapshot=false，应用现在的Active/Inactive、applied=sequence、highest=sequence、Currentity=Current。曾有缺口/跨代/重启则HistoryComplete=false；全新源epoch1、seq1且无缺口时可为true。MissingRange事实和SnapshotReconciliation依据仍保留，不伪造缺失期间的转换。
5. 普通Sample/Heartbeat将highest=sequence。若RequiresSnapshot=true则MissingSnapshot、不应用真值；若开放缺口则SequenceGap、Currentity=Unknown、不应用真值；若Sample不是Current+Good则SourceUnavailable、RequiresSnapshot=true、不应用真值；否则连续Sample才应用，applied=sequence。Heartbeat固定Unknown，不改变applied/IsActive；Current+Good只能在无RequiresSnapshot/gap时维持当前性，不能凭心跳重新证明条件。
6. 非当前/非Good观察同时置RequiresSnapshot=true，并将Currentity标输入失效状态（非Good但输入Current时投影Unknown），不续LastGoodReceived期限；good且能代表当前来源才更新LastGoodReceived与本实例单调TTL。Source.LastReceived更新所有已接受非迟到输入。新highest/缺口/发生变化与回执在**同一Commit**原子写；持久成功后才发布，重复不增revision。

seq1→3→2→4和首次权威seq42的逐状态oracle见§8.1。不存在“先更新highest再要求同一snapshot更大”的路径。精确开放缺口集合由Store中GapFact的打开/闭合事实重放，热Source只用包络作阻断；Core不为每个丢失序号分配对象。

新代权威Active且旧发生未清除：**保持原occurrence**，不猜重连期间再发生次数；新代权威Inactive可以清除同ConditionKey旧Active，ClearBasis=SnapshotReconciliation。旧代迟到Inactive不能清新代。首次明确Active而没有原Active时创建，ActivationEvidence区分EdgeObserved/FirstKnownActive/AfterHistoryGap，不能把收到时刻冒充真实故障起点。epoch/sequence正UInt64，checked耗尽时拒绝，不回绕；来源另给稳定InstanceId再登记。

### 2.4 时间、重启和有限抑制

ObservedAtUtc仅审计，不排序/定TTL。注入TimeProvider产生ReceivedAtUtc和单调timestamp。最后Good接收+FreshnessTtl到期只标Stale，不清Active。执行/抑制期限用单调时钟，墙钟回拨不延长。

冷重启恢复已证实定义/发生/确认/回执；来源一律Unknown，要求权威快照重新Current，不重播声音/设备/MES写。截断/缺页/未知codec进入只读RecoveryUncertain；**已证实的确认保留**，无法证实的那条投影Unacknowledged+AckEvidenceUncertain，原始bytes保留，不自造确认或恢复。

Suppress维护抑制与Shelve操作者搁置均针对ConditionKey、有限Duration、理由与分别授权。只降低通知/默认列表优先级，不隐藏活动计数/未确认/gap/历史；同期限内新发生仍独立未确认。宿主以AllowedVisibility=0禁止关键条件隐藏，不由severity猜安全政策。开始保存BootId/UTC审计/Duration，本实例单调deadline；到期Effective=false，即使到期审计暂存失败也不能继续隐藏。Runtime每500ms维护Task写唯一Expired，失败显示“已到期，记录待保存”。新Boot不持有旧单调deadline，一律ExpiredAfterRestart，可提前失效不延长。查询只读，不由UI timer暗写。撤销独立权限/CAS，不是确认。

### 2.5 启动投影、多站读取与参数来源

RuntimeId每运行实例唯一，BootId是宿主为该Scope生命周期代分配的不可复用标识；同时访问同Scope的操作站共享当前BootId，不因新开一个view/查询站便换Boot。Role显式LifecycleOwner或OperatorStation，默认LifecycleOwner只用于§7两个独立来源Host；真实操作站必须显式传OperatorStation，零Observe/维护写，仍能按普通Grant执行确认/备注/可见性命令。宿主只在上一代所有来源/维护writer真排空或已被原Owner fenced后切Boot；旧未知writer不准被新Boot掩盖。两个独立消费者的Scope、来源Owner和Clock分别独立，§7共仓库并发case在同一SyntheticClock/Boot下运行；跨机台不能用不同本地单调钟解释同一租约。现场跨机器运行的操作站只读来源Owner已提交Currentity，不用自己的钟替代来源Owner的TTL；收到者自己的连接失效可把页面标Unknown，不能清条件。来源发布和期限维护仍由原宿主明确的生命周期writer执行，普通操作站没有该能力。

LifecycleOwner.Create恢复时保存启动StoreRevision为本地BootFloor，构造**本地有效投影**：原epoch/highest/applied不变，需重新证明的Source.Currentity=Unknown、RequiresSnapshot=true；旧Boot可见性Effective=false。此投影不暗写Store，不改原事实和确认。首次提交后、属于该Source的新的AuthoritativeSnapshot事件才能解除本地重证明状态；旧快照/普通心跳/晚到pre-BootFloor事件不能解除。OperatorStation不将启动当来源重启、不改durable RequiresSnapshot，只消费来源Owner已提交的Currentity；自身读链未知时保守显示Unknown而不写Source。重启事件只为来源失效证据，不创建故障次数。Plan用于Observation时合成本地RequiresSnapshot约束；用于纯确认/备注时不得将本地启动投影塞进无关Source Delta。Store的After只应用显式Delta，不用本地完整投影覆写别站来源。

维护Task由受信任factory启动配置所授**内部有限能力**运行：只读本Scope快照和ledger、追加Stale/Expired对应Maintenance计划，没有外部Execute入口、不获得人工确认权限；Authority启动面必须以`AcquireRuntimeAsync(AlarmRuntimeConfiguration configuration,TimeSpan maxHold,CancellationToken ct)`返回原`AlarmGrantResult`（作为IAlarmAuthority新增方法）。它使用受信任启动身份，返回PrincipalId=`runtime`；工厂启动先取得StartupBudget内Grant，每批维护再取本次MaxExecutionBudget内Grant、审计DecisionId、真实Dispose后结束，长期能力不是永久Grant。configuration.RuntimeId/BootId/Scope由该Authority已登记启动上下文精确核，不接请求自造principal/proof。授权失效时维护不发Commit、health显式只读，TTL/Lease期限的保守失效仍在本地投影立即生效；恢复需宿主重新授该同运行上下文，不能借操作者Grant。SyntheticAuthority实现此方法，仅表内两个Host exact configuration可授runtime能力；Grant计数及期限与普通Acquire相同。

MissingRange按Condition+epoch分开；Source.GapFrom/Through仅是**当前epoch**开放范围的包络，旧epoch缺口保在OpenMissingRanges并使RequiresSnapshot=true，不拿不同epoch序号取数值min/max。新epoch权威snapshot可以关闭该Condition所有旧开放范围，逐范围Closed事实保原epoch/From/Through，不宣称补回旧转换。GapFact的HistoryGap.From=Through=打开该MissingRange那条GapFact的最终事件cursor（先以Receipt.StoreRevision和固定Fact ordinal分配）；SourceSequence历史键固定原打开cursor/Condition/ReasonCode=SequenceMissing，闭合Fact复用同一HistoryGap，闭合Cause在GapFact.ReasonCode=Resynchronized。迟到或合并热MissingRange不删除原打开事实；闭合合并区间时按包含关系移除热区间，历史各原范围保留。在新snapshot同批打开又闭合时先打开后闭合、同一Missing/HistoryGap键，当前为空而历史仍在。

参数无隐式生产默认：定义/绑定必须显式给Severity、AckPolicy、AllowedVisibility、FreshnessTtl和Duration上限；条件阈值/等级/故障反应均由设备或服务Owner提供。§7的10s/30s TTL、Severity700/400及期限是确定性合成值，不能抄作客户政策。本模块无图像/坐标/单位换算/视觉算法，不消费viewport/AsunImage；HALCON算子和图像操作不适用。无AI/自动报警阈值优化、自动等级、自动确认、自动Reset或参数学习；只提供有界UI初值与固定软件配额，不把“推荐”静默写配方。Counts/风暴窗口仅投影，不产生新条件或防护命令。

参数决策顺序固定为：消费者Profile显式值→已登记Owner绑定/定义→本模块结构上限；任何缺失的生产Profile字段在启动拒绝，禁止使用“安全默认值”。模块给出的推荐仅是设计审查起点：`PageSize=128`、订阅容量64、每次确认最多128、执行预算2s、维护周期500ms、Store桥等待预算1s；实现可在Profile中选择更小值，不能超过合同上限，不能静默扩大。§7的Host值只证明边界和故障路径；客户报警频率、保留期、FreshnessTtl、Severity、AckPolicy、通知和停机规则分别由两个消费者Owner在Profile采纳。

## 3. Module API Contract 1.0.0：精确DTO

### 3.1 原语和定义/观察

所有声明namespace `Asun.Modules.Alarms`；using System、System.Collections.Immutable、System.Threading、System.Threading.Tasks。record不可变，ImmutableArray的default拒绝，明确空用Empty；限长后复制，不保留可变集合。以下是待实现签名，未编译，不能当现成DLL。

Key字符串ASCII、大小写敏感、`^[A-Za-z0-9][A-Za-z0-9._:/-]*$`，不trim/折叠/作路径。ScopeId1..64bytes，Definition.Id1..64，SourceId/InstanceId/PrincipalId/ProofRef1..128，BootId/RuntimeId1..64；资源键1..128同Key。Version严格三段0..65535、无前导零（0本身除外）、无metadata/prerelease。备注/理由合法UTF8/NFC，拒绝孤立代理项/NUL，不静默正规化；最长2048标量且8192bytes，备注可空串，理由至少1标量，不含凭据。UTC offset=0，未知用null不填MinValue。所有enum按声明顺序从0递增，未定义值拒绝；nullable无值不等于0。正Revision溢出RevisionExhausted，不回绕。

```csharp
public readonly record struct DefinitionKey(string Id, string Version);
public readonly record struct SourceIdentity(string SourceId, string InstanceId);
public readonly record struct ConditionKey(DefinitionKey Definition, SourceIdentity Source);
public readonly record struct OccurrenceId(string Value); // occ_ + 64 lowercase hex
public readonly record struct Revision(ulong Value); // 0仅未建立，持久行>0
public readonly record struct RequestId(Guid Value); // 非Empty
public sealed record AlarmCaller(string PrincipalId, string ProofRef);
public sealed record AlarmEvidenceRef(string Owner,string Id,string Version,string Sha256);
public enum AckPolicy { Required, Optional, Disabled }
public enum AckState { Unacknowledged, Acknowledged, NotRequired }
[Flags] public enum VisibilityCapabilities { None=0, Suppress=1, Shelve=2 }
public enum VisibilityMode { None, Suppressed, Shelved }
public enum Currentity { Unknown, Current, Stale, Disconnected }
public enum ObservationQuality { Good, Uncertain, Bad }
public enum ConditionValue { Unknown, Inactive, Active }
public enum ObservationKind { Sample, Heartbeat, AuthoritativeSnapshot }
public enum ActivationEvidence { EdgeObserved, FirstKnownActive, AfterHistoryGap }
public sealed record AlarmDefinition(DefinitionKey Key,string TitleKey,
    string DescriptionKey,string RecoveryKey,ushort Severity,AckPolicy AckPolicy,
    VisibilityCapabilities AllowedVisibility,int MaxCommentScalars,
    TimeSpan MaxSuppressDuration,TimeSpan MaxShelveDuration);
public sealed record ConditionBinding(ConditionKey Key,DefinitionKey Definition,
    TimeSpan FreshnessTtl,Revision Revision);
public sealed record ConditionObservation(DefinitionKey Definition,SourceIdentity Source,
    ulong Epoch,ulong Sequence,ObservationKind Kind,ConditionValue Value,
    Currentity Currentity,ObservationQuality Quality,DateTimeOffset ObservedAtUtc,
    ulong? CoversThrough,AlarmEvidenceRef? Evidence);
```

Severity0..1000纯宿主元数据，MaxCommentScalars1..2048，FreshnessTtl1s..1h，最大抑制/搁置期限1s..30d（禁用时也提供合法值保证编码确定）。Evidence.Owner/Id1..128、Version同Version、Sha256严格64小写hex，仅稳定引用不授动作/删除权。Sample必须Active/Inactive且CoversThrough=null；Heartbeat必须Unknown且CoversThrough=null；AuthoritativeSnapshot必须Current+Good、Active/Inactive且CoversThrough>=Sequence-1。epoch/sequence>0。

### 3.2 事实行

```csharp
public sealed record AlarmOccurrence(OccurrenceId Id,DefinitionKey Definition,
    ConditionKey Condition,ulong RaisedEpoch,ulong RaisedSequence,
    DateTimeOffset RaisedObservedAtUtc,DateTimeOffset RaisedReceivedAtUtc,
    ActivationEvidence ActivationEvidence,bool IsActive,AckState AckState,
    DateTimeOffset? ClearedAtUtc,string? ClearBasis,DateTimeOffset? AcknowledgedAtUtc,
    string? AcknowledgedBy,string? AckComment,bool AckEvidenceUncertain,
    AlarmEvidenceRef? Evidence,Revision Revision);
public sealed record SourceState(ConditionKey Condition,ulong CurrentEpoch,
    ulong HighestSeenSequence,ulong LastAppliedSequence,string? LastPayloadHash,
    Currentity Currentity,ObservationQuality Quality,bool IsGapOpen,
    ulong? GapFrom,ulong? GapThrough,bool RequiresSnapshot,bool HistoryComplete,
    DateTimeOffset? LastReceivedAtUtc,DateTimeOffset? LastGoodReceivedAtUtc,
    OccurrenceId? CurrentOccurrenceId,Revision Revision);
public sealed record VisibilityLease(ConditionKey Condition,VisibilityMode Mode,
    string LeaseId,string BootId,string PrincipalId,string Reason,
    DateTimeOffset StartedAtUtc,DateTimeOffset ExpiresAtUtc,TimeSpan Duration,Revision Revision);
public sealed record OccurrenceTarget(OccurrenceId Id,Revision ExpectedRevision);
```

Active时Clear时间/Basis均null，清除后均非null，Basis仅Sample/SnapshotReconciliation。Acknowledged时Ack时间/人/备注非null（备注可空）；另外两态三字段均null。无法证实则AckEvidenceUncertain=true，不同时声称已证实人工确认。CurrentOccurrenceId只指未清除发生，确认不置null。GapFrom/Through同null或同时非null且From<=Through；Source只存包络缺口区间，精确缺失范围另存GapFact，避免伪称包络中全部丢失。

### 3.3 命令

```csharp
public abstract record AlarmCommand(RequestId Id);
public sealed record RegisterDefinition(RequestId Id,AlarmDefinition Definition):AlarmCommand(Id);
public sealed record BindCondition(RequestId Id,ConditionBinding Binding,
    Revision ExpectedBindingRevision):AlarmCommand(Id);
public sealed record Acknowledge(RequestId Id,ImmutableArray<OccurrenceTarget> Targets,
    string Comment):AlarmCommand(Id);
public sealed record AddComment(RequestId Id,OccurrenceTarget Target,string Comment):AlarmCommand(Id);
public sealed record SetVisibility(RequestId Id,ConditionKey Condition,
    Revision ExpectedVisibilityRevision,VisibilityMode Mode,TimeSpan Duration,string Reason):AlarmCommand(Id);
public sealed record ClearVisibility(RequestId Id,ConditionKey Condition,
    Revision ExpectedVisibilityRevision,string Reason):AlarmCommand(Id);
public enum OwnerActionKind { Reset, Retry, Continue }
public enum OwnerActionPhase { Requested, Succeeded, Failed, Unknown }
public sealed record RecordOwnerAction(RequestId Id,OccurrenceTarget Target,
    OwnerActionKind Kind,OwnerActionPhase Phase,string Owner,string OwnerActionId,
    string? OwnerResultCode,AlarmEvidenceRef? Evidence):AlarmCommand(Id);
```

Acknowledge同时用于单/批量，Targets1..128、ID不重复、按ID Ordinal排序，ExpectedRevision>0。提交对象集固定，新增行不加入；任一无效/版本冲突/Disabled/评论超限则整批拒绝、零确认变化、回执指明失败目标。对已确认的新请求NoChange保留原Actor/Comment，不覆盖；同RequestId始终原回执。AddComment追加Fact、CAS并Revision+1，不改原AckComment。绑定新建Expected=0且Binding.Revision=0，更新两者equal>0，成功+1。SetVisibility只许Suppressed/Shelved，Duration1s..定义上限；Expected=0新建或exact旧revision；新/延期形成新LeaseId=请求D格式，重核权限/理由。Clear要求exact当前租约revision，已None为NoChange，保留终止行防ABA。Owner/OwnerActionId/ResultCode1..128；Requested时ResultCode=null，其它Phase必填；完成应附原Owner证据。RecordOwnerAction不执行动作，不从点击推定成功。

### 3.4 错误/回执/查询形状

```csharp
public enum AlarmFaultCode { InvalidInput,DefinitionUnknown,DefinitionConflict,
    BindingConflict,SourceDenied,EpochStale,OutOfOrder,SequenceGap,MissingSnapshot,
    IdentityConflict,IdentityExpired,OccurrenceUnknown,TargetRevisionConflict,AckDisabled,
    VisibilityDenied,AuthorizationDenied,StoreUnavailable,StoreFull,CommitUnknown,
    RecoveryUncertain,CapacityExceeded,CancelledBeforeAdmission,CancelledBeforeCommit,
    ExecutionDeadline,Stopping,UnsupportedVersion,RevisionExhausted,ProviderProtocolError,
    ResourceCleanupFailed,SnapshotChanged,SubscriptionClosed,SourceUnavailable }
public sealed record AlarmFault(AlarmFaultCode Code,string MessageKey,
    ImmutableArray<string> Arguments,bool Retryable,string? DiagnosticId);
public enum AlarmInputKind { Observation, Command, Maintenance }
public sealed record AlarmIdentity(string ScopeId,AlarmInputKind Kind,string Key,string PayloadHash);
public enum AlarmCommitState { NotSubmitted, Recorded, Unknown }
public enum AlarmDisposition { Applied, NoChange, Rejected }
public sealed record TargetReceipt(OccurrenceId Id,Revision Revision,AckState AckState);
public sealed record AlarmReceipt(AlarmIdentity Identity,AlarmDisposition Disposition,
    Revision StoreRevision,DateTimeOffset RecordedAtUtc,ImmutableArray<TargetReceipt> Targets,
    string ObjectSetHash,AlarmFault? Rejection);
public sealed record AlarmWriteResult(AlarmCommitState CommitState,AlarmReceipt? Receipt,
    AlarmFault? Fault,bool IsReplay);
public sealed record AlarmRead<T>(T? Value,AlarmFault? Fault) where T:class;
public enum LedgerState { Recorded, InProgress, Unknown, AbsentSafe, AbsentUnsafe, Expired }
public sealed record AlarmLedgerLookup(AlarmIdentity Identity,LedgerState State,
    AlarmReceipt? Receipt,AlarmFault? Fault);
public sealed record AlarmClosure(bool AdmissionClosed,bool ResourcesReleased,
    int RunningCalls,int OpenSubscriptions,bool StoreClosed,bool StoreDisposed,AlarmFault? Fault);
```

Recorded必有Receipt，Applied/NoChange时Rejection=null，Rejected必有Rejection。NotSubmitted=Receipt null+Fault，Unknown=Receipt null+CommitUnknown。耐久记录业务拒绝也是Recorded，不能称Applied。IsReplay是本次观察属性，不改原Receipt。AlarmRead严格Value或Fault二选一，空页用合法Empty。Ledger.Recorded有原Receipt，其它State无Receipt；AbsentUnsafe不是可重试证明，Expired不能复用key。错误MessageKey=`Alarms.Error.<Code>`；Arguments<=8，每项<=256UTF8bytes且脱敏，原Exception只在诊断引用。语法/授权拒绝不授回执敏感信息。

### 3.5 当前/历史/事件

```csharp
public readonly record struct AlarmCursor(ulong StoreRevision,uint Ordinal);
public enum HistoryGapKind { Retention, SourceSequence, ImportedTruncation, Unavailable }
public sealed record HistoryGap(HistoryGapKind Kind,AlarmCursor From,AlarmCursor Through,
    ConditionKey? Condition,string ReasonCode);
public sealed record MissingRange(ConditionKey Condition,ulong Epoch,ulong From,ulong Through);
public sealed record AlarmEvent(AlarmCursor Cursor,string EventId,AlarmIdentity Identity,
    DateTimeOffset RecordedAtUtc,AlarmFact Fact);
public sealed record CurrentAlarmQuery(string? SourceId,bool IncludeClearedUnacknowledged,
    bool IncludeSuppressed,int PageSize,string? ContinuationToken);
public sealed record CurrentAlarmRow(AlarmOccurrence Occurrence,SourceState Source,
    VisibilityLease? Visibility,bool VisibilityEffective,bool ExpiryRecordPending);
public sealed record AlarmCounts(long Active,long Unacknowledged,long SuppressedActive);
public sealed record AlarmCurrentPage(Revision AsOfRevision,AlarmCounts Counts,
    ImmutableArray<CurrentAlarmRow> Rows,ImmutableArray<SourceState> UnavailableSources,
    string? ContinuationToken,ImmutableArray<HistoryGap> Gaps);
public sealed record HistoryAlarmQuery(DateTimeOffset FromUtc,DateTimeOffset ToUtc,
    SourceIdentity? Source,int PageSize,string? ContinuationToken);
public sealed record AlarmHistoryPage(Revision AsOfRevision,ImmutableArray<AlarmEvent> Items,
    string? ContinuationToken,ImmutableArray<HistoryGap> Gaps);
public sealed record AlarmEventPage(ImmutableArray<AlarmEvent> Items,AlarmCursor Next,
    bool AtEnd,ImmutableArray<HistoryGap> Gaps);
public sealed record SubscriptionRequest(AlarmCursor After,int Capacity);
public enum StreamFrameKind { Events, Gap, Closed }
public sealed record AlarmStreamFrame(StreamFrameKind Kind,ImmutableArray<AlarmEvent> Events,
    AlarmCursor Through,ImmutableArray<HistoryGap> Gaps);
```

PageSize1..256；From<To最长366d；SourceId可null表示本Scope授权范围全部。**首版不维护旧热快照、不实现MVCC、不提供ReadAsOf**。Current每页调用一次ReadHot取得原子完整快照；首请求捕获StoreRevision和本Runtime ProjectionGeneration，续页二者必须与token相等，否则SnapshotChanged、零行、无新token，调用方丢弃旧分页投影并显式从首页重查。ProjectionGeneration本地正UInt64：TTL/可见性有效性变化及启动/权限读取范围变化时递增；RuntimeId/BootId也进Current token，因此不能跨Runtime拼当前页。期间仅调用方重新鉴权，权限范围变更拒续页，不给旧授权页。生成页面前/后检查generation；本次变化即最多3次重读（限原executionBudget），耗尽SnapshotChanged，禁止无限复读。

History按不可变事件Cursor稳定keyset，**也采用头版本检测**，不猜后端隔离：首请求ReadHot取head、ReadHistory读取<=head的事件、再ReadHot；两head一致才返回。首请求变化最多3轮重读；续页要求输入token.head等于前/后head，任何不符直接SnapshotChanged，不自动换AsOf。首请求Runtime先生成LastEvent=(0,0)、LastGap=null的内部HistoryPageToken传给Store；Store不自行选择head。Store.ReadHistory必须根据该token限定上界、校验覆盖并返回准确Gaps，Runtime复核其AsOf及事件上界；未知Reader/缺页明确错误/Gap，不能把缺页当尾页。追加和任何保留/截断元数据变化同样提高StoreRevision。head检查后发生的变化在该检查点之后，下一页明确拒绝，而不是承诺旧快照仍可取得。

Rows按OccurrenceId Ordinal、来源按Definition.Id→Version→SourceId→InstanceId Ordinal；每页二者各<=PageSize，两个last键分别推进，Counts在该页同一个完整授权快照上于筛选前计算。History按Revision→Ordinal，区间`[FromUtc,ToUtc)`，source exact match；每页Gaps<=PageSize，另用完整LastGap推进，与事件游标同时编码，直到二者到尾才无token。Gap全序为From→Through→Kind→Condition（null先，非null按四Key）→ReasonCode Ordinal，完全相同项去重；仅From不足以区分同位置不同条件/类型，不使用LastGapCursor。Gap投影附首次记录UTC和发布revision，按查询区间/head限制；Retention/Unavailable覆盖查询cursor区间时也返回，不能因失去原时间而过滤掉。ReadHistory明确接收/返回Gaps，不能静默丢截断标记。清除已确认/NotRequired离热待办但历史保留；IncludeSuppressed=false只筛行，不篡改Counts和失效来源/Gaps。无发生但源失效也必须有UnavailableSources。复杂跨域查询交IM045。

公开纯token合同（属于§5.4 codec，不是权限凭据）：

```csharp
public abstract record AlarmPageToken(string ScopeId,Revision AsOfRevision,string QueryHash);
public sealed record CurrentPageToken(string ScopeId,Revision AsOfRevision,string QueryHash,
    string RuntimeId,string BootId,ulong ProjectionGeneration,
    OccurrenceId? LastRow,ConditionKey? LastSource):AlarmPageToken(ScopeId,AsOfRevision,QueryHash);
public sealed record HistoryPageToken(string ScopeId,Revision AsOfRevision,string QueryHash,
    AlarmCursor LastEvent,HistoryGap? LastGap):AlarmPageToken(ScopeId,AsOfRevision,QueryHash);
```

QueryHash编码不含ContinuationToken，含所有其余query字段（PageSize也含），查询类型分域，详见§5.4。token<=2048bytes，严格base64url无padding；未知版本/tag、重复尾字节、checksum不符、filter/scope不同InvalidInput，已失覆盖IdentityExpired，head不同SnapshotChanged。token解码后仍重新鉴权，checksum仅防误用。

### 3.6 Factory/Runtime/Options

```csharp
public sealed record AlarmLimits(int MaxDefinitions,int MaxBindings,
    int MaxRetainedOccurrences,int MaxRequestBytes,int MaxFactsPerCommit,
    int MaxRunningCalls,int MaxSubscriptions,int MaxSubscriptionCapacity,
    int MaxLedgerEntries,long MaxLedgerBytes,long MaxHotBytes);
public enum AlarmRuntimeRole { LifecycleOwner, OperatorStation }
public sealed record AlarmRuntimeConfiguration(string ScopeId,string RuntimeId,string BootId,
    AlarmLimits Limits,TimeSpan MaxExecutionBudget,TimeSpan MaintenanceInterval,
    TimeSpan LedgerGuarantee,AlarmRuntimeRole Role=AlarmRuntimeRole.LifecycleOwner);
public sealed record AlarmFactoryOptions(TimeSpan StartupBudget);
public sealed record AlarmDependencies(IAlarmStoreFactory Stores,IAlarmAuthority Authority,
    TimeProvider Clock);
public sealed class AlarmInitializationException:Exception
{
    public AlarmFault Fault { get; }
    public bool RollbackComplete { get; }
    public ImmutableArray<Exception> CleanupFailures { get; }
    public AlarmInitializationException(AlarmFault fault,bool rollbackComplete,
        ImmutableArray<Exception> cleanupFailures,Exception? inner);
}
public sealed class AlarmRuntimeFactory
{
    public AlarmRuntimeFactory(AlarmDependencies dependencies,AlarmFactoryOptions options);
    public Task<IAlarmRuntime> CreateAsync(AlarmRuntimeConfiguration configuration,CancellationToken ct);
}
public interface IAlarmRuntime:IAsyncDisposable
{
    Task<AlarmWriteResult> ObserveAsync(ConditionObservation input,AlarmCaller caller,
        TimeSpan executionBudget,CancellationToken ct);
    Task<AlarmWriteResult> ExecuteAsync(AlarmCommand input,AlarmCaller caller,
        TimeSpan executionBudget,CancellationToken ct);
    Task<AlarmRead<AlarmLedgerLookup>> QueryReceiptAsync(AlarmIdentity identity,
        AlarmCaller caller,TimeSpan executionBudget,CancellationToken ct);
    Task<AlarmRead<AlarmCurrentPage>> QueryCurrentAsync(CurrentAlarmQuery query,
        AlarmCaller caller,TimeSpan executionBudget,CancellationToken ct);
    Task<AlarmRead<AlarmHistoryPage>> QueryHistoryAsync(HistoryAlarmQuery query,
        AlarmCaller caller,TimeSpan executionBudget,CancellationToken ct);
    Task<IAlarmSubscription> OpenSubscriptionAsync(SubscriptionRequest request,
        AlarmCaller caller,TimeSpan executionBudget,CancellationToken ct);
    Task StopAsync();
    AlarmClosure GetClosure();
    AlarmRuntimeHealth GetHealth();
}
public interface IAlarmSubscription:IAsyncDisposable
{
    Task<AlarmRead<AlarmStreamFrame>> ReadAsync(int maxEvents,AlarmCaller caller,
        TimeSpan executionBudget,CancellationToken ct);
    Task CloseAsync();
}
```

Factory构造被动验证/保存，不开Store/线程/timer。Create原Task内开独占Store、加载验证快照、创建一个维护worker；截断/未知codec可只读降级（写拒绝RecoveryUncertain）。Open失败由工厂回滚部分资源，原Create Task等清理真结束才异常完成。调用方Factory前须有根槽，见§7。Stores/Authority/Clock归caller，Open返回Store归Runtime，不共用同一独占实例。

Limits全正checked；MaxFactsPerCommit>=130，MaxSubscriptions<=64，Capacity<=4096，MaxRunningCalls<=256，MaxRequestBytes<=1MiB；预算先验最坏热/订阅bytes<=MaxHotBytes。MaxExecutionBudget1ms..1min，每call1ms..Max；StartupBudget1ms..1min；`MaintenanceInterval`首版必须精确为500ms（不是调用方可调默认值）；LedgerGuarantee1h..366d，生产由Profile采纳。未排空和未决身份不可按TTL淘汰。额度满在外部端口前拒绝，无无界接纳队列、无async void/fire-and-forget。

### 3.7 自有持久/授权端口和Fact union

```csharp
public sealed record AlarmHotSnapshot(string ContractVersion,string ScopeId,
    Revision StoreRevision,ImmutableArray<AlarmDefinition> Definitions,
    ImmutableArray<ConditionBinding> Bindings,ImmutableArray<SourceState> Sources,
    ImmutableArray<AlarmOccurrence> RetainedOccurrences,
    ImmutableArray<MissingRange> OpenMissingRanges,
    ImmutableArray<VisibilityLease> Visibility,bool Complete,ImmutableArray<HistoryGap> Gaps);
public sealed record AlarmDelta(ImmutableArray<AlarmDefinition> Definitions,
    ImmutableArray<ConditionBinding> Bindings,ImmutableArray<SourceState> Sources,
    ImmutableArray<AlarmOccurrence> Occurrences,ImmutableArray<VisibilityLease> Visibility);
public sealed record AlarmCommitBatch(AlarmIdentity Identity,Revision ExpectedStoreRevision,
    AlarmDelta Delta,ImmutableArray<AlarmFact> Facts,AlarmReceipt Receipt);
public enum StoreCommitState { Recorded, RevisionConflict, Unknown, Rejected }
public sealed record AlarmStoreCommitResult(StoreCommitState State,AlarmReceipt? Receipt,
    AlarmFault? Fault);
public interface IAlarmStoreFactory
{
    Task<IAlarmStore> OpenAsync(AlarmRuntimeConfiguration configuration,CancellationToken ct);
}
public interface IAlarmStore:IAsyncDisposable
{
    Task<AlarmHotSnapshot> ReadHotAsync(CancellationToken ct);
    Task<AlarmLedgerLookup> LookupAsync(AlarmIdentity identity,CancellationToken ct);
    Task<AlarmStoreCommitResult> CommitAsync(AlarmCommitBatch batch,CancellationToken ct);
    Task<AlarmHistoryPage> ReadHistoryAsync(HistoryAlarmQuery query,CancellationToken ct);
    Task<AlarmEventPage> ReadEventsAsync(AlarmCursor after,int maxEvents,CancellationToken ct);
    Task CloseAsync();
}
public abstract record AlarmFact;
public sealed record DefinitionRegisteredFact(AlarmDefinition Definition):AlarmFact;
public sealed record ConditionBoundFact(ConditionBinding Binding):AlarmFact;
public sealed record ObservationFact(ConditionObservation Observation,string ObservationHash,
    DateTimeOffset ReceivedAtUtc,string DecisionCode):AlarmFact;
public sealed record RaisedFact(AlarmOccurrence Occurrence):AlarmFact;
public sealed record ClearedFact(OccurrenceId Id,Revision Before,AlarmOccurrence After,
    string Basis):AlarmFact;
public sealed record AcknowledgedFact(OccurrenceId Id,Revision Before,AlarmOccurrence After,
    string PrincipalId,string AuthorizationDecisionId):AlarmFact;
public sealed record CommentFact(OccurrenceId Id,Revision Before,Revision After,
    string PrincipalId,string Comment,string AuthorizationDecisionId):AlarmFact;
public sealed record VisibilityFact(VisibilityLease Lease,string ReasonCode,
    string AuthorizationDecisionId):AlarmFact;
public sealed record OwnerActionFact(RecordOwnerAction Action,string PrincipalId,
    string AuthorizationDecisionId,Revision After):AlarmFact;
public sealed record SourceFact(SourceState State,string ReasonCode):AlarmFact;
public sealed record GapFact(HistoryGap Gap,MissingRange? Missing,bool Closed,
    string ReasonCode):AlarmFact;
public sealed record RejectedFact(AlarmFault Fault,string PrincipalId,
    string AuthorizationDecisionId):AlarmFact;
public enum AlarmPermission { PublishCondition,RegisterDefinition,BindCondition,Acknowledge,
    Comment,Suppress,Shelve,Unsuppress,RecordOwnerAction,ReadCurrent,ReadHistory,ReadReceipt,Subscribe }
public sealed record AlarmAccessRequest(AlarmCaller Caller,string ScopeId,
    AlarmPermission Permission,ImmutableArray<ConditionKey> Conditions,
    ImmutableArray<OccurrenceId> Occurrences,TimeSpan MaxHold);
public interface IAlarmGrant:IAsyncDisposable
{
    string PrincipalId { get; }
    string DecisionId { get; }
}
public sealed record AlarmGrantResult(IAlarmGrant? Grant,AlarmFault? Fault);
public interface IAlarmAuthority
{
    Task<AlarmGrantResult> AcquireAsync(AlarmAccessRequest request,CancellationToken ct);
    Task<AlarmGrantResult> AcquireRuntimeAsync(AlarmRuntimeConfiguration configuration,
        TimeSpan maxHold,CancellationToken ct);
}
```

Store是领域Repository，完整数据Owner仍alarms，技术实现见§6。Snapshot超额度返回StoreFull，不能截断却Complete=true。Delta为完整行upsert、按key排序无重复，未列行保持；终止Visibility以Mode=None保留revision，不删除造成ABA。热待办一旦终结可由Store在同事务移到历史投影，Facts/Receipt不能丢。所有端口Task返回前实际IO/Grant/Reader/事务清理；失败Factory负责部分回滚，资源转交之后Runtime负责。

FactType wire为上述顺序1..12，0非法。Observation.DecisionCode闭包Applied/Raised/Cleared/SameValue/Heartbeat/GapOpened/Resynchronized/OutOfOrder/EpochStale/MissingSnapshot/SourceUnavailable；Source.ReasonCode闭包Applied/SameValue/Heartbeat/GapOpened/Resynchronized/MissingSnapshot/Disconnected/QualityUncertain/QualityBad/Stale/Restart/ContinuityLost；Visibility.ReasonCode闭包Set/Cleared/Expired/ExpiredAfterRestart；Gap.ReasonCode仅SequenceMissing/Resynchronized/Retention/ImportedTruncation/Unavailable。未知码拒UnsupportedVersion。精确SourceSequence缺口用MissingRange，不混成store revision范围。

SourceSequence GapFact.Missing必填，Closed=false表示打开该精确范围，Closed=true表示用本次权威快照闭合该范围，历史Gap仍在；其它GapKind的Missing=null且Closed=false。OpenMissingRanges为所有尚未闭合SourceSequence Missing的精确有序投影，按Condition/epoch/from排序、重叠/相邻范围合并但不吞已接收序号；每Condition最多64个分离范围，超限该普通输入在推进watermark前返回CapacityExceeded并要求权威快照，既有缺口/Active不丢。Snapshot给Core完整OpenMissingRanges，不能只凭Source包络猜精确闭合。Store按Core给的GapFact更新此投影（机械打开/闭合），不另选报警算法。既有历史Missing事实不因合并/关闭删除。范围数组整体<=MaxBindings*64，bytes计入MaxHotBytes。

Acquire结果Grant/Fault二选一；Grant.PrincipalId必须Caller一致、DecisionId1..128且稳定，绑定精确Scope/对象/权限。授权Owner保证有限MaxHold内决策有效，撤权作用于下一Grant；超期不能新发Commit，已发的只保存原结果/清理，不抹事实。批量核全部对象权限。授权拒绝由Authority审计Owner留Decision，不绕权写模块事实；已授权业务拒绝由RejectedFact审计。维护只获启动时有限生命周期能力，不能确认/清条件/执行人工命令。

### 3.8 纯Reducer与健康

```csharp
public sealed record AlarmPlanningContext(string ScopeId,string BootId,string PrincipalId,
    string DecisionId,DateTimeOffset ReceivedAtUtc);
public abstract record AlarmInput;
public sealed record ObservationInput(ConditionObservation Observation):AlarmInput;
public sealed record CommandInput(AlarmCommand Command):AlarmInput;
public sealed record MaintenanceTarget(ConditionKey Condition,Revision ExpectedRevision);
public sealed record MaintenanceInput(ImmutableArray<MaintenanceTarget> StaleSources,
    ImmutableArray<MaintenanceTarget> ExpiredVisibility):AlarmInput;
public sealed record AlarmPlan(AlarmIdentity Identity,AlarmDelta Delta,
    ImmutableArray<AlarmFact> Facts,AlarmReceipt Receipt);
public static class AlarmCore
{
    public static AlarmPlan Plan(AlarmHotSnapshot snapshot,AlarmInput input,
        AlarmPlanningContext context,AlarmLimits limits);
    public static string ComputeOccurrenceId(string scopeId,DefinitionKey definition,
        SourceIdentity source,ulong epoch,ulong sequence);
    public static AlarmIdentity ComputeIdentity(string scopeId,AlarmInput input,
        string principalId,int maxBytes,string? maintenanceBootId);
}
public sealed record AlarmMetrics(long CurrentActive,long CurrentUnacknowledged,
    long EffectiveSuppressed,long RaisedInLast60Seconds,bool WindowExact,
    int CompletedSecondBuckets,string BootId);
public sealed record AlarmRuntimeHealth(bool StoreAvailable,bool Writable,
    bool RecoveryUncertain,long RejectedBeforeAdmission,long SubscriberGapCount,
    int RunningCalls,long ReservedBytes,AlarmFault? LastFault,AlarmMetrics Metrics);
```

Plan同步无IO/线程/全局状态/系统墙钟，非法shape抛ArgumentException（Runtime闭合InvalidInput），合法业务冲突生成拒绝计划，不让Store/fake重实现算法。Context.UTC用于审计，不入语义hash；同snapshot/input/context同结果。维护输入为Runtime用单调期限算出的**exact revision对象集**，每批最多64个，source/visibility跨版本的target跳过并重读，不误过期新租约。

健康同步本地有界、独立于Store，不经失败的Store递归报警/日志；Diagnostics失败只计数。统计CurrentActive数所有IsActive，Unacknowledged含清除未确认，SuppressedActive数有效租约覆盖活动。风暴固定61个桶、单调整秒索引；每个耐久RaisedFact只加一次checked Int64，重复/轮询/Heartbeat不加。统计最近60个**完整秒**`[floor(now)-60,floor(now))`，排除当前未完秒，分辨率1s，返回次数不冒充每秒速率/精确滑动窗口。Boot前60s不足完整桶、溢出/单调异常/事件gap则WindowExact=false；不饱和成正确值。ObservedAt 100s→1s乱序不影响。重启只重置窗口，不清历史。

## 4. 事务、取消、原Task、事件与资源

### 4.1 精确CAS/幂等

Commit一个原子批次：校验Scope/hash→查唯一`(Scope,Kind,Key)`→同hash返原Receipt/异hashIdentityConflict→CAS全局StoreRevision→核Target revisions和delta/facts一致→写热行、不可变Facts、Receipt、事件Ordinal→StoreRevision+1。两站依赖同后端权威，不能靠各自lock。业务拒绝/NoChange也可只存Receipt+RejectedFact并+1；技术CAS失败不存伪拒绝事实。

Recorded恰Receipt非null/Fault=null；RevisionConflict为Receipt=null+TargetRevisionConflict；Unknown为null+CommitUnknown；技术Rejected为null+明确Store/identity错误。业务拒绝在Recorded.Receipt.Rejection中。已确认新请求NoChange且返当前Target，旧Expected不匹配先报TargetRevisionConflict（不可覆盖）；两个站同Expected最多一个Applied。新增第三个发生不在已提交batch中。

Runtime技术StoreRevision冲突最多3次ReadHot+重Plan，保持同原Identity/Targets/Expected，不能吞目标CAS冲突。未知Commit不走该循环，只QueryReceipt/Lookup；AbsentUnsafe/Unknown/InProgress不可重effect。AbsentSafe必须后端证明旧writer已结束/不可绕过fenced且权威确无提交；显式恢复沿原identity/payload，不改RequestId。过保证期Expired，永不授旧key重用。Query只观察，不暗启动补写/恢复。

### 4.2 接纳与取消

限制/复制→与Stop共门预约running槽和bytes→根持原Task→鉴权持Grant→查Identity→原回执或ReadHot/Plan→核budget/Grant→一次Commit→保存结果→释放所有Grant/IO借用→释放running槽→原Task完成。无无界队列。观察同身份重复同payload原回执，不新增发生/确认Fact；查询权限每次重核，不靠旧Receipt授新权。

取消接纳前NotSubmitted+CancelledBeforeAdmission、零Store；接纳后合作取消，Commit前可CancelledBeforeCommit，但等读/Grant实际归还。Commit已发保持原Task直到Known/Unknown且本地IO释放，不能以ct/OCE/WaitAsync判回滚。执行budget单调从接纳开始，查询/重试不续预算，不配合的后端使原Task仍未完成。端口异常闭合ProviderProtocolError/StoreUnavailable；若已可能Commit必须CommitUnknown，不把任意异常当NotSubmitted。Primary业务错误与Cleanup释放错误分别留原异常，已知提交不因cleanup失败变“未提交”。

### 4.3 Stop、Dispose和失败两轴

首次Stop原子关接纳，保存唯一原Stop Task，取消维护等待/订阅接纳，等原调用、worker、订阅Read/Grant与Store.Close实际完成。**Stop只关闭Store接纳/借用；不Dispose Store**：Stop成功时AdmissionClosed=true、RunningCalls=0、OpenSubscriptions=0、StoreClosed=true、StoreDisposed=false、ResourcesReleased=false，尚持独占Store。Dispose复用原Stop，随后一次Store.Dispose，且保存原Dispose Task；只有StoreClosed/StoreDisposed均为true、所有原调用/worker/Grant/订阅资源释放、cleanup无未证明项，ResourcesReleased才true。GetClosure在Dispose完成后仍允许读取本实例最终缓存，不调用已Dispose端口。

Stop故障保留原异常；Dispose在Stop**原Task已经结束**后即使它faulted，也按关闭所有已结束借用的证明尝试唯一Store.Dispose，独立保留Stop/Dispose故障，不以finally覆盖原业务错误；任何release不确定均ResourcesReleased=false。原Stop尚未结束时Dispose继续等待，不并发销毁活跃Store。重复Stop/Dispose观察同原Task，不再调用后端；无内建超时。业务Known但释放未知合法，不能归还根槽/依赖。Factory原Create异常必须带RollbackComplete，只有true且CleanupFailures为空才能证明未交付资源归还。O-10也须Stop+Dispose两阶段，不用Stop成功替代真Released。

### 4.4 事件、慢订阅和线程

Runtime强持一个维护/持久事件拉取Task；每500ms最多一个ReadEvents和一个到期提交在途，上一Task没退出不再开；本实例commit可唤醒，跨站变化由ReadEvents发现。事件Cursor严格递增，只有耐久Fact才发布；失败保留旧cursor和health，不递归制造报警。事件是刷新，业务结果以Receipt为准。

OpenSubscription授权的是当次开订阅，Grant在资源完整交付前释放，**不永久绑定旧Grant**。原请求After/Scope固定；每次公开ReadAsync都给Caller和executionBudget，Caller.PrincipalId必须等于建立者（ProofRef可更新）。先用单调budget等待缓存有Events/Gap/Closed，再对本批完整Conditions/Occurrences重新Acquire Subscribe Grant；权限须同时覆盖本Scope订阅及本批所有对象。原订阅建立时空集合明确是Scope-wide Subscribe而非任意写权。Grant有效期限为该Read剩余budget，检查到拷贝交付的线性化点，过期先胜出即拒交任何payload；成功先胜出交完整batch后Dispose Grant。ct/预算到期结束本Read且等Grant/等待timer真释放，返回AlarmRead.Fault=CancelledBeforeCommit/ExecutionDeadline，不续预算、不偷偷后台交payload。

撤权或Acquire失败返回AuthorizationDenied、Value=null，擦除未交付buffer、关闭本订阅且等待在途Read/Grant归还；再次授权需显式新OpenSubscription。缓冲仍在内存不是继续授读理由。新条件到来时Read对新对象重新鉴权；不得按开连接时的旧对象集漏检。Close/Dispose本身为资源清理，不要求恢复权限才能释放。

每订阅Capacity1..4096，Read.maxEvents1..min(256,capacity)，同时仅一Read，重入AlarmRead.Fault=InvalidInput。溢出清普通缓冲置Desynchronized，单独保留合并Gap范围；随后只发Gap，仍每次重新鉴权。调用方查当前AsOf、Close旧订阅、从`(AsOfRevision,uint.MaxValue)`重新订阅，不能静默续读称完整。源历史缺口仍保留。Close取消本Read等待并等Grant/等待timer结束，不取消业务写；Dispose复用原Close，订阅buffer真的释放后才从OpenSubscriptions扣除。Runtime Stop关闭全部自身订阅。Core不回调UI；consumer切Dispatcher，异常不进入writer。

| 资源 | Owner及归还条件 |
|---|---|
| Factory/Stores/Authority/Clock/根槽/调用令牌 | caller在Factory前强持；未排空不可释放/换实例 |
| Open返回独占Store、worker、订阅、原Task | Runtime；Stop/Dispose真实结束前保持 |
| Grant、Reader/事务/连接 | 端口及当前调用；Task返回前实际归还，迟到结果保存原身份 |
| 输入DTO/immutable snapshot | caller输入；Core验证复制，不保留可变对象/SDK句柄 |
| UI控件、Dispatcher pending、view subscription | 每view adapter和Host根；Detach原Task真结束前保持 |

## 5. Codec、身份和向量

### 5.1 公开入口和唯一流头

下面静态类型位于Core公开namespace；无IO/反射序列化/线程/可变静态表，Input/Fact/ComputeFactHash/QueryHash的maxBytes为15..1048576；Input运行时取Limits.MaxRequestBytes，Fact独立上限1048576。Commit/Snapshot为15..Int32.MaxValue，运行时取checked min(Limits.MaxHotBytes,Int32.MaxValue)，临时buffer/对象图也计入预约bytes。PageToken为47..2048，含流/checksum、未base64url前；Hash为1..Int32.MaxValue。Limits.MaxRequestBytes至少15。总长度/count在分配前拒超限。类型/格式错误抛ArgumentException；Runtime转InvalidInput/UnsupportedVersion，不吞尾部。

```csharp
public static class AlarmCodecV1
{
    public static ImmutableArray<byte> Encode(AlarmInput value,int maxBytes);
    public static AlarmInput Decode(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeFact(AlarmFact value,int maxBytes);
    public static AlarmFact DecodeFact(ImmutableArray<byte> bytes,int maxBytes);
    public static string ComputeFactHash(AlarmFact value,int maxBytes);
    public static ImmutableArray<byte> EncodeCommit(AlarmCommitBatch value,int maxBytes);
    public static AlarmCommitBatch DecodeCommit(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeSnapshot(AlarmHotSnapshot value,int maxBytes);
    public static AlarmHotSnapshot DecodeSnapshot(ImmutableArray<byte> bytes,int maxBytes);
    public static string EncodePageToken(AlarmPageToken value,int maxBytes);
    public static AlarmPageToken DecodePageToken(string token,int maxBytes);
    public static string ComputeQueryHash(CurrentAlarmQuery value,int maxBytes);
    public static string ComputeQueryHash(HistoryAlarmQuery value,int maxBytes);
    public static string Hash(ImmutableArray<byte> bytes,int maxBytes);
}
```

每个完整流均为 `ASCII("ALM1") + U16(1) + U16(0) + U16(0) + U8(FrameType) + U32(payload字节数) + payload`；固定流头15bytes。FrameType固定Input=1、Fact=2、Commit=3、Snapshot=4、PageToken=5、Query=6。顶层版本只许1.0.0，payload长度必须恰等于剩余长度且总长<=maxBytes；未知FrameType/版本、额外尾byte、截断、异常长度在分配前拒绝。嵌套DTO不重复流头；嵌套Fact/Command只写union tag及正文，不重复RequestId。调用Encode自动输出唯一canonical排序，Decode要求输入已按同顺序严格递增，不能接受乱序再偷偷正规化。

原语：Str=U16(UTF8字节数)+严格UTF8；U16/U32/U64/I64大端；Bool=00/01；enum=U8且只许已定义值；nullable=00无值或01+value；数组=U32(count)+items，default拒绝、空=00000000；UTC=I64(UtcTicks)，Duration=I64(Ticks)；hash=32原始bytes（DTO仍以64小写hex表达）；RequestId=Str(Guid的36字符小写D格式)。Ordinal/Revision wrapper不加额外字节。复合Key按DTO字段声明顺序展开；备注不做文化转换/NFC修复。Count/字符串长在分配前核业务域、checked剩余长度和总配额；Command Targets<=128、Maintenance每集合<=64、FactCount<=MaxFactsPerCommit，所有DTO嵌套数组也不得超Limits。不能以只核顶层总长代替对象个数限制。

### 5.2 Input union与逐命令字段

Input payload开头tag严格Observation=01、Command=02、Maintenance=03；与AlarmInputKind enum的0/1/2区分，Key.Kind存枚举，wire union用本表。不存在0/其它Input tag。

| union/tag | 按顺序编码的正文（只有这些字段） |
|---|---|
| Observation/01 | Definition.Id,Version；Source.SourceId,InstanceId；Epoch U64；Sequence U64；Kind U8（Sample0/Heartbeat1/AuthoritativeSnapshot2）；Value U8（Unknown0/Inactive1/Active2）；Currentity U8（Unknown0/Current1/Stale2/Disconnected3）；Quality U8（Good0/Uncertain1/Bad2）；ObservedUtc I64；nullable CoversThrough U64；nullable Evidence（Owner,Id,Version,Hash32） |
| Command/02 | 先CommandTag U8，再RequestId Str**一次**，再下表tail；派生record的继承Id不另写 |
| Maintenance/03 | 集合标签01+U32 staleCount+staleTargets；集合标签02+U32 expiredCount+expiredTargets；两个集合均必写，空集合也写标签/count。target=ConditionKey（Definition.Id,Version,SourceId,InstanceId）+ExpectedRevision U64 |

| CommandTag | 唯一tail（Id已由公共前缀写入） |
|---|---|
| 01 RegisterDefinition | AlarmDefinition所有字段：Key.Id,Version,TitleKey,DescriptionKey,RecoveryKey,Severity U16,AckPolicy U8,AllowedVisibility U8,MaxCommentScalars U32,MaxSuppressDuration I64,MaxShelveDuration I64 |
| 02 BindCondition | ConditionBinding：Key四Str,Definition两Str,FreshnessTtl I64,Revision U64；ExpectedBindingRevision U64 |
| 03 Acknowledge | U32 targetCount；每target OccurrenceId Str+ExpectedRevision U64；Comment Str |
| 04 AddComment | Target(Id Str+ExpectedRevision U64)；Comment Str |
| 05 SetVisibility | ConditionKey四Str；ExpectedVisibilityRevision U64；Mode U8；Duration I64；Reason Str |
| 06 ClearVisibility | ConditionKey四Str；ExpectedVisibilityRevision U64；Reason Str |
| 07 RecordOwnerAction | Target；Kind U8；Phase U8；Owner Str；OwnerActionId Str；nullable OwnerResultCode Str；nullable Evidence |

Targets按OccurrenceId Ordinal，维护两个集合各按Definition.Id→Version→SourceId→InstanceId Ordinal（不按ExpectedRevision决定键）排序；同集合重复Key拒绝。相同Condition可同时在stale和expired两集合，标签区分两种事实，不跨集合去重。维护Identity额外绑定BootId：`ComputeIdentity`的maintenanceBootId在Maintenance时必填且PrincipalId必须`runtime`，另外两种输入必须null；不把BootId暗塞未声明的DTO。

### 5.3 Facts、commit、hash写入者

Fact payload=FactTag U8+正文。FactTag固定：1 DefinitionRegisteredFact、2 ConditionBoundFact、3 ObservationFact、4 RaisedFact、5 ClearedFact、6 AcknowledgedFact、7 CommentFact、8 VisibilityFact、9 OwnerActionFact、10 SourceFact、11 GapFact、12 RejectedFact。正文按§3.7**该派生record**字段声明顺序；nested Occurrence/Source/Lease/Gap/Action全字段按其声明顺序展开；RecordOwnerAction在Fact内编码CommandTag07+Id一次+tail，以和Command相同唯一codec复用。字符串nullable、各enum、Evidence、Before/After revision均按§5.1，不省略默认值。AlarmFault=Code U8+MessageKey Str+U32 Arguments.Count+每Argument Str+Retryable Bool+nullable DiagnosticId Str；HistoryGap及MissingRange按各自DTO字段次序。

**FactHash=SHA256(EncodeFact(fact,maxBytes))**，包含Fact完整流头/版本和tag。Runtime调用AlarmCore.Plan后作为实际作者按Facts列表索引逐条ComputeFactHash；Store在事务边界独立重算并产生事件EventId，二者必须一致。Store不是算法Owner，不能改Fact/重新推导状态。EventOrdinal=Facts列表index+1；列表次序固定：定义/绑定Fact→ObservationFact→本次Raised或Cleared→SourceFact→GapFact（Condition/epoch/from/through，同范围打开先于闭合）→Acknowledged/Comment按Target.Id升序→Visibility按Condition升序→OwnerAction→Rejected。无状态变更的命令/迟到拒绝只含RejectedFact；SequenceGap/MissingSnapshot/SourceUnavailable是拒绝应用条件真值，仍原子记录Observation/Source/Gap及末尾RejectedFact，Delta不得包含发生清除。空Facts仅NoChange允许，仍可记唯一NoChange回执；不编假的空事件。事实的hash和EventId不编码进该Fact，不自引用。

Commit payload按AlarmCommitBatch声明顺序：Identity（Scope Str,Kind U8,Key Str,PayloadHash32）；ExpectedStoreRevision U64；Delta（五数组依次Definitions/Bindings/Sources/Occurrences/Visibility，每数组U32 count+完整DTO，键按§3规定Ordinal排序）；Facts（U32 count+每个Fact的tag/正文，**不加嵌套流头**）；Receipt（Identity完整一次、Disposition U8、StoreRevision U64、RecordedUtc I64、Targets数组、ObjectSetHash32、nullable Rejection）。Receipt.Identity必须和外层identity完全相同，Receipt.StoreRevision=checked(Expected+1)，不因重复编码省去字段；Decode和Store核对。Snapshot同理是声明顺序全部字段，数组按各自主键严格递增；无隐藏字段。

### 5.4 身份、查询/token和版本

OccurrenceId=`occ_`+SHA256(ASCII `ALM-OCC-1`+Str(Scope)+Definition两Str+Source两Str+U64(epoch)+U64(firstSequence))，保留原67byte向量。观察Identity.Key=`obs_`+SHA256(ASCII `ALM-OBS-ID-1`+同五Str（Scope一Str+Definition两Str+Source两Str）+U64(epoch)+U64(sequence))；命令Key=`cmd_`+Id D字符串。维护Key=`maint_`+SHA256(ASCII `ALM-MAINT-ID-1`+Str(Scope)+Str(BootId)+**Maintenance payload中从集合标签01至结尾的原字节**)，固定两集合标签/排序。PayloadHash=SHA256(ASCII `ALM-SEM-1`+Str(Scope)+Str(Principal，维护为runtime)+nullable Str(BootId，仅维护有值)+Encode(input))；不含ReceivedUTC、Grant DecisionId、ProofRef、等待/执行预算。ObjectSetHash=SHA256(ASCII `ALM-SET-1`+U32 count+已排序Targets)，无Targets写count0。EventId=`evt_`+SHA256(ASCII `ALM-EVT-1`+Str(Scope)+U64(StoreRevision)+U32(Ordinal)+FactHash32)。所有hash小写64hex，hash前ASCII域无长度前缀/终止byte。

Query完整流FrameType6，payload QueryTag01 Current或02 History，随后query所有字段声明顺序**排除ContinuationToken**；PageSize U32、include Bool、SourceId nullable Str、History的From/To I64和nullable Source两Str。ComputeQueryHash=SHA256该完整Query流。PageToken FrameType5，payload tag01 Current或02 History，公共Scope Str+AsOf U64+QueryHash32仅一次；Current tail=RuntimeId Str+BootId Str+ProjectionGeneration U64+nullable LastRow Str+nullable LastSource四Str；History tail=LastEvent(U64 revision+U32 ordinal)+nullable LastGap（完整HistoryGap声明字段）。在完整token流后附32bytes SHA256(前面完整流)，base64url输出**无padding**；payload长度不包括最后checksum，Decode明确分离这32bytes再检查原流长度，不能当尾字节吞掉。解码token总bytes<=2048，check未授权读取无效。初始LastEvent=(0,0)、LastGap=null；LastEvent必须<=AsOf，LastGap按§3.5全序单调且对应记录发布revision<=AsOf；事件包含Ordinal=1..MaxFactsPerCommit，订阅After允许uint.MaxValue表示跳过整revision，非事件项。

版本exact1.0.0，unknown tag/nullable flag/未定义enum/非法UTC、长度超限、重复键、排序逆序、stream截断/剩余byte均拒绝，禁止未知tag“忽略”。Input/Fact/Commit/Snapshot/Token分别Decode相应FrameType，交叉喂入拒绝。未来升版先明确新codec/Upcast/只读迁移预览，保留旧原bytes/identity/receipt，宿主显式切writer；旧版本遇新事实不可读则只读恢复，不删事实回退。

### 5.5 完整软件向量

向量是独立合成规格，C#实现仍须字段重建、Decode→Encode一致与负向量；不冒充模块运行。以下Occurrence预像67bytes：Scope=lab-a，Definition=TEMP.HIGH@1.0.0，Source=line-a/oven-01，epoch1/sequence42。

```text
414c4d2d4f43432d3100056c61622d61000954454d502e484947480005312e302e3000066c696e652d6100076f76656e2d30310000000000000001000000000000002a
SHA256=2a779da4e961377ce8f6e81c76b88c873e62f54018717bc469bf03c4512cd64b
OccurrenceId=occ_2a779da4e961377ce8f6e81c76b88c873e62f54018717bc469bf03c4512cd64b
```

Observation/单确认/ObservationFact完整流向量在下表后给出；不是仅OccurrenceId摘要。三向量共同Observation=`TEMP.HIGH@1.0.0,line-a/oven-01,epoch1,seq42,AuthoritativeSnapshot(2),Active(2),Current(1),Good(0),ObservedUTC=0001-01-01T00:00:01Z（Ticks=10000000，合法合成审计时刻）,CoversThrough=41,Evidence=null`；Caller=owner，仅PayloadHash域使用，原流不含Caller。单确认Id=`11111111-1111-1111-1111-111111111111`，Targets为上述67byte身份的occurrence、ExpectedRevision=1、Comment=`ok`。ObservationFact包含该完整Observation、ObservationHash=SHA256完整Observation Input流、ReceivedAtUTC ticks=20000000、DecisionCode=`Raised`。

| 完整流 | bytes | SHA-256 |
|---|---|---|
| Observation Input | 89 | `caf1ea507f6fc7eb0a21be578fc5d9cf256345a8aa14e9428e6a24950e94d653` |
| Acknowledge Input | 141 | `cfaf641f0856dc89c9318fda4dd827c5d9a7d7f5c06a5399eb31ba3fb6f1ca00` |
| ObservationFact | 137 | `4944d8fc35948dd4abf9073e6dee3d4ed5ebd567ee36a007d9435c2de78a395a` |
| Maintenance Input | 112 | `28aa97a61e922a8fbf2d5f15f37e4534842f8d007cebe0ccd66be99a7c10a8c0` |

完整hex（每行是一个完整流，不能截取部分字段当全流）：

```text
Observation Input
414c4d31000100000000010000004a01000954454d502e484947480005312e302e3000066c696e652d6100076f76656e2d30310000000000000001000000000000002a02020100000000000098968001000000000000002900
Acknowledge Input
414c4d31000100000000010000007e0203002431313131313131312d313131312d313131312d313131312d3131313131313131313131310000000100446f63635f32613737396461346539363133373763653866366538316337366238386338373365363266353430313837313762633436396266303363343531326364363462000000000000000100026f6b
ObservationFact
414c4d31000100000000020000007a03000954454d502e484947480005312e302e3000066c696e652d6100076f76656e2d30310000000000000001000000000000002a02020100000000000098968001000000000000002900caf1ea507f6fc7eb0a21be578fc5d9cf256345a8aa14e9428e6a24950e94d6530000000001312d000006526169736564
Maintenance Input
414c4d310001000000000100000061030100000001000954454d502e484947480005312e302e3000066c696e652d6100076f76656e2d303100000000000000020200000001000954454d502e484947480005312e302e3000066c696e652d6100076f76656e2d30310000000000000003
```

Maintenance向量使用同一完整ConditionKey，stale集合ExpectedRevision=2、expired集合ExpectedRevision=3，两个集合各1项、标签01/02均存在；相同Condition跨集合合法，任一集合内重复拒绝。ObservationFact的ObservationHash是89byte Input全流SHA，FactHash是137byte Fact全流SHA，不能反过来把FactHash填入ObservationHash。

双实例身份反例：同Scope/Definition/SourceId=line-a/epoch1/seq42，InstanceId=oven-01的70byte `ALM-OBS-ID-1`预像摘要为 `8faa903f871db884fb800b235b1dfceea5cd4daf67575c883fa3975730fd9f73`，InstanceId=oven-02为 `e632a2b992f19b93cd8bf5dac23958eb97dbc1c7dafe375ad29de89b40d238d0`。两个Key不同、各自ledger和occurence独立；同InstanceId/序号改Value或ObservedAt导致PayloadHash不同，必须IdentityConflict。两完整预像如下：

```text
414c4d2d4f42532d49442d3100056c61622d61000954454d502e484947480005312e302e3000066c696e652d6100076f76656e2d30310000000000000001000000000000002a
414c4d2d4f42532d49442d3100056c61622d61000954454d502e484947480005312e302e3000066c696e652d6100076f76656e2d30320000000000000001000000000000002a
```

## 6. AL-S1 Storage-database领域桥

### 6.1 公开构造、依赖与所有权

IM066 C0/C1规格已经接收；只读消费其[唯一指导§6/6.3/6.7](../storage-database/DEVELOPMENT-GUIDE.md)，不改上游、不把整个IM066写成待准入。AL-S1只负责报警Owner的codec、注册绑定、结果解码和Store端口；不实现事务引擎/通用SQL/连接池/技术ledger。namespace `Asun.Modules.Alarms.Storage`，引用Core、`Asun.Platform.StorageDatabase.Contracts`及Runtime；下面SC为Contracts namespace别名，SR为Runtime别名。PG专属codec单独namespace `Asun.Modules.Alarms.Storage.PostgreSql`，该类型显式引用已冻结IM066 PostgreSql公开marshal合同；Core/无UI纯桥不引用PG/Npgsql。

```csharp
public sealed record AlarmStorageOptions(string ScopeId,SC.StorageScope Scope,SC.StoreRef Store,
    SC.CallerRef ServiceCaller,TimeSpan ExecutionBudget,TimeSpan WaitBudget,
    int MaxPendingOperations,long MaxPendingBytes,int MaxResultBytes);
public sealed record AlarmStorageBindingSet(SC.StorageBindingDescriptor Commit,
    SC.StorageBindingDescriptor Hot,SC.StorageBindingDescriptor Receipt,
    SC.StorageBindingDescriptor History,SC.StorageBindingDescriptor Events);
public sealed record AlarmStorageRegistration(AlarmStorageBindingSet Bindings,
    SC.StorageBindingCatalog Catalog,SC.StorageInputLimits InputLimits,
    ImmutableArray<AlarmStatementDocument> Statements);
public sealed record AlarmStatementDocument(SC.VersionRef Version,
    ImmutableArray<byte> Bytes);
public sealed record AlarmStoragePending(AlarmIdentity AlarmIdentity,
    SC.OperationIdentity Operation,SC.TaskHandle? Task,SC.StorageExecutionState State);
public sealed record AlarmStorageClosure(bool Closed,bool Released,int RunningCalls,
    int OpenSessions,int PendingTasks,ImmutableArray<AlarmFault> CleanupFaults);
public interface IAlarmStorageStore:IAlarmStore {
    AlarmStorageClosure GetStorageClosure();
    ImmutableArray<AlarmStoragePending> GetPendingOperations();
}
public sealed class AlarmStorageStoreFactory:IAlarmStoreFactory,IAsyncDisposable {
    public AlarmStorageStoreFactory(SC.IStorageDatabase borrowedRuntime,
        AlarmStorageRegistration registration,AlarmStorageOptions options,TimeProvider clock);
    public Task<IAlarmStore> OpenAsync(AlarmRuntimeConfiguration configuration,CancellationToken ct);
    public AlarmStorageClosure GetClosure();
    public ValueTask DisposeAsync();
}
public static class AlarmStorageRegistrationV1 {
    public static AlarmStorageRegistration Create(AlarmLimits limits,int maxResultBytes);
}
public sealed record AlarmStoragePartition(SC.StorageScope Scope,string StoreId,
    long StoreGeneration,string AlarmScopeId);
public sealed record AlarmCommitPayload(SC.VersionRef Schema,AlarmStoragePartition Partition,
    AlarmCommitBatch Batch,
    AlarmHotSnapshot After):SC.IOwnerStoragePayload;
public enum AlarmStorageReadKind { Hot, Receipt, History, Events }
public sealed record AlarmReadPayload(SC.VersionRef Schema,AlarmStoragePartition Partition,
    AlarmStorageReadKind Kind,AlarmIdentity? Identity,HistoryAlarmQuery? History,
    AlarmCursor? After,int MaxEvents,Revision? Head):SC.IOwnerStoragePayload;
```

构造被动校验，不开Session。options.ScopeId与AlarmRuntimeConfiguration.ScopeId exact；Scope/Store/Profile/Generation固定，ServiceCaller是当前可信服务主体，不从AlarmCaller.ProofRef猜数据库凭据。ExecutionBudget正且≤1min、WaitBudget正且≤ExecutionBudget；首版MaxPendingOperations1..256且≥configuration.Limits.MaxRunningCalls，MaxPendingBytes≥一份最大commit/result的预约量，MaxResultBytes15..Int32.MaxValue且覆盖完整热快照；不足在Open前拒，不能截断后Complete=true。所有技术call的deadline取本次剩余期限，不刷新；清理不使用已取消的工作token。clock与报警Runtime同实例、借用。

一个factory最多一个未Disposed的Store，Open前锁门预约；成功Store归报警Runtime，失败只在部分资源真实归还后抛AlarmInitializationException。Store每个原调用先预约固定槽/bytes，显式OpenSession：Commit用Production、Hot/Receipt/History/Events用Query，技术Operation恢复用Runtime.QueryOperationAsync的Recovery授权。Open原ValueTask只AsTask一次并强持，迟到成功先接管Session再处理取消。每Session只有本call一个读/事务，最终ReleaseAsync原Task到ResourceState.Released，再Dispose原Session。无永久连接、无共享Session、无后台提前返池。Store.Close关接纳并等待原call及release；Store.Dispose复用Close并释放自己的有界缓存。Factory.Dispose等待其StoreDisposed；**永不Stop/Dispose borrowedRuntime**，宿主只在报警Runtime/桥factory真Released后关闭自己创建的storageRuntime。

### 6.2 Owner唯一字节与注册绑定

领域桥独立流头 `ASCII ALS1 + U16(1)+U16(0)+U16(0)+U8(tag)+U32(payloadBytes)`，15bytes，primitive同§5.1。CommitInput tag1=Partition+U32完整EncodeCommit长+bytes+U32完整EncodeSnapshot(After)长+bytes；ReadInput tag2=Partition+ReadKind U8+nullable Identity+nullable History（全部query字段，包含nullable token）+nullable After+MaxEvents U32+nullable Head U64。Partition=Scope五Str（Tenant/Site/Line/Station/Device）、StoreId Str、StoreGeneration I64、AlarmScopeId Str，不含Caller/Proof/预算；Store生成并与CallContext.Scope/Store exact比较，调用者不得绕Store换分区。四种Read互斥：Hot其它null/MaxEvents0；Receipt仅Identity非null、Head=null；History有History+Head（Head与内部token.AsOf相同）、其它null/MaxEvents0；Events有After+Head且MaxEvents1..256。Head允许0（初始化合法空库）。After快照由Store机械应用Delta/Gap形成，不重新判断条件；Scope/Revision/Receipt/Delta/Facts与Batch逐字段一致。Gap打开/闭合按§3.7，保留旧历史；所有canonical流的长度/count/域在分配前核。Schema属性不重复进入payload，在输入codec和Binding分别exact核验。

Result tags：3 Commit（StoreCommitState U8+nullable完整AlarmReceipt+nullable AlarmFault）；4 Hot（U32快照长+完整ALM1 Snapshot）；5 Lookup（完整AlarmLedgerLookup字段）；6 History（AlarmHistoryPage全部字段）；7 Events（AlarmEventPage全部字段）。Receipt/Ledger/Event/Page嵌套严格声明顺序，Fact采用§5.3 tag/正文；数组排序遵循§3.5，HistoryGap全键，不省Gaps。结果不是自由JSON，任何错误Schema/尾byte/超限/半页→ProviderProtocolError，未知格式→RecoveryUncertain。GetReferences只返回Empty；AlarmEvidenceRef不等于IM066.ObjectRef，未授权转成GC引用，模块不获得证据删除权。图像/点云禁止进领域blob。

```csharp
public static class AlarmStorageCodecV1 {
    public static ImmutableArray<byte> EncodeCommit(AlarmCommitPayload payload,int maxBytes);
    public static AlarmCommitPayload DecodeCommit(ImmutableArray<byte> bytes,SC.VersionRef schema,int maxBytes);
    public static ImmutableArray<byte> EncodeRead(AlarmReadPayload payload,int maxBytes);
    public static AlarmReadPayload DecodeRead(ImmutableArray<byte> bytes,SC.VersionRef schema,int maxBytes);
    public static ImmutableArray<byte> EncodeReceipt(AlarmReceipt value,int maxBytes);
    public static AlarmReceipt DecodeReceipt(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeEvent(AlarmEvent value,int maxBytes);
    public static AlarmEvent DecodeEvent(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeGap(HistoryGap value,int maxBytes);
    public static HistoryGap DecodeGap(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeCommitResult(AlarmStoreCommitResult value,int maxBytes);
    public static AlarmStoreCommitResult DecodeCommitResult(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeHotResult(AlarmHotSnapshot value,int maxBytes);
    public static AlarmHotSnapshot DecodeHotResult(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeLookupResult(AlarmLedgerLookup value,int maxBytes);
    public static AlarmLedgerLookup DecodeLookupResult(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeHistoryResult(AlarmHistoryPage value,int maxBytes);
    public static AlarmHistoryPage DecodeHistoryResult(ImmutableArray<byte> bytes,int maxBytes);
    public static ImmutableArray<byte> EncodeEventsResult(AlarmEventPage value,int maxBytes);
    public static AlarmEventPage DecodeEventsResult(ImmutableArray<byte> bytes,int maxBytes);
}
```

EncodeReceipt使用ALS1 tag8+Receipt字段（供私有行存储）；其余tag均按上表，Read输入只允许上述四种shape。公共输入codec具体类`AlarmCommitPayloadCodec(SC.VersionRef version,SC.VersionRef schema)`和`AlarmReadPayloadCodec(…same…)`实现IStoragePayloadCodec，PayloadType分别exact两个payload类型，Encode调用以上纯入口且核Schema；GetReferences验证字节后Empty。`AlarmStorageResultCodec(SC.VersionRef version,SC.VersionRef schema,AlarmStorageReadKind? kind)`实现IStorageResultCodec：kind=null仅CommitResult，其余对应Result，Validate有界完整解析、零IO。无反射/请求delegate/静态可变注册。

Registration.Create返回5条descriptor和对应codecs。OwnerKey固定`alarms`；VersionRef.Revision=1；Schema/Codec/Binding/StatementCatalog各自不同Id，前缀`alarms/1/`，后缀分别`schema/{commit-input,read-input,commit-result,hot-result,lookup-result,history-result,events-result}`、`codec/<同名>`、`binding/{commit,hot,receipt,history,events}`、`statements/<同binding>`。Schema/codec的Hash为唯一描述流SHA256：ASCII `ALS-SCHEMA-1`或`ALS-CODEC-1`+Str(Id)+U32(1)+Str(`1.0.0` Core合同)+U8(input/result tag)+Str(本节字段表对应类型名)，不用Markdown/源文件hash冒充语义版本。Binding.Version.Hash为ASCII `ALS-BINDING-1`+binding字段按声明序展开（排除自身Version和StatementCatalog.Hash，只写其Id/Revision），防止catalog包含binding ref又让binding hash包含catalog hash的循环。descriptor仍持StatementCatalog完整exact ref，绑定catalog时逐字段比较；SQL变化须新StatementCatalog修订/hash和新Binding修订，不能替换已注册同版本内容。StatementCatalog严格JSON字段/原bytes/hash生成规则和SQL正文见§6.5，不是生产现场待决项；本轮只冻结规格不生成文件。

| Binding | Kind/Purpose/Isolation | Input→Result | Permission/行/命令/重试 |
|---|---|---|---|
| commit | Transaction/Production/Serializable | commit-input→commit-result | alarms.storage.commit；MinAffectedRows1、MaxAffectedRows1、MaxCommands1、MaxRetries0 |
| hot | Read/Query/RepeatableRead | read-input→hot-result | alarms.storage.read；0/0、2、0 |
| receipt | Read/Query/RepeatableRead | read-input→lookup-result | alarms.storage.receipt；0/0、2、0 |
| history | Read/Query/RepeatableRead | read-input→history-result | alarms.storage.history；0/0、3、0 |
| events | Read/Query/RepeatableRead | read-input→events-result | alarms.storage.events；0/0、3、0 |

五条descriptor的RetryDelay=10ms、ServerLockTimeout=500ms、ServerStatementTimeout=2s、AllowEmptyBatch=false；这些是有界软件测试注册值，部署Profile显式采纳/新版本后使用，不称客户节拍。ResultSchema/Codec必须exact，输入/结果codec均在Catalog注册且VersionRef匹配。StorageInputLimits.MaxBatchRows/Bytes、MaxPayloadBytes/ResultBytes与桥额度一致；不足拒启动，不放宽上游Limits。

### 6.3 事务、快照、历史及原Operation的精确映射

Store.Commit先ReadHot验证preRevision和完整After，机械应用Delta，按Fact闭合OpenMissingRanges、历史Gap投影；若已经热头不符直接RevisionConflict且零transaction。仍须在领域事务内再次CAS，不能把先读当锁。构造`RegisteredTransactionRequest(context,operation,Commit.Version,payload,ImmutableArray<SC.ObjectRef>.Empty)`。技术Identity.Scope/StoreId/Generation/OwnerKey固定；OperationId/IdempotencyKey=`almop_`+SHA256(ASCII `ALS-ATTEMPT-1`+完整AlarmIdentity+SHA256(EncodeCommitPayload))。**技术PayloadHash必须由SR.StorageRequestHasher.Compute(requestWithPlaceholderHash,CommitDescriptor,canonicalPayload,limits)取得**，不把AlarmIdentity.PayloadHash直接塞进去；Hasher信封不编码原PayloadHash，placeholder仅用于构造后替换。只有前次技术结果已知且业务RevisionConflict，Runtime才最多3次重Plan形成下一attempt；Unknown永不生成新attempt。

领域表仅在报警Owner注册包定义，不公开到Core，不复制im066技术表：Scope分区固定完整StorageScope五字段+StoreId/Generation+AlarmScopeId，所有text C collation、ordinal、RLS同授权Scope；UInt64列numeric(20,0) CHECK 0..18446744073709551615，不转bigint。`alarms_head`一行Revision/完整snapshot bytes；`alarms_receipt`唯一(Scope,Kind,Key)，存PayloadHash32/完整receipt bytes/UTC/guarantee，不可覆；`alarms_event`唯一(Scope,revision,ordinal)，存EventId/hash/完整event bytes、UTC、nullable四ConditionKey；`alarms_gap`唯一(Scope,完整HistoryGap canonical bytes)，存发布revision/UTC/Gap bytes及检索全键；`alarms_commit`唯一(Scope,revision)，存完整ALM1 commit及其hash。blob长度≤已注册max；FK事件/Gap发布revision→commit，head和receipt与commit同事务。发生/定义/来源行只在完整snapshot投影，不另建第二真值表。初始head Revision0/合法Empty snapshot由批准Owner初始化迁移一次预置；Open不偷偷建库/建head，缺行RecoveryUncertain。

固定领域transaction按Scope锁head→查receipt唯一键（同hash原Recorded、异hashIdentityConflict，无字段变化/新领域事实）→核ExpectedRevision→校验After.Revision=Expected+1、完整数据/容量/FactHash→原子更新head+append commit/receipt/events/gaps。SQL仅位置参数，完整正文/参数见§6.5；没有请求SQL/动态表名。校验超限在Execute前Rejected CapacityExceeded，进入SQL后结果code仅0 Recorded/1 RevisionConflict/2 IdentityConflict，SQL结束总RecordsAffected=1（最终UPDATE head，即使字段不变），插入事件/Gap数量通过RETURNING计数逐项核。技术receipt记录该已知业务结果，不称技术Committed=报警Applied。

需要的上游端口已经存在：IPostgreSqlBindingCodec.GetParameters/EncodeResult、StoragePostgreSqlBackendFactory(codecs,documents…)、IStorageTrustedDocumentSource.OpenAsync(StatementCatalog)。报警Owner自身SQL/byte映射在本页决定；真实SQL执行/迁移/RLS验收后置，不能用规格冒称数据库已通过。

读取映射：Hot按输入回显+业务Read取一条完整head；Receipt按完整Identity核hash，已证实原receipt Recorded，异hashIdentityConflict，保证期过Expired；无记录默认AbsentUnsafe，不以一次NotFound授effect。History三条注册Read command依次回显输入、events、gaps，head/token固定；events cursor>LastEvent且≤head、UTC区间/Source exact，gaps按完整LastGap和§3.5规则，各取PageSize+1有界lookahead；尾页直到两集合都无more；Events同样含输入回显及两个业务command，事件>After、ascending、maxEvents+1，gap范围与覆盖明确。ResultEncoder生成完整AsOf/token/Next/AtEnd/Gaps；缺项/超限/codec错不返半页。ReadHot完整snapshot自含OpenMissingRanges，不靠SQL重新判断活动。事务/读取一律当前服务StorageAuthority核权，Core另外核操作者权限。

ExecuteTransactionAsync返回Accepted/Running/Draining等不是完成：保留原TaskHandle，GetTaskStatusAsync(new TaskQuery(context,originalHandle),ct)只观察原任务，最多一查询Task在途；StorageTaskStatus.Completed才证明本次技术执行排空。先读到OperationRecord.Committed仍等待原任务Completed再释放Session。已完成+Committed核TechnicalCommitReceipt的完整OperationIdentity、ResultSchema及ResultBytes，再DecodeCommitResult；Recorded必须原报警Receipt一致。Completed+RolledBack/Rejected且明确无提交→Rejected；可能提交/State.Unknown/通信异常→Unknown。清理错另存Closure，不能把已知Recorded改NotSubmitted；报警Runtime仍保原提交结论和释放故障两轴。

Unknown/响应丢失：只调用`QueryOperationAsync(new OperationQuery(context,originalOperation),ct)`和原`GetTaskStatusAsync`，不重复ExecuteTransaction/Observation。技术回查预算使用新有限**观察**预算，每次≤options.WaitBudget，不能刷新原执行deadline。本Store槽在方法返回前必须已知本地任务Completed、Session Released/Disposed；如果取消不能证释放，原Commit Task继续Pending，外层只有限观察。跨进程桥只能从报警receipt读取已证实结果；无原Operation资料/未知旧writer时AbsentUnsafe/RecoveryUncertain。原受管Host可保存上述Pending完整identity作只读恢复，Query不生成新effect、不自动对账写。Factory/Store/GetClosure保持原cache至真Released。

### 6.4 双无UI Host与切片断言

两Host分别取§7 machine/mes配置，先预约各自根槽再**显式创建IM066 Runtime**：唯一公开`new SR.StorageRuntimeFactory(new StorageRuntimeDependencies(resolver,backends,storageClock,barrier),new StorageFactoryOptions(5s))`，CreateAsync(storageConfiguration,storageAuthority,ct).AsTask只转一次；注入IM066已接收C1的有界fake backend，不重写storageRuntime。resolver在原ResolvedStorageConfiguration.Bindings中接入Registration.Catalog的5 descriptor/codecs；Owner registration登记`alarms`和exact Scope/Store，References Empty resolver不能读私有表。Machine SC.Scope=`tenant-a/site-a/line-a/station-a/oven-01`，MES=`tenant-b/site-b/line-b/station-b/edge-1`，Store分别`alarms-machine/alarms-mes`、Generation1，Profile和其它VersionRef取各自resolver纯夹具的精确Hash，不能共享权限或凭据。

两Host独立options=(本AlarmScope,上述Scope/Store,CallerRef(`alarms-service-m/i`,`authority-m/i`),Execution5s,Wait1s,MaxPending16,MaxPendingBytes64MiB,MaxResultBytes16MiB)，Registration.Create(该Host Limits,16MiB)→new AlarmStorageStoreFactory(storageRuntime,registration,options,同clock)→new AlarmRuntimeFactory(new AlarmDependencies(bridge,alarmAuthority,clock),5s)→Create→Register/Bind→§7.3各自scenario。顺序和调用全经固定Task槽；factory拒容量在技术端口前零OpenSession。finally sub Close/Dispose→alarm Stop/Dispose→bridge.Dispose→宿主storage Stop(原StopRequest/InstanceEpoch)/Dispose，所有原Tasks保存且独立Primary/Cleanup；任何前置未排空不得先Dispose兄弟/借用Runtime。Slot扩展固定StorageCreate/StorageStop/StorageDispose/BridgeDispose，不用Task无限列表。

有限观察10s/工作取消120s/外层watchdog180s复用§7根；GetTaskStatus有TaskHandle但原方法已返回时，Host/bridge强持它且每次1s观察、不并发开第二query；Pending计数/bytes保持至Completed和Session Released。known commit+BeforeResourceRelease barrier：先QueryOperation能见Committed，Alarm.Commit原Task不完成、不能返槽；解除后真释放，返回Recorded。失败清理沿同原Task，不再次Create/Stop。两个host先后恢复不同Boot仍保Scope ledger/水位；S1 fake只证明映射、事务调用、原Task和资源闭包，不能称真实PG耐久。

| ID | 必须输入/结果断言 |
|---|---|
| S-01 | Registration5项exact CLR PayloadType/Schema/result tags；交叉codec/尾byte/超限拒，Empty引用合法；§5观察/事实向量嵌入CommitInput不改字节 |
| S-02 | 成功commit使完整head、receipt、events、gap同revision；Next/History双集合不漏同From两个不同gap；head改变SnapshotChanged |
| S-03 | 两Store相同Expected，一次Recorded、另RevisionConflict；最多3次已知重Plan；技术attempt hash重新计算而报警RequestId不变 |
| S-04 | commit响应丢失→原Operation回查；零二次Execute、原Receipt可读；NotFound无writer终止证明→AbsentUnsafe |
| S-05 | known commit但任务Draining时不释放Session/返槽；Open迟到先接管；Release fault保Primary/cleanup；borrowed runtime Stop/Dispose调用数均0 |
| S-06 | 错Scope/Generation/服务权限/ResultSchema拒；截断snapshot只读RecoveryUncertain；回退旧codec不覆写新事实；Factory额度满零技术调用 |

### 6.5 PG领域注册包的确定SQL与marshal

本节只冻结Owner元数据与算法；Storage工程的`PostgreSql/AlarmPostgreSqlBindingCodec.cs`实现IM066的IPostgreSqlBindingCodec，构造器`AlarmPostgreSqlBindingCodec(SC.StorageBindingDescriptor binding,AlarmLimits limits,int maxResultBytes)`；`Version=binding.InputCodec`、InputSchema/ResultSchema exact，GetParameters先完整Decode/验证canonical输入再返回固定BCL值，EncodeResult只核固定命令/列数/实际写入计数并调用§6.2 result编码，零IO、不取连接。Storage工程增加IM066 PostgreSql公开合同引用；不是Core依赖、也不实现第二数据库后端。

分区键p=大端`ASCII ALS-SCOPE-1+Str(tenant/site/line/station/device五项)+Str(StoreId)+I64(Generation)+Str(AlarmScopeId)`原bytes；不是仅tenant或hash，不因同SourceId混分区。五表共有p bytea NOT NULL；head的r为numeric(20,0)、b为bytea，PK(p)，r范围0..UInt64.Max。commits(p,r,b,h) PK(p,r)，r>0、h长度32；receipts(p,k,x,h,b,u) PK(p,k,x)，k0..2、h32、u bigint精确UTC ticks；events(p,r,o,b,u,d,v,s,i) PK(p,r,o)，o1..MaxFactsPerCommit、u bigint精确UTC ticks，四条件Text全null或全有；gaps(p,b,r,u,fr,fo,tr,to_,k,d,v,s,i,z) PK(p,b)，u bigint精确UTC ticks，fr/tr numeric、fo/to_ bigint0..UInt32.Max、k0..3、z ReasonCode Text、四条件同全null/全有，CHECK(From<=Through)。所有text COLLATE C，所有blob有限CHECK octet_length(b)<=注册maxResultBytes，全部r numeric合法域；events/gaps发布r FK commits(p,r) RESTRICT，receipt引用原commit修订从其canonical验证；创建/check/index/初始head属于Owner受控迁移，Runtime.Open只验证，零DDL/自动删除。

RLS：Owner迁移建立`alarms.scope_acl(p bytea,db_role name,can_read boolean,can_write boolean,PRIMARY KEY(p,db_role))`，只由已获部署授权的迁移主体写；runtime不可写ACL。五领域表启用并FORCE ROW LEVEL SECURITY，SELECT USING `EXISTS(SELECT 1 FROM alarms.scope_acl a WHERE a.p=<当前表>.p AND a.db_role=current_user AND a.can_read)`，INSERT/UPDATE相同WITH CHECK再要求can_write，DELETE不给runtime授权。scope_acl允许Runtime SELECT但只读当前db_role行；RLS不是靠未知im066 session变量猜授权。数据库角色仍满足IM066非superuser/无BYPASSRLS等要求；桥SC.CallContext和技术Authority每call核Scope，acl只限定该角色已登记分区，不替代操作者权限。生产Scope/角色/ACL由部署输入，软件设计无动态角色升级。

Commit参数固定：$1 p Bytea，$2 Expected UInt64，$3 New UInt64，$4 k Int32，$5 key Text，$6 payloadHash Bytea，$7 afterSnapshot Bytea，$8 commit Bytea，$9 receipt Bytea，$10 events Text，$11 gaps Text，$12 RecordedUTC Int64（UtcTicks），$13 commitHash Bytea。合法shape/After与batch一致/全hash/limits在Store和codec各自核，不允许绕Store直接提供任意After。事件JSON顺序与Facts一致，字段`o,b,u,d,v,s,i`，b是完整AlarmEvent canonical小写hex；gap JSON字段`b,fr,fo,tr,to_,k,d,v,s,i,z,u`，b是完整HistoryGap canonical hex；数值UInt64用十进制字符串，字符串JSON由System.Text.Json固定属性序列编码且无缩进，null条件完整四null。p/r取外层参数，不受JSON覆盖。输入校验数目/内容后下列SQL是唯一可信固定命令（分号终结、LF、无注释），不是产品代码已实施：

```sql
WITH h AS MATERIALIZED (SELECT r,b FROM alarms.head WHERE p=$1 FOR UPDATE),
old AS MATERIALIZED (SELECT h,b FROM alarms.receipts WHERE p=$1 AND k=$4 AND x=$5),
q AS MATERIALIZED (
 SELECT CASE WHEN EXISTS(SELECT 1 FROM old WHERE h<>$6) THEN 2
             WHEN EXISTS(SELECT 1 FROM old) THEN 0
             WHEN h.r<>$2 THEN 1 ELSE 0 END AS code,
        NOT EXISTS(SELECT 1 FROM old) AND h.r=$2 AS apply,
        COALESCE((SELECT b FROM old),$9) AS rb FROM h),
c AS (INSERT INTO alarms.commits(p,r,b,h)
 SELECT $1,$3,$8,$13 FROM q WHERE apply RETURNING r),
a AS (INSERT INTO alarms.receipts(p,k,x,h,b,u)
 SELECT $1,$4,$5,$6,$9,$12 FROM q WHERE apply RETURNING k),
e AS (INSERT INTO alarms.events(p,r,o,b,u,d,v,s,i)
 SELECT $1,$3,j.o,decode(j.b,'hex'),j.u::bigint,j.d,j.v,j.s,j.i
 FROM q CROSS JOIN jsonb_to_recordset($10::jsonb)
 AS j(o integer,b text,u text,d text,v text,s text,i text)
 WHERE q.apply RETURNING o),
g AS (INSERT INTO alarms.gaps(p,b,r,u,fr,fo,tr,to_,k,d,v,s,i,z)
 SELECT $1,decode(j.b,'hex'),$3,j.u::bigint,j.fr::numeric,j.fo,j.tr::numeric,j.to_,j.k,j.d,j.v,j.s,j.i,j.z
 FROM q CROSS JOIN jsonb_to_recordset($11::jsonb)
 AS j(b text,fr text,fo bigint,tr text,to_ bigint,k integer,d text,v text,s text,i text,z text,u text)
 WHERE q.apply ON CONFLICT(p,b) DO NOTHING RETURNING k)
UPDATE alarms.head t SET r=CASE WHEN q.apply THEN $3 ELSE t.r END,
 b=CASE WHEN q.apply THEN $7 ELSE t.b END FROM q WHERE t.p=$1
RETURNING q.code,CASE WHEN q.code=0 THEN q.rb ELSE NULL END,
 (SELECT count(*)::integer FROM c),(SELECT count(*)::integer FROM a),
 (SELECT count(*)::integer FROM e),(SELECT count(*)::integer FROM g),t.r;
```

commits.h保存**完整commit SHA256**；$6仍是identity payloadHash，$13是SHA256($8)，c行写$13。Gap相同canonical b重放只一历史投影，打开/闭合完整Facts仍在events；gap.firstPublished/UTC保原，g计数≤输入distinctGap数。apply=true要求c/a各1、e=Facts.Length、g≤distinctGaps，apply=false四计数均0；r=after或原r；冲突code1/2 receipt必须null。旧receipt同hash原完整bytes返回，不使用当前request重编码。SQL返回零行表示缺head/权限/损坏，ProviderProtocolError/RecoveryUncertain；不初始化默认行。

Read catalog固定语句（参数字节类型/行最大值由codec核；PageSize+1≤257）：

```sql
SELECT r,b FROM alarms.head WHERE p=$1;
SELECT h,b,u FROM alarms.receipts WHERE p=$1 AND k=$2 AND x=$3;
SELECT r,o,b FROM alarms.events WHERE p=$1 AND (r,o)>($2,$3) AND r<=$4 AND u>=$5 AND u<$6 AND ($7::text IS NULL OR (s=$7 AND i=$8)) ORDER BY r,o LIMIT $9;
SELECT fr,fo,tr,to_,k,d,v,s,i,z,b FROM alarms.gaps WHERE p=$1 AND r<=$2 AND ((u>=$3 AND u<$4) OR k IN (0,3)) AND ($5::text IS NULL OR (s=$5 AND i=$6) OR (k IN (0,3) AND s IS NULL)) AND (fr,fo,tr,to_,k,COALESCE(d,''),COALESCE(v,''),COALESCE(s,''),COALESCE(i,''),z)>($7,$8,$9,$10,$11,$12,$13,$14,$15,$16) ORDER BY fr,fo,tr,to_,k,d NULLS FIRST,v NULLS FIRST,s NULLS FIRST,i NULLS FIRST,z LIMIT $17;
SELECT r,o,b FROM alarms.events WHERE p=$1 AND (r,o)>($2,$3) AND r<=$5 ORDER BY r,o LIMIT $4;
SELECT fr,fo,tr,to_,k,d,v,s,i,z,b FROM alarms.gaps WHERE p=$1 AND r>$2 AND r<=$5 ORDER BY r,fr,fo,tr,to_,k,d NULLS FIRST,v NULLS FIRST,s NULLS FIRST,i NULLS FIRST,z LIMIT $4;
```

每行就是一个固定命令，顺序Hot、Receipt、History-events、History-gaps、Events-events、Events-gaps；每Read binding在前置输入回显后按对应1/2行装配。History无LastGap时全序哨兵From/Through0/0、k=-1、四Key/Reason空；非null完整tuple编码，保证合法gap包括cursor0都大于哨兵。数值列使用UInt64/UInt32/Int32、条件Text nullable、b Bytea、u Int64 UTC ticks，不把numeric返回decimal误当UInt64，A1按登记类型核再交codec。History结果有lookahead则移除仅超出PageSize的一项并给token；最后键分别取交付Items/Gaps末项，某集合本页为空保持原last。Hot必须一行；Receipt零行→AbsentUnsafe，过本ScopeLedgerGuarantee显式Expired仅有持久retirement证据时返回，不能从当前UTC单独推旧writer已死；对应row h异payload→IdentityConflict。

Events-events读无head，因此桥先Hot取得H并限定r<=H（该语句增加`AND r<=$5`，$5 UInt64=H）；Events-gaps按`r>After.Revision AND r<=H`读取保留缺口投影；同一revision中具体SourceSequence GapFact已经以完整AlarmEvent存于events，不能依赖gaps表的revision单列推断ordinal。两条结果只到H，Read后head校验变化则重读最多3次，不拼新旧页。**Gap数量>maxEvents时不能先读完整事件再静默漏gap**：Events结果Items=Empty、Next保持输入After、AtEnd=false、Gaps为一个Unavailable覆盖(After,(H,uint.MaxValue))，ReasonCode=Unavailable；consumer走snapshot重建，不无限读同一gap分页。未超限时Next为最后事件cursor或无事件时(H,uint.MaxValue)，AtEnd依据lookahead，两类gap均显式包含。Retention/Unavailable在History选取保守覆盖区间，可能多报但不宣称遗漏没有；来源Missing事实通过原events保留精确内容。

catalog JSON严格字段`kind,id,revision,ownerKey,binding,codec,commands`，无BOM/缩进，字段此顺序、commands数组顺序、嵌套ref id/revision/hash固定、LF一个结尾；kind=`StatementCatalog`，id/revision来自descriptor.StatementCatalog，binding=Binding.Version、codec=InputCodec；每条command字段依次kind/sql/parameterTypes/resultColumnTypes/maxRows/maxBytes。JSON转义使用System.Text.Json默认JavaScriptEncoder，不插入手写反斜杠，SQL原换行保留LF、文末一个分号，不替换标识符。Hash为最终JSON原bytes SHA256，Registration.Statements返回该5份不可变原文；宿主可信DocumentSource只按exact ref转交这些bytes。PG SQL或marshal改变必须提升Binding/StatementCatalog修订；新schema需Owner迁移plan及真实RLS/Unknown资格，当前无运行。精确结果回显和列型表见§6.6；这是同一注册目录，不建立第二套binding。

### 6.6 结果回显、输入配额、完整恢复和一致性修复

**消除隐藏请求缓存。** IM066的`IPostgreSqlBindingCodec.EncodeResult(commands,maxResultBytes)`没有请求参数，也不获得Reader/Session/Context；每个Read binding在§6.5业务SQL前加一个固定Read command：`SELECT $1::bytea AS canonical_input;`，唯一参数Bytea为完整ALS1 ReadInput原bytes、唯一结果Bytea，maxRows1。command0必须exact回显输入，业务command从1开始；Hot/Receipt共2、History/Events共3，与§6.2一致。EncodeResult从command0有界DecodeRead，得到Partition、Identity、完整History及Head/After，不用static/AsyncLocal/上次GetParameters缓存。每份codec可被并发安全共享；跨绑定只在Version/Schema/同一实例均一致时复用。结果中的head/token/query hash由回显原请求和本事务结果构造；桥仍按原request逐字段复核回显、Scope、AsOf、Receipt和cursor，数据库回显不授权限。

GetParameters按binding的ReadKind核输入shape：command0只回canonicalInput独立byte[]；Hot业务返回p；Receipt返回p/k/key；History事件参数为p/LastEvent.Revision/LastEvent.Ordinal/Head/FromUtc.UtcTicks/ToUtc.UtcTicks/nullableSourceId/nullableInstanceId/PageSize+1；History gap参数依次p/Head/FromUtc.UtcTicks/ToUtc.UtcTicks/SourceId/InstanceId/完整LastGap十元组/PageSize+1；Events事件参数p/After.Revision/After.Ordinal/maxEvents+1/Head，Events gap参数p/AfterRevision/maxEvents+1/Head。§6.5六条业务SQL中，Events两条在此重复列出用于参数/列数核对，必须与§6.5完全一致：

```sql
SELECT r,o,b FROM alarms.events WHERE p=$1 AND (r,o)>($2,$3) AND r<=$5 ORDER BY r,o LIMIT $4;
SELECT fr,fo,tr,to_,k,d,v,s,i,z,b FROM alarms.gaps WHERE p=$1 AND r>$2 AND r<=$5 ORDER BY r,fr,fo,tr,to_,k,d NULLS FIRST,v NULLS FIRST,s NULLS FIRST,i NULLS FIRST,z LIMIT $4;
```

两条SQL按§6.5原文执行，不在LIMIT后拼AND；Events-gaps只按发布revision范围读取，不使用隐藏的 `(tr,to_)` 请求游标。同一revision的SourceSequence GapFact已作为完整AlarmEvent存入events，不能从gaps表的revision单列推断ordinal。HistoryGap十元组类型顺序UInt64/UInt32/UInt64/UInt32/Int32/Text×5；Kind哨兵-1只在读取参数、从不进入DTO。参数类型History-events为Bytea/UInt64/UInt32/UInt64/Int64/Int64/Text/Text/Int32；History-gaps为Bytea/UInt64/Int64/Int64/Text/Text/UInt64/UInt32/UInt64/UInt32/Int32/Text×5/Int32；Events-events为Bytea/UInt64/UInt32/Int32/UInt64；Events-gaps为Bytea/UInt64/Int32/UInt64。Hot为Bytea，Receipt为Bytea/Int32/Text。Commit参数13项按§6.5顺序，类型Bytea/UInt64/UInt64/Int32/Text/Bytea/Bytea/Bytea/Bytea/Text/Text/Int64/Bytea。command类型校验后才物化BCL值。

业务结果列型固定：Commit=Int32/Bytea(nullable)/Int32×4/UInt64（7列）；Hot=UInt64/Bytea（2）；Receipt=Bytea/Bytea/Int64（3）；events=UInt64/UInt32/Bytea（3）；gaps=UInt64/UInt32/UInt64/UInt32/Int32/Text×5/Bytea（11）。Read.AffectedRows=0；Commit.AffectedRows=1、返回恰1行，code1/2转领域RevisionConflict/Rejected IdentityConflict，不当成功报警。SQL无序列/设备/外发副作用。events.b用新增ALS1 tag9完整AlarmEvent声明字段编码；gaps.b用tag10完整HistoryGap；两个纯入口`EncodeEvent/DecodeEvent`及`EncodeGap/DecodeGap`按其他codec方法同形（value/bytes,maxBytes），完整15byte流头、无多余尾byte。结构列与canonical中的cursor/UTC/四Condition/Gap全键逐项等值；不一致ProviderProtocolError、零页面。事件Condition投影取Fact显式Condition或Occurrence.Condition；只有Id的Comment/OwnerAction从本次Before/After的稳定发生取原Condition；定义登记或Rejected无具体对象时四null，不能从正文字符串猜Source。

Store读取若发生合法的空行：Hot缺头RecoveryUncertain；Receipt无行返回完整请求Identity+AbsentUnsafe；History/Events两个集合都空仍按回显Head返回合法空页/Next，不返回null Schema。History token从回显query.ComputeQueryHash和Head/LastEvent/完整LastGap生成，PageSize也入hash；续页不得混换head。Hot由snapshot.StoreRevision与r相等、Scope等于Partition验证。Events先独立ReadHot捕获Head，再原Read transaction并后置Head检查（3次上限）；最后Page.AtEnd=true时Next=(Head,uint.MaxValue)，否则Next=交付Items末cursor；gap超限返回一个Unavailable且不推进原cursor。解码结果不建立跨事务MVCC。

Registration.InputLimits由Create一次checked确定，MaxIdBytes128；MaxPayloadBytes=checked(2*min(MaxHotBytes,Int32.MaxValue)+4096)，结果/中间输入实际须≤Int32.MaxValue；MaxResultBytes=实参；MaxReferences1（合法Empty），MaxBatchRows=checked(2+2*MaxFactsPerCommit)，MaxBatchBytes=MaxPayloadBytes，MaxCatalogEntries64，MaxCatalogBytes=checked(五份statement原bytes+五descriptor及codec注册描述bytes)。这些是桥所需最低值，宿主IM066 InputLimits逐项覆盖且runtime排队/bytes配额满足，再允许Open；缺失拒初始化，不自动提高上游Profile。Store factory必须显式用Registration.InputLimits传SR.StorageRequestHasher.Compute。Commit完整After、两份编码/结果、JSON展开和连接任务占用按实测对象图计入MaxPendingBytes，按槽先预约最坏值；§6.4 Host使用MaxPendingBytes=64MiB、MaxResultBytes=16MiB，足够单批预约，不能因MaxPending16而隐式允许16份64MiB。

**首次提交与Unknown恢复。** Ledger.AbsentUnsafe是查询事实，不是新请求唯一性的证明。宿主首次调用Execute只能使用其新生成、从未发出的RequestId；来源首次Observe须原Owner保证同Instance/epoch/sequence无未决旧writer，Runtime在途同Identity同hash返回原Task，同identity异hash拒。这些是首次接纳的输入前置条件，不靠Lookup猜“从未请求”；拒权不占身份。一个已经提交/可能提交的原意图，无论重启或Lookup空，都只能QueryReceipt/原Operation，不能再次走首次Execute/Observe。S1本版不授AbsentSafe、不提供自动重effect；无receipt且没有原Operation完整资料时保AbsentUnsafe/RecoveryUncertain。新请求的唯一Alarm receipt约束和StoreRevision CAS原子守住并发，同RequestId已Recorded即原Receipt。技术Unknown的原identity/payload/TaskHandle在GetPendingOperations和宿主根中保留；进程恢复时原Host保存的Pending精确SC Operation字段只读QueryOperation，不能把它改成新CallContext的Store/Generation。跨进程需要保存未决意图时由宿主已有受管请求journal保留该typed Pending；没有该证据时只凭Alarm receipt核已知结果，未知保持，不猜原OperationId。无额外设备动作可被重放。

**无限历史不挤入热快照。** 首版不自动删除Receipt/Commit/Events/Gap：LedgerGuarantee是最低保证、不是TTL删库策略，AL-S1保留全部原identity，同旧Key永远原Receipt/IdentityConflict；Expired只有批准retirement墓碑才能返回，本版未提供retirement写入口。热retained仅Active或Unacknowledged；事务机械剔除Cleared且Acked/NotRequired行，其完整Occurrence仍在历史Facts。Source.CurrentOccurrenceId只指Active，Visibility.Mode=None行保revision。AlarmHotSnapshot.Gaps最多64项且仅含ImportedTruncation/Unavailable/Retention等恢复完整性告警；SourceSequence全部历史保在gaps/events，当前精确OpenMissingRanges在热快照，Source.HistoryComplete=false保留。新SourceSequence GapFact不不断追加热Gaps导致数日后StoreFull。热Gaps超64不合并成“完整”，置Complete=false/RecoveryUncertain并拒写，原资料不删除；历史查询照全键完整分页。Owner迁移只预置本Schema/索引/RLS与合法r0完整空snapshot，Existing head不覆盖、重复初始化同bytes no-op、异bytes拒；备份/恢复引用目录对本版IM066 ObjectRef始终Empty，但仍核本报警Scope全部5事实表、ACL、codecs和commit/head链，不能以EvidenceRef冒称保管图像字节。

**SQL范围反例。** 更新head与commit/event/receipt同一个技术事务；code1/2无新增领域Fact但固定UPDATE相同值产生一条技术影响行，不改报警revision。Gap.d/v/s/i全null或全有，SourceSequence必须有完整Condition；相同From、不同Through/Kind/Condition/Reason的b不同，均分页。对C collation nullable Key统一用COALESCE空串作比较和ORDER BY，合法Key非空故null哨兵唯一。注册函数不改变技术表/技术fence策略；Serialize失败是已知NoCommit时可原Request重Plan的技术冲突，可能提交时Unknown只读。所需上游原Owner仅IM066的公开Session/Transaction/Read/Operation/Task/Release端口；这些已冻结，未在本页要求上游新API。

## 7. 两个独立Synthetic Host（软件oracle，不是生产资格）

### 7.1 唯一测试夹具和完整参数

以下是**未来Smoke内的软件规格/可编译目标片段，尚无实现/运行**；只依本页实际Factory/DTO/端口。构造参数仅使用AlarmLimits的固定11项；订阅容量只在SubscriptionRequest传，发生容量用MaxRetainedOccurrences（包括清除未确认），不另设活动数专属配额。

Smoke私有夹具精确构造：`SyntheticClock(DateTimeOffset start)`继承TimeProvider，GetTimestamp为1e7Hz单调ticks、CreateTimer为可控可取消timer、`Advance(TimeSpan)`同时前进UTC/单调并触发到期timer，`ActiveTimerCount`给尚未Dispose的timer数；`MoveUtc(TimeSpan)`仅改UTC；`SyntheticAuthority(ImmutableArray<SyntheticRule>,TimeProvider)`实现IAlarmAuthority，rule=(PrincipalId,ProofRef,ScopeId,ImmutableArray<AlarmPermission>)，只许本Scope对象，匹配失败Fault；Grant.DecisionId=`grant_`+每实例递增序号，MaxHold单调到期、Dispose记录真实归还，`BorrowedCount`为尚未Dispose的Grant数，无静态计数。`SyntheticRepository(AlarmRuntimeConfiguration)`持有本Scope耐久模拟事实/ledger，`BorrowedCount`为Store调用中的IO借用数，容量/bytes按Limits；`SyntheticStoreFactory(SyntheticRepository,SyntheticSchedule)`实现IAlarmStoreFactory，每Open返回新的独占Store包装同一仓库。仓库用一把lock/CAS原子写本页batch，不能重写reducer；用于两Runtime并发时共享Repository、Factory各自独立。`SyntheticSchedule()`无参构造，`Mode`属性使用`SyntheticScheduleMode` enum None/OpenBlocked/CommitRecordedResponseLost/CloseBlocked/DisposeBlocked，闩锁、Open/Commit/Read/Close/Dispose计数均实例字段；`ReleaseAll()`只解除本夹具阻塞。Lookup响应Unknown与持久事实分别注入，不把mock视作真正durability。

构造前需根槽。每Host完全独立配置如下，所有11个Limits参数均提供：

```csharp
// Machine host，全部配置值，不依赖任何全局默认
var ml = new AlarmLimits(MaxDefinitions:16,MaxBindings:32,MaxRetainedOccurrences:64,
    MaxRequestBytes:16384,MaxFactsPerCommit:256,MaxRunningCalls:8,MaxSubscriptions:4,
    MaxSubscriptionCapacity:64,MaxLedgerEntries:4096,MaxLedgerBytes:4194304,
    MaxHotBytes:16777216);
var mc = new AlarmRuntimeConfiguration("synthetic.machine","machine-host-1","boot-m1",
    ml,TimeSpan.FromSeconds(5),TimeSpan.FromMilliseconds(500),TimeSpan.FromHours(24));
var md = new AlarmDefinition(new("TEMP.HIGH","1.0.0"),"Alarms.Temp.Title",
    "Alarms.Temp.Description","Alarms.Temp.Recovery",700,AckPolicy.Required,
    VisibilityCapabilities.Shelve,512,TimeSpan.FromMinutes(10),TimeSpan.FromMinutes(5));
var mb = new ConditionBinding(new(md.Key,new("line-a","oven-01")),md.Key,
    TimeSpan.FromSeconds(10),new Revision(0));
var madmin = new AlarmCaller("admin-1","proof-admin-m");
var msource = new AlarmCaller("owner-machine","proof-source-m");
var moperator = new AlarmCaller("operator-1","proof-operator-m");
var mmaint = new AlarmCaller("maint-1","proof-maint-m");
var mo = new AlarmFactoryOptions(TimeSpan.FromSeconds(5));
// MES host，可独立运行，不复用Machine运行/权限/订阅集合
var il = new AlarmLimits(MaxDefinitions:32,MaxBindings:64,MaxRetainedOccurrences:128,
    MaxRequestBytes:32768,MaxFactsPerCommit:256,MaxRunningCalls:16,MaxSubscriptions:4,
    MaxSubscriptionCapacity:64,MaxLedgerEntries:8192,MaxLedgerBytes:8388608,
    MaxHotBytes:16777216);
var ic = new AlarmRuntimeConfiguration("synthetic.mes","mes-host-1","boot-i1",il,
    TimeSpan.FromSeconds(5),TimeSpan.FromMilliseconds(500),TimeSpan.FromHours(24));
var id = new AlarmDefinition(new("QUEUE.BACKLOG","2.1.0"),"Alarms.Queue.Title",
    "Alarms.Queue.Description","Alarms.Queue.Recovery",400,AckPolicy.Optional,
    VisibilityCapabilities.Suppress,256,TimeSpan.FromMinutes(10),TimeSpan.FromMinutes(5));
var ib = new ConditionBinding(new(id.Key,new("mes","edge-1")),id.Key,
    TimeSpan.FromSeconds(30),new Revision(0));
var iadmin = new AlarmCaller("admin-2","proof-admin-i");
var isource = new AlarmCaller("owner-mes","proof-source-i");
var ioperator = new AlarmCaller("operator-2","proof-operator-i");
var io = new AlarmFactoryOptions(TimeSpan.FromSeconds(5));
```

Machine授权完整表：admin RegisterDefinition/BindCondition/ReadCurrent/ReadHistory/ReadReceipt/Subscribe；source PublishCondition/RecordOwnerAction/ReadReceipt；operator Acknowledge/Comment/ReadCurrent/ReadHistory/ReadReceipt/Subscribe；maint Shelve/Unsuppress/ReadCurrent/ReadReceipt/Subscribe。MES表相同角色映射，operator额外Suppress/Unsuppress，source Owner=mes，admin2、operator2分别Proof exact匹配。无人获设备命令或质量权限。Open/每Read使用同表重新发Grant；撤权夹具删rule，下一Read不得交payload。两个Scope授权不交叉。单call executionBudget固定2s、subscription request=(After从读取AsOf,Capacity=64)。每个Factory构造为`new AlarmRuntimeFactory(new AlarmDependencies(storeFactory,authority,clock),options)`，没有第四依赖。

### 7.2 Factory前根槽、原Task与有限观察

两个Host均用下面Smoke私有实例根（每个可独立实例化；单根MaxSlots=2、总预约128MiB，每Host预约64MiB）。Program/STA supervisor在Factory前构造并强持该根至最后返回；非静态单例。ticket.Key固定Machine=`machine-run-1`、MES=`mes-run-1`，已存在key返回**原ticket**，不二次Create。满槽/超总bytes在Factory/夹具构造前拒绝。root在Start门内先登记ticket再调用body，body强持Factory、configuration、repository、authority、clock、cancel源；原Task保存后才await。

```csharp
// 本段为待实现Host helper的完整行为；只在唯一Smoke，不进入产品Core。
enum HostCall { Create, Register, Bind, Work, Query, Subscribe, Read,
    SubscriptionClose, SubscriptionDispose, Stop, Dispose, Count }
sealed class HostTicket {
    public required string Key;
    public required long Bytes;
    public readonly object Gate = new();
    public readonly Task?[] Calls = new Task?[(int)HostCall.Count];
    public readonly CancellationTokenSource Work = new(TimeSpan.FromSeconds(120));
    public readonly List<Exception> Cleanup = new(); // 最多4：sub close/dispose、stop/dispose
    public Exception? Primary;
    public IAlarmRuntime? Runtime;
    public IAlarmSubscription? Subscription;
    public AlarmRuntimeFactory? Factory;
    public AlarmDependencies? Dependencies;
    public SyntheticRepository? Repository;
    public SyntheticSchedule? Schedule;
    public SyntheticClock? Clock;
    public SyntheticAuthority? Authority;
    public Task? Body;
    public AlarmIdentity? LastIdentity;
    public AlarmWriteResult? LastResult;
    public bool AllReturned;
    public Task<T> Keep<T>(HostCall slot,Func<Task<T>> start) {
        lock(Gate) {
            var old=Calls[(int)slot];
            if(old is not null && !old.IsCompleted) throw new InvalidOperationException("slot busy");
            var original=start(); Calls[(int)slot]=original; return original;
        }
    }
    public Task Keep(HostCall slot,Func<Task> start) {
        lock(Gate) {
            var old=Calls[(int)slot];
            if(old is not null && !old.IsCompleted) throw new InvalidOperationException("slot busy");
            var original=start(); Calls[(int)slot]=original; return original;
        }
    }
}
sealed class HostRoot {
    readonly object gate=new();
    readonly HostTicket?[] slots=new HostTicket?[2];
    long reserved;
    public HostTicket Start(string key,Func<HostTicket,Task> body) {
        lock(gate) {
            foreach(var existing in slots) if(existing?.Key==key) return existing;
            int index=Array.FindIndex(slots,x=>x is null);
            const long bytes=64L*1024*1024;
            if(index<0 || checked(reserved+bytes)>128L*1024*1024)
                throw new InvalidOperationException("host capacity");
            var t=new HostTicket { Key=key,Bytes=bytes };
            slots[index]=t; reserved=checked(reserved+bytes);
            try { t.Body=body(t); }
            catch(Exception ex) { t.Primary=ex; t.Body=Task.FromException(ex); }
            return t;
        }
    }
    public bool TryReturn(HostTicket t) {
        lock(gate) lock(t.Gate) {
            int index=Array.FindIndex(slots,x=>ReferenceEquals(x,t));
            if(index<0) return false;
            if(t.Body is null || !t.Body.IsCompleted || !t.AllReturned
                || t.Cleanup.Count!=0 || Array.Exists(t.Calls,x=>x is not null && !x.IsCompleted)
                || (t.Repository?.BorrowedCount??0)!=0 || (t.Authority?.BorrowedCount??0)!=0
                || (t.Clock?.ActiveTimerCount??0)!=0) return false;
            t.Work.Dispose(); slots[index]=null; reserved=checked(reserved-t.Bytes); return true;
        }
    }
}
```

单slot只在前一个Task真结束后复用，迟到/faulted Task不丢。Task.Invoke同步抛出尚未返回Task时，原异常归Primary/cleanup；端口不得在返回Task前产生未受管effect。Create原Task成功后**先**写ticket.Runtime再核取消，Subscribe迟到成功先写Subscription再核取消；body的finally清理，因此观察超时/取消不会丢晚交付实例。`AlarmInitializationException.RollbackComplete=false`即使Task已fault也AllReturned=false，根继续保留工厂/依赖。Primary与Cleanup独立字段，不覆盖。

公共装配最小顺序（两个Host各自运行下段body，输入取§7.1自己的完整配置/授权表，不读对方对象）：

```csharp
static async Task RunHostAsync(HostTicket t,AlarmRuntimeConfiguration c,
    AlarmFactoryOptions o,AlarmDefinition d,ConditionBinding b,AlarmCaller admin,
    AlarmCaller source,AlarmCaller op,ImmutableArray<SyntheticRule> rules,
    Func<HostTicket,ConditionBinding,AlarmCaller,AlarmCaller,Task> scenario) {
    try {
        var clock=new SyntheticClock(c.ScopeId=="synthetic.machine"
            ? DateTimeOffset.Parse("2026-01-01T00:00:00Z")
            : DateTimeOffset.Parse("2026-01-02T00:00:00Z"));
        t.Clock=clock;
        t.Authority=new SyntheticAuthority(rules,clock);
        t.Repository=new SyntheticRepository(c); t.Schedule=new SyntheticSchedule();
        t.Dependencies=new(new SyntheticStoreFactory(t.Repository,t.Schedule),
            t.Authority,clock);
        t.Factory=new AlarmRuntimeFactory(t.Dependencies,o);
        t.Runtime=await t.Keep(HostCall.Create,()=>t.Factory.CreateAsync(c,t.Work.Token));
        t.Work.Token.ThrowIfCancellationRequested(); // 迟到实例已接管
        var reg=await t.Keep(HostCall.Register,()=>t.Runtime.ExecuteAsync(
            new RegisterDefinition(new RequestId(Guid.Parse("00000000-0000-0000-0000-000000000001")),d),
            admin,TimeSpan.FromSeconds(2),t.Work.Token));
        RequireApplied(reg); // 下述确定assert：Recorded、Receipt.Applied、无fault
        var bind=await t.Keep(HostCall.Bind,()=>t.Runtime.ExecuteAsync(
            new BindCondition(new RequestId(Guid.Parse("00000000-0000-0000-0000-000000000002")),b,new(0)),
            admin,TimeSpan.FromSeconds(2),t.Work.Token));
        RequireApplied(bind);
        await scenario(t,b,source,op); // §7.3逐步scenario，所有原call经Keep
    } catch(Exception ex) { t.Primary=ex; }
    finally {
        if(t.Subscription is not null) {
            try { await t.Keep(HostCall.SubscriptionClose,()=>t.Subscription.CloseAsync()); }
            catch(Exception ex) { t.Cleanup.Add(ex); }
            try { await t.Keep(HostCall.SubscriptionDispose,()=>t.Subscription.DisposeAsync().AsTask()); }
            catch(Exception ex) { t.Cleanup.Add(ex); }
        }
        if(t.Runtime is not null) {
            try { await t.Keep(HostCall.Stop,()=>t.Runtime.StopAsync()); }
            catch(Exception ex) { t.Cleanup.Add(ex); }
            try { await t.Keep(HostCall.Dispose,()=>t.Runtime.DisposeAsync().AsTask()); }
            catch(Exception ex) { t.Cleanup.Add(ex); }
            t.AllReturned=t.Cleanup.Count==0 && t.Runtime.GetClosure().ResourcesReleased;
        } else t.AllReturned=t.Cleanup.Count==0 && (t.Primary is null
            || t.Primary is AlarmInitializationException { RollbackComplete:true }
            || t.Calls[(int)HostCall.Create] is null); // 尚未调用Create可归还
    }
}
static void RequireApplied(AlarmWriteResult r) {
    if(r.CommitState!=AlarmCommitState.Recorded || r.Receipt is null
        || r.Receipt.Disposition!=AlarmDisposition.Applied || r.Fault is not null)
        throw new InvalidOperationException("expected recorded/applied");
}
```

根的`Start`和`TryReturn`须在同一实例lock下实现：Start先checked余额、登记ticket，再令ticket.Body=RunHostAsync原Task；TryReturn只有Body.IsCompleted、Calls所有非null均IsCompleted、AllReturned=true、cleanup为空、repository/authority/timer夹具借用计数为0才移槽/扣Bytes。Start同步body返回失败保留Primary，不能把有可能Create的槽直接删。固定数组+最后结果+4cleanup保证根有界，不积累每次轮询Task无限列表。尚未完成Task绝不复用slot。

外层**10/120/180**：每次UI/CLI观察原Body用`await Body.WaitAsync(TimeSpan.FromSeconds(10), observerCt)`，Timeout/observer取消只返回Pending和原Key，不Dispose根；Work的120s只合作取消业务。清理不借用Work取消token，无自动放弃。watchdog 180s是Smoke进程外上限，只判未完成/非零，不声称Released；强制进程退出仅终止旧实例，耐久Unknown仍需新受管只读回查。正常恢复在同root查原ticket、再次有限观察原Body/Calls，不再调用Factory/Create/Commit/Stop/Dispose。后台body继续接管迟到Create/订阅并清理；只有原根TryReturn通过才能释放caller依赖或建同Scope替代Runtime。不得写 `using root` 后在Timeout离栈释放它。

### 7.3 两个scenario的完整调用对象/顺序

每次观测构造：`new ConditionObservation(binding.Definition,binding.Key.Source,1,seq,kind,value,currentity,quality,clock.GetUtcNow(),covers,null)`；clock从首次UTC起每步Advance1s。identity在发原Task前用`AlarmCore.ComputeIdentity(c.ScopeId,new ObservationInput(obs),source.PrincipalId,c.Limits.MaxRequestBytes,null)`保存t.LastIdentity；经t.Keep(Work,()=>Runtime.ObserveAsync(...2s,Work.Token))保存原result。Query结果require Value非null/Fault=null，用最新OccurrenceTarget(Id,Occurrence.Revision)，不硬猜修订。

Machine：seq1 authoritative Inactive/Covers0 → seq2 Sample Active → **原obs对象**重复seq2（不新取ObservedAt）=IsReplay/原Receipt → seq3 Inactive清除但未确认 → QueryCurrent(IncludeClearedUnacknowledged=true,IncludeSuppressed=true,PageSize64,null) → requestId …003 Acknowledge该唯一target Comment=`seen` → seq4 Active新ID → seq5 Heartbeat Unknown/Disconnected，不清活动 → seq6 authoritative Active/Covers5重新当前 → maint request…004 SetVisibility condition Expected0 Shelved Duration5min Reason=`maintenance` → 时钟前进5min，维护tick原Task被根持有，Query确认Effective=false，VisibilityFact Expired一次 → source seq7 Sample Inactive清除 → seq8 Sample Active新未确认（抑制已过期） → operator/第二站各固定request…005/…006相同TargetExpected，两个Task分别另占固定Work/Query槽，断言只有一个Applied、另一Rejected TargetRevisionConflict，原Actor不覆盖 → finally Stop+Dispose。第二站Caller同operator规则授权，不改Scope。

MES：seq1 authoritative Active/Covers0 → seq3 Sample Inactive → seq2 Sample Inactive（迟到，OutOfOrder且无真值变化）→ seq4 authoritative Active/Covers3 → seq5 Sample Inactive → request…003 Acknowledge current target前Schedule设CommitRecordedResponseLost：Commit原Task返回Unknown但实际Receipt Recorded → QueryReceipt原identity断言Recorded/同target，不第二次Execute → OpenSubscription(After=(当前AsOf,uint.MaxValue),Capacity64)并先保存返回Subscription → 制造65条有序新observation（seq6..70，交替值、LastObservedAt各Advance1s）且不Read，事件worker推进，Read新的Grant后必Gap/不静默全交付 → Close/Dispose原subscription保存原Tasks → 当前查询捕获AsOf后重新Open，撤权规则、Read得到AuthorizationDenied且无payload。冷重启单独case：先Stop+Dispose旧ticket真Released，再沿同Repository开新Boot=boot-i2且不同RuntimeId，入口依然新根槽；Source Unknown、原Active/确认不伪变，截断夹具只读RecoveryUncertain；不把未知旧writer视为已死重启。

两个Host每个完整scenario可独立运行，注入阻塞/失败在同一表再执行，不伪称这些片段已编译。事件由Store.ReadEvents与Runtime worker产生。软件额度/时钟值只用于确定性和拒绝路径，不是客户性能/设备安全指标。

## 8. 固定Oracle与反例

### 8.1 pre-state顺序与双实例完整oracle

本表给出独立source的第一条观察前 `CurrentEpoch=0,Highest=0,Applied=0,RequiresSnapshot=true,CurrentOccurrence=null`（新Bind只登记绑定，不伪创建发生）。定义/绑定已经存在；StoreRevision基数记R，以下每个新观察写一次回执使StoreRevision递增，重复不递增；SourceRevision新建为1，以后每条实际更新+1，拒绝迟到仅写ledger不改SourceRevision。Occurrence新建处理Revision=1，source同值/gap/失效不改处理Revision；清除/确认/备注/OwnerAction使其+1。

| 输入（每条epoch=1，所有当前快照Covers>=seq-1） | 比较前highest | 提交后highest/applied | 开放gap/历史完整性 | 发生/确认/回执 |
|---|---|---|---|---|
| seq1权威Active,Covers0 | 0 | 1/1 | 无gap、RequiresSnapshot=false、HistoryComplete=true | 新O1 Active/Unacknowledged，OccurrenceRevision1，Raised一次，Store R+1 |
| seq3普通Inactive | 1 | 3/1 | MissingRange[2,2]，gap包络[2,2]、HistoryComplete=false | O1仍Active，Source Unknown，SequenceGap拒绝回执已耐久，Store R+2 |
| seq2普通Inactive迟到 | 3 | 3/1 | [2,2]保持；此迟到不填gap | OutOfOrder，O1不变、SourceRevision不变，Store R+3 |
| seq4权威Active,Covers3 | **3，先核4>3** | 4/4 | 同事务闭合[2,2]，gap null、RequiresSnapshot=false；HistoryComplete仍false | 同O1 Active/Unacknowledged，不再Raised；Resynchronized/Source Current，Store R+4 |
| 同seq4原对象重放 | 4 | 4/4 | 不变 | 原Receipt/IsReplay，Store仍R+4；若重取UTC变payload则IdentityConflict |
| seq5普通Inactive | 4 | 5/5 | 无gap、历史不完整标记保留 | O1 Cleared/Unacknowledged，OccurrenceRevision2、ClearBasis=Sample，Store R+5 |

首次权威seq42独立流：preHighest0→先算新增Missing[1,41]→核快照42>0且Covers41→同一事务**打开历史缺失并闭合当前gap**；postHighest=42/applied=42/Currentity=Current/RequiresSnapshot=false/IsGapOpen=false/HistoryComplete=false，新O42的ActivationEvidence=AfterHistoryGap，Occurred Observed只是输入时间；Occurred ID按67byte向量而非guess missing41次。Facts顺序ObservationFact→RaisedFact→SourceFact→GapFact打开Missing[1,41]（SequenceMissing）→GapFact闭合该范围（Resynchronized），丢历史保留，不显示当前序列已完整。首次seq42普通Sample则MissingSnapshot+gap[1,41]，不创建O42；随后seq43权威Covers42合法，才以seq43创建新发生。

新epoch规则反例：已有epoch1 O1 Active，epoch2 seq1普通Inactive→high=1/applied=0/RequiresSnapshot=true，不清O1；epoch2 seq2权威Active/Covers1→核2>preHigh1、恢复Current，同O1（RaisedEpoch/Sequence/ID不变）；随后epoch1任何迟到Inactive EpochStale，不清O1。epoch2权威Inactive才以SnapshotReconciliation清旧O1。重启**同epoch**preHigh4仍4，新的权威seq5可恢复，seq1不能因重启重放。

双实例：同DefinitionKey/SourceId、InstanceId=oven-01/oven-02均epoch1/seq42权威Active，各自ConditionKey和obs identity不同（§5.5两个70byte完整预像），独立两条Active/Unacknowledged且无相互冲突。oven-01同epoch/seq改Value/ObservedAt必IdentityConflict，不能影响oven-02。维护target完整DefinitionKey/SourceId/**InstanceId**/ExpectedRevision，旧instance到期/确认不作用于新instance。

### 正常

| ID | 场景 | 必须断言 |
|---|---|---|
| O-01 | 首次权威/连续Active | 一条RaisedFact，IsActive=true，AckState按政策，revision+1。 |
| O-02 | 同序列同hash | 原ObservationReceipt/ledger，发生数、revision、事件数不增加。 |
| O-03 | 有效Inactive | 同occurrence IsActive=false，未确认仍保留，ClearBasis明确。 |
| O-04 | 清除后再Active | 新OccurrenceId，旧Ack/历史不变。 |
| O-05 | 单/批确认 | 精确targets、全权限、CAS后只改Ack；新增occurrence不入旧batch。 |
| O-06 | 搁置到期 | Expired一次、活动/未确认/计数仍真；Store失败显式Pending。 |
| O-07 | 重启恢复 | 来源Unknown；已证实确认保留，确认证据不完整则该条AckEvidenceUncertain，不能伪成功。 |
| O-08 | 原回执查询 | Commit响应丢失只读原identity回执；不产生第二fact。 |
| O-09 | CAS并发 | 两站同Expected一胜；另一方冲突/重读后明确NoChange，不覆盖原Actor。 |
| O-10 | 真实关闭 | Stop只StoreClosed=true、ResourcesReleased=false；Dispose原Task完成且StoreDisposed=true、全部借用已归还才ResourcesReleased=true。 |

### 反例

| ID | 禁止 | 必须结果 |
|---|---|---|
| N-01 | Disconnected/Unknown/坏质量Inactive | SourceFact，活动不清。 |
| N-02 | 高epoch普通Inactive | MissingSnapshot，旧活动不清。 |
| N-03 | 序列跳号后越过gap | MissingRange/GapFact；不应用真值。 |
| N-04 | 同序列异payload/低序列迟到 | IdentityConflict/OutOfOrder，不覆盖。 |
| N-05 | 已确认重复/RequestId换payload | NoChange原receipt/IdentityConflict。 |
| N-06 | 批量期间加入新行 | 新行未确认，旧ObjectSetHash不变。 |
| N-07 | Store失败后内存先成功 | StoreUnavailable/Unknown，不能发布成功事件。 |
| N-08 | 慢订阅无限排队/静默丢 | 有界Gap；查snapshot、关闭旧订阅、从新cursor重建。 |
| N-09 | ERROR诊断、确认按钮触发设备 | 无报警转换；只记确认/Owner回执，不发动作。 |
| N-10 | 重启猜确认/清Active | RecoveryUncertain或Source Unknown；不伪确认/恢复。 |
| N-11 | 到期由UI查询或timer暗写 | 只有Runtime维护task写一次Expired；到期事实失败也不继续隐藏。 |
| N-12 | 回查Unknown换新ID重跑 | 原identity只读回查/保留Unknown，禁止重复副作用。 |
| N-13 | 关闭超时直接Success | Closure未释放/Unknown；原Task继续被根持有。 |
| N-14 | 风暴按ObservedAt乱序或重复轮询计数 | 接收单调固定桶；仅耐久RaisedFact加一次。 |

## 9. AL-W1 WPF/DevExpress装配与PageContract

### 9.1 公开Factory/Session/有界Owner

namespace `Asun.Modules.Alarms.Wpf`；net10.0-windows、UseWPF=true、Core、本机DevExpress25.2.3的Core/Grid/CoreGrid/Docking程序集直接Reference。Core不引用WPF。控件只消费Core Query/Command/Subscription；借用宿主Runtime，不隐藏创建Runtime。宿主保持主题和语言入口；控件内部不改Application.Current、Thread.CurrentCulture、主题或屏幕设置。下面声明引用System.Windows.FrameworkElement、System.Windows.Threading.Dispatcher；单个session独占一棵View、一个dispatcher、一个subscription，不跨STA共享DependencyObject。

```csharp
public sealed record AlarmViewOptions(int PageSize,int SubscriptionCapacity,
    int MaxSelectedTargets,int MaxPendingDispatcherOperations,long MaxProjectionBytes,
    TimeSpan ExecutionBudget,TimeSpan RefreshCoalesceInterval);
public enum AlarmViewMode { Workbench, SummaryStrip }
public sealed record AlarmViewConfiguration(string ViewId,string ScopeId,string Culture,
    AlarmViewMode Mode=AlarmViewMode.Workbench);
public sealed record AlarmWorkbenchOpenRequest(string ScopeId,Revision AsOfRevision);
public sealed record AlarmViewCallerContext(AlarmCaller Caller,string ScopeId,
    ImmutableArray<AlarmPermission> PreviewPermissions,ulong PermissionGeneration);
public interface IAlarmCallerSource {
    AlarmViewCallerContext GetCurrentContext(); // 同步线程安全/有界；权限仅预览，不授Grant
}
public interface IAlarmTextCatalog {
    ImmutableArray<string> Cultures { get; }
    string GetText(string culture,string key,ImmutableArray<string> arguments);
}
public sealed record AlarmViewClosure(bool Detached,bool ResourcesReleased,int RunningCommands,
    int PendingDispatcherOperations,bool SubscriptionReleased,AlarmFault? Fault);
public interface IAlarmViewSession:IAsyncDisposable {
    event EventHandler<AlarmWorkbenchOpenRequest>? WorkbenchRequested;
    FrameworkElement View { get; } // 仅所属Dispatcher访问
    Task RefreshAsync(CancellationToken ct);
    Task ChangeLanguageAsync(string culture,CancellationToken ct);
    Task DetachAsync();
    AlarmViewClosure GetClosure(); // 线程安全，Dispose后仍可读最终缓存
}
public sealed class AlarmViewFactory {
    public AlarmViewFactory(IAlarmTextCatalog texts,AlarmViewOptions options,TimeProvider clock);
    public Task<IAlarmViewSession> CreateAsync(AlarmViewConfiguration configuration,
        IAlarmRuntime borrowedRuntime,IAlarmCallerSource callerSource,
        Dispatcher dispatcher,CancellationToken ct);
}
public sealed class AlarmViewTicket {
    public string ViewId { get; }
    public Task<IAlarmViewSession> Creation { get; }
    public Task Completion { get; } // 一次Detach+Dispose，真释放才完成
    public IAlarmViewSession? Session { get; }
    public Exception? PrimaryFailure { get; }
    public ImmutableArray<Exception> CleanupFailures { get; }
}
public sealed class AlarmViewHostOwner {
    public AlarmViewHostOwner(int maxViews,long maxReservedBytes);
    public AlarmViewTicket Attach(AlarmViewFactory factory,AlarmViewConfiguration configuration,
        IAlarmRuntime borrowedRuntime,IAlarmCallerSource callerSource,Dispatcher dispatcher,
        long reservedBytes,CancellationToken workCancellation);
    public Task DetachAsync(string viewId);
    public AlarmViewTicket? Find(string viewId);
    public bool TryReturn(string viewId);
}
```

ViewId/ScopeId同Key1..64。options固定首版PageSize128（有效1..256）、SubscriptionCapacity64（1..4096）、MaxSelectedTargets128（1..128）、MaxPendingDispatcherOperations2（1..8）、MaxProjectionBytes8MiB（正且足以预约所选页）、ExecutionBudget2s（1ms..Runtime.MaxExecutionBudget）、RefreshCoalesceInterval100ms（50..1000ms）。UI只保当前页/历史页各最多PageSize、预览最多128、当前失效源/Gap各最多PageSize；全部DTO、文本、选择快照、原Command和dispatcher操作计入MaxProjectionBytes，超限保留上个已证实投影并显示CapacityExceeded，不截断假称完整。

Host先new Owner(2,128MiB)并强持，再构造被动Factory。Attach与Detach共实例lock：先预约exact ViewId槽/64MiB，保存caller/runtime/dispatcher/factory/原CreateTask；同ViewId+同配置/引用返回原ticket，不新Create，异对象冲突；满额零Core/Dispatcher调用。取消Create仍先接管迟到Session，Create失败只在部分订阅/dispatcher原操作真归还后异常，异常带AlarmInitializationException.RollbackComplete。Detach未调用时Completion为未完成闩锁，不等于Creation完成；首次Detach设置原Completion任务且以后复用。Find仅观察原ticket。TryReturn只在Creation和Completion真结束、Session.GetClosure.ResourcesReleased、无cleanup未知、所有原Task完成时移槽；创建失败RollbackComplete=true允许无Session归还。Owner不Dispose borrowedRuntime/dispatcher，不因观察超时丢ticket。

Create先校验全部参数/三语资源→在所属Dispatcher.InvokeAsync(Action,DispatcherPriority.Normal,ct)构造View/VM并保存原DispatcherOperation.Task→调用Core.QueryCurrent→获取稳定AsOf/完整页→OpenSubscription(after=(AsOf,uint.MaxValue),capacity64)，迟到成功先保存再核取消→在原dispatcher发布页面→交付Session。首次查询和订阅之间缺口由持久事件cursor保证，不能只凭时间戳略过。Dispatcher已Shutdown拒初始化；任何失败关闭/Dispose已创建subscription、等所有原Core/dispatcher任务结束并解除UI事件后再异常。Factory没有async void、隐藏窗口、全局服务定位或静态集合。

### 9.2 固定控件、紧凑布局与模板

只在1920×1080验证viewport，宿主按实际任务栏/边框/标题/状态栏扣除可用客户区；默认停靠控件最小有效内容1440×760，嵌入紧凑面板最小960×640。两种宿主窗口在同一固定viewport内，非另一分辨率矩阵；低于模块最小宽度显示明确展开面板提示，命令区域换行而不消失。平台设备主页面影像优先：报警摘要可置高度40的Strip，完整报警工作台由操作者显式打开，不用报警表永久挤占影像主区。

View正文Grid行高40/40/*/28，边距12、区域gap8、字体14（主状态16半粗）、表行32、命令高32；顶行活动/未确认/来源失效/gap和数据截至时刻，第二行独立命令工具条和搜索；左宽*主列表，右380详情，底部历史Tabbed区域默认收起/选择历史时展开。Dock panel AllowClose=false保证关键区域可恢复可见；用户可调整详情宽度，默认最小320。不重复TreeList或第三份事实表。颜色用宿主主题动态brush：严重状态红/警示琥珀/当前正常中性，均配短文案+形状图标；图标由模块已有矢量geometry、没有位图生成依赖；等待只用局部细进度，不闪屏/鸣笛。

`AlarmViewMode.SummaryStrip`只呈现高度40的活动/未确认/来源未知/gap/截至revision摘要和“打开报警工作台”命令；不显示可确认/抑制等写命令，不保存第二份事实。该命令触发`WorkbenchRequested`，携带Scope与当前AsOfRevision，由宿主在同一Runtime/Caller下创建或显示`Workbench` session；宿主未提供工作台时命令明确显示“工作台不可用”，不能把摘要条升级为隐藏的确认入口。`Workbench`才使用下方Grid/Details/History结构。摘要条和工作台均遵循同一三语资源、权限和来源Unknown/gap文案。

以下为待实现的实际XAML结构，x:Class `Asun.Modules.Alarms.Wpf.AlarmView`；WPF resource key在每Session.View.Resources填充，不写全局ResourceDictionary。原控件API已查本机25.2.3 XML：GridControl.View、DataControlBase.ItemsSource/CurrentItem/SelectedItems/SelectionMode、BaseColumn.Width/Header、ColumnBase.FieldName、TableView.RowMinHeight/AutoWidth、GridViewBase.ShowGroupPanel、DataViewBase.AllowEditing；DockLayoutManager/LayoutGroup/LayoutPanel/TabbedGroup、BaseLayoutItem.ItemWidth/AllowClose；ToolBarControl/BarItem.Command/Content/SuperTip。SuperTip直接挂BarButtonItem.SuperTip，不猜未查到的SuperTipService。

```xml
<UserControl x:Class="Asun.Modules.Alarms.Wpf.AlarmView"
 xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
 xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
 xmlns:dx="http://schemas.devexpress.com/winfx/2008/xaml/core"
 xmlns:dxb="http://schemas.devexpress.com/winfx/2008/xaml/bars"
 xmlns:dxg="http://schemas.devexpress.com/winfx/2008/xaml/grid"
 xmlns:dxd="http://schemas.devexpress.com/winfx/2008/xaml/docking">
 <Grid Margin="12">
  <Grid.RowDefinitions><RowDefinition Height="40"/><RowDefinition Height="40"/>
   <RowDefinition Height="*"/><RowDefinition Height="28"/></Grid.RowDefinitions>
  <TextBlock Text="{Binding SummaryText}" FontSize="16" FontWeight="SemiBold"
   AutomationProperties.AutomationId="Alarms.Summary"/>
  <dxb:ToolBarControl Grid.Row="1">
   <dxb:BarButtonItem Content="{DynamicResource Alarms.Command.Acknowledge}"
    Command="{Binding PreviewAcknowledgeCommand}">
    <dxb:BarButtonItem.SuperTip><dx:SuperTip><dx:SuperTipItem
     Content="{DynamicResource Alarms.Tip.Acknowledge}"/></dx:SuperTip></dxb:BarButtonItem.SuperTip>
   </dxb:BarButtonItem>
   <dxb:BarButtonItem Content="{DynamicResource Alarms.Command.Comment}" Command="{Binding CommentCommand}"/>
   <dxb:BarButtonItem Content="{DynamicResource Alarms.Command.Shelve}" Command="{Binding ShelveCommand}"/>
   <dxb:BarButtonItem Content="{DynamicResource Alarms.Command.Suppress}" Command="{Binding SuppressCommand}"/>
   <dxb:BarButtonItem Content="{DynamicResource Alarms.Command.Unsuppress}" Command="{Binding UnsuppressCommand}"/>
   <dxb:BarButtonItem Content="{DynamicResource Alarms.Command.Refresh}" Command="{Binding RefreshCommand}"/>
  </dxb:ToolBarControl>
  <dxd:DockLayoutManager Grid.Row="2">
   <dxd:LayoutGroup Orientation="Horizontal">
    <dxd:TabbedGroup>
     <dxd:LayoutPanel Caption="{DynamicResource Alarms.Page.Current}" AllowClose="False">
      <dxg:GridControl ItemsSource="{Binding CurrentRows}" CurrentItem="{Binding CurrentRow,Mode=TwoWay}"
       SelectedItems="{Binding SelectedRows}" SelectionMode="Row" AutomationProperties.AutomationId="Alarms.Current">
       <dxg:GridControl.Columns>
        <dxg:GridColumn FieldName="StateText" Header="{DynamicResource Alarms.Column.State}" Width="120"/>
        <dxg:GridColumn FieldName="TitleText" Header="{DynamicResource Alarms.Column.Alarm}" Width="240"/>
        <dxg:GridColumn FieldName="SourceText" Header="{DynamicResource Alarms.Column.Source}" Width="170"/>
        <dxg:GridColumn FieldName="RaisedText" Header="{DynamicResource Alarms.Column.Raised}" Width="180"/>
        <dxg:GridColumn FieldName="AckText" Header="{DynamicResource Alarms.Column.Ack}" Width="120"/>
       </dxg:GridControl.Columns>
       <dxg:GridControl.View><dxg:TableView AllowEditing="False" AutoWidth="True"
        RowMinHeight="32" ShowGroupPanel="False"/></dxg:GridControl.View>
      </dxg:GridControl>
     </dxd:LayoutPanel>
     <dxd:LayoutPanel Caption="{DynamicResource Alarms.Page.History}" AllowClose="False">
      <ContentControl Content="{Binding HistoryContent}"/>
     </dxd:LayoutPanel>
    </dxd:TabbedGroup>
    <dxd:LayoutPanel Caption="{DynamicResource Alarms.Page.Details}" ItemWidth="380" AllowClose="False">
     <ContentControl Content="{Binding DetailsContent}"/>
    </dxd:LayoutPanel>
   </dxd:LayoutGroup>
  </dxd:DockLayoutManager>
  <TextBlock Grid.Row="3" Text="{Binding StatusText}" TextWrapping="Wrap"
   AutomationProperties.AutomationId="Alarms.Status"/>
 </Grid>
</UserControl>
```

VM内部类型不是公共合同：CurrentRows/HistoryRows为有界ObservableCollection，row key始终OccurrenceId或AlarmCursor；CurrentRow和SelectedRows在同Dispatcher处理。HistoryContent为同GridControl只读TableView，列固定时间180/事件160/报警220/来源170/操作者140，绑定有限HistoryRows，含独立缺口提示与首页/下一页/From/To输入。DetailsContent为ScrollViewer+纵向Grid，依次定义标题/恢复说明、OccurrenceId/版本、活动/确认/当前性/质量、epoch/highest/applied、缺口、观察/接收/清除/确认时刻、Visibility/到期、证据引用、Owner动作原回执；自动化Id均`Alarms.Detail.<字段>`，来源未知文字常驻。批量预览用本控件内右侧可焦点panel（不新隐藏Window），最多128条Grid和Comment输入+明确“确认所选”/“返回”。详情/历史/预览都使用同Per-session资源和图标，不把ContentControl留为不可用placeholder。

### 9.3 授权、命令、语言和键盘

公开命令由内部同步ICommand开启**已保存原Task**的执行器；Command.Execute本身不async void，重入拒绝且反馈忙状态。工具条CanExecute取callerSource.GetCurrentContext的最新PreviewPermissions、对象shape及Core健康，PreviewPermissions只能让按钮可尝试，不授实际操作权；actual Core Execute每次重新核权。Context.ScopeId必须配置一致、PermissionGeneration正且变化使旧预览失效；未取得/撤权时禁用写并显示原因，清理不需要读权。不能仅按角色名/Severity硬编码。

确认：选择≤128行→拷贝exact Id/Revision→预览展示固定数量、活动/已清除状态和备注→确认时生成一次RequestId/对象集→Execute Acknowledge→Recorded回执更新/重查；新发生不加入旧预览。RevisionConflict保留旧预览、标具体冲突行并要求显式重查/重新选择，不自动确认新发生。批量Disabled/超长评论提前显示错误；服务器仍是最终校验。备注/AddComment、搁置/维护抑制及撤销分别独立权限/理由/期限/CAS；有效性到期只更新显示，不由WPF写Expired。Unknown保留原Command/Identity/Task，只QueryReceipt；不重生成RequestId、不把忙/取消当失败后重发。按钮等待状态显示“保存中”“结果待核实”“关闭中”，不说成功直到原Receipt已证实。

WPF只显示Reset/Retry/Continue的OwnerAction原回执，提示“设备操作请到机台页面”；设备动作按钮和设备Owner权限由原机台页面负责，本W1无设备调用口。这落实§1不执行动作的边界，不凭UI点击写OwnerAction.Succeeded。记录外部动作仍由已获RecordOwnerAction权限的来源调用Core，页面读取已证实事实。

三语完整键集由同一key表维护：Page/Column/Command/Tip/State/Permission/Validation/Recovery、所有AlarmFaultCode及参数、Definition.Title/Description/RecoveryKey。宿主IAlarmTextCatalog对已登记key返回非空，缺键初始化InvalidInput；动态Definition key缺资源以Definition.Id显示、给“说明未提供”，不显示raw exception或内部AI文字。数字/日期CultureInfo指定Culture；身份/hash固定ordinal不翻译。ChangeLanguage在原Dispatcher一次替换View.Resources并重投影有限row/details/tooltip/validation，保持选择/焦点/原Task，不影响生产事实；catalog.Cultures必须含zh-CN/zh-TW/en-US、default/重复/非法culture拒；culture只支持catalog已登记项，扩展由hostcatalog显式登记资源，不做简繁字符自动转换。

| key后缀 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Command.Acknowledge / Command.Comment | 确认 / 备注 | 確認 / 備註 | Acknowledge / Comment |
| Command.Shelve / Command.Suppress / Command.Unsuppress | 搁置 / 维护抑制 / 取消隐藏 | 擱置 / 維護抑制 / 取消隱藏 | Shelve / Suppress / Restore visibility |
| State.Active / State.Cleared / State.Unacknowledged | 活动 / 已清除 / 未确认 | 活動 / 已清除 / 未確認 | Active / Cleared / Unacknowledged |
| Recovery.SnapshotChanged | 数据已变化，请重新查询 | 資料已變更，請重新查詢 | Data changed. Refresh the list. |
| Recovery.Unknown | 结果待核实，请查询原回执 | 結果待核實，請查詢原回執 | Result unknown. Check the original receipt. |
| Tip.Acknowledge | 只确认所选报警，不清除故障。Ctrl+Enter打开预览 | 只確認所選警報，不清除故障。Ctrl+Enter開啟預覽 | Acknowledges selected alarms. The fault stays active. Ctrl+Enter opens preview. |

表是具体术语基线，资源须覆盖上述完整键集而非只实现表中几句；字段值来自typed事实，不拼英文enum。Tab按筛选→当前列表→详情→命令→预览→状态；Enter列表打开详情，Ctrl+Enter只开确认预览、预览内另显式确认；Esc退出预览/返回不取消已提交动作，F5显式刷新，Space选择行。Grid虚拟化不回收稳定Id的语义；模板/AutomationPeer暴露`Alarms.Row.<OccurrenceId>`及State/Ack/Currentity/Gap/CommandState，BarItem生成实际按钮peer的AutomationId由宿主适配后验证，不以给非UI BarItem贴属性冒称UIA成功。读屏状态文字和文本图标同时存在，tooltip不是错误唯一出口。

### 9.4 刷新、Dispatcher原Task、Detach与有限恢复

每session一个串行pump：Read订阅(maxEvents64,当前Caller,2s,token)→只标投影Dirty→100ms合并最多一次Query；上一Query/Read/Dispatcher操作未真结束不重入。Core页与事件只作投影：Current/History续页SnapshotChanged清旧continuation并提示显式首页重查，不混跨版本页；Gap保留常驻、Close/Dispose旧sub后QueryCurrent再从AsOf显式新Open，使用新Caller授权。撤权Read无payload、清理缓存/遮住旧详情，显示无权；再次获得权限后操作者Refresh才新Open，不能轮询权限绕过。最新身份Principal改变必须关闭旧sub，不能用另一人读同连接。

发布通过已保存原DispatcherOperation.Task；操作入口检查generation/Detached和ct，旧epoch迟到投影不写入View，但原Task仍观察到结束。记录最多2个原dispatcher操作（发布/语言或Detach），额度满合并Dirty不追加队列。Grid更新BeginDataUpdate→按Id diff→EndDataUpdate在finally，不一口Reset ItemsSource夺焦点；原选行仍存在则保留，同Id revision变动使旧预览失效；消失则显示“所选报警已更新”且不自动焦点到下一条后允许确认。View事件处理只调用有界执行器，不递归刷新。

Detach原子关命令接纳/投影epoch→取消Read/timer等待→等待原Command/Query/Open/Read（工作ct仅合作取消）→sub.Close/Dispose→pump真退出→同Dispatcher解绑事件/ItemsSource/VM→所有原DispatcherOperation.Task结束→Detached/SubscriptionReleased/ResourcesReleased缓存。Dispose复用唯一DetachTask。**不Stop/Dispose borrowedRuntime，不Shutdown宿主Dispatcher**。原Stop/Command尚未完成时控件Owner保持引用；若用户关Window，Window.Closing第一次e.Cancel=true并请求Detach，只有真Released后用原Dispatcher允许最终Close。宿主必须保Dispatcher消息循环直至全部view释放，禁止先Shutdown造成无人清理。

有限观察每次10s WaitAsync(ticket.Creation/Completion,observerCt)，超时返回原ViewId/“关闭仍在进行”，不Dispose Owner/Runtime/重建View。work120s合作取消，清理无取消，Smoke180s外层watchdog非零。Dispatcher shutdown/Invoke Task fault与Core commit结论分轴；Primary/cleanup分别保存。已Known提交仍可显示最后Receipt，而释放未知不返Owner槽；恢复从Find同ticket再观察原任务，取消/超时不产生第二Create/Detach。需要替换Dispatcher只在旧实例真Released或旧进程已终止后由宿主新受管实例完成；耐久Unknown仍原identity只读回查。

### 9.5 双STA宿主和反例断言

Machine主Window宿主与独立Maintenance/MES Window宿主各自new Thread→SetApartmentState(STA)→在线程上Dispatcher.CurrentDispatcher→Dispatcher.Run；入口先根Owner预约再Factory.Create，thread.Start原thread由外层有限Owner强持。两STA使用各自Runtime/Caller/TextCatalog/View资源，不共享DependencyObject/ObservableCollection，且在同1920×1080验证viewport中依次置顶验证。不在两STA创建多个WPF Application实例。Host①取§7 machine Runtime显示活动/未确认/gap、预览确认、注入commit Unknown原回查；Host②取mes Runtime显示多gap历史、三语切换/过滤/权限撤销。每个创建顺序Owner→被动Factory→Attach→await原Creation→Window.Content=session.View；关闭依§9.4→TryReturn→宿主alarm Stop/Dispose→最后Dispatcher.InvokeShutdown并Join原thread（有限观察，未结束非零）。Runtime归该Host，Session只借用。测试可用Core Runtime+SyntheticRepository，不能把假Runtime/HTML截图代替真实WPF。

| ID | 可判定断言 |
|---|---|
| W-01 | 两STA、两View、独立CurrentItem/选择/语言资源；切换不改变Receipt/Occurrence/Scope；借用Runtime Stop/Dispose计数0 |
| W-02 | 固定viewport扣除宿主chrome，简/繁/英无关键按钮截断；1440/960模块空间按指定换行；图像主区与展开工作台分离；UIA键盘完成预览/确认/返回 |
| W-03 | 预览后新发生/旧Revision变化不入旧Targets；整批CAS失败不假确认；F5/Selection不写Fact；设备动作只展示原Owner回执 |
| W-04 | 慢订阅Gap→新AsOf重建；两页head变动SnapshotChanged；同From多gap全键不漏；页面不静默把Unknown当Cleared |
| W-05 | Dispatcher发布阻塞且Close：原Command已Recorded但Detached=false/slot不返；解除消息闩锁后sub/操作真归还，Detach完成；超时重复观察Create/Detach调用数1 |
| W-06 | 权限撤销零payload/遮蔽敏感旧投影，重新获权显式Refresh；语言切换/布局损坏不修改Fact；初始化迟到Subscription由原Owner清理 |

布局可选保存只用已核SaveLayoutToStream/RestoreLayoutFromStream，由host提供可信、按user/scope/view/version隔离的≤64KiB原bytes；不接受报警查询中带布局、不将用户自由XML喂Restore。未知/损坏回退本节默认且提示，恢复失败不影响事实。真实WPF编译、自动化peer、主题细节、语言长度、当前OS DPI、窗口chrome与退出验证尚未执行，W1整体PreparationIncomplete；软件构造/Owner/刷新/恢复是本页确定设计，不列为客户外门。

## 10. 测试、性能、发布和外部资格

Core唯一Smoke为Microsoft.NET.Sdk/net10.0/OutputType Exe，只引Core+BCL，固定§7 SyntheticClock/闩锁，命令：

```text
dotnet build src/Modules/alarms/Asun.Modules.Alarms.Core/Asun.Modules.Alarms.Core.csproj -c Release
dotnet run --project tests/Modules/alarms/Asun.Modules.Alarms.Core.Smoke/Asun.Modules.Alarms.Core.Smoke.csproj -c Release
```

测试组：Contract（域/codec/向量/版本）；Lifecycle（O-01..O-10与Active/Cleared×Ack）；Ordering（epoch/gap/乱序/重复/坏质量/重启）；Concurrency（CAS、同/异Request、订阅单读、Stop）；Persistence（Store故障/Unknown/回查/截断）；Commands（权限/批量固定集/期限/Owner回执）；Events（cursor/gap/慢订阅/查询恢复）；Resources（取消/超时/原Task/双轴释放）。任一失败、跳过、超时或ResourcesReleased未知非零。测试不冒充真实后端、WPF、设备安全、客户Golden或现场资格。

BenchmarkProfile `ALM-CORE-01/1.0`：记录输入Contract/codec hash、scope/host、冷/热、并发、facts/events、Store延迟、队列/订阅峰值、managed heap/线程、commit和ResourcesReleased。端到端起点为接纳，终点为提交、事件发布和资源释放；另测取消到真实排空。完整样本按DEV-GOV-010 nearest-rank `Q(p)=sorted[ceil(p*n)-1]`给P50/P95/P99；失败/timeout/Unknown/排空未知单列，不筛成功样本。软件拒绝额度：request1MiB、fact/commit有限、订阅4096、批确认128、页256、活动/ledger由Host固定；客户报警频率、存储保留、P50/P95/P99、过载设备反应待两个消费者Profile采纳，当前NotEvaluated。

发布只包含Core contract/codec；Storage/WPF/Owner适配分包，包带Contract/codec版本、Source commit/hash、依赖和迁移/回退说明。新版本先隔离副本hash校验/预览，显式切换；旧回退不丢新事实。AL-S1真实PG接入须将本页报警Owner binding/Schema/codec/固定catalog部署到IM066并取得RLS/迁移/Unknown回查证据；AL-W1须真实DevExpress/WPF/1920×1080/三语/UIA/退出证据；设备、MES、客户、HIL、现场安全和质量放行是外部门，不阻断无关Core。

## 11. 来源与两轮怀疑式自审

来源固定且已实际读取：PKG-059报警专项（发生/确认/清除/再发生/抑制/历史/双消费者）；SM-005诊断（日志、指标、健康，不能接管报警）；OPC Part9§5.7 v1.05.06，本地摘录SHA256 `d550b709cdefefb86ebbc30dfc663ace434527492643b5ea2fb62c4465ebcb86`；OPC固定commit `46fa7d364a0bc44b71a78bbe3cc415edda4a46bd` 的固定文件及SHA：`AlarmRateTracker.cs`=`a68e0062273a29b63bd218b42e4f75e2decfff856dce22135e246bd230acd0cd`，`AlarmRateTrackerTests.cs`=`de68cff6ac7cf76166ecb407749554990e5b9d96463b686a1026f3217f441df0`，`ConditionStateTests.cs`=`09fd0dfb87d64d20b2086e5247d9caf6276a49d9a6d4453c11a45f1cdf113547`，`Opc.Ua.Server.csproj`=`f8db3181509958bdd2a1b37317ad486f2d5a3d153a4f832f9fec738c6799d586`，`Directory.Packages.props`=`bf8b7dfbcd8e119a161b968b49e09f57e2d84a745338b609ea7bd42ed46141a5`，`LICENSE.txt`=`7ef7a25dbc6464d4a40f7a2c6c35ca78f485f9c52cadcad47da8289cce6970a5`。借鉴：Acked/Confirmed分离、针对特定事件身份、重启不确定时不得假确认、注入时钟和分开计数。限制：源码计数器无上限、假设时间有序、未拒绝非正窗口、测试Sleep且未在本环境构建/运行；本页采用有界固定桶/受控时钟/gap测试，不引完整网络栈或复制OPC DTO/类型。

第一轮按场景链逐项走：输入→授权→lookup→快照→Plan→CAS→Receipt→Event→Query/UI→重启/恢复；覆盖Active/Cleared与Ack、再发生、多个清除未确认、断连/epoch/gap/乱序、批量CAS、到期/慢订阅/存储Unknown/真实排空。新增S1检查覆盖五个Owner binding、head/receipt/event/gap双读、技术Operation原身份和借用Runtime不释放；W1覆盖Attach/Dispatcher/订阅、批量CAS预览、撤权、三语和Detach。结果：未知不清Active，拒绝应用仍原子保存Source/Gap，确认无设备副作用，原回执不重跑，事件仅刷新，事实不会因UI消失。

第二轮按字段反查：Definition/Binding来自配置登记；Source/Epoch/Sequence来自原Owner；Currentity/Quality来自来源；Received/Revision/Receipt/Facts来自Core+Store；Actor/Grant来自授权Owner；OwnerAction来自设备/互联Owner回执；cursor/gap来自持久事件；Scope/codec/hash由本页固定；S1的StorageScope/Store/Generation/OperationIdentity来自IM066已接收公开Contract，Owner SQL/Schema由本页唯一决定；W1的控件和布局API均有本机25.2.3 XML声明依据。反查未发现需实现者自行猜测的Owner、单位、状态、身份字节、SQL参数顺序或失败语义；未知的客户容量、物理阈值、真实数据库部署、WPF运行环境和外部授权仍保留为后续门。

## 12. 六项准备状态（本模块自审结论，实施资格仍分开判断）

| DEV-GOV-010 §3.1 | 证据 | 状态 |
|---|---|---|
| 1 边界/非目标/第二消费者 | §1、架构§3/7.1、双Host、§6.4、§9.5 | AL-C0/C1：ModuleCoreImplementationReady（规格）；AL-S1/AL-W1：PreparationIncomplete |
| 2 唯一typed Contract、参数/错误/取消/排空/资源/版本 | §2.5、§3-6、§5 codec、§6.1-6.6、§9.1-9.4 | AL-C0/C1：ModuleCoreImplementationReady（规格）；AL-S1/AL-W1：PreparationIncomplete |
| 3 无UI最小宿主、依赖从端口注入 | §3.6-4、§7、§6.4、§9.1/9.5 | AL-C0/C1：ModuleCoreImplementationReady（规格）；AL-S1：PreparationIncomplete（真实PG后端未验）；AL-W1：PreparationIncomplete（真实WPF未验） |
| 4 正常/边界/失败/重复/并发/取消/超时/关闭/回退 | §2、§6.6、§7、§8、§10、S-01..06、W-01..06 | AL-C0/C1：ModuleCoreImplementationReady（规格）；AL-S1/AL-W1：PreparationIncomplete |
| 5 BenchmarkProfile、测点、分位/资源/失败 | §10及各切片S/W断言 | AL-C0/C1：ModuleCoreImplementationReady（方法已定，目标待Profile）；AL-S1/AL-W1：PreparationIncomplete / NotEvaluated |
| 6 唯一工程/测试/变更范围/最小顺序 | §1.2、§6.1/6.4/6.5、§9.1/9.5、§10 | AL-C0/C1：ModuleCoreImplementationReady（规格）；AL-S1/AL-W1：PreparationIncomplete |

本轮模块自审完成；总模块仍为 `PreparationIncomplete / PendingAcceptance`。AL-C0/C1 仅表示 Core/Runtime 规格达到开工门，不表示代码已实现或验证；AL-S1 缺真实PG/迁移/RLS/Unknown/Golden运行证据，AL-W1缺真实WPF/DevExpress/UIA/三语/退出证据。真实代码编译、Storage/MES/设备、WPF、性能、HIL、现场、Golden和生产资格均未验收。客户容量、物理阈值、部署凭据和外部授权是明确后续门；其余软件字段、参数、序列、SQL/marshal、UI模板和失败语义已在本指导冻结。**表中的`PreparationIncomplete`只表示实现/运行证据门未关闭，不表示本页仍有可决定的软件设计欠项；完整范围结论见§13。**任何范围、Owner、权限、序号、容量或验收变化先修订本唯一指导，再重新自审。


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

## 13. 完整批准范围的文档准备结论（原会话最终结论）

### 13.1 结论与适用范围

对本页当前已批准/已接收的 AL-C0、AL-C1、AL-S1、AL-W1 范围，**可决定的软件设计欠项为零**。输入/输出、状态与事实Owner、授权、取消/超时/排空、版本与codec、持久化绑定、WPF装配、双消费者、参数推荐、异常恢复、性能测点和失败语义均已在本唯一指导中冻结；实现者不需要再补猜领域、SQL、序号、权限、UI命令或恢复决定。该结论是文档准备结论，不提升代码、数据库、WPF、性能、HIL、现场或生产运行资格。

### 13.2 批准摘要条与逐切片结论

| 范围 | 已闭合的软件决定 | 当前实施/验收边界 |
|---|---|---|
| AL-C0 | §2-5 的报警生命周期、epoch/sequence/gap、身份、事实、幂等、完整 ALM1 codec、向量和纯 reducer；§8 的正常/反例 oracle | `ModuleCoreImplementationReady`（仅规格）；Core代码、Smoke、编译和运行尚未执行 |
| AL-C1 | §3.6-4 的 Factory/Runtime、授权端口、原Task、订阅、维护、Stop/Dispose、重启投影和资源所有权；§7 的无UI双Host夹具 | `ModuleCoreImplementationReady`（仅规格）；Core代码、并发、取消、排空和资源实测尚未执行 |
| AL-S1 | §6.1-6.6 的 IM066 五个binding、Owner codec、固定SQL/marshal、schema/RLS边界、UTC ticks、Operation/Task回查、Unknown/AbsentUnsafe、迁移与回退边界 | 软件设计已闭合；仍为 `PreparationIncomplete`，等待真实PG迁移/RLS/注册包、Unknown回查和Golden运行证据 |
| AL-W1 | §9 的 Factory/Session/HostOwner、SummaryStrip/Workbench、DevExpress 25.2.3布局、三语、权限、键盘/UIA、批量CAS预览、双STA、Dispatcher原Task、Detach和借用Runtime释放 | 软件设计已闭合；仍为 `PreparationIncomplete`，等待真实WPF/DevExpress编译、UIA、1920×1080、三语和退出释放证据 |
| 双消费者与边界 | 机台运行/维护宿主和独立MES互联/存储宿主各自Scope、Runtime、Caller、Clock、资源和语言投影，共用同一无UI合同；报警只记录Owner回执，不执行设备动作，不消费图像/AsunImage/HALCON/视觉参数 | 两个消费者的Profile采纳和实际接线仍由各自Owner完成，不产生新的Core设计分歧 |

### 13.3 参数、恢复和性能计划的闭合判断

- 参数来源已固定为“消费者Profile显式值→登记Owner绑定/定义→本模块结构上限”；推荐起点为 `PageSize=128`、订阅容量64、批确认最多128、执行预算2s、维护周期500ms、Store桥等待预算1s。缺失生产Profile拒绝启动，推荐值不得静默写入工艺或扩大上限。客户报警频率、保留期、FreshnessTtl、Severity、AckPolicy、通知和停机规则由两个消费者Owner采纳。
- 异常恢复已固定为原Identity/原Receipt/原Operation只读回查，Unknown不重放副作用，AbsentUnsafe不作为首次重试证明；epoch/sequence缺口、SnapshotChanged、权限撤销、慢订阅、数据库空行、Dispatcher迟到、Stop/Dispose和借用Runtime释放均有明确结果与恢复链。UI不清Active、不确认新Revision、不执行设备动作。
- 性能计划已固定为 `ALM-CORE-01/1.0`：以接纳为起点、提交/事件发布/资源真实释放为终点，记录冷/热、并发、Store延迟、队列/订阅峰值、托管堆/线程、失败/Timeout/Unknown/排空未知，并按完整样本给 P50/P95/P99；软件额度和双Host断言已定，客户目标值待Profile采纳。

上述三项均已有可执行设计，当前没有需要开发者自行决定的软件参数、恢复语义或性能测点。

### 13.4 剩余实现项与外部输入Owner

| 类型 | Owner | 剩余输入/证据 |
|---|---|---|
| Core实现与Smoke | alarms 原会话/产品实现Owner | 创建精确工程，按§10编译、运行Contract/Lifecycle/Ordering/Concurrency/Persistence/Resources测试并取得BenchmarkProfile；不改变本页合同 |
| PG与IM066接入 | storage-database/部署Owner | 提供受管PG、迁移主体、Scope/角色/ACL/凭据，执行本页注册包、RLS、迁移、事务、Unknown回查和Golden；不得由报警模块猜部署事实 |
| WPF与宿主接线 | alarms WPF/宿主Owner | 在真实DevExpress 25.2.3/.NET 10 WPF上完成编译、UIA/键盘、三语长度、1920×1080、Dispatcher和退出释放；宿主继续持有根Owner和Dispatcher直到真释放 |
| 来源与消费者Profile | 设备/采集/互联Owner、机台Owner、MES Owner | 提供Condition事实、Source/Instance/epoch/sequence、阈值/等级/通知/停机政策、保留与频率Profile及OwnerAction原回执；报警模块不补造物理值 |
| 客户与现场资格 | 客户/质量/现场Owner | 提供真实Golden、HIL、物理验收值、设备安全和生产放行输入；这些是外部门，不回写为软件默认 |

### 13.5 自审完成范围与限度

已完成并可复用的证据为：第一轮输入→授权→lookup→快照→Plan→CAS→Receipt→Event→Query/UI→重启/恢复场景链，含 AL-S1 五个binding及原Operation、AL-W1 Attach/Dispatcher/撤权/三语/Detach；第二轮 Definition/Source/Currentity/Receipt/Fact/Actor/OwnerAction/cursor/gap/Scope/codec/UI 字段反查；以及文档链接/DAG/消费者映射、Markdown fence、NUL/零宽字符、codec/SQL/参数/结果列/UTC ticks/关键矛盾定向检查。此前固定来源、字节向量、长度/hash和两轮模块自审结论继续有效，本节不重复重审Core/向量/UI/研究。

限度保持明确：本结论未执行 C# 编译、真实PostgreSQL、WPF/DevExpress/UIA、性能实测、客户Golden、HIL、设备安全或生产验收；因此不把任何 `PreparationIncomplete` 切片提升为运行准入，也不把合成Host或文档校验当作现场证据。若范围、Owner、权限、序号、容量、SQL/codec、UI恢复或验收值变化，必须先修订本指导并重新执行适用自审。

