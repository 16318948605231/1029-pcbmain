# 运动控制能力独立模块开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`S1, S2, Motion Read Bridge v0.1`

- 模块：`motion-control`（运动控制能力）
- 映射：`IM-010` / `PKG-010`
- 文档版本：`0.2.5-prep`
- 状态：S1/S2、Motion Read Bridge v0.1 `ModuleCoreImplementationReady`（仅规格准备）；S3/S4 与产品集成 `PreparationIncomplete`；逐切片结论见 A.6/A.8
- 日期：2026-10-11
- 规划消费者：扫描工具、定位工具、维护工具
- 技术基线：C# / .NET 10；核心无 UI；可选 WPF/DevExpress 控件；设备由适配器注入
- 全范围文档核实：当前架构 IM-010 的可决定软件设计已闭合，原会话完成内容自审；完整范围、补充实施规则和外部门 Owner 见 §17。此结论不是整模块实施或运行资格，也不再等待总控内容审核。
- 模块级设计评审态：`DesignReview`（方案可评审）。§17「当前架构全范围核实与补充实施规则」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本文是该模块的唯一实施指导。它定义设备无关的运动边界和可验证语义，不表示厂商 SDK、PLC、安全回路或 HIL 已接入，也不授予生产资格。未冻结的设备事实必须由适配器能力快照报告，不能在核心中猜测。

## Core implementation binding

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/motion-control/Asun.Modules.MotionControl.Core/Asun.Modules.MotionControl.Core.csproj`；namespace：`Asun.Modules.MotionControl`。预定测试工程：`tests/Modules/motion-control/Asun.Modules.MotionControl.Core.Tests/Asun.Modules.MotionControl.Core.Tests.csproj`。上述项目尚未创建。
- Core/Simulator/Adapter Port 的实现切片只允许上述 Core 和测试工程目录；Simulator 不另建产品工程。最小 Host 是测试工程中的 `Hosts/MinimalMotionHost.cs`，两个消费者契约测试位于 `Consumers/`。核心程序集及 NuGet 包名均为 `Asun.Modules.MotionControl.Core`，`net10.0`，仅 BCL，不引用 WPF 或其它模块实现。
- `Motion Read Bridge v0.1` 属 Core 内的增量只读能力，允许变更仍限上述 Core/Tests 目录；其两个 mosaic 空 Host 只作为后续消费者契约测试输入，不在 motion-control 外创建工程，不修改 mosaic/共享/产品代码。
- 可选 UI 后续切片唯一落点：`src/Modules/motion-control/Asun.Modules.MotionControl.Wpf/Asun.Modules.MotionControl.Wpf.csproj`（`net10.0-windows`，namespace `Asun.Modules.MotionControl.Wpf`）；测试：`tests/Modules/motion-control/Asun.Modules.MotionControl.Wpf.Tests/Asun.Modules.MotionControl.Wpf.Tests.csproj`，内置 `Hosts/MotionControlTestWindow.xaml`。UI 只引用 Core 和本机 DevExpress 25.2.3；测试窗口不是产品 Shell。不得用本条提前创建空工程。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 当前状态：主控已接收 S1（纯模型/校验/codec）及 S2（Core + Simulator/Replay + 注入 Ports）为 `ModuleCoreImplementationReady`，仅表示 DEV-GOV-010 §3.1 六项规格准备已接收。权威代码快照/分支尚未确认，须在后续明确实现任务创建工程前确认；本次不创建工程、不自动派发实现。真实 S3 WPF、S4 硬件/持久 ledger/路径能力、性能与现场门保留，产品集成仍为 `PreparationIncomplete`；本绑定不是实现、测试、集成或资格通过声明。

## 1. 职责与禁止边界

### 1.1 模块负责

- 轴和坐标系的强类型描述、能力快照、版本和来源。
- 连接生命周期、状态镜像、位置/速度/跟随误差反馈。
- 回零、绝对/相对定位、连续点动、轴组插补（设备支持时）、比较触发登记（设备支持时）。
- 受控停止、保持、故障复位、互锁变化和紧急停止事实的镜像。
- 位置转换、软限位预检、settled 窗口判定、命令幂等、取消/期限和资源排空。
- 结构化回执、诊断事件、测量时序和可重放的 Simulator/Adapter 合同。

运动控制没有视觉算法路线。HALCON 26.05 `halcon算子手册\\operators` 与 `ImageLibDotNet` 公共边界对本模块核心不适用；位置/反馈滤波也不得借视觉算子或 AsunImage 隐式实现。若宿主同时处理图像遮挡、模糊或退化，视觉质量与重拍策略由宿主/视觉模块负责，不能改写 Motion actual、settled 或安全状态。

### 1.2 模块不负责

- 安全 PLC、门禁、急停回路、危险区、机械限位的实现或替代；软件只能请求/镜像，硬件安全链拥有最终权威。
- 扫描路径、定位目标、板件/工单/Panel/FOV 关联、采集编排、工艺解释、质量放行、复判或设备出板。
- PCB、PCBA、SPI、AOI、点胶、涂覆等制程判定。
- 私有数据库、产品 ViewModel、全局 ServiceLocator、自动发现设备、隐藏窗口初始化。
- 将指令位置、命令 ACK、最后一次状态或模拟器结果包装成实际到位/稳定/安全证据。
- 直接引用厂商 SDK 类型；SDK 只能存在于可替换 Adapter。

调用方拥有流程顺序、目标关联、权限策略、路线授权、采集触发许可、质量处置和所有产品副作用。模块返回事实和可判定失败，不替调用方做最终决定。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.MotionControl.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.MotionControl.Wpf` 可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1 已确认"核心可在无设备、无 WPF 宿主中运行"；§1.2 已确认"事件通过宿主提供的调度器发布；默认不保证 UI 线程，WPF 控件自行切换 Dispatcher，核心不引用 Dispatcher"，二者直接验证这条门禁。

**Blazor/Web 宿主中的运动状态监控**：Web 端需要"展示轴实际位置、跟随误差、限位状态与运行模式"时，服务端通过 `integration-transport` 的 SignalR Hub 推送本模块的状态快照。约束：
- 浏览器端只渲染数值与状态灯，**不直接发运动命令**；绝对定位、点动等命令必须经 WPF 操作台（或已授权的维护接口）发起，不经浏览器
- §1.1 已明确"不用指令位置或命令 ACK 替代实际到位/稳定/安全证据"——Web 端的"到位"指示只能来自本模块的已确认 settled 事实，不是命令确认
- §1.2 已明确"软件只能请求/镜像，硬件安全链拥有最终权威"——Web 端不得以"远程解除互锁"为由绕过硬件安全链

**AI 推理 Tiling 适配**：运动控制与 AI 推理的交互点是**扫描触发时序**。适配约束：
- `ai-inference` 不直接调用本模块；触发时序由宿主编排（宿主在扫描到位后触发 `camera-acquisition` 采集，采集完成后启动 AI 推理流程）
- 三态仲裁（`ai-inference` §1A）中的 `NeedsHuman` 或 `NeedsSampling` 决定**不重新触发运动**；重拍路径由宿主按已冻结策略决定，不在本模块内部实现

**HALCON 备选策略不适用**：本模块不执行任何视觉算法（§1.1 已明确"运动控制没有视觉算法路线，HALCON 26.05 与 ImageLibDotNet 对本模块核心不适用"）。HALCON 备选双跑 CI 不涉及本模块。

## 2. 设计与依赖边界

```text
扫描/定位/维护宿主
        ↓ 公开强类型接口
Motion Core（状态、校验、命令、回执、诊断）
        ↓ I/O 端口
Motion Adapter（PLC/控制器/模拟器；厂商 SDK 只在此处）
        ↓
设备安全链与实际反馈
```

核心可在无设备、无 WPF 宿主中运行。公开端口由附录 A 定义；宿主以组合适配器接入 `coordinate-geometry`、`diagnostics`、授权和存储能力，Core 不直接引用它们的实现或产品 DTO，不复制它们的资产和事实 Owner。坐标端口只解析宿主已选择的版本，不优化扫描路线。视觉算法不参与运动计算；本模块不调用 HALCON/AsunImage。

幂等与操作回执通过注入的 `IOperationLedger`/耐久回执端口保存；Core 不创建私有数据库、文件格式或第二事实库。Ledger 必须能按授权域、CommandId、canonical hash、generation 和 operation revision 原子查询/保留/提交/读取，实际存储、备份、ACL、磁盘配额和跨进程一致性由部署/平台 Owner 提供。端口不可用、只读或无法证明原子性时，硬件写通道保持关闭；Simulator 可使用内存实现但必须标记来源。

## 3. 公共契约与单位语义

模块 Core API 唯一形状见附录 A v0.2；本章解释其单位和处理语义。产品映射仍为候选，不得把模块 API 当作已采纳的平台 Schema。旧 v0.1 的不完整代码形状被 v0.2 替代；不存在同时有效的两套 DTO。

### 3.1 标识、单位和数值

| 类型 | 字段 | 单位/约束 | 默认或来源 |
|---|---|---|---|
| `AxisId` | `Value` | 非空、ASCII `[A-Za-z0-9._-]{1,64}` | 设备能力快照；区分大小写规则由 Adapter 声明 |
| `CoordinateFrameId` | `Value` | 非空、同上 | 坐标资产/适配器；未知帧拒绝 |
| `LinearPosition` | 毫米 | 有限；Adapter 转换脉冲/编码器值 | 调用方目标坐标 + 能力快照/坐标资产；不接受无单位裸数 |
| `RotaryPosition` | 度 | 有限；Adapter 转换设备原生角度 | 调用方目标坐标 + 轴能力；不能把度解释为弧度 |
| `Velocity` | mm/s 或 deg/s | 正值且不超过能力范围 | 每次请求显式提供；生产/维护配置由调用方 Profile 提供，不设模块默认值 |
| `Acceleration` | mm/s² 或 deg/s² | 正值且不超过能力范围 | 每次请求显式提供或引用有版本的运动 Profile；不设模块默认值 |
| `Jerk` | mm/s³ 或 deg/s³ | 可选；正有限且不超过能力上限 | 仅 Profile/能力均支持时接受；不支持时返回 `Unsupported` |
| `PositionTolerance` | 与轴位置相同 | 正值且不小于能力可分辨下限 | SettledPolicy/设备 Profile 显式提供；不设模块默认值 |
| `SettledDwell` | 单调时钟时长 | 正值且能被采样策略观测 | SettledPolicy/Profile 显式提供；不设模块默认值 |
| `CommandDeadline` | 单调时钟时长 | 正值且在运行时允许范围内 | 调用方任务期限；缺失则参数错误，不用无限期限或模块猜值 |
| `FeedbackPeriod` | 单调时钟时长 | 不得要求超过设备能力的采样率 | Adapter/设备能力声明；宿主只可选择已声明档位 |

整数和计时换算使用 checked；浮点每次运算后检查 IsFinite 和范围，拒绝 NaN、Infinity、溢出和单位缺失。负零在校验和 canonical 中统一为正零，不作为另一方向或另一请求。长度/角度符号由轴能力的正方向定义；核心不根据轴名猜方向。范围、步进、单位、正方向、分辨率、是否需停机、是否可写、是否需要授权和精度必须绑定 `MotionCapabilitySnapshot` 与配置 revision。运动参数不得有隐藏默认值；缺项、单位冲突或能力范围不完整时，在设备调用前拒绝。唯一可用默认是无副作用读查询和 Simulator 的测试策略，不能沿用到硬件。

### 3.2 轴、轴组、版本与授权

轴 ID 使用 Ordinal、区分大小写；全模块不允许同名映射到两根物理轴。线轴用 mm，角轴用 deg，速度/加速度/jerk 分别用对应单位的一、二、三阶时间导数；位置只表示有界、多圈展开值，不隐式取模或选择最短旋转。需要模轴路线时，宿主先提供明确展开轨迹及圈数，Core 按同一路径验限位。

轴组是能力快照中的唯一 `AxisGroupCapability`：有序轴集合、可并发资源键、可用插补/原子提交/同步反馈能力。单轴请求的 Scope 只含一轴且 GroupId 为空；轴组请求必须与登记集合完整一致。重复轴、空集合、未声明组、两个组共享轴但同时写入，分别在提交前拒绝或返回 Busy。独立轴可在 Adapter 明确支持并行资源键时并行；共享轴按排序后的资源键一次性预留，禁止先锁部分再无限等待。Controller 级 Open/配置/Reset/Recover/Close 为全控制器屏障；轴命令只比较其 Scope 的轴状态版本，不因无关轴位置变化误拒绝。

`CommandContext` 绑定授权域、OwnerId、CommandId、ExpectedBootId/Generation、能力/配置摘要、目标轴状态版本和总 Deadline。会话配置 Revision 与每轴 StateVersion/PositionVersion 分开：反馈采样序号不是位置版本；轴状态、目标、可信基准或坐标映射变化使对应版本更新，静止期间重复采样只更新 SampleSequence。旧版本不能补成“当前版本”。跨线程身份/Scope/前置/CAS 和优先停止标志在同一 gate 提交，实际 IO 在 gate 外且由单一提交 Owner 执行；普通提交必须在发起原生调用前最后核停止标志。

版本分工：StateVersion 在轴工作态、Servo/Homed/限位/故障等控制事实变化时推进；PositionVersion 在接受的实际位置值或其可信基准/Frame/资产变化时推进（同值重复采样不推进）。**TargetVersion 独立**，每个已接纳位置/Home operation 为每轴冻结一次，不能因实际反馈变化而推进。SettledRequest/ExecutionRecord.TargetVersions 使用 AxisTargetVersion；FinalPositionVersion 仍绑定窗口最后实际反馈。TargetVersion 按 A.5 的唯一 `motion-target-v0.2` 字节预像生成；新移动/基准失效使当前目标版本不再可用于新的 settled，历史回执保留。不得用接纳时 PositionVersion 要求移动后的 actual 仍是旧版本，否则正常移动永远不能 settled。

`MotionAuthorization` 是可信宿主的用途限定引用，Core 经 `IMotionAuthorizationPort` 校验原 Owner、Scope、命令种类、内容摘要、期限及撤销。UI enabled、调用者布尔值或两个相同 hash 都不是授权。授权刷新在状态 gate 外进行，gate 内只重核已准备的本地验证结果；不得 IO、阻塞或重入。一次 Move 的授权不能用于 Home/Jog/Reset/Recover；模块不自行签发、不持私钥、不带板流或质量语义。

普通副作用命令先查幂等账本，再校验完整前置条件。使用外部变换/误差图的坐标请求必须携带 `CoordinateAssetSha256`，摘要纳入 canonical request；坐标资产 Owner 负责内容，Core 只按固定版本解析并验证唯一结果。直接机器轴 Frame 与能力一致、无外部变换时该字段为 null，由能力摘要/基准版本绑定；不调用坐标端口。OneSided 或 ControllerQualified 还必须提供相应用途的资格资产。所需资产缺失、过期、多个候选或单位冲突分别返回 `MOTION_COORDINATE_INVALID` / `MOTION_COORDINATE_AMBIGUOUS`，不调用设备。

Stop/取消停止和 Close 的紧急收敛路径使用 `StopRequest` 的原 Controller/Boot/Generation、Owner、Scope、可选原 OperationId 与 StopId，不要求 Ready、Homed、旧轴 CAS、当前坐标/配置可用或普通 Move 授权仍有效。它只收敛原 Owner 已取得的资源，不能借停机请求夺取其它设备。若旧身份已经不对应当前连接，隔离原 Owner 并查询原 operation，不向新设备盲发；硬件安全链不受软件身份校验限制。Drain 和联锁事实同样不依赖位置映射；不得以普通运动验证阻断它们。

`CancellationToken` 不进入请求正文/hash。普通命令接纳前取消返回 Rejected，零设备动作；接纳后取消发起原 operation 的 Stop/Drain，由内部独立且有限的清理预算执行，不能把已取消 token 传给 Stop。取消只读等待/订阅只取消该读取者，不停止其它宿主的运动。

Stop/Close/CompareCancel 的 ct 只取消调用者观察，不撤回原资源收敛；入口先核原身份/所有权，再以内部清理预算执行。已取消 ct 不能成为遗失原操作 Stop 的理由。普通 CancellationToken 回调只设置取消意图/唤醒 priority actor，不在回调或状态 gate 中同步执行 SDK/ledger/宿主回调。

### 3.3 输出、实际反馈和 settled

`MotionOperation` 是某一 revision 的不可变回执，不是 SDK task 或租约。分别记录 `Acceptance`、`ExecutionState`、`DrainState`、`ResourceState` 和 `DeviceReconciliationState`；返回 Draining/Unknown 回执不代表终态。每轴同时保留 start/target/controller-command/encoder-actual，字段不可测用 null + Quality=Unavailable；不以命令位置补编码器 actual。位置附带单位、Frame、轴方向约定、坐标/校准资产摘要、Boot/Generation/ClockEpoch、PositionVersion、设备 tick/序号和接收时单调时间。

`MotionStatusSnapshot` 包含每轴 Homed/Servo/InPosition/限位/Fault/速度/following error、联锁快照和新鲜度。State 是轴/Scope 投影；控制器聚合 Ready 只在全轴所需事实完整时成立。一个无关轴未知不伪造整机 Ready，也不必阻断设备已声明可隔离的其它 Scope；若安全联锁为控制器级，则影响全 Scope。`Holding` 必须有实际静止与设备保持事实；只发 Stop 或 ACK 时状态仍为 Unknown/停止待确认。

settled 采用原始、连续、同域反馈，逐轴判定，禁止将 mm 与 deg 混成欧式误差。对每轴 i：
`abs(qActual_i - qTarget_i) <= PositionTolerance_i`，
`abs(vActual_i) <= VelocityTolerance_i`，
`abs(followingError_i) <= FollowingErrorTolerance_i`；
同时 Servo/Homed/InPosition（按能力声明是否必需）、无故障/限位/失效联锁。边界使用 <=，容差均由批准 Profile 显式提供且不小于可分辨下限。任一字段缺失不能把条件视为真。

同 Boot/Generation/ClockDomain/Epoch 的有效样本从首个合格 tick 起连续满足 Dwell；至少两个不同序号，样本间隔 <= MaxSampleGap、反馈年龄 <= MaxFeedbackAge，整组采样偏斜 <= MaxAxisSkew。重复样本不增加窗口；越界、倒序、缺口、轴集合不全或 epoch 改变清空窗口并返回明确原因。设备 tick 用 capability 的 TickFrequency 转时长；Adapter 必须声明已展开计数器，回卷不能由 Core 猜。跨时钟轴仅在坐标/时钟 Owner 提供带版本和不确定度上界的固定映射后组合；含不确定度的最坏间隔/偏斜仍须满足 Policy。不能使用主机轮询到达时间、UTC 校时、sleep 或首尾两点插值替代设备连续区间。

反馈年龄同时检查接收后年龄和设备采样时刻映射到主机单调域的最坏年龄，避免迟到旧帧一收到就“新鲜”。主机域固定为 `host:` + SessionId、epoch=SessionId、Frequency=注入 TimeProvider.TimestampFrequency；ClockMappings 提供该域的有界历史映射，不靠第一次收包对齐设备时钟。无适用映射或不确定度已超过 MaxFeedbackAge 时，硬件反馈不可用于 settled/PhysicallyStopped，不编造延迟界；Simulator 的 fixture 显式给 1000 device ticks/s→10000000 host ticks/s、同零点的有理映射。未来映射出的样本同样无效，不用负年龄补成 0。

`SettledEvidence` 绑定 OperationId、目标/最终位置版本、PolicySha256、CoordinateAssetSha256、连续样本起止 tick/序号、Boot/Generation/Epoch、实际最终位置及逐轴最大误差/速度/跟随误差。过去的 settled 不授权未来触发：再次移动、复位、坐标失效、断线或 epoch 变化时，当前状态的 SettledEvidence 失效；历史回执保留原样。曝光区间封存、MotionActual 产品 Schema 和采集许可由宿主/相关 Owner 另行接入，不在这里增加采集 API。

## 4. API 入口与事件时序

唯一入口为附录 A 的 `IMotionSession`；具体方法、DTO、端口和回执全部在那里定义。Core 的 `MotionSession` 实现此接口。同步 Get 只读不可变缓存，异步 Get 可等待有界设备读回；查询结果携带质量/新鲜度，不因读失败改写最后可信样本。副作用方法有界返回当前回执，最迟到调用 Deadline；若 native/停止/排空仍未确认，返回 Pending/Unknown，Owner 继续持有真实 task，宿主用 QueryOperationAsync 查询。WaitForSettledAsync/WaitOperationAsync 为纯等待，取消等待不取消原 operation。

比较触发登记、撤销、Servo 使能/失能、相对位移、轨迹提交、Jog 心跳和 Close 均有公开入口；功能 Unsupported 在设备调用前拒绝。EmergencyStopFact 不接受任意宿主调用：EStop 仅来自注入的可信 `IMotionInterlockPort` 或 Adapter 反馈；模块没有软件冒充物理急停的公共命令。

未接纳路径为 `RequestReceived → RequestRejected`：无 Operation reservation 时 OperationId=null，DeviceCallMade=false，不伪造 Draining。已接纳事件按每 OperationId 的 OperationEventSequence 单调递增；EventSequence 则是同一 Session 流的全局单调序号：

1. Accepted：已预留账本、Scope 和完整资源；尚未提交设备。
2. CommandIssued：设备提交成功或结果未知；精确标记 DeviceCallMade 和控制器序列。
3. FeedbackChanged；适用时 SettlingStarted → Settled / NotSettled。迟到旧 epoch 仅作诊断。
4. LogicalCompleted / LogicalPartial / LogicalCancelled / LogicalTimedOut / LogicalFailed：执行结果或停止后逻辑意图固定，仍非 operation 终态。
5. Draining → Drained → ResourcesReleased → 一次 Completed / Partial / Cancelled / TimedOut / Failed；只有本 operation 的 native task、回调、临时缓冲、轴独占资源均已收敛且设备结果可对账才发终态。Drain 超时保持 Draining/DrainUnknown，无 ResourcesReleased 或伪终态；实际回执经原 revision 继续推进。

Move 的 ResourcesReleased **仅释放本 operation 资源**，不关闭会话连接、全局反馈订阅或共享账本；控制器写 Owner 保持到 Close。Close 的同名事件才覆盖会话自有连接/订阅。借用的授权/账本/坐标/诊断端口不被 Dispose。Compare 登记持有独立 RegistrationId 和登记资源，操作回执完成不等于登记已撤销；Close 必须逐登记撤销并确认。

事件投影含 SessionId、OperationId（会话事件可空）、AxisScope、SessionRevision、Boot/Generation、EventSequence/OperationEventSequence、Timestamp、来源和回执 revision。反馈投影可合并，事实/终态先保全到同一 ledger，再送事件通道；慢订阅者超上限以显式 EventGap 结束该订阅，可查询 ledger，不允许运动线程阻塞等待 UI。不在设备锁内执行宿主回调。

## 5. 状态机与错误语义

轴状态主路径为 Unknown → Initializing → NotHomed → Homing → Ready → Moving → Settling → Ready。会话另有 Created/Open/Closing/Quarantined/Closed 生命周期，不用轴状态表示 Dispose。状态只由 Core 接收的实际反馈与原 operation 推进，Adapter 不直接写 Core StateVersion。

| 当前轴态 | 允许的普通命令 | 可判定结束与恢复 |
|---|---|---|
| Unknown/Initializing/Disconnected | 只读、可信联锁事实、原 operation 查询；恢复读连接后仅可按 §17.3 对账；Open 只用于 Created 或已确认 Closed 后的新实例 | 缺字段保持 Unknown；不得自动重发，未对账前不执行解锁/复位 |
| NotHomed | Home、按批准维护策略 EnableServo；维护 Jog 仅在能力提供无基准点动模式和专门机械包络时允许 | Home 原点/Index/基准提交全部证明后到 Ready；普通绝对/相对/轨迹移动拒绝 |
| Ready | Move/MoveRelative/Trajectory/Jog/Compare/配置；Home 需单独维护授权且先停稳 | 实际移动到 Moving；静止空位移仍形成可追溯回执，不能省略 settled |
| Homing/Moving/Settling | 只读、原 operation 查询、Stop、Compare 撤销；其它写命令 Busy，不隐式 blend/preempt | 完整连续证据才 Ready；停止确认且保持事实才 Holding |
| Holding | Reset（设备故障需清除时）、Recover；不得直接 Move/Home 退出 | Recover 重新核联锁、轴静止、可信基准、无未知 operation 和控制器 stop-lock 已释放，才 Ready；基准失效则 NotHomed |
| Interlocked/Faulted/EStopped | 只读、Stop、维护 Reset/Recover（先满足安全 Owner 的复归事实） | Reset 不释放安全链，不自动 Ready；基准失效至少 NotHomed |
| 任意态 | 原资源 Stop、联锁/EStop 事实、Drain/Close | 未有物理静止证据保持 Unknown；不能发 Holding 掩盖未知 |

多个事实同时到达时保留所有标志；显示优先级 EStopped > Faulted > Interlocked > Disconnected > Unknown > 工作态。该优先级只决定投影，不丢失状态原因，也不以故障码自动放行。

错误对象为附录 A `MotionFailure`。Retryable 仅表示修正原因后能否提出新**已证明未发出**请求；从不许可重复未知物理动作。DeviceCallMade 是回执事实，PossiblePhysicalEffect 单独表达提交未知。

| 稳定错误码 | 语义与恢复 |
|---|---|
| MOTION_INVALID_ARGUMENT | 空输入、重复轴、单位/范围/非有限数/组合错，接纳前零设备动作 |
| MOTION_STATE_CONFLICT | Scope 版本或 Session 配置过期；查询后重建未发出请求 |
| MOTION_COORDINATE_AMBIGUOUS / MOTION_COORDINATE_INVALID | 多候选或资产缺失/失效；拒绝位置命令，Stop/Drain 不受阻 |
| MOTION_NOT_HOMED | 没有可信基准；不以编码器绝对数值冒充机器坐标 |
| MOTION_CAPABILITY_CHANGED | boot/firmware/轴映射/hash 变化；隔离旧请求和坐标依据 |
| MOTION_LIMIT_VIOLATION | 预检时零设备调用；运行中触发则保留真实 DeviceCallMade 与位置、停止证据 |
| MOTION_INTERLOCK_OPEN / MOTION_INTERLOCK_UNKNOWN | 已打开或过期/缺失/矛盾联锁；阻断影响 Scope 的普通命令 |
| MOTION_AUTHORIZATION_INVALID | 权限引用不可信/撤销/过期/内容错；不阻止原 Owner 停止 |
| MOTION_CONTROLLER_UNAVAILABLE / MOTION_CONTROLLER_BUSY | 连接不可用或 Scope/控制器 lease 被占；不得自动抢占 |
| MOTION_COMMAND_REJECTED / MOTION_UNSUPPORTED | 控制器明确拒绝或无所需能力；Unsupported 必须零下发 |
| MOTION_TIMEOUT_UNKNOWN / MOTION_CANCELLED | 超时未知或取消意图；分别查询原 operation 和停止证据 |
| MOTION_NOT_SETTLED / MOTION_SETTLE_TIMEOUT / MOTION_FEEDBACK_GAP | 不合格窗口、等待超时或时序缺口；不产生稳定事实 |
| MOTION_FOLLOWING_ERROR / MOTION_DIRECTION_UNKNOWN | 跟随误差或要求的接近方向不可证；停止/拒绝按发生阶段处理 |
| MOTION_DUPLICATE_CONFLICT | 同授权域/Owner/CommandId 正文不同；无第二动作 |
| MOTION_RESOURCE_LIMIT / MOTION_LEDGER_UNAVAILABLE | 限额/原子账本不可用；普通命令未提交，Stop 走预留收敛通道 |
| MOTION_DRAIN_TIMEOUT / MOTION_RELEASE_UNKNOWN | native 未排空或资源归还失败；保留原 Owner，隔离且可继续查询/Close |
| MOTION_DIAGNOSTIC_SINK_FAILURE / MOTION_ADAPTER_FAILURE | 诊断降级或设备适配异常；不以日志/异常生成 Success |
| MOTION_EVENT_GAP / MOTION_SCHEMA_UNSUPPORTED | 慢订阅缺口或不支持回执/请求版本；查询原记录或显式拒绝 |

### 5.1 取消、停止、超时和恢复

Stop 区分 StopRequested、StopAccepted、PhysicallyStopped、ControllerStopLockReleased、NativeDrained 五项证据；Stop ACK 不代表轴停，轴停不代表控制器允许新命令，worker 退出不代表设备已停。Holding 只表示保持已确认，退出保持必须经过 Recover 和设备 stop-lock 释放回读，不能把软件取消等价急停。

PhysicallyStopped 使用 RuntimeProfile.StopPolicy 对原 Scope 的全部轴判断连续速度窗口，采用 §3.3 的同域/序号/间隙/年龄/偏斜规则，但不要求目标到位、Homed、Servo、InPosition 或坐标资产有效。PositionHeld=True 的新鲜设备事实与完整静止窗口同时成立才可投影 Holding；stop-lock 释放必须逐轴回读 ControllerStopLockActive=False，未知不能代替 False。StopEvidence 绑定 StopId/原身份/Scope/Policy/控制器序列和窗口 Witnesses；Core 重新判定窗口，不信任 Adapter 单个 PhysicallyStopped=True。NativeDrained 只能由持有真实 task/回调的 Owner 证明。Recover 经 Adapter 的显式维护命令解除控制器锁后再回读，不能仅改软件状态。

operation Deadline 从首次接收单调时刻开始，不在排队、查询/重试或子段之间续期；停止/排空的 CleanupBudget 另由批准 RuntimeProfile 给定。deadline 到时停止新普通命令，Stop/查询原请求，返回 Unknown/Draining 快照；清理实际 task、回调和 lease 仍由原 Owner 保管。取消/超时等待的包装 task 完成不释放其底层 task。

断线或进程重启从 Unknown 重新只读建立身份/能力/反馈；原账本未决不重发 Move/Home/Jog/Compare/配置/Servo。同 operation 原生任务迟到，仅在相同 boot/generation/session/axis operation token 下更新原回执，不覆盖新代或已固定终态。关闭失败由注入的 `IMotionLifecycleOwner` 保留强引用及 RetryClose 入口；不得丢弃 await using 后的未知设备责任。重新连接不是旧资源自动归还证明。

## 6. 资源、线程和并发

- 每个物理控制器有跨进程单一命令 Owner；同一进程内每个轴组/轴命令按资源键串行。`Stop`/急停事实优先于普通队列。若宿主无法证明多个进程共享同一个 Gateway/租约协调器，第二实例必须拒绝连接写通道，只允许标明新鲜度的只读访问。
- `ResourceLimits` 必须在打开硬件写通道前从能力和经批准的部署 Profile 合成，并固定 revision/hash；每项上限均为正有限值。任一上限缺失、互相矛盾或过期时拒绝写通道。请求超过轴数、轨迹样本、在途数、命令队列、反馈率、事件积压或保留内存上限，返回 `MOTION_RESOURCE_LIMIT`，且不得占用设备或静默截断轨迹。
- 轨迹整体先验证坐标帧、每点单位/范围、采样间隔、速度/加速度/jerk、总点数和完整路径边界，再原子登记和提交。同步插补只允许能力明确的 AtomicGroup；IndependentSerial 是调用方显式选择的非同步逐轴定位，不冒充插补。每轴回执、已发生运动和停止结果分别返回，禁止声称跨轴物理回滚。
- Gateway/Adapter 拥有 SDK 句柄、连接、订阅、命令队列和原生缓冲；Core 不暴露句柄。Core 在接纳时对请求集合/字节作有界不可变复制，之后调用者改草稿不改变正文/hash。结果为不可变值，无隐藏 Dispose 租约；连接和订阅仅在 Session Close 释放。
- 反馈线程只做有界解码、序列校验、状态提交和有界排队；不阻塞等待宿主或 UI。CPU 密集计算在独立调度器执行。积压达 `MaxEventLag` 时先合并可合并的状态投影；命令/终态/互锁/EStop 事实不得丢弃，无法保留时转 `Unknown`、停止接受普通命令并报告资源错误。
- 事件通过宿主提供的调度器发布；默认不保证 UI 线程。WPF 控件自行切换 Dispatcher，核心不引用 Dispatcher。
- 同一实例允许并行只读查询；两个实例的取消、语言、缓存和事件不得互相污染。两个实例不能共享可变静态状态。
- `CloseAsync` 先关闭普通准入、撤销 Compare 登记并确认、Stop 所有活跃 Scope、排空 native/回调，再释放自有订阅/连接和控制器 lease，状态变 Closed；借用端口不释放。`DisposeAsync` 调用相同 Close，失败抛含 SessionId 的 `MotionDrainException`，先把本 Session 交给 LifecycleOwner 保留，状态 Quarantined。再次 Close 幂等续做未完阶段；关闭完成后查询原账本允许，其它写入口返回已关闭失败；读缓存仍带旧身份/年龄，异步设备读返回不可用。强杀进程只可能证明进程级 OS 资源退出，不证明物理停止、设备对账或 motion 终态。
- 每控制器在 Open 时预留独立 Stop/联锁收敛容量和 CleanupBudget，不与普通 MaxQueuedCommands 竞争。账本运行时失效、普通队列满或普通权限撤销时仍允许原 Owner 向原连接请求 Stop；停止意图使用稳定 StopId 及预留容量尽力保全，账本未知则回执标 LedgerUnknown，禁止普通重试或成功终态。持久账本恢复后只补记原 Stop 事实，不再次发送运动。

## 7. 适配器、能力实施卡与模拟器

`IMotionAdapter` 端口完整形状见附录 A。构造 MotionSession 时显式移交未打开 Adapter 的所有权；Open 指定固定 ControllerId，不自动发现、选择第一台或隐式打开设备；所有 Open 只连接/读事实，不隐式伺服使能、回零、复位或改输出。每实例返回 AdapterIdentity、固件/SDK 运行时指纹、Boot/Generation、能力和时钟信息；能力 Unsupported 在调用前拒绝。厂商地址、句柄、寄存器、线程和脉冲转换只留 Adapter。

### 7.1 单轴/轴组绝对与相对定位

Move 顺序为幂等查询 → gate 外解析固定资产/准备授权 → gate 内预检 → gate 外原子 ledger reserve → gate 内 Scope CAS/完整资源取得 → gate 外耐久提交意图 → gate 内重核并交给原 Owner 的有界提交 actor → gate 外 Submit → 原始反馈 → settled → operation drain。gate 内不执行端口 IO 或用户代码；重核失败保全未发出的回执并归还 operation 资源。相对移动从 Preconditions.Axes 指定版本的**新鲜 actual**冻结Start，Machine Frame直接一次计算 `target = actual + delta`；其它Frame的Delta先由§17.2坐标端口映射再加到Machine Start，gate外完成计算/解析，在Scope CAS时重核原版本。冻结 Start、原Delta 和 ResolvedTarget 到原 ledger。解析期间版本改变就拒绝，不悄悄重算后复用授权；同键重查原 target，不再次加 Delta，不从上次命令目标累加。

零位移仍需授权、前置和实际窗口；允许不下发位移命令，但保留 DeviceCallMade=false 的 operation 与 settled 回执。空 Scope/Delta、重复轴、轴组缺项、非有限和加法溢出零下发；超过资源上限完整拒绝，不截断集合。AtomicGroup 仅设备声明支持时一次提交，部分 ACK/轴接受为 Partial/Unknown 并请求整组 Stop。IndependentSerial 的顺序是能力轴组的固定顺序，逐轴确认并记录，每轴都不宣称同步；调用方显式接受该模式，核心不自动降级。

