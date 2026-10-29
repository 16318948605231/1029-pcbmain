# Lighting Control（光源控制能力）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`LC-C1, LC-C2`

- 模块 ID：`IM-009`；来源映射：`PKG-009`。
- 版本：`0.3.1-prep`（2026-10-11 对齐IM-066 0.3.1-prep启动注册、引用epoch及resolver关闭接线；既有Core/UI/LC-S1准备结论保持）。
- 状态：当前全部已批准范围的可决定软件设计已闭合（分类见§15.1）；模块整体实现/集成资格仍`DesignReview/Prep / PreparationIncomplete`。LC-C1与LC-C2均为`ModuleCoreImplementationReady`（仅六项规格准备，既有接收保持）。LC-C2仅限Core及明确Simulation的Adapter/ledger/lease/permit测试端口，不包括可分发新Simulator协议、真实durability/fencing、SDK/HIL、WPF或生产；LC-U为已接收的指导范围及本轮窄补，不提升两种Ready。本文不代表代码、WPF、性能、HIL或生产资格通过。
- 固定基线：C# / .NET 10；Core 无 UI；可选控件采用 WPF / 本机 DevExpress 25.2.3。WinForms、服务和控制台通过相同 Core API 使用能力，不在 Core 引入 WPF 类型。
- 真实复用计划：AOI 多光多步骤采集、钢网/印刷静态及多光采集、工程试验台；调用方拥有曝光、帧、目标和质量解释。

## Core implementation binding

| 切片 | 唯一工程与命名空间 | 边界 |
|---|---|---|
| LC-C1 纯模型/编译/编辑 | `src/Modules/lighting-control/Asun.Modules.LightingControl.Core/Asun.Modules.LightingControl.Core.csproj`；`Asun.Modules.LightingControl` | 不可变模型、能力/单位/范围/互斥校验、规范化、hash、步骤组合复制/粘贴、证据匹配；无设备或存储副作用 |
| LC-C2 会话/模拟/事务端口 | 同一 Core 工程；模拟器在同工程 `Simulation` 子命名空间，不另造通用模块 | 单 Owner、分组控制、工程预览、观察/查询、幂等、排空与恢复；只接明确标记 Simulation 的 Adapter、ledger、占用与许可端口 |
| LC-U 可选嵌入控件 | 后续独立 `src/Modules/lighting-control/Asun.Modules.LightingControl.Ui.Wpf/Asun.Modules.LightingControl.Ui.Wpf.csproj`；`Asun.Modules.LightingControl.Ui.Wpf` | 仅投影和编辑意图；直接引用 Core，不依赖产品页面/ViewModel |
| LC-S1 可选技术持久化桥 | `src/Modules/lighting-control/Asun.Modules.LightingControl.Storage/Asun.Modules.LightingControl.Storage.csproj`；`Asun.Modules.LightingControl.Storage`，PG marshal子命名空间`.PostgreSql` | net10.0，引用本模块Core及IM-066 Contracts/Runtime；PG marshal显式引用IM-066 PostgreSql公开合同，零直接Npgsql/SQL执行入口。精确规格见A.5；不改变Core依赖或设备Owner |
| LC-H 具体 Adapter/HIL | 单独准入，本文不创建厂商工程或写 SDK 实现 | 目标 SDK 映射、光学/触发/热/安全资格；不得借模拟结果关闭实物门 |

Core测试/最小宿主唯一位置：`tests/Modules/lighting-control/Asun.Modules.LightingControl.Core.Tests/Asun.Modules.LightingControl.Core.Tests.csproj`，冻结为`net10.0 / OutputType=Exe`的BCL断言宿主，仅ProjectReference Core，不引入xUnit/NUnit或另建样例Host工程；同一Exe分别执行AOI与钢网消费者。UI测试计划位置：`tests/Modules/lighting-control/Asun.Modules.LightingControl.Ui.Wpf.Tests/Asun.Modules.LightingControl.Ui.Wpf.Tests.csproj`。LC-S1测试唯一位置为`tests/Modules/lighting-control/Asun.Modules.LightingControl.Storage.Tests/Asun.Modules.LightingControl.Storage.Tests.csproj`（net10.0 / OutputType=Exe）；同Exe执行两个独立BCL Host与S-A..H，无WPF/SDK。工程均未由本轮创建；实现前确认权威仓库/分支或批准的可审计代码快照。Core `net10.0`、UI `net10.0-windows`；Core只用.NET BCL，无厂商、视觉、数据库和UI程序集依赖。UI用已有DevExpress程序集，不下载或改版本。

本轮仅允许修改本目录唯一 `DEVELOPMENT-GUIDE.md`；获准代码任务也只能写其指定切片目录。禁止修改其它模块、产品 Shell/Domain/Integration、共享契约/页面、参考快照、AsunImage 内部、入口/进度/会话登记。本模块从设计到返修使用 [模块索引](../MODULE-INDEX.md) 登记的永久会话 `01a10306-e930-7c21-8684-a996e3df4c56`，不派生会话或子代理。

LC-C1不实现accepted、设备生命周期或durable ledger；主控已按DEV-GOV-010 §3.1接收其六项纯Core规格，状态为ModuleCoreImplementationReady（规格准备），本轮不开始实现。LC-C2同样已接收为ModuleCoreImplementationReady，仅限Core及明确Simulation的Adapter/ledger/lease/permit测试端口；附录A只定义可模拟的事务语义。可分发新Simulator协议不在当前获批范围，也无独立发布消费者，不作为当前设计欠账；真实存储durability/保留期、跨进程fencing、SDK/HIL、LC-U实现与产品资格另按§15.1分类，不随两片规格接收成为Ready。

## 1. 目的、边界与完整能力

模块负责设备能力快照、稳定通道身份、场景编译、分组控制、触发配置、有限执行/工程预览、逐步读回与观察、热/互斥限制、停止/Blackout、未知结果查询、关闭/资源归还和结构化审计。全部能力有无 UI 入口；UI 不承担唯一校验或隐藏初始化。

调用方负责设备用途与权限、物理占用服务、持久化部署、相机曝光与帧关联、目标/FOV/板身份、配方批准、重拍、PLC/安全链、工艺判定与质量放行。Core 消费这些边界的公开证据，不引用其私有对象，不替宿主驱动相机、运动、PLC。停止/Blackout 是普通软件恢复能力，不是急停、安全 PLC 或硬件互锁。

不把 ACK、寄存器零、颜色名称、数组下标、图像暗、采集完成、SDK 返回或进程退出当作物理安全事实。输出事实、模拟事实、候选草稿和宿主质量决定分开。

### 1A. 新架构适配要点

**架构门禁**：光源 Core 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；只有可选 UI 切片可引用，Core 不得反向引用。HALCON 不适用于本模块核心（§2 已明确）。

**Blazor/Web**：Web 端只展示通道状态、已应用场景 hash、互斥锁状态；写通道配置必须经已授权维护接口，不经浏览器。

**AI/HALCON**：光源控制是设备事务，不执行视觉算法；双跑 CI 不涉及本模块。

## 2. 依赖与 HALCON 适用性

Lighting 是设备事务，当前无图像算法；均匀性、弱信号、饱和、遮挡评价属于 image-quality，参数搜索属于 imaging-optimization。它们只提供引用和候选，不在本模块训练或评价影像。相关缺证只阻断相应用途，纯编译不等待 HALCON/硬件。

复用 HALCON 26.05 本地手册既有结论：`add_scene_3d_light` 只为 `scene_3d` 渲染添加光；`set_framegrabber_param` 只设采集接口参数，两者不是物理 LED、频闪或 Blackout 的控制端口。HALCON 算子若被外部质量模块采用，经 `ImageLibDotNet.cv2` 使用；本模块不另接 `HOperatorSet`/`halcondotnet.dll`，不重复核验薄封装是否含算子，不扫描内部。本文无 ROI/粗精视觉路线和 AI 推理后端，算法性能比较在其唯一所属模块进行。

注入端口仅为本模块定义的 `ILightingAdapter`、`ILightingLedger`、`ILightingLeasePort`、`ILightingPermitPort`、`TimeProvider`。前三类运行依赖不能落入 LC-C1。不存在静态 CurrentController、隐藏窗口、产品数据库或 Shell 单例依赖。

## 3. Owner、身份与迁移事实

每物理控制器一个 `LightingController` Owner，所有写命令串行；不同控制器可并行，查询读取不可变快照。Adapter 单独拥有连接、SDK 句柄和回调订阅；Controller 拥有状态/operation/队列；ledger 拥有本模块操作记录的持久化技术实现；lease port 是排他占用权威，不能用本地 actor 推断跨进程独占。宿主不得同时绕过 Controller 写相同设备。

所有运行请求绑定controller/device/boot/generation/capability hash/session/operation/request hash和expected stateVersion；状态变化递增stateVersion。Generation由Controller在每次新的Open尝试前checked递增，传给Adapter.Open；成功能力快照必须回显同值。能力/固件/连接变化先锁存Hold、使旧场景失效，只在安全Close后新Open产生新generation；不存在自动重新发现并继续原Emit。设备没有boot标识时Adapter明示缺少跨重启对账资格，禁止猜boot未变，真实路径保持Hold；模拟boot由脚本显式给出。

### 3.1 DZ-XVision 与 AOI 来源中已采纳的经验

DZ-XVision 20261004 只读快照提供串口、序列号和 IP 连接经验；端点是宿主保护配置的引用，不在 Core 写地址/波特率。单通道与固定组宽（来源出现 2/4/8/16）、UDP 完整帧和 OPT 顺序表能力由目标能力快照声明，不变为平台默认。通道成员/序列深复制为运行快照；白光通道颜色相同仍按各自 ID 保留。XOR/CRC/ACK 是传输证据，不能升级为物理事实。曝光和通道组合分离；审计保留 old→new、operation、能力/场景 hash 和恢复动作，不复制旧 UI、MES/条码或工艺流程。

PCBA-AOI 20261006 来源提供当前会话内复制/粘贴步骤通道组合经验，保留目标步骤身份、曝光与触发时序，成功后废弃旧 Actual；其五通道仅作合成样例，不写进能力上限。来源中的具体 OPT/客户限值不迁移。

## 4. 工程单位、能力与场景编译

附录 A 是公开字段与方法的唯一声明；本节给出处理规则。所有集合使用 `ImmutableArray<T>`；构造时拒绝 default 集合、null 元素和重复 ID。入站不接收任意字典或双精度 NaN/Infinity；decimal 本身无这些值，外部文本/浮点适配遇到非有限或超出 decimal 值必须拒绝，不强制转零。

| 参数 | 单位、范围及来源 | 规则 |
|---|---|---|
| 强度 | Percent 为 0..100，Milliamp 为 mA，DeviceUnit 为设备刻度，WattPerSquareMetre 为 W/m²；且必须落在通道自身 Min/Max | 单位严格相等；百分比不除以100后当 mA，设备刻度不当测量值。辐照度设定仅在能力给出已验证转换的 CalibrationHash 时可用 |
| 关闭 | `Enabled=false, Requested=null` | Off 是明确禁用；不把 value=0 视作禁用或物理黑场。Enabled=true 必须有非空设定和单位 |
| 量化 | Min 为网格原点，Step>0，Min<=Max；能力声明是否可预装 | `Reject` 要求精确网格；`Nearest` 用 decimal 的 midpoint-to-even，`Down` 向较低网格取整。先检查原值范围再量化，量化后重验，不钳位；量化差异逐字段输出。所有算术 overflow 返回错误 |
| 时间 | API 为 TimeSpan ticks，1 tick=100ns；设备分辨率见 TickStep/Min/Max | 不宣称任意微秒均可表示；脉宽必须>0，模式=Continuous 时 Width/Period=null、Count=0；SoftwarePulse/HardwareTrigger 必须有 Width>0、Count>=1 |
| 频闪占空 | Count×Width/Window<=通道 MaxDuty，Width<=Period，Delay+(Count-1)×Period+Width<=Window | 使用 checked ticks/decimal；单操作校验不能替代滚动热预算。HardwareTrigger的Period/Count是许可约束，不能由主机据此推定外部脉冲实际发生 |
| 场景时间窗 | 步骤按 Ordinal=0..n-1，Window>0；连续模式亮光也必须有限 Window | Core 只冻结需求时间，不用 Task.Delay 声称硬件稳定/精确触发；CameraExposureReference 是不透明关联，不由模块解释曝光 |
| 互斥/功率 | GroupCapability 的成员、MaxEnabled、MaxPowerWatts；Channel 的 CertifiedMaxPowerWatts | 保守功率上界为每个 Enabled 通道的认证最大功率求和，不按 Percent/DeviceUnit 线性猜功率。限值缺失时纯草稿可诊断，但 Emit 不能编译成功 |
| 读回/用途 | RequiredReadback、MaxReadbackAge、各通道 ReadbackTolerance；RequirePhysicalBlackout | 能力缺少本用途证据为 Unsupported；无公差不得默认经验公差；寄存器精确比较可显式提供0 |
| 资源 | MaxSceneSteps/MaxChannels/MaxPayloadBytes，运行队列/事件/ledger/观察/排空预算 | 由宿主显式提供，均有界；本文不编客户数字 |
| 默认值 | 只有类型语义，无默认设备强度、通道数、触发模式或 deadline | Off 可由草稿显式构造；所有执行参数由调用方给出 |

### 4.1 唯一编译顺序

1. 检查 API 版本、资源预算、输入集合大小，拒绝超限后才遍历/复制；检查 binding 与能力精确匹配、唯一稳定身份。
2. 只允许目标能力完整 OwnedChannels 集合：每步含全部拥有的通道，未用通道显式 Off；禁止“省略即保留旧亮度”。完全共享控制器未声明隔离分区时不能单消费者只写其自认为属于自己的通道。
3. 校验 Ordinal/StepId、模式/组宽/分组顺序、单位/数值/时间；量化并记录差异。执行读取 `NormalizedScene`，原草稿不在途中修改。
4. 对全部步骤检验互斥、功率上界、脉冲组合、触发延时/窗口和能力支持；频闪缺热限制拒绝。Compile 不发设备命令，滚动热/互锁由运行许可进一步确认。
5. 空步骤/空完整通道集合为 SceneInvalid；全部 Off 只可编译 `ConfigureOnly`，不允许 Arm/Execute 宣称曝光成功；`Emit` 至少有一个启用通道。
6. 生成规范字节与 SceneHash。参数、通道成员、单位、时间、binding 或用途改变均得到新场景身份；UI 清旧 Actual，运行场景失效、需新 Apply/Arm。规范化不是生产批准。

预算预检查不先序列化整个输入：MaxSceneSteps/MaxChannels/MaxPayloadBytes均须>0，能力通道数及每步通道数不得超过MaxChannels。先查集合Length、string.Length（字符数已超过字节预算则直接拒绝），再逐字段用strict UTF-8计数并checked累计长度前缀/存在标志/固定字段；累计超限立即停止，随后才复制、排序和分配规范字节。MaxPayloadBytes分别约束完整能力编码、场景编码和运行请求编码，不仅约束裸通道值；引用、ID、组成员等也计入。嵌套集合须同时受完整编码预算限制，不能因每组宽合法就接收无限组。运行重编译使用不宽于RuntimeLimits.Compile的CompiledLimits，不能由调用方自填更大预算绕过运行限额。超限统一LIGHT_RESOURCE_LIMIT，不截断或计算超限输入的hash。

量化以decimal的整数系数/scale转为相同十进制尺度的BigInteger作精确除法：d=value-Min，s=Step；DivRem(d,s)得到q/r，Reject仅r=0通过，Down取q，Nearest比较2r与s，等于时取偶数q。结果为Min+q×Step，checked转换回decimal并重验范围；无法精确表示或算术溢出返回LIGHT_ARITHMETIC_OVERFLOW。不得以已四舍五入的decimal除法商判断网格或中点。Max不要求位于网格，原值未越界但Nearest落到Max之上仍拒绝；时序网格用整数余数，计算中间量溢出即拒绝。

### 4.2 确定性编码与参数建议

本模块冻结 `lighting-binary-v1`，不用 JCS 的 double 编码承载精确 decimal/ticks，也不修改其它模块资产摘要规则。使用 strict UTF-8（非法 surrogate 拒绝）；string 为 uint32 大端字节长度+原始 UTF-8，无 trim/大小写折叠/Unicode 重写。非空 ID 按 ordinal 比较。集合先写 uint32 count；通道按 ChannelId ordinal 排序，步骤按 Ordinal；nullable 用单字节0/1存在标志；bool 用0/1；decimal 用 invariant `G29` 文本，零统一为 `0`；时间/int64/int32 用大端整数，枚举用本文固定数值 int32，byte数组为长度+内容。SHA-256 小写64hex。

编码标识为上述string编码的固定文本`lighting-binary-v1`，紧随int32域标识：Capability=1、Scene=2、Open=3、Submit=4、Close=5，随后才是下文列出的其余字段。防止不同类型对象落入同一摘要域。该布局仍处于首次实现前准备，本版不接收先前未带域标识的准备字节；已存在的历史身份继续按其原编码只读验证。

Scene 规范字段固定顺序：编码标识、ApiVersion、binding五字段、Purpose、步骤集合；每步为 StepId、Ordinal、Window ticks、ExposureReference、Trigger字段（Mode/Width/Period/Count/Delay ticks/SourceReference）、通道集合（ChannelId/Enabled/Requested unit/value）。CapabilityHash编码顺序为编码标识、ApiVersion、Binding的ControllerId/DeviceId/BootId/Generation（排除CapabilityHash自身）、Channels、Groups、TriggerModes、TriggerDelay、Simulation、FirmwareReference、SourceReference；嵌套record按附录A声明字段顺序，ScalarRange为Min/Max/Step，Intensity统一Unit在前Value在后，TickRange为MinTicks/MaxTicks/StepTicks。通道按ID、读回种类/触发模式按枚举值、groups按GroupId排序，组成员保留协议顺序，SupportedWriteWidths升序。运行Submit的CommandHash固定顺序为编码标识、ApiVersion、LedgerOperationKind、Binding五字段、SessionId、OperationContext（OperationId/IdempotencyKey/ExpectedStateVersion/ActorReference/PurposeReference/Budget两个期限ticks）、SceneHash（无场景为null）、CompiledLimits三字段/Quantization（无场景为null）、Usage.ProfileHash；StepId包含在SceneHash中，安全命令无额外步骤字段。同key改预算/参数也冲突。不把墙钟、Actual、错误文案或局部UI顺序写入hash；旧版本字节按原规则验旧身份。

上述字段序列均在编码标识后插入对应域标识；SceneHash独立nullable string编码，CompiledLimits/Quantization视为一个nullable块：有scene时写1再三个int32限额及int32策略，无scene时只写0。Usage.ProfileHash、SceneHash/CapabilityHash及编码结果hash须为小写64hex；ComputeCapabilityHash的输入hash可为空且不被编码，PendingOpenIdentity只限Open接纳和历史查询，不能进入场景。Emit的每个步骤都须至少一个Enabled通道，全Off步骤仅ConfigureOnly可用，不把等待/暗帧偷偷编码为发光步骤。

模块只建议合法量化值并输出 `NormalizationChange`，不从影像自动调亮、不排序多个优化候选。外部参数建议须有候选 ID、算法版本、输入证据/来源、能力/场景 hash，由宿主选一个作为新 Draft；多候选未选择拒绝执行。重跑同输入/量化策略必须等价；即使建议在域内，也不隐含批准，不静默更新生产 frozen scene。

宿主在提交前用附录A的EncodeOpenRequest/EncodeCommandRequest/EncodeCloseRequest取得`CanonicalLightingRequest`并保留Hash/Bytes；Controller使用同一编码，receipt丢失或接纳查询超时仍能用原OperationId/Hash查询。编码方法只有纯形状、版本、枚举、预算与字段编码校验，不核设备当前状态/实时许可；非法输入返回Value=null和结构化Faults。请求重新编码不能产生新的ID/key/预算，场景编码与运行编码分别有界。

## 5. 公共 API、最小 Host 与调用顺序

公开 API 唯一见附录 A；不得继续实现旧的无字段 factory 示例或为未来功能另造接口。Core 构造无设备副作用；`Compile`/`CopyCombination`/`PasteCombination`/`CompareEvidence` 是同步纯计算；Controller 运行调用均异步。编辑草稿与设备状态分离。

LC-C1 无 UI 最小 Host：引用 Core → 构造明确标记 Simulation 的五通道 CapabilitySnapshot 与 Limits → 构造两个 SceneStep/SceneDraft → Compile → 检查 Rejected/Changes → CopyCombination/PasteCombination → 再 Compile → 比对 Hash；不需要静态配置、Dispatcher、数据库或 Adapter。构造类型与集合按附录 A，不使用不存在的 `LightingScene.Create`/`session.Id` 等假 API。

### 5.1 LC-C2有界组合根与预持身份

组合根在调用任何设备方法前占用一个宿主恢复槽；一个controller仅一个槽，槽已占则拒绝新实例/Open。本页两个测试consumer合计最多两槽，但§11.1使用相同sim-light身份的AOI/钢网必须串行并复用同controller键，前一个槽未安全退出时后一个不得启动；并发反例须显式使用不同controller/device能力并重算binding/hash。实例、任务或占用未知时不扩容、不驱逐。真实宿主槽容量须显式配置，不把本地槽当跨进程lease。槽是测试/宿主私有生命周期记录，不增加Core公开API；保存Controller、原Adapter引用（只能由Controller关闭）、原Open请求/DisposalOperation、Pending身份/规范bytes/hash、最后可信Capability/Binding/Snapshot、所有已发operation的固定ID/key/hash、在途Task、最新回执及有界异常诊断。操作槽数量由CompileLimits.MaxSceneSteps对应实际单步链限定：每步Apply/Arm/Execute各一次，加Open/Stop/Close；追加前先核额度，满时走finally，不生成新亮光身份。

先构造Open请求及不同ID/key的DisposalOperation（§11.1），用`LightingCore.EncodeOpenRequest(openRequest, runtimeLimits.Compile)`核成功，预持`PendingOpenIdentity(openRequest.ControllerId, openRequest.DeviceId, openRequest.SessionId, openRequest.Operation.OperationId, encoded.Hash)`。OpenTask和编码必须留在原槽，即使等待取消也不丢任务。每次Submit前以公开`EncodeCommandRequest(command, openRequest.Usage.ProfileHash, runtimeLimits.Compile)`保存其原请求/hash；Close前`EncodeCloseRequest`保存原Close hash。Close使用已预持DisposalOperation，安全lane忽略其旧version，Dispose会加入同一个Close单飞；不能异常后换ID/key/预算再发一次。任何编码失败都记录错误并进入下一层finally，不直接跳出整条资源收尾链。

### 5.2 两个consumer共用的异常收尾链

以下是宿主控制流规格，`记录/有限等待/尝试`为宿主私有处理说明，不是新增Core方法或已编译样例。每个尝试捕获并保留异常/回执，不覆盖首个消费异常；`Task`由每个ValueTask仅一次`AsTask()`取得并保存，逾时只结束观察，任务仍由原槽持有。组合根持有链接调用方ct的businessCts，businessCt为其Token；finally由宿主请求businessCts取消，使原Open/Execute进入Owner逻辑收尾，不能依赖用户稍后取消。observerCts独立管理本waiter。安全Stop/Close传CancellationToken.None，查询用独立有限queryCt；所有等待仍受原API预算和§12 wall保护，不能用取消业务token跳过安全调用。businessCts/observerCts在相应Task真实退出后才Dispose，未知则同原槽保留。

```text
占原controller恢复槽；预持Open请求、Pending身份、DisposalOperation及op/hash
构造LightingController并保存；未转交Controller前构造失败由原组合根有限Dispose Adapter
try
    保存OpenTask = Controller.OpenAsync(openRequest, businessCt).AsTask()
    有限等待OpenTask；回复未知只Controller.QueryOpenAsync(pendingIdentity, queryCt)
    将每次有效回执写回槽；仅同session、已验证Capability/Binding、Ready才继续
    foreach consumer提供的单步草稿（步数在原额度内）
        LightingCore.Compile；检查Value/Faults/Changes；消费异常进入finally
        取最新Snapshot.StateVersion，编码并保存Apply，再SubmitAsync
        核Configured；编码并保存Arm，再SubmitAsync；核Armed
        预持Execute command/ID/key/hash（当前版本）
        保存observeTask = Controller.ObserveStepAsync(
            StepQuery(binding, session, executeId, sceneHash, stepId, waitDeadline), observerCt).AsTask()
        try
            保存executeTask = Controller.SubmitAsync(executeCommand, businessCt).AsTask()
            并行观察observeTask与executeTask；只有有效起点才让consumer消费观察
            消费者异常、Execute/观察失败、取消或等待超时均退出本步到外层finally
            未知Execute只QueryOperationAsync(OperationQuery(binding, session, executeId, originalHash))
            核原Execute回执、黑场/冷却与operation资源，再进入下一步
        finally
            请求observerCts.Cancel，仅解除本waiter；捕获Cancel回调异常并保存尚未退出的observeTask
            观察Task的失败/取消不丢弃；此处不无限await，继续外层安全收尾
finally
    请求businessCts取消，登记异常，不把取消当native排空；继续以下所有finally
    try
        若尚未有正式Binding：有限QueryOpenAsync原Pending，保全返回身份/能力/任务
        独立捕获Query异常；槽原来已有正式Binding时不查Pending，也不清空该Binding
        若已有同session正式Binding：预持固定Stop command/hash，SubmitAsync StopAndDrain
        捕获编码/Query/Stop的异常、未知或超时；均保留原槽，不阻止下一层finally
    finally
        try
            仅原槽已有正式Binding时，构造CloseLightingRequest(binding, session, DisposalOperation)
            编码并保存后CloseAsync；已有CloseTask则只加入/查询原任务，不创建第二个Close
            没有正式Binding：不构造Close、不Submit、不Perform；保持原Open内部cleanup
            捕获Close编码/调用/观察异常或未知；均不阻止最外层Dispose尝试
        finally
            尝试原Controller.DisposeAsync；保存DisposeTask和CleanupException原身份
            未知半开且无Binding时Dispose仅观察原Open内部cleanup，超时仍留原Owner
            有限观察剩余observer/execute/open/close/dispose任务；异常均登记，未知不释放槽
```

恢复槽只接受同原session/完整Binding的回执，不以当前另一个session覆盖；QueryOpen仍Pending时不能“借”另一个成功Open的Binding。外层catch由组合根记录消费/编译/编码/查询异常并在finally完成后报告失败，不让异常处理本身发送设备命令。Stop只是降低输出风险，不代表lease归还；必须Close的Session资源Drained/Released均确认、原Dispose成功、所有本宿主持有任务真实完成及awaiter/回调退出才具备正常返槽条件。任何本轮失败、task/native/ledger/lease未知均不返槽，原实例和诊断进入恢复列表；后续显式恢复只在同槽继续QueryOpen/QueryOperation/GetSnapshot及已有安全单飞阶段，确认上述事实后才能释放槽，不自动换Owner。处理失败时继续其它consumer只能使用另一独立controller槽，不能对同设备重开。

AOI按§11.1将多步编辑草稿拆为单步Emit，钢网直接给单步草稿，两者都执行上述try/finally、身份预持与观察Task路径，差异仅是草稿/曝光引用；不能为钢网省略Apply或资源收尾。独立工程Preview也从Ready/Configured提交已编码单步Preview，用相同恢复槽/观察/嵌套finally，不先Apply/Arm；其内部顺序与边界见§6.1。

每个 Apply/Arm/Execute 是不同 operation/key，回放已完成结果先于 stateVersion 检查；新请求只在绑定仍相同、预期版本匹配时接纳。非法输入走 RequestRejected，无 OperationAccepted、无设备调用、不改 stateVersion。运行队列限额在 durable accepted 前预留，取消未接纳请求只删除本地等待，不声称任何发光。

构造后、首次Open前GetSnapshot返回Closed/Unknown/version0、Binding=null、SessionId为空、ApplyDisposition=None，仅为未绑定投影；不能用于命令。Open的预发现查询使用独立PendingOpenIdentity(controller/device/session/operation/hash)，不把boot/hash空、generation0伪装成Binding；它只允许查该Open的历史ledger进度。找到记录时核controller/device/session/op/hash，返回已保全的正式Binding，不要求宿主已收到丢失的Open回复。其余历史Query用记录关联的完整Binding；任何查询身份都不授权新设备动作。

测试Exe的两个host共享同一DLL和公开端口形状，各自实例化测试工程内的`ScriptedAdapter`、`MemoryLedger`、`ScriptedLeasePort`、`ScriptedPermitPort`和`ManualTimeProvider`；这些是测试夹具，不增加产品公开factory或可配置运行脚本协议。构造输入按§11.1，夹具通过barrier控制迟到/不返回/续租/事件而不依赖用户环境；正常与故障脚本的动作、证据、时间与预期沿§11–12，LC-C2的Simulator即此边界下的可模拟能力。当前没有要求非测试消费者装配并发布这些夹具，不欠一个产品Simulator factory或新脚本协议。若将来明确批准独立发布用途，由本原会话限定新切片的消费者、公开构造/版本/脚本持有/有界恢复及测试，再作准入；本轮不先造通用DSL、网络Simulator或重做适用研究。

## 6. 状态、读回证据和事件

### 6.1 状态与命令可执行性

连接状态与光学状态是两条事实：`Closed/Open/Ready/Configured/Armed/Emitting/Cooling/Blackout/Faulted/Hold/Disposed` 为会话状态；`Unknown/CommandedOff/RegisterOff/PhysicallyOff/PhysicallyOn` 为输出证据。Closed 不证明物理 Off。Blackout 状态只在当前绑定的可信物理黑场确认后进入，否则 Hold；业务可读回寄存器，但不得将其命名为 BlackoutConfirmed。

