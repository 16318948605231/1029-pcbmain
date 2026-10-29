# 通用设备信号与 I/O 独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, C3`

- 模块：`IM-041`；来源：`PKG-058`
- 中文名称：通用设备信号与 I/O
- 文档版本：`0.2.1-prep`
- 文档状态：`DesignReview / Prep`
- 切片准入：C1/C2/C3=`ModuleCoreImplementationReady`（既有规格接收保持）；W1 确定指导保持，`PreparationIncomplete / NotReady`（真实 WPF 资格及受影响平台接入门未关闭）；A1 通用软件适配契约已在永久原会话完成定向内容审核，内部设计闭合，真实型号接入/平台绑定与资格仍 `PreparationIncomplete / NotReady`。整模块仍为准备阶段，未实现或生产验收。
- 适用基线：C# / .NET 10；核心可脱离 UI 运行；设备适配器按现场协议单独交付
- 规划消费者：触发观察、DI/DO/AI/AO、计数/锁存和独立维护工具
- 本页是本模块唯一实施指导。这里区分两层：`Module API` 是本模块程序集内部/模块消费者使用的代码形状，可在本页冻结并独立编码；平台产品的 Contract/Schema/State/Owner 序列化、业务绑定和设备 Profile 仍须由主项目串行采纳。Module API 冻结不等于平台 Contract 获批、设备接入或生产验证。

## 1. 目标和边界

### 1.1 能力职责

模块把一个或多个物理设备的信号能力暴露为可替换、可测试的强类型端口：

1. 发现并发布设备能力、连接代、逻辑信号到物理通道的映射版本。
2. 读取或订阅数字输入（DI）、数字输出（DO）、模拟输入（AI）、模拟输出（AO）以及设备支持的计数和锁存观察。
3. 保留原始值、工程值、单位、质量、原因、采样时刻、接收时刻、时间域、序号和连接代。
4. 在权限、运行模式、映射版本、期限和设备能力均满足时提交受控写入或脉冲请求，并返回可判定的实际结果。
5. 在断线、重连、映射更新、回绕、缓冲溢出、取消和关闭时保持事实可追溯，不把未知转换为安全或质量结论。
6. 通过诊断端口提供延迟、积压、事件缺口、异常和资源排空观测。

### 1.2 明确禁止

核心不得包含以下事实或行为：

- PCB、PCBA、SPI、AOI、点胶、涂覆、钻孔、来料、板流或其它制程判定；
- 到板、夹紧、读码、PASS/FAIL、返修、放行、工单或目标关联的业务解释；
- 运动轴位置、相机/光源/结构光采集编排，或 MES/Hermes/客户协议；
- 急停、安全继电器、安全 PLC 的实现、旁路或软件替代；
- 由 UI、ViewModel、数据库、报告或日志成为第二事实写入者；
- 隐式发现设备、全局单例连接、硬编码地址、自动重放旧输出、自动复位物理输出；
- 以轮询的“当前值”伪造同一时刻的多通道一致采样；
- 未确认的厂商 SDK 方法、原子性、锁存、脉冲精度或实时保证。

调用方负责流程顺序、目标/尝试关联、工艺解释、质量判定、放行、人机权限政策以及任何设备副作用策略。安全链由硬件安全体系和设备 Owner 管理；本模块最多镜像状态并报告限制。

### 1.3 依赖方向

```text
应用/维护工具/采集编排
        ↓ 公开候选 Contract
DeviceSignals.Core（本模块）
        ↓ 端口
IDeviceSignalAdapter / IDeviceSignalLease（厂商或模拟适配器）
        ↓
PLC、IO 卡、控制器或回放文件
```

模块可依赖配置、诊断、授权和公共取消/时间抽象；不得反向引用产品页面、私有数据库表、Motion/Camera 私有类型或 AsunImage 内部。视觉算法不适用于信号协议；Core 不调用 HALCON/AsunImage，具体 Adapter 的 HALCON 26.05/cv2 备用路线见 §16。若上层将信号与影像关联，由上层保存各自的证据和时钟域。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.DeviceSignals.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.DeviceSignals.Wpf` 可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1.3 依赖图已明确 Core 只依赖端口/适配器，不依赖 WPF；C1/C2/C3 最小测试宿主（无 WPF/SDK）直接验证这条门禁。

**Blazor/Web 宿主中的信号监控**：Web 端需要"实时展示 DI/DO/AI/AO 值、质量、时间域与通道映射版本"时，服务端通过 `integration-transport` 的 OPC UA Pub/Sub 或 SignalR Hub 推送本模块的信号快照。约束：
- 浏览器端只渲染数值与质量标记，**不直接写 DO/AO 输出**；写信号必须经已授权的维护接口（带权限令牌和运行模式检查），不经浏览器
- §1.2 已明确"以轮询的当前值伪造同一时刻的多通道一致采样"是禁止行为——Web 端展示的多通道值是**各自的最新快照**，不是同一采样时刻；前端需要明确标注时间戳，不得以"同屏显示"暗示一致采样
- §1.2 已明确"未确认的厂商 SDK 原子性或锁存精度"是禁止行为——Web 端不得以"看起来同时"解释为硬件原子操作
- 信号历史（缓冲窗口内）通过 gRPC/REST 查询，不通过 SignalR 传输全部历史缓冲

**AI 推理 Tiling 适配**：设备信号（DI/DO/AI/AO）是 AI 推理的**辅助上下文**而不是图像输入。适配约束：
- 本模块提供"当前设备状态快照"给宿主编排层，由宿主决定是否把信号条件附加到 AI 推理请求的 `RequestContext`
- 三态仲裁（`ai-inference` §1A）中的 `AutoResolved` 自动判定**不触发 DO 输出**（§1.2 已明确禁止）；DO 输出必须经宿主策略明确授权
- 本模块不持有推理 tile 租约，也不参与分块编排

**HALCON 备选策略**：§1.3 依赖图已明确"Core 不调用 HALCON/AsunImage"；具体 Adapter 的 HALCON cv2 备用路线见 §16（仅在厂商 SDK 能力存在缺口且需要视觉辅助时使用）。HALCON 备选双跑 CI 不涉及本模块核心。

## 2. 角色、Owner 和事实

| 角色 | 责任 | 不得做的事 |
|---|---|---|
| 设备适配器 Owner | 独占物理连接、协议读写、原始回执、驱动回调和排空 | 不解释制程、不直接通知 UI 写入 |
| DeviceSignals Core | 校验契约、映射/代隔离、值换算、质量和状态传播、请求生命周期 | 不拥有设备安全链或业务流程 |
| 应用/编排 Owner | 组合读数、触发、尝试/目标关联、重试政策和业务判定 | 不绕过 Core 直接写适配器 |
| 授权/模式 Owner | 提供不可伪造的能力、角色、维护模式、期限和审计上下文 | 不因 UI 可见就授予写权 |
| UI/报告投影 | 显示能力、设定/回读差异、质量/年龄/原因和命令状态 | 不成为事实写入者、不隐藏 Unknown |

同一物理连接只有一个写入 Owner。允许多个只读订阅者，但每个订阅者都必须使用不可变观察快照。若 Motion、Lighting 或采集 Owner 已持有控制器会话，本模块通过注入的共享端口接入，不再创建第二个连接或第二个写锁。

### 2.1 DZ-XVision 现场信号样例与迁移边界

只读快照显示一台已运行设备把控制卡 I/O 用于上下轨传感器、板流握手、门/气压/急停状态、启动/复位输入、检测触发事件、挡板/气缸、OK/NG、塔灯和蜂鸣器。此处只采纳“现场存在这些信号类别、需要映射/极性/回读/连接生命周期”的事实；不采纳旧软件中的轨道状态机、报警即停策略、检测判定或默认通道号为平台规则。

来源及可复核位置：

| 快照文件 | 直接观察到的内容 | 来源 SHA-256（见快照 manifest） |
|---|---|---|
| `DZ-XVision/MotionParams.ini` | `[Motion]` 中 DI/DO 逻辑名到通道号、`-1` 未配置值、逐通道 `INIOInvert`/`OUTIOInvert`、门/气压检测开关；这是该快照的一份具体配置，不是通用默认值 | `a47e470a4c9e6531c17f6cd0ad813cd00c7dc94c9fce675901583e2a5adae49c` |
| `Motion9014/Motion9014.cs` | DI、DO 读回数组；读取后应用极性归一化；`set_io_do_bit` 写物理输出；I/O 周期线程、通道映射和上/下轨事件 | `12c427093c375b8d1229e1469449399a6162bdb2e64e31c08b38eb2a7ddb83c5` |
| `DZ-XVision/DZXVision.cs` | I/O 显示、上下轨传感异常提示，以及运动侧 `BoardGrab(index)` 到采图/检测编排的事件桥接 | `b64d236457eeb8aa821376861288a5d061d3367afb403021a74ef543459d0ca1` |
| `DZ-XVision/DZXVisionConfig.cs` | 维护页显示 DI/DO 映射和当前回读；UI 是观察投影，不是 I/O Owner | `16269dd329e0760a305d8661d5b26a85777f65a49ec9f3138cc6e73f53c6b465` |

可迁移抽象和平台映射要求：

| 观察到的现场类别 | 公开类型/映射要求 | 处理、输出和状态规则 | 恢复及验收断言 |
|---|---|---|---|
| DI：传感器、上下轨光电、到位/减速、启动/复位、门、气压、急停输入 | 每个逻辑信号使用 `SignalDescriptor` + `DigitalValue`；映射快照记录方向、通道、有效电平/极性、配置来源和 `MappingRevision`。如 `-1` 未配置只能在 Adapter Profile 转为 `Unsupported`，不得读通道 0 作为默认 | 适配器先读取原始位，再按映射的有效电平产生逻辑位；同一观察同时保留原始位、归一值、质量、采样/接收时间及连接/映射代。断线/读取失败使旧值 `Stale/Unknown`，不合并成 `false` | 配置缺失、重复/越界地址、极性缺失时上线前拒绝或标为不可用；模拟测试逐一翻转原始位，断线后验证旧 `true` 不再是当前值，重连必须取得新代观察 |
| DO：输送握手“要板/有板”、挡板/气缸命令、OK/NG 输出、塔灯/蜂鸣器 | DO 仍只是有类型的逻辑输出名；“要板/OK/红灯”等名称来自应用 Profile，不能让 Core 赋予流程/质量含义。输出设定、协议 ACK、端子回读、外部机构传感器必须是不同事实 | 校验授权、模式、映射/连接代、有效期和能力后才发送；端子回读独立产生 `SignalObservation`。ACK 只能是 `Acknowledged`；端子值只能证明输出通道读回，不证明气缸/挡板/灯具或板件已达预期物理状态，物理到位需独立 DI | 映射冲突或回读不符进入 `Failed/Unknown/Degraded` 并保留逐项结果，不自动切换通道或重复命令。断言：DO 已写但无回读不返回 `Applied`；回读成功也不伪造外部机构完成 |
| 输送/门禁/安全相关信号 | Core 只返回原始或归一化 DI/DO 事实、时间和质量；安全输入可标注来源类别，但不得暴露 `SafeToRun`、`DoorPermit`、`EmergencyStopCleared` 等软件放行结论 | 业务状态机、输送时序、传感器组合解释、异常停机策略和安全 PLC/硬件链由其外部 Owner 完成。`Good=true` 仅表示本次电信号观察有效，不代表安全许可 | 门/急停/气压状态 Unknown、Stale、断线或配置错误时不得被模块转换成许可；契约测试断言模块只输出信号事实，不发送运动/输送/复位或安全旁路命令 |
| 触发/到位后采集 | 通过 DI/边沿/锁存观察携带来源序号、设备 tick/时钟域和连接代；采集 Owner 把观察关联到采集尝试并决定何时采图 | DZ-XVision 中运动事件回调进入 `BoardGrab(index)` 后才由应用进行拍照任务选择、光源/曝光设置和取图。可迁移的是“信号事实与采集编排分层”，不是 BoardGrab 或产品位置语义进入 Core | 缺边沿、重复边沿、旧代迟到、时间域不匹配均作为诊断/质量事实交给采集 Owner；回放断言事件不丢序、不重复伪造采集、Core 不启动相机 |

旧项目的线程轮询间隔、数组索引、INI 通道号、`isdoorI`/`isAirI` 开关、极性默认值及“两个传感器同时有效”的报警条件均为该机器的 Profile/实现细节，不能照搬为模块默认参数。此现场快照验证了 DI/DO 的需求类型和端子回读的重要性，不证明通用软件可替代输送 PLC、安全 PLC、硬件互锁或实际设备验收。

### 2.2 共享物理连接的单一写 Owner 和通道租约

Motion、DeepSight/采集和 DeviceSignals 即使分别使用不同逻辑信号，只要底层是同一张控制卡、PLC 会话、串口或 TCP 连接，就必须由宿主组合根或已批准的设备连接 Owner 创建唯一物理会话。该 Owner 独占连接打开/关闭、重连、连接代、协议序号、底层互斥/写队列、最终排空和未决副作用对账。Signals Core 只通过注入的 `typed sub-port`/通道租约读取其批准通道；若获准写 DO/AO，也只能经共享 Owner 的统一仲裁队列，不创建独立锁来假装连接互斥。

接入顺序固定为：

1. 组合根从唯一连接 Owner 获取当前连接代和共享端口；采纳的 Profile 提供逻辑信号映射、读写权限、有效电平/量程、通道租约范围及修订号。
2. Owner 校验设备身份/能力，并检查所有活跃租约。相同物理输出被两个写 Owner 声明、同一资源存在不兼容协议/极性/地址配置，或租约越权时，拒绝接入并返回 `ResourceBusy`/`MappingMismatch`；不得以模块内锁、最后写入者胜出或启动第二条连接解决。
3. Owner 按设备协议序列化所有消费者的读写；每一命令、回读和回调标记唯一连接代、映射代、请求 ID/序号。逻辑信号别名只允许在 Profile 显式声明且无竞争写 Owner 时使用。
4. 某消费者关闭或映射升级时先停止其新请求，撤销其订阅，结清或查询其未知请求，再排空该租约。正常关闭只在最后租约归还后；故障恢复由连接 Owner 先全局失效旧代、停止所有发送并等待真实排空，再按 Profile 决定重连，不要求消费者先自愿退出；任何消费者不能关闭共享句柄或把别的租约的请求判为完成。
5. 连接代变化使所有旧租约失效；重新发现能力并重新授予租约前，读值标 `Stale`、未决写保持 `Unknown`，禁止旧输出自动重放。

可判定验收：模拟两个消费者并发连接/写/退订；底层 open 次数始终为 1；并发命令由唯一 Owner 序列化，租约冲突在发送前拒绝；取消一个消费者不关闭另一个租约；断线时连接代递增、旧事件不能进入新代；最后租约排空前不释放句柄；排空超时保留 Owner 和未决资源并返回 `DrainTimeout`。Motion 运动命令、DeepSight 采集触发/相机状态与 Signals 通道租约仍由各自 Owner 管理，Signals 不夺取其设备状态机或对同一物理资源开第二写通道。

## 3. Module API Contract v0.2：值、映射与观察

本节至 §7 是唯一类型声明位置；§9 只调用，不再复制接口。以下 C# 块是公开声明规格（省略方法实现，不声称该块可直接编译）。实现时统一为 public，命名空间 `Asun.Modules.DeviceSignals`，使用 net10.0 BCL 的 `System.Collections.Immutable`、`System.Numerics`、`TimeProvider`。平台序列化及 State/Owner 整数编码另由平台采纳；这些编码不反向改变本页 Module API。所有 DTO 的集合使用 `ImmutableArray<T>`；禁止 `default(ImmutableArray<T>)`、null 元素、可变集合穿透和 `Dictionary<string, object>`。构造不做 I/O；入口校验无效 DTO 并返回字段错误。

### 3.1 身份、值和错误

ID 使用区分大小写的 ordinal 字符串，不作 Trim、大小写归并或文化转换；null、空白、控制字符拒绝。首片不臆造客户长度限制，运行态再按宿主显式 UTF-8 字节预算拒绝。稳定错误按字段路径 ordinal 排序，再按 Code 排序；相同输入的输出顺序相同。

```csharp
public enum SignalKind { DigitalInput, DigitalOutput, AnalogInput, AnalogOutput, Counter, Latch }
public enum SignalDirection { Input, Output }
public enum ValueQuality { Good, Stale, Invalid, Filtered, Degraded, Overflow, Discontinuous, Unknown }
public enum ConnectionState { Offline, Connecting, Online, Degraded, Draining, DrainUnknown, Closed }
public enum ResourceState { Active, Draining, DrainUnknown, Released }
public enum OperationState { Validating, Queued, Executing, Observed, Completed,
    Rejected, Failed, Cancelled, TimedOut, Unknown }
public enum CommandOutcome { NotSent, Rejected, Sent, Acknowledged, Applied,
    NotApplied, Failed, NotExecuted, Unknown }
public enum ErrorCode { None, InvalidArgument, Unsupported, MappingMismatch,
    CapabilityMismatch, PermissionDenied, ModeDenied, NotConnected, StaleObservation,
    TimeDomainMismatch, DeadlineExceeded, Cancelled, Busy, QueueFull, ProtocolError,
    DeviceFault, PartialFailure, Overflow, Discontinuous, ResourceBusy, DrainTimeout,
    Disposed, UnknownOutcome, PersistenceUnavailable, IdempotencyConflict, PrecisionLoss }
public enum IssueCode { Required, InvalidId, DuplicateId, InvalidAddress, AddressConflict,
    RevisionMismatch, KindMismatch, DirectionMismatch, CapabilityConflict, InvalidRange,
    InvalidUnit, InvalidTransform, ValueTypeMismatch, OutOfRange, NonFinite,
    BitWidthMismatch, PrecisionLoss, ResolutionMismatch, Unsupported, InvalidFilter }

