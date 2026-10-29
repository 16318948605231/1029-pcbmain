# diagnostics：诊断、日志与指标独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, C3, S1`

- 文档 ID：`IM-005-DIAGNOSTICS`（对应 `PKG-005`、`SM-005`）
- 版本：`0.2.3-prep`
- 状态：C1/C2/C3/S1 `ModuleCoreImplementationReady`（仅文档规格，依注入端口）；A1自有装配规格接收，真实适配 `IntegrationPending`；U1可选控件设计规格接收，运行资格未通过。整模块未达到 `ImplementationSpecificationReady`。
- 技术基线：C# / .NET 10；无 UI 核心类库；可选 WPF + DevExpress 25.2.3 投影层
- 规划消费者：全部能力模块、服务宿主、维护工作站和长稳测试工具
- 允许写入范围：本目录。本文是独立模块的唯一实施指导，不产生实现代码或第二套平台契约。
- 模块级设计评审态：`DesignReview`（方案可评审）。§15.1「当前架构全部批准范围的指导准备结论」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

既有接收（2026-10-10，0.2.2-prep）：C1/C2/C3/S1六项文档规格、A1本模块自有装配及U1控件合同/工程挂接/有限解除设计规格已接收。2026-10-11完整范围接续只在本页补规范编码、真实适配映射、支持包/下载/保留及Owner结论，见§15.1；不重复授Core准入，不创建工程或启动实现。编译、BCL、真实WPF、性能、耐久及现场均未执行。

本文定义一个可脱离本检测平台接入其它视觉项目的诊断能力包。它拥有诊断事件、指标和健康投影的接收、查询、订阅及导出生命周期；调用方拥有业务流程、目标关联、工艺解释、质量放行、设备副作用和正式生产证据。第 3～7 节、§8.5～8.6 及附录 A 合并构成本模块唯一 `Module API Contract v0.2` 候选基线，可用于获准的无产品 Core 切片；它不是已批准的平台 Contract/Schema/State/Owner，也不授权生产 SDK。v0.1 从未发布，本文的 `EventId`、指标入口、通知修订和流所有权变更不提供未经批准的迁移承诺。未在本文明确声明的类型、方法或状态必须先修订本文，不得由实现者猜造。

## 1. 职责、非目标与准入

### 1.1 模块负责

1. 接收带稳定关联身份的结构化诊断事件，并在有界缓冲内完成接纳、持久化或明确丢弃/拒绝反馈。
2. 记录计数器、仪表盘值、直方图摘要和健康快照；指标数值不自动成为质量指标或设备状态。
3. 为同一操作提供相关 ID、单调序列和时间域，支持查询、订阅和脱敏导出。
4. 公开存储、时钟、脱敏、健康探针和读取授权适配端口；核心不绑定数据库、消息中间件或某个产品 Shell。
5. 在磁盘满、慢订阅者、接收器故障、进程重启和排空超时时保持可判定状态，并报告自己的丢弃计数。

### 1.2 明确不负责

- 不产生 PCB、PCBA、SPI、AOI、点胶、涂覆或其它制程的缺陷判定、放行结论、目标关联和配方解释。
- 不写入 Board/Attempt/Inspection/Quality/Evidence 等业务事实库，不替调用方提交、撤回或修改生产事实。
- 不从 `ERROR` 日志生成报警，不确认/结束报警，不发设备命令。设备、采集及互联 conditions 的判据与原始观察仍由各原 Owner 负责；报警发生、条件清除关联历史与人工确认/抑制等处理记录由 [IM-068 alarms](../alarms/DEVELOPMENT-GUIDE.md) 唯一指导定义。diagnostics 仅接收相关结构化日志并提供只读查询/投影，不写报警事实或处理记录；设备动作与质量处置仍归各原 Owner。
- 不持有 HALCON 对象、`ImageLibDotNet` 图像句柄、相机/运动/PLC SDK 句柄或产品 ViewModel。视觉引用只能是调用方提供的稳定字符串/哈希/URI。
- 不承诺 exactly-once、跨进程原子事务或网络送达；持久化接受、业务提交和设备 Applied 必须分别表示。
- 不以内存队列、Grid、导出文件或 UI 投影作为事实第二写入权威。

### 1.3 独立性检查

核心类库在无 WPF、无产品 Shell、无隐藏窗口初始化的最小宿主中可运行。存储、时钟、脱敏、健康和订阅均通过构造依赖注入；禁止静态可变单例、Service Locator、读取调用方私表或反射激活未知类型。至少两个不同宿主使用同一包：

| 消费者 | 典型任务 | 必须证明 |
|---|---|---|
| 视觉服务宿主（无 UI） | 算法阶段记录开始/结束、资源等待、错误和指标 | 记录接纳不会同步阻塞算法；实例/操作关联不串；取消和重启状态可查询 |
| 长稳/维护工具（可选 UI） | 采样运行计数、队列、磁盘健康，查询并导出支持包 | 查询/导出可脱敏、慢订阅者隔离；关闭窗口不停止服务或取消其它订阅 |

这两个消费者只能通过本页第 3～7 节及附录 A 定义的同一Core公开候选契约接入（可选控件另消费§8.5～8.6，复用这些Core DTO），不得为某一宿主增加核心分支。本文只保证候选模块语义，不替代平台级 Contract/Schema/State/Owner 登记。

### 1.3A 新架构适配要点

**架构门禁**：`Asun.Diagnostics.Core` 与 `Asun.Diagnostics.Adapters` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Diagnostics.Wpf`（可选诊断控件）可引用。

**Blazor Server Web 层诊断端点**：Web 端（Blazor Server + SignalR）可作为本模块的第三个消费者：
- 只读查询（`QueryAsync`、`SubscribeAsync`）经 `integration-transport` 的 gRPC/REST 端点暴露
- SignalR Hub 推送诊断事件流，但 Hub 层只做**投影**：订阅者慢时由 Core 侧缓冲区按 §6 语义丢弃并报告丢弃计数，Hub 不缓存
- Web 端不直接访问诊断存储；所有查询经 Core 的脱敏端口，`export` 能力在 Web 端默认禁用（避免未脱敏日志外泄）
- 诊断事件的 `CorrelationId`/`OperationId` 与 Web 端请求 ID 显式关联，不复用浏览器生成的 ID 作为事实身份

**架构观测指标的独立采集**：本模块记录的是模块自身与调用方的诊断事件，不承担 Prometheus/OpenTelemetry 指标导出职责。若宿主需要标准指标端点，由宿主将 Core 的 `Snapshot` 投影为 OTel/Prometheus 格式，Core 不内置 exporter 依赖。

**三态仲裁与诊断**：当 `ai-inference` 产出 `AutoResolved`/`NeedsHuman`/`NeedsSampling` 三态结果时，本模块记录仲裁事件（仲裁耗时、命中规则、最终状态），供后续分析自动判定率与人工介入率。仲裁事件只作观察，不改变判定结果。

**HALCON 备选无关性**：本模块不执行视觉算法，不涉及 HALCON/OpenCV 双跑。

## 2. 架构与数据流

```text
调用方（服务/工具/模块）
  → 校验与脱敏
  → 有界接纳队列（按实例隔离）
  → StoreAdapter 批量写入 / 独立内存健康通道
  → 查询、订阅、导出投影
```

接纳与持久化是两个维度：接纳阶段为 `Received → Validated → Accepted | Dropped | Rejected`；对已 `Accepted` 的事件，`PersistenceState` 从 `Pending` 变为 `Persisted`、`NotPersisted` 或 `Unknown`。`Persisted` 只表示注入的存储适配器返回了持久回执，不是 `DiagnosticOutcome` 值。存储故障用独立健康通道报告一次状态和计数，递归记录只保留内存计数，不再写入同一故障存储。

事件和指标必须携带 `InstanceId`；事件必须另有唯一 `EventId`，以及调用链稳定的 `OperationId`，指标通过 `MetricSampleId` 识别一次样本。可选 `TraceId`、`SpanId`、`ParentOperationId`、`CorrelationId` 和 `ResourceRef` 仅用于诊断链路，不是业务身份；调用方负责这些 ID 与业务目标的关系，模块只保证原值保留和同一实例内序列可追溯。`OperationId` 不是事件去重键：同一操作可有 Started、Waiting、Completed 等多个 `EventId`。时间同时保留 UTC `OccurredAt`/`ObservedAt`、接收时间和单调 `Sequence`；本机时钟回拨不能改变序列顺序。

## 3. Module API Contract v0.2：值、配置与结果

以下公开声明统一属于 namespace `Asun.Modules.Diagnostics`，只依赖 .NET 10 BCL；片段使用 System、System.IO、System.Collections.Generic、System.Threading、System.Threading.Tasks。这是拟实现 API，尚未创建或编译；字段、方法、错误与有效域在本文冻结，平台登记及真实后端格式由主任务接收，不能反向改 Core 语义。

### 3.0 身份、状态与输入

```csharp
public readonly record struct DiagnosticInstanceId(Guid Value);
public readonly record struct EventId(Guid Value);
public readonly record struct OperationId(Guid Value);
public readonly record struct CorrelationId(Guid Value);
public readonly record struct MetricSampleId(Guid Value);
public readonly record struct TraceId(string Value);
public readonly record struct SpanId(string Value);
public readonly record struct DiagnosticSequence(ulong Value);
public readonly record struct NotificationRevision(ulong Value);
public enum DiagnosticSeverity { Trace, Debug, Information, Warning, Error, Critical }
public enum DiagnosticOutcome { Accepted, Dropped, Rejected, Cancelled, TimedOut }
public enum DiagnosticPersistenceState { Pending, Persisted, NotPersisted, Unknown }
public enum DiagnosticBatchOutcome { NoWork, Complete, Partial, Failed, Unknown }
public enum DiagnosticLifecycle { Created, Running, Faulted, Draining, Drained, ResourcesReleased, Stopped }
public enum DiagnosticHealth { Healthy, Degraded, Unavailable, Unknown }
public enum DiagnosticStoredKind { Event, Metric, Health }
public enum DiagnosticValueKind { Counter, Gauge, Histogram, Duration, Bytes, Ratio }
public enum DiagnosticEventKind { Started, Waiting, Running, Sent, Received, Retried, Completed, Failed, Rejected, TimedOut, CancelRequested, Cancelled, DrainStarted, DrainCompleted, DrainTimedOut, Unknown }
public enum DiagnosticOperationState { Running, Completed, Rejected, Cancelled, TimedOut, Unknown }
public enum DiagnosticNotificationKind { EventAccepted, PersistenceChanged, MetricRecorded, HealthChanged, Gap }
public enum ReceiptLookupState { Found, NotFound, Unknown, Rejected }
public sealed record DiagnosticEventDraft(
    DiagnosticInstanceId InstanceId, EventId EventId, OperationId OperationId,
    OperationId? ParentOperationId, CorrelationId? CorrelationId,
    TraceId? TraceId, SpanId? SpanId, DateTimeOffset OccurredAtUtc,
    DiagnosticSeverity Severity, DiagnosticEventKind EventKind,
    string Code, string MessageKey, IReadOnlyDictionary<string,string> Attributes,
    ReadOnlyMemory<byte> Payload, string? ResourceRef);
public sealed record MetricSample(
    DiagnosticInstanceId InstanceId, MetricSampleId SampleId, OperationId OperationId,
    DateTimeOffset ObservedAtUtc, string Name, DiagnosticValueKind Kind, string Unit,
    double Value, IReadOnlyDictionary<string,string> Dimensions);
public sealed record MetricDefinition(
    string Name, DiagnosticValueKind Kind, string Unit, double Minimum, double Maximum,
    IReadOnlyList<string> DimensionKeys, IReadOnlyList<double> BucketUpperBounds);
public sealed record HealthSample(
    Guid SampleId, Guid InstanceEpoch, string CheckId, string SourceId, string SourceVersion,
    DateTimeOffset ObservedAtUtc, long StartedTimestamp, long EndedTimestamp,
    DiagnosticHealth State, double? Value, string? Unit, string? EvidenceSha256,
    string? ErrorCode);
```

### 3.1 有效域、复制与脱敏

| 字段/规则 | 冻结行为 |
|---|---|
| Guid 身份 | 非 Empty；实例不匹配拒绝 DG-VAL-001；一个 runtime 一个实例 |
| EventId / SampleId | 调用方生成并在重试复用；OperationId可关联多个事件/样本，不能据它去重 |
| TraceId / SpanId | Trace为32个小写hex，Span为16个小写hex；不能全零；Span非空要求Trace非空；同跨度多事件合法 |
| ParentOperationId | 非Empty且不同于自身；父记录未到达保留缺口；不按线程/时间补父 |
| UTC时间 | Offset为零，保留原精度；ReceivedAt另取TimeProvider UTC；截止只用单调时间 |
| Code / MessageKey | Code匹配 `^[A-Z0-9][A-Z0-9_.-]{0,127}$`；MessageKey为1–256 UTF-8 bytes |
| Attributes | ≤32对，键1–64 ASCII且Ordinal唯一，值≤1024 UTF-8 bytes；重复键/别名冲突拒绝 |
| Payload | 空或UTF-8 JSON object，≤32个平级string/bool/有限number/null字段；不允许嵌套、数组、重复键、未知字段或任意二进制；不放图像/原始请求响应正文 |
| ResourceRef | 可空，≤512 UTF-8 bytes；策略登记的稳定标识；不允许带凭证URL、原始路径/连接串/SDK序列化 |
| Sequence / Revision | 从1开始ulong，0不分配；溢出Faulted，不回绕；每次创建新Guid InstanceEpoch |
| 指标 | Name为1–128 ASCII且在定义中；Kind/Unit完全匹配定义；Value有限且在定义域；维度≤8对，键须登记、值≤128 UTF-8 bytes |
| 指标桶 | Histogram/Duration边界有限严格递增、≤64；末端隐含+∞；其它Kind桶为空；Minimum/Maximum有限有序 |
| 健康样本 | SampleId非Empty；Check/Source为1–128 ASCII，SourceVersion为1–128 UTF-8 bytes；值/单位同时有或无，值有限；起止同epoch单调时间域且结束≥开始；hash若有为64小写hex |
| 未知枚举/版本/单位 | 拒绝，历史不支持版本DG-VER-001；不把未知转成功 |

调用方在调用期间不得并发修改输入。Core在接纳前复制有界输入、脱敏并生成自有不可变记录；返回后调用方可立即复用缓冲。不得保留延迟格式化lambda、异常实例、ThreadStatic scope或调用方字典。事件/指标身份摘要覆盖脱敏后规范输入及配置/策略/指标修订，不含接收时刻、epoch或分配序列：固定字段顺序、字典键Ordinal排序、UTC ISO8601 round-trip、double invariant round-trip、UTF-8 JSON；负零规范为0，禁止NaN/Infinity。重试跨epoch使用同身份仍比较相同摘要；更改配置修订需新身份。不同原输入脱敏为同内容不造成秘密比较泄露。内部健康存储校验的epoch域见§3.1.1，不混作跨epoch事件身份。

IRedactionPolicy必须同步、纯内存、有界且不可变白名单，对Code/MessageKey/Attributes/Payload/ResourceRef/Dimensions统一校验；未知字段失败安全。秘密直接移除或拒绝，低熵密码/Token不能用裸SHA冒充脱敏。必要的稳定tokenization由宿主批准适配器在入参前完成。失败DG-SEC-002，只增独立内存计数，原载荷不入日志/异常。Core不接纳SecurityAudit/ProductEvidence，Severity不替代正式Owner。

#### 3.1.1 规范编码的精确边界

事件/指标身份摘要、读取审计摘要和NDJSON共用唯一私有编码组件，不增加公开codec API。使用.NET 10 `Utf8JsonWriter`，`JsonWriterOptions`固定`Encoder=JavaScriptEncoder.UnsafeRelaxedJsonEscaping, Indented=false, SkipValidation=false`；属性名显式camelCase，不使用record默认序列化、运行时命名策略或当前Culture。字符串拒绝未配对UTF-16代理项及无效UTF-8，不做Unicode归一化；转义交给该固定encoder，不同用途不能换用Default或另一个encoder。该输出只作为JSON数据/纯文本，不内嵌HTML/script；UI按文本显示。格式版本绑定该规范，目标运行时升级导致字节改变时必须升级格式/codec并保留旧读法，不静默改变既有摘要。

Guid/Trace/Span/Sequence/Revision等值包装类型均写其Value标量，不输出额外value对象；Guid为小写D；UTC先验证Offset=0，再以`ToString("O", CultureInfo.InvariantCulture)`写字符串（七位小数及`+00:00`，不替换成Z）；整数用十进制完整精度，不经double；有限double先把正负零统一为0，再以`ToString("R", CultureInfo.InvariantCulture)`并`WriteRawValue(text, skipInputValidation:false)`写入。Payload的number先按double读取并检查有限/域，不能混用decimal或保留调用者词法；`1`与`1.0`、`-0`与`0`相同。字典/Payload键按StringComparer.Ordinal排序，可空字段全部写null，空字典写`{}`，空Payload写null。规范JSON不含BOM/空白/换行；只有NDJSON行最后追加一个0x0A，计入实际字节/hash。ContentSha256是小写64hex SHA-256。

| 编码用途 | 固定字段次序及边界 |
|---|---|
| Event身份摘要 | 顶层`schemaVersion, configRevision, redactionRevision, metricRegistryRevision, event`；event依DiagnosticEventDraft声明次序转换成camelCase。输入已经脱敏；不含ProducerVersion、AdapterId、接收UTC/单调值、epoch、Sequence或ContentSha256本身。重试只比较该完整规范输入，不比较原秘密。 |
| Metric身份摘要 | 同上四个修订字段，最后为`metric`；metric依MetricSample声明次序，`sampleId`对应SampleId，Dimensions排序。不含接收窗口/epoch；跨epoch原SampleId重放不因窗口改变而变成新样本。 |
| 健康存储校验 | HealthSample不是跨epoch生产者重试入口；StoreItem.ContentSha256覆盖四个修订字段及`health`（依HealthSample声明次序，包含其InstanceEpoch/单调起止）。内部身份为实例+epoch+SampleId；不能用它跨epoch重放。 |
| 读取请求摘要 | 顶层`action, scope, metricName, windowFromUtc, windowToUtc, exportId, byteLimit`；scope次序为`instanceId, instanceEpoch, operationId, traceId, fromUtc, toUtc, minimumSeverity, code, pageSize`，null epoch先解析当前值。不适用的附加字段写null；Subscribe用§8.2合成scope。RequestId/Cursor/Timeout及Access原token不进入此内容摘要；Access另按§8.2绑定并由Gate当前核权，摘要本身不授予权限。 |
| 已交付内容摘要 | 事件页为按Sequence排序的DiagnosticRecord规范JSON数组，指标页为按§8.1排序的MetricProjection规范JSON数组，通知为DiagnosticNotification声明次序的规范JSON；属性camelCase、null不省略、整数不降精度。空页为`[]`，不是空字节。流导出则是§8.3完整NDJSON含LF；不得拿页数组hash当流hash。 |

StoreItem的持久codec必须逐项保留§7.1全部字段及原规范输入；对象图不等于平台wire schema。健康CheckId/SourceId/SourceVersion/Unit仅接收Create登记的Probe属性，ErrorCode仅§5已声明键或null，EvidenceSha256仅摘要；不得借健康字段绕过日志脱敏写凭证/自由错误文本。健康UTC/Guid/枚举/字符串仍按§3.1检查。

### 3.2 不可变配置与预算

```csharp
public sealed record DiagnosticsOptions(
    DiagnosticInstanceId InstanceId, string ConfigRevision, string ProducerVersion,
    string RedactionRevision, string MetricRegistryRevision,
    int QueueCapacity, long QueueBytes, int MaxEventBytes, int BatchSize,
    TimeSpan FlushInterval, int CriticalReservedCount, long CriticalReservedBytes,
    double DebugSampleRatio, int MaxReceiptEntries, int MaxMetricSeries,
    int MetricWindowCount, TimeSpan MetricWindowWidth, int MaxSnapshots,
    TimeSpan SnapshotTtl, int MaxQueryPageSize, int MaxSubscribers, int SubscriberCapacity,
    TimeSpan CallbackTimeout, int MaxActiveOperations, long ReadBufferBytes,
    long MaxExportBytes, TimeSpan IoTimeout, TimeSpan HealthPollInterval,
    TimeSpan HealthSampleMaxAge, TimeSpan ShutdownDrainTimeout,
    IReadOnlyList<MetricDefinition> MetricDefinitions);
