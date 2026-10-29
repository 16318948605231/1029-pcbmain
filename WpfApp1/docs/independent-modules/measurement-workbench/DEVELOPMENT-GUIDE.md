# IM-065 独立测量工作台开发指导

> 状态标记：review=`DesignReview`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2`

- 模块 ID：`IM-065`
- 模块键：`measurement-workbench`
- 中文名称：二维/三维测量工具工作台
- 状态：全部已批准范围的可决定软件设计已闭合；C1/C2 `ModuleCoreImplementationReady`；A1/U1 既有接收保持；整模块集成/运行仍 `PreparationIncomplete / NotReady`（2026-10-11；准确范围见 A.11.8）
- 指导版本：`0.7.0-prep`（2026-10-11；全模块准备核实及 A.11 补缺，Core API v0.3不变）
- 模块角色：可独立引用、构建、测试、发布和嵌入的测量工作台模块
- 规划消费者：独立工程测量工具、二维/三维工程工具、其他视觉项目
- 目标运行时：C# / .NET 10；WPF + DevExpress 25.2.3
- 视觉后端：HALCON 26.05，经 `ImageLibDotNet` 公共接口使用项目内 AsunImage
- 模块级设计评审态：`DesignReview`（方案可评审）。A.11「全批准范围的软件准备收口」已给出本模块当前批准范围的软件设计与自审结论；该状态只表示方案可供评审，不表示已实现、已集成、已测性能、已过 WPF/HIL 或已获生产资格。

本文是 `IM-065` 唯一活动指导。模块提供无 UI Core、可选 WPF/DevExpress 投影、显式适配端口和测试宿主；它可以独立发布并嵌入多个外部宿主。模块通过公开契约组合 `IM-024 roi-geometry`、`IM-036 metrology` 和 `IM-060 viewport`，但不复制三者的算法、资源事实或内部类型。外部产品宿主仍拥有产品目标、制程解释、质量放行、设备副作用和产品数据库事实。

## 1. 范围与边界

### 1.1 模块负责

1. 提供测量会话、不可变上下文、草稿、operation/attempt、状态事件和恢复元数据。
2. 通过公开端口编排来源、坐标、ROI、参数、计量、视口和证据引用的交互顺序。
3. 提供工具目录、参数草稿、校验、执行、取消、重算、结果比较和证据投影。
4. 在 2D/3D 间传递来源、几何和坐标身份，投影联动高亮、剖面和结果几何。
5. 提供页面级命令可用性、三语、权限快照、UIA、键盘、焦点和可恢复错误。
6. 提供可替换的适配端口、Replay/TestHost、故障注入和双消费者验证边界。

模块输出用户意图、结果投影、诊断和 typed receipt。产品宿主决定是否把结果用于工艺判定、报告、质量放行或设备动作；IM-065 不替代这些决定。

### 1.2 明确不负责

- 不实现 ROI 布尔、拓扑修复、绘制命中、撤销栈或 Region/XLD 转换；这些属于 `IM-024`。
- 不实现边缘提取、拟合、距离、角度、面积、体积和三维量测算法，也不持有计量算法事实；这些属于 `IM-036`。
- 不实现纹理/GPU/Tile 解码、三维渲染、显示缓存、拾取和视口变换；这些属于 `IM-060`。
- 不解释 PCB/PCBA 目标、焊盘、孔、位号、工单、制程缺陷、客户阈值或 Required/缺项。
- 不保存产品数据库表、质量事实、配方发布指针、设备 SDK 句柄或最终放行结论。
- 不把像素、屏幕坐标、颜色、结果行号、AI 分数、适配器 ACK 或 UI 保存成功转成物理事实。
- 不使用静态“当前图像/当前 ROI/当前配方”，不在隐藏窗口或构造函数中初始化视觉资源。
- 空输入、无支持、后端异常、取消、超时和未知回执不得返回 PASS；未知必须保留明确原因与 `Unknown`/`DrainUnknown`/`ReleaseUnknown`，不引入未定义 Blocked 状态。
- 不扫描、修改、反射访问或优化 AsunImage 内部；适配器只能经 `ImageLibDotNet` 公共边界调用已核对能力。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.MeasurementWorkbench.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"不使用静态当前图像/当前 ROI/当前配方，不在隐藏窗口或构造函数中初始化视觉资源"。

**Blazor/Web**：测量工作台的 Web 版本支持远程工程调试。服务端执行所有几何计算，浏览器只渲染测量结果标记；坐标由 `coordinate-geometry` 服务端计算后传递，浏览器不重写矩阵（同 IM-007 §1A）。

**AI Tiling**：`ai-inference` 推理结果可作为测量工作台的输入候选；本模块不持有推理 tile 租约，不参与分块编排。

**HALCON 双跑**：测量工作台复用 `metrology`/`features-2d` 等模块的 HALCON 路线；本模块自身不直接调用 HALCON 算子，HALCON 备选 CI 在被复用的子模块中执行。

## 2. 模块结构、依赖与发布单元

```text
外部产品宿主 / 工程工具 / 其他视觉项目
                 |
        IM-065 MeasurementWorkbench
       Core + 可选 WPF + Adapters
        /          |             \
 IM-024 ROI   IM-036 Metrology   IM-060 Viewport
        \          |             /
   image-frame / coordinate / parameter / evidence / authorization