public sealed record MappingValidationIssue(IssueCode Code, string Path, string MessageKey);
public sealed record SignalError(ErrorCode Code, string ReasonCode, string FieldPath,
    string MessageKey, string? VendorCode, bool MayHaveSideEffect, string DiagnosticId);
public abstract record RawSignalValue;
public sealed record RawDigital(bool High) : RawSignalValue;
public sealed record RawSigned(long Value, int BitWidth) : RawSignalValue;
public sealed record RawUnsigned(ulong Value, int BitWidth) : RawSignalValue;
public sealed record RawFloating(double Value) : RawSignalValue;
public sealed record RawCounter(ulong Value, int BitWidth) : RawSignalValue;
public sealed record RawLatch(bool Latched, string SourceId, ulong? CaptureId) : RawSignalValue;
public abstract record SignalValue;
public sealed record DigitalValue(bool Value) : SignalValue;
public sealed record AnalogValue(double Value, string Unit) : SignalValue;
public sealed record CounterValue(ulong Value, int BitWidth) : SignalValue;
public sealed record LatchValue(bool Latched, string SourceId, ulong? CaptureId) : SignalValue;
```

`SignalValue` 是工程值，`RawSignalValue` 是原始证据；两者不能混用。Counter 不经 double，64 位整数不得损失精度。未知/失败观察的 raw 可以缺失，工程值也必须缺失；缺失不是 0 或 false。库按稳定 MessageKey 返回错误，宿主翻译并格式化；厂商原码不翻译、不执行为命令。

### 3.2 强类型映射和参数来源

```csharp
public enum Polarity { ActiveHigh, ActiveLow }
public enum QuantizationMode { Exact, NearestToEven }
public sealed record ChannelAddress(string Bus, string Address, int? SubChannel,
    string AddressFormatVersion);
public abstract record SignalSpec;
public sealed record DigitalSpec(Polarity Polarity) : SignalSpec;
public abstract record AnalogRawFormat;
public sealed record SignedAnalogFormat(int BitWidth, long Min, long Max) : AnalogRawFormat;
public sealed record UnsignedAnalogFormat(int BitWidth, ulong Min, ulong Max) : AnalogRawFormat;
public sealed record FloatingAnalogFormat(double Min, double Max) : AnalogRawFormat;
public sealed record AnalogSpec(AnalogRawFormat RawFormat, double Scale, double Offset,
    string Unit, double EngineeringMin, double EngineeringMax, double Resolution,
    double ResolutionOrigin, QuantizationMode WriteQuantization,
    double WriteGridTolerance, string CalibrationReference) : SignalSpec;
public sealed record CounterSpec(int BitWidth, string ResetEpochSource,
    bool HasResetEpoch, bool HasHardwareSequence) : SignalSpec;
public sealed record LatchSpec(string SourceId, bool HasCaptureId, bool CanClear) : SignalSpec;
public enum FilterKind { None, DigitalStableWindow, AnalogHysteresis }
public sealed record FilterSpec(FilterKind Kind, TimeSpan Window,
    double? Lower, double? Upper, string Revision, string SourceReference);
public sealed record SignalDescriptor(string SignalId, string DisplayNameKey,
    SignalKind Kind, SignalDirection Direction, ChannelAddress Address,
    bool CanRead, bool CanWrite, bool CanSubscribe, bool CanPulse,
    SignalSpec Spec, FilterSpec Filter, string MappingRevision,
    string CapabilityRevision, string SourceReference, string? ReadAliasGroup);
public sealed record MappingSnapshot(string Revision, string CapabilityRevision,
    ImmutableArray<SignalDescriptor> Signals);
public sealed record DeviceIdentity(string DeviceId, string Vendor, string Model,
    string Firmware, string AdapterId, string AdapterVersion);
public enum SamplingMode { Sequential, DeviceSnapshot }
public enum EdgeSource { None, HardwareEvent, PollingDifference }
public enum CommandQueryScope { None, Connection, DevicePersistent }
public sealed record ClockDescriptor(string DomainId, long TicksPerSecond,
    int? CounterBitWidth, TimeSpan? ErrorBound, string EvidenceReference);
public sealed record SignalRuntimeCapability(string SignalId, EdgeSource EdgeSource,
    bool TerminalReadback, bool CorrelatedApplicationReceipt,
    bool HardwarePulse, TimeSpan? MinPulseWidth, TimeSpan? MaxPulseWidth,
    CommandQueryScope QueryScope, string EvidenceReference);
public sealed record DeviceCapabilities(DeviceIdentity Identity, ConnectionState State,
    string ConnectionGeneration, string CapabilityRevision, string MappingRevision,
    SamplingMode SamplingMode, ImmutableArray<ClockDescriptor> Clocks,
    ImmutableArray<SignalRuntimeCapability> Signals, bool Simulation);
```

映射校验按以下顺序闭合，不能靠上线失败来补规则：

1. Mapping/Capability 修订非空，逐项修订完全相同；SignalId 唯一。DI/AI/Counter/Latch 是 Input，DO/AO 是 Output。Input 禁止 CanWrite/CanPulse；Pulse 只对 CanWrite 的 DO；CanSubscribe 要求 CanRead。
2. 地址三个字符串有效，SubChannel 若给出须 >=0。通用 Core 只核结构，不推断厂商数字地址范围/字节序；具体 AddressFormatVersion 的解析、界限、canonical 地址由 Adapter Profile 负责。重复三元地址只允许显式相同 ReadAliasGroup 的只读别名，且 Kind/Spec/Filter/修订一致；任何输出重复、读写别名或不同极性冲突都拒绝。
3. Spec 必须与 Kind 对应；极性无默认。Digital 的原始 High 按 ActiveHigh 原样、ActiveLow 取反产生逻辑值，输出反向同一规则。Counter 位宽仅 8/16/32/64；不声明清零 API。Latch SourceId 必填，CanClear 仅能力事实，本模块没有隐式/通用 clear 命令。
4. Signed/UnsignedAnalogFormat 位宽 8/16/32/64，raw min/max 在该类型可表示范围且 min<=max；FloatingAnalogFormat 边界有限且 min<=max。Scale 有限且 !=0（允许负斜率），Offset 有限；工程边界有限且 min<=max，Resolution 有限且 >0，Origin 有限；WriteGridTolerance 有限、>=0 且 < Resolution/2。单位是精确 ordinal 标识，不自动换算 V/mV；CalibrationReference/SourceReference 必填，来源不得由 Core 编造。
5. raw 两端换算均必须有限；换算域与工程有效域至少相交，不能要求 raw 全量程都有效而掩盖保留/故障码。工程有效域更窄时，域外保留 raw 且产生 OutOfRange；绝不夹紧。
6. Filter None 要求 Window=0、Lower/Upper=null；DigitalStableWindow 仅 DI/DO，Window>0 且上下阈值为空；AnalogHysteresis 仅 AI/AO，Window=0，Lower/Upper 有限、Lower<Upper 且在工程有效域。窗口和阈值都由 Profile 显式给出，SourceReference/Revision 必填。
7. 不在线能力由能力列表缺项表达；未配置地址在配置导入端变成未绑定项并报错，不构造“地址 -1 等于通道 0”。能力是否支持必须由实际能力发现匹配，首片纯校验不虚构 Supported。

### 3.3 纯 Core 精确入口

```csharp
public sealed record MappingValidationResult(bool IsValid,
    ImmutableArray<MappingValidationIssue> Issues);
public sealed record SignalValueValidationResult(bool IsValid, SignalValue? Value,
    ImmutableArray<MappingValidationIssue> Issues);
public sealed record EngineeringConversionResult(bool IsValid,
    SignalValue? EngineeringValue, ValueQuality Quality,
    ImmutableArray<MappingValidationIssue> Issues);
public sealed record RawEncodingResult(bool IsValid, RawSignalValue? RawValue,
    SignalValue? EffectiveValue, ImmutableArray<MappingValidationIssue> Issues);
public static class DeviceSignalsModule
{
    public static MappingValidationResult ValidateMapping(MappingSnapshot mapping);
    public static SignalValueValidationResult ValidateValue(
        SignalDescriptor descriptor, SignalValue value);
    public static EngineeringConversionResult ConvertEngineeringValue(
        SignalDescriptor descriptor, RawSignalValue rawValue);
    public static RawEncodingResult EncodeOutput(
        SignalDescriptor descriptor, SignalValue value);
}
```

输入参数 null 或非法枚举值也作为结构化 Required/KindMismatch 返回；不靠异常表示字段错误。ValidateValue 先校验该 descriptor 的局部完整性，再匹配工程类型/单位/有效域；不因 CanWrite=false 拒绝读取的值，输出权限由 EncodeOutput 额外检查。纯函数无线程、I/O、时钟、Store、环境变量、缓存或全局可变状态；结果不持有调用方可变对象。

模拟量正向统一 `e = r * Scale + Offset`，明确采用两步 IEEE 754 运算（先乘再加，不用 FMA）；每一步用 IsFinite 检查，`checked double` 不能检测 infinity。Signed/Unsigned 转 double 前用 BigInteger 与 double 对应的精确整数比较；不能精确表示则 PrecisionLoss，不悄悄近似。raw 越界、换算非有限、工程越界都返回工程值 null 与 Invalid/Overflow，raw 由外围观察保留。Good 不包含输出网格判定，输入采样不强制落在命令网格上。

AO 输出：先验证工程值，`q=(e-Origin)/Resolution` 有限；Exact 要求重建网格值与 e 的绝对差 <=显式 WriteGridTolerance，失败 ResolutionMismatch。NearestToEven 用 Math.Round(q, MidpointRounding.ToEven)，得到 EffectiveValue 后重新校验工程范围；不截断边界。再逆变换 `r=(EffectiveValue-Offset)/Scale` 并检查 finite、raw 域；整数 raw 要求整数且可精确表示，转换使用 checked。逆变换、raw 编码、再正向换算的绝对误差不得超过 WriteGridTolerance，否则 PrecisionLoss。Floating raw 仍验证该误差。不静默扩大容差。DO EncodeOutput 使用极性反转；Counter/Latch 输出一律 Unsupported。错误 Normalized/EffectiveValue 和 raw 均为 null，不返回半成功值。

RawSigned/RawUnsigned的BitWidth必须与AnalogRawFormat一致，并在该位宽可表示域和声明raw域内；RawFloating只匹配FloatingAnalogFormat。CounterValue/RawCounter的BitWidth必须与CounterSpec一致、value<=2^BitWidth-1，64位上界用BigInteger计算不做移位64；LatchValue/RawLatch的SourceId须与LatchSpec一致，HasCaptureId=true时CaptureId必填，false时不允许伪造CaptureId。Convert对Counter/Latch只复制这些已校验字段，不做double换算。EngineeringConversionResult失败Quality按原因：NonFinite/算术溢出为Overflow，其余Invalid；成功Good。数字映射无模拟量单位/量程，不能传AnalogValue(true的数值编码)代替DigitalValue。

### 3.4 时间、来源与质量

```csharp
public enum ObservationSource { DirectRead, HardwareSample, HardwareEdge,
    PollingSample, PollingDifference, Replay }
public enum SequenceSource { Device, Adapter }
public sealed record HostStamp(string DomainId, long Tick, long TicksPerSecond);
public sealed record DeviceStamp(string DomainId, ulong Tick, string ClockRevision);
public sealed record ObservationTime(DateTimeOffset ReceivedAt, HostStamp Received,
    HostStamp? EarliestSample, HostStamp? LatestSample, DeviceStamp? Device,
    TimeSpan? ClockErrorBound);
public sealed record SignalObservation(string RequestId, string SignalId,
    RawSignalValue? RawValue, SignalValue? EngineeringValue,
    ValueQuality Quality, string ReasonCode, ObservationSource Source,
    ObservationTime Time, ulong Sequence, SequenceSource SequenceSource,
    string ConnectionGeneration, string MappingRevision, string? SnapshotId,
    string? ResetEpoch, bool IsCurrent, bool Simulation);
public sealed record FilteredObservation(SignalObservation Raw,
    SignalValue? FilteredValue, ValueQuality Quality, string FilterRevision,
    TimeSpan Delay, ulong SuppressedTransitions, string ReasonCode);
public sealed record ObservationBatch(ImmutableArray<SignalObservation> Observations,
    SamplingMode SamplingMode, string? SnapshotId, ImmutableArray<SignalError> Errors);
public sealed record SignalEvent(ulong EventOrdinal, string SubscriptionId,
    SignalObservation? Observation, FilteredObservation? Filtered,
    SignalError? Error, ResourceState ResourceState, ulong TotalGapCount);
```

- HostStamp 域由实例 TimeProvider 与实例 nonce 组成，TicksPerSecond>0，所有比较用其 GetElapsedTime 或同域比例；设备域须由 ClockDescriptor 声明，频率/回绕/误差来自官方设备/标定证据。缺少映射误差界就不能把 device tick 转成主机采样时刻。墙钟只审计，跳时不延长期限。
- DirectRead 的 EarliestSample 为发出读取前、LatestSample 为响应收到后；若协议返回缓存且不知 age，则这两个字段均为空，不能用“刚收到”证明新鲜。设备采样能映射时提供采样区间和误差；接收年龄只用于通信诊断。
- 请求 MaxAge 的满足条件：最早可能采样距当前单调时刻 <=MaxAge，且区间有效、同域、当前代、Good、无缺口。MaxAge=0 明确要求为本请求执行新读并带 RequestId 和读窗口，不复用缓存；新读窗口仍不等于严格瞬时采样。缺证据返回 StaleObservation/TimeDomainMismatch。
- PollingDifference 只表示相邻两次有效采样不同，边沿发生区间为前一有效采样至本次有效采样，不提供硬件边沿时刻/完整性保证。相同值不能证明中间没有短脉冲。请求硬件边沿/一致快照而能力仅轮询时直接 Unsupported，不静默降级。
- Sequence 按设备提供则保留其来源，Adapter 序号不冒充硬件序号。首观察无前驱不能推出边沿。乱序/重复分别诊断，不更新当前缓存；同序号不同 payload 是 ProtocolError。同代回绕须协议位宽和连续性证据；重连不拼接序列。
- DeviceSnapshot 只有设备明确提供一次捕获及同快照 ID 才成立；Sequential 逐项保留自己的时间窗，无全批时间。质量未知/无值、Stale、过滤、缺口都是独立事实，不能被绿色灯号合并。FilteredObservation 保留 Raw，过滤结果不能覆盖 raw 通道历史。

## 4. 运行端口、工厂与有界进程 Owner

C1 纯函数不依赖本节。C2 托管服务、模拟/回放和宿主可在无真实设备环境运行；真实 Adapter 和平台 Owner 绑定单独准入。本节端口是本模块运行契约，不向调用者泄漏 SDK 句柄。

### 4.1 请求、预算与授权

```csharp
public sealed record AuthorityContext(string PrincipalId, string SessionId,
    string CredentialReference, string PolicyRevision);
public enum SignalAction { Read, Subscribe, Write, Pulse, Query }
public sealed record AuthorizationRequest(AuthorityContext Caller, SignalAction Action,
    string DeviceId, ImmutableArray<string> SignalIds, string MappingRevision,
    string ConnectionGeneration, string RequestId);
public sealed record AuthorizationDecision(bool Allowed, string DecisionId,
    string PolicyRevision, HostStamp Expires, SignalError? Error);
public interface ISignalAuthorizationPort
{
    ValueTask<AuthorizationDecision> AuthorizeAsync(
        AuthorizationRequest request, CancellationToken ct);
}
public sealed record ResourceLimits(int MaxSignalsPerRequest, int MaxSubscriptions,
    int MaxPendingOperations, int RawEventCapacity, long RawEventBytes,
    long MaxRequestBytes, long IdempotencyBytes, int IdempotencyEntries,
    TimeSpan IdempotencyRetention, int MaxDiagnosticEvents);
public enum JournalPolicy { MemoryOnly, DurableBeforeSend }
public sealed record RuntimeProfile(string Id, string Revision, string SourceReference,
    ResourceLimits Limits, TimeSpan CleanupObservation, TimeSpan DisposeDeadline,
    TimeSpan ReadRetryDelay, int ReadRetryCount, JournalPolicy JournalPolicy);
public sealed record OperationContext(string RequestId, AuthorityContext Authority,
    string ExpectedMappingRevision, string ExpectedConnectionGeneration,
    TimeSpan Budget, DateTimeOffset? AuditNotAfter);
public sealed record ReadSignalsRequest(OperationContext Context,
    ImmutableArray<string> SignalIds, TimeSpan MaxAge, bool RequireDeviceSnapshot);
public sealed record SubscribeRequest(OperationContext Context, string SubscriptionId,
    ImmutableArray<string> SignalIds, EdgeSource RequiredEdgeSource,
    bool IncludeUnchanged, TimeSpan MinPublishInterval, int BufferCapacity);
public sealed record IdempotencyIdentity(string DeviceId, string OwnerNamespace,
    string Key);
public sealed record WriteSignalRequest(OperationContext Context, string SignalId,
    SignalValue Value, bool RequireApplicationEvidence, IdempotencyIdentity Identity);
public sealed record PulseRequest(OperationContext Context, string SignalId,
    bool ActiveValue, bool EndValue, TimeSpan Width, IdempotencyIdentity Identity);
public enum BatchFailurePolicy { StopBeforeNext, Continue }
public sealed record WriteBatchRequest(OperationContext Context,
    ImmutableArray<WriteSignalRequest> Items, BatchFailurePolicy FailurePolicy);
public sealed record QueryCommandRequest(OperationContext Context,
    IdempotencyIdentity Identity, string OriginalConnectionGeneration);