```

全部参数由Host明确传入并Create冻结，无静态默认或环境变量覆盖。所有修订非空≤128 UTF-8 bytes，运行中变更创建新epoch。下列是工程测试Profile，不是客户性能目标。

自动参数在本模块仅指离线计算容量建议：代入本节checked预算式，返回候选页大小/并发/容量及各项占用，由Host Profile Owner明确采纳后Create。没有自动运行中扩队列、改采样、换白名单、调健康阈值或延长保留的入口；负载变化只报告实测和超限。视觉自动参数/HALCON候选不适用。建议不改变生产参数，亦不替代§12测量。

| 参数 | 支持域 / 测试起点 | 约束与来源 |
|---|---|---|
| QueueCapacity / QueueBytes | 128–1,000,000条 / 1MiB–4GiB；4096 / 64MiB | 有界内存安全：队列及在途批次共同计费 |
| MaxEventBytes / BatchSize | 1KiB–1MiB / 1–4096；64KiB / 128 | 整条规范记录非仅Payload；BatchSize≤Capacity |
| CriticalReservedCount / Bytes | 1–Capacity-1 / MaxEventBytes–QueueBytes-MaxEventBytes；64 / 4MiB | 为Error/Critical预留，普通负载只能用余量；不驱逐已Accepted项 |
| DebugSampleRatio | 0–1；0.1 | 只Trace/Debug；EventId SHA256首64bit/2^64与比率比较，接纳前确定性采样 |
| MaxReceiptEntries | QueueCapacity–2,000,000；16384 | Pending/Unknown不能驱逐；表满拒绝新身份 |
| MaxMetricSeries / WindowCount / Width | 1–100000 / 1–1024 / 100ms–1h；256/60/1s | series×窗口×桶计入ReadBufferBytes；不无限标签 |
| MaxSnapshots / SnapshotTtl | 1–1024 / 1s–30min；16/30s | 固定身份和有限租约；超域拒绝 |
| MaxQueryPageSize | 1–1000；32 | 每并发读页按此上限预约，不依实际返回条数超额接入 |
| MaxSubscribers / SubscriberCapacity | 1–1024 / 16–100000；8/256 | 投影队列计入ReadBufferBytes，不占写入预留 |
| CallbackTimeout / MaxActiveOperations | 1ms–30s / 1–1024；1s/8 | 每订阅仅一个在途回调；慢任务未退出仍占槽 |
| ReadBufferBytes / MaxExportBytes | 1MiB–1GiB / 1MiB–16GiB；16MiB/32MiB | 页、桶、回执、通知、staging、操作状态先预约 |
| FlushInterval / IoTimeout | 10ms–5s / 1ms–30min；250ms/5s | 调度频率与等待截止分开，不代表终止 |
| HealthPollInterval / MaxAge | 100ms–60s / PollInterval–1h；1s/5s | 过期Unknown，不维持最后Healthy |
| ShutdownDrainTimeout | 100ms–5min；10s | 等待期限，不强杀源任务 |

Create要求MaxActiveOperations≥2，HealthProbes数量≤MaxActiveOperations-1，至少一槽为写源保留，其它读/探针不能占写保留槽；可用读并发以MaxActiveOperations预约是保守上界。Create用checked计算全部保守预约上界，预算不闭合拒绝启动，不能以OOM作为正常背压。每事件租约按MaxEventBytes及固定槽计费，批次移出Channel不归还，源写入完成且不再使用缓冲后归还；回执每槽按1KiB、快照每槽4KiB、操作每槽4KiB、通知每槽MaxEventBytes、指标每窗口每series按(256+8×桶数)bytes预留；实时表一份、每个在途指标查询一份（共1+MaxActiveOperations份），并将当前读页(每并发MaxQueryPageSize×MaxEventBytes)与每操作staging MaxEventBytes及输出64KiB缓冲计入ReadBufferBytes；若组合超预算必须改小页上限/并发或显式增预算，不能超额创建。Options测试起点应按实际组合校验后采用，非可直接照抄的完整配置。进程对象/GC实际开销另实测，预留数不等于工作集。

调用前先检查有界形状，再预约一个MaxActiveOperations处理槽才复制/序列化；同步槽不足立即Rejected，异步也不先保留完整输入副本无限等待。异步接纳等待者、身份查证、导出活跃句柄共用有限操作表，终态且无资源持有才可淘汰；同ExportId被淘汰后只能拒绝DG-STATE-001，不能自动再写流。重放判定表用MaxReceiptEntries限制，表满拒绝新ExportId。通知序号耗尽Faulted。

终态可按接收序列淘汰（导出按开始序号）；Pending/Unknown和正在访问项不可淘汰。旧身份不在内存时先查Store，历史不可可靠查证则拒绝重写DG-STORE-002。所有指标/健康/导出操作槽也有界，不能仅限制事件Channel。

### 3.3 输出和读取

```csharp
public sealed record DiagnosticReceipt(DiagnosticInstanceId InstanceId, Guid InstanceEpoch,
    EventId EventId, DiagnosticOutcome Outcome, DiagnosticPersistenceState PersistenceState,
    DiagnosticSequence? Sequence, string? ContentSha256, DateTimeOffset? AcceptedAtUtc,
    ulong Revision, string? ErrorCode);
public sealed record MetricReceipt(MetricSampleId SampleId, DiagnosticOutcome Outcome,
    DiagnosticPersistenceState PersistenceState, DiagnosticSequence? Sequence,
    ulong Revision, string? ErrorCode);
public sealed record ReceiptLookup(ReceiptLookupState State, DiagnosticReceipt? Receipt, string? ErrorCode);
public sealed record MetricReceiptLookup(ReceiptLookupState State, MetricReceipt? Receipt, string? ErrorCode);
public sealed record DiagnosticRecord(DiagnosticEventDraft Event, Guid InstanceEpoch,
    DiagnosticSequence Sequence, DateTimeOffset ReceivedAtUtc, string ContentSha256,
    string SchemaVersion, string ProducerVersion, string ConfigRevision,
    string RedactionRevision, string MetricRegistryRevision, string AdapterId);
public sealed record DiagnosticCursor(string OpaqueValue);
public sealed record DiagnosticAccessHandle(string OpaqueValue);
public sealed record DiagnosticQuery(Guid RequestId, DiagnosticInstanceId InstanceId,
    Guid? InstanceEpoch, OperationId? OperationId, TraceId? TraceId,
    DateTimeOffset FromUtc, DateTimeOffset ToUtc, DiagnosticSeverity MinimumSeverity,
    string? Code, int PageSize, DiagnosticCursor? Cursor,
    DiagnosticAccessHandle Access, TimeSpan Timeout);
public sealed record QueryPage<T>(DiagnosticOperationState State, IReadOnlyList<T> Items,
    DiagnosticCursor? NextCursor, string? SnapshotId, string? ErrorCode);
public sealed record MetricQuery(DiagnosticQuery Scope, string Name,
    DateTimeOffset WindowFromUtc, DateTimeOffset WindowToUtc);
public sealed record MetricProjection(string Name, string Unit, string DimensionsSha256,
    DateTimeOffset WindowStartUtc, DateTimeOffset WindowEndUtc, long Count,
    double Sum, double? Minimum, double? Maximum, double? LastValue,
    IReadOnlyList<long> BucketCounts, bool HasGap, string MetricRegistryRevision);
public sealed record HealthSnapshot(DiagnosticLifecycle Lifecycle, DiagnosticHealth State,
    Guid InstanceEpoch, DateTimeOffset CapturedAtUtc, IReadOnlyList<HealthSample> Samples,
    long Dropped, long Rejected, long Pending, long Persisted, long NotPersisted,
    long Unknown, int ActiveOperations, int ActiveCallbacks, string? ErrorCode);
public sealed record FlushReceipt(Guid InstanceEpoch, DiagnosticSequence HighWatermark,
    DiagnosticBatchOutcome Outcome, long Persisted, long NotPersisted,
    long Unknown, long Pending, string? ErrorCode);
public sealed record DiagnosticExportRequest(Guid ExportId, DiagnosticQuery Query,
    long ByteLimit, TimeSpan Timeout);
public sealed record ExportReceipt(Guid ExportId, DiagnosticOperationState State,
    bool Incomplete, long BytesWritten, long RecordCount, string? Sha256,
    bool ResourcesReleased, string? ErrorCode);
public sealed record DiagnosticStopReceipt(DiagnosticLifecycle Lifecycle, bool DrainTimedOut,
    int ActiveOperations, int ActiveCallbacks, long Pending, long Unknown,
    bool ResourcesReleased, string? ErrorCode);
public sealed record DiagnosticSubscriptionRequest(Guid RequestId, DiagnosticInstanceId InstanceId,
    DiagnosticAccessHandle Access, DiagnosticSeverity MinimumSeverity);
public sealed record DiagnosticNotification(NotificationRevision Revision,
    DiagnosticNotificationKind Kind, DiagnosticReceipt? Receipt,
    MetricReceipt? Metric, HealthSnapshot? Health, NotificationRevision? GapFrom,
    NotificationRevision? GapTo);
public interface IDiagnosticExportOperation {
    Guid ExportId { get; }
    Task<ExportReceipt> Completion { get; }
    ValueTask<ExportReceipt> WaitAsync(TimeSpan timeout, CancellationToken ct);
    void RequestCancel();
}
public interface IDiagnosticSubscription {
    Task Completion { get; }
    void RequestClose();
    ValueTask<bool> CloseAsync(TimeSpan timeout, CancellationToken ct);
}
```

所有三类StoreItem、HealthSnapshot和通知规范大小须≤MaxEventBytes，否则拒绝并返回相应容量错误；不能无限复制探针集合。对外不可变快照不持有内部租约，调用方保留数量属于Host内存责任。

结果集合为自有不可变快照；Receipt.Revision按持久状态变化递增，Outcome永不变。Pending为正在处理，NotPersisted为确认未写且不再自动写，Unknown为副作用不确定，Persisted仅绑定耐久回执。Unknown经原身份查询可转Persisted/NotPersisted，暂时查无不能宣称未写。未接纳结果无Sequence/AcceptedAt、PersistenceState=NotPersisted；摘要只在已通过脱敏时可有。Query时间为UTC半开区间且From<To，PageSize必须在1–MaxQueryPageSize内，Timeout为1ms–IoTimeout；RequestId/ExportId非Empty；Access/Cursor长度1–4096 UTF-8 bytes，Core不自行相信字符串。

## 4. 唯一入口与处理算法

### 4.1 构造与公开入口

```csharp
public sealed record DiagnosticsDependencies(IDiagnosticStore Store,
    IRedactionPolicy Redaction, IDiagnosticReadGate ReadGate,
    IReadOnlyList<IHealthProbe> HealthProbes, TimeProvider Time);
public sealed record DiagnosticCreateResult(IDiagnosticsRuntime? Runtime, string? ErrorCode);
public static class DiagnosticsRuntime {
    public static DiagnosticCreateResult Create(
        DiagnosticsOptions options, DiagnosticsDependencies dependencies)
        => throw new NotImplementedException(); // 仅声明规格，不是实现代码
}
public interface IDiagnosticsRuntime {
    DiagnosticInstanceId InstanceId { get; }
    Guid InstanceEpoch { get; }
    DateTimeOffset CreatedAtUtc { get; }
    Task<DiagnosticStopReceipt> Stopped { get; }
    DiagnosticReceipt Report(DiagnosticEventDraft draft, CancellationToken ct = default);
    ValueTask<DiagnosticReceipt> ReportAsync(DiagnosticEventDraft draft,
        TimeSpan enqueueTimeout, CancellationToken ct);
    MetricReceipt RecordMetric(MetricSample sample, CancellationToken ct = default);
    ValueTask<MetricReceipt> RecordMetricAsync(MetricSample sample,
        TimeSpan enqueueTimeout, CancellationToken ct);
    ValueTask<MetricReceiptLookup> GetMetricReceiptAsync(MetricSampleId sampleId,
        TimeSpan timeout, CancellationToken ct);
    ValueTask<ReceiptLookup> GetReceiptAsync(EventId eventId, TimeSpan timeout, CancellationToken ct);
    ValueTask<QueryPage<DiagnosticRecord>> QueryAsync(DiagnosticQuery query, CancellationToken ct);
    ValueTask<QueryPage<MetricProjection>> QueryMetricsAsync(MetricQuery query, CancellationToken ct);
    HealthSnapshot GetHealth();
    ValueTask<FlushReceipt> FlushAsync(DiagnosticInstanceId instanceId, TimeSpan timeout, CancellationToken ct);
    IDiagnosticExportOperation StartExport(DiagnosticExportRequest request, Stream destination,
        CancellationToken ct = default);
    IDiagnosticSubscription Subscribe(DiagnosticSubscriptionRequest request,
        Func<DiagnosticNotification,CancellationToken,ValueTask> handler, CancellationToken ct = default);
    ValueTask<DiagnosticStopReceipt> StopAsync(DiagnosticInstanceId instanceId,
        TimeSpan drainTimeout, CancellationToken ct);
}
```

工厂为public static class DiagnosticsRuntime的唯一public static Create方法，签名如上声明；先检查全部依赖、版本、预算、定义唯一性和脱敏修订，不做外部IO。成功返回已发布runtime（初始Running，发布后故障可转Faulted）；发布前失败Runtime=null及稳定ErrorCode，无部分后台任务。CreatedAtUtc为Create冻结的零offset UTC锚点T0，只读且不随系统时钟变化，供Host精确构造订阅读取意图；不是业务发生时间。一个runtime只一个InstanceId/epoch；同Store可被多runtime注入，Store须按实例隔离。所有端口由Host拥有，Core不Dispose它们，Host只能在Stopped.ResourcesReleased=true后释放。Core无无限DisposeAsync：关闭用有限StopAsync，真实终态由Stopped观察；不需要隐藏窗口、ServiceLocator或Start初始化。

### 4.2 接纳、去重、计数与Flush

Report/RecordMetric只做有限检查、复制、脱敏、摘要和队列操作，不等待磁盘/网络/回调。原子预约回执槽、条数/字节后分配序列并发布队列项，才线性化Accepted。ReportAsync/RecordMetricAsync仅等待接纳/历史查证，enqueueTimeout为0–30s；接纳锁内裁决取消/截止：尚未接纳返回Cancelled/TimedOut+NotPersisted，无后台偷偷继续接纳；已接纳返回Accepted+Pending，即使截止同时到达。取消不删除已接纳项。

首次启动epoch从未见身份可同步接纳；若同InstanceId恢复了持久历史或Store声明可能有历史，同步未知身份需要历史查证时返回Rejected+DG-STORE-002，Host分别走ReportAsync/RecordMetricAsync。同EventId/SampleId同摘要返回既有回执，不重计或累加；异摘要DG-ID-001。超过去重窗口先查Store，只有可靠NotFound且NoPendingAttempt=true允许再接纳，外部最终一致查无/不可用不允许重写。丢失写回执Pending→Unknown，保留原epoch/sequence沿原身份查证；不自动重发未知批次。

Trace/Debug采样未选或普通预算满可Dropped；其它级别不静默丢弃，满载Rejected+DG-QUEUE-001。指标不采样；关键预留不保证持久成功。使用BoundedChannelFullMode.Wait和TryWrite，禁止DropOldest/DropNewest/DropWrite驱逐Accepted项。锁协调双预约，失败全退且不留下半回执；序列只分配给成功接纳项。

一致快照计数：`receivedAttempts = duplicateAttempts + acceptedNew + dropped + rejected + cancelledBeforeAccept + timedOutBeforeAccept`；`acceptedNew = persisted + notPersisted + unknown + pending`。事件/指标/健康分别计账，GetHealth的数字仅事件；Accepted写失败不改Outcome，确认零副作用NotPersisted，不确定Unknown。逐项批回执少/多/重复身份为适配协议故障，未确认项Unknown，不能凭批次Partial把所有项标Persisted。

Flush在接纳锁捕获高水位H，等待本epoch序列≤H的事件/指标/健康；后接纳不进入屏障。全部Persisted才Complete；存在明确未写为Partial/Failed，存在Unknown优先Unknown，截止有Pending返回Unknown+DG-TIMEOUT-001，源批次继续；无待处理NoWork。计数覆盖整个屏障，不能用Channel已空证明写完。

### 4.3 指标、健康与通知

MetricDefinition构造冻结。Counter为非负增量；Gauge/Bytes/Ratio为观测值；Duration非负耗时；Histogram为观察样本，均受定义域约束。series=`Name+Kind+Unit+排序维度+RegistryRevision`；以创建时UTC锚点T0及TimeProvider单调锚点t0计算k=floor(GetElapsedTime(t0,tReceived)/MetricWindowWidth)，窗口起点=T0+k×Width；按该单调窗口落桶，保留原ObservedAt，不回写封闭窗口。摘要Count/Sum/Min/Max；Counter Sum求增量，Gauge等LastValue按Sequence；Histogram/Duration桶为互斥`(-∞,b0],(b0,b1],…,(bn,+∞)`，桶和=Count。在接纳锁内检查更新后Count/桶计数/有限Sum，溢出返回DG-METRIC-001且样本不接纳；持久失败样本仍计入实时接纳投影，持久历史只重放Persisted并标HasGap；不用0掩盖缺口，不临时估计分位。series超限拒绝不裁标签；轮转释放内存，历史由Store不可变样本按同定义重放，QueryMetrics标HasGap。SampleId重复不再累加；内存聚合成功不等于持久化。

每探针最多一个在途任务，超IoTimeout标Unknown并保留槽，真实退出前不重复调度。过期/缺样/未来UTC/重复身份异内容/来源版本单位不符/跨epoch时间域均Unknown。健康不是设备Readiness；连续历史按同Check/Source/version/epoch不可变样本重算，不接受自报连续次数。探针错误和存储故障只更新独立内存计数，不递归Report。

每订阅按NotificationRevision递增，不能要求迟到持久回执按事件Sequence递增。同事件Accepted及Persisted是两条通知，Receipt.Revision防旧投影覆盖新状态；先登记Accepted投影才登记同项PersistenceChanged，回调可以早于Report返回。每订阅仅一个回调且不在UI线程。队列满清除未投递项并合并为Gap通知，GapFrom/To绑定丢失通知修订闭区间，消费者重新Query，不冒充事件持久丢失。异常/CallbackTimeout隔离订阅并请求取消，尚在途继续占槽，不无限起新任务。

RequestClose不阻塞；CloseAsync有限等待，false表示未退出，不能归还资源。回调内部可RequestClose；检测到CloseAsync自等待立即false并计DG-SUB-001，禁止等待自己的Completion。Host自行Dispatcher调度，不能同步等待UI关闭。每次交付前ReadGate验证当前授权，撤权清队列/关闭；已交付字节不能撤回。

## 5. 稳定错误与恢复

| 错误码 | 结果与恢复 |
|---|---|
| DG-VAL-001/002/003 | 身份缺失/无效字段/超限；接纳前Rejected；修正后新身份，不截断/补默认 |
| DG-ID-001 | 同身份异内容；拒绝，不用旧成功替代新请求 |
| DG-METRIC-001 | 定义、series预算或有限算术失败；登记新配置或降低维度 |
| DG-QUEUE-001 | 未接纳资源满；有限等待/宿主背压，不扩容 |
| DG-STORE-001/002 | 确认未写/不确定；Accepted不变，沿原身份查证，不盲重发 |
| DG-SUB-001 | 慢回调/异常/Gap；隔离本订阅，重查快照 |
| DG-QUERY-001 | 范围/游标/快照失效；重新查询，不扩大范围或回退当前数据 |
| DG-EXPORT-001 | 超限/流写失败；Incomplete，不覆盖旧完整产物 |
| DG-CANCEL-001 / DG-TIMEOUT-001 | 等待取消/截止，源终态独立；不解释为已释放 |
| DG-VER-001 | 版本/单位不支持；拒绝，不改历史 |
| DG-SEC-001/002 | 当前授权/审计不满足或脱敏失败；零新数据交付 |
| DG-STATE-001 / DG-HEALTH-001 | 生命周期不允许/探针错误；读最小状态，不产生业务失败/设备结论 |

机器键与本文语义冻结，平台注册仅登记；未知错误不能显示成功。正常拒绝用回执；null参数/流不可写等编程错误ArgumentException；OOM不伪装正常背压。端口未声明异常由Core捕获并按副作用确定性分类，仅保存受控异常类型，不复制任意Message/Stack或客户载荷。

下表固定错误标题资源；不拼原Exception.Message，不暗示生产/设备结果。P1/R1 Host沿用对应机器键作诊断投影，实际storage/authorization原错误与原回执仍保留在所属Owner，不能以DG键替换根因。

| 资源键（机器码） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| DG-VAL-001 | 实例或身份无效 | 執行個體或識別無效 | Invalid instance or identity |
| DG-VAL-002 | 字段无效 | 欄位無效 | Invalid field |
| DG-VAL-003 | 数据超过上限 | 資料超過上限 | Data limit exceeded |
| DG-ID-001 | 同一身份内容不同 | 同一識別內容不同 | Identity content conflict |
| DG-METRIC-001 | 指标定义或容量不满足 | 指標定義或容量不符 | Metric definition or capacity invalid |
| DG-QUEUE-001 | 接收容量已满 | 接收容量已滿 | Intake capacity full |
| DG-STORE-001 | 已确认未写入 | 已確認未寫入 | Write did not occur |
| DG-STORE-002 | 写入结果待查证 | 寫入結果待查證 | Write result needs verification |
| DG-SUB-001 | 更新中断，请重新查询 | 更新中斷，請重新查詢 | Updates interrupted. Query again. |
| DG-QUERY-001 | 查询范围或快照失效 | 查詢範圍或快照失效 | Query scope or snapshot invalid |
| DG-EXPORT-001 | 导出未完成 | 匯出未完成 | Export incomplete |
| DG-CANCEL-001 | 等待已取消 | 等待已取消 | Wait cancelled |
| DG-TIMEOUT-001 | 等待超时 | 等待逾時 | Wait timed out |
| DG-VER-001 | 版本或单位不支持 | 版本或單位不支援 | Unsupported version or unit |
| DG-SEC-001 | 读取权限或审计不满足 | 讀取權限或稽核條件不符 | Read permission or audit unavailable |
| DG-SEC-002 | 脱敏校验失败 | 去識別化檢查失敗 | Redaction validation failed |
| DG-STATE-001 | 当前状态不允许此操作 | 目前狀態不允許此操作 | Operation unavailable in current state |
| DG-HEALTH-001 | 健康检查结果未知 | 健康檢查結果未知 | Health check result unknown |

恢复资源以`diag.recovery.<机器码>`固定映射：VAL组“修正输入后重试 / 修正輸入後重試 / Correct the input and retry”；ID“核对原身份与内容 / 核對原識別與內容 / Check the original identity and content”；METRIC“核对定义并减少维度 / 核對定義並減少維度 / Check the definition and reduce dimensions”；QUEUE“降低输入速率后重试 / 降低輸入速率後重試 / Reduce the input rate and retry”；STORE组“按原身份查证写入结果 / 依原識別查證寫入結果 / Verify the write using the original identity”；SUB/QUERY组“在原权限范围重新查询 / 在原權限範圍重新查詢 / Query again within the permitted scope”；EXPORT“等待原导出释放，再重新导出 / 等待原匯出釋放，再重新匯出 / Wait for export resources to release, then retry”；CANCEL/TIMEOUT组“检查原任务和资源状态 / 檢查原工作與資源狀態 / Check the original task and resource state”；VER“使用支持该版本的读取器 / 使用支援此版本的讀取器 / Use a reader that supports this version”；SEC-001“恢复权限和审计后重试 / 恢復權限與稽核後重試 / Restore permission and audit service, then retry”；SEC-002“核对脱敏规则，勿发送原文 / 核對去識別化規則，勿傳送原文 / Check redaction rules; do not send raw content”；STATE“检查实例退出状态 / 檢查執行個體結束狀態 / Check the instance shutdown state”；HEALTH“检查探针来源和更新时间 / 檢查探測來源與更新時間 / Check the probe source and update time”。资源可翻译扩展，机器码/副作用/重试边界不变。

## 6. 有限截止、真实排空与资源

所有IO源任务登记在MaxActiveOperations内；Store、ReadGate、Probe、Stream任务从所属操作追踪，不每条Task.Run。查询/IO/回调/停止等待由TimeProvider单调时间计量；不允许InfiniteTimeSpan，GetReceipt/GetMetricReceipt/Flush/Wait/Close为0–IoTimeout，Stop为0–ShutdownDrainTimeout。截止仅结束等待并请求取消，不释放源仍用的缓冲、流、快照或端口，尚在途继续占槽。

Query截止返回空Items+TimedOut/Unknown及错误码；迟到页只在内部清理，不能向已结束调用者交付；不启动第二个无限读取。GetReceipt/GetMetricReceipt在Draining可查本地，在Stopped只读有限终态缓存，不再访问已释放端口。Stopped回执仍可含持久Unknown；资源归还与事实已写分开。

StartExport返回句柄，同ExportId同规范请求且同Access返回原操作，异摘要或不同Access拒绝；访问原句柄只限同可信Host会话；完成重放不再写第二个Stream。操作槽不足/非法输入返回已完成Rejected句柄。目的Stream由Host拥有，直到Completion.ResourcesReleased=true才能关闭/复用；WaitAsync超时返回TimedOut/Incomplete及当前计数，源Completion继续；RequestCancel仅请求停止。逐页读取、脱敏、审计、重验授权再写；输出固定UTF-8 NDJSON，每行DiagnosticRecord规范JSON、LF，无BOM。空导出0bytes/0rows，SHA256为空字节摘要；只有完整成功提供Sha256。全部写任务退出、destination.FlushAsync完成、快照释放后Completed且ResourcesReleased=true；不代表耐久保存、原子发布或下载完成。流故障/超限已经写字节不能回滚，Incomplete=true；迟到写必须仍持有流租约，Host不得提前关闭。

Stop原子禁止接纳并捕获最终H，关闭Channel writer，拒绝新Query/Export/Subscribe；请求关闭探针/读源，排完Accepted写队列，停止投递并等回调真实退出。唯一阶段`Running/Faulted→Draining→Drained→ResourcesReleased→Stopped`；Drained要求全部源任务、回调、IO、临时缓冲实际退出。资源已归还但持久Unknown可保留，不伪造Persisted。Host此后才释放借入端口；Core留下有界终态墓碑与计数。截止DrainTimedOut=true、Lifecycle=Draining，保留原Stopped任务，重复Stop不新建排空。未知native不强杀线程，由Host进程隔离适配门接管；不阻断可合作BCL模拟切片。

## 7. 精确端口与版本

### 7.1 适配端口

```csharp
public sealed record RedactionResult(bool Allowed, DiagnosticEventDraft? Event,
    MetricSample? Metric, string? ErrorCode);