```

| 单元 | 职责 | 约束 |
|---|---|---|
| `MeasurementWorkbench.Core` | 会话、快照、草稿、编排、状态、事件、请求/结果投影、恢复元数据 | 不引用 WPF、DevExpress、产品 VM、数据库或设备 SDK；不实现视觉算法 |
| `MeasurementWorkbench.Wpf` | 可选页面、布局、输入路由、UIA、三语、主题和状态投影 | 只调用 Core 和公开投影端口；不持有长期 native 句柄或写质量事实 |
| `MeasurementWorkbench.Adapters` | 来源、坐标、ROI、计量、视口、证据和会话存储的端口适配 | 显式声明版本、线程、取消、超时、租约和回退；不泄漏厂商对象 |
| `MeasurementWorkbench.TestHost` | 无 UI Replay、模拟端口、故障注入、Golden 和双消费者样例 | 只用于验证，不作为生产实现或现场资格证据 |

Core 只依赖稳定公开 Contract 和显式注入端口。WPF 依赖 Core，不反向污染 Core。适配器依赖端口 Contract，不引用 `IM-024/036/060` 内部实现。外部宿主可作为组合根，但不能改变 IM-065 的模块边界。

### 2.1 事实 Owner

| 事实 | Owner | IM-065 权限 |
|---|---|---|
| 帧、Tile/Pyramid、原值、有效域、租约 | `IM-006 image-frame` 或表面 Owner | 只读描述和 lease 引用 |
| 坐标、单位、标定、变换和求逆 | `IM-007 coordinate-geometry`、`IM-013 calibration-assets` | 请求映射和资格校验，保存 revision/hash |
| ROI 几何、编辑命令、Undo/Redo、提交 | `IM-024 roi-geometry` | 发送 typed intent，投影 draft/preview/receipt |
| 计量方法、数值结果、支持域和不确定度 | `IM-036 metrology` | 创建 request，跟踪 attempt，投影结果 |
| 渲染、Tile 缓存、拾取和显示坐标 | `IM-060 viewport` | 提交显示计划和联动意图 |
| 证据保存、查询和产品提交 | 外部注入的 Evidence/Submission Owner | 持有引用和回查 receipt，不写产品事实 |
| 权限、语言和诊断 | `IM-004`、`IM-003`、`IM-005` 与宿主 | 接收快照，不缓存永久授权或自建词典 |

## 3. 当前 Contract、工程绑定与实施切片

唯一模块 API 为附录 A 的 **Module API Contract v0.3**。本轮替代未实现的 v0.1/v0.2 暂停稿形状，删除自由字符串命令、重复 DTO 和自动刷新 latest 的入口；没有已发布客户端迁移承诺。正文只解释同一组声明。Core 的内容引用是带 Owner、版本、revision、hash 的不可变公开资产引用，具体 ROI/参数/计量内容由原模块的公开 Contract 解释，不以任意 JSON、字符串 payload 或私有类型补充接口。

### 3.1 工程、命名空间与允许范围

状态为 NewProjectRequired；下列是目标落点，尚未创建工程。本次文档任务只改本文件。

| 层 | 唯一工程/根命名空间 | 依赖与测试工程 |
|---|---|---|
| Core | src/Modules/measurement-workbench/Asun.Modules.MeasurementWorkbench.Core/Asun.Modules.MeasurementWorkbench.Core.csproj；Asun.Modules.MeasurementWorkbench | net10.0，仅 BCL，公开 Contract 同 DLL；tests/Modules/measurement-workbench/Asun.Modules.MeasurementWorkbench.Core.Tests/Asun.Modules.MeasurementWorkbench.Core.Tests.csproj |
| Adapters | src/Modules/measurement-workbench/Asun.Modules.MeasurementWorkbench.Adapters/Asun.Modules.MeasurementWorkbench.Adapters.csproj；同前缀 .Adapters | Core + 上游公开程序集；tests/Modules/measurement-workbench/Asun.Modules.MeasurementWorkbench.Adapters.Tests/Asun.Modules.MeasurementWorkbench.Adapters.Tests.csproj；视觉桥按需要固定 Windows target |
| Wpf | src/Modules/measurement-workbench/Asun.Modules.MeasurementWorkbench.Wpf/Asun.Modules.MeasurementWorkbench.Wpf.csproj；同前缀 .Wpf | net10.0-windows / UseWPF；Core、本机 DevExpress 25.2.3、上游公开 UI；tests/Modules/measurement-workbench/Asun.Modules.MeasurementWorkbench.Wpf.Tests/Asun.Modules.MeasurementWorkbench.Wpf.Tests.csproj |
| TestHost | samples/Modules/measurement-workbench/Asun.Modules.MeasurementWorkbench.TestHost/Asun.Modules.MeasurementWorkbench.TestHost.csproj；同前缀 .TestHost | 可选桌面完整工作台宿主；CLI 两消费者夹具放 Core.Tests；不成为生产默认 Adapter |

后续实现仅允许对应已授权切片的上述精确目录；唯一写入 Owner 为 IM-065 登记永久会话。禁止修改其它模块、共享 Contracts/solution、产品 Shell/Domain/数据库/设备 SDK、用户配置、原件/快照和 AsunImage 内部；共享引用由主任务串行整合。开产品代码前绑定权威仓库/分支或可审计快照；本目录无 Git 不阻断本轮文档。

### 3.2 完整模块切片

| 切片 | 包含的实际能力 | 后续门 |
|---|---|---|
| C1 | 有界根/会话、精确上下文、授权、执行编排、事件/查询、取消/真实排空/释放、幂等与两实例隔离 | 六项文档规格已由主控接收为ModuleCoreImplementationReady；后续实施按附录 A + T01/T09–T11/T15 + 两无 UI Host验证，不等待真实 HALCON/WPF |
| C2 | 工具/ROI/参数意图、建议采用、重算/比较、Checkpoint、保存/恢复/导出、未知回执原请求查询 | 六项文档规格已由主控接收为ModuleCoreImplementationReady；后续实施按C1 + T03/T04/T06/T12/T13验证，只使用确定端口与内存夹具，不写产品事实 |
| A1 | §8 已闭合公开内容的身份/单位/版本映射与 Replay | 仅A.6明确公开值/原请求/原结果映射指导内容已限定接收；实际上游编译/运行另验，未定义范围隔离，不复制算法 |
| A2 | 真实源/计量/native/证据/持久化桥 | 实际公开调用、Golden、资源/性能/权限/恢复验收 |
| U1 | 完整可嵌入 WPF 控件、单一主视区、参数/ROI/结果联动、局部三语、键盘/UIA/布局/有限 Detach | 公开装配与Owner恢复指导内容已限定接收；§7 与附录 A.7/A.8的真实 WPF/上游控件/Dispatcher 资格另验，不标纯 CoreReady |
| H1 | CLI EngineeringReplayHost 与独立 EmbeddedWorkbenchHost，两种组合根、完整端口注入；桌面双实例 TestHost | 各切片运行证据；两个夹具不冒充已交付的两个现场产品 |

小 Core 切片不替代完整模块；交付完成必须包含 Core、必要 Adapter、可选完整 UI、宿主接入说明与对应验证。

### 3.3 输入、单位和有效域

AssetRef 的 Owner/Id 标识非空、NFC、Ordinal 比较；字符串不 trim/变大小写，revision 从 1 起，Sha256 为 64 位小写 hex。SessionId/OperationId/AttemptId 为非空 Guid。集合非 default 且深冻结；空来源不允许 Attach/Execute，空工具目录可只读查看并明确无可用工具。全部字节/条数/在途/订阅计入 Profile，checked 运算溢出拒绝。

SourceBinding 明确来源类型、frame、calibration、有效域、尺寸和元素计数；没有 source hash、资格或映射不得猜当前最新值。Image2D/TilePyramid2D 的量测输入是原值或明确层级，不是 GPU/截图；HeightField3D/PointCloud3D/TriangleMesh3D 的孔洞、遮挡、未知 Z/法向保持未知，不填零、不封孔。坐标与单位由 coordinate Owner 转换，数学 XY、图像 row/column、屏幕 DIP、世界 XYZ 分开。

工作台只投影计量 Owner 的数量/单位/区间/有效性/支撑/不确定度。可显示真实零值；无量不建 QuantityProjection，不能 NaN、-1 或零替代 Missing。通用状态只有数值资格，没有 PASS/NG。参数 schema/range/default/单位/建议算法由工具/参数 Owner 给出；编辑和脚本调用同一校验入口，工作台不维护第二份约束。

## 4. 端到端流程、状态与重试

### 4.1 正常操作链

1. Host先由进程入口depot预留root槽，Factory绑定root后再Create预留有界session槽 得到 Created 会话；Attach 精确 Context，探测端口契约/能力并核 View 权限。源引用只绑定，不自动加载全图或执行。
2. 操作者选来源、工具、ROI 与参数草稿；以稳定 ID 保持树、主图、Inspector、结果行联动。每次确认编辑调用原 Owner；取消拖动不生成正式历史。
3. Execute 同步校验结构、当前 epoch/草稿、授权、Profile 和幂等记录，原子预留操作/请求/最大结果字节后返回 Accepted。后台依次核来源→坐标→ROI→参数→计量资格；失败不派发计量。
4. 准备的不可变引用与来源 scope 保留至下游退出。Metrology Start 返回受管理 job；job 内部持有 native child，Core 不接收 HALCON/窗口句柄。结果到达重新核授权、epoch、源/ROI/参数/工具绑定，旧代只记诊断并清理，不替换主图。
5. ResultAvailable 只表示结果可读；真实计量、呈现和证据 child 全退出并反序归还后才 ResourcesReleased，随后唯一 operation 终态。保存/导出是独立显式操作，不因完成量测自动写生产事实。

### 4.2 会话和 operation 分开

会话状态：Created → Attaching → Active；更换输入为 Active → Rebinding → Active；Close 为任何非 Closed → Closing → Closed。等待期限到而仍有工作/释放未知为 DrainUnknown，继续持 root/槽/任务，再次 Close 查询同一关闭过程。Attach失败的资源条件及Rebind恢复按A.4；重绑定失败保留旧上下文并标旧投影；关闭意图一旦建立不复开该实例。Editing/Busy/Stale 是 Snapshot 的投影，不是会话状态；多个独立操作不能把会话状态相互覆盖。

operation 顺序：Accepted → Preparing → Executing → ResultAvailable 或 LogicalFailed/CancelRequested → Draining → Drained → ResourcesReleased → Completed/Rejected/Cancelled/TimedOut/Failed/Unknown。无外部资源的拒绝也生成空 Drained/ResourcesReleased 记录；执行前未接纳的结构/预算拒绝仅返回错误，不创造操作。DrainUnknown/ReleaseUnknown **非终态**，额度、原任务、lease 与查询入口继续保留。Unknown 终态仅用于底层确已退出且资源已归还、业务保存/导出回执仍无法确认；不能表示 native 仍在跑。

CancellationToken 的含义由入口区分：Execute 请求的 execution cancellation 请求停止操作；Attach/WaitOperation/Drain/Close 的 waitCancellation 仅结束本次观察，不撤销已建立的生命周期意图。deadline 由注入 TimeProvider 的单调时间执行，不因系统 UTC 调整延长；UTC 仅诊断。撤权、换源、取消先撤回结果采纳资格，再请求停止。忽略取消的 backend 保持 DrainUnknown，不把 Task.WaitAsync 到期当退出。

### 4.3 幂等、重算与未知回执

同会话同 OperationId/AttemptId、同完整 payload（并复核 Canonical hash）重放原记录，不重新取得来源或 Start；任一字段不同为 IdentityConflict。每个已接纳 attempt 恰好一个终态事件；幂等记录满时拒新操作，不静默逐出 Unknown 或活动记录。显式新计算必须新 OperationId 和 AttemptId，并记录 Previous；SameInputs 复用原精确输入/参数/工具/坐标，原引用失效返回 StaleBinding，不转 latest。ExplicitInputs 完整给出替代引用，显示差异后执行；不提供自动刷新来源策略。

保存/导出回执 Unknown 不允许换 ID重发。ResolveMutation 只查询原 MutationRequest/原 hash，不能另建写入。对终态 Unknown 的后续回查只更新 ReconciliationReceipt 和投影，不再给原 attempt 第二个终态。适配器需保留原请求/查询权威；进程重启后恢复为只读，查询外部原 ID，不自动执行未完成工作。

### 4.4 编辑、联动和比较

ROI Begin/Apply/Undo/Redo 只转原模块 typed command 的不可变资产引用；IM-024 ProcessLocalEphemeral 首片没有持久 Commit，工作台不伪造 Committed。持久提交若未来有明确公开 Owner，另走它的 CAS/Query。工作台选择、镜头和参数编辑不是 ROI 历史；参数 Undo/Redo 只归 IM-062，文本编辑中 Ctrl+Z 只归文本编辑器。

跨 ROI+参数批量操作不许承诺原子：本版拒绝混合事务，要求分别确认并显示结果；同一 Owner 内批改使用其 Atomic 入口，失败不留一半。更换来源、工具、坐标或 schema 必须结束/取消未确认缓冲，生成新 epoch，旧草稿不偷偷重基。建议带源/ROI/参数/Profile/version/hash，采用前再次核精确基线，只改参数草稿，不自动执行或 Apply。

2D→3D 高亮/剖面和 3D→2D 回投携带 frame/revision、原采样索引、映射误差和 generation。没有有效公开映射为 NoMapping；插值点标 Interpolated，不能作为原样本计量。多层/孔洞剖面保留多个区间及 gap，不画连续线掩盖。比较仅匹配同 quantity key/candidate ID/单位/定义；域、输入或 Profile 不同列出 Differences，禁止合成误差合格或排名。Core 不重复计算计量差值公式，差值/区间由 ComparePort 原定义提供。

## 5. 线程、任务与资源生命周期

Core 不捕获 WPF SynchronizationContext；短锁只保护接纳/版本/事件，所有端口调用在锁外。授权 Check 为同步无 IO、不回入；其它端口返回可跟踪 job，不在 Start 内阻塞。端口不能靠等待 UI 回调完成 Core 状态变更。每个 job 从 Start 返回起由 root 强引用，后台 Task、CTS、资源预留与原 release Task 同槽登记；异常/取消/迟到仍归原槽，不遗弃 Task。

来源 StartAcquire 的 job 直到计量 child/viewport child 退出后才 Release；校准/ROI/参数读取 job 的结果深复制保留，只有确实无后续借用才释放。逆序是显示/证据 child→计量 job→参数/ROI/坐标 job→source job。ReleaseAsync 观察到期只停止等待；job 的 ReleaseUnknown 保留底层对象和原 release Task，再查询/等待该 Task，不再次无条件 Dispose。不使用 finally 中连续 Dispose 来假称清理完成。

| 资源/事实 | Owner 与归还条件 |
|---|---|
| source/Tile/mesh parent lease | 原 Owner；所有 metrology/viewport child 真实退出后归还，不以 UI 已隐藏代替 |
| native计量/渲染/GPU | 上游 Adapter；BackendReceipt 确认 Exited 且 Released；不跨 UI/序列化 |
| ROI/参数内存会话 | 原模块；工作台借用，不在 Unloaded/Close Dispose 宿主共享会话 |
| operation请求/结果/事件 | root/session；Profile 有界，Unknown/活动记录不得淘汰 |
| WPF control/surface/Dispatcher任务 | WPF根槽；原 Dispatcher Detach 回执完成后解除；Core关闭与UI卸载分别进行 |
| 注入 ports、TimeProvider | Host 借给 root；root不Dispose共享端口；Host等全部root/surface收尾再关闭它们 |

IAsyncDisposable 只是标准清理入口：用 Profile 的有限 CloseTimeout 观察同一关闭过程；仍有 pending 时抛 WorkbenchCleanupIncompleteException 并带 CloseReceipt，root/Host保留原实例。正常 Host 先明确 CloseAsync 并查 receipt；不能 using 离开后丢失未排空 root。恢复可查询旧 job、重试观察或隔离后端进程；没有进程级已验证退出证据不得强制把 native lease 归还。

订阅采用 pull 流，无同步 UI observer；每订阅独立有界队列。满时压缩为 SnapshotRequired、保存缺口序号并暂停增量，消费者 ReadSnapshot 后 AcknowledgeSnapshot；错误/终态不丢其权威记录，Query 始终可回取。慢消费者不回压计量，不分配无界队列。退订只排空自身读取，不能关闭会话；收到事件后查询仍核当前 View 权限。



## 6. 无 UI API 与空宿主接入

完整声明见附录 A；公开构造为 进程入口 WorkbenchRecoveryDepot.Reserve → MeasurementWorkbenchFactory() → CreateRoot(IRootReservation, RootOptions, WorkbenchPorts, TimeProvider) → root.Create(SessionOptions) → AttachAsync(Context,budget,waitToken) → SetDraft/Edit/Execute/QueryOperation/WaitOperationAsync → CloseAsync。构造不读配置、不建窗口、不调用 native；所有依赖在 WorkbenchPorts 一次显式注入。两个不同 root 或同 root 下两个 session 都不共享可变草稿、授权、取消源和语言。

端口方法 Start* 返回原 job，再通过 GetOutcomeAsync/Query/RequestCancel/ReleaseAsync 管理其实际生命周期。GetOutcomeAsync 等待 token 不取消后台工作。异步端口即使失败也先完成其已取得的资源登记；Start 要么返回可追踪 job，要么在无任务/资源/副作用时抛错，不允许“内部已启动但没返回 Owner”。端口可用底层原 Task 包装；不得假装普通取消 Task 即证明 native 已停止。

Core 公开编辑是 typed action + 对应 Owner 的不可变 command/snapshot 引用；真实宿主先通过该 Owner 的公开 API/Codec 生成、注册其内容，再传 AssetRef。引用不是自由字符串 payload：§8逐行限定 Contract、允许类型与回显内容，端口读取后核规范hash、version、base revision和完整内容。Core无权反序列化上游私有对象。未连接 capability 返回 Unsupported，不能悄悄保留一个按钮假成功。

## 7. 完整可嵌入工作台与专业交互

### 7.1 操作者、任务与构图

工程操作者连续完成“选源→选工具/域→看单位/参数/支撑→测量→检查候选/证据→显式重算/比较→保存或导出”；只读用户看原证据，授权用户编辑工程草稿。生产宿主可嵌入同一完整控件，生产身份/放行/设备命令仍在宿主。MeasurementWorkbenchControl 是一个模块级 UserControl，不创建产品 Shell、主菜单、全局主题、语言入口或数据库。

只用 1920×1080 屏幕基线，按实际任务栏、窗口边框、标题及状态栏计算客户区；不把 1920×1080 当内容区、不改显示设置。顶部身份32 DIP、主命令36 DIP、底部状态24 DIP、结果区初始96 DIP；左树160 DIP、右 Inspector280 DIP是初始布局值。中间**一个实际主 Surface**默认占可用工作区面积≥60%，专注模式≥80%，不把两个小图面积相加算主图；面积分母、DPI折算和确定折叠顺序见 A.11.5。2D/3D/剖面用主图页签/切换和有界关联预览，始终保留身份、执行/取消、单位/状态和主图；长英文不挤掉关键命令。

### 7.2 已核 DevExpress 25.2 组合

| 区域/任务 | 具体组合与行为 |
|---|---|
| 身份与主命令 | BarManager/BarButtonItem，常驻来源/工具/状态、执行、取消；PopupMenu仅次要动作，SuperTip解释前置/限制/恢复 |
| 面板与布局 | DockLayoutManager + LayoutPanel/DocumentPanel；身份/命令/主图不允许关闭，高级证据面板可隐藏；模块不创建宿主全局停靠体系 |
| 来源/ROI/工具树 | TreeListControl/TreeListView，稳定asset/node/tool ID，支持搜索、多选、锁和可见状态；隐藏不改变测量支持域 |
| 动态参数 | 嵌入 IM-062 ParameterEditorControl，同一个参数会话与工作台 port；其 PropertyGridControl schema缓冲/校验/Undo唯一权威，不另反射算法对象 |
| 候选/比较/证据 | GridControl + TableView，按 candidate/quantity稳定键；原值、单位、支撑、误差/不确定度、输入差异分别显示，无量为短横线和原因 |
| 剖面 | ChartControl + XYDiagram2D + LineSeries2D；ChartControlBase.CrosshairEnabled，按原样本索引联动，hole分系列断开，不生成伪连续观测 |
| 高级信息 | DevExpress.Xpf.Editors.Flyout.FlyoutControl、局部 PopupMenu/SuperTip，单位/来源/支持/拒识原因按需展开 |

不能以公开名称/截图证明模板、三语Popup、真实Surface、UIA或大图性能已通过。dock 的 SaveLayoutToStream/RestoreLayoutFromStream只读模块自有有界布局、固定panel白名单/版本/校验和；不载任意XAML/类型，restore失败回默认布局，不能影响测量内容。公开XML依据见§11。

### 7.3 输入与恢复

PointerTool 明确 Navigate、Select、DrawRoi、EditRoi、Profile；工具切换先结束或取消当前gesture。不把双击缩放放在Draw/Edit模式；中键临时导航释放后回原模式。拖动只向ROI Owner发Preview，松开/Enter才一次Apply；Esc、失焦、capture lost、撤权、换源或Detach取消当前Preview、归还capture，不提交半成品。点击多候选显示列表，不默选第一个。冻结gesture开始时的source/frame/epoch与参数解析culture，迟到结果不能切回旧对象。

Tab顺序：来源→工具→树→主Surface→Inspector→执行/取消→结果→证据。Ctrl+Enter执行当前合法草稿；Ctrl+Z/Ctrl+Y按焦点路由到文本、ROI或参数的各自历史；F5仅显式SameInputs重算，原输入失效提示重绑定；Esc先撤当前编辑/Flyout，无编辑时请求取消选定operation，不关闭整个Host。IME组合输入、单元格编辑和modal内不抢查看器快捷键；快捷键都有三语SuperTip。错误保留合法旧图/旧结果并标旧输入，告诉用户缺哪一项及可用恢复动作，不用空白区代替失败。

每个control/panel/tool/command/result有稳定AutomationIdPrefix+实例ID+稳定键；本地化Name/Role/Enabled/Busy/焦点状态。两实例prefix不同；浮动panel、Popup、SuperTip、上下文菜单、Chart tooltip必须同呈现修订。UIA查询以真实控件/焦点/命令状态断言，截图只验证视觉。

### 7.4 挂载、局部三语与实际Surface

附录 A.7给无参control、Mount/SetPresentation/Detach与surface/inspector公开桥。Host先在有限root槽登记control/session/原Mount Task；surface provider必须返回**实际UIElement实例**和该实例的binding/cleanup Owner，不能返回截图或“绑定已完成”布尔量。viewport桥用原IViewportControlBinding.BindAsync(session, processRoot, options)，OwnSession=false；参数桥用原ParameterEditorControl.Attach，二者借用Host已构造的会话，禁止借全局“当前视口”。挂载失败已启动的迟到child仍进入原UI槽清理。

ResourceCulture为zh-CN/zh-TW/en-US并可扩展；FormatCulture与持久编码分开。SetPresentation只改变实例资源/主题/显示格式，不写CurrentCulture/全局ThemeManager/在途Profile。保留IME token、selection及启动编辑culture，确认/取消后再换格式，不能将1,5重解成15。宿主提供文本资源接口，模块随包提供三语默认资源并可被宿主覆盖；缺资源按en-US→短中性标签回退并诊断，不显示内部key。

Unloaded只请求Detach，不代表已释放。Detach关闭UI接纳→退订→取消gesture/投影→原Dispatcher清除图/overlay/菜单引用→等待render/Dispatcher/popup回调真实退出→按child逆序归还→Detached+Drained。Dispatcher不可用、cleanup失败、token到期时保留原槽、control、surface与Task，报告UiCleanupUnknown；不得后台伪造UI ACK，不重复Mount到另一窗口。Host仍需单独Close Core，所有原UI任务/root都排空后才关闭Dispatcher。UI Root的RequestClose/Observe汇总其slot，不能在当前cleanup任务中等待自己。

## 8. 上游公开映射、能力与视觉路线

### 8.1 精确公开消费范围

以下指向已读的唯一公开指导；A1映射不复制DTO/算法，真实公共程序集尚须消费工程编译。前置不满足只隔离该映射/工具，C1/C2内存端口仍可验证。

| 工作台内容/端口 | 公开Owner与固定映射 | 不得宣称的范围 |
|---|---|---|
| RoiSnapshot/Command | IM-024 v0.3，namespace Asun.Modules.RoiGeometry；IRoiGeometryFactory.Open、IRoiGeometryCore.Query/Validate/Apply/PreviewAsync/QueryOperation/DrainAsync；command资产仅RoiEditRequest，Mode/expected revision/profile/deadline逐字段核 | 首片无持久Commit；Interaction/Codec/Spatial资格独立，不调用未定义接口 |
| ParameterSnapshot/EditBatch/建议 | IM-062 v0.2，namespace Asun.Modules.ParameterEditor；ParameterEditorFactory.Create/Restore，session.Read/CheckEdits/SetValues/Undo/Redo/RecommendAsync/AcceptSuggestion/ExportCheckpoint；command资产仅EditBatch或其原RecommendationRequest | 参数事实/校验/Undo不在工作台重写；不得把工程建议自动RequestApply |
| 离散量测 | IM-036 §11–16，Asun.Metrology.Contracts v0.2；IMetrologyService.Validate/MeasureAsync/GetOperation/RequestCancel；每工具冻结MethodProfile/Definition及operand Role，request.Key映射本operation的固定key | 不能仅enum路由；图像Arc/Ellipse等受上游当前Unsupported限制 |
| 连续量测 | IM-036 §19 v0.3；IContinuousMetrologyService同类入口；ContinuousRequest/Profile/Payload/Report case一一配对 | 不把v0.2扩enum冒充0.3；SupportedField材料/未知域由原Owner提供，工作台不分类、不重建 |
| 显示/拾取 | IM-060 v0.1，IViewportFactory/IViewportSession.AttachAsync/UpdateAsync/ApplyAsync/ProbeAsync/DisposeAsync(timeout,ct)，纯操作IViewportPureOperations；UI原ViewportControl + IViewportControlBinding | parent/child/source/Required资源Owner不能丢；UI owner接管不等Drained |
| source/coordinate | 原image-frame、surface-data、coordinate公开Contract绑定至本页SourceBinding/CoordinateBinding；校验frame/单位/域/源hash逐值回显 | Tile只显示；未知3D/多源变换/材料资格不从图像猜 |
| store/evidence/compare | 外部Owner实现本页端口；内存夹具仅工程引用/草稿/差异 | 不写产品库、质量事实、设备、报告批准；没有现实第二产品接入证据 |

计量v0.2的AssetRef没有OwnerId，Adapter用固定公开Owner路由并映射Id/revision/hash；不能剥掉工作台Owner后在未知全局registry找对象。上游 OperationKey 是 OperationId+RequestRevision；工作台 Key.Operation.Value 映射 OperationId，RequestRevision 固定1；AttemptId仅为工作台关联身份且与OperationId双射，不重写同 key。v0.2 source单通道图像当前仅Byte量测，其UInt16/Float32内容可显示但相应图像测量Unsupported。ROI像素X=column,Y=row；metrology D2物理X右/Y上、图像row下；显式Mapping完成手性/单位，rad和mm/mm²/mm³原样保存，3D HALCON内部meter转换只由计量Adapter做。

计量返回GetOperation.phase为DrainUnknown/ReleaseUnknown时，等待返回的逻辑结果只投影停止原因；job不得自报Exited/Released。上游lease/GetReceipt/CloseReceipt与本页 JobReceipt逐项映射，不把Close返回bool代替各个原operation真实排空；共享服务不按工作台单操作取消关闭整服务。IM-036连续C1–C4规格已接收不是运行结果；不沿用旧“全部三维缺合同”判断。

### 8.2 能力与版本

Probe返回模块/build/Contract及具体ToolDescriptor，明确2D/3D/Tile/剖面/原样本/参数建议/导出/持久查询能力和限额。ToolDescriptor包含实际Profile/Schema/定义、允许SourceKind/必需operand，输入层级固定在Plan.SourceBinding；不只一个Supported=true。缺能力命令可见禁用并短说明；用户只能显式选择另一个定义，不能偷降级改变原结果。

Context/执行绑定Core+Adapter+上游Contract+工具Profile+源/坐标/ROI/参数+证据hash。更换version须排空后建新session；未知版本只读展示保存元数据，不能执行。回滚整个匹配包组合，旧证据保持旧版本；迁移本版仅支持同Contract冷读取；未知版本只读元数据，缺源/无法映射的Checkpoint只读，不自动填值。

### 8.3 HALCON消费约束与方法说明

计量Owner选择路线，工作台只呈现要求/参数来源及拒识，不调用另一个HOperatorSet或自算同名方法。非视觉事务/授权/存储不适用HALCON。已读26.05原页形成这些消费约束：

- measure_pos/gen_measure_rectangle2：Image domain不代搜索ROI；半轴、row/column、Sigma与边界余量显式，Threshold的Byte范围不套UInt16/real；边/距离tuple数量分别处理。
- apply_metrology_model/get_metrology_object_result：多instance顺序不是质量排名，选择Unique/All/显式anchor；修改同model handle须由Owner串行，不由UI复用可变模型。
- fit_circle_contour_xld/fit_primitives_object_model_3d：输入先是一个候选结构；算子不自动分割，不把all误作全类型返回。算法最低样本数不证明覆盖/精度；3D plane Tukey不能宣称稳健效果，按上游支持表拒绝。
- area_center/fit_surface_first_order：空域或零面积需有效性原因；ROI/Regions显式，不靠Image domain限制fit；像素面积不直接贴mm²。
- intersect_plane_object_model_3d/triangulate_object_model_3d：截面采用7元素pose的局部xy面，保多层/洞/原face；不把Hessian四数当pose，不默认封洞。
- volume_object_model_3d_relative_to_plane：mesh/face方向、pose/mode由计量定义冻结；最终累计绝对值，signed选项不表示输出一定带符号。工作台显示上游VolumeEvidence/连续IntegralReport的正、负幅值/净量，不自己推号。

这些是语义研究，不是实测算子/Golden或最快路线证据。候选ROI粗精、参数建议和同样本P50/P95/P99由原视觉Owner按DEV-VIS-021比较；工作台记录路由/拒识/引用，不再做一份算法库。

## 9. 两消费者、反例与Benchmark

### 9.1 独立Host

H1 EngineeringReplayHost是无UI/生产库/设备的CLI，在Core.Tests具名夹具构造所有端口，从Attach→编辑→Execute→Query→比较→保存/恢复→Close。H2 EmbeddedWorkbenchHost使用独立组合类与不同source/Profile/授权/store，CLI先验证同一API；桌面TestHost再嵌入完整control与两个不同Dispatcher/窗口绑定，验证同进程双实例和独立主题/语言/关闭。不以两个harness名称证明第二现场产品，实际外部视觉项目接入仍是后续真实消费者门。

附录 A.8给完整双无UI/双STA构造与有限观察，端口夹具行为表有固定断言。Host禁止使用全局ServiceProvider/静态当前图像、将正在清理的session丢进using、在finally吞DrainUnknown。桌面两Host按A.7使用 MeasurementWorkbenchControl.MountAsync 并登记 UI 槽，原 Viewport/Parameter 会话由各 Host 显式构造；未定义上游真实源桥只阻断A2/U1相应scope，不阻断纯Core夹具。

### 9.2 必需断言

| ID | 输入/反例 → 可判定结果 |
|---|---|
| T01 | Empty source/default数组/错hash/错revision/未知tool/超限 → 接纳前拒绝或准备拒绝；零计量Start，不填latest |
| T02 | (column,row)到物理右手XY、mm/µm/rad及大/小有限数 → 正确Owner映射并回显；奇异/未知calibration阻断，不改标签冒换算 |
| T03 | ROI创建/预览/取消/Undo/Redo、最后一项非法的Atomic、CAS旧revision → 原Owner单次变更/原子拒绝；混ROI参数批改直接拒绝 |
| T04 | 合法参数/范围错/建议基线已变/IME/多字段批改 → 同PE校验；Stale建议不采用，不自动执行/Apply |
| T05 | 弱边/遮挡/退化/多候选/不确定度缺分量 → 原Validity/支撑/错误完整；不得第一候选、零量或PASS |
| T06 | SameInputs/ExplicitInputs与旧源不可取 → 前者精确相同或Stale；后者显示所有差异；比较不同定义/单位拒绝，不造差值 |
| T07 | 孔洞、多层、未知高度、2D→3D无映射、插值probe → gap/多区间/NoMapping/Interpolated保留，不封孔/不转原样本 |
| T08 | Profile容量N/N+1、响应/资产超byte预算 → N接纳，N+1零派发；逻辑/managed/native/GPU各额度不混；大图不拷全图 |
| T09 | A/B两个session、撤权、旧epoch迟到结果 → B正常；A禁止披露/采用，旧结果只清理；取消A不关闭B共享服务 |
| T10 | 同ID同完整payload/异payload、Unknown save/export、回执晚到 → 只Start一次/IdentityConflict/仅原请求Query；唯一终态、不自动换ID重发 |
| T11 | deadline/忽略取消/断连/Release失败/Acquire晚到/Close等待取消 → 保原Task/资源/槽，DrainUnknown或ReleaseUnknown非终态；恢复后顺序Drained→ResourcesReleased→终态恰一次 |
| T12 | 推荐同输入重复/无可行候选/版本变更 → 确定性引用/拒识原因；人工采用只改草稿；冻结前后建议与生产值分开 |
| T13 | 冷读取Checkpoint、缺资产/错schema/旧operation/迁移失败 → 只读恢复/Stale/Unknown；不恢复授权/期限/lease、不重跑 |
| T14 | 真实WPF1920×1080、三语长字、键盘/IME/capture lost/UIA、Dispatcher关闭/晚Mount → 比例/可达/状态断言；UIcleanup未知保槽，不伪Detached/Drained |
| T15 | 慢订阅/满队列/退订、端口非法回入、同root两个Host/shared pool → SnapshotRequired+回取，有限内存；无UI等待环/自清理等待，独立root额度和原Owner计账 |

纯Core测试工程按DEV-GOV-010 §3.1：Microsoft.NET.Sdk / net10.0 / OutputType=Exe，只BCL和受测工程；固定时钟、确定断言、异步闩锁。执行dotnet build指定Core.csproj -c Release；dotnet run --project指定Core.Tests.csproj -c Release。必须执行绑定切片所有T编号/子反例，失败、未完成或必需跳过非零；dotnet test不能替代Exe。真实WPF/AsunImage/性能/HIL另验，本轮未创建或运行这些工程。

### 9.3 可执行BenchmarkProfile

附录 A.9的BenchmarkPlan是Host输入。统计唯一遵循DEV-GOV-010 §3.1，不复制分位算法。工作负载至少冻结源种类/hash、width/height/points/faces、ROI数量/顶点/孔、工具/参数Schema、候选/结果条数、Tile尺寸/level、交互模式、session/operation并发、subscriber数/读取速率、save/export字节、版本包/CPU/GPU/OS及冷/热/预热/采样计划。

测点：接纳、准备每port、source借用、计量Start/逻辑结果、停止采纳、请求取消、backend真实退出、UI最后呈现ACK、证据回执、每lease归还、ResourcesReleased和唯一终态。端到端从Accepted到ResourcesReleased；取消分别到真实退出/归还。计managed/native/GPU峰值、root逻辑预留、source/child lease数、队列/事件/Dispatcher积压；只测算法内核或截图帧率不能替代。

失败/拒识/取消/超时/未完成/删失/DrainUnknown/ReleaseUnknown逐项列出，不能删掉慢样本；无实际target或外部门未通过为NotEvaluated。执行上限与软件fixture值不是客户节拍/精度资格。性能目标、长稳时长、真实样本与Golden来自已采纳消费者Profile，缺失不编造，仍可做诊断测量。

## 10. 本轮准入结论与自审

### 10.1 逐切片六项

主控于2026-10-11接收的基线为0.5.0-prep / Module API Contract v0.3，定向回读A.1–A.9及下表六项后，C1/C2六项文档规格为 **ModuleCoreImplementationReady**。0.6.1完成A.10参数表示规则及工程receipt；当前0.7.0补齐全部已批准模块范围的可决定软件设计，准确结论与映射见A.11.8。已接收Core/API/编码/Host、A1原A.6公开映射、U1公开装配与Owner恢复指导接收保持。A1/U1未获得实际运行资格，U1不属于纯Core准入；整模块集成/运行仍为PreparationIncomplete / NotReady，未获得生产准入。

| DEV-GOV-010 §3.1项 | C1 | C2 | A1/U1后续 |
|---|---|---|---|
| 1 边界/第二消费者 | §1–3/9.1 | 同前，草稿不写生产事实 | 独立控件与公开Owner，§7/8 |
| 2 唯一完整API/单位/错误/版本/资源 | A.1–A.5/A.9、§3–5 | A.2–A.6/A.9、§4/8 | A.7与§8映射；实际消费程序集另验 |
| 3 无UI显式Host | A.8两种组合根、有限Close | 同Host的编辑/比较/存储链 | UI实际child/Dispatcher/root接线按A.7 |
| 4 正常/反例/生命周期 | T01/T02/T08–T11/T15 | T03–T07/T10/T12/T13 | T14及真实Golden/lease |
| 5 Benchmark | §9.3/A.9；未采纳目标NotEvaluated | 同前含恢复/保存/比较 | GPU/UI/真实计量目标另采纳 |
| 6 工程/测试/允许禁止/最小顺序 | §3.1/6/A.8/9.2 | 同一工程分切片，不新建权威 | §3.1对应独立层；共享整合由主会话 |

主控已按独立字段重建A.9 Execute的1098 bytes，完整hex/SHA-256与本页向量一致；A.8两无UI Host、原DispatcherOperation/inner Task双登记、双STA独立root及Proof移交定向回读一致。本次接收关闭C1/C2六项文档规格准入，不代表实现或验证完成。A.10/A.11已明确本模块软件映射、WPF PageContract、推荐/比较/导出及验证计划，不再将这些已冻结设计整项列为欠账。整模块ImplementationSpecificationReady仍按受影响范围核实际上游程序集消费、真实来源/资源回执、WPF/Golden/Replay、已采纳消费者Profile与性能；客户物理真值、精度/公差/吞吐/现场验收只阻断依赖它们的范围，不阻断C1/C2。实际build/run、真实WPF/算法Golden/性能/现场未验；本次文档修订不触发产品实现或全审。

### 10.2 两轮自审范围

第一轮按工程操作者走载入、选源/工具、ROI/参数、建议、计量、歧义/孔洞、重算比较、证据、恢复；以T01–T08/T12–T14逐条反例查输入/状态/恢复。第二轮脱离辅助文件按空Host构造、端口原Task移交、同ID回放、撤权迟到、慢订阅、关闭/Release失败、两实例/Dispatcher/版本退回，查A.1–A.9字段/顺序与T09–T11/T15。两轮已完成：修正了缺声明/引用状态、薄Source→完整Owner Contract推断、Root离栈无强持、host自清理等待、STA async void/外层任务提前完成、双Dispatcher同窗并发及异常转交、同请求重放及无权读投影；定向检查仅本页链接/标题/围栏/类型/调用和A.9完整Golden。Golden独立逐字段解码1098 bytes及SHA-256一致，只证明规范字节，不是产品运行；未运行全仓校验/产品代码测试。

### 10.3 主会话串行事项

主会话已完成上述0.5.0范围的定向接收；入口/进度/模块索引/OPEN-GATES由主会话串行同步。本原会话完成0.7.0全批准范围的执行、内容审核、修复与文档验证，只交本指导结论，不等待总控内容复核。真实源/native lease、完整域/参考证据的真实性、现实Store目的地和外部产品交接仍按受影响A2运行/产品门；真实计量/Viewport/Parameter UI及产品验证另验。不修改共享文件或发消息。

## 11. 研究依据、采纳与局限

- [ROI唯一指导](../roi-geometry/DEVELOPMENT-GUIDE.md)、[计量唯一指导](../metrology/DEVELOPMENT-GUIDE.md)、[视口唯一指导](../viewport/DEVELOPMENT-GUIDE.md)、[参数编辑器唯一指导](../parameter-editor/DEVELOPMENT-GUIDE.md)：§8映射以2026-10-10定向读取的公开契约为准。
- [DEV-GOV-005](../../01-governance/DEV-GOV-005_模块独立性与复用标准.md)、[DEV-GOV-010](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)：独立边界与唯一六项/统计/Exe测试标准。
- [DEV-VIS-020](<../../shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md>)、[DEV-VIS-021](../../shared-modules/guidance/03-vision/DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md)、[DEV-UI-040](<../../shared-modules/guidance/05-ui/DEV-UI-040_WPF+DevExpress Design System开发指导.md>)、[DEV-UI-041](../../shared-modules/guidance/05-ui/DEV-UI-041_高保真PageContract与工作台开发指导.md)：视觉Owner与工作台UI/语言规范。
- HALCON26.05本地原件：[measure_pos](../../../halcon算子手册/operators/measure_pos.html)、[gen_measure_rectangle2](../../../halcon算子手册/operators/gen_measure_rectangle2.html)、[apply_metrology_model](../../../halcon算子手册/operators/apply_metrology_model.html)、[get_metrology_object_result](../../../halcon算子手册/operators/get_metrology_object_result.html)、[fit_circle_contour_xld](../../../halcon算子手册/operators/fit_circle_contour_xld.html)、[area_center](../../../halcon算子手册/operators/area_center.html)、[fit_surface_first_order](../../../halcon算子手册/operators/fit_surface_first_order.html)、[fit_primitives_object_model_3d](../../../halcon算子手册/operators/fit_primitives_object_model_3d.html)、[intersect_plane_object_model_3d](../../../halcon算子手册/operators/intersect_plane_object_model_3d.html)、[triangulate_object_model_3d](../../../halcon算子手册/operators/triangulate_object_model_3d.html)、[volume_object_model_3d_relative_to_plane](../../../halcon算子手册/operators/volume_object_model_3d_relative_to_plane.html)。实际已读语义采纳在§8.3，未执行算子/实测比较。
- DevExpress官方25.2随附公共XML：C:/Program Files/DevExpress 25.2/Components/Bin/NetCore；Docking SHA256 b11b45dd7afc27b5e16b679a6a9e2e4291ecd13cb1f8e1b7c0fbe4e94a64477f，Grid 7537e3db16162155eda70058baccf40a6731f6dc9851ad31d382332c39c3d6bd，PropertyGrid 0e0cb8a0503889f13cd86fa4d5db7cbb975c9c4f4506dfea8d681f68fc4a65c9，Charts 2e80660ea0316294482e5b45096cc23c52250243e12551e84c117f692445bfb0，Core cf99d297b336a80f2361fa8bb79369434a6a10b9426efa670d636803433e8196。官网403且本会话无dxdocs；采用实际已读成员，未证实成员不猜。
- napari v0.6.6的实际commit 59ea1849d144e53cc9d42826139f545937b3eb91：[viewer_model源码](https://github.com/napari/napari/blob/59ea1849d144e53cc9d42826139f545937b3eb91/src/napari/components/viewer_model.py)、[对应测试](https://github.com/napari/napari/blob/59ea1849d144e53cc9d42826139f545937b3eb91/src/napari/components/_tests/test_viewer_model.py)、[鼠标源码](https://github.com/napari/napari/blob/59ea1849d144e53cc9d42826139f545937b3eb91/src/napari/components/_viewer_mouse_bindings.py)、[鼠标测试](https://github.com/napari/napari/blob/59ea1849d144e53cc9d42826139f545937b3eb91/src/napari/components/_tests/test_viewer_mouse_bindings.py)。实际读过空/单点3D、mix_dims、活动层/选择隔离、非导航模式双击不缩放等源码/断言，采纳gesture/稳定选择/相机与数据分离，不采全局settings主题或新图层抢选择。BSD-3-Clause；LICENSE hash f1d02529b3aa4cc61ef4bfa02ff904c795ebd5277401b696403524a623a9def2；pyproject hash c59b262da7d66a95922fe49125c3f728d83b42ab1bce666db05e642c6abe0622。Python≥3.10、numpy≥1.24.2、QtPy≥2.3.1、vispy≥0.15.2且<0.16及dask/pydantic/psygnal/plugin栈仅作研究，不引入C#运行依赖；未运行其测试，不证明工业精度/授权/lease。未成功读Helix源码，不列为已完成证据。
- 微软官方[协作取消](https://learn.microsoft.com/dotnet/standard/threading/cancellation-in-managed-threads)、[WPF线程模型](https://learn.microsoft.com/dotnet/desktop/wpf/advanced/threading-model)：取消≠实际退出，Dispatcher不用Task.Wait/Result形成等待环。




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

## 附录 A：Module API Contract v0.3（唯一公开声明）

0.4.0 暂停稿中只有文字而无声明的接口、自由字符串状态、未绑定的 helper 和 Host 顺序由本附录替代。没有已经发布的 v0.2 实现；此处是目标公开签名，省略类实现体，不是可编译代码交付。Core 的统一 namespace 为 Asun.Modules.MeasurementWorkbench，引用 System、System.Collections.Immutable、System.Threading、System.Threading.Tasks；WPF/上游类型只允许各自可选 DLL。

### A.1 输入、版本、单位、域与有界政策

~~~csharp
public readonly record struct WorkbenchSessionId(Guid Value);
public readonly record struct OperationId(Guid Value);
public readonly record struct AttemptId(Guid Value);
public readonly record struct Epoch(long Value);
public readonly record struct Sequence(ulong Value);
public readonly record struct OperationKey(OperationId Operation, AttemptId Attempt);
public readonly record struct AssetRef(string Owner, string Id, ulong Revision, string Sha256);
public readonly record struct ContractRef(string Name, string Version);
public enum SourceKind { Geometry, Image2D, RegionRuns2D, Contours2D, TilePyramid2D,
    HeightField3D, PointCloud3D, TriangleMesh3D, ContinuousField3D }
public enum UnitCode { Pixel, Pixel2, Mm, Mm2, Mm3, Mm4, Rad, Ratio }
public enum AxisConvention { ColumnRowPixelCenters, RightHandedXY, RightHandedXYZ }
public enum SamplingKind { Original, ExplicitLevel, InterpolatedDiagnostic }
public enum SupportStatus { NotProvided, Partial, Complete }
public enum SessionMode { EngineeringEditable, EvidenceReadOnly }
public enum MeasurementContract { Replay, Metrology02, Continuous03 }
public enum MeasureScope { Engineering, CalibratedPhysical, PixelDiagnostic }
public enum WorkbenchSessionState { Created, Attaching, Active, Rebinding, Closing, DrainUnknown, Closed }
public enum OperationPhase { Accepted, Preparing, Executing, ResultAvailable, LogicalFailed,
    CancelRequested, Draining, DrainUnknown, Drained, ReleaseUnknown, ResourcesReleased,
    Completed, Rejected, Cancelled, TimedOut, Failed, Unknown }
public enum OperationOutcome { Measured, Partial, Unevaluated, InvalidInput, Unsupported,
    Unqualified, Cancelled, TimedOut, ResourceLimited, Failed, Unknown }
public enum ValueValidity { Valid, Invalid, Indeterminate }
public enum RecomputePolicy { SameInputs, ExplicitInputs }
public enum CancelReason { User, Deadline, AuthorizationRevoked, Rebinding, Closing }
public enum AuthorizationAction { View, EditRoi, EditParameters, Execute, Save, Export, Compare }
public enum WorkbenchErrorCode { InvalidRequest, IdentityConflict, StaleBinding, Unauthorized,
    Unsupported, InputUnavailable, InputHashMismatch, CoordinateMismatch, VersionMismatch,
    BudgetExceeded, DeadlineExceeded, Cancelled, BackendFailure, PersistenceFailure,
    DrainUnknown, ReleaseUnknown, CleanupUnknown, NotFound }

public sealed record CoordinateRef(AssetRef Frame, UnitCode Unit, AxisConvention Axes,
    AssetRef? Calibration);
public sealed record SupportDomainRef(SupportStatus Status, AssetRef? DesignDomain,
    AssetRef? DataDomain, AssetRef? ObservedDomain, AssetRef? Qualification);
public sealed record SourceBinding(string OperandId, string Role, AssetRef Content,
    ContractRef ContentContract, SourceKind Kind, CoordinateRef Coordinates,
    SupportDomainRef Support, int Width, int Height, long Elements,
    SamplingKind Sampling, int Level, double ScaleX, double ScaleY,
    double? PositionErrorBound, AssetRef? SamplingReceipt);
public sealed record CoordinateBinding(AssetRef SourceFrame, AssetRef TargetFrame,
    AssetRef Mapping, AssetRef? Calibration, AssetRef? ApplicabilityReceipt,
    UnitCode TargetUnit, AxisConvention TargetAxes);
public sealed record GeometryAsset(AssetRef Snapshot, ContractRef Contract,
    string RoiSessionId, string DocumentId, long Revision, long OwnerEpoch,
    string ProfileRevision, CoordinateRef Coordinates,
    SupportDomainRef Support);
public sealed record ParameterAsset(AssetRef Schema, AssetRef Snapshot, ContractRef Contract,
    Guid EditorSessionId, long Generation);
public sealed record ToolDescriptor(string ToolId, string ToolVersion,
    MeasurementContract MeasurementContract, AssetRef MethodProfile,
    ContractRef ProfileContract, ImmutableArray<SourceKind> AllowedSources,
    ImmutableArray<string> OperandIds, AssetRef? ParameterSchema,
    int MaximumCandidates, string NameResourceKey, string HelpResourceKey);
public sealed record MeasurementPlan(ToolDescriptor Tool, AssetRef RequestTemplate,
    ContractRef RequestContract, OperationKey TemplateKey,
    ImmutableArray<SourceBinding> Inputs, CoordinateBinding Coordinates,
    GeometryAsset? Roi, ParameterAsset? Parameters, AssetRef? ParameterProfileBinding);
public sealed record WorkbenchContext(WorkbenchSessionId SessionId,
    ImmutableArray<SourceBinding> Sources, CoordinateRef PrimaryFrame,
    string AuthorizationRevision, ImmutableArray<ContractRef> Dependencies);
public sealed record MeasurementDraft(long Revision, MeasurementPlan Plan, string DraftHash);
public sealed record WorkbenchCapabilities(string ModuleVersion, string AdapterVersion,
    ImmutableArray<ToolDescriptor> Tools, bool RoiEdit, bool ParameterEdit,
    bool Recommendations, bool ViewportLink, bool Checkpoint, bool Export);

public sealed record ResourceProfile(string ProfileId, ulong Revision,
    int MaxSources, int MaxRoiNodes, int MaxParameters, int MaxResults,
    int MaxOperations, int MaxConcurrentOperations, int MaxSubscriptions,
    int MaxNotificationsPerSubscription, int MaxStringsUtf8Bytes,
    long MaxRequestBytes, long MaxResultBytes, long MaxRetainedBytes,
    long MaxManagedBytes, long MaxNativeBytes, long MaxGpuBytes,
    int MaxTrackedJobs, TimeSpan OperationTimeout, TimeSpan CloseTimeout);
public sealed record RootOptions(string RootId, string ConsumerId, int MaxSessions,
    ResourceProfile Profile);
public sealed record SessionOptions(WorkbenchSessionId SessionId, SessionMode Mode);
public sealed record CallContext(WorkbenchSessionId SessionId, OperationKey Key,
    Epoch Epoch, string RequestHash, ResourceProfile Profile,
    TimeSpan RemainingBudget, string AuthorizationRevision);
public sealed record AuthorizationQuery(WorkbenchSessionId SessionId,
    AuthorizationAction Action, ImmutableArray<AssetRef> Resources, Epoch Epoch);
public sealed record AuthorizationDecision(bool Allowed, DateTimeOffset ValidUntilUtc,
    string Revision, CancellationToken Invalidated, WorkbenchError? Error);
public interface IWorkbenchAuthorizationPort {
    AuthorizationDecision Check(AuthorizationQuery query);
}
~~~

AssetRef 的 Owner/Id 为非空 NFC、Ordinal；revision≥1，SHA-256为64位小写hex。上游允许revision=0时不得偷偷+1：§A.6的专门桥以资产登记revision≥1、正文保留原上游revision=0，二者各司其职。Guid不为Empty；Epoch、草稿代次≥0，checked递增且不回绕。无效/未知enum、default ImmutableArray、重复身份、非有限数、孤立surrogate拒绝；构造record并不等于校验成功。所有响应重新有界深冻结，纯内存集合不允许IO枚举器。

SourceBinding 覆盖 Geometry、RegionRuns/Contours 和连续场，不能把这几种原料伪标为Image/mesh。Role是上游固定枚举名称或连续输入固定名 Input，大小写敏感；同源可有多个不同OperandId，各绑定保留原顺序，不按source去重删operand。图像Width/Height>0；非图像尺寸为0，Elements≥0。Original要求Level=0、ScaleX=ScaleY=1、SamplingReceipt=null；ExplicitLevel要求level≥0、有限scale>0及原Owner回执；InterpolatedDiagnostic不能执行CalibratedPhysical或完整原样本测量。PositionErrorBound可空，非空有限≥0、与CoordinateRef.Unit同单位，不从比例自行推误差。

SupportStatus.NotProvided四引用必须null；Partial/Complete前三域非null且同frame/unit，Complete须原Qualification证明D=V，不相信调用方bool。ROI Domain为IM-024三域；离散计量Support.Complete只是本候选支撑完备，不能升级为整输入D=V；连续域D/F/B/Us/Uh/E/U保在原SupportedField，工作台不把多域压成一个“有效百分比”。缺覆盖或资格只阻依赖其整量/物理资格的工具；几何工程诊断可运行并保持原Scope/Validity。坐标/单位缺失不得推断；数学坐标、row/column、DIP及XYZ不混用。

PrimaryFrame是显示主身份，计算使用Plan.Coordinates的明确Source/Target/Mapping。mm/µm与degree/rad转换由原Owner/§A.6具名桥完成；Core不计算单位系数。字段不允许自由“Unit string”、ValiditySummary、SupportSummary或自动latest代替事实。

Profile所有计数/bytes/timeout正数，MaxGpuBytes/MaxNativeBytes允许0仅表示禁止该资源；MaxConcurrentOperations≤MaxOperations，MaxTrackedJobs≥(MaxSources+4)×MaxConcurrentOperations+MaxSessions+1。每次操作最坏预留MaxSources个source job、坐标/校验/计量3个job和1个worker槽；root还预留每session关闭、1个root关闭，不能普通工作吃完cleanup容量。MaxRetainedBytes至少能容纳一次MaxRequestBytes+MaxResultBytes预留；满足代数不等于实际性能通过。字符串上限按每个UTF-8字节，max source/ROI/parameter/results按完整内容而非可见项。MaxOperations含所有已接纳历史和未决记录，满即拒新key，不自动逐出。MaxRetainedBytes涵盖请求/结果/错误/事件/未知job与引用载荷逻辑大小；原Owner计实际managed/native/GPU backing，不双扣共享池。未决job/释放/迟到Acquire仍占额度。

Check在锁外同步无IO、不回入；端口由Host绑定身份，Context.AuthorizationRevision不是凭证。每次读取、派发、采纳、编辑、比较/导出重核当前Check与Invalidated/ValidUntilUtc，撤权取消原执行资格及Disclosure。TimeProvider管理单调累计期限，UTC仅用于权限期限和诊断；接受期限取请求OperationTimeout与Profile上限较小值，排队/所有阶段共用剩余时间，不每port重置。全部Native/存储入口另核当前权限，Core授权不证明远端原子性。

### A.2 结果与正交资源状态

~~~csharp
public sealed record WorkbenchError(WorkbenchErrorCode Code, string MessageKey,
    ImmutableArray<KeyValuePair<string,string>> Arguments, string RecoveryKey);
public sealed record WbResult<T>(bool Succeeded, T? Value,
    ImmutableArray<WorkbenchError> Errors) where T : class;
public enum JobPhase { Running, ExitUnknown, Exited, ReleaseUnknown, Released }
public sealed record JobReceipt(string JobId, JobPhase Phase,
    bool CancelRequested, ImmutableArray<WorkbenchError> Errors);
public interface IWorkbenchJob<T> where T : class {
    string JobId { get; }
    ValueTask<WbResult<T>> GetOutcomeAsync(CancellationToken waitCancellation);
    JobReceipt Query();
    void RequestCancel();
    ValueTask<JobReceipt> ReleaseAsync(TimeSpan observationBudget,
        CancellationToken waitCancellation);
}
public abstract record MeasureValue;
public sealed record ScalarValue(double Value) : MeasureValue;
public sealed record IntervalValue(double Lower, double Upper) : MeasureValue;
public enum UncertaintyStatus { NotProvided, NotEvaluable, Propagated }
public sealed record UncertaintyProjection(UncertaintyStatus Status,
    double? Standard, double? Expanded, double? Factor, double? Probability,
    AssetRef? Model, ImmutableArray<string> MissingComponents);
public sealed record QuantityProjection(string CandidateId, string Key,
    MeasureValue? Value, UnitCode Unit, ValueValidity Validity,
    AssetRef? Support, UncertaintyProjection? Uncertainty, string? ReasonKey);
public sealed record MeasurementResult(OperationKey Key, OperationOutcome Outcome,
    ValueValidity Validity, MeasureScope Scope, ImmutableArray<QuantityProjection> Quantities,
    AssetRef OriginalResult, ImmutableArray<AssetRef> Evidence, string ResultFingerprint);
public sealed record OperationSnapshot(OperationKey Key, OperationPhase Phase,
    OperationOutcome? PendingOutcome, OperationPayload? Result,
    WorkbenchError? Error, bool DisclosureAllowed, bool ResourcesReleased, ImmutableArray<JobReceipt> Jobs);
public sealed record ReconciliationReceipt(OperationKey OriginalKey, MutationReceipt ResolvedReceipt);
public sealed record MutationSnapshot(OperationKey Key, MutationState State,
    MutationReceipt? Receipt, ReconciliationReceipt? Reconciliation, bool ResourcesReleased, ImmutableArray<JobReceipt> Jobs);
public sealed record SessionSnapshot(WorkbenchSessionId SessionId,
    WorkbenchSessionState State, Epoch Epoch, Sequence ThroughSequence,
    WorkbenchContext? Context, MeasurementDraft? Draft,
    ImmutableArray<OperationSnapshot> Operations,
    ImmutableArray<MutationSnapshot> Mutations, bool RecoveryReadOnly);
public sealed record AttachReceipt(bool Attached, WorkbenchSessionState State,
    Epoch Epoch, WorkbenchCapabilities? Capabilities,
    ImmutableArray<WorkbenchError> Errors);
public sealed record ExecuteReceipt(bool Accepted, OperationKey Key,
    OperationSnapshot? Snapshot, ImmutableArray<WorkbenchError> Errors);
public sealed record CancelRequest(OperationKey Key, CancelReason Reason);
public sealed record CancelReceipt(bool Found, bool Requested, OperationSnapshot? Snapshot,
    ImmutableArray<WorkbenchError> Errors);
public sealed record DrainReceipt(bool Drained, bool WaitCancelled,
    ImmutableArray<OperationSnapshot> PendingOperations,
    ImmutableArray<MutationSnapshot> PendingMutations,
    ImmutableArray<JobReceipt> PendingJobs, ImmutableArray<WorkbenchError> Errors);
public sealed record CloseReceipt(bool Closed, DrainReceipt Drain,
    RetentionReceipt Retention);
public enum WorkbenchEventKind { StateChanged, Progress, ResultChanged,
    MutationChanged, Terminal, SnapshotRequired }
public sealed record WorkbenchEvent(WorkbenchSessionId SessionId, Epoch Epoch,
    Sequence Sequence, WorkbenchEventKind Kind, OperationKey? Key,
    OperationPhase? Phase, Sequence? FirstMissing, Sequence? LastMissing,
    DateTimeOffset UtcTime, long MonotonicTimestamp, long FrequencyHz);
public sealed record SubscriptionId(Guid Value);
public sealed record EventBatch(ImmutableArray<WorkbenchEvent> Events,
    Sequence ThroughSequence, bool SnapshotRequired);
~~~

WbResult成功时Value非null、Errors为空，失败Value=null且Errors非空；输入与expected response结构违规为InvalidRequest/BackendFailure。量值只允许有限Scalar/有序有限Interval；Missing保持Value=null及Reason，不拿0/NaN当缺量。未知union case拒绝。MeasurementResult原完整结果资产保留上游字段/域/原SampleId/几何/证据；投影不代替原结果事实。原ResultFingerprint原样转发，不能对瘦投影哈希后冒充原结果摘要。数量状态和操作/资源状态分开。

job的GetOutcome返回逻辑输出不证明Exited；Query为底层实际执行/释放权威。原任务可能在逻辑取消后继续Running/ExitUnknown；所有尚在使用的child/native必须退出才Exited。ReleaseAsync只启动一次原释放任务；后续调用只观察它，不二次归还；ReleaseUnknown不释放job引用/槽。source job在Exited后仍可持source scope，直到child结束再Release。释放异常保留原error、任务与所有资源；不能先Throw丢Owner。Released是实际逻辑借用归还，不要求共享物理pool销毁。

operation终态只能在全部job真实Exited→Released和worker结束后形成；ResourcesReleased先于唯一Terminal事件。Rejected在已Accepted后属于逻辑拒绝，需要同样排空。接纳前返回ExecuteReceipt.Accepted=false/Snapshot=null，不伪造终态。Unknown终态限持久化回执无法确认且所有工作已经Released；DrainUnknown/ReleaseUnknown非终态。事件是通知投影，原Query为权威；当前无View权Read/ListTools失败无载荷；QueryOperation/WaitOperation返回同身份资源元数据，DisclosureAllowed=false且Result=null，不重写原Result/Error事实。恢复View后原合法结果可读。DrainReceipt中的OperationSnapshot亦按当前View裁剪，RootSnapshot只给RootSessionStatus和JobReceipt，不绕过授权披露Context/Draft/量值。cleanup查询可用元数据归还。

Subscribe每队列有界，满时撤增量并留一个SnapshotRequired（FirstMissing/LastMissing）；后续缺口只更新同标记，不无限enqueue。ReadSnapshot返回ThroughSequence，Ack只能确认已交付该订阅snapshot的序号；继续增量从严格更大序号开始。终态保在Query记录，不需要无界“绝不丢通知”。Sequence耗尽关接纳并清理，不回绕。线程池pull事件不捕获Dispatcher，无同步observer导致等待环。


### A.3 显式端口、输入scope、编辑与存储

~~~csharp
public sealed record ProbeRequest(WorkbenchContext Context);
public sealed record SourceRequest(SourceBinding Binding);
public sealed record SourceScope(SourceBinding Binding, string BorrowId);
public sealed record CoordinateRequest(CoordinateBinding Binding,
    ImmutableArray<SourceBinding> Sources);
public sealed record CoordinateReceipt(CoordinateBinding Binding, AssetRef Receipt);
public sealed record PlanValidationRequest(MeasurementPlan Plan);
public sealed record PlanValidationReceipt(MeasurementPlan Plan, AssetRef ValidationReceipt);
public sealed record MeasurementRequest(OperationKey Key, MeasurementPlan Plan);
public interface IWorkbenchSourcePort {
    IWorkbenchJob<SourceScope> StartAcquire(SourceRequest request, CallContext call,
        CancellationToken executionCancellation);
}
public interface IWorkbenchCoordinatePort {
    IWorkbenchJob<CoordinateReceipt> StartValidate(CoordinateRequest request,
        CallContext call, CancellationToken executionCancellation);
}
public interface IWorkbenchMetrologyPort {
    IWorkbenchJob<WorkbenchCapabilities> StartProbe(ProbeRequest request,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<PlanValidationReceipt> StartValidate(PlanValidationRequest request,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<MeasurementResult> StartMeasure(MeasurementRequest request,
        ImmutableArray<SourceScope> sources, CallContext call,
        CancellationToken executionCancellation);
}
public enum RoiAction { Apply, Preview }
public sealed record RoiIntent(RoiAction Action, string UpstreamOperationId,
    GeometryAsset Base, AssetRef Command, ContractRef CommandContract);
public enum ParameterAction { SetValues, Undo, Redo, Recommend, AcceptSuggestion }
public sealed record ParameterIntent(ParameterAction Action, Guid UpstreamOperationId,
    ParameterAsset Base, AssetRef? Command, ContractRef? CommandContract,
    string? CandidateId, int Steps);
public sealed record EditRequest(OperationKey Key, Epoch ExpectedEpoch,
    RoiIntent? Roi, ParameterIntent? Parameters, TimeSpan OperationTimeout);
public sealed record EditReceipt(GeometryAsset? Roi, ParameterAsset? Parameters,
    AssetRef OriginalReceipt, bool Changed, bool DraftAdopted);
public interface IWorkbenchRoiPort {
    IWorkbenchJob<EditReceipt> StartEdit(RoiIntent request, CallContext call,
        CancellationToken executionCancellation);
}
public interface IWorkbenchParameterPort {
    IWorkbenchJob<EditReceipt> StartEdit(ParameterIntent request, CallContext call,
        CancellationToken executionCancellation);
}
public enum LinkKind { Highlight, Profile, Probe }
public sealed record ViewportLink(string LinkId, SourceBinding Source,
    CoordinateBinding Coordinates, LinkKind Kind, ImmutableArray<string> StableIds,
    AssetRef? OriginalLinkQuery);
public sealed record ViewportLinkReceipt(string LinkId, AssetRef OriginalReceipt,
    bool MappingAvailable, bool Interpolated, AssetRef? OriginalSamples);
public interface IWorkbenchViewportPort {
    IWorkbenchJob<ViewportLinkReceipt> StartLink(ViewportLink request,
        CallContext call, CancellationToken executionCancellation);
}
public sealed record CompareRequest(OperationKey Key, Epoch ExpectedEpoch,
    OperationKey Left, OperationKey Right, TimeSpan OperationTimeout);
public sealed record ComparisonEntry(string CandidateId, string QuantityKey,
    QuantityProjection? Left, QuantityProjection? Right, string ReasonKey);
public sealed record ComparisonResult(bool SameDefinition, bool SameInputs,
    ImmutableArray<ComparisonEntry> Entries, ImmutableArray<string> Differences);
public interface IWorkbenchComparePort {
    IWorkbenchJob<ComparisonResult> StartCompare(MeasurementResult left,
        MeasurementResult right, CallContext call,
        CancellationToken executionCancellation);
}

public enum SaveKind { Checkpoint, Evidence, Export }
public enum MutationState { Pending, Succeeded, Rejected, Unknown }
public enum ExportFormat { EvidenceBundle, CsvInvariant }
public sealed record PersistedOperation(OperationKey Key, OperationPhase LastPhase,
    AssetRef? OriginalResult, string RequestHash);
public sealed record CheckpointAsset(string ContractVersion,
    WorkbenchSessionId OriginalSessionId, WorkbenchContext Context,
    MeasurementDraft? Draft, ImmutableArray<PersistedOperation> Operations,
    ImmutableArray<MutationRequest> OriginalMutations);
public sealed record MutationRequest(OperationKey Key, SaveKind Kind,
    AssetRef Destination, ulong ExpectedRevision, CheckpointAsset? Checkpoint,
    ImmutableArray<AssetRef> Evidence, ExportFormat? ExportFormat);
public sealed record SaveRequest(MutationRequest Mutation, Epoch ExpectedEpoch,
    TimeSpan OperationTimeout);
public sealed record MutationReceipt(OperationKey Key, string RequestHash,
    MutationState State, AssetRef? SavedAsset, AssetRef? OriginalReceipt,
    ImmutableArray<WorkbenchError> Errors);
public sealed record RestoreRequest(OperationKey Key, Epoch ExpectedEpoch,
    AssetRef Checkpoint, TimeSpan OperationTimeout);
public sealed record RestoreReceipt(bool Restored, bool ReadOnly,
    ImmutableArray<AssetRef> Unavailable, SessionSnapshot Snapshot);
public interface IWorkbenchSessionStore {
    IWorkbenchJob<MutationReceipt> StartSave(MutationRequest request,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<MutationReceipt> StartQuery(MutationRequest original,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<CheckpointAsset> StartRead(AssetRef checkpoint,
        CallContext call, CancellationToken executionCancellation);
}
public interface IWorkbenchEvidencePort {
    IWorkbenchJob<MutationReceipt> StartSave(MutationRequest request,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<MutationReceipt> StartQuery(MutationRequest original,
        CallContext call, CancellationToken executionCancellation);
}
public sealed record WorkbenchPorts(IWorkbenchSourcePort Sources,
    IWorkbenchCoordinatePort Coordinates, IWorkbenchRoiPort Roi,
    IWorkbenchParameterPort Parameters, IWorkbenchMetrologyPort Metrology,
    IWorkbenchViewportPort Viewport, IWorkbenchComparePort Compare,
    IWorkbenchSessionStore Store, IWorkbenchEvidencePort Evidence,
    IWorkbenchAuthorizationPort Authorization);
~~~

Start*为同步有限接纳，仅预检/返回job，不做native/阻塞IO；所有底层原Task由job持有并在返回前挂到§A.5预留槽。同步抛错只能发生在零任务、零资源、零副作用路径；启动失败/异常用job失败回执并收尾。Core在端口返回前保留dispatch原Task和请求/预算；若非法Adapter返回null且内部已动资源，BackendFailure封口且资源未知，不能以catch空引用自报释放。GetOutcome/Release观察用独立有限token，executionCancellation负责停止请求，二者不混。

SourceScope不是裸native token，只有原端口签发且绑定BorrowId/来源hash/frame/domain的实例才有效。它的parent job强持真实lease；metrology Adapter只能经已绑定reader形成该BorrowId下的child。若原source/计量reader无公共child借用桥，A1真实零拷贝source消费不准入；不得反射scope找HObject。本版可用同Owner独立合法读lease（两parent分别计账/排空），不能把一份已Released parent当仍可借。C1 Replay只持BCL scope，不假装原图已读取。Coordinate Receipt只是资格/映射引用，不由Core重新求矩阵。

编辑请求恰一个Roi或Parameters；混合拒绝。ROI.Apply/Preview的Command精确为原RoiEditRequest，不是Proposed Geometry替代编辑命令；Undo/Redo在该原命令内，不由Core反算。PE SetValues Command为EditBatch；Recommend Command为RecommendationRequest；Undo/Redo要求Command/Contract/Candidate=null、Steps=1，PE公开仅一次Undo/Redo不能暗扩Steps。AcceptSuggestion要求Command=null、CandidateId非空、原UpstreamOperationId为推荐操作、Steps=0。PE SetValues/Recommend Steps=0、Candidate=null。上游epoch/generation取Base固定引用及原会话绑定，不能从“当前值”隐藏填入。WorkBench operation key与上游操作ID均保留，二者不混。

建议采用仅在当前精确Base的同PE会话执行AcceptSuggestion；返回新ParameterAsset才允许显式SetDraft。不自动Apply/执行。若上游推荐只返回OperationView，OriginalReceipt保其完整资产，Parameters仍原Base，Changed=false；选中候选后才新编辑意图。Roi Preview DraftAdopted=false，不更新正式draft；已应用编辑如恰逢换epoch仍保OriginalReceipt/Changed，DraftAdopted=false并显示Stale，不能假称上游没修改。所有这些C2操作纳入同job/操作记账、查询、停止、事件、Drain；不只跟踪计量job。

CheckpointContract固定0.3，编码WB-TLV-3；未知/变更版本只读拒执行。Checkpoint不含SessionSnapshot的运行job、token、原deadline、Dispatcher、授权Allowed或SourceScope；Context.AuthorizationRevision仅旧出处。Checkpoint原操作保存最后观察态，恢复成只读历史，不复活工作。OriginalMutations禁止Kind=Checkpoint内嵌Checkpoint（防递归checkpoint）；保存checkpoint时将历史checkpoint写入记录保存在PersistedOperation且只保SavedAsset/原身份引用，不嵌套payload。有限集与无环检查先于编码。

SaveKind.Checkpoint仅Store，Checkpoint非null、Evidence空、ExportFormat=null；Evidence走EvidencePort，Checkpoint=null且Evidence非空；Export走同Port且ExportFormat非null、证据非空。Destination是Owner资产目标，无裸文件路径，ExpectedRevision来自调用方明确CAS（0表示CreateOnly，其它正数）。端口回显同Key+完整原Mutation canonical hash；错回执拒绝且查询原请求，不能认另一目的地成功。MutationReceipt.State和job资源状态两个轴：持久化Unknown+job Released可记录Unknown终态；job未知不能返回ResourcesReleased。

Query原Mutation只能StartQuery，不调用StartSave；原相同Save重放只返回原MutationSnapshot。恢复不知道原内容或原hash仅保存Unknown关联，禁止新发Query变更载荷。Checkpoint与证据查询职责不同，不在两个Port各读相同Checkpoint创建第二Owner。


### A.4 工作台自身调用、幂等和重算

~~~csharp
public sealed record ExecuteRequest(OperationKey Key, Epoch ExpectedEpoch,
    MeasurementPlan Plan, TimeSpan OperationTimeout);
public sealed record RecomputeRequest(OperationKey Key, Epoch ExpectedEpoch,
    OperationKey Previous, RecomputePolicy Policy, MeasurementPlan? ExplicitPlan,
    TimeSpan OperationTimeout);
public sealed record LinkRequest(OperationKey Key, Epoch ExpectedEpoch,
    ViewportLink Link, TimeSpan OperationTimeout);
public sealed record RebindRequest(WorkbenchContext Context, Epoch ExpectedEpoch,
    TimeSpan OperationTimeout);
public abstract record OperationPayload;
public sealed record MeasurementPayload(MeasurementResult Value) : OperationPayload;
public sealed record EditPayload(EditReceipt Value) : OperationPayload;
public sealed record LinkPayload(ViewportLinkReceipt Value) : OperationPayload;
public sealed record ComparisonPayload(ComparisonResult Value) : OperationPayload;
public sealed record RestorePayload(RestoreReceipt Value) : OperationPayload;
public sealed record MutationPayload(MutationReceipt Value) : OperationPayload;
public interface IMeasurementWorkbenchFactory {
    IMeasurementWorkbenchRoot CreateRoot(IRootReservation reservation,
        RootOptions options, WorkbenchPorts ports, TimeProvider timeProvider);
}
public sealed record ChildRegistration(string OwnerId);
public interface IMeasurementWorkbenchRoot : IAsyncDisposable {
    WbResult<ChildRegistration> RegisterChildOwner(IWorkbenchChildOwner owner);
    string RootId { get; }
    IMeasurementWorkbenchSession Create(SessionOptions options);
    RootSnapshot Query();
    ValueTask<CloseReceipt> CloseAsync(TimeSpan observationBudget,
        CancellationToken waitCancellation);
}
public interface IMeasurementWorkbenchSession : IAsyncDisposable {
    WorkbenchSessionId Id { get; }
    WbResult<SessionSnapshot> Read();
    WbResult<WorkbenchCapabilities> ListTools();
    ValueTask<AttachReceipt> AttachAsync(WorkbenchContext context, TimeSpan observationBudget,
        CancellationToken waitCancellation);
    ValueTask<AttachReceipt> RebindAsync(RebindRequest request,
        CancellationToken executionCancellation);
    WbResult<MeasurementDraft> SetDraft(MeasurementPlan plan, Epoch expectedEpoch);
    ExecuteReceipt Execute(ExecuteRequest request, CancellationToken executionCancellation);
    ExecuteReceipt Recompute(RecomputeRequest request, CancellationToken executionCancellation);
    ExecuteReceipt Edit(EditRequest request, CancellationToken executionCancellation);
    ExecuteReceipt Link(LinkRequest request, CancellationToken executionCancellation);
    ExecuteReceipt Compare(CompareRequest request, CancellationToken executionCancellation);
    ExecuteReceipt Restore(RestoreRequest request, CancellationToken executionCancellation);
    WbResult<OperationSnapshot> QueryOperation(OperationKey key);
    ValueTask<WbResult<OperationSnapshot>> WaitOperationAsync(OperationKey key,
        TimeSpan observationBudget, CancellationToken waitCancellation);
    CancelReceipt RequestCancel(CancelRequest request);
    WbResult<MutationSnapshot> Save(SaveRequest request,
        CancellationToken executionCancellation);
    WbResult<MutationSnapshot> QueryMutation(OperationKey original);
    ExecuteReceipt ResolveMutation(OperationKey queryKey, OperationKey original,
        TimeSpan operationTimeout, CancellationToken executionCancellation);
    WbResult<CheckpointAsset> ExportCheckpoint();
    WbResult<SubscriptionId> Subscribe(int capacity);
    ValueTask<WbResult<EventBatch>> ReadEventsAsync(SubscriptionId subscription,
        Sequence after, int maxItems, TimeSpan observationBudget, CancellationToken waitCancellation);
    WbResult<SessionSnapshot> ReadSnapshot(SubscriptionId subscription);
    WbResult<EventBatch> AcknowledgeSnapshot(SubscriptionId subscription, Sequence through);
    ValueTask<DrainReceipt> UnsubscribeAsync(SubscriptionId subscription,
        TimeSpan observationBudget, CancellationToken waitCancellation);
    ValueTask<DrainReceipt> DrainAsync(TimeSpan observationBudget, CancellationToken waitCancellation);
    ValueTask<CloseReceipt> CloseAsync(TimeSpan observationBudget, CancellationToken waitCancellation);
}
public sealed class MeasurementWorkbenchFactory : IMeasurementWorkbenchFactory {
    public MeasurementWorkbenchFactory();
    // CreateRoot严格实现上面唯一接口，无其它隐藏构造或environment读取。
}
public sealed class WorkbenchConfigurationException : Exception {
    public WorkbenchConfigurationException(string message);
}
public sealed class WorkbenchCleanupIncompleteException : Exception {
    public WorkbenchCleanupIncompleteException(CloseReceipt receipt);
    public CloseReceipt Receipt { get; }
}
~~~

OperationSnapshot 的Result字段类型唯一为OperationPayload?；Measure/Edit/Link/Compare/Restore按上述case一一匹配，不能以后续helper扩union。ResolveMutation产生独立query操作，只读取原Mutation；其逻辑输出为MutationPayload，属于同一封闭联合。不带新写入权。所有方法target signature冻结，例子旧ExecuteAsync/SetDraftAsync/CancelAsync/QueryMutationAsync不再适用。

Created会话Attach首次成功Active；Attach结构/授权失败无job回Created；已派发后失败只在已真实释放时回Created，未释放保持Attaching/DrainUnknown并拒新Attach，待Close。Attach观察取消不撤意图。Rebind的execution token请求停止新准备，先撤旧采纳、epoch+1、排空在途原operation及display link job，全部已释放才读取替代精确Context；失败回Active且保留旧Context但Draft=null/旧投影标Stale，不能回绕epoch。epoch溢出封口清理。Close永不复开。

Drain停止当前operation/child并排空，保持Active且不允许新接纳直到此次drain真实结束；Close额外永久关接纳。SessionState.DrainUnknown对应关闭/重绑定待清理；DrainReceipt具体资源轴不据会话状态推断。Root Close关闭所有session和内部worker/child Owner；host调用者任务由depot单独等待，root不等待Close的调用者，waitCancellation只结束本次观察；标准Dispose用Profile.CloseTimeout，同一关闭未收敛抛上述Cleanup异常，保留depot绑定。

Plan.Inputs必须逐项匹配接受时Context.Sources中的完整绑定（source/hash/frame/domain/sampling/operand/role）；执行不得偷带未授权新源，ExplicitInputs重算若改变Context外的源须先Rebind显式Context。TemplateKey与模板实际Key一致，MethodProfile/Contract/全部operands/参数绑定必须逐字段验证；A.6 StartValidate经ReadMethodProfileAsync/ReadContinuousProfileAsync读取精确引用并调用Asun.Metrology.Core.MetrologyValidator.Validate(request,profile)对应公开重载；连续公开Compute/Validate依实际payload，不从request资产猜字段，Continuous payload资格仍由Reader/Service在执行时验证，不谎称未读取payload已完整验证。SourceRole/有效域/手性未知不得默认为主图或完整支持。

每个新操作key的OperationId及AttemptId都唯一，二者1:1；同OperationId换AttemptId、同AttemptId换OperationId均IdentityConflict。一次重放按规范字段完整值比较，不靠record数组引用Equals或hash单值；操作token对象不参与身份；OperationTimeout首次接纳冻结、后续重放不能延长。结构前检→原key查完整payload→已有项回放/冲突→仅新key核epoch/授权/状态/预算/token→原子预留→派发；关闭/撤权不会把原同payload状态查询改成新执行，payload披露仍核View权。

Execute只接受显式Plan，没有SameInputs枚举可被忽略。Recompute.SameInputs要求ExplicitPlan=null，Previous存在且原完整Plan/已接纳Context保存；精确复用Inputs/Coordinates/ROI/Parameters/tool/profile/template，绝不读当前Draft代替。ExplicitInputs要求ExplicitPlan完整非null，所有差异向用户投影；Previous保追溯。重算采用新Key、调用当前授权/引用资格检查，不修改旧结果。原source失效是StaleBinding/InputUnavailable，不切latest、不自动降为插值。TemplateKey是模板原请求里的key；Adapter仅将request.Key替换为新的上游key，模板其它字段完整保持。模板的MethodProfile/operands与Plan逐字段一致才运行，不从ToolId猜Definition。

Edit/Link/Compare/Restore/Resolve各有唯一key、同身份重放、有界job与Query；同key跨操作种类冲突。Compare只给原有效/无量投影及精确差异，不计算第二份计量差值公式，不强配不同candidate ID。异单位/定义不可比较，只列两侧和Reason；不把差异当合格。恢复需Created/Active无未决操作、epoch匹配、View权和相同Contract；成功RecoveryReadOnly=true，显式重新Attach到新session并SetDraft才可执行，Restore不重新取得历史lease/运行未完成请求。

Edit.Return上游已变更事实而本工作台epoch/授权失效时不撤销原Owner；保存OriginalReceipt但DisclosureAllowed=false/不采用新Draft，恢复后显式读取原Owner最新的确定revision再SetDraft，不把原Applied改写Cancelled。

原业务错误和cleanup错误分别保留：关闭失败不覆盖已发生的输入/计量/存储错误；Host exit code按所有业务/收尾断言合并，不在try中return绕过finally对退出码的修改。异常投影仅WorkbenchError固定Code/key+有界args，不解析异常文案猜领域失败。


### A.5 Factory前预留、Root强持与确认转交

~~~csharp
public sealed record DepotOptions(string DepotId, int MaxRoots, int MaxTrackedHostTasks,
    long MaxRetainedBytes, TimeSpan CleanupObservationBudget);
public enum RetentionState { Reserved, Owned, TransferOffered, Transferred, Released }
public sealed record RetentionReceipt(string DepotId, Guid ReservationId,
    string RootId, RetentionState State, Guid? AcceptedTransferId);
public sealed record RootSessionStatus(WorkbenchSessionId SessionId,
    WorkbenchSessionState State, int PendingOperations, int PendingMutations);
public sealed record RootSnapshot(string RootId, bool AdmissionClosed,
    ImmutableArray<RootSessionStatus> Sessions, ImmutableArray<JobReceipt> PendingJobs,
    long ReservedBytes, RetentionReceipt Retention);
public sealed record RootReservationRequest(string RootId, long MaxRetainedBytes);
public sealed record TransferOffer(Guid OfferId, string RootId,
    string SourceDepotId, Guid SourceReservationId, string TargetDepotId,
    IMeasurementWorkbenchRoot Root, ImmutableArray<Task> OriginalHostTasks,
    long ReservedBytes);
public interface ITransferProof {
    string IssuerDepotId { get; }
    Guid TransferId { get; }
    RetentionReceipt Query();
}
public sealed record TransferAcceptance(Guid OfferId, Guid TransferId,
    string TargetDepotId, Guid TargetReservationId, string RootId, bool Accepted, ITransferProof? Proof);
public sealed record DepotSnapshot(string DepotId, int Roots,
    int HostTasks, long ReservedBytes, ImmutableArray<RetentionReceipt> Retained);
public interface IRootReservation {
    Guid ReservationId { get; }
    RetentionReceipt Query();
}
public interface IWorkbenchRecoveryDepot {
    WbResult<IRootReservation> Reserve(RootReservationRequest request);
    WbResult<TransferOffer> OfferTransfer(IRootReservation reservation, string targetDepotId);
    WbResult<TransferAcceptance> AcceptTransfer(TransferOffer originalOffer);
    WbResult<RetentionReceipt> ConfirmTransfer(IRootReservation original,
        TransferAcceptance acceptance);
    WbResult<RetentionReceipt> Query(Guid reservationId);
    WbResult<IRootReservation> GetReservation(Guid reservationId);
    WbResult<RetentionReceipt> ReleaseClosed(IRootReservation reservation);
    DepotSnapshot Read();
    ValueTask<DepotSnapshot> ObserveAsync(TimeSpan observationBudget,
        CancellationToken waitCancellation);
}
public sealed class WorkbenchRecoveryDepot : IWorkbenchRecoveryDepot, IWorkbenchHostTaskAdmission {
    public WorkbenchRecoveryDepot(DepotOptions options, TimeProvider timeProvider);
    // 实现上述接口，内部有界ledger；不读取环境、不创建hidden service。
}
~~~

Host进程入口持有两个具体depot实例直到整个应用/测试进程结束，所有根创建前必须Reserve；Factory验证reservation由本模块具体depot签发、未消费、RootId/bytes与RootOptions一致，原子把创建的root绑定其ledger再返回。Factory异常若无任务/资源将Reserved释放；创建过程中已有资源则depot继续Owned返回明确错误，不允许Host局部变量为null就放槽。记录自身root/session/job/worker/内部关闭原Task，不靠Host日志声称保留。Profile预留与depot总MaxRetainedBytes两个门同时检查。

Host工作派发前同一depot先通过ReserveHostTask占有界槽，Start在槽已占有后调用dispatch并保存返回的原Task。Start只允许一次；派发异常保原错误和槽直到确认零资源/任务，不能先Task.Run再登记或无限重试。以下是同一depot的完整task接纳接口：

~~~csharp
public interface IHostTaskReservation {
    Task Start(Func<Task> dispatch);
}
public interface IWorkbenchHostTaskAdmission {
    WbResult<IHostTaskReservation> ReserveHostTask(IRootReservation reservation);
}
~~~

WorkbenchRecoveryDepot实现IWorkbenchHostTaskAdmission，ReserveHostTask最多MaxTrackedHostTasks且每root≥1关闭观察保留槽。Start只一次，不对自己原Task调用root.Close造成自等待：Host业务task的状态/cleanup任务放depot的Host槽，但root.Close仅等待root内部job/worker；depot.ReleaseClosed另外确认Host槽退出。root不能等待当前Host正在等待的Close调用者。Host任务异常是一个原错误，depot不把其faulted当资源Released。

Offer关源reservation新Host任务派发门，冻结root/原task列表+预算并保源depot引用；target.Accept在本机同一进程中校验OfferId/Root引用一致、issuer/源原reservation合法及预算后原子强持相同root/所有task，签发TransferId/target reservation，Accepted=true。Confirm必须通过target签发的Proof回查目标实际ledger状态：Proof是模块内部sealed能力实例，强持target具体depot与原offer/reservation，伪造ITransferProof实现/不匹配issuer或TransferId拒绝；不能根据record字符串寻找全局depot。源仍保留至确认；确认后源变Transferred、解除它的引用和计账，目标变唯一Owned，root的retention指向同Proof真实ledger；已登记原Host task的完成关联一并转移，不能只拷当时Task数组后丢迟到引用。确认前所有新增派发拒绝，不让Offer之外冒新task。容量不足/迟到/异常无确认时源继续Owned/TransferOffered；不能凭接受字符串/日志认为转交。再次同offer幂等返回同acceptance，异payload拒绝。Offer/Acceptance是运行capability，不可序列化或跨进程重启恢复；没有静态全局depot。

RootSnapshot/CloseReceipt.Retention指出当前真实depot/reservation，不等于Released；Owner转交不改变operation终态或Drained值。ReleaseClosed只在root.Closed、所有root内job实际Released、无pendingHostTask及其可能迟到结果、无UI借用时成功；否则返回CleanupUnknown并留槽。仅Reserved且尚未绑定root且零task可释放。发生超时/离栈/异常，方法调用者可结束，但进程入口的depot仍持整个引用图；若入口也退出就是进程级中断，不能声称后续原Task仍被追踪或“下次启动继续释放”。测试外层强杀仅失败证据。


### A.6 逐字段公开消费范围（Adapters DLL）

以下bridge只读取/组合公开值类型；没有从产品对象反射字段、从UI行号推身份、从参数名字猜方法或复制任何ROI/拟合/积分算法。所有类型引用以完整namespace消歧。A1本轮限定为已明确的ROI纯编辑、PE内存编辑、metrology离散/连续精确请求以及viewport显式完整Context；真实native/源lease/持久化Owner接线属于A2。

| 消费链 | 字段与固定执行 | 缺口/拒绝边界 |
|---|---|---|
| ROI snapshot | GeometryAsset.Contract=(Asun.Modules.RoiGeometry.GeometrySnapshot,0.3)；RoiSessionId/DocumentId/Revision/Frame逐值等于IRoiGeometryCore.Query。pixel=(ColumnRowPixelCenters,Pixel)，物理XY=(RightHandedPhysicalXY,Millimeter)；Micrometer必须外部coordinate转换/保新出处，不能贴Mm标签 | 空Nodes合法纯编辑，不证明支持；工作台ROI不是计量SearchRoi operand，不能自动转换curve/region |
| ROI命令 | Command精确读Asun.Modules.RoiGeometry.RoiEditRequest；OperationId=UpstreamOperationId，SessionId=Base.RoiSessionId，ExpectedRevision=Base.Revision，Epoch=Base.OwnerEpoch、ProfileRevision=Base.ProfileRevision，两者在新的operation接纳时与登记原session逐值核查；已登记原ID同payload先按上游原回执查询/回放，不因当前revision变了再次Apply；Mode匹配RoiAction；Commands内容/順序/原deadline全保存。Apply在有界worker调用core.Apply，Preview调用core.PreviewAsync；QueryOperation原ID检查ResourcesReleased/IsTerminal，非终态保持job未知 | 不从工作台Epoch写上游Epoch；原ROI deadline由Host建立Command资产时用Stopwatch显式给出，Adapter不改资产内deadline；验证其当前剩余时间不大于本次CallContext.RemainingBudget，违反则在零Apply前拒绝并要求新Command/新Key。原同payload重放复用原deadline；不拿工作台TimeProvider timestamp直接当Stopwatch |
| ROI hash/输出 | GeometrySnapshot由原IRoiGeometryCodec.Encode生成roi-json-v1全envelope与Sha256；payloadHash与envelope hash分别保存，AssetRef.Sha256为全envelope；不能只hashnode数组。收尾不Drain共享ROI session，只观察本操作；Host最终独立关闭其owned ROI | snapshot跨进程值编码消费与本模块command值封装在A.10.4闭合；原Codec-01规格已接收，实际编译/运行另验。Command不使用Geometry Codec冒充命令Codec；跨进程draft与新进程原RoiEditRequest身份分开 |
| PE schema/snapshot | Asun.Modules.ParameterEditor v0.2；ParameterAsset.EditorSessionId=session.Id，Generation=Read.Draft.Generation，schema/source/hash用ParameterCanonical原规范；Schema ref.Version保留原Version，不能改成AssetRef.Revision文本。snapshot内容hash不含Generation，但请求身份包含Generation | Missing/Null/Default/Explicit原样；单独工作台AssetRef revision不可替代PE generation |
| PE编辑 | SetValues→CheckEdits/EditBatch→SetValues；Undo/Redo→原单次Undo/Redo(expectedGeneration)；Recommend→RecommendAsync原request，再GetOperation同Upstream ID直到ResourcesReleased；AcceptSuggestion→原推荐ID+candidateId+Base.Generation。Read.Errors/Validation完整保OriginalReceipt | PE数据为decimal/long；不得让AngleDegrees进入decimal通用或Int64/ms映射Duration。候选采用不RequestApply |
| PE→计量 | 参数snapshot与工具MethodProfile必须有Owner签发ParameterProfileBindingReceipt(Parameters,MethodProfile)，且Exact=true、完整定义已冻结。A.10.1–A.10.3给三种固定工具的Schema/Patch/新Profile/receipt映射 | 不提供通用Schema字段→MethodProfile转换器；未列工具/字段组合Unsupported，数值不保真拒绝；角单位及客户资格不暗推 |
| metrology v0.2输入 | 原MetrologyRequest完整模板，Key.OperationId替换workbench Key.Operation.Value，RequestRevision固定1；MethodProfile=Tool.MethodProfile.Id/Revision/hash；Operands按原顺序与Plan.Inputs逐项OperandId/Role/Content/Frame/Calibration/Kind/unit相等；Coordinates五资产字段与Plan等；Definition、Budget全部来自原template/profile逐字段相等 | Scope只Engineering/CalibratedPhysical/PixelDiagnostic原枚举；不得根据ToolId推Scope。Revision ulong与AssetRef保持，无long溢出转型 |
| v0.2数据资格 | Geometry/RegionRuns/Contours/Mesh/Image对应DataKind；图像仅Byte量测。Frame/math XY/row-col、Mapping/Calibration/ApplicabilityReceipt必须明确；IRoi node选域需原Owner派生SourceRef并提供完整operand/support receipt | TilePyramid/HeightField/PointCloud不冒Image/TriangleMesh；先经原Owner得到合格payload/asset才接入。域缺口依原method拒识，不截分母 |
| v0.2执行/资源 | IMetrologyService.Validate→MeasureAsync原Task→GetOperation原key/RequestCancel。观察Phase.ResourcesReleased+terminal及原Task真实完成才job.Exited/Released；Phase.DrainUnknown/ReleaseUnknown保job/输入scope。共享Service不能每operation Close | 开放接口不足以证明child borrow的范围按A.3处理；不能取service内backend/native 私有字段 |
| v0.2输出 | Outcome/Validity/Scope原样；每Candidate.Quantities→scalar投影，Unit枚举同名映射；Support、Uncertainties、Witnesses、Coverage、Affine、Edges、SelectionPosition、Volume及FittedGeometry保OriginalResult资产。Support.Complete不映D=V | 未提供不确定度保持NotProvided/NotEvaluable与MissingComponents；不改Measured事实为PASS |
| continuous v0.3 | 原ContinuousRequest/profile/input，Key同上；Profile/Input/TargetFrame与精确资产相等，Method与Profile、Payload/Options/report case依IM-036§19一一对应；全部mm且TargetFrame已经归一，不隐式映多frame。IContinuousMetrologyService.Validate→MeasureAsync→GetOperation/RequestCancel | SupportedField/Q/材料资格由原Owner供，不拟合、重建、封洞或把KnownPartDiagnostic称整量 |
| 连续结果投影 | Sections/Path/Axes/Projection/Planes/GeometryMeasures/Field七case原report保留。Intervals直接IntervalValue；Domain面积mm²、Integral体积mm³、Moments M00 mm²/M10-M01 mm³/M20-M11-M02 mm⁴，PositiveCenter J/K mm⁴，CDF probability Ratio/Height mm，Quantiles mm；signed/positive/negativeMagnitude原name+区间分别列；未知整域缺量 | 有理/数值证书NumericStatus/StoppedFragment/CompletedE/RemainingU/TargetComplete保原report，不从投影值估合格。Unit=Mm4新增投影枚举不改变上游Contract |
| viewport Context | 完整原Asun.UI.Viewports.ViewportContext资产，由原Owner读出Sources/Layers/Authorization/Language/ApiVersion/ContextRevision/InitialView。SourceRole/CorrelationId/Timing明确；image Width/Height/channel/bit/sample/convention/CoordinateRevision/SourceRevision/channels/validity/levels/decode/statistics全保留 | Workbench SourceBinding本身没有channels/decode/camera等全部viewport字段，不推断填造；缺完整Context拒link/显示，不缩成“source ID相同即可” |
| viewport操作 | 创建的session一次AttachAsync；后续完整更新用ViewportUpdate(BaseContextRevision,Replacement)，不是再次Attach。Link原查询资产只能已声明ViewportCommand/ProbeRequest；ApplyAsync/ProbeAsync原task登记；UI绑定用IViewportControlBinding.BindAsync(session,同root,ViewportUiBindingOptions OwnSession=false) | 工作台Epoch不冒viewport generation。Partial/Unknown/PendingResources逐项保原receipt；UI卸载不关闭共享source/其它session |
| viewport退出/Owner | link既有session借用只停止/清理本link投影，不调用shared session.Dispose；若link拥有独立session可调用DisposeAsync(timeout,ct)。原CleanupSnapshot.State=OwnerAccepted只是责任转移，Drained=false直到原root查到真归还 | same source double实例不能省Required准入/资源permit；BudgetOnly仅离线私有pool |

下列是Adapters的唯一公开装配声明；资产reader返回内存深冻结公开DTO并有界校验，IO/native由其Host实现，不能成为未声明的“helper”。所有Read*参数含预留CallContext，不能无界加载。Source/Coordinate/Store/Evidence/Viewport/Compare/Authorization实现由Host显式注入；ROI/PE/计量桥本模块实现，SourceBridge真实零拷贝能力依原Owner。

~~~csharp
// namespace Asun.Modules.MeasurementWorkbench.Adapters
public sealed record OwnerValue<T>(AssetRef Identity, ContractRef Contract, T Value) where T : class;
public sealed record ParameterProfileBindingReceipt(ParameterAsset Parameters,
    AssetRef MethodProfile, AssetRef Receipt, bool Exact);
public interface IWorkbenchOwnerAssets {
    ValueTask<OwnerValue<Asun.Modules.RoiGeometry.RoiEditRequest>> ReadRoiCommandAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<OwnerValue<Asun.Modules.ParameterEditor.EditBatch>> ReadParameterEditAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<OwnerValue<Asun.Modules.ParameterEditor.RecommendationRequest>> ReadRecommendationAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<OwnerValue<Asun.Metrology.Contracts.MetrologyRequest>> ReadMetrologyRequestAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<OwnerValue<Asun.Metrology.Contracts.ContinuousRequest>> ReadContinuousRequestAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<OwnerValue<Asun.Metrology.Contracts.MethodProfile>> ReadMethodProfileAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<OwnerValue<Asun.Metrology.Contracts.ContinuousProfile>> ReadContinuousProfileAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<OwnerValue<ParameterProfileBindingReceipt>> ReadParameterBindingAsync(
        AssetRef asset, CallContext call, CancellationToken ct);
    ValueTask<AssetRef> RetainResultAsync(OwnerResult publicDto, ContractRef contract,
        CallContext call, CancellationToken ct);
}
public sealed record PublicOwnerBindings(Asun.Modules.RoiGeometry.IRoiGeometryCore Roi,
    Asun.Modules.RoiGeometry.Serialization.IRoiGeometryCodec RoiCodec,
    Asun.Modules.RoiGeometry.ValidationProfile RoiProfile,
    Asun.Modules.ParameterEditor.IParameterEditorSession Parameters,
    Asun.Metrology.Contracts.IMetrologyService Metrology,
    Asun.Metrology.Contracts.IContinuousMetrologyService? Continuous,
    IWorkbenchOwnerAssets Assets, IWorkbenchSourcePort Sources,
    IWorkbenchCoordinatePort Coordinates, IWorkbenchViewportPort Viewport,
    IWorkbenchComparePort Compare, IWorkbenchSessionStore Store,
    IWorkbenchEvidencePort Evidence, IWorkbenchAuthorizationPort Authorization);
public sealed class WorkbenchAdapterFactory {
    public WorkbenchAdapterFactory();
    public WorkbenchPorts Create(PublicOwnerBindings bindings, ResourceProfile limits);
}
~~~

RetainResultAsync只接受以下封闭OwnerResult包装，不接受object/任意JSON；未知派生case拒绝，不反射私有字段。

~~~csharp
public abstract record OwnerResult;
public sealed record RoiOwnerResult(Asun.Modules.RoiGeometry.RoiOperationReceipt Value) : OwnerResult;
public sealed record ParameterOwnerResult(Asun.Modules.ParameterEditor.EditorView Value,
    Asun.Modules.ParameterEditor.OperationView? Operation) : OwnerResult;
public sealed record MetrologyOwnerResult(Asun.Metrology.Contracts.MetrologyResult Value) : OwnerResult;
public sealed record ContinuousOwnerResult(Asun.Metrology.Contracts.ContinuousResult Value) : OwnerResult;
~~~

RetainResultAsync参数为OwnerResult publicDto，没有object重载。Reader返回Contract/Identity逐值与请求相等后还需原canonical/hash核验；ROI跨进程command只承载A.10.4完整编辑值，在目标进程显式绑定新Session/Epoch/deadline后登记新RoiEditRequest，不能把源请求hash或源期限当新执行身份。原结果完整保留失败时量测结果可只作内存工程投影并标EvidenceUnavailable，不能称持久证据已保存。

MeasurementPlan的ParameterProfileBinding：Parameters非null则必填该绑定receipt、参数hash与MethodProfile精确闭合；null Parameters时该字段必须null。ROI输入到计量的映射只允许Plan.Inputs已列的明确派生资产；不把显示ROI自动当operand。A.10闭合固定参数转换、C5实际多父读取、reference/Q值映射和连续方法消费；未支持的构造组合明确拒绝，真实原资源桥与client产品Store目的地仍依相应A2运行/产品门，C1/C2接收保持。


### A.7 可选WPF接入、UI根与原Dispatcher任务

~~~csharp
// Core：外部UI/源Owner仅公开生命周期，不把WPF对象带进Core。
public interface IWorkbenchChildOwner {
    string OwnerId { get; }
    void RequestClose();
    ValueTask<DrainReceipt> ObserveAsync(TimeSpan budget, CancellationToken waitCancellation);
}
~~~

IMeasurementWorkbenchRoot的公开成员包括RegisterChildOwner(IWorkbenchChildOwner owner)→WbResult<ChildRegistration>；ChildRegistration(string OwnerId)是登记回执，构造/预算/唯一ID验过且root/depot已强持owner后才Succeeded。登记只能在root未关闭且child尚未派发任务时进行；child capacity占MaxTrackedJobs，不重置Profile。Root.Close先RequestClose，观察child资源归还；若child等待同Root.Close构成自等待，违规BackendFailure并保Owner，不能强行成功。

~~~csharp
// namespace Asun.Modules.MeasurementWorkbench.Wpf
public sealed record UiRootOptions(string OwnerId, int MaximumBindings,
    int MaximumTrackedTasks, long MaximumRetainedBytes, TimeSpan CleanupBudget);
public sealed record WorkbenchPresentation(string ResourceCulture,
    string FormatCulture, string ThemeName, long Revision);
public interface IWorkbenchTextResources {
    string Resolve(string resourceKey, string resourceCulture);
}
public sealed record WorkbenchMountOptions(string BindingId, string AutomationIdPrefix);
public enum UiPhase { Created, Mounting, Bound, Closing, CleanupUnknown, Released }
public sealed record UiReceipt(string BindingId, UiPhase Phase, bool Detached,
    bool Drained, ImmutableArray<string> PendingIds,
    ImmutableArray<WorkbenchError> Errors);
public sealed record UiMountRequest(string BindingId, IMeasurementWorkbenchSession Session,
    WorkbenchContext Context, WorkbenchPresentation Presentation,
    IWorkbenchTextResources Resources);
public interface IWorkbenchUiChildrenLifetime {
    ValueTask<WbResult<UiReceipt>> SetPresentationAsync(WorkbenchPresentation presentation,
        TimeSpan observationBudget, CancellationToken waitCancellation);
    ValueTask<UiReceipt> DetachAsync(TimeSpan observationBudget,
        CancellationToken waitCancellation);
}
public sealed record UiChildren(System.Windows.UIElement MainSurface,
    System.Windows.UIElement? Inspector, IWorkbenchUiChildrenLifetime Lifetime,
    string SurfaceId);
public interface IWorkbenchUiChildrenFactory {
    IWorkbenchJob<UiChildren> StartMount(UiMountRequest request,
        CancellationToken executionCancellation);
}
public sealed class MeasurementWorkbenchUiRoot : IWorkbenchChildOwner {
    public MeasurementWorkbenchUiRoot(IMeasurementWorkbenchRoot root,
        UiRootOptions options);
    public string OwnerId { get; }
    public void RequestClose();
    public ValueTask<DrainReceipt> ObserveAsync(TimeSpan budget,
        CancellationToken waitCancellation);
    public UiReceipt Query(string bindingId);
}
public interface IMeasurementWorkbenchControl {
    ValueTask<WbResult<UiReceipt>> MountAsync(MeasurementWorkbenchUiRoot uiRoot,
        IMeasurementWorkbenchSession session, WorkbenchMountOptions options,
        WorkbenchPresentation presentation, IWorkbenchTextResources resources,
        IWorkbenchUiChildrenFactory childrenFactory, TimeSpan observationBudget,
        CancellationToken waitCancellation);
    ValueTask<WbResult<UiReceipt>> SetPresentationAsync(WorkbenchPresentation presentation,
        TimeSpan observationBudget, CancellationToken waitCancellation);
    ValueTask<UiReceipt> DetachAsync(TimeSpan observationBudget,
        CancellationToken waitCancellation);
}
public sealed class MeasurementWorkbenchControl : System.Windows.Controls.UserControl,
    IMeasurementWorkbenchControl {
    public MeasurementWorkbenchControl();
    // 三方法严格实现上面接口，不靠ServiceLocator或附加未声明入口。
}
~~~

UiRoot构造无窗口/IO，同步RegisterChildOwner并核success后才可Mount；constructor登记失败抛WorkbenchConfigurationException、零control动作。UI Root.OwnerId/root引用固定，不能绑定另一root的session/同名ID。内部在childrenFactory.StartMount前预留binding槽、child job、原DispatcherOperation.Task及迟到输出/cleanup空间；MaximumTrackedTasks≥8×MaximumBindings+1，bytes>0且受Core root剩余logical上限。每binding最多8个本层原task，3个关闭/迟到任务保留；上游viewport/PE自己根预算也独立预留，不能借“其root已收费”省工作台强持。图像像素/GPU额外由原Owner批准，与逻辑引用bytes两个轴。

Mount必须在本Control.Dispatcher调用，唯一原对象保在UI根；same bindingId+same control/session/presentation原请求幂等，different冲突。输入未通过/无View权不调用child；超时/等待取消只结束本次观察，仍Mounting/CleanupUnknown。迟到UiChildren先登记再取消/Detach/Release原child，不在已关闭控件安装；MainSurface必须实际UIElement且无其它视觉parent、Dispatcher同control，Inspector同；错Dispatcher/假截图拒绝，原job仍清理。设置Content、WPF property或截图不证明已渲染/原native借用退出。

Control借用session，Detach永不关闭Core session；关闭权限由Host单独session.Close/root.Close，没有OwnSession歧义。Detach停新命令、退订、取消capture/gesture、排空原投影read，原Dispatcher移除内容/图/菜单引用，然后children Lifetime.Detach→原child job.Release。它只等自身task（slot外总关闭），不在某cleanup Task里等待该Task。Unloaded只是RequestClose；Dispatcher关闭无法执行移除/ACK为CleanupUnknown，保所有task/child/control/binding，不能后台构造成功回执。UiRoot RequestClose不会Close Core；Core Close可RequestClose UiRoot，外部Host负责先UI Observe后Core Close，不形成UI→Core→UI环。

工作台独立包随Wpf DLL提供DefaultWorkbenchTextResources无参实现IWorkbenchTextResources，三语命令/状态/恢复/工具/单位/Tooltip/UIA俱全；宿主可注入覆盖。SetPresentation只更新本binding/child/菜单/SuperTip/浮动区域，失败保持旧revision且保IME token；资源缺键按§7.4fallback，并记具体key诊断。数值显示不改变上游原request hash或量值。

真实public-owner child工厂构造声明（仅Wpf DLL引用上游UI）：

~~~csharp
public sealed record ViewportUiOwner(Asun.UI.Viewports.IViewportSession Session,
    Asun.UI.Viewports.IViewportProcessRoot Root,
    Asun.UI.Viewports.Wpf.ViewportControl Control,
    Asun.UI.Viewports.Wpf.ViewportUiBindingOptions Options);
public sealed record ParameterUiOwner(
    Asun.Modules.ParameterEditor.IParameterEditorSession Session,
    Asun.Modules.ParameterEditor.Wpf.ParameterEditorControl Control,
    Asun.Modules.ParameterEditor.Wpf.InspectorOptions Options,
    Asun.Modules.ParameterEditor.Wpf.IEditorTextResources Resources,
    Asun.Modules.ParameterEditor.Wpf.EditorPresentation Presentation);
public sealed class PublicOwnerUiChildrenFactory : IWorkbenchUiChildrenFactory {
    public PublicOwnerUiChildrenFactory(ViewportUiOwner viewport,
        ParameterUiOwner? parameters, TimeSpan cleanupBudget);
    // 实现StartMount，两个Owner借用，不dispose其root/session。
}
public sealed class DefaultWorkbenchTextResources : IWorkbenchTextResources {
    public DefaultWorkbenchTextResources();
    public string Resolve(string resourceKey, string resourceCulture);
}
~~~

Viewport Options.OwnSession必须false；MainSurface就是传入Control，同一实例调用((IViewportControlBinding)Control).BindAsync原Session/Root/Options，保返回IViewportUiBinding与原Bind task；Parameters非null则调用其同一Control.Attach(Session,Options,Resources,Presentation)，failure不得装假Inspector。随后Viewport.SetResourcesAsync/PE.SetPresentationAsync更新各实例；Detach PE.Detach原Task、Viewport binding.Unbind原Task以及工作台原Dispatcher引用全部退出才child job Released。不Close上游session，也不把viewport CleanupState.OwnerAccepted当Drained。

无参数Owner仍完整工作台结果/工具/只读Inspector投影，参数编辑禁用并说明未连接；编辑型HostU必须提供ParameterUiOwner，不以只读页代替可编辑资格。Source/Viewport Context实际由§A.6公开Owner资产提供，不能从薄SourceBinding生成缺字段ViewportContext。本轮双STA Replay规格覆盖本模块UIroot/键盘/三语/生命周期，原PublicOwner工厂接线已定义，真实上游编译/控件/渲染与source消费者分别后验。


### A.8 双无UI、双STA Host与离栈反例

本节代码是按目标公开签名可构造的Host规格，尚未建工程/编译；测试夹具只在§3.1唯一Core.Tests/Wpf.Tests，真实计量走A2，不能把Replay固定量称算法/现场测值。以下具名fixture声明及行为是实现测试夹具的完整消费合同，不成为产品默认backend或另一个活动文档。

~~~csharp
// Core.Tests namespace；全部BCL，fixture显式取得完整Plan/Context/Profile。
public enum ReplayFailure { None, InputUnavailable, IgnoresCancel, ReleaseUnknown, MutationUnknown }
public sealed record ReplayFixtureOptions(MeasurementPlan Plan, double FixedValueMm,
    ReplayFailure Failure);
public sealed class ReplayWorkbenchFixture {
    public ReplayWorkbenchFixture(ReplayFixtureOptions options, TimeProvider timeProvider);
    public WorkbenchPorts Ports { get; }
    public int MeasurementStarts { get; }
    public int Saves { get; }
    public int Queries { get; }
    public void AllowExit();
    public void AllowRelease();
}
~~~

| fixture成员/端口 | 有限确定行为/完整输出 |
|---|---|
| constructor | 校验Replay Plan/finite值，不开后台；创建10个端口实例（可同fixture实现上述接口），Ports完整，独立计数/CTS/job字典，不static |
| Probe | 返回Tools=[options.Plan.Tool]、ModuleVersion=replay/1、AdapterVersion=fixture/1、全部编辑/建议/link为false、Checkpoint/Export=true；无UI/HALCON |
| Source/Coordinate/Validate | 与options.Plan完整Source/Coordinates/template逐值相等才输出SourceScope(Binding,BorrowId=JobId)/CoordinateReceipt(原Binding,原Mapping)/PlanValidationReceipt(原Plan,MethodProfile)；不执行坐标算法，不升资格。InputUnavailable使source失败且零MeasurementStarts |
| Measure | 每新call.Key计Starts一次；输出固定量CandidateId=replay、Key=Distance、Scalar(options.FixedValueMm)、Mm、Validity.Valid、Support/Uncertainty=null，Outcome.Measured/Scope=MeasureScope.Engineering；OriginalResult=(replay,result.<operation-guid-N>,1,WorkbenchCanonical.HashReplayResultContent的规范摘要)，Evidence=[]，Fingerprint同内容hash。完整输入/Key不匹配拒绝，不算法求值 |
| Compare | 同tool定义、template/source/坐标/参数/ROI为SameInputs；quantity按candidate/key/unit配，两侧原投影；不同字段写Differences，不做几何差值 |
| ROI/PE/Link | return失败Unsupported的已Exited job；不假装完整上游算法已运行 |
| Store/Evidence Save | 明确CAS：首次目标ExpectedRevision=0成功，SavedAsset以Destination.Owner/Id、Revision=1及Mutation canonical hash；原key同payload返回原receipt，异payload冲突；每首次Save计Saves一次。MutationUnknown把State=Unknown，原jobExited/Released，StartQuery同原request才计Queries并返回Succeeded同SavedAsset |
| Read checkpoint | 仅返回本fixture由StartSave已保存的原Checkpoint；未知资产InputUnavailable，绝不自动造最新 |
| job生命周期 | 正常GetOutcome立即，Query=Exited；Release一次后Released；IgnoresCancel/ReleaseUnknown以异步TCS闩锁分别保持Running/ReleaseUnknown，不阻塞线程，AllowExit/AllowRelease只推进原job，RequestCancel仅标记，永不创建第二release Task |
| 授权 | View/Execute/Compare/Save/Export允许、Invalidated=None、Utc截止=TimeProvider.GetUtcNow()+软件fixture24h；编辑拒绝。另测试用可撤权policy回CancellationTokenSource且不共享两Host |

空Host构造（H1/H2同一段调用两次，所有输入可定位，未使用未声明profile/source/helper）。SHA256这里只为具名合成输入资产标签，Replay reader登记这些完整字段；不是metrology/ROI真实payload canonical。请求身份仍必须用A.9 Canonical工具计算和完整payload重核。

~~~csharp
// Core.Tests: 显式BCL合成数据构造，函数本身就是唯一Host装配示例。
static (IMeasurementWorkbenchRoot Root, IMeasurementWorkbenchSession Session,
    IRootReservation Reservation, ReplayWorkbenchFixture Fixture, WorkbenchContext Context,
    MeasurementPlan Plan) BuildReplayHost(
        string marker, double valueMm, ReplayFailure failure, WorkbenchRecoveryDepot depot)
{
    AssetRef Asset(string id) => new("replay",marker+"."+id,1,
        Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(
            System.Text.Encoding.UTF8.GetBytes(marker+"."+id))).ToLowerInvariant());
    var profile = new ResourceProfile(marker,1,4,32,64,128,32,2,4,16,4096,
        1L<<20,1L<<20,16L<<20,64L<<20,0,0,32,
        TimeSpan.FromSeconds(1),TimeSpan.FromSeconds(1));
    var reservationResult=depot.Reserve(new RootReservationRequest(marker,profile.MaxRetainedBytes));
    if(!reservationResult.Succeeded) throw new InvalidOperationException("Reserve failed");
    var reservation=reservationResult.Value!;
    var id=new WorkbenchSessionId(Guid.NewGuid());
    var frame=new CoordinateRef(Asset("frame"),UnitCode.Mm,AxisConvention.RightHandedXY,null);
    var source=new SourceBinding("subject","Subject",Asset("points"),
        new ContractRef("replay.geometry","1"),SourceKind.Geometry,frame,
        new SupportDomainRef(SupportStatus.NotProvided,null,null,null,null),
        0,0,2,SamplingKind.Original,0,1,1,null,null);
    var coordinates=new CoordinateBinding(frame.Frame,frame.Frame,Asset("identity"),
        null,null,UnitCode.Mm,AxisConvention.RightHandedXY);
    var tool=new ToolDescriptor("replay.distance","1",MeasurementContract.Replay,
        Asset("profile"),new ContractRef("replay.profile","1"),
        ImmutableArray.Create(SourceKind.Geometry),ImmutableArray.Create("subject"),
        null,1,"workbench.distance","workbench.distance.help");
    var templateKey=new OperationKey(new OperationId(Guid.NewGuid()),new AttemptId(Guid.NewGuid()));
    var plan=new MeasurementPlan(tool,Asset("template"),new ContractRef("replay.request","1"),
        templateKey,ImmutableArray.Create(source),coordinates,null,null,null);
    var context=new WorkbenchContext(id,ImmutableArray.Create(source),frame,"replay-access-1",
        ImmutableArray.Create(new ContractRef("replay.geometry","1"),
            new ContractRef("replay.profile","1"),new ContractRef("replay.request","1")));
    var fixture=new ReplayWorkbenchFixture(new ReplayFixtureOptions(plan,valueMm,failure),TimeProvider.System);
    var root=new MeasurementWorkbenchFactory().CreateRoot(reservation,
        new RootOptions(marker,marker,2,profile),fixture.Ports,TimeProvider.System);
    var session=root.Create(new SessionOptions(id,SessionMode.EngineeringEditable));
    return (root,session,reservation,fixture,context,plan);
}
~~~

Host进程入口强持depot，不从Run里创建后丢失。下面完整有界正常/超时路径，业务和清理错误分别汇总；所有Task返回到depot预留槽，局部栈结束仍保Root：

~~~csharp
static async Task<int> ExerciseReplayAsync(
    (IMeasurementWorkbenchRoot Root, IMeasurementWorkbenchSession Session,
     IRootReservation Reservation, ReplayWorkbenchFixture Fixture,
     WorkbenchContext Context, MeasurementPlan Plan) h,
    WorkbenchRecoveryDepot owner, WorkbenchRecoveryDepot recovery)
{
    int code=0;
    try {
        var attach=await h.Session.AttachAsync(h.Context,TimeSpan.FromSeconds(1),CancellationToken.None);
        if(!attach.Attached) throw new InvalidOperationException("Attach");
        var current=h.Session.Read();
        if(!current.Succeeded) throw new InvalidOperationException("Read");
        var epoch=current.Value!.Epoch;
        var draft=h.Session.SetDraft(h.Plan,epoch);
        if(!draft.Succeeded) throw new InvalidOperationException("Draft");
        var key=new OperationKey(new OperationId(Guid.NewGuid()),new AttemptId(Guid.NewGuid()));
        var request=new ExecuteRequest(key,epoch,h.Plan,TimeSpan.FromSeconds(1));
        var first=h.Session.Execute(request,CancellationToken.None);
        var replay=h.Session.Execute(request,CancellationToken.None);
        if(!first.Accepted || !replay.Accepted) throw new InvalidOperationException("Accept");
        var one=await h.Session.WaitOperationAsync(key,TimeSpan.FromSeconds(2),CancellationToken.None);
        if(!one.Succeeded || one.Value!.Phase!=OperationPhase.Completed ||
           !one.Value.ResourcesReleased || h.Fixture.MeasurementStarts!=1)
            throw new InvalidOperationException("Completion/idempotency");
        var next=new OperationKey(new OperationId(Guid.NewGuid()),new AttemptId(Guid.NewGuid()));
        var rerun=h.Session.Recompute(new RecomputeRequest(next,epoch,key,
            RecomputePolicy.SameInputs,null,TimeSpan.FromSeconds(1)),CancellationToken.None);
        if(!rerun.Accepted) throw new InvalidOperationException("Recompute");
        var two=await h.Session.WaitOperationAsync(next,TimeSpan.FromSeconds(2),CancellationToken.None);
        if(!two.Succeeded || !two.Value!.ResourcesReleased) throw new InvalidOperationException("Second");
        var compareKey=new OperationKey(new OperationId(Guid.NewGuid()),new AttemptId(Guid.NewGuid()));
        h.Session.Compare(new CompareRequest(compareKey,epoch,key,next,TimeSpan.FromSeconds(1)),
            CancellationToken.None);
        var cmp=await h.Session.WaitOperationAsync(compareKey,TimeSpan.FromSeconds(2),CancellationToken.None);
        if(!cmp.Succeeded || cmp.Value!.Result is not ComparisonPayload cp ||
           !cp.Value.SameInputs || !cp.Value.SameDefinition) throw new InvalidOperationException("Compare");
        var checkpoint=h.Session.ExportCheckpoint();
        if(!checkpoint.Succeeded) throw new InvalidOperationException("Checkpoint");
        var saveKey=new OperationKey(new OperationId(Guid.NewGuid()),new AttemptId(Guid.NewGuid()));
        var destination=new AssetRef("replay","checkpoint",1,new string('d',64));
        var mutation=new MutationRequest(saveKey,SaveKind.Checkpoint,destination,0,
            checkpoint.Value!,ImmutableArray<AssetRef>.Empty,null);
        var saved=h.Session.Save(new SaveRequest(mutation,epoch,TimeSpan.FromSeconds(1)),
            CancellationToken.None);
        if(!saved.Succeeded) throw new InvalidOperationException("Save accepted");
        var savedOperation=await h.Session.WaitOperationAsync(saveKey,TimeSpan.FromSeconds(2),CancellationToken.None);
        if(!savedOperation.Succeeded || !savedOperation.Value!.ResourcesReleased)
            throw new InvalidOperationException("Save resources");
    } catch(Exception) { code=1; }
    // 不在try return；cleanup失败单独合并，不覆盖原业务原因。
    using var cleanupCts=new CancellationTokenSource(TimeSpan.FromSeconds(2));
    try {
        var close=await h.Root.CloseAsync(TimeSpan.FromSeconds(1),cleanupCts.Token);
        if(!close.Closed) code=Math.Max(code,2);
    } catch(Exception) { code=Math.Max(code,2); }
    if(h.Root.Query().AdmissionClosed && h.Root.Query().PendingJobs.Length==0) {
        var release=owner.ReleaseClosed(h.Reservation);
        if(!release.Succeeded) code=Math.Max(code,2);
    }
    // 还在root/host/UI中使用的资源，不凭Close包装Task完成清掉depot。
    if(!owner.ReleaseClosed(h.Reservation).Succeeded) {
        var offer=owner.OfferTransfer(h.Reservation,recovery.Read().DepotId);
        if(offer.Succeeded) {
            var acceptance=recovery.AcceptTransfer(offer.Value!);
            if(!acceptance.Succeeded ||
               !owner.ConfirmTransfer(h.Reservation,acceptance.Value!).Succeeded)
                code=Math.Max(code,3);
        } else code=Math.Max(code,3);
    }
    return code;
}
// 进程入口变量在两个Host及全部recovery观察完成前始终存活。
// release成功后的再次ReleaseClosed必须同reservation幂等，不能变“找不到所以成功”。
var owner=new WorkbenchRecoveryDepot(new DepotOptions("host-owner",4,16,64L<<20,
    TimeSpan.FromSeconds(1)),TimeProvider.System);
var recovery=new WorkbenchRecoveryDepot(new DepotOptions("host-recovery",4,16,64L<<20,
    TimeSpan.FromSeconds(1)),TimeProvider.System);
var a=BuildReplayHost("A",3,ReplayFailure.None,owner);
var b=BuildReplayHost("B",4,ReplayFailure.None,owner);
var slotA=((IWorkbenchHostTaskAdmission)owner).ReserveHostTask(a.Reservation);
var slotB=((IWorkbenchHostTaskAdmission)owner).ReserveHostTask(b.Reservation);
if(!slotA.Succeeded || !slotB.Succeeded) throw new InvalidOperationException("Host task budget");
int codeA=-1, codeB=-1;
var taskA=slotA.Value!.Start(async()=> { codeA=await ExerciseReplayAsync(a,owner,recovery); });
var taskB=slotB.Value!.Start(async()=> { codeB=await ExerciseReplayAsync(b,owner,recovery); });
await Task.WhenAll(taskA,taskB).WaitAsync(TimeSpan.FromSeconds(12));
await owner.ObserveAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
await recovery.ObserveAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
int finalCode=(codeA==0 && codeB==0)?0:1;
foreach(var retained in recovery.Read().Retained) {
    var held=recovery.GetReservation(retained.ReservationId);
    if(!held.Succeeded || !recovery.ReleaseClosed(held.Value!).Succeeded) finalCode=2;
}
if(owner.Read().Roots!=0 || recovery.Read().Roots!=0) finalCode=2;
// 测试入口最后才return finalCode；非零/在途均不得PASS。
~~~

上例HostTask内部ReleaseClosed会因自身host task尚未退出而保留，因此转交正确，但目标仍须入口在taskA/taskB退出后ReleaseClosed目标reservation，不能以Observe成功就取消强持。更简洁正常Host可把ReleaseClosed搬到入口after WhenAll；本页保留内部失败路径专门检验不自等待/不提前放槽。TransferAcceptance的TargetReservationId可用recovery.Query回取retention，但ReleaseClosed目标reservation需公开GetReservation(Guid)→WbResult<IRootReservation>（同depot真实capability，只同进程，不重建record）。入口按recovery.Read().Retained逐项GetReservation→ReleaseClosed；未成功保其Owned、报告非零。转交成功不是测试pass、资源已释放或进程可退出的证据。

纯异常Host反例（T11/T15）：A改IgnoresCancel，Execute后RequestCancel(User)→WaitOperation观察到期→root.Close.Closed=false、depot原引用仍Owned；保持B正常完成；A业务方法离栈后入口从TransferAcceptance取同root，调用原fixture.AllowExit/AllowRelease；Observe原job再Close→ReleaseClosed。Source晚到成功、release故障、异常路径都有相同原任务转交，不新Acquire/不新release。测试超时返回非零，外层有限子进程kill也非通过。

双STA只在Wpf.Tests/桌面TestHost，固定1920×1080物理screen基线在同一观察窗口同时摆窗。测试夹具公开ReplayUiChildrenFactory(string marker)实现A.7 StartMount：在当前Dispatcher造一个真实Border/MainSurface（标题“回放/回放/Replay”+已给原数量投影）、可选只读Grid Inspector，稳定marker ID；支持真实键盘/焦点、局部三语和闩锁晚Mount/Detach，保原Dispatcher task。它不是bitmap/HALCON/viewport算法资格。编辑型PublicOwner UI另使用A.7完整constructor，把原上游UI实参逐项注入后验，未通过不得以Replay代替。

~~~csharp
// Wpf.Tests：这个fixture唯一公开构造与接口，所有行为按上段冻结。
public sealed class ReplayUiChildrenFactory : IWorkbenchUiChildrenFactory {
    public ReplayUiChildrenFactory(string marker);
    public void AllowMount(); public void AllowDetach();
}
static Task<UiReceipt> StartSta(
    IMeasurementWorkbenchRoot root, IMeasurementWorkbenchSession session,
    string marker, WorkbenchRecoveryDepot processOwner, IRootReservation reservation,
    out Thread staThread)
{
    var result=new TaskCompletionSource<UiReceipt>(TaskCreationOptions.RunContinuationsAsynchronously);
    var admission=(IWorkbenchHostTaskAdmission)processOwner;
    var threadSlot=admission.ReserveHostTask(reservation);
    var callbackSlot=admission.ReserveHostTask(reservation);
    var outerSlot=admission.ReserveHostTask(reservation);
    if(!threadSlot.Succeeded || !callbackSlot.Succeeded || !outerSlot.Succeeded)
        throw new InvalidOperationException("STA task budget");
    threadSlot.Value!.Start(()=>result.Task); // 原thread退出回执任务，派发前strong hold。
    staThread=new Thread(()=> {
        UiReceipt? completed=null;
        Exception? businessError=null;
        try {
            var dispatcher=System.Windows.Threading.Dispatcher.CurrentDispatcher;
            var uiRoot=new MeasurementWorkbenchUiRoot(root,new UiRootOptions(
                marker+".ui",1,16,4L<<20,TimeSpan.FromSeconds(1)));
            var control=new MeasurementWorkbenchControl();
            var window=new System.Windows.Window {
                Width=1600,Height=900,Title="测量",Content=control };
            Func<Task> run=async()=> {
                try {
                    var resources=new DefaultWorkbenchTextResources();
                    var children=new ReplayUiChildrenFactory(marker);
                    children.AllowMount(); children.AllowDetach();
                    var mount=await control.MountAsync(uiRoot,session,
                        new WorkbenchMountOptions(marker,marker),
                        new WorkbenchPresentation("zh-CN","zh-CN","Office2019Colorful",1),
                        resources,children,TimeSpan.FromSeconds(1),CancellationToken.None);
                    if(!mount.Succeeded) throw new InvalidOperationException("Mount");
                    window.Show();
                    var tw=await control.SetPresentationAsync(
                        new WorkbenchPresentation("zh-TW","zh-TW","Office2019Colorful",2),
                        TimeSpan.FromSeconds(1),CancellationToken.None);
                    if(!tw.Succeeded) throw new InvalidOperationException("zh-TW");
                    window.Title="量測";
                    var en=await control.SetPresentationAsync(
                        new WorkbenchPresentation("en-US","en-US","Office2019Colorful",3),
                        TimeSpan.FromSeconds(1),CancellationToken.None);
                    if(!en.Succeeded) throw new InvalidOperationException("en-US");
                    window.Title="Measurement";
                } catch(Exception e) { businessError=e; }
                // 独立cleanup期限，不链接用户operation token。
                using var cleanup=new CancellationTokenSource(TimeSpan.FromSeconds(2));
                try {
                    completed=await control.DetachAsync(TimeSpan.FromSeconds(1),cleanup.Token);
                    var drained=await uiRoot.ObserveAsync(TimeSpan.FromSeconds(1),cleanup.Token);
                    if(completed.Drained && drained.Drained) {
                        window.Close();
                        dispatcher.BeginInvokeShutdown(
                            System.Windows.Threading.DispatcherPriority.Background);
                    }
                    // 否则Dispatcher继续Run；TCS未完成，root/depot保UI owner和原Task。
                } catch(Exception e) {
                    businessError??=e; // 清理原因仍由uiRoot.Query保存，不覆盖原错误。
                }
            };
            // 先在真实 STA Dispatcher 上取得唯一原 DispatcherOperation，再把其
            // Task 注册到两个独立的 Host 槽；这样 callback/outer 派发没有空引用竞态，
            // 也不会用一个尚未开始的包装 Task 冒充 Dispatcher 的原任务。
            var originalDispatch=dispatcher.InvokeAsync(run); // Func<Task>，禁止async void。
            var actualCallback=callbackSlot.Value!.Start(()=>
                originalDispatch.Task.Unwrap()); // 原inner Task由Unwrap及UIroot引用链保留。
            outerSlot.Value!.Start(()=>originalDispatch.Task); // 原DispatcherOperation.Task。
            System.Windows.Threading.Dispatcher.Run();
            // Run退出才形成thread结果；Async回调/Dispatcher不得未结束就伪完成。
            if(!actualCallback.IsCompleted || completed is null || !completed.Drained)
                result.TrySetException(new InvalidOperationException("STA cleanup incomplete"));
            else if(businessError is not null) result.TrySetException(businessError);
            else if(actualCallback.IsFaulted) result.TrySetException(actualCallback.Exception!);
            else result.TrySetResult(completed);
        } catch(Exception e) { result.TrySetException(e); }
    });
    staThread.IsBackground=true;
    staThread.SetApartmentState(ApartmentState.STA);
    staThread.Start();
    return result.Task;
}
// 桌面入口单独建新root；不能使用上面ExerciseReplay已关闭的a/b。
var staA=BuildReplayHost("STA-A",3,ReplayFailure.None,owner);
var staB=BuildReplayHost("STA-B",4,ReplayFailure.None,owner);
if(ReferenceEquals(staA.Root,staB.Root) || ReferenceEquals(staA.Session,staB.Session) ||
   ReferenceEquals(staA.Fixture.Ports,staB.Fixture.Ports) ||
   staA.Context.SessionId.Equals(staB.Context.SessionId))
    throw new InvalidOperationException("STA roots/providers are not isolated");
var attachA=await staA.Session.AttachAsync(staA.Context,TimeSpan.FromSeconds(1),CancellationToken.None);
var attachB=await staB.Session.AttachAsync(staB.Context,TimeSpan.FromSeconds(1),CancellationToken.None);
if(!attachA.Attached || !attachB.Attached) throw new InvalidOperationException("STA Attach");
// 两个 Dispatcher 在同一观察窗口内启动，验证关闭/语言/资源不会串到另一实例。
var uiTaskA=StartSta(staA.Root,staA.Session,"STA-A",owner,staA.Reservation,out var threadA);
var uiTaskB=StartSta(staB.Root,staB.Session,"STA-B",owner,staB.Reservation,out var threadB);
var uiFailure=0;
try {
    await Task.WhenAll(
        uiTaskA.WaitAsync(TimeSpan.FromSeconds(8)),
        uiTaskB.WaitAsync(TimeSpan.FromSeconds(8)));
    if(!threadA.Join(TimeSpan.FromSeconds(1)) || !threadB.Join(TimeSpan.FromSeconds(1)))
        throw new InvalidOperationException("STA thread");
} catch(Exception) {
    uiFailure=1;
    // 超时/异常时不调用Close或ReleaseClosed：两个原thread、Dispatcher、child
    // 和迟到结果仍由source depot强持，然后用同一进程的Proof确认转交。
    foreach(var pending in new[] { staA.Reservation, staB.Reservation }) {
        var state=owner.Query(pending.ReservationId);
        if(state.Succeeded && state.Value!.State==RetentionState.Released) continue;
        var offer=owner.OfferTransfer(pending,recovery.Read().DepotId);
        if(!offer.Succeeded) { uiFailure=2; continue; }
        var acceptance=recovery.AcceptTransfer(offer.Value!);
        if(!acceptance.Succeeded ||
           !owner.ConfirmTransfer(pending,acceptance.Value!).Succeeded)
            uiFailure=3;
    }
}
if(uiFailure==0) {
    try {
        var closedA=await staA.Root.CloseAsync(TimeSpan.FromSeconds(1),CancellationToken.None);
        var closedB=await staB.Root.CloseAsync(TimeSpan.FromSeconds(1),CancellationToken.None);
        if(!closedA.Closed || !closedB.Closed ||
           !owner.ReleaseClosed(staA.Reservation).Succeeded ||
           !owner.ReleaseClosed(staB.Reservation).Succeeded)
            throw new InvalidOperationException("STA Root cleanup");
    } catch(Exception) {
        uiFailure=4;
        foreach(var pending in new[] { staA.Reservation, staB.Reservation }) {
            var state=owner.Query(pending.ReservationId);
            if(state.Succeeded && state.Value!.State==RetentionState.Released) continue;
            var offer=owner.OfferTransfer(pending,recovery.Read().DepotId);
            if(!offer.Succeeded) { uiFailure=5; continue; }
            var acceptance=recovery.AcceptTransfer(offer.Value!);
            if(!acceptance.Succeeded ||
               !owner.ConfirmTransfer(pending,acceptance.Value!).Succeeded)
                uiFailure=5;
        }
    }
}
if(uiFailure!=0) throw new InvalidOperationException("STA cleanup/transfer incomplete");

~~~

Dispatcher.InvokeAsync的原DispatcherOperation.Task及Func<Task>委托的实际内部Task由预留Host槽登记，control内部任务另由UiRoot登记，不能只跟踪outer的Task<Task>。StartSta例的入口需要对原thread加入一个有限Join观察（最多相同8s），Join失败非零且root/depot保留；后台thread标志只是进程退出策略，不是释放证据。真实1920×1080扣除任务栏等按§7计算，不运行其它resolution，截图不替代UIA/资源断言。两STA使用独立root/session/provider/Dispatcher，关A不动B；晚Mount/关Dispatcher故障持续保原UI槽等待可恢复收尾。

测试命令仍为§9.2指定Core build/run；UI工程为net10.0-windows/UseWPF/OutputType=Exe、同样fail/nonzero契约，run指定唯一Wpf.Tests.csproj -c Release且先build它的所有受测依赖；不只build Core后--no-build跑从未build的Tests。本轮这些工程、Host、Golden C#断言没有执行。


### A.9 Canonical、独立Golden与BenchmarkPlan

~~~csharp
public sealed record WorkloadProfile(ImmutableArray<AssetRef> Inputs,
    ImmutableArray<ContractRef> Versions, int Width, int Height, long Points,
    long Faces, int RoiNodes, int RoiVertices, int RoiHoles, int Parameters,
    int ResultItems, int TileSize, int Levels, int Sessions, int Operations,
    int Subscribers, int EventsPerRead, long SaveBytes, string InteractionMode);
public sealed record PerformanceTargets(TimeSpan? MaximumP95,
    TimeSpan? MaximumP99, TimeSpan? MaximumCancelToReleased,
    long? MaximumManagedBytes, long? MaximumNativeBytes, long? MaximumGpuBytes,
    TimeSpan? LongRunDuration, AssetRef? Authority);
public sealed record BenchmarkPlan(string PlanId, WorkloadProfile Workload,
    ResourceProfile Resources, int WarmupRuns, int MeasurementRuns,
    int MinimumCompleteSamples, bool Cold, TimeSpan ObservationDeadline,
    PerformanceTargets Targets, string EnvironmentDescription);
public static class WorkbenchCanonical {
    public static byte[] EncodePlan(MeasurementPlan plan);
    public static byte[] EncodeExecute(ExecuteRequest request);
    public static byte[] EncodeEdit(EditRequest request);
    public static byte[] EncodeLink(LinkRequest request);
    public static byte[] EncodeCompare(CompareRequest request);
    public static byte[] EncodeRestore(RestoreRequest request);
    public static byte[] EncodeRecompute(RecomputeRequest request);
    public static byte[] EncodeProfile(ResourceProfile profile);
    public static byte[] EncodeMutation(MutationRequest request);
    public static byte[] EncodeCheckpoint(CheckpointAsset checkpoint);
    public static string Sha256(ReadOnlySpan<byte> bytes);
    public static string HashReplayResultContent(OperationKey key, double fixedValueMm,
        MeasurementPlan plan);
}
~~~

身份编码固定WB-TLV-3，域分别mwb-plan-v3/mwb-execute-v3/mwb-recompute-v3/mwb-profile-v3/mwb-mutation-v3/mwb-checkpoint-v3；Edit/Link/Compare/Restore分别mwb-edit-v3/mwb-link-v3/mwb-compare-v3/mwb-restore-v3；域也是UTF-8长度前缀字符串。记录逐声明字段序递归，不加record名或隐含字段；union MeasureValue/OperationPayload先字符串叶类型名再字段，未知case拒绝。嵌套record按字段递归不加其独立域前缀；EncodeExecute内Plan不另调用EncodePlan，独立EncodePlan才带mwb-plan-v3。非空string为uint32 LE字节长度+严格UTF-8，不BOM/换行，不替换无效Unicode；int32/int64/uint64固定little-endian；bool单字节0/1；Guid用16字节RFC4122/network顺序（Guid.TryWriteBytes(bigEndian:true)），不Guid默认混合端序。enum按声明大小写名称作为string；TimeSpan为int64 ticks；double为IEEE64 LE，finite前检，-0归+0；可空值/引用存在位0/1+非null内容；非可空record不写存在位。ImmutableArray先uint32数量后按原顺序写全字段；键值args按原名字Ordinal排序，重复拒绝，其余全部数组不排序/不删重复观测。Epoch等值包装只写其值；AssetRef Owner/Id/Revision/Sha256全部编码，不把所有hash当可排除self字段。

仅MeasurementDraft自己的DraftHash不入其内容，Checkpoint没有自身hash字段；执行/重算包含完整Plan/Key/ExpectedEpoch/timeout，模板原key也入身份。profile全部字段入编码，不有额外ProfileSha256字段自循环。SourceSupport的资格引用、参数绑定、模板Contract/ROI/参数都入Plan，不能只hashInput list。AssetRef引用hash是被引用Owner原件身份，不由此编码替代上游原canonical。端口返回Plan逐字段闭合后再核哈希；Core原操作额外保存接受时Context/RootProfile完整值，ctx切换后原同request重放仍查原Context闭包，不重hash为当前Context。所有本模块hash是Sha256(对应Encode*)，不同域不共用digest；请求Record不让调用者自己报hash代替完整payload核查。

ReplayResultContent域mwb-replay-result-v3，按Key、固定double、uint32 Plan完整字节长度+EncodePlan写，不包括将要生成的OriginalResult.Sha256/ResultFingerprint（它们回填此内容hash）；此仅Replay fixture具名规范，不改原计量ResultFingerprint。泛UI/diagnostic的content不作为请求准入身份。

BenchmarkPlan WarmupRuns≥0、MeasurementRuns>0、MinimumCompleteSamples∈[1,MeasurementRuns]、ObservationDeadline>0；每负载尺寸计数有限且按源种类允许0。PerformanceTargets可空表示NotEvaluated，不自动填Profile执行预算当验收门；非空数有限非负（latency>0）且Authority必填。按§9.3和DEV-GOV-010唯一统计/删失口径执行，另记实际任务/lease/Dispatcher原Owner状态；失败不是成功样本被删，未知资源不判通过。

完整Execute Golden的输入如下，之后的hex/长度/hash按字段独立拼接，不调用WorkbenchCanonical。它消除Record数组引用比较、Guid端序、支持null、显式单位及scope身份的歧义；未来C#必须断言完整bytes/len/hash，不把产品Encode输出当自己的expected。软件例不赋客户精度/节拍或真实source资格：

- Key=(OperationId 11111111-1111-1111-1111-111111111111，AttemptId 22222222-2222-2222-2222-222222222222)，ExpectedEpoch=0，OperationTimeout=1秒。
- 每个资产AssetRef按(Owner=replay,Id=下列名字,Revision=1,Sha256=64个a)。Tool=(ToolId=replay.distance,ToolVersion=1,MeasurementContract=Replay,MethodProfile=profile,ProfileContract=(replay.profile,1),AllowedSources=[Geometry],OperandIds=[subject],ParameterSchema=null,MaximumCandidates=1,NameResourceKey=distance,HelpResourceKey=distance.help)。
- Template资产=request，RequestContract=(replay.request,1)，TemplateKey=(33333333-3333-3333-3333-333333333333,44444444-4444-4444-4444-444444444444)。
- Inputs恰一项：OperandId=subject，Role=Subject，Content=points，ContentContract=(replay.geometry,1)，Kind=Geometry，Coordinates=(Frame=frame,Unit=Mm,Axes=RightHandedXY,Calibration=null)，Support=(NotProvided,null,null,null,null)，Width=Height=0，Elements=2，Sampling=Original，Level=0，ScaleX=ScaleY=1，PositionErrorBound=null，SamplingReceipt=null。
- Coordinates=(SourceFrame=frame,TargetFrame=frame,Mapping=mapping,Calibration=null,ApplicabilityReceipt=null,TargetUnit=Mm,TargetAxes=RightHandedXY)；Roi、Parameters、ParameterProfileBinding全null。


完整域：Execute，**1098 bytes**；SHA-256：`71a129e3ff1ace2a4fa33abfeb980840c1b953264c606359a25515128219ffce`。

~~~text
0e0000006d77622d657865637574652d7633111111111111111111111111111111112222222222222222222222222222
222200000000000000000f0000007265706c61792e64697374616e63650100000031060000005265706c617906000000
7265706c61790700000070726f66696c6501000000000000004000000061616161616161616161616161616161616161
6161616161616161616161616161616161616161616161616161616161616161616161616161616161616161610e0000
007265706c61792e70726f66696c650100000031010000000800000047656f6d6574727901000000070000007375626a
65637400010000000800000064697374616e63650d00000064697374616e63652e68656c70060000007265706c617907
000000726571756573740100000000000000400000006161616161616161616161616161616161616161616161616161
61616161616161616161616161616161616161616161616161616161616161616161616161610e0000007265706c6179
2e7265717565737401000000313333333333333333333333333333333344444444444444444444444444444444010000
00070000007375626a656374070000005375626a656374060000007265706c617906000000706f696e74730100000000
000000400000006161616161616161616161616161616161616161616161616161616161616161616161616161616161
61616161616161616161616161616161616161616161610f0000007265706c61792e67656f6d65747279010000003108
00000047656f6d65747279060000007265706c6179050000006672616d65010000000000000040000000616161616161
616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161
61616161616161616161020000004d6d0d000000526967687448616e6465645859000b0000004e6f7450726f76696465
640000000000000000000000000200000000000000080000004f726967696e616c00000000000000000000f03f000000
000000f03f0000060000007265706c6179050000006672616d6501000000000000004000000061616161616161616161
616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161
616161616161060000007265706c6179050000006672616d650100000000000000400000006161616161616161616161
616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161
6161616161060000007265706c6179070000006d617070696e6701000000000000004000000061616161616161616161
616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161616161
6161616161610000020000004d6d0d000000526967687448616e64656458590000008096980000000000
~~~

独立字节重建仅证明本编码向量；未执行C# Encode/Golden。修改任一Operand角色/源域/Mapping/ExplicitPlan或Guid、timeout均应改变身份；换语言/viewport镜头不能改变该执行的原输入。

本轮A.4/A.5补充的接纳/收敛断言仍属同一契约：Save先以Mutation.Key保操作/查询墓碑、预留job和最大响应，按Kind派发唯一Port；接受后QueryOperation/WaitOperation可查同key的MutationPayload。Succeeded→Completed、Rejected→Rejected、Unknown→Unknown均只有job.Release实际确认后形成唯一终态；receipt先到而job还在Running/ReleaseUnknown时仅更新MutationSnapshot，不能虚填ResourcesReleased。ResolveQuery的key是新读操作，原Mutation仍保持原终态；以ReconciliationReceipt(OriginalKey,ResolvedReceipt)投影解释后续确认，不给原Key第二Terminal。当前Core程序员不得创建一条隐含Save后自动Execute的链。

源码首片工作顺序：实例接纳短锁→资源/权限与原意图冻结→worker在锁外依次端口→逻辑结果暂存→请求停止/原job退出→逆序Release→worker任务真实完成→root的有界完成观察生成ResourcesReleased/唯一终态。worker不能同步等待自己的终态或Root.Close；Root.Close也不等depot里的当前Host等待者。源Acquire晚到成功时必须仍持其job/额度并在收到真实SourceScope后顺序归还，不因撤权就丢出引用。任何token/观察超时不是原Task真实退出、返回lease或Dispatcher完成证据。

全模块验证中的准确剩余范围：C1/C2公开Core编排、Replay、Depot/Host、编码规格的六项文档条件已由主控接收为ModuleCoreImplementationReady；A1仅A.6明确公开值/原请求/原结果映射、U1仅公开装配与Owner恢复指导内容限定接收，未授A1/U1运行或整模块生产准入。本版新增A.10的A2固定工具接线及参数表示修订已在永久原会话完成限定内容审核；真实源/native lease、非规则场资格生产证据、现实Store/Evidence目标及外部产品交接仍按对应范围验收。ROI值运输和三种PE→Profile转换不再整项记为缺合同；未支持的命令/工具/单位/来源组合按A.10拒绝。真实WPF/上游编译、UIA/模板/呈现、算法Golden/性能/现场仍未验证；文档接收不等于实际build/run或生产资格。

### A.10 A2固定工具、值编码与真实来源消费（0.6.1修订；原会话限定内容审核完成）

本节只增量定义Adapters的三种工具转换和确定公开来源接线；不修改A.1–A.5、A.7–A.9的Core/Host/编码。复用已读[IM-062参数编辑器](../parameter-editor/DEVELOPMENT-GUIDE.md)§3–4/8、[IM-024 ROI](../roi-geometry/DEVELOPMENT-GUIDE.md)§8.2/A.1–A.3、[IM-031 surface-data](../surface-data/DEVELOPMENT-GUIDE.md)§2–3/15、[IM-035 reference-surface](../reference-surface/DEVELOPMENT-GUIDE.md)§4/6/8和[IM-036 metrology](../metrology/DEVELOPMENT-GUIDE.md)§11–16/19，按2026-10-11定向读取的形状消费。这些Core规格已接收；实际DLL/HALCON/native运行是后续验证，不将内部字段映射改称客户外门。

#### A.10.1 首版三个工具与完整基线来源

| ToolId / ToolVersion | Profile、模板、输入与输出 |
|---|---|
| `mwb.point-distance` / `1` | IM-036 v0.2 Method.PointDistance/Dimension.D2；Selector.Unique、CandidateId/Anchor=null、AngleMode.Directed2D、VolumeMode.NetMagnitude；Fit/Edge/Model=null、ProfileStations=Empty、ProfileDirection/MaxProfileHalfLengthMm=null；Support/PrimitiveFit3/Affine=null、SurfaceSign.Unsigned、RequireQuantitativeUncertainty=false。两个operand严格Subject、Reference，各GeometryPayload恰一个Point2，原SampleId保留，物理工程单位Mm；结果Distance/mm和原witness |
| `mwb.image-edge-pair` / `1` | IM-036 v0.2 ImageEdgePair2/D2；Selector从本节PE选择，CandidateId/Anchor=null；其余无关Definition字段同上。Edge非null且Rectangles非空，Fit/Model/Support/PrimitiveFit3/Affine=null，SurfaceSign.Unsigned、RequireQuantitativeUncertainty=false。Subject为原单通道Byte Image，SearchRoi为原Owner已冻结的RegionRuns；mm物理计算经原CoordinateBinding，image元数据仍Pixel/ColumnRowPixelCenters。结果Distance、Edges原像素/物理点及amplitude，HALCON运行门保留 |
| `mwb.field-distribution` / `1` | IM-036 v0.3 ContinuousMethod.SupportedField、MethodVersion=SupportedField/1；一个SourceBinding OperandId=`field`/Role=`Input`/Kind=ContinuousField3D，Content等于原ContinuousRequest.Input，TargetFrame/mm/右手XYZ精确相等。仅FieldInput，FieldModel.AffineTriangles或AffineTopMinusQuadratic，DomainPurpose.GeometricHeight；FieldOptions固定Integral=true、AreaMoments=false、PositiveVolumeCenter=false、EquivalentMomentEllipse=false；Coverage/Transform及单个CDF/概率由本节PE。结果FieldResult及原区间、E/U、证书；不解释材料分类或产品合格 |

所有Profile的ContractVersion/MethodVersion、Numeric/ExecutionBudget、输入/坐标/ROI、模板key和工具版本来自Host提供的**完整已冻结基线**；PointDistance/ImageEdgePair ContractVersion=0.2、MethodVersion分别PointDistance/1、ImageEdgePair2/1。未编辑的字段逐字段保原值，ExecutionBudget九字段（MaxInputElements/MaxPairChecks/MaxCandidates/MaxOutputSamples/MaxManagedBytes/MaxNativeBytes/MaxParallelism/ExecutionTimeout/DrainTimeout）不从PE改变；离散request.Definition/Budget必须等于新Profile对应字段，连续request没有Definition/Budget字段，只保原Method/Input/TargetFrame并替换Profile引用。工具注册时校验上述固定值，冲突Unsupported；不得把任意旧Profile当模板补默认。Scope本版固定Engineering，新工具/CalibratedPhysical/RequireQuantitativeUncertainty=true不由转换器提升资格。

ImageEdgePair的SearchRectangle Center/PhiRad/HalfLength1Px/HalfLength2Px及完整有效域来自原模板/显式ROI派生Asset，不在参数转换器计算、绘制或从UI矩形猜值；PhiRad无PE角字段。图像UInt16/Float32、显示LOD、InterpolatedDiagnostic、强行缩放pixel距离或不完整mask均Unsupported/Unqualified。SurfaceField工具不将HeightField/PointCloud/Mesh枚举改名为ContinuousField：先完成A.10.5–A.10.6的原Owner资产与支撑闭包。

#### A.10.2 PESchema、Full Patch与具名参数表示转换

Schema.Identity.Id固定为`mwb.<tool>.parameters`（其中tool取上表ToolId去掉mwb.），Identity.Version=`1`、CanonicalizationVersion=`pe-v2-tlv1`，Identity.Sha256用ParameterCanonical.EncodeSchema复算。每行ParameterDefinition字段固定：DisplayNameResourceKey=`workbench.<tool>.<key>.name`，DescriptionResourceKey末段help，CategoryResourceKey=`workbench.parameters`，Advanced=false，Required=true、Nullable=false、ReadOnly=false、ApplyMode.OwnerDefined，Text=null，VisibleWhen/EditableWhen=null，DefinitionVersion=`1`，SourceRef为精确原冻结Profile的ContentRef（Version保原Owner资产版本，不用PE Generation替代）。DefaultValue=null；初始值为原Profile对应值/Explicit，绝不将缺项改为0/default。其它未列参数没有Definition，导入未知key拒绝。三语分别用“点距/點距/Point distance”、“边距/邊距/Edge distance”、“场分布/場分布/Field distribution”，参数/错误/恢复全部资源键。

上表Required/ReadOnly适用于本次**实际进入Schema的定义**。先通过原Profile Validator，再按A.10.10逐numeric key求Baseline投影；合法原值返回ReadOnly时，该key确定性省略于本次Definitions和初始Snapshot，不建Required+Missing行、不放default或伪Decimal。工作台在Inspector旁的只读原值区保留key、原R文本/原bits、单位及不可编辑原因；Enum及其它可投影字段仍正常编辑。省略集由完整原Profile及固定规则计算并核hash，调用方不能任意删定义；Schema版本按本节保持，完整身份Sha256因实际定义集不同而不同，不复用全字段Schema hash。省略字段不可出现在Patch/建议Edits，转换时保原Profile bits。若全部字段省略，原PE空Schema合法，只查看、无绑定空Patch；原Plan仍可显式执行。非finite或原Validator不合法并不因省略获得执行资格。A.10.8工厂与BindingOwner都重算此集合；PE不负责显示被省略字段。

| 工具/Key | PE ValueType / Unit=DisplayUnit / Numeric / AllowedValues | 新Profile唯一目标与校验 |
|---|---|---|
| 点距 `length_tolerance` | Length / Millimetre / Minimum=(0,false)，Maximum/Step=null，StepOrigin=0；AllowedValues=Empty | ParameterValue.LengthMillimetres→Definition.Numeric.LengthTolerance；LengthUnit保持Mm；其它Numeric/Definition/Profile字段原样 |
| 边距 `sigma_px`（PE加法接收后） | Decimal / Pixel / Minimum=(0.4,true)，Maximum=(100,true)，Step=null，StepOrigin=0；AllowedValues=Empty | ParameterValue.Decimal→Definition.Edge.SigmaPx，经A.10.10具名表示转换；核decimal意图及输出binary64均满足上下界、输出sigma≤0.5×每个原Rectangle.HalfLength1Px。不限制整数、不以Int64替合法0.4/0.5；若宿主实际仍提供旧PE Schema Version=`1`，本字段不进入可编辑PE Schema，原sigma保bits只读，其它合法参数照常编辑 |
| 边距 `threshold` | Decimal / None / Minimum=(1,true)，Maximum=(255,true)，Step=null，StepOrigin=0 | Decimal→Edge.Threshold；这是Byte梯度门，不当灰度物理单位/客户公差 |
| 边距 `transition` | Enum / None / Numeric=null | Enum名称逐一映EdgeTransition.All/Positive/Negative/AllStrongest/PositiveStrongest/NegativeStrongest，AllowedValues恰这六项、Retired=false、各有name资源键 |
| 边距 `interpolation` | Enum / None / Numeric=null | Enum Nearest/Bilinear/Bicubic恰三项；有效mask及图像边距检查由原计量Owner，改变此值不擅改ROI |
| 边距 `selector` | Enum / None / Numeric=null | Enum Unique/All恰两项→Definition.Selector；NearestAnchor不在Schema，不能自动补anchor |
| 场 `coverage` | Enum / None / Numeric=null | FullTarget/KnownPartDiagnostic→FieldOptions.Coverage；选FullTarget仍须原域/资格充分，不增加支持 |
| 场 `transform` | Enum / None / Numeric=null | Signed/PositiveOnSameDomain→FieldOptions.Transform，只控制CDF/Quantile随机变量，不改Integral四量或域 |
| 场 `cdf_height` | Length / Millimetre / Minimum/Maximum/Step=null、StepOrigin=0 | LengthMillimetres→CdfHeightsMm=[value]；本工具只支持一个明确阈值，原数组不为恰1项则不注册此编辑工具 |
| 场 `probability` | Ratio / None / Minimum=(0,true)，Maximum=(1,true)，Step=null、StepOrigin=0 | ParameterValue.Ratio→Probabilities=[value]；显示None，不能以Percent字样二次除100；原数组必须恰1项 |

长度/threshold/ratio及获PE加法接收后的sigma使用A.10.10唯一`mwb.parameter.binary64/1`规则：原double以确定的shortest round-trip**数值**投影为decimal，复转bits一致才可编辑；新decimal意图按有界整数比较取最近finite binary64，半途tie取偶数。0.1/0.01/0.4/1e-9合法普通参数不因数学不完全相等拒绝。PE原decimal/Schema/Snapshot/Patch全保原；输出bits与准确有理表示误差写工程receipt，不把它当客户物理误差容限或改变计量阈值。未改字段保原bits；改值先核十进制目标边界，再核输出边界与原Validator，越界拒绝不clamp。极端原double没有可表示的shortest decimal值时仅该字段只读，原Profile可打开/查看，其它合法字段继续编辑；无零默认/自动舍入旧Profile。本版没有AngleDegrees→rad编辑路线，ParameterKey全部小写ASCII。Q单位/模型资格沿A.10.6原精确保真门，禁止套用本参数规则。

PE Decimal/Pixel 已按 IM-062 `0.2.2-prep` 接收，完整五项 EdgePair Schema 使用 Version=`2`；它只改变已接收的PE参数类型组合，不改变本模块的计量语义。工厂仍核新Schema/hash，并用新PE session/完整baseline承接，不在旧session更换Definition或伪造旧Patch。点距/场Schema Version=`1`保持，实际定义集按上段合法可投影字段重算完整hash；本转换版本由receipt/2及RuleRef绑定，不重算旧PE事实。若宿主实际仍提供旧Schema Version=`1`，只启用四项非sigma编辑，sigma按原Profile bits只读，不把PE-1007误报为参数值错误。

固定校验顺序：①核ToolId/Version/Schema全部定义/身份、基线Profile与模板hash；②核PE session.Id、Schema/ParameterAsset.EditorSessionId及当前Draft.Generation/hash；③CheckEdits Atomic→SetValues（以Assessment.ExpectedGeneration提交）→Validate Full；④CreatePatch(PatchOptions ExpectedGeneration=当前代、全新PE OperationId、IdempotencyKey为此次唯一意图、Scope=`mwb-engineering/<tool>`)。ValidatedPatch指这个原PatchIntent，不另造上游不存在的ValidatedPatch类型；验证SessionId、Before.Owner/Revision/hash、Proposed.Generation/hash、Changes四态、Validation.Schema/Generation/hash/Mode.Full/IsValid及RequestSha256=ParameterCanonical.EncodePatch规范摘要；⑤再读当前PE，逐字段匹配Proposed，变化即StaleBinding；⑥原基线调用MetrologyValidator/ContinuousMeasurements.Validate，再逐表转换并核单位、原基线固定字段和交叉约束；⑦Publisher预留新身份并构造新模板，按A.10.3对新请求/Profile及实际Field payload作原Validator校验后发布immutable Profile/完整模板/Parameters/binding receipt，重新读回校验再SetDraft。

点距Constraints=Empty；边距额外约束由转换器核每个原rectangle，PE Schema不能拿三角函数或外部IO表达式代替；场Constraints=Empty，原数值/域Validator负责完整关联。Changes至少一项，不接纳空Patch作为新发布；Missing/Null/Origin变化须原PE校验，任何本表Required被remove/null均拒绝。新Profile只用完整Proposed快照生成，不能只套Changes到“当前”Profile。Before.Owner精确等于原Profile引用；来源不匹配、PE schema换代、Recommendation基线过时均零发布。

建议消费原IParameterRecommendationProvider；本工具的具体来源是IM-036§13.3–13.4已给出的ReplayParameterRecommendationProvider，完整接线见A.11.4。request.Profile、Provider版本、plan/trials证据hash、Schema/草稿代次固定，MaximumCandidates和Timeout取Host明确预算；PE.RecommendAsync→GetOperation原ID且ResourcesReleased后用户显式AcceptSuggestion原candidate ID→重新走上述Full/Patch/新Profile链。候选超范围/输出表示越界直接拒绝，Abstained保原值。点距及场数值门不从数据自动放宽；没有匹配Provider/完整挑战集时推荐命令明确不可用，不伪造默认候选。AcceptSuggestion和Profile发布都不RequestApply，不修改产品配方或执行量测。

#### A.10.3 Adapters具体发布入口与receipt

以下增量声明位于Asun.Modules.MeasurementWorkbench.Adapters；只使用原PE/IM036具体值及已有MeasurementPlan，不新增Core DTO或替换A.6旧装配。每Host独立创建BindingOwner并在root派发前RegisterChildOwner；全部原读/发布job和临时请求纳其有界槽，根仍使用A.8两个depot/Root。

~~~csharp
public sealed record PointDistanceBindingInput(MeasurementPlan BaselinePlan,
    Asun.Metrology.Contracts.MethodProfile BaselineProfile,
    Asun.Metrology.Contracts.MetrologyRequest BaselineRequest,
    Asun.Modules.ParameterEditor.PatchIntent Patch, ParameterAsset Parameters);
public sealed record EdgePairBindingInput(MeasurementPlan BaselinePlan,
    Asun.Metrology.Contracts.MethodProfile BaselineProfile,
    Asun.Metrology.Contracts.MetrologyRequest BaselineRequest,
    Asun.Modules.ParameterEditor.PatchIntent Patch, ParameterAsset Parameters);
public sealed record FieldBindingInput(MeasurementPlan BaselinePlan,
    Asun.Metrology.Contracts.ContinuousProfile BaselineProfile,
    Asun.Metrology.Contracts.ContinuousRequest BaselineRequest,
    Asun.Metrology.Contracts.FieldInput Input,
    Asun.Modules.ParameterEditor.PatchIntent Patch, ParameterAsset Parameters);
public interface IWorkbenchToolProfilePublisher {
    IWorkbenchJob<MeasurementPlan> PublishPointDistance(PointDistanceBindingInput original,
        Asun.Metrology.Contracts.MethodProfile converted,
        WorkbenchParameterNumericConversions conversions,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<MeasurementPlan> PublishEdgePair(EdgePairBindingInput original,
        Asun.Metrology.Contracts.MethodProfile converted,
        WorkbenchParameterNumericConversions conversions,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<MeasurementPlan> PublishField(FieldBindingInput original,
        Asun.Metrology.Contracts.ContinuousProfile converted,
        WorkbenchParameterNumericConversions conversions,
        CallContext call, CancellationToken executionCancellation);
}
public sealed class WorkbenchToolBindingOwner : IWorkbenchChildOwner {
    public WorkbenchToolBindingOwner(IMeasurementWorkbenchRoot root, string ownerId,
        IMeasurementWorkbenchSession session, IWorkbenchAuthorizationPort authorization,
        Asun.Modules.ParameterEditor.IParameterEditorSession parameters,
        IWorkbenchOwnerAssets assets, IWorkbenchToolProfilePublisher publisher,
        ResourceProfile limits, TimeProvider timeProvider);
    public string OwnerId { get; }
    public void RequestClose();
    public ValueTask<DrainReceipt> ObserveAsync(TimeSpan budget, CancellationToken waitCancellation);
    public IWorkbenchJob<MeasurementPlan> StartPointDistance(PointDistanceBindingInput input,
        CallContext call, CancellationToken executionCancellation);
    public IWorkbenchJob<MeasurementPlan> StartEdgePair(EdgePairBindingInput input,
        CallContext call, CancellationToken executionCancellation);
    public IWorkbenchJob<MeasurementPlan> StartField(FieldBindingInput input,
        CallContext call, CancellationToken executionCancellation);
}
public static class WorkbenchToolBindingCanonical {
    public static string HashPointDistance(PointDistanceBindingInput input);
    public static string HashEdgePair(EdgePairBindingInput input);
    public static string HashField(FieldBindingInput input);
}
~~~

首次Schema只使用A.10.8的唯一纯工厂，先Schema/原PE Factory，再构造含真实Patch的BindingInput，禁止循环依赖或占位Patch。所有Start遵循A.3有限接纳/原任务/零副作用抛错规则；Schema/状态预检不合格返回已Exited失败job，未发布资产。

Publisher先在本工程发布组内预留新Profile/Template资产身份，再从original.BaselineRequest生成新模板，填预留新Profile的Id/Revision和converted canonical hash；转换Owner不预猜Publisher将分配的身份，不传入指向尚未分配资产的convertedTemplate。Publisher在任何可采用发布前调用原Asun.Metrology.Core.MetrologyValidator.Validate(newRequest,converted)，或ContinuousMeasurements.Validate(newRequest,converted,original.Input)；Errors非空不提交组。身份预留/失败保其原job记录，不自动重发/覆盖旧值。

BindingCanonical是Adapters纯值工具：WB-TLV-3域依次为`mwb-tool-bind-point/2`、`mwb-tool-bind-edge/2`、`mwb-tool-bind-field/2`，后先按A.10.10递归写固定RuleRef三字段，再按顺序写uint32长度+WorkbenchCanonical.EncodePlan(BaselinePlan)原bytes、原Profile canonical hash字符串、原Request canonical hash字符串、仅Field的ContinuousCanonical.HashInput字符串、uint32长度+原ParameterCanonical.EncodePatch bytes、原Patch.RequestSha256字符串、Parameters按A.9递归字段序。离散hash用Asun.Metrology.Core.MetrologyCanonical，连续用Asun.Metrology.Core.ContinuousCanonical；不得对任意显示JSON造hash。非法结构ArgumentException、超limits在Start零Publisher拒绝。call.RequestHash必须等对应Hash*；同Key重放还逐字段比完整输入，不用hash或record数组Equals替代。Publisher只接受对应Owner核过且converted、conversions及新template与原Proposed/初始baseline/具名RuleRef逐字段可复算相等的调用。

构造核session属于该root并同步登记child，借用session/PE/authorization不关闭。新Key接纳前session.Read核Active/SessionId/Epoch、原Plan输入与Context、call.Profile/AuthorizationRevision；以View+EditParameters及完整输入/Profile资产检查当前权限，PE仍核它自己的Edit权限。发布前再核权限/代次，Invalidated连到执行取消；撤权或换epoch后不发布新采纳值，已发生的工程追加保原事实并收尾。返回Plan由Host再次核当前PE代次/epoch后显式session.SetDraft(plan,call.Epoch)，Owner不隐藏调用SetDraft。既有Key先同payload回放原job，披露再核View，不因关闭/撤权重新Start。

Publisher是Host工程资产Owner：只追加工程immutable值，不CAS生产Profile指针/数据库/设备。新Profile Id/Revision由显式注入Owner分配且不覆盖旧资产；Sha256分别Asun.Metrology.Core.MetrologyCanonical.HashProfile或ContinuousCanonical.HashProfile，模板分别HashRequest；原Request.Key先保BaselineRequest.Key=BaselinePlan.TemplateKey，新请求模板仅改变Profile引用、Definition/Budget（离散）且逐值等于新Profile；连续保持Input/TargetFrame/Method/Scope，新的执行Key仍由A.4/A.6桥替换。ParameterAsset.Schema/Snapshot与原PE规范摘要、Generation精确一致；binding receipt的既有四字段为(本次Parameters,新MethodProfile,Receipt资产,Exact=true)；Exact表示新Profile bits逐项等于本次具名转换及未改位保留的确定结果，不表示decimal与binary64数学相等或物理精度获批。Receipt资产内容按WB-TLV-3独立域`mwb-tool-binding/2`依次编码：uint32长度+ParameterCanonical.EncodePatch原bytes、Patch.RequestSha256 string、ToolId string、ToolVersion string、原BaselinePlan.Tool.MethodProfile AssetRef、新Profile AssetRef、原BaselinePlan.RequestTemplate AssetRef、新Template AssetRef、本次ParameterAsset、WorkbenchParameterNumericConversions按A.10.10声明字段序递归编码；不在receipt内容嵌自身Receipt AssetRef产生循环，不重新发明PE编码。完整Patch含原Before/Proposed/Validation，并据原RequestSha256再复核。资产发布完整成功前不返回可执行Plan；部分发布保原job/已发布引用，失败不给Plan，孤立值只工程保留，不自动删除或生产采纳。

Publisher按call.SessionId/Key与完整original/converted payload保有界原记录：同Key同payload回原job/原分配资产，异payload IdentityConflict；不得观察到期重新分配revision或另Start。Parameters由Host为本次PE snapshot显式预留资产身份，Publisher在同一工程发布组内登记原Schema、完整Patch.Proposed、Profile、Template和receipt，读回一致才成功。新生成参数Profile不调用PE.AdoptAppliedBaseline或伪造ApplyReceipt；同一PE session继续编辑时始终从其**初始冻结BaselineProfile/Template**及完整Proposed重新转换，Before.Owner仍匹配原PE Baseline。若要将新Profile作为另一编辑基线，Host显式关闭/保留旧session并用新Schema/新Baseline创建新PE session，不自动重基或清Undo。本版不把连续Profile强行序列化成v0.2 MethodProfile。旧receipt/1及三种bind*/1只历史按原包规则查看，不按新规则重签或重新解释；新工程转换只生成receipt/2，Core API和四字段公开回执不改。

返回Plan的Tool仅替换MethodProfile、ProfileContract保原0.2/0.3、ParameterSchema精确为本次PE session使用的原Schema；同session不按新Profile重新生成Schema而改变SourceRef/草稿身份。Parameters/ParameterProfileBinding及RequestTemplate明确替换，Inputs/Coordinates/Roi保持原值。BindingOwner通过A.6 Assets读取新Profile/template/receipt再核hash、原完整值/参数Exact和当前PE代次，失败不SetDraft。旧Profile仍可用于旧SameInputs结果/重算；新转换不重写其闭包。Publisher签发可信receipt而非调用方自填Exact；Core依旧只消费原A.6 Port，不能以receipt自报获得物理资格。

#### A.10.4 ROI snapshot/command跨进程值封装与新进程接纳

snapshot直接调用已接收IRoiGeometryCodec.Encode/Decode，格式roi-json-v1/major1/minor0；Sha256核整个envelope，payloadHash单独核，Revision=0原样保留。Known DraftImport才可在目标Host新session.Open；ReadOnlyUnknown只历史查看/原bytes导出。工作台Checkpoint保存资产引用，不塞native、Undo栈或源会话期限。Codec实例/ValidationProfile由原Host明确提供，不把当前未编译当缺契约。

上游没有RoiEditRequest command codec；本模块提供**编辑值运输**而非远程执行/幂等续跑。封装`mwb-roi-edit-values/1`按UTF8无BOM固定JSON顺序：format,sourceOperationId,baseSnapshot,profileId,profileRevision,profileHash,mode,commands。baseSnapshot为roi-json-v1完整原envelope对象；commands保原顺序，每项首字段kind=create/replace/delete/transform/reparent/undo/redo，再依原声明字段序写node/nodeIds/transform/parentId/steps；Create/Replace node使用IM-024§8.2完全相同node/shape/constraint/source值规则，但它是command值，不能用孤立节点GeometryCodec.Encode绕过parent引用验证。Transform字段M11/M12/Tx/M21/M22/Ty首字母小写规则；所有null显式、数组非default、字符串与finite数字规则完全沿roi-json-v1。SourceOperationId保源原OperationId，仅追溯，不授远端幂等或授权。SessionId/Epoch/Stopwatch Deadline均**不写入值封装**，hash为完整原bytes，与目标进程完整RoiEditRequest身份分开；未知字段/case/version保原bytes只读，损坏拒绝。

| 原command | 本封装完整字段顺序（kind之后） |
|---|---|
| CreateCommand / ReplaceCommand | node；node完整id,parentId,zOrder,visible,locked,shape,constraints,source |
| DeleteCommand | nodeIds，保原次序 |
| TransformCommand | nodeIds,transform；transform=m11,m12,tx,m21,m22,ty |
| ReparentCommand | nodeIds,parentId；null表示原根级意图 |
| UndoCommand / RedoCommand | steps，原int32正整数 |

编码必须重新写baseSnapshot的已知v1规范envelope，不能把带空格或未知字段的原JSON片段拼入规范封装；其规范payloadHash与完整envelope hash分别核验。Decode先总bytes/UTF8/深度/重复字段/完整JSON前检，再识别版本；未知版本/字段不解析已知子集、不重编码未知bytes。已知格式除payloadHash外还要求按本规约重编码与整个输入逐字节相等，非规范字段顺序/空格拒绝InvalidRequest；enum mode仅原Apply/Preview。Commands恰1..profile.MaxNodes项，nodeIds每项非default/非空且不超MaxNodes，steps≤MaxUndoSteps；base与所有command值聚合统计nodes/vertices/rings/components/UTF8及工作字节，均受原ValidationProfile对应上限约束，不把每command单项限额当总限额。按CheckBatchSize检查localDeadline；不能把源deadline当本地计时器。

~~~csharp
public sealed record RoiEditValues(string SourceOperationId,
    Asun.Modules.RoiGeometry.GeometrySnapshot BaseSnapshot,
    string ProfileId, string ProfileRevision, string ProfileHash,
    Asun.Modules.RoiGeometry.RoiEditMode Mode,
    ImmutableArray<Asun.Modules.RoiGeometry.RoiEditCommand> Commands);
public sealed class WorkbenchRoiEditValueCodec {
    public WorkbenchRoiEditValueCodec(Asun.Modules.RoiGeometry.Serialization.IRoiGeometryCodec snapshots);
    public WbResult<ImmutableRoiEditBytes> Encode(RoiEditValues values,
        Asun.Modules.RoiGeometry.ValidationProfile profile,
        Asun.Modules.RoiGeometry.MonotonicDeadline localDeadline);
    public WbResult<RoiEditValues> Decode(ImmutableArray<byte> bytes,
        Asun.Modules.RoiGeometry.ValidationProfile profile,
        Asun.Modules.RoiGeometry.MonotonicDeadline localDeadline);
    public WbResult<Asun.Modules.RoiGeometry.RoiEditRequest> Bind(RoiEditValues values,
        Asun.Modules.RoiGeometry.RoiSessionSnapshot target,
        Asun.Modules.RoiGeometry.ValidationProfile profile, string newOperationId,
        Asun.Modules.RoiGeometry.MonotonicDeadline localDeadline);
}
public sealed record ImmutableRoiEditBytes(ImmutableArray<byte> Bytes, string Sha256);
~~~

Encode/Decode有界值操作消费MaxSerializedBytes/MaxJsonDepth/MaxNodes/MaxVertices/MaxRings/MaxComponents/MaxWorkingBytes/MaxOutputBytes及上述聚合限额、独立localDeadline；调用原snapshot codec后重核错误/格式/hash，不修改几何或自动Apply。Decode命令shape/约束只做有界值结构检查，最终拓扑/锁/历史语义由目标IRoiGeometryCore.Validate/Apply/Preview执行，不能运输成功就说编辑已合法。Unknown返回Unsupported且无RoiEditValues，原bytes由Host保留；不丢未知字段生成部分命令。Bind只构造原新请求，最终授权/当前会话核查仍在A.6派发前完成，不以绑定成功授予Apply。

Bind由Host显式调用，要求目标Open、目标Snapshot全部字段与BaseSnapshot相等、Profile.Id/Revision/Hash/Frame与原封装精确相等，newOperationId非空且与SourceOperationId不同；工作台完成当前View/EditRoi授权后，以target.SessionId/Epoch/Snapshot.Revision/ProfileRevision及Host当前Stopwatch建立的localDeadline创建**新**原RoiEditRequest。Commands/Mode完整保持，不改base revision、不延长原已接纳请求。源进程的旧Unknown/已Applied不能靠运输重新执行：Host原事务Owner先查询/确认原结果，未确认则只留只读draft；新进程本版Undo/Redo运输仅供历史展示，Bind返回Unsupported（目标Undo栈不与源相同），不能把steps在新会话无条件执行。Create/Replace/Delete/Transform/Reparent最终经A.6 Edit新Key、新UpstreamOperationId显式派发，原同进程ID重放规则不变。运输内容是值，没有把旧ROI会话迁移或旧期限复活。

编辑值编码固定向量`MWB-ROI-V01`（不含围栏和行尾换行）；profileHash仅SHA256(UTF8 `profile.vector/1`)的Synthetic标识，不提供完整Profile参数或执行资格。使用原RG-K03 revision0空base及Preview/Create Point(1,2)：

~~~json
{"format":"mwb-roi-edit-values/1","sourceOperationId":"source-op-1","baseSnapshot":{"format":"roi-json-v1","major":1,"minor":0,"payloadHash":"0aae522e5aa588fdc37e53d93bb346a34e970a24d27b442b29d638ac019ea35b","payload":{"documentId":"doc.vector","revision":0,"frame":{"id":"pixel.xy","unit":"Pixel","axisConvention":"ColumnRowPixelCenters"},"nodes":[]}},"profileId":"profile.vector","profileRevision":"1","profileHash":"be77d207330ec87b86076b3a026611832f974df5264d50ab5910b4e1259fe80b","mode":"Preview","commands":[{"kind":"create","node":{"id":"p1","parentId":null,"zOrder":0,"visible":true,"locked":false,"shape":{"kind":"point","center":{"x":1,"y":2}},"constraints":[],"source":null}}]}
~~~

完整封装UTF8无BOM为**688 bytes**，Sha256=`53c175db966d27aaa13ea21431e27371c2dda532c86a3d53823eaea23f30bd95`；内嵌base envelope为269 bytes、Sha256=`af00b9b22e6739b78a2cdbafdfbe8a2809b936b669be749233fedefe5b311713`，payload仍133 bytes/原RG-K03 hash。实现验证须从独立固定字节串重建并逐字段核查，不能由受测codec自身提供期望值。运输返回原SourceOperationId/全部node字段且不含Session/Epoch/deadline；Bind后新Request才含目标本地身份。此向量仅编码证据，不代表已执行编辑或上游编译。

#### A.10.5 C5多父来源：确切载体、Origin与读取链

工作台工程Surface→reference/field输入只接**显式原载体/原贡献表**。IM-031 Api0.4 ISurfaceDataService和Contribution Api0.1 IContributionReader按原Factory分别创建，参数/ResourceBudget由相应Host冻结，不能把C5版本写成0.4。SurfaceReadRequest Selection=PreserveAll、按Vertex Ordinal范围、ReadCoordinates=true；HeightField选原Height、PointCloud/Mesh选原X/Y/Z，合法Triangular Cells须原ROI/surface派生Owner已有连续证据，工作台不自动生成mesh。未知/无效点保原SampleState/Reason/SourceIndex，不能先ValidPositions删点后缩小分母。

对应ContributionReadRequest必须使用同Carrier.Key/全部Descriptor、同Vertex Domain、CarrierFieldId=null（Height或XYZ完整值），同Start/Count、明确Generation>0、PageCarrier/EntryLimit/MaxFanIn/MaxTotalEntries和Budget。字段单独属性支持、Face载体和XYZ不同实际Origin的组合本工具Unsupported，不能取一列/一个parent代替位置来源。Reader.Validate→Plan→Start；OnPage同步复制有界States/MethodIds/Offsets/Entries或原页证据引用，Span不能离回调或跨await；直到原Completion=Completed且EndOfRequest、DeliveredCarriers=RequestedCarriers、Integrity.FullBuffers才采用整批。Complete指读取完整而非全部Exact；部分范围EndOfTable=false正常，不能为等全表结束扩大范围。

每carrier关联以原ordinal为键，页局部offset对应本页Entries；方法/父项固定slot/ordinal/weight/实际Origin，不把ordinal转double（可>2^53）/Root SourceIndex/最近点。C5已核同session两scope完整hash及每行Origin；工作台核其ContributionReceipt/descriptor精确闭包，不另开私有buffer扫描替代C5。每Exact行的所有父项（含零权）按A.10.9合并的有限读范围经对应父Surface/domain/ordinal原ISurfaceDataService取得，复用已冻结的相同父ordinal读值而不重复开请求；父snapshot/frame/hash须匹配ContributionParentReference，单位另从原父Descriptor和明确坐标映射核查（ParentReference没有Unit字段）；父值Valid/Unknown/Invalid和方法Evidence保持。ObservedIdentity/ConvexCombination权重原样，不重归一、不算插值、不合并父项、不将派生Origin升级Observed；Unknown/Unsupported空父行不会变Exact。

跨父frame/单位在贡献事实读取层合法；本版reference/field自动接线只接父/载体已由原coordinate Owner归一到同一明确Frame/mm且保Mapping receipt的范围，缺映射Unsupported/NoMapping；不在工作台加权XYZ猜target位置。Contribution.Method.EvidenceSha256/Parent.SnapshotSha256为原Owner证据引用，不是物理校准proof。各父读取和原贡献读取均有独立原Task/额度，Completion真实退出后释放原session；父源值被深冻结到工程snapshot后才可归还。取消/late页/Dispose未知使暂存整批不可采用，A.5 root持原操作/Task/绑定Owner继续有限观察，不能Close共享reader来取消另一Host。

C5记录和父值资格只能构成**来源闭包**；对一个SurfaceCell的WholeCellSupport、Material/UnknownHeight划分和参考整片适用证书须由原领域/ROI/reference Owner给确定资产，工作台不凭三顶点Exact、权重和1、ProducerRecorded或C5完成授完整物理域。本文已确定实际公开读取/字段映射，不再写“多父合同不存在”；未有整片支持的输入精确Partial/Unqualified，不让程序员补假qualification。

#### A.10.6 reference/Q与连续域：值映射、调用和拒绝

首版reference接线选IM-035 HeightSecondOrder/SignedAxisHeight，仅Engineering，无全局/局部隐式替代。输入SurfaceSnapshot.Unit=Millimeter、稳定SourceIndex与C5载体ordinal→原SourceIndex关联保存；IsValid依据原位置状态及具体来源用途资格，Unknown不标valid。Cells只保原连续证据CellId/顶点SourceIndex/IsContinuous/EvidenceReference，R/X/C/T的SourceIndices和CellIds来自显式原域资产、revision/hash/Chart/ReferenceDirection/重叠许可均保留。Profile全部Robust/Numerical/Support字段、Budget与Options由Host原冻结ReferenceSurfaceRequest给出，无工作台默认；ComputeSurface/Domain/Profile/Request哈希逐层复核，不把C5 descriptor hash当reference hash。

调用原ReferenceSurfaceFactory.Create→engine.ExecuteAsync完整request；借用已构造engine则不另开重复执行，原request ID只派发一次。执行原Task和event元数据登记为A.5/A.7的child Owner；等待到期不等ResourcesReleased。只有Status.Succeeded、Binding/Request/Profile/Model/Evidence/Result全部hash精确闭合及原Task真实结束才可发布工程Artifact。重新求值只用原Result+FrozenProfileReference经ProfileSource.ResolveAsync→EvaluateAsync，返回原Profile lease的Dispose真实完成后才输出批次；不按新用途Profile扩大旧支持。

连续Q转换限定已显式同Chart/PhysicalFrame/mm：PhysicalFrame.Origin=原Chart.Origin（原单位Millimeter）、U/V/N=Chart.U/V/HeightAxis，原TargetFrame精确一致；原HeightModel.Chart全部值相等、ModelKind.HeightSecondOrder、CoefficientsInMeters恰6项顺序[1,u,v,u²,uv,v²]。QuadraticReference.Model为原ModelSha256所登记资产；Center=(CenterXInMeters×1000,CenterYInMeters×1000)、ScaleXmm/ScaleYmm=原ScaleX/ScaleYInMeters×1000，CenterZmm=0、ScaleZmm=1、Coefficients=每个CoefficientsInMeters×1000。每个乘1000结果用IEEE有理值精确核对，不保真/溢出/原Scale非正即Unsupported；不平移拟合、不翻normal、不重算系数、不把底面三点变仿射。0/1是本具名表示分解常数，仍全部进入ContinuousCanonical.HashInput，不是物理底高默认。

Applicability/Qualification由原Owner提供PlanarDomain.Decomposition+原Reference SupportEvidence/Profile/Model闭包，且必须覆盖本次每WholeCellSupport对应的整片，ForbiddenCells/UnknownCells/孔洞/外推范围不得被省略。CoverageQualified/RMS小/拟合Rank充分只为原reference事实，不能单独作为任意新cell的Q Qualification。确定接线核原资格资产与这次原request/model/域引用，缺原整片资产精确Unqualified；需要新分解/含洞裁切由原ROI Owner提供，工作台不生成PlanarDomain或补边界证书。旧只有离散点、斜Chart变换、H→Q补零、Plane→Q、未获支持外推在本Q工具范围Unsupported。

上层仿射场/下层Q的最终FieldInput由已登记IM036 IContinuousReader取得：FieldInput.Field的Frame/Purpose/Model/D/F/B/Us/Uh/E/U/Cells/Fragments/Quadratic/UnknownBound所有字段保原，Purpose=GeometricHeight，Q路线BottomHeightsMm必须Empty。A.10.5记录仅关联每cell Sources/WholeCellSupport来源，不重算TopHeightsMm或实际权重、不将C5三点完整当单元内部完整。AffineTriangles仅保原上下三点及共同分片证据（显式bottom=0才表示平面基底），不能对缺bottom补0。material用途、AreaDomain、Q PositiveCenter、多CDF/概率编辑、新生成分类/共网格不在本固定工具，Unsupported；上游这些公开能力本身不受本工具限制。

执行顺序：新field Profile/template/ParameterProfileBinding冻结→IContinuousMetrologyService.Validate→原MeasureAsync（reader.ReadProfileAsync/AcquireAsync核ContinuousCanonical.HashProfile/Input、Scope/TargetFrame与资格）→ContinuousMeasurements.Validate(request,profile,实际payload)→原backend→GetOperation/RequestCancel/Released。工作台的SourceScope保原reader入口/父child直到原runtime输入lease.GetReleaseReceipt=Released且原Measure Task完成，不能在工作台先Dispose同一lease；Runtime唯一拥有它并归还，adapter借用reader/service。Core.Compute只Engineering但本Host仍走service，不能借纯Compute绕过reader资格/资源或给fake input证明HALCON包。

FieldResult投影精确保原DomainReport.Measure/TargetComplete、CompletedE/RemainingU/CompletedFragmentIds、Integral.Signed/Positive/NegativeMagnitude/Absolute/ConditionalWhole、CDF与Quantile的Known/ConditionalWhole区间、Atoms、NumericCertificate状态/预算/StoppedFragmentIds。单CDF/概率仍保请求顺序；Missing/NoResult不建0或取区间中点。mm²/mm³/mm⁴/Ratio沿A.6；数值包络与reference.Uncertainty(false/limitations)分开，不作置信度/合格。ImageEdgePair保原candidate/Edges/witness/支持与原ResultFingerprint，点距保原witness；全部OriginalResult原版本/原payload保留。

#### A.10.7 两消费者：复用双Root的实际链与可选UI

H1为独立工程测量工具、H2为外部二维/三维视觉工程工具接入计划，沿§9.1/A.8原双Host/depot/Root/session和独立ports/provider/store；不增工程/另起第三Host，不把示例等同已交付的第二产品。合成Replay只继续验证Core生命周期；下列Port使用实际原模块公开值/服务，原runtime包未运行时标NotEvaluated，不以Replay固定值替代。

| 消费者 | 无UI确定链 | 可选UI/Overlay和Owner恢复 |
|---|---|---|
| H1 点距/边距 | 显式冻结PointDistance或ImageEdgePair Profile/template/source/coordinate/ROI→A.10.8纯Schema工厂→原ParameterEditorFactory.Create(schema,baseline,显式options/access/time,preview/recommend按已绑定能力,apply=null)→CheckEdits/SetValues/Validate Full/CreatePatch→独立BindingOwner.Start*/发布原新Profile/模板/receipt→job真实Released→session.SetDraft→Execute新Key→原IMetrologyService.MeasureAsync/GetOperation原key→原回执 | 使用A.7传入同PE session的ParameterUiOwner与同Host的ViewportUiOwner；Inspector改动走同CheckEdits链，转换完成前执行禁用。边距Edges.Pixel按(Column,Row)无损构造原SourcePoint2D，稳定SampleId/CandidateId/source/coordinate revision绑定原OverlayLayer/SetLayersCommand，详见下段。不拿行号/pixel比例造物理线。关闭UI先Detach/Observe，不Close借用PE/Viewport；Core根最后关，异常保BindingOwner/原Measure/Dispatcher任务并用Proof转交 |
| H2 场分布 | A.10.9来源Owner保持原C5/SurfaceRead→父snapshot/单位/实际Origin/支撑闭包→原reference.ExecuteAsync或完整冻结Artifact/EvaluateAsync→核精确Q与原Qualified FieldInput/ContinuousRequest/Profile→A.10.8.FieldDistribution→PE Full/Patch→BindingOwner.StartField→新ContinuousProfile/template/receipt→SetDraft→Execute新Key→原IContinuousMetrologyService.MeasureAsync/GetOperation→原FieldResult | 参数Inspector借同PE；主Viewport仍显示其已批准载体和原reference层。当前OverlayPayload只提供2D SourcePolyline/RoiGeometry/Label，不能表达任意3D triangle或ReferenceIntersection，本工具对该3D Overlay精确Unsupported并保原结果表/CompletedE/RemainingU/证据；不扩造命令。显式坐标Owner已提供匹配2D源映射时才允许只读SourcePolyline导航投影，不授新测量值。reference只读Inspector由原IM035 Wpf模块Host控制 |

首次构造顺序固定为A.10.8纯工厂→完整PE baseline→原ParameterEditorFactory.Create（显式TimeProvider）→BindingOwner，之后Start才消费真实PE Patch。无UI与可选UI使用同一Schema/session和转换入口，禁止假Patch/空Guid/隐式默认值。

边距原Edges.Pixel已属Subject图像，使用Asun.UI.Viewports.OverlayPayload(OverlayKind.SourcePolyline,原SourceId/CoordinateRevision,原GeometryRevision,Geometry=Empty,Polyline为原Edges逐点Column/Row,LabelResourceKey为空,SelectionPriority为Host原层值)，OverlayLayer.LayerId由长度前缀工具/operation/candidate/SampleId闭包稳定生成，ZOrder/Visible/Interactive=Host明确只读显示值，SourceRevision精确原descriptor；从原session当前完整层集合中只替换本tool/operation拥有的层，保其它Owner层及原source/revision不变，完整Replacement通过原SetLayersCommand(Replacement)，不发未声明的AddOverlay字符串命令。扫描不连续/不同pair分不同层，不能连线掩gap；SourcePolyline多点全原顺序，不拿amplitude排序。PointDistance几何只有mm而无该图像pixel对应时仅原witness表/结果几何证据，不猜SourcePoint2D；若coordinate Owner已提供匹配source/revision的明确映射则其返回点作只读导航Overlay，不改变原Distance。

工具变更发布新Profile而不改变source/context时以新Plan SetDraft；改变Context外输入、坐标或reference/field来源须Rebind并清旧采纳；不能沿新参数SameInputs旧operation。推荐采用后仍显式确认转换/执行，生产Apply/保存由宿主原Owner。每个新job在Start前按Profile预留最大输入/结果/Task，BindingOwner.RequestClose只停止自己的转换/发布观察，不关闭共享端口；迟到发布记录原资产但不安装旧epoch/Draft，Owner.Observe不能等待自己的cleanup任务。source/reference/ROI/PE/service各原Owner关自己的Owned实例，借用不dispose；无结果、取消、超时或ReleaseUnknown不放root槽，A.5 Offer→Accept→Confirm保持同原Task/asset关系。

#### A.10.8 首次Schema工厂与本增量验收

~~~csharp
public static class WorkbenchToolParameterSchemas {
    public static Asun.Modules.ParameterEditor.ParameterSchema PointDistance(
        AssetRef profile, Asun.Metrology.Contracts.MethodProfile exactProfile,
        ResourceProfile limits);
    public static Asun.Modules.ParameterEditor.ParameterSchema EdgePair(
        AssetRef profile, Asun.Metrology.Contracts.MethodProfile exactProfile,
        ResourceProfile limits);
    public static Asun.Modules.ParameterEditor.ParameterSchema FieldDistribution(
        AssetRef profile, Asun.Metrology.Contracts.ContinuousProfile exactProfile,
        ResourceProfile limits);
}
~~~

首次Schema一律由本纯工厂建立，核Tool方法固定字段、原profile hash/版本/全部上限及A.10.2/A.10.10表示投影及原bits保留；非法结构ArgumentException，未支持组合NotSupportedException（Host投影既有Unsupported与资源键）。无PE/IO/native/授权副作用。Host先纯Schema→原PE Factory，之后才构造含真实Patch的BindingInput。初始ParameterSnapshot只有映射为numeric表示的key按A.10.10从对应原Profile值取得可回转bits的decimal投影；Enum按原枚举值保留，Length、Ratio等按各自原PE ValueType、单位、边界及对应表项规则映射，不把它们套成通用Decimal。Generation=0、Origin.Explicit，Schema/hash用原PE规范；Baseline.Owner=原Profile ContentRef、Revision为其真实ulong经checked long转换（溢出Unsupported，不截断），PE内部Generation与AssetRef.Revision分开。

这里的初始Snapshot仅包含A.10.2工厂实际保留的key；被省略numeric key没有PE entry，完整性核对以重算后的实际Schema为准。例如合法场Profile的cdf_height=1e308、probability=0.5，生成coverage/transform/probability三个定义和Explicit entry，cdf_height原bits仅在工作台只读区与Profile保留；修改probability=0.7后Full有效，新Profile仍保cdf_height=1e308。向Patch注入cdf_height为未知key拒绝且零Publisher；不能为“全字段必填”阻断另三个字段或给cdf_height补0。

0.6.0增量两轮有限文档自审已完成；0.6.1本次参数修订另按A.10.10两轮定向自审，未编译/运行：视角一走操作者/数据链（初次Schema、旧值、合法修改、推荐拒识/显式采用、Profile发布、实际Measure、结果/Overlay、Close），视角二走外部实现者（单位/精确转换、原canonical/hash、C5 Origin+父ordinal/零权、多域/Q资格、跨进程命令/deadline/历史、late发布/撤权/释放未知）。第一轮修正ExecutionBudget九字段、Schema.Identity、PE键/单位和原Profile基线、ROI七case完整顺序与聚合预算；第二轮修正权限/epoch显式注入、父快照原编码/实际范围核验、无效NaN坐标边界、首次求值先取得原Result、新版Q不沿旧资格及Overlay保其它Owner层。定向检查仅本页链接/围栏/声明、冻结章节hash和新增MWB-ROI-V01字节，不重审已接收Core/Host或执行全仓校验。以下是后续实现应复用T02/T04/T06/T07/T09–T14的验收断言，未执行这些产品测试，不新造测试工程：

- 0.1/0.01/0.4/1e-9按A.10.10最近值oracle和准确有理误差接纳；未改字段保baseline bits，修改边界的decimal意图与输出分别核验，不clamp。极端原值仅对应字段只读；sigma按已接收的Decimal/Pixel加法启用，否则原值只读且其它参数可编辑。半径/角/未批准单位映射拒绝。
- PE建议过时代次/patch hash被改/Before.Owner错/Full无效/空Patch→零发布；合法patch只改表中目标，所有无关字段/预算/原Inputs逐字段相等；publisher错新Profile/错receipt/late旧epoch→不SetDraft，原job/已发布工程资产继续有界收尾。
- ROI snapshot revision0、一般Curve U/V和全部Source/约束按原codec保留；command七case值不缺字段。新目标base不相等→StaleBinding、旧deadline不转运、源Unknown不续跑、跨进程Undo/Redo→Unsupported；值运输成功仍零Apply，显式新意图才调用原API。
- C5同carrier但错Origin控制列/父slot/weight/descriptor hash→原reader失败整批失效；Unknown/Unsupported、零权无效父、父ordinal>2^53、(EndOfRequest=true,EndOfTable=false)原样；C5完成不授整片资格，不将cross-frame父位置加权猜XYZ。
- Q模型6系数/坐标/尺度×1000不能exact、斜Chart/缺整片Qualification/错reference Result/Profile/Model hash→Unsupported/Unqualified零Measure；合格原Field保持D/E/U和Q，Hole/Unknown不能删掉；PositiveOnSameDomain不改signed Integral，CDF/Quantile/数值证书不当质量/物理不确定度。
- H1关A不影响H2的PE/service/Dispatcher/root；late Profile/Contribution/Reference/Measure task仍保原Owner，有限Observe过期不释放/不新Acquire、不重发生产Apply/Save，Proof确认前源depot继续强持。

来源/版本依据复用上述已读上游正文与已有HALCON/DevExpress研究；本节只映射公开值及调用、不增加算法路线。另核微软[数值转换规则](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/numeric-conversions)（2026-10-11）：decimal到double可能舍入，目标.NET10不能依赖.NET11改进保证，因此本版参数转换用A.10.10有界整数最近值/偶数舍入并保存准确有理误差；shortest投影经同规则回转bits核验。Q米→mm仍采用原精确有理比较。尚未执行产品C#、HALCON、WPF、Golden或性能；A2本节内容接收和真实运行资格分别记录。

#### A.10.9 具名来源Owner、租约与参考资格消费

本节公开具体H2来源准备入口，禁止将A.10.5/A.10.6中的关联变成隐藏helper/静态当前surface。类型仍在Adapters，引用原SurfaceData、Contribution、ReferenceSurface和Metrology公开值；不在Core加领域类型。参考点/域/Field已经由对应Owner提供，准备Owner只检查实际读值/原证据相等并调用原服务，不创造拓扑/材料/Qualification。

~~~csharp
public sealed record WorkbenchReferenceEvaluation(string RequestId,
    ImmutableArray<Asun.Modules.ReferenceSurface.ReferenceEvaluationPoint> Points,
    Asun.Modules.ReferenceSurface.HeightDistanceMode Mode,
    Asun.Modules.ReferenceSurface.ExecutionBudget Budget);
public sealed record WorkbenchParentSnapshotEvidence(
    Asun.Modules.SurfaceData.Contribution.ContributionParentReference Reference,
    Asun.Modules.SurfaceData.SurfaceDescriptor Descriptor,
    ContractRef SnapshotContract, ImmutableArray<byte> OriginalSnapshotBytes);
public sealed record SurfaceFieldPreparationInput(MeasurementPlan Plan,
    Asun.Modules.SurfaceData.SurfaceReadRequest CarrierRead,
    Asun.Modules.SurfaceData.Contribution.ContributionReadRequest Contributions,
    ImmutableArray<Asun.Modules.SurfaceData.SurfaceReadRequest> ParentReads,
    Asun.Modules.ReferenceSurface.ReferenceSurfaceRequest Reference,
    Asun.Modules.ReferenceSurface.ReferenceSurfaceResult? FrozenReference,
    WorkbenchReferenceEvaluation? Evaluation,
    Asun.Metrology.Contracts.ContinuousRequest Request,
    Asun.Metrology.Contracts.ContinuousProfile Profile,
    Asun.Metrology.Contracts.FieldInput Field);
public interface IWorkbenchSurfaceEvidenceReader {
    IWorkbenchJob<WorkbenchParentSnapshotEvidence> ReadParentSnapshot(
        Asun.Modules.SurfaceData.Contribution.ContributionParentReference expected,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<OwnerValue<Asun.Metrology.Contracts.FieldInput>> ReadQualifiedField(
        Asun.Metrology.Contracts.ContinuousRequest expected,
        Asun.Modules.SurfaceData.Contribution.ContributionDescriptor contribution,
        Asun.Modules.ReferenceSurface.ReferenceSurfaceRequest reference,
        Asun.Modules.ReferenceSurface.ReferenceSurfaceResult result,
        CallContext call, CancellationToken executionCancellation);
    IWorkbenchJob<OwnerValue<Asun.Modules.ReferenceSurface.ReferenceSurfaceResult>> RetainReference(
        Asun.Modules.ReferenceSurface.ReferenceSurfaceRequest original,
        Asun.Modules.ReferenceSurface.ReferenceSurfaceResult result,
        CallContext call, CancellationToken executionCancellation);
}
public sealed class WorkbenchSurfaceFieldOwner : IWorkbenchChildOwner {
    public WorkbenchSurfaceFieldOwner(IMeasurementWorkbenchRoot root, string ownerId,
        IMeasurementWorkbenchSession session, IWorkbenchAuthorizationPort authorization,
        Asun.Modules.SurfaceData.ISurfaceDataService surfaces,
        Asun.Modules.SurfaceData.Contribution.IContributionReader contributions,
        Asun.Modules.ReferenceSurface.IReferenceSurfaceEngine reference,
        Asun.Modules.ReferenceSurface.IReferenceSurfaceProfileSource profiles,
        IWorkbenchSurfaceEvidenceReader evidence, ResourceProfile limits,
        TimeProvider timeProvider);
    public string OwnerId { get; }
    public void RequestClose();
    public ValueTask<DrainReceipt> ObserveAsync(TimeSpan budget, CancellationToken waitCancellation);
    public IWorkbenchJob<MeasurementPlan> StartPrepare(SurfaceFieldPreparationInput input,
        CallContext call, CancellationToken executionCancellation);
}
public static class WorkbenchSurfaceFieldCanonical {
    public static string HashPreparation(SurfaceFieldPreparationInput input);
}
~~~

构造核session属于root并同步注册child/原端口强持，不开Source/engine/native；Root关接纳拒构造。HashPreparation按WB-TLV-3域`mwb-surface-prepare/1`后递归写SurfaceFieldPreparationInput全部声明字段：嵌套原DTO依公开声明字段序，数组保持原顺序/显式null存在位；ContinuousProfile.Options是唯一FieldOptions叶，先写叶名再字段，其余record不加tag。字典先uint32项数，long key升序、string key Ordinal序，写完整key/value；DateTimeOffset写UTC ticks int64，byte写单字节，uint写uint32 LE，其余沿A.9。不调用上游排除RequestId/Budget的hash替代完整原请求身份；hash字段也保原，double仅finite/-0归0。此纯值工具限已知形状，非法ArgumentException；call.RequestHash须等该hash。Start按同Key完整payload回放/冲突，再仅新Key核session.Read的SessionId/Epoch/Active/Context、call.Profile和AuthorizationRevision、View+Execute及完整来源/域/Profile资产；Invalidated连执行取消，采纳前再核权限/epoch。借用session/authorization不关闭，不在Read失败后披露输入。

StartPrepare在原job槽内串行调用原服务，call的单调RemainingBudget跨全部阶段；每一阶段派发前重核其原Surface/Contribution/Reference预算≤当时剩余预算及双边字节/工作量限额，不改已冻结原请求字段缩短或延长。超过剩余时该阶段零派发、已开始阶段继续真实收尾，Host显式新意图/新Key重新准备。准备Owner只执行只读服务/工程资产保留，不自授生产资格。序列固定：

1. 核完整Plan/ContinuousRequest/Profile/FieldInput的version/hash/TargetFrame、Carrier/Contribution同key/domain/range、ParentReads完整集合、Reference请求Profile/域/Chart/hash、当前权限/epoch；预留carrier/父页副本、贡献页、reference输入/原输出最大值、原服务/发布/关闭Task与至少一个cleanup槽，MaxSources/MaxTrackedJobs/bytes任一不足零Start。每个child真实Release前占槽，不用总fan-in平均值省预算。
2. 原surfaces.Validate(new SurfaceSet(CarrierRead.Descriptor.Key.Id,CarrierRead.Descriptor.Key.Revision,[CarrierRead.Descriptor]))及Plan后StartRead，原contributions.Validate(Contributions.Descriptor)/Plan后Start；SurfaceSet只作纯校验集合，不赋新快照身份。登记各返回ISurfaceOperation/IContributionOperation与Completion。同步OnBlock/OnPage只短复制到预留不可变BCL副本；完成须原Completion已返回且Snapshot.Phase为ResourcesReleased或Terminal（后者已包含释放完成），Surface Outcome=Completed/Completeness=Complete/DeliveredItems=RequestedItems/Integrity=FullBuffers、C5同A.10.5全部条件。空请求/部分读不可作为完整准备，Errors非空/IssuesTruncated不采用。按ordinal关联SourceIndex/原位置状态及元数据，Valid位置与Reference.Surface.Points逐值相等；原Field来源引用须包含该载体及完整域证据。原Surface的Invalid/Unknown Positions可能NaN，不能直接塞给要求finite坐标的Reference：只有原坐标Owner已提供有来源证据的有限平面位置和有限占位高度、IsValid=false才保留原slot，缺该事实Unqualified/零reference；不造0、不删点。重复SourceIndex/Unknown误标valid拒绝，不以原Template旧点替缺读。
3. ParentReads按贡献Parents的稳定slot再按Ordinal Start排序，Range固定Vertex/Ordinal（Tile=null）、Selection=PreserveAll/ReadCoordinates=true，FieldIds为原Height或X/Y/Z。仅实际有父项的slot须有读请求，但每条实际ParentOrdinal（含零权）必须被恰一个范围覆盖；多个carrier共用同父ordinal复用该冻结读值，并完整保留各carrier的原ParentContribution，不能合并权重。ReadParentSnapshot每slot一次：返回Reference逐字段等expected，SHA256(OriginalSnapshotBytes)=expected.SnapshotSha256，SnapshotContract保原Owner公开编码/版本，Reader须由可信原Owner路由按该原格式验证bytes所绑定的完整Descriptor/Key/Frame/domain ItemCount；未知原格式Unsupported，不杜撰surface统一hash算法。ParentReads.Descriptor须深值等此Descriptor、原Frame/单位与明确映射核实。该bytes不是选定buffer，不能用某Buffer.Sha256代snapshot摘要。父读取仍独立由原Surface服务核实际buffers/hash；成功条件同载体，每个父位置原state/Origin保留。范围互不重叠，覆盖缺失StaleBinding；保守多读许可但预算/证据包含全部读项，不无限逐item派发。所有ParentReads涉及的slot必须存在且Descriptor唯一对应，父face/domain本工具Unsupported。
4. FrozenReference=null时carrier来源匹配后仅一次reference.ExecuteAsync(Reference,progress,linkedExecutionToken)，登记ValueTask.AsTask一次，保持完整R/X/C/T/原RequestId/CorrelationId。FrozenReference非null则不Execute，按原ReferenceSurfaceIdentity逐层核该完整Artifact与本次Reference的Request/Profile/Binding/Model/Evidence/Result；原RequestId/CorrelationId也须相等，读值真实性由原Reader可信路由核验，不能从GetSnapshot造历史结果。只有Succeeded完整闭包且原Task结束可用。超时/取消继续观察同原Task/来源，不再Execute，借用engine不Close；随后RetainReference登记完整原Reference+原Result/hash，返回Contract=(Asun.Modules.ReferenceSurface.ReferenceSurfaceResult,rs-api-0.1)、Identity.Sha256=原Result.ResultSha256且Value逐字段相等。失败/保存未知不输出可采纳Plan，不借此端口修改生产指针。
5. Evaluation非null时用其显式RequestId/Points/Mode/Budget及第4步确切原Result构造原ReferenceEvaluationRequest，再调用EvaluateAsync(request,profiles,linkedExecutionToken)；不要求调用方预先猜本次结果或ResourcesReleasedAt。Mode须SignedAxisHeight、单位同原Binding；Profile Resolve/lease释放由原engine负责，本Owner只持原Task，不Dispose它的同一lease。成功batch.Status/RequestId/Values顺序与原points匹配，受支撑的数值才可投影，Unknown/Forbidden保原状态。Evaluation=null只省这一显式求值，无隐式生成“所有顶点都支持”；求值也不生成FieldInput/whole qualification。
6. ReadQualifiedField(Request,Contributions.Descriptor,Reference,第4步原Result,call,token)通过可信原Owner路由核已有WholeCellSupport/Classification/BoundaryQualification/Q.Qualification资产与这次完整载体/父snapshot/Reference Model/Profile/域闭包，不按引用hash自报资格。返回OwnerValue.Identity与原Request.Input逐字段相等、Contract=(Asun.Metrology.Contracts.FieldInput,0.3)，核ContinuousCanonical.HashInput、Frame/域/whole support与原参考结果/原C5父来源关联。SurfaceFieldPreparationInput.Field与该返回FieldInput必须完整相等。仿射Q转换只校核input.Field.Field.Quadratic等于A.10.6的精确表示；不在这里`with`改Q后保旧WholeCellSupport。若新reference导致Q/qualification改变，当前准备StaleBinding/Unqualified，必须由原Owner产生新版**完整FieldInput/qualification**后Host新Request/Input/Key，而非在本工作台局部补proof。AffineTriangles虽可不使用Q，其下场仍须原whole support；本H2请求仍核明确Reference与用途，不能自动换底面。
7. 原Surface/Contribution Completion已完成且副本使用结束、reference/evaluation原Task完成、每个evidence job真实Released后，才返回原Plan（不改Inputs/Template/资格）；调用Host再进行PE编辑/Profile绑定。所有阶段的错误用既有WorkbenchError固定分类和字段资源键，保上游完整原回执资产；不因source/ref逻辑成功提早判ResourcesReleased。

本增量的Unqualified/Partial/NoMapping是上游结果或用途说明，不扩WorkbenchErrorCode：准备或发布job缺资格用Unsupported + `workbench.qualification.required`，缺坐标映射用CoordinateMismatch + `workbench.coordinate.noMapping`，结构/数组错误InvalidRequest、原hash不符InputHashMismatch、旧基线StaleBinding、预算BudgetExceeded、超时DeadlineExceeded；原上游状态/错误完整保原回执。只有真实量测结果才按A.6投影OperationOutcome/量值有效性，不让WbResult失败凭空携量。evidence jobs的本地身份按(OwnerId,call.Key,method,expected父引用/完整请求)分槽，每方法每父最多一次并保持原Task，同Key异payload冲突；ReleaseAsync只观察同一原释放，读完不重新Acquire。

ReadQualifiedField是显式工程资产/资格Reader，不是自定义AI/重建/质量判定端口；实现者只按固定原Owner路由读已有全片证据与payload，不生成证书。实际Source/native与IM036.IContinuousReader的资源桥仍由真实消费者用同一输入资产建立：允许A.3已定义的两个独立合法parent读取，各自计账，不声称原IM031分页Span能直接转IContinuousLease或原snapshot自动零拷贝。IM036 runtime自己Acquire/Release它的input；准备Owner不持/不Dispose该lease。Parent Snapshot和ReferenceSurfaceResult都是不可变值资产，不能替代真实Source session释放回执。

每Host的SurfaceFieldOwner/BindingOwner均分别登记Core root，最多一个当前prepare/转换（其余拒接纳，历史按原Profile.MaxOperations/bytes有界保留）；原task列表由root→child owner→service operation/evidence job引用图保留。RequestClose只取消本实例operations/jobs/Reference task的执行token，不关闭借用服务。Observe不等当前正在观察自己的任务；Profile.CloseTimeout到期返回Drained=false，保原child/Task/暂存与可晚到值。Factory/consumer/engine异常都由这一图收尾；转交仍只用A.5原Proof/root，不复制任务数组冒新Owner或新Open。Host最终独占服务的Close按各原公开回执验证，不把C5.CloseReport或reference.GetSnapshot零active当另一个原lease已释放。


#### A.10.10 具名 Decimal→binary64 表示转换、边界与固定 oracle

本模块的参数表示转换版本固定为 "mwb.parameter.binary64/1"，对应一个不可变 ContentRef(Id="mwb.parameter.binary64", Version="1", Sha256="ffe0be320233c775a5362d7faa958e2a9fbeae2618c9116e1398ac446b13e284")。它是工程参数表示规则，不是PE的新事实、客户容差、测量不确定度或质量资格；receipt/2必须保存此RuleRef，旧receipt/1不能按本规则重签。

上述RuleRef的唯一规范资产预像固定为UTF-8无BOM、无前后空白、无行尾换行的175 bytes，字节内容（不含代码围栏）为：

~~~text
mwb-parameter-binary64/1|decimal96-scale0..28|nearest-even|shortest-roundtrip-value/1|preserve-baseline-bits|check-intent-and-output|error=output-minus-intent|no-qualification
~~~

该字节串的SHA-256必须为`ffe0be320233c775a5362d7faa958e2a9fbeae2618c9116e1398ac446b13e284`；实现或审核者按上述原始字节重算，不对规则名、Markdown、代码围栏或换行求hash。规则内容若需改变，必须升RuleRef.Version并重算新字节/hash及新receipt/2；本轮不重签旧receipt/1，oracle摘要亦不因本定义回溯改写。

~~~csharp
public enum WorkbenchNumericConversionDirection { BaselineDoubleToDecimal, DecimalIntentToBinary64 }
public enum WorkbenchNumericConversionStatus { Preserved, Converted, ReadOnly, BoundaryRejected, DecimalRangeExceeded, OverflowRejected }
public sealed record WorkbenchParameterNumericConversion(
    string Key, WorkbenchNumericConversionDirection Direction,
    WorkbenchNumericConversionStatus Status, string SourceDecimalCanonical,
    ulong OriginalBits, ulong OutputBits, string OutputNumerator,
    string OutputDenominator, string ErrorNumerator, string ErrorDenominator,
    ContentRef RuleRef, string BoundaryRuleRef);
public sealed record WorkbenchParameterNumericConversions(
    ContentRef RuleRef, ImmutableArray<WorkbenchParameterNumericConversion> Entries,
    string CanonicalSha256);
public static class WorkbenchParameterNumericConverter {
    public static WorkbenchParameterNumericConversion FromBaseline(
        string key, double baseline, ContentRef ruleRef);
    public static WorkbenchParameterNumericConversion FromDecimalIntent(
        string key, decimal intent, ulong originalBits,
        decimal? minimum, decimal? maximum, ContentRef ruleRef);
}
~~~

FromBaseline 的有限生成固定如下（仅Adapters参数投影，不增加Core API或PE类型）：

1. 读原IEEE-754 bits。非finite返回ReadOnly，并仍由原Profile Validator拒绝无效基线；正负零均投影Decimal规范值`0`，返回Preserved，OutputBits保持原零的sign bit，不经下面的正零转换。
2. 有限非零只生成一次 .NET 10 `baseline.ToString("R", CultureInfo.InvariantCulture)` 的最短round-trip文本。不枚举精度或指数，本版没有G17或其它fallback；以下任一步失败即ReadOnly。文本最多64个ASCII字符，系数有效数字最多17位，语法固定`[+-]?[0-9]+(\.[0-9]+)?(E[+-]?[0-9]{1,3})?`，指数范围固定−324..308；禁止空白、分组、NaN、Infinity和区域符号。
3. 单次从左到右解析符号、去小数点后的无符号系数c、小数位数f和指数e（无指数为0）；设k=e−f。c=0固定Decimal正零；k≥0只算一次c×10^k，k<0设scale=−k，并最多删除17个系数尾零、同步减scale。结果必须scale=0..28且c≤2^96−1；否则ReadOnly，不能舍入到28位或取零。由c的三个32-bit limbs、sign和scale显式构造Decimal；可用Decimal.TryParse复核，但不是转换权威，复核值须先消除无意义scale/零sign后与上述构造bits相等。规范文本用无指数、无正号、无无意义前导/小数尾零的十进制值，零为`0`；不改原PE Snapshot/Patch编码。
4. 以此Decimal调用下述具名最近值算法，必须回转bits逐位等于OriginalBits才给可编辑投影；记录Direction=BaselineDoubleToDecimal、Status=Converted、精确Output与Error=(原double−投影Decimal)。未编辑字段发布时仍走Preserved而不重新量化。R文本、Decimal构造、回转各只一次；范围或bits不匹配保原值只读，其它合法字段继续编辑。

官方依据为[标准数值格式的Round-trip (R)说明](https://learn.microsoft.com/en-us/dotnet/standard/base-types/standard-numeric-format-strings?view=net-10.0#round-trip-format-specifier-r)及[官方runtime v10.0.0 Number.Formatting源码](https://github.com/dotnet/runtime/blob/v10.0.0/src/libraries/System.Private.CoreLib/src/System/Number.Formatting.cs)：目标.NET 10的R采用最短round-trip格式；旧.NET Framework/Core<3.0的说明不作为本目标实现。不能用`(decimal)double`、当前区域格式、未经具名回转核验的R/G文本或record/cast equality替代。

FromDecimalIntent 的确定算法固定如下：

1. 从Decimal.GetBits取得signed coefficient p（绝对值最多96位）和scale=0..28，设q=10^scale>0（最多94位）；此时不需先约分。Decimal本身无NaN/Infinity；超出此类型的原文本在PE/受限解析入口返回DecimalRangeExceeded，不可能先截断后传入本方法。先核下段具名边界。零意图直接输出正零bits `0000000000000000`，Error为`0/1`；明确修改成零不继承OriginalBits的负号，未修改−0只走Preserved路径。
2. 非零取a=abs(p)。正finite幅值bits即单调MagnitudeCode，区间固定`lo=0`、`hi=0x7fefffffffffffff`。解码某code：`E=(code>>52)&0x7ff`、`F=code&0x000fffffffffffff`；E=0给`n=F,d=2^1074`（含零/subnormal）；1≤E≤2046设m=2^52+F、h=E−1075，h≥0给`n=m<<h,d=1`，h<0给`n=m,d=1<<(-h)`。E=2047永不入区间。统一以`n*q`与`a*d`比较，不转double。若a/q超过最大finite返回OverflowRejected，恰相等立即选hi；本Decimal域的非零正常输入严格在两端之间。
3. 当`hi-lo>1`：`mid=lo+((hi-lo)>>1)`，解码mid并精确比较；`n*q<a*d`令`lo=mid`，`n*q>a*d`令`hi=mid`，相等直接选mid并结束。每轮严格缩小区间，初始差小于2^63，最多63轮；到限仍未相邻为OverflowRejected，不增加轮数。退出核`hi=lo+1`及`value(lo)<a/q<value(hi)`，不凭循环次数假定成功。
4. 解码相邻L=nL/dL、U=nU/dU（尚未约分的d均为2的幂），设D=max(dL,dU)、NL=nL×(D/dL)、NU=nU×(D/dU)。比较`2*a*D`与`q*(NL+NU)`：小于选L，大于选U，相等选`code&1==0`的偶数候选（normal/subnormal/跨指数均适用）。这是精确距离比较的共同分母形式，避免把两个距离分母再次相乘。负输入仅对非零所选输出设置sign bit。
5. 解码选中输出并加sign得到signed n/d，Output约分；Error先按`(n*q-p*d)/(d*q)`构造后约分，零分数固定`0/1`。所有分母为正，分子/分母十进制字符串InvariantCulture、无加号/无前导零。意图与输出各自按下段精确边界比较，最后仍由原Validator核完整Profile/request；全部成功才Status=Converted并交Publisher。

整数预算：采用BCL BigInteger的精确整数，checked只管机器整数/位移/计数，BigInteger另显式检查abs值的bit length≤2048（零为0位）。每次乘法、左移和加减先核保守结果位长，再分配/运算；超限OverflowRejected。单候选分子≤1024位、分母≤1075位，搜索比较乘积≤1171位；相邻共同分母的码值分子只差至多一个二进制尺度，midpoint及Error乘积≤1172位，均落在2048上限内。约分使用Euclid余数法，每个分数最多4096次取余，超限同样拒绝；不逐码扫描、不枚举指数、不用容差比较，Host原ResourceProfile/执行deadline及失败零Publisher继续适用。

BoundaryRuleRef 来源固定为`mwb.parameter.boundary/1|source=A.10.2|key=<ParameterKey>`，对Baseline/Intent/Preserved/失败记录均由本Adapters按A.10.2具名numeric key生成，不接受调用方自填。该字符串是边界规则定位标识，不是ContentRef/hash。key仅允许length_tolerance、sigma_px、threshold、cdf_height、probability；Length/Ratio保持原PE类型和单位。minimum/maximum须逐值匹配表项（null表示无界），包含性也取表项：length_tolerance下界0排除；sigma_px为[0.4,100]；threshold为[1,255]；probability为[0,1]；cdf_height无上下界。未知key/界限不符为BoundaryRejected。分别用Decimal有理值和输出binary64有理值核包含性，不拿舍入后的界限double代替十进制边界。sigma与每个原Rectangle的额外交叉约束仍由BindingOwner按原冻结Profile/Schema及A.10.2、原Validator核验，BoundaryRuleRef不自授该事实或物理资格。

Record字段固定：OriginalBits始终是原Profile bits。成功Converted保存规范SourceDecimalCanonical、OutputBits、约分Output及Error；Preserved保原bits，Output为原double有理值、Error=`0/1`，Source为成功投影值，若本字段无Decimal投影则为空。ReadOnly时Source固定为空（即使内部曾产生未通过回转的候选）；BoundaryRejected/OverflowRejected保有效意图的规范Source；DecimalRangeExceeded或语法解析失败无有效Decimal，Source为空。所有失败OutputBits=OriginalBits，OutputNumerator/OutputDenominator/ErrorNumerator/ErrorDenominator四字符串均为空；不会把中间结果写作输出，不clamp、不发布、不替换原Profile。非finite ReadOnly不使用Preserved输出有理数，完整基线由原Validator拒绝。

转换的固定顺序是：①核PE Decimal类型、scale、Finite和资源预算；②保存原规范Decimal/原Profile bits/来源Key；③按上述有界整数比较取最近值；④以原MetrologyValidator或ContinuousMeasurements.Validate核完整新Profile/request，并再次核Decimal意图边界和输出binary64边界；⑤若任一边界、有限性、溢出或原Validator失败，返回 BoundaryRejected/OverflowRejected，不clamp、不发布、不替换原Profile；⑥成功才由Publisher写receipt/2。未修改字段的 OriginalBits=OutputBits 且 Status=Preserved，不经Decimal重新量化。连续Q的米→mm乘1000和WholeCellSupport/Qualification仍严格按A.10.6的原Owner模型/证据闭包；不得调用本转换器修改Q、Field、WholeCellSupport或任何资格引用。

上游边界与PE-1007兼容性固定如下：已接收PE Decimal/Pixel组合可编辑 sigma_px 的 0.4..100（含0.4、0.7、1.5），输出仍须满足每个SearchRectangle的 sigma≤0.5×HalfLength1Px；旧PE Schema Version=1时，sigma保持只读而其它四项仍可编辑。Length/Ratio/threshold也使用同一表示规则，但各自先核本Schema边界；AngleDegrees→rad、Pixel↔mm、任意跨单位或隐式scale仍拒绝。典型 0.1、0.01、0.4、0.7、1.5、1e-9只因binary64不完全相等不得拒绝。

固定 oracle 使用本节规则独立以整数/有理数重建，不能由受测转换器产生：

| 输入 Decimal 意图 | 输出 bits（hex） | 输出 exact rational | 误差（output−intent） | 结论 |
|---|---|---|---|---|
| 0.1 | 3fb999999999999a | 3602879701896397/36028797018963968 | 1/180143985094819840 | Accepted |
| 0.01 | 3f847ae147ae147b | 5764607523034235/576460752303423488 | 3/14411518807585587200 | Accepted |
| 0.4 | 3fd999999999999a | 3602879701896397/9007199254740992 | 1/45035996273704960 | Accepted |
| 0.000000001 | 3e112e0be826d695 | 4835703278458517/4835703278458516698824704 | 588233/9444732965739290427392000000000 | Accepted |
| 34359738368.000003814697265625（2^35与下一binary64的半途值） | 4220000000000000（下位significand为偶数；上位为4220000000000001） | 34359738368/1 | -1/262144 | Accepted，ties-to-even |
| 0.3999999999999999999999999999 | — | — | — | BoundaryRejected（小于sigma下界0.4） |
| 79228162514264337593543950336 | — | — | — | DecimalRangeExceeded（超PE Decimal最大值） |
| 原double 1e308 | — | — | — | ReadOnly（无scale≤28且回转bits一致的PE Decimal候选，原bits保留） |

固定 oracle 的唯一规范JSON字节串如下，不含围栏和行尾换行，UTF-8无BOM、无额外空白，字段顺序为format,ruleRef,cases及各case原顺序；ruleRef是上述ContentRef的`Id/Version#Sha256`文本投影。长度1750 bytes、SHA-256=`d275c712561b0babdc62ef1cee4e02e25eb7b89e254782d68337eba916225b6f`。