public sealed record DrainRequest(string RequestId, TimeSpan ObservationBudget);
```

全部 TimeSpan 非负且不允许 Infinite；Budget/CleanupObservation/DisposeDeadline>0，Width>0，MaxAge>=0、MinPublishInterval>=0。资源容量/字节>0、Retention>0、ReadRetryCount>=0；没有默认物理脉宽、采样率、缓冲、重试或 P99。资源上限必须可被宿主总预算容纳，配置不完整先拒绝工厂，不开连接。有效请求编码的 UTF-8 字节数和 DTO 估算保有字节由 §14 的规范方式计入预算；Batch 总项数/字节也在总预算内，不按每项重复扩张。Context 各修订必须当前匹配，AuditNotAfter 过期即拒绝；接纳时将预算固定为单调截止时刻，不随墙钟调整。

AuthorityContext 是凭证引用，不是权限。调用方填写 `maintenance.output` 等字符串不能授权；宿主端口认证 Principal/Session/Credential 并核模式、互锁政策和动作范围。Core 入队前校验一次；发送前共享 Owner 在其唯一发送序列内再次调用授权并核代/期限。若授权端口异步等待，返回后再次核对所有快照；模式/权限修订更改使决定失效。Owner 以“验证决定→提交到设备”的不可交错发送段避免 TOCTOU；不能把互锁的物理持续保证交给软件授权。Authorization 失败/异常/超时 fail closed，0 次发送；读权限也必须显式校验。

### 4.2 结果、订阅与诊断

```csharp
public sealed record ReadSignalsResult(OperationState State, ObservationBatch Batch,
    ImmutableArray<SignalError> Errors);
public enum CommandEvidenceKind { ProtocolAck, CorrelatedApplicationReceipt,
    TerminalReadback, PulseStart, PulseEnd }
public sealed record CommandEvidence(CommandEvidenceKind Kind, string RequestId,
    string ConnectionGeneration, string? DeviceCommandId,
    SignalObservation? Observation, string EvidenceReference);
public sealed record CommandResult(string RequestId, IdempotencyIdentity Identity,
    OperationState State, CommandOutcome Outcome, ResourceState Resources,
    ImmutableArray<CommandEvidence> Evidence, ImmutableArray<SignalError> Errors);
public sealed record WriteResult(CommandResult Command,
    SignalValue Requested, SignalValue? Effective);
public sealed record PulseResult(CommandResult Command, bool? StartApplied,
    bool? EndApplied, TimeSpan RequestedWidth, TimeSpan? MeasuredWidth,
    string? MeasurementEvidence);
public sealed record WriteBatchResult(OperationState State,
    ImmutableArray<WriteResult> Items, ImmutableArray<SignalError> Errors);
public enum CommandLookupStatus { Found, NotFound, Unsupported, Unavailable }
public sealed record CommandLookupResult(CommandLookupStatus Status,
    CommandResult? Result, ImmutableArray<SignalError> Errors);
public sealed record DrainResult(string RequestId, ResourceState State,
    int InFlightOperations, int Callbacks, int Leases, ImmutableArray<SignalError> Errors);
public sealed record DiagnosticSnapshot(string RootId, string OwnerNamespace,
    ConnectionState Connection,
    ResourceState Resources, string? ConnectionGeneration,
    int PendingOperations, int Subscriptions, int QueuedEvents, long QueuedBytes,
    ulong Gaps, ulong Rejected, int UnresolvedCommands,
    ImmutableArray<SignalError> RecentErrors);
public interface ISignalDiagnosticsPort
{
    bool TryPublish(DiagnosticSnapshot snapshot); // 非阻塞；false 增加独立丢失计数
}
public interface ISignalSubscription
{
    string SubscriptionId { get; }
    IAsyncEnumerable<SignalEvent> ReadAllAsync(CancellationToken ct);
    Task<DrainResult> StopAsync(DrainRequest request);
}
public sealed record SubscriptionResult(OperationState State,
    ISignalSubscription? Subscription, ImmutableArray<SignalError> Errors);
```

同一事件 Observation 和 Error 可同时存在（原始证据有效但过滤/缺口退化）；Filtered.Raw 必须与 Observation 同身份。Fatal 错误没有观察时 Observation=null。SubscriptionId 只在当前服务代有效，不允许复用停过的订阅。ReadAll 取消仅停止该读取者；StopAsync 才撤销订阅，后台排空不由枚举 finally 猜测。Stop/Close 幂等并返回原 Task，有限观察到期可返回 DrainUnknown 快照；资源退出继续由原 Owner 跟踪，不由第二次调用重新发 stop。

### 4.3 工厂、原 Task 强持和端口

```csharp
public sealed record RootRegistryOptions(int Capacity, string OwnerId,
    string SourceReference);
public sealed record RootOptions(string RootId, RuntimeProfile Profile);
public sealed record ServiceOptions(string OwnerNamespace, DeviceIdentity ExpectedDevice,
    MappingSnapshot Mapping, RuntimeProfile Profile);
public sealed record ServiceDependencies(IDeviceSignalAdapter Adapter,
    ISignalAuthorizationPort Authorization, ISignalDiagnosticsPort Diagnostics,
    ISignalOperationJournal? Journal);
public sealed record ServiceOpenResult(OperationState State,
    IDeviceSignalService? Service, ImmutableArray<SignalError> Errors);
public sealed record CleanupObservation(ResourceState State,
    ImmutableArray<DiagnosticSnapshot> Snapshots, ImmutableArray<SignalError> Errors);
public sealed class OwnedTask<T>
{
    public string OperationId { get; }
    public Task<T> Completion { get; } // 原始唯一 Task；不换成超时包装 Task
}
public sealed class SignalRootRegistry
{
    public SignalRootRegistry(RootRegistryOptions options, TimeProvider clock);
    public SignalRoot CreateRoot(RootOptions options);
    public Task<CleanupObservation> ObserveShutdownAsync(TimeSpan budget);
    public ImmutableArray<DiagnosticSnapshot> Snapshot();
}
public sealed class SignalRoot
{
    public string RootId { get; }
    public OwnedTask<ServiceOpenResult> BeginCreate(ServiceOptions options,
        ServiceDependencies dependencies, CancellationToken ct);
    public Task<CleanupObservation> BeginClose(TimeSpan observationBudget);
    public OwnedTask<CommandLookupResult> BeginReconcile(
        QueryCommandRequest request, CancellationToken ct);
    public DiagnosticSnapshot Snapshot();
}
public interface IDeviceSignalService
{
    DeviceCapabilities Capabilities { get; }
    DiagnosticSnapshot Diagnostics { get; }
    OwnedTask<ReadSignalsResult> BeginRead(ReadSignalsRequest request, CancellationToken ct);
    OwnedTask<SubscriptionResult> BeginSubscribe(SubscribeRequest request, CancellationToken ct);
    OwnedTask<WriteResult> BeginWrite(WriteSignalRequest request, CancellationToken ct);
    OwnedTask<PulseResult> BeginPulse(PulseRequest request, CancellationToken ct);
    OwnedTask<WriteBatchResult> BeginWriteBatch(WriteBatchRequest request, CancellationToken ct);
    OwnedTask<CommandLookupResult> BeginQuery(QueryCommandRequest request, CancellationToken ct);
    Task<DrainResult> CloseAsync(DrainRequest request);
}
```

Registry 是宿主在进程启动时显式创建并长持的有界进程 Owner，不是模块静态单例。CreateRoot 在任何设备/Adapter/Factory 工作前占 Registry 槽位；RootId 重复、容量不足或错误配置同步抛 ArgumentException/InvalidOperationException，尚未产生外部副作用。CreateRoot 后 Root 立即已登记，即使 BeginCreate 同步异常也有 finally 可观测的 Owner。BeginCreate 首先捕获 options、deps、ct、原 Task 身份和借用对象，再经内部启动门放行实际工作；资源任务不能在登记前启动。Factory 只支持一个服务/Root；重复 BeginCreate 拒绝，不暗中开第二连接。

Begin* 接口同步注册 OwnedTask、不可变请求和借用端口，在放行前占 MaxPendingOperations；容量不足生成已完成的 Rejected 结果，不调用 Adapter。预期错误不抛 Task 异常；意外实现异常归入 Failed/Unknown 并保留原异常诊断，资源归还仍待独立证据。调用方用 WaitAsync 只限制自己的等待，超时包装不覆盖 Completion，取消不丢 original Task。Task、延迟工厂产物、在途订阅、buffer、Adapter 租约、Journal 都强持于 Root，直至原工作实际结束且归还已确认。

BeginClose 首次即同步关接纳门，返回同一观察 Task；内部 Close 完整工作 Task 独立强持，不能受已取消的业务 token 控制。观察预算届满返回 DrainUnknown 与剩余量；Registry 槽不释放，不能成功、强杀 SDK 或丢 Owner。迟到 Factory 成功时 Root 不再发布可用服务，立即排空/归还新获得租约；迟到 Subscribe 同理先 Stop 后归还；迟到 ACK 只追加对账。最终排空且没有未决命令后原 Registry 删除该槽，可再次分配；无法证明停止的对象一直占槽，新的接入 ResourceBusy。若物理资源已 Released 但命令仍 Unknown，Root保持 UnresolvedCommands>0 和原命令身份/结果/Task/Journals，不能因资源释放丢对账Owner。监督/移交必须由进程 Owner 明确接受 Root 对象与原 Task、未决命令原payload及查询入口后才可解除原持有者；本轮不提供自动移交API，未接收前一直保有。窗口关闭、方法离栈、GC 和观察到期都不是接受证明。

Registry 的 ObserveShutdownAsync 只有限观察已 BeginClose 的全部 Roots 并请求未关闭 Roots 关闭，不声称观察超时等于进程已停止。宿主进程退出政策/强制停机只能由外部设备 Owner 决定；模块不在未知资源上执行强制退出。

RootOptions.Profile必须与ServiceOptions.Profile逐字段一致；clock由Registry注入服务，Simulator/Replay必须接收同一TimeProvider与相同主机DomainId声明，真实设备ClockDescriptor不能冒充HostStamp域。OwnedTask构造器仅内部可用，公开调用者不能替换Completion/OperationId。CommandResult.Resources只指本操作拥有的队列登记/缓冲/回调；不把仍在用的服务lease误列为该操作资源，Root最终释放另查全服务lease。

BeginReconcile仅对本Root已登记的Unknown原身份开放，允许在正常服务接纳已关闭后执行有限查询；不是重开写服务。原资源尚在途时继续经原lease的Owner查询；已经Released时，仍由同Root登记原Task并调用保存的Adapter工厂Acquire一个**只读查询租约**，核验设备身份/QueryScope，查询OriginalConnectionGeneration与原Identity，finally按独立期限归还。该租约不允许Write/Pulse/Subscribe、不开第二物理连接；QueryScope=Connection且旧代已失效时返回Unsupported/Unknown，不Acquire重发。新lease所有晚产物仍归原Root强持，可能使Resources重新Draining/DrainUnknown；查询期间不能回收Root槽。Found且相关可靠证据确认Applied/NotApplied/明确NotExecuted后只追加原命令结果并减少UnresolvedCommands；NotFound/异常/超时绝不减数。BeginReconcile的Context使用查询时当前授权/代/有限Budget，OriginalConnectionGeneration保持原值；新Context不改原动作payload/截止期。进程Owner可通过已持有Root引用发起该操作，无需创建另一会话/Owner或变更幂等namespace。


## 5. 执行顺序、命令事实与恢复

### 5.1 接纳、读取和连接代

服务开通顺序：登记 Root → 验证 mapping/Profile/身份 → AcquireLease → 核对能力/当前连接代/地址 canonical/时钟描述 → 取得当前能力快照 → 发布服务。任何阶段失败都返回 ServiceOpenResult；未归还资源留于 Root，不把 Service=null 当作已释放。一个服务固定一个 MappingRevision；映射更新须新 Root/新 lease，并按唯一 Owner 串行切换，旧请求不迁移。

读取顺序：结构/预算 → 修订/连接代 → 认证授权 → 单调截止检查 → 逐项或设备快照读 → 核来源序列与时间 → raw 校验/转换 → 更新有效缓存 → 按输入顺序返回逐项观察。空/重复 SignalId、不可读、旧代、预算缺失在发送前拒绝。设备批响应必须每个请求项一一对应；缺项返回 Unknown/ProtocolError，不把先前缓存当本次读数；重复/多余项亦协议错误。只读重试最多 ReadRetryCount 次，每次重新核代、期限与授权，ReadRetryDelay 用虚拟/注入单调时钟，不重试 clear-on-read、锁存取走等副作用协议；此类协议不得声明为本模块普通 Read。

Connection Online 是通信与能力当前有效，不能推出“安全可运行”。协议错误可 Degraded，断线停止发送并撤销当前代资格，缓存投影 Stale。共享 Owner 先将旧代标失效，停止全连接新发送，隔离所有旧回调，然后排空并按设备 Profile 决定是否重新打开；消费者租约无需全部“自愿退出”才能开始故障失效，但旧实际资源排空前不得释放/复用原句柄。排空超时进入 DrainUnknown，禁止冒进重连。正常共享连接关闭只在最后 lease 归还后；服务 Close 不主动关其它 lease。重连后能力重新验证和授予新 lease，不自动续订，不重放任何输出。

### 5.2 幂等边界与查询

幂等范围固定为 `DeviceId + OwnerNamespace + Key`，DeviceId 是已核验设备身份而非 IP；OwnerNamespace 来自唯一连接/写 Owner，不由调用方任意换 namespace 绕过检查。Write/Pulse 请求身份中 DeviceId/OwnerNamespace 必须与服务一致。第一次接纳保存规范命令 payload；重复请求用深比较：

- 相同身份、完全相同 payload：返回原请求/原 OwnedTask 对应事实，即使新的 Context.RequestId 不同也返回原 RequestId；不再占设备发送次数。
- 同身份不同目标、值、脉宽、结束值、映射或语义期限：IdempotencyConflict，0 次额外发送。排队/执行中的并发同键由原 Owner 原子登记，只有一个 winner。
- payload 包含 Action、SignalId、值类型/位宽/单位、EffectiveValue、映射修订、CapabilityRevision、原连接代、Width/EndValue、RequireApplicationEvidence、第一次接纳的授权 Principal/Policy 和 AuditNotAfter；Budget 在第一次接受时固定，重复调用不能延长执行期限。Read/Query/Drain 不使用输出幂等键。
- 原命令未决时禁止按 TTL/容量驱逐；已知命令也至少保留 Retention。到容量上限先拒绝新输出，不删 Unknown 来腾空间。到期删除只允许原 Owner 已确认结果且无未决资源，保留身份墓碑至该 OwnerNamespace 停止接受；重用过期键返回 IdempotencyConflict，新动作由调用方显式选择新键。墓碑计入同一预算，容量不足拒绝。
- Query 仅查询原身份与原连接代；NotFound/Unsupported/Unavailable 都没有“不执行”的含义。连接内可查询的协议，跨重连后只能 Unknown；DevicePersistent 必须实证设备持久化的 ID/查詢有效期，不从内存 journal 推断。
- MemoryOnly 明确只保证当前进程去重，崩溃后所有未决为 Unknown，开机不自动重发。DurableBeforeSend 也不等于恰好一次：设备与 Store 之间没有事务时“保存意图后已发送但发送标记未落盘”的窗口仍为 Unknown。只有设备持久化幂等/查询及实证覆盖后才可说该具体命令可跨重启对账。

### 5.3 写入、回读与批量

发送链唯一：validate → register original key/payload → 权限/期限/代 → durable intent及send-attempt提交（政策要求时）→ 进入共享 Owner 队列 → 发送段再次授权/代/期限 → physical send → 收集相关证据 → 写回执 → 返回 CommandResult。Store等待不得插入最后授权与send之间的发送段；send-attempt早于发送且仅表达可能执行，后续撤权/期限拒绝追加NotSent记录。写、脉冲、clear、复位均禁止传输层自动重发。可确认未发送的 Rejected/NotExecuted 才没有副作用；底层 send 异常但可能已到设备为 Unknown。

Applied 限定为**相关联的设备应用证据**，不是“现在看见设定值”：
- ProtocolAck 仅 Acknowledged。
- CorrelatedApplicationReceipt 必须带当前代、原 DeviceCommandId/RequestId，并由协议明确表示该动作已应用。
- TerminalReadback 是独立观察；若协议不带动作关联，可能早于发送、值恰好相同、其它写者写入或发生 ABA，不自动提升 Applied。可信串行 Owner 的新鲜写后读仅证明当前端子值；只能附证据，不能证明脉冲/一次性动作执行。
- 明确设备关联拒绝可 NotApplied/Failed；超时、关联缺失或回读矛盾是 Unknown/Degraded，不伪造 NotApplied。即使 Applied 也不证明气缸到位/安全许可/质量放行。
- RequireApplicationEvidence=true 在能力不能产生相关应用证据时发送前 Unsupported；false 可返回 Acknowledged/Sent，UI仍不能写“输出完成”。

Batch 固定非原子，按 Items 顺序；总 Context 与各项身份/映射/授权一致，每项独立幂等键，重复键整批预校验拒绝。整批先做可离线校验，失败全部 NotSent；运行权限撤销、断线等仍可部分成功。StopBeforeNext 在某项非 Applied 后停止后续，将后续明确 NotExecuted；Continue 逐项重新核权限/期限继续，只能在 Owner 仍允许时执行。不回滚，不声明原子写，不把未发送项遗漏。返回长度/顺序等于输入，整体 PartialFailure 伴逐项事实；所有 Applied 时才 Completed。缺少应用证据而策略接受 ACK 仍整体 Unknown/未证实，不全批成功。

PartialFailure是ErrorCode，不是OperationState枚举。batch只要任一项副作用Unknown，State=Unknown；否则有非Applied项State=Failed并Errors含PartialFailure；预校验整批拒绝State=Rejected；全部Applied且各操作资源Released才Completed。正常Read无错误且全部满足时State=Observed，部分/缺失在Batch.Errors逐项保留，State=Failed或TimedOut，不能Observed。CommandOutcome.Sent/Acknowledged只表示已有该级证据且应用未证实，OperationState=Unknown；Outcome=Applied且资源尚未释放只发布Executing快照，不最终Completed。

### 5.4 脉冲、计数、锁存与滤波

脉冲主路线为设备自主硬件计时，CanPulse 且 HardwarePulse、明确 Width 有效域及最终电平语义才可发送；Width 在闭区间 MinPulseWidth..MaxPulseWidth（两者非空、>0、min<=max），ActiveValue与EndValue必须不同，EndValue必填、不猜默认false。软件 Task.Delay 两次写作为通用脉冲路线**不选**：无法保证取消/GC/断线/权限撤销时第二沿送达或精确时宽；需要软件开关序列的产品另行编排并承认两个独立副作用。硬件启动 ACK 不等于脉冲结束；只有相关 Start/End 证据完整且时域已知才 Completed/Applied。结束未知时 EndApplied=null、Outcome=Unknown，即使资源 Released 也不能认为输出已恢复；不发补偿复位。测得宽度须独立设备/HIL证据，不能用主机两次接收差当实际脉宽。

Counter 只观察原始 unsigned、位宽、ResetEpoch 和序列。差量只在同连接代/同 epoch、设备可靠序列/连续性和明确最大可能增量证据下求模；必须保证观察间真实增量 <2^BitWidth。否则 raw 仍保留而 delta=null、Discontinuous，不能假设只回绕一次；多圈、重启、清零、缺样都不能合并。Latch Latched=true 仅表示某 Source 的锁存事实；CaptureId 支持时用于重复去重，不支持时不能数“触发次数”。Read 不清锁存，CanClear 也不授清除权；clear/reset 需设备/外部 Owner 的独立副作用契约，当前整模块非目标。

过滤主路线为 Core 对原始时间证据的确定性投影，设备已滤波的数据明确 SourceReference，不能再当未滤原始边沿。DigitalStableWindow：新逻辑值成为 pending，在**持续有效观察**且有效采样间隔上界由设备证据覆盖窗口时才提交；无边沿/样本不能靠单纯等待证明稳定。缺口/断线/过龄清 pending 并置 Unknown，首次值作为基线不伪造边沿。AnalogHysteresis：初始值在上下阈值之间时输出未定，>=Upper 为 true、<=Lower 为 false，中间保留已知状态；这只是阈值投影，不是任何设备许可。原值噪声/过滤延迟/抑制计数独立保留。

## 6. 结果与资源分离、取消和关闭

OperationState/CommandOutcome 表示工作和设备副作用，ResourceState 表示实际在途资源；它们是两个轴。Command Unknown 可以随后资源 Released，仍需设备对账；命令 Applied 可以资源 DrainUnknown，仍不能释放其在途缓冲。资源未知时不得发布清理成功或取消成功。调用返回一个 Unknown 快照不销毁真实工作 Task。

| 条件 | 工作/命令结果 | 资源/后续动作 |
|---|---|---|
| 入队前无效/无权/已取消 | Rejected/NotSent 或 Cancelled/NotExecuted | 没有外部租约时可 Released；已有服务 lease 不因此关闭 |
| 排队后确认发送前移除 | Cancelled/NotExecuted | 等队列登记归还，原 Task 保留 |
| 已开始 send，取消/超时/丢 ACK | Unknown/UnknownOutcome | 停止新发送，原 Owner 查原命令，不能新键重发 |
| 读等待超时且无副作用 | TimedOut，缺失项 Unknown | 在途 read/callback 实际退出前 Draining/DrainUnknown |
| 回执关联证明应用 | Completed/Applied | 独立跟踪该操作资源，不能提前 Dispose |
| 排空观察预算届满 | 无新增完成结论 | DrainUnknown，Owner/Task/lease 仍强持 |
| producer/callback/消费者任务退出且 lease 归还已确认 | 保留原结果/追加查询结果 | Released，允许回收 Root 槽 |

取消令牌用于请求停止接纳/等待，不是物理撤销保证。CloseAsync 首次同步关闭服务接纳门、拒绝后续 Begin*，撤销原订阅 producer，等待在途 callback/协议/consumer，释放自有 buffers，归还本服务 lease；共享连接由连接 Owner 决定。Close 与 Root Close 都使用新独立 cleanup 截止时刻，不传入已取消业务 token。设备 Query 有有限查询期限，查询失效不阻断已经证明的内存资源归还，但输出 Unknown 继续保留记录；设备 still-running resource 无退出证据才阻断归还。

Close 内部完整 Task 不因观察到期消失，所有 late callback/Acquire/Subscribe/Read result 被原 Root 捕获；旧代事件诊断隔离，不回流当前订阅。late资源归还异常进入 DrainUnknown、保留对象和原异常；不重建“第二Owner cleanup”。异常处理顺序保持主错误、另附 cleanup 错误，finally 不覆盖主错误。同步 Dispose 不提供；Close 是显式异步协议，有界观察和实际归还分开。多次 Close 的观察结果不是多次物理 stop/close。

## 7. Adapter、模拟/回放及纯观察辅助端口

### 7.1 Adapter 完整边界

```csharp
public enum LeaseAccess { Normal, QueryOnly }
public sealed record AdapterAcquireRequest(DeviceIdentity ExpectedDevice,
    MappingSnapshot Mapping, string OwnerNamespace, RuntimeProfile Profile,
    HostStamp HostClock, HostStamp Deadline, LeaseAccess Access);