| 起点与命令 | 固定动作与到达条件 |
|---|---|
| Closed → OpenAsync → Open → Ready | 获排他lease、Adapter.Open返回能力、停止外部触发并安全关闭输出，按Usage.RequirePhysicalBlackout/BlackoutLimits确认；冷却未完为Cooling，缺证为Hold，不自动Arm |
| Ready/Configured → Apply → Configured | 冻结场景；仅能力声明 DisabledPreload 且已确认禁用时可写预装并核寄存器。不能禁用预装的控制器在 Core 保存配置，完全不写亮度，回执标 Deferred；Actual 未观察 |
| Configured → Arm → Armed | 核能力/场景版本、当前许可、互锁/温度/滚动热/时钟与触发配置；外部触发线必须先被硬件门控，配置脉宽不等于允许线立即触发。确认门控失败拒绝 Arm |
| Armed → Execute | 再核实时许可与温度/预算，才允许 enable/trigger。Deferred 的亮度写在该操作内进行；软件频闪/硬件序列按声明路线，不拆组绕限制 |
| Ready/Configured → Preview | 单步Emit、可信当前黑场、独立工程用途许可；同一Preview operation内部按Apply→Arm→Execute语义串行，不产生三个子operation/key，不借用旧Armed或生产许可。任一阶段失败即收尾 |
| Execute 在途 | 只收到命令/寄存器回应时 PhysicalEffect=MayHaveStarted；不发布虚构 EmissionStarted。可信物理起点到来才为 Emitting，结束证据/时间预算到期进入收尾；单靠主机计时不能证明物理结束 |
| Execute/Stop → Cooling/Blackout | 先关闭/禁触发并验证，再按设备给出的冷却就绪证据恢复 Ready；不能先等待冷却再关连续亮光。旧 Armed 总是失效 |
| Faulted/Hold → 恢复 | 保留 binding/占用/旧操作，只查询或安全收尾；先确认原session黑场/排空/native Close/lease归还，才能显式新session Open/新generation/重新Apply/Arm。当前无绕过Close的重连API，不自动重放 |
| Close/Dispose | 先停止准入与触发→关闭输出→确认黑场→所有操作排空→native close→lease release，全部确认后 Closed/Disposed。失败锁存 CleanupFailed/Hold，原实例仍可 Query |

Closed 没有连接时Blackout不能承诺驱动物理输出，返回Unconfirmed；原实现假设有独立安全通道时须由该适配切片另行提供受保护端口和证据，当前不凭空增加SDK能力。直接从Ready/Blackout提交Execute和无重新Arm的重复Execute均禁止；Preview只通过其内部布防步骤进入Emitting。

Apply接纳新场景时清旧Armed/Actual；草稿编辑和Compile本身不修改正在运行的Controller，只有新的合法运行请求改变其状态。Execute/Preview/Stop/Blackout收尾均清ArmedOperationId及活动SceneHash，成功确认黑场且CoolingComplete后回Ready，冷却未完则Cooling；不恢复先前生产配置。Preview后生产必须重新Apply/Arm。Armed/Emitting/Cooling时新Apply/Preview拒绝为StateConflict；Cooling只允许查询和安全动作，Controller按许可轮询确认冷却后转Ready。Preview事件的OperationId始终是Preview的ID，观察接口的ExecuteOperationId字段也可绑定此Preview ID。

Apply的Deferred通过`SessionSnapshot.ApplyDisposition`明确返回，值为None/Deferred/DisabledPreloadVerified；只要任一写入分区不能禁用预装就整体Deferred，不混合预写一部分、延期另一部分。Configured只证明已冻结/可安全预装，Emit资格仍在Arm/Execute。Blackout为黑场确认后的收尾中间状态；无锁存故障时转Cooling/Ready，已有Hold/Faulted时继续锁存，不因一次黑场证据抹掉ledger/Owner故障。StateVersion以session为域，初始0，actor每发布一次不同的状态事实快照递增1，包括接纳、有效证据、状态和资源变化；重复同EvidenceId、Rejected、Query、历史回放不增，溢出锁存Hold/ArithmeticOverflow而不回绕。

### 6.2 读回匹配与观察

TransportReceipt、RegisterReadback、ElectricalMeasurement、OpticalMeasurement 四种 EvidenceKind 不用“越大越真实”的枚举排序。EvidenceSubject 分开 Setpoint/Enabled/EmissionStart/EmissionEnd/Blackout/Temperature。同一证据不能跨 subject 证明其它事实。记录 `EvidenceId/Binding/OperationId/StepId/SceneHash/ChannelId?/Unit/Value?/Enabled?/ClockId/ObservedTicks/Frequency/EvidenceKind/Subject/SourceReference/Simulation`。

CompareEvidence 先核完整身份/subject/时间来源，再核单位、字段是否存在、观察年龄与阈值，最后核 requested/actual 差异。RegisterReadback 的值是 `RegisterActual`，绝不标成光学强度；光学实测标 `MeasuredOutput`。ACK 无数值为 NotObserved；旧读回、跨步、跨代、时钟不可比较均拒绝。没有噪声/公差来源，不用“近似零”判关灯；Blackout 的阈值及受信来源由用途策略/物理 Profile 确认。

受信不是SourceReference非空：Usage.TrustedEvidenceSources由宿主用途Profile列出精确Kind/Subject/ChannelId/SourceReference/CalibrationHash组合，Controller先匹配此允许表，再将匹配来源填入EvidenceRequirement。CompareEvidence只核指定来源的一致性，不颁发来源信任。测量与设定比较时CalibrationHash必须非空、同时匹配允许表与该通道能力；不需要转换的寄存器证据两者均为null。Blackout不与设备刻度比较，只按对应物理单位的BlackoutLimit与批准测量来源判定。外部引用对应传感器、资格及覆盖范围由宿主保管，不能由调用者自由填入一个相同字符串就取得实际来源资格；Adapter仍须绑定获准的物理来源。

运行所有ClockStamp使用RuntimeLimits.ClockId及注入TimeProvider.TimestampFrequency的同一单调epoch；ClockId在进程/时钟重启时必须变更，宿主配置Adapter/lease/permit到该域。原始硬件时钟仅在适配切片完成资格映射后可用于此域，SourceReference保留其映射证据，不能用回调到达时间冒充物理发生时间。Now.Ticks>=ObservedAt.Ticks且差值/Frequency<=MaxAge（用BigInteger交叉乘比较，MaxAge>=0）才当前有效，未来时间拒绝，域/频率不等为ClockMismatch。历史起止事实按其入站及执行窗口时的校验保全，不因后来Query时间经过而改历史结果；新的Observe仍按当前MaxReadbackAge返回Unknown/Stale，不能凭旧起点确认此刻发光。每步窗口锚点在实际发光动作前记录为单调时间，截止为锚点+Window且不晚于Request到期点；窗口到期开始安全关闭，不作为结束证据。EmissionEnd须同step在Start之后，起止落在该步许可窗口内；硬件多步无法提供资格时间映射或逐步证据时保持Unknown/Unsupported。

多步骤硬件序列若只能读当前步号/整表，不足以证明各步实际发生。仅声明支持单步观察的设备，可逐个单步场景运行并由宿主串行采集；不能承诺原子多步同步。序列表能力缺失必须 Unsupported，不退回软件延时伪造硬件精度。

ObserveStepAsync 可在 Execute 前/在途中登记，绑定确切 execute operation/step/binding/scene hash；已有可信起点立即返回相同事实，无起点则有限等待。达到 MaxObservers 拒绝，不影响设备；取消/超时只释放本 waiter；过期事实/未知起点明确 Unknown/Unsupported。返回起点不承诺当前仍发光、剩余窗口或相机同步合格；宿主另核窗口与时钟域，不在 Core 驱动相机。

### 6.3 生命周期、事件与所有权

事件为统一 `LightingEvent` 载荷，不在设备锁内调用宿主。接纳前：RequestReceived→RequestRejected。已接纳命令：OperationAccepted→SceneValidated→可选的 RegisterApplied/ReadbackVerified/Armed/TriggerIssued/受信 EmissionStarted/StepActualRecorded/EmissionEnded→LogicalCompleted|LogicalFailed|LogicalCancelled→Draining→Drained→ResourcesReleased→唯一 OperationCompleted|OperationFailed|OperationCancelled。事件是条件序列，不强制每个 Apply 假造 Emission/Cooling/Blackout。

ResourcesReleased 的 Scope=`Operation` 只归还该命令的回调、waiter、临时 buffer；设备连接和会话排他 lease 保持到 Close。Close 的 Scope=`Session` 只有 native close 与占用归还都确认才发布。Applied/Armed 成功不释放持有设备的会话。排空未知保持 Draining/Hold，没有终态或 ResourcesReleased；Query 可以返回 RunningUnknown，不发假 terminal。物理事实 Unknown 与资源事实未知是不同字段，即使资源已释放也不得改历史物理结果。Execute/Preview必须有本Usage要求的各步事实与最终物理黑场才Completed；缺起止或黑场为Failed/MayHaveStarted/Hold（若操作资源已排空可终结其Failed，但session仍保留）。Blackout/Stop只回读到寄存器也不能Completed为物理关闭成功。

## 6A. 双视角反例与能力闭合

### 6A.1 输入/工艺接入视角

| 场景 | Core 处理及输出断言 |
|---|---|
| 正常五通道，其中两个不同白光 | 两白光独立 ID/值；两个步骤完全通道集合，可不同曝光引用；顺序不变，hash对成员排序稳定，不以颜色合并 |
| 空/null/全 Off | null/default/空步骤拒绝，Off与0区分；全Off ConfigureOnly合法，Emit拒绝，无设备写入 |
| 大规模 | 准入前检查步数/通道数/字节预算；checked算术；上限处通过、上限+1拒绝，不截断通道/步骤“成功” |
| 弱信号/遮挡/反光/噪声/退化 | 本模块保存照明证据；宿主质量拒识不改Actual、不自动增亮或重拍，不由图像黑证明Blackout |
| 多建议/参数改变 | 未选一个候选不执行；更改单位/亮度/窗口/能力产生新hash和旧Armed失效；超限建议拒绝，不钳位 |
| 量化/不同单位 | 合成 min=0、step=2、max=100 的 DeviceUnit，5按Nearest→4、7→8，Reject拒绝，max+1拒绝；Percent=50不等于50mA |
| 多通道/组事务/互斥 | 完整集含Off；组宽不支持拒绝。单白与双白颜色不参与互斥判断；互斥成员同时Enabled拒绝，即使数值0 |
| 回读缺失/旧值/局部写 | 先停止继续写→记录逐通道→关闭→对账；不发布Configured或假光学稳定；原草稿不被部分Actual覆盖 |

### 6A.2 时序/故障接入视角

| 场景 | 处理与验收断言 |
|---|---|
| 同controller两个写、查询并发 | 一个actor，精确CAS；跨controller不阻塞；查询无写入，快照带version |
| Apply抢占Blackout、预装不能禁用 | Blackout安全lane先关闭准入/失效Arm；不并发写同SDK，等在途返回后优先执行。Apply deferred不会预先点亮 |
| 重复key/回复丢失 | 同key/hash返回原operation；异hash冲突；Execute触发计数不增加；operation不找到不能推断未发生 |
| 取消/超时/迟到回调 | 取消后安全收尾用独立cleanup预算；SDK在途不free；跨generation回调只隔离诊断，不回填新操作 |
| 断连/掉电/ledger损坏 | 已发输出保持MayHaveStarted/Hold，占用不自动归还；只允许查询/安全关闭，受保护恢复须先关闭旧Owner，旧scene全失效，不重放亮光 |
| Close/native释放失败 | 临时资源释放不等于session关闭；原实例/lease保留，重复Dispose不假成功，不重复未知native Close |
| 日志满/事件队列满 | 关键事实先保全，无设备锁阻塞UI；停新准入并安全关闭；不丢关键事件后返回成功，不让ledger失败阻止已在途安全关闭 |
| 迁移/回退/重启 | 旧hash按原编码验证；新能力重编译为草稿；不按默认白光/通道序号迁移，不恢复历史Armed为活动许可 |
| AOI/钢网第二消费者 | 相同Core测试host各自持有曝光引用/质量解释，无私有配方/表；安全与时序需求来自各自Profile，不能用第一个宿主阈值冒充另一个 |

## 7. 稳定错误与恢复语义

本节唯一冻结错误字符串；程序按键判断，Adapter 保留 VendorCode/SourceReference，UI 用资源译文。附录 A 的 Fault.Code 只能取此集合：

`LIGHT_DEVICE_NOT_FOUND`、`LIGHT_CAPABILITY_INCOMPLETE`、`LIGHT_SAFETY_PROFILE_MISSING`、`LIGHT_SESSION_CONFLICT`、`LIGHT_STATE_CONFLICT`、`LIGHT_IDEMPOTENCY_CONFLICT`、`LIGHT_UNKNOWN_CHANNEL`、`LIGHT_DUPLICATE_CHANNEL`、`LIGHT_SCENE_INVALID`、`LIGHT_UNIT_MISMATCH`、`LIGHT_OUT_OF_RANGE`、`LIGHT_QUANTIZATION_REQUIRED`、`LIGHT_POWER_LIMIT`、`LIGHT_DUTY_LIMIT`、`LIGHT_OVER_TEMPERATURE`、`LIGHT_TRIGGER_NOT_ARMED`、`LIGHT_TRIGGER_LOST`、`LIGHT_READBACK_MISMATCH`、`LIGHT_PARTIAL_WRITE`、`LIGHT_CONTROLLER_FAULT`、`LIGHT_TIMEOUT`、`LIGHT_CANCELLED`、`LIGHT_BLACKOUT_UNCONFIRMED`、`LIGHT_GENERATION_MISMATCH`、`LIGHT_RESOURCE_LIMIT`、`LIGHT_RESOURCE_DRAIN_TIMEOUT`、`LIGHT_UNSUPPORTED`、`LIGHT_STALE_SCENE`、`LIGHT_TRANSPORT_NOT_OPEN`、`LIGHT_TRANSPORT_TIMEOUT`、`LIGHT_TRANSPORT_CHECKSUM_INVALID`、`LIGHT_TRANSPORT_NACK`、`LIGHT_TRANSPORT_DISCONNECTED`、`LIGHT_READBACK_UNAVAILABLE`、`LIGHT_GROUP_WIDTH_UNSUPPORTED`、`LIGHT_TRIGGER_PROFILE_UNAVAILABLE`、`LIGHT_AUDIT_WRITE_FAILED`、`LIGHT_EVIDENCE_STALE`、`LIGHT_CLOCK_MISMATCH`、`LIGHT_ARITHMETIC_OVERFLOW`、`LIGHT_PERMISSION_DENIED`、`LIGHT_CLEANUP_FAILED`、`LIGHT_CONTRACT_VERSION_UNSUPPORTED`。

Fault 必含 Code、FieldPath（非字段故障可空）、IsRetryable、PhysicalEffect、Recovery、VendorCode?、SourceReference?；PhysicalEffect=NotStarted/MayHaveStarted/Confirmed，只说是否发生效果，不说合格。普通ACK不能设Confirmed。Recovery=CorrectInput/Query/Blackout/Reopen/ManualSafety/None；可重试只是建议，不隐含自动动作许可。

非法预接纳参数返回结构化 Rejected；调用方显式取消等待抛OperationCanceledException，此异常只表示调用等待结束，不是OperationStatus.Cancelled；已接纳或接纳未知的原operation仍按已知ID/hash查询。预期设备错误不向外只抛普通 false；非预期.NET异常隔离为ControllerFault并尝试安全收尾。Dispose清理失败抛 `LightingCleanupException`，其 Binding/SessionId/OperationId/CanonicalRequestHash/Fault 可用于原实例查询，不 swallow。

## 8. 幂等、持久化、安全抢占与关闭

### 8.1 Command 接纳与 ledger

普通命令：纯形状校验/编码冻结与预算→查询(key,hash)→已存在核历史binding后返回同operation/冲突→预留有界队列与占用→在单actor中核当前binding/version、重编译与当前permit→以ledger原子Reserve写accepted/reserved（版本/key/op唯一）→才发设备命令→保全事实→临时资源排空归还→ledger Finalize唯一终态→对外回执。历史回放不得先拿当前能力重编译旧scene再把合法历史请求拒绝。Reserve包含stateVersion核对结果与规范字节；不存在跨“外部CAS+落盘”的隐含原子性。实际设备不支持“数据库和SDK一个事务”，发送后断电结果为Unknown，Query不重发。

ledger返回 Durable=false/Unknown 时禁止新点亮；Finalize失败不改真实设备证据，保持查询为RunningUnknown，阻断新准入并保留原记录/占用。日志是投影，不替ledger；内存ledger仅Simulation可用。真实端口必须持久化完整请求/事实/资源终态/唯一终态，能查询旧operation与hash，并定义原子去重、满盘、损坏、保留与恢复。保留到期只可保留带hash的墓碑，不把NotFound当安全重发许可。

### 8.2 安全关闭优先级

安全 lane 只接受同controller/device/boot/generation与原lease，允许已锁存Faulted/Hold和失效业务许可；Blackout/Stop 不因旧 expectedStateVersion 或已取消用户token拒绝。错误device/generation仍拒绝，不能对新设备发送旧关灯命令。它先锁存拒新emit、使Armed失效，再协调actor；最多一个合并中的安全动作，调用者各有回执关联，不占满普通队列。它不是“并发调用同一串口/SDK”或立即中断不可取消native。

安全lane关联等待者也有界，最多RuntimeLimits.MaxQueuedOperations个；先锁存安全信号，再登记等待者，超限调用返回Rejected/ResourceLimit但不能撤销已锁存安全动作。已接纳的不同安全操作分别保全ledger记录，不以合并SDK调用伪造相同operation身份；新的安全调用不能复位Close/cleanup截止时间。Owner内部故障收尾挂在原操作上，不依赖另建一条可被满队列拒绝的普通Submit。

ledger/审计写失败不能阻止已有设备的关闭/禁触发尝试：先用原Owner独立cleanup预算执行已批准安全关闭，记录AuditWriteFailed/未知持久化并Hold；绝不把应急例外用于新emit。若SDK调用尚未返回且无法中断，保持Hold，不能承诺Blackout在毫秒内完成；现场安全依赖硬件链。当前合同不声明自动重试次数/资格，Controller不自动重试trigger或Readback；后续新的显式安全Readback仍受原Owner/同binding/有限预算约束，不能重放emit探测结果。

### 8.3 资源与 deadline

RuntimeLimits控制普通队列、关键事件、观察waiter和ledger字节；两个独立预算是RequestDeadline与CleanupDeadline。Request超时/原始业务调用取消会请求逻辑收尾，但业务等待结束不证明收尾完成，必须继续Stop/Blackout/对账/排空；cleanup超时保留原lease和句柄、Query入口，禁止重占。WaitAsync或Channel完成不代表native返回，不在Task取消后释放连接。

普通Open/Apply/Arm/Execute/Preview的原始ct取消：接纳前停止；接纳后请求逻辑取消并由Owner安全收尾，调用方等待可先抛OperationCanceledException，不能据此认定terminal。重复请求的ct只取消本次查旧操作的等待，不撤销原operation。Stop/Blackout/Close的ct仅取消本调用等待，不能阻挡安全动作；Query/GetSnapshot/Observe/事件枚举的ct仅解除本次读取/订阅。RequestDeadline到期由Controller请求业务超时收尾，若CleanupDeadline也到期，返回RunningUnknown+DrainTimeout并保留Owner，实际资源退出后才追加最终事实。Dispose无ct，等待以Open中宿主显式预留的DisposalOperation预算限定。

期限字段为相对时长：从公共调用入口以TimeProvider单调时间固定Request到期点，含查ledger/排队/许可/所有设备动作；收尾开始时另固定唯一Cleanup到期点。每个端口调用只传相应剩余时长，不为每组/每步骤/重试重置完整预算；剩余<=0不发新业务动作，进入收尾或报告排空未知。安全动作合并不能延长已经固定的底层收尾预算。Query/GetSnapshot由RuntimeLimits.QueryDeadline与ct中较早者界定，Observe由WaitDeadline和ct中较早者界定；查询超时抛TimeoutException且不修改设备，Observe到期返回Unknown+LIGHT_TIMEOUT。调用方等待取消不销毁在途操作。

每命令的回调/临时buffer/观察waiter实际退出后才能 Operation ResourcesReleased；会话句柄/SDK库/lease 到 Close 才归还。lease续租失败立刻禁止新触发并安全关闭；占用服务不得因TTL过期自动授权仍可能发光的旧Owner与新Owner双写，需硬件fencing或显式安全回收。此跨进程物理隔离是LC-H门，不在单机Simulation伪证。

Close单飞；调用方取消等待不取消底层Close，Query返回原进度；native Close从未执行的排队超时不禁止首次清理，已执行未知的Close不得重复直到厂商明确保证可重试。只lease持久归还失败时可重试lease释放，不重跑已成功native Close。Dispose不创建替代Owner，不把二次无异常/Disposed标志当释放成功；失败原host保留实例/诊断。进程崩溃不能释放任何native保证，只由宿主依ledger与外部占用恢复。

Open预留DisposalOperation（与Open及其它请求的ID/key不同、ExpectedStateVersion=0，Actor/Purpose为宿主批准的生命周期恢复身份），成功接纳Open后保存；它不是当场Reserve的第二操作。未显式Close而Dispose时，使用这个固定身份构造Close请求，安全lane忽略其旧version；多次Dispose复用同一Close进度，不创建新Owner/新Close。显式Close已在途时Dispose加入其单飞任务，Close成功后才Dispose Adapter；尚未Open的Dispose仅归还未连接Adapter，预算用RuntimeLimits.QueryDeadline。Close超时且native未执行可由新安全请求在相同Owner内继续未完成阶段；native已执行未知保持原任务查询，不重发。终态Close回执只有Session资源真实归还才存在，未知释放不得伪造Failed terminal。

## 9. Adapter、模拟器与版本兼容

选择主路线为一个controller一个actor＋.NET10有界Channel（SingleReader=true、SingleWriter=false、FullMode=Wait、AllowSynchronousContinuations=false）。普通Submit采用TryWrite并在满时明确ResourceLimit，避免无限阻塞接纳者；安全lane为独立有界合并信号，actor每次正常写前先检查安全状态。关键事实队列不使用Drop模式；UI快照可合并但必须带watermark，关键operation事实可Query。回调只做有界归档/唤醒，不执行UI或持锁调用宿主。

actor串行化状态和SDK写，不得在等待一条长native任务时停止处理许可/续租/故障/查询/安全信号。保存唯一nativeInFlight任务，完成通知回actor；期间只处理状态及外部lease/permit端口，不发第二个SDK动作。读回也经过同native串行路线，不用“只读”绕过线程/协议约束。定时器仅投递有界合并信号，长期不返回的native保持原Owner，许可过期仍锁存Hold/安全请求。此调度不能证明native可被中止或硬件立即关灯。

设备发现只在Adapter.OpenAsync内执行，AdapterOpenResult.Capability是唯一能力返回；不再另发没有能力返回值的Discover动作。AdapterAction的值1保留不用，其余固定值不重排。动作为DisableTriggers/ConfigureDisabled/ConfigureTrigger/ApplyForEmission/IssueTrigger/Readback/Blackout/Drain/Close。ConfigureDisabled仅能力明确支持才调用；ApplyForEmission是有作用动作（完整设定及使能），Continuous由此进入等待物理起点；SoftwarePulse在设定后由IssueTrigger发一个声明的脉冲序列；HardwareTrigger的IssueTrigger只解除经许可的触发门控并等待外部边沿，不由主机伪造外部边沿。ConfigureTrigger不解除门控；DisableTriggers在收尾/故障优先请求，Blackout禁用所有OwnedChannels，Drain只等待实际在途退出，Close才释放连接。返回Unsupported不能换协议乱尝试；GroupCapability.HardwareSequence/StepObservation声明决定分支。参数/receipt及证据形状见附录；不定义SDK句柄、ABI、端口帧或固定重试数。

Simulator使用注入TimeProvider和明确脚本，事件/证据全标Simulation；可注入部分写、Checksum错误、延迟、温度、断连、无法禁触发、native不返回、ledger满/坏、lease失败、事件溢出。不使用真时钟长sleep证明完成；模拟OpticalMeasurement不能满足真实黑场策略。

v0.2 API/编码整体版本化：不兼容字段/单位/枚举/排序规则发布新版本并显式迁移；未知enum拒绝执行，不默认Continuous。旧operation只读原规范字节，迁移生成新Draft，不修改历史hash或Actual。Optional字段也只有明确兼容处理时可读，不能直接声称所有新增字段天然兼容。回退Core/Simulator/Ui/Adapter/Contract按矩阵成组，旧schema不能读时停在Hold，不点亮。

## 10. 可选 WPF 控件规格

### 10.1 任务流、控件组合与布局

可选 `LightingEditorControl` 只编辑宿主提供的场景草稿与投影；无独立产品工作台或第二语言入口，不嵌相机采集逻辑。工程人员：读取能力→选步骤→编辑完整通道组合→校验→查看量化差异→受控单步预览→确认Blackout→返回草稿；生产操作者只读冻结场景/实际/状态，按宿主权限可停止/关闭，不编辑生产frozen参数。预览就是有限单步Execute，走同一permit/ledger/安全/排空路径，不是另一条直连SDK捷径。预览取消、失焦或控件卸载请求停止；等待确认并保留原host恢复页，不自行Close生产会话。

仅1920×1080屏幕验收；先扣任务栏、系统标题/边框和宿主状态栏，以宿主实际ClientArea布局，不修改显示设置。模块顶部命令带48 DIP、底部状态带28 DIP，其余用 DockLayoutManager：左能力树22%、中步骤+通道矩阵53%、右高级属性25%；中区下方时间线占中区高28%，诊断面板默认折叠。最小左240、中560、右260 DIP，宿主可用宽不足先将高级设置转Flyout、诊断收起，中矩阵横向滚动；关键命令/身份/未知状态不裁切。不运行其它屏幕分辨率矩阵。

- 能力树：`GridControl + TreeListView`，KeyFieldName=NodeId，ParentFieldName=ParentId；controller→组→稳定ChannelId，波段/几何只是标签，不能按颜色聚合通道。搜索保留选择ID。
- 中区：步骤列表与 `GridControl + TableView`，列固定通道ID、名称、启用、设定值/单位、量化值、寄存器值、光学实测、证据年龄/状态；未知用“未读取”，不用0。同组选中用于批量草稿编辑，一次Core校验后原子应用，不绕互斥。
- 右区：`PropertyGridControl.SelectedObject` 绑定步骤草稿副本，分类为触发、时序、用途/证据；身份/hash/Actual只读。范围/单位编辑器来自同Core能力规则，text输入中间态保留，不失焦静默clamp；Enter显式提交草稿、Esc撤销单元格，不触发设备。
- 时间线：`ChartControl + XYDiagram2D + LineStepSeries2D` 展示各Channel Requested与RegisterActual/MeasuredOutput分开；没有实际事件只画请求虚线，Unknown区间断线，不插值成实际发光。点选步骤/通道联动矩阵与属性，不触发Apply。
- 高级设置/帮助：`DevExpress.Xpf.Editors.Flyout.FlyoutControl`；限值、证据含义和恢复使用 `SuperTip/SuperTipItem`。Blackout、停止预览、Query/恢复入口始终在主命令带，不能藏菜单。主题由宿主通过ThemeManager统一，明暗色身份/错误/未确认均有文字与图标，不仅依颜色区分。
- DockLayoutManager的SaveLayoutToStream/RestoreLayoutFromStream仅处理宿主可信的本地、版本化布局；不接用户任意反序列化字节，不持久化设备句柄或business state；恢复失败回到默认布局，不影响operation。关闭停靠面板不能Dispose共享Controller。

Tab顺序：步骤→通道表→参数→校验→预览→停止/关闭→诊断；矩阵方向键导航、F2编辑、Ctrl+C/V只复制/粘贴组合、Ctrl+Z只撤销草稿。编辑文本时Ctrl+C/V用文本语义；按钮Enter只激活当前焦点，不能全局Enter触发亮光。安全关闭不使用容易误触的裸Esc全局快捷键。UIA命令/表格有稳定AutomationId，Busy禁普通编辑但安全关闭/Query保持可达。

### 10.2 步骤组合复制与粘贴

Core CopyCombination冻结完整通道Enabled/Requested、binding和来源SceneHash；不复制StepId、Ordinal、曝光/触发/时序，不复制Actual/验证结果。PasteCombination只向已存在目标StepId替换完整通道组合，保留目标身份和时序，先以当前能力对全场景Compile；成功返回新Draft/新hash，失败原子返回原草稿，零设备调用。

只在当前编辑会话缓存；重载/能力或generation变化/控件关闭清除。复制后来源继续编辑不能变缓冲内容；成功后目标旧Actual/预览/验证投影全部失效，失败保留旧投影。只读、Busy、Stale、无目标禁用。多选粘贴先校验每个目标，任一失败整批拒绝；Core单目标API由控件先计算所有候选再一次替换集合，不边循环边修改原集合。

### 10.3 文字、状态与 UI 性能

控件仅提供 `SetCulture(CultureInfo)` 与CultureChanged，宿主切换；输入按当前culture解析，规范hash始终Invariant。切语保留编辑缓冲/选择/operation；未提交无效数值不能因切语变合法。资源键覆盖标题、列、参数、单位、错误/恢复和SuperTip。长英文换行/表头tip，身份短显+完整复制，不把状态或安全动作省略。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Lighting.Copy | 复制组合 | 複製組合 | Copy channels |
| Lighting.Paste | 粘贴组合 | 貼上組合 | Paste channels |
| Lighting.Validate | 校验场景 | 驗證場景 | Validate scene |
| Lighting.Preview | 预览此步骤 | 預覽此步驟 | Preview step |
| Lighting.Stop | 停止预览 | 停止預覽 | Stop preview |
| Lighting.Blackout | 关闭光源 | 關閉光源 | Switch off lights |
| Lighting.Unknown | 输出未确认 | 輸出未確認 | Output unconfirmed |
| Lighting.ReadbackMissing | 未读取实际值 | 未讀取實際值 | Actual not read |
| Lighting.Hold | 暂停使用，请查询状态 | 暫停使用，請查詢狀態 | On hold. Check status |
| Lighting.PasteScope | 仅复制通道与设定值 | 僅複製通道與設定值 | Copies channels and setpoints only |