public interface IRedactionPolicy {
    string Revision { get; }
    RedactionResult RedactEvent(DiagnosticEventDraft draft);
    RedactionResult RedactMetric(MetricSample sample);
}
public sealed record StoreItem(DiagnosticInstanceId InstanceId, Guid InstanceEpoch,
    DiagnosticSequence Sequence, DiagnosticRecord? Event, MetricSample? Metric,
    HealthSample? Health, string ContentSha256, string SchemaVersion,
    string ProducerVersion, string ConfigRevision, string RedactionRevision,
    string MetricRegistryRevision, DateTimeOffset ReceivedAtUtc,
    long ReceivedTimestamp, long TimestampFrequency, DateTimeOffset? MetricWindowStartUtc);
public sealed record StoreItemReceipt(Guid InstanceEpoch, DiagnosticSequence Sequence,
    DiagnosticPersistenceState State, string? ErrorCode);
public sealed record StoreSnapshot(string SnapshotId, string StoreId,
    string StoreGeneration, string IndexVersion, Guid InstanceEpoch, DiagnosticSequence HighWatermark,
    DateTimeOffset ExpiresAtUtc);
public sealed record StoreReadRequest(StoreSnapshot Snapshot, DiagnosticQuery Query, DiagnosticStoredKind Kind,
    Guid? AfterEpoch, DiagnosticSequence? AfterSequence);
public sealed record StorePage(IReadOnlyList<StoreItem> Items, Guid? LastEpoch,
    DiagnosticSequence? LastSequence, bool HasMore);
public sealed record StoreIdentityLookup(ReceiptLookupState State, StoreItem? Item,
    StoreItemReceipt? Receipt, bool NoPendingAttempt);
public interface IDiagnosticStore {
    string AdapterId { get; }
    bool MayContainHistory { get; }
    ValueTask<IReadOnlyList<StoreItemReceipt>> AppendAsync(
        IReadOnlyList<StoreItem> items, TimeSpan timeout, CancellationToken ct);
    ValueTask<StoreIdentityLookup> FindEventAsync(DiagnosticInstanceId instanceId,
        EventId eventId, TimeSpan timeout, CancellationToken ct);
    ValueTask<StoreIdentityLookup> FindMetricAsync(DiagnosticInstanceId instanceId,
        MetricSampleId sampleId, TimeSpan timeout, CancellationToken ct);
    ValueTask<StoreSnapshot> OpenSnapshotAsync(DiagnosticQuery query,
        TimeSpan ttl, CancellationToken ct);
    ValueTask<StorePage> ReadPageAsync(StoreReadRequest request,
        TimeSpan timeout, CancellationToken ct);
    ValueTask ReleaseSnapshotAsync(StoreSnapshot snapshot, CancellationToken ct);
}
public sealed record DiagnosticReadIntent(Guid RequestId, string Action,
    string CanonicalRequestSha256, DiagnosticQuery Scope);
public sealed record DiagnosticReadPermit(string OpaqueValue);
public sealed record DiagnosticReadResult(Guid RequestId, string SnapshotId,
    string ContentSha256, long Rows, long Bytes, DiagnosticOperationState State);