~~~json
{"format":"mwb-parameter-binary64-oracle/1","ruleRef":"mwb.parameter.binary64/1#ffe0be320233c775a5362d7faa958e2a9fbeae2618c9116e1398ac446b13e284","cases":[{"input":"0.1","outputBits":"3fb999999999999a","outputNumerator":"3602879701896397","outputDenominator":"36028797018963968","errorNumerator":"1","errorDenominator":"180143985094819840","status":"Accepted"},{"input":"0.01","outputBits":"3f847ae147ae147b","outputNumerator":"5764607523034235","outputDenominator":"576460752303423488","errorNumerator":"3","errorDenominator":"14411518807585587200","status":"Accepted"},{"input":"0.4","outputBits":"3fd999999999999a","outputNumerator":"3602879701896397","outputDenominator":"9007199254740992","errorNumerator":"1","errorDenominator":"45035996273704960","status":"Accepted"},{"input":"0.000000001","outputBits":"3e112e0be826d695","outputNumerator":"4835703278458517","outputDenominator":"4835703278458516698824704","errorNumerator":"588233","errorDenominator":"9444732965739290427392000000000","status":"Accepted"},{"input":"34359738368.000003814697265625","outputBits":"4220000000000000","outputNumerator":"34359738368","outputDenominator":"1","errorNumerator":"-1","errorDenominator":"262144","status":"Accepted"},{"input":"0.3999999999999999999999999999","outputBits":null,"outputNumerator":null,"outputDenominator":null,"errorNumerator":null,"errorDenominator":null,"status":"BoundaryRejected"},{"input":"79228162514264337593543950336","outputBits":null,"outputNumerator":null,"outputDenominator":null,"errorNumerator":null,"errorDenominator":null,"status":"DecimalRangeExceeded"},{"input":"1e308","outputBits":null,"outputNumerator":null,"outputDenominator":null,"errorNumerator":null,"errorDenominator":null,"status":"OriginalDoubleReadOnly"}]}
~~~

