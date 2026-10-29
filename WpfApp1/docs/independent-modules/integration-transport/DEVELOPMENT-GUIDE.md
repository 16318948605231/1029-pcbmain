# 外部系统可靠交付（integration-transport）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, S1`

- 模块 ID：`IM-046`
- 来源：`PKG-047`；本页版本独立维护，不改来源原文
- 中文名称：外部系统可靠交付
- 版本：`0.2.4-prep`
- 状态：`DesignReview / Prep`
- 日期：2026-10-12
- 规划消费者：MES 互联服务、线体/外部系统连接服务；两个消费者必须使用同一 Core 和同一公开语义
- 目标运行时：C# / .NET 10；核心不依赖 WPF、DevExpress、产品 Shell、ViewModel、制程数据库或设备 SDK

> 本页是脱离检测平台也可接入的实施指导。第3～6节、资源/测试约束及附录A构成本模块唯一 `Module API Contract v0.2` 候选基线：它冻结可先实现的无产品 Core 语义，但不是已批准的平台 `Contract/Schema/State/Owner` 或生产互操作 API。若与后续获批权威或宿主协议冲突，停止受影响切片并先修订本页；未在本文定义的类型不得由实现者自行补造。本页不声称已实现、已互操作、已通过生产或客户验收。

## 0. 权威与阅读顺序

本页只维护外部系统可靠交付的独立接入语义。实施前按以下顺序读取并登记版本：

1. [独立模块架构 IM-ARCH-001](../INDEPENDENT-MODULE-ARCHITECTURE.md)
2. [PKG-047 MES及线体互联交付](../../shared-modules/packages/PKG-047_FactoryIntegration.md)
3. [DEV-PLT-013 跨模块事件与外部互联](../../shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md)
4. [SM-024 外部通信与可靠交付](../../shared-modules/modules/SM-024_integration.md)
5. [公共接口交接地图](../../shared-modules/INTERFACE-MAP.md)
6. [DEV-GOV-004 Contract/Schema Validator 标准](../../01-governance/DEV-GOV-004_Contract_Schema_Validator开发标准.md)、[DEV-GOV-005 模块独立性标准](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)及已批准的 State/Owner/Authority 规则。

`DEV-PLT-013` 的外部消息原字节、字段存在性、两级身份和持久接纳语义是入站适配的上位约束；`DEV-PLT-012` 的发件箱/回执交接是出站持久化约束。当前完整通用技术设计见§8.10～8.12/9/13/16.4；客户Profile/FunctionSpec尚未批准只阻断其生产消息映射/真实互操作，不免除本模块内部protocol/codec/配置/UI设计，也不授权生产互操作。

### 0.1 第二轮复审结论与非适用能力

本轮按正常、边界、故障、恢复和长期运行场景重新推导本页；新增的场景规则优先于仅有的 happy path 示例。模块没有视觉算法、训练或模型恢复路线：噪声、遮挡、退化在本模块对应为字节损坏、截断、编码错误、连接抖动、带宽下降、远端限流和下游不可用，由适配器/队列状态处理。不得为“满足视觉核对”在本模块引入 HALCON 算子、`ImageLibDotNet` 句柄或图像质量判定。

项目 HALCON 26.05 算子资料入口为 [`halcon算子手册/operators`](../../../halcon算子手册/operators/)；本模块不调用其中任何算子。AsunImage 的公共边界为 `ImageLibDotNet`；本模块只允许传递调用方已批准的可序列化引用/载荷，不引用 `HObject`、`HMessage`、`HMessageQueue` 或内部句柄。若未来协议确需传视觉证据，由视觉/证据模块提供版本化引用和保留策略，传输模块不解释像素、区域或质量。

### 0.2 H:\docs 来源复核与采纳边界（2026-10-06）

两份原文已逐段复核，路径、大小和 SHA-256 与[20261006 来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)的 `entries` 一致。本节链接只定位历史来源清单，不声称H:\docs当前文件版本已快照；原路径仅为来源信息。本节只记录本页的内容采纳；清单中的历史 `not-reviewed-in-full-hdocs-audit` 不由本页改写，也不代表来源所述代码已在本平台实现。

| 只读来源与锁定版本 | 本页采纳位置与范围 |
|---|---|
| [MES_Hermes_CFX集成开发指导.md来源登记](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)，原路径 `H:\docs\40-development\60-data\MES_Hermes_CFX集成开发指导.md`，`DEV-INT-001` v2.11，116028 bytes；SHA-256 `48a4546f02add64570f082ccfc17484689f62ea4846d1b14801e82fbbfbcf94e` | 原文§2、§2.1、§2.2、§9～13及2026-10-04候选C：§5.2明确原回执读回，S8/S9明确读取失败和换代围栏，§7明确停止顺序，§7.2分开积压与历史保留，§8.1/8.3细化凭证、协议能力和撤销边界。离线回放沿既有 `DEV-PLT-013 §8.3` 落实，不另建回放权威。 |
| [工厂级数据网络与多站点治理开发指导.md来源登记](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)，原路径 `H:\docs\40-development\60-data\工厂级数据网络与多站点治理开发指导.md`，`DEV-DAT-004` v1.1，4119 bytes；SHA-256 `55f7f7ea13dc14d8112e029a41b1d127ae306f1aa45e2f2f7528be726b523dc3` | 原文§1～3.2：§7.1细化受信作用域隔离、慢站点/热点隔离与恢复公平性，§8.3区分能力声明和互操作证据，§12/13补充可判定验收与队列年龄测点。 |

不迁入 AOI 业务 Envelope、BoardRun/工单/配方对象、配置工作流、签名 Registry、双人再认证实现、`CFX.Reconcile*`/Hermes 恢复 API、中心管理/SPC/设备发布或物理交接动作；这些由各原 Owner 与宿主负责。源项目的“已实现”、exactly-once、认证/现场通过陈述不能成为本平台结论；源容量、离线时长、设备数和长稳时限不能成为本模块默认或客户 SLA。可靠交付须达到声明的耐久确认点并具备所需协议/端口能力，按协议采用至少一次与幂等处理；未知副作用沿原操作对账，不承诺网络恰好一次。

2026-10-06采纳未扩展当时v0.1入口；2026-10-09在相同职责内用v0.2补齐入站、查询、恢复、事件及端口类型。单实例固定Scope，多站点通过独立实例与宿主调度组合，不新建授权系统/MES业务。本页整模块实现/真实资格保持 `DesignReview / Prep`、`PreparationIncomplete`；原C1/C2/S1与A0/A1-DB/U1限定接收保持，当前全部批准范围文档准备结论见§16.4，逐切片状态见§15，不启动产品实现。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Core/Asun.Modules.IntegrationTransport.Core.csproj`；Core 与本文第 3～6 节所有公开类型统一使用 namespace `Asun.Modules.IntegrationTransport`。预定测试工程：`tests/Modules/integration-transport/Asun.Modules.IntegrationTransport.Core.Tests/Asun.Modules.IntegrationTransport.Core.Tests.csproj`。上述项目尚未创建；协议适配器和可选 UI 不在当前 Core binding 内；§10的两个独立无UI Host与模拟端口放唯一测试工程，发布Simulator的路径见§15。
- 允许变更范围：仅上述 Core 和测试工程目录；在明确获准的实现切片中，必要的新文件也只能放入这两个目录。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前C1/C2/S1原六项规格接收保持；C1/C2/S1为`ModuleCoreImplementationReady`（仅准备，未实现/验证）。A0已接收为Core公开端口规格，不是任何真实Adapter资格。主控2026-10-11已限定接收A1-DB 0.2.3-prep的分页/资产/DB双Host指导内容；真实PG statement/fence/RLS/吞吐、WPF、协议及现场资格仍为`PreparationIncomplete / NotReady`；整模块仍PreparationIncomplete。代码任务仍须另行绑定可审计代码基线与明确切片。

## 1. 职责与禁止边界

### 1.1 模块职责

本模块把调用方已经确定的出站意图或受信入站消息，经过有界校验、协议适配、持久队列、幂等登记、重试、回执关联和死信管理，交付给外部系统。核心职责是：

1. 固定一次操作的身份、载荷摘要、目的地、协议版本和映射版本。
2. 区分本地持久接收、网络/传输接受、外部业务接受、外部应用完成和结果未知。
3. 在网络断开、重启、重复消息、乱序、旧租约回调和响应丢失时保留可查询的原操作。
4. 为每个目的地/分区提供有界背压、顺序策略和可观测的积压状态。
5. 将协议、序列化、认证、存储、时钟和诊断实现放在可替换适配器后面。

### 1.2 禁止边界

- 不创建或修改业务事实、机器判定、质量放行、工单主数据、库存、生产排程、配方、运动或 IO 状态。
- 不把 HTTP 200、TCP ACK、消息 broker 确认或本地入队当作 `Applied`、`Committed`、过站批准或设备动作完成。
- 不持有调用方私有表、产品页面、ViewModel、制程规则、设备句柄或厂商 DTO。
- 不从报文中的字符串动态激活 CLR 类型，不使用共享可变的全局序列化设置。
- 不以新操作 ID 规避旧操作的未知回执，不以重试次数换取“网络恰好一次”承诺。
- 不把取消、超时、解析失败、业务拒绝和结果未知压缩成一个 `bool`。
- 不在模块核心使用 HALCON/AsunImage 算子；本能力是非视觉传输能力。涉及视觉事实时只传调用方提供的稳定引用和已批准载荷。

调用方拥有流程顺序、实体/尝试关联、工艺解释、质量放行、设备安全互锁和副作用授权。模块只返回可靠交付事实和投影。

## 1B. 新架构适配要点

本模块的工业协议扩展（OPC UA Pub/Sub、MQTT Sparkplug B）与 Blazor Server Web 层已在 §15B 展开，本节补充面向新平台架构的适配约束。

**架构门禁**：`Asun.Modules.IntegrationTransport.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"本能力是非视觉传输能力"，Core 不使用 HALCON/AsunImage 算子。§10 已明确"两个独立无 UI Host"。

**Blazor/Web**：本模块是 Web 层的传输底座，约束：
- Web 端的 SignalR Hub 推送**状态快照与事件摘要**，不承载原始大对象（图像帧、3D 点云、文件）——这些走 HTTP Range 分片下载
- §1 已明确"不把 HTTP 200、TCP ACK、broker 确认当作 `Applied`/`Committed`"——Web 端不得以"消息已送达"暗示下游已处理
- 浏览器不直接持有设备连接或 OPC UA 会话；所有协议连接由服务端 `IProtocolConnectionFactory` 创建并管理
- §1 已明确"不以新操作 ID 规避旧操作的未知回执"——Web 端重试必须复用原操作 ID

**AI 推理 Tiling**：本模块只传递调用方提供的稳定引用（如 `ModelAssetRef`、`FrameRef`），不参与推理 tile 租约管理；§1 已明确"涉及视觉事实时只传调用方提供的稳定引用和已批准载荷"。

**HALCON 双跑**：本模块是传输层，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 依赖、分层与交付单元

```text
调用应用 / 独立互联 Host
        │ 公开 ContractCandidate（正式采纳后替换）
        ▼
IntegrationTransport.Core（无 UI、无厂商类型）
        ├─ PersistencePort（发件箱、Inbox、租约、死信）
        ├─ TransportAdapter（HTTP/MQTT/TCP/文件等协议）
        ├─ SerializationAdapter（固定版本映射与规范化）
        ├─ CredentialProvider（只读凭证引用）
        ├─ Clock / Scheduler / Diagnostics
可选 IntegrationTransport.Wpf ──公开Core API──► Core（只消费，不由Core引用）
```

公开契约与Core同处 `Asun.Modules.IntegrationTransport.Core.dll`，不机械新增Contracts空工程；协议实现按§8.10固定为Protocols/Brokers包，Wpf按需引用Core/Protocols，Core不反向引用，Host显式装配。Core 可嵌入机台，也可由独立互联 Host 托管；管理 UI 关闭不应停止已声明生命周期的服务。

### 2.1 MES 独立 Host 与通用传输 Core 的边界

“MES 模块”不能等同于本通用传输类库。MES 场景由两个独立交付层组合：

1. **IntegrationTransport.Core/Adapters** 是可嵌入、可单测、无 UI 的技术模块，只负责消息验证、协议映射执行、持久收发、幂等、回执和排空；不含任何 MES 实体、过站规则或检测平台引用。
2. **MES Integration Host** 是单独部署和生命周期管理的进程/服务，也是组合根。它装配 Core、经批准的 MES 协议适配器、版本化映射、凭证引用、持久化端口、健康/诊断端点和可选管理 UI。Host 的启停、升级、配置代、密钥轮换、备份恢复、服务账号、网络隔离与健康检查都必须能脱离检测产品独立执行。

Host 可托管经批准的 MES 业务映射/用例适配，但其每个业务写入仍须调用检测平台或 MES 各自的事实 Owner；不得把工单、产品身份、过站判定、质量放行或库存事实塞入通用 Core。设备应用也可直接复用同一个 Core，不必依赖 MES Host。MES Host 不要求 WPF 常驻；管理 UI 可单独装配、关闭或远程连接，不能持有服务生命周期或事实写权限。

Host 的部署清单至少冻结进程身份、配置/密钥来源、队列存储和容量、监听端口、协议能力、网络/证书策略、启动/停止/排空顺序、升级回退兼容窗及告警探针。客户 MES 协议、字段映射、确认语义、过站规则和现场 SLA 未获批准时，只能交付模拟/回放 Host，不能宣称 MES 互操作完成。

依赖方向只能由 Core 依赖抽象端口，宿主在组合根注入实现。不得在 Core 中 Service Locator、硬编码路径、自动寻找设备、自动创建数据库或隐式初始化 UI。

## 3. Core API v0.2 公共强类型契约

本轮关闭v0.1未定义端口类型和缺失入口，升级为本模块候选 `Module API Contract v0.2`；这是待主会话接收的技术规格修订，不改平台共享契约。当前无已交付v0.1程序集，不能把破坏签名当成已发布版本的Minor兼容。第3～6节、§7/8/10/12/13及附录A共同定义实施语义；消费者不从聊天或脚本补类型。

### 3.1 标识与状态

```csharp
public readonly record struct EndpointId(string Value);
public readonly record struct OperationId(Guid Value);
public readonly record struct MessageId(string Value);
public readonly record struct PartitionKey(string Value);
public readonly record struct PayloadHash(string Value);
public readonly record struct SchemaVersion(ushort Major, ushort Minor);
public readonly record struct MappingVersion(string Value);
public enum DeliveryKind { Observation, Command }
public enum Durability { PersistBeforeSend }
public enum OrderingMode { Unordered, PerPartition }
public enum SequencePolicy { RejectGap, BufferGap }
public enum ReceiptStage { None, Persisted, TransportAccepted, BusinessAccepted, Applied, Rejected, Unknown }
public enum OperationState
{
    Created, Persisted, Sending, RetryWait, CancelRequested, Cancelled,
    Draining, Drained, ResourcesReleased, Completed, Rejected, DeadLetter, Unknown
}
public enum BatchMode { Atomic, PerItem }
```

OperationId非空Guid，Endpoint/Mapping为1..128可打印ASCII字符，MessageId为1..256 UTF-8字节，Partition为1..256 UTF-8字节，Scope各分量为1..128 UTF-8字节；禁止空白、控制字符、无效UTF-16。不自动trim、大小写转换或Unicode归一化来合并身份，比较采用Ordinal；已批准协议要求的规范化在codec做且保留原字节。PayloadHash为64位小写hex SHA-256。Schema.Major≥1；Sequence为0..long.MaxValue，不经double。未知枚举值拒绝。

UTC事件用DateTimeOffset且Offset=0，缺来源时间保留null；不再使用未定义的UtcInstant。`ReceiptStage`表示证据阶段，`OperationState`是当前运行生命周期，`DeliveryStatus`是可跨恢复run查询的交付结果；不能用一个字段代替三者。运行终态对每个RunId唯一，交付Unknown可由后续仅查询的run收敛；历史终态和回执不覆盖。服务生命周期另用ServiceState。本可靠Core仅提供PersistBeforeSend，不提供隐式Volatile降级；旧v0.1的Volatile概念被撤回，不表示无持久化也可靠。

### 3.2 不可变请求、配置与容量

```csharp
public sealed record DeliveryIntent
{
    public required OperationId OperationId { get; init; }
    public required EndpointId Endpoint { get; init; }
    public required SchemaVersion Schema { get; init; }
    public required MappingVersion Mapping { get; init; }
    public required PayloadHash ProfileHash { get; init; }
    public required PayloadHash CapabilityHash { get; init; }
    public required string MessageName { get; init; }
    public required DeliveryKind Kind { get; init; }
    public required string ContentType { get; init; }
    public required ReadOnlyMemory<byte> Payload { get; init; }
    public required PayloadHash PayloadHash { get; init; }
    public PartitionKey? Partition { get; init; }
    public long? Sequence { get; init; }
    public DateTimeOffset? ExpiresAtUtc { get; init; }
    public string? ExternalCorrelation { get; init; }
    public Durability Durability { get; init; } = Durability.PersistBeforeSend;
}
public sealed record EndpointProfile
{
    public required EndpointId Endpoint { get; init; }
    public required ImmutableHashSet<DeliveryKind> AllowedKinds { get; init; }
    public required ImmutableHashSet<SchemaVersion> AllowedSchemas { get; init; }
    public required ImmutableHashSet<string> AllowedMessageNames { get; init; }
    public required MappingVersion Mapping { get; init; }
    public required PayloadHash ProfileHash { get; init; }
    public required AdapterCapabilities Capabilities { get; init; }
    public required ReceiptStage RequiredStage { get; init; }
    public OrderingMode Ordering { get; init; } = OrderingMode.Unordered;
    public SequencePolicy SequencePolicy { get; init; } = SequencePolicy.RejectGap;
    public long FirstSequence { get; init; } = 0;
    public int MaxReorderItems { get; init; } = 128;
    public TimeSpan GapTimeout { get; init; } = TimeSpan.FromSeconds(30);
    public bool AllowEmptyPayload { get; init; }
    public int MaxPayloadBytes { get; init; } = 10_485_760;
    public long MaxQueueBytes { get; init; } = 1_073_741_824;
    public int MaxQueueItems { get; init; } = 100_000;
    public int MaxConcurrentSends { get; init; } = 8;
    public int MaxConcurrentApplicationCalls { get; init; } = 8;
    public TimeSpan ConnectTimeout { get; init; } = TimeSpan.FromSeconds(5);
}
public sealed record TransportOptions
{
    public int MaxPayloadBytes { get; init; } = 10_485_760;
    public long MaxQueueBytes { get; init; } = 1_073_741_824;
    public int MaxQueueItems { get; init; } = 100_000;
    public long MaxResidentBytes { get; init; } = 268_435_456;
    public int MaxConcurrentSends { get; init; } = 8;
    public int MaxConcurrentApplicationCalls { get; init; } = 8;
    public int MaxAttempts { get; init; } = 8;
    public TimeSpan InitialRetryDelay { get; init; } = TimeSpan.FromSeconds(1);
    public TimeSpan MaxRetryDelay { get; init; } = TimeSpan.FromMinutes(5);
    public TimeSpan OperationTimeout { get; init; } = TimeSpan.FromSeconds(30);
    public TimeSpan DrainTimeout { get; init; } = TimeSpan.FromSeconds(30);
    public TimeSpan HeartbeatInterval { get; init; } = TimeSpan.FromSeconds(3);
    public TimeSpan HeartbeatTimeout { get; init; } = TimeSpan.FromSeconds(10);
    public TimeSpan MaxClockSkew { get; init; } = TimeSpan.FromMinutes(5);
    public TimeSpan DeadLetterRetention { get; init; } = TimeSpan.FromDays(30);
    public TimeSpan LeaseDuration { get; init; } = TimeSpan.FromSeconds(60);
    public TimeSpan RecoveryPollInterval { get; init; } = TimeSpan.FromSeconds(1);
    public int EventBufferItems { get; init; } = 256;
    public int MaxSubscriptions { get; init; } = 16;
}
public sealed record TransportConfiguration(TransportScope Scope,
    TransportOptions Options, ImmutableArray<EndpointProfile> Endpoints);
public sealed record BatchDeliveryIntent(string BatchId, BatchMode Mode,
    ImmutableArray<DeliveryIntent> Items);
```

配置是宿主已验证的不可变输入，不提供远端热改Profile API；替换通过Stop/排空、新实例或新服务代完成。ProfileHash覆盖端点配置/Mapping/Schema/消息集合/确认与顺序政策，CapabilityHash等于Capabilities.Fingerprint；完整持久快照供历史run使用，Hash不等于认证证明。消息名和ContentType为1..128可打印ASCII字符，ExternalCorrelation为0..256 UTF-8字节，非空时参与指纹；期限初次提交须晚于接收时点，重复已接纳请求先查原回执再判断新接纳期限。

指纹采用§3.4唯一canonical编码与完整Golden，覆盖字段、顺序、nullable、集合及自Hash排除均由该节冻结，禁止“按DTO声明顺序”推断。先验证原字节摘要，再计算指纹；Hash不证明认证、不允许替代原字节核对。连接identity/generation只作为当前认证与会话证据，不进入跨重连去重指纹。映射升级不重算已持久指纹；同来源键异原字节即使解码结果相同也冲突。

各硬上限是软件工程有效域与示例默认，不是现场目标。所有数量使用checked累计，不能因int溢出出现负容量：

| 参数 | 有效域/关系 | 生效范围 |
|---|---|---|
| MaxPayloadBytes | 0..1 GiB；默认10 MiB；空输入仅AllowEmptyPayload=true | 原始/展开/编码后的实际上限为Options、Profile、Capabilities的最小值。 |
| MaxQueueBytes / MaxQueueItems | 1 MiB..1 TiB / 1..10000000；默认1 GiB/100000 | 总Outbox+Inbox未完成项，以及各Endpoint子限额；副本只计一次逻辑载荷，原字节/展开字节皆纳预算。 |
| MaxResidentBytes | 1 MiB..1 TiB，默认256 MiB | 所有驻留复制、解码、编码、在途buffer、事件/任务账本及保留Owner预留总额；含原Task和迟到资源，见§7/10/13。 |
| MaxConcurrentSends / MaxConcurrentApplicationCalls | 各1..1024，总限额与端点子限额取小 | 入/出站不互占满；每PerPartition至多1个在途调用。 |
| MaxAttempts | 1..100，总Send/Apply尝试数，含首次，默认8 | Query/编码失败不消耗发送次数但受时间预算；次数耗尽不将Unknown伪装成DeadLetter。 |
| InitialRetryDelay / MaxRetryDelay | 100 ms..1 h / 1 s..24 h；前者≤后者 | 明确可重试且NotSent错误的有限退避，不适用于未知副作用盲发。 |
| OperationTimeout / ConnectTimeout | 100 ms..24 h / 100 ms..10 min | 单次存储/解析/认证/网络等待预算；整体run另受期限约束。 |
| DrainTimeout / LeaseDuration | 1 s..24 h；默认30 s / 60 s；LeaseDuration≥2×OperationTimeout | 排空等待/存储租约；续租最多每LeaseDuration/3一次，源任务未退出禁止借租约超时释放内存。 |
| HeartbeatInterval / HeartbeatTimeout | 500 ms..1 h / 1 s..24 h；Timeout≥Interval | 仅能力支持时由适配器使用，不能当业务确认或删操作。 |
| MaxClockSkew | 0..24 h，默认5 min | 只诊断时间域，不能补原事件时间/重排序列。 |
| DeadLetterRetention | 1 h..3650 d，默认30 d | 实际删除仍受宿主保留窗口/Legal Hold/去重引用，期限不构成自动删除许可。 |
| RecoveryPollInterval | 100 ms..1 min，默认1 s | 仅查询恢复/持久待办轮询，避免丢调度通知后永久停顿。 |
| EventBufferItems / MaxSubscriptions | 1..10000 / 1..1024；默认256/16 | 瞬时事件只可合并，无生产消息丢弃。 |
| FirstSequence / MaxReorderItems / GapTimeout | 0..long.MaxValue / 1..10000 / 100 ms..24 h | Profile定义序号起点；BufferGap的待缺口项/等待上限，超时阻断该分区不跳过。 |

关系校验用ticks做checked算术，先检查各自范围，再检查LeaseDuration.Ticks≥checked(2×OperationTimeout.Ticks)。默认60 s=2×30 s有效；OperationTimeout覆盖为31 s而租约仍60 s时拒绝，31 s/62 s有效；因租约上限24 h，OperationTimeout的可行组合上限为12 h（12 h/24 h有效，12 h+1 tick/24 h拒绝）。不得钳制、截断或自动延长。端点ConnectTimeout也受对应调用总预算约束。

批次BatchId为1..128可打印ASCII字符，Items为1..10000；default ImmutableArray、空批次、同批重复OperationId均拒绝，不能把空输入标成Completed。Atomic与PerItem只是本地接纳事务，**不是外部批量动作原子性**。Atomic遇已有同指纹项可复用，其余新项同事务提交；任一冲突整批新项不提交、已有历史不撤销。BatchId只关联，幂等由各OperationId决定，按Items顺序返回全集。

### 3.3 快照、回执与预算

```csharp
public sealed record QueryOptions
{
    public bool ReadReceipts { get; init; } = true;
    public bool IncludeDiagnostics { get; init; }
    public int MaxReceiptCount { get; init; } = 100;
    public TimeSpan? Timeout { get; init; }
}
public sealed record DeliverySnapshot
{
    public required OperationId OperationId { get; init; }
    public required EndpointId Endpoint { get; init; }
    public required DeliveryDirection Direction { get; init; }
    public required Guid RunId { get; init; }
    public required OperationState State { get; init; }
    public required DeliveryStatus DeliveryStatus { get; init; }
    public required ReceiptStage Stage { get; init; }
    public required long Revision { get; init; }
    public required PayloadHash PayloadHash { get; init; }
    public required SchemaVersion Schema { get; init; }
    public required MappingVersion Mapping { get; init; }
    public required PayloadHash ProfileHash { get; init; }
    public required PayloadHash CapabilityHash { get; init; }
    public int AttemptCount { get; init; }
    public bool MayHaveReachedRemote { get; init; }
    public bool ResourcesReleased { get; init; }
    public DateTimeOffset? PersistedAtUtc { get; init; }
    public DateTimeOffset? LastAttemptAtUtc { get; init; }
    public DateTimeOffset? CompletedAtUtc { get; init; }
    public string? ErrorCode { get; init; }
    public string? DiagnosticRef { get; init; }
}
```

RequiredStage只允许TransportAccepted/BusinessAccepted/Applied；Applied必须有能力支持和目标Owner回执，RequiredStageReached才可DeliveryStatus=Succeeded。只取得TransportAccepted且还等待业务阶段时为Pending，等待预算到期为Unknown，保留已证明Stage。Profile不能用Rejected/Unknown当“成功目标”。OperationState.Completed表示该run完成资源与已声明目标，不代表整个产品工艺完成；查询run可Completed但DeliveryStatus仍Unknown/Rejected，UI必须同时显示。

QueryOptions为引用record，避免struct的default把默认MaxReceiptCount变为0；Timeout=null沿用OperationTimeout，显式值100 ms..10 min。长时间等待和总排空采用TimeProvider单调时钟，LeaseToken过期由Store权威时间判定，两者不得混用。Stage/Revision/RunId、UTC时点和证据引用皆是快照，不能由UI编辑。所有端口和服务结果的可选字段由状态判别，不用null推断成功。

### 3.4 Canonical编码与独立Golden

以下是v0.2唯一算法，不使用JSON顺序、GetHashCode、平台端序或Guid.ToByteArray。域是无长度前缀的ASCII固定串；S(x)=U32BE(UTF8字节数)+严格UTF8(x)，无效UTF-16拒绝，不规范化。U32为枚举/集合个数，I32为int限额，I64为long、字节长度和ticks，Schema=U16BE(Major)+U16BE(Minor)；Hash是解码后的32字节，不是64字节hex文本。Guid用S(小写D格式)。bool单字节00/01；nullable先00/01，有值随后按其类型编码，空串存在与null不同；UTC期限用I64(UtcDateTime.Ticks)。枚举编码值为§3/4声明从0开始的固定值，未来不得重排。

集合先U32数量，字符串按Ordinal严格排序后逐个S编码，Schema按Major/Minor升序，Kinds按U32升序；重复成员/空必需集合拒绝。Capability的MessageNames/AuthenticationModes/EvidenceRefs/Limitations按集合处理并禁止重复；后两项可空但不可default。Capability.Fingerprint与Profile.ProfileHash分别排除自身；Profile只写已重算核对的Capability.Fingerprint，完整Capability仍保存在闭包中。每次加载先验证capHash再验证profileHash，不能用Hash替代全部字段可读性。

| 域 | 固定顺序（不从DTO声明顺序推导） |
|---|---|
| ASUN-IT-CAP-V2 | ProtocolId,WireVersion,Role,AdapterVersion,PackageHash,MessageNames,AuthenticationModes,MaxWireBytes,MaxExpandedBytes,SupportsQuery,SupportsIdempotency,SupportsAppliedReceipt,SupportsOffline,Ordering,EvidenceRefs,Limitations |
| ASUN-IT-PROFILE-V2 | Endpoint,AllowedKinds,AllowedSchemas,AllowedMessageNames,Mapping,Capabilities.Fingerprint,RequiredStage,Ordering,SequencePolicy,FirstSequence,MaxReorderItems,GapTimeout.Ticks,AllowEmptyPayload,MaxPayloadBytes,MaxQueueBytes,MaxQueueItems,MaxConcurrentSends,MaxConcurrentApplicationCalls,ConnectTimeout.Ticks |
| ASUN-IT-INTENT-V2 | Scope.TenantId,SiteId,LineId,OperationId,Endpoint,Schema,Mapping,ProfileHash,CapabilityHash,MessageName,Kind,ContentType,I64(Payload.Length),PayloadHash,Partition?,Sequence?,ExpiresAtUtc?,ExternalCorrelation?,Durability；PayloadHash只写一次，原载荷逐字节先验Hash |
| ASUN-IT-INBOUND-V2 | Scope.TenantId,SiteId,LineId,Endpoint,SourceNamespace,Decoded.MessageId,RawHash,I64(RawBytes.Length),Decoded.Schema,Mapping,ProfileHash,CapabilityHash,Decoded.MessageName,RawContentType,Decoded.ContentType,Decoded.Partition?,Decoded.Sequence?,I64(ApplicationPayload.Length),Decoded.PayloadHash |

入站OperationId不进入来源去重指纹，第一次登记后返回原OperationId；ConnectionIdentity/Generation不进入指纹但每次须受信核对。Mapping来自冻结Profile，Decoded内容来自已批准codec；同原字节不同解码结果/政策视为冲突，不重写历史解释。哈希碰撞/错误的调用方Hash不能省略原字节保留和逐字节冲突验证。

下面Golden是合成小输入，数值为工程夹具，不是客户事实。全部字段由§10 HostInputs.Create("s")构造：Scope=t/s/l，Endpoint=e，Mapping=m，M/Observation，Schema1.0，两个payload均UTF8 "{}"（7b7d），GUID出站末位1、入站末位2；cap=sim/1/client/1，PackageHash=SHA256(empty)，消息M，认证host-ref，两上限1024，Query/Idempotency/Offline=true、Applied=false、Unordered，EvidenceRefs=[sim-only]、Limitations=[no-network]。Profile全部值见§10赋值，其余默认Ordering/SequencePolicy/FirstSequence/AllowEmptyPayload取0/0/0/false；RequiredStage=BusinessAccepted(3)，所有nullable为空。Inbound来源n、连接connection-1/generation1，decoded ID=i，M、Schema1.0、ContentType=application/json、payload7b7d。

空包Hash=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855；
payloadHash=44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a。
下面每行是一组已标出的字段字节；从上到下直接拼接，无换行/分隔字节。

**Capability：148 bytes；SHA256=fca0467a2740fcec48fe1f4641740ccdd2c0a08e896b115b6b31e174d3612be6**

```text
4153554e2d49542d4341502d5632
0000000373696d 0000000131 00000006636c69656e74 0000000131
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
00000001000000014d 0000000100000008686f73742d726566
00000400 00000400 01 01 00 01 00000000
000000010000000873696d2d6f6e6c79 000000010000000a6e6f2d6e6574776f726b
```

**Profile：150 bytes；SHA256=5ce4959b78fd146fb17b73d5d2a830383b9811560df2e3166db83b9bda66270e**

```text
4153554e2d49542d50524f46494c452d5632
0000000165 0000000100000000 0000000100010000 00000001000000014d 000000016d
fca0467a2740fcec48fe1f4641740ccdd2c0a08e896b115b6b31e174d3612be6
00000003 00000000 00000000 0000000000000000 00000001
0000000000989680 00 00000400 0000000000100000 00000004
00000001 00000001 0000000000989680
```

**Intent：227 bytes；SHA256=f30b876fe83f585ae5b0cc6be8a7a94fd2f89c52772a6f1fa7ff72a6ca492468**

```text
4153554e2d49542d494e54454e542d5632
0000000174 0000000173 000000016c
0000002430303030303030302d303030302d303030302d303030302d303030303030303030303031
0000000165 00010000 000000016d
5ce4959b78fd146fb17b73d5d2a830383b9811560df2e3166db83b9bda66270e
fca0467a2740fcec48fe1f4641740ccdd2c0a08e896b115b6b31e174d3612be6
000000014d 00000000 000000106170706c69636174696f6e2f6a736f6e 0000000000000002
44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
00 00 00 00 00000000
```

**Inbound：248 bytes；SHA256=b1f6ea6f96ce7344e92aeaa6fa4d963d13ea2bd6c54132ac31c78620ae903378**

```text
4153554e2d49542d494e424f554e442d5632
0000000174 0000000173 000000016c 0000000165 000000016e 0000000169
44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
0000000000000002 00010000 000000016d
5ce4959b78fd146fb17b73d5d2a830383b9811560df2e3166db83b9bda66270e
fca0467a2740fcec48fe1f4641740ccdd2c0a08e896b115b6b31e174d3612be6
000000014d 000000106170706c69636174696f6e2f6a736f6e
000000106170706c69636174696f6e2f6a736f6e 00 00 0000000000000002
44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a
```

测试必须独立按字段生成以上bytes并比较长度、逐字节内容和Hash三者；不能只调用Core后与其自算Hash比较。变体断言：交换集合输入顺序Hash不变；改Scope/Mapping/RequiredStage/任一上限改变对应Hash；连接generation1→2指纹不变而旧代回调不能推进状态；同来源键RawBytes变化Conflict；null→存在空Correlation编码多四字节并改变指纹；非UTC期限拒绝，超大Sequence保持整数精确。Golden重算只证明canonical数学，不代表产品C#或协议互操作通过。

## 4. API 入口与适配端口

以下是 `Module API Contract v0.2` 的唯一端口，不是语义伪代码。第3节与本节的 C# 类型统一显式 `public`，namespace 为 `Asun.Modules.IntegrationTransport`；只依赖 .NET 10 BCL。具体实现尚未创建。构造函数为 `IntegrationTransport(TransportConfiguration configuration, IPersistencePort persistence, ITransportAdapterProvider adapters, ISerializationAdapter codec, IApplicationPort application, IAuthorityPort authority, TimeProvider timeProvider)`；实现 `IIntegrationTransport`。依赖均由宿主注入，构造只做内存校验，不开连接、不建库。

### 4.1 公开服务

```csharp
public interface IIntegrationTransport
{
    ValidationResult Validate(DeliveryIntent intent, EndpointProfile profile);
    Task<EnqueueResult> EnqueueAsync(DeliveryIntent intent, CallContext call,
        CancellationToken ct = default);
    Task<BatchEnqueueResult> EnqueueBatchAsync(BatchDeliveryIntent batch,
        CallContext call, CancellationToken ct = default);
    Task<EnqueueResult> ReceiveAsync(InboundDeliveryIntent input, CallContext call,
        CancellationToken ct = default);
    Task<DecodeResult> ReplayAsync(InboundDeliveryIntent input, CallContext call,
        CancellationToken ct = default);
    Task<QueryResult> QueryAsync(OperationId id, QueryOptions options,
        CallContext call, CancellationToken ct = default);
    Task<DeliveryPage> ListAsync(DeliveryFilter filter, CallContext call,
        CancellationToken ct = default);
    IAsyncEnumerable<DeliveryEvent> ObserveAsync(CallContext call,
        CancellationToken ct = default);
    Task<ControlResult> RecoverAsync(RecoveryRequest request, CallContext call,
        CancellationToken ct = default);
    Task<ControlResult> RequestCancelAsync(OperationId id, long expectedRevision,
        CallContext call, CancellationToken ct = default);
    Task<ServiceResult> StartAsync(CallContext call, CancellationToken ct = default);
    Task<DrainResult> DrainAsync(TimeSpan timeout, CancellationToken ct = default);
    Task<ServiceResult> StopAsync(TimeSpan timeout, CancellationToken ct = default);
}
```

### 4.2 六组公开入口/请求/回执映射

v0.2补齐既有能力入口；六组按职责计，不按方法计，不沿用旧v0.1的缺项签名。

| 入口组 | 方法 | 可执行语义 |
|---|---|---|
| 1. 校验 | `Validate` | 同步、无I/O的字段/摘要/Profile形状检查；不证明当前授权，不创建操作。 |
| 2. 接纳与离线解析 | `EnqueueAsync/EnqueueBatchAsync/ReceiveAsync/ReplayAsync` | 前三者达到持久接纳才返回Persisted；Replay只解析，禁生产端点/应用/队列写入。 |
| 3. 查询与投影 | `QueryAsync/ListAsync/ObserveAsync` | 权威存储快照和可丢失的瞬时通知分开；Query不隐式对账，List有界翻页。 |
| 4. 取消与受控恢复 | `RequestCancelAsync/RecoverAsync` | 当前授权、原身份、ExpectedRevision；恢复模式区分仅查询对账与已证明安全的重投，绝不换ID。 |
| 5. 生命周期 | `StartAsync/StopAsync` | 返回服务结果；Stop未排空不能成功，Start不能覆盖正在排空/隔离实例。 |
| 6. 排空 | `DrainAsync` | 关闭新接纳/领取门，等待本层真实任务/回调/引用归还；可保留持久待办。 |

`QueryResult.Status=Found` 才有Snapshot；`NotFound` 必须来自成功的权威读取。Unavailable/Conflict/Cancelled是不同结果，不能伪造空快照。业务校验、端口错误与取消采用本页结果返回；对象已释放/调用结构错误可抛标准异常，不以异常文字作为用户提示。服务收到调用方取消后可能已提交，Enqueue返回 `CommitStatus.Unknown` 并保留原ID；不得用 `TaskCanceledException` 暗示“未接纳”。批量返回每项CommitStatus，不用State=Rejected冒充已持久操作。所有异步入口预算由Options或调用参数限定。

Start按：校验不可变配置→核授权/能力→读取存储健康/兼容与遗留租约→打开适配器→开启接纳/调度门；任一步失败关闭已打开实例并报告ServiceResult。重复Start在Running返回原运行代；停止中返回Conflict。Drain/Stop共享同一个后台排空任务；调用方取消只停止等待，服务保持Draining。只有Drained且ResourcesReleased=true，Stop才能返回Stopped；否则NotDrained/Cancelled。成功Stopped后可再Start生成新服务代，旧回调不能跨代；旧隔离任务未结束时拒绝重启。

### 4.3 可替换端口

```csharp
public interface IAuthorityPort
{
    Task<AuthorityDecision> CheckAsync(AuthorityRequest request, CancellationToken ct);
}
public interface ITransportAdapterProvider
{
    Task<PortResult<ITransportAdapter>> OpenAsync(TransportScope scope,
        EndpointProfile profile, CancellationToken ct);
}
public interface ITransportAdapter
{
    AdapterCapabilities Capabilities { get; }
    Task<TransportSendResult> SendAsync(TransportEnvelope envelope, CancellationToken ct);
    Task<RemoteQueryResult> QueryAsync(TransportQuery query, CancellationToken ct);
    void RequestClose(); // 幂等、不等待、不执行宿主取消回调
    Task<AdapterDrainResult> DrainAsync(TimeSpan timeout, CancellationToken ct);
}
public interface ISerializationAdapter
{
    Task<PortResult<EncodedPayload>> EncodeAsync(DeliveryIntent intent,
        EndpointProfile profile, CancellationToken ct);
    Task<DecodeResult> DecodeAsync(InboundDeliveryIntent input,
        EndpointProfile profile, CancellationToken ct);
}
public interface IApplicationPort
{
    ApplicationCapabilities Capabilities { get; }
    Task<TransportSendResult> ApplyAsync(ApplicationRequest request, CancellationToken ct);
    Task<RemoteQueryResult> QueryAsync(TransportQuery query, CancellationToken ct);
    void RequestClose();
    Task<AdapterDrainResult> DrainAsync(TimeSpan timeout, CancellationToken ct);
}
public interface IPersistencePort
{
    Task<PortResult<StoreHealth>> CheckAsync(TransportScope scope, CancellationToken ct);
    Task<RegistrationResult> RegisterAsync(RegistrationRequest request, CancellationToken ct);
    Task<PortResult<StoredOperation>> ReadAsync(TransportScope scope,
        OperationId id, CancellationToken ct);
    Task<PortResult<StoredOperation>> ReadInboxAsync(TransportScope scope,
        EndpointId endpoint, string sourceNamespace, MessageId messageId,
        CancellationToken ct);
    Task<PortResult<StorePage>> ListAsync(TransportScope scope,
        DeliveryFilter filter, CancellationToken ct);
    Task<PortResult<ClaimedOperation>> ClaimAsync(ClaimRequest request, CancellationToken ct);
    Task<PortResult<LeaseToken>> RenewAsync(LeaseToken lease,
        TimeSpan duration, CancellationToken ct);
    Task<PortResult<DeliverySnapshot>> CompareExchangeAsync(StoreUpdate update,
        CancellationToken ct);
    Task<PortResult<bool>> ReleaseAsync(LeaseToken lease, CancellationToken ct);
    Task<PortResult<QueueStatistics>> GetStatisticsAsync(TransportScope scope,
        CancellationToken ct);
}
```

Store端口拥有原子持久登记、Inbox来源唯一键、作用域/端点/分区游标、容量预留、租约和CAS；Core拥有调度/交付状态，不写业务表。Register在同一事务核对身份指纹、总量/子配额、分区序号并写入载荷/初始快照/回执；Atomic批量全部校验和提交或全拒，PerItem各自提交。支持不了原子批量则在任何写入前返回IT-CAP-001，不能降为逐项。相同原ID同指纹先回读，再检查新接纳容量/期限；旧记录不因队列已满/过期变成新请求拒绝。同外部来源键重复入站返回首次OperationId。存储故障后按原操作读回，不生成第二账本。

Claim一次只返回一个操作，租约必须原子检查Scope、Endpoint、Direction、DueAt、分区头和容量；`NotFound` 是当前无可领取，不是存储坏。发送前CAS写入当前RunId、`MayHaveReachedRemote=true`、尝试数和Revision后才能调用外部端口；崩溃宁可保持Unknown，不能先发送后记录。Renew依据存储权威期限，不把某worker本机时钟作为跨进程有效性。CompareExchange原子校验ExpectedRevision和当前LeaseToken，追加不可变回执并更新状态/调度时间/游标；不能覆盖或减少历史回执。旧租约释放是幂等的，但不得释放新租约。新worker领取“曾Sending、旧租约过期”只能先查询原远端，不因租约过期证明未发生副作用。

端口返回的Task代表其源工作与回调已退出；Core的WaitAsync/预算只截止等待，保留未退出的源Task与buffer。`RequestClose`仅发关闭信号，DrainStatus证明释放；Unsupported/TimedOut都不复用实例。所有依赖引用默认由宿主拥有，Core仅拥有provider返回的连接scope、自己复制的buffer、租约和订阅；共享Application/Store服务不能由一个模块实例全局Dispose。Application的RequestClose/Drain只停止该绑定实例的本层调用，不撤销已提交业务。TimeProvider使用GetTimestamp/GetElapsedTime控制本地预算，UTC仅作接收/到期记录。

### 4.4 端口类型闭合

以下声明与第3节拼接构成公开类型全集；使用 `System.Collections.Immutable`、`System.Threading.Tasks`、`System.Threading`。集合/记录返回后不可变，输入ReadOnlyMemory在原始异步Task真实完成前由调用方保持字节不变；WaitAsync包装器超时不结束借用。Core在接纳前复制成自有字节，原任务超时/迟到时由§10根Owner保留输入、原Task和复制体。宿主若违反借用约定，摘要变化拒绝，不保证并发写内存可接受。

```csharp
public enum CommitStatus { Persisted, Rejected, Unknown }
public enum PortStatus { Ok, NotFound, Conflict, Unavailable, Cancelled, Unknown }
public enum QueryStatus { Found, NotFound, Unavailable, Conflict, Cancelled, Unauthorized }
public enum RecoveryMode { ReconcileOnly, RetryProvenSafe }
public enum ControlStatus { Accepted, NoChange, Conflict, Denied, Unknown, Cancelled }
public enum ServiceState { Stopped, Starting, Running, Draining, Isolated }
public enum ServiceStatus { Started, AlreadyRunning, Stopped, NotDrained, Conflict, Failed, Cancelled }
public enum DrainStatus { Drained, NotDrained, Cancelled }
public enum AdapterDrainStatus { Drained, TimedOut, Unsupported }
public enum DeliveryDirection { Outbound, Inbound }
public enum DeliveryStatus { Pending, Succeeded, Rejected, Cancelled, DeadLetter, Unknown }
public enum SendCertainty { NotSent, MayHaveReached, ReceiptConfirmed }
public enum RemoteStatus { Found, ProvenNotApplied, NotFound, Unavailable, Conflict, Unsupported }
public enum EventKind { SnapshotChanged, QueueChanged, RefreshRequired }
public enum TransportAction { Start, Enqueue, Receive, Query, Replay, Cancel, Reconcile, Retry }

public sealed record TransportScope(string TenantId, string SiteId, string LineId);
public sealed record CallContext(string AuthorizationRef, string TraceId);
public sealed record TransportError(string Code, string FieldPath, string ActualSummary,
    bool Retryable, string NextActionKey, string? DiagnosticRef = null);
public sealed record ValidationResult(bool IsValid,
    ImmutableArray<TransportError> Errors);
public sealed record PortResult<T>(PortStatus Status, T? Value, TransportError? Error);
public sealed record AuthorityRequest(TransportScope Scope, TransportAction Action,
    CallContext Call, OperationId? OperationId, EndpointId? Endpoint,
    PayloadHash? RequestFingerprint, long? ExpectedRevision);
public sealed record AuthorityDecision(bool Allowed, long AuthorityEpoch,
    DateTimeOffset ValidUntilUtc, string PolicyHash, TransportError? Error);
public sealed record AdapterCapabilities(string ProtocolId, string WireVersion,
    string Role, string AdapterVersion, PayloadHash PackageHash, PayloadHash Fingerprint,
    ImmutableArray<string> MessageNames, ImmutableArray<string> AuthenticationModes,
    int MaxWireBytes, int MaxExpandedBytes, bool SupportsQuery, bool SupportsIdempotency,
    bool SupportsAppliedReceipt, bool SupportsOffline, OrderingMode Ordering,
    ImmutableArray<string> EvidenceRefs, ImmutableArray<string> Limitations);
public sealed record ApplicationCapabilities(bool SupportsQuery, bool SupportsIdempotency);
public sealed record InboundDeliveryIntent(OperationId OperationId, EndpointId Endpoint,
    string SourceNamespace, string ConnectionIdentity, long ConnectionGeneration,
    PayloadHash ProfileHash, PayloadHash CapabilityHash, string ContentType,
    ReadOnlyMemory<byte> RawBytes, PayloadHash RawHash);
public sealed record DecodedMessage(MessageId MessageId, string MessageName,
    SchemaVersion Schema, PartitionKey? Partition, long? Sequence,
    string ContentType, ReadOnlyMemory<byte> ApplicationPayload, PayloadHash PayloadHash);
public sealed record DecodeResult(bool IsValid, DecodedMessage? Message,
    ImmutableArray<TransportError> Errors);
public sealed record EncodedPayload(string ContentType, ReadOnlyMemory<byte> Bytes,
    PayloadHash WireHash);
public sealed record TransportEnvelope(TransportScope Scope, Guid RunId,
    DeliveryIntent Intent, EncodedPayload Encoded);
public sealed record TransportQuery(TransportScope Scope, OperationId OperationId,
    EndpointId Endpoint, PayloadHash RequestFingerprint, string? ExternalCorrelation);
public sealed record ReceiptRecord(string ReceiptId, OperationId OperationId,
    ReceiptStage Stage, string AuthorityId, string EvidenceRef, PayloadHash EvidenceHash,
    DateTimeOffset ReceivedAtUtc, long ConnectionGeneration);
public sealed record TransportSendResult(SendCertainty Certainty,
    ReceiptRecord? Receipt, TransportError? Error, TimeSpan? RetryAfter);
public sealed record RemoteQueryResult(RemoteStatus Status, ReceiptRecord? Receipt,
    string? NotAppliedEvidenceRef, TransportError? Error);
public sealed record ApplicationRequest(TransportScope Scope, Guid RunId,
    OperationId OperationId, EndpointId Endpoint, DecodedMessage Message,
    MappingVersion Mapping, PayloadHash ProfileHash, PayloadHash RequestFingerprint);
public sealed record EnqueueResult(OperationId OperationId, CommitStatus CommitStatus,
    bool Persisted, bool DuplicateOfExisting, long? InitialRevision,
    ImmutableArray<TransportError> Errors);
public sealed record ItemDeliveryResult(OperationId OperationId, CommitStatus CommitStatus,
    OperationState? State, string? ErrorCode, long? Revision);
public sealed record BatchEnqueueResult(string BatchId, BatchMode Mode,
    ImmutableArray<ItemDeliveryResult> Items, bool Persisted, bool AtomicRejected);
public sealed record QueryResult(QueryStatus Status, DeliverySnapshot? Snapshot,
    ImmutableArray<ReceiptRecord> Receipts, TransportError? Error);
public sealed record DeliveryFilter(EndpointId? Endpoint, DeliveryDirection? Direction,
    DeliveryStatus? Status, string? Cursor, int PageSize = 100);
public sealed record DeliveryPage(ImmutableArray<DeliverySnapshot> Items,
    string? NextCursor, TransportError? Error);
public sealed record RecoveryRequest(OperationId OperationId, long ExpectedRevision,
    RecoveryMode Mode);
public sealed record ControlResult(ControlStatus Status, DeliverySnapshot? Snapshot,
    TransportError? Error);
public sealed record ServiceResult(ServiceStatus Status, ServiceState State,
    long ServiceGeneration, DrainResult? Drain, TransportError? Error);
public sealed record DrainResult(DrainStatus Status, int ActiveOperations,
    int PendingPersistedOperations, bool ResourcesReleased);
public sealed record AdapterDrainResult(AdapterDrainStatus Status, int ActiveCalls,
    bool ResourcesReleased);
public sealed record DeliveryEvent(long ServiceGeneration, long EventSequence,
    EventKind Kind, OperationId? OperationId, long? Revision);
public sealed record QueueStatistics(long PendingItems, long PendingBytes,
    long HistoryItems, long HistoryBytes, TimeSpan? OldestPendingAge);
public sealed record StoreHealth(bool Durable, bool AtomicBatch,
    string StoreSchemaVersion);
public sealed record StoredOperation(TransportScope Scope, EndpointProfile Profile,
    DeliveryIntent? Outbound,
    InboundDeliveryIntent? Inbound, DecodedMessage? Decoded,
    PayloadHash RequestFingerprint, DeliverySnapshot Snapshot,
    ImmutableArray<ReceiptRecord> Receipts, DateTimeOffset? NextAttemptAtUtc);
public sealed record RegistrationRequest(TransportScope Scope, string? BatchId,
    BatchMode Mode, ImmutableArray<StoredOperation> Operations,
    TransportOptions Limits, ImmutableArray<EndpointProfile> Profiles);
public sealed record RegistrationResult(ImmutableArray<EnqueueResult> Items,
    bool AtomicRejected);
public sealed record StorePage(ImmutableArray<StoredOperation> Items, string? NextCursor);
public sealed record ClaimRequest(TransportScope Scope, EndpointId Endpoint,
    DeliveryDirection Direction, Guid WorkerId, TimeSpan LeaseDuration);
public sealed record LeaseToken(TransportScope Scope, OperationId OperationId,
    Guid WorkerId, long LeaseGeneration, DateTimeOffset ExpiresAtUtc);
public sealed record ClaimedOperation(StoredOperation Operation, LeaseToken Lease);
public sealed record StoreUpdate(TransportScope Scope, OperationId OperationId,
    long ExpectedRevision, LeaseToken? Lease, DeliverySnapshot NextSnapshot,
    ImmutableArray<ReceiptRecord> AppendReceipts, DateTimeOffset? NextAttemptAtUtc);
```

StoredOperation的Outbound/Inbound严格二选一，Inbound必须有Decoded且保存RawBytes/RawHash；Snapshot.OperationId与来源原操作一致。权限、配置、能力与原请求完整指纹都不是可由远端声明的认证证明。AuthorityPort必须解析不可伪造的宿主引用，绑定Scope/Action/原请求指纹/CAS；返回Unknown、过期或PolicyHash缺失一律拒绝新副作用。撤权要求宿主在真实端口边界提供当前epoch/租约围栏，重复CheckAsync不宣称跨进程瞬时撤权原子性。诊断读取和列表使用当前权限，不沿旧回执授权新动作。

ReceiptId/AuthorityId是1..256 UTF-8字节稳定ID；EvidenceRef是受控引用，非任意路径/URL，EvidenceHash核其原字节。ReceiptConfirmed必须有已验证回执；NotSent禁止带成功回执；ProvenNotApplied必须有端点权威证据引用，普通NotFound、HTTP404、空响应都不等价。ReceiptStage不以枚举大小作max比较；保存已证明的成功阶段，Unknown/Rejected另保留错误/回执，不抹掉旧TransportAccepted。Applied只有端点声明支持且精确业务证据确认时采纳，本模块仍不获设备/质量权。

### 4.5 查询、事件、入站确认与重投

List在Scope内按创建序号、OperationId稳定翻页，PageSize=1..500；Cursor为Store签发的有界不透明游标（≤2048 UTF-8字节），绑定筛选与Scope。错误返回Error，不返回成功空页。QueryOptions.MaxReceiptCount=0..10000，按持久回执序号取最后N项，空数组不能改变Snapshot已证明阶段；查询取消/读取坏与NotFound区分。

Observe是瞬时投影，不是审计/完整状态日志；订阅上限来自Options，每订阅有界Channel。事件只带ID/Revision，无载荷/秘密；慢消费者积压时合并最新Revision并发RefreshRequired，通知遗漏不影响Store。ServiceGeneration+EventSequence识别重启，事件序号不充当业务序号。观察者异常/取消只取消订阅；UI据Query/List重新同步，当前授权失效立即结束订阅。永久回执只能从Store读，不以事件“未看到”推断未执行。

Receive从受信连接上下文和RawBytes有界解码，缺MessageId/消息类型/必需字段拒绝；`ConnectionIdentity/SourceNamespace/Generation`与宿主路由、当前能力精确核对，解析器不能创造业务身份。生产Inbox唯一键是Scope+Endpoint+SourceNamespace+MessageId，**不含连接generation或映射版本**；版本/generation是被核对的内容。同键同原消息回原OperationId/回执，不再Apply；同键异原内容Conflict。连接重投允许新连接上下文但不能改已存原内容/映射解释，须先按原身份与授权路线对账。分区序号在独立会话域验证，不作为跨代去重键。

接纳与处理异步分开：Receive返回Persisted只表示本地Inbox确认点；协议层可据已批准ACK政策确认传输，不返回业务Applied。下游Application能力有幂等+查询时调用Apply并在Unknown后查原ID；没有该能力仍可只读Replay，生产入站拒绝IT-CAP-001。跨Store与Application不假设全局事务；Application已提交而本Store写回失败时保持Unknown并查原receipt，禁止再次调用Apply。

Recover(ReconcileOnly)只持租约查原端点/原Application；已完成只回读，未能证明结果保持Unknown，不发新消息。Recover(RetryProvenSafe)只针对已排空的Unknown/DeadLetter/明确未发送待办，CAS核对原身份、原载荷/版本、期限和当前授权；Unknown须ProvenNotApplied或端点经批准的同键幂等重投能力，命令仍先查原操作。业务Rejected、Succeeded、已取消不允许通用重投；内容修改是新意图与显式更正关联。新恢复RunId拥有自己的资源生命周期，原回执/尝试数永久保留，不重置总自动重试预算；需要扩大预算须宿主批准新Profile并明确迁移，不能重复点“重投”无限续命。

### 4.6 可选投影根端口（Core公开契约，无WPF类型）

以下namespace仍为 `Asun.Modules.IntegrationTransport`，由宿主实现；Core服务不创建根，不默认选择实现。§10 ProcessRootOwner实现此接口；Wpf控件只依赖这个公开接口，不引用测试Hosting类。

```csharp
public readonly record struct ProjectionOwnerId(Guid Value);
public sealed record ProjectionBudget(long MaxResidentBytes, int MaxTasks,
    TimeSpan CloseTimeout);
public enum ProjectionCleanupStatus { Released, Retained }
public sealed record ProjectionCleanup(ProjectionOwnerId OwnerId,
    ProjectionCleanupStatus Status, bool Accepted, TransportError? Error);
public interface IProjectionRootOwner
{
    bool TryReserveProjection(ProjectionBudget budget,
        out IProjectionLease? lease, out TransportError? error);
    bool TryGetProjection(ProjectionOwnerId ownerId, out ProjectionCleanup? receipt);
    Task<ProjectionCleanup> JoinProjectionAsync(ProjectionOwnerId ownerId,
        TimeSpan timeout, CancellationToken ct);
}
public interface IProjectionLease
{
    ProjectionOwnerId Id { get; }
    void RegisterResource(object resource);
    Task<T> InvokeAsync<T>(Func<Task<T>> launch, CancellationToken waitToken);
    Task<ProjectionCleanup> CloseOrRetainAsync(Func<Task> closeProjection,
        TimeSpan timeout);
}
```

TryReserveProjection在任何枚举器/CTS/Query/Dispatcher工作前原子预留独立投影槽、bytes、MaxTasks和专用关闭worker，失败返回false/IT-QUEUE-001，零副作用。Budget.bytes为1MiB..根的投影总上限，MaxTasks=1..根上限（示例16），CloseTimeout=1s..24h；不能用host槽代替投影槽。成功时根已强持lease（Accepted=true），直到Released才归还。资源登记槽在此一次预留（最多16个拥有者/枚举器/CTS/有界buffer容器），RegisterResource只消费预留槽、不能在已构造资源迟到时拒收；超过已声明资源布局则拒绝创建。InvokeAsync先预留任务槽再在有界worker调用launch，worker前导真实返回Task后即可处理下一个launch，原Task与捕获buffer继续被根持有；否则长等待MoveNext占住唯一worker会阻塞Query。waitToken只限定等待。关闭信号/CancelAsync/DisposeAsync预留两个独立控制任务槽，业务MaxTasks满仍能关闭。异步返回/同步前导/迟到结果义务沿§10，不以包装Task作释放依据；Dispatcher被阻塞其原Task也由根保留。每调用真实finally归还任务槽，不删除仍在执行的原Task。

CloseOrRetainAsync先将lease关闭新工作，单次启动并登记closeProjection原Task；callback由控件实现快速关闭投影准入/退订信号，清敏感详情、安排独立投影CTS.CancelAsync，然后等待本绑定所有Query/List/枚举器/Dispatcher Task并DisposeAsync枚举器与自有buffer。它不调用服务Stop/Drain，不与服务生命周期形成环等待。callback抛错也必须记录并由根继续观察原任务/资源，不能把异常当释放。根并发汇合callback和原Task，确认无active且每个资源已真实释放才Released；timeout返回Retained/Accepted=true且有有效OwnerId，源/迟到资源继续被强持。无法确认Accepted不得返回成功移交；控件保留原lease、报退订失败并禁止重绑。JoinProjection有限观察同一关闭任务，不重启callback；TryGetProjection返回已接受Retained或最终Released回执，找不到/失效ID明确false，不能伪造Released。已Released保存有限无敏感回执至宿主查询确认后，不保留载荷；审计不是此临时回执。

## 5. 处理流程与事件顺序

### 5.1 出站顺序

1. 宿主检查授权、业务版本、范围和副作用政策，构造不可变 `DeliveryIntent`。
2. Core 有界检查字节数、摘要、Schema/Mapping、期限、分区序号和端点能力。
3. 全部交付通过IPersistencePort.RegisterAsync原子登记发件箱和操作身份；耐久确认才返回Persisted，不提供Volatile降级。
4. 获得有效租约后调用适配器；同一分区按序发送，跨分区可并行。
5. 按适配器结果保存传输/业务回执；响应丢失则为 `Unknown`，沿原操作查询。
6. 明确NotSent且可重试的失败超过总尝试预算才进入 `DeadLetter`；MayHaveReached/未知提交保持 `Unknown`，保留原身份、已证明阶段和对账动作。

同一操作的持久状态必须携带 `OperationId`、端点、租约代和单调 `Revision`；瞬时通知额外携带单调 `EventSequence`。唯一 Core 状态枚举为第 3.1 节的 `OperationState`。回执阶段 `ReceiptStage` 独立于资源生命周期，`TransportAccepted/BusinessAccepted/Applied` 是 `ReceiptStage`，不得混入 `OperationState`。建议顺序：

每个RunId生命周期为 `Created → Persisted → Sending ↔ RetryWait → Draining → Drained → ResourcesReleased → Completed/Rejected/DeadLetter/Cancelled/Unknown`，CancelRequested可在Persisted/Sending/RetryWait后进入。尚未领取的持久待办保持Persisted，服务排空不强行将待办改Unknown。成功Stage按证据保留，未知写DeliveryStatus.Unknown和新错误/回执；没有远端证据时才可Stage.Unknown。恢复新RunId以CAS递增Revision，旧run终态不覆盖。RetryWait前归还当前调用buffer/许可，退避不占发送/应用额度。

已接纳的操作即使在发送前确定失败或取消，也必须先停止新工作并完成 `Draining → Drained → ResourcesReleased`，再发布唯一的 `Rejected`、`Cancelled`、`Unknown` 或 `DeadLetter` 终态。尚未接纳且未取得租约的预检拒绝可走短路径；逻辑业务回执不等于本层资源已归还。

`RetryScheduled`、`Progress` 和诊断事件可合并，但不得覆盖正式回执。旧租约事件的代号小于当前有效代时丢弃并记录 `LeaseStale`，不能推进新状态。订阅者异常隔离于交付状态；回调不在 I/O 线程同步阻塞。终态 `Completed/Rejected/DeadLetter/Cancelled` 仅可在 `ResourcesReleased` 之后发布；若排空预算到期仍有工作，返回 `DrainStatus.NotDrained` 并保持 `Draining`，不发布 `Drained`、`ResourcesReleased` 或伪造终态。持久业务回执可先记录，但操作快照保持可查询且资源未释放的事实。

RequiredStage到达且本层资源归还后才更新DeliveryStatus.Succeeded；只有TransportAccepted且目标是业务阶段时为Pending，预算到期为Unknown，保留旧Stage。回执核对Scope/Endpoint/原ID/指纹/版本/Authority与证据摘要；多候选矛盾回执进入IT-CONFLICT-001隔离，不选最新或最高枚举。旧代真实结果可保留诊断证据，不能直接推进新代；当前run查询原端点收敛。

### 5.2 入站顺序

1. 适配器取得原始字节并在解码前限制压缩后大小、深度、对象/数组数和字符串长度。
2. 校验端点身份、协议版本、允许消息名、字段存在性、编码和摘要；保存原内容引用。
3. 有界解码取得MessageId后先ReadInboxAsync(Scope,Endpoint,SourceNamespace,MessageId)；存在时核原RawBytes/RawHash与来源身份，只回原记录，不按当前Mapping重建解释。不存在才完成当前Schema/Mapping校验并RegisterAsync，唯一约束再次防并发重复。
4. 固定映射版本、业务端口和原操作身份后，调用方应用端口采纳；Core 不写其业务表。
5. 回执分别投影为“已接收、已采纳、已拒绝、未知”；协议确认不代表应用已执行。

外部 `Source` 字符串不能授予权限。缺少可靠业务身份时不得用图像摘要、列表行号、相同时间或 SDK 自动 Guid 合并真实业务事件。批量消息按协议声明原子或逐项；逐项必须返回每项完整结果。

Inbox 已接纳但应用回执未知时，只查询原应用操作；读回已提交回执后保存原关联，不再次调用采纳写入。原字节的离线回放默认只执行有界解析/映射与预期结果比较，不打开生产端点、不写生产 Inbox/Outbox、不调用生产应用端口。生产受控重投使用原可恢复操作、原载荷/版本和当前授权；原操作已提交则只返回原回执。修正内容沿显式更正关系提交新请求，不能把离线验证成功当成重投许可。

### 5.3 场景驱动架构复审

下列场景是实现和审核的最小推演集。每个场景都要求记录输入快照、参数来源、处理顺序、输出、状态/错误、恢复动作和可判定验收；只有“日志看起来正常”不算通过。

#### S1 正常配置与执行

- **输入与来源：** 已授权的 `EndpointProfile`、不可变 `DeliveryIntent`、Contract/Schema 版本、Mapping 版本、凭证引用和存储能力；端点/容量/顺序来自版本化配置，载荷摘要由调用方提供并由 Core 重算。
- **处理顺序：** 校验身份/期限/能力 → 校验字节和摘要 → 持久登记 → 领取带代号租约 → 适配器发送 → 保存传输和业务回执 → 发布快照/通知。
- **输出：** `DeliverySnapshot`、阶段回执、可查询 `OperationId`；`BusinessAccepted` 仍不产生调用方质量或设备结论。
- **状态/错误：** `OperationState=Created/Persisted/Sending/Draining/Drained/ResourcesReleased/Completed`；成功业务回执另记 `ReceiptStage=BusinessAccepted`。任一步的权限、版本、摘要错误分别为 `IT-AUTH-001`、`IT-VERSION-001`、`IT-VAL-001`。
- **恢复与验收：** 相同输入重复调用只返回原操作；回读的摘要、Mapping、Revision 与原记录一致，且第二次没有外部发送。

#### S2 空输入与部分成功

- **输入与来源：** 空载荷、空批次、批量中一项缺字段/超限/摘要冲突；`BatchMode` 来自批准 Profile，不能按调用者意图临时改变。
- **处理顺序：** 先检查批次和项级上限 → 逐项完整验证 → `Atomic` 在持久化前整体拒绝；`PerItem` 为每项独立登记，成功项再领取租约。
- **输出：** 空载荷只有AllowEmptyPayload=true才可发送；空批次无副作用拒绝；逐项返回ItemDeliveryResult.CommitStatus；未接纳项State=null，不伪造持久Rejected操作。
- **状态/错误：** 缺少必需载荷或空批次为 `IT-VAL-001`；批量超限为 `IT-VAL-002`；一项失败不能把整批映射为 `Completed`。
- **恢复与验收：** `Atomic` 失败重试前必须修正整批；`PerItem` 只查询/重试失败项的原 `OperationId`。验收要求能证明没有半批幽灵记录，也没有丢失已持久化的成功项。

#### S3 歧义与错误输入

- **输入与来源：** 重复字段、允许别名同时出现、缺 `MessageId`、不一致 `Sequence/Partition`、非法 UTF-8/日期、未知 Schema/消息类型、来源声明与认证连接不符。
- **处理顺序：** 先保留原字节/摘要（受容量和隐私政策约束）→ 有界解析 → 检查字段存在性和 token 类型 → 核端点身份/允许模型 → 冲突检测 → 才能生成映射请求；禁止“最后一个字段覆盖前一个”。
- **输出：** `IT-PARSE-001`、`IT-CONFLICT-001`、`IT-VERSION-001` 或 `IT-SEC-001`，附字段路径、原始位置和脱敏诊断引用；不交应用采纳端口。
- **状态/恢复：** `Rejected`，或写入不作为 `OperationState` 的受限诊断记录；不重试确定性错误。修正输入需新消息/新映射关系，不能复用同一身份塞入新字节。
- **验收：** 同一原字节重复解析结果稳定；两个冲突别名始终拒绝；大整数不转 `double`；缺时间偏移不套本机时区；原消息缺失与空字符串不混淆。

#### S4 超大输入与高并发

- **输入与来源：** 接近/超过 `MaxPayloadBytes` 的载荷，压缩炸弹，深层嵌套，多个端点和分区同时涌入，慢消费者及突发重连。
- **处理顺序：** 在完整分配或解压前检查压缩前/展开后大小、深度、元素数和字符串长度 → 按总字节/条数/端点/分区上限排队 → 每分区按序、跨分区受 `MaxConcurrentSends` 限制 → 资源不足立即背压。
- **输出：** `IT-VAL-002`（输入本身超限）、`IT-QUEUE-001`（队列满）或 `IT-RESOURCE-001`（内存/磁盘/句柄不足）；已持久化项保持可查询，未持久化项明确未接收。
- **恢复与验收：** 下游恢复后按原顺序继续；不得丢弃最早项、无限扩容或以提高线程数掩盖内存压力。测试需在峰值并发下证明租约、buffer、连接和回调均归还。

#### S5 损坏、截断与退化信道

- **输入与来源：** TCP 半帧/错误长度、TLS/签名失败、消息校验摘要不符、连接抖动、带宽下降、远端 429/限流、长尾响应。视觉“噪声/遮挡”不在本模块解释为图像缺陷；它们只映射为上述传输退化。
- **处理顺序：** 适配器先做帧长/编码/完整性检查和协议认证 → Core 判断错误发生在发送前还是发送后 → 发送前确定失败可按策略重试；发送后且结果不可证明时转 `Unknown`。
- **输出：** `IT-PARSE-001`、`IT-NET-001`、`IT-NET-002` 或远端业务错误；不生成伪造的业务接受。
- **恢复与验收：** 可查询的端点使用原 `OperationId` 查询；不可查询的 `Command` 保持 Unknown 并要求调用方对账。半帧不会触发业务回调，迟到的旧回执因租约/Revision 校验被丢弃并记诊断。

#### S6 取消、超时、native/适配器排空

- **输入与来源：** 在解析、持久化、领取租约、网络写入、等待回执和关闭阶段收到 `CancellationToken`；适配器可能没有真正的 abort 能力。
- **处理顺序：** 标记 `CancelRequested` → 停止接受该操作的新工作 → 若适配器支持取消则等待确认，否则隔离连接/调用上下文并禁止复用 → 等待 I/O、native 回调和租约结束 → 保存 `Cancelled` 或 `Unknown`。
- **输出：** `IT-CANCEL-001` 只表示本层取消完成；网络写入已发生但结果不明时必须是 `Unknown`，不得返回 `Cancelled` 掩盖远端副作用。
- **恢复与验收：** Drain关闭接纳/领取、RequestClose、等待源任务、归还资源；超时只停止调用方等待，后台仍Draining/Isolated。迟到回调核RunId/LeaseGeneration/Revision，不提前释放内存。

#### S7 资源上限与长期运行

- **输入与来源：** 连续数小时/数天运行、磁盘接近满、队列长期积压、连接泄漏、死信增长、凭证轮换和时钟跳变。
- **处理顺序：** 周期采集水位/句柄/连接/租约/回调数 → 达到预警阈值停止对应端点接收或转背压 → 达到硬上限返回明确错误 → 按保留策略归档/清理已无引用诊断，不能删除未完成操作。
- **输出：** 健康快照、积压和水位指标；资源不足为 `IT-RESOURCE-001`，容量满为 `IT-QUEUE-001`，凭证轮换失败为 `IT-AUTH-001`。
- **恢复与验收：** 下游恢复/空间释放后恢复同一队列；长稳测试证明无静态状态串扰、无计数溢出、无租约 ABA、无未退订回调和无界日志增长。时钟跳变只影响期限诊断，不重排已有事件。

#### S8 持久化、崩溃窗口与版本修订

- **输入与来源：** 发件箱登记前崩溃、写入后未 fsync、已发送但回执未落盘、Inbox 去重写入与应用采纳之间崩溃；Schema/Mapping 修订和 `Revision` 并发更新。
- **处理顺序：** 写入不可变载荷/摘要 → 达到明确耐久确认点 → 原子登记操作与初始 `Revision=0` → 领取租约并 CAS 更新 Revision → 外部回执按期望 Revision 写入；跨数据库/blob 不假设全局原子。
- **输出：** 每个断点都能区分“未持久”“已持久未发送”“发送结果未知”“已回执未通知”。写入冲突为 `IT-STORE-001` 或 `IT-LEASE-001`，不得用空查询推断未发送。
- **恢复与验收：** 重启首先读取原操作/租约/回执，再决定继续、查询或进入 Unknown；同一 `OperationId + PayloadHash + Mapping` 才能复用。持久化适配器若不能提供原子唯一登记和 CAS，阻断生产实现。

读取超时、存储不可用、记录损坏、摘要/关联失配必须返回 `IT-STORE-001` 或 `IT-CONFLICT-001`，不得折叠成 `NotFound`、空队列或“未发送”。只有权威存储成功完成查询并明确证明不存在时才能报告未找到；错误恢复后仍查原身份，不创建替代操作。验收分别注入不存在、读取失败和已提交回执损坏，三者结果必须可区分，后两者无新发送/采纳。

#### S9 升级、回退与在途修订

- **输入与来源：** Core/协议适配器 N→N+1、Mapping 旧→新、在途旧操作、备份恢复、回退到旧二进制。
- **处理顺序：** 停止新入队并排空 → 固化运行/Schema/Mapping/适配器版本和租约代 → 对在途操作继续使用其原版本 → 对新操作启用新 Profile → 运行兼容性和历史查询检查。
- **输出：** 兼容操作继续原状态；不可读取的新格式为 `IT-VERSION-001 + Unknown`，保留原始数据，不删除或重写；修订内容必须新 `OperationId` 或显式更正关系。
- **恢复与验收：** 回退不回滚已持久事实；恢复后查询原操作，只有外部幂等和权限再次通过才受控重投。验收覆盖旧 worker 迟到回调、Mapping 变更在途不变、备份恢复重复投递和旧版本无法读取新 Schema。

涉及同一业务分区的连接 generation 更换时，先停止旧连接的新工作并实际排空，再以持久租约/CAS 围栏旧 writer，核对原 Inbox/Outbox、回执与未决副作用，最后启用新 generation。无法证明排空或对账完成时保留隔离，不启动竞争消费者。协议会话序号可按协议规则重建，但不能重置业务高水位、幂等身份或历史回执；不靠换分区/新 GUID 绕过未决消息。Host 提供换代协调和授权，本 Core 不复制源项目的业务恢复准备或审批 API。

#### S10 无 UI、可选 UI 与第二消费者

- **输入与来源：** 无 UI Host（MES 互联服务）和第二无 UI Host（线体/外部系统连接）分别提供端点 Profile、持久化和适配器；可选 WPF 只提供投影快照和命令意图。
- **处理顺序：** 两个 Host 都直接调用 Core 的 Validate/Enqueue/Query/Drain；UI 只能调用同一 Core，不得持有连接或事实写权；关闭 UI 只退订投影。
- **输出：** 两个消费者得到相同状态/错误/回执语义，但可有不同端点 Profile、队列容量和语言；第二消费者不得复制 Core、Outbox、Inbox 或状态机。
- **恢复与验收：** 在不启动视觉产品和不加载 WPF 的情况下完成正常、重复、未知、重启、死信和受控重投；两个 Host 的配置/取消/缓存相互隔离。UI 慢订阅者或异常不得阻塞发送线程。

#### S11 不支持能力与明确边界

本模块不支持：没有幂等或查询能力的未知副作用自动重发；没有持久化确认的“可靠交付”承诺；动态任意协议/类型加载；跨实体全局顺序；替调用方做业务字段补全、实体绑定、质量判断或设备安全互锁；把原始视觉句柄、数据库连接或厂商 DTO 作为公共契约。遇到这些输入必须返回 `IT-CAP-001`、`IT-VERSION-001` 或 `Unknown`，由调用方/人工对账处理。

## 6. 状态、错误码与重试语义

### 6.1 状态语义

| 状态 | 进入条件 | 允许动作与终态 |
|---|---|---|
| `Created` | 仅在内存形成请求 | 可验证/拒绝；未持久化关闭后不声称可恢复。 |
| `Persisted` | 发件箱/InBox 达到持久确认点 | 可领取、查询、排队；不代表已发送。 |
| `Sending` | 有效租约且适配器调用中 | 取消只停止本层等待；远端可能仍在途。 |
| `Rejected` | 可证明的校验/权限/业务拒绝 | 不自动重试；需新内容/新授权才可新操作。 |
| `Unknown` | 超时、断连、响应丢失且无法证明结果 | 查询同一操作；有副作用时禁止盲重发。 |
| `RetryWait` | 明确可重试的暂时错误 | 仅保留原身份/载荷，受次数、期限和容量限制。 |
| `DeadLetter` | 已证明未发送/未应用的可恢复失败耗尽预算，或明确未产生副作用的永久技术失败 | 保留证据，人工受控重投只能复用原意图或创建显式修正请求。 |
| `CancelRequested/Cancelled` | 尚未产生外部副作用的取消 | 不回滚已提交事实；迟到回执仍按原操作处理。 |
| `Draining` | 当前run停止产生新工作并回收在途资源 | 超时保持此态/隔离；未发送持久待办不因此变Unknown。 |
| `Drained` | 已接纳操作的适配器调用、回调和队列工作真实退出 | 进入资源归还阶段；不得再接受该操作的新工作。 |
| `ResourcesReleased` | 本操作拥有的租约、缓冲、连接引用和回调上下文已归还 | 之后才可发布唯一交付终态。 |

`TransportAccepted`、`BusinessAccepted` 和 `Applied` 只在 `ReceiptStage` 中记录；它们可以在 `Sending` 或 `Unknown` 之后被查询补齐，但不能替换 `OperationState`。`Rejected`/`Unknown` 在两个枚举中含义不同：`ReceiptStage` 表示回执结果，`OperationState` 表示本地生命周期终态；实现必须同时保存两者，不能用一个枚举字段代替另一个。

### 6.2 错误码候选

错误码是稳定分类，不携带凭证、完整载荷或堆栈给远端。`Retryable` 只表示本层可以按策略再次观察/发送，不能替调用方决定副作用重试。

| 代码 | 类别 | 默认可重试 | 语义 |
|---|---|---:|---|
| `IT-VAL-001` | Validation | 否 | 必填字段、范围、摘要或类型无效。 |
| `IT-VAL-002` | PayloadLimit | 否 | 字节、深度、字段或批量规模超过上限。 |
| `IT-AUTH-001` | Authorization | 否 | 端点、用途、作用域或凭证无权。 |
| `IT-CAP-001` | Capability | 否 | 适配器未声明所需协议/查询/幂等能力。 |
| `IT-CONFLICT-001` | IdentityConflict | 否 | 同操作/消息身份对应不同关键内容。 |
| `IT-VERSION-001` | VersionMismatch | 否 | Schema、Mapping、端点能力或期限不兼容。 |
| `IT-QUEUE-001` | QueueFull | 是（背压解除后） | 达到字节/条数/分区上限，不能丢弃旧事实。 |
| `IT-NET-001` | TransportUnavailable | 是 | 连接、DNS、TLS 或 broker 暂不可用。 |
| `IT-NET-002` | TransportTimeout | 未知 | 请求是否到达未知；先查原操作。 |
| `IT-BUS-001` | BusinessRejected | 否 | 外部业务明确拒绝；保留远端代码和原因。 |
| `IT-LEASE-001` | LeaseStale | 否 | 旧 worker/旧代回调不能推进当前租约。 |
| `IT-STORE-001` | PersistenceFailure | 未知 | 持久状态未确认，不回成功；恢复后按原操作查询。 |
| `IT-CANCEL-001` | Cancelled | 否 | 本层取消已完成；不表示远端已撤销。 |
| `IT-RESOURCE-001` | ResourceExhausted | 是（受预算） | 内存、磁盘、并发或句柄不足。 |
| `IT-PARSE-001` | MalformedMessage | 否 | 编码、语法、字段存在性或允许模型失败。 |
| `IT-SEQUENCE-001` | SequenceGap | 否（需补齐/对账） | 缺口、乱序容量/期限或同序号冲突阻断分区。 |
| `IT-LIFECYCLE-001` | ServiceUnavailable | 否 | 未启动、停止中或隔离实例不接纳新工作。 |
| `IT-SEC-001` | SecurityViolation | 否 | 签名、来源、重放窗口或策略校验失败。 |

每个错误实例还应包含 `OperationId`/`MessageId`（若已有）、阶段、端点、可重试理由、下一动作、首次/最近发生时间和脱敏诊断引用。

### 6.3 顺序、重连与退避的确定路线

PerPartition主路线为持久游标+单分区在途，不靠多个Channel消费者“自然有序”。出站序号域绑定Scope/Endpoint/Partition，入站会话序号域额外绑定受信ConnectionIdentity/generation；跨代去重仍用消息来源键。同sequence不同ID/原字节冲突，重复消息不消耗新sequence；Unordered不承诺顺序。

RejectGap在登记前返回IT-SEQUENCE-001；BufferGap允许有界未来项但不可领取，缺项达到RequiredStage并完成资源归还后才推进分区头。等待项计入容量；MaxReorderItems/GapTimeout到达则阻断分区，不跳号、不清最早项或补造消息。前序业务拒绝/DeadLetter/Unknown同样阻断后续；宿主修正/协议明确处理才解除，Core不提供Skip按钮。对应Store游标更新必须和Snapshot/回执CAS在同一事务。

明确NotSent且Retryable时，第k次失败后上界B=min(MaxRetryDelay, InitialRetryDelay×2^(k-1))，先饱和运算。抖动为B×(0.5+0.5u)，u来自SHA-256(OperationId小写D格式ASCII+4字节大端k)前8字节无符号大端数/2^64；用于可复现分散，不用于密码。RetryAfter有效时取两者较大；超过MaxRetryDelay则暂停该端点并返回限流原因，不截短远端限制。期限不足不重投。MaxAttempts包含首次，不因重连/人工恢复归零；MayHaveReached先查，不被Retryable标记自动发送。

每端点唯一连接Owner串行Open；失败以同一退避政策有界重连，不并发创建重复消费者。握手/心跳只改连接健康，重连先排空/围栏旧代，不重置业务游标。线路退化只影响网络恢复/背压，不降低检测质量或变更业务参数。

## 7. 取消、超时、资源与线程

- `CancellationToken` 只表达调用方停止等待或停止本层工作的请求。Core 必须等待当前 I/O、解码和适配器回调真正结束或确认不可再回调后，才能释放缓冲区、租约和连接。
- 超时不是回滚。若请求可能已到达远端，状态为 `Unknown`，使用原 `OperationId` 查询；没有查询/幂等能力时保持 Unknown，交给调用方对账。
- `DrainAsync` 先禁止新 `EnqueueAsync`，再停止领取新租约，最后等待在途调用和回调。`DrainTimeout` 到期时只释放已有独立完成证明的资源；仍可能被 I/O、适配器回调或远端调用使用的缓冲、连接和租约必须隔离并继续保留，持久操作和远端未知状态沿原 `OperationId` 查询，返回 `NotDrained`，禁止复用或伪造已排空。
- 每个模块实例拥有自己的队列、取消源、事件订阅和缓存；两个实例不能共享当前端点、客户、Json 设置或认证状态。
- I/O 使用 `async/await`；CPU 密集的摘要/规范化可在线程池执行；不得阻塞 UI 线程或 I/O 接收线程。ObserveAsync不保证UI线程；Wpf包装层通过Dispatcher投影，生产I/O不执行UI回调。
- `ReadOnlyMemory<byte>` 的借用/复制期限必须在 Contract 中注明。Core 不把原生网络缓冲或 SDK handle 越过适配器；持久化前必须复制到拥有方或获得独立租约。
- 队列同时按总字节、端点、分区和外部应用在途数背压。队列满返回 `IT-QUEUE-001`，不静默丢弃、覆盖或降级为内存队列。

停止信号须独立于凭证/能力解析器的取消回调：先关闭接纳/领取门，适配器在排空中按目标网络库的安全关闭语义关闭实际 socket/channel 以解除阻塞，再等待发送、接收、解析任务及回调结束，最后归还资源。关闭连接不等于释放仍被任务使用的 buffer。取消回调抛异常或阻塞不能阻止发出连接关闭信号；原解析任务仍须纳入排空。异步入口不得在返回 `Task` 前同步等待配置锁或解析器；实际 I/O 与等待均受调用方取消和有限预算约束。`StopAsync` 成功仍遵守§4.2的真实排空条件。

### 7.0 有界调用与启动代资源Owner

§10进程根在Factory前预留。Core自身按实例拥有有界源Task账本（不超过配置并发、独立控制槽与订阅上限），覆盖Store/Authority/Codec/Provider/Send/Apply/Query原Task和CTS.CancelAsync回调Task；WaitAsync超时仅使等待者返回，不从账本删除、不归还源任务仍占用的额度。Port getter、构造、RequestClose和异步方法前导必须快速无等待；不能满足时由预留的有界worker执行整个调用前导，账本保留worker和随后返回的原Task。专用关闭worker不能被业务调用占满；不能用无界Task.Run化解永久阻塞。

Start创建Starting generation并登记每个Open原Task及部分返回资源，失败走同一关闭任务；Stop在Starting也关闭该代准入门。Open迟到成功先登记资源，核代号/Closing后RequestClose与Drain，不再发布Started。多次Start/Drain/Stop共用原任务，不重复打开/清空账本。Restart仅允许Stopped且所有旧代任务/资源已归还后递增generation；generation溢出拒绝，不能回0复用。租约到期、权限撤销或取消不会取消所有权；旧结果保留证据而不推进新run。ACK未知与资源NotDrained是不同轴，业务Unknown能先保存，运行资源未排空不能发布伪终态。

根与Core额度分工：Options.MaxResidentBytes是完整实例预留，包含所有输入副本、编码/解码、原任务捕获和迟到资源；根只登记同一预留，不重复计费，跨实例预算为这些预留之和。存储队列额度不等于内存额度。未知大小资源只能在受限Adapter声明的最大驻留预留内打开；无声明拒绝，迟到资源也不能超限扩张。资源计费保持到最后真实引用解除。Borrow仅转移对象引用时不等价释放。

### 7.1 作用域隔离与恢复公平性

宿主从认证主体、设备身份和批准路由固定租户/站点/线体/端点作用域；外部报文只能声明待核对值，不能创建或扩大范围。VPN连通、IP白名单、端点在线均不能单独授权；跨机认证和 mTLS/TLS 策略由宿主提供，Core 不建身份或设备中心。中心不可用时保留本地持久事实及原版本，不使用过期缓存扩大权限；是否暂停生产或出站由宿主已批准策略决定，传输 Core 不承诺所有中心故障都不影响生产。

当前v0.2只在TransportConfiguration绑定TransportScope，不接受请求自报租户；单实例固定唯一授权作用域，持久记录、去重键、缓存、查询和诊断引用均隔离到该作用域。共享底层存储时须使用作用域命名空间，不能仅靠 UI 过滤。查询、载荷查看、导出和诊断访问由宿主检查当前授权，撤权后不能从旧缓存继续披露内容。多租户共用实例须先冻结显式作用域契约与端口，不能借 `PartitionKey` 或任意字符串偷渡授权。

调度顺序为：确认当前作用域/端点预算 → 将离线追赶与新请求纳入同一总预算及各作用域子预算 → 在可运行端点/分区间公平领取 → 分区内按原顺序发送。公平性以§7.3等权轮转和已采纳最大等待预算定义，不允许单租户热点、慢站点或积压追赶耗尽其它端点的连接、并发和内存；隔离后不另开无界恢复队列。重连采用有界退避和抖动，不能造成重复消费者。缺少可判定公平预算时不宣称性能达标。

### 7.2 未完成积压与历史保留

`MaxQueueItems/MaxQueueBytes` 统计仍待交付、重试或对账的未完成 Outbox/Inbox，包括 Unknown；终态已确认的历史记录退出积压计数，但其操作身份、去重摘要、回执、原映射/协议版本及证据引用仍受独立保留预算约束。死信仍保留原身份并按 `DeadLetterRetention` 管理，不能为减少积压把未知操作伪装成已完成。

存储维护顺序为：核对持久终态和引用 → 检查支持的重投/备份恢复窗口、保留策略及 Legal Hold → 只归档/清理符合条件的历史内容 → 核验原身份与回执仍可解析 → 更新独立历史水位。不得为腾容量删除仍需去重/对账的依据；内容可清理时仍须按支持窗口保留必要身份/摘要/回执或可验证归档。无法证明旧消息不会重新进入时保留去重依据，容量不足明确背压，不把重投当新消息。维护、保留和恢复窗口由存储 Owner/宿主 Profile 冻结，本模块不增设事实账本或自行定义删除 API。

### 7.3 调度、动态列表与维护的实现确定项

现Core字段没有权重表，故当前唯一调度冻结为**等权端点轮转**（不留“或加权”的实现选择）：Endpoint.Id按Ordinal建立不可变环，各Direction分开在各自并发额度内每轮每端点最多Claim一次；没有到期/受限/Unknown阻塞头的端点跳过，不消耗其它端点槽。可运行分区由Store按最早创建序号、PartitionKey Ordinal确定，每分区仅一个在途；新接纳与恢复待办走同一个created_sequence队列，不能给恢复另开优先队列。通知只加速唤醒，RecoveryPollInterval每轮补扫描；一个端点等待远端时不持全局锁。轮转正确性判据为所有可运行端点在各自槽可用时每完整轮都有一次领取机会，单端点无限重试不得剥夺其它端点机会；具体时延SLA仍由Profile给出。若将来要加权需单独修改契约，本轮不让实现者通过“性能优化”暗改公平政策。

§4.5操作List是**当前状态投影**，不等于§8.8保护引用总体。Store在首次List冻结当前max created_sequence上界，按(created_sequence,OperationId小写D)keyset；过滤状态在每次Query事务读取时成立，扫描间状态变化可能改变后续展示，UI用Refresh从首游标更新，不宣称一次List Complete是历史事实全集。Cursor明确Base64Url无padding，decoded bytes=ASCII域ASUN-IT-LIST-1+S(Scope.TenantId/SiteId/LineId)+Endpoint?/U32 Direction?/U32 Status?（每nullable B标志）+I64 upper_created_sequence/I64 last_created_sequence+S(last_operation_id)+H(SHA256前述bytes)，编码≤2048UTF8。解码checked长度/default/枚举/Scope/筛选exact、last≤upper、原operation存在或已批准归档可定位，不接受SQL/表名/任意OFFSET；hash只查损坏不授权，当前AuthorityPort必须通过，篡改有效游标也不能跨scope/滤条件取数据。首cursor=null；末页NextCursor=null；错误Empty+Error，不冒称成功零项。新行seq>upper本轮不进入，重新刷新可见；引用Resolver不使用此动态cursor。退役旧格式返回IT-VERSION-001/要求首查询，不吞错误。

A1-DB预定索引精确服务现查询：operation(K,created_sequence,operation_id)、operation(K,endpoint,direction,next_attempt_utc,created_sequence)及partition(K,endpoint,direction,partition_key)，lease已有PK/CAS，entity_reference按§8.8 K与完整keyset投影、reference_head按K唯一。所有Scope/tenant谓词在可信statement内；状态筛选不是另建全表常驻缓存。phase=Open可聚合一次全集refs，Page不得聚合COUNT/SUM；实际PG查询计划/索引成本由隔离负载测量，不能因索引名称存在宣称性能达标。本轮不做自动partition DDL；按Host采纳保留/规模Profile由IM046提供批准迁移包，经IM066维护角色实施expand→数据验证→读切换→旧写者fence→contract，Factory零DDL，旧Schema/codec保留到全部原Operation/Unknown可回读且迁移门通过。Unknown/去重/history维护与已有§7.2/8.6/14同一Owner，不提供“清空队列/跳过分区”API。

## 8. 适配器设计与可借鉴实现

### 8.1 适配器边界

每个协议适配器负责连接建立、协议编码、协议级 ACK/错误、能力声明和连接生命周期；不负责业务事实、质量规则、全局重试或设备安全。序列化适配器必须固定版本和字段存在性，禁止使用任意类型激活或共享可变静态设置。认证适配器只返回短期使用的凭证句柄/引用，不把密钥写入日志、包或 UI。

已配置认证时，凭证绑定精确端点与用途；来源异常、缺失、过期、撤销或错绑返回 `IT-AUTH-001`，不回退匿名或降低 TLS 校验。凭证读取有界且可取消，适配器不持久化秘密。撤销停止后续收发并关闭对应连接，已可能到达远端的操作保留原 Unknown/回执；脱敏错误不能携带原始密码或解析器异常中的秘密。真实部署凭证来源仍由宿主负责，工程夹具不构成生产授权。

对于 TCP 类协议，帧读取必须“先读固定长度头，再按上限精确读满”，在分配完整载荷前检查长度；并发发送必须串行化或由协议明确支持多路复用；心跳只证明通道存活，不产生业务回执。协议若没有幂等查询能力，`Command` 的超时必须保持 Unknown。

### 8.2 只读参考

`../../references/project-snapshots/AsunControl/20261004/original/ClassLibrary\TcpCommon.cs` 的 4 字节长度头、最大帧限制和 `ReadExactAsync` 可作为边界读取参考；`TcpClientEx.cs`/`TcpServerEx.cs` 的心跳、发送锁、取消后关闭连接可作为资源生命周期参考。其 `AutoSendFeedback`、事件字符串、自动重连和 TCP ACK 不是本模块业务语义，缺少持久发件箱、幂等登记、租约代、死信和 Unknown 恢复，禁止直接复制为 Core 实现。

HALCON 消息句柄能力仅作为历史背景；本模块不读取或依赖 AsunImage 源码，不引用 `HMessage`/`HObject`，也不把它们作为传输 Contract。若未来需要视觉载荷，必须由目标消费项目的 `ImageLibDotNet` 公共适配器先形成版本化、可序列化引用。

### 8.3 版本化协议能力与撤销

第4.4节已定义AdapterCapabilities；它与受信EndpointProfile绑定以下事实，不另建ProtocolCapabilityDescriptor或签名Registry：

| 声明组 | 必须绑定的事实 |
|---|---|
| 身份与版本 | protocol ID、标准/wire 版本、transport、client/server/上下游角色、适配器版本及包/入口摘要；不能只写“支持CFX/Hermes”。 |
| 功能与限制 | 明确消息集合、可选功能、编码、认证模式、帧/消息及展开上限、顺序、ACK含义、查询/幂等/离线能力和不支持项。 |
| 能力证据 | 声明、代码实现、标准符合性、真实互操作、客户认证/批准及当前启用分别记录，证据精确绑定版本/角色/范围；连通、loopback或模拟通过不代替其它层级。 |

宿主提供当前受信能力与撤销来源，Core/适配器只消费，不签发批准或自行建立密钥/Registry。启用条件按对应客户/协议 Profile 要求的证据判定，不把所有协议强行置于一种认证流程。`Validate` 仅使用已注入的本地不可变快照，不新增同步网络解析。

启动/恢复及实际 encode/decode/发送前核对当前能力、安装实例、版本/摘要和撤销状态；解析返回后若配置代已改变，旧结果不能成为新工作的准入依据。已返回的适配器实例不能绕过后续撤销/卸载；撤销、换包或未知能力立即停止新工作，以 `IT-CAP-001`/`IT-VERSION-001` 保留原因并执行§7排空。在途操作固定原版本，已有发送/回执事实不因撤销抹掉，不能偷偷换适配器继续发送。恢复需重新核对当前能力与原未决操作，不能从 Enabled 字段或旧缓存推导授权。

若后续选择 XML/Hermes 适配器，须精确声明 XML profile。[.NET 10 XmlReader 官方说明](https://learn.microsoft.com/en-us/dotnet/api/system.xml.xmlreader?view=net-10.0)规定其遵循 XML 1.0；删除或改写 XML 声明不能证明 XML 1.1 字符/换行语义兼容。适配器应拒绝未声明版本、DTD和外部实体；本页不因此宣称已实现 Hermes 1.0.4、CFX 2.1 或其它协议。CFX 字段存在性、原字节和固定源码证据直接复用 `DEV-PLT-013 §8`，不重新引入源项目 SDK/AMQP 依赖或迁移其事件子集。

### 8.4 已复用研究与选择依据（固定版本）

.NET runtime v10.0.0 commit `60629d14374c56f1cb51819049ad1fa529307f8d`，MIT；已定向读取[Channel源码](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Threading.Channels/src/System/Threading/Channels/Channel.cs)、BoundedChannel.TryWrite及BoundedChannelTests容量/丢弃反例，本地原件位于 `.work/full-development-prep-20260927/research/dotnet-runtime/src/libraries/System.Threading.Channels/`。BoundedChannel.cs SHA256=`4798673d97ee37741287c70b7f017b5f962b956b1a9e214b9089e0940a4ee406`，测试SHA256=`765025b2722caed432f1ccbe7bdefb8be7750ef1274791778950cdcbfb16dc70`。不复制runtime源码、测试或依赖；Core调用BCL Channels。上游测试依赖xUnit/Microsoft.DotNet.XUnitExtensions，本轮未运行。

[官方Channels说明](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)和源码支持：BoundedChannelFullMode.DropWrite可让TryWrite返回true却丢掉新项，故业务调度采用Wait模式+TryWrite失败明确背压、AllowSynchronousContinuations=false。Channel只放OperationId通知，不承担持久确认；通知满/漏由Store有限轮询重新领取，不能“channel写成功=Persisted”。事件投影合并可丢，但生产载荷不可丢。

[RabbitMQ 4.1 confirms官方说明](https://www.rabbitmq.com/docs/4.1/confirms)明确publisher confirms与consumer acknowledgements相互独立，deliveryTag属于channel；本页只采纳确认阶段不能当业务幂等/Applied的边界，不引RabbitMQ包，也不把AMQP0-9-1规则套到CFX AMQP1.0。CFX SDK2.1.1/wire2.1、commit `880255d2f7380f340f56b243a51d99f2136bdae3`、Apache-2.0来源与实际CFXEnvelope/JsonConvert/AmqpReceiverLink/OtherTests沿DEV-PLT-013 §8和REF-002 factory-input-source-research复用。缺字段自动生成身份、共享JSON设置和SDK测试不能证明本Core业务幂等；仅移植存在性/原字节/重复反例，不迁SDK或上游测试，未执行上游测试。

DevExpress25.2.3网页因访问挑战未读到正文，dxdocs本会话无可用工具；具体公开控件/属性依据本机官方XML `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`。Grid XML SHA256=`7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd`，Charts=`2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0`，Docking=`b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f`，Core=`cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196`，PropertyGrid=`0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9`。Grid.Core XML核DataViewBase/DataControlBase属性；Docking SaveLayoutToXml(string)/RestoreLayoutFromXml(string)只用于受信宿主布局。PropertyGrid.ReadOnly文档矛盾以§9真编辑反例验收。XML只证明公共声明/官方说明，不证明WPF运行、三语、UIA或渲染通过，不下载替换既定程序集。

### 8.5 A1-DB：消费IM-066公开Runtime的唯一数据库接线

本节冻结本模块持久队列的技术注册与事务映射，不设计产品表、不写工单/质量/设备事实。唯一上游为[IM-066 storage-database 0.3.1-prep §6～7](../storage-database/DEVELOPMENT-GUIDE.md#6-公开集成契约module-api-contract-v03-的-io-部分)的已接收C1端口：namespace `Asun.Platform.StorageDatabase.Contracts`（以下C#别名SD），Runtime哈希入口 `Asun.Platform.StorageDatabase.Runtime.StorageRequestHasher`。注册/原事务/读取/原操作生命周期依据§6.1～6.3/7.2；物理实现由IM-066的PostgreSQL+Npgsql包负责。共享数据库不降级SQLite、不另建连接池/ORM/驱动入口，图像/点云/原始测量数据不入bytea。

本模块独立Adapter工程为 `src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Storage/Asun.Modules.IntegrationTransport.Storage.csproj`，net10.0、namespace `Asun.Modules.IntegrationTransport.Storage`，只引用本Core与IM-066 Contracts/Runtime；不引用产品、Simulator或Npgsql。测试仍用§12唯一Exe，受测Storage Adapter显式引用；真实PG由IM-066后端隔离夹具提供。Root仍归Host，此Adapter借用已创建的IStorageDatabase，不Dispose/Stop共享Runtime。

```csharp
using SD = Asun.Platform.StorageDatabase.Contracts;
public sealed record DatabasePersistenceOptions(long MaxHistoryBytes,
    long MaxHistoryItems, int MaxMutationSlots, int MaxPageEntries,
    TimeSpan ExecutionBudget, TimeSpan WaitBudget);
public sealed record DatabasePersistenceOwnership(Action<int> ReserveResourceSlots,
    Action<object> RegisterResource, Action<DatabaseMutationRef> RememberMutation);
public enum DatabaseAssetKind
{
    Schema, InputCodec, ResultCodec, Statement, Resolver,
    Validation, Binding, Catalog, Owner, ReferenceCatalog
}
public sealed record DatabaseAssetProjection(SD.VersionRef Version,
    DatabaseAssetKind Kind, ImmutableArray<byte> Bytes);
public sealed record DatabaseMutationRef(SD.OperationIdentity Identity,
    SD.VersionRef Binding);
public sealed record DatabasePersistenceDrain(bool ResourcesReleased,
    int ActiveCalls, int OpenSessions, ImmutableArray<DatabaseMutationRef> Unresolved,
    TransportError? Error);
public sealed record DatabaseMutationObservation(DatabaseMutationRef Mutation,
    SD.OperationQueryResult Observation, bool ExecutionResourcesReleased);
public sealed record TransportDatabaseRegistration(
    SD.StorageBindingCatalog Catalog, SD.StorageOwnerRegistration Owner,
    ImmutableArray<SD.StorageBindingDescriptor> Transactions,
    ImmutableArray<SD.StorageBindingDescriptor> Reads,
    SD.StorageReferenceCatalog References,
    ImmutableArray<DatabaseAssetProjection> Assets);
public enum DatabaseReadKind { Health, ByOperation, ByInbox, List, Statistics }
public sealed record DbRegisterPayload(SD.VersionRef Schema,
    RegistrationRequest Request, ImmutableArray<DatabaseEntityReferences> EntityReferences,
    ImmutableArray<SD.ObjectRef> References)
    : SD.IOwnerStoragePayload;
public sealed record DbClaimPayload(SD.VersionRef Schema, ClaimRequest Request)
    : SD.IOwnerStoragePayload;
public sealed record DbRenewPayload(SD.VersionRef Schema, LeaseToken Lease,
    TimeSpan Duration) : SD.IOwnerStoragePayload;
public sealed record DbCasPayload(SD.VersionRef Schema, StoreUpdate Update)
    : SD.IOwnerStoragePayload;
public sealed record DbReleasePayload(SD.VersionRef Schema, LeaseToken Lease)
    : SD.IOwnerStoragePayload;
public sealed record DbReadPayload(SD.VersionRef Schema, DatabaseReadKind Kind,
    TransportScope Scope, OperationId? OperationId, EndpointId? Endpoint,
    string? SourceNamespace, MessageId? MessageId, DeliveryFilter? Filter)
    : SD.IOwnerStoragePayload;
public sealed record DatabaseEntityReferences(OperationId OperationId,
    ImmutableArray<SD.ObjectRef> References);
public interface ITransportDatabaseReferenceMapping
{
    SD.VersionRef Version { get; }
    ImmutableArray<DatabaseEntityReferences> ValidateAndGetEntityReferences(
        ImmutableArray<StoredOperation> operations, int maxReferences);
}
```

唯一实现类 `DatabasePersistencePort : IPersistencePort, IAsyncDisposable` 公开构造为
`DatabasePersistencePort(TransportConfiguration configuration, SD.IStorageDatabase runtime, TransportDatabaseRegistration registration, Func<SD.CallContext> getCurrentContext, ITransportDatabaseReferenceMapping references, TimeProvider timeProvider, DatabasePersistenceOptions options, DatabasePersistenceOwnership ownership)`。
所有参数必填、构造无I/O；公开附加方法为 `Task<DatabasePersistenceDrain> CloseAsync(TimeSpan timeout, CancellationToken ct)`、`Task<DatabaseMutationObservation> ReconcileMutationAsync(DatabaseMutationRef mutation, CancellationToken ct)`、`ValueTask DisposeAsync()`。Close/Dispose仅关本Adapter准入、释放本Adapter所有原Session/任务，不能Stop Runtime；超时保留原关闭Task/原Session并由根确认接收。Reconcile只调用Runtime.QueryOperationAsync，不重新Execute，不删除数据。

注册包工厂为 `TransportDatabaseRegistrationFactory.Create(TransportConfiguration configuration, SD.StorageScope storageScope, SD.StoreRef store, SD.StorageInputLimits limits, DatabasePersistenceOptions options, ITransportDatabaseReferenceMapping references, string referenceAuthorityId)`。输出Catalog/Owner/§8.6的11条描述符加§8.8引用快照1条（共12条）、5个mutation InputCodec与2个Read InputCodec（共7个）、1个ResultCodec；namespace与Adapter相同。每个Codec均为本模块实现已知公开IStoragePayloadCodec/IStorageResultCodec，exact PayloadType与上表对应；Version/Schema/StatementCatalog资产由本模块可信静态定义生成VersionRef(Id,2,SHA256实际投影字节)，不得用零hash、占位值或来自客户端的Schema。工厂不创建数据库、不迁移、不安装注册包。Host的IM-066 configuration resolver将此Catalog原样放ResolvedStorageConfiguration.Bindings，Owner并入References.Owners，RuntimeConfiguration.OwnerBindingCatalog与Catalog.Version exact匹配；可信IM-066 BackendFactory按同Statements VersionRef解析本模块参数化映射包，不能让请求注入SQL/delegate。IM-066具体A1 StatementCatalog加载/PG实现须由其原Owner按上游A1接口接收，不能在本模块猜一个未公开的“注册SQL”方法。

OwnerKey固定 `integration-transport`。storageScope Tenant/Site/Line必须逐分量等于configuration.Scope，StationId/DeviceId为Host显式注册的服务身份，**不从endpoint补造**，不拿空值或通配符当全站；Context.Store与store的id/generation/profile exact匹配，getCurrentContext每次取当前已授权引用，禁永久缓存首次caller。同一个Store可托管两Host，但两份注册Scope与权限/配额明确给出；同业务Scope的技术服务身份可不同，但不得借Station/Device更换扩大Outbox去重键。DB实体键使用Store/Generation+TransportScope三分量，RLS/绑定额外核当前完整StorageScope在注册集合中，tenant条件和Site/Line过滤不可省略。

options有效域：MaxHistoryBytes=1MiB..1TiB、MaxHistoryItems=1..10000000、MaxMutationSlots=1..64、MaxPageEntries=1..500；0<WaitBudget≤ExecutionBudget≤Options.OperationTimeout，且≤IM-066 Runtime.MaxOperationTime。注册最大条数沿Batch的10000，canonical字节/命令数不得超过注入SD.StorageInputLimits及IM-066 Profile；预算不够在登记/事务前拒绝，不拆Atomic批次、不放宽。Root先预留实例预算与所有mutation/session登记槽，ownership.RememberMutation在Execute之前强持原MutationRef，记不住则不进入存储副作用。

references是受信任、无I/O的Owner映射端口，先验证元数据报文/Schema，再按每个OperationId返回明确DatabaseEntityReferences，数组须和输入操作一一对应、无重复，所有引用完整且已封口耐久；不得把图像本体、base64图片或原始2D/3D放数据库，也不得把看不懂的引用当Empty。注册payload在Canonical内保存每个实体映射（DbRegisterPayload.EntityReferences字段位于Request之后/References之前），References为按ObjectKey排序的完整并集；两者核对，注册payload持这些精确References，Codec.GetReferences只读canonical内的它们并与RegisteredTransactionRequest.References完全核对；IM-066负责Publish/GC线性化与同事务Owner引用。只传合成M/7b7d的两个Host使用确定的 `SimulationMetadataReferences(SD.VersionRef version)`（本Adapter测试namespace，非Simulator），其ValidateAndGetEntityReferences只接受M/Schema1.0、两个ContentType=application/json、载荷精确7b7d、无任何对象引用，返回每个OperationId各一条DatabaseEntityReferences(id,ImmutableArray.Empty)；其它报文拒绝IT-VERSION-001，不当通用元数据判定器。真实消息的ObjectRef/Schema映射属于相应Owner/协议准入，但本端口和事务传递不能待客户来设计。

### 8.6 A1-DB注册目录、技术表与原子确认点

输入codec canonical域为 `ASUN-IT-DB-INPUT-1`，结果域为 `ASUN-IT-DB-RESULT-1`，均ASCII无终止字节；原语沿§3.4。输入先U32类别（Register=0/Claim=1/Renew=2/CAS=3/Release=4/Read=5），再编码下表固定tail（引用快照类别6沿§8.8）；结果先U32同类别。类别0..5随后编码PortStatus、nullable TransportError、业务结果按下表类型（Read先另U32 DatabaseReadKind）；类别6不带PortStatus/TransportError，固定为ReferencePageResult的SnapshotId(S)、ReferenceEpoch(I64)、Population.Hash(H)/TotalEntries(I64)/TotalEntryBytes(I64)、StartSequence(I64)、U32(Entries.Count)+SD canonical每entry、Next?（B存在+§8.8 Cursor）、Complete(B)。Phase=Open成功Entries=Empty/StartSequence=0/Complete=false/Next=首cursor，Phase=Page成功严格遵循§8.8；DB外层失败按SD.OwnerReadResult失败形状，不编码伪成功tag6。数组数量U32、按请求顺序逐项，哈希为32byte，byte[]用I64长度+原字节；期限/TimeSpan均I64 ticks。ResultCodec.Validate在commit前检查完整union/结果上限/身份与引用，Decode只读不可变bytes，不能以当前Profile改旧结果。失败/空查询同样按Schema编码，禁止JSON任意对象或序列化CLR Type。

Payload.Schema由注册Binding绑定并核exact VersionRef，不进入本payload canonical尾再重复编码；它已在IM-066完整StorageRequestHasher的Binding描述中绑定。DbReadPayload尾的固定顺序为Kind,Scope,OperationId?,Endpoint?,SourceNamespace?,MessageId?,Filter?（五个nullable）；Filter固定Endpoint?,Direction?,Status?,Cursor?,PageSize。属于SD的VersionRef/ObjectRef/Scope等嵌套值复用IM-066 §6.3/6.4的公开canonical规则，不把SD域的字节序/版本Hash改成本模块规则；本模块对象沿本节big-endian编码。

本payload独立小Golden（不代表完整SD请求信封）：Scope=t/s/l，DbReadKind.Health(0)、其余五字段null为46 bytes；ByOperation(1)、OperationId=00000000-0000-0000-0000-000000000001、其余四字段null为86 bytes。原语与字段生成以下hex，Schema在本payload中不自Hash：

```text
Health46: 4153554e2d49542d44422d494e5055542d31000000050000000000000001740000000173000000016c0000000000
SHA256: 30345cbd9cb014521365fbe3c9834f6a055bebbc0237e36733fef81378f6e18e
ByOperation86: 4153554e2d49542d44422d494e5055542d31000000050000000100000001740000000173000000016c010000002430303030303030302d303030302d303030302d303030302d30303030303030303030303100000000
SHA256: 2e98364bc986749b875d0c90000266bef384a00bc726c40ed3434ce792183eaf
```

资产投影字节与创建拓扑只按§8.9，Owner不含References/Catalog VersionRef；此处不保留另一个生成顺序或Hash方案。全部当前A1-DB资产修订统一2，实际字段/参数均入对应投影；小Golden是revision1语法夹具，不能代生产目录版本。物理实现包需另外exact绑定本Statement manifest，不声明SQL代码已运行。

| Binding Id（本轮A1-DB资产revision2，未发布）/用途 | PayloadType/tail与结果 | 注册语义 |
|---|---|---|
| it046.db.register / Production | DbRegisterPayload：RegistrationRequest,EntityReferences,References；结果RegistrationResult | Serializable，一批单事务；AllowEmptyBatch=false |
| it046.db.claim / Production | DbClaimPayload：ClaimRequest；结果PortResult<ClaimedOperation> | Serializable；租约领取事务 |
| it046.db.renew / Production | DbRenewPayload：LeaseToken,Duration；结果PortResult<LeaseToken> | Serializable；同代续租CAS |
| it046.db.cas / Production | DbCasPayload：StoreUpdate；结果PortResult<DeliverySnapshot> | Serializable；状态/回执/游标/配额一事务 |
| it046.db.release / Production | DbReleasePayload：LeaseToken；结果PortResult<bool> | Serializable；只释放同代租约 |
| it046.db.health / Query | DbReadPayload：Kind,Scope,其余null；结果PortResult<StoreHealth> | RepeatableRead、read-only，不写缺失health/schema |
| it046.db.read-operation / Query | Kind,Scope,OperationId，其余null；结果PortResult<StoredOperation> | RepeatableRead；不存在成功返回NotFound |
| it046.db.read-inbox / Query | Kind,Scope,Endpoint,SourceNamespace,MessageId，ID/Filter=null；结果PortResult<StoredOperation> | RepeatableRead；返回来源首次OperationId |
| it046.db.list / Query | Kind,Scope,Filter，其余null；结果PortResult<StorePage> | RepeatableRead；有限页/绑定cursor |
| it046.db.statistics / Query | Kind,Scope,其余null；结果PortResult<QueueStatistics> | RepeatableRead；有限聚合 |
| it046.db.recover-read / Query | 与read-operation形状相同；只查原事实 | RepeatableRead；明确调用者恢复权限，仍零写入 |

五个mutation InputSchema Id分别为 `it046.db.input.register/claim/renew/cas/release`，Read InputSchema为 `it046.db.input.read`；InputCodec Id为相同Id加 `.codec`，exact CLR Type逐项对应上表，读取六个binding共享一个DbReadPayload codec，引用快照另用DbReferenceSnapshotPayload codec。ResultSchema为 `it046.db.result`、ResultCodec为 `it046.db.result.codec` 强类型union。12条Binding的StatementCatalog指向同 `it046.db.statements` 受信包，Catalog为 `it046.db.catalog`。PermissionKey写=`integration-transport.store.write`，读=`integration-transport.store.read`，恢复读还须Core原操作Query/Reconcile授权；Read PoolPurpose只能Query，QueryOperation由IM-066保留Recovery池负责，不伪造一个带写功能的Recovery Session。

描述符固定MinAffectedRows=0、MaxAffectedRows=注入limits.MaxBatchRows、MaxCommands=1；每个绑定通过一个可信参数化CTE语句完成全部本模块表变更与RETURNING结果，不由请求上传过程/SQL。实际修改行计数由写集按operation/inbox/run/receipt/lease/partition/quota逐表checked求和，不能只取最外层SELECT的行数；此计数作为注册映射结果校验项与IM-066 affected-row核对。上界超过MaxAffectedRows或canonical/result超MaxBatchBytes先拒绝Atomic整体；PerItem仍逐项独立事务。IM-066自身route/receipt写入由其后端负责，不混入Owner的affected-row预算。自动whole-transaction MaxRetries=0，RetryDelay采用已验证InitialRetryDelay，ServerLockTimeout与ServerStatementTimeout均等于options.ExecutionBudget且>0；本模块不外层无限重试/重复ExtendWaitBudget。以后批准DB serialization失败重试须保持完整原MutationIdentity和单调deadline；commit Unknown不得用serialization规则重投。Statement包所有值用位置参数，表名/列名来自固定包，客户端的Owner/Schema/字段名不能拼SQL。

以下表属于**IM-046技术Schema `it046`**，由本模块Owner映射拥有，不访问/修改IM-066私有operation_route/operation_receipt或其它产品表。IM-066通过自己的事务实现写技术mutation回执及对象引用；本模块只经公开Runtime QueryOperation读取。每表公共键前缀K=(store_id,store_generation,tenant_id,site_id,line_id)，身份相等按.NET Ordinal且不归一化；需要字符串排序的SQL使用§8.8固定UTF16大端投影，不将PostgreSQL默认/C排序等同于.NET Ordinal，tenant RLS+完整scope predicate；runtime无DDL，Schema创建/迁移必须由获准IM-066迁移角色加载本模块固定迁移包。

| it046表/键 | 必需列及权威 | 事务/恢复义务 |
|---|---|---|
| operation PK(K,operation_id)，UK(K,created_sequence) | endpoint,direction,original_request_fingerprint,完整StoredOperation canonical（原Profile/Capability/Mapping/原bytes/decoded均在闭包）、当前Snapshot列revision/run_id/state/delivery_status/stage/attempt_count/may_have_reached/resources_released、created_sequence、next_attempt_utc、payload_charge_bytes、history_charge_bytes | Register唯一写入原请求/版本；CAS只更新合法快照/nextAttempt。不可覆盖原payload/hash/Mapping或历史run；新run终态保存独立run记录 |
| inbox PK(K,endpoint,source_namespace,message_id)，UK(K,operation_id) | original_request_fingerprint、first_operation_id | 和operation同登记事务；唯一键不含generation/Mapping/Station/Device；异raw保留Conflict，不在表内覆盖 |
| run PK(K,operation_id,run_id)，FK operation | 本run不可变完成快照/业务结论、revision范围、真实资源释放事实、原错误/诊断引用 | 当前run未Released不能写“已完成”；恢复新RunId不覆旧终态 |
| receipt PK(K,operation_id,receipt_sequence)，UK(K,operation_id,receipt_id) | 完整ReceiptRecord canonical、阶段/Authority/证据摘要、generation | append-only；同ReceiptId同内容幂等，异内容Conflict；Snapshot已证明stage不能因分页为空倒退 |
| lease PK(K,operation_id) | worker_id,lease_generation,expires_at_utc；generation永不归零复用 | Claim/Renew/Release原子CAS，DB权威时间判过期；过期不证明资源释放，源Task仍属旧Root |
| partition PK(K,endpoint,direction,partition_key) | first_sequence,next_sequence、blocked_reason、当前头身份、gap_started_utc、future_item_count | 注册RejectGap/BufferGap、合法确认后推进cursor与snapshot同事务；Unknown/Rejected/DeadLetter阻断，不能跳号 |
| quota PK(K,scope_kind,endpoint_key) | scope_kind=Instance/Endpoint两值，endpoint_key实例固定技术哨兵不可与真实endpoint相混；pending_items/bytes,history_items/bytes,next_created_sequence、冻结limits/profilehash | 先锁实例再按Endpoint Ordinal锁行，再锁partition，再操作身份/lease，统一顺序；两层checked额度同事务预留/释放。Unknown计pending；真实已确认终态才转history，租约过期不转history |

StoredOperation/Profile/Snapshot/回执canonical不只存hash：Profile用§3.4完整配置字段+自身ProfileHash与完整Capability字段+Fingerprint；Intent用§3.4字段并在PayloadLength后存实际payload再PayloadHash；Inbound存§4.4全部原连接字段与rawbytes/hash；Decoded存MessageId/MessageName/Schema/Partition/Sequence/ContentType/applicationbytes/hash；Snapshot按§3.3所列完整21字段固定顺序；StoredOperation固定Scope/Profile/Outbound?/Inbound?/Decoded?/RequestFingerprint/Snapshot/Receipts/NextAttemptAtUtc。其余nested record明确采用§4.4当前冻结字段顺序（该序是v1编码表，不因以后C#成员重排改变），TransportOptions固定19字段顺序为MaxPayloadBytes,MaxQueueBytes,MaxQueueItems,MaxResidentBytes,MaxConcurrentSends,MaxConcurrentApplicationCalls,MaxAttempts,InitialRetryDelay,MaxRetryDelay,OperationTimeout,DrainTimeout,HeartbeatInterval,HeartbeatTimeout,MaxClockSkew,DeadLetterRetention,LeaseDuration,RecoveryPollInterval,EventBufferItems,MaxSubscriptions。Nullable有存在标志，Dictionary/任意对象不进入编码，ImmutableArray不排序，HashSet排序沿§3.4；加载严查长度/default/重复/枚举/引用/闭包一致。修改编码升Schema，不重算/改写历史hash。

Register事务先按同来源/ID读取已存在项（保持原ID/回执，不重新检查新接纳期限/容量），再在写集中验证所有指纹/原字节/配置/序号/checked新增额度；Atomic任一冲突返回全集Rejected且零新行，PerItem各自独立Storage事务但返回全部结果。同批新行的operation/inbox/初始run/partition/quota和**IM-066原Mutation技术回执**在一commit点；commit前不得报告Persisted。同ID hash相同但原bytes不同仍Conflict，不能只相信hash。SQL唯一冲突回读原键并比较，不把所有23505当重试。

Claim只选due+正确partition头的一条，在Serializable事务核quota/lease，锁定并递增generation；活跃lease返回不可领而非抢占。过期lease+may_have_reached=true只能领取作原操作对账，Core不得走新Send。发送前CAS提交may_have_reached=true、attempt+1/run/revision后才可外传；确认Unknown时不能Send。Renew核worker/代/当前DB时间与正Duration；Release只释放同代，不清Snapshot或SourceTask。CAS核ExpectedRevision、当前lease、合法Stage/运行迁移、append回执、future/partition游标和pending→history变更，一事务成功或全不动。任何COMMIT错误都不能由客户端猜RolledBack。

PendingBytes出站计Payload.Length，入站计RawBytes.Length+ApplicationPayload.Length（两个语义载荷各计一次，物理副本不重复计）；history计保存的实际canonical主行+run+回执bytes，checked总和，去重键/历史仍有显式限额。MaxHistory满返回IT-QUEUE-001，对历史不自动删；DeadLetter/Unknown按§7.2保留，不借TTL解除身份。List按created_sequence+OperationId稳定keyset，cursor包含冻结K/筛选、上边界created_sequence、last tuple与包版本，严格验证，不能OFFSET全历史、不能从客户端cursor推断授权；每页读一致、跨页不是全局Snapshot，删改已影响当前结果时返回明确冲突/刷新，不漏成成功空页。所有读取返回原Profile闭包，不借当前Profile重解释历史。Health明确核Schema/hash/角色能力与Durable声明，缺/错Schema=Unavailable，不建空表。DB租约UTC取事务内权威时点并固定本次now，不从本机TimeProvider获得跨进程租约权；本机TimeProvider只计算等待/排空deadline。

### 8.7 A1-DB公开调用、未知提交与有限关闭

1. Host先创建注册包，并通过自己实现的IM-066 IStorageConfigurationResolver/IStorageBackendFactory把Catalog/版本及Statement包接入。在任何StorageRuntimeFactory.CreateAsync前按§10根预留槽；Factory原Task、部分后端、迟到Runtime都登记到原Root。已创建Runtime传DatabasePersistencePort，供两个技术Host按不同Scope装配；共享Runtime由更上层Host唯一拥有，不由每个Core独占释放。
2. 每个IPersistence方法先冻结不可变payload/参数、取当前SD.CallContext，核注册Scope/Store/用途/权限和限额，再Runtime.OpenSessionAsync(new SD.SessionRequest(context,"integration-transport",Purpose),executionToken)。每次独立逻辑Session（单Session只允许一个在途操作），原ValueTask只AsTask一次并强持，Session返回即登记到Root；Open迟到成功先接管再Release。
3. mutation生成**新的技术事务身份**（不是新的IT业务OperationId）：Store/generation/完整Scope/OwnerKey、技术OperationId=受信任Host本次固定Guid D、IdempotencyKey=同Guid D；一个调用只生成一次，重查不换。构造SD.RegisteredTransactionRequest(context,identity,binding,payload,refs)，用本InputCodec.Encode得到独立canonical，再调用StorageRequestHasher.Compute(request,descriptor,canonical,limits)将identity.PayloadHash置为完整Storage hash。ownership.RememberMutation记下完整MutationRef，随后Session.ExecuteTransactionAsync。IM-066内部按公开RegisterAsync/route/CAS写耐久技术身份，**本Adapter不直接调用IStorageDatabaseBackend.RegisterAsync**，更不自己复制route账本。IT原OperationId和指纹在payload内保持不变。
4. 返回StorageTaskStatus.Completed且Result.Commit.State=Committed、正确ResultSchema/结果bytes与本输入绑定后，才解码为IPersistence的Ok/Persisted等结果。读取调用Session.ReadAsync(new SD.RegisteredReadRequest(context,binding,payload),token)，成功Schema/Bytes/References全部核对后解码；Fault/坏Schema/缺回执不变成成功/NotFound。Read失败返回Unavailable/Conflict/Cancelled等稳定错误；查询不执行原事务。
5. Execute返回Accepted/Running/Draining/DrainUnknown或等待超时：保留TaskHandle、原Task/Session/MutationIdentity；沿Runtime.GetTaskStatusAsync(new SD.TaskQuery(currentContext,handle),token)有限观察。CommitUnknown/没有确认原commit时返回PortStatus.Unknown（Register逐项CommitStatus.Unknown）并携原Mutation引用到DiagnosticRef，不盲重新Execute。权限拒绝/ResultExpired/读Unavailable与权威NotFound分开；NotFound不证明旧写者不会迟到，也不能许可新Send。
6. 原Mutation回查**只**走Runtime.QueryOperationAsync(new SD.OperationQuery(currentContext,originalIdentity),token)，即ReconcileMutationAsync；Committed精确重放原ResultSchema/bytes（Register会回原IT ID/Revision），RolledBack/Rejected保持对应失败，Unknown/InProgress仍Unknown。技术COMMIT已确认+本地未释放仍不是此调用Released。新实例重启从本技术表原IT操作/lease/may-have-reached读起，未决发送原ID对账；恢复只读不能复活原进程TaskHandle、重造业务ID、重放已有Apply/Send。原技术MutationId可由已持有的Root/脱敏诊断引用查询，不跨过程猜一个旧事务已回滚。
7. 每次真正finally安排Session.ReleaseAsync(new SD.ResourceReleaseRequest(currentContext,固定释放Identity,session.Handle),independentCleanupToken)，固定释放identity只生成一次，沿Diagnostics.GetResourceStatusAsync确认Released/ActiveOperations=0；Release的原Task仍登记，不循环重发Release/Dispose。仅Released后才Session.DisposeAsync归还本调用额；未完成转Root确认保留。单调用出错和cleanup出错分别保留，不覆业务结果。CloseAsync关新调用门、先发本地合作停止，再汇合所有原Open/Execute/Read/Query/Release任务；真实ActiveCalls/OpenSessions为0、SourceTask/reader/transaction已归还才ResourcesReleased=true。它不停止共享Runtime，Root在所有借用Adapter Released后由Runtime唯一Owner另行Stop/Dispose。
8. Root对RememberMutation/Session/原Task使用有界池，MaxMutationSlots满先背压；未知提交记录不能被诊断tombstone策略淘汰。外层WaitAsync、服务Stop、窗口关闭不证明事务/连接归池；迟到Committed结果仍写原operation证据且可查，不能丢弃。

Scope A/B数据库Host的唯一装配差异为完整TransportConfiguration/已注册SD.StorageScope/Context授权；其它均用本Adapter同一实现：CreateRegistration(A/B)+公开ReferenceResolver实例（注册包Factory返回后用Owner.ReferenceResolver、Owner及第12条Binding按§8.8构造）→各自受控Catalog/Runtime配置（本轮A/B各有Runtime；共享变体仅同一exact注册Scope/Store，不把两个不同Scope合并成未定义聚合Owner）→根强持Runtime并显式ReferenceResolver.BindRuntime→new DatabasePersistencePort(...registration,currentContext,references,clock,options,ownership)→§4 IntegrationTransport构造的persistence参数替换MemoryStore→原Start/Enqueue/Receive/Query/finally。Callback注入明确为ReserveResourceSlots=lease.ReserveResourceSlots、RegisterResource=lease.RegisterResource、RememberMutation=m=>{journal.Remember(m);lease.RegisterResource(m);}（该技术ref槽在生成前预留，登记不执行I/O），禁止静态捕获/让Adapter自己new Root。S1诊断Host仍使用MemoryStore，数据库Host不可把fake耐久=true当真实PG。

本节A1-DB内部注册/事务/读取/原Mutation恢复映射指导内容已由主控2026-10-11限定接收；IM-066具体A1 provider/StatementCatalog加载和真实PG部署/耐久/权限测试仍按该模块资格门，不把本Owner payload/Schema/SQL逻辑欠账转成客户物理门。A2尚未批准的客户协议仅阻断其wire/映射/互操作，不能阻断C1/C2/S1准备。

### 8.8 A1-DB受保护的完整Owner引用分页

沿IM-066现公开 `IStorageOwnerReferenceResolver.OpenAsync(OwnerReferenceSnapshotRequest,CancellationToken)`、`IStorageOwnerReferenceSnapshot.ReadAsync(long nextSequence,CancellationToken)` 和 `DisposeAsync()`，**页MaxEntries/MaxBytes不是整个Owner的条数/字节上限**。不通过一次读全集再切数组、不持有未经公开的Session事务/reader句柄。上游未公开跨ReadAsync事务固定快照API，本模块冻结每页独立只读事务+Owner引用版本不变验证，任何变化拒绝整次快照，不能混合总体。

#### 8.8.1 明确公开DTO、保护端口与构造

以下仍位于Storage namespace、仅用Core/SD/BCL；SD类型保持原签名，不替上游新增方法：

```csharp
public sealed record ReferenceScanLimits(long MaxTotalEntries, long MaxTotalBytes,
    int MaxPages, int MaxResidentBytes, TimeSpan ScanTimeout, TimeSpan CloseTimeout);
public sealed record ReferenceScopeKey(string StoreId, long StoreGeneration,
    string TenantId, string SiteId, string LineId);
public sealed record ReferenceKey(ReferenceScopeKey K, string EntityId,
    int EntityRevision, SD.Sha256 EntityHash, SD.ObjectKey ObjectKey);
public sealed record ReferenceCursor(string SnapshotId, long ReferenceEpoch,
    SD.Sha256 PopulationHash, long NextSequence, ReferenceKey? Last);
public enum ReferenceReadPhase { Open, Page }
public sealed record DbReferenceSnapshotPayload(SD.VersionRef Schema,
    SD.OwnerReferenceSnapshotRequest Request, ReferenceReadPhase Phase,
    ReferenceCursor? Cursor, ReferenceScanLimits Limits) : SD.IOwnerStoragePayload;
public sealed record ReferencePopulation(SD.Sha256 Hash, long TotalEntries,
    long TotalEntryBytes);
public sealed record ReferencePageResult(string SnapshotId, long ReferenceEpoch,
    ReferencePopulation Population, long StartSequence,
    ImmutableArray<SD.OwnerReferenceEntry> Entries,
    ReferenceCursor? Next, bool Complete);
public sealed record ReferenceFenceObservation(bool Protected, SD.StorageFault? Fault);
public interface ITransportReferenceFence
{
    ValueTask<ReferenceFenceObservation> CheckAsync(
        SD.OwnerReferenceSnapshotRequest request, CancellationToken ct);
}
```

公开Resolver构造固定为
`TransportDatabaseReferenceResolver(SD.VersionRef version, SD.StorageOwnerRegistration owner, SD.StorageBindingDescriptor binding, SD.StorageInputLimits inputLimits, ReferenceScanLimits scanLimits, ITransportReferenceFence fence, TimeProvider timeProvider, DatabasePersistenceOwnership ownership)`，
其 `Version` 为给定exact引用，`BindRuntime(SD.IStorageDatabase runtime, Func<SD.CallContext> getCurrentContext)` 只允许Host成功创建Runtime后显式一次绑定。所有参数必填，不从global取Runtime/Root/Clock。本切片Owner必须是本Factory产生的一个完整StorageScope/Store注册（对应单实例TransportScope），exact核对，额外未注册Scope/Store拒绝而非截取；因此完整Owner总体就是此注册域的所有存活实体引用，不能以页限额截断。跨Scope聚合Owner不在本轮绑定中，不用单scope Session冒充跨Store读取。未绑定Open为null+Unavailable，启动失败不是空快照。Resolver只借Runtime，Host拥有其Root与fence；Resolver不Stop共享Runtime。另有公开 `Task<DatabasePersistenceDrain> CloseAsync(TimeSpan timeout, CancellationToken ct)` 与 `ValueTask DisposeAsync()`：只关闭本Resolver新快照门，汇合全部原snapshot任务；未知释放继续由原Root强持，未结束不归还槽。

`ReferenceScanLimits` 必填、checked：MaxTotalEntries=1..long.MaxValue-1、MaxTotalBytes=1..long.MaxValue、MaxPages=1..int.MaxValue、MaxResidentBytes=4096..实例已预留MaxResidentBytes、ScanTimeout/CloseTimeout=1s..24h且≤相应Host/上游配置预算。没有客户端任意覆盖。Request.MaxEntries为1..500、MaxBytes为4096..min(inputLimits.MaxResultBytes,scanLimits.MaxResidentBytes)，实际页总bytes含header/Next/entry，不只算载荷。Snapshot最多1个在途页调用，本切片同一Resolver最多1个活动snapshot（构造固定，不留未定义并发配置）；页返回后调用者持有的页数组计入其自身有界消费额度，Resolver不缓存全部历史页。MaxTotalEntries/Bytes/Pages和ScanTimeout控制**整次扫描工作量**，超过为CapacityExceeded或TimedOut/非Complete，不能以截尾作全集。大库通过宿主采纳足够大的有限总预算分页扫描，不提高常驻内存到总库大小。零引用总体可以成功，但仍有header/保护核验。

ITransportReferenceFence的默认确定实现为宿主 `ObservedReferenceCoordinator : SD.IStorageReferenceCoordinator` + `BorrowedReferenceFence`，不进入Core/Simulator。完整构造分别为
`ObservedReferenceCoordinator(SD.IStorageReferenceCoordinator inner, int maxLeases, Action<object> registerResource)`、
`BorrowedReferenceFence(ObservedReferenceCoordinator coordinator)`。
代理只调用inner已有EnterAsync/ValidateAsync/PreserveAsync/ReconcilePublicationAsync/DisposeAsync，并转发原结果/错误。Enter成功时先将原request.Context/request.Identity/原lease.Token/原lease强持登记到有界map，登记失败在原Owner下真实Dispose后失败，不交无主lease；返回包装lease（实现原SD接口），GetStatus/Check/Renew代理原lease，Dispose只一次退出并登记原Dispose Task，不能直接移除未退出lease。成功Runtime唯一拥有该代理后端及其inner，Runtime排空后只调用代理Dispose，由代理一次Dispose inner；Host/Environment借用，不能在Runtime结束后再次Dispose代理/inner；它不生成token/fence、不作为第二权限事实权威。

Fence.CheckAsync用request.Barrier.Handle查已登记exact原token（所有字段/Store/Owner集合）与request.Owner/Catalog合法绑定；用原Context及原Handle调用**原lease.GetStatusAsync(new SD.ResourceQuery(originalContext,handle),ct)**，要求返回的SD.HoldStatus.Resource.Handle等于原Handle、Resource.State=SD.ResourceState.Open、Resource.Fault=null、Version非null且>0、ExpiresAtUtc非null且未到实际期限，并核token.Kind为Backup/BackupCut/GcPlan、原OwnerKeys/Stores覆盖、原Enter request.Context.Scope在Owner.Scopes中（token本身没有Scopes字段）、epoch/fence/refepoch未改变。此Check的原ValueTask、ledger lease和任务由Root保留，取消只停止等待，不Dispose调用者借出的Barrier。失联/Unknown/旧handle/expired/参数错配一律Protected=false+固定Fault。不能从当前epoch数字大、缓存true或GetTaskStatus推断保护；上游保持真正隔离/fencing权威，Owner的总体不变证明另由下节DB header实现，不从Token.ReferenceEpoch推断所有实体未变。

#### 8.8.2 唯一绑定、总体header与keyset算法

第12条 `it046.db.references` 仍为Query/RepeatableRead，exact payload上述DbReferenceSnapshotPayload，结果schema union类别6改为ReferencePageResult。Open/Page共享一个可信只读绑定，输入canonical在ASUN-IT-DB-INPUT-1+U32(6)后固定为：Request.Context.Scope、Context.Store（SD公开canonical）、OwnerKey、Owner.Scopes/Stores排序集合、Catalog、完整Barrier、MaxEntries/MaxBytes、U32(Phase)、Cursor?、Limits六字段（声明顺序）。Cursor单独采用本模块大端编码SnapshotId(S)、ReferenceEpoch(I64)、PopulationHash(raw32)、NextSequence(I64)、Last?；Last固定K.StoreId(S)/K.StoreGeneration(I64)/K.TenantId(S)/K.SiteId(S)/K.LineId(S)/EntityId(S)/EntityRevision(I32)/EntityHash(raw32)/ObjectKey的StoreId(S),Generation(I64),TenantId(S),StorageDomain(S),ObjectId(S)。Cursor只能由Resolver签发/保存在原snapshot，公开SD ReadAsync只传nextSequence不接受任意Cursor或SQL参数；篡改字段直接InvalidInput/Conflict。

新增本Owner技术表 `it046.reference_head`，PK=K，字段owner_reference_revision(long>0)、reference_catalog_hash(raw32)。任何会改变operation/run/receipt所持精确引用集合/EntityVersion/保留资格的Register/CAS/批准归档在同事务CAS递增此revision；不能只在有新ObjectRef时更新。refs维护为同事务 `it046.entity_reference`，PK=(K,entity_id,entity_revision,entity_hash,ObjectKey五字段)，存完整ObjectRef，另存不可变entity_version_bytes（按§8.6版本StoredOperation完整canonical），FK仅指operation(K,operation_id)，不能指向已被CAS覆盖的当前revision。同行EntityVersion.Hash必须等于这些实际版本bytes的SHA256；同实体/版本多Object引用共享同一不可变版本内容且计历史预算。EntityVersion.Id=原IT OperationId小写D、Revision=int且>0（超过int.MaxValue拒绝需显式schema升版，不截断），Hash=原不可变StoredOperation版本bytes的SHA256；ObjectRef不同完整描述同ObjectKey为IntegrityFailed，不任选一项。历史/Unknown/DeadLetter/LegalHold的仍存活引用保留在此关系中，不能为了GC主动删历史；删除仅原Owner已批准的事务，触发head递增。与SD.owner_object_reference在同事务核对应关联，DB提供技术持久操作/保护，IM-046拥有业务去重/队列语义，两Owner不合并。

**PopulationHash**使用ASCII域 `ASUN-IT-DB-POP-1` + OwnerKey(S) + Catalog完整VersionRef + 按Scope/Store全键排序的[StorageScope/StoreRef/owner_reference_revision/reference_catalog_hash]数组。含请求覆盖的每个已注册scope/store，缺行/Schema错/未知权威拒绝，不把缺行当revision0。所有版本只增不复用，防ABA；Hash不是从当前页算整体。引用总体按K的StoreId/StoreGeneration/TenantId/SiteId/LineId声明顺序→EntityId→EntityRevision数值→EntityHash字节→ObjectKey五字段（Generation数值，其余字符串）排序；所有字符串用.NET Ordinal的UTF16代码单元顺序，PG statement对排序字段采用固定UTF16大端bytea排序投影（不是数据库默认/C排序），同一函数用于WHERE元组比较与ORDER BY，空前缀先于非空，禁止文化比较/Unicode归一化，相同键只一entry；完整Object描述不同不得去重。ReferenceKey.EntityId及表entity_id均为原IT OperationId小写D；对外SD.OwnerReferenceEntry.EntityId为lowerhex(SHA256(ASCII域ASUN-IT-DB-ENTITY-1+K五分量依S/I64编码))+"/"+原OperationId小写D（固定101 ASCII bytes，须≤inputLimits.MaxIdBytes），EntityVersion.Id仍为原OperationId。固定域与完整K绑定，解码时从实际K重新核EntityId，不把hash当跨scope权限；完整K仍在cursor与关系键中。keyset只比较未拼接的强类型字段，不能用带长度前缀的hex字符串大小代替元组顺序。Sequence是**本快照流中的连续位置**从0，非表行号/业务序号，不从Guid大小造序号。

1. Open先预留snapshot/page/Session/原Task槽，生成受信Guid SnapshotId；核当前授权/fence。以Phase=Open、Cursor=null调用Runtime.OpenSessionAsync(Query)→Session.ReadAsync(RegisteredReadRequest)。一个只读statement在同事务读取全部header版本、COUNT完整refs及SUM精确entry canonical长度（checked）；不把所有entry返回内存。TotalEntryBytes只计完整SD.OwnerReferenceEntry编码（含Sequence），页header bytes另计实际总页开销；缺描述、负/溢出或总预算不足失败，Root真实清理后返回null+Fault。生成冻结PopulationHash/TotalEntries/TotalEntryBytes，不给fake empty/Partial成功。
2. Open成功释放该Session后返回snapshot，ReferenceEpoch**恒等请求Barrier.ReferenceEpoch**。首个cursor为冻结总体、NextSequence=0/Last=null；没有页证明前不报Complete，不持原数据库transaction跨页。每次Read调用前/后fence.Check，采用原固定deadline与新当前查询权限；Barrier释放/epoch/授权/实体head变化返回Empty、NextSequence=null、Complete=false、Fault，不沿旧snapshot恢复生产写。
3. 每页开独立Query Session，只读绑定在该事务先读取覆盖域的单调reference_head数组并计算PopulationHash，逐项exact核Open冻结的head/Hash；任一变化或缺行立即拒绝原快照，不重算COUNT/SUM后接续旧流。head完全相同时复用Open冻结的TotalEntries/TotalEntryBytes，**同一次SQL statement**仅沿索引读取key > Last的至多MaxEntries条，逐项编码后不超过MaxBytes（含所有header与Next）。多出1条只取键与编码长度作有界lookahead，不取完整ObjectRef/载荷；缓存上一页与构建新页/结果bytes/固定lookahead同时计MaxResidentBytes，总和不得超额，不能把每页MaxBytes当两个页各可用额度。不返回全表，不用OFFSET；索引/排序必须满足上述固定UTF16大端排序投影与生成key，不从任意输入拼列。无法容纳单项+header时CapacityExceeded，不能空非末页无限重试。Page.statement返回当前PopulationHash及head一致证明，不把未重新聚合的总计伪称新测量。COUNT/SUM完整总体仅在Open计算；正常页、最近页重读和最终尾页均不得无条件扫描全表重算总计，避免O(N×页数)。这一复用依赖所有影响引用总体的变更与单调head更新在同事务提交、禁止ABA；不放宽Barrier、授权、前后Hash及第4条累计/尾部核验。
4. 页Entries.Sequence严格为requested nextSequence+i、从冻结cursor.Last继续，Count不超过页限。NextSequence仅当未到尾时=起点+Count，必须严格前进；Complete=true**仅**已读条数=冻结TotalEntries、累计entry bytes=冻结TotalEntryBytes、无lookahead剩项、所有key严格增且前后fence/PopulationHash一致。Complete时NextSequence=null；空总体第一次Read(0)返回Empty/Complete=true。尚剩项返回非空/Complete=false，无法证明总数一致返回IntegrityFailed，不凑空尾页冒称完整。
5. 成功页实际bytes累计（含header/next）/entry总数/page数checked核ScanLimits，总deadline固定不因读页/重试续命；边界>=允许恰好完成，下一项超额拒绝。TotalEntryBytes是entry累计对齐目标，MaxTotalBytes额外包含所有页header，Open不能仅凭entry总计保证之后页开销仍有预算。MaxPages用于有限扫描，不规定一次最多N条就是整体上限。失败结果Empty/Complete=false/Fault，不交失败前半页，已返回页作为候选证据不得用于完整GC/备份直到整个流Complete。
6. snapshot严格顺序消费。同expected NextSequence重复调用（同一**最近已成功页**的起点）可返回缓存这一页且不再次计总数，但先重新核当前授权/fence/head；其它旧/未来seq拒绝。最多缓存最近1页（计驻留）；真正推进新页替换缓存，已Complete只允许最近页的同起点有限重读，不能开启第二流。外部只读页面不会隐式登记写操作/补引用。
7. 所有Session实际Release→ResourcesReleased→Dispose后才归还当前调用槽。DisposeAsync先关snapshot新Read门、独立取消源页任务并登记，再汇合原Open/Read/fence/Release/Dispose，释放缓存/Root槽；原SD Dispose无timeout参数，调用者有限观察但原Dispose Task继续强持。Root可查询原snapshot资源与有效OwnerId/保留回执，未Exited不得Released。取消后不留reader连接，原Barrier由调用者保持到snapshot Dispose真正结束，再按IM-066闭包/GC转换/释放其保护；snapshot不自己销毁借用Barrier，避免把“页读完”当整个备份闭包已保护。

#### 8.8.3 注册与验证端口保持

TransportDatabaseRegistrationFactory仍输出12条Binding、7个InputCodec、1个ResultCodec。ReferenceResolver/ReadValidation的VersionRef生成只按§8.9，不再用两种“先Owner或先Catalog”顺序。Resolver的构造/Runtime显式绑定沿§8.8.1；result codec必须核header/cursor/total/连续seq/Complete union，错误不变空总体。OwnerReadResult.References在Open为Empty；Page为本页Entries.Object按ObjectKey排序的精确并集（同Key异描述拒绝），Refs/Bytes共同计单页与驻留预算并核当前注册Scope/Store/Generation。payload tag6的GetReferences为Empty，因为Barrier/查询参数不是待发布对象；不把读结果引用注册成新写事实。ReadValidation资产代表隔离目标的只读Owner完整性校验，实际调用沿SD.IStorageDatabaseBackend.ValidateOwnerAsync；不新增SD方法或在运行时请求“注册SQL”。本Owner可信Statement manifest供Host backendFactory装配其已有IStorageDatabaseBackend，参数化实现包属于IM-066 A1实现边界；manifest及本Owner算法/字段在本页冻结，不能宣称未实现SQL/PG实际符合性。

断言：3条引用、MaxEntries=1三页seq0/1/2→Complete，仅驻留一页；该稳定总体扫描的完整COUNT/SUM聚合调用计数仅Open一次（最近页重读/末页不增加），页读取只核有限head和索引keyset；head变化拒绝旧快照且不靠重新聚合续流；空总体seq0Complete；页2前新增/移除/改EntityVersion或同Key异Object描述拒绝、不能将总数3改4续流；释放Barrier/权限撤销/epoch变化拒绝；第一项过MaxBytes明确CapacityExceeded；超总pages/bytes/deadline无假Complete；重复最近页不重复计量，旧seq/任意cursor拒绝；Fault/取消Read和Dispose原TaskRoot仍持有直到归还。真实PG statement、协调fence、RLS和大库代价须后续验证，此规格不替代运行资格。

#### 8.8.4 消费IM-066 0.3.1启动快照与同事务epoch

本增量只消费上游§6.1/6.7.3的确定接线，不改已接收公开DTO、12条Binding或§8.9资产/历史hash。注册工厂先在零backend IO阶段冻结全部Scope/Store/Profile、descriptor、嵌套数组及codec声明；按Binding.Version定位，再在该Binding内核exact PayloadType，不能把跨Binding共用封闭payload类型当重复。默认/重复/依赖缺失/同Version异声明或实例拒绝。Host保持所注入codec/resolver的唯一所有权，Version/Schema/PayloadType getter零IO且声明不可变；Storage Runtime先冻结同一目录再交PG工厂，不二次Resolve、热登记或请求补Owner。两个Host各自构造自己的完整引用范围目录；窄读目录不能用于全库闭包/GC。

Register/CAS在原Owner固定事务内变更operation、entity_reference、reference_head时，只读取上游A1已设置的transaction-local `current_setting('app.im066_reference_epoch',true)`（严格正Int64 E），不取Token.ReferenceEpoch作新提交界，也不另开事务分配epoch。Owner fixed SQL在原事务更新本Scope/K的head及完整引用；上游reference_authority→route/attempt→技术object/reference→本Owner领域行锁序保持。E、Owner行、精确引用与原技术receipt一起commit/rollback；Unknown沿原Mutation查询，零补写/零重分配。所有注册写事务包括References=Empty仍取此E；普通Read/List/Statistics/Reference Open/Page和Created=false重放不分配E。local GUC仅传技术上下文，不是授权或物理fence证明；缺失、非正值、修改或epoch耗尽在Owner变更前拒绝。Owner命令行数仅累计本statement实际Mutation，不能把上游epoch/receipt隐含写入算入现Binding Min/Max。

§8.8的Population.ReferenceEpoch仍等原Barrier.ReferenceEpoch；head/count/hash是该保护快照下的本Owner总体承诺，并非“当前最大epoch=本Owner未变”。已有有限head核验/keyset/累计尾部/前后Barrier检查全部保持。跨Owner无关epoch不能冒充本Ownerhead变更；本Owner新增/释放/改版本或同ObjectKey描述变化必须在同事务推动head。新增计划断言复用IT-T34/原隔离PG夹具：初始已提交e=7，成功Register E=8后同事务head/引用/receipt一致；下一CAS分配9后回滚，所有Owner变化不可见且原7/8历史可读；Read/Query不得读到可写local E，技术行数不加入Owner计数；commit响应丢失只查原Mutation。启动前修改注册声明/同Version换实例/使用只读Host目录作GC均拒绝，Factory零DDL。此处是规格检查，未运行PG/Runtime。

### 8.9 A1-DB资产投影、VersionRef与完整无环Golden

本节是资产**唯一**编码与依赖顺序，取代§8.6/旧§8.8的自然语言“规范字节”推断。它是IM-046资产摘要投影，**不更改SD请求信封或SD.ObjectRef canonical**。本资产采用§3.4大端原语：U32计数/enum、I32有符号int、I64计数/ticks、B单字节、S严格UTF8+U32字节长度、H raw32；V(ref)=S(Id)+I32(Revision)+H(Hash)，Revision>0；Scope=五个S按SD.StorageScope声明顺序，Store=S(StoreId)+I64(Generation)+V(Profile)。数组U32数量；集合按Ordinal key/数值升序去重，DTO字段列表按显式顺序不排序。禁止文件路径/异常文本/README/当前时间/Type.AssemblyQualifiedName/Marshal/raw结构作为Hash材料。

每个资产的外层bytes统一：
ASCII `ASUN-IT-DB-ASSET-1`（无终止/长度）+U32(Kind)+S(Id)+I32(Revision)+该Kind固定body。
Kind=Schema0/InputCodec1/ResultCodec2/Statement3/Resolver4/Validation5/Binding6/Catalog7/Owner8/ReferenceCatalog9。VersionRef=Id/Revision/SHA256**整个此bytes**；自身Hash不编码，Header.Id/Revision编码，子V完整编码。所有Kind均禁止未知值、default数组、无效UTF16、负预算、重复key/超过已注入限额。已有外部Store.Profile等V由Host取得其真实规范bytes并核Hash，未提供拒绝，不用zero/随机hash。

| Kind | body唯一字段/顺序（类型） |
|---|---|
| Schema | S(RootTypeToken), U32(TypeDefinitions.Count)，各定义按TypeToken Ordinal排序：S(TypeToken),U32(Members.Count)，各member按本指导已冻结record成员顺序：S(Name),S(TypeToken),U32(Rule)。Rule=0ExactRequired/1NullablePresence/2OrderedArray/3SortedSet。原子type tokens只取u32/i32/i64/bool/string/hash/bytes/time/utc/guid；bytes有I64长度+原值，容器token为array:T/set:T/nullable:T，named record token为本页全名或SD:全名。每个nested named record在TypeDefinitions有一次完整定义（递归图不可环），不以文件行号指类型；SD嵌套token明确采用SD canonical并定义成员原始顺序，此asset记录结构但不改其实际编码。 |
| InputCodec | V(Schema),S(ExactPayloadTypeFullName),U32(Algorithm=1 ASUN-IT-DB-INPUT-1),U32(PayloadTag=0..6),U32(ReferenceMode=0None/1DbRegisterEntityMapping/2ReferencePageParameters)。条数/字节有效上限由调用者inputLimits封装、Hash不绑定每次Encode(maxBytes)，不隐式读取全局Profile。 |
| ResultCodec | V(Schema),U32(Algorithm=1 ASUN-IT-DB-RESULT-1),U32(UnionTags.Count)+升序U32每tag（0..6）。结果Schema描述全部tag/字段，tag6是ReferencePageResult，不能只填OwnerReferencePage。 |
| Statement | U32(Entries.Count)，按BindingId Ordinal每项：S(BindingId),U32(OpCode),U32(Parameters.Count)，按位置各S(ParameterName),S(TypeToken)，U32(Tables.Count)+Ordinal S每表token，U32(Predicates.Count)+升序U32每predicate，B(ReadOnly),U32(CommitPoint=0ReadOnly/1AtomicWithSDReceipt)。OpCode=0Register/1Claim/2Renew/3CAS/4Release/5Health/6ReadOperation/7ReadInbox/8List/9Statistics/10RecoverRead/11References。Predicate闭集=0ExactStoreGeneration/1TenantRls/2RegisteredScope/3CurrentAuthority/4ImmutableIdentity/5ExpectedRevision/6LeaseFence/7PartitionHead/8Quota/9ReferencePopulation/10Barrier。 |
| Resolver | S(OwnerKey),S(ReferenceBindingId),U32(Algorithm=2ProtectedKeyset),S(OrderToken="K/EntityId/EntityRevision/EntityHash/ObjectKey"),U32(PageResultTag=6),U32(ScanPolicy=1FiniteWholeScan),B(RecheckBeforeAfter=true)。不含Binding/Catalog/Owner V；仅用稳定Id定位、Runtime创建后再exact核目录，消除循环。 |
| Validation | S(OwnerKey),U32(Algorithm=1ReadOnlyIntegrity),U32(Tables.Count)+排序S，U32(CheckCodes.Count)+升序U32；CheckCodes=0SchemaExact/1CanonicalHash/2OriginalIdentity/3ReferenceRelation/4NoMissingDescriptor/5HeadMonotone/6NoDispatch。无修表/重新发送。 |
| Binding | S(OwnerKey),U32(Kind),V(InputSchema),V(InputCodec),V(ResultSchema),V(ResultCodec),V(Statement),S(PermissionKey),U32(Purpose),U32(Isolation),I32(MinAffectedRows),I32(MaxAffectedRows),I32(MaxCommands),I32(MaxRetries),I64(RetryDelay.Ticks),I64(LockTimeout.Ticks),I64(StatementTimeout.Ticks),B(AllowEmptyBatch)。Kind/Purpose/Isolation取SD当前明确从0开始枚举，不按字符串改值；与SD.StorageBindingDescriptor字段一一对应、Version自Hash只在外层。 |
| Catalog | U32(Bindings.Count)+按Id Ordinal的V每Binding，U32(InputCodecs.Count)+按Id Ordinal的V每codec，U32(ResultCodecs.Count)+按Id Ordinal的V每codec。包含整个描述符已承诺的Hash，实际加载还逐字节重算Binding内容，不能只验表面Id。 |
| Owner | S(OwnerKey),U32(Scopes.Count)+按五分量Ordinal的Scope，U32(Stores.Count)+按StoreId/Generation/Profile.Id/Revision的Store，V(Resolver),V(Validation)。**不含Catalog/References V**，SD.StorageOwnerRegistration本身也无此字段。 |
| ReferenceCatalog | S(AuthorityId),U32(Owners.Count)，按OwnerKey Ordinal的V(OwnerAsset)。加载时把这些精确Owner值填SD.StorageReferenceCatalog.Owners，不发明SD.Owner.Version属性；OwnerAsset为本模块可追溯投影，SD目录只持真实registration值。 |

生产Schema Roots为§8.5公开payload/结果union，构造图来自本页冻结字段清单；本轮DbReferenceSnapshotPayload字段以§8.8为准，References参数Schema/codec/statement/resolver/binding/catalog/owner/reference目录等本轮资产统一revision2；未发布v1既有描述仅作历史读规格，不改旧hash。Schema的name仅类型全名（namespace.Type，无程序集版本），Member.Name精确属性名；实例Scope/Store、预算值不进通用结构Schema，它们进入Binding/Owner/当前请求。本目录工厂必须用显式Schema图初始化，禁止反射枚举不确定顺序。所有primitive/容器rule一致，nullable TypeToken须nullable:T且Rule=1，数组Rule=2，集合Rule=3，Required字段Rule=0；Schema图缺nested定义拒绝。ResultCodec.UnionTags必须等于对应结果schema所定义完整集合，不能接受未知tag。

Statement参数统一一个`payload`，TypeToken=对应InputCodec.ExactPayloadTypeFullName（位置$1），不是任意SQL字符串；参考分页Op11固定Phase/Cursor/ScanLimits都在payload中。Tables token带固定前缀it046.，精确集合按以下唯一表（只含Owner访问表，不含IM-066技术私表）：

| OpCode | Tables（实际编码按token Ordinal排序） |
|---|---|
| 0 Register | operation,inbox,run,partition,quota,entity_reference,reference_head |
| 1 Claim | operation,lease,partition |
| 2 Renew | operation,lease |
| 3 CAS | operation,run,receipt,lease,partition,quota,entity_reference,reference_head |
| 4 Release | operation,lease |
| 5 Health | 空集合，只受信Schema/role校验，不写 |
| 6 ReadOperation / 10 RecoverRead | operation,run,receipt |
| 7 ReadInbox | inbox,operation,run,receipt |
| 8 List | operation |
| 9 Statistics | operation,quota,partition |
| 11 References | entity_reference,reference_head |

完整Predicate集：所有op含0/1/2/3；写op含4，CAS含5/6/7/8，Claim含6/7，Renew/Release含6，Register含7/8；References含9/10。各Op仅访问该表精确集合，无任意表名或实现者另选表。Op0/1/2/3/4 CommitPoint=1/ReadOnly=false，其余0/true。RecoverRead与ReadOperation相同只读算法但Id/权限范围不同。

资产创建唯一拓扑：
**Schema → InputCodec/ResultCodec → Statement → Resolver/Validation → Binding → Catalog；Resolver/Validation与外部Scope/Store → Owner；Owner → ReferenceCatalog**。
Owner与Catalog无相互引用；配置装配最后同时绑定Catalog.Version和ReferenceCatalog.Version。允许Schema/Codec/Statement先并行内存计算，但加载V必须从上述已生成真实bytes取得；Resolver只绑定ReferenceBindingId，后校验catalog内该Id exact descriptor是否符合Op11/Schema/revision，不能偷偷引用其V成环。Factory输出registration新增 `SD.StorageReferenceCatalog References` 属性，完整资产表以 `ImmutableArray<DatabaseAssetProjection> Assets` 返回；类型为 `DatabaseAssetProjection(SD.VersionRef Version, DatabaseAssetKind Kind, ImmutableArray<byte> Bytes)`，DatabaseAssetKind取上表十值。Factory.Create参数增加 `string referenceAuthorityId`（1..128UTF8，Host明确提供）并按唯一顺序产生全部资产，所有descriptor/Codecs.Version/Owner.ReferenceResolver/ReadValidation/References/Catalog逐V exact对齐。

Golden如下是**完整小资产图**：单只读Binding、Schema原子string、scope=t/s/l/p/d、Store=q generation1 Profile外部p/revision1/hash=SHA256(empty)（外部真实bytes就是empty，仅合成夹具）、Owner=o、Authority=a；资产Id用s/c/r/j/x/v/b/k/o/z、revision全1，输入/结果共用Schema s，合法声明InputType=string为纯canonical夹具（不是生产DbReadPayload），codec算法1/tag5/refs0，Result tags=[5]；Statement Op5/只读/commit0、参数payload:string、无表、Predicates=[0,1,2,3]；Resolver owner=o/refBinding=b、固定algorithm/order/tag/policy，Validation无表/checks=[0,6]；Binding Read1/Query1/RepeatableRead1、权限p、row0..1/commands1/retries0、三个timeout均1tick、AllowEmpty=false。Catalog只列b/c/r，Owner带x/v，ReferenceCatalog带o。字段故意极小以可完整重建，不把此单Binding图当生产12条目录。

**Asset s：45 bytes；SHA256=dd92d0e8d8853ed517cbab99b802d30a72347950be7662115ce038ae52a97a1b**

```text
4153554e2d49542d44422d41535345542d310000000000000001730000000100000006737472696e6700000000
```

**Asset c：94 bytes；SHA256=bc0b35d087574018b6fadb516b3459888bbc503c73d3992aa9eb4f03d1e7d90c**

```text
4153554e2d49542d44422d41535345542d3100000001000000016300000001000000017300000001dd92d0e8d8853ed517cbab99b802d30a72347950be7662115ce038ae52a97a1b00000006737472696e67000000010000000500000000
```

**Asset r：84 bytes；SHA256=72381f048e2f15238e7a3a1228ba6af133b9643e6c906ad480b6e5b2738fa5fa**

```text
4153554e2d49542d44422d41535345542d3100000002000000017200000001000000017300000001dd92d0e8d8853ed517cbab99b802d30a72347950be7662115ce038ae52a97a1b000000010000000100000005
```

**Asset j：98 bytes；SHA256=1c2e1871d0a47d82c99231db2f227509aece6c1d0877de6065f93f243b12a85e**

```text
4153554e2d49542d44422d41535345542d3100000003000000016a000000010000000100000001620000000500000001000000077061796c6f616400000006737472696e670000000000000004000000000000000100000002000000030100000000
```

**Asset x：104 bytes；SHA256=44cdc18ef4b75078a83dea0b203b7f6da4cb0c010a543bf6fd6ca41b202ee493**

```text
4153554e2d49542d44422d41535345542d3100000004000000017800000001000000016f0000000162000000020000002e4b2f456e7469747949642f456e746974795265766973696f6e2f456e74697479486173682f4f626a6563744b6579000000060000000101
```

**Asset v：56 bytes；SHA256=c4a63148efb8dcced71a21c2cb95987dc3c55f1af7eb268556e8fd8896f85a08**

```text
4153554e2d49542d44422d41535345542d3100000005000000017600000001000000016f0000000100000000000000020000000000000006
```

**Asset b：299 bytes；SHA256=17a9224a00a24d06f9540090a1ee82c9a8b63e4439057915691e1e4bdb53d0f4**

```text
4153554e2d49542d44422d41535345542d3100000006000000016200000001000000016f00000001000000017300000001dd92d0e8d8853ed517cbab99b802d30a72347950be7662115ce038ae52a97a1b000000016300000001bc0b35d087574018b6fadb516b3459888bbc503c73d3992aa9eb4f03d1e7d90c000000017300000001dd92d0e8d8853ed517cbab99b802d30a72347950be7662115ce038ae52a97a1b00000001720000000172381f048e2f15238e7a3a1228ba6af133b9643e6c906ad480b6e5b2738fa5fa000000016a000000011c2e1871d0a47d82c99231db2f227509aece6c1d0877de6065f93f243b12a85e000000017000000001000000010000000000000001000000010000000000000000000000010000000000000001000000000000000100
```

**Asset k：166 bytes；SHA256=9fa0381bfe646301c37b0412e2dfa4141b92d6f91a0abea6a64400196fa2b5b7**

```text
4153554e2d49542d44422d41535345542d3100000007000000016b000000010000000100000001620000000117a9224a00a24d06f9540090a1ee82c9a8b63e4439057915691e1e4bdb53d0f400000001000000016300000001bc0b35d087574018b6fadb516b3459888bbc503c73d3992aa9eb4f03d1e7d90c0000000100000001720000000172381f048e2f15238e7a3a1228ba6af133b9643e6c906ad480b6e5b2738fa5fa
```

**Asset o：205 bytes；SHA256=64dde81e7549aa76941e15c61526fc5121fca700ca8560bafe7f55c3979099a6**

```text
4153554e2d49542d44422d41535345542d3100000008000000016f00000001000000016f0000000100000001740000000173000000016c000000017000000001640000000100000001710000000000000001000000017000000001e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85500000001780000000144cdc18ef4b75078a83dea0b203b7f6da4cb0c010a543bf6fd6ca41b202ee493000000017600000001c4a63148efb8dcced71a21c2cb95987dc3c55f1af7eb268556e8fd8896f85a08
```

**Asset z：81 bytes；SHA256=bb55a0cf9d74e34006e30d2caed08e4f0677fd5ddf52099c1b3a2420231950e9**

```text
4153554e2d49542d44422d41535345542d3100000009000000017a00000001000000016100000001000000016f0000000164dde81e7549aa76941e15c61526fc5121fca700ca8560bafe7f55c3979099a6
```


小Golden的全部V为上面资产真实SHA256，完整binding/catalog/owner/references已覆盖；测试按字段独立重建10份bytes，再核byte/length/hash/依赖拓扑。把Scope t改t2只改变Owner/ReferenceCatalog，不改变通用Schema/Codec；改Schema成员顺序改变其V并传递到Codec/Binding/Catalog；自Hash字段不形成循环；改变Statement predicate/Resolver分页算法/Validation检查集必须改相应V。不能用同一编码器算期望和实际后称Golden通过。

### 8.10 完整协议与序列化装配（A2技术规格，不含客户业务）

本节补齐架构中“端点/映射、序列化、认证、协议交付”的可决定设计。它与§4现有端口组合，不改变已接收Core DTO/状态/指纹，也不新增MES流程或标准认证权。HTTP、有限TCP、JSON/XML为本模块技术实现；MQTT/AMQP/标准XML通过下列同一有界连接端口装配，标准握手/传输会话与业务Owner分离。物理驱动、消息字段采纳和真实互操作分别验收，不能把未写驱动或测试说成内部API未定。

唯一新增预定工程为 `src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Protocols/Asun.Modules.IntegrationTransport.Protocols.csproj`（net10.0，Core+BCL，namespace `Asun.Modules.IntegrationTransport.Protocols`）。所有本节DTO/契约/codec/provider/HTTP和TCP连接实现归此包；Core不反向引用它。MQTT/AMQP驱动可由宿主注入同一契约，不让Core加载SDK、程序集路径或报文指定类名；驱动实现任务仍在本模块永久会话内，不笼统移交未来模块。Hermes整机传板状态、设备动作与双机互锁不属于本模块：只做显式获准消息的XML/连接/接收交接，不在本技术包实施传板业务状态机。

#### 8.10.1 有限Profile与公开构造

以下类型均公开、不可变、参数全必填，构造无I/O。字符串身份沿§3.2，未定义enum/default集合/重复路由拒绝。单实例bindings=1..64；每binding Messages=1..64、每message Fields=4..11、Receipt Fields恰为下文五角色；Selector≤1024 UTF8 bytes/64分量，全部冻结配置规范bytes≤1MiB且计原Root预算，default/超限先拒绝，不由Preview截断规则。JsonPointer只允许RFC6901逐分量路径；XML selector只允许 `/{namespace-uri}local-name` 逐层展开名路径及叶属性 `/@{namespace-uri}local-name`，不执行XPath函数/递归/脚本。XML路径分量解析必须识别大括号中的完整namespace URI（URI中的斜杠不作路径分隔）；null namespace用{}，重复展开名/同角色拒绝。Opaque只是保留枚举，本通用codec构造拒绝该值，必须另有获准标准codec；不以未解析bytes冒充已验证业务消息。

```csharp
public enum WireEncodingKind { JsonUtf8, Xml10Utf8, Opaque }
public enum ProtocolTransportKind { Https, TlsLength32, Mqtt5, Amqp10, XmlStream }
public enum ProtocolExecutionKind { Production, SoftwareFixture }
public enum WireScalarKind { String, Int64, Decimal, Boolean, UtcOffset, RawValue }
public enum MessageFieldRole
{
    MessageId, MessageName, Schema, Partition, Sequence, Payload,
    OperationId, RequestFingerprint, ReceiptId, ReceiptStage, AuthorityId
}
public sealed record ParseLimits(int MaxRawBytes, int MaxExpandedBytes,
    int MaxDepth, int MaxTokens, int MaxMembersPerObject, int MaxArrayItems,
    int MaxStringBytes);
public sealed record WireFieldRule(MessageFieldRole Role, string Selector,
    WireScalarKind Kind, bool Required);
public sealed record MessageWireRule(string MessageName, SchemaVersion Schema,
    string ContentType, ImmutableArray<WireFieldRule> Fields,
    bool PreserveUnknownFields);
public sealed record ProtocolReceiptRule(WireEncodingKind Encoding,
    string ContentType, string AuthorityId,
    ImmutableArray<ReceiptStage> AllowedStages,
    ImmutableArray<WireFieldRule> Fields);
public sealed record ProtocolBinding(TransportScope Scope, EndpointId Endpoint,
    MappingVersion Mapping, PayloadHash AssetHash, EndpointProfile Profile,
    ProtocolTransportKind Transport, WireEncodingKind Encoding,
    string AddressRef, string CredentialRef, string TlsPolicyRef,
    string SourceNamespace, ParseLimits Limits,
    ImmutableArray<MessageWireRule> Messages,
    string? QueryAddressRef, bool QueryProvesNotApplied,
    ProtocolReceiptRule? ReceiptRule, int MaxInFlight, long MaxConnectionBytes, TimeSpan ConnectBudget);
public sealed record ProtocolInput(string ConnectionIdentity,
    long ConnectionGeneration, string SourceNamespace, string ContentType,
    ReadOnlyMemory<byte> Bytes, PayloadHash Hash, string AckToken);
public sealed record WireExchangeRequest(TransportQuery Identity,
    string ContentType, ReadOnlyMemory<byte> Bytes, PayloadHash Hash,
    bool QueryOnly);
public sealed record WireExchangeResult(SendCertainty Certainty,
    string ContentType, ReadOnlyMemory<byte> Evidence, PayloadHash EvidenceHash,
    TimeSpan? RetryAfter, RemoteStatus? QueryStatus, TransportError? Error,
    bool TransportAcknowledged, string? AcknowledgementId);
public interface IProtocolConnection : IAsyncDisposable
{
    string Identity { get; }
    long Generation { get; }
    Task<WireExchangeResult> ExchangeAsync(WireExchangeRequest request,
        CancellationToken ct);
    IAsyncEnumerable<ProtocolInput> ReadAsync(CancellationToken ct);
    Task ConfirmInboxAsync(string ackToken, bool persisted, CancellationToken ct);
    void RequestClose();
    Task<AdapterDrainResult> DrainAsync(TimeSpan timeout, CancellationToken ct);
}
public sealed record ProtocolEvidenceInput(TransportQuery Identity,
    string ConnectionIdentity, long ConnectionGeneration, string ContentType,
    ReadOnlyMemory<byte> Bytes, PayloadHash Hash);
public sealed record ProtocolEvidenceStored(string EvidenceRef,
    PayloadHash Hash, bool Durable);
public interface IProtocolEvidencePort
{
    Task<PortResult<ProtocolEvidenceStored>> StoreAsync(
        ProtocolEvidenceInput input, CancellationToken ct);
    Task<PortResult<ProtocolEvidenceStored>> QueryAsync(
        TransportQuery identity, PayloadHash evidenceHash, CancellationToken ct);
}
public interface IProtocolAuthenticationState
{
    Task<AuthorityDecision> CheckAsync(ProtocolBinding binding, CancellationToken ct);
}
public interface IProtocolConnectionFactory
{
    Task<PortResult<IProtocolConnection>> OpenAsync(ProtocolBinding binding,
        CancellationToken ct);
}
public interface IProtocolFixtureConnectionFactory : IProtocolConnectionFactory { }
public sealed record AuthenticatedProtocolChannel<T>(string Identity,
    long Generation, T Channel) where T : class;
public sealed record ProtocolOwnership(Action<int> ReserveResourceSlots,
    Action<object> RegisterResource);
public interface IProtocolInboundSink
{
    Task<EnqueueResult> AcceptAsync(InboundDeliveryIntent input,
        CallContext call, CancellationToken ct);
}
```

`BoundedMessageCodec(ImmutableArray<ProtocolBinding> bindings, TimeProvider timeProvider, ProtocolOwnership ownership)` 实现ISerializationAdapter；`ProtocolAdapterProvider(ImmutableArray<ProtocolBinding> bindings, IProtocolConnectionFactory connections, IProtocolAuthenticationState authentication, IProtocolEvidencePort evidence, ProtocolExecutionKind executionKind, TimeProvider timeProvider, ProtocolOwnership ownership)` 实现ITransportAdapterProvider；`ProtocolIngress(ProtocolBinding binding, IProtocolConnection connection, IProtocolInboundSink sink, IProtocolAuthenticationState authentication, Func<CallContext> currentCall, TimeProvider timeProvider, ProtocolOwnership ownership)` 的公开方法为 `Task RunAsync(CancellationToken ct)`、`void RequestClose()`、`Task<AdapterDrainResult> DrainAsync(TimeSpan timeout,CancellationToken ct)`。Sink实现只调用已构造Core.ReceiveAsync；currentCall在每次接收取得，作为AcceptAsync第二参数原样传递，由Sink交Core.ReceiveAsync(input,call,ct)校验，不授予旁路应用权限。Provider返回的每个 `ProtocolTransportAdapter` 实现§4.3全部ITransportAdapter方法，构造内部仅接已打开connection、exact binding、clock和ownership；Provider成功把连接scope移给返回Adapter，由Adapter在全部任务Released后一次调用connection.DisposeAsync（原Task保存）；Host Root登记是强持而非第二Dispose Owner。Open失败/迟到Closing未交Adapter时由原Provider唯一关闭/Dispose，不二次归还。

有效域与工程建议：raw/expanded=1..min(Options/Profile/Capability上限)，raw推荐1MiB，expanded默认等raw（本轮不支持压缩，Content-Encoding/gzip/zip拒绝）；depth=1..128推荐32；tokens=1..1000000推荐100000；members=1..10000推荐256；array=1..100000推荐10000；string bytes=1..raw推荐65536；MaxInFlight=1..min(Profile并发,Options并发)推荐1；MaxConnectionBytes=1MiB..Options.MaxResidentBytes推荐4MiB，实际与codec/其它驻留预算共同取小；ConnectBudget取Profile.ConnectTimeout并≤Options.OperationTimeout。没有足够预算拒绝，不静默缩字段、钳制数值或申请无限buffer。上述仅技术建议；采用后生成新资产，不自动调生产参数。

ProtocolBinding.AddressRef/CredentialRef/TlsPolicyRef为受信宿主注册引用，不接受消息内URL/主题/用户名。SourceNamespace与已认证connection精确绑定。ReceiptRule=null明确只能沿后文真实ACK证据路线返回TransportAccepted、不得解析业务/Applied回执；查询Found必须有ReceiptRule否则Conflict/IT-CAP-001，不伪造成功。本规则必填OperationId/RequestFingerprint/ReceiptId/ReceiptStage/AuthorityId五个String scalar，字段角色不能与MessageWireRule混用；OperationId为小写D Guid，RequestFingerprint为lowerhex SHA256，Stage固定原文transport-accepted/business-accepted/applied/rejected，AllowedStages显式非空集合按§6.1偏序检查，不按枚举max；AuthorityId须与规则受信值exact，EvidenceHash仍核原bytes。QueryAddressRef=null明确Unsupported查询；QueryProvesNotApplied=false为推荐默认。只有标准/客户正式回查合同提供原ID、内容摘要、范围和“未应用”证据时才true，不凭HTTP404、空表或broker packetId置true。Bindings的同Scope/Endpoint只能一项，Profile/Mapping/Capabilities exact，拒绝歧义候选；引用保留到历史操作/Unknown最终退役。

#### 8.10.2 JSON/XML解析、字段存在性与编码步骤

1. 在分配/解码之前核原字节/hash和raw上限。JSON仅严格UTF8、无BOM、无comment/trailing comma/多个根；显式JsonReaderOptions(MaxDepth=limits.MaxDepth, CommentHandling=Disallow, AllowTrailingCommas=false)，Utf8JsonReader逐token读取。每token先checked增加总数；每层object记录解转义后的property name，Ordinal重复（包括 `"id"`/`"\u0069d"`）拒绝。拒绝孤立surrogate、非有限值、类型元数据驱动CLR激活；不对原文unicode归一化。不得先JsonDocument/SDK反序列化后再发现规模或缺字段。
2. 字符串以解码UTF8字节数核限额；数值保留ValueSpan原token，Int64仅TryGetInt64且整数语法/范围吻合，Decimal用有界原token拆符号/整数系数/小数位/十进制指数，以BigInteger系数和checked指数核值；先消去系数尾随0，再要求scale=0..28、绝对系数≤2^96-1（负scale仅在checked预算内乘10转scale0），据此构造decimal；超范围/非零被舍弃位拒绝，不调用会舍入的宽松TryParse；不是转double后比较。UtcOffset只接ASCII yyyy-MM-ddTHH:mm:ss，小数部分可省略或为1..7位，末尾必须为Z或±hh:mm，DateTimeOffset.TryParseExact配InvariantCulture/DateTimeStyles.None，显式offset范围±14:00、日期合法、拒闰秒/缺offset/超过tick精度，转换UTC用于比较，原token保留，不补本机时区。null、缺失、空字符串、false、0四类分别处理；Required字段缺失/null失败，可选字段没有规范默认则保持缺失，不自动生成ID/时间/成功状态。
3. XML走XmlReaderSettings：DtdProcessing=Prohibit、XmlResolver=null、CheckCharacters=true、ConformanceLevel=Document、MaxCharactersInDocument受expanded预算、MaxCharactersFromEntities=0（DTD已拒绝），自计元素深度/节点/属性/文本字节；仅XML1.0/UTF8，XML1.1或声明与实际编码错配拒绝。按namespace URI+local name核路径/属性，不按prefix字符串；重复映射scalar leaf、同角色歧义、DTD/外部实体拒绝。XmlReader不保留字节位置时诊断只写展开名路径，原RawHash/原件仍完整保存，不伪造offset。入站数据元素顺序按所选schema规则核验。
4. 先核MessageName/Schema及fixed rule，再取MessageId/Partition/Sequence/Payload；Schema原文是ASCII `major.minor`，Major=1..65535、Minor=0..65535（现SchemaVersion为ushort；资产槽仍按§3.4编码I32）、无符号/空白/前导零（0本身除外），不把任意版本字符串Parse成最新；MessageId/Name/Schema角色全必填String，Partition可选String、Sequence可选Int64非负、Payload必填RawValue，其它Kind错配在构造拒绝。rule不允许缺MessageId或用OperationId/随机Guid/时间替代。语法无误不证明来源；ConnectionIdentity/generation/SourceNamespace/Profile与当前能力/绑定不符先拒绝。Payload selector取原JSON value token区间或XML原件批准子内容；JSON原token片段保持原bytes，不重新序列化成另一消息；XML有mixed content/实体转义时不按字符串切出假原件，ApplicationPayload默认完整原XML文档，由批准应用映射消费字段。原应用Owner解释量值/单位/业务实体；互联层保留token，不换单位或重判PASS。
5. Encode先核DeliveryIntent.Schema/MessageName/ContentType及原PayloadHash，使用同reader检查已获准完整原wire envelope，按原bytes复制。MessageId必须已存在，通用路线要求它等于原OperationId小写D；消息名/Schema与intent exact匹配。原应用需要标准SDK特定包装时必须先由该应用映射形成完整原文，再交本技术codec验证，不能让通用codec猜字段。此路线不做JSON↔XML转换、不自动填字段、不把CFX重新格式化；编码bytes与批准payload一致。JSON/XML的序列化职责为可复现有界验证和原文输出，不保证不同空白格式语义同hash。
6. 结果EncodedPayload/DecodedMessage均只交自有不可变副本，WireHash/PayloadHash核实际bytes；原SourceTask结束前不归还借用。每次解析/编码含合作取消检查，CPU工作放预留worker；没有I/O，失败固定IT-PARSE-001/IT-VAL-002与字段路径，不回半个DecodedMessage。Replay调用同Codec，Open/ConfirmInbox/Store/Apply次数全0。

统一mapping技术资产不是“任意序列化设置”。用ASCII域 `ASUN-IT-PROTOCOL-ASSET-1` + §3.4原语编码，AssetHash排除自身和Mapping；字段固定Scope三S、Endpoint(S)、U32 Transport/Encoding、AddressRef/CredentialRef/TlsPolicyRef/SourceNamespace(S)、QueryAddressRef?、B(QueryProvesNotApplied)、ReceiptRule?（B存在；存在时U32 Encoding/S ContentType/S AuthorityId/U32 AllowedStages.Count+升序U32各stage/U32 Fields.Count+与下述相同的Role/Selector/Kind/Required编码）、I32 MaxInFlight、I64 MaxConnectionBytes/ConnectBudget.Ticks、ParseLimits七I32、U32 Messages.Count（MessageName/Schema升序），每项S MessageName+I32 Schema.Major/Minor+S ContentType+B PreserveUnknownFields+U32 Fields.Count（按Role升序）+每项U32 Role/S Selector/U32 Kind/B Required；最后下述ProfileProjectionHash与Capabilities.Fingerprint raw32。禁止Provider由reflection补字段。公开唯一 `ProtocolBindingFactory.Freeze(ProtocolBinding draft) : PortResult<ProtocolBinding>` 在无I/O受限worker中按下列拓扑生成全部hash并返回同record新值；draft形状/字段可验证，提交只接受Freeze后的exact值，不能信任UI自填hash。Binding.Mapping.Value固定 `asset:`+完整AssetHash（asset编码不含Mapping，防自Hash环）；ProfileHash仍依§3.4生成，不编码该ProfileHash以免mapping asset成环：资产末尾的Profile承诺为SHA256(ASCII域ASUN-IT-PROFILE-PROJECTION-1+§3.4 ASUN-IT-PROFILE-V2表的同顺序body，仅移除Mapping字段且本来已排除自ProfileHash)，命名 `ProfileProjectionHash`；该末尾第二项仍完整CapabilityFingerprint。Factory先ProfileProjection→AssetHash→Mapping→ProfileHash，再绑定exact DTO，生产切换无循环。已接收S1的m映射不变，不用于A2生产绑定。Fields一角色只能一项，JSON Pointer重复/前缀包含Payload与身份路径冲突拒绝；未知字段Preserve=true仅保存原文/给应用Owner查看，不主动执行。Source/业务对象/类型名不由规则开放动态解析。

#### 8.10.3 认证与原Operation查询

ConnectionFactory.Open在解析可信endpoint后，逐步核Scope/Endpoint/asset/profile/capability→当前认证引用及用途→DNS/连接预算→TLS→协议握手→登记generation/原资源→返回。Factory必须返回已认证精确Identity/generation，未认证连接不交Provider。TLS最低1.2、支持1.3则由受信策略允许；服务器名、链、有效期及策略的撤销检查不放宽，不提供“忽略证书错误”按钮。认证策略明确Anonymous/Bearer/mTLS/broker SASL等；只有Profile显式批准Anonymous才可无凭证，缺CredentialRef不能默认匿名。Secret只在受信连接实现短时使用，不进任何Core DTO、mapping资产、持久消息/诊断/预览；Asset仅含引用。Host安全Owner实现IProtocolAuthenticationState（不含秘密/SDK）：每次Open/Exchange/Query/Receive/Confirm前后Check本exact binding，Decision要求Allowed=true、当前AuthorityEpoch/ValidUntilUtc/PolicyHash有效且与此连接原授权代一致；撤销/换代/过期/Unknown即关新工作与原连接、在途保留事实，不允许只Open检查。真实端口最终提交/ACK的撤权线性化由该Owner和driver提供同代fence，不能把前后两次Check当原子保证。Host安全Owner拥有secret解析与撤权事实，模块拥有正确调用/释放，不重复搭建鉴权系统。

技术HTTP/TCP构造固定：`HttpProtocolConnectionFactory(Func<ProtocolBinding,CancellationToken,Task<AuthenticatedProtocolChannel<System.Net.Http.HttpClient>>> openAuthenticatedClient, TimeProvider clock, ProtocolOwnership ownership)`、`StreamProtocolConnectionFactory(Func<ProtocolBinding,CancellationToken,Task<AuthenticatedProtocolChannel<System.IO.Stream>>> openAuthenticatedStream, TimeProvider clock, ProtocolOwnership ownership)`，均实现IProtocolConnectionFactory。callback仅来自可信Host组合根，绝不能报文/目录动态加载；原callback Task和迟到HttpClient/Stream由Root接收，关闭代后立即安排停止并观察Dispose。callback返回AuthenticatedProtocolChannel<T>（broker tuple同样含Identity/Generation），两字段由同Host认证路由赋予，不从HttpClient/Stream猜取。connection的Identity为Host认证路由赋予的1..128UTF8稳定ID，Generation>0且只增不复用；Open真实返回前两者已登记，空/重复/溢出拒绝。每次Open返回独占实例（HTTP handler/连接池也独占本connection），模块关闭不Dispose其它Host共享池；同实例重复交两Owner拒绝。BCL工厂在模块负责Exchange/读/ACK/排空；HTTP callback返回AuthenticatedProtocolChannel.Channel中的HttpClient必须已设合法绝对HTTPS BaseAddress；Send固定POST该BaseAddress，Query固定GET同origin的BaseAddress+相对QueryAddressRef并仅以Uri.EscapeDataString编码operationId/requestFingerprint/scope三分量，QueryAddressRef只允许受信相对path无query/fragment/userinfo（不是任意输入URL）。stream callback已按AddressRef的已批准host/port握手。Host提供认证连接callback的完整具体步骤在下节，不由开发者猜驱动行为。MQTT/AMQP通道同样必须返回下节声明的受控connection，不借此转移消息事实Owner。

ProtocolTransportAdapter.SendAsync重核envelope.Scope/Endpoint/Profile/Mapping/Capability/资产代及原WireHash→从§3.4 Intent规则算完整RequestFingerprint（输入Scope完整绑定）→创建TransportQuery原OperationId（RunId仅当前尝试，不替原ID）→Exchange(QueryOnly=false)；错误certainty按实际发生点返回。QueryAsync只查原Scope/Endpoint/OperationId/RequestFingerprint；不换ID、不重新POST/Publish/写socket生产帧。BoundedMessageCodec的公开附加方法 `RemoteQueryResult DecodeReceipt(WireExchangeResult result,TransportQuery expected,ProtocolReceiptRule rule,long connectionGeneration,ProtocolEvidenceStored stored)` 从Evidence提取原OperationId/RequestFingerprint/ReceiptId/Stage/AuthorityId，逐项exact且认证来源吻合才返回RemoteStatus.Found及非null Receipt；Send仅将该组合映射为ReceiptConfirmed；权限不足/坏摘要/关联不符返回Conflict+IT-SEC-001，Send映射为MayHaveReached+原错误，不能忽略坏回执。TransportAccepted仅真实协议ACK，BusinessAccepted/Applied只由获批端点证据；driver不能用client库“发送完成”补Applied。Receipt返回前，Provider先通过显式IProtocolEvidencePort.StoreAsync保存原Evidence副本；Store以完整Scope/Endpoint/原OperationId/RequestFingerprint+EvidenceHash为不可变幂等键，同键同bytes重放原引用，同键异内容Conflict，不能生成另一个操作来掩盖Unknown。只接受PortStatus.Success、Hash与实际bytes相同、受控EvidenceRef非空、生产Durable=true；DecodeReceipt只从这个stored取得EvidenceRef，不凭字符串拼接制造可回读证据。Store确认丢失/权限失效/非耐久/Unknown时Send仍MayHaveReached，原proof保存Task/bytes由Root强持，只用QueryAsync查原键；Query零新写，NotFound不证明远端未执行。EvidencePort由Host组合根显式注入原取证/存储Owner批准的耐久归档能力，模块负责有界调用、原身份及移交，归档Owner负责原件回读、对象引用保护/保留和退役；生产没有此能力就在Open前拒绝，不以Root内存当耐久资产。测试Host使用本地有限字典端口（MaxEntries=100、MaxBytes=64KiB、immutable复制、明确Durable=false），只验证协议/幂等，不用于生产或伪造耐久。Provider的executionKind参数必填且不进入历史消息hash：Production必须Durable=true；SoftwareFixture只允许显式IProtocolFixtureConnectionFactory（无网络/设备IO）与Capabilities.Limitations含not-production，才可接受Durable=false的合成回执。Host输出必须标软件夹具，不能由SupportsOffline/缺归档自动降为fixture；真实HTTP/TCP/Brokers工厂不实现此marker，错误组合构造拒绝。该模式不授予生产资格或持久Inbox成功ACK。字典、连接/解析实际驻留及worker均共同扣Host原1MiB/额度，64KiB是分项上限而非额外总预算，满时拒绝且保留原未知任务。无UIHost同样必须显式提供，不能隐藏初始化。
    
TransportAcknowledged=true仅来自已验证MQTT PUBACK成功或AMQP Accepted disposition；AcknowledgementId为原通道局部packet/delivery标识且非空、generation exact。TCP Write完成、HTTP普通2xx、心跳与SDK返回不产生此标志。无ReceiptRule时可据这类真实ACK构造仅TransportAccepted证据：ASCII域ASUN-IT-ACK-1+Scope三S/Endpoint(S)/OperationId小写D(S)/RequestFingerprint(H)/ProtocolId(S)/WireVersion(S)/ConnectionIdentity(S)/Generation(I64)/AcknowledgementId(S)，原语沿§3.4，原bytes/hash同样先Store；ReceiptId=ack:完整证据Hash，AuthorityId=该已认证binding.SourceNamespace，ReceivedAtUtc取显式clock。该格式只记录真实技术outcome，没有Business/Applied字段；没有ACK或没有可保存证据则MayHaveReached+Receipt=null。存在ReceiptRule时优先检查原业务证据，坏业务回执返回错误/MayHaveReached，不被技术ACK覆盖。Query Found必须由业务规则产生Receipt；技术ACK不是业务回查。Exchange(QueryOnly=true)的QueryStatus必须有值且不可为发送certainty凭空推导，生产发送QueryStatus=null；Query只允许GET/查询主题或批准query消息，收到业务NotFound仍RemoteStatus.NotFound；ProvenNotApplied必须额外获准“未执行”证据及旧写者fence，禁止通用HTTP404替代。

Inbound以原connection.ReadAsync逐条有界输入→核当前来源/代/asset→Host显式新技术OperationId→sink.AcceptAsync→保留原结果/确认任务。Inbox首ID属本Core首次持久登记；新连接重复外部MessageId回首次原ID而不再Apply。ConfirmInboxAsync(ackToken,true)仅在本地Durable=true且CommitStatus.Persisted时发送已批准传输ACK；Unknown/失败不得成功ACK、保持原AckToken查询/重投策略，不“异常finally自动ack”。Durable=false合成Host不得生产确认；不可hold的协议明确不保证持久接收，不用HTTP200替代。客户端ACK token是通道局部身份，不成为业务MessageId；失连后旧token禁止确认新代，原Inbox事实仍保留。RequestClose只关准入/连接，原Confirm/MoveNext/解析/Receive/Query Task和bytes到真实退出才Released，沿§7/10已接收Root，不再新增Keeper。

#### 8.10.4 各协议技术行为及不适用条件

| 路线 | 冻结调用顺序/会话能力 | 不得推断与恢复 |
|---|---|---|
| HTTPS/.NET10 BCL | Host显式new SocketsHttpHandler：AllowAutoRedirect=false、AutomaticDecompression=None、UseCookies=false、ConnectTimeout=ConnectBudget、MaxConnectionsPerServer=MaxInFlight、凭证与SslOptions由受信策略提供；new HttpClient(handler,disposeHandler:true)，Timeout=InfiniteTimeSpan，原请求受独立deadline。Exchange new HttpRequestMessage，固定受信URI/方法，发送用SendAsync(...,ResponseHeadersRead,ct)；显式有界读正文及每次ReadAsync剩余deadline，限额先于分配，finally Dispose response/request/body。Content-Length只作先验检查，chunked也逐字节核总量。重定向/401/403/429/503不自动跟随/重新发。 | POST前连接失败可NotSent；一旦进入可能发送的SendAsync保守MayHaveReached，不能凭异常证明未到达。2xx是HTTP响应，只有合格证据才能ReceiptConfirmed。429/503带合法Retry-After供§6.3，若可能已写则先查原ID。HTTP404仅NotFound。下游HTTP接收由Host监听，传raw到Ingress/sink后按冻结ACK政策响应，监听器不进Core。 |
| TLS长度TCP/.NET10 BCL | Host new TcpClient→ConnectAsync(host,port,ct)→SslStream→AuthenticateAsClientAsync(SslClientAuthenticationOptions,ct)，服务端对应受信证书/客户端策略；只交成功authenticated stream。本模块StreamProtocolConnection按4byte无符号大端长度（含1byte Kind）+Kind+payload，Kind=Data1/Query2/Receipt3/Ping4/Pong5/InboxAck6；ReadExactlyAsync先4byte头再核1..min(MaxWireBytes-4,uint.MaxValue)（完整帧含4byte头受wire上限；MaxWireBytes<5构造拒绝），再租有界body。每连接唯一read pump、唯一send lock，partial/truncated/unknown Kind拒绝并关闭。 | 0/越界长度不分配body；EOF/部分发送MayHaveReached，socket WriteAsync完成不等远端业务接受。只对批准query消息发Query2；无Query规则返回Unsupported。Query2 body固定ASCII域ASUN-IT-QUERY-1+§3.4大端S(Scope三分量)/S(OperationId小写D)/S(Endpoint)/H(RequestFingerprint)/ExternalCorrelation?（B存在+S），不把原生产Data payload再发一次；Receipt3 body为ReceiptRule声明的原JSON/XML证据。Data1/Receipt3之外的控制帧展开均计wire预算；Ping4/Pong5无body，仅单个在途心跳且禁止Ping反触Data。Inbound Data1的AckToken只在原connection内映射到该原RawHash/外部MessageId，InboxAck6 body=S(MessageId)+H(RawHash)+B(persisted=true)，不发送本地随机token给远端当业务ID；未确认持久仅不ACK/关闭，不能发送成功标志。Ping/Pong只更新连接健康；缺心跳超过Timeout关闭连接，未决操作仍Unknown。标准协议不是此自定义长度帧，不能拿该帧冒充Hermes/CFX。 |
| MQTT5 | 按OASIS MQTT5固定会话参数：独占ClientId精确Scope/Endpoint；QoS1为可靠传输推荐、QoS0仅显式只读可丢用途；Receive Maximum≤MaxInFlight，Maximum Packet Size≤MaxWireBytes，Retain=false生产事件，不自动订阅通配/共享订阅；Topic及reply topic来自可信AddressRef注册。受控driver连接→CONNACK成功→精确SUBACK→PUBLISH；PUBACK仅TransportAccepted。入站应用ACK模式先受控hold再持久Inbox→PUBACK，driver不支持manual ACK则拒绝持久接收路线。 | packetId/DUP/QoS2不代MessageId/本Core Inbox；会话过期/SessionPresent=false仍按原业务ID查询，不能把缓存清空当应用未执行。回复主题是批准query合同，不能重发生产Publish充当Query。CleanStart/session expiry/KeepAlive来自有限版本配置，无自动提高；未知PUBACK以后仍原ID/Approved同键恢复，不承诺全链exactly-once。 |
| AMQP1.0/CFX固定wire2.1 | driver独占container/link identity、受信地址/TLS/SASL；有限link credit≤MaxInFlight及字节预留，accepted/rejected/released/modified disposition逐项处理；outbound settled accepted仅TransportAccepted，client deliveryTag仅link局部键；Receive hold/unsettled→持久Inbox→accept；不允许SDK自动accept先于本地确认。CFX信封先由§8.10.2原字节/存在性验证，固定MessageName/Version/Source规则，才接批准模型。 | SDK2.1.1来源沿§8.4，不能使用其静态JsonSettings/自动Guid时间/自动Type.GetType路径。CFX没有本模块统一Reconcile API；仅客户明确提供的原Operation查询消息可Query，否则Unsupported/Unknown。不把AMQP0-9-1 confirm调用套到AMQP1.0，不伪造连接库API或认证通过。 |
| XML stream/Hermes消息桥 | 受信驱动按所选标准原始framing读取完整有界文档，不套用上述4byte自定义帧；本包按§8.10.2核XML1.0/namespace、显式BoardId/消息身份/固定允许集合，保留原件并调用Sink。未知XML/版本/角色拒绝，握手成功只标健康。标准版本、角色、message set、framing rule及供应实现作为binding的Capabilities exact字段，启动缺任一拒绝。 | `BoardAvailable/MachineReady/StartTransport/StopTransport/TransportFinished` 只交原线体应用Owner的批准消息，不由本模块决定启动运动/完成传板/删除BoardId/自动恢复。未批准Hermes标准实例无真实interop资格；这属于所选外部标准Profile输入，不允许开发者自选分隔符/板状态机。无业务原Operation查询合同则Unsupported/Unknown；不能宣称Hermes符合性或兼容所有版本。 |

MQTT/AMQP/Hermes受控驱动由本模块实现/测试负责人接入并对照上表，不是任意host SDK对象越过Core。公开构造 `BrokerProtocolConnectionFactory(ImmutableArray<ProtocolBinding> bindings,IProtocolConnectionFactory qualifiedDriver,ProtocolOwnership ownership)` 为有限核验代理：只允许Mqtt5/Amqp10/XmlStream的exact角色/版本/认证/预算，Open转交已注册qualifiedDriver，先登记原Task与迟到连接；Exchange/Read/Confirm/Close/Drain全部透传真实结果并执行上述certainty、ACK与代号核验。qualifiedDriver不含Core业务或客户端请求delegate；缺握手/framing/ACK能力在Open前IT-CAP-001拒绝，不造no-op成功。供应驱动具体包/公开签名的绑定属于真实实现任务，现技术契约、调用义务与失败判定可确定；换库不改变Module API、不改变消息/应用Owner。现场指定标准消息字段、认证端点/secret与业务查询才是外部门。

#### 8.10.5 有限推荐和配置采纳

不另加AI/自动自调。建议由纯函数 `ProtocolRecommendations.Create(ProtocolBinding binding,TransportOptions options)` 返回新的ProtocolBinding候选（按ProtocolBindingFactory.Freeze生成新hash/Mapping/Profile）：只取本节推荐解析/并发/驻留预算与现Options最小可行组合；当推荐不可行返回ValidationResult+无候选，不钳制原输入。公开返回类型 `ProtocolRecommendation(ProtocolBinding? Candidate,ValidationResult Validation)`。参数改动均列明字段/旧值/候选值/限额来源，以同Codec/Profile检查验证；不会修改原绑定、Store或发送消息。用户在配置Host显式审核候选、冻结AssetHash/Mapping/Profile，按§14关旧代并保留原Unknown后装配新实例。地址、消息语义、ACK级别、查询证据/幂等声明、TLS与凭证引用、RequiredStage不在自动建议域，不借网络变慢降认证或质量条件。

#### 8.10.6 MQTT/AMQP驱动的确定库与公开接线

上节qualifiedDriver不是让程序员再选技术方案。首选冻结MQTTnet v5.2.0（commit `14463d1ef9f1f119514185c1832905b91bff827d`，MIT，目标net8/net10）和AMQP.Net Lite v2.5.4（commit `f1c1d58f8d265c53dfb8d22591b6f185fa4dc458`，Apache-2.0，NuGet AmqpNetLite，采用其net5.0资产由net10消费）；没有安装/下载/兼容性验收结果。单独预定驱动工程 `src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Brokers/Asun.Modules.IntegrationTransport.Brokers.csproj`，namespace `Asun.Modules.IntegrationTransport.Brokers`，net10.0，Protocols+MQTTnet5.2.0+AmqpNetLite2.5.4；这些依赖仅此包，CFX SDK不引入。双方驱动实现同IProtocolConnectionFactory/Connection、exact Binding和资源契约，归本模块Owner，不把消息台账/SDK句柄漏到Core。

构造明确为：
- `Mqtt5ProtocolConnectionFactory(Func<ProtocolBinding,CancellationToken,Task<(string Identity,long Generation,MQTTnet.IMqttClient Client,MQTTnet.MqttClientOptions Options,string SendTopic,string? QueryTopic,string ReplyTopic)>> openAuthenticatedClient,TimeProvider clock,ProtocolOwnership ownership)`。Host回调只创建配置完整的独占client/options，不Connect；Options已有限ReceiveMaximum/MaximumPacketSize/精确认证/TLS、MQTT5与独占ClientId，所有topic禁止通配符且已注册。tuple.Identity/Generation与Host认证注册exact；driver在有界worker上逐步装事件→ConnectAsync(options,ct)→SubscribeAsync(精确ReplyTopic options,ct)并核成功→交连接，不接纳同时Connect/Disconnect（上游接口显式禁止）。
- `Amqp10ProtocolConnectionFactory(Func<ProtocolBinding,CancellationToken,Task<(string Identity,long Generation,Amqp.Connection Connection,string SendAddress,string? QueryAddress,string ReplyAddress)>> openAuthenticatedConnection,TimeProvider clock,ProtocolOwnership ownership)`。Host用受信ConnectionFactory.SSL/SASL、实际公开CreateAsync(Address address,CancellationToken cancellationToken,IHandler handler=null)完成握手；原Task与迟到连接按Root保存；driver再new Session/独占SenderLink/ReceiverLink，原构造、Attach callback与迟到对象先登记，绑定失败关闭已建部分资源。地址是批准服务内路径，不由消息字符串生成。

MQTT Send：冻结MqttApplicationMessage（实际原bytes、固定topic、QoS1、Retain=false）→client.PublishAsync(message,ct)原Task→核成功PUBACK reason再产TransportAccepted技术证据（原OperationId/fingerprint、packet局部确认与认证generation）。失败前certainty按§8.10.4。ApplicationMessageReceivedAsync中**先设置AutoAcknowledge=false**，从ApplicationMessage取得raw Payload复制到预留槽，PacketIdentifier+generation+本连接递增receive序号+RawHash签发不复用AckToken；同packetId仍在pending时仅接受exact DUP/原bytes，不覆盖原args并保持原event args/ACK Task；入站和reply不同精确topic路由。ConfirmInbox(true)只调用此原args.AcknowledgeAsync(ct)一次，拒绝/Unknown保持未ACK并依批准连接策略断连重新投递，不能删除仍占用args/原Task。超过pending ACK项/byte限额前暂停读取/降低credit或关连接，不无限存event args。QueryOnly用专门批准query topic，不沿SendTopic生产Publish；只关联原OperationId/fingerprint且等待有限reply，没query topic则Unsupported。业务reply用ReceiptRule，不把PUBACK当BusinessAccepted。

AMQP Send：new Message携原bytes，SenderLink.Send(message,OutcomeCallback,state) callback路线（已读actual public signature）注册TCS RunContinuationsAsynchronously；调用前先把message/callback/TCS登记。Accepted/Rejected/Released/Modified只生成其原技术outcome，callback迟到进入原connection generation账本而不交新run。Reader用ReceiverLink.Start(0,callback)，随后SetCredit(MaxInFlight,false)明确manual credit，不用默认autoRestore；成功Inbox确认后原ReceiverLink.Accept(message)，归还该项字节预留/credit；异常/未提交不Accept，必要时Release原message或Close连接后重投，保留原消息/Task和Inspector原ID查询。Attach/flow/rejected没有业务Applied。Query用独立批准地址和消息，Query result仍需ReceiptRule或权威NotFound证据。Close没有已确认异步快捷API时，用独立预留关闭worker依Receiver/Sender→Session→Connection的Close(TimeSpan remaining)真实调用并保持原worker，避免主线程同步等待；超时只是Retained，按AddClosedCallback/IsClosed与原callback/Task全部退出判断释放，不以Close返回或超时推断资源已归还。任何原message/outcome迟到回调都必须能回原Owner，不能解订阅就宣布Released。

MQTT关闭：关闭新Exchange/Ingress门→对已完成Connect的client安排DisconnectAsync原Task（Connect尚在途仅安排独立取消请求，迟到成功关闭）→并发汇合所有Publish/Read/reply/ACK原任务与event callbacks→只在实际退出后client.Dispose一次；若SDK Disconnect/Dispose同步前导阻塞，关闭worker原Task留Root，Drain TimedOut,false，不夺SDK内存。AMQP Close同理。公开Port不得返回早于内部资源退出的Task；包装deadline停止等待，§7 Root保留原调用与callbacks。库测试有延迟ACK/flow/close样例可借其思想，但不以已有tests通过替本驱动证明。

实际只读源码/测试与依赖记录（2026-10-12，未运行上游测试）：MQTT [IMqttClient](https://github.com/dotnet/MQTTnet/blob/14463d1ef9f1f119514185c1832905b91bff827d/Source/MQTTnet/IMqttClient.cs) SHA256 `841cce7e94476453e008732e0e54714d4a67c01eb27aeccdbac0852a69022dc8`、[ReceivedEventArgs](https://github.com/dotnet/MQTTnet/blob/14463d1ef9f1f119514185c1832905b91bff827d/Source/MQTTnet/Receiving/MqttApplicationMessageReceivedEventArgs.cs) `e8003504fe2f4b5f3469bbb07bb9f9d39dcd516755bc49de798b6537c7ac47cd`、ClientTests `a535c03eba93adf8382e9049fbc6187ccb3d529579194f5ec0e91be40ecf2022`（含AutoAcknowledge=false/延迟Acknowledge反例）；本库无所读项目中的外部运行PackageReference，Directory.Build.props net8/net10，测试MSTest4.0.2/RecyclableMemoryStream3.0.1不迁入唯一Exe。AMQP [ReceiverLink](https://github.com/Azure/amqpnetlite/blob/f1c1d58f8d265c53dfb8d22591b6f185fa4dc458/src/ReceiverLink.cs) `595d98b3d5a39aab01d58a3a4e698e9cb9440e1e113c9537693c7c7731f2d7f6`、SenderLink `7401fde1d61c914d036db0195d9ca486049318011e4a222483003d7741238079`、ConnectionFactory `95491c37f5c5a37c81cc589fb3a45cae33f89adacdbcda5cf7c79241eff1fe3e`、AmqpObject `7cffcd1416aa799948e16c259ac1aa50227a098549f862f55f40227dca14db9e`、LinkTests `12968eeb71bb131dff99d38d9dd99c324e7e9ee9167764753c1a87f90574e1ae`；所读工程只有SourceLink1.0.0 build private依赖/net48专用System.Transactions，不使用环境TransactionScope。测试需真实或loopback broker，未执行；源码支持manual credit/接受/同步关闭边界，不证明取消、库缓存或大库吞吐符合本Profile。具体库升级按新commit/hash与同反例单独变更，不自动跟最新版。

### 8.11 新技术范围的固定依据与限制

仅为§8.10新缺口定向读取官方资料，不重研已接收Core/Store/Root。读取日期2026-10-12：
- .NET10官方 [Utf8JsonReader](https://learn.microsoft.com/en-us/dotnet/api/system.text.json.utf8jsonreader?view=net-10.0)、[HttpCompletionOption](https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpcompletionoption?view=net-10.0)、[SslStream.AuthenticateAsClientAsync](https://learn.microsoft.com/en-us/dotnet/api/system.net.security.sslstream.authenticateasclientasync?view=net-10.0)。ResponseHeadersRead只覆盖headers阶段的HttpClient Timeout，body必须独立受deadline/上限控制；JSON reader的MaxDepth不能代tokens/重复字段/精度检查；TLS握手不证明业务来源授权。
- 沿§8.4 runtime v10.0.0固定commit，实际只读 [HttpClient.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Net.Http/src/System/Net/Http/HttpClient.cs) SHA256 `4863135632cecd06c9a2afa2010d4955a1586c4f677fbfbff7bc6b4b9a6d4d43`、[Utf8JsonReader.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Text.Json/src/System/Text/Json/Reader/Utf8JsonReader.cs) `a7dab10c4c40fcdce85b85602a0b9e94ee1c9b89880eba3dffb06033e64622e0`、[SslStream.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Net.Security/src/System/Net/Security/SslStream.cs) `12498a2be0432c4fa5b23abff34c022ab63c3f5c794963623fe23eed5b119143`；MIT/BCL依赖，不复制源码或运行其测试。只采纳实际调用/读取/资源退出边界，不把BCL源码当Core端到端证据。
- [OASIS MQTT5.0 2019-03-07正式标准](https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html)正文SHA256 `acb004f3b3388cf4ba26bd9f4483b07ea0e94eeadf09c8159e00e3cee2710196`，采用§3.1/3.3/4.3/4.9/4.10的会话、QoS与流控边界；标准文档无运行依赖，不复制标准实现。QoS保证与应用幂等分层，不能由规范推断本驱动已支持延迟ACK。
- CFX固定源码/OtherTests与AsunControl长度读取来源沿§8.2/8.4复用；本次未重算旧来源hash。AsunControl使用BitConverter本机字节序，与本节明确大端不兼容，只借鉴先长度后分配/精确读取思路，禁止静默称wire兼容。
- Hermes官方候选网页本轮404，未读到目标版本正文，不记为规范证据；本模块只冻结通用XML消息/连接桥，具体标准实例必须由宿主提供准确版本/角色/完整规范引用与获准framing，现场板传状态归线体Owner。无此输入时不能启动该标准实例，也不阻断HTTP/TCP/JSON或Core。已保留AOI历史Hermes来源不是标准符合性证明。
- dxdocs工具当前不可用，已定向读取本机25.2官方XML并确认Grid DataControlBase.ItemsSource/SelectedItem、DataViewBase.AllowEditing/ShowSearchPanelMode、Docking.BaseLayoutItem.AllowClose和Editors.BaseEdit.EditValue；PropertyGrid.ReadOnly文档矛盾继续真编辑反例验收。未定位到FlyoutControl.IsOpen，故本UI不使用该未知成员，非关键详情以WPF Expander承载。没有DevExpress安装/许可证或版本适配任务。

### 8.12 协议Golden、独立消费者与异常断言

以下仅合成技术输入，不是CFX/Hermes消息或客户确认。JSON/XML均MessageId=00000000-0000-0000-0000-000000000001、M、Schema1.0，JSON Payload原片段为{}；XML ApplicationPayload为完整81byte文档，不假装保留一个重写后的子XML原件。TCP仅适用本节明确长度大端路线。此前§3.4/8.6/8.9有效向量原样复用，不重复重建。

小型完整mapping投影夹具：Scope=t/s/l，Endpoint=e，Transport=Https(0)，Encoding=JsonUtf8(0)，AddressRef=a/CredentialRef=c/TlsPolicyRef=x/SourceNamespace=n，QueryAddressRef=null、QueryProvesNotApplied=false、ReceiptRule=null、MaxInFlight=1、MaxConnectionBytes=1048576、ConnectBudget=10000000ticks；ParseLimits声明顺序=1024/1024/8/100/16/16/128；一个Message M/1.0/application-json（实际ContentType=application/json）、PreserveUnknown=false；Fields按Role=MessageId0/MessageName1/Schema2/Payload5，Selectors=/id,/name,/schema,/payload，Kinds=String0/String0/String0/RawValue5，Required全true。末尾ProfileProjectionHash与CapabilityFingerprint均取真实合成外部bytes empty的SHA256；这是资产语法Golden，不是可启动生产Profile，实际Freeze用完整ProfileProjection与Capability投影。Mapping=asset:658fb6e97b7feae36bebbd9c3c208aed261574fb755aa8aea92be5a4535c052d。

**ProtocolJson：84 bytes；SHA256=e0e45fa4cd82b2ab2211338044a99d92ae07e1569ad95a407a44efc886d499c2**

```text
7b226964223a2230303030303030302d303030302d303030302d303030302d303030303030303030303031222c226e616d65223a224d222c22736368656d61223a22312e30222c227061796c6f6164223a7b7d7d
```

**ProtocolXml：81 bytes；SHA256=3c514147c6029c2176f0465b39fb74880699131744bd435dba6641dbc48ff39a**

```text
3c6d2069643d2230303030303030302d303030302d303030302d303030302d30303030303030303030303122206e616d653d224d2220736368656d613d22312e30223e3c7061796c6f61642f3e3c2f6d3e
```

**LengthTcp：89 bytes；SHA256=e94bb7bf32c7a0b32844d279ebe52cd536e6d508bc1f634e44dd842f0bc43e31**

```text
00000055017b226964223a2230303030303030302d303030302d303030302d303030302d303030303030303030303031222c226e616d65223a224d222c22736368656d61223a22312e30222c227061796c6f6164223a7b7d7d
```

**ProtocolAsset：304 bytes；SHA256=658fb6e97b7feae36bebbd9c3c208aed261574fb755aa8aea92be5a4535c052d**

```text
4153554e2d49542d50524f544f434f4c2d41535345542d3100000001740000000173000000016c00000001650000000000000000000000016100000001630000000178000000016e00000000000001000000000010000000000000009896800000040000000400000000080000006400000010000000100000008000000001000000014d0000000100000000000000106170706c69636174696f6e2f6a736f6e000000000400000000000000032f6964000000000100000001000000052f6e616d65000000000100000002000000072f736368656d61000000000100000005000000082f7061796c6f61640000000501e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

双消费者A沿MES HTTP：§10.1 HostInput scope=t/s/l完整现值，delivery payload替换上述84byteJSON、PayloadHash取其真实Hash，ProtocolBinding草稿AddressRef=mes-a/认证cred-a/tls-a；消息rule取上述字段、Parser1024/1024/8/100/16/16/128，其余预算使用Host已预留1MiB（不得采用4MiB建议越过root）。Freeze先算真实Projection/Asset/Mapping/ProfileHash，DeliveryIntent及InboundDeliveryIntent引用该ProfileHash/CapabilityHash；新Capability为https/1.1/client、MessageNames=[M]、auth模式=[host-ref]、Wire/Expanded上限1024、Query=true（仅fake获批query，Host同时明确ReceiptRule以解析以下合成业务证据）、Idempotency=true、Applied=false、Offline=true、Unordered；PackageHash绑定真实受测程序集bytes，合成fixture则明确原始UTF8“http-fixture-v1”bytes且不声称实际包；Fingerprint用§3.4算，EvidenceRefs=[fixture-http]、Limitations=[not-production]。两个Host的完整ReceiptRule固定JsonUtf8/application-json（实际application/json）、AuthorityId=remote-fixture、AllowedStages=[BusinessAccepted]、5个必填String字段Role=OperationId/RequestFingerprint/ReceiptId/ReceiptStage/AuthorityId，路径=/operationId,/fingerprint,/receiptId,/stage,/authority；callback Evidence用独立UTF8构造{"operationId":"原ID","fingerprint":"实际§3.4 Intent指纹","receiptId":"r-原ID","stage":"business-accepted","authority":"remote-fixture"}，只有用于技术fixture。纯语法Golden的ReceiptRule=null不直接作为Host binding。Host创建真实ProtocolAdapterProvider/BoundedMessageCodec并显式注入上述有限EvidencePort，executionKind=SoftwareFixture，connection factory为显式IProtocolFixtureConnectionFactory/可控IProtocolConnection fake，Application/Authority沿已接收§10，Store沿MemoryStore（DB的7b7d元数据夹具不借用来解释新84byte协议样例），不fake整个Core。

消费者B沿线体有限TLS-TCP：Provider同样显式SoftwareFixture和独立有限EvidencePort，TransportScope=t/s2/l，其它完整DTO沿§10.1，Capability改tls-length32/1/client、Package原bytes“tcp-fixture-v1”、EvidenceRefs=[fixture-tcp]、Limitations=[not-hermes]；Transport=TlsLength32，地址/认证引用=line-b/cred-b/tls-b，Wire帧输入为上述89bytes（解帧后RawBytes为84），Parser同A、Scope/asset/profile按真实字段重算。实例各自clock/root/own callbacks；ProtocolIngress.Sink分别调用同Core.ReceiveAsync，只读消息Application桥沿§10.5；两Host旧ID允许同值但Store、EvidencePort和认证Scope不串。配置预览复用这两个输入，任何Preview零Open/Store/Apply，收到同源MessageId两次只首次Apply；ACK确认丢失沿原Inbox/原Operation Query，不替换ID。两个消费者使用同一Protocols DLL，不复制实现或启动检测产品。

必要反例/计划（同§12唯一Exe，代码任务获准后执行）：
- IT-T35 parser/asset：独立字段重建四Golden，MessageId缺失/null/空、escaped duplicate id、BOM/坏UTF8/孤立surrogate、多根、超depth/tokens/string/array、Int64=9223372036854775808、不可精确decimal、缺offset时间、XML1.1/DTD/外部实体/namespace错/歧义selector均拒绝且副作用0。MessageId字符串不得经double；rawhash相同而Scope不同仍不同binding。
- IT-T36 connection/certainty：HTTP只有200/空体不得BusinessAccepted，redirect不能跨地址凭证，headers成功/body超限或卡住仍有限；TCP首字节逐片输入、length0/0xffffffff/半头/半体拒绝不超分配，前导连接失败NotSent、发送后丢Receipt MayHaveReached。MQTT/AMQP ACK只能TransportAccepted，driver自动ACK/无hold能力生产Receive拒绝；old generation AckToken不能确认新代。Query相同ID/fingerprint、业务NotFound不ProvenNotApplied，确认已Applied也不重Apply。
- IT-T37 recommendations/UI：无UIValidate/Recommend/Preview与Panel结果一致；推荐只生成候选，不Connect/Save/Send；提案CAS错/撤权/Unknown未迁移拒绝旧配置替换；两WPF Host三语、全键盘、1920×1080、禁用原因/授权预览/迟到Dispatcher/解绑保留逐项核，stats端口当前Query权限/Scope精确，失败不补0，Root任务实际归还后Released。旧S1/A1-DBRoot断言直接复用，不重造根测试。
- 所有close/原worker/Connection.Read/ACK/HttpClient/Stream/Codec原Task同Root原槽保持，finally关闭先于汇合，Retained/未知证据引用/未完成case返回非零，不能把fixture 0当生产协议通过。客户标准实例的真实规范消息与interop另由获准Profile加入同门，未提供时Unverified。

## 9. 可选 UI 契约

已有可选监控控件保留，补齐架构已规划的连接/映射只读预览和参数提案面板；非Core强制依赖，不新增产品页面、任意脚本设计器、MES流程或远控能力。使用者为运行查看员（状态/错误/积压），集成人员（原消息/证据/对账），获授权的运维人员（取消未发送项/安全重投）；角色名称不授予权限，实际动作仍由宿主AuthorityPort判定。Core完全可无UI运行，视觉/影像视口比例对本控件不适用。

### 9.1 独立控件公开接入

后续 `Asun.Modules.IntegrationTransport.Wpf.dll` 的namespace是 `Asun.Modules.IntegrationTransport.Wpf`，类 `IntegrationTransportMonitor : System.Windows.Controls.UserControl` 实现以下接口。公开构造函数为 `IntegrationTransportMonitor(IProjectionRootOwner rootOwner, ProjectionBudget budget)`；rootOwner和budget是不可省略的显式输入，空值/无效域抛ArgumentException，无默认全局根或无参构造路径。方法必须在控件Dispatcher调用，绑定错误返回false，不开启隐藏窗口。投影根端口唯一见§4.6，不引用测试Hosting或产品类型。

```csharp
public enum MonitorCommandKind { InspectEvidence, Query, Reconcile, Retry, Cancel }
public sealed class MonitorCommandEventArgs : EventArgs
{
    public MonitorCommandKind Kind { get; }
    public OperationId OperationId { get; }
    public long ExpectedRevision { get; }
    public MonitorCommandEventArgs(MonitorCommandKind kind, OperationId id, long revision)
        => (Kind, OperationId, ExpectedRevision) = (kind, id, revision);
}
public interface IIntegrationTransportMonitor
{
    Task<bool> AttachAsync(IIntegrationTransport transport,
        Func<CallContext> getCurrentCall, CancellationToken ct = default);
    Task DetachAsync(CancellationToken ct = default);
    ProjectionOwnerId? ProjectionOwner { get; }
    ProjectionCleanup? LastProjectionCleanup { get; }
    void SetLanguage(System.Globalization.CultureInfo culture);
    event EventHandler<MonitorCommandEventArgs>? CommandRequested;
}
```

Attach在同一控件已绑定时拒绝，Detach终止List/Query/Observe投影任务并清空敏感详情，不Stop/Drain服务；取消只停止等待，后台退订继续。getCurrentCall由宿主提供当前授权引用，不能缓存首次引用永久使用。控件直接调用只读Query/List/Observe；CommandRequested只提交Kind/原ID/CAS草稿，宿主再次授权后调用Core的取消/恢复或证据Owner只读入口，结果通过同一查询刷新。双击/长按不发设备或重投命令；事件异常隔离。更换语言保留OperationId选择、过滤/键盘焦点，不改变Profile或消息字节。SetLanguage支持zh-CN/zh-TW/en-US及已加载语言资源；未支持语言保持原语言并抛ArgumentException（稳定参数名culture，无秘密），宿主统一提供语言入口与主题。

Detach/Unbind与控件卸载共用唯一退订Task，不调用服务Stop。Attach使用构造输入rootOwner.TryReserveProjection(budget)，并RegisterResource绑定Owner，成功才启动Observe/List/Query；返回false时ProjectionOwner保持null、服务调用计数为0。成功绑定保存lease.Id到ProjectionOwner；控件参数不隐式改变根容量。根/投影池构造见§10.1/10.2，投影槽独立于maxHosts，但bytes/worker计入同一进程总额。

绑定代单调递增，卸载先关闭新投影门、清敏感详情并通过lease.CloseOrRetainAsync启动唯一退订工作。根持有控件、枚举器、每个原Query/List/MoveNext/DispatcherOperation.Task、CTS.CancelAsync/DisposeAsync原Task及迟到buffer，未真实退出不归还投影槽。所有异步投影通过lease.InvokeAsync启动；BCL异步枚举器也登记为资源，不将MoveNext包装超时当成枚举器终止。Dispatcher回调核binding generation、Scope、当前授权、选择原ID+Revision和Loaded，迟到回调只释放自有投影buffer，不显示、不发命令。Source CTS与等待CTS分开，调用方取消只停止等待。

有限退订预算来自构造budget.CloseTimeout。LastProjectionCleanup保存Released或Retained回执并仍保留ProjectionOwner以供宿主rootOwner.JoinProjectionAsync/TryGetProjection；Retained必须Accepted=true且根确认强持才结束等待，失败保留lease引用并禁重绑。旧投影未Released拒绝同控件重绑；服务可继续运行。Detach返回Task不等于释放证明；宿主仅按LastProjectionCleanup和根回执判定。Host UI构造顺序明确为已存在的transport+当前权限委托+§10根 → new IntegrationTransportMonitor(root,new ProjectionBudget(1_048_576,16,TimeSpan.FromSeconds(30))) → AttachAsync → Query/List/Observe → DetachAsync → 用ProjectionOwner查根并Join；任何时候不通过静态ServiceLocator取根。

### 9.2 操作流程与1920×1080布局

唯一验证基线1920×1080，先扣OS任务栏、窗框/标题和宿主状态栏，以下比例以控件最终客户区计；不改显示设置。顶部48 DIP工具区为端点/方向/交付结果筛选、原ID搜索和“查询”；底部28 DIP显示数据时点、作用域、离线/刷新失败。主体初始宽度约左18%端点树、中间52%操作列表、右30%详情；详情下半区回执时间线，列表下方可展开队列趋势。最小可用宽度不足时收拢端点/趋势为可展开面板，列表与身份/Unknown原因始终可见，不把关键命令藏进悬停菜单。

| 区域/控件 | 具体职责与联动 |
|---|---|
| DockLayoutManager + LayoutGroup/LayoutPanel | 承载端点、操作、详情、趋势；列表主面板不允许关闭；保留拖拽分隔/停靠布局。恢复仅宿主受信、版本化布局，失败回默认，不读取消息中的布局路径。 |
| GridControl + TreeListView | Scope内Endpoint→Partition导航，仅显示授权范围与积压/缺口；选择端点更新同一筛选，节点不含设备控制命令。 |
| GridControl + TableView | 只读操作表；固定原OperationId、端点、方向、DeliveryStatus/Stage列，剩余包含年龄/次数/Mapping/错误；状态用图标+文字，颜色不单独传义。原ID可复制，禁止编辑结果。 |
| PropertyGridControl | 详情只读展示ProfileHash/CapabilityHash/原摘要/关联/RunId/Revision；不暴露凭证。随选中行版本更新，选择变化取消旧详情查询，迟到结果核对原ID+Revision后才显示。 |
| 回执GridControl | 按原ReceiptId显示阶段、Authority、证据引用、时点；点击“查看证据”向宿主发InspectEvidence，不将自由字符串当文件路径。技术ACK与业务回执独立行。 |
| ChartControl + XYDiagram2D + LineSeries2D | 队列条数/最老年龄的有限窗口趋势；统计由§9.4显式统计端口有界采样，缺样显示空档/时点，不插值冒充事实；点击时间区间只改变查询过滤，不回放生产消息。 |
| SuperTip / WPF Expander | 查询/重投不确定性、资源未排空及限额恢复说明；Expander展示筛选和非关键详情，当前错误与安全下一动作始终常显。 |

流程固定为选端点→按原ID/交付结果定位→选行看原版本/回执→查询本地原操作→必要时显式“对账”→只有可安全重投且当前权限允许时“重投”。Unknown行主要动作为“对账”；对账Unavailable保持旧阶段并显示“查询失败，稍后再查”，不能刷成未发送。成功重投后仍显示原ID与新RunId，滚动位置不丢。取消显示“取消本地工作”，已可能到达远端时说明需对账，不承诺撤销。

键盘Tab依次筛选→搜索→列表→详情→常显动作；Ctrl+F到搜索，Enter只查询/打开详情，Esc收起筛选Expander，不停止服务；重投/取消需明确按钮和原ID确认，双击不重复提交。UIA提供列名/状态/禁用原因。错误、Unknown、权限撤销和NotDrained同屏可见，详情长hash中间省略且可复制完整值，英文/繁体换行不截断主动作。主题使用宿主统一DevExpress主题、8 DIP间距、单一强调色；新通知淡入不打断选择/焦点，不用无限动画提示离线。

所有表ReadOnly；本机XML对PropertyGridControl.ReadOnly说明存在摘要与value文字矛盾，实施使用true并以编辑尝试/键盘反例验收，不能按错误value描述反转。DataViewBase.AllowEditing=false、DataViewBase.ShowSearchPanelMode=Always，DataControlBase.SelectedItem联动；不猜派生类自有SelectedItem。过长文本用Tooltip/SuperTip显示授权详情，不能用完整载荷填提示。

### 9.3 投影性能与三语

List分页100条、最多缓存5页，最多500行实例，排序/筛选对Store查询而不是把全部历史加载进内存。滚动到下一页按原筛选Cursor；详情最多100条回执，更多由QueryOptions显式取得。Observe事件合并并在每250 ms UI批次刷新（工程节流策略，不是SLA）；每批先核授权，撤权清空敏感详情。服务负载/慢UI不得阻塞I/O，停止订阅不丢持久回执；性能按UI Profile测选行到可见详情及Dispatcher占用，未经WPF实测不标通过。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Query | 查询 | 查詢 | Query |
| Reconcile | 对账 | 對帳 | Reconcile |
| Retry | 重投 | 重新傳送 | Retry delivery |
| Persisted | 已保存，待发送 | 已儲存，待傳送 | Saved, pending send |
| Unknown | 结果未知 | 結果未知 | Outcome unknown |
| NotDrained | 仍在停止，请稍候 | 仍在停止，請稍候 | Still stopping; wait |
| ScopeDenied | 无权查看此范围 | 無權查看此範圍 | Access denied for this scope |

错误详细文案由稳定Code+NextActionKey在模块资源映射，不显示异常堆栈、秘密或AI解释。实际WPF三语、UIA、键盘和布局运行验证为后续UI门；本页§9作为本模块唯一PageContract/控件接入规格，不另等未定义产品页面补设计，也不代表UI已实现。

### 9.4 连接/映射预览、批准提交与完整控件接线

本控件直接消费Core查询和§8.10 Protocols配置服务；没有图像、ROI或3D窗口，也不直接消费viewport WPF/Assembly v0.2，故viewport §10.6～10.9不适用。§9.1既有ProjectionRoot/Close/原Task保持直接复用，不引新Root、不把服务Stop交窗口。监控页与配置页用相同Root lease/权限委托，当前未获生产运行资格不免除本文技术UI设计。

配置能力是端点/映射参数检查和原消息只读预览，不是任意脚本编辑器。唯一服务 `ProtocolConfigurationService(ImmutableArray<ProtocolBinding> active, TimeProvider clock, ProtocolOwnership ownership)` 属Protocols包，公开 `ValidationResult Validate(ProtocolBinding draft)`、`ProtocolRecommendation Recommend(ProtocolBinding draft,TransportOptions options)`、`Task<DecodeResult> PreviewAsync(ProtocolBinding draft,InboundDeliveryIntent sample,CancellationToken ct)`；Preview使用与生产相同BoundedMessageCodec但没有Provider/Store/Apply，测试这些计数必须0。active是构造的不可变只读快照，Service没有隐式Save或reload。配置提交只发事件 `ProtocolDraftProposal(ProtocolBinding Draft, PayloadHash ExpectedActiveAssetHash)`；Host安全/配置Owner再次授权、检查旧hash CAS、保留历史binding资产和Unknown、按§14排空换代后才提交新配置。若CAS/预算/授权失败，旧配置保持，草稿显示错误；不在模块UI直接读写宿主配置文件或数据库。

新可选类 `IntegrationTransportConfigurationPanel : UserControl`（与Monitor同Wpf包）公开构造为 `(IProjectionRootOwner rootOwner, ProjectionBudget budget, ProtocolConfigurationService service, IAuthorityPort authority, Func<CallContext> getCurrentCall)`，方法 `Task<bool> AttachAsync(ProtocolBinding active,CancellationToken ct)`、`Task DetachAsync(CancellationToken ct)`、`void SetLanguage(CultureInfo culture)`，事件 `EventHandler<ProtocolDraftProposalEventArgs> Proposed`（EventArgs封装唯一Proposal属性）。所有UI方法Dispatcher线程；Attach先Root.TryReserveProjection，核authority.CheckAsync(绑定Scope,Query,currentCall...)通过后才拷贝草稿，Preview按Replay动作再次检查，Detach/Unloaded共原Close，不Stop服务。Proposed只提案，无副作用/权限证明，Host提交前必须再次CheckAuthority；关闭面板不提交草稿，重新绑定前旧lease须Released。CLI也能直接Validate/Recommend/Preview后由同Host提交，不依赖该面板初始化。

布局使用固定1920×1080验证视口内扣除任务栏、边框、标题栏和状态栏后的实际客户区：Monitor保持§9.2，端点树选项卡切到“连接与映射”，占原主体不叠加第二全屏。配置页左28%为端点/协议/地址引用/认证引用（隐藏秘密）、中42%为Grid字段规则（角色/路径/类型/必需，最多64行），右30%为只读原消息预览/字段存在性与错误路径。底部常显“检查”“预览”“生成提案”，未授权时保留原因；高级解析限额用WPF Expander渐进显示，不藏现错误/限额。文本编辑使用DevExpress TextEdit.EditValue（属性继承BaseEdit）；枚举用明确只含批准值的选择列表，不以自由字符串新增协议/role；规则编辑Grid允许编辑**草稿**，Monitor/证据所有表仍AllowEditing=false。BaseLayoutItem.AllowClose=false用于必要列表，ItemsSource/SelectedItem从DataControlBase绑定，不猜控件属性。未确认Flyout公开成员不使用它；非关键说明用Expander和已确认SuperTip/ToolTip路径。

样例预览仅显示最多16KiB授权文本/64行字段，原bytes另外由sample原Task保持到退出，错误附字段路径与原摘要；超限“预览已截断”只影响显示，不截断解析输入或改变判定。原Payload/secret不进Tooltip。Validate错误定位草稿字段并禁提案，网络地址测试只允许显式获授权无业务连接健康，不调用Send/Apply/Confirm；默认Preview为纯本地。提案确认展示Scope/Endpoint、旧/新AssetHash、变更字段、Unknown待办数和“旧消息保留原映射”，禁止自动“试发一下”或清队列修复。Tab依次端点→参数→规则→sample→检查/预览→提案；Ctrl+F仍搜索、Ctrl+Enter只Preview，Enter不提交提案，Esc关闭高级面板不退出服务。UIA标注必填、错误路径与禁用原因，三语保持草稿和焦点。

监控趋势公开统计端口为Wpf内 `ITransportMonitorStatisticsPort.ReadAsync(CallContext call,CancellationToken ct) : Task<PortResult<QueueStatistics>>`；Host实现固定Scope、先IAuthorityPort.CheckAsync(Query)，再调用其已注入IPersistencePort.GetStatisticsAsync，不新增IIntegrationTransport方法。Monitor新增明确构造重载 `(IProjectionRootOwner rootOwner,ProjectionBudget budget,ITransportMonitorStatisticsPort statistics)`；原双参数构造保留，仅显示已有列表/回执且趋势标NoSamples，不偷偷找数据源。采用统计重载时每1s有限采样，180点/每series环形缓存，Query失败添加缺样标记而不填0/补线；§9.3的250ms批次与本1s采样均工程节流。取消/重投事件由Host按当前原ID+Revision再次Core权限/CAS验证，UI不根据stage枚举大小决定可点击；Store/能力错误禁副作用，Query/Reconcile作为安全下一动作。两个独立WPF Host分别在MesHost/LineHost已存在Root/服务上new Monitor和配置Panel，显式预算各1MiB/16Tasks/30s，root maxProjections=2/total2MiB；同进程若A/B各同时两控件必须显式扩大到4投影的总bytes/worker，不借已有2槽无限挂控件。不同进程各用其Root；同根仅最多两已预留控件，第三个Attach=false/无服务调用。构造→SetLanguage→Attach→Query/选行或Validate/Preview→Proposed Host处理→finally Detach→JoinProjection→有限根DrainAll；Host业务/cleanup双结果轴沿§10。使用既有Root不重审已闭逻辑。

### 9.5 完整三语状态、动作与恢复词表

以下与§9.3资源表合并使用，所有标签/参数/列/状态/错误/禁用原因均由模块resx按key查，动态值用带CultureInfo格式化占位符，code/hash/ID/JSON/XML不本地化。未列参数标题直接使用本表固定术语加单位，不能暴露CLR属性名当客户文字；规则Role按含义显示，原role token在授权详情单列。未知error用通用“操作失败，请查看诊断代码”，不把服务异常/堆栈作主文案。

| key/覆盖 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title / Configuration | 交付状态 / 连接与映射 | 交付狀態 / 連線與對應 | Delivery status / Connection and mapping |
| Endpoint / Direction / Status / OriginalId | 端点 / 方向 / 状态 / 原操作ID | 端點 / 方向 / 狀態 / 原操作ID | Endpoint / Direction / Status / Original operation ID |
| Inbound / Outbound / Pending | 入站 / 出站 / 待处理 | 接收 / 傳送 / 待處理 | Inbound / Outbound / Pending |
| Succeeded / Rejected / Cancelled / DeadLetter | 已交付 / 已拒绝 / 已取消本地工作 / 待人工处理 | 已交付 / 已拒絕 / 已取消本機工作 / 待人工處理 | Delivered / Rejected / Local work cancelled / Needs review |
| TransportAccepted / BusinessAccepted / Applied | 传输已接受 / 业务已接受 / 应用已确认 | 傳輸已接受 / 業務已接受 / 應用已確認 | Transport accepted / Business accepted / Application confirmed |
| Cancel / InspectEvidence / Refresh | 取消本地工作 / 查看证据 / 刷新 | 取消本機工作 / 查看證據 / 重新整理 | Cancel local work / View evidence / Refresh |
| Check / Preview / Propose / Recommend | 检查 / 预览 / 生成提案 / 参数建议 | 檢查 / 預覽 / 產生提案 / 參數建議 | Validate / Preview / Create proposal / Parameter suggestions |
| AddressRef / CredentialRef / TlsPolicyRef | 地址引用 / 凭证引用 / TLS策略引用 | 位址參照 / 憑證參照 / TLS原則參照 | Address reference / Credential reference / TLS policy reference |
| Protocol / WireVersion / Mapping / Required / Path / Type | 协议 / 线协议版本 / 映射 / 必填 / 字段路径 / 类型 | 通訊協定 / 線路版本 / 對應 / 必填 / 欄位路徑 / 型別 | Protocol / Wire version / Mapping / Required / Field path / Type |
| Bytes / Items / Depth / Timeout / Concurrent | 字节 / 条数 / 深度 / 超时(ms) / 并发数 | 位元組 / 筆數 / 深度 / 逾時(ms) / 並行數 | Bytes / Items / Depth / Timeout (ms) / Concurrency |
| ParseRecovery | 消息格式无效，请检查字段路径 | 訊息格式無效，請檢查欄位路徑 | Invalid message; check the field path |
| CapacityRecovery | 已达限额，请等待积压减少 | 已達上限，請等待待辦減少 | Limit reached; wait for the backlog to decrease |
| AuthRecovery | 权限或凭证失效，请联系管理员 | 權限或憑證失效，請聯絡管理員 | Authorization or credentials expired; contact an administrator |
| NetworkRecovery | 连接中断，原操作待查询 | 連線中斷，原操作待查詢 | Connection lost; query the original operation |
| ConflictRecovery | 原ID内容不一致，请查看原记录 | 原ID內容不一致，請查看原紀錄 | Content conflicts with the original ID; view its record |
| StoreRecovery | 保存结果待确认，请查询原操作 | 儲存結果待確認，請查詢原操作 | Save outcome unknown; query the original operation |
| VersionRecovery | 版本不匹配，请选择批准的映射 | 版本不相符，請選擇核准的對應 | Version mismatch; select an approved mapping |
| LeaseRecovery | 操作版本已变化，请刷新 | 操作版本已變更，請重新整理 | Operation version changed; refresh |
| SequenceRecovery | 序号有缺口，请补齐或对账 | 序號有缺口，請補齊或對帳 | Sequence gap; restore the missing item or reconcile |
| SecurityRecovery | 消息来源或证据无效，请检查连接 | 訊息來源或證據無效，請檢查連線 | Invalid source or evidence; check the connection |
| Truncated / Stale / ProposalConflict | 预览已截断 / 数据未更新 / 配置已变化，请重新加载 | 預覽已截斷 / 資料未更新 / 設定已變更，請重新載入 | Preview truncated / Data is stale / Configuration changed; reload |
| MayHaveReached / RetryConfirm | 消息可能已到达，需对账 / 重投保留原ID，请确认 | 訊息可能已送達，需對帳 / 重新傳送保留原ID，請確認 | Message may have arrived; reconcile / Retry retains the original ID; confirm |
| MissingIdentity / NoSamples | 缺少源消息ID / 暂无样本 | 缺少來源訊息ID / 暫無樣本 | Source message ID missing / No samples yet |

Error Code→资源固定对应：VAL001 ParseRecovery（具体field override）、VAL002/QUEUE001/RESOURCE001 CapacityRecovery、AUTH001 AuthRecovery、CAP001/VERSION001 VersionRecovery、CONFLICT001 ConflictRecovery、NET001/NET002 NetworkRecovery、BUS001 Rejected+端点原代码、LEASE001 LeaseRecovery、STORE001 StoreRecovery、CANCEL001 Cancelled、PARSE001 ParseRecovery、SEQUENCE001 SequenceRecovery、LIFECYCLE001 NotDrained/未启动（按实际ServiceState）、SEC001 SecurityRecovery。字段参数的数值范围来自§3.2/8.10，SuperTip显示当前值/上限/拒绝原因，不编现场SLA。Sample缺单位/客户字段的错误来自原应用映射，不在本控件赋默认或换算。

## 10. 两个独立无UI Host与有界进程根Owner

本节是实施规格与C#调用骨架，尚未编译或运行；不是已交付产品示例。两个Host分别是独立MES互联服务的技术演练A和线体/外部系统服务的技术演练B，均从下面完整DTO自行装配同一Core，不外传transport/profile/payload、不借产品启动补依赖。业务MES/线体语义由正式Owner负责，本节只使用合成消息M与模拟确认点。测试Host/根Owner/端口实现放§12唯一Exe工程，namespace `Asun.Modules.IntegrationTransport.Tests.Hosting`；可发布模拟端口按§15 S1迁入独立Simulator DLL，不能让Core引用测试工程。

### 10.1 DTO装配与两个入口

以下C#块需 `using System.Collections.Immutable;`、`using System.Security.Cryptography;`、`using System.Text;` 和Core namespace。Canonical是§3.4逐字段编码的测试实现，不能调用受测Core指纹方法生成期望值；方法签名为 `PayloadHash Capability(AdapterCapabilities value)`、`PayloadHash Profile(EndpointProfile value)`。自Hash字段为零值暂占位，编码明确排除该字段，随后with设置计算值。

```csharp
public sealed record HostInput(TransportConfiguration Configuration,
    DeliveryIntent Outbound, InboundDeliveryIntent Inbound, CallContext Call);
public sealed record HostBusiness(EnqueueResult Outbound, EnqueueResult Inbound,
    QueryResult OutboundQuery, QueryResult InboundQuery);
public enum HostCleanupStatus { Released, Retained }
public sealed record HostCleanup(HostCleanupStatus Status, Guid OwnerId,
    string? ErrorCode);
public sealed record HostResult(ImmutableArray<OperationId> OperationIds,
    HostBusiness? Business, string? BusinessError, HostCleanup Cleanup);
public static class HostInputs
{
    public static HostInput Create(string site)
    {
        var zero = new PayloadHash(new string('0', 64));
        var bytes = Encoding.UTF8.GetBytes("{}");
        var hash = new PayloadHash(Convert.ToHexString(
            SHA256.HashData(bytes)).ToLowerInvariant());
        var cap = new AdapterCapabilities("sim", "1", "client", "1",
            new PayloadHash(Convert.ToHexString(SHA256.HashData(
                Array.Empty<byte>())).ToLowerInvariant()), zero,
            ImmutableArray.Create("M"), ImmutableArray.Create("host-ref"),
            1024, 1024, true, true, false, true, OrderingMode.Unordered,
            ImmutableArray.Create("sim-only"), ImmutableArray.Create("no-network"));
        cap = cap with { Fingerprint = Canonical.Capability(cap) };
        var profile = new EndpointProfile
        {
            Endpoint = new("e"), AllowedKinds = ImmutableHashSet.Create(
                DeliveryKind.Observation), AllowedSchemas = ImmutableHashSet.Create(
                new SchemaVersion(1, 0)), AllowedMessageNames =
                ImmutableHashSet.Create(StringComparer.Ordinal, "M"),
            Mapping = new("m"), ProfileHash = zero, Capabilities = cap,
            RequiredStage = ReceiptStage.BusinessAccepted,
            MaxReorderItems = 1, GapTimeout = TimeSpan.FromSeconds(1),
            MaxPayloadBytes = 1024, MaxQueueBytes = 1_048_576, MaxQueueItems = 4,
            MaxConcurrentSends = 1, MaxConcurrentApplicationCalls = 1,
            ConnectTimeout = TimeSpan.FromSeconds(1)
        };
        profile = profile with { ProfileHash = Canonical.Profile(profile) };
        var options = new TransportOptions
        {
            MaxPayloadBytes = 1024, MaxQueueBytes = 1_048_576, MaxQueueItems = 4,
            MaxResidentBytes = 1_048_576, MaxConcurrentSends = 1,
            MaxConcurrentApplicationCalls = 1
        }; // OperationTimeout=30s / LeaseDuration=60s，关系校验不省略
        var configuration = new TransportConfiguration(new("t", site, "l"),
            options, ImmutableArray.Create(profile));
        var outbound = new DeliveryIntent
        {
            OperationId = new(Guid.Parse("00000000-0000-0000-0000-000000000001")),
            Endpoint = profile.Endpoint, Schema = new(1, 0), Mapping = profile.Mapping,
            ProfileHash = profile.ProfileHash, CapabilityHash = cap.Fingerprint,
            MessageName = "M", Kind = DeliveryKind.Observation,
            ContentType = "application/json", Payload = bytes, PayloadHash = hash
        };
        var inbound = new InboundDeliveryIntent(
            new(Guid.Parse("00000000-0000-0000-0000-000000000002")),
            profile.Endpoint, "n", "connection-1", 1, profile.ProfileHash,
            cap.Fingerprint, "application/json", bytes, hash);
        return new(configuration, outbound, inbound,
            new CallContext("simulation-authority", "host-" + site));
    }
}
public static class MesHost
{
    public static ProcessRootOwner CreateRoot() => HostRoots.Create();
    public static Task<HostResult> RunAsync(ProcessRootOwner root,
        TimeProvider timeProvider, CancellationToken ct) => HostRunner.RunAsync(
            root, HostInputs.Create("s"), timeProvider, ct);
}
public static class LineHost
{
    public static ProcessRootOwner CreateRoot() => HostRoots.Create();
    public static Task<HostResult> RunAsync(ProcessRootOwner root,
        TimeProvider timeProvider, CancellationToken ct) => HostRunner.RunAsync(
            root, HostInputs.Create("s2"), timeProvider, ct);
}
public static class HostRunner
{
    public static async Task<HostResult> RunAsync(ProcessRootOwner root,
        HostInput input, TimeProvider timeProvider, CancellationToken caller)
    {
        // 先预留；失败不执行Factory，不复制大输入，不创建worker或打开端口。
        HostLease lease = root.Reserve(input.Configuration.Options.MaxResidentBytes);
        HostBusiness? business = null;
        string? businessError = null;
        HostCleanup cleanup = new(HostCleanupStatus.Retained, lease.Id, "IT-DRAIN-001");
        try
        {
            lease.BindInput(input);
            var businessCts = CancellationTokenSource.CreateLinkedTokenSource(caller);
            lease.RegisterResource(businessCts); // 由根在源任务真实结束后Dispose
            businessCts.CancelAfter(TimeSpan.FromSeconds(60));
            // Factory原Task先登记，迟到bundle仍进入同一Owner。
            var bundle = await lease.CallAsync(() => Task.FromResult(
                SimulatedBundle.Create(input, lease, timeProvider)), businessCts.Token);
            var start = await lease.CallAsync(() =>
                bundle.Transport.StartAsync(input.Call, lease.OperationToken),
                businessCts.Token);
            if (start.Status is not (ServiceStatus.Started or ServiceStatus.AlreadyRunning))
                throw new HostCallFailure("IT-HOST-START");
            var a = await lease.CallAsync(() => bundle.Transport.EnqueueAsync(
                lease.Input.Outbound, input.Call, lease.OperationToken), businessCts.Token);
            var b = await lease.CallAsync(() => bundle.Transport.ReceiveAsync(
                lease.Input.Inbound, input.Call, lease.OperationToken), businessCts.Token);
            var qa = await lease.CallAsync(() => bundle.Transport.QueryAsync(
                a.OperationId, new QueryOptions(), input.Call, lease.OperationToken),
                businessCts.Token);
            var qb = await lease.CallAsync(() => bundle.Transport.QueryAsync(
                b.OperationId, new QueryOptions(), input.Call, lease.OperationToken),
                businessCts.Token);
            business = new(a, b, qa, qb); // 快照，不能据此宣称交付完成
            if (a.CommitStatus != CommitStatus.Persisted ||
                b.CommitStatus != CommitStatus.Persisted ||
                qa.Status != QueryStatus.Found || qb.Status != QueryStatus.Found)
                businessError = "IT-HOST-BUSINESS"; // 保留四个原结果
        }
        catch (OperationCanceledException) { businessError = "IT-HOST-CANCELLED"; }
        catch (TimeoutException) { businessError = "IT-HOST-TIMEOUT"; }
        catch (HostCallFailure e) { businessError = e.Code; }
        catch (Exception) { businessError = "IT-HOST-FAULT"; }
        finally
        {
            // 与caller/业务CTS独立。该Task负责异常归一化，不抛出覆盖业务轴。
            cleanup = await lease.CloseOrRetainAsync(TimeSpan.FromSeconds(30));
        }
        return new(ImmutableArray.Create(input.Outbound.OperationId,
            input.Inbound.OperationId), business, businessError, cleanup);
    }
}
public sealed class HostCallFailure(string code) : Exception
{
    public string Code { get; } = code;
}
public static class HostRoots
{
    public static ProcessRootOwner Create() => new(
        maxHosts: 2, maxResidentBytes: 4_194_304, maxWorkers: 12,
        maxProjections: 2, maxProjectionTasks: 16,
        maxProjectionBytes: 2_097_152);
}
```

两个入口各自Create完整DTO、Factory注入全部端口，只有Core DLL相同；scope内可使用相同原ID。两个Host正常验收包括Persisted/Found以及Released，两站点同ID不串数据；停止A不能取消B。快照尚Pending是合法状态，不是完成。完整处理结果由Store/Receipt查询和控制闩锁断言收敛。不得把任一已释放Host的输入数组复用于未结束任务。

### 10.2 根Owner的真实方法、容量和确认移交

`ProcessRootOwner(int maxHosts, long maxResidentBytes, int maxWorkers, int maxProjections, int maxProjectionTasks, long maxProjectionBytes)` 实现§4.6的IProjectionRootOwner，由进程Main调用MesHost.CreateRoot或LineHost.CreateRoot在任何Factory前创建并强持至进程结束；同一进程组合两个Host时只创建一次并显式传两入口。所有参数为正、计数采用checked，示例值唯一见HostRoots.Create。根不是静态全局；HostRoots只是无状态构造函数，不缓存实例。maxHosts=2只限服务槽，独立maxProjections=2/每投影MaxTasks≤16；投影总bytes≤2MiB、每投影示例1MiB，服务各1MiB，进程总额4MiB。服务各预留3业务+1关闭worker，投影各预留1调用+1关闭worker，总上限12；不足即拒绝，不无限Task.Run。两个无UI入口只使用服务槽，真实可选WPF Host持同一个根的IProjectionRootOwner引用按§9显式构造控件，无UI时投影占用=0。方法及实现义务如下，不能以未定义Keeper或fire-and-forget替代：

| 公开方法/属性（Hosting namespace） | 确定实现语义 |
|---|---|
| `HostLease Reserve(long bytes)` | 同步无I/O原子预留host槽、完整实例驻留预算与每Host4个worker额度（3业务/1关闭）；不足抛HostCallFailure(IT-QUEUE-001)，Factory调用数为0。每Host源Task槽与资源登记槽分别最多64、计入驻留预算，控制工作另有已预留槽，超额拒绝新launch/资源分配。创建有唯一Guid的槽并加入根字典，根从此已确认接收所有后续资源；任何退出不自动归还。 |
| `HostLease.OperationToken : CancellationToken` | 根创建并登记的独立操作CTS，仅端口使用此token，不链接caller，不使用会同步触发外部回调的CancelAfter。Caller/60s业务等待CTS只用于CallAsync的WaitAsync；超时finally先关闭连接/准入，再在专用worker安排OperationCTS.CancelAsync并登记其原Task。Caller取消回调不能阻塞关闭信号。 |
| `HostLease.Id : Guid`；`HostLease.Input : HostInput` | Input由Factory调用前的`BindInput(HostInput)`复制并登记，浅复制record不能算复制byte[]。复制前核原/展开上限和额度；记录两消息共享源时仍核每个拥有的独立副本；示例Runner在Reserve后try内首行调用BindInput。 |
| `void BindInput(HostInput input)` | 仅一次；复制Outbound.Payload、Inbound.RawBytes为自有数组，保持源/副本引用到原任务完成；复制预算不足直接拒绝，仍由finally收尾。非载荷DTO保留不可变快照。 |
| `Task<T> CallAsync<T>(Func<Task<T>> launch, CancellationToken waitToken)` | 先预留任务/worker槽，再在有界worker上执行launch；同步前导不得在调用线程执行。登记worker原Task、launch返回的原Task、捕获闭包与结果/迟到结果接收器；worker采用Task<Task<T>>分开跟踪，前导已真实返回Task即可归还worker执行槽，原Task/输入/任务槽直到真实完成才归还。同步前导仍阻塞时worker槽继续保留，取消不丢原Task。包装WaitAsync仅限定等待；闭包/原Task异常全部观察，有限故障摘要与cleanup轴分开。 |
| `void ReserveResourceSlots(int count)` / `void RegisterResource(object resource)` | 先在原槽内预留资源登记槽/声明bytes再构造或Open，超过64个资源槽拒绝且不分配对象。Factory在任何new前一次预留其完整32槽，Provider每次Open先预留1槽；未使用槽在该Factory/Open原Task完成后归还。RegisterResource消费已预留槽、先登记再下一步，不因Closing拒收或再做可能失败的额度分配；不只登记最后bundle。迟到bundle进入原槽，若Closing立即安排该实例RequestClose/Drain，绝不投递已超时caller。资源释放后登记槽可再用，不从未结束任务夺槽。Reserve本身已为OperationCTS与Host等待CTS预留控制资源槽。 |
| `Task<HostCleanup> CloseOrRetainAsync(TimeSpan timeout)` | 快速同步前导将槽标Closing、关闭Factory/新调用门并安排唯一cleanup原Task。先登记并启动Core.StopAsync原Task，使Core接纳/领取门收到关闭信号；不等待完整Stop。随后分别安排所有Adapter/Application.RequestClose和独立OperationCTS.CancelAsync原Task，每一步异常记录后仍安排其余止血信号，不等待取消回调完成才关闭连接。最后并发汇合Factory/业务/Stop/取消原Task与端口Drain，确认账本为空。停止工作使用预留关闭worker，业务同步阻塞不能占满它；Core.Stop前导须快、先关门再异步等待。迟到Core立即登记同代Stop并关闭其迟到Adapter，不接受新Start；不让Start/业务等待完整Stop而Stop反等这些调用退出。独立deadline只停止等待，cleanup原Task继续由根持有。停止/取消回调异常记录cleanup轴，返回Released或Retained，绝不抛出。 |
| `Task<HostCleanup> JoinAsync(Guid ownerId, TimeSpan timeout, CancellationToken ct)` | 只观察已存在槽/cleanup，不重复Stop或重复释放；有限等待到最终Released，超时仍Retained。不可用业务ID冒充OwnerId。 |
| `bool TryGetRetention(Guid ownerId, out HostCleanup receipt)` | 根锁内确认槽强持源/stop/Factory/迟到Task、输入和所有已开资源，返回Retained回执。Close预算耗尽必须此确认成功后才向caller返回Retained；若根接收失败，原Host保留引用/隔离且失败退出，不能宣称“已移交”。 |
| `Task<HostCleanup[]> DrainAllAsync(TimeSpan timeout, CancellationToken ct)` | Main有限等待全部槽；尚Retained明示非零退出/人工处理。不能借进程终止宣称正常释放；永久阻塞只能由获授权进程隔离策略处理，不强杀worker线程。 |

只有Core Stop返回Stopped且Drain.ResourcesReleased=true，所有原Task已完成、端口ActiveCalls=0且ResourcesReleased=true、订阅/租约/worker/副本归还，cleanup才能为Released，再Dispose本槽CTS/模拟资源并归还根额度。Stop成功不自动证明私有Factory已结束。Stopped结果与原任务未结束矛盾时保持Retained。无Core的部分Factory失败也须按账本确认全部释放。业务成功+cleanup失败、业务失败+cleanup成功、双失败均保留两轴；Retained的OwnerId必须可Join，不用业务Unknown替代资源状态。进程根必须可查询占用并对新Host背压，不能不断新建Keeper。

### 10.3 Factory与可控模拟端口：全部方法有消费方

`SimulatedBundle` 为Hosting中public sealed record，属性 `IIntegrationTransport Transport`、`IPersistencePort Store`、`ITransportAdapterProvider Provider`、`ISerializationAdapter Codec`、`IApplicationPort Application`、`IAuthorityPort Authority`。其静态 `Create(HostInput input, HostLease lease, TimeProvider timeProvider)` 的完整装配见§10.5，无I/O：先lease.ReserveResourceSlots(32)，再依次创建并RegisterResource以下实例；最后调用§4构造函数并登记Core，再返回bundle。构造使用lease.Input、Host显式注入的同一TimeProvider和同一Scope。Factory自身可能阻塞/抛异常，由CallAsync有界worker保留；任何部分资源不等bundle才登记。

每个端口公开Async方法进入后即返回Task；不在Task前等待锁/调用外部函数。模拟器每个实例只有短内存锁，锁内不await、不执行事件/取消回调。故障闩锁为 `TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously)`，按方法名+阶段索引；暴露 `Entered`、`Release()`、`Fail(Exception)`、`IgnoreCancellation` 和调用计数，测试等待Entered后才取消/撤权/换代，不用Sleep猜竞态。每调用登记资源/active计数并在真实finally减计数；RequestClose只是Interlocked关闭门+安排解除连接闩锁，不调用用户CancellationTokenSource.Cancel。迟到返回和取消抛错也必须计数收敛。

| 实例/端口方法（签名唯一见§4.3） | 完整模拟实现与闩锁位置 |
|---|---|
| MemoryStore.CheckAsync | 返回StoreHealth(false,true,"sim-v2")；Durable=false不能宣称掉电耐久。HealthFault可返回Unavailable。 |
| RegisterAsync | Scope+ID字典、Inbox来源键字典、分区游标/容量计数在同一短锁事务处理。先查同键同指纹返回原ID/Revision/重复=true，再核冲突、Profile闭包和配额；Atomic先在临时写集验证全批，失败只返全集拒绝，成功一次commit；PerItem逐项同算法。保存自有数组和不可变回执；BeforeCommit闩锁在锁外，AfterCommit闩锁可隐藏确认造成Unknown，不能撤销已写。 |
| ReadAsync / ReadInboxAsync | 错Scope不可读；成功不存在才NotFound，ReadFault为Unavailable，损坏记录为Conflict。Inbox重复按原来源键查，返回首次ID与Profile闭包。 |
| ListAsync | Scope+筛选绑定游标（Guid令牌+实例字典，不自解析任意输入）；按创建序号/ID取PageSize，并返回NextCursor；坏/跨scope游标Conflict，不默认为第一页。 |
| ClaimAsync | 锁内检查due、分区头、未完成状态与原租约；一次选最早一项。过期旧租约但MayHaveReachedRemote=true只允许对账领取，不能直接Send。递增LeaseGeneration，使用注入时钟ExpiresAtUtc；无可领才NotFound。 |
| RenewAsync / ReleaseAsync | 核Scope/ID/worker/代/当前期限，过期或旧代Conflict；Renew原子延长期限，Release只解除同代租约。Release不清buffer，也不将未知交付改完成。 |
| CompareExchangeAsync | 核ExpectedRevision+合法状态迁移+当前租约，NextRevision恰旧+1，历史回执只能追加且ReceiptId冲突检查；快照、回执、nextDue、积压/分区游标一起commit。CASFault可发生提交前/后，后者返回Unknown供原ID读回。 |
| GetStatisticsAsync | 锁内快照按§7.2统计pending/history/最老年龄；未知保留pending，无泄漏scope计数。历史超额模拟明确背压，不自行删除。 |
| SimProvider.OpenAsync | scope/profile/capability必须精确匹配；OpenEntered/OpenLate可延迟创建。Adapter创建即向lease登记后再返回Ok。Closing时迟到Adapter仍登记并RequestClose，不交新service generation。失败返回Unavailable且已有实例走排空。 |
| SimAdapter.Capabilities / SendAsync | getter为不可变快照，无解析/I/O。Send在相同scope+原ID+指纹台账核幂等；正常生成BusinessAccepted Receipt（证据UTF8 "accepted"，SHA256与引用sim/receipt/id绑定）；同键异内容Conflict/NotSent。BeforeSend可NotSent，AfterSend已写远端台账后可MayHaveReached丢ACK，不生成假回执。Send计数不因Query增加。 |
| SimAdapter.QueryAsync | 对相同台账返回Found原Receipt；只有本模拟明确从未提交且锁内确认时ProvenNotApplied+证据sim/not-applied/id；普通缺项故障返回NotFound不等价安全重投。矛盾Receipt故障为Conflict。 |
| SimAdapter.RequestClose / DrainAsync | 关闭门后新Send拒绝，当前已提交事实不撤销。Drain等待所有原Send/Query finally计数为0才返回Drained/Released；超时TimedOut,false；IgnoreCancellation闩锁不因包装超时被删除。 |
| SimCodec.EncodeAsync | 固定profile核闭包与payloadhash，再复制原Payload为EncodedPayload并计算WireHash；工程夹具为identity编码，不宣称标准JSON schema符合性。EncodeGate/超限/损坏hash返回相应错误。 |
| SimCodec.DecodeAsync | HostInput只允许精确原字节7b7d、contentType application/json及已核连接/来源；返回MessageId i、MessageName M、Schema1.0、无Partition/Sequence、ApplicationPayload自有7b7d、正确hash。其它字节/重复属性/截断明确Invalid；不从缺ID创造Guid，不当通用JSON解析器。DecodeGate支持迟到。 |
| SimApplication.Capabilities / ApplyAsync / QueryAsync | 能力为true,true；用scope+原ID+fingerprint台账一次应用，副作用是独立的模拟计数，正常BusinessAccepted Receipt证据sim/application/id。ApplyBefore/After闩锁分别未提交/已提交丢确认；Query回原receipt或具有证明的未应用结果，不复做Apply。异常分支沿Adapter同样Certainty，不触设备/质量事实。 |
| SimApplication.RequestClose / DrainAsync | 与SimAdapter相同关闭门/真实active归零语义，不能因取消caller把active设0。 |
| SimAuthority.CheckAsync | 只认固定引用simulation-authority、input.Scope、动作范围及操作指纹/CAS；固定时钟有效至now+1min、PolicyHash为模拟政策摘要、AuthorityEpoch单调。Revoke令epoch递增、Allowed=false；CheckGate可阻塞。模拟端口在副作用锁内核当前epoch与授权，撤权先于提交则拒绝；提交先于撤权仍保留已提交证据。它只证明模拟围栏，不宣称真实跨进程原子撤权。 |

MemoryStore共享实例用于双Scope测试时同样隔离；模拟“重启”是保留MemoryStore对象、换Core/端口generation，不是进程掉电。正式持久Adapter另受§15 A1门。所有实现不得NotImplemented、无条件Ok、静默吞错、无限Task.Run、同步阻塞取消回调或全局可变JSON设置。

### 10.4 S1可发布Simulator的确定构造与装配

C1/C2已接收的测试夹具范围不依赖S1发布就绪：§10.3端口在唯一BCL Exe内以namespace `Asun.Modules.IntegrationTransport.Tests.Simulation` 实现同名夹具，构造按本节同一确定签名；§10.1/10.5装配仅把using指向这些夹具，不增加DLL引用或第二实现规格。S1获准后这组实现移入独立DLL，测试/Host改using直接引用，不复制保留两套模拟算法；Root始终留在宿主。下面固定的public签名属于发布S1，private测试夹具遵守同参数关系，不自行补默认。

唯一DLL/namespace为 `Asun.Modules.IntegrationTransport.Simulator.dll` / `Asun.Modules.IntegrationTransport.Simulator`，仅引用Core和net10.0 BCL。以下public DTO声明与构造签名是本模块Simulator契约；类实现完整沿§10.3同名方法义务，不另建模拟算法。Root、HostInputs、HostResult、ProcessRootOwner、HostLease和canonical期望编码仍归宿主/唯一Exe，不进入Simulator。

```csharp
public sealed record SimulationLimits(int MaxGates, int MaxActiveCalls,
    long MaxResidentBytes, int MaxResultBytes, int MaxLedgerItems,
    int MaxReceipts);
public sealed record SimulationResourceCallbacks(
    Action<int> ReserveResourceSlots, Action<object> RegisterResource);
public sealed record SimulationInboundCase(TransportScope Scope, EndpointId Endpoint,
    string SourceNamespace, string ConnectionIdentity, long ConnectionGeneration,
    string ContentType, ImmutableArray<byte> RawBytes, DecodedMessage Message);
```

下面表列的是**完整C#公开成员签名与确定语义**，不是带空body/NotImplemented的类实现；实际类需同时实现其Core接口所有方法。参数无默认值/无无参构造，不用可选scope集合或隐式Clock/Root。

| 类型/接口（全部上述namespace、public sealed class） | 公开构造/控制签名 |
|---|---|
| SimulationGate | `SimulationGate(bool initiallyOpen, bool ignoreCancellation)`；`Task Entered { get; }`；`bool IgnoreCancellation { get; }`；`void Release()`；`void Fail(Exception error)` |
| SimulationGates | `SimulationGates(int maxGates, SimulationResourceCallbacks resources)`；`SimulationGate Configure(string method, string phase, bool initiallyOpen, bool ignoreCancellation)`；`bool TryGet(string method, string phase, out SimulationGate? gate)` |
| MemoryStore : IPersistencePort | `MemoryStore(ImmutableArray<TransportConfiguration> configurations, TimeProvider timeProvider, SimulationLimits limits, SimulationGates gates, SimulationResourceCallbacks resources)`；`long GetCallCount(string method)` |
| SimAuthority : IAuthorityPort | `SimAuthority(TransportConfiguration configuration, string authorizationRef, PayloadHash policyHash, TimeSpan decisionTtl, TimeProvider timeProvider, SimulationLimits limits, SimulationGates gates, SimulationResourceCallbacks resources)`；`long Epoch { get; }`；`void Revoke()`；`long GetCallCount(string method)` |
| SimProvider : ITransportAdapterProvider | `SimProvider(TransportConfiguration configuration, SimAuthority authority, TimeProvider timeProvider, SimulationLimits limits, SimulationGates gates, SimulationResourceCallbacks resources)`；`long GetCallCount(string method)` |
| SimAdapter : ITransportAdapter | `SimAdapter(TransportConfiguration configuration, EndpointProfile profile, SimAuthority authority, TimeProvider timeProvider, SimulationLimits limits, SimulationGates gates, SimulationResourceCallbacks resources)`；`long GetCallCount(string method)` |
| SimCodec : ISerializationAdapter | `SimCodec(TransportConfiguration configuration, ImmutableArray<SimulationInboundCase> inboundCases, SimulationLimits limits, SimulationGates gates, SimulationResourceCallbacks resources)`；`long GetCallCount(string method)` |
| SimApplication : IApplicationPort | `SimApplication(TransportConfiguration configuration, SimAuthority authority, TimeProvider timeProvider, SimulationLimits limits, SimulationGates gates, SimulationResourceCallbacks resources)`；`long GetCallCount(string method)` |

构造只校验与有界深拷贝，不开连接/库、启动worker或隐藏UI；所有reference参数必填。Configurations为1..16且Scope不重复的完整配置数组，default/empty/重复Scope拒绝；Scope比较为三个原分量Ordinal。MemoryStore只接纳其中注册Scope与Profile，不把未知Scope自动注册，不允许部分配置相同Scope两份并存。单scope Host传ImmutableArray.Create(input.Configuration)；多scope夹具传明确A/B配置，并以同一宿主Owner持该Store直到两个Core均排空，不把一个可关闭资源同时独占登记到两个根。不同scope同OperationId/MessageId分别保存，错scope读拒绝，A的lease/容量/取消不推进B。

SimAuthority/Provider/Adapter/Codec/Application各只绑定一个configuration；authority.Configuration.Scope/Profiles须与其它注入配置exact匹配，Adapter.profile须为其中完整Profile且hash闭包正确。决策TTL为1s..1h、UTC来自同TimeProvider，policyHash重算模拟政策UTF8字节；AuthorizationRef非空且只允许精确匹配，不回退匿名。Revoke单调递增epoch并禁止新副作用，不能“取消”已提交事实；该Authority不能跨scope共用，合法共享MemoryStore配两独立Authority。Clock由Host注入，禁TimeProvider.System作为隐式默认；诊断Host显式注入System，确定性测试显式注入§12 FixedTimeProvider。

SimulationLimits有效域：MaxGates=1..64、MaxActiveCalls=1..64、MaxResidentBytes=1MiB..Options.MaxResidentBytes（多scopeStore不超过各宿主已联合预留总额）、MaxResultBytes=1..Options.MaxPayloadBytes+8192且checked、MaxLedgerItems=1..100000、MaxReceipts=1..10000。全部正值，不钳制；模拟配置/端点既有限额仍取小。实例账本满/原Task未结束/历史占额满时拒绝或背压，不删Unknown。Limits与配置无默认值；limits是模拟技术限额，不是生产Profile。MemoryStore单实例共享时所有scope计入全局限额，同时每scope/endpoint按自身Options/Profile计数；不得每scope各放满后超过总驻留预算。

SimulationGates的键为Ordinal(method,phase)，method使用§10.3确切类型.方法名（如MemoryStore.RegisterAsync），phase为该表BeforeCommit/AfterCommit/OpenEntered/OpenLate/BeforeSend/AfterSend/ApplyBefore/ApplyAfter/DecodeGate等已定义阶段；不存在的阶段拒绝。未配置键明确表示“不注入故障”，TryGet=false、正常分支不隐式分配gate。Configure只能一次，在操作前ReserveResourceSlots(1)再创建gate并RegisterResource，超过MaxGates拒绝且不创建TCS；同键重复拒绝，不在运行中换gate。Entered是首个调用进入的观察点，Release/Fail中首次结局获胜，其余幂等；Fail只测试脱敏故障，不能把异常文本写诊断。IgnoreCancellation=false合作退出，true须一直被根保留到Release/Fail真实结束；不以取消调用者设置active=0。直接new SimulationGate的消费者也须先在根预留/登记；它没有默认开放状态。

资源callback来自HostLease实例方法，不捕获静态global；ReserveResourceSlots在资源构造/Open前，RegisterResource只快速确认已预留资源的强持，关闭中也不能拒收迟到资源。Provider.Open先预留Adapter登记槽→按相同配置/authority/clock/limits/gates/resources构造SimAdapter→RegisterResource→返回Ok；Closing时原槽关闭信号按§10.2先发，不交新generation。Simulator不Dispose注入的兄弟Authority/Clock/Gates/Store/Root，只释放自身原Task与buffer，整体Owner仍是Host。

### 10.5 两Host直接引用S1装配（替换§10.3私有装配壳）

HostInputs.Create、MesHost/LineHost、HostRunner的完整DTO与try/finally沿§10.1，只把SimulatedBundle.Create实现明确如下。此类属于宿主Hosting，**不是Simulator**；引用上述DLL，不外传私有Store/Provider/Codec变量，不复制其实现。两个入口均明确接收TimeProvider：`MesHost.RunAsync(ProcessRootOwner root, TimeProvider timeProvider, CancellationToken ct)` 与 `LineHost.RunAsync(ProcessRootOwner root, TimeProvider timeProvider, CancellationToken ct)`，分别传Create("s")/Create("s2")给同HostRunner。每个进程先各自CreateRoot，组合进程明确共享一个根；诊断入口传TimeProvider.System，测试传固定Clock实例。HostRunner的签名同步增加TimeProvider参数，并将Factory调用变为下面三参数Create；Core、原Task保留、Stop顺序和finally不变。

```csharp
public sealed record SimulatedBundle(IIntegrationTransport Transport,
    IPersistencePort Store, ITransportAdapterProvider Provider,
    ISerializationAdapter Codec, IApplicationPort Application, IAuthorityPort Authority)
{
    public static SimulatedBundle Create(HostInput input, HostLease lease,
        TimeProvider timeProvider)
    {
        lease.ReserveResourceSlots(32);
        var c = lease.Input.Configuration;
        var p = c.Endpoints[0]; // HostInputs唯一端点；default/非单端点先拒绝
        var limits = new SimulationLimits(16, 32,
            c.Options.MaxResidentBytes, 8192, 128, 128);
        var resources = new SimulationResourceCallbacks(
            lease.ReserveResourceSlots, lease.RegisterResource);
        var gates = new SimulationGates(limits.MaxGates, resources);
        lease.RegisterResource(gates);
        var policyBytes = Encoding.UTF8.GetBytes("sim-policy");
        var policyHash = new PayloadHash(Convert.ToHexString(
            SHA256.HashData(policyBytes)).ToLowerInvariant());
        var authority = new SimAuthority(c, input.Call.AuthorizationRef, policyHash,
            TimeSpan.FromMinutes(1), timeProvider, limits, gates, resources);
        lease.RegisterResource(authority);
        var store = new MemoryStore(ImmutableArray.Create(c),
            timeProvider, limits, gates, resources);
        lease.RegisterResource(store);
        var provider = new SimProvider(c, authority,
            timeProvider, limits, gates, resources);
        lease.RegisterResource(provider);
        var i = lease.Input.Inbound;
        var decoded = new DecodedMessage(new MessageId("i"), "M", new(1, 0),
            null, null, "application/json", i.RawBytes, i.RawHash);
        var fixture = new SimulationInboundCase(c.Scope, p.Endpoint,
            i.SourceNamespace, i.ConnectionIdentity, i.ConnectionGeneration,
            i.ContentType, i.RawBytes.ToArray().ToImmutableArray(), decoded);
        var codec = new SimCodec(c, ImmutableArray.Create(fixture),
            limits, gates, resources);
        lease.RegisterResource(codec);
        var application = new SimApplication(c, authority,
            timeProvider, limits, gates, resources);
        lease.RegisterResource(application);
        var transport = new IntegrationTransport(c, store, provider,
            codec, application, authority, timeProvider);
        lease.RegisterResource(transport);
        return new(transport, store, provider, codec, application, authority);
    }
}
```

SimCodec构造逐case核Scope/Endpoint/Profile/受信连接来源、rawhash与decoded hash后深拷贝，exact原字节命中才解码；同匹配键不同raw/decoded拒绝，不能选第一候选。Input fixture不把缺业务ID填为自动ID，合成i是Host显式构造的预期值。关闭/重启时fixture仍由原Root保持。两个Host的预期均为Persisted/Found与最终Released，Clock/根/gates各实例注入；故障模式仍用§10.3与§12断言，不以公开构造存在宣称S1已实现。

独立可执行宿主的最外层调用如下；两个Main分别用于不同可执行进程，代码在唯一Exe中按Host模式选择（不新增两个测试工程）。Root在任何Factory前建立，finally有限等待所有Host与投影槽；cleanup状态不覆盖业务失败，任何根未Released也非零。不在Main用using自动Dispose未排空根。这里只传BCL与公开Simulator，检测产品不启动。

```csharp
public static class SimulatorEntrypoints
{
    public static Task<int> MesMainAsync(CancellationToken ct) =>
        RunAsync(true, ct);
    public static Task<int> LineMainAsync(CancellationToken ct) =>
        RunAsync(false, ct);
    private static async Task<int> RunAsync(bool mes, CancellationToken ct)
    {
        var root = mes ? MesHost.CreateRoot() : LineHost.CreateRoot();
        int exit = 1;
        bool rootReleased = false;
        try
        {
            var result = mes
                ? await MesHost.RunAsync(root, TimeProvider.System, ct)
                : await LineHost.RunAsync(root, TimeProvider.System, ct);
            exit = result.BusinessError is null &&
                result.Cleanup.Status == HostCleanupStatus.Released ? 0 : 1;
        }
        catch (Exception) { exit = 1; } // 无载荷/凭据输出
        finally
        {
            var final = await root.DrainAllAsync(
                TimeSpan.FromSeconds(30), CancellationToken.None);
            rootReleased = final.All(x => x.Status == HostCleanupStatus.Released);
        }
        return rootReleased ? exit : 2;
    }
}
```

DrainAllAsync必须包含独立投影槽；已Released槽有限tombstone查询不占运行额度。进程最终仍Retained返回2仅是失败观察，不证明资源已归还；保留/隔离策略沿§10.2，正常服务部署不在此夹具里强杀线程。真实Clock/故障测试把TimeProvider.System替换为确定Clock参数并按§12手控gates，禁止把系统时钟诊断Host当确定性测试。

### 10.6 A1-DB两个完整构造Host与原Mutation根

以下是**实现规格/C#调用骨架，未build/run**，namespace仍Tests.Hosting；只引用本Core/Storage/S1及SD Contracts/Runtime/BCL。A/B分别创建HostInputs.Create("s")和Create("s2")，完整DTO、字节、hash、权限call沿§10.1，**没有外传Runtime/Session/Store变量**。实际数据库部署把明确标出的fixture IStorageBackendFactory换成IM-066已获准A1工厂；本节不虚构其PostgreSql工厂名字或“RegisterSql”API。Root/原Task/Mutation/Session全由宿主强持，Core服务、IPersistence Adapter、Runtime是三个生命周期，不能一个Stop充当全释放。

```csharp
using SD = Asun.Platform.StorageDatabase.Contracts;
using SR = Asun.Platform.StorageDatabase.Runtime;
using ITDB = Asun.Modules.IntegrationTransport.Storage;
public sealed record DatabaseHostResult(HostBusiness? Business, string? BusinessError,
    HostCleanup CoreCleanup, HostCleanup DatabaseCleanup,
    ImmutableArray<ITDB.DatabaseMutationRef> Mutations,
    ImmutableArray<ITDB.DatabaseMutationRef> Unresolved);
public static class DatabaseHosts
{
    public static Task<DatabaseHostResult> AAsync(ProcessRootOwner root,
        TimeProvider clock, CancellationToken ct) => RunAsync(root, HostInputs.Create("s"), clock, ct);
    public static Task<DatabaseHostResult> BAsync(ProcessRootOwner root,
        TimeProvider clock, CancellationToken ct) => RunAsync(root, HostInputs.Create("s2"), clock, ct);
    private static async Task<DatabaseHostResult> RunAsync(
        ProcessRootOwner root, HostInput input, TimeProvider clock, CancellationToken caller)
    {
        // DB实例独立预留8MiB。A/B同进程用maxHosts=4/maxBytes=20MiB根，
        // core+database分别一个slot；不借S1示例4MiB根超额度。
        var slots = root.ReserveBatch(ImmutableArray.Create(
            8_388_608L, input.Configuration.Options.MaxResidentBytes));
        var database = slots[0];
        var core = slots[1];
        HostBusiness? business = null;
        string? error = null;
        HostCleanup cc = new(HostCleanupStatus.Retained, core.Id, "IT-DRAIN-001");
        HostCleanup dc = new(HostCleanupStatus.Retained, database.Id, "IT-DRAIN-001");
        DatabaseMutationJournal? mutations = null;
        try
        {
            var waitCts = CancellationTokenSource.CreateLinkedTokenSource(caller);
            database.RegisterResource(waitCts);
            waitCts.CancelAfter(TimeSpan.FromSeconds(60));
            core.BindInput(input);
            database.BindInput(input);
            database.ReserveResourceSlots(32);
            mutations = new DatabaseMutationJournal(32);
            database.RegisterResource(mutations);
            var ownership = new ITDB.DatabasePersistenceOwnership(
                database.ReserveResourceSlots, database.RegisterResource,
                m => { mutations.Remember(m); database.RegisterResource(m); });
            var environment = await database.CallAsync(() => Task.FromResult(
                DatabaseFixtureEnvironment.Create(input, clock, ownership)), waitCts.Token);
            database.RegisterResource(environment);
            // 完整构造Profile/注册/assets/fence见下文。没有新建默认库/Schema。
            var dependencies = new SD.StorageRuntimeDependencies(
                environment.Resolver, environment.Backends,
                environment.Clock, environment.Barrier);
            var factory = new SR.StorageRuntimeFactory(dependencies,
                new SD.StorageFactoryOptions(TimeSpan.FromSeconds(5)));
            database.RegisterResource(factory);
            var runtime = await database.CallAsync(() => factory.CreateAsync(
                environment.Configuration, environment.Authority,
                database.OperationToken).AsTask(), waitCts.Token);
            database.RegisterResource(runtime); // 迟到Create也由database slot接管
            environment.ReferenceResolver.BindRuntime(runtime,
                () => environment.CurrentContext);
            var persistence = new ITDB.DatabasePersistencePort(input.Configuration,
                runtime, environment.Registration, () => environment.CurrentContext,
                environment.MetadataReferences, clock, environment.Options, ownership);
            database.RegisterResource(persistence);
            database.SetDatabaseClosePlan(new DatabaseClosePlan(runtime, persistence,
                environment.ReferenceResolver, () => environment.ControlContext,
                environment.StopIdentity)); // 仅Host方法，不是SD接口
            var transport = await core.CallAsync(() =>
            {
                var sim = SimulatorPorts.Create(input, core, clock);
                var service = new IntegrationTransport(input.Configuration, persistence,
                    sim.Provider, sim.Codec, sim.Application, sim.Authority, clock);
                core.RegisterResource(service);
                return Task.FromResult(service);
            }, waitCts.Token);
            var start = await core.CallAsync(
                () => transport.StartAsync(input.Call, core.OperationToken), waitCts.Token);
            if (start.Status is not (ServiceStatus.Started or ServiceStatus.AlreadyRunning))
                throw new HostCallFailure("IT-HOST-START");
            var a = await core.CallAsync(() => transport.EnqueueAsync(
                core.Input.Outbound, input.Call, core.OperationToken), waitCts.Token);
            var b = await core.CallAsync(() => transport.ReceiveAsync(
                core.Input.Inbound, input.Call, core.OperationToken), waitCts.Token);
            var qa = await core.CallAsync(() => transport.QueryAsync(a.OperationId,
                new QueryOptions(), input.Call, core.OperationToken), waitCts.Token);
            var qb = await core.CallAsync(() => transport.QueryAsync(b.OperationId,
                new QueryOptions(), input.Call, core.OperationToken), waitCts.Token);
            business = new(a, b, qa, qb);
            error = a.CommitStatus == CommitStatus.Persisted &&
                b.CommitStatus == CommitStatus.Persisted &&
                qa.Status == QueryStatus.Found && qb.Status == QueryStatus.Found
                    ? null : "IT-HOST-BUSINESS";
        }
        catch (OperationCanceledException) { error = "IT-HOST-CANCELLED"; }
        catch (TimeoutException) { error = "IT-HOST-TIMEOUT"; }
        catch (HostCallFailure e) { error = e.Code; }
        catch (Exception) { error = "IT-HOST-FAULT"; }
        finally
        {
            // 先发所有关闭信号，两个独立原cleanup同时已启动，然后分别有限观察。
            // SetDatabaseClosePlan后才可能有业务；部分Factory也属于database槽账本。
            var coreClose = core.CloseOrRetainAsync(TimeSpan.FromSeconds(30));
            var databaseClose = database.CloseOrRetainAsync(TimeSpan.FromSeconds(30));
            cc = await coreClose;
            dc = await databaseClose;
        }
        return new(business, error, cc, dc, mutations?.Snapshot() ?? ImmutableArray<ITDB.DatabaseMutationRef>.Empty,
            database.GetDatabaseUnresolved());
    }
}
```

两个独立进程入口也从根开始，不能要求消费方提供未定义Runtime/Session。

```csharp
public static class DatabaseHostMain
{
    public static Task<int> MainAAsync(CancellationToken ct) => RunAsync(true, ct);
    public static Task<int> MainBAsync(CancellationToken ct) => RunAsync(false, ct);
    public static ProcessRootOwner CreateRoot() => new(
        4, 20_971_520, 20, 2, 16, 2_097_152);
    private static async Task<int> RunAsync(bool a, CancellationToken caller)
    {
        var root = CreateRoot();
        DatabaseHostResult? result = null;
        HostCleanup[] final = Array.Empty<HostCleanup>();
        bool fault = false;
        try
        {
            result = a
                ? await DatabaseHosts.AAsync(root, TimeProvider.System, caller)
                : await DatabaseHosts.BAsync(root, TimeProvider.System, caller);
        }
        catch (Exception) { fault = true; }
        finally
        {
            final = await root.DrainAllAsync(
                TimeSpan.FromSeconds(30), CancellationToken.None);
        }
        return !fault && result is not null && result.BusinessError is null &&
            result.CoreCleanup.Status == HostCleanupStatus.Released &&
            result.DatabaseCleanup.Status == HostCleanupStatus.Released &&
            !result.Unresolved.IsDefault && result.Unresolved.IsEmpty &&
            Array.TrueForAll(final, x => x.Status == HostCleanupStatus.Released)
                ? 0 : 2;
    }
}
```

以上0仅是该软件fixture正常且资源已释放；不表示真实数据库/性能/生产PASS。测试从CreateRoot开始，A/B显式传同一FixedTimeProvider；双Host同进程时显式共享同一root并同时调用AAsync/BAsync，最终共同DrainAll。Root最终Retained仍保留所有原引用与OwnerId；返回2不证明释放，也不以退出进程消除Unknown。

数据库装配只取Provider/Codec/Application/Authority，不建多余Core/MemoryStore；因此冻结宿主明确方法
`SimulatorPorts.Create(HostInput input, HostLease core, TimeProvider timeProvider)`
返回 `SimulatorPorts(ITransportAdapterProvider Provider, ISerializationAdapter Codec,IApplicationPort Application,IAuthorityPort Authority)`，
实现只采用§10.5对应4端口/gates的完整相同构造与RegisterResource，**不new MemoryStore/IntegrationTransport**；上例已使用此唯一调用行。不复制S1实现，只复制显式组合根语句。原transport分别注入DB persistence，所以双Host确实走SD注册/事务/读取端口。

#### 10.6.1 完整fixture Profile、目录与真实Runtime依赖

以下全部是Hosting内的public类、直接构造方法，无隐藏全局；fixture不是PostgreSQL/NAS耐久。唯一环境入口为
`DatabaseFixtureEnvironment.Create(HostInput input, TimeProvider timeProvider, DatabasePersistenceOwnership ownership)`，
返回readonly环境属性 `SD.RuntimeConfiguration Configuration; SD.IStorageConfigurationResolver Resolver; SD.IStorageBackendFactory Backends; SD.IStorageClock Clock; SD.IStorageExecutionBarrier Barrier; SD.IStorageAuthority Authority; SD.CallContext CurrentContext; SD.CallContext ControlContext; SD.OperationIdentity StopIdentity; TransportDatabaseRegistration Registration; TransportDatabaseReferenceResolver ReferenceResolver; DatabasePersistenceOptions Options; ITransportDatabaseReferenceMapping MetadataReferences`。所有对象先Reserve/登记再生产，返回后不可变。以下storageScope/inputLimits/runtimeLimits/maintenanceLimits/transport均是明确命名的局部变量，Configuration大写属性表示最终SD.RuntimeConfiguration，不能把它误传给Owner注册工厂。生产依赖输入必须替换明确Profile/BackendFactory/Authority，不沿合成label默默连库。

* transport=input.Configuration；site=transport.Scope.SiteId；storageScope=new SD.StorageScope(transport.Scope.TenantId,transport.Scope.SiteId,transport.Scope.LineId,"integration-service","host-"+site)；store=new SD.StoreRef("queue-store",1,FixtureV("runtime-"+site))。FixtureV(s)=new SD.VersionRef(s,1,new SD.Sha256(SHA256(UTF8("IM046-FIXTURE:"+s)).lowerhex))，实际规范bytes就是这一字节串，resolver exact核ref，不声称真实服务器/域Profile身份。所有外部fixture引用统一该公开算法，不用emptyhash代生产Profile。
* inputLimits=new SD.StorageInputLimits(128,1_048_576,1_048_576,1024,10000,1_048_576,64,1_048_576)；
runtimeLimits=new SD.StorageRuntimeLimits(32,1_048_576,8,64,128,64,128,1_048_576,5s,30s,30s,1d,1h)；
maintenanceLimits=new SD.StorageMaintenanceLimits(1,10000,16MiB,10000,16MiB,100,1MiB,16MiB,16MiB,1h,1s,1h,1d,30s,30s,16MiB,16MiB,16MiB,null,null)；
quota=new SD.StorageQuota(storageScope,"integration-transport",32,1_048_576,4)。无Production/Query/Recovery之外的隐式无限池。上述s/d/h是TimeSpan，MiB是checked long byte值，实际C#用TimeSpan.FromSeconds/Days/Hours和整数，不把这些记号当可编译literal。
* Options=new DatabasePersistenceOptions(1MiB,32,32,100,30s,5s)，scan=new ReferenceScanLimits(10000,16MiB,1000,1MiB,30s,30s)；MetadataReferences=new SimulationMetadataReferences(FixtureV("metadata-empty"))只接受§8.5两消息，保存完整版本引用。ReferenceAuthorityId="it-reference-"+site。先TransportDatabaseRegistrationFactory.Create(transport,storageScope,store,inputLimits,Options,MetadataReferences,ReferenceAuthorityId)得到**真实资产投影hash**，不是FixtureV伪目录；最后ReferenceResolver.Version/Owner/References/Catalog均取实际生成。
* CurrentContext=new SD.CallContext(storageScope,store,new SD.CallerRef("simulation-service","storage-authority-"+site),30s,5s)，ControlContext同scope/store、PrincipalId="simulation-runtime-control"、AuthorityContextId="storage-control-"+site；StopIdentity=new SD.OperationIdentity(storageScope,store.StoreId,store.Generation,"integration-transport","stop-"+site,"stop-"+site,new SD.Sha256(SHA256(UTF8("stop-"+site))))。Stop控制身份不进durable route，给固定真实hash只为合法shape，重复清理保持同identity。
* runtimeProfile=new SD.StorageRuntimeProfile(store.Profile,inputLimits,runtimeLimits,maintenanceLimits,ImmutableArray.Create(quota))；
Relational=new SD.StorageRelationalProfile(FixtureV("relational-"+site),FixtureV("endpoint"),FixtureV("tls"),FixtureV("topology"),FixtureV("technical-schema"),18,12,Pools)；
Pools明确Production/Query/Recovery/Maintenance四个SD.StoragePoolProfile(purpose,FixtureV("credential"),0,2,5,30,60,10,1000)，这只是可控backend fixture的配置，不创建实际连接/Npgsql池或核现场TLS。
* clock=new DatabaseFixtureClock(timeProvider)先构造并登记；References=Registration.References；构造ObservedReferenceCoordinator(new DatabaseFixtureCoordinator(timeProvider,32),32,ownership.RegisterResource)，再BorrowedReferenceFence(observer)，再new TransportDatabaseReferenceResolver(Owner.ReferenceResolver,Owner,Reads中Id=it046.db.references的descriptor,inputLimits,scan,fence,timeProvider,ownership)。原coordinator只被一个成功Runtime拥有，Factory未接管前由原Root持有，启动失败BackendFactory/root按一次Dispose收口，fence借它；Environment只登记持有但不二次Dispose所有Backend子对象。
* 完整Resolved=new SD.ResolvedStorageConfiguration(runtimeProfile,relational,ImmutableArray<SD.StorageFileProfile>.Empty,Registration.Catalog,Registration.References,ImmutableArray.Create<SD.IStorageOwnerReferenceResolver>(referenceResolver),Empty<StorageBackupProfile>,Empty<StorageIsolatedTargetProfile>,Empty<IStorageObjectFormatValidator>,Empty<StorageRetentionPlan>)；无对象、维护或backup需求，因此这些集合明确空，启动仍有References Owner注册；未知文件/维护请求拒绝，不当空集合成功。配置=new SD.RuntimeConfiguration("runtime-"+site,store,ControlContext,relational.Version,Empty<SD.VersionRef>,Registration.Catalog.Version,Registration.References.Version)。
* resolver=new DatabaseFixtureConfigurationResolver(configuration,resolved)实现现SD.ResolveAsync，仅exact匹配5个配置引用/Scope/Store后返回resolved，否则StorageInitializationException UnsupportedVersion。上述clock实现IStorageClock的四个现方法（GetTimestamp/GetElapsedTime/GetUtcNow/DelayAsync），Delay采用BCL TimeProvider可取消timer，原timerRoot持有且结束销毁。barrier=new DatabaseFixtureBarrier(ownership)实现ReachAsync，默认无故障立即完成；测试可明确配置同§10 gate，无静态闩锁。
* authority=new DatabaseFixtureAuthority(ControlContext,CurrentContext)实现现AuthorizeAsync，按完整Scope/Store/Principal/AuthorityContext校验；Control仅runtime_create/stop，Current仅本Owner注册读/写/必要query/release。Epoch/撤销由fixture属性Revoke()控制，拒绝不是空scope通配符，身份不扩大到其它租户。
* backendFactory=new DatabaseFixtureBackendFactory(Registration,observer,clock,ownership)实现现OpenAsync，校验resolved exact refs后构造**独占**DatabaseFixtureBackend/UnsupportedFileBackend/observer/UnsupportedMaintenanceBackend/UnsupportedAssetBackend这5实例返回SD.StorageBackendSet；每new前预留部分构造槽并登记，失败逆序真实Dispose。此factory只能fake backend，不fake IStorageDatabase/StorageRuntimeFactory。所有需要的现接口方法均明确实现，method表如下。

辅助类的唯一构造签名同属Hosting：`DatabaseFixtureClock(TimeProvider timeProvider)`、`DatabaseFixtureCoordinator(TimeProvider timeProvider,int maxLeases)`、`DatabaseFixtureConfigurationResolver(SD.RuntimeConfiguration configuration,SD.ResolvedStorageConfiguration resolved)`、`DatabaseFixtureBarrier(DatabasePersistenceOwnership ownership)`、`DatabaseFixtureAuthority(SD.CallContext control,SD.CallContext current)`、`DatabaseFixtureBackendFactory(TransportDatabaseRegistration registration,ObservedReferenceCoordinator references,SD.IStorageClock clock,DatabasePersistenceOwnership ownership)`。各参数无默认/全必填；Clock与TimeProvider类型明确区分。观察代理和inner协调器的释放Owner仅是成功Runtime（启动失败由BackendFactory），Environment只借用，不重复Dispose；其它Resolver/Clock/Barrier/Authority/Factory归Host，按§10.2由Root在Runtime完成之后释放。fixture历史上限1MiB/32项，队列/tombstone/编码/双页/任务/注册资产所有驻留对象在database槽8MiB总额内checked收费，不能拿扫描16MiB总工作量当驻留许可；不足在分配/事务前拒绝，不提高根限额。

| fixture backend现方法 | 实现义务/明确不支持项 |
|---|---|
| Database.RegisterAsync/ReadRouteAsync/AppendEvidenceAsync/ReadEvidenceAsync/QueryAsync | 按IM-066 §6.3完整identity/Kind/Profile/Binding精确的有界route/receipt/CAS、原技术commit回执；Duplicate Created=false不重Execute，Unknown必须保留原route并用原operation读回。账本属于fake SD技术Owner，不能和it046去重字典混成一个identity。 |
| Database.ExecuteAsync / ReadAsync | 只接受注册12 descriptor exact hash、真实Prepared canonical/WriterToken/PublicationToken/限额；解码本Owner payload后沿§8.6/8.8算法在fake事务写集中全提交或全回滚。原事务技术Receipt与Owner it046变更一锁原子边界；before/afterCommit闩锁决定已知/未知，本地资源active真实finally归零后返回。Read Phase Open返回header、Page按keyset有限页并核refhead，不能fake总量只读首N。 |
| Database.CheckHealthAsync / DisposeAsync | Healthy仅表明fake健康，StoreHealth.Durable=false，不冒称PG；Dispose等待原调用/lease归还，失败/迟到按Root账本，不能清未知receipt。 |
| Database.BeginMaintenanceResumeAsync/ProbeEffectAsync/ApplyMigrationStepAsync/CreateBaseBackupAsync/ReadBaseBackupAsync/ReadCutAsync/RestoreDatabaseAsync/VerifyDatabaseAsync/ValidateOwnerAsync | 本fixture不授权维护/文件效果，按IM-066现签名的对应结果返回UnsupportedVersion/既定无成功payload；ValidateOwner只可运行本Owner已注册只读完整性校验，其余Owner拒绝。无假migration/backup/restore成功。 |
| Coordinator.EnterAsync/ValidateAsync/PreserveAsync/ReconcilePublicationAsync及lease Check/Renew/GetStatus/Dispose | 完整scope/store/owner/token kind/fence不可复用，活动token不靠超时删除；零refs事务Publish与Operation合法，保护期内reference snapshot token前后核查。observer只转发/强持，fake coordinator拥有技术fence事实，引用总体header仍Owner拥有。 |
| File/Maintenance/Assets全部现公开方法 | 每个现签名都实现为对应结果的UnsupportedVersion/Fault、null资源/empty集合、不启动effect、不抛NotImplemented；CheckHealth不作为所需DB健康误失败，未启用文件用途清楚记Unverified。Dispose no-op仅因这些fixture从未建资源，不以此代表真实文件后端排空。 |

#### 10.6.2 Root公开保持、原Mutation查询及收尾顺序

ProcessRootOwner公开新增 `ImmutableArray<HostLease> ReserveBatch(ImmutableArray<long> bytes)` 为Host原子预留方法；先checked验证全集host/worker/bytes，再一次加入根字典，任一不足全部不预留、Factory零调用，无“DB已Reserve、Core失败”漏槽。数据库双Host根明确构造 `new ProcessRootOwner(4,20_971_520,20,2,16,2_097_152)`；核心各1MiB、DB各8MiB，共18MiB，另投影2MiB、worker服务4×4+投影2×2=20，Factory前完整预留。未知/Root Retained不复用旧槽。A/B不同进程各构造此根调用AAsync或BAsync；同进程显式共享同一根，不静态缓存。

`DatabaseMutationJournal(int capacity)` 是Hosting有界保持容器，`void Remember(DatabaseMutationRef mutation)`（同原identity/hash/binding幂等、异内容拒绝、满先拒执行）、`ImmutableArray<DatabaseMutationRef> Snapshot()`，根持有直到原资源和未知事实引用已交宿主确认保留。Mutation引用是原存储技术查询输入，不是第二业务账本；消费者通过Runtime.QueryOperation/ReconcileMutation查看，不读fake私表。记住的Unknown未对账即使资源Released也保留有界结果引用，不借诊断tombstone淘汰后盲重投。

`DatabaseClosePlan(SD.IStorageDatabase Runtime, DatabasePersistencePort Persistence, TransportDatabaseReferenceResolver Resolver, Func<SD.CallContext> CurrentControl, SD.OperationIdentity StopIdentity)` 为Hosting record；
`HostLease.GetDatabaseUnresolved()` 返回 `ImmutableArray<DatabaseMutationRef>`：根保存本Persistence原Close结果的Unresolved；Close尚未给出完整结果、部分Factory/无法对账时保守返回journal全部身份，绝不default/臆测Empty。已有Unknown即使资源Released也在原根有界保留其查询引用，直到宿主明确接收；Runtime已Dispose后的耐久回查通过新获准Runtime.QueryOperationAsync，不能查询旧实例诊断。正常已确认Committed/RolledBack/Rejected且原任务终结的记录不列Unresolved，仍可保留于Mutations追溯。该方法只读，不重Execute。

`HostLease.SetDatabaseClosePlan(DatabaseClosePlan plan)` 仅一次、Root已强持所有借用资源后调用。部分Factory尚未形成plan时也必须保持原Create/Open/后端task，其迟到Runtime进入同一Root并立即安排Stop/Dispose，不让返回值逃出Closing槽。Resolver新增 `Task<DatabasePersistenceDrain> CloseAsync(TimeSpan timeout,CancellationToken ct)`（只关本Resolver新快照门与汇合原snapshot Dispose，不Stop Runtime），每个原Task保留。

Core/DB关闭工作启动顺序固定：Core原Stop先关接纳/领取门 → Persistence.Close与Resolver.Close各先关新工作并发安排已有Session/快照释放 → Runtime唯一Owner立刻登记/调用 `Runtime.StopAsync(new SD.StopRequest(control,originalStopId,Runtime.InstanceEpoch),independentControlToken).AsTask()`，该前导不等待完整Core/Session任务再发信号；然后并发汇合原Core/Adapter/Resolver/Runtime Stop/资源状态查询。Stop回执State=SD.StorageExecutionState.Completed/Result=null/Fault=null且InstanceEpoch/原Identity相符才说明Runtime实例原资源已Released，但仍须核Root原Factory/Mutation/OpenSession/Query/Release tasks完成、Adapter.Close ResourcesReleased=true。最后Runtime.DisposeAsync只调用一次（原ValueTask.AsTask保存），再Environment借用依赖允许释放；失败分别记录cleanup轴，不覆BusinessError。共享Runtime变体由一个RuntimeRoot在所有Adapter已关闭准入后统一Stop，任何Adapter.Close不单独Stop它，不能让A关停B。

Source/lease/body缓存/gate/codec/Session/原storage TaskHandle保持到真实Released；原技术Committed但Session仍Draining时DatabaseCleanup仍Retained。未知commit后Main用Mutations+OwnerId查原技术身份，未取完真值只读，不能建立替代IT ID。若Root确认移交失败，原Host隔离强持而不是给false Released。数据库Main最终也有限DrainAll，任何业务/cleanup/未执行/NotEvaluated资格输出不当生产成功；该Host通过只证明软件结构和fake fault语义。

## 11. 正常、边界与失败案例

| 场景 | 预期结果 |
|---|---|
| 小于上限的只读上报，持久化后收到业务接受 | `OperationState: Persisted → Sending → Draining → Drained → ResourcesReleased → Completed`；`ReceiptStage: Persisted → TransportAccepted → BusinessAccepted`；查询可回读同一摘要。 |
| 同一 `OperationId` 同一摘要重复提交 | 返回原操作快照，不新增发送，不增加业务副作用。 |
| 同一 `OperationId` 内容或 Mapping 改变 | `IT-CONFLICT-001`，旧操作保持不可变；修正必须是显式新操作/更正关系。 |
| 队列达到字节上限 | 返回 `IT-QUEUE-001`，保留旧项，通知背压；不丢结果、不无限分配。 |
| TCP/HTTP 写入后响应超时 | `Unknown`；若适配器支持查询则查原操作，否则保持 Unknown，不盲重发 `Command`。 |
| 外部业务明确拒绝 | `Rejected` + 远端代码/脱敏原因；不按网络错误重试。 |
| 两个 worker 同时领取同一操作 | 只有一个租约代有效；旧租约回调 `IT-LEASE-001`，不能完成新代。 |
| 进程重启后恢复 | 从持久发件箱/Inbox恢复；映射版本和摘要不变；已提交操作只查回执，不重造事实。 |
| 入站同 `MessageId` 不同原字节 | Inbox 冲突，原字节和冲突引用保留；不交应用端口。 |
| 管理 UI 关闭 | 仅退订 UI；服务按声明生命周期继续，操作状态可通过无 UI Query 获取。 |
| 取消正在解码或网络等待的操作 | 等待实际 I/O/回调结束再释放；外部已可能到达时状态为 Unknown。 |
| 批量消息一项拒绝 | 按协议声明逐项或整批；逐项模式返回全部项状态，不以一项成功宣称整批完成。 |

## 12. 测试矩阵与验收断言

文档阶段只定义验收，不宣称已执行。实现必须保存输入快照、配置/映射版本、操作身份、日志追踪和期望/实际结果。

| ID | 层级 | 场景 | 断言 |
|---|---|---|---|
| IT-T01 | Contract | 缺字段、空值、类型、范围、摘要错误 | 稳定 `IT-VAL-*`，不入队。 |
| IT-T02 | Contract | Schema/Mappings/能力版本 | 兼容通过；不兼容 `IT-VERSION-001`，不静默降级。 |
| IT-T03 | Contract | 大整数、非有限数、时间偏移、重复属性 | 原值/存在性可诊断；不先转 `double` 或覆盖取最后值。 |
| IT-T04 | Unit | 同 ID 同内容/异内容 | 前者复用原回执，后者冲突；无第二操作。 |
| IT-T05 | Unit | 退避、次数、期限、死信 | 只重试声明可重试且NotSent错误；预算耗尽为DeadLetter，未知副作用仍为Unknown。 |
| IT-T06 | Integration | 正常只读上报 | 持久确认、网络接受、业务接受阶段不混淆。 |
| IT-T07 | Integration | 有副作用命令 | 仅有授权/能力/查询条件才发送；ACK 不映射 Applied。 |
| IT-T08 | Fault | 断网、DNS/TLS、broker 断开 | 有界重连/重试；队列不丢失；恢复后保持原身份。 |
| IT-T09 | Fault | 写入后响应丢失/超时 | `Unknown`，查原操作；不新 ID 盲重发。 |
| IT-T10 | Concurrency | 两 worker、旧租约、重复回调 | CAS/租约代保护；旧代不能推进新状态。 |
| IT-T11 | Recovery | 崩溃、重启、备份恢复 | 恢复原发件箱/Inbox/回执；不重放已提交设备副作用。 |
| IT-T12 | Recovery | 映射升级在途 | 在途操作使用原 Mapping；新操作使用新版本，历史可查询。 |
| IT-T13 | Resource | 队列满、磁盘满、超大报文、内存压力 | 有界拒绝/背压；无无界解压、泄漏或静默丢弃。 |
| IT-T14 | Cancellation | 解码、发送、等待回执各阶段取消 | 取消与已停止分开；资源/订阅/租约归还。 |
| IT-T15 | Adapter | 模拟 HTTP/TCP/消息总线 | Core 不依赖厂商类型；不同适配器语义一致。 |
| IT-T16 | Consumer-A | 独立 MES 互联 Host | 不启动检测产品即可入队、查询、死信和受控重投。 |
| IT-T17 | Consumer-B | 独立线体/外部系统 Host | 使用同一 Core；命令权限与上报队列分离，未知结果可查询。 |
| IT-T18 | UI（适用时） | 三语、关闭窗口、慢订阅者、键盘/UIA | UI 仅投影/命令意图；无 UI 语义不变；不阻塞 I/O。 |
| IT-T19 | Performance | 冷启动、热路径、并发、长尾 | 按 PF 记录 P50/P95/P99、CPU、内存、队列和恢复时间。 |
| IT-T20 | Security | 凭证过期、来源伪造、重放、日志脱敏 | 权限/来源/重放窗口明确拒绝；日志无秘密和完整载荷。 |
| IT-T21 | Capability | 已返回适配器后撤销/卸载/换包，能力解析迟到 | 后续编码/解码/发送拒绝；旧结果不能准入新配置代；原在途排空且发送事实保留，无静默换版。 |
| IT-T22 | Recovery | 不存在、存储读取失败、原回执/关联损坏 | 三者可区分；失败/损坏不当 NotFound，不重新入队/采纳；恢复后读原身份。 |
| IT-T23 | Replay | 原字节离线解析与生产重投隔离 | 默认回放无生产连接/持久队列/应用写入；原已提交操作只回读；修正不占用旧身份。 |
| IT-T24 | Retention | 终态归档、Unknown积压、历史预算满、Legal Hold | 完成历史退出积压计数但去重仍有效；Unknown保留积压；维护不删受引用/保留数据，超限明确背压。 |
| IT-T25 | Isolation | 两作用域同外部ID、错scope查询/缓存/导出/诊断、撤权 | 去重和结果互不串扰；错范围与撤权访问拒绝，无载荷披露；共享存储隔离独立于UI。 |
| IT-T26 | Performance | 单租户热点、慢站点、离线追赶与新请求竞争 | 按冻结权重/最大等待预算验证可运行端点进展与分区顺序；总资源有界，无饥饿/重连风暴。 |
| IT-T27 | Cancellation | 能力/凭证解析器及其取消回调阻塞/抛异常 | 连接关闭信号仍可执行；原任务继续排空，超时为NotDrained；未退出前不释放借用资源，错误无秘密。 |

通过条件按切片判定：当前Core/Simulator两个合成Host完成§12.1必需模拟断言；Contract/Schema/State/Owner 唯一；未知、拒绝、取消和缺项可查询，无未解释P0/P1。真实存储/协议/WPF/HIL另按§15受影响范围执行，未执行为Unverified；未采纳性能Profile为NotEvaluated，不得把两者合成“全通过”。

### 12.1 唯一BCL Exe、有限执行与必需断言

唯一测试工程为开头binding的 `tests/Modules/integration-transport/Asun.Modules.IntegrationTransport.Core.Tests/Asun.Modules.IntegrationTransport.Core.Tests.csproj`，Microsoft.NET.Sdk/net10.0/OutputType=Exe，Nullable与ImplicitUsings开启，只引用受测工程与.NET BCL，不引xUnit/NUnit/MSTest或待选包。S1以后获准时显式引用Simulator。该Exe始终不引用WPF；U1真实UI验收由§15绑定的WPF消费Host执行T18交互与释放断言，不新增第二测试工程，不以Core Harness代替WPF。未获准的真实后端/协议/HIL不列作当前Core必需case；到对应切片成为必需时不得skip。

确定性固定时钟实现TimeProvider.GetUtcNow/GetTimestamp与CreateTimer：所有timer有限、由测试Advance触发，在锁外调用回调；同截止按登记序排列。回调任务也进根账本。采用§10闩锁，不用真实Sleep控制竞态。所有assert带IT-T编号、输入/期望/实际，任何例外、超时、未完成、必需项跳过、Retained或资源账本非零令Main返回非零；不能只打印失败后返回0。case截止120s、suite截止300s、外层进程截止360s为工程测试控制预算，非生产性能门；正常case只等待Entered/Release/结果，不耗尽这些预算。suite截止停止启动case并关闭根，剩余case标未完成、非零；永久阻塞由外层终止测试进程并记录失败，不能算Released。

| 必需组/编号 | 可执行输入与确定断言 |
|---|---|
| Canonical / IT-T01..04、28 | §3.4四个Golden由测试独立逐字段编码；长度/bytes/Hash完全匹配；集合重排不变、scope/内容/nullable变体、边界lease组合、未知枚举/default集合/空/大/坏hash拒绝且Register/Send/Apply调用为0 |
| Flow / IT-T05..07、09、12、15..17 | 两Host从Create输入启动；用Send/Apply Entered闩锁推进，校验Persisted/Found；ACK丢失后原ID对账Found且Send/Apply计数不增加；NotFound不允许命令盲重投；NotSent总尝试=MaxAttempts、退避/期限有限；Atomic冲突无新写，PerItem返回全部结果；旧Mapping闭包不重解释 |
| Ownership / IT-T10、14、21、27、29 | 在Factory部分构造、Open迟到、Codec/Authority阻塞、取消回调抛错/忽略取消、Send/Apply/Store提交后分别取消/Stop；Close返回Retained且根确认持原Task/输入/迟到资源，新Host限额拒绝。解除闩锁后同OwnerId Join收敛Released，无双释放；Start/Stop竞态和Restart旧代不能推进，旧租约CAS拒绝。以BCL投影callback闩锁验证独立投影额度/原Task保留/确认回执/服务关闭不反等投影；此项不冒充真实WPF卸载 |
| Store / IT-T08、11、13、22、24..26、30 | 模拟不可用/提交后确认丢失、保留Store换Core重启；原ID/回执不丢。容量满/热点/慢站点/BufferGap阻断/租约过期/历史额满有界；WrongScope及坏游标拒绝。真实崩溃/fsync/TLS不在Core模拟资格范围；对应A1/A2成为必需时执行 |
| Security/Replay / IT-T20、23 | 正常/拒绝/epoch撤销/过期引用、伪连接/改raw；撤权先于提交时副作用0，反之保留回执；Replay可Decode但Open/Register/Apply为0；日志无凭证/完整payload |
| Profile / IT-T19、26 | 固定负载/有限deadline/资源账本；按§13与DEV-GOV-010统计。没有采纳Profile输出NotEvaluated，禁止性能PASS；软件不越额度的assert仍须完成，不用NotEvaluated跳过 |
| 后续UI / IT-T18 | U1获准后绑定/退订/卸载/迟到Dispatcher/三语/键盘只读反例/1920×1080；Root投影账本归零，不能只测Core替代WPF |
| S1公开构造 / IT-T31 | 按§10.4/10.5给出每个构造必填参数，two Host分别root/clock/config/callback注入；无参/default/重复Scope/错Authority配置/非法gate key/槽满拒绝且零Open。共享MemoryStore用明确A/B联合Owner，同ID分scope隔离；Revoke(A)不停B；Open迟到Register后才返回，IgnoreCancellation闩锁释放前未Released |
| A1-DB映射 / IT-T32..34 | IT-T32：12条catalog Kind/Purpose/exact codec/Schema/hash/限额与完整Scope绑定，§8.9十资产独立字段生成的bytes/VersionRef逐项吻合、Owner/Catalog无环，Health46/ByOperation86独立字段编码吻合；缺注册/错schema/图像body拒绝，metadata fixture零Refs。IT-T33：真实IM-066 Runtime配可控fake Database/Coordinator/Resolver；引用3条、MaxEntries=1逐三页seq0/1/2到Complete，空总体seq0Complete；最近页重读不重复计量、旧seq拒绝，head/EntityVersion/Barrier/授权变化及页/总/驻留/deadline超额拒绝不Complete；Execute前RememberMutation、重复原Mutation不第二Execute；Atomic冲突零新写、CAS/lease/partition/quota一事务、Unknown回QueryOperation原id而非重投；不能fake整个IStorageDatabase绕过Runtime。IT-T34：§10.6两空Host独立全DTO/Factory装配，含原子ReserveBatch失败零Factory；Session/Open/commit/Release/快照Dispose迟到、撤权读取拒绝、双业务/cleanup失败；SourceTask/Session/原Mutation槽由根保留到实际归还，Close不Stop共享Runtime；真实PG隔离事务/RLS/断线提交/重开耐久在IM-066 A1资格就绪后另跑 |

新增IT-T28=独立Canonical Golden；IT-T29=Factory前根预留、确认保留、业务/cleanup四组合；IT-T30=默认/边界关系、空/冲突/分区完整事务。IT-T31绑定S1公开构造与两个Host；IT-T32..34绑定A1-DB注册/原事务/原操作及Session关闭。当前仅有C1/C2规格接收，未有任何测试执行通过；C1/C2/S1原六项规格接收保持，A1-DB指定指导内容已限定接收（均未运行），各自进入实现验证时全部执行，不能skip。所有旧矩阵项按上表拆出当前模拟断言与后续真实门；测试Harness不能假装实现HTTP/TCP/MQ互操作。

正式实现时执行以下命令（本轮未创建工程、未运行）：

```powershell
dotnet build src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Core/Asun.Modules.IntegrationTransport.Core.csproj -c Release
dotnet build tests/Modules/integration-transport/Asun.Modules.IntegrationTransport.Core.Tests/Asun.Modules.IntegrationTransport.Core.Tests.csproj -c Release
$itTestArgs = @('run','--project','tests/Modules/integration-transport/Asun.Modules.IntegrationTransport.Core.Tests/Asun.Modules.IntegrationTransport.Core.Tests.csproj','-c','Release','--no-build')
$itTestProcess = Start-Process dotnet -ArgumentList $itTestArgs -WindowStyle Hidden -PassThru
if (-not $itTestProcess.WaitForExit(360000)) {
    $itTestProcess.Kill($true)
    $itTestProcess.WaitForExit()
    throw 'integration-transport suite process timeout (exit 124)'
}
if ($itTestProcess.ExitCode -ne 0) {
    throw "integration-transport suite failed: $($itTestProcess.ExitCode)"
}
```

构建各有CI外层120s截止、任何构建非零即不运行；上面run外层实际调用dotnet run，仅调用dotnet test不执行本Exe。脚本throw使验证失败；终止后退出不能冒充资源释放。输出有限case摘要和所有失败ID，不新增每轮过程报告；正式测试记录由既有验收消费者保留。

## 13. 性能预算与可观测性

### 13.1 PF-IT-001测量方法与目标来源

测量/统计唯一采用[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)，本页不复制或修改分位算法。Profile必须先冻结版本/hash、Scope/端点、消息集合、载荷大小分布、积压/历史量、入出站比、分区/缺口、并发、故障时点、时钟与硬件/OS/GC、冷/热/预热、样本计划、最低有效n、有限deadline和目标来源。无采纳Profile可诊断测量，结果统一NotEvaluated，不填造≤5ms/≤50ms等目标。

| 测点 | 开始/结束与失败观察 | 阈值来源 |
|---|---|---|
| 纯校验 | Validate进入→返回；独立于I/O | 已采纳消费者Profile；缺失NotEvaluated |
| 接纳/解码/持久登记 | 入口接纳、Decode/Validate/Store各阶段原Task真实结束；提交Unknown另列 | Profile耐久介质/确认点/时延与失败预算 |
| 发送/应用/回执 | 领取/编码/副作用前记录/实际端口/业务回执分别计时 | Profile协议、消息、RequiredStage和限流 |
| 端到端/取消/恢复/排空 | 接纳→ResourcesReleased；另计取消→实际任务排空→最后资源归还；Unknown/NotDrained不能当完成样本 | DEV-GOV-010统计规则及已采纳目标 |
| 调度/公平性 | 新请求/旧积压、热点/慢站点、每端点最大等待、最老pending年龄、追赶吞吐 | Profile冻结权重/最大等待/RPO/RTO |
| 可选UI | 选择→授权详情可见、Dispatcher占用、Unbind→真实投影释放 | UI Profile及真实1920×1080 WPF验证 |

Options.OperationTimeout/DrainTimeout/LeaseDuration是操作控制预算，不是性能达标阈值；默认30s/30s/60s不证明任何生产SLA。源Task未排空的超时/失败/未读取/删失样本按唯一统计规则另列，不能丢掉后宣称通过。发送/应用丢弃计数必须0；允许合并的投影通知另统计，不能混淆。

唯一驻留上限为Options.MaxResidentBytes；不得另用“队列字节+2×载荷+64MiB”。配额账本在分配/打开之前预留原字节副本、展开/编码buffer、源Task/闭包、bounded worker、事件订阅/页缓存、CTS/租约、根Owner和迟到资源的声明最大驻留值。测量另记录进程峰值/稳态工作集、托管分配/GC、句柄/连接/Task/worker/租约数量及长期斜率；账本限额不冒充精确OS内存。无法上界的Adapter只可隔离到另有明确资源限制的Host，不在本实例无限分配。根按实例预留求和，SourceTask超时仍占额；未知/历史存储与内存分别限额。

### 13.2 诊断字段与指标

结构化日志至少包含 `TraceId`、`OperationId`、`EndpointId`、`MessageId`（若有）、阶段、Revision、LeaseGeneration、Schema/Mapping 版本、错误码、耗时、载荷大小和摘要；凭证、完整秘密、未经授权的原载荷不得写日志。指标至少包括：入队/发送/业务接受/Applied/Unknown 数量，重试和死信数量，队列字节/条数，分区缺口，连接/心跳状态，回执延迟分位数，取消/排空延迟，磁盘水位和资源租约。

按受信作用域/端点分别投影队列年龄、恢复进度、预算占用、历史保留水位和能力版本/限制；区分可连接、可发送、可持久接纳和可恢复，不能仅用 Connected 掩盖存储失败或游标冲突。诊断查询/导出仍受§7.1隔离与脱敏约束，不从指标恢复秘密或完整载荷。

### 13.3 可执行负载、协议测点与软件判据

纯软件Profile P-IT-SW-1是实现验证输入，不是客户SLA：固定Scope=t/s/l与t/s2/l，源消息上限1024bytes、队列4项/1MiB、每端点并发1、两Host Root预算沿§10；数据集包含§8.12的84byteJSON/81byteXML及89byteTCP frame、长度0/超限/截断/重复/坏receipt；本节新负载由字段独立构造并冻结输入hash，既有fixture不复算成新的事实。10次冷构造、100次预热、10000次热Validate/Encode/Decode、每Host1000次Enqueue/Receive/Query（每项真实释放后再接续以遵守队列4），正常1000次完整回执循环（10个独立批次各100case，每批原Host/root/有限EvidencePort在全部case断言及原历史引用已由测试消费者确认接收后真实关闭，再创建下一批；不为正常吞吐提前淘汰未知证据或扩大100项字典）；故障点为beforeSend/afterSend/beforeACK/bodyRead/ReferencePage2/Close callback，每点至少10次受控闩锁。测量最低有效n=1000，不足/超时按§13.1删失与失败独列，分位/统计只按DEV-GOV-010，不另造P99算法。受测协议样例fake不能代真实broker/网络。

负载组：两端点等权轮转（一端持续积压、一端每轮一条）；一个慢application/ACK、一个正常端点；断线后原ID恢复与新请求共队列；10000 refs、MaxEntries=1/100/500的冻结总体扫描（refs合成夹具独立于元数据7b7d，不授生产对象耐久）；有限5页/500行/100回执UI与180点趋势、250ms batch；支持的最大输入边界、强制反序列化预算超额和Retained源Task拒新Root任务。UI仅1920×1080/当前DPI环境，三语长标签和授权撤销，不新增分辨率矩阵。真实PG/broker/现场Profile可扩大数据和并发，先采纳其版本/范围/总预算再测，不直接扩大软件默认。

| 阶段/风险 | 记录的开始→结束、资源与可判定软件门 |
|---|---|
| 解析/资产/推荐 | 原bytes接入→完整Decode/Encode/Freeze返回；token/depth/字段/原Task/分配计数；超限副作用0、旧Asset/Profile不变、不可精确数值拒绝 |
| HTTP/TCP | Open握手→可用；headers→有界body读取；每frame头/body/解码→原bytes结束；同步前导worker与Stream/response真实释放；越界长度不得body分配、redirect不得跨源secret、未知query零重发 |
| MQTT/AMQP | Connect/Attach/Suback、Publish→技术ACK、Inbox persist→原ACK、Query→原ID receipt；有限credit/pending ACK bytes、client/link/callback数量；不允许提前ACK、自动重发未知生产消息或业务Applied伪回执 |
| Reference分页 | Open head/COUNT/SUM→snapshot；每页head核验/索引读/编码→Session Released；全scan总页/entry/实际bytes、resident峰值、原Dispose；稳定一次总体聚合、页读取规模≤页限+1key、变化拒绝、不完整GC/闭包提交次数0 |
| 公平/恢复/Root | 每轮可运行端点机会、最老待办、原Operation Query→明确或Unknown、Close→原最后资源退出；热点不饿死慢/新端点、Root额度拒新、Retained Owner仍可Join |
| UI/配置 | 选择→当前授权详情呈现、Preview→错误定位、Propose→Host批准/拒绝、Unbind→原Task/lease归还；最多500行/100回执/180点、未授权披露0、preview网络/生产调用0、异常不覆盖业务轴 |

软件判据：丢生产消息=0、原Unknown重投次数=0（无明确安全证据时）、重复消息额外Apply=0、跨Scope披露=0、超预算分配/worker/ACK/连接=0、未确认Released=0，迟到结果可用原Owner/identity追踪。它们是确定正确性门而非延迟承诺；吞吐、P50/P95/P99、冷启动/关闭最大时延、GC/句柄长期斜率、RPO/RTO阈值必须由有来源的客户/部署Profile填定，缺数值结果NotEvaluated而不跳过上述软件assert。真实Brokers包额外第三方库内部缓冲峰值必须实测并计入声明预算，无法保证上界则拒此Profile或按批准资源限额独立Host隔离，不在Core隐藏无限缓存。

## 14. 版本兼容、迁移、发布与回退

### 14.1 兼容规则

分别版本化 Core API、Contract/Schema、协议能力和 Mapping。Minor 版本只能增加可选字段/能力；删除字段、改变单位、改变存在性、状态语义或幂等范围必须升 Major 并由迁移说明。未知扩展字段只有在 Profile 允许时保留；未知必需字段、消息类型或版本拒绝。每个在途操作持久化其 Schema/Mapping 版本，升级不重新解释旧操作。

### 14.2 发布单元

发布包必须包含程序集、依赖清单、Contract/Schema 版本、适配器能力矩阵、配置样例、迁移脚本/说明、测试报告、性能原始数据、回退步骤和 SHA-256。禁止把密钥、客户配置、私有表快照或原始生产数据打进包。

### 14.3 回退

1. 停止接受新请求并执行有界排空，导出/保护发件箱、Inbox、回执和死信引用。
2. 记录当前 Core/Schema/Mapping/适配器版本和租约代；旧 worker 全部失效。
3. 回退程序集/适配器时保留持久数据；若旧版本无法读取新 Schema，将操作置为 `VersionMismatch`/`Unknown`，不得删除或重写。
4. 用原 `OperationId` 查询外部结果；只有协议明确幂等且权限重新通过时才允许受控重投。
5. 验证两个消费者的健康、积压、历史查询和死信可见性，再恢复接收新请求。

二进制回退不等于数据回退；禁止通过删除队列、换新 ID 或清空审计记录“恢复成功”。

## 15. 逐切片实施准备、准入与真实外门

主控2026-10-10已独立回读并接收0.2.1-prep的C1/C2/A0六项规格，C1/C2同步为ModuleCoreImplementationReady（仅规格准备）；A0仅为已接收的Core公开端口，不是具体Adapter资格。U1布局/公开投影根绑定/释放指导内容已接收，真实WPF/产品保持PreparationIncomplete / NotReady。S1公开构造/双Host0.2.2-prep内容已由主控预读接收（仅规格准备，真实运行未完成），本轮同步；主控2026-10-11已限定接收A1-DB0.2.3-prep分页/资产/DB双Host指导内容，真实PG statement/fence/RLS/吞吐、WPF、协议及现场资格保持PreparationIncomplete / NotReady。以下六列严格对应DEV-GOV-010 §3.1，整模块DesignReview / Prep、PreparationIncomplete不变；规格接收不是代码、构建、运行或生产通过。

| 切片/真实消费者 | ①边界/第二消费者 | ②API/所有权 | ③无UI装配 | ④案例/断言 | ⑤Benchmark | ⑥工程/路径/顺序 |
|---|---|---|---|---|---|---|
| C1 校验/Canonical/只读Replay；两独立Host | §1/2/10，禁业务与生产端点 | §3/4.1/4.4、v0.2、§7 | §10完整DTO/Codec/Authority；Replay不开Adapter | §3.4 Golden、§11/12 T01..04/23/28/30 | §13纯校验/解析/资源计数，目标缺失NotEvaluated | 唯一Core+唯一Exe；先构造/Validate/Replay，再finally；禁止目录见binding |
| C2 可靠调度/出入站/恢复/生命周期；两Host | §1/2/5/7.1，Store与应用两权威 | §3/4全部端口、§5..7状态、§10根保留 | §10Factory注入全端口；不依赖真实库/协议 | §11/12模拟Flow/Store/Ownership/Security、Unknown/ACK/重启/撤权 | §13端到端、排空、公平/峰值，上限来自Options | 唯一Core+Exe；Start→Enqueue/Receive→Query→Recover/Cancel→finally Stop |
| S1 可发布Simulator；两Host及模块集成人 | §10.3不触设备/业务事实，Durable=false | §10.4确定public构造/参数关系/资源callback，复用§4端口 | §10.1/10.5完整DTO两Host、同DLL显式clock/root callback | §12同fixture及本轮S1断言、active/租约/根账本归零 | §13与固定TimeProvider，模拟时延不作生产门 | 唯一Simulator+同Exe；创建→注入→控制闩锁→Join；ModuleCoreImplementationReady（S1公开构造/双Host规格预读接收，未运行） |
| A1-DB 本模块Owner映射；两技术Host | §8.5独立Adapter，零产品事实，不绕IM-066；§10.6 A/B | §8.5构造、§8.6事务表/编码、§8.7原Mutation/资源、§8.8分页保护、§8.9无环资产 | §10.6完整Profile/DTO/真实Factory/fake后端/Root与有限Main，§8.7借用边界 | §8.8/8.9 Golden与§12 IT-T32..34正常/异常/恢复；真实PG另门 | §13及IM-066冻结方法；§8.8总/页/驻留/时间预算、§10.6根预算；目标未采纳NotEvaluated | §15.1唯一Storage工程+同Exe，禁止产品/驱动/其它目录；指定指导内容限定接收；真实后端/运行资格PreparationIncomplete / NotReady，未build/run |
| A0 技术Adapter公开边界（无具体wire/provider）；Adapter实施者/两Host | §4.3/8，Core不包含协议/DB事实 | §4.3/4.4/8.3能力、未知、关闭/排空 | 注入实现，不猜SDK/存储/协议API | §12 T08/15/21/22/27的契约模拟 | §13开放阶段与资源计数/上界声明 | 接口源码属于唯一Core、测试在同Exe；Open→Encode/Send或Decode/Apply→Query→RequestClose/Drain |
| A2 通用Protocols/Brokers；MES A与线体B | §8.10完整通用技术与标准实例边界，不含板传/质量决策 | §8.10公开binding/connection/auth/evidence/codec，唯一连接Owner与原Query | §8.12两完整无UIHost，同DLL/独立Scope与有限证据端口 | 四Golden与IT-T35/36，原身份/技术ACK/证据保存/撤权/迟到/预算反例 | §13.3明确软件负载和分阶段资源测点，客户SLA缺失NotEvaluated | §15.1唯一Protocols/Brokers工程+同Exe；本轮技术指导准备，尚未独立实施准入/运行 |
| U1 监控与连接/映射配置控件；MES服务/线体服务管理Host | §9角色/流程、控件不Stop服务或写产品配置 | §9公开控件/统计/提案端口、投影Retention、binding generation/授权 | 无UI不加载Wpf；§9.4显式注入服务/权限/投影根，CLI同配置服务 | §9三语/只读/草稿/键盘/迟到/Unbind、§12 T18及IT-T37 | §13.3 UI负载/有限缓存/真实Dispatcher排空 | 下表唯一Wpf工程、同Core Exe保留BCL；原限定内容接收保持，新增配置指导未运行；真实UI由获准WPF Host按T18/37交互验收 |

C1/C2六项已接收并为ModuleCoreImplementationReady，A0端口规格已接收。S1公开构造/双Host内容已预读接收；A1-DB指定指导内容已限定接收，真实PG statement/fence/RLS/吞吐等资格未关闭；U1限定指导已接收，实际宿主接线/真实WPF资格未关闭。A0只冻结可替换端口，不含HTTP/TCP/MQTT/CFX/Hermes或数据库驱动实现。具体技术Adapter以A1/A2逐项开工复核，不得用A0候选契约或首片Core规格替代其方法/wire/持久确认点。所有Host/原Task/cleanup/Golden欠账是内部规格责任，本轮写回本页，不得列成客户外门。

### 15.1 唯一落点与依赖方向

| 受影响切片 | 唯一预定代码工程 | 测试/允许范围 |
|---|---|---|
| C1/C2/A0 | `src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Core/Asun.Modules.IntegrationTransport.Core.csproj`，net10.0/BCL | binding唯一Exe，§10两个Host/根/独立canonical在测试目录，Core不得引用它 |
| S1 | `src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Simulator/Asun.Modules.IntegrationTransport.Simulator.csproj`，net10.0/BCL、仅引用Core | 同Exe显式引用Simulator；namespace Asun.Modules.IntegrationTransport.Simulator，public MemoryStore/SimProvider/SimAdapter/SimCodec/SimApplication/SimAuthority。注入TimeProvider/Scope/Capabilities/资源登记回调，构造无I/O；HostRoot归属宿主，不迁产品业务 |
| U1 | `src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Wpf/Asun.Modules.IntegrationTransport.Wpf.csproj`，net10.0-windows/UseWPF、Core/Protocols及本机DevExpress25.2.3 | 此控件工程目录允许真实UI接入/验收fixture；唯一Core Exe始终net10.0/BCL，不引用或初始化WPF。实际Host/WPF运行验证先绑定获准消费项目及T18输入，不新增第二测试工程或假UI框架 |
| A1-DB Owner映射 | `src/Modules/integration-transport/Asun.Modules.IntegrationTransport.Storage/Asun.Modules.IntegrationTransport.Storage.csproj`，net10.0、Core+IM-066 Contracts/Runtime；namespace Asun.Modules.IntegrationTransport.Storage | §8.5～8.9及§10.6注册/技术表/分页/资产/原操作与Host映射指定指导内容已限定接收；同Exe显式引用受测Adapter。IM-066真实PG接入/耐久资格未关闭，不接生产库 |
| A2通用Protocols/Brokers | §8.10唯一Protocols工程（Core+BCL）与Brokers工程（Protocols+冻结MQTTnet/AmqpNetLite）；同§12唯一Exe显式引用受测包 | 完整protocol/codec/profile/auth/ACK/原ID查询与双消费者设计已闭，§8.12 IT-T35～37；不是运行/生产Ready。客户标准实例/字段和真实认证由对应Owner提供 |

S1唯一构造/控制契约见§10.4，完整两Host DTO与装配见§10.1/10.5；不保留自然语言备选构造。Root归Host，不进Simulator；端口实现义务唯一沿§10.3。A1-DB唯一构造/注册/事务/分页/资产/原Mutation查询和关闭映射见§8.5～8.9/10.6；具体物理后端通过IM-066，不从Core或本Adapter直接引用Npgsql。

### 15.2 真正外门与只阻断的范围

| 门/来源 | 阻断范围 | 无依赖切片可做的事 |
|---|---|---|
| 正式MES/线体标准实例版本/角色、字段与业务确认/幂等/查询政策，由客户/原事实Owner批准 | 对应标准实例/业务映射、真实互操作/产品资格；§8.10内部通用技术已确定，物理动作只属应用Owner | C1/C2/S1/A0合成Contract/模拟未知恢复 |
| 真实存储的耐久确认、重开/断电/备份恢复与保留加密政策；由存储Owner/现场证据给出 | A1真实持久资格；不能把MemoryStore状态保留当fsync/掉电 | C2原子登记/CAS/租约/回执软件语义 |
| 真实凭证、端点授权、跨进程撤权fence；由宿主安全Owner给出 | 实际连接/发送/生产入站；重复Check不是原子撤权证明 | 模拟拒绝/epoch/提交窗口与脱敏 |
| 已采纳客户PerformanceProfile、硬件/负载和RPO/RTO实测 | 性能/长稳达标结论；未采纳NotEvaluated | 有限方法/额度与统计测点冻结、诊断测量 |
| 应用副作用安全互锁、Applied权威回读与客户现场/HIL输入 | 有副作用命令/物理交接生产资格；不属于Core放行权 | 只读Observation、模拟Application/Receipt |
| 正式产品Contract/Owner映射、实际WPF Host/三语/UIA/1920×1080验证 | 产品接线与U1运行资格；规格接收不等于WPF通过 | 公开Core/控件候选及投影释放指导 |

按C1→C2（模拟端口）→S1/A0内容接收→A1/A2各自具体指导→U1实际宿主→真实互操作/耐久/性能/HIL/客户验收推进；可按不依赖关系调整顺序，不把客户/设备无法确定的事实编成默认。不安排AsunImage/DevExpress安装、适配或许可证审核。本轮不创建任何代码工程。

## 15B. 工业协议扩展与 Web 层接口

本节补入架构确认的三类新接口方向：OPC UA Pub/Sub、MQTT Sparkplug B（工业协议扩展）和 Blazor Server Web 层。它们使用本模块已有的 `IProtocolConnectionFactory` / `ProtocolBinding` 框架，不新增模块。

### 15B.1 OPC UA Pub/Sub（机器↔MES，行业标准）

**适用场景**：多台机器统一上报状态/结果给 MES，机器间事件订阅，跨工序关联。OPC UA Pub/Sub 是工业 4.0 的事实标准（IEC 62541），支持 MQTT/UDP 两种传输。

**技术选型**：OPC Foundation 官方 .NET 库 `OPCFoundation/UA-.NETStandard`（MIT，项目内已有只读快照 `docs/references/open-source/OPCFoundation_UA-.NETStandard`）。

**使用规范**：
- 订阅者只订阅已在 `ProtocolBinding.Capabilities` 注册的 DataSetClass；不订阅通配符
- 发布者只发布 `MessageNames` 中注册的 DataSetWriter；不通过宏/变量名动态构造主题
- 所有 UA NodeId 通过 `AddressRef` 注册，不从消息体动态解析
- 连接时核 UA SecurityMode（至少 `SignAndEncrypt`），不接受 `None` 的生产连接

```csharp
// OPC UA Pub/Sub 连接工厂（扩展现有 IProtocolConnectionFactory）
// namespace: Asun.Modules.IntegrationTransport.OpcUa
public sealed class OpcUaPubSubConnectionFactory : IProtocolConnectionFactory
{
    // 订阅 DataSetWriter 的发布/接收
    // 内部使用 OPCFoundation UA-.NETStandard，不向 Core 泄露 UA 类型
}
```

**与 MES 集成的 NTP 时序要求**：
- SPI ↔ AOI 工序关联时，时间误差需 < 50ms
- 所有时间戳使用 `DateTimeOffset.UtcNow`，不用本地时间
- NTP 对时由宿主层负责（Windows Time Service），本模块只记录时间戳，不自行对时

### 15B.2 MQTT Sparkplug B（边缘↔云状态上报）

**适用场景**：机台状态（在线/离线/运行中）、产量、报警实时上报到云端或 MES 看板。

**Sparkplug B 规范**：在 MQTT 基础上定义了标准的 topic 命名（`spBv1.0/GroupID/NodeID/DeviceID`）和 Protobuf payload，消除了自定义 topic 混乱的问题。

**实现规范**：
- `ProtocolBinding.Capabilities` 中声明 `sparkplug-b-v1.0` 标识
- NBIRTH / DBIRTH / NDATA / DDEATH 消息按 Sparkplug B 规范产出，不手写 Protobuf 字段序号
- Sparkplug B 的 `seq` 字段（0-255 循环）由本模块维护，不由宿主写入
- 推荐使用 `Cirrus Link` 或 `SparkplugNet`（MIT）库

```csharp
// MQTT Sparkplug B 适配器标识
// Capabilities 中注册 sparkplug-b-v1.0 时自动启用 Sparkplug 协议封装
public static class SparkplugCapabilityIds
{
    public const string SparkplugBV1 = "sparkplug-b-v1.0";
}
```

### 15B.3 gRPC / REST（批量证据传输）

**适用场景**：
- `gRPC` 双向流：实时推送检测结果、图像片段（适合本地网络高吞吐）
- `REST`（HTTP + JSON）：结果查询、证据文件下载、MES 轮询

**设计原则**：
- 所有 gRPC/REST 端点通过 `ProtocolBinding` 注册，不在代码里硬编码 URL
- 大文件（图像/点云）走 HTTP Range / 分片，不通过 gRPC 流式传输超过 4MB 的单个消息
- gRPC proto 文件版本化，向前兼容（不删除字段，只新增）；proto 文件存放于 `src/Modules/integration-transport/protos/`

```protobuf
// 示例：检测结果推送（inspection_result.proto）
syntax = "proto3";
package asun.integration.v1;

service InspectionResultService {
    // 双向流：实时推送检测结果
    rpc StreamResults (stream ResultRequest) returns (stream InspectionResultMessage);
    // 单向查询
    rpc QueryResult (ResultQueryRequest) returns (InspectionResultMessage);
}

message InspectionResultMessage {
    string batch_run_id = 1;
    string session_id = 2;
    int64 frame_sequence = 3;
    string verdict = 4;           // "pass" | "fail" | "needs_human"
    string model_version_hash = 5;
    double confidence = 6;
    int64 timestamp_utc_ticks = 7;
    // 大字段通过 evidence_ref 引用，不内联
    string evidence_ref = 8;
}
```

### 15B.4 Blazor Server Web 层接口

**定位**：`integration-transport` 提供数据传输能力，Blazor Web 层是它的一个宿主，不是一个独立模块。Blazor 层通过本模块的公开端口消费数据，不直接访问数据库。

**架构原则**：
```
浏览器（只渲染）
    ↕ SignalR（状态推送）
ASP.NET Core + Blazor Server（服务端）
    ↕ integration-transport 模块端口
数据层（storage-database / query 模块）
```

**服务端职责**（在本模块提供的端口基础上）：
- `IStatusProjectionPort`：实时机台状态 → SignalR Hub → 浏览器
- `IResultQueryPort`：检测结果查询 → Blazor 页面
- `IEvidenceStreamPort`：证据图像分片传输（HTTP Range / CDN），不通过 SignalR 传大文件

**Web 层注册协议**：Web 宿主通过 `ProtocolBinding` 向本模块注册 `blazor-server-v1` 能力：

```csharp
// Blazor 宿主注册端口
services.AddIntegrationTransport(config =>
{
    config.RegisterCapability(
        new ProtocolBinding(
            Scope: "web-dashboard",
            Endpoint: "internal",
            Capabilities: ImmutableArray.Create(
                new Capability("blazor-server-v1", "1.0.0"))));
});
```

**坐标传递规则**（保证浏览器与桌面一致性）：
- 服务端只传预先计算好的像素坐标（由 `coordinate-geometry` 模块转换）
- 浏览器只画多边形/标记，不自己做仿射变换
- 这保证 Web 端坐标与 WPF 端坐标精确一致，不出现"Web 上看起来偏了"的问题

**Web 端数据大小约束**：
- 单次结果查询最多 100 条，超出分页
- 证据图像通过 `evidence_ref` 引用，不内联传输
- SignalR Hub 消息 < 32KB，大数据分批推送

### 15B.5 协议选用决策表

| 场景 | 协议 | 理由 |
|---|---|---|
| 机台 ↔ MES 结果上报 | OPC UA Pub/Sub (MQTT transport) | 行业标准，MES 原生支持 |
| 机台状态 ↔ 云端看板 | MQTT Sparkplug B | 标准化 topic / payload，互操作性强 |
| 本地高吞吐结果推送 | gRPC 双向流 | 低延迟，类型安全 |
| MES 轮询查询 | REST HTTP | 通用，MES 易对接 |
| Web 浏览器实时状态 | SignalR (WebSocket) | ASP.NET Core 原生支持，Blazor 集成简单 |
| 证据图像下载 | HTTP Range + CDN | 大文件走专用通道，不阻塞控制平面 |
| SPI ↔ AOI 跨工序关联 | OPC UA 时间戳（NTP < 50ms） | 标准时间戳，跨系统可比较 |

## 16. 自审清单（本模块交付前）

- [ ] 目录外无代码、入口、制程指导、客户项目或历史原件被修改。
- [ ] Core 可在无 UI、无产品 Shell、无设备 SDK 的最小宿主中运行。
- [ ] 出站上报与可能产生副作用的命令分队列、权限、幂等范围和回执阶段。
- [ ] 本地持久、传输接受、业务接受、Applied、拒绝和 Unknown 没有合并。
- [ ] 同 ID 异内容、重复消息、乱序、旧租约、响应丢失、重启和队列满均有明确结果。
- [ ] 取消、超时、排空、线程、buffer、租约和回调释放责任明确。
- [ ] 两个独立消费者使用同一 Core，未复制第二套事实 Store/状态机。
- [ ] UI 只是可选投影，关闭 UI 不停止服务，也不能写业务事实或设备命令。
- [ ] 工程限额与客户性能目标分开；未采纳Profile为NotEvaluated，未执行真实验证为Unverified。
- [ ] 未引入 HALCON/AsunImage 算法或猜测公共 API；AsunControl 仅作为只读边界参考。

本页完成的是 `DesignReview / Prep` 文档交付。实现、真实协议互操作、现场性能、HIL、生产资格和客户验收均未由本页宣称完成。

### 16.1 已接收0.2.1-prep的两次内容自审（2026-10-10）

第一轮沿正常、空/default/超大/坏摘要、原ID重复/冲突、批量两模式、多候选矛盾回执、并发/旧租约/撤权、取消/迟到/恢复/回退走§3～12，修正Unknown不能因耗尽转DeadLetter、默认租约关系、独立操作/等待CTS、SourceTask与worker额度、Stop先发信号再汇合。第二轮从空Host按§10公开DTO/全部端口/根预留/真实finally/双结果轴走查，并核§4.6/9显式投影根输入、独立额度与回执；消除控件隐式取根、先等业务才Stop、迟到资源登记再分配额度的漏洞。

实际执行的是文档内容/字段走查与内存计算：四个canonical按独立字段构造，再对正文hex复算长度和SHA256（148/150/227/248 bytes均吻合）；v0.2活动契约统一、代码围栏成对、无重复标题、Markdown本地文件目标可定位。未运行C#编译、BCL Exe、真实持久/协议、WPF、性能或HIL。此处记0.2.1-prep的原自审事实。主控随后已接收C1/C2/A0六项和U1限定内容，当前精确状态以§15为准；0.2.1自审时S1/A1-DB未接收；该历史停点随后S1公开构造/双Host规格已预读接收，A1-DB当时待接收；当前限定接收范围见§15，不提升整模块PreparationIncomplete。

### 16.2 0.2.2-prep窄修的两轮定向复核

第一轮仅核本轮改动与直接消费者：C1/C2/A0/U1接收范围同步，不把S1/DB/真实WPF提前提升；S1全部构造/required/default/Scope隔离、资源callback/gate/clock与两Host逐项对照，修正旧Factory签名/旧备选构造及19字段Options编码表。数据库逐IPersistence方法对照IM-066已接收的RegisteredTransactionRequest/RegisteredReadRequest/OpenSession/QueryOperation/GetTaskStatus/Release等实际public声明，明确12条Binding/7个InputCodec、可信参数化映射、对象元数据引用及保护快照，原业务ID与技术MutationID分别保持。

第二轮从两个空Host与两个DB Scope沿构造→Register/Claim/CAS→确认丢失→Query原Mutation→Session释放/根保留走查，核Root不进入Simulator、C1夹具不依赖未获准的S1发布DLL、Close不Stop共享Runtime、原Task/迟到结果与旧租约不被释放或重投；复核投影根/Stop已接收语义未退回。独立按字段计算新DB payload Health/ByOperation为46/86 bytes并复核正文hex/Hash；保留四域148/150/227/248 Golden仍吻合。定向结构检查确认版本/状态、本地来源链接、唯一public类型声明/代码围栏，未写或创建其它文件。

以上是指导内容与字节计算检查；没有创建工程、运行C# build/Exe/真实数据库、WPF、协议、性能或HIL。该0.2.2自审当时S1与A1-DB新规格待接收；该历史停点随后S1公开构造/双Host规格已预读接收，A1-DB当时待接收；当前限定接收范围以§15为准；客户/物理资格保留§15明确门，不能作为内部构造/映射欠账的替代。

### 16.3 0.2.3-prep A1-DB两轮有限自审（2026-10-11）

第一轮由实现者按正常→异常→恢复走查：正常路径从A/B的完整HostInput、原子ReserveBatch、fixture真实StorageRuntimeFactory、12条注册Binding/10类资产、ReferenceResolver Open→MaxEntries=1三页→Complete，再到原Mutation Query与Core/Database双Close。异常覆盖页前后Barrier/Owner head/EntityVersion/授权/epoch变化、错误Scope/Store、页/总/驻留/页数/deadline超额、重复最近页、旧sequence/篡改cursor、提交确认丢失、Session/Dispose/Factory迟到和Reserve不足；均保持Empty/Incomplete/Fault、原Task/Mutation/Root槽，不冒称Complete/Released。恢复只按原Snapshot/原技术OperationIdentity有限回查，绝不新建业务ID、重Execute或把Unknown改成NotFound。检查还发现并已修正：ReferenceKey显式K排序、Barrier使用实际HoldStatus、4个数据库CallAsync统一waitCts、fixture TimeProvider/IStorageClock类型边界、tag6不套用PortStatus、Owner/ReferenceCatalog无环和Host有限DrainAll。

第二轮从两个空外部消费者Host A/B走查：A用site=s、B用site=s2，分别创建Root/clock/Configuration/Authority/Runtime/ReferenceResolver/DatabasePersistencePort/SimulatorPorts/IntegrationTransport，所有资源/原Task登记到各自Root；同Root并行时仅共享已声明的Root额度和确定性clock，不共享Scope事实。故障时A的Revoke/Stop/cleanup、Unknown Mutation与Root Retained不影响B；B同样隔离。双Host都只通过公开IM-066 Runtime/Session/QueryOperation/Release/Reference Coordinator接口，不读fake私表、不调用未声明SQL/事务方法。最终Core/Database cleanup与DrainAll必须逐项Released；任一Retained、Unresolved、未观察的迟到任务或业务/cleanup错误都返回非零并保留OwnerId/原引用。内存验证已独立按字段重建§8.9十资产bytes/hash/逐子VersionRef，全部与正文吻合；保留四域148/150/227/248 bytes/Hash复算吻合，Health46/ByOperation86按字段重建吻合。本页代码围栏成对、public类型/标题无重复、13个本地链接目标存在，数据库Host各CallAsync等待token一致。上述为文档自审和内存字段检查，未运行C#、fixture、真实PG、WPF、协议、性能、HIL或生产验收；该自审时A1-DB仍待主控接收；主控随后已限定接收指定指导内容，真实PG statement/fence/RLS/吞吐、WPF、协议及现场资格保持PreparationIncomplete / NotReady。

### 16.4 0.2.4-prep全部批准范围文档准备结论（2026-10-12）

按当前IM-046架构完整能力核实，**可决定的软件设计已闭合，没有需交后续开发者补猜的内部算法/API/架构决定**。该结论覆盖以下全部当前批准范围，而非只覆盖已接收C1/C2；不创建代码工程、不提升真实运行/生产资格。旧研究、§16.1～16.3两轮自审、§3.4/8.6/8.9有效向量直接复用，本轮只修实际缺口。总控只接收状态；本原会话完成新内容自审和文档验证，不等待主控代做内容审核。

| 完整能力/消费者 | 唯一确定指导 | 剩余Owner与门（均不是软件设计欠账） |
|---|---|---|
| 端点/身份/认证/映射/有界校验；MES A与线体B | §1～4、§8.10.1～3/8.11；完整asset/Profile/来源域、secret引用及当前撤权检查 | 宿主安全Owner提供真实凭证/端点/TLS/撤权fence；产品Owner批准所选消息字段/来源与业务确认，模块Owner实现调用/释放 |
| 出入站持久接纳/幂等/批量/回执/Unknown/重试/背压/公平/重启恢复 | §4.3～7.3、§10/12/13；等权轮转、两个ID域、原Operation只读回查、动态列表不冒充事实全集 | IM046实现真实队列/状态机与声明断言；应用Owner提供Apply/Query真实幂等/质量或设备副作用互锁；客户性能/保留窗口由部署/质量Owner采纳 |
| 协议/序列化/技术ACK/业务证据；HTTP/TCP/MQTT/AMQP/标准XML消息桥 | §8.10～8.12；具体Profile/严格JSON/XML、BCL调用、MQTTnet/AMQP.Net Lite版本/实际API与manual ACK、查询拒绝策略；自定义TCP不冒充标准framing | 本模块Owner实施Protocols/Brokers与driver实测；客户/线体Owner提供准确CFX/Hermes标准实例/角色/消息字段/地址/批准query与业务证据；Hermes传板业务状态机/运动不属模块，不能由本包猜协议物理动作 |
| DB技术Owner、完整引用与参考资产/归档/版本恢复 | §7.2～3/8.5～9/10.6/14；稳定head/keyset/count复用、原Mutation/Session/Barrier与无环资产 | IM046实现自身固定codec/SQL/迁移/引用resolver；IM066实现PG statement加载/技术提交/epoch/GC物理fence及RLS/耐久资格；部署Owner提供真实PG/对象域/保留/备份/恢复窗口，未知引用禁止闭包确认 |
| 可发布模拟、两个无UI消费者/有限Root收尾 | §10/12；Core/S1/DB根与原任务/迟到/Unresolved保持 | 模块Owner实施并实际运行；主集成人在代码阶段绑定可审计仓库/准确项目，现文档结论不代build/Exe |
| 监控、连接/映射检查与预览、有限参数建议、三语权限/键盘恢复 | §9.1～5、§8.10.5/12/13.3；不改Core，公开statistics端口/提案事件，Host批准CAS/换代，CLI同服务 | IM046实施Wpf控件/资源与真实双STA Host验收，宿主配置Owner提交提案/批准迁移；viewport与HALCON非直接依赖，本控件无图像区，不适用视口Assembly/HALCON算子 |
| 发布/升级/退役/回退 | §14/15与各唯一工程；旧配置/Unknown/证据和codec可回读才退役，不删除队列换ID | 模块Owner发布测试证据与版本包；部署Owner批准真实切换/维护窗口/回退目标；生产验收由客户/现场Owner执行 |

本轮第一轮自审从实现者正常→异常→恢复：逐新binding/decoder/连接/Receipt→Inbox确认→Query/关闭走查，修正ProfileProjection/Asset/Mapping/ProfileHash自环、原文Codecs的字段规则、receipt与技术ACK不混合、QueryStatus显式而非certainty推断、每次当前认证代与最终fence责任、Connection唯一Dispose Owner、精确长度帧/BOM/escaped重复字段和预算拒绝。第二轮从两空消费者、CLI配置预览及两个可选WPF Host走查：全部构造/数据/Scope/clock/root/权限/回执/建议/提案CAS显式；监控统计不猜IIntegrationTransport新方法，Preview零网络/Store/Apply；A取消、授权撤销、旧generation/迟到ACK/原Unknown不影响B；不依赖产品页面/隐藏初始化/私表/设备质量放行，Root/原任务关闭规则复用。新增证据归档端口把保存结果与资源归还分开，生产Durable与明确SoftwareFixture模式不混合，保存确认丢失只Query原键；同事务引用epoch与启动目录冻结沿IM-066 0.3.1接线，不重算旧资产。四个新Golden已按独立字段重建完整bytes，对正文hex/长度/Hash逐项一致：JSON84/XML81/TCP89/Asset304 bytes；旧§3.4、§8.6、§8.9及附录A与修改前文本逐段比较保持原样，未重复复算已接收向量。代码围栏、标题及节编号、公开类型唯一性和本地文件链接完成定向检查。软件负载仅核规格可执行性，后续真运行必须执行IT-T35～37，不以文档验证代运行通过。

现文档准备结论与实施/验收分开：C1/C2/S1原ModuleCoreImplementationReady六项接收保持，A0端口与A1-DB/U1既有限定内容接收保持；本轮A2与配置/UI完整技术指导已自行收口，仍没有独立实现准入/真实运行证据。整模块DesignReview/Prep，代码/真实PG、broker/XML互操作、WPF、性能/长稳、HIL和现场资格保持PreparationIncomplete / NotReady或相应Unverified；缺实际性能Profile为NotEvaluated。没有为推进准备而建测试工程、过程脚本/报告或改共享/参考原件；本轮完成后停止，不继续代码开发。


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

## 附录 A：模块核心 API Contract v0.2（核心候选契约；逐切片准入）

本节与第 3～6 节合并构成唯一 `Module API Contract v0.2` 候选基线。核心 API 语义对明确获准的 Core 切片具有约束力，但本附录本身不表示准入通过或平台 Contract 已采纳。实现者不得另造第二套核心 DTO、状态机或错误语义；第 3.1 节的 `OperationState`、`ReceiptStage` 是唯一对应类型，附录不得扩大或改变其状态。第 4.2 节明确列出六组公开入口：校验、接纳与离线解析、查询与投影、取消与受控恢复、服务生命周期和排空；“六组”按入口组计数，`StartAsync`/`StopAsync` 同属服务生命周期组。

- `Module API Contract v0.2` 只覆盖无产品事实写入的 Core、Simulator 和显式 Adapter Port。它不把平台 C-01～C-08、客户工艺阈值、最终放行、产品数据库字段或厂商私有类型冻结为模块 API。
- 正文中仍称“候选”的内容，若属于平台 Schema 映射、序列化、Owner、生产资格或客户 Profile，继续保持候选；若属于本模块 Core 的字段/方法/事件/错误/资源语义，则按本节冻结，任何未定义操作必须先补回本指导再编码。
- 本模块无视觉 API；Core、Simulator 和传输适配器不引用 HALCON/AsunImage 签名。协议/存储适配器只按其目标协议和存储的公开签名核对；未核实签名只阻断对应适配器切片，不阻断不依赖它的 Core/Simulator/契约测试。
- 本附录不声明准入状态。具体 Core 切片只有在本指导明确实现范围、命名空间、唯一代码/测试工程、允许/禁止路径，并逐项满足 DEV-GOV-010 §3.1 六项条件且由主任务接收后，才可标记为 `ModuleCoreImplementationReady`；否则保持 `PreparationIncomplete`。