public sealed record AdapterLeaseResult(IDeviceSignalLease? Lease,
    ImmutableArray<SignalError> Errors);
public sealed record AdapterReadRequest(string RequestId,
    ImmutableArray<ChannelAddress> Channels, bool RequireDeviceSnapshot,
    HostStamp Deadline);
public sealed record RawChannelObservation(ChannelAddress Address, RawSignalValue? Value,
    ValueQuality Quality, string ReasonCode, ObservationSource Source,
    ObservationTime Time, ulong Sequence, SequenceSource SequenceSource,
    string ConnectionGeneration, string? SnapshotId, string? ResetEpoch, bool Simulation);
public sealed record AdapterReadResult(ImmutableArray<RawChannelObservation> Items,
    SamplingMode SamplingMode, string? SnapshotId, ImmutableArray<SignalError> Errors);
public abstract record AdapterCommand;
public sealed record AdapterWrite(ChannelAddress Address, RawSignalValue Value) : AdapterCommand;
public sealed record AdapterPulse(ChannelAddress Address, bool RawActive,
    bool RawEnd, TimeSpan Width) : AdapterCommand;
public sealed record AdapterCommandContext(string RequestId, IdempotencyIdentity Identity,
    ImmutableArray<byte> CanonicalPayload, string PayloadHash,
    string ConnectionGeneration, string MappingRevision,
    HostStamp Deadline, AuthorizationRequest Authorization);
public sealed record AdapterCommandReceipt(CommandOutcome Outcome,
    string? DeviceCommandId, ImmutableArray<CommandEvidence> Evidence,
    ImmutableArray<SignalError> Errors);
public sealed record AdapterSubscribeRequest(string SubscriptionId,
    ImmutableArray<ChannelAddress> Channels, EdgeSource RequiredSource, int Capacity);
public sealed record RawSignalEvent(RawChannelObservation? Observation,
    SignalError? Error, ulong TotalGapCount);
public interface IRawSignalSubscription
{
    IAsyncEnumerable<RawSignalEvent> ReadAllAsync(CancellationToken ct);
    Task<DrainResult> StopAsync(DrainRequest request);
}
public sealed record AdapterSubscriptionResult(IRawSignalSubscription? Subscription,
    ImmutableArray<SignalError> Errors);
public interface IDeviceSignalAdapter
{
    ValueTask<AdapterLeaseResult> AcquireAsync(AdapterAcquireRequest request,
        CancellationToken ct);
}
public interface IDeviceSignalLease
{
    DeviceCapabilities Capabilities { get; }
    ValueTask<AdapterReadResult> ReadAsync(AdapterReadRequest request, CancellationToken ct);
    ValueTask<AdapterCommandReceipt> ExecuteAsync(AdapterCommand command,
        AdapterCommandContext context, ISignalAuthorizationPort authorization,
        CancellationToken ct);
    ValueTask<AdapterSubscriptionResult> SubscribeAsync(AdapterSubscribeRequest request,
        CancellationToken ct);
    ValueTask<CommandLookupResult> QueryAsync(QueryCommandRequest request,
        HostStamp deadline, CancellationToken ct);
    Task<DrainResult> ReleaseAsync(DrainRequest request);
}
```

Adapter 对象是无资源的接入端口/工厂，实际连接租约只由 Acquire 得到；若外部组合根已持有连接，其 sub-port Acquire 只授通道租约而非重开连接。Lease 不曝光 SDK 句柄，全部路径由共享 Owner 管理物理互斥/发送及最终排空。Core 等待 Acquire 前已登记；返回非空 Lease 即使 Errors 非空仍须归还，不忽略失败产物。

AcquireRequest.HostClock是Registry的主机时标声明，Deadline同域且未来；Adapter读取/接收时使用该注入TimeProvider生成HostStamp，不另造未知频率。Access=QueryOnly严格禁止Execute/Subscribe，正常Acquire使用Access=Normal。Acquire身份/域/期限不合法先拒绝，无lease时Errors非空；真实共享Owner能力改变必须通过新代发现，不修改已发布不可变Capabilities。动态健康/gap/资源通过Diagnostics和事件发布；每个订阅EventOrdinal由Core在接受正式事件时单调递增，overflow不能借UI preview覆盖。正常事件顺序固定：注册接收路径→Subscribe成功→Observation/Gap/错误→Stop开始→producer退出→在途callback/consumer退出→Released；Stop与首回调交错由同一接纳门串行，未获得SubscriptionResult的late订阅也归Root注销。

Execute 内执行 §4.1 的发送前授权和 §5.2 原子幂等登记，共享 Owner 接收 PayloadHash 与原始结构 payload 对应的记录，hash 相同不能取代精确记录比较。调用结果应逐值映射厂商 status。Release 不复位输出、不 close 其它租约、没有隐式自动重连。协议 flush/关句柄与回调同步必须按厂商规定；不能认为 socket关闭或 Channel.TryComplete 就释放 native。

原始队列用 bounded Channel，FullMode=Wait、AllowSynchronousContinuations=false；驱动 callback 不 await/阻塞，调用 TryWrite，false 立即在独立原子状态计缺口/Overflow，并将消费者质量降为 Discontinuous，必要时暂停新接纳。缺口记录不能也依赖满队列才能可见。队列耗字节随入队、出队和归还计数。默认不选 DropOldest/DropNewest/DropWrite；UI latest-value 投影可单独合并，不能覆盖原队列。一个订阅慢消费者只影响其预算/缺口，不能占用驱动线程或静默掩盖其它消费者数据。

### 7.2 确定性 Simulator 与 Replay

```csharp
public enum SimulationAction { Emit, Disconnect, Reconnect, LoseAck, Duplicate,
    OutOfOrder, FailRead, RejectCommand, LosePulseEnd, Overflow,
    DelayAcquire, DelaySubscribe, DelayRelease, PersistFailure }
public sealed record SimulationStep(TimeSpan At, SimulationAction Action,
    string TargetId, RawChannelObservation? Observation, SignalError? Error);
public sealed record SimulatorOptions(DeviceCapabilities Capabilities,
    ImmutableArray<RawChannelObservation> InitialObservations,
    ImmutableArray<SimulationStep> Steps, string ScenarioId, string ScenarioHash);
public sealed record ReplayOptions(DeviceCapabilities Capabilities,
    ImmutableArray<RawSignalEvent> Events, string RecordingId, string RecordingHash);
public static class DeviceSignalAdapters
{
    public static IDeviceSignalAdapter CreateSimulator(
        SimulatorOptions options, TimeProvider clock);
    public static IDeviceSignalAdapter CreateReplay(ReplayOptions options, TimeProvider clock);
}
public sealed record FilterState(string ConnectionGeneration, string MappingRevision,
    SignalValue? Baseline, SignalValue? Pending, HostStamp? PendingSince,
    ObservationTime? LastTime, ulong? LastSequence, SequenceSource LastSequenceSource,
    bool? HysteresisValue, ulong SuppressedTransitions);
public sealed record FilterResult(FilterState State, FilteredObservation Projection,
    ImmutableArray<SignalError> Errors);
public sealed record CounterDeltaRequest(SignalObservation Previous,
    SignalObservation Current, ulong MaximumPossibleIncrement, string BoundEvidence);
public sealed record CounterDeltaResult(ulong? Delta, ValueQuality Quality,
    ImmutableArray<SignalError> Errors);