实现须逐字段复算表内bits、分数和状态。此oracle是输入→转换结论的数学向量，不是WorkbenchParameterNumericConversion序列化：Accepted对应record的Converted；OriginalDoubleReadOnly对应ReadOnly；失败字段null只表示无可采用输出，实际record按上段保持OriginalBits且四个分数字符串为空。前五项核无附加客户边界的数值规则，第六项核sigma下界，第七项核Decimal入口，第八项核Baseline受限投影；不以向量授PE、计量、WPF或现场运行资格。

本节此前两轮有限自审保持；2026-10-11从落盘停点完成本轮软件定义修复，再做一轮反例复核：R单次生成/精确受限解析/ReadOnly、二分相邻不变量与63轮上限、normal/subnormal/跨指数解码、共同分母tie、2048-bit上限与4096次约分、普通小数/Decimal端点/正负零、失败记录及BoundaryRuleRef来源、规则175-byte与oracle1750-byte原文重建；仅采用内存整数/有理数检查和正文一致性检查，不运行产品。未改字段bits、Q/WholeCell资格隔离、旧Core/API/Golden/receipt及业务/资源两轴恢复保持。未编译、未执行.NET转换器、HALCON/WPF、真实Golden/性能或现场验收，不修改上游指导或产品代码。

本轮准备结论：A.10确定映射与A.10.10软件定义已在IM-065永久原会话完成限定内容审核，不再等待总控内容复核。DEV-GOV-010 §3.1的C1/C2保持ModuleCoreImplementationReady；A1公开值映射和U1装配/恢复指导接收保持。A2本轮指导内容已闭合，但实际适配/源/native/Publisher/资格资产的消费运行及U1真实WPF仍PreparationIncomplete / NotReady，不将本次纯数值检查提升为整A2或产品ImplementationSpecificationReady。本轮软件定义无剩余内部决定或新增外部门；真实来源和资格仍需A.10.9的原Surface/Contribution/Reference服务及IWorkbenchSurfaceEvidenceReader.ReadQualifiedField、计量原Validator/reader/service、Host IWorkbenchToolProfilePublisher按原证据与资源回执消费，不在本模块生成物理资格。