Error显示具体controller/step/channel和允许动作；传输异常细节在诊断，普通UI不显原生stack/秘密端点。状态明确未配置/草稿/已配置/已布防/预览/冷却/输出未确认/清理失败/只读。

Grid只绑定有界分页/虚拟数据，时间线仅有界可视窗口；后台事件不直接推UI，UI dispatcher合并快照但不丢关键错误，投影水位可Query追齐。绘图采样不变Core事实；Dispatcher耗时、事件积压、切语和关闭延迟由UiBenchmarkProfile采纳，当前TargetPending。实际WPF构建/键盘/UIA/主题/三语/ClientArea截断及性能另验，没有本轮UI运行结论。

### 10.4 装配、三类投影与恢复任务

唯一公开装配签名及Owner桥接见附录A.4；不增加Core factory、第二ledger或UI设备状态机。宿主按§5构造原Controller、原ledger/lease/permit及Clock，并完成Open或QueryOpen。只有取得正式Binding和原Capability后才Attach；PendingOpen只在宿主恢复区展示，控件不伪造可编辑context。Ui factory仅创建Session、控件及内部Presenter，不连接设备。Session是UI生命周期，Presenter是草稿/命令意图与投影协调器，二者不获得设备Owner、质量放行或生产参数批准权。

| 投影 | 唯一来源与显示规则 | 失效及允许动作 |
|---|---|---|
| 请求 | 当前草稿、Compile的NormalizedScene/Changes；请求值与量化值各占一列，量化差异须显式确认当前SceneHash | 编辑后旧确认失效；不把草稿保存、校验成功或ACK显示为设备已应用 |
| 实际 | 同Binding/session/operation/step/SceneHash/channel的Core证据；寄存器和光学值分列，显示来源、Simulation标记和同Clock证据年龄 | 用A.1 CompareEvidence及原Usage检查支持域、来源与年龄；超龄保留历史值并标“已过期”，不作为当前实际。新草稿/hash不沿用旧实际 |
| 未知 | 原回执Status/PhysicalEffect/Blackout/Resources及缺口；输出未知、黑场未确认和资源未归还分别显示 | 禁止新Preview，保留原ID查询、停止/关闭和宿主恢复入口；取消等待、寄存器0、窗口消失均不消除未知 |

投影只读Core事实。Clock必须是原组合根的同一TimeProvider实例与RuntimeLimits.ClockId，不用DateTime/Dispatcher计时推导读回年龄。缺/跨Clock证据标未确认，不能用UI重新采样时间延长证据寿命。Blackout只有原Usage要求的受信物理证据与Core判定满足时才显示“黑场已确认”；Stop完成、Blackout确认、Operation排空和Session释放是四个独立结果。Safety命令ACK或CommandedOff只显示请求已发送，不能显示为Stop已完成；只有原回执满足终态和资源事实时才显示对应完成。真实Usage阈值未取得时不运行真实预览，§11.1模拟黑场不成为物理门值。

联动固定为能力树ChannelId→矩阵同ID→时间线同ID；步骤列表StepId→属性副本→时间线对应窗口，联动/搜索/布局恢复不提交设备命令。批量设定与多目标场景粘贴共用§10.2全量候选校验/一次草稿替换；单位不同不能批填，禁用通道Requested=null，双白仍为两行。行内错误定位步骤/通道，主带显示错误摘要与首个可修字段；高级触发/预算/可信源详情放右侧或Flyout，身份、请求/实际/未知和安全命令保持可见。量化确认不能藏在属性面板或由Preview自动勾选。

权限来自宿主当前角色投影，Core permit为实际动作权威。只读允许选择/复制只读身份和查看证据，不能编辑/粘贴/预览；CanStop控制用户主动Stop/Blackout。撤权在Dispatcher上立即禁新意图；已发Preview仍由原根按已保存安全用途收尾，不因按钮变灰取消必要清理。控件失焦仅在焦点离开整个控件子树时触发；打开本控件Flyout/编辑器弹窗不构成失焦。失焦、Preview等待取消、Detach和卸载对同一在途Preview加入同一个Stop单飞，不向另一宿主或生产执行发Stop。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Lighting.Query | 查询原请求 | 查詢原請求 | Query request |
| Lighting.BlackoutPending | 黑场未确认，请查询原请求 | 黑場未確認，請查詢原請求 | Blackout unconfirmed. Query request |
| Lighting.BlackoutVerified | 黑场已确认 | 黑場已確認 | Blackout confirmed |
| Lighting.CleanupPending | 资源未归还，请继续恢复 | 資源未歸還，請繼續復原 | Resources retained. Continue recovery |
| Lighting.WaitCancelled | 已取消等待，操作结果待查询 | 已取消等待，操作結果待查詢 | Wait cancelled. Query operation |
| Lighting.EvidenceExpired | 已过期 | 已過期 | Expired |
| Lighting.Simulation | 模拟结果 | 模擬結果 | Simulated result |
| Lighting.ReadOnly | 只读 | 唯讀 | Read only |

窗口关闭由宿主Closing事件先取消当次关闭，再异步Detach并按§5嵌套finally执行原Owner收尾，不能在Dispatcher上同步Wait/Result。预算到期返回宿主恢复区：保留原Controller/Task/ledger/lease、身份及错误，明确输出/资源未确认；不得显示“灯已关”或“已退出设备”。视觉窗口可由仍存活的原组合根接管后关闭，原恢复服务不能随控件Dispatcher销毁；需要终止进程时由宿主现场安全流程处理，UI不宣称退出进程释放了设备。原根有限Query及原安全单飞恢复见§5.2/A.3，不自动重建Controller、重新Open或释放另一Host租约。

### 10.5 两个空STA宿主的可判定验收

UI测试唯一工程沿Core binding既定位置，冻结`net10.0-windows / UseWPF=true / OutputType=Exe`，只引用本模块Core、Ui.Wpf与本机25.2.3必要程序集，不依赖产品Shell、数据库、相机、语言模块隐藏初始化或其它模块页面。两个消费者在该Exe中分别运行于独立STA线程/Dispatcher和空Window根，不在同一Dispatcher伪装两宿主。各根独立构造§11.1已有Simulation Adapter/ledger/lease/permit及ManualTimeProvider、§5原槽、Open/Disposal身份；不新增可分发Simulator协议。AOI两步草稿与钢网单步草稿直接复用§11.1，不另造通道/光学向量。

正常双根用不同controller/device/session/lease/operation，CapabilityHash按各自Binding重算；不是同时争用同一个模拟灯。另一个负例仅让同device两根共用同一模拟lease权威（各自ledger、Controller和UI不共享）：第二Open被拒绝，device打开/发光计数不增加，第一根lease/fence不变，第二根只能收尾自己未获占用的实例。这里验证软件拒绝行为，不证明真实跨进程fencing。

每根顺序：构造原Core根→Encode/保存Open和Disposal→Open并按原记录取得Capability→factory.Create→将Session.Control作为空Window.Content→Attach→宿主单一ReadEvents扇出到UpdateProjection。所有UI入口在所属Dispatcher；后台执行/查询不得同步阻塞它。AOI为工程编辑角色，可批量双白/两个目标步骤、确认量化及有限单步Preview；钢网先工程角色完成W1单步，再在同context撤为只读角色验证冻结投影/CanStop。测试权限转换不批准任何生产配方。每次Submit桥接必须保留原command/hash/Task后调用既有Controller；无UI仍可调用全部Core功能。

两根的UI软件夹具显式使用LightingEditorOptions(各根原ManualTimeProvider, 各根RuntimeLimits.ClockId, 64, 512, 8, 16ms, 200ms)，依次为诊断数、绘图点数、可视operation数、普通投影间隔及查询等待期限；不是产品默认或性能达标值。§11.1的CompileLimits.MaxSceneSteps=4给每根A.4生命周期记录上限15项。每根预持Open/DisposalClose及根finally Stop共3项，每次Preview/它的Stop原子占2项，最多6次；第7次在设备调用前明确拒绝且根安全单飞仍可达。显式Blackout另占1项并减少剩余额度；夹具不把历史完成项驱逐来延长同一session寿命。U-H另外验证64条诊断后摘要、513点时采样、9项operation分页及15项根记录满时的拒绝，投影分页不能截掉原根保全身份。

| Case | 必需任务与判定断言（AOI/钢网均执行，角色适用项另注明） |
|---|---|
| U-A 空根与边界 | 两根不需要产品静态状态；Create/Attach设备写与额外Open计数0。跨线程调用失败且无动作；重复Attach拒绝。不同根的选择、草稿、语言、operation和lease不互相污染；同device冲突按上段检查 |
| U-B 编辑与高级联动 | AOI双白ID独立、步骤/树/矩阵/时间线联动无设备调用；批填/两目标粘贴任一失败整批不变，成功保留目标StepId/曝光/触发/窗口且旧Actual失效。输入中间态、撤销、量化未确认禁Preview；钢网只读禁编辑/粘贴/Preview，安全命令按CanStop可达 |
| U-C 设置与读回 | 对所选步生成Ordinal=0单步Preview，同一原ID完成内部阶段且不更改多步草稿。请求/量化/寄存器/光学分列；注入缺读回、跨Clock、过期、错step/hash及只有寄存器0的黑场，均不得显示有效实际/黑场成功；§11.1可信模拟读回只显示带Simulation标记的确认 |
| U-D 未知与原ID查询 | Reserve/回复丢失保留原ID/key/bytes/hash及Task；按钮只Query原operation，查不到仍Unknown、不新Preview/重发。不将StateVersion新快照当旧operation终态；事件缺口由根Query追齐，关键故障/未释放身份保持可见 |
| U-E 取消、撤权与失焦 | 等待取消不等于OperationStatus.Cancelled；撤权和离开整个控件触发原Preview安全收尾。弹窗内焦点移动不触发；取消/失焦/Detach竞争Stop单飞且无另一根命令。安全权限撤回后原根仍执行其生命周期恢复，UI不生成新发光意图 |
| U-F 关闭、迟到与原槽恢复 | Preview/Stop/Close排空barrier中关闭窗口；Detach取消也不丢原根任务。旧代次完成不能覆盖新context，未知仍归原根；Close异常后Dispose仍尝试。先断言原Owner未归还、无替代Open，再由脚本释放原barrier并有限查询/收尾；只在§5返槽条件全满足后完成夹具，另一Host租约不变 |
| U-G 键盘、语言与可见性 | 固定1920×1080实际ClientArea中依§10.1走Tab/F2/Ctrl+C/V/Z、聚焦Enter及Esc；无全局发光快捷键。zh-CN/zh-TW/en-US切换保留无效编辑缓冲、选中ID与原op/hash；长英文、明暗主题、Flyout、折叠诊断仍可见安全命令/Unknown/身份且UIA可定位，无裁切关键文字 |
| U-H 错误与有界投影 | handler抛异常不阻止原根恢复；普通快照可合并但关键错误、Unknown和未释放op不丢。超UI可视预算明确摘要/分页并保留原根全记录，不把旧Actual改成0；诊断不暴露秘密端点/stack。重复/乱序/同version矛盾投影不回退或覆写 |

自动化软件case/suite/进程采用§12.1的10s/120s/180s wall保护，与ManualTimeProvider分开；每个root/case必需任务和Dispatcher退出纳入完成清单，超时/仍存活任务非零退出。人工三语/键盘/视觉任务逐项执行与记录，不用自动case的10s冒称操作员速度门值；UiBenchmarkProfile仍TargetPending。固定视口复用§10.1，不改系统分辨率，不跑其它分辨率矩阵。

上述LC-U规格准备已由主控接收；真实WPF构建/两个STA运行/视觉与UIA/性能是各自执行门，均未在本轮执行。Simulation未知/黑场演练不关闭真实SDK、光学黑场/热/时钟、durability/保留期、跨进程fence、HIL、物理及现场验收门；门的原Owner与范围沿§15，不合并成一个“UI通过”。

## 11. Golden、正常与失败期望

下列数字仅是标记Simulation的测试向量，不是任何设备默认或物理验收阈值：

- C1-A：5个ID=R/G/B/W1/W2、DeviceUnit 0..100 step=2，组MaxEnabled=5，各认证功率1W、组限5W；单步Continuous Window=100ms，W1=10/W2=14，其它Off。Compile保持两白独立、归一化无差异，不发设备命令。另一Compile输入同值decimal=10.0m、通道枚举反序，规范字节/hash等价。
- C1-B：5→4、7→8（Nearest）；Reject拒绝非网格；101原值越界拒绝；Enabled=false但Requested=0拒绝；Enabled=true,0不会成为Off；互斥MaxEnabled=1而W1/W2都Enabled即使0也拒绝。
- C1-C：PulseWidth=2ms、Period=4ms、Count=2、Window=10ms、Delay=1ms，累计4ms/10ms=0.4；maxDuty=0.3拒绝，0.5允许纯编译，执行仍需滚动热许可。width0、period<width、overflow拒绝，不软件补延时。
- C1-D：Copy来源两白不同值→Paste目标另一StepId，保留目标Window/Exposure/Trigger；所有off也是完整组合；能力hash变、缺成员、外来Unit或target不存在拒绝，原目标/旧投影不变。
- C2-A：DisabledPreload=false；Apply设备写计数0，Arm只核受保护触发/许可；Execute才开始ApplyForEmission。单步可信Simulation起点/结束/Blackout全匹配→每operation临时资源归还，session lease仍占用，Close后才lease归还。
- C2-B：第一通道成功、第二NACK→立即停止后续、Blackout/Query、Faulted/Hold；不Configured/Armed，Actual仍逐通道保留。
- C2-C：Execute返回ACK和寄存器却无光学起点→Observe Unknown、不EmissionStarted；黑场只寄存器0→Unconfirmed/Hold，不允许新Execute/释放占用。
- C2-D：Reserve失败→普通emit SDK次数0；已有emit且ledger坏→仍尝试安全关闭，保留未知持久化/占用；Finalize失败不返回虚假唯一成功。
- C2-E：Close SDK在途取消→仍占用；SDK已关闭但lease归还失败→重试只调用lease归还，native close总次数1；native close未知→后续Close返回原RunningUnknown而非再call。
- C2-F：旧session安全Close后新session Open形成新generation，旧迟到事件即使ChannelId相同也不能回填；同key不同Window冲突、同key/hash重放触发次数1；无人能“找不到op所以再发一次”。
- C2-G：Ready提交Preview，只出现一个Reserve和一个terminal，内部配置/布防/发光共用该ID；成功黑场并冷却后SceneHash/ArmedOperationId为空、状态Ready，后续Execute必须重新Apply/Arm；Armed中Preview拒绝且设备调用0。
- C2-H：合成同clock/frequency的lease ValidFor=100ms，LeaseRenewInterval=20ms；到Renew返回时剩余仅10ms即不可继续emit，关灯并Hold，不用原100ms重置寿命。未来CheckedAt/跨clock/fence改变也失败；字面相同SourceReference但Kind/Subject/ChannelId/CalibrationHash不匹配不得通过证据允许表。
- C1-E/C2-I：MaxPayloadBytes按完整编码计数，上限处通过、加一个UTF-8字节即ResourceLimit；decimal极小Step与极大值不因除法舍入误判网格；start比Now未来一个tick拒绝；Open黑场StepId/SceneHash=null匹配，空字符串不等价；事件保留缺口抛LightingEventStreamException并要求Query，不产生伪连续流。
- C2-K：提交前EncodeOpenRequest保留op/hash，ReserveOpen回复未知且设备未返回时QueryOpenAsync用PendingOpenIdentity查同记录，返回原PendingIdentity和可空正式Binding；发现后QueryOpen返回原OpenCapability，不重新Open或Acquire。隐式Dispose在已取得正式Binding时只Reserve预留DisposalOperation一次；未形成正式Binding的未知半开只观察原Open cleanup，不构造Close。重复Dispose/native未知不增加Close调用，异常含原session/op/hash。首次Open前Dispose不Acquire lease、不Open设备，只尝试归还未连接Adapter；借用ledger/lease/permit从不被Dispose。

### 11.1 两个无UI宿主的完整合成输入

以下补足C1-A/C2-A的构造字段，不是生产默认：ApiVersion=2，binding为ControllerId=`sim-light`、DeviceId=`sim-device`、BootId=`sim-boot-1`、Generation=1；CapabilityHash先为空，ComputeCapabilityHash后写回。五通道按R/G/B/W1/W2分别声明DeviceUnit、Range(0,100,2)、CalibrationHash/GeometryLabel/WavebandLabel=null、CertifiedMaxPowerWatts=1、MaxDutyCycle/PulseWidth/PulsePeriod=null、ReadbackKinds=[RegisterReadback]、ReadbackTolerance=0。唯一组ID=`all`、Role=WritePartition、OrderedMembers=[R,G,B,W1,W2]、SupportedWriteWidths=[5]、MaxEnabled=5、MaxPowerWatts=5、DisabledPreload=false、HardwareSequence=false、StepObservation=true；TriggerModes=[Continuous]、TriggerDelay=TickRange(0,0,1)、Simulation=true、FirmwareReference=`sim-fw-1`、SourceReference=`sim-cap-1`。

AOI宿主准备step-a/step-b，分别W1/W2=10/14、14/10，其余Off；Ordinal=0/1、Window=100ms、ExposureReference=`aoi-exp-a`/`aoi-exp-b`，Trigger为Continuous、Width/Period=null、Count=0、Delay=0、SourceReference=null。本能力不支持硬件多步：保留多步编辑草稿，执行前每步形成Ordinal=0的单步Emit场景并分别Compile→Apply→Arm→Execute→观察→确认黑场/冷却→下一步，绝不把两步scene作为硬件原子序列提交。钢网宿主采用同一能力、独立session，单步Ordinal=0、Window=100ms、ExposureReference=`stencil-exp-a`、W1=10/W2 Off，其余Off，走完整Apply/Arm/Execute链；互不共享session或操作身份。

两者测试预算均明确为CompileLimits(4,5,65536)，RuntimeLimits(8,128,8,16384,1048576,`sim-clock-epoch-1`,200ms,20ms,20ms,同CompileLimits)；这些数字仅供有界模拟测试。注入TimeProvider.TimestampFrequency=10000000，GetTimestamp从0由测试驱动推进。Usage的ProfileHash为宿主固定的合成测试身份，RequiredReadback=RegisterReadback、Tolerances为全部五通道0、MaxReadbackAge=50ms、RequirePhysicalBlackout=true、BlackoutLimits=[(null,Intensity(0,WattPerSquareMetre),`sim-blackout-profile`)]、AllowSimulation=true。TrustedEvidenceSources为每通道(RegisterReadback,Setpoint/Enabled,channel,`sim-register`,null)，每步整组(OpticalMeasurement,EmissionStart/EmissionEnd,null,`sim-optical`,null)，及整组(OpticalMeasurement,Blackout,null,`sim-blackout`,null)，均逐项显式列出且无重复。端口输出证据只来自这些模拟脚本。

RuntimeLimits增加的QueryDeadline显式为200ms；Open.DisposalOperation的Actor=`sim-engineer`、Purpose=`sim-lifecycle`、ExpectedStateVersion=0、Budget(2s,2s)，ID/key独立。模拟ProfileHash仅为宿主测试身份，固定用64个小写`a`，不声称来自客户Profile或真实资格。Emit时整组起止覆盖所有本step启用通道，结束后读取全部通道Enabled=false和整组Value=0 W/m²黑场；Off通道不要求不存在的亮度Requested读回，仍须Enabled=false。正常脚本续租/许可轮询在20ms完成，避免100ms窗口误用已到期100ms许可；物理Start在步窗口锚点+1ms、End在+90ms，最终Blackout在+95ms，均为合成证据。

Open给出Transport=SerialNumber、EndpointReference=`sim-endpoint`、独立SessionId、OperationId/key、ExpectedStateVersion=0、ActorReference=`sim-engineer`、PurposeReference=`sim-inspection`、Budget(2s,2s)。后续每个操作换新ID/key并取上一快照版本，预算仍为(2s,2s)，Query用原CanonicalRequestHash。lease脚本返回固定LeaseId、Fence=1、Held=true/Released=false、CheckedAt=当前测试时钟、ValidFor=100ms、AuthorityReference=`sim-lease`、Faults空；permit脚本精确回显请求身份/用途、ValidFor=100ms、所有批准及CoolingComplete=true、AuthorityReference=`sim-permit`、Faults空。Open禁触发和Blackout/Readback给出同Open ID、StepId/SceneHash=null的整组黑场；每步寄存器证据用自己的step/hash/channel，物理Start/End用自己的step/hash及ChannelId=null，黑场用该操作ID且StepId/SceneHash=null。所有EvidenceId唯一、CalibrationHash=null、Simulation=true，Open/Execute/Close只在脚本实际排空后报告相应资源归还。

### 11.2 C1-F 固定编码向量

用CompileLimits(1,1,4096)、Quantization=Reject、ApiVersion=2、binding=(c,d,b,1,计算所得CapabilityHash)。能力仅通道x：DeviceUnit、Range(0,10,1)、Calibration/Geometry/Waveband=null、CertifiedMaxPowerWatts=1、MaxDuty/PulseWidth/PulsePeriod=null、ReadbackKinds=[RegisterReadback]、ReadbackTolerance=0；组g为WritePartition、OrderedMembers=[x]、SupportedWriteWidths=[1]、MaxEnabled=1、MaxPowerWatts=1、DisabledPreload=true、HardwareSequence=false、StepObservation=true。TriggerModes=[Continuous]、TriggerDelay=(0,0,1)、Simulation=true、FirmwareReference=f、SourceReference=s。Capability规范字节长195，hash=`224f9cadaf6bd405d55b8377f061e76fbce572add58d452dd81040d4cb341a54`。

场景Purpose=ConfigureOnly，唯一step s0、Ordinal=0、Window=1 tick、ExposureReference=null，Trigger=(Continuous,null,null,0,0,null)，通道x为Off/Requested=null。规范字节长178，SceneHash=`49e3d4c359c8b8f39957331975d8a3ac169e92afa13f0f79f94636e54f71d2a4`，完整字节如下（单行hex，无换行字节）：

```text
000000126c69676874696e672d62696e6172792d7631000000020000000200000001630000000164000000016200000000000000010000004032323466396361646166366264343035643535623833373766303631653736666263653537326164643538643435326464383130343064346362333431613534000000010000000100000002733000000000000000000000000100000000010000000000000000000000000000000000000100000001780000
```

此向量由独立字段编码复算，后续产品测试必须比对上述字节/长度/hash；不是从未来C#实现生成期望，也不证明SDK/光学运行。

## 12. 可执行验证计划

后续实现测试放唯一Core.Tests，使用附录公开API、手动TimeProvider、脚本Adapter/ledger/lease/permit，不能只测私有函数复制同算法。编译契约测试从空console宿主引程序集、无WPF/数据库/设备SDK依赖。参数化覆盖C1-A..D，独立手算网格/位编码Golden，不用实现本身生成全部期望；两消费者host各自传用途/曝光引用验证同API。测试保留正式输入与预期字节/hash后才实际报告通过。

后续授权实现后从仓库根运行（本轮未执行）：

```powershell
dotnet build src/Modules/lighting-control/Asun.Modules.LightingControl.Core/Asun.Modules.LightingControl.Core.csproj -c Release
dotnet run --project tests/Modules/lighting-control/Asun.Modules.LightingControl.Core.Tests/Asun.Modules.LightingControl.Core.Tests.csproj -c Release -- --cases all
dotnet run --project tests/Modules/lighting-control/Asun.Modules.LightingControl.Core.Tests/Asun.Modules.LightingControl.Core.Tests.csproj -c Release -- --consumer aoi
dotnet run --project tests/Modules/lighting-control/Asun.Modules.LightingControl.Core.Tests/Asun.Modules.LightingControl.Core.Tests.csproj -c Release -- --consumer stencil
```

Exe入口接受上述三种参数模式，任意断言失败/未预期异常/超时退出码1，参数非法退出码2，全部指定断言实际执行且通过退出码0；不以dotnet test的零测试退出代替此Exe。C1-A..F、C2-A..I为固定case ID，§12取消位置/并发/Owner恢复为C2-J，未Open Dispose/隐式Dispose身份/未知接纳查询为C2-K；LC-C1只执行C1组，LC-C2执行C2组及两个consumer。失败收尾用finally保留原Controller，若cleanup未知打印原session/op/hash并使退出失败，不用新实例补清理。编译、运行及性能结果只有实际执行后填写。

### 12.1 夹具、case与进程的固定测试期限

固定软件测试wall保护为10s/120s/180s，不是设备响应、清理、光学窗口或客户性能目标：每fixture阶段（构造/挂接及最终拆卸）最多10s；每case或consumer从开始夹具准备到自身断言和finally拆卸总共最多10s，fixture不能叠加成额外10s，拆卸只用case剩余时间。每次Exe运行的所选suite总共最多120s，含全部fixture/case/consumer、必要回执核对和最终任务退出；外部运行器对单个命令进程最多180s，从启动计时，包含dotnet run构建启动，不能对重复重启重置期限。Suite到期打印未完成case/原session/op/hash并非零终止；外部到期标失败并终止原测试进程，不将进程终止视为设备/lease安全释放。该外层只运行LC-C1/LC-C2的BCL模拟测试，不能套在真实LC-H设备会话当资源回收证明。

wall保护使用真实`Stopwatch`/宿主超时token及外部进程等待，独立于注入的ManualTimeProvider；推进虚拟时钟或解除barrier不能延长10s/120s/180s。ManualTimeProvider只控制业务Request/Cleanup/观察/续租时序，每个barrier在进入、释放、迟到完成都有明确测试驱动者，不能用真实sleep等事件碰巧发生。`WaitAsync`只限定测试观察，不宣称被等Task已结束；超时后§5恢复槽仍持有原Task/Controller。wall保护的取消不能取消已经接纳的安全Close，嵌套finally仍用当时剩余case/suite wall窗口观察收尾。

Exe清单启动时固定要求执行的case及consumer ID和数量：`--cases all`必须包含C1-A..F、C2-A..K及aoi/stencil；`--consumer aoi`/`stencil`只选择对应完整宿主链。每case仅在实际执行所有必需断言、finally和任务退出检查后登记完成；跳过、未启动、required Task未完成、诊断丢失、wall超时或未确认的最终夹具释放均退出码1，不能在结果计数中减掉失败项目获得0。预期Unknown/超时注入是成功断言的输入：断言原Owner仍占后，由脚本原任务受控迟到完成，再按同槽查证与收尾，才允许夹具完成；脚本永不返回而测试退出时任务仍未知则该run失败，不为测试通过强制dispose句柄。C1测试也受相同期限制，不以纯函数无设备为由无限运行。

外部验证调用者用有限进程等待核退出码和上述完成清单，180s到期输出Timeout并视为必需验证未完成；本页§12的dotnet命令是被监督命令，不是没有超时的无限等待入口。本轮不创建外部脚本或进程、不执行这些命令。

时序测试用可控barrier枚举取消位置（准入前/Reserve后/命令已发/回读后/排空中/Close中），以及Blackout与Apply/Execute竞争、100个查询＋2个同设备写＋两个不同controller；数字是模拟反例负载，不是消费者性能目标。断言无双写、critical事实无掉队、terminal最多1、operation scope与session scope释放不同、迟到不回填、资源未知不terminal。

C2-J另含§5宿主异常链：consumer在可信起点后抛异常→observer取消并保留ExecuteTask→Stop/Close/Dispose仍按顺序尝试；QueryOpen抛异常且无正式Binding→Submit/Close调用计数0，Dispose观察原Open cleanup，槽不返；已有正式Binding时QueryOperation消费失败→用预持Stop/Close身份收尾；Stop编码或调用异常→Close/Dispose均尝试，Close异常→Dispose仍尝试，任一失败槽保留。对aoi/stencil分别注入同样位置，断言原op/hash不变、无替代Controller/lease、任务未知不返槽。C2-K的未知半开Open再断言Pending查询异常和Dispose超时不会合成Binding，受控迟到恢复只更新原槽，不能再Open。记录全部尝试及首个异常，单个finally错误不得吞掉后续错误或假报告完成。

模拟循环可复用原1000切换向量，soak时长/轮数最终由消费者Profile指定，原24/72小时不再作为无来源门值。资源斜率、滚动热、断连、lease/ledger故障、overflow注入均有观测；无设备时只声称软件模拟证据。HIL另测输出稳定/实际强度/触发门控与抖动/波段互斥/温升/物理黑场/断电、断网、安全链；SDK返回与Synthetic图不能替代。

UI只测1920×1080实际ClientArea、三语、双白独立、长英文、复制原子性、无效编辑中间态、语言保留、键盘/UIA、Busy/Unknown/CleanupFailed、安全命令可达、面板关闭不Dispose会话。本轮不造UI截图或宣称运行。

## 13. BenchmarkProfile 与可观测性

性能状态 `TargetPending`。当前无已采纳Lighting消费者BenchmarkProfile，无毫秒、Hz、资源字节或soak达标目标。Profile采纳前诊断结果为NotEvaluated；缺资源限额/有限deadline不能运行有副作用测试，不能以“目标未定”允许无界队列。

Profile冻结输入/version/hash、通道/组/步骤/payload维度、启用比例、拒绝/重复比例、并发controller/调用数、冷/热/预热、样本计划、目标机/时钟和硬件/模拟标记、Compile/RuntimeLimits、失败阈值来源与处理。测点：Compile验证/量化/hash/复制粘贴/证据匹配；Reserve/队列等待/许可检查/Adapter每动作/逐步观察/安全关闭/操作排空与归还/Finalize；Close另计session资源归还。LC-C1是纯同步方法入口至返回，无资源租约时不伪造ResourcesReleased；LC-C2端到端按DEV-GOV-010 §3.1从接纳至真实operation资源归还，ledger finalize延迟另外记录。

P50/P95/P99/n、冷/热和失败/未读/超时/删失样本、资源终态严格引用DEV-GOV-010 §3.1统一统计方法，不复制算法。记录max、分配字节、峰值/稳态内存、线程/句柄、正常/安全/事件队列深度、waiter数、ledger字节和长期斜率；排空未知不能性能通过。硬件触发/稳定/热/光学指标须对应物理Profile/HIL，有软件测量不能声称物理节拍。