public static class SignalObservationFunctions
{
    public static FilterResult ProjectFilter(SignalDescriptor descriptor,
        FilterState? previous, SignalObservation observation,
        TimeSpan MaximumSampleGap, string GapBoundEvidence);
    public static CounterDeltaResult ComputeCounterDelta(CounterDeltaRequest request);
}
```

工厂只校验和深拷贝数据，不能打开设备、启动线程或模拟 root 外资源；模拟Acquire亦遵循真实lease边界。Simulator 时间由注入 clock 驱动，不随机、不按实际 sleep 推动；Steps At>=0、按时间和原数组下标排序，相同时间按输入顺序。Delay* 在“到达点+注入clock前进”释放 gate，可配置一直无 release 的场景用于 DrainUnknown；core/case wall watchdog 仍独立。Replay 只读，Write/Pulse 返回 Unsupported，所有 Capabilities/Observations 强制 Simulation=true，输入声称 false 也不得继承。模拟结果不得出现在生产证据渠道。

Replay事件按输入数组顺序且必须同记录主机时间域/正频率，接收tick非降；原始乱序设备seq可回放，但主机接收时间倒退/跨域记录在工厂拒绝。第一接收tick映射至Acquire完成时的注入clock起点，后续以原接收tick差/frequency调度；保留原DeviceStamp与recording来源，接收HostStamp映射到模拟主机域，不声称硬件时钟标定。无Observation的错误事件在紧随其前的观察时点发出，首个错误事件在起点发出。Subscribe仅从当前回放游标开始，不为新订阅重播历史；Read返回最近已到达的事件且按采样证据判断age，MaxAge=0不伪造新硬件观察，若录制无请求相关新读证据则StaleObservation。Replay没有事件时明确Unknown，不内置默认传感值。

IncludeUnchanged=false只减少相同采样值的订阅投影，不删除原始硬件边沿/Counter/Latch事件；MinPublishInterval只限制可合并的值预览，Raw事件逐一按序发送并计预算，不能用它去抖/丢边沿。RequiredEdgeSource=None允许纯采样；PollingDifference必须设备可read且Profile有显式轮询节奏，当前RuntimeProfile未提供PollInterval，所以C2不自行启动轮询线程，而只接受Adapter已按其Profile提供的Poll事件。硬件与poll模式不在运行中无提示切换。

Simulator 包含明确数值断言：每条命令 Execute 次数、在途 callback/Lease 数、订阅注册/注销次数、原Root保留数、原Task最终状态，可从 Diagnostics 读取；测试也可使用测试工程内实现的 BCL 假端口计数，不能在发布 API 中加测试魔法。PersistFailure 属于模拟Journal端口注入，不能让Adapter成为第二Store。

ProjectFilter 是纯状态转移：传入 MaximumSampleGap>0 与证据来源，用 LastTime/LastSequence 检查两个有效观察的最坏采样间隔；更宽/未知gap、不同代/映射/时间域、倒序/重复冲突、无效质量都重置pending，输出Unknown。pending候选取首次新值的LatestSample作为可保证起点，当前EarliestSample减PendingSince>=Window才提交，避免时间窗不确定性提前提交；无区间则不提交。连续相同值保留原pending起点，变化时换pending，提交后Baseline更新、Pending清空。原始采样之间即使间隔有界仍可能存在未观测跳变，所以该结果仅为采样去抖投影，不能证明物理持续稳定或完整边沿。硬件事件有完整无缺口证据时可作硬件事件去抖，但也不因无新事件凭空提交，需当前有效时间证据。AnalogHysteresis的FilteredValue是DigitalValue阈值投影，Raw仍是AnalogValue；Filter None返回原工程值、Delay=0，保持原Quality。SuppressedTransitions仅在pending逻辑候选被新变化取代而未提交时加一，不在重复样本加一；Delay按同主机域保守时间间隔，溢出返回Overflow。LastTime/Sequence每次有效且同代观察更新。ComputeCounterDelta 需要两个 RawCounter 同位宽、同ResetEpoch且非空、同代/映射、Good及无丢失设备序列，MaximumPossibleIncrement <模数，BoundEvidence 必填。模差用 BigInteger 防64位溢出；差>MaximumPossibleIncrement拒绝，不能用差很小反推没有多圈。没有条件返回 Discontinuous。辅助函数不访问时钟/设备、无隐藏状态。


### 7.3 A1 通用软件适配契约审核与绑定顺序

2026-10-11 本永久原会话按最新授权完成 A1 范围定向审核；不再等待总控技术复核。本节是 §7.1 端口的实现约束，不增加第二套 DTO、产品工厂或厂商 SDK API。公开参数、返回值及工厂已经确定：宿主注入无资源的 IDeviceSignalAdapter，唯一服务工厂为 §4.3 SignalRoot.BeginCreate；Simulator/Replay 工厂见 §7.2。具体厂商对象的构造和 SDK 方法属于型号接入任务，当前不虚构通用 CreateVendorAdapter，不把其尚无工程目录当成通用软件设计欠账。

**接入前与接入后绑定分开。** 宿主在 Registry.CreateRoot 前只构造无资源配置/端口，保证 Adapter 与 Registry 使用同一个注入 TimeProvider；已有物理会话由共享连接 Owner 持有，传入 sub-port，不重新打开。Root 占槽后才 BeginCreate，先执行 §3.2 映射、§4.1 Profile/预算/身份校验，再 AcquireAsync。HostClock 是主机域/频率声明，不是 TimeProvider 实例：适配器构造由宿主明确注入 Registry 所用 clock，Acquire 时核验声明与该 clock，不能从单个 Tick 推出频率或构造另一系统时钟。任何身份、修订、地址或能力不一致在服务发布及 Execute 前拒绝，不自动修订 MappingSnapshot。

Acquire 的配置检查顺序固定为：

1. ExpectedDevice 六个字段（DeviceId/Vendor/Model/Firmware/AdapterId/AdapterVersion）精确 ordinal 匹配实际身份；不把同 IP 当同设备，不用空字段通配。能力 ConnectionGeneration 非空、State=Online 或明确允许只读的 Degraded；Normal 写入资格仍须 Online，QueryOnly 不能写/订阅。
2. CapabilityRevision/MappingRevision 与请求一致，SignalRuntimeCapability.SignalId 唯一；映射每项都必须有能力项。能力中额外未租用信号可以保留在 Owner，不能因此授予本 lease 地址。缺项 Unsupported，修订变化 CapabilityMismatch/MappingMismatch；不以旧发现结果替代当前代。
3. Adapter 按其已绑定 AddressFormatVersion 解析每个地址；拒绝未知版本/越界/字节序不明/非法 SubChannel。解析后以实际物理端点身份判冲突，再按 §3.2 检查只读 alias；例如文本 `01`/`1` 若厂商解析为同通道，必须发现冲突，不能只比较原字符串。原地址继续保存在映射与诊断中，canonical 端点及 SDK handle 留在 Adapter/连接 Owner 内，不返回 UI 或作为新逻辑 SignalId。解析规范及实际范围来自型号 Profile；缺规范时拒绝该地址，不猜数值范围。
4. Adapter 按内部型号 Profile/官方能力事实核对 mapping 申请的读/写/订阅、raw 类型/位宽/量程和极性转换方向；公开 SignalRuntimeCapability 不含 raw域或 CanRead/CanWrite，不能从其缺少字段推断已支持，这些检查由 Adapter 在授 lease 前完成，不让 Core 猜 SDK。Spec 是宿主工程参数，不由能力发现覆写；厂商 raw域与宿主 raw域不兼容时拒绝，不夹紧。HardwarePulse 必须有同一型号证据及有效 min/max/end 行为；TerminalReadback/CorrelatedApplicationReceipt/QueryScope 均独立核实。未提供相关应用证据不开放 RequireApplicationEvidence 写入，不能把端子回读填作相关回执。
5. Clocks 的 DomainId 唯一，TicksPerSecond>0，CounterBitWidth 若存在只能 8/16/32/64，ErrorBound 若给出须非负且来源明确；观测 DeviceStamp.ClockRevision 对应该次能力修订，未知域/修订拒绝为 TimeDomainMismatch。没有时间映射/连续性证据仍可发布 raw 诊断，但不得伪造 current、硬件边沿时刻或 counter delta。
6. 连接 Owner 在实际授 lease 前检查全连接资源冲突、通道权限与 OwnerNamespace、接纳状态及 Deadline；失败零 Execute。QueryOnly 只授本 Root 原身份的有限查询权，不能借只读恢复打开额外输出入口。成功后 Capabilities 固定不可变，恢复/配置变化产生新代，旧 lease 无权发送。

**部分构造与原任务责任不能留给 SDK 猜测。** 每个异步 SDK open/register/subscribe/read/write/close 开始前，Adapter/共享 Owner 先登记原任务与可能生成的资源槽；即使 Acquire 未能返回 Lease，已经分配的句柄/回调仍由这个原 Owner 强持并按 §6 排空。不能仅 catch 后返回 null Lease 就丢弃内部产物。若异常返回非空 Lease，Root 仍归还；若底层产物晚到，原 Adapter Owner 捕获并释放，不能交给已关闭 UI。外部 ValueTask 需要观察/等待/清理时只调用一次 AsTask，保存该唯一 Task，不重复 await 或重复 AsTask 消费 SDK 提供的单次 ValueTask。Root 保存这条原 Task 及 lease/请求；超时 WaitAsync 只是观察包装。

**软件状态和有限恢复已确定。** 绑定阶段错误按上述 InvalidArgument/Unsupported/CapabilityMismatch/MappingMismatch/TimeDomainMismatch/ResourceBusy 及 §3 SignalError 返回；Acquire 后尚有未归还资源，Root 必须 Draining/DrainUnknown，不把失败产物视为 Released。正常工作、退化、断线、旧代隔离、关闭分别遵循 §5.1/§6。Adapter 不自动重连、不重发输出；Core 只按 §5.1 的有限 read retry 政策重试无副作用读取。每次 BeginReconcile 最多一次 Acquire、一次 Query、一次 Release，由 Context.Budget/独立 cleanup 预算限时观察，超时继续强持原 Task，不能循环创建查询 lease。重复恢复调用在原 Root 单飞：已有查询在途时 Busy；结束后宿主可显式创建新查询请求，原命令身份不变。物理资源 DrainUnknown 时不得为查询重开同设备第二连接；只能经仍在用的原 Owner 查询或返回 Unavailable。

**写入桥没有新的判定权。** AdapterWrite 仅接收 §3.3 EncodeOutput 校验后的 raw，不能再反转一次极性或静默量化；AdapterPulse 的 RawActive/RawEnd 按同 DigitalSpec 转换一次。Execute 核验 canonical bytes/hash、原身份/地址/连接代、发送前授权与期限，经过共享 Owner 单次发送；batch 在 Core 按 §5.3 逐项调用，Adapter 不能暗中改为原子批或自动回滚。回执原厂商 status 逐项映射，ACK/Applied/端子回读及双沿证据保持 §5.3～§5.4 区分；未知结果与资源状态保持双轴。Release 不复位、不清锁存、不关闭其它消费者 lease。

无 UI 接入直接复用 §9 两 Host：已配置 Adapter→ServiceDependencies→进程 Registry/CreateRoot→BeginCreate→观察/维护→finally 有限 BeginClose→原 Root 迟到归还/BeginReconcile；真实 Provider 只替换 deps.Adapter，不改变调用形状。厂商 SDK 暂不纳入，因此没有批准的厂商工程/公共 SDK 签名；这阻断具体型号实现，不阻断上述公开接口与软件处理顺序。

本轮增量反例走查：地址 `01`/`1` 解析同端点时写冲突拒绝；能力缺项/旧修订/原时钟域不匹配时不发布可写服务；open 取消但晚产物生成时原 Adapter Owner 保有并归还；同 Root 两次并发恢复时只有一个查询，第二 Busy；原资源 DrainUnknown 时不 Acquire 第二物理连接；QueryOnly Execute 拒绝；raw 极性转换仅一次；ACK 丢失后仍 Unknown。预期断言落在既有 §12 的 C2 Open/Root 与 C3 Auth/Write/Idem/Host 假端口 case，不创建新测试工程；真实端点解析/SDK行为与硬件输出断言仍在 A1 型号接入/HIL。每条反例同时核零额外发送、原 Task/Owner 保有和有限恢复，未执行 C# 测试或设备验证。

## 8. 参数建议、版本和配置治理

三层配置分开：宿主连接/Owner 与 RuntimeProfile；工程 MappingSnapshot；运行请求不可变 Context。每层记录 ID、修订、来源/hash/适用设备身份，历史观察永远按原 mapping解释；不按新极性重算旧数据。Core v0.2 Module API 是本轮唯一版本，旧 v0.1 不含极性/原始类型的 DTO 不能静默升级为有效映射。Major 改变类型/语义，Minor只增可选能力且有明确不支持策略，Patch不改变状态/判定。字段序列化、平台 ContractMajor 等由平台映射拥有，不再往模块 DTO 填未定义字段。

参数建议只用已标 Simulation/Replay 或授权离线证据，无真实设备副作用：
1. 数字去抖候选窗口从带硬件时标、gap界及标记参考的稳定/抖动片段提取。候选不超过 Profile 的最大可接受延迟，短有效脉冲不在评估中消失；缺标签/硬件完整性则 Abstain，不根据轮询无变化推荐。
2. 模拟滞回阈值只在已知有效域内，比较固定候选的误触发/漏检、最大延迟和原值保留；不从分位数推成物理工艺阈值。Scale/Offset、极性、单位、counter位宽、脉冲宽度没有自动推荐，必须工程/设备证据明确。
3. 缓冲容量/MinPublishInterval 可以基于固定profile的burst与消费者速度形成离线候选；必须处于宿主总预算内，关键raw不丢失。候选仅提示，不静默改变生产参数/扩容。
4. 建议记录输入hash、候选列表、评估方法、误接受/拒绝、P50/P95/P99/资源、边界/弃权原因、软件版本，由工程Owner确认形成新Mapping/Profile修订；旧请求停接纳/排空后才切换。UI只编辑draft，不把推荐当已批准事实。

绑定过程先验证身份/model/firmware/Adapter版本和Source，再验证capability/address/量程与clock事实，再授权/模式，最后开放服务。没有厂商地址/能力证据阻断该Adapter；不阻断纯Mapping/Simulator。运行修订更新不可覆盖当前snapshot，旧任务保留原连接/映射/权限修订和幂等记录；新Root须由共享Owner允许才能取得lease。

## 9. 两个不同无 UI 消费者最小调用闭包

以下是**以本页公开声明实现后可编译的宿主示例规格**，本轮没有创建/构建工程，不称已运行。使用 BCL，不引用 WPF/产品Shell/数据库。示例代码在消费者测试工程，不是额外发布DTO；两个方法的参数都可用 §3/4/7 的构造器构造。进程在启动时构造 SignalRootRegistry 并强持，方法返回之后仍负责该Registry，不能把它做为方法局部后丢弃。调用前 reserve Root，不先调用异步Factory再补登记。

### 9.1 触发观察/传感采集宿主

此消费者获取信号事实并交自身编排，绝不启动相机或给板件放行。返回 Success 仅说明该软件读取任务完成；不是硬件资格或生产许可。

```csharp
using Asun.Modules.DeviceSignals;
using System.Collections.Immutable;

public sealed record HostRunReport(bool Success, string Status,
    ImmutableArray<SignalObservation> Observations,
    ImmutableArray<string> Errors, CleanupObservation? Cleanup);