Trajectory 只消费宿主给定的有限时间化折线：每点含完整轴值与从起点算的 TimeSpan Offset，Offset 严格递增，第一点 Offset=0 且与冻结 Start 一致，末点为 Target。无平滑隐式插入、不做扫描优化；控制器拥有批准 Profile 的实际插补。Core 对全部段和声明的插补轨迹包络核软限位/禁区、每轴单位/动力学界，插补器可能超越折线包络时必须有 Adapter 验证证明，否则 Unsupported。未知 jerk 或包络不以端点合格替代；方向反转、拐角速度和停止距离也需能力/机器 Profile 给出。到期未提交段不再发送，已提交段逐项对账。

### 7.2 方向、回差与坐标事实

坐标端口输入完整 Start/目标或轨迹、Frame、资产摘要与每轴请求的 ApproachPolicy；输出唯一机器域路径、禁区验证、映射摘要和每轴接近方向。不自己标定或修改补偿资产。每轴能力明确 EncoderPositiveSign（+1/-1）、PositionResolution、反馈坐标约定；正负方向由已展开 actual 增量超过可分辨阈值的样本证实，零/抖动不翻方向。direction history 绑定 Boot/Generation/基准与配置版本；Home、Reset、掉电/断线、触限位或方向反馈不可信后置 Unknown。

主路线为 None：不额外做回差动作，记录实际最终方向和补偿来源；ControllerQualified 表示控制器已按批准资产补偿，Core 不重复补偿。需要精确单向接近时，显式 OneSided policy 由坐标端口返回 `preTarget = target - signedApproachDistance` 及 preTarget → target 的完整两段机器路径；批准距离必须大于已测回差及其不确定度，最终段 Profile 也显式提供。整条路径、额外轴资源、预算和最终方向在接纳前冻结/预检/授权；preTarget 越限或禁区、方向未知、资产不适用均拒绝，不能静默取消预接近或改成另一侧。算法不写 EncoderActual；`CompensatedCommand` 与原目标/编码器 actual 分开回执。方向相关误差图由资产 Owner 提供，现场重复性与正反向误差是外部门；没有实测不能声称“消除回差”。

### 7.3 Home、Servo、配置与恢复

Home 使用每轴批准 HomePolicyId/Sha256、模式、搜索方向/速度/加速度、搜索范围、期限、所需原点/Index 事件及基准提交规则。设备执行具体搜索顺序；Core 核能力与维护授权、搜索机械包络，接收 HomeEvidence 的事件顺序、原点/Index（按模式所需）和实际基准提交版本。原点开关最终电平不必为真，须以批准回零程序的 latch/离开/Index 证据判断；不能把所有模式统一为“最后原点位为真”。AbsoluteReference 模式仅设备明确支持并能证明绝对编码器基准资格时适用。失败保持 NotHomed/Unknown，不无限重试或按单个限位自动反向；有批准 BackOff 只由新的受控维护请求实施。

HomeEvidence 的 SwitchLatch/IndexLatch/ReferenceCommit 是同 Boot/Generation/clock epoch 的事件时刻，必须位于 Start–End；SwitchThenIndex 要求 switch <= index <= commit，Switch/Index 按对应所需事件 <= commit，缺 latch 或反序拒绝。AbsoluteReference 不伪造开关/Index，只接受设备资格资产和实际 ReferenceCommit/基准 revision；SearchDirection 可 Unknown 且不得发搜索动作。Core 根据 ReferenceOffset 建立新的目标/位置版本，再用实际编码器和 Home.Settled 判断；设备返回“Done”不跳过窗口。

EnableServo 只在能力、联锁和维护权限满足时执行并回读；DisableServo 前必须 Stop 和确认静止，不能从 Moving 直接失能引起未定义物理动作。状态无法观测返回 Unknown。AxisConfigurationDraft 仅软限位和普通运动默认草稿，带 BaseRevision；默认值仅存配置，**请求仍显式提供 Profile**。完整字段组先校验，再逐字段写入/回读，Applied/PartiallyApplied/Unknown 逐字段返回；部分写入使配置 revision 不可用于新运动，保留已写字段，不能声称物理回滚。安全参数、伺服整定、电子齿轮仍在厂商/维护专项边界。

Reset 清故障不证明基准、安全或 stop-lock 已恢复。Recover 是有授权的显式对账：查询原未决请求与 ledger、确认实际静止、联锁/基准/控制器锁/版本，写新的对账回执后开放相应 Scope；确认不足保持隔离，禁止以重连或“忽略故障”恢复 Ready。

### 7.4 Jog、保持和比较登记

Jog 是一轴有界持续命令：方向、Profile、MaxDuration、HeartbeatTimeout、Owner 和专门维护授权均必需。心跳 `JogHeartbeatAsync` 绑定原 OperationId、Owner、Boot/Generation 和递增序号，只延续该 operation 的 deadman，不延长从接纳开始的 MaxDuration；重复/倒序心跳不续期。失焦、松键、失去捕获、权限撤销、心跳缺失、反向按键冲突或断连均 Stop。禁止键盘自动重复创建新 Jog，不能排队正向/反向两个命令。方向切换先 Stop/静止/排空，再新 ID 开始；Core/Adapter deadman 不能只靠 UI。设备停止上界和机械包络仍须 HIL。

CompareTriggerRequest 明确单轴、OutputChannelRef（信号 Owner 的不透明引用）、有序位置表、方向、迟滞、登记 revision/hash、能力时钟域和期限。Core 只登记/撤销，不能设置未定义的电平或脉宽。有限位置、方向排序、重复点和容量先校验；返回 RegistrationId、Loaded/Active/Exhausted/Cancelled/Unknown 及实际设备回执。已装载不等于触发，单纯 API 接受不等于激活。Home/Reset/代际/坐标变化使登记不可复用，先阻断后续动作并经原 RegistrationId 撤销/对账；已发生输出无法回滚。Compare 撤销不受普通位置 CAS 阻挡，Close 必须能证明旧登记不再产生输出。

### 7.5 联锁端口与模拟/Replay

`IMotionInterlockPort` 只读提供可信 SafetySourceId、Boot/Epoch、递增 Sequence、受影响 Scope、门禁/急停/允许运动三态（True/False/Unknown）、单调采样时刻与批准 freshness；不提供安全旁路或放行 API。Core 将权限/设备/联锁当前事实在同一准入点核验；安全输入异步变化立即关闭受影响普通准入并请求 Stop。旧序列、来源不符、缺失、过期或与 Adapter 矛盾为 InterlockUnknown，不能认为关闭就是安全。读端口/订阅失败也收敛写通道；硬件安全链自身 Stop 不等待 Core。

SimulatorAdapter 使用 A.7 冻结的脚本式 `SimulationPlan`，固定 Seed、Capability、初始反馈、有限 FaultSchedule 和虚拟时钟，不加载厂商库、不打开设备。每个 FaultInjection 绑定调用 ID 或样本序号，覆盖拒绝/部分接受/ACK 丢失、重复/迟到、设备不动而 ACK 成功、噪声/量化/方向反转/回差、时钟跳变/回卷、反馈断流/单轴缺失、联锁变更、断线/重启、native 永不返回、释放失败。轨迹、反馈扰动均由脚本给定，不声称模拟控制器动力学或自行生成默认运动曲线。虚拟 Advance 只推进模拟；相同计划/时间推进/闩锁顺序应产生相同事实与 ledger 回执。

ReplayAdapter 只读固定 capability + 原反馈集合 + 原 operation/Schema/哈希（A.7）；不能接受 Move/Home/Jog/配置/Compare/Stop/Reset/Recover。Replay 的 WaitForSettled 从只读 replay ledger 取得历史目标/版本，再核原反馈连续区间，输出 Source=Replay，不创建新移动。缺样、过大、版本不支持和哈希错显式拒绝；加载既有记录不改变物理状态。

### 7.6 Mosaic 首行线扫只读桥（Motion Read Bridge v0.1）

`mosaic` 的 `FirstLineEncoderTranslationMeshV1` 是本模块已确认的窄消费者：它只读取首行曝光关联所需的 XY 实际反馈、时钟映射和本 run 动态包络证据，禁止发 Move/Home/Jog/Stop/Settled/Compare 或修改 Motion 事实。现有 `RawAxisSample`/`AdapterFeedback` 可作为源记录的实际值和原始 `ClockStamp`，现有 `AxisFeedback.PositionVersion` 可作为位置版本；但它们没有有界历史读取、同步 XY 成对采样、连续序列/缺包证明和 run 适用动态证据。因此冻结下面的增量只读桥。既有 Core Contract v0.2、46/47/102-byte codec 向量和 S1/S2 `ModuleCoreImplementationReady` 不变；本桥自身为 `Motion Read Bridge v0.1`、本桥已接收准备基线为 `0.2.4-prep`，当前全范围修订见 §17，六项文档规格已获主控接收为 `ModuleCoreImplementationReady`（仅准备），不提升整模块、真实来源/SDK/物理资格或产品集成状态。mosaic消费者接线由其永久原会话后续处理，本模块不修改mosaic或共享文件。

桥由 Motion Owner/Adapter/Gateway 提供，`mosaic` 只能借用已绑定桥实例。桥的来源闭包必须同时绑定 `BridgeId`、`SessionId`、`OwnerId`、`ControllerId`、`BootId`、`Generation`、`SourceKind`、`CapabilitySha256`、`ReadContractVersion=motion-read-bridge-v0.1` 和源时钟 `Domain/Epoch/Frequency`；每个读取结果、样本、缺包证据和动态证据回显同一身份。读取范围、输出数量和证据摘要由桥冻结并有界复制；桥不持有质量、曝光、图像、标定或运动命令 Owner。

桥只接受 `ReadOnly` 读取用途；Owner/Scope/Controller lease 和权限由可信宿主预先绑定，不能由 mosaic 请求临时扩大。桥执行时先核当前 Boot/Generation/Capability/源时钟，再交给单一只读源读取；任何变化、撤权、关闭或桥身份不符都返回 `Unknown`/`NotSupported`，不把旧缓存补成当前事实。源必须提供两个轴同一真实采样 tick/sequence 的成对记录；不能从两个不同 `ClockStamp.Tick`/`Sequence` 的轴记录拼 XY。输出只接受 `RawAxisSample.EncoderActual` 或等价已核验 actual，不接受 `ControllerCommand`/`Target`/`CompensatedCommand` 代替；X/Y 的 `PositionVersion` 必须分别存在。动态速度/加速度不能由命令 Profile 或离散差分自证，必须原样回显外部 Owner 对该 run/clock 区间发布的证据；桥只核身份、范围和版本，不授物理资格。

`MotionReadBridge` 的所有读调用均受请求的单调 Deadline 与 `MotionReadLimits.MaxObservationWait` 较小者限制；调用取消只取消观察，不取消源 task。迟到源 task、回调、缓冲和映射查询由桥的原 Owner 继续强持，独立 cleanup 只收敛该 readId 的资源，不能关闭 Motion Session 或影响其它读者。重复相同 `ReadId + RequestSha256` 返回同一只读结果/正在进行的同一 task；同 ReadId 异摘要冲突，绝不重新读取。关闭先拒绝新读、等待/取消本桥读者、清理映射订阅和输出缓冲，再返回 `Released`；未收敛保留桥实例与原 task，返回 `Unknown`/`DrainUnknown`，不得用 await 包装 task 完成冒充源释放。

## 8. 可选 UI 契约

这是既有可选运动控件，不新增产品生产页。观察者只能看轴/回执；定位角色提交一次明确 Move；维护角色执行 Home/Jog/Servo/配置/恢复。Core API 全部可无 UI 调用，控件只接借用 Session、宿主请求生成器和语言/主题上下文，不直接打开 Adapter、签发授权或创建 ledger。

### 8.1 1920×1080 工作台构图与 DevExpress 组合

唯一验证屏幕为 1920×1080。测试窗口在该 viewport 内扣除实际 OS 任务栏、窗口边框、标题栏后，以剩余客户区布局；不得按整屏像素假装可用空间，也不更改用户显示。顶部命令带 48 DIP、底部状态带 28 DIP；中间 `DockLayoutManager + LayoutGroup/LayoutPanel`：左轴树 18%、中央状态/轨迹 54%、右动作/参数 28%；下方可缩放诊断区初始占中间高度 28%。轴/停止/当前未知状态面板 AllowClose=false、AllowFloat=false；只有诊断/高级参数允许折叠，恢复布局是只读布局操作。运行 Jog 时禁布局定制，不能让拖动隐藏停止入口。

| 区域 | 已核对 25.2 控件/成员 | 具体数据与联动 |
|---|---|---|
| 左侧轴与轴组 | `TreeListControl + TreeListView` | Controller → Group → Axis；显示单位、Homed、限位与状态文字；选组联动整组，选单轴不隐式继承其它轴；未知/不支持有原因 |
| 中央反馈表 | `GridControl + TableView` | 固定轴、Actual、Target、误差、速度、方向、反馈年龄、状态列；Actual 优先、目标次级、单位靠数值；排序/筛选只影响投影 |
| 中央时序 | `ChartControl + XYDiagram2D + LineSeries2D`；`ChartControlBase.CrosshairEnabled` | position/target、velocity、following-error 分图，共享设备时间轴；mm 和 deg 不混 Y 轴；光标联动下方事件和原样本，不以平滑线冒充反馈 |
| 右动作/草稿 | `PropertyGridControl.SelectedObject` | 显式白名单草稿及按能力分组的 Profile；校验显示单位/范围/来源；编辑不写设备，应用显示逐字段回读与部分失败 |
| 下方诊断 | `GridControl + TableView` | 操作/阶段/序号/时间/原码/恢复文字；选 operation 将曲线和轴表冻结到该回执，明显标“历史”，返回实时只改变视图 |
| 辅助说明 | `SuperTip`；`DevExpress.Xpf.Editors.Flyout.FlyoutControl` 的 IsOpen/PlacementTarget | SuperTip 给权限、限制、失效条件和下一步；Flyout 展示“为何不能移动”的字段差异，停止/故障恢复不藏于 Flyout |

色彩跟随宿主局部主题：普通反馈中性色、目标虚线、运行蓝色、需处理琥珀、故障红色、未知灰色加文字，不能只凭颜色；不把 Ready 显示为“安全”。正文 14 DIP、数字 16 DIP、主 Actual 20 DIP，8/12/16 DIP 间距；长轴名省略可提示，动作按钮随语言内容自适应并换行，不压缩停止。图表仅可视环形缓存，MaxVisibleSamples/HistoryRows/RenderPeriod 来自 MotionUiProfile；显示可抽稀保留 min/max 和缺口标记，Core settled/历史证据不抽稀。停机、互锁和未知结果即时更新，普通数值按 RenderPeriod 批量 Dispatcher 提交；暂停图表不暂停设备或隐藏最新故障。

### 8.2 安全操作链、键盘、三语和恢复

定位：选 Scope → 编辑草稿目标/明确 Absolute 或 Relative → 显示 Frame/资产、当前版本、解析全路径/额外回差段和预算 → 获取宿主该用途授权 → 用户确认“移动” → 锁住本草稿并显示 OperationId → 跟踪实际/settled/排空。任何版本或参数变化使旧预检/授权失效，不能以确认时旧值重新下发。轨迹预览、读程序、切页/语言、展开树、导出诊断均零物理动作。

路径预览调用 Core.PreviewAsync，以 ProposedCommand 的 Move/Relative/Trajectory 完整草稿取得 MotionPreviewResult；它复用同一数值/坐标/路径预检，零 reservation/运动提交，不签发授权或改变状态。UI 展示返回的 Start/全机器路径/额外接近段、版本和意图摘要（排除授权引用），宿主生成最终用途授权后仍由正式 Move 再核全部准入。Preview 不要求已有 Move 授权，读取权限由借用 Session 的宿主接入控制；不能凭 IsValid 绕过普通命令授权。原参数/版本与最终授权改变使预览失效，须重新显示确认。设备不支持预检时显示明确原因，不虚构“路线通过”。

点动只在选定一轴和批准速度下按住：鼠标捕获或有焦点按键创建一个 Jog；松开/捕获丢失/失焦/窗口卸载/撤权/断连立即发同 Owner Stop。键盘 Space 仅在点动按钮焦点下作为 deadman，自动重复忽略；同按正负向立即停，不排队。Tab 顺序为轴树 → 目标/Profile → 预检 → 移动/回零 → 点动 → 停止 → 回执 → 诊断；Enter 在参数编辑器仅提交草稿，不启动设备；Esc/Alt+S 请求停止本控件拥有的活跃 Scope，持续显示“停止待确认”直至证据齐全。软件“停止”不标“急停”，不得承诺键盘取代硬件急停。

恢复区列原 OperationId、未确认阶段、最后可信 actual/年龄、设备/boot、所需权限/联锁和下一步。查询、停止、清故障、回零、对账分开；没有事实不能启用“继续移动”。配置部分失败逐字段显示“已写入/未写入/未知”，普通编辑不清掉旧回执。危险 Home/Servo/配置/Recover 执行前确认用途和范围，Stop 无二次确认。

宿主调用 `SetCulture(CultureInfo)` 动态切换 zh-CN/zh-TW/en-US，无模块语言按钮，不改事实/hash。资源覆盖每个状态、字段、单位说明、错误键和恢复项，原厂文本只作附加详情。基准词：
停止/停止/Stop；停止待确认/停止待確認/Stop unconfirmed；实际位置/實際位置/Actual position；目标位置/目標位置/Target position；尚未回零/尚未回原點/Not homed；反馈已过期/回饋已過期/Feedback stale；查询原操作/查詢原操作/Query original operation。
未知 MessageKey 的三语兜底分别为“操作失败：{code}。查询原操作。”、“操作失敗：{code}。查詢原操作。”、"Operation failed: {code}. Query the original operation."，不显示堆栈或含糊“智能恢复”。

公开控件为 `MotionControlView`，WPF namespace 已在绑定节固定：
无副作用默认构造 `MotionControlView()`；公开 `void Attach(MotionViewBinding)`、`void SetCulture(CultureInfo)`、
`ValueTask<DrainResult> DetachAsync(TimeSpan budget, CancellationToken ct)`。
WPF 包的 sealed record `MotionViewBinding` 精确字段为 `IMotionSession Session, string OwnerId, AxisScope AllowedScope, MotionUiProfile Profile, CultureInfo Culture, string ThemeId, Func<MotionUserIntent,CancellationToken,ValueTask<MotionCommand>> CreateCommand, IMotionLifecycleOwner LifecycleOwner`。`MotionUserIntent` 精确字段为 `CommandKind Kind, MotionCommand ProposedCommand, long BindingGeneration`；ProposedCommand 使用 A.2 对应完整强类型请求，是不可变且不可信的编辑草稿，Kind 必须与 CLR 类型相符，只允许普通 MotionCommand。生成器基于草稿取得新用途授权/当前前置，不能隐式更改路径、Scope 或预算；更改这些字段必须重新预检/确认。`MotionUiProfile` 精确字段为 `TimeSpan RenderPeriod, int MaxVisibleSamples, int HistoryRows, TimeSpan DetachBudget`，正有限且受 RuntimeProfile/ResourceLimits 约束。

Open/Close 属宿主，不经过 CreateCommand。控件的 Stop 由已接纳回执中原 ControllerId/Boot/Generation、Binding.OwnerId、Scope 和 OperationId 构造 A.2 StopRequest；CompareCancel 由本控件保存的 RegistrationId 构造，不依赖普通请求生成器、旧授权或当前 CAS。StopId 在每次逻辑停止首次生成后固定，重查/续收敛复用，不重复生成停止操作。控件只停止本控件已接纳的操作/登记，不得因当前选轴而停止别人的资源。

Attach 仅在 Unattached 状态成功，借用 Session 不 Close；每次 Attach 增加本地 BindingGeneration。Detach 先禁普通提交、取消草稿生成和本订阅 → Stop 本控件活跃操作、撤销其 Compare → Drain 明确 OperationIds → 释放控件订阅/Dispatcher 回调。ct 只取消调用者等待，已发起清理沿有限 DetachBudget 继续。失败保留 Binding/原操作映射和查询入口，并交 Binding.LifecycleOwner 保留 Session；成功才可 Attach 下一 Binding。生成/事件/Dispatcher 完成时须比对 BindingGeneration，旧代只保全原操作不写新视图；旧代生成器迟到返回的命令不得提交。DetachAsync 的结果沿用 DrainResult，但 IsReleased 仅表示本控件操作和 UI 资源收敛，不表示整个借用 Session 已关闭。主题/语言/回调不静态共享，慢 UI 不阻塞反馈。

UI 验收后续执行：真实 25.2.3 编译、唯一 1920×1080 viewport、宿主实际 DPI、三语长文本、UIA/Tab/Space deadman/失焦、布局恢复零设备调用、停止可见、慢渲染/Detach 未排空。当前是规格审查，没有运行 WPF 或截图验收。

## 9. 无 UI 最小 Host 与两个消费者

`MotionSession` 构造只保存依赖，不打开设备；附录 A 定义所有依赖参数。测试工程 Hosts/MinimalMotionHost 使用 SimulatorAdapter、内存原子 ledger、明确的坐标/授权/联锁/控制器 lease test ports、TimeProvider 和 LifecycleOwner，不依赖平台 Shell。以下为调用顺序示例，`fixture` 是测试工程明确构造的合成 Profile/请求集合，不是生产默认配置：

```csharp
var session = new MotionSession(fixture.Dependencies, fixture.RuntimeProfile);
try
{
    var opened = await session.OpenAsync(fixture.OpenRequest, CancellationToken.None);
    if (opened.Acceptance == Acceptance.Rejected) return;
    var status = await session.GetStatusAsync(fixture.StatusRequest, CancellationToken.None);
    // fixture 根据 status 构造完整请求；Home 不是构造时隐式动作。
    var home = await session.HomeAsync(fixture.HomeRequest(status), CancellationToken.None);
    if (home.Acceptance == Acceptance.Rejected || home.OperationId is not string homeId) return;
    var homed = await session.WaitOperationAsync(fixture.WaitRequest(homeId), CancellationToken.None);
    if (homed.Execution != ExecutionState.Completed || homed.Drain != DrainState.Drained
        || homed.Resources != ResourceState.Released) return;
    status = await session.GetStatusAsync(fixture.StatusRequest, CancellationToken.None);
    var move = await session.MoveAsync(fixture.MoveRequest(status), CancellationToken.None);
    if (move.Acceptance == Acceptance.Rejected || move.OperationId is not string moveId) return;
    var result = await session.WaitOperationAsync(fixture.WaitRequest(moveId), CancellationToken.None);
    fixture.Observe(result); // Pending 可以没有 Failure；保留原 ID，不盲重发。
}
finally
{
    try
    {
        var closed = await session.CloseAsync(fixture.CloseRequest, CancellationToken.None);
        if (!closed.IsReleased)
            fixture.LifecycleOwner.Retain(session, closed.Failure ?? fixture.PendingCloseFailure());
    }
    catch (MotionDrainException e)
    {
        fixture.LifecycleOwner.Retain(session, e.Failure);
    }
    catch (Exception e)
    {
        fixture.LifecycleOwner.Retain(session, fixture.CloseExceptionFailure(e));
        fixture.NoteCleanup(e); // 保留独立清理失败，不覆盖原业务异常。
    }
}
```

该示例为待绑定工程的语义示例，不是现有可编译 Host。测试 fixture 的 `Observe(MotionOperation)` 保存回执；`PendingCloseFailure()` 返回 MOTION_RELEASE_UNKNOWN；`CloseExceptionFailure(Exception)` 返回 MOTION_ADAPTER_FAILURE 并只记录异常类型、不推断设备已停。两者都填稳定 MessageKey/RecoveryKey 和真实已知身份/副作用标志，未证明零动作时 PossiblePhysicalEffect=true。`void NoteCleanup(Exception error)`是fixture的有界、不抛异常记录入口，保存异常类型和对应清理失败，不记录秘密/堆栈；Host同时返回/呈现业务结果与cleanup结果，suite有任一未归还Session或NoteCleanup记录均非零，不因业务成功吞掉清理失败。生产 Host 不能从合成 fixture 取阈值。所有提前返回、设备异常和关闭异常都走同一 finally/Retain，LifecycleOwner.Retain 必须有界、不抛异常；实现测试覆盖这些路径。第二消费者测试不复制 Core：
扫描工具只提交有限公开轨迹/读取原回执（扫描路线由其宿主准备，不进入本模块）；
定位工具提交绝对/相对目标并消费 SettledEvidence；
维护观察者只读状态，维护权限才可 Home/Jog/Recover。
独立模拟实例的语言/取消/故障不串扰；共用一物理 Controller 时必须经同一 Gateway/lease端口，第二写实例 Busy，不另加载 SDK。打包后的 net10.0 最小控制台与 WPF Host 分别引用本模块包验证，两者不要求产品源码存在。

## 10. 正常、边界和失败案例

| 案例 | 输入 | 可接受结果 |
|---|---|---|
| 正常定位 | 已回零、能力 hash 匹配、目标在软限位内 | `Accepted → CommandIssued → FeedbackChanged → SettlingStarted → Settled → LogicalCompleted → Draining → Drained → ResourcesReleased → Completed`，含 actual 和稳定区间 |
| 幂等重试 | 相同 CommandId 和 canonical bytes | 返回同一 OperationId/回执，不产生第二动作 |
| 维护点动 | 显式 Jog 权限、按住窗口和速度上限 | 按住运行；松开/失焦发送 Stop；停止结果单独确认 |
| 边界位置 | 目标恰在边界、checked 转换无溢出 | 由能力定义是否接受；边界不确定则拒绝，不向设备发命令 |
| 未回零 | Move 请求当前位置坐标 | `MOTION_NOT_HOMED`，不把编码器绝对值当可信坐标 |
| 反馈抖动 | 误差在 tolerance 内但未连续满足 dwell | `MOTION_NOT_SETTLED`，不发稳定事实 |
| 迟到 ACK | deadline 到期后 ACK 到达 | `MOTION_TIMEOUT_UNKNOWN` 或关联原回执；禁止盲重发 |
| 互锁变化 | Moving 中门禁/PLC interlock 丢失 | 记录 Interlocked，停止/保持由安全链和 Adapter 完成，触发许可失效 |
| 断线重连 | boot/generation 改变 | `Unknown → Initializing`，重新能力/状态；不自动重放 |
| 同键异内容 | 复用 CommandId 但目标不同 | `MOTION_DUPLICATE_CONFLICT`，无设备副作用 |
| 排空失败 | Dispose/关闭时回调或 SDK 未退出 | `MOTION_DRAIN_TIMEOUT`，保留资源 Owner 和未知状态 |

### 10.1 场景驱动复审

下面场景是指导的实施检查点。所有参数均须绑定请求、能力快照或批准部署/Machine Profile 的 revision/hash；未给出生产数值时，不允许由开发者临时补值。每项验收同时运行无设备 Simulator 契约测试；它不能代替硬件验收。

#### A. 正常配置与执行

- 输入：完整轴组、唯一坐标帧、配置 revision、目标、运动 Profile、settled policy、权限引用、期限、期望状态版本。
- 来源：机器/维护配置 Owner、坐标资产 Owner、调用宿主和授权服务；能力范围来自当前 Adapter 快照。
- 顺序：幂等查询 → 校验版本/能力/坐标/全路径/资源 → 原子 reservation → Scope CAS/取得整组独占权 → 耐久提交意图/最终准入重核 → Adapter 下发 → 按同一 epoch 接收实际反馈 → 满足 settled 策略 → 记录完成/失败意图 → 排空本 operation 回调、轴资源和临时缓冲（保留 Session 连接/控制器租约）→ 持久终态 → 发终态事件。
- 输出/状态：每轴目标与 actual 分开，回执绑定 request hash、配置/能力版本、控制器序列、settled 样本区间；`Ready` 只在权威反馈支持时发布。
- 恢复/验收：相同输入可重放同一回执；Adapter 每个运动副作用最多一个命令；丢 ACK 后查询原 Operation，不重复位移。

#### B. 空输入与多轴部分成功

- 输入：空轴组/空目标、空轨迹、缺某轴的目标，或控制器只接受部分轴的多轴命令。
- 来源：调用请求和 Adapter 的原子提交能力声明。
- 顺序：空/缺项在任何资源获取和 Adapter 调用前校验；多轴请求先整组校验，再根据能力决定一次原子提交或具名分阶段提交。
- 输出/状态：空输入为 `MOTION_INVALID_ARGUMENT`；IndependentSerial 按冻结顺序，每轴使用 A.1 ExecutionState；IssuedAxes/ConfirmedNotIssuedAxes 与控制器序列区分已发/已证实未发，未证明的轴为 Unknown，总结果为 `Partial` 或 `Unknown`，不得汇总成功。
- 恢复/验收：不做物理“回滚”假设；按已登记策略向整组发 Stop，读取所有轴实际状态，资源保持到各轴排空。注入第 N 轴拒绝时能证明已发出的轴和未发出的轴集合准确。

#### C. 歧义与错误输入

- 输入：同名轴映射冲突、多个可解析坐标变换、frame/单位不匹配、重复轴、非有限数、配置/能力 hash 过期、相同 CommandId 不同正文、负/零期限。
- 来源：调用 DTO、公开坐标转换结果、revision/hash 与能力快照。
- 顺序：规范化输入但不修复语义 → 检查唯一解析/单位/范围/版本/幂等内容 → 失败则返回；不得自动选第一个 frame、按轴名猜单位或舍入越界值。
- 输出/状态：输入错返回 `MOTION_INVALID_ARGUMENT`，映射多解返回 `MOTION_COORDINATE_AMBIGUOUS`，版本错返回对应 Conflict/Changed，全部注明 `DeviceCallMade=false`。
- 恢复/验收：宿主提供唯一有效坐标/新配置后创建新 CommandId；旧请求保持拒绝。逐类断言 Adapter 调用次数为零。

#### D. 超大输入与高并发

- 输入：轴数、轨迹点、在途操作、订阅者、查询速率、事件积压或持久回执字节达到/超过 `ResourceLimits`。
- 来源：当前能力快照与批准部署 Profile 的有限上限；两者合成规则须版本化。
- 顺序：读取完整请求长度并限制解析分配 → 先做限额/checked 运算 → 一次性预留完整资源 → 再进入状态 CAS/Adapter；不可无界排队、分批静默截断或丢弃轨迹尾部。
- 输出/状态：超限为 `MOTION_RESOURCE_LIMIT`，设备未调用；同资源写命令串行，其它请求有界等待或拒绝。只读查询可合并，但快照注明年龄。
- 恢复/验收：负载解除后宿主用新请求重试；上限边界内成功，边界外拒绝；压力测试证明内存、队列和 native 句柄保持 Profile 上限，`Stop` 不被普通命令饿死。

#### E. 噪声、遮挡式缺失与反馈退化

- 输入：编码器量化/抖动、重复或倒序样本、采样间隙、following error 跳变、反馈滞后、一个轴反馈丢失、设备 clock epoch 变化。
- 来源：Adapter 原始样本、设备规格、批准的 SettledPolicy 与 clock mapping；软件不得把通信缺样当“遮挡可推断”。
- 顺序：保留原始样本序号与 tick → 核验新鲜度/单调性/完整轴集合/误差界 → settled 只在同 boot/epoch 的连续有效样本窗判定。可选滤波只用于展示，不参与本契约的控制或 settled；改变实际反馈判定路线须修订契约，不能靠 Profile 静默切换。
- 输出/状态：重复样本标记不增窗口；间隙/epoch 改变返回 `MOTION_FEEDBACK_GAP` 并转 Unknown/NotReady；单轴缺反馈使整组不可 settled。不得用插值、最近值或目标值填补。
- 恢复/验收：重新建立新鲜反馈窗口后重新查询/操作；噪声测试不能令 unsafe 状态恢复 Ready，稳定边界与样本缺口反例结果确定。

#### F. 取消、超时和 native 排空

- 输入：调用取消/期限到期，Adapter 调用可取消或不可取消，迟到 ACK/回调，宿主关闭。
- 来源：调用 CancellationToken/单调 deadline、Adapter 的 native 取消与 drain 能力声明。
- 顺序：禁止受影响 Scope 的新普通命令 → 保留取消意图/回执 → 向 Adapter 发受控 Stop → 等待状态反馈和 native operation 真实退出 → 固定逻辑结果意图 → 排空该 operation 回调/租约/临时资源 → 发布终态；只有 Session Close 才释放连接，不能等待时返回未知并隔离 Adapter/轴组。
- 输出/状态：分开 `CancelRequested`、`StopAccepted`、`PhysicallyStopped`、`NativeDrained`；只在每项有证据时报告。超时为 `MOTION_TIMEOUT_UNKNOWN`，排空超时为 `MOTION_DRAIN_TIMEOUT`。
- 恢复/验收：相同 OperationId 查询；未排空不能重新使用句柄/轴组。故意迟到回调不得覆盖新 generation；强杀测试不被算作已停机。

#### G. 资源上限与降级

- 输入：内存/句柄/反馈通道/持久卷已达可用预算，或共享控制器授权租约不可取得。
- 来源：OS/部署 Profile、Adapter 能力与运行时资源计量，均带 revision。
- 顺序：命令前 reserve → 使用中计量 → 完成/停止后 drain → 释放；禁止先副作用再发现无回执容量。降级只允许取消非权威 UI 预览/合并状态投影，不可降低必需反馈率、轴数或安全事实。
- 输出/状态：`MOTION_RESOURCE_LIMIT` 或 `MOTION_CONTROLLER_BUSY`；不会产生新动作。资源状态不确定时写通道保持关闭。
- 恢复/验收：释放已确认资源后重新查询能力/资源，不自动续跑旧命令；磁盘满/额度耗尽时终态与实际动作仍能通过预留容量保全。

#### H. 持久化、重复提交和版本修订

- 输入：新命令、同键同内容、同键异内容、状态 CAS 冲突、进程在“记意图/提交设备/记回执”任一断点崩溃、配置或契约 revision 变化。
- 来源：稳定 CommandId、canonical request hash、expected state version、能力/配置/契约版本和耐久 operation ledger。
- 顺序：先解析已有 ledger；同键同 hash 返回/查询原 operation，同键异 hash 冲突；新 operation 原子 reserve → CAS → 记录待发意图 → Adapter 调用 → 保存 ack/unknown → 以状态事实推进 → 保存终态。无法证明设备是否接受的断点一律 Unknown，禁止自动重放。
- 输出/状态：回执具备可重启解析的 OperationId、request hash、ledger revision 和设备 boot/generation；新 schema 不重写历史回执。
- 恢复/验收：逐断点故障注入；相同 key 不产生第二动作，状态 CAS 冲突不进 Adapter，磁盘满不发布虚假成功。Ledger 的持久化 Owner/部署边界尚待主会话裁决，见 §15。

#### I. 升级、回退与配置失效

- 输入：契约/Adapter/固件/坐标资产升级或降级，在途操作、未决回执和能力 hash 变化。
- 来源：签名包清单、支持矩阵、迁移说明、旧版本 ledger 与设备实际 fingerprint。
- 顺序：禁止新命令 → 查询并排空所有 operation → 导出/保持 ledger → 安装兼容包 → 重新 Open/读取 capability/boot/state → 核对迁移 → 再开放写通道。
- 输出/状态：不兼容、未知动作或不可逆配置变更时保持 Unknown/NotReady；不兼容回执可只读解释，不得静默转成新字段。
- 恢复/验收：回退不清除 ledger，不自动重 Home 或重发命令；新旧包互读兼容样例/拒绝样例逐项可判，真实运动回滚需人工设备恢复流程。