public interface IDiagnosticReadGate {
    ValueTask<DiagnosticReadPermit?> BeginAsync(DiagnosticReadIntent intent, CancellationToken ct);
    ValueTask<bool> ValidateAsync(DiagnosticReadPermit permit, CancellationToken ct);
    ValueTask<bool> BindSnapshotAsync(DiagnosticReadPermit permit, StoreSnapshot snapshot, CancellationToken ct);
    ValueTask<bool> SealAsync(DiagnosticReadPermit permit, DiagnosticReadResult result, CancellationToken ct);
}
public interface IHealthProbe {
    string CheckId { get; }
    string SourceId { get; }
    string SourceVersion { get; }
    string? Unit { get; }
    ValueTask<HealthSample> SampleAsync(Guid instanceEpoch, TimeProvider time,
        TimeSpan timeout, CancellationToken ct);
}
```

StoreItem恰一个Event/Metric/Health非null，三类均含同实例身份与完整修订envelope、本epoch共享序列。健康写入同样预约但失败仅内存计数，禁止递归。Store按实例+epoch+sequence及EventId/SampleId唯一，重放返回原内容回执、异摘要不能覆盖。NotFound且NoPendingAttempt=true才可靠未写；最终一致查无/代际不明/超时为Unknown。后端耐久语义、刷盘、恢复对账需真实适配声明；内存模拟Persisted仅相对模拟进程，不是磁盘证据。

ReadGate是Host可信授权/审计组合端口：Begin验证当前主体并耐久预留、BindSnapshot耐久绑定来源、Seal耐久完成结果、Validate当前撤权检查；任一null/false/异常零新数据交付。Handle/Permit为不透明token，字符串本身不授权；Gate验证主体/会话/动作/范围/规范摘要。Action仅QueryEvents/QueryMetrics/Export/Subscribe；摘要绑定所有筛选/页大小/实例范围，另含指标Name/窗口或ExportId/字节限额；排除Cursor/Timeout/RequestId。模拟Gate仅固定测试token，禁止部署生产。

TimeProvider替代草案IClock，Options及内部租约替代IResourceBudget，Store统一存储/遥测；历史用不可变Store快照。删除未闭合的IDiagnosticSink/IHealthHistoryResolver/IProtectionResolver候选Core端口；保护引用/签名包/下载/通用清理由§8.3 Host/存储Owner承接，Core没有Purge或设备Readiness。

健康Probe属性在Create冻结且CheckId唯一，Probe数量≤MaxActiveOperations-1；Sample必须匹配所给epoch及四项属性。事件/指标/健康身份及导出重放墓碑共用MaxReceiptEntries总槽上限，健康内部SampleId去重也占此总槽，满载不接纳新健康样本并标Unknown。读取/导出只读取Persisted记录；快照未覆盖的Accepted/Pending不能混进历史页。StoreItem中的ReceivedTimestamp只在对应epoch/frequency内可比，MetricWindowStartUtc由Core写入；历史按存储窗口及RegistryRevision重放；过去窗口只能按对应不可变定义，Core不持有该修订时DG-VER-001，不按ObservedAt重分桶。Query.InstanceEpoch=null解析为当前epoch并进入规范摘要；历史必须显式指定单个epoch，一次快照不跨epoch。StoreReadRequest.Kind为明确三选一，返回项仅该类；Event按§8.1事件筛选、Metric按Scope接收UTC及Operation筛选（Trace/Code为空），Health按接收UTC筛选。每种都先筛选再分页。StorePage按Sequence严格递增，仅同snapshot epoch，返回超过PageSize、重复/倒序/异epoch或H以上项一律拒绝。Event/Metric/Health三个分账总和用于FlushReceipt，GetHealth仅事件分账。GetReceipt/GetMetricReceipt是可信生产者的原写入元数据查询，不提供日志内容读取授权；不向非可信远端/UI直接暴露此入口。

### 7.2 版本与发布

当前SchemaVersion=`diagnostics/0.2`，DTO与NDJSON按本文；v0.1未发布，不伪造迁移通过。Major改变字段/单位/有效域/结果/排序，须新格式及只读迁移；Minor可加不改变旧读取的可选字段；Patch不改语义。事件/指标/健康均绑定Producer/Config/Redaction/MetricRegistry/Adapter版本，旧记录不重写。平台C-01～C-08仅接入映射。

Core与公开Contracts先在唯一Core工程实现，后续包名Asun.Diagnostics.Contracts/Asun.Diagnostics.Core不是第二namespace。升级先双读适配→回放/迁移验证→旧接纳关闭真实排空→新epoch写入→观察未知/丢弃/资源→保留回退；回退不删新记录、不改单位、不复用旧序列。

### 7.3 A1：本模块的构造、注入和异常退出

A1的本模块装配入口就是§4.1的`DiagnosticsRuntime.Create(DiagnosticsOptions, DiagnosticsDependencies)`，不增加另一套Runtime/Builder/全局容器。真实Store/ReadGate/Redaction/Probe实现由对应已批准适配提供，其具体后端构造不属于Core；**本模块自己的装配不得留待Host猜测**，固定如下：

| 步骤 | 模块内确定动作与注入方向 | 失败与Owner |
|---|---|---|
| 1 输入冻结 | 同步检查Options/依赖非null、修订、Store.AdapterId/MayContainHistory、Probe属性；复制Options/MetricDefinitions/Probe列表，保留端口对象引用 | 无外部IO；失败返回Runtime=null及§5错误，借入端口原样归Host，不Dispose |
| 2 纯值构造 | 构造值验证/规范化/摘要组件（注入冻结配置与Redaction）；构造条数/字节预算、身份回执表及指标窗口表；捕获TimeProvider的UTC/单调锚点、生成epoch/游标密钥 | checked与预算先验；未发布部分仅释放模块自有内存/密钥，不启动源任务 |
| 3 运行组件 | 构造有界Channel、批写泵（Store+Time）、快照读取器（Store+ReadGate+Redaction+预算+游标密钥）、订阅调度（ReadGate+Time+回调预算）、健康调度（Probe+Time）、停止协调器（所有组件和同一租约表） | 这些都是唯一Core工程内的私有实现，不成为新公共端口；禁止组件反向读取Host私表/静态服务 |
| 4 原子发布 | 所有纯构造完成后，一次提交Running runtime和Stopped任务；内部启动门在提交前关闭，不允许Append/Probe/Gate/回调提前执行。提交后才启用批写/健康/过期计时和受控工作泵 | 提交前构造失败完整回滚且返回null；提交后的计时/调度失败属于已返回实例Faulted，启动有限Stop并保留Stopped，不能再返回null冒充无源任务 |
| 5 调用路径 | Report→验证/预约/去重→Channel→批写泵→逐项Store回执→同一回执表→通知；Query→快照读取器→Gate/Store→授权投影；StartExport→同一读取器→借入Stream；Probe→健康接纳→同一Store | 不另建错误日志sink；接口异常由对应步骤转换受控错误，持久不确定保持Unknown |
| 6 退出 | Stop关闭接纳、各读/探针取消请求、最终H批写、关闭订阅，实际泵/计时回调/端口源结束，清快照/缓冲/密钥并完成Stopped | 先释放模块自有租约；Stopped.ResourcesReleased后Host才释放Store/Gate/Probe/Time；超时继续持有，不能在finally无条件Dispose |

Host的确定装配顺序为：按外部适配合同取得Store/ReadGate/Redaction/Probe及其Owner释放句柄→构造`DiagnosticsDependencies(store, redaction, readGate, probes, time)`→调用唯一Create→保存返回runtime→交给生产者或§8.5 Binding。Redaction/Time/Probe可能借用同一服务，Host按引用身份只释放一次；同Store共享多实例时，最后一个runtime实际Stopped后才释放共享Owner。Core永远不调用借入对象的Dispose/IAsyncDisposable，也不替Host关闭连接。

异常退出分三支，不能共用无条件using：①Create前适配取得一半失败，按适配自身有限退出合同逆序归还已取得Owner；②Create返回null，Core保证无源任务，Host可逆序归还；③已取得runtime后业务启动/窗体挂接/后台执行失败，保留原异常的受控类型，先取消本Host生产者并解除本Host U1，再有限Stop；结果未释放则把runtime/Owner保留在Host的有界在途表，拒绝再次建相同实例，不关闭借入端口，沿原Stopped继续观察。真正Stopped后逆序释放。Host进程退出/适配源不合作只记排空未知，不伪造释放；不把这条恢复链留给产品页面猜测。

本模块装配代码仍在唯一Core工程，配套DG-A01～03在唯一Core测试工程使用已定义BCL夹具验证；真实后端的连接/事务/审计耐久实现不是被此装配规格自动批准。外部门只影响这些真实适配事实。

### 7.4 A1：真实Store与读取门的宿主接线

本节冻结diagnostics Owner可决定的映射和恢复，不增加Core API、通用数据库DLL或新的认证系统。采用[IM-066 storage-database §6.3/6.7/7.1](../storage-database/DEVELOPMENT-GUIDE.md)的已声明注册事务/窄读/对象引用/真实排空能力；可信身份、授权和审计复用[authorization §8.1～8.4](../authorization/DEVELOPMENT-GUIDE.md)的来源绑定、提交/撤权临界区和持久意图规则。上游数据库技术表、账号/角色/签名私钥不归diagnostics。以下Owner逻辑记录/注册标识是本模块的实施规格，尚不是平台合同获批或实际建表结果。

组合根输入必须包含：唯一的InstanceId→可信租户/StorageScope/StoreRef路由，冻结的OwnerKey=`diagnostics`、Bindings/References/codec修订，StoreId/恢复代际及IndexVersion，已认证会话来源、四个读取Action的对象级范围规则，独立读取审计持久路径，Probe/白名单和有限Host预算。全部按原身份/Ordinal查找；重复/缺失/来源未知初始化失败，不能从InstanceId、UI文本或ResourceRef拼数据库名/路径。Host预算至少显式给出最大路由、在途适配源、快照、持久恢复意图条数/实际编码字节及退出期限；先预留§9 Owner槽再取得资源。授权审计存储故障不调用本模块Report作为补偿。

| Owner逻辑记录 | 最小字段、唯一性和写入权威 |
|---|---|
| 诊断不可变项 | 完整StoreItem及规范输入字节；主键为可信scope+InstanceId+epoch+Sequence，独立唯一键为scope+InstanceId+kind+EventId/MetricSampleId（Health另含epoch+SampleId）。Schema/Producer/Config/Redaction/Registry/Adapter、接收单调频率/指标窗口全部保留；一次接纳只有一个kind。不得按UTC、OperationId或hash单独去重。 |
| 身份账本 | 同唯一身份、原ContentSha256、原epoch/Sequence、持久状态/回执及`PayloadRetired`；与项写入同事务。删除载荷不能删除未知写入/重复防护语义；账本自身保留策略须明确，不能为腾空间伪造可靠NotFound。 |
| 提交时钟 | 每scope+InstanceId+epoch的单调UInt64 commitRevision；每次成功追加在同事务锁定/推进并赋给新项，重放不推进。溢出拒新写。不是Core Sequence，也不是UTC或数据库自增分配值。 |
| 快照租约 | 不透明SnapshotId、scope/InstanceId/epoch、冻结提交代G和H、Store恢复代/IndexVersion、到期、原筛选hash及保护状态。开快照在同一致事务读取G/H并登记保护；页只能读commitRevision≤G且Sequence≤H的已提交成员。晚提交的低Sequence不得混入。 |
| 读取审计意图 | 原RequestId、可信主体/会话引用、Action/规范请求hash、来源快照绑定、结果hash/条数/字节/状态、审计修订与持久回执；状态`Reserved→SourceBound→Sealed`，Subscribe明确跳过SourceBound。同阶段同内容重放，异内容冲突；不写Access原token、凭证或原日志正文。 |

注册项在可信配置启动前装成不可变`StorageBindingCatalog`/`StorageReferenceCatalog`：写事务`diag.append.v1`、`diag.snapshot.open.v1`、`diag.snapshot.release.v1`、`diag.retire.v1`、`diag.package.publish.v1`、`diag.read.audit.v1`；窄读`diag.identity.event.v1`、`diag.identity.metric.v1`、`diag.snapshot.page.v1`、`diag.package.find.v1`、`diag.read.audit.find.v1`。这里是VersionRef的Id，Revision=1；其schema/codec/StatementCatalog逐项由本Owner实现并与本节输入/结果绑定，不能作为动态SQL或delegate。VersionRef.Hash必须来自可信发布中对应规范内容的实际SHA-256；完整Id/Revision/Hash匹配才注册，不能只凭这里的Id或零hash启动。生产StatementCatalog/物理DDL由该适配接入发布绑定；诊断/Core/UI不读storage技术私表。诊断源、包和快照保护通过OwnerReferenceResolver登记，Owner事实与对象引用写/释放在同storage事务且推进reference epoch；未知resolver不能当空集。

执行链固定如下：

1. **Append。** 检查整批有界大小和每项双身份/规范输入；以稳定原批次身份调用注册事务，逐身份insert-if-absent并比较完整规范输入，同内容返回原回执，冲突零覆盖。整个批次采用一次事务全提交或全未提交；Core仍保留其逐项协议以支持其它合法Store。只有storage终态确认原事务持久才Persisted；确认未提交才NotPersisted；提交响应丢失/恢复中/端口故障为Unknown。保存原storage operation/task映射，在真实源退出前不重新占槽或发第二批；之后QueryOperation及原身份查证。重启不重放未知批次为新批次。
2. **Find。** 按可信路由及完整身份读取一致的账本和载荷，核原摘要/回执。仅当前恢复代已核完整、该身份没有原未决事务且账本没有retired记录时才NotFound+NoPendingAttempt=true。PayloadRetired且无法提供原StoreItem时返回Unknown+NoPendingAttempt=false，DG-STORE-002；既有证明不得因载荷删除变成“从未写入”。恢复代不明同样Unknown。生产Adapter.MayContainHistory恒true，不能因本进程缓存空而改false。
3. **Snapshot/Page。** Open用原筛选登记一致G/H，StoreGeneration编码恢复代及G，IndexVersion冻结。记录不可变、commitRevision≤G限定成员；持有该epoch保护期间不得retire相应项。按§7.1 kind筛选和Sequence分页，读取当前generation/租约，失效明确失败，不重开同名快照。末页/过期/取消请求Release，等真实数据库/对象读取退出再归还保护；恢复后旧SnapshotId全部失效，不能拼接恢复前后的页。单epoch保守保护允许整epoch暂缓清理，不能用更细的未经证明锁优化删除。
4. **Gate。** Begin从已认证来源核当前主体、用途、范围/字段/限额，以原RequestId耐久预留审计后才发opaque permit；Bind核实际snapshot并耐久CAS绑定；Seal核来源及实际结果并耐久CAS完成；Validate在每次交付边界核当前会话/政策/资源代。使用Host当前权威提交/撤权临界区序列化最终校验与本次投影交付预约；撤权先线性化则零新数据，交付先线性化则只保留已经预约的有界本次页/流块，后续禁止。不得把authorization的Read/NotRequired当作本模块已耐久读取审计，Gate另持自己的受控读审计意图。
5. **恢复/退出。** 审计Unknown按原RequestId查同阶段完整记录，不新建RequestId补成功；恢复身份重新核权，Conflict/缺来源/撤权保持NeedsAttention，不披露旧成功。快照/包发布/retire也沿原storage identity与不可变意图回查，Query本身不继续写/删除。Host先禁新源、解除本Host控件、Stop Core并等待原源/审计/对象lease真释放，再释放StorageSession/共享根；任一未知按§9原槽移交。Core Stopped不代表Host自身IO排空。

真实路由/凭证/存储介质耐久声明、审计策略、具体StatementCatalog及迁移部署包由适配/消费者Owner提供并实施验证；本节的软件映射不把这些外部事实伪装已绑定。A1保持IntegrationPending，不反向修改已接收Core。

## 8. 查询、导出和可选 UI 契约

### 8.1 查询与指标范围

事件查询使用InstanceId、单epoch、OperationId/TraceId、OccurredAtUtc半开时间范围、MinimumSeverity、Code与分页上限；AND组合，筛选先于分页，排序固定Sequence升序，不按UTC猜因果。只有Persisted事件进入结果。空匹配为Completed空页，不是错误。查询不写事实、不创建业务关联；关联父事件缺失/迟到/循环显示缺口，不补成功链。

MetricQuery.Scope中的FromUtc/ToUtc作用于StoreItem.ReceivedAtUtc，WindowFromUtc/WindowToUtc筛选窗口起点，均为UTC半开区间；Name必须登记，Scope.TraceId/Code必须null、MinimumSeverity必须Trace，禁止默默忽略事件条件。Scope.OperationId可筛原样本，但返回的是该筛选集的重算摘要，不能冒充完整series。每页按WindowStartUtc、Name、DimensionsSha256的Ordinal次序排列；同epoch/registry/series/window聚合，不跨来源版本拼接。指标游标由Core从Store快照扫描并建立有限聚合表后分页，预约MaxMetricSeries×MetricWindowCount，按每在途查询独立预约，超限明确拒绝；不能把每个Store原始页分别聚合再称完整窗口。当前epoch遗漏Pending/Unknown/NotPersisted时HasGap=true；历史适配无法证明完整时也true。窗口不足、不支持定义版本或溢出返回明确错误，不补0。

GetHealth为当前epoch最小诊断投影；连续历史只由Host经Store快照按Check/Source/version/epoch重算。Core不提供设备Readiness或连续健康合格判定接口。本模块不是通用SQL Store，外部查询模块只能读取授权投影，不能取得写权。

### 8.2 可信读取门、不可变快照与游标

OperationalLog、SecurityAudit、ProductEvidence分属不同Owner。本模块只拥有第一类及自身指标/健康投影；正式审计由ReadGate的Host实现耐久保存，不写回故障诊断队列。Access来自认证后的可信Host，绑定主体/会话、动作/用途、实例/epoch/范围、允许字段、条数/字节上限、TTL和适用审批；用户名、角色文本、UI按钮或IsAuthorized不授予权限。Core不实现账号、MFA或租户策略。

每页顺序固定：有界校验→规范请求摘要→ReadGate.BeginAsync耐久预留→OpenSnapshot/续页绑定→BindSnapshotAsync耐久绑定→ReadPage并验证来源/范围/排序→在Core脱敏白名单内校验→SealAsync耐久记录实际行数/字节/内容hash/结果→ValidateAsync确认当前权限→交付。null/false/异常/截止均零新数据交付。失败页Items为空，ErrorCode保留；审计未知沿原RequestId由Gate恢复，不新建副作用。续页每次使用新RequestId，原请求摘要与snapshot/permit必须仍一致。

Core持有随机32bytes epoch密钥，以BCL HMACSHA256保护游标，固定时比较MAC；密钥不出模块，停止后清理。游标是UTF-8规范JSON载荷的base64url加MAC（无padding），载荷绑定格式版本、规范范围hash、Access SHA256、snapshot/store/generation/index/epoch/H、完整最后排序键、PageSize、到期时间；MaxSnapshots表保存当前permit及来源租约。不支持跨runtime重放。句柄Hash只作绑定，仍每次Gate验证，不能代替授权。未知字段、重复字段、超长、篡改、跨Access/范围/页大小/epoch、失效snapshot均DG-QUERY-001；不回退当前数据。StoreSnapshot高水位仅属于所指定epoch，Store必须保证读到同代际不可变数据；Core不会凭一个最大序列猜快照。指标聚合不保存在snapshot表，续页在同快照重新有限扫描/聚合，以相同排序键跳过已交付项，避免每个闲置snapshot暗持整张表。

快照TTL用单调租约（Store UTC到期仅额外上限）；末页、取消、过期和关闭均请求ReleaseSnapshotAsync，实际源退出前保留槽。分页结果的SnapshotId不是授权。QueryMetrics先扫描整份同快照原始指标并有限聚合，再形成指标排序键；禁止超预算临时数组。Gate.Seal的hash针对实际将交付的规范内容，空页也审计。模拟Gate的固定token只用于S1；真实门在A1关闭。

订阅RequestId非Empty，Create时UTC锚点作为FromUtc，ToUtc固定DateTimeOffset.MaxValue（零offset），当前epoch、无Operation/Trace/Code、PageSize=1、Cursor=null、Timeout=IoTimeout，MinimumSeverity来自请求，构成Subscribe专用合成Scope；绑定的Access须允许此持续范围。每通知交付前使用该Scope+通知Revision生成独立RequestId执行Begin→Seal（SnapshotId为epoch/revision标识）→Validate，不打开Store，也不调用BindSnapshot；Gate对Subscribe须支持该明示分支。事件级别过滤只影响EventAccepted/PersistenceChanged，Metric/Health/Gap不过滤。通知不带原日志内容；授权或审计失败关闭本订阅，不扩大范围。审计端口缓慢同样占操作槽。

### 8.3 流导出与支持包/下载/保留集成

Core只按§6的StartExport向借入Stream输出已授权事件NDJSON，Query.Cursor必须null。规范写法由Utf8JsonWriter逐字段生成，不直接默认Serialize record：顶层顺序为schemaVersion、producerVersion、configRevision、redactionRevision、metricRegistryRevision、adapterId、instanceId、instanceEpoch、sequence、receivedAtUtc、contentSha256、event；event顺序对应DiagnosticEventDraft声明，Guid小写D，枚举用精确名称，sequence为JSON整数，UTC round-trip，字典Ordinal排序，可空字段写null。Payload为空写null，非空按Ordinal键排序逐字段写入校验后的JSON object（number invariant round-trip，负零为0），禁止ReadOnlyMemory默认base64编码；数字round-trip且负零为0。换行LF计入bytes/hash。固定快照及版本的相同输入产生同字节；不能声称不同epoch也相同。

ByteLimit为1–MaxExportBytes。写每行前验证累计长度，超限不写半行；Stream自身部分写失败仍可形成半行，Incomplete=true。每页在写前完成审计/当前授权及脱敏验证，Stream.WriteAsync之后不能撤回已交付字节。Source snapshot和输出租约直到真实源终止才归还。Timeout从StartExport计，WaitAsync仅改变本次等待；成功hash覆盖实际全部字节。请求/结果/终态缓存有界，非法句柄输出不得掩盖原在途源。

支持包、签名发布、下载及保留属于完整诊断消费链的宿主集成P1/R1，软件步骤见以下子节；不新增Core包/下载/Purge入口，不制造通用发布/下载服务DLL。Host持有产品任务/网络会话，diagnostics持有自身记录及Owner映射，storage-database持有技术存储/保护协调/物理GC，安全Owner持有密钥和信任/保留策略。P1/R1只具指导规格，不授新增代码切片准入。

#### 8.3.1 完整事件与NDJSON规范向量

输入为§3.1.1 Event规范对象：下行无换行、UTF-8共640bytes，SHA-256=`a539cac7caff31b1845b4fd6ecf84b16bc15bdea27d8fa31db57e6cf1a258fb5`。Payload n的原输入可为-0，规范后为0；Attributes原输入逆序也得到同一行。下例不包含非ASCII转义，避免把Python通用encoder当成.NET固定encoder。

```json
{"schemaVersion":"diagnostics/0.2","configRevision":"cfg-1","redactionRevision":"red-1","metricRegistryRevision":"met-1","event":{"instanceId":"11111111-1111-1111-1111-111111111111","eventId":"22222222-2222-2222-2222-222222222222","operationId":"33333333-3333-3333-3333-333333333333","parentOperationId":null,"correlationId":null,"traceId":"0123456789abcdef0123456789abcdef","spanId":"0123456789abcdef","occurredAtUtc":"2026-10-11T00:00:00.0000000+00:00","severity":"Information","eventKind":"Completed","code":"DG.DONE","messageKey":"diag.done","attributes":{"a":"1","z":"2"},"payload":{"n":0,"ok":true,"text":"ready"},"resourceRef":null}}
```

同一输入用producer-1/store-1、epoch=44444444-4444-4444-4444-444444444444、Sequence=1、ReceivedAtUtc=2026-10-11T00:00:01+00:00形成下行。**行末一个LF**后共949bytes，SHA-256=`16c541aa14a85c6b0f2abcdac2c623c0d038353fc8d989384a322bae295c2741`。ByteLimit=949可完整写这一行，948在写前拒绝且此行0bytes；Stream真实部分写失败仍按Incomplete处理。

```json
{"schemaVersion":"diagnostics/0.2","producerVersion":"producer-1","configRevision":"cfg-1","redactionRevision":"red-1","metricRegistryRevision":"met-1","adapterId":"store-1","instanceId":"11111111-1111-1111-1111-111111111111","instanceEpoch":"44444444-4444-4444-4444-444444444444","sequence":1,"receivedAtUtc":"2026-10-11T00:00:01.0000000+00:00","contentSha256":"a539cac7caff31b1845b4fd6ecf84b16bc15bdea27d8fa31db57e6cf1a258fb5","event":{"instanceId":"11111111-1111-1111-1111-111111111111","eventId":"22222222-2222-2222-2222-222222222222","operationId":"33333333-3333-3333-3333-333333333333","parentOperationId":null,"correlationId":null,"traceId":"0123456789abcdef0123456789abcdef","spanId":"0123456789abcdef","occurredAtUtc":"2026-10-11T00:00:00.0000000+00:00","severity":"Information","eventKind":"Completed","code":"DG.DONE","messageKey":"diag.done","attributes":{"a":"1","z":"2"},"payload":{"n":0,"ok":true,"text":"ready"},"resourceRef":null}}
```

实现验收须从该draft生成两种实际.NET字节而非只hash复制的字符串；另覆盖非ASCII/引号/反斜线/控制字符、无效代理项、数字词法、null/空Payload、未知/重复字段、UInt64完整精度。此向量本轮只完成字节复算，不称已运行C# Golden。

#### 8.3.2 P1：支持包构建、签名与原子发布

这是两个消费者可复用的**宿主内部协议**，不是新的公开Core DTO/SDK。Host组合根显式注入已批准的源Owner读取能力、IStorageDatabase、当前授权/审计门和安全Owner签名能力；没有按URI下载任意源、动态发现resolver或自动回退无签名包。Source Owner返回精确身份/版本、长度/hash、媒体类型、来源权限及有界读取lease，Host重验当前版本并借读；不解析凭证URI。ExportReceipt本身没有SnapshotId/StoreGeneration；日志产物的来源信息须由本Host自有Gate的原Export规范请求hash（含ExportId）及各页RequestId对应的耐久SourceBound记录取得，并核全部页属于同一原快照，不能从另一Query补填，也不要求Core新增来源字段。未取得匹配审计来源则不构建包。日志来源使用Core StartExport完成的NDJSON，只有Completed且真实ResourcesReleased后才取得该产物描述。其它附件只接受已登记的脱敏诊断文本/摘要，不把SecurityAudit、原始图像、私表、SDK dump或产品证据复制进包。

Host Profile显式给出MaxArtifacts（1～256）、MaxManifestBytes（1KiB～1MiB）、MaxPackageBytes（1MiB～16GiB）、MaxActivePackages/MaxPendingPackageEntries（正Int32）、MaxPendingPackageBytes（正Int64）、有限构建/下载/收尾期限；一次源读取/写入缓冲固定≤64KiB，manifest有界完整编码后才写，不整包拷内存。总包长及预约checked；无槽/超限在借源前拒绝。每artifact稳定身份/版本字符串≤128 UTF-8 bytes、媒体类型≤128 ASCII，长度非负Int64、hash为64小写hex，附件经同Host冻结白名单。这些是软件支持域，不是生产默认或客户负载目标。

格式固定`diagnostics-support/1`：包头ASCII `ASUN-DIAG-PKG1`加LF；随后8bytes little-endian UInt64 manifest长度、manifest规范JSON字节；再按manifest entries顺序逐项写8bytes little-endian UInt64内容长度和内容；最后固定64bytes签名，无尾随数据/压缩/本地时间/随机目录名。manifest顶层次序为`schemaVersion, packageId, operationId, requestSha256, instanceId, instanceEpoch, sourceSnapshotId, sourceStoreGeneration, redactionRevision, createdAtUtc, signingAlgorithm, signingKeyId, signingKeyEpoch, entries`；entries按稳定artifactId的Ordinal排序且不重复，每项次序`artifactId, version, mediaType, bytes, sha256`。createdAtUtc/PackageId在首次受控接纳时冻结；sourceSnapshotId/storeGeneration来自原来源回执，不能从后来Query补填。纯NDJSON产物固定artifactId=`events.ndjson`、version=`diagnostics/0.2`、mediaType=`application/x-ndjson`；附件依上述resolver登记。JSON沿§3.1.1，manifest不含包hash/签名本身，避免自引用。

签名基线为ECDSA P-256、SHA-256、IEEE P1363固定64bytes，algorithm字符串=`ECDSA-P256-SHA256-P1363`。签名覆盖上述包头、所有长度字段、manifest及所有内容的SHA-256，最后签名字节不进入待签hash；完整包另算SHA-256并存ObjectRef/发布回执。使用BCL ECDsa.SignHash/VerifyHash显式DSASignatureFormat.IeeeP1363FixedFieldConcatenation，实际私钥可能由安全适配器持有；Core/VM不取得私钥。KeyId/KeyEpoch来自安全Owner当前受信配置，验证只用可信注册公钥，不信包自带公钥/URL。包内日期不授权过期/撤销密钥；不支持算法或无可信key明确失败。ECDSA签名可不同，**不承诺同内容重新签名的整包hash相同**；同幂等请求必须重放已封口的原包，不能重签覆盖。

执行及恢复顺序：

1. 当前核构建权→在`diag.package.publish.v1`对应的Owner operation记录预留稳定幂等键/完整请求摘要/PackageId/原源描述/KeyEpoch。键是可信scope+主体会话命名空间+Host IdempotencyKey；相同键/摘要返回原operation，异内容冲突。摘要含原Core查询规范范围、脱敏修订、所有源身份/版本/长度/hash和签名配置，不含Access秘密。历史回执查询仍核当前权限。
2. 取得/保留每个原源lease，逐项重验长度/hash/媒体类型/当前权限，流式生成固定格式及待签hash。任一变化/撤权/不足/多出字节即Failed/Incomplete，不发布；源未退出保留原Owner槽，不能Close后重读另一来源补成成功。源内容先冻结到受保护staging；完整artifact描述确认后才生成manifest，不能先写占位再覆盖长度/hash。
3. 生成签名，再从最终staging完整读回，重验manifest/各项字节、签名及全包hash；验证成功才调用storage FileObjects.StageAndSealFileAsync注册格式`diagnostics-support/1`。保留源Stream直到原storage task真实释放；仅SealedDurable及完整ObjectRef可用于发布。中途失败只留下未发布/孤立对象供storage受保护恢复，不可下载。
4. 用原identity的注册发布事务CAS写`Published`及精确ObjectRef、全部源引用/签名信息/验证证据，与Owner对象引用/reference epoch同事务提交。耐久发布后才能返回完整包。提交结果Unknown沿原storage QueryOperation及`diag.package.find.v1`回查，未确认不展示可下载；不重新建PackageId或重写文件。签名成功/SealedDurable单独均不等于Published。
5. Host重启只加载未决原operation/源身份/封口回执，重新核恢复权并原身份回查；可以确认原发布或进入NeedsAttention，**只读回查不自动继续构建/发布**。明确受控恢复命令才可在原identity下续未执行步骤，若源/key版本变更保留失败，新的内容需新幂等键。所有生产签名/介质耐久/撤权并发验证仍是外门。

#### 8.3.3 P1：下载续传与一次性许可

下载是Host transport职责，UI仍只消费§8.5导出回执，不增加下载按钮/网络Core端口。仅Published且验证ObjectRef完整的包可打开；每次当前授权精确绑定scope、主体/会话、PackageId/版本/hash/长度、半开range、TTL和用途。使用storage FileObjects.OpenReadAsync取得对象lease，不按文件名或包hash去其它租户找源；借读到源真实退出后才Release。

Host持久下载记录键为可信scope+DownloadId，保存完整包引用、当前主体会话、expiresUtc、confirmedOffset、最多一个pendingRange、审计意图及状态；所有bytes/offset为checked Int64。首次confirmedOffset=0；只接受`[confirmedOffset, end)`且0≤offset<end≤包长/本次限额。一个未确认range只能原样重传，不能跳跃/重叠确认、同时开第二range或换主体/包。授权撤销/过期禁止新交付，已经交付字节不能撤回。确认由当前认证会话提交原pendingRange身份及接收hash，Host核服务器实际发送的该range hash并耐久CAS推进confirmedOffset；发送返回不自动确认，确认响应丢失读原DownloadId。重传不重复推进。

confirmedOffset到包长后，核原SealedDurable/Published回执及客户端明确的全包hash确认，在当前核权临界区耐久CAS为`DeliveryAcknowledged`并消费一次性许可；失败/Unknown保持原许可保留态，沿原DownloadId查，不因超时换许可。该状态只证明协议确认，**不声称接收端落盘耐久或人工已使用**。空包不属于此格式（至少有header/manifest/签名）；有效包的空events附件允许。超时只结束本次等待；Host源流/租约/下载记录仍由原Owner收尾。外部transport公开签名及实际协议绑定由产品接入任务核对，本文不猜供应商接口。

#### 8.3.4 R1：诊断保留、保护引用与清理

保留Policy由客户/安全/运维Owner显式给出并版本化：各kind/级别的保留期限、法律/调查保持来源、最低去重账本期限、包保留期限、隔离期、最大计划项/字节及维护权限。缺Policy、身份账本恢复不完整、时钟基准未知时零删除，不给“7天”等客户默认。诊断内容清理不操作SecurityAudit/ProductEvidence/alarms事实；日志故障恢复不调用清空目录。

软件流程唯一为`Plan→Preview→Authorize→Retire/Quarantine→Revalidate→PhysicalGc→Receipt`。Plan在一致恢复代/ReferenceEpoch冻结候选原身份、版本/hash、范围、策略修订及理由；年龄只是候选条件，不授权删除。Preview只读并显示受保护/未知/可处理项，批准只绑定该计划，不能顺带清理后来发现的项。未达到容量上限前分页处理；超限明确缩小计划，不建无限对象数组。

| 步骤/Owner | 可执行检查及失败结果 |
|---|---|
| retire诊断载荷；diagnostics Owner注册事务 | 当前维护权+原计划/Policy/恢复代/版本一致；同epoch活跃快照/在途读取、Pending/Unknown写、调查/法律保持、未完成导出/构建/下载及其它登记引用全部重验。任一不明该对象Skipped/Unknown、零删除。与保护增加/引用释放处于同一协调临界区；成功只标PayloadRetired/移除可清理载荷与自身业务引用，保留原身份账本及持久回执，不假造NotFound。 |
| 隔离文件；storage-database | 仅Owner已经明确释放全部引用的包/staging候选，按上游不可变GC计划及物理身份/fence进入隔离；同内容多引用/别名也须完整闭合。不由diagnostics调用File.Delete或自选目录。 |
| 物理GC；storage-database | 隔离期后再次核当前法律/调查/引用/lease/backup/Policy及physical identity，使用其PlanOrphanCollectionAsync→CollectEligibleOrphansAsync原plan；新增保护先提交则跳过，删除先线性化则保护新增须明确失败/重新解析，不允许两边都成功。resolver未知、generation变化或备份闭包未知均保留。 |
| 回执/恢复；Host与原Owner | 每项保留计划身份、步骤、Confirmed/NoEffect/Unknown、原storage operation及证据；聚合Partial不能称全成功。响应丢失先回查原identity/journal，Unknown不自动重删/换计划。只读查询不触发清理；恢复需新的当前维护授权及原计划CAS。 |

保护引用由diagnostics的IStorageOwnerReferenceResolver读取自身同事务引用epoch，storage协调器合并其它Owner、hold/backup/法律来源；自报pin/文件年龄不是保护权威。原源在途还占Owner槽，TTL到期仅禁止新读，不提前释放仍使用的Stream/对象。账本后续获批回收后，Store仍须声明该历史覆盖段不能可靠证明未写，对该段未知身份保持NoPendingAttempt=false；不能把保留策略降低成重新接纳同ID的漏洞。清理后任何旧游标失效都DG-QUERY-001，不返回缺页冒充完整历史。

### 8.4 可选工作台 PageContract（U1）

角色与任务：维护工程师定位一条操作的阶段/存储问题；开发人员比较指标趋势；运维人员按Host范围只读；导出须独立权限。流程为选择实例/epoch/UTC范围→筛选→选事件→查看关联链和脱敏详情→联动指标→按权限导出→查看真实完成/不完整和恢复动作。页面不改日志等级、确认报警、放行质量或操作设备。

在固定1920×1080验证viewport内扣除任务栏、窗口边框/标题栏及Host状态栏后记录实际client；不改显示设置。顶部约8%为实例/时间/级别/Code筛选及查询/导出主命令，中部约86%采用DockLayoutManager：左约65%事件Grid，右约35%关联链及只读详情，下方可展开指标趋势；底部约6%健康、丢弃、持久Unknown、更新时刻及一个恢复动作。主列表最小700px，详情最小360px；空间不足折叠非关键详情/趋势，保留实例、权限、状态、结果及查询/取消/导出。Dock布局由Host按§8.5的WorkbenchLayout版本化保存/恢复，恢复失败回安全默认，不初始化Core、不访问私有DockLayoutManager。

使用已核对v25.2的DockLayoutManager/LayoutGroup/LayoutPanel与TableView.AllowPerPixelScrolling。Grid固定行高，不把全部Payload塞入单元格，长值截略并在只读详情展示。ChartControl.Diagram使用XYDiagram2D，Series.DataSource/ArgumentDataMember/ValueDataMember绑定有限MetricProjection DTO；精确控件及series接线在§8.6冻结，使用已查25.2.3 XML成员，不采用未定义PropertyGrid/TreeList API。关联链以OperationId/ParentOperationId/Trace/Span分层，缺口标文字，禁止按相邻时间补父。

视觉统一使用Host主题/字号/间距/图标；重要状态同时用文字和颜色，Unknown不与Healthy同色。控件只对展开/选中提供短过渡，关闭动效不影响取消。高级字段/修订默认折叠，SuperTip说明UTC范围、持久Unknown、Gap需重查、导出期限仅结束等待；不得把关键命令藏进菜单。

筛选联动采用generation+独立CancellationTokenSource，换范围递增generation，迟到结果不得覆盖新页。订阅增量进入有限UI缓冲，按最多4次/秒合并刷新，Gap显示“更新有缺口，请重新查询”，只重查当前授权范围。选中事件定位相同epoch/operation的链和指标时间，Metrics窗口保持可见。每页≤MaxQueryPageSize，未读页不全部缓存。Host通过§8.5 Services提供Access、调用SetCulture并继承主题资源，控件使用所属Dispatcher；关闭控件只RequestClose自己的订阅、取消自己的查询/导出等待；流须仍由Host保管直到ResourcesReleased。撤权立刻停止新交付并清本地敏感投影，显示拒绝原因。

键盘：Tab按筛选→查询→列表→详情→导出顺序；Enter执行有效查询，Esc取消本次等待；列表箭头选行、Ctrl+C只复制已授权选中字段，焦点返回触发控件；无键盘死锁。语言切换保留选中身份/筛选，重新解析标题、状态、错误/恢复资源，不重复放语言入口。枚举每个值与§5每个机器错误码都有三语资源（逐项覆盖断言，不直接显示enum/exception），例如：

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| diag.title | 诊断 | 診斷 | Diagnostics |
| diag.query | 查询 | 查詢 | Query |
| diag.export | 导出 | 匯出 | Export |
| diag.persistence.unknown | 写入结果未知 | 寫入結果未知 | Write result unknown |
| diag.gap | 更新有缺口，请重新查询 | 更新有缺口，請重新查詢 | Updates missing. Query again. |
| diag.export.incomplete | 导出未完成 | 匯出未完成 | Export incomplete |
| diag.wait.timeout | 等待超时，操作仍在结束中 | 等待逾時，操作仍在結束中 | Wait timed out. Operation is finishing. |
| diag.access.denied | 无读取权限 | 無讀取權限 | Read access denied |
| diag.metrics.next | 下一组窗口 | 下一組視窗 | Next windows |
| diag.metrics.maximum | 窗口最大值 | 視窗最大值 | Window maximum |
| diag.close.pending | 窗口正在关闭 | 視窗正在關閉 | View is closing |
| diag.view.detached | 未连接 | 未連接 | Not connected |
| diag.view.attaching | 正在连接 | 正在連接 | Connecting |
| diag.view.attached | 已连接 | 已連接 | Connected |

U1验收包括真实WPF/Dispatcher、固定viewport三语最长文本、DPI记录、键盘/UIA可达、快速换筛选迟到抑制、权限撤销、Gap、关闭重开及源流未退出场景。本文未执行这些检查，视觉品质和功能分别接收。

### 8.5 U1：可嵌入控件的唯一公开合同

以下为拟实现签名，尚未编译。独立程序集`Asun.Modules.Diagnostics.Wpf`、namespace `Asun.Modules.Diagnostics.Wpf`，只引用本模块Core和WPF/本机DevExpress；引用Core DTO通过`using Asun.Modules.Diagnostics`。所有自身公开成员在此定义，不泄漏内部ViewModel/Store/DevExpress句柄。具体类`public sealed class DiagnosticsWorkbench : System.Windows.Controls.UserControl, IDiagnosticsWorkbench`仅有public无参构造函数；构造只创建空视觉树/本地资源，不连接runtime，不启动查询。下述接口即该类必须实现的全部自身public实例成员；另提供`public static readonly System.Windows.DependencyProperty SnapshotProperty`，对应只读Snapshot（私有DependencyPropertyKey），供Host原生WPF绑定。标准继承的WPF成员不另造封装。

```csharp
public enum WorkbenchLifecycle { Detached, Attaching, Attached, Detaching }
public enum WorkbenchReadAction { QueryEvents, QueryMetrics, Subscribe, Export }
public sealed record WorkbenchFilter(Guid InstanceEpoch, OperationId? OperationId,
    TraceId? TraceId, DateTimeOffset FromUtc, DateTimeOffset ToUtc,
    DiagnosticSeverity MinimumSeverity, string? Code);