### A.11 全批准范围的软件准备收口（0.7.0；原永久会话内容审核）

本节覆盖§1–9及架构IM-065已经批准的完整模块范围，补足参数命令接线、比较/导出内容、推荐消费、PageContract和验收负载。A.10.10结论保持为其限定数值修订结论；当前整模块结论以A.11.8为准。只在原Adapters/Wpf工程增加下列明确公开面，不改变Core API v0.3、A.1–A.9字节协议、Owner判定或上游契约，不增加新工具/产品流程。未写产品代码或测试工程。

#### A.11.1 数值转换集合的唯一内容身份

WorkbenchParameterNumericConversions.CanonicalSha256按WB-TLV-3独立域`mwb-parameter-numeric-conversions/1`编码：域字符串→RuleRef(Id/Version/Sha256)→uint32 Entries数量→逐条WorkbenchParameterNumericConversion声明字段序。Key用Ordinal升序、同key按Direction声明顺序（BaselineDoubleToDecimal先）排序；同(key,direction)重复拒绝。每条RuleRef必须逐字段等集合RuleRef，BoundaryRuleRef用A.10.10原规则；Key恰A.10.2该工具numeric key，不接受其它字段。OriginalBits/OutputBits为uint64 LE，不能经WB的double正零规范化；字符串即A.10.10规范十进制/分数原文。**仅本集合CanonicalSha256排除自身**，其它引用hash全保留。完整receipt/2中嵌套集合按声明字段序，包括已核过的CanonicalSha256，不再插独立域；先算集合再算receipt，不循环。