审计绑定binding/session/op/key/hash/version/step/channel、requested/normalized/register/physical分开、monotonic clock来源、vendor code、重试序号、PhysicalEffect和Recovery。Connection/GroupApplied/ActualReadback/Recovery事件沿用来源经验，但日志不是ledger。UI诊断有界；普通日志不存地址/凭据，SourceReference用受保护引用。

LC-U测量计划在既有Profile上增加以下测点，不另建性能DTO或报告权威：用户命令进入Dispatcher→草稿全量Compile/一次替换→DraftChanged完成；UpdateProjection调用前→Dispatcher接受→矩阵/属性/时间线完成同水位绑定与布局；SetCulture入口→三语资源和布局完成（无效编辑缓冲另核不变）；Stop/Detach入口→预持安全请求交原根→Core回执/真实排空→UI解除挂接；窗口Closing→原根接管确认→原根返槽，窗口隐藏时间另列，不能替代资源归还。Dispatcher排队耗时、单次UI更新耗时和数据水位落后量分别记录。画面呈现/键盘/UIA验收另做真实WPF任务，不把绑定/布局完成当GPU呈现或操作员任务完成。

软件测点用真实Stopwatch，同步UI段在所属Dispatcher计时，Core证据年龄仍用原TimeProvider；虚拟时钟推进不能当真实延迟样本。UI负载用§10.5双根、两步/单步五通道及三语，另在A.4各有界上限及上限+1测试；批量编辑、普通投影、关键故障、原ID查询、安全请求竞争逐项测量。记录活跃根数/根记录数、UI排队工作数、挂接/handler/观察Task数、诊断数、绘图点、分页项、分配/峰值内存及Detach后残留；WPF分配同时列进程总量与Dispatcher线程量，异步链不能仅以某一线程分配代替总量。冷/热、预热/有效样本数量、P50/P95/P99及失败/删失样本沿DEV-GOV-010 §3.1，消费者Profile Owner采纳实际数量/资源与延迟阈值后才能判性能；缺值只NotEvaluated/TargetPending。有限队列、未知不能返槽及不丢安全身份的功能断言始终必须满足，不随性能阈值未采纳而放宽。

## 14. 独立发布、回退与两个消费者

Core独立DLL及API/编码版本、Simulator标记、错误键、Golden、端口契约测试为单独发布包，不要求WPF或硬件SDK才能引用/构建/测试。可选Ui.Wpf包单独引用Core，本机25.2.3程序集部署边界由宿主负责。Adapter单独版本化，禁止公开SDK类型；无UI样例Host只引用Core、显式注入端口，不用产品Shell初始化。每版本兼容矩阵绑定Core API/编码/Adapter/Capability/Ui，不用统一“最新”代身份；回退不重写历史记录。

| 消费者 | 具体最小使用链 | 宿主事实/接收条件 |
|---|---|---|
| AOI | 五通道合成多步骤草稿→Compile/Copy/Paste→Simulator Apply/Arm→Execute+Observe每步骤→Query→安全关闭→Close | AOI host保留各step曝光引用和帧，逐步可信观察不足时改用单步scene串行，由宿主编排，不把帧有效或质量放行字段加入Core |
| 钢网/印刷 | Open→完整通道集中的一个/多个静态通道→有限Continuous单步→Compile/Apply/Arm/Execute→观察/回读→关闭→Close资源归还 | 自己的强度单位/热/窗口/黑场策略和曝光引用；不用AOI通道数/白光配置默认；同Core DLL无UI接线验证 |
| 工程台（可选第三消费者） | 可选Ui.Wpf与相同Core，限时单步Preview、取消/失焦/恢复 | 工程权限单独批准，不开放生产动作；UI不是唯一可用入口 |

两个独立host的Golden/Replay、异常/资源和构建实测是发布验收，当前未执行；不要求客户现场数据先存在才能写无作用Core，但真实集成必须由产品Owner映射正式契约与真实身份/占用/权限。

## 15. 逐切片六项准备结论与待决影响

| DEV-GOV-010 §3.1 | 本页实际落点与准备判断 |
|---|---|
| 1 边界/消费者 | §1–3/14已明确，文档层闭合；第二消费者不是泛称 |
| 2 精确模块契约 | §4–9与附录A v0.2声明类型/方法/单位/失败/Owner；LC-C1、限定Simulation测试端口的LC-C2及LC-U §10.1–10.5/A.4增量规格均已由主控接收，尚无C#编译证据 |
| 3 最小独立Host | §5/附录A无UI引用和注入边界明确；LC-C1不需外部端口，LC-C2只允许Simulation，LC-U保留两个空STA宿主规格；尚未创建/运行工程 |
| 4 反例/生命周期 | §6A/10.4–10.5/11–12和Close/ledger故障路径已给出断言；未执行测试，真实WPF、HIL明确后续 |
| 5 Benchmark | §13测量方法/资源输入来源明确；TargetPending，不冒充已采纳Profile/达标 |
| 6 工程/变更/顺序 | Core binding/§5/14冻结，权威代码快照尚需实现任务确认；不自动开工 |

按切片接收：LC-C1六项规格定位为§1–4/14、A.1及纯请求编码、§5/11.1/12的BCL Exe、C1-A..F、§13、Core binding；主控已走读上述职责/公开合同/decimal精确量化/Copy/Paste/Compare/两个消费者/Benchmark/落点，并独立逐字段复算Capability 195 bytes与Scene 178 bytes、完整hex及两个hash一致，LC-C1同步ModuleCoreImplementationReady（仅规格准备）。LC-C2为§1–3/14、A.2–3、§5.1–5.2/11.1/12.1的同一Exe、C2-A..K与§6A/8、§13、Core binding；主控已复核有界预持槽/PendingOpen身份、观察与Execute并行、嵌套finally、10s/120s/180s期限及C2-J/K，并接续公开端口/ledger/Owner/版本/Benchmark/两个Host六项走查，LC-C2同步ModuleCoreImplementationReady，仅限Core及明确Simulation的Adapter/ledger/lease/permit测试端口规格准备。

模块整体实现/集成资格仍PreparationIncomplete；LC-C1及上述限定范围的LC-C2六项规格均已接收为ModuleCoreImplementationReady，未编译/实现；LC-U既有接收与本轮窄补均为文档准备，不标ImplementationSpecificationReady或ModuleCoreImplementationReady。可分发新Simulator协议在当前范围外，不设当前待关闭准入门；真实Runtime/durability/fencing、LC-H/SDK/HIL、LC-U真实WPF/UIA/性能、集成及生产不随之Ready。各项真实构建、运行、性能和现场验收仍未执行，不把这些规格接收当作整模块完成，也不据此将已闭合软件设计写成待设计。

具体外部门：LC-H的控制器型号/SDK操作和分组/触发门控能力、受信光学起止/黑场来源、公差/稳定/抖动/温升/滚动热与时钟资格；LC-C2真实部署的durability/保留期/fencing；LC-U真实WPF/25.2.3/UIA/三语/性能；产品集成正式C/Schema/Owner映射。这些不阻断无作用LC-C1规格实现。缺客户数值不猜，尤其Percent→mA/功率转换、物理黑场阈值不编。

LC-U新增准备范围定位为§10.1–10.5/A.4：可选Control/Session/内部Presenter、factory/options与原根桥接、权限/语言/Clock、三类投影和两个空STA消费者。上述UI规格增量既有接收保持，本轮只补根槽容量、观察等待和§13性能测点并在本原会话审核；可决定软件设计已闭合。尚不标ImplementationSpecificationReady或ModuleCoreImplementationReady；LC-U真实WPF/UIA/性能及设备、durability、fence、HIL、物理现场资格仍为PreparationIncomplete/NotReady，各自缺项见§15.1。C1/C2已接收合同、固定编码向量及其范围不因UI准备改变。仅以本页正文为交付，不新增报告、工程或测试文件。

### 15.1 全部批准范围的文档准备与剩余Owner

当前批准文档范围为LC-C1、LC-C2的Core＋明确Simulation测试端口、LC-U可选WPF指导及本轮LC-S1既有ledger可选技术持久化桥。本原会话复用已完成研究、接收和有效向量，补完A.5的完整codec/历史重放、Schema/SQL/注册、技术身份及原根恢复、双Host/Golden和性能方法。结论：上述全部范围无尚需开发者补猜的内部软件算法/API/构造/Owner/有界恢复/测试及测量方法决定。模块整体仍PreparationIncomplete；这是文档闭合，不是代码或生产资格。

| 范围/条件 | 软件文档准备结论与唯一落点 | 精确仍缺项及Owner | 未执行的实现/实测 |
|---|---|---|---|
| LC-C1 模型/编译/组合/证据及纯编码 | 已闭合；§1–4、A.1、§5/11.1/11.2/12–14；既有ModuleCoreImplementationReady保持。非视觉事务，HALCON适用性按§2，不欠图像算法 | 当前范围无软件设计欠账；代码启动前权威仓库/快照绑定由实现任务Owner确认；消费者Profile Owner采纳性能目标/样本数 | C#编译、Core断言/Golden/双消费者与性能诊断未执行，文档向量有效结论复用 |
| LC-C2 Core会话及Simulation测试端口 | 已闭合；A.2–3、§5.1–5.2/6–9/11–13，正常/故障脚本字段、时钟、barrier、原Owner及10s/120s/180s明确；既有ModuleCoreImplementationReady保持 | 当前范围无软件设计欠账；实现与Profile责任同上。测试夹具私有构造与数据结构为既定契约的实现细节，不能擅加公开协议 | actor/端口/资源/迟到与C2-A..K、双BCL Host实际运行及性能未执行 |
| 可分发新Simulator协议 | 不在批准范围；§5.2限定测试工程夹具，目前无非测试真实消费者/独立发布用途。因此不是当前模块文档缺项，也不设待关闭Ready门 | 将来确有消费者并获范围批准时由本模块原会话Owner定义新切片的公开factory/脚本/版本/限额/发布验收；当前不新增 | 未实现可发布Simulator，测试夹具不能作为其发布资格 |
| LC-U独立Control/Session/Presenter与宿主桥 | 已闭合；§10.1–10.5/A.4及§13。明确依DevExpress25.2.3已有组合、无UI同Core、三语/权限/Clock、原ledger-backed Controller、双空STA、根额度/安全单飞/观察/窗口恢复/性能计划；无软件欠账 | 本切片是WPF而非§3.1“无UI最小Core”切片，ModuleCoreImplementationReady不作替代UI准入标签。ImplementationSpecificationReady仍需消费产品Owner正式采纳其Contract/Schema/角色与根恢复/页面映射及实际公共程序集/产品接线资格；UI/性能Profile Owner采纳目标。这是具体集成及证据门，不是公开factory/Owner重设计 | Ui.Wpf构建、两个STA/1920×1080实际ClientArea/DevExpress键盘/UIA/三语/视觉/关闭恢复及真实性能均未运行；不得将模拟黑场当现场结果 |
| LC-S1技术持久化桥及真实durability/保留期 | 本轮文档闭合；§8.1/A.3、A.5.1–6：有界完整镜像/调用历史、codec/版本/hash、领域迁移/SQL/PG marshal、注册/技术身份、CAS/Unknown/两轴资源、双Host/Golden及性能方法明确。不自动标两种Ready | **lighting-control本原会话**按A.5实施桥与验收；**消费产品组合根/部署Owner**采纳精确Store/Scope/可信注册、迁移/最小角色/单权威、实际额度与RPO/RTO；**客户数据Owner**采纳容量/保存期。上游公开合同足够本设计消费，未发现必须修改上游端口的阻断 | 未创建/构建工程，S-A..H/双Host未运行；真实PG迁移/SQL/RLS/响应丢失/恢复/断电与保存期未测。文档Golden仅为规范字节校验，MemoryLedger/fake不证明耐久 |
| 真实lease/fence | 通用ILightingLeasePort及Adapter占用隔离、旧Owner未知不接管合同闭合（§3/8/A.3及§15.2）；没有已批准的生产设备占用authority实现 | 设备占用权威尚无可直接引用的已登记独立模块端口；由**消费产品组合根Owner**登记可信authority、物理设备键与唯一写入者，lighting-control本原会话在接入获批后负责具体实现映射；storage-database协调token不等于设备fence，device-signals lease也不替代它。具体需回应内容及物理Profile见§15.2 | 多进程争用/旧Owner写拒绝/重启恢复与实物fence未验；本地根槽、DB锁或连接消失均不能替代 |
| LC-H/物理及客户现场 | 现有厂商中立端口、Usage/能力/来源/失败边界闭合；具体SDK映射、目标设备与物理Profile仍为另行批准任务（§2/6/8/11/15、A.3） | 设备Adapter Owner冻结目标SDK/动作映射；设备厂商/客户工艺与安全Owner提供型号、boot/门控、单位转换、受信光学起止/黑场、公差/覆盖/时钟/热/互锁与现场验收值；缺这些事实只阻对应实物用途 | SDK/光学黑场/稳定/抖动/温升/时钟/HIL/FAT/SAT与客户生产验收未执行，不靠Simulation关闭 |

§13的Benchmark方法/负载/统计与有界资源判据已明确，TargetPending只指消费者尚未采纳的目标/样本计划，不是算法或测点缺失。平台最终Contract/Schema/Owner采纳责任在消费产品Owner；本文模块合同始终是自身Core/UI实现的唯一依据，不要求开发者从候选DTO猜测。后续出现具体生产端口需求须在获批切片修订部署规格；无关LC-C1/C2或本页UI软件设计不因此退回待设计。

本轮文档验证：定向检查本节分类与A.4/§10/13一致；反例走查普通额度满但原Stop/Close仍可达、整对预留拒绝、重复/并发Detach、Observe取消但Preview继续、迟到waiter不返额度、关键投影合并不丢原身份及跨根租约保护；核本地引用/围栏/公开签名/原合同区段保持。只说明所列软件设计断言和文档一致性，未执行产品代码/STA/性能/持久化/fence/HIL/物理现场验证，不新增过程材料。

### 15.2 通用端口、生产技术接入与物理Profile的精确分类

**① 当前模块通用软件合同。** 已能完整实施LC-C2及其可替换端口的调用/模拟契约，无缺失公开类型或必需参数。ILightingLedger唯一数据结构是A.3的LedgerReservation/PendingOpenReservation、LedgerProgress/PendingOpenProgress、LedgerFinalization/PendingOpenFinalization及LedgerReceipt；完整原请求bytes/hash/key、controller/device/session、原operation、正式Binding/Capability、Revision、Snapshot/Events与资源/唯一终态已确定。§8.1/A.3规定双唯一键、同值重放/异值冲突、Reserve先于设备作用、Append事实与head的同Revision CAS、Finalize唯一终态、原Pending发现后不换键、只读Query及保留墓碑；任何写/commit结果未知只回查原身份，不能以NotFound重发。物理事实与持久化结论独立，主库已提交不等于光源已完成。数据库SQL/生产codec不是这个通用接口的隐含默认，也不要求消费者使用未公开API。

ILightingLeasePort的可实施软件规则是：同一可信设备注册键下，Acquire串行/原子地建立唯一OwnerId=SessionId、LeaseId/Fence；同原请求重放不产生第二租约，另一session或冲突原请求不得取得占用。Renew/Release只命中同原LeaseId/Fence及其权威登记，checked递增的Fence不复用、不回绕；AuthorityReference变化/重启未恢复原记录、旧任务或物理关闭未知时保持占用未知，禁止新Owner接管。CheckedAt/ValidFor只表示许可有效期，**到期不等于Released，也不证明旧写者停止**；失效令原Controller停止新emit并走§8安全收尾，租约转交仍须§5/A.3原native/任务排空及归还事实。Release确认才Held=false/Released=true；确认前未知或释放错误不得删除占用行。Adapter只执行Open接纳的同session/LeaseId/Fence动作，禁止绕过共享Owner另开写连接；模拟authority以有界表/锁或CAS复现这些语义，算法不留给开发者选择“过期即接管”。跨进程/硬件的不可绕过隔离须由生产authority/SDK接入证明，普通本机检查不冒充它。设备键由宿主可信注册映射到物理设备，不能靠改ControllerId/端点别名创造第二排他域；原Controller的失败、查询及收尾接口不变。

**② 精确技术消费入口及Owner回应。** LC-S1已在本轮获准完成文档，并由A.5冻结全部lighting领域codec/Schema/SQL/Golden/技术身份设计。文档闭合不等于实现准入或发布；设备占用authority的具体生产接入仍独立，不由数据库桥隐含获得。

| 接入责任 | 已核实的唯一公开入口/指导位置 | 尚需冻结或上游回应，不能伪装物理门 |
|---|---|---|
| ledger技术持久化：storage-database（IM-066） | [storage-database指导](../storage-database/DEVELOPMENT-GUIDE.md) §6/6.1/6.3/6.6、§6.7.3、§7.1/7.2；命名空间Asun.Platform.StorageDatabase.Contracts。宿主以IStorageRuntimeFactory.CreateAsync建立原IStorageDatabase，OpenSessionAsync取得IStorageSession；写入仅ExecuteTransactionAsync(RegisteredTransactionRequest)，查询用ReadAsync(RegisteredReadRequest)，提交未知沿原技术OperationIdentity调用IStorageDatabase.QueryOperationAsync，任务/资源状态用GetTaskStatusAsync/ReleaseAsync；不直接调用后端私有SQL或IStorageDatabaseBackend | **lighting-control原会话**已在A.5冻结领域Schema/codec/SQL/Golden/注册/逐变更技术身份与原照明身份映射，后续负责实施；**storage-database原会话`01a109b6-49e5-7380-95ca-cbe3ba32b2c8`**的公开合同已覆盖单行CAS、Mutation RETURNING、有界结果、原技术查询与资源分轴，本轮无需增改上游API。实际PG保证及额度按其既有资格验收，不先假定完成。**消费产品组合根Owner**采纳StoreRef/Scope/可信authority/注册目录/角色与Profile |
| 占用记录可选技术落盘：同IM-066注册事务能力 | 仍用上述公开事务/读口承载领域占用记录；上游IStorageReferenceCoordinator.EnterAsync/ValidateAsync与StorageCoordinationToken是§6.3/6.6存储operation/引用/对象保护，不是ILightingLeasePort的替身 | **lighting-control原会话**在获批接入范围内定义设备占用记录的原Acquire/Renew/Release身份、CAS与恢复映射；**消费产品组合根Owner**首先登记真正的设备占用authority及不可绕过的发送路径/物理键。IM-066只回应记录事务与其存储writer隔离能力，不能回应“DB fence自动让灯设备拒旧命令”。软件记录与设备发送若不能线性化/隔离，生产写保持NotReady，不以两次RPC宣称原子 |
| device-signals/authorization不是设备占用authority | [device-signals指导](../device-signals/DEVELOPMENT-GUIDE.md) §7.1的IDeviceSignalAdapter/IDeviceSignalLease管理信号连接/通道；[authorization指导](../authorization/DEVELOPMENT-GUIDE.md) §5.3的authority fence是权限提交边界 | 当前无需这两个模块为照明增加公共租约API，不转发虚构的上游欠账。若真实灯与信号设备共用同一硬件连接，**device-signals原会话`01a10307-099b-7532-9471-d488c3d937d6`**需回应共享连接Owner/子租约排空边界，**lighting-control原会话**给出灯动作桥；尚未指定共用设备时不先造此桥。权限服务可供permit上游，权限Allowed不授设备排他或物理黑场 |

读写恢复固定区分三类身份：照明业务operation/hash（本模块ledger事实）、每次存储技术transaction identity/hash（存储原提交/资源事实）、设备Session/LeaseId/Fence（输出Owner）。技术提交Unknown不重发照明动作；存储资源已归还不释放设备lease；照明Closed不销毁宿主借用StorageRuntime；DB/设备不同fence不可互相替代。LC-S1软件文档闭合、代码未实施与生产部署未采纳分开；设备authority具体接入尚未批准/绑定，不能写成客户物理值待给或数据库自动解决。已有C1/C2与UI接收保持。

**③ 无法由公开资料替客户确定的部署事实。** 消费产品部署/运维Owner提供实际DB/介质位置、单权威拓扑、凭据/TLS/容量/IO故障域、供电/备份与实际RPO/RTO；客户质量/数据责任Owner批准保存期/法律保持/客户追溯窗口，设备厂商及现场安全Owner提供稳定物理身份、硬件是否能拒旧fence、禁触发/黑场测量及断网/掉电行为。实际保留天数、容量/时延门值、写缓存/flush断电耐久及光学/热/时钟阈值不能编造。保留期是客户政策输入，墓碑保留原hash/未知不TTL清除、禁止复用过期key/旧Owner接管等恢复算法已经明确，不随天数变化重新设计。公开软件技术选择/领域Schema/codec/SQL/占用隔离映射属于②，不能放进③掩盖未闭合软件接入。

本轮只定向回读上述既有公开入口，无新增研究或依赖；反例核对ledger回复未知不重发灯命令、到期旧Owner未知不转交、DB与设备fence互换被拒、存储commit/资源释放不升格为灯完成/lease归还、换物理别名不形成第二Owner。未实施生产Adapter，不创建软件工程/脚本/报告，也不宣称主库耐久、跨进程或硬件fence实测通过。

## 16. 来源与核对记录

- `docs/shared-modules/packages/PKG-009_Lighting.md`：职责、消费者和独立交付边界。
- `docs/shared-modules/guidance/02-platform/DEV-PLT-015_设备、相机、光源、运动与采集开发指导.md`：设备能力分层、采集时序、实际设置/回读、取消排空与两消费者验收。
- [PCBA-AOI 2026-10-06 光源指导快照](../../references/project-snapshots/PCBA-AOI/20261006/acquisition-lighting-control/README.md)：新版指导按独立清单归档，采纳范围见本页§3.1/16.1；来源中的AOI配方、SDK数值和产品流程不进入独立Core。
- `docs/references/project-snapshots/PCBA-AOI/20260927/original/docs/40-development/41-vision-platform/02-acquisition/光源控制抽象与照明配方开发指导.md`：LightingScene、逐步骤 Actual、Blackout、错误和 UI/Adapter 边界；该原件只读。
- `docs/13-contract-candidates/DEV-CONTRACT-002_功能卡Contract、Schema、State、Owner与提交绑定开发指导.md`：身份、CAS、幂等、提交/未知回执和资源语义。
- `ImageLibDotNet` 的结构光封装能力（如目标消费项目公共程序集/公开文档确认存在）：仅作结构光适配背景，不作为光源控制 API。
- `halcon算子手册/operators/add_scene_3d_light.html`（HALCON 26.05.0.0）：只读核对，属于 `scene_3d` 渲染光源，不是物理照明控制。
- `halcon算子手册/operators/set_framegrabber_param.html` 与目标消费项目 `ImageLibDotNet` 公共适配器：属于采集设备参数/回调，不是光源控制 API。
- `docs/references/project-snapshots/DZ-XVision/20261004/README.md`：来源性质、版本差异和只读边界。
- `docs/references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/C_Lights.cs`：连接方式、通道设置/关闭、Adapter 错误传播边界；旧连接和页面类型不迁移。
- `docs/references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/LampControllerUART.cs`：单通道/组宽写入、XOR 回读帧、有限响应等待的事实观察；协议范围和默认值不外推。
- `docs/references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/LampControllerUDP.cs`：固定长度通道帧、XOR 校验和有限响应窗口的事实观察；UDP ACK 不升级为物理事实。
- `docs/references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/OPTControllerAPI.cs`：多通道开关、强度/触发/序列表回读入口及厂商错误码存在性；具体数值/语义仍须目标 SDK 官方资料和能力探针确认。
- `docs/references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/ProgramP.cs`、`Runtime/CaptureTask.cs`：每采集步骤保存曝光与通道组合并深复制运行快照的事实观察。
- `docs/references/project-snapshots/DZ-XVision/20261004/original/DZ-XVision/PubParams.cs`：参数 old→new 变更审计的事实观察；不迁移产品日志文本或 MES 流程。




### 16.1 本轮实际研究与正文落点