public sealed record WorkbenchOptions(int PageSize, int MaxRows, int NotificationCapacity,
    int MaxRecordBytes, long ProjectionBytes,
    TimeSpan RefreshInterval, TimeSpan OperationTimeout, TimeSpan CloseTimeout,
    long ExportByteLimit, string CultureName, string MetricRegistryRevision,
    IReadOnlyList<MetricDefinition> MetricDefinitions);
public sealed record WorkbenchAccessRequest(Guid RequestId, WorkbenchReadAction Action,
    DiagnosticInstanceId InstanceId, WorkbenchFilter Filter, int PageSize,
    string? MetricName, Guid? ExportId, long? ExportByteLimit);
public interface IDiagnosticsWorkbenchServices {
    ValueTask<DiagnosticAccessHandle?> AcquireAccessAsync(
        WorkbenchAccessRequest request, TimeSpan timeout, CancellationToken ct);
    ValueTask<IDiagnosticExportOperation?> BeginExportAsync(
        DiagnosticExportRequest request, TimeSpan timeout, CancellationToken ct);
}
public sealed record WorkbenchLayout(int Version, double MainWidthFraction,
    double TrendHeightFraction, bool DetailsVisible, bool TrendsVisible);
public sealed record WorkbenchBinding(IDiagnosticsRuntime Runtime,
    IDiagnosticsWorkbenchServices Services, WorkbenchOptions Options,
    WorkbenchFilter InitialFilter, TimeProvider Time);
public sealed record WorkbenchResult(DiagnosticOperationState State,
    ulong Generation, string? ErrorCode);
public sealed record WorkbenchSnapshot(WorkbenchLifecycle Lifecycle, ulong Generation,
    WorkbenchFilter? Filter, IReadOnlyList<DiagnosticRecord> Events,
    EventId? SelectedEventId, string? SelectedMetricName,
    IReadOnlyList<MetricProjection> Metrics, HealthSnapshot? Health,
    ExportReceipt? Export, WorkbenchFilter? ExportFilter,
    bool HasNextPage, bool HasNextMetricPage, bool HasGap, bool IsBusy,
    string CultureName, string? ErrorCode);
public sealed record WorkbenchCloseReceipt(bool UiResourcesReleased,
    int ActiveOperations, string? ErrorCode);
public interface IDiagnosticsWorkbench {
    WorkbenchSnapshot Snapshot { get; }
    Task<WorkbenchCloseReceipt> Detached { get; }
    ValueTask<WorkbenchResult> AttachAsync(WorkbenchBinding binding, CancellationToken ct);
    ValueTask<WorkbenchResult> ApplyFilterAsync(WorkbenchFilter filter, CancellationToken ct);
    ValueTask<WorkbenchResult> RefreshAsync(CancellationToken ct);
    ValueTask<WorkbenchResult> LoadNextPageAsync(CancellationToken ct);
    ValueTask<WorkbenchResult> LoadNextMetricPageAsync(CancellationToken ct);
    WorkbenchResult SelectEvent(EventId? eventId);
    ValueTask<WorkbenchResult> SelectMetricAsync(string? name, CancellationToken ct);
    ValueTask<WorkbenchResult> ExportAsync(CancellationToken ct);
    WorkbenchResult SetCulture(string cultureName);
    WorkbenchLayout CaptureLayout();
    WorkbenchResult ApplyLayout(WorkbenchLayout layout);
    void InvalidateAccess();
    void RequestDetach();
    ValueTask<WorkbenchCloseReceipt> DetachAsync(TimeSpan timeout, CancellationToken ct);
}
```

#### 输入有效域与挂接语义

Binding/Runtime/Services/Time非null；runtime必须Running且InstanceId非Empty。Options在Attach复制冻结：PageSize为1～1000且≤Core.MaxQueryPageSize；MaxRows=PageSize，只保存当前页及所选记录的同页引用，不无限累积翻页；NotificationCapacity为16～256；MaxRecordBytes等于Host冻结Core.MaxEventBytes（1KiB～1MiB），ProjectionBytes为1MiB～1GiB且checked覆盖`(4×PageSize+2+NotificationCapacity)×MaxRecordBytes+64KiB`：事件/指标各当前与替换页、健康双份、通知环及控制状态。实际超过规范字节上限拒绝DG-VAL-003，不临时扩容。外部保留Snapshot的内存由Host负责；RefreshInterval为250ms～5s（上限4Hz）；OperationTimeout为1ms～Core.IoTimeout；CloseTimeout为0～Core.ShutdownDrainTimeout；ExportByteLimit为1～Core.MaxExportBytes；MetricDefinitions最多256项、Name以Ordinal唯一且遵守§3.1有效域，MetricRegistryRevision须与同Host冻结Core修订一致（非空≤128 UTF-8 bytes）；复制整份定义供Kind/Unit/显示测点选择，不让UI猜Kind。只传本控件需显示的子集，实际定义必须与Core同修订相等，投影修订/单位不符拒绝DG-VER-001。冻结定义/字符串/布局/Access/Cursor控制对象合计≤64KiB（按规范UTF-8计费，含两份事件/指标游标），超限拒绝；该上限计入上述控制状态预约，不让256个完整定义暗增无界副本。UI参数由同Host已冻结Core Options校对后传入，Core继续独立校验，不靠UI可信。CultureName必须在模块资源支持集，首版zh-CN/zh-TW/en-US，可经嵌入同程序集的新资源扩展；不接受随意UI文本覆盖。Filter遵守Core UTC/枚举/身份/Code域，epoch非Empty，InstanceId来自Binding不能由筛选改写；历史epoch允许查询但不订阅历史。

Services是可信Host服务，控件不拥有或Dispose。AcquireAccessAsync输入只表示读取意图；返回null即DG-SEC-001，返回字符串也必须由Core ReadGate校验。该端口不授予Host UI任何新主权。QueryEvents请求Filter原样、MetricName/ExportId/ByteLimit为null；QueryMetrics按§8.1清Trace/Code、MinimumSeverity=Trace，保留Operation与UTC范围，MetricName必有；Export包含唯一ExportId/字节限额且MetricName=null；Subscribe使用§8.2固定合成范围（FromUtc=Runtime.CreatedAtUtc、ToUtc=DateTimeOffset.MaxValue）、当前epoch、PageSize=1，其余可选字段null。超时参数用OperationTimeout；RequestId非Empty且每次新建，与后续对应Core Query.RequestId/Subscription.RequestId一致。Core Timeout同OperationTimeout；指标窗口查询范围取Filter.FromUtc/ToUtc，不能静默扩大。

除Task观察外，所有方法须从控件所属Dispatcher调用，错线程抛InvalidOperationException；null等编程错误ArgumentException，业务/权限/超限返回WorkbenchResult+§5机器键。除DetachAsync使用显式timeout外，各异步入口以OperationTimeout有限等待，服务/Runtime任务忽略取消时仍登记原源，期限仅返回TimedOut及错误，不释放槽；Attach超时转同解除链。异步延续在投影时才Dispatcher派发，不让迟到Service延续绕过代际检查。无隐式Loaded初始化；初始Snapshot为Detached/Generation0/空集合、初始Detached为已完成释放回执。Attach只在Detached且上轮UiResourcesReleased=true可执行；冻结配置→借入runtime/services/time→构造有限UI投影/CTS/计时器→附加本控件按钮/选择处理器→当前epoch时授权并建立唯一订阅→查询首个事件页→附加成功。失败清空数据，进入Detaching，按同一解除链清理；有未退出源时返回错误且保留Detached任务，不把半挂接当成功。无权限时零敏感数据显示，Host重新授权后先完全Detach再Attach；不自动伪造测试Access。

挂接后每种工作最多一个源（事件查询、指标查询、Host授权/导出启动、订阅），所有源登记在4槽表；同种在途请求返回Rejected/DG-STATE-001，不能无限排队，筛选/选择更改仅各保留一个最新草稿。授权调用是其调用源的串行阶段（事件/指标/导出/订阅各自一个），不得另建并行授权任务；导出源的一槽同时覆盖其Begin/Wait有限等待。generation在Attach/换Filter/Refresh/撤权/解除递增且checked，溢出解除并返回DG-STATE-001。事件/指标/健康调用捕获binding代际+generation+epoch（导出按下表独立ExportId）；Dispatcher提交前再比对三者，迟到结果只清理，不覆盖当前Snapshot。Snapshot集合为不可变有限副本，setter仅模块内部；不暴露Access/Permit或原异常。IsBusy只代表本控件源，不代表设备正在运行。

#### 成员、结果与实际处理

| 成员 | 冻结处理/输出 |
|---|---|
| AttachAsync | 按上文挂接链建立一次Binding，完成返回Completed，未接纳挂接返回Rejected，期限/取消分别TimedOut/Cancelled并启动解除；返回Generation属于这次Binding。重复Attach不替换旧实例 |
| ApplyFilterAsync / RefreshAsync | 校验并递增generation，取消旧读取等待、清旧Cursor/选择/详情/趋势；旧源未退出时仅保留最新Filter并返回Running，旧源结束后只执行最后一份草稿；Refresh沿同Filter新快照。订阅的epoch/严重级别改变或转历史时，先关闭旧订阅并确认Completion后才建新订阅，历史不订阅；不重叠持有两个订阅。有效新页才替换Snapshot.Events；Failed/TimedOut等返回空新页及错误，不能显示旧页冒充新范围 |
| LoadNextPageAsync / LoadNextMetricPageAsync | 分别沿事件/指标的独立Cursor、snapshot和原Access读取下一页（新RequestId），替换对应当前页；不重新Acquire另一个Access来续旧游标。分别依据HasNextPage/HasNextMetricPage，无下一页Rejected/DG-QUERY-001；不累积缓存。游标失效/撤权提示重查，不能自动从当前数据续页。趋势显式标当前窗口页，提供“下一组窗口”命令，不把首32项冒充全范围 |
| SelectEvent | null清选择；非null必须当前页EventId，异页Rejected/DG-VAL-002；详情仅投影已脱敏记录。关联链只用当前页/已授权当前范围，缺父显示缺口，不递归加载全历史、不扩大筛选；有SelectedMetricName时仅调度一次同有限指标槽的联动查询，返回Running，最后一次选择草稿覆盖旧草稿，迟到结果需比对所选EventId |
| SelectMetricAsync | null清趋势；有效名须在Options.MetricDefinitions，形成同epoch/operation/时间范围MetricQuery，独立授权；结果仅当前页Metrics。超限/未知单位显示错误，不计算临时P95。选事件时自动把该记录OperationId用于趋势，时间仍在当前Filter内；取消选择回Filter.OperationId |
| ExportAsync | 一个活跃导出，冻结Filter/新ExportId→AcquireAccess(Export)→形成Cursor=null的Core请求→Services.BeginExportAsync→观察返回operation.WaitAsync(OperationTimeout, ct)。null为Cancelled；Running/TimedOut等回执如实进入Snapshot.Export；只显示最近回执计数和未完成状态，不编造百分比/持续进度；后续4Hz计时器只在原operation.Completion已完成时更新终态，不阻塞等待。一个控件保留一个导出引用直到终态/解除，未完成不得启动第二导出。ExportFilter冻结原范围，筛选改变仍显示该原范围，导出终态按binding代际+ExportId匹配，不使用新的事件筛选覆盖；解除后迟到终态不再提交。不得把Host已打开流视为成功 |
| SetCulture | 同步替换模块资源/格式，保留Filter/选择身份/数据，缺资源或不支持culture则Rejected/DG-VAL-002且保留原语言；枚举/错误与SuperTip覆盖三语，不直接展示enum/exception；不修改runtime |
| CaptureLayout / ApplyLayout | 同步读写纯值布局；Version仅1，MainWidthFraction为0.55～0.75、TrendHeightFraction为0.15～0.40且均有限，DetailsVisible/TrendsVisible控制渐进区。安全默认为(1,0.65,0.25,true,false)。Host只序列化该record，不能注入DevExpress XML/类型/任意控件；无效版本/数值返回Rejected/DG-VAL-002并恢复安全默认。保留§8.4最小宽及关键状态/命令，视口不够折叠渐进区，Capture记录请求布局而非临时折叠状态；不改筛选/事实/权限，Detached时可预置供下次Attach |
| InvalidateAccess | 同步清事件/详情/趋势/健康/导出敏感投影、Cursor/Access，递增generation，取消本控件等待并RequestClose订阅，转Detaching；无重新授权前不再交付。权限按钮只是投影，Core仍每次验证 |
| RequestDetach / DetachAsync / Detached | 统一解除链见下文；重复解除同一任务，期限/取消只结束该次等待。不得Stop runtime或关闭Host Stream |

通知回调只入本控件有界环缓冲，不直接Dispatcher.Invoke；4Hz计时器每次最多处理NotificationCapacity项并合并状态。缓冲满生成本地HasGap并请求当前范围重查，保留Revision防倒退；不能每通知都排Dispatcher任务。最多一个待提交Dispatcher操作，关闭时Abort未执行的本控件操作，已执行项用generation检查丢弃。健康只显示当前epoch最小诊断状态，历史筛选不把当前健康冒充历史。

#### 有限解除、Host导出Owner与迟到对象

RequestDetach立即禁止新命令、递增generation、取消本控件读取/授权/导出**等待**、RequestClose本订阅、停止计时器并解绑本控件事件处理器，清敏感Snapshot。不取消或Dispose共享runtime/services/time，不退出其它控件。Unloaded仅调用RequestDetach，不同步等待Dispatcher；临时Dock重挂接也必须由Host等Detached后显式Attach，不在Loaded偷偷重连。

DetachAsync的timeout为0～Options.CloseTimeout，未挂接时仅允许0；单调有限等待本控件源、订阅真实Completion及计时/Dispatcher投影退出。全部完成才UiResourcesReleased=true并清借入引用，完成本轮Detached；截止/取消返回false+活动数及DG-TIMEOUT-001/DG-CANCEL-001，仍Detaching且保留原任务，拒绝再次Attach。Host可移除视觉Content，但须继续持有控件直到Detached完成；禁止同步.Result/Wait。解除发起时在Dispatcher清完视觉数据/处理器后，剩余源清理与Detached完成用不捕获Dispatcher的有限源观察，不要求已关闭窗口继续派发；Dispatcher shutdown之后不再更新DependencyProperty。Host必须在关闭Dispatcher之前发起解除，Shutdown先于解除属于Host顺序错误，不能冒充UiResourcesReleased。UiResourcesReleased只表示UI自有引用/回调释放，**不等于导出Stream或runtime释放**。

Services.BeginExportAsync的Host实现必须使用Binding同一runtime：在有界Host导出表预约→取得/创建由Host拥有的目标Stream（用户取消返回null）→runtime.StartExport(request, stream, ct)→先将operation与Stream登记在Host表并安装不引用控件的Completion观察→返回原operation。此Host表采用Core.MaxActiveOperations上限，开流失败或StartExport抛编程错误时仅在确认未借出后关闭新流；句柄Rejected且ResourcesReleased=true可立即回收。operation.Completion.ResourcesReleased=true才关闭/交付该Stream；否则一直持有，不因窗口关闭、Begin/Wait超时或Host异常finally提前Dispose。控制器永远不拥有Stream，不复制另一套ExportReceipt。

Host服务忽略取消而迟到返回Access时只丢弃token，不再启动Query；迟到返回导出operation时Host已拥有源与Stream，控件只清本地引用，导出终态仍由Host表观察。迟到返回null/抛错转换为受控UI结果，不向已解除视图提交。ActiveOperations计入仍在运行的Services任务，Detach不能在它们未退出前报告UI释放。控件不把Host导出源绑到自己的Dispatcher生命周期；主动取消导出由Host持原句柄RequestCancel，Esc/解除只取消本控件等待。重新挂接不重放旧ExportId。

### 8.6 U1：唯一工程、接线与Host调用顺序

唯一控件工程：`src/Modules/diagnostics/Asun.Modules.Diagnostics.Wpf/Asun.Modules.Diagnostics.Wpf.csproj`，Microsoft.NET.Sdk、net10.0-windows、UseWPF=true，类库，ProjectReference唯一Core；唯一UI测试/可视Host工程：`tests/Modules/diagnostics/Asun.Modules.Diagnostics.Wpf.Tests/Asun.Modules.Diagnostics.Wpf.Tests.csproj`，net10.0-windows、UseWPF=true、OutputType=Exe、[STAThread]入口，仅引用本模块Wpf/Core及WPF/BCL/同版本DevExpress。不新建第三个UI demo工程、不引入待选测试框架。两工程尚未创建，本轮只冻结落点。

DevExpress直接Assembly Reference到本机25.2.3程序集及其已有传递依赖，不PackageReference/下载安装。成员接线固定：DockLayoutManager.LayoutRoot=LayoutGroup，LayoutPanel内主GridControl，GridControl继承的DataControlBase.ItemsSource=当前Snapshot.Events，TableView.AllowPerPixelScrolling=true；关联链用原生WPF TreeView/HierarchicalDataTemplate投影当前页，详情用只读TextBlock/只读TextBox，不用未核TreeList/PropertyGrid API。趋势使用ChartControl.Diagram=XYDiagram2D，LineSeries2D.DataSource=Snapshot.Metrics，ArgumentDataMember=WindowStartUtc，ValueDataMember按Options.MetricDefinitions中的Kind：Counter选Sum、Gauge/Bytes/Ratio选LastValue、Histogram/Duration选Maximum（界面明确“窗口最大值”，不误标均值/分位）。空/HasGap不补0，按Name/Unit/DimensionsSha256及连续WindowEndUtc=下一WindowStartUtc分有限片段series；HasGap窗口断开连线，单页series数量≤PageSize。不同单位分图显示，不混纵轴。SuperTip由DevExpress.Xpf.Core.v25.2.dll中的SuperTip.Items/SuperTipItem.Content构造并经原生ToolTipService.ToolTip附加，所有内容资源化。Host主题继承普通WPF资源，控件不改全局主题。

Host最小调用规格（未编译；services为上述精确接口实现）：在同一Dispatcher上`var view = new DiagnosticsWorkbench()`→`contentHost.Content = view`→`await view.AttachAsync(new WorkbenchBinding(runtime, services, uiOptions, initialFilter, time), ct)`→查看WorkbenchResult和Snapshot，失败走解除→用户操作直接调用同表方法，不让页面绕过controller读Store→Host语言变化调用SetCulture，布局保存调用CaptureLayout并由Host持久化纯值，恢复调用ApplyLayout，撤权调用InvalidateAccess→关闭先RequestDetach/await DetachAsync(uiOptions.CloseTimeout, ct)→清contentHost.Content→若false继续持有view并有限观察同Detached，不再次Attach；UiResourcesReleased=true后放掉view。Host运行异常也执行同解除链，再按§7.3 Stop runtime及归还借入端口。只关闭页面时不调用Stop；进程退出需先停止全部生产者、解除所有本Host view、协调Host导出表、再Stop全部runtime及最终资源归还。

```text
dotnet build src/Modules/diagnostics/Asun.Modules.Diagnostics.Wpf/Asun.Modules.Diagnostics.Wpf.csproj -c Release
dotnet run --project tests/Modules/diagnostics/Asun.Modules.Diagnostics.Wpf.Tests/Asun.Modules.Diagnostics.Wpf.Tests.csproj -c Release
```

与§9 Core Profile配套的完整UI输入为`new WorkbenchOptions(PageSize: 32, MaxRows: 32, NotificationCapacity: 32, MaxRecordBytes: 64*1024, ProjectionBytes: 16L*1024*1024, RefreshInterval: TimeSpan.FromMilliseconds(250), OperationTimeout: TimeSpan.FromSeconds(5), CloseTimeout: TimeSpan.FromSeconds(5), ExportByteLimit: 32L*1024*1024, CultureName: "zh-CN", MetricRegistryRevision: options.MetricRegistryRevision, MetricDefinitions: options.MetricDefinitions)`；其投影预约为10,682,368bytes（10.1875MiB）≤16MiB。初始Filter为`new WorkbenchFilter(runtime.InstanceEpoch, null, null, runtime.CreatedAtUtc, runtime.CreatedAtUtc.AddMinutes(1), DiagnosticSeverity.Trace, null)`；所有UTC值零offset，历史须显式更换epoch。第二WPF Host为另一个Window/ContentControl与独立WorkbenchBinding，同runtime共享端口也不共享控件/订阅/投影；解除一个不影响另一个。Host主题资源与窗口/contentHost归Host，ctrl仅借入。

UI测试入口维持真实STA Dispatcher消息循环，不以无窗口单测代替实际绑定；每case10s/suite120s/外层180s，任一必需跳过/失败/未完成非零。U01～U06用一个固定1920×1080验证viewport，记录client/DPI而不改显示设置。完整操作/三语最长文本/联动/Unknown/主命令/键盘与UIA、视觉紧凑与层级分别验收；性能依§12真实Profile，尚未执行。

## 9. 无 UI 最小接入与模拟夹具

以下是按本页拟实现声明编写的调用规格，尚未创建工程或经C#编译。夹具名仅为未来唯一测试工程内部类型，不是新Core端口；不使用await using或不存在的Clock/Budget属性。

```csharp
var instanceId = new DiagnosticInstanceId(Guid.NewGuid());
var options = new DiagnosticsOptions(
    InstanceId: instanceId, ConfigRevision: "test-config-1", ProducerVersion: "test-host-1",
    RedactionRevision: "test-redact-1", MetricRegistryRevision: "test-metrics-1",
    QueueCapacity: 4096, QueueBytes: 64L*1024*1024, MaxEventBytes: 64*1024, BatchSize: 128,
    FlushInterval: TimeSpan.FromMilliseconds(250), CriticalReservedCount: 64,
    CriticalReservedBytes: 4L*1024*1024, DebugSampleRatio: 1,
    MaxReceiptEntries: 16384, MaxMetricSeries: 256, MetricWindowCount: 60,
    MetricWindowWidth: TimeSpan.FromSeconds(1), MaxSnapshots: 16,
    SnapshotTtl: TimeSpan.FromSeconds(30), MaxQueryPageSize: 32,
    MaxSubscribers: 4, SubscriberCapacity: 32, CallbackTimeout: TimeSpan.FromSeconds(1),
    MaxActiveOperations: 8, ReadBufferBytes: 128L*1024*1024,
    MaxExportBytes: 32L*1024*1024, IoTimeout: TimeSpan.FromSeconds(5),
    HealthPollInterval: TimeSpan.FromSeconds(1), HealthSampleMaxAge: TimeSpan.FromSeconds(5),
    ShutdownDrainTimeout: TimeSpan.FromSeconds(10),
    MetricDefinitions: new[] { new MetricDefinition("stage.ms", DiagnosticValueKind.Duration,
        "ms", 0, 10000, Array.Empty<string>(), new double[] { 1, 5, 10, 100 }) });