Publisher接受的成功集合覆盖原工具全部numeric key：每key一条BaselineDoubleToDecimal；合法可投影字段为Preserved，因数值不可投影而省略的字段为ReadOnly且保原bits/空Source与四分数字符串。legacy Schema因PE能力而省略sigma时仍记录其实际数值转换结论，不伪造ReadOnly数值失败，但禁止sigma意图条目。每个实际数值改变另有一条DecimalIntentToBinary64/Converted；未变字段没有意图条目，Enum改值没有数值转换条目。PE Origin改变但规范数值未变不重新舍入；完整Profile按原bits保留。BoundaryRejected/DecimalRangeExceeded/OverflowRejected等失败仅诊断，不发布成功receipt。BindingOwner从原基线和完整Proposed复算条目/排序/摘要，Publisher再核，不信任调用方自报摘要。

新增Adapters纯工具签名如下。Encode忽略self hash值但核其它结构，Publisher要求Hash等CanonicalSha256。均先按ResourceProfile计长/计条，再编码；此处不改变A.10.10转换器签名。最小编码向量是结构测试的空Entries集合（无成功绑定资格）：RuleRef=(r,1,64个a)。完整预像可直接重建为`LE32(35) || UTF8(mwb-parameter-numeric-conversions/1) || LE32(1) || UTF8(r) || LE32(1) || UTF8(1) || LE32(64) || UTF8(a×64) || LE32(0)`；长度及摘要见本节末的验证结论。正式三工具非空覆盖要求不能被该结构向量绕过。