- [.NET Channels 官方资料](https://learn.microsoft.com/en-us/dotnet/core/extensions/channels)，访问2026-10-09：bounded/full modes/背压和continuations；配合既有固定源码，不仅依据API简介选队列。主路线落点§8–9，满队列是明确拒绝；安全lane独立而不并发写SDK。
- [dotnet/runtime v10.0.0固定commit](https://github.com/dotnet/runtime/tree/60629d14374c56f1cb51819049ad1fa529307f8d)，复用[既有研究摘取](../../references/open-source/dotnet_runtime/60629d14374c56f1cb51819049ad1fa529307f8d/)。实读BoundedChannel.cs的TryComplete/TryWrite分支（约305–441行），BoundedChannelTests.cs的满Wait/Drop（72–94、221–239）、取消被阻塞writer（476–497）、continuations（638–655），两个Channels csproj；联网读取固定commit的测试/根LICENSE.TXT（MIT），不新增副本。Wait满TryWrite=false；DropWrite可能true却未保留数据；Channel完成不能证明device drain，取消一个等待写不撤销已有元素。测试用int，不证明SDK/设备行为。采用.NET10已有BCL接口，不复制runtime源码/测试；源码依赖System.Runtime/Threading/Memory等，测试依赖runtime公共设施/xUnit，旧framework条件分支不是平台新增依赖。未执行上游测试，不声明性能更优。落点§6A/8/9/12。
- DevExpress官方网页DockLayoutManager/TreeListView/PropertyGridControl/ChartControl的25.2请求本轮HTTP 403，浏览器仅到安全验证页，未冒称网页核验成功；当前没有dxdocs工具或匹配WPF skill。实际读取本机官方公共XML `C:\Program Files\DevExpress 25.2\Components\Bin\NetCore\DevExpress.Xpf.{Docking,Grid,PropertyGrid,Charts,Core}.v25.2.xml`，对应Grid DLL FileVersion=25.2.3.0。核实DockLayoutManager/布局SaveLayoutToStream/RestoreLayoutFromStream、GridControl/TableView/TreeListView及KeyFieldName/ParentFieldName、PropertyGridControl.SelectedObject、ChartControl/XYDiagram2D/LineStepSeries2D、`DevExpress.Xpf.Editors.Flyout.FlyoutControl`、SuperTip/SuperTipItem/ThemeManager；不是猜错的StepLineSeries2D或Xpf.Core.FlyoutControl。官方XML说明Restore从不可信来源可有安全风险，§10限制可信布局。复用[REF-004](../../references/REF-004_DevExpress与UI工作台官方研究基线.md)为参考，不以其26.1网页状态覆盖25.2.3。公共资料核实不等于WPF运行/键盘/渲染验收，不下载/核验用户已批准依赖授权。落点§10/12/14。
- [PCBA-AOI 20261006来源清单](../../references/project-snapshots/PCBA-AOI/20261006/acquisition-lighting-control/source-manifest.json)，文档SHA-256 `4ebaf7a387b798d3e2eafdb092fc63f9d81ae45e9f05ef95e5efd25f52d322f5`，只读复核§3.2、清理失败条款和逐步观察条款：迁移双白独立/复制组合/旧Actual失效/单步起点证据/Close未知保留Owner思想，具体客户SDK数值不采纳。原件已有来源/hash，不再复制成第二正式指导。
- 本轮没有新增图像算法、竞品内部实现推断、SDK实现或第三方运行时；同样本算法/HIL/WPF与产品Benchmark均未运行。引用原件承担依据核查，实施要求全部在本页正文/附录，不靠会话或.work脚本补契约。



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

## 附录 A：Module API Contract v0.2（唯一模块内部规格）

本节替代旧v0.1中未定义类型的代码形状。下列声明是实现规格，未作为本轮产品源码编译；实际实现用同名类型/签名，不以C-01～C-08候选DTO代替。全部在 `Asun.Modules.LightingControl`；UI类型单独在 `Asun.Modules.LightingControl.Ui.Wpf`。字段不可变不等于构造自动合法；所有公共入口校验形状/身份/预算，不能依赖调用方只经某个构造器。

### A.1 模型和纯 Core

正式Binding只表示已发现且通过能力校验的身份；`SessionSnapshot.Binding`仅在尚未Open或Open尚未形成正式身份的投影中允许为null。任何`LightingCommand`、`CloseLightingRequest`、`OperationQuery`、`StepQuery`和设备证据必须携带正式Binding。Open发现前的接纳/失败/排空生命周期事件允许Binding=null，由session/op/hash定位原Pending记录，不是设备作用证据；发现后所有事件必须有正式Binding。`PendingOpenIdentity`只用于Open接纳及历史查询，不进入场景或设备命令。

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace Asun.Modules.LightingControl;

public enum IntensityUnit { Percent=1, Milliamp=2, DeviceUnit=3, WattPerSquareMetre=4 }
public enum TriggerMode { Continuous=1, SoftwarePulse=2, HardwareTrigger=3 }
public enum ScenePurpose { ConfigureOnly=1, Emit=2 }
public enum QuantizationPolicy { Reject=1, Nearest=2, Down=3 }
public enum EvidenceKind { TransportReceipt=1, RegisterReadback=2,
    ElectricalMeasurement=3, OpticalMeasurement=4 }
public enum EvidenceSubject { Setpoint=1, Enabled=2, EmissionStart=3,
    EmissionEnd=4, Blackout=5, Temperature=6 }
public enum ComparisonStatus { Matched=1, Mismatch=2, Unknown=3, Unsupported=4 }
public enum PhysicalEffect { NotStarted=1, MayHaveStarted=2, Confirmed=3 }
public enum Recovery { None=1, CorrectInput=2, Query=3, Blackout=4, Reopen=5, ManualSafety=6 }
public enum SessionState { Closed=1, Open=2, Ready=3, Configured=4, Armed=5,
    Emitting=6, Cooling=7, Faulted=8, Blackout=9, Hold=10, Disposed=11 }
public enum OutputState { Unknown=1, CommandedOff=2, RegisterOff=3,
    PhysicallyOff=4, PhysicallyOn=5 }
public enum ReleaseScope { Operation=1, Session=2 }
public enum OperationStatus { Rejected=1, Accepted=2, Running=3, RunningUnknown=4,
    Completed=5, Failed=6, Cancelled=7, NotFound=8 }
public enum TransportKind { Serial=1, SerialNumber=2, Ip=3 }
public enum GroupRole { WritePartition=1, SafetyConstraint=2 }
public enum ApplyDisposition { None=1, Deferred=2, DisabledPreloadVerified=3 }

public sealed record Binding(string ControllerId, string DeviceId, string BootId,
    long Generation, string CapabilityHash);
public sealed record ClockStamp(string ClockId, long Ticks, long Frequency);
public sealed record Intensity(decimal Value, IntensityUnit Unit);
public sealed record ScalarRange(decimal Min, decimal Max, decimal Step);
public sealed record TickRange(long MinTicks, long MaxTicks, long StepTicks);
public sealed record ChannelCapability(string ChannelId, IntensityUnit Unit,
    ScalarRange Range, string? CalibrationHash, string? GeometryLabel,
    string? WavebandLabel, decimal? CertifiedMaxPowerWatts, decimal? MaxDutyCycle,
    TickRange? PulseWidth, TickRange? PulsePeriod,
    ImmutableArray<EvidenceKind> ReadbackKinds, decimal? ReadbackTolerance);
public sealed record GroupCapability(string GroupId, GroupRole Role,
    ImmutableArray<string> OrderedMembers, ImmutableArray<int> SupportedWriteWidths,
    int? MaxEnabled, decimal? MaxPowerWatts, bool DisabledPreload,
    bool HardwareSequence, bool StepObservation);
public sealed record CapabilitySnapshot(int ApiVersion, Binding Binding,
    ImmutableArray<ChannelCapability> Channels, ImmutableArray<GroupCapability> Groups,
    ImmutableArray<TriggerMode> TriggerModes, TickRange TriggerDelay,
    bool Simulation, string FirmwareReference, string SourceReference);
public sealed record ChannelSetting(string ChannelId, bool Enabled, Intensity? Requested);
public sealed record TriggerProfile(TriggerMode Mode, TimeSpan? Width, TimeSpan? Period,
    int Count, TimeSpan Delay, string? SourceReference);
public sealed record SceneStep(string StepId, int Ordinal, TimeSpan Window,
    string? CameraExposureReference, TriggerProfile Trigger,
    ImmutableArray<ChannelSetting> Channels);
public sealed record SceneDraft(int ApiVersion, Binding Binding, ScenePurpose Purpose,
    ImmutableArray<SceneStep> Steps);
public sealed record CompileLimits(int MaxSceneSteps, int MaxChannels, int MaxPayloadBytes);
public sealed record NormalizationChange(string FieldPath, string RequestedInvariant,
    string NormalizedInvariant);
public sealed record LightingFault(string Code, string FieldPath, bool IsRetryable,
    PhysicalEffect PhysicalEffect, Recovery Recovery,
    string? VendorCode, string? SourceReference);
public sealed record NormalizedScene(SceneDraft Scene, string SceneHash,
    ImmutableArray<byte> CanonicalBytes, CompileLimits CompiledLimits,
    QuantizationPolicy Quantization);
public sealed record CompileResult(NormalizedScene? Value,
    ImmutableArray<NormalizationChange> Changes, ImmutableArray<LightingFault> Faults);
public sealed record CanonicalLightingRequest(string Hash, ImmutableArray<byte> Bytes);
public sealed record RequestEncodingResult(CanonicalLightingRequest? Value,
    ImmutableArray<LightingFault> Faults);
public sealed record ChannelCombination(Binding Binding, string SourceSceneHash,
    ImmutableArray<ChannelSetting> Channels);
public sealed record PasteResult(SceneDraft Draft, CompileResult Compilation, bool Applied);
public sealed record LightingEvidence(string EvidenceId, Binding Binding,
    string OperationId, string? StepId, string? SceneHash, string? ChannelId,
    EvidenceKind Kind, EvidenceSubject Subject, Intensity? Value, bool? Enabled,
    ClockStamp ObservedAt, string SourceReference, string? CalibrationHash, bool Simulation);
public sealed record EvidenceRequirement(Binding Binding, string OperationId,
    string? StepId, string? SceneHash, string? ChannelId, EvidenceKind Kind,
    EvidenceSubject Subject, ClockStamp Now, TimeSpan MaxAge,
    Intensity? ExpectedValue, decimal? Tolerance, bool? ExpectedEnabled,
    string SourceReference, string? CalibrationHash, bool AllowSimulation);
public sealed record EvidenceComparison(ComparisonStatus Status,
    ImmutableArray<LightingFault> Faults);

public static class LightingCore
{
    public static string ComputeCapabilityHash(CapabilitySnapshot capability,
        CompileLimits limits); // 排除Binding.CapabilityHash后返回小写SHA-256
    public static CompileResult Compile(CapabilitySnapshot capability, SceneDraft draft,
        CompileLimits limits, QuantizationPolicy quantization); // 实现时添加方法体
    public static ChannelCombination CopyCombination(NormalizedScene source, string stepId);
    public static PasteResult PasteCombination(CapabilitySnapshot capability, SceneDraft target,
        string targetStepId, ChannelCombination combination, CompileLimits limits,
        QuantizationPolicy quantization);
    public static EvidenceComparison CompareEvidence(LightingEvidence evidence,
        EvidenceRequirement requirement);
    public static RequestEncodingResult EncodeOpenRequest(OpenLightingRequest request,
        CompileLimits limits);
    public static RequestEncodingResult EncodeCommandRequest(LightingCommand request,
        string usageProfileHash, CompileLimits limits);
    public static RequestEncodingResult EncodeCloseRequest(CloseLightingRequest request,
        CompileLimits limits);
}
```

这是C#声明规格，不把缺方法体的static class片段冒称可编译代码。ComputeCapabilityHash只接收除Hash自身外已满足能力形状/预算的输入，非法形状抛ArgumentException；宿主先构造Hash空的快照→计算→复制Binding.Hash→Compile，不在Core做设备发现。CompileResult成功仅当Value非空且Faults为空；量化Changes不等于错误，调用方必须确认新hash。失败Value=null，不返回部分场景。Paste失败返回输入target不变及失败Compilation；Copy无步骤/无效输入返回ArgumentException（纯函数无副作用）。Compile/Paste/Compare的可预期输入错误结构化返回；null顶级输入或null必需类型为ArgumentNullException，不产生运行生命周期。LC-C1没有异步取消/关闭/租约或本地日志持久化，不伪造运行命令。

Copy先用source.CompiledLimits重新编码Scene并核SceneHash/CanonicalBytes，不需要连接设备；不能仅凭一个NormalizedScene类型就信任其内容。Paste中SourceSceneHash仅为来源追溯，Binding/完整通道/单位/目标全场景Compile才决定合法性，不把字符串hash当编辑授权。Compile失败Faults按FieldPath ordinal再Code ordinal排序，Changes按步骤Ordinal/ChannelId/字段顺序，返回数量也受payload预算，遇到资源超限立即只返回ResourceLimit；未知枚举/非法形状的Compare返回Unknown+SceneInvalid，不默认Matched。

Binding五字段全部非空；Generation>0；ApiVersion=2；ID长度与字节大小受Limits约束，ordinal区分大小写；Clock Frequency>0，只有同ClockId/Frequency可比较，跨boot/epoch不可拼时长。集合default和未知enum拒绝。所有强度域Min>=0、Max>=Min、Step>0，Percent还须Max<=100；认证功率>0、占空在(0,1]，MaxEnabled在0..组成员数，时间范围MinTicks>=0、Max>=Min、StepTicks>0；Emit启用通道必须可得到合法大于0的脉宽（脉冲用途）。不能从负强度域推测双极输出支持。Capability.Binding.CapabilityHash按§4.2对快照编码重算（排除该hash字段），不得信任调用方自填。FirmwareReference/SourceReference为不可变证据引用；未知几何/波段用null，不默认Top/White。权威通道完整性以capability.Channels为准，每组OrderedMembers中的ID必须存在且不重复；同通道可归属于多个约束组，每组都校验，分组写事务路线由能力明确，不从颜色猜分组。

Group OrderedMembers保留协议成员顺序，hash也保留该顺序；Role=WritePartition必须构成Channels的无重叠完整分区，Role=SafetyConstraint可以重叠且不直接产生写命令，不能对同一通道反复写来满足两组约束。SupportedWriteWidths为去重正整数并排序；一次整组成员数必须在允许组宽内，安全约束组无写入能力。不能把声明的16通道完整写拆成若干8通道实现。Channel ReadbackTolerance非负且同Unit；测量Subject=Temperature不使用强度单位，Value=null，其具体温度事实由permit port独立承接，不伪装Intensity。Emit使用的写入组缺功率/MaxEnabled、通道缺认证功率或脉冲模式缺占空/频闪范围即SafetyProfileMissing；Continuous不用频闪占空，但必须有当前滚动热许可。ConfigureOnly可生成无执行资格的草稿。Continuous不做PulseWidth==0兼容：Width/Period必须null，Count0，Delay0；脉冲模式Width/Period均必填，单脉冲也需显式Period，硬件触发来源必填。TickRange基于MinTicks网格，时序不量化，非网格拒绝，避免静默改变同步条件。

EvidenceRequirement的ExpectedValue=null表示此subject不比较强度，不表示any-value通过；Setpoint须有值+Tolerance，Enabled须ExpectedEnabled，EmissionStart/End和Blackout必须是本用途受信OpticalMeasurement且有SourceReference，Blackout另由Profile的观测阈值/全通道覆盖确认。温度不能通过此简化API判安全。物理黑场使用controller整组受信来源时ChannelId=null并证明全部OwnedChannels关闭；逐通道来源必须集齐全部，缺一Unknown。Simulation证据永不满足AllowSimulation=false。

StepId/SceneHash为nullable且必须同时有值或同时null；步骤设定/使能/起止必须有精确step/hash，Open及关闭阶段Blackout为两者null，空字符串非法。EvidenceId/OperationId/SourceReference非空，ChannelId=null只表示已批准整组来源。Setpoint/Enabled必须为逐通道证据；EmissionStart须Enabled=true，EmissionEnd/Blackout须Enabled=false。Kind/Subject/源/标定不匹配为Mismatch，缺必要事实或超龄为Unknown，能力不支持为Unsupported；只有全部要求满足才Matched。CompareEvidence不支持用Subject=Temperature判定，明确返回Unsupported。

### A.2 运行请求、结果与事件

```csharp
public enum CommandKind { Apply=1, Arm=2, Execute=3, Preview=4,
    StopAndDrain=5, Blackout=6 }
public enum AdapterAction { DisableTriggers=2, ConfigureDisabled=3,
    ConfigureTrigger=4, ApplyForEmission=5, IssueTrigger=6, Readback=7,
    Blackout=8, Drain=9, Close=10 }
public enum EventKind { RequestReceived=1, RequestRejected=2, OperationAccepted=3,
    SceneValidated=4, RegisterApplied=5, ReadbackVerified=6, Armed=7,
    TriggerIssued=8, EmissionStarted=9, StepActualRecorded=10, EmissionEnded=11,
    LogicalCompleted=12, LogicalFailed=13, LogicalCancelled=14, Draining=15,
    Drained=16, ResourcesReleased=17, OperationCompleted=18, OperationFailed=19,
    OperationCancelled=20, SafetyCloseRequested=21, EvidenceUnknown=22 }
public sealed record CommandBudget(TimeSpan RequestDeadline, TimeSpan CleanupDeadline);
public sealed record OperationContext(string OperationId, string IdempotencyKey,
    long ExpectedStateVersion, string ActorReference, string PurposeReference,
    CommandBudget Budget);
public sealed record ChannelTolerance(string ChannelId, decimal Tolerance);
public sealed record OpticalBlackoutLimit(string? ChannelId, Intensity Maximum,
    string AuthorityReference);
public sealed record TrustedEvidenceSource(EvidenceKind Kind, EvidenceSubject Subject,
    string? ChannelId, string SourceReference, string? CalibrationHash);
public sealed record UsagePolicy(string ProfileHash, EvidenceKind RequiredReadback,
    ImmutableArray<ChannelTolerance> Tolerances, TimeSpan MaxReadbackAge,
    bool RequirePhysicalBlackout, ImmutableArray<OpticalBlackoutLimit> BlackoutLimits,
    ImmutableArray<TrustedEvidenceSource> TrustedEvidenceSources, bool AllowSimulation);
public sealed record RuntimeLimits(int MaxQueuedOperations, int MaxEvents,
    int MaxObservers, int MaxEventPayloadBytes, long MaxLedgerBytes,
    string ClockId, TimeSpan QueryDeadline, TimeSpan PermitPollInterval, TimeSpan LeaseRenewInterval,
    CompileLimits Compile);
public sealed record OpenLightingRequest(int ApiVersion, string ControllerId,
    string DeviceId, string SessionId, TransportKind Transport, string EndpointReference,
    OperationContext Operation, OperationContext DisposalOperation, UsagePolicy Usage);
public sealed record LightingCommand(int ApiVersion, Binding Binding, string SessionId,
    CommandKind Kind, OperationContext Operation, NormalizedScene? Scene);
public sealed record CloseLightingRequest(Binding Binding, string SessionId,
    OperationContext Operation);
public sealed record OperationQuery(Binding Binding, string SessionId,
    string OperationId, string CanonicalRequestHash);
public sealed record StepQuery(Binding Binding, string SessionId, string ExecuteOperationId,
    string SceneHash, string StepId, TimeSpan WaitDeadline);
public sealed record StepObservation(ComparisonStatus Status,
    ImmutableArray<LightingEvidence> Evidence, ImmutableArray<LightingFault> Faults);
public sealed record ResourceFacts(ReleaseScope Scope, bool Drained, bool Released,
    ClockStamp? ReleasedAt);
public sealed record SessionSnapshot(Binding? Binding, string SessionId, long StateVersion,
    SessionState State, OutputState Output, string? SceneHash, string? ArmedOperationId,
    string? ActiveOperationId, ImmutableArray<LightingEvidence> Evidence,
    ImmutableArray<LightingFault> Faults, ApplyDisposition ApplyDisposition);
public sealed record LightingOperationReceipt(string OperationId, string CanonicalRequestHash,
    OperationStatus Status, SessionSnapshot Snapshot, PhysicalEffect PhysicalEffect,
    ComparisonStatus Blackout, ResourceFacts Resources,
    ImmutableArray<LightingFault> Faults);
public sealed record OpenLightingResult(CapabilitySnapshot? Capability,
    PendingOpenIdentity? PendingIdentity, LightingOperationReceipt Receipt);
public sealed record PendingOpenIdentity(string ControllerId, string DeviceId,
    string SessionId, string OperationId, string CanonicalRequestHash);
public sealed record LightingEvent(long Sequence, EventKind Kind, ClockStamp At,
    Binding? Binding, string SessionId, string OperationId, string RequestHash,
    long StateVersion, ReleaseScope Scope, string? StepId,
    LightingEvidence? Evidence, LightingFault? Fault);
public interface ILightingController : IAsyncDisposable
{
    ValueTask<OpenLightingResult> OpenAsync(OpenLightingRequest request, CancellationToken ct);
    ValueTask<OpenLightingResult> QueryOpenAsync(PendingOpenIdentity identity, CancellationToken ct);
    ValueTask<SessionSnapshot> GetSnapshotAsync(CancellationToken ct);
    ValueTask<LightingOperationReceipt> SubmitAsync(LightingCommand command, CancellationToken ct);
    ValueTask<LightingOperationReceipt> QueryOperationAsync(OperationQuery query, CancellationToken ct);
    ValueTask<StepObservation> ObserveStepAsync(StepQuery query, CancellationToken ct);
    ValueTask<LightingOperationReceipt> CloseAsync(CloseLightingRequest request, CancellationToken ct);
    IAsyncEnumerable<LightingEvent> ReadEventsAsync(long afterSequence, CancellationToken ct);
}
public sealed class LightingCleanupException : Exception
{
    public Binding? Binding { get; }
    public string SessionId { get; }
    public string OperationId { get; }
    public string CanonicalRequestHash { get; }
    public LightingFault Fault { get; }
    public LightingCleanupException(Binding? binding, string sessionId, string operationId,
        string canonicalRequestHash, LightingFault fault);
}
public sealed class LightingEventStreamException : Exception
{
    public LightingFault Fault { get; }
    public long EarliestAvailableSequence { get; }
    public LightingEventStreamException(LightingFault fault, long earliestAvailableSequence);
}
```

实现类唯一为 `LightingController : ILightingController`，公开构造器：
`LightingController(ILightingAdapter adapter, ILightingLedger ledger, ILightingLeasePort leasePort, ILightingPermitPort permitPort, TimeProvider timeProvider, RuntimeLimits limits)`。构造只是保存经校验依赖，不启动连接/线程/查数据库。对象独占Adapter，首次Open后拥有session；成功Close后可显式重新Open新session/generation，成功Dispose后不可Open。外部ledger/lease/permit为借用依赖，Controller不Dispose宿主服务；Adapter成功关闭再Dispose一次。SDK关闭未知时不卸载仍被使用的库。

所有RuntimeLimits计数/字节限额及QueryDeadline/PermitPollInterval/LeaseRenewInterval均>0，ClockId非空，Compile子预算按§4校验；构造null依赖抛ArgumentNullException，非法预算抛ArgumentException，无副作用。所有端口返回集合不得default/null，Adapter/Capability/Evidence.Simulation须一致；AllowSimulation=true是允许而非要求模拟，AllowSimulation=false拒绝任何模拟设备/证据/ledger。CleanupException只有从未Open的Adapter归还失败允许SessionId/OperationId/Hash空（无ledger操作），Binding=null；未知半开Open失败也允许Binding=null，但必须有原Open SessionId/OperationId/Hash，其它失败必须有正式Binding及原收尾身份。

操作字段不可缺省；OperationId/key非空、expected>=0、两个deadline>0且由宿主预算限定。Open的SessionId由宿主显式提供并持久保留，用于未知Open恢复，ExpectedStateVersion=0，不产生秘密默认参数。Scene在Apply/Arm/Execute/Preview必须非空，其他Kind必须null；Arm/Execute/Preview必须ScenePurpose.Emit，ConfigureOnly不能布防。Preview仅Emit单步、有限窗口，不复用生产session的Armed许可。Arm/Execute必须精确等于已Apply/已Arm的SceneHash；篡改NormalizedScene的hash/bytes在接纳前重算拒绝。Stop/Blackout/Close按§8安全lane规则，同binding仍验证。

Usage.AllowSimulation=false不能连接Simulation Adapter/内存ledger；真实用途RequirePhysicalBlackout=true，若调用方设false，仅ConfigureOnly诊断可用，不能Emit或“安全释放”会话。ProfileHash绑定完整UsagePolicy和用途的许可/热要求，由宿主采纳的Profile提供，不是模块自行颁发授权。运行Tolerances覆盖所有受读回比较通道，0只代表明确精确比较；同时不超过能力允许公差，缺值拒绝，不扩大能力公差后隐含生产批准。RequiredReadback=RegisterReadback时仅比较原单位设定寄存器；Electrical/Optical只有实测Unit与Requested相同且已有转换CalibrationHash时才可比较。DeviceUnit请求＋W/m²实测可并列记录，但无转换不能做差或用图像分数替代readback。

BlackoutLimits必须覆盖全部OwnedChannels（逐通道）或唯一ChannelId=null的整控制器受信检测来源，不能混合/缺成员；Maximum为非负且有显式单位的物理观测上限，AuthorityReference非空，由物理Profile提供。可信OpticalMeasurement的Value须同单位且0<=Value<=Maximum、Enabled=false，整控制器来源另须资格证明覆盖全部输出；缺信号/超龄/遮挡/仪器故障不能判关灯。启动之前读取的是Open operation下StepId=null、SceneHash=null的安全观测，不能用后续步骤影像补它。本轮无这些物理阈值，真实路径保持外部门；Simulation可提供明确合成阈值。CompareEvidence对EmissionStart/End检查存在的受信物理事件，对Blackout的数值上限由Controller依据BlackoutLimits判定，不用ExpectedValue±Tolerance近似代替单侧上限。

Query预算为RuntimeLimits.QueryDeadline与调用方ct中较早者，不能终止原操作。NotFound回执Resources.Drained/Released=false且PhysicalEffect=MayHaveStarted；RequestRejected是已知无作用短路径，可Resources以Operation/true/true描述无需资源，不发布Draining/ResourcesReleased假事件。Accepted/RunningUnknown不是terminal；Completed/Failed/Cancelled必须Scope资源确认及ledger唯一Finalize。Open失败仍用Receipt保留session与PendingOpenIdentity；发现能力前Capability=null且没有正式Binding，例外仅供Open记录/历史查询，不接受后续设备Command；设备BootId未知时缺物理重启身份资格，不编boot。

Open先用明确SessionId＋controller/device＋operation/key规范化请求并查询/Reserve，之后才Acquire lease和Adapter.Open；不是打开设备后补accepted。其请求字节字段顺序为编码标识/域3、ApiVersion、LedgerOperationKind.Open、controller/device/session、transport/EndpointReference、OperationContext全字段、DisposalOperation全字段、UsagePolicy全字段（按record声明顺序，Tolerances/BlackoutLimits按ChannelId排序，null整组键先于其它；TrustedEvidenceSources按Kind数值/Subject数值/ChannelId/SourceReference/CalibrationHash逐键排序，字符串ordinal、null在前，完全重复项拒绝），绑定尚未发现的boot/generation不填入Open请求hash。Close请求固定编码标识/域5、ApiVersion=2、LedgerOperationKind.Close、完整binding/session与OperationContext。Submit使用LedgerOperationKind对应值而非同号CommandKind，按§4.2字段顺序和域4，不允许用不同Profile解释同一运行请求。limits/量化不在SceneHash里但在CommandHash里；NormalizedScene被调用方自行构造时Controller必须按其CompiledLimits/Quantization重新Compile并比SceneHash/CanonicalBytes，不能仅检查64hex格式。v0.2当前仍为未实施准备合同，本轮新增字段必须随首次合同采纳一起复核，不能将已保存旧准备字节当本版输入自动重算。

发现的新binding写为Append的不可变事实，不能重算已接纳Open请求hash。Open在正式Binding形成前只调用`FindPendingOpenAsync`/`ReserveOpenAsync(PendingOpenReservation)`，普通`FindByKeyAsync`/`ReserveAsync`只接受正式Binding；Open保留的Pending身份不能进入普通设备命令。ledger去重/operation查找主键使用controller/device/session/key或operation，不以boot/generation变化建立第二键空间；查询验证记录关联的历史binding，绝不把历史binding作为新设备动作许可。既有Open的回复丢失时，同SessionId/key/hash只查询旧记录，不能重新连接获取另一lease。新Open必须有显式新session并确认旧session安全释放；进程重启不能凭新实例解除旧Hold。

ReadEventsAsync是Controller单一事件读取出口，host负责一次读取后投影给多控件；afterSequence>=0且表示最后消费的Sequence，初始0从第一条读取，Sequence在Controller存活期严格递增。无法追到保留水位、重复并发读者或单载荷超MaxEventPayloadBytes时，枚举抛LightingEventStreamException，Fault.Code=LIGHT_RESOURCE_LIMIT、Recovery=Query并带EarliestAvailableSequence；不返回latest假装无缺口。消费者枚举取消抛OperationCanceledException并只解除订阅，不取消设备；没有事件时可等待ct，成功Dispose且缓冲读完后正常结束。事件队列满/关键事实无法保全仍按§8关闭准入和安全收尾，此故障不能依赖已满队列才能通知。未来多订阅广播不是默许无界event channel。

### A.3 可模拟端口与失败合同

```csharp
public sealed record AdapterOpenRequest(string ControllerId, string DeviceId,
    string SessionId, string OperationId, long Generation, string LeaseId, long Fence,
    TransportKind Transport, string EndpointReference, CommandBudget Budget);
public sealed record AdapterOpenResult(CapabilitySnapshot? Capability,
    PhysicalEffect Effect, bool Drained, bool NativeClosed,
    ImmutableArray<LightingFault> Faults);
public sealed record AdapterRequest(AdapterAction Action, Binding Binding,
    string SessionId, string OperationId, string LeaseId, long Fence,
    NormalizedScene? Scene, string? StepId, string? GroupId,
    CommandBudget Budget);
public sealed record AdapterReceipt(PhysicalEffect Effect,
    ImmutableArray<LightingEvidence> Evidence, bool Drained, bool NativeClosed,
    ImmutableArray<LightingFault> Faults);
public sealed record AdapterEvent(long Sequence, Binding Binding, string OperationId,
    string? StepId, LightingEvidence? Evidence, LightingFault? Fault);
public interface ILightingAdapter : IAsyncDisposable
{
    bool Simulation { get; }
    ValueTask<AdapterOpenResult> OpenAsync(AdapterOpenRequest request, CancellationToken ct);
    ValueTask<AdapterReceipt> PerformAsync(AdapterRequest request, CancellationToken ct);
    IAsyncEnumerable<AdapterEvent> ReadEventsAsync(long afterSequence, CancellationToken ct);
}
public sealed record LeaseRequest(string ControllerId, string DeviceId, string OwnerId,
    string OperationId, TimeSpan Deadline);
public sealed record LeaseReceipt(string LeaseId, long Fence, bool Held, bool Released,
    ClockStamp CheckedAt, TimeSpan ValidFor, string AuthorityReference,
    ImmutableArray<LightingFault> Faults);
public interface ILightingLeasePort
{
    ValueTask<LeaseReceipt> AcquireAsync(LeaseRequest request, CancellationToken ct);
    ValueTask<LeaseReceipt> RenewAsync(string leaseId, long fence, TimeSpan deadline, CancellationToken ct);
    ValueTask<LeaseReceipt> ReleaseAsync(string leaseId, long fence, TimeSpan deadline, CancellationToken ct);
}
public sealed record PermitRequest(Binding Binding, string SessionId,
    string OperationId, CommandKind Kind, string? SceneHash, string ProfileHash,
    string ActorReference, string PurposeReference, string LeaseId, long Fence,
    TimeSpan Deadline);
public sealed record PermitReceipt(bool Allowed, Binding Binding, string SessionId,
    string OperationId, CommandKind Kind, string? SceneHash,
    string ActorReference, string PurposeReference,
    string ProfileHash, string LeaseId, long Fence, ClockStamp CheckedAt, TimeSpan ValidFor,
    bool InterlockConfirmed, bool ThermalApproved, bool TriggerGateConfirmed,
    bool CoolingComplete, string AuthorityReference, ImmutableArray<LightingFault> Faults);
public interface ILightingPermitPort
{
    ValueTask<PermitReceipt> CheckAsync(PermitRequest request, CancellationToken ct);
}
public enum LedgerOperationKind { Open=1, Apply=2, Arm=3, Execute=4, Preview=5,
    StopAndDrain=6, Blackout=7, Close=8 }
public sealed record LedgerReservation(Binding Binding, string SessionId, LedgerOperationKind Kind,
    OperationContext Operation, string RequestHash, ImmutableArray<byte> CanonicalRequest,
    long AcceptedStateVersion, ReleaseScope Scope);
public sealed record PendingOpenReservation(PendingOpenIdentity Identity,
    OperationContext Operation, string RequestHash, ImmutableArray<byte> CanonicalRequest,
    long AcceptedStateVersion);
public sealed record LedgerReceipt(bool Durable, bool Conflict, bool Existing,
    long Revision, LightingOperationReceipt? Operation, CapabilitySnapshot? OpenCapability,
    ImmutableArray<LightingFault> Faults);
public sealed record LedgerProgress(OperationQuery Query, long ExpectedRevision,
    SessionSnapshot Snapshot, ImmutableArray<LightingEvent> Events);
public sealed record LedgerFinalization(OperationQuery Query, long ExpectedRevision,
    LightingOperationReceipt Terminal);
public sealed record PendingOpenProgress(PendingOpenIdentity Identity, long ExpectedRevision,
    CapabilitySnapshot? Capability, SessionSnapshot Snapshot, ImmutableArray<LightingEvent> Events);
public sealed record PendingOpenFinalization(PendingOpenIdentity Identity, long ExpectedRevision,
    LightingOperationReceipt Terminal);
public interface ILightingLedger
{
    bool Simulation { get; }
    ValueTask<LedgerReceipt> FindPendingOpenAsync(PendingOpenIdentity identity, string key,
        CancellationToken ct);
    ValueTask<LedgerReceipt> ReserveOpenAsync(PendingOpenReservation request,
        CancellationToken ct);
    ValueTask<LedgerReceipt> QueryOpenAsync(PendingOpenIdentity identity, CancellationToken ct);
    ValueTask<LedgerReceipt> AppendOpenAsync(PendingOpenProgress progress, CancellationToken ct);
    ValueTask<LedgerReceipt> FinalizeOpenAsync(PendingOpenFinalization request, CancellationToken ct);
    ValueTask<LedgerReceipt> FindByKeyAsync(Binding binding, string sessionId,
        string key, string requestHash, CancellationToken ct);
    ValueTask<LedgerReceipt> ReserveAsync(LedgerReservation request, CancellationToken ct);
    ValueTask<LedgerReceipt> AppendAsync(LedgerProgress progress, CancellationToken ct);
    ValueTask<LedgerReceipt> FinalizeAsync(LedgerFinalization request, CancellationToken ct);
    ValueTask<LedgerReceipt> QueryAsync(OperationQuery query, CancellationToken ct);
}
```

端口方法全有有限deadline：Adapter从Budget读取；Permit/Lease请求直接传；ledger等待由Controller从剩余RequestBudget给linked token限定，安全收尾用剩余CleanupBudget。取消token是请求，不是native中止证明；端口未知失败必须映射Fault而非无异常false。Adapter Perform动作与Scene/StepId/GroupId的合法组合由§6/9规定：DisableTriggers/Blackout/Drain/Close无场景且StepId/GroupId=null，配置/发光/触发有精确Scene，逐步/逐写入分区动作有StepId/GroupId；Readback可带Scene/StepId/GroupId指定原operation对账，无场景仅用于Open或关闭观测。控制器原子硬件序列可StepId=null，但不伪造逐步观察；多写入分区由能力声明的事务顺序串行，每区先验证配置和回读，再进入下一分区，局部失败立即收尾，不能保证跨分区硬件原子性。GroupId不得指SafetyConstraint或任意字符串。无支持动作返回Unsupported/NotStarted；返回迟到/不确定仍保留Effect=MayHaveStarted。证据为只读事实，不接受Adapter“成功”布尔值替代其中字段。

Adapter请求携带原session/operation/LeaseId/Fence，Adapter必须核对Open时接纳的占用身份，不让旧Owner直接写新占用；本机核对不冒充硬件fencing资格。AdapterOpenResult.Capability非空且通过Controller校验才形成正式binding。能力无返回但连接可能半开时保留原Adapter/lease和Open记录为Hold；Adapter.Open须在原Cleanup预算内尝试自己的半开资源收尾，Effect/Drained/NativeClosed分别记录，不能用Capability=null推断未打开。只有Effect=NotStarted、Drained=true、NativeClosed=true明确证明从未取得native连接/未发输出动作时可释放刚取得的lease；否则缺binding/物理黑场资格不得构造任意BootId去调用Perform，交原Owner查询和宿主受保护恢复，不提供无契约重连。

WritePartition动作按GroupId ordinal顺序，分区内按OrderedMembers顺序；不能用输入Groups枚举顺序改变执行。多步Emit只在所有写入分区HardwareSequence=true时接纳为整序列，且全部StepObservation=true才能承诺逐步Observe；否则返回Unsupported，宿主将草稿拆成独立单步场景。安全约束组无写入能力，其SupportedWriteWidths必须空、DisabledPreload/HardwareSequence/StepObservation=false；其MaxEnabled/MaxPowerWatts仍逐步校验，不借安全组扩展写入资格。

Permit在Arm和每个真实emit前检查当前binding/hash/Profile/lease/fence/单调有效期，Returned Allowed只是其中一项，Interlock/Thermal/TriggerGate缺一不可用；Continuous仍需明确“触发不适用且禁止外部触发”的门控证据。许可端口源引用需宿主可信authority，不能用UI禁用按钮伪造。执行期间监听Adapter故障/健康，按RuntimeLimits.PermitPollInterval重新核许可与热预算，Permit过期前必须完成核验，否则Stop/Hold；通知由host调用StopAndDrain。轮询和LeaseRenewInterval必须显式正值且短于来源许可/租约有效期，由部署Profile采纳，无默认间隔；线程调度延迟不能替代硬件热/安全保护。关灯后CoolingComplete不明时保持Cooling；只有后续当前同binding可信permit的CoolingComplete与热/互锁均确认才Ready，采集完成/软件sleep不自动恢复许可。

Permit必须精确回显SessionId/OperationId/Kind/ActorReference/PurposeReference，避免另一操作者或用途的旧许可被复用；Preview所有内部阶段均使用Kind=Preview和本操作用途。Open及收尾冷却查询使用Kind=StopAndDrain、SceneHash=null、本次Open/安全操作身份；其Allowed只表示该查询/恢复用途，不授权Emit。Cooling轮询保留最近收尾操作的身份，哪怕Snapshot.SceneHash已清空也不生成新生产许可。Controller发现许可到期/撤销/故障即自行进入安全lane，不能等待host通知；host收到外部变化也可主动StopAndDrain。

Lease ID/fence由宿主权威提供，OwnerId固定为宿主明确的SessionId，Controller不能仅生成GUID就称硬件排他。Held=true须Released=false、Fence>0、LeaseId/AuthorityReference非空、Faults为空，CheckedAt域/频率同当前TimeProvider且不在未来，ValidFor>0；以CheckedAt+ValidFor计算到期，返回时消耗掉的时间不能重新授予。Renew只接受同LeaseId/Fence/AuthorityReference，RuntimeLimits.LeaseRenewInterval必须小于当前剩余有效期；失效/续租失败按§8.3收尾。Release只有Held=false/Released=true才确认归还，未知保持原占用。Permit也按CheckedAt+ValidFor扣掉端口等待时间，并核AuthorityReference为宿主部署的许可权威，不能只比轮询间隔与原ValidFor。lease/permit端口可信性来自宿主注入服务及部署资格，不由回执字符串自证。Open acquired后SDK失败仍按native/lease实际状态收尾，不能遗漏连接半开资源；不持锁调用lease/permit。

Reserve原子唯一键含controller/device/session/idempotencyKey，以及独立唯一operationId；boot/generation不是新去重命名空间。相同key/hash返回既有accepted/terminal，异hashConflict=true；已用operationId换key也冲突。AcceptedStateVersion来自actor核验，不是另一个ledger全局计数器。Append按Revision CAS追加不可变Events与Snapshot，不覆盖历史Actual；Finalize按Revision CAS和terminal唯一约束，重复同hash/同terminal返回原记录，异terminal冲突。ledger中无记录/Durable未知时不返回Completed；Query缺记录不会执行动作。真实端口序列化/API版本/retention/fencing/部署资格另审，本文未引入数据库实现或宣称分布式恰好一次。

LedgerReceipt形状：Durable=true/Conflict=false/Existing=false/Operation=null/Faults空仅表示可靠查询未找到；Existing=true必须带原Operation，Reserve新成功须Durable=true/Existing=false且带Accepted回执与Revision。Conflict=true不得执行设备，故障/未知须Faults非空；Controller不把Operation=null推断为成功。归档墓碑保留原op/hash与资源/终态事实供重放，不回到未找到。Simulation ledger按本页请求/事件/快照字段编码的实际字节计入MaxLedgerBytes，容量不足时不改已存在记录；真实ledger的介质计数/retention/崩溃恢复必须由真实端口规格冻结，未纳入LC-C2的软件模拟接收。

Open专用端口补充规则：PendingOpenIdentity五字段全部非空，CanonicalRequestHash为原Open编码结果；ReserveOpen.OperationId必须等于Identity.OperationId、RequestHash等于Identity.CanonicalRequestHash、Expected/AcceptedStateVersion=0，Scope固定Operation。FindPendingOpen使用controller/device/session/key与operation双唯一规则，不以空Binding查询。AppendOpen/FinalizeOpen始终以原Pending身份＋Revision CAS定位，即使发现后Snapshot.Binding已经非空也不改历史键；QueryOpen从该记录快照恢复Capability（发现时完整快照随AppendOpen保全），OpenLightingResult.PendingIdentity在每个已编码Open回执中必须回显原身份。QueryOpen与普通Query使用相同有限预算/取消/NotFound语义，不发设备动作；找不到时Capability=null、Snapshot.Binding=null、PhysicalEffect=MayHaveStarted、Resources未确认。

PendingOpenProgress增加的Capability见公开字段，null只表示尚未发现；一旦非空必须与Snapshot.Binding相同并保全完整能力，后续不得用null覆盖。Open形状非法而无法编码时Rejected回执PendingIdentity=null；已编码但未接纳仍回显身份，不能把Rejected当已Reserve。未知半开且无正式Binding的Dispose只能等待/查询原Open的内部cleanup，预算到期抛带原Open SessionId/OperationId/Hash、Binding=null的CleanupException；不得生成CloseLightingRequest或调用正式Perform。只有Open资源确已收尾、native已关且lease已归还才可Dispose Adapter；原Pending Owner不能被新实例替代。

LedgerReceipt.OpenCapability只用于Open记录且与已保全Snapshot.Binding相同，发现前及非Open记录必须null；重复Open或QueryOpen从这个字段取得原能力，不再调用设备发现。ReserveOpen的唯一operationId/场景无关hash/CAS/容量/故障规则与普通Reserve相同，Open记录Kind固定Open，CanonicalRequest必须与原编码字节一致。Pending身份五字段不含key，因此FindPendingOpen另传原key；QueryOpen只以完整Pending身份查，Kind不是Open时返回Conflict，不查询任意普通操作。

### A.4 可选控件公开边界

本节维护LC-U已接收的唯一增量合同及本轮有界等待/根额度窄补，替代此前仅有Context/回执事件的未接收简写；A.1–A.3不变。本轮内容审核与验证由本永久原会话完成，接收/文档准备不授予真实WPF/UIA/性能或设备资格。所有下列类型位于`Asun.Modules.LightingControl.Ui.Wpf`。公开factory创建一个UI Session，包含一个Control和一个内部`LightingEditorPresenter`；Presenter不公开构造、不成为新的设备Session，也不提供额外状态/命令API。Session公开Control属性，无设备Dispose/Close入口；宿主以Control.DetachAsync结束UI挂接，再按§5处理Core。Control无公开构造器，宿主将factory返回的Control置入Content，不要求XAML秘密初始化。

```csharp
using System;
using System.Collections.Immutable;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Controls;
using System.Windows.Threading;
using Asun.Modules.LightingControl;

namespace Asun.Modules.LightingControl.Ui.Wpf;

public sealed record LightingEditorOptions(TimeProvider TimeProvider, string ClockId,
    int MaxDiagnostics, int MaxTimelinePoints, int MaxVisibleOperations,
    TimeSpan ProjectionInterval, TimeSpan QueryWaitDeadline);
public sealed record LightingEditorContext(ILightingController Controller,
    CapabilitySnapshot Capability, SessionSnapshot Snapshot, SceneDraft Draft,
    CompileLimits Limits, QuantizationPolicy Quantization,
    bool ReadOnly, bool CanPreview, bool CanStop, string ActorReference,
    string PreviewPurposeReference, string SafetyPurposeReference,
    CommandBudget Budget, string CultureName, ILightingEditorOwnerPort OwnerPort);
public sealed record LightingEditorAccess(bool ReadOnly, bool CanPreview, bool CanStop);
public sealed record LightingDraftChange(SceneDraft Draft, CompileResult Compilation,
    ImmutableArray<string> ChangedStepIds);
public sealed record LightingEditorSubmission(LightingCommand Command,
    CanonicalLightingRequest Encoding, LightingCommand? PreviewStop,
    CanonicalLightingRequest? PreviewStopEncoding);
public sealed record LightingEditorRecovery(OperationQuery Query,
    LightingOperationReceipt? Receipt, string ReasonCode);
public sealed record LightingEditorProjection(SessionSnapshot Snapshot,
    long EventSequence, ImmutableArray<LightingOperationReceipt> Operations);

public interface ILightingEditorOwnerPort
{
    ILightingController Controller { get; }
    UsagePolicy Usage { get; }
    RuntimeLimits RuntimeLimits { get; }
    TimeProvider TimeProvider { get; }
    ValueTask<LightingOperationReceipt> SubmitAsync(
        LightingEditorSubmission submission, CancellationToken waitCt);
    ValueTask<LightingOperationReceipt> QueryAsync(OperationQuery query,
        CancellationToken waitCt);
    ValueTask<StepObservation> ObserveStepAsync(StepQuery query,
        CancellationToken waitCt);
}
public static class LightingEditorFactory
{
    public static LightingEditorSession Create(Dispatcher dispatcher,
        LightingEditorOptions options); // 声明规格，实施时添加方法体
}
internal sealed class LightingEditorPresenter
{
    internal LightingEditorPresenter(Dispatcher dispatcher,
        LightingEditorOptions options); // 仅factory使用；不持有设备Owner
}
public sealed class LightingEditorSession
{
    internal LightingEditorSession(); // 仅factory使用
    public LightingEditorControl Control { get; }
}
public sealed class LightingEditorControl : UserControl
{
    internal LightingEditorControl();
    public ValueTask AttachAsync(LightingEditorContext context, CancellationToken ct);
    public ValueTask<LightingOperationReceipt?> DetachAsync(CancellationToken ct);
    public void UpdateAccess(LightingEditorAccess access);
    public void UpdateSnapshot(SessionSnapshot snapshot);
    public void UpdateProjection(LightingEditorProjection projection);
    public void SetCulture(CultureInfo culture);
    public ValueTask<LightingOperationReceipt> PreviewAsync(string stepId, CancellationToken ct);
    public ValueTask<LightingOperationReceipt?> StopPreviewAsync(CancellationToken ct);
    public ValueTask<LightingOperationReceipt> BlackoutAsync(CancellationToken ct);
    public ValueTask<LightingOperationReceipt> QueryAsync(OperationQuery query, CancellationToken ct);
    public ValueTask<StepObservation> ObserveStepAsync(StepQuery query, CancellationToken ct);
    public event EventHandler CultureChanged;
    public event Action<LightingDraftChange> DraftChanged;
    public event Action<LightingEditorRecovery> RecoveryRequired;
}
```

**factory/options与必需输入。** Create及全部Control入口必须在指定Dispatcher的STA线程；dispatcher不是当前线程、线程非STA或已shutdown时抛InvalidOperationException，无设备动作。null输入抛ArgumentNullException，非法options/context/access/枚举/预算抛ArgumentException；options三项计数及两个期限均>0、ClockId非空、TimeProvider.TimestampFrequency>0。Create不启动设备/事件读取/持久化/后台常驻任务；Presenter由factory直接构造，不能依赖全局service locator。MaxTimelinePoints只限制绘图采样，MaxDiagnostics只限制普通诊断，MaxVisibleOperations只限制分页可见数；原根的未结操作不能因此淘汰。ProjectionInterval为普通快照合并间隔，关键错误/Unknown与安全意图立即投递；不作为设备时序/许可期限。

**有界UI根与等待。** 原根沿§5恢复槽计算本session保全operation额度`checked(3 * RuntimeLimits.Compile.MaxSceneSteps + 3)`，构造前核乘加未溢出；不增加Core字段或新的Owner。Open、预持DisposalClose和根finally Stop占3项；每次预览在调用前原子预留Preview/其Stop两项，即使Stop最终未发也保留身份，显式Blackout占1项，重入同请求不重复计数。普通额度不足以容纳整对时返回原请求的Rejected/LIGHT_RESOURCE_LIMIT（未接纳、无设备作用，资源按A.2预拒绝短路），不能先发Preview后发现Stop无处保全。历史终态身份保持到session安全关闭，不能在控件Detach或翻页时删除；重新预览额度耗尽时提示宿主关闭/恢复原session，只有§5返槽条件满足后才能显式新session。必要安全单飞使用已预留项，不依赖普通余量，余量不足不妨碍原根Close/Dispose。原Actor/安全用途对应预持请求，本session内不更换执行者；改Actor须原根正常收尾后显式新session，UpdateAccess只改权限投影。

若显式新Blackout连一项都不能保全，不接纳该新身份、不得绕过保存直接调用Core；原根仍主动加入已预持的根Stop安全单飞，并以该原Stop回执/查询反馈“请求额度已满，正在停止；请由宿主关闭会话”。新Blackout的Rejected与原Stop结果分别投影，不显示Blackout完成；同一满槽反复点击只加入该根Stop，不换其ID/hash或生成新任务。该情况停止新Preview直至§5原根收尾/返槽，UI不自行Close。U-H必须同时断言新Blackout未接纳、原Stop尝试次数1、Close/Dispose仍可达，不能因为根表满而停掉必要安全动作。此反馈资源键为Lighting.RequestLimitStopping，按§10三语资源规则，zh-TW为“請求額度已滿，正在停止；請由宿主關閉工作階段”，en-US为“Request limit reached. Stopping. Close the session in the host.”；本地stop请求不代表灯已关。

UI Dispatcher仅允许一个普通投影待处理工作、一个关键回执/故障待处理工作；普通快照只保留最新合法水位，关键项按原根operation身份保留有界最新回执及故障摘要，完整历史仍在原ledger/恢复槽，不对每条事件无限BeginInvoke。关键未确认项只有原根同身份证据才可更新，普通新快照不清除；根额度外的OperationQuery/回执拒绝。MaxVisibleOperations仅分页上限，原根保全表受上段额度约束；MaxDiagnostics满保留错误摘要/原operation查询入口，不能截断不可恢复身份。Unloaded/Detach撤销未执行的普通UI工作，原根任务不撤销；同控件代次的重复Detach加入一次解除挂接，不对已解除挂接再次增长代次或新建Stop。

QueryAsync只允许原根已保全OperationQuery；ObserveStepAsync只允许原根已保全Preview/Execute及其编译SceneHash/StepId，StepQuery.WaitDeadline必须>0且<=options.QueryWaitDeadline。原根转接既有Controller.ObserveStepAsync，形成每次仅一次AsTask的waiter，有限等待使用本根同Clock TimeProvider及独立query/observer token，不触发设备写或重新Reserve。Query/Observe的UI并行等待额度共用RuntimeLimits.MaxObservers；满则在建立新waiter前以LIGHT_RESOURCE_LIMIT拒绝，已存在的安全/原Owner不受影响。调用方ct只取消其查询/观察等待，Observe等待解除不取消Preview；到期/缺证返回Core原Unknown/Unsupported及Faults，绝不把StepObservation当operation终态或此刻正在发光。尚未退出的waiter Task由原根持有，只有实际退出后回收额度；Detach后Task迟到只交原根，不回填新context。上下文形状/身份非法抛ArgumentException且零调用；有效请求的资源/期限错误沿Core原结构化回执，UI不造新设备事实。

Attach采用context原字段，额外必需OwnerPort而非可选默认。Controller必须ReferenceEquals(OwnerPort.Controller)，options.TimeProvider必须ReferenceEquals(OwnerPort.TimeProvider)，ClockId等于原RuntimeLimits.ClockId；Limits等于原RuntimeLimits.Compile，Budget与QueryWaitDeadline不超过宿主冻结预算（QueryWaitDeadline<=RuntimeLimits.QueryDeadline）。OwnerPort.Usage就是原Open的Usage，含原ProfileHash、读回/年龄、可信源和物理黑场要求，不能给UI另造宽松Usage。OwnerPort的Query/ObserveStep必须由§5组合根使用**原ledger-backed Controller**实现：Controller内部借用的原`ILightingLedger`、lease和permit不作为UI属性暴露，UI不能直接写ledger、续租/释放lease或核permit。ObserveStep返回的Evidence必须沿原Binding/session/operation/step/SceneHash、EvidenceId、SourceReference、CalibrationHash、ObservedAt和Simulation字段，黑场缺失/过期/只有寄存器0仍按A.1/A.3为Unknown；UI不自行读取Adapter。实际durability/fence资格仍按A.3/§15。宿主保证这些只读属性在该挂接内不变，改变Controller/Clock/Usage须先Detach再绑定新根，不用UpdateAccess偷换它们。

Snapshot须有正式Binding、非空SessionId且匹配Capability/Draft，Capability/hash及草稿校验复用A.1；非法Draft通过CompileResult显示待修，不自动改原稿，身份/能力非法则Attach拒绝。CultureName是宿主明确CultureInfo，当前必须支持zh-CN/zh-TW/en-US；不支持的culture拒绝并保留旧语言。ActorReference、两个PurposeReference非空、Budget显式正值；CanPreview=true要求ReadOnly=false且CanStop=true。CanPreview只是宿主投影，实际按钮还须Ready/Configured、无本根未结/未知、有效草稿及量化确认，Core仍核permit。Attach只建编辑副本/投影，设备调用和事件订阅为0；不Open/Apply/Arm、无隐藏校验设备读回。

**原根桥接与提交。** ILightingEditorOwnerPort由宿主在§5原组合根实现，仅转接已存在Core Controller与原恢复槽；不是新的ledger协议/通用模块。Submit限定Preview/StopAndDrain/Blackout；其他Kind在桥接准入前拒绝，无设备动作。宿主先按A.1用原Usage.ProfileHash与CompileLimits重编码并比Encoding完整bytes/hash，核原Binding/session/Actor/Purpose/预算及本根角色。预览提交必须携带独立ID/key的PreviewStop及其编码，Kind=StopAndDrain、Scene=null、同Binding/session、ExpectedStateVersion=0、原Actor/SafetyPurpose/Budget；安全lane对旧version的处理直接沿§8。非Preview提交两项PreviewStop字段必须null。桥接在调用Controller前将原Preview和这个Stop身份/bytes/hash保全到原根槽，映射为该Preview唯一收尾请求；已有槽冲突或无普通容量就拒绝新Preview，不能驱逐未知Owner或丢安全身份。

保全后原根创建并持有Controller.SubmitAsync的原Task及观察/恢复任务，再返回可取消的等待。waitCt仅取消桥接调用者等待，不传成终止安全任务的token；Core业务取消/安全接纳沿§5/§8，不复制状态机。即使UI未收到回执/事件handler失败/Dispatcher已退出，原根仍保留任务、请求和未知恢复；不能把RecoveryRequired事件作为唯一保全渠道。Query只转接原Controller.QueryOperationAsync，有限期限沿RuntimeLimits.QueryDeadline，UI等待另受QueryWaitDeadline，不读第二事件流，不借Query重发设备命令。桥接Exception/取消不证明未接纳；编码成功且已交原槽的操作始终用原OperationQuery定位。

PreviewAsync把所选step复制为Ordinal=0且保留StepId/完整通道/Window/CameraExposureReference/Trigger的单步Emit草稿，Compile后确认新SceneHash/Changes；不改变原多步草稿。每个新Preview及预持Stop各生成一次Guid字符串OperationId/key（彼此不同），取最新Snapshot.StateVersion用于Preview，并在首次调用前编码/保全。内部配置/布防/执行走Core Preview单一operation，UI不分发Apply/Arm/Execute。尚未结清的Preview拒绝第二个；相同未知请求只Query。编码失败无设备调用，结构化故障显示在原字段。

StopPreviewAsync无自身在途Preview返回null，不能停止宿主生产operation；否则提交预持的Stop请求并加入本挂接的同一Task，重复点击/取消/失焦/Detach不改ID/key/预算、不重复创建Stop。BlackoutAsync是用户显式操作，要求CanStop且同正式Binding/session，由原根许可/安全lane判定；UI当前在途Blackout重复点击加入同一请求，未知时Query，不另发同义请求。无黑场物理证据不显示成功。UpdateAccess撤权立即停止新意图；自己已发Preview的必要生命周期Stop使用原预持安全身份，不因CanStop后来变false抛弃。这个收尾权限由原宿主根核定，UI布尔值不授予新的设备权力。没有自己的Preview时撤权/失焦/Detach设备命令数0。

**投影、线程与身份。** 宿主是唯一ReadEvents消费者；取同根事件/Query回执后在控件Dispatcher调用UpdateProjection。EventSequence>=0且不回退，Operations集合不可default、只含本根已保全身份，每回执hash必须匹配原请求；未知/关键故障保留在原根恢复槽。StateVersion只在同session/完整Binding内递增；更旧快照忽略，相同version且事实相同视为幂等，相同version内容矛盾拒绝并显示诊断，不能任选一个。更高version不替代旧operation的终态/资源事实。事件水位仅表示宿主实际连续消费或Query对账过的位置，事件缺口由宿主Query原请求/快照追齐，不自行假增水位；合并快照不合并掉Operations中的关键回执。UpdateSnapshot是只更新快照的便捷入口，沿同样核对规则，不推进EventSequence、不清操作恢复列表。跨Binding/session拒绝并要求Detach/Attach。

请求与实际展示沿§10.4/A.1/A.3，不新造设备“实际状态”DTO。Snapshot.Evidence与Operation回执使用原EvidenceId去重且限已保全身份；过期值为历史，历史查询不会刷新ObservedAt。绘图分页/采样、局部selection、busy及Attachment代次只属UI状态，不写Scene/Command hash或ledger。QueryAsync只允许本根已保全的完整OperationQuery（包括原Stop/Blackout），Identity不匹配抛ArgumentException无动作；未知Open在宿主QueryOpen区处理，不填成OperationQuery。

Attach不可覆盖已挂接context；每次成功Attach及开始Detach递增局部代次，溢出拒绝后续挂接而不回绕。Detach先封新意图、断普通投影/订阅、清复制缓冲，并把自己的在途Preview交原根预持Stop单飞；ct取消仅结束等待并抛OperationCanceledException，逻辑挂接仍解除，原根继续恢复，不Dispose/Close共享Controller。正常返回为其Stop回执（可以RunningUnknown/Blackout未确认），无自身Preview返回null；返回值不代表Session资源释放。后续Attach只能使用宿主已核合法的根，不能借控件重新挂接绕过同device原Owner。旧代次完成只更新原根恢复槽，不更新新context草稿；旧根不再具备Dispatcher时由其恢复区消费，不强投已shutdown Dispatcher。

Preview/Stop/Blackout等待取消和非预期桥接异常触发RecoveryRequired，事件参数保留原OperationQuery、可空Receipt与既有§9错误键（例如LIGHT_CANCELLED/LIGHT_TIMEOUT/LIGHT_CLEANUP_FAILED），不伪造失败回执。原Task未知用LIGHT_RESOURCE_DRAIN_TIMEOUT诊断并保留，不造新错误码或重试身份。事件在可用Dispatcher逐handler隔离，异常只记有界诊断，不吞Core异常、不影响原根已保全请求；原根是可靠恢复权威。SetCulture/CultureChanged保留未提交输入原文本及其原解析culture、选择/草稿/operation，已解析值按新culture显示，未解析文本仍须原culture显式提交或用户重输，不能静默改值；业务hash invariant。资源和语言入口规则沿§10.3，不在独立控件重复放切语按钮。DraftChanged只在原子提交有效草稿后发出，包含同次Compilation与ChangedStepIds，宿主拥有保存/批准；无效输入仅留编辑缓冲和错误，不发“已保存”事件。

### A.5 LC-S1 可选技术持久化桥唯一规格

本切片由2026-10-11本轮任务明确授权完善文档，覆盖既有照明ledger的可选后端；不是新设备/产品业务功能。Core A.1–A.3及UI A.4公开合同不变。职责为把ILightingLedger方法变成IM-066已注册事务/只读调用并保留技术Unknown；不实现另一数据库、连接池、通用SQL执行口、设备lease或permit。选择**每Scope/Store/controller/device一个有界完整镜像＋单行CAS**，避免在通用Core加入SQL；代价是每次更新复制有限镜像，不适用于无界海量历史。首版无自动清理/归档/分区删除，镜像满拒新Reserve；既有entry已预约整份容量，设备安全动作及bridge控制收尾不依赖再接纳一条新entry。不以性能或保存期理由删未知原身份，record耗尽的审计失败沿下文封闭处理。

#### A.5.1 公开装配、Options与所有权

声明规格位于Asun.Modules.LightingControl.Storage，SC/SR分别为Asun.Platform.StorageDatabase.Contracts/Runtime别名。现有Core与Storage类型重复引用不另造同义DTO；下列为新桥所需公开面，方法体在后续授权实现补入。

```csharp
public sealed record LightingLedgerStorageOptions(
    SC.CallContext WriteContext, SC.CallContext ReadContext,
    string ControllerId, string DeviceId, int MaxIdBytes, int MaxRecords, int MaxRecordBytes,
    int MaxImageBytes, int MaxRetainedCalls, long MaxRootBytes,
    int MaxCasAttempts, TimeSpan QueryDeadline, TimeSpan CleanupDeadline,
    int MaxDiagnostics, bool Simulation, CompileLimits Compile);
public sealed record LightingLedgerBindingSet(
    SC.StorageBindingDescriptor Replace, SC.StorageBindingDescriptor Read,
    SC.StorageBindingCatalog Catalog);
public sealed record LightingLedgerPartition(SC.StorageScope Scope,
    string StoreId, long StoreGeneration, string ControllerId, string DeviceId);
public sealed record LightingLedgerImage(LightingLedgerPartition Partition,
    long Revision, ImmutableArray<LightingLedgerEntry> Entries);
public sealed record LightingLedgerEntry(
    LedgerReservation? Reservation, PendingOpenReservation? PendingReservation,
    long Revision, SessionSnapshot Snapshot, CapabilitySnapshot? OpenCapability,
    ImmutableArray<LightingEvent> Events, LightingOperationReceipt? Terminal,
    ImmutableArray<LightingLedgerHistory> History);
public sealed record LightingLedgerHistory(long Revision, byte Action,
    ImmutableArray<byte> Input);
public sealed record LightingLedgerReplacePayload(SC.VersionRef Schema,
    LightingLedgerPartition Partition, long ExpectedRevision, string ExpectedHash,
    ImmutableArray<byte> NewImage) : SC.IOwnerStoragePayload;
public sealed record LightingLedgerReadPayload(SC.VersionRef Schema,
    LightingLedgerPartition Partition) : SC.IOwnerStoragePayload;
public sealed record LightingLedgerReadResult(LightingLedgerImage? Image);
public sealed record LightingLedgerReplaceResult(bool Applied,
    LightingLedgerImage? Image);
public sealed record LightingLedgerBridgeStatus(bool AdmissionClosed,
    bool CallsDrained, bool SessionsReleased, int RetainedCalls,
    ImmutableArray<LightingFault> Faults);
public static class LightingLedgerStorageRegistration
{
    public static LightingLedgerBindingSet Create(LightingLedgerStorageOptions options,
        SC.StorageInputLimits storageLimits);
    public static SC.IStorageOwnerReferenceResolver CreateReferenceResolver(
        SC.VersionRef version, ImmutableArray<LightingLedgerStorageOptions> partitions,
        Func<LightingLedgerPartition, LightingStorageLedger?> ledgerFor,
        int maxPartitions, TimeProvider timeProvider);
}
public sealed class LightingStorageLedger : ILightingLedger, IAsyncDisposable
{
    public LightingStorageLedger(SC.IStorageDatabase database,
        LightingLedgerStorageOptions options, LightingLedgerBindingSet bindings,
        SC.StorageInputLimits storageLimits, TimeProvider timeProvider);
    public bool Simulation { get; }
    public ValueTask OpenAsync(CancellationToken ct);
    public ValueTask<LightingLedgerImage> ReadImageAsync(CancellationToken waitCt);
    // ILightingLedger全部方法按A.3原签名实现，不增加设备命令入口。
    public ValueTask<LightingLedgerBridgeStatus> RecoverAsync(CancellationToken waitCt);
    public ValueTask<LightingLedgerBridgeStatus> CloseAsync(CancellationToken waitCt);
    public ValueTask DisposeAsync();
}
public static class LightingLedgerCodecV1
{
    public static ImmutableArray<byte> EncodeImage(LightingLedgerImage image,
        LightingLedgerStorageOptions limits);
    public static LightingLedgerImage DecodeImage(ImmutableArray<byte> bytes,
        LightingLedgerStorageOptions limits);
    public static ImmutableArray<byte> EncodeReplace(LightingLedgerReplacePayload payload,
        LightingLedgerStorageOptions limits);
    public static LightingLedgerReplacePayload DecodeReplace(ImmutableArray<byte> bytes,
        LightingLedgerStorageOptions limits);
    public static ImmutableArray<byte> EncodeRead(LightingLedgerReadPayload payload,
        LightingLedgerStorageOptions limits);
    public static LightingLedgerReadPayload DecodeRead(ImmutableArray<byte> bytes,
        LightingLedgerStorageOptions limits);
    public static ImmutableArray<byte> EncodeReadResult(LightingLedgerReadResult result,
        LightingLedgerStorageOptions limits);
    public static LightingLedgerReadResult DecodeReadResult(ImmutableArray<byte> bytes,
        LightingLedgerStorageOptions limits);
    public static ImmutableArray<byte> EncodeReplaceResult(LightingLedgerReplaceResult result,
        LightingLedgerStorageOptions limits);
    public static LightingLedgerReplaceResult DecodeReplaceResult(ImmutableArray<byte> bytes,
        LightingLedgerStorageOptions limits);
}
```

构造只校验/保存借用database、TimeProvider、Options和exact Binding，零IO/DDL/线程；null抛ArgumentNullException，非法域抛ArgumentException。两个Context的Scope、Store（含Profile）、Caller exact一致，DeviceId=Scope.DeviceId，ControllerId/DeviceId非空；Write/Read用途在Binding固定Production/Query，不能用Recovery角色执行领域UPDATE。所有计数/字节/期限>0，MaxCasAttempts在1..16；`checked(MaxRecords * MaxRecordBytes + 4096)<=MaxImageBytes<=MaxPayloadBytes`且MaxResultBytes>=MaxImageBytes+64；strict UTF-8身份及Schema的实际字节须另外符合上游InputLimits，4096是保守固定header预约上限，超过拒构造不截断。`MaxRootBytes>=checked(MaxRetainedCalls*(4L*MaxImageBytes+4096))`，每call复制前先预约此上界；预算不够零IO。MaxRecordBytes含该entry完整请求/所有事件/快照/终态，Reserve时为它永久预约一整份；实际记录填满时不丢事实，返回ResourceLimit并让Controller沿§8安全例外/Hold，未知记录不驱逐。MaxImageBytes不得宽于RuntimeLimits.MaxLedgerBytes；上游MaxBatchRows>=1、MaxCommands/MaxBatchBytes等须覆盖此单行替换。

原根在构造桥和StorageRuntimeFactory前预留槽，强持database、bridge、Options/目录版本、原Open/Close Task、所有调用记录/技术身份/原字节及异常；同partition一个桥写Owner，独立进程并发仍由DB CAS及设备lease隔离。桥独占自己Open取得的两个IStorageSession，不拥有database；不Stop/Dispose借用Runtime、不触碰Controller/Adapter/lease。Open依次OpenSessionAsync(SessionRequest(WriteContext,OwnerKey,Production))和(Query)；一旦返回非null产物即保存，即使同时Fault也须释放。第二失败嵌套finally释放第一；Open取消/超时保留原Task至资源真实归还，禁止新Open补位。IStorageDatabase.Create仍归宿主，可用一个借用Runtime服务多个已授权partition。

Options.Simulation必须与宿主选择的fake/真实后端资格一致：fake只能true，Usage.AllowSimulation=false不得注入它。true不能由存储方法证明设备模拟；设备及证据的Simulation仍由Core核。ILightingLedger成功写的Durable=true在Simulation下只表示fake契约确认，所有Host结论显式Simulation，不能升级物理断电耐久。真实bridge只在已采纳IM-066单权威配置/事务耐久Profile下使用false，配置不能只因DTO布尔值而取得资格。

#### A.5.2 完整账本codec、身份与版本

桥流固定ASCII四byte `LCL1`＋U8 tag；tag=1 Partition、2 Image、3 Entry、4 ReplaceInput、5 ReadInput、6 ReadResult、7 ReplaceResult。每个顶层只一个头，嵌套不重复头。原语沿§4.2：严格UTF-8 Str=U32BE字节数＋原文、I32BE/I64BE、数组U32BE count、bool/U8=0/1、nullable=0或1＋字段；bytes=U32BE length＋原bytes；decimal=Str(invariant G29)、TimeSpan=I64 ticks、所有enum=已冻结I32。hash在本桥流为**32原始byte**，输入string必须小写64hex；Scope按五ID声明序、Partition按公开声明序。VersionRef在Payload头后先写Id Str/Revision I32/hash32；SC.Sha256同hash32。所有bytes有界深复制，读取先检查长度/count/总预算再分配；不接受多余尾字节、非法UTF-8、未知tag/enum、default集合、非法null/非规范decimal或顺序。Encode/Decode均零IO，失败ArgumentException，ILedger转换为§9故障。

| tag | 头后全部字段（严格顺序） |
|---|---|
| 1 | Partition八字符串Scope五个/StoreId/ControllerId/DeviceId中StoreGeneration插在StoreId后I64；即Scope→StoreId→StoreGeneration→ControllerId→DeviceId |
| 2 | Partition正文、Image.Revision I64、Entries count＋Entry正文；Entries按SessionId ordinal→OperationId ordinal严格递增 |
| 3 | nullable Reservation、nullable PendingReservation、Revision I64、Snapshot、nullable OpenCapability、Events数组、nullable Terminal、History数组；前两者恰一非null |
| 4 | Schema VersionRef、Partition、ExpectedRevision I64、ExpectedHash32、NewImage bytes（含其tag2头） |
| 5 | Schema VersionRef、Partition |
| 6 | nullable Image（存在时bytes包含tag2头） |
| 7 | Applied bool、nullable Image（存在时bytes包含tag2头）；Applied=true必有Image，false必须null |

Entry内部A.2/A.3所有record递归按**公开声明字段顺序完整编码**，不省略重复身份：Binding五字段（CapabilityHash为hash32）、OperationContext全部七语义项及Budget两ticks、Reservation.Kind/Scope、CanonicalRequest原bytes、Expected/AcceptedStateVersion、Snapshot.Binding可空/SessionId/StateVersion/State/Output/SceneHash?/ArmedOperationId?/ActiveOperationId?/Evidence/Faults/ApplyDisposition、Evidence全部字段、Fault全部字段、LightingEvent全部字段、ResourceFacts全部字段、Terminal全部字段。Intensity仍特殊为Unit I32→Value Str（与§4.2一致）；ClockStamp为ClockId Str/Ticks I64/Frequency I64。Capability完整record包括自身Binding.CapabilityHash，随后Channels/Groups/TriggerModes/TriggerDelay/Simulation/Firmware/Source全部字段；它的hash校验另按A.1排除自身，不能用完整存储编码替代CapabilityHash。PendingReservation包括Identity五字段、Operation全字段、RequestHash32、CanonicalRequest bytes、AcceptedStateVersion。场景请求已经由Core规范编码，原CanonicalRequest仅保存其精确bytes且SHA等于RequestHash，不从当前DTO重建旧请求。完整Capability/OpenDisposal/Usage仍按原请求bytes/原快照保全，不用桥重写Core编码。

History每项为Revision I64→Action U8→Input bytes；Action固定1=LedgerReservation、2=PendingOpenReservation、3=LedgerProgress、4=PendingOpenProgress、5=LedgerFinalization、6=PendingOpenFinalization。Input是对应A.3 record按上述递归规则的**完整正文**，不带LCL1/tag，不只存hash/最新Snapshot；只能按Action选定类型解码且必须耗尽。History从revision0连续到Entry.Revision，count=checked(Revision+1)，首次Action仅1/2且其Input exact等于该entry Reservation/PendingReservation正文；后续Action只能同类3/5或4/6，Input.ExpectedRevision=History.Revision-1，Finalize只能最后一项。完整History按初始保守Snapshot及后续Append/Finalize顺序fold，得到的Snapshot/OpenCapability/Events/Terminal必须与Entry投影exact；Finalize的Snapshot取Terminal.Snapshot。Events按Sequence去重合并，原Append输入本身不重排以保留同值重放判断。History及重复投影全部计入MaxRecordBytes；count先以剩余bytes/每项最小13bytes及MaxRecordBytes作上界，再分配，不能用I64 revision直接分配集合。达到记录预算时拒绝追加并安全收尾，不裁历史。

旧ExpectedRevision的Append/Finalize定位History[ExpectedRevision+1]，Action及Input逐byte相同才为幂等；同一旧revision换Snapshot/Events/Capability/Terminal一律Conflict。幂等返回当前已验证entry/原终态，不回退head或投影；ExpectedRevision大于当前或存在终态后新增动作拒绝。这样在Append→Finalize后仍能检验旧Append，而不是拿最新快照猜旧输入。普通Reserve的保守Hold只作查询投影，正常Reserve回执不得令实时Controller进入Hold；S-B同时核此反例与终态后的旧Append重放/异内容冲突。

Encode/Decode的对称规则包括可空hash仍用存在位＋hash32、可空record用存在位＋正文、一般字符串不因名称含Reference就当hash；只有A.1–A.3声明的Hash字段采用hash32。Type名用于版本摘要时精确为`Asun.Modules.LightingControl.Storage.`加对应公开record名（image为LightingLedgerImage）；内部History没有独立tag或Schema。Partition顶层编码由公开EncodeRead/DecodeRead或Image.Partition按同一正文规则取得，注册包内部纯函数加tag1头，无额外可变状态。

Entries不跨Options.partition；同(session,key)及同(session,OperationId)双唯一，历史Binding不能给新请求换键。Reservation/Open身份和CanonicalRequest immutable；Revision>=0，每次Append/Finalize checked+1。Events保留原Sequence升序、同Sequence同完整事件幂等、不相同Conflict，允许其它operation的全局Sequence插在间隔中；Evidence按原Snapshot顺序保存（不重排其历史），EvidenceId同值重复不新增、异内容Conflict。OpenCapability首次非null后必须exact保留，不可变null；正式Binding形成后必须与它一致。Terminal若存在须身份/hash/Binding一致、Resources.Scope匹配且Drained/Released=true、Status为Completed/Failed/Cancelled、无矛盾唯一终态；Closed/释放与Blackout按Core原含义分开。快照版本回退/同version异内容拒绝；历史boot/clock不转当前epoch。新镜像需先完整Decode/校验旧镜像并逐项确认只增改本次合法entry，不能用调用者传整镜像删其它记录。

新Reserve的Entry.Revision=0；Pending初始Snapshot=(null,原session,0,Closed,Unknown,null,null,null,Empty,Empty,None)，普通初始Snapshot=(原Binding,原session,AcceptedStateVersion,Hold,Unknown,null,null,null,Empty,Empty,None)。这是ledger“尚无设备事实”的保守查询投影，不能回写Controller实时State；Reserve返回OperationStatus.Accepted、PhysicalEffect.MayHaveStarted、Blackout.Unknown、ResourceFacts(原Scope,false,false,null)。Append保存Controller提供的Snapshot/Events；未Finalize的Query Status=RunningUnknown、PhysicalEffect.MayHaveStarted、Blackout.Unknown，资源事实仅从该entry同Scope的Drained/ResourcesReleased事件确认，缺事件为false；实际发光事实仍在Snapshot原Evidence中。不凭ACK或RegisterOff构造Blackout.Matched。Finalize/历史Query精确回放原Terminal；Reserve同identity同bytes返回Existing=true的原记录，不再Apply。桥保持保守Unknown不会凭Query推断取消/安全释放。

fold的可空Capability规则：PendingOpenProgress.Capability=null只表示本次无新增能力，保留此前OpenCapability；非null首次写入后，后续非null必须完整exact相同。Finalize也保留已保存能力，不从当前设备重新发现。非终态回执的Faults取当前Snapshot.Faults；资源Scope取Reservation.Scope（Pending固定Operation），Drained只取存在该Scope的Drained事件、Released只取存在该Scope的ResourcesReleased事件，ReleasedAt取该Scope最后一个ResourcesReleased的原At，没有则null；单一事件不猜另一轴，也不以现在时间刷新。新Reserve Accepted回执Faults=Empty。Find/Query/旧Append重放的非终态统一用上述RunningUnknown投影，终态一律exact原Terminal，返回LedgerReceipt.Faults仅本次存储/输入故障，正常为Empty。

技术身份与照明ID分离：令M=EncodeReplace完整tag4流，`mutationDigest=SHA256(M)`；Storage.OperationId=`lcl-tx-`＋小写mutationDigest，IdempotencyKey同串，OwnerKey=`lighting-control`；Scope/StoreId/Generation来自原Context。每次partition CAS的新ExpectedRevision/NewImage改变技术ID，但同次Unknown只持原M/ID查询。先构造带合法占位hash的RegisteredTransactionRequest(Context,identity,Replace.Version,payload,References.Empty)，用**SR.StorageRequestHasher.Compute(request,ReplaceDescriptor,M,storageLimits)**取得真正SC.PayloadHash后替换，不把照明RequestHash或mutationDigest直接冒充技术PayloadHash。Storage运行版本/Binding/Schema/Options在原调用内冻结；原call同时保存照明身份、Entry ExpectedRevision、partition ExpectedRevision/Hash、M、技术request/hash及原Task。

Schema/codec注册Id统一前缀`lighting-ledger/1/`；Revision=1。输入/结果schema的后缀为`schema/{replace,read,read-result,replace-result,image}`，codec同名`codec/...`，bindings为`binding/{replace,read}`，catalog为`statements/{replace,read}`。Schema.Hash=SHA256(ASCII `LCL-SCHEMA-1`＋Str(Id)＋I32(1)＋Str(`LCL1`)＋U8对应tag＋Str(上表相应完整类型名))；codec.Hash同字段但域`LCL-CODEC-1`。公开具体codec为`LightingLedgerReplaceCodec(version,schema,options)`、`LightingLedgerReadCodec(...)`实现SC.IStoragePayloadCodec（PayloadType分别exact两个Payload，Schema匹配，Encode调用上述方法，GetReferences验证完整流后Empty）；`LightingLedgerResultCodec(version,schema,options,bool replace)`实现SC.IStorageResultCodec（完整解析tag6/7并校验，不执行IO）。Binding hash使用域`LCL-BINDING-1`＋descriptor声明序全部字段，排除自身Version，仅将StatementCatalog写Id/Revision、不写其hash，防止环；catalog仍完整携带已计算Binding ref，最后exact核StatementCatalog.Hash。SQL/codec改变显式新revision，旧Pending调用不跟随换版；首版仅读LCL1/写LCL1，不默默迁移旧准备字节。

Create返回Catalog.Version.Id=`lighting-ledger/1/catalog`、revision1，Hash=SHA256(ASCII `LCL-CATALOG-1`＋两Binding.Version按replace/read顺序完整VersionRef＋四codec.Version按replace/read/read-result/replace-result顺序完整VersionRef)。Catalog.Bindings仅这两项、Codecs仅两个输入codec、ResultCodecs仅两个结果codec，Schema image只作领域文档ref，不注册不存在的IOwnerStoragePayload。StatementCatalog.kind精确为`StatementCatalog`，每个commands仅一项；各ref用上述确定生成算法，不放占位hash。Binding摘要中字符串=Str、VersionRef=Str/I32/hash32、enum=I32的公开C#数值、int=I32、TimeSpan=I64 ticks、bool=U8，参数变化也改变Binding/Catalog版本摘要。codec的Encode/Validate同时取min(方法maxBytes,Options上限)，GetReferences即使maxReferences=0也可返回Empty，但必须验证完整载荷；不因无文件引用而跳过完整性。

输入NewImage.Partition必须exact等于Payload.Partition/Options.partition，Schema必须是本注册包对应exact ref；CanonicalRequest除hash校验外还解析原Core版本/域与不可变Binding或Pending身份、Kind、Operation/key/预算及AcceptedStateVersion关系，不接受将另一请求bytes配给当前record。所有事件必须绑定该entry原operation/hash/session及合法Scope；Snapshot与该session/当前正式Binding一致（未发现的Pending例外）。普通Core限额仍沿Options.Compile；Reserve/Append的嵌套数组同时受record/image预算约束，不因每个原请求单独合法而允许无界History。

构造补充预算硬门：`checked(MaxImageBytes+4096)<=storageLimits.MaxPayloadBytes`，为tag4/Schema/partition/ExpectedHash/length预留完整包络；包络实际长度超过4096则拒构造。QueryDeadline不得大于任一Context.ExecutionBudget。MaxRootBytes是原根持有的规范bytes预约，并非宣称CLR对象开销等于字节数；复制/索引/History解码的集合数量先以编码预算约束，真实性能另测峰值内存。每record永久额度避免其它Reserve挤占既有entry，**不承诺任意多安全事件都可落盘**；record实际已满时Controller照常独立关灯、保留原审计失败/Unknown，不截断快照/事件/终态以伪造Durable。

Options.MaxIdBytes固定在76..256且<=storageLimits.MaxIdBytes；所有桥/Scope/Store/Core嵌套身份与引用字符串先查strict UTF-8字节长<=此值，原CanonicalRequest作为完整bytes另受Compile/record预算而不按单个ID截断。如此tag1 Partition最多2093bytes、tenant最多256bytes，复合PK键保持在PG18标准8KiB页的BTREE可索引范围；已采用其它BLCKSZ的部署不是本PG18首版Profile。全部codec直接从Options取得此显式限额，不读取隐藏Runtime配置；Registration.Create还与上游InputLimits核对。固定软件fixture与双Host的Options.MaxIdBytes均256；长文本诊断不入此存储桥的自由日志，超出规范字段预算返回ResourceLimit，保留原根有界摘要而不删原身份。

#### A.5.3 Owner Schema、迁移、固定SQL与marshal

只建立本模块领域schema `lighting_ledger`，不改`im066`表，不公开Npgsql/Reader。首版表`lighting_ledger.head`全部列为：tenant text COLLATE "C" NOT NULL；p bytea NOT NULL；r bigint NOT NULL CHECK(r>=0)；b bytea NOT NULL；h bytea NOT NULL CHECK(octet_length(h)=32)；主键(tenant,p)。p是含头的tag1 Partition完整bytes，r/b/h分别Image.Revision/tag2完整bytes/SHA256(b)。tenant必须等于p.Scope.TenantId，p的Scope/Store与CallContext exact、Device匹配，由codec和Owner包校验；所有text ID受InputLimits.MaxIdBytes，不trim。表CHECK octet_length(p)>0、octet_length(b)>0；最大实际尺寸在有界codec和可信注册包双核。无触发器/sequence/identity默认列/动态表名/时间默认值/自动删除；不可用DB时间代替原ClockStamp。

迁移包`lighting-ledger/1/migration`固定三个步骤：建schema/table与PK/check→ENABLE及FORCE ROW LEVEL SECURITY→建立SELECT/UPDATE/seed策略；tenant条件均`tenant=current_setting('app.tenant_id',true)`。runtime角色只有该表SELECT/UPDATE（Query仅SELECT）、无INSERT/DELETE/DDL/owner/BYPASSRLS。隔离Migration角色在批准的partition清单各插一行r=0、空Entries的tag2镜像/h，冲突时逐字段校验exact空镜像或保留已存在合法镜像，不重置已有r。初始化参数exact为tenant Text、p Bytea、b Bytea、h Bytea，r字面0。bridge启动核已采纳版本与预置head，不建表/建head；实际Schema/PK/RLS/角色核验归下文部署迁移及PG验收。缺head=LIGHT_AUDIT_WRITE_FAILED/Recovery.Query，绝不NotFound=空库。新partition须显式批准同迁移初始化；镜像未来清理/压缩/字段变更是新Owner迁移版本，当前无自动retention删除。下游软件回退只允许旧包支持原codec/schema；否则隔离恢复，不在生产重写旧bytes/hash/terminal。批准迁移身份/技术plan及IM-066技术Schema由上游既有Migrate流程负责，本包提供上述三个DDL step及初始化与前后验证/回退：建表前无事实可撤注册，新事实已写则保留只读，不DROP以假回退。

三步DDL原文如下（逐块LF、末尾LF，包revision=1；既有对象必须按迁移记录及以下结构核验，不靠IF NOT EXISTS忽略差异）：

```sql
CREATE SCHEMA lighting_ledger;
CREATE TABLE lighting_ledger.head (
    tenant text COLLATE "C" NOT NULL,
    p bytea NOT NULL,
    r bigint NOT NULL,
    b bytea NOT NULL,
    h bytea NOT NULL,
    CONSTRAINT lighting_head_pk PRIMARY KEY (tenant,p),
    CONSTRAINT lighting_head_r CHECK (r>=0),
    CONSTRAINT lighting_head_p CHECK (octet_length(p)>0),
    CONSTRAINT lighting_head_b CHECK (octet_length(b)>0),
    CONSTRAINT lighting_head_h CHECK (octet_length(h)=32)
);
```

```sql
ALTER TABLE lighting_ledger.head ENABLE ROW LEVEL SECURITY;
ALTER TABLE lighting_ledger.head FORCE ROW LEVEL SECURITY;
```

```sql
CREATE POLICY lighting_head_read ON lighting_ledger.head
FOR SELECT USING (tenant=current_setting('app.tenant_id',true));
CREATE POLICY lighting_head_update ON lighting_ledger.head
FOR UPDATE USING (tenant=current_setting('app.tenant_id',true))
WITH CHECK (tenant=current_setting('app.tenant_id',true));
CREATE POLICY lighting_head_seed ON lighting_ledger.head
FOR INSERT WITH CHECK (tenant=current_setting('app.tenant_id',true));
```

seed策略仅配合Migration角色INSERT ACL；普通Production/Query均没有INSERT权，策略不授ACL。角色名来自可信部署注册，不是请求或本包可插值变量；部署以独立Owner建表、先REVOKE PUBLIC该schema/table全部权限，再授上述最小USAGE/SELECT/UPDATE及Migration的初始化权限，并核角色继承无升权。初始化固定SQL：

```sql
INSERT INTO lighting_ledger.head(tenant,p,r,b,h)
VALUES ($1,$2,0,$3,$4)
ON CONFLICT (tenant,p) DO NOTHING;
```

Migration在同scope事务先设置app.tenant_id，再初始化，之后使用固定Read SQL验证已存在镜像；0行不重置它。DDL、seed及ACL/RLS/PK实际核验是部署迁移/PG验收门，不由bridge Open通过未定义私有连接执行；Open只核已采纳的精确迁移/绑定版本及Read结果，版本/部署验收未采纳拒绝真实后端装配。DDL包hash=SHA256(三个DDL块UTF8原文依次连接＋seed SQL原文)，真实角色ACL属于批准部署Profile而非改写此hash；运行中权限失效仍由IM-066/RLS及实际SQL失败封闭处理。无损旧库重试仅在IM-066迁移记录已确认该step提交且结构一致时跳过，缺记录/结构不符隔离，不自动DROP/重建。

只有两条固定StatementCatalog；所有占位都按下表类型，不插值SQL。

```sql
UPDATE lighting_ledger.head
SET r=$5, b=$6, h=$7
WHERE tenant=$1 AND p=$2 AND r=$3 AND h=$4
RETURNING r,b,h;
```

Replace参数序：1 tenant Text、2 Partition bytes Bytea、3 ExpectedRevision Int64、4 ExpectedHash byte[32] Bytea、5 NewImage.Revision Int64、6 NewImage bytes Bytea、7 SHA256(NewImage) byte[32] Bytea。NewImage.Revision=checked(ExpectedRevision+1)，完整校验后才交SQL。commandIndex=0、kind=Mutation、resultColumnTypes=[Int64,Bytea,Bytea]、maxRows=1；affectedRows只允许0或1。0行表示CAS未命中（包括缺行），结果EncodeReplaceResult(false,null)，随后必须Read区分冲突/缺失，**不能作为照明写成功**。1行核r/镜像Revision及hash自洽，结果EncodeReplaceResult(true,完整NewImage)。marshal/ResultCodec在IM-066 commit前核三列及镜像形状/预算，超限或不自洽回滚；请求exact赋值由固定UPDATE保证，bridge取得已提交Result后再与原NewImage逐byte核对，不以codec保存每请求可变状态关联返回值。任何已提交但结果不匹配保持Integrity/Unknown，不抹已提交真值、不发灯命令。bridge返回Durable=true还要技术Committed确认。

```sql
SELECT r,b,h FROM lighting_ledger.head WHERE tenant=$1 AND p=$2;
```

Read参数1 tenant Text、2 Partition bytes Bytea；commandIndex0、kind=Read、AffectedRows=0、resultColumnTypes同上、maxRows=1；0行EncodeReadResult(null)，1行核b的Partition/r、h/hash及完整codec后EncodeReadResult(image)，>1行或类型/长度错完整失败，不交部分镜像。Read成功但无head只表示缺初始化或损坏，不是某照明op不存在；有合法head而entry不存在才按A.3返回可靠未找到，Controller仍不得因此重发。

具体marshal `Asun.Modules.LightingControl.Storage.PostgreSql.LightingLedgerPostgreSqlCodec(binding,options,storageLimits)`实现IM-066已冻结IPostgreSqlBindingCodec；Version=binding.InputCodec，InputSchema/ResultSchema exact，GetParameters先完整Decode tag4/5核Context/partition与预算再返回上述BCL object数组；EncodeResult只接受单个PostgreSqlCommandResult(commandIndex=0)，按上述Rows/AffectedRows核对并编码tag6/7，零IO/不接连接/SQL delegate。数据深复制在预算内，null只有result的Image缺失，不给PG参数DBNull；long不窄化，bytea不装图像或SDK对象。Hash错=LIGHT_AUDIT_WRITE_FAILED/VendorCode=storage.integrity_failed、版本错=LIGHT_CONTRACT_VERSION_UNSUPPORTED；RLS/权限错误=LIGHT_PERMISSION_DENIED；CAS/照明身份冲突=LIGHT_IDEMPOTENCY_CONFLICT或LIGHT_STATE_CONFLICT（ExpectedRevision冲突），调用方据原请求查询，不解析provider文字。

descriptor公共字段：OwnerKey=`lighting-control`，Replace.Kind=Transaction/Purpose=Production/Isolation=ReadCommitted/MinAffectedRows=0/MaxAffectedRows=1；Read.Kind=Read/Purpose=Query/Isolation=ReadCommitted/Min=Max=0；MaxCommands=1、MaxRetries=0、RetryDelay=1ms、ServerLockTimeout=options.QueryDeadline、ServerStatementTimeout=WriteContext.ExecutionBudget（Read取ReadContext.ExecutionBudget）、AllowEmptyBatch=false。PermissionKey分别`lighting.ledger.replace`/`lighting.ledger.read`；这些权限只授账本行，不授设备动作。MAX bytes/行必须<=上游Profile。StatementCatalog严格JSON无BOM，字段序`kind,id,revision,ownerKey,binding,codec,commands`，ref为`id,revision,hash`；commands字段序`kind,sql,parameterTypes,resultColumnTypes,maxRows,maxBytes`，SQL采用上述正文LF换行且末尾LF，无缩进JSON并末尾一个LF，JSON仅标准字符串转义；maxBytes=storageLimits.MaxResultBytes。Hash=最终原UTF8 bytes SHA256，SQL变化修订Binding及Catalog，不依环境替换。Catalog trusted source按exact ref交IM-066，Runtime不从用户请求接受SQL。批次/文件References始终Empty；完整OwnerReferenceResolver仅列登记partition的账本影像元数据且ObjectRef集合Empty，因为本桥无外部文件对象；Complete必须在所有登记partition实际读验后才true，不能因没有文件而跳过损坏账本。

ReferenceResolver由上列CreateReferenceResolver构造，返回内部实现SC.IStorageOwnerReferenceResolver（不另设产品服务）；partitions为可信完整有限清单、长度1..maxPartitions、同Owner/Store/Scope域、partition唯一，构造零IO。Version.Id=`lighting-ledger/1/references`/revision1，Hash=SHA256(ASCII `LCL-REFERENCES-1`＋按完整tag1 bytes字典序排序的partition bytes数组)；每数组项为length＋完整tag1 bytes。ledgerFor是仅启动注入的受信根查找器，不能来自请求，查找结果必须ReferenceEquals该根预登记桥且Options/partition exact；Runtime构造前可暂返回null，正式使用时缺根=Unavailable，不创建/替换Runtime。版本/ref与注册清单进入宿主StorageOwnerRegistration/ReferenceCatalog，不在Create返回的BindingCatalog中冒充SQL codec。

**IM-066 0.3.1-prep接线补充。** Create/CreateReferenceResolver只复制有界注册值并保存注入对象，构造和声明getter均不得调用ledgerFor、OpenAsync或ReadImageAsync；不是“先调用后容忍null”。宿主在RuntimeFactory前冻结同一Binding/codec/marshal/Owner/Scope/Store/partition目录，声明从构造至所有借用退出均不可变；字段值逐项比较，不用ImmutableArray引用相等代替内容一致。Runtime/A1只消费这一冻结快照，不重新Resolve或读取全局目录。原Factory成功后构造bridge、一次登记其原根映射并Open成功，之后才开放消费者/维护根读取；登记后不得热替换桥。尚未登记/未Open/失败的根查询返回Unavailable，不作空完整根。启动只核resolver声明，不枚举Owner根；完整备份/GC仍须宿主登记该范围全部Owner，普通只读Host的窄注册不能宣称完整闭包。

Replace即使References.Empty，仍由IM-066 §6.7.3在**同一PG提交事务**锁reference_authority、分配并更新E，再执行本模块CAS并写技术回执；本桥不自行取得或更新E，不从Token.ReferenceEpoch/镜像Revision推导新提交epoch。本模块首版无文件引用/root_history或按E定界的领域行，现有固定UPDATE不需新增epoch列、GUC读取或第二事务补写；0/1 Min/MaxAffectedRows只统计目录中的这条UPDATE，排除上游隐含epoch/route/receipt SQL。CAS false的已知提交也不表明上游技术epoch未变，Applied仅描述照明镜像是否替换；ordinary Read/QueryOperation/已提交重放不分配E。resolver.ReferenceEpoch继续使用原保护屏障确认的request.Barrier.ReferenceEpoch，不是Fence；该值只标保护快照，不声称最新head具备历史区间。GC本Owner零ObjectRef仍须完整结构核验，完整备份的head读取必须在上游BackupCut屏障内且该范围新写已封闭，不用最新head冒充指定旧epoch的历史镜像。Query用Query/READ ONLY，原技术operation回查用Runtime Recovery保留池，均零领域写入。

OpenAsync核request.Owner/Scopes/Stores/ReferenceResolver/Catalog exact、Barrier为调用IM-066组合器已取得并在读取全过程保持的Backup/BackupCut/Gc保护token、MaxEntries/MaxBytes为正；不把客户端任意token当授权。沿清单依次调用各原桥ReadImageAsync，并在request.Context预算内完整decode/fold/hash；任何缺head、损坏、超时或未知返回Snapshot=null/对应StorageFault，原Task由原根保留，零Complete。ReadImageAsync复用本桥Query actor/槽/期限/校验，无新SQL或设备动作，失败不返回部分镜像。所有通过后只保留有限partition/hash摘要（不持整镜像），形成固定SnapshotId=SHA256(ASCII `LCL-REFERENCE-SNAPSHOT-1`＋resolver.Version完整ref＋每partition bytes及Image.Revision I64/hash32)，ReferenceEpoch=request.Barrier.ReferenceEpoch；返回Snapshot的ReadAsync只接受nextSequence=0，输出Entries.Empty/NextSequence=null/Complete=true/Fault=null，SnapshotId/ReferenceEpoch不变。该Owner无ObjectRef故没有伪造的OwnerReferenceEntry；摘要仍计request.MaxBytes，超限拒绝。Dispose幂等，释放本快照借用，不释放调用方Barrier、bridge或Runtime。请求取消只结束等待，原根观察未退出读者；token失效按上游组合器封闭，不交完整闭包。

Owner.ReadValidation.Id=`lighting-ledger/1/read-validation`/revision1，Hash=SHA256(ASCII `LCL-VALIDATION-1`＋resolver.Version完整ref＋Read.Version完整ref)。可信Maintenance/隔离target目录绑定同一有限partition清单、上文固定Read SQL及tag6完整Decode/fold校验；必须在目标库本scope下逐partition检查head存在/完整/版本/hash并覆盖全部登记项，ObjectRef为Empty。验证只用目标只读连接，不调用源bridge，不建表/修数据/发设备命令；任一缺失/超限/失败不Complete。实际SQL/角色/RLS/DDL验证仍按S-F与PG门，不把resolver的空引用投影当数据库结构已验。

resolver同时只允许一个Open或未Dispose的snapshot，另一个返回ResourceBusy；其原Task/保护token由调用它的IM-066 Maintenance根保全。内部读取用与ReadImageAsync相同的Query actor，但必须观察到原read IO真实退出才释放resolver借用，不能只等一个可取消的外层waiter；取消/期限到达封后续读取，当前读未退出保持原Open Task/Barrier借用且不交Snapshot。Open/Read异常与Dispose路径均归还本resolver槽，前提仍是原IO退出；不负责释放调用方token。Snapshot元数据按Str(SnapshotId)＋I64(ReferenceEpoch)＋partition数组(count＋各bytes/revision/hash32)精确计MaxBytes，超限在复制前失败；ReadAsync非法nextSequence或已Dispose返回Empty/Complete=false/InvalidInput，不创建新snapshot。ReadValidation对target也遵守相同完整读取/真实排空和有界错误规则。

resolver及snapshot严格实现上游SC.IStorageOwnerReferenceResolver/SC.IStorageOwnerReferenceSnapshot原签名，Open/Read返回SC.OwnerReferenceSnapshotResult/SC.OwnerReferencePage，不另造通用类型；成功Open Fault=null，失败Snapshot=null且Fault非null。Version/请求校验失败为UnsupportedVersion或InvalidInput，缺桥/读失败为Unavailable，损坏为IntegrityFailed，额度满为CapacityExceeded；保留具体既有fault，不解析异常文字。ReadImageAsync返回完整只读领域Image；等待取消抛OperationCanceledException，非成功存储读转既有LIGHT_AUDIT_WRITE_FAILED并由resolver映射为相应StorageFault，不将丢失、损坏或未知投影为Empty/Complete。

关闭顺序补充：宿主先停止lighting消费者及新维护接纳，在原根封resolver新Open入口，并观察原Open/Read Task、已交付snapshot及其保护借用真实排空；此时仍保留bridge Query Session供已接纳resolver完成读取。之后才执行bridge.Close/两个Session Release/Dispose，再Stop/Dispose借用Runtime及backend，最后结束codec/resolver/marshal/注册对象的宿主生命周期。resolver无新增公共Close API，接纳门和活动借用计数由本Owner内部实现及其宿主强根管理；关闭后Open返回ResourceBusy/非Complete，已交snapshot由原持有者Dispose。任何期限到达但原Task/snapshot仍未归还则保留同组根/对象，不继续销毁依赖、不替换ledgerFor映射；resolver不反向Dispose Runtime或bridge。S-E受影响断言增加：构造时ledgerFor/Open/Read调用数0、登记后替换根拒绝、resolver在途关闭不提前Release Query Session、snapshot未Dispose不Stop Runtime；这些为既有fixture验收要求，本轮未运行。

#### A.5.4 ledger操作、CAS/Unknown及原根两轴恢复

所有ILedger调用先按原A.3校验身份/bytes/hash/预算，按partition在本桥单actor序列化；查询可独立Query session。先预约MaxRetainedCalls/MaxRootBytes并将原call输入放原根，再Read当前合法Image。Reserve扫描双唯一索引（可从已解有界Entries建只读字典，字典不另写真值），同身份same bytes返回Existing=true，任何key/op/Binding冲突返回Conflict，无DB mutation；新记录必须整份容量已预约。Append/Finalize核原entry存在、ExpectedRevision及immutable身份；同Expected+同内容已写时返回既有记录，不再次递增；异内容或别的终态Conflict。合法修改生成下一Image.Revision且仅改原entry、保全其它entries。末位Revision/Sequence溢出拒绝/锁存ArithmeticOverflow，不回绕。

每次读使用`ReadAsync(new SC.RegisteredReadRequest(ReadContext,Read.Version,new LightingLedgerReadPayload(Read.InputSchema,partition)),workerCt)`；原ValueTask仅一次AsTask并入原槽。成功必须Fault=null、Schema exact Read.ResultSchema、References为非default Empty、Bytes通过完整DecodeReadResult及Options.partition核验；缺head/损坏/资源仍在途均不回可靠NotFound。Read没有durable技术OperationIdentity或可返回TaskHandle，不能虚构它们；取消/未知仅观察原本地Read Task，真实退出前不复用该Query Session。需要读镜像的mutation与普通Query按同Query Session串行借用，零并发重入。装配/角色不足等接纳前明确Rejected是本次无作用失败，不能一律升级成可重试Unknown；进入后端后未获明确结论才按下文保全。

首次Session交付后立即生成固定Release控制身份：digest=SHA256(ASCII `LCL-RELEASE-1`＋Partition正文＋ResourceHandle.InstanceEpoch Str＋ResourceId Str)，OperationId/key均`lcl-release-`＋digest小写hex，PayloadHash=该digest，Scope/Store/Owner照原Context；这是IM-066实例控制身份，不走durable transaction hasher/route。两Session各自一个原ResourceReleaseRequest，重复Close只加入原Task；不在重试时重新生成。无关联照明operation而bridge清理失败（如Open后尚未Reserve）的LightingCleanupException采用Binding=null及三个空身份字符串，Fault=LIGHT_CLEANUP_FAILED；有原照明operation则保留其完整身份，不能把Release技术ID当照明ID。

每一次新Image replacement均先编码/保存原技术request，再ExecuteTransactionAsync(WriteContext,原技术Identity,Replace.Version,payload,Empty)。一次ValueTask仅一次AsTask，Task/TaskHandle、原返回/故障、预留sessions由原槽强持；调用者ct只结束外层等待，worker execution budget固定来自原Context，不因Query/重复点击重启。成功条件为：IM-066技术Record.Commit.State=Committed、ResultSchema exact、References.Empty、DecodeReplaceResult.Applied=true且返回Image exact原NewImage；同时原技术任务ResourcesReleased/Completed已确认后才向正常调用返回已排空成功。技术提交事实已知而资源未归还仍保留原task，不Dispose session，不以ledger真值替代资源证据。技术Committed+Applied=false是**已知CAS无作用**，正常有限Read最新Image重新核该照明动作；同照明身份已存在返回原事实，另一已知revision竞争可在原deadline内最多MaxCasAttempts次重算，生成新M/技术身份。MaxCasAttempts耗尽返回StateConflict及原最新回执，不能无穷循环。

CAS false允许重算还须原本地Task真正完成及技术State=Completed/资源已释放，不能只看Committed就在同Write Session发下一attempt。资源轴未知则仅Recover原ID；Recover本身永不Execute，确认旧Applied=false且排空后结束该原call为StateConflict（由调用方按原照明事实恢复），不在恢复方法暗中续开attempt。Recover只对并发调用单飞；前一观察已退出后可再次作新的只读观察，固定原技术身份不变。MaxCasAttempts计实际发出的replacement次数，不计Read次数；原call deadline从首次接纳开始，不因CAS竞争/再次观察刷新。

Register/Execute/commit/返回丢失、Cancellation/Timeout、结果hash错或技术Unknown时，不进入CAS重算重试分支，原call保持Unknown，禁该partition新mutation（但允许只读/原任务观察、Controller原安全关闭）。Recover只沿原SC.OperationIdentity调用IStorageDatabase.QueryOperationAsync，及有TaskHandle时GetTaskStatusAsync；绝不Execute同/新request探测。技术Committed回执可确定旧Applied true/false，须再等原本地Task及资源退出；如果需刷新照明投影Read原head，同镜像必须含该entry原事实或更高合法revision，不能以之后head变化抹原提交。技术明确RolledBack且原writer/IO排空后，该照明调用返回AuditWriteFailed/无本次写入，Controller负责决定如何收尾；桥不自动发起新attempt。NotFound/InProgress/ResultExpired/权限不可查均保持Unknown，技术route是否为空不证明照明动作未发生。重启只创建只读查询根查原Identity/账本（不接管设备Owner、不重演Reservation），有可信旧task移交/原device Owner安全释放前不得恢复新emit。

可靠Read已存在head且找不到entry时，LedgerReceipt(Durable=true,Conflict=false,Existing=false,Revision=0,Operation=null,OpenCapability=null,Faults=Empty)沿A.3；可用记录时Existing=true/Revision=原entry revision、Operation按A.5.2保守/终态规则、原OpenCapability。Reserve新成功Existing=false但Operation为Accepted、Revision0；普通Append/Finalize或重放Existing=true。Fault转换：存储Unavailable/CommitUnknown/ResultExpired/原task未知→LIGHT_AUDIT_WRITE_FAILED、Durable=false/Conflict=false、保留最近已验证Operation（没有则null）、Recovery.Query；身份/载荷或CAS冲突→Conflict=true并保持原record；CapacityExceeded→LIGHT_RESOURCE_LIMIT；IntegrityFailed→LIGHT_AUDIT_WRITE_FAILED+VendorCode原key、绝不返回可靠NotFound。调用者等待取消抛OperationCanceledException，原worker仍保全。bridge不覆盖Core安全lane，ledger坏时Controller仍尝试原关闭且Hold，不依赖bridge完成新安全mutation才关灯。

Close先封新mutation/普通查询，原call/Recover/只读原身份恢复仍允许。独立CleanupDeadline只限制本次观察，不取消既发技术commit/native返回；每次从原remaining预算核，重复Close不能把底层原cleanup无限延期。嵌套finally：观察原worker/task→各自ReleaseAsync原session.Handle（在首次Open后立即预持固定控制Identity）→有限观察两session Released→Dispose两个原Session各一次；Release失败也尝试另一Session，原Task未退出的Session不提前Dispose。primary业务异常与所有cleanup异常并列保存，不覆盖。DisposeAsync加入同一Close/cleanup任务，预算到期抛LightingCleanupException，Binding/Session/op/hash使用所关联原照明身份（Open前依A.3空身份例外），RecoveryRequired/诊断仍归原槽。CallsDrained只在所有原worker/回调/awaiter实际退出、SessionsReleased只在两Session原Release/Dispose均完成；这两轴任一未知不得返槽。已提交事实/失败事实与这两轴分别记录，不以Status bool把Unknown改成功。宿主等所有借用桥/Session原Task退出后才自行Stop/Dispose StorageRuntime；lighting Controller Dispose永不Dispose桥或StorageRuntime。

Open/Close/Recover本身也先保留原Task在同根，不能在Close超时方法离栈后让局部await using清理借用Runtime。MaxRetainedCalls满拒普通调用但Close/Recover各一个预留控制单飞不占普通槽；未知call不驱逐。对已知终态且技术原Task/观察者/Session工作实际排空的普通call才释放其根内临时记录与字节额度；账本entry与原技术identity/hash墓碑仍保留在IM-066及Image，释放临时根额度不允许复用照明key。每桥原session一次只一工作；Query超时底层尚未退出时保留原Query Task，拒在同Query Session叠加读取；Recover可通过Runtime原Operation查询保留池观察，不能借新Query session掩盖未退出读者。

进程崩溃后的边界明确：Image保留照明原输入/历史/终态，可直接只读恢复这些事实；本桥首版不另建跨进程原根journal，不声称从最新head反推某次丢失技术request/hash/TaskHandle。宿主若已保全完整原SC.OperationIdentity，可用Runtime公开只读Query回查；未保全的原技术身份不可伪造，禁止自动重建/重发或宣称原任务已排空。重启查询根只能Read/Query，不能以新epoch中的Task表为空取得旧设备Owner。跨进程写恢复须消费产品确认旧进程/设备发送路径隔离及旧Owner安全释放，并显式建立新的组合根；这是生产fence/部署恢复资格门，绝不默认为本轮桥的自动接管能力。

**设备占用权威消费合同保持独立。** 宿主注入A.3 ILightingLeasePort及可信AuthorityReference/物理设备键映射，deadline全部为正有限且核TimeProvider同epoch/频率；Acquire绑定原ControllerId/DeviceId/OwnerId=SessionId/OperationId，不接受请求自选另一authority。每次返回精确原租约/当前Fence、CheckedAt/ValidFor，remaining寿命不足按§8取消点亮并安全收尾。撤权/到期由Controller轮询自主Stop/Hold并使旧Armed无效；原LeaseId/Fence即使权限撤回仍供安全收尾与释放，不能借失效权限丢原Owner。Renew回显不同Fence/authority或未来Clock即失败；Release只能处理原Owner、原native/任务已排空后的归还，不释放另一Host。未知/重启/旧writer未隔离不自动转交，设备不能强制拒旧命令时禁止声称跨进程fence资格；**存储Operation token不输入此设备租约，也不由本桥签发**。这些输入/失效/恢复规则全部可在software authority fixture复现；真实设备gateway/epoch稳定性由部署Owner提供，不留未定义设备动作给开发者猜测。

#### A.5.5 双无UI Host、具体样例与性能计划

唯一Storage.Tests采用真实IM-066 StorageRuntimeFactory/StorageRequestHasher及本桥，只有ConfigurationResolver、BackendFactory五端口/Clock/Barrier为IM-066 C1式可控fake；不fake整个IStorageDatabase，不引产品Shell/WPF/设备SDK。两Host为`--host aoi`及`--host stencil`，各自原root/Runtime/双Session/Bridge/Controller/lease/permit/Task表。各根先预留启动/cleanup槽与总字节→构造Registration/codec与trusted目录→RuntimeFactory.Create→bridge.Open→注入原LightingController→§11.1完整Open/单步Apply/Arm/Execute/Observe/Stop/Close→Controller Dispose→bridge.Close/Dispose→Runtime Stop/Dispose。另一只读重启consumer可仅Runtime Query/bridge Query原照明ID，不Open灯；取回原OpenCapability，不再Acquire/发光。两个设备正常场景controller/device/partition不同；同设备双写负例共享原authority拒第二设备Owner。DB并发专门两bridge共享**同一fake DB原CAS持久状态**、不同Runtime/session且不连接真设备，验证重放/冲突；不能把字典各自一份伪装并发存储。

固定软件Options：Scope=(t,s,l,n,d)，Store=(x,1,已登记fixture Profile)，ControllerId=c、DeviceId=d；MaxRecords=8、MaxRecordBytes=65536、MaxImageBytes=528384（8×65536+4096）、MaxRetainedCalls=4、MaxRootBytes=8470528（4×(4×528384+4096)）、MaxCasAttempts=3、QueryDeadline=200ms、CleanupDeadline=2s、MaxDiagnostics=64、Simulation=true、Compile沿§11.1；Write/Read的ExecutionBudget=2s、WaitBudget=200ms，Caller exact=`fixture-owner`/`fixture-authority`，fake原Clock频率10000000。StorageInputLimits=(MaxIdBytes=256,MaxPayloadBytes=1048576,MaxResultBytes=1048576,MaxReferences=1,MaxBatchRows=1,MaxBatchBytes=1048576,MaxCatalogEntries=16,MaxCatalogBytes=1048576)；StorageRuntime其它限额按上游C1 fixture，必须显式提供>=本桥预约且不小于2个Session/控制操作所需额度，不能用无界默认。运行期限沿§12.1 10s/120s/180s，SQL超时数值只为fixture不是现场节拍。

本桥fixture补齐上游限额的精确值（采用其公开类型，不假设上游存在未列明默认）：StorageRuntimeLimits按声明序为(16,16777216,16,8,64,32,256,16777216,2s,3s,2s,10min,1day)；StorageQuota为(本Scope,lighting-control,16,16777216,4)，StorageFactoryOptions.ResolutionBudget=2s。fake Runtime的Relational四用途各MinPoolSize0/MaxPoolSize4、TotalConnectionBudget16；OpenTimeoutSeconds=2、CommandTimeoutSeconds=2、ConnectionIdleLifetimeSeconds=60、ConnectionPruningIntervalSeconds=10、CancellationTimeoutMilliseconds=2000。单Host只独占两个Session及fixture控制槽；每次test隔离Runtime，不能跑满256墓碑后删除仍在引用的历史。S-G在专门新fixture收紧目标额度并以N/N+1断言，不修改正常Host配置。

完整双Host为保守容纳§11.1全链的Snapshot/History，采用独立且明确的较大软件Profile：MaxRecordBytes=1048576、MaxImageBytes=8392704、MaxRootBytes=134299648、StorageInputLimits的MaxPayloadBytes/MaxResultBytes/MaxBatchBytes均16777216，Runtime MaxQueuedBytes/MaxTombstoneBytes及Quota.MaxQueuedBytes均268435456；Controller.RuntimeLimits只将MaxLedgerBytes设为16777216，其余仍沿§11.1。不改变原Core C1/C2 fixture及既有向量。其余LC-S1 Options同上；AOI/钢网分别以自身§11.1 controller/device重算partition/binding/hash，不能将c/d的Golden字面身份覆盖真实样例。所有额度仍有界，是否足够及实际峰值由首次实现的必需Host验证，超限必须非零并修订受影响Profile后重测，不能静默扩容或跳过历史。

| Case | 精确必需断言 |
|---|---|
| S-A codec/Golden/版本 | A.5.6完整流/长度/hash；所有字段单点变更摘要变化；Scope/Store/Partition/版本/header/请求hash/尾byte/非法UTF8/enum/default/预算N+1拒绝，零数据库IO；原C1-F不变；旧tag/version不静默迁移 |
| S-B Reserve/Append/Finalize正常 | 预置head r0/空Entries；Reserve得到head r1、entry revision0/Accepted；Append(Expected0)得到r2/entry1；Finalize(Expected1)得到r3/entry2/原terminal。三技术OperationId不同，Query旧照明ID返回同terminal/原bytes/hash/OpenCapability。重复三次原Reserve/Append/Finalize无新替换，head仍3；另一key同op及同key改hash冲突，head不变。终态资源/blackout按原值不升级 |
| S-C 双写CAS | 同partition两个桥从r0计算各自不同op；一个r1成功，另一技术Committed+Applied=false后Read/re算至r2，两个entry都存在。相同op同bytes竞争只1条entry；相同op异bytes只一成功，另一Conflict，原terminal不可覆盖；第三次已知CAS竞争到MaxCasAttempts返回StateConflict，不无限重试 |
| S-D Unknown两轴 | 在fake实际commit后、返回前阻塞，wait取消后原照明ledger写未知、原技术Task/Identity保留、设备新emit次数0；QueryOperation可看到Committed，但BeforeResourceRelease未解除时不CallsDrained/不返槽。解除原barrier后Recover同技术ID/原镜像，无第二Execute，方可排空。另注入CAS false/明确回滚/NotFound/ResultExpired/不可查，分别核已知无作用重算/失败/Unknown禁止重发 |
| S-E 原根异常/关闭 | Open第二Session失败仍释放第一；consumer异常同时Release/Dispose异常均保留；Close等候到期不Stop/Dispose借用Runtime、不释放设备lease。原write/Query永久未知则run非零；受控迟到恢复才完成夹具。重复Close/Recover/Dispose各自单飞、Root满仍能收尾；另一Host所有租约和Session计数不变 |
| S-F 完整性/迁移/RLS | head缺失不能当空；r/b/hash不符、旧同versioncodec/SQL改字节、错误tenant/Store/namespace、forged committed结果拒绝；移除RLS/多行返回/Reader类型错阻断装配或完整失败。迁移不重置r3，回退不能覆盖新事实；fake只验预期映射，真实PG/RLS/DDL另测 |
| S-G 有界资源/安全 | 8个records全部预约后第9 Reserve零Execute；既有record内安全追加/终态仍有整份MaxRecordBytes；record满/ledger坏时Controller独立关灯尝试，不宣称ledger/黑场成功。call槽/总字节满零新IO，旧Unknown不能驱逐；64诊断后保留摘要；Query session在途不叠第二读 |
| S-H 设备lease隔离 | 到期/撤权/错误Clock/Fence/authority触发原Controller安全lane；未确认释放时第二session Acquire拒绝。DB CAS成功/存储writer token变化/Runtime Dispose都不能释放灯lease或授权emit，旧设备任务未知不接管；串口/SDK实际隔离为HIL门 |

性能Profile沿§13/DEV-GOV-010：分别计完整codec检查/byte复制/hash、Read→decode/双索引、队列、registered transaction接纳/SQL CAS/commit、原ID Query、已知CAS重算次数、原call取消→storage真实资源退出、bridge Close→两个Session Released、Controller Close另计设备资源。负载为1/2独立partition、同partition2写＋8查询、0/1/8 Entries、短/MaxRecordBytes及MaxImageBytes/N+1、每record 0/1/MaxEvents、正常/冲突/Unknown/损坏、冷/热与原适用1000切换向量；记录P50/P95/P99/n、失败/超时/删失、分配、峰值内存、序列化总bytes、复制次数、root/Runtime quota/session/task/DB连接/ledger bytes/长期斜率。每完整镜像写O(MaxImageBytes)已是明确代价；不得偷删历史或仅hash保存以“优化”。方法/负载/有限resource判据已冻结，样本数/延迟/容量/RPO/RTO目标由真实Profile采纳，缺值NotEvaluated；软件fixture数据不是PG或物理耐久资格。

授权实现后的被监督命令是`dotnet build src/Modules/lighting-control/Asun.Modules.LightingControl.Storage/Asun.Modules.LightingControl.Storage.csproj -c Release`及`dotnet run --project tests/Modules/lighting-control/Asun.Modules.LightingControl.Storage.Tests/Asun.Modules.LightingControl.Storage.Tests.csproj -c Release -- --cases all`、同路径`--host aoi`/`--host stencil`；Program启动固定S-A..H＋两个Host必需清单，参数错误2，未执行/跳过/超时/Unknown Task未退出/断言或最终夹具资源失败1，所有实际执行并排空才0。真实PG/SQL/migration/RLS/耐久验证另按已登记测试隔离目标及IM-066 A1规程，不用fake通过冒充，不在本轮创建任何工程/脚本或运行这些命令。

#### A.5.6 完整规范字节Golden与本轮自审结论

Golden是一次普通StopAndDrain的Reserve镜像，不发灯命令。ApiVersion=2，Binding=(c,d,b,1,`aa`重复32byte的小写hex)，SessionId=s；Operation=(p,k,0,a,z,CommandBudget(1 tick,1 tick))，LedgerKind=6、Scope=Operation1、AcceptedStateVersion=0；Scene=null、CompiledLimits/Quantization=null、Usage.ProfileHash=`a`重复64字符。Core原CanonicalRequest沿§4.2/附录A生成，桥仅原样保全，不能把Core中的64字符hash改成桥hash32。partition为A.5.5的(t,s,l,n,d)/x/1/c/d；expected head=空镜像revision0，replacement镜像revision1，仅一entry。Entry.Revision=0、Snapshot=(Binding,s,0,Hold10,Unknown1,null,null,null,Empty,Empty,None1)、OpenCapability=null、Events=Empty、Terminal=null；History仅(0,Action1,完整LedgerReservation正文)。保守Hold不是设备处于故障的事实。

| 对象 | bytes | SHA-256小写hex |
|---|---:|---|
| 原Core CanonicalRequest | 244 | `3c85a79fd97019051f9638794ebb0d138ec167ed4ddc7bbfb7bbc17c85737cd1` |
| Partition含tag1头 | 53 | `86390ab86dc67902e984df891bd448552d7c92fe20f4b7229c77004e611c5f7d` |
| 空Image含tag2头 | 65 | `5f13421154394f1718320ae353f36831a2891524e7c34fb53b78cc4def222eed` |
| Entry含tag3头 | 930 | `1ef72d4be44b56d1a9dc6190a0f47bc1231a2c1b2496391e5252cbb88a9a0421` |
| NewImage含tag2头 | 990 | `a53028c78787832186b5ade759786170611e0d6f711c1f4768ccc94d54708848` |
| 完整ReplaceInput含tag4头 | 1159 | `b31f3f99a5e4f4521175df5e1f696387c2da582552a516c4c9abafe2b2b218bb` |

Replace.Schema=(lighting-ledger/1/schema/replace,1,`fcbd7425de40e1ff740df2e7dcacf1a8351022bc74fce02864be163ba8e0d729`)；SchemaHash按A.5.2的完整类型名与tag4计算。技术OperationId/key均`lcl-tx-b31f3f99a5e4f4521175df5e1f696387c2da582552a516c4c9abafe2b2b218bb`；此digest不是Storage PayloadHash，S-A必须调用真实StorageRequestHasher与Runtime分别重算真实技术hash，不能拿照明hash/digest替代。

空Image完整hex（换行只排版）：

```text
4c434c310200000001740000000173000000016c000000016e00000001640000000178000000000000000100000001630000000164000000000000000000000000
```

完整ReplaceInput hex；去掉换行后必须正好2318个hex字符，包含全部Entry、Snapshot、原请求和History正文，不是投影：

```text
4c434c3104000000206c69676874696e672d6c65646765722f312f736368656d612f7265706c61636500000001fcbd7425de40e1ff740df2e7dcacf1a8351022bc74fce02864be163ba8e0d72900000001740000000173000000016c000000016e0000000164000000017800000000000000010000000163000000016400000000000000005f13421154394f1718320ae353f36831a2891524e7c34fb53b78cc4def222eed000003de4c434c310200000001740000000173000000016c000000016e00000001640000000178000000000000000100000001630000000164000000000000000100000001010000000163000000016400000001620000000000000001aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa0000000173000000060000000170000000016b00000000000000000000000161000000017a000000000000000100000000000000013c85a79fd97019051f9638794ebb0d138ec167ed4ddc7bbfb7bbc17c85737cd1000000f4000000126c69676874696e672d62696e6172792d76310000000400000002000000060000000163000000016400000001620000000000000001000000406161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616100000001730000000170000000016b00000000000000000000000161000000017a0000000000000001000000000000000100000000004061616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161000000000000000000000001000000000000000000010000000163000000016400000001620000000000000001aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa000000017300000000000000000000000a0000000100000000000000000000000000000100000000000000000001000000000000000001000001900000000163000000016400000001620000000000000001aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa0000000173000000060000000170000000016b00000000000000000000000161000000017a000000000000000100000000000000013c85a79fd97019051f9638794ebb0d138ec167ed4ddc7bbfb7bbc17c85737cd1000000f4000000126c69676874696e672d62696e6172792d76310000000400000002000000060000000163000000016400000001620000000000000001000000406161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616100000001730000000170000000016b00000000000000000000000161000000017a0000000000000001000000000000000100000000004061616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161000000000000000000000001
```

以完整流byte0为起点：NewImage在offset169、length990；Entry正文offset234、length925（独立tag3表示需另加5byte头）；History.Input offset759、length400。S-A必须完整逐字段decode到末尾，核两份Reservation正文一致、原请求bytes/hash一致、initial Snapshot与History fold一致，再encode原样回环；改变History旧Input而不改投影必须拒绝。ReadResult/ReplaceResult分别按tag6＋1＋bytes(NewImage)、tag7＋1＋1＋bytes(NewImage)生成，长度1000/1001；CAS false固定hex=`4c434c31070000`、Read missing固定hex=`4c434c310600`。该missing仅为wire形状，不是可向Controller返回的可靠未找到。

本轮在原会话两轮有界自审，范围为LC-C1/C2/LC-U既有指导保持及新增LC-S1全部软件设计：第一轮核公开类型/递归字段/同值历史重放/容量与SQL CAS/注册版本，补上终态后旧Append可判定历史；第二轮核不同op并发合并、同op异bytes冲突、提交后响应丢失禁止第二attempt、技术commit与资源/设备lease分轴、迁移seed与RLS/ACL、查询缺head不当空、原根关闭失败并列/未退出不Dispose、进程重启只读而不伪造原Task。文档校验复算本Golden全流/字段/长度/hash及原Core/UI/固定向量保持，并检查本地链接和围栏。当前批准文档范围内部设计闭合；无新增代码/工程/脚本/报告。LC-S1真实实现、双Host、PG/RLS/DDL/性能/介质耐久及SDK/WPF/HIL/现场资格均未执行，各Owner与准入仍按§15.1，不能由本轮文档结论自动关闭。