#### J. 无 UI 调用与可选 UI

- 输入：同一版本化请求分别经无 UI 客户端和 WPF 控件提交；包括非法参数、取消和慢订阅者。
- 来源：宿主 Profile、语言服务、权限引用、Motion Core 公共入口。
- 顺序：两条路径都调用同一 validator/Core；UI 只做输入草稿/确认/投影，在后台执行并显式回到 Dispatcher 更新视图。
- 输出/状态：相同请求具有相同 Core 结果/ErrorCode/operation 回执；UI 可以显示语言化 MessageKey，不改变事实。
- 恢复/验收：卸载 UI 后核心任务仍可完成；慢/抛错 UI 回调不阻塞运动反馈。1920x1080 键盘/焦点/窗口关闭验证属于将来 UI 实现门，当前没有声称已测。

#### K. 第二消费者和长期运行

- 输入：扫描工具与定位工具同时连接同一物理控制器，另有维护只读观察；并连续经历取消、重连、订阅者增删、反馈退化和多小时/天负载。
- 来源：部署中唯一 Gateway/跨进程租约、每宿主独立配置/权限及共同契约版本。
- 顺序：第二进程发现已存在权威 Gateway 后经公开通道申请读/写 lease；不得各自加载 Adapter 独立写；每个租约绑定调用者、资源、期限和 operation。长期运行对每个订阅/缓存/ledger/queue 持续计量。
- 输出/状态：竞争写入一个被拒绝并返回 `MOTION_CONTROLLER_BUSY`，只读快照仍标 freshness；不出现双状态 Owner。长期指标包含句柄/内存/队列/operation/重连累计与排空失败。
- 恢复/验收：宿主重启不重放未知动作；长稳/重连测试证明无单调泄漏、序列回卷误判、重复命令和跨实例取消。定位工具无需改 Core 即能消费相同回执。

### 10.2 DZ-XVision 快照迁移的设备故障场景

以下只吸收 `DZ-XVision/20261004` 快照中可迁移的控制故障模式。快照中的板流阶段、具体轴卡函数、固定 IO 位、固定日志目录和旧 SDK 返回码均不是本模块 API。

#### 启动部分成功与关闭部分失败

- 输入：控制器身份/能力请求、配置 revision、启动期限；Adapter 可能在连接、状态读取、反馈订阅、后台任务中的任一步失败；旧来源的输出复位不得迁入 Open。
- 处理顺序：建立 `Initializing` → 验证控制器/能力/安全事实 → 读取全轴状态 → 按 Adapter 合同启动反馈与诊断任务 → 逐项确认 ready；任何一步失败立即停止接受普通命令，记录已启动资源和失败阶段，按已取得资源执行 Stop/Drain/Dispose。
- 输出/状态：完整启动为 `Ready` 或 `NotHomed`；部分成功为 `Unknown/Disconnected` 或显式 `MOTION_ADAPTER_FAILURE`，不得只因控制器已连接就开放写通道。关闭时分别报告各后台任务 `StopRequested/Stopped/DrainTimeout`，不能把线程标志清零当作 native 已退出。
- 恢复/验收：启动重试只能在上一轮资源已排空、且原 Session 已确认 Closed、物理对账允许重新连接后进行；仅被生命周期 Owner 接管不允许新实例夺取连接；关闭超时保留句柄和控制器租约。注入“连接成功但反馈订阅失败”“反馈停止但诊断任务未退出”均能看到逐资源结果和唯一 Owner。

#### 运动启动前置条件与启动失败

- 输入：轴组、目标/连续方向、单位化速度 Profile、坐标/能力 hash、期望状态版本、授权和 deadline。
- 处理顺序：确认 `Ready/NotHomed` 的合法前态、伺服/互锁/限位/故障/急停事实和资源预算 → 校验目标/路径 → 记录 operation reservation → 提交 Adapter → 等待控制器接受和实际反馈；命令 ACK 不等于已运动。
- 输出/状态：未满足前置条件返回 `MOTION_STATE_CONFLICT`、`MOTION_INTERLOCK_OPEN`、`MOTION_LIMIT_VIOLATION` 或 `MOTION_COMMAND_REJECTED`，并带 `DeviceCallMade`；提交结果未知使用 `MOTION_TIMEOUT_UNKNOWN`，不猜测未启动。
- 恢复/验收：先查询原 operation 和实际状态；只有明确未提交且已排空才允许同语义重试。测试覆盖“控制器连接但轴故障”“配置写入部分成功后启动”“反馈未更新但 ACK 成功”。

#### 停止请求、停止确认与停止超时

- 输入：正常 Stop/Hold、软件取消、窗口失焦、关闭或故障触发；Adapter 声明受控停止、保持和 native drain 能力。
- 处理顺序：停止新命令 → 记录 `StopRequested` → 调用受控 Stop/Hold → 等待控制器确认、速度/位置反馈和 native operation 退出 → 记录 `PhysicallyStopped`（仅有证据时）→ 排空回调与租约。
- 输出/状态：区分 `StopAccepted`、`PhysicallyStopped`、`NativeDrained`；等待期限到返回 `MOTION_TIMEOUT_UNKNOWN` 或 `MOTION_DRAIN_TIMEOUT`，状态保持 `Holding/Unknown`。软件取消不升级为急停，硬件/安全 Owner 仍拥有急停。
- 恢复/验收：停止超时进入 Adapter 隔离，不强杀线程、不返还句柄、不重放新命令；由生命周期 Owner 查询/复位/重新建立 generation。必须能证明迟到的停止回调不会覆盖新 operation。

#### 回零失败、原点/Index 歧义与限位触发

- 输入：轴、回零方向、回零模式（原点开关/Index 等能力）、速度 Profile、限位/互锁事实和回零 deadline。
- 处理顺序：确认轴未运动或满足回零前置 → 校验方向、原点/Index 能力和限位极性/来源 → 提交 Home → 按样本记录 home switch、Index、正/负限位、actual/cmd position、velocity、fault 和 in-position → 按批准策略完成减速/停止、稳定窗口和位置基准提交。
- 输出/状态：`Homing` 期间触发限位、故障、反馈缺口或 deadline 到期，返回 `MOTION_LIMIT_VIOLATION`、`MOTION_FOLLOWING_ERROR`、`MOTION_FEEDBACK_GAP` 或 `MOTION_TIMEOUT_UNKNOWN`；没有批准 HomeMode 所需的 latch/Index 事件、稳定与基准提交证据，不得进入 `Ready`；不强求回零结束时原点/Index 电平仍同时有效。
- 恢复/验收：触发限位时默认停止并保持 Unknown/Holding；只有设备 Profile 明确允许、方向/释放距离/安全条件均已验证时，才能执行一次受控 back-off/retry。不得根据单个限位位自动反向回零，不得把位置清零调用的返回值当作基准已生效；需重新读实际位置/位置版本。覆盖“原点一直有效”“限位与原点同时有效”“到位但无原点”“Index 缺失”“回零后反馈旧 epoch”。

#### 运行中硬限位、故障和安全输入变化

- 输入：Moving/Settling 状态中正/负硬限位、驱动故障、急停/门禁/互锁变化、反馈中的 abort/error 标志。
- 处理顺序：以硬件/安全 Owner 的事实为准 → 立即撤销触发/普通命令许可 → 记录限位方向、实际/指令位置、速度、故障码、互锁/急停和 operation → 请求受控停止或等待安全链 → 查询实际停止和排空。
- 输出/状态：进入 `Interlocked/Holding/Faulted/EStopped/Unknown` 的明确状态；任何单一状态位缺失或矛盾都按 Unknown 处理，不把“到位/停止”显示为安全结论。
- 恢复/验收：故障复位不自动恢复 `Ready`；按安全 Owner 的确认、重新状态同步，必要时重新 Home。测试覆盖限位在启动前、运动中、停止后改变，以及状态读取异常；不得只依赖 UI 轮询。

#### 期限超时与可追溯诊断

- 输入：operation deadline、当前阶段（连接/提交/运动/回零/停止/排空）、最后可信反馈和单调时钟。
- 处理顺序：期限使用单调时间 → 记录阶段和已发生副作用 → 发起停止/查询/排空 → 记录逻辑结果或 Unknown/Draining 回执；只有真实排空、归还并完成对账才能发布唯一 operation 终态，不将 TimeoutUnknown/DrainTimeout 错作终态枚举，不因应用重启删除超时事实。
- 输出/状态：超时事件必须带 elapsed、deadline、last feedback age、命令/实际位置、速度、限位/故障/互锁快照和 `DeviceCallMade`；板件进出、检测或 MES 超时名称留在调用方。
- 恢复/验收：超时后只按原 OperationId 对账；没有明确“未提交/已停止/已排空”证据时禁止新 CommandId 重试。注入迟到 ACK、迟到反馈、时钟 epoch 变化和进程重启，结果必须可判定且不重复运动。

## 11. 测试矩阵与验收断言

文档阶段仅定义验收；未执行即不得标为通过。Simulator 套件和真实 Adapter 必须共享同一契约测试。

两个审查视角直接落实到测试：能力/数据视角逐方法走正常、空/重复、上限±1、弱/缺反馈、映射多候选和参数改变；外部接入/生命周期视角在 reserve、提交、ACK、settle、停止、排空、释放每个边界注入并发/取消/崩溃/迟到/关闭/回退。资源责任和每次 DeviceCallMade 都要可判定，不能仅断言 bool 或错误文本。

| 层级 | 必测内容 | 断言 |
|---|---|---|
| Contract | 单位、范围、NaN/Infinity、序列化、hash、版本、坐标资产绑定 | 非法输入和失效坐标/校准版本在设备调用前拒绝；canonical bytes 稳定 |
| State | 全部合法/非法边、Unknown、NotHomed、Hold、Interlock、EStop | 无权威反馈不能到 Ready；非法边不发布状态 |
| Idempotency | 同键同内容、同键异内容、丢回复后查询 | 同键只产生一个物理命令；冲突可判定 |
| Motion | 绝对/相对/Jog/插补/回零/比较触发能力 | 目标、实际、控制器序列和单位不混淆 |
| Settled | 容差边界、连续 dwell、抖动、反馈空洞、时钟跳变、位置/坐标资产版本变化 | 只有有界同域连续样本满足策略且回执绑定区间、最终位置版本和实际位置才返回 Settled |
| Cancel/Timeout | 取消前/中/后、deadline、迟到事件 | 取消不伪造急停；超时不盲重试；事件终态唯一 |
| Recovery | 断线、重启、能力变化、限位、跟随误差、排空失败 | 新 epoch 建立前保持 Unknown/Hold；资源不泄漏 |
| Scenario | 空输入、部分多轴成功、歧义、多解、ResourceLimits、迟到回调、ledger 断点 | 每种情形有明确 `DeviceCallMade`、逐轴终态和恢复动作 |
| Startup/Home/Stop | 启动部分成功、后台任务停止超时、回零原点/Index/限位、受控停止超时 | 各资源/阶段有独立回执；未知动作不重试，未获基准证据不 Ready |
| MotionLog | 结构化事件、顺序、generation、落盘失败、队列满、迟到/重复事件 | 可重建 operation 链；日志不成为运动事实或重试依据 |
| Adapter | 模拟与厂商端口的线程、释放、原码和不支持能力 | SDK 类型不泄漏到 Core；不支持显式返回 |
| UI | 1920x1080、键盘、失焦、关闭、三语、权限变化 | UI 只调用 Core；失焦/关闭可观察停止与排空结果 |
| 两个消费者 | 扫描工具与定位工具使用同一 Core；维护工具隔离实例 | 无核心修改即可接入；配置、取消、语言、缓存不串扰 |
| HIL/现场 | 回零、点动、边界、急停、掉电、真实时序、长稳 | 单独由硬件/安全/客户门禁签署；模拟结果不替代 |

### 11.1 可执行合成反例和工程测试落点

以下数值**仅为确定性单元/模拟样例**，没有客户计量/节拍含义。Fixture-F1：X/Y 线轴 mm、位置 [-100,100]、分辨率 0.001，Theta 角轴 deg、位置 [-720,720]、分辨率 0.001；设备 tick frequency=1000，Boot=b1/Generation=1/Epoch=e1。settled：X/Y 位置容差 0.01 mm，Theta 0.1 deg，各轴速度容差按单位 0.01/s、跟随误差容差按单位 0.02，Dwell=20 ms、Gap=10 ms、Age=10 ms、Skew=2 ms；它们由 fixture 明确构造/hash，不传播到生产。命令/清理 deadline 和 resource limits 从每个测试给定的有限 fixture Profile 取，不接受 infinite。

| 测试类/公开能力 | 具体输入或边界 | 断言与恢复 |
|---|---|---|
| ContractTests/Open | 未打开构造、ReadOnly Open、缺依赖、重复 OpenId、Controller 不匹配 | 构造零设备动作；同键同正文一个连接；read-only 拒绝全部写；初始化失败逐资源回执，Close 可重试 |
| ScopeTests | 空/重复/缺 Y 的 XY 组、10000 轴请求、重叠 XY/YTheta 并发、独立 X/Theta 并发 | 空/重复/超限零提交；资源按整组预留；共享轴一个 Busy；设备未声明并行则仍串行，不能猜硬件能力 |
| PositionTests/Relative | actual X=10，delta=2，响应丢失后同键重查；两请求均引用旧位置版本 | 原目标永远 12，不变 14；竞争请求只能一个接受，另一 Conflict；溢出、未回零、-0/NaN 拒绝/规范化按 A.1 |
| TrajectoryTests | offset=0/10/20 ms，X=0/1/2；offset 重复/倒序、轴缺项、内部段出禁区、未知 jerk/插补包络 | 合法完整一次提交；异常在 Submit 前拒绝；第 N 轴部分 ACK 停整组并列真实已发集合；不伪造物理回滚 |
| DirectionTests | 起点 X=5、target=2、Positive OneSided distance=1，preTarget=1；target=-100 时 preTarget=-101 | 前例冻结两段 5→1→2，最终 Positive；后例整体拒绝零动作，不省略预接近；Home/断线后历史 Unknown，不能沿用上次方向 |
| SettledTests | target X=1、Theta=10；tick 0/10/20，actual X=1.01、Theta=10.1，速度/跟随误差在界内 | 合格边界可 settled；Theta=10.11 即拒绝，不与 X 求混合范数；重复 tick/样本只一次贡献 |
| ClockTests | 0/10/20 之间缺 10、旧 epoch、新 mapping、分轴相差 3 tick、UTC 前后跳 | 缺口/epoch/映射错或 Skew=3 ms 时失败；墙钟跳不延 deadline；ClockMapping 最坏误差界纳入，不拿主机接收时间替代 |
| SettledRevocationTests | 先完成窗口，再开始另一 Move、Home/Reset、断线或校准资产更新 | 旧回执保留；当前 settled 立即失效，Wait 请求旧目标版本失败；过去窗口不自动授权未来曝光 |
| HomeTests | Switch/Index/SwitchThenIndex/AbsoluteReference 分别所需证据；原点一直亮、终点开关已离开、Index 缺失、基准写 ACK 无回读 | 按模式接收 latch/Index/基准版本，末态电平不是统一通过条件；缺所需事实仍 NotHomed/Unknown；不无限 backoff |
| JogTests | 一个正向 Jog，重复/倒序心跳、失焦、同时按正负、最长 duration 到期、ct 已取消 | 重复不续期，冲突或 deadline/deadman Stop；清理不用已取消 token；心跳不产生新移动 ID，不延最长寿命 |
| ServoConfigurationTests | Moving 时 DisableServo；部分 soft-limit 写失败；缺字段、越界、BaseRevision 过期 | Disable 先可证 Stop；配置无假回滚，逐字段 Applied/Unknown 保留，新运动关闭；修正不重发未知写 |
| CompareTests | 正向升序表、重复点/反序/超容量、加载 ACK 无 Active、触发后 Cancel、Close 撤销失败 | 只登记不宣称触发；非法零提交；Close 保留登记 Owner，不能归还可继续输出的资源 |
| InterlockTests | 门禁中途开、丢订阅、EStop True、旧 Sequence、未知/过期、Adapter 与端口矛盾 | 立即关闭对应普通 Scope，可信 EStop 事实镜像；软件无法伪造物理急停，Stop 通道仍可用 |
| StopCancelTests | 普通 CAS/坐标过期、权限已撤、普通队列满、账本掉线、ACK 成功但实际速度不零、Stop Done 但控制器锁仍持有 | Stop 不被普通验证/队列挡住；Holding/Ready 不提前，LedgerUnknown 不派新动作，ControllerLockReleased 必需 |
| NativeLifecycleTests | WaitAsync 先超时、底层 Read/Submit 迟到、Dispose 释放抛错、worker 退出但设备仍 Moving | 原 Owner 留真实 task；新代拒旧回调；Dispose 转 Quarantined 并 Retain；OS 回收不算物理停止/终态；RetryClose 只续清理 |
| LedgerRecoveryTests | reserve/意图/提交/ACK/逻辑意图/排空/终态各点崩溃、同键异正文、账本磁盘满 | 原 ID 查询，未知不重发；CAS 冲突零提交；终态一次且不可改写；预留尾容量有明确断言 |
| ConsumerPackageTests | 独立控制台扫描消费者、定位消费者、只读维护，共用/分离 Session | 只引用发布包/公开 port；共用物理资源唯一写 Owner；取消/语言/配置无串扰；需要产品 Shell 才能运行即失败 |
| MigrationTests | v0.2 codec golden、未知 enum/Schema、不兼容旧回执、Profile 修改且有在途命令 | bytes/hash 固定、未知版本拒绝；升级/回退保持原 ledger，不默默转换原 identity 或恢复运动 |
| TargetVersionTests | 接纳目标后 actual 从 0→0.5→1，PositionVersion 逐样变化，TargetVersion 不变；随后新 Move 改目标版本 | 正常移动能 settled；旧目标查询失效，历史 FinalPositionVersion 不改写；相对请求仍按最新实际版本 CAS |
| HostClockAgeTests | device tick=0 的旧帧到 host 30 ms 才收到，Age 上限 10 ms；设备到主机映射缺失/最大误差 11 ms | 接收时间新不能遮盖原样本过期；缺映射/超不确定度不可 settled 或 PhysicallyStopped；Stop 仍能请求 |
| EventCursorTests | 两操作交错、Scope 筛选、订阅容量满、终态重投、原子 ledger Commit 失败 | 会话 cursor 不混操作序号；筛选缺号不伪造 EventGap，重投同 EventId；ledger 未保全不发布成功终态 |
| RegistrationRecoveryTests | 装载 op 已 Completed 而登记 Active；Exhausted 但登记资源 Held；Cancel 回读成功而 ledger 写失败 | ReadPending/Close 仍列旧登记；不重新装载，不漏撤销；未耐久确认不释放登记，保持原 Owner |
| ScriptReplayTests | plan/hash/版本错、脚本缺 Stop、HoldNative 后超时、FailRelease 后 Close 重查；历史能力 Hardware、投影 Replay | 无脚本不伪造停止；真实 task 留存，ReleaseFault 只释放一次；Replay 零物理写、原样本重核、历史身份/目标/源不重写 |
| PathCapabilityTests | 端点合格但插补包络 Unknown、校验后配置变更、ReadCapabilities 刷新、新 Boot | 缺预检/版本不符零 Submit；只读刷新不再次 Open、不改配置，不自动恢复旧 operation |
| PreviewTests | 同一 Relative 草稿预览两次、生成授权、预览后 actual/配置改变、只读宿主预览 | 零 reservation/Submit；相同意图摘要，不两次累加 Delta；最终 Move 仍完整授权/CAS，过期预览不能下发；Preview 不开放只读写通道 |

测试文件位于绑定 Core.Tests 的 Contract/State/Motion/Clock/Lifecycle/Consumers 子目录；类名按上表，不建立过程报告。用虚拟 TimeProvider 推进确定性时间，用 TaskCompletionSource 屏障制造真实竞争；不得用固定 sleep 隐藏竞态。Core.Tests 固定为 `Microsoft.NET.Sdk`、`net10.0`、`OutputType=Exe`，仅 BCL 与受测 Core；入口执行上表全部确定性断言。唯一命令为 `dotnet run --project tests/Modules/motion-control/Asun.Modules.MotionControl.Core.Tests/Asun.Modules.MotionControl.Core.Tests.csproj -c Release`；任一失败、未完成或必需项跳过返回非零并列明用例 ID。采用有限测试截止点及外层进程超时，未排空不得返回 0。`dotnet test` 不执行此 Exe，不能代替验证；正常测量另用 §12.2，SDK/HIL/UI 分门。

Core Exe 首版墙钟预算固定：每 case **10 s**（从该 case 开始装配到断言、finally、故障释放与资源收敛全部结束），suite **120 s**（从 Exe 入口计至全部 case 和 suite 清理结束），外层 `dotnet run` 进程 **180 s**（从启动命令计，包括 restore/build/Exe/退出）。case/suite 使用 `TimeProvider.System` 的单调计时或 Stopwatch，外层运行器使用独立主机单调计时；不使用注入的 MotionVirtualTimeProvider，不因虚拟 Advance、任务重试或进入 finally 重置预算。某 case 的实际可用时长取 10 s 与 suite 剩余时长较小值；超时立即标失败并列出用例 ID/未结束阶段，不再启动依赖该资源的 case。清理观察仍受该 case/suite 剩余墙钟预算约束，未知任务保留原 Owner，不把超时包装完成当排空；suite 预算耗尽时停止启动新 case，退出非零并列未完成/必需跳过项。外层 180 s 到期记录进程超时及最后用例 ID、结束整个本次测试进程树，运行结果非零；这是 harness 故障保护，不是设备停止或产品资源释放证据。模拟的 HoldNative 等 case 必须在预算内受控 ReleaseFault/Close 并核 pending 计数才能通过；不可恢复挂起仅能判失败。§12.2 Benchmark、真实 S3/S4 不套用这些测试预算或把它们当客户节拍。

## 12. 性能、容量与可观测性

性能预算是待按机器 Profile 冻结的工程门，不在本页虚构客户节拍。实现必须测量并报告：

- 状态查询/反馈解码、命令提交、首个实际反馈、Move 完成、settle 窗口、Stop 回执的 P50/P95/P99 和最大值。
- 反馈采样周期、事件发布延迟、队列深度、丢弃/重复/乱序数量、排空时间和 CPU/内存峰值。
- 轴数、并发只读查询、单控制器多轴、插补点数和在途 Operation 数的容量边界。

本页不规定客户节拍或固定毫秒阈值。Core 解析、事件入队和参数校验的 P50/P95/P99 目标必须由每个部署 Profile 以版本化预算给出；设备命令、反馈和 settled 时间由 Adapter/设备 Profile 给出。没有预算来源的数字不能写入实现或验收；任何超预算必须保留原始 trace 和配置版本。

每个 trace 关联 `OperationId`、`CommandId`、`AxisId/AxisGroup`、`StateVersion`、`BootId/Generation`、`CapabilitySha256`、`ControllerSequence`、坐标帧、授权引用摘要和 `Simulation/Replay/Hardware` 来源。指标与日志不可成为第二状态写入者；日志脱敏，不记录授权秘密。

### 12.1 MotionLog 事件契约

快照中的 `MotionInfo`、`MotionError`、`MotionDebug` 和专用日志类别可迁移为诊断投影，但不能继续使用只有本地时分秒和自由文本的日志作为事实来源。模块通过注入的 `IMotionDiagnosticSink` 发布结构化事件，持久化位置、轮转、保留期和权限由宿主/诊断 Owner 决定。

每条事件至少包含：

- `EventId`、`EventSequence`、`Severity`（Trace/Info/Warning/Error/Critical）、`DiagnosticKind`（Startup/Command/Feedback/Limit/Home/Stop/Timeout/Recovery/Resource/Drain）；
- `OperationId`、`CommandId`、授权域、轴/轴组、控制器/Adapter 身份、`BootId`、`Generation`、`StateVersion` 和能力/配置/契约 hash；
- 阶段、单调时间/设备 tick/时钟域、UTC 审计时间、事件来源（Hardware/Simulation/Replay）和 `DeviceCallMade`；
- command/actual position、command/actual velocity、following error、in-position、home switch/Index、正/负限位、fault、interlock、EStop/abort、控制器序列和原始错误码（字段不可用时显式 `Unknown`）；
- deadline、elapsed、last feedback age、停止请求/接受/物理停止/native 排空证据、资源队列水位和恢复建议；
- `MessageKey` 与结构化参数。原始厂商文本只作诊断附加字段，不得取代稳定错误码。

日志顺序按 `EventSequence` 和 generation 解释；迟到、重复、跨 generation 事件保留为诊断，不改写已提交 operation。正式终态、互锁、急停、限位和排空事件不得因日志队列满而丢失；普通状态/Trace 可在有界预算内合并。Sink 不可用、写入失败或磁盘满时，运动事实仍按 Core/ledger 语义返回，同时发布 `MOTION_DIAGNOSTIC_SINK_FAILURE` 并进入诊断降级；不能把“日志写成功”当作运动成功，也不能因日志失败自动重试物理命令。

验收至少覆盖：启动部分成功、停止超时、回零限位、运行中限位、迟到 ACK、native 未排空、Adapter 重连和日志落盘失败。事件可按 `OperationId + Generation` 重建启动→命令→反馈→限位/故障→停止→排空链，且不包含板件流程、质量判定或安全链控制权。

### 12.2 BenchmarkProfile 与运行步骤

本节属于 §12 性能规范，沿 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门) 的唯一分位/删失/端到端口径，不复制算法。Core.Tests 的 `Benchmarks/MotionBenchmarkRunner.cs` 是后续测量消费者，使用真实单调 `TimeProvider.System`/Stopwatch 测软件成本；虚拟设备 tick 只作输入，不当运行性能。无客户目标时只允许 NotEvaluated 诊断测量，不能判 PASS。

`MotionBenchmarkProfile` 为测试/宿主测量配置 sealed record，精确字段：string ProfileId/Version/InputSha256/RuntimeProfileSha256/WorkloadId，SourceKind Source，int AxisCount/GroupCount/TrajectoryPointCount/FeedbackRateHz/ConcurrentReaders/ConcurrentScopes/SubscriberCount/WarmupCount/MeasurementCount/MinimumValidSamples，TimeSpan Deadline，ResourceLimits Limits，ImmutableDictionary<string,TimeSpan> LatencyTargets，ImmutableDictionary<string,long> ResourceTargets，string? TargetApprovalRef。所有数量非负，实际测量次数/轴数/反馈率/有限 Deadline/上限正；Warmup 可零但明确记录。目标字典空或 ApprovalRef=null 即 NotEvaluated，不临时补门槛。

运行顺序：记录 net10.0/进程位数/主机/runtime/Adapter 或 Simulator 指纹、配置/能力/输入 hash → 冷启动一轮 → 每 workload 精确预热次数 → 测量次数 → 等待本轮 operation Drained/ResourcesReleased → 记录样本/错误/删失及资源终态 → 只按同 Profile 比较。变版本/输入/计时域不合并；构建优化、GC 配置、日志/图表开关和长稳时长由采纳 Profile 固定。

负载维度：单线轴/单角轴/混合轴组；绝对/相对/零位移/全容量轨迹/OneSided；反馈率低/声明上限、轨迹点与事件积压上限±1、独立/共享 Scope 竞争、快/慢/抛错订阅者、多个只读 Host、ledger 延迟/容量耗尽、取消/超时/重连/迟到回调/释放失败。每类同正常/故障注入版本绑定；不把 UI 抽样后数据用作 Core 基准。

阶段测点：接纳前校验/codec/坐标解析，reserve/CAS，Submit/首反馈/实际停止，settled 首样本/末样本，逻辑意图/Draining/Drained/ResourcesReleased；Stop 另测请求→ACK→PhysicallyStopped→ControllerStopLockReleased→排空→归还。端到端和取消到归还按 GOV-010，记录 P50/P95/P99、n、最大值，失败和未知排空单列不得删除。资源计数：活动 operation/Scope lease/Controller lease、查询/native task/回调、反馈/事件队列、Compare 登记、ledger 预留字节、托管内存峰值/句柄/CPU；超过 ResourceLimits 或资源未收敛为测量失败，既定时延目标缺失为 NotEvaluated。设备实际停止距离、回差、误差/时钟资格与客户节拍只在 S4/HIL 上独立验收。

## 13. 版本、发布、迁移与回退

- 发布单元：`Asun.Modules.MotionControl.Core` 包含 Contract/Simulator/Replay/Port；可选 `Asun.Modules.MotionControl.Wpf` 独立发布；真实厂商包由对应适配模块负责，不在本模块另建 `Motion.Contracts` 或 Simulator 包；版本遵循 SemVer，契约主版本变化不得静默兼容。
- 包清单固定目标框架、公开 API、依赖版本、Adapter 能力版本、配置 Schema、测试套件版本和 SHA-256；不把产品工程或 SDK 二进制打进 Core。
- 向后兼容：新增可选字段/能力并保留旧语义；修改单位、状态、错误码、事件顺序、取消或资源所有权必须升主版本并提供迁移说明。
- 运行前比较契约版本、能力快照、坐标资产和配置 hash。发现不匹配时拒绝受影响命令，保留旧回执，不自动降级为旧坐标。
- 回退先停止新命令、查询/排空所有在途 Operation、保留真实设备状态和回执，再切换软件包；禁止通过重启抹掉 Unknown。回退后需重新 Open、读取 boot/generation、确认状态，必要时由维护流程重新 Home。
- SDK/PLC 交付、HIL、安全签署、FAT/SAT 和客户验收是独立门；本指导完成不等于这些门通过。

## 14. 第二消费者接入验收

第二消费者为**定位工具**（第一消费者为扫描工具，维护工具用于第三种权限/恢复路径）。定位工具提交明确的 `MoveRequest`/`RelativeMoveRequest`/`SettledRequest`，将位置事实交给自身定位流程；它不得读取扫描工具私有状态或把 settled 结果改写为质量结论。验收要求：

1. 两个宿主只引用发布包和公开契约，均可用 Simulator 完成 Open、Status、Move、Settled、Cancel、Close。
2. 两个宿主同时运行时，轴资源竞争按同一 Owner/租约规则可判定；拒绝不会产生设备副作用。
3. 一个宿主取消、断开 UI 或切换语言不影响另一个实例；事件包含各自 OperationId 和 epoch。
4. 用同一真实 Adapter 契约测试验证同样的状态、错误、幂等、排空和恢复语义；硬件/安全资格另行计门。

## 15. 待决项与接入前清单

- 目标 PLC/控制器、SDK 路径/版本/API 快照、线程模型、停止和释放语义。
- 每轴真实单位、量程、分辨率、正方向、软/硬限位、回零序列、伺服使能和坐标资产。
- settled 的反馈来源、采样周期、误差界、连续窗口、时钟域和触发时序。
- 比较触发、电子齿轮、插补、同步采样以及断电/重启后的实际行为。
- 路线授权签发者、权限策略、审计保存者和安全 PLC 验证责任。
- 跨进程唯一 Gateway、轴/控制器租约、Operation ledger 的持久化 Owner、提交前后断点恢复协议和磁盘/权限边界；未裁决前不允许多个宿主各自持有写 Adapter。
- 多轴分阶段提交是否允许、部分成功的停止/补偿策略及其客户验收责任；核心不能假设物理回滚。
- 视觉遮挡/噪声不属于 Motion 算法输入；若视觉宿主需要用运动反馈建立图像证据，需由主会话裁决 MotionActual 证据合同和跨模块 Owner。
- 两个消费者的客户 Profile、节拍、容量、HIL、FAT/SAT 和回退验收值。

这些外部事实按依赖分门，精确 Owner 和关闭证据见 §17.7。真实机械/SDK/PLC/安全输入只阻断 S4；MotionActual 产品映射只阻断对应集成；1920×1080/WPF 编译交互只阻断 S3 资格。S1/S2 和只读桥已有规格接收保持有效；§17 已补齐当前全范围的内部软件定义，不再把 Adapter 换算、UI 根持有、恢复顺序或参数算法选择列为外部门。实现任务仍须用户指定并确认权威代码快照/分支，目标缺失的诊断 Benchmark 为 NotEvaluated；整模块仍 `PreparationIncomplete`，没有实现/测试/生产/安全通过结论。

## 16. 依据与自审

本指导核对并继承以下现行边界：

- `docs/shared-modules/packages/PKG-010_Motion.md`：轴配置、回零、定位/插补、比较触发、反馈、停止/复位及两个消费者要求。
- `docs/shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md`：设备能力分离、命令 ACK 与实际事实分离、先注册关联再触发、取消/排空和 PLC 安全边界。
- 只读来源 `H:\docs\40-development\41-vision-platform\02-acquisition\运动控制抽象与坐标运动开发指导.md`（source-manifest SHA-256：`6bd3175286075b9f376e5f0799b930e31300c9d7d7789665e599d4fd08f7bcba`）：仅采纳位置反馈携带坐标/校准版本、Settled 回执绑定连续反馈区间与最终位置版本的通用运动约束；采集宿主授权与曝光封存流程、PCB/PCBA/3D 路线和性能阈值不属于本模块指导。
- `docs/independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md` 与 `docs/01-governance/DEV-GOV-005_模块独立性与复用标准.md`：独立类库、无 UI 核心、强类型契约、资源/线程/版本/两个消费者。
- 历史只读参考 `docs/references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/运动控制抽象与坐标运动开发指导.md` 及其 `PLT-ACQ-03` 合同索引：状态、幂等、Unknown/Hold、Move/Settled/Reset/Recover/Estop 语义。该原件不被本平台改写为实现证据。
- DZ-XVision 只读快照 `docs/references/project-snapshots/DZ-XVision/20261004/`（Manifest tree SHA-256：`a3649338762b234537d185d18496fcd438ba91eafd06b8d817ebee4c5a5ceae8`）：`Motion9014`/`MotionPanel` 展示控制器初始化、轴状态字段、回零/原点与限位处理、停止等待超时、后台任务启动/停止和 `MotionLog` 分类。仅迁移故障模式、证据字段和恢复要求；不迁移板流语义、固定 IO/时间、旧 SDK API 或日志路径。
- [`AsunControl` 只读快照](../../references/project-snapshots/AsunControl/20261004/original)：仅发现线阵标定代码中的运动方向/速度字段，未发现可复用运动控制核心；不作为本模块 API 或实现依据。

本轮复用已直接读过的官方正文、源码和测试，不复制上游代码、不引入上游依赖：