public static partial class SignalHostExamples
{
public static async Task<HostRunReport> RunObservationHost(
    SignalRootRegistry processRoots, RootOptions rootOptions,
    ServiceOptions options, ServiceDependencies dependencies,
    AuthorityContext caller, ImmutableArray<string> signalIds,
    TimeSpan maxAge, TimeSpan operationBudget, TimeSpan wallWaitBudget,
    TimeSpan cleanupBudget, TimeSpan wallCleanupBudget, CancellationToken ct)
{
    SignalRoot? root = null;
    CleanupObservation? cleanup = null;
    var errors = ImmutableArray.CreateBuilder<string>();
    var observations = ImmutableArray<SignalObservation>.Empty;
    bool success = false;
    string status = "Unavailable";
    try
    {
        root = processRoots.CreateRoot(rootOptions); // 副作用前登记
        OwnedTask<ServiceOpenResult> opening = root.BeginCreate(options, dependencies, ct);
        ServiceOpenResult opened = await opening.Completion.WaitAsync(wallWaitBudget, ct);
        if (opened.State != OperationState.Completed || opened.Service is null)
            throw new InvalidOperationException("OpenRejected");
        IDeviceSignalService service = opened.Service;
        var context = new OperationContext("read-0001", caller,
            service.Capabilities.MappingRevision, service.Capabilities.ConnectionGeneration,
            operationBudget, null);
        OwnedTask<ReadSignalsResult> pending = service.BeginRead(
            new ReadSignalsRequest(context, signalIds, maxAge, false), ct);
        ReadSignalsResult result = await pending.Completion.WaitAsync(wallWaitBudget, ct);
        observations = result.Batch.Observations;
        success = result.State == OperationState.Observed &&
            result.Errors.IsEmpty && result.Batch.Errors.IsEmpty &&
            observations.Length == signalIds.Length &&
            observations.All(x => x.IsCurrent && x.Quality == ValueQuality.Good);
        status = success ? "Observed" : "ObservationUnavailable";
    }
    catch (OperationCanceledException ex) { status = "WaitCancelled"; errors.Add(ex.GetType().Name); }
    catch (TimeoutException ex) { status = "WaitTimedOut"; errors.Add(ex.GetType().Name); }
    catch (Exception ex) { status = "HostFailed"; errors.Add(ex.GetType().Name); }
    finally
    {
        if (root is not null)
        {
            try
            {
                // 独立期限、无已取消业务 token；超时只停止宿主等待
                cleanup = await root.BeginClose(cleanupBudget).WaitAsync(wallCleanupBudget);
                if (cleanup.State != ResourceState.Released)
                { success = false; errors.Add("CleanupUnconfirmed"); }
            }
            catch (Exception ex) { success = false; errors.Add("Cleanup:" + ex.GetType().Name); }
        }
    }
    if (cleanup?.State != ResourceState.Released) success = false;
    return new(success, status, observations, errors.ToImmutable(), cleanup);
}
}
```

原 opening/pending 仍存于Root，不依赖局部变量寿命；TimeoutException/OCE 不调用第二Factory、不 dispose借用Adapter。进程监督从 processRoots.Snapshot 看到 DrainUnknown，继续持有并接收late Acquire/Read；最终Released之前不得将Root从registry移除。以上 .All 来自 System.Linq（测试工程 ImplicitUsings=enable）。

### 9.2 维护工具宿主：受控输出与原请求查询

与观察宿主不同，此消费者有显式维护授权、一个输出动作与原请求对账；参数不得从任意可编辑文本获得权限。未确认结果不能 Success，也不能再用新键写一遍。Pulse使用同样链但必须独立身份，不在Write超时后自动改发Pulse。

```csharp
public static partial class SignalHostExamples
{
public static async Task<HostRunReport> RunMaintenanceHost(
    SignalRootRegistry processRoots, RootOptions rootOptions,
    ServiceOptions options, ServiceDependencies dependencies, AuthorityContext caller,
    string signalId, SignalValue value, string key, TimeSpan operationBudget,
    TimeSpan wallWaitBudget, TimeSpan cleanupBudget, TimeSpan wallCleanupBudget,
    CancellationToken ct)
{
    SignalRoot? root = null;
    CleanupObservation? cleanup = null;
    var errors = ImmutableArray.CreateBuilder<string>();
    bool success = false;
    string status = "Unavailable";
    try
    {
        root = processRoots.CreateRoot(rootOptions);
        OwnedTask<ServiceOpenResult> opening = root.BeginCreate(options, dependencies, ct);
        ServiceOpenResult opened = await opening.Completion.WaitAsync(wallWaitBudget, ct);
        if (opened.State != OperationState.Completed || opened.Service is null)
            throw new InvalidOperationException("OpenRejected");
        IDeviceSignalService service = opened.Service;
        string generation = service.Capabilities.ConnectionGeneration;
        var identity = new IdempotencyIdentity(
            options.ExpectedDevice.DeviceId, options.OwnerNamespace, key);
        var context = new OperationContext("write-0001", caller,
            service.Capabilities.MappingRevision, generation, operationBudget, null);
        OwnedTask<WriteResult> pending = service.BeginWrite(
            new WriteSignalRequest(context, signalId, value, true, identity), ct);
        WriteResult result = await pending.Completion.WaitAsync(wallWaitBudget, ct);
        CommandResult command = result.Command;
        if (command.Outcome == CommandOutcome.Unknown)
        {
            var queryContext = context with { RequestId = "query-0001" };
            OwnedTask<CommandLookupResult> lookup = service.BeginQuery(
                new QueryCommandRequest(queryContext, identity, generation), ct);
            CommandLookupResult found = await lookup.Completion.WaitAsync(wallWaitBudget, ct);
            if (found.Status == CommandLookupStatus.Found && found.Result is not null)
                command = found.Result;
        }
        success = command.Outcome == CommandOutcome.Applied &&
            command.State == OperationState.Completed &&
            command.Resources == ResourceState.Released && command.Errors.IsEmpty;
        status = command.Outcome.ToString(); // 调用方显示时使用资源键映射
        if (!success) errors.Add("OutputUnconfirmed");
    }
    catch (OperationCanceledException ex) { status = "WaitCancelled"; errors.Add(ex.GetType().Name); }
    catch (TimeoutException ex) { status = "WaitTimedOut"; errors.Add(ex.GetType().Name); }
    catch (Exception ex) { status = "HostFailed"; errors.Add(ex.GetType().Name); }
    finally
    {
        if (root is not null)
        {
            try
            {
                cleanup = await root.BeginClose(cleanupBudget).WaitAsync(wallCleanupBudget);
                if (cleanup.State != ResourceState.Released)
                { success = false; errors.Add("CleanupUnconfirmed"); }
            }
            catch (Exception ex) { success = false; errors.Add("Cleanup:" + ex.GetType().Name); }
        }
    }
    if (cleanup?.State != ResourceState.Released) success = false;
    return new(success, status, ImmutableArray<SignalObservation>.Empty,
        errors.ToImmutable(), cleanup);
}
}
```

等待超时时 pending结果尚未到达，Root仍拥有完整请求/身份/原Task；宿主从Root Diagnostics追踪并由进程监督保有原Root，在需要时调用其BeginReconcile，不能用新的服务代覆盖原身份。Query新预算不改变原命令截止时刻。两个宿主的finally遇到cleanup异常，只附加错误，不覆盖原HostFailed/WaitTimedOut。示例 WaitAsync 的wall预算是宿主有限观察watchdog，运行语义期限由注入clock；不是靠实际sleep执行设备时序。

### 9.3 构造来源和最小工程

生产调用将设备/映射/权限/Profile作为已审工程配置传参，无隐式发现。离线最小夹具在 C1/C2 的同一 BCL Exe 测试工程内构造：

- Identity = `("sim-io","Fixture","Memory","1","sim","0.2")`；MappingRevision="map-1"，CapabilityRevision="cap-1"，Bus="sim"，Address="di/0"、"do/0"，AddressFormatVersion="fixture-v1"，SubChannel=null。
- DI "sensor.in"/Input：CanRead=true、CanWrite=false、CanSubscribe=true、CanPulse=false、DigitalSpec(ActiveLow)。DO "lamp.out"/Output：CanRead/CanWrite/CanSubscribe=true、CanPulse=false、DigitalSpec(ActiveHigh)。Filter None/Window零/阈值空，Revision="filter-1"，SourceReference="synthetic-fixture"；ReadAliasGroup=null，DisplayNameKey为 Signal.Sensor/Signal.Lamp，mapping source均为 synthetic-fixture。
- Capabilities Online、generation="sim-g1"、SamplingMode.Sequential、Simulation=true；ClockDescriptor `("sim-clock",1000,64,TimeSpan.Zero,"synthetic-fixture")`。两项 runtime EdgeSource=HardwareEvent、TerminalReadback=true，DO CorrelatedApplicationReceipt=true、QueryScope=Connection，DI该两项为false/None；HardwarePulse=false、脉宽null。不是实机能力。
- Simulator InitialObservations显式给sensor.in raw High=false、lamp.out raw High=false，其余字段依§3.4完整构造，Steps空；Simulator不内置产品信号名或默认初值。正常read以对应初值及虚拟clock当前read窗口生成Simulation观察，Source=Replay、adapter序号递增，逻辑sensor=true。相关命令receipt仅在传入能力声明与模拟Action脚本允许时生成；write改变对应地址模拟端子状态，pulse按虚拟clock安排Start/End并独立注入LosePulseEnd，不能让宿主wall wait伪造完成。InitialObservations地址须映射唯一且全覆盖可读fixture地址，缺值返回Unknown而非false。异常场景另传已hash Steps。ScenarioId/hash须非空，测试以固定fixture bytes和SHA-256产生；源事件时间改写为当前模拟域只用于模拟执行，原recording事件另保留，不标硬件事实。
- 授权测试端口实现 ISignalAuthorizationPort，显式认可测试Principal/动作/模式，输出同 clock 的到期 HostStamp；诊断端口只收有界快照。测试MemoryOnly时Journal=null。真实宿主不能引用此授权端口。
- 测试 RuntimeProfile为 synthetic软件夹具：MaxSignalsPerRequest=8、MaxSubscriptions=4、MaxPendingOperations=16、RawEventCapacity=16、RawEventBytes=65536、MaxRequestBytes=16384、IdempotencyBytes=65536、IdempotencyEntries=32、IdempotencyRetention=1分钟、MaxDiagnosticEvents=32、CleanupObservation=2秒、DisposeDeadline=2秒、ReadRetryDelay=零、ReadRetryCount=0、JournalPolicy=MemoryOnly；ProfileId="fixture-1"/Revision="1"/SourceReference="synthetic-software-test"。这些仅是**可复算测试输入**，不成为模块默认上限或现场目标。
- RegistryOptions Capacity=2、OwnerId="fixture-process"、SourceReference同上。每个Host用不同RootId、OwnerNamespace；独立Simulator，不构造第二物理连接。共享模拟用同一Owner工厂授两个不冲突lease，冲突测试专门使用相同DO。Host normal预算2秒、wall wait 3秒、cleanup2秒、wall cleanup3秒，仅该synthetic夹具；MaxAge=0，caller测试凭证引用，SignalIds=["sensor.in"]，输出new DigitalValue(true)与key="maint-1"。
- 虚拟clock推进与Host并行且由case调度器驱动，不能等BeginRead结束才推进其预算。C1最小调用不需要registry，直接构造MappingSnapshot后 ValidateMapping→ValidateValue→ConvertEngineeringValue→EncodeOutput；两消费者均引用同发布Core，不能复制函数。
- 无UI测试工程 net10.0、OutputType=Exe、ImplicitUsings=enable、Nullable=enable；无PackageReference，仅ProjectReference到本模块Core。所有模拟端口/virtual TimeProvider/BCL断言在该测试工程，DLL保持无设备SDK/UI。实现后的命令为 `dotnet build tests/Modules/device-signals/Asun.Modules.DeviceSignals.Core.Tests/Asun.Modules.DeviceSignals.Core.Tests.csproj` 和同路径 `dotnet run --no-build --project ... -- --suite C1`/`--suite C2`；不在本轮执行或创建工程。

## 10. 可选 WPF 控件与操作流

UI发布于独立 `Asun.Modules.DeviceSignals.Wpf`，宿主注入服务、Registry/Root Owner、语言/主题及readonly授权投影；无隐藏窗口初始化或产品数据库。参数与输出走同一Core验证。连接由宿主Root持有，关闭面板仅停止本面板投影，服务由宿主明确Close；独立维护工具退出时遵循§9的有界finally，不因Window.Closed丢Task。

### 10.1 1920×1080工作台构图和高级联动

只验证一个固定1920×1080 viewport，扣OS任务栏、窗口边框/标题与宿主状态栏，布局以**实际client区域**为准，不改显示设置、不多分辨率扩测。DockLayoutManager：上方紧凑设备身份/连接代/映射代状态带，左/中主Grid约client宽65%，右侧约35%为选中信号详情/映射draft/命令预览；下方可收合趋势与请求记录约client高25%，主表优先。尺寸是设计比例，真实布局按client限制；空间不足先收辅助趋势，关键身份/结果/下一动作不可藏入Flyout。信号非视觉模块没有伪影像区。

GridControl+TableView：固定逻辑名/方向/类型/值/质量列，水平扩展地址/raw/时刻/序号/代；ShowAutoFilterRow支持按质量/方向/名称筛选，多选用于查看/导出明确观察集合。选择行同时联动PropertyGridControl.SelectedObject只读详情、ChartControl/XYDiagram2D/LineSeries2D趋势、该信号原请求与回执。趋势按设备域分轨，缺口断线留空段，不连接伪连续曲线；raw/filtered不同系列，预览降采样标明且不能作为测量证据。

映射编辑为独立不可变draft副本，PropertyGrid编辑Spec参数并立即调用ValidateMapping/ValidateValue；字段旁定位错误；“应用映射”走宿主配置Owner审查、新修订、停接纳/排空/重新绑定链，不直接改当前服务。批量编辑仅同Spec类型的非地址/权限draft字段，明确逐项差异并验证；不提供批量隐藏输出。

高级联动：双击只定位详情，不能写DO；筛选后保留SignalId选择，避免行索引变化误写；请求记录点选高亮命令原Mapping/Connection及相关证据，并显示“历史映射”标签。布局保存/恢复调用SaveLayoutToXml/RestoreLayoutFromXml，仅宿主自建版本化受控文件，不接受现场未知layout反序列化。默认统一主题、8/16 DIP间距体系、对齐数值/单位、语义图标与文本双编码、有限状态变更动画；异常/Unknown无闪烁误导，无装饰覆盖关键信息。

### 10.2 角色任务与一条安全下一步

| 任务 | 输入与可见反馈 | 命令/恢复 |
|---|---|---|
| 操作员观察 | 当前质量、raw/工程值、采样来源/年龄、缺口、代；Unknown/Stale保留文字与原因 | “查看详情”，无写入入口；断线显示旧值仅供诊断 |
| 工程员调整映射 | draft、来源、旧/新极性/单位/换算差异及字段验证 | “验证映射”→“应用映射”；失败保持draft，当前snapshot不改变 |
| 授权维护单路输出 | 精确设备/通道/逻辑与raw值/脉宽/结束值/修订/期限预览 | “提交输出”一次确认；待回执禁重复提交，Unknown下一步“查询原请求” |
| 支持人员对账 | 请求身份、设备关联证据、端子回读、资源状态、厂商码 | 导出所选诊断；无重发、全复位或旁路按钮 |
| 关闭/取消 | 当前Owner与在途计数、工作状态/资源状态分别展示 | “停止接纳”；DrainUnknown显示“仍在等待资源归还”，由宿主监督 |

DO按钮不使用双击、网格复选框或Enter默认立即发送；确认区再次显示准确SignalId与当前代，显示授权禁用原因。协议ACK显示“设备已应答”，Applied显示“设备已确认应用”，端子一致显示“当前端子值一致”，不写“机构到位”。非关键细节可用FlyoutControl，关键输出确认/错误/Unknown不能仅悬浮可见。SuperTip用于限制、disabled原因和恢复，键盘也可获知。

### 10.3 控件端口、语言与真实验证门

```csharp
// 此块属于 Wpf 程序集，命名空间 Asun.Modules.DeviceSignals.Wpf。
public sealed record SignalLanguage(string CultureName, long Revision);
public interface ISignalTextPort
{
    SignalLanguage Current { get; }
    string Get(string resourceKey);
    event EventHandler<SignalLanguage> Changed;
}
public interface ISignalUiHostPort
{
    ValueTask<MappingValidationResult> ApplyMappingAsync(
        MappingSnapshot draft, CancellationToken ct); // 外部配置Owner审批后生效
    void ReportCleanup(CleanupObservation observation);
}
public sealed record SignalWorkbenchOptions(IDeviceSignalService Service,
    ISignalTextPort Text, ISignalUiHostPort Host, bool AllowMappingDraft,
    bool AllowOutputPanel, int PreviewCapacity, TimeSpan PreviewInterval);
