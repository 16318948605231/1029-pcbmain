# IM-064 googol-motion-adapter 开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2`

- 模块：`IM-064` / `googol-motion-adapter`；版本：`0.3.0-prep`；日期：2026-10-11。
- 状态：整体 `DesignReview/Prep`；C1/C2 六项文档规格已接收为 `ModuleCoreImplementationReady`；W1/N1及产品集成保持 `PreparationIncomplete / NotReady`，不自动开工。
- 基线：C# / .NET10 / x64；可选 WPF / 本机 DevExpress25.2.3。
- 永久会话：`01a1053f-d078-79e1-b675-d05126c8ea82`，见 [模块索引](../MODULE-INDEX.md)。
- 消费者：扫描宿主、独立定位/维护工具；均可无UI，WPF诊断包可选。

正文与附录A共同定义唯一规格，不表示代码、build/run、WPF、性能、Golden/Replay、HIL或现场已通过。当前仅修改本文，不创建产品工程/脚本/报告，不写其它模块、共享入口、参考原件、客户项目或AsunImage内部。非视觉事务，不使用HALCON；不安排依赖安装/授权核验。

## 1. 职责与研究依据

### 1.1 边界

Core负责固高配置、地址一致性、单位换算、配置摘要与无设备脚本工厂。Native负责连接/厂商ABI、能力证据、命令/原始反馈、有限等待、资源收敛和诊断。卡核轴只存在本模块配置/诊断，不泄漏上游逻辑轴/业务对象。

[IM-010 motion-control](../motion-control/DEVELOPMENT-GUIDE.md) 当前Module API v0.2已有精确IMotionAdapter，持有准入/授权/幂等账本、状态、目标版本、settled、实际停止判定和终态。不再写接口不存在/候选，不另造NativeMotionCommand、万能Execute或运动状态机；规格存在不等于程序集已构建。[IM-041 device-signals](../device-signals/DEVELOPMENT-GUIDE.md) 持有DI/DO/AI/AO、脉冲/过滤/质量/Journal语义，固高仅实现其§7.1 typed子端口。

不承载采集、灯光、板流、工艺判定、质量放行、安全PLC或机械安全链；软件Stop不称硬件急停，不提供任意宿主制造EStop事实的方法。不搬静态GGClass、WinForms页面、StartupPath或默认参数。

### 1.2 只读来源与结论

来源：[GGSport](../../references/project-snapshots/GGSport/20261004/README.md)、[manifest](../../references/project-snapshots/GGSport/20261004/source-manifest.json)、[DZ-XVision](../../references/project-snapshots/DZ-XVision/20261004/README.md)。manifest tree SHA-256分别为`f62c102b565cc145e97a123407544d89f5188a2d5ed1d056dfcba5fdb4802681`、`a3649338762b234537d185d18496fcd438ba91eafd06b8d817ebee4c5a5ceae8`，不是全项目审计。

| 已读原件与hash | 可迁移事实 | 不照搬/落点 |
|---|---|---|
| GGSport GGClass.cs：`9c75031245bf847af1eb7f46e9eba98432c6008adb7e2dbf03c4817eb5faa9f2` | 状态/limit/encoder，Trap/Jog/Update、Home、FIFO/IO | OpenCard隐含Reset/LoadConfig/ResetExtMdl/ClrSts，须拆只读；MoveRel截断encoder加delta不可复用；CloseCard/AxisOff不证明停止，见§4～6 |
| GtsCompat.cs：`5e9198a294fa30f54760b91fb62636c731fd4279351fb5538facfccab78cd986` | GTN、compare/capture/FIFO声明定位 | 不是目标DLL导出/设备支持证明；out string、C long/C# long、packing/数组count不可照抄，见§4.1 |
| gts.cs：`611b45b093cbdacb8c40f53b3b00b7f24cddb8331cb3034abf7e42ae88c5266f` | 原码、结构与候选能力 | 负码有通信错误，正15/16/17有版本warning，不能非负=成功 |
| axisConfig.json / IOConfig.xlsx / GGControl.cs | Home、地址、电平与反馈需求 | 显式迁移/三语投影，禁止旧UI/静态状态/IO权限 |
| DZ-XVision Motion9014.cs / NcConfig.vb | 轮询、回零反向恢复/停止等待/独立IO场景 | 不搬裸Thread、无限重试、INI默认/产品流程；恢复由批准Profile/上游决定 |

只移植思想/断言，未复制源码、未改客户交付项目；来源原生声明不能代替目标官方ABI。SDK资料缺口仅阻断依赖它的函数。

### 1.3 官方与固定源码