var time = new ControlledTimeProvider();
var store = new BoundedMemoryStore();
var redaction = new TestWhitelistRedaction("test-redact-1");
var gate = new TestReadGate();
var dependencies = new DiagnosticsDependencies(
    store, redaction, gate, Array.Empty<IHealthProbe>(), time);
// hostPending是Host生命周期监督者持有的有界表，不是方法内临时字典。
// 表和槽的具体要求在下文；满表在Create/开流之前拒绝，不扩容。
var slot = new HostLifetimeSlot { Dependencies = dependencies };
lock (hostPending) {
    if (hostPending.Count >= options.MaxActiveOperations ||
        hostPending.ContainsKey(instanceId))
        throw new InvalidOperationException("host lifetime slot unavailable");
    hostPending.Add(instanceId, slot); // Owner先登记，再产生任何Core源任务。
}
try {
    var created = DiagnosticsRuntime.Create(options, dependencies);
    slot.Runtime = created.Runtime; // 先保存返回实例，再检查/消费结果。
    if (slot.Runtime is not { } runtime)
        throw new InvalidOperationException(created.ErrorCode);
    var operationId = new OperationId(Guid.NewGuid());
    var draft = new DiagnosticEventDraft(instanceId, new EventId(Guid.NewGuid()), operationId,
        null, null, null, null, time.GetUtcNow(), DiagnosticSeverity.Information,
        DiagnosticEventKind.Started, "OPERATION.START", "diag.operation.start",
        new Dictionary<string,string> { ["stage"] = "replay" }, ReadOnlyMemory<byte>.Empty, null);
    var accepted = runtime.Report(draft);
    // 断言/下游消费可抛错，仍须进入同finally；此处只接受正常Profile结果。
    if (accepted.Outcome != DiagnosticOutcome.Accepted)
        throw new InvalidOperationException(accepted.ErrorCode);
    var flushed = await runtime.FlushAsync(instanceId, options.IoTimeout, ct);
    var query = new DiagnosticQuery(Guid.NewGuid(), instanceId, runtime.InstanceEpoch,
        operationId, null, time.GetUtcNow().AddMinutes(-1), time.GetUtcNow().AddMinutes(1),
        DiagnosticSeverity.Trace, null, 32, null, new DiagnosticAccessHandle("test-only"),
        options.IoTimeout);
    var page = await runtime.QueryAsync(query, ct);
    if (page.State != DiagnosticOperationState.Completed)
        throw new InvalidOperationException(page.ErrorCode);
    slot.Output = new MemoryStream(); // 不使用using；先由已登记的槽持有。
    var request = new DiagnosticExportRequest(Guid.NewGuid(), query,
        options.MaxExportBytes, options.IoTimeout);
    slot.StartInvoked = true; // 此后抛错而无句柄，也保守认为可能借出。
    slot.Export = runtime.StartExport(request, slot.Output, ct);
    var exportResult = await slot.Export.WaitAsync(options.IoTimeout, ct);
    var completed = await slot.Export.Completion.WaitAsync(options.IoTimeout, ct);
    if (!completed.ResourcesReleased)
        throw new InvalidOperationException("export lease held");
    // 下游处理page/exportResult/completed也必须位于此try内。
}
finally {
    // 用户ct可能已取消；清理独立于ct，先发起，再有限观察同一源。
    Task<DiagnosticStopReceipt>? stopWait = null;
    using var cleanup = new CancellationTokenSource(options.ShutdownDrainTimeout);
    try {
        if (slot.Export is { } export) export.RequestCancel();
    }
    catch (Exception) { slot.CleanupErrorCode = "DG-EXPORT-001"; }
    try {
        if (slot.Runtime is { } runtime) {
            stopWait = runtime.StopAsync(instanceId, options.ShutdownDrainTimeout,
                CancellationToken.None).AsTask();
            slot.StopWait = stopWait; // 超时仍保存原等待任务，不能遗失。
            slot.Stopped = runtime.Stopped; // 原真实终态任务，不重建实例。
        }
    }
    catch (Exception) {
        slot.CleanupErrorCode = "DG-STATE-001";
        if (slot.Runtime is { } runtime) slot.Stopped = runtime.Stopped;
    }
    try {
        if (stopWait is not null)
            await stopWait.WaitAsync(cleanup.Token);
        if (slot.Stopped is { } stopped)
            await stopped.WaitAsync(cleanup.Token); // 共用此有限清理预算。
    }
    catch (Exception) { slot.CleanupErrorCode = "DG-TIMEOUT-001"; }
    // finally不无条件Dispose、不无限await、不重建runtime或再次StartExport。
    lock (hostPending) {
        // 已预登记的同一槽原地移交；没有关闭时再找一个可能满的接收队列。
        slot.SupervisorOwns = true;
        if (!ReferenceEquals(hostPending[instanceId], slot) || !slot.SupervisorOwns)
            throw new InvalidOperationException("host ownership acknowledgement failed");
    }
    // 原业务异常继续传播；监督者已确认持有全部引用，不依赖本方法继续存活。
}
```

示例中的`HostLifetimeSlot`只在唯一测试工程/其Console Host内部定义，不是新模块端口。具体字段如下，使用同一有界Host表`Dictionary<DiagnosticInstanceId, HostLifetimeSlot>`；表由生命周期监督者持有，所有登记/移交/回收在同一锁内，监督者只处理`SupervisorOwns=true`槽，移交前字段仅由上述方法写入。

本BCL示例的time/store/redaction/gate构造不取得需释放的外部连接。真实Host须在**取得第一个有Owner的适配对象前**预约同一槽，每取得一个Owner立即登记到该槽，取得中途失败也走同finally与§7.3发布前分支；不能先开连接再因Host表满丢失Owner。槽已预约而尚未调用Create可安全归还已取得Owner，未取得的不释放。示例只把完全构成的Dependencies放入槽，真实Owner集合必须保留逐个取得状态，不假定一个Dependencies能替代适配释放句柄。

```csharp
internal sealed class HostLifetimeSlot {
    public DiagnosticsDependencies? Dependencies;
    public IDiagnosticsRuntime? Runtime;
    public Stream? Output;
    public IDiagnosticExportOperation? Export;
    public bool StartInvoked;
    public Task<DiagnosticStopReceipt>? StopWait;
    public Task<DiagnosticStopReceipt>? Stopped;
    public bool SupervisorOwns;
    public string? CleanupErrorCode;
}
```

监督者确认移交后，按固定有限节拍逐槽检查，不为每槽无限Task.Run/await：

1. **未借出流。** Output非null但StartInvoked=false，说明开流后在调用之前失败；仅该Stream可立即关闭并清字段，不要求Core停完才能关它。StartExport返回Rejected/其它终态且原Completion成功并明确ResourcesReleased=true，同样可关闭流。不能仅看Outcome或Wait的超时回执判定释放。
2. **已借出或调用结果不明。** StartInvoked=true后，无句柄/Completion fault/cancel/未完成都保留原Output。只有原Export.Completion成功且ResourcesReleased=true，或原runtime.Stopped成功且ResourcesReleased=true证明该实例全部IO已实际退出，才关闭并清流；Stopped中的持久Unknown不妨碍真实资源退出，但不能改成Persisted。无句柄且原Stopped未释放时不重试StartExport。
3. **借入端口。** Create返回null/发布前抛错且无runtime时，依§7.3保证无Core源，可由Host释放自己取得的Owner；否则仅原Stopped成功且ResourcesReleased=true，且该共享端口所有其它runtime也真实停止后，才依外部适配释放合同逆序归还。本示例BCL夹具无需Dispose，不假造持久资源；真实Host用已有Owner释放动作，Core仍不Dispose它们。Owner释放动作抛错保留槽/错误，不把失败当已释放。
4. **未排空与迟到。** 监督者每次观察最多IoTimeout，使用自己的非用户取消预算；Stop发起异常时沿同Runtime有限重试Stop并保存原Stopped，正常Draining只观察原任务，不不断新增Stop等待。对StopWait/Completion/Stopped的fault/cancel记录受控机器键，不能以任务结束替代ResourcesReleased。槽满拒绝新实例/导出，不驱逐持有中的槽；迟到终态仅归还原槽资源，不回传到已失败消费路径。流和端口全部真实归还后才移除该槽。移交确认失败属Host不变量错误，原表仍保留槽且Host不得退出/释放资源，需修复监督者所有权；不伪造排空成功。

这些步骤是本页具体最小Host的收尾规格，不是包发布/下载服务。监督者生命周期覆盖方法/窗口退出；程序整体退出若仍有未归还槽，结果为排空未知/失败，不能宣称正常停止。工作异常保留原传播路径，清理异常只保留一个受控CleanupErrorCode（示例有限清理等待失败统一DG-TIMEOUT-001，不能作为根因诊断），不得递归写故障Store或泄露原Exception.Message。

该Profile按§3.2冻结预约计算：回执16MiB、通知8MiB、指标(1+8)×256×60×(256+8×5)=40,919,040bytes、读页8×32×64KiB=16MiB、操作32KiB、快照64KiB、staging与输出8×(64KiB+64KiB)=1MiB，总额约80.12MiB，小于128MiB。桶数含隐含+∞，故为5；复制/排序临时读页只使用同一个预约的缓冲或双缓冲计费，不暗增第二份完整页。队列/在途共同64MiB，Critical预留4MiB；这不是实测工作集/客户性能Profile。其它配置须同算法重算。

TestWhitelistRedaction只允许stage键及空Payload/ResourceRef，未知字段拒绝；BoundedMemoryStore容量固定，原子逐项回执，可控制NotPersisted/Unknown/写入闩锁、不可变snapshot/可靠NoPendingAttempt，按实例隔离，不读产品库。ControlledTimeProvider控制UTC、单调timestamp/frequency及CreateTimer，必须推进等待调度，不仅改GetUtcNow。TestReadGate检查固定test-only、范围hash/动作/epoch、审计顺序和撤权闩锁，永远不用于生产。测试夹具实现这些完整public端口；不建立第二套DTO、不下载测试包、不增加生产模拟程序集。

第二消费者以独立长稳Console Host同时创建不同InstanceId runtime，同一个Core包、独立TimeProvider/配置/订阅，可故意共享Store验证实例隔离；不用第一Host的静态全局状态。第二Host记录Metric/查询窗口、导出及关闭，第一Host仍可Report/Flush。UI只是后续第三接入投影，不把两个带皮肤的同一Shell算双消费者。

## 10. 具体场景、异常与恢复

所有算例为软件合成断言。生产者负责阶段：同OperationId的Started、Waiting、Completed分别使用EventId e1/e2/e3，可乱序到达，Sequence只表接收序；未知父保持缺口。AttemptId、外部状态、retry资格仅是白名单Attributes，不新增视觉/MES/运动专属字段，不自动重试副作用。秘密、原请求响应正文、条码、凭证URL、SDK句柄均不作为Payload；脱敏失败不改业务结果。

| 场景 | 输入与可判定结果 | 恢复责任 |
|---|---|---|
| 正常与重复 | e1接纳序列1；同e1同摘要重试仍序列1；e2同operation接纳序列2 | 查询原回执；不同内容需新EventId |
| 身份冲突 | e1 Code从OPERATION.START变为OPERATION.END | DG-ID-001，旧回执不替代新输入 |
| 普通满载 | 预留之外容量耗尽，Information新身份 | Rejected/DG-QUEUE-001；Error仍可用关键预约 |
| 采样 | Trace比率0、新EventId | Dropped，无序列/后台写；Critical不采样 |
| 写回执丢失 | Store已写但抛错/无逐项回执 | Accepted保持，Unknown；沿e1查证，禁止盲重写 |
| 屏障 | H=3后e4接纳，e1～e3持久完成，e4闩锁未开 | Flush只等≤3；不因e4阻塞、不用队列空作证 |
| 桶边界 | Duration桶[1,5,10,100]，样本1、5、6ms | 桶计数[1,1,1,0,0]，Count3/Sum12；同SampleId不再累加 |
| 时间回拨 | UTC回拨，单调时钟推进一窗口 | Sequence递增，按单调窗口入新桶；原ObservedAt不重写 |
| 订阅缺口 | 慢回调耗尽通知队列 | Gap含丢失Revision闭区间；事件持久计数不受影响 |
| 自关闭 | 回调内RequestClose或CloseAsync | 请求成功；自等待立即false，源退出后Completion终结 |
| 超时迟到 | Export写源忽略取消，Wait截止 | Wait TimedOut/Incomplete，流仍借用；释放闩锁后Completion真实释放 |
| 撤权/审计不可用 | 读取前/Seal后撤权或Seal失败 | Items空/无新输出字节；不泄露秘密/旧包hash |
| Stop超时 | 批写或Probe仍在途 | Lifecycle Draining，重复Stop同一Stopped；源终结才Stopped |
| 版本回退 | Store出现未知Major/单位/旧定义 | DG-VER-001；保留旧原件，不猜字段、不删新数据 |

静态工厂声明中的NotImplementedException仅表达未实现规格，不能作为后续产品实现或测试通过路径。

只读恢复为重查原身份/新建有效查询；诊断模块不执行设备复位、MES上传、业务重试、质量处置、日志删除或权限批准。Store故障只更新内存健康，不能递归写自己的错误。导出失败Host保存不完整元数据，不能覆盖上一次完整结果。

## 11. 测试与验收矩阵

本轮仅冻结断言，尚未执行。全部case映射到唯一测试工程，确定性TimeProvider/闩锁，逐case与全局有限截止；不使用Sleep猜调度、不使用InfiniteTimeSpan。

| ID / 切片 | 输入或故障 | 断言 |
|---|---|---|
| DG-T01 / C1 | 正常/空Guid/UTF-8字节边界/嵌套Payload/枚举未知 | 有效接纳且复制；无效不入队、不截断；返回后修改原字典不影响记录 |
| DG-T02 / C1 | 同Operation不同EventId、同EventId同/异摘要、并发100次同身份 | 多阶段合法；同身份只一次接纳/写入；异内容拒绝，计数等式一致 |
| DG-T03 / C1 | 普通满、Error预留、比率0、回执表满、在途批次 | 不驱逐Accepted；双预约无泄漏；序列只给接纳项，溢出Faulted |
| DG-T04 / C1 | 取消/截止与接纳锁竞态 | 未接纳Cancelled/TimedOut不后台入队；已接纳返回Accepted；取消不删除 |
| DG-T05 / C1 | 部分/重复/多余批回执、回执丢失、可靠与不可靠查无 | 逐项分类；Unknown保留；只可靠NoPendingAttempt允许重接；计数不重增 |
| DG-T06 / C1 | FlushH后继续接纳、Channel空但写源未退出 | 仅≤H；Pending不Complete，后接纳不延长屏障 |
| DG-T07 / C1 | Stop前/中/后、忽略取消源、异常/健康递归 | 超时仍Draining；真实退出才释放且恰一次；Stopped有Unknown仍不伪造已写 |
| DG-T08 / C2 | 桶上界/负值/NaN/溢出/单位/series上限/重复SampleId | §10算例准确；无效不接纳；Count/桶和一致；持久/实时分开 |
| DG-T09 / C2 | UTC回拨、窗口轮转、持久重放、定义修订 | 单调窗口稳定，重放使用存储窗口；HasGap不补0；异版本不混合 |
| DG-T10 / C2 | Probe慢/异常/过期/未来/身份冲突/来源错/跨epoch | Unknown，单探针仅一源、未退出不重调度；不产生设备Readiness |
| DG-T11 / C3 | AND筛选/空页/分页并发写/历史epoch/metric范围 | 筛选先分页；同快照无漏重，H不跨epoch；指标完整扫描后分页 |
| DG-T12 / C3 | 游标改字节/过期/跨Access/筛选/索引或代际变化 | 拒绝，无回退当前数据；有限快照实际释放；Secret不入错误 |
| DG-T13 / C3 | Begin/Bind/Seal/Validate故障及各边界撤权 | 审计成功才交付；读取及历史回执不靠UI授权；拒绝零数据 |
| DG-T14 / C3 | Export同/异请求、不同Stream/Access、超限/部分写/迟到 | 同请求不再写第二流；异请求拒绝；hash/bytes/LF准确；真实退出才ResourcesReleased |
| DG-T15 / C3 | Gap、回执迟到、慢/抛错回调、自Close、撤权 | Revision防倒退；Gap闭区间；单回调/槽有界；关闭不停止runtime |
| DG-T16 / S1 | 两Host同时运行、共享Store、关闭其一 | 实例/序列/语言投影/缓存无串扰，同公开契约无Host分支 |
| DG-T17 / C1～C3 | 未知Schema Major/旧单位/回退 | DG-VER-001，原件保留；无伪迁移成功 |
| DG-T18 / C1～C3 | 全资源槽/预算边界、循环Query/Export/Subscribe | checked预约及完整归还，保留源时不重新占同槽；无无限副本/任务/标签 |
| DG-A01 / A1装配 | 依赖/修订无效、Probe属性getter抛错、预算不闭合 | Create返回null，无Append/Gate/Probe/回调任务；借入对象不Dispose，模块自有租约归零 |
| DG-A02 / A1装配 | 发布后计时/写泵启动异常、业务启动失败 | 已返回runtime Faulted→同Stop链；不返回null掩盖任务；未Stopped前Owner不释放 |
| DG-A03 / A1装配 | 两实例共享Store/Time、关闭其一、另一个源迟到 | 最后一个真实Stopped后共享Owner仅释放一次；原Stopped/Unknown可追踪，无递归日志 |
| DG-H01 / S1、A1装配 | Query/消费/开流/StartExport/Wait/Completion逐点抛错，工作ct预取消或中途取消 | 所有已返回runtime均进入finally并以CancellationToken.None发起有限Stop；原Stopped与StopWait保存在同预登记槽，原业务异常继续传播，不无条件释放端口 |
| DG-H02 / S1、C3 | 开流成功但未调用、StartExport抛错无句柄、Completion fault/cancel/迟到、Stop超时 | 未调用流可立即关闭；已调用结果不明保留，只有原Completion或原Stopped成功且ResourcesReleased=true才释放；无无限await、无重开ExportId/实例 |
| DG-H03 / S1、A1装配 | Host表满、取得适配一半失败、移交/Owner释放失败、共享端口仍有活跃实例 | 先预约后取得Owner；同槽原地确认移交，满表不驱逐；Owner逐个逆序归还，异常/未确认保留槽；迟到回执仅回收原资源，不覆盖消费结果 |
| DG-U02 / U1 | 无参构造、Attach失败/重复、错线程、两个Host/控件 | 构造零IO；半挂接转解除；错线程有明确异常；实例/订阅不串，关闭其一不Stop runtime |
| DG-U03 / U1 | 连续改筛选/选择、事件与指标续页、旧Access变化 | 仅最后草稿执行，4槽/一个Dispatcher提交有界；续页同Access/快照；迟到不覆盖当前代际，指标不隐瞒分页 |
| DG-U04 / U1 | Services忽略取消迟到返回、回调/Dispatcher在途、Detach超时重挂接 | 未退出UiResourcesReleased=false，重复同Detached；迟到token不查询、迟到export仍由Host持流；未释放拒绝Attach |
| DG-U05 / U1 | 导出等待超时、换筛选、关窗口、Host StartExport异常 | 原ExportFilter/ExportId绑定；控件不关闭流，Host真实Completion后才释放；失败未借出分支逆序收尾，无旧终态覆盖新导出 |
| DG-U06 / U1 | 本地投影预算、环满、权限撤销、Dispatcher关闭顺序 | 预约不闭合拒绝Attach，环满HasGap；撤权立即清敏感投影；解除后源清理无需已关闭Dispatcher |
| DG-U01 / U1 | §8.4真实WPF任务链与三语、权限、键盘/UIA | 1920×1080唯一viewport，迟到不覆盖、关闭只自身；功能与视觉品质各验收 |

A1后续真实存储/授权/审计需耐久重启、磁盘满/断电/事务回执丢失、撤权、长期资源与恢复对账。P1/R1按§8.3.2～8.3.4软件协议绑定以下断言；不以当前流测试替代真实集成门。这些是既有测试/集成范围的实施断言，本轮未创建测试文件或执行测试。

| 完整范围增量场景 | 可判定断言与消费者 |
|---|---|
| DG-I01：规范输入/NDJSON，逆序字典/负零/不同Culture/UInt64 | 实际.NET生成§8.3.1的640/949bytes及两个hash；ByteLimit 949/948边界；非ASCII/转义沿固定encoder，不从Python差异反改格式。Core/双Host消费。 |
| DG-I02：Seq2已提交，快照G后Seq1才提交 | 旧页只含G时成员，不含迟到Seq1；新快照可读Seq1/2；没有重复/缺口冒充快照完整。A1 Store消费。 |
| DG-I03：回执丢失、恢复代变更、retire后原身份重试 | Unknown沿原operation/identity查询，无新写；恢复代未核及retired返回NoPendingAttempt=false；同身份异内容不能覆盖。A1/R1消费。 |
| DG-I04：最终交付预约前/后撤权、审计写入未知 | 撤权先提交时新字节0；交付先提交只限原有界单元，后续0；Read/NotRequired不当Sealed，Unknown不披露数据。A1 Gate及P1消费。 |
| DG-I05：manifest长度/次序/附件/签名/key/尾随字节篡改 | 任一失败无Published/下载引用；源Owner变更/hash不符拒绝；无签名回退0。只有真实SealedDurable和原子Owner引用才发布。P1双Host消费。 |
| DG-I06：同键并发、签名后崩溃、封口后/发布响应丢失 | 一原operation/原包；不同摘要Conflict；查询不续写；旧完整包不覆盖，确认后只重放同ObjectRef，不因ECDSA随机签名换hash。P1消费。 |
| DG-I07：range越界/跳跃/异主体/重复确认，最终确认响应丢失 | 未授权新字节0；只有原pendingRange连续CAS；offset不重增；全包确认及耐久CAS前不消费许可，响应丢失同DownloadId查询。P1 transport消费。 |
| DG-I08：Preview后新增法律保持/快照/引用，resolver Unknown，GC结果未知 | 每步当前重验及同协调边界；受影响对象零删除/Skipped；Unknown不重删，身份账本语义保留；不触及其它事实Owner。R1消费。 |

I01可在已指定Core.Tests实施并只验证Core编码；I02～04由获准A1适配验证，I05～08由具体消费Host已有集成测试承接，不能为了记录规格提前建第三套工程。最小两个Host分别为无UI服务与独立维护CLI：服务产生原诊断并交回执/包引用，CLI只经当前授权窄读/下载/保留预览，不能读服务私表；实际维护副作用另授权限。测试Owner仍在本模块永久会话，跨Owner实现仅在其原会话完成。

## 12. 性能、容量与可观测性

本节冻结测量协议与测点，不设未经真实消费者采纳的性能达标值。每个不可变 BenchmarkProfile 必须记录唯一 ID/修订/hash、构建提交与 .NET/适配器/后端版本、OS 与 CPU/内存/存储/网络配置、带 hash 的输入集及规模分布、调用混合与并发/到达模型、队列与资源预算、时钟测点边界、故障注入点，以及 ColdSampleCount、WarmupIterationCount、MeasuredSampleCount 和各指标的验收目标/阈值来源。Profile 变更必须产生新修订，不得跨 Profile 合并数据。

冷测每个样本均从新进程/新模块实例开始，并清空模块自有缓存；OS 文件缓存、数据库缓存、外部服务和设备状态无法由模块清空时，必须记录其实际状态，使用隔离可重建夹具，不标称为冷。热测先按 Profile 固定次数执行预热，再按固定样本数测量；不使用自适应停止、只报最快值或丢弃慢样本。外部副作用操作使用可重建隔离夹具和唯一操作 ID。每个样本用单调时钟记录原始耗时；P50/P95/P99 的算法按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md) 计算，并同时报告样本数、单位和原始值。吞吐量使用 Profile 固定的观察窗口计算已完成且有效的操作数/时间，并单列拒绝、错误、重试和未完成项。

每轮同时记录 CPU、工作集/私有字节、托管分配与 GC、native/适配器缓冲、磁盘/网络 I/O、连接/句柄峰值，队列当前/峰值条数与字节、排队等待、积压变化、接受/拒绝/丢弃计数。排空时间从关闭新接纳开始，至在途操作、回调、IO/适配器资源全部实际归还结束；期限到达只记超时和未完成项，不得强杀后宣称排空。每项验收阈值必须引用消费者要求、正式 Contract/资源风险依据或已批准资格记录的稳定 ID；没有来源时写 TargetPending，只能报告测量结果，不得判定达标。协议/资源硬上限与性能目标分开，只有唯一权威中的必要性、数值和来源均已明确时才可作为硬上限，不从基准数据臆造上限。

### 本模块固定测点
分别测 Report 校验/脱敏/序列化、异步接纳等待、批写/刷盘/持久回执、分页查询、流式导出的首字节与完成时间。Profile 固定事件字节分布/严重级别比例、突发与稳态输入计划、批大小、持久适配器/磁盘、订阅者数量和消费速率、查询/导出范围。记录事件/指标/健康独立接纳/拒绝/持久化/丢弃完整性、操作槽/回执槽/快照/series-window/subscriber的当前与峰值、源真实归还时刻；失败/未读/超时/删失样本及排空Unknown另列，目标缺失结果NotEvaluated。记录条数与字节队列水位、慢订阅者隔离、磁盘/内存峰值、导出输出字节和排空剩余项；数据量相关的容量和延迟阈值没有部署方依据时均为 TargetPending。

## 13. 发布、回退与集成门

先在唯一Core工程提供namespace Asun.Modules.Diagnostics的公开契约与无UI实现，不预建空Contracts包。真实消费者与独立发布生命周期稳定后才拆Asun.Diagnostics.Contracts/Core/存储适配/可选WPF包，沿用同一声明；不复制DTO或改接口绕过接收。发布携net10.0、Schema/API版本、公开依赖、显式配置及错误资源、变更/迁移与回退说明。

C1～C3/S1按附录A逐切片接收；真实适配A1另绑定正式Owner/平台映射、后端耐久与跨进程身份对账、实际脱敏白名单、可信授权审计、真实负载/保留/性能Profile。U1按§8.5～8.6控件合同/唯一工程接入，绑定PageContract和实际DevExpress/WPF验收；依赖按已确定版本直接引用，不核验安装/许可证。没有客户阈值只报告NotEvaluated。

升级按§7.2真实排空、新epoch、只读兼容与回放；回退保留新版本日志、用户配置、未知回执/未完成流及来源hash。不支持格式明确拒绝、不删字段、不清日志以恢复。实际仓库/分支在后续实现任务绑定，本地文档阶段不声称HEAD。

## 14. HALCON/AsunImage 适用性与资料依据

本模块是非视觉事务能力，没有图像算法、HALCON 算子或 `ImageLibDotNet` 调用；HALCON 26.05 算子核对项对本模块记为“不适用”。若未来记录视觉资源，只接收视觉模块经公共边界产生的稳定引用和错误上下文，不持有图像对象，不复制图像事实，也不把诊断指标当视觉质量指标。

本指导依据并受以下资料约束：

- `PROJECT_ENTRY.md`、`PROJECT_PROGRESS.md`、`docs/independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md`
- `docs/shared-modules/packages/PKG-005_Diagnostics.md`、`docs/shared-modules/modules/SM-005_diagnostics.md`
- `docs/01-governance/DEV-GOV-005_模块独立性与复用标准.md`、`DEV-GOV-010_实施级规格唯一标准.md`
- `docs/shared-modules/guidance/02-platform/DEV-PLT-013_跨模块事件与外部互联开发指导.md`、`DEV-PLT-014_性能预算与并发流水线开发指导.md`、`DEV-PLT-016_部署、Supervisor与本机隔离开发指导.md`
- 只读外部对照：`H:\docs\40-development\00-standards\可观测性与诊断开发指导.md`，本次读取版本 SHA-256 `EA5690C1D914DCBF964AD0705208698C28A9BDE5D55ACA4A1D07E1F6A95007EE`，文件时间为 2026-10-04 11:50（H 盘）；重点对照 §3、§7.1、§8、§10、§11、§13.5。吸收仅限授权查询边界、快照游标、导出完整性、续传及保护引用方面的可复用约束。来源技术基线标为 HALCON 24.11；本项目按 26.05。此模块无 HALCON/ImageLib 调用，未将来源中的任何算子/API 细节迁入；来源中的 Asun.Logging/AOI 类型、实现状态、认证事实、SQLite 方案、具体签名算法及 2D/3D 产品流程均未成为本模块契约或实现证据。
- 只读参考：`../../references/project-snapshots/AsunControl/20261004/original/ClassLibrary\TcpCommon.cs` 与 `TcpServerEx.cs`。其中有界帧长度、取消传播、心跳计数和连接级资源释放可作为一般工程参考；其 .NET 8/WinForms/TCP 实现不是本模块依赖，也未被复制。
- 只读参考：`docs/references/project-snapshots/DZ-XVision/20261004/README.md`、`Motion9014/MotionUtil.cs`、`DZ-XVision/SimpleMes/MesCommunicationLogger.cs`、`DZ-XVision/SimpleMes/SimpleAoiMesClient.cs`、`SPC-YSmart30/SPC-YSmart30/SqlData.cs`。仅采纳阶段节点、请求/响应分离、尝试/超时/停止结果和操作审计的定位经验；原始请求/响应正文、条码/URL、密码流转、旧文件命名、数据库表结构、MES 状态和旧 API 均判定为不适合直接迁移。
- 只读来源审查：`H:\docs\40-development\70-operations\维护健康备份升级开发指导.md`，SHA-256 `6af219d420fc9feb953a3fca9d2946fe3fe64e5ac74ed8cc63b30416b6479b02`，映射状态 `not-reviewed-in-full-hdocs-audit`。采纳为通用 diagnostics 增量：健康样本以稳定检查/样本身份、来源版本、证据摘要和单调时间域绑定；连续历史按不可变快照重算；诊断包在来源复核、脱敏、manifest/签名校验后原子发布；幂等回执重放仍需当前授权；保留清理在一致代际解析并于隔离/删除前重验保护引用，未知时零删除。排除其 Operations/设备/升级/备份业务状态、签名策略、客户阈值、产品编排、UI 和验收结论；诊断模块不接管设备/维护决策、通用存储或其领域事实。来源标注 HALCON 24.11，本模块按项目 HALCON 26.05 规则；本次只讨论非视觉事务，没有 HALCON 算子或 AsunImage API 增量。


### 固定官方/源码证据与适用限制（2026-10-09）

- [.NET Channels官方说明](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)：采用Wait+TryWrite及有界背压；不采用Drop*驱逐已Accepted项。BCL TimeProvider用于UTC/单调时间/可控计时器；不引入外部Clock包。
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)：32/16小写hex、非全零及Trace/Span关联约束；不将trace作为业务身份。
- [OpenTelemetry .NET core-1.12.0固定commit](https://github.com/open-telemetry/opentelemetry-dotnet/tree/a67acd87d5e4d437c5398664f75faa19494beb9c)，Apache-2.0。已读BatchExportProcessor源码及日志/trace批处理测试：采纳有界排空逐项计数、复制ThreadStatic/scope输入及触发Flush/Shutdown后验证源实际完成；不采纳源码测试中的Infinite/Sleep，也不引入SDK/其默认丢弃行为。该版本依赖Microsoft.Extensions.Diagnostics.Abstractions/Logging.Configuration，Directory.Packages.props中LatestRuntimeOutOfBandVer=9.0.0；本Core仅BCL，不迁入这些依赖。

| 固定commit内文件 | SHA-256（实读版本） |
|---|---|
| src/OpenTelemetry/BatchExportProcessor.cs | af94e80f5e5c2ad346518678f4be166180aff32e49061d588d1df58d289a9204 |
| test/OpenTelemetry.Tests/Trace/BatchExportActivityProcessorTests.cs | f7e10ca54d2a86aea212447cf0a97e719ab1bd599f9c717d60a7b335bc92d00e |
| test/OpenTelemetry.Tests/Logs/BatchLogRecordExportProcessorTests.cs | b1e3e57ba32b868a67fee22f885f808b8b75ad00641faaf29dbf2a34b65fead6 |
| LICENSE | c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4 |

DevExpress v25.2官方资料已核对[DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[TableView.AllowPerPixelScrolling](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TableView.AllowPerPixelScrolling?v=25.2)、[ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)：分别为DevExpress.Xpf.Docking.v25.2、Grid.v25.2、Charts.v25.2.dll。ChartControl使用Diagram/XYDiagram2D、Series.DataSource/ArgumentDataMember/ValueDataMember。官方文档家族25.2与本机25.2.3同基线；页面展示的更新补丁不是本项目升级要求。本会话无dxdocs工具，使用官方网页定向读取；尚未运行本机WPF，不声称真实渲染通过。已读上述源码/测试用于设计证据，未复制产品代码、不作生产性能证明。


本次仅按成员名定向复用本机25.2.3公共XML（2026-10-10），没有扫描厂商内部实现。统一根目录为`C:/Program Files/DevExpress 25.2/Components/Offline Packages/`，下表每个包路径中间固定`25.2.3/lib/net8.0-windows/`；这是已安装程序集说明位置，不安排NuGet获取或替换。核对到DockLayoutManager.LayoutRoot/LayoutGroup/LayoutPanel、GridControl及其继承DataControlBase.ItemsSource、TableView.AllowPerPixelScrolling、ChartControl.Diagram/XYDiagram2D/LineSeries2D及Series.DataSource/ArgumentDataMember/ValueDataMember、SuperTip.Items/SuperTipItem.Content。WPF原生ContentControl.Content、TreeView、只读文本、Dispatcher和ToolTipService只承担宿主视觉/线程边界，不向Core引入UI依赖。

| 25.2.3 XML包/文件 | SHA-256（定向实读文件） |
|---|---|
| devexpress.wpf.docking/DevExpress.Xpf.Docking.v25.2.xml | b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f |
| devexpress.wpf.grid.core/DevExpress.Xpf.Grid.v25.2.xml | 7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd |
| devexpress.wpf.grid.core/DevExpress.Xpf.Grid.v25.2.Core.xml | 9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba |
| devexpress.wpf.charts/DevExpress.Xpf.Charts.v25.2.xml | 2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0 |
| devexpress.wpf.core/DevExpress.Xpf.Core.v25.2.xml | cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196 |

2026-10-11规范编码/签名增量定向读取本机官方.NET 10.0.12公共参考XML（不读取实现）：根`C:/Program Files/dotnet/packs/Microsoft.NETCore.App.Ref/10.0.12/ref/net10.0/`。System.Text.Json.xml核JsonWriterOptions.Encoder/Indented/SkipValidation及Utf8JsonWriter.WriteRawValue(string,bool)，SHA-256=`63342e258274d49ea205580a1f9d526ac41189b8e741314c625a6989cf350bde`；System.Text.Encodings.Web.xml核JavaScriptEncoder.UnsafeRelaxedJsonEscaping，SHA-256=`1e5ab354f4ab73cdfacfe347fadfed7399e7b7733c6b0c35a875b0b1a9486fd9`；System.Security.Cryptography.xml核ECDsa.SignHash(byte[],DSASignatureFormat)/VerifyHash(byte[],byte[],DSASignatureFormat)及IeeeP1363FixedFieldConcatenation，SHA-256=`d5bd5ffbd61e6eb370d89e06721ef3f3029e2e2d75a8e4fcb45db66b1157078d`。只按这些BCL公开能力定协议，不新增第三方依赖/来源代码；实现后仍须对本页向量、非ASCII转义、真实密钥/签名验证，不把公共签名核对当作运行证明。

## 15. 双视角自审与精确外部门

功能/算法视角（2026-10-09）：从多阶段正常接纳、身份冲突、双预约失败、回执丢失、Flush屏障、指标桶边界/单调窗口/重放、Probe过期、通知Gap、自关闭、迟到流写到Stop实际退出逐步走读。修复OperationId错误去重、初始NotPersisted、队列已空等于持久、接纳后取消删除、UTC回拨重分桶、默认JSON把Payload编码成base64、慢回调无限任务及Wait超时归还流等歧义。正文现在只用v0.2声明，Accepted与Persistence、Lifecycle与Health、事件Sequence与NotificationRevision分别计账；没有质量/设备命令和视觉库调用。

陌生宿主接入视角：从无Shell/无数据库/无UI的新Console按§9构造Options与四个端口，先接纳/Flush、查询/流导出、观察Completion再停止；另一个实例使用相同包验证共享Store隔离。修复缺失静态工厂声明、指标历史查重入口、探针来源属性、单epoch快照、订阅读取意图、有限页预算及第二消费者责任。Host owns端口/Stream，Core owns队列/租约/订阅，未真实退出不得释放。示例仍是拟实现调用规格，不冒称C#编译结果。


定向退修两轮反例自审（2026-10-10，均为正文走读，未执行代码）：

1. **第一轮，功能与并发反例。** 以原游标续页却重新授权返回新Access、指标首32项被误当完整趋势、换筛选后旧导出覆盖新范围、授权/BeginExport忽略取消为反例。修正为事件/指标独立续页入口且沿原Access；ExportFilter/ExportId独立绑定并由有限计时器观察真实终态；UiResourcesReleased与Host Stream/Core资源释放分离；未退出Services源仍占槽。公开CreatedAtUtc锚点使Subscribe意图可精确构造，不让Host猜Create时间。
2. **第二轮，陌生Host与异常装配反例。** 从空WPF Host只看签名，发现仅指标名无法选择Kind/Unit测点、Dispatcher先关闭会阻断收尾、发布后的启动异常若返回null会漏掉已活跃实例。修正为传冻结MetricDefinitions/RegistryRevision、明确投影字节预约和完整Options算例、解除先清视觉再无Dispatcher依赖观察源、Create发布前回滚与发布后Faulted/Stop分支分开。已走读双控件共享runtime、迟到Access/Export、半挂接、Host开流失败/未释放流、重复解除及未释放重挂接，责任和恢复落在§7.3/8.5～8.6/DG-A01～03/DG-U01～06。

2026-10-10装配/U1退修结论：当时已检出的模块自身装配、U1公开合同/工程/挂接/有限解除缺口闭合；当时未扩展的§8.3支持包等指导欠账，本轮在§7.4/8.3.2～8.3.4补齐软件协议。真实后端、可信身份审计绑定、白名单/健康定义、客户负载及真实WPF资格仍按§15.1具体Owner处理，不再把尚未执行的验证写成开发者补设计。

§9 Host异常收尾两轮反例自审（2026-10-10，本轮正文走读，未执行代码）：第一轮沿Query、消费、开流、StartExport、Wait、Completion每个抛错点检查，修复正常路径未finally及工作ct取消阻断清理；预登记有界槽先持有runtime/Stream，再发起导出和独立有限Stop，原Stopped持续可观测。第二轮以StartExport调用后无句柄、Completion失败但源未退出、清理预算到期、表满/移交失败、共享Owner仍被另一runtime使用为反例：未借出流可单独关闭，已借出或结果不明仅凭原Completion/Stopped的真实ResourcesReleased归还；确认移交同槽，不另建可能满的表，不在异常后重建实例。原工作异常与清理状态分开，DG-H01～03及六项表同步。主控已完成0.2.2-prep内容复核，接收Host finally、预登记有界Owner槽、未借出及已调用未知Stream、原Stopped真实释放闭包；该接收仅为文档规格，不证明运行释放通过。

| 门 | 依赖它的切片 | 不阻断范围 |
|---|---|---|
| 主控内容接收已完成：C1/C2/C3/S1六项文档规格、A1自有装配、U1控件设计规格 | 接收范围见附录A；实际实现另按明确任务启动 | 本轮仅同步文档，不扩大到真实适配或运行资格 |
| 权威仓库/分支绑定 | 实际代码提交 | 文档准备 |
| 真实Store的耐久/事务/恢复、跨进程身份查证 | A1及生产历史/持久结果 | BCL端口与内存模拟 |
| 可信认证/授权/审计，真实字段白名单及保留合规 | A1及生产查询/订阅/导出 | 测试Gate/白名单 |
| 消费者真实负载/性能目标与健康检查定义/物理阈值 | 对应性能/现场健康资格 | 可测量Core及Probe模拟 |
| §8.5～8.6控件合同/本机成员已定，实际WPF、三语/DPI/UIA/视觉品质待验证 | U1 | 无UI Core/双Console |
| §7.4/8.3.2～8.3.4软件映射已定，源/密钥/生产保留Policy及真实集成证据待绑定 | P1/R1消费Host集成 | NDJSON流与C1～C3 |

定向文档检查（2026-10-09）：代码围栏配对、标题唯一、本页本地Markdown链接、旧版API冲突、唯一Core binding、DG-T01～18覆盖、逐切片六项表和完整Options参数匹配均通过；测试Profile读预约84,008,960bytes（约80.12MiB）≤128MiB。检查只针对本文，不代表全仓一致性或C#编译。

定向退修检查（2026-10-10）：正文/API/Host顺序与六项表同步；14个控件方法、2个只读属性均有对应语义，Core/UI Options示例参数与声明一致，DG-A01～03/DG-U01～06均已绑定；围栏、标题、本地Markdown引用、唯一Core binding、旧缺口声明清除及5个本机XML来源hash检查通过。UI投影预约10,682,368bytes≤16MiB。这里只做文档与定向算例检查，未创建工程或执行C#/真实WPF/性能/现场验证。

本轮Host异常收尾检查（2026-10-10）：§9示例已验证预登记有界生命周期槽、`try/finally`、独立清理取消令牌、原`StopWait`/`Stopped`观察、同槽移交、导出未借出/已借出或结果不明/未排空四分支；DG-H01～03与C1/C3/S1/A1表项同步。该检查仍只验证正文结构和有限示例算例，不证明真实任务、Stream、端口或适配器已运行。

既有接收结论（2026-10-10）保持：C1/C2/C3/S1为ModuleCoreImplementationReady，仅表示依注入端口的六项文档规格已接收；A1自有装配及U1控件设计规格已接收，真实适配IntegrationPending，真实WPF资格未通过。当前完整范围结论见§15.1，整模块不提升为ImplementationSpecificationReady；未执行编译、BCL、WPF、性能、耐久及现场验证。不自动开工。

### 15.1 当前架构全部批准范围的指导准备结论（2026-10-11）

本轮覆盖完整诊断能力及其宿主消费链，复用2026-10-09～10有效研究/自审与既有Core、装配、U1接收。新增内容只有：§3.1.1规范编码、§3.2离线容量建议、§5三语错误/恢复、§7.4真实适配映射、§8.3.1向量、§8.3.2～4支持包/下载/保留和DG-I01～08。P1/R1是本页已有集成责任的任务名，未新增独立模块、公共Core API、UI页面、工程或外部服务范围。

| 完整批准能力 | 当前唯一实施位置/软件结论 | 尚待事项及Owner |
|---|---|---|
| 日志、trace/span、关联、结构编码/敏感字段 | §3.0～3.2/3.1.1/4.2/8.3.1；规范输入/字节/去重可执行 | diagnostics Owner实施编码与Golden；消费Host/安全Owner提供真实白名单，不向开发者转交字段敏感性判断 |
| 背压、指标、快照、通知、排空/资源 | §3.2/4～8.2/9；既有规格复用，A1补提交成员快照 | diagnostics Owner实施/针对性验证；真实Store提交与排空证据由storage适配Owner提供 |
| 错误/报警独立性 | §1.2/5；仅只读日志投影，三语错误及恢复固定 | IM-068 alarms持发生/人工处理事实；设备/质量Owner持条件/动作/处置；无diagnostics设计欠账 |
| 健康与恢复 | §4.3/7.4/9/10；过期Unknown、原身份回查及Host原槽收尾已定；健康历史由受信Host按同源/epoch快照重算 | Host/探针来源Owner提供检查定义/物理阈值；diagnostics不新增Readiness判定或公开健康历史业务接口 |
| A1真实Store/读取Gate | §7.4；注册、逻辑记录、提交代际、幂等、审计、撤权和恢复协议已定 | diagnostics适配Owner实施Owner codec/注册StatementCatalog及迁移；storage Owner提供当前可信StoreRef/后端耐久/恢复配置；authorization/认证Owner提供当前权威身份/策略，消费Host绑定生产路由/审计路径。实际声明/实现/证据未完成，IntegrationPending |
| P1支持包/签名/原子发布 | §8.3.2；精确格式、限额、签名、两阶段封口/发布、回查已定 | 消费Host实现编排与源resolver绑定；源Owner提供原版本/证据；安全Owner提供P-256 KeyId/epoch/可信公钥及密钥使用策略；storage Owner提供SealedDurable/对象引用服务。无凭证不能签生产包，但不阻断Core |
| P1下载/续传 | §8.3.3；单pendingRange、连续确认/当前核权/许可CAS已定 | 产品transport Owner绑定真实端点/客户端确认协议并验证；网络/接收端落盘不由diagnostics编造，协议确认不等于落盘耐久 |
| R1保留/保护/清理 | §8.3.4；预览、逐步重验、同事务引用、去重语义/未知零删除已定 | 客户/安全/运维Owner提供真实期限/法律保持/调查授权；diagnostics Owner实施自身retire/resolver；storage Owner实施隔离/物理GC及其它Owner保护合并。未知源保持零删除 |
| U1紧凑查询/指标工作台/三语 | §8.4～8.6/5；复用控件合同/本机接线/有限解除，错误文案补齐 | diagnostics Owner实施控件并做真实1920×1080、三语/键盘/UIA/DPI/视觉与性能验证；Host提供当前Access/主题/语言；未执行不写通过 |
| 参数建议/性能/发布回退 | §3.2/12/13；离线容量式、显式冻结/测点/回退已定 | 消费Profile Owner提供真实负载/P95等目标及现场验收值；diagnostics Owner测量并报告NotEvaluated/失败，不静默自动调参 |

**准备结论：当前架构批准范围内，可由本模块决定的软件指导欠账已闭合；不再把P1/R1协议或A1恢复映射笼统留给Host猜。** 余项是表内具体实现、生产来源/Profile/密钥/客户事实绑定及尚未执行的验证，不以“总控待内容审核”重复阻断。永久原会话负责本模块执行、自审与返修，总控只接收状态/跨Owner依赖；本轮不发消息给其它会话，不写共享调度文件。

本轮两轮有限自审：①功能/并发反例覆盖快照打开后低Sequence迟提交、载荷retire后旧身份重试、撤权/交付两个线性化方向、签名随机性、发布响应丢失、range重复确认及保护新增/GC竞争；结论分别固化为G成员快照、Unknown/NoPendingAttempt=false、当前权威交付预约、重放原包、原identity回查、连续CAS和同协调零删除。②陌生Host只看已声明端口走装配/来源读取/下载/退出，发现ExportReceipt不带source metadata，明确从本Host原Gate耐久SourceBound读取而非猜字段；production Read/NotRequired不代替本模块Seal审计；源任务/TTL/Stream/Owner仍依§9真实释放。未增未声明Core调用，未运行C#。

本轮实际文档检查：围栏配对、标题唯一、本地Markdown引用5处、18项三语错误资源、DG-I01～08及新增节/既有binding同步通过；从正文两项JSON向量复算640/949bytes及SHA-256通过。这里的向量复算是内存Python字节检查，不是.NET encoder/Golden运行；本机.NET公共XML只核签名/说明，未运行签名或序列化。新规则与状态链已按上述两轮有限反例走读，未重新全审已接收Core或其它模块。既有C1/C2/C3/S1准入保持；A1/P1/R1生产集成和U1运行资格仍未取得，整模块未达ImplementationSpecificationReady；全仓索引、C#、真实provider/WPF、性能、HIL及现场不在本轮验证范围。

## 附录 A：Module API Contract v0.2 与逐切片六项结论

唯一Core契约是§3～7；唯一WPF控件扩展契约是§8.5～8.6（独立namespace，直接消费Core DTO）；§8其它部分及§9～12解释同一声明，不重复接口。平台C-01～C-08、客户阈值、领域Schema及正式事实Owner只作未来映射。第13节包名不是第二namespace；未声明入口须先修订本页。HALCON/AsunImage对本模块不适用，真实Backend或WPF签名仅阻断对应适配。

下表六项严格对应[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，按主控2026-10-10对0.2.2-prep的内容复核同步**文档规格接收结论**，不代表执行验证。C1/C2/C3/S1为依注入端口的ModuleCoreImplementationReady；A1仅自有装配规格、U1仅可选控件设计规格接收，均不扩大为真实适配或WPF资格。C2/C3依赖C1，S1覆盖各切片的相应case，不猜造产品能力。

| 切片 | ①职责/第二消费者 | ②唯一API/语义 | ③无UI/注入 | ④场景断言 | ⑤测量/目标来源 | ⑥工程/范围/顺序 | 当前结论 |
|---|---|---|---|---|---|---|---|
| C1 事件/队列/回执/Flush/Stop | §1/2；双Host | §3～7；EventId/状态/所有权 | §7端口，BCL | §10、T01～07/17/18、H01～03 | §3.2/12；目标待Profile | §9 finally/原Stopped及binding | ModuleCoreImplementationReady；六项文档规格已接收，依注入端口；未执行验证 |
| C2 指标/健康 | §1/4.3；长稳Host | SampleId/定义/窗口/Probe | 同Store/Time/Probe | T08～10/17/18 | 窗口/series预算及§12 | 依C1，同工程/§9 | ModuleCoreImplementationReady；六项文档规格已接收，依注入端口；未执行验证 |
| C3 快照查询/读取门/流/订阅 | §1/8；维护/服务 | §3～8；cursor/Gate/lease | Store/Gate/Stream注入 | T11～15/17/18、H02 | 读预算/截止与§12 | 依C1，§9未借出/已借出Owner分支及binding | ModuleCoreImplementationReady；六项文档规格已接收，依注入端口；未执行验证 |
| S1 BCL夹具/双Host | §9两独立消费者 | 消费同v0.2，不扩端口 | 四种test fixture+有界Host槽 | 全部适用T01～18/H01～03 | 固定Time/资源/§12 | 唯一Exe测试工程；同槽移交 | ModuleCoreImplementationReady；六项文档规格已接收，依注入端口；未执行BCL测试 |
| A1 模块装配/真实Store与ReadGate接入 | §1/7.3；两个Host | §4.1/7.1/7.3工厂及注入链已定 | 唯一Core内装配、端口借入 | A01～03/H01～03；真实故障另门 | §12方法已定，真实耐久/Profile待绑定 | §7.3/9异常退出及Core binding | 仅本模块自有装配及Host退出规格已接收；真实后端/可信权限审计IntegrationPending；未执行耐久验证 |
| U1 可选WPF投影 | §8.4～8.6；双Window Host | §8.5公开合同/§8.6本机XML接线已定 | 独立Wpf库借入Core/Services，无产品依赖 | U01～06，未执行 | §8.5投影预算/§12方法，目标待Profile | §8.6唯一WPF/测试工程及挂接/解除顺序 | 可选控件合同/工程挂接/有限解除设计规格已接收；不是无UI Core；真实WPF/性能/现场资格未通过 |

六项规格接收与代码测试通过分别记，不将S1夹具通过视为A1耐久/撤权或U1真实WPF通过。§7.4/8.3.2～4的A1/P1/R1完整范围软件指导已在原会话补齐；它们保持生产绑定/实际实现及运行验证门，不据此授新增切片ModuleCoreImplementationReady，也不缩小总体职责宣称整模块完成。


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

## Core implementation binding

- 准入路径：NewProjectRequired；唯一Core：`src/Modules/diagnostics/Asun.Modules.Diagnostics.Core/Asun.Modules.Diagnostics.Core.csproj`；namespace `Asun.Modules.Diagnostics`。
- 唯一测试：`tests/Modules/diagnostics/Asun.Modules.Diagnostics.Core.Tests/Asun.Modules.Diagnostics.Core.Tests.csproj`；Microsoft.NET.Sdk、net10.0、OutputType=Exe，仅ProjectReference受测Core与.NET BCL，**沿用 DEV-GOV-010 §3.1 的 BCL Exe 约定**（原措辞"沿用现存 `tests/Asun.Simulation.Core.Smoke/` 约定"已于 2026-10-28 审核更正：该工程已随 `c4e10cf` 移除，不再存在，约定来源改为治理标准本身）。两工程尚未创建，本轮不创建。
- 获准Core切片允许路径仅这两个目录；禁止其它模块、产品Shell/Domain/Integration、asunimage内部、只读来源/快照、用户配置/正式测试和共享文档。A1自身装配在Core，真实后端实现另按已批准合同与工程接入；U1只能在§8.6唯一WPF/测试两目录获准后开工，不能在Core偷偷引用WPF。本文修订允许路径始终只有本指导，不授权创建这些工程。
- 最小顺序：创建工程→值/Options校验→端口夹具→接纳/队列/逐项回执→Flush/Stop→C2→C3→双Host；每片先执行绑定case再扩大，依赖未接收不猜造。

```text
dotnet build src/Modules/diagnostics/Asun.Modules.Diagnostics.Core/Asun.Modules.Diagnostics.Core.csproj -c Release
dotnet run --project tests/Modules/diagnostics/Asun.Modules.Diagnostics.Core.Tests/Asun.Modules.Diagnostics.Core.Tests.csproj -c Release
```

测试进程内每case最多10s，全suite120s；入口列明实际case ID及失败/必需跳过/未完成，任一非通过返回非零。外层执行器180s截止，超时返回失败并保存未退出/资源持有状态，必要终止测试进程仅为测试隔离，不算模块排空。固定闩锁最终在finally释放并观察源任务；不会无限await Completion。`dotnet test`对Exe空执行不作为验证。性能另按§12已采纳Profile，真实WPF/持久/现场另门。

当前C1/C2/C3/S1为ModuleCoreImplementationReady（仅已接收的文档规格，依本文注入端口）；A1自有装配及Host退出规格保持接收，§7.4补真实适配软件映射，实际生产绑定/耐久仍IntegrationPending。U1按§8.6独立WPF/测试工程的控件设计规格接收，不属于本无UI Core绑定；P1/R1为§8.3 Host消费集成，不沿本binding创建Core产品接口或空工程。全范围准备结论见§15.1。唯一工程尚未创建，编译/BCL/WPF/性能/耐久/现场均未执行；本绑定不是运行或生产资格声明，不提升整模块为ImplementationSpecificationReady，不自动创建工程或启动代码。