| 固定来源 | 实际读取与可迁移约束 | 限制/落点 |
|---|---|---|
| [.NET 协作取消](https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads)、[Task.WaitAsync（.NET 10）](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.waitasync?view=net-10.0) | 监听者负责退出；等待包装的超时/取消不能证明底层 task 退出 | §5–6：真实 task/回调继续由原 Owner 保管，不把 token 或 WaitAsync 完成当物理停止 |
| [Beckhoff TwinCAT 3 Tc2_MC2 MC_Stop](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2/70108555.html) | Done 表示静止但 Busy/Active 可仍 true；Execute=false 后还需周期完成解锁 | §5.1/A.1/A.3：静止、保持、控制器 stop-lock 与 native 排空分离；不假设其它控制器有同 API 或周期 |
| [OpenPnP commit 5bd404cfc70f34103a3ca0fbb6b50c2b465f407c](https://github.com/openpnp/openpnp/tree/5bd404cfc70f34103a3ca0fbb6b50c2b465f407c) | `ReferenceControllerAxis.java` 的 None/OneSided/Directional/SneakUp；`AbstractMotionPlanner.java` 的方向/额外段/速度/offset、Home 清历史；`AdvancedMotionTest.java` 的 long/short/tiny/micro 与动力学异常 | Java/Maven，源码头 GPL-3.0-or-later；pom JNA 5.8.0/JUnit Jupiter 5.7.1/JFreeChart 1.5.3。只迁移全路径预检/方向清理与反例思想（§7.2/11.1），不复制代码；测试不是回差现场资格 |
| [Ruckig v0.15.3](https://github.com/pantor/ruckig/tree/v0.15.3) | `input_parameter.hpp`、`test/test_target.cpp` 的有限性/负界/超速/input-validation 与轨迹/同步反例；已读 `CMakeLists.txt`/`LICENSE` | MIT、C++17，默认 BUILD_CLOUD_CLIENT=ON，doctest/third_party；部分 acceleration/jerk 默认 infinity、Phase 可退为 Time、部分中间点功能 Pro。只借鉴验证与反例，不原样引入、不允许无穷参数或隐式同步降级，不替代控制器 |
| [DevExpress WPF 25.2](https://docs.devexpress.com/WPF/?v=25.2) 与本机官方 XML | DockLayoutManager、GridControl/TreeListView、PropertyGridControl、ChartControl、SuperTip、`DevExpress.Xpf.Editors.Flyout.FlyoutControl` 官方正文；本机 XML 确认 AllowClose/AllowFloat/AllowCustomization、SelectedObject、XYDiagram2D/LineSeries2D、ChartControlBase.CrosshairEnabled、FlyoutBase.IsOpen/PlacementTarget | §8 组合与成员依据；本机 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/DevExpress.Xpf.{Docking,Grid,PropertyGrid,Charts,Core}.v25.2.xml`。在线 25.2 可对应较新 patch，真实 25.2.3 编译/交互仍为 S3 门；不下载/改版本 |

已读取原件的 SHA-256：OpenPnP `AbstractMotionPlanner.java` 55250 bytes、`cbef8710c956fb9be51630b962cd0a6d4341442ae39d2f7d73e005a283f4c9ac`；`AdvancedMotionTest.java` 22008 bytes、`93a972c57b6917f38d65212cba0c260224abf48a726673ed12b6959e70c0b7c6`。Ruckig `input_parameter.hpp` 21813 bytes、`37a4dc34e2093e775e3fd5ae6c34971661fd852ed165ee9e7ddc3dcb0b1cc96d`；`test_target.cpp` 52826 bytes、`9feddcf103b08fc4061dd83ad34d4407c81f3c8d6a61b5ed15ff2fb8d99e2f47`。部分本地上游快照不含上述文件，引用固定 commit/tag 原始路径，不声称新增或完整保存了上游快照。

自审结论：本文没有写入 PCB/PCBA/SPI/AOI/点胶/涂覆判定，没有授予质量放行或设备安全权，没有依赖产品页面、私表、AsunImage 内部或厂商 SDK；核心入口可无 UI 调用。当前逐切片准备状态见 A.6，全范围文档结论见 §17；正式产品 Contract、设备事实、HIL 与生产资格均保留为对应接入前门。

2026-10-10 自审历史：关闭机器轴 null 资产与 DTO 冲突、浮点 checked/负零规则冲突、Host 早退/Rejected ID/Pending 无 Failure 的清理漏洞、Stop 回读与锁解除缺字段、ledger 提交意图/原路径与事件 cursor 缺失、ReadOnly/Replay 写通道、Simulator 构造/注入/释放和 UI Detach 旧代回调欠定义，以及旧测试命令/拆包建议与当前绑定冲突。随后 S1/S2 与只读桥规格已获接收，见 A.6；本次完整范围核实见 §17，不重复旧研究/向量复算。上述均为规格自审，未执行 Core、WPF、Benchmark、HIL 或生产测试。

## 17. 当前架构全范围核实与补充实施规则（2026-10-11）

本节按架构 IM-010 的扫描、定位、维护三个消费者核实全部已规划能力，包括可选 WPF 和设备无关 Adapter 边界；不是仅检查已接收 Core。IM-064 的厂商 SDK 实现仍归其永久原会话，本节只冻结 IM-010 必须向它提供的语义，不检查或修改其它模块。§3–14、A.1–8 的有效研究、自审和固定向量直接复用；本节补充其中尚需开发者决定的软件细节。正式产品映射仍未采纳，不改变 Core v0.2 请求/回执、Read Bridge v0.1 字段、枚举编号或既有字节向量；未发布的CoordinateQuery端口补显式Kind/Start，WPF补根Owner，精确形状在本节与A.4同步，不保留旧不完整端口。

### 17.1 能力覆盖与参数权威

| 当前批准范围 | 唯一实施位置与成功/失败边界 |
|---|---|
| 强单位、轴/组、坐标与版本、权限、限制 | §3、A.1–5；§17.2/17.6 补原生换算和版本确定规则；缺必需事实零下发 |
| 绝对/相对/轨迹、单向接近、控制器补偿 | §7.1–2、A.4；§17.2 补普通定位时间化与量化包络；全路径冻结且验证为真才接纳 |
| Home、Servo、普通配置、Reset/Recover | §5/7.3、A.2–4、§17.3；基准、实际静止、锁解除与对账分开，不从 ACK 恢复 Ready |
| Jog/deadman、停止、联锁与 Compare | §5.1/6/7.4–5、A.3–4；原身份停止容量独立，登记输出撤销单独归还 |
| Ledger、租约、事件、诊断、原 Task 与关闭 | §4/6/9/12–13、A.4–5、§17.3–4；未知保留根 Owner，订阅与 UI 不是事实库 |
| Simulator/Replay、两个独立消费者 | §9–11/14、A.7、§17.6；固定脚本、独立端口和有界恢复，无 SDK/产品 Shell |
| 同 run XY 历史、时钟、动态证据只读桥 | §7.6、A.8、§17.5；原 tick/sequence/actual/位置版本保留，物理资格由外部事实 Owner 提供 |
| 可选 WPF 控件、三语、键盘与卸载 | §8、§17.4/17.6；借用 Session、不签发授权、不隐式打开设备，实际 WPF 验收单列 |
| 正确性、容量、性能、发布/回退 | §10–14、§17.6–7；合成反例只证明软件语义，P50/P95/P99 与物理指标分开 |

参数只有四种来源：能力快照给设备声明的可观测范围/分辨率；有版本的宿主 Profile 给速度、加速度、jerk、settled/StopPolicy/期限/容量；固定坐标/资格资产给映射、禁区、回差距离；本节算法只推导转换值、派生时间与显示投影。范围取能力和批准 Profile 的交集，空交集拒绝。变更任一相关版本使预览、普通授权、未提交路径预检失效，原回执保持旧依据。模块没有自动整定、自动选择 Home、自动扩大容差或自动改生产速度的能力，也没有待实现的通用 AI 参数推荐；因此无需另设计推荐 API。时间化与量化是确定的计算，不写回 Profile，不作为新生产参数建议。

### 17.2 原生单位换算、量化和普通定位时间化

**原生映射仍属于 Adapter 的私有部署配置，不新增 Core DTO。** 每轴必须配置以下完整字段：Axis/Unit/Frame、MappingRevision、Boot/DeviceReferenceRevision、Sign（±1）、Int64 NativeOrigin、有限 double EngineeringOrigin、正 Int64 ScaleNumerator/ScaleDenominator（最大公约数约分，单位为 mm/count 或 deg/count）、Int64 NativeMin/NativeMax、正有限 MaxCommandQuantization（工程位置单位）、非负有限 QualifiedFeedbackError（同单位）。命令脉冲与编码器计数可能不同，必须各有一份具名映射，不能互相套用；原生速度/加速度/跟随误差的单位和比例也各具名，时间基准明确为秒，不能猜 SDK 的 ms/min。若 SDK 已直接返回工程量，配置显式 Identity 映射并保留来源，不再乘齿轮比。坐标补偿不并入该比例。MappingRevision 与全部字段及 SDK 单位解释纳入 Adapter.RuntimeFingerprint/ConfigurationRevision 的版本依据，任一变化必须导致 Capability 摘要变化；基准变化按位置版本规则处理。

绝对位置公式为 `q = EngineeringOrigin + Sign × (n-NativeOrigin) × ScaleNumerator / ScaleDenominator`。差分/速度/加速度只用比例和 Sign，不加两个 origin；following error 同理，若设备只报告误差绝对值则该字段不能冒充有符号误差。实现用 BCL BigInteger 对整数和 binary64 的精确有理表示运算，不能先做可能溢出的 Int64 差/乘。输出 double 采用最近值、偶数中点舍入，结果有限且在能力范围；将表示误差上界向上计入反馈误差资格。最终 RawAxisSample.EncoderPositiveSign 只描述该原生映射方向，Core 对已换算 q **不再乘一次 Sign**。

命令逆变换先求精确有理 `r = NativeOrigin + Sign × (q-EngineeringOrigin) × ScaleDenominator / ScaleNumerator`，按最近整数、中点取偶数舍入为 n；先核 n 在 NativeMin/NativeMax 和 Int64 内，再计算回投影 qn。`abs(qn-q)` 必须 <= MaxCommandQuantization，且 q、qn 以及适用的完整误差包络都在软件限位/批准禁区外；越界拒绝，不能 clamp、改方向或减小目标。目标/TargetVersion 仍绑定用户原 q，qn 作为 ControllerCommand/CompensatedCommand 的命令事实；settled 仍对原 q 判定，容差必须能覆盖该轴已批准的量化/实际反馈误差预算，否则拒绝该配置/请求，不自动放宽容差。脉冲累加相对指令只有能证明与冻结绝对目标等价时才可使用；超时不再累加。

合成算例：Sign=-1、NativeOrigin=100、EngineeringOrigin=10 mm、比例=1/1000 mm/count，则 n=1100 对应 q=9 mm。中点反例另用可精确二进制表示的比例1/1024：q=9.99951171875 mm 逆算 r=100.5，偶数舍入 n=100，回投影10 mm，量化误差1/2048 mm；q=9.99853515625 逆算101.5，舍入102；r=-1.5 舍入-2、r=-2.5 也舍入-2。比例/边界用精确有理数验证，binary64 输入按其实际位值解释，不能用十进制近似相等代替边界断言。原生计数溢出、原点差溢出、非法比例、反向二次乘号、qn 越限、误差预算不足分别是必须拒绝的反例；无原生计数输出时不得编造该计数。

**普通 Move/Relative 的时间由 Core 确定，不留给坐标端口或 UI 猜。** CoordinateQuery显式绑定Kind与冻结的Machine Start（A.4精确声明已补）：Kind仅Move/MoveRelative/Trajectory。Move的InputPath仅一个Offset0目标点、Frame为用户目标Frame；MoveRelative仅一个Offset0点，其Positions表示该Frame的Delta向量，不能解释为绝对位置；Trajectory包含用户完整点列/原Offset，Frame为所有输入点的用户Frame。坐标端口按Kind解析输入，机器Start不参与再次坐标变换。Move返回Machine Start/目标两点，Relative先将Delta向量按固定资产映射到Machine（非线性资产须有批准的局部位移规则，否则拒绝），再checked/有限运算加到冻结Machine Start；相同Frame无外部资产时由Core直接加Delta。Trajectory逐点变换后核首点与Machine Start一致并保持Offset。普通返回路径的Offset仅严格顺序占位，Core随后时间化；Trajectory的Offset始终是用户时间，不自动retime。端口不根据值或tick大小猜Kind，Core不把未知Frame目标与Machine actual相减，也不自行求坐标资产逆变换。

OneSided的preTarget及最后接近方向在机器域解析，端口返回全部几何顶点，普通Move/Relative在Core统一重新时间化。需要OneSided时即使Frame=Machine，仍须请求显式CoordinateAssetSha256指向包含批准接近几何/禁区和各Approach.QualificationAssetSha256引用的资产，传给CoordinateQuery.AssetSha256；不能把null、第一轴资格或当前默认资产补进去。普通Machine/None不调用Coordinates，ControllerQualified只核资格而不追加段。Trajectory没有Approach，端口逐点保持原Offset，只做坐标变换/批准禁区核对，不能插入控制器未批准的路线。几何转换的顺序、资产和最终路径均绑定原请求授权，不变更输入Frame或自动挑变换。该补充只扩未发布的CoordinateQuery端口，不改普通请求/回执codec或旧固定向量；消费适配器须按此Kind/Start实现，不再使用旧缺上下文查询。

普通定位采用每机器顶点停止、每段 rest-to-rest 的名义时间表，禁止隐式 blend。AtomicGroup 每段各轴同时开始/结束，取各轴最小时间最大值；IndependentSerial 先按能力组顺序展开成每段只变化一轴的顶点，其它轴保持，不能用最大值冒充串行总时长。位置距离 d=abs(终点-起点)，v/a 为该段 Profile 正上限，最终 OneSided 段改用显式 FinalApproachProfile。无 jerk 控制时，d=0 的轴时间为0；`d <= v²/a` 时 `T=2√(d/a)`，否则 `T=d/v+v/a`。

有 jerk 上限 j 时采用对称七阶段 S 曲线的名义时间，只推导时间，不在 Core 实现控制器插补：

1. 若 `v >= a²/j`，置 `tj=a/j, ta=v/a-tj`；否则 `tj=√(v/j), ta=0`。到速度上限所需距离 `dv=v×(2tj+ta)`。
2. 若 `d >= dv`，`tv=(d-dv)/v`，保留 tj/ta；若 `d < dv` 且 `d >= 2a³/j²`，`tj=a/j, ta=(-3tj+√(tj²+4d/a))/2, tv=0`；其它情况 `tj=∛(d/(2j)), ta=tv=0`。
3. `T=4tj+2ta+tv`；d=0 单独返回0。每段时间取向上到整 TimeSpan tick 的最大轴 T，非零段至少1 tick，累计 checked，不向下舍入/续请求期限。全路径零位移时保留首末同值点，末点1 tick，仅作可追溯预检，按 §7.1 可零位移设备调用。

名义七段的时长依次为tj/ta/tj/tv/tj/ta/tj，jerk按运动方向依次为+j/0/-j/0/-j/0/+j；零时长段跳过。名义公式使用.NET 10 `Math.Sqrt`/`Math.Cbrt`和有限double逐步检查，向上转TimeSpan tick前不先舍入小数位；数值不能有限表示、tick超Int64或累计超请求剩余Deadline即拒绝。此排程的数值精度不构成实际动力学误差界，Adapter的连续包络核验仍为必需，不能因公式已算而略过。

较短轴按共同段时长同比拉伸，速度/加速度/jerk 只会降低；不是用普通线性插值瞬时转角替代动力学。直接机器 Frame 的路径也执行同一时间化。若有外部路径，解析摘要先核坐标结果；时间化后的最终路径摘要以 A.5 标量规则、domain=`motion-resolved-path-v0.2`、I32(2)、Scope字段、I32(点数)、各 TrajectoryPoint 字段生成，保存为 ExecutionRecord.ResolvedPathSha256，不能继续用时间化前摘要。AdapterPathQuery/QuerySha256 绑定该最终路径、起始原反馈及请求 Profile；OneSided 的 FinalApproachProfile 已在原请求/授权/AdapterCommand 内，ValidatePath 使用较严的原 Profile 与 FinalApproachProfile 的逐轴交集检查附加段。额外段若无法按这个保守交集证明，则拒绝，不替用户选择更快路线。

以上是名义排程，不是对设备实际曲线的证明。Adapter 必须核真实起始速度/加速度、每段零速连接、有限 jerk、停止包络、原生量化和控制器执行时间偏差，给 EnvelopeVerified/DynamicsVerified；SDK 或已资格模型不能执行/证明该时间表则 Unsupported，不能静默改为 ASAP 或忽略 Offset。非零初速不能偷当0，未知初始加速度不能默认合格。Trajectory 只核用户时间表及实际插补器包络，差分只是必要筛查，不能单独证明连续动力学。最后 gate 仍核 Start/配置/身份版本，过期预检不下发。

合成时间反例：d=1、v=2、a=4、无 j 时 T=1 s；d=5 同上 T=3 s；两轴 d=1/5 的 AtomicGroup 为3 s，IndependentSerial 为4 s。j=8、a=4、v=2 时，d=0.25 为纯 jerk 的1 s，d=2 为2 s，d=4 为3 s；d=4.375、a=2、j=4、v=10 得 tj=0.5、ta=0.75、T=3.5 s。这些只是排程公式 oracle；不能将它们包装成真实电机停止距离、客户节拍或已运行轨迹。

### 17.3 断线重连、Recover 与耐久对账

连接故障立即关闭普通写准入并保留原 Session、Adapter、真实 task、ledger/Scope/lease 身份，当前投影 Disconnected/Unknown。**传输重新连接只恢复读取，不等于运动恢复。** 现有 ReadCapabilitiesAsync 可以在已打开逻辑连接内对原固定 endpoint 做一次有限的传输重新绑定，仍使用原 Controller lease/fencing token；不得发现新设备、建立第二写 Owner、Servo/Home/Reset/解锁/改输出。只有 Adapter 能证明旧 native 访问已退出、不会与新传输访问同句柄竞争时才允许；否则返回不可用，继续保留旧 Owner。不支持无副作用重新绑定的厂商适配器显式 Unsupported，不伪造可恢复性。每次显式刷新最多一次重连尝试，失败不后台循环；Simulator 用 Capabilities/故障脚本表示读失败和同身份恢复，Replay 不重连真实设备。

读回同 Controller/Boot/Generation/轴映射/配置时，先查本 Session 原 ledger 与全部未决登记，逐原 OperationId/ControllerSequence 查询；读取源必须能证明实际状态、连续静止、当前联锁、基准和未决 native 资源。Recover 在 gate 外完成这些准备，在控制器屏障内冻结原未决集合/新维护授权；未知执行/登记、尚未退出的 Submit、活 Owner 无正式移交、旧 lease失效、设备不能查原请求时不执行维护解锁，返回原 ID 的 Unknown/Quarantined。只有对账结果已保全、需要解除的 stop-lock 已明确且授权覆盖时，才 Submit 原 Recover 一次，随后回读锁解除/静止/联锁/基准，再耐久写对账回执，才开放相应 Scope。Reset 不复用 Recover 授权，两者不自动串行执行。

若 Boot/Generation/映射变化，原实例保持 Quarantined，不向新设备发送原 Stop/Recover，不把原 operation 成功化。Gateway 可另建只读 Session 获取新身份供维护比较，但不能绕过旧写 lease/未决记录另开写 Session。原未决物理效果须由设备查询、批准的外部安全/维护证据与 Gateway 移交协议处理；核不清时停在 Unknown。关闭旧句柄/进程只证明相应软件资源退出，不能证明原运动/比较输出已停止。Close 的资源、对账两轴及原日志均保留；外部恢复决策由明确的维护/安全 Owner 负责，不能用“设备已重启”填物理证据。

持久 ledger 的端口算法已由 A.4 冻结：Reserve/Commit CAS/事实事件原子性、原意图/路径/授权域保存、完整 pending 分页、尾部回执预留与同 ID 恢复；这些不再待存储 Owner 重新设计。Core 只消费 IOperationLedger，不直接调用通用数据库或自造第二套 SQL/文件。生产组合根负责提供该端口的真实耐久实现、ACL/事务/配额/备份，并执行 §11.1 崩溃点合同测试；缺它只关闭硬件写通道，不影响内存 Simulator。期限到期的 Find/Reserve/Commit 真实 Task 继续由 Session 根持有，晚到 reservation 需以原 ID 只续零下发/清理，不能创建第二流程。

### 17.4 WPF 装配、根 Owner、命令和三语

§8 的公开 Binding/Attach/Detach 形状保持，增加仅 WPF 包的显式根 Owner，用于强持控件、CreateCommand/订阅/Dispatcher 的真实任务；IMotionLifecycleOwner 仍只保留 Session，不能替代 UI 根。公开 `sealed class MotionViewOwner` 的构造为 `MotionViewOwner(int capacity, TimeProvider time)`，方法为 `bool TryRegister(MotionControlView view)`、`ImmutableArray<MotionControlView> GetPending()`、`bool ConfirmReleased(MotionControlView view, DrainResult result)`。capacity正，time非null；同步方法有界不做IO，重复注册同实例成功，容量满返回false。注册时控件与Owner互持，GetPending返回不可变副本；ConfirmReleased 只在该控件的原 Detach 回执匹配当前 BindingGeneration、IsReleased=true，且实际生成器task/枚举器Dispose/Dispatcher待处理/本控件操作和登记均收敛时删除，不能只信调用者构造的 DrainResult。Owner 无设备命令，也不能主动删未归还控件。

默认 MotionControlView 构造零副作用；必须先根 Register，再 Attach(binding)，未注册/错线程/已挂接时 Attach 抛 InvalidOperationException，绑定字段无效抛 ArgumentException，均零设备调用。构造、Register、Attach、SetCulture 和视图状态改变在控件 Dispatcher；Owner 的快照/确认线程安全，实际WPF状态核对由控件Dispatcher准备不可变释放证据，不能在Owner锁内 Dispatcher.Invoke。SetCulture只接受三种基准文化，未知文化回退en-US并在本控件显示语言回退提示，不改宿主文化。ThemeId由宿主验证后局部应用，不设置全局 ApplicationThemeName；主题应用失败保留前主题、显示原因，不阻Stop/Query。

每 Binding 最多一个 CreateCommand 在途；先在本控件根占槽并保存草稿/BindingGeneration，再只调用生成器一次，将返回 ValueTask.AsTask **一次**保存为原Task；预检、普通提交、订阅枚举器MoveNext/Dispose同样记录真实任务。草稿生成与普通读取的UI观察上界为原 ProposedCommand.Context.Deadline 与Profile.DetachBudget较小值，均在调用前开始计时；读取没有草稿时以显式StatusRequest/Query的Deadline与DetachBudget较小值，Core仍独立执行其RuntimeProfile准入与期限检查。UI不读取未公开的Session运行时策略，不在每次 await 重置。超时/取消只结束观察，迟到命令不提交，槽直到实际结束和后处理完才归还；禁止新的草稿生成绕过挂起槽。事件立即入有界UI队列，Dispatcher只呈现当前代；Stop/故障/撤权不等待 RenderPeriod。编辑使用白名单具名草稿，PropertyGrid不反射显示Authorization/原生句柄或秘密。

命令可用性是 Core 准入的保守投影：观察模式没有CreateCommand用途授权；定位模式只有Move/Relative/Trajectory；维护模式在对应能力/用途授权具备时可Home/Jog/Servo/普通配置/Reset/Recover/Compare。Binding不增加自报Role/CanMove布尔授权，CreateCommand拒绝或Core失败显示稳定原因；控件不探测权限或试发命令。普通确认后只派对应 A.2 方法一次；配置逐字段结果展示，Compare保存原RegistrationId；Stop/CompareCancel/Query走§8原身份路径，不经过生成器。授权可能在点击后撤销，UI disabled不代替Core最终检查。ReadOnly绑定普通动作隐藏或禁用并写原因，不请求权限扩大。

Detach 仍按§8顺序执行，但**必须同时**收敛生成器、Preview/普通读取、订阅MoveNext/Dispose、待处理Dispatcher、本控件原operation/登记；取消令牌不构成实际退出证据。Detached成功后才能根ConfirmReleased或重新Attach。失败保留完整Binding/原Task/原ID/控件，Session另交LifecycleOwner，恢复入口只续同控件Detach/原ID Query/Stop，不重复生成普通命令。窗口关闭事件先设置Cancel=true并禁普通动作，异步进行Detach；只有成功才解除Closing拦截，失败显示未确认项并由应用Root保留可查询面板。不得销毁窗口后仅留下Session而丢生成器task，也不得无限等待阻塞UI。Detach观察预算取传入budget与Profile.DetachBudget较小值，用TimeProvider.System单调时钟；预算到期返回DrainUnknown，根继续持有原任务。

以下是资源词表，键固定 `Motion.Command.<名称>`、`Motion.Field.<名称>`、`Motion.State.<枚举名>`，所有§8按钮/表列/动作区只用资源，不以enum.ToString/厂商文本作为标签。其余错误资源的固定生成规则在下段，无未定义显示路线：

| 名称/用途 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Move / MoveRelative / Trajectory | 移动 / 相对移动 / 执行轨迹 | 移動 / 相對移動 / 執行軌跡 | Move / Move relative / Run trajectory |
| Home / Jog / Servo | 回零 / 点动 / 伺服 | 回原點 / 寸動 / 伺服 | Home / Jog / Servo |
| Configuration / Reset / Recover | 应用参数 / 清除故障 / 对账恢复 | 套用參數 / 清除故障 / 核對復原 | Apply settings / Clear fault / Reconcile |
| CompareRegister / CompareCancel | 登记比较输出 / 撤销比较输出 | 登記比較輸出 / 撤銷比較輸出 | Register compare output / Cancel compare output |
| Preview / Query / Stop | 预检 / 查询原操作 / 停止 | 預檢 / 查詢原操作 / 停止 | Preview / Query original operation / Stop |
| Axis / Group / Frame / Unit | 轴 / 轴组 / 坐标系 / 单位 | 軸 / 軸組 / 座標系 / 單位 | Axis / Axis group / Frame / Unit |
| Actual / Target / Velocity / FollowingError | 实际位置 / 目标位置 / 速度 / 跟随误差 | 實際位置 / 目標位置 / 速度 / 跟隨誤差 | Actual position / Target position / Velocity / Following error |
| Acceleration / Jerk / Direction / FeedbackAge | 加速度 / 加加速度 / 方向 / 反馈年龄 | 加速度 / 加加速度 / 方向 / 回饋時間差 | Acceleration / Jerk / Direction / Feedback age |
| Scope / Deadline / PositionTolerance / Dwell | 轴范围 / 期限 / 位置容差 / 连续时长 | 軸範圍 / 期限 / 位置容差 / 連續時間 | Axis scope / Deadline / Position tolerance / Dwell |
| Unknown / Initializing / NotHomed | 未知 / 正在初始化 / 尚未回零 | 未知 / 正在初始化 / 尚未回原點 | Unknown / Initializing / Not homed |
| Homing / Ready / Moving / Settling | 正在回零 / 可接收命令 / 正在移动 / 等待稳定 | 正在回原點 / 可接收命令 / 正在移動 / 等待穩定 | Homing / Ready for command / Moving / Waiting for stability |
| Holding / Interlocked / Faulted / EStopped / Disconnected | 保持已确认 / 联锁阻断 / 设备故障 / 急停已触发 / 已断线 | 保持已確認 / 互鎖阻擋 / 設備故障 / 緊急停止已觸發 / 已斷線 | Hold confirmed / Interlocked / Device fault / Emergency stop active / Disconnected |
| Applied / PartiallyApplied / Unknown（配置） | 已写入 / 部分写入 / 写入结果未知 | 已寫入 / 部分寫入 / 寫入結果未知 | Applied / Partially applied / Write result unknown |
| Historical / Stale / Gap / CleanupPending | 历史记录 / 反馈已过期 / 反馈缺失 / 资源归还待确认 | 歷史記錄 / 回饋已過期 / 回饋缺失 / 資源歸還待確認 | History / Feedback stale / Feedback gap / Resource release unconfirmed |
| ReadOnly / NoPermission / Unsupported / LanguageFallback | 只读连接 / 当前用途未获授权 / 设备不支持 / 此语言不可用，已使用英语 | 唯讀連線 / 目前用途未獲授權 / 設備不支援 / 此語言不可用，已使用英語 | Read-only connection / Purpose not authorized / Device unsupported / Language unavailable; using English |

下列资源覆盖其余公开回执/阶段/布尔值，键为`Motion.<类型>.<值>`，同词可共享资源值但不同语义不合并字段。事件显示组合为“本地化操作名 · 本地化阶段”，保持原EventId/两个序号；不显示CLR枚举名作为操作者文字。

| 类型及值（按序） | zh-CN（按序） | zh-TW（按序） | en-US（按序） |
|---|---|---|---|
| SessionState Created/Open/Closing/Quarantined/Closed | 未连接/已连接/正在关闭/已隔离/已关闭 | 未連線/已連線/正在關閉/已隔離/已關閉 | Not connected/Connected/Closing/Quarantined/Closed |
| Acceptance Rejected/Accepted/PendingReservation | 未接纳/已接纳/等待预留 | 未接納/已接納/等待保留 | Rejected/Accepted/Awaiting reservation |
| ExecutionState Reserved/Submitted/Accepted/Running/Completed/Partial/Cancelled/TimedOut/Failed/Unknown | 已预留/已提交/设备已接受/正在执行/已完成/部分执行/已取消/已超时/失败/执行未知 | 已保留/已提交/設備已接受/正在執行/已完成/部分執行/已取消/已逾時/失敗/執行未知 | Reserved/Submitted/Device accepted/Running/Completed/Partial execution/Cancelled/Timed out/Failed/Execution unknown |
| DrainState NotStarted/Draining/Drained/DrainUnknown | 尚未排空/正在排空/排空已确认/排空未确认 | 尚未清空/正在清空/清空已確認/清空未確認 | Drain not started/Draining/Drain confirmed/Drain unconfirmed |
| ResourceState Held/Released/ReleaseUnknown | 资源持有中/资源已归还/归还未确认 | 資源保留中/資源已歸還/歸還未確認 | Resources held/Resources released/Release unconfirmed |
| DeviceReconciliationState NotRequired/Pending/Confirmed/Quarantined | 无需对账/等待对账/对账已确认/对账隔离 | 無需核對/等待核對/核對已確認/核對隔離 | Reconciliation not required/Awaiting reconciliation/Reconciliation confirmed/Quarantined |
| RegistrationState Loaded/Active/Exhausted/Cancelled/Unknown | 已装载/登记有效/位置表已用尽/已撤销/登记未知 | 已載入/登記有效/位置表已用盡/已撤銷/登記未知 | Loaded/Registration active/Positions exhausted/Cancelled/Registration unknown |
| Direction Unknown/Negative/Positive；Truth Unknown/False/True | 方向未知/负向/正向；未知/否/是 | 方向未知/負向/正向；未知/否/是 | Direction unknown/Negative/Positive; Unknown/No/Yes |
| Quality Unavailable/Stale/Valid；SourceKind Simulation/Replay/Hardware | 不可用/已过期/有效；模拟/历史重放/真实设备 | 無法使用/已過期/有效；模擬/歷史重播/真實設備 | Unavailable/Stale/Valid; Simulation/Replay/Hardware |
| Stage RequestReceived/RequestRejected/Accepted/CommandIssued/FeedbackChanged | 请求已收到/请求未接纳/请求已接纳/命令已发出/反馈已更新 | 請求已收到/請求未接納/請求已接納/命令已發出/回饋已更新 | Request received/Request rejected/Request accepted/Command issued/Feedback updated |
| Stage SettlingStarted/Settled/NotSettled/StopRequested/StopAccepted/PhysicallyStopped/ControllerStopLockReleased | 开始稳定观察/稳定已确认/稳定未确认/已请求停止/设备已接受停止/实际静止已确认/停止锁已解除 | 開始穩定觀察/穩定已確認/穩定未確認/已請求停止/設備已接受停止/實際靜止已確認/停止鎖已解除 | Stability observation started/Stability confirmed/Stability unconfirmed/Stop requested/Device accepted stop/Physical stop confirmed/Stop lock released |
| Stage InterlockChanged/EventGap | 联锁已变化/事件记录缺失 | 互鎖已變更/事件記錄缺失 | Interlock changed/Event gap |

EventKind的LogicalCompleted/LogicalPartial/LogicalCancelled/LogicalTimedOut/LogicalFailed使用相应ExecutionState词前加“逻辑结果：／邏輯結果：／Logical result: ”；它们仍显示单独Drain/Resources列，不表示终态。Draining/Drained/ResourcesReleased复用上述对应字段词；Completed/Partial/Cancelled/TimedOut/Failed使用对应ExecutionState词并显示“终态／終態／Final”，只有§4终态门满足才出现。ClockDomain/Boot/Generation/OperationId/RegistrationId/Sequence/Revision等追溯字段用“时钟域／時鐘域／Clock domain”“启动标识／啟動識別／Boot ID”“代际／世代／Generation”“操作标识／操作識別／Operation ID”“登记标识／登記識別／Registration ID”“序号／序號／Sequence”“版本／版本／Revision”；ID内容原样，不翻译、不展开秘密。

§5每个错误码必须有唯一 `Motion.Error.<去掉MOTION_后的PascalCase名>` 资源，恢复键固定 `Motion.Recovery.<同名>`；已明确的Codec键保持A.5名称。错误正文按三类确定：参数/单位/限位/坐标/能力/权限/状态冲突为“{字段}不满足{要求}。修改后重新预检。”／“{欄位}不符合{要求}。修改後重新預檢。”／“{field} does not meet {requirement}. Correct it and preview again.”；执行/停止/连接/对账未知为“{阶段}未确认。查询原操作 {operationId}。”／“{階段}未確認。查詢原操作 {operationId}。”／“{stage} is unconfirmed. Query original operation {operationId}.”；资源/账本/排空为“{资源}不可用或尚未归还。保留原操作，检查{原因}。”／“{資源}無法使用或尚未歸還。保留原操作，檢查{原因}。”／“{resource} is unavailable or unreleased. Retain the original operation and check {reason}.”。每个Code按§5语义固定到对应类，字段/阶段/要求/资源/原因参数也用资源键，不直接插厂商自然语言；无已知ID显示“未接纳／未接納／Not accepted”，不能构造假ID。Recovery正文复用§5该行的明确下一步，不提供盲重发按钮。确认、读取失败、撤权、历史/模拟/Replay标记、图表各坐标和空/过大输入均走这套资源，SuperTip同时给限制与下一步。未知键沿§8兜底，原码保留可复制。

### 17.5 只读桥的连续覆盖与物理证据边界

A.8的已接收DTO/预像/两Host保持。SourceComplete不是消费者可自填的资格：source必须对请求闭区间提供完整保留水位，首记录tick<=StartTick、末记录tick>=EndTick，且相邻展开Sequence无缺口、同tick成对；若请求边界没有原样本，source可以返回各边界的紧邻外侧原记录作覆盖见证，样本仍保留原tick，不能插值为边界值。因此A.8“窗口之外不得回填或外推”允许紧邻外侧原记录作见证，禁止的是造值/外推。没有两端见证时IsComplete=false；空记录无论SourceComplete自报什么都不能Available/IsComplete。maxSequence限制、截断或保留水位不足同样必须Partial，不得仅因中间两个记录相邻就宣称完整。

已知缺失序号用MotionSequenceGap的闭区间；头/尾缺失序号无法知道时不编造数字：以相邻已知Sequence（无记录则0）作哨兵闭区间、Reason固定`BoundaryCoverageUnknownStart`或`BoundaryCoverageUnknownEnd`、相应Before/After为空，并强制IsComplete=false/Availability=Partial。哨兵只表示无法证明覆盖，不计为“恰丢一个样本”；UI按Reason显示时间边界未知。双边均未知给两条，容量不足不能截掉Gap后报完整。源原Record/Feedback的参考版本与同时采样标记由同一可信Gateway映射产生，Simultaneous=true自身不授物理同步资格；真实硬件必须有§17.7同步时序证据。

MaxSpeedX/Y与MaxAccelerationX/Y都是各轴绝对上界（mm/s、mm/s²），不带运动符号；单位枚举MotionUnit.Millimeter只给基础量纲，阶数由字段固定。若下游需要XY欧氏上界，取 `sqrt(Bx²+By²)` 并向上包络，不取max(Bx,By)；对加速度同理。本桥只回显原分轴上界，欧氏组合由下游显式计算。QualifiedFeedbackError/编码器误差不在v0.1 DTO内，故v0.1只证明原actual来源与时序，不能自证计量位置误差；需要误差资格的消费者另绑定同DeviceReferenceRevision的批准误差资产，缺失不得将误差设0或把时间不确定度当位置误差。新增测量能力须另立明确增量合同，不能默默扩v0.1字段。

### 17.6 确定性装配与增量验收断言

版本字符串是Core不透明投影，但生成不再留给实现者自由选择：每Session的SessionRevision为`SessionId + ":" + 十进制计数`，Created从0起，Open成功/Closing/Quarantined/Closed及能力或配置准入依据变化时加1，不因无关轴actual采样变化而推进；每轴StateVersion=`sv:`加非负Int64十进制计数，PositionVersion=`pv:`同理，从首次建轴的0起，在§3.2所述对应事实实际变化时各加1，同次反馈每类最多加1。计数Ordinal、无前导0，checked溢出关闭普通准入；比较始终连同Session/轴/Boot/Generation，不把`pv:1`当跨会话唯一身份。无实际值/无可信基准时版本仍存在以表示未知投影，不能把该版本用于普通位置准入。TargetVersion保持A.5生成规则。ReadSource导出实际对应Core版本，不自行按样本数造版本；A.8Synthetic的px/py仅为外部已关联历史的不透明测试引用，无需改旧向量。

**最小无设备装配配方 F2**（补充A.7，不替代§10.1物理反例，所有数值Synthetic）：两个入口 ScanHost/PositionHost各用独立SessionId=`scan1`/`position1`、OwnerId=`scan-owner`/`position-owner`、ControllerId=`sim-scan`/`sim-position`；虚拟时间原点2000-01-01T00:00:00Z，TimestampFrequency=10000000，设备d/e为1000Hz。Limits按A.1字段序为`2,64,4,8,1000,128,4194304,4,4,64,4,4`，Runtime CleanupBudget=1s、InterlockFreshness=50ms、MaximumCommandDeadline=5s、LeaseHeartbeatPeriod=10ms；StopPolicy为X/Y各0.01 mm/s、Dwell20ms、Gap10ms、Age10ms、Skew2ms。Runtime/Stop等hash按A.5从实际字段构造，不放任意64位占位hash。

两轴X/Y能力：mm、Machine frame、Sign+1、Position/Velocity/FollowingErrorResolution各0.001、PositionRange[-100,100]、VelocityRange[0.001,10]、AccelerationRange[0.001,20]、JerkRange=null、Features仅Absolute/Relative/Trajectory、HomeModes空、RequiresServoEnable=true、RequiresInPosition=true、HardwareLimitIsAuthoritative=true、MaxFeedbackRateHz=1000、WritableConfigurationFields空、ReportsPositionHold=true、UsesControllerStopLock=false。组XY按X/Y顺序、ResourceKeys为`controllerId:X`/`controllerId:Y`、AtomicSubmission/SupportsTrajectory/SynchronizedFeedback均true；AdapterIdentity=`sim-adapter`/`script-v0.2`/该ControllerId/Simulation，Firmware=`sim-fw-1`、Boot=`b1`、Generation=1、ConfigurationRevision=`cfg1`、Clocks仅d/e、CapturedAtUtc为原点、SupportsIndependentStop=true。这组初始基准由脚本显式声明，不调用Home；Home案例另用§11.1模式专用计划，不能将最小Host的已回零来源冒充现场回零。

所有Raw样本按A.4完整字段构造：X/Y各ControllerCommand=EncoderActual=q、Velocity=0、FollowingError=0、Quality=Valid、Frame=Machine、CoordinateAsset=null、EncoderPositiveSign=1、Homed/Servo/InPosition/PositionHeld=True、双Limit/Fault/ControllerStopLockActive/HomeSwitch/IndexObserved=False、DeviceReferenceRevision=`ref1`、VendorFaultCode=null；Clock=d/e/tick/sequence/1000。初始tick0/seq0/qX=qY=0；之后每10ms提供一帧，seq=tick/10，直至2s。ScanHost的X线性从tick0的0到tick1000的1，Y一直0；PositionHost同样最终X=1，用Move而非轨迹；tick1000–2000保持actual=1。运动中Velocity字段给X=1、Y=0，PositionHeld=False、InPosition=False，末位置从tick1000起全部恢复上述静止事实。该反馈仅是协议脚本，并非名义rest-to-rest曲线或真实动力学；PathValidations显式Synthetic，不声称物理可信。

MotionProfile为X/Y各v=2、a=4、j=null；Settled为X/Y容差位置0.01、速度0.01、跟随误差0.02，Dwell20ms、Gap10ms、Age10ms、Skew2ms。Coordinate端口对Machine/null不被调用；ClockMappings返回d/e到`host:<SessionId>`/SessionId比例10000/1、offset0、error0、valid[0,2000]的固定映射；InterlockSource=`sim-safety`、Boot=b1、同设备时钟/ScopeXY、MotionPermitted/DoorClosed=True、EStop=False、QualityValid，每10ms显式刷新。授权引用为Authority=`fixture-auth`、ScopeId=`fixture-scope`、ReferenceId=`move-permit`或`trajectory-permit`（Open用`read-write-permit`），ReferenceSha256为固定用途UTF-8文本的一次SHA-256；测试端口仅认可该实例Owner/Kind/Scope/实际IntentSha256、有限期限且未撤销，不把这条Synthetic认可用于硬件。

初始Open成功的SessionRevision固定`<SessionId>:1`，首次反馈Unknown→Ready令StateVersion=`sv:1`、actual基准首次建立令PositionVersion=`pv:1`；Start缓存形成屏障前不Advance。普通命令CommandId=`move1`/`trajectory1`、Deadline=2s、ScopeXY、Context取上述完整授权/当前版本和cfg1/capabilityhash。Move目标X1/Y0、FrameMachine、资产null、AtomicGroup、Approach各轴None；Trajectory为t0的0/0和t1s的1/0，同Profile/Settled。两者分别形成同1s最终机器路径，但CommandKind/授权/CommandId不同。期望OperationId按A.5从Owner/fixture-scope/CommandId生成；计划RequestSha256、PathValidation.QuerySha256在创建Adapter之前依本节初始版本、完整路径和请求计算，不能用“接受任意hash”的测试端口避过校验。

SimulationPlan.SchemaVersion=`motion-simulation-v0.2`、Seed=1、Duration=2s、OpenDelay=0、Capabilities/FaultSchedule默认空，InitialFeedback/Feedback/Interlocks用上述完整帧，PathValidations恰一项QuerySha256/True/True/`synthetic-path-v1`/null。Calls正常恰三项：一个普通命令、一个Drain、一个Close。普通RequestId取命令ID、ExpectedResolvedPathSha256取最终路径hash、Delay=0、AdapterReceipt为原operation/Controller/b1/1/ControllerSequence=`synthetic-1`、Execution=Accepted、每轴AdapterAxisReceipt为Accepted/null/null/null/true/true、Stop为未请求、登记/配置revision为空、ConfigurationFields空、DeviceCallMade=true、Failure=null，DrainReceipt=null；CloseRequest为该Owner/`close1`/1s，Call.Kind=Close、RequestId=close1、RequestSha256按A.5、ExpectedResolvedPathSha256=null、Delay=0、Receipt=null、DrainReceipt为Drained/Released/未请求Stop/空pending/null。普通operation的Drain Call键按A.7规范OperationIds摘要、该DrainRequest期限1s，ExpectedResolvedPathSha256=null、Delay=0、Receipt=null，返回同无pending的DrainReceipt。未请求Stop字段为五Truth.Unknown、身份/ID/Policy/Sequence/窗口null、ScopeXY、Witnesses空。fixture异常退出变体额外提供与原身份匹配的Stop脚本和连续静止帧；缺脚本必须测试失败/Retain，不能默认释放。

Host步骤：进程入口先强持有界LifecycleOwner/Adapter候选（容量各2）→构造全部计划/端口→new Adapter（尚未打开）→new MotionSession，成功后转移Adapter所有权→Open→取得初始状态→分别SubmitTrajectory或Move→在每10ms Advance前后await受控屏障让反馈/lease/联锁/actor都消费完→核tick1000/1010/1020形成settled→WaitOperation核原ID/完整终态/归还→finally同实例Close→实际pending计数0才删根。MotionSession构造失败时根持Adapter并按有限预算Dispose；构造成功后只由Session关闭Adapter。Session/Adapter根必须在首次异步调用之前已有强引用，只有确认资源归还才释放。§9的Home调用示例是维护变体，不是F2的必要步骤。共享物理Controller的第二消费者则显式共用同一lease协调器，第二写Open被拒绝；两独立F2不共享缓存/取消/语言。

两个可选WPF Host沿这两套已Open Session构造：应用入口Root先保持LifecycleOwner和`MotionViewOwner(2,TimeProvider.System)`→各STA线程创建Dispatcher/测试Window→new view→TryRegister成功→Attach完整MotionViewBinding。Owner/Scope来自该F2，MotionUiProfile=`RenderPeriod50ms,MaxVisibleSamples512,HistoryRows128,DetachBudget1s`、Culture分别zh-CN/en-US、ThemeId为宿主局部当前主题；CreateCommand只接该Host预先构造的Move或Trajectory草稿，重核Intent/版本后返回新用途授权命令，禁止不同Scope或预算。窗口按§8客户区尺寸创建，不改分辨率；测试入口驱动同样虚拟帧，WPF渲染使用真实Dispatcher/墙钟。finally先Detach并根ConfirmReleased，再由拥有Session的Host Close；Close失败仍保留Session，借用控件不得代宿主关闭Session。第二STA换zh-TW/长英文和不同主题，断言实例隔离。WPF.Tests为net10.0-windows、OutputType=Exe、UseWPF=true，仅引用Wpf/Core/本机25.2.3程序集；唯一运行命令为 `dotnet run --project tests/Modules/motion-control/Asun.Modules.MotionControl.Wpf.Tests/Asun.Modules.MotionControl.Wpf.Tests.csproj -c Release`。每case30s、suite180s、外进程240s墙钟，失败/未知收尾/必需跳过均非零；屏幕不满足唯一viewport时报告未执行，不换用户显示设置。

| 增量断言（加入原§11对应测试类，不另建过程报告） | 可判定结果 |
|---|---|
| Native转换正负/原点/中点/极大整数、qn越限与预算不足 | 精确有理oracle一致；错误零Submit，双Sign转换不发生 |
| 无jerk/三种S曲线、零距离、两轴Atomic/Serial、OneSided最终Profile、时间溢出 | 本节合成时间正确；最终路径hash绑定真实Offset；不做隐藏blend/续期 |
| 首速非零/加速度未知、Adapter不能执行该表、量化后包络越界 | Validate拒绝/Unsupported；不能只凭端点或名义时间下发 |
| 同身份读重连、不同Boot、旧Submit挂起、Recover查不到原登记 | 只重建读取；旧task持有时不重绑；不向新设备发原命令、不自动解锁 |
| Reserve/坐标/授权/预检/Query晚到、根容量满、构造失败 | 调用前保留槽，晚到只续原收敛；不得用await包装释放或遗失Adapter |
| WPF CreateCommand挂起/撤权/卸载、订阅Dispose挂起、旧代Dispatcher | DetachUnknown且View/Session两根保留；受控释放后同实例收敛，旧代零提交 |
| WPF两STA、三语、Enter/Space/Esc、捕获丢失、停止可见、局部主题失败 | §8行为可观察；UI不跨线程、不篡改Profile/hash、不扩权限 |
| XY首尾无见证、maxSequence截断、空历史、gap哨兵、误差资产缺失 | Partial/Unknown、IsComplete=false，保留原tick和原因，不授计量资格 |

这些是后续实现/运行的验收规格，当前未创建工程或执行它们。软件性能沿§12，新增换算/时间化/重连读/生成器/Detach分别计阶段时长、pending槽和内存峰值；真实墙钟P50/P95/P99与虚拟tick分开，客户目标缺失仍NotEvaluated。

### 17.7 全模块结论与精确外部门

当前架构全部IM-010能力的可决定软件设计已在本文闭合，无待开发者选择的换算、排程、恢复、UI资源保留、参数推荐或端口编排方案。S1/S2、Read Bridge的既有 `ModuleCoreImplementationReady` 是规格状态，继续有效；S3/S4/产品集成仍 `PreparationIncomplete`，因为真实编译、适配、部署和资格未完成，不能据文档自审授整模块Ready。后续实现仍由用户指定范围，本次只修本文；总控接收此状态即可，不再设置主控内容复审门。

| 剩余门与Owner | 必须提供的输入/关闭证据 | 只影响的范围 |
|---|---|---|
| 实现任务/代码组合根Owner | 权威仓库/分支、明确批准的实现范围 | 对应工程创建/实现；不是文档设计欠账 |
| IM-064/目标控制器Adapter Owner | SDK公共签名/线程/单位/Stop/句柄回收；实现本文端口、原生映射和路径预检，不能反向改Core或伪造资格 | 实际厂商Adapter，不阻Simulator/Core |
| 设备/机械/计量Owner | 各轴原生比例/正向/量程、回差/限位/停止距离、Home程序和基准、反馈误差、jerk/插补/同步时序资格 | 硬件参数与物理精度/运动资格 |
| 安全PLC/现场安全Owner | 联锁来源/期限、安全链复归、断线/断电/急停后的实际动作和允许恢复证据 | 实机恢复与HIL/FAT/SAT，不授软件安全权 |
| Gateway/部署/持久存储Owner | 跨进程唯一lease及fencing/移交、真实耐久IOperationLedger、完整pending扫描/崩溃恢复/ACL/配额/备份，持久历史保留水位 | 硬件写与历史服务；不要求Core选数据库 |
| 权限/产品宿主Owner | 可信用途授权签发/撤权、扫描/定位/维护Profile、MotionActual正式映射和产品恢复流程 | 对应产品组合/流程，不阻独立模块调用 |
| ReadSource/时钟/动态资格Owner | 同tick XY与原Core位置版本关联、时钟映射/误差/保留水位、同run分轴速度/加速度物理包络和误差资产 | 真线扫/计量用途；缺失明确NotSupported/Unknown |
| WPF实现与验收Owner（本模块后续切片） | 25.2.3真实编译、1920×1080客户区/实际DPI、三语键盘/UIA、两STA与卸载原Task验证 | S3运行资格；不是未来重新设计控件的门 |
| 消费者验收/性能/现场Owner | 采用的BenchmarkProfile阈值、独立两Host及真实样本/设备Golden、长稳/HIL/FAT/SAT/回退 | 对应性能、集成及生产资格 |

原会话自审覆盖正常定位/轨迹、反向回差、限位、未知动力学、Home证据、Servo/配置部分写、Jog与Compare、停止/锁/排空、断线对账、只读桥覆盖、两个消费者及UI卸载。已复用的研究/旧向量不重复复算；本轮定向检查新增数学分支、字段装配、任务根持有与文档引用。内存精确有理数核验正负中点和回投影、名义时间oracle及216组S曲线距离/速度/加速度关系一致；据核验修正一个加速度受限分支的算例距离（4.375对应3.5s）。`python -B tools/validate_docs.py`文档完整性校验通过，章节/代码围栏定向检查通过；这些只证明所列数学/文档性质，不是实现测试或语义完备的自动证明。未执行C#构建、Core/Simulator/Replay产品测试、真实WPF、性能测量、SDK/HIL、物理Golden或现场验收。


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

## 附录 A：Module API Contract v0.2（Core/Simulator/Port 规格；逐切片状态见 A.6）

本附录与正文共同构成唯一 Core 规格；以下是**规定的公开声明**，不声称已有程序集或编译通过。所有类型在 `Asun.Modules.MotionControl`，BCL `System`、`System.Threading`、`System.Threading.Tasks`、`System.Collections.Immutable`；无 HALCON/AsunImage/DevExpress 依赖。不可变 record/record struct；集合为 ImmutableArray/ImmutableDictionary，接纳时有界复制，default 集合视为空并拒绝必需字段。表格中的 `T?` 为可空值，缺失不等于零。标识非空 ASCII 1–64（CommandId/OperationId/摘要引用允许最多 128）；hash 为 64 位小写十六进制。UTC 只审计，期限/年龄均以单调 TimeProvider 或设备域解释。

### A.1 标量、枚举、能力和策略

枚举持久编号按以下列出的左至右顺序从 0 起冻结，不允许插入重排；未知值拒绝。新增值升契约版本并显式映射，不让 default=0 隐式成立：

- `MotionUnit`：Millimeter, Degree；`MotionState`：Unknown, Initializing, NotHomed, Homing, Ready, Moving, Settling, Holding, Interlocked, Faulted, EStopped, Disconnected。
- `SessionState`：Created, Open, Closing, Quarantined, Closed；`Truth`：Unknown, False, True；`Quality`：Unavailable, Stale, Valid。
- `SourceKind`：Simulation, Replay, Hardware；`Direction`：Unknown, Negative, Positive；`SubmissionMode`：AtomicGroup, IndependentSerial。
- `MotionFeature`：Home, Jog, Servo, Absolute, Relative, Trajectory, Compare；`HomeMode`：Switch, Index, SwitchThenIndex, AbsoluteReference。
- `ApproachMode`：None, ControllerQualified, OneSided；`Acceptance`：Rejected, Accepted, PendingReservation。
- `ExecutionState`：Reserved, Submitted, Accepted, Running, Completed, Partial, Cancelled, TimedOut, Failed, Unknown。
- `DrainState`：NotStarted, Draining, Drained, DrainUnknown；`ResourceState`：Held, Released, ReleaseUnknown；`DeviceReconciliationState`：NotRequired, Pending, Confirmed, Quarantined。
- `RegistrationState`：Loaded, Active, Exhausted, Cancelled, Unknown；`ConfigurationOutcome`：Applied, PartiallyApplied, Unknown。
- `CommandKind`：Open, Configuration, Home, Move, MoveRelative, Trajectory, Jog, Servo, CompareRegister, CompareCancel, Stop, Reset, Recover, Close, Drain。
- `EventKind`：RequestReceived, RequestRejected, Accepted, CommandIssued, FeedbackChanged, SettlingStarted, Settled, NotSettled, StopRequested, StopAccepted, PhysicallyStopped, ControllerStopLockReleased, LogicalCompleted, LogicalPartial, LogicalCancelled, LogicalTimedOut, LogicalFailed, Draining, Drained, ResourcesReleased, Completed, Partial, Cancelled, TimedOut, Failed, InterlockChanged, EventGap。
- `DiagnosticSeverity`：Trace, Info, Warning, Error, Critical；`DiagnosticKind`：Startup, Command, Feedback, Limit, Home, Stop, Timeout, Recovery, Resource, Drain。

下表逐行规定 sealed record 的全部构造字段；未列的物理参数不能由实现者新增默认值。Unit 的时间导数量纲按字段名称（Velocity/Acceleration/Jerk）确定：

| 类型 | 精确字段（C# 类型 + 名称，按序） |
|---|---|
| AxisId / CoordinateFrameId | readonly record struct，各为 string Value |
| NumericRange | double Min, double Max；有限、Min <= Max、闭区间 |
| MotionValue | double Value, MotionUnit Unit |
| AxisScope | string? GroupId, ImmutableArray<AxisId> Axes |
| ClockStamp | string DomainId, string Epoch, long Tick, long Sequence, long TickFrequency；非负展开 Tick/Sequence、正 Frequency |
| ClockDescriptor | string DomainId, string Epoch, long TickFrequency, bool CounterUnwrapped；声明而非实时样本，CounterUnwrapped 必须 true |
| AdapterIdentity | string AdapterId, string RuntimeFingerprint, string ControllerId, SourceKind Source |
| ResourceLimits | int MaxAxesPerCommand, int MaxTrajectorySamples, int MaxInFlightOperations, int MaxQueuedCommands, int MaxFeedbackRateHz, int MaxEventLag, long MaxRetainedBytes, int MaxSubscribers, int MaxReadQueries, int MaxComparePoints, int MaxRegistrations, int MaxStopRequests；全部正有限 |
| AxisCapability | AxisId Axis, MotionUnit Unit, CoordinateFrameId Frame, int EncoderPositiveSign, double PositionResolution, double VelocityResolution, double FollowingErrorResolution, NumericRange PositionRange, NumericRange VelocityRange, NumericRange AccelerationRange, NumericRange? JerkRange, ImmutableArray<MotionFeature> Features, ImmutableArray<HomeMode> HomeModes, bool RequiresServoEnable, bool RequiresInPosition, bool HardwareLimitIsAuthoritative, int MaxFeedbackRateHz, ImmutableArray<string> WritableConfigurationFields, bool ReportsPositionHold, bool UsesControllerStopLock |
| AxisGroupCapability | string GroupId, ImmutableArray<AxisId> Axes, ImmutableArray<string> ResourceKeys, bool AtomicSubmission, bool SupportsTrajectory, bool SynchronizedFeedback |
| MotionCapabilitySnapshot | AdapterIdentity Identity, string FirmwareFingerprint, string BootId, long Generation, string SnapshotSha256, string ConfigurationRevision, ResourceLimits Limits, ImmutableArray<AxisCapability> Axes, ImmutableArray<AxisGroupCapability> Groups, ImmutableArray<ClockDescriptor> Clocks, DateTimeOffset CapturedAtUtc, bool SupportsIndependentStop |
| AxisDynamics | AxisId Axis, MotionValue Velocity, MotionValue Acceleration, MotionValue? Jerk |
| MotionProfile | string ProfileSha256, ImmutableArray<AxisDynamics> Axes；每 Scope 轴恰一项 |
| AxisSettledPolicy | AxisId Axis, MotionValue PositionTolerance, MotionValue VelocityTolerance, MotionValue FollowingErrorTolerance |
| SettledPolicy | string PolicySha256, ImmutableArray<AxisSettledPolicy> Axes, TimeSpan Dwell, TimeSpan MaxSampleGap, TimeSpan MaxFeedbackAge, TimeSpan MaxAxisSkew |
| ApproachPolicy | AxisId Axis, ApproachMode Mode, Direction RequiredDirection, MotionValue? ApproachDistance, MotionProfile? FinalApproachProfile, string? QualificationAssetSha256；OneSided 全字段必需 |
| AxisStopPolicy | AxisId Axis, MotionValue VelocityTolerance；正且不低于可分辨速度，停止不需要目标位置/坐标资产 |
| MotionStopPolicy | string PolicySha256, ImmutableArray<AxisStopPolicy> Axes, TimeSpan Dwell, TimeSpan MaxSampleGap, TimeSpan MaxFeedbackAge, TimeSpan MaxAxisSkew |
| RuntimeProfile | string ProfileSha256, ResourceLimits Limits, TimeSpan CleanupBudget, TimeSpan InterlockFreshness, TimeSpan MaximumCommandDeadline, TimeSpan LeaseHeartbeatPeriod, MotionStopPolicy StopPolicy |
| MotionAuthorization | string AuthorityId, string ScopeId, string ReferenceId, string ReferenceSha256；均为不透明可信引用，不放秘密 |
| AxisExpectedVersion | AxisId Axis, string StateVersion, string PositionVersion |
| AxisTargetVersion | AxisId Axis, string TargetVersion；目标身份，不是实时 actual 版本 |
| OperationPrecondition | string ExpectedSessionRevision, string ExpectedBootId, long ExpectedGeneration, string ExpectedCapabilitySha256, string ExpectedConfigurationRevision, ImmutableArray<AxisExpectedVersion> Axes |
| CommandContext | string OwnerId, string CommandId, MotionAuthorization Authorization, OperationPrecondition Preconditions, TimeSpan Deadline |
| AxisConfigurationDraft | AxisId Axis, MotionValue? SoftMin, MotionValue? SoftMax, MotionValue? DefaultVelocity, MotionValue? DefaultAcceleration, CoordinateFrameId Frame, string BaseConfigurationRevision |
| HomeAxisPolicy | AxisId Axis, string HomePolicyId, string HomePolicySha256, HomeMode Mode, Direction SearchDirection, NumericRange SearchEnvelope, bool RequiresSwitchLatch, bool RequiresIndex, MotionValue ReferenceOffset |
| TrajectoryPoint | TimeSpan Offset, ImmutableDictionary<AxisId,MotionValue> Positions |
| StopIdentity | string ControllerId, string BootId, long Generation, string OwnerId |
| StopEvidence | Truth Requested, Truth Accepted, Truth PhysicallyStopped, Truth ControllerLockReleased, Truth NativeDrained, string? StopId, StopIdentity? Identity, AxisScope Scope, string? PolicySha256, string? ControllerSequence, ClockStamp? Start, ClockStamp? End, ImmutableArray<RawAxisSample> Witnesses；未请求时身份/窗口为 null、Witnesses 为空，不伪造 False=已停 |
| ControllerLease | string LeaseId, string ControllerId, string OwnerId, long FencingToken, bool IsWrite, TimeSpan Remaining；FencingToken 单调，物理所有权先于 Open，设备 Boot/Generation 另由 Open 回读，失效只停不续跑 |

数量/上限采用能力与 RuntimeProfile 对应项的较小正值；profile hash 缺失或范围矛盾拒绝 Open 写通道。MaxStopRequests 预留于 Open，不能借给普通队列。时间均正且 <= MaximumCommandDeadline，CleanupBudget 独立正有限，不能从客户节拍猜值。double 的 checked 不足以捕获浮点溢出：每次运算后再核 IsFinite/范围；canonical 将 -0 规范为 +0，拒绝 NaN/Infinity。ID 比较 Ordinal；不大小写折叠。

PositionResolution/VelocityResolution/FollowingErrorResolution 均正有限且按该轴单位分别为位置、位置/s、位置；各 tolerance 至少对应 resolution。运动速度/加速度/jerk 为正有限且位于对应能力闭区间，方向独立；Jerk=null 仅声明设备 Profile 不使用 jerk 控制，Trajectory 若无法证明转接的 jerk/包络仍 Unsupported。OneSided 的 ApproachDistance 正有限、FinalApproachProfile 全 Scope 完整；None 时 RequiredDirection=Unknown、距离/Profile/资格资产为空；ControllerQualified 必须有资格资产，不追加 Core 补偿段。ClockDescriptor.DomainId 唯一，每轴原始时钟须能关联声明域。

### A.2 命令、查询和会话入口

`MotionCommand` 为 abstract record，构造字段 `CommandContext Context, AxisScope Scope`；下表命令继承它，新增字段按序，Common 不再重复序列化。Open/Stop/Close 为特殊类型不继承普通位置命令。轴配置普通字段只能按能力允许写入；Home/Jog/Servo 的参数单位必须逐轴相符。

| 类型 | 除 Common 外的精确字段 |
|---|---|
| OpenRequest（独立 record） | string OwnerId, string CommandId, string ControllerId, bool ReadOnly, MotionAuthorization Authorization, TimeSpan Deadline |
| MoveRequest | ImmutableDictionary<AxisId,MotionValue> Target, CoordinateFrameId Frame, string? CoordinateAssetSha256, MotionProfile Profile, SettledPolicy Settled, SubmissionMode Submission, ImmutableArray<ApproachPolicy> Approach |
| RelativeMoveRequest | ImmutableDictionary<AxisId,MotionValue> Delta, CoordinateFrameId Frame, string? CoordinateAssetSha256, MotionProfile Profile, SettledPolicy Settled, SubmissionMode Submission, ImmutableArray<ApproachPolicy> Approach；Start 来自 Preconditions.Axes 的位置版本 |
| TrajectoryRequest | ImmutableArray<TrajectoryPoint> Points, CoordinateFrameId Frame, string? CoordinateAssetSha256, MotionProfile Profile, SettledPolicy Settled；只允许 AtomicGroup |
| HomeRequest | ImmutableArray<HomeAxisPolicy> Policies, MotionProfile Profile, SettledPolicy Settled |
| JogRequest | AxisId Axis, Direction Direction, MotionProfile Profile, TimeSpan MaxDuration, TimeSpan HeartbeatTimeout, string MaintenanceEnvelopeSha256 |
| JogHeartbeatRequest（独立 record） | StopIdentity Identity, string OperationId, long Sequence；只续原 deadman |
| ServoRequest | bool Enable, string MaintenancePolicySha256 |
| ConfigurationRequest | ImmutableArray<AxisConfigurationDraft> Drafts |
| CompareTriggerRequest | AxisId Axis, string OutputChannelRef, ImmutableArray<MotionValue> Points, Direction Direction, MotionValue Hysteresis, CoordinateFrameId Frame, string? CoordinateAssetSha256, string RegistrationRevision, string ClockDomainId, string ClockEpoch |
| CompareCancelRequest（独立 record） | StopIdentity Identity, string StopId, string RegistrationId, TimeSpan Deadline |
| StopRequest（独立 record） | StopIdentity Identity, string StopId, AxisScope Scope, string? OperationId, TimeSpan Deadline；只受原所有权和身份验证 |
| ResetRequest | string MaintenancePolicySha256 |
| RecoverRequest | ImmutableArray<string> UnresolvedOperationIds, string RecoveryPolicySha256；不得仅靠调用者“已停”声明 |
| StatusRequest | AxisScope Scope, TimeSpan MaxAge, TimeSpan Deadline |
| SettledRequest | string OperationId, AxisScope Scope, ImmutableArray<AxisTargetVersion> ExpectedTargetVersions, SettledPolicy Policy, TimeSpan Deadline |
| MotionOperationQueryRequest | string OwnerId, string OperationId, TimeSpan Deadline |
| OperationWaitRequest | MotionOperationQueryRequest Query, TimeSpan Deadline |
| MotionSubscription | string OwnerId, AxisScope Scope, long? AfterEventSequence, int Capacity |
| DrainRequest | string OwnerId, ImmutableArray<string> OperationIds, TimeSpan Deadline |
| CloseRequest | string OwnerId, string CloseId, TimeSpan Deadline |

所有请求边界字节受 MaxRetainedBytes；空/重复/超限在分配/设备调用前拒绝。Home 等公共方法的 Context/Scope 由基类构造传入，不再另造字段。接口声明如下；`MotionSession(MotionDependencies dependencies, RuntimeProfile profile)` 为唯一构造，初态 Created：

```csharp
public interface IMotionSession : IAsyncDisposable
{
    string SessionId { get; }
    SessionState SessionState { get; }
    MotionCapabilitySnapshot? GetCapabilities();
    MotionStatusSnapshot GetStatus(StatusRequest request);
    ValueTask<MotionCapabilitySnapshot?> GetCapabilitiesAsync(CancellationToken ct);
    ValueTask<MotionStatusSnapshot> GetStatusAsync(StatusRequest request, CancellationToken ct);
    ValueTask<MotionPreviewResult> PreviewAsync(MotionCommand request, CancellationToken ct);
    ValueTask<MotionOperation> OpenAsync(OpenRequest request, CancellationToken ct);
    ValueTask<MotionOperation> MoveAsync(MoveRequest request, CancellationToken ct);
    ValueTask<MotionOperation> MoveRelativeAsync(RelativeMoveRequest request, CancellationToken ct);
    ValueTask<MotionOperation> SubmitTrajectoryAsync(TrajectoryRequest request, CancellationToken ct);
    ValueTask<MotionOperation> HomeAsync(HomeRequest request, CancellationToken ct);
    ValueTask<MotionOperation> JogAsync(JogRequest request, CancellationToken ct);
    ValueTask<HeartbeatResult> JogHeartbeatAsync(JogHeartbeatRequest request, CancellationToken ct);
    ValueTask<MotionOperation> SetServoAsync(ServoRequest request, CancellationToken ct);
    ValueTask<ConfigurationResult> ApplyAxisConfigurationAsync(ConfigurationRequest request, CancellationToken ct);
    ValueTask<CompareTriggerResult> RegisterCompareTriggerAsync(CompareTriggerRequest request, CancellationToken ct);
    ValueTask<CompareTriggerResult> CancelCompareTriggerAsync(CompareCancelRequest request, CancellationToken ct);
    ValueTask<MotionOperation> StopAsync(StopRequest request, CancellationToken ct);
    ValueTask<MotionOperation> ResetAsync(ResetRequest request, CancellationToken ct);
    ValueTask<MotionOperation> RecoverAsync(RecoverRequest request, CancellationToken ct);
    ValueTask<SettledResult> WaitForSettledAsync(SettledRequest request, CancellationToken ct);
    ValueTask<MotionOperationReceipt> QueryOperationAsync(MotionOperationQueryRequest request, CancellationToken ct);
    ValueTask<MotionOperation> WaitOperationAsync(OperationWaitRequest request, CancellationToken ct);
    IAsyncEnumerable<MotionEvent> SubscribeAsync(MotionSubscription request, CancellationToken ct);
    ValueTask<DrainResult> DrainAsync(DrainRequest request, CancellationToken ct);
    ValueTask<DrainResult> CloseAsync(CloseRequest request, CancellationToken ct);
}
```

GetCapabilities 在未成功 Open 时 null，不触发隐式连接；异步版本读回沿 RuntimeProfile 的有限只读预算（MaximumCommandDeadline），不能无界等待。StatusRequest.Scope 可空仅用于“全已知轴”的只读查询，普通写 Scope 不可空。非正常输入返回结构化 Rejected；构造依赖缺失抛 ArgumentException，使用已经确认 Closed 的普通入口返回 MOTION_CONTROLLER_UNAVAILABLE，不向设备写入。QueryOperation/WaitOperation 的 NotFound 返回原查询失败，不创操作，不证明“未发生动作”；WaitOperation 为此返回 OperationId=查询 ID、Acceptance=Rejected、Execution=Unknown、Failure，不能用该对象更新 ledger。

ReadOnly Open 仍验证指定身份/读取用途授权和只读 lease，但不要求耐久写账本，也不启动任何设备输出/Servo/复位。其连接回执保存在本 Session 的有界缓存；读取的 ledger 可为不可写。普通写、Stop/CompareCancel 一律零下发拒绝，Close 只关闭本只读连接/订阅并归还只读 lease，不停止其它写 Owner。Replay 仅允许此路径，能力 Source=Replay；原历史回执保持原身份，投影另标 Replay。普通硬件 Open 必须先取得唯一写 lease 和可写原子 ledger。重复 Open 同 ID/内容只查询原打开结果；不同 ID 再次 Open 返回状态冲突，不二次连接；已确认 Closed 后只能新建 Session，不复活原实例。

### A.3 反馈、回执和事件

| 类型 | 精确字段 |
|---|---|
| AxisFeedback | AxisId Axis, MotionState State, string StateVersion, string PositionVersion, string? TargetVersion, MotionValue? Target, MotionValue? ControllerCommand, MotionValue? EncoderActual, MotionValue? CompensatedCommand, MotionValue? Velocity, MotionValue? FollowingError, Quality Quality, CoordinateFrameId Frame, string? CoordinateAssetSha256, int EncoderPositiveSign, Direction LastApproach, Truth Homed, Truth Servo, Truth InPosition, Truth PositiveLimit, Truth NegativeLimit, Truth Fault, ClockStamp Clock, long ReceivedAtTimestamp, Truth PositionHeld, Truth ControllerStopLockActive, string? VendorFaultCode, Truth HomeSwitch, Truth IndexObserved |
| InterlockSnapshot | string SourceId, string BootId, ClockStamp Clock, AxisScope Scope, Truth MotionPermitted, Truth DoorClosed, Truth EStopActive, long ReceivedAtTimestamp, Quality Quality |
| MotionStatusSnapshot | string SessionId, SessionState SessionState, string SessionRevision, string? BootId, long? Generation, ImmutableArray<AxisFeedback> Axes, InterlockSnapshot? Interlock, long ReceivedAtTimestamp, TimeSpan Age, SourceKind? Source, MotionFailure? Failure；Open 前身份/联锁不可用不能补空字符串 |
| AxisSettledEvidence | AxisId Axis, MotionValue FinalActual, string FinalPositionVersion, MotionValue MaximumPositionError, MotionValue MaximumVelocity, MotionValue MaximumFollowingError |
| SettledEvidence | string OperationId, string PolicySha256, string CapabilitySha256, string? CoordinateAssetSha256, string BootId, long Generation, ClockStamp Start, ClockStamp End, ImmutableArray<AxisTargetVersion> TargetVersions, ImmutableArray<AxisSettledEvidence> Axes, SourceKind Source |
| SettledResult | bool IsSettled, SettledEvidence? Evidence, MotionFailure? Failure；IsSettled=true 当且仅当完整有效 Evidence |
| MotionPreviewResult | bool IsValid, string IntentSha256, AxisScope Scope, ImmutableArray<AxisFeedback> Start, ImmutableArray<TrajectoryPoint> ResolvedMachinePath, string? ResolvedPathSha256, string? CapabilitySha256, string? ConfigurationRevision, AdapterPathValidation? PathValidation, MotionFailure? Failure；只用于 Move/Relative/Trajectory 草稿，IsValid 不授予动作许可 |
| HomeEvidence | AxisId Axis, string HomePolicySha256, Truth SwitchLatched, Truth IndexObserved, Truth ReferenceCommitted, string? ReferencePositionVersion, ClockStamp Start, ClockStamp End, ClockStamp? SwitchLatch, ClockStamp? IndexLatch, ClockStamp? ReferenceCommit |
| AxisOperationResult | AxisId Axis, ExecutionState Execution, AxisFeedback? Start, AxisFeedback? Final, MotionValue? ResolvedTarget, HomeEvidence? Home, MotionFailure? Failure, bool DeviceCallMade, bool PossiblePhysicalEffect |
| MotionExecutionRecord | CommandKind Kind, string ControllerId, string? CapabilitySha256, string? ConfigurationRevision, string RuntimeProfileSha256, ImmutableArray<AxisTargetVersion> TargetVersions, ImmutableArray<TrajectoryPoint> ResolvedMachinePath, string? ResolvedPathSha256, ImmutableArray<ClockMapping> ClockMappings, ImmutableArray<AxisId> IssuedAxes, ImmutableArray<AxisId> ConfirmedNotIssuedAxes, bool SubmissionIntentCommitted, string? ControllerSequence, AdapterPathValidation? PathValidation；只保存原版本，不从当前快照补历史 |
| MotionFailure | string Code, string MessageKey, ImmutableDictionary<string,string> Parameters, bool Retryable, string? OperationId, string? StateVersion, bool DeviceCallMade, bool PossiblePhysicalEffect, string? VendorCode, string RecoveryKey |
| MotionOperation | string? OperationId, string CommandId, string OwnerId, string RequestSha256, long Revision, Acceptance Acceptance, ExecutionState Execution, DrainState Drain, ResourceState Resources, DeviceReconciliationState Reconciliation, AxisScope Scope, string? BootId, long? Generation, ImmutableArray<AxisOperationResult> Axes, SettledEvidence? Settled, StopEvidence Stop, bool DeviceCallMade, bool LedgerUnknown, long StartedAtTimestamp, DateTimeOffset AuditTimeUtc, MotionFailure? Failure, MotionExecutionRecord? ExecutionRecord, string AuthorityScope, ImmutableArray<byte> CanonicalRequest, SourceKind? Source, CompareRegistrationRecord? CompareRegistration, string SessionId, long TimestampFrequency；未接纳可为 null，提交意图前已知字段必须完整保全；Open 未读回时能力/配置/Boot/Generation 为 null，不能造空 hash |
| MotionOperationReceipt | bool Found, MotionOperation? Operation, MotionFailure? Failure |
| FieldConfigurationResult | AxisId Axis, string FieldName, MotionValue? Requested, MotionValue? ReadBack, ConfigurationOutcome Outcome, MotionFailure? Failure |
| ConfigurationResult | MotionOperation Operation, ConfigurationOutcome Outcome, ImmutableArray<FieldConfigurationResult> Fields, string? ConfirmedConfigurationRevision |
| CompareTriggerResult | MotionOperation Operation, string? RegistrationId, RegistrationState State, string? ConfirmedRevision |
| CompareRegistrationRecord | string RegistrationId, string RegistrationOperationId, RegistrationState State, string? ConfirmedRevision, DrainState Drain, ResourceState Resources；原登记 operation/Scope/Boot/Generation/Owner 由所属 MotionOperation 固定，登记独占资源与 operation 资源分开 |
| HeartbeatResult | bool Accepted, long LastAcceptedSequence, TimeSpan RemainingMaxDuration, MotionFailure? Failure |
| DrainResult | string SessionId, DrainState Drain, ResourceState Resources, bool IsReleased, ImmutableArray<string> PendingOperationIds, MotionFailure? Failure |
| MotionEvent | string EventId, string SessionId, string? OperationId, long EventSequence, long? OperationEventSequence, EventKind Kind, AxisScope Scope, string SessionRevision, string? BootId, long? Generation, ClockStamp? DeviceClock, long ReceivedAtTimestamp, SourceKind? Source, long? OperationRevision, MotionFailure? Failure |
| MotionDiagnostic | MotionEvent Event, DiagnosticSeverity Severity, DiagnosticKind Kind, ImmutableArray<AxisFeedback> Feedback, StopEvidence Stop, TimeSpan Deadline, TimeSpan Elapsed, TimeSpan LastFeedbackAge, int QueueDepth, string MessageKey, ImmutableDictionary<string,string> Parameters |
| MotionEventQuery | string OwnerId, string SessionId, long AfterSequence, int Capacity, TimeSpan Deadline；AfterSequence >= 0，Capacity 正且 <= MaxEventLag |
| MotionEventPage | bool Found, ImmutableArray<MotionEvent> Events, long NextSequence, bool HasMore, MotionFailure? Failure；只读历史，不创建事件 |
| PendingOperationQuery | string ControllerId, string RequestingOwnerId, string? AfterOperationId, int Capacity, TimeSpan Deadline；Capacity 正且受 MaxInFlightOperations/MaxRegistrations 合成限额 |
| PendingOperationPage | ImmutableArray<MotionOperation> Operations, string? NextOperationId, bool HasMore, MotionFailure? Failure；按 OperationId Ordinal 返回未决 operation 和资源未 Released 的所有登记（含 Loaded/Active/Unknown/Exhausted/Cancelled），不能只找 Execution=Running |

MotionOperation 不含可变 SDK 对象或引用方授权秘密；Configuration/Compare 的嵌套 Operation 遵守相同终态规则。DrainResult.IsReleased 只在所请求范围 Drained 且 Resources=Released 时为 true，不证明安全；有未知物理动作时须 Reconciliation=Pending/Quarantined，operation 不发布 Completed。坐标资产摘要仅在实际使用外部变换/误差图时必需；直接设备 Machine 轴坐标明确 Frame/方向/单位/基准版本并绑定 CapabilitySha256，无外部变换时 CoordinateAssetSha256=null，不捏造校准资产。Home 以新 ReferencePositionVersion/机器基准判 settled；Servo/配置/Compare 不产生定位完成时 Settled=null。Nullability 不可用与 stale 质量分开；回执中的历史字段永不被新能力快照覆盖。

MotionExecutionRecord 在提交意图前完整保存，TargetVersions 是接纳时冻结的独立 TargetVersion，不能拿不断变化的 SampleSequence 代替。IssuedAxes 表示已提交或提交结果未知，ConfirmedNotIssuedAxes 只包含明确未调用的轴，二者不交；未能证明的执行结果保持 Unknown。重启只使用此记录/原 ledger 与 Adapter.QueryOperationAsync 对账；缺记录、控制器无法按序列查询或身份变更都隔离，不据 NotFound 重发。ControllerId 直接保存在原 ExecutionRecord；CanonicalRequest 保存完整原请求，AuthorityScope 保全原幂等域，Source 为原来源（未识别时 null），不以当前授权/快照代替。

回执 SessionId/TimestampFrequency 绑定 StartedAtTimestamp 的原主机域/频率，重启不能把旧 timestamp 当新 Session 的计时起点。新 Session 只能对账历史 deadline 结果，不能续期或根据新时钟复活动作；RuntimeProfileSha256 保全原清理/容量/StopPolicy 的配置依据。账本只读投影和 Replay 保持这些原字段，显示语言与当前 Profile 不改写它们。

Subscribe.AfterEventSequence 是当前 SessionId 的流 cursor，不是某 operation 序号；OperationEventSequence 在会话事件为 null。不订阅全部 Scope 也可能看到流序号缺口，不能单凭数字跳跃推断设备事实丢失；只有显式 EventGap 才表示订阅保留不足。事实事件与回执经同一 Commit CAS 原子提交后投影，事件重投保留同 EventId/两种序号，不生成第二终态。ledger 的 ReadEventsAsync 仅返回该 Owner/Session 已保全事实事件，未保存的普通 feedback projection 不补造；UI gap 后先 Query 原回执，可再读历史事实，无法完整回放投影时明确显示缺口。

登记成功先把 RegistrationId/State/Revision 保全到原 MotionOperation.CompareRegistration，再返回 CompareTriggerResult；取消确认先推进原登记记录，再完成取消操作回执。任一 ledger 写未知保持登记资源 Held/Unknown，不发布已释放；重查只续对账/撤销，不重新装载比较表。Close 从原 Session 与 ReadPendingAsync 取全部登记，不能因为其装载 operation 已 Completed/ResourcesReleased 就遗漏。Exhausted 只有设备证明该登记不再输出且撤销/排空资源已确认时才能移出待收敛集合；未确认仍由 pending 查询保留。

写 Open 的耐久 ledger 必须能完整分页查询该 Controller 的未决记录（包含其它 Owner 的未决身份），仅返回空的私人 ledger 不能证明控制器无未知动作。跨 Owner 查询权限由可信 Gateway/账本部署端口控制，不由普通 UI 授予。分页在 Open 总 Deadline/资源额度内有界；失败、未完整或发现未决就保持普通写准入关闭，返回需对账状态。新 Session 不能直接接管另一个活 Owner 的 task/Scope；Recover 由原 Owner/已批准移交的 Gateway 显式对账，原 Boot/Generation 不符不向新设备盲发。此端口冻结 Core/模拟扫描，跨进程持久扫描/移交证明仍是 S4 部署门。

### A.4 注入端口与 Adapter 所有权

`MotionDependencies` 的精确构造字段：
`string SessionId, IMotionAdapter Adapter, IOperationLedger Ledger, IMotionCoordinatePort Coordinates, IMotionClockMappingPort ClockMappings, IMotionAuthorizationPort Authorization, IMotionInterlockPort Interlocks, IControllerLeasePort ControllerLeases, IMotionDiagnosticSink Diagnostics, IMotionLifecycleOwner LifecycleOwner, TimeProvider Time`。
Adapter 在构造成功后归 Session；其它端口借用，不由 Session Dispose；构造失败不接管 Adapter。诊断失败不改变运动事实，授权/坐标/联锁/lease/账本失败阻断相关普通准入并保持停止路径。

SessionId 由宿主显式给定，ASCII `[A-Za-z0-9._-]{1,48}`，每次新 Session 唯一且不复用；fixture 在隔离 ledger 中用固定 ID 以保证重放可比。它同时标识事件流与主机时钟 epoch，不能用可变静态计数或重新连接后复用旧 ID。EventId 固定为 SessionId + `:` + EventSequence（总长度 <=128），OperationId 按账本键生成；业务稳定性不依赖随机 ID/UTC。资源保留需先为所有允许的在途 Session 预留 LifecycleOwner 容量，Retain 不得满额后静默丢弃；容量不足时禁止新写 Session/新普通准入，仍保留原未决 Session。

下表给出端口的全部方法（均 instance）；未写 async 的方法禁止 IO/阻塞/重入：

| 端口 | 精确方法签名与响应 |
|---|---|
| IMotionAdapter : IAsyncDisposable | ValueTask<MotionCapabilitySnapshot> OpenAsync(string controllerId, bool readOnly, TimeSpan deadline, CancellationToken ct)；ValueTask<MotionCapabilitySnapshot> ReadCapabilitiesAsync(TimeSpan deadline, CancellationToken ct)；ValueTask<AdapterFeedback> ReadStatusAsync(StatusRequest request, CancellationToken ct)；ValueTask<AdapterPathValidation> ValidatePathAsync(AdapterPathQuery query, CancellationToken ct)；ValueTask<AdapterReceipt> SubmitAsync(AdapterCommand command, CancellationToken ct)；ValueTask<AdapterReceipt> StopAsync(StopRequest request, CancellationToken ct)；ValueTask<AdapterOperationLookup> QueryOperationAsync(AdapterOperationQuery query, CancellationToken ct)；ValueTask<AdapterDrainReceipt> DrainAsync(DrainRequest request, CancellationToken ct)；IAsyncEnumerable<AdapterFeedback> ReadFeedbackAsync(AxisScope scope, CancellationToken ct)；ValueTask<AdapterDrainReceipt> CloseAsync(CloseRequest request, CancellationToken ct)；ValueTask<AdapterReceipt> CancelCompareAsync(AdapterCompareCancel command, CancellationToken ct)；无第二 Core 事件发布入口 |
| IMotionCoordinatePort | ValueTask<CoordinateResolution> ResolveAsync(CoordinateQuery query, CancellationToken ct)；bool IsCurrent(string assetSha256)；只返回唯一固定版本路径，不写资产 |
| IMotionClockMappingPort | ValueTask<ClockMapping?> ResolveAsync(ClockStamp source, ClockStamp target, TimeSpan deadline, CancellationToken ct)；bool IsCurrent(string mappingSha256)；只读取批准历史映射，不校准时钟 |
| IMotionAuthorizationPort | ValueTask<AuthorizationCheck> PrepareAsync(AuthorizationQuery query, CancellationToken ct)；bool IsCurrent(AuthorizationCheck prepared)；不能回调 Core 或自行签发 |
| IMotionInterlockPort | InterlockSnapshot ReadCurrent(AxisScope scope)；IAsyncEnumerable<InterlockSnapshot> SubscribeAsync(CancellationToken ct) |
| IControllerLeasePort | ValueTask<ControllerLease?> AcquireAsync(string controllerId, string ownerId, bool write, TimeSpan deadline, CancellationToken ct)；bool IsCurrent(ControllerLease lease)；ValueTask<ControllerLease?> RenewAsync(ControllerLease lease, TimeSpan deadline, CancellationToken ct)；ValueTask<bool> ReleaseAsync(ControllerLease lease, CancellationToken ct) |
| IOperationLedger | ValueTask<MotionOperationReceipt> FindAsync(string ownerId, string authorityScope, string commandId, TimeSpan deadline, CancellationToken ct)；ValueTask<LedgerReservation> ReserveAsync(LedgerIntent intent, CancellationToken ct)；ValueTask<bool> CommitAsync(string operationId, long expectedRevision, MotionOperation next, ImmutableArray<MotionEvent> events, TimeSpan deadline, CancellationToken ct)；ValueTask<MotionEventPage> ReadEventsAsync(MotionEventQuery query, CancellationToken ct)；ValueTask<PendingOperationPage> ReadPendingAsync(PendingOperationQuery query, CancellationToken ct)；ValueTask<MotionOperationReceipt> ReadAsync(MotionOperationQueryRequest request, CancellationToken ct) |
| IMotionDiagnosticSink | bool TryPublish(MotionDiagnostic diagnostic)；有界、线程安全、非阻塞，false=诊断降级 |
| IMotionLifecycleOwner | void Retain(IMotionSession session, MotionFailure reason)；有界、不抛异常；保存强引用/SessionId 和未决回执，提供宿主维护调用 Close/Query 的原会话；不是后台自动重放 |

端口承载类型（sealed record）：

| 类型 | 精确字段与语义 |
|---|---|
| AdapterCommand | string OperationId, MotionCommand Command, ImmutableArray<TrajectoryPoint> ResolvedMachinePath, string ResolvedPathSha256, AdapterPathValidation? PathValidation；物理命令必须绑定完整机器路径/Profile，非位置命令 path 为空 |
| RawAxisSample | AxisId Axis, MotionValue? ControllerCommand, MotionValue? EncoderActual, MotionValue? Velocity, MotionValue? FollowingError, Quality Quality, CoordinateFrameId Frame, string? CoordinateAssetSha256, int EncoderPositiveSign, Truth Homed, Truth Servo, Truth InPosition, Truth PositiveLimit, Truth NegativeLimit, Truth Fault, ClockStamp Clock, string? DeviceReferenceRevision, Truth PositionHeld, Truth ControllerStopLockActive, string? VendorFaultCode, Truth HomeSwitch, Truth IndexObserved；不含 Core StateVersion、Target、PositionVersion 或 settled |
| AdapterFeedback | string ControllerId, string BootId, long Generation, ImmutableArray<RawAxisSample> Axes, ClockStamp Clock, SourceKind Source, MotionFailure? Failure |
| AdapterAxisReceipt | AxisId Axis, ExecutionState Execution, RawAxisSample? FinalSample, HomeEvidence? Home, MotionFailure? Failure, bool DeviceCallMade, bool PossiblePhysicalEffect |
| AdapterReceipt | string OperationId, string ControllerId, string BootId, long Generation, string? ControllerSequence, ExecutionState Execution, ImmutableArray<AdapterAxisReceipt> Axes, StopEvidence Stop, string? RegistrationId, RegistrationState? RegistrationState, ImmutableArray<FieldConfigurationResult> ConfigurationFields, string? ConfirmedConfigurationRevision, bool DeviceCallMade, MotionFailure? Failure；控制器 ACK 保留 Accepted，不推断 Completed |
| AdapterDrainReceipt | DrainState Drain, ResourceState Resources, StopEvidence Stop, ImmutableArray<string> PendingOperationIds, MotionFailure? Failure；Adapter 不发布 Core ResourcesReleased 或终态 |
| AdapterCompareCancel | string OperationId, CompareCancelRequest Request |
| AdapterPathQuery | string QuerySha256, string ControllerId, string BootId, long Generation, string CapabilitySha256, string ConfigurationRevision, AxisScope Scope, ImmutableArray<TrajectoryPoint> MachinePath, MotionProfile Profile, ImmutableArray<RawAxisSample> StartSamples, TimeSpan Deadline |
| AdapterPathValidation | string QuerySha256, Truth EnvelopeVerified, Truth DynamicsVerified, string ValidatorFingerprint, MotionFailure? Failure；原控制器/配置对应的无副作用预检，不代表现场精度/安全资格 |
| AdapterOperationQuery | string ControllerId, string BootId, long Generation, string OperationId, string RequestSha256, string? ControllerSequence, TimeSpan Deadline |
| AdapterOperationLookup | bool Found, AdapterReceipt? Receipt, MotionFailure? Failure；NotFound 只表示控制器未能找到，不证明未执行 |
| CoordinateQuery | CommandKind Kind, AxisScope Scope, ImmutableArray<AxisFeedback> Start, ImmutableArray<TrajectoryPoint> InputPath, CoordinateFrameId Frame, string AssetSha256, ImmutableArray<ApproachPolicy> Approach, TimeSpan Deadline；Kind仅Move/MoveRelative/Trajectory，Start为完整冻结Machine实际值；输入点的目标/Delta/轨迹语义见§17.2 |
| CoordinateResolution | bool IsUnique, ImmutableArray<TrajectoryPoint> MachinePath, string AssetSha256, string PathSha256, bool EnvelopeVerified, ImmutableDictionary<AxisId,Direction> FinalApproach, MotionFailure? Failure；只要 IsUnique/EnvelopeVerified=false 或 hash 不匹配即拒绝 |
| ClockMapping | string MappingSha256, string SourceDomain, string SourceEpoch, string TargetDomain, string TargetEpoch, long ScaleNumerator, long ScaleDenominator, long OffsetTargetTicks, long MaximumErrorTargetTicks, long ValidSourceTickMin, long ValidSourceTickMax；比例正、误差非负、范围有界；目标 tick = source tick × numerator/denominator + offset，checked 有理运算并向不利方向取整，不丢失误差界 |
| AuthorizationQuery | string OwnerId, CommandKind Kind, AxisScope Scope, MotionAuthorization Reference, string IntentSha256, TimeSpan Deadline |
| AuthorizationCheck | string CheckId, string OwnerId, CommandKind Kind, AxisScope Scope, string IntentSha256, long ExpiresAtTimestamp, string AuthorityRevision, MotionFailure? Failure；CheckId 只给本地 IsCurrent 使用，不信任调用者传入 |
| LedgerIntent | string OperationId, string OwnerId, string AuthorityScope, string CommandId, string RequestSha256, long RequiredBytes, MotionOperation Initial, TimeSpan Deadline |
| LedgerReservation | bool Acquired, MotionOperationReceipt Existing, MotionFailure? Failure |

账本键为 (OwnerId,AuthorityScope,CommandId)，Reserve 原子创建/比较 hash；同键同内容返回原 operation，异内容 Conflict。OperationId 按 A.5 的唯一 `motion-operation-id-v0.2` 字节预像生成，同键重试不生成第二 ID。OperationId 等生成标识允许冒号，仍限制为 ASCII `[A-Za-z0-9._:-]{1,128}`，不套用 AxisId 的无冒号语法。Commit 只在 expectedRevision 精确匹配时增加一次 revision；同一 Owner 原子保全回执与该 revision 的事实事件/终态意图和完整断点记录；反馈投影不逐样本写 ledger。Find/Read 无副作用；Read NotFound 不证明没提交。提交意图必须先耐久写入；崩溃后 Reserved 也不能未经 Adapter/设备对账就假定零动作。内存实现标 Simulation，硬件部署需要支持进程重启、原子 reservation/CAS、提交前预留尾部回执容量的真实实现；存储格式/事务由存储 Owner 负责，不在 Core 新建数据库。

Reserve 的 Initial 是 Acceptance=PendingReservation/Execution=Reserved 的暂存记录，仅持 ledger 额度，未获得运动准入；同键竞争者查询该记录，不启动第二协调流程。完整 Scope CAS/前置重核和提交意图耐久完成后才能转 Accepted、发 Accepted 事件；随后 Submit 前仍核停止/联锁 gate。CAS/授权/持久化失败时转 Rejected/Failed、DeviceCallMade=false，并归还已取得资源；存在 reservation 可保留 OperationId，不冒充已发运动。普通命令所有步骤共用从首次接收起的总 Deadline，不为耗时准备阶段另续一轮；截止时间不写进 canonical，只写有限时长，计时起点属于 ledger 原记录。

特殊幂等域：Open 从其授权 ScopeId 取域；Stop/CompareCancel/Close 从原 Session/operation 保全的授权域取得，不重新要求普通用途授权；CommandId 对应 Open.CommandId、Stop.StopId、CompareCancel.StopId、Close.CloseId。同键同正文先返回原记录，身份不符先隔离不向新设备 Stop。Scope 为空的 Close 是控制器屏障，必须覆盖本 Session 所有原资源；Drain.OperationIds 只可查询/收敛原 Owner 的操作，空数组仅表示无 operation，不绕过会话连接的 Close。Query/Drain/Stop/Close 的 Deadline 是本次有限观察/清理预算，重复调用可继续原收敛阶段但不得重置原运动 Deadline、重发普通命令或生成新运动 ID。每控制器 StopId 容量超过 MaxStopRequests 时合并已有原身份/Scope 的收敛并返回当前未知回执，已有停止 task 不取消，不为满队列制造无限停止任务。

每种 Adapter Submit 的 CommandKind 由请求 CLR 类型固定映射；CompareCancel/Stop/Close 不伪装普通 Move，Core 的 priority actor 调 Adapter.Stop/Close/CancelCompare。跨时钟 Scope 在接纳时冻结全部 ClockMapping 摘要，反馈阶段持续核适用域；映射缺失、已失效或误差后 MaxSampleGap/MaxAxisSkew 不满足即反馈不可观测。Adapter 不能获取 Core 状态写入权；厂商间反馈转换通过此端口共享同一契约测试。SDK 不可取消任务始终由 Adapter 保管实际 task；禁止 Thread.Abort；进程隔离策略由厂商适配指导决定，物理 Unknown/重启对账仍回 IM-010。

全路径预检：Core 检查有限性、逐轴闭区间软限位、完整 Scope/严格轨迹时间、Profile 范围；外部坐标端口核批准禁区/额外接近段；Adapter.ValidatePathAsync 在 gate 外检查该版本插补器的完整包络和有限动力学（包含原起始速度及段间连接）。两个 Verified 都须 True 且 QuerySha256 匹配，才能保全到 ExecutionRecord/AdapterCommand 后提交；未知插补/jerk 不猜，Unsupported 零下发。QuerySha256 沿 A.5 构造字段编码、排除自身摘要，domain 为 motion-path-validation-v0.2；最终 gate 核原 Boot/Generation/配置/Start 版本不变，否则丢弃预检并拒绝。验证调用本身不得产生运动/输出；真实 SDK 是否提供原生预检、或厂商适配用已资格化的离线模型，是 S4 实施门，不是 Core 临时引入 Ruckig 的理由。Simulator 按计划 PathValidations 精确匹配 QuerySha256 返回，不把端点通过自动升级为包络通过。

所有外部异步端口调用都受剩余请求 Deadline 或独立 CleanupBudget 包装；过期只结束本等待，原 task 留在原 Owner 的有界 pending 集合，所占额度/资源不归还。禁止无限 while 重试、CancellationToken.None 配无限等待或跨期限重复启动端口 task。ReleaseAsync/DisposeAsync 虽无 deadline 参数，也使用此有限观察规则并保留原任务。只读查询未退出同样消耗 MaxReadQueries，不得连续超时后无限重建读取；Stop 使用预留通道，硬件写 Open 要求 SupportsIndependentStop=true，厂商不能用被阻塞的普通 SDK 队列伪装独立 Stop。该字段只声明软件通道，不替代安全回路。

能力的 WritableConfigurationFields 仅允许 SoftMin/SoftMax/DefaultVelocity/DefaultAcceleration；Draft.Frame 是核对上下文，不是普通配置可写资产。ReportsPositionHold=false 时 PositionHeld=Unknown；UsesControllerStopLock=false 时 Adapter 明确回报 ControllerStopLockActive=False（声明不存在该锁），不能把无法读取混成不存在。反馈 Clock.Domain/Epoch/Frequency 必须匹配对应 ClockDescriptor；capability 的描述不包含实时 tick/sequence，重复采样不会改变 capability hash。只有接受的新序号刷新该轴 ReceivedAtTimestamp，重复/倒序不能刷年龄。

### A.5 canonical、版本兼容及发布

请求规范编码为 `motion-core-v0.2` 二进制（Core 的 `MotionRequestCodec.Encode(MotionCommand)`/`Sha256(MotionCommand)`；特殊请求各有同名重载）。所有字符串 UTF-8 NFC、前置 Int32 字节长，小写 hash，有限限额；空与 null 用不同标记。整数字段固定 little-endian，TimeSpan 用 ticks，double 写规范 +0 的 IEEE754 Int64 bitpattern，布尔 0/1，枚举用冻结 Int32。先写域、版本、CommandKind，再按 A.1/A.2 构造字段顺序递归；字典按 AxisId Ordinal 排序，集合有序（不擅自重排轨迹/轴组），包含调用 Deadline/Profile/授权引用/坐标资产/版本。排除 CancellationToken、UTC/当前时间、运行时授权 CheckId、结果 hash；没有 JSON 隐式字段兼容。IntentSha256 按相同编码排除 Authorization 四字段，独立域 `motion-intent-v0.2`，授权准备后正文只附引用，不重新计算位置/预算。

**Header 与 ID 预像的唯一排布**：下文 `S(x)` 就是本节已有字符串规则：严格 UTF-8 编码 NFC 后的 x，先写其字节长度的 Int32 little-endian，再写原 UTF-8 bytes；不加 BOM、NUL、分隔符或 nullable 标记。`I32(x)`/`I64(x)` 分别为有符号 Int32/Int64 little-endian；`+` 仅表示 bytes 直接拼接，不写入加号字符。固定 wire version 是 **Int32 值 2**，bytes=`02000000`，不是字符串 `0.2`、两个版本整数或文档 prep 版本；domain 名中的 `v0.2` 保留原样。根对象不存在额外类型名/长度/nullable 标记。

| 根编码/预像 | 依序写入的完整结构 |
|---|---|
| 普通 MotionCommand 请求 | `S("motion-core-v0.2") + I32(2) + I32(CommandKind) + Context字段 + Scope字段 + 具体派生请求新增字段`；递归按 A.1/A.2 构造顺序，Common 恰写一次 |
| Open/Stop/Close/CompareCancel/Drain 特殊请求 | 同一个 `S("motion-core-v0.2") + I32(2) + I32(CommandKind)` header，接该独立 record 的 A.2 字段；不追加普通 Context/Scope。kind 固定 Open=0、Stop=10、Close=13、CompareCancel=9、Drain=14 |
| 普通请求 IntentSha256 预像 | `S("motion-intent-v0.2") + I32(2) + I32(CommandKind) + 原普通请求正文`；从正文中完全省略 Authorization 的四个字段，无占位/null标记，其余字段与请求编码相同 |
| 能力/Policy/Profile/Receipt/路径验证/Simulation/Replay | `S(本节或对应章节已规定的domain) + I32(2) + 对应构造字段`；不写 CommandKind，因为不是请求根。只按已有规则排除自身摘要/明确排除字段；SchemaVersion 字段仍作为正文字符串写入 |
| OperationId 预像 | `S("motion-operation-id-v0.2") + I32(2) + S(OwnerId) + S(AuthorityScope) + S(CommandId)`；只含这五项，没有 kind、SessionId、deadline、request hash 或分隔符 |
| TargetVersion 预像 | `S("motion-target-v0.2") + I32(2) + S(OperationId) + S(AxisId.Value)`；只含这四项，OperationId 是含 `op:` 前缀的完整 ASCII ID，不是其 hash 原始 32 bytes |

OperationId=`"op:" + lowercaseHex(SHA256(OperationId预像))`；TargetVersion=`"target:" + lowercaseHex(SHA256(TargetVersion预像))`。SHA-256 对完整预像原 bytes 做一次计算，输出完整 32 bytes 的 64 位小写 hex，不截断、不对 hex 文本再 hash。ID 前缀只在结果中追加，不在对应预像中另写一次。以下固定向量仅冻结合同，未引入另一 ID/哈希算法。

Stop/Open/Close/CompareCancel 独立重载按自己的字段顺序编码；JogHeartbeat 为 lease 续约消息，不创建新的 motion reservation。CompareCancel 只撤销原登记，来源身份由原 Owner 核验；Adapter 原始样本由 Core 按轴资源/operation 关联生成 StateVersion/PositionVersion/目标，不让 Adapter 成为第二状态 Owner。HomeEvidence.ReferencePositionVersion 在 Adapter 中表示其设备基准提交引用，Core 建立新 PositionVersion 时保留该引用的映射。
规范能力/Policy/Profile 同样按对应构造字段顺序编码，domain 分别为 `motion-capability-v0.2`、`motion-settled-v0.2`、`motion-profile-v0.2`、`motion-runtime-v0.2`，计算 hash 时只排除对象自身 hash 字段；CapturedAtUtc 不进入能力 hash。权威资产摘要保持原 Owner 规则，不重新生成坐标资产身份。接口 DTO 版本不等于客户 Profile 版本。

递归编码补充：所有可空字段统一先写 byte 0/1 表示 null/present，present 后按该类型编码；字符串/数组/字典长为非负 Int32，集合写长度后逐项；record struct 不写额外类型名。字典先写 key 再 value，字符串 key 按 Ordinal；其它字典沿声明 key 的固定比较器。TimeSpan ticks 为 Int64，DateTimeOffset 审计字段编码 UTC ticks/offset ticks 两个 Int64，byte 数组按长度加原 bytes，UInt64 Seed 固定 little-endian。未知字段/enum/schema 或长超限拒绝，不读取任意 CLR 类型名。普通请求拒绝非有限 double；Simulation/Replay 计划内**原始反馈**按原 IEEE754 bits 保留 NaN/Infinity/-0，以便 Core 实际验证这些反例，不能把它们变成有效请求。MotionStopPolicy 摘要 domain 为 motion-stop-policy-v0.2。

`MotionRequestCodec` 公开静态 `byte[] Encode(MotionCommand request)`/`string Sha256(MotionCommand request)`，`string IntentSha256(MotionCommand request)`；以及 OpenRequest/StopRequest/CloseRequest/CompareCancelRequest/DrainRequest 的 Encode/Sha256 对应重载；只为这些幂等请求建立 codec。operation 原 CanonicalRequest 以该 Encode 的有界不可变 bytes 保存。`MotionReceiptCodec` 公开静态 `byte[] Encode(MotionOperation receipt)`/`MotionOperation Decode(ReadOnlyMemory<byte> bytes, ResourceLimits limits)`，domain 为 motion-receipt-v0.2，按 A.3 构造字段/上述编码递归，解码校验所有结构/上限/身份字段但不把历史 Pending 转成功。非法输入无法形成 canonical 时，其未接纳回执 CanonicalRequest 为空、RequestSha256 为 SHA256(empty)、OperationId=null，不进账本、不作为幂等凭据。codec golden 至少包括正/负零同 bytes、null 与空不同、字典不同插入序相同、轴组顺序不同 hash 不同、所有已知请求 kind、原 Unknown/Draining 回执解码不改状态、未知 schema 拒绝。

**公开 codec 错误与所有权**：Encode/Sha256/IntentSha256 的顶层 request/receipt 或 Decode 的 limits 为 null 时抛 `ArgumentNullException`，ParamName 为对应声明参数名；其余合同编码/解码拒绝统一抛 `MotionCodecException : Exception`。该 sealed class 的公开构造为 `MotionCodecException(string code, string messageKey)`，公开只读属性 `string Code`、`string MessageKey`，Exception.Message 等于稳定 MessageKey，不附原请求/授权内容。Code/MessageKey 固定对应：`MOTION_INVALID_ARGUMENT`/`Motion.Error.InvalidArgument`（字段/单位/范围、非法 UTF-16/UTF-8、截断、非法 length/presence/bool、尾部多余 bytes、非法 hash/ID 或不能形成 canonical）、`MOTION_SCHEMA_UNSUPPORTED`/`Motion.Error.SchemaUnsupported`（未知 domain/wire version/请求 CLR 类型/enum）、`MOTION_RESOURCE_LIMIT`/`Motion.Error.ResourceLimit`（已声明限额或 checked 长度/计时运算溢出）。Sha256/IntentSha256 与 Encode 使用相同校验，不用空 bytes/hash 表示成功；Session 在未接纳路径捕获该异常并按同 Code 返回结构化失败，保留前述空 CanonicalRequest 占位规则，不 reservation/设备调用。物理状态、权限及当前版本准入仍由 Session 验证，codec 不做 IO/签发授权或替它们决定成功。Decode 必须消费全部 bytes，拒绝非 canonical 字符串/字典顺序/重复 key；普通有限数值的负零 wire 表示同样拒绝，RawAxisSample 按前述原始 bits 例外保留；不默默修复输入，也不吞运行环境的内存耗尽等异常冒充合同拒绝。

Encode 每次成功返回一个新建、长度恰等于编码长度的 `byte[]`，所有权交调用者；不返回内部缓存、ArrayPool 租约或可修改的共享数组。调用者修改一个结果不影响其它 Encode、Sha256、ledger 或原 record。保存到 CanonicalRequest 时独立有界复制为 ImmutableArray；Decode 不修改输入，返回 record 及集合不借用输入内存，返回后输入 bytes 可回收/修改。调用期间调用者不得并发修改 Decode 的 ReadOnlyMemory backing buffer；这不是 Core 资源租约，无 Dispose 义务。codec 全部纯同步、无静态可变缓存；限额检查在按不可信 length 分配前完成。

**固定合同向量**（hex 无空格、无换行 bytes；正文排版换行不进入预像）：

- `MC-CODEC-CLOSE-01`：`new CloseRequest("o", "c", TimeSpan.FromTicks(10000000))`。header 为 S(motion-core-v0.2)/I32(2)/I32(13)，正文为 S(o)/S(c)/I64(10000000)，无 nullable 标记。完整输出 **46 bytes**：

```text
100000006d6f74696f6e2d636f72652d76302e32020000000d000000010000006f01000000638096980000000000
```

SHA-256=`bf496978670b653c34f2fc40b1d2fdf9301aec0151bbca62643ee518a3b6c802`。字段 offset（零起点）：domain length 0–3/domain 4–19/version 20–23/kind 24–27/OwnerId length 28–31/value 32/CloseId length 33–36/value 37/Deadline 38–45。

- `MC-ID-OP-01`：OwnerId=`o`、AuthorityScope=`s`、CommandId=`c`。完整 OperationId 预像 **47 bytes**：

```text
180000006d6f74696f6e2d6f7065726174696f6e2d69642d76302e3202000000010000006f01000000730100000063
```

SHA-256=`a6c14501c030589bf6f56c6d5952c8e2e742817b8a15d19af558a6784ee54832`；期望 OperationId=`op:a6c14501c030589bf6f56c6d5952c8e2e742817b8a15d19af558a6784ee54832`。

- `MC-ID-TARGET-01`：OperationId 为上一向量完整结果、AxisId.Value=`X`。完整 TargetVersion 预像 **102 bytes**（OperationId 的 UTF-8 长度为 67，即前缀 `43000000`）：

```text
120000006d6f74696f6e2d7461726765742d76302e3202000000430000006f703a613663313435303163303330353839626636663536633664353935326338653265373432383137623861313564313961663535386136373834656535343833320100000058
```

SHA-256=`fe155e37e192e87e8be7901b0ff48509079f6f4ee2a095dae7a058fb227a233d`；期望 TargetVersion=`target:fe155e37e192e87e8be7901b0ff48509079f6f4ee2a095dae7a058fb227a233d`。2026-10-10 已用 Python struct/UTF-8/hashlib 与独立 .NET BinaryWriter/UTF-8/SHA256 按字段分别重建，三份完整 bytes、长度和摘要一致；这是规格向量复算，未声称产品 codec 编译/执行通过。后续 ContractTests 必须断言完整 bytes/长度/hash/ID，不能只断言两次调用相等；同时断言 Encode 输出独立、修改返回数组不改原 record/后续 hash、非法输入按上述异常分类拒绝。

`MotionDrainException : Exception` 的公开只读属性为 string SessionId、MotionFailure Failure，构造参数相同；消息来自稳定键，未知资源仍归 LifecycleOwner。方法不以异常漏掉已接纳 operation。对外 Contract 不公开私有数据库/厂商字段，Schema 未知主版本拒绝、原回执只读保留；v0.1 尚无已发布 Core，不声称真实旧包迁移通过。未来首次发行必须随包包含 API/codec/兼容样例并保持历史 bytes，主版本改单位/取消/时序需迁移门。

发布 Core 单包的唯一构建入口为预定 csproj；WPF 另包仅依赖 Core/本机 DevExpress，Simulator 在 Core 工程的 Simulation 子目录（namespace 仍为 Asun.Modules.MotionControl）但仍使用同一公开端口。构建命令为 `dotnet build src/Modules/motion-control/Asun.Modules.MotionControl.Core/Asun.Modules.MotionControl.Core.csproj -c Release`；Core harness 命令见 §11.1；包 restore/消费者 reference 只针对绑定工程；不改平台 solution/统一版本文件。回退先 Close/对账未决，保留 ledger/资产/Profile 原版本和配置，不覆盖历史。包 smoke 与独立控制台/WPF Host 验证还未执行。

### A.6 逐切片六项准备结论

2026-10-10 主控已完整走查 0.2.1-prep 的正文能力/状态/Stop 连续反馈/TargetVersion/持久对账/双 Host/Simulator 与 Replay/Clock/事件/Benchmark 及六项规格，并接收 0.2.2-prep 的 A.5/§11.1 定向补充。S1（纯模型/校验/codec）、S2（Core + Simulator/Replay + 注入 Ports）现为 `ModuleCoreImplementationReady`，仅规格准备；下表六项均已获主控内容接收。本文较早“待接收/DesignReview/Prep”措辞是接收前自审记录，当前逐切片状态以头部、binding 与本节为准。权威代码快照/分支尚未确认，后续明确实现任务创建工程前仍须确认，不自动开工。

0.2.2-prep 的 A.5 header/ID 预像、codec 错误/输出所有权与固定向量，以及 §11.1 case/suite/外进程墙钟预算已获主控定向接收；主控独立逐字段复算 Close/Operation/Target 的 46/47/102 bytes 及 SHA-256 一致。此结论仅为合同规格核查，未执行产品 codec/Core/Simulator/Replay 测试。真实 S3/S4 门保持，不授整模块 Ready。

0.2.3-prep 新增 `Motion Read Bridge v0.1`，只服务 mosaic 的首行线扫窄消费者：它补有界原始历史、同 tick/sequence 的同步 XY、缺包证据、clock epoch/frequency 有理映射和按 run 绑定的只读动态包络证据。该增量不改变已接收 S1/S2 的 Core API/codec/Simulator/Replay 语义，不修改 mosaic 或共享指导；其六项文档规格已结合0.2.4-prep窄补充获主控接收为 `ModuleCoreImplementationReady`（仅准备），真实 Adapter/Gateway、物理动态资格与性能/现场门仍保留。

0.2.4-prep 的 A.8.4 两种入口/嵌套字段/证据正文预像及 A.8.5–6 调用前原Task根槽、全字段Synthetic双Host/端口/finally/迟到同桥恢复已获主控回读接收。主控独立逐字段重建MR-XY/MR-DY/MR-EV的176/186/337 bytes，完整hex/hash一致；结合A.8.1–3，Motion Read Bridge v0.1六项文档规格为 `ModuleCoreImplementationReady`（仅准备）。不改S1/S2已接收合同或A.5，不授真实来源/SDK/同步采样/同run物理动态包络资格，也不授权创建工程或产品代码。

0.2.5-prep由永久原会话完成当前架构全部能力的内容核实、自审和必要修复，见§17。已接收请求/回执与全部固定向量保持；未发布CoordinateQuery补Kind/Start，MotionViewOwner及根持有/名义时间化/原生转换/读重连/首尾覆盖已冻结，消费者实现按当前唯一形状。S1/S2与Read Bridge的既有准备结论有效；S3/S4内部设计已明确，真实运行、产品映射和外部事实仍未通过。不存在待主控内容审核门；本文不据文档完备宣称整模块ImplementationSpecificationReady。

| DEV-GOV-010 §3.1 条件 | 本页位置与本轮结论 |
|---|---|
| 1 边界/依赖/第二消费者 | §1–2/§14/A.4 已规定；产品扫描编排排除 |
| 2 API/单位/结果/取消/版本/Owner | §3–7/A.1–5/A.7 已给公开类型/端口；不再要求实现者选择同义 DTO |
| 3 最小无UI无SDK宿主 | §9/A.4/A.7 已规定 test ports 和 Session 构造；硬件/真实持久存储在后续门 |
| 4 正常/边界/并发/关闭/回退反例 | §10–11 已规定逐能力及外部调用者反例；尚未实施测试 |
| 5 Benchmark 可执行口径 | §12/12.2 沿 GOV-010 统计，负载/测点/限额/阈值来源已规定，目标待 Profile，未测 |
| 6 唯一落点/禁止路径/调用顺序 | 绑定节/§9/A.5 已规定完整 Core+Simulator+Ports 及后续 UI；工程未建 |

S1＝全部 Core 值契约/单位/codec/校验/settled/状态；S2＝全部会话/命令/ledger/lease/联锁/生命周期 + Simulator/Replay + 最小 Host/两消费者；两者已接收为 `ModuleCoreImplementationReady`，无代码/构建/运行测试/性能结论。S3＝可选 WPF 控件，官方 25.2 API 和本机 XML 已查，真实 25.2.3 编译/交互仍为后续门。S4＝真实厂商 Adapter、跨进程 Gateway/持久 ledger 部署、路径验证能力、时钟与 HIL/现场资格，所需实际机械/SDK/安全/客户输入详见 §15；S3/S4 及产品集成保持 `PreparationIncomplete`。性能目标/Profile、真实测量与现场验收未授通过，不因 S1/S2 规格接收宣称整模块 Ready。

### A.7 Simulator/Replay、虚拟时钟和最小宿主装配

以下类型仍在 Core 的 `Asun.Modules.MotionControl`，不是另一个仿真包。模拟器是可审查的脚本执行器，未提供设备物理模型。sealed record 构造字段如下；所有数组受 ResourceLimits 和 MaxRetainedBytes，时间非负有限、按规定顺序且不超过计划有限时长：

| 类型 | 精确字段 |
|---|---|
| SimulationFrame | TimeSpan Offset, AdapterFeedback Feedback；从时钟构造原点计时，相同 Offset 按数组顺序 |
| SimulationCapabilityFrame | TimeSpan Offset, MotionCapabilitySnapshot Capability；声明的配置/Boot/Generation/epoch 变化，不与每帧 tick 同步重算 hash |
| SimulationInterlockFrame | TimeSpan Offset, InterlockSnapshot Snapshot；仅由 SimulationInterlockPort 发布 |
| SimulationCall | CommandKind Kind, string RequestId, string RequestSha256, string? ExpectedResolvedPathSha256, TimeSpan Delay, AdapterReceipt? Receipt, AdapterDrainReceipt? DrainReceipt；从调用计时，Submit/Stop/CompareCancel 只用 Receipt，Drain/Close 只用 DrainReceipt |
| FaultInjection | string FaultId, SimulationFaultKind Kind, string? RequestId, long? SampleSequence, int Occurrence, AdapterFeedback? ReplacementFeedback, AdapterReceipt? ReplacementReceipt, AdapterDrainReceipt? ReplacementDrainReceipt；Occurrence 从 1 起，精确一次注入 |
| SimulationPlan | string SchemaVersion, string PlanSha256, ulong Seed, TimeSpan Duration, TimeSpan OpenDelay, MotionCapabilitySnapshot Capability, ImmutableArray<SimulationCapabilityFrame> Capabilities, AdapterFeedback InitialFeedback, ImmutableArray<SimulationFrame> Feedback, ImmutableArray<AdapterPathValidation> PathValidations, ImmutableArray<SimulationCall> Calls, ImmutableArray<SimulationInterlockFrame> Interlocks, ImmutableArray<FaultInjection> FaultSchedule |
| ReplayPlan | string SchemaVersion, string PlanSha256, TimeSpan Duration, MotionCapabilitySnapshot Capability, MotionCapabilitySnapshot RecordedCapability, AdapterFeedback InitialFeedback, ImmutableArray<SimulationFrame> Feedback, ImmutableArray<SimulationInterlockFrame> Interlocks, ImmutableArray<MotionOperation> Operations |

`SimulationFaultKind` 编号从 0 依次为 ReplaceFeedback, SuppressFeedback, ReplaceReceipt, HoldNative, FailRelease。反馈类必须有 SampleSequence、不得有 RequestId；ReplaceFeedback 必须有 ReplacementFeedback，其余 replacement 字段为空。调用类必须有 RequestId、不得有 SampleSequence；ReplaceReceipt/FailRelease 按目标方法恰有对应 replacement receipt，HoldNative 必须保存该调用原定 receipt 以供受控释放，replacement 字段为空。不适用字段/重复 FaultId/不在计划范围/无匹配调用或样本/相同匹配点两个故障都在构造时拒绝。SampleSequence 匹配 AdapterFeedback.Clock.Sequence，不匹配逐轴序号。脚本保留故意重复/倒序/非有限原始反馈用于验证 Core 拒绝，构造校验结构/预算/身份标记，不代 Core 吞掉这些反例。

公开构造/辅助方法固定为：

```csharp
public sealed class MotionVirtualTimeProvider : TimeProvider
{
    public MotionVirtualTimeProvider(DateTimeOffset originUtc);
    public void Advance(TimeSpan elapsed);
}
public sealed class SimulatorAdapter : IMotionAdapter
{
    public SimulatorAdapter(SimulationPlan plan, MotionVirtualTimeProvider time);
    public bool ReleaseFault(string faultId);
}
public sealed class ReplayAdapter : IMotionAdapter
{
    public ReplayAdapter(ReplayPlan plan, MotionVirtualTimeProvider time);
}
public sealed class SimulationInterlockPort : IMotionInterlockPort
{
    public SimulationInterlockPort(ImmutableArray<SimulationInterlockFrame> frames,
        ResourceLimits limits, MotionVirtualTimeProvider time);
}
public sealed class InMemoryMotionLedger : IOperationLedger
{
    public InMemoryMotionLedger(ResourceLimits limits, SourceKind source,
        ImmutableArray<MotionOperation> replayHistory);
}
```

上段为公开 API 形状，类需按 A.4 实现全部接口方法，不是可直接编译的源码。构造只接管不可变计划，不 Advance/发反馈/打开 Session。时钟的 TimestampFrequency 固定为 TimeSpan.TicksPerSecond，初始 timestamp=0，UTC=originUtc；Advance 只接受非负有限 TimeSpan，checked 加法，不允许并发/递归 Advance。GetTimestamp/GetUtcNow/CreateTimer 按 TimeProvider 契约实现，计时器按到期时间、创建序号稳定执行，在时钟锁外调用；同一 Advance 内执行到新时点的全部到期项。无限 dueTime/period 只表示禁用计时器，不作命令无限期限；零 period 为一次性。异常不被吞掉，测试显式失败。Advance 不替代异步闩锁：测试在每阶段 await 屏障，保证续体处理完再推进下一段。

Simulation Schema 固定 `motion-simulation-v0.2`，Replay 为 `motion-replay-v0.2`，计划 hash 沿 A.5 构造字段编码并排除 PlanSha256 本身，保留全部原始反馈/时钟/故障。Seed 是输入追溯，不启动隐藏随机数；量化/噪声/回差/联锁变化均以明确样本/联锁帧表达。Simulator Capability/Feedback.Source 必须 Simulation；Replay 必须 Replay，原 Operations 的历史身份/源不改写，读回投影标记 Replay。Plan.Duration 为总上界，OpenDelay <= Duration；超过末帧返回 Stale，不循环/外推实际位置。

Simulator.OpenAsync 仅按 OpenDelay 返回声明的 Capability，ControllerId/ReadOnly 与请求核对；ReadStatusAsync 返回当前虚拟时点最新原帧并按年龄标记质量，ReadFeedbackAsync 从当前时点订阅后续帧，不将过去样本冒充实时。Calls 以 Kind+RequestId 唯一匹配：普通命令 RequestId=Context.CommandId，Stop=StopId，CompareCancel=StopId，Close=CloseId；Drain 的键为请求 OperationIds 按 Ordinal 排序后的 canonical 摘要。RequestSha256 必须匹配实际请求，AdapterCommand 还核 ResolvedMachinePath/hash 与冻结执行记录；匹配后 Delay 到期仅返回脚本给定 receipt，不用 ACK 自动产生位置变化。同 ID 普通提交重复调用返回原 task/receipt，不再次消费脚本；Close/Drain 只续做未完成收敛，异内容拒绝。脚本缺项 Submit 拒绝零动作，Stop/Drain/Close 缺项返回 Unknown/Held，不伪造停止/排空。QueryOperationAsync 只返回已调用脚本保留的原 operation receipt，未返回/未找到均不证明未发出。

ReadCapabilitiesAsync 只在已打开连接读取最新完整快照，不二次 Open/改配置；Simulator 从 Capabilities 时间表取当前声明（之前用 Plan.Capability），Replay 仅返回其只读 Capability。Core 的 GetCapabilitiesAsync 调此方法后校验身份/hash/配置，并只更新未来准入使用的缓存，不覆盖原 operation。配置回读 revision 尚未与新 capability 一致时保持普通写关闭；设备 Boot/Generation/轴映射变化隔离原资源，不把刷新当恢复。

HoldNative 故意保留未完成真实托管 task；普通 deadline 到期只结束调用者等待，不结束它。ReleaseFault 仅用于测试：HoldNative 对原 task 完成一次原定 receipt；FailRelease 撤除失败覆盖，使同 CloseId/Drain 键的下一次收敛尝试返回原定 drain receipt。重复释放返回 false。普通 Submit/Stop 同 ID 缓存原 task；Close/Drain 允许同逻辑 ID 续做未完释放阶段，不能靠另建 Adapter 绕过。未排空时 Adapter.DisposeAsync 抛 MotionDrainException 并保留 task；Session 转交 LifecycleOwner。确认无 pending task/订阅后才释放，计数仍受 MaxInFlightOperations/MaxReadQueries/MaxSubscribers，不允许用故障测试制造无界任务。Close 不以虚拟时间到期自动证明停止。

Replay.OpenAsync 只支持 ReadOnly=true；ReadStatus/Feedback 同上述时间语义，所有物理写均返回 Unsupported/DeviceCallMade=false。Close/Drain 只清本 replay 枚举器，无设备 Stop；运行到计划末尾不抹掉历史未决 operation。InMemoryMotionLedger 的 Simulation 模式支持有界原子 reservation/CAS，但 replayHistory 必须空；Replay 模式只加载计划原回执供 Find/Read，拒绝 Reserve/Commit，Find 按原 Owner/授权域/CommandId 查询。Hardware 模式构造拒绝，不能把内存存储部署为耐久账本。历史回执需保留 A.3 的 AuthorityScope/CanonicalRequest，不靠当前授权推断旧键。

Replay.RecordedCapability 是保留原 hash/Source 的历史能力；Capability 是只读 Replay 投影（Identity.Source=Replay 且重新计算投影 hash）。历史 operation 的 CapabilitySha256/Boot/Generation 必须与 RecordedCapability 一致；原值不被投影覆盖。Replay WaitForSettled 仅核被选 operation 的原 TargetVersions/ResolvedTarget 和计划原样本，年龄沿原记录 Offset 的虚拟时间计算，不与当前控制器的 CAS/StateVersion 比较。TargetVersions 缺失、域不符或样本不覆盖原窗口为明确失败。新结果 SettledEvidence.Source=Replay，历史 ledger 只读；不能沿用历史 IsSettled=true 而跳过原样本验证。Replay.QueryOperation 读取本计划历史，不能暗中连接原 Controller。Simulator 脚本 Drained/Released 也必须与真实托管 pending task/订阅计数交叉核对，脚本不能令仍运行的 task 被归还。

最小 Host 装配由测试工程 `Hosts/MotionFixture.cs` 明确完成：new 时钟 → 合成能力/Policy/脚本并计算摘要 → SimulatorAdapter 或 ReplayAdapter → 同时钟 SimulationInterlockPort → InMemoryMotionLedger → 测试端口 → MotionDependencies → MotionSession。测试端口放 `Hosts/TestPorts.cs`，实现 A.4 全部方法；直机器坐标不调用 Coordinates，外部坐标案例用固定唯一/多解/失效响应；ClockMappings 用固定有理数映射；Authorization 只认可 fixture 的 Owner/用途/Scope/IntentSha256，撤销由测试闩锁控制；ControllerLeases 在 fixture 内共享协调实例，FencingToken 单调且拒绝第二写 Owner；Diagnostics 有界保存投影；LifecycleOwner 有界保存未决 Session，归还确认前不删引用。不访问文件/数据库/SDK/产品静态状态，所有实例由 fixture 显式传入，无全局默认。Replay 另提供明确历史目标的 SettledRequest，不伪造 Move 来取得 OperationId。

### A.8 Motion Read Bridge v0.1：mosaic 只读连续反馈/动态证据

本附录是 `Asun.Modules.MotionControl` 的**增量只读合同**，版本独立于 Core Contract v0.2；它只为已确认消费者 `mosaic` 的 `FirstLineEncoderTranslationMeshV1` 提供输入。增量版本为 `motion-read-bridge-v0.1`，已接收准备基线为 `0.2.4-prep`，当前全范围修订见 §17，六项文档规格已获主控接收，状态 `ModuleCoreImplementationReady`（仅准备）。S1/S2 六项接收、A.5 header/ID 规则及 46/47/102-byte 向量不变。桥只读Actual Encoder同步XY、原tick/sequence/PositionVersion/ClockMapping及同run外部动态包络，不授运动、settled、曝光、图像、标定、质量或动态资格Owner；`SourceKind=Simulation/Replay`只能证明软件协议，不能作为真实线扫物理资格。主控已独立逐字段重建176/186/337-byte完整向量并确认hex/hash一致，未据此授运行或现场资格。

#### A.8.1 身份、范围和公开构造

以下类型仍在 Core namespace；集合均为不可变副本，读取在分配前检查 `MotionReadLimits` 和 `MaxRetainedBytes`。ID 使用本指导的 ASCII/Ordinal 规则；`ReadId` 必须稳定且在同一 Bridge/Owner 内幂等。`ClockRange` 的 start/end 属同一 Domain/Epoch/Frequency，`EndTick >= StartTick`；窗口之外不得回填或外推。

| 类型 | 精确字段（按声明顺序） |
|---|---|
| MotionReadLimits | int MaxSamples, long MaxBytes, int MaxPendingReads, int MaxQueueDepth, TimeSpan MaxObservationWait, TimeSpan CleanupBudget |
| MotionClockRange | string SourceDomain, string SourceEpoch, long SourceFrequency, long SourceTickStart, long SourceTickEnd, string TargetDomain, string TargetEpoch, long TargetFrequency |
| MotionReadSelector | string BridgeId, string SessionId, string OwnerId, string ControllerId, string ExpectedBootId, long ExpectedGeneration, AxisScope Scope, AxisId AxisX, AxisId AxisY, MotionClockRange Range |
| MotionReadIdentity | string BridgeId, string SessionId, string OwnerId, string ControllerId, string BootId, long Generation, SourceKind Source, string CapabilitySha256, string ContractVersion, string SourceDomain, string SourceEpoch, long SourceFrequency |
| MotionSequenceGap | MotionReadIdentity Identity, long MissingFromInclusive, long MissingToInclusive, string Reason, ClockStamp? Before, ClockStamp? After |
| MotionRawHistoryRecord | string SourceRecordId, string ControllerId, string BootId, long Generation, long Sequence, ClockStamp Clock, AxisId AxisX, AxisId AxisY, RawAxisSample AxisSampleX, RawAxisSample AxisSampleY, AxisFeedback FeedbackX, AxisFeedback FeedbackY, string DeviceReferenceRevision, TimeSpan TimestampUncertainty, bool Simultaneous, SourceKind Source |
| MotionRawHistoryRead | MotionReadIdentity Identity, ImmutableArray<MotionRawHistoryRecord> Records, ImmutableArray<MotionSequenceGap> Gaps, bool SourceComplete, MotionFailure? Failure |
| MotionSynchronizedXYSample | MotionReadIdentity Identity, string ReadId, string SourceRecordId, long Sequence, ClockStamp Clock, AxisId AxisX, AxisId AxisY, MotionValue ActualX, MotionValue ActualY, CoordinateFrameId Frame, string PositionVersionX, string PositionVersionY, string DeviceReferenceRevision, TimeSpan TimestampUncertainty |
| MotionReadResources | int PendingReads, int QueueDepth, int SampleCount, long Bytes, bool Released |
| MotionXYHistoryResult | MotionReadIdentity Identity, string ReadId, string RequestSha256, ClockMapping? Mapping, MotionReadAvailability Availability, ImmutableArray<MotionSynchronizedXYSample> Samples, ImmutableArray<MotionSequenceGap> Gaps, bool IsComplete, MotionReadResources Resources, MotionFailure? Failure |
| MotionDynamicsReadRequest | string ReadId, MotionReadSelector Selector, string RunId, string ApplicabilityRevision, ImmutableArray<MotionDynamicsOrigin> AllowedOrigins, long MaxBytes, TimeSpan Deadline |
| MotionDynamicsEvidence | MotionReadIdentity Identity, string EvidenceId, string EvidenceSha256, string RunId, string ApplicabilityRevision, MotionClockRange ApplicableRange, string AuthorityId, string DeviceReferenceRevision, MotionValue MaxSpeedX, MotionValue MaxSpeedY, MotionValue MaxAccelerationX, MotionValue MaxAccelerationY, TimeSpan TimestampUncertainty, MotionDynamicsOrigin Origin, MotionEvidenceState State |
| MotionDynamicsResult | MotionReadIdentity Identity, string ReadId, string RequestSha256, MotionReadAvailability Availability, MotionDynamicsEvidence? Evidence, MotionReadResources Resources, MotionFailure? Failure |
| MotionReadBridgeDependencies | IMotionReadSource Source, IMotionClockMappingPort ClockMappings, IMotionReadRoot Root, TimeProvider Time |
| MotionReadBridgeOptions | MotionReadIdentity ExpectedIdentity, AxisScope AllowedScope, MotionReadLimits Limits |

冻结枚举值：`MotionReadAvailability`=`Available=0, Partial=1, NotSupported=2, Unknown=3, Closed=4, DrainUnknown=5`；`MotionDynamicsOrigin`=`ControllerPublished=0, PhysicallyQualified=1, Simulation=2, Replay=3, Unknown=4`；`MotionEvidenceState`=`Confirmed=0, Unknown=1, NotSupported=2, Expired=3, Revoked=4`。`Origin=PhysicallyQualified` 仅表示外部 Owner 的来源标签，Core 不据此签发资格；速度/加速度值必须来自证据正文，不能由 `MotionProfile`、`ControllerCommand`、`Target` 或相邻样本差分生成。

源端只读接口和桥的公开构造固定如下；它们没有任何运动/settled/曝光方法：

```csharp
public interface IMotionReadSource
{
    ValueTask<MotionReadIdentity> GetIdentityAsync(CancellationToken cancellationToken);
    ValueTask<MotionRawHistoryRead> ReadHistoryAsync(
        MotionReadSelector selector, long maxSequence, int maxSamples,
        long maxBytes, TimeSpan deadline, CancellationToken cancellationToken);
    ValueTask<MotionDynamicsEvidence?> ReadDynamicsAsync(
        MotionDynamicsReadRequest request, CancellationToken cancellationToken);
}

public sealed class MotionReadBridge : IAsyncDisposable
{
    public MotionReadBridge(MotionReadBridgeDependencies dependencies,
        MotionReadBridgeOptions options);
    public ValueTask<MotionXYHistoryResult> ReadSynchronizedXYAsync(
        MotionReadSelector selector, string readId, long maxSequence,
        int maxSamples, long maxBytes, TimeSpan deadline,
        CancellationToken cancellationToken);
    public ValueTask<MotionDynamicsResult> ReadRunDynamicsAsync(
        MotionDynamicsReadRequest request, CancellationToken cancellationToken);
    public ValueTask<DrainResult> CloseAsync(TimeSpan deadline,
        CancellationToken cancellationToken);
}

public sealed class MotionReadVirtualSource : IMotionReadSource
{
    public MotionReadVirtualSource(MotionReadIdentity identity,
        MotionReadLimits limits, ImmutableArray<MotionRawHistoryRecord> records,
        ImmutableArray<MotionSequenceGap> gaps,
        ImmutableArray<MotionDynamicsEvidence> dynamics,
        MotionVirtualTimeProvider time);
}
```

`MotionReadBridge` 构造只借用 Source/ClockMappings/Root，不打开设备；`ExpectedIdentity`、`AllowedScope` 和 Limits 在构造时冻结，缺项、Scope 轴不为恰两轴、正/有限上限缺失抛 `ArgumentException`；A.8.5 的桥根槽必须在构造前预留。`ReadSynchronizedXYAsync` 的 `selector.Range` 先以 source `SourceTickStart`、sequence=0 和 target `TargetTick=0` 的两个 `ClockStamp` 调用 `IMotionClockMappingPort.ResolveAsync`，取得当前有理 `ClockMapping`；`OffsetTargetTicks` 以该 TargetDomain/Epoch 的 tick=0 为基准，输出映射的有效 source 范围必须覆盖请求。若 source/target epoch、frequency、有效范围或误差不能覆盖请求，返回 `NotSupported`/`Unknown`，不把 host arrival/UTC/序号当时间。`MotionReadSelector.Range.Target*` 是 mosaic 的 scan clock，桥输出仍保留原 source `ClockStamp` 和完整 mapping 版本供消费者自行复核；桥不替 mosaic 改写 `LineClockMapping`。

现有 `IMotionAdapter.ReadFeedbackAsync` 只提供从订阅建立时起的流时，Adapter/Gateway 必须另以 `IMotionReadSource` 提供可回溯且有界的 records；不能把桥建立后的有限缓存宣称为请求窗口的历史，也不能从 `AdapterFeedback` 两条不同 tick 的轴样本拼成 XY。若源没有连续历史、Core 无法关联 `AxisFeedback.PositionVersion`、没有稳定 `SourceRecordId`/缺包事实、或只能返回 ControllerCommand/Target，则在 source call 前后都返回 `NotSupported`/`Unknown`，不通过插值、最近值、重采样或当前快照填补。`SimulationPlan`/`MotionReadVirtualSource` 可以完整注入这些字段与故障以验证协议，但不证明真实 Adapter 能力。

桥将 `MotionRawHistoryRead.Records` 映射为输出时逐项要求：Identity 与 ExpectedIdentity 完全匹配；AxisSampleX/Y 和 FeedbackX/Y 的Axis、Frame、EncoderActual、EncoderPositiveSign、Clock与原record对应字段逐一相符；原RawAxisSample.Quality须Valid；`AxisSampleX.Clock`/Y 与记录 Clock 的 Domain/Epoch/Tick/Frequency/Sequence 相同；X/Y Sequence 相同且 `Simultaneous=true`；`EncoderActual` 均非 null、有限、单位/Frame一致；`FeedbackX.PositionVersion`/Y 非空；Boot/Generation/Controller/DeviceReferenceRevision不变。输出 `ActualX/ActualY` 只取两条 `RawAxisSample.EncoderActual`，不取 ControllerCommand/Target/CompensatedCommand。保持原Sequence顺序，不通过排序修复倒序；相同SourceRecordId/Sequence的所有原字段完全相同可去重，任一字段不同为Unknown，不以两个自报hash相等代替全字段比较。`Gaps` 必须记录所有缺包区间（含 source 报告的断口和请求首尾无法覆盖部分）；仅 `SourceComplete=true`、无 Gap、序号严格相邻、样本数/字节在限额内才 `IsComplete=true`。任何分轴不同 tick、PositionVersion缺失、实际值缺失、epoch/Boot/Generation变化或源报告不完整都不能生成“同步XY”，返回Partial/Unknown并保留证据。

`ReadRunDynamicsAsync` 只读取外部证据并逐字段核 `Identity`、`RunId`、`ApplicabilityRevision`、`ApplicableRange`、Controller/Boot/Generation/DeviceReferenceRevision、单位、有限正边界、`AllowedOrigins` 和 `State`，重算 EvidenceSha256；不计算/拟合/平滑/从反馈差分推导速度或加速度。`State=Confirmed` 且 `Origin` 在请求 `AllowedOrigins` 内才返回 Available/Evidence；过期、撤销、范围不覆盖或 authority 不明返回 Availability=Unknown、对应 Failure，诊断 Evidence 若保留必须保留原 Expired/Revoked/Unknown State，不能作为物理用途。State=NotSupported 返回 Availability=NotSupported，源无证据返回 Unknown/Evidence=null。`MotionDynamicsEvidence` 是“应用于 run”的只读引用，不保证硬件真实资格；S4 由设备/测量/资格 Owner 另行关闭。

两种请求和证据的完整预像唯一见 A.8.4；复用 A.5 标量编码，不依赖未声明的反射/tag/record 序列化规则。`RequestSha256` 是对应完整请求预像的一次 SHA-256；相同 ReadId+摘要返回同一 result/原 Task，跨 XY/Dynamics 复用 ReadId 也是异摘要冲突。结果的 Identity、每个 sample 的 Identity、Gaps 和 Dynamics Evidence 必须与同一桥闭包一致；不接受调用方自填的 Boot/Generation/Source 来替代 Source.GetIdentityAsync 的回读。EvidenceSha256 按 A.8.4 实际正文排除自身字段后重算，来源自报相同 hash 不代替正文/适用性验证。

#### A.8.2 两个空 Host、资源/关闭和可判定验证

两个消费者 Host 都从空 Exe 开始，不能引用 mosaic 内部或 Motion Adapter：

1. **MosaicViewHost（只读查看）**：构造独立 `TimeProvider`、`MotionReadLimits(MaxSamples=4096, MaxBytes=4*1024*1024, MaxPendingReads=2, MaxQueueDepth=8, MaxObservationWait=250ms, CleanupBudget=1s)`、桥依赖、ExpectedIdentity 和 XY selector；调用 `ReadSynchronizedXYAsync`，只把 `Available/Partial` 的实际样本交给 mosaic 的只读输入，不发任何 Motion 命令。行数/字节/队列超限在 Source 前拒绝；缺包、过期、epoch 改变显示 Unknown/Partial，并保留 Gaps。窗口关闭先取消观察、调用桥 Close，Close 超时保留原桥/Task 交 Host Root，不启动第二次读取。
2. **MosaicAnalysisHost（几何分析）**：使用独立 Owner/Session/BridgeId/Scope 和同样有界但独立的 Limits；先取 XY history，再用同一 `RunId + Target clock range + ApplicabilityRevision` 调 `ReadRunDynamicsAsync`，只有 Evidence=Confirmed 且 source/boot/generation/范围闭包完整才把输入交 mosaic 分析。它不把命令速度、离散差分或 settled 回执当包络；重复相同 ReadId 复用结果，异摘要拒绝。关闭/取消/迟到处理与 ViewHost 相同，两个 Host 的队列、Task、identity、语言和清理互不共享。

两个 Host 的 Synthetic 测试可使用 `MotionReadVirtualSource`（公开构造：`MotionReadVirtualSource(MotionReadIdentity identity, MotionReadLimits limits, ImmutableArray<MotionRawHistoryRecord> records, ImmutableArray<MotionSequenceGap> gaps, ImmutableArray<MotionDynamicsEvidence> dynamics, MotionVirtualTimeProvider time)`），仅验证协议，不模拟真实机械。测试必须覆盖空范围、最大样本/字节/队列及 +1 拒绝、同 tick 与异 tick XY、重复/乱序/缺序列/跨 Boot/Generation/epoch、missing gap、PositionVersion/EncoderActual 缺失、mapping 失效、动态 evidence Unknown/Expired/Revoked、取消前/中/后、deadline、迟到 source task、重复 ReadId、异摘要冲突、关闭时原 Task 强持和独立 cleanup。桥输出不得出现 commanded 值，NotSupported/Unknown 必须带稳定错误和原身份。

本切片测试/性能测点：读取接纳→source call、mapping resolve、首个/最后样本、结果返回、取消到 source task 收敛、Close 到 Resources.Released；分别记录 P50/P95/P99、最大值、样本/字节/队列/Task/回调/托管内存峰值和 Gaps 数，不把虚拟时钟 Advance 当墙钟性能。`MotionReadLimits` 目标缺失则 `NotEvaluated`；故障/迟到/未释放样本不能删掉。每个 case 仍服从 §11.1 的 10s/120s/180s Core harness 墙钟规则，桥自己的 Deadline/CleanupBudget 独立更小者优先。

#### A.8.3 六项准备和真实后门

| 条件 | 本切片结论 |
|---|---|
| 边界/真实消费者 | mosaic FirstLineEncoderTranslationMeshV1；只读连续 XY/动态证据，禁止运动/settled/曝光/图像/标定事实 |
| API/单位/结果/取消/版本/Owner | A.8.1/A.8.4–5 字段、Source/Bridge/ReadRoot 构造、身份闭包、双请求/证据正文预像、NotSupported/Unknown、调用前原Task根槽/清理规则已获主控接收；仅规格准备 |
| 最小无 UI/无 SDK Host | A.8.2/A.8.6 全字段Synthetic夹具、两空Host实际调用、独立ClockMappings/虚拟时钟/有界suite根和finally已规定；尚未创建/编译/运行 |
| 正常/边界/并发/关闭/回退 | 同 tick、缺包、迟到、重复 ReadId、取消/关闭/任务强持/异摘要反例已列；尚未实现测试 |
| Benchmark | 读取/映射/首末样本/取消/关闭 P50/P95/P99、资源与 Gaps 测点已列；客户/硬件目标待 Profile，当前 NotEvaluated |
| 唯一落点/禁止路径/调用顺序 | 只改本指导；实现后仍落 Core/Tests 绑定目录，桥不进入 mosaic/共享/产品代码；真实 Adapter/Gateway 不在本切片 |

本增量六项文档规格已获主控接收，但真实后门仍为：厂商同步反馈SDK/Gateway必须能提供同一真实采样tick的X/Y、连续展开Sequence、原始实际EncoderActual、PositionVersion、Boot/Generation/DeviceReferenceRevision、缺包/回卷事实和可核验source identity；否则桥返回NotSupported/Unknown。速度/加速度物理包络必须由应用于当前run的ControllerPublished/PhysicallyQualified外部Owner证据提供，不能由Core、mosaic、命令Profile或离散反馈自行证明。真实来源/SDK适配、跨进程lease、持久历史、动态测量/物理资格、性能Profile及实测、HIL/现场验收仍为后续门；独立S3/S4和产品集成状态保持。mosaic消费者随后由其原会话接线，本会话不修改mosaic/共享，不创建工程或编码；文档接收不表示产品运行通过。

#### A.8.4 XY/Dynamics 请求与证据正文的精确预像

本节替代 A.8 旧“同域正文沿递归规则”的不完整描述；不改 A.5 或已接收 v0.2 编码。只复用其标量定义：`S(x)`=strict UTF-8 NFC（无 BOM/NUL）的 Int32 little-endian 字节长度和实际 bytes；`I32/I64`=有符号整数 little-endian；`F64`=有限 IEEE754 binary64 bits little-endian，输入 -0 规范为 +0；`+` 仅表示拼接。读取合同独立 wire version **I32(1)**，不是 Core 的 I32(2)。每个字段只写下面规定的实际值，无字段名、CLR 类型名、record tag、额外长度或根 presence。单元/时长不得经文本转换。

| 嵌套对象 | 唯一逐字段顺序 |
|---|---|
| AxisId / CoordinateFrameId | 仅 `S(Value)`；无 wrapper/tag |
| AxisScope | GroupId=null 写单 byte 00；非 null 写 01+S(GroupId)；然后 I32(Axes.Length)+按原序 S(每 Axis.Value)。本读取 Scope 恰为 `[AxisX,AxisY]`，两轴不同；允许 GroupId=null 表示只读选择对，不套用普通轴组运动准入 |
| MotionClockRange | S(SourceDomain), S(SourceEpoch), I64(SourceFrequency), I64(SourceTickStart), I64(SourceTickEnd), S(TargetDomain), S(TargetEpoch), I64(TargetFrequency) |
| MotionReadSelector | S(BridgeId), S(SessionId), S(OwnerId), S(ControllerId), S(ExpectedBootId), I64(ExpectedGeneration), AxisScope 的上述 bytes, S(AxisX.Value), S(AxisY.Value), MotionClockRange 的上述 bytes |
| MotionReadIdentity | S(BridgeId), S(SessionId), S(OwnerId), S(ControllerId), S(BootId), I64(Generation), I32(Source), S(CapabilitySha256), S(ContractVersion), S(SourceDomain), S(SourceEpoch), I64(SourceFrequency) |
| AllowedOrigins | I32(Count)+逐原序 I32(enum)。非空、不重复，顺序进入摘要，不排序；Simulation=2。未知 enum 拒绝 |
| MotionValue | F64(Value)+I32(Unit)；Millimeter=0、Degree=1。这里 XY/dynamics 只允许 mm；速度/加速度量纲分别由 MaxSpeed/MaxAcceleration 字段确定为 mm/s、mm/s²；不把两个单位混用，换米仅在消费边界明确除 1000 |

所有 root/上述 record、集合及必需字符串不得 null；仅 AxisScope.GroupId 可 null，空 string 不视为 null 且按 ID 校验拒绝。集合写 Int32 数量后写元素，无每元素 nullable marker。Deadline/TimestampUncertainty 写 I64(TimeSpan.Ticks)，前者正有限、后者非负有限且有来源；SourceTick 非负、frequency 正、Generation 非负，Int32 长度在分配前 checked/限额。hash 是 64 字符小写 hex，仍写 S(hash)，不是 raw 32 bytes。读取请求不含 MotionUnit 的隐含默认字段，Selector 的实际值由原能力/来源固定；不可把 q、速度或 hash 拼进域名。取消 token、UTC、接收时刻、当前队列水位不进预像。

| 根 | 完整预像（按列示次序，嵌套仅展开上述字段） |
|---|---|
| ReadSynchronizedXYAsync | S("motion-read-v0.1") + I32(1) + I32(1) + S(readId) + Selector + I64(maxSequence) + I32(maxSamples) + I64(maxBytes) + I64(deadline.Ticks) |
| ReadRunDynamicsAsync | S("motion-read-v0.1") + I32(1) + I32(2) + S(request.ReadId) + Selector + S(RunId) + S(ApplicabilityRevision) + AllowedOrigins + I64(MaxBytes) + I64(Deadline.Ticks) |
| MotionDynamicsEvidence | S("motion-read-evidence-v0.1") + I32(1) + Identity + S(EvidenceId) + S(RunId) + S(ApplicabilityRevision) + ApplicableRange + S(AuthorityId) + S(DeviceReferenceRevision) + MaxSpeedX + MaxSpeedY + MaxAccelerationX + MaxAccelerationY + I64(TimestampUncertainty.Ticks) + I32(Origin) + I32(State) |

证据预像只省略 `EvidenceSha256`，不省略 EvidenceId、原 Identity/CapabilitySha256、run、范围、authority、单位、误差、Origin/State。EvidenceId/ApplicabilityRevision 为原 Owner 的稳定外部标识，不能由 EvidenceSha256 自身生成；Identity.CapabilitySha256 是独立原能力摘要，不能指该证据/request。RequestSha256/EvidenceSha256 都是对应完整预像一次 SHA256 的64位小写hex，不截断、不再次 hash hex。桥从 actual evidence 正文重建并比较，篡改数值/单位/run/范围/State/hash任一项都拒绝；摘要相等只证明内容，不证明外部authority可信或真实物理资格。source 开始/结束适用性核验仍必需。上述根仅供桥内部计算；不新增第二工厂或额外产品 codec API。

**全字段独立向量**：公共 Selector=`BridgeId=b1, SessionId=s1, OwnerId=o1, ControllerId=c, ExpectedBootId=k, ExpectedGeneration=1, Scope=(GroupId=null, Axes=[X,Y]), AxisX=X, AxisY=Y, Range=(d,e,1000,0,2,t,u,1000)`。这些是 Synthetic ID。请求域字符串 UTF-8 实际长度16；不是15。

`MR-XY-01`：上述 Selector，readId=`xy1`，maxSequence=2，maxSamples=2，maxBytes=4096，deadline=2500000 ticks。完整 **176 bytes**，SHA256=`c45f21a75eb127a312c88906376a31709d9abdbbd96b6286f127fdc6694ee903`：

```text
100000006d6f74696f6e2d726561642d76302e31010000000100000003000000787931020000006231020000007331020000006f310100000063010000006b01000000000000000002000000010000005801000000590100000058010000005901000000640100000065e8030000000000000000000000000000020000000000000001000000740100000075e8030000000000000200000000000000020000000010000000000000a025260000000000
```

`MR-DY-01`：上述 Selector，ReadId=`dy1`, RunId=`run`, ApplicabilityRevision=`rev`, AllowedOrigins=[Simulation=2], MaxBytes=4096, Deadline=2500000 ticks。完整 **186 bytes**（与 mosaic 的旧186-byte向量无关），SHA256=`14fea86c4b75282e597f9fc30d53bc58a114f6169e5130aec0fa0e3be7f44661`：

```text
100000006d6f74696f6e2d726561642d76302e31010000000200000003000000647931020000006231020000007331020000006f310100000063010000006b01000000000000000002000000010000005801000000590100000058010000005901000000640100000065e8030000000000000000000000000000020000000000000001000000740100000075e8030000000000000300000072756e0300000072657601000000020000000010000000000000a025260000000000
```

`MR-EV-01`：Identity=`(b1,s1,o1,c,k,1,Simulation=0,"a"重复64次,motion-read-bridge-v0.1,d,e,1000)`；EvidenceId=ev，RunId=run，ApplicabilityRevision=rev，ApplicableRange 与上述 Range 相同；AuthorityId=auth，DeviceReferenceRevision=ref；四个 MotionValue 依序 `(2,mm),(2,mm),(10,mm),(10,mm)`，TimestampUncertainty=0 ticks（明确Synthetic事实）、Origin=Simulation=2、State=Confirmed=0。EvidenceSha256 字段省略。完整 **337 bytes**，SHA256=`9e4921bc2b8c63a9853f3b69d3ccc015ce61c0503bf6d8a81cb872a34d918e77`：

```text
190000006d6f74696f6e2d726561642d65766964656e63652d76302e3101000000020000006231020000007331020000006f310100000063010000006b0100000000000000000000004000000061616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161170000006d6f74696f6e2d726561642d6272696467652d76302e3101000000640100000065e8030000000000000200000065760300000072756e0300000072657601000000640100000065e8030000000000000000000000000000020000000000000001000000740100000075e80300000000000004000000617574680300000072656600000000000000400000000000000000000000400000000000000000000024400000000000000000000024400000000000000000000000000200000000000000
```

后续合同断言须以这些全字段输入在独立 BinaryWriter 实现中重建完整bytes，与正文hex/长度/hash比较；不能调用受测桥生成“期望hash”。另测同 ReadId 的 XY 与 Dynamics 得到不同预像并冲突、Scope 原序、Origins 顺序改变摘要、GroupId null与非null不同、EvidenceSha256替换不改变证据预像但校验失败、任何正文实际值变化改变证据摘要、旧A.5 46/47/102-byte向量原样保留。

#### A.8.5 桥根 Owner、原 Task 和有限 Close

已接收 `IMotionLifecycleOwner.Retain(IMotionSession,...)` 不适用于桥，不改其方法。本增量 Dependencies.Root 改为下述 `IMotionReadRoot`；仅是只读桥原已要求的根保持端口，不增运动工厂/API。宿主实现须在任何 Source/ClockMappings 调用前存在并取得容量，不能在 timeout 后才临时创建 Owner。

```csharp
public interface IMotionReadRoot
{
    bool TryReserveBridge(MotionReadIdentity identity, MotionReadLimits limits);
    void AttachBridge(MotionReadIdentity identity, MotionReadBridge bridge);
    string? TryReserveCall(MotionReadIdentity identity, string readId,
        string stage, ImmutableArray<object> borrowed);
    void AttachTask(string slotId, Task originalTask);
    void ConfirmCall(string slotId);
    void RetainBridge(MotionReadIdentity identity, MotionFailure reason);
    bool ConfirmBridgeReleased(MotionReadIdentity identity, DrainResult? closed);
}
```

这些方法有界/线程安全/不执行 IO、不回调桥；Attach/Retain/Confirm 不抛异常。TryReserveBridge 不成功则构造/Source调用次数0；成功在根内保留 Identity/Limits 槽，构造成功 AttachBridge，构造失败 ConfirmBridgeReleased(identity,null)只在从未Attach且无call/Task时收回空槽。同 Identity 只允许一个桥，不能重构绕过未知任务。Root 保留桥和所有源/clock/selector/两个轴 record 及请求不可变内容，不使用弱引用。`MotionReadResources.Released` 是某回执时刻的读临时资源投影，不能释放桥根；正常删除必须传**原桥实际Close返回**的closed，SessionId等于绑定身份、Drain=Drained/Resources=Released/IsReleased=true/PendingOperationIds为空，并且Root原子检查无reserved/attached/processing call和临时输入/后处理。桥只有queue/临时缓冲也零才产生该Close回执；调用者不得用某个读结果Resources或自造回执代替。结果是独立不可变owned副本，根删除不改变已交付值。

每次源调用的唯一实现顺序：接纳读并占有有界 readId slot → TryReserveCall（先保留 Source/ClockMappings/原selector/两轴输入及内部独立token）→ slot!=null 才调用端口 → 得到 ValueTask 后只调用一次 AsTask/AttachTask，AttachTask 保存**原 Task**，不保存 WaitAsync 包装 → 在 gate 外有限观察原 Task → 实际完成、异常已观测、输出已复制/丢弃并归还临时输入/回调后 ConfirmCall。同步端口抛错也在原slot记录失败后 ConfirmCall；端口在调用返回 ValueTask 前同步阻塞，Host仍有reserved slot/bridge/borrowed输入强引用，不会因缺Task而删除根；端口禁止同步阻塞，反例测试通过闩锁返回未完成Task，不冒称同步阻塞可被token抢占。

XY 顺序为 GetIdentity(before) → ClockMappings.Resolve → ReadHistory → GetIdentity(after)，Dynamics 为 GetIdentity(before) → ReadDynamics → GetIdentity(after)；每阶段都先预留自己的 slot。仅在 before/after 等于原 ExpectedIdentity、当前 IsCurrent(mapping) 和正文/范围/证据核验后交付 Available。source task 超时/取消仍运行就停在该阶段，不启动下阶段、不重启同阶段，不把迟到的旧identity结果交付新的read。Roots 当前未知读取占 MaxPendingReads，普通队列 MaxQueueDepth 有界；满额返回 MOTION_RESOURCE_LIMIT，sourcecall为0；同读重复不增加槽/Task。root 的 `stage` 固定 IdentityBefore/ClockResolve/History/Dynamics/IdentityAfter，slotId 由根单调counter分配且不复用，root lifetime内counter溢出拒绝新调用。每 readId 至多一个外部原Task在执行，保留的两轴数组/映射和结果bytes均计入 MaxBytes。

请求 Deadline 从首次读取接收的注入 TimeProvider timestamp 开始，sourcecall/queue/identity重核共用剩余预算，不分阶段续期；观察取 deadline、MaxObservationWait 与调用者取消中的最先。调用者 token 不传入源；源用桥内部独立清理token，请求取消只停止观察/交付。本次取消/超时结果 Availability=Unknown，Failure=MOTION_CANCELLED/MOTION_TIMEOUT_UNKNOWN，Resources.Released=false只要原Task/后处理未完；None token同样有限。原Task迟到后桥唯一continuation观测错误、丢弃未交付结果、归还临时持有再 ConfirmCall，不续读取/交付、不覆盖原取消回执，也不影响其它read。已确认Released的完整结果可从有限readId缓存复用，不反复IO；缓存条目容量=MaxQueueDepth+MaxPendingReads，bytes计MaxBytes，容量满就拒绝新ID，不删除幂等身份后重读旧ID。

Close 首次线性化Closing、关闭新读、停止queue、请求本桥内部取消；每次 Close 观察预算=min(传入正有限deadline,Limits.CleanupBudget)，从本次Close接收起计。ct只取消观察，清理仍用独立budget；已挂起源/Resolve任务不会被丢弃，重复Close只观察/续归还同原Task。Drained/Released要求所有reserved/attached/processing slots/queues/临时buffers/回调=0，不依赖Source.Read结果自己的Resources字段。失败DrainUnknown/Resources=Held/IsReleased=false，PendingOperationIds写原readId而非motion operation，SessionId沿桥绑定原Session。Close失败先Root.RetainBridge再返回；DisposeAsync调同Close，失败Root.RetainBridge并抛既有MotionDrainException（原SessionId），不擅自Dispose借用Source/ClockMappings/MotionSession。恢复必须由原Host保留该Root，并在源的受控故障解除/原Task真实退出后→同桥再次Close→ConfirmBridgeReleased，不能“移交成功”或方法离栈当释放；Root本身没有释放运行Task的API。原业务错误先保存，finally清理错误另记、不替换原异常。

#### A.8.6 两个完整 Synthetic Host 与端口实施块

以下是未来 Core.Tests `Consumers/MotionRead/` 内的测试实施正文；只引用 BCL+本模块Core。`ReadFixture.cs`、`ReadBinary.cs`、`ReadPorts.cs`、`ReadViewHost.cs`、`ReadAnalysisHost.cs` 是后续绑定工程的责任位置，本轮不创建文件/工程。Fake字段全部为Synthetic，SourceKind=Simulation、Origin=Simulation、State=Confirmed只是协议fixture，任何宿主不可把它交成Hardware资格。下面的声明/调用尚未编译，不声称现有代码；每个构造字段都明确，辅助端口行为在后表固定，不能只写一个泛称fixture补猜。

```csharp
using System.Collections.Immutable;
using System.Security.Cryptography;
using System.Text;
using Asun.Modules.MotionControl;

internal sealed class ReadFixture
{
    public MotionReadIdentity Identity { get; }
    public MotionReadSelector Selector { get; }
    public MotionReadLimits Limits { get; }
    public MotionDynamicsReadRequest DynamicsRequest { get; }
    public MotionReadBridgeDependencies Dependencies { get; }
    public MotionReadBridgeOptions Options { get; }
    public SyntheticReadRoot Root { get; }
    public SyntheticReadScript Script { get; }
    public MotionReadVirtualSource VirtualSource { get; }
    public MotionVirtualTimeProvider DeviceClock { get; }
    public ImmutableArray<MotionRawHistoryRecord> Records { get; }
    public MotionDynamicsEvidence Evidence { get; }
    public static string H(string text) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(text))).ToLowerInvariant();

    public ReadFixture(bool analysis)
    {
        var x = new AxisId("X"); var y = new AxisId("Y");
        var frame = new CoordinateFrameId("axis");
        var scope = new AxisScope(null, ImmutableArray.Create(x,y));
        // b1/s1/o1对应MR-XY/DY/EV向量；第二Host独立闭包b2/s2/o2。
        Identity = new(analysis?"b2":"b1", analysis?"s2":"s1", analysis?"o2":"o1",
            "c","k",1,SourceKind.Simulation,new string('a',64),
            "motion-read-bridge-v0.1","d","e",1000);
        var range = new MotionClockRange("d","e",1000,0,2,"t","u",1000);
        Selector = new(Identity.BridgeId,Identity.SessionId,Identity.OwnerId,"c","k",1,
            scope,x,y,range);
        Limits = new(4096,4L*1024*1024,2,8,TimeSpan.FromTicks(2500000),TimeSpan.FromSeconds(1));
        DynamicsRequest = new("dy1",Selector,"run","rev",
            ImmutableArray.Create(MotionDynamicsOrigin.Simulation),4096,TimeSpan.FromTicks(2500000));
        DeviceClock = new(new DateTimeOffset(2000,1,1,0,0,0,TimeSpan.Zero));

        MotionValue Mm(double n) => new(n,MotionUnit.Millimeter);
        RawAxisSample Raw(AxisId axis,double actual,ClockStamp at) => new(axis,
            null,Mm(actual),Mm(axis==y?2:0),Mm(0),Quality.Valid,frame,null,1,
            Truth.True,Truth.True,Truth.False,Truth.False,Truth.False,Truth.False,
            at,"ref",Truth.False,Truth.False,null,Truth.False,Truth.False);
        AxisFeedback Feedback(RawAxisSample raw,string positionVersion) => new(raw.Axis,
            MotionState.Moving,"state-1",positionVersion,null,null,null,raw.EncoderActual,
            null,raw.Velocity,raw.FollowingError,Quality.Valid,frame,null,1,
            raw.Axis==y?Direction.Positive:Direction.Unknown,Truth.True,Truth.True,
            Truth.False,Truth.False,Truth.False,Truth.False,raw.Clock,0,
            Truth.False,Truth.False,null,Truth.False,Truth.False);
        MotionRawHistoryRecord Record(long sequence,long tick,double actualY)
        {
            var at = new ClockStamp("d","e",tick,sequence,1000);
            var sx=Raw(x,0,at); var sy=Raw(y,actualY,at);
            return new("rec-"+sequence,"c","k",1,sequence,at,x,y,sx,sy,
                Feedback(sx,"px1"),Feedback(sy,"py"+sequence),"ref",
                TimeSpan.Zero,true,SourceKind.Simulation);
        }
        // 同步tick0/2(=0/2ms)，仅actual Y=0/.004mm；commanded为空。
        Records = ImmutableArray.Create(Record(1,0,0),Record(2,2,0.004));
        DeviceClock.Advance(TimeSpan.FromMilliseconds(2)); // 读取已形成的历史，不读未来帧。
        var unsigned = new MotionDynamicsEvidence(Identity,"ev",new string('0',64),
            "run","rev",range,"auth","ref",Mm(2),Mm(2),Mm(10),Mm(10),
            TimeSpan.Zero,MotionDynamicsOrigin.Simulation,MotionEvidenceState.Confirmed);
        // ReadBinary是下面规定的独立测试编码器，不调用受测桥。
        Evidence = unsigned with { EvidenceSha256 = ReadBinary.EvidenceHash(unsigned) };
        VirtualSource = new(Identity,Limits,Records,
            ImmutableArray<MotionSequenceGap>.Empty,ImmutableArray.Create(Evidence),DeviceClock);
        Script = new(TimeProvider.System,4);
        Root = new(1,8,TimeProvider.System); // 调用前1桥根/8 call槽，非静态。
        var source = new SyntheticReadSource(VirtualSource,Script);
        var map = new ClockMapping(H("Synthetic-map-d-to-t"),"d","e","t","u",1,1,0,0,0,2);
        var mappings = new SyntheticReadClockMappings(map,1000,1000,Script);
        Dependencies = new(source,mappings,Root,TimeProvider.System);
        Options = new(Identity,scope,Limits);
    }
}
```

Source时间取DeviceClock，桥期限取 `TimeProvider.System`，测试外层取 Stopwatch；设备虚拟Advance既不推动/暂停250ms观察，也不冒充软件耗时。两端映射为明确1000Hz→1000Hz、scale1/1、offset0、误差0、有效域[0,2]的Synthetic事实，不用第一次收包推零点。XY实际0/.004mm转换到mosaic米制为0/.000004m，0.5/1.5ms插值是.000001/.000003m；这只是消费者转换断言，Motion桥不执行插值，也不发settled。

**独立测试编码器** `ReadBinary` 的签名/实现形状固定：static `byte[] XY(MotionReadSelector s,string readId,long maxSequence,int maxSamples,long maxBytes,TimeSpan deadline)`、`byte[] Dynamics(MotionDynamicsReadRequest request)`、`string EvidenceHash(MotionDynamicsEvidence evidence)`。每个方法创建独立MemoryStream+BinaryWriter(strict UTF8无BOM)，按 A.8.4硬编码字段顺序，S先NFC校验/写UTF8长度bytes，I32/I64写对应整数，F64先有限/-0规范化后写 `BitConverter.DoubleToInt64Bits`；GroupId按00/01、集合按Int32/count逐项。Evidence只省EvidenceSha256。SHA256对ToArray完整bytes计算。禁止 GetProperties/反射排序、JSON、动态record tag、调用受测模块encoder生成期望。Viewfixture重建A.8.4三份向量；Analysisfixture同方法全字段重建，b2/s2/o2必须使所有请求/证据hash变化，且BridgeId/SessionId/OwnerId闭包不与View相同。其它字段与View完全一致，不能为“第二Host”只换一个显示标签。

**`ReadPorts.cs` 的确定实现规格**（internal测试端口，不新增产品工厂）：

| 测试端口/精确构造与成员 | 唯一行为 |
|---|---|
| `SyntheticReadRoot(int maxBridges,int maxCallSlots,TimeProvider clock) : IMotionReadRoot`；只读 `int ActiveBridgeCount`/`int ActiveCallCount`；`void NoteCleanup(Exception error)` | 锁保护固定容量Bridge/Call字典，逐字实现A.8.5全部签名；槽预留即强持borrowed，AttachTask只接原Task，ConfirmCall仅在真正任务完成且桥后处理完后删call；ConfirmBridgeReleased仅无call/processing/queue才删bridge。不以Result.Resources.Released删根。超额TryReserve返回false/null；NoteCleanup有界队列、不抛，保留原业务错误。测试需访问原Task.IsCompleted和借用对象身份，不能只用计数自报证明归还 |
| `SyntheticReadSuiteRoot(int maxRoots)`；`bool TryHold(SyntheticReadRoot root)`、`void ConfirmClosed(SyntheticReadRoot root)`、只读 `int PendingRootCount` | 测试进程最外层先构造，固定容量字典强持每个Host根；TryHold在ReserveBridge/桥构造/源调用前完成，容量满禁止新Host。ConfirmClosed仅两根计数0且所有Task/后处理已确认才移除；未释放、错误或观察到期都保留。suite结束PendingRootCount>0必需失败非零；宿主生命周期对象继续持此实例，不用临时局部/finalizer代替 |
| `SyntheticReadScript(TimeProvider wallClock,int maxGates)`；`void Arm(string stage)`、`Task WaitEnteredAsync(string stage,TimeSpan budget)`、`void Release(string stage)`、`Task AtAsync(string stage)` | stage只允许Identity/ClockResolve/History/Dynamics，Arm为下一次该stage建立TaskCompletionSource闩锁；At进入时标Entered并返回原未完成Task，忽略请求ct；Release只完成该原TCS一次，不创建替代Task。WaitEntered用独立wallClock有限budget；容量不足拒绝Arm，重复Arm拒绝。所有TCS使用RunContinuationsAsynchronously，无sleep/静态状态 |
| `SyntheticReadSource(IMotionReadSource inner,SyntheticReadScript script) : IMotionReadSource` | GetIdentity：await AtAsync(Identity)再调用inner.GetIdentity；History：await AtAsync(History)再调用inner.ReadHistory；Dynamics同理。恰实现A.8.1接口，不额外发布运动/关闭/读取入口；wrapper原Task始终由桥Root登记。可在某stage定向脚本抛错；Bridge唯一finally必须处理。关闭挂起测试用Script.Release原stage，再同桥Close，不重建inner |
| `SyntheticReadClockMappings(ClockMapping mapping,long sourceFrequency,long targetFrequency,SyntheticReadScript script) : IMotionClockMappingPort` | Resolve先await AtAsync(ClockResolve)，要求两stamp Domain/Epoch/Frequency与构造一致、source.Tick在[0,2]、target.Tick=0，返回唯一固定mapping，否则null；IsCurrent仅比较构造MappingSha256。撤销测试把实例本地Current=false，IsCurrent返回false；不会修改mapping原值/hash，闭包来源标签Synthetic |
| `MotionReadVirtualSource`（产品增量构造见A.8.1） | GetIdentity返回原identity，History按range/maxSequence限制读取、保持原sequence/records，任何截断必须SourceComplete=false且报Gap，不造PositionVersion或混两个tick；Dynamics按RunId/Revision/完整Range返回原evidence，否则null。时间和错误范围来自构造、无隐藏随机/外推/SDK；异常record结构可注入给桥验证，不预先“修好”反例 |

两种 Host 的实际调用/收尾示例如下，核心读入口只用现有A.8接口。future Exe入口先构造 `var suite = new SyntheticReadSuiteRoot(2)`，再调用 `RunReadHost(false,suite,ct)` 与 `RunReadHost(true,suite,ct)` 两个独立入口，suite一直在进程入口的强引用中。View也读取Dynamics闭包（显示用但不宣称物理资格）；Analysis另外核两个实际值/PositionVersion/run，均只能把已核输出交宿主投影，不引用mosaic私有DTO。

```csharp
static async Task<(MotionXYHistoryResult XY,MotionDynamicsResult Dynamics)>
    RunReadHost(bool analysis,SyntheticReadSuiteRoot suite,CancellationToken caller)
{
    var f = new ReadFixture(analysis);
    if (!suite.TryHold(f.Root))
        throw new InvalidOperationException("Synthetic suite root capacity exhausted");
    if (!f.Root.TryReserveBridge(f.Identity,f.Limits))
    {
        suite.ConfirmClosed(f.Root); // 尚无bridge/call，只回收空根。
        throw new InvalidOperationException("Synthetic root capacity exhausted");
    }
    MotionReadBridge? bridge = null;
    try
    {
        bridge = new(f.Dependencies,f.Options); // 构造前根槽已登记。
        f.Root.AttachBridge(f.Identity,bridge);
        var xy = await bridge.ReadSynchronizedXYAsync(f.Selector,"xy1",2,2,4096,
            TimeSpan.FromTicks(2500000),caller);
        if (xy.Availability!=MotionReadAvailability.Available || !xy.IsComplete
            || xy.Samples.Length!=2 || xy.Gaps.Length!=0 || xy.Mapping is null)
            throw new InvalidOperationException("Synthetic XY unavailable");
        if (xy.Samples[0].ActualY.Value!=0 || xy.Samples[1].ActualY.Value!=0.004
            || xy.Samples[0].PositionVersionX!="px1"
            || xy.Samples[1].PositionVersionY!="py2")
            throw new InvalidOperationException("Synthetic actual/version mismatch");
        var dynamics = await bridge.ReadRunDynamicsAsync(f.DynamicsRequest,caller);
        if (dynamics.Availability!=MotionReadAvailability.Available
            || dynamics.Evidence is not MotionDynamicsEvidence evidence
            || evidence.State!=MotionEvidenceState.Confirmed || evidence.RunId!="run"
            || evidence.Identity!=f.Identity || evidence.EvidenceSha256!=f.Evidence.EvidenceSha256)
            throw new InvalidOperationException("Synthetic dynamics unavailable");
        // 两个Host只读拥有值；没有Move/Stop/Settled/Exposure调用。
        return (xy,dynamics);
    }
    finally
    {
        // 不传caller；None也受Close独立1s预算，原业务异常不能被cleanup覆盖。
        if (bridge is null)
        {
            if (f.Root.ConfirmBridgeReleased(f.Identity,null))
                suite.ConfirmClosed(f.Root); // 仅回收无call的构造失败空根。
        }
        else
        {
            try
            {
                var closed = await bridge.CloseAsync(TimeSpan.FromSeconds(1),CancellationToken.None);
                if (!closed.IsReleased || !f.Root.ConfirmBridgeReleased(f.Identity,closed))
                    f.Root.RetainBridge(f.Identity,closed.Failure ?? Pending(f.Identity));
                else
                    suite.ConfirmClosed(f.Root);
            }
            catch (Exception cleanup)
            {
                f.Root.NoteCleanup(cleanup);
                f.Root.RetainBridge(f.Identity,Pending(f.Identity));
            }
        }
    }
}

static MotionFailure Pending(MotionReadIdentity id) => new(
    "MOTION_DRAIN_TIMEOUT","Motion.Error.DrainTimeout",
    ImmutableDictionary<string,string>.Empty.Add("bridgeId",id.BridgeId),
    false,null,null,false,false,null,"Motion.Recovery.QueryOriginalRead");
```

`return` 只归还owned值，不表示整个桥释放；正常Host测试返回后还断言Root计数0、原Task都真正完成。finally失败时suite字典仍强持Root→bridge→Source/ClockMappings/所有原Task/两轴输入，不因f离栈而被GC回收；真实宿主将suite/root放进应用生命周期对象，禁止用临时局部Root即返回后忘掉。Pending.PossiblePhysicalEffect=false仅因**该桥本身**无物理写，不声明借用的真实Controller已停止。前台参数/消费者异常不发Stop给其它Motion Owner。恢复在同suite确认后才ConfirmClosed删除原root；清理失败额外日志不覆盖原读取/分析异常。

**挂起/迟到的实际恢复调用**：在构造前fixture/root准备后，`f.Script.Arm("History")`（分别对Identity/ClockResolve/Dynamics重复此独立case）；ReserveBridge→构造/Attach→保存 `Task<MotionXYHistoryResult> originalRead = bridge.ReadSynchronizedXYAsync(...).AsTask()`（Dynamics case保存对应Task）→有限WaitEnteredAsync(History,1s)→取消caller或等250ms观察→Unknown且Root.ActiveCallCount>0；本originalRead只是桥返回Task，Root另外须有inner源原Task，其IsCompleted仍false。finally调用Close(1s,None)为DrainUnknown，根和X/Y record/selector/映射依赖保留→suite recovery先 `f.Script.Release("History")`→等inner原Task实际完成和桥late-result processing确认（外层1s墙钟，非无限await）→同实例Close(1s,None)→ConfirmBridgeReleased=true、两根计数0。迟到输出不再交付原取消读者，也不继续下阶段GetIdentity，重复同readId只返原取消结果；未释放case必需失败，suite不得退出0。Identity/ClockResolve同样必须在端口调用前已有root slot，Cancel/Close不会删除它们；同步throwcase也在finally收回call槽。受控Source.Release来自Script而非Root API，根只保管，不“释放”尚运行Task。

本窄补充两轮有限核对：第一轮按嵌套字段独立复算MR-XY/DY/EV bytes/hash，校验域入口/版本/自身字段排除和两Host构造字段/单位/实际值；2026-10-11 Python struct/UTF8/hashlib和独立.NET BinaryWriter/UTF8/SHA256逐字段重建176/186/337 bytes，完整hex/length/hash一致。第二轮沿Identity→Mapping→History/Dynamics→IdentityAfter、调用前原Task登记/取消/迟到/finally/同实例Close与suite根删除核Owner闭包，Closed receipt不能以读结果Released代替。主控已完成A.8.1–6回读并独立逐字段确认三份完整向量，接收Motion Read Bridge v0.1为 `ModuleCoreImplementationReady`（仅六项文档规格准备）。新增测试断言计入原Core Exe 10s/120s/180s；未创建工程、测试/脚本文件，未编译或运行产品Core/SDK/WPF/Benchmark/HIL/现场检查，不授真实能力或产品资格。