public sealed class SignalWorkbenchControl : System.Windows.Controls.UserControl
{
    public SignalWorkbenchControl();
    public void Bind(SignalWorkbenchOptions options);
    public Task<CleanupObservation> UnbindAsync(TimeSpan observationBudget);
}
```

Bind只能一次有效绑定，Unbind后可重新Bind；配置有界/Interval>0，引用和事件在Unbind实际停止dispatcher投影后解除，预览Task/late Dispatcher item由控件宿主强持至归还。Bind失败不触发输出，无语言端口/host端口则拒绝；AllowOutputPanel只影响可见性，不赋权；ApplyMapping的审批/持久化原Task由宿主Root持有，控件取消只是停止等待。Unbind异常/超时归ReportCleanup，不伪装成功。控件自身无第二语言切换按钮；Changed触发后更新已有标题、SuperTip、字段错误/状态、culture数值与日期，保留SI单位和原协议码，不重建/重发命令。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Workbench.Title | 设备信号 | 設備訊號 | Device signals |
| Command.Submit | 提交输出 | 送出輸出 | Submit output |
| Command.Query | 查询原请求 | 查詢原請求 | Query original request |
| Mapping.Changed | 映射已变更，请重新绑定 | 對應已變更，請重新綁定 | Mapping changed. Bind again. |
| Observation.Stale | 旧值仅供诊断 | 舊值僅供診斷 | Previous value is for diagnostics. |
| Outcome.Unknown | 输出结果未知 | 輸出結果未知 | Output outcome unknown |
| Resource.DrainUnknown | 仍在等待资源归还 | 仍在等待資源歸還 | Waiting for resource release |
| Error.Permission | 无输出权限 | 沒有輸出權限 | Output permission required |

这是术语基线，全部IssueCode/SignalError ReasonCode、动态SignalId/DisplayNameKey、单位标题/权限/恢复文字都必须完整三语资源，不只翻译此表。缺key记录诊断并返回稳定key可识别fallback，不能空白或露出异常栈。Tab顺序身份→筛选→Grid→详情/draft→命令预览→确认/取消；Esc仅撤销未发送draft/确认，不发送EndValue。UIA暴露行身份/质量/禁用原因，颜色不作为唯一提示。真实WPF验收涵盖键盘/读屏、1920 client裁切、OS既有DPI、英文长度、运行中切语、theme、burst preview与close-race；本轮只规格，不声称已验证控件/截图/帧率。


## 11. 两视角的具体正常、边界与故障算例

合成值用于冻结软件行为，非客户公差/设备参数。第一视角怀疑每个事实来源和异步交错；第二视角是只引用DLL的外部消费者，检查不用知道内部实现就能构造、判错、恢复和归还。

| 场景/最小输入 | 怀疑视角处理与预期 | 外部消费者断言/恢复 |
|---|---|---|
| DI ActiveLow，raw High=false | 逻辑true，raw false保留；新鲜证据完整才Good/current | Convert结果DigitalValue(true)，不产生到板/许可 |
| 空mapping/Signals default；空SignalIds | Required/InvalidArgument，空API请求不调用设备 | 可定位字段，0 Acquire/Read/Write，不把空视为成功 |
| 多候选/歧义：两个SignalId写同地址但极性相反 | AddressConflict，即使名称不同也不允许最后写者胜出 | ValidateMapping失败，改明确Profile；read-only alias须显式声明且Spec相同 |
| AO raw signed16 100，Scale=.01/Offset=0、V、工程0..10 | 两步换算1.0 V；输入分辨率不改变raw | 工程值1.0，raw仍100，不另建视觉换算 |
| AO工程2.5 V，Scale=.001，raw signed16 0..10000，Resolution=.001/Origin=0、Exact、Tolerance=1e-12 | raw2500，Effective2.5；Tolerance是fixture不是客户精度 | Encode通过；2.5005 Exact网格拒绝，NearestToEven按声明并复验，不静默clip |
| Scale负值-.01、Offset=10，raw100 | 9 V，按声明排序域，不将负斜率误判不合法 | min/max端点可转换，越域拒绝 |
| raw ulong9007199254740993，analog转换double | 无精确表示，PrecisionLoss；Counter同数仍精确保留 | 不从rounded工程值算计数/放行 |
| raw/Scale含NaN、乘法溢出Infinity、非法枚举/bit width | NonFinite/InvalidTransform/BitWidthMismatch，工程值null | 无写副作用，字段错误稳定，无checked-double假通过 |
| Min/Max刚好命中、超过一个输入单位 | 边界包含，域外OutOfRange、不截断 | raw证据在外围保留，不把0/false当恢复 |
| Sensor weak/Blocked/NoSignal，无视觉图像 | adapter原因Invalid/Unknown，不猜遮挡面积/实物状态 | 上层决定重采样/人工处理，模块不生成质量或安全许可 |
| 同代重复seq+相同payload，或同seq不同payload | 前者只诊断不重复事件；后者ProtocolError | 不数二次触发，不更新缓存 |
| poll false→true，仅5ms间隔 | PollingDifference区间，不是硬件边沿时刻；false→false不证明无短脉冲 | RequiredEdgeSource.HardwareEvent在poll能力时Unsupported |
| 多路Sequential采样不同tick；要求DeviceSnapshot | 能力不支持时发送前Unsupported | 不把一次API响应当一致快照；原时间窗逐项返回 |
| ReceivedAt刚更新，但设备缓存age未知 | StaleObservation，收到新包不等于新样本 | 保留旧值诊断，禁止current前置条件通过 |
| 数字抖动false,true,false，Window=5ms，样本间隔未知 | pending重置；filtered Unknown/未提交，raw三项保留 | 不证明中间持续stable；硬件连续事件与poll投影能力明确区分 |
| Counter65535→0，16bit、同epoch、无缺样、最大可能增量1且证据有效 | delta1；失epoch/最大增量可能>=65536则Discontinuous | 保留raw/bitwidth，unknown delta绝不0；不发clear |
| Latch=true CaptureId7两次，或CaptureId缺失 | 同capture去重；缺capture只表示锁存值 | 不把true重复采样数成触发，Read不清锁存 |
| 新映射改极性，旧callback迟到 | 旧事件隔离，不能更新新代缓存/filtered状态 | 重新绑定新Root；历史仍按原极性 |
| 同key100并发/不同RequestId同payload | 一个original命令/Task，返回原RequestId | Execute恰好1；不同payload额外0次，IdempotencyConflict |
| ACK丢失后端子当前true，先前也true/他人写/ABA | TerminalReadback独立，仍Unknown | Query原身份；NotFound/无关联不能重发/称Applied |
| 入队时有权，发送前权限撤销 | Owner重新认证失败，NotSent | 0物理send，UI不能通过保持已启用按钮绕过 |
| 三路batch第二路拒绝，StopBeforeNext | 一路真实结果、第二拒绝、第三NotExecuted | 数量=3顺序固定；未知/非Applied不能全批成功/自动rollback |
| pulse已有StartApplied=true，End丢证据 | EndApplied=null、Unknown，不测伪宽度 | 不执行补偿false、不新键重发；原Owner对账 |
| queued cancel / send内cancel / read timeout | 分别NotExecuted / Unknown / TimedOut+资源未定 | cancellation不证明已撤销，原Task仍强持 |
| Create尚未完成时Host异常finally/cleanup超时 | Root在Factory前登记；DrainUnknown保留slot，late lease立刻归还 | 无Root/Task遗失，无第二Factory或租约交叉，processRegistry继续监督 |
| Subscribe延迟返回，Window已经关闭 | 晚订阅产物由原Owner Stop→排空→归还 | 不重启UI、不再发布当前值；未确认归还仍DrainUnknown |
| native/read callback尚在途，TryComplete已完成 | 禁止close/free buffer，继续等待真实退出 | queue完成不能替代callback计数0，DrainUnknown不成功 |
| 事件queue满或消费者慢，诊断queue也满 | 独立gap计数+Overflow，当前/filtered降级，有限拒绝 | 无silent drop，驱动callback不阻塞，内存不无界 |
| 未决幂等记录满/TTL到期 | 不驱逐Unknown/墓碑，拒绝新输出 | 达到budget可判ResourceBusy，不能用另一namespace绕过 |
| durable意图写失败/已send后回执落盘失败 | 前者NotSent，后者设备结果保留但PersistenceUnavailable | 不声称已持久化/恰好一次，恢复只查原ID |
| 重启/设备断电/共享两lease重连 | 旧代失效先排空，不重放，未决Unknown | 两消费者一个退出不关闭另一个，故障失效由唯一Owner |
| 升级/回退保留旧mapping/event/包 | 离线验证→停接纳→排空→Owner切换→新代重新授权 | 旧Unknown先对账，不能按旧包重新解释新记录或清原配置 |
| 无UI与UI同输入，运行中切语/关闭 | 核心结果相同，语言只投影，不重发 | Core不加载WPF，Unknown显示文字，UI任务实际退出才解绑 |

“遮挡/多候选”在本模块只对应不可观测/映射歧义，不制造视觉算法。“弱信号”只转发设备诊断/域外事实，没有传感物理阈值时不推工艺异常。

## 12. 逐切片测试与验收设计

### 12.1 BCL Exe测试工程与有限执行

C1/C2/C3测试全部 net10.0 BCL Exe，无PackageReference，仅Core项目引用。case内断言用明确比较/throw；退出0仅当**全部必需断言和资源最终断言**执行完且通过，无跳过、无“caught异常即PASS”、无超时后继续总绿。未知测试/缺suite/fixturehash不符/不完整结束/任意断言失败/cleanup不明都非0。输出仅stdout结构化case名/断言结果/错误/资源计数，既有CI消费者收集，不提前生成第二报告文件。

受控软件夹具 case期限10秒、suite120秒、测试进程wall watchdog180秒。这是用户本轮指定测试预算，非生产超时。case的业务/Timer/Deadline由自制TimeProvider推进；wall watchdog独立Stopwatch/真实进程时钟，不能也用同虚拟clock，否则deadlock无法终止。case watchdog只使测试失败，不声称resource Released；测试驱动的真实资源仅托管假端口，返回非0仍打印原Root/Task/late产物保有量。运行命令支持 `--suite C1|C2|C3 --case <stable-id>`，省略case运行该suite全部必需项；所有suite由外部runner分别执行，不让一次120秒suite绕过180秒进程期限。

### 12.2 必需断言位置

| 切片 | case前缀与必需断言 | 适用不适用 |
|---|---|---|
| C1 值/映射/编码 | Map-* 空/重复/alias/地址结构/修订/能力/过滤；Value-* 全类型单位/位宽/有限性/边界；Convert-*负斜率/非有限/精度；Encode-*网格round-to-even/逆变换/不截断；相同输入重复等值/无副作用；rollback旧snapshot不重解释 | 无连接/线程/取消/排空；这些不适用，另在C2，不造native gate |
| C2 观察/托管服务/Simulator/Replay | Open-*失败产物归还；Read-*同域/current/缺项/快照/时间回退；Sub-*硬件与poll区别/重复/乱序/overflow/慢reader/late stop；Filter-*gap/初值/窗口/阈值/版本；Counter-*64位/多圈/epoch；Close-*cancel/timeout/DrainUnknown/late acquire/late subscription；Root-*factory前登记/容量/双实例/共享lease | 不证明硬件边沿完整性/精度；Replay只读拒绝写；设备能力fake明确Simulation |
| C3 命令/journal | Idem-*相同/冲突/并发/TTL墓碑/满；Auth-*撤销/期限/模式；Write-*ACK/ABA/关联/未知；Pulse-*双沿/End未知/不补偿；Batch-*逐项/stop与continue；Journal-*提交前/后失败/崩溃窗口/原查询；Host-*两个finally/原错误不被cleanup覆盖/Root强持/late归还 | 全用假Owner/Journal，设备输出不执行；跨进程精确一次不适用且不得宣称 |
| W1 控件 | 绑定/解绑/late Dispatcher/原Owner、Grid联动/draft/批预览/键盘/UIA/三语/主题/viewport/preview预算；无UI行为等价 | 必须真实WPF，本轮未跑；截图/合成不能替代运行交互 |
| A1 真实Adapter | per-value status/地址/端序/官方时序/共享锁/句柄/断线/恢复；硬件输出HIL、时宽、回读、持久化查询和安全链Owner | 厂商SDK实现暂不纳入，具体设备Profile/HIL门单独 |

复用§11输入输出，不另写同义测试清单。关键并发交错按gate精确触发，不用Task.Delay“碰运气”：pre-register→acquire late、pre-auth→policy revoke、send-start→cancel、callback-enter→close、lease-return→dispose、intent-commit→crash、response-receive→Store-fail。每个case最后核Root槽、Task、lease、callback、queue字节和订阅回到基线；故意DrainUnknown的case核Owner仍在/无新admit，并在放行late gate后追加核归还，不能只验证Unknown枚举。

### 12.3 两消费者接收和HIL范围

观察/采集尝试Owner与维护工具是两个明确复用计划，§9从公开构造器/工厂完成最小调用。C1复用各自mapping，C2/C3独立配置、授权/取消/错误投影、同publish DLL、无核心复制；共享Owner测试open计数1、一个消费者stop不关另一lease，重复DO写Owner在send前拒绝。接口接收还须真实消费者Owner审核，不以示例存在冒充已接收。

HIL另取具体型号/firmware/官方SDK、真实DI/DO电气极性/AI校准域/锁存/脉冲min-max/时钟频率误差/共享连接/设备重启查询证据；现场验收参数由设备与客户Owner给出，不能由模拟夹具值推定。安全链保持硬件/PLC Owner，本模块不出安全许可。缺HIL只阻断A1和对应生产集成，不阻断纯托管规格与模拟测试设计。

## 13. BenchmarkProfile、预算和可观测测点

测量方法冻结，目标值待真实消费者Profile采纳；不写无来源P99/资源通过。BenchmarkProfile是实现测试中的不可变BCL输入记录，至少包含 ID/Revision/SourceReference、构建代码快照与.NET/Adapter版本、OS/CPU/RAM、带hash输入、通道/信号类型分布、raw尺寸、mapping大小、并发/到达/burst/订阅消费模型、RuntimeProfile完整预算、fault/reconnect节奏、ColdSampleCount/WarmupIterationCount/MeasuredSampleCount、每项target及其source。全部计数正、warmup可0；缺target记TargetPending而非false PASS。序列化是测试consumer私有输入不提升产品Contract。

冷测每个样本新进程/新Root；纯C1无缓存。外部OS/设备/Store缓存不能清时记录状态不称冷。热测固定warmup后固定样本数，失败/拒绝/超时/缺失单列且保留慢样本；不自适应停止或选最快。用单调clock记录真实耗时（性能用真实TimeProvider，虚拟clock只功能测试）。样本升序，nearest-rank：Pp=`sorted[ceil(p*n)-1]`，p=.50/.95/.99；n>0，单位统一ms，记录n与原值来源。吞吐固定窗口内完成有效操作/秒，拒绝/未完成/Unknown不计完成，单列队列等待。冷/热不同Profile不能合并。

C1测 ValidateMapping/Value/Convert/Encode 的端到端时间、分配/GC与mapping规模；C2测从入队至正确观察发布、producer→消费延迟、过滤新增延迟/缺口、subscribe/late-stop/真实排空；C3测授权/登记/Store/Owner排队/send/证据/查询分层及总等待；W1仅测预览投影/dispatcher积压/交互响应，设备时序/HIL另测，禁止把软件低延迟当脉宽精准。每轮CPU、工作集/private bytes、托管分配/GC pause、native/lease/句柄、queue条数与字节峰值、诊断丢失、在途Task/Root槽/Idem tombstone、取消与从停接纳至实际Released的排空时间均报告。超时只记未完成，不能强杀后计“排空耗时”。

软件夹具§9.3预算可用来验证**上限执行**，不代表客户性能目标。达到预算停止新接纳，不扩容、不删除Unknown、不silent-drop。mapping和值纯运算大输入在C1可测到宿主批准的规模；并行C1共享输入不可变、无全局状态，输出等价。长期运行窗口/检查间隔均Profile给出，复用已有测试consumer；任何Root/lease/callback/queue/Idem计数无法解释单调增长、序号水位回退或旧代串入都失败，不通过重启掩盖。


## 14. Journal、规范命令与审计

### 14.1 单一Journal端口

```csharp
public enum JournalPhase { Intent, SendAttempt, Receipt, Lookup, ResourceReleased }
public sealed record SignalJournalEntry(string EntryId, string OriginalRequestId,
    IdempotencyIdentity Identity, ImmutableArray<byte> CanonicalPayload,
    string PayloadHash, JournalPhase Phase, DateTimeOffset AuditAt,
    string ConnectionGeneration, string MappingRevision,
    CommandResult? Result, SignalError? Error);
public sealed record JournalAppendResult(bool Committed, string? CommitId,
    ImmutableArray<SignalError> Errors);
public sealed record JournalLookupResult(CommandLookupStatus Status,
    ImmutableArray<SignalJournalEntry> Entries, ImmutableArray<SignalError> Errors);
public interface ISignalOperationJournal
{
    ValueTask<JournalAppendResult> AppendAsync(SignalJournalEntry entry, CancellationToken ct);
    ValueTask<JournalLookupResult> FindAsync(IdempotencyIdentity identity, CancellationToken ct);
}
```

Journal注入由宿主/存储Owner实现，Core不建数据库、不藏文件、不维护第二业务库。EntryId同内容重复append幂等，冲突报PersistenceUnavailable/ProtocolError；Committed必须实际存储提交确认，不能用“入内存queue”当durable。Append/Find原Task也由Root强持，提交超时Unknown会迟到，不自动再append不同ID来掩盖；意图未知时不发送，晚提交后只追加未发送事实。

DurableBeforeSend顺序：提交Intent→提交SendAttempt→发送→Receipt→Lookup/ResourceReleased追加。SendAttempt只表示**可能即将/已发送**，崩溃后不能判断NotExecuted；关联设备证据才确定Outcome。Receipt落盘失败不改变已知设备事实，但PersistenceUnavailable单列；日志顺序/commit属于Store，设备结果属于Owner。恢复读取原意图/代/规范payload并查询设备原ID，不重放pending queue；跨进程memory-only缺记录必须Unknown，不能因Store NotFound允许重发。Journal本身不授任何设备安全权限。

### 14.2 编码、hash与预算

模块内规范payload仅用于幂等相等/hash与测试复算，**不是平台网络/数据库Contract**。字符串不做Unicode归一化，以UTF-8无BOM严格编码，孤立surrogate拒绝；数值bits不经culture文本。字段顺序固定，小端二进制：
- 前缀4 bytes `44 53 30 32`（DS02），action byte（Write=1、Pulse=2）；每个字符串为 uint32 byte length +原UTF-8。固定依次DeviceId、OwnerNamespace、Key、SignalId、MappingRevision、CapabilityRevision、OriginalConnectionGeneration、PrincipalId、PolicyRevision。
- Write：value tag byte（Digital=1、Analog=2）；Digital一个byte 0/1。Analog写EffectiveValue的IEEE754 binary64 bits，再unit字符串；-0 canonical为+0，NaN/Infinity拒绝。原RequestedValue另以同规则写入，确保改变用户意图不被量化掩盖；Digital两值都写。接着RequireApplicationEvidence byte 0/1。
- Pulse：active byte、end byte、width的Int64 TimeSpan ticks（100ns），不经浮点。只支持逻辑Digital，不写未定义AnalogPulse。
- 最后AuditNotAfter存在标记byte，存在则UTC ticks Int64；空无后续字段。预算不进入payload，因为首次接纳固定；RequestId不进入，因为重复调用可返回原RequestId。
- hash是上述全bytes SHA-256的小写64字符hex；原bytes与hash同时保存，hash相等仍比较bytes。同一payload需要缓存/保存真实CanonicalPayload，不能只hash。
- DTO预算采用规范payload byte count + UTF-8诊断/身份字符串 + 每个固定字段实际固定编码宽度；队列raw值编码依次tag/digital或integer位宽/数值bits/source/time/seq/代，按同长度前缀与固定宽度实际byte计数；为了不把对象开销漏算，另计托管实际allocated bytes峰值测量并留宿主明确余量。逻辑byte预算不是CLR精确内存上限，不能宣称MaxRequestBytes涵盖对象头；ResourceLimits同时限制条数与逻辑字节，Profile物理memory目标另由Benchmark验证。

输入Items/字符串集合大于cap先检测计数，再严格计字节，避免为拒绝请求先构造巨型编码。int/long大小累加用checked，溢出InvalidArgument/ResourceBusy；错误输出也受MaxDiagnosticEvents预算，保留稳定总数与first错误，不能海量异常字符串扩大内存。外部厂商协议的CRC/端序由Adapter独立实现，本payload hash不校验硬件报文。

### 14.3 审计和事实保留

审计含OriginalRequestId/Identity、mapping/capability/connection代、Outcome与ResourceState分别记录、raw/工程值、时间来源、厂商码、授权DecisionId/Policy、Profile修订、queue水位与gap、查询/只读重试次数、可能副作用、JournalCommitId。credential仅引用不输出秘密。MessageKey与参数是投影，原码/原payload不可由翻译更改。Unknown之后得到相关Applied/NotApplied只append关联证据，不删除原Unknown。保留期/脱敏权限由宿主，未知请求不能因普通日志到期而丢唯一对账入口；硬盘不可用不将设备事实改为PASS/FAIL。

## 15. 独立发布、迁移、版本回退

Core发布 `Asun.Modules.DeviceSignals.Core` 包，含唯一Module API/纯函数/托管服务及无设备Simulator/Replay工厂，BCL依赖，无SDK/UI/产品配置。WPF独立发布 `Asun.Modules.DeviceSignals.Wpf`，引用Core和本机DevExpress25.2.3；各具体Adapter另包，由已批准的设备Owner部署，当前不生成猜测性厂商包。没有独立contracts真实消费者之前不再拆第二Contracts DLL。

发布记录复用既有release消费者，包含代码快照/包hash、net10.0/Module API版本、对应Profile/schema/adapter版本、公开能力限制、测试suite版本和已执行结果、HIL/WPF范围、旧包/config/mapping/Journals的可回读性。不得修改来源snapshots或客户交付项目，不能把旧INI默认带入。

升级先离线回放+两个消费者→新包Shadow只读且未夺写Owner→停止旧新接纳→原Owner排空并对账Unknown→保存旧修订/原Task/journal查询入口→独占Owner切换→新能力/代/授权→显式开放受控输出。新旧包同时运行只允许独立无冲突通道或只读投影，不能各开同设备连接。回退同序恢复旧包/原配置，历史按原版本读；不能跨Major忽略新字段。新payload不能旧版本解释时保留新Reader查询旧事实、不重发。切换/回退失败保持Unknown/DrainUnknown并由原Owner监督，不重启进程伪造复位。

## 16. 已查证依据与主/备路线

### 16.1 非视觉核心、HALCON 26.05 I/O Adapter候选

本模块Core主路线是 .NET托管强类型契约/确定性换算/有界Owner和注入设备端口；它处理信号事务，HALCON视觉算子/ROI/AI不适用。真实设备主路线由已有唯一控制器Owner注入官方设备协议typed sub-port；备用只在具体设备HALCON I/O interface适合且证据明确时采用HALCON 26.05 I/O Adapter内部路线，均不把SDK句柄暴露Core。

已直接核对本项目26.05.0.0官方HTML：
[open_io_device](../../../halcon算子手册/operators/open_io_device.html)、
[query_io_device](../../../halcon算子手册/operators/query_io_device.html)、
[open_io_channel](../../../halcon算子手册/operators/open_io_channel.html)、
[read_io_channel](../../../halcon算子手册/operators/read_io_channel.html)、
[write_io_channel](../../../halcon算子手册/operators/write_io_channel.html)、
[control_io_device](../../../halcon算子手册/operators/control_io_device.html)、
[control_io_channel](../../../halcon算子手册/operators/control_io_channel.html)、
[close_io_channel](../../../halcon算子手册/operators/close_io_channel.html)、
[close_io_device](../../../halcon算子手册/operators/close_io_device.html)。

open返回设备handle后打开通道；read/write的每值Status=0才该值成功，其余由interface定义，算子整体返回2不能证明所有值成功。control action接口特定，不能猜clear/pulse/复位通用语义。close_channel/close_device修改handle且跨线程需同步；close_device会关闭所属通道/释放缓冲，因此共享lease不得自行调用。设备接口参数、状态映射、资源排空、精度/HIL仍在A1。

用户已明确HALCON26.05算子均经 `ImageLibDotNet.cv2` 调用，不再查“封装是否覆盖I/O算子”、授权/依赖准入，不直连HOperatorSet/halcondotnet.dll，不扫描AsunImage内部。仅真实C#参数类型/重载/封送歧义时读取公共签名或消费项目编译；此缺口仅限实际Adapter。HALCON路线不选为Core事实Contract、不默认替代既有Motion共享Owner；软件Task.Delay脉冲、不相关回读、传输层写重试也明确不选，理由见§5。

具体Adapter比较在同代表设备记录/故障注入下验证正确性、误接受/误拒绝、相关证据、端到端P50/P95/P99、资源/排空及参数可复现性；非视觉不造图像算法比较，不用模拟证明实际时序。参数建议策略见§8，无自动生产参数改变。

### 16.2 固定源码与测试，只移植思想

| 来源/版本与真实查阅 | 可迁移优点 | 明确反例/不照搬 |
|---|---|---|
| [dotnet/iot GpioController.cs](https://github.com/dotnet/iot/blob/d84c940755444c63697d5fb89135ab973df46597/src/System.Device.Gpio/System/Device/Gpio/GpioController.cs)，commit d84c940755444c63697d5fb89135ab973df46597（2026-10-08）；[测试](https://github.com/dotnet/iot/blob/d84c940755444c63697d5fb89135ab973df46597/src/System.Device.Gpio.Tests/GpioControllerSoftwareTests.cs)；net8.0，MIT | 注入driver、pin模式/能力、callback注册/注销、wait cancel、mock driver资源归还 | Write非Output静默return，测试WriteInputPinDoesNotThrow固化该行为，本模块明确拒绝；默认板卡发现与Dispose关闭全部pins不适合共享lease。OpenTwiceGpioPinAndClosedTwiceThrows/UsingLogicalNumberingDisposesTheRightPin/CallbackOnEventWorks/WaitForEventAsyncFail与Success提供反例思想，不提供工业幂等/HIL/精确脉宽 |
| [NModbus ModbusTransport.cs](https://github.com/NModbus/NModbus/blob/baddfca14e2852373a238aee8d234d6627983b20/NModbus/IO/ModbusTransport.cs)，commit baddfca14e2852373a238aee8d234d6627983b20（2026-06-30）；[测试](https://github.com/NModbus/NModbus/blob/baddfca14e2852373a238aee8d234d6627983b20/NModbus.UnitTests/IO/ModbusTransportFixture.cs)；MIT | UnicastMessage锁住Write/ReadResponse，ValidateResponse校功能码/从站；ACKNOWLEDGE再读而非再发 | timeout/IO/socket/format可resubmit，busy配置可能无界；Retries测试断言Retries+1写，不能用于脉冲/写入盲重试。UnicastMessage_TimeoutException/Retries/AcknowlegeSlaveException/SlaveDeviceBusySlaveExceptionDoesNotFailAfterExceedingRetries/ReReads_IfShouldRetryReturnTrue和ValidateResponse_MismatchingFunctionCodes/SlaveAddress是具体反例 |
| [.NET Channels官方](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels) | bounded/Wait、TryWrite admission、完整producer/consumer lifecycle | Wait模式TryWrite=false需独立Overflow，Drop*会丢数据；AllowSynchronousContinuations=true可能writer执行reader；TryComplete只关写入，不能证明callback/consumer已排空 |

已读两个仓库项目和LICENSE，不复制代码、不引入生产依赖；dotnet/iot库target net8.0，GenAPI为构建依赖，其版本未沿props追踪，因此不作为生产依赖依据。NModbus库targets net46/netstandard1.3/netstandard2.0/net6.0，所读库csproj无PackageReference；测试net4.6、xunit2.4.2/Moq4.17.2/TestSDK17.6.2/TraceSource4.3.0，仅说明旧测试工具链不能照搬。本模块采用本轮指定net10.0 BCL Exe，不下载这些库。固定源码/测试思想不足以证明生产可靠，实际模块必须执行§12自己的断言。

DZ-XVision已核hash事实保持§2.1（快照manifest tree SHA-256 `a3649338762b234537d185d18496fcd438ba91eafd06b8d817ebee4c5a5ceae8`）；未重复审查原件。AsunControl已只读确认TcpClientEx.cs/TcpCommon.cs具有异步连接/取消/事件清理模式，没有可采纳DI/DO/AI/AO实现；WinForms页面/私有TCP事件/默认参数不复制。

### 16.3 DevExpress25.2.3官方本机API证据

本轮无可调用dxdocs端口，网页403；复用本机官方XML文档核验结果，没有下载/换版本。文件位于 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/`，对应DLL FileVersion=25.2.3.0：

