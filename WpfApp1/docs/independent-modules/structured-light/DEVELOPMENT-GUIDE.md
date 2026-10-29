# 结构光投影能力独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`Slice-0, Slice-1, Slice-2`

- 模块：`IM-011 structured-light`；来源包：`PKG-011`；专业指导：`DEV-PLT-015`、`DEV-VIS-027`。
- 版本：`0.2.12-prep`；整模块状态：`DesignReview/Prep / PreparationIncomplete`；日期：2026-10-11。Slice-0 `ManagedPatternSequence`、Slice-1 本模块托管事务/Simulator、Slice-2 本模块托管生成/观察/Advice端口：`ModuleCoreImplementationReady`（主控接收各切片六项文档规格）。Slice-3 本模块独立WPF控件：主控已接收指导规格内容（接收日期：2026-10-10），准入状态 `PreparationIncomplete/NotReady`；真实WPF/产品接线资格门未关闭。保留无非现场内部设计缺项的内容接收结论，产品代码/构建/运行未执行；B.4已支持的下游公开消费桥指导内容获主控限定接收（2026-10-11），真实AsunImage/共同标定资格未提升；WPF实窗、DPI/UIA/三语、设备联动与受影响平台接入验收保留后续门。 B.4.6 Joint producer及B.4.7重建0.2.5受支持诊断消费增量获主控限定内容接收（2026-10-11），保留原切片接收与未运行状态。IM-032 0.2.6无setup decode-only C1/S1已接收、A1指导限定内容接收；本页B.4.6.6首次观测producer确定消费指导获主控限定内容接收（2026-10-11），仅观测producer规格，不含五组重解/求解或运行资格。CAL 0.3.2-prep §7.4.6B JointQualificationBinding v1已获主控限定内容接收；本页B.4.6.7资格绑定消费增量已获主控限定内容接收（2026-10-11），范围为同次Resolve捕获/原Owner复查/完整快照技术指纹及版本域消费指导。真实binding/native/WPF/物理/运行/现场资格仍NotReady，不以纯值一致性代替资格来源或执行验收。
- 永久会话：`01a10306-eb75-7773-8a6f-aa96fac1afc3`；本轮任务：`IM-REVIEW-20261009/structured-light`。
- 基线：C# / .NET 10；可选 WPF / 本机 DevExpress 25.2.3；视觉通过 `ImageLibDotNet.cv2` 使用 AsunImage / HALCON 26.05。
- 规划消费者：3D 检测宿主、结构光试验台。本文是唯一实施规格；没有宣布产品代码、Golden、性能、WPF 实窗、HIL、计量或生产验收通过。本轮完整架构范围的可决定软件设计闭合结论见§15.1；包括AsunImage生成Adapter、独立UI、恢复和离线建议，不仅已接收Core；原运行/实施门保持。

## Core implementation binding

四个切片分别评审，不以首片替代整模块。下列工程均为未来获准后的唯一落点，当前不创建工程。当前目录无 Git 元数据；代码任务另绑定权威仓库/分支或可审计快照。

| 切片 | namespace / 责任 | 工程名（均为同名 .csproj） | 依赖 |
|---|---|---|---|
| Slice-0 ManagedPatternSequence | `Asun.Modules.StructuredLight`；不可变图案/步序、校验、canonical/hash、预算、确定性模拟 | `Asun.Modules.StructuredLight.Core` | net10.0 / BCL；无 UI/设备/视觉/IO |
| Slice-1 ProjectorTransactionPort | `Asun.Modules.StructuredLight.Projection`；事务、租约、状态、注入端口、设备模拟器 | `Asun.Modules.StructuredLight.Projection` | Core / BCL；厂商 SDK 不进入此包 |
| Slice-2 StructuredLightVisionPort | `Asun.Modules.StructuredLight.Vision`；生成/观察端口、诊断与离线候选 | `Asun.Modules.StructuredLight.Vision`；真实实现为 `Asun.Modules.StructuredLight.AsunImage`，同名 namespace | 托管端口依赖 Core、Projection 的纯值/clock/资源查询类型及BCL，不创建设备session；真实实现显式引用已确定的 AsunImage |
| Slice-3 OptionalUi | `Asun.Modules.StructuredLight.Ui.Wpf`；嵌入式参数、图案和时序诊断控件 | `Asun.Modules.StructuredLight.Ui.Wpf` | net10.0-windows；公开 Core/Projection/Vision 契约、本机 DevExpress |

代码完整路径规则：`src/Modules/structured-light/<工程名>/<工程名>.csproj`；对应测试：`tests/Modules/structured-light/<工程名>.Tests/<工程名>.Tests.csproj`。因此首片唯一代码工程为 `src/Modules/structured-light/Asun.Modules.StructuredLight.Core/Asun.Modules.StructuredLight.Core.csproj`，唯一测试为 `tests/Modules/structured-light/Asun.Modules.StructuredLight.Core.Tests/Asun.Modules.StructuredLight.Core.Tests.csproj`。其余四个工程（含 AsunImage 实现）严格代入同一规则，不另建第二套路径。最小 Host 放对应测试工程 `Hosts/`，不创建平台 Shell。

未来获准切片的允许路径仅该切片上述代码/测试目录；当前允许写入仅本文。禁止其它模块、共享契约/入口/进度/架构/登记、tools、产品 Shell、参考项目、来源原件和 AsunImage 内部。Slice-0 不动态加载后续切片；后续切片不依赖隐藏窗口或全局服务定位器。准入六门见 §15。

## 1. 职责、非目标和两个消费者

### 1.1 唯一 Owner

| 能力 | 本模块拥有 | 外部 Owner |
|---|---|---|
| 图案生成与描述 | 像素/hash、生成参数/版本、角色/方向/相位、完整生成顺序 | 宿主批准/保存配方；设备不能偷偷 gamma/缩放后沿用原 hash |
| 序列与投影事务 | 步序、投影能力、session/generation、slot/lease、请求/实际/读回、停止/黑场/排空 | 宿主拥有跨设备编排、互锁、attempt/FOV、重拍决定与恢复审批 |
| 相机数据 | 消费投影实际事实的关联需求 | camera-acquisition 唯一接受相机帧并生成 FrameBinding；本模块不生成 FrameSet |
| 相位/质量诊断 | 版本化观察结果的核验与展示、离线参数候选 | [IM-032 reconstruction-3d](../reconstruction-3d/DEVELOPMENT-GUIDE.md) 唯一拥有解码、对应关系、表面重建；image-quality 拥有图像质量事实 |
| 标定 | 只消费已核适用性的资产内容和外部资格引用；不签发资格 | calibration-assets 持有相机标定资产内容/解析及失效传播；资格决定、签发/撤回和激活绑定归模块外原资格 Owner。内容发布不等于用途资格 |
| UI/维护 | 宿主授权的限时预览、状态与恢复回执 | 宿主权限、安全链和最终质量/设备工艺决定 |

旧文在本模块另建解码/重建链与 IM-032 重复。本版冻结：本模块生成图案和执行投影，宿主通过 IM-032 公开端口取得重建候选及支持路线的成功重建诊断层，通过 image-quality 取得原图组质量诊断；B.4.7消费已接收0.2.5公开增量，不另建解码器、重建模型或高度事实。生成和解码使用各自 operation-local 模型，以相同参数及完整图案 manifest 验证等价，不跨模块传 HALCON handle。calibration-assets 0.3.1 Joint API v1已接收，B.4.6按专用观测包/字节/用途/资格进行交接；首次共同标定需要无先验setup的HybridBoth命名双层，IM-032 0.2.6 §7.6无setup decode-only已接收；首次producer通过其公开IStructuredLightDecoder取得具名payload，逐字段桥见B.4.6.6（主控限定内容接收，2026-10-11），真实运行/封存/采样资格仍NotReady。已校成功重建的DiagnosticLayers不能绕作首次标定输入。CAL 0.3.2-prep §7.4.6B已限定接收；本模块按B.4.6.7消费JointQualificationBinding v1并保留完整伴随资格/原Task关联（资格绑定消费增量已获主控限定内容接收，2026-10-11），不自行定义IM-032资格codec或替它批准接线，不用普通相机资产或Synthetic setup补造；现有其它模块及共享旧表述由主会话串行整合。

非目标：普通白/RGB/同轴照明控制、相机接受/触发实现、运动/夹具、标定求解、量测/质量放行、PCB/PCBA/AOI 专属判定、产品页/ViewModel/数据库表、厂商 SDK 实现。ACK、Ready、解码成功、清晰影像或有效点比例均不授予 PASS 或工艺放行权。deflectometry 仅保留明确类型的离线生成/诊断入口，不扩成未批准的反射计量产品。

### 1.2 消费链

3D 检测宿主：冻结配方/资产/设备 Profile → 生成/取得图案 → Plan → 投影 Upload/Prepare → 采集 Owner 武装相机 → Arm → Actual → 采集 Owner 绑定完整同 attempt 图像 → IM-032 解码/重建 → 独立计量/质量 Owner。投影结束必须单独停止/排空；本模块不等待”最后一帧”决定采集终态。

试验台：同一 Core 离线规划/模拟；或显式注入 Projection session 做限时预览/时序诊断。模拟器结果标 Simulation；无光学传感器只能诊断软件/设备回执，不说物理相位稳定。两宿主各自提供权限、Profile、clock/ledger/Adapter、语言 scope，不读对方配置/数据库。相同计划得到同校验/hash，权限/Profile 不同可以拒绝执行且原因明确。

### 1A. 新架构适配要点

**架构门禁**：所有 Core/Simulator 切片（Slice-0/1/2）不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`。只有 `Asun.Modules.StructuredLight.Ui.Wpf`（Slice-3）可引用 WPF/DevExpress，且 Core 不得反向引用它。CI 架构测试扫描程序集引用，违反即构建失败。§1.2 已明确”不能等待 Dispatcher 或把设备回调直接更新 WPF 控件”；Core 和 Simulator 的最小 Host（无 WPF）直接验证这条门禁。

**Blazor/Web 宿主中的投影状态与图案预览**：Web 端需要”展示投影序列状态、已上传图案 hash、采集绑定状态与时序诊断”时，服务端通过 `integration-transport` 的 gRPC/SignalR 推送本模块的事务快照。约束：
- 浏览器端只渲染状态与 hash 摘要，**不直接控制投影器上传/开始/停止**；所有投影命令走 3D 检测宿主的已授权路径，不经浏览器
- 图案预览（测试投影的缩略图）通过 HTTP Range 分片下载，不通过 SignalR 传输原始图案像素
- §1.1 已明确”ACK、Ready、解码成功不授予 PASS 或工艺放行权”——Web 端的投影状态指示只反映本模块的事务事实，不暗示物理光学成功

**AI 推理 Tiling 适配**：结构光图像组是 AI 推理前的**原始采集源**，但本模块不直接参与 AI 推理流程。适配约束：
- 图像组（`FrameSet`）经 `camera-acquisition` 绑定后，由 `reconstruction-3d`（IM-032）解码重建，得到高度场/点云后再由 AI 推理消费；本模块不持有推理 tile 租约
- 三态仲裁（`ai-inference` §1A）对重建结果的判定，不触发本模块的重新投影；重拍路径由宿主按已冻结策略决定

**HALCON 备选策略（图案生成路线）**：本模块通过 AsunImage HALCON 26.05 进行条纹图案生成（`gen_structured_light_pattern_info` 等算子），是 HALCON 备选双跑 CI 的**图案生成落点**。约束：
- 图案像素 hash 是本模块的核心不变量；双跑须确保 HALCON 路线与托管参照路线对相同参数（频率/相位/尺寸/编码方案）生成相同 hash——**hash 一致是强门禁**
- 已知差异：HALCON 内部的 gamma 预补偿和量化策略；宿主/设备不得在原 hash 基础上再做 gamma/缩放（§1.1 已明确”设备不能偷偷 gamma/缩放后沿用原 hash”）
- **第三方 oracle 覆盖有限**：本仓固定 Open3D 快照不含结构光图案生成，无第三方参照；托管参照须按 HALCON 26.05 资料逐参数自证；HALCON 仍是生产路线，不引入平行生产算法

## 2. 组件、依赖和所有权

```text
Host A / Host B
 -> Core Validate / Plan / Simulate
 -> Projection session -> IProjectorAdapter
                       -> IProjectionClock / IOperationLedger / IProjectionAuthority
 -> Vision generator -> AsunImage / ImageLibDotNet.cv2
 -> Host observation port -> IM-032 / image-quality / calibration-assets
OptionalUi -> host application port + same contracts
```

Core 的 ImmutableArray 为 .NET BCL 值集合；不可借用可变 array。Projection 持有投影连接/回调和 lease，ledger 拥有耐久记录；宿主拥有采集帧和业务存储；Vision 生成器独占模型/临时图像，导出托管内容后释放；UI 只持有受预算约束的显示副本/显示 lease。HALCON/native 句柄和厂商对象不进入以上共享 DTO。

缓存 key 为 projectorId/generation/patternHash/transferFormat；活跃 lease 不可 LRU 淘汰。同图案重复 step 不复制像素。上传格式转换必须成为新的 transfer artifact/hash，保存原图谱系；slot/文件名不替代内容身份。模块独立性是可单独引用/构建/测试/发布，不是零依赖。

## 3. Module API Contract v0.2

本节和附录 A/B/C/D 同属唯一 v0.2。Slice-0 C#形状在A；Slice-1完整值/请求/结果/session/Adapter/ledger/authority/分页事件在C；Slice-2托管生成/观察/Advice与可查询资源端口在B；Slice-3 Host/Payload/结果/订阅/显示lease/关闭在D。正文表解释对应声明；涉及方法签名/嵌套字段以这些完整声明为唯一形状，不保留无类型Payload或未定义返回类型。它们是本模块拟实现API，未编译/运行，不是其它模块/厂商现API；既有切片接收与未运行门保持；本轮完整范围的执行、内容审核、修复和文档验证在本永久原会话完成，总控只接收状态（见§15.1）。产品 C-01～C-08 仅为宿主映射。

### 3.1 Slice-0 规范

ID 采用 1..128 ASCII `[A-Za-z0-9._:-]`、Ordinal 大小写敏感；版本为 SemVer 2.0.0，不接受空格/v 前缀/省略段。当前 ManagedPatternPlan/ProjectionPlan/GenerationSpec.ContractVersion 固定为字符串 `0.2.0`；其它版本仅走 §8 显式导入，不按“可解析 SemVer”自动接受。hash 为64位 hex，校验接受大小写，输出/canonical 小写。未知 enum 拒绝。

具体规范化：PatternArtifact.ContentSha256 与每个 ProjectionStep.PatternHash 均先校验为恰64个 ASCII hex 字符（不去空白、不接收 `0x`），再解码32 bytes；引用匹配按这32 bytes比较，不作原字符串大小写敏感比较。Plan 输出新建元数据记录，将上述两个字段和 PlanSha256 均展示为64位小写 hex，不修改调用方输入或 Content。canonical 中这两个 hash 字段均直接写32原始bytes，不写hex字符串长度或文本；其余ID仍Ordinal大小写敏感。大小写混合/全大写/全小写表达同一digest，预算中的字符串长度也相同，因此不改变计划hash。附录 A.1 给出完整固定向量。

| 字段 | 单位、有效域、行为 |
|---|---|
| Width/Height/PixelFormat | 正 int，px；ByteGray=1 byte，UInt16Gray=2 bytes；packed、无 padding、uint16 little-endian |
| ByteLength/Content | checked Width*Height*bpp；Content.IsDefault=ReferenceOnly；非 default 的空内容非法；提供内容须重算 SHA256，结果 Verified |
| Role/Direction | Black/White 的 Direction=None；Gray/GrayInverted/Phase/SingleStripe/Custom 必须 Vertical 或 Horizontal；Both 只属于生成参数 |
| PhaseIndex/PhaseRadians/SpatialFrequency | 仅 Phase 必填，index>=0；rad 有限 [0,2π)，cycles/pixel 有限 >0；其它角色均 null |
| IntensityScale | finite 0..1、无量纲数字比例，不是功率/照度；变化产生新 artifact/version/hash |
| Step | Ordinal 从0连续；StepId 唯一；PatternId/hash 精确引用；ExposureRole opaque ID，不绑定相机 |
| ManagedPatternPlan | ContractVersion、SequenceId/version、Patterns、Steps；无第二份 limits、device、lease、标定或 native handle |
| PlanningLimits | MaxWidth/Height/Patterns/Steps/Issues/Events 正 int；MaxPatternBytes/MaxWorkingBytes 正 long；调用方显式传入，无隐藏默认 |

default/空集合、重复 PatternId/StepId、缺引用、未使用图案均拒绝；同图案供多个不同 step 使用合法。Content 长度必须 <=int.MaxValue（当前单 ImmutableArray 支持域）；超大总图案集合以多个有界 artifact 表达，不以 checked 溢出/OOM 代替拒绝。调用方创建 Content 前预检预算并复制可变源；Planner 不再次复制像素，只逐块哈希已有 immutable bytes。不提供内容时不声称已检验像素，Upload 必须补齐后再次重验。

错误结构 Code/Path/DetailKey；Path 使用 `Patterns[i].Width`、`Steps[i].PatternId` 等原输入索引，按 Path Ordinal、Code 枚举值排序。为避免无界错误，维护最多 MaxIssues 个最小排序项；发现更多错误置 IssueLimitReached=true、结果保持 Rejected。取消返回 Cancelled，无部分 ProjectionPlan。无设备或 native 排空。

预算先校验数量/尺寸/checked bytes，再索引/哈希。图案 bytes 每唯一 artifact 计一次，steps只引用。MaxWorkingBytes 是准入用保守逻辑计账，不冒充 CLR 实际分配：固定 charged bytes = 4096 + 1024*P + 512*S + 512*MaxIssues + 128*MaxEvents + 4*输入所有字符串 UTF8 byte 总数；checked 溢出即 BudgetExceeded。Content 已由调用方拥有不计新分配；canonical 用 streaming，不另建全量像素或 canonical 大数组。报告同时输出 PatternBytes/ChargedWorkingBytes；CLR峰值另测 §13。此公式是同版本固定准入规则，改变它须更新 contract。

Canonical 固定域 ASCII `ASUN-SL-PLAN-2\0`，末尾 `\0` 是单个 NUL byte 00，不是反斜线和数字0。次序：ContractVersion、SequenceId、SequenceVersion；Patterns按 PatternId Ordinal排序、写count及附录 PatternArtifact 的声明字段（跳过 Content，ContentSha256 写32原始bytes）；Steps按原序写count及声明字段（PatternHash 同样写32原始bytes）；最后按 PlanningLimits 声明次序写全部 limits。int/int enum为int32 LE，long为int64 LE，string为int32 UTF8 byte长度+bytes（UTF8无BOM），nullable为byte0/1+值；double为binary64 LE，-0统一+0，NaN/Inf先拒绝。ByteLength 在 Width/Height/PixelFormat 之后；版本保留原合法SemVer文本，不合并 build metadata。hash包含元数据、限制和内容hash，不含 Content本体、Integrity、语言/时间/诊断。不使用 JSON属性顺序或 GetHashCode；canonical版本变化按major处理。

### 3.2 Projection 值类型

以下均 immutable；ID/SHA 复用 Core 的校验规则，非空 Guid 用于 OperationId/SessionId/LeaseId/ActualId/BootId。Generation为正 ulong，StateVersion/LeaseVersion为正 long，首次Open的expected值才允许0。每个 nullable均在表中注明；不可观测物理量为null，不是0。

| 类型 | 完整字段与语义 |
|---|---|
| ClockStamp | BootId、ClockDomainId string ID、Ticks long>=0、FrequencyHz long>0；仅同boot/domain频率可相减；预算ns按checked整数向上转换 |
| AssetRef | Id、Version、Sha256；仅标定/非量测预览明确允许null，Profile/Runtime必需 |
| Capability | ProjectorId、FirmwareVersion、Fingerprint、Generation、BootId、Width/Height、Formats、MaxSlots/Bytes、Modes、ReadbackLevels、SwitchSettleNs/MinimumHoldNs、CanPreempt、StopBoundNs nullable、TemperatureRangeC/PowerRangeW/DutyRange(nullable)、PhysicalMappingHash、ObservedAt、EvidenceMode；集合/范围类型见C.1 |
| ProjectionSequence | ProjectionPlan、Mode SoftwareStep/HardwareSequence、TimingSteps、ProfileRef/RuntimeRef、CalibrationRef nullable、CapabilityFingerprint、PhysicalMappingHash、RequiredReadback、TotalBudgetNs/StopBudgetNs>0 |
| TimingStep | Ordinal、PatternHash、ExposureRole、HoldNs>0、SettleNs/ExposureStartOffsetNs/GuardBeforeNs/GuardAfterNs>=0、ExposureDurationNs>0、TriggerRole ID |
| PatternLease | LeaseId、SessionId、ProjectorId、PatternHash、Slot>=0、Generation、CapabilityFingerprint、BootId、ExpiresAt、LeaseVersion；slot<MaxSlots |
| CommandMeta | OperationId、IdempotencyKey ID、RequestSha256、SessionId、ExpectedGeneration、ExpectedStateVersion、Deadline、AuthorityScope ID |
| PreparedReceipt | OperationId、SequenceHash、SessionId/Generation/StateVersion、LeaseSnapshotHash、ExactLeases(LeaseId/version) |
| ArmedReceipt | OperationId、PreparedOperationId、ExecutionOperationId、SequenceHash、SessionId/Generation/StateVersion、Mode、TriggerId、LeaseSnapshotHash、FrozenLeases |
| ProjectionActual | ActualId、CommandOperationId、ExecutionOperationId、SessionId/Generation/StateVersion、SequenceHash、Ordinal、PatternHash、LeaseId/LeaseVersion、LeaseSnapshotHash、TriggerId、RequestedAt、ActualAt nullable、ReadbackLevel、Trust、TemperatureC/PowerW nullable、ProfileRef/RuntimeRef、CalibrationRef nullable、EvidenceMode；无frameId |
| OperationSnapshot | OperationId、RequestSha256、Phase、LogicalOutcome nullable、TerminalOutcome nullable、LastActualOrdinal nullable、StopStatus、BlackoutStatus、DrainStatus、ResourceStatus、DeviceInvocation、Issues、Generation/StateVersion、ObservedAt |
| SessionSnapshot | SessionId、ProjectorId、State、Generation/StateVersion、BootId、CapabilityFingerprint、ActiveExecutionId nullable、StopStatus/BlackoutStatus/DrainStatus/ResourceStatus、ObservedAt、Stale、Issues |
| ProjectionEvent | OperationId、EventOrdinal long从0连续、Kind、ClockStamp、Generation/StateVersion、SequenceHash nullable、Actual nullable、Issue nullable |
| DrainReceipt | OperationId、DrainStatus、ResourceStatus、BlackoutStatus、LogicalOutcome nullable、TerminalOutcome nullable、ObservedAt、Issues |
| ProjectionLimits | MaxSlots/MaxCommands/MaxCallbackItems/MaxEventsPerOperation正int；MaxPatternBytes/MaxInFlightBytes/MaxLedgerBytes/MaxRetainedOperations/MaxDiagnosticBytes正long；CommandBudgetNs/CleanupBudgetNs正long；caller显式提供 |

ReadbackLevel=None/CommandAck/PatternId/OpticalSensor；Trust对应C.1的ActualTrust=None/CommandAccepted/DeviceReported/SensorConfirmed；光学确认也只证明该测点。LogicalOutcome/TerminalOutcome取Completed/Failed/Cancelled/TimedOut/Unknown；Phase=Accepted/Invoking/Executing/LogicalEnded/Draining/DrainUnknown/Terminal。StopStatus=NotRequested/Requested/Confirmed/Unknown；BlackoutStatus=NotRequested/Requested/AckOnly/Confirmed/Unconfirmed；DrainStatus=Pending/Confirmed/Unknown；ResourceStatus=Held/Released；DeviceInvocation=KnownNotInvoked/Invoked/Unknown。Unknown drain禁止Released及TerminalOutcome。纯副作用前Rejected单独通过CommandReply表达，不伪造设备operation终态。

### 3.3 Projection 方法、端口、请求和结果

`ProjectionSession.Create(projectorId, adapter, clock, ledger, authority, limits)` 返回 `IProjectionSession`；依赖均注入。命令Async返回 `ValueTask<CommandReply<T>>` 且带 CancellationToken；Query、Retention Release/GetUsage使用C完整声明。CommandReply<T>字段：Disposition Accepted/Rejected/Replay/Conflict/Released、OperationId、Value nullable、Issues、Snapshot nullable、Tombstone nullable；Released无Value且有原墓碑，不再执行。Rejected/Conflict无新设备调用，已接纳后通过Snapshot/查询表达未知或未排空，不能把取消异常吞成Rejected。Hardware方法是单独 `IAsyncEnumerable<ProjectionExecutionItem>`。

| 方法 | 请求（Meta=CommandMeta） | T/前置 |
|---|---|---|
| OpenAsync | OpenRequest(Meta,ExpectedProjectorId) | SessionSnapshot；Closed，首次expected值0；读取身份/能力、黑场确认后Ready |
| GetCapabilityAsync / GetSnapshotAsync | ct | Capability/SessionSnapshot；最后观察事实，Stale不冒充实时 |
| Validate（同步） | sequence,capability,limits,ct | Core ValidationReport；无副作用 |
| UploadAsync | UploadRequest(Meta,Artifact,RequestedLeaseNs) | PatternLease；必须Verified内容，Ready/Uploading |
| RenewLeaseAsync | RenewRequest(Meta,LeaseId,ExpectedLeaseVersion,RequestedLeaseNs) | LeaseMutationReceipt(Disposition Renewed/Released/AlreadyReleased,Lease nullable,StateVersion) |
| ReleaseLeaseAsync | ReleaseRequest(Meta,LeaseId,ExpectedLeaseVersion) | LeaseMutationReceipt；仅可释放无执行引用的lease |
| PrepareAsync | PrepareRequest(Meta,Sequence,ExactLeases) | PreparedReceipt；全部验证/租约覆盖执行+cleanup后才Prepared |
| ArmAsync | ArmRequest(Meta,PreparedOperationId,TriggerId,Mode,LeaseSnapshotHash) | ArmedReceipt；宿主完成相机/触发源武装，再冻结 |
| DisplayStepAsync | DisplayStepRequest(Meta,ArmedOperationId,Ordinal,PatternHash,LeaseId,LeaseVersion) | ProjectionActual；仅SoftwareStep，下一连续ordinal |
| ExecuteHardwareSequenceAsync | HardwareSequenceRequest(Meta,ArmedOperationId,LeaseSnapshotHash) | ProjectionExecutionItem stream；仅HardwareSequence、一次启动 |
| StopAndDrainAsync | StopRequest(Meta,ExecutionOperationId,ReasonKey,CleanupBudgetNs) | DrainReceipt；未排空返回Pending/Unknown，不业务终态 |
| BlackoutAsync | BlackoutRequest(Meta,ExecutionOperationId nullable,ReasonKey) | BlackoutReceipt(OperationId,Confirmation,ObservedAt,StateVersion,Issues)；不代替排空 |
| QueryOperationAsync / GetEventsAsync | OperationQueryRequest(operationId,deadline) / EventQuery(operationId,afterOrdinal,maxItems,deadline)，ct | OperationQuery / EventPage；C.1–2的Found/NotFound/Unavailable，NotFound不证明未执行 |
| ReleaseOperationAsync / GetRetentionUsageAsync | RetentionReleaseRequest / ct | RetentionReleaseReply / RetentionUsage；只压缩终态且实际归还的结果，不释放设备lease；§6.1/C.5 |
| RecoverAsync | RecoverRequest(Meta,AbortOperationId,ExpectedBootId,ExpectedFingerprint) | SessionSnapshot；同代恢复见§5 |
| RunDiagnosticAsync | DiagnosticRequest(Meta,Kind Health/SelfTest/Timing,ProfileRef,BudgetNs) | DiagnosticReceipt(OperationId,Observations,Status Observed/NotObserved/Failed,Issues) |
| ShutdownAsync | ShutdownRequest(Meta,CleanupBudgetNs,ReasonKey) | DrainReceipt；所有在途operation可查；Unknown保持Owner |
| DisposeAsync | 无 | 只在Shutdown drainConfirmed后托管收尾；否则DisposeBeforeDrain并保留恢复Owner |

Observation数值项统一 DiagnosticObservation(Name/Value nullable/Unit/Source/ObservedAt/Status)，类型见C.1；不得仅给bool健康。ProjectionExecutionItem为StepActual(Actual)或LogicalEnd(ExecutionOperationId,LogicalOutcome,Issues)，判别字段及nullable互斥见C.1–2，恰一个LogicalEnd；它不代表资源终态。实际终态从Query/Event取得。stream消费取消/提前退出也启动同一cleanup，不依赖枚举器继续读才关光。

IProjectorAdapter的模块端口（非厂商现有API）完整签名/嵌套Adapter请求和结果见C.3；不将上层CommandMeta直接传厂商。AdapterContext=OperationId/SessionId/Generation/Deadline/CleanupScope；结果均包含Invocation、设备原始错误码、ObservedAt、确认等级；Upload返回slot，Drain返回回调/设备命令/slot引用是否全部释放的证据。Execute返回AdapterStreamItem；Readback返回pattern identity nullable+等级；Release/Close必须有已确认资源结果。模块lease由session建立/续租，adapter不维护第二权威租约。厂商类型/回调只在未来Adapter包。

IProjectionClock.Now返回ClockStamp；不注入墙钟充当单调时间。IOperationLedger和IProjectionAuthority使用C.3的完整请求/结果：BeginAsync(LedgerBeginRequest,ct)、AppendAsync(LedgerAppendRequest,ct)、ReadAsync(OperationQueryRequest,ct)、ReadEventsAsync(EventQuery,ct)；CheckAsync(AuthorityRequest,ct)。包括Unavailable状态、有限deadline、revision/回执bytes/错误，禁止用裸bool替代。Begin和Invoking耐久提交先于设备调用，保存失败禁止输出；调用之后保存失败=Unknown且禁止重放。内部已接纳cleanup沿原授权scope完成关光，不再次被UI退出取消。

请求hash：固定域ASUN-SL-CMD-2、方法名、Meta声明字段（跳过RequestSha256）、请求其余字段按表次序，沿§3.1编码；跨切片新增编码：Guid为RFC 4122网络字节顺序16bytes（不使用默认ToByteArray混合字节序），ulong为uint64 LE，bool为byte0/1，DateTimeOffset为UTC ticks的int64 LE。嵌套plan用其hash，lease列表按LeaseId上述16bytes字典序排序，资产完整引用，内容用hash，不序列化委托/handle。session重算后比较。相同idempotencyKey/hash先回放原结果，再检查当前CAS；异hash为Conflict。一个OperationId不得绑定不同key/hash。ExecutionOperationId贯穿所有step和cleanup，各命令自身operation只记录子命令。重复查询不执行设备；NotFound/超时不允许新key重试未知副作用。

终态/排空字段覆盖execution及持有资源的operation；Upload的Accepted回执只表示租约已建立，不表示该租约资源Released。父execution和session汇总未释放lease/子命令，不以子命令ACK宣布父任务终态。空闲已缓存图案由显式Release或Shutdown释放；新execution可复用Ready的有效lease，但前次execution的在途引用必须先排空，不能以缓存仍驻留推断仍有设备命令运行。


## 4. 处理链、时序和事件

### 4.1 纯托管处理

Validate(plan,limits,ct)按§3.1验证；Plan调用同一校验，失败不返回部分plan，成功保留原Steps顺序、排序后的Pattern目录、hash、资源账和Integrity；返回元数据副本按§3.1将ContentSha256/PatternHash规范为小写，不改输入。复杂度O(P log P+S+提供内容bytes)。Simulate只接受Validated生成的ProjectionPlan（仍校验其版本/hash与结构），按SimulatedTicks产生确定性计划事件，不读真实clock、不延时、不伪造Actual/ACK/曝光/黑场。

SimulatorOptions指定StepTicks>0、MaxEvents>0、Fault=None/MissingStep/DuplicateStep/OutOfOrder/Timeout/ResourceRejected、FaultOrdinal。None必须FaultOrdinal=null；其余必须0..N-1；OutOfOrder需至少两步且FaultOrdinal<N-1。正常事件PlanStarted、StepPlanned(ordinal)*、PlanCompleted；Missing跳过目标step，Duplicate重复该step，OutOfOrder交换目标及下一step，然后验证观察序列并PlanRejected；Timeout在目标前PlanTimedOut；ResourceRejected在起点PlanRejected。事件数先预计算，超MaxEvents/计划MaxEvents返回BudgetExceeded、零事件；从不静默截断。每事件SimulatedTicks=(事件序号)*StepTicks，checked溢出拒绝。PlanCancelled是托管终态，和设备LogicalCancelled无关。

### 4.2 设备处理和曝光窗口

设备链固定：验证权限/预算 → ledger Begin → 读取能力/boot/generation及互锁输入 → Upload逐项验证内容/资源 → Prepare冻结exact leases → 宿主采集/触发Owner武装 → Arm冻结hash/trigger/lease快照 → Software或Hardware单一路径 → 记录LogicEnd → Stop/Blackout → Drain → ResourcesReleased → 终态。错误/取消从当前点转cleanup，不回到旧步骤自动重发。

TimingStep须满足（全部ns、checked计算）：
- SettleNs >= capability.SwitchSettleNs，HoldNs >= MinimumHoldNs；
- ExposureStartOffsetNs >= SettleNs+GuardBeforeNs；
- ExposureStartOffsetNs+ExposureDurationNs+GuardAfterNs <= HoldNs；
- 所有HoldNs之和+StopBudgetNs <= TotalBudgetNs；每个租约到期必须晚于预计结束+cleanup预算；
- 每次Display/硬件启动前再验证lease/generation/能力/授权有效性。武装后不续租改变冻结快照；时间不足拒绝启动。
- 相机跨clock窗口只能通过宿主提供的已资格化ClockMapping（source/target domains、offset、uncertaintyNs、valid interval、hash）核验；两端guard各覆盖uncertainty。无映射不直接相减，不声称同步合格。

SoftwareStep：宿主在该步达到要求的读回等级和settle后触发/等待相机；投影器不自己触发相机。HardwareSequence：唯一触发源Owner由Profile绑定，适配器仅运行一次武装序列；宿主完成外部触发源协调。两模式不能混用。§3.2 TimingStep描述冻结窗口，不将软件计时/请求时间当物理显示时间；无实际传感器时ActualAt按读回来源记录，光学相位稳定=NotObserved。

### 4.3 事件和流完整性

ProjectionEvent.Kind全集：OperationAccepted、CapabilityVerified、LeaseAcquired、Prepared、Armed、StepRequested、StepActual、LogicalCompleted、LogicalFailed、LogicalCancelled、LogicalTimedOut、LogicalUnknown、StopRequested、StopConfirmed、StopUnknown、BlackoutRequested、BlackoutConfirmed、BlackoutUnconfirmed、DrainPending、DrainUnknown、Drained、ResourcesReleased、Completed、Failed、Cancelled、TimedOut、Unknown。预检拒绝只回CommandReply，不向未接纳执行编造事件。

正常顺序Armed → (StepRequested/StepActual)* → 唯一LogicalCompleted → StopRequested → StopConfirmed → BlackoutRequested → BlackoutConfirmed → Drained → ResourcesReleased → Completed。故障可在LogicalEnd前发安全Stop/Blackout，逻辑结果随后固定；但所有终态必须在Drained和ResourcesReleased之后，Confirmed黑场才允许成功/Ready。释放的是本次execution的在途引用；未过期缓存lease继续由session单独记账，Shutdown必须释放全部。黑场最终Unconfirmed而资源确已排空/释放可终态Unknown，但设备保持Faulted隔离。DrainUnknown只是非终态，保留Held，不得组合“Cancelled + Released”。

Hardware stream只接StepActual及恰一个LogicalEnd；ordinal必须0..N-1连续、hash/generation/lease完全匹配。缺步/重复/乱序/None/双LogicalEnd/LogicalEnd后数据/流断开=SL-SEQ-001或SL-IO-001，保存原数据诊断，不能用帧数相等补齐。stream LogicalEnd不含ResourcesReleased；需继续查询/订阅事务事件。消费者丢弃stream仍触发cleanup。迟到回调按原ExecutionOperationId/generation归档，不更新新session。

## 5. 状态、错误与恢复

State全集Closed/Opening/Ready/Uploading/Prepared/Armed/Displaying/Cooling/Draining/Faulted/Unknown/Disposed；一个物理投影器一个串行写Owner，所有状态转换CAS递增StateVersion。活动中热/功率越界仍须先Draining，确认关光/排空后才Cooling；空闲且无在途时可直接Cooling。优先Blackout只改变调度顺序，不绕权限、ledger和CAS；若不能抢占，能力必须CanPreempt=false并由硬件互锁停止，不虚构软件保证。

| 状态 | 可接纳动作 | 禁止/后继 |
|---|---|---|
| Closed | Open、查询 | Open确认黑场/能力→Ready；失败→Faulted/Unknown |
| Ready/Uploading | Upload、Renew、Release、Prepare、诊断、Shutdown | Upload失败前置资源归还；Prepare成功→Prepared |
| Prepared | Arm、StopAndDrain、Blackout、Shutdown、查询 | 禁止Upload/Renew/Release改冻结集合；Arm→Armed |
| Armed/Displaying | 匹配模式/ordinal的执行、StopAndDrain、Blackout、Shutdown、查询 | 禁止改图案/租约/参数；结束→Draining |
| Cooling | Release无执行引用lease、Health、Stop/Blackout/Shutdown、查询 | 不续租/上传/Arm；温度等恢复且无在途→Ready |
| Draining | cleanup/查询/幂等重复Shutdown | 不接受新输出；确认排空/释放且黑场确认→Ready或Closed |
| Faulted/Unknown | 查询、Stop/Blackout/Shutdown、满足条件的Recover | 不重试生产；未知结果不能ClearError变Ready |
| Disposed | 只读墓碑/usage与旧identity精确Released回复；Projection由ledger提供 | 新identity/ObjectDisposed，绝不调用设备；旧已释放identity先查墓碑，不作为新请求接纳（C.5） |

异常码和动作不把投影失败改成业务FrameSet事实；本模块报告执行无效，由采集Owner处理帧组。

| 稳定码 | 含义、状态/保留内容 | 唯一下一步 |
|---|---|---|
| SL-VAL-001/002 | 参数错误/空输入；Rejected，无副作用 | 修正原请求后用新operation；保留问题路径 |
| SL-PAT-001 | 内容hash/尺寸/格式不符 | 重新取得artifact并重验，不沿旧身份修改 |
| SL-CAP-001 | boot/generation/能力变化；旧lease失效 | 停止并排空；新代Open，不跨代Recover |
| SL-CON-001 | 同key异hash、并发CAS冲突 | 查询原operation；不新key绕过 |
| SL-LEASE-001 | 过期/版本/slot不符 | 已执行则cleanup；重新Upload/Prepare |
| SL-SEQ-001/SL-TRG-001 | 缺/重复/乱序/hash或触发不符 | 整次执行无效，保存Actual；重拍由宿主决定 |
| SL-RDB-001 | 读回不符/等级不足 | 不升级Trust，停止对账 |
| SL-TEMP-001 | 温度/功率/占空越界 | Cooling或Faulted，黑场/冷却/维护 |
| SL-BLK-001 | 仅ACK或黑场未确认 | 禁止下一输出；查询/物理确认/维护 |
| SL-IO-001 | 设备调用/通信未知 | 原operation查询；不盲重试 |
| SL-CANCEL-001 | 已接纳取消、排空未确认 | LogicalCancelled、DrainUnknown、Held；恢复Owner继续查询 |
| SL-RES-001 | slot/bytes/队列/ledger/deadline预算超限 | 副作用前拒绝；在途超限停止准入+cleanup |
| SL-MIG-001 | contract/Profile/runtime解释不兼容 | 隔离原operation，使用原解释器/回退 |
| SL-VIS-001/002/003 | 生成参数不合法/观察谱系不符/诊断不可用 | 不生成可执行结果/不展示旧诊断为当前结果 |

恢复分两条：
1. 同boot/generation/fingerprint：Query原operation → 停止触发Owner → Stop/Blackout → Drain确认 → 释放lease/cache引用 → Recover(原AbortOperationId和精确boot/fingerprint) → 自检/能力复核 → Ready。不可从旧armed继续，重新Prepare/Arm。
2. boot/generation改变或设备重连：旧operation保留Unknown及恢复记录；先确认旧物理输出关闭/在途排空或设备复位证据，再Close旧连接、建立新session/Open读取新generation，清空旧cache/leases。复位后的空缓存不证明旧曝光未发生。若无法确认旧资源，保持隔离，不能用“新Open成功”覆盖旧Unknown。

## 6. 取消、期限、线程、关闭与资源

Slice-0支持ct；校验每个artifact/step和内容每64KiB检查取消，返回Cancelled/no plan；Simulate逐事件检查。无Stop/native排空。并行调用不共享可变集合/随机源/clock，错误顺序一致。

Slice-1所有命令在接纳前检查取消/deadline；取消或过期前未调用设备为KnownNotInvoked。接纳后取消只是停止后续工作，不能撤销已发生投影。设备调用超时若结果不确定=Unknown。普通命令使用有限预算，cleanup使用独立scope/token和CleanupBudgetNs，不能沿已取消ct立即退出。cleanup截止仍未排空则DrainUnknown；恢复服务保留连接/回调/lease owner，UI不得强制Dispose。

队列有界，ledger/事件达到限额前停止准入；审计级Actual/逻辑结束/资源事件不合并、不drop。回调线程只封装/入队；溢出记录不可恢复完整性错误、隔离输出并cleanup。不能等待Dispatcher或把设备回调直接更新WPF控件。事件订阅者异常隔离，不改变设备事实，终态可Query。ledger保留策略由宿主采纳；不能删除尚未终态/被恢复引用的记录。

HALCON模型每operation独占，同handle生成/参数修改/解码串行；reentrant/global不表示同handle并发安全。native工作取消仅停止准入并等真实返回，不能用Task.WaitAsync超时当原算子已结束；到期未知保留模型/输入Owner，排空后才clear/dispose。成功、失败、取消均释放临时图像/模型；生成部分失败不发布部分可执行manifest。

UI关闭先停止交互/解绑新命令，再由宿主Shutdown并显示排空状态，确认后释放view和session；窗口可移交恢复面板，但不能假称设备已关。宿主退出需在Dispatcher/事件循环仍可用时等待Shutdown，ProcessExit仅尽力通知。异常退出/重启按ledger原operation对账。DisposeAsync发现活动/未知资源必须报告DisposeBeforeDrain，不删除恢复Owner。

### 6.1 有限结果保留与释放（Slice-1/2/3）

结果payload、回放bytes、事件、幂等identity分别计账，统一纯值类型在C.5。ProjectionLimits/VisionLimits/ViewOptions均显式包含RetentionPolicy；原MaxLedgerBytes/MaxRetainedBytes和新额度同时适用，取更严限制。MaxPayloadRecords覆盖已接纳运行/未知/终态完整结果，MaxPayloadBytes覆盖canonical请求、ReplyBytes、snapshot、事件、错误/引用/像素及序列metadata；MaxIdentityRecords/Bytes单独覆盖仍有payload的identity和释放后的墓碑，不把字典key忽略为“免费”。索引逻辑计账每identity为512+4*该identity所有字符串UTF8总bytes；OperationTombstone额度按C.5固定小头与索引公式预留，不能把完整回执/像素藏在墓碑；所有identity在接纳前预留可压缩空间。payload按C.3完整canonical编码实际bytes另加每记录1024、每集合项128的固定索引预算，checked溢出拒绝。UI任意enum/nullable/联合类型依声明字段编码，类型判别Kind为int32；接纳前做有界count/string校验及计账，不依赖JSON/CLR对象大小猜测。

MaxSingleReplyBytes是每次回执/Query/Page编码上限；MaxPayloadBytes/记录额度不足时，SL-RES-001副作用前拒绝新identity，不创建无限拒绝日志或去重记录。已接纳操作预留自己及cleanup/终态/墓碑额度；未知任务不会被新请求覆盖，cleanup不得被普通新请求占走预留。释放payload返还payload额度，不返还identity额度；达到有限identity额度时停止接纳新操作，既有查询/停止/排空/Release仍可用。此初版采用有限且不滚动的登记：所有已接纳OperationId/idempotencyKey（UI为CommandId、RequestId/SubscriptionId）和hash墓碑保留，不按LRU/时间逐出。不能清索引、重建session或重启后让旧身份变New；Projection生产ledger跨重启保留同identity，内存Vision/UI只在原session scope内接受请求，已Close的对象不能复用scope，创建新scope不恢复/重放旧未知operation。

ResultRetentionNs从最终Terminal且实际DrainConfirmed/ResourceReleased的时刻开始计，未终态/未知无过期计时；到期只标ResultRetentionState.Expired，不自动删除/再运行，Query仍可读完整结果，caller可Release并压缩为墓碑。该值不是“墓碑TTL”。跨clock boot重启不能相减；无法确认保留时间已满就继续Retained，显式Release不依赖到期，但须满足终态/资源/owner条件。没有提供外部永久去重替代门，初版不开放清空/轮转墓碑API；额度满是可见拒绝，不用无限结果缓存换持续吞吐。长期消费者据实际吞吐/寿命冻结有限identity预算，容量耗尽需另获批的持久分区/迁移方案，不能在本轮偷增清理接口。

ReleaseOperationAsync（Projection）/ReleaseResultAsync（Vision）/ReleaseCommandAsync（UI）仅压缩自己的已终态结果，不是Stop/ReleaseLease/ReleaseDisplay：ExpectedStateVersion CAS核对、所有相关native/回调/执行引用实际归还、父/子记录不再作为Prepare/Arm/恢复输入、外部消费者已取得必要证据才可Release。Projection设备Unknown终态仍隔离：如该记录仍被故障恢复引用则Busy，不能释放。Upload/Prepare/Arm记录仍提供有效lease/执行上下文时Busy，必须先ReleaseLease/Shutdown等完成归还。不能对活跃/DrainUnknown返回Released；Busy不改结果，Unavailable/期限到期不证明任何压缩完成。重复Release同id/hash返回AlreadyReleased且同墓碑，异hashConflict，不新增release操作索引；CAS不匹配且未释放返回Conflict。Release未找到返回NotFound，绝不是可以重跑的证明。

墓碑包含原identity/hash、原结果SHA256、原终态/真实资源状态、释放时刻和最后revision，不保留像素/native/大事件。Query已释放身份返回QueryStatus.Released+Tombstone、无payload；GetEvents返回Released/空events/墓碑，不伪造ledger断档为Unavailable。Projection同key/hash重新提交返回CommandDisposition.Released，Value=null/墓碑，LedgerBegin.Released不触发Adapter；异hashConflict。Vision同OperationId/hash返回相应Status.Released，Plan/层/metrics/candidate结果为空、Issues含SL-RET-001，详细原终态从Query墓碑取得，不用Released伪装成功；异hashSL-CON-001。UI同CommandId/hash返回UiReplyStatus.Released/Result=null/Tombstone，不能再次发光/生成。SL-RET-001只是已释放结果，SL-RET-002为仍有使用者；二者必须自然三语显示，不直接输出enum。

Query/Release/GetUsage均有限deadline/本地QueryBudget或CommandBudget，使用原身份不消耗新的identity槽；usage在同Owner锁线性化返回计数。Close先停止准入/真实排空，不主动删除结果/identity；CloseConfirmed表示工作资源归还，不表示回放已丢弃。Closed后原对象仍允许只读Query/GetUsage/Release到其有限session生命周期（Dispose前）；Dispose只有所有活跃Owner已移交/归还且完整结果都已Release或移交给明确接收者才可结束。Projection墓碑保留在注入ledger，Vision/UI恢复服务持有原session，不能用GC把payload/幂等索引变无主。原结果immutable传给caller后模块释放只解除自己的保留引用，caller副本属于caller预算，不偷偷invalidate它或删宿主证据。Projection的ReleaseOperationAsync、Vision的ReleaseResultAsync和UI的ReleaseCommandAsync成功后各自只把对应identity的payload降为墓碑；ReleaseLease/ReleaseDisplay/SubscriptionClose仍是独立资源动作，必须先按本页Owner规则真实归还。释放Projection父operation前，父/子operation和lease引用均须已终态/Released；释放Vision生成结果前，Observed层/Advice评估和模型均须已释放；释放UI命令前，关联显示lease/订阅已Released/Closed。Host应先取得所需immutable副本再Release，不要求副本继续由模块Query。

### 6.2 本轮两轮有限反例走查

第一轮按API/容量走查：合成Policy.MaxPayloadRecords=2、MaxIdentityRecords=3及显式byte预算，两个已终态结果占payload2，第三请求因payload满拒绝；Release第一个后第三可接纳，第四仍因identity3满拒绝（payload空也不例外）。Query/同id重放/release不增加槽；超过任一byte上限1 byte副作用前拒绝，墓碑额度预留不足也不能接纳后强删。ResultRetentionNs到期仍Query完整，Release后精确Released/墓碑，同id异hashConflict。同样验证Projection/Vision/UI实例，数字只为合成断言，不是现场容量。

第二轮按Owner/恢复走查：第一个操作DrainUnknown占槽时Release返回Busy，Close仍Held；新请求不得覆盖它，迟到资源归还后保持原Cancelled/TimedOut逻辑，只有最终Terminal/实际归还及无父子使用才可压缩。Projection子Upload记录活跃lease/Prepared依赖、Vision候选未结束、UI显示/订阅回调未结束分别Busy；原Host/finally移交拒绝仍持有Owner。缺键/Released/Busy/Unknown三语文案实际动作区不显示enum；详细诊断才保留技术key/code。这些为文档反例走查，未运行产品代码/实窗。

保留的所有索引都在Policy额度内：Projection leaseId/ReleasedLease tombstone、上传cache身份、子命令/parent、Vision去重/Advice身份、UICommand/display RequestId+LeaseId/subscriptionId均占IdentityRecords/Bytes，不能只算operation字典。显示slot/lease/回调对象分别受MaxSlots/MaxCallbackItems/MaxThumbnailBytes/队列上限，Adapter只保存活跃调用，终态回放统一ledger/session，不在Adapter再无限缓存回执。每项索引用kind+Guid作复合身份以免跨kind碰撞；不共享一个未定义global cache。RequestId→LeaseId或SubscriptionId→closed-state是有界墓碑，释放/关闭后精确查Released/Closed而非重新分配/重新订阅。同id新hash冲突，过期Acquire要先Release旧结果，不新identity偷偷顶替仍Held资源。

清理保留能力的准入预留：每次设备序列在Prepare前预留剩余step子命令N、Stop/Blackout/Shutdown各1及所有可能ReleaseLease的M个identity槽/小头字节（N为余steps、M为唯一lease数量，实际已有槽不重计），这些仍计Policy总额度，不新增无限“安全队列”。Open/Upload也先预留其最终Shutdown/slot释放需要的槽；内部cleanup重试沿原key/id，不不断造新key。普通新请求不能占这些已预留槽；结果Release/Query/GetUsage不需新增identity。Host finally的cleanup Meta首次在这组预留槽登记，重复finally必须复用同request；容量满仍能用既有预留完成清理，不给新生产输出准入。结果先压缩再计余量，未知/未使用cleanup预留在归还后计为剩余有限identity可用量。设备已终态但slot仍缓存时ReleaseLease使用它的预留释放identity；不能因identity满而遗弃设备资源。需要超过预留的未知恢复动作保持原Owner/原request对账，停机并报容量原因，不盲重发新输出。

Hardware已Released请求的stream只返回一个ExecutionItemKind.Released（Actual=null、LogicalOutcome=null、Tombstone必填、SL-RET-001），不发StepActual/LogicalEnd或启动设备；正常新请求/尚Retained replay仍沿C.2完整stream规则。Host看到Released走Query墓碑，不拿它当缺帧后重执行。UiCommandQuery.Status=Found返回原UiReply（含StateVersion/RetentionState）、Released仅墓碑、NotFound/Unavailable无payload，原CommandId/RequestHash在墓碑准确保留；不因查询缺结果而再发新的CommandId。已释放显示Acquire返回DisplayStatus.Released/Lease=null/墓碑，QueryDisplay.Released无bytes，ReleaseDisplay重复同LeaseId返回Released=true及相同墓碑；释放后不能把原显示buffer重新复制回Host缓存。已关闭订阅同id/hash接入只给原closed-state且无新sink调用，订阅payload压缩/释放计入D的Policy；Closed=true且Confirmed/Released才可把原sink引用移除，不因deadline清字典使旧id成为新订阅。

## 7. HALCON 26.05 / AsunImage 路线与诊断

全部调用通过`using ImageLibDotNet;`中的`cv2`，不另接HALCON程序集或HOperatorSet，不扫描AsunImage内部，不重复审查“封装是否有算子”。只有消费项目实际C#参数类型、tuple/image-array重载或封送有歧义时，查看公开签名/编译核对；该具体问题仅阻该AsunImage适配切片。以下算子名/参数是26.05官方语义，不是未验证的C#调用示例。

### 7.1 路线和参数

| 路线 | 固定处理/适用条件 | 选择与拒绝 |
|---|---|---|
| 主路线 | create_structured_light_model('3d_reconstruction') → set参数 → get回读 → gen_structured_light_pattern → 导出完整有序manifest/hash → clear_structured_light_model | 默认hybrid Gray+phase；输入完整、Profile和标定适用才可交IM-032 |
| Gray-only受控备选 | pattern_type='gray_code'，其余链相同 | 只有已采纳Profile同样本资格才可选择；不是在线遇错自动降级 |
| 部分镜面候选 | pattern_type='single_stripe'；HALCON同时生成single-stripe、Gray和phase，不能只取单条纹组 | 官方支持，不默认Unsupported；新增帧/资源预算且同样本评估后批准使用 |
| deflectometry | 显式modelType='deflectometry'，独立Profile和诊断 | create默认虽是deflectometry，本模块不沿默认；不得调用3D表面重建冒充高度 |
| Custom | 显式托管artifact，可规划/投影 | 无批准下游解码契约则只预览，不推断可量测；不自动转换路线 |
| AI | 无本模块训练/推理实现 | 外部Advice需独立版本/谱系，不能改Actual、生产参数或设备指令 |

| 参数 | 类型/单位/范围 | 来源与变化影响 |
|---|---|---|
| pattern_width/height | int>=1 px，均>min_stripe_width/2 | Profile/投影器实际尺寸；绑定camera_setup时须等于projector index1尺寸 |
| min_stripe_width | int>=4、2的幂；不超过宽/高分别上取2幂后的最小值 | Profile；不是任意double或“越小越好” |
| pattern_orientation | vertical/horizontal/both | 3D运行官方建议vertical，reconstruct仅用vertical；标定需both由标定Owner规定 |
| pattern_type | gray_code_and_phase_shift / gray_code / single_stripe | 已批准路线；不自动fallback |
| normalization | global / inverted_pattern | global生成black+white；inverted_pattern生成Gray及反图、图更多，部分镜面候选 |
| single_stripe_width | int>=min_stripe_width、2幂且>=4，尺寸约束同手册 | single_stripe Profile；其它路线不偷偷使用 |
| min_gray_difference | integer>=0 DN | IM-032/image-quality资格Profile；0几乎关闭对比拒识，不能自动降0求通过；手册默认30不作生产阈值 |
| persistence | bool，默认false | 常规处理false；相位中间图诊断需解码前true及独立预算；变更清结果 |
| camera_setup_model | HALCON模型语义为camera=0/projector=1；专用Joint资产/资格/导出 | 按已接收calibration-assets §7.4及B.4.6核JointUse/当前水位、真实file与meter→mm1000；Synthetic只CalibrationReplay。首次无setup观测走B.4.6.6；真实重建缺B.4.6.7完整绑定/当前资格时不启动真实重建，生成不替代求解/资格 |

生成参数变更清解码状态，必须重新gen且发布新参数/manifest/sequence hash；不能在旧模型上继续decode。每方向官方phase组为4幅；整套数量/顺序取gen真实结果和官方排列，不把4/6/8/32写成固定设备帧数。导出器按§7.4显式完整布局定义和26.05生成语义逐对象核角色映射；官方页面没有公开的“对象序号→角色”查询API，不把页面组别说明当全局索引表；保留HALCON一基索引为SourceIndex，公开steps转零基，一一核验尺寸/格式/hash。无法证明角色/相位元数据时返回SL-VIS-001，不猜文件名/数组下标含义、不标Custom规避检查。生成参数和manifest原顺序传给IM-032重建operation-local模型并核对图案数/hash；不把生成模型handle传出。

### 7.2 下游观察与合法中间结果

宿主接入端口 `IStructuredLightObservationPort.ObserveAsync(ObservationRequest,ct)` 返回 `ObservationReply`。托管契约：
- ObservationRequest=OperationId、AttemptId、SequenceHash、Generation、ManifestHash、OrderedBindingRefs(AssetRef)、CalibrationRef nullable、ProfileRef、RuntimeRef、RequestedLayers(枚举 Correspondence/PatternRegion/Phase/GrayBinary/GrayCorrespondence/SingleStripe/Defect)、RoiRef nullable、BudgetBytes/BudgetNs正long、PersistenceRequested。
- ObservationReply=OperationId、AttemptId、SequenceHash/ManifestHash、AlgorithmRoute、ProducerId/Version、Profile/Runtime/Calibration refs、Status Observed/NotObserved/Rejected/Cancelled/DrainUnknown、Metrics、LayerRefs、Issues、DrainStatus/ResourceStatus。
- LayerRef=AssetRef、Kind、Width/Height、PixelType、CoordinateFrameId、Unit、ValidDomainRef、SourceBindingRefs；Metrics=Name/Value nullable/Unit/Denominator long/DomainRef/ThresholdProfileRef nullable/Status。所有图像通过宿主受控证据/显示lease引用取得，不跨模块传native handle。
- manifest、attempt、采集binding顺序/数量/尺寸/完整性必须精确匹配；缺/重复/跨attempt拒绝整组；不拼旧帧。无质量/光学数据=NotObserved，不能用空数组表示合格。
- 已接收image-quality/IM-032公开字段的宿主消费映射见B.4：原图诊断、完整重建请求和发布Simulator的原接收保持；B.4.6–7确定指导增量获主控限定内容接收（2026-10-11）。IM-032 0.2.5支持完整黑白/反图与成功重建后的无句柄诊断层，HybridBoth+Diagnostics拒绝；首次Joint无setup decode-only源规格现已接收，B.4.6.6首次观测producer确定指导已获主控限定内容接收（2026-10-11）；不循环依赖已校重建；CAL 0.3.2-prep资格绑定源桥已限定接收，本模块B.4.6.7资格绑定消费增量已获主控限定内容接收（2026-10-11）。实际接线/运行/算法/UI/资格未验。

以下是HALCON 26.05算子语义和IM-032执行Owner边界，不等于其公开端口已交付这些图层。HALCON可执行decode_structured_light_pattern(byte/uint2完整image-array)，然后get_structured_light_object；IM-032当前光学输入只接受Mono8，其它位深明确拒绝，见B.4.3；correspondence_image、pattern_region无须persistence。decoded_phase_shift_image、binarized_image、gray_code_correspondence_image、decoded_single_stripe_image需提前persistence=true；解码后切true会清结果，须新operation重解码，不能读旧phase。defect_image只适用deflectometry，3d路线不索取。reconstruct_surface_structured_light仅non-specular/vertical对应及有效标定，归IM-032；无效域不填0，测量单位/世界坐标由其契约决定。

相位误差仅在来源明确给出rad、相同周期/相位定义及真值的有效共同域D上计算：e=atan2(sin(phiObserved-phiReference),cos(phiObserved-phiReference))；报告mean(abs(e))、RMS、max(abs(e))、有效像素数/ROI分母、invalid比例，单位rad。IM-032 0.2.5的Phase单位为HalconPhaseValue，不能直接带入此公式或改成rad，缺尺度/真值/共同域时NotEvaluated。不用有符号平均证明精度；多个候选不平均成生产参数。不能从软件clock抖动推导光学phase误差。

### 7.3 同样本比较与有界离线建议

冻结代表样本：正常、弱对比、饱和/眩光、遮挡、运动/漂移、不同材料、无结果与公差边界；按attempt/材料/设备分组，训练/选择和验收组隔离。同一曝光图组才能比较兼容解码参数；生成参数改变须取得匹配的新完整图组，不能拿旧曝光假评估新pattern。主/备/single-stripe比较正确对应、误接受/拒绝、共同域phase误差、覆盖及拒识原因、端到端P50/P95/P99、峰值managed/native/diagnostic资源。未实测不说最快/最佳。

先image-quality ROI粗质量检查，再完整序列精诊断；ROI只能保原幅坐标/域（需要时reduce_domain），不可偷偷crop/scale改变投影对应与标定。ROI结果只证明其域；完整图案仍需全组。任何降采样只用于展示，不改数值事实。

`RecommendAsync(RecommendationRequest,ct)`只离线Advice：请求=OperationId、BaselineProfileRef、EvidenceSetRef、Candidates(有序有限GenerationSpec/Profile组合)、MaxCandidates/MaxEvaluations正int、BudgetNs/Bytes正long、ExpiresAt、AcceptanceProfileRef。候选枚举来自调用方批准范围，禁止在线无限搜索；排序固定为“全部质量/拒识门通过优先，再最小误接受率、最小误拒绝率、最小max相位误差、最小P95、最小峰值bytes，最后候选ID Ordinal”。误接受/拒绝率的真值、计数分母和各上限均取AcceptanceProfileRef；无阈值不视为门已通过。候选按请求顺序各评估一次，MaxEvaluations不足覆盖全部候选则副作用前拒绝，不评到一半静默选优。缺真值/共同域/资源或性能目标的候选标NotEvaluated、不得推荐为生产值；互不匹配曝光组不可排名。

结果=AdviceId、BaselineHash、EvidenceHash、CandidateId/参数hash、Metrics/拒绝原因、Rank、ExpiresAt、NotEvaluated项；输出不是配方。证据/设备/资产/Profile/hash变化或到期即Stale；宿主人工批准产生新Profile/sequence/model epoch并重验。不静默改曝光/gamma/阈值、不自动重拍、不重新估标定、不覆盖原证据。

### 7.4 AsunImage 生成 Adapter 的公开装配、布局与像素导出

本节补齐生成实现的确定装配，沿B的IStructuredLightGenerationAdapter及既有Generate/QueryDrain/Close公开协议，不改Core/B/C/D原合同。生成只使用HALCON 26.05；Gray+phase为主路线，Gray-only和single-stripe按已批准Profile选取，deflectometry只生成/离线诊断。解码和自解码都不在生成器执行，本模块不因导出元数据另写相位解包、相机标定或重建。厂商Adapter仍只需实现C.3端口，具体SDK实现不在本范围。

**显式布局输入，禁止索引猜测。** 官方gen页规定四类图组、每axis四个cosine相移kπ/2（k=0..3），get_object页规定phase周期覆盖min_stripe_width投影器pixel；它们不提供全局对象序号标签API，也不授权从公开数组下标猜Both的V/H顺序。故真实生成工厂必须显式收到已版本化的完整原始布局，消费已登记Profile的数字事实；首次无setup图组仍使用这一布局，但没有CalibrationRef。此布局不是相机setup、光学/计量资格或某产品数据库。缺布局、有未指定phase、布局非完整、真实gen不等布局统一SL-VIS-001，拒绝整组而不降级Custom。生产参数或候选改变生成Spec时，宿主须提供与新Spec精确匹配的另一生成定义，不以旧定义评估新pattern。

下面是本方AsunImage程序集新增的拟实现公开装配形状，未编译/不冒充当前DLL现有API；仅同步校验/复制有限元数据，不在Create时生成、打开设备/文件或创建设备session。

```csharp
namespace Asun.Modules.StructuredLight.AsunImage;
public sealed record AsunImageGenerationDefinition(
    Asun.Modules.StructuredLight.Vision.GenerationSpec ExpectedSpec,
    System.Collections.Immutable.ImmutableArray<
        Asun.Modules.StructuredLight.Vision.GeneratedPatternEntry> OrderedLayout,
    Asun.Modules.StructuredLight.Projection.AssetRef LayoutEvidenceRef,
    long MaxResidentNativeBytes);
public static class AsunImageGenerationFactory
{
    public static Asun.Modules.StructuredLight.Vision.IStructuredLightGenerationAdapter Create(
        AsunImageGenerationDefinition definition,
        Asun.Modules.StructuredLight.Projection.IProjectionClock clock,
        Asun.Modules.StructuredLight.Vision.VisionLimits limits);
}
```

ExpectedSpec所有字段逐值等于Generate实际Spec，包括ProfileRef/GeneratorVersion/SequenceId/version与nullable CalibrationRef；布局沿B.GeneratedPatternEntry原SourceIndex=1..P、PatternId、Role/Direction/PhaseIndex/PhaseRadians/SpatialFrequency/ContentSha256，所有字段必经B/§3.1校验。向B.4下游manifest映射时RoleOrdinal为同axis/角色的0起有序计数；GrayInverted恰对应原Gray同RoleOrdinal、phase PhaseIndex为0..3且精确匹配Layout定义的生成相位顺序，黑/白均RoleOrdinal0/Axis=None。不把SourceIndex直接当RoleOrdinal，也不将单axis的Layout顺序套Both。LayoutEvidenceRef为宿主明确引用的本生成定义来源，GeneratorId/GeneratorVersion绑定这一完整definition和HALCON版本；同GeneratorId/GeneratorVersion与SpecHash组合不得登记两份不同OrderedLayout；不同合法Spec各有其明确definition，该宿主不可变绑定随root传入，不能接受相同GeneratorVersion却换未记录phase定义。不能用随机新hash替代；其来源读取/发布由宿主已有Profile/证据Owner负责，不引入模块服务定位或第二存储。Module不凭引用自证布局正确：真实生成验收由本模块AsunImage实现Owner核定数字布局，生成时再逐对象比真实输出hash。LayoutEvidence必须保留完整布局、参数、实际HALCON/runtime/generator版本和参考图案hash，原definition/LayoutEvidenceRef随原root和生成证据一起交宿主保存，不能仅返回几个像素hash后丢来源；原件语义证据随本模块实际native资格记录；该软件验收是实现任务，不能移交客户决定内部映射。

布局取得/验收方法固定为：独占的HALCON26.05模型同参数生成真实图组并保留原序→以官方四组定义标注候选角色→用同参数vertical-only/horizontal-only的独立生成图组逐对象像素验证轴，global黑/白必须全0/255，Gray及其反图按逐pixel和255及同RoleOrdinal核对，Gray从粗到细→各axis四phase的相位由原数字生成坐标/独立四步cosine参考验证kπ/2与1/MinStripeWidth cycles/pixel，不从camera解码相位反推→single-stripe每axis亮条覆盖每投影器pixel恰一次、完整Gray+phase组仍存在→将验证后的实际原序/完整像素hash及精确版本登记为definition。参考定义只用于核metadata/生成数字图，不生成替代图案或相机测量；四phase不能凭“有4幅”就通过。图案extent截断、Gray与single条组外观重合而无法唯一证明、版本变化或原始phase相位原点无法证明时拒绝该定义，保留原native验收失败，禁止人工改label凑通过。下游IM-032仍独立重gen并逐原manifest像素hash核布局，不信任这个标注自己构成资格。

本版主线默认建议是ThreeDReconstruction/Hybrid/Global：运行Vertical，首次Joint Both；MinStripeWidth、尺寸和single宽均需Profile明确，无通用生产数字默认。min_gray_difference只在下游Decode Profile使用，生成不接入该判据；SingleStripeWidth仍须2幂且>=MinStripeWidth，Width/Height均>SingleStripeWidth/2；其它route的SingleStripeWidth=null。IntensityScale固定1，HALCON本生成出口只ByteGray，不能转uint16或偷偷gamma/resize。Custom/UInt16的托管规划与投影能力保持，由其原内容Owner供artifact，不能宣称HALCON生成了uint2图案。定义MaxResidentNativeBytes>0是针对完整P/W/H/版本和本生成实现的保守准入envelope，受limits/context剩余限制；未有该上界拒绝native生成而不阻Core/模拟端口。

**处理步骤和费用。**

1. 宿主按§9.3/9.4在factory前预留原根/所有task及输出；Create核definition/clock/limits并深复制有限布局。一次实例只绑定一个definition，宿主多定义依次创建独立instance/session或独立完成后更换，不运行时覆写ExpectedSpec。缺布局/非法definition在factory或Generate前明确SL-VAL/SL-RES/SL-VIS，native调用0。
2. Generate原OperationId/RequestHash/Deadline入实例有界表；同id/hash回原状态/结果，异hash冲突。每实例一个串行native执行Owner，队列按VisionLimits有限，关闭停准入。native调用只能在普通工作线程，不在UI Dispatcher；外层原Task及完成路径强持到真正结束。
3. P=布局count，N=checked(W*H)，ByteGray总输出B=P*N，各artifact N<=int.MaxValue。session在调用port前先核B<=GenerationLimits.MaxPatternBytes/其输出与Retention上限、P<=各MaxPatterns及W/H限额，再把GenerationLimits/limits各维和父剩余的小值写VisionAdapterContext.MaxManagedBytes/MaxNativeBytes/MaxResultBytes及Deadline；Adapter只拿公开context，不猜未传入的GenerateRequest.Limits。逻辑托管预留至少2*B+65536+4096*P（packed输出+导出暂存+metadata/hash），session将GenerationLimits.MaxWorkingBytes与VisionLimits.MaxManagedBytes限制传入context后，Adapter核不超context剩余；若实现转移buffer确无副本，仍按该保守准入，不靠引用算零。native按definition.MaxResidentNativeBytes全额预留，含gen完整tuple/所有选取引用和模型，不在gen完成后才问是否超预算。全局HALCON/native隐藏分配实际峰值另测，准入上界不是实测达标值。
4. create_structured_light_model显式modelType；依次set pattern_width、pattern_height、min_stripe_width、pattern_orientation、pattern_type、normalization，SingleStripe才set single_stripe_width；生成模型persistence=false、不绑定camera_setup。get同参数及type逐值回读，任何不等拒绝。然后gen一次，count_obj核实际P，禁止将返回tuple截成MaxPatterns或重排。
5. 对i=1..P按原序select_obj；count_channels必须1，get_image_size/get_image_type必须Expected W/H/byte。get_image_pointer1取得指针/byte/W/H并再核一致；图像为完整原幅row-major byte，checked N一次有界Marshal.Copy到自有buffer，只读原指针，不调用reduce_domain/crop/convert_image_type/scale_image。select_obj只是引用，pointer生命周期依附原图像；Copy完成前不得释放selected或gen tuple，不把IntPtr存入DTO/任务或返回调用方。
6. 每buffer重算SHA256并等于OrderedLayout[i-1].ContentSha256，再赋原metadata到GeneratedPatternPixels，Content为自有ImmutableArray。所有对象全核后才交给session形成B规范SpecHash/ManifestHash及A计划；Role/Direction/phase只来自已核definition，不按亮度/文件名推断。global两图和互补Gray的像素核验可随导出执行，未能证明完整角色元数据或phase定义立即整组拒绝，无部分Generated。
7. 每个选取对象在copy/hash完毕后释放本引用，完成/取消/失败均待实际调用退出再归还完整gen tuple、临时buffer、最后clear_structured_light_model；共享buffer有引用不当释放。native不能被ct抢占时逻辑取消固定、根保Held直到原Task真退出并实际clear，不因WaitAsync到期清句柄；释放异常分别保存cleanup错误，查询DrainUnknown，不把资源不明标Confirmed。只有全部本次native/暂存归还后可GenerationAdapterReply.Completed/Confirmed/Released，result托管payload仍沿Retention单独Release。GeneratorVersion精确ExpectedSpec.GeneratorVersion。

QueryDrain/Close仅用B已有接口；原生call未退出时Close返回原全量UnresolvedOperationIds/Held/有限结果，后台root继续持模型/Task，重复Close只观察第一次清理，不第二clear。factory的definition/clock借用边界明确，root完结后才归还自身深副本；三个Adapter若由宿主同对象复用，Close按实际对象去重，不以角色名多关一次。真实C#tuple/iconic类型和Dispose封送在消费项目公共签名/编译中确认，不能扫描AsunImage内部，不能把尚未编译写作已签名通过。

**SL-GX断言及两个消费者。** A无UI 3D宿主按§9.4单Generate+Query/Release/Close，B独立实验台同factory/definition/自己的namespace、clock/根与限额；两者相同定义必须产生相同P/bytes/hash/metadata及原计划，B含WPF也只能消费同回复。B.4.6首次producer和B.4.7诊断仍使用各自唯一下游Owner，生成器native解码调用0。

| 断言 | 输入/确定结果 |
|---|---|
| SL-GX01 | 宿主提供完整已核ThreeD/Hybrid/Global Both定义，P按真实布局；全规范bytes与每SourceIndex角色/hash一致；Vertical对应projector column、Horizontal对应row，phase metadata每axis完整四步，不对称W/H的参考pixel分别核轴。无camera_setup仍Generated，仅生成不授重建资格；缺定义/phase原点/任一hash错误→Rejected/native消费与设备调用0 |
| SL-GX02 | GrayOnly/Global、Hybrid/InvertedPattern、SingleStripe及Deflectometry各明确definition；global黑白0/255，反Gray和255，single组与完整Gray/phase均在原序，deflectometry不获取3D高度。仅预览Custom独立Core路径；字节转uint2/gamma/删反图/删normalization/重排均拒绝，不伪匹配IM-032 |
| SL-GX03 | N/P/B/envelope/managed/单artifact及父期限上界±1；gen count/尺寸/type/通道不等、pointer元数据不等/空值→明确失败，未结束原图不dispose；无native预算源时native调用0。两根参数/取消独立，不拿另一实例envelope补足本实例 |
| SL-GX04 | create/set/get/gen/select/copy/hash/clear逐点fault，gen迟到、caller取消、Close/Query异常；保原Task/元数据/费用、业务首错与cleanup两轴；待真实native退出再首次clear/归还，Unknown不冒Released，late完整图只归原取消操作 |
| SL-GX05 | A正常归还、B未知全量移交拒绝/丢确认/晚确认；原definition、gen tuple/selected、pointer借读期、原Task/完成路径及额度在原root，确认全量接收才换Owner，Transferred不释容量；正常Query→Release→Close与墓碑保留同§9.4.1。旧Core289-byte和B.4向量不重算，native成功Golden只能来自本模块实际26.05运行资格 |

## 8. 适配器、版本与接入门

版本使用SemVer：字段语义、状态/canonical/恢复变化为major；仅可忽略的可选信息为minor；实现/文案修正为patch。未知必需enum/major明确拒绝。旧v0.1没有本版完整canonical，导入保留原身份为LegacyUnverified；通过显式转换生成新sequence/version/hash，不“修复”旧hash或已提交Actual。

设备Adapter冻结SDK/固件/Profile/physical mapping及原始错误码映射；无可观测能力使用null/Unsupported，不冒充Confirmed。实际SDK暂不纳入本轮。真实AsunImage消费者编译仅核C#类型/重载/封送，不是重开依赖/许可证准入。托管Vision端口不加载AsunImage，真实实现按§7数据导出/清理及Golden验证。更新任何包前停止新准入，处理旧operation到排空或隔离，保留旧解释器和rollback包；回退不重放设备命令。

## 9. 最小 Host 与调用顺序

### 9.1 Slice-0（公开API示例，尚未编译）

```csharp
var validation = StructuredLightPlanner.Validate(plan, limits, ct);
if (validation.Status != CoreStatus.Valid) return;
var planned = StructuredLightPlanner.Plan(plan, limits, ct);
if (planned.Status != CoreStatus.Valid) return;
var simulation = StructuredLightSimulator.Simulate(planned.Plan!, options, ct);
// 只比较计划hash/模拟事件，不能产生ProjectionActual或生产结论。
```

Host-A传内存artifact/steps；Host-B在独立进程/实例重复同输入并验证字节hash/问题顺序/事件等价。测试Host无设备/视觉/网络/文件业务/桌面初始化；读取测试fixture不成为Core运行依赖。

### 9.2 Projection Host（语义伪代码，不是厂商调用示例）

```text
Create(explicit adapter, clock, ledger, authority, limits)
Open(meta) -> Validate(sequence, capability, limits)
Upload(each Verified artifact) -> Prepare(exact leases)
host acquisition owner arms camera/trigger
Arm(prepared, trigger, frozen lease hash)
try:
    Software: DisplayStep(each ordinal); pass Actual to acquisition owner
    Hardware: consume StepActual* and one LogicalEnd
finally:
    StopAndDrain(original execution, fresh cleanup scope + finite budget)
    Query(original execution) until Confirmed drain or recovery deadline
    if drain unknown: transfer owner to host recovery service; keep resources
    else: Shutdown; Dispose after confirmed release
```

每个命令使用新的子operation和稳定key，重试同一命令沿原meta；查询/cleanup不沿已取消ct。Blackout单独成功不替代StopAndDrain。宿主采集Owner接收Actual、创建binding；IM-032诊断由宿主传入完整证据；此Host不实现相机/解码。测试台和检测Host不共享全局session/语言/数据库。



### 9.3 Slice-1 无UI Host 调用模板

以下是使用附录C公开调用的宿主语义模板，未编译/未运行；存活槽和下述动作属于宿主本地责任，不是新增模块API、恢复服务DLL或厂商SDK接口。输入包括projectorId、adapter/clock/ledger/authority/limits、Verified artifacts、ProjectionSequence、批准scope/triggerId、armAcquisition/acceptActual、业务预算、独立cleanup预算以及adoptRecovery闭包。模块不承担相机武装或产品结果接受。

**两个Host共用的宿主动作定义：**

- 宿主有进程生命周期的强引用表，不能只由方法局部变量、异常栈、窗口或弱引用持有。factory前以checked预留一个存活槽及其全流程额度；没有槽就拒绝本次创建，factory调用次数为0。配置明确MaxLiveOwners、每槽MaxOriginalTasks/MaxSubmittedIds/MaxMetadataBytes/MaxHeldInputBytes以及总额度，均为正且有限；计入请求/hash、Task/closure、输入引用、回执和错误metadata，不能把引用的完整输入/结果算成零。额度独立于模块RetentionPolicy，仍受宿主总资源预算；模块payload/identity额度不因Host预留而返还。按唯一artifact数/step数/候选数预先计算所有业务、读快照、回调、stream MoveNext/Dispose、Query/Release、Stop/Close/usage/Dispose/移交所需槽，预留cleanup份额，溢出/超限在factory前拒绝。
- Create是本地有限构造，不调用设备/启动native工作。保留预留槽跨越factory调用，返回后立刻将session强绑定到该槽，**绑定完成才进入业务try**。构造抛错且确认没有返回session/后台Owner时只退本次空预留；若不能确认，槽保持ConstructionUnknown及输入Owner，不再次factory。Bind使用已预留位置，不再申请可失败的槽；不能由factory产生无人接收的后台任务。
- `启动并登记(标签, 原请求或无请求, 调用闭包)`：调用前先在槽中预留任务条目、保存原OperationId/idempotencyKey/hash及完整有界signed request；不能等Accepted回执才登记。调用返回ValueTask后只做一次AsTask并立即登记**原Task**，以后观察都用这个Task；同步抛错也保留该条目和原请求。读/Close/usage/Dispose/移交没有OperationId时用宿主本地条目号关联session，不捏造模块OperationId。Host回调与stream的enumerator/各MoveNext原Task和Dispose原Task也归此槽，流提前退出仍保留它们及原hardware request。
- `有限观察(条目, 期限, token)`仅观察原Task，返回Completed/Faulted/Cancelled/WaitExpired和可用回执；等待用Task.WaitAsync或同等有界机制，等待Task不得替换原Task。timeout/取消/Task已完成都不推断DrainConfirmed/ResourceReleased；原Task fault也不表示副作用未发生。业务调用使用业务ct及有限业务wall期限；模块deadline按clock构造，Host另用单调wall stopwatch防卡死。模块与宿主回调的调用入口须同步有限返回异步句柄，禁止在入口同步阻塞；异步wrapper不能使同步卡死变可取消。
- cleanup在factory前已冻结独立正预算：Stop、Close、Query/Release、usage、Dispose、移交各有有限wall观察份额及有限总cleanup wall截止，模块请求另有对应clock/ns预算；每阶段取其份额与总截止剩余值的较小者，业务ct不参与。未启动而已无剩余预算时记NotStarted并保留Owner，进入后续finally；不无限等、不加后台重试。阶段观察使用各自cleanup token，token/等待截止只停止观察，不删除原Task。首次构造的cleanup请求保存到槽，重复finally复用原请求/原Task，不再造key。
- `记录清理失败`把阶段、原条目、异常/截止/拒绝写入已预留的有界错误metadata，不抛出覆盖业务异常，不把全部Exception.Data/无限stack/log复制进去；计数和可定位的首个错误保留，超额置截断标志。先捕获业务异常的ExceptionDispatchInfo，finally结束后原栈重抛；cleanup错误留在存活槽供恢复读取。任一尚未确认接收的cleanup错误阻止正常退槽，连同全部原Task走移交或保持RecoveryHeld，不能在成功Dispose后顺手丢掉错误。没有业务错误而cleanup失败时才报告Host清理失败，同时保留槽。
- `尝试移交`使用预留的本地OwnerTransferId和adoptRecovery闭包；闭包收到整槽session、**全部原OperationId、原请求、原Task、保留结果/输入、错误和额度**，不是只给unresolved子集。移交自身原Task也先登记。接收者先有界预留并强持有整个Owner，再确认接收；确认前原Owner仍是唯一写入者，未确认接收者只托管引用、不另发命令。移交pending期间原Owner也停止新写入，按同一offer对账，不新offer重复移交。回执拒绝、异常、超时或丢失则原槽持续存活；晚到确认只在原offer上提交唯一Owner切换。确认切换后旧槽才交出写入权和额度引用，不能先remove再调用接收者。
- `尝试Dispose并退槽`仅在Close明确Confirmed/Released、所有原业务/回调/cleanup Task和enumerator已观察结束、usage明确PayloadRecords=0且PayloadBytes=0、所有相关lease/model/回调实际归还、原namespace墓碑查询Owner已确认保留时调用Dispose。Dispose原Task也登记并有限观察；抛错/卡住/未确认成功不得退槽。Vision内存墓碑仍须由原session查询Owner持有，不能以Dispose删掉它们；没有满足墓碑接收条件便保持原session并走全量移交。正常退槽需成功Dispose且没有未确认原Task/移交；确认全量移交则原Owner不再Dispose接收者的session。无接收者时有界槽保持RecoveryHeld，拒绝后续占槽创建，不靠GC/进程退出声称归还。

Hardware的原Task条目按MaxEventsPerOperation而非只按计划step数预留：最多E+1次MoveNext（包含结束观察）、E次acceptActual和1次enumerator.Dispose；checked计入其它请求/快照/cleanup条目后再核宿主上限。第E+1次若仍有事件即记完整性错误，不调用其acceptActual或再启动MoveNext。enumerator.Dispose观察也用独立cleanup份额，不沿已取消业务ct；若MoveNext仍pending，不并发调用同enumerator的Dispose，而保留enumerator/原Task和待Dispose标记，先走session Stop/Shutdown及恢复移交。流内业务异常先捕获，流Dispose失败单独记cleanup错误，不能覆盖它；这些未接收的cleanup错误也阻止正常退槽，随全槽交恢复Owner确认保留。同步调用抛错时条目明确NoTaskReturned及原异常，不伪造Completed Task证明资源已归还。移交接收者须先观察原Close/usage/Dispose/MoveNext等未确认Task，再依据真实状态恢复，不在它们pending时盲目重发或启动并发Dispose。

`Meta`语义保持附录C：OperationId由RetentionIdentity.New(limits.Retention.NamespaceId)分配，key为首次生成的Guid文本，RequestSha256经ProjectionRequests.Sign填充，SessionId/scope显式绑定；Open的ExpectedGeneration/StateVersion=0，其余来自有限观察的GetSnapshotAsync。Deadline用clock.Now加对应正ticks并checked，requestBudgetTicks/cleanupBudgetTicks与Profile ns预算一致。读快照自身也登记原Task；快照失败/超时不能补猜generation/CAS。Stop或Shutdown若因此不能构造请求，记录NotStarted并保留原execution/session，继续后续finally的usage/移交。

```text
预留存活槽(全流程计数/字节与cleanup预算)        // 容量不足：不调用factory
session = ProjectionSession.Create(projectorId, adapter, clock, ledger, authority, limits)
把session强绑定到预留槽                       // 在业务try之前，槽由进程存活表持有
businessError = null; closeEvidence = null; usageEvidence = null
try:
    open = 保存signed OpenRequest(Meta首次, projectorId)，启动并登记OpenAsync，有限观察
    Require(open): 仅Accepted/Replay且Value非空继续；其它进入异常清理
    capability = 启动并登记GetCapabilityAsync，有限观察
    Validate(sequence, capability, limits, ct)必须Valid
    对artifacts按ContentSha256去重：
        保存signed UploadRequest(Meta, artifact, checked(TotalBudgetNs + CleanupBudgetNs))
        启动并登记UploadAsync，有限观察；Require后收集唯一LeaseRef
    保存signed PrepareRequest(Meta, sequence, ExactLeases)
    启动并登记PrepareAsync，有限观察；Require后保存prepared
    启动并登记armAcquisition(prepared, ct)，有限观察
    保存signed ArmRequest(Meta, prepared.OperationId, triggerId, mode, LeaseSnapshotHash)
    在启动Arm前保存executionId = armRequest.Meta.OperationId
    启动并登记ArmAsync，有限观察；Require后保存armed
    SoftwareStep：
        逐step按PatternHash取得唯一FrozenLease
        保存signed DisplayStepRequest(Meta, armed.OperationId, ordinal, hash, leaseId/version)
        启动并登记DisplayStepAsync，有限观察；Require
        启动并登记acceptActual(actual, ct)，有限观察
    Hardware：
        保存signed HardwareSequenceRequest(Meta, armed.OperationId, LeaseSnapshotHash)
        保留ExecuteHardwareSequenceAsync原enumerator，逐MoveNext启动登记/有限观察
        StepActual启动并登记acceptActual；LogicalEnd非Completed记业务失败
        正常/异常退出均按上述串行规则登记enumerator.DisposeAsync原Task并独立有限观察
        LogicalEnd/流结束不当作ResourcesReleased
catch 业务异常:
    捕获原ExceptionDispatchInfo到businessError
finally:
    try:
        若有executionId：构造或复用原signed StopRequest，登记StopAndDrainAsync
        用独立Stop份额有限观察；失败/未知只记录，不认定执行归还
    catch 清理异常: 记录清理失败
    finally:
        try:
            构造或复用原signed ShutdownRequest，登记ShutdownAsync
            独立Close份额有限观察；只有实际回执可作为closeEvidence
            确认排空后按§9.4.1 Query/Release，均登记原Task并有限观察
        catch 清理异常: 记录清理失败
        finally:
            try:
                登记GetRetentionUsageAsync；独立usage份额有限观察
                只有成功回执作为usageEvidence；异常/超时不补零
            catch 清理异常: 记录清理失败
            finally:
                try:
                    满足全部退槽前置才尝试Dispose并退槽
                catch 清理异常: 记录清理失败
                finally:
                    若尚未确认退槽/移交：尝试移交(独立移交份额)
                    移交任一失败/未确认：记录错误，原槽保持RecoveryHeld
finally后：businessError若存在按原栈重抛；否则报告有界cleanup结果与Owner状态
```

artifacts每PatternId恰一个且Content完整、hash已按Core规范化；同尺寸/格式按内容hash去重上传，ExactLeases无重复，不能因两个PatternId同像素而产生两个冲突slot。最末SoftwareStep记录LogicalCompleted并启动同execution cleanup；finally的重复Stop幂等继续，不产生新execution。任一Open/Upload/Prepare/Arm/step/hardware调用即使无回执，其原身份/Task也随槽保留。方法不是重试循环；恢复同命令只复用signed request，不再调用Meta生成新key。

查询使用 `session.QueryOperationAsync(new OperationQueryRequest(originalId, finiteDeadline), queryCt)`、`session.GetEventsAsync(new EventQuery(originalId,-1,32,finiteDeadline),queryCt)`（32仅合成Host且<=MaxEventsPerOperation），都按槽登记/有限观察。Pending/Unknown转原恢复Owner，下一次观察须新的有限deadline和剩余槽容量，不无期限await。接纳前取消且Open未发生也不能从异常推断Closed；Stop/Shutdown/usage失败不跳过移交，仍持有全部原请求和未确认Task。

### 9.4 Slice-2 托管生成/观察/Advice Host 模板

参数为附录B公开类型，三个adapter显式注入；测试Host使用Synthetic，生产Host组合已批准公开映射。沿§9.3同一存活槽/登记/有限观察/错误规则，未编译/运行，不实现HALCON或其它模块。Host接收generation/observation/recommendation及三个独立OperationId，cleanupBudgetNs与独立wall阶段预算；不能借推荐candidate身份覆盖生成operation。

```text
factory前预留存活槽和全部业务/Close/Query/Release/usage/Dispose/移交Task额度
session = StructuredLightVisionSession.Create(generator, observations, evaluations, clock, adviceClock, limits)
立即把session强绑定到槽                       // 完成后才进try
businessError = null; closeEvidence = null; usageEvidence = null
try:
    保存generation原OperationId/hash/完整请求，登记GenerateAsync(generation, ct)原Task
    有限观察；Generated才继续，其它保留实际结果并停止后续准入
    保存observation原OperationId/hash/请求，登记ObserveAsync(observation, ct)原Task
    有限观察；Observed才继续
    保存recommendation原OperationId/hash/请求，登记RecommendAsync(recommendation, ct)原Task
    有限观察；Advice仅离线结果，不批准/写回生产Profile
catch 业务异常:
    捕获原ExceptionDispatchInfo到businessError
finally:
    try:
        登记CloseAsync(new VisionCloseRequest(cleanupBudgetNs, "SL.HostClose"), 独立cleanup token)
        独立Close份额有限观察；成功回执才给closeEvidence
        Close失败/Unknown不使用空UnresolvedOperationIds当无资源
        确认排空后按§9.4.1 Query/Release，均登记原Task/有限观察
    catch 清理异常: 记录清理失败
    finally:
        try:
            登记GetRetentionUsageAsync(独立cleanup token)原Task，有限观察
            成功回执给usageEvidence；异常/超时不补零
        catch 清理异常: 记录清理失败
        finally:
            try:
                满足§9.3全部退槽前置及原session墓碑查询Owner保留条件，才尝试Dispose并退槽
            catch 清理异常: 记录清理失败
            finally:
                未确认退槽/移交则尝试全量移交，独立有限预算，不沿业务ct
                Close/usage/Dispose/移交抛错、卡住、拒绝或未确认：原槽持续持有全部身份/Task/额度
finally后：业务异常原栈重抛；cleanup错误独立保留；没有业务异常才报告清理失败
```

observation由宿主以generated manifest/实际完整binding建立；预传输入不匹配明确Rejected，不替换其hash继续。单独生成Host只做Generate+Query+Close，不需要观察/推荐实测；未用端口提供Rejected且Confirmed/Released的托管NoCapability，不动态加载真实模块。Query用 `session.QueryAsync(new VisionQueryRequest(originalId,finiteDeadline), queryCt)`，原Task也登记，晚到结果只能按原id/hash恢复，不能新id重复Generate。Close有有限BudgetNs；Task完成而native未停止仍Held，继续保留模型/输入、所有已提交身份及原Close/usage/Dispose/移交Task。宿主消费外部calibration资格，不能补“可用”标志骗过观察。正常生成成功后仍有结果payload也不得直接Dispose；按§9.4.1显式释放或确认全量接收，原session墓碑查询Owner没有确认前存活槽不退出。

### 9.4.1 有限 Query→Release→Close Host 调用（Slice-1/2）

以下补充已有Host中输出消费完成后的释放，不替代Stop/Drain，模板未编译/运行。所有deadline已由clock构造；不进行无限轮询。Projection按 `QueryOperationAsync(new OperationQueryRequest(originalId,deadline),ct)` 查询，Found/Snapshot.Phase=Terminal/DrainConfirmed/ResourcesReleased时，调用 `ReleaseOperationAsync(new RetentionReleaseRequest(originalId,snapshot.RequestSha256,snapshot.StateVersion,deadline),ct)`；Released直接读墓碑，Busy或Unavailable保持Owner，不新operation重发。Vision同样用 `QueryAsync(new VisionQueryRequest(originalId,deadline),ct)`，满足Terminal/实际归还条件后 `ReleaseResultAsync(new RetentionReleaseRequest(originalId,snapshot.RequestHash,snapshot.StateVersion,deadline),ct)`。两个Release方法在调用方判断后仍重验CAS/依赖，查询和释放之间可能有竞争，不能信查询代替原子判定。

§9.3/9.4 Host保留所有已提交id的有界列表（包括未收到接纳回执者；count/bytes计宿主槽额度，同时核模块Policy准入/cleanup预留）。输出消费完后按原id Query/Release，不以Close成功删记录：Projection先Shutdown真实归还所有slot，然后依赖逆序压缩step/子命令、父execution/Prepare/Upload/Shutdown回执；lease尚活跃或父record仍依赖则Busy，先ReleaseLease/停止/真实排空。Vision先等Observe/Evaluate归还再压缩它们与Generate结果。所有Release返回Released/AlreadyReleased才清对应pending状态，原身份/hash、请求及原Task条目在整个槽生命周期内仍保留用于移交/对账；失败/未知保留原session/id恢复Owner，不能Dispose后丢入口。若需Replay则保留完整结果到期限，expired仍可Query，但不得突破有限容量自动保存到第二无界Host缓存。Dispose前GetRetentionUsage的原Task登记并独立有限观察，明确PayloadRecords/Bytes为0且满足§9.3其余前置；全量移交则由接收者继续持有，不由原Owner随后Dispose。原幂等墓碑留在ledger/原session查询Owner。重复Close是固定小回执，不注册更多identity。

Host移交沿§9.3的全槽闭包adoptRecovery：整个session的活跃Owner、所有原请求/id/Task、已保留结果/输入、错误及额度都接收，包括Close已Confirmed但PayloadRecords>0或DisposeTask未确认的情况；UnresolvedOperationIds只是回执中的待核子集，空数组不意味着全部payload/identity已释放。恢复服务从原session Query/Release并观察原Task，不重新创建同nonce任务。接收者确认前原进程存活表持续持有槽，移交原Task及其晚到确认也按原offer对账；不能让方法抛错/窗口关闭丢失引用或产生双写Owner。payload为0的Projection墓碑属于ledger，ledger查询Owner持续保留；Vision的墓碑/命名空间随原session恢复Owner保留，Disposed原session拒绝任何新Generate/Observe/Recommend调用，不把原identity交新scope执行。

### 9.5 Slice-3 独立WPF Host 模板

测试Host在固定1920×1080 viewport中创建真实WPF窗口，扣除边框/taskbar，不改显示设置；注入附录D的Host，不引用产品Shell/数据库。以下是**可实施的宿主语义模板，未编译/未运行实窗**；宿主根槽、调用网关、Dispatcher登记和全量接收闭包是本地责任，不增加模块或恢复服务公开API。输入为明确的Host组装闭包及其依赖、控件options、三语culture、ViewCloseRequest的预算/原因、有限业务/cleanup wall预算和全槽adoptRecovery闭包。Host组装没有本模块factory API，使用宿主已有依赖组合产生IStructuredLightViewHost；不猜厂商构造器。

**WPF动作的实现定义：**

- 沿§9.3进程生命周期强引用表，**任何Host/view factory或Bind前**checked预留有界根槽。槽持有Host组装依赖、原Host、view、viewSession（未返回时可空）、所有原Task/DispatcherOperation、UiCommand及CommandId/嵌套OperationId、DisplayRequestId/LeaseId、SubscriptionId/订阅对象/sink和有界输入/错误。MaxLiveOwners、每槽Task/身份/metadata/显示bytes/事件队列总额度在启动前为有限正值；Options.Retention/MaxThumbnailBytes同时适用。业务份额耗尽停止本view新命令/显示/订阅，cleanup预留不被占用；无槽时factory/Bind/设备调用均为0。不能仅由窗口、方法局部变量或异常栈持有。单次组装和Bind同步有限、没有设备/订阅/Acquire副作用，禁止同步等待Dispatcher或在Bind内部阻塞I/O。
- 外层try覆盖组装、控件创建和Bind。每个同步factory结果在执行该闭包内立即写入已预留根槽再交付caller；失败若不能确认无Owner，保持ConstructionUnknown，不重建。view在目标Dispatcher上创建（`new StructuredLightView()`），强持view后才Bind。Bind保持D签名 `view.Bind(hostGateway, options)`；返回时在同一Dispatcher委托内先把viewSession和ViewSessionId写入根槽，再让投递Task完成。因此caller等待超时或交付异常也不丢晚到session。未返回/抛错的Bind必须按D.2局部原子回滚规则无外部副作用；未确认原BindTask结束则保持BindUnknown，不能靠再Bind取session或猜ViewSessionId。
- `Dispatcher登记`：先预留条目，使用`view.Dispatcher.InvokeAsync(Action)`或已知目标Dispatcher同等异步投递，记录原DispatcherOperation及其Task；不使用Invoke/Wait/Result。委托执行前核根槽Closing/原revision，关闭后只跳过尚未运行的业务投影，已运行者仍保留。委托只做有界创建/Bind/取得异步句柄及登记：Apply/UpdateCulture/Close/Dispose的ValueTask在委托中仅一次AsTask，**原Task立即写根槽**，不在Dispatcher内await后再登记。外层有限观察投递Task后观察已登记原Task；取消/WaitExpired不代表委托没运行、session没建立或lease已归还。Dispatcher已关闭/无法投递时记NotStarted/Unknown，原根仍持有view/Host/Task；不得为完成清理重开隐藏窗口。工厂/Bind同步卡死是实现违约，wall观察返回失败仍强持原委托/依赖，不能用Task包装宣称已结束。
- `Host登记网关`实现的就是D中IStructuredLightViewHost，作为Bind参数；不改变业务hash/判定或公开类型。每次转发前按§9.3预留并保存完整有界原请求、CommandId/嵌套OperationId或RequestId/SubscriptionId，然后调用**同名现有方法**，一次AsTask并强持原Task，再将其ValueTask结果交给view。包括GetSnapshotAsync、所有UiCommand动作、SubscribeEventsAsync、AcquireDisplayAsync、QueryDisplayAsync、ReleaseDisplayAsync、QueryCommandAsync、ReleaseCommandAsync、ResolveTextAsync、ClosePreviewAsync和GetRetentionUsageAsync；不会因入口异常/未收到回执而丢登记。正常或晚到返回的subscription、DisplayLease、payload/bytes都先归原根，再按当前Owner决定展示或恢复；late capture只登记，不隐式启动新的设备预览/Acquire。接收者确认切换后晚到回执写同一共享槽，不写已关闭Dispatcher。
- 订阅按原`host.SubscribeEventsAsync(subscriptionRequest, sink, ct)`登记；sink的OnEventsAsync只做有界入队和Dispatcher投影，原回调Task/投递Task也计槽额度。返回前关闭或订阅回执丢失时原SubscribeTask及SubscriptionId仍持有，晚到订阅写根槽。已经取得subscription用`subscription.GetStateAsync(cleanupCt)`确认Closed/Confirmed/Released；`subscription.DisposeAsync()`如需停止，只调用一次并登记原Task，随后仍核GetState的真实状态。Closed事件/队列空/DisposeTask完成都不替代回调实际归还。
- 显示先保存`DisplayRequest.RequestId`并登记`host.AcquireDisplayAsync(request, ct)`。AcquireTask未知或caller未收到lease只按原`host.QueryDisplayAsync(new DisplayQueryRequest(originalRequestId, finiteDeadline), cleanupCt)`对账，不新RequestId分配。关闭/revision变更后晚到lease不得再Apply：先强持其LeaseId/bytes，再登记一次`host.ReleaseDisplayAsync(new DisplayReleaseRequest(lease.LeaseId, finiteDeadline), cleanupCt)`；原ReleaseTask未知时只观察并QueryDisplay，不再Release同lease。实际Released回执且QueryDisplay资源Released/墓碑才确认归还；Found/Held、NotFound/Unavailable或查询失败均保留原RequestId、lease和bytes额度。late receipt/recovery动作同样有独立有限观察，不发无人登记的fire-and-forget；本次cleanup已到期则只登记原回执/待释放标记交原根恢复。
- `Close一次`：进入finally先将根槽Closing=true，拒绝本view新的业务命令/显示/订阅及展示旧图，保留cleanup/查询入口。已取得session才在Dispatcher委托内登记`viewSession.CloseAsync(closeRequest with { ViewSessionId = viewSession.ViewSessionId }, cleanupCt)`原Task；PreviewExecutionOperationId仅填本view原预览身份。网关同时持有内部`host.ClosePreviewAsync(sameRequest, cleanupCt)`原Task，按同ViewSessionId/原请求缓存该调用；两层原Task都保留。若原Close已启动而异常/卡住，无第二次Close/ClosePreview、无新request重试；仅观察原Task和原operation/显示/订阅对账。未交付Bind时本次Close记NotStarted；仍pending的Bind/DispatcherTask移交全槽，晚到session先捕获后由唯一Owner在新的有限恢复预算内**首次**Close，不能在未知Bind时补一个SessionId。
- cleanup沿§9.3独立token、各阶段有限wall份额及总deadline，分开Close、显示/订阅对账、结果Query/Release、usage、Dispose、移交；不沿已取消业务ct。Close/GetUsage/Dispose只首次启动一次，反复观察复用原Task，不能因超时再次调用。每阶段无剩余预算记NotStarted并保持Owner，仍进入后续finally。业务异常先保存ExceptionDispatchInfo，cleanup异常/拒绝/期限单独保留到有界metadata；cleanup失败不覆盖业务错误，也不因Dispose成功清掉错误。
- `退槽条件`：Bind/factory已确定结束、Close明确Confirmed/Released且三个Unresolved集合均空、所有显示确实Released、所有订阅GetState.Closed且Confirmed/Released、全部业务/回调/投递/cleanup原Task结束、GetUsage明确PayloadRecords=0/PayloadBytes=0、无未接收cleanup错误，并确认原scope墓碑的Host查询Owner继续存活。满足后才登记`viewSession.DisposeAsync()`原Task并独立有限观察；Dispose未确认不可退槽。D的Host没有IAsyncDisposable声明，不虚构host.DisposeAsync；本view清理不销毁外部生产session。成功退的是重资源/工作Owner引用；原Host的有界墓碑查询Owner仍按C.5保留。
- `全量移交`沿§9.3同一OwnerTransferId：adoptRecovery闭包接收根槽全部Host/view/session、未交付Bind/DispatcherTask、所有CommandId/DisplayRequestId/订阅/原请求/原Task、显示bytes、错误与额度。接收者先有界预留并强持，再确认唯一写入Owner切换；未确认前原根持续持有并停止新写入，拒绝/异常/timeout不退根，晚到确认只提交同offer一次。ViewCloseReply.RecoveryOwnerAccepted仅是内部回执，不能代替这些原Task/未交付session/显示Owner的全量接收确认。接收者不并发重发原Close/GetUsage/Dispose或重Bind；恢复查询可用新有限deadline、仍计原槽剩余额度。Dispatcher不可用时恢复只对原Host资源对账，不向已关闭view投影；未结束的UI Task仍保留，不能为关窗口强行释放。

下列host调用均指登记网关转发到同一个原Host，不能绕过网关；subscription对象同样用本地登记代理转发其现有GetStateAsync/DisposeAsync，所有原Task先保留。晚到捕获采用每个原调用一个预留的有限完成路径：等待原Task的同一结果，先在根槽锁内登记session/lease/subscription/payload，再交付结果；捕获/交付路径自身Task也计额度，原Task仍是底层调用Task，不能用这个wrapper覆盖它。网关输出前已持有结果，即使view调用方抛错或失去await也不丢Owner；原任务永久pending则有限观察返回、完成路径仍随原根保留，没有重复轮询/重订阅。sink入口每次先预留回调/投递条目，额度不足返回明确失败以沿D.2关闭该展示订阅，保留原订阅/未结束回调，不伪造Closed；持续展示超出有限Task历史额度须可见停止准入，不自动淘汰未确认条目。Close内的首次显示归还/订阅停止也通过相同网关/代理条目去重，与finally后续观察复用原Task，不并发Dispose。每个显示/订阅/命令清理失败独立记录并继续下一个有剩余预算的条目，未知对象/回执统一留根。

Host组装闭包限纯托管依赖组合：在已预留根条目中用一次本地Task.Run执行并登记原组装Task，闭包返回前强写Host，等待取消不取消晚到捕获；不把厂商阻塞/native/设备调用放进去，也不将Task.Run当作强停。view创建/Bind使用已知目标Dispatcher投递，不能放Task.Run规避WPF线程归属。factory/Bind/GetSnapshot/Apply/UpdateCulture的观察为Faulted/Cancelled/WaitExpired或未交付时立即停止后续业务，按原业务异常或有限等待异常进入finally，不把它们当成功继续读取空session。Bind已确认抛错才按局部原子性确认无外部动作；仍pending只能BindUnknown。本轮实例正常/异常步骤都使用§9.3相同有限观察定义，不含无期限await。

```text
先预留进程根槽(Host依赖、factory/Bind/Dispatcher/原请求Task及全部cleanup额度)
businessError = null; closeEvidence = null; usageEvidence = null
try:
    有界组装原Host并在同闭包中强写根槽，有限观察原组装Task后建立同D接口登记网关
    Dispatcher登记：new StructuredLightView()，立即强写根槽；有限观察原创建投递Task
    前步成功才Dispatcher登记view.Bind(hostGateway, options)，返回即强写viewSession/ViewSessionId
    有限观察原Bind投递Task；任一步未确认不继续下一步/不再次创建或Bind
    登记hostGateway.GetSnapshotAsync(ct)原Task，有限观察snapshot
    Dispatcher登记viewSession.ApplySnapshotAsync(snapshot, ct)原Task，有限观察
    Dispatcher登记viewSession.UpdateCultureAsync(cultureName, ct)原Task，有限观察
    后续UiCommand/显示/订阅均通过上述登记网关，以原身份恢复，业务各有有限wall期限
catch 业务异常:
    保存原ExceptionDispatchInfo到businessError
finally:
    根槽Closing = true
    try:
        已捕获viewSession才Close一次(独立Close份额)
        未交付Bind/pending Close记Unknown/NotStarted，不补空成功回执
        原Close回执确认才赋closeEvidence
    catch 清理异常: 有界记录cleanup错误
    finally:
        try:
            原DisplayRequestId QueryDisplay，已知lease按一次ReleaseDisplay规则归还
            取得/晚到subscription按一次Dispose及GetState确认回调Released/Closed
            逐CommandId QueryCommand，资源确实归还后ReleaseCommand；均登记原Task/有限观察
        catch 清理异常: 有界记录cleanup错误
        finally:
            try:
                登记一次hostGateway.GetRetentionUsageAsync(cleanupCt)原Task，独立有限观察
                成功回执才赋usageEvidence；异常/超时不补零
            catch 清理异常: 有界记录cleanup错误
            finally:
                try:
                    全部退槽前置满足才Dispatcher登记一次viewSession.DisposeAsync原Task
                    独立有限观察，明确成功才退重资源槽
                catch 清理异常: 有界记录cleanup错误
                finally:
                    尚未确认退槽则尝试全量移交(独立有限份额)
                    拒绝/异常/超时/回执丢失保持RecoveryHeld及全部原Owner/Task/额度
finally后：先原栈重抛businessError；没有业务异常才报告cleanup失败/Owner状态
```

Command结果消费后登记 `host.QueryCommandAsync(new UiCommandQueryRequest(originalCommandId,finiteDeadline),cleanupCt)`；Found且原Reply关联资源全部归还，再登记 `host.ReleaseCommandAsync(new RetentionReleaseRequest(originalCommandId,q.Reply.RequestHash,q.Reply.StateVersion,finiteDeadline),cleanupCt)`，Host重验CAS。Released只读原墓碑，Busy/Unavailable保持Owner，不新CommandId。仅清pending标记，所有原身份/Task继续随根保留至确认退槽/全量移交。显示/订阅先实际归还，再压缩相关命令结果；Close成功/RecoveryOwnerAccepted/窗口消失都不等于完整payload与原Task结束。若尚有未知Close或UI Task，GetUsage即使双零也不能Dispose。

同一Host按zh-CN/zh-TW/en-US验证参数/Unknown/恢复，不隐藏停止；NoUiHost通过C/B并行另一实例，view异常/切语/关闭不影响它。D.Host动作均有匹配UiPayload，不从global ViewModel补字段。实际DevExpress布局/API沿§10/16既有证据，真实WPF/DPI/UIA/主题/keyboard/语言长度尚未运行；以上内部接线与Owner路径是本Slice-3本轮文档要求，不能将它们留成“待真实运行才决定”的缺口。§12的10/120/180s wall期限保持，虚拟clock只控制逻辑时间。

## 10. 可选 WPF UI / PageContract SL-UI-01

### 10.1 嵌入契约和任务流

`StructuredLightView : UserControl`，namespace见binding；`Bind(IStructuredLightViewHost host, StructuredLightViewOptions options)`返回`IStructuredLightViewSession`。Host全部方法/结果/订阅/关闭/显示租约声明在D，映射同一§3/§7 API，不直接连接SDK。UI命令使用D的UiCommand，含CommandId、SelectionRevision、ExpectedSequenceHash、AuthorityScope、Kind与完整UiPayload判别联合；宿主重新校验权限/CAS，view禁用按钮不算授权。

Options=CultureName、ThemeName、ReadOnly、MaxVisibleEvents、MaxThumbnailBytes、MaxChartPoints、RefreshIntervalMs、QueryBudgetNs、CleanupBudgetNs；全部预算正值由宿主提供。ViewSession.UpdateCultureAsync(culture,ct)、ApplySnapshotAsync(snapshot,ct)、CloseAsync(request,ct)、DisposeAsync；language/theme仅当前view scope，不改Application全局资源、不另放语言切换入口。宿主负责提供三语资源和受控图像/视口服务；view dispose只解订阅/释放显示资源，设备恢复仍由宿主Owner负责。

角色：操作员查看已批准序列/实际/错误并停止；工艺人员离线编辑草稿、比较候选；维护人员获限时scope才预览/自检/恢复。唯一主动作随状态为“验证”“准备”“预览”“停止”或“查询状态”，危险输出前显示设备/序列/期限。停止始终可见，Recover仅条件满足才可用，不提供“忽略错误继续”。取消/编辑均不能覆盖已执行事实。

### 10.2 1920×1080构图和控件

只在固定1920×1080验证viewport测试；扣除OS任务栏、边框/标题/状态栏后记录实际client与DPI，内部布局按client计算，不改用户显示设置、不跑其它分辨率矩阵。顶部单行命令/设备身份≤client高8%；底部状态/恢复区≤8%；中部影像宽≥55%，左序列约20%，右属性约25%；下方可调整时序/实际表约中部高25%。影像最小宽不得被属性面板挤掉；可折叠高级参数，不隐藏关键Stop/Unknown状态。

- DockLayoutManager + LayoutGroup/LayoutPanel安排主图、序列表、属性、下方时序；布局按view schema/version隔离保存，损坏时回默认，不改数值/权限。
- 序列/Actual用GridControl + TableView，显式ItemsSource/列、固定ordinal/角色/hash、启用虚拟化和AllowPerPixelScrolling；请求/实际时间及读回等级并列，不只用绿色灯。大量事件只显示分页/有限窗口，原ledger事实仍完整可查。
- 参数用PropertyGridControl.SelectedObject指向草稿投影，显式属性定义/类别/单位/只读规则；搜索只过滤显示，不删除参数。生产执行中只读；高级诊断/persistence渐进展示。
- ChartControl + XYDiagram2D按step画hold/settle/exposure/readback延迟，Series绑定typed数据；不得每像素/帧都造视觉对象。选择step同步图案缩略图、Actual、图表游标及错误路径；多选仅离线比较，不批量输出设备。
- 命令优先ToolBarControl/StatusBarControl；BarManager属官方legacy，不为简单嵌入面板引入。BarItem.SuperTip直接提供上下文；普通SimpleButton.ToolTip使用SuperTipControl包含SuperTip，不能错误套WinForms API。非关键参数解释可FlyoutControl，PlacementTarget绑定按钮；关键Stop/恢复不藏Flyout。
- 树状来源确有层级时才用GridControl.View=TreeListView、KeyFieldName/ParentFieldName、TreeDerivationMode=Selfreference；普通步序保持TableView。主影像按§10.4消费D已有DisplayLease的Pbgra32显示副本；宿主可在自身显示服务复用公开视口完成转图。本控件不建立第二套HALCON显示器或图像算法。

延迟/温度等数值带单位/来源，nullable显示“未观测”。Simulation使用持久文字标签和纹理，不能只靠颜色；图层标题显示phase/correspondence的Owner、attempt、hash和是否Stale。同一主题使用宿主已有字体/图标/间距；错误具有文字+图标、焦点框、图例；减少装饰动画，窗口resize不触发设备动作。视觉品质和操作可用性分别验收。

### 10.3 交互、语言和失败恢复

Tab顺序：序列 → 主图工具 → 属性 → 主命令 → Stop → 恢复/诊断。方向键在序列表导航，Enter只执行当前安全主命令；Space不隐式发光；Esc关闭非关键Flyout或取消草稿编辑，不能当已停止；Stop有显式Alt+S且焦点不在文本编辑也可调用。输出命令只接受一个未完成请求，双击不生成第二operation。

参数修改增加DraftRevision，旧计划/诊断/建议标Stale、禁止Prepare；重新Validate/Generate建立新hash。页面切换/失焦只对限时预览请求停止，不取消后台生产Owner的有效事务；预览期限/互锁在Host执行，UI计时仅展示。关闭时显示“正在停止/等待排空”，未知时呈现operationId和“查询状态”，不能直接显示“已停止”。

投影更新用有界batch并按RefreshIntervalMs合并纯进度；Actual/逻辑结束/故障/排空终态不得丢弃，先落ledger再投影。选择变化或新revision后迟到诊断丢弃其显示更新并保留原记录，不覆盖当前图。subscription Dispose后不再投递Dispatcher；显示副本按MaxThumbnailBytes/MaxChartPoints/MaxVisibleEvents预算，超限明确分页/抽样标识，原事实不降采样。

| Key | zh-CN | zh-TW | en-US |
|---|---|---|---|
| SL.Stop | 停止投影 | 停止投影 | Stop projection |
| SL.WaitDrain | 正在等待设备排空 | 正在等待裝置排空 | Waiting for device drain |
| SL.Unknown | 设备状态未确认。查询原操作后再恢复。 | 裝置狀態未確認。查詢原操作後再復原。 | Device state is unconfirmed. Query the original operation before recovery. |
| SL.Blackout | 黑场未确认，投影已锁定。检查设备反馈。 | 黑場未確認，投影已鎖定。檢查裝置回饋。 | Blackout is unconfirmed. Projection is locked. Check device feedback. |
| SL.Stale | 参数已变更。重新生成并验证序列。 | 參數已變更。重新產生並驗證序列。 | Parameters changed. Generate and validate the sequence again. |
| SL.NotObserved | 未观测 | 未觀測 | Not observed |
| SL.Simulation | 模拟结果 | 模擬結果 | Simulation result |

其余所有标题/参数/单位说明/错误/提示/权限/恢复均为资源键，沿同一术语表扩展，不能只翻按钮。数字显示按culture，传输/hash始终culture-invariant；更换语言不改输入/序列/操作身份。WPF实施时验证三语最长文本、UIA name/role/状态、键盘焦点、DPI和固定viewport实际截断/遮挡；本轮只冻结要求，未执行实窗。

### 10.4 完整显示挂接、编辑与三语资源实施补充

本节使用D既有DisplayRequest/DisplayLease/IStructuredLightViewHost，不新增viewport、native句柄或保存服务API；D.1/D.2既有命令/回复保持，编辑源的必要附加接口在§10.4.1冻结。默认嵌入组合固定为DockLayoutManager四区，左GridControl/TableView序列、中部可平移缩放的WPF Image、右PropertyGridControl草稿、下方Actual GridControl和ChartControl/XYDiagram2D；顶ToolBarControl的验证/准备/预览与始终可见停止，底StatusBarControl身份/状态/唯一恢复动作。Tooltips沿§10.2公开SuperTip组合。25.2.3本机程序集直接引用；本轮环境仍无dxdocs工具，复用§16.4已核25.2官方页面，不猜额外控件属性或换NuGet版本。layout/control声明和DataContext均属于本UI模块，不能要求宿主先开某产品窗口初始化。

**显示默认路径。** Host以原DisplayRequest.Asset精确取得原图案/诊断/证据，按自己的已有显示服务限额转换为D定义的premultiplied BGRA32；alpha=0的invalid/missing区域透明，phase/float诊断的显示范围/LUT由原显示Profile提供，无Profile不自动min/max重标生产图层。生成byte图案按原0..255灰度复制B=G=R、A=255；软件Preview显示图案不等于向设备发光。Downsampled=true只展示并带持久文字，不能作为新的测量源/导出图案；原数字仍由生产Owner查询。

收到Acquired Lease后先存入§9.5根，再核request/SelectionRevision/SourceAsset/尺寸/stride/长度/有效期与总额度。Dispatcher只创建`WriteableBitmap(width,height,96,96,PixelFormats.Pbgra32,null)`并`WritePixels(Int32Rect(0,0,width,height),独立有界显示buffer,stride,0)`，绑定Image.Source；不要把premultiplied字节给PixelFormats.Bgra32，也不借read pointer造BitmapSource。图案模型/native和原帧lease不在ViewModel。Bitmap及转换buffer属于本view本地显示Owner，Host DisplayLease仍归原RequestId/LeaseId；不能因bitmap已copy就默认Host租约Released。

显示费用准入按B=checked(width*height*4)：同屏更换保守预约旧显示LUT/lease+bitmap 2*B_old与新lease+copy暂存+bitmap 3*B_new，合计不超过Options.MaxThumbnailBytes（Host还分别核自己的lease总额），计入§9.5根的实际持有输入/输出预算。首次只有3*B_new，reuse确无copy仍用此保守上界。不足时保持原图并显示限额原因，不释放仍被原Task借用的旧lease，不无限Acquire。请求MaxBytes取当前剩余/3且核正值；新显示Apply成功后才按原LeaseId首次Release旧lease，旧Release未知则保持Held费用并禁止超预算继续刷新。清空Image.Source/取消Dispatcher不等Host Release。关闭或stale/late lease按SL-UC04/RET04原查询与根路径归还，不画旧图，不新RequestId补丢回执。

图像布局用统一缩放与平移，Fit取min(clientWidth/displayWidth,clientHeight/displayHeight)保持纵横比；1:1为一个display pixel到一个DIP（不是相机计量1:1），wheel以鼠标位置为中心放缩，scale夹在[0.1,32]、无旋转/镜像，拖动只改本地TranslateTransform。滚轮不触发生成/设备命令，双击Fit，Ctrl+0 Fit、Ctrl+1 1:1，Esc只取消手势或草稿。cursor读图坐标由显示变换求逆，半开范围[0,W)×[0,H)、index=floor(row)*W+floor(column)；本地读到的是Pbgra32显示值，不能冒充phase/correspondence原值。Downsampled或拿不到原Asset栅格尺寸/映射时只显示“预览像素”，不通过比例猜源坐标；真实源像素值查询/ROI交互属于宿主视口/证据Owner，本模块不另建测量/ROI工具。Actual表/时序图保原ClockStamp/原单位，只有同boot/domain或C.4已核映射才在同时间轴比较；用原首tick为局部起点、BigInteger有理ns转有限显示double，Unknown窗口画带文字的缺测段，不用0延迟或一条绿线补齐。图表离线抽样仅显示，Actual/故障/终态保原ledger。选择step仍同步SourceAsset/Actual/图表游标，图层的Owner、attempt、单位、invalid、Stale一并显示。

### 10.4.1 草稿输入与完整命令的宿主构造扩展

D.ViewSnapshot只有ManagedPatternPlan，不能倒推出GenerationSpec/GenerationLimits/normalization等字段；D.UiCommand也不能由view猜权限、Meta、leases或trigger。下面是同UI程序集新增的拟实现公开接口，实际编辑型Host实现IStructuredLightViewInputs，view在Bind后通过显式的`host is IStructuredLightViewInputs`取得本scope源，不通过服务定位或隐藏窗口。只有展示的Host不实现扩展时仍可显示D快照并Query/Close，编辑/主动执行入口显示ReadOnly；完整试验台/3D维护嵌入Host须实现本扩展，不能以“缺端口所以永远只读”冒充其全部能力完成。

```csharp
namespace Asun.Modules.StructuredLight.Ui.Wpf;
public sealed record GenerationDraftSnapshot(
    long SnapshotRevision,
    Asun.Modules.StructuredLight.Vision.GenerationSpec? Spec,
    Asun.Modules.StructuredLight.Vision.GenerationLimits? GenerationLimits,
    Asun.Modules.StructuredLight.PlanningLimits PlanningLimits,
    System.Collections.Immutable.ImmutableArray<
        Asun.Modules.StructuredLight.Projection.ModuleIssue> Issues);
public sealed record ViewCommandIntent(
    System.Guid CommandId, UiCommandKind Kind, long ExpectedSnapshotRevision,
    string? ExpectedSequenceHash,
    Asun.Modules.StructuredLight.Vision.GenerationSpec? EditedGenerationSpec,
    Asun.Modules.StructuredLight.ManagedPatternPlan? EditedPlan,
    System.Guid? OriginalExecutionOperationId, long? PreviewBudgetNs);
public interface IStructuredLightViewInputs
{
    System.Threading.Tasks.ValueTask<GenerationDraftSnapshot> GetGenerationDraftAsync(
        Asun.Modules.StructuredLight.Projection.ClockStamp deadline,
        System.Threading.CancellationToken ct);
    System.Threading.Tasks.ValueTask<UiCommand> BuildCommandAsync(
        ViewCommandIntent intent,
        Asun.Modules.StructuredLight.Projection.ClockStamp deadline,
        System.Threading.CancellationToken ct);
}
```

本扩展仅值读取/构造，绝不Prepare/Arm/Upload/Generate/采集/查询设备或签资格；原D Host方法才执行。GetGenerationDraft与D.GetSnapshot分别读取时可能遇revision变化：必须相等才接纳显示可编辑源，不等标Stale并保旧值，使用下一显式刷新（有预算、无无界循环）重新取得；不能混两次快照拼接。GenerationDraftSnapshot.SnapshotRevision与同次D.GetSnapshot.Revision一致，Spec/GenerationLimits同时非null或同时null；null表示本scope未配置生成源，不能从HALCON默认填。PlanningLimits始终由Host显式注入，不能view选预算；Spec所有Profile/runtime/版本来源沿B原边界。GetGenerationDraft在Options.QueryBudgetNs/传入deadline小值内读取本scope冻结值，失败保原草稿/提示Query，不返回伪默认配置。

BuildCommand输入本地新CommandId（原Retention namespace）、Kind、已持有的原SnapshotRevision/hash与可选完整草稿，布局和生成定义Profile必须匹配§7.4。Intent规范身份固定域ASCII `ASUN-SL-UI-INTENT-1`加单NUL，再按ViewCommandIntent声明次序写全部字段；枚举/Guid/string/nullable/hash沿§3/C，EditedGenerationSpec按B.GenerationSpec完整字段，EditedPlan沿A完整metadata/Steps且Content只原SHA32bytes、不混入PlanningLimits，非null PreviewBudgetNs写int64LE。Build查询deadline不进意图hash，不以延长deadline改变原意图；有限相同意图回放不重新生成operation。Intent同id/完整值在Host有限构造索引内回原UiCommand；异值Conflict，新的CommandId才表示明确新意图。命令构造索引/原Task与规范预像计入原scope Options.Retention/§9.5，构造记录与D command同一个CommandId/槽，由Host登记Kind/IntentHash/完整UiCommand及原构造Task，不重复创建第二identity。IntentHash只供构造输入去重；D.UiReply.RequestHash/墓碑仍严格为原ASUN-SL-UI-CMD-2完整命令hash，不能把IntentHash写进去。每槽有Built与Executed两种独立状态：Built不等Applied、不阻首次执行；进入Executed前比较完整UiCommand规范hash，同id异命令Conflict，已执行按D原规则回原回复。构造/执行一起Release后保有界墓碑和IntentHash，Build同id不重分配内嵌operation，明确返回已释放的本地协议异常，由view查询原CommandId；一次单规范预像<=Options.Retention.MaxSingleReplyBytes且<=2MiB，先checked计长/全部string有界再copy，超限SL-RES拒绝，不开第二无界缓存；没有设备副作用的构造失败不冒称旧设备未知可重新执行。构造完成路径先将完整UiCommand（含内嵌operation/id/hash）写根再交view；caller期限到期、重入或未交付只观察原Task，不再分配内嵌operation。有限错误用SL-VAL/SL-CON/SL-RES抛本地参数/协议异常，保原ExceptionDispatchInfo；不把null当已构造成功。

Intent字段不得跨Kind暗中忽略：EditedGenerationSpec仅GenerateDraft可非null，EditedPlan仅ValidateDraft可非null，PreviewBudgetNs仅StartPreview可非null且必须为正；OriginalExecutionOperationId仅StopAndDrain/Shutdown/Recover可非null，并须匹配本scope原目标（StopAndDrain停自己的预览，Shutdown/Recover核同代session及其原未决操作）。其它字段不适用时必须null，未知Kind/多余字段先SL-VAL拒绝，不默默丢字段后执行。ExpectedSnapshotRevision必须>=1；清理原execution沿D即使当前选择已变仍可进行，不以新的选择hash拒绝关光。

每Kind构造唯一：ValidateDraft要求EditedPlan或原快照Draft完整，GenerationSpec=null，使用Host同PlanningLimits；GenerateDraft要求EditedGenerationSpec或Spec完整，用同GenerationLimits和新原GenerateId；Prepare核Validated且非Stale的本scope原ProjectionSequence、当前确切leases/版本、Profile/Runtime、Capability/generation、实际授权scope和总预算，组原PrepareRequest；StartPreview用同原PreparedOperationId/LeaseSnapshotHash/TriggerId/SoftwareStep与实际授权，PreviewBudgetNs显式为正且取Host批准Preview上限/lease剩余/父剩余的小值；StopAndDrain/Shutdown/Recover沿原scope已有execution/recovery身份，OriginalExecutionOperationId由根保存且必须属于本view，不能改成另一个生产execution；Observe/Recommend分别组B.4已确定的完整实际binding/资产/图层/ROI/评估资料和已批准有界候选、期限/费用。没有这些原输入时SL-VIS/SL-VAL拒绝，不制造新的影像/qualification或隐式拍照。每个内嵌CommandMeta均由Host按同scope真实clock/ledger/authority及C的完整hash创建，UiCommand.AuthorityScope与之相同；view只核Kind/Payload/Revision/hash和原任务关联，再调用对应D方法一次。Build不等授权，实际Host方法仍再次核权限/撤权/CAS/预算；UI未知结果沿原CommandId及内嵌id查询，不Build新意图代重试。

本地选行/图层/zoom只改变view的有限呈现generation和选中Asset，不增加Host ViewSnapshot/Selection.Revision或伪造新的CAS；DisplayRequest.SelectionRevision始终实际已持有snapshot的Revision，原Task捕获本地呈现generation，迟到结果还须generation匹配才可画。Host权威新Revision从GetSnapshot/事件到来后整体更新；本地DraftRevision用于编辑dirty/stale，提交intent的ExpectedSnapshotRevision仍原Host revision，成功执行后读取新的Host快照再允许下一命令。不能令“选行”自行改变全局当前设备/产品选择；生产execution开始后选图不取消它。原快照、草稿和Profile失效时保本地缓冲只读，重新读取显式源，不反向从生成像素猜原参数。

**编辑和权限。** PropertyGrid.SelectedObject绑定本地有限Draft编辑投影，永不指向已执行Plan/Actual对象。数值编辑先保culture文本缓冲，中间态如空串、负号、`0.`不更新原GenerationSpec；Enter/失焦明确提交时用当前culture的严格数值解析，拒绝分组分隔、NaN/Inf/非整数计数字段/非法SemVer及超界，经同Core/Vision Validate后一次替换DraftRevision。失败保缓冲/错误路径并禁止Generate/Prepare，Esc回原值，不用局部parse失败默认0。相移/Gray路线/normalization/Orientation改变一次就把plan/observation/advice Stale；生成期间编辑只改新草稿，原operation参数保持原deep copy。

参数面板先显尺寸/方向/路线/stripe与Profile/实际源，再折叠SingleStripe、Persistence、时序guards、资源限额；不显示仅影响其它路线的可编辑single宽，改route后按完整Spec重验。显示Profile批准的推荐值及来源，缺生产参数时显示“未配置”，不从HALCON默认1024/768/stripe值填现场设置。ReadOnly禁止Generate/Prepare/Preview/Recover/参数提交及启动新的Observe/Recommend/ValidateDraft；只显示已存在Observation/Advice/快照并查询原操作，不把“查看诊断”解释为发新Observe；Stop自己的预览与关闭内部cleanup不因只读或撤权失效。硬件启动/跨设备触发由Host和C.3资格再核，UI按钮不构成授权。Tab/Alt+S和Enter安全主命令规则沿§10.3，文本编辑Enter只提交字段、不得顺带发光；时间/读回Unknown不显示绿色成功。

**完整固定目录。** 下表是本UI程序集随包的基线资源，Host ResolveText可覆写为已登记扩展语言/术语；资源键不写入算法hash。枚举到key的映射在本页固定，无动态enum.ToString直显；ID/hash/原设备错误码只在可复制的技术详情区保留，正文只显示短句和下一步。中文长度不同不得裁掉停止/未知/恢复按钮；英文最长错误进两行状态区或SuperTip，最多状态区8%client高，详细原因进下方诊断，不用弹窗阻塞关光。复用§10.3和D.2已有Stop/Unknown/Blackout/Stale/NotObserved/Simulation/Busy/Released/缺资源后备，本表不复制它们。

| Key/消费位置 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| SL.Title | 结构光投影 | 結構光投影 | Structured light projection |
| SL.Sequence | 图案序列 | 圖案序列 | Pattern sequence |
| SL.Image | 图案与诊断 | 圖案與診斷 | Pattern and diagnostics |
| SL.Parameters | 参数 | 參數 | Parameters |
| SL.Timing | 曝光与读回 | 曝光與讀回 | Exposure and readback |
| SL.Actuals | 实际记录 | 實際紀錄 | Actual records |
| SL.Diagnostics | 诊断记录 | 診斷紀錄 | Diagnostic log |
| SL.Validate | 验证序列 | 驗證序列 | Validate sequence |
| SL.Generate | 生成图案 | 產生圖案 | Generate patterns |
| SL.Prepare | 准备投影 | 準備投影 | Prepare projection |
| SL.Preview | 限时预览 | 限時預覽 | Timed preview |
| SL.Query | 查询原操作 | 查詢原操作 | Query original operation |
| SL.Recover | 恢复连接 | 復原連線 | Recover connection |
| SL.Observe | 查看诊断 | 查看診斷 | View diagnostics |
| SL.Recommend | 比较候选 | 比較候選 | Compare candidates |
| SL.Shutdown | 关闭连接 | 關閉連線 | Close connection |
| SL.Advanced | 高级参数 | 進階參數 | Advanced parameters |
| SL.Fit | 适应窗口 | 符合視窗 | Fit to window |
| SL.OneToOne | 预览 1:1 | 預覽 1:1 | Preview 1:1 |
| SL.PreviewPixel | 预览像素 | 預覽像素 | Preview pixel |
| SL.Downsampled | 缩小预览 | 縮小預覽 | Reduced preview |
| SL.Unconfigured | 未配置 | 未設定 | Not configured |
| SL.ReadOnly | 只读 | 唯讀 | Read only |
| SL.Permission | 无操作权限。查询状态或联系维护人员。 | 無操作權限。查詢狀態或聯絡維護人員。 | No permission. Query status or contact maintenance. |
| SL.Param.Size | 投影尺寸（像素） | 投影尺寸（像素） | Projector size (pixels) |
| SL.Param.Orientation | 编码方向 | 編碼方向 | Encoding direction |
| SL.Param.Route | 图案类型 | 圖案類型 | Pattern type |
| SL.Param.Stripe | 最小条纹宽（像素） | 最小條紋寬（像素） | Minimum stripe width (pixels) |
| SL.Param.SingleStripe | 单条纹宽（像素） | 單條紋寬（像素） | Single stripe width (pixels) |
| SL.Param.Normalization | 亮度归一化 | 亮度正規化 | Intensity normalization |
| SL.Param.Persistence | 保留解码诊断 | 保留解碼診斷 | Retain decode diagnostics |
| SL.Param.Hold | 保持时间（ns） | 保持時間（ns） | Hold time (ns) |
| SL.Param.Settle | 稳定等待（ns） | 穩定等待（ns） | Settle time (ns) |
| SL.Param.Exposure | 曝光窗口（ns） | 曝光視窗（ns） | Exposure window (ns) |
| SL.Param.Guard | 保护时间（ns） | 保護時間（ns） | Guard time (ns) |
| SL.Param.Budget | 时间与资源限额 | 時間與資源限額 | Time and resource limits |
| SL.Param.Profile | 参数来源 | 參數來源 | Parameter source |
| SL.Param.Runtime | 运行版本 | 執行版本 | Runtime version |
| SL.Param.Calibration | 共同标定资产 | 共同標定資產 | Joint calibration asset |
| SL.Param.Generator | 生成器版本 | 產生器版本 | Generator version |
| SL.Role.Black / White | 黑场 / 白场 | 黑場 / 白場 | Black / White |
| SL.Role.Gray / GrayInverted | 灰码 / 反灰码 | 灰碼 / 反灰碼 | Gray code / Inverted Gray code |
| SL.Role.Phase / SingleStripe / Custom | 相移 / 单条纹 / 自定义 | 相移 / 單條紋 / 自訂 | Phase shift / Single stripe / Custom |
| SL.Direction.None / Vertical / Horizontal | 无方向 / 竖条纹（列） / 横条纹（行） | 無方向 / 直條紋（欄） / 橫條紋（列） | No axis / Vertical stripes (columns) / Horizontal stripes (rows) |
| SL.Route.Hybrid / GrayOnly / SingleStripe | 灰码与相移 / 仅灰码 / 单条纹组合 | 灰碼與相移 / 僅灰碼 / 單條紋組合 | Gray code and phase / Gray code only / Single stripe combination |
| SL.Normalization.Global / InvertedPattern | 黑白参考 / 正反图 | 黑白參考 / 正反圖 | Black and white references / Complementary patterns |
| SL.Model.ThreeD / Deflectometry | 三维重建图案 / 反射检测图案 | 三維重建圖案 / 反射檢測圖案 | 3D reconstruction patterns / Deflectometry patterns |
| SL.State.Closed / Opening / Ready / Uploading | 未连接 / 正在连接 / 就绪 / 正在上传 | 未連線 / 正在連線 / 就緒 / 正在上傳 | Disconnected / Connecting / Ready / Uploading |
| SL.State.Prepared / Armed / Displaying | 已准备 / 已武装 / 正在投影 | 已準備 / 已待觸發 / 正在投影 | Prepared / Armed / Projecting |
| SL.State.Cooling / Draining / Faulted / Unknown / Disposed | 正在冷却 / 正在排空 / 故障 / 状态未确认 / 连接已释放 | 正在冷卻 / 正在排空 / 故障 / 狀態未確認 / 連線已釋放 | Cooling / Draining / Fault / State unconfirmed / Connection released |
| SL.Outcome.Completed / Failed / Cancelled / TimedOut / Unknown | 已完成 / 失败 / 已取消 / 超时 / 结果未确认 | 已完成 / 失敗 / 已取消 / 逾時 / 結果未確認 | Completed / Failed / Cancelled / Timed out / Result unconfirmed |
| SL.Trust.None / CommandAccepted / DeviceReported / SensorConfirmed | 未观测 / 命令已接受 / 设备读回 / 传感器确认 | 未觀測 / 命令已接受 / 裝置讀回 / 感測器確認 | Not observed / Command accepted / Device readback / Sensor confirmed |
| SL.NotEvaluated | 未评估 | 未評估 | Not evaluated |
| SL.Rejected | 已拒绝 | 已拒絕 | Rejected |
| SL.ParameterError | 参数无效。修正标记项后重新验证。 | 參數無效。修正標記項後重新驗證。 | Invalid parameters. Correct marked fields and validate again. |
| SL.SourceMismatch | 图案或来源不符。重新取得完整原图组。 | 圖案或來源不符。重新取得完整原圖組。 | Pattern or source mismatch. Retrieve the complete original image set. |
| SL.Incomplete | 图像缺失或顺序不符。本次结果无效，查看原记录。 | 影像缺失或順序不符。本次結果無效，查看原紀錄。 | Images are missing or out of order. This result is invalid. Check the original record. |
| SL.Capacity | 资源不足。先查询并归还已完成操作。 | 資源不足。先查詢並歸還已完成操作。 | Insufficient resources. Query and release completed operations first. |
| SL.LayoutUnavailable | 生成布局未验证。选择已验证的参数版本。 | 產生布局未驗證。選擇已驗證的參數版本。 | Generation layout is unverified. Select a verified parameter version. |
| SL.DisplayUnavailable | 预览暂不可用。查询原显示请求。 | 預覽暫不可用。查詢原顯示要求。 | Preview unavailable. Query the original display request. |
| SL.Qualification | 资产资格未确认。查询原资格记录。 | 資產資格未確認。查詢原資格紀錄。 | Asset qualification is unconfirmed. Query the original qualification record. |
| SL.Cooling | 设备超过运行范围。停止投影并检查温度或功率。 | 裝置超出執行範圍。停止投影並檢查溫度或功率。 | Device is outside its operating range. Stop projection and check temperature or power. |
| SL.Version | 版本不匹配。使用原版本查询并恢复。 | 版本不符。使用原版本查詢並復原。 | Version mismatch. Query and recover with the original version. |
| SL.AdviceIncomplete | 比较缺少依据。补齐真值、参数或性能目标。 | 比較缺少依據。補齊真值、參數或效能目標。 | Comparison lacks evidence. Provide ground truth, parameters or performance targets. |
| SL.NonMeasurement | 仅预览，不用于量测 | 僅預覽，不用於量測 | Preview only; not for measurement |

同格斜线并列key各自独立资源，按所列顺序一一对应，不能把整格当单enum文本。所有其余计数/identity/Source字段标题从本模块字段名固定映射到上述类别及原术语：序号/步号/图案/hash/版本/原操作/设备/时钟/时间/源/单位/有效域/读回；三语依次为Ordinal/Step/Pattern/Hash/Version/Original operation/Device/Clock/Time/Source/Unit/Valid domain/Readback，繁中序號/步號/圖案/雜湊/版本/原操作/裝置/時鐘/時間/來源/單位/有效域/讀回。不可观测物理量沿SL.NotObserved；null Profile用SL.Unconfigured而非0。指标十个名称沿B.3固定键，显示名分别为误接受率/误拒绝率/相位平均绝对误差/相位均方根误差/相位最大误差/有效比例/P50/P95/P99/峰值资源；繁中誤接受率/誤拒絕率/相位平均絕對誤差/相位均方根誤差/相位最大誤差/有效比例/P50/P95/P99/峰值資源；英文False acceptance rate/False rejection rate/Mean absolute phase error/RMS phase error/Maximum phase error/Valid fraction/P50/P95/P99/Peak resources。单位rad/ns/bytes/px由原metric声明，mm从下游引用取得，不改HalconPhaseValue为rad。

稳定错误码到文案：SL-VAL→ParameterError，SL-PAT/SL-VIS-002→SourceMismatch，SL-SEQ/SL-TRG→Incomplete，SL-RES→Capacity，SL-CON/SL-IO/SL-CANCEL/SL-RDB/SL-DISPOSE→原SL.Unknown及Query，SL-LEASE→Stale，SL-CAP→Version及停止后新代Open，SL-TEMP→Cooling，SL-BLK→原Blackout，SL-MIG→Version，SL-VIS-001→LayoutUnavailable（字段非法则ParameterError），SL-VIS-003→DisplayUnavailable。质量Observed只“已观测/已觀測/Observed”，候选Eligible只“可比较/可比較/Eligible for comparison”，不给“合格”；未评估/无资格/Unknown三者分开。生成的Generated显示“已生成/已產生/Generated”，Prepared不是投影中。Scope权限/设备物理停止仍用原Owner回执，不由翻译或显示颜色推断。

**SL-UX验证。** 复用§9.5两独立STA Host A/B（各Dispatcher/view/Host/namespace，不引用对方控件或产品Shell），固定1920×1080验证viewport内扣taskbar/边框，不另跑分辨率矩阵；给双方D真实contract的Synthetic DisplayLease与固定有效期、明确标Simulation，只测试显示/协议。

| 断言 | 可执行输入与预期 |
|---|---|
| SL-UX01 | D.Acquired 2×1/stride8/Pbgra32 bytes `[0,0,0,0,64,32,16,128]`、源Asset/hash/Revision完整；第0pixel透明，第1pixel半透明，不premultiply两次，底图不变。Fit/1:1/轮缩/平移/逆坐标半开边界，不触发设备；新Revision/late/过期不画旧图并按原lease释放；Downsampled只显示预览坐标 |
| SL-UX02 | 总预算按首次3B/更换2B_old+3B_new上界±1；copy/WritePixels/Dispatcher未投递或已执行未交付/Release/query失败→保原Task/bitmap/lease费用，不能GC退根。A关闭B仍显示/查询；拒绝移交保持全原根，复用SL-UC05/RET04而不造新恢复API |
| SL-UX03 | zh-CN/zh-TW/en-US全部固定Key及各枚举/十指标/错误正常、缺资源/异常/空文/timeout后备；最长英文不遮Stop/未知/恢复，culture切换不改hash/操作/输入。ReadOnly/撤权/selection stale禁止发光和参数提交，自己的Stop/cleanup仍可执行；Alt+S/Enter/Tab/Esc规则一致 |
| SL-UX04 | 文本逐字符`0.`→`0.1`、非法整数/NaN/Inf/负号/超界/版本及取消编辑；无中间态提交、失败不补0、不覆盖原Spec，Enter字段编辑不启动预览；生成源缺失/草稿revision错/Build同id异值/丢命令回执/选择只改本地generation反例，Build设备调用0，D执行一次，原内嵌id/权限/CAS/限额可查。DraftRevision变旧Advice/Plan Stale，选择行联动图/Actual/时序且不创建第二事实；图层Owner/单位/invalid保真 |

## 11. 怀疑式场景走查

下列数字均为合成契约算例，不是生产阈值。

| 输入/触发 | 处理与预期 | 恢复/消费者断言 |
|---|---|---|
| 2×2 ByteGray内容[0,0,0,0]，一个Vertical Custom图案p1，steps s0/s1均引用p1 | 4 bytes、两个不同StepId、ordinal0/1，计划合法；PatternBytes=4，不复制为8 | 两Host同hash；只证明规划，不证明可解码 |
| 改第二step ordinal为0/引用错误hash | SL-VAL结构问题、Rejected、无plan | 原索引路径稳定，不自动修正 |
| UInt16 2×2却声明4bytes | 应8bytes，InvalidValue | 上传前拒绝，不能补零 |
| width=int.MaxValue,height=int.MaxValue,UInt16 | checked字节/limits拒绝，未复制/哈希大内容 | 无OOM作为正常流程 |
| PhaseRadians=NaN、2π或缺frequency | InvalidValue；-0合法canonical为+0 | culture切换不改hash |
| 首个step合法但第末个缺失/重复/乱序 | 整次模拟/设备序列无效，不以计数补齐 | 采集Owner决定新attempt，不拼旧帧 |
| 相位误差+0.2和-0.2rad | 有符号均值0不能通过；MAE/RMS=0.2，max=0.2 | acceptance阈值来自Profile |
| 相位参考π-0.01，观测-π+0.01 | circular绝对误差0.02rad，不是约6.26 | 无效域不参与误差分母 |
| Prepare leaseVersion=3，续租竞态变4/boot改变 | Arm拒绝，冻结hash不匹配；不输出 | 同代重新Prepare；新代Open |
| 同key/hash重复Display，当前stateVersion已变 | 先Replay原Actual，设备调用仍一次 | 同key异hash Conflict |
| display响应丢失，设备可能已发光 | Invoked/Unknown，原operation查询、cleanup | 禁止新key重发/清空历史 |
| Display中取消，Stop ACK但Drain unknown | LogicalCancelled、Held、无TerminalOutcome | 恢复Owner继续；不释放句柄 |
| 只收到Blackout CommandAck | AckOnly/Unconfirmed、锁定生产 | 物理读回或维护，不说黑场确认 |
| 弱信号/饱和/遮挡，没有相位有效域 | observation拒绝或NotObserved、有效比例带分母 | 不降min_gray_difference至0求通过 |
| 多候选仅部分有同谱系证据 | 缺证据项NotEvaluated，结果Advice/Stale规则 | 无静默选优/写入生产 |
| UI关闭、切语、迟到旧诊断 | Owner继续cleanup、旧revision不覆盖当前 | 第二Host操作/语言不变 |
| 进程重启ledger NotFound | 缺记录≠无副作用，Unknown/隔离 | 外部安全状态确认后恢复 |

普通实现者视角：从DTO、单位、校验、hash、事件走到结果；不得猜枚举/阈值/模型类型。集成人/操作者视角：空Host接入、权限拒绝、设备未知、关闭/重启、第二消费者；不得以UI消失/ACK/漂亮表面替代事实。上述反例分别对应§12，不新增平行审计报告。

## 12. 测试与可判定验收

首版纯托管测试沿[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)：Microsoft.NET.Sdk、net10.0、OutputType=Exe，只引用受测工程/BCL，确定性断言+固定clock+可控异步闩锁，不临时选测试包。任一失败/未完成/必需项跳过返回非零，全部执行通过才0。dotnet test空执行不算通过。

| 用例ID/切片 | 覆盖与断言 |
|---|---|
| SL-C01 / 0 | 正常/reference-only/verified/单图重复step；Validate/Plan同limits、一致报告，hash稳定 |
| SL-C02 / 0 | default/空、非法ID/SemVer/enum、duplicate、unreferenced、NaN/Inf/phase组合；路径/错误排序固定，MaxIssues截断仍Rejected |
| SL-C03 / 0 | checked乘加、单artifact int容量、每项/总bytes/working/events边界；等于上限通过、+1拒绝，无部分plan |
| SL-C04 / 0 | 附录 A.1 的完整289-byte固定canonical向量/三个SHA256预期、UTF8长度/LE、-0/+0、hash大小写规范化及ReferenceOnly/Verified同hash；多artifact按PatternId排序后输入重排hash不变，step重排拒绝/重新编号后新hash，limits变化新hash；独立预期bytes核验而非调用同实现算预期 |
| SL-C05 / 0 | Simulator各fault/事件顺序/ticks/超限；正常恰N步；缺/双/乱不可PlanCompleted |
| SL-C06 / 0 | 并发不同plan、每个处理点取消、重复/版本导入；无共享状态、Cancelled无plan、不加载UI/SDK/视觉 |
| SL-P01 / 1 | 全状态/命令矩阵，双写CAS/同key replay/异hash conflict；设备调用一次；ledger Begin/Invoking失败不调用 |
| SL-P02 / 1 | slot满/lease过期/renew-release竞态/跨boot/generation；Prepared/Armed不可续租；旧回调不更新新代 |
| SL-P03 / 1 | Software/Hardware模式、时序不等式、不同clock无映射、stream缺/重复/双结束/流退出；不伪造同步/完整性 |
| SL-P04 / 1 | 在每个设备调用点取消/超时/断线、迟到Actual、保存失败、NotFound；Stop/Blackout/Drain顺序及未知Held/无终态 |
| SL-P05 / 1 | Close/Shutdown重复、无法抢占、callback/ledger容量、过温、重启/同代恢复/新代Open；Owner保留、无盲重试/资源泄漏 |
| SL-V01 / 2端口 | GenerationSpec非法/观察谱系错误/预算/取消、Advice多个候选/过期；无native也可测 |
| SL-GX01～05 / AsunImage生成设计 | §7.4完整定义/公开factory/逐对象hash与角色、raw byte导出/指针有效期/有界根，双无UIHost与失效/错误/取消/清理；原SL-V02及正式native向量保持，未运行 |
| SL-UX01～04 / WPF补充设计 | §10.4无隐藏viewport默认挂接/显示坐标与双buffer预算/三语完整目录/参数编辑回滚，复用§9.5/SL-UC及两STA Host；未实窗 |
| SL-V02 / AsunImage | 三路线生成数/顺序/角色/hash；参数变更重新gen；同handle串行；部分失败/取消真实排空后清模型 |
| SL-V03 / 真实AsunImage与集成IM-032 | HALCON原byte/uint2解码算子语义及persistence前置/切换清结果、3D不可Defect、无效域/ROI坐标、circular phase反例；阈值来自Golden/Profile。当前IM-032光学仅Mono8，uint2及未公开phase/layer不通过现桥伪装接通，能力拒绝见SL-BR03 |
| SL-BR01～07 / 2宿主消费桥 | B.4.5的A quality+发布SIM、B quality+缺项Advice两完整无UI输入；SL-BR02谱系/域、03支持边界、04共同资产/参数匹配、05原Task/异常/排空/全量移交、06逐维预算、07runtime/输出闭合，具体输入与预期唯一见B.4.5。使用同一10/120/180s wall期限；文档断言尚未运行 |
| SL-JB01～07 / 2 Joint producer | B.4.6公开组/内容/专用refs、A Solve/Validate/Publish及B Resolve双无UI Synthetic Host、原Task/stream/根与有限恢复；首次无setup新消费桥见B.4.6.6，真实运行资格NotReady；10/120/180s断言未运行 |
| SL-JD01～05 / 2首次观测producer | B.4.6.6完整DecodeRequest/具名8raster/6Joint payload/两独立域/原Owner、两个原Synthetic Host正常拒识与g1完整封存、取消迟到/顺序错；10/120/180s断言未运行 |
| SL-QB01～07 / 2 Joint资格绑定消费 | B.4.6.7原两个无UI Host同次Resolve捕获/同Owner独立复查/纯值指纹与完整伴随引用；正常、撤回优先、epoch/evidence变化、错来源/关联、迟到、限额及全量移交；复用上游四向量，不重算旧Golden；新增文档断言未运行 |
| SL-DG01～05 / 2成功重建诊断桥 | B.4.7完整角色/支持域、D01/D02八层字节/单位/域/来源与受限本地LayerRefs映射、迟到/异常/预算；复用IM-032唯一夹具；文档断言未运行 |
| SL-U01 / 3 | §10的实窗、键盘/UIA、三语、主题、关闭/未知/迟到/虚拟化；停止不被遮挡，数据/hash不变 |
| SL-H01 / HIL | 实际投影/相机触发、光电读回、黑场、掉线/掉电/互锁、热稳/长稳、时间不确定度；设备/光学负责人按Profile签收 |
| SL-X01 / 双Host | 无UI检测Replay Host和可选UI试验台同API；分别走正常归还与异常保留。A在Close/usage/Dispose/移交逐点抛错或不返回时保留原槽，B仍可完成查询/归还；A取消/切语/恢复不更改B的ct/身份/额度。A槽耗尽仅拒绝超出宿主总预算的新创建，不清理B既有Owner；历史可读，生产业务不进入Core |
| SL-PC06 / 1 | C.1/C.3全部集合/range/nullable：Formats空/重复、NaN range、负pending、Unknown配Released拒绝；初始Closed generation0与Open后正generation分开 |
| SL-PC07 / 1 | Ledger.New/Replay/Conflict/Unavailable、回执bytes解析、parent/child CAS及close期间Append失败；同key同hash设备调用一次、异hash0次、未知记录不被容量淘汰 |
| SL-PC08 / 1 | Query/GetEvents deadline过期/Unavailable/分页/断档/旧generation回调；非阻塞、有界MaxItems、事件cursor不跳过缺项、query取消不更改execution终态 |
| SL-PC09 / 1 | 最末step后自动cleanup与Host finally重复Stop/Shutdown复用原请求；Open/Upload/Prepare/Arm/step/hardware丢回执保留全部原id/request/Task，Arm启动前executionId已保存。Stop/Shutdown/快照/usage/Dispose/移交逐点同步抛错、异步fault、WaitExpired/取消、迟到；嵌套finally仍到移交处理，业务异常原栈/独立cleanup错误均可查；拒绝或未确认不退槽，未知不能Dispose，Task完成也不替代实际归还。stream按E+1/E/1预留，超限不再MoveNext，pending MoveNext不并发Dispose，原enumerator随槽恢复 |
| SL-VC04 / 2托管 | 所有B请求/枚举/集合边界、同operation/hash重入/异hash；假Adapter生成2×2、Manifest乱序、相位元数据缺项→Rejected无Plan；不用真实HALCON证明合格 |
| SL-VC05 / 2托管 | Generate/Observe/Evaluate逐点取消/超时/迟到；QueryDrainUnknown保持Held，Close返回全量unresolved。Close/usage/Dispose/移交逐点抛错、不返回、拒绝或回执丢失：原进程槽保留session、全部Generate/Observe/Recommend身份与所有原Task/输入/额度，usage失败不补零，Close空unresolved不删payload。嵌套finally到移交；业务错误不被cleanup覆盖；drain确认前不释放bytes/model，晚到数据只归旧operation，接收确认前不退槽 |
| SL-VC06 / 2托管 | candidate缺指标/无真值/错曝光谱系/MaxEvaluations不足/过期、+0.2与-0.2相位；NotEvaluated无Rank/Advice，排序稳定且结果不写Profile |
| SL-VC07 / 2托管 | 两session/同Adapter串行、队列/retainedBytes+1、Profile变化、重复Close/Dispose提前；独立Host关闭不影响另一Host，资源容量可查，不把Task超时当native停止 |
| SL-UC02 / 3托管 | 所有UiPayload/Kind/method/UiResult匹配、未知派生类、CommandId异payload、stale revision、ReadOnly；禁止错Kind/旧选择产生设备调用 |
| SL-UC03 / 3托管 | Subscribe队列满、sink异常/迟到、deadline关闭/Dispose；Gap+NeedsResync，ledger不丢Actual/终态；闭窗后不再访问Dispatcher |
| SL-UC04 / 3托管 | Acquire旧revision/过期/超MaxThumbnailBytes、length/stride溢出、释放失败；迟到Lease仍Release追踪，不能GC当释放，三语显示不改hash |
| SL-UC05 / 3托管Host及实窗 | §9.5/10/D：factory/Bind前根槽容量不足时调用0次；逐点注入组装/Bind/GetSnapshot/ApplySnapshot/UpdateCulture/Close/GetUsage/Dispose业务或清理异常、原Task卡住和Dispatcher未投递/已运行未交付。业务原栈与cleanup错误分别可查；嵌套finally到全量移交，根仍持有未交付Bind/晚到session/显示/订阅及全部Task/身份。原Close/GetUsage/Dispose调用各至多一次；移交拒绝/异常/超时不退根，迟到接收只切换一次Owner。托管/可控Dispatcher断言不冒充实窗；实窗另按固定1920×1080扣边框/taskbar、三语/Stop常显/未知状态验证，关闭失败不报完成、不取消无关生产Owner |
| SL-RET01 / 1/2/3托管 | §6.2合成payload2/identity3及每byte上限±1；预留cleanup/墓碑后接纳，Release返payload不返identity，第四新请求被拒且无设备/生成调用；GetUsage包含所有key/lease/display/subscription索引 |
| SL-RET02 / 1/2托管 | QueryTerminal→Release CAS竞态、同id/hash重复/异hash、released old请求/硬件stream、expired结果仍完整；Released返回同墓碑/原ResultHash、零重执行；Unknown/Borrowed父子依赖Release Busy不改原payload |
| SL-RET03 / 1/2/3托管 | 保留clock boot变更/重启namespace、索引满/ledger保存失败、迟到原结果；未知Owner/原namespace恢复不丢，新namespace拒绝旧Guid前缀；不以close/dispose/TTL删除去重身份。Host存活槽/Task数/metadata/输入bytes任一满时factory=0；绑定发生在业务try前；保留已Released原身份与原Task条目直到确认退槽/全量移交。cleanup额度不被业务耗尽/取消，Dispose未确认和移交拒绝/异常/超时保持槽；晚到确认沿原offer只切换一次Owner，无重复设备调用/双写；正常退出须实际归还、payload双零、墓碑查询Owner确认及Dispose成功 |
| SL-RET04 / UI | Command/Display/Subscription释放墓碑、Acquire丢回执/迟到/期限、缺键/空文/超时三语后备；QueryCommand/QueryDisplay精确Released，Busy/Unknown正常文案不直显enum/key。关闭后晚到DisplayLease先强持LeaseId/bytes再首次Release，不Apply旧图/不新RequestId Acquire；ReleaseTask未知只观察原Task并QueryDisplay。业务异常叠加Close/usage/Release/订阅Dispose/GetState/全量移交异常或未确认：保留CommandId/DisplayRequestId/SubscriptionId、原Task、未交付Bind与迟到session/lease、错误/额度，不能清索引。payload双零但原Task/显示/回调未结束仍不退槽；仅显示Released+订阅Closed/Confirmed/Released、Close确认、全部相关Task结束、usage双零及Dispose成功且墓碑查询Owner确认后退重资源槽。拒绝移交/迟到确认/Close回执RecoveryOwnerAccepted不足以全量接收均不得丢根 |

| 2宿主消费桥 | B.4.5同完整manifest/原帧/ROI，A SIM/质量，B两阈值同样本/九缺项；原位深/stride、group数、支持域、正常/故障/取消 | 原帧借读/copy/hash前后当前性、quality累计读取/共同支持、IM-032 run/lease/native/CSR copy、剩余预算与Held占用；原Construct/Completion/Close/run/stop/dispose及全量移交阶段耗时、两级根slot/任务/身份/bytes高水位；事实Producer/域分离与十项缺项率，目标未冻结NotEvaluated |
构建命令（未来工程创建且获准后执行）：
`dotnet build src/Modules/structured-light/Asun.Modules.StructuredLight.Core/Asun.Modules.StructuredLight.Core.csproj -c Release`；
验证命令：
`dotnet run --project tests/Modules/structured-light/Asun.Modules.StructuredLight.Core.Tests/Asun.Modules.StructuredLight.Core.Tests.csproj -c Release`。
Projection/Vision托管端口工程代入binding同名规则执行build/run；真实AsunImage/WPF工程分别在目标本机BCL Exe Host运行适用用例，不将跳过硬件/实窗标通过。托管Exe冻结三级单调wall期限：每case含其清理观察共10s、单suite共120s、外层托管测试进程共180s；达到任一期限为失败/非零，不把剩余项跳过算通过。case内部业务/cleanup预算必须分配在10s内，模拟clock推进仅驱动逻辑deadline/迟到顺序，不改变wall stopwatch，也不需真实等待ResultRetentionNs。故障Task可以保持pending以验证Owner保留，case验收的是有限观察返回且原槽仍存活，不要求虚构资源已归还；suite持有这些有界槽直到闩锁释放并按真实回执对账。180s外层监督仅可终止纯托管Simulator卡死测试并报告失败，不宣称原Task/设备/native资源归还；真实硬件不得以Kill证明drain，继续沿现场恢复Owner/设备规程。以上命令本轮均未运行。

消费桥BenchmarkProfile额外固定两个只读基线版本/hash、memory/managed或AsunImage后端、源copy/原帧租约路径、矩形ROI/ValidMask及原支持用途、每candidate原图组/参数/真值/AcceptanceProfile引用、各下游与父最早deadline/预算归属。一次端到端样本从前检/源借读开始，到原Task与全部资源真实归还结束；Unknown/WaitExpired/未移交样本保留删失/失败状态，不进入“已释放成功”的尾延迟分位或峰值合格集合。Group共同支持不替代表面域，软件限额448/512MiB不当实测峰值；单次计时不生成P50/P95/P99，两个candidate相同曝光输入不能充作独立样本。测点沿SL-BR05/06及DEV-GOV-010口径，未有批准目标不判性能通过。

## 13. 性能预算与可观测性

沿DEV-GOV-010 §3.1唯一统计口径，不复制分位公式。BenchmarkProfile必含ProfileId/version/hash、Core/Adapter/runtime/OS/CPU/设备/固件、HALCON/AsunImage、输入plan/manifest/证据hash、尺寸/格式/图案/step数量、cold/warm/预热/样本计划、并发、有限deadline、各资源上限、测点、目标值及批准来源。无目标允许测量但结论NotEvaluated；未排空不得性能通过。

| 切片 | 负载维度 | 阶段/资源测点 |
|---|---|---|
| 0 | ReferenceOnly/Verified，byte/uint16，P/S/总bytes/MaxIssues/Events，合法/错误/取消；单Host与并发独立Host | Validate/Plan/hash/Simulate耗时，charged vs CLR峰值、hash输入bytes、错误/事件数、分配/GC；无设备指标 |
| 1 | slots/bytes/steps、Software/Hardware、ACK/PatternId/光学、clock映射、热/功率、callback burst | 排队/Upload/Prepare/Arm/trigger-display/readback/Stop/Blackout/Drain/端到端；slot/lease/ledger/queue高水位、超时/Unknown/迟到率 |
| 2 | 三生成路线、方向/归一化、全幅/ROI、persistence开/关、共同样本/诊断层 | 生成/导出/哈希/观察/复制；IM-032阶段只消费其测点；native/managed/result/诊断峰值；不可观测记Unknown |
| 2 Joint/诊断消费增量 | 同组white/black/white-surface/valid/两命名层、环带支持数、Joint typed/raw闭包、D01/D02层数量/域/来源 | 首次Decode的原接纳→真归还、source含padding/hash/Mapping/独立域/qNaN核验、producer copy/hash/EOF/封存、provider→workspace→Store完整字节导入、Resolve当前资格/导出复制、R3DL编码/域副本/峰值、原Task实际退出/stream归还/根移交延迟；与native算法/物理时序分别统计，无目标NotEvaluated |
| 2 Joint资格绑定消费 | 原/待绑定/复查完整规范快照≤64KiB各份，两个独立根/一次内部Read/一次直接复查、8输出/64任务 | Resolve原Task与Owner Task/完成路径、完整snapshot编码/深复制/复查/Bind/伴随封存耗时，桥1MiB逻辑预留与实际CLR峰值、源Owner/operation关联失败、epoch/evidence/invalidation、Unknown/撤回/迟到/未决直接Task及全量移交；Export/Store/native另计，不以Core Stop当Host复查排空，无目标NotEvaluated |
| 3 | 实际1920×1080client/DPI、最长三语、步数/事件窗/图表点/缩略图budget | Dispatcher投影延迟、选择联动、丢弃迟到计数、显示资源、关闭到移交恢复；不把UI帧率当设备时序 |

资源目标先于执行冻结；未有可信native envelope时拒绝相应真实诊断，不先分配再OOM。长期运行按Profile有限窗口观察slots/lease/handle/队列/ledger/显示副本是否随operation无限增长；既有证据输入/版本未变复用，不重复全审。日志带operation/session/projector/generation/stateVersion/sequenceHash/ordinal/adapterVersion/clock domain、请求/实际时间、Trust/读回、停止/黑场/排空结果及错误；不写凭据、不嵌大量原图、诊断不是第二事实库。

本版保留专项Benchmark维度补充：§6.1/C.5的payload records/bytes、identity records/bytes、ReplyHeaderBytes、cleanup预留、拒绝/Busy/Released比例、GetUsage/Query/Page/Release耗时及并发CAS负载。分别测N个完成后仍Retained、expired未释放、已Released墓碑、未排空Held四桶，长期曲线应被显式额度截住；identity满允许拒绝新请求，不能以吞吐持续为由清墓碑。每次调用回执bytes<=MaxSingleReplyBytes，native未知归还仍按原Owner统计，不省略失败/删失样本。本轮仅冻结测点/断言，Profile目标/实测仍NotEvaluated，不改DEV-GOV-010统计口径或Core已接收资源公式。

## 14. 独立发布、回退和第二消费者验收

Core、Projection、Vision端口、AsunImage实现、WPF分别发布，公开XML文档/错误资源/contract version随包；厂商Adapter另包。Core不打包桌面/视觉/厂商runtime。发布声明实际目标框架、直接依赖/程序集版本、API/canonical版本、构建/用例结果与限制，不创建无人消费的重复manifest。用户已确定AsunImage/DevExpress直接引用，不下载/改版/许可证核验。

升级顺序：停止准入 → drain或隔离旧operation → 保留原ledger/配置/图案/资产/解释器 → 新包离线Replay → Host验证 → 切换；失败回退原包和原Profile。旧hash/Actual/记录只读；回退不复现设备副作用、不删除未知任务。contract major不兼容需显式转换新身份。

双消费者验收范围：检测Host无UI规划/执行模拟与采集binding交接；试验台同DLL规划/限时预览/诊断；各自实例、语言/权限/clock/ledger、一个真实物理设备仍由宿主互斥。两Host必须验证无隐藏窗口/产品数据库、相同错误语义、取消/DrainUnknown及历史回放。真实相机/计量/现场性能另门，不以Host模拟替代。

## 15. 六项准入与剩余外部门

Slice-0/1/2按DEV-GOV-010 §3.1核验：主控已独立复算附录A.1并接收Slice-0六项文档规格，原接收保留；主控已内容复核§9.3–9.4.1及SL-PC/VC/RET断言，接收Slice-1本模块托管事务/Simulator、Slice-2本模块托管生成/观察/Advice端口六项规格，ModuleCoreImplementationReady保持，仅规格准备。Slice-3为WPF切片，主控于2026-10-10逐项接收§1/10角色、消费者、任务流与独立边界，D.1–D.2公开值/API与Owner，§9.5 Root/Dispatcher/迟到Bind/显示订阅/cleanup/确认全量移交，SL-U01/UC02～05/RET04断言，§13 UI测点及唯一程序集/测试路径/范围。已接收范围仅本模块独立WPF控件与D公开Host组合的指导规格内容，未发现该范围的非现场内部设计缺项，已完成指导全部保留。按DEV-GOV-010 §3/§3.1统一门槛，真实WPF资格和受影响平台接入未关闭，Slice-3准入仍为PreparationIncomplete/NotReady，不授ImplementationSpecificationReady或ModuleCoreImplementationReady；内容接收不替代资格关闭。不包含正式产品Contract/Schema接线、真实AsunImage或真实下游接线/共同标定资格；B.4已支持的公开字段消费桥指导内容获主控限定接收（2026-10-11），不提升实际接线/运行/算法/UI/资格状态。真实WPF实窗、DPI/UIA/三语、设备联动、性能与产品代码/构建/运行仍未执行。整模块保持DesignReview/Prep / PreparationIncomplete，不据此授产品集成或生产验收。

| 切片 | 1边界/消费者 | 2唯一API/资源 | 3独立Host | 4场景/断言 | 5Benchmark | 6工程/范围/调用 | 当前结论/剩余门 |
|---|---|---|---|---|---|---|---|
| 0 | §1–2 | §3.1/附录A/A.1 | §9.1 | §11/SL-C01～06 | §13 Core | binding/§9/12 | ModuleCoreImplementationReady（主控已接收六项文档规格）；代码基线/编译运行未执行 |
| 1托管事务/Simulator | §1–2 | §3.2–3.3/4–6.2/C.1–5 | §9.3/9.4.1 | SL-P01～05/SL-PC06～09/SL-RET01～03 | §13 Projection及保留专项 | binding/§9.3/12 | ModuleCoreImplementationReady（主控已接收六项文档规格，仅规格准备）；实际代码/构建/运行未执行；真实SDK/耐久服务/HIL另门 |
| 2托管生成/观察/Advice端口 | §1/7 | B.1–3/§6.1/C.5 | §9.4/9.4.1 | SL-V01/SL-VC04～07/SL-X01/SL-RET01～03 | §13 Vision及保留专项 | binding/§9.4/12 | ModuleCoreImplementationReady（主控已接收本模块端口六项文档规格，仅规格准备）；实际代码/构建/运行未执行；B.4已支持消费桥指导内容已限定接收（2026-10-11），首次Joint decode-only源规格已接收、本页B.4.6.6首次观测producer指导已获主控限定内容接收（2026-10-11）；CAL 0.3.2-prep资格技术绑定/版本域源桥已限定接收；B.4.6.7资格绑定消费增量已获主控限定内容接收（2026-10-11），真实资格及接线另门 |
| 2宿主下游消费桥增补 | §1/7/B.4两真实消费用途 | B.4.1–4，只消费已接收下游公开规格 | B.4.5 A/B完整fixture及两级根 | SL-BR01～07，未运行 | §13桥测点/Profile，未实测 | 既有Vision.Tests/Hosts；只改本文 | 已支持的image-quality/reconstruction消费桥指导内容获主控限定接收（2026-10-11）；实际接线/运行/算法/UI/资格未验，不撤回既有Slice-2端口ModuleCoreImplementationReady。Joint 0.3.1及IM-032 0.2.5源合同已接收；B.4.6–7本模块确定指导增量已获主控限定内容接收（2026-10-11），不改变原B.4.1–5限定接收；首次decoder源规格已接收、本地首次观测producer B.4.6.6指导已获主控限定内容接收（2026-10-11）；CAL 0.3.2-prep资格绑定源桥已限定接收，B.4.6.7资格绑定消费增量已获主控限定内容接收（2026-10-11）；HybridBoth诊断不支持 |
| 2 Joint producer/重建诊断增量（限定内容接收） | B.4.6.1/B.4.7 | Joint §7.4公开合同及IM-032 §4.2.2/4.4.1；本地copy/refs不增DTO | B.4.6.4双Host/B.4.7 D01/D02 | SL-JB01～07/SL-DG01～05 | §13新增测点 | 原Vision.Tests/Hosts，只改本文，无新工程 | 本模块确定指导增量获主控限定内容接收（2026-10-11），范围为Joint provider/规范封存/源与Store Owner/原Task/双Synthetic Host、完整角色与受支持诊断保真消费及SL-JB/SL-DG断言；不授真实接线或运行资格。原Slice-0/1/2准备保持；首次decode-only源规格已接收、本地首次观测producer B.4.6.6指导已获主控限定内容接收（2026-10-11）；CAL 0.3.2-prep §7.4.6B技术资格绑定/期望watermark及版本域源桥已限定接收；B.4.6.7资格绑定消费增量已获主控限定内容接收（2026-10-11），真实算法/运行/性能/物理资格未验 |
| 2首次观测producer（限定内容接收） | B.4.6.6/CAL-JC现消费者 | 已接收IM-032 §7.6公开Decode契约/规范bytes及本地Owner映射 | 原两个Synthetic Host/3×2反序与64×48 g1完整包 | SL-JD01～05 | §13 Decode→封存/归还测点 | 原Vision.Tests/Hosts；本轮仅指导 | 源C1/S1六项规格接收/A1指导限定接收；本模块B.4.6.6确定观测producer指导获主控限定内容接收（2026-10-11），含双Synthetic Host 3×2反序核对及64×48 g1完整包封存；缺其它四组同新manifest/mapping不得Solve，旧五组成功仍沿B.4.6.4。主控未独立复构新g1 payload向量；真实native/封存/全首次Joint/资格/运行/WPF/性能/物理现场门仍PreparationIncomplete，不扩大B.4.7 |
| 2 Joint资格绑定消费增量（限定内容接收） | B.4.6.7/原两个无UI Host | 已限定接收CAL 0.3.2-prep §7.4.6B公开Bind/JointCodec；不增本方API | B.4.6.7 A/B同次捕获/原Owner复查/纯值子例 | SL-QB01～07，未运行 | §13捕获/复查/绑定/根预算测点 | 原Vision.Tests/Hosts；仅修改本文 | 资格绑定消费增量已获主控限定内容接收（2026-10-11）；源桥接收和四软件oracle核对不替代真实binding/native/全首次Joint/WPF/性能/物理运行资格；其它原接收保持 |
| 2真实AsunImage | §7/7.4 | §7.4公开factory/definition与B原接口 | 独立目标本机双Host | SL-V02/03/SL-GX01～05 | §13 Vision/7.4预算 | binding/§7/12 | 软件处理/布局来源/生成导出/根资源设计已冻结；本模块实际native定义/角色/phase/像素hash验收、公共C#封送编译/真实资源envelope及Golden未执行，只阻该适配及真实联动，不移交客户补选算子或API |
| 3 WPF | §10角色/任务 | D.1–2/§6.1/C.5 | §9.5进程根/Dispatcher/Query/Release/全量接收模板 | SL-U01/SL-UC02～05/SL-RET01～04 | §13 UI及保留专项 | binding/§9.5/10/12 | 主控已接收指导规格内容（2026-10-10，无非现场内部设计缺项）；PreparationIncomplete/NotReady，真实WPF/产品接线资格门未关闭；实际产品代码/构建/运行、WPF实窗、DPI/UIA/三语、设备联动/受影响平台接入与性能验收未执行，保留后续门 |

外部门准确隔离：
- 真实设备分辨率/格式、gamma/物理映射、触发/读回/Stop/Blackout、热/功率/互锁和时钟误差，来自选定SDK/Profile/HIL；阻真实设备执行/现场资格，不阻Core。
- 代表图像/共同真值、phase/覆盖/误接受拒绝阈值、性能目标、标定适用域，来自批准消费者Profile/Golden/计量；阻真实算法资格和生产，不编造。
- image-quality 0.6.0-prep Service/Core+Simulator、IM-032 0.2.4 Core/发布Simulator及0.2.5完整角色/成功重建诊断增量、calibration-assets 0.3.1 Joint API v1公开规格已接收；旧源正文待接收字样不能覆盖本轮主控明确接收。B.4.1–5原支持范围内容接收保持，本模块B.4.6–7确定消费指导增量获主控限定内容接收（2026-10-11）；不重审源Core、不提升运行资格。旧专业指导/产品Contract/持久化Schema由主会话串行整合。
- Slice-1接口声明已补齐，生产ledger耐久实现/恢复服务/互锁scope需宿主接入验证。首次共同标定的无setup HybridBoth解码接口现已由IM-032 §7.6接收，B.4.6.6精确消费（主控限定内容接收，2026-10-11，仅观测producer规格），不再将源公开接口列未接收。CAL 0.3.2-prep §7.4.6B资格技术绑定/期望watermark与版本域源桥已获主控限定内容接收，原接口缺口按源规格闭合；本模块消费指导唯一见B.4.6.7，资格绑定消费增量已获主控限定内容接收（2026-10-11），不能将尚未执行的消费者接线/来源关联验证改称客户外门或运行通过。完整快照技术指纹不等资格原件签名，不用Check/runtime摘要替代。B.4.6保留完整Joint专用refs；B.4.7原成功重建诊断限定接收与HybridBoth诊断不支持保持。真实Adapter/C#封送、资源系数/Golden/性能及Slice-3真实视口/显示/WPF仍须运行验收。
- AsunImage/DevExpress按已确定依赖直接用，不列安装、授权、兼容性复查或算子存在性门。

B.4两轮定向自审（2026-10-11）：第一轮对照两个只读公开基线逐字段/factory/nullable/支持域，补明确ProjectionSequence及原hash、完整ReconstructionInput.Calibration/Execution.Calibrations、原时序12字段、源mask/矩形ROI限制和下游缺角色/layer拒绝；纠正笼统“下游公开字段未接收”。第二轮走两Host正常/错误/取消/迟到/排空/拒绝移交，落实同父3s剩余、10/120/180s wall预算、448MiB保守同时预留、原Completion保存及共享quality关闭去重，禁止adapter.Close反调父Close。Core附录A、B.1–3/C/D公开声明与既有§9.3–9.5调用/SL-PC/VC/RET断言保留；本轮为文档核对，未创建/编译/运行任何Host或真实Adapter。主控随后增量回读0.2.7-prep B.4.1–B.4.5并限定接收已支持的消费桥指导内容（2026-10-11）；本次只同步状态，不新增研究/重审/实现。

两轮内容自审（此前版本定向收口，结论保留）：第一轮从普通实现者视角核B/C/D每个请求/结果/嵌套类型、枚举值、nullable判别、deadline/budget和唯一签名；关闭了Capability无集合类型、Adapter无返回形状、ledger/authority裸bool、Vision无操作查询/Close、UiPayload无判别类型等具体缺口，并将正文调用同步到完整声明。第二轮从Host/恢复/操作者视角走§9.3–5正常→失败→并发→取消→未知→迟到→关闭/第二消费者，修正Arm未知时丢execution身份、finally移交失败丢session Owner、显示lease晚到未归还、订阅期限和ledger分页缺项等路径；对应反例落SL-PC/VC/UC组。它们是文档走查断言，未执行代码/设备/性能/实窗。图案/相机帧绑定/外部资格/重建Owner仍唯一；未知资源不终态，不质量放行。

### 15.1 当前架构全部批准范围的文档准备结论（2026-10-11）

本模块永久原会话对IM-011完整架构范围的结论：**可决定的软件设计已闭合，当前没有要求后续开发者补猜的内部算法、API、模块边界、UI或恢复决定。** 该结论覆盖生成AsunImage Adapter、投影端口及模拟器、观察/推荐、无setup首次producer、共同资产/资格消费和完整可嵌入UI，不仅是已接收Core。旧研究、自审、Core289-byte、Joint/Decode/诊断/资格四向量与既有接收直接复用；本轮只补§7.4真实生成的显式定义/factory/导出/根Owner与§10.4/10.4.1完整显示、编辑输入/命令构造和三语目录，修正当前权威中的过时接收表述。没有修改其它模块或共享文件，没有新工程、产品代码、测试、报告或脚本文件。

这只是DEV-GOV-010 §4的文档完整结论，**不授整模块ImplementationSpecificationReady，不提升原切片代码/真实运行资格**。Slice-0/1/2原ModuleCoreImplementationReady六项文档规格保持；Slice-3、真实AsunImage及受影响平台组合仍PreparationIncomplete/NotReady。已批准的B.4支持消费、首次观测及资格绑定指导接收保持；首次3×2只协议拒识、64×48新g1只封存一个完整观测包，缺另外四组同新manifest/mapping仍不得Solve，不将旧五组成功重写为新初始化完成。没有执行C#编译/产品代码、生成native布局资格、完整首次Joint、实际binding/Store、WPF、性能或物理现场验收。

| 当前完整能力/使用场景 | 唯一实施位置与确定结论 | 不适用/拒绝边界 |
|---|---|---|
| 无UI图案/原始自定义输入、内容/hash/预算/回放 | §3.1/A/A.1、§4.1/9.1/12，规划/Verified或ReferenceOnly、零基ordinal、ByteGray/UInt16Gray完整packed/units/错误和有界Simulator明确；不要求生成/设备/窗口初始化 | ReferenceOnly不可直接Upload；Custom不推断解码/计量，未知enum/版本/异常内容明确拒绝 |
| 三种HALCON生成路线、deflectometry入口、方向/相移/Gray与反图 | §7.1/7.4/B.1–3/9.4固定HALCON26.05算子和显式layout/factory/byte导出/预算/实际任务归还；同参数两独立Host，原native验收计划SL-V02/GX01～05 | 不猜Both序号/phase原点，不生成相机setup，不另实现decode/reconstruct；deflectometry只有生成/离线诊断入口，反射高度/缺陷算法不在IM-011范围，IM-032当前不适用用途拒绝 |
| 投影事务/缓存租约/软件步进与硬件序列/时序/能力/故障/恢复 | §3.2–6/C.1–5、§9.2–3/9.4.1固定请求/状态/端口、耐久Begin→Invoking、实际读回、ClockMapping上下包络、Stop/Blackout/Drain与同代/重连恢复；父/子/root及有界墓碑明确 | SDK具体实现暂不纳入；ACK或软件时间不证明光学稳定，不能抢占时显式互锁；Unknown/Held不能重发新身份、放行或退根 |
| 通用图像来源、饱和/弱对比/缺测/时序关联与成功诊断 | B.4.1–5/B.4.7、§7.2–3精确消费image-quality/IM-032公开输入：原Mono8/stride与EOF/hash/完整角色序列/attempt/frame/timing、独立quality域和surface域、支持图层/单位/来源与原任务 | 原图/两域/源坐标不得crop重算；缺/跨组/乱序整组拒绝，无值为NotObserved/NotEvaluated/qNaN或null，不补0/插值/旧帧。质量/饱和阈值归原Profile Owner；uint2光学、HybridBoth成功诊断及HalconPhaseValue转rad不在当前源合同支持 |
| 无camera_setup首次共同标定与资产封存/资格 | B.4.6.1–7唯一Decode→8raster/6payload+两独立域→provider→CAL-JC，白面/参考件/环带采样/版本/源与Store Owner、同次Resolve原Task/snapshot、同Owner新复查/完整伴随绑定均明确 | 不重复decode/get/find/局部拟合，不捏造setup/采样资格；Pure Bind/hash不签资格，单g1不得Solve，源Revision不改SemVer，缺完整伴随或水位变化拒绝真实使用 |
| 离线候选、参数建议及比较拒绝/解释 | §7.3/B.2–3/B.4.3/B.4.5固定有界候选/每项一次、同谱系曝光、10metric及阈值/分母/真值/共同域、Eligibility/排序/过期/缺项规则；source不可用有明确NotEvaluated | 不静默搜索/调gamma/阈值/重拍；生成参数变更须新definition和新匹配图组，不拿旧相机帧评新pattern；当前不证明rad和真值时phase门不得Eligible，不用缺项0宣称自动推荐完成 |
| 独立可嵌入WPF：角色/权限/参数/影像/时序/诊断/恢复/语言 | §10/10.4.1、D、§9.5/6.1/C.5固定25.2.3控件组合、Pbgra32显示/坐标/预算、显式GetDraft/BuildCommand、原Host revision与本地呈现generation、完整三语目录/键盘/权限及根清理；无UI仍同Core/Projection/Vision | view不依赖产品Shell，不自造授权Meta/触发，显示降采样不改数值或坐标事实；ReadOnly/撤权禁发光而自己的cleanup不丢，恢复未知只查原身份，不将窗口关闭当设备已停 |
| 双消费者、正确性/性能/发布回退 | §11–14、§9双无UI与双STA、SL-PC/VC/UC/RET、BR/JB/JD/QB/DG及新增GX/UX，正常/边界/取消/late/异常/confirmed全量移交完整；Profile负载/冷暖/端到端真归还/失败删失/资源/P50/P95/P99及版本回退有确定计划 | 10/120/180s是软件有限验证wall预算，不是现场节拍；Synthetic/Simulator/文档hash检查不能替代HALCON/WPF/HIL/计量/生产，性能目标未批准时NotEvaluated |

**剩余门与确切Owner。** 它们都是上述规则的实际实现/资格输入或范围外事实，没有未选的软件方案；不能笼统称未来Owner再设计。

| 剩余项 | Owner/需要的事实与验证 | 实际阻断范围 |
|---|---|---|
| 本模块工程、公共C#封送、真实生成数字布局/原件、clear/资源envelope及native Golden | 本模块AsunImage实现Owner；按§7.4公开factory在目标HALCON26.05/AsunImage编译调用和实际生成图组，验证完整role/方向/kπ/2/周期/原序/像素hash，记录真实峰值并核保守MaxResidentNativeBytes。C#tuple/iconic Dispose歧义仅通过公共签名/消费工程解决 | 真实生成/算法资格；不阻A纯Core/模拟端口，不交客户决定role/API |
| 物理设备能力、投影读回/黑场/排空、gamma/温度功率/触发与跨时钟误差 | 投影器厂商Adapter/设备集成Owner、采集/时钟/互锁Owner；按C.3和Profile提供实测能力、停止上界/稳定窗/映射/温度与HIL；本模块Own事务实现按已冻结合同消费 | 真设备执行/曝光同步/恢复安全；不新增SDK内部实现任务、不编造门值 |
| 参考件实测几何/证书/共面白区/采样资格、五组真实首次输入与Joint求解 | 参考件/独立计量/WhiteSurface与采集Owner、calibration-assets/IM-032原Owner；本模块producer按B.4.6实际取得完整两轴结果/环带/证据并封存，不决定他们的工艺阈值 | 真实首次Joint/计量；新g1不足五组时精确拒绝Solve，旧协议oracle不顶替实物 |
| 实际当前资格/Store与伴随封存、平台组合接线和事实提交 | 原Qualification/资产Store/宿主证据Owner；本模块消费实现按B.4.6.7同次Observer/同Owner复查及完整记录，持久化与发布必须原Owner真实确认；产品组合根由相应宿主Owner冻结实际authority/ledger与引用源 | 真实绑定/重建/产品集成；本模块纯值正确性不授签名/授权/质量放行，未执行消费者接线不冒称已运行 |
| 原图质量/误接受拒绝/phase真值/候选阈值、性能与资源目标 | image-quality/IM-032事实Producer、外部真值/AcceptanceProfile和消费者性能Profile Owner；本模块按§7.3/B.3执行固定排名与缺项规则，按§13已冻结口径测量 | 算法/生产建议和现场性能，缺目标仍可诊断NotEvaluated，不阻既有Core |
| 本模块WPF实现/三语/输入源、Root与真实显示资格 | 本模块Ui.Wpf实现Owner；按§10.4/D/§9.5实现两STA Host及固定viewport、参数逐字符/权限/图像/期限/根清理；实际组合宿主Owner实现显式IStructuredLightViewInputs和D Host端口，现场设备不由UI自动接管 | 本模块实窗/产品接入/运行资格，开发者无需再选控件或猜GenerateDraft/Prepare/Arm数据源 |
| 权威代码仓库与生产交付/现场验收 | 用户指定的仓库/交付Owner及客户/设备/计量负责人；代码任务前绑定实际仓库/分支或可审计快照，真实Golden/性能/HIL/FAT/SAT保原基线 | 本轮不写代码，不宣称当前HEAD/构建/运行/生产Ready |

本轮原会话审核与文档验证：第一轮以普通实现者从完整架构能力沿§3/7/B/C/D到输出，发现并补齐生成装配/未文档化索引假设、原生像素copy/借用期、草稿输入与命令构造/显示预算/完整三语；第二轮按独立宿主和操作员走正常→缺数据/版本/权限→取消/late→异常/关闭/恢复，核原Task/root/输出/预算和本地选行与Host权威revision不混。新增有限数学/字节边界及正式链接/围栏/表格定向核对，旧Core/已接收向量/API/fixture保持（C.5仅过时状态句同步），不重新验算旧Golden，不把文档检查当native/实窗运行。实际验证结果：复用tools/validate_docs.py的仓库文档完整性检查通过；本页正式本地路径、显式anchor唯一性、代码围栏配对、新表列数及GX/UX唯一导航通过。内存有限算例核W80/H60/P14生成B=67200、managed预留257280，以及2×1显示首次24/更换40 bytes的上界±1、预乘字节/四phase间距/一基转零基/半开逆坐标边界；这仅核规范数学，未运行像素生成/WritePixels。全文回读等于计划文本；原A、B.1–3、B.4全消费、§9.3–9.5及PC/VC/RET断言逐字保持，C/D仅上述已知状态句变更。CAL当前四个桥record字段顺序与本消费表一致，四hash仅存在性/一致性核对，未重算。达到当前全部批准范围的文档标准后本轮收口；后续实现发现新事实或正式合同变化再按受影响范围修订，不等待总控内容复核。

**CAL 0.3.3-prep定向兼容核对。** 本轮读取[calibration-assets唯一指导](../calibration-assets/DEVELOPMENT-GUIDE.md)（SHA256 `2acc06afd665c74065b3f30f6fa1658ce5fb85e68583f39df39a2e7832a4e532`），按§7.4.6B当前公开Expectation/Request/Result/Projection及Bind签名逐字段对照本页B.4.6.7消费表，完整字段、桥包1.0.0、快照规范/四向量和同次Resolve/同Owner复查流程兼容。§7.3A的Specialized类型/响应与平场/显示校正、§9.2A自动参数及§9.4二维读取/局部平面是独立合同，不替代Joint、不成为本方隐式gamma/LUT或生成更新来源；§10.1–2只取消其本scope操作，与本方独占预览根清理无冲突。§17.3采样/时序/命名层、IM-032/资格/Store的Owner分工与本页一致。本轮不重算旧向量、不修改CAL或本方B/C/D合同；B.4.6.7中0.3.2原接收版本/hash继续保留作历史基线。本方新增factory和IStructuredLightViewInputs须由本模块实现及相应完整编辑Host接线，显示Host仍按明确只读边界消费。

## 16. 来源、采纳与限制

### 16.1 当前权威与只读历史

- [独立模块架构](../INDEPENDENT-MODULE-ARCHITECTURE.md)、[永久会话表](../MODULE-INDEX.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)、[DEV-UI-040](<../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)、[IM-032](../reconstruction-3d/DEVELOPMENT-GUIDE.md)。
- [PKG-011](../../shared-modules/packages/PKG-011_Projection.md)、DEV-PLT-015、DEV-VIS-027用于应用映射，不再建立本模块第二API。
- `H:\docs\40-development\41-vision-platform\02-acquisition\结构光投影器抽象与图案时序开发指导.md`：83728bytes，SHA256 `1e0dd07fa80acd0a0545c7651e5363c8047f9d39a7c3b2076f46a3d9a08691f2`；2026-10-06已核，来源只读。采纳lease/operation/回读/关闭思想，不采旧HALCON24.11、AOI编排或设备阈值。[来源清单](../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json)保留原位置/hash。
- 20260927 PCBA-AOI原始副本、`docs/references/official/halcon/20260927/`与AsunControl历史结构光场景继续只读保留；不是26.05或当前AsunImage公共签名权威，不检查其中封装内部作为新API依据。

### 16.2 HALCON 26.05 本地官方原件

根入口：[operators](../../../halcon算子手册/operators/)；已直接读取生成/参数/解码/对象/清理/重建正文。SHA256用于本轮研究可追溯，不代替算法实测。

| 页面 | SHA256 | 采纳落点/局限 |
|---|---|---|
| [create_structured_light_model](../../../halcon算子手册/operators/create_structured_light_model.html) | d5792a723895470b0e66514d87fcb6967fd7197c90f3d1587ea223e580aa6170 | §7显式modelType，不沿deflectometry默认 |
| [set_structured_light_model_param](../../../halcon算子手册/operators/set_structured_light_model_param.html) | 898dddd8137f941ec78c0ae187886ac954abd455d06183dc4d98962afc2618be | 参数范围、变更清结果、persistence |
| [get_structured_light_model_param](../../../halcon算子手册/operators/get_structured_light_model_param.html) | 25f591112c7df562be77885b32eb3718966fd4f19b1af7ea7392ec5a89bacd5d | 参数回读，不是物理投影确认 |
| [gen_structured_light_pattern](../../../halcon算子手册/operators/gen_structured_light_pattern.html) | 18d525eeb3fb1475afb1aea1cf9473dc35de5a8cf471a7c3e9c073f8678cb948 | 完整normalization/Gray/phase/single-stripe组、4phase/方向 |
| [decode_structured_light_pattern](../../../halcon算子手册/operators/decode_structured_light_pattern.html) | 6647813490fb72589068375f1ce21cd9639b147467555588921c71c044e70c6c | IM-032完整数组/模型串行；非本模块第二实现 |
| [get_structured_light_object](../../../halcon算子手册/operators/get_structured_light_object.html) | 058227815d2bd5e50f9cf7bd91652f6b19e6b1e93a434bcf7f1aa31bbf012b31 | diagnostic persistence及deflectometry-only Defect |
| [clear_structured_light_model](../../../halcon算子手册/operators/clear_structured_light_model.html) | 6e82afaf0559b8d1278233118f5b5c4d40cfe4a4deaa1364590b312767b7266a | 排空后清理；不跨Owner共享handle |
| [reconstruct_surface_structured_light](../../../halcon算子手册/operators/reconstruct_surface_structured_light.html) | 86e3ebf6dd45e4348ea34dc5914097159ad17b1571a5dba561d55e7b0bd16b75 | non-specular/vertical；IM-032执行，无效域不填0 |
| [count_obj](../../../halcon算子手册/operators/count_obj.html) | 31cb3e6ee59a74e107689dcaae58c78a99728ee35bdc6da0b52163f133e5d8c9 | §7.4真实tuple数量，不截断 |
| [select_obj](../../../halcon算子手册/operators/select_obj.html) | 7b5488807ee20f0aec05f46fecb9ed432360a714f85700f5231cadc7590dc77d | §7.4一基index、借用引用不复制，pointer有效期 |
| [get_image_size](../../../halcon算子手册/operators/get_image_size.html) | 9f9dfacddacf8cea96986fe2478e84e139a15e944aac2c7720be7020db0d4d78 | §7.4原W/H |
| [get_image_type](../../../halcon算子手册/operators/get_image_type.html) | e1d0eb3106ecc726f03493acd2ab860e5e254f248ae96697cda51d2ac857d7ec | §7.4单通道byte出口，非原生uint2 |
| [count_channels](../../../halcon算子手册/operators/count_channels.html) | 27f21bc0e0589ef514da1c2b94059912d64125b09d75fe527229a80ab6d888ce | §7.4只接受1 channel |
| [get_image_pointer1](../../../halcon算子手册/operators/get_image_pointer1.html) | 720f3d922e81b12d27615a17e2744fcb7b449c6db78b3ad78c957bac44b9ba35 | §7.4row-major完整byte，只读copy且必须image存活，不跨DTO传指针 |
| [Structured Light章节](../../../halcon算子手册/operators/toc_inspection_structuredlight.html) | dc0785ba201f9a647cb7ffdac822d6a384830b058b79ba7366aacd18435a640a | 显式生成/保持完整数组；未提供对象角色索引API，不从默认/图片推断量测资格 |

### 16.3 外部实现/测试研究（只借思想）

OpenCV opencv_contrib 4.12.0固定commit `d943e1d61c8bc556a13783e1546ee7c1a9e0b1cf`；实际读源码/测试，不凭README或stars。下表路径均相对[固定源码树](https://github.com/opencv/opencv_contrib/tree/d943e1d61c8bc556a13783e1546ee7c1a9e0b1cf/modules/structured_light)。根LICENSE Apache-2.0；所读老源/测试有原BSD三条款风格文件头，若未来复制须逐文件保留/核对；本轮未复制代码/引入OpenCV。

| 路径 | SHA256 | 可借鉴 / 明确局限 |
|---|---|---|
| src/graycodepattern.cpp | eb2840559d4ee81d49a589376f8f0e2c8760bda3bd86e0630879d5ce145e2a7e | 正反图/black-white/越界拒识；两相机rectified、索引/缺域及大bucket内存假设，不能替代事务/安全 |
| src/sinusoidalpattern.cpp | cce9bb6189e6eac13b01f9e29353bddfcaebe4e966fa28138f146b223e1e13ff | PSP/FTP/FAPS研究对照，不替代HALCON路线 |
| test/test_getProjPixel.cpp | 846a2937852a009e124f95f37ef1aadb1e248f520cdddf15b7cb6734a3b441b0 | 合成图案逐像素坐标往返思想；非实际光学 |
| test/test_faps.cpp | 07567f20166736fb68702fd85720baedd4cc5f15d51193e504979b5e2a4211bc | phase测试结构；有符号平均/整数除法不足，不复制其通过判据 |
| test/test_plane.cpp | d1baeade13b44e11fa9c33db59c98b46620637b267653e5470ac3fbc1652cd40 | 公开plane数据端到端思想；3mm阈值不是本设备标准 |
| misc/python/test/test_structured_light.py | 6c40683362de4f9c8d234ec42d58888cb3b71e0eda01c338cf9c2244692abd45 | 有符号phase差平均会正负抵消；§7/11用circular abs/RMS/max与域 |
| CMakeLists.txt | b94fff5b53d627d4e04fe0f5417a178a1d2a3a21db590770affc662b9be4f2d8 | core/imgproc/calib3d/phase_unwrapping，optional viz；不为本模块引该依赖 |

### 16.4 DevExpress 25.2 官方 API 研究

已通过官方网页实际读取25.2页面；本环境没有可调用dxdocs或匹配专用WPF技能，因此使用以下版本化官方页面。页面可能显示后续25.2维护包，不能据此升级本机25.2.3；只采已查公开成员，目标本机消费者编译/实窗留§15。
- [DockLayoutManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Docking.DockLayoutManager?v=25.2)：布局/MVVM/保存恢复，采纳§10。
- [GridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.GridControl?v=25.2)、[TreeListView](https://docs.devexpress.com/WPF/DevExpress.Xpf.Grid.TreeListView?v=25.2)：ItemsSource/View、虚拟化、KeyFieldName/ParentFieldName。
- [PropertyGridControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.PropertyGrid.PropertyGridControl?v=25.2)：SelectedObject、类别/搜索/显式属性定义。
- [ChartControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Charts.ChartControl?v=25.2)：XYDiagram2D、Series数据绑定。
- [SuperTip](https://docs.devexpress.com/WPF/DevExpress.Xpf.Core.SuperTip?v=25.2)：BarItem.SuperTip与普通控件SuperTipControl不同接法。
- [FlyoutControl](https://docs.devexpress.com/WPF/DevExpress.Xpf.Editors.Flyout.FlyoutControl?v=25.2)：IsOpen/StaysOpen/PlacementTarget、FlyoutSettings；仅非关键解释。
- [BarManager](https://docs.devexpress.com/WPF/DevExpress.Xpf.Bars.BarManager?v=25.2)：legacy说明，优先ToolBarControl/StatusBarControl。
- [.NET 10 WPF WriteableBitmap.WritePixels](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.imaging.writeablebitmap.writepixels?view=windowsdesktop-10.0)、[PixelFormats.Pbgra32](https://learn.microsoft.com/en-us/dotnet/api/system.windows.media.pixelformats.pbgra32?view=windowsdesktop-10.0)：本轮直接读取公开Array/stride/offset重载与8-bit BGRA预乘alpha语义，§10.4固定托管显示副本，不从IntPtr借用native显示。


## 附录 A：Slice-0 Managed Core API Contract v0.2

以下为拟实现公开声明，不是已编译代码；记录类型可直接按此形状实施。构造记录不代替Validate；输入必须由安全factory复制可变字节源。静态入口签名见声明表，禁止同时保留旧Validate(plan)或Simulator.Run入口。公开字段名/次序是§3.1 canonical的一部分；命名空间 `Asun.Modules.StructuredLight`。

```csharp
using System.Collections.Immutable;
using System.Threading;

namespace Asun.Modules.StructuredLight;

public enum PixelFormat { ByteGray = 1, UInt16Gray = 2 }
public enum PatternRole
{
    NormalizationBlack = 1, NormalizationWhite = 2,
    Gray = 3, GrayInverted = 4, Phase = 5, SingleStripe = 6, Custom = 7
}
public enum PatternDirection { None = 0, Vertical = 1, Horizontal = 2 }
public enum ContentIntegrity { ReferenceOnly = 1, Verified = 2 }
public enum CoreStatus { Valid = 1, Rejected = 2, Cancelled = 3 }
public enum CoreError
{
    EmptyInput = 1, InvalidValue = 2, IdentityConflict = 3,
    ReferenceMissing = 4, BudgetExceeded = 5,
    UnsupportedPlanShape = 6, ContentMismatch = 7,
    SequenceIncomplete = 8, OperationCancelled = 9
}
public sealed record Issue(CoreError Code, string Path, string DetailKey);
public sealed record PatternArtifact(
    string PatternId, string Version, string GeneratorId, string GeneratorVersion,
    int Width, int Height, PixelFormat PixelFormat, long ByteLength,
    string ContentSha256, PatternRole Role, PatternDirection Direction,
    int? PhaseIndex, double? PhaseRadians, double? SpatialFrequency,
    double IntensityScale, ImmutableArray<byte> Content);
public sealed record ProjectionStep(
    int Ordinal, string StepId, string PatternId,
    string PatternHash, string ExposureRole);
public sealed record ManagedPatternPlan(
    string ContractVersion, string SequenceId, string SequenceVersion,
    ImmutableArray<PatternArtifact> Patterns, ImmutableArray<ProjectionStep> Steps);
public sealed record PlanningLimits(
    int MaxWidth, int MaxHeight, int MaxPatterns, int MaxSteps,
    int MaxIssues, int MaxEvents, long MaxPatternBytes, long MaxWorkingBytes);
public sealed record PatternIntegrity(string PatternId, ContentIntegrity Integrity);
public sealed record ResourceEstimate(long PatternBytes, long ChargedWorkingBytes);
public sealed record ValidationReport(
    CoreStatus Status, ImmutableArray<Issue> Issues, bool IssueLimitReached,
    ImmutableArray<PatternIntegrity> Integrity, ResourceEstimate? Resources);
public sealed record ProjectionPlan(
    string ContractVersion, string SequenceId, string SequenceVersion,
    ImmutableArray<PatternArtifact> Patterns, ImmutableArray<ProjectionStep> Steps,
    PlanningLimits Limits, string PlanSha256,
    ImmutableArray<PatternIntegrity> Integrity, ResourceEstimate Resources);
public sealed record PlanningResult(
    CoreStatus Status, ProjectionPlan? Plan, ValidationReport Validation);

public enum SimulatorFault
{
    None = 0, MissingStep = 1, DuplicateStep = 2,
    OutOfOrder = 3, Timeout = 4, ResourceRejected = 5
}
public sealed record SimulatorOptions(
    long StepTicks, int MaxEvents, SimulatorFault Fault, int? FaultOrdinal);
public enum SimulatorEventKind
{
    PlanStarted = 1, StepPlanned = 2, PlanCompleted = 3,
    PlanRejected = 4, PlanTimedOut = 5, PlanCancelled = 6
}
public enum SimulationStatus
{
    Completed = 1, Rejected = 2, TimedOut = 3, Cancelled = 4
}
public sealed record SimulatorEvent(
    int EventOrdinal, long SimulatedTicks,
    SimulatorEventKind Kind, int? StepOrdinal);
public sealed record SimulatorRunResult(
    SimulationStatus Status, string PlanSha256,
    ImmutableArray<SimulatorEvent> Events, ImmutableArray<Issue> Issues);
```

静态方法的完整拟实现签名（声明表，非方法实现）：

| 所属公开静态类 | 唯一方法签名 |
|---|---|
| StructuredLightPlanner | `ValidationReport Validate(ManagedPatternPlan plan, PlanningLimits limits, CancellationToken ct)` |
| StructuredLightPlanner | `PlanningResult Plan(ManagedPatternPlan plan, PlanningLimits limits, CancellationToken ct)` |
| StructuredLightSimulator | `SimulatorRunResult Simulate(ProjectionPlan plan, SimulatorOptions options, CancellationToken ct)` |

不提供省略limits/ct的默认重载；ct不取消时caller传CancellationToken.None。plan/limits/options运行时null也返回EmptyInput，不NullReference；仅进程级无法恢复故障不保证转为业务报告。ValidationReport.Valid才有完整Integrity/Resources；Rejected可返回已确定的Resources或null，Cancelled不返回未完成Integrity。PlanningResult.Status必须等于Validation.Status；非Valid时Plan=null。输出集合不为default，成功Issues为空；所有字符串不可为空（DetailKey为资源键）。

ProjectionPlan虽公开record可被caller构造/with修改，任何消费入口都重验结构/canonical hash和资源账；不得把类型名当验证凭证。ReferenceOnly与Verified相同元数据/内容hash得到相同PlanSha256，但Integrity不同；包含verified bytes的plan仍不证明实际投影。Core输出无device/Actual/trigger/native类型。

MaxEvents计算：正常N+2；Missing=N+1；Duplicate=N+3；OutOfOrder=N+2；Timeout=FaultOrdinal+2；ResourceRejected=2。模拟前要求该数<=options.MaxEvents且<=plan.Limits.MaxEvents，ticks乘法不溢出；错误fault输入无事件。取消返回PlanCancelled仅在预留事件容量内，替换原预计尾事件而非超限追加，已发计划步前缀保留；SimulatorRunResult.Status=Cancelled。验证完成前取消可零事件；从不标PlanCompleted。

为避免报告消费者歧义，CoreError与设备SL错误是两层：Core只产上列枚举/资源键；Projection把其映射SL-VAL/SL-PAT/SL-RES并保留原Issue.Path，不让设备错误反向进入Core。Slice-0无时间期限参数，因为纯有限计算通过资源预算/ct停止；Timeout只属于确定性模拟故障，不是实际clock期限。

### A.1 SL-C04 固定 canonical 向量

这是纯托管合同的合成算例，不证明光学/设备/性能资格。输入为一个最小2×2 ByteGray artifact、两个不同step复用同一artifact。下列C#仅完整表达DTO输入，不是产品实现；除显式的Content.IsDefault外没有省略字段或隐含limits。

```csharp
var plan = new ManagedPatternPlan(
    ContractVersion: "0.2.0",
    SequenceId: "q",
    SequenceVersion: "1.0.0",
    Patterns: ImmutableArray.Create(new PatternArtifact(
        PatternId: "p",
        Version: "1.0.0",
        GeneratorId: "g",
        GeneratorVersion: "1.0.0",
        Width: 2,
        Height: 2,
        PixelFormat: PixelFormat.ByteGray,
        ByteLength: 4L,
        ContentSha256: "df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119",
        Role: PatternRole.Custom,
        Direction: PatternDirection.Vertical,
        PhaseIndex: null,
        PhaseRadians: null,
        SpatialFrequency: null,
        IntensityScale: 1.0,
        Content: default(ImmutableArray<byte>))),
    Steps: ImmutableArray.Create(
        new ProjectionStep(
            Ordinal: 0, StepId: "s0", PatternId: "p",
            PatternHash: "df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119",
            ExposureRole: "e"),
        new ProjectionStep(
            Ordinal: 1, StepId: "s1", PatternId: "p",
            PatternHash: "df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119",
            ExposureRole: "e")));
var limits = new PlanningLimits(
    MaxWidth: 2, MaxHeight: 2, MaxPatterns: 1, MaxSteps: 2,
    MaxIssues: 8, MaxEvents: 8,
    MaxPatternBytes: 4L, MaxWorkingBytes: 16384L);
```

上述Content为default，校验/规划状态Valid、Issues空、IssueLimitReached=false，Integrity为p/ReferenceOnly。独立内容证据为四个bytes `00 00 00 00`，其SHA256正是上述ContentSha256；把唯一artifact.Content改成 `ImmutableArray.Create<byte>(0, 0, 0, 0)` 后重算，Integrity为p/Verified，canonical与PlanSha256仍完全相同。不允许用空的非default集合替代这两个状态。PatternBytes=4；所有输入字符串UTF8 byte总数=223（三个64字符hash各计一次），ChargedWorkingBytes=4096+1024+1024+4096+1024+892=12156，因此上述预算合法。ContentSha256/两个PatternHash各自改成大写或混合大小写也必须通过，输出三个字段仍全部小写；输入对象文本不被原地改写。

下表覆盖完整规范流，offset从0计，按行顺序连接hex就是全部bytes；hex列无长度前缀省略、无占位符。Domain为15bytes含末尾00；所有hash段为32原始bytes。总长度 **289 bytes**，末项覆盖offset281..288；Content/Integrity/ResourceEstimate不是canonical字段。

| Offset | Bytes | 字段 | 完整hex |
|---:|---:|---|---|
| 0 | 15 | Domain | `4153554e2d534c2d504c414e2d3200` |
| 15 | 9 | ContractVersion | `05000000302e322e30` |
| 24 | 5 | SequenceId | `0100000071` |
| 29 | 9 | SequenceVersion | `05000000312e302e30` |
| 38 | 4 | Patterns.Count | `01000000` |
| 42 | 5 | Patterns[0].PatternId | `0100000070` |
| 47 | 9 | Patterns[0].Version | `05000000312e302e30` |
| 56 | 5 | Patterns[0].GeneratorId | `0100000067` |
| 61 | 9 | Patterns[0].GeneratorVersion | `05000000312e302e30` |
| 70 | 4 | Patterns[0].Width | `02000000` |
| 74 | 4 | Patterns[0].Height | `02000000` |
| 78 | 4 | Patterns[0].PixelFormat | `01000000` |
| 82 | 8 | Patterns[0].ByteLength | `0400000000000000` |
| 90 | 32 | Patterns[0].ContentSha256 | `df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119` |
| 122 | 4 | Patterns[0].Role | `07000000` |
| 126 | 4 | Patterns[0].Direction | `01000000` |
| 130 | 1 | Patterns[0].PhaseIndex | `00` |
| 131 | 1 | Patterns[0].PhaseRadians | `00` |
| 132 | 1 | Patterns[0].SpatialFrequency | `00` |
| 133 | 8 | Patterns[0].IntensityScale | `000000000000f03f` |
| 141 | 4 | Steps.Count | `02000000` |
| 145 | 4 | Steps[0].Ordinal | `00000000` |
| 149 | 6 | Steps[0].StepId | `020000007330` |
| 155 | 5 | Steps[0].PatternId | `0100000070` |
| 160 | 32 | Steps[0].PatternHash | `df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119` |
| 192 | 5 | Steps[0].ExposureRole | `0100000065` |
| 197 | 4 | Steps[1].Ordinal | `01000000` |
| 201 | 6 | Steps[1].StepId | `020000007331` |
| 207 | 5 | Steps[1].PatternId | `0100000070` |
| 212 | 32 | Steps[1].PatternHash | `df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119` |
| 244 | 5 | Steps[1].ExposureRole | `0100000065` |
| 249 | 4 | Limits.MaxWidth | `02000000` |
| 253 | 4 | Limits.MaxHeight | `02000000` |
| 257 | 4 | Limits.MaxPatterns | `01000000` |
| 261 | 4 | Limits.MaxSteps | `02000000` |
| 265 | 4 | Limits.MaxIssues | `08000000` |
| 269 | 4 | Limits.MaxEvents | `08000000` |
| 273 | 8 | Limits.MaxPatternBytes | `0400000000000000` |
| 281 | 8 | Limits.MaxWorkingBytes | `0040000000000000` |

基准PlanSha256：`8dcc9fa0b04e05103ed0446a9cae3caa89cafa32fba267f87ac0093e2c4803ae`。

本轮用Python标准库struct的逐字段LE编码+hashlib，与独立PowerShell/.NET BinaryWriter的请求值编码+SHA256.HashData复算；两条路径均从上述输入建立bytes，未调用产品Planner，也未用基准hex作为第二条路径的输入。完整289bytes、基准hash及以下两个合法变体hash逐一相同。这只核固定向量，C#产品实现/SL-C04 harness尚未执行；未来测试以这里的字面hex/hash为oracle，不能调用受测编码器生成预期值。

| 改动（其它字段完全沿基准） | 校验/规划预期 | PlanSha256 |
|---|---|---|
| limits.MaxWorkingBytes从16384改为16385 | Valid；资源账仍12156，但limits是身份的一部分，必须新hash | `76d5a6316ac872063f017dc86f5ef19e101bc763a9fdb418f819e0c1241b6b29` |
| 把Steps数组两项直接互换，保留原Ordinal=1/0 | Rejected：数组位置与Ordinal不连续；Plan=null，不生成新hash，不自动排序 | 不存在 |
| 将步序改为先s1后s0，同时分别显式设置Ordinal=0/1 | Valid；两个step仍引用p，合法新步序必须新hash | `74dd64df798a62d698bdb55d3344d032c2594875c40c019a56c27cbe5e094804` |
| limits.MaxPatternBytes从4改为3 | BudgetExceeded / Rejected；不生成plan，不返回部分hash | 不存在 |
| limits.MaxWorkingBytes从16384改为12155 | BudgetExceeded / Rejected；12156超过上限 | 不存在 |

step顺序参与身份；同pattern被多个step复用不改变该原则。Pattern目录则先按PatternId Ordinal排序：多artifact合法计划只改变输入目录排列、其字段及引用不变时，canonical/hash不变。本向量只有一个artifact，不声称已覆盖多artifact排序测试。正常/limits+1/重新编号后步序互换三组规范字节差异均有唯一预期，不能以“结果等价”免除hash变化断言。

## 附录 B：Slice-2 Vision 完整托管声明 v0.2

本附录替换旧字段名表。namespace为Asun.Modules.StructuredLight.Vision；Core图案类型引用附录A，跨切片值/clock/drain/issue引用附录C的Projection纯托管值，不引用设备SDK、不创建session。AsunImage实现另包；宿主按B.4消费已接收IM-032/image-quality公开API并实现这里的适配，不猜未覆盖字段或共同标定资产API。

### B.1 类型和公开入口

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.StructuredLight;
using Asun.Modules.StructuredLight.Projection;

namespace Asun.Modules.StructuredLight.Vision;

public enum StructuredLightModelType { ThreeDReconstruction = 1, Deflectometry = 2 }
public enum GenerationOrientation { Vertical = 1, Horizontal = 2, Both = 3 }
public enum AlgorithmRoute { Hybrid = 1, GrayOnly = 2, SingleStripe = 3 }
public enum NormalizationMode { Global = 1, InvertedPattern = 2 }
public enum GenerationStatus { Generated = 1, Rejected = 2, Cancelled = 3, DrainUnknown = 4, Released = 5 }
public enum LayerKind
{
    Correspondence = 1, PatternRegion = 2, Phase = 3,
    GrayBinary = 4, GrayCorrespondence = 5, SingleStripe = 6, Defect = 7
}
public enum VisionStatus
{
    Observed = 1, NotObserved = 2, Rejected = 3, Cancelled = 4, DrainUnknown = 5, Released = 6
}
public enum MetricStatus { Observed = 1, NotObserved = 2, NotEvaluated = 3, Rejected = 4 }
public enum LayerPixelType { Byte = 1, UInt16 = 2, Float32 = 3, Float64 = 4, BinaryMask = 5 }
public enum RecommendationStatus { Completed = 1, Rejected = 2, Cancelled = 3, DrainUnknown = 4, Released = 5 }
public sealed record GenerationSpec(
    string ContractVersion, string SequenceId, string SequenceVersion,
    string GeneratorId, string GeneratorVersion, StructuredLightModelType ModelType,
    int Width, int Height, int MinStripeWidth, GenerationOrientation Orientation,
    AlgorithmRoute Route, NormalizationMode Normalization, int? SingleStripeWidth,
    double IntensityScale, AssetRef ProfileRef, AssetRef? CalibrationRef);
public sealed record GenerationLimits(
    int MaxPatterns, int MaxWidth, int MaxHeight,
    long MaxPatternBytes, long MaxWorkingBytes, long MaxNativeBytes, long BudgetNs);
public sealed record GenerateRequest(Guid OperationId, GenerationSpec Spec, GenerationLimits Limits);
public sealed record GeneratedPatternEntry(
    int SourceIndex, string PatternId, PatternRole Role, PatternDirection Direction,
    int? PhaseIndex, double? PhaseRadians, double? SpatialFrequency, string ContentSha256);
public sealed record GenerateReply(
    Guid OperationId, GenerationStatus Status, string SpecHash,
    ManagedPatternPlan? Plan, ImmutableArray<GeneratedPatternEntry> OrderedManifest,
    string? ManifestHash, AssetRef ProfileRef, AssetRef? CalibrationRef,
    ImmutableArray<ModuleIssue> Issues, DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    OperationTombstone? Tombstone);
public sealed record Metric(
    string Name, double? Value, string Unit, long Denominator,
    AssetRef? DomainRef, AssetRef? ThresholdProfileRef, MetricStatus Status);
public sealed record LayerRef(
    AssetRef Asset, LayerKind Kind, int Width, int Height, LayerPixelType PixelType,
    string CoordinateFrameId, string Unit, AssetRef ValidDomainRef,
    ImmutableArray<AssetRef> SourceBindingRefs);
public sealed record ObservationRequest(
    Guid OperationId, string AttemptId, string SequenceHash, ulong Generation,
    string ManifestHash, ImmutableArray<AssetRef> OrderedBindingRefs,
    AssetRef? CalibrationRef, AssetRef ProfileRef, AssetRef RuntimeRef,
    ImmutableArray<LayerKind> RequestedLayers, AssetRef? RoiRef,
    long BudgetBytes, long BudgetNs, bool PersistenceRequested);
public sealed record ObservationReply(
    Guid OperationId, string AttemptId, string SequenceHash, string ManifestHash,
    AlgorithmRoute AlgorithmRoute, string ProducerId, string ProducerVersion,
    AssetRef ProfileRef, AssetRef RuntimeRef, AssetRef? CalibrationRef,
    VisionStatus Status, ImmutableArray<Metric> Metrics, ImmutableArray<LayerRef> LayerRefs,
    ImmutableArray<ModuleIssue> Issues, DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    OperationTombstone? Tombstone);
public sealed record RecommendationCandidate(
    string CandidateId, GenerationSpec GenerationSpec,
    AssetRef DecodeProfileRef, AssetRef MatchedEvidenceSetRef);
public sealed record RecommendationRequest(
    Guid OperationId, AssetRef BaselineProfileRef, AssetRef EvidenceSetRef,
    ImmutableArray<RecommendationCandidate> Candidates,
    int MaxCandidates, int MaxEvaluations, long BudgetNs, long BudgetBytes,
    DateTimeOffset ExpiresAt, AssetRef AcceptanceProfileRef);
public sealed record RankedCandidate(
    string CandidateId, string SpecHash, int? Rank, ImmutableArray<Metric> Metrics,
    bool Eligible, ImmutableArray<string> NotEvaluatedKeys, ImmutableArray<string> RejectKeys);
public sealed record RecommendationReply(
    Guid OperationId, RecommendationStatus Status, Guid? AdviceId,
    string BaselineHash, string EvidenceHash,
    ImmutableArray<RankedCandidate> RankedCandidates, DateTimeOffset ExpiresAt,
    ImmutableArray<ModuleIssue> Issues, DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    OperationTombstone? Tombstone);
public enum VisionOperationKind { Generate = 1, Observe = 2, Recommend = 3 }
public enum VisionOperationPhase { Accepted = 1, Running = 2, Draining = 3, DrainUnknown = 4, Terminal = 5 }
public sealed record VisionOperationSnapshot(
    Guid OperationId, VisionOperationKind Kind, string RequestHash,
    VisionOperationPhase Phase, OperationOutcome? LogicalOutcome,
    OperationOutcome? TerminalOutcome, DrainStatus DrainStatus,
    ResourceStatus ResourceStatus, long StateVersion, ClockStamp ObservedAt,
    ImmutableArray<ModuleIssue> Issues);
public sealed record VisionQueryRequest(Guid OperationId, ClockStamp Deadline);
public sealed record VisionQueryReply(
    QueryStatus Status, VisionOperationSnapshot? Snapshot,
    GenerateReply? Generation, ObservationReply? Observation,
    RecommendationReply? Recommendation, ImmutableArray<ModuleIssue> Issues,
    OperationTombstone? Tombstone, ResultRetentionState RetentionState);
public sealed record VisionCloseRequest(long CleanupBudgetNs, string ReasonKey);
public sealed record VisionCloseReply(
    DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    ImmutableArray<Guid> UnresolvedOperationIds, ImmutableArray<ModuleIssue> Issues);
public interface IStructuredLightPatternGenerator
{
    ValueTask<GenerateReply> GenerateAsync(GenerateRequest request, CancellationToken ct);
}
public interface IStructuredLightObservationPort
{
    ValueTask<ObservationReply> ObserveAsync(ObservationRequest request, CancellationToken ct);
}
public interface IStructuredLightRecommendationService
{
    ValueTask<RecommendationReply> RecommendAsync(RecommendationRequest request, CancellationToken ct);
}
public interface IStructuredLightVisionSession :
    IStructuredLightPatternGenerator, IStructuredLightObservationPort,
    IStructuredLightRecommendationService, IAsyncDisposable
{
    ValueTask<VisionQueryReply> QueryAsync(VisionQueryRequest request, CancellationToken ct);
    ValueTask<RetentionReleaseReply> ReleaseResultAsync(
        RetentionReleaseRequest request, CancellationToken ct);
    ValueTask<RetentionUsage> GetRetentionUsageAsync(CancellationToken ct);
    ValueTask<VisionCloseReply> CloseAsync(VisionCloseRequest request, CancellationToken ct);
}
```

有限托管factory签名 `StructuredLightVisionSession.Create(IStructuredLightGenerationAdapter generator, IManagedObservationAdapter observations, ICandidateEvaluationPort evaluations, IProjectionClock clock, IAdviceClock adviceClock, VisionLimits limits)`→IStructuredLightVisionSession。裸Generate/Observe/Recommend接口是宿主组合端口，不自带隐藏后台服务；具体session承担operation索引、预算/并发/结果copy/恢复查询和Close。Dispose仅在CloseConfirmed/Released后；否则SL-DISPOSE-001且保留原恢复Owner。

### B.2 生成Adapter、候选评估和资源查询

```csharp
public sealed record VisionLimits(
    int MaxOperations, int MaxPatterns, int MaxBindings, int MaxLayers,
    int MaxMetrics, int MaxCandidates, int MaxIssues,
    long MaxManagedBytes, long MaxNativeBytes, long MaxResultBytes,
    long MaxRetainedBytes, long QueryBudgetNs, long CleanupBudgetNs,
    RetentionPolicy Retention);
public interface IAdviceClock { DateTimeOffset UtcNow { get; } }
public sealed record VisionAdapterContext(
    Guid OperationId, string RequestHash, ClockStamp Deadline,
    long MaxManagedBytes, long MaxNativeBytes, long MaxResultBytes);
public sealed record GeneratedPatternPixels(
    int SourceIndex, PatternRole Role, PatternDirection Direction,
    int? PhaseIndex, double? PhaseRadians, double? SpatialFrequency,
    int Width, int Height, PixelFormat PixelFormat, ImmutableArray<byte> Content);
public enum VisionAdapterStatus
{
    Completed = 1, Rejected = 2, Cancelled = 3, DrainUnknown = 4
}
public sealed record GenerationAdapterReply(
    Guid OperationId, VisionAdapterStatus Status,
    ImmutableArray<GeneratedPatternPixels> Patterns, string GeneratorVersion,
    DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    ImmutableArray<ModuleIssue> Issues);
public sealed record VisionAdapterQuery(
    QueryStatus Status, Guid OperationId, DrainStatus DrainStatus,
    ResourceStatus ResourceStatus, ClockStamp ObservedAt,
    ImmutableArray<ModuleIssue> Issues);
public interface IVisionResourcePort
{
    ValueTask<VisionAdapterQuery> QueryDrainAsync(VisionQueryRequest request, CancellationToken ct);
    ValueTask<VisionCloseReply> CloseAsync(VisionCloseRequest request, CancellationToken ct);
}
public interface IStructuredLightGenerationAdapter : IVisionResourcePort
{
    ValueTask<GenerationAdapterReply> GenerateAsync(
        VisionAdapterContext context, GenerationSpec spec, CancellationToken ct);
}
public sealed record CandidateEvaluationRequest(
    Guid OperationId, RecommendationCandidate Candidate,
    AssetRef EvidenceSetRef, AssetRef AcceptanceProfileRef, ClockStamp Deadline,
    long BudgetBytes);
public sealed record CandidateEvaluationReply(
    Guid OperationId, string CandidateId, string SpecHash,
    ImmutableArray<Metric> Metrics, ImmutableArray<string> RejectKeys,
    ImmutableArray<string> NotEvaluatedKeys, DrainStatus DrainStatus,
    ResourceStatus ResourceStatus, ImmutableArray<ModuleIssue> Issues);
public interface ICandidateEvaluationPort : IVisionResourcePort
{
    ValueTask<CandidateEvaluationReply> EvaluateAsync(
        CandidateEvaluationRequest request, CancellationToken ct);
}
public interface IManagedObservationAdapter :
    IStructuredLightObservationPort, IVisionResourcePort { }
```

Create的observations参数为IManagedObservationAdapter，不接受无法查drain的裸接口。端口返图案字节必须为自有ImmutableArray，可直接移交给session；单artifact<=int.MaxValue且checked尺寸/bytes预算先于导出。GenerationAdapterReply.Completed只在全部图案、实际资源drainConfirmed后；native句柄不跨端口。session验证规范化角色/方向/phase/hash并形成GeneratedPatternEntry/ManagedPatternPlan，不相信适配器给的GeneratorVersion与Profile不一致；不支持“部分Completed”。回调迟到或查询DrainConfirmed后才到图案的Adapter是协议违约，session隔离对应operation，结果不能覆盖已固定Cancelled/Rejected。

查询结果/资源由实际端口可查询，不能因为它返回了ValueTask就假定内部工作停止。Vision.Query.Status=Found时Snapshot必填且至多Generation/Observation/Recommendation之一非null、必须匹配Kind；运行中/未知时可均null，最终回执保持原请求身份。不存在/查询不可用返回NotFound/Unavailable，不作无副作用证明。Query不等待新结果，Deadline与limits.QueryBudgetNs取小者；取消不触发第二次Generate/Observe/Evaluate。每operation StateVersion递增；TerminalOutcome只在实际Drained/Released后，逻辑取消可保留LogicalOutcome=Cancelled直到drain确认。迟到结果只归原OperationId，不转给当前选择/新Advice。

生成器、观察器、评估器的出参皆immutable托管值；大LayerRef/AssetRef仅引用宿主已有证据，不通过此端口写产品事实。内部MaxManagedBytes计输入复制/manifest/索引，MaxResultBytes计输出像素/metadata/metrics/引用/错误（单个字符串ASCII ID<=128、DetailKey<=128、NativeCode<=256；其余诊断不放任意文本）；MaxRetainedBytes覆盖可查询结果。所有计数上界必须正且先于copy，检查每集合count；native envelope只能由目标部署Profile冻结，未知上界拒绝真实native，不阻纯端口Simulator。成功前预留结果/操作索引容量，不先返回成功再丢查询。达到MaxOperations/retained上限拒绝新的operation，不逐出未知任务；已终态且caller显式释放consumer引用后经ReleaseResultAsync/C.5压缩为有限墓碑，不能删id/hash去重索引。

operation身份采用固定domain ASUN-SL-VISION-2+VisionOperationKind+请求全部字段按声明顺序，Guid/Clock/Asset沿§3.3/C编码，数组原序；Generate.Limits包含在request hash，但SpecHash不含运行预算。Observation同层请求必须去重且保持caller顺序，不排序假装同请求；重复operationId/同hash回放当前/最终原结果，异hash SL-CON-001无调用。独立客户端的同input不同operation允许并行，但共享同Adapter不能并发同模型；session每Adapter单执行Owner（generate/observe/evaluate各自一个），另operation有界排队，ct/Deadline未接纳就拒绝/取消，已接纳使用独立cleanup。端口请求剩余BudgetNs不可重置为完整预算，推荐多个candidate共享总deadline/bytes余额。

完整hash/结果约束：SpecHash域ASUN-SL-GEN-2+GenerationSpec全部声明字段，ManifestHash域ASUN-SL-MANIFEST-2+SpecHash32bytes+OrderedManifest count/完整entries原序；字段编码沿A/C，所有域末尾单NUL。GeneratedPatternEntry.SourceIndex从1连续，PatternId精确为SequenceId+":p:"+SourceIndex的十进制InvariantCulture无前导零；超128字符拒绝，不截断。对应ManagedPatternPlan.ContractVersion取Spec.ContractVersion，SequenceId/version取Spec，PatternArtifact.Version取SequenceVersion，GeneratorId/version取实际已核生成器，Steps.Ordinal=SourceIndex-1、StepId=SequenceId+":s:"+Ordinal无前导零，ExposureRole="capture"；步骤数等于manifest数且PatternHash按像素digest，角色/phase由已验证生成映射提供，不猜。建议Candidate.SpecHash同此规范，Metadata.Direction/Phase字段不因上传去重而丢失。托管生成/观察/Advice不定义额外回调事件，结果只经Reply/Query传递；UI事件由宿主以D投影，不能建立第二事实链。

所有端口调用期限到时，session可以返回DrainUnknown/进行Query，仍追踪实际未返回Task/输入lease/预算槽直到真实结束；不能通过WaitAsync取消包装器来释放底层工作。底层迟到结果先检查OperationId/RequestHash，处理实际资源归还，再保留原逻辑Cancelled/TimedOut；不返回新Generated或Advice覆盖原终态。无法报告身份/排空的宿主适配器明确拒绝接入，不靠HALCON/SDK名字提供隐含保证。关闭建议分析session不会撤销已外部保存的证据引用；本模块只归还自己取得的工作/显示租约。

### B.3 观察、建议有效性和可重复测试

本版保留状态追加规则：Released并非Generated/Observed/Completed，不套成功大结果的非空集合规则；其Tombstone必填、native工作资源Confirmed/Released、所有大集合空，非nullable纯metadata从C.5固定小头读取。VisionQuery.Status=Released时Snapshot和三种大结果均null、Tombstone必填、RetentionState=Released；Found才有Snapshot、Tombstone=null，Expired只改变保留投影不改业务结果。Generate/Observe/Recommend直接同identity replayReleased返回Released短回执，不返回null hash/原Status伪装正常结果；异hashConflict是明确Issue/no新调用，不能用Released回旧identity的不同请求。

Spec和§7参数完全同域，IntensityScale当前只1；缺共同标定合同/外部资格只能非量测生成或离线诊断，不得填伪CalibrationRef。GenerationStatus.Generated需Plan+ManifestHash完整且Drained/Released，Rejected/Cancelled/DrainUnknown Plan=null；SpecHash对非法Spec无法形成时用空字符串只限Rejected，无合法hash不能执行/持久化为生成事实（不能伪64个0）。

Metric.Name固定接收键：FalseAcceptRate、FalseRejectRate、CircularPhaseMAE、CircularPhaseRMS、CircularPhaseMax、ValidRatio、P50Ns、P95Ns、P99Ns、PeakBytes；扩展键仅同版本Profile明确登记。Observed需Value有限、Denominator>0；率0..1、phase rad>=0、时间ns/bytes>=0；NotObserved/NotEvaluated值为null、Denominator可0且有键原因，禁止NaN。DomainRef对像素metric必填，ThresholdProfileRef对Eligibility的门必填；性能目标未提供为NotEvaluated而非通过。LayerRef的Width/Height正且与绑定/full-frame坐标一致；SourceBindingRefs非空，ValidDomainRef必须存在，不用坐标0或空域代表有效图。ProducerId/version属于实际Owner，不写“结构光模块”冒充IM-032事实Owner。

Advice排序仅Eligible且必要metrics齐全的candidate按§7.3排序；Rank从1连续，不Eligible的Rank=null，按CandidateId Ordinal附尾。所有candidate至少得一个RankedCandidate，缺证据/预算/取消不能悄悄少项。一次candidate Evaluate不可隐式获取新图/重拍；参数与MatchedEvidenceSetRef不兼容则RejectKeys明确。不合资格样本不得补0误差。AdviceId只有完整评估/释放且至少一个Eligible才非null；Completed只表示离线分析完成，不作生产值。过期由IAdviceClock.UtcNow和ExpiresAt校验，UTC变化不会影响native运行Deadline；期限过去或Evidence/Profile/设备/标定变动后UI和宿主同时标Stale。

ICandidateEvaluationPort由宿主接外部真值/资格Profile Owner，负责按请求AcceptanceProfileRef解析阈值、分母/共同域和每个质量门，输出RejectKeys/NotEvaluatedKeys及带精确ThresholdProfileRef的Metrics；本模块不自行读取未声明的Profile私有表或猜标准。session核对候选ID/SpecHash、全部必要10项metric名称无重复、阈值ref与请求一致及数值有效域，且RejectKeys/NotEvaluatedKeys均空才Eligible；不能以端口Status或“测量值有了”代替门结果。请求Profile没有相位门（如GrayOnly）时端口须明确NotEvaluated，当前通用推荐器不排名为Eligible；Gray-only生产资格仍宿主批准路线，不借Advice强行补0相位误差。session排序只是确定性Advice，端口需要真实数据/下游公开接口绑定才可宣称算法资格。

托管最小Host用有界假Adapter提供明确标Synthetic的2×2像素、绑定refs/metrics和可控QueryDrain；验证接口/拒绝/资源协议，不把这些当HALCON图案。真实gen形态/4phase/manifest映射仍§7/15真实适配门。观察器缺相位/光学数据返回NotObserved，不伪造Observed；查询/Close在DrainUnknown时返回UnresolvedOperationIds全量（count<=MaxOperations）、Held，Deadline过了仍保留恢复Owner。Close确认释放全部操作/输入显示引用后才Released，RepeatedClose按相同状态回执且无第二native调用；Dispose不能绕过Close。


### B.4 下游公开消费桥（2026-10-11，已支持范围指导内容限定接收）

本节只规定宿主对B.2 `IManagedObservationAdapter` / `ICandidateEvaluationPort` 的实现接线，不复制质量、解码、相位或重建算法，不转移生产事实Owner。只读基线是[image-quality 0.6.0-prep §16.2–16.11/§20.5/§24.3](../image-quality/DEVELOPMENT-GUIDE.md)（Service/Core+Simulator已接收，源SHA256 `70f031c3c3a5bb37c7e54508c13f3f7b16e44c3d7579af9cb1a6f748526aa873`）及[reconstruction-3d 0.2.5-prep §4–5/§8/§13.4–13.7](../reconstruction-3d/DEVELOPMENT-GUIDE.md)（Core/发布Simulator已接收，源SHA256 `45a2abfacaa0f1d7e8ee5507a5f1e6d09d5a2bf24fc1a4ed583b05d7b8b9bfa6`）。它们的公开声明是应实现合同，不声称DLL已存在/编译/运行。calibration-assets 0.3.1-prep §7.4 Joint API v1已接收（源SHA256 `a97e77afad585eb6c0f4f918f4fc34faba4aade26d2650cc6dd7722b00c75ca2`），本模块消费见B.4.6；首次decode-only源规格现已接收，新增精确消费见B.4.6.6；CAL 0.3.2-prep §7.4.6B正式资格技术绑定/版本域源桥已限定接收，本地消费见B.4.6.7（资格绑定消费增量已获主控限定内容接收，2026-10-11），相关真实重建仍不因指导新增而运行。无关托管原帧诊断/请求/Simulator仍可验证。

消费桥是未来宿主的本地组合，namespace引用 `Asun.Modules.ImageQuality`、`Asun.Modules.Reconstruction3D`，模拟Host另引用 `Asun.Modules.Reconstruction3D.Simulation`。Vision端口包不增加两个算法实现包依赖；示例未来只放binding指定Vision.Tests/Hosts，产品接入由宿主承担，不新增桥模块、恢复服务API、数据库Schema或本轮工程。下面的“消费清单/根槽”是显式传给本地adapter构造闭包的不可变值及Owner责任，没有公共resolver、私表或global latest。

#### B.4.1 原帧、manifest、域和Profile展开

| 有界清单输入 / 原Owner | 必须提供及逐项映射 |
|---|---|
| GenerationSpec/GenerateReply/投影sequence / IM-011 | 原SpecHash、ManifestHash、OrderedManifest、ManagedPatternPlan及冻结ProjectionSequence；SourceIndex1..N→step ordinal0..N−1，PatternId/角色/方向/phase/hash一致。Observation.SequenceHash仍设备冻结sequence hash，Generation仍其代次，不能用PlanSha256/ManifestHash代替 |
| OrderedBindingRefs / 采集及证据Owner | 每binding的原AssetRef、FrameId、实际载荷RevisionRef、只读原Bytes/RowStrideBytes、ValidityMask、相机W/H/格式、DirectionId/CameraIndex、曝光/运动/投影/辐射/坐标revision、完整FrameTiming及原Actual稳定窗/同步时钟证据（fixture仅synthetic）；同attempt/epoch/物件关联，严格manifest原序等长一一对应。缺/重复/跨attempt/原hash改变副作用前拒绝，不按文件名/到达顺序重排或拼帧 |
| RoiRef / 原ROI Owner | 原幅PixelRoi、CoordinateRevision及矩形请求域AssetRef。null为全相机域；本桥只接受矩形ROI，额外前景/排除域mask在现QualityServiceRequest中无字段，明确拒绝，不把它写入原帧ValidMask；转QualityBox(Row,Column,checked(Row+Height),checked(Column+Width))半开框，不crop/scale/压缩有效点，不改原W/H/stride；不同源域/坐标或框外拒绝 |
| ProfileRef / 消费实验Profile Owner | 完整QualityServiceRequest的Methods/Policy/区域和预算，完整Decode PatternSpec/ReconstructionParameters、固定质量支持或表面支持用途、原domain ref、期望RuntimeRevision/包版本。普通程序员不选阈值/算法/用途，不取HALCON默认或最近Profile；Quality Policy只工程可观测性，不授质量PASS |
| CalibrationRef / calibration-assets与资格Owner | 原JointUse/JointPublishedRef/JointQualifiedRef/JointSetupExport完整保留并按B.4.6只读核验；不把普通相机asset当共同标定。Joint源Revision原string不改；按已接收CAL §7.4.6B和本地B.4.6.7取得完整快照技术指纹/桥包SemVer及伴随记录（资格绑定消费增量已获主控限定内容接收，2026-10-11），缺来源关联/伴随快照拒绝组装。Synthetic只CalibrationReplay，不交真实AsunImage |
| RuntimeRef / 部署Owner | 原asset对应实际QualityServiceReport.RuntimeRevision及IM-032部署包/adapter身份文本；精确核对，不从字段截取猜版本或把HALCON版本当全部runtime |
| Candidate.MatchedEvidenceSetRef/DecodeProfileRef、EvidenceSetRef、AcceptanceProfileRef / 证据及资格Owner | 显式成员列表、同生成spec/manifest/原帧/ROI/设备/曝光/runtime，原真值标签/分母、有限样本计划、metric阈值/测点/来源。缺项NotEvaluated，不能新造质量标签、设备命令或工艺放行 |

AssetRef只有Id/Version/Sha256，不编码路径；所有ref先由原Owner核验再展开。映射到IM-032 RevisionRef(Id,Sha256)时Version在原消费清单同时留存并核验，不能丢版本后单靠相等hash判断适用。真实源原字节/validmask只读；物理借读由原帧Owner提供，copy/hash前后查同revision/当前性，Changed整次失败，不替换为最近源。Quality可限额复制为自有QualityMemorySource，原借读直到该次复制/hash退出才归还；仍给IM-032使用的原帧保持至其lease真实排空。自有copy归桥预算，不声称零复制。memory-port.CheckCurrent=Current只证明快照不可变，不能代原设备/采集来源证据。

原pixel坐标不变；角度、NativeLengthToMm及world frame只来自已发布原合同，不能从图案Vertical/Horizontal或数值大小推断。Quality组依据包括原曝光/Projection/ObservationGroup/Motion修订及来源，不用同名字串自证物理静止；fixture的这些声明均标synthetic。

#### B.4.2 image-quality 完整装配、请求与结果

唯一公开调用链是 `QualityHostLifetimeRoot.Reserve(slotId,reservedBytes)` → `slot.ConstructAsync` → `IImageQualityService.Validate` → `slot.Start` → 原 `slot.OriginalCompletion`（必须ReferenceEquals原Operation.Completion）。ConstructAsync两显式lambda为 `ImageQualityMemoryInputFactory.Create(inputProfile,sources,clock,instanceLimits)` 和 `ImageQualityManagedVisualFactory.Create(visualProfile,clock,instanceLimits)`，它内部唯一调用 `ImageQualityServiceFactory.Create(input,visual,clock,instanceLimits)`。需要既有HALCON路线时第二lambda明确改成 `Asun.Modules.ImageQuality.AsunImage.ImageQualityAsunImageFactory.Create(clock,instanceLimits)`，不改Service/事实Owner；实际native系数/运行另验。托管visual只支持RawStatistics/StructuredGroupSupport，不伪造Sobel/Noise。

| 完整DTO字段 | 接线规则 |
|---|---|
| QualitySourceRef / QualitySourceDescriptor | SourceId=FrameId、Revision=清单核定原载荷revision；Kind按确为RawAcquisition/Derived/ImportedFile，派生ParentRevision必留；PlaneId原通道、PixelType实际UInt8/UInt16/Float32、WidthPx/HeightPx原相机。CoordinateRevision、ParentRevision、ObservationGroupRevision、StepIndex、ExposureRevision、MotionRevision、ProjectionRevision、RadiometricRevision、AcquisitionUtc、ImportUtc、EffectiveBitDepth、BlackLevel、WhiteLevel逐项原值，未观测可空项仍null |
| QualityMemorySource | Samples/ValidMask长度恰原W×H，按原stride/明确字节序逐行无损承载，不归一化、不转8bit；UInt16整数范围/Float32有限且可精确回转，未知格式/stride/hash拒绝。仅复制像素，不在桥实现质量算子 |
| QualityInput / QualityRegionSpec | RoleKey="step-"+原manifest ordinal，Source原ref；RegionKey来自Profile，Bounds原ROI半开框，各依赖源同坐标/同框，mask原位置保留 |
| QualityMethodPlan | MethodKey/Revision/RegionKey/RoleKey/Route/具体Parameters/Policy/Required逐项取Profile；RawStatistics为QualityRawParameters(完整ManagedQualityMethodSet)。Group为QualityGroupParameters(完整OrderedRoleKeys,OrderedStepIndices)，按manifest序，不以Inputs到达序猜角色。参数非法拒绝，缺可观测依据保留NotObservable |
| QualityServiceRequest / QualityBudget | 独立不复用RequestId与SL原OperationId在根槽关联，ApiVersion="image-quality-service-v0.1"，Inputs/Regions/Methods为非default ImmutableArray；ManagedBytes/NativeBytes/MaxReadPixels/MaxOutputBytes/MaxDuration/DeadlineUtc及TileWidthPx/TileHeightPx全部显式且不超父剩余。不为各method重置总deadline |
| QualityOperationResult / Report | 原State/Report/Issue、GetSnapshot.Drained/ResourcesReleased、Sources/Methods/Observations/RuntimeRevision/PeakManagedBytes/PeakNativeBytes/ReadPixels核对；QualitySupport.RequestedPixels/ValidPixels/CenterPixels/Bounds/CoordinateRevision/Model原样。Computed须完整封闭键，CompletedWithUnavailableMetrics不能当全部Required有值 |

group Computed时 `commonValidFraction` / Fraction映射成B `Metric("ValidRatio",value,"fraction",Support.RequestedPixels,qualityDomainRef,null,Observed)`；denominator原ROI请求数，域为**原像素共同支持**，不能改名phase精度/表面覆盖。requiredSteps从原Methods的OrderedRoleKeys/OrderedStepIndices读取，presentSteps仅取原完整组Computed的Count键（缺组不补造）；原RawValues保留在quality原报告，不能映射成FalseAccept/误差/mm不确定度。缺step直接Quality调用可NotObservable/StepMissing，B完整组前检应先拒绝，不把部分输入当完整Observation。

质量用途ObservationReply：原B身份/AttemptId/SequenceHash/ManifestHash/ProfileRef/RuntimeRef，CalibrationRef=null，AlgorithmRoute原generation route（只是图案来源，不称quality已解码），ProducerId="image-quality"、ProducerVersion=Report.ModuleVersion；Observed须至少一个明确Observed metric和Required group可用，LayerRefs.Empty且RequestedLayers须Empty。合法缺依据→NotObserved/metric.Value=null，provider故障保留错误，不用0或空数组冒充合格；report的Support/来源仍由image-quality拥有。

#### B.4.3 IM-032 全请求、支持域与出参

装配入口 `new ReconstructionFactory().Create(new ReconstructionPorts(Frames,SurfaceInputs,CalibrationAssets,StructuredLight,Stereo,Surface,Transform,Clock,Diagnostics))`。本桥真实结构光用途是IFrameSource/ICalibrationAssetSource/IStructuredLightEngineAdapter三端口，SurfaceInputs/Stereo/Surface=null；单方向源world AlreadyInOutput/count0时Transform=null/DirectionTransforms=null/Fusion=null。不估计多方向角度/矩阵，不将图案Both拆成两个物理方向；ApplyPublished必须另消费IM-033完整已发布快照，不能暗乘identity或scale。

| 完整请求 | 固定映射与校验 |
|---|---|
| ReconstructionRequest | ApiVersion=ReconstructionFactory.ApiVersion="0.2"，OperationId/CalculationId两个独立字符串预登记、永久不复用，Input/Parameters/Fusion如下，Deadline不晚于B父截止，AuthorityScope原授权 |
| FrameRef / DirectionCapture | FrameId/Revision原binding，Gray→SampleKind.GrayCode、GrayInverted→GrayCodeInverted、NormalizationBlack/White→同名SampleKind、Phase→PhaseShift、SingleStripe→SingleStripe；新增角色必须opt-in B.4.7完整Sequence；原camera W/H，光学仅PixelFormat="Mono8"/stride>=W/实际bytes长度及hash；AcquiredAt原曝光，SequenceOrdinal=SourceIndex−1、DirectionId原光学方向、PatternId=manifest.PatternId、ExposureProfileId原曝光Id。capture.Frames完整原序，DirectionCalibration=scope.Asset，SourceFrame=标定重建world、Unit=Millimeter，DeclaredSupport仅原声明，不顶替实际mask |
| Route / PatternSpec | ThreeDReconstruction+Hybrid/Vertical→HybridVertical、Hybrid/Both→HybridBoth、GrayOnly/Vertical→GrayVertical、SingleStripe/Vertical→SingleStripeVertical；Deflectometry/Horizontal-only/Custom明确不支持。Profile=DecodeProfile的RevisionRef，ProjectorWidth/Height=GenerationSpec，MinStripeWidth/SingleStripeWidth原值，Global→"global"/InvertedPattern→"inverted_pattern"，MinGrayDifference由DecodeProfile显式0..255，CapturePhaseDiagnostics=冻结PersistenceRequested，OrderedPatternIds完整manifest |
| AcquisitionScope / FrameTiming | epoch/TimingProfile/MaxSequenceSpan/MaxStereoSkew/SceneStationaryVerified及全部12字段timing取原证据；同attempt、同步clock、expected ordinal/PatternId一一相等，曝光完全在原稳定窗内；无窗/不同域拒绝R3D-021，不能用Bool代静止来源。Roi原PixelRoi，Grid=null/Stereo=null，不裁图/换原点 |
| CalibrationRef / CalibrationScope | 共同资产Owner提供原Asset/Qualification、有限正NativeLengthToMm、CameraFrame/WorldFrame/CalibrationKind/有效窗、ReconstructionFrame、camera0/projector1及双方尺寸；DirectionCalibration=scope.Asset。按B.4.6核已接收Joint专用资产；CAL §7.4.6B给完整快照技术指纹/版本域桥，本地消费见B.4.6.7（资格绑定消费增量已获主控限定内容接收，2026-10-11），不把技术指纹称资格原件签名；缺完整关联/伴随快照时**不组装伪真实值、不获取源或调用native**。下面旧synthetic资产仅模拟既有消费类型；不得用Joint Synthetic setup运行真实重建 |
| ReconstructionInput / Execution其它值 | InputSetId/InputRevision原冻结组，Mode StructuredLight/Directions原序/Calibration=上述完整CalibrationRef/OutputFrame原world/DirectionTransforms null，ZMin/ZMax同时null或原Profile显式值，MaxPixels显式软件限；每方向TransformUses AlreadyInOutput/0/null，QualificationProfile可null（Unverified、不融合），Budget/DrainTimeout如下 |
| ReconstructionParameters / ResourceBudget | AlgorithmProfileId=AlgorithmProfileRevision.Id，MinStructuredLightFrames=manifest数，MinValid/MaxInvalid/MaxDisagreement缺资格全部null不猜门值；MaxDirections1..16且>=方向数、MaxNativeBytes=Execution.Budget.Native、Timeout剩余100ms..30min、PartialResultPolicy本桥单方向RejectOperation。Managed/Native/Result各64MiB..8GiB且不超父/宿主剩余，MaxPoints/MaxVoxelCells显式，DrainTimeout1..60s且cleanup已预留；不够64MiB/100ms即SL-RES-001，不延长父预算 |

IM-032 adapter沿其现签名取得IFrameLease/ICalibrationAssetLease并唯一归还，桥不再提前Acquire一份、替adapter.Dispose或传HALCON handle。质量可诊断UInt16/Float32，当前重建光学公开支持仅Mono8；高位深R3D-007/SL-VIS-003拒绝，不截断/归一化绕过。IFrameLease不含先验有效mask，重建有效域来自IM-032输出；若请求要求用上游mask先过滤重建而现合同无法表达，副作用前拒绝，不把quality共同mask冒作重建输入域。

**已接收0.2.5的消费增量**：完整NormalizationBlack/White及GrayCodeInverted、显式Sequence和成功重建后的DiagnosticLayers可按B.4.7接线；不是所有RequestedLayers都拒绝。未声明部署能力、非法/缺少角色、Defect、GrayVertical+Phase、非SingleStripe+SingleStripe、HybridBoth+Diagnostics仍在获取源前明确拒绝；不得从内部模型取图/重复get算子。DiagnosticLayers不是无先验标定的decode-only入口，首次Joint命名row/column现通过另已接收IM-032 §7.6无setup入口，B.4.6.6精确消费；本地首次观测producer指导已获主控限定内容接收（2026-10-11），真实运行/封存/采样资格NotReady。

表面用途仅从成功回执单方向CameraSamples、原camera W/H、ROI/domain与全CSR源帧相符的候选取得ValidFraction，denominator冻结原请求ROI域大小，不从有效点数倒推。Observation.ProducerId="reconstruction-3d"，ProducerVersion=已核部署实际Core包版本（Result没有ModuleVersion，不猜字段），原CalibrationRef；Metric("ValidRatio",...,"fraction",roiRequestedPixels,surfaceDomainRef,null,Observed)，域明确**重建候选有效域**。不能与qualityDomainRef混用或同一个Reply中重复同名两个域；需要二者由宿主保留两份原报告/两明确用途请求。旧Diagnostics=null仍LayerRefs.Empty；显式支持层按B.4.7限额封存映射。无Result/非成功/全不可观测不能Observed；mm XYZ与QualityState不转rad/Phase/生产PASS。mask=false保持XYZ=null及原因，合法Z=0保留；未有误差模型不输出不确定度。

#### B.4.4 Advice、错误、原Task与有限排空

候选必须有匹配完整GenerationSpec/manifest/图组/ROI/runtime；stripe/route/normalization/尺寸变更还拿旧帧→RejectKeys="MatchedPatternEvidenceMismatch"，不Generate/重拍弥补。Decode阈值候选只原Profile明确范围且同组；每候选独立Quality.RequestId，确实调用IM-032的用途另登记其OperationId/CalculationId两个字符串；仅质量用途不启动/补造R3D任务，在实际CandidateEvaluationRequest.OperationId+CandidateId下关联原Recommend身份，有限串行一次，不重用CandidateId代替operation。下游任务共享父最早期限/资源余额。

十项metric各一：ValidRatio按构造冻结用途的真实支持域；FalseAcceptRate/FalseRejectRate须原真值计数/分母；CircularPhaseMAE/RMS/Max须公开phase原值、明确rad尺度/周期及真值/共同有效域；IM-032已交Phase但其HalconPhaseValue不等于rad，尺度/真值/域缺失仍NotEvaluated并区分PhaseUnitUnavailable/PhaseReferenceUnavailable/PhaseDomainUnavailable，完全无层才PhaseEvidenceUnavailable；P50Ns/P95Ns/P99Ns须完整同样本的实际ResourcesReleased端到端测量及Profile统计口径，PeakBytes须同Owner账本/实测维度。未测/无标签/无目标均Value=null、Denominator=0、NotEvaluated/原因明确，单位fraction/rad/ns/bytes，不从XYZ、Sobel或时钟抖动编相位，不把单次stopwatch当P95。像素metric精确DomainRef，资格metric精确AcceptanceProfileRef；缺项列NotEvaluatedKeys，不隐藏。B.3要求十项齐全且全部门通过，当前信息不足Rank=null/Eligible=false/AdviceId=null；Completed仅有限离线分析结束，不写回生产参数。

错误原Owner仍存QualityIssue.Code/FieldPath/MessageKey、R3D Code/Stage/DirectionId/AdapterCode/DirectionIssues/FusionIssue及原状态；桥映射非法字段SL-VAL-001、谱系/hash/timing SL-VIS-002、无观测/不支持SL-VIS-003、预算SL-RES-001、同id异hash SL-CON-001。ModuleIssue.Path原字段、DetailKey稳定资源键、NativeCode原QS/R3D code（有界），不拼大异常文本。合法不可观测/缺真值给NotObserved/NotEvaluated；provider故障不被Optional吞成成功。资源未确认始终DrainUnknown/Held，真实归还后仍保原Cancelled/Rejected逻辑，不以晚到Completed覆盖。

新增消费原因的宿主资源键及三语文本如下，ModuleIssue.DetailKey使用该稳定键，ErrorCode仍前表原SL码；这些是投影解释，不新增下游错误enum/质量状态。缺项原因与metric Name在消费清单一一关联，不直接把内部枚举/异常文本给操作者。

| 稳定资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| FrameKindUnsupported | 重建接口未定义该帧角色。保留整组原图。 | 重建介面未定義此影格角色。保留整組原圖。 | The reconstruction interface does not define this frame role. Keep the complete frame group. |
| DiagnosticLayerNotExported | 重建接口尚未提供该诊断层。 | 重建介面尚未提供此診斷層。 | The reconstruction interface does not export this diagnostic layer. |
| PhaseEvidenceUnavailable | 缺少相位数据，无法评价误差。 | 缺少相位資料，無法評估誤差。 | Phase data is missing. Phase error cannot be evaluated. |
| MatchedPatternEvidenceMismatch | 图案参数与原图组不匹配。选择匹配图组。 | 圖案參數與原圖組不符。選擇相符圖組。 | Pattern parameters do not match the frame group. Select a matching group. |
| GroundTruthUnavailable | 缺少真值，无法评价误接受或误拒绝。 | 缺少真值，無法評估誤接受或誤拒絕。 | Ground truth is missing. False acceptance and rejection cannot be evaluated. |
| PerformanceEvidenceUnavailable | 缺少性能目标或实测数据，无法评价性能。 | 缺少效能目標或實測資料，無法評估效能。 | Performance targets or measurements are missing. Performance cannot be evaluated. |
| RequestDomainUnsupported | 当前接口无法传递该请求域。保留原域设置。 | 目前介面無法傳遞此請求範圍。保留原範圍設定。 | The interface cannot carry this requested domain. Keep the original domain settings. |

桥沿§9.3 factory前进程根额外强持qualityRoot/slot/OriginalConstruction/OriginalCompletion/ActiveCloseObservation、engine原run/stop/dispose、sim/clock/gates原stop/dispose、清单/输入借读/输出及错误。原运行Task不是WaitAsync包装Task；QueryDrain查SL原id映射下全部任务/资源：quality snapshot Drained/ResourcesReleased、构造/Completion/关闭Task实际退出；R3D.Query原ID.Drain=Released且run退出；sim.Query active/pending/lease计数0。某Task未退出/查不到/借读未归还→Unknown/Held；确定未启动无资源可Confirmed/Released，绝不用native=0/QueryNotFound当归还。B.Close.Unresolved列SL父id，完整下游ID仍留根。

独立cleanup token与有限wall总/阶段份额，嵌套finally：停止准入→quality slot.CloseAsync(QualityStopWaitBudget,waitToken)有限观察→R3D StopAndDrainAsync原ID且run退出后才Dispose→engine确认后sim Stop/Dispose→quality确认无借读/工作后TryForget→释放桥自己借读→宿主按§9.4.1压缩B结果→确认全量移交/退槽。各阶段catch独立记cleanup错误，finally继续其它已登记Owner；不覆盖原业务错误，不发新Start/Reconstruct/Acquire。Quality恢复仅原合同允许且无活动观察时RecoverAsync/RetryRelease，不重算；R3D未知Stop/Dispose只观察原Task，不并发释放。sim不能在engine用Ports时先Dispose；TryForget=false不证明释放。IReconstructionIsolationOwner.Retain只确认engine部分，不能据此清quality/桥/sim；adoptRecovery全槽接收确认后才转Owner，否则原进程根持续强持，迟到仍原ID/Task不回调已返回Host。

调用层级固定：Host finally首先登记原B.CloseAsync，它调用adapter.CloseAsync停止并有界观察下游；adapter.Close绝不反向调用B.Close/Release，避免递归/互等。共享quality槽的observation/evaluation两个端口以同一已登记CloseTask去重；同步拒绝/异常记NoTaskReturned及原错误，不补成功Task。下游未确认时B.Close只能Unknown/Held/列原父id，Host仍继续usage/全量移交。已Released的旧quality报告/原Completion在桥根保留至各B父请求结束，不能因slot下一Start覆盖OriginalCompletion丢失旧Task。

ns→TimeSpan向下到100ns tick，不足1tick/checked溢出拒绝；R3D不足最低100ms/资源64MiB则不调用。不跨ClockStamp Boot/domain相减；TimeProvider与R3DClock各按父剩余换截止，UTC后退不延长。共享UTC不能证明相机/投影纳秒域同步。原quality/重建/桥源copy与输出、原图metadata/keys、仍Held资源同时计父Managed/Native/Result及Host根，预算不足分配/factory前拒绝；串行也不能把Held额度当已回收。两Host沿本页10/120/180s wall预算，虚拟clock/gate仅模拟逻辑，不采用外模块suite期限或kill证明排空。

#### B.4.5 两个完整无UI Host与明示fixture

未来binding指定Vision.Tests/Hosts各独立Program/工厂/根/clock，仅引用本模块公开Core/Projection/Vision及下游Core/发布Simulator、不引用外模块Core.Tests/隐藏builder/平台Shell。所有列表用ImmutableArray非default、字典ImmutableDictionary.Empty.WithComparers(Ordinal)；不是已编译运行。辅助Hash(x)=SHA256(UTF8(x))小写，asset(x)=AssetRef(x,"1.0.0",Hash(x))、rev(x)=RevisionRef(x,Hash(x))仅fixture身份；帧/标定载荷用实际bytes hash，不拿Hash(ID)自证内容。Guid/RetentionIdentity首次生成后根保存，同请求观察不换ID。以下生成/帧/标定全部synthetic，不能当真实HALCON布局/曝光/标定/计量数据。

| 两Host各自完整输入（H分别为A/B独立前缀） | 逐字段值 |
|---|---|
| 已冻结生成及投影来源 | H取A或B：GenerationSpec("0.2.0","seq-"+H,"1.0.0","synthetic-port","1.0.0",ThreeDReconstruction,8,8,4,Vertical,Hybrid,Global,null,1,asset("gen-"+H),null)。六GeneratedPatternEntry的SourceIndex=1..6、PatternId="seq-"+H+":p:"+index；前2 Gray/Vertical，后4 Phase/Vertical、PhaseIndex0..3、PhaseRadians0,π/2,π,3π/2、SpatialFrequency0.25，其它phase字段null。每PatternArtifact用上述ID/Version1.0.0/GeneratorId及Version/8×8/ByteGray/ByteLength64/实际64byte全10的digest/对应role及phase/IntensityScale1/这64byte的ImmutableArray。六ProjectionStep(ordinal0..5,"seq-"+H+":s:"+ordinal,对应PatternId,对应ContentSha256,"capture")。ManagedPatternPlan("0.2.0","seq-"+H,"1.0.0",六Artifacts,六Steps)，SpecHash/ManifestHash按B.2逐字段计算。冻结GenerateReply(独立原生成Guid,Generated,SpecHash,该ManagedPatternPlan,六Entries,ManifestHash,asset("gen-"+H),null,Issues.Empty,Confirmed,Released,null)由fixture显式传入，不调用/重写生成器；六步仅合成消费协议，不是HALCON Global完整光学布局证明 |
| 投影来源对象及hash | planningLimits=PlanningLimits(8,8,6,6,16,16,1MiB,1MiB)，显式StructuredLightPlanner.Validate/Plan上述ManagedPatternPlan必须Valid，得到ProjectionPlan；这只计划既有图案，不生成/投影。六TimingStep(i,对应ContentSha256,"capture",10000,0,1000,1000,0,0,"capture-H")。ProjectionSequence(该ProjectionPlan,SoftwareStep,六TimingSteps,asset("projection-profile-"+H),asset("runtime-"+H),null,Hash("cap-"+H),Hash("mapping-"+H),None,1_000_000_000,100_000_000)，SequenceHash按C.1 ASUN-SL-SEQ-2完整编码，Generation1是synthetic输入代次；没有ProjectionSession/设备调用。原稳定窗在每step内，模拟采集证据另列；不以Core PlanSha256顶替SequenceHash |
| 原帧/来源 | 六FrameId="H-f0"..5/2×1/Mono8/stride2/Bytes[10,20]/hash实际两byte digest/mask全true（B第3帧第二位置false）。QualitySourceRef(FrameId,载荷hash)；Descriptor(Source,RawAcquisition,"mono",UInt8,2,1,"pixel-H",null,"epoch-H",i,"exp-H","stationary-H",原SequenceHash,null,AcquiredAt,null,8,null,null)。now由qualityClock.GetUtcNow；离线FrameTiming起点固定2026-10-11T00:00:00Z，曝光[i*10000+1000,i*10000+2000]ns/稳定[i*10000,i*10000+3000]ns，attempt-H/epoch-H/device-H/clock-H/ExposureRevision rev(exp-H)/ExpectedOrdinal i/PatternId对应。AcquiredAt起点+包含曝光结束ns的上舍入100ns UTC ticks（真实接线直接原时间） |
| ROI/B请求 | PixelRoi(0,0,2,1)，qualityDomainRef=asset(quality-domain-H)、surfaceDomainRef=asset(surface-domain-H)。ObservationRequest(独立原ObserveGuid,"attempt-H",原SequenceHash,1,原ManifestHash,[asset(binding-H-0)..5],null,asset(bridge-profile-H),asset(runtime-H),RequestedLayers.Empty,asset(roi-H),512MiB,3_000_000_000,false)。六binding展开上述一一帧/时序与源，仅原图共同支持用途，CalibrationRef=null |
| quality参数/请求 | Inputs=[QualityInput("step-i",source-i)]；Regions=[QualityRegionSpec("roi",QualityBox(0,0,1,2))]。六QualityMethodPlan("raw-step-i","r1","roi","step-i",RawStatistics,QualityRawParameters(ManagedQualityMethodSet(Required=[ManagedSaturationMethod("r1",0,255),ManagedCoverageMethod("r1")],Optional.Empty)),QualityObservablePolicy(1,0,null,null,null),true)。末method group-support/r1/roi/step-0/StructuredGroupSupport/QualityGroupParameters(["step-0"..5],[0..5])/同Policy/true。QualityServiceRequest(原Guid,"image-quality-service-v0.1",Inputs,Regions,七Methods,Budget,2,1) |
| quality公开构造和额度 | qualityClock=TimeProvider.System；clockNow=qualityClock.GetUtcNow()，root=new QualityHostLifetimeRoot(qualityClock,new QualityHostRootLimits(1,128MiB))，slot=root.Reserve(原SlotGuid,128MiB)在factory前。instance=QualityBudget(64MiB,64MiB,1_000_000,16MiB,3s,初始父UtcDeadline=clockNow+3s)；每次request Budget(32MiB,1MiB,100_000,8MiB,min(2s,父剩余),min(初始父UtcDeadline,qualityClock.GetUtcNow()+2s))。inputProfile=QualityMemoryInputProfile("memory-H","r1",6,1MiB)，visualProfile=QualityManagedVisualProfile("managed-H","r1",256,6)，六QualityMemorySource(完整Descriptor,ImmutableArray<double>[10,20],原mask)；RuntimeRef清单绑定image-quality-managed-port-v0.1/<实际Core包版本>/r1及该ModuleVersion，精确核对，不造HALCON身份 |

两个Host各自的B完整limits=VisionLimits(8,6,6,7,10,2,16,256MiB,128MiB,96MiB,16MiB,100_000_000,7_000_000_000,RetentionPolicy(namespace-H,8,16MiB,2MiB,16,2MiB,60_000_000_000))；namespace-H为各Program首次生成并保存的非零ulong，所有B业务Guid沿C.5生成同namespace前缀且互不复用。进程桥根先按§9.3预留MaxLiveOwners1、每槽原Task最多96（业务64/cleanup32）、身份最多32（含两个候选各下游原ID）、metadata<=16MiB、本方源copy/结果<=48MiB，共桥本方64MiB；容量不足在任何factory/copy前返回非零。保守同时预留quality槽128MiB、其native64MiB、IM-032 Managed/Native/Result各64MiB和桥64MiB，共448MiB<=父512MiB；quality输出及输入copy包含在槽128MiB内，不重复扣也不漏扣。各维仍核上述VisionLimits，实际CLR/native峰值另验；托管factory没有native分配也不挪用它的预算给其它Owner。

初始wallStart在源copy/构造之前，整体业务deadline=wallStart+3s，整体case deadline=wallStart+10s；各请求的3s/2s为上限，前步骤耗时从同一父剩余扣除，剩余<=0不启动下一步。quality每次Start重新显式构造上行Budget并固定其更早UTC截止；R3D Timeout/Deadline按下行取剩余，不先写死2s后超父期限。QualityStopWaitBudget每次明示MaxWait=min(1s,当前cleanup剩余)、DeadlineUtc=当前qualityClock.GetUtcNow()+该MaxWait；R3D/SIM Stop的waitBudget同一剩余份额，DrainTimeout1s在case清理7s内另预留。新调用不足下游最小预算即拒绝，cleanup无份额仍留根进入全量移交/保留，不重置时钟。

本地clock只实现现B/C两个接口，两个Program各new且由根强持，方法体完整如下；TimeProvider.System同时供quality，模拟曝光纳秒域仍独立：
```csharp
internal sealed class BridgeHostClock : IProjectionClock, IAdviceClock
{
    private readonly TimeProvider source;
    private readonly long started;
    private readonly Guid boot = Guid.NewGuid();
    private readonly string domain;
    public BridgeHostClock(TimeProvider source, string hostId)
    {
        this.source = source;
        domain = "bridge-" + hostId;
        started = source.GetTimestamp();
    }
    public ClockStamp Now => new(boot, domain,
        source.GetElapsedTime(started).Ticks, TimeSpan.TicksPerSecond);
    public DateTimeOffset UtcNow => source.GetUtcNow();
}
```
visionClock=new BridgeHostClock(qualityClock,H)，adviceClock=visionClock；guid/native预算与wall clock不依赖window。adapter.QueryDrain按B.4.4的原请求关联即时快照，Close沿原下游Task，不占有生产设备。未用generator是§9.4的NoCapability，未用evaluations（A）同理，不假生成/假评估；意外调用明确Rejected/Confirmed/Released，下游调用计数0。下面Host A只Observe一次后消费独立SIM请求，Host B Observe一次后Recommend一次，各层原Task在调用前预留、返回即登记，没有两套手动Start与session内部Start重复。

Host A完整无UI调用：先预留桥根→上述root.Reserve→Create本模块session并绑定原根→登记一次session.ObserveAsync原Task；其observation adapter消费上述清单，在内部slot.ConstructAsync(()=>ImageQualityMemoryInputFactory.Create(inputProfile,sources,qualityClock,instance),()=>ImageQualityManagedVisualFactory.Create(visualProfile,qualityClock,instance),instance)保留原构造Task→有限观察→service.Validate(request)→slot.Start(request,ct)→保存原Completion/有限观察→group RequestedPixels2/ValidPixels2/CenterPixels2/commonValidFraction1/Fraction，六Raw各Coverage1、低/高截断计数0，group presentSteps/requiredSteps为Count6→B返回image-quality/ValidRatio1/LayerRefs.Empty，留原报告。另在剩余预算满足下游下限时按下表完整装配IM-032 Simulator进行消费协议验证，原候选单独留存，不换B质量域/Producer：

| Host A完整ReconstructionRequest及Simulator载荷 | 明示值 |
|---|---|
| 输入/身份 | 先new SimulationClock(固定起点)并强持，再冻结请求；ApiVersion0.2/OperationId="A-reconstruct"/CalculationId="A-calc"/AuthorityScope synthetic-only/Deadline=clockA.UtcNow+父当前剩余（固定SIM域），Host额外保持原单调wall截止；InputSetId A-input/InputRevision rev(A-input)/Mode StructuredLight/Calibration=下行完整CalibrationRef/Directions=[DirectionCapture("A-dir",六FrameRef,"synthetic-cal-A"的revision,world-A,Millimeter,Fraction1)]/OutputFrame world-A/DirectionTransforms null/ZMin/ZMax null/MaxPixels2。FrameRef(FrameId,实际byte RevisionRef,前两GrayCode其余PhaseShift,2,1,"Mono8",原AcquiredAt,i,"A-dir",manifest.PatternId,"exp-A") |
| 模拟标定/Execution | bytes=UTF8("synthetic-cal-A")，calAsset=RevisionRef("synthetic-cal-A",实际bytes hash)。CalibrationRef(calAsset,camera-A,world-A,"synthetic",固定起点−1day,起点+1day)。CalibrationScope("A-dir",calAsset,rev(synthetic-qualification-A),1,world-A,0,1,2,1,8,8)。AcquisitionScope(epoch-A,rev(timing-A),1s,0,true,上述六timings)。TransformUses=[A-dir/AlreadyInOutput/0/null]；PatternSpec(rev(decode-A),HybridVertical,8,8,4,null,"global",10,false,六PatternIds)，Stereo=null/Roi=PixelRoi(0,0,2,1)/Grid=null/QualificationProfile=null；ResourceBudget(ByteCount64MiB,64MiB,64MiB,MaxPoints16,MaxVoxelCells16)/DrainTimeout1s |
| Parameters / Fusion | ReconstructionParameters("decode-A",rev(decode-A),6,null,null,null,1,ByteCount64MiB,Timeout=min(2s,父剩余且>=100ms),RejectOperation)，Fusion=null；Qualification null不Qualified/不融合 |
| 模拟输出 | SurfaceResult("A-surface","A-calc",StructuredLight,world-A,Millimeter,2,1,Z[-0.25,0],mask[true,true],reason[0,0],Uncertainty null,六SourceFrameIds,["A-dir"],ContributionCount[1,1],Unverified,ValidFraction1,ConflictFraction0,rev(decode-A),Provenance=[rev(synthetic-A),原input/profile revision])；SurfaceGeometry("A-surface",CameraSamples,null,X[0,1],Y[0,0],SourceOffsets[0,6,12],Sources每pixel六SampleSource("A-dir",FrameId,SampleIndex=pixel,ImageRow0,ImageColumn=pixel,Stereo null),ConflictPairCount[0,0],Transforms=[TransformProvenance("A-dir",AlreadyInOutput,null,0,1)])；AdapterDirectionResult(surface,geometry,Warnings.Empty,ResourcePeaks ImmutableDictionary.Empty) |
| 公开SIM装配 | clockA=new SimulationClock(固定起点)、gatesA=new SimulationGates(ImmutableArray<string>.Empty)、diagnostics实现IReconstructionDiagnostics仅存容量256序号/错误/不抛不写生产。Frames六SimulationFrame("A-dir",原FrameRef,2,ImmutableArray<byte>[10,20])；Calibrations=[SimulationCalibration("A-dir",calAsset,模拟bytes)]；Directions=[SimulationDirection("A-dir",上述RawObservation)]。script=ReconstructionSimulationScript(ReconstructionSimulationFactory.ScriptVersion,"bridge-A",7UL,完整Request,Frames,Calibrations,Directions,Steps.Empty,ByteCount1MiB)。先root槽再new ReconstructionSimulationFactory().Create(script,clockA,gatesA,diagnostics)并立即保留sim/clock/gates；engine=new ReconstructionFactory().Create(sim.Ports)并强持；全嵌套集合不可变 |

Host A先以engine.Validate(sim.Request.Input,sim.Request.Parameters,sim.Request.Fusion)确认三个参数的结构校验；request身份/版本/Deadline仍由随后ReconstructAsync预检，不能拿Validate替代。登记engine.ReconstructAsync(sim.Request,ct).AsTask一次，有限观察Completed/Released/Unverified、Z负值与合法零、完整12条CSR、6帧+1资产共7lease各归还一次。该旧synthetic协议无真实共同标定适用性/资格，不得调用AsunImage。finally按B.4.4嵌套quality Close、engine Stop/原run观察/Dispose、sim Stop/Dispose、所有原Task结束/资源零、quality TryForget、本方copy/借读归还；未确认全槽移交则保留原根，0只软件fixture协议检查通过。没有未声明request/builder/source stub；SIM输出明示，不是从原图推高度。

Host B是独立试验台Advice console，不引用A/不加载WPF/设备/标定：上述B前缀六frame中第3帧mask[true,false]→group RequestedPixels2/ValidPixels1/commonValidFraction0.5，各Raw RequestedPixels2，前述第3帧ValidPixels1/Coverage0.5，其余ValidPixels2/Coverage1；各低/高截断计数0，group Count键presentSteps/requiredSteps均6。先按A相同预留/Create/Observe链构造一次B自己的quality service，原观察取得image-quality/ValidRatio0.5；保存原ObserveTask/报告后再构造RecommendationRequest(独立原RecommendGuid,asset(baseline-B),asset(evidence-B),Candidates=[("c10",GenerationSpec-B,asset(decode10-B),asset(matched-B)),("c20",同Spec,asset(decode20-B),同matched)],MaxCandidates2,MaxEvaluations2,BudgetNs=同Host3s父业务截止的当前剩余ns（<=3_000_000_000）,BudgetBytes512MiB,ExpiresAt=clockNow+1min,AcceptanceProfileRef=asset(acceptance-B))。清单明确两个decode阈值10/20、同原完整图组/ROI、无真值/phase/性能目标/共同标定，不因不同decode ref捏不同帧。

每candidate Evaluate调用同公开quality路径但以独立RequestId/剩余Budget（强持实际收到的B.2 CandidateEvaluationRequest.OperationId/CandidateId并关联原RecommendGuid；不猜二者Guid相等、不另生成公开子Guid，下游各RequestId仍不同），在已开放service上一Completion结束且ResourcesReleased后才slot.Start新请求；不重复Construct/不在候选中Close后复用已关service。结束统一Close。CandidateEvaluationReply保实际request.OperationId/原CandidateId/SpecHash，ValidRatio0.5/fraction/denominator2/quality-domain-B/AcceptanceProfileRef/Observed；另9项Name为FalseAcceptRate、FalseRejectRate、CircularPhaseMAE、CircularPhaseRMS、CircularPhaseMax、P50Ns、P95Ns、P99Ns、PeakBytes，Value=null/Denominator0/NotEvaluated，单位依次fraction×2/rad×3/ns×3/bytes，ThresholdProfileRef均原AcceptanceProfileRef，phase DomainRef为本次预期同原共同像素域quality-domain-B（不称已有phase测量），其余DomainRef=null。NotEvaluatedKeys为这9个Name的Ordinal有序数组，原因按B.4.4留原有界Issues/消费清单；RejectKeys.Empty，DrainStatusConfirmed/ResourceStatusReleased/Issues仅保留缺项原因、无provider故障；B.session.RecommendAsync排序得到两Eligible=false/Rank=null、AdviceId=null，Completed只分析完成，不能称生产推荐。若候选生成Spec改变而仍用旧图直接RejectKeys匹配错误；真实首次producer运行/资格桥尚未关闭不阻纯质量诊断/Advice缺项，R3D source/native调用0。异常finally同A的两轴/原Task/全根确认（B不构造sim/engine，不能补造清理Task）。

两个Host把显式消费清单及端口闭包注入StructuredLightVisionSession.Create(generator,observations,evaluations,visionClock,adviceClock,limits)，其Generate/Observe/Recommend/Query→ReleaseResult→Close仍B原API。本Host只消费已冻结GenerateReply，generator用§9.4 NoCapability（意外Generate明确Rejected/Confirmed/Released），不冒充生成成功。Projection clock/Advice clock由Host明确注入、与父deadline同域；NoCapability未用端口也有QueryDrain/Close，不能动态加载真实模块。主Program持桥根至真实归还或确认接收，两Host独立进程也验证同样结果。case业务最多3s、cleanup总最多剩余7s、各观察使用其剩余份额且Stop/Dispose单阶段最多1s；全部含构造/源copy/收尾在10s内，suite120s/外层180s，fixture数字只软件限额。虚拟SIM正常NotBefore0/gates空无需真实Sleep；故障gate由case Owner finally放行并有界观察，不从clock推进推native已释放。

| 新断言 | 确定输入变化与预期 |
|---|---|
| SL-BR01 | A quality+SIM和B quality+Advice完整调用，核上述数值/域/CSR/lease及三层原Task/root；A取消/消费异常不改B，synthetic不Qualified/不发设备/不写生产 |
| SL-BR02 | 缺/重复binding、跨attempt、错sequence/manifest/hash、无稳定窗/clock不符、ROI越界/尺寸变化/伪source revision→桥前检拒绝，下游调用0；直接QS缺step的NotObservable不能绕过B完整组 |
| SL-BR03 | UInt16帧quality保原码、R3D-007不转8bit；Deflectometry/Horizontal-only/Custom仍拒绝。完整黑白/反图及支持RequestedLayers改按B.4.7/SL-DG验证，不删帧/冒角色；额外ROI域mask/要求先验mask过滤重建无法表达仍拒绝，不重写坐标/单位 |
| SL-BR04 | 普通相机asset冒共同标定→quality仍可运行/真实重建调用0，synthetic bytes不给AsunImage；candidate stripe/route变却旧图→拒绝且不Generate/重拍；缺9项→NotEvaluated/无Rank/AdviceId |
| SL-BR05 | Quality构造/Completion/Close、R3D run/stop/dispose、lease.Dispose与SIM callback/release gate逐点挂住/异常；观察有限但Task/借读仍强持/B DrainUnknown，finally仍到全量移交；拒绝/丢回执保留原错误/Root，恢复不重算/新Acquire |
| SL-BR06 | Budget/Root槽/MaxBindings/读取/输出/native envelope上限±1、ns不足tick或R3D100ms/64MiB→复制/factory/native前拒绝；native0/QueryNotFound/Released快照但原Task pending都不能退槽/重算 |
| SL-BR07 | runtime漂移、Quality少键/Support错域或R3D CSR/mask/XYZ畸形→保原Owner错误并拒绝，不改Observed；两域同名ValidRatio不能混装、Z0仍有效/mask无效不填0 |

B.4.1–5已支持消费桥指导内容获主控限定接收（2026-10-11），原Slice-0/1/2及Slice-3内容接收保持。旧六帧/Diagnostics=null的两个Host仍只协议fixture，新增完整角色/层消费见B.4.7，不把旧fixture冒成真实HALCON布局；Joint首次decoder准确边界见B.4.6。真实原帧接线、AsunImage/C#封送、资源系数/Golden/性能/产品资格均未运行，B.4.6–7确定指导增量获主控限定内容接收（2026-10-11），原切片接收及真实资格边界保持。

#### B.4.6 Joint producer 与两个独立无 UI Host（主控限定内容接收，2026-10-11）

##### B.4.6.1 唯一来源、逐字段交接与真实边界

本节只消费[calibration-assets 0.3.1-prep §7.4 Joint API v1](../calibration-assets/DEVELOPMENT-GUIDE.md#74-相机投影器共同标定首版内部规格joint-api-v1)，不向B.1–3增加decoder接口、LayerKind或新的标定ref。公开namespace为 `Asun.Modules.CalibrationAssets` / `.Joint`。本地producer实现其 `IJointObservationProvider`，接收原采集Owner、生成Owner、解码Owner及参考件/计量Owner已经核定的完整输入；字段/codec/阈值/采样拟合/资格仍以上游§7.4为唯一权威。本模块只保真封存/关联/限额交付，不拟合黑圆周围映射、不签采样或用途资格、不求解、不发设备命令。

真实首次CAL-JC需要无先验camera_setup的完整 `gray_code_and_phase_shift/both/global`，命名ProjectorRows及ProjectorColumns。IM-032 0.2.5成功重建诊断先依赖已校setup，且HybridBoth+Diagnostics明确不支持；不能借它生成首次标定观测、造初始setup、从内部模型取图或在此自己decode/get。IM-032 0.2.6 §7.6无setup decode-only公开规格已接收，B.4.6.6使用独立IStructuredLightDecoder/具名payload完成首次producer接口桥（主控限定内容接收，2026-10-11，仅观测producer规格）。原B.4.6.1–5接收保持；实际native/封存/采样/完整Joint运行资格仍 `PreparationIncomplete/NotReady`，不阻已接收Core、原图quality或成功重建支持诊断。

| JointObservationPacket / 原来源 | 精确交接 |
|---|---|
| Group | 原ObservationId、PoseIndex、CaptureGroupId、ObservedAtUtc及Packet；同一次实际物件/姿态，不按点拆fit/check。Fit/Check按完整物理组隔离，id/组/序列不能交叠；不以相同黑场内容hash判重复物理组 |
| Optics | 两端完整DeviceConfigurationSnapshot、CameraFrame/ProjectorFrame及PhysicalMapping ContentRef；static area-scan/division、完整active raster、binning1、相机/投影器分别宽高。OS缩放、keystone、crop/flip/resample不能沿旧映射摘要。两端初参/来源由JointProfile给出，不猜同焦距/pitch |
| Pattern | JointPattern的Width/Height/MinStripeWidth/MinGrayDifference/Manifest/Decoder/DirectionMapping全原值；标定固定HybridBoth/global。Manifest闭包保原GenerationSpec/完整OrderedManifest/投影计划、实际FrameBinding顺序、全部黑白/Gray/Phase身份/hash，不因灰度低删帧 |
| CameraImage/WhiteImage/BlackImage | 同CaptureGroup的UInt8白场reference、白场、黑场原图；CameraImage可与WhiteImage同完整ContentRef。实际白场用于finder/实测点关联，不把投影生成白图或软件常数图当相机曝光 |
| WhiteSurfaceMask | 参考件/白面证据经宿主核定的原camera栅格0/1 mask；只表示同平面白色漫反射可采样区，排除黑圆/边缘/板外/污染/饱和/混合像素。本模块不另写材质分割器，也不凭此签材质/共面资格 |
| ProjectorRows/ProjectorColumns | 解码Owner给具名全相机W×H Float64LE层、各自完整内容引用及来源；单位projector pixel。vertical=projector column、horizontal=projector row必须有不对称Golden与DirectionMapping原件；不猜Both[0]/[1]，不把两个axis当两个物理方向 |
| ValidMask | 原解码有效mask，保持原pixel位置；只有有效pixel的两命名坐标有限且在实际投影器0..H−1/0..W−1内。黑圆暗心invalid正常，不能判整组失败或填0冒对应；white-surface与valid两mask分别保留 |
| QualityEvidence/StableEvidence | 同组所有图案曝光的质量/未饱和及实际静止窗口/运动/投影读回证据，原ContentRef闭包；不是quality总分、ACK或Ready。原参考件/实测XYZ、证书/平面及不确定度另在JointInput.Geometry/Target/Plan持有 |
| ClockEpoch/CaptureSkew/StableWindow | 采集Owner核定同clock epoch/时钟映射/全部曝光，skew≤Profile.Limits.MaxCaptureSkew，stable≥MinStableWindow且整个white/black/完整Both采集都在实际稳定窗内。保原tick/UTC/映射证据，不从帧数或软件clock推物理稳定 |
| Points | 原点号、白场CameraRow/Column、完整row/column有序Support、具名projector中心值和JointLocalMap/SamplingQualification。Support值恰原层同pixel，包含原三bool质量依据；不在黑心取decoder值、不按“缺中心”自动剔除补采、不抽样截断支持数 |

JointProfile.Reference、两端CameraInitial/ProjectorInitial、20字段JointLimits、JointSamplingProfile、Volume、ValidationPlan、ParameterSources及CompatibleRuntimePatterns全部显式，由原Owner批准并核规范hash；不从B.ProfileRef字符串提取阈值。两端初始化向量按上游division 8参数/单位，参数来源与实测几何一起封存。标定Both manifest和运行Vertical manifest分别真实保存，不能只改Route或伪用同一个manifest。

黑圆中心由CAL-JA固定的白区环带局部映射求：上游§7.4.2规定完整支持/四象限、inner/outer、fit/check、凸包内含、normalized_dlt、leave-out/inverse/中心差及独立SamplingQualification。producer不重写这些算法/门限；只交可重算原图/层/mask/支持及资格字节，CAL-JA唯一重算/拒识。独立采样实验和黑白共面/中心偏差界不能用低拟合误差替代；真实来源不足明确拒识，无无限重拍或其它算法fallback。

##### B.4.6.2 实际内容字节、封存顺序与 stream/copy Owner

`ContentRef(Digest,Format,FormatRevision,ByteLength)`不是路径。Digest.Algorithm精确SHA-256、Hex为小写64hex；按实际全部bytes重算，恰ByteLength后还须EOF。不hashID/ToString/PNG或只核长度；相同bytes可共享一个引用，但format/revision/长度全部必须一致。N=checked(camera W×H)，每幅UInt8图/mask N bytes，每个Float64LE层8N bytes，先checked尺寸/数量/预算再打开源。图像格式 `image-gray8-rowmajor`、mask `valid-mask-u8`、层 `projector-coordinate-f64le`；真实format revision取上游批准原值。有效mask每pixel只0/1，两命名层保原LE bytes，invalid像素也保原内容而不靠数值0猜域。原stride有padding时由输入Owner逐行无损打包新规范bytes/新ContentRef，并保原source revision/hash关联，不能拿旧含padding摘要冒新内容。

唯一封存顺序：

1. factory/copy前在进程根预留组/任务/输出/bytes槽；强持原Generation/采集binding、授权Profile、借读Owner及完整原来源清单。核同组/clock/稳定窗/双方尺寸/顺序与方向证据，缺项在解码或Joint调用前拒绝。
2. 按已声明借读期限读原图/mask/层，在同revision/currentness两次核验间限额复制及流式hash，检查长度/EOF；变化整次失败，不替换latest。本地copy封存后可归还本次借读，仍被原decoder使用的lease由其原Owner待实际排空归还，producer不重复Acquire或代Dispose。
3. Geometry的nominal/measured/证书/平面原内容由参考件Owner提供实际bytes，producer不发明Geometry codec。Plan/Sampling/Profile/Observation只用公开JointCodec.EncodeValidationPlan/EncodeSamplingQualification/EncodeProfileContent/EncodeObservation；各自编码投影沿上游，最终ref由实际规范bytes生成。Artifact/Check由上游scope经EncodeArtifact/EncodeCheckReport封存，Store用公开DecodeCheckReport核规范报告，不偷补字段。合法临时ref只用于内部构造，不能出现在最终输入/依赖闭包；typed每次≤1MiB及caller余额，不创建自引用hash。
4. 形成完整final JointObservationPacket及Group.Packet，再将finalGroup用于JointInput.Fit/Check；原图、层、mask、证据和typed bytes以完整ContentRef核定只读关联。原包不改阈值/拟合/资格，且copy预算与来源关联一直可回查。
5. provider.OpenContentAsync每次返回独立只读Stream；**Core唯一Dispose已交付Stream**。provider只负责交付前自己持有的失败资源；调用返回迟到Stream必须先登记到原operation/ledger后真实Dispose，不能丢失或再交当前请求。ReadAsync/ReadPlanAsync/ReadSamplingQualificationAsync/ReadPhysicalEvidenceAsync返回防御副本，原Task直至真实退出仍强持。
6. Core跟踪provider并将全部实际内容导入独立workspace；Store.WriteAsync只经公开workspace.OpenReadAsync复制完整依赖闭包，不能偷读provider私字典、共享路径或假设两者同实例。Store-owned副本与provider/source复制分别计费；A关闭不能清B仍需的Store。Joint Resolve的Export.Bytes为独立防御副本，caller取得后归caller预算。

本地可只用BCL有界字典/只读buffer完成Synthetic端口，不新建公共blob-store/resolver API。真实Store/证据发布按其既有Owner实现；未接收到公开持久化端口的消费者不能凭引用宣称保存成功。同引用不同bytes或缺闭包统一保原CAL-108/来源错误，不能在桥内修摘要后继续。

##### B.4.6.3 Joint 专用 refs、用途与有限根

唯一入口 `JointCalibrationModule.Create(options,new JointAdapters(Factory,Observations,Store,Qualifications,ExecutionGate,Diagnostics,Clock))`。A有全部端口，B只读令Factory/Observations=null。options只容量，不代替每次请求预算；五入口只用 `JointCall<T>("1",originalOperationId,budget,payload)`，payload恰JointSolveInput/JointValidateInput/JointPublishInput/JointResolveInput/JointReceiptInput。Budget.Deadline/WaitLimit是duration，WaitLimit≥Deadline，不是UTC时间；每入口与同一父剩余取小，不借查询重置业务期限。

| 调用/引用 | 接收条件与不能省略的原事实 |
|---|---|
| Solve/Validate/Publish | 原SessionId/Input、Candidate、成功CheckEvidence逐次使用；ResourcesReleased+Error=null+匹配Value才消费。Validated才有Report。PublishReceipt.QualificationIssued恒false，发布不授资格；未知发布只在原任务/held已归还后以新查询id+原OriginalPublishId回查，不再次Publish |
| Resolve / JointUse | 原Published/ActualOptics/精确运行Pattern、全部实际曝光起止、实际Volume及Purpose；每次问当前Qualification/Watermark，不缓存旧Applicable或晚到资格。Unknown/NotApplicable均无Qualified/Export，不用旧文件继续 |
| Applicable/Export | 原JointQualifiedRef全部资格id/revision/watermark/有效期及JointSetupExport.Asset/File/Bytes/CameraFrame/WorldFrame/NativeLengthToMm/两个index，核用途/范围/曝光/水位、文件恰长/hash、frame同cam0、index0/1、NativeLengthToMm=1000。真实file为halcon-camera-setup-file/26.05并具roundtrip及当前真实用途资格；meter到mm仅一次，方向不从Vertical推导 |
| Synthetic/1 | 仅cp-joint-synthetic-setup-v1/1、Purpose=CalibrationReplay。完整核bytes/资格也只证明模拟协议，不给read_camera_setup_model/AsunImage，不传SurfaceReconstruction或生产消费者 |
| 版本/资格映射 | Joint RevisionId为原string，B/C AssetRef.Version为完整SemVer；CAL 0.3.2-prep §7.4.6B JointQualificationBinding v1已限定接收，本地唯一消费见B.4.6.7（资格绑定消费增量已获主控限定内容接收，2026-10-11）。源Revision（含"1"/source-A/qual-A）保持，SL AssetRef.Version="1.0.0"只表示桥包；完整源Revision/资格/Scope/evidence/watermark/原Task关联必须伴随保存。QualificationSnapshotContent是完整快照技术指纹，不是资格原件签名；Check/runtime/candidate摘要不能代填。原B.4.6.4基线仍仅专用refs，新绑定作为B.4.6.7明确子例，实际binding/native接线仍NotReady |

factory前根显式保Options/Adapters/Input/所有原operation IDs、原Factory/业务Task及完成路径、模块、借读/交付Stream账本、copy/Export输出与预约。复用§9.3根Owner/全量offer原则与上游§7.4.6A的2根/64tasks/8outputs/8MiB上界；桥关联记录有界，不另加全局缓存。业务ValueTask只AsTask一次，WaitAsync仅观察wrapper；即使观察Task结束/Reply.DrainPending，也查询原id.GetOperationState.HeldResources、逐个原Task/资源实际状态。ResourcesReleased不能仅由空native计数或root转交推得。

finally先Closing禁止新消费，用独立有限cleanup token；每实例只登记一次原StopAsync(DrainRequest(originalStopId,remaining),ct)及其原Task，Stop未知/异常逐原id查询、不并发第二Stop。只有Stop确认ResourcesReleased且全部原Task/完成路径/stream/lease真实退出/归还，才登记一次DisposeAsync原Task。Dispose异常/迟到保根；factory失败也收尾实际已产生模块，晚到先写根再执行首次有限恢复，不重Create。业务ExceptionDispatchInfo与有界cleanup错误分开，收尾不覆盖首错。

未知时全量offer包含以上所有字段/Task/输出/资源和预算预约；接收者先强持并在同锁确认原OfferId后才切换Owner。拒绝/丢确认/throw保持原根；Transferred/Retained不等于Released，原Slot查找不删除。迟到Export仅留原Outputs，不触发重建；迟到Publish仍原Store身份回查。共享端口归fixtureOwner，A不关闭/清空Store/Gate/Clock/资格端口；A/B全Released后才能释放共享副本，方法离栈/窗口关闭/GC均非释放证据。

##### B.4.6.4 两个空宿主的确定 Synthetic 装配

完整输入/五包/所有mock端口行为唯一复用上游[§7.4.6A](../calibration-assets/DEVELOPMENT-GUIDE.md#746a-完整-synthetic-小夹具与双-host-实施卡)；下面给本消费者的装配/断言差异。两个Program只引用已发布Core与BCL，按该节公开DTO/JointCodec和完整端口表**本地构造**，不引用Core.Tests，不调用JointSyntheticFixture.Build/RootRegistry私有类，不加载WPF/AsunImage/设备，不创建第三个fixture权威。未在下表改变的每个字段精确继承该唯一卡，包括完整20字段Limits、Division初值/solved值、设备快照、ReferenceGeometry/证书、采样与计划、五组Pose/支持、Fit/Check/Physical报告及规范封存顺序。

| 同一完整fixture输入 | 继承值与本桥应核的输出 |
|---|---|
| 内容/光学/几何 | t0=2026-10-11T00:00:00Z，cam64×48/projector80×60，syn-cam0/syn-proj1/syn-board；6点P0..5的2×3/.04m实测几何，P1.x=.00001/P4.x=−.00001；initial focus .0098/.01176与solved .010/.012保持不同；不拿initial代solved |
| 五包分区/同步 | Fit g0..2、Check g3..4，d=[.22,.25,.28,.23,.27]、Rx=[−.12,0,.12,−.08,.08]；capture-gN/t0+g ms/syn-clock-1/skew1ms/stable100ms。全部Synthetic，实际静止/同步/运动未知 |
| 原图/mask/双层 | white180、距6黑圆中心≤1.8px为20，black10，CameraImage=WhiteImage；white-surface排黑圆，valid再核projector边界；Z(r,c)=cos(a)*d/(-sin(a)*(r−24)/100+cos(a))，Rows=r+6、Columns=c+8−2/Z，原Float64LE。每图/mask3072bytes、每层24576bytes；g1 pixel(10,50)为Z=.25/row16/column50，拒绝row/column颠倒 |
| 支持/原证据 | radius2/4.5/6、支持≤256、fit/check象限3/2，H/其Frobenius同上游公式，inner=outer，mock三误差0；按原全部环带/row-col排序保留。C(label)真UTF8 SYNTHETIC|label|v1及typed/raw真实摘要，不能冒真实局部拟合/计量资格 |
| setup/options/预算 | setup真UTF8 SYNTHETIC|SETUP|cam=0|proj=1|meter|baseline=.02|v1；options(2,128,8388608,1s,64,8)，每入口Budget(2s,3s,32,65536,10000,8388608,1)与父剩余取小；shared gate8MiB/solve1；t0 FixedTimeProvider.TimestampFrequency=1M、显式Advance，正常同步ValueTask无Sleep |
| 容量/进程 | 2根总8MiB（每根4MiB）、task64/output8各根，provider字典8MiB、Store副本8MiB、gate/workspace8MiB分开受限；进程保守同时32MiB，禁止把四种Owner的额度重复挪用。复制/输出须先checked报价，超过剩余明确拒绝，不按“小fixture”省账本 |
| wall期限 | 一个双Host case总10s，业务总≤8s，两个根cleanup各≤1s且仍取case剩余；suite120s/外层180s。入口2s/3s取父单调剩余，query仍该余额，清理不套上游其它30s模板；真实wall限制与Synthetic Advance分开 |

Host A为无UI共同标定producer实验台：在构造前Reserve A根→以完整Factory/provider/Store/Qualification/gate/diagnostics/clock构造JointAdapters与module→登记Solve id1/session100原Task→只在Released成功后取得Candidate→Validate id2→只在Validated/完整Report后Publish id3。各结果先写Outputs再交caller；正常发布核Published(syn-joint-asset,Revision1,candidate.digest)/QualificationIssued=false。若发布未知且原task/resources已实际Released，仅Query id4/OriginalPublishId3求权威Found Published；在途/Unknown不重发，不以ref填成功。finally cleanup id5走B.4.6.3；A输出完整Published/Store闭包给明确fixtureOwner，关闭A不清共享数据。

Host B为独立无UI共同资产回放消费者：独立options/module/root，请求/原Task/输出不复用A，Factory/Observations=null，仅显式借Store/Gate/Clock/Diagnostics及外部资格port。若单独启动，先按同卡公开record/codec预置完整JointStoredArtifact、成功Check规范bytes和全部闭包，不能只传PublishedRef隐含已运行A。Use精确Published、Optics、runtimeVertical、曝光[t0,t0+4ms]、Volume及CalibrationReplay；Resolve id6时DecisionAvailable=false，预期ResourcesReleased/Unknown/无Qualified/Export。外部fixtureOwner显式改true（模块无写API）后Resolve id7，预期Applicable/完整syn-q/Revision1/Synthetic水位及Export，核所有字段、独立Bytes/长度/hash、cam0两个frame、1000、index0/1；然后caller副本修改实验不能改变Store/原Export。可用新id9仅改Purpose=SurfaceReconstruction，预期Unknown/无Export、HALCON及真实重建调用0。finally cleanup id8；B成功是CalibrationReplay协议核验，不将其Export映射成B.CalibrationRef或IM-032资产。

A/B的全部provider/scope/Store/Qualifications/gate端口严格实现上游完整表，不留未定义builder/resolver；Store.Copy只从workspace公开stream。异常注入同时可定位factory、每公开read/open/write/reserve、原业务/Stop/Dispose、回调与移交确认；每次原Task先登记，迟到stream/lease/export先留根，再真实Dispose/隔离。总case超时返回非零并保根，不让Synthetic clock跳变代原Task退出。

##### B.4.6.5 SL-JB 可判定断言与接收边界

| 断言 | 输入/预期 |
|---|---|
| SL-JB01 | 上述A/B完整正常链及B单独启动预置闭包，逐ref/规范byte/hash/长度/Export/资格三态相同；A关闭不破坏B，native/设备/生产发布调用0；只有两根/全部原Task/stream/gate计数真实归零才exit0 |
| SL-JB02 | 缺/跨CaptureGroup、clock漂移、曝光越稳定窗、fit/check重叠、少Both axis/方向证据→producer前检拒绝/不调用Joint solver；g1不对称像素交换row/col拒绝；不凭一致名字/命令自证静止 |
| SL-JB03 | image/mask/层N或8N±1、尾多字节、hash变、mask值2、有效pixel越界/NaN、Support不等原层→拒绝/CAL-108或原观测错误；有padding重包必须新ref。暗心invalid仍可按合格完整环带通过，缺环带/资格不补0/拟合/剔除重拍 |
| SL-JB04 | Published但无资格、撤回/水位gap/晚到资格、Purpose/manifest/decoder/Optics/Volume/曝光不符→Unknown或NotApplicable且无Export；Synthetic不喂HALCON、不用SurfaceReconstruction、不改Revision1为SemVer、不用check/runtime hash填Qualification |
| SL-JB05 | provider.Open迟到/Stream.Dispose挂住、gate late lease、Store迟到发布、Resolve late Export、factory/Stop/Dispose各异常→原id/原Task/资源强持，首错与cleanup错均可查；Stop/Dispose各最多1，未知发布只Query原3不再Publish |
| SL-JB06 | 根满/bytes、MaxImages/ImageBytes/Points/Resident/codec1MiB/支持数上界±1及父剩余不足→打开源/factory/分配前拒绝；cleanup独立有限，拒绝/丢移交确认保全部原根预约；Transferred≠Released |
| SL-JB07 | Profile省Reference、Observation省Group.Packet、Plan省Reference、Check省Evidence，Sampling/Artifact按完整公开投影；provider→workspace→Store实际闭包与EOF、A/B不同实例、caller改副本不改原；首次Joint请求不调用IM-032已校重建/私模型/本地decode，新无setup公开消费见B.4.6.6，实际native/封存/采样资格精准NotReady；仅文档断言，未运行 |

##### B.4.6.6 首次 producer → 无 setup Decode → CAL-JC（0.2.10-prep 主控限定内容接收，2026-10-11）

**范围与来源。** 本节消费[reconstruction-3d 0.2.6-prep §7.6](../reconstruction-3d/DEVELOPMENT-GUIDE.md#76-cal-jc-初始化交接无标定-decode-only独立软件切片)：R3D-Decode-C1/S1六项规格已由主控接收，A1固定HALCON/公开工厂指导限定内容接收（2026-10-11）；本轮读取源SHA256 `a3b0f66f4e16aee006e7c8b3f6712858f640cf4864c672c4ab0f1aba6fe11487`。主控独立重建A/B Mapping538、Request6894（MaxPixels96）、Result3895及五类payload长度/hash一致，仅是文档字节核对。本模块首次观测producer确定消费指导已获主控限定内容接收（2026-10-11），包含双Synthetic Host 3×2反序检查及完整64×48 g1包封存；不撤回原Core/B.4.6.1–5/B.4.7接收。接收只表示观测producer规格：缺其它四组同新manifest/mapping不得Solve，旧五组Solve成功沿B.4.6.4，不声称本新增片已完成五组重解。主控未独立复构新g1 payload向量，不将作者文档oracle记为主控复算；CAL 0.3.2-prep §7.4.6B新资格技术绑定源桥现已限定接收，本地消费唯一见B.4.6.7（资格绑定消费增量已获主控限定内容接收，2026-10-11），不以此扩大本节观测producer接收。真实native/封存/全首次Joint/资格/运行/WPF/性能/物理现场门仍PreparationIncomplete。

唯一首拍链为原采集/白面/参考件Owner冻结输入 → `IStructuredLightDecoder.DecodeAsync` → 原Task退出且ResourcesReleased → 核具名输出/全来源 → 限额封存原payload及mapping/两独立域 → producer公开`IJointObservationProvider`交完整`JointObservationPacket` → CAL-JC Solve/Validate/Publish。producer不执行create/gen/decode/get、重建、find/局部拟合，不调用ReconstructionResult.DiagnosticLayers充作首次结果，不造fake setup。原CAL-JA承担点/环带/采样方法重算与求解，参考件/独立计量及资格Owner承担各自事实。只有真实用途资格另经完整已接收合同闭合后，才允许后续真实重建消费setup；calibration-assets 0.3.2-prep §7.4.6B资格技术绑定桥现已限定接收，期望来自同次Resolve的原Owner封存值，具体消费见B.4.6.7（资格绑定消费增量已获主控限定内容接收，2026-10-11）；本节只交首次观测，不签发或构造资格。

**公开装配。** namespace `Asun.Modules.Reconstruction3D.Decoding`（随既有Core），以及真实适配包 `Asun.Modules.Reconstruction3D.Adapters.Decoding`。宿主先预留B.4.6.3既有有界根/任务位置和各Owner的bytes额度，再以 `new StructuredLightDecodeAsunImageFactory().Create(deployment)`得到独占`IStructuredLightDecodeAdapter`，立即强持；`new StructuredLightDecodeFactory().Create(new DecodePorts(frameSource,maskSource,adapter,acceptedMappings,clock,diagnostics))`得到独立`IStructuredLightDecoder`。二者构造只值校验、不Acquire/不native/不IO；无CalibrationAssets/DI。deployment完整取原部署Owner的`DecodeBackendInfo(RuntimeRevision,Origin,EngineVersion,SupportsBoth,NativeEnvelope,FixedNativeBytes,NativeBytesPerCameraPixel,NativeBytesPerPatternPixel)`，真实Origin=Decoder/EngineVersion=26.05、Both支持及实测envelope/实际运行身份须核原依据，不能自填true或猜系数。Simulator改用下述发布CreateDecode入口，既有AsunImage依赖直接使用，不检查内部。服务每实例只一个作业/无队列；同ID重Decode为R3D-023，终态不能换新ID复用，下一组须新的预留槽/实例和原Owner当前mapping快照，不重新采集。

| DecodeRequest全部字段 / 原Owner | 唯一接线与预检 |
|---|---|
| Version/OperationId/CalculationId/AuthorityScope | Version=StructuredLightDecodeFactory.Version（r3d-decode-v1）；两个非复用字符串ID在根预登记并关联原Joint组/Solve身份，AuthorityScope来自原宿主授权。IDs不从FrameId/PointId临时拼成恢复身份 |
| CaptureGroupId/DirectionId/InputRevision | 原同姿态采集组、一个物理光学方向、原输入快照revision；不把V/H拆成两物理方向。InputRevision为原Owner核完整采集/派生mask的有界快照，不以相等名字自证同组 |
| Frames | 非default ImmutableArray<FrameRef>，完整原ordinal0..F−1/单方向Mono8、同camera W/H；每FrameRef的FrameId/实际payload Revision/Kind/Width/Height/PixelFormat/AcquiredAt/SequenceOrdinal/DirectionId/PatternId/ExposureProfileId全原值。含黑/白/V-H Gray和四步Phase，按SourceIndex−1保原序，不删黑白、不按亮度/到达顺序重排；source Bytes hash包含原stride padding |
| Pattern | 原PatternSpec.Profile、HybridBoth、实际ProjectorWidth/Height、MinStripeWidth、SingleStripeWidth=null、Normalization=global、MinGrayDifference、CapturePhaseDiagnostics=false、OrderedPatternIds原序；Sequence=完整r3d-sl-sequence-v1/原ManifestRevision/全部binding（原PatternId/ordinal/Kind/Axis/RoleOrdinal/PhaseStepIndex/生成图hash），Diagnostics=null。沿B.4.7既有角色映射而不引其重建工厂；投影生成hash不是相机payload hash |
| Acquisition | 原CaptureEpoch/TimingProfile/MaxSequenceSpan/MaxStereoSkew/SceneStationaryVerified、每帧完整12字段FrameTiming，原attempt/device/clock/曝光/稳定窗/ExposureRevision/ExpectedOrdinal/ExpectedPatternId；集合必须boxed非default ImmutableArray，不通过可变列表或自定义getter隐藏源改变 |
| Evidence | DecodeCaptureEvidence完整StableEvidence/QualityEvidence/CaptureGroupId/CaptureEpoch/ClockEpoch/ClockDomain/StableStartNs/StableEndNs/CaptureSkew/MaxCaptureSkew/MinStableWindow；CaptureEpoch=Acquisition.CaptureEpoch，ClockEpoch仍独立原事实，不能把两者强行改成同名。每FrameTiming.ClockDomain同原域，全部曝光/各图案稳定窗在组窗内；CaptureSkew为最早/最晚曝光中点差按源合同checked两倍ns/向上100ns tick，不截整ms；阈值取原TimingProfile与JointProfile相容值 |
| DirectionMapping | 完整原DecodeDirectionMapping.Reference；原Owner提供正文/RuntimeRevision/PatternProfile/ManifestRevision/双方W/H/一基ColumnObjectOrdinal与RowObjectOrdinal/State/Origin/GoldenEvidence/MaxErrorPixel/全部Probes，经公开StructuredLightDecodeCodec.EncodeMapping核正文hash。factory AcceptedMappings只0..1个已核DecodeAcceptedMapping，两个Evidence bool来自原接收记录；不能自声明Accepted或array[0]是列。MaxErrorPixel取已接收Golden计划，不设物理默认值 |
| Auxiliary | DecodeAuxiliarySources.BlackFrameId/WhiteFrameId精确为原Sequence黑白帧，decoder不额外Acquire。WhiteSurface=完整DecodeWhiteSurfaceRef.SourceId/Revision/Width/Height/CaptureGroupId/ClockEpoch/ParentWhiteRevision/DerivationRevision，由既有producer/白面Owner给原0/1 mask；父White必须原payload revision，方法引用真实，不能decoder按暗点补白面/平面/材质真值 |
| Budget/Timeout/DrainTimeout/Deadline | DecodeBudget.ManagedBytes/NativeBytes/ResultBytes、MaxInputBytes、MaxPixels、MaxFrames、MaxRowStrideBytes七值均显式。Managed/Native/Result各64MiB..8GiB，MaxPixels同时覆盖N=camera W×H和G=projector W×H，F≤256；checked((F+1)*maxStride*H)≤MaxInputBytes（含mask）。Timeout100ms..30min、DrainTimeout1..60s、Deadline取父最早截止；不足下限在factory/source前拒绝，不给每组重置父期限 |

frames source是原公开IFrameSource，mask source是IDecodeMaskSource；Core唯一取得/归还原IFrameLease及IDecodeMaskLease。adapter只借它复制的immutable DecodeFrameSnapshot/DecodeMaskSnapshot，不重复Acquire、不代宿主Dispose。mask/每frame实际Bytes恰stride×H、stride在[W,maxStride]，Core先核含padding全payload hash再逐行复制无padding像素；producer直接消费公开输出，不另读旧lease当“更原始”结果。不接受source变化/错父White/跨组/跨clock，未知资源不称Released。

**DecodeReply/封存逐字段。** 只有原run真实完成且Operation.State=Completed、Drain=Released、Error=null、Result非null并核原身份，才开始producer采用。原OperationId/CalculationId/RequestSha256（公开codec.HashRequest）及Input/CaptureGroup/ClockEpoch/Origin/Runtime/Mapping/Manifest/Stable/Quality/SourceFrames/WhiteSurfaceSource必须逐项匹配冻结请求/Info；Query结果保留限64MiB，ResultNotRetained时保原回执自己的immutable结果，不因Query.Result=null重Decode。非成功/取消/DrainUnknown均不交JointPacket，不把全commonValid=0当质量通过。

| 具名公开payload / 必保来源 | JointObservationPacket与ContentRef |
|---|---|
| ProjectorRows | Axis=Horizontal、ObjectOrdinal=原mapping.RowObjectOrdinal；Coordinates为原camera全幅projector-coordinate-f64le、FormatRevision=1、恰8N bytes，projector row pixel；逐实际bytes hash→`new ContentRef(new Digest("SHA-256",raster.Sha256),raster.Format,new RevisionId("1"),checked(8L*N))`→Packet.ProjectorRows |
| ProjectorColumns | Axis=Vertical、ObjectOrdinal=原mapping.ColumnObjectOrdinal；同格式/长度/单位，projector column pixel；独立核bytes/hash→Packet.ProjectorColumns。不因Both返回对象反序交换具名结果、不改原ordinal或+0.5 |
| Rows.Domain/Columns.Domain | 各自原valid-mask-u8/1、N个0/1 byte，分别核SHA/长度/原pixel坐标并封存为原观测证据闭包；不合并丢失两原域、不套white-surface/Surface.mask。域内两层各自有限且在projector对应边界，域外对应8byte唯一qNaN LE 000000000000f87f |
| ValidMask | 原valid-mask-u8/1、N bytes/hash，逐pixel恰Rows.Domain AND Columns.Domain→Packet.ValidMask。单axis可观测的原值继续保其原层/域，共同valid0不作JointSupport，即使其另一层有值；合法坐标0与unknown不可混 |
| WhiteImage/BlackImage | 原image-gray8-rowmajor/1、N bytes/hash、UInt8原码/no padding/no normalize→Packet.WhiteImage/BlackImage。白场来自Auxiliary对应原frame，CameraImage直接同完整WhiteImage ContentRef；去padding产生新payload摘要，保原FrameRef含padding摘要/stride关联，不能沿旧hash |
| WhiteSurfaceMask | 原valid-mask-u8/1、N bytes/hash，WhiteSurfaceSource完整等原Aux.WhiteSurface，父White/Derivation/组/clock全保真→Packet.WhiteSurfaceMask；不以valid域代白面mask，不由decoder补物理资格 |
| Group/Optics/Pattern/证据/Points | Group原Id/PoseIndex/CaptureGroup/ObservedAtUtc；Optics仍原两端设备/frame/PhysicalMapping。JointPattern.Manifest/DirectionMapping/Decoder由原Owner展开Sequence.ManifestRevision、mapping正文及实际backend版本，不从RevisionRef猜路径/format/length。Stable/Quality来自Evidence原ContentRef，ClockEpoch同原值，CaptureSkew同原证据，StableWindow为原组End−Start checked/与批准阈值核。Points仍由既有producer/参考件/采样Owner给完整点号/实测中心/环带/Mapping/Qualification；只有两域commonValid1/white面1且真实原质量依据符合时Support才取有限两层。decoder不生成点、采样资格或中心拟合 |

映射正文只通过已接收StructuredLightDecodeCodec.EncodeMapping取得实际r3d-direction-mapping-v1/1 bytes，SHA必须等Reference.Sha256；不能封存两个indices或Golden标签替代正文。Manifest/实际部署/quality/stable原件的Format/Revision/ByteLength来自原Owner的完整源清单（RevisionRef只有Id/hash），hash逐实际原bytes核；decoder版本通过原部署Owner的完整JointAdapterVersion与DecodeBackendInfo关联证据提供，BuildDigest仍实际构建原bytes摘要，不拿Request/Runtime hash冒build。R3DO EncodeResult保完整source/timing/mapping关联供原Replay证据，但不是cp-joint-observation-v1或其ContentRef替代物。两个独立域/原帧含padding谱系及完整请求/mapping内容由本地有界producer原证据Owner关联保留，原QualityEvidence/StableEvidence继续按其Owner的真实内容合同封存；不让只有Id/hash的引用偷偷证明新附加证据已持久化，不发明新公共存储协议。

在producer根暂存全部8个raster及元数据/copy，核checked格式/长度/EOF/全部SHA/domain/唯一qNaN、来源和父时序；全部通过后才采用6个Joint payload引用（两域另保）。JointObservationPacket用公开JointCodec.EncodeObservation（省Group.Packet）产生实际规范bytes/新final Packet，Group引用该完整摘要，再进入原IJointObservationProvider.ReadAsync/OpenContentAsync→Core workspace→Store公开复制闭包。两Domain的ContentRef及完整DecodeResult/source关联由原producer证据Owner限额强持，未确认接收前不释放本方Outputs；JointObservationPacket没有独立域字段，不能声称JointStore自动保存未声明的两域。CAL-JC Store只沿其公开闭包处理6payload/包/原Evidence/Pattern引用，另外两域及源请求的保存/原件读取归producer既有证据Owner（Synthetic为fixtureOwner），不得造额外Joint字段。points没有可靠实测/完整环带/采样资格时不补造，CAL-JC按原门拒识；初始化接口可先于setup不代表物理采样可用。Origin=Simulator的所有新包/manifest/mapping/源证据只在Synthetic/1、CalibrationReplay链可消费，不能授SurfaceReconstruction/真实采样/资格。

**有界Owner与取消恢复。** 复用B.4.6.3原root/输出槽/offer/Store Owner，逐组临时decoder/sim附在该根，不建第三根服务。发任何Factory/Decode/Stop/Dispose/封存之前有槽，原ValueTask只AsTask一次；每组至多五Host原Task（run/core-stop/core-dispose/sim-stop/sim-dispose）及producer封存/完成路径均计原64task额度，内部524task由decoder自己的账本持有并计资源，不能塞进五个外Task后误认为全排空。借用端口的实际来源Owner保持到原lease归还；decoder/backend/源在途不以copy/封存Task结束或Native0解除根。

关闭使用原OperationId和独立有限token：decoder.StopAndDrainAsync(originalId,remaining,cleanupCt)保原Task；真实Released且原run实际退出/故障已观察之后首次DisposeAsync，失败保根。sim.StopAndDrainAsync/DisposeAsync同样保存原Task并核snapshot active/pending/lease=0/Acquired=Released；五原Task全部真实退出才关闭该组。只停止本根/本组，不关闭其它消费者借用端口，真实adapter没有可猜测的额外Close/Dispose接口，由decoder公开停止及其原Owner释放账本确认。父Slot.Closing后迟到DecodeResult只登记Outputs、拒绝producer发布；迟到frame/mask lease先由decoder登记再唯一归还。已开始内容封存的stream/copy也强持原Task，取消不发布半Packet、不重Decode/重Create绕过未知；provider stream仍Core唯一Dispose，Store只通过workspace复制。首业务ExceptionDispatchInfo与各cleanup异常分开；offer先强持全部Task/decoder/sim/源/mapping/封存输出与额度后确认，否则原root保留。Transferred不代表Released。

报价先checked N/G/F/stride：沿源Managed=4*MaxInputBytes+192*N+8192*F+1024*Probes+262144，Result=22*N+8192*F+1024*Probes+16384；native为原部署实测Info的fixed+F*N*CameraCoeff+F*G*PatternCoeff。producer另计8原raster完整132/22N bytes、封存copy/规范Packet/两域/关联与原ContentRef；不挪decoder预算给Store/caller，不把预约当实测峰值。下游与producer都取同父剩余，资源/期限不足source前拒绝，无目标性能NotEvaluated。原case10s/suite120s/外层180s保持；新case业务总≤8s、根cleanup总≤2s，各首次Stop/Dispose及恢复观察取剩余≤1s，正常每组即时释放不真实Sleep。虚拟Advance只驱动测试，不冒真实资源归还。

**两个原Synthetic Host的fresh首次子例。** 原B.4.6.4 CAL-JC 64×48/80×60全fixture及B.4.7 D01/D02不变。新增空宿主A（首次producer）/B（离线观测消费者）首先精确继承上游§7.6.6的decode-A/decode-B全字段14帧/3×2相机、12×8投影器、完整Evidence/Aux/Backend/Mapping/Budget(64MiB,64MiB,64MiB,1024,96,16,5)、1s/1s/null Deadline及两反序mapping；B含每row[99,88] padding。直接用公开BCL/DTO、发布ReconstructionSimulationFactory.CreateDecode(script,clock,gates,diagnostics)→立即持sim→StructuredLightDecodeFactory.Create(sim.Ports)→Validate→Track原DecodeAsync→有限观察，不引用Core.Tests/helper/DI/真实AsunImage。两Host具名六payload相同，原mapping各538/Request6894/Result3895及源五类payload48/48/6/6/6 length/hash依唯一上游oracle核，native0/原frame14+mask1=15各归还一次；本方桥报价含8raster132bytes+全部封存/来源copy，根4MiB内预留，另decoder64MiB×3及sim2MiB独立预约，进程256MiB保守限。

3×2小图不能满足CAL-JC六实测点/完整环带，不能给它补点后冒Solve成功。该正常子例完整核Decode→所有raster ContentRef与两域的字节/Owner交付；没有3×2的实测Optics/参考件/环带输入，桥在JointInput/JointPacket组装前明确SL-VIS-003/SamplingInputInsufficient，不造3×2光学参数或向CAL提交未知Input、solver native调用0。这是正常边界拒识链，原64×48完整Synthetic Solve/Validate/Publish/Resolve成功另沿B.4.6.4，不拿小decoder图覆盖该fixture。为验证真实尺寸的完整正常首拍协议，A/B另按下一张**只读原fixture派生卡**运行一个完整g1包：不是新测试工程/第二套物理真值。

| 64×48 g1 完整正常bridge子例（只在本地fresh副本，不改原fixture） | 每个新增字段及既有输入继承 |
|---|---|
| source/identity | 继承calibration-assets §7.4.6A g1原64×48白/黑/白面/valid与全部6 Points/环带/local map/Optics/几何/证书/采样/Plan。t0+1ms/capture-g1/syn-clock-1；ScriptId=sl-joint-decode/Seed7，OperationId=sl-joint-decode-g1/CalculationId=sl-joint-decode-g1-calc，AuthorityScope=fixture-only，DirectionId=joint-dir，InputRevision=rev(sl-joint-input-g1)。rev为SHA严格UTF8(id)的Synthetic身份，不是物理证据 |
| 原14帧/完整Sequence | PatternId/Kind/Axis/RoleOrdinal/PhaseStepIndex逐项继承§7.6.6 black/white/vg0/vg1/vp0..3/hg0/hg1/hp0..3原顺序；FrameId=J1-f0..13、camera64×48/Mono8/stride64，Black/White原g1实际bytes；Gray全60/90、Phase全70/100/130/100相机byte，投影器80×60生成图Black0/White255/VGray column<40及floor(column/20)偶奇、HGray row<30及floor(row/15)偶奇、Phase全64/128/192/128，实际4800bytes hash。完整FrameRef其余AcquiredAt=曝光End UTC/ordinal i/DirectionId joint-dir/ExposureProfileId syn-exp-g1。此14帧明示synthetic布局，不宣称实际HALCON80×60生成数量 |
| Pattern/原Owner展开 | PatternSpec.Profile=rev(sl-joint-pattern)、HybridBoth/80/60/4/null/global/30/false/完整14PatternIds，Sequence版本r3d-sl-sequence-v1；ManifestRevision=RevisionRef(sl-joint-manifest,原C(sl-joint-manifest,synthetic-pattern-manifest).Digest.Hex)。Manifest标签沿上游C真实UTF8 SYNTHETIC\|sl-joint-manifest\|v1，完整14bindings及原生成图bytes另随冻结Request/source清单保存；它只为Synthetic模拟manifest身份，不能冒真实生成manifest正文/布局。Diagnostics=null |
| Acquisition/Evidence | CaptureEpoch=epoch-joint-g1、TimingProfile=rev(sl-joint-timing)、MaxSequenceSpan1s/MaxStereoSkew0/SceneStationaryVerified true、14 immutable timings；base=1000000ns，每timing为原frame/attempt-joint-g1/epoch-joint-g1/syn-device/syn-clock域、曝光base+i*10000+1000..+2000、step稳定base+i*10000..+3000、rev(syn-exp-g1)/i/PatternId。Evidence原C(stable-g1)/C(quality-g1)对应RevisionRef(stable-g1/quality-g1,实际C bytes hash)，capture-g1/epoch-joint-g1/syn-clock-1/syn-clock、组窗[base,base+100000000]ns，Skew130µs/MaxSkew2ms/MinStable50ms。这是显式fixtureOwner新增采集事实，原g1旧skew1ms不冒作新值；最终Packet使用此新证据/130µs/100ms |
| Auxiliary/Backend | Black=J1-f0/White=J1-f1；WhiteSurface=DecodeWhiteSurfaceRef(sl-joint-white-g1,RevisionRef(同Id,原g1白面Nbytes hash),64,48,capture-g1,syn-clock-1,原J1-f1.Revision,rev(sl-joint-white-derivation))、maskStride64/原0-1byte。Backend Runtime=syn=RevisionRef(synthetic:sl-joint-decode,SHA256(UTF8(r3d-decode-simulator-v1换行sl-joint-decode换行7)))，Origin Simulator/EngineVersion Synthetic/1/SupportsBoth true/NativeEnvelope rev(sl-joint-envelope)/fixed及两coeff0 |
| 完整Mapping | Version=r3d-direction-mapping-v1/Reference.Id=sl-joint-mapping、Runtime=syn/Profile=rev(sl-joint-pattern)/Manifest同上、camera64×48/projector80×60、ColumnOrdinal1/RowOrdinal2/State Accepted/Origin Simulator/GoldenEvidence rev(sl-joint-golden)/MaxErrorPixel0；3 probes(camera10,50→row16,col50,obj1=50,obj2=16)、(10,30→16,30,30,16)、(20,30→26,30,30,26)。独立软件公式取原g1 d=.25/Rx0/Rows=r+6/Cols=c，不用实际运行返回制造expected；公开EncodeMapping/SHA后填Reference，Request用完整ref，外部mock部署Owner核正文/oracle后提供两Evidence bool true |
| RawObjects/Budget/完整script | Object1=Columns/Object2=Rows、W64/H48，两Domain恰原g1 valid mask，域内values取原g1Float64层、域外null，SupportUnion同mask；Runtime=syn/NativeBytes0。Budget(67108864,67108864,67108864,65536,4800,16,64)，Timeout1s/Drain1s/Deadline=null。ScriptVersion=r3d-decode-simulator-v1、上述全部Request、14 SimulationFrame(joint-dir,完整FrameRef,64,实际bytes)、原mask引用/stride64/bytes、Backend/Mapping/RawObjects/SupportUnion、Steps.Empty、MaxSnapshotBytes2097152；没有setup/calibration/重建字段 |
| 出参/实际封存/JointPacket | RequestSha256由公开codec核全部冻结字段、SourceFrames原14项/新时序证据、Rows.Axis Horizontal/Object2、Cols.Vertical/Object1。N3072/G4800/F14；原source46080bytes，8raster67584bytes；Managed预约1231872/Result201728、sim1675264≤2MiB，三预算各64MiB，不把这些软件费用称真实native峰值。raw invalid的原有限层位置在Decode输出变唯一qNaN，产生新坐标ContentRef，其他有效位置不变。mapping/body/两原domain一并封存；白场同Camera引用。最终Points全部继承g1原6实测点/完整Support/原Mapping/SamplingQualification，每个Support与新层有效pixel逐字节复核，暗心不直接采样。只有新Pattern、Skew和相关证据/ref字段更新至同fresh source，EncodeObservation省Packet再给新final Group.Packet；不改原fixture包/hash |

g1子例的JointPattern全部字段为Width80/Height60/MinStripe4/MinGrayDifference30、上述Manifest实际ContentRef、`JointAdapterVersion`取原fixture decoderVersion（完整Id/Revision1/RuntimeVersion Synthetic/1/实际UTF8 decoder标签BuildDigest）并由fixtureOwner保其与冻结syn的模拟关联、DirectionMapping为实际R3DM ContentRef（format r3d-direction-mapping-v1/revision1/codec实际长度/hash）。该关联只是模拟部署证据，不冒代码构建/真实Golden。其6点/白区环带中心来自原CAL-JA fixture，producer不拟合。provider.ReadAsync返回这个完整finalPacket，OpenContentAsync供原14frame/source/mapping/两域/所有6payload及包真实bytes闭包；原producer-copy、Core workspace与Store复制路径同B.4.6.2。

该g1只验证完整可用首拍观测包进入CAL-JC provider预检/封存，而不替代整个三Fit/二Check求解输入：真实或模拟JointInput必须所有组都与同一JointPattern/Decoder/Manifest/DirectionMapping兼容，不把一个新g1夹进旧五包直接Solve。若没有其它四组同新manifest/mapping的完整输入，则保持未组装/不调用Solve；原B.4.6.4完整成功求解仍沿原五包，不能宣称本新增子例已全量解码或求解。这是本任务首次观测producer边界，CAL-JC本身已接收范围不重审。两个原Host都可分别fresh执行3×2反序检查与g1封存，B仅消费其自己的原公开结果/副本，不隐含依赖A已运行。

g1五类裸payload的文档oracle按上表点/黑圆/有效域公式独立构造（非decoder/Host实跑）：Rows 24576 bytes/SHA256 `66a30d6c791be9b1c73e8cb16b5a27697808e3f549b7bbb96776a75d3d2371fd`；Columns 24576/`58954fe57af183ea97787b73a054ef61192513476d9264939ac437b121b4c491`；Valid/两Domain/WhiteSurface各3072/`30399550fbd6ff6875b3f9d1d6430e8a48b4475d77b8e9c0770230da4b063a5f`；White/Camera同引用3072/`0ebbad7f0dcc715915bfec986cf9a1dbb691aaafa06d5328fe6665e5c1984b05`；Black3072/`d628561804c1cff2c1e00392265b905d01cbd24887b2d5e49a18adbca41dc724`。这些摘要核实际qNaN/原pixel字节和producer新ContentRef，不替代旧B.4.6.4原有限层/包/hash。只在本地正常case中逐字节比对独立expected，原完整fixture不变。


| 新断言 | 正常/反例预期（复用根/Store/两Host，尚未运行） |
|---|---|
| SL-JD01 | A/B原§7.6.6完整14帧正常无setup Decode，五payload length/hash及8raster/完整来源/两个反序mapping保真，15源lease各归还一次；3×2缺实测采样输入时组装前SamplingInputInsufficient、不造JointPacket/成功。64×48 g1完整正常Packet/6点环带与实际payload封存通过所有字段/EOF/hash核对，但缺其它四匹配组不启动Solve，不借旧组或fake setup |
| SL-JD02 | manifest顺序交换/帧ordinal重复、mapping错排列/伪对称证据、不同runtime/Manifest/Profile、父White错、CaptureEpoch或ClockDomain不符、少Both/组窗越界→源前001/002/003/004/007/015/021准确；不重排修复、不猜array顺序。bytes含padding摘要与无padding新ContentRef分别保留，不冒用原hash |
| SL-JD03 | 在fresh上游A脚本副本只将原Object2（Rows）camera(0,1)的Domain改true/Values改合法0，并将SupportUnion该位改true；Object1/Columns仍domain false/null，其他全部原字段/Probes/源保持，不修改原oracle。具名两原域/单axis原值保持，共同Valid=AND；qNaN位错/域内NaN/有效mask与两域不符/white-surface2/hash或尾字节改→整组拒绝，0合法、unknown不补0、不产生Support。缺白面/实测/采样资格仍原CAL拒识，不从decoder暗点编真值 |
| SL-JD04 | 发原Decode后在MaskAcquire、CallbackExit、MaskRelease CompleteLate gate处取消；Stop只观察有限、Unknown/无Packet，原Task/source/adapter/封存资源持续强持。仅放本case gate后真实run/stop/dispose及15归还退出再退槽，首业务错仍保留；封存失败/晚到Result不交JointPacket、不再次Decode/Create。offer拒绝/丢确认全部原root保留 |
| SL-JD05 | 工厂/预算/MaxPixels小于G4800（小夹具96）/MaxFrames/stride上界±1/父期限不足、SourceBytes或闭包损坏→copy/source前拒绝。Simulator仅CalibrationReplay/非物理sampling，生产用途调用0；资格绑定只沿已接收CAL 0.3.2-prep §7.4.6B及本地B.4.6.7（资格绑定消费增量已获主控限定内容接收，2026-10-11），本首次观测子例绑定调用0；不用CheckEvidence或runtime hash当完整资格快照指纹，原B.4.7成功重建诊断支持不扩大 |

新增Bridge Benchmark只在§13原测点上分别记录Decode原接纳→真实归还、具名/两域核验、payload/Mapping/Joint规范hash/封存copy/Stream归还/根移交；cold/warm/P50/P95/P99和资源实测目标缺失仍NotEvaluated。第一轮自审对照上游公开形状逐字段及qNaN/域/格式/原stride/ordinal/Mapping/技术资格边界；第二轮走两Host正常拒识/g1完整封存与取消迟到/顺序错/资源真归还/有限收尾，未将3×2小图、单g1或Synthetic替换真实五组采样/完整求解。无工程、测试文件或过程报告；实际C#编译/双Host/HALCON/native/完整首次Joint调用/WPF/性能/物理/现场资格均未执行。



##### B.4.6.7 JointQualificationBinding v1 的完整资格消费桥（0.2.11-prep，资格绑定消费增量已获主控限定内容接收，2026-10-11）

**范围与只读来源。** 本节只消费[calibration-assets 0.3.2-prep §7.4.6B](../calibration-assets/DEVELOPMENT-GUIDE.md#746b-两消费者资格绑定技术桥jointqualificationbinding-v1)已经主控限定接收的公开桥；本轮首次读取源SHA256 `b20eeb06ff1e1e34e2e9b9305384f2cd1ceb2b63c981715c10d660584ea275aa`；随后复读原Owner接收状态同步稿SHA256 `7e57a372cc36ea7ae9fb58b36afac356dd4880510e80437b40901e0b33f2eb83`，公开形状/取得流程及四oracle一致，不修改源指导。沿源命名空间`Asun.Modules.CalibrationAssets.Joint`和既有`IJointQualificationPort/JointCodec`，不新增SL公开DTO、resolver、codec或资格Owner。源桥及主控四个软件oracle核对已接收，资格绑定消费增量已获主控限定内容接收（2026-10-11）；本节未运行Bind/C#/Host/native/Store/全首次Joint/WPF/性能或物理验收。B.4.6.6首次观测限定接收、缺其余四组匹配输入不得Solve及B.4.7成功诊断支持域保持。

技术快照指纹仅绑定收到的完整纯值，既不是资格原件/签名，也不证明Owner可信、物理适用或生产放行。`JointQualificationBinding.Bind(snapshot,request)`不查询Authority、不签资格、不证明caller来源。支持域是同一次Resolve捕获的资格快照到装配前原Owner复查仍精确相同且有效；快照变化时新操作重新Resolve，不在当前操作改Expected或无界复查。宿主真实执行/激活/提交仍按原事务重核权限、资格、水位及CAS，纯值绑定不是下游提交的原子事务。

**原Owner及同次捕获，唯一顺序。**

1. factory前沿B.4.6.3预留根、任务、输出和完整费用；由宿主显式端口配置确定实际Qualification Owner对象，先注入本地转发观察器实现既有`IJointQualificationPort`，再构造module。不根据待绑定snapshot的Authority选Owner，不在Resolve后替换注入端口。观察器转发既有查询/Watch语义，不增加查询、缓存最近值或新公开API。
2. `module.ResolveAsync`内部一次`Qualifications.ReadAsync`调用前，同根登记原Query、`SolverExecutionContext`、token、实际Owner对象及任务条目；Owner返回的原ValueTask恰一次`AsTask()`，强持这个原Task。完成路径先深复制完整响应（含全部嵌套值/集合）、编码并封存原规范bytes及ContentRef写根，再将保持原语义的值交Core；调用方或待绑定副本后续修改不影响封存值。复制/编码失败保留实际返回的原响应/错误和任务责任，Host Unknown，不制造成功捕获。
3. 原`Query.OperationId=execution.OperationId=resolveId`；一次Resolve只允许一次对应Owner Read。0次、多次、重复冲突、错误执行ID或来源不确定统一Host Unknown，不另查询一份“最近快照”填缺口。原Resolve Task、Owner Task和各完成路径都在同根登记；GUID相等只用于定位，不等于来源证明。
4. 仅原Resolve Task真实退出且原Reply `Completion=ResourcesReleased/Error=null/Value.Status=Applicable`、完整Qualified/Export均存在时继续。逐字段核Qualified的Asset/QualificationId/QualificationRevision/Watermark五字段/ValidFrom/ValidTo等于捕获snapshot；Export.Asset=snapshot.Asset，snapshot.CheckEvidence=原Query.CheckEvidence，Query.Use=本次RequestedUse，ContentDigest=RequestedUse.Asset.Digest。保存原Reply/Export全部字段与独立Bytes，核File规范长度/hash及原B.4.6要求的frame/index/单位/尺寸。RuntimeValidationEvidence路线与用途沿Resolve预检，不由hash推断证据正文。
5. 装配前同一实际Owner对象用独立非空`recheckId!=resolveId`直接调用下列原公开端口；先登记request/execution/token/原Task，再启动并有限观察。宿主是这次直接查询的ledger Owner，不声称Core创建了这个作业。响应完成路径同样先存完整深副本和规范bytes；核返回Asset和Scope.Asset仍为本次Asset，ActualOptics/Pattern/ActualVolume/Purpose仍对应原查询。关联缺失或其它asset的撤回回执返回Host Unknown，不能当本asset NotApplicable。

```csharp
owner.ReadAsync(
    new JointQualificationQuery(originalQuery.Use, originalQuery.ContentDigest,
        originalQuery.CheckEvidence, recheckId),
    new SolverExecutionContext(recheckId, remainingBudget), linkedToken);
```

`remainingBudget`取父单调期限/各维剩余与原入口预算的小值，不延长父期限；`linkedToken`关联caller与该有限业务期限。原Owner返回当前权威的完整不可变查询快照，不能只查通知或水位。即使仅ObservedAtUtc/ValidUntilUtc变化，也按完整指纹变化拒绝旧绑定；无法提供精确当前快照的来源只能Unknown，不删时间字段凑相同hash。

6. Expected从**原封存s1/同次ResolveQualified**取得，待绑定snapshot是独立副本；Rechecked字段从原复查s2取得。复查真结束后立即在同根准入锁内核`Closing=false`、无已知invalidation/epoch gap、期限/水位有效、父预算仍足，调用Bind，保存完整结果与伴随记录，然后才允许Applicable的本地下游请求组装。中间异步等待、排队或已知失效使旧绑定无效；新操作重新Resolve，不复用旧Expected。若没有Watch/权威当前性证据，不把空通知序列称无失效保证。

**逐字段绑定，不复制上游实现。** 只调用上游公开`JointCodec.EncodeQualificationSnapshot`、`ComputeQualificationSnapshotDigest`和`ComputeDigest`；不新增解码入口或本地序列化。完整规范顺序含`Status,Asset,Scope,CheckEvidence,Id,Revision,Watermark,ValidFrom,ValidTo,RuntimeValidationEvidence`；Scope的Asset/ActualOptics/Pattern/曝光/ActualVolume/Purpose及所有嵌套值、两种evidence完整引用全部纳入。字段/集合逐值、Ordinal比较，不依赖record内数组引用相等。水位的Authority/Epoch/Revision/ObservedAtUtc/ValidUntilUtc全部纳入，不从projection排除任何时间或evidence。

ContentRef固定`Format="cp-joint-qualification-snapshot"`、`FormatRevision=RevisionId("1")`、ByteLength为实际规范长度、Digest为完整bytes SHA-256。单规范输出≤65536 bytes、单字符串≤256严格UTF-8 bytes，先checked计长后分配；未知enum、非法surrogate、非有限值/溢出拒绝。原Qualified缺必需字段可编码合法空形状作审计，不可Applicable。直接codec非法值抛ArgumentException、超限抛ArgumentOutOfRangeException；Bind转有限Unknown（Binding.Encoding/Version/Budget）且无Projection，不逃逸部分成功。Host自己的捕获/费用失败同样拒绝消费，不能改合法Expected来使helper通过。

| 上游公开对象/字段 | 本地唯一来源与核验 |
|---|---|
| JointQualificationExpectation：Status、Asset、QualificationId、QualificationRevision | 原封存s1.Status/Asset/Id/Revision；不取待绑定副本、不从Published状态制造Qualified |
| Expectation：Watermark、ValidFrom、ValidTo、ResolveQualified | 原s1完整水位/有效窗；ResolveQualified是同次成功Resolve原Qualified，核其全部字段，不仅有效时间。非Qualified原值不制造Qualified引用 |
| Expectation：ExpectedScope、ExpectedSnapshotContent | 原s1.Scope的完整深副本及原s1规范ContentRef；待绑定内容改变不能重新编码并覆盖Expected |
| Expectation：ResolveOperationId、QualificationQueryOperationId | 原根中Resolve/其内部Owner Query实际ID，非空且相等；原Query/execution/Owner/Task关联必须存在 |
| JointConsumerBindingRequest：Expected、RequestedUse | 上述完整Expectation、本次原Use深副本；Asset精确，非时间Optics/Pattern/Volume/Purpose相等，有序曝光闭区间在原Scope覆盖窗和资格有效期内 |
| Request：RecheckedWatermark、RecheckedStatus、RecheckedSnapshotContent、WatermarkRecheckOperationId | 同实际Owner复查s2完整水位/状态/规范ContentRef及实际新Query ID；不以“没有通知”替代响应，不取伪全零hash |
| Request：EvaluatedAtUtc、BridgePackageVersion | 根准入锁内原Clock当前UTC，水位有效闭窗内；严格"1.0.0"只表示桥包SemVer，不表示资产/资格源修订 |
| JointConsumerBindingResult：Status、Projection、SnapshotContent、Findings | 原helper结果完整保存；只有Applicable且Projection/两个快照ContentRef一致才组装。合法非Applicable可保SnapshotContent审计，Projection=null；非法编码/版本/容量时SnapshotContent也null。保原Finding Field/Status/MessageKey/Evidence，不把Unknown改成PASS |
| JointConsumerBindingProjection：BridgePackageVersion、SourceAsset、SourceQualification、QualificationSnapshotContent | 完整防御复制值；SourceAsset原Id/任意Revision/Digest，SourceQualification全部字段，ContentRef等原封存s1及Result.SnapshotContent；不只保投影的几个hash |
| Projection：StructuredLightAssetId、StructuredLightAssetVersion、StructuredLightAssetSha256 | 分别SourceAsset.Id.Value、"1.0.0"、SourceAsset.Digest.Hex；Id满足本方1..128 ASCII `[A-Za-z0-9._:-]`，hash为64位小写；非法Id拒绝，不清理或改名。源Revision="1"/source-A与资格Revision=qual-A仍原string，不改成SemVer |
| Projection：ReconstructionAsset、ReconstructionQualification | 仅保上游JointTechnicalRevisionFingerprint完整(Id,Sha256)投影，前者原asset id/digest，后者原资格id/完整snapshot digest；不在SL复制IM-032资格codec、改其API或代批准它的实际消费者接线 |

沿上游Bind唯一优先序：请求关联/桥版本/有限形状及ExpectedContent格式→可信**同asset**复查Suspended/Revoked/Expired优先NotApplicable（RecheckedStatus），Unknown或缺完整水位/指纹Unknown→原snapshot Status/Content/Scope与原Expected不等Unknown，原一致snapshot撤回NotApplicable→Asset/Scope/有序曝光及有效窗不等NotApplicable，必需字段缺失Unknown→完整ResolveQualified/身份/修订/有效期一致，水位五字段与Expected及recheck全等、recheck完整Content=原ExpectedContent、EvaluatedAt在有效闭窗内→Applicable。ValidFrom必填，ValidTo=null为无上界，不伪造日期。epoch/evidence/任一水位时间变化都是Unknown，不删字段；合法源撤回优先于旧Qualified和指纹变化。Host来源/关联失败在helper前Unknown；没有真实复查不能伪填Revoked得到拒绝证据。

**SL AssetRef与伴随记录。** 只在Applicable且完整记录可保真保存时，以上表三个SL字段构造原B/C `AssetRef(Id,Version,Sha256)`。根内本地伴随记录是原八输出槽内的宿主数据，不是新公共DTO/数据库：同一次保存SourceAsset（含任意源Revision）、完整SourceQualification/Expected/RequestedUse、QualificationSnapshotContent及规范bytes、原Qualified/Export、原Resolve/内部查询/直接复查request/execution/实际Owner对象/原Task关联、完整BindingResult和下游请求。少伴随或关联断裂时拒绝native/设备使用，或继续Joint专用完整绑定对象路径，不能只拿普通AssetRef向global/latest resolver补资格。下游模块独立验收仍由其原会话承担；本节Synthetic只验证值组装，不喂真实HALCON或设备。

**原两个无UI Host的新增子例。** 沿B.4.6.4的本地公开值/端口构造，不引用任一外模块测试工程/fixture私有builder，也不造第三Host。以下实际module链都使用原Store中Published的`syn-joint-asset/Revision("1")`和原fixture Qualification Owner；`syn-bind-asset`纯值向量不是Store资产，不能冒充Resolve成功。

| 原Host/新增子例 | 确定输入、关联及预期 |
|---|---|
| A发布后消费（插在原finally id5之前） | 原Solve1/Validate2/Publish3及必要Query4保持，PublishedUnqualified不Bind；由fixtureOwner显式令DecisionAvailable=true，再以**已于factory前注入**的观察器及同实际Owner Resolve id11，Use与B原runtimeVertical/Optics/Volume/CalibrationReplay及[t0,t0+4ms]精确同值。内部Read实际id11，捕获s1/Qualified/Export真归还；独立直接复查id12，Expected/Request逐表取原值，固定clock t0，s2=s1→Applicable。保存完整伴随后组装AssetRef(syn-joint-asset,"1.0.0",原candidate.digest)，源Revision/资格Revision仍"1"；原cleanup仍一次id5。此子例在原完整五包链后，不声称B.4.6.6新g1已完成五组重解 |
| B只读消费（插在原finally id8之前） | Factory/Observations=null、独立module/root/options/观察器，借原Store/Gate/Clock及同实际Owner；原Resolve6 DecisionAvailable=false仍Unknown，不Bind。DecisionAvailable=true后原Resolve7/内部Read7捕获完整原s1并核原Export，直接复查id10，固定clock t0，s2=s1→Applicable。同一表组装本Host自己的SL AssetRef/完整伴随，不共享A请求/Task/输出；原Purpose反例id9仍Unknown，cleanup仍一次id8。本模块B子例只验证SL消费，不依赖IM-032测试类或创建native file |
| A/B fresh纯值子例（不运行module/Store） | 复用上游§7.4.6B完整oracle：asset syn-bind-asset/source-A，scope optics/runtimeBoth/[t0−1day,t0+1day]/volume/CalibrationReplay；RequestedUse只曝光[t0,t0+1ms]，w1 Synthetic/epoch-1/wm-A/t0..t0+1day，s1 Qualified/syn-q/qual-A/C(binding-check)/C(runtime-HybridBoth)，qref1完整。A原期望/内部Query ID201、复查202，B301/302；其余字段精确同上游，IDs不进编码。两个Host各自根持纯值，前一case两根真释放且原费用实际归还后才启动，不超过总2根；确认全量移交仍Held时不能释放容量启动新根；无Store/file/native调用，无伪真实Owner关联证明 |

实际module正常子例必须分别观察内部查询恰一次、直接复查恰一次、所有原Task/完成路径及Export bytes归还；A关闭不能清B的Store/Gate/资格Owner。fresh纯值子例的R/M/T/Frame/Dev/C/D等值只按上游完整公开生成规则在各Host本地构造；不复制完整hex到本页、不重算旧Joint/Golden。上游主控独立字段重建已核正常/epoch各2904 bytes、撤回2902 bytes、换CheckEvidence2904 bytes及四hash；下表复用其oracle，不声称本轮重新复算或运行Bind。

| 两Host均执行的纯值变体（其它字段精确同原s1，Expected保持） | 预期及完整规范SHA-256 |
|---|---|
| 正常s2=s1 | Applicable；2904 bytes/hash `c28ce09df20e2237cbb31357bd70a2f20113841e64fdfe0a9e1fd3c72c982a17`；SL=(syn-bind-asset,"1.0.0",`a3b5783df1fcf87c3e9192b923ed9c9cba8e238f2ee0660784fc9f6b42b74c58`)，源source-A/qual-A完整伴随 |
| s2仅Epoch=epoch-2，其余水位不变 | Unknown/Projection=null；2904 bytes/hash `c0e16a99eb8dc57fdd7e512354ad4e9898a1d4e1465c820d2b33efed53e10d6e`；不能原地改Expected成epoch-2凑一致 |
| s2仅Status=Revoked，其余字段原值 | NotApplicable/RecheckedStatus/Projection=null；2902 bytes/hash `982a9327fbed9cd79e6933d5f4497190adfb377db6810fc1eb6cbe388d7bbf7a`；撤回优先于旧Qualified，不当Unknown掩盖撤回 |
| s2仅CheckEvidence=C(binding-check-2)，含水位其余不变 | Unknown/Projection=null；2904 bytes/hash `df73ce1b44edcd91090747f25c34f27167752d7a2fbf4211d07d9429ea77229a`；待绑定s1仅换该evidence而Expected仍原指纹也Unknown |

**有界根、费用和清理。** 沿原最多2根/每根64任务/8输出/4MiB、总根8MiB及provider/Store/workspace/gate各自原费用Owner，不增加并发。每根4MiB明确预留**其中1MiB**桥逻辑增量：原/待绑定/复查规范编码各≤64KiB合≤192KiB，其余≥832KiB覆盖有界深复制值、Expected/Request/helper输出和根记录；剩余3MiB承接原输出。Export.Bytes/Store读取/workspace/native仍按原报价单独占用，不藏进1MiB；checked总额须在根/父预算/gate实际剩余内，费用只能一个Owner，不漏Held也不双计借用的同记录。真实CLR峰值另验，不把逻辑1MiB当峰值承诺。不持gate预约跨重新Resolve再预约制造自锁；module IO按原gate流程，桥用独立根输出预约保管快照直到归还。

八输出槽固定为①Export及Bytes、②原snapshot/规范bytes、③ResolveReply、④Expected/RequestedUse、⑤复查snapshot/规范bytes、⑥待绑定snapshot/helper临时bytes、⑦BindingResult、⑧下游请求/完整伴随ref；其它已有输出在不再被任务借用且实际归还后于同锁结束其槽使用，不能暗加第九槽。后续消费前先按旧发布/候选/报告的在途依赖和原移交用途核剩余：原Outputs仍需保留时保留并拒绝容量不足的新消费；不得为跑成功子例删仍被引用的原结果。A若八槽不足则在前一case根/输出/费用真实归还后，用同一Host新预留只读实例/root执行公开完整预置Store链的后续case，重新注入观察器/实际Owner，A后续只读子例固定resolve13/recheck14/cleanup15；若B原根也无空槽，同法B后续只读子例固定resolve16/recheck17/cleanup18。只读实例Factory/Observations=null、Use仍原runtimeVertical/Optics/Volume/CalibrationReplay及[t0,t0+4ms]、DecisionAvailable=true，前一case公开Store完整闭包由fixtureOwner保留；内部Query沿各新resolve ID，正常s2=s1固定clock t0。不复用已Dispose的原module或超出2根。

Resolve原Task、内部Owner原Task、Host直接recheck原Task与所有完成路径都计64额度，调用前预留；ValueTask一次AsTask，不拿WaitAsync包装Task当原任务。caller取消/Timeout/late/编码或费用失败只有Unknown，不Bind、不组装、不触发native；晚到完整结果仍先入原根。cleanup先Closing，沿原独立有限token、一次Stop/Dispose和原ID查询，保业务首错/cleanup错误两轴。Core Stop只证其Own任务归还，**不能证Host直接recheck原Task退出**；module自己的任务/资源全部真归还后可实际Dispose，但根持直接查询/完成路径/全部输出/费用到它们真结束和输出归还，不能凭Dispose退根。provider/Store/Qualifications借用不Dispose。

未知时原一次全量offer必须含实际Owner对象/观察器、Query/execution/token/全部原Task及完成路径、原s1/s2/待绑定副本/规范bytes/Expected/Request/Reply/Export/BindingResult/伴随记录、业务和cleanup错误、根身份/费用预约；接收者先强持全量再于同锁确认原OfferId，才切Owner。拒绝、丢确认、异常、超时继续保原根；Transferred≠Released。正常退出必须所有任务真退出、输出实际归还、原Stop/Dispose确认及墓碑查询Owner存活，A/B共享fixture资源仅最后Own任务结束后由fixtureOwner归还。整个双Host case含清理10s、业务≤8s/两根cleanup各≤1s且取case剩余；suite120s/外层180s，不用Synthetic Advance代wall期限或无限延长复查。

| 新增断言 | 输入/确定预期（文档断言，尚未运行） |
|---|---|
| SL-QB01 | A11/12、B7/10（原输出仍占槽则A13/14、B16/17后续只读case）同次捕获/同Owner正常链与两个fresh纯值正常子例；Query/exec/Resolve关联及八槽伴随逐字段一致、原SourceRevision保真、caller改副本不影响源/封存；PublishedUnqualified/Resolve6/Purpose9不绑定，真实native/设备调用0 |
| SL-QB02 | 两Host源撤回/暂停/过期优先NotApplicable；同水位只换CheckEvidence或RuntimeValidationEvidence、任意Scope/资格Revision/有效期/待绑定副本变化而Expected保持→不Applicable；正常/epoch/撤回/CheckEvidence四hash复用上游，无Check/runtime/candidate摘要冒填 |
| SL-QB03 | Authority/Epoch/Revision/ObservedAtUtc/ValidUntilUtc任一变化/缺水位/过期/已知gap→Unknown；非时间用途/Optics/Pattern/Volume不符或曝光闭窗越界→NotApplicable，缺必需值Unknown；ValidTo=null保无上界，EvaluatedAt仍在有限水位闭窗，不能删时间字段接受 |
| SL-QB04 | 0/多次内部Read、query/exec/Resolve ID错、recheck ID重用、wrong Owner/其它asset撤回/原Qualified或Export断关联、伪Expected来源→Host Unknown且Bind/组装/native调用0；不得新查最近值修复，不从snapshot Authority选Owner |
| SL-QB05 | bridge版本非严格1.0.0、非法SL Id、未知enum/非有限值/非法UTF8/字符串256 bytes±1/编码65536±1、深复制/checked/根4MiB总8MiB/任务64/槽8±1及父剩余不足→复制或调用前有界拒绝，保原实际响应，Projection无部分成功；不替换源Revision或加未计槽 |
| SL-QB06 | Resolve/内部Owner/直接复查Task或完成路径取消/超时/迟到、factory/编码/Bind封存异常→Unknown、原Task/bytes/Owner保根，不交下游；Core Stop已Released而直接复查pending仍不退根；module Dispose不释放借用Owner，不把late值补回已失败绑定 |
| SL-QB07 | 原Stop/Dispose/全量offer逐点fault/WaitExpired/拒绝/丢确认→保首错和cleanup两轴/完整请求响应任务及预约；收悉全量才切Owner一次，Transferred不冒Released；A关闭B仍可读，两个根未真归还不得fresh第三根，确认全量移交但仍Held也不释放容量；10/120/180s为有限观察验收，不声称native/设备释放 |

本增量两轮有界自审：第一轮核源0.3.2-prep公开字段/版本域/完整Scope与evidence/规范ContentRef及信任来源，区分桥包SemVer、技术指纹和资格原件；第二轮走两个原Host正常、撤回优先、epoch/evidence变化、错Owner/断关联、迟到/预算/直接查询未决和确认全量移交。仅文档核对，不新研究、不复算旧Golden、不创建/编译/运行产品或Host；资格绑定消费增量已获主控限定内容接收（2026-10-11），原Core/首次producer/成功诊断及未执行资格保持。

#### B.4.7 IM-032 0.2.5 完整角色与成功重建诊断消费（主控限定内容接收，2026-10-11）

源§4.2.2/§4.4.1/§13.6.1已由主控接收，八份规范编码长度/hash已由主控独立字段重建一致；0.2.5起草期的旧待接收文字不覆盖该明确指令。B.4记录的源SHA256锁定本轮已完整读取的0.2.5快照；该历史快照之后的IM-032 0.2.6 §7.6无setup decode-only规格现已由主控接收，其首次观测消费只见B.4.6.6新增指导；本节保持原0.2.5成功重建诊断范围，不能把新decode-only等同于HybridBoth+Diagnostics支持。本模块按以下接线，不扩大原B API或改IM-032契约。真实完整manifest/原帧/已适用共同setup及IM-032正式Qualification引用映射仍是实际输入前提；此处两个Synthetic Host只核消费协议。

**完整Sequence逐字段**：PatternSpec.Sequence=`StructuredLightSequenceSpec("r3d-sl-sequence-v1",RevisionRef(原manifest身份,原ManifestHash),Patterns)`，id须能保真满足对方字段域，否则拒绝，不能把GeneratedPatternSha256换成相机载荷hash。每StructuredLightPatternBinding为原PatternId、SourceIndex−1、Kind、Axis、RoleOrdinal、PhaseStepIndex、GeneratedPatternSha256。原PatternRole逐项映射为NormalizationBlack→SampleKind.NormalizationBlack、NormalizationWhite→SampleKind.NormalizationWhite、Gray→GrayCode、GrayInverted→GrayCodeInverted、Phase→PhaseShift、SingleStripe→SingleStripe；同样Kind用于FrameRef。Black/White为Axis.None/ordinal0/phase null，Gray/反图同axis同role ordinal且紧随成对；其余axis来自原PatternDirection，role ordinal为同axis同角色的原连续顺序，四步phase的PhaseStepIndex/RoleOrdinal0..3且相等，PhaseRadians仍留原manifest而不猜index0=0rad。global恰一Black/White且无反图；inverted_pattern无全局黑白且每Gray必有反图，所有原帧均保留。V/H不是两个DirectionCapture，HybridBoth完整重建可支持但Diagnostics必须null。真实Adapter按同参数gen逐对象/hash核布局，旧六帧fixture不代其布局证据。

本模块LayerKind与对方StructuredLightDiagnosticKind逐名称映射，**数值不可强转**（B从1起，对方从0起）。RequestedLayers非空时先去核合法无重复/实际支持及本方limits；按对方enum递增冻结 `StructuredLightDiagnosticRequest("r3d-sl-diagnostics-v1",Layers,ByteCount(MaxOutputBytes),MaxLayers,RuntimeRevision)`。RuntimeRevision来自原RuntimeRef展开的实际部署包，不能只用HALCON版本；Simulator用script.SyntheticRevision。MaxLayers对整个operation1..1024且≥实际层数，GrayBinary按原Gray数增加层，不按RequestedLayers.Count估输出数；本方VisionLimits.MaxLayers仍独立限制。MaxOutputBytes1..8GiB且≤父余额/下游Managed/Result，本桥先报价全部层和本方copy/编码/domain引用。CapturePhaseDiagnostics=PersistenceRequested；四持久化kind要求true，Correspondence/PatternRegion可false，不在decode后改开关。

| LayerKind | 首版支持/数量 | B.LayerRef与实际值单位 |
|---|---|---|
| Correspondence | HybridVertical/GrayVertical/SingleStripeVertical，每物理方向1 | Float64/ProjectorPixel，Axis.Vertical，原projector column；0合法 |
| PatternRegion | 上述三路线，每方向1 | BinaryMask/Membership，Axis.None；原冻结ROI内0/1，ROI外null，不当Surface.ValidMask |
| Phase | HybridVertical/SingleStripeVertical，每方向1且persistence | Float64/HalconPhaseValue；保原phase，不改rad/mm、不unwrap |
| GrayBinary | 三vertical路线，原Gray数量且persistence，不含反图 | Byte/BinaryClass，0/1，ObjectOrdinal=GrayRoleOrdinal+1，保对应Gray及完整normalization来源 |
| GrayCorrespondence | 三vertical路线，每方向1且persistence | Float64/HalconGrayCorrespondenceValue；不冒stripe编号/混合correspondence/mm |
| SingleStripe | 仅SingleStripeVertical，每方向1且persistence | Float64/HalconSingleStripeValue；不冒中心pixel/高度 |
| Defect/HybridBoth+Diagnostics/GrayVertical+Phase/非SingleStripe+SingleStripe | 副作用前明确NotSupported/SL-VIS-003并保R3D-007原因 | 不取私模型/重复算子、不省层或运行时换路线 |

**完整出参核验/本地引用**：只在原重建成功且实际资源归还后，从公开ReconstructionReply.Result（ReconstructionResult）的DiagnosticLayers取得原不可变值，保持物理Directions原序→Kind→ObjectOrdinal；每层Version/LayerId/DirectionId/Kind/Axis/ObjectOrdinal/GrayRoleOrdinal/W/H/Unit/Observation/Origin、Input/Manifest/Pattern/Algorithm/Runtime五revision、完整SourceFrames（含实际frame revision/ordinal及黑白或反图）、Domain/Values/ContentSha256逐字段校验。W/H为原相机、Domain/Values恰N，域外null、域内有限，Membership/Binary仅0/1；非PatternRegion空domain为NotObservable，不能填0。PatternRegion的ROI域/原region与Correspondence域一致性按源契约核；不同其它层domain允许不同，不套Surface.mask，不crop/降采样/世界变换。ApplyPublished只改Surface，诊断原hash/坐标不变、不参与融合。

本桥按源§4.4.1唯一R3DL编码从全部原字段重算**实际规范bytes**与ContentSha256，不发明另一层codec：ASCII R3DL/U16LE1、严格UTF8长度、enum U8、ordinal/尺寸I32LE、可空标志、五revision、完整SourceFrames、Domain0/1及Nullable Float64LE的顺序/−0归一/EOF均沿源。本地受限copy目录只保(original immutable DTO,规范bytes,domain bytes,原binding关联)，不新增公共存储API。AssetRef.Id使用预留安全ASCII本地id（如dg-D01-0-1），不直接用含“/”的LayerId；Version为实际消费包合法SemVer，原LayerId/所有源revision在DTO内保真，Asset.Sha256=R3DL实际bytes hash。ValidDomainRef是同尺寸N个0/1原domain实际bytes摘要/安全本地id，Kind、W/H、PixelType按表、CoordinateFrameId=原binding的相机pixel frame、Unit精确枚举名，SourceBindingRefs为原SourceFrames逐项匹配的完整B bindings。LayerRef只索引本地已封存DTO/bytes，PixelType描述Values类型而不是R3DL容器布局；null以Domain/Values保留，Byte/BinaryMask不能把域外null写成有效0。

原B DTO没有Axis/ObjectOrdinal/GrayRoleOrdinal等字段，故LayerRefs不得脱离同时保存的完整原DTO/目录解释；不丢源字段后把引用伪称完整外部证据。两个本地Host可直接按其Owner清单读已登记不可变copy；跨进程发布/外部显示/持久化仅在宿主正式来源/读取合同获接收后使用，不凭ref宣称已经保存。不支持保真读取的宿主拒绝相应层交付，不能造blob-store API。先在本地根暂存并核齐全部请求层/bytes/域，全部通过后一次采用LayerRefs；编码/预算/取消/保存失败不交部分成功组，不把先交phase当操作成功。DrainUnknown时Result=null/LayerRefs.Empty；迟到结果归原根，原Task/lease退出后才可退槽，copy完成不等于native释放。

计费沿源每层 `512+32*N+Σ(max(2*string.Length,StrictUtf8ByteCount)+32)+512*SourceFrames.Length`，含64字符hash、全部重复出现revision/source字符串；typed/Domain/Values/编码保守单份费用总≤MaxOutputBytes，下游adapter+Core至少两份、真实run scratch `32*N+65536`及native persistence实测envelope另计。本方目录DTO/规范byte/domain和返回引用追加自己的费用，不挪用下游Result；保守每层预留上式两份+N（copy/编码+domain）及B refs/本方已有metadata报价，所有副本在最早父期限内复制，预算不够源/factory前拒绝。无法核当前runtime/源/完整层组/真实native envelope时拒绝，不以Synthetic费用证明native峰值。

**两个现无UI Host的后续case**：精确继承IM-032§13.6.1 D01/D02全字段payload/八层oracle及§13.6双根/五原Task调用，不引用Core.Tests或便捷Build类；按公开DTO/BCL/发布SimulationFactory本地构造，所有未变字段只从该唯一卡取值。D01为HybridVertical/global/black-white-g0-g1-p0..3八帧，6层；D02为GrayVertical/global/四帧、ROI column1，2层。各自独立clock/gates/script/sim/engine/root，先Reserve再Create(sim)→Attach→Create(engine)→Validate→原ReconstructAsync；旧F0/F0-S/ST0及B.4.5原Diagnostics=null Host保持不变。这是原两个Host fresh后续case，不增加第三Host/工程/decoder。

消费核D01每层7914/总47484bytes，D02每层4938/总9876bytes（下游报价），八份R3DL编码长度依源表1185/1185/1185/1189/1181/1185/841/841及对应hash；本方另预留上式两份+N每层（D01总94980、D02总19756bytes）及refs/metadata，不混成下游单份输出预算65536。D01灰二层Domain=[true,false]/Values=[1,null]、Phase=[0,1.25]的HalconPhaseValue，D02Domain=[false,true]/Values=[null,4.25]及PatternRegion[null,1]必须保原pixel位置；source8/4帧且9/5lease各取得/归还一次。为本地LayerRef明确绑定SourceBindingRefs `dg-binding-D01-i`/`dg-binding-D02-i`、Version=0.2.5-prep、实际两byte载荷hash，原pixel frame由各Host清单固定 `dg-pixel-D01`/`dg-pixel-D02`；domain id为`dg-domain-H-kind-object`/同version/实际0-1 bytes hash，layer id同规则`dg-H-kind-object`（H=D01/D02、kind为对方数值、object原ordinal）。这些是Synthetic本地来源别名，目录同时持有完整原SourceFrames/DTO关联，不将它们发布成采集Owner真实binding。

| 断言 | 输入/预期 |
|---|---|
| SL-DG01 | 两完整D01/D02消费，核八层全部字段/来源/域/单位/实际规范length/hash/LayerRefs目录映射，Z0和对应0合法；所有原Task与9/5lease和本地copy归还才exit0，不授Qualified/rad/真实布局 |
| SL-DG02 | 缺/重复/错角色/互补/phase/生成图hash、Sequence未opt-in/部署无能力、enum数值误强转→源前拒绝；完整Black/White/GrayInverted不冒Gray。Both无Diagnostics可保原重建，Both+Diagnostics/Defect等明确不支持 |
| SL-DG03 | 少层/多层/错shape/错来源顺序/值与domain冲突/hash改/错误单位、R3DL截断/尾字节→整组拒绝，不交部分LayerRefs；未给rad尺度/参考/共同域→CircularPhase各NotEvaluated，不输出0误差/Rank/Advice |
| SL-DG04 | 复制/编码/回执消费异常与取消/Stop/Dispose/CallbackExit/Release迟到→原run/core-stop/core-dispose/sim-stop/sim-dispose五Task和sourcelease/root持续强持，收尾首错两轴/全量接收同B.4.4；未排空LayerRefs.Empty，复制完成不退native槽 |
| SL-DG05 | 实际Gray层数/MaxLayers/MaxOutputBytes/本方copies/codec峰值/父期限上界±1、persistence false索phase→分配前拒绝，不截层/延长deadline；真实DiagnosticLayers不作为首次CAL-JC无setup来源 |

两个case沿10s/suite120s/外层180s wall验收与原有限收尾；不扩大矩阵或重新跑无关检查。B.4.6–7第一轮按公开字段/版本域/typed/raw实际bytes/支持域/单位和消费Owner核对；第二轮走A/B与D01/D02正常→取消/迟到/异常→Stop/Dispose→全量offer及父余额路径，当时未把待接收decode-only或资格digest映射补成事实；现首次无setup已接收源规格的消费增量只见B.4.6.6；CAL 0.3.2-prep资格绑定源桥已限定接收，本地消费见B.4.6.7（资格绑定消费增量已获主控限定内容接收，2026-10-11），不扩大本成功重建诊断的支持域。本轮仅新增指导并定向自审，产品代码、C#构建/Host、HALCON、性能、物理/现场资格均未执行。


## 附录 C：Slice-1 Projection 完整托管声明 v0.2

以下是唯一拟实现公开类型/签名；§3字段表解释这些声明，不再提供另一套候选类型。未编译、未运行，不声明厂商SDK现有方法。nullable只允许声明位置；集合一律非default ImmutableArray，结果错误用ModuleIssue而不把设备错误塞入Core.Issue。string ID/hash规则沿§3.1；所有hash输出小写。投影与Vision共用的AssetRef、ModuleIssue、ClockStamp、资源状态等在此纯托管namespace定义；Vision只引用这些值/查询端口，不创建ProjectionSession。

### C.1 值、枚举和结果

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.StructuredLight;

namespace Asun.Modules.StructuredLight.Projection;

public sealed record AssetRef(string Id, string Version, string Sha256);
public sealed record ModuleIssue(
    string Code, string Path, string DetailKey, string? NativeCode);
public sealed record ClockStamp(
    Guid BootId, string ClockDomainId, long Ticks, long FrequencyHz);
public sealed record NumericRange(double Minimum, double Maximum);
public enum ProjectionMode { SoftwareStep = 1, HardwareSequence = 2 }
public enum ReadbackLevel { None = 0, CommandAck = 1, PatternId = 2, OpticalSensor = 3 }
public enum ActualTrust { None = 0, CommandAccepted = 1, DeviceReported = 2, SensorConfirmed = 3 }
public enum DeviceInvocation { KnownNotInvoked = 1, Invoked = 2, Unknown = 3 }
public enum StopStatus { NotRequested = 1, Requested = 2, Confirmed = 3, Unknown = 4 }
public enum BlackoutStatus
{
    NotRequested = 1, Requested = 2, AckOnly = 3, Confirmed = 4, Unconfirmed = 5
}
public enum DrainStatus { Pending = 1, Confirmed = 2, Unknown = 3 }
public enum ResourceStatus { Held = 1, Released = 2 }
public enum OperationOutcome { Completed = 1, Failed = 2, Cancelled = 3, TimedOut = 4, Unknown = 5 }
public enum OperationPhase
{
    Accepted = 1, Invoking = 2, Executing = 3, LogicalEnded = 4,
    Draining = 5, DrainUnknown = 6, Terminal = 7
}
public enum ProjectorState
{
    Closed = 1, Opening = 2, Ready = 3, Uploading = 4, Prepared = 5,
    Armed = 6, Displaying = 7, Cooling = 8, Draining = 9,
    Faulted = 10, Unknown = 11, Disposed = 12
}
public enum CommandKind
{
    Open = 1, Upload = 2, RenewLease = 3, ReleaseLease = 4,
    Prepare = 5, Arm = 6, DisplayStep = 7, ExecuteHardwareSequence = 8,
    StopAndDrain = 9, Blackout = 10, Recover = 11,
    RunDiagnostic = 12, Shutdown = 13
}
public enum CommandDisposition { Accepted = 1, Rejected = 2, Replay = 3, Conflict = 4, Released = 5 }
public enum LeaseDisposition { Renewed = 1, Released = 2, AlreadyReleased = 3 }
public enum DiagnosticKind { Health = 1, SelfTest = 2, Timing = 3 }
public enum ObservationStatus { Observed = 1, NotObserved = 2, Failed = 3 }
public enum EvidenceMode { Physical = 1, Simulation = 2 }
public sealed record Capability(
    string ProjectorId, string FirmwareVersion, string Fingerprint,
    ulong Generation, Guid BootId, int Width, int Height,
    ImmutableArray<PixelFormat> Formats, int MaxSlots, long MaxBytes,
    ImmutableArray<ProjectionMode> Modes,
    ImmutableArray<ReadbackLevel> ReadbackLevels,
    long SwitchSettleNs, long MinimumHoldNs, bool CanPreempt,
    long? StopBoundNs, NumericRange? TemperatureRangeC,
    NumericRange? PowerRangeW, NumericRange? DutyRange,
    string PhysicalMappingHash, ClockStamp ObservedAt, EvidenceMode EvidenceMode);
public sealed record TimingStep(
    int Ordinal, string PatternHash, string ExposureRole,
    long HoldNs, long SettleNs, long ExposureStartOffsetNs,
    long ExposureDurationNs, long GuardBeforeNs, long GuardAfterNs, string TriggerRole);
public sealed record ProjectionSequence(
    ProjectionPlan Plan, ProjectionMode Mode,
    ImmutableArray<TimingStep> TimingSteps,
    AssetRef ProfileRef, AssetRef RuntimeRef, AssetRef? CalibrationRef,
    string CapabilityFingerprint, string PhysicalMappingHash,
    ReadbackLevel RequiredReadback, long TotalBudgetNs, long StopBudgetNs);
public sealed record PatternLease(
    Guid LeaseId, Guid SessionId, string ProjectorId, string PatternHash, int Slot,
    ulong Generation, string CapabilityFingerprint, Guid BootId,
    ClockStamp ExpiresAt, long LeaseVersion);
public sealed record LeaseRef(Guid LeaseId, long LeaseVersion);
public sealed record CommandMeta(
    Guid OperationId, string IdempotencyKey, string RequestSha256,
    Guid SessionId, ulong ExpectedGeneration, long ExpectedStateVersion,
    ClockStamp Deadline, string AuthorityScope);
public sealed record PreparedReceipt(
    Guid OperationId, string SequenceHash, Guid SessionId,
    ulong Generation, long StateVersion, string LeaseSnapshotHash,
    ImmutableArray<LeaseRef> ExactLeases);
public sealed record ArmedReceipt(
    Guid OperationId, Guid PreparedOperationId, Guid ExecutionOperationId,
    string SequenceHash, Guid SessionId, ulong Generation, long StateVersion,
    ProjectionMode Mode, string TriggerId, string LeaseSnapshotHash,
    ImmutableArray<PatternLease> FrozenLeases);
public sealed record ProjectionActual(
    Guid ActualId, Guid CommandOperationId, Guid ExecutionOperationId,
    Guid SessionId, ulong Generation, long StateVersion, string SequenceHash,
    int Ordinal, string PatternHash, Guid LeaseId, long LeaseVersion,
    string LeaseSnapshotHash, string TriggerId, ClockStamp RequestedAt,
    ClockStamp? ActualAt, ReadbackLevel ReadbackLevel, ActualTrust Trust,
    double? TemperatureC, double? PowerW, AssetRef ProfileRef,
    AssetRef RuntimeRef, AssetRef? CalibrationRef, EvidenceMode EvidenceMode);
public sealed record OperationSnapshot(
    Guid OperationId, string RequestSha256, OperationPhase Phase,
    OperationOutcome? LogicalOutcome, OperationOutcome? TerminalOutcome,
    int? LastActualOrdinal, StopStatus StopStatus, BlackoutStatus BlackoutStatus,
    DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    DeviceInvocation DeviceInvocation, ImmutableArray<ModuleIssue> Issues,
    ulong Generation, long StateVersion, ClockStamp ObservedAt);
public sealed record SessionSnapshot(
    Guid SessionId, string ProjectorId, ProjectorState State,
    ulong Generation, long StateVersion, Guid BootId, string CapabilityFingerprint,
    Guid? ActiveExecutionId, StopStatus StopStatus, BlackoutStatus BlackoutStatus,
    DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    ClockStamp ObservedAt, bool Stale, ImmutableArray<ModuleIssue> Issues);
public sealed record DrainReceipt(
    Guid OperationId, DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    BlackoutStatus BlackoutStatus, OperationOutcome? LogicalOutcome,
    OperationOutcome? TerminalOutcome, ClockStamp ObservedAt,
    ImmutableArray<ModuleIssue> Issues);
public sealed record ProjectionLimits(
    int MaxSlots, int MaxCommands, int MaxCallbackItems, int MaxEventsPerOperation,
    long MaxPatternBytes, long MaxInFlightBytes, long MaxLedgerBytes,
    long MaxRetainedOperations, long MaxDiagnosticBytes,
    long CommandBudgetNs, long CleanupBudgetNs, RetentionPolicy Retention);
public sealed record CommandReply<T>(
    CommandDisposition Disposition, Guid OperationId, T? Value,
    ImmutableArray<ModuleIssue> Issues, OperationSnapshot? Snapshot,
    OperationTombstone? Tombstone) where T : class;
public sealed record LeaseMutationReceipt(
    LeaseDisposition Disposition, PatternLease? Lease, long StateVersion);
public sealed record BlackoutReceipt(
    Guid OperationId, BlackoutStatus Confirmation, ClockStamp ObservedAt,
    long StateVersion, ImmutableArray<ModuleIssue> Issues);
public sealed record DiagnosticObservation(
    string Name, double? Value, string Unit, string Source,
    ClockStamp ObservedAt, ObservationStatus Status);
public sealed record DiagnosticReceipt(
    Guid OperationId, ImmutableArray<DiagnosticObservation> Observations,
    ObservationStatus Status, ImmutableArray<ModuleIssue> Issues);
public enum QueryStatus { Found = 1, NotFound = 2, Unavailable = 3, Released = 4 }
public sealed record OperationQuery(
    QueryStatus Status, OperationSnapshot? Snapshot, long LedgerRevision,
    ClockStamp ObservedAt, ImmutableArray<ModuleIssue> Issues,
    OperationTombstone? Tombstone, ResultRetentionState RetentionState);
public enum ProjectionEventKind
{
    OperationAccepted = 1, CapabilityVerified = 2, LeaseAcquired = 3,
    Prepared = 4, Armed = 5, StepRequested = 6, StepActual = 7,
    LogicalCompleted = 8, LogicalFailed = 9, LogicalCancelled = 10,
    LogicalTimedOut = 11, LogicalUnknown = 12, StopRequested = 13,
    StopConfirmed = 14, StopUnknown = 15, BlackoutRequested = 16,
    BlackoutConfirmed = 17, BlackoutUnconfirmed = 18, DrainPending = 19,
    DrainUnknown = 20, Drained = 21, ResourcesReleased = 22,
    Completed = 23, Failed = 24, Cancelled = 25, TimedOut = 26, Unknown = 27
}
public sealed record ProjectionEvent(
    Guid OperationId, long EventOrdinal, ProjectionEventKind Kind,
    ClockStamp ClockStamp, ulong Generation, long StateVersion,
    string? SequenceHash, ProjectionActual? Actual, ModuleIssue? Issue);
public enum ExecutionItemKind { StepActual = 1, LogicalEnd = 2, Released = 3 }
public sealed record ProjectionExecutionItem(
    ExecutionItemKind Kind, Guid ExecutionOperationId,
    ProjectionActual? Actual, OperationOutcome? LogicalOutcome,
    ImmutableArray<ModuleIssue> Issues, OperationTombstone? Tombstone);
public sealed record EventQuery(
    Guid OperationId, long AfterOrdinal, int MaxItems, ClockStamp Deadline);
public sealed record EventPage(
    QueryStatus Status, ImmutableArray<ProjectionEvent> Events,
    long NextAfterOrdinal, bool HasMore, OperationSnapshot? Snapshot,
    ImmutableArray<ModuleIssue> Issues, OperationTombstone? Tombstone);
```

NumericRange的两端finite且Minimum<=Maximum，温度单位°C可负，功率W下界>=0，Duty无量纲0..1。Capability集合非空、无重复、未知enum拒绝；MaxSlots/Bytes正值，SwitchSettleNs>=0、MinimumHoldNs>0、StopBoundNs若有则>0。None读回不是能力证明。Simulation明确出现在Capability/Actual，不能由UI推断或在发布时移除。ModuleIssue.Code限定§5的稳定SL码加SL-CANCEL-002（接纳前取消）/SL-QRY-001（查询不可用）/SL-DISPOSE-001（排空前Dispose）/SL-RET-001（结果已释放）/SL-RET-002（结果仍被使用）；DetailKey资源键，NativeCode仅诊断可null，Path不能为空。跨切片校验不得返回未定义“异常文本”作唯一错误。

值类型补充：ClockStamp.BootId是该clock域的启动身份；Capability/PatternLease.BootId是设备启动身份，不能要求设备boot等于宿主clock.boot。Lease.ExpiresAt/所有命令deadline取注入clock同域。刚Create的Closed快照尚未读取设备时Generation/StateVersion=0、BootId=Guid.Empty、CapabilityFingerprint为空；首次Open的Accepted/Invoking OperationSnapshot及对应event在CapabilityVerified之前也允许Generation=0，StateVersion按session已线性化转换递增，绝不能把0写成已观察设备代。Ready后均须实值；Open失败保留未观察字段和Issues，不猜固件/boot。GetCapability在未Open时抛InvalidOperationException且无设备调用，不假造Capability。ModuleIssue.Path<=1024、DetailKey<=128、NativeCode<=256，长原始诊断只通过宿主证据引用，不能无界塞进队列；MaxDiagnosticBytes是DiagnosticReceipt全量编码字节上限，超限ObservationStatus.NotObserved+SL-RES-001，不静默截成健康。

设备SequenceHash与Core.PlanSha256不同：固定NUL结尾域ASUN-SL-SEQ-2，依ProjectionSequence声明次序写PlanSha256的32bytes、Mode、TimingSteps及完整资产/capability/physical mapping/readback/budgets；TimingStep.PatternHash也写32bytes。LeaseSnapshotHash域ASUN-SL-LEASES-2+按LeaseId网络字节序排序的FrozenLeases完整字段（包括版本/到期/slot/boot），两者用SHA256、小写输出；准备/武装/Actual全部沿用相同冻结结果。同Core计划但曝光/预算/资产变化必须新SequenceHash，不能用Core.PlanSha256代替。Command hash三个域ASUN-SL-CMD-2/REPLY-2与Vision/Manifest域均在末尾写单NUL，字段按声明顺序；Capability集合规范排序enum数值，资产声明顺序Id/Version/Sha，sha都32bytes。

Projection当前支持域补齐：所有artifact Width/Height等于Capability，整个序列同一个PixelFormat且在Formats中；混合格式切换没有声明时序/设备语义，返回UnsupportedPlanShape，不影响Core离线允许的metadata集合。同hash的多PatternId在相同尺寸/格式下复用一个slot/lease（方向/Role仍由step/manifest保留）；Upload命中已有有效lease只回该lease，不续租/改版本，期限不足应显式Renew后重新Prepare。ExactLeases是去重集合且须覆盖所需唯一内容hash，无闲置项，FrozenLeases每hash恰一个，因此Host.Single无歧义。Prepared后禁止改变lease集；Release/Drain仅归还执行引用，Shutdown最终释放全部slot。设备FirmwareVersion是原始非空文本<=128，不强制SemVer；模块/资产版本仍沿各自SemVer规则。

### C.2 请求和session

```csharp
public sealed record OpenRequest(CommandMeta Meta, string ExpectedProjectorId);
public sealed record UploadRequest(
    CommandMeta Meta, PatternArtifact Artifact, long RequestedLeaseNs);
public sealed record RenewRequest(
    CommandMeta Meta, Guid LeaseId, long ExpectedLeaseVersion, long RequestedLeaseNs);
public sealed record ReleaseRequest(CommandMeta Meta, Guid LeaseId, long ExpectedLeaseVersion);
public sealed record PrepareRequest(
    CommandMeta Meta, ProjectionSequence Sequence, ImmutableArray<LeaseRef> ExactLeases);
public sealed record ArmRequest(
    CommandMeta Meta, Guid PreparedOperationId, string TriggerId,
    ProjectionMode Mode, string LeaseSnapshotHash);
public sealed record DisplayStepRequest(
    CommandMeta Meta, Guid ArmedOperationId, int Ordinal,
    string PatternHash, Guid LeaseId, long LeaseVersion);
public sealed record HardwareSequenceRequest(
    CommandMeta Meta, Guid ArmedOperationId, string LeaseSnapshotHash);
public sealed record StopRequest(
    CommandMeta Meta, Guid ExecutionOperationId, string ReasonKey, long CleanupBudgetNs);
public sealed record BlackoutRequest(
    CommandMeta Meta, Guid? ExecutionOperationId, string ReasonKey);
public sealed record RecoverRequest(
    CommandMeta Meta, Guid AbortOperationId, Guid ExpectedBootId, string ExpectedFingerprint);
public sealed record DiagnosticRequest(
    CommandMeta Meta, DiagnosticKind Kind, AssetRef ProfileRef, long BudgetNs);
public sealed record ShutdownRequest(CommandMeta Meta, long CleanupBudgetNs, string ReasonKey);
public sealed record OperationQueryRequest(Guid OperationId, ClockStamp Deadline);
public interface IProjectionSession : IAsyncDisposable
{
    Guid SessionId { get; }
    ValueTask<CommandReply<SessionSnapshot>> OpenAsync(OpenRequest request, CancellationToken ct);
    ValueTask<Capability> GetCapabilityAsync(CancellationToken ct);
    ValueTask<SessionSnapshot> GetSnapshotAsync(CancellationToken ct);
    ValidationReport Validate(
        ProjectionSequence sequence, Capability capability, ProjectionLimits limits, CancellationToken ct);
    ValueTask<CommandReply<PatternLease>> UploadAsync(UploadRequest request, CancellationToken ct);
    ValueTask<CommandReply<LeaseMutationReceipt>> RenewLeaseAsync(RenewRequest request, CancellationToken ct);
    ValueTask<CommandReply<LeaseMutationReceipt>> ReleaseLeaseAsync(ReleaseRequest request, CancellationToken ct);
    ValueTask<CommandReply<PreparedReceipt>> PrepareAsync(PrepareRequest request, CancellationToken ct);
    ValueTask<CommandReply<ArmedReceipt>> ArmAsync(ArmRequest request, CancellationToken ct);
    ValueTask<CommandReply<ProjectionActual>> DisplayStepAsync(DisplayStepRequest request, CancellationToken ct);
    IAsyncEnumerable<ProjectionExecutionItem> ExecuteHardwareSequenceAsync(
        HardwareSequenceRequest request, CancellationToken ct);
    ValueTask<CommandReply<DrainReceipt>> StopAndDrainAsync(StopRequest request, CancellationToken ct);
    ValueTask<CommandReply<BlackoutReceipt>> BlackoutAsync(BlackoutRequest request, CancellationToken ct);
    ValueTask<OperationQuery> QueryOperationAsync(OperationQueryRequest request, CancellationToken ct);
    ValueTask<EventPage> GetEventsAsync(EventQuery request, CancellationToken ct);
    ValueTask<RetentionReleaseReply> ReleaseOperationAsync(
        RetentionReleaseRequest request, CancellationToken ct);
    ValueTask<RetentionUsage> GetRetentionUsageAsync(CancellationToken ct);
    ValueTask<CommandReply<SessionSnapshot>> RecoverAsync(RecoverRequest request, CancellationToken ct);
    ValueTask<CommandReply<DiagnosticReceipt>> RunDiagnosticAsync(DiagnosticRequest request, CancellationToken ct);
    ValueTask<CommandReply<DrainReceipt>> ShutdownAsync(ShutdownRequest request, CancellationToken ct);
}
```

唯一factory签名：`ProjectionSession.Create(string projectorId, IProjectorAdapter adapter, IProjectionClock clock, IOperationLedger ledger, IProjectionAuthority authority, ProjectionLimits limits)`→`IProjectionSession`。另提供无副作用签名构造器 `ProjectionRequests.Sign<T>(T request)`→同类型T（支持且仅支持C.2的命令request），它按§3.3重算Meta.RequestSha256，不能查询权限/设备；不把泛型T序列化为任意object/JSON。Create分配非空SessionId、Closed，clock.Now用于首次expected0的deadline。

查询不需写权限、不发设备输出；OperationQueryRequest/EventQuery有显式deadline；GetCapability/GetSnapshot只是读取本地最后快照，以limits.CommandBudgetNs限制锁等待。Query取消允许OperationCanceledException，因为无副作用；调用方不能因此认定资源Released。OperationQuery.Status=Found才Snapshot非null且LedgerRevision>0，NotFound/Unavailable为null并保留查询时间/原因；Released时Snapshot=null、墓碑非null，不能误判NotFound。EventQuery.AfterOrdinal=-1表示首项，MaxItems在1..MaxEventsPerOperation；非阻塞读取现有页，页满用HasMore/NextAfterOrdinal续查，空页不会等待新事件。ledger断档返回Unavailable+SL-QRY-001，不越过缺项。终态可重复查询，订阅/分页结束不代表执行结束。

执行stream在接纳前拒绝时只产一个LogicalEnd(原请求OperationId,Failed/Cancelled,issues)，未接纳必须没有Armed execution副作用、无Actual；ledger记录KnownNotInvoked或拒绝回执可查。已接纳后step和LogicalEnd必须完整，ct取消触发原cleanup；enumerator DisposeAsync不能用取消token中止cleanupOwner。ExecutionItem.Kind=StepActual时Actual必填、LogicalOutcome=null；LogicalEnd时Actual=null、LogicalOutcome必填。ExecutionOperationId首次Arm采用Arm.Meta.OperationId，不新增隐藏随机ID，所有后续命令关联它。

### C.3 Adapter、ledger、authority与读回的精确端口

```csharp
public interface IProjectionClock { ClockStamp Now { get; } }
public sealed record AdapterContext(
    Guid OperationId, Guid SessionId, ulong Generation,
    ClockStamp Deadline, string CleanupScope);
public enum AdapterStatus { Succeeded = 1, Rejected = 2, Failed = 3, Unknown = 4 }
public enum AdapterConfirmation { None = 0, CommandAck = 1, DeviceReadback = 2, SensorReadback = 3 }
public sealed record AdapterReply<T>(
    AdapterStatus Status, T? Value, DeviceInvocation Invocation,
    string? NativeCode, ClockStamp ObservedAt,
    AdapterConfirmation Confirmation, ImmutableArray<ModuleIssue> Issues) where T : class;
public sealed record AdapterOpen(string ProjectorId);
public sealed record AdapterUpload(PatternArtifact Artifact);
public sealed record AdapterPrepare(ProjectionSequence Sequence, ImmutableArray<SlotRef> Slots);
public sealed record SlotRef(int Ordinal, int Slot, string PatternHash);
public sealed record AdapterArm(
    Guid ExecutionOperationId, ProjectionMode Mode, string TriggerId, string SequenceHash);
public sealed record AdapterDisplay(
    Guid ExecutionOperationId, int Ordinal, int Slot, string PatternHash);
public sealed record AdapterExecute(Guid ExecutionOperationId, string SequenceHash);
public sealed record AdapterReadback(Guid? ExecutionOperationId);
public sealed record AdapterStop(Guid? ExecutionOperationId);
public sealed record AdapterBlackout(Guid? ExecutionOperationId);
public sealed record AdapterDrain(Guid? ExecutionOperationId);
public sealed record AdapterRelease(int Slot, string PatternHash);
public sealed record AdapterClose(string ProjectorId);
public sealed record AdapterOpenValue(Capability Capability);
public sealed record AdapterUploadValue(int Slot, string PatternHash, long Bytes);
public sealed record AdapterPreparedValue(string SequenceHash);
public sealed record AdapterArmedValue(Guid ExecutionOperationId, string TriggerId);
public sealed record AdapterReadbackValue(
    string? PatternHash, int? Slot, int? Ordinal,
    ClockStamp? ActualAt, ReadbackLevel Level,
    double? TemperatureC, double? PowerW, bool? OpticalBlackout);
public sealed record AdapterStopValue(StopStatus Status);
public sealed record AdapterBlackoutValue(BlackoutStatus Status);
public sealed record AdapterDrainValue(
    DrainStatus Status, long PendingCommands, long PendingCallbacks, long PendingSlotReferences);
public sealed record AdapterReleaseValue(int Slot, bool Released);
public sealed record AdapterCloseValue(bool ConnectionReleased, bool CallbacksReleased);
public enum AdapterStreamKind { StepReadback = 1, LogicalEnd = 2 }
public sealed record AdapterStreamItem(
    AdapterStreamKind Kind, Guid ExecutionOperationId,
    AdapterReply<AdapterReadbackValue>? Readback,
    OperationOutcome? LogicalOutcome, ImmutableArray<ModuleIssue> Issues);
public interface IProjectorAdapter
{
    ValueTask<AdapterReply<AdapterOpenValue>> OpenAsync(
        AdapterContext context, AdapterOpen request, CancellationToken ct);
    ValueTask<AdapterReply<Capability>> GetCapabilityAsync(AdapterContext context, CancellationToken ct);
    ValueTask<AdapterReply<AdapterUploadValue>> UploadAsync(
        AdapterContext context, AdapterUpload request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterPreparedValue>> PrepareAsync(
        AdapterContext context, AdapterPrepare request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterArmedValue>> ArmAsync(
        AdapterContext context, AdapterArm request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterReadbackValue>> DisplayStepAsync(
        AdapterContext context, AdapterDisplay request, CancellationToken ct);
    IAsyncEnumerable<AdapterStreamItem> ExecuteHardwareSequenceAsync(
        AdapterContext context, AdapterExecute request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterReadbackValue>> ReadbackAsync(
        AdapterContext context, AdapterReadback request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterStopValue>> StopAsync(
        AdapterContext context, AdapterStop request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterBlackoutValue>> BlackoutAsync(
        AdapterContext context, AdapterBlackout request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterDrainValue>> DrainAsync(
        AdapterContext context, AdapterDrain request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterReleaseValue>> ReleaseAsync(
        AdapterContext context, AdapterRelease request, CancellationToken ct);
    ValueTask<AdapterReply<AdapterCloseValue>> CloseAsync(
        AdapterContext context, AdapterClose request, CancellationToken ct);
}
public enum LedgerBeginStatus { New = 1, Replay = 2, Conflict = 3, Unavailable = 4, Released = 5 }
public enum LedgerAppendStatus { Committed = 1, Conflict = 2, Unavailable = 3 }
public sealed record LedgerBeginRequest(
    CommandMeta Meta, CommandKind Kind, Guid? ParentExecutionOperationId,
    ImmutableArray<byte> CanonicalRequest, ClockStamp Deadline);
public sealed record LedgerBeginReply(
    LedgerBeginStatus Status, long Revision, OperationSnapshot? Snapshot,
    ImmutableArray<byte> OriginalReplyBytes, ImmutableArray<ModuleIssue> Issues,
    OperationTombstone? Tombstone);
public sealed record LedgerAppendRequest(
    Guid OperationId, long ExpectedRevision, ProjectionEvent Event,
    OperationSnapshot Snapshot, ImmutableArray<byte> ReplyBytes, ClockStamp Deadline);
public sealed record LedgerAppendReply(
    LedgerAppendStatus Status, long Revision, ImmutableArray<ModuleIssue> Issues);
public interface IOperationLedger
{
    ValueTask<LedgerBeginReply> BeginAsync(LedgerBeginRequest request, CancellationToken ct);
    ValueTask<LedgerAppendReply> AppendAsync(LedgerAppendRequest request, CancellationToken ct);
    ValueTask<OperationQuery> ReadAsync(OperationQueryRequest request, CancellationToken ct);
    ValueTask<EventPage> ReadEventsAsync(EventQuery request, CancellationToken ct);
    ValueTask<RetentionReleaseReply> ReleaseAsync(RetentionReleaseRequest request, CancellationToken ct);
    ValueTask<RetentionUsage> GetUsageAsync(CancellationToken ct);
}
public enum AuthorityDecision { Allowed = 1, Denied = 2, Expired = 3, Unavailable = 4 }
public sealed record AuthorityRequest(
    string Scope, string ProjectorId, CommandKind Kind,
    string? SequenceHash, ClockStamp Deadline);
public sealed record AuthorityReply(
    AuthorityDecision Decision, long Revision, ClockStamp? ValidUntil,
    ImmutableArray<ModuleIssue> Issues);
public interface IProjectionAuthority
{
    ValueTask<AuthorityReply> CheckAsync(AuthorityRequest request, CancellationToken ct);
}
```

AdapterReply.Succeeded才Value非null，其它状态Value可null且Issues非空；拒绝必须KnownNotInvoked，异常/超时可能调用则Unknown；Confirmation不与Status合并。仅声明端口不能证明实机“StopConfirmed”。AdapterReadbackValue没有frameId；Slot/Ordinal同时有或同时null，PatternHash/ActualAt缺失不能补为请求值。光学传感器只对其标定观测域有效；OpticalBlackout=true且SensorReadback才支持Blackout.Confirmed。DeviceReadback的明确设备黑场状态也可按批准Profile确认，CommandAck永远AckOnly。

AdapterDrainValue.Pending*均>=0，仅三个都0且实际回调/命令查询确认时Status=Confirmed，不能用本地队列空代表设备排空。Release不许在PendingSlotReferences>0时调用；只返回Released=true且连接仍有其他缓存不等于Shutdown完成。Close仅在DrainConfirmed后，ConnectionReleased及CallbacksReleased都true才session可Disposed。任何SDK调用未真正返回，Core不能将取消/超时当作DrainConfirmed；AdapterContext清理期限后未知所有权仍在恢复服务。

Ledger.New必须Revision>0、Snapshot.Phase=Accepted；Replay提供原首个回执bytes/当前查询Snapshot，Conflict不改记录，Unavailable禁止新调用。Begin/Append耐久性是实现承诺，不通过接口名称证明；托管测试用同语义内存ledger，生产宿主另接耐久实现。ReplyBytes编码只服务本模块回放，固定域ASUN-SL-REPLY-2+CommandKind+对应C.1结果按声明次序；Snapshot/Issue/Clock/Asset按字段次序，nullable/array沿§3.1。不序列化异常/委托，不以原设备命令重建回执。回执不可观测字段保持null；回放校验schema/域，不能decode则SL-MIG-001隔离、不重发。

执行父记录的Append与子命令记录分别CAS；同一物理输出由session Owner串行，对ParentExecutionOperationId的更新完成耐久提交后才回复。append持久化未知时operation Unknown且仍保留设备Owner，不能用旧snapshot Completed。各请求/回执bytes+事件计入MaxLedgerBytes；预留至少本次剩余终态/cleanup容量，不足时拒绝新输出但使用已预留cleanup容量。MaxRetainedOperations不允许逐出未知/活跃记录，已终态且不再被使用者引用才经ReleaseOperationAsync/C.5压缩为有限小头墓碑，不保留完整ReplyBytes；不得删除idempotency索引使旧请求再次New。

Authority.Allowed需Revision>0/ValidUntil非null且同clock域足够覆盖本次执行+cleanup；Denied/Expired/Unavailable禁止输出，原接纳scope过期仍允许原操作内部Stop/Blackout排空，不能续生产动作。cleanup scope就是原AuthorityScope及原ExecutionOperationId的绑定，不给任意caller额外关光权限。

### C.4 时序、诊断和模拟的缺口闭合

C.2执行stream的StepActual/LogicalEnd互斥约束适用Retained结果；C.1追加ExecutionItemKind.Released例外只用于旧已压缩identity，Tombstone必填、Actual/LogicalOutcome为null，不属于新的执行组。Host不得把Released项落为新的设备Actual/重复LogicalEnd；Query/EventPage Released按§6.1/C.5返回墓碑而非Unknown或NotFound。C.1 ModuleIssue白名单本版追加SL-RET-001/002，详细原因和自然文案见D，技术码不直显为操作指令。

```csharp
public sealed record ClockMapping(
    ClockStamp SourceAnchor, ClockStamp TargetAnchor,
    long OffsetNs, long UncertaintyNs, ClockStamp ValidFrom,
    ClockStamp ValidUntil, string Sha256);
public enum SimulatorAdapterFault
{
    None = 0, Disconnect = 1, LostReply = 2, LateReadback = 3,
    GenerationReset = 4, OverTemperature = 5,
    BlackoutAckOnly = 6, DrainUnknown = 7, CallbackOverflow = 8
}
public sealed record SimulatorAdapterOptions(
    Capability Capability, SimulatorAdapterFault Fault, int? FaultOrdinal,
    long ReplyDelayTicks, long JitterTicks, long? LateReplyTicks,
    bool InitiallyDrained, int MaxRetainedCallbacks);
```

唯一模拟factory签名 `ProjectorSimulator.Create(SimulatorAdapterOptions options, IProjectionClock clock)`→IProjectorAdapter；无设备IO、所有值标Simulation。Fault=None时FaultOrdinal=null，执行step故障Ordinal为0..N-1，其它故障发生在下一个对应Open/Stop/Blackout/Drain点；Options和固定clock决定结果，不用Random/真实Sleep。ReplyDelay/Jitter>=0，LateReplyTicks若有>0，MaxRetainedCallbacks>0；抖动按偶数ordinal加Jitter、奇数减Jitter且不低于0。不能把Simulation capability改Physical。

ClockMapping两个Anchor为不同域时，OffsetNs为两锚处映射到target域的残余校正：targetNs=TargetAnchorNs+(sourceNs-SourceAnchorNs)+OffsetNs，UncertaintyNs>=0；频率不要求相同。各ClockStamp转ns为BigInteger精确有理数Ticks*1000000000/FrequencyHz，校验曝光start下界向下取整、end上界向上取整并加两端uncertainty，不用浮点double直接相减；最终long范围溢出拒绝。ValidFrom/Until属于source域且from<=until，source窗口须完整在其间；target窗口必须完整落在targetStepStart+SettleNs+GuardBeforeNs至targetStepStart+HoldNs-GuardAfterNs。不能以此估算硬件相位稳定。ProjectionSequence不增加隐含ClockMapping字段；宿主用公开纯函数签名 `ProjectionTiming.ValidateMapping(ClockMapping mapping, ClockStamp sourceExposureStart, ClockStamp sourceExposureEnd, TimingStep targetStep, ClockStamp targetStepStart)`→ValidationReport，在Arm前单独验证。没有资格证据的mapping最多Simulation验证，真实触发仍门。

Timing诊断在初版RunDiagnostic仅Readback/能力快照，不直接发光、不会绕过Prepare/Arm。需要发光的时序诊断由宿主显式组合§9.2完整execution并将观测ProfileRef传入；诊断Receipt不虚构ExecutionOperationId。SelfTest同样只读取适配器状态，不调用未知厂商自检API。确认停止/排空后的故障复核可调用Recover；UI不能通过RunDiagnostic将Faulted自动复位。


### C.5 共享保留额度、墓碑和Release完整类型

类型仍在Asun.Modules.StructuredLight.Projection，B/D引用其纯值，未授予跨模块事实写入权限。这些保留字段沿Slice-1/2既有六项文档规格及Slice-3指导限定内容接收；附录A/Slice-0的canonical/limits保持原样。所有期限同注入clock，正额度显式传入。

有限session身份隔离：Policy.NamespaceId是宿主分配的非零ulong，生产/长生命周期宿主用已有配置/持久Owner单调分配且不复用；不是全局可变模块状态。OperationId/Ui.CommandId/Display.RequestId/SubscriptionId的Guid网络字节序前8bytes固定为NamespaceId big-endian、后8bytes为非零随机nonce。公开纯构造签名 `RetentionIdentity.New(ulong namespaceId)`→Guid（只生成值，不登记/IO）；所有接纳入口先校验前缀，异namespace副作用前拒绝SL-CON-001，不能作为新操作接纳。session内nonce碰撞按同id hash去重/冲突处理，不改变本页有限额度；Projection生产ledger恢复继续原namespace。新Vision/UI scope换namespace后旧identity只从原恢复Owner查询/释放，不在新scope运行；caller不可手动给旧OperationId重写前缀并称重试。RequestSha包括完整Guid，改前缀已是新身份且须宿主明确新业务意图，不能恢复未知操作。此规则只针对后续Slice登记identity，不改Core.PatternId/Steps或已接收canonical向量；SessionId/ActualId/LeaseId等结果关联Guid保持既有规则。

```csharp
public sealed record RetentionPolicy(
    ulong NamespaceId, int MaxPayloadRecords, long MaxPayloadBytes,
    long MaxSingleReplyBytes, int MaxIdentityRecords,
    long MaxIdentityBytes, long ResultRetentionNs);
public enum ResultRetentionState { Retained = 1, Expired = 2, Released = 3 }
public enum RetainedReplyKind { Projection = 1, Vision = 2, UI = 3, Display = 4, Subscription = 5 }
public sealed record OperationTombstone(
    Guid Identity, string RequestHash, string ResultHash,
    OperationOutcome TerminalOutcome, DrainStatus DrainStatus,
    ResourceStatus ResourceStatus, long LastStateVersion, ClockStamp ReleasedAt,
    string? IdempotencyKey, ImmutableArray<byte> ReplyHeaderBytes);
public enum RetentionReleaseStatus
{
    Released = 1, AlreadyReleased = 2, Busy = 3,
    Conflict = 4, NotFound = 5, Unavailable = 6
}
public sealed record RetentionReleaseRequest(
    Guid Identity, string RequestHash, long ExpectedStateVersion, ClockStamp Deadline);
public sealed record RetentionReleaseReply(
    RetentionReleaseStatus Status, OperationTombstone? Tombstone,
    ImmutableArray<ModuleIssue> Issues);
public sealed record RetentionUsage(
    int PayloadRecords, long PayloadBytes, int IdentityRecords,
    long IdentityBytes, long ReservedCleanupBytes, ClockStamp ObservedAt);
```

retention状态在Projection.OperationQuery和Vision.VisionQueryReply/UI.UiReply中按下列声明字段返回；Retained/Expired仍完整payload，Released只有墓碑。UiReply.StateVersion为Host该CommandId登记的正revision，不等于SelectionRevision或设备CAS；QueryStatus.Released才墓碑非null、其它情况下null。OperationTombstone.TerminalOutcome记录原结果，不重新取现在的设备状态；ResultHash是完整原回执（跳过新增RetentionState自身）的canonical SHA256，不用请求hash冒充。

ReplyHeaderBytes是完整原回执的固定小头，最多4096 bytes，域ASUN-SL-RET-2末尾单NUL，随后写RetainedReplyKind（Projection=1/Vision=2/UI=3/Display=4/Subscription=5）和如下固定字段，不含图案内容、层、metrics/candidate列表、事件/异常字符串或Tombstone自身。Projection=CommandKind/OperationId/SessionId/Generation/StateVersion及SequenceHash(nullable)；Vision=VisionOperationKind/OperationId及SpecHash(nullable)/AttemptId(nullable)/SequenceHash(nullable)/ManifestHash(nullable)/ProfileRef(nullable)/RuntimeRef(nullable)/CalibrationRef(nullable)/ExpiresAt(nullable)/AlgorithmRoute(nullable)/ProducerId(nullable)/ProducerVersion(nullable)/BaselineHash(nullable)/EvidenceHash(nullable)，缺少的kind专属项明确presence0；UI=UiCommandKind/CommandId/SelectionRevision/ExpectedSequenceHash(nullable)/内嵌OperationId(nullable)；Display=DisplayRequest.RequestId/SelectionRevision/AssetRef；Subscription=SubscriptionId/LastSequence。其后统一原OperationOutcome、DrainStatus、ResourceStatus。Enums沿本页声明，nullable沿canonical，不含调用方翻译。墓碑保留原IdempotencyKey（Projection）/其它种类null，索引绑定Identity→hash与key→Identity不发生重定向。

为恢复VisionReleased的必需非nullablemetadata，session从此小头回填原Profile/Runtime/Attempt/Sequence/Manifest等字段，非法输入导致未接纳Rejected则不登记、无Released形式；Generate/Observe/RecommendationReleased对应大集合空/Plan=null、Tombstone必填。OriginalReplyBytes在LedgerBegin.Released为空，Tombstone为原墓碑；不能解析头返回Unavailable+SL-MIG-001且禁止重发。ResultHash计算原完整回执时跳过Tombstone/RetentionState（两者为后加保留投影），不是对当前Released短回执计算。字段容量超4096或single-reply额度无法预留时副作用前拒绝，不为成功任务造截断头。墓碑charge修正为4096+ReplyHeaderBytes.Length+4*墓碑各string UTF8总bytes；在接纳前按最大4096头预留，释放后按实际charge归还差额，索引charge仍单独计。它是有限字节预算而非CLR内存测量。

Release能力所有返回的Tombstone仅Status.Released/AlreadyReleased时必填；Busy/Conflict/NotFound/Unavailable为null并保留具体Issues。ExpectedStateVersion>0；AlreadyReleased按原hash回相同墓碑优先于过时CAS，不允许新hash借过时CAS变成Released。GetUsage计数非负且不超过Policy（含预留），查询结果本身大小在MaxSingleReplyBytes内；可不新增永久查询记录。Policy.ResultRetentionNs不是设备预算、Advice.ExpiresAt或display.ExpiresAt，三者不得互相替代。

Disposed的精确行为：Dispose释放实际工作/显示/native引用，不释放有限墓碑索引的查询Owner；原对象保留仅查询/旧identity回复的轻量登记直到宿主生命周期结束，不开放新identity接纳。Projection透传原ledger墓碑，Vision/UI原scope有限登记继续响应Query/GetUsage/AlreadyReleased及已Released同id/hash短回执；先判断namespace及旧hash/墓碑，再检查新请求的Disposed状态。旧同id异hash仍Conflict；新idObjectDisposedException且无副作用。宿主退出后Projection历史可从原ledger读取，Vision/UI内存scope仅原Owner仍存活时可查询；新scope拒绝旧identity前缀，不声称已丢失内存结果仍可读取，也不重新生成。所有待恢复Unknown任务必须在Dispose前移交存活Owner；不能销毁旧内存scope来处理未知任务或绕有限identity容量。


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

## 附录 D：Slice-3 WPF 托管 Host / View 声明 v0.2

本附录仅声明本模块WPF控件的端口，不猜DevExpress/视口/其它模块已有方法。全部设备/生成动作通过宿主组合Projection/Vision公开端口。namespace为Asun.Modules.StructuredLight.Ui.Wpf，下面代码引用.NET WPF/BCL及本模块契约，不泄漏SDK/native句柄。

### D.1 选择、命令、回复和完整Payload

```csharp
using System;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Controls;
using Asun.Modules.StructuredLight;
using Asun.Modules.StructuredLight.Projection;
using Asun.Modules.StructuredLight.Vision;

namespace Asun.Modules.StructuredLight.Ui.Wpf;

public sealed record StructuredLightViewOptions(
    string CultureName, string ThemeName, bool ReadOnly,
    int MaxVisibleEvents, long MaxThumbnailBytes, int MaxChartPoints, int RefreshIntervalMs,
    long QueryBudgetNs, long CleanupBudgetNs, RetentionPolicy Retention);
public sealed record ViewSelection(
    long Revision, string? SequenceHash, int? StepOrdinal, Guid? ExecutionOperationId);
public enum UiCommandKind
{
    ValidateDraft = 1, GenerateDraft = 2, Prepare = 3, StartPreview = 4,
    StopAndDrain = 5, Recover = 6, Observe = 7, Recommend = 8, Shutdown = 9
}
public abstract record UiPayload;
public sealed record ValidateDraftPayload(
    ManagedPatternPlan Plan, PlanningLimits Limits) : UiPayload;
public sealed record GenerateDraftPayload(GenerateRequest Request) : UiPayload;
public sealed record PreparePayload(PrepareRequest Request) : UiPayload;
public sealed record StartPreviewPayload(
    ArmRequest Request, long PreviewBudgetNs) : UiPayload;
public sealed record StopAndDrainPayload(StopRequest Request) : UiPayload;
public sealed record RecoverPayload(RecoverRequest Request) : UiPayload;
public sealed record ObservePayload(ObservationRequest Request) : UiPayload;
public sealed record RecommendPayload(RecommendationRequest Request) : UiPayload;
public sealed record ShutdownPayload(ShutdownRequest Request) : UiPayload;
public sealed record UiCommand(
    Guid CommandId, long SelectionRevision, string? ExpectedSequenceHash,
    string AuthorityScope, UiCommandKind Kind, UiPayload Payload);
public enum UiReplyStatus { Applied = 1, Rejected = 2, Stale = 3, Unknown = 4, Released = 5 }
public abstract record UiResult;
public sealed record ValidationUiResult(ValidationReport Report) : UiResult;
public sealed record GenerationUiResult(GenerateReply Reply) : UiResult;
public sealed record PrepareUiResult(CommandReply<PreparedReceipt> Reply) : UiResult;
public sealed record PreviewUiResult(CommandReply<ArmedReceipt> Reply) : UiResult;
public sealed record StopUiResult(CommandReply<DrainReceipt> Reply) : UiResult;
public sealed record RecoverUiResult(CommandReply<SessionSnapshot> Reply) : UiResult;
public sealed record ObservationUiResult(ObservationReply Reply) : UiResult;
public sealed record RecommendationUiResult(RecommendationReply Reply) : UiResult;
public sealed record ShutdownUiResult(CommandReply<DrainReceipt> Reply) : UiResult;
public sealed record UiReply(
    Guid CommandId, long SelectionRevision, UiReplyStatus Status,
    UiResult? Result, ImmutableArray<ModuleIssue> Issues, OperationTombstone? Tombstone,
    long StateVersion, ResultRetentionState RetentionState, string RequestHash);
public sealed record ViewSnapshot(
    long Revision, ViewSelection Selection, SessionSnapshot Session,
    Capability? Capability, ManagedPatternPlan? Draft, ProjectionPlan? Plan,
    ImmutableArray<ProjectionActual> VisibleActuals,
    ImmutableArray<ProjectionEvent> VisibleEvents,
    ObservationReply? Observation, RecommendationReply? Advice,
    bool PlanStale, bool ObservationStale, bool AdviceStale,
    bool EventsWindowed, ImmutableArray<ModuleIssue> Issues);
public sealed record UiQueryRequest(Guid OperationId, ClockStamp Deadline);
public interface IStructuredLightViewHost
{
    ValueTask<ViewSnapshot> GetSnapshotAsync(CancellationToken ct);
    ValueTask<UiReply> ValidateDraftAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> GenerateDraftAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> PrepareAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> StartPreviewAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> StopAndDrainAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> RecoverAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> ObserveAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> RecommendAsync(UiCommand command, CancellationToken ct);
    ValueTask<UiReply> ShutdownAsync(UiCommand command, CancellationToken ct);
    ValueTask<OperationQuery> QueryOperationAsync(UiQueryRequest request, CancellationToken ct);
    ValueTask<ViewCloseReply> ClosePreviewAsync(ViewCloseRequest request, CancellationToken ct);
    ValueTask<IViewEventSubscription> SubscribeEventsAsync(
        ViewSubscriptionRequest request, IViewEventSink sink, CancellationToken ct);
    ValueTask<DisplayLeaseReply> AcquireDisplayAsync(DisplayRequest request, CancellationToken ct);
    ValueTask<DisplayReleaseReply> ReleaseDisplayAsync(DisplayReleaseRequest request, CancellationToken ct);
    ValueTask<DisplayQueryReply> QueryDisplayAsync(DisplayQueryRequest request, CancellationToken ct);
    ValueTask<string> ResolveTextAsync(TextRequest request, CancellationToken ct);
    ValueTask<RetentionReleaseReply> ReleaseCommandAsync(RetentionReleaseRequest request, CancellationToken ct);
    ValueTask<RetentionUsage> GetRetentionUsageAsync(CancellationToken ct);
    ValueTask<UiCommandQueryReply> QueryCommandAsync(UiCommandQueryRequest request, CancellationToken ct);
}
```

UiPayload/UiResult只允许本附录sealed派生类型，运行时自造类型拒绝SL-VAL-001；不用object/Dictionary/string JSON藏未知字段。Kind必须与Payload和调用方法匹配，Result与原Kind一致；Applied仅指命令已接纳/结果可展示，不代表资源终态/质量合格。UiReply.Stale不调用设备，Unknown含原CommandId/原operation可查；晚到Applied只可写历史，不能覆盖新Revision。选择在设备执行中改变不撤销原execution。

Host实例是一个明确view scope，一个Host实例不能同时Bind两个view；两个view各注入自己的Host/selection/subscription/display索引，底层设备session仍按物理设备Owner互斥。这样GetSnapshotAsync/Text/Query不会读“当前全局窗口”。UiCommand所有string/hash和嵌套请求重验，SelectionRevision>=1，ExpectedSequenceHash在Generate/Validate无已选计划时才可null，Prepare/Preview/Observe/Recommend必须与当前选择精确相符。Close/Stop/Query使用原OperationId，即使选择已变仍可停止自己的旧预览；不能要求旧hash变当前hash才能关光。Host.Unknown必须Issues说明已调用/排空/查询状态，不可仅隐藏Result造成“未调用”错觉。UiReply.RequestHash固定域ASUN-SL-UI-CMD-2加单NUL后编码完整UiCommand，Kind指定唯一Payload派生类型（不另写C#类型名），字段顺序沿D声明；Validate/Generation payload中大Content只写其hash，ManagedPatternPlan用A完整metadata/steps canonical但不混入隐藏limits，显式PlanningLimits另编码，所有hash规范小写/32bytes。查询与Release以此hash，不能用嵌套设备RequestSha代替UI命令hash。

StartPreviewPayload只软件步进预览：PreviewBudgetNs>0且<=Arm后剩余总deadline及lease有效期；Host依据既有prepared序列依次调用DisplayStep并将Actual写ledger，deadline前独立cleanup。UI StartPreviewAsync的返回值只是Armed回执，其后进度/终态走事件/Query；Host无窗口也执行TTL。Hardware预览初版拒绝，不以未知payload启动设备。AuthorityScope与内嵌Meta.AuthorityScope必须相同；UiCommand.CommandId用于view层去重，内嵌Meta.OperationId仍设备权威身份，不能由view重新分配。重复CommandId/同Payload回原reply，异payload拒绝；stale selection不能以重试获得旧权限。

### D.2 事件、关闭与显示lease

D的RetainedReply/UiQuery/Display与订阅索引计入Options.Retention，全量不可在ViewSnapshot/OnEvents之外无限缓存。UiReplyStatus.Released和DisplayStatus.Released都无大结果/显示buffer且墓碑必填，其它状态Tombstone=null；UiCommandQuery.Released无Reply。QueryDisplay资源已归还返回Released+墓碑，Pending/Held仍Found且Lease可null，不能通过Status.Released表示“已发送Release请求”。GetUsage锁等待以Options.QueryBudgetNs限制。ResolveText仅缓存已登记资源目录（有界键/语言来自宿主目录），不为任意TextRequest参数组合永久缓存；后备三语最小资源是固定常量目录，不为每次缺键新增结果identity或日志无限队列。

```csharp
public sealed record ViewSubscriptionRequest(
    Guid SubscriptionId, long AfterSequence, int MaxQueuedItems,
    int MaxBatchItems, ClockStamp Deadline);
public enum ViewEventKind
{
    Snapshot = 1, Projection = 2, Generation = 3,
    Observation = 4, Advice = 5, Display = 6, Gap = 7, Closed = 8
}
public sealed record ViewEvent(
    long Sequence, long SelectionRevision, ViewEventKind Kind,
    ViewSnapshot? Snapshot, ProjectionEvent? Projection,
    GenerateReply? Generation, ObservationReply? Observation,
    RecommendationReply? Advice, DisplayLeaseReply? Display,
    ImmutableArray<ModuleIssue> Issues);
public sealed record ViewEventBatch(
    Guid SubscriptionId, ImmutableArray<ViewEvent> Events,
    long LastSequence, bool NeedsResync);
public interface IViewEventSink
{
    ValueTask OnEventsAsync(ViewEventBatch batch, CancellationToken ct);
}
public interface IViewEventSubscription : IAsyncDisposable
{
    Guid SubscriptionId { get; }
    ValueTask<ViewSubscriptionState> GetStateAsync(CancellationToken ct);
}
public sealed record ViewSubscriptionState(
    Guid SubscriptionId, bool Closed, long LastSequence,
    bool NeedsResync, int QueuedItems, DrainStatus DrainStatus,
    ResourceStatus ResourceStatus, ImmutableArray<ModuleIssue> Issues);
public sealed record ViewCloseRequest(
    Guid ViewSessionId, Guid? PreviewExecutionOperationId,
    long CleanupBudgetNs, string ReasonKey);
public sealed record ViewCloseReply(
    Guid ViewSessionId, DrainStatus DrainStatus, ResourceStatus ResourceStatus,
    ImmutableArray<Guid> UnresolvedOperationIds,
    ImmutableArray<Guid> UnresolvedDisplayRequestIds,
    ImmutableArray<Guid> UnresolvedSubscriptionIds, bool RecoveryOwnerAccepted,
    ImmutableArray<ModuleIssue> Issues);
public sealed record DisplayRequest(
    Guid RequestId, long SelectionRevision, AssetRef Asset,
    int MaxWidth, int MaxHeight, long MaxBytes, ClockStamp Deadline);
public enum DisplayStatus { Acquired = 1, Rejected = 2, Stale = 3, Unknown = 4, Released = 5 }
public sealed record DisplayLease(
    Guid LeaseId, AssetRef SourceAsset, long SelectionRevision,
    int Width, int Height, int StrideBytes, ImmutableArray<byte> Bgra32,
    bool Downsampled, DateTimeOffset ExpiresAt);
public sealed record DisplayLeaseReply(
    Guid RequestId, DisplayStatus Status, DisplayLease? Lease,
    ImmutableArray<ModuleIssue> Issues, OperationTombstone? Tombstone);
public sealed record DisplayReleaseRequest(Guid LeaseId, ClockStamp Deadline);
public sealed record DisplayReleaseReply(
    Guid LeaseId, bool Released, ImmutableArray<ModuleIssue> Issues,
    OperationTombstone? Tombstone);
public sealed record DisplayQueryRequest(Guid RequestId, ClockStamp Deadline);
public sealed record DisplayQueryReply(
    Guid RequestId, QueryStatus Status, DisplayLease? Lease,
    ResourceStatus ResourceStatus, ImmutableArray<ModuleIssue> Issues,
    OperationTombstone? Tombstone);
public sealed record UiCommandQueryRequest(Guid CommandId, ClockStamp Deadline);
public sealed record UiCommandQueryReply(
    QueryStatus Status, UiReply? Reply, OperationTombstone? Tombstone,
    ImmutableArray<ModuleIssue> Issues);
public sealed record TextRequest(
    string Key, string CultureName, ImmutableArray<string> Arguments);
public interface IStructuredLightViewSession : IAsyncDisposable
{
    Guid ViewSessionId { get; }
    ValueTask UpdateCultureAsync(string cultureName, CancellationToken ct);
    ValueTask ApplySnapshotAsync(ViewSnapshot snapshot, CancellationToken ct);
    ValueTask<ViewCloseReply> CloseAsync(ViewCloseRequest request, CancellationToken ct);
}
```

唯一控件公开签名：`StructuredLightView : UserControl`，`IStructuredLightViewSession Bind(IStructuredLightViewHost host, StructuredLightViewOptions options)`。Bind在控件Dispatcher上执行，返回当前view scope并只绑定一次；重复Bind须先旧session.Close/Dispose/解绑。ApplySnapshotAsync替代旧无Async的名称，不构建隐藏窗口。所有Apply/UpdateCulture通过Dispatcher有界投递（不等待已关闭Dispatcher），ct仅取消显示工作；默认closed对象明确ObjectDisposedException，不改设备状态。

Bind局部原子性与§9.5一致：同步只校验options/唯一view scope、建立本地session和控件绑定，不在返回前调用设备、SubscribeEvents/AcquireDisplay或启动后台工作；失败时回滚本次局部绑定/事件处理器/引用，Host未接纳外部动作。成功返回由调用的Dispatcher委托先强写进程根槽再交付；投递已运行而caller超时仍保持原BindTask/view/Host，晚到session归同根，不第二次Bind。Apply/UpdateCulture等投影委托关闭后跳过未执行部分，已执行或无法投递不推断资源归还；原投递/回调/异步Task均按§9.5保留。此为既有签名的实施要求，不新增“找回session”API。

ViewSnapshot.Revision>=1且Selection.Revision一致；VisibleActuals/VisibleEvents<=Options.MaxVisibleEvents，截窗必须EventsWindowed=true并保留可查ledger identity。全量集合不能先进ViewSnapshot再截以规避预算。DisplayReply只Kind.Display填Display；其它Kind严格只填对应payload，Gap/Closed无payload有Issues。OnEventsAsync在普通工作线程单订阅串行调用，不设备回调/Dispatcher；view桥负责Dispatcher。sink异常/超时停止该订阅，NeedsResync=true，不终止设备或丢ledger；query原snapshot+GetEvents补窗，Sequence不补成连续假事件。

Subscribe起点AfterSequence=-1，MaxQueuedItems/MaxBatchItems正值且batch<=queue，预算由Host限制；Deadline有限、无永续隐式长轮询。达到deadline以Closed事件或GetState.Closed确认停止准入，只有GetState.DrainConfirmed/Released才确认订阅回调已归还。溢出发送可保留Gap/NeedsResync并关闭展示订阅，原审计仍完整；纯Snapshot进度可合并，ProjectionActual/故障/逻辑结束/排空不得合并覆盖。DisposeAsync停止准入并等待已接纳sink调用到有限subscription deadline，回调不能再访问view；到期保持subscription恢复Owner而view解绑显示，SL-DISPOSE-001/DrainUnknown/Held，不将未完成回调算成功Disposed。重复Dispose不发设备命令。Close在UnresolvedSubscriptionIds保留未完成订阅；订阅Closed和设备Closed不是同一事实。

DisplayLease只有托管自有BGRA32 buffer，top-down、StrideBytes=checked Width*4、Length=checked stride*height<=int.MaxValue，padding为0、byte数<=request.MaxBytes及view总MaxThumbnailBytes；Premultiplied alpha明确使用（无alpha原图转255）。所有像素转换/降采样仅显示，在宿主现有viewport服务实现，不在本模块改原测量/图案。收到新Revision/过期/关闭的旧Lease必须ReleaseDisplay，不只丢引用。Release回执Released=false/超时则保留leaseId到宿主清理Owner、禁止新显示超总预算；已有不可变bytes的owner由宿主回执追踪，不能从GC推断已归还。Acquire接纳后丢回执仍按原RequestId QueryDisplay，不新request重复分配；Found可含正在生成时的null Lease/Held，NotFound/Unavailable不证明Released。Query有deadline且非阻塞，成功释放墓碑保留RequestId/ResourceStatus.Released、Lease=null；Close将未解决RequestId列在UnresolvedDisplayRequestIds并移交恢复Owner，不能只关投影却泄漏显示资源。

TextRequest只传本模块已登记资源键和显示string参数，不在业务hash/诊断中插入翻译。ResolveText缺键、空串、异常或期限到期时，操作区必须显示控件内置最小后备资源：zh-CN“提示暂时无法显示。请查看诊断记录。”；zh-TW“提示暫時無法顯示。請查看診斷紀錄。”；en-US“Message unavailable. Check the diagnostic log.”。缺键标记/key/code只进入详细诊断，可独立显示经本地资源格式化的诊断编号，不直接把enum、资源键、原始异常或“文字资源缺失”作为操作文案。此最小后备资源随UI程序集，不再递归调用已失败ResolveText。已释放结果的后备短句分别为“结果已释放。请查看原操作记录。”、“結果已釋放。請查看原操作紀錄。”、“Result released. Check the original operation record.”；Busy为“操作尚未结束，暂不能释放结果。”、“操作尚未結束，暫時無法釋放結果。”、“Operation is still active. The result cannot be released yet.”。Culture只能zh-CN/zh-TW/en-US或宿主已登记扩展资源；扩展语言缺本地后备时沿宿主已批准fallback culture，最终en-US，不临时造翻译。UI scope切换后文本/数字重新投影，ID/Canonical不变。ThemeName必须宿主已有主题，不改Application全局；ReadOnly拒绝所有发光/恢复/参数提交，仅允许看/查询和本view ClosePreview内部cleanup。

ViewCloseRequest只关闭此view发起的PreviewExecutionOperationId；生产Host任务不属于view，关闭不取消它。ClosePreview需先移交原execution及所有显示/订阅资源到Host恢复服务并开始StopAndDrain；三个Unresolved集合任一非空时成功移交必须RecoveryOwnerAccepted=true且Held；无法移交则RecoveryOwnerAccepted=false，view不能宣布Closed或提前Dispose。订阅Dispose可按其既有停止/有限等待契约首次启动，但只有GetState.Closed且实际Confirmed/Released后才解除订阅Owner；显示只有ReleaseDisplay实际Released后才解除重资源Owner。原viewSession.Dispose另须§9.5全部前置。closeDeadline到期仍允许窗口从宿主恢复面板追踪原operation，RecoveryOwnerAccepted不代替全量根槽接收。所有集合返回非default，已确认关闭三集合必须均空。禁止按钮以“已关闭窗口”冒充设备终态。

所有Host读操作/文本/Dispatcher投影以Options.QueryBudgetNs建立独立有限等待，caller CancellationToken同时有效；操作的底层等待期限以签名中的deadline或嵌套Meta为准。Close/显示归还使用Options.CleanupBudgetNs和新token，不能沿cancelled UI token。到期保留原RequestId/SubscriptionId到Host恢复Owner并返回Unknown或查询状态，不将被超时包装的底层Task判为已结束。Dispatch无法投递也不会取消正在运行的投影；UI控件Dispose不得独立杀死设备线程。

