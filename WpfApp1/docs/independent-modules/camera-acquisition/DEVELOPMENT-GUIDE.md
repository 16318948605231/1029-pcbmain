# 相机采集能力独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2-RF`

- 模块：`camera-acquisition`（相机采集能力）
- 文档 ID：`IM-008`；来源：`PKG-008`；版本：`0.4.3-prep`
- 状态：C1、C2-RF `ModuleCoreImplementationReady`（仅规格准备）；C2其余范围及C3–C6保留各自准入门；当前阶段：全部批准范围文档准备收口（2026-10-11），结论见§21
- 规划消费者：视觉检测应用、独立采集工具
- 实现、测试和发布状态：尚未实现；尚无产品或现场验收结论
- 技术基线：C# / .NET 10；平台消费者经 `ImageLibDotNet` 公共边界使用 AsunImage；HALCON 参考版本 26.05
- 模块级设计评审态：`DesignReview`（方案可评审）。§21「全部批准范围的文档准备结论」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本文是相机单设备能力的独立实施指导。模块自身公开契约以附录 A 的 `Module API Contract v0.2` 为唯一实施候选，覆盖完整模块能力；C1的泛型托管Core/Contracts、Simulator、测试ports与无UIHost已由主控按DEV-GOV-010 §3.1六项接收，状态为 `ModuleCoreImplementationReady`（仅规格准备）；C2-RF（§20）的只读Core/typed端口/双Synthetic Host与有限验证文档规格已于2026-10-11由主控限定接收为 `ModuleCoreImplementationReady`（仅规格准备）。实施派发、代码基线与真实验证另行处理。平台 Schema、共享帧合同与设备资格另按对应 Owner 采纳，不因本指导补齐而视为获批。设计边界与 [独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)、[PKG-008](../../shared-modules/packages/PKG-008_Camera.md)、[SM-007](../../shared-modules/modules/SM-007_acquisition.md) 一致。

本轮吸收的现场来源是只读快照 [DZ-XVision 2026-10-04](../../references/project-snapshots/DZ-XVision/20261004/README.md)。快照为 .NET Framework 4.7.2 WinForms 整机，依赖、页面、产品/MES 事务和旧图像封装均不迁移；下文只记录经抽象后可用于通用端口、状态、回执、故障恢复和验收的事实。快照事实是现场经验，不是本平台实现或硬件资格证据。

## 1. 职责与边界

模块负责一台相机或一个相机端口实例的发现、能力查询、连接、配置校验/应用/回读、触发控制、采集启动/停止、帧交付、断连检测和本实例资源排空。一个物理相机同时只能有一个配置/命令 Owner；可有多个只读状态订阅者，但不得通过第二个模块实例绕开该规则。C2-RF（§20）已获主控限定文档接收，状态为 `ModuleCoreImplementationReady`（仅规格准备）；C2设备/Frame Owner正式映射、真实SDK/编译、WPF、性能/HIL/现场门仍保留，不获得运行或产品资格。

公开的帧数据复用 [PKG-006 图像帧契约](../../shared-modules/packages/PKG-006_Frames.md)。本模块只建立相机来源、会话、触发/帧关联和配置修订的交付信息，不重新定义帧像素布局、租约、缓存或图像对象。驱动原生 buffer 的生命周期与 PKG-006 帧租约的生命周期必须分别记录；只有帧所有权成功转移或复制/保全完成，才可释放驱动 buffer。

模块不负责多相机/多设备编排（PKG-012）、照明、运动、结构光序列、FOV/扫描规划、目标或板件身份关联、覆盖完整性、图像质量、视觉算法、工艺解释、复判、结果提交、质量放行、生产重拍策略及安全互锁。宿主拥有调用流程、使用权限、生产策略和设备副作用授权。模块不发运动/照明/PLC 命令，不根据采集结果推断 PASS/NG，不因失败自行无限重试。

设备 SDK 句柄、原生指针和回调只存在于可替换适配器内部，不出现在核心公共契约、UI、日志或消费者对象图中。HALCON/AsunImage 不是采集业务状态的所有者。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Pcb.Modules.CameraAcquisition.Contracts`（合同层）与 `Asun.Pcb.Modules.CameraAcquisition`（Core）不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `CameraWorkbench` WPF 控件切片（§10）可引用 WPF/DevExpress，Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1 已明确"最小 Host 是普通 .NET 10 console，无 WPF/DevExpress/HALCON/SDK"，直接验证这条门禁。

**Blazor/Web 宿主中的相机状态与采集监控**：Web 端需要"展示相机连接状态、帧率、最近一帧缩略图与采集会话统计"时，服务端通过 `integration-transport` 的 SignalR Hub 把本模块的状态快照推送到浏览器。约束：
- 浏览器端只渲染状态与数字，**不直接控制相机连接/触发/采集**；所有命令走 WPF 操作台（或已授权的 gRPC 接口），不经浏览器发
- 帧缩略图通过 HTTP Range 分片下载，不通过 SignalR 传输原始帧字节
- Web 端的"相机在线"状态是本模块事实的只读投影；任何控制路径必须经授权并绑定会话，Web 端无法绕开
- §1 已明确"不允许第二个模块实例绕开单配置 Owner 规则"——Web 宿主不得以"远程操作"为由新建第二个 CameraAcquisition 实例

**AI 推理 Tiling 适配**：本模块的输出（帧 + FrameLease）是整个视觉链的起点，也是 AI 推理 tiling 的最终图像来源。适配约束：
- 推理 tile 由 `image-frame` 从本模块交付的帧租约裁切，**本模块不持有推理 tile 租约**，也不直接与 `ai-inference` 通信
- 帧租约的生命周期由 `image-frame` 管理；§1 已明确"驱动原生 buffer 的生命周期与 PKG-006 帧租约的生命周期必须分别记录"——两套生命周期不得互相替代
- AI 推理的三态仲裁（`ai-inference` §1A）对本模块采集到的帧"质量低"的判定，不触发本模块的重拍；重拍策略由宿主负责（§1 已明确"不因失败自行无限重试"）

**HALCON 备选策略不适用**：本模块不执行视觉算法，采集帧只是像素字节搬运。HALCON 备选双跑 CI 不涉及本模块核心；图像质量评估由 `image-quality` 模块负责，本模块只负责把帧正确交付到帧租约。

## 2. 组件与依赖方向

```text
视觉检测应用 ─┐
              ├─ camera-acquisition Core ─ Camera Adapter ─ 厂商 SDK / HALCON 图像采集
独立采集工具 ─┘              │
                             ├─ PKG-006 帧契约
                             └─ 诊断端口 / 时钟端口（宿主注入）
```

发布候选为无 UI 的 Core/Contracts、每种设备族可选 Adapter、可选 WPF 参数/诊断控件。模块不能引用消费者程序集、产品 ViewModel、私有数据库、全局 ServiceLocator 或隐藏窗口。Core 构造时显式注入 transport、clock、ledger、access、frames、diagnostics 与 limits；无 SDK 的文件、回放和模拟源实现同一适配器端口。AsunImage 仅在需调用图像采集/转换或 HALCON 图像能力时经 `ImageLibDotNet` 公共 API 接入，不能在设备核心中新增平行图像实现。

## 3. 公共输入、输出与参数

下表定义参数语义，精确名称/形状见附录 A；平台映射仍待相应 Owner 接收。不得把动态字符串字典作为通用参数 API。

| 概念 | 强类型语义 | 单位、范围与默认规则 |
|---|---|---|
| `CameraSelector` | 稳定适配器类型 + 厂商/接口提供的稳定设备标识；枚举结果另含显示名 | 标识按不透明字符串传递；不默认选第一个发现设备，不把显示名当唯一键 |
| `CameraCapabilities` | 能力版本、设备型号/固件、支持功能、参数定义、触发模式、像素格式、尺寸/ROI 限制、可并发采集模式 | 范围/离散步进或连续域/枚举必须逐台设备报告；未知、不支持、暂不可读/写分别表达；不得合并成空值或假范围 |
| `CameraConfiguration` | 可选字段构成不可变配置快照：像素格式、ROI、binning、曝光、增益、触发源/边沿/延时、采集模式 | ROI 用整数传感器像素 `(x,y,width,height)`；正尺寸，坐标原点、边界和步进由设备能力明示。曝光 API 单位为 µs，必须在设备给出的有限范围及已声明的离散步进/连续域内。增益必须携带明确单位标识（如 dB 或设备原生单位）及设备修订；不能跨设备换算猜值。Trigger delay 用 µs，只有设备能力声明精度/步进后可写 |
| 配置缺省 | 未提供某一字段表示 `Unchanged`，不是 0、设备默认或“自动” | 首次连接不隐式写曝光、增益、ROI或像素格式。若调用方要求设备默认，必须显式使用设备能力报告的 default 值并回读；自动曝光是单独能力和模式，不是空值 |
| `OperationBudget` | 每操作必填的单调时钟预算、可选排队预算和外部 `CancellationToken` | 全部为正 `TimeSpan`，不得为 Infinite；操作缺省预算为无效输入。预算上限由适配器声明；本文件不虚构通用毫秒值 |
| `CaptureRequest` | 触发模式/触发数、请求帧数、不可变配置修订、帧队列容量、来源标签、预算/取消 | 单次请求帧数和队列容量为正整数且不得超过能力/预留资源上限。未填最大丢失数时为 0；采集关键帧禁止静默丢弃。`SourceTag` 由调用方提供非业务解释标记，可空 |
| `CameraFrameEnvelope` | PKG-006 frame lease + camera instance/session/epoch + 本会话单调序号 + 触发关联（若可证明）+ capture source + 配置/能力 revision + 设备时间戳原值/时钟域 + 主机接收时间 | 时间值同时携带单位、时钟域、启动代和采集事件语义；无可信触发 ID 时明确 `Uncorrelated`，不得按最近时间或数组下标强行关联 |
| `ConfigurationApplyResult` | 每字段 `Accepted/Applied/ReadBack/Unknown/Rejected` 结果，应用前值（可得时）、读回值、revision 和设备原码 | 批量部分成功必须逐项返回；不承诺设备具有回滚。ACK 只表示端口接收，不能代表已应用、已回读或本帧实际生效 |
| `CaptureOutcome` | 逻辑结果、成功交付数、缺失/冲突/丢弃区间、停止与 drain 回执、实际配置/来源修订 | 采集命令成功、触发已确认、曝光已发生、帧已到达、帧完整、帧已移交、队列已排空分别表示；不折叠为一个 `Success` |

设备参数的可用范围和 factory default 不在模块中另造全局值；范围来自当前设备能力查询，默认来源来自设备官方资料/读回。无有效能力清单或关键字段读回未知时，拒绝相关设置/模式并报告具体字段。产品 Profile 可以提供宿主默认值，但不能冒充设备默认。

## 4. 操作入口与事件顺序

同步入口只允许纯验证/查询，例如 `ValidateConfiguration`、读取不可变状态快照；设备发现、连接、配置、触发、取帧、停止、排空、关闭必须为异步并可接收预算与取消。模块唯一实施 API 见附录 A；本节只定义方法语义，不再声明第二套方法名、参数或 DTO。

适配器若底层只有同步阻塞 SDK，必须在专属 worker/线程执行；不允许占用 UI Dispatcher、调用线程池后假称底层已取消，或在回调中调用 HALCON、持久化、WPF事件或用户代码。

正常产生设备副作用的入口必须先通过宿主注入的 `IOperationLedger` 在耐久记录中以 `operationId`、幂等键、canonical request hash、session/epoch 和阶段原子登记，再调用适配器；账本失效时已接纳采集的必要停止按 A.6 的故障清理例外处理并保留 Unknown，不宣称耐久完成。`QueryOperationAsync` 是唯一的原操作对账入口，必须能在进程重启后返回已持久化的阶段、设备调用是否发生、终态、排空状态和原生回执；`NotFound` 只表示该 ledger 没有记录，不能证明设备没有执行，宿主必须保持 `Unknown` 并转入设备 Owner 的恢复流程。查询不得创建新设备动作。

每个会话的事件语义顺序如下（失败/取消先记录逻辑结果；已接纳采集请求在操作资源确认归还前不得发布最终终态，接纳前拒绝走 RequestRejected 短路径）：

1. `SessionOpening` → `SessionOpened`；连接失败则 `SessionFailed`，不得产生采集事件。
2. `CapabilitiesRead`；每次重连都重新读取能力并创建新的 session epoch。
3. `ConfigurationApplying` → 按配置字段稳定排序的 `ConfigurationItemResult` → `ConfigurationCompleted`。完成事件仅汇总逐字段回执，不得将 partial/unknown 变成 applied。
4. `CaptureArmed` → `TriggerRequested` → `TriggerAcknowledged`（仅适用可确认的触发模式）。ACK 与传感器曝光不是同一事件。
5. 每个有效到帧依序发出 `FrameReceived`（接收层）→ `FrameValidated`（布局/来源/epoch 校验）→ `FrameDelivered`（所有权/租约转移已确认）。重复帧发冲突/重复诊断，不重复交付；不合格 buffer 在转移前释放。
6. `CaptureStopRequested` → `CaptureInputClosed`（不再接受新触发/帧）→ 封口前完成已移交帧计数；封口后未移交队列明确归还/记AfterSeal → `DrainCompleted`（设备、回调和内部缓冲已排空）→ `ResourcesReleased`（帧租约、临时缓冲和适配器资源已归还）→ `CaptureCompleted/Cancelled/Failed`。
7. `SessionClosing` → `SessionClosed`。关闭/释放错误必须保留 `ResourcesOutstanding` 或 `Unknown`，不能报告已关闭。

已建立会话的通知携带 `sessionId`、`epoch`、`operationId`；接纳前拒绝无会话时Session/OperationId可null且EventSequence=0；会话流的eventSequence递增。所有通知携带UTC审计时间和单调时间。订阅者不得通过事件返回值修改模块结果。回调顺序只在同一 session/event stream 内保证；不同会话之间不保证全序。进度/诊断允许合并，帧与终态结果不得合并或丢弃。订阅者异常隔离并计入诊断，慢订阅者不能阻塞设备回调或帧读取。

## 5. 状态、错误与幂等语义

以下状态词汇是行为定义，不是与平台状态机并行的持久枚举：

| 阶段 | 语义 | 可接受的下一动作 |
|---|---|---|
| `Closed` | 本实例无设备会话/资源 | Connect / Discover |
| `Opening` | 正在取得资源，尚无可用 session | 等待、取消并排空；不得配置/触发 |
| `Ready` | 能力已读；配置状态及 revision 已知 | Apply、Capture、Close |
| `Configuring` | 正在逐字段应用或回读 | 禁止并发配置和触发 |
| `Capturing` | 接受本 epoch 的触发/帧 | Stop、读取帧；禁止改需停采参数 |
| `Stopping` | 已关新触发入口，正在处理在途操作 | 等待 drain；不得新 Start |
| `Faulted` | 错误阻止继续操作，资源排空状态独立记录 | 只允许查询、停止/排空、关闭或由宿主重新打开 |
| `Disposed` | 本实例已清理结束 | 新命令拒绝；Snapshot、授权原Query/释放回执可只读，重复释放幂等 |

每一操作至少返回结果类别、稳定模块错误码、可重试性（`Never/AfterStateCheck/WithNewOperation`）、阶段、原生来源码（若有）、关联 ID 和建议恢复动作。候选错误码及映射需 Contract Owner 采纳：

| 候选码 | 含义 | 默认重试规则 |
|---|---|---|
| `CAM-INPUT-INVALID` | 参数缺失、越界、单位/能力版本不匹配 | 不重试；修正输入 |
| `CAM-DEVICE-NOT-FOUND` | 发现目标不存在或已移除 | 检查选择器/连接；新 operation 才可重试 |
| `CAM-DEVICE-BUSY` | 设备被另一 Owner/进程占用 | 禁止强占；查询 Owner/状态后新 operation |
| `CAM-UNSUPPORTED-CAPABILITY` | 设备明确不支持请求项 | 不重试；删去/替换受影响功能 |
| `CAM-CONFIG-PARTIAL` | 部分字段 applied，部分拒绝/未知 | 先读回完整状态；不可盲目重放整组 |
| `CAM-TRIGGER-UNKNOWN` | 触发命令结果未知，可能已执行 | 查设备/触发回执；不得自动重发 |
| `CAM-CAPTURE-TIMEOUT` | 操作预算到期，停止/排空另有回执 | 只可在新 attempt 且旧资源排空后重启 |
| `CAM-CANCELLED` | 取消已接受；不表示 native 已停止 | 等待 Stop/Drain receipt，不立即释放资源 |
| `CAM-FRAME-INVALID` | 像素布局、payload、时间/来源元信息无效 | 丢弃该 buffer，报告缺失；不可交算法 |
| `CAM-FRAME-DUPLICATE` / `CAM-FRAME-CONFLICT` | 稳定键重复相同内容 / 同键内容冲突 | 不增加计数；冲突帧隔离，不采用最后到达者 |
| `CAM-QUEUE-OVERFLOW` | 必需帧队列无法接收新帧 | 执行配置好的受控停止/失败，不静默丢弃 |
| `CAM-DISCONNECTED` | 会话中链路断开 | 关闭当前 epoch；宿主决定是否新建 session |
| `CAM-DRAIN-INCOMPLETE` | 超时后仍有回调、buffer 或租约占用 | 保持资源占用标记；不得 Dispose/重开同物理设备 |
| `CAM-ADAPTER-FAILURE` | 适配器异常或未映射原始错误 | 保留原码/堆栈诊断，失败关闭并排空 |

这些候选码不得被实现自行写入平台正式错误 Schema。返回超时或取消后，调用方必须通过 `QueryOperationAsync` 查询同一 `operationId` 的终态；若设备副作用未知，状态保持 Unknown，不以重试产生新事实。查询返回 `NotFound` 也不能证明副作用未发生。发现断线后旧 epoch 立刻停止交付；重连必须新建 epoch、重查能力/当前状态，不重放未知 Trigger 或配置副作用。

## 6. 取消、超时、排空与资源

显式 `StopAndDrainAsync(Reason=Cancelled)` 的取消流程固定为：拒绝新准入/触发 → 请求适配器停止 → 标记在途 trigger/callback 为关闭或结果未知 → 收取/隔离已发生的迟到帧 → 保留封口前已交付事实，未交付帧归还并记录原因 → 等 SDK 回调/worker 退出 → 归还驱动 buffers → 等所有 PKG-006 帧 lease 的实际消费者归还 → 返回独立 `StopReceipt`。方法 cancellationToken 只控制当前等待；显式Stop才请求取消采集。它们都不是硬件急停、设备已停止或SDK资源已释放的证据。

operation timeout 使用单调时钟。到期只终止等待预算，不强行释放可能仍被 native 使用的内存/句柄。公开 API 只提供 DisposeAsync；设备停止与排空需异步确认。若底层 SDK 永不返回，适配器把资源标为仍占用/未知，阻止同进程重连及重复打开；进程结束也不能证明相机硬件实际停止，须由宿主设备治理层检查。

同一实例的并发关闭、重复 `DisposeAsync` 和关闭中同步重入必须汇合到同一次关闭尝试及其回执，不因“已请求关闭”标志提前返回成功；重入回调只登记请求，不同步等待需要自身退出的关闭任务。先阻新准入，再等待已准入命令、帧读取、异步来源解析和回调退出，最后释放其依赖；失败保留 Owner、未完成阶段和查询入口。后续显式恢复仅处理未完成阶段，已成功的阶段不重复执行；底层未声明可重试的释放失败不能因第二次空 `Dispose` 被判为已释放，不自动重发设备命令。

所有 buffer 有界：采集队列必须按最大帧数、最大 payload/plane 数和峰值内存预算预留；容量不足前应暂停可控输入或拒绝 Start。外触发源不可背压时，超限产生明确 overflow/丢失范围并沿安全的设备停止路径处理。生产帧禁止 latest-wins、DropOldest 和 UI 慢消费导致的静默丢弃。独立预览可使用有界 latest-wins 投影，但须由宿主持有独立快照/租约，不能拖住驱动 buffer。

buffer 所有权在每个成功、取消、异常、重复回调、队列拒绝、消费者提前退出及关闭路径均须唯一。回调最多做有界元数据检查、取得/转移 buffer 所有权并入队；消费端释放 PKG-006 lease。异常路径使用 `finally` 释放尚未转移资源。关闭前分别统计 outstanding callback、worker、driver buffer、frame lease 和临时适配器资源；callback/worker/driver buffer 任一非零都不能返回 `DrainCompleted`；frame lease、临时 buffer 或适配器资源任一非零都不能返回 `ResourcesReleased`。最终采集终态只能在 `ResourcesReleased` 后发布。

## 7. 配置、安全与版本

一次 Apply 先校验能力修订、全部字段类型/单位/量程/步进、字段间依赖和当前会话允许写入条件，再应用并逐项读回。禁止没有设备证据时假设原子应用或通用 rollback；部分写入时返回逐项结果和当前读回，不把期望值覆盖成已应用值。任何参数写入只针对明确传入的配置快照，不从全局配置、UI 草稿或隐式 profile 读取。

API、适配器协议和帧适配分别版本化。只增可选字段且保留旧语义可作为兼容增加；改变单位、默认语义、帧身份、丢帧策略、取消/释放所有权或状态含义属于破坏性变更，升主版本并提供迁移说明。升级时每个消费者先校验 API/adapter/frame contract 兼容范围；不兼容拒绝启动，不静默降级。配置快照携带 Schema 版本、设备能力 revision 和来源。旧配置迁移要逐字段转换并回读，不把未知单位/能力值猜成新值。

发布包应独立版本 Core、Contracts、各厂商 Adapter 及可选 UI；消费者通过锁定版本升级。发布记录兼容矩阵、HALCON/AsunImage边界、Adapter SDK 版本、已覆盖设备能力和已知限制。回退使用上一个已验收包及原配置快照；旧包不可用时保持相机关闭/仅查询，不通过自动重放旧配置恢复采集。配置或固件更改后重新读取能力并验证适用性。

## 8. 适配器与 HALCON / AsunImage 决策

本能力不做视觉算法，因此无需以 HALCON 算法替代相机控制。已核对项目内 `halcon算子手册/operators` 的 HALCON 26.05 条目：`open_framegrabber`、`close_framegrabber`、`grab_image`、`grab_image_async`、`grab_image_start`、`grab_data`、`grab_data_async`、`set_framegrabber_param`、`get_framegrabber_param`、`info_framegrabber`、`set_framegrabber_callback`。`open_framegrabber` 的 26.05 说明包含设备连接测试和显式设备默认值；`grab_image_async` 的 `MaxDelay` 是自异步抓取启动起计算的图像年龄上限（ms），超龄可重新抓取，负值关闭旧图检查，并不是调用等待超时；默认会在返回前启动下一次异步抓取；HALCON 资料还说明可用 `set_framegrabber_param('do_abort_grab', ...)` 中止，但只有具体采集接口支持时才成立。`set_framegrabber_callback` 的建议类型包括 `exception`、`exposure_start`、`exposure_end`、`transfer_end`，可用集合需通过 `get_framegrabber_param('available_callback_types')` 查询；回调签名包含 acquisition handle、接口上下文和 user context。`open_framegrabber`、`close_framegrabber` 及 `info_framegrabber` 在多线程使用时要求互斥，关闭时不能有另一线程并发使用同一 handle。上述事实只证明 HALCON 的候选采集语义，不证明目标相机/接口可用，HALCON 算子通过 `ImageLibDotNet.cv2` 调用。选该路线按 DEV-VIS-021 核对应算子版本、异常、线程/回调和 native buffer 生命周期；仅实际 C# 类型/重载/封送有歧义时查公共签名；不得照搬另一仓库或反射内部方法。

HALCON 相机适配器经 `ImageLibDotNet.cv2` 使用对应算子，不重复核验算子是否存在；实际 C# 类型/重载/封送有歧义时以消费项目公共签名和编译确定；`Vision_CameraCalib` 文档/代码只作为已有图像来源的历史场景参考，不是通用相机采集模块。不能根据方法名把调用当作可取消 `Task`，也不能把旧项目的包装方法、原生句柄模式、generic 参数或设备默认值迁移为本模块 API。适配器必须依据实际公开签名，在专用 worker 上运行可能阻塞的调用，并单独实现等待取消、停止和 native drain；回调委托及上下文必须保持存活到实际注销并排空，不能让回调直接执行业务/UI。不同相机族的默认值不可提升为通用默认。此处只用于提醒核对既有采集路线、线程和资源语义。

每个 Adapter 必须声明：支持的设备/固件范围、能力发现可靠性、配置/回读精度、触发和帧身份来源、队列/背压能力、线程亲和、同步/异步原生行为、取消与停止保证、关闭后回调行为、native buffer 归还条件及原始错误映射。HALCON Adapter 与厂商 Adapter 都实现同一 Core 端口；文件/回放和模拟 Adapter 显式标记 `Replay`/`Simulation` 来源，不冒充实机。

### 8.1 MVS 4.8.1.0 公共事实限制（Adapter 专属）

只读来源为 `H:\docs\40-development\41-vision-platform\02-acquisition\相机采集抽象与诊断开发指导.md`，SHA-256 `207b4585f07fe997bc0003a38d20ca67a3b9e4de73a9adecc0664d23cf07dfca`，定位于 MVS-SOURCE-01、§19.1–19.3 及关闭/资源修订；登记见 [全量来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)。本轮与指定 net40 目录公共 XML（SHA-256 `888f5a9cb93db5d8017a7842e810a455984e6255a44e9de8a914eced1f7b0777`）及 `Development/Includes/CameraParams.h` 定向核对后，采纳下列限制；来源中的 MVS 5.0.2/SDK 4.8.1.2 研究不替换本平台指定 managed DLL `4.8.1.0`。

1. XML `IEventOutInfo.BlockId` 和头文件事件帧号明确标注暂无固件支持；不能用 `ExposureEnd` 到达顺序关联帧。`DevTimeStamp` 数值不自证纳秒单位或曝光语义，`TriggerIndex` 计数不自证调用方 `TriggerId`，`ExposureTime`/`Gain` 标量不自证逐帧 chunk。缺证据保持未知或 `Uncorrelated`；需要该能力的设置/模式按明确不支持/未知分别以 `CAM-UNSUPPORTED-CAPABILITY`/`CAM-CAPABILITY-UNKNOWN` 拒绝，不新增来源项目的错误码、时间默认值或关联规则。
2. `IFloatValue.CurValue/Min/Max` 不提供步长，`SetFloatValue` 接收 `System.Single`。能力中不能编造步长/容差；按已批准参数语义先校验有限性、单位、范围和步进，再记录 requested、转换后的实际下发值与 SDK readback。不得将正常 double→single 表示变化误当设备漂移，也不得将读回值覆写为 requested 或虚构逐帧实际曝光；缺步进不能推断为连续域；只有设备文档/节点明示连续浮点域，才能按连续域校验；两种域均未知则按 §3 拒绝相关设置，不借普通试机例外放宽生产准入。
3. chunk 使用当前设备/固件明确的布局检查字节长度、类型、单位、端序、偏移、重复和截断；SDK 标量与 chunk 的对应关系需有可复查来源，不能假定未解析列表包含全部已解析字段。元数据大小、条目数和等待预算由 Profile 显式提供，不沿用来源的固定上限。异步事实解析在 SDK 锁和指针使用区外执行，沿用原帧剩余预算；交付前再核 session/epoch/配置 revision，取消或超时后的迟到结果不得回填新采集。

MVS `IImage.PixelData` 会从非托管内存复制到托管内存，不能宣称零拷贝；`PixelDataPtr` 仅提供非托管指针，不自带安全借用资格。复制路径须在 `FreeImageBuffer` 前完成有界像素/元数据复制并恰好归还所取得的 SDK buffer，指针不得离开 Adapter，释放后不得再读；释放失败保留故障与 Owner，不交付成功帧。`FrameGrabedEventEx` 明确要求手动释放，其规则不能套用于其它事件模式；每种实际调用模式分别核对释放责任。SDK buffer 已归还与我方独立帧 lease 仍在使用分别记录，后者未结束不能覆写我方池槽。

本节及 §6/§14 的增量仅补强现有 Adapter、关闭和容量验收，不新增公共 DTO、状态机、持久化权威或签名来源。来源的 AOI Actor/任务/工作树、BoardRun/FOV/质量编排、内存账本实现、默认容量与性能阈值、3D设计、旧接口索引及项目验收结果均不采纳；已有能力/诊断/触发/恢复要求直接复用现指导。本轮未采用 HALCON 24.11 方法，不新增视觉算法。

### 8.2 MVS Adapter 的固定装配与取流算法

本节给出C3的软件设计，不创建厂商SDK实现。唯一命名空间/工程沿A.8的 `Adapters.Mvs`；公开 `MvsCameraTransport` 实现 `ICameraTransport<IFrameLease>`，IFrameLease与帧服务只引用image-frame §4.3，不进入C1 Contracts。构造固定为 `(MvsSdkRuntime runtime, MvsAcquisitionProfile profile, IFrameService frames, IManagedLayoutValidator validator, ICameraClock clock, CameraLimits limits)`。构造只校验并保存借用，不初始化SDK、不open、不创Core。Host先登记原transport/runtime/frames和Core到§9恢复槽，Connect才允许初始化/open。transport生命周期由原Core管理，runtime/frames仍由Host所有。

`MvsSdkRuntime` 是此Adapter包的sealed class/IAsyncDisposable，构造 `(ICameraClock clock, CameraLimits limits)`；Host进程内给全部MVS实例注入同一对象。它私有串行Initialize、枚举、Finalize，Connect/Discover首次使用才调用 `SDKSystem.Initialize()`；取得实际使用计数，只有全部设备/原SDK调用退出才能Finalize一次。Dispose未排空按CameraDisposalException保留对象/引用，不用模块隐式静态全局或窗口保存SDK。不得另建runtime绕过同一设备Owner；其它软件的争用仍由跨进程access/设备独占判定。

设备Profile是有来源的绑定值，不是可执行插件或参数字典；以下新增record只在Adapter包，按字段顺序编码，空/重复/不可信证据在Connect前拒绝：

| 类型 | 完整字段与域 |
|---|---|
| `MvsAcquisitionProfile` | `string ProfileId, Revision; CapabilityEvidence Evidence; CameraCapabilities CapabilityTemplate; CameraProtocolLayout Protocol; A<CameraNodeBinding> Nodes; A<MvsPixelBinding> PixelBindings; uint ImageNodeCount; TimeSpan NativePollBudget`；模板锁定Model/Firmware/geometry/单位/依赖/已证明资源上界，Session/Current不作活动事实；节点及像素绑定非空；节点数正，poll预算正且不超过limits/Transport.MaxBudget，不提供设备默认 |
| `CameraNodeBinding` | `CameraNodeRole Role, TriggerSelector? Selector, string NodeName, CapabilityEvidence Evidence`；Role={PixelFormat,RoiX,RoiY,RoiWidth,RoiHeight,BinningHorizontal,BinningVertical,ExposureMode,ExposureValue,GainMode,GainValue,TriggerSelector,TriggerMode,TriggerSource,TriggerActivation,TriggerDelay,TriggerCommand,AcquisitionMode,AcquisitionCount}；仅Trigger类含selector，其它null；(Role,Selector)唯一；NodeName为设备已证明节点，不能由UI输入 |
| `MvsPixelBinding` | `string FormatId, uint NativeValue, PixelScalarKind Scalar, ByteOrder ByteOrder, int BitsPerSample, ChannelCount, PlanePacking Packing, PlaneRole Role, A<string> Channels, CapabilityEvidence Evidence`；复用image-frame Core枚举；位数/packing/channels按其validator接受域，只有无损字节布局已证明的格式才报告支持，packed/Bayer无映射则Unsupported，不偷偷转换成Mono8/RGB |

Profile模板的NumericDomain/Defaults/Trigger规则及Transport上界须逐项有设备资料依据，实际查询与模板取更严格合法域，实际型号/固件或枚举不符拒绝对应能力；Read/Write均以当次node access为事实。Profile hash用A.6值规则，`Revision`为SHA-256(ProfileId、Evidence的SourceReference/SourceVersion/SourceHash、CapabilityTemplate的ContentHash、Protocol、Nodes、PixelBindings、ImageNodeCount、NativePollBudget.Ticks)，排除本Revision和ObservedUtc；嵌套Nodes按Role/Selector、PixelBindings按FormatId Ordinal排序，模板ContentHash先按CameraCanonical核对。软件测试可显式fixture标识，Hardware须真实编码hash。未提供Profile只阻此Adapter，不阻C1/C2-RF。

固定调用映射来自§8.1同一4.8.1.0 XML（本轮指纹未变）及本机官方 `Development/Samples/C#/MvCameraControlNet_V2/General/Grab_GetImageBuffer/Grab_GetImageBuffer.cs`，SHA-256 `95681ebe26125a017ce128b8d84065ac557aa0bde30ead652a5ec4103dbb5235`。样例仅证明公共调用顺序，不采用其静态全局、1000ms等待、索引选择、无限循环、忽略释放结果或自动重连。

| 端口方法 | 固定SDK调用与软件处理 |
|---|---|
| Discover/Connect | `DeviceEnumerator.EnumDevices`在runtime短门内，复制稳定标识/型号/接口后退出；StableDeviceId绑定接口类型+SerialNumber（无稳定序列号则该设备不可选），不以IP/显示名/列表下标唯一。精确匹配后 `DeviceFactory.CreateDevice`→`IDevice.Open()`独占→校验型号/固件/Profile→读能力/当前设置。任何失败保留实际device和原Task，Core按原Connect/Dispose清理；不open第二台替代 |
| 能力/读回 | `IDevice.Parameters.GetNodeAccessMode`：NI为Unsupported、NA为TemporarilyUnavailable、WO/RO/RW分别报告写/读能力，Undefined/CycleDetect/查询失败为Unknown并留原码；`GetIntValue`取Min/Max/Inc/CurValue，`GetFloatValue`取范围/CurValue但域性质/步长仍依§8.1，`GetEnumValue`只取已报告SupportEnumEntries的Symbolic/Value。读回不可得不填模板请求值 |
| ApplyItem | 只写当前ConfigurationField的节点；Int用checked Int64、Float记录decimal→Single实际值后 `SetFloatValue`、enum使用已读Symbolic精确匹配的Value→`SetEnumValue`，每项写后用同节点Get读回。自动Once/Continuous只有对应枚举明示支持才开放。Trigger item先选择目标selector上下文再写该selector Mode/Source/Activation/Delay，不改其它selector；Off只关闭Mode，不默改source。ROI合法过渡见下段；任何native失败停止后续写，保留部分回执，不假回滚 |
| Arm/Trigger | 预留SDK/独立staging/共享发布容量后 `StreamGrabber.SetImageNodeNum(ImageNodeCount)`→`StartGrabbing(StreamGrabStrategy.OneByOne)`；主路线为专属取流worker，**不同时注册另一FrameGrabed事件生产同一帧**。软件Trigger只调用绑定的 `SetCommandValue(TriggerCommand.NodeName)`一次，成功仅ACK，不赋ExposureObserved；硬触发只arm |
| Receive | `GetImageBuffer(checked uint毫秒预算,out IFrameOut)`；预算取NativePollBudget与capture剩余deadline较小者，不足SDK最小1ms则不再发read。MV_E_NODATA只表示本次未到帧，保留原capture与截止，不增加缺失计数/不重触发；其它错误结构化ReportFault。实际帧号/长度/ImageSize/Width/Height/PixelType/包丢失按Profile验证；不能以FrameNum或TriggerIndex自动构造预约证据 |
| Stop/Close | 先关输入；worker在本次有限read真返回后不再read，归还仍持IFrameOut→`StopGrabbing()`→确认SDK/worker退出→Core归还队列/lease→`IDevice.Close()`真成功后再对同一device执行Dispose，最后归还runtime使用计数；已成功Close/Dispose不重复。只有设备资料保证跨线程Stop/abort安全时才由控制worker并行中止；否则有限观察保留原read/Owner，禁止另线程Close指针。未知释放不再read/不Finalize/不放grant |

ROI item内部固定合法过渡为：在同一已核sensor/binning域内，先把Width/Height分别缩为min(当前读回尺寸,请求尺寸)，再写目标X/Y，最后写目标Width/Height，逐步读回并记录本项partial。这些过渡仍只修改请求的Roi字段；若中间值不满足当前已声明步进/依赖或尺寸域在同次Apply因binning改变而不可证明，则在任何set前纯校验拒绝该组合，调用方先单独应用前置字段、重新读能力再提交ROI。不得隐式把未请求的Binning/Exposure/Trigger关闭作为恢复。未知当前ROI不能执行此过渡。 GetCapabilities/ReadConfiguration纯读时不写TriggerSelector切换上下文：只返回当前可证读值，其它selector读回Unknown；若当前设备仅能通过selector写入才能核关联，必须由显式Apply对应Trigger项选择并读回，Required采集只接受已确认的selector事实，不把Profile模板标为Current。 Float下发值须有限且转换后仍在当前设备域内；未声明ReadbackTolerance时读回必须与实际Single下发值精确相等，decimal投影按Single的invariant往返字符串解析，requested原decimal另存，不用任意epsilon或expected请求值覆盖差异。

每次取得IFrameOut后，SDK Owner进入有界staging复制：按已核PixelBinding、实际payload长度和行stride复制像素/必要chunk至独立私有数组，保存原始事实；`IImage.PixelData`本身的复制也计入短时双占。SDK `FreeImageBuffer`真成功后才进入独立帧发布队列；finally确保未移交buffer也恰好归还。释放失败保留原对象及取流Owner，不发布staging，不把后继一帧抵消失败。独立数组实现image-frame `IFrameInputRows`，不暴露可写数组/指针；下一次SDK读不得覆写前一staging。

共享发布固定为：预持新的FrameKey/Publish RequestId/Read RequestId及原frames.ServiceEpoch→用源layout/metadata/单位/坐标构造FrameDescriptor→`PublishCopyAsync`→确认该原publish OperationResourcesReleased→`ReadAsync`取得已注册ConsumerId的完整窗口/全部plane/ExactSamples/Halo=0租约→确认该原read OperationResourcesReleased→TryAccept。未知时保留原source/frame-service Task/ID；用 `QueryOperation(serviceEpoch,requestId)`查原操作，不能再Publish。成功移交或Core拒收并归还本lease后，Adapter对自己的发布持有 `RetireAsync`，不Release消费者lease；Retire保留的backing仍计入物理账。frames是Host借用对象，transport不得Close整服务。SourceId绑定selector；SourceRevision为原cap/config/capture来源；CoordinateReference为本session传感器零基像素域，物理坐标由外部标定Owner处理。Mono8等无padding紧凑帧可直接发布；非紧凑布局须有实际stride证明，不以FrameLen/height猜步长。任何metadata/格式不明拒帧并保留fault。

#### 8.2.1 设备事实的固定解码与Unknown边界

MvsAcquisitionProfile与HalconAcquisitionProfile在Nodes前的必需字段均为 `CameraProtocolLayout Protocol`。它是本Adapter包的值契约，复用CameraTimeEvent/TriggerSelector/EvidenceState/ByteOrder，不接受表达式、执行脚本或厂商object。两Profile的Revision预像在Nodes前编码Protocol全部稳定字段；Protocol自身Revision排除，ObservedUtc排除。SDK抽取代码和下面的字节解码算法由本模块实施，设备字段位置/语义是硬件Owner提供的事实；只凭rule名不能开放“可关联”能力。

| 类型 | 完整字段与合法域 |
|---|---|
| `CameraProtocolLayout` | `string Revision; CapabilityEvidence Evidence; A<CameraProtocolField> FrameFields, RowFields; long RowRecordsOffset, RowRecordStride; int MaxRowRecords; int FrameCounterBits; bool HasLineProtocol; string CounterRuleRevision, AssociationRuleRevision, ClockDomain, BootEpoch; long? TicksPerSecond`；frame/row字段按FactKind固定枚举序，重复拒绝；RowFields只接受ChunkBytes/HalconDataBytes且至少有RowIndex/DeviceCounter，实际行payload位置/字节窗由已核像素布局及同RowIndex确定，不能把frame scalar复制成每行证据；时间频率正或null/Unknown；bits=1..64，有行协议时row stride/最大记录数正且受Transport/CameraLimits限额，无行协议三数固定0、RowFields空，不从SDK行宽猜协议 |
| `CameraProtocolField` | `CameraFactKind Kind; CameraFactSource Source; long Offset; int WidthBytes; ByteOrder Order; bool Signed; string UnitId; decimal Scale; CapabilityEvidence Evidence`；Kind={FrameNumber,BlockNumber,RowIndex,ArrivalOrdinal,DeviceCounter,TriggerToken,ExposureStart,ExposureEnd,DeviceTimestamp,ExposureValue,GainValue}；Source={FrameNum,DevTimeStamp,TriggerIndex,ExposureTime,Gain,ChunkBytes,HalconDataBytes}。SDK scalar来源Offset=0/WidthBytes=0/Order=LittleEndian，仅对应FrameNum→FrameNumber、DevTimeStamp→DeviceTimestamp、TriggerIndex→TriggerToken、ExposureTime→ExposureValue、Gain→GainValue；其它Kind只可已保存原字节。字节WidthBytes=1/2/4/8，offset非负、checked范围合法；Scale正、只有ExposureValue/GainValue可非1，原counter/index/tick不缩放；字段单位必须有官方依据，不隐含ns/µs |

Hardware先核Evidence与型号/固件/布局版本。Protocol.Revision为按A.6值规则对本record排自身Revision/ObservedUtc求SHA-256；Profile不得将空layout解释为设备无字段。无公开chunk/HALCON Data的稳定原字节映射时仅可SDK标量事实、HasLineProtocol=false；不把未解析SDK ChunkInfo对象或HTuple任意索引强转为byte协议。首次支持某种字节协议须提供该实际设备原件证据和至少正常/截断/错端序/重复字段的oracle，缺证据关闭该模式；不要求本轮虚构设备字节fixture。

解码先核完整payload/chunk大小和当前session/capture/revision，再核字段唯一/偏移/stride/记录数及总预算。字节字段仅按WidthBytes/Order读整数，Signed时按对应位数二补码符号扩展到decimal，Unsigned时精确保留原UInt64；禁止先转double。decimal可精确承载64位整数，时间RawTicks保持原值，换算只另作诊断。曝光/增益SDK Single须有限，以§8.2往返投影再乘已证Scale，保留原值/UnitId；不赋ExposureObserved。所有checked加乘或解码范围失败整项Rejected/CAM-FRAME-INVALID，不零填越界字段。不支持此整数原字节方案的浮点chunk只能关闭其字段支持，不假装本版已解析，原字节仍可保存。

Frame key有已证明设备FrameNumber时为 `Epoch小写D/CounterRuleRevision/原无符号帧号十进制`；同key用实际字节/元信息摘要判duplicate/conflict。没有可信frame number时可由Adapter接纳源单调序号形成来源定位键（同session `adapter/<序号>`），FrameIdentity仍Unknown、不能用于Required触发或缺帧设备计数；不把软件键当设备counter。回卷/reset只有原协议证据才分新域，疑义封口且保持Unknown。RowIndex取原字段，不从ReceivedLines/数组序号补；ArrivalOrdinal只取原设备字段；设备缺失时为null，适配器接收顺序单列诊断，不冒设备排序。

TriggerToken原值按声明位数十进制不透明串与同selector的ExpectedDeviceToken精确匹配；只有协议明确这个token标识当前曝光/帧或当前capture、字段证据Confirmed且与reservation同域，才赋Proven。不同capture/selector/token相同不能合并；MissingReservations只移除已证实的预约。不支持关联而Correlation.Required则arm前拒绝，NotRequired保留Uncorrelated/Unknown。曝光start/end要有同帧/同line token证据、同ClockDomain/BootEpoch/频率才标Confirmed；只有ExposureEnd SDK事件不赋帧曝光。行counter rule与association rule分开验证，解码出的原行直接投影§20.4；wrap/reset未报告为Unknown，不能以未观察到事件填NotOccurred。Frame ActualConfiguration只有逐帧确认ExposureValue/GainValue才Confirmed，其余设置按设备逐帧证据规则处理，current读回仍单列。

#### 8.2.2 Profile oracle与拒绝样例

无设备的确定性decoder fixture仅为算法oracle：ChunkBytes `01000000ffffffffffffffff`，FrameNumber字段Offset0/Width4/LittleEndian/Unsigned/Scale1读1；DeviceCounter Offset4/Width8/LittleEndian/Unsigned读18446744073709551615，Signed同字节读-1，原位宽/域不能互用；另一 `00000100` Offset0/Width4/LittleEndian读65536，BigEndian读256。截去最后一byte→边界拒绝，无字段成功补零；重复FrameNumber→输入拒绝；ExposureStart未知Clock频率→保留原tick、TicksPerSecond=null/关联Unknown，不给µs。fixture HasLineProtocol=false、FrameIdentity Unknown，不构造Hardware或Proven触发。CAM.A1.06复用这些实际字节值与§20已接收UInt64/padding向量，不新建过程文件/假设备Golden。

### 8.3 HALCON Adapter 的装配、数据与停止

唯一工程/命名空间沿A.8的 `Adapters.Halcon`；公开 `HalconCameraTransport` 实现 `ICameraTransport<IFrameLease>`，构造 `(HalconAcquisitionGate gate, HalconAcquisitionProfile profile, IHalconFrameAdapter imports, IFrameService frames, ICameraClock clock, CameraLimits limits)`。IHalconFrameAdapter是image-frame §19.1既有公开适配器，不另造HObject租约；HALCON类型只在本Adapter内部，全部算子经ImageLibDotNet.cv2。gate是本包sealed class，无参构造；Host给进程内全部此类Adapter同一gate，串行§18.2 exclusive open/close/info并协调活跃handle。它不取得设备命令Owner、不替代access；Host禁止其它路径绕过此gate争用句柄。构造不open，原Core恢复槽保有所有借用。

公开Profile字段固定为 `string ProfileId, Revision; CapabilityEvidence Evidence; CameraCapabilities CapabilityTemplate; HalconOpenSpec Open; HalconGrabRoute Route; CameraProtocolLayout Protocol; A<CameraNodeBinding> Nodes; TimeSpan NativePollBudget; bool AbortFromOtherThreadProven, PrefetchAuthorized; A<PlaneRole> Roles; A<PlaneMetadata> Metadata`。Route={SynchronousImage,AsynchronousImage,AsynchronousData}；Nodes沿§8.2封闭语义角色，数值/字符串按对应setting及官方接口参数类型传tuple，不开放任意SDK调用。`HalconOpenSpec`为record：`string Name; int HorizontalResolution, VerticalResolution, ImageWidth, ImageHeight, StartRow, StartColumn; string Field; int BitsPerChannel; string ColorSpace; double Generic; string ExternalTrigger, CameraType, Device; int Port, LineIn`；字段顺序即open_framegrabber的16项输入。所有值由具体acquisition interface资料确定，含其允许的0/-1/特殊值，不能机械套传感器正尺寸域。非有限Generic拒绝；不接受外部任意HTuple。Profile的Revision以§8.2同值规则对ProfileId/Evidence稳定来源/CapabilityTemplate.ContentHash/Open/Route/Protocol/Nodes/NativePollBudget.Ticks/两个bool/Roles/Metadata编码求hash，double（Generic及Metadata.Scale/Bias）采用有限G17 invariant往返形式；不含自身Revision/ObservedUtc。

Connect经gate：info_framegrabber核指定Name和设备信息→按Open原值open_framegrabber→get_framegrabber_param读能力/当前配置，setter只使用对应节点的已核类型/范围；不以通用GenICam节点名猜HALCON interface参数名。SynchronousImage用一个专属worker调用grab_image，设备接口必须提供已验证有限等待/停止语义；NativePollBudget只写接口资料支持的取图等待参数，不用MaxDelay假超时。异步路线arm时grab_image_start，然后grab_image_async/grab_data_async的MaxDelay固定-1，关闭超龄重抓；仍需PrefetchAuthorized证明预取不会制造未授权曝光，缺此证明拒绝该异步模式，保留可用的显式同步模式。不得运行中混用同步/异步或自动换接口。

取得Image后先核count_obj=1与Roles/Metadata/通道布局，再用原HObject调用imports.ImportCopyAsync（HalconImportRequest全部字段沿image-frame §19.1）；原Import Task/ServiceEpoch/RequestId在取图前预持槽，OperationResourcesReleased前不Dispose输入、不开始会覆写该借用的下一次grab。成功CPU发布再按§8.2 Read/移交/Retire；Import未知只Query原adapter操作，不能再次import同源造成功。grab_data_async返回的Regions/Contours/Data同批在原worker/持有槽中逐一登记、退出后释放；数据映射只有设备已证明的固定typed事实才进入§20入口，无行协议时NoLineProtocol，不把Data索引猜曝光或运动。未使用的非图像对象也须释放，不能只Dispose Image。

停止为封输入→若AbortFromOtherThreadProven，控制worker执行set_framegrabber_param('do_abort_grab',接口定义值)一次→等待原grab和全部import/source借用真退出→Dispose本次图像/tuple/非图像结果→gate内close_framegrabber→释放grant。无abort能力则等待原有限grab返回；观察期限到仍保有handle/Task，不用close破坏在途指针。错误包含acquisition interface原码、原operation和资源轴；不重复成功阶段。不设置全局set_system，不核AsunImage内部/授权，也不把运行时重载/真实设备资格转成已验证事实。

## 9. 无 UI 最小 Host 与两消费者

最小 Host 是A.8/A.9的普通.NET 10 console，显式注入端口/limits，不加载WPF、DevExpress、HALCON或SDK。以下为按现有公开合同可实施的语义例，不是已编译源码；`查询并记录`、`有限观察`、`记录异常`只是TestHost本地控制流，不是新增Core入口。不得使用`await using core`后丢弃失败实例。

### 9.1 先取得恢复槽和操作身份

每个mode只有**一个Host恢复槽**，在Discover/设备动作前分配固定记录与观察任务容量，槽未能分配则拒绝开始。槽字段为原`core/sink/transport/frames/ledger/access/clock`引用、selector、authorityToken的安全引用、预生成connectId/captureId/stopId/closeId、各入口是否已尝试、所有尚未完成的Task、最近回执/异常和`CleanupObserved/OwnerRetained`；不是另一份产品状态或设备授权。Core构造后立即登记到槽，sink构造后立即登记；任一装配失败归还本Host已取得资源，不访问未创建实例。槽保留至本实例实际清理已确认；未知时它和原组合根继续存活，禁新建同设备Core或清空旧slot。原组合根从创建就是Owner，不依赖临时窗口或未定义的恢复服务。

Host fixture的总恢复观察窗口是独立单调10s：Query每次Total=2s/Queue=1s，显式Stop/Close每次Total=3s/Queue=1s，limits.CleanupBudget=3s、DisposeBudget=3s；全部取剩余恢复窗口，不在每层重置总10s，剩余不足时只保留任务/Owner而不开始又一个完整等待。页面/正常操作token与恢复窗口分离；清理调用使用`CancellationToken.None`，外层有限观察只结束等待，不取消或忘记已接纳清理。Host记录原Task以收取迟到结果，禁止每次timeout重发调用。 剩余Total>0时Queue取min(1s,剩余Total)，保证0<Queue≤Total；已无观察时间则不构造0/负Budget。最后finally仍立即调用一次原DisposeAsync（内部使用原limits.DisposeBudget），保存Task而不等待，所需槽从启动前已预留；后台必要清理仍有独立预算，前台10s窗口不被延长。10s是模拟Host的软件恢复观察fixture，不是实机排空/急停性能承诺；真实Host的窗口来自其已接收Profile。

精确selector来自Host配置并与Discover候选核对，不默认首台；在Connect前已持有selector、connectId、captureId（不是等ticket才取ID）。`SessionIdentity? session=null`；只能从Success SessionReceipt或授权Query返回的原Connection中取得**已完成移交**的session。未知Connect回执的OperationSnapshot.Session可能只是连接尝试内部预分配身份，不能当成成功session，也不能用new SessionIdentity补假的关闭参数。

### 9.2 正常、未知和异常共用 finally

```text
取得一个恢复槽，预持selector/connectId/captureId/stopId/closeId和独立预算
装配原core与sink；把所有原引用登记在槽；session=null；connectAttempted=captureAttempted=false
try:
    DiscoverAsync → 必须找到精确selector；否则记录拒绝并进入finally
    connectAttempted=true （必须在调用前置位）
    ConnectAsync(ConnectRequest(Command(connectId,key,budget),selector,authorityToken), workToken)
    若Success且SessionReceipt有效：session=Value.Session
    否则：有限QueryOperationAsync(OperationQuery(connectId,selector,authorityToken,queryBudget), None)
          仅原Connection已确认移交且原Core仍Ready时可记录该session；本次不自动续发Apply/Capture
          进入finally；Unknown/NotFound不再Connect，不根据返回时间推断设备未打开
    GetCapabilitiesAsync(SessionQuery(session,budget),workToken)
    ValidateConfiguration → ApplyAsync → 检查每个实际readback及confirmed revision
    任一步非Success、partial/unknown或异常：记录原operation后进入finally
    captureAttempted=true （在CaptureAsync前置位）
    CaptureAsync(显式带captureId的CaptureRequest,原sink,workToken)
    若未返回有效Armed票据：保留captureId并进入finally，不等票据才登记清理身份
    若Software：逐预约TriggerAsync；否则等待Host自有外触发
    WaitCaptureAsync(CaptureQuery(captureId,queryBudget),workToken)
    消费原sink帧；任何消费异常在消费者finally归还自己的lease，然后进入Host finally
catch 所有操作/查询/消费异常（包括等待取消）：
    记录错误，不把异常变成功，不在catch重新触发/连接
finally:
    try:
        先阻止sink接收新消费任务；启动原sink.DrainAsync(cleanupBudget,None)，保存其Task
        若captureAttempted且有已移交session：
            同时启动StopAndDrainAsync(StopRequest(Command(stopId,key,cleanupBudget),session,captureId,Reason),None)
            Reason按原失败/显式取消/正常完成选择；Capture未接纳可得到NotFound，无需造ticket
        对sink/stop分别有限观察并记录；一个失败/超时不能跳过另一个的观察/保留
    catch 清理/观察异常：记录并保留原Task/lease
    finally:
        try:
            若有已移交session，原core尚未Disposed且Snapshot仍为该session：
                CloseAsync(CloseRequest(Command(closeId,key,cleanupBudget),session),None)，有限观察/记录
            若无已移交session：跳过公开CloseAsync；不能向它提交假的session
        catch Close/观察异常：记录，仍进入下一层finally
        finally:
            对仍持有的原core调用一次DisposeAsync并保存Task，以剩余窗口有限观察
            正常完成/CameraDisposalException/其它异常全部记录；不以异常退出丢原Core
    完成上述嵌套finally后，有限查询connectId（若尝试）、captureId（若尝试）及close/Dispose实际原ID
    每次查询自身try/catch；查询失败不反向跳过已安排的Close/Dispose，也不再次创建设备动作
    同一槽内确认本次清理结论并登记结果；有未确认资源/Task/Owner则槽保持占用
```

`RecordingFrameSink.DrainAsync`的精确返回形状为`ValueTask<CameraReply<ResourceSnapshot>>`，只请求本sink停止准入/归还并有限观察；false/异常移交路径仍按A.5保有唯一Owner。所有消费任务持有原frameport，finally释放且与Stop/Dispose并行，不等待资源终态才归还帧。Snapshot用于判断本进程状态，不能替代未知native/ledger事实；`Stop`在captureId根本未接纳时返回NotFound/CAM-OPERATION-NOT-FOUND且不触碰其它capture，Host仍Drain自己sink并清理本session。成功Dispose之后仍可授权Query原ID；UnknownTrigger等设备事实可留NonTerminal，需要保留耐久对账记录，但不得据此重新打开或声称采集成功。

### 9.3 未移交 Connect 的 Dispose 与有限保留

未移交连接由**原Core**持有实际connecting session/handle/grant（若已取得）、原connect operation和进行中Task；Host只有connectId也能调用现有DisposeAsync关闭准入、等原Connect任务真实结束/清理。不需要公开的新入口，也不需要Host构造SessionIdentity。Dispose的固定close identity按A.6.1规则：已有已移交session时base=session.SessionId；否则有已尝试Connect时base=原connectId；完全未尝试Connect时base=core.Snapshot.InstanceId。前缀仍为`CAM/1/dispose/`，同一Dispose尝试首次确定base/ID后冻结，晚到Connect结果不得换ID再发close。key=`dispose/<base小写D>`；Host本地可按A.6.1的SHA256/Guid字节规则预测，但实际ID以CameraDisposalException.OperationId或原Close回执为准，查询时仍保留connectId。Dispose前若Core已经完成真实Session移交但Host尚未收到，base取原Core真实移交身份，不能按Host的null session重置base。只有未创建core才无Dispose动作。

有pending Connect时Dispose close记录使用原selector/OwnerNamespace、Session可null、CloseReceipt可null，Stages与Resources必须保留实际清理；Core仅在自己内部已有真实session时调用transport.CloseAsync，未open且已确认不执行open则不发native close，只结束临时资源/正确归还grant。原Connect Task仍运行、是否open未知或native释放失败时，Dispose有限返回CameraDisposalException，其OperationId是该固定close ID；core保持Faulted并保留所有依赖，不能Disposed、不能放grant。晚到Connect成功也禁止发布Ready/向已关闭准入移交会话，直接归原关闭任务清理；已成功native close/release不重复。预算到时Host保存该Dispose Task/ID，后续只能观察原Task、Query原connect/close及必要时重新Dispose观察同一未完成阶段，不重新Connect。账本记录失败时Query可Unknown/NotFound，必须保留异常Fault/原Snapshot/Task，不将其当释放证据。

完全未尝试Connect且无任何资源时Dispose直接完成、状态Disposed，不强行造selector或ledger close记录；只有这个已证实纯无设备路径，预测Dispose ID的Query可NotFound且不妨碍确认无资源。曾尝试Connect的NotFound不能用该例外。成功清理确认要求原任务全部实际结束、sink HeldCount=0、CountsComplete且本操作的callback/worker/buffer/lease/temp全部归还、device grant/handle已释放、core Disposed；异常/设备未知仍分别记失败/待对账。

有限移交是**同一Host槽内**的模式从前台运行转为原组合根的恢复持有，不是新设备Owner：在剩余窗口内2s完成门内标记OwnerRetained=true并核原引用/Task/ID均仍在该槽，确认后前台返回“未确认清理”，总体结果非零。不能分配另一个槽或临时“恢复服务”后清空旧槽；确认失败则原前台/组合根仍保有槽、禁退出Owner。未确认时测试模式可非零结束报告，但不能宣称杀进程已停止设备；实际Hardware宿主继续保留原Owner并遵守外部治理。无资源成功才撤槽，前台取消不释放槽。

| 消费者 | 必需装配与真实消费 | 独立性断言 |
|---|---|---|
| 视觉检测宿主 | 自有selector/权限/配置/帧sink及一个恢复槽；只消费可信关联帧，算法自身finally归还；运动/光源/质量放行留宿主 | 无Shell/产品DB也运行，消费异常不跳过原Core清理；Core不收板/FOV/工单/PASS/NG |
| 独立采集工具 | 自有console/配置/日志/sink/恢复槽；同Core+Simulator或MVS Adapter单拍/有限连续/线扫块，完整执行§9.2嵌套finally | 删除检测宿主仍构建，UnknownConnect无session也保住原Owner；不改Core，不绕过物理独占 |

共享TFrame/模拟ManagedTestFrame及真实端口切片沿用A.5/A.9/A.11；本例不改变共享契约、设备权限或帧所有权。


### 9.4 本次两轮有限走读结论

| 走读 | 固定反例 | 收口断言 |
|---|---|---|
| 第一轮：调用者按公开合同执行 | UnknownConnect无Session、Capture返回前异常、Query/消费异常 | Connect/Capture尝试标志在调用前置位；session只取真实移交结果，缺session跳公开Close/Stop并由原Dispose清理；Query失败不能越过嵌套finally。CAM.C1.16/17 |
| 第二轮：Owner在截止和晚到结果后继续持有 | 恢复预算已耗尽、Dispose抛错后连接才返回、保留槽未确认、case时钟停滞 | 最后finally始终对原Core触发一次Dispose，即使剩余观察为0仍保存其Task不等待；Dispose固定ID首次冻结、晚到结果归原任务清理、不发第二close；槽移交失败保留原Owner。虚拟闩锁和真实10s/120s/180s各自有限，未完成非零 |

这是规格路径走读，不是Host或BCL Exe运行。§17.2已同步主控对C1六项及本次Host退修的内容接收（仅规格准备）；已核算法、来源、摘要向量、平台映射及其它切片未重开。

## 10. 可选 UI 契约

本节为模块可嵌入采集工作台的实施候选 PageContract，不另建页面权威。操作角色是设备调试员和维护员；宿主决定权限，生产操作者仅看到宿主允许的连接、采集、停止和状态。宿主注入 Core、帧投影、权限、三语资源、主题、布局存储及生命周期，不在模块重复放语言选择器。Core 不依赖 WPF 初始化。

### 10.1 布局、控件与操作链

仅以 1920×1080 验证窗口，实际可用区域扣除系统任务栏、窗口边框、标题栏、宿主导航和状态栏，不更改用户显示设置。中央影像占可用主区至少 60%；侧栏按最小可读宽度约束并可收起高级参数，空间不足优先收起诊断详情，不压缩主图或隐藏停止。首次进入采用宿主主题、统一间距/字阶和语义图标；颜色同时配状态文字与图标，动效只用于面板展开/状态过渡，不遮挡错误或延迟停止。

| 区域 | 具体内容与 DevExpress 25.2.3 候选 | 行为与可判定验收 |
|---|---|---|
| 顶部常显命令/身份 | 发现、连接/关闭、应用、开始、停止；精确设备摘要、Hardware/Replay/Simulation 来源、session/epoch、配置修订 | 连接不隐式开始；应用与开始互斥；停止始终可见。未知排空时显示“资源未归还”，禁重新开始/连接；只读权限不发设备命令 |
| 左侧设备列表 | `GridControl` + `TableView`，状态/接口/型号/稳定标识摘要，精确单选 | 刷新不自动切换当前设备；断连保留选中项和原因。选中行与能力/诊断联动，不选择首台默认连接 |
| 中央影像 | 注入的 viewport 控件，原始尺寸/格式/有效性/帧身份、显示缩放与选帧 | 只持独立投影 lease；选帧同步定位诊断行/时间点。图像变换不修改原帧；无新帧显示最后有效帧及“已停止/断开”，不冒充实时 |
| 右侧基础参数/高级参数 | 基础字段表展示 requested/applied/readback/actual；高级 `PropertyGridControl` 显式 `PropertyDefinitions`，禁直接暴露 SDK 属性对象 | 草稿可编辑但不自动写设备；校验定位字段并显示量程、单位、步进/连续域及能力 revision；能力未知显示“尚未读取”，明确不支持显示“设备不支持” |
| 底部诊断 | 只读 `GridControl`，必要时 `ChartControl`/`LineSeries2D` 显示队列水位/交付延迟；错误、原码、阶段、operation、停止/资源计数 | 图表点击定位同一 operation/frame 记录；UI 显示队列有界且按注入刷新间隔批量更新。显示节流单列计数，不改变生产 sink 交付集合 |
| 布局与说明 | `DockLayoutManager`、`LayoutPanel`；非关键诊断可 `AutoHideGroup`，主命令禁止关闭/浮动隐藏；非显然命令用 `BarItem.SuperTip`，复杂说明用 `DevExpress.Xpf.Editors.Flyout.FlyoutControl` | 宿主恢复可信的同版本布局，损坏布局回默认；不反序列化任意外部布局。提示说明限制和恢复，不堆 SDK 术语或宣称性能 |

采用 `DataControlBase.ItemsSource/SelectedItem`、`DataViewBase.AllowEditing/NavigationStyle`、`TableView.ShowAutoFilterRow/AutoWidth` 实现只读诊断/单选设备；`PropertyGridControl.SelectedObject` 绑定强类型草稿投影而非 Core 可变配置；`BaseLayoutItem.AllowClose/AllowFloat` 保护关键面板。布局保存/恢复用 `SaveLayoutToStream/RestoreLayoutFromStream`，授权、验证和持久化仍由宿主完成。精确命名依据 §18 的本机官方 XML；不要求为使用控件而堆叠面板。

任务链固定为：发现 → 精确选择 → 连接/读取能力 → 编辑草稿 → 验证/应用并检查差异 → 选择有限采集请求 → 开始 → 软触发（若适用）/等待宿主外触发 → 查看计数及逻辑结果 → 停止/归还帧 → 确认排空 → 关闭。硬触发入口显示“等待外部触发”，不伪造软件按钮控制外部设备。配置 partial 时保留草稿与读回差异，提供“重新读取能力/当前值”及关闭；不提供盲目“重试全部”。触发未知时提供原 operation 查询，禁止再次触发同 reservation。

### 10.2 线程、键盘、语言与恢复

UI 只调用附录 A 的同一校验/操作入口，所有异步命令不阻塞 Dispatcher。选帧/图表导航仅操作投影；不可在事件处理器同步等待 Stop/Close，关闭页面只撤订阅和归还本页 lease，将仍运行的会话交还宿主 Owner。开始/应用的失败显示字段/阶段和下一动作；停止请求后显示“正在停止”，驱动排空后仍有租约则显示“等待帧归还”，`ResourcesReleased` 后才显示“已停止”。未知不能使用绿色完成图标。

Tab 顺序为设备 → 连接 → 基础参数 → 应用 → 采集参数 → 开始/软触发 → 停止 → 影像 → 诊断；Enter 仅执行焦点所在命令，Esc 仅关闭浮层，不承担设备急停或隐式停止。按钮提供稳定 AutomationId、可读名称、禁用原因；列表支持键盘选行，校验失败焦点移到首个错误字段。宿主三语热切换保留草稿、选帧、operation 与资源 Owner；日期/数值显示随语言变化，API 单位与小数序列化不变。

最小文案资源包括“连接/連線/Connect”“开始采集/開始擷取/Start capture”“停止/停止/Stop”“等待外部触发/等待外部觸發/Waiting for external trigger”“等待帧归还/等待影格歸還/Waiting for frame return”“资源状态未知，请查询原操作/資源狀態未知，請查詢原操作/Resource state unknown. Query the original operation.”。参数、状态、错误、提示、日志投影和恢复动作全部资源化；设备原始码作为诊断附值，不替代本地化说明。

真实 UI 验收在固定 1920×1080 可用视口执行三语、实际 DPI、键盘/UIA、最小栏宽、长错误文本、布局损坏恢复、慢预览、断连、partial、未知触发及持帧停止；检查无裁剪/命令遮挡、焦点可达、UI 不挂起、关闭不丢 Owner。视觉验收单独检查主题、图标、对齐、间距、主图比例和状态动效。显式挂接/代次/权限/关闭形状见A.10；本轮是可执行设计，尚未运行 WPF 或 UI 验收。

### 10.3 固定工作台装配、参数编辑和命令输入

C5的实际控件组合冻结为：一个WPF Grid外壳（顶部命令/主区/底部状态）、DevExpress BarManager/Bar/BarButtonItem常显命令，主区DockLayoutManager含设备、Host Preview.View、参数、诊断四个LayoutPanel。设备和诊断分别GridControl/TableView，只读、单行导航；基础数字参数SpinEdit、枚举ComboBoxEdit、显式模式切换ComboBoxEdit，进阶参数PropertyGridControl的显式PropertyDefinitions。默认不加入ChartControl：表格已可查看计数和阶段，Host需要趋势时才在诊断panel内启用§10.1既有投影，不能增加生产采集路径。API成员按§18.3同版官方XML，不因dxdocs不可用猜属性；本轮dxdocs服务器未配置，已定向复核本机BarItem.Command/SuperTip、BaseLayoutItem.AllowClose/AllowFloat、BaseEdit.EditValue、LookUpEditBase.ItemsSource、SpinEdit.MinValue/MaxValue、PropertyDefinitionBase.Path和DataViewBase.AllowEditing，来源指纹沿§18.3。

布局尺寸是软件设计DIP，不是另一个屏幕测试矩阵：主区默认设备栏224、参数栏304、两分隔各8，中央占其余；诊断默认折叠为一行摘要，展开高度160。可用宽W时，中央最小0.60W；若上述侧栏不能满足该条件，先把设备列表放入AutoHideGroup，再收参数高级组，中央与停止命令不缩小/遮挡。顶栏高度48、状态栏28、常规间距8、分组间距16；长文本换行或SuperTip，字段标签不截断数值单位。主图panel不AllowClose、不AllowFloat，停止所在Bar不放溢出菜单；设备/高级诊断可收起，原设备身份常显。Host实际剩余区域和DPI决定DIP可用宽，验证仍仅1920×1080；不保存当前Session/命令/帧引用到布局。布局Stream限额由Host审批，恢复异常先回固定默认布局，再显示简短提示；不放任意类型反序列化。

基础字段固定为格式、ROI x/y/width/height、binning、曝光模式/µs、增益模式/设备单位、逐selector触发mode/source/edge/delay、采集模式。左右对照草稿/当前读回，partial逐字段显示，不用一行“设置成功”。SpinEdit的min/max只做输入辅助，decimal EditValue按culture完整解析，不用double草稿/自动量化；文本空白表示Unchanged，自动Once/Continuous显式选择且其数值框禁用/null。离散格点仍由Core.ValidateConfiguration判断，步长未知禁写，不能靠编辑器增量证明合法。设备默认按钮仅复制已核Domain.DefaultValue到草稿，记录capability revision；没有default/已过期禁用。既有revision/单位变化时标草稿待重新验证，不自动改实际设备值。PropertyDefinitions.Path仅指这些强类型草稿属性，不生成SDK属性浏览器。

A.10的 `CameraWorkbenchOptions<TFrame>` 末尾字段为 `CameraWorkbenchInputs Inputs`；此为C5候选契约的本轮确定设计，不改C1/已接收向量。`CameraWorkbenchInputs` record完整字段为 `string AdapterId, AuthorityToken; DiscoveryRetryPolicy DiscoveryRetry; CameraSelector? InitialSelection; CameraCaptureDraft Capture`；token仅安全引用不入日志/布局/hash，InitialSelection必须精确发现匹配，null不自动选择。`CameraCaptureDraft` record为 `int ExpectedUnits, QueueCapacity; ulong ReservedBytes; CaptureUnitKind UnitKind; int? LinesPerUnit; A<TriggerReservation> Reservations; CorrelationPolicy Correlation; StabilizationPolicy Stabilization; string? SourceTag`，域复用A.2。来自Host的reservation/token只读；独立工具可以显式选NotRequired/空reservation，不由UI推断物理trigger。attachment新增 `void SetInputs(CameraWorkbenchInputs inputs)`，只更新下次调用的输入投影并派到Dispatcher，不变更已发operation/原票据/原授权上下文。任何更新都在开始新命令前固定一个不可变快照。

全部命令由attachment同一Core执行，无新的Host设备操作接口。新操作预生成Guid与key=`ui/<attachmentId小写D>/<operationId小写D>`，保存原输入/Task/回执后再发；重复查询/点击对账复用原ID，不按重绘生成新动作。设备按Snapshot.Session及真实Connect回执绑定，不能用InitialSelection生成假Session：

| UI命令/AutomationId | 精确请求、权限和完成行为 |
|---|---|
| 发现 / cam.discover | DiscoveryRequest(CommandBudget,Inputs.AdapterId,Inputs.DiscoveryRetry)，CanDiscover；刷新精确列表，不改变已连接selector |
| 连接 / cam.connect | 已选selector+Inputs.AuthorityToken+预持CommandContext构成ConnectRequest，CanConnect且Core.Closed/无未清理实例；pending/unknown只保有原Task并查询，不重open |
| 读取当前 / cam.read | GetCapabilitiesAsync(SessionQuery真实session,CommandBudget)，CanQuery；不Apply。把实际Current更新对照列，保留草稿 |
| 应用 / cam.apply | 当前草稿按A.3生成CameraConfiguration，RequestedRevision为本草稿GuidD，RequestedHash调用CameraCanonical；先同Core.ValidateConfiguration，错误定位首字段；通过后ApplyRequest，CanConfigure且Ready；不在UI重写厂商校验 |
| 开始 / cam.start | CaptureDraft+真实session+当前ConfirmedConfigurationRevision/CapabilityRevision构成A.2 CaptureRequest与原ProductionSink，CanCapture且Ready/CaptureEligible；预算/额度/输入完整才发，ticket只取成功Armed回执 |
| 软件触发 / cam.trigger | 同ticket/未claim且Software的reservation构成TriggerRequest，CanSoftwareTrigger；没有可证明软件预约不提供伪“触发一次”，ACK/Unknown/曝光三栏分开 |
| 停止 / cam.stop | 原ticket/captureId的StopRequest(HostRequest)，CanRequestStop；正在捕获/停止时常显可聚焦，没权限显示原因及原Host Owner处理提示。Close/Query状态不能取消真实清理 |
| 关闭设备 / cam.close | CloseRequest真实session，CanConnect投影+Core最终授权；设备关闭与“关闭本页”分开。无移交session只由原Host Core.Dispose恢复，不编造Close参数；页面始终不拥有Core |
| 查询原操作 / cam.query | OperationQuery原operationId/原selector/原AuthorityToken安全上下文/CommandBudget，CanQuery；改变Inputs或设备选择不改变原Query绑定，越域由Core拒绝 |
| 选帧 / cam.frames | A.10 PreviewSelection指定capture/source key/revision；只读投影，无设备动作；无同revision帧保留最后图且显示状态，不偷偷显示latest |

对有device副作用的按钮采用每attachment单飞：运行时禁用发新Apply/Start/Connect/Trigger，Stop/Query保留独立清理路径；不把bool Busy锁住停止。主路径触发完成后仍等待Core事件/Snapshot/Query，UI通知不当物理完成。取消等待只保有原Task，按钮不因此变“可以重发”。配置校验错误/显式stop/断开走同Core，不写设备SDK。

固定新增三语资源（key以cam.开头，原错码与参数单位单列）：

| key后缀 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| readCurrent | 读取当前值 | 讀取目前值 | Read current values |
| useDefault | 使用设备默认 | 使用設備預設值 | Use device default |
| draftExpired | 能力已变化，请重新验证 | 能力已變更，請重新驗證 | Capabilities changed. Validate again. |
| configPartial | 设置未全部完成，请读取当前值 | 設定未全部完成，請讀取目前值 | Configuration incomplete. Read current values. |
| triggerUnknown | 触发结果未知，请查询原操作 | 觸發結果未知，請查詢原操作 | Trigger result unknown. Query the original operation. |
| noStopPermission | 无停止权限，请联系设备负责人 | 無停止權限，請聯絡設備負責人 | Stop permission required. Contact the device owner. |
| previewFailed | 图像未更新，已保留上一帧 | 影像未更新，已保留上一影格 | Image not updated. Previous frame retained. |
| layoutReset | 布局无法恢复，已使用默认布局 | 版面無法還原，已使用預設版面 | Layout could not be restored. Default layout applied. |
| rowProtocolMissing | 设备未提供逐行事实 | 設備未提供逐行事實 | Device provides no per-line facts. |
| closePage | 关闭本页 | 關閉本頁 | Close page |
| closeDevice | 关闭设备 | 關閉設備 | Close device |

全部A.4错误码映射§5/A.4 RecoveryAction到FixInput/ReadCurrent/QueryOriginal/ReturnFrames/CloseWhenDrained/AskDeviceOwner的三语文案，安全参数只显示字段、设备摘要和原operation短码；native异常放诊断，不能只把英文异常当中文结果。模式/单位/数字格式随语言显示，设备enum token只作技术附值，不把未经设备定义的enum改名写回。三语列表为首版资源，新增culture由宿主ResourcePort提供并按同Key查找，不增Core分支。

### 10.4 Dispatcher、预览根与双宿主验收

Host在调用AttachAsync前预持view/options/Preview/原Attach Task与一槽；Factory在任何订阅/嵌入View/Select之前先将attachment强持到view附加状态槽，槽含原AttachmentId、generation、subscription、刷新Task、全部Select原Task和Preview引用。`CameraWorkbenchFactory.GetAttachment<TFrame>(CameraAcquisitionControl view)`为新增公开同步只读入口，返回 `CameraWorkbenchAttachment<TFrame>?`，同Dispatcher调用；尚未登记返回null，登记后即使Attach未移交也返回原对象。Attach失败不能清空活借用槽；Host用该入口取回原attachment再Close，不为同view另Attach。槽只有本页资源真归还/全部原Task退出后才清空；预算到期/页面Unloaded不是释放证明。

生产Preview桥的确定调用者是Host的viewport Owner；其公开端口仍仅A.10，借用关系按以下固定实现：SnapshotItems只返回有界元数据；Select精确核原revision，取得viewport接受的独立投影lease并在attachment槽保存，然后派Dispatcher呈现，只有呈现调用真结束才Presented。无需新增显示算法/持有生产sink帧。新选帧先Release旧generation；旧Select未知时不开始第二个Select，等待/取消只观察原Task。Release封本attachment/旧generation新显示，等原Select/Dispatcher退出，按实际独立lease归还，Released证据不足保留原View/port/Task。旧代次晚到不得更新新图；不能先清Preview.View.Content再声称释放。Dispatcher已shutdown且无法确认呈现/归还时返回Unknown，保留原槽交同Host进程Owner处理，不反复BeginInvoke或另建Dispatcher。具体viewport厂商绘制/资源借用由已批准viewport端口实现，不下沉为相机算法。

CAM.W1沿A.10扩为CAM.W1.06～09：06未移交Attach/Dispatcher异常可GetAttachment找回原槽且实际归还一次；07挂接前无token/采集draft拒绝、草稿partial/default/revision/权限热更新、每个命令与console请求同形；08慢Select/新选帧/关闭只原Task有限观察、旧代次不呈现、不提前IsClosed；09真实DevExpress命令/数值编辑/三语资源/损坏布局和键盘。双WPF宿主各为独立STA：一为独立采集工具，一为检测应用的嵌入工作台；各自注入同契约的Core/资源/Preview，STA与Core实例互相隔离；Fake Preview只用于闩锁/资源断言，不冒真实viewport通过。测试只在原A.8 Tests.Wpf候选工程实现，先STA构造Dispatcher→view→登记组合根→Attach→发现/选设备/草稿/有限采集/选帧→语言/权限更新→Close attachment→Host sink归还/Core Stop/Close/Dispose，全部嵌套finally原引用强持；每例/全套/外层10s/120s/180s沿已冻结边界，未完成/跳过非零。真实WPF只有固定1920×1080视口，不调整显示分辨率。

## 11. 正常、边界与失败场景

| 场景 | 输入/事件 | 期望结果 |
|---|---|---|
| 正常单帧 | 能力完整，ROI/曝光/格式在范围内，软触发回执和唯一帧键有效 | 配置逐项读回；按事件序交付一个有效 lease；停止/drain 后所有资源计数归零 |
| 外触发多帧 | 固定 N 帧、有限队列，外部触发身份可追溯 | 每帧独立关联；到齐只表示模块收到 N 帧，不作覆盖/质量判定；Stop 后禁止新帧加入该 epoch |
| ROI 边界 | ROI 正好满足设备右/下界、步进合法 | 校验通过；回读尺寸/偏移如设备支持，否则报告读回能力限制 |
| ROI 越界/非法步进 | 负坐标、零尺寸、越界或非步进值 | `CAM-INPUT-INVALID`，无设备副作用 |
| 不支持增益/格式 | 能力明确标不支持，调用方仍请求设置 | `CAM-UNSUPPORTED-CAPABILITY`，不能忽略字段后声称整组成功 |
| 部分配置失败 | 曝光已应用，ROI 被拒绝/读回超时 | 返回逐字段状态和当前读回；禁止假回滚；依赖 ROI 的采集被阻断，宿主决定恢复 |
| 触发响应丢失 | 触发命令可能到达设备，ACK 超时 | 返回 `CAM-TRIGGER-UNKNOWN`；不自动重复触发；查同一 operation 回执/设备状态 |
| 重复与冲突帧 | 同 epoch/触发键重复且 payload 相同 / payload 不同 | 相同内容不重复计数；异内容隔离并报冲突；不 last-wins |
| 断连后迟到帧 | 旧 epoch 回调晚于重连到达 | 旧帧隔离；新 epoch 序号/能力独立，不进入新会话 |
| 取消时消费者持帧 | 下游仍持有已交付 lease 时请求 Stop | 驱动回调排空与下游 lease 归还分开报告；未归还时不宣称 fully drained 或重用物理 buffer |
| 队列满 | 设备不能暂停且有新帧到达 | 明确 overflow/丢失区间并受控终止；无静默丢帧或扩容到无界 |
| Stop/Close 超时 | SDK worker 或 callback 未退出 | `CAM-DRAIN-INCOMPLETE`，保留 outstanding 资源/设备占用标记；不能 Dispose 后重开 |
| 模拟/回放输入 | 文件或合成帧通过同一 Adapter 契约 | 输出带 Simulation/Replay 来源；可验证软件链但不得据此宣称硬件曝光、同步或节拍通过 |

## 12. 第二轮场景驱动架构复审

本节是对本模块的反例复审，不是产品验收结果。每个场景都必须由 Core 先依据输入快照和能力 revision 做无副作用校验，再由单一适配器执行；输出同时包含模块状态、错误/未知语义、资源计数和可查询的 operationId。调用方的板件、目标、工艺和放行含义不进入这些场景。

| 场景 | 输入与参数来源 | 处理顺序 | 输出、状态/错误和恢复 | 可判定验收 |
|---|---|---|---|---|
| 正常配置与单次执行 | 选择器来自宿主；能力来自本 session；ROI/格式/曝光/增益来自调用方不可变配置快照；预算来自调用方 | Connect → 读能力 → 校验全部字段/依赖 → 逐项应用 → 逐项回读 → Capture → 校验并移交帧 → StopAndDrain | `Ready → Configuring → Capturing → Stopping → Ready/Closed`；每个字段有 Accepted/Applied/ReadBack；返回逻辑结果、`DrainCompleted` 和 `ResourcesReleased` 回执 | 同一输入重放得到同样的校验结果；设备没有未请求写入；帧布局、epoch、配置 revision、lease 所有权均可追溯，资源计数归零 |
| 空输入 | 空设备选择器、空能力集合、空配置、0 帧请求、空帧 sink 或非法队列容量（状态订阅者可为零） | 在获取设备/申请 buffer/注册回调前拒绝；不调用 open、set 或 trigger | `CAM-INPUT-INVALID`；保持 `Closed/Ready` 原状态；无回调、无句柄、无驱动副作用 | 监视适配器调用计数为 0；错误指出具体缺项；重复提交不会创建 operation 或资源 |
| 部分成功配置 | 配置字段来自同一 revision，但设备只接受部分字段或读回超时 | 先完成已接受字段，再停止后续依赖字段；保留每项实际结果，不猜回滚 | `CAM-CONFIG-PARTIAL`；相关配置 revision 标为 `Partial/Unknown`；禁止进入依赖未确认字段的 `Capturing`；宿主先完整读回或关闭 | 读回快照能重建每个字段的实际状态；不得出现“整组成功”；失败路径释放临时值和订阅 |
| 部分帧/提前结束 | 请求 N 帧，设备仅交付 K<N，或来源明确报告缺帧 | 按稳定 frame key 检查已到、明确缺失、冲突；封口后隔离迟到帧 | `CaptureOutcome=Incomplete` 或 `CAM-CAPTURE-TIMEOUT`；不补零、不把 K 当 N；宿主决定新 operation/补采策略 | 缺失集合和截止屏障可重算；迟到帧不改已封口集合；旧 operation 与新 operation 可区分 |
| 歧义与错误输入 | 单位未声明、能力 revision 过期、同一配置字段重复且值冲突、触发 ID 不可关联、相同键不同 payload | 在硬件副作用前拒绝；运行中歧义进入隔离通道，不采用最近时间/数组顺序/last-wins | `CAM-INPUT-INVALID`、`CAM-FRAME-CONFLICT` 或关联 `Unknown`；保持原会话，禁止伪造完整帧 | 每个拒绝都带字段/关联键和来源；相同输入不产生设备写入；冲突不增加完成计数 |
| 超大帧/大批量 | 能力报告的最大 stride/plane/chunk、请求帧数、队列容量和内存预算；不得由 `width×height` 猜容量 | 启动前计算上限并预留；不足则先拒绝/降级到调用方明确的新配置，不占设备后等待内存 | `CAM-INPUT-INVALID` 或 `CAM-QUEUE-OVERFLOW`；禁止无界扩容、静默 DropOldest/latest-wins；宿主重新提交新 operation | 压力测试中峰值内存不超过 profile；拒绝发生在 trigger 前；任何未转移 buffer 都有唯一释放记录 |
| 高并发/多实例 | 多宿主线程、两个 Core 实例、同设备 selector、多个只读订阅者 | 宿主 access 端口建立跨实例唯一命令租约；Core 串行本实例操作，HALCON Adapter 另串行全局 exclusive 操作；帧读取可并发但 lease 独立 | 第二写 Owner 得 `CAM-DEVICE-BUSY`；订阅者异常隔离；实例取消不影响另一实例 | 两实例不会交叉写配置或关闭句柄；事件带 session/epoch/sequence；取消 A 后 B 的帧和 lease 不改变 |
| 噪声/遮挡/退化输入 | 帧 payload 完整但图像有噪声、遮挡、饱和、低照或运动模糊；质量阈值若有，来自宿主/PKG-013，不由本模块生成 | 模块仅校验传输完整性、stride、CRC/chunk（若适配器提供）、来源/时间；不运行缺陷/质量算法 | 传输有效则正常交付，并保留 `ImageCondition=Unknown/Unassessed`；传输无效才报 `CAM-FRAME-INVALID`；宿主/质量模块决定拒识或重采 | 同一退化帧不被模块误判 PASS/NG；无质量算法或训练集进入 Core；有效帧仍可被 Replay 复现 |
| 取消/超时/native 未排空 | 取消 token、单调预算、适配器停止能力和当前 outstanding callback/buffer/lease | 关闭新准入 → 请求停止/abort（仅适配器声明支持时）→ 隔离迟到回调 → 排空 worker/native → 等 lease 归还 | 显式Stop取消形成逻辑Cancelled；等待token取消为WaitCancelled不改变capture，总预算到期为逻辑TimedOut/`CAM-CAPTURE-TIMEOUT`；若资源未知则追加 `CAM-DRAIN-INCOMPLETE`，不重开/重用设备 | Stop receipt 明确“请求已发/设备已停/回调已空/lease 已空”；任一未知不会显示 Stopped 或允许新 Start |
| 资源上限/背压 | 队列容量、driver buffers、PKG-006 lease 和预览容量来自 profile/能力；外触发是否可暂停来自适配器 | 关键帧走有界可靠队列；预览走独立投影；达到水位按设备能力暂停或受控失败 | 生产队列不得静默丢帧；不可背压时 `CAM-QUEUE-OVERFLOW` 并停止/隔离；预览丢帧只记诊断 | 高水位、丢弃区间、停止原因和物理 buffer 数可观测；慢 UI 不改变生产交付集合 |
| 持久化与修订 | 配置快照/能力快照可由宿主持久化；模块输入带 Schema/API/Adapter/设备能力 revision 和 hash | 模块只校验、应用、回读；持久化写入由宿主或明确注入的存储端口执行；先写临时 revision，回读成功后才发布引用 | 存储失败不撤销已发生硬件副作用，返回 `Unknown`/诊断；旧 revision 不自动应用；新 revision 与 operation 绑定 | 重启后能区分 requested/applied/readback/actual；损坏/缺失快照不触发设备；同一 revision 幂等查询不会重复写硬件 |
| 升级/回退 | 新旧 Core/Adapter/Frame Contract 兼容矩阵、当前设备固件和配置快照 | 先停止新触发并完成或明确失败 drain → 校验版本/能力 → 迁移字段并读回 → 新包新 session；回退按同顺序 | 不兼容 `CAM-UNSUPPORTED-CAPABILITY`/版本错误；未知资源时保持设备不可用；不重放未知 trigger/config | 升级中不存在新旧包同时持有设备；回退后事件/帧语义不变或主版本明确拒绝；迁移失败无设备写入 |
| 无 UI 调用 | 控制台/服务/Replay 宿主直接注入 Adapter、时间源、诊断和 frame factory | 与 UI 完全相同的校验、事件、错误、取消、lease 和 drain 顺序 | 无订阅者仍能完成；诊断 sink 失败不改变结果；返回值是唯一操作结果来源 | 移除 WPF/DevExpress 引用仍可构建并运行模拟/文件 Adapter；同一非法输入与 UI 得到相同错误 |
| 可选 UI | 宿主提供语言、主题、权限和能力投影；编辑草稿含配置 revision | UI 只调用 Core Validate/Apply/Start/Stop；显示 requested/applied/readback/actual 与 Simulation/Replay/Hardware 来源 | UI 关闭只撤订阅；`Stopping/Draining` 未完成不能显示 Stopped；不支持项显示原因 | UI 不持 native handle、不重复校验、不发其它设备命令；慢 UI、切换语言或关闭窗口不影响 Core 资源 |
| 第二消费者 | 独立采集工具自有选择器/配置/日志，不引用视觉检测宿主 | 使用同一 Core/Adapter/PKG-006 合同完成 discover→configure→capture→cancel→drain | 结果/错误/资源语义与视觉检测消费者一致；工具自己的流程不回写模块 | 删除任一消费者仍能构建模块；核心无需制程字段、产品 VM 或私表 |
| 长期运行/重连 | 由 profile 给出的运行时长、帧率、温度/链路诊断、周期性能力读回策略；无固定全设备数值 | 定期采集计数/水位/延迟/资源；只在明确断连或 epoch 变化时停止旧流并新建 session；不在后台偷偷重放配置 | 计数器可回卷/重启；内存、句柄、lease 无增长；断连为 `CAM-DISCONNECTED`，新 epoch 重新读能力 | 长稳测试无未归还资源和事件序列溢出；每次重连 epoch 唯一；旧帧不能进入新会话；停止后无后台线程存活 |
| 发现重试 | 设备暂不可见；显式 retry policy；每次尝试有总预算 | 只对声明可重试的“无设备副作用”错误重试；记录每次 attempt，达到上限停止 | `CAM-DEVICE-NOT-FOUND` 或适配器原码；不连接未知设备、不默认选择首台 | 每次尝试 receipt 完整；总耗时不超过预算；策略关闭时只调用一次 |
| 心跳丢失 | 已连接会话、健康探测或链路回调报告失联 | 关闭新触发，标记健康降级/断连，隔离迟到帧；按宿主授权启动新 session | `CAM-DISCONNECTED`；不把心跳恢复当采集完成，不自动重放配置/触发 | 旧 epoch 无新交付；新 epoch 重新读能力；故障回执含最后健康时间 |
| 启动期旧帧 | Adapter profile 明确前 K 帧为缓存，且有可验证帧键/触发关联 | 在适配器内部按 profile 丢弃并逐帧记录；稳定化耗尽后才交付 | `FrameDiscarded(reason=StartupStabilization)`；不可固定三次或只保留最后返回码 | 丢弃键、计数和预算可查询；稳定化失败返回缺失/未知，不伪造有效帧 |
| 帧复制/转移失败 | SDK 返回图像对象或外部 buffer；PKG-006 工厂分配/转移失败 | 先保持原 buffer Owner，释放未转移对象；不得把空引用交给下游 | `CAM-FRAME-INVALID` 或资源错误；capture outcome 保留缺帧和释放结果 | 下游从不读到已释放/被复用 buffer；每个 buffer 恰好一个释放者 |
| 结构化故障回执 | 连接、配置、触发、接收、校验、排空任一阶段异常；诊断 sink 可失败 | 生成 fault receipt 并继续执行必要 drain；日志失败只增加诊断丢失计数 | 稳定错误码 + 原始码 + operation/session/epoch + 阶段 + 恢复建议；不返回无上下文 `false` | 相同故障可按 operation 查询；敏感图像/产品数据不进入普通日志；资源计数与终态一致 |

### 12.1 算法、备用路线与训练边界

相机采集不是视觉判定算法。噪声、遮挡、低照、饱和和模糊只在本模块形成传输/元数据状态或 `Unassessed` 标记；不在这里选择阈值、分割、去噪、补帧、缺陷候选、AI 模型或训练集。没有“算法备用路线”可由本模块自动切换：当帧不完整或来源不可信时唯一安全路线是隔离/拒绝交付，并把恢复选择交给宿主和对应视觉模块。

HALCON采集适配器按§8.3/§18.2实施，具体路径是 `open_framegrabber` → 设备能力/参数查询 → `grab_image` 或 `grab_image_async`/`grab_data_async` → `set_framegrabber_param('do_abort_grab', ...)`（仅在设备资料声明支持时）→ `close_framegrabber`。这不是本模块的新算法，也不能用 `grab_image_start` 作为跨设备预取保证。`grab_image_async` 的 `MaxDelay` 只表达旧图年龄检查及必要的重新抓取语义，不能当作等待超时；适配器必须把它与 Core 的单调预算、取消和 drain 分开。若该路线不支持目标设备的可证明帧身份、停止或 buffer 所有权，则由宿主显式选择设备官方 Adapter，或拒绝该采集模式；Replay 仅作离线软件验证，不以时间最近法补关联。

### 12.2 复审结论与架构裁决点

本轮复审保留单设备 Owner、单 epoch、帧租约独立释放和未知结果不重试四项不变约束。待主会话/对应 Owner 接收的是正式平台身份与错误映射、共享帧桥接及每个真实相机族的设备资格。独占租约和配置持久化的本地工程责任已确定，不再列为未决设计。模块本地工程决定已按附录 A 明确：宿主设备租约防跨实例争用，Core 串行本实例命令；帧端口桥接共享租约，默认复制；配置持久化归宿主。正式平台映射及设备资格只阻断对应集成切片，C1六项规格已接收，C2–C6保持 `DesignReview/Prep`；实际代码派发与各集成/运行门另行关闭。

## 13. 测试矩阵

| 层次 | 必测内容 | 证据边界 |
|---|---|---|
| Core 单元 | 全参数范围边界/步进/单位；能力版本变化；显式默认与 Unchanged；状态转换和错误映射 | 不证明 SDK/真实设备行为 |
| Adapter 合同套件 | 同步回调重入、异步乱序、重复/冲突键、错误原码、partial apply/readback、断连和迟到回调 | 用假驱动验证适配协议，不代现场 |
| 并发/生命周期 | 两个实例隔离；同设备第二写 Owner 被拒；Start/Stop 竞态；重复 stop/dispose；取消迟到；事件订阅者异常/慢回调 | 宿主 access 负责跨实例独占，Core 负责本实例串行；不可只测纯函数 |
| 资源/背压 | buffer 唯一释放；多消费者显式独立 lease；零拷贝防覆写；队列容量上限；慢消费者、消费者异常/提前退出、drain 超时 | 资源计数归零断言及诊断记录 |
| Replay/模拟 | 常规帧、格式变化、损坏帧、缺触发 ID、回卷/重置、时间域变化、部分帧和断连序列 | 清楚标注合成/回放；不作硬件资格 |
| 消费者集成 1 | 视觉检测宿主以公开 API 注入相机源并接 PKG-006 帧，接入宿主自己的流程 | 验证产品流程不下沉模块；使用获准设备配置/profile |
| 消费者集成 2 | 独立采集工具或无 UI 采集工具引用同一包；独立配置来源、诊断、取消与关闭 | 不引用检测宿主/私有数据库；不改核心即可接入 |
| HALCON/AsunImage | 只对选择的公开 acquisition route 核 26.05 算子语义、ImageLibDotNet 可调用签名、native 资源/线程和错误映射 | 算子直接经 cv2 使用；仅真实 C# 类型/重载/封送歧义核公共签名，不检查内部；不测试无关图像算法 |
| HIL/现场 | 实际型号/固件、曝光/触发时序、断连重连、持续帧率/丢帧、关闭与 buffer 回收 | 独立产品验收门；模拟、截图、单测均不替代 |

§8.1 的定向验收须覆盖缺时间单位/步长、事件无帧号、错误触发关联、非整数参数表示与真实错读回、chunk 截断/错端序、异步解析期间 Stop/换代，以及成功/取消/异常路径的 SDK buffer 恰好归还和释放失败不交付。§6 的关闭反例包含并发/重入关闭、失败后依赖仍保留、显式恢复不重复成功阶段；§14 的容量反例包含 N/N+1、部分池分配失败、重复租用不重复计容量，以及 SDK 归还后独立 lease 仍有效。这些是后续切片的验收断言，不代表本轮已运行产品测试。

测试不把连接成功等同完整采集、不把 `N` 个缓冲等同 N 次有效曝光，也不将模块帧接收归因成应用覆盖完整。所有取消/异常和部分成功路径均检查资源数与设备占用状态。

## 14. 性能预算与可观测性

每个设备/Adapter 消费者必须提供不可变 `BenchmarkProfile`，绑定设备型号/固件与 capability revision、adapter/API、OS/驱动/运行时、像素格式、ROI、触发模式及 fixture/config hash。负载按实际 plane stride、行数、chunk/metadata、曝光/读出模式、触发速率、消费者速度、并发和冷/热状态分桶。Profile 预先冻结预热和测量次数、最低有效样本数、吞吐观察窗口、有限停止/deadline、驱动缓冲/队列/in-flight 上限及阈值来源；相机预热/稳定条件依设备采集状态明确定义，冷启动另桶测量。

每帧 payload 按各 plane 的实际 `stride × rows` 求和并加 chunk/metadata；驻留预算按不同物理分配的完整 backing capacity 求和，加 SDK/采集卡基线、临时复制/转换及停止反应窗口内尚未预约的在途增量，使用 checked 算术，溢出或缺少可证上界时拒绝相关 Start。共享 PKG-006 lease/池槽只计一次物理容量，真实副本分别计；不能只按 payload 或租用次数计容量。MVS `SetImageNodeNum` 只设置用户节点数，XML 明确实际节点还包含 SDK 内部预分配，且可能按资源重算；不得把设置值当总驻留容量。池槽归还、`ArrayPool.Return`、清字段、Dispose 或 GC 不证明物理容量释放；仍驻留的池保持计入预算，不预扣期望消费者即将释放的容量。全局额度仍由宿主 Owner 提供，本模块只消费明确预算，不另建总账。

回调仅允许执行有界校验、必要复制和所有权转移，禁止算法、用户事件派发和磁盘 IO，也不为每帧创建等待队列空位的 Task；回调延迟作为待测维度，不保留无来源的固定毫秒目标。使用单调时钟分别测回调/入队、设备读出、传输、队列等待、交付、停止与排空；记录设备能力条件、帧数/缺失/重复/冲突/丢弃、队列深度/高水位、buffer/lease outstanding、托管/native/SDK 峰值、复制字节/原因与短时双占、吞吐、停止和 drain。采集拒帧、预览显示跳帧和宿主存证失败由各自 Owner 分列，不把显示节流当相机丢帧；无公共接口可观测的资源记 `Unknown`，不得记为零。

冷态和热态、完整排空端到端时长、取消至真实停止和 lease 归还分别测量；P50/P95/P99、样本有效性、失败/删失及未排空规则按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)。丢帧、帧重复/冲突和设备停止失败另按设备状态分项计数。延迟、帧率、吞吐和资源验收线只能来自已采纳的设备/消费者 Profile；没有批准目标标 `TargetPending`。

每会话至少记录稳定 device/session/epoch ID（日志需脱敏序列号）、adapter/API/设备固件/能力 revision、配置请求/应用/读回差异、operation/trigger/frame 关联、原始与换算时间域、帧数/缺帧/重复/冲突/丢弃区间、队列深度/高水位、buffer/lease outstanding、停止和 drain 时长、原始驱动码。禁止记录图像内容、客户板身份或配方明文到普通诊断日志；如宿主需要追溯，由其按获批证据策略保存引用。

诊断接口不得阻塞采集回调；指标/日志 sink 失败不改变帧状态和设备命令结果，但要暴露诊断丢失计数。模拟来源在每条帧与会话指标中可见。

## 15. DZ-XVision 来源事实的通用化采纳

以下规则来自快照中的 [`PubParams.CameraParams`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/PubParams.cs)、[`DZXVision.BoardGrab`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/DZXVision.cs)、[`CaptureTask`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/Runtime/CaptureTask.cs)、[`ProductImageLayout`](../../references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/Runtime/ProductImageLayout.cs) 和运行日志调用；它们只作为通用端口/回执/恢复候选，已剥离旧 SDK、WinForms、产品点位、光源和拼板语义。

### 15.1 发现、连接和健康状态

快照的启动路径先扫描设备，设备为空时按固定次数和间隔再次扫描，再连接目标、设置心跳、开始采集；连接失败保持未连接并写错误日志。可迁移规则是：

1. `DiscoverAsync` 接收显式 `DiscoveryRetryPolicy`（最大尝试数、每次等待、总预算、是否只重试“暂时无设备”）。默认策略由调用方提供，Core 不隐式循环；无策略时一次尝试。
2. 每次尝试产生 `DiscoveryAttemptReceipt`：attempt index、开始/结束单调时间、候选设备摘要、适配器/原始码、是否可重试和下一动作。发现为空、查询失败、设备被占用和输入非法必须区分。
3. `ConnectAsync` 成功后先取得能力和健康快照，再允许 `Apply`/`Start`。支持心跳或链路健康的 Adapter 提供 `GetHealthAsync`/`HealthChanged`；心跳丢失进入 `Degraded`/`Disconnected`，不把旧 `IsConnected=true` 当事实。健康探测不得自动重放曝光、触发或配置。
4. 重连必须停止旧 epoch、隔离迟到帧、重新发现/读能力/读回当前状态并建立新 epoch。重连成功只表示会话恢复，不能表示上一操作或上一帧已成功。

### 15.2 配置应用与采集回执

快照在取图前检查连接，并把曝光写入设备后才采集；通用化后每次 `ApplyAsync` 都必须以 `CapabilityRevision` 和当前 session 为前提，逐字段返回 accepted/applied/readback/unknown。曝光单位、默认和回读仍由设备能力提供；旧项目的 `3000` 等数值不能成为公共默认。光源设置、稳定等待和运动到位不属于本模块，宿主按各自 Owner 在触发前完成。

快照的普通光/UV 图像分别保存到独立槽位，且按采集点顺序消费；可迁移为 `FrameSourceDescriptor`：`sourceKind`（Hardware/Replay/Simulation）、`modality`（设备声明的枚举，不在相机模块硬编码 Normal/UV）、session/epoch、capture sequence、configuration revision 和 frame lease。不同 modality 或配置 revision 的帧不能互相覆盖；同一 frame 只能有一个租约 Owner，复制/转移完成后才能释放适配器对象。

### 15.3 重试与稳定化的边界

快照在一次采集点上连续调用三次取图，最终以最后一次返回码决定是否复制图像。该行为可提示某些设备需要“丢弃启动期旧帧/稳定化”的适配模式，但不能迁移为通用三次重试：它可能重复真实曝光、掩盖触发未知、丢失中间错误并破坏帧身份。

通用端口只允许以下两类重试，并必须在 `CaptureRequest` 中显式声明：

- **未产生设备副作用的重试**：发现为空、能力查询的可重试传输错误。每次尝试有独立 receipt，达到上限即终止；不重试参数非法/设备占用。
- **适配器声明的稳定化采集**：设备资料明确说明启动后前 K 帧为旧缓存，且提供可验证帧序号/触发关联。适配器报告丢弃的帧键和原因；稳定化帧数、上限和总预算属于设备 profile，不以固定 3 次代替。

触发已发出但回执未知、曝光可能已发生、帧关联不可靠或队列溢出时不得自动再触发。需要补采的策略、次数和质量原因由宿主/采集编排 Owner 决定；Core 只返回失败/缺失/未知和可查询 operation。

### 15.4 故障日志和可观察回执

快照在连接、曝光设置、采图、拼图和资源处理异常时记录异常文本，同时把简短错误显示到运行列表或对话框。通用模块不得持有 UI，但应提供结构化 `CameraFaultReceipt` 和诊断 sink，至少包含：`operationId`、session/epoch、设备稳定标识摘要、阶段（discover/open/health/configure/arm/trigger/receive/validate/transfer/stop/drain）、模块错误码、适配器/原始码、异常类型与安全摘要、重试次数/策略、配置 revision、帧/触发键（如有）、资源计数、单调时间和恢复建议。

日志写入失败不改变采集结果；日志不得写图像像素、产品/工单身份、配方明文或 SDK 句柄。相同故障可合并指标，但每次 operation 的终态和未知回执必须可查询。`CAM-FRAME-INVALID`、`CAM-TRIGGER-UNKNOWN`、`CAM-DRAIN-INCOMPLETE` 等错误不得只记录字符串后返回通用 `false`。

### 15.5 帧来源、资源和下游交接

快照在取图成功后复制到独立图像对象，再旋转、拼接和保存到产品上下文；通用化后 Adapter 必须在 `FrameReceived` 到 `FrameDelivered` 之间完成 payload/layout 校验，并明确是零拷贝 lease 转移还是独立快照。旋转、拼接、质量检查、图像落盘和总览图均是下游消费者；模块只交付未解释的帧及来源元数据。下游失败不能反向释放或篡改已交付帧，必须按 PKG-006 归还 lease。

若一组请求含多个 modality 或多个 capture slot，Core 只按稳定的 capture key/sequence 交付和封口，不检查产品点位数量、不拼接总览、不判断“所有点已完成”。缺失或重复键形成显式 `Incomplete/Duplicate/Conflict` 回执，不能以数组下标或最后到达帧补齐。

### 15.6 来源限制与不可迁移做法

不得迁移：全局静态 `CameraParams`/`HObject`；固定硬编码相机索引；连接成功后无能力读回即采集；只保留最后一次取图返回码；通过 `Thread.Sleep` 代替设备同步；把旋转/拼图/保存图像和采集状态写进 Core；WinForms 控件、DevExpress 弹窗、产品/MES 日志、AOI/点位/UV工艺规则；旧 AsunImage 或相机 SDK 类型。它们分别违反实例隔离、事实完整性、时间/触发语义、帧 Owner 或模块边界。

## 16. 发布、回退与第二消费者

最小发布物是独立可引用、构建和测试的 Core/Contract 包；按需要分别发布 Adapter 和可选 UI。无 UI 示例宿主作为验收消费者，不要求运行任何检测平台。在对应切片获准后，Core、Contract、Simulator 和契约测试可与设备 SDK 解耦并先行开发、构建与验证；已授权的 MVS 相机 Adapter 可按具体适配切片进入开发，使用指定的 `MvCameraControl.Net.dll 4.8.1.0`、其 XML 公共 API、官方 C# 示例及对应 SDK 资料核对实际调用。Adapter 只实现本模块公开端口，不向 Core、宿主或公开 Contract 泄漏 MVS 类型、句柄、回调对象或线程细节。

MVS Adapter 的切片准入仍须单独证明 .NET 10 加载、封送、原生依赖和 x64 部署兼容性，并核对回调线程与短回调约束、native buffer 的取得/归还、取消/超时、停止排空、关闭后的迟到回调和资源释放语义；缺库、错位数、缺依赖或版本不匹配必须给出可诊断错误。软件链验证不等于真实设备资格，断连/重连、触发、持续采集、停止排空、长稳和 HIL 仍是独立验收门，未通过前不得宣称 MVS 实机或生产通过。OPT 光源 SDK 不属于本相机模块的 Adapter 范围。

升级前在独立消费者验证 API major、帧契约、配置单位/default semantics、错误/终态、取消和释放兼容性；升级包并行运行真实设备需有单一设备 Owner 计划，不能让新旧包竞争打开设备。回退时停新触发并完成/明确失败的 drain，记录当前实际设备设置；校验旧包支持当前固件/配置后再恢复，不自动重放未知命令。未知资源状态下保持设备不可用，由宿主设备治理流程确认，不以强杀线程当回退。

第二消费者验收必须由与视觉检测不同的独立采集工具/无 UI 作业宿主完成：同一 Core/Adapter 可被引用；设备选择和配置来自工具自身；通过同一能力清单与参数校验采集、读取帧、取消/停止、排空、关闭；不增加任何制程身份、工艺字段或产品 VM 依赖。两个宿主行为相同地遵守 Core 契约，同时各自保留应用流程和权限。

## 17. 实施准入与未决项

### 17.1 AOI.Main 相机闭环补充

只读复核 [影像窗口交互指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-image-viewport-interaction-design.md)、[原图预览与保存指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-original-preview-and-save-design.md) 和 [连续采集序列指导](../../references/project-snapshots/AOI-Main/20261004/original/Docs/superpowers/specs/2026-07-29-camera-capture-sequence-browsing-design.md) 后，采集适配器必须将以下内容作为通用端口验收条件：

1. 回调收到的帧先复制或取得有证明的只读 lease，再发出 `FrameDelivered`；不得把 SDK 缓冲区直接交给 Viewport、Replay 或导出线程。
2. 预览可以返回轻量缩略图，但必须同时登记原始尺寸、像素格式、行跨度和 共享帧 revision（从 frame port 事实取得）；原图保存和选中窗口加载不能读缩略图。
3. 连续采集使用每相机独立的 capture epoch、目标帧数和有界容量预检。取消、断开、单相机失败和部分帧保留分别表达，不能把“未收到”写成“缺陷”或“成功”。
4. 配置应用、实际回读、首帧到达和停止排空是四个独立回执；设备 ACK 不能代表图像已发布，停止请求返回也不能代表所有回调已排空。

相机数量、最大帧数、像素格式和无损编码格式不从 AOI.Main 默认值升级为公共默认；调用应用必须提供真实 `BenchmarkProfile` 与设备能力清单。

### 17.2 六项核心准入定位与切片

主控已完成0.4.2-prep的C1六项内容走读及§9/A.6.1退修接收，并独立复算CAM.C1.13-A的474 bytes与SHA-256一致。C1（泛型托管Core/Contracts + Simulator/测试ports/无UIHost）保持 `ModuleCoreImplementationReady`（规格准备）。2026-10-11主控完整回读§20后，C2-RF六项文档规格限定接收并同步为 `ModuleCoreImplementationReady`（仅规格准备）；边界/消费者、精确API、双无UI Host、有限测试及沿用的Benchmark/工程范围均已明确。C2其余范围及C3–C6不沿用该状态，仍分别保留其真实契约映射、输入与运行门；文档和算术不是C#或设备验证。平台 DTO/共享租约/设备资格不得成为未定义 Core API 的借口，也不得由 Core 猜测。

| DEV-GOV-010 §3.1 条件 | 本文定位与可接收内容 | 当前结论 |
|---|---|---|
| 1 边界/消费者 | §1–2、§9、§16；单设备采集，两独立消费者，排除产品编排 | C1六项规格已由主控接收 |
| 2 唯一 Module API | 附录 A；命名空间、强类型输入/输出、能力域、方法/端口/事件、Owner/幂等/取消/drain | C1 Module API v0.2规格已接收；不等于平台Schema或C2共享帧映射获批 |
| 3 无 UI/SDK 最小宿主 | §9.1～9.3、附录 A.8–A.9；预持ID/恢复槽/嵌套finally与泛型帧端口、Simulator、内存 ledger 和单进程 access 仅限非 Hardware | C1最小Host及异常/无session退修已接收；真实端口不隐式替代 |
| 4 可判定测试 | §11–13、§19、附录 A.6–A.9；正常/非法/重复/并发/取消/超时/关闭/回退及CAM.C1.16/17 | C1固定10s/120s/180s与CAM.C1.16/17断言规格已接收；尚未运行 |
| 5 BenchmarkProfile | §14；实际 backing 容量、全链/取消测点、冷/热、失败/未知与公共分位口径 | C1测量方法规格已接收；目标值待消费者Profile采纳，未执行性能验证 |
| 6 工程/允许范围 | 附录 A.8–A.9；唯一BCL Exe工程、命令、测试位置、调用顺序、禁止路径与后续门 | C1固定Exe/命令/预算及允许范围规格已接收；代码基线与实际实施派发未授予 |

| 切片 | 范围与真实消费方 | 额外门及失败影响 |
|---|---|---|
| C1 泛型托管Core/Contracts + Simulator/测试ports + 无UIHost | 发现、能力、配置、有限面阵/线扫块、显式软触发、健康、事件、幂等、停止/关闭、资源协议；两个 §9 消费者 | `ModuleCoreImplementationReady`（规格准备），DEV-GOV-010 §3.1六项已接收；实际开发另绑定可审计代码基线/派发，不写设备、不依平台产品DTO。不得把仅参数校验称为完整模块 |
| C2 共享帧与宿主治理桥接 | 泛型 TFrame 绑定 image-frame 公共 lease，耐久 ledger、跨进程独占/可撤销权限 | 对应 Owner 接收正式类型和资源监测；未知共享合同仅阻本切片。零拷贝另有生命周期证明门 |
| C2-RF 线扫原行事实只读桥 | 面向 IM-023 mosaic C.2/C.3 与未来标定采样宿主，按原 Owner 提供不可变、有界、可分页逐行事实；含 64 位 counter、epoch/wrap/reset、曝光/物理关联、原始行字节 hash、跨块连续性和恢复语义；两个 Synthetic Host 与 CAM.RF.01～10 已写入 §20 | `ModuleCoreImplementationReady`（仅规格准备）；主控于2026-10-11按 DEV-GOV-010 §3.1 六项限定接收。只读桥不发运动、Trigger、硬件、编码器或光源命令；C2设备/Frame Owner正式映射、真实SDK/编译、WPF、性能/HIL/现场门保留，不提升C2其余范围或运行/产品资格，C1/C3–C6状态不变 |
| C3 MVS 官方 Adapter | 指定 SDK 4.8.1.0 公共 API、x64 部署、回调/buffer、参数与触发 | 具体型号/固件/接口、量程/步进/单位、帧身份、停止行为及真实加载/封送验证；不核验 AsunImage/DevExpress 授权 |
| C4 HALCON acquisition Adapter | §8/§18 的已选设备接口，经 `ImageLibDotNet.cv2` | 对应 26.05 acquisition interface 参数/abort/预取/帧身份及必要的公开重载，禁止直接引用 halcondotnet 或静默切换 |
| C5 可选 WPF 工作台 | §10 的两角色流程/控件与投影 | A.10显式挂接/Host预览桥接接收、实际 25.2.3 WPF、三语、1920×1080 UI/视觉验收；不阻 C1 |
| C6 设备/产品资格 | 实机帧、连续/线扫、触发关联、重连、停止、长稳、性能/HIL和客户接入 | 已采纳 Profile、真设备/样本、时序及外部物理验收值；模拟软件结果不代现场 |

自审边界：正文覆盖相机全能力，未写入 PCB/SPI/AOI/点胶/涂覆判定、产品身份、运动/光源命令或质量放行。文档和资料核对不代表实现、构建、性能、WPF、HIL 或生产通过。跨文件平台采纳由主会话串行处理；本任务仅写本指导，不修改入口、进度、其它模块或共享契约。

## 18. 研究依据、路线选择与参数建议

### 18.1 固定源码与测试的可迁移结论

复用 [REF-002 固定源码基线](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md) 的 Aravis v0.8.36，commit `97ff5e330919d7a44b871df4eda669feeafdf342`；本轮实际读取源码/测试并从上游固定 raw 地址比对关键文件，不引入其运行库或复制代码。

| 直接依据 | 观察与可迁移规则 | 限制/依赖与许可 |
|---|---|---|
| [src/arvstream.c](../../references/open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvstream.c)；SHA-256 `ab5d1a8326b4ba8b84bcfb8a79520c6b84ded0b40141494b22a7ac041c2b7396` | push 的 transfer-full 与 pop 交接体现唯一 Owner；pop 到 buffer 后仍须检查状态；timeout-pop 单位是 µs；接收线程 callback 不执行用户业务 | GAsyncQueue 不是平台有界队列证明；不能由返回对象推断有效曝光或硬件停止。源码 LGPL-2.1-or-later，仓库 COPYING 为 LGPL2.1 |
| [tests/buffer.c](../../references/open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/tests/buffer.c)；SHA-256 `99ab3f6adc8a470c4df0fbb7978dd760b77a52143bed30de6826726fa4bafdd5` | 初始 received size=0/status Cleared；预分配 pointer 与 userdata destroy callback 有断言；设备 timestamp 与 system timestamp 分开 | 测试文件 SPDX Unlicense；只移植断言思想，不复制 C 内存模型，不声称运行上游测试 |
| [src/arvfakestream.c](../../references/open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/src/arvfakestream.c)、[tests/fake.c](../../references/open-source/AravisProject_aravis/97ff5e330919d7a44b871df4eda669feeafdf342/tests/fake.c) 的 `fake_stream_test` 与 `camera_trigger_selector_test` | fake stream 无输入 buffer 计 underrun；测试校验 completed/failures/underruns 和输入/输出队列；FrameStart/AcquisitionStart 的 TriggerMode 互不覆盖 | Fake 的成功不证明网卡/设备时序、停止或真实带宽；不同 TriggerSelector 必须分别记录能力与配置 |

读取的 meson.build 依赖包括 GLib/GObject/GIO（GLib ≥2.52）、libxml2、zlib、可选 libusb，Windows 链接 ws2_32/iphlpapi。本平台 C# Core 不携带上述原生依赖；可迁移的是所有权、无输入 buffer、触发选择器与测试反例。已有 DZ-XVision/AsunControl/AOI.Main/MVS 资料的事实和限制沿用 §8.1、§15、§17.1，不重复建立来源报告。

### 18.2 HALCON 26.05 路线裁决

| 路线 | 处理与适用条件 | 拒绝/切换条件 |
|---|---|---|
| MVS 官方 Adapter（当前指定设备族主路线） | 指定 4.8.1.0 官方公共 API；先查询能力/配置回读、预约 buffer，再 arm/显式触发，逐帧复制或证明转移，按实际获取模式归还 SDK buffer | 缺帧身份/单位/停止能力时拒绝对应模式；不通过 HALCON 自动绕过设备失败 |
| HALCON acquisition Adapter（显式选择的设备接口路线） | `cv2` 调用 `info_framegrabber`/`open_framegrabber`、get/set 参数、同步 `grab_image` 或异步 `grab_image_start`+`grab_image_async`/`grab_data_async`，停止后 `close_framegrabber`；所有控制均通过适配器 | 设备 acquisition interface 未明确、abort/预取/关联/资源无法证明则拒绝，宿主停旧会话并显式换 Adapter；无运行中隐式回退 |
| Simulator / Replay | 同 Core/端口输入，确定性故障序列和来源标记；Replay 保留原帧来源引用及回放 epoch | 不接真实触发/设备，不作硬件资格或实际曝光证据；不能作为生产失败的成功替代 |

官方本地入口：[open_framegrabber](../../../halcon算子手册/operators/open_framegrabber.html)、[info_framegrabber](../../../halcon算子手册/operators/info_framegrabber.html)、[grab_image](../../../halcon算子手册/operators/grab_image.html)、[grab_image_start](../../../halcon算子手册/operators/grab_image_start.html)、[grab_image_async](../../../halcon算子手册/operators/grab_image_async.html)、[grab_data_async](../../../halcon算子手册/operators/grab_data_async.html)、[set_framegrabber_param](../../../halcon算子手册/operators/set_framegrabber_param.html)、[get_framegrabber_param](../../../halcon算子手册/operators/get_framegrabber_param.html)、[set_framegrabber_callback](../../../halcon算子手册/operators/set_framegrabber_callback.html)、[close_framegrabber](../../../halcon算子手册/operators/close_framegrabber.html)。算子均经 `ImageLibDotNet.cv2` 使用，不核“是否包含算子”，不接 `HOperatorSet`/halcondotnet，不检查 AsunImage 内部。

适配实现必须保持以下版本语义：同步取图不能用 Task token 假取消；`grab_image_start.MaxDelay` 已废弃且不生效，只与异步取图配合，切换同步取图会中止原异步抓取并重新同步取图。`grab_image_async.MaxDelay` 单位 ms，限制自异步启动起的旧图年龄，超龄可能重抓，负值关闭旧图检查；默认返回前预启下一次抓取。硬触发模式禁止以重抓替换旧帧或把预取等同宿主授权曝光。异步路线需逐接口证明触发门/预取及停止语义，不能证明则不开放该模式。`grab_data_async` 的 Image/Region/Contours/Data 均按实际返回类型释放，不能只释放 Image；非图像输出不泄漏 Core。`do_abort_grab` 及可跨线程调用仅在具体接口支持时成立；关闭前不能有另一线程仍用同句柄。open/close/info 的全局 exclusive 约束由 HALCON Adapter 内部统一调度，Core 的单实例锁不能替代它。

本模块不生成自动曝光/增益优化算法；UI 只根据当前能力列出合法范围、离散值或设备报告的 default，本模块不生成数值推荐，只展示已核合法域/default并经用户显式选择。建议绑定 capability/config revision、单位与原因，revision 变化立即过期；用户显式提交新快照后才写设备。若未来需要图像质量驱动推荐，由相应优化模块评估并通过相机公开 API 提交，不在这里静默调生产参数。无视觉算法缺口，因此不另引平行算法，也不伪造路线性能比较。

### 18.3 官方触发与 DevExpress 依据

官方 [Basler Triggered Image Acquisition](https://docs.baslerweb.com/triggered-image-acquisition)、[Encoder Control](https://docs.baslerweb.com/encoder-control) 于 2026-10-09 实际读取：FrameStart/LineStart/ExposureStart、TriggerSelector/Mode/Source/Activation/Delay 必须按型号分别查询；软件触发先配置软件 source，LineStart 可由型号支持的 encoder source 产生。它们只支持本指导的概念划分，不能证明 MVS 支持某 encoder、时序或单位，也不移植 Basler SDK。

本次 dxdocs 工具未暴露，在线文档返回 403；控件成员依据本机官方 25.2.3 XML，位置 `C:/Program Files/DevExpress 25.2/Components/Offline Packages/<package>/25.2.3/lib/net8.0-windows/`，不是兼容性/授权审查。已读 docking/Grid/Grid.Core/PropertyGrid/Charts/Core 的公开说明，SHA-256 依次为 `b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f`、`7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd`、`9ca164e53a54e5bc0eb6432a709e95c9295e60db3b0eac4fabf6dd32604b8eba`、`0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9`、`2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0`、`cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196`。§10 控件/API 名称来自这些官方文件；本地 XML 不证明真实布局、UIA、三语或性能已验收。

## 19. 面阵、线扫与可重算样例

### 19.1 能力、计数与关联处理顺序

| 条件 | 必须明确的能力/输入 | 固定处理/输出 |
|---|---|---|
| 面阵 | Area；sensor/ROI/binning/format、触发选择器及帧计数来源 | 一次完整设备帧是一个 delivery unit；帧计数不代表曝光已证实。不同 plane/chunk 仍是同帧，不拆成多曝光 |
| 线扫块 | LineScan；设备成块交付或明确 RawLines 模式；每块行数、行编号/完整性、格式/stride、触发路由 | 首选设备交付完整块。RawLines 仅在设备协议明确单行边界、有限行数/内存/封口后聚块；只按设备定义的块/行键组合，不按产品、运动位置或 FOV 拼接 |
| 多个触发选择器 | 每个 FrameStart/LineStart/ExposureStart/AcquisitionStart 的独立 source/activation/delay、可并存关系 | 配置按 selector 区分；同一命名的 TriggerMode 不互相覆盖。禁止把 LineStart pulse 数等同 block 数或一次 ExposureStart 等同完整 frame |
| 软件触发 | Software source、可发命令、每 reservation 的 selector/身份及设备 ACK 能力 | Core 预约后显式 `TriggerAsync`；先登记幂等，返回 ACK/Unknown，不声称曝光。软件高速逐行不满足设备预算时拒绝，不以线程 Sleep 补时序 |
| 外触发/encoder | Hardware source token、设备输入/边沿/时序/计数器、关联证据；宿主外部命令 Owner | Core 只 arm/接收；不发 PLC/encoder/光源命令。若关联必需而设备无法证明，启动前拒绝；宽松独立采集可 Uncorrelated 但不声称触发对应 |
| ID/计数回卷或重置 | 原始 counter 位宽/域/启动代及设备 reset/wrap 明确证据 | 保留原值与域。仅按已知模数和单调边界解 wrap；reset/歧义立即关闭旧 capture、标 Unknown，不把小值当新旧任一帧补齐 |
| 时间/曝光区间 | 设备原始 ticks、频率/单位、clock domain/boot epoch、事件语义和可信帧关联 | 原样保留；有官方频率才换算。exposure_start/end 缺关联则只作事件诊断；arrival/transfer_end 不当曝光时间；线扫无证据不合成整块曝光区间 |
| 缺行/重复/丢失 | 块/行稳定键、期望行区间、设备完整性/丢行标志、有效字节长度 | 相同内容重复不增加数；同键不同内容冲突；缺行/坏行块拒交付并记原因，不补零或插值。额外完整块隔离，不覆盖已封口集合 |

先验证能力/输入与预算 → 配置逐项读回 → 预留生产队列及在途/复制容量 → arm → 按 selector 触发/等待外触发 → 校验帧/块/行键及完整性 → 验 layout/来源/不可变性 → 唯一转移 sink → 封口逻辑集合 → 停止/drain → 等租约归还。缓冲回调次数、行数、块数、软触发命令数、已证曝光数、已交付数均独立记录。

### 19.2 合成例与双视角反例

下列数字仅是确定性软件 fixture，不是机台默认值、性能阈值或实测结果。

| 合成输入 | Core/Adapter 应输出 | 宿主/消费者应断言 |
|---|---|---|
| 能力 ROI x/y 步进 2，width 步进 4，height 步进 2；sensor=640×480；请求 (0,0,640,480) / (1,0,640,480) | 前者合法；后者校验定位 x 非步进且越界，无设备 set/arm/trigger | UI 与 console 同错；不能自动把 x 改 0 后应用 |
| 曝光域 [10,1000]µs、离散步进 0.5µs；请求 10.5 / 10.25；另设备明确 Continuous | 离散设备前者通过、后者拒绝；连续设备按实际闭区间校验；未知步进且未知域拒绝该设置 | 不把“SDK 接受浮点”当连续证明；建议值与实际配置分开 |
| 3 个 delivery slots：到 A、B、B 同内容，deadline 后无 C | 交付 2，duplicate=1，missing=C（fixture预声明源键），逻辑 TimedOut，若设备明确提前结束则Incomplete；排空/资源另计 | 不以 3 次回调显示完成；停止时先归还 A/B，不等待资源终态才归还 |
| 同 epoch/source key=A，两个不可变 payload 摘要不同 | 后到帧隔离，conflict=1，capture 逻辑 Failed，已交付 A 不能撤回但其 capture 被污染 | 不接受 last-wins；下游不得在采集逻辑封口前据单帧宣称整批成功 |
| LineScan 块 100 行：设备行键 0..98，payload 只有 99 行，另重复行 98 | 完整性失败，交付 0；missing={99}、duplicate=1，释放所有未转移行/块 | 不补一行、不把重复行凑成100；不推断物理扫描覆盖或运动距离 |
| 请求 1 个100行块，FrameStart=1、LineStart=100，硬件只确认99个有效line事件 | frame/pulse/block 三种计数分列；不能仅凭FrameStart ACK宣称块完整 | 不根据编码器厂商说明臆造本机计数频率；缺失触发关联要求由宿主选择拒采或独立采集 |
| 一个独立 backing 4096 bytes，两个 lease 引用它，另复制一份4096 bytes；driver 8192 bytes | 容量=16384 bytes，lease=3，allocation=3；不是3×4096再重复计共享，也不是只计payload | 宿主额度与 Core reservation 对账；lease归还但池驻留仍计4096，不把GC当释放 |
| stride=2^62、rows=4（恶意元信息），或 metadata长度大于可读buffer | checked乘法/边界拒绝，CAM-FRAME-INVALID；不能读内存、不能交付 | adapter原buffer恰好归还；错误摘要不输出指针 |
| Stop时 callback=1、driverBuffer=1、lease=0；稍后callback/driver=0、lease=1 | 首阶段DrainCompleted=false；第二阶段DrainCompleted=true、ResourcesReleased=false；lease归还后唯一终态 | UI依阶段显示，不释放Owner或重连；停止查询取消不丢原operation |
| Trigger写入意图耐久成功，SDK命令返回前进程退出 | 重启Query原operation为Unknown/待对账，禁止重发reservation；无新Trigger事实 | 宿主保留物理占用恢复门；NotFound不代表未触发；新session不能续用旧ticket |


## 附录 A：Module API Contract v0.2

### A.1 唯一入口与构造

命名空间 `Asun.Pcb.Modules.CameraAcquisition.Contracts`，Core 类 `Asun.Pcb.Modules.CameraAcquisition.CameraAcquisition<TFrame>`；`TFrame : class` 绑定宿主已有帧租约，不创建第二个 FrameLease。本附录的接口与字段表共同构成唯一模块 API 候选。字段表是不可变 record/enum 的定义规范，不是可直接编译的源码；不使用 object/dynamic、任意参数字典、SDK 句柄或产品 DTO。

```csharp
public interface ICameraAcquisition<TFrame> : IAsyncDisposable where TFrame : class
{
    CameraSnapshot Snapshot { get; }
    IDisposable Subscribe(ICameraEventSink sink);
    ValueTask<CameraReply<DiscoveryResult>> DiscoverAsync(DiscoveryRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<SessionReceipt>> ConnectAsync(ConnectRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CameraCapabilities>> GetCapabilitiesAsync(SessionQuery request, CancellationToken cancellationToken);
    ConfigurationValidation ValidateConfiguration(CameraCapabilities capabilities, CameraConfiguration configuration);
    ValueTask<CameraReply<ConfigurationApplyResult>> ApplyAsync(ApplyRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CaptureTicket>> CaptureAsync(CaptureRequest request, ICameraFrameSink<TFrame> sink, CancellationToken cancellationToken);
    ValueTask<CameraReply<TriggerReceipt>> TriggerAsync(TriggerRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CaptureOutcome>> WaitCaptureAsync(CaptureQuery request, CancellationToken cancellationToken);
    ValueTask<CameraReply<StopReceipt>> StopAndDrainAsync(StopRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CloseReceipt>> CloseAsync(CloseRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<HealthSnapshot>> GetHealthAsync(SessionQuery request, CancellationToken cancellationToken);
    ValueTask<CameraReply<OperationSnapshot>> QueryOperationAsync(OperationQuery request, CancellationToken cancellationToken);
}
```

使用 System/Threading/Threading.Tasks/Collections.Immutable；下表 `A<T>` 是 `ImmutableArray<T>`，`?` 是可缺，不代表“默认设备值”。构造参数顺序固定为 `ICameraTransport<TFrame> transport, ICameraClock clock, IOperationLedger ledger, ICameraAccessPort access, ICameraFramePort<TFrame> frames, ICameraDiagnostics diagnostics, CameraLimits limits`。宿主拥有注入端口，Core 只拥有自己取得的设备租约、队列和本实例资源，不能 Dispose 宿主共享端口。

`CameraReply<T>` 字段为 `ReplyKind Kind, Guid? OperationId, T? Value, A<CameraFaultReceipt> Faults`。Kind={Success,Rejected,Partial,Pending,Unknown,NotFound,WaitCancelled}。Success 仅表示本方法达成（如返回 Armed ticket/逻辑结果），不暗含资源终态；Success 的 Value 非空。Partial 带逐项回执，Pending/Unknown/WaitCancelled 保留原 operationId/最近快照；NotFound 只用于查询未命中。普通设备异常变为结构化回执，不以 null/false 掩盖。构造参数无效和已释放实例的新操作使用标准参数/生命周期异常且不发生设备动作。

### A.2 请求、身份与限额

所有 Guid 非 Empty，标识字符串非空、Ordinal 不透明比较，不 trim/折叠大小写。数组不可为 default；字符串/数组大小由 CameraLimits 限定；超限准入前拒绝。UTC 用 DateTimeOffset；单调 long ticks 仅在同 clock domain 比较。每个操作显式有限预算，不造全设备默认值。

| 类型 | 字段与有效域 |
|---|---|
| `CameraSelector` | `string AdapterId, StableDeviceId`；稳定ID由Adapter提供，不用显示名/索引代替 |
| `OperationBudget` | `TimeSpan Total, Queue`；0<Queue≤Total，有限且≤MaxOperationBudget；从接纳起计截止，排队不重置 |
| `CommandContext` | `Guid OperationId, string IdempotencyKey, OperationBudget Budget`；调用前即持有ID，拿不到ticket仍可Query |
| `SessionIdentity` | `Guid InstanceId, SessionId, Epoch, CameraSelector Selector`；实例构造生成InstanceId，每次连接新SessionId/Epoch |
| `DiscoveryRetryPolicy` | `int MaxAttempts, TimeSpan BetweenAttempts, bool RetryEmpty, RetryTransientRead`；MaxAttempts≥1、间隔≥0且有限；无隐式重试，调用方显式给1次 |
| `DiscoveryRequest` | `OperationBudget Budget, string AdapterId, DiscoveryRetryPolicy RetryPolicy`；只枚举指定Adapter |
| `ConnectRequest` | `CommandContext Command, CameraSelector Selector, string AuthorityToken`；授权引用不入普通日志/hash明文 |
| `SessionQuery` | `SessionIdentity Session, OperationBudget Budget`；GetCapabilities读取能力及当前配置，GetHealth不写参数 |
| `ApplyRequest` | `CommandContext Command, SessionIdentity Session, CameraConfiguration Configuration`；仅Ready允许 |
| `CaptureRequest` | `CommandContext Command, SessionIdentity Session, string CapabilityRevision, ConfigurationRevision, int ExpectedUnits, QueueCapacity, ulong ReservedBytes, CaptureUnitKind UnitKind, int? LinesPerUnit, A<TriggerReservation> Reservations, CorrelationPolicy Correlation, StabilizationPolicy Stabilization, string? SourceTag`；计数/容量/字节均正且≤能力及limits；SourceTag可空、无产品语义 |
| `TriggerReservation` | `Guid ReservationId, long Ordinal, TriggerSelector Selector, string SourceId, string? ExpectedDeviceToken`；Ordinal从0连续；token仅设备能读/关联时提供，不以软件ID冒物理证据 |
| `StabilizationPolicy` | `int MaxDiscardUnits, TimeSpan Budget, string? DeviceProfileRevision`；0禁止稳定化且Budget=0；启用时数量/预算正，有官方设备依据/可验证旧帧键 |
| `TriggerRequest` | `CommandContext Command, SessionIdentity Session, Guid CaptureOperationId, ReservationId`；仅配置Software且该预约未执行时有效 |
| `CaptureQuery` | `Guid CaptureOperationId, OperationBudget Budget`；等逻辑封口，不等帧归还 |
| `StopRequest` | `CommandContext Command, SessionIdentity Session, Guid CaptureOperationId, StopReason Reason`；Reason={Completed,Cancelled,Timeout,Fault,HostRequest}；独立停止预算 |
| `CloseRequest` | `CommandContext Command, SessionIdentity Session`；先清理本实例capture，再关闭/释放Owner |
| `OperationQuery` | `Guid OperationId, CameraSelector Selector, string AuthorityToken, OperationBudget Budget`；不要求当前session存在；先授权对应selector/Query权限，再读原记录并核OwnerNamespace/selector，越域拒绝 |
| `CameraLimits` | `TimeSpan MaxOperationBudget, CleanupBudget, DisposeBudget, AccessCheckInterval; int MaxActiveOperations, MaxRetainedOperations, MaxUnits, MaxReservations, MaxQueueCapacity, MaxMetadataBytes, MaxMetadataItems, MaxTextLength, MaxEventQueue, MaxReceiptItems; ulong MaxResidentBytes`；全部正且有限，由Host/profile给定 |
| 枚举 | `CaptureUnitKind={AreaFrame,LineBlock}`；`CorrelationPolicy={Required,NotRequired}`；`TriggerSelector={FrameStart,LineStart,ExposureStart,AcquisitionStart}`；`CameraSourceKind={Hardware,Replay,Simulation}`；`DeviceGeometry={Area,LineScan}` |

ExpectedUnits计完整帧/块，reservation数不必等于帧数（LineStart可能多pulse成一块），配对关系必须有Adapter设备协议证明。自由运行可Reservations为空且NotRequired；外触发要求关联但缺证据时拒绝。不能用预约数组序号对到帧赋关联。线扫LinesPerUnit正且在LineBlock.LinesPerBlock域内，面阵必须null。capture没有无界默认流，设备Continuous仍受ExpectedUnits/总预算封口。loss默认0；任何损坏/丢失显式失败/Incomplete，不提供静默容错计数。

### A.3 配置与能力类型

| 类型 | 字段形状/语义 |
|---|---|
| `CameraConfiguration` | `int SchemaMajor, SessionIdentity Session, string CapabilityRevision, RequestedRevision, RequestedHash, PixelFormatSetting? PixelFormat, RoiSetting? Roi, BinningSetting? Binning, ExposureSetting? Exposure, GainSetting? Gain, A<TriggerSetting> Triggers, AcquisitionSetting? Acquisition`；major=1，null/空Triggers表示Unchanged；至少一个设置，空Apply拒绝 |
| `PixelFormatSetting` | `string FormatId`；设备显式枚举，不由Core推断packed/Bayer布局 |
| `RoiSetting` | `long X,Y,Width,Height`；传感器像素，非负偏移、正尺寸，坐标约定由能力明确；checked计算边界 |
| `BinningSetting` | `int Horizontal, Vertical`；正，按设备显式组合校验 |
| `ExposureSetting` | `AutomaticMode Mode, decimal? Microseconds`；Mode={Off,Once,Continuous}；Off须正µs，自动模式值null且设备明确支持 |
| `GainSetting` | `AutomaticMode Mode, decimal? Value, string UnitId`；Off有值并在设备域内；自动为null，单位与设备完全匹配，不猜换算 |
| `TriggerSetting` | `TriggerSelector Selector, TriggerMode Mode, string? SourceId, TriggerActivation? Activation, decimal? DelayMicroseconds`；Mode={Off,On}；On必须合法source，activation/delay按能力；Off其附值null；同selector重复拒绝 |
| `TriggerActivation` | {RisingEdge,FallingEdge,AnyEdge,LevelHigh,LevelLow}；按selector/source查询支持 |
| `AcquisitionSetting` | `AcquisitionMode Mode, int? DeviceUnitCount`；Mode={Single,Finite,Continuous}；Single=1，Finite正整数，Continuous为null |
| `NumericDomain` | `decimal Minimum, Maximum, decimal? Increment, NumericDomainKind Kind, decimal? DefaultValue, string UnitId`；Kind={Discrete,Continuous,Unknown}；离散Increment>0、以Minimum为格点原点；连续Increment=null；未知不能写；最大≥最小，default须在域内 |
| `CapabilityAccess` | {Supported,Unsupported,Unknown,TemporarilyUnavailable}；未知不能冒充不支持/默认值 |
| `CapabilityEvidence` | `string SourceReference, SourceVersion, string? SourceHash, DateTimeOffset ObservedUtc`；具体型号资料/SDK公共读值，不以营销当证据 |
| `NumericCapability` | `CapabilityAccess Read, Write, NumericDomain? Domain, decimal? ReadbackTolerance, CapabilityEvidence Evidence`；容差非负且单位同域，有设备依据才使用，无依据不可任意epsilon |
| `RoiCapability` | `NumericCapability X,Y,Width,Height; long SensorWidth, SensorHeight; RoiCoordinateConvention CoordinateConvention; A<BinningSetting> AllowedBinning`；Convention={UnbinnedSensorZeroBased}，原点左上，X向右/Y向下，半开矩形。Adapter明确换算设备binning域为该域，无法确定换算拒绝配置；复杂依赖由Adapter纯校验 |
| `TriggerCapability` | `TriggerSelector Selector, string SourceId, TriggerSourceKind SourceKind, A<TriggerActivation> Activations, NumericCapability Delay, bool SoftwareCommandSupported, CapabilityAccess IdentityRead, string? AssociationRuleRevision, A<TriggerSelector> CompatibleSelectors, ReservationAssociationScope AssociationScope, CapabilityEvidence Evidence`；SourceKind={Software,Hardware,FreeRun}；规则revision锁定Adapter协议，不由Core解释字符串算法；AssociationScope={PerUnit,PerCapture}，前者一个预约只能关联一个unit；后者同token可覆盖本capture多unit，但规则须有设备来源、每unit逐项证实且总unit有限 |
| `ConfigurationField` | record：`ConfigurationFieldKind Kind, TriggerSelector? Selector`；Kind={PixelFormat,Roi,Binning,Exposure,Gain,Trigger,Acquisition}；仅Trigger附selector，其它null |
| `ConfigurationDependency` | `ConfigurationField Target, ConfigurationField? Prerequisite, DependencyKind Kind, A<AcquisitionMode> AllowedModes`；Kind={ApplyBefore,RequiresStopped,AllowedAcquisitionModes}；仅ApplyBefore需Prerequisite非null，其它null；AllowedAcquisitionModes数组必填，其余空；仅ApplyBefore参与拓扑排序，循环拒绝 |
| `TransportLimits` | `int MaxUnits, MaxQueueCapacity, MaxPlanes, MaxLinesPerBlock; ulong MaxUnitBackingBytes, DriverResidentUpperBoundBytes, InFlightUpperBoundBytes; TimeSpan MaxBudget; CapabilityAccess Stop, Abort, Pause, FrameIdentity, LineIdentity, ExposureEvents; string LayoutContractRevision`；未知上界拒绝capture，0仅有实际无分配证明时用于driver/inflight |
| `LineBlockCapability` | `NumericCapability LinesPerBlock, CapabilityAccess DeviceBlockDelivery, RawLineDelivery, string? LineIdentityRuleRevision, BlockClosureRule Closure, CapabilityEvidence Evidence`；Closure={DeviceBlockEnd,FixedVerifiedLineCount}；线扫必填，面阵null；Adapter验证有限行键/完整块边界再送Core，不送半块 |
| `CameraCapabilities` | `SessionIdentity Session, int SchemaMajor, string Revision, ContentHash, Model, Firmware, AdapterVersion, CameraSourceKind Source, DeviceGeometry Geometry, A<string> PixelFormats, RoiCapability Roi, LineBlockCapability? LineBlock, NumericCapability Exposure, Gain, A<AutomaticMode> ExposureModes, GainModes, A<AcquisitionMode> AcquisitionModes, A<TriggerCapability> Triggers, A<ConfigurationDependency> Dependencies, CameraConfigurationReadback Current, TransportLimits Transport, CapabilityEvidence Evidence`；major=1；字段不可读明确标状态，不填假范围 |
| `CameraConfigurationReadback` | `SessionIdentity Session, string CapabilityRevision, string? ConfirmedConfigurationRevision, A<ConfigurationItemReceipt> Items, bool CaptureEligible`；初次连接读当前事实，revision由事实hash产生而非UI草稿 |
| `ConfigurationValidation` | `bool IsValid, string CapabilityRevision, RequestedHash, A<ValidationIssue> Issues, A<ConfigurationField> ApplyOrder`；纯函数，无设备/ledger调用；拓扑稳定排序 |
| `ValidationIssue` | `ConfigurationField? Field, IssueSeverity Severity, string Code, ResourceKey, A<string> SafeArguments`；Severity={Info,Warning,Error}；资源key映射三语，参数无机密 |
| `ConfigurationValue` | 封闭联合，每种派生record持一个强类型setting：PixelFormatValue/RoiValue/BinningValue/ExposureValue/GainValue/TriggerValue/AcquisitionValue；类型分别是本表对应setting，无字符串写参数 |
| `EvidenceState` | {Confirmed,NotOccurred,Unknown,NotApplicable}；每个字段说明证据，不把未知合并为空 |
| `ConfigurationItemReceipt` | `ConfigurationField Field, bool Accepted, EvidenceState Applied, ReadBack, ConfigurationValue? Requested, Before, Actual, CameraFaultReceipt? Fault`；纯读当前时Requested=null；只有Confirmed Actual参与capture校验 |
| `ConfigurationApplyResult` | `SessionIdentity Session, Guid OperationId, string CapabilityRevision, RequestedRevision, string? ConfirmedRevision, A<ConfigurationItemReceipt> Items, CameraConfigurationReadback Current`；全请求字段应用且回读成功才赋ConfirmedRevision |

校验顺序：identity/schema/revision/hash → 空/重复 → read/write能力 → 单位/量程/格点/枚举 → ROI/binning checked边界 → trigger组合 → 依赖/状态 → 容量。复杂设备依赖再由transport无副作用ValidateNativeConfiguration验证，全部完成后才set。Apply按ApplyOrder逐项写/读，失败停止后续写并安全读当前；未执行项显式NotOccurred，不能遗漏。partial不发布ConfirmedRevision。重新读当前用GetCapabilities，不重试Apply冒充读取。自动曝光/增益actual逐帧按设备事实给出，未知不拿请求值顶替；消费者Profile决定是否允许自动模式。

### A.4 帧、结果、事件与故障

| 类型 | 字段形状与语义 |
|---|---|
| `FrameSourceDescriptor` | `CameraSourceKind SourceKind, string AdapterVersion, string? ReplayEvidenceReference, Modality`；modality设备声明，不是工艺枚举；Source不可被UI改成Hardware |
| `CameraFrameEnvelope<TFrame>` | `TFrame Frame, FrameFacts Facts`；唯一租约，Facts不含像素/指针；不走多播事件 |
| `FrameFacts` | `SessionIdentity Session, Guid CaptureOperationId, long DeliverySequence, string SourceFrameKey, CapabilityRevision, ConfigurationRevision, FrameSourceDescriptor Source, CaptureUnitKind UnitKind, int? ReceivedLines, LineBlockFacts? Lines, FrameAssociation Association, A<CameraTimestamp> Timestamps, A<ConfigurationItemReceipt> ActualConfiguration, string? SourceTag, EvidenceState TransportIntegrity, string LayoutRevision`；Adapter候选DeliverySequence=0，Core成功移交时连续赋号 |
| `LineBlockFacts` | `int ExpectedLines, ReceivedLines; decimal? FirstLineKey, LastLineKey; string? IdentityRuleRevision; EvidenceState Completeness; long MissingLines, DuplicateLines, ConflictingLines`；原行键为整数并精确承载有符号/无符号64位，未知两端null；有设备完整块/验证行区间证据才Completeness=Confirmed |
| `FrameAssociation` | `AssociationState State, A<ReservationEvidence> Reservations, string? RuleRevision`；State={Proven,Uncorrelated,Unknown,Conflict}；Uncorrelated数组空，Proven数组非空且逐项有同capture设备证据；线扫块可关联FrameStart/多个LineStart，禁止靠数组/arrival赋Proven |
| `ReservationEvidence` | `Guid ReservationId, string DeviceTriggerToken, TriggerSelector Selector`；同块内预约ID唯一，token来自设备且经锁定协议验证；软件ACK不得独自作Proven |
| `CameraTimestamp` | `decimal RawTicks, string UnitId, long? TicksPerSecond, string ClockDomain, BootEpoch, CameraTimeEvent Event, string? SourceFrameKey, EvidenceState Association`；Event={HostArrival,ExposureStart,ExposureEnd,TransferEnd,DeviceFrame,DeviceLine}；RawTicks为整数，精确承载有符号/无符号64位原值，不截断或重解释负值；有官方频率才换算，原值保留 |
| `FrameInspection` | `Guid LeaseId, A<FrameBackingCharge> Allocations, string LayoutRevision, bool LayoutValid, ReadOnlyStable, string ContentSha256, CameraFaultReceipt? Fault`；帧端口校验共享layout，摘要含不可变payload及解释元信息（不含arrival）；Allocations识别所有物理分配、不是指针，capacity不按payload猜 |
| `CaptureTicket` | `SessionIdentity Session, Guid CaptureOperationId, string SinkId, CapabilityRevision, ConfigurationRevision, A<TriggerReservation> Reservations, long ArmedAt, DeadlineAt`；仅确认armed后返回，同session有效，重启仅查询 |
| `TriggerReceipt` | `Guid OperationId, CaptureOperationId, ReservationId, EvidenceState CommandIssued, Acknowledged, ExposureObserved, string? DeviceTriggerToken, CameraFaultReceipt? Fault`；ACK不证明曝光，Unknown禁止重发 |
| `CaptureOutcome` | `Guid CaptureOperationId, CaptureLogicalResult LogicalResult, int ExpectedUnits, DeliveredUnits, A<string> MissingSourceKeys, A<Guid> MissingReservations, int UnknownMissingCount, A<string> DuplicateKeys, ConflictKeys, A<DiscardReceipt> Discards, A<CameraFaultReceipt> Faults, CaptureCounters Counters, bool DetailsTruncated, long SealedAt`；LogicalResult={Complete,Incomplete,Cancelled,TimedOut,Failed,Unknown}；缺物理key时给数量/预约键，不造ID；Complete不证明产品覆盖/质量 |
| `DiscardReceipt` | `string? SourceFrameKey, DiscardReason Reason, long At, CameraFaultReceipt? Fault`；Reason={Duplicate,Conflict,StaleEpoch,Invalid,Overflow,StartupStabilization,AfterSeal,SinkRejected}；列表受MaxReceiptItems限制，完整计数在CaptureCounters，不无界存原键 |
| `CaptureCounters` | `long Received, Validated, Delivered, Duplicate, Conflict, Invalid, Overflow, Stale, AfterSeal, StabilizationDiscarded, UnknownMissing`；每项非负，计数checked；完整计数用于CaptureOutcome/OperationSnapshot，不以详情列表长度冒充总数 |
| `ResourceSnapshot` | `Guid? CaptureOperationId, long Callbacks, Workers, DriverBuffers, InternalFrames, DeliveredLeases, TemporaryResources, ulong KnownResidentBytes, bool CountsComplete, EvidenceState DeviceStopped, long ObservedAt`；非负；CountsComplete=false不得视为0；驻留池仍计容量，ResourcesReleased仅表示操作租约/临时资源实际归还，不声称宿主池物理释放 |
| `StopReceipt` | `Guid StopOperationId, CaptureOperationId, EvidenceState StopRequested, InputClosed, DeviceStopped, CallbacksDrained, DriverBuffersReturned, bool DrainCompleted, ResourcesReleased, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults`；drain需device/callback/worker/driver/internal都已空，resources再需lease/temp归还且计数证据完整 |
| `CloseReceipt` | `Guid OperationId, SessionIdentity Session, EvidenceState NativeHandleClosed, DeviceLeaseReleased, bool ResourcesReleased, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults`；前置未完成不能关闭handle/放Owner |
| `SessionReceipt` | `Guid OperationId, SessionIdentity Session, CameraCapabilities Capabilities, HealthSnapshot Health`；连接但读能力失败不得返回Success |
| `DiscoveryResult` | `A<CameraDevice> Devices, A<DiscoveryAttemptReceipt> Attempts`；精确selector去重，同selector冲突信息报故障，不自动选择 |
| `CameraDevice` | `CameraSelector Selector, string DisplayName, Model, InterfaceId, CameraSourceKind Source, CapabilityAccess Availability`；占用/未知分开 |
| `DiscoveryAttemptReceipt` | `int Attempt, long StartedAt, EndedAt, A<CameraDevice> Candidates, bool Retryable, CameraFaultReceipt? Fault`；从1计，结束≥开始 |
| `HealthSnapshot` | `SessionIdentity Session, HealthState State, DateTimeOffset? LastHealthyUtc, long ObservedAt, A<CameraFaultReceipt> Faults`；State={Healthy,Degraded,Disconnected,Unknown}；无探测能力为Unknown |
| `CameraSnapshot` | `Guid InstanceId, CameraState State, SessionIdentity? Session, string? CapabilityRevision, ConfigurationRevision, Guid? ActiveCaptureOperationId, ResourceSnapshot Resources, HealthSnapshot? Health, long LastEventSequence`；State={Closed,Opening,Ready,Configuring,Capturing,Stopping,Faulted,Disposed}；健康/逻辑/资源独立 |
| `OperationKind` | {Connect,Apply,Capture,Trigger,Stop,Close,Query}；Query只作授权分类，不在ledger创建副作用记录 |
| `OperationSnapshot` | `Guid OperationId, CameraSelector Selector, string IdempotencyKey, RequestSha256, OperationKind Kind, SessionIdentity? Session, A<OperationStageReceipt> Stages, CaptureTicket? Ticket, ConfigurationApplyResult? Configuration, TriggerReceipt? Trigger, CaptureOutcome? Capture, StopReceipt? Stop, CloseReceipt? Close, SessionReceipt? Connection, ResourceSnapshot Resources, CaptureCounters Counters, Guid? DeviceLeaseId, long? DeviceFence, string OwnerNamespace, OperationFinalState FinalState, long Revision`；Kind={Connect,Apply,Capture,Trigger,Stop,Close}；FinalState={NonTerminal,Completed,Cancelled,Failed}；本operation仍拥有的资源未知只能NonTerminal；不存像素lease |
| `OperationStageReceipt` | `long Sequence, OperationStage Stage, ConfigurationField? Field, Guid? ReservationId, EvidenceState SideEffect, DateTimeOffset Utc, long MonotonicTicks, CameraFaultReceipt? Fault`；Stage={Accepted,PermissionGranted,LeaseAcquired,BeforeDeviceCall,AfterDeviceCall,Armed,InputClosed,LogicalSealed,NativeDrained,ResourcesReturned,HandleClosed,LeaseReleased,Terminal}；每阶段序号唯一单调 |
| `CameraFaultReceipt` | `string Code, Guid? OperationId, SessionIdentity? Session, CameraPhase Phase, string? AdapterId, NativeCode, FieldPath, string ResourceKey, A<string> SafeArguments, RetryAdvice Retry, RecoveryAction Recovery, ResourceSnapshot? Resources, DateTimeOffset Utc, long MonotonicTicks`；Phase={Discover,Connect,Capabilities,Configure,Arm,Trigger,Receive,Validate,Deliver,Stop,Drain,Close,Health,Ledger,Access}；Retry={Never,AfterStateCheck,WithNewOperation}；Recovery={FixInput,ReadCurrent,QueryOriginal,ReturnFrames,CloseWhenDrained,AskDeviceOwner}；安全摘要不含图像、指针、机密 |
| `CameraEvent` | `CameraEventKind Kind, SessionIdentity? Session, Guid? OperationId, long EventSequence, DateTimeOffset Utc, long MonotonicTicks, CameraSnapshot Snapshot, string? SourceFrameKey, ConfigurationItemReceipt? ConfigurationItem, CameraFaultReceipt? Fault`；EventKind为§4全部事件加HealthChanged/FrameDiscarded/RequestRejected/SubscriberGap；事件不带TFrame |
| `ICameraEventSink` | 方法`bool TryPublish(CameraEvent notification)`；非阻塞，不抛异常；false拒收。Subscribe返回只撤当前订阅的IDisposable |
| `CameraDisposalException` | Exception派生，公开`Guid OperationId, CameraFaultReceipt Fault`；清理失败保留原ID/Owner，可Query/Close，不标Disposed |

新增稳定模块码：CAM-CAPABILITY-UNKNOWN（未知/暂不可用）、CAM-REVISION-MISMATCH、CAM-IDEMPOTENCY-CONFLICT、CAM-LEDGER-FAILURE、CAM-ACCESS-DENIED、CAM-ACCESS-REVOKED、CAM-VERSION-UNSUPPORTED、CAM-RESOURCE-INSUFFICIENT、CAM-SINK-REJECTED、CAM-OPERATION-NOT-FOUND、CAM-QUERY-TIMEOUT、CAM-STATE-INVALID。与§5既有码构成默认映射；仅显式Unsupported用CAM-UNSUPPORTED-CAPABILITY。未知native码映射CAM-ADAPTER-FAILURE保留原码，不猜设备执行状态。

### A.5 注入端口与资源协议

```csharp
public interface ICameraFrameSink<TFrame> where TFrame : class
{
    string SinkId { get; }
    bool TryDeliver(CameraFrameEnvelope<TFrame> frame);
}
public interface ICameraIngress<TFrame> where TFrame : class
{
    bool TryAccept(CameraFrameEnvelope<TFrame> candidate);
    void ReportFault(CameraFaultReceipt fault);
    void ReportHealth(HealthSnapshot health);
    void ReportEnd(AdapterEndReceipt receipt);
}
public interface ICameraFramePort<TFrame> where TFrame : class
{
    ValueTask<CameraReply<FrameInspection>> InspectAndTrackAsync(TFrame frame, Guid captureOperationId, OperationBudget budget, CancellationToken cancellationToken);
    ValueTask<CameraReply<ResourceSnapshot>> ReturnAsync(TFrame frame, OperationBudget budget, CancellationToken cancellationToken);
    ResourceSnapshot Snapshot(Guid captureOperationId);
}
public interface ICameraTransport<TFrame> where TFrame : class
{
    TransportDescriptor Descriptor { get; }
    ValueTask<CameraReply<DiscoveryResult>> DiscoverAsync(DiscoveryRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<SessionReceipt>> ConnectAsync(TransportConnectRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CameraCapabilities>> GetCapabilitiesAsync(SessionQuery request, CancellationToken cancellationToken);
    ConfigurationValidation ValidateNativeConfiguration(CameraCapabilities capabilities, CameraConfiguration configuration);
    ValueTask<CameraReply<ConfigurationItemReceipt>> ApplyItemAsync(TransportApplyItemRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CameraConfigurationReadback>> ReadConfigurationAsync(SessionQuery request, CancellationToken cancellationToken);
    ValueTask<CameraReply<AdapterArmReceipt>> ArmAsync(CaptureRequest request, ICameraIngress<TFrame> ingress, CancellationToken cancellationToken);
    ValueTask<CameraReply<TriggerReceipt>> TriggerAsync(TriggerRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<StopReceipt>> StopAndDrainAsync(StopRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CloseReceipt>> CloseAsync(CloseRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<HealthSnapshot>> GetHealthAsync(SessionQuery request, CancellationToken cancellationToken);
    ResourceSnapshot SnapshotResources(Guid? captureOperationId);
}
public interface ICameraClock
{
    long Timestamp { get; }
    long Frequency { get; }
    string DomainId { get; }
    DateTimeOffset UtcNow { get; }
    ValueTask DelayAsync(TimeSpan delay, CancellationToken cancellationToken);
}
public interface ICameraDiagnostics { bool TryWrite(CameraDiagnostic diagnostic); }
public interface IOperationLedger
{
    LedgerDurability Durability { get; }
    ValueTask<CameraReply<LedgerBeginResult>> TryBeginAsync(LedgerIntent intent, OperationBudget budget, CancellationToken cancellationToken);
    ValueTask<CameraReply<OperationSnapshot>> CommitAsync(OperationSnapshot snapshot, long expectedRevision, OperationBudget budget, CancellationToken cancellationToken);
    ValueTask<CameraReply<OperationSnapshot>> ReadAsync(Guid operationId, OperationBudget budget, CancellationToken cancellationToken);
    ValueTask<CameraReply<OperationSnapshot>> LookupAsync(string ownerNamespace, string idempotencyKey, OperationBudget budget, CancellationToken cancellationToken);
    ValueTask<CameraReply<LedgerBeginResult>> TryBeginTriggerAsync(LedgerIntent intent, Guid captureOperationId, Guid reservationId, OperationBudget budget, CancellationToken cancellationToken);
}
public interface ICameraAccessPort
{
    AccessIsolation Isolation { get; }
    string GetOwnerNamespace(CameraSelector selector);
    ValueTask<CameraReply<AccessDecision>> AuthorizeAsync(CameraAccessRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CameraAccessGrant>> RecoverAsync(Guid leaseId, CameraSelector selector, Guid instanceId, OperationBudget budget, CancellationToken cancellationToken);
    ValueTask<CameraReply<CameraAccessGrant>> AcquireAsync(CameraAccessRequest request, CancellationToken cancellationToken);
    ValueTask<CameraReply<CameraAccessGrant>> CheckAsync(CameraAccessGrant grant, OperationKind operation, OperationBudget budget, CancellationToken cancellationToken);
    ValueTask<CameraReply<CameraAccessGrant>> ReleaseAsync(CameraAccessGrant grant, OperationBudget budget, CancellationToken cancellationToken);
}
```

| 类型 | 字段/协议 |
|---|---|
| `TransportApplyItemRequest` | `CommandContext Command, SessionIdentity Session, string CapabilityRevision, ConfigurationField Field, ConfigurationValue Requested`；原Apply操作ID/预算，Core按ApplyOrder每次只执行一项；Adapter不得额外写其它字段，返回本项实际回执 |
| `AdapterEndReceipt` | `SessionIdentity Session, Guid CaptureOperationId, EvidenceState InputEnded, CameraFaultReceipt? Fault`；Confirmed为源不会再发新帧，仍须排空callback；缺帧为Incomplete，Unknown不得封成功 |
| `TransportConnectRequest` | `CommandContext Command, SessionIdentity Session`；session由Core生成，Selector包含其中，Adapter不得另建epoch；不把授权token泄漏SDK |
| `TransportDescriptor` | `string AdapterId, ApiVersion, AdapterVersion, CameraSourceKind Source, A<int> SupportedContractMajors`；major含1才组合，Source构造后不变 |
| `AdapterArmReceipt` | `SessionIdentity Session, Guid CaptureOperationId, EvidenceState Armed, long ArmedAt, ResourceSnapshot Resources`；不是最终逻辑结果；SDK先callback后Arm返回亦须支持 |
| `CameraDiagnostic` | `string MetricId, decimal Value, string UnitId, Guid? OperationId, SessionIdentity? Session, CameraSourceKind Source, DateTimeOffset Utc, long MonotonicTicks, CameraFaultReceipt? Fault`；metric固定映射§14，拒收计诊断丢失 |
| `LedgerIntent` | `Guid OperationId, CameraSelector Selector, string OwnerNamespace, IdempotencyKey, RequestSha256, OperationKind Kind, SessionIdentity? Session, DateTimeOffset Utc, long MonotonicTicks`；OwnerNamespace宿主稳定设备命名域，不来自产品身份 |
| `LedgerBeginResult` | `LedgerBeginKind Kind, OperationSnapshot Snapshot`；Kind={Created,ExistingSame,Conflict}；双索引operationId及OwnerNamespace/key原子唯一 |
| `LedgerDurability` | {MemoryOnly,Durable}；Hardware必须Durable；Commit以expectedRevision CAS，耐久确认后Success |
| `CameraAccessRequest` | `CameraSelector Selector, string AuthorityToken, Guid InstanceId, OperationKind Operation, OperationBudget Budget`；同时检查授权/原子独占，不先open后抢锁 |
| `AccessDecision` | `bool Allowed, string OwnerNamespace, CameraFaultReceipt? Fault`；纯授权查询，无独占/设备动作；命名域与GetOwnerNamespace一致，拒绝时不查缓存结果 |
| `CameraAccessGrant` | `Guid LeaseId, CameraSelector Selector, Guid InstanceId, string OwnerNamespace, long Fence, EvidenceState Valid, Released`；Fence递增由Owner治理，撤销/失联Check可见 |
| `AccessIsolation` | {ProcessOnly,CrossProcess}；Hardware要求CrossProcess及设备端或Owner证明的fencing/recovery，不能在旧设备未停时自动超期重授；ProcessOnly仅非Hardware |

Check在每个设备副作用前及采集运行检查点调用；检查间隔来自limits.AccessCheckInterval并受Host profile约束，撤销后关新触发并保留清理权限，允许Stop/Drain/Close。设备不能强制fence时宿主必须禁止失联旧Owner未对账前重授。账本/access失败在发命令前拒绝，发出后Unknown并保留Owner。Release只在handle/drain确认完成后幂等执行。跨进程防护不足拒绝Hardware，不声称本地锁可控制其它未知软件。

资源交接与线程规则：

1. Adapter拥有native buffer，默认在预留容量内复制像素/必要元数据到宿主独立lease，SDK归还成功再TryAccept；失败不能交成功帧。指针不出Adapter。零拷贝需设备生命周期证明及Frame Owner接收，默认关闭。SDK回调只必要复制/事实提取/入有界队列，不做hash、用户事件或磁盘IO。
2. TryAccept=true即转移Core；false仍Adapter拥有且必须Return。每候选只投递一次；满队列/关闭Core记录overflow/封口并受控停止，禁止静默丢弃。不以每帧Task等待空位制造无界任务。ReportFault/Health非阻塞，失败也须可从transport资源/健康快照查询。
3. Core worker在预算内InspectAndTrack，验证共享layout、只读、摘要、唯一lease/allocation并登记实际归还监测；交付前重查epoch/revision/封口。校验失败由当前Owner归还；未track的帧也允许Return，重复Return不重复释放。SDK buffer与共享lease分列，不重复计物理容量。
4. TryDeliver=true后sink拥有，false/异常视作未转移，sink不得保留/释放，Core归还并报CAM-SINK-REJECTED受控停止。sink非阻塞，只入自身有界队列；其消费任务finally Return。单帧不多播；预览/第二消费者需共享帧Owner批准的独立lease或显式复制。
5. 帧端口观察消费者真实lease归还，即使消费者直接Dispose正式lease也必须触发监测；Snapshot不得因出队减为零。未知归还保留outstanding，不能靠超时/GC清零。已归还池backing仍驻留计容量，不提前释放额度。FrameInspection是共享校验投影，不复制共享像素布局。

transport控制命令本实例串行，Stop可跨线程中止阻塞读取只在官方SDK保证时开放；clock/ledger/access/frameport可并发查询/归还。同步native放专属worker，不用UI/线程池饥饿假取消。diagnostics/event失败隔离；Snapshot一致且CountsComplete=false传播Unknown。Core合成StopReceipt：Adapter只证明device/callback/worker/native归还，frameport证明Core/消费者lease；Adapter不得虚报消费者ResourcesReleased。

### A.6 幂等、预算与生命周期顺序

canonical request hash=SHA-256：UTF-8无BOM，JSON字段按本附录声明顺序，整数不用指数，decimal去无意义尾零/不用指数，Guid小写D，TimeSpan为整数ticks，enum固定英文值，null显式null，标准JSON字符串转义且不做Unicode归一化。数组保持语义顺序，配置Triggers按selector枚举序排序且重复先拒绝。操作hash排除operationId/key、授权token、实时UTC/单调值/对象引用，包含schema/API major、完整session/revision、预算、所有配置/触发/容量/来源字段及capture SinkId。配置RequestedHash对配置本体计算且排除自身hash；外层包含已核对的配置hash。权限由OwnerNamespace限定幂等域并每次检查查询授权，不以省略token允许跨Owner读取。Connect无session时hash包含selector和请求固定字段；新epoch在ledger接纳后生成并持久化，重复Connect复用原session，不每次生成新hash。

| 入口/阶段 | 实施顺序与返回语义 |
|---|---|
| Discover | 纯校验 → 按有限策略尝试 → 精确selector去重 → candidates/attempts；取消不影响已有session，绝不open默认首台 |
| Connect | 校验 → access.AuthorizeAsync确认权限/稳定OwnerNamespace → ledger.LookupAsync查询原幂等记录 → Acquire独占（重复Acquire同实例必须返回同grant）→ ledger TryBegin → 新session/epoch及grant引用先commit → transport Connect/读取能力健康 → commit实际事实 → Ready。重复同请求只返回原Connection/阶段，不能再次open；Conflict拒绝；open未知保留grant并清理。GetOwnerNamespace仅定位，缓存读取仍须Authorize；Hardware准入前要求Durable ledger和合格CrossProcess access |
| GetCapabilities/Health | 核session → 有限只读 → 一致capability/Current；内容不变保留revision。采集中必需配置变更封口失败并stop；无健康能力Unknown，不能写设备恢复。GetCapabilities允许Ready/Faulted下安全读；采中是否可读依Adapter无副作用保证 |
| Apply | 基本形状/hash和授权/重复对账 → 仅新请求全字段纯校验/transport纯设备依赖校验 → access Check → ledger接纳/hash → BeforeDeviceCall耐久 → Core按ApplyOrder逐字段ApplyItemAsync（各次BeforeDeviceCall耐久并带Field）→ 每次回执commit → ReadConfigurationAsync读当前 → commit实际/未执行/未知 → confirmed或partial。不以重复Apply做读回；用GetCapabilities |
| Capture | 基本形状/hash和授权/重复对账 → 仅新请求核Current/revision/关联/模式 → 预检总backing上界 → sink合法 → access Check → ledger接纳/hash → 实际预留队列/容量 → commit arm意图 → transport Arm绑定ingress → commitArmed → ticket；SDK先callback后arm返回合法，接纳队列/资源先准备。arm未知不给可触发ticket，保留原IDQuery |
| Trigger | 基本形状/hash和授权/重复对账 → 仅新请求核同session/ticket/reservation且Software → access Check → ledger原子reservation claim → BeforeDeviceCall耐久 → transport命令一次 → commitIssued/ACK/Unknown。新key不能绕过已claim预约；硬触发不调用此入口 |
| 交付/封口 | 单worker线性化epoch/layout/完整性/关联/去重 → sink转移/计数 → 到ExpectedUnits、deadline、断连、冲突或取消时固定逻辑结果 → 关输入并自动CleanupBudget停止。后到帧隔离归还，不改逻辑集合；若后到同键发现冲突，保留逻辑快照并追加IntegrityFault使最终Failed，不对已交付像素进行last-wins |
| WaitCapture | query有限预算等LogicalSealed → CaptureOutcome；query到期Pending+CAM-QUERY-TIMEOUT；token只取消本次等待，不改变capture |
| StopAndDrain | 入口原子关闭capture准入 → 汇合同capture已有停止尝试 → 耐久stop意图 → Adapter停止/等待native → 内部未移交队列按AfterSeal归还 → DrainCompleted → 等实际lease归还 → ResourcesReleased → 原capture唯一最终终态；已封口逻辑Complete不因清理等待token取消改Cancelled；真实清理/完整性故障追加fault使最终Failed |
| Close | 关新准入 → 汇合本实例已接纳操作/capture清理 → 所有资源证实 → ledger close意图 → transport Close → handle确认 → access Release → commit Closed；并发Close汇合同一次尝试，已成功阶段不再次发设备命令 |
| Query | access.AuthorizeAsync(Selector,AuthorityToken,Operation=Query) → ledger原ID Read → 核回执OwnerNamespace/原selector → 阶段/逻辑/drain/resources/final；必要合并本进程未耐久事实必须标Unknown，不冒耐久成功；NotFound不证明设备未执行、不产生设备动作 |

LookupAsync/TryBeginTriggerAsync已统一在A.5的IOperationLedger中，用于跨进程原请求定位与预约唯一claim。

Lookup纯查询，未命中NotFound；TryBeginTrigger在同一耐久事务中完成operation/key唯一登记与(capture,reservation) claim，已claim返回原operation或Conflict，不能先claim后落盘留下无主预约。TryBegin和TryBeginTrigger Created的初始snapshot为Revision=0、FinalState=NonTerminal，字段合法缺省/null只用于尚未发生阶段，不用Unknown伪装Complete。设备grant引用以OperationSnapshot的DeviceLeaseId/DeviceFence/OwnerNamespace持久化；A.5 RecoverAsync仅核原grant，不新授Owner。重启恢复原InstanceId需Host从原snapshot构造恢复上下文，不能伪造当前实例仍持旧lease；Core仅返回Unknown供Host治理，自动续跑旧capture禁止。

重复：同owner/key同hash返回原operation，即使调用方新operationId也不建第二动作；同operationId换key/同key异hashCAM-IDEMPOTENCY-CONFLICT。lookup后仍核当前权限才能返回机密结果；仅查询权限不足不能重新设备动作。capture同实例SinkId及对象绑定必须一致，不允许重复请求换sink；重启只对账，不续送旧像素。CAS冲突有限重读，不重发硬件命令。before-call/after-call之间崩溃必Unknown；本地幂等不保证设备exactly-once。

接纳前token取消无设备副作用；接纳后命令token只取消调用方等待，Core以原ID继续对账/必要清理，未发阶段是否取消以实际阶段证据为准。显式取消采集用Stop(Reason=Cancelled)；总deadline由Core封口TimedOut并启动独立CleanupBudget。Wait/Query/Stop等待取消不撤已发stop，不丢Owner；新的Stop/Close等待继续未完成阶段，不重复已成功设备阶段。内部适配调用用生命周期token及剩余预算，不把页面token等同native已取消。

Stop入口关准入即使ledger故障也生效；正常设备清理先耐久登记，ledger故障时不发新普通动作，但对已接纳的持续采集仍尝试必要受控停止/清理一次，保留未耐久Unknown及Owner对账门，不宣称exactly-once。释放失败只有SDK明确可安全重试才允许继续；无法证明则保持outstanding。停止不等于外部硬件急停，不承担外部安全系统时延。

DisposeAsync使用limits.DisposeBudget汇合本实例关闭，不拥有宿主端口；具体未移交Connect、无Session、纯未尝试及固定close身份按§9.3处理。成功后Disposed、重复完成；失败抛CameraDisposalException并保持Faulted/查询/清理入口，不能丢引用或强制释放native。Disposed后Snapshot、Query及原已释放receipt允许只读，新命令拒绝。事件/callback/sink不得同步等待需要自身退出的Stop/Close。消费者释放lease与drain并行，不能等待FinalState/Close才释放。



资源按操作和会话分别归属：Connect 成功将长期 handle/device grant 从连接尝试明确移交本实例 Session Owner，能力/临时资源释放且移交耐久后，Connect operation 可 Completed，不要求先 Close 才返回最终连接回执。Apply/Trigger 的临时资源结束并取得实际回执即可结束该命令 operation；触发 Unknown 仍 NonTerminal。Capture 必须等其 native/in-flight/internal/消费者 lease 全部归还才终结；session handle/grant仍由 Session Owner 持有，不计作 capture 未归还临时资源。Close 负责释放 session 长期资源。OperationSnapshot.Resources按该operation范围，CameraSnapshot.Resources按本实例全部范围，DeviceLeaseId/Fence保留关联证据。失败连接没有完成移交时仍由连接 operation 保有资源，未知禁止终结/重开；不能靠虚构“移交成功”清零。

其他可执行边界：Core.ValidateConfiguration只执行公开域/依赖纯校验；Apply内部额外调用ValidateNativeConfiguration（同样无副作用），设备特有条件失败回传字段错误并保留草稿，UI不重复实现厂商校验。在arm确认前到达的candidate只能有界缓存在Core，确认后再校验交付；arm失败/未知的缓存全部隔离归还，不能先交帧冒充已启动。Sink抛异常视作合同违反，隔离/停止且不得同时声称已转移；sink不得“先取得再抛”。源frame key、行数与计数器解释是Adapter锁定协议，而非Core猜测。

有限budget从clock.Timestamp/正Frequency以checked换算，溢出拒绝，不使用UTC计截止；跨进程旧monotonic ticks只能作历史证据，不直接继续计预算。Close/Stop重入只请求并异步汇合，不能在正在派发的sink/event线程等待自身退出。Core 内存预留是本实例额度内的原子 reservation；平台总额度由Host预先提供，Core不能向未知总账扩容。Production frame分配器/已有共享frame factory由Adapter组合根注入，C2按Frame Owner正式合同接入；它不成为Core的第二frame factory，C1由Simulator生成ManagedTestFrame。


### A.6.1 第一轮反例裁决：完整性、重复入口和有限观察

本节细化 A.1–A.7 同一契约，不引入第二套入口。

- **重复先对账，再校验当前可执行状态。** Apply/Capture/Trigger 的准入顺序改为基本形状/hash校验 → 当前授权 → ledger查同key/同operation → 返回原回执或Conflict → 仅新请求执行当前revision/state校验。旧请求完成后设备revision变化、当前已Stopping、预约已claim或实例已Disposed，均不能让同请求被误判“新命令”并重发；不同hash仍Conflict。授权失败不返回原结果。同key换operationId可取原回执；同operationId换key直接Conflict。查询等候不新登记操作。首次Connect取得grant但TryBegin失败/竞争ExistingSame时，只有确认本次没有新open、grant未归属既有session才Release；同实例幂等Acquire返回原grant时禁止误释放它。
- **配置/能力摘要无递归。** Capability ContentHash 只含 SchemaMajor、Adapter/设备版本、Source/Geometry、参数域/枚举/依赖/Transport/LineBlock及Evidence的SourceReference/Version/Hash；排除Session、Revision、ContentHash、Current和ObservedUtc。Revision为该hash，重连仍由session/epoch区分。Current事实摘要只含SchemaMajor、capability revision、按字段/selector排序的ReadBack状态与Actual强类型值；排除ConfirmedConfigurationRevision、Requested/Before/Applied/时间/故障文字/本摘要。全部采集必需字段已读且合法时ConfirmedConfigurationRevision为该事实hash；字段未知不造confirmed。请求配置hash包含明确输入和RequestedRevision，但排除自身RequestedHash；它与实际事实revision不同，不能混用。Apply全成功返回Current实际hash，requested revision作为来源保留。
- **公开摘要工具。** Contracts提供静态纯值类 `CameraCanonical`，所有方法返回 `CameraReply<string>`，JSON无任何布局空白/末尾换行：`HashConfiguration(CameraConfiguration)`、`HashCapabilities(CameraCapabilities)`、`HashCurrent(CameraConfigurationReadback)`、`HashConnect(ConnectRequest)`、`HashApply(ApplyRequest)`、`HashCapture(CaptureRequest, string sinkId)`、`HashTrigger(TriggerRequest)`、`HashStop(StopRequest)`、`HashClose(CloseRequest)`。字段顺序按本附录形状表；操作投影为对象键 `ApiMajor`（1）、`OperationKind`、`Request`（对应请求按A.6排除项）及capture的`SinkId`；不可把运行对象序列化。字符串采用System.Text.Json规范转义，Unicode scalar非法/未配对代理字符拒绝；显式选择 `JavaScriptEncoder.UnsafeRelaxedJsonEscaping` 以保留非ASCII原字符，仅在内部hash字节使用、不用于HTML。schema字段名保留PascalCase，decimal零输出0、布尔小写，SHA256输出64位小写hex。嵌套Closed联合编码为 `Kind` + `Value`，Kind取A.3派生record名称；ConfigurationField排序Kind枚举序再selector序。能力集合按FormatId、selector/source（Ordinal）、enum序稳定排序，配置Dependencies按Target/Prerequisite/Kind排序；语义有序的Reservations保留Ordinal序。无UI与UI调用同一工具，不让消费者另猜规范。
- **线扫/多预约。** Reservations是预期触发协议，不等于帧数组；每帧/块的FrameAssociation.Reservations逐项携带设备token。只有实际verified的预约可从MissingReservations移除；一个预约默认只关联一个完整delivery unit，明确FrameStart/AcquisitionStart批次规则允许一对多时须声明AssociationScope=PerCapture并绑定AssociationRuleRevision，每个所覆盖源键在FrameFacts逐项留关联证据，不能依据时间最近法。RawLineDelivery只在Adapter内按LineIdentityRuleRevision/Closure形成完整块，Core仅收完整LineBlock；行数/缺行/重行证据进入传输完整性，不以byte长度相同证明无缺行。FrameFacts.Lines按A.4的LineBlockFacts定义，面阵null，无可信行键两端为null，Completeness只有设备完整块证据或已验证连续行区间才能Confirmed。行键64位溢出按原协议处理，不能靠加1猜wrap。
- **封口边界。** sink成功转移和Delivered计数在同一个Core短门线性化；取消先赢则帧不交付、当前Owner归还；转移先赢则该帧保留、消费者归还。到齐且已处理输入无故障时LogicalSealed=Complete，不等同最终资格。Stop/取消显式封口后内部尚未移交帧均记录AfterSeal并归还，不再“完成旧队列”改变集合；若设备明确提前结束且K<N为Incomplete，总deadline则TimedOut，未知设备执行/关联为Unknown，冲突/坏帧/overflow为Failed。封口后仍观察已准入callback至native drain，后到同键冲突追加故障使最终Failed，不撤换已交付帧。先Wait逻辑仅供预览/候选处理，消费者须等最终资源回执和故障集合才能认定本次采集链完成。
- **资源失败不假释放。** InspectAndTrack返回Success需布局/摘要读scope已结束；若其异步工作尚未停止，frameport必须在Snapshot报告Workers/TemporaryResources且Return只能请求归还、不能回池。Core保留原inspection任务，只有限等候/观察，不重新发起Inspect。TryAccept/TryDeliver的false含义仅适用于调用者当前确有所有权的合法帧；再次投递同一个已转移lease是Adapter合同违例，隔离CAM-FRAME-CONFLICT，禁止第二次Return已移交对象。不同新lease但相同source key仍按重复/冲突规则唯一归还各自lease。
- **实际计账。** CameraLimits的MaxActiveOperations/MaxRetainedOperations均为必填正整数；命令/排队/停止观察等待者都占有限槽，槽满CAM-RESOURCE-INSUFFICIENT，不创无界等待Task。ledger也遵守同上限，未终结/未知及reservation claim禁止自动删除，已完成墓碑不在连接重启时清空；满则拒绝新普通操作，保留既有Query/必要Stop/Close控制槽。解除历史占用由Host治理的明确保留/迁移策略完成，不把本模块擅自清空作为恢复。去重表最多ExpectedUnits+MaxDiscardUnits个源键，达到上限拒绝额外输入并受控停止；buffer物理预算以已分配容量及在途上界计算，不只按列表条数。

`OperationBudget`的Total同时约束前台观察；已接纳后外部端口/worker未结束时入口必须在Total内返回Pending/Unknown/WaitCancelled和原ID，后台仍由Owner排空，不无限await SDK或抛弃任务。Stop/Close/Dispose的观察亦有限；一个有限周期结束后只有安全清理任务继续，普通配置/触发禁止开始。自动停止使用由capture派生的稳定ID：取 `SHA256(UTF8("CAM/1/cleanup/") + 原capture Guid的RFC4122大端16字节)` 前16字节（若全零则末字节置1）作为stop operationId，幂等key为 `cleanup/<captureGuid小写D>`；内部Dispose的base及前缀 `CAM/1/dispose/` 按§9.3同规则生成固定close ID；已移交session/未移交connect/纯实例三条分支首次确定后冻结。保持同capture/session一个清理任务，用户新Stop/Close只有限观察/继续原未完成阶段；控制回执必须给实际原清理operationId，不装作调用者新ID已执行另一命令。


### A.7 有界通知、完整性与版本

生产像素仅经sink；事件是投影。每session eventSequence从1递增；事实先commit后通知，每订阅独立MaxEventQueue队列。溢出显式SubscriberGap并断开该订阅或要求Snapshot/Query恢复，不承诺无界事件回放；终态权威在耐久Query，不能因通知丢失丢终态。通知回调异常隔离。§4“帧与终态不得丢弃”指生产sink交付和权威回执，不要求慢UI通知无限缓存。

duplicate键域是epoch/sourceFrameKey/config revision，按不可变content hash分相同/冲突；arrival不同不形成新帧。Correlation Required缺设备证据启动前拒采；NotRequired也需稳定的传输frame key（Adapter声明来源与reset行为），不得以arrival伪造物理曝光身份。frame序号回卷歧义封口Unknown。有限集合详情至MaxReceiptItems；结果的DetailsTruncated与Counters明确详情截断及全计数，截断后不宣称完整missing/conflict列表。关键配置结果/预约/阶段数组不能截断改变语义：预检请求项数及最坏阶段数上界，超限准入前拒绝；运行中的大批错误只做有界聚合计数及首尾key，仍保留最终错误类别与UnknownMissingCount。不另造无消费方证据文件。

API major=1，本文v0.2为设计修订而非发布包。Core/Contracts/Simulator/Adapter/UI分别版本；同major增加可选字段须明示缺省行为，更改单位/Owner/取消/键/触发/封口/资源语义升major。SupportedContractMajors不含调用者major则CAM-VERSION-UNSUPPORTED无设备动作。消费者锁定Core/Contracts、frame port、Adapter/SDK/固件/OS/位数及UI25.2.3矩阵；不以文件存在推断兼容。旧配置先无副作用显式迁移，未知单位/revision拒绝；按§16排空后换包/回退，禁止两个包同时持同设备。

### A.8 唯一工程与实施范围

下列是切片接收后的规划落点，不是本轮创建工程或写代码授权。既有同职责代码先核消费者/测试再接入，不覆盖用户基线。

| 工程/命名空间后缀 | 唯一工程路径与职责 |
|---|---|
| Contracts | `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Contracts/Asun.Pcb.Modules.CameraAcquisition.Contracts.csproj`；net10.0，全部强类型合同/端口，无UI/SDK/产品引用 |
| Core（无后缀） | `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.csproj`；net10.0，仅Contracts/BCL，完整状态/有限队列/幂等/资源协调 |
| Simulator | `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Simulator/Asun.Pcb.Modules.CameraAcquisition.Simulator.csproj`；net10.0，ManagedTestFrame/帧port、可控时钟、内存ledger、ProcessOnly access、面阵/线扫确定性源，仅Simulation/Replay |
| Tests | `tests/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Tests/Asun.Pcb.Modules.CameraAcquisition.Tests.csproj`；net10.0、Microsoft.NET.Sdk、OutputType=Exe，仅BCL/受测工程，执行A.9全部确定性断言；不用未选测试包 |
| TestHost | `samples/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.TestHost/Asun.Pcb.Modules.CameraAcquisition.TestHost.csproj`；net10.0 console，§9全调用链及独立消费者，无UI/SDK |
| Integration | `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Integration/Asun.Pcb.Modules.CameraAcquisition.Integration.csproj`；net10.0，C2 SharedCameraFramePort桥接共享Resources，不成为C1 Core依赖；公开类型映射见A.11 |
| Adapters.Mvs | `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Adapters.Mvs/Asun.Pcb.Modules.CameraAcquisition.Adapters.Mvs.csproj`；net10.0-windows/x64，指定4.8.1.0SDK仅此引用 |
| Adapters.Halcon | `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Adapters.Halcon/Asun.Pcb.Modules.CameraAcquisition.Adapters.Halcon.csproj`；net10.0-windows/x64，只经AsunImage公共引用，无直接halcondotnet |
| Wpf | `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Wpf/Asun.Pcb.Modules.CameraAcquisition.Wpf.csproj`；net10.0-windows/UseWPF，公开Core/Contracts/宿主viewport、直接本机25.2.3，三语/投影，不引用产品VM |
| Tests.Wpf（C5后续验证） | `tests/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Wpf.Tests/Asun.Pcb.Modules.CameraAcquisition.Wpf.Tests.csproj`；net10.0-windows/UseWPF/OutputType=Exe、x64，仅BCL/本模块Wpf/Core/Simulator及本机25.2.3，双STA执行CAM.W1.01～09；不改变无UI Tests工程 |
| Tests.Adapters（C3/C4后续验证） | `tests/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Adapters.Tests/Asun.Pcb.Modules.CameraAcquisition.Adapters.Tests.csproj`；net10.0-windows/OutputType=Exe、x64，仅本模块Adapter及其已批准依赖；fake调用层只在Adapter内部测试可见，不泄漏厂商句柄到Core；实际加载/取流/释放与HIL分别标记 |

命名空间均以 `Asun.Pcb.Modules.CameraAcquisition` 加表内后缀，不得在Contracts引用厂商/WPF或复制image-frame布局。C1允许前五工程内必要文件，不写设备/WPF工程、不接实机、不定义新共享FrameLease；C2–C5分别接收才写对应工程/定向测试，共享契约/宿主修改由主会话串行安排。禁止参考项目、原始证据、用户配置、其它模块、平台DTO/产品状态、规则/入口/进度路径。代码基线、授权未接收前仅此指导可修改。

最小Host唯一失败清理顺序见§9.1～9.3：先恢复槽/预持ID，操作与消费在try中，sink/Stop、Close、Dispose用嵌套finally独立收尾；无移交session只由原Core.Dispose清理，所有Query异常独立记录且不跳过收尾。不自动新开。独立工具换配置/日志/sink重复同链，不改Core；模拟正常3帧/缺第三帧/重复/持帧取消/断连迟到验证逻辑、drain、资源各轴，未知保留实例和Owner并非零退出。后续定向build/test及Profile测量按受影响工程执行，HIL/WPF/真实性能各自报告，不把模拟PASS升级生产PASS。

### A.9 Simulator、两个 BCL 消费者与验证命令

Simulator 命名空间为 `Asun.Pcb.Modules.CameraAcquisition.Simulator`，类型只在非Hardware验证使用，均不成为共享frame contract。

| 类型/构造 | 固定形状、所有权和用途 |
|---|---|
| `ManagedTestFrame` | sealed class，构造 `(Guid leaseId, string allocationId, ReadOnlySpan<byte> payload, TestFrameLayout layout)`；构造checked校验/按精确长度复制，数组私有不外露，提供只读 `LeaseId/AllocationId/Layout/IsReturned` 和同步 `CopyRow(int row, Span<byte> destination)`；Return与CopyRow在同短门协调，正在复制未结束不能覆写/回收，Return幂等；不把CPU模拟数组当HALCON对象 |
| `TestFrameLayout` | record `int Width, Height, StrideBytes, string FormatId`；仅`Mono8`和`Rgb8Interleaved`确定性fixture，width/height/stride正，checked最小行字节及完整backing，capacity≤Array.MaxLength/int.MaxValue/limits.MaxResidentBytes，溢出/OOM无遗留额度；不支持格式明确拒绝，不自行写生产格式转换算法 |
| `ManagedTestFramePort` | ctor `(ICameraClock clock, CameraLimits limits)`，实现ICameraFramePort<ManagedTestFrame>；按lease与allocation真实归还监测，登记不可变摘要/checked capacity，CopyRow取副本后hash，拒绝重复lease持有；生产共享类型由C2桥接替换 |
| `SimulatorClock` | ctor `(long frequency, string domainId, DateTimeOffset startUtc)`；frequency>0，实现ICameraClock，测试显式 `Advance(TimeSpan elapsed)` 唤醒Delay；ticks与UTC统一推进但deadline只读ticks，故障测试可另 `SetUtc(DateTimeOffset)` 不影响ticks |
| `InMemoryOperationLedger` | ctor `(ICameraClock clock, CameraLimits limits)`，MemoryOnly，TryBegin/Trigger双索引CAS及claim与durable端口同语义，仅进程内；重启用受控内存snapshot重装测试表示“恢复fixture”，不宣称持久存储通过 |
| `ProcessCameraAccess` | ctor `(ICameraClock clock, CameraLimits limits)`，ProcessOnly，共享此对象的两个模拟Core独占相同selector；测试 `SetPermission(string authorityToken, bool allowed)`/`Revoke(Guid leaseId)` 明确授权变化，默认未登记token拒绝；清理权限保持，不能模拟授权为空即允许 |
| `CameraSimulator` | 非泛型公开类，ctor `(SimulatorPlan plan, ICameraClock clock, ManagedTestFramePort frames, CameraLimits limits)`，实现ICameraTransport<ManagedTestFrame>；Core自行构造，不隐藏创建第二Core；Source=Simulation |
| `SimulatorPlan` | record `CameraSelector Selector, CameraCapabilities CapabilityTemplate, A<SimulatorStep> Steps`；template中的Session在Connect时统一替换为Core传入Session，Current/Revision按A.6.1重建；不把模板Guid冒活动session |
| `SimulatorStep` | record `long Ordinal, SimulatorSignal Signal, TimeSpan OffsetFromArm, Guid? ReservationId, FrameFacts? FactsTemplate, TestFrameLayout? Layout, A<byte> Payload, string? FaultCode`；Signal={Frame,Disconnect,DeviceEnd,ArmUnknown,ReturnUnknown,StallNative,TriggerAckLost}；offset≥0且有界，ordinal唯一稳定；Frame须完整layout/payload/facts，设备事件无payload；Frame模板session/capture只在arm时绑定，预声明源键不按到达顺序造关联 |
| `RecordingFrameSink` | ctor `(string sinkId, ManagedTestFramePort frames, ICameraClock clock, CameraLimits limits)`，实现sink；有限队列TryDeliver只转移，`ValueTask<CameraReply<ResourceSnapshot>> DrainAsync(OperationBudget, CancellationToken)`停止消费/归还所有已接收并有限观察，拒绝的frame不保留；`HeldCount`/`DeliveredFacts`为有界观察；消费错误finally归还，不等最终终态 |

SimulatorSignal.DeviceEnd由A.5 ingress.ReportEnd及AdapterEndReceipt表达提前终止，Confirmed表示设备不会再为该capture发新帧（仍须排空已有callback），非完整请求则Incomplete；Unknown不封成功。Core主动ExpectedUnits/deadline封口不依赖该通知。`SimulatorSignal.Frame`可把同一payload用两个独立lease送重键反例，禁止再次移交同一个已被sink持有的lease。线扫fixture每行一个递增值，Adapter验证原行区间后形成完整块；缺行只ReportFault/拒交，不补行。

两个无UI消费者使用同一个TestHost Exe的两个独立mode：`inspection-source` 使用自有配置、sink返回只读行副本给占位纯计算消费者；`standalone-capture` 使用不同selector/profile/log/sink独立单拍/有限连续/线扫/取消。前者只验证公开帧交接，不加入真正缺陷/工艺判定；两mode分别构造Core/ports，不能通过共享产品ServiceLocator运行。测试把两mode作为单独组合根函数，并断言删去任何一个不会改变Core引用。测试复用一个ProcessCameraAccess才可证模拟双实例独占；不同access对象不宣称跨实例设备治理。

唯一Tests工程为A.8的net10.0 BCL Exe，入口固定顺序执行CAM.C1.01～17。本轮按主控明确指定的10s/120s/180s约定补齐DEV-GOV-010有限截止要求：当前DEV-GOV-010 §3.1正文给出有限case/外层进程规则，未直接列这三个数字；此处数字是本模块冻结的软件验证fixture，非相机实际时延目标。每case从装配起**真实单调10s**（包含try/finally、保留/清理及断言）；整个Core suite从第一case前开始**真实单调120s**，独立外层执行器从启动dotnet run开始**真实单调180s**。case截止取min(case起点+10s,suite剩余)，不得因有17例把suite改成170s，必需项未完成/跳过非零。两个TestHost mode各采用真实总120s/外进程180s，单次采集及恢复仍按10s case观察边界。

固定clock fixture为frequency=1,000,000 ticks/s、起始Timestamp=0、UTC=2026-10-10T00:00:00Z、domain=`camera-core-test-v1`；每例使用独立clock/ports/IDs，跨例不清空未知真实Owner冒成功。请求OperationBudget(Total=2s,Queue=1s)，Stop/Close观察3s/1s、CleanupBudget=DisposeBudget=3s、AccessCheckInterval=100ms，恢复虚拟总窗口10s；模块工程范围/容量值按各例明确有限fixture输入。正常虚拟事件以1ms固定Advance递进，最多10,000步；每步先按ordinal释放已安排事件并让continuation运行至约定闩锁，禁止Thread.Sleep实现设备同步。闩锁采用BCL TaskCompletionSource与RunContinuationsAsynchronously，case finally释放本例可控停滞闩锁并收取已有Task；不得为通过检查创建新native/inspection工作。模拟clock停滞时真实Stopwatch和有界Task.WhenAny观察仍在10s内失败，不能依赖虚拟clock自己唤醒挂死测试。

任一错误、超时、必需项未完成/跳过返回非零且打印case ID、原operation/资源状态。预期Unknown反例必须先证明原Owner/任务/资源确被保留，再在同例闩锁明确释放后确认实际清理完成；否则case非零，不因为“预期超时”容忍泄漏任务。外层180s超时标记失败/未知、记录未结束case并终止**测试进程**，不得把终止当设备停止或资源归零；不拿dotnet test空执行当验证。TestHost为Microsoft.NET.Sdk/net10.0/OutputType=Exe，无PackageReference。生产Benchmark/实机HIL另用正式Profile，不采用这组软件fixture阈值。

```powershell
dotnet build src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.csproj -c Release
dotnet run --project tests/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Tests/Asun.Pcb.Modules.CameraAcquisition.Tests.csproj -c Release
dotnet run --project samples/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.TestHost/Asun.Pcb.Modules.CameraAcquisition.TestHost.csproj -c Release -- --mode inspection-source
dotnet run --project samples/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.TestHost/Asun.Pcb.Modules.CameraAcquisition.TestHost.csproj -c Release -- --mode standalone-capture
```

这些是获准实现后的命令，本轮不创建工程、不执行不存在的工程命令。

| 用例 ID | 输入/控制事件 | 必须判定的断言 |
|---|---|---|
| CAM.C1.01 | §19 ROI/曝光合法及越界/非步进/Unknown域、空/default数组、无sink/坏revision | 合法同UI/无UI纯校验结果；非法set/arm/trigger=0且字段码准确，无ledger新副作用；能力Unknown不映射Unsupported |
| CAM.C1.02 | 曝光write成功、ROI拒绝、readback未知；重复原Apply且当前revision已变 | 全请求项有结果、后续set=0、confirmed为空；重读获取事实而非重放set；原key取原partial，异hashConflict |
| CAM.C1.03 | 三个Mono8有效独立lease，软预约/ACK/设备token分别显式 | Armed后才Trigger、FrameFacts证据正确；Delivered=3、LogicalComplete，消费者归还后drain/resources true、capture唯一Completed，session资源仍由Host持有 |
| CAM.C1.04 | §19 A/B/B、设备明确DeviceEnd；另同输入仅deadline | 两次真实交付、duplicate=1；DeviceEnd=>Incomplete，deadline=>TimedOut；有预声明C则missing=C，否则UnknownMissingCount=1，不造frame key |
| CAM.C1.05 | 单块100行缺99或重复98；另完整100行且FrameStart+100个LineStart预约 | 缺行交付0/lease全部归还；完整关联数组包含设备已验证预约，三种frame/line/pulse计数不混用，不因单FrameStart ACK宣称完整 |
| CAM.C1.06 | Arm内同步callback后返回Unknown；调用者观察取消 | arm前无sink移交、缓存有界；返回原ID，必要stop继续，所有未交付lease归还；未确认不发Trigger |
| CAM.C1.07 | sink false/抛异常、慢消费者队列满、独立lease重键冲突、同lease再次回调 | false/异常Core仅归还本次合法所有权；新lease恰好Return一次；旧已转移lease不被第二Return；生产不DropOldest，冲突capture最终Failed |
| CAM.C1.08 | Stop与sink转移闩锁竞态、消费者持帧并行Return、Stop查询token取消 | 转移/取消有单一线性化结果；逻辑固定，callback/driver与lease两轴独立；有限观察返回Pending/WaitCancelled，原清理任务唯一、资源未知不重开 |
| CAM.C1.09 | inspector/native停滞、释放异常、并发Close/Dispose、同步重入事件 | 不同步等自身回调；有限观察/原ID/资源占用保留，失败不Disposed，不放grant；晚到真实完成后只继续未完阶段、close/stop成功阶段不重复 |
| CAM.C1.10 | 两实例同selector/shared access；授权撤销；Query错selector/token；重启snapshot恢复 | 第二OwnerBusy，撤销阻新Trigger但允许原清理；越域Query拒绝不泄漏原结果；旧epoch帧不进新session，原UnknownTrigger不重发、旧ticket不续跑 |
| CAM.C1.11 | 同reservation不同key并发；before-call后崩溃；ledger CAS/耐久失败 | claim事务最多一命令，第二请求返回原operation或Conflict；after-call缺失Unknown；CAS只对账不再trigger，必要停止账本故障标未耐久 |
| CAM.C1.12 | stride溢出/OOM、容量N/N+1、allocation共享、多lease、inspection未结束归还 | checked拒绝，无越界读/泄漏reservation；按allocation物理计一次、lease槽分别计；Return观察超时不回池；未知不算零 |
| CAM.C1.13 | 摘要同输入、字符串Unicode/decimal表示、时间/Current变而静态能力不变 | Hash工具稳定无自引用；ObservedUtc/Current不改CapabilityHash，实际readback改CurrentHash；hash碰撞不借助字段字符串拼接判断，非法UTF16拒绝；配置哈希校验不写设备 |
| CAM.C1.14 | 版本不支持、两个独立mode、三次连接关闭、回退但旧lease未空 | major不兼容无设备动作；两个组合根完整运行；新旧Owner不能同时开，未知资源阻回退；Core无WPF/SDK/产品引用 |
| CAM.C1.15 | 无订阅/慢订阅溢出、100个额外事件、限额达到 | 无订阅也完成；SubscriberGap/Query可恢复且通知不带像素，MaxReceiptItems截断明确Counters不丢；新命令额度满拒绝，原Stop/Close保留控制槽 |
| CAM.C1.16 | Connect已预持ID但在实际open/回执移交之间Unknown、等待取消或抛错；无公开Session；对照完全未尝试Connect路径 | Host不构造假Session/CloseRequest；Dispose固定base=connectId且晚到Connect不换ID、不Ready、不二次open；Query原Connect/固定close按selector授权，NotFound不当未执行；原Task/Owner/槽保留，闩锁释放后一次实际close/release。未尝试路径仅无资源Disposed可无ledger记录 |
| CAM.C1.17 | CaptureAsync返回ticket前抛错；下游消费、Stop观察、Query、Close分别故障/取消；组合根恢复槽满或移交未确认 | 调用前captureAttempted/ID已登记；可用成功session按原IDStop、否则Dispose内部清理；sink归还并行；一个异常不跳过Close/Dispose嵌套finally；独立预算不复用取消token/不重置截止。slot满动作数0；未确认移交原Owner不退出、不释放槽、整体非零；故障闩锁收回后无遗留Task/lease。按10s case/120s suite/180s进程边界证明必需未完成非零 |

Benchmark执行复用上述mode/fixture和§14测点，由TestHost显式 `--mode benchmark --profile <Host批准profile路径>`（profile由Host所有，不另建默认文件）运行：输入profile缺单位/hash/样本数/总截止/资源上界则拒绝；缺目标值可诊断但NotEvaluated；全链从capture接纳至ResourcesReleased，另测logical seal、native drain、消费者归还、取消/触发/CopyRow/摘要字节量。故障/未完成/删失单列，使用DEV-GOV-010唯一P50/P95/P99口径；合成吞吐不冒SDK/相机FPS。Profile解析属于TestHost，不给Core增加持久化权威。

### A.10 可选 WPF 显式挂接与关闭合同

此切片命名空间 `Asun.Pcb.Modules.CameraAcquisition.Wpf`，不由Core创建窗口，不把WPF投影DTO写入Contracts。`CameraAcquisitionControl`为可嵌入UserControl，公开无参构造仅构建被动视图，未挂接时所有设备命令禁用；唯一挂接工厂 `CameraWorkbenchFactory.AttachAsync<TFrame>(CameraAcquisitionControl view, CameraWorkbenchOptions<TFrame> options, OperationBudget budget, CancellationToken cancellationToken)` 返回 `ValueTask<CameraReply<CameraWorkbenchAttachment<TFrame>>>`，TFrame:class。同view有未关闭attachment时拒绝第二次挂接；设备session/生产sink始终归Host，本工厂不隐式Connect/Start，也不转移Core生命周期。

| WPF 类型/端口 | 字段/方法及Owner |
|---|---|
| `CameraWorkbenchOptions<TFrame>` | record `ICameraAcquisition<TFrame> Core, ICameraFrameSink<TFrame> ProductionSink, ICameraWorkbenchPreviewPort Preview, ICameraWorkbenchResourcePort Resources, CameraWorkbenchPermissions Permissions, string CultureName, ThemeName, OperationBudget CommandBudget, CloseBudget, TimeSpan RefreshInterval, int MaxVisibleRecords, CameraWorkbenchInputs Inputs`；Inputs完整字段/命令接线见§10.3；culture为zh-CN/zh-TW/en-US，未知language用zh-CN并显式诊断；预算/刷新/显示容量正且有限。命令仅传同Core及同sink，UI不取得像素所有权 |
| `CameraWorkbenchPermissions` | record `bool CanDiscover, CanConnect, CanConfigure, CanCapture, CanSoftwareTrigger, CanQuery, CanRequestStop`；Host显式更新；这是可见/启用投影，最终设备授权仍由Core access判定，不能因按钮enabled获得权限。生产工作台停止/关闭必须有受控Owner路径，UI不凭布尔强占他人session |
| `CameraWorkbenchAttachment<TFrame>` | sealed class/`IAsyncDisposable`，只由工厂返回；只读 `Guid AttachmentId, long Generation, bool IsClosed, ResourceSnapshot PreviewResources`。方法 `void SetInputs(CameraWorkbenchInputs inputs)`、`void SetLanguage(string cultureName)`、`void SetPermissions(CameraWorkbenchPermissions permissions)`、`void SetTheme(string themeName)`、`ValueTask<CameraReply<WorkbenchCloseReceipt>> CloseAsync(OperationBudget budget, CancellationToken cancellationToken)`；所有UI改变派到view.Dispatcher，旧generation通知丢弃但其预览lease仍必须归还 |
| `ICameraWorkbenchResourcePort` | `string Resolve(string resourceKey, A<string> safeArguments, string cultureName)`；非阻塞、不抛，缺key返回本模块三语通用“操作失败，请查看诊断/操作失敗，請查看診斷/Operation failed. Check diagnostics.”并附稳定Code，计缺失资源诊断，不展示key当成功说明；缓存按culture/revision隔离 |
| `CameraPreviewItem` | record `Guid CaptureOperationId, string SourceFrameKey, ulong FrameRevision, int Width, Height, string PixelFormatId, CameraSourceKind Source, EvidenceState Validity`；有界元数据，frame revision/尺寸来自宿主已有frame合同；不带TFrame/指针 |
| `PreviewSelection` | record `Guid AttachmentId, long Generation, CameraPreviewItem Item, OperationBudget Budget`；显式选帧revision，禁止以当前latest代替指定帧 |
| `CameraPreviewReceipt` | record `Guid AttachmentId, long Generation, Guid? ProjectionLeaseId, bool Presented, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults`；只在宿主独立预览lease有效且显示完成才Presented；资源Owner为Preview port，非生产sink |
| `ICameraWorkbenchPreviewPort` | `System.Windows.FrameworkElement View { get; }`、`A<CameraPreviewItem> SnapshotItems(Guid attachmentId)`、`ValueTask<CameraReply<CameraPreviewReceipt>> SelectAsync(PreviewSelection request, CancellationToken cancellationToken)`、`ValueTask<CameraReply<CameraPreviewReceipt>> ReleaseAsync(Guid attachmentId, long generation, OperationBudget budget, CancellationToken cancellationToken)`、`ResourceSnapshot SnapshotResources(Guid attachmentId)`；Host桥接已批准viewport，不重新绘图算法/布局。port为当前attachment取得独立只读投影，所有暂停/换图/迟到/异常Release负责实际归还 |
| `WorkbenchDisposalException` | Exception派生，公开 `Guid AttachmentId, WorkbenchCloseReceipt Receipt`，页面关闭失败保留attachment，不能将此ID混作设备operation |
| `WorkbenchCloseReceipt` | record `Guid AttachmentId, long Generation, bool SubscriptionDetached, CommandsDetached, PreviewResourcesReleased, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults`；不声明设备已停/Core已Disposed；页面Owner须等自身lease真实归还才IsClosed |

挂接固定顺序：验证同Dispatcher/参数/权限投影 → 为view生成attachmentId和generation → 读取不可变Core snapshot → 嵌入Host Preview.View → Subscribe元数据通知 → 有界刷新任务 → 启用允许命令；任何失败撤销本次订阅/刷新/预览借用，原Core/Host sink继续由Host所有。SnapshotItems不得持生产lease，列表选择/诊断/图表通过capture/source key/revision联动；SelectAsync失败保留最后有效图及失败状态，不取未选新帧充当成功。生产sink已收帧后的算法/导出与preview关闭互不控制。

页面命令调用§9/A.1的唯一请求形状，每次提交草稿固定revision/operationID；UI语言/主题/布局切换不得修改当前配置、token、ticket或图像源事实。权限更新使禁用原因立即可见，已发副作用以原operation对账。选帧切换generation递增并请求Release旧generation；迟到Select完成不得显示于新代次，但Preview port必须归还其独立lease。RefreshInterval/MaxVisibleRecords只约束显示，事件缺口从Core Snapshot/Query修复，不能静默Drop生产sink。

页面Close：关闭本页新命令/选帧 → generation递增 → 撤订阅和停止刷新 → 对所有旧generation的Preview请求取消等待并按attachmentId等待真实归还 → 有限返回WorkbenchCloseReceipt。已经发出的Core命令只是交给**原Host Session Owner**继续查询/Stop/Close；该Owner从创建时就在场，不依赖页面关闭另建未定义“接收者”。页面不自动Close Core、不释放grant、不重新触发；Host若因应用退出需要停止，独立调用A.1 Stop/Close并并行归还生产sink lease。Preview资源未知时attachment仍Closing，不能重挂view、清空指针或显示关闭成功；Host保留attachment与Preview port引用，继续原attachment Release观察，不反复Select。DisposeAsync按CloseBudget执行同一关闭，未知抛WorkbenchDisposalException（公开Guid AttachmentId与WorkbenchCloseReceipt Receipt，仅WPF关闭作用域），保留未关闭attachment；最终Core设备状态需Query原设备operation，不将AttachmentId查询设备ledger。

新增UI定向用例归CAM.W1.01～05：未挂接禁命令/同view二次拒绝；三语/主题切换保留revision；旧generation迟到不显示且归还；Preview返回Unknown时页面不IsClosed不重挂；Host生产sink持帧页面关闭后仍由Host并行清理。真实WPF在§10唯一1920×1080视口执行，未运行前不能据本合同宣称DevExpress/WPF/UIA通过。

### A.11 第二轮反例裁决、共享帧投影与准入结论

第二轮以“外部调用者照指导装配”和“Owner在失败后保住真实资源”两个视角复走CAM.C1.01～15及CAM.W1.01～05；这是规格自审，不是执行测试。本轮关闭逐字段意图、重启授权、摘要自引用、完整块结束通知、多预约关联、BCL Exe和UI挂接的内部说明缺口；C1已按主控接收指令同步六项规格准备；C5仍待其独立接入/运行门，不扩大C1状态。

| 第二轮反例 | 已确定的实施行为/验收定位 |
|---|---|
| Core计算ApplyOrder但Adapter整组随意写，崩溃丢失已写字段 | Core按序调用A.5 ApplyItemAsync，每项BeforeDeviceCall带Field并耐久，结果逐项commit；ReadConfigurationAsync只读当前。ApplyItem不能写其它字段；CAM.C1.02/11 |
| 相机FrameInspection只记一个allocation，但共享lease有多个plane/backing | FrameInspection以Allocations数组投影全部物理分配，Core按allocation ID去重/checked容量，leases分别计槽；CAM.C1.12 |
| 共享lease已LeaseClosed但scope还在CopyRow；另一消费者也持同storage | 只在原lease Drain=Drained才归还本capture lease槽，不等无关消费者全局StorageReleased；自身scope未知不能归零；CAM.C1.08/12 |
| Query原operation传任意ID/旧epoch，授权以显示按钮推断 | OperationQuery明确selector/token，先Authorize(Query)，再核原selector/OwnerNamespace；清理原Owner即使普通操作权限撤销仍可对账自身清理，不可查另一Owner；CAM.C1.10 |
| Callback先到、arm未确认；Stop已封口但worker晚到要交帧 | arm前只有限暂存；arm未知归还，封口后AfterSeal不再交付。ReportEnd只证明源封口不代callback排空；CAM.C1.06/08 |
| 页面关掉被误认为Core/设备已关；旧Preview显示在新选帧 | A.10 attachment代次和Preview独立归还；Host原Owner从创建一直保有Core/生产sink，不重新授Owner；CAM.W1.03～05 |
| 无subscriber、额度满或Query等待取消让Stop控制失效 | 有界事件gap/Query权威、必要清理保留控制槽、有限观察不取消后台清理；CAM.C1.09/15 |

共享CPU帧集成候选明确绑定 [image-frame §4.3](../image-frame/DEVELOPMENT-GUIDE.md#43-module-api-contract-v01进程内-copystoragelease) 的 `Asun.Modules.ImageFrame.Resources.IFrameLease`，即 `TFrame=IFrameLease`，不新造租约。相机桥接类固定 `SharedCameraFramePort`，位于 `Asun.Pcb.Modules.CameraAcquisition` 的C2集成子命名空间 `Integration`，构造 `(ICameraClock clock, CameraLimits limits)`；依赖共享Resources公开包，仅C2桥接工程引用，不让C1 Core引用该包。唯一工程候选为 `src/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Integration/Asun.Pcb.Modules.CameraAcquisition.Integration.csproj`，net10.0。Host的生产源提供已稳定独立副本给IFrameService.PublishCopyAsync，ReadAsync取得消费者IFrameLease，确认Publish/Read本操作OperationResourcesReleased后才可归还其源借用/复制源；原SDK必须在相机默认独立复制完成后已归还，不能让SDK回调等待共享发布的不可控耗时；成功storage发布持有归共享FrameService，Host按引用策略Retire自身发布持有，不将其带入相机Core。

C2映射规则：lease.Id→FrameInspection.LeaseId；lease.Allocations逐项Guid小写D/checked非负Bytes→FrameBackingCharge；布局只经已有ManagedLayoutValidator/lease.Layout验证；TryOpenReadScope→逐plane/localY CopyRow到一行有界scratch→scope.Dispose→稳定layout/metadata+紧凑实际行字节hash（不hash未定义padding）→Inspect Success。Core不调用共享内部，不将CPU row复制替代HALCON生产算法。Return调用原lease.ReleaseAsync(剩余有限观察期限)，LeaseClosed且Drain=Drained才释放本lease槽；DrainUnknown保留原lease/资源/Query，重复Release只是观察未完成归还，绝不重新Publish/Read。共有allocation还有别人持有时StorageReleased=false是合法，不能要求另一消费者退出才结束相机本operation；KnownResidentBytes仍保留诊断/Host物理总账，不等同本operation未归还槽数。直接IFrameLease.DisposeAsync按共享FrameDrainException保留原lease；成功调用之后frameport仍须以Release观察/公开事件确认Drain，不能以Dispose正常返回代替未知scope。共享Resources公开回执接收和真实Host绑定由对应Owner接收；本模块不修改共享契约。

FrameBackingCharge字段固定为 `string AllocationId, ulong CapacityBytes`。FrameInspection的 `Allocations`非空且ID唯一、Bytes正、有上界；零像素/空layout不是采集有效帧。ManagedTestFrame模拟只提供一个charge。多plane共享一个分配只出现一次，独立plane backing各列一项；源和副本短时双占分别记录。

配置摘要固定向量 CAM.C1.13-A：输入字段如下（RequestedHash排除，decimal 10.50规范为10.5）；UTF-8无BOM、无换行/空白，恰474 bytes，SHA-256=`a71b5c12ad3317b32cb6e31c7402652ea2571639c125b0ab85cd95831143fde7`。本轮用内存规范字节复算，非C#运行验证；CapabilityRevision在此仅测试标识，不是正式设备hash。

```json
{"SchemaMajor":1,"Session":{"InstanceId":"11111111-1111-1111-1111-111111111111","SessionId":"22222222-2222-2222-2222-222222222222","Epoch":"33333333-3333-3333-3333-333333333333","Selector":{"AdapterId":"sim","StableDeviceId":"cam-1"}},"CapabilityRevision":"fixture-cap-1","RequestedRevision":"fixture-cfg-1","PixelFormat":null,"Roi":{"X":0,"Y":0,"Width":4,"Height":2},"Binning":null,"Exposure":{"Mode":"Off","Microseconds":10.5},"Gain":null,"Triggers":[],"Acquisition":null}
```

字段表中hash/revision是非空不透明token；标准Hash工具实际输出64位hex，生产读回ConfirmedRevision只能由事实hash生成，不能用上述fixture标识冒硬件事实。本模块不输出邻近量化值或自动曝光数值推荐：UI只显示已核能力域/default；“使用设备默认”仅复制设备已报告合法default到草稿，仍须用户显式Apply。没有default或revision变则禁用并说明原因，不能把建议直接写生产参数。

本轮余门定位：C1内部API/Simulator/测试ports/无UIHost与工程说明已由主控按§17.2六项接收，为 `ModuleCoreImplementationReady`（规格准备）；正式可审计代码基线与实施授权仍需主控绑定。C2需Frame/设备治理Owner接收共享公开回执映射、耐久ledger及跨进程fencing/恢复的实际宿主端口；这是集成规格接收与实际绑定门，不阻C1。C3/C4需对应型号/固件/acquisition interface的触发计数/关联/停止、SDK公共调用/部署及必要重载绑定；未知设备事实拒绝其对应模式，不补猜。C5需Host实际viewport/资源/权限/主题桥接接收与真实WPF验证；C6需客户Profile的物理时序/性能/HIL/现场阈值与实际样本。未执行产品C#编译/BCL Exe、HALCON/MVS、WPF/UIA/1920×1080、真实Benchmark、HIL/FAT/SAT/生产验证；本次没有创建代码工程或样机界面。

## 20. C2-RF 线扫原行事实只读桥（ModuleCoreImplementationReady，仅规格准备）

### 20.1 范围、消费者与唯一事实边界

C2-RF 是 C2 共享帧与宿主治理桥接下的独立只读切片，真实消费者是 IM-023 mosaic C.2/C.3 连续线扫链和未来标定采样宿主。它只读取原采集 Owner 已接纳的 frame/block，不发送运动、Trigger、硬件、编码器、光源或任何采集命令；不改变 C1 的 ModuleCoreImplementationReady 接收结论。主控于2026-10-11限定接收本切片文档规格，状态为 `ModuleCoreImplementationReady`（仅规格准备）；C2设备/Frame Owner正式映射及真实运行、集成和产品资格另门。

只读桥为每个原 frame/block 提供不可变、有界、可分页的逐行事实：源 frame/block/row 身份、原始 UInt64 counter 位、epoch/boot/wrap/reset/rule revision、设备曝光 raw tick 的 start/end、clock domain/epoch/frequency、单位和不确定度、物理关联证据、实际原始行字节窗口的 hash/长度/padding/closure、arrival ordinal 和 source revision。arrival time、名义行频、帧序号、请求曝光和宿主接收顺序不能冒充设备事实。仅缺曝光时行协议仍受支持，字段为 Unknown/Partial；没有线行协议时才是 NotSupported，不返回伪造成功空页。

本切片复用本文既有 HALCON 26.05、ImageLibDotNet.cv2 公共边界和相机研究，不新增平行算法、不重复研究、不改变 C3/C4 设备资格门。

### 20.2 命名空间、公开构造和精确 API

完整命名空间固定为 Asun.Pcb.Modules.CameraAcquisition.LineFacts。SessionIdentity、CameraReply<T>、OperationBudget、ResourceSnapshot、CameraFaultReceipt、EvidenceState 和 A<T> 复用附录 A 既有类型；不复制、不扩展这些既有类型。EvidenceState 的既有值只表示字段证据：Confirmed=1、NotOccurred=2、Unknown=3、NotApplicable=4。连续性、支持性、关联性和回执结果使用本节独立状态，不能把 Failed、Proven 或 NotSupported 塞进 EvidenceState。

TFrame 只作source/payload与宿主原帧类型的消费绑定，不出现在LineFactRow事实值中。source/factory/source lease/payload port/payload lease/payload row/typed借用分支保留泛型，约束为class；不引入第二套Frame或SDK对象。ILineFactReader 是非泛型，且 CreateAsync 返回的不可变 LineFactReaderHandle 直接实现 ILineFactReader；Host 不需要把 Handle 转换成未声明的 reader。

公开 factory 是 sealed class LineFactReaderFactory<TFrame>，唯一构造为：

    LineFactReaderFactory(ILineFactSource<TFrame> source, ILineFactOwnerRecovery recovery, ILineFactRootPort root, ILineFactClock clock, ILineFactIdSource ids, LineFactLimits limits)

公开 reader/source/恢复端口签名固定为：

    ValueTask<CameraReply<LineFactReaderHandle>> ILineFactReaderFactory<TFrame>.CreateAsync(LineFactReaderRequest request, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactSnapshot>> ILineFactReader.SnapshotAsync(LineFactSnapshotRequest request, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactPage>> ILineFactReader.ReadPageAsync(LineFactPageRequest request, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactQueryResult>> ILineFactReader.QueryAsync(LineFactQuery request, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactCloseReceipt>> ILineFactReader.CloseAsync(LineFactCloseRequest request, CancellationToken cancellationToken)

    ValueTask<CameraReply<LineFactSourceLease<TFrame>>> ILineFactSource<TFrame>.OpenAsync(LineFactSourceRequest request, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactSnapshot>> ILineFactSource<TFrame>.ReadSnapshotAsync(LineFactSourceReadRequest request, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactPage>> ILineFactSource<TFrame>.ReadPageAsync(LineFactSourceReadRequest request, LineFactPageRequest page, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactQueryResult>> ILineFactSource<TFrame>.QueryAsync(LineFactSourceReadRequest request, LineFactQuery query, CancellationToken cancellationToken)
    ValueTask<CameraReply<LineFactSourceCloseReceipt>> ILineFactSource<TFrame>.CloseAsync(LineFactSourceCloseRequest request, CancellationToken cancellationToken)

    ValueTask<CameraReply<LineFactRecoveryReceipt>> ILineFactOwnerRecovery.RecoverAsync(LineFactRecoveryRequest request, CancellationToken cancellationToken)

请求和状态 record 的完整字段固定如下。LineFactOwner 是本切片新增绑定值，原附录 A 的 OwnerNamespace 仍为 string，不是本 record；可信 producer 以构造参数的既有 namespace 绑定本 OwnerId，不把 UI 输入当授权。其 JSON 键与已冻结 Owner 向量一致：

    record LineFactOwner(Guid OwnerId, Guid SessionId, Guid Epoch, CameraSelector Selector, string Scope)


    enum LineFactReadMode { FixedSnapshot=1, CurrentSource=2 }
    enum LineFactLeaseState { Open=1, Closing=2, Released=3, Unknown=4 }
    enum LineFactOperationKind { Create=1, Snapshot=2, Page=3, Query=4, Close=5, Recover=6, LedgerRead=7, PayloadOpen=8, PayloadRead=9, PayloadReturn=10, PayloadClose=11, SourceClose=12 }
    enum LineFactTaskState { Registered=1, Running=2, Pending=3, Completed=4, Failed=5, Unknown=6, Released=7 }

    record LineFactReaderRequest(LineFactOwner Owner, SessionIdentity Session, Guid CaptureOperationId, string SourceRevision, LineFactReadMode Mode, ulong MaxRows, ulong MaxTotalBytes, OperationBudget Budget)
    record LineFactSourceRequest(LineFactOwner Owner, SessionIdentity Session, Guid RootId, Guid ReaderId, Guid CaptureOperationId, string SourceRevision, LineFactReadMode Mode, OperationBudget Budget)
    record LineFactSnapshotRequest(Guid ReaderId, string ExpectedSourceRevision, OperationBudget Budget)
    record LineFactPageRequest(Guid ReaderId, ulong PageSize, ulong MaxTotalBytes, string? ContinuationToken, string ExpectedSourceRevision, OperationBudget Budget)
    record LineFactQuery(Guid ReaderId, string? SourceBlockKey, string? CounterEpochId, string? CounterRuleRevision, ulong? CounterFrom, ulong? CounterTo, ulong MaxRows, ulong MaxTotalBytes, string? ContinuationToken, string ExpectedSourceRevision, OperationBudget Budget)
    record LineFactCloseRequest(Guid ReaderId, Guid LeaseId, Guid RootId, OperationBudget Budget)
    record LineFactSourceReadRequest(Guid LeaseId, Guid ReaderId, string ExpectedSourceRevision, OperationBudget Budget)
    record LineFactSourceCloseRequest(Guid LeaseId, Guid ReaderId, Guid RootId, OperationBudget Budget)
    record LineFactRecoveryRequest(Guid RootId, Guid ReaderId, Guid? LeaseId, Guid TaskId, LineFactOwner Owner, Guid CaptureOperationId, string SourceRevision, LineFactRecoveryStage Stage, OperationBudget Budget)
    record LineFactLimits(ulong MaxPageRows, ulong MaxQueryRows, ulong MaxTotalRows, ulong MaxPageBytes, ulong MaxTotalBytes, ulong MaxTokenLifetimeTicks)
    interface ILineFactClock { string EpochId { get; } ulong FrequencyNumerator { get; } ulong FrequencyDenominator { get; } ulong NowTicks { get; } }
    interface ILineFactIdSource { Guid NextRootId(); Guid NextReaderId(); Guid NextLeaseId(); Guid NextTaskId(); }

    enum LineFactRecoveryStage { ObserveOpen=1, ObserveRead=2, ObserveSnapshot=3, ObserveQuery=4, ObserveClose=5, ReleaseSourceLease=6, ReleaseRoot=7 }

LineFactReaderRequest 必须有 CaptureOperationId、Owner/session/epoch/source revision；MaxRows、MaxTotalBytes 和预算先做 checked 有界校验。ReaderId在Create启动前由ids生成供root预登记；成功只移交Handle能力，未成功不假造Handle。Create canonical 中ReaderId仍固定null，不把随机资源身份计入Create意图hash。ExpectedSourceRevision 不是 ReaderRequest 字段，Create 时按 SourceRevision 派生；其它 read/page/query/snapshot request 必须显式带 ExpectedSourceRevision。

LineFactReaderHandle 是不可变身份和能力绑定：

    sealed class LineFactReaderHandle : ILineFactReader
    {
        public Guid ReaderId { get; }
        public Guid RootId { get; }
        public Guid LeaseId { get; }
        public LineFactOwner Owner { get; }
        public SessionIdentity Session { get; }
        public Guid CaptureOperationId { get; }
        public string SourceRevision { get; }
        public Guid SnapshotId { get; }
        public LineFactReadMode Mode { get; }
        public bool IsClosed { get; }
    }

Handle 绑定同一 LineFactOwner、Session/Epoch、CaptureOperationId、SourceRevision 和 SnapshotId；每个方法内部携带同一 binding，不能改写为当前 latest、其它 Owner 或新 epoch。IsClosed 是只读投影，不代表设备 session 已关闭。

ILineFactSource<TFrame> 的 producer 固定使用本模块新增的只读端口。公开构造为：

    LedgerBackedLineFactSource<TFrame>(ILineFactLedgerReadPort ledger, ILineFactPayloadReadPort<TFrame> payload, ILineFactRootPort root, ILineFactClock clock, ILineFactIdSource ids, LineFactLimits limits)

    interface ILineFactLedgerReadPort {
        string OwnerNamespace { get; }
        LineFactOwner Owner { get; }
        ValueTask<CameraReply<LineFactLedgerCaptureSnapshot>> ReadCaptureAsync(LineFactLedgerCaptureRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<string>> ReadCurrentRevisionAsync(LineFactLedgerCaptureRequest request, CancellationToken cancellationToken);
    }
    interface ILineFactPayloadReadPort<TFrame> where TFrame : class {
        ValueTask<CameraReply<LineFactPayloadLease<TFrame>>> OpenAsync(LineFactPayloadOpenRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactPayloadRow<TFrame>>> ReadRowAsync(LineFactPayloadReadRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactPayloadReturnReceipt>> ReturnRowAsync(LineFactPayloadReturnRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactPayloadCloseReceipt>> CloseAsync(LineFactPayloadCloseRequest request, CancellationToken cancellationToken);
    }

    record LineFactLedgerCaptureRequest(LineFactOwner Owner, SessionIdentity Session, Guid CaptureOperationId, string SourceRevision, OperationBudget Budget)
    record LineFactExpectedCounterRange(string FrameKey, string BlockKey, string EpochId, string CounterRuleRevision, ulong First, ulong Last, EvidenceState Evidence, string EvidenceId)
    record LineFactRowLocator(ulong SourceOrdinal, ulong? RowIndexInBlock)
    record LineFactLedgerBlockSnapshot(string FrameKey, string BlockKey, ulong BlockOrdinal, CounterEpoch Epoch, string CounterRuleRevision, string AssociationRuleRevision, LineFactExpectedCounterRange? ExpectedRange, bool BlockClosed, A<LineFactRowLocator> Rows)
    record LineFactLedgerCaptureSnapshot(LineFactOwner Owner, SessionIdentity Session, Guid CaptureOperationId, Guid SnapshotId, string SourceRevision, LineFactSupportState Support, string? SupportReasonCode, A<LineFactLedgerBlockSnapshot> Blocks)
    record LineFactPayloadOpenRequest(LineFactOwner Owner, SessionIdentity Session, Guid CaptureOperationId, string SourceRevision, Guid SnapshotId, OperationBudget Budget)
    record LineFactPayloadLease<TFrame>(Guid LeaseId, LineFactOwner Owner, Guid CaptureOperationId, Guid SnapshotId, string SourceRevision, ulong MaxBorrowedRows, LineFactLeaseState State) where TFrame : class
    record LineFactPayloadReadRequest(Guid LeaseId, string BlockKey, ulong SourceOrdinal, OperationBudget Budget)
    record LineFactPayloadRow<TFrame>(Guid BorrowId, ulong SourceOrdinal, string FrameKey, string BlockKey, ulong? RowIndex, ulong? ArrivalOrdinal, A<byte> FullPayload, RowByteWindow Window, PaddingSemantics Padding, DeviceCounterFact Counter, CounterEpoch Epoch, CounterTransitionEvidence? Wrap, CounterTransitionEvidence? Reset, ExposureObservation Exposure, RowAssociationEvidence Association, RowClosure Closure, string SourceRevision) where TFrame : class
    record LineFactPayloadReturnRequest(Guid LeaseId, Guid BorrowId, OperationBudget Budget)
    record LineFactPayloadReturnReceipt(Guid LeaseId, Guid BorrowId, EvidenceState Returned, ResourceSnapshot Resources)
    record LineFactPayloadCloseRequest(Guid LeaseId, LineFactOwner Owner, OperationBudget Budget)
    record LineFactPayloadCloseReceipt(Guid LeaseId, EvidenceState Released, ResourceSnapshot Resources)

Open 先在已有 Root 下登记 LedgerRead，再读同 Owner/Session/Capture/revision 的不可变 ledger snapshot；Support=NotSupported 时返回 Rejected/NoLineProtocol（带该快照），payload.Open 调用数为0。CurrentSource每次操作另登记LedgerRead调用ReadCurrentRevisionAsync，它只读Owner已有revision并返回string；与原SourceRevision不同即Rejected/RevisionChanged，不能重Open。FixedSnapshot不以current值替换旧内容。Supported 时逐块核封口与容量，再登记 PayloadOpen，取得已有载荷的只读 lease，不采集新数据。SnapshotId 来自 ledger，不由 factory 重造。读行按 ledger BlockOrdinal/SourceOrdinal 定位 payload，连接键为 Owner/Capture/SnapshotId/SourceRevision/BlockKey/SourceOrdinal，原 RowIndex/ArrivalOrdinal 可以 Unknown；不能从内存下标补设备行号。CounterRuleRevision 与 AssociationRuleRevision 分别验证，绝不互用。原始字节是稳定 A<byte> 完整载荷，仅 Window.HashCoveredRanges 按 Offset 升序串接计算 SHA-256；PayloadLength 检查完整载荷，LengthBytes 是实际 hash 覆盖长度，padding 单独验证。每行读取都登记 PayloadRead 并强持返回对象，再登记 ReturnRow；Return 未 Confirmed 前不得遗弃 BorrowId。

ledger 是期望范围、块封口、source order、capture/Owner 和两种规则修订的唯一来源；ExpectedRange 是已有封口协议证据，不是消费者设置的“期望行频”。缺行只能在同原 epoch/counter rule 的 Confirmed First..Last 内判，跨回卷范围必须两段，未知范围时 MissingRows.Value=null。RowCount 从已封口 Rows.Count 取得，不能把未知协议的空 Rows 冒零行成功。payload port 是实际完整载荷与设备逐行事实来源；无对应 SDK 行协议时源适配器明确返回 NotSupported，有行而事实缺失用 Unknown/Partial。

本切片只新增上述端口/DTO/producer；不向旧 IOperationLedger 或 ICameraFramePort 调用逐行、payload、ReadSnapshot、Page 等不存在成员，不改 C1。宿主把原 Owner 已保存的 immutable 行账和载荷接到两个新端口；真实 SDK 接线依 C3/C4 各自资格门。软件验证使用 §20.6 两 Fake 端口，并真实经过同一 LedgerBackedLineFactSource，不绕开 producer。

### 20.3 Root 强持原 Task、typed 借用与有限恢复

本节公开原语属于 ILineFactRootPort 与其返回的 LineFactTaskHandle。root 是宿主进程长期对象，由 HostOwner 强持，factory/reader 方法离栈不会 Dispose 它。全部身份在调用前由注入 ids 取得；SourceLease.LeaseId 只取实际 Open 回执，尚未移交时 LeaseId=null，不能捏造 lease。

    interface ILineFactRootPort {
        ValueTask<CameraReply<LineFactRootLease>> ReserveAsync(LineFactRootRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactTaskHandle>> RegisterTaskAsync(LineFactTaskRegistrationRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactRootLease>> ReadRootAsync(Guid rootId, LineFactOwner owner, OperationBudget budget, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactTaskHandle>> GetTaskAsync(LineFactTaskObservationRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactTaskObservation>> ObserveTaskAsync(LineFactTaskObservationRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<LineFactTaskConfirmation>> ConfirmTaskAsync(LineFactTaskConfirmationRequest request, CancellationToken cancellationToken);
        ValueTask<CameraReply<ResourceSnapshot>> ReleaseAsync(LineFactRootReleaseRequest request, CancellationToken cancellationToken);
    }
    record LineFactRootRequest(Guid RootId, Guid ReaderId, LineFactOwner Owner, Guid CaptureOperationId, string SourceRevision, ulong MaxReaders, ulong MaxTasks, ulong MaxBorrowedObjects, OperationBudget Budget)
    record LineFactRootReleaseRequest(Guid RootId, LineFactOwner Owner, OperationBudget Budget)
    record LineFactTaskRegistrationRequest(Guid RootId, Guid TaskId, Guid ReaderId, Guid? LeaseId, LineFactOwner Owner, Guid CaptureOperationId, string SourceRevision, LineFactOperationKind OperationKind, OperationBudget Budget)
    record LineFactTaskObservationRequest(Guid RootId, Guid TaskId, LineFactOwner Owner, OperationBudget Budget)
    record LineFactTaskConfirmationRequest(Guid RootId, Guid TaskId, LineFactOwner Owner, A<Guid> ReturnedBorrowIds, OperationBudget Budget)
    record LineFactTaskConfirmation(Guid TaskId, LineFactTaskState State, bool ResultAccounted, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults)
    record LineFactTaskObservation(Guid TaskId, LineFactTaskState State, bool CancellationObserved, bool DeadlineReached, bool LateResult, ResourceSnapshot Resources)

LineFactRootLease（sealed class）提供只读 RootId/ReaderId/Owner/Fence、容量、A<LineFactTaskHandle> ActiveTasks、A<LineFactBorrow> BorrowedResources 与 State。身份不可改，容量固定 MaxReaders=1、MaxTasks=8、MaxBorrowedObjects=4；其中2个 task 槽保留给 Return/Close/Recovery。任务额度不足在源调用前拒绝，必要清理不与新 read 竞争额度。

LineFactTaskHandle（sealed class）提供只读 TaskId/RootId/ReaderId/nullable LeaseId/Owner/CaptureOperationId/SourceRevision/OperationKind/State/Budget；公开下列 Attach 方法。每个 Attach 接受一个“尚未调用”的 typed start，先把 start 闭包/端口/请求/borrowed refs 强持到 root 的已登记槽，再在该槽内只调用一次，并立即强持其返回的**原 Task**。返回值就是原 Task；不得返回 WaitAsync 包装 task 当底层 task。ValueTask 只在 start 内调用一次 AsTask()；若 start 同步抛错，同一槽存 Task.FromException，闭包和 borrowed refs 仍保留。Attach 对同槽第二次调用（包括不同 operation）拒绝，不再次调用 start。

    Task<CameraReply<LineFactSourceLease<TFrame>>> AttachOpen<TFrame>(ILineFactSource<TFrame> source, Func<Task<CameraReply<LineFactSourceLease<TFrame>>>> start) where TFrame : class
    Task<CameraReply<LineFactLedgerCaptureSnapshot>> AttachLedgerRead(Func<Task<CameraReply<LineFactLedgerCaptureSnapshot>>> start)
    Task<CameraReply<string>> AttachCurrentRevision(Func<Task<CameraReply<string>>> start)
    Task<CameraReply<LineFactPayloadLease<TFrame>>> AttachPayloadOpen<TFrame>(ILineFactPayloadReadPort<TFrame> port, Func<Task<CameraReply<LineFactPayloadLease<TFrame>>>> start) where TFrame : class
    Task<CameraReply<LineFactPayloadRow<TFrame>>> AttachPayloadRead<TFrame>(ILineFactPayloadReadPort<TFrame> port, LineFactPayloadLease<TFrame> lease, Func<Task<CameraReply<LineFactPayloadRow<TFrame>>>> start) where TFrame : class
    Task<CameraReply<LineFactPayloadReturnReceipt>> AttachPayloadReturn(Func<Task<CameraReply<LineFactPayloadReturnReceipt>>> start)
    Task<CameraReply<LineFactPayloadCloseReceipt>> AttachPayloadClose(Func<Task<CameraReply<LineFactPayloadCloseReceipt>>> start)
    Task<CameraReply<LineFactSnapshot>> AttachSnapshot(Func<Task<CameraReply<LineFactSnapshot>>> start)
    Task<CameraReply<LineFactPage>> AttachPage(Func<Task<CameraReply<LineFactPage>>> start)
    Task<CameraReply<LineFactQueryResult>> AttachQuery(Func<Task<CameraReply<LineFactQueryResult>>> start)
    Task<CameraReply<LineFactSourceCloseReceipt>> AttachSourceClose(Func<Task<CameraReply<LineFactSourceCloseReceipt>>> start)
    Task<CameraReply<LineFactCloseReceipt>> AttachReaderClose(Func<Task<CameraReply<LineFactCloseReceipt>>> start)
    void TrackSource<TFrame>(ILineFactSource<TFrame> source, LineFactSourceLease<TFrame> lease) where TFrame : class
    void TrackPayload<TFrame>(ILineFactPayloadReadPort<TFrame> port, LineFactPayloadLease<TFrame> lease) where TFrame : class
    void TrackRow<TFrame>(ILineFactPayloadReadPort<TFrame> port, LineFactPayloadLease<TFrame> lease, LineFactPayloadRow<TFrame> row) where TFrame : class

类型闭合的资源分支固定为：

    abstract record LineFactBorrow(Guid BorrowId); // private protected 构造，只允许下面三分支
    sealed record LineFactSourceBorrow<TFrame>(ILineFactSource<TFrame> Source, LineFactSourceLease<TFrame> Lease) : LineFactBorrow(Lease.LeaseId) where TFrame : class
    sealed record LineFactPayloadBorrow<TFrame>(ILineFactPayloadReadPort<TFrame> Port, LineFactPayloadLease<TFrame> Lease) : LineFactBorrow(Lease.LeaseId) where TFrame : class
    sealed record LineFactRowBorrow<TFrame>(ILineFactPayloadReadPort<TFrame> Port, LineFactPayloadLease<TFrame> Lease, LineFactPayloadRow<TFrame> Row) : LineFactBorrow(Row.BorrowId) where TFrame : class

root 私有实现按上述12种typed操作分支保存确切 Task<CameraReply<T>> 和对应资源，不接受任意 object/SDK handle。即使调用者已超时且未 Track，Attach 的完成回调仍在同槽自动 Track Open/PayloadOpen/PayloadRead 的成功 Value；只读回执先保存后通知。GetTask/Observe 取得原槽，无新源调用；Recovery 使用该槽中真实 task/result/Source/Port/Lease/Row 进行必要归还，不能用一组ID重建已丢失资源。Track 同一借用 ID/同实例幂等；同 ID 不同对象拒绝并保留两者用于原 Owner 对账。

factory 构造前 HostOwner 存有 source/root/recovery/ids/clock；Create 前先 ids 取得 RootId/ReaderId/CreateTaskId，Reserve→Register(Create)→AttachOpen(source, () => source.OpenAsync(...).AsTask())。Source Open 内部 ledger/payload 子 task 复用同 root，各有固定子 TaskId；独立资源归还可用两个保留槽。读/Snapshot/Query/Close 均先 Register，再 Attach 对应 typed task。源有待归还任务时只允许原 task 的有限 Observe，不发同义操作。完成一次 read 后复制不可变事实到 page，实际 Row 已 Return Confirmed 才 ConfirmTask，task结果交付/归还轴分开；调用者输入 ReturnedBorrowIds 不是释放事实，root 还须核原 return/close 回执。

LineFactSourceLease<TFrame> 的只读字段固定为 LeaseId、RootId、ReaderId、Owner、Session、CaptureOperationId、SourceRevision、SnapshotId、Mode、State、Resources。LineFactSourceRequest 增加 RootId/ReaderId（在 Owner/Session 之后）以让 source 复用已登记根槽；LedgerBacked source 在 root 中注册实际 payload lease，SourceLease 是逻辑读 lease，不替代实际资源持有。

Observe/Recover 使用独立有限预算和取消 token，只取消等待；原 Task、closure、返回 Value、source/payload borrowed refs 保持强持。清理固定三轴：ReaderCleanup 封新读、等原 page/snapshot/query task；SourceCleanup 等原 Open/Read/ReturnTask、Return 每个原 Row，再关闭原 payload/source lease；RootCleanup 最后核所有 task 退出、结果已对账、borrowed refs 实际归还，Release root。原 business fault 和 cleanup faults 分别保留，不覆盖主故障。同步构造失败、无成功 handle、Close异常都继续上述清理。进程内 HostOwner 持有根直到 Released；恢复槽没移交确认时 HostOwner 不离场，不以ID代引用。

RecoverAsync 继续既有 LineFactRecoveryRequest，但 LeaseId 改为 Guid?：Open未知时必须允许null，不能假造。同 RootId/ReaderId/TaskId/Owner/Capture/revision 查 GetTask；Stage只可观察原分支及做必要 Return/Close。晚到 Open success 在同根被 Track 并直接关闭，不能向已封口 reader 交成功、不能重Open。Root.Release 成功须 source/payload lease 真实释放、borrow refs为空、所有原task结束且已Confirm；Expired/Unknown/NotFound不是释放证明。固定 identity 不随迟到结果更换，取得实际lease后只补该nullable字段。

Confirm成功后释放该槽的已交付纯值结果和已结束Task引用，容量可复用，但TaskId不复用；每reader仅保留最近8个确认墓碑（RootReleased墓碑到原60s期限），不堆积百万行task记录。Open/PayloadOpen的活lease转到Root.BorrowedResources继续强持，确认其Task已结束不代表lease已归还。所有当前调用和nested producer task同reader串行，MaxTasks=8包含两个保留cleanup槽；Root source/payload两个lease加至多一Row，不超MaxBorrowedObjects=4。

### 20.4 事实字段、状态和连续性

新增状态不污染附录 A 的 EvidenceState：

    enum LineFactSupportState { Supported=1, NotSupported=2 }
    enum LineFactContinuityState { Confirmed=1, Incomplete=2, OutOfOrder=3, Duplicate=4, Conflict=5, Unknown=6 }
    enum LineFactAssociationState { Confirmed=1, Uncorrelated=2, Unknown=3, Conflict=4 }
    enum RowFactAvailability { Confirmed=1, Partial=2, Unknown=3, NotSupported=4, Failed=5 }
    enum CounterEncoding { UInt64WireBits=1, UInt64LittleEndian=2, UInt64BigEndian=3 }
    enum TickEncoding { UnsignedUInt64=1, SignedInt64TwosComplement=2, OpaqueUInt64=3 }
    enum ClockDomainKind { Device=1, Encoder=2, Host=3, Unknown=255 }
    enum PaddingKind { NoPadding=1, IncludedDefined=2, ExcludedDefined=3, Unknown=4, NotSupported=5 }
    enum ClosureReason { BlockClosed=1, DeviceEnd=2, SourceClosed=3, Truncated=4, Unknown=255 }

    record DeviceCounterFact(EvidenceState Evidence, ulong? RawBits, CounterEncoding? Encoding, string? EpochId, string? RuleRevision)
    record CounterEpoch(EvidenceState Evidence, string? EpochId, string? BootId, CounterEncoding? Encoding, string? RuleRevision)
    record CounterTransitionEvidence(EvidenceState Evidence, DeviceCounterFact? Previous, DeviceCounterFact? Current, string? EpochId, string? DeviceEvidenceId)
    record ClockDomain(ClockDomainKind Kind, string DomainId, string EpochId, ulong? FrequencyNumerator, ulong? FrequencyDenominator, string Unit, EvidenceState FrequencyEvidence)
    record DeviceTick64(ulong RawBits, TickEncoding Encoding)
    record ExposureObservation(EvidenceState Availability, DeviceTick64? Start, DeviceTick64? End, ClockDomain Clock, string? PhysicalUnit, DeviceTick64? Uncertainty, string? DeviceEvidenceId)
    record ByteRange(ulong Offset, ulong Length)
    record PaddingSemantics(PaddingKind Kind, A<ByteRange> IncludedRanges, A<ByteRange> ExcludedRanges, EvidenceState Evidence)
    record RowByteWindow(ulong PayloadOffset, ulong PayloadLength, A<ByteRange> HashCoveredRanges)
    record RowBytesClosure(EvidenceState Evidence, ulong? DeclaredBytes, ulong? ObservedBytes, string? ReasonCode)
    record RawRowBytesEvidence(EvidenceState Evidence, string? HashAlgorithm, string? Hash, ulong? LengthBytes, PaddingSemantics Padding, RowByteWindow? Window, RowBytesClosure Closure, string SourceRevision)
    record RowClosure(EvidenceState Evidence, ClosureReason Reason, bool BytesComplete, bool CounterComplete, bool ExposureComplete)
    record LineFactCount(EvidenceState Evidence, ulong? Value)
    record RowAssociationEvidence(LineFactAssociationState State, string RuleRevision, string? TriggerToken, string? EncoderToken, string? PhysicalEvidenceId, AssociationScope Scope)
    enum AssociationScope { PerLine=1, PerBlock=2, PerCapture=3 }

    record LineFactRow(string SourceFrameKey, string SourceBlockKey, ulong? RowIndexInBlock, ulong? ArrivalOrdinal, DeviceCounterFact Counter, CounterEpoch Epoch, CounterTransitionEvidence? Wrap, CounterTransitionEvidence? Reset, ExposureObservation Exposure, RowAssociationEvidence Association, RawRowBytesEvidence RawBytes, RowClosure Closure, string SourceRevision, RowFactAvailability Availability, EvidenceState Integrity)

    record CounterContinuitySummary(LineFactContinuityState State, LineFactCount Blocks, LineFactCount KnownRows, LineFactCount MissingRows, LineFactCount DuplicateRows, LineFactCount OutOfOrderRows, LineFactCount ConflictRows, string RuleRevision)
    record LineFactBinding(LineFactOwner Owner, SessionIdentity Session, Guid CaptureOperationId, Guid ReaderId, Guid SnapshotId, string SourceRevision, string ClockEpochId, ulong ClockFrequencyNumerator, ulong ClockFrequencyDenominator)
    record LineFactSnapshot(LineFactBinding Binding, Guid ReaderId, Guid SnapshotId, string SourceRevision, LineFactSupportState Support, string? SupportReasonCode, LineFactCount TotalRows, LineFactCount TotalBytes, RowFactAvailability Availability, CounterContinuitySummary Continuity, bool ImmutableContent, SnapshotCurrentness Currentness, PageIntegrity Integrity, ResourceSnapshot Resources)
    enum SnapshotCurrentness { Current=1, Fixed=2, Invalidated=3 }
    record LineFactPage(LineFactBinding Binding, Guid ReaderId, Guid SnapshotId, string SourceRevision, LineFactPageRequest Request, A<LineFactRow> Rows, string? ContinuationToken, bool IsLast, PageIntegrity Integrity, ResourceSnapshot Resources)
    record LineFactQueryResult(LineFactBinding Binding, Guid ReaderId, Guid SnapshotId, string SourceRevision, LineFactQuery Query, A<LineFactRow> Rows, string? ContinuationToken, QueryIntegrity Integrity, ResourceSnapshot Resources)
    record PageIntegrity(EvidenceState Evidence, bool DetailsTruncated, string? FailureCode, string CanonicalSha256)
    record QueryIntegrity(EvidenceState Evidence, bool DetailsTruncated, string? FailureCode, string CanonicalSha256)
    record LineFactSourceCloseReceipt(Guid LeaseId, bool SourceLeaseReleased, LineFactLeaseState State, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults)
    record LineFactCloseReceipt(Guid ReaderId, Guid LeaseId, Guid RootId, bool ReaderClosed, bool SourceLeaseReleased, LineFactLeaseState State, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults)
    record LineFactRecoveryReceipt(Guid RootId, Guid ReaderId, Guid? LeaseId, Guid TaskId, LineFactRecoveryStage Stage, bool Progressed, bool SourceLeaseReleased, bool RootReleased, ResourceSnapshot Resources, A<CameraFaultReceipt> Faults)

EvidenceState=Unknown 时对应 nullable 值必须为 null；未知计数用 LineFactCount(Evidence=Unknown, Value=null)，绝不使用 0。Raw bytes/hash/length/padding 未知时 RawRowBytesEvidence.Evidence=Unknown、HashAlgorithm/Hash/LengthBytes/Window=null、Padding.Kind=Unknown、Closure 数值为 null；不生成未知 hash。仅缺曝光时 Exposure.Availability=Unknown，LineFactRow.Availability=Partial；没有 row identity/counter protocol 时 Support=NotSupported、RowFactAvailability=NotSupported，并且不返回 TotalRows=0 的成功结果。

UInt64 RawBits 只能按 CounterEncoding 无损解码为八字节位模式，禁止先转 Int64、double 或 decimal。wrap/reset 必须各有公开 CounterTransitionEvidence，保留 Previous/Current 原位和 EpochId。相同 counter 只有在 SourceRevision、SourceFrameKey、SourceBlockKey、EpochId、Counter.RuleRevision、Association.RuleRevision 都相同而 RawBytes.Hash 不同才是 Conflict；不同 epoch、rule 或 source 不得互相计 Duplicate/Conflict。跨 wrap 查询必须按 epoch/rule 分段。

### 20.5 Snapshot、实际正文哈希与稳定分页 token

FixedSnapshot 固定 Content revision，后续 source 发布新 revision 不改变它；CurrentSource 每次 read 先核 current revision，变化返回 Rejected/RevisionChanged，不跨 revision 拼接。显式 Owner 撤销旧快照时两种模式均 Invalidated；原lease/Task只清理不能消失。

LineFactLimits 的软件上限为 (MaxPageRows=4096, MaxQueryRows=1000000, MaxTotalRows=1000000, MaxPageBytes=16777216, MaxTotalBytes=1073741824, MaxTokenLifetimeTicks=60000000000)。Root在每个reader另预留重放缓存 MaxCachedPages=8、MaxCachedBytes=33554432，计入请求 MaxTotalBytes 和Root物理账。PageSize=1..4096；MaxRows=1..1000000；byte限制按行完整payload与canonical实际bytes的较大者收费，所有加乘checked。即将输出的完整页超过MaxPageBytes时不切断行，返回Partial/LimitReached；无剩余预算时返回Rejected/LimitReached，不能伪 IsLast。缓存额度不足在该页读源及CAS前返回Rejected/ReplayCacheFull，原游标不变。

ILineFactClock.NowTicks 为同epoch的1ns UInt64 tick，FrequencyNumerator=1000000000/Denominator=1。TimeSpan预算为100ns tick，转换clock期限需checked(Budget.Total.Ticks*100)，队列期限同理；token expiry=min(reader创建截止、NowTicks+60000000000)。ClockEpochId变化或NowTicks倒退即拒绝原token并保留资源恢复；不把跨重启monotonic值继续计期限。

LineFactCanonicalJsonWriter 只有下面这些明确入口，均为纯值 UTF-8 byte[]，不输出运行对象。所有值先验证，非法UTF16 surrogate拒绝；固定键顺序按下面各projection列表，不声称“与DTO声明顺序相同”。非ASCII直接原UTF8（U+2028/2029也不转义），不做normalization；slash不转义；quote/backslash分别为 \"、\\；U+0000..001F一律小写 \u00xx（换行也不用 \n），布尔小写，整数十进制无前导零/指数，Guid小写D，byte/hex/hash小写，enum按本节固定名称，null键显式，A<T>.IsDefault拒绝。嵌套Rows逐项用Row的**正文字段**，不嵌套CanonicalVersion/ProjectionKind头。

    static byte[] WriteReaderRequest(LineFactReaderRequest value)
    static byte[] WritePageRequest(LineFactPageRequest value)
    static byte[] WriteQuery(LineFactQuery value)
    static byte[] WriteSnapshot(LineFactSnapshot value)
    static byte[] WriteRow(LineFactRow value)
    static byte[] WritePage(LineFactPage value)
    static byte[] WriteQueryResult(LineFactQueryResult value)
    static byte[] WritePageIntent(LineFactBinding binding, LineFactPageRequest request)
    static byte[] WriteQueryIntent(LineFactBinding binding, LineFactQuery request)

CanonicalVersion全部为line-fact/v0.1，ProjectionKind分别为ReaderRequest/PageRequest/Query/Snapshot/Row/Page/QueryResult/PageIntent/QueryIntent。字段投影固定如下（头中派生值不能被调用者覆盖）：

| projection | 头后精确字段顺序 |
|---|---|
| ReaderRequest | ReaderId=null、Owner、Session、CaptureOperationId、SourceRevision、Mode、MaxRows、MaxTotalBytes、BudgetTicks=Budget.Total.Ticks、BudgetQueueTicks=Budget.Queue.Ticks、ExpectedSourceRevision=SourceRevision |
| PageRequest | ReaderId、ExpectedSourceRevision、PageSize、MaxTotalBytes、ContinuationToken、BudgetTicks、BudgetQueueTicks |
| Query | ReaderId、ExpectedSourceRevision、SourceBlockKey、CounterEpochId、CounterRuleRevision、CounterFrom、CounterTo、MaxRows、MaxTotalBytes、ContinuationToken、BudgetTicks、BudgetQueueTicks |
| PageIntent | Owner、Session、CaptureOperationId、ReaderId、SnapshotId、SourceRevision、ExpectedSourceRevision、PageSize、MaxTotalBytes、ClockEpochId、ClockFrequencyNumerator、ClockFrequencyDenominator |
| QueryIntent | Owner、Session、CaptureOperationId、ReaderId、SnapshotId、SourceRevision、ExpectedSourceRevision、SourceBlockKey、CounterEpochId、CounterRuleRevision、CounterFrom、CounterTo、MaxRows、MaxTotalBytes、ClockEpochId、ClockFrequencyNumerator、ClockFrequencyDenominator |
| Snapshot | Owner、Session、CaptureOperationId（来自Binding）、ReaderId、SnapshotId、SourceRevision、Support、SupportReasonCode、TotalRows、TotalBytes、Availability、Continuity、ImmutableContent、Currentness、Resources、Integrity |
| Page | ReaderId、SnapshotId、SourceRevision、PageIntent、Rows、IsLast、Resources、Integrity |
| QueryResult | ReaderId、SnapshotId、SourceRevision、QueryIntent、Rows、Resources、Integrity |
| Row | SourceFrameKey、SourceBlockKey、RowIndexInBlock、ArrivalOrdinal、Counter、Epoch、Wrap、Reset、Exposure、Association、RawBytes、Closure、SourceRevision、Availability、Integrity |

Binding与顶层ReaderId/SnapshotId/SourceRevision、request ExpectedSourceRevision必须全等，否则拒绝编码。Intent从Binding和真实request上述字段派生，排除ContinuationToken、CAS cursor、到期值、nonce及等待预算；不同页可用剩余预算而不改变QueryHash。实际Page/QueryResult正文必须编码真实Rows和原来源，不能用WritePageRequest/WriteQuery的意图hash充当正文hash。ContinuationToken是授权/游标运输字段，不进入Page/QueryResult正文hash；分页内容由真实Rows体现。不同页Rows变更会改变正文hash。

所有复用嵌套类型精确映射：Owner是本节LineFactOwner按OwnerId、SessionId、Epoch、Selector、Scope；原OwnerNamespace是string，不复制原契约；Session按附录A的InstanceId、SessionId、Epoch、Selector；Selector按AdapterId、StableDeviceId。Resources按附录A顺序CaptureOperationId、Callbacks、Workers、DriverBuffers、InternalFrames、DeliveredLeases、TemporaryResources、KnownResidentBytes、CountsComplete、DeviceStopped、ObservedAt，其中ObservedAt规范值固定0（运行回执仍保真）；其余计数与CountsComplete原样，不把未知补0。Continuity按State、Blocks、KnownRows、MissingRows、DuplicateRows、OutOfOrderRows、ConflictRows、RuleRevision；LineFactCount按Evidence、Value。事实嵌套record按§20.4逐字段顺序，Integrity按Evidence、DetailsTruncated、FailureCode、CanonicalSha256=null。

Snapshot/Page/QueryResult的自身Integrity.CanonicalSha256在所有哈希预像中固定null，SHA256计算完成后才写实际回执；Write方法即使输入已含hash也仍投影null，校验等式不会自引用。RawBytes.Hash是实际行窗口独立hash，属于正文，不排除；Row.Integrity为EvidenceState而无self-hash。Hash算法全部SHA-256，输出64字符小写hex。

Source排序来自ledger Blocks.BlockOrdinal、Rows.SourceOrdinal，均唯一且在快照内不可变；不能由frame key字典序猜顺序。每行原ArrivalOrdinal独立留存；OutOfOrder按同epoch/counter rule中原ArrivalOrdinal检查下降，排序分页不抹去乱序。CounterFrom/To仅作同epoch/rule的闭区间raw UInt64过滤：两者同有或同null，from<=to；有范围必须显式CounterEpochId/CounterRuleRevision，未填返回Rejected/CounterDomainRequired。reader可含多个epoch，但指定域只返回该域；不能用RawBits横跨域，跨wrap必须在各域/transition的非回卷区间拆请求。无范围时两domain可null以列全部行，Continuity仍逐域分段；未知RawBits不计作范围命中，Query返回Partial/UnknownCounter，不SilentDrop。

token固定177 bytes。offset/length固定为Version[0,1)、ReaderId[1,17)、SourceRevisionSha256[17,49)、QueryHash[49,81)、SortKeyHash[81,113)、LastOrdinal[113,121)、ExpiryMonotonicTicks[121,129)、Nonce[129,145)、MAC[145,177)。Guid16按RFC4122显示串去“-”后逐hex pair，即00112233-4455-6677-8899-aabbccddeeff编码00112233445566778899aabbccddeeff，不能用默认Guid.ToByteArray小端。两个UInt64大端；SourceRevisionSha256=SHA256(原revision UTF8)；QueryHash=SHA256(WritePageIntent或WriteQueryIntent完整字节)；MAC=HMAC-SHA256(key, bytes[0:145])。token无padding Base64Url，长度236字符，解码必须177，拒绝非canonical编码。

SortKeyHash完整预像由相同writer的JSON值规则产生：{"CanonicalVersion":"line-fact/v0.1","ProjectionKind":"SortKey","SnapshotId":<原GuidD>,"SourceRevision":<原string>,"BlockOrder":"LedgerBlockOrdinalAscending","RowOrder":"LedgerSourceOrdinalAscending","UnknownRowIndex":"KeepSourceOrdinal","ArrivalOrder":"PreserveFactOnly"}。不能用未定义“规则hash”。Root构造时生产使用RandomNumberGenerator.GetBytes(32)生成每root私有key，并为每签发token用GetBytes(16) nonce；保留到该root真实Released，不暴露在业务日志。SyntheticRoot显式注入固定测试key/nonce，只限测试，不能成为生产默认。

CAS状态是root私有的(ReaderId,QueryHash,LastOrdinal,Expiry,cacheEntry)。首请求token=null且从0开始；token LastOrdinal 是**已返回行数/下个匹配行下标**。首次消费有效token先预留缓存，再读一完整页、归还Row后，原子CAS把游标从token LastOrdinal推进至next ordinal，并同一事务存输入token全文→不可变原Page/QueryResult与输出token。失败/CAS失配归还本次源借用，不发布新页。只有同输入token、相同intent/Owner才允许重放原缓存回执（原Resources也保持原值，当前资源另Observe），不得再次read或再CAS。CAS冲突且不是缓存重放返回Rejected/TokenConflict。

缓存8页/32MiB且消耗请求MaxTotalBytes，满时不逐出未过期页，不前进游标；期限就是输入token expiry，同clock epoch且NowTicks<expiry可重放。Close封读、Owner撤销、clock epoch变化或expiry到期立即禁止重放；缓存只在无原task引用且实际borrow已归还后释放，根未释放不能假装资源0。第一页无输入token不享受token重放；要重读第一页显式新reader，绝不自动重Open。缓存哈希/页内容不含随机输出token，减少授权物变化对正文hash的影响。

### 20.6 双 Synthetic Host 的固定 typed 输入与完整接线

两个 Host 均用 §20.2 的真实 LedgerBackedLineFactSource<SyntheticFrame>，不使用绕开producer的SyntheticLineFactSource。私有fixture只实现新只读端口，公开构造/接口如下：

    sealed class SyntheticFrame { } // TFrame绑定占位，不包含设备/运行对象
    sealed class SyntheticLedger : ILineFactLedgerReadPort
    SyntheticLedger(string ownerNamespace, LineFactLedgerCaptureSnapshot snapshot)
    sealed class SyntheticPayload : ILineFactPayloadReadPort<SyntheticFrame>
    SyntheticPayload(LineFactOwner owner, Guid captureId, Guid snapshotId, string revision, Guid leaseId, A<LineFactPayloadRow<SyntheticFrame>> rows, LineFactLimits limits)
    sealed class SyntheticIds : ILineFactIdSource
    SyntheticIds(Guid rootId, Guid readerId, Guid firstTaskId)
    sealed class SyntheticRoot : ILineFactRootPort
    SyntheticRoot(LineFactOwner owner, ILineFactClock clock, A<byte> tokenKey, A<byte> nonceStart, LineFactLimits limits)
    sealed class SyntheticRecovery : ILineFactOwnerRecovery
    SyntheticRecovery(ILineFactRootPort root)
    sealed class SyntheticClock : ILineFactClock
    SyntheticClock(string epochId, ulong frequencyNumerator, ulong frequencyDenominator, ulong nowTicks)
    void SyntheticClock.AdvanceChecked(ulong nanoseconds) // 私有锁下checked推进，仅测试手动闩锁使用

SyntheticLedger仅接受构造绑定Owner/Session/Capture/revision，ReadCapture返回同一immutable snapshot，ReadCurrentRevision返回构造revision（revision变体显式发布新current但仍保留旧snapshot）；不伪造协议。SyntheticPayload按BlockKey/SourceOrdinal精确定位行，完整载荷A<byte>深拷贝一次并冻结；同一BorrowId同时借用二次拒绝。ReturnRow成功确认该BorrowId实际归还，Close须等待所有Rows归还再Released=Confirmed；注入读/关闩锁时Task保留、计数不归零。每个fixture有自己的typed状态表，无静态全局。SyntheticIds实际传factory和producer：NextRootId/NextReaderId返回构造值一次，再调用拒绝；NextTaskId从firstTaskId的RFC4122 bytes最后8 bytes作为UInt64大端起始序号，首次返回firstTaskId，随后checked+1，前8 bytes固定，返回Guid显示串；NextLeaseId只在生产source需要新逻辑读lease时按同样序号+1，实际payload lease仍由SyntheticPayload回执取得。SnapshotId总是ledger snapshot的值。SyntheticRoot先验证Key=32、Nonce=16、owner，私有保存深拷贝；测试nonce每次签发按16byte大端+1，溢出拒绝。SyntheticClock软件fixture通过闩锁AdvanceChecked(ulong nanoseconds)显式推进NowTicks；真实10/120/180s外层仍采用真实单调clock，不能用fixture时间证明执行期限。

B/X共用limits=(4096,1000000,1000000,16777216,1073741824,60000000000)，每request预算 new OperationBudget(TimeSpan.FromTicks(100000000),TimeSpan.FromTicks(10000000))；这是10s/1s纯软件fixture预算。close/recovery各建独立取消token和同形预算，全部观察截止取min(case真实起点+10s, suite120s剩余)，绝不因finally新增10s重置case。cleanup任务继续由长期Root持有，超过suite必需项未完成则外层非零。

固定身份全部如下（LineFactOwner.Scope="LineFacts"；Selector按AdapterId,StableDeviceId；Owner中的SessionId/Epoch与Session全等）：

| 字段 | Host-B | Host-X |
|---|---|---|
| OwnerId | aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa | eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee |
| InstanceId | 99999999-9999-9999-9999-999999999999 | 88888888-8888-8888-8888-888888888888 |
| SessionId | bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb | ffffffff-ffff-ffff-ffff-ffffffffffff |
| Epoch | cccccccc-cccc-cccc-cccc-cccccccccccc | 11111111-2222-3333-4444-555555555555 |
| Selector | ("synthetic","line-b") | ("synthetic","line-x") |
| CaptureOperationId | dddddddd-dddd-dddd-dddd-dddddddddddd | 66666666-7777-8888-9999-aaaaaaaaaaaa |
| Ledger OwnerNamespace | cam/synthetic/line-b | cam/synthetic/line-x |
| SourceRevision | rev-b-1 | rev-x-1 |
| SnapshotId | 03030303-0303-0303-0303-030303030303 | 13131313-1313-1313-1313-131313131313 |
| RootId | 01010101-0101-0101-0101-010101010101 | 11111111-1111-1111-1111-111111111111 |
| ReaderId | 02020202-0202-0202-0202-020202020202 | 12121212-1212-1212-1212-121212121212 |
| PayloadLeaseId | 04040404-0404-0404-0404-040404040404 | 14141414-1414-1414-1414-141414141414 |
| firstTaskId | 05050505-0505-0505-0000-000000000001 | 15151515-1515-1515-0000-000000000001 |
| Host Clock | ("clock-b-1",1000000000,1,1000000) | ("clock-x-1",1000000000,1,1000000) |
| Counter epoch/boot | boot-b-1 / boot-b-1 | boot-x-1 / boot-x-1 |
| CounterRuleRevision | counter-b-1 | counter-x-1 |
| AssociationRuleRevision | assoc-b-1 | assoc-x-1 |
| key hex（仅Synthetic） | 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f | 202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f |
| first nonce hex | 000102030405060708090a0b0c0d0e0f | 101112131415161718191a1b1c1d1e1f |

Host-B一个frame/block，ledger FrameKey=frame-b-0、BlockKey=block-b-0、BlockOrdinal=0，Rows locators=[(SourceOrdinal=0,RowIndex=0),(1,1),(2,2),(3,3)]，BlockClosed=true、ExpectedRange=null；因此MissingRows=Unknown/null，不能以100→MaxUInt64跨度造巨大缺行。Host-X FrameKey=frame-x-0，block-A/BlockOrdinal=0/Rows[(0,0),(1,1)]，block-B/BlockOrdinal=1/Rows[(0,0),(1,1)]，两block均封口。ExpectedRange分别为 new LineFactExpectedCounterRange("frame-x-0","block-A","boot-x-1","counter-x-1",100,101,Confirmed,"range-x-A") 与 new LineFactExpectedCounterRange("frame-x-0","block-B","boot-x-1","counter-x-1",102,103,Confirmed,"range-x-B")，来源是SyntheticLedger的预置完整封口协议证据。缺103时block-B Rows仅[(0,0)]，ExpectedRange仍102..103，MissingRows才可确定1；不能由收到行的max逆推期望尾端。

八行完整实际bytes和身份如下；BorrowId从所在Host PayloadLeaseId的RFC4122 bytes最后一byte按0x21+i替换（B为...0421/...0422/...0423/...0424；X为...1421/...1422/...1423/...1424，GuidD），与source/payload lease身份分离。每条LineFactPayloadRow.SourceRevision从上表复制，SourceOrdinal是块内定位，不是counter。不从hash/ordinal反造payload。

| Host/i | Block/RowIndex/SourceOrdinal | ArrivalOrdinal | Counter.RawBits | FullPayload hex |
|---|---|---|---|---|
| B/0 | block-b-0/0/0 | 0 | 100 | 00010203aabb |
| B/1 | block-b-0/1/1 | 1 | 101 | 10111213aabb |
| B/2 | block-b-0/2/2 | 2 | 102 | 20212223aabb |
| B/3 | block-b-0/3/3 | 3 | 18446744073709551615 | ff00ff00aabb |
| X/0 | block-A/0/0 | 0 | 100 | 00010203aabb |
| X/1 | block-A/1/1 | 1 | 101 | 10111213aabb |
| X/2 | block-B/0/0 | 2 | 102 | 20212223aabb |
| X/3 | block-B/1/1 | 3 | 103 | 30313233aabb |

每行其它全部typed字段固定：Counter=new DeviceCounterFact(Confirmed,表内RawBits,UInt64WireBits,表内counter epoch,表内CounterRuleRevision)；Epoch=new CounterEpoch(Confirmed,epoch,boot,UInt64WireBits,CounterRuleRevision)。Wrap与Reset均 new CounterTransitionEvidence(NotOccurred,null,null,epoch,null)，Synthetic仅声明本fixture未发生transition，不证明真实设备。Window=new RowByteWindow(0,6,[new ByteRange(0,4)])；Padding=new PaddingSemantics(ExcludedDefined,[],[new ByteRange(4,2)],Confirmed)；Closure=new RowClosure(Confirmed,BlockClosed,true,true,false)。Exposure=new ExposureObservation(Unknown,null,null,new ClockDomain(Device,"cam-clock-b"/"cam-clock-x",counter epoch,1000000000,1,"tick",Confirmed),"us",null,null)。Association=new RowAssociationEvidence(Confirmed,AssociationRuleRevision,"trig-b-i"/"trig-x-i","enc-b-i"/"enc-x-i","phys-b-i"/"phys-x-i",PerLine)，i取行表序号（数字十进制）；绝不把AssociationRuleRevision写到Counter.Epoch.RuleRevision。

producer投影RawBytes=(Confirmed,"SHA-256",SHA256(FullPayload[0:4]),4,Padding,Window,new RowBytesClosure(Confirmed,4,4,"row-closed"),SourceRevision)，LineFactRow.Availability=Partial、Integrity=Confirmed；Canonical已冻结的B/3完全匹配§20.7行向量。各4byte hash由§20.7固定字节表给出；无padding参与，原六byte完整payload仍由borrow持有。RowBytesClosure的4只指hash window闭包，不替代payload6容量账。

两个Host从空组合根按完全相同顺序装配，参数分别代入上表实际值：

    clock = new SyntheticClock(clockEpoch,1000000000,1,1000000);
    ids = new SyntheticIds(rootId,readerId,firstTaskId);
    root = new SyntheticRoot(owner,clock,key32,nonce16,limits);
    recovery = new SyntheticRecovery(root);
    ledger = new SyntheticLedger(ownerNamespace, new LineFactLedgerCaptureSnapshot(owner,session,captureId,snapshotId,revision,Supported,null,blocks));
    payload = new SyntheticPayload(owner,captureId,snapshotId,revision,payloadLeaseId,rows,limits);
    source = new LedgerBackedLineFactSource<SyntheticFrame>(ledger,payload,root,clock,ids,limits);
    factory = new LineFactReaderFactory<SyntheticFrame>(source,recovery,root,clock,ids,limits);

blocks/rows是上表逐字段构造的immutable A<T>，无BuildFixture/helper。ids确实注入factory和producer，Host可在调用前保存构造给ids的RootId/ReaderId；不再次Next消耗ID。HostOwner在构造factory前强持所有组合根，并在Create调用前存 operationAttempted=true，handle初值null，businessFault/cleanupFaults独立保存。source/factory均不Dispose宿主端口。B与X Create均 (owner,session,captureId,revision,FixedSnapshot,4,65536,budget)；source中的原Open Task由root AttachOpen强持，即使Create回执丢失也能从ReadRoot原Root找回。

成功Create后handle.Value才能调用 SnapshotAsync(new LineFactSnapshotRequest(readerId,revision,budget))。B pageRequest=new LineFactPageRequest(readerId,2,65536,null,revision,budget)，X pageRequest=(readerId,3,65536,null,revision,budget)；第二页只把ContinuationToken换为第一页返回值，ExpectedSourceRevision/PageSize/MaxTotalBytes原值保持，等待budget可用剩余值。B两页2/2，X两页3/1，最后一页IsLast=true。B Query=new LineFactQuery(readerId,"block-b-0","boot-b-1","counter-b-1",100,18446744073709551615,4,65536,null,revision,budget)，X Query=(readerId,null,"boot-x-1","counter-x-1",100,103,8,65536,null,revision,budget)。源过滤前核同counter域，4行全部命中且原arrival留存；QueryRows与page原行事实一致。Snapshot TotalRows=4、TotalBytes=24（6byte完整payload*4）；KnownRows=4，X Missing/Duplicate/OutOfOrder/Conflict=0，B Missing=Unknown。返回的计数都使用LineFactCount而非裸ulong；正常SourceLeaseReleased/RootReleased是回执bool=true，不写作EvidenceState.Confirmed。

完整收尾与迟到恢复顺序：

    try {
        // Create → Snapshot → Page1 → Page2 → Query，上述准确request顺序。
        // 每一步保存原Task（Host层异步调用只AsTask一次），root内部已强持真正source task。
    } catch (Exception fault) { businessFault=fault; }
    finally {
        try {
            if (handle != null)
                await handle.CloseAsync(new LineFactCloseRequest(readerId,handle.LeaseId,rootId,closeBudget),closeToken);
            // Close异常或Pending只加cleanupFault，不跳到Root释放。
        } catch (Exception fault) { cleanupFaults.Add(fault); }
        finally {
            // 无handle也执行，原RootId/ReaderId从Create前已保存。
            // ReadRootAsync(rootId,owner,recoveryBudget,recoveryToken)取得真实ActiveTasks/borrow refs。
            // 每个原task GetTask→ObserveTask，按该原task OperationKind选ObserveOpen/Read/Snapshot/Query/Close。
            // RecoverAsync(new LineFactRecoveryRequest(rootId,readerId,actualLeaseIdOrNull,taskId,
            //     owner,captureId,revision,stage,recoveryBudget),recoveryToken) 只观察同槽。
            // 原read结果先归还Row；Open晚到Value被Root自动Track后继续ReleaseSourceLease。
            // source/payload Close完成、全部原Task退出/Confirm后，最后Recover(Stage=ReleaseRoot)。
        }
    }

ReadRoot NotFound只在Reserve未接纳且无源调用记录时可视为无本次root；Otherwise保留Unknown和HostOwner。Recovery调用抛错也留根及原Task，不能用finally异常覆盖businessFault。Close自身的AttachReaderClose/SourceClose/ReturnTask不等自己退出；Close等此前业务task，返回资源回执后RootCleanup由Host外层Recover触发，避免等待自身Task造成死锁。Root已成功Released后不重复源Close，重复Recover只返回保留的释放墓碑（reader身份相同）。测试注入 late Open/Read/Close：关闭闩锁→观察有限Pending→用ReadRoot确认原Task/Borrow refs非空→释放同闩锁→Observe/Recover同task→每个借用恰好归还一次→Root最终Released，Open计数始终1。闩锁未解除则suite非零且HostOwner仍持有根，不能归零或声称完成。

X反例只改明确一处输入，所有typed来源同步：
- 缺103：上文已封口ExpectedRange保留，Rows删X/3，Missing=1/Incomplete。
- Duplicate：新增X/2复制事实、不同BorrowId/SourceOrdinal=2/ArrivalOrdinal=4、同Block/RowIndex/RawBits/CounterRule/hash，Duplicate=1；原Rows3 locator和容量同步。
- 乱序：X/2 ArrivalOrdinal=3，X/3 ArrivalOrdinal=2（原到达100,101,103,102），分页source order仍100,101,102,103，OutOfOrder=1/OutOfOrder；counter/association规则不变。
- Conflict：增加第二条Block-B/RowIndex0/RawBits102、相同CounterRule与AssociationRule，Payload=21212223aabb，独立BorrowId/SourceOrdinal2/Arrival4，hash变化，Conflict=1（Duplicate=0）。若CounterRule改为counter-x-2并在ledger明确分段，则不计Conflict/Duplicate，Continuity=Unknown；只改AssociationRule成assoc-x-2也不得假装same physical rule conflict，关联分段/Unknown单独记录。
- epoch变化：X/2,X/3 Counter/Epoch/Wrap/Reset改boot-x-2，ledger block-B/range也改同epoch；不合并两域。旧X query显式boot-x-1只返回100/101，新query boot-x-2返回102/103，CounterEpochId=null但from/to非null时Rejected/CounterDomainRequired。
- revision变化：发布另rev-x-2 ledger/payload（各来源一致），旧FixedSnapshot继续rev-x-1；CurrentSource旧reader Rejected/RevisionChanged。单行revision与ledger不等为Rejected/SourceRevisionMismatch，不能混进旧快照。
- Area/无行协议：ledger Support=NotSupported，SupportReasonCode=NoLineProtocol，payload.Open=0、Rows不伪成功；仅未知Exposure或Counter则Supported，逐字段Unknown/Partial。

### 20.7 Canonical fixture vectors、测试和预算

CanonicalVersion 固定为 line-fact/v0.1。以下三组向量必须由 LineFactCanonicalJsonWriter 逐字节复算；request 不含 ReaderId/ExpectedSourceRevision，向量中分别使用 null 和由 SourceRevision 派生的值。REQUEST_JSON、ROW_JSON、UNKNOWN_ROW_JSON 及其 UTF8_LENGTH/UTF8_HEX/SHA256 均保留在本节的 fixture 行中，不能再增加 hash256 标签或第二个 hash 字段。MaxUInt64 行使用 Host-B 的完整六字节 payload、四字节 hash window 和 [4,6) padding exclusion；Unknown 行的 raw hash、length、window、padding ranges 全为 null/Unknown 形状。

测试沿用 C1 的真实单调 10s 每 case、120s suite、180s 外层进程边界；本节只冻结软件验证，Benchmark 结果为 NotEvaluated。CAM.RF.01 分页 token/CAS/固定 snapshot；CAM.RF.02 ExpectedRange 缺行、arrival out-of-order、同 counter hash conflict、rule/epoch/revision 分段；CAM.RF.03 曝光 Unknown 与仅无行协议 NotSupported；CAM.RF.04 UInt64 0/1/Max、wrap/reset 原位证据、padding window/hash；CAM.RF.05 Owner/session/capture/revision 越界；CAM.RF.06 root 长期 task、取消/超时/双 cleanup/late recovery；CAM.RF.07 两 Host reader/root/task/hash 隔离；CAM.RF.08 1000 行、页/总 byte 上限和 Partial 截断；CAM.RF.09 唯一 JSON writer 的 non-ASCII、slash、control、hex 大小写；CAM.RF.10 source ledger task/lease 未释放时 Root 不得 Released。任何未完成/跳过 case 非零。


Canonical fixture 的实际输入如下（每行 JSON 均为单行 UTF-8）：

    REQUEST_JSON = {"CanonicalVersion":"line-fact/v0.1","ProjectionKind":"ReaderRequest","ReaderId":null,"Owner":{"OwnerId":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","SessionId":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","Epoch":"cccccccc-cccc-cccc-cccc-cccccccccccc","Selector":{"AdapterId":"synthetic","StableDeviceId":"line-b"},"Scope":"LineFacts"},"Session":{"InstanceId":"99999999-9999-9999-9999-999999999999","SessionId":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","Epoch":"cccccccc-cccc-cccc-cccc-cccccccccccc","Selector":{"AdapterId":"synthetic","StableDeviceId":"line-b"}},"CaptureOperationId":"dddddddd-dddd-dddd-dddd-dddddddddddd","SourceRevision":"rev-b-1","Mode":"FixedSnapshot","MaxRows":4,"MaxTotalBytes":65536,"BudgetTicks":100000000,"BudgetQueueTicks":10000000,"ExpectedSourceRevision":"rev-b-1"}
    REQUEST_UTF8_LENGTH = 782
    REQUEST_UTF8_HEX = 7b2243616e6f6e6963616c56657273696f6e223a226c696e652d666163742f76302e31222c2250726f6a656374696f6e4b696e64223a2252656164657252657175657374222c225265616465724964223a6e756c6c2c224f776e6572223a7b224f776e65724964223a2261616161616161612d616161612d616161612d616161612d616161616161616161616161222c2253657373696f6e4964223a2262626262626262622d626262622d626262622d626262622d626262626262626262626262222c2245706f6368223a2263636363636363632d636363632d636363632d636363632d636363636363636363636363222c2253656c6563746f72223a7b22416461707465724964223a2273796e746865746963222c22537461626c654465766963654964223a226c696e652d62227d2c2253636f7065223a224c696e654661637473227d2c2253657373696f6e223a7b22496e7374616e63654964223a2239393939393939392d393939392d393939392d393939392d393939393939393939393939222c2253657373696f6e4964223a2262626262626262622d626262622d626262622d626262622d626262626262626262626262222c2245706f6368223a2263636363636363632d636363632d636363632d636363632d636363636363636363636363222c2253656c6563746f72223a7b22416461707465724964223a2273796e746865746963222c22537461626c654465766963654964223a226c696e652d62227d7d2c22436170747572654f7065726174696f6e4964223a2264646464646464642d646464642d646464642d646464642d646464646464646464646464222c22536f757263655265766973696f6e223a227265762d622d31222c224d6f6465223a224669786564536e617073686f74222c224d6178526f7773223a342c224d6178546f74616c4279746573223a36353533362c224275646765745469636b73223a3130303030303030302c2242756467657451756575655469636b73223a31303030303030302c224578706563746564536f757263655265766973696f6e223a227265762d622d31227d
    REQUEST_SHA256 = 1c4a8bebe1d70a1f6dafb8b318e2b3d9a9b1f1e3043c91f553121e6a103b27b5

    ROW_JSON = {"CanonicalVersion":"line-fact/v0.1","ProjectionKind":"Row","SourceFrameKey":"frame-b-0","SourceBlockKey":"block-b-0","RowIndexInBlock":3,"ArrivalOrdinal":3,"Counter":{"Evidence":"Confirmed","RawBits":18446744073709551615,"Encoding":"UInt64WireBits","EpochId":"boot-b-1","RuleRevision":"counter-b-1"},"Epoch":{"Evidence":"Confirmed","EpochId":"boot-b-1","BootId":"boot-b-1","Encoding":"UInt64WireBits","RuleRevision":"counter-b-1"},"Wrap":{"Evidence":"NotOccurred","Previous":null,"Current":null,"EpochId":"boot-b-1","DeviceEvidenceId":null},"Reset":{"Evidence":"NotOccurred","Previous":null,"Current":null,"EpochId":"boot-b-1","DeviceEvidenceId":null},"Exposure":{"Availability":"Unknown","Start":null,"End":null,"Clock":{"Kind":"Device","DomainId":"cam-clock-b","EpochId":"boot-b-1","FrequencyNumerator":1000000000,"FrequencyDenominator":1,"Unit":"tick","FrequencyEvidence":"Confirmed"},"PhysicalUnit":"us","Uncertainty":null,"DeviceEvidenceId":null},"Association":{"State":"Confirmed","RuleRevision":"assoc-b-1","TriggerToken":"trig-b-3","EncoderToken":"enc-b-3","PhysicalEvidenceId":"phys-b-3","Scope":"PerLine"},"RawBytes":{"Evidence":"Confirmed","HashAlgorithm":"SHA-256","Hash":"3554726ba0f5404f9a0d3f318041d420f7dc94a4088a548a8c2148bcfd8bb49a","LengthBytes":4,"Padding":{"Kind":"ExcludedDefined","IncludedRanges":[],"ExcludedRanges":[{"Offset":4,"Length":2}],"Evidence":"Confirmed"},"Window":{"PayloadOffset":0,"PayloadLength":6,"HashCoveredRanges":[{"Offset":0,"Length":4}]},"Closure":{"Evidence":"Confirmed","DeclaredBytes":4,"ObservedBytes":4,"ReasonCode":"row-closed"},"SourceRevision":"rev-b-1"},"Closure":{"Evidence":"Confirmed","Reason":"BlockClosed","BytesComplete":true,"CounterComplete":true,"ExposureComplete":false},"SourceRevision":"rev-b-1","Availability":"Partial","Integrity":"Confirmed"}
    ROW_UTF8_LENGTH = 1812
    ROW_UTF8_HEX = 7b2243616e6f6e6963616c56657273696f6e223a226c696e652d666163742f76302e31222c2250726f6a656374696f6e4b696e64223a22526f77222c22536f757263654672616d654b6579223a226672616d652d622d30222c22536f75726365426c6f636b4b6579223a22626c6f636b2d622d30222c22526f77496e646578496e426c6f636b223a332c224172726976616c4f7264696e616c223a332c22436f756e746572223a7b2245766964656e6365223a22436f6e6669726d6564222c2252617742697473223a31383434363734343037333730393535313631352c22456e636f64696e67223a2255496e7436345769726542697473222c2245706f63684964223a22626f6f742d622d31222c2252756c655265766973696f6e223a22636f756e7465722d622d31227d2c2245706f6368223a7b2245766964656e6365223a22436f6e6669726d6564222c2245706f63684964223a22626f6f742d622d31222c22426f6f744964223a22626f6f742d622d31222c22456e636f64696e67223a2255496e7436345769726542697473222c2252756c655265766973696f6e223a22636f756e7465722d622d31227d2c2257726170223a7b2245766964656e6365223a224e6f744f63637572726564222c2250726576696f7573223a6e756c6c2c2243757272656e74223a6e756c6c2c2245706f63684964223a22626f6f742d622d31222c2244657669636545766964656e63654964223a6e756c6c7d2c225265736574223a7b2245766964656e6365223a224e6f744f63637572726564222c2250726576696f7573223a6e756c6c2c2243757272656e74223a6e756c6c2c2245706f63684964223a22626f6f742d622d31222c2244657669636545766964656e63654964223a6e756c6c7d2c224578706f73757265223a7b22417661696c6162696c697479223a22556e6b6e6f776e222c225374617274223a6e756c6c2c22456e64223a6e756c6c2c22436c6f636b223a7b224b696e64223a22446576696365222c22446f6d61696e4964223a2263616d2d636c6f636b2d62222c2245706f63684964223a22626f6f742d622d31222c224672657175656e63794e756d657261746f72223a313030303030303030302c224672657175656e637944656e6f6d696e61746f72223a312c22556e6974223a227469636b222c224672657175656e637945766964656e6365223a22436f6e6669726d6564227d2c22506879736963616c556e6974223a227573222c22556e6365727461696e7479223a6e756c6c2c2244657669636545766964656e63654964223a6e756c6c7d2c224173736f63696174696f6e223a7b225374617465223a22436f6e6669726d6564222c2252756c655265766973696f6e223a226173736f632d622d31222c2254726967676572546f6b656e223a22747269672d622d33222c22456e636f646572546f6b656e223a22656e632d622d33222c22506879736963616c45766964656e63654964223a22706879732d622d33222c2253636f7065223a225065724c696e65227d2c225261774279746573223a7b2245766964656e6365223a22436f6e6669726d6564222c2248617368416c676f726974686d223a225348412d323536222c2248617368223a2233353534373236626130663534303466396130643366333138303431643432306637646339346134303838613534386138633231343862636664386262343961222c224c656e6774684279746573223a342c2250616464696e67223a7b224b696e64223a224578636c75646564446566696e6564222c22496e636c7564656452616e676573223a5b5d2c224578636c7564656452616e676573223a5b7b224f6666736574223a342c224c656e677468223a327d5d2c2245766964656e6365223a22436f6e6669726d6564227d2c2257696e646f77223a7b225061796c6f61644f6666736574223a302c225061796c6f61644c656e677468223a362c2248617368436f766572656452616e676573223a5b7b224f6666736574223a302c224c656e677468223a347d5d7d2c22436c6f73757265223a7b2245766964656e6365223a22436f6e6669726d6564222c224465636c617265644279746573223a342c224f627365727665644279746573223a342c22526561736f6e436f6465223a22726f772d636c6f736564227d2c22536f757263655265766973696f6e223a227265762d622d31227d2c22436c6f73757265223a7b2245766964656e6365223a22436f6e6669726d6564222c22526561736f6e223a22426c6f636b436c6f736564222c224279746573436f6d706c657465223a747275652c22436f756e746572436f6d706c657465223a747275652c224578706f73757265436f6d706c657465223a66616c73657d2c22536f757263655265766973696f6e223a227265762d622d31222c22417661696c6162696c697479223a225061727469616c222c22496e74656772697479223a22436f6e6669726d6564227d
    ROW_SHA256 = e93f183b8e23a1b245293a5da7368375f899d0bc67543814952a0eebca619bb7

    UNKNOWN_ROW_JSON = {"CanonicalVersion":"line-fact/v0.1","ProjectionKind":"Row","SourceFrameKey":"frame-u-0","SourceBlockKey":"block-u-0","RowIndexInBlock":null,"ArrivalOrdinal":null,"Counter":{"Evidence":"Unknown","RawBits":null,"Encoding":null,"EpochId":null,"RuleRevision":"counter-u-1"},"Epoch":{"Evidence":"Unknown","EpochId":null,"BootId":null,"Encoding":null,"RuleRevision":"counter-u-1"},"Wrap":null,"Reset":null,"Exposure":{"Availability":"Unknown","Start":null,"End":null,"Clock":{"Kind":"Unknown","DomainId":"unknown","EpochId":"unknown","FrequencyNumerator":null,"FrequencyDenominator":null,"Unit":"tick","FrequencyEvidence":"Unknown"},"PhysicalUnit":null,"Uncertainty":null,"DeviceEvidenceId":null},"Association":{"State":"Unknown","RuleRevision":"assoc-u-1","TriggerToken":null,"EncoderToken":null,"PhysicalEvidenceId":null,"Scope":"PerLine"},"RawBytes":{"Evidence":"Unknown","HashAlgorithm":null,"Hash":null,"LengthBytes":null,"Padding":{"Kind":"Unknown","IncludedRanges":[],"ExcludedRanges":[],"Evidence":"Unknown"},"Window":null,"Closure":{"Evidence":"Unknown","DeclaredBytes":null,"ObservedBytes":null,"ReasonCode":null},"SourceRevision":"rev-u-1"},"Closure":{"Evidence":"Unknown","Reason":"Unknown","BytesComplete":false,"CounterComplete":false,"ExposureComplete":false},"SourceRevision":"rev-u-1","Availability":"Unknown","Integrity":"Unknown"}
    UNKNOWN_ROW_UTF8_LENGTH = 1344
    UNKNOWN_ROW_UTF8_HEX = 7b2243616e6f6e6963616c56657273696f6e223a226c696e652d666163742f76302e31222c2250726f6a656374696f6e4b696e64223a22526f77222c22536f757263654672616d654b6579223a226672616d652d752d30222c22536f75726365426c6f636b4b6579223a22626c6f636b2d752d30222c22526f77496e646578496e426c6f636b223a6e756c6c2c224172726976616c4f7264696e616c223a6e756c6c2c22436f756e746572223a7b2245766964656e6365223a22556e6b6e6f776e222c2252617742697473223a6e756c6c2c22456e636f64696e67223a6e756c6c2c2245706f63684964223a6e756c6c2c2252756c655265766973696f6e223a22636f756e7465722d752d31227d2c2245706f6368223a7b2245766964656e6365223a22556e6b6e6f776e222c2245706f63684964223a6e756c6c2c22426f6f744964223a6e756c6c2c22456e636f64696e67223a6e756c6c2c2252756c655265766973696f6e223a22636f756e7465722d752d31227d2c2257726170223a6e756c6c2c225265736574223a6e756c6c2c224578706f73757265223a7b22417661696c6162696c697479223a22556e6b6e6f776e222c225374617274223a6e756c6c2c22456e64223a6e756c6c2c22436c6f636b223a7b224b696e64223a22556e6b6e6f776e222c22446f6d61696e4964223a22756e6b6e6f776e222c2245706f63684964223a22756e6b6e6f776e222c224672657175656e63794e756d657261746f72223a6e756c6c2c224672657175656e637944656e6f6d696e61746f72223a6e756c6c2c22556e6974223a227469636b222c224672657175656e637945766964656e6365223a22556e6b6e6f776e227d2c22506879736963616c556e6974223a6e756c6c2c22556e6365727461696e7479223a6e756c6c2c2244657669636545766964656e63654964223a6e756c6c7d2c224173736f63696174696f6e223a7b225374617465223a22556e6b6e6f776e222c2252756c655265766973696f6e223a226173736f632d752d31222c2254726967676572546f6b656e223a6e756c6c2c22456e636f646572546f6b656e223a6e756c6c2c22506879736963616c45766964656e63654964223a6e756c6c2c2253636f7065223a225065724c696e65227d2c225261774279746573223a7b2245766964656e6365223a22556e6b6e6f776e222c2248617368416c676f726974686d223a6e756c6c2c2248617368223a6e756c6c2c224c656e6774684279746573223a6e756c6c2c2250616464696e67223a7b224b696e64223a22556e6b6e6f776e222c22496e636c7564656452616e676573223a5b5d2c224578636c7564656452616e676573223a5b5d2c2245766964656e6365223a22556e6b6e6f776e227d2c2257696e646f77223a6e756c6c2c22436c6f73757265223a7b2245766964656e6365223a22556e6b6e6f776e222c224465636c617265644279746573223a6e756c6c2c224f627365727665644279746573223a6e756c6c2c22526561736f6e436f6465223a6e756c6c7d2c22536f757263655265766973696f6e223a227265762d752d31227d2c22436c6f73757265223a7b2245766964656e6365223a22556e6b6e6f776e222c22526561736f6e223a22556e6b6e6f776e222c224279746573436f6d706c657465223a66616c73652c22436f756e746572436f6d706c657465223a66616c73652c224578706f73757265436f6d706c657465223a66616c73657d2c22536f757263655265766973696f6e223a227265762d752d31222c22417661696c6162696c697479223a22556e6b6e6f776e222c22496e74656772697479223a22556e6b6e6f776e227d
    UNKNOWN_ROW_SHA256 = a9f5b277beeab3ee3438e1f311135f7470a032632e82b93d85f9eefdd59e88dc

固定 token fixture（B第一页输出、第二页输入）独立按上述字段拼接：clock NowTicks=1000000、reader预算10s，Expiry=10001000000ns，LastOrdinal=2，生产key不使用本fixture。下列全部hex无省略，BASE64URL无padding。

    PAGE_INTENT_JSON = {"CanonicalVersion":"line-fact/v0.1","ProjectionKind":"PageIntent","Owner":{"OwnerId":"aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa","SessionId":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","Epoch":"cccccccc-cccc-cccc-cccc-cccccccccccc","Selector":{"AdapterId":"synthetic","StableDeviceId":"line-b"},"Scope":"LineFacts"},"Session":{"InstanceId":"99999999-9999-9999-9999-999999999999","SessionId":"bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb","Epoch":"cccccccc-cccc-cccc-cccc-cccccccccccc","Selector":{"AdapterId":"synthetic","StableDeviceId":"line-b"}},"CaptureOperationId":"dddddddd-dddd-dddd-dddd-dddddddddddd","ReaderId":"02020202-0202-0202-0202-020202020202","SnapshotId":"03030303-0303-0303-0303-030303030303","SourceRevision":"rev-b-1","ExpectedSourceRevision":"rev-b-1","PageSize":2,"MaxTotalBytes":65536,"ClockEpochId":"clock-b-1","ClockFrequencyNumerator":1000000000,"ClockFrequencyDenominator":1}
    PAGE_INTENT_UTF8_LENGTH = 885
    PAGE_INTENT_HEX = 7b2243616e6f6e6963616c56657273696f6e223a226c696e652d666163742f76302e31222c2250726f6a656374696f6e4b696e64223a2250616765496e74656e74222c224f776e6572223a7b224f776e65724964223a2261616161616161612d616161612d616161612d616161612d616161616161616161616161222c2253657373696f6e4964223a2262626262626262622d626262622d626262622d626262622d626262626262626262626262222c2245706f6368223a2263636363636363632d636363632d636363632d636363632d636363636363636363636363222c2253656c6563746f72223a7b22416461707465724964223a2273796e746865746963222c22537461626c654465766963654964223a226c696e652d62227d2c2253636f7065223a224c696e654661637473227d2c2253657373696f6e223a7b22496e7374616e63654964223a2239393939393939392d393939392d393939392d393939392d393939393939393939393939222c2253657373696f6e4964223a2262626262626262622d626262622d626262622d626262622d626262626262626262626262222c2245706f6368223a2263636363636363632d636363632d636363632d636363632d636363636363636363636363222c2253656c6563746f72223a7b22416461707465724964223a2273796e746865746963222c22537461626c654465766963654964223a226c696e652d62227d7d2c22436170747572654f7065726174696f6e4964223a2264646464646464642d646464642d646464642d646464642d646464646464646464646464222c225265616465724964223a2230323032303230322d303230322d303230322d303230322d303230323032303230323032222c22536e617073686f744964223a2230333033303330332d303330332d303330332d303330332d303330333033303330333033222c22536f757263655265766973696f6e223a227265762d622d31222c224578706563746564536f757263655265766973696f6e223a227265762d622d31222c225061676553697a65223a322c224d6178546f74616c4279746573223a36353533362c22436c6f636b45706f63684964223a22636c6f636b2d622d31222c22436c6f636b4672657175656e63794e756d657261746f72223a313030303030303030302c22436c6f636b4672657175656e637944656e6f6d696e61746f72223a317d
    PAGE_INTENT_SHA256 = 4fffd2ebc3366a8f7a81cb9e7e0e5704a070128a360db7de09cb880f7659a08b
    SORT_KEY_JSON = {"CanonicalVersion":"line-fact/v0.1","ProjectionKind":"SortKey","SnapshotId":"03030303-0303-0303-0303-030303030303","SourceRevision":"rev-b-1","BlockOrder":"LedgerBlockOrdinalAscending","RowOrder":"LedgerSourceOrdinalAscending","UnknownRowIndex":"KeepSourceOrdinal","ArrivalOrder":"PreserveFactOnly"}
    SORT_KEY_UTF8_LENGTH = 300
    SORT_KEY_HEX = 7b2243616e6f6e6963616c56657273696f6e223a226c696e652d666163742f76302e31222c2250726f6a656374696f6e4b696e64223a22536f72744b6579222c22536e617073686f744964223a2230333033303330332d303330332d303330332d303330332d303330333033303330333033222c22536f757263655265766973696f6e223a227265762d622d31222c22426c6f636b4f72646572223a224c6564676572426c6f636b4f7264696e616c417363656e64696e67222c22526f774f72646572223a224c6564676572536f757263654f7264696e616c417363656e64696e67222c22556e6b6e6f776e526f77496e646578223a224b656570536f757263654f7264696e616c222c224172726976616c4f72646572223a225072657365727665466163744f6e6c79227d
    SORT_KEY_SHA256 = d2c417243bf84ca5f4c4f767f3ba096e7f37b1df360a8b7120a371ab2be3d88a
    TOKEN_PREIMAGE_UTF8_LENGTH = 145
    TOKEN_PREIMAGE_HEX = 0102020202020202020202020202020202b5f9e2fbbcc754ad73b36d0a0763bb7c488436f4e84db29045f9d8d6c1bcdc344fffd2ebc3366a8f7a81cb9e7e0e5704a070128a360db7de09cb880f7659a08bd2c417243bf84ca5f4c4f767f3ba096e7f37b1df360a8b7120a371ab2be3d88a000000000000000200000002541b2640000102030405060708090a0b0c0d0e0f
    TOKEN_PREIMAGE_SHA256 = 369fdc8fb4eeecf91b4b015b71ea9367f8c4751a8a80c0f7d4279a9fe4084ff9
    TOKEN_UTF8_LENGTH = 177
    TOKEN_HEX = 0102020202020202020202020202020202b5f9e2fbbcc754ad73b36d0a0763bb7c488436f4e84db29045f9d8d6c1bcdc344fffd2ebc3366a8f7a81cb9e7e0e5704a070128a360db7de09cb880f7659a08bd2c417243bf84ca5f4c4f767f3ba096e7f37b1df360a8b7120a371ab2be3d88a000000000000000200000002541b2640000102030405060708090a0b0c0d0e0f8faf1ad4fbb11f83fb883e4f4c19568a75f0626dcbaece795c6a1be7ec24d0bf
    TOKEN_SHA256 = 68151d6bd6c18db9f916c85ba09998bb06e8d6504a71fa28b97d6d68b4344bb7
    TOKEN_MAC_HEX = 8faf1ad4fbb11f83fb883e4f4c19568a75f0626dcbaece795c6a1be7ec24d0bf
    TOKEN_BASE64URL = AQICAgICAgICAgICAgICAgK1-eL7vMdUrXOzbQoHY7t8SIQ29OhNspBF-djWwbzcNE__0uvDNmqPeoHLnn4OVwSgcBKKNg233gnLiA92WaCL0sQXJDv4TKX0xPdn87oJbn83sd82CotxIKNxqyvj2IoAAAAAAAAAAgAAAAJUGyZAAAECAwQFBgcICQoLDA0OD4-vGtT7sR-D-4g-T0wZVop18GJty67OeVxqG-fsJNC_

载荷hash fixture（RawBytes.LengthBytes=4，完整六byte容量账保留padding）：

| 完整payload | hash覆盖[0,4) | SHA-256 |
|---|---|---|
| 00010203aabb | 00010203 | 054edec1d0211f624fed0cbca9d4f9400b0e491c43742af2c5b0abebf0c990d8 |
| 10111213aabb | 10111213 | a00291e8229d191815f2cbd2aa49d3b783585deae8012ca5941f011ceb9eb119 |
| 20212223aabb | 20212223 | dca25343ae48846cd00fa1d9675ddb0912738b5ac700bda7022a81678fb83ed7 |
| ff00ff00aabb | ff00ff00 | 3554726ba0f5404f9a0d3f318041d420f7dc94a4088a548a8c2148bcfd8bb49a |
| 30313233aabb | 30313233 | 1be2e452b46d7a0d9656bbb1f768e8248eba1b75baed65f5d99eafa948899a6a |
| 21212223aabb | 21212223 | a9691948c25de2def93c443da8c81402bbe68da37d3e8ab3a7d176034b47a1fb |

### 20.8 两轮有限定向自审与状态

第一轮仅复走本次接口：Root Reserve/Register→typed Attach强持原Task→自动Track成功Value→有限Observe/GetTask→真实Return/Close→Confirm→Release；producer的Ledger/完整Payload/ExpectedRange三来源逐字段接线；双Host在无handle、Open/read/close迟到、cleanup抛错情况下仍保留原Root/Task/资源。不重审C1或硬件研究。

第二轮仅复走编码与反例：Snapshot/Page/QueryResult正文self-hash=null、真实Rows/来源、Owner/Session/Resources顺序，稳定PageIntent/QueryIntent排token/CAS，RFC4122 Guid16、177byte token及145byte MAC，排序预像/key/nonce/CAS重放缓存预算与失效，X的counter/association两规则、缺行范围、arrival逆序和跨epoch查询。三组已接收编码向量保留，新增token/载荷向量只作规格编码校验。

主控于2026-10-11完整回读§20并限定接收C2-RF六项文档规格，C2-RF同步为 `ModuleCoreImplementationReady`（仅规格准备）；C1的ModuleCoreImplementationReady与原474-byte向量保持，C2设备/Frame Owner正式映射、真实SDK/编译、WPF、性能/HIL/现场门不变，不提升运行或产品资格。仅编辑本指导，没有新增工程/测试/脚本/报告/会话/子代理或共享文件；未编译、未运行产品BCL Exe、HALCON/MVS/WPF、性能、HIL或现场验证。


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

## 21. 全部批准范围的文档准备结论

### 21.1 采集、逐行事实与高吞吐的确定实现

本模块完整批准范围为单设备面阵/有限连续/线扫块、触发selector与预约关联、设备逐行事实只读交付、曝光/自动模式、配置/读回、丢帧/部分帧、独占/恢复/资源生命周期、Simulator/Replay接入端口、MVS/HALCON适配与可选工作台。多个相机分别实例化本模块并保留各自selector/session/epoch/预算/队列/租约/恢复槽；共享runtime/gate仅串行必要SDK全局调用，不串行所有相机的数据worker。跨相机时钟同步、同一运动轨迹、结构光图案序列、光源、生产补拍和质量放行均由外部编排Owner决定，模块不新增GroupCapture/运动对象，不用到达时间排序制造跨设备全序。

线扫成块首选设备已封口块。RawLineDelivery的内部聚块算法固定：在arm前按LinesPerUnit/最大行payload预留有限块槽/位图/行缓冲；单一Adapter worker按设备已证block key与原行index映射到[0,LinesPerUnit)，保留原arrival/counter/epoch/两种rule。新行先核长度、单位/来源、同块规则和索引；重复index且同事实/字节只计Duplicate，不覆盖原槽；异内容计Conflict并污染块，原资源仍逐一归还。只有设备BlockEnd或FixedVerifiedLineCount的原协议能确定块终点；每位齐、无conflict、原规则/完整性已证实才按RowIndex升序复制到独立块并交Core。封口时缺行/坏行/timeout为Incomplete或Failed，交付0块、不补零/插值；保存原收到事实和期望范围供§20诊断读。跨epoch/wrap/rule新块必须有原协议分段证据，无证据则拒该模式，不能把RawBits小值推为回卷。设备行timestamp/exposure/encoder不可得用Unknown，块首尾/名义行频不能插值生成中间曝光或motion pose。

§20只读入口的真实连接由原Camera Session Owner保存 immutable `LineFactLedgerCaptureSnapshot` 与实际 `LineFactPayloadRow<TFrame>`：在SDK buffer仍有效时提取原行事实/复制完整载荷到预留staging；归还成功后冻结行和完整payload；同capture封口后以新SourceRevision发布一份快照。Ledger端口仅读此快照的block/locator/期望range；Payload端口按原block/source ordinal读保存的完整payload，取得独立BorrowId并监测Return/Close。未提供行协议则Support=NotSupported并禁止payload Open，不以失败空数组冒0行；有行协议但字段未知保留Unknown。两只读端口不拥有设备、不调用SDK获取“当前帧”、不重采，也不通过旧IOperationLedger的operation摘要伪造行账。保存事实的Owner可用宿主已批准内存/存储实现，软件Core不依私有数据库；容纳行/payload的容量与MaxTotalRows/Bytes在capture接纳前一并预留，不因读者要求历史事实再无限留图。

读取前的引用和捕获生命周期分开：快照发布持有由原Session Owner保留；每个reader/payload lease借用同一不可变修订，Close只归还自身借用；Owner只有封禁止新reader且所有原借用/原Task实际退出后才可退役该修订。Revision变化发布另一修订，原FixedSnapshot不变；CurrentSource只查询current revision，不能重新open旧设备。需要历史持久/跨重启保留的策略属于Host证据Owner，必须给出期限/容量/稳定revision和引用回执，否则仅提供进程内已保存快照，不能声称重启后逐行事实仍在。

高吞吐固定三个串行阶段/有界队列：SDK接收及短复制→独立staging发布/事实冻结→Core inspect/hash/交付；控制Stop/Close走保留控制槽，不在每帧建Task等空位。Q=QueueCapacity，P=每完整backing上界，D=DriverResidentUpperBoundBytes，I=InFlightUpperBoundBytes，T=所有scratch/元数据/聚块位图，S=设备元数据/原SDK复制临时上界，C=本次消费者仍持有且未包含在Q的独立backing上界。capture reservation至少checked `D+I+Q*P+S+T+C`；共享发布产生另一独立storage时该阶段每slot同时staging/target双占计2P，故该阶段Q*P项改为Q*2P，不能用“默认会很快归还”扣额度。实际物理allocation仍按唯一ID计一次，保留池不清零。无S/C或读出在途停止窗口上界证明时拒Hardware Start，软件fixture显式冻结这些上界不冒设备数值。

队列满或出版物/行账额度满时，Core/Adapter立即封输入并沿A.6必要清理；可Pause只在已声明设备语义且Host明确允许时使用，不丢必需帧/行。不提供LatestImageOnly作为生产取流策略。计算摘要在worker，不在SDK指针回调。SharedCameraFramePort的ContentSha256完整预像为：A.6值规则编码对象 `{"LayoutRevision":...,"Layout":<lease.Layout完整字段>,"Metadata":<lease.Metadata完整数组>}` UTF8，无self-hash/arrival；然后按planeIndex/localY顺序拼每行精确RowBytes原字节，SHA-256小写hex。Layout/Metadata字段顺序直接沿image-frame §4.4/§4.3，不另序列化frame对象；Metadata.Scale/Bias有限double按G17 invariant往返形式编码，非有限拒绝，不用语言相关格式或转decimal截精度。声明精确行长度且无padding混入；原frame key/epoch/capture是去重域，不以不同frame ID的hash相同就当重复。单块查重在MaxUnits/MaxReceiptItems额度内，计数checked、截断只影响详情，不删除冲突总数。

§20.RawBytes.Hash仍只覆盖声明窗口；其Canonical正文/token沿已接收向量，不把本段整帧摘要换成原行hash。运动Actual XY/时钟映射/触发工位来自motion-control/device-signals及宿主同步Owner，不在Adapter把First/LastLineEncoderCount标量推为连续轨迹。需要可信运动/逐行时间的mosaic/标定宿主只消费对应Owner的同run桥；无域/关联证据就拒其物理计算，同时允许独立采集工具观察Uncorrelated原帧。

### 21.2 自动模式、版本、验收与双消费者

自动曝光/增益只有设备已声明Once/Continuous才允许显式请求；off请求固定有限数值，auto请求数值null，设备auto不是本模块图像质量优化。每帧actual仍以设备逐帧证据为准，只有当前读回无chunk时不能冒actual。自动模式导致当前值变化时，Current事实revision随真实读回变化，CaptureRequest锁定的配置revision描述arm时设置，后继FrameFacts.ActualConfiguration保留实际字段证据；若设备不能提供采集Profile所要求的逐帧actual/稳定条件，拒该Profile的auto模式，不用名义曝光证明图像/节拍合格。本模块无数值推荐算法，合法域/default来自已核能力，用户显式应用；image-quality/imaging-optimization若给建议，也必须以新配置/版本走同一纯校验和Apply，不能绕Owner或静默改生产值。

Core Module API v0.2及line-fact/v0.1不改。§10.3新增Inputs/SetInputs/GetAttachment为WPF候选形状v0.3，必须显式提供完整Inputs；旧候选形状v0.2不隐式补空token/draft，实施时按新的模块包版本绑定并拒不兼容consumer。不存在已交付旧包迁移或实现兼容承诺；未来改变单位/所有权/default仍按§7升破坏性版本。Adapter Profile是独立版本/hash，格式映射或设备node语义变则重新查询能力，不复用旧ConfirmedRevision。

后续Tests.Adapters执行CAM.A1.01～08：01两个selector/实例数据和SDK runtime引用隔离，第二Owner拒；02node访问/Single表示/enum/ROI安全过渡及partial；03OneByOne/SDK buffer短复制且Free失败不交付；04poll timeout/停止/晚到read仍强持原Task，不二次open；05发布/Read/import未知保留原source与原operation查询且只复制一次；06原行缺/重/冲突/回卷不猜、无行协议拒；07HALCON同步/异步MaxDelay/预取授权/所有多输出释放及gate；08runtime Finalize只能在全部设备关闭和原SDK Task退出后。每case/套件/外层有限预算沿A.9，不用fake判断实机支持的停止行为。两个独立消费者沿§9/§20，新增软件fixture为两个4×2 Mono8源，各8个已知字节（A为0001020304050607，B为1011121314151617，stride=4、两行、Full域），不同selector/frame key/独立allocation；A消费异常/持帧停采，B数据/计数/hash保持，A独立lease归还前A不Released。逐行B/X有效向量复用，不重新生成；SDK/真实接口分别独立数据源，不能同进程重复打开一个物理设备当双消费者通过。

公开验证路径只在实际切片授权后创建A.8各工程：`dotnet build <A.8对应csproj> -c Release`；`dotnet run --project tests/Modules/CameraAcquisition/Asun.Pcb.Modules.CameraAcquisition.Adapters.Tests/Asun.Pcb.Modules.CameraAcquisition.Adapters.Tests.csproj -c Release`及同目录 `Asun.Pcb.Modules.CameraAcquisition.Wpf.Tests/Asun.Pcb.Modules.CameraAcquisition.Wpf.Tests.csproj` 执行受影响用例，不用dotnet test无输出冒完成。Benchmark复用§14/A.9全部cold/hot/deadline/真实释放分位规则，增加rawline聚块、SDK复制→共享发布短时双占、metadata/row摘要、Q高水位、两设备共享gate竞争、UI显示节流的独立测点；所有目标由Consumer Profile，缺值NotEvaluated。HIL/物理曝光/丢行/encoder时序、WPF/UIA/固定1920×1080、加载/封送/真实资源仍未执行。

### 21.3 准备结论与准确外部Owner

**结论：当前架构及用户批准的完整模块范围，可决定的软件设计已闭合；没有留给后续开发者补选的内部算法、API、架构或UI接线决定。** §8.2/8.3和§10.3/10.4是本轮补齐的缺口，§21.1补精确RawLine聚块/保存事实/容量与摘要边界；已接收C1和C2-RF及有效研究/向量继续复用。设计已确定不等于正式平台集成接收、代码Ready、实现或运行通过；C1/C2-RF仅保持原ModuleCoreImplementationReady规格状态，其余切片按DEV-GOV-010受影响准入项执行。

| 完整范围/关键正文 | 文档准备与保留Owner/外部门 |
|---|---|
| 单设备发现/参数/面阵/有限连续/触发/帧关联/错误/资源 | §1–7、§9、§19、A.1–A.9；软件设计闭合，Core/Simulator已接收规格。实现Owner为本模块原会话；可审计代码基线/实施派发由平台集成Owner绑定，本轮不写代码 |
| 多相机/序列/运动与时间使用 | §1/§19/§20/§21.1；实例隔离/可证明事实交付闭合。跨相机/PTP或硬件时钟/图案序列/运动联动由宿主编排、device-signals/motion-control/structured-light Owner提供同run证据；不是相机未设计的Group API |
| C2共享帧/ledger/access/逐行只读桥 | A.5/A.11、§20；映射/来源/取消/恢复/借用已明确。image-frame Owner持共享公开lease/布局与真实归还实现；Host设备治理Owner负责耐久IOperationLedger、CrossProcess access/fencing及进程恢复，硬件Owner提供封口/逐行协议。正式平台Schema/技术部署是对应采纳门，不让Core猜私有DB/设备字段 |
| C3 MVS/C4 HALCON | §8.1–8.3/§18；具体装配、public调用、复制/导入/停止/释放设计闭合。目标设备/采集接口Owner提供型号/固件、节点/像素/单位/stride/trigger/line/chunk/abort/资源上界的官方Profile；缺失只拒受影响模式。实际DLL加载/重载/封送/x64/native与SDK HIL由本模块实施时验证；不重核AsunImage/DevExpress依赖资格 |
| 参数default/自动模式/推荐 | §3/§18.2/A.3/§21.2；设备报告域/default与显式Once/Continuous闭合，不提供图像驱动数值推荐。设备Owner确定可观测auto/逐帧actual，消费者Profile Owner确定其允许条件；质量优化归相应优化Owner，不是隐式生产参数权威 |
| C5独立WPF工作台 | §10/A.10/§21.2；真实控件组合、布局、三语、命令、权限、键盘、Dispatcher/原Attach/Preview恢复及双STA验证规格闭合。Host viewport/本地化/主题与设备Session Owner负责其真实端口组合；本模块负责WPF实现和定向验证，页面无设备/质量放行权 |
| C6高吞吐/正确性/Golden/HIL/交付 | §11–14/§16/§19/§20.7/§21.1–2；负载/测点/合成oracle/失败/双消费者规格闭合。客户与设备验收Owner提供真实Profile/样本/预热与时延/丢帧/曝光/停止等物理目标，本模块负责实施后的Golden/资源/性能/HIL验证；未知事实不编数值 |

### 21.4 本轮有限自审与文档验证边界

自审仅覆盖上述实际缺口：第一次按两个消费者装配，复走Profile→SDK/取流→独立staging→发布/import→sink/原lease归还→runtime/gate关闭及工作台未移交Attach恢复；第二次用SDK Free失败、pub/import迟到、ROI依赖变化、自动模式无actual、RawLine缺/重/跨epoch、队列/额度满、Dispatcher关闭、权限撤回和显示代次反例对照单一Owner/有限预算。未重审C1/C2-RF已接收内容或复做研究；两次属于设计走读，不能写作已运行测试。

文档验证复用tools/validate_docs.py，并对本指导新增类型/正文引用、章节/表格/fence/本地链接、既有向量文本保持及MVS/DevExpress本机官方公开成员作定向核对；本轮这些检查已通过，范围仅文档一致性。没有创建过程报告、测试工程、脚本、会话或子代理；没有修改其它模块/共享文件/客户项目。本轮只交付指导；产品C#编译/BCL Exe、MVS/HALCON/WPF/UIA、真实性能/Golden、HIL/FAT/SAT/生产资格全部保持未执行，不等待总控再做模块内容审核。

### 21.5 兼容影响与既有消费者同步

本轮不改变Core v0.2输入/输出、Owner/单位/取消及归还合同，也不改变§20 line-fact/v0.1的record字段、分页/token编码或原五组向量。WPF候选形状v0.3新增必需Inputs及SetInputs/GetAttachment，旧v0.2构造**不能源兼容**：采集工具与检测应用工作台组合根必须提供显式Adapter/token/draft，并在Attach未知时保有原槽/用GetAttachment恢复；不允许以默认值适配旧构造。本项目尚无已交付WPF包，不能声称旧二进制已兼容。

MvsCameraTransport/HalconCameraTransport及其Runtime/Gate/Profile/Protocol是原候选Adapter装配的首次精确定义；新的真实Host按§8.2–3提供依赖/Profile及原Task恢复槽。这些类型不替换ICameraTransport/Core接口，不要求Simulator或纯Core消费者引入SDK。Target SDK/接口/物理字段事实仍由设备Profile Owner确认，不把新增Profile字段伪装为已有客户配置信息。自动actual/Single表示/SDK归还/原行Unknown与高吞吐背压只是补明既有证据、精度、生命周期语义，不改变默认值、不允许静默设备动作。

| 既有消费者/Owner | 本轮同步要求 |
|---|---|
| IM-023 mosaic C.10/M-LR | 上游指南版本可登记0.4.3-prep；依赖的§20构造/API/身份/完整Rows/hash/token/原Task不变，**无需修改消费契约或向量**，不得因此重做既有C2-RF消费审算 |
| IM-013 calibration-assets及相机采样宿主 | 逐行读取/只读事实与Core类型不变，**无需消费者API修改**；真实硬件装配时采用本轮明确Profile和原Owner，不从未知曝光/encoder补采样值 |
| IM-011 structured-light | FrameFacts/预约/触发API未改，**无需消费者合同修改**；跨设备/图案序列仍归其Owner，不将相机原字段当自动同步证明 |
| IM-006 image-frame、viewport/本地化/主题模块 | 本方只调用上游已批准端口，**无需上游API修改**。生产Host新Adapter/工作台组合根负责提供原service/import/preview借用，不要求上游新增SDK/相机业务字段 |
| 独立采集工具、检测应用工作台组合根Owner | 采用WPF v0.3显式Inputs、GetAttachment原槽恢复、固定实际权限/布局/三语；真实Adapter接线采用§8.2–3。这是本轮需同步的具体调用者；目前未发现其它模块指导直接声明旧CameraWorkbench构造，禁止据此擅改其它模块 |

SharedCameraFramePort的完整layout/metadata+行字节hash属于本轮补明的编码语义，尚无已核实的既有实现/持久摘要迁移事实：实现Owner须按§21.1重算本方摘要，若实际客户实现使用其它preimage，必须版本化/重算其自己保存的摘要，不静默把旧值标为新编码；它不替换image-frame自身content hash或C2-RF RawBytes.Hash。无需其它模块改公开合同，正式消费者若锁定本方FrameInspection摘要须由其原Owner在实现接入时确认这条编码。未扫描产品代码、不代做跨模块审核；总控据本表协调原会话即可。