已读 [.NET native interop](https://learn.microsoft.com/en-us/dotnet/standard/native-interop/best-practices)、[CancellationToken](https://learn.microsoft.com/dotnet/api/system.threading.cancellationtoken)、[Task.WaitAsync](https://learn.microsoft.com/dotnet/api/system.threading.tasks.task.waitasync)、[Thread.Abort](https://learn.microsoft.com/dotnet/api/system.threading.thread.abort)：精确ABI/SafeHandle/有限观察；协作取消、等待到期不证明native中止。

已读dotnet/runtime固定tag `v10.0.0`（commit `60629d14374c56f1cb51819049ad1fa529307f8d`）的 [Process.Windows.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Diagnostics.Process/src/System/Diagnostics/Process.Windows.cs)，SHA-256 `49620fb20feffb84e36d587a381c0cf161e3ec8c114f6ff1e7fa2d7672b518cf`；[ProcessTests.cs](https://github.com/dotnet/runtime/blob/60629d14374c56f1cb51819049ad1fa529307f8d/src/libraries/System.Diagnostics.Process/tests/ProcessTests.cs)，`edd67501aab8241740cf6a4c1f42661a26ff2a5f1f5698799a88755d7c4bb98e`。TerminateProcess与WaitForExitCore分离，Kill_NotStarted、Kill_ExitedChildProcess_DoesNotThrow、Kill_EntireProcessTree_False_OnlyRootProcessTerminated提供退出/异常/树边界反例。MIT，仅用.NET10 BCL，不复制实现/新增包；进程退出不证明设备运动/输出停止。

已读官方 [DockLayoutManager 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)、[GridControl 25.2](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl?v=25.2)。网页族版本不等于25.2.3编译；无dxdocs可调用端口，补用本机匹配官方XML，见§8.4，不安装升级。

### 1A. 新架构适配要点

**架构门禁**：固高适配器 Core 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；`gts.dll` SDK 只在 Native 层，不进入公共契约。§1.1 已明确"不搬静态 GGClass、WinForms 页面或 StartupPath"。

**Blazor/Web**：Web 端只展示轴状态/限位/编码器（通过 `device-signals` 的信号通道投影）；写命令必须经 `motion-control` 已授权接口，不经浏览器直接调用 `gts.dll`。

**AI/HALCON**：固高适配是纯设备事务，不执行视觉算法；双跑 CI 不涉及本模块。

## 2. 分层、共享物理Owner

```text
两个宿主 → IM-010 MotionSession / IM-041 SignalRoot+Service
                  ↓ 当前公开typed ports
        固高Motion子端口 / Signals子租约
                  ↓ 同一physical Owner
        有界调度/独立停止/x64 native worker → 控制器
```

宿主组合根在首次Open/Acquire/worker之前预留、登记并强持Owner/原task槽，一个physical controller一个Owner。身份取批准设备键，不能用UI名/card索引/枚举顺序，多卡歧义拒绝。Core校验不打开设备。

MotionSession构造成功接管未打开IMotionAdapter，其余Dependencies借用；子端口Close/Dispose仅收敛本租约/订阅，不关闭Signals。Signals Adapter无资源，Acquire产出lease，Errors非空仍归还非空产物；Release不复位输出、不关闭其它租约。最后子租约/native原task/callback/consumer真实退出才物理Close；Unknown的身份/原task/查询入口仍由原Owner保留，不能随句柄释放删除。

Motion写fencing/lease由IControllerLeasePort；Signals通道由mapping/授权/幂等域，不互授权。轴内置Home/limit/INP直接作为Motion原证据，不强依赖IM-041；重复线路登记唯一读写Owner/电平revision。Compare位置表归Motion，线路/电平/宽度归Signals/采集宿主，双回执关联；一方Unknown不启动采集，不承诺跨域原子提交。

Owner锁仅接纳/计数/代/task登记，锁内不await SDK/授权/账本/Dispatcher/消费者。SDK全局选卡核+调用同单元串行；若进程全局选择按SDK全局互斥，不能只锁card。Native affinity以目标资料冻结；Core不要求STA，WPF STA不是native Owner。

## 3. 公开绑定、配置与单位

### 3.1 当前端口直接复用

Motion namespace `Asun.Modules.MotionControl`，类型/字段唯一见其A.1～A.7。完整方法绑定：

| IMotionAdapter精确入口 | 固高行为 |
|---|---|
| ValueTask<MotionCapabilitySnapshot> OpenAsync(string controllerId, bool readOnly, TimeSpan deadline, CancellationToken ct) | 指定身份只连接/读，零复位/使能/Home/改输出 |
| ValueTask<MotionCapabilitySnapshot> ReadCapabilitiesAsync(TimeSpan deadline, CancellationToken ct) | 更新未来准入，不覆盖历史 |
| ValueTask<AdapterFeedback> ReadStatusAsync(StatusRequest request, CancellationToken ct) | RawAxisSample，不造StateVersion/TargetVersion/settled |
| ValueTask<AdapterPathValidation> ValidatePathAsync(AdapterPathQuery query, CancellationToken ct) | 完整包络/动力学无副作用预检，未知Unsupported零下发 |
| ValueTask<AdapterReceipt> SubmitAsync(AdapterCommand command, CancellationToken ct) | 原机器路径/Profile/OperationId/hash，不二次累计相对量 |
| ValueTask<AdapterReceipt> StopAsync(StopRequest request, CancellationToken ct) | 独立Stop，撤权后仍凭原StopIdentity收敛 |
| ValueTask<AdapterOperationLookup> QueryOperationAsync(AdapterOperationQuery query, CancellationToken ct) | 原身份/序列相关查询，NotFound不证明未执行 |
| ValueTask<AdapterDrainReceipt> DrainAsync(DrainRequest request, CancellationToken ct) / CloseAsync(CloseRequest request, CancellationToken ct) | 排空/资源分列，不关其它子租约 |
| IAsyncEnumerable<AdapterFeedback> ReadFeedbackAsync(AxisScope scope, CancellationToken ct) | 有界原反馈，无第二Core事件入口 |
| ValueTask<AdapterReceipt> CancelCompareAsync(AdapterCompareCancel command, CancellationToken ct)；ValueTask DisposeAsync() | 归还原登记，不代替停止确认 |

Signals唯一§7.1：AcquireAsync(AdapterAcquireRequest,CancellationToken)→ValueTask<AdapterLeaseResult>；lease Capabilities、ReadAsync、ExecuteAsync（含ISignalAuthorizationPort）、SubscribeAsync、QueryAsync（含HostStamp deadline）、ReleaseAsync精确沿上游，不公开厂商万能IO Execute。QueryOnly禁止Execute/Subscribe；Release返回原Task<Signals.DrainResult>，不换包装Task。两个域同名AdapterCommand/DrainRequest/ResourceState用namespace别名，不enum整数强转。

### 3.2 单位与配置版本

完整构造/算法见附录A。AxisId/地址分别唯一、Ordinal；只核card/core非负、axis正、重复/预算。目标上限、mask位宽/起始位由Native Profile核，不猜32轴可用。

上游mm/degree、velocity unit/s、acceleration unit/s²、jerk unit/s³沿用。S=正有理PulsesNumerator/UnitsDenominator，sign=±1，OriginPulse为逻辑零对应raw偏置，不是清零命令。p=origin+sign×x×S，最近偶数取pulse，核raw范围/批准量化误差；不截断、回绕、clamp。double原IEEE754精确有理展开+BigInteger，不能先把Int64 origin转double。误差预算来自批准Profile，无生产默认。

NativeTimeBase显式Second/Millisecond，后者速度/加速度/jerk除1000/1000000/1000000000。旧GetEncVel pulse/ms不能推广全部Home/插补API，逐函数保留单位证据。反馈逆换算；缺值null/Unavailable不补0；finite/精度不足拒绝，checked不保证浮点安全。

配置revision/native回读revision/capability hash/Boot/Generation/ScaleRevision/reference分别保留。scale/方向/原点/映射变化失效预检/compare/解释，关新写并排空，冻结新revision后回读，不运动中替换/重解释历史pulse。普通配置仅SoftMin/SoftMax/DefaultVelocity/DefaultAcceleration逐项回读；Home电平/卡配置/零位另行批准维护Profile。

配置持久化在宿主Owner，Core不建文件库。新JSON严格schema/字段/单位、UTF-8/InvariantCulture，重复/未知拒绝后同一Validate；旧HomeMode/HomeMoveDir/HomeIndexDir/HomeEdge/HomeTriggerIndex/HomeVelHigh/HomeVelLow/HomeAcc/HomeDec/HomeOffset/SearchHomeDistance只离线显式迁移，原hash/逐字段来源/未定值/复核保留既有提交记录，不运行时混新旧。宿主原子替换保旧revision；文件保存不表示设备应用。

### 3.3 指纹与能力证据

离线DLL路径/hash/PE x64/导出与目标ABI→Owner只读Open→身份/固件/地址/时钟→能力/config一致→授权/lease/耐久ledger/独立Stop→写开放。离线不OpenCard、不在主进程执行未知DLL初始化。BootId来自可信设备boot；无API时Profile只能声明connection-scoped synthetic epoch及设备重启不可观测，不UUID/时间伪装真实boot或DevicePersistent查询。Generation为Owner连接代，进程epoch不复用；固件变更不等于复位，身份不足禁止硬件写不挡C1/C2。

能力区分声明/export、只读观测、HIL资格、Unknown/Unsupported。export不证明支持；Snapshot只批准单位/范围/特性/分辨率/stop能力，原码/地址留诊断。反馈不重算capability hash。SupportsIndependentStop必须真实不受阻塞SDK队列影响，预留优先队列不够，当前未证明，硬件写Open关闭。

## 4. typed Native与worker

### 4.1 逐函数证据卡

下表是观察路线，不是P/Invoke声明。每函数实现前在此补目标DLL hash/头文件版本页码、export/calling convention、参数序号/C宽度符号、packing/sizeof/offset、编码、数组count/容量/入出、单位/范围、返回码/副作用/timeout/abort/线程域；齐全才typed LibraryImport/函数指针。禁止万能Move/Execute/object/IntPtr管线；句柄/结构/地址仅Native，C long不默认C# long。

| 能力/已观察符号 | 正常路线与拒绝 |
|---|---|
| Open/Close、GetCardNo/GetCore、GetVersion(Ex)、GetClock/高精度 | 指定身份只读，字符串指针/长度/所有权按头文件，不out string照抄 |
| GetSts/GetLimitStatus/GetPrfPos/GetEncPos/GetEncVel | 各原码/时标/序号；实时limit与锁存分开，不清锁存伪造未触发；顺序读取不冒充原子snapshot |
| AxisOn/Off/ClrSts/ZeroPos、StepConfig、Home/Limit/Alarm | 逐项预检/写/回读，AxisOff不当Stop、ClrSts不当故障消失；零位变reference |
| GetHomePrm/GoHome/GetHomeStatus、StandardHome候选 | 有限搜索/Profile/电平，latch/index/reference不齐不Homed |
| PrfTrap/SetTrapPrm/SetPos/SetVel/Update；PrfJog/SetJogPrm/SetVel/Update | 参数失败零Update，Update未知保持可能动作，顺序非原子 |
| Stop(core,mask,option) | core分组/checked mask，controlled/immediate按目标手册，旧软件EStop非STO |
| CrdClear/SetCrdPrm/CrdSpace/LnXY/XYZ/…/CrdStart/Status(Ex) | 全轴组/FIFO/路径预检，部分装载不Start/不假rollback，清除确认前持FIFO |
| PosComparePulse/Start/Stop/Clear/Status/Data/Data2D/Linear/Map/Space | 装载/激活/耗尽/撤销分开，绑定登记/输出租约/revision，数组通道能力另核 |
| SetCaptureMode/GetCaptureStatus/ClearCaptureStatus/GetCaptureRepeatPos | 相关source/时钟事实，Clear副作用不能藏读路径 |
| GetDi/Do/DiEx/DoEx/DiBit、SetDo/DoEx/DoBit | 仅Signals，out scalar+count>1禁止，typed足量buffer/逐位码极性，末码不代表整批 |
| PT/PVT/gear/cam、弧线/多维/扩展IO | 无批准上游语义/资格则Unsupported，不扩产品范围 |

### 4.2 原任务、deadline与退出

默认独立x64 worker；仅该函数官方timeout/abort与HIL返回上界齐后允许同进程，不扩大全部SDK。IPC条数/长度有界，协议版/Owner epoch/generation/OperationId/hash/方法/剩余单调期限/sequence完整关联；先登记原task再send，迟到仅原操作对账不改新缓存/发第二终态；阻塞读占槽不无限重建。

到期关新写/调度→尝试已证明可达独立Stop有限观察→Unknown隔离→尝试Kill/有限等待退出。卡死worker同队列Stop不可达，明确Stop未确认并通知可信宿主/独立安全链，不假另线程/进程SDK安全并发。Kill成功不等于退出；OS/权限错误/未确认强持Process/IPC/task/额度、ReleaseUnknown，不无限Kill/替代worker写。退出且callback/consumer结束仅OS Released，运动/IO仍可能持续。Thread.Abort、GC、窗口关闭、WaitAsync均非回收证据。

重连仅批准只读对账，禁自动write/Reset/清状态/重发；SDK Open不可拆只读不能用它对账。新generation与原boot分别保留，完整轴/limit/encoder/servo/命令序列/输出核原记录；NotFound/无历史/Boot不符不证明零动作。恢复归原Motion/Signals Owner和安全链，worker退出不解除隔离。

## 5. 能力处理与预期失败

### 5.1 配置/Servo/Reset/Home

普通写核原Scope/lease/fence/授权/boot/generation/capability/config/scale/reference/deadline；实际SDK send前共享Owner再核本地gate，防准备期撤权/换代。先全部参数转换再写，四项普通配置逐字段Requested/ReadBack/Outcome，部分应用保已写、关动作，不假原子rollback。

Servo显式Enable/maintenance policy、ACK仅Accepted后回读；失能可能失保持力不替代Stop。Reset/ClrSts明确批准范围，不错误重试暗复位。Home冻结HomeAxisPolicy/Profile/搜索包络/方向/mode/switch/index/offset→GoHome→有限反馈，reference/latch不可观测Unknown/Unsupported；limit/Home丢失/取消/断线按原Stop，反向恢复由新批准请求，不无限反向重试。

### 5.2 Abs/Relative/Jog/轨迹/Compare

Abs用原ResolvedMachinePath和pulse转换；Relative上游已用原PositionVersion解析目标，不EncPos截断再加delta/换基准续跑。IndependentSerial部分失败已发/未发/Unknown分别；AtomicGroup无资格整请求零下发，不分轴伪原子。

Jog最大时长/heartbeat/envelope上游管理，不隐无限Jog。失心跳/lease关新写原Stop，未归还不接受反向新Jog，UI松键不直调Native。

ValidatePath核QuerySha256/原Start/全包络动力学含段间jerk，端点通过不足；无原生预检/资格模型Unknown/Unsupported零下发，不临时引规划器。FIFO预留→参数/逐段确认→Start，部分失败不Start，保FIFO停止/清除对账，未确认持资源不重装。

Compare绑定Axis/Points/Direction/Hysteresis/OutputChannelRef/registration/clock epoch，装载/激活/耗尽/撤销独立事实；电平/宽度归Signals/采集。超容量/单位/点方向冲突预拒绝，ACK未知不新ID盲装。Capture需相关source/time/sequence/clear Owner，不新增质量/扫描判定。

### 5.3 反馈/实际停止/查询

仅RawAxisSample原command/encoder/velocity/error、servo/Homed/INP/limit/fault/hold/stop-lock/switch/index/clock/reference/quality。缺失null/Unknown，失败/重复/倒序不刷新年龄；顺序读取各时标，wrap/reset按证据，不UTC冒充同步。

ACK=Accepted；Stop Requested/Accepted/PhysicallyStopped/ControllerLockReleased/NativeDrained分别Truth。实际停止由IM-010 MotionStopPolicy连续窗口判，Adapter供Witnesses/原码/sequence；单帧velocity=0/INP/AxisOff/Kill/Close不升级，不与settled目标判据混用。

Query核原controller/boot/generation/OperationId/hash/sequence，无相关查询Unsupported/Unknown；当前停着/IO等目标不证原完成，Signals ACK不Applied。只有限重查原身份，不重发普通write。

## 6. 状态、lease、取消/排空

沿Motion ExecutionState/DrainState/ResourceState/DeviceReconciliationState/StopEvidence；Signals独立CommandOutcome/ResourceState，不integer强转/第二状态机。

| 事实 | 结果/Owner保留 | 恢复 |
|---|---|---|
| 发送前拒绝 | DeviceCallMade=false，Rejected/NotSent无作用 | 修草稿新请求，原键不改内容 |
| ACK已收实际未齐 | Accepted，不停/完成/排空推断 | 原ID查询/Stop，不放行 |
| 已call SDK应答丢失 | Unknown/PossiblePhysicalEffect，原task/额度 | 隔离查询/收敛/人工对账 |
| 已实际停止native仍跑 | PhysicallyStopped=True，DrainUnknown/Held | 继续收敛不提前终态/归句柄 |
| worker退出device未对账 | OS Released，Execution Unknown/Reconciliation Pending/Quarantined | 保原身份/查询入口，只读对账 |
| 调用/callback/queue/lease排空 | Drained/相应Released | 上游按动作事实判终态，排空非安全/质量 |

幂等/canonical/hash/授权域/OperationId沿Motion A.5，Adapter只bounded关联不第二耐久ledger。同ID同内容原task/回执，异内容Conflict，跨代不续动作；Signals发送前§7.1授权/原子幂等，不底层盲重试。

ct仅结束等待/表达收敛，不能撤销物理作用。task先登记后Open/Acquire/Subscribe/Close，包装超时不转Owner。late产物不发布写通道立即收敛，错误有非空产物也归还；旧回执只原事实追加不改新binding/epoch、不删Unknown。

Close同步关准入→原Stop/CompareCancel（readonly不停止其它writer）→producer退出→native/callback/consumer退出→子lease归还→最后physical Close。Motion Drain/Signals Release不互替；独立CleanupBudget观察不用取消业务token，未排空MotionLifecycleOwner/SignalRootRegistry/physical Owner强持原对象/task，返回/抛对应错误。确认路径释放，未确认隔离强持，不能“所有路径立即释放”。

## 7. 错误/线程/队列/诊断

Core错误A.1，Native用上游MotionFailure/SignalError稳定key/参数/原码/OperationId/可能作用，不新增上游enum；原码按目标版本表，未分类Unknown/warning不success。

| 故障 | Owner与允许恢复 |
|---|---|
| 参数/unit/scale/地址/hash | 配置Owner，修草稿校验零设备重试 |
| ABI/version/bitness/export | NativeOwner保指纹，写关闭选批准Profile，不自动下载降版 |
| stale/gap/epoch | 原样本Owner，上游降质量，查询原操作，不last-good标实时 |
| send/stop未知 | 原Owner+安全链，停止待确认/原ID查询，不新动作 |
| OS回收未知 | 原Process/IPC/task强持，隔离有限观察禁替代worker |
| 部分config/FIFO未清 | 保逐项已写/未写/未知与登记，对账撤销不盲重试 |

原queue bounded/条数logical bytes双计，callback TryWrite失败独立atomic gap/overflow标记并关相关普通准入，不能靠满queue送gap。不可重建回执/故障/lease/Stop先保原Owner/ledger再投影，容量耗尽fail closed；UI另latest合并不覆盖原反馈，事件sequence/EventId沿上游。

诊断含device/ABI/config/scale/hash/boot/代/原码/方法/有限摘要/时标/水位/stop-drain两轴与Source Simulation/Replay/Hardware；脱秘密/凭据，保留/导出归宿主既有sink，不增库。日志失败不改设备事实。

## 8. 可选WPF工作台与双STA

### 8.1 公开控件/角色流

WPF namespace `Asun.Modules.GoogolMotionAdapter.Wpf`，以下为规格声明，未创建程序集：

```csharp
public sealed record GoogolViewBinding(
    Asun.Modules.MotionControl.Wpf.MotionViewBinding Motion,
    GoogolConfiguration Configuration, GoogolCoreLimits Limits,
    IGoogolDiagnosticReader? Diagnostics = null);
public sealed class GoogolDiagnosticsView : System.Windows.Controls.UserControl
{
    public GoogolDiagnosticsView();
    public void Attach(GoogolViewBinding binding);
    public void SetCulture(System.Globalization.CultureInfo culture);
    public GoogolConfiguration GetDraft();
    public ValueTask<Asun.Modules.MotionControl.DrainResult> DetachAsync(
        TimeSpan budget, CancellationToken ct);
}
```

组合上游MotionControlView，借用MotionViewBinding的Session/owner/scope/Profile/请求生成器/LifecycleOwner；仅增加vendor config/scale/ABI证据与离线草稿校验。不初始化Open/ledger/隐藏窗口/线程；Attach不移交physical Owner，Detach不Close别人。config与actual capability ControllerId/轴/Frame/unit/revision一致，否则显示差异、禁动作，不造能力。GetDraft返回本view不可变副本，不写设备/文件；无binding时InvalidOperationException，重复Attach或未完成Detach拒绝。

观察者选轴→actual/target/velocity/quality/age→关联原回执→查询；定位/维护沿上游Preview/授权/确认/Move/Home/Jog/Servo/四项配置/Stop。mapping/scale/native Home草稿仅校验/GetDraft交宿主离线评审，无隐式“应用到设备”；普通Motion草稿应用/撤销仍逐字段回读，不混两种配置Owner。

### 8.2 构图/联动/恢复

唯一1920×1080屏幕viewport，扣实际taskbar/title/border/status，以剩余客户区布局，不客户区=整屏、不改显示设置。顶48 DIP设备/原身份/readonly；底28 DIP年龄/gap/drain；中间左18%轴/映射、中央54%actual/曲线/原operation、右28%动作/草稿，下诊断初始中间高26%。轴/Stop/Unknown/恢复常显；Jog期间禁拖动藏Stop。

| 区域/匹配控件 | 数据/联动 |
|---|---|
| DockLayoutManager+LayoutGroup/LayoutPanel | 紧凑分区/分割/恢复默认；布局操作零动作，仅本宿主可信布局xml，不反序列化任意来源 |
| GridControl+TableView.ShowAutoFilterRow | actual优先、身份/unit固定、target/velocity/limit/age/status；筛选不改Scope，虚拟化有界历史，不每反馈自动重排 |
| PropertyGridControl.SelectedObject | 白名单草稿副本，unit/range/source/revision；原pulse/量化误差联动，编辑零动作 |
| ChartControl+XYDiagram2D+LineSeries2D | actual/target与velocity分图，同device轴；不同unit不混轴，事件定位原样本/gap断线，显示抽稀保min/max不改stop/settled原证据 |
| SuperTip.Items+SuperTipHeaderItem/SuperTipItem、DevExpress.Xpf.Editors.Flyout.FlyoutControl（继承FlyoutBase.PlacementTarget） | 原因/限制/下一步，Flyout仅字段/版本差异；Stop/恢复不藏弹层 |

Actual20 DIP/数字16/正文14、8/12/16间距，局部宿主theme不改全局App。蓝运行/琥珀需处理/红故障/灰未知都配文字，Ready不译安全。数值按MotionUiProfile.RenderPeriod批次Dispatcher，stop/fault/Unknown立即投影；图表暂停不暂停设备或藏新故障。

Jog松键/捕获丢失/失焦/卸载/撤权/断连均原身份Stop；正负同时按立即停不queue，键重复不建多Jog。Tab轴→参数→预览→动作→Stop→回执→诊断；Enter编辑仅草稿，Esc/Alt+S停本控件原Scope，Stop无二次确认。UIA names本地化，英文/繁体按钮适应长度不截关键命令；恢复区列原OperationId/最后可信年龄/未确认阶段/下一步，查询/Stop/清故障/Home/对账分开，无“继续移动”绕未知。

### 8.3 三语、两个Dispatcher与Detach

宿主SetCulture动态zh-CN/zh-TW/en-US并可扩展，模块无重复语言入口；标题/字段/状态/error/tip/恢复全资源，原码不翻译不改hash。

| key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title | 固高运动诊断 | 固高運動診斷 | Googol motion diagnostics |
| Actual | 实际位置 | 實際位置 | Actual position |
| Draft | 参数草稿 | 參數草稿 | Parameter draft |
| Stop | 停止 | 停止 | Stop |
| StopUnknown | 停止待确认 | 停止待確認 | Stop unconfirmed |
| Stale | 反馈已过期 | 回饋已過期 | Feedback stale |
| Query | 查询原操作 | 查詢原操作 | Query original operation |
| DrainUnknown | 排空待确认 | 排空待確認 | Drain unconfirmed |
| ScaleInvalid | 换算参数无效，请检查单位和版本。 | 換算參數無效，請檢查單位與版本。 | Invalid scale. Check units and revision. |

未知key三语兜底分别“操作失败：{code}。查询原操作。”、“操作失敗：{code}。查詢原操作。”、“Operation failed: {code}. Query the original operation.”，不堆栈/“智能恢复”。

每view固定创建STA/Dispatcher。双STA各new控件/草稿/chart/resource dictionary/Brush/Binding，不共享DependencyObject/ViewModel/DispatcherTimer，不同步跨Dispatcher Invoke；共享仅线程安全不可变DTO/公开session，订阅各有界。两个只读view可借同session，写仅一个批准owner；独立Session接同physical Owner的writer/readonly子端口，不第二物理Open。一viewDetach/语言不关另一view/Signals。

Attach增加BindingGeneration，全部生成/事件/Dispatcher完成核代，旧授权生成器迟到不Submit。Detach同步禁普通写、取消草稿→委托上游原Stop/CompareCancel/Drain→本订阅/Dispatcher退出→确认后解除binding；ct仅取消本等待，原cleanup沿budget持续强持。未归还禁重新Attach，由LifecycleOwner保原session/操作映射，窗口销毁非释放。

### 8.4 本机官方API证据

定向读 `C:/Program Files/DevExpress 25.2/Components/Bin/NetCore/` 官方XML，Core DLL FileVersion=25.2.3.0；只定控件组合，未编译/实窗：

| XML | SHA-256 | 核验API |
|---|---|---|
| DevExpress.Xpf.Core.v25.2.xml | `cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196` | SuperTip.Items/FlyoutBase.PlacementTarget |
| DevExpress.Xpf.Grid.v25.2.xml | `7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd` | GridControl/TableView.ShowAutoFilterRow |
| DevExpress.Xpf.Docking.v25.2.xml | `b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f` | DockLayoutManager/LayoutPanel/SaveLayoutToXml(string)/RestoreLayoutFromXml(string) |
| DevExpress.Xpf.PropertyGrid.v25.2.xml | `0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9` | PropertyGridControl.SelectedObject |
| DevExpress.Xpf.Charts.v25.2.xml | `2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0` | ChartControl/XYDiagram2D/LineSeries2D |

新增属性再查匹配XML/dxdocs，不猜API/改版本；真实WPF/双STA/UIA后续W1门。

## 9. 两个无UI宿主与完整装配

### 9.1 离线扫描规划消费者

以下是实现后可编译的规格示例，未build/run；只Core+Motion Core/BCL：

```csharp
using System.Collections.Immutable;
using Asun.Modules.MotionControl;
using Asun.Modules.GoogolMotionAdapter;

var axis = new AxisId("X");
var scale = new GoogolAxisScale(1000, 1, 1, 0, "scale-1");
var binding = new GoogolAxisBinding(axis, new CoordinateFrameId("machine"),
    MotionUnit.Millimeter, new GoogolAxisAddress(0, 0, 1), scale);
var config = new GoogolConfiguration("googol-config-v0.2", "controller-1", "cfg-1",
    ImmutableArray.Create(binding));
var limits = new GoogolCoreLimits(8, 16384);
var validation = GoogolModule.ValidateConfiguration(config, limits);
if (!validation.IsValid) throw new InvalidOperationException(validation.Errors[0].Code.ToString());
var digest = GoogolModule.ConfigurationSha256(config, limits);
var converted = GoogolModule.EncodePosition(binding,
    new MotionValue(1.25, MotionUnit.Millimeter),
    new GoogolPulseLimits(-1000000, 1000000,
        new MotionValue(0.0005, MotionUnit.Millimeter))); // 合成预算，非生产默认
if (!converted.IsValid || converted.Pulse != 1250)
    throw new InvalidOperationException("Conversion rejected");
// 仅候选换算，不发送设备、不宣称实际位置/安全/全路径通过。
```

### 9.2 独立回放/维护消费者

不另做产品Shell/DB/隐藏Window。public factory接上游完整ReplayPlan与显式时钟，字段构造在Motion A.7/A.5 fixture；沿§9.1的using，并使用BCL System/Threading/Tasks（工程ImplicitUsings=enable）。下列方法放消费者静态Host类，不增加发布API；参数都可通过公开构造取得：

```csharp
public static async Task<AdapterFeedback> ReadReplayAsync(
    GoogolConfiguration config, GoogolCoreLimits limits,
    ReplayPlan plan, MotionVirtualTimeProvider time,
    StatusRequest status, TimeSpan budget, CancellationToken ct)
{
    var adapter = GoogolModule.CreateReplay(config, limits, plan, time);
    try
    {
        var caps = await adapter.OpenAsync(config.ControllerId, true, budget, ct);
        if (caps.Identity.Source != SourceKind.Replay)
            throw new InvalidOperationException("Wrong source");
        return await adapter.ReadStatusAsync(status, ct);
    }
    finally
    {
        await adapter.DisposeAsync();
    }
}
```

本小例仅A.5固定Replay零订阅/无pending故障task，budget正有限且status.Deadline不大于budget，Replay Open/Read本路径同步完成，构造/读取无native；返回前Dispose已确认无模拟资源。ct预取消拒绝零动作，不是实机超时模板。完整Simulator/维护Host次序：进程先保LifecycleOwner/physical Owner容量→config/limits/plan/time→CreateSimulator或未打开Native Adapter→MotionDependencies全部显式端口（ledger、coordinates、clock mappings、authorization、interlocks、controller leases、diagnostics、lifecycle owner、time）→MotionSession→登记原task→Open→command/feedback/query→原Stop/CompareCancel→Drain/Close→确认Released再释放槽。所有外部task按剩余budget有限观察，late/超时仍占槽，finally不仅Dispose假释放。

本测试工程Hosts/TestPorts.cs实现Motion A.4全部借用接口，不引用上游私有测试。固定授权仅认合成owner/scope/intent；共享lease协调器拒第二writer、允受限reader；有界lifecycle强持原Session/task。Simulator返回上游SimulatorAdapter/ReleaseFault，Replay返回ReplayAdapter、禁物理写；无需厂商DTO/默认singleton。两个消费者独立可构造/验证，真实共享卡与HIL另门。

## 10. 合成Golden与两个有限自审视角

### 10.1 固定换算反例

均合成，不作客户公差；构造于唯一测试工程，不增manifest/报告：

| ID | 输入 | 唯一断言 |
|---|---|---|
| G01 | S=1000/1、sign=+1、origin=0、mm=1.25 | pulse=1250/Error=0；Decode1250=1.25 |
| G02 | S=1/1、origin=0、x=2.5/3.5/-2.5/-3.5、误差预算=0.5 | pulse=2/4/-2/-4，最近偶数，不截断 |
| G03 | S=1000、sign=-1、origin=100、x=1.25 | pulse=-1150，逆1.25，Error=0 |
| G04 | S=1000，velocity2 unit/s、acceleration3 unit/s²，Millisecond | raw2 pulse/ms、0.003 pulse/ms²；逆2/3 |
| G05 | G02预算=0.49；或超raw范围/Int64 | QuantizationExceeded/Overflow，Pulse=null，零device |
| G06 | origin=9007199254740993、x=0、允许raw该值 | pulse精确原origin，禁止先转double；native整数转double不无损时不调用double解码伪造 |
| G07 | 空/重复axes/地址、空revision、unit不符、NaN/Infinity、ratio0/sign0 | 确定field错误，无默认/工厂产物/native |
| G08 | 同config反转axes顺序；改ratio/revision/地址 | 顺序hash不变；实字段变化hash变，schema未知拒绝 |

### 10.2 实现者/外部消费者

| ID/视角 | 触发与可判断言 |
|---|---|
| I01 实现者正常链 | config→校验/转换→factory→Open/Read/Submit脚本→原回执→Stop/Drain/Close；错误零call、无反馈ACK不升Completed |
| I02 证据弱/缺失 | 丢样/重复倒序/nonfinite/clock回退/limit锁存矛盾降质量、不续freshness/不造stop；影像遮挡/弱纹理非模块输入，反馈缺失适用 |
| I03 完整能力 | Home无reference/FIFO部分接受/Compare未撤/IO应答丢失→Unsupported/Unknown，不Start/假完成；不以首片替全能力完善 |
| I04 deadline/late | HoldNative到期原task/额度Held；同queue Stop不可达不标已停；ReleaseFault后原回执对账不改新代 |
| I05 OS/device | Kill/exit成功而device未知→OS Released+Motion Unknown/Quarantined；Kill/exit失败保Owner/ReleaseUnknown，零替代write worker |
| E01 空宿主 | 两独立Exe只public构造，无UI/SDK/DB；缺time/limits/plan/config同步拒绝，不私有fixture |
| E02 并发/lease | 两writer同controller仅一成功；reader Close不Stop writer；Signals Release不关Motion；fence过期零写 |
| E03 cancel/close | Open/Acquire/Subscribe finally后迟到产物原根接管排空；budget到期原Task/槽留；未Released禁重Attach |
| E04 幂等/query | 同ID同内容原task、不同Conflict，Relative不二次加量/pulse不重发；NotFound/现值等目标不证完成 |
| E05 双STA | 各view/brush/字典/dispatcher，写权限冲突、失焦Jog/绑定代/一viewDetach/三语；无跨线程对象/互关 |
| E06 预算/回退 | axes/bytes/task/订阅/FIFO超cap预拒绝；旧schema/hash原reader，不能新进程复活动作/重算历史身份 |

模拟计划hash/调用匹配/故障/闩锁/时间规则复用Motion A.7，不复制动态模型。Native后续typed sizeof/packing/数组red-zone/多卡序列/副作用计数；两视角从输入走到恢复/Owner，不用编译失败替契约设计。

## 11. 验证执行与现场门

C1/C2沿 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门) 的net10.0 BCL Exe/固定时钟/可控闩锁，不新测试包；具体build/run见binding。G01～G08/I01～I04/E01～E04/E06按切片全部执行，失败/未完成/必需skip非零。C1同步纯函数，cancel/drain/native不适用；C2有原task/late/close适用。

合成harness预算：axes8/config16384 logical bytes，在途16/queued32/readers8/subscribers4/events256，case墙钟10s、suite120s、外层process150s，均防挂测试值非生产默认/目标。虚拟时间每段await屏障后推进不真实sleep拼顺序；期望Held的故障case仍明确监督/释放/剩余量，不能未完成返回PASS。外层杀测试进程是失败，不物理Stop。

W1真实固定viewport双STA/三语/键盘/UIA/曲线gap/Detach迟到另验。Native官方ABI/IPC/不可达Stop/exit失败另验。HIL指定卡/固件/SDK/hash，量具核方向/unit/limit/Home电平；全范围Abs/Relative/Jog/Home/FIFO/Compare、controlled/immediate Stop与硬件急停；断电/断网/reboot/输出保持/原身份对账，两个真实消费者长稳/资源增长。公差/停止时间/settled/频率/脉宽/长稳时长由批准Profile/现场合同，不猜；模拟/截图/单测不现场资格。

## 12. Benchmark/发布/迁移/回退

分位/失败口径唯一沿DEV-GOV-010 §3.1，不复制算法。BenchmarkProfile冻结ProfileId/revision/source/hash、ModuleAPI/Motion/Signals/SDK/firmware/config/scale/version/hash、SourceKind、轴数/ratio/边界/config bytes、反馈率/丢样/FIFO/Compare规模、调用/订阅并发/queue cap、冷/热/预热/样本计划/最低有效n、deadline/cleanup、失败/删失/Unknown、logical bytes/allocated bytes/峰值working set/handles/native worker/task/lease/subscriber cap、时延/资源目标及来源。

C1测校验/hash/位置/速率开始至结果，无虚构drain；C2factory/Open/read/原task/最后订阅/Close，虚拟delay与真实CPU分开；Native IPC→function→ACK→相关feedback，cancel→实际Stop/native drain/OS Released/device对账分别计；W1render/Dispatcher lag/Detach/cache独立。端到端原接纳至真正resources released，Unknown/未释放不性能PASS；失败/timeout/删失资源全列不只挑成功。客户阈值未有=方法冻结/TargetPending/NotEvaluated，8小时/合成预算不是交付指标。

C1/C2一个Core DLL，net10.0/x64，公开引用Motion Core/Simulator不SDK/UI/产品；W1另包引用本Core/Motion Wpf/本机DevExpress；Native另包实现两typed ports，不提前拆未稳定Contracts/gateway/store。发布记录复用现有消费者，固定代码快照/包hash/API/Profile/schema/SDK/firmware/实际验证范围与回读；当前不造包/清单。

升级/回退：离线双消费者→Shadow只读→旧关接纳→原Owner排空/核Unknown/全部Compare/Signals pulse结束→保旧包/config/ledger reader→独占切换→新代/能力/授权→显式write。新旧不同时写，不自动降版运动会话，不软件重启当设备复位。Unknown原Owner/task/query保留，旧格式原reader/hash，不能改身份续跑。旧.NET8/WinForms项目保客户验收/config/data/可回退，不因本文迁移。

## 13. 六项定位与剩余切片门

2026-10-11主控接收0.2.0-prep的C1配置换算/hash、C2公开Simulator/Replay工厂六项文档规格为 `ModuleCoreImplementationReady`，并独立按字段重建126 bytes配置/hash一致；0.2.1仅同步该历史接收。本版复用已接收规格，不重审C1/C2，完成全范围实际缺口的本原会话自审，见§15～17。W1指定投影原限定接收保持，新UI根/证据与N1托管接线内部设计已闭合；真实WPF/Native/产品仍 `PreparationIncomplete / NotReady`，不代表build/run/生产通过，不等待总控内容复核。

| 切片 | ①边界/消费者 | ②API/单位/Owner | ③空宿主 | ④反例 | ⑤Benchmark | ⑥落点/顺序 | 状态/剩余门 |
|---|---|---|---|---|---|---|---|
| C1配置/换算/hash | §1～3/9.1 | A.1～A.3 | §9.1 | §10.1/E06 | §12 | §14/9.1 | `ModuleCoreImplementationReady`，六项规格已接收；不依赖SDK/HIL/WPF，后续获派实现时绑定权威快照 |
| C2脚本工厂/契约/双消费者 | §1～2/9 | §3/6/A.4～A.5 | §9.2/Motion A.4/A.7 | §10.2/11 | §12 | §14/9.2 | `ModuleCoreImplementationReady`，六项规格已接收；公开Motion程序集实现绑定后执行build/run，不要求安装SDK，不模拟物理资格 |
| W1诊断/双STA | §8.1/16 | §8/16 | §9/16.3 | E05/§11/17.2 | §12/17.2 | §14/16.3 | 全范围内部软件规格闭合；`PreparationIncomplete / NotReady`，真实WPF/1920×1080/双STA/UIA及受影响产品资格未执行 |
| N1 Native共享Owner | §2～5/15 | §3～7/15 | §15.2 typed后端/17.2 | I03～I05/§11/17.2 | §12/17.2 | §14/15.2～15.3 | 托管接线/Profile codec/Owner软件设计闭合；`PreparationIncomplete / NotReady`，ABI/硬件/独立Stop/只读Open/boot-query/时间单位/路径资格/Signals通道事实门，不阻Core |

外部门仅相关切片：目标SDK库/hash/头文件/CallingConvention/packing/数组/错误码、实际卡核轴/firmware/FIFO/Compare、boot/clock wrap/reset/掉电行为、可靠独立Stop、原operation查询、批准脉冲当量/Home/limit/INP/servo/electrical值、停止/定位/settled/频率/脉宽目标、安全/对账权限、真实消费者性能合同/HIL。表达这些值的类型存在不代表值获批；未证SupportsIndependentStop不true。不挡无关C1/C2，不再问常规技术选择。

## 14. Core implementation binding

- NewProjectRequired，namespace `Asun.Modules.GoogolMotionAdapter`。唯一码：`src/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Core/Asun.Modules.GoogolMotionAdapter.Core.csproj`；测试：`tests/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Core.Tests/Asun.Modules.GoogolMotionAdapter.Core.Tests.csproj`。C1/C2同工程，不第二Simulator/DTO/Contracts包。
- Core公开引用Motion Core，路径以上游binding为准，不其测试/私有实现；不SDK/WPF/DevExpress/AsunImage/产品Shell/DB。N1才公开引用Signals Core。
- W1唯一码/测试：`src/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Wpf/Asun.Modules.GoogolMotionAdapter.Wpf.csproj`、`tests/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Wpf.Tests/Asun.Modules.GoogolMotionAdapter.Wpf.Tests.csproj`。
- N1后续唯一码/测试：`src/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Native/Asun.Modules.GoogolMotionAdapter.Native.csproj`、`tests/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Native.Tests/Asun.Modules.GoogolMotionAdapter.Native.Tests.csproj`；当前不创建。
- 获准实现仅本模块上述src/tests；禁止其它模块/产品Shell/Domain/Integration/客户项目/config原件/参考快照/共享入口/AsunImage内部/依赖改版。本轮仅本文。
- 后续命令：`dotnet build src/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Core/Asun.Modules.GoogolMotionAdapter.Core.csproj -c Release`；`dotnet run --project tests/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Core.Tests/Asun.Modules.GoogolMotionAdapter.Core.Tests.csproj -c Release`。BCL Exe不dotnet test代替，当前工程未建、未执行。
- 拟定测试文件Golden/ConversionCases.cs、Contracts/FactoryCases.cs、Hosts/OfflinePlanner.cs、Hosts/ReplayMaintenance.cs、Hosts/TestPorts.cs，各有上文真实断言消费者，不提前建空文件。实现先确认权威仓库/分支或可审计快照，不猜无git目录HEAD。

## 15. N1 完整软件接线、设备Profile与原生边界

本节补齐此前仅有行为说明的可构造接线；属于既有固高厂商适配范围，不新增产品动作/通用Motion或Signals服务。N1的托管桥与后端注入可无SDK验证，具体GTS/Gg函数实现仍按项目暂缓边界。下述公开构造不是已存在的程序集；Core C1/C2类型、算法与126-byte hash均不改。

### 15.1 两种计数、轴参数与默认/推荐规则

§3.2/C1的GoogolAxisScale是**一份指定坐标的换算配置**，不能自动当命令脉冲、编码器计数、跟随误差三者的同一比例。Native每轴具名保存CommandPosition/EncoderPosition/FollowingError三个映射，以及CommandVelocity/EncoderVelocity/Acceleration/Jerk四个速率映射；后者可以明确Unsupported，不从前者推断。设备已经返回工程量时采用显式identity比例与官方来源，禁止再乘齿轮比。

Native所有部署类型在`Asun.Modules.GoogolMotionAdapter.Native`；表中每行是sealed record完整位置构造字段。下文M/S分别指`Asun.Modules.MotionControl`/`Asun.Modules.DeviceSignals`，仅文字别名，不新namespace。新增Profile只有硬件部署消费者，不进入C1 ConfigurationSha256或产品数据库。

| 类型 | 完整构造字段（按序） |
|---|---|
| GoogolCountMap | long NativeOrigin, double EngineeringOrigin, long CountsNumerator, long UnitsDenominator, int Sign, long NativeMin, long NativeMax, double MaxQuantizationError, double QualifiedFeedbackError, string Revision, string EvidenceReference |
| GoogolRateMap | long CountsNumerator, long UnitsDenominator, int Sign, NativeTimeBase TimeBase, string Revision, string EvidenceReference |
| GoogolAxisDeviceProfile | M.AxisId Axis, M.MotionUnit Unit, M.CoordinateFrameId Frame, GoogolCountMap CommandPosition, GoogolCountMap EncoderPosition, GoogolCountMap? FollowingError, GoogolRateMap CommandVelocity, GoogolRateMap EncoderVelocity, GoogolRateMap Acceleration, GoogolRateMap? Jerk, GoogolHomeBinding? Home, string ReferenceEvidence, bool ReportsPositionHold, bool UsesControllerStopLock |
| GoogolHomeBinding | string PolicyId, string PolicySha256, M.HomeMode Mode, M.Direction SearchDirection, M.NumericRange SearchEnvelope, bool SwitchActiveHigh, bool IndexActiveHigh, bool PositiveLimitActiveHigh, bool NegativeLimitActiveHigh, bool InPositionActiveHigh, M.MotionValue ReferenceOffset, string EvidenceReference |
| GoogolAbiFunctionEvidence | string FunctionName, string HeaderSha256, string HeaderLocation, string Prototype, string MarshallingEvidence, string UnitEvidence, string ReturnCodeEvidence, string ThreadingEvidence, string TimeoutEvidence, bool HasSideEffect |
| GoogolSignalBankProfile | string Bank, int LogicalCount, int NativeIndexBase, bool CanRead, bool CanWrite, bool HardwarePulse, TimeSpan? MinPulseWidth, TimeSpan? MaxPulseWidth, string MappingRevision, string EvidenceReference |
| GoogolNativeProfile | string ProfileId, string Revision, string ContentSha256, string ControllerId, string ConfigurationSha256, string SdkDllSha256, string SdkVersion, string DeviceModel, string FirmwareFingerprint, ImmutableArray<GoogolAxisDeviceProfile> Axes, ImmutableArray<GoogolAbiFunctionEvidence> Functions, string ReadOnlyOpenEvidence, string BootEvidence, string ClockEvidence, string IndependentStopEvidence, string PathValidationEvidence, ImmutableArray<GoogolSignalBankProfile> SignalBanks, string SignalsAddressEvidence |

CountsNumerator/UnitsDenominator均正Int64，表示counts/unit；Sign±1，两origin不同量纲；raw闭区间，工程origin/误差finite，MaxQuantizationError非负、QualifiedFeedbackError非负。每类映射revision/source必给，无源不提升支持；C1的configuration地址/轴/unit/frame与Profile精确对应。CommandPosition与C1 Scale须数学等价：比例/Sign一致，NativeOrigin-Sign×EngineeringOrigin×N/D精确等于C1 OriginPulse，不能截断；encoder不要求等于command。FollowingError差分映射两origin须0，缺signed误差则null。部署hash纳入所有map revision/SDK证据，M.RuntimeFingerprint含Profile hash令能力随之变化；设备Profile变更由配置Owner显式批准新ConfigurationRevision，不复用旧revision掩盖变更。Home的mode/方向/包络/electrical原值来自批准策略和设备证据，不以record默认值猜事实；不适用Home=null/对应feature Unsupported。

计数公式`raw=NativeOrigin+Sign×(q-EngineeringOrigin)×N/D`；反式`q=EngineeringOrigin+Sign×(raw-NativeOrigin)×D/N`。原binary64/整数经C1已定BigInteger有理helper，最近偶数舍入/范围/误差复核，不能Int64先相减溢出；命令回投影qn与**原用户q**都核完整软件限位/禁区/误差预算。RawAxisSample.ControllerCommand=实际qn，EncoderActual用EncoderPosition、FollowingError用独立差分映射（无origin），EncoderPositiveSign=编码器映射Sign，Core对已转换工程值不二次乘Sign。只提供误差绝对值的API不能伪造signed FollowingError；设备QualifiedFeedbackError加最终binary64表示误差的向上界用于消费者资格，缺此资格只读可显示Unknown，不据之完成运动。

Home完成后的DeviceReferenceRevision须来自设备基准写/回读证据；software Profile origin修改不伪造设备reference commit。INP/limit/home实时与锁存分别来源，开关极性一次转换；同线路S.Mapping Spec极性重复/矛盾拒绝。servo/fault/status mask、卡核/轴上限、控制器时钟counter width/frequency/wrap/reset、native stop option均来自目标官方资料，不写猜值。

没有生产速度/加速度/jerk、Home方式、电平、settled/Stop容差或lease/deadline默认；依赖能力与批准Profile的交集，缺项拒绝写。**没有自动整定/自动选Home/自动扩大容差/自动改速度/AI推荐能力**，架构只批准厂商适配；无需凭“自动参数”新增推荐API。确定量化值/原生速率、已有Profile范围和错误修正说明可作为只读提示，输入/hash变更即失效，不写回Profile。控制器配置工具若给推荐值，保留其来源为候选，由配置Owner显式批准，不Adapter自行试运动整定。图像/ROI/视觉参数与HALCON路线不适用。

ABI evidence是**声明元数据，不是通用可执行调用描述**；Prototype/MarshallingEvidence必须逐参数列C宽度/布局/array count/方向/字符串ownership等§4.1内容。未取得目标头文件的函数没有一个有效条目，对应功能Unknown/Unsupported；编码时按核实签名写具名typed方法，不按字符串反射invoke或动态object参数。Profile中HasSideEffect与方法白名单交叉核，连接/只读函数不得带隐式Reset/ClrSts。真正CallConvention/packing缺项是厂商事实门，不能靠另造IGoogolNativePort模糊掉。

### 15.2 共享Root、后端注入与公开装配

物理Root管理设备生命周期，与M.ControllerLease/S.SignalRoot分别配合，不授软件安全权。一个可信应用进程先创建注册表并长持，后端构造必须未Open、未启动worker/回调，登记成功才移交给Root。Backend是N1实现/故障测试的typed能力边界，参数与返回不含SDK句柄；真实Backend内部才持native资源并走§4函数表。

| 类型 | 精确构造字段 |
|---|---|
| GoogolBridgeLimits | int MaxDevices, int MaxMotionEndpoints, int MaxSignalLeases, int MaxPendingTasks, int MaxQueuedCalls, int MaxSubscriptions, int MaxEvidenceFacts, long MaxRetainedBytes, int MaxIpcFrameBytes, TimeSpan MaximumCallBudget, TimeSpan CleanupBudget |
| GoogolConnectionBinding | string RootId, GoogolConfiguration Configuration, GoogolCoreLimits CoreLimits, GoogolNativeProfile Profile, IGoogolConnectionBackend Backend |
| GoogolChildRequest | string RootId, string EndpointId, string ControllerId, string ConfigurationSha256, string ProfileSha256, string OwnerEpoch, long? ExpectedGeneration, bool ReadOnly, TimeSpan Deadline |
| GoogolBridgeFailure | string Code, string MessageKey, string FieldPath, bool PossiblePhysicalEffect, string? VendorCode |
| GoogolBackendOpenResult | GoogolDeviceEvidence? Evidence, GoogolBridgeFailure? Failure |
| GoogolMotionEndpointResult | M.IMotionAdapter? Endpoint, GoogolBridgeFailure? Failure |
| GoogolConnectionDrain | string RootId, GoogolConnectionState State, int PendingTasks, int ChildEndpoints, int SignalLeases, int Callbacks, M.ResourceState OsResources, ImmutableArray<string> UnresolvedOperationIds, GoogolBridgeFailure? Failure |

枚举GoogolConnectionState固定编号0起：Reserved, Opening, ReadOnly, Active, Closing, Quarantined, Closed。它仅描述适配连接Owner，绝不替换M.MotionState/操作终态。所有limits正有限；MaxIpcFrameBytes<=MaxRetainedBytes，MaximumCallBudget/CleanupBudget正有限，Cleanup独立不取业务已取消token。MaxDevices/MotionEndpoints/SignalLeases/PendingTasks/QueuedCalls/Subscriptions/RetainedBytes按Registry全部Root合计限制；MaxEvidenceFacts为单snapshot上限、MaxIpcFrameBytes为单frame上限，不能每Root自得一整份总额度。IDs按ASCII1～64/Ordinal，Profile hash按§15.4，RootId全进程唯一不可复用给新物理设备；Registry同时拒绝相同ControllerId第二Root，不能换RootId绕过。

```csharp
public interface IGoogolConnectionBackend
{
    TimeProvider Time { get; }
    string ProfileSha256 { get; }
    string OwnerEpoch { get; }
    GoogolBridgeLimits Limits { get; }
    ValueTask<GoogolBackendOpenResult> OpenReadOnlyAsync(
        GoogolChildRequest request, CancellationToken ct);
    ValueTask<GoogolMotionEndpointResult> CreateMotionEndpointAsync(
        GoogolChildRequest request, CancellationToken ct);
    ValueTask<Asun.Modules.DeviceSignals.AdapterLeaseResult> AcquireSignalsAsync(
        Asun.Modules.DeviceSignals.AdapterAcquireRequest request, CancellationToken ct);
    ValueTask<GoogolConnectionDrain> ClosePhysicalAsync(
        string rootId, TimeSpan observationBudget, CancellationToken ct);
}
public sealed class GoogolConnectionRegistry
{
    public GoogolConnectionRegistry(GoogolBridgeLimits limits, TimeProvider time);
    public GoogolConnectionOwner Register(GoogolConnectionBinding binding);
    public ImmutableArray<GoogolConnectionDrain> Snapshot();
    public bool ConfirmReleased(GoogolConnectionOwner owner, GoogolConnectionDrain result);
}
public sealed class GoogolConnectionOwner : IGoogolDiagnosticReader
{
    public Asun.Modules.MotionControl.IMotionAdapter CreateMotionAdapter(string endpointId);
    public GoogolMotionPorts CreateMotionPorts(string endpointId,
        Asun.Modules.MotionControl.IMotionAuthorizationPort authorization,
        Asun.Modules.MotionControl.IControllerLeasePort controllerLeases);
    public Asun.Modules.DeviceSignals.IDeviceSignalAdapter CreateSignalsAdapter(string ownerNamespace);
    public Task<GoogolConnectionDrain> CloseAsync(TimeSpan observationBudget);
    public GoogolDeviceEvidence GetEvidence();
    public GoogolDeviceEvidence ReadCurrent();
}
```

`GoogolMotionPorts`为Native sealed record，完整构造字段`M.IMotionAdapter Adapter, M.IMotionAuthorizationPort Authorization, M.IControllerLeasePort ControllerLeases`。CreateMotionAdapter(string)只提供只读子端口，write Open拒绝；需要写的消费者使用CreateMotionPorts，并将返回的三个端口一起注入同一个M.MotionDependencies，其余依赖仍由宿主提供。传入的原授权/lease端口借用，不Dispose；构造与预留零设备IO。CreateMotionPorts与CreateMotionAdapter共享endpointId唯一槽，不能给同endpoint同时建两工厂。后端返回的原typed adapter仍由facade持有，不绕过这层返回给产品。

两个转发端口逐方法原样委托原M端口，不签授权/自授lease、不额外Acquire：ControllerLeases保存原Acquire/Renew返回的ControllerLease与对应OwnerId/ControllerId/fencing token，原Release始终转发并撤该许可；Authorization保存原Prepare返回的AuthorizationCheck及原AuthorizationQuery（OwnerId/Kind/Scope/Reference/IntentSha256），IsCurrent仍调用原端口。先预留有界槽才调用原task，null/failure不成为许可；每endpoint至多一个当前controller lease、至多MaxPendingTasks个有效授权检查/在途准备，保存字节计Root总预算，满额返回原类型的ResourceLimit/null，不开第二请求。未供发送使用的已过期检查可撤，其在途原Task仍保；实际普通请求占槽后强持其匹配检查至收敛。

转发的ValueTask.AsTask仅一次，原Prepare/Acquire/Renew/Release任务也计Root在途/字节；Root关闭后迟到check不能开放发送门。迟到非空lease仍交原Session的已登记task/Owner收尾，不Root另抢Release；原Release失败/在途保持捕获身份和隔离。子adapter资源已归还但转发lease尚未归还时，ChildEndpoints仍计该逻辑子端点，Root不能提前PhysicalClose；Session原Close/lease归还顺序照上游执行，adapter.Close的设备排空回执不等待本Session尚未发起的lease Release而造成循环等待。

write Open要求该endpoint此前捕获原Session的写lease及Open用途的当前授权；Submit依据原Command.Context/Scope与M.MotionRequestCodec.IntentSha256重新关联原检查，不从厂商DTO猜权限。发送/permit之前在锁外调用原Authorization.IsCurrent/ControllerLeases.IsCurrent并核原检查单调到期，再于Root gate核捕获的check/lease仍为同实例版本、fencing token/owner/boot/generation/stop gate/请求期限；不在锁内回调端口。许可只指已核凭据，授权撤销不能由UI布尔值替代；无法取得对应凭据则未发送拒绝MOTION_AUTHORIZATION_INVALID或MOTION_CONTROLLER_BUSY。原Stop/Query/CompareCancel/Close走原停止身份与收敛路径，不要求仍有普通写授权。Motion上游未把ControllerLease放入AdapterCommand，因此必须由此公开转发接线取得原凭据，不能宣称只凭命令已复核lease。

GoogolConnectionOwner只由Register构造，不能new越过注册；Register同步校验config/Profile/budget/身份、Backend.ProfileSha256与Profile身份相等及Backend.Time与Registry.Time为同一注入实例、Backend.Limits与注册表限额逐字段相同、OwnerEpoch格式正确且在Root冻结，先占槽再交Backend所有权，失败不接管Backend、不工作。Backend.Time只读借用、不能在Close Dispose它。CreateMotionAdapter/CreateSignalsAdapter只是同步构造本Root子facade、预留有界逻辑endpoint，不触发Open/Acquire；重复endpointId/namespace拒绝ArgumentException、容量不足InvalidOperationException，零SDK动作。MaxSignalLeases同时约束预留工厂namespace数与实际lease数，无无限无资源工厂；Signals adapter无设备资源，lease只有Acquire成功/迟到时才出现，由S.Root记录。无用的未打开Motion facade Dispose直接撤其预留槽；Signals无Release工厂，Root Close撤所有工厂槽但不能因撤工厂认为已有lease归还。

真实后端公开 `sealed class GoogolWorkerBackend : IGoogolConnectionBackend` 唯一构造 `GoogolWorkerBackend(GoogolConfiguration configuration, GoogolCoreLimits coreLimits, GoogolNativeProfile profile, GoogolWorkerOptions options, GoogolBridgeLimits limits, TimeProvider time)`，getter/全部方法恰实现上述接口。`GoogolWorkerOptions` 为sealed record，构造字段 `string WorkerExecutablePath, string WorkerExecutableSha256, string SdkDllPath, string OwnerEpoch`；路径为宿主批准绝对文件、hash hex64、epoch为进程唯一ASCII1～64。构造仅有界校验冻结配置，零加载/文件IO/进程；首次BackendOpen才核两文件hash并启动批准x64 worker（后台无可见控制台），不搜索PATH、不下载、不打开配置窗口。子EndpointId只为逻辑token，不SDK句柄。§14 Native工程同时提供Worker命令行模式`--googol-worker`（net10.0 OutputType=Exe可引用），worker实际处理本节白名单协议，不另创产品Shell或独立猜测程序集。实际函数声明按§4.1事实卡，故构造可定义、硬件实现暂缓。测试注入IGoogolConnectionBackend假对象，不为构造测试启动真实SDK。

首次子Open/Acquire在Root记录原Task/参数/额度后，用Root内一次共享OpenReadOnlyAsync任务建立物理会话。后端物理Open只连接读、不改输出，ReadOnly描述准入无副作用，不能假定SDK具有通用readonly flag。并发请求加入同一Open任务各有剩余观察期限，不重开；首请求到期后Root仍强持原任务、隔离且只收尾，late成功不开放新写。成功后Backend CreateMotionEndpointAsync返回未打开的**逻辑**IMotionAdapter，子Open只核其role/代/能力，不再次SDK Open。ReadOnly=false仅分配写子通道，不能隐式AxisOn/配置；仍须M写lease/授权/耐久ledger/独立Stop全部门。

每motion facade固定EndpointId/role，Open第一次冻结readOnly，此后不同role拒绝而非升级原实例。每子endpoint实现M.A.4全部方法，反馈/路径/回执归原子实例；Backend与facade两个层使用同一typed API，不二次运动协调。不能让两facade共享一个有Open/Close私有状态的IMotionAdapter实例。子Close/Dispose只归本backend endpoint，不physical close、不停止其它writer；子Drain资源计数不能改S lease数。Root状态Reserved→Opening→ReadOnly（物理已读、无writer）→Active（存在批准write子通道，不代表运动），故障→Quarantined，Close→Closing，真实收尾→Closed。Quarantined/Closing禁新Open/Acquire/普通write，原query/stop/cancel/close仍可收敛；Closed不复活。

Signals Acquire前核Root当前同物理身份/profile及S.Mapping/Capability/Clock/lease access，Create工厂namespace须等于request.OwnerNamespace。Backend返回S.AdapterLeaseResult，任何非空lease包括错误/late由原S.Root/physical Root保留并归还，不丢产物。Acquire.QueryOnly不能Execute/Subscribe，其Normal也按用途授权；ReadOnly物理Owner状态只是未有任何普通写，不是“所有Normal租约都禁写”的错误推断。转换后的Motion反馈与S观察共用同native generation来源，不互篡质量。

后端task/value-task AsTask仅一次、保原Task；每调用前占MaxPendingTasks/bytes，容量不足时拒绝新调用，不遗弃原任务。普通调用排队有界且fair FIFO，Stop/撤Compare/Close采用预留收敛通道不借普通队列；预留仍不是可靠物理Stop证明。超期未send从队列移除标NotSent，已send未知关新普通写，未完成原任务与额度不归还。订阅MoveNext/Dispose、原回调与workerExit都计入Root与后端真实counter；纯snapshot不触发设备IO。

readOnly Open预算仍是请求总deadline，不首次物理Open后重新分配一轮；CreateEndpoint和其逻辑Open按剩余量执行。Root收尾无业务ct，Close在异常中也能观察；调用前所有Limit正有限且每阶段预算<=MaximumCallBudget，deadlineRemainingTicks按真正耗时递减，不每个pipe round-trip续期。可取消未启动任务移除时释放其槽/bytes，已发未知不释放。

预留资源算法：Register预留Root自身Open、worker生命周期监督、PhysicalClose三任务槽及Open/Close两控制消息槽；每个已创建Motion endpoint预留一个收敛task/一个控制消息槽，每个Signal工厂预留一个归还task/一个控制消息槽，未接纳普通调用不可借用；剩余MaxPendingTasks/MaxQueuedCalls用于普通操作。workerExit监督占自己的原Task槽至真实退出，不能与仍挂起的Open共用槽；Open/Bootstrap按阶段串行沿原Open槽登记，有限观察包装不算第二设备调用。若总限额不能容纳当前Root与子端点预留，Register/Create即拒绝，不等超时才发现无法Close。上游每endpoint的MaxStopRequests若超此一个并行task，以原StopIdentity/Scope去重合并收敛，不无限分配停止任务；不宣称多个独立硬件Stop同时可执行。Compare撤销与关闭在此预留通道串行，仍不能使阻塞native可中止。未决槽长期占用达到cap时禁止新Endpoint/普通write，原Stop/Close/task监督仍有效。

### 15.3 故障后收敛/原任务与对账的接收条件

Root.Close首次同步关新准入，开始**唯一完整清理task**，返回每次有限观察Task；重复只观察/续同阶段，budget=min(请求,Limits.CleanupBudget)，不重复物理Close/Open。不以新callSequence重发同PhysicalClose；原Task真实退出后若后端明确有未完阶段，续该阶段，不第二次call已确认关闭函数。正常Host先让自己持有的M.Session/S.Service收敛operation/compare/pulse/lease，再Root.Close；Root不回调产品Session、不抢原owner发写，仍有子资源返回计数与Closing/Held等待自愿释放。late未交消费者的endpoint/lease由Root Close/Release，不推给已返回的局部Host。

所有子资源归还→确认原backend/native任务与callback退出→ClosePhysicalAsync→本IPC/Process消费者退出，最终才确认OS Released。Physical.Close原Task未知保Root/后端/子产物/原ledger入口；Fault时§4.2 Kill退出也只OS Released，UnresolvedOperationIds仍保有，registry不移除。worker已退出则ClosePhysicalAsync只确认原OS回收记录、零重新SDK Close，不启动第二进程替代写。GoogolConnectionDrain不声称物理停止；后端读回停止事实只交M/S原回执，各Owner自己的Stop/Applied判定仍权威。

Quarantined时现有原端点Query/Recover可经Backend执行**同Root监督的只读重连对账阶段**，不另创建端点/Root或复活普通写。先核独立安全链允许的读用途及只读Open证据，登记单一原reconcile task/读额度，重连一次读新Boot/Generation，若无法关联原控制器persistent sequence/原body/boot，就Unknown而非将原请求代号贴在新回执上。相关事实能证明原操作才由上游原Session/SignalRoot进展恢复；仅当前静止/人工点击不能伪造旧动作结果。确无原结果可查则原Unknown/根保留，设备现场重新取得控制权须原Motion/Safety部署Owner按批准RecoverPolicy提供明确审计/资源移交方案；本模块无“清空未知/自动抢占”API。该限制是已确定的fail-closed恢复，不让开发者临时设计重发路径。

ConfirmReleased只能核该Owner当前RootId和**原Close生成的内部回执**/计数真实0、State=Closed、OsResources=Released、UnresolvedOperationIds空，不信外部构造相等record；引用并行变化在Root同gate复核。全部满足才移除Registry槽，不删正式ledger。若物理资源已Released但设备动作未决，由原M/S原会话查询/Recover完成并将后端相关未决索引同步，Root后续Close仅续本收敛，不能调用者传“已停=true”删除。对账失败持续占槽；不新Root绕过、无自动移交API。进程关闭/方法离栈/GC非接收。

Backend失败归类与上游精确映射如下；MessageKey=`Googol.Error.<下表后缀>`，Code=`GOOGOL_<后缀>`。表中前七行是未发出时的失败；已发出而结果不可证统一保Unknown/PossiblePhysicalEffect=true，不映射NotSent或以原错误码宣称未执行。上游已给出的权限/模式/幂等错误直接保其原typed failure，不压为厂商参数错误。

| 后缀 | Motion Code | Signals ErrorCode |
|---|---|---|
| INVALID_ARGUMENT | MOTION_INVALID_ARGUMENT | InvalidArgument |
| PROFILE_MISMATCH | MOTION_CAPABILITY_CHANGED | MappingMismatch；若仅能力修订不符用CapabilityMismatch |
| ABI_UNVERIFIED | MOTION_UNSUPPORTED | Unsupported |
| UNSUPPORTED | MOTION_UNSUPPORTED | Unsupported |
| OWNER_CLOSED | MOTION_CONTROLLER_UNAVAILABLE | NotConnected |
| RESOURCE_LIMIT | MOTION_RESOURCE_LIMIT | ResourceBusy |
| DEADLINE | MOTION_TIMEOUT_UNKNOWN，DeviceCallMade=false/PossiblePhysicalEffect=false | DeadlineExceeded，Outcome=NotSent |
| UNKNOWN_OUTCOME | MOTION_TIMEOUT_UNKNOWN，保真实DeviceCallMade/PossiblePhysicalEffect | UnknownOutcome，Outcome=Unknown |
| DRAIN_UNKNOWN | MOTION_DRAIN_TIMEOUT，Resources未证归还则Held/ReleaseUnknown | DrainTimeout，Resources按原证据Draining/DrainUnknown |

无receipt方法不能返回假快照：Open/Read失败抛`GoogolBridgeException : Exception`，公开构造`GoogolBridgeException(GoogolBridgeFailure failure)`及只读属性`GoogolBridgeFailure Failure`；failure非null，Exception.Message为MessageKey、不含payload/秘密。Session保原打开task/异常并保持未知/未排空。BackendOpenResult有Evidence+Failure时仍保其连接事实，不能因失败丢已打开资源。

原物理设备只能只读重新对账，不普通写重放；并发读也受原槽/deadline。设备实停、安全链/质量不由Registry保证。上游M.IMotionReadSource只读历史桥不包含在IM-064既有motion命令适配范围：没有同步XY/稳定SourceRecordId/PositionVersion/缺包连续历史就明确NotSupported，不从ReadFeedback两帧拼历史。本模块提供原反馈/clock/sequence以供批准历史Owner保留，不能暗建扫描产品历史库；该限制不缩减固高原已批准Home/Move/Jog/FIFO/Compare/IO。

### 15.4 部署Profile身份、内部IPC与Signals地址

GoogolNativeProfile ContentSha256编码域`googol-native-profile-v1`，按C1的S/I32/I64规则，前缀为S(domain)+I32(1)，再表中构造顺序递归，排ContentSha256自身；GoogolCountMap/RateMap/SignalBank嵌套字段按表顺序，double为finite IEEE754 bits little-endian I64、-0规范+0，bool一byte0/1，null先byte0否则byte1+值，TimeSpan为Int64 ticks，immutable array I32 count逐项，enum I32沿所属已冻结编号。Profile的Axes按Axis.Value Ordinal、Functions按FunctionName Ordinal、SignalBanks按Bank Ordinal排序，重复拒绝；其他数组保持契约声明顺序。configuration hash为外部已冻结引用，不再编码原config；source/prototype文字严格UTF-8无BOM、无Unicode归一化，长度<=4096 UTF-8 bytes，标识<=128 ASCII，单profile受Root MaxRetainedBytes。此codec只N1，函数名不是执行权限。

N1公开`static class GoogolNativeProfileCodec`仅`byte[] Encode(GoogolNativeProfile profile, GoogolBridgeLimits limits)`及`string Sha256(GoogolNativeProfile profile, GoogolBridgeLimits limits)`，hash排自身但Encode含不含自身的定义须统一：**Encode返回上述hash预像，固定排自身**，非wire保存完整DTO。输入hash若非空须hex64，Validate/注册时独立Sha256相等才接收；计算新hash时允许空ContentSha256，注册不允许空。新byte[]每次独立所有权、无共享缓存；未知enum/非finite/长度超限/截断或类型不匹配按本节BridgeException对应错误，未运行。

递归编码具体化：AxisId/Frame仅S(Value)，NumericRange为F64(Min)+F64(Max)，MotionValue为F64(Value)+I32(Unit)，Home其余字段按§15.1表序；NativeTimeBase沿附录A Second=0/Millisecond=1，速率order由具名字段对应1/1/2/3，不额外插入order字段。所有hash须小写hex64；必需record/string/数组元素非null，N1数组default拒绝，空数组须显式Empty。顶层profile/limits=null抛ArgumentNullException；其余结构/枚举/无效Unicode/范围错为INVALID_ARGUMENT，长度或checked字节累加超限为RESOURCE_LIMIT，声明hash与重算不等为PROFILE_MISMATCH。先以checked计算准确编码长度并核数组count/字段长度，再分配结果；count受可编码长度及MaxRetainedBytes限制，Register另核CoreLimits.MaxAxes。空Functions/SignalBanks或空功能证据允许结构编码，不能据此授功能支持。

Profile JSON由宿主配置Owner解析成上述typed record，单独schema=`googol-native-profile-v1`，精确camelCase字段，不额外CLR $type；Int64十进制整数、double round-trip、enum冻结名称、nullable显式null、数组显式给出，duplicate/未知字段拒绝，不默认字段。部署文件另外包含SDK路径（绝对批准目录）与完整ContentSha256，路径不进profile身份；读DLL先核exact SHA256，不搜索PATH/当前目录。不是GGSport旧JSON运行时迁移，旧文件仍只读。proto/证据文本不能作为动态原生指令。

IPC仅Native/worker内部：binary固定20-byte头`GGIP`+U16LE协议1+U16LE方法tag+U32LE payload长度+I64LE callSequence；payload用严格UTF-8 JSON manual typed reader，字段依序rootId/endpointId/ownerEpoch/generation/requestId/profileSha256/configurationSha256/deadlineRemainingTicks/body，无CLR类型名。sequence正、checked单调，generation首次未读时null，回应关联原sequence/epoch不凭null当当前身份；deadline ticks正且受剩余预算，worker接收以自身单调时钟开始有限等待，不跨进程比较absolute timestamp。

tag冻结1..15：OpenReadOnly、CreateMotionEndpoint、MotionReadCapabilities、MotionReadStatus、MotionValidatePath、MotionSubmit、MotionStop、MotionQuery、MotionDrain、MotionClose、MotionCancelCompare、SignalsAcquire、SignalsRead、SignalsExecute、SignalsQuery；16订阅数据、17SignalsSubscriptionStop、18PhysicalClose、19返回、20错误、21SignalsSubscribe、22SignalsLeaseRelease、23MotionFeedbackSubscribe、24MotionFeedbackUnsubscribe。Response tag19的body为`{requestTag,result}`，错误tag20为GoogolBridgeFailure；结果数据严格沿对应typed返回record。Live IMotionAdapter/lease/subscription不能序列化：Create endpoint结果wire为`{endpointId,failure}`、SignalsAcquire为`{leaseId,capabilities,errors}`、Subscribe为`{subscriptionId,errors}`，client包装为既有typed实例，token只该Root/epoch/generation有效，迟到也须查同token归还，不SDK句柄。worker token由原endpointId/requestId登记生成、重复不创建第二资源；Release/Stop/Unsubscribe各用原token与相应上游DrainRequest/Scope。

内部body的多参数/实例绑定固定：tag1/2为GoogolChildRequest；tag3为`{deadlineTicks}`；tag4～11分别为M.StatusRequest/AdapterPathQuery/AdapterCommand/StopRequest/AdapterOperationQuery/DrainRequest/CloseRequest/AdapterCompareCancel。tag12为S.AdapterAcquireRequest；tag13/14/15为`{leaseId,request}`/`{leaseId,command,context}`/`{leaseId,request,deadline}`，request分别S.AdapterReadRequest/QueryCommandRequest，command/context为S.AdapterCommand/AdapterCommandContext。tag17/22为`{subscriptionId,request}`/`{leaseId,request}`，request为S.DrainRequest；tag18为`{rootId,observationBudgetTicks}`；tag21为`{leaseId,request}`，request为S.AdapterSubscribeRequest；tag23为`{scope}`（M.AxisScope），返回`{subscriptionId,failure}`；tag24为`{subscriptionId}`，取消枚举并保原Dispose/回调收敛。tag16为`{subscriptionId,source,value}`，source精确MotionFeedback/SignalEvent，对应M.AdapterFeedback/S.RawSignalEvent。外层endpointId定位原Motion实例或Signals工厂，body token须归同Root/epoch/代，不接受调用者换实例。取消token是本地观察/控制信号，不序列化CLR对象；控制侧未完成的原Dispose/Stop仍登记保留。

tag2在worker冻结逻辑token的role/代，返回的client后端endpoint仍未被M.Session打开；其OpenAsync仅核本地controller/role/期限并以tag3有限读当前能力，不另发物理Open/切role。tag24实际原枚举器Dispose/回调退出后result=null（无上游void回执可伪造）；原task未结束时不能以一个null ACK证明归还。tag25/26的payloadSha256为**完整普通调用body原UTF-8 bytes**的SHA-256，仅关联内部许可、不得替业务canonical身份；Motion还核原request/path/PathValidation hash，Signals还核原CanonicalPayload/PayloadHash。双方保留相同原bytes，不重新序列化后猜许可身份。

body按各方法的上游输入record camelCase（例tag4直接StatusRequest）；标准enum使用冻结名称，Int64数字在manual reader直接GetInt64不得转double，byte[]/ImmutableArray<byte>用小写hex字符串（偶数长度，限预算），TimeSpan用Int64 ticks，DateTimeOffset用`{utcTicks,offsetTicks}`，nullable显式null，string严格UTF-8不Unicode归一化。字典AxisId key用Axis.Value且Ordinal规范，不允许重复；AxisId/Frame作为值用`{value}`。普通MotionCommand使用`{kind,request}`并按kind白名单CLR类型读原Context/Scope/派生字段，Signals AdapterCommand与RawSignalValue用`{type,value}`，type分别Write/Pulse及Digital/Signed/Unsigned/Floating/Counter/Latch（只允许上游对应record字段），禁止未知tag/default分支按object读。上游特殊请求不伪装普通command。普通字段非finite拒绝；现场原反馈值不可编码成合法JSON数字时相应字段置null、质量Unavailable/原码诊断，Simulator内部原位值直接走原计划、不通过IPC洗掉反例。

整数类型逐字段保持：S.RawUnsigned/RawCounter/CaptureId/Sequence的UInt64用GetUInt64（0～2^64-1），不经Int64/double；M.Generation用非负Int64，本Root的S.ConnectionGeneration固定为`OwnerEpoch+":"+generation的无前导零十进制`，由后端同次发现生成、不把SDK boot或S字符串硬转long。重连新增代但查询body的OriginalConnectionGeneration/Boot/Generation保原值，外层generation只表示当前查询通道。SDK不能关联旧代时明确Unsupported/Unknown。

S.HostStamp保持parent注入TimeProvider域：Acquire.HostClock/所有Deadline先在parent验证同域并算剩余量，worker只把原域/tick当关联证据，用外层deadlineRemainingTicks限制本地等待，不能以worker tick比较原HostStamp。S.Read的本请求发送前/收到后由parent包围并填本域读取窗口；只有官方证据保证该读取确为本请求新采样才填Earliest/Latest，否则null。订阅Received由parent实际接收记录，不把它充当设备采样；worker原接收域只作诊断。设备DeviceStamp/ClockDescriptor保原域，缺有效跨域映射时不填设备到主机样本时间/误差。GoogolDeviceEvidence的CapturedAtTimestamp/TimestampFrequency也由parent缓存更新时赋值，worker的时标不冒充Root时钟。

未知field/tag/enum、尾bytes/截断/bytes超cap在分配/dispatch前拒绝，业务hash仍上游canonical不hash JSON；收到payload先完整parse校验后才任何native call，转义/空白变化可读但不影响业务身份。每live接口原task/token在client/server双方有界根保留，token丢失则Unknown/保持隔离，不靠进程退出伪造设备归还。协议不负责新产品通信，拒未知major版本；Open/create关联原callSequence与body精确身份，不重发ACK丢失的写。

接口对象不能进JSON：Signals.Execute的ISignalAuthorizationPort只在parent借用；child预检完成到send前通过控制tag25（ReadyToSend，body字段`originalCallSequence,token,payloadSha256,generation`）通知parent，parent按原端口/原context再次授权并在当前Root gate核有效/fence/期限，发tag26（SendPermit，body字段`originalCallSequence,token,permitId,payloadSha256,generation,remainingTicks,fencingToken`；Signals无Motion fence时最后字段显式null）。permitId为Root单调唯一ASCII标识；控制帧本身sequence也独立正单调，原调用关联只用originalCallSequence，不能复用普通seq冒充新调用。parent先记录许可可能物理作用再send，child仅同代/原body/未消费/未过期许可执行，非许可tag不能write；拒绝零SDK写。许可发出后撤权已越过“动作可能发出”边界，原Stop/关新准入，不承诺跨进程撤销已发许可。ACK丢失许可不重发，不新授权续期限；parent失联child有界等待后不send。Motion普通命令仍来自可信M.Session用途授权/账本，parent通过上述GoogolMotionPorts保存的原凭据复核，不签新Motion授权；许可前核共享Owner lease/epoch/原context/stop gate，不借pipe绕Core。硬件独立安全链不依赖此协议，不能把UI布尔值代授权。

worker启动后第一条tag27 Bootstrap的body完整字段依序为configuration/coreLimits/profile/limits/sdkDllPath/ownerEpoch；全部按上文typed JSON读取/预算，且外层rootId/profileSha256/configurationSha256/epoch匹配、generation=null。worker以TimeProvider.System计本机剩余时长，不拿parent Timestamp当自身tick；实际GGS进程后端要求parent用真实单调System时钟，虚拟测试只假Backend不用进程。Bootstrap只核文件hash/元数据，不Open/Reset，回应仍tag19；未经Bootstrap或重复异内容Bootstrap拒绝隔离。SDK加载及首次连接在其后明确OpenReadOnly阶段，未取得官方只读路径则拒绝不试开。真实测试须同时观测worker bootstrap原task/IPC/Process Owner，不进程启动后补登记。

取消/收尾信号走独立有界控制pipe，本地send关闭不证明设备stop。进程访问仅同用户批准子进程、不可从外部任意TCP连入；IPC不是跨产品通信模块。worker调用序列与回应顺序独立，通过callSequence+epoch对账，失配隔离。物理Stop是否独立/可达必须另官方证据，不把独立pipe当硬件资格。未知原生buffer绝不跨IPC，status/数组copy成typed值且长度核实。

Signals地址固定`Bus="googol-gts"`、AddressFormatVersion=`googol-channel-v1`，Address=`card=<c>;core=<k>;bank=<b>;index=<i>`，SubChannel=null。c/k/i为无前导0非负十进制Int32（0例外），bank仅`di/do/ai/ao/counter/latch/compare`小写；bank必须在Profile.SignalBanks唯一存在且logical i<LogicalCount、NativeIndex=checked(NativeIndexBase+i)，不能隐式+1猜SDK。count正、base非负、末index不得Int32溢出，范围来自目标官方/设备Owner。空SignalBanks明确不提供IO，codec结构允许但真实Acquire拒绝Unsupported。bank函数调用采用§4.1对应已核typed函数，不凭bank字符串反射执行，扩展/标准通道差异在固定版本typed实现与EvidenceReference标注。

CanRead/Write与S.Spec/Direction/Mapping严格交叉，输入禁write；HardwarePulse=true须目标原生脉冲、正min<=max/证据齐，false则两width null，不Task.Delay兜底。compare输出只能登记归属线路，不普通DO兼写；重复输出/compare与DO同物理线路冲突/极性矛盾拒绝，readonly别名仅上游ReadAliasGroup批准。AI/AO raw格式/分辨率由上游S.AnalogSpec与型号实际值交叉，未支持不默认double输出。S raw观察逐项质量/原设备时标/接收时刻/seq/代返回，批量一个码不能所有项Applied。

## 16. W1 原UI根、证据/草稿与完整双STA装配

### 16.1 可构造证据输入与更新

§8.1增加的可选Diagnostics参数为默认null，保留三参数旧绑定形状；null明确“未提供厂商证据”，不能自动探设备。类型在Core namespace `Asun.Modules.GoogolMotionAdapter`，纯不可变诊断投影，不引Signals/SDK；新类型供UI/Native真实消费者，不改变C1配置hash。

| 类型/接口 | 精确字段/方法 |
|---|---|
| GoogolEvidenceQuality（enum0起） | Unknown, Declared, Observed, Qualified |
| GoogolEvidenceFact | sealed record：string Key, string? Value, GoogolEvidenceQuality Quality, string SourceReference |
| GoogolDeviceEvidence | sealed record：string RootId, string ControllerId, string ConfigurationSha256, string? ProfileSha256, string? BootId, long? Generation, M.SourceKind Source, long CapturedAtTimestamp, long TimestampFrequency, ImmutableArray<GoogolEvidenceFact> Facts |
| IGoogolDiagnosticReader | `GoogolDeviceEvidence ReadCurrent()`；有界、线程安全、纯缓存读，无设备IO/任务/权限副作用 |

Root新增实现该接口，ReadCurrent=GetEvidence同原缓存，不传native handle或原Task。Reserved阶段以Source=Hardware表示来源目标但所有未观测fact=Unknown、Boot/Generation=null，不能显示已连接。Facts key白名单SdkHash/Abi/Firmware/Card/Core/CommandScale/EncoderScale/Clock/StopRoute/Connection/OsResources/Unresolved，不直接输出任意XML/SQL/配置秘密。未知Value=null，Declared不是Observed/Qualified；来源Reference可定位本Profile/官方证据/HIL记录，既有Core Simulator无Native Root时Diagnostics=null，来源看Session的Simulation/Replay。

读者每次只给不可变snapshot，GoogolViewBinding.Diagnostics借用不Dispose。控件普通render周期在本Dispatcher读取一次ReadCurrent（缓存，不开启async轮询），按config.ControllerId/hash与Session当前Boot/generation关联；错身份或旧代显示“历史/版本不符”不刷新当前设备事实，不能改变Session准入。读者失败只显示证据不可用，不覆盖原运动错误/Stop/Query，不经此读者派命令。Snapshot.CapturedAtTimestamp属于Root固定TimeProvider域（RootId为epoch），age不能与另进程/虚拟clock相减；跨域只显示原采样时标，不编造年龄。

PropertyGrid白名单AxisId/Frame/unit/address/Scale ratio/sign/origin/revision，draft初始为Binding.Configuration，变更后GetDraft返回含原schema/controller/base revision的不可变新草稿；修改只是本地候选，保存由宿主正式配置Owner取得新revision，不模块自增revision伪批准。校验用C1，同步错误标字段/原值，取消草稿恢复Binding的原snapshot。字段变化使本页pulse预览失效重算，不写设备/不刷新能力hash。Native完整Home/encoder/ABI Profile只读证据，不本页暗改；这些值变更必须宿主批准新Profile并原Owner收敛。

### 16.2 View根、原Dispatcher任务和恢复

Motion当前§17.4已新增MotionViewOwner（保inner view/生成器真实Task），IMotionLifecycleOwner仅持Session不能代UI。本模块outer view必须另有根，不把窗口闭后原outer task遗失。

WPF新增`sealed class GoogolViewOwner`唯一构造 `GoogolViewOwner(int capacity, Asun.Modules.MotionControl.Wpf.MotionViewOwner motionViews, TimeProvider time)`；方法 `bool TryRegister(GoogolDiagnosticsView view)`、`ImmutableArray<GoogolDiagnosticsView> GetPending()`、`bool ConfirmReleased(GoogolDiagnosticsView view, M.DrainResult result)`。capacity正、依赖非null，借用motionViews/time不Dispose；根由应用进程提前持有。TryRegister在view.Dispatcher，先预留outer槽，再注册其私有inner MotionControlView，失败原子撤未开始槽、返回false；成功两根互持，未注册Attach拒绝。重复注册同实例成功，不双扣槽；构造/注册均无设备副作用。

GetPending/ConfirmReleased线程安全，有界快照不IO；Confirm仅接受该view原Detach结果且bindingGeneration/inner真实回执一致，outer缓存读/render回调、inner generator/preview/submit/枚举器dispose/Dispatcher、原operation/compare全部确认退出，才先inner根确认再outer删槽。普通调用者构造IsReleased=true无效，根不在锁内跨Dispatcher.Invoke。解绑后可同实例先Register再Attach下一binding，原未归还禁重绑。

Detach观察budget=min(参数,Binding.Motion.Profile.DetachBudget)，ct只结束观察；完整cleanup task在GoogolViewOwner记录并强持，与inner原task相关，不每次重复Detach新stop/generator。退出路径保原业务错误，再单列cleanup失败，不finally异常覆盖它。超时返回M.DrainResult DrainUnknown/Resources Held/IsReleased=false（SessionId原binding），保root/view/Binding/原task/未决ID；即使Session已移交LifecycleOwner，outer/inner UI根仍保留各自任务。恢复只在原Dispatcher继续同view.Detach/原ID Query，后确认两根释放；不销毁dispatcher再试从其它STA访问原view。

窗口Closing先Cancel=true、禁普通写→有限Detach观察。成功才解除Closing；失败显示“资源归还待确认”，应用保窗口/原Dispatcher或不结束原dispatcher loop的受控后台视图，保可查询panel，不抛失去根。进程退出若必须终止，不把它记作Motion/设备安全通过。调用方提前取消/Dispose只是观察条件，不清空pending。

### 16.3 两个真实WPF Host与文案覆盖

Host A扫描只读与Host B定位/维护的Core/Session分别按§9/Motion当前§17.6显式构造，无空宿主猜Dependencies；仅软件动作 fixture用Motion已冻结F1/F2合成计划，不在此重写其Golden。应用先new MotionViewOwner(2,TimeProvider.System)、GoogolViewOwner(2,innerRoot,TimeProvider.System)，强持两Session LifecycleOwner；STA-A/STA-B各创建Dispatcher/Window/GoogolDiagnosticsView，TryRegister→Attach完整GoogolViewBinding。MotionUiProfile合成RenderPeriod50ms/MaxVisibleSamples512/HistoryRows128/DetachBudget1s，Culture分别zh-CN/en-US，第二再换zh-TW；ThemeId宿主当前局部主题，config用对应fixture的controller/轴/unit/frame/revision，不能把§9.1 controller-1强绑F2其它controller。Diagnostics null或从同Root缓存Reader借用，A/B只共享线程安全Root/不可变snapshot，不共享视觉对象。

CreateCommand沿inner绑定显式用途/原Scope/Context/预算；readonly A拒任何普通写，B只发预先构造的公开Move/Home/Jog草稿用途，Stop/Query原身份与generation，不UI bool授权限。finally先本view原Detach/确认inner+outer根，然后**拥有Session的宿主**Close；业务主错误/cleanup错误分开，未知保原Dispatcher/task/Root，不控件Close借用Session。双STA实际循环/窗口与UIA后续W1.Exe验证，case30s/suite180s/外进程240s（合成防挂非客户指标），1920×1080唯一viewport，未满足时记录未执行不换屏。

动作/state/error三语复用Motion当前§17.4资源词表（标题/参数/禁止原因/原操作/恢复/未知），固高新增字段键`Googol.Field.<name>`不enum.ToString：

| name | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Card/Core/Axis | 卡/核/轴 | 卡/核心/軸 | Card/Core/Axis |
| CommandScale/EncoderScale | 命令脉冲比例/编码器比例 | 命令脈衝比例/編碼器比例 | Command pulse scale/Encoder scale |
| DirectionSign/OriginPulse | 方向符号/原始零位 | 方向符號/原始零位 | Direction sign/Native origin |
| CountsNumerator/UnitsDenominator | 计数分子/工程单位分母 | 計數分子/工程單位分母 | Count numerator/Engineering unit denominator |
| Revision/Evidence/Abi | 版本/证据来源/原生接口 | 版本/證據來源/原生介面 | Revision/Evidence source/Native interface |
| Validate/Revert/VersionMismatch | 校验草稿/撤销草稿/版本不符 | 驗證草稿/還原草稿/版本不符 | Validate draft/Revert draft/Revision mismatch |
| Unknown/Declared/Observed/Qualified | 未确认/资料声明/已读回/已验证 | 未確認/文件宣告/已讀回/已驗證 | Unconfirmed/Declared/Observed/Qualified |

厂商错误资源逐码如下；键为§15.3的Googol.Error.<后缀>，FieldPath按字段词表显示，无法定位字段时使用“操作/操作/Operation”。模板分别为“{字段}：{原因}。{恢复}”/“{欄位}：{原因}。{復原}”/“{field}: {reason}. {recovery}”。VendorCode仅作为诊断原码，不替换这些文字；原因和恢复不能省略成泛“错误”。

| 后缀 | zh-CN 原因；恢复 | zh-TW 原因；恢复 | en-US reason; recovery |
|---|---|---|---|
| INVALID_ARGUMENT | 参数无效；检查字段范围和单位。 | 參數無效；檢查欄位範圍和單位。 | Invalid setting; Check the field range and unit. |
| PROFILE_MISMATCH | 版本不符；核对配置和设备版本。 | 版本不符；核對設定和設備版本。 | Revision mismatch; Check the configuration and device revisions. |
| ABI_UNVERIFIED | 原生接口未核实；补齐目标 SDK 接口证据。 | 原生介面未核實；補齊目標 SDK 介面證據。 | Native interface unverified; Provide interface evidence for the target SDK. |
| UNSUPPORTED | 不支持此操作；查看设备能力。 | 不支援此操作；查看設備能力。 | Operation unsupported; Check the device capabilities. |
| OWNER_CLOSED | 连接已关闭；查询原连接的归还状态。 | 連線已關閉；查詢原連線的歸還狀態。 | Connection closed; Query the original connection's release status. |
| RESOURCE_LIMIT | 资源不足；等待原任务结束，再检查资源上限。 | 資源不足；等待原工作結束，再檢查資源上限。 | Resource limit reached; Wait for pending work, then check the resource limits. |
| DEADLINE | 观察超时；查询原操作，不要重发。 | 觀察逾時；查詢原操作，不要重送。 | Observation timed out; Query the original operation. Do not resend. |
| UNKNOWN_OUTCOME | 执行结果未确认；查询原操作，不要重发。 | 執行結果未確認；查詢原操作，不要重送。 | Execution result unconfirmed; Query the original operation. Do not resend. |
| DRAIN_UNKNOWN | 资源归还未确认；保留原连接，继续查询归还状态。 | 資源歸還未確認；保留原連線，繼續查詢歸還狀態。 | Resource release unconfirmed; Retain the original connection and query its release status. |

SuperTip同时显示版本/来源/范围、操作影响和恢复，不堆栈/夸张AI词。图像操作不属于运动诊断控件，不放假影像区/ROI工具；专业品质验实际数值层级/布局/联动与键盘各自断言，不能功能可点就算精美。

## 17. 本轮全模块准备结论、增量断言与外部Owner

### 17.1 已批准完整能力与可决定设计

完整范围包括固高配置/单位/hash/旧配置显式迁移、SDK/卡核轴/能力发现、公共Motion与Signals桥、Home/Abs/Relative/Jog/Servo/配置/Reset/Recover、插补FIFO/compare/capture、状态/clock/查询/lease/Stop互锁/未知与排空、Simulator/Replay/双无UI消费者、WPF三语/双STA/诊断草稿与恢复、Benchmark/发布回退。每项唯一处理链§1～7/15，UI§8/16，Core附录A，验收§10～12/17.2。自动整定/视觉/质量放行/安全PLC/SDK具体实现暂缓的界限§1.1/15.1，不遗漏已规划Adapter/UI，也不扩为生产扫描流程。

**本原会话完成内容审核/修复/定向验证后，对以上批准范围判断：可决定的软件设计欠账已闭合。** 原C1/C2接收与向量有效；W1/N1托管接线/codec/根Owner/状态/单位/原任务/预算/双Host的内部规格现在可照文实施，不再等待总控内容复核。N1每个真实函数是否可使用、何种C ABI/物理参数，仍必须补目标资料事实，不以内部接口冻结冒充它已具备。整模块保持DesignReview/Prep；W1/N1/产品保持PreparationIncomplete/NotReady，这是正式实现/运行/物理资格边界，不重新把已定软件规格列待设计。

### 17.2 仅增量的Golden、恢复与验证计划

复用§10/G01～G08及126-byte向量，不重算已接收片。新增N1/wpf断言在§14各自唯一测试工程，当前不创建/执行：

| ID | 输入与Oracle |
|---|---|
| N-G01 两映射 | Command N=1000/D=1/sign=1/origin0/工程origin0；Encoder N=2000/D=1/sign=-1/nativeorigin100/工程origin10，目标q=1.25。命令1250；raw encoder20100→q=0。不得原命令scale解encoder；例目标encoder17600→q=1.25 |
| N-G02 有理/边界 | encoder/sign=-1/nativeorigin100/工程origin10/N=1024/D=1，q=9.99951171875→raw100.5→最近偶数100，回投影10/error1/2048；q=9.99853515625→101.5→102。任一限位/误差包络不容纳则拒绝，不改目标 |
| N-G03 地址/单位 | `card=0;core=0;bank=di;index=0`有效结构；index=00/-1或bank=DI/未知/Kind不符/SubChannel非null拒绝。profile单位各API不同显式map，配置scale变化invalidates能力，不猜ms/s |
| N-R01 注册/late | registry容量1，second同Controller即换RootId拒绝；Open task在slot登记后才启动。首次观察超时保Root/task；late evidence/endpoint/lease非空+failure逐产物收尾，不发布writer |
| N-R02 两客户端 | 子writer与reader Close不互关；同卡S lease Release不关Motion；只最后计数0调用PhysicalClose一次。profile独立Stop证据空，硬件write Open拒绝但readonly/Core正常 |
| N-R03 关闭/未知 | 后端Kill确认→OsResources Released但Unresolved非空Registry Confirm=false；重复Close续同task；原Owner相关Query/Recover后才能清未决。clone构造Closed结果不能骗Confirm |
| N-R04 发送与共享 | 普通queue满Stop预留依然接纳，但card死锁不能标stop成功；CreateMotionPorts转发原Prepare/Acquire/Renew/Release，原lease/授权捕获失败或撤权/换代send前拒绝，已发permit未知不可NotSent。只读CreateMotionAdapter不能write Open；绕过转发端口的Dependencies拒绝写。UI/SDK callbacks不锁内Invoke/无无限task |
| N-C01 身份/codec | profile Encode相同排序轴/函数无关顺序hash相等，改变encoder origin/native时间单位/SDK hash/electrical证据hash变化；config旧126 bytes不变。返回bytes独立、mutation不改下次hash；未知enum/非finite/超bytes拒绝 |
| N-C02 IPC | 合成tag6/seq1/有限Move正文，按GGIP头核payload byte count；故意截断/尾bytes/错epoch/hash/未知field/Int64>2^53在parser仍整数，零raw call或相关Unknown。协议1拒major2，无动态CLR执行 |
| W-R01 UI根 | 未Register Attach拒绝；inner容量满outer回滚；CreateCommand挂起Detach超时两UI根/Session三者各持原任务，旧生成器晚到零Submit；fake released不能删root |
| W-R02 双STA/缓存 | A readonly/B writer，主题/语言/字典隔离；一窗Detach不CloseB/S。Diagnostics旧hash/generation显示history差异，不实际freshness；reader异常Stop仍可用 |
| W-R03 关闭 | Closing拦截/有限观察，pending不销原Dispatcher；解除闩锁→同view Detach→两根Confirm→宿主Session Close，业务错误不被finally覆盖 |

N-G/N-C数学/结构可离线执行；N-R用本测试工程可控IGoogolConnectionBackend与上游typed假端点，不新发布“物理Simulator”，证明Root原Task/计数而非真实设备。N1 Exe采用BCL/net10.0（实际worker/IPC另进程），case10s/suite120s/外进程150s；W1用§16.3预算。性能新增记录Root slots/high-water、两端lease/task logical bytes/实际heap、Open join/late归还、IPC拒绝/queue wait、PhysicalClose原task/未决保留数、UI inner/outer回调至真正Detach；统计沿§12/GOV，目标待合同/消费者采纳，不填猜值。

### 17.3 外部事实Owner与实际资格，精确剩余项

消费Motion 0.2.5-prep新增字段的确定规则：M.CoordinateQuery.Kind/Start只由Motion Core与其注入坐标端口消费，IM-064不实现该端口、不猜Delta/绝对意义；收到M.AdapterCommand的ResolvedMachinePath就是已转换/已时间化机器路径，IM-064保留每TrajectoryPoint.Offset/Profile/ResolvedPathSha256逐段验证与下发，不重新rest-to-rest排程/改speed/补路径。普通Relative不再次积累，Origin/Sign/feedback比例按§15.1不二次乘号。路径预检如果固高插补器不能接受该时间/动力学模型则Unsupported零动作，不自动retime。重连只读对账/原task/WPF内外Root与停止门直接消费上游§17，已接收上游算法/向量不重审。

字段同步范围：今后实现本模块的扫描/定位/维护组合根须使用§15的Register→typed子端口/Root；写Session须同时注入CreateMotionPorts返回的Adapter/Authorization/ControllerLeases，不能只换Adapter留下未转发的两个依赖。§16 UI根和可选Diagnostics、worker两端协议1/新Profile schema（含SignalBanks）同步。坐标资产适配器若实现M.IMotionCoordinatePort必须消费Kind/Start，归其原Owner；本模块不修改该公开类型或其他指导。M/S自身无需为固高新增产品DTO/enum/算法，C1/C2消费者签名及126-byte身份保持，旧三参数GoogolViewBinding仍兼容Diagnostics=null。仅上游已发布二进制和未来构造调用需按现合同编译核对，未发消息或写其它模块。

| 剩余项 | 取得/批准Owner | 阻断范围 |
|---|---|---|
| 目标GTS/Gg DLL/头文件/API/结构/返回码/线程域/时间基底 | 固高官方目标SDK资料；现场集成方提供准确包/版本，IM-064原会话据资料填§4.1/15.1证据卡 | 对应Native函数实际编码，不阻Core/typed假后端桥 |
| 只读Open、boot/clock/掉线后设备行为、相关Query、独立Stop及停止锁 | 固高目标手册/固件事实+设备/安全链集成Owner的HIL；IM-064保正确映射，IM-010判运动事实 | 真实写Open/恢复/操作能力；不能以worker隔离替事实 |
| command/encoder比例/原点/方向、Home/limit/INP/servo/electrical、axis/FIFO/compare上限 | 机台工程/计量/运动配置Owner，Profile显式版本来源；信号线路Owner为IM-041/宿主 | 指定设备Profile与实际位置/信号资格 |
| 轨迹完整包络/jerk/原生插补器能力、compare/pulse实际时序 | 型号官方资料/经资格化模型Owner，Motion与Signals各事实Owner | 对应轨迹/compare/输出功能，不零端点模型伪证 |
| 持久ledger/授权/安全链/跨进程fencing部署 | 原Motion/Signals/存储/身份Owner的公开端口与可信宿主组合根 | 真硬件接入/进程重启对账，不新的产品内部设计 |
| 客户误差/停止时间/settled/性能/频率脉宽/长稳指标 | 客户合同、机台Profile批准者/现场验收方 | 目标判定/现场，不妨碍软件Benchmark方法 |
| build/run、WPF25.2.3/双STA/UIA、真实IPC/HIL/性能/产品接线 | 后续明确获派实现/资格任务，由本永久原会话执行；产品宿主Owner提供真实场景 | 实际ImplementationSpecificationReady/生产资格，当前无通过结论 |

软件判断不移交总控审核；总控仅接收此状态。N1函数缺“哪一个C声明/电平/单位值”不含可决定架构/算法欠项，取得事实后按本正文实施并验证。若后来发现事实与本文冲突，仅暂停受影响函数、修本唯一指导，不以参数试跑/编译错误偷偷改合同。

### 17.4 增量固定向量与唯一验证记录

`N-PROFILE-01`为§15.4完整字段编码的合成Profile：ProfileId=p-1、Revision=r-1、ControllerId=controller-1、ConfigurationSha256引用既有126-byte配置hash；SdkDllSha256=64个0（仅codec合成，不能批准真实DLL）、SdkVersion=fixture-sdk、DeviceModel=fixture-model、FirmwareFingerprint=fixture-fw；Axes=[X/Unit0/machine]，CommandPosition=EncoderPosition均NativeOrigin=0/EngineeringOrigin=0/N=1000/D=1/Sign=1/raw[-1000000,1000000]/MaxQuantizationError=.0005/QualifiedFeedbackError=0/Revision=map-1/EvidenceReference=fixture；FollowingError=null，CommandVelocity=EncoderVelocity=Acceleration均N1000/D1/Sign1/TimeBase Second0/Revision=rate-1/Evidence=fixture，Jerk=null/Home=null/ReferenceEvidence=fixture/ReportsPositionHold=false/UsesControllerStopLock=false。Functions空，SignalBanks=[]，ReadOnlyOpenEvidence/BootEvidence/ClockEvidence均fixture，IndependentStopEvidence/PathValidationEvidence/SignalsAddressEvidence空。ContentSha256按规则排除自身；这是不具备设备功能的fixture，codec可编码不等于Register/真Open就有ABI资格。

完整648 bytes hex（围栏排版不进入bytes）：

```text
18000000676f6f676f6c2d6e61746976652d70726f66696c652d76310100000003000000702d3103000000722d310c000000636f6e74726f6c6c65722d31400000003338663235633434393765613435326365373866396331363838356238643238616433623662343362376539613662343137616162666462393132663435303840000000303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030300b000000666978747572652d73646b0d000000666978747572652d6d6f64656c0a000000666978747572652d667701000000010000005800000000070000006d616368696e6500000000000000000000000000000000e803000000000000010000000000000001000000c0bdf0ffffffffff40420f0000000000fca9f1d24d62403f0000000000000000050000006d61702d31070000006669787475726500000000000000000000000000000000e803000000000000010000000000000001000000c0bdf0ffffffffff40420f0000000000fca9f1d24d62403f0000000000000000050000006d61702d31070000006669787475726500e8030000000000000100000000000000010000000000000006000000726174652d310700000066697874757265e8030000000000000100000000000000010000000000000006000000726174652d310700000066697874757265e8030000000000000100000000000000010000000000000006000000726174652d3107000000666978747572650000070000006669787475726500000000000007000000666978747572650700000066697874757265070000006669787475726500000000000000000000000000000000
```

SHA-256=`3d288a64c17774640a2c2f26396db39aef007e81b26cec1e86a201fb2477c259`。固定IPC负例：tag6、sequence1、body原bytes`{}`（2bytes），20-byte头hex=`4747495001000600020000000100000000000000`，完整frame22bytes。header合法但缺必需envelope/body，契约期望Protocol拒绝/零native call，不因为tag正确发运动；增加/截断payload长度亦拒绝。本轮只核其报文结构，未运行IPC parser/worker。真实合法Submit还必须完整上游AdapterCommand/canonical hash/path，复用Motion向量不新造产品写授权。

本轮文档自审已完成：从真实消费者构造/捕获原授权与lease/发送前gate/双比例/epoch/原Task/最后lease/Unknown恢复/内外UI根/原Dispatcher走至可保留或释放状态，补齐遗漏的GoogolMotionPorts转发接线、worker监督/控制槽、UInt64/HostStamp/代映射及逐码三语恢复。定向验证通过：按字段独立构造648-byte Profile完整hex/hash一致，再用独立cursor逐字段读取（96个值/长度读取）并核末尾无余bytes；20-byte IPC头/22-byte负例结构及N-G01/N-G02有理算例一致；本文件本地链接、标题唯一、围栏配对、新增公开类型/构造/调用定位及上游Motion0.2.5/Signals类型与签名引用检查通过。上述是文档/数学/格式检查，原Task/恢复/双STA反例的运行断言仍须后续实现执行。C1/C2既有算法/G01～G08/126-byte接收不重算，只确认固定文本保持，不降低门禁。未创建报告/脚本/产品工程，未build/run/HALCON/WPF/性能/HIL；本轮已达文档准则，停止于此范围。

N1两消费者的公开构造线不留给调用方猜：进程先new GoogolConnectionRegistry(limits,time)，再new GoogolWorkerBackend(config,coreLimits,profile,workerOptions,limits,time)，然后Register(new GoogolConnectionBinding(rootId,config,coreLimits,profile,backend))；只有此后才owner.CreateMotionPorts("scan",hostAuthorization,hostControllerLeases)/CreateSignalsAdapter("scan-signals")。Motion将返回的三个端口一起注入M.MotionDependencies，Signals注入S.ServiceDependencies，由原M.Session.Open/S.Root.BeginCreate登记task并工作。维护消费者新建其自己的只读Motion子adapter("maintenance")及授权身份，复用同owner不new后端二次物理Open；维护需写时同样使用CreateMotionPorts("maintenance",...)，共享同原ControllerLease权威，不自授第二writer。当前没有真实Motion写lease时仅readonly诊断。两消费者末尾各关闭自己Session/Service，最后应用owner.CloseAsync有限观察/registry.ConfirmReleased。Register/创建子工厂异常无设备task且不覆盖初始主错误，已取得的原产物由原Owner收尾。无硬件验证将同构造链的backend换测试工程IGoogolConnectionBackend假实现，time可控，所有SDK/function counters显式为模拟；不另发一套厂商运动事实。

新增N1资源类型统一仍绑定§14 Native/Native.Tests，WPF新增根在Wpf/Wpf.Tests；Core仅追加纯证据record/reader，不修改已接收C1/C2声明/配置hash。未来实现命令：`dotnet run --project tests/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Native.Tests/Asun.Modules.GoogolMotionAdapter.Native.Tests.csproj -c Release`与`dotnet run --project tests/Modules/googol-motion-adapter/Asun.Modules.GoogolMotionAdapter.Wpf.Tests/Asun.Modules.GoogolMotionAdapter.Wpf.Tests.csproj -c Release`。Native.Tests net10.0 BCL Exe；Wpf/Wpf.Tests均net10.0-windows/UseWPF=true、测试OutputType=Exe，只公开引用绑定程序集与本机25.2.3；真SDK/worker不得用假后端PASS代替，真实屏幕不满足唯一基线报告未执行。


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

## 附录A：Module API Contract v0.2（唯一Core构造/调用）

### A.1 完整类型与所有权

全部Core类型在 `Asun.Modules.GoogolMotionAdapter`，BCL System/Immutable/Numerics，复用Motion的AxisId/CoordinateFrameId/MotionUnit/MotionValue/计划/adapter。下表每行是sealed record完整位置构造字段，不另造Motion命令。不可变数组default视空，null必需字段/元素拒绝；标识上游ASCII/Ordinal，revision ASCII 1～128，schema精确匹配。record构造本身不打开设备，函数统一校验。

| 类型 | 精确构造字段（按序） |
|---|---|
| GoogolAxisAddress | int Card, int Core, int Axis |
| GoogolAxisScale | long PulsesNumerator, long UnitsDenominator, int DirectionSign, long OriginPulse, string ScaleRevision |
| GoogolAxisBinding | AxisId Axis, CoordinateFrameId Frame, MotionUnit Unit, GoogolAxisAddress Address, GoogolAxisScale Scale |
| GoogolConfiguration | string SchemaVersion, string ControllerId, string Revision, ImmutableArray<GoogolAxisBinding> Axes |
| GoogolCoreLimits | int MaxAxes, long MaxConfigurationBytes；正有限，count先检测/bytes checked |
| GoogolPulseLimits | long MinPulse, long MaxPulse, MotionValue MaxQuantizationError；闭区间、同unit、误差非负finite |
| GoogolError | GoogolErrorCode Code, string FieldPath, string MessageKey |
| GoogolValidation | bool IsValid, ImmutableArray<GoogolError> Errors |
| GoogolPositionResult | bool IsValid, long? Pulse, MotionValue? EffectivePosition, MotionValue? QuantizationError, ImmutableArray<GoogolError> Errors |
| GoogolValueResult | bool IsValid, double? NativeValue, MotionValue? EngineeringValue, ImmutableArray<GoogolError> Errors |

枚举编号从0依列序：GoogolErrorCode = InvalidArgument, SchemaUnsupported, DuplicateAxis, DuplicateAddress, UnitMismatch, ScaleInvalid, Overflow, QuantizationExceeded, BudgetExceeded, CapabilityMismatch；NativeTimeBase=Second, Millisecond；RateOrder=Velocity, Acceleration, Jerk。未知enum拒绝，不隐式单位/时间默认。失败IsValid=false、值字段全null、Errors非空；成功全部值完整/Errors空。Path为Axes[index].字段/Value/Limits.字段，MessageKey=`Googol.<Code>`，不得错误文字影响hash。

纯函数无ct/Dispose/Drain，不制造task；borrow不可变输入不改，结果每次新建immutable、无static mutable cache。参数校验返回结构化error；hash/factory无法给有效产物时同步抛 `GoogolContractException : ArgumentException`，公开构造 `GoogolContractException(GoogolError error)`，只读属性 `GoogolError Error`，Message=Error.MessageKey；Error不可空。调用方可取得稳定Code/FieldPath，未产生外部resource/task。上游计划构造的MotionCodecException/ArgumentException映射为本异常：schema→SchemaUnsupported、资源→BudgetExceeded，其余→InvalidArgument、path=Plan；不吞运行环境异常冒充合同拒绝。Core数值是换算候选，不设备位置/安全事实。

### A.2 方法与精确算法

```csharp
public static class GoogolModule
{
    public static GoogolValidation ValidateConfiguration(
        GoogolConfiguration configuration, GoogolCoreLimits limits);
    public static string ConfigurationSha256(
        GoogolConfiguration configuration, GoogolCoreLimits limits);
    public static GoogolPositionResult EncodePosition(
        GoogolAxisBinding axis, Asun.Modules.MotionControl.MotionValue value,
        GoogolPulseLimits limits);
    public static GoogolValueResult DecodePosition(GoogolAxisBinding axis, double nativePulse);
    public static GoogolValueResult EncodeRate(
        GoogolAxisBinding axis, Asun.Modules.MotionControl.MotionValue value,
        RateOrder order, NativeTimeBase timeBase);
    public static GoogolValueResult DecodeRate(
        GoogolAxisBinding axis, double nativeRate, RateOrder order, NativeTimeBase timeBase);
    public static Asun.Modules.MotionControl.SimulatorAdapter CreateSimulator(
        GoogolConfiguration configuration, GoogolCoreLimits limits,
        Asun.Modules.MotionControl.SimulationPlan plan,
        Asun.Modules.MotionControl.MotionVirtualTimeProvider time);
    public static Asun.Modules.MotionControl.ReplayAdapter CreateReplay(
        GoogolConfiguration configuration, GoogolCoreLimits limits,
        Asun.Modules.MotionControl.ReplayPlan plan,
        Asun.Modules.MotionControl.MotionVirtualTimeProvider time);
}
```

Validate顺序：limits→schema/controller/revision→axes count 1..MaxAxes→输入index各项ID/frame/unit/address/scale→重复axis/address→canonical实际byte预算。count先拒绝，不先构巨型编码；所有Core函数仅返回按此顺序首个错误（Errors长度1），限制诊断分配。每轴先检查字符串长度，再checked累计编码字节，超限即止，不先形成整份bytes。card/core>=0、axis>=1，ratio各long>0、sign±1、scale revision有效。单轴函数同校验，不接受unit不同/nonfinite。MaxAxes与bytes显式宿主输入，无生产默认。

EncodePosition：binary64符号/指数/尾数展开x=n/d（正规有效53位，次正规指数-1074，-0规范+0）→BigInteger共同分母算origin+sign×x×S→abs DivRem，2×余数比较分母；>则增1，=仅奇quotient增1，再恢复符号→核Int64/MinPulse/MaxPulse→精确有理逆坐标与error=effective-requested→与误差预算的原binary64有理绝对值比较→输出pulse/effective/error。拒绝不返回可用pulse。最终有理→binary64最近偶数，不能把分子分母分别cast double再除。

有理→binary64内部helper确定步骤：约分/取符号→用BigInteger位长和移位比较确定floor(log2(abs(n/d)))→正规按e-52步长、次正规按2^-1074步长做整数DivRem→同偶数舍入→处理53位进位并重核指数→组装bits；溢出为Overflow，-0规范+0。非零rate下溢到0也Overflow，禁止“0速度已停”假象。位置error与预算先精确比较，显示error的舍入不影响准入。BigInteger只BCL，不新算法库。

DecodePosition输入可为fractional encoder pulse，原IEEE有理展开后精确减origin/乘sign/除S再binary64舍入。NativeValue=原pulse规范-0，EngineeringValue=逆值；原整数pulse转double需先确认无损，超过2^53的Int64 Native typed路径内部直接沿同helper，不能先丢位后调用本double入口。finite/最终overflow拒绝，不clamp。

EncodeRate/DecodeRate：order映射导数1/2/3，Second factor=1，Millisecond分别1000/1000000/1000000000；精确有理sign×S×rate/factor或逆式（无origin），最后最近偶数/finite/underflow检查。Encode的EngineeringValue为原请求，NativeValue为转换；Decode相反。Core数学允许signed rate，运动幅度正/范围/envelope由上游Profile，不把本函数可计算性当设备可用。

### A.3 canonical与固定Golden

hash仅Validate成功配置，SHA256小写hex64；UTF-8无BOM严格，ASCII标识不Unicode归一化。S=Int32 little-endian byte length+bytes，I32/I64 signed little-endian。前缀ASCII四字节GG02→S(schema)→S(controller)→S(revision)→I32(axis count)；axes按Axis.Value Ordinal排序，逐S(Axis.Value)、S(Frame.Value)、I32(Unit按Motion A.1编号)、I32(Card)、I32(Core)、I32(Axis)、I64(PulsesNumerator)、I64(UnitsDenominator)、I32(sign)、I64(origin)、S(scaleRevision)。不含UTC/UI/budget、不JSON/hash自含、不约分ratio改变批准身份。logical byte count包括所有prefix/fixed字段，checked cap前止，不等CLR heap上限。

固定向量为§9.1的schema googol-config-v0.2/controller-1/cfg-1/X/machine/Unit0/0,0,1/1000,1,+1,0/scale-1。完整126 bytes hex：

```text
4747303212000000676f6f676f6c2d636f6e6669672d76302e320c000000636f6e74726f6c6c65722d31050000006366672d31010000000100000058070000006d616368696e6500000000000000000000000001000000e8030000000000000100000000000000010000000000000000000000070000007363616c652d31
```

SHA-256=`38f25c4497ea452ce78f9c16885b8d28ad3b6b43b7e9a6b417aabfdb912f4508`。已按字段独立数学复算，不是产品codec运行结果，不能以产品输出反填期望。该域不改变motion-core-v0.2/OperationId。未知schema/字段/enum拒绝，增加字段升版本显式reader；旧未冻结候选Native口无兼容承诺，历史格式/hash原reader保留，显式离线迁移不重写旧身份。

### A.4 Simulator/Replay构造与Owner

Factory顺序Validate config→plan/time非空→ControllerId/ConfigurationRevision精确一致→轴集合/Frame/unit一一匹配/无重复→new上游SimulatorAdapter/ReplayAdapter，由上游构造器校验完整计划schema/hash/Source/预算。ControllerId/revision/轴映射冲突抛本异常CapabilityMismatch/path=Plan.Capability；返回前全部检查完成。分辨率/范围使用完整Capability，不从整数command pulse推导encoder分辨率（encoder可能分数pulse）。失败无产物/task/native；构造不打开设备、不启动异步任务。结果唯一未打开adapter，归调用者/后续MotionSession；time借用不Dispose/Advance，config/plan不可变不修改。

Simulator Source=Simulation，Replay投影=Replay；RecordedCapability/history保原Source/hash，不要求原hash等投影hash。计划Capabilities/Calls/Feedback/FaultSchedule/Interlocks/Replay Operations构造、hash、查询、late、ReleaseFault、持原Task、FailRelease/HoldNative收敛全部沿Motion A.7，不第二动态模型/时钟/账本。config用GoogolCoreLimits，运行用能力与宿主ResourceLimits较小值，不MaxConfigurationBytes代所有heap预算。默认位置分辨率不得猜。

双消费者可同config独立factory/clock/plan/ledger，标Simulation/Replay；数学可构造不证明physical共享卡。工厂只固高配置一致性加上游脚本复用，不宣称模拟ABI/固件/机械动力学。

### A.5 最小Replay/Simulator输入构造与消费

以下合成fixture将§9.1配置延伸为§9.2可用的公开计划，值仅用于软件检查，不批准任何设备Profile。所有record按Motion A.1/A.3/A.7的位置字段构造；表内分组仅省排版，每个构造字段均须给出，不以未声明默认factory代替。两Host各显式new实例，无隐藏窗口/静态状态。

| 输入类型 | 固定字段值 |
|---|---|
| MotionVirtualTimeProvider | originUtc=2026-01-01T00:00:00Z；tick初始0 |
| ResourceLimits | 按上游构造顺序：8,32,16,32,100,256,1048576,4,8,32,4,4 |
| AxisCapability | Axis=X、Unit=Millimeter、Frame=machine、EncoderPositiveSign=1；PositionResolution=.001、VelocityResolution=.001、FollowingErrorResolution=.001；PositionRange=[-100,100]、VelocityRange=[.001,10]、AccelerationRange=[.001,20]、JerkRange=null；Features/HomeModes/WritableConfigurationFields全部空；RequiresServoEnable/RequiresInPosition=false、HardwareLimitIsAuthoritative=false、MaxFeedbackRateHz=100、ReportsPositionHold/UsesControllerStopLock=false |
| AdapterIdentity | AdapterId=googol-replay-fixture、RuntimeFingerprint=fixture-v1、ControllerId=controller-1、Source=Replay（RecordedCapability对应另一个Source=Simulation/AdapterId=googol-sim-fixture） |
| ClockDescriptor | DomainId=fixture-clock、Epoch=fixture-epoch、TickFrequency=10000000、CounterUnwrapped=true |
| MotionCapabilitySnapshot | 上述Identity、FirmwareFingerprint=fixture-fw、BootId=fixture-boot、Generation=1、ConfigurationRevision=cfg-1、上述Limits、Axes=[上述X能力]、Groups空、Clocks=[上述描述]、CapturedAtUtc=originUtc、SupportsIndependentStop=false；SnapshotSha256按Motion A.5的motion-capability-v0.2字节规则算（排自身hash/CapturedAtUtc），不能填全0占位当有效hash |
| ClockStamp | DomainId/Epoch/Frequency同描述，Tick=0、Sequence=1 |
| RawAxisSample | Axis=X；ControllerCommand/EncoderActual=0 mm、Velocity=0 mm/s（MotionValue Unit=Millimeter）、FollowingError=0 mm；Quality=Valid、Frame=machine、CoordinateAssetSha256=null、EncoderPositiveSign=1；Homed/Servo/InPosition/PositiveLimit/NegativeLimit/Fault/PositionHeld均Unknown、ControllerStopLockActive=False（声明无该锁）、HomeSwitch/IndexObserved=Unknown；上述Clock、DeviceReferenceRevision=ref-1、VendorFaultCode=null |
| AdapterFeedback | ControllerId=controller-1、BootId=fixture-boot、Generation=1、Axes=[上述raw]、Clock同上、Source=Replay、Failure=null |
| ReplayPlan | SchemaVersion=motion-replay-v0.2、Duration=1s、Capability=Replay投影、RecordedCapability=上述Simulation原能力、InitialFeedback=上述Replay反馈、Feedback/Interlocks/Operations全部空；PlanSha256按Motion A.5/A.7计划规则排自身hash算，历史记录为空不伪造原操作 |
| StatusRequest | Scope=new AxisScope(null,[X])、MaxAge=100ms、Deadline=1s；§9.2 budget=1s，ct=None仅本同步有限只读例 |

Capability/Plan摘要按上游已给的domain/version/字段递归规则用本测试工程的纯fixture helper构造，不假设上游另有未声明的public hash API；不增加产品codec或平行公共契约。读取结果Source=Replay、actual=0、Homed=Unknown；任何采样为0均不推出安全/settled。time.Advance(200ms)后再读该原帧应Stale；不能靠收到重复帧刷新年龄。readonly零写/零订阅例Dispose后无pending模拟资源。

只读Simulator最小计划：上述能力Identity/反馈Source改Simulation（重新按规则计算能力hash），SchemaVersion=motion-simulation-v0.2、Seed=1、Duration=1s、OpenDelay=0、Capabilities/Feedback/PathValidations/Calls/Interlocks/FaultSchedule全部空，InitialFeedback同样仅原raw证据；PlanSha256重新计算。Open/Read成立；缺脚本Submit零下发拒绝，缺Stop/Drain/Close脚本按Motion A.7返回Unknown/Held，不用只读例Dispose规则伪造其可排空。完整有动作脚本/Close故障例按§10在测试中逐调用填SimulationCall/明确receipt，继承上游资源行为。

此前有限自审/定向验证记录保持：已关闭候选接口泄漏、Relative重复加量、Boot伪造、Stop队列不可达、Exit与停止混同、所有路径立即释放、command/encoder分辨率误推断、空Host类型/异常不闭合、双STA对象共享与客户区误标；本地链接、标题/围栏、Core类型/调用与126-byte数学Golden有效，本轮复用不重审已接收片。0.3.0的实际增量审核/文档验证见§17.4；未创建工程或执行产品C#、Simulator/Replay、真实WPF/性能/HIL，不自动进入实现。