~~~csharp
public static class WorkbenchParameterNumericConversionsCanonical {
    public static byte[] Encode(WorkbenchParameterNumericConversions conversions, ResourceProfile limits);
    public static string Hash(WorkbenchParameterNumericConversions conversions, ResourceProfile limits);
}
~~~

#### A.11.2 完整命令接线、参数绑定与换工具

Wpf公开加法成员：`MeasurementWorkbenchControl.CommandBinding { get; set; }`，类型如下；A.7原Mount/SetPresentation/Detach、A.8已有只读消费者保持兼容。未提供时完整主图/结果/参数基础编辑仍可用，涉及工程资产的动作显示“未连接”，不能自造Profile、OperationKey或目的地。

~~~csharp
// namespace Asun.Modules.MeasurementWorkbench.Wpf
public interface IWorkbenchControlCommandBinding {
    WbResult<Asun.Modules.ParameterEditor.EditorView> ReadParameters();
    WbResult<MeasurementPlan> SelectPlan(string toolId, SessionSnapshot current);
    IWorkbenchJob<MeasurementPlan> StartBindParameters(OperationKey key, SessionSnapshot current,
        CancellationToken executionCancellation);
    WbResult<ExecuteRequest> CreateExecute(SessionSnapshot current);
    WbResult<RecomputeRequest> CreateRecompute(SessionSnapshot current, OperationKey previous);
    WbResult<EditRequest> CreateRoiEdit(SessionSnapshot current, RoiIntent original);
    WbResult<EditRequest> CreateParameterEdit(SessionSnapshot current, ParameterIntent original);
    WbResult<LinkRequest> CreateLink(SessionSnapshot current, ViewportLink original);
    WbResult<CompareRequest> CreateCompare(SessionSnapshot current,
        OperationKey left, OperationKey right);
    WbResult<SaveRequest> CreateSave(SessionSnapshot current, MutationRequest original);
    WbResult<RestoreRequest> CreateRestore(SessionSnapshot current, AssetRef checkpoint);
}
~~~

Binding是显式Host桥，不是ServiceLocator。构造时固定本root/session、完整工具目录与各工具原BaselinePlan/Profile/Request（Field另含原FieldInput）、所属PE session、A.10 BindingOwner/Publisher、工程参数资产Owner、TimeProvider、ResourceProfile与AuthorizationPort；不能从名称推Profile或从磁盘latest填字段。SelectPlan及Create*为有界无IO构造，生成本Host新operation/attempt，期限取已注入Profile，不调用Core；返回原完整请求，control在当前授权/epoch下调用同session对应API。新命令绑定仅作用未来调用；已接纳job仍归原Owner。UI Root强持Binding及其命令Task；有资源的Binding另按A.5 RegisterChildOwner并真实排空，借用Core/PE不负责关闭。

ReadParameters只调用此Binding所借PE.Read并将原错误投影为WorkbenchError，不读取Inspector私有字段；control用该完整冻结投影显示绑定状态。StartBindParameters不是泛化转换：先原PE.Read/Validate Full，冻结本次editor的Schema/Generation/hash/本初始Baseline；再CreatePatch(新PE OperationId、原current generation、唯一幂等键、mwb-engineering/tool scope)。不再对已提交草稿重复SetValues。工程参数资产Owner在本次有界job内预留**实际完整Schema/Proposed**资产身份/预算，得到ParameterAsset；与原Patch生成A.10三个具体BindingInput之一，逐字段计算Hash*与CallContext，调用原WorkbenchToolBindingOwner.StartPointDistance/StartEdgePair/StartField。原预留/调用/发布Tasks登记后才出job；异常/观察到期保原job/已发布引用，不能另Start分配新资产。成功只返回完整Plan：control再ReadParameters、核Plan.Parameters绑定的generation/schema/snapshot hash及当前epoch/权限，显式session.SetDraft；失败或过期保旧Plan和可修草稿，新Plan不自动Execute。

control每次明确绑定意图生成新非空OperationId/AttemptId并保存原key；重复观察/回调沿同key/原完整快照返回同job，同key不同快照IdentityConflict。BindingOwner的CallContext.Key使用该key；PE OperationId、资产预留及Patch只创建一次并保存，不在重放时重新Read当前草稿形成新payload。UI在原发布未释放时禁新绑定；失败已退出但工程追加回执Unknown仍先查原Publisher，不能换key掩盖原事实。Root资源与记录上限满则拒新key，原记录不逐出。

第一次无PE变化直接用原BaselinePlan，不创建空Patch；Undo回到初始完整值也可以显式选择原Plan，必须原当前Snapshot规范值+Origin逐字段等初始Baseline，不能仅看IsDirty或显示字符串。之后每次提交仍从PE**初始**Baseline全量转换，保持A.10.3不自动重基规则。绑定成功记录已绑定PE session/generation/schema/snapshot完整引用；PE任何后续修改/Undo/Redo/采用建议使UI标为“参数未绑定”，Ctrl+Enter/执行暂不可用，常驻“绑定参数”恢复；按F5明确重算历史输入仍允许，不谎称用了新草稿。ROI Apply返回新geometry但无原Owner派生计量operand/template时同样标“输入未绑定”，只允许编辑/查看或Host显式给完整新Plan。

工具列表从session.ListTools与Host完整Plan目录逐项交集取得，按ToolId Ordinal稳定排列；三种固定工具的具体验证仍A.10.1。选另工具先结束IME/单元格token（选择确认或取消，不隐式提交），取消gesture/未接纳候选；有未保存工程草稿时提供保留旧草稿、取消切换两个动作，保留不生产Apply。当前参数发布/编辑仍在途则等原资源ACK或取消后排空；不得用换工具摆脱Unknown。通过原RebindAsync的新epoch及SelectPlan完整验证后，原control.Detach真实Detached+Drained，再以新bindingId、新PE/viewport childrenFactory及匹配Binding重新Mount，同一实例root保持。清理Unknown保旧UI槽，不重挂其它窗口/工具；Core rebind失败保旧完整上下文。新Mount失败显示具体恢复，不丢旧结果/工程资产引用。旧PE/viewport若Host owned，由其Owner最后关闭；工作台仅退借用绑定。

命令门是当前View/操作权限、Active与epoch、预算、合法Plan、焦点/在途状态的合取，UI只是提示，Core/原Owner在接纳前及采纳前再核。取消不需要新Execute权限，但仅取消本session已登记原operation；只读/恢复只读禁编辑、绑定、执行，允许有View的历史查看和有Export的证据导出。执行用精确当前Plan；F5用原Previous+SameInputs、ExplicitPlan=null；比较选中两项原已释放可披露MeasurementPayload；Save/Export用Host给定Destination/ExpectedRevision，未知回执只Resolve原Mutation，不能重复Save。

#### A.11.3 比较与导出的稳定内容、codec和失败边界

比较端口不能从结果名称猜原定义；Host在Core接纳Execute/Recompute时保原接受Plan与Context，结果完成后绑定其OriginalResult/ResultFingerprint。该表仅接受Core已接纳原请求，不从当前Draft构造。公开的窄读桥和具体比较Owner为Adapters加法：

~~~csharp
public sealed record AcceptedMeasurementPlan(OperationKey Key, MeasurementPlan Plan,
    WorkbenchContext Context, AssetRef OriginalResult, string ResultFingerprint);
public interface IWorkbenchAcceptedPlanReader {
    ValueTask<WbResult<AcceptedMeasurementPlan>> ReadAsync(MeasurementResult result,
        CallContext call, CancellationToken cancellationToken);
}
public sealed class WorkbenchProjectionCompareOwner : IWorkbenchComparePort, IWorkbenchChildOwner {
    public WorkbenchProjectionCompareOwner(IMeasurementWorkbenchRoot root, string ownerId,
        IWorkbenchAcceptedPlanReader plans, ResourceProfile limits, TimeProvider time);
    public string OwnerId { get; }
    public IWorkbenchJob<ComparisonResult> StartCompare(MeasurementResult left,
        MeasurementResult right, CallContext call, CancellationToken executionCancellation);
    public void RequestClose();
    public ValueTask<DrainReceipt> ObserveAsync(TimeSpan budget, CancellationToken waitCancellation);
}
public sealed record WorkbenchEvidenceBytes(AssetRef Asset, ContractRef Contract,
    ImmutableArray<byte> Bytes);
public sealed record WorkbenchExportMeasurement(AcceptedMeasurementPlan Accepted,
    MeasurementResult Result);
public sealed record WorkbenchExportContent(ImmutableArray<AssetRef> RequestedEvidence,
    ImmutableArray<WorkbenchExportMeasurement> Measurements,
    ImmutableArray<WorkbenchEvidenceBytes> Evidence);
public interface IWorkbenchExportContentReader {
    ValueTask<WbResult<WorkbenchExportContent>> ReadAsync(MutationRequest original,
        CallContext call, CancellationToken cancellationToken);
}
public static class WorkbenchExportCodec {
    public static byte[] EncodeEvidenceBundle(WorkbenchExportContent content, ResourceProfile limits);
    public static byte[] EncodeCsvInvariant(WorkbenchExportContent content, ResourceProfile limits);
}
~~~

比较Owner构造同步RegisterChildOwner成功后才能接纳，遵循A.3/A.5有界槽、原Task排空规则。先两侧当前View/Compare权限（Core负责），再Reader核Key、OriginalResult、fingerprint和原Plan/Context；Reader只返回有界冻结值，不外传lease，内部借用真实归还才返回成功。全部原读任务退出后输出，找不到原闭包为NotFound，hash/单位/版本错用原错误，不返回自报SameDefinition。SameDefinition要求Result.Scope、Tool全字段、RequestContract、RequestTemplate、原Profile及ParameterSchema/Parameters/ParameterProfileBinding精确相等；本首版窄Reader不含模板正文，不同RequestTemplate即SameDefinition=false，Reason=definitionChanged，不猜“名称一样”。SameInputs要求Inputs/Coordinates/Roi逐声明值、顺序、hash等；定义不同仍显示两侧原投影。两轴及请求payload重放继续A.3规则，不新造单独历史。

Quantities按(CandidateId,Key)唯一，重复拒InvalidRequest；用两侧键的稳定union，先candidate再quantity Ordinal排序。只一侧存在Reason=leftMissing/rightMissing；两侧均存在依次检查definitionChanged、unitMismatch、valueMissing、invalidValue；均可配对Reason=paired。missing是不存在quantity/null Value，真实0不missing；先定位无量，再标有值但Invalid/Indeterminate，避免将缺值原因隐藏为普通无效。Entries完整保两侧QuantityProjection，不删无量/Invalid/Indeterminate；CompareResult没有差值字段，本具体Owner不计算delta、百分比、排名或“合格”。Differences为Plan不同字段的唯一稳定路径集合（以A.1声明名为段，数组用零基`[i]`，如`Inputs[0].Content.Sha256`），Scope不同时另加`Result.Scope`，Ordinal排序；Missing侧用本级字段路径，旧结果保持，不能从选中顺序反转历史事实。例：相同定义同单位Distance左0mm、右null/Indeterminate→一行valueMissing，左0完整保留；右candidate为另一ID则两行单侧，不能就近匹配。

导出仅为值codec；实际读取、工程目的地CAS/IO及StartSave/StartQuery属于注入EvidencePort。ExportContentReader在原Save job里核原Evidence请求每引用、当前View+Export、全部原bytes及其SHA-256/Contract；RequestedEvidence必须等原Mutation.Evidence顺序，不少/多。Measurements由请求内已选结果的原完整结果闭包得到，Accepted.Key/OriginalResult/fingerprint和Plan/Context逐项匹配；请求若没有可读结果则CSV拒InvalidRequest，EvidenceBundle仍可仅保原证据。每个RequestedEvidence至少有对应原byte资产，结果的OriginalResult与Result.Evidence、Plan各内容引用须可解析为bundle内Evidence或保持明确外部引用；外部引用不伪装为已打包原bytes。Evidence只按完整AssetRef去重，不按Id；同引用不同bytes为InputHashMismatch。不可读/超限/缺原闭包均零目的地写入，不做部分CSV/Bundle。未知格式/版本保原bytes只读，不重编码已知子集。

EvidenceBundle格式固定`mwb-evidence-bundle/1`，按WB-TLV-3域字符串→RequestedEvidence原序数组→Measurements数组→Evidence数组递归编码。Measurements按OperationKey两个Guid的RFC4122字节词典序排列，重复key拒绝；Evidence按Owner/Id Ordinal→Revision数值→Sha256 Ordinal排序。Accepted字段按声明序，其中Plan/Context递归原字段；Result及Quantity/Uncertainty亦逐声明序，MeasureValue union叶名ScalarValue/IntervalValue在前。**本导出域的double全部写原finite IEEE64 LE，保−0**；不套A.9请求hash的零规范化，不准NaN/Infinity。Evidence.Bytes为uint32长度+原bytes；不放bundle自身hash或目的地路径，SavedAsset.Sha256由Owner对整个bundle实际bytes算。编码不复制任意JSON，也不把未知Contract/原证据解释成计量结果。编码器核Result.Quantities唯一key、Scalar/Interval结构、Lower≤Upper、nullable有限数、Accepted与Result身份逐值一致；无量是null而不是非法浮点。

CSV固定UTF8无BOM、逗号、CRLF（末行也有CRLF），字段全加双引号，内部引号加倍；显示语言不入CSV，数值用InvariantCulture/R，bits用16位小写hex，null为`""`。列顺序恰：`operation,attempt,resultOwner,resultId,resultRevision,resultSha256,fingerprint,candidate,quantity,valueKind,scalar,lower,upper,scalarBits,lowerBits,upperBits,unit,validity,reason,supportOwner,supportId,supportRevision,supportSha256,uncertaintyStatus,standard,expanded,factor,probability,modelOwner,modelId,modelRevision,modelSha256,missingComponents,evidenceRefs`。每quantity一行，零quantity仍一行，仅Result身份/fingerprint及evidenceRefs非空，不捏造Quantity。排序同Bundle结果，再candidate/key；scalar与interval列互斥。missingComponents和evidenceRefs用严格JSON紧凑字符串（前者原字符串数组；后者原序AssetRef四字段对象，字段为owner/id/revision/sha256），JSON再按CSV引号规则转义；空数组为`[]`。Unit/Validity/Uncertainty用原enum名称；Uncertainty=null对应全部相关列空，非null完整保各nullable值/模型/缺项。CSV只保存投影，Full Plan/原bytes由EvidenceBundle保留，UI明确显示“结果表（CSV）/完整证据”。

CSV防公式解释只作用外部文本单元格：按.NET10 Char.IsWhiteSpace寻找首个非空白字符；若是`= + - @`或原首字符为TAB/CR/LF，则在原文本最前加单引号，其它文本保原。数值列/结构化JSON/规范Guid/hash/enum不加，正常负数仍数值；此是CSV展示转义，不改变证据或原结果hash。可逆识别需要原证据Bundle，CSV不作为重新执行输入。独立单元格向量：原文本`=1+1`→CSV bytes为`"'=1+1"`，原文本`a"b`→`"a""b"`，数值−0的文本`-0`及bits`8000000000000000`分别全引号，不能加防公式前缀。

完整CSV向量MWB-CSV-V01复用A.9 Golden的Plan/Key；Result按A.8 Replay结果字段定义，固定值1.5mm、CandidateId=replay、QuantityKey=Distance、ScalarValue/Valid，Support/Uncertainty=null、Reason=null、Result.Evidence=[]。其原ReplayResultContent为1115 bytes、SHA-256=`ae84d00895be23360a58a916d74d1433275eaa856f78249e596a67c3d2790d2e`，OriginalResult=(replay,result.11111111111111111111111111111111,1,此hash)，ResultFingerprint同hash；Accepted使用相同原Plan/Key/Context与结果身份。RequestedEvidence=[OriginalResult]，Evidence保原1115-byte ReplayResultContent，Contract=(replay.result,1)；Plan其它引用为显式外部fixture引用，不冒充现场原件。CSV第一行为上段34个列名（各全引号），第二行必须逐字符为下串；两行各CRLF、无BOM、无其它bytes，完整834 bytes，SHA-256=`e043cf4e0607f07ce86d9f5939a164c1d94fa3d177d7e08b8c275a70255f9be9`：

~~~csv
"11111111-1111-1111-1111-111111111111","22222222-2222-2222-2222-222222222222","replay","result.11111111111111111111111111111111","1","ae84d00895be23360a58a916d74d1433275eaa856f78249e596a67c3d2790d2e","ae84d00895be23360a58a916d74d1433275eaa856f78249e596a67c3d2790d2e","replay","Distance","ScalarValue","1.5","","","3ff8000000000000","","","Mm","Valid","","","","","","","","","","","","","","","","[]"
~~~

Reader与codec在分配前核MaxSources/MaxResults/MaxStringsUtf8Bytes/MaxRequestBytes/MaxResultBytes/MaxRetainedBytes，按checked完整计长，包括引用闭包、Schema/Plan/原bytes、输出及转义膨胀同时保留；输出byte[]不超过MaxResultBytes且uint32长度。Reader负责IO分批deadline/取消与内部租约真实归还，只返回有界不可变值；codec纯值不带token，不宣称运算可中断，数据和每项计数都受已接纳Profile约束。调用方在有界后台执行并持有**原编码Task**至退出；deadline只封后续目的地写入/采纳、不能释放仍在编码的任务槽，UI不在Dispatcher编码大文件。结构非法抛ArgumentException，超预算抛WorkbenchConfigurationException并按既有BudgetExceeded投影；无IO副作用。Save取得业务成功回执但job释放未知仍Unknown资源；写入未知用原Mutation key/完整payload查，不重编码不同格式或换目标“重试”。

#### A.11.4 自动参数的实际公开消费链

本版已有可消费的有限Replay比较/PE桥：IM-036§13.3的ReplayRecommendationPlan/ReplayTrial/ReplayParameterComparison，以及§13.4的ReplayParameterRecommendationProvider。§13.2的算法路线/挑战集条件继续适用，但旧泛述“没有自动参数产品API”不覆盖这两个已经具体冻结的工程Replay入口；本模块不发明Metrology.RecommendAsync、不运行无限寻优、不把数据驱动阈值当客户质量门。

工程Host先以原计量Host流程执行冻结候选×挑战集的完整计划，保每行结果、原key/hash、耗时/资源/真实ResourcesReleased，固定Profile/seed/ROI与输入；未派发/错误/取消/删失行也保在分母，不补成功。R1按原误接受/误拒绝/绝对误差及Gates.Authority计算ComparisonOnly/Eligible/排名，门缺失不能自动推值。只消费五字段完整EdgePair Schema Version2且selector=Unique；本模块Schema因ReadOnly省略字段、legacy四字段、Selector.All、候选含Model长度等都与该Provider不匹配，明确Unsupported。点距/场保持人工工程参数，不推荐数值/资格边界。

Provider用已冻结plan/trials/schema/baseline、版本包ContentRef(metrology.replay-parameters,1,真实包hash)、ReplayProviderOptions和TimeProvider显式构造，并在Host根持有。RecommendRequest.Profile准确取Applicability的Id/Invariant Revision/hash；Evidence恰`metrology.replay-plan`和`metrology.replay-trials`两个键，值Version1及原HashPlan/HashTrials，原source/ROI/Profile/真值证据已在闭包内，不另加零散证据使原Provider拒绝。MaximumCandidates取PE/Host两门最小值、Timeout有限。用CreateParameterEdit产生A.3 Recommend原资产请求→session.Edit→原PE RecommendAsync/GetOperation；UI读取原完整候选和Reason，不按confidence自动采纳；原操作Completed且ResourcesReleased、非HistoryOnly、当前generation/hash/授权相等才允许明确AcceptSuggestion。

Provider冻结的完整baseline必须等本次PE草稿规范值及原来源；编辑后与该baseline不同，不能沿旧trials推荐“当前值”，命令标为过期。Host可在显式绑定新工程Profile后，按A.10.3新基线流程创建对应新plan/trials/Provider/PE session，旧实例先保原操作并真实排空；不在旧PE session隐式换Provider或重基。无UI同样遵守此条件。

采用后只生成PE草稿及一次Undo；后续常驻“绑定参数”走A.11.2/A.10 Full/Patch/Publisher，用户再明确执行。推荐也能用无UI相同PE链，不要求Inspector初始化。无门/无Eligible/全部无变化为Abstained，列表为空、原值保持；误差/性能门来自工程挑战集Owner，实际尚无真值时只允许ComparisonOnly诊断，不声称推荐有效。Provider原Task/Drain/Dispose.GetSnapshot.Closed与PE操作排空由各自Owner强持；建议迟到、撤权、来源/hash变更、工具切换不改新草稿，未知清理不另建Provider绕账。

双消费者断言复用IM-036§13.4：2候选×2挑战，一项可量10mm及一项拒识；软件fixture误差0.1mm、FA/FR=0、其余门null，c0=10.25mm且错误接受拒识样本，c1=10mm且拒识正确，只有c1 Eligible。该例仅协议/排序断言，不是客户阈值。两个Host分别PE/Provider/计量根与原ID，建议采用只改各自草稿、零生产Apply/设备/Store动作；比较表不完整/伪Released/hash错/单位错/seed变即拒。实际算法效果/峰值/挑战集代表性另验，不将合成表升级资格。

#### A.11.5 WPF PageContract、布局、命令与视觉验收

§7的单主Surface规则按**实际嵌入control客户区**计算。屏幕固定1920×1080 pixels；记control实际客户宽高为W/H DIP，由VisualTreeHelper.GetDpi对应DpiScale换算，只读当前DPI、不改系统设置或扩大测试矩阵。顶部32+36、底部24共92 DIP为常驻chrome，可用工作区矩形为W×(H−92)，包含树、Inspector、结果和辅助面板，不以“扣掉所有侧栏”抬高占比。主Surface用其实际可见裁剪矩形面积，减被Flyout/浮动预览等覆盖面积的union，除上述工作区面积；同一时刻只计一张实际Surface，Chart/2D/3D切换不相加。popup瞬时操作过程单列，关闭popup后的默认/专注稳定布局分别必须≥60%/80%。工作区≤0拒挂载可操作页并显示空间不足，不创建隐藏第二窗口。

布局确定顺序：默认160左树/280右Inspector/96下结果→关闭非关键证据、图例、关联预览→下结果改32 DIP摘要并保“展开结果”→左树折为32 DIP入口→右Inspector折为32 DIP入口，逐步重算，达到60%即停；Inspector一次展开编辑时标为临时编辑布局，完成/取消后回稳定布局。专注模式关闭辅助面板、左右折32、下结果32，再按需要将左右入口放常驻命令区，直到80%；执行、取消、绑定参数、来源/工具、单位/状态和错误恢复始终可见。空间仍不足为compact只读/编辑布局并明确未满足本次验收，不声称达标；布局验收仅固定基线viewport的实际可用客户区。RestoreLayoutFromStream核白名单、版本和预算后仍按本规则纠正折叠，不能关主图或覆盖关键按钮。浮动在宿主可用边界内且保持当前三语，不借宿主全局Dock/Theme。