| 官方XML | SHA-256 | 已核验API |
|---|---|---|
| DevExpress.Xpf.Core.v25.2.xml | cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196 | SuperTip.Items、SuperTipHeaderItem/SuperTipItem；DevExpress.Xpf.Editors.Flyout.FlyoutControl及基类FlyoutBase的OpenOnHover/PlacementTarget |
| DevExpress.Xpf.Grid.v25.2.xml | 7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd | GridControl、TableView、ShowAutoFilterRow |
| DevExpress.Xpf.Docking.v25.2.xml | b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f | DockLayoutManager、LayoutPanel、SaveLayoutToXml(string)/RestoreLayoutFromXml(string)及非可信反序列化警示 |
| DevExpress.Xpf.PropertyGrid.v25.2.xml | 0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9 | PropertyGridControl.SelectedObject |
| DevExpress.Xpf.Charts.v25.2.xml | 2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0 | ChartControl、XYDiagram2D、LineSeries2D |

资料核验只决定§10控件组合，不声称已编译/真实WPF验证。未核IsOpen等未用属性不猜；实现W1若新增具体属性再按本机匹配XML/dxdocs核签名，非重复依赖准入。

## 17. 逐切片 DEV-GOV-010 §3.1 六项定位和状态

六项顺序固定：①职责/第二消费者；②精确Module API/单位/状态/所有权；③无UI无SDK注入；④正常/反例/取消/排空/回退断言；⑤Benchmark方法/阈值来源；⑥唯一路径/允许禁止/调用顺序。2026-10-10 主控已按本页内容复核接收 C1/C2/C3 六项规格，三者状态为 `ModuleCoreImplementationReady`；只覆盖下表所列托管范围，不包含真实 Adapter、Store、平台集成或生产资格，不自动启动代码开发。

W1 的角色流、PageContract、公开控件 API、恢复、三语及测试/性能方法已由主控内容接收。按 [DEV-GOV-010 §3 与 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，`ImplementationSpecificationReady` 还要求受影响的正式平台 Contract/Schema、真实公共程序集签名、WPF/Golden-Replay/性能资格关闭；§3.1 的无 UI 核心例外不适用于 W1。真实 WPF 资格未执行，平台接入绑定亦未接收，因此 W1 保持 `PreparationIncomplete / NotReady`，不能仅凭规格接收提升。这里是明确资格/集成门，不再把已接收的控件内部规格列为欠账；本轮不扩大范围开展真实验证。

| 切片 | ① | ② | ③ | ④ | ⑤ | ⑥ | 状态 | 剩余门 |
|---|---|---|---|---|---|---|---|---|
| C1 mapping/value/encode | §1/2/9 | §3.1～3.3/8 | §3.3/9.3 | §11/12.1～12.2 C1 | §13 C1 | §18 C1 | `ModuleCoreImplementationReady` | 规格已接收；后续实现前绑定权威代码快照；设备/WPF/平台序列化不阻断本托管切片 |
| C2 托管观察/过滤/计数/Owner与模拟Replay | §1/2/9.1 | §3.4/4/5.1/5.4/6/7/8 | §4.3/7.2/9 | §11/12 C2/Root/Host | §13 C2 | §18 C2 | `ModuleCoreImplementationReady` | 同域/事件/late归还/两Host规格已接收；真实硬件频率/连续性/共享Owner仅A1，本状态不含设备资格 |
| C3 托管命令/批/pulse生命周期/Journal端口 | §1/2/9.2 | §4/5.2～5.4/6/7.1/14 | §7/9.2 Journal注入 | §11/12 C3 | §13 C3 | §18 C3 | `ModuleCoreImplementationReady` | 仲裁/规范payload/Journal/恢复规格已接收；仅托管生命周期及假Owner/Journal，不含真实发送、durable Store、设备查询/HIL |
| W1 可选WPF控件 | §10.1～10.2 | §10.3/4/6 | Core独立，WPF只投影 | §10.3/11/12 W1 | §13 W1 | §18 W1 | `PreparationIncomplete / NotReady`；规格内容已接收 | DEV-GOV-010 §3/§3.1 的真实WPF资格及受影响平台接入门未关闭，不能标 `ImplementationSpecificationReady` |
| A1 具体Adapter/平台集成 | §2共享Owner | §7.1/7.3/16.1 | §7.3及§9两Host，注入sub-port无SDK泄漏 | §7.3增量反例/§11/12 A1 | §13/16.1 | §18 A1边界 | 通用软件适配设计已闭合并由本永久原会话完成内容审核；具体接入 `PreparationIncomplete / NotReady` | 未提供具体型号的协议/地址解析规则/SDK公共签名/物理时序，以及平台Owner/Schema绑定；Owner见下表。不再因旧总控接收流程列为内部设计欠账 |

已冻结mapping/时钟证据/Owner根/原Task/late资源/授权/send/幂等/payload/批量/脉冲两沿/过滤/控件组合；C1/C2/C3/W1 的**规格内容接收已完成，实际实现及验证未执行**。A1及真实集成仍按影响范围等待物理域、时宽、频率误差、Profile目标/现场权限安全政策、官方协议与真实接入/Store/WPF资格。没有客户性能阈值可报告TargetPending，不阻断C1测量方法。

2026-10-11 未决范围分类（文档设计、实现、运行及物理资格分别判断）：

| 未决切片/范围 | 内部软件设计 | 精确缺项与 Owner | 影响阶段 |
|---|---|---|---|
| A1 通用适配契约 | 已闭合，原会话按§7.3定向审核完成 | 无剩余通用软件设计决定，不等待总控内容审核 | 文档准备完成；不表示厂商代码存在 |
| A1 具体型号接入 | 公开端口/工厂与binding/原Task/恢复规则确定 | 型号/firmware及官方协议、地址格式canonical规范/边界/字节序、SDK公共方法/线程与实际stop语义由设备接入Owner提供；实际电气/量程/时宽/时钟误差/设备持久化查询由设备/HIL Owner核定 | 只阻断对应厂商实现与物理资格；提供事实后在本原会话补型号映射，当前厂商SDK实现不纳入 |
| A1 平台组合绑定 | 单连接/写Owner、typed lease、授权、Journal注入及两Host顺序确定 | 具体部署的组合根/设备Owner身份、配置与凭证来源由宿主集成Owner选定；外部Schema编码与宿主事实映射由平台Contract Owner采纳，真实Journal的提交/恢复证明由Store Owner提供 | 对应平台集成及真实持久化门；不是重做本模块DTO/生命周期设计 |
| W1 | 既有角色流/公开控件/宿主投影/三语/键盘/UIA/有限收尾指导保持，无新增内部设计欠账 | WPF实现与1920×1080实际client、键盘/UIA/语言切换/close-race运行证据由本模块实现与UI验证Owner执行；真实宿主/语言/主题装配由宿主集成Owner绑定 | WPF代码/运行与产品接线资格仍未执行，保持NotReady，不笼统列为需要再设计 |
| C1/C2/C3实施落地 | 既有六项准备接收保持 | 权威代码快照与具体实施派发由代码仓库/实施Owner绑定；既有BCL Exe断言、两个Host、Golden/Replay与Benchmark由本模块实现/验证Owner执行；物理目标数值由真实消费者Profile Owner提供 | 未创建产品/测试工程，未执行build/run/性能，不影响已确认的规格准备 |

总控仅调度、接收上述状态和转发依赖；本模块后续执行、内容审核、修复、验证继续由本登记原会话承担。A1实现和生产未就绪不等于其通用软件设计未定义，缺少实测亦不自动退回重新设计。

### 17.1 全部已批准范围的文档准备结论

2026-10-11 本永久原会话收口结论：在当前批准的通用 DI/DO/AI/AO、观察/订阅、时间/质量、计数/锁存观察、过滤投影、受控写入/硬件pulse生命周期、非原子batch、幂等与Journal端口、共享lease/有限恢复、Simulator/Replay、双无UI消费者及可选WPF工作台范围内，**可决定的软件设计欠账已闭合**。C1/C2/C3既有六项规格接收、W1确定指导和已有研究/反例保持，未重复审算；本轮仅补A1通用适配边界实际缺口并完成原会话内容审核。不是最后任务completed代替全部范围判断，也不将该文档结论改写为整模块ImplementationSpecificationReady。

判定依据：职责/真实复用计划与禁止领域见§1/2；唯一公开类型、数值/单位/转换及时间事实见§3；工厂/注入/授权/原Task/进程Owner见§4；写/批/pulse/计数/过滤、错误与有限取消/恢复见§5/6/7；参数来源、离线建议与版本见§8；两个Host及完整finally、可构造软件夹具见§9；角色流、DevExpress25.2.3组合/布局/键盘/UIA/三语与恢复见§10；合成Golden期望/正确性与异步反例、BCL Exe测试计划及Benchmark负载/资源/阈值来源见§11～13；Journal/规范命令/审计、发布回退及固定官方/源码依据见§14～16。核心是非视觉事务，无坐标/ROI/图像算法；HALCON26.05/cv2仅为具体Adapter的有条件备用路线，不缺一套视觉算法，也不把安全链/工艺放行纳入批准能力。

§8建议是离线工程候选与审核流程，不新增自动参数生成器或生产自动应用API；实际采样/过滤/量程/时宽等参数均来自明确Profile并在调用前冻结。无客户物理值时按§17指定Owner等待事实，不让实现者随意选值。具体厂商SDK实现、软件两次写的精确脉冲、通用clear/reset、安全许可和制程判定不在当前批准实现范围，不以扩展这些内容证明指导“完整”。

剩余项仅为§17表内的具体型号事实与公共SDK绑定、宿主/平台Contract/真实Store绑定、权威代码快照与实际实施，以及软件/真实WPF/设备/HIL/Golden-Replay/性能/现场资格证据；各项Owner和受阻阶段已经逐项定位。产品/测试工程、真实运行及物理客户资格均未执行。本轮达到文档收口准则即停止，不继续全审、造过程材料或自动实施。


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

## 18. 唯一工程、范围和有限自审

### 18.1 预定工程路径，当前不创建

| 切片 | 唯一码/测试位置 | 允许内容 |
|---|---|---|
| C1 | `src/Modules/device-signals/Asun.Modules.DeviceSignals.Core/Asun.Modules.DeviceSignals.Core.csproj`；`tests/Modules/device-signals/Asun.Modules.DeviceSignals.Core.Tests/Asun.Modules.DeviceSignals.Core.Tests.csproj` | §3.1～3.3/8的纯类型/映射/换算/编码，BCL Exe C1断言 |
| C2 | 同一Core/Tests，避免第二套DTO/Simulator工程 | §3.4/4/5.1/5.4/6/7的托管服务、辅助纯函数、模拟/Replay及C2/Host断言 |
| C3 | 同一Core/Tests | §5.2～5.4/14命令生命周期/Journal端口、假Owner/Journal C3断言；真实Store实现不在Core |
| W1 | `src/Modules/device-signals/Asun.Modules.DeviceSignals.Wpf/Asun.Modules.DeviceSignals.Wpf.csproj`；`tests/Modules/device-signals/Asun.Modules.DeviceSignals.Wpf.Tests/Asun.Modules.DeviceSignals.Wpf.Tests.csproj` | §10可选控件，同核心校验/命令；本机DevExpress引用与真实WPF测试 |
| A1 | 通用接口及binding约束在同一Core，定向反例在同一Core.Tests；具体厂商工程未纳入，型号接入任务再绑定唯一路径 | §7.1/7.3通用契约/绑定/原Task/恢复与§16证据已确定；不凭目录模板创建厂商SDK工程 |

全部项目尚未在本任务创建；后续实现先绑定权威代码仓库/分支或可审计代码快照，当前目录无.git不据旧HEAD开工。禁止产品Shell/Domain/Integration、其它模块src/tests、客户项目、AsunImage内部、DevExpress依赖替换、refs原件和共享文件修改。当前文档任务仅修改本DEVELOPMENT-GUIDE.md，不创建脚本、manifest、报告或测试。C1/C2/C3 的六项规格已接收，后续只在获派实现任务时进入各自托管范围；W1/A1保留§17门。逐切片接收不能授整模块Ready。

### 18.2 两轮定向自审边界

第一轮怀疑视角：按§11检查事实来源、数值/单位与double精度、采样/接收/边沿时间、相关回执/ABA、授权撤销、同键并发、未知结果/资源两个轴、故障换代/最后lease、背压、pulse结束、counter多圈、durable崩溃窗。发现问题直接修本正文，不新增过程文件。

第二轮外部消费者视角：仅用§3/4/7公开构造与§9最小Host按正常/异常/finally完整走查；Factory前Registry根、原Task/借用对象强持、有限cleanup/late归还及两消费者接线、BCL测试预算/六门定位；再对本文件做Markdown fences/标题唯一/API引用/本地链接定向检查，不全仓校验、不无限重复全审。

本轮完成**指导规格定向自审、结构核对及主控接收状态同步**；未执行产品C# build/run、HALCON/AsunImage调用、真实WPF实窗、性能、设备/HIL、Golden/Replay运行或生产验收。整模块保留DesignReview / Prep，逐切片状态唯一见§17；C1/C2/C3的规格准入不表示实现完成，W1/A1保留PreparationIncomplete / NotReady。本次同步不自动开启实现。

2026-10-10定向自审记录：两视角已走查并关闭重复/未声明API、缺极性与raw格式、checked-double非有限遗漏、ACK/ABA误升Applied、结果与排空混轴、Factory前无Owner、late产物丢失、Unknown资源Released后对账Owner被回收、过滤状态缺前驱时间、共享故障重连需全租约自愿退出等缺陷。结构检查确认公开类型无重复声明（两个Host partial容器例外）、代码围栏成对、标题无重复、旧示例入口已移除、本地引用目标存在；未创建产品工程或额外证据文件。随后依据主控内容复核同步§17：C1/C2/C3为ModuleCoreImplementationReady，W1规格接收但资格/集成门未关闭，A1未接收；不覆盖任何未执行验证事实。

2026-10-11 A1定向增量：沿既有§7接口/§9 Host核对公开参数、构造、绑定、状态/时间/脉冲/批量/幂等、原Task与有限恢复，仅补§7.3的地址canonical冲突、clock注入、部分构造失败产物、单次ValueTask消费及恢复单飞约束；原会话完成该软件范围内容审核。2026-10-10的“A1未接收”保留为历史停点，当前分类以§17为准。已确认范围不重审、不新建工程/报告/脚本，不声称真实SDK/设备/WPF/Golden/性能通过。