区域职责：顶部显示源身份/修订、工具、Scope、坐标单位；命令区常驻执行/取消/绑定参数，重算/比较/保存/导出相邻可见且Enabled原因明确；树显示稳定来源/ROI/工具键、锁/可见状态；主Surface显示实际原图/3D/剖面与当前选中候选Overlay；Inspector显示PE及省略字段只读区；结果区分原数值、单位、有效性、支撑/不确定度、来源修订与未绑定/历史标记；证据区显示完整原引用、输入差异和资源/持久化两轴，不以进度条代替释放ACK。主图保持最近合法图，迟到/失败标明旧输入，不自动清空。

只使用§7.2已核DevExpress组合：BarItem.Command/CommandParameter接上述命令桥，SuperTip由本模块Resources解析；panel AllowClose/AllowDrag/AllowFloat仅对许可辅助区开放，主Surface禁止关闭/浮走。TreeListView KeyFieldName/ParentFieldName用稳定ID，不以显示名作键；Chart Series.DataSource/ArgumentDataMember/ValueDataMember用原样本，gap拆独立Series，Crosshair以原索引绑定；候选Grid按稳定quantity键选中，不因sort/filter改变计算。主题用本实例ThemeManager.SetThemeName，取Host给定已安装主题；不设置全局ApplicationThemeName。采用主题资源颜色、8 DIP基础间距、正文最小12 DIP、主命令最小32 DIP高度、统一图标与文本；值右对齐单位固定，状态同时有文字/图标，不能只靠红绿。Busy仅用不遮图的状态标记，动效仅投影层，键盘可完成全部关键任务。

| Command key（workbench.command.前缀） | 前置、操作与键盘 | 稳定AutomationId末段 |
|---|---|---|
| execute | 合法精确Plan+Execute权+参数/输入已绑定；Ctrl+Enter，一次新Execute；不在IME/编辑/modal内触发 | command.execute |
| cancel | 本session已选未释放operation，取消原ID；Esc仅无编辑/菜单时触发，禁止取消另一实例 | command.cancel |
| bindParameters | PE Full有效、有实际变化、EditParameters权、无原发布未决；显式A.11.2，成功只SetDraft | command.bindParameters |
| recompute | 可披露原结果+Execute权+原完整Plan；F5 SameInputs，不读当前草稿；失效返回具体重绑定原因 | command.recompute |
| compare | 两侧已释放原结果+View/Compare权；显式A.11.3，选中键顺序保左/右 | command.compare |
| save / export | 当前View及Save/Export权、Host目的地CAS及完整原证据；格式/目的地确认后一次Save | command.save / command.export |
| restore | Created/Active且无未决、View权；原Checkpoint只读恢复，不重启历史operation | command.restore |
| recommend / acceptSuggestion | 匹配Provider+完整证据/预算/PE合法；候选已释放且当前基线/权限匹配才允许显式采用 | command.recommend / command.acceptSuggestion |
| resolve | 持久化Unknown且原Mutation完整保存；仅Query原ID/原载荷，不能再次保存 | command.resolve |
| focus / showResults | 只改布局/投影；专注可逆；展开结果将焦点送到原选中行，不改ROI/参数 | command.focus / command.showResults |

Prefix+实例ID由A.7 MountOptions提供；tree节点为`tree.<asset/node/tool稳定键>`，Surface为`surface.<SurfaceId>`，参数为`parameter.<key>`、只读字段为`baseline.<key>`，结果为`result.<operation>.<candidate>.<quantity>`，动态键UTF8 percent-encode、禁止碰撞。局部Tab/ShiftTab顺序遵§7.3，菜单Esc关闭后恢复触发按钮焦点，错误定位把焦点交给有错参数并保原token。失焦/capture lost取消Preview；异步UI更新在原Dispatcher，epoch及presentation revision核过再投影。无映射联动保当前选择并显示NoMapping；插值标识常驻，不能替换原样本；多candidate必须明确选，不默认首项。Owner的ROI/PE Undo独立，历史不因语言/折叠变化新增。

##### A.11.5.1 直接消费 viewport 0.3.4-prep / WPF Assembly Contract v0.2

本模块确实通过A.7 PublicOwnerUiChildrenFactory直接消费ViewportControl；本小节取代A.7中旧的省略接线说法，保持其公开ViewportUiOwner/工厂/Mount声明和Root/Close协议，不重造视口资源Owner。上游唯一正文是[viewport指导](../viewport/DEVELOPMENT-GUIDE.md)§10.6–10.9/20.4；Core API0.1不变，WPF Assembly Contract v0.2与资源schema viewport-ui-text/1分别绑定，不声称未实现程序集已经有成员。

1. Host在相同STA/Dispatcher上构造实际ViewportControl，先取得`((IViewportControlBinding)control).Presentation`稳定转发端口，再创建视口session；原Options.Presentation必须是该端口。若使用上游内置renderer，显式`ViewportRendererFactory.Create(control,viewportRoot,rendererOptions)`，成功后同一返回值Backend给原Options.Backend、Lifetime给ViewportUiBindingOptions.Lifetime。资源/Policy/baseline/raster/任务容量取Host冻结Profile，不能反射其它源payload或用本模块UIRoot账冒原native准入；自有renderer同样实现原三个公开端口、同Control/root，禁止交叉实例。
2. Host调用`ViewportUiResourceCatalog.Get(ResourceCulture)`，核Succeeded+完整Value、RequiredKeys及Revision=viewport-ui-text/1，再传ViewportUiOwner.Options；OwnSession=false、Lifetime显式非null、ExecutionBudget由Host为原root/session明确批准。未知语言仅用Host完整自定义快照，Catalog失败不能拿本模块en-US单key回退拼成上游完整包。本模块自己的IWorkbenchTextResources回退规则不改变上游原子缺键拒绝。
3. PublicOwnerUiChildrenFactory在工作台原UI槽内调用同Control.BindAsync(Session,Root,Options)，保留**原Bind Task**、成功IViewportUiBinding及MainSurface同一实际Control；Bind只InstallEmpty，不Acquire/Attach/测量。UI Bound只表示装配成功。之后Host原视口Session.Attach/真实提交沿上游端口；control.Presentation直接转交同binding原Commit/Revoke Task，不用async wrapper替换，也不从薄WorkbenchContext构造缺字段ViewportContext。
4. 原binding.GetPresentations()仅观察原PresentationRequest/SourceCall、OriginalCommit/Acquire/Confirm/Revoke/Return、PresenterIdentity及Cleanup，不授Host手动Return权。匹配binding、submission/presentation ID、display/backend generation、原context/授权/有限deadline且实际ConfirmVisibleAsync成功才投影可见；property赋值、Dispatcher完成、Rendering事件、工作台UiReceipt.Bound均不能代替VisibleConfirmed。失败/取消/晚到/授权失效仍保原trace与上游lease，旧代不装入新主图；Workbench不重复Acquire/Return/clear_window。
5. UiChildren.Lifetime.SetPresentationAsync对**已保留binding**调用原`SetResourcesAsync(完整catalog快照,剩余观察期限,ct)`，PE用原SetPresentationAsync；不调用不存在的ViewportControl.SetResourcesAsync。以当前binding/presentation revision串行更新，全部预检后派发；任一child失败，不提升工作台revision，已成功child用原完整旧快照恢复，恢复未知为CleanupUnknown并保原Task，不谎称整个更新原子成功。保原IME/token/gesture策略，不读latest资产或重跑量测。
6. Detach封新命令/退订/capture→原Dispatcher移除本模块视觉引用→原binding.UnbindAsync(剩余有限观察期限,ct)，保原Unbind Task；只有Detached&&Drained且原cleanup/Presenter/source读引用与回调实际收敛，PE及工作台自身Task也退出，才本child Released。WaitCancelled、OwnerAccepted、观察到期或Dispatcher退出都不是Drained。Revoke/Return由原同presentation Owner幂等单飞；迟到Acquire lease由原root登记并真实归还，工作台继续持有原binding/control/task/slot，不自行第二次Return。OwnSession=false不Close/Dispose视口session/root/Lifetime服务；Host最后按原Owner责任关闭。不改变A.5/A.7已有Root.Close，不在worker内等待自身，不用新Control/binding逃Unknown。

为外部Host和本模块真实UI验证暴露只读加法方法：`PublicOwnerUiChildrenFactory.GetViewportPresentations()`返回`IReadOnlyList<Asun.UI.Viewports.Wpf.ViewportUiPresentationTrace>`，直取其已保留原binding的有界不可变快照；未Bind成功返回空，但空不证明显示/释放。工厂不重新包装原Task，不序列化trace/lease，不让调用方操作Presenter；返回元数据/引用计本工作台预算，上游原ledger仍为资源权威。本节既不重算视口Core/C5向量，也不把新版装配文档当真实renderer、HALCON/GPU/WPF运行通过。

#### A.11.6 三语资源、状态和恢复

下表为随Wpf包DefaultWorkbenchTextResources的最小完整资源正文，Host可覆盖相同key但不改语义。`workbench.command.<key>`也作为对应UIA Name；SuperTip标题用同名、正文用A.11.5对应前置及本节恢复词，三语均直接描述动作。不显示内部key、Profile或参数值猜测；上游原PE/Viewport/Metrology资源继续由其Owner三语包解析，本模块不重写原错误Code。

| key（workbench.command.） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| execute | 测量 | 量測 | Measure |
| cancel | 取消 | 取消 | Cancel |
| bindParameters | 绑定参数 | 綁定參數 | Bind parameters |
| recompute | 按原输入重算 | 依原輸入重算 | Recompute original inputs |
| compare | 比较结果 | 比較結果 | Compare results |
| save | 保存证据 | 儲存證據 | Save evidence |
| export | 导出 | 匯出 | Export |
| restore | 恢复记录 | 還原記錄 | Restore record |
| recommend | 参数建议 | 參數建議 | Suggest parameters |
| acceptSuggestion | 采用所选建议 | 採用所選建議 | Accept selected suggestion |
| resolve | 查询原回执 | 查詢原回執 | Query original receipt |
| focus | 专注视图 | 專注檢視 | Focus view |
| showResults | 展开结果 | 展開結果 | Show results |

| key（workbench.label.，parameters除外） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| source / tool / unit | 来源 / 工具 / 单位 | 來源 / 工具 / 單位 | Source / Tool / Unit |
| results / evidence / differences | 结果 / 证据 / 输入差异 | 結果 / 證據 / 輸入差異 | Results / Evidence / Input differences |
| candidate / support / uncertainty | 候选 / 支撑 / 不确定度 | 候選 / 支撐 / 不確定度 | Candidate / Support / Uncertainty |
| parameters（key为workbench.parameters） | 参数 | 參數 | Parameters |
| parametersUnbound / inputsUnbound | 参数未绑定 / 输入未绑定 | 參數未綁定 / 輸入未綁定 | Parameters not bound / Inputs not bound |
| history / readOnly / interpolated | 历史输入 / 只读 / 插值显示 | 歷史輸入 / 唯讀 / 插值顯示 | Historical inputs / Read only / Interpolated display |
| noMapping / noValue / disconnected | 无坐标映射 / 无有效值 / 未连接 | 無座標映射 / 無有效值 / 未連接 | No coordinate mapping / No valid value / Not connected |
| csv / bundle | 结果表（CSV） / 完整证据 | 結果表（CSV） / 完整證據 | Result table (CSV) / Complete evidence |
| retainDraft / cancelSwitch | 保留草稿并切换 / 取消切换 | 保留草稿並切換 / 取消切換 | Keep draft and switch / Cancel switch |
| originalValue / spaceInsufficient | 原始值 / 显示空间不足 | 原始值 / 顯示空間不足 | Original value / Insufficient display space |

参数key沿A.10.2；每行对应`workbench.<tool>.<key>.name`和`.help`，tool为point-distance/image-edge-pair/field-distribution。help不代替原范围验证：

| tool/key | name：zh-CN / zh-TW / en-US | help：zh-CN / zh-TW / en-US |
|---|---|---|
| point-distance/length_tolerance | 数值长度容限 / 數值長度容限 / Numeric length tolerance | 数值计算容限，单位mm；不作产品公差。 / 數值計算容限，單位mm；不用作產品公差。 / Numeric tolerance in mm; no product tolerance. |
| image-edge-pair/sigma_px | 平滑宽度 / 平滑寬度 / Smoothing width | 单位px；范围0.4至100，并受搜索矩形限制。 / 單位px；範圍0.4至100，並受搜尋矩形限制。 / In px; 0.4 to 100, limited by the search rectangle. |
| image-edge-pair/threshold | 梯度阈值 / 梯度閾值 / Gradient threshold | Byte图像梯度门，范围1至255。 / Byte影像梯度門，範圍1至255。 / Byte image gradient threshold, 1 to 255. |
| image-edge-pair/transition | 边缘方向 / 邊緣方向 / Edge transition | 选择原算法的边缘方向与强边策略。 / 選擇原演算法的邊緣方向與強邊策略。 / Select the original edge transition and strongest-edge rule. |
| image-edge-pair/interpolation | 采样插值 / 取樣插值 / Sampling interpolation | 只改采样方法，不补孔洞或扩大有效域。 / 只改取樣方法，不補孔洞或擴大有效域。 / Changes sampling; keeps holes and the valid domain. |
| image-edge-pair/selector | 候选选择 / 候選選擇 / Candidate selection | 唯一候选或全部候选；多解不默认取第一项。 / 唯一候選或全部候選；多解不預設取第一項。 / Unique or all candidates; multiple results require selection. |
| field-distribution/coverage | 覆盖要求 / 覆蓋要求 / Coverage requirement | 完整目标须有原域资格；局部仅作诊断。 / 完整目標須有原域資格；局部僅供診斷。 / Full target needs original domain qualification; known part is diagnostic. |
| field-distribution/transform | 分布变量 / 分布變數 / Distribution variable | 只影响CDF和分位数，不改变积分四量。 / 只影響CDF與分位數，不改變積分四量。 / Affects CDF and quantiles; keeps the four integral quantities. |
| field-distribution/cdf_height | CDF高度 / CDF高度 / CDF height | 单位mm；保留原模型和支撑域。 / 單位mm；保留原模型與支撐域。 / In mm; keeps the original model and support domain. |
| field-distribution/probability | 分位概率 / 分位機率 / Quantile probability | 范围0至1；不是百分数输入。 / 範圍0至1；不是百分數輸入。 / From 0 to 1; enter a ratio. |

枚举name资源由实际AllowedValue各自key指向`workbench.enum.<name>`：All=全部/全部/All，Positive=正向/正向/Positive，Negative=负向/負向/Negative，AllStrongest=全部最强/全部最強/Strongest of all，PositiveStrongest=正向最强/正向最強/Strongest positive，NegativeStrongest=负向最强/負向最強/Strongest negative，Nearest=最近邻/最近鄰/Nearest，Bilinear=双线性/雙線性/Bilinear，Bicubic=双三次/雙三次/Bicubic，Unique=唯一/唯一/Unique，FullTarget=完整目标/完整目標/Full target，KnownPartDiagnostic=已知局部诊断/已知局部診斷/Known part diagnostic，Signed=有符号高度/帶符號高度/Signed height，PositiveOnSameDomain=同域正值分布/同域正值分布/Positive values on the same domain。工具名用A.10.2三语，工具help用本表对应参数help与A.10.1范围，不宣称精度或“智能优化”。单位资源固定Pixel=px、Pixel2=px²、Mm=mm、Mm2=mm²、Mm3=mm³、Mm4=mm⁴、Rad=rad、Ratio=1，三语符号相同。

工具NameResourceKey/HelpResourceKey固定`workbench.tool.<ToolId>.name/help`，name用A.10.2三语；help分别为：点距“测量两个原点的距离，单位mm。/量測兩個原始點的距離，單位mm。/Measure the distance between two source points in mm.”，边距“测量Byte图像两边缘的距离，保留原支撑与候选。/量測Byte影像兩邊緣的距離，保留原支撐與候選。/Measure two edges in a Byte image; retain their support and candidates.”，场分布“显示原连续场的积分、CDF与分位区间。/顯示原連續場的積分、CDF與分位區間。/Show the original field integrals, CDF and quantile intervals.”。不改变Replay旧工具资源键，未知注册工具必须由原工具Owner完整三语资源及原Profile/template支持，不能生成猜测性说明。

显示输入类型/模式时资源为`workbench.kind.<name>`：Geometry=几何/幾何/Geometry，Image2D=二维图像/二維影像/2D image，RegionRuns2D=二维区域/二維區域/2D region，Contours2D=二维轮廓/二維輪廓/2D contours，TilePyramid2D=分块金字塔/分塊金字塔/Tile pyramid，HeightField3D=高度场/高度場/Height field，PointCloud3D=点云/點雲/Point cloud，TriangleMesh3D=三角网格/三角網格/Triangle mesh，ContinuousField3D=连续场/連續場/Continuous field，ColumnRowPixelCenters=列行像素中心/欄列像素中心/Column-row pixel centers，RightHandedXY=右手XY/右手XY/Right-handed XY，RightHandedXYZ=右手XYZ/右手XYZ/Right-handed XYZ，Original=原样本/原始樣本/Original sample，ExplicitLevel=指定层级/指定層級/Explicit level，InterpolatedDiagnostic=插值诊断/插值診斷/Interpolated diagnostic，EngineeringEditable=工程编辑/工程編輯/Engineering edit，EvidenceReadOnly=证据只读/證據唯讀/Read-only evidence。PointerTool按钮文字沿Viewport完整资源；工作台独有DrawRoi/EditRoi对应workbench.pointer.DrawRoi/EditRoi=绘制ROI/编辑ROI、繪製ROI/編輯ROI、Draw ROI/Edit ROI，Profile=剖面/剖面/Profile，三者仍遵§7.3的原Owner操作门。

所有WorkbenchErrorCode对应`workbench.error.<Code>`/`workbench.recovery.<Code>`；参数args只能通过已授权安全字段投影，原敏感值不插入资源。以下斜线前是error，后是recovery：

| Code | zh-CN | zh-TW | en-US |
|---|---|---|---|
| InvalidRequest | 输入不完整或无效。 / 修正已标记的输入。 | 輸入不完整或無效。 / 修正已標記的輸入。 | Input is incomplete or invalid. / Correct the marked input. |
| IdentityConflict | 同一请求标识对应不同内容。 / 查询原请求；新操作使用新标识。 | 同一請求識別碼對應不同內容。 / 查詢原請求；新操作使用新識別碼。 | Request ID has different content. / Query the original; use a new ID for new work. |
| StaleBinding | 输入或参数绑定已过期。 / 重新选择完整输入并绑定参数。 | 輸入或參數綁定已過期。 / 重新選取完整輸入並綁定參數。 | Input or parameter binding is stale. / Select complete inputs and bind parameters again. |
| Unauthorized | 当前权限不允许此操作。 / 使用有权限的身份继续。 | 目前權限不允許此操作。 / 使用有權限的身分繼續。 | Current access does not allow this action. / Continue with authorized access. |
| Unsupported | 当前组合不受支持。 / 选择已支持的工具、格式或输入。 | 目前組合不受支援。 / 選取已支援的工具、格式或輸入。 | This combination is unsupported. / Select a supported tool, format or input. |
| InputUnavailable | 原输入不可读取。 / 恢复原来源或明确选择新输入。 | 原輸入無法讀取。 / 恢復原來源或明確選取新輸入。 | Original input is unavailable. / Restore its source or explicitly select new input. |
| InputHashMismatch | 原内容与引用摘要不一致。 / 核对原证据，不执行此输入。 | 原內容與引用摘要不一致。 / 核對原證據，不執行此輸入。 | Content does not match its hash. / Verify the original evidence before execution. |
| CoordinateMismatch | 坐标或单位不匹配。 / 提供原Owner确认的映射与单位。 | 座標或單位不符。 / 提供原Owner確認的映射與單位。 | Coordinates or units do not match. / Provide the original owner's mapping and units. |
| VersionMismatch | 契约版本不匹配。 / 使用匹配版本；原记录只读保留。 | 契約版本不符。 / 使用相符版本；原記錄唯讀保留。 | Contract versions do not match. / Use matching versions; keep the original read only. |
| BudgetExceeded | 已达到本会话资源上限。 / 等待原任务归还资源或调整已批准Profile。 | 已達本工作階段資源上限。 / 等待原工作歸還資源或調整已核准Profile。 | Session resource limit reached. / Wait for resource release or adjust the approved profile. |
| DeadlineExceeded | 操作超过执行期限。 / 查询原状态，确认归还后再新建操作。 | 操作超過執行期限。 / 查詢原狀態，確認歸還後再建立操作。 | Execution deadline exceeded. / Query the original; start new work after release. |
| Cancelled | 已请求取消。 / 等待原任务退出和资源归还。 | 已要求取消。 / 等待原工作退出與資源歸還。 | Cancellation requested. / Wait for the original work to exit and release resources. |
| BackendFailure | 原后端操作失败。 / 查看原诊断，按原Owner恢复步骤处理。 | 原後端操作失敗。 / 查看原診斷，依原Owner還原步驟處理。 | Original backend failed. / Review its diagnostics and recovery steps. |
| PersistenceFailure | 保存未确认成功。 / 查询原回执，不重复保存。 | 儲存尚未確認成功。 / 查詢原回執，不重複儲存。 | Save success is unconfirmed. / Query the original receipt; do not save again. |
| DrainUnknown | 原任务退出状态未知。 / 保留原任务并继续查询。 | 原工作退出狀態未知。 / 保留原工作並繼續查詢。 | Original work exit is unknown. / Retain the work and keep querying. |
| ReleaseUnknown | 资源归还状态未知。 / 保留原Owner，不释放槽位。 | 資源歸還狀態未知。 / 保留原Owner，不釋放槽位。 | Resource release is unknown. / Retain the owner and its reserved slot. |
| CleanupUnknown | 界面清理状态未知。 / 保留原窗口绑定，等待原Dispatcher确认。 | 介面清理狀態未知。 / 保留原視窗綁定，等待原Dispatcher確認。 | UI cleanup is unknown. / Retain the binding and wait for its dispatcher acknowledgement. |
| NotFound | 找不到原记录或内容。 / 核对原标识和证据位置。 | 找不到原記錄或內容。 / 核對原識別碼與證據位置。 | Original record or content was not found. / Verify its ID and evidence location. |

所有可见状态使用`workbench.state.<name>`。相同enum字面共享词义；这些词不替代两轴状态：

| name | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Created | 已创建 | 已建立 | Created |
| Attaching / Mounting | 正在连接 / 正在挂载 | 正在連接 / 正在掛載 | Attaching / Mounting |
| Active / Bound | 可操作 / 已绑定 | 可操作 / 已綁定 | Active / Bound |
| Rebinding / Closing / Closed | 正在重新绑定 / 正在关闭 / 已关闭 | 正在重新綁定 / 正在關閉 / 已關閉 | Rebinding / Closing / Closed |
| Accepted / Preparing / Executing | 已接纳 / 正在准备 / 正在执行 | 已接納 / 正在準備 / 正在執行 | Accepted / Preparing / Executing |
| ResultAvailable / LogicalFailed | 结果已到达 / 逻辑操作失败 | 結果已到達 / 邏輯操作失敗 | Result available / Logical operation failed |
| CancelRequested / Cancelled | 已请求取消 / 已取消 | 已要求取消 / 已取消 | Cancellation requested / Cancelled |
| Draining / Drained / DrainUnknown | 正在等待退出 / 已退出 / 退出未知 | 正在等待退出 / 已退出 / 退出未知 | Draining / Drained / Drain unknown |
| ReleaseUnknown / ResourcesReleased / Released | 归还未知 / 资源已归还 / 已归还 | 歸還未知 / 資源已歸還 / 已歸還 | Release unknown / Resources released / Released |
| Completed / Rejected / TimedOut / Failed / Unknown | 已完成 / 已拒绝 / 已超时 / 已失败 / 未知 | 已完成 / 已拒絕 / 已逾時 / 已失敗 / 未知 | Completed / Rejected / Timed out / Failed / Unknown |
| Measured / Partial / Unevaluated | 已测量 / 部分结果 / 未评价 | 已量測 / 部分結果 / 未評估 | Measured / Partial / Unevaluated |
| InvalidInput / Unsupported / Unqualified / ResourceLimited | 输入无效 / 不支持 / 资格不足 / 资源受限 | 輸入無效 / 不支援 / 資格不足 / 資源受限 | Invalid input / Unsupported / Unqualified / Resource limited |
| Valid / Invalid / Indeterminate | 有效 / 无效 / 不确定 | 有效 / 無效 / 不確定 | Valid / Invalid / Indeterminate |
| Running / ExitUnknown / Exited | 正在运行 / 退出未知 / 已退出 | 正在執行 / 退出未知 / 已退出 | Running / Exit unknown / Exited |
| Pending / Succeeded | 待确认 / 已成功 | 待確認 / 已成功 | Pending / Succeeded |
| CleanupUnknown | 界面清理未知 | 介面清理未知 | UI cleanup unknown |
| NotProvided / NotEvaluable / Propagated | 未提供 / 无法评价 / 已传播 | 未提供 / 無法評估 / 已傳播 | Not provided / Not evaluable / Propagated |
| Complete / Engineering / CalibratedPhysical / PixelDiagnostic | 支撑完整 / 工程测量 / 标定物理测量 / 像素诊断 | 支撐完整 / 工程量測 / 校正物理量測 / 像素診斷 | Complete support / Engineering / Calibrated physical / Pixel diagnostic |
| Abstained / Candidates / ComparisonOnly / Recommended | 无可用建议 / 建议候选 / 仅比较 / 有可用建议 | 無可用建議 / 建議候選 / 僅比較 / 有可用建議 | Abstained / Candidates / Comparison only / Recommended |
| leftMissing / rightMissing / definitionChanged / unitMismatch / invalidValue / valueMissing / paired | 左侧缺项 / 右侧缺项 / 定义不同 / 单位不同 / 值无效 / 无量 / 已配对 | 左側缺項 / 右側缺項 / 定義不同 / 單位不同 / 值無效 / 無量 / 已配對 | Left missing / Right missing / Definition changed / Unit mismatch / Invalid value / Value missing / Paired |
| Preserved / Converted / ReadOnly / BoundaryRejected / DecimalRangeExceeded / OverflowRejected | 保留原值 / 已转换 / 只读 / 超出边界 / 超出Decimal范围 / 转换超限 | 保留原值 / 已轉換 / 唯讀 / 超出邊界 / 超出Decimal範圍 / 轉換超限 | Preserved / Converted / Read only / Boundary rejected / Decimal range exceeded / Conversion overflow |

多key一行按斜线一一对应，不生成带斜线的复合key。Scope/支撑/业务结果/资源状态分栏展示；例如Measured+ReleaseUnknown仍写“已测量；归还未知”，不显示Completed。Missing数值显示短横线并附原Reason，不显示0。ReadOnly数值原因用“原值无法映射到可编辑Decimal。/原值無法映射至可編輯Decimal。/Original value cannot be represented by editable Decimal.”，恢复用“保留原值；可编辑其它参数。/保留原值；可編輯其他參數。/Keep the original value; edit other parameters.”，资源键为workbench.numeric.readOnly及workbench.numeric.keepOriginal。

语言切换由Host SetPresentation触发：zh-CN/zh-TW/en-US实例资源连同Popup/SuperTip/Chart/UIA同revision更新，FormatCulture只影响显示，A.9/A.11 codec不变。IME或未确认token保启动culture，提交/取消后再显示新culture；缺keyen-US回退并诊断，三语默认包本表所有键不得缺失。三语实测英文最长命令与恢复段不截关键动作、键盘焦点可达，两实例不同语言不互改；不在模块另放语言入口。

#### A.11.7 验证计划、负载和文档反例

本节绑定已有§9.2的T01–T15及§3.1唯一工程，不新建平行验证体系。Core继续A.8两CLI Host/A.9 Golden；Adapters组扩展数值/Schema/Publisher、比较与codec、来源/推荐；Wpf组扩展真实双STA/实际Surface、CommandBinding与三语/焦点。后续执行命令仍DEV-GOV-010的BCL Exe约定；文档阶段本轮不执行产品测试，不能以结构检查充当这些断言通过。

| 已有组 | 本增量必须具备的可判定断言 |
|---|---|
| T02/T04/T06 | cdf_height=1e308只读省略，probability 0.5→0.7可Full/Patch/发布且原cdf bits不变；非法原Profile仍拒；空可编辑Schema不建Patch。PE提交后执行禁用，绑定成功才启用；发布后PE再变代次则不SetDraft，旧Plan/原发布job保留；零Apply |
| T03/T07/T12 | Compare原Plan reader缺闭包拒；不同candidate不匹配；同单位0与null无差值；字段Differences稳定。CSV含引号、换行、公式文本、负数/−0/null/interval；Bundle原bytes/hash和版本完整，MaxResultBytes+1零写入；Unknown仅查原Mutation |
| T06/T09/T10 | 原R1/R2完整候选×挑战表、无门ComparisonOnly/Abstained、过期/撤权/回调未退；A/B独立根、Provider/PE不同ID，未知释放不新建Provider/新绑定绕账 |
| T09–T11/T14/T15 | 双STA 1920×1080固定viewport实际client/DPI；默认/专注面积、折叠顺序、三语最长词、Tab/IME/焦点CtrlZ、跨实例取消、popup/SuperTip/动态资源/UIA、失焦/capture lost。viewport同Control Presentation/Backend/Lifetime，缺Lifetime/资源键或错root在零Acquire前拒；原Task identity不替换，VisibleConfirmed=false不算呈现；晚到lease走原Revoke/Return。工具切换清理Unknown不重Mount；真实UI任务/child/root ACK，与原槽同时保留 |

Benchmark用A.9 BenchmarkPlan原字段填**实际冻结负载**，至少覆盖下列四组，每组同样跑正确性断言后再测；统计继续DEV-GOV-010 §3.1唯一算法：

1. 无UI组合：一组取A.9明确几何2点/单结果，一组取Profile.MaxSources/MaxParameters/MaxResults的合法边界资产；合法上限完成，任何Max+1在零下游派发拒BudgetExceeded，不能编错误定义来凑边界。单/双Host并发分别计session/operation/订阅/原任务/保留字节，迟缓subscriber按原事件bounded策略且结果可Query。
2. 实际算法与来源：原Byte图ImageEdgePair、C5多parent/Q/Field分别取已采纳输入hash/真实尺寸/ROI与域；含孔洞、多candidate/拒识和完整与部分支撑。测source/coordinate/参数绑定/validator/Measure/Release分阶段及Accepted→ResourcesReleased端到端，不能只量HALCON kernel。算法效果与性能必须同一冻结Profile/原输入资格，不采用显示LOD。
3. 存储与推荐：完整Bundle/CSV同时计原证据+输出/转义膨胀；CAS冲突、写入成功回执丢失只Query，失败不写部分。R1候选×挑战完整分母、warmup/measurement原plan、PE候选/绑定/撤权；计Provider/回调退出，不仅耗时R1纯排序。
4. UI投影：固定实际主图、1920×1080viewport，正常与Profile批准最大结果/Overlay/剖面区间；语言/选择/工具切换、连续Preview后取消/Detach。测最后真实呈现ACK及Dispatcher积压、managed/native/GPU峰值，主图不被迟到旧代覆盖，业务结果/资源两轴可见；两实例分别计账。

WarmupRuns/MeasurementRuns/MinimumCompleteSamples、冷/热、有限deadline、P95/P99、CancelToReleased、资源和LongRunDuration由已采纳消费者Profile原Authority提供。未有这些实际target可诊断但NotEvaluated；没有source/真实算法回执不以合成行填真实性能。观测未完成/失败/删失/资源未知保分母和原因，不删慢行，不用新Root重跑替换失败。关闭成功要求原操作、Provider、UI/Dispatcher、source/child所有真实任务退出并归还，缺任一ACK仍NotReady。

#### A.11.8 全模块结论、范围映射与剩余门

0.7.0的内容审核对象是IM-065完整已批准范围，非仅Core或最后数值切片；本原永久会话已经补齐所有从现有架构/指导/公开证据可决定的软件语义。允许写入仅本指导；不扫描AsunImage内部、不改其它Owner指导/共享调度文件，不创建子会话、产品工程、脚本或重复报告。A.1–A.9冻结Core/Host/Golden保持；既有A.10.10规则/oracle与ROI值向量保持。新增三语/命令/codec/推荐接线是同模块软件规格，不授生产Apply/设备/产品事实权限。

| 全批准范围 | 唯一实施章节/输入输出与断言 | 当前准确结论 |
|---|---|---|
| 会话/授权/epoch/执行/事件/幂等/取消/两轴恢复与资源强持 | §3–6、A.1–A.5/A.8/A.9、T01/T09–T11/T15 | C1/C2既有ModuleCoreImplementationReady保持；未实现运行 |
| 工具目录、ROI/参数草稿、三个固定工具完整转换与receipt、推荐显式采用 | §4/8、A.6/A.10.1–3/8/10、A.11.1/2/4、T02/T04/T06 | 可决定软件设计闭合，A1已有公开映射接收保持；不泛化其它工具 |
| C5多父、reference/Q/ContinuousField与资格、跨进程ROI codec | A.10.4–7/9、原Owner合同、T02/T05/T08/T14 | 完整公开消费与拒绝边界已明确；真实性与实际消费另验 |
| 重算/比较、Checkpoint、保存/导出、未知写入原请求Query | §4.3–4.4、A.3/A.4/A.9、A.11.3、T03/T07/T12/T13 | 定义/输入与结果原闭包、格式/CAS/失败语义闭合，实际IO另验 |
| 可选完整WPF/DevExpress工作台、工具/键盘/焦点/UIA、三语/布局/Overlay/剖面/Detach | §7、A.7/A.8/A.10.7、A.11.2/5/6、T14/T15 | PageContract软件设计闭合；U1原装配/恢复接收保持，真实WPF未验 |
| 两无UI与双STA消费者、独立发布/Host接入与性能/异常/资源验收 | §2/3/9、A.5/A.8/A.9/A.10.7、A.11.7 | 调用与验证方法闭合；未冒称两个客户产品或性能达标 |

本模块不再有需由普通程序员补猜的内部设计项，也不再等待总控内容审核。**全部批准范围的软件准备已闭合**与**整模块集成/运行PreparationIncomplete / NotReady**同时成立，后者仅由以下受影响输入/执行证据决定：

- Host实际提供完整已冻结Plan/Profile/template及工程Parameter/Profile/receipt发布Owner、AcceptedPlan/原证据读取Owner、目的地CAS/权限配置；这些端口及本模块应执行的消费步骤已明确，实际接入值不得以latest或假引用替代。无真实目的地只阻实际保存/导出，不阻Core/value codec。
- Source/SurfaceData/Contribution/ReferenceSurface的真实内容/域/资格/原证据、IWorkbenchSurfaceEvidenceReader及Metrology原reader/service/Validator回执按A.6/A.10读取；不在本模块生成物理资格。缺真实输入仅阻依赖它的算法/来源运行，几何工程诊断及协议fixture仍可独立验证。
- 对应公开程序集的实际消费者编译、Core/Adapters契约与异常/资源测试、真实HALCON/Golden/Replay、1920×1080实际WPF/DevExpress/UIA/三语及双Host均未执行；性能数值/长稳/资源门须已采纳消费者Profile，缺目标为NotEvaluated。AsunImage/DevExpress按用户已冻结依赖直接消费，不新增安装、兼容或授权核验待办。
- 客户物理真值/精度/公差/节拍/现场验收只由真实消费者/计量/设备Owner提供；仅依赖这些资格的产品切片等待相应外部证据，不阻纯Core、工程软件流程或本次文档收口。

本轮有限自审按操作者正常链及外部集成人失败链完成：编辑→绑定→Measure→重算/比较→证据→关闭；极端只读、空Schema、发布迟到、推荐无门/过期、不同candidate/null、导出缺原证据/CAS未知、IME/语言/工具切换/清理未知与两个Host独立Owner。发现的Schema必填阻断、转换集合self hash、命令接线缺失、比较原Plan来源、CSV/Bundle内容、旧自动参数泛述及布局面积分母均在正文修正。实际文档验证结果在下段记录；没有产品运行或物理资格结论。

2026-10-11定向文档验证：A.1–A.9逐节摘要与冻结基线一致，A.10.10正文摘要一致（仅排除追加章节分隔空行）；原Execute 1098-byte、ROI 688-byte、规则175-byte及oracle1750-byte原文/摘要保持。A.11.1空集合预像独立重建为121 bytes、SHA-256=`5764a55f82781b7c9dd71c62e744e1d34d2a3fdaede7e882f57e9b3f6759a12b`；MWB-CSV-V01从原Plan与Replay内容独立构造，34列、834 bytes、CRLF/完整摘要与正文一致，原引号/换行/公式文本/负数及−0 bits单元格反例核对。18项Workbench错误/恢复、可见状态枚举和三语分组键覆盖一致，新增公开类型无重复、viewport直接消费声明与原§10.6–10.9一致；本页标题/围栏/本地权威链接通过。比较null/Indeterminate反例已将valueMissing优先于invalidValue，Scope差异明确进Differences。以上是内存规范字节/字段和文本检查，未执行.NET转换器、产品构建/测试、WPF/HALCON、实际IO、Golden算法运行、真实性能或现场验收；不新增辅助文件。达到本模块全部批准范围的文档准备准则后停止，不扩展未批准能力。
