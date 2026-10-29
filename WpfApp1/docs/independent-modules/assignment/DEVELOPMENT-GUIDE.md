# 有界二部图分配（assignment）开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2, C3, C4`

- 模块 ID：`IM-037`
- 来源指导：`PKG-062`（当前 `0.2.3-prep`）
- 本文版本：`0.1.2-prep`（2026-10-11 全批准范围文档收口）
- 文档状态：`DesignReview / Prep`
- 技术基线：C# / .NET 10；可在无 UI、无图像、无设备宿主中运行
- 规划消费者：钻孔候选关联、微孔候选关联、通用几何候选关联工具
- 允许写入范围：本目录；本文是本模块唯一活动实施指导

> 本文是 IM-037 唯一活动实施指导。§3～§8 与附录 A 定义 Core 契约及实施方法；主控于2026-10-09接收C1～C4的DEV-GOV-010 §3.1六项文档规格，结论为 ModuleCoreImplementationReady（规格准备）；平台 C-03/C-04/C-07 的映射仍由原 Contract Owner 采纳。本文不授予产品事实写入权，不表示代码、性能或生产准入。旧 PKG-062 仅为历史来源，不再与本文并列为实施权威。

## 1. 能力定义与边界

### 1.1 能力职责

模块接收调用方已经冻结的有限二部图：左顶点全集 `L`、右顶点全集 `R`、合法边集合 `E` 及每条边的有限非负费用 `c(e)`。它在同一输入快照内完成：

1. 输入结构和数值校验；
2. 连通分量拆分（保留孤立顶点）；
3. 最大基数 `K*` 求解；
4. 在 `K*` 下求最小总费用 `C*`；
5. 按分量绝对费用带 `delta` 检查近等价替代映射；
6. 返回匹配边、未匹配全集、证明阶段、见证、预算消耗和终止原因。

目标函数固定为“最大匹配数优先，其次最小费用”。模块不接受字符串表达式、任意回调或宿主注入的比较器，以保证证明和重放可复算。

### 1.2 禁止边界

模块核心不得：

- 读取图像、区域、轮廓、HALCON handle 或 `ImageLibDotNet` 对象；
- 计算坐标变换、孔径、深度、缺陷、置信度、工艺公差或物理误差；
- 生成、解析或写入产品身份、工单、板件、层、程序、数据库事实；
- 把唯一数值解解释为物理身份、缺孔、错位、缺陷或质量结果；
- 负责候选提取、跨 tile 补边、物理去重、方法资格、完整性判定或费用构造；
- 支持容量大于 1、多对一、多对多、强制边、未配对罚分、必需优先或材料复制；
- 调用设备、持久化、权限、放行、复判、报表或生产提交；
- 维护静态“当前图”、跨请求缓存、全局可变配置或隐藏窗口；
- 通过增加大罚分把缺边或未配对伪装成稠密矩阵；
- 以 UI 显示排序、四舍五入或 tie-break 取代数学证明。

调用方拥有调用顺序、目标含义、候选完整性、物理解释、最终判定和设备副作用。模块只报告“给定输入图和费用政策下”的计算事实。

### 1.3 依赖边界

核心依赖 .NET 基础类型和批准的公共诊断/取消端口即可。它不强制依赖 AsunImage、HALCON、WPF、DevExpress、数据库或具体工艺包。若某宿主已经用视觉能力生成顶点、边或费用，视觉步骤必须在宿主侧完成并以不可变快照交给本模块。

### 1.4 全部批准范围与不适用能力

当前架构IM-037的钻孔、微孔、通用候选关联均消费同一有限一对一图，不新增工艺分支。已登记的插装针/孔、OCR目标与单词以及SPI观察子问题也只在独立基准、物理去重及固定合法边成立时调用；具体应用映射见 [PKG-062产品接入导航](../../shared-modules/packages/PKG-062_Assignment.md)，这些消费者不向Core增加文字、材料或身份字段。未知整体位姿会改变边费用、容量大于1或真实多重关系时，本算法不适用；调用方不得复制顶点或用大费用补边来强行接入。

全部批准软件能力为§1.1六项、精确证书/残量替代、同步/异步及停止恢复、显式候选端口、双消费者接入和独立发布/验证。约束由单位容量及原图中边的存在表达；缺失由合法未匹配全集表达；并列由同K绝对费用带表达。没有坐标/像素/物理单位输入，Cost及delta同属调用方冻结的无量纲费用尺度。默认预算是工程资源政策；推荐规则固定为沿宿主已采纳Profile选择预算，超限仅允许显式修改Profile后新请求，不存在自动训练、自动调delta、自动删边或自动扩大资源的能力。

本模块没有独立WPF控件、viewport消费、生产建图Adapter、存储codec或特定native求解器交付。§7.1是调用边界，§7.3是已冻结的公开候选后端端口；§12的测试codec/薄Adapter只服务精确往返与独立接入断言，不成为运行依赖。UI/视觉/硬件不适用的依据是输入与权责，而非尚未获得编码授权；不能以后续名义漏掉本模块自身停止、数值、端口或测试设计。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.Assignment.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；纯 BCL 图/分配算法模块，无 UI、无 HALCON/AsunImage 依赖。

**Blazor/Web**：Assignment 结果经 gRPC/REST 查询，浏览器只渲染关联图；不经浏览器修改分配结果。

**AI Tiling**：AI 推理先产出候选，宿主再调用本模块关联到目标；本模块不参与推理分块编排。

**HALCON 双跑不适用**：本模块不执行视觉算法（纯数值图优化/分配）；HALCON 备选 CI 不涉及本模块。

## 2. 设计前核对与研究记录

### 2.1 HALCON / AsunImage 核对

目标 HALCON 为 26.05。已核对项目内 `halcon算子手册/operators/assign.html`、`assign_at.html` 及关联资料：`assign` 是变量赋值，不是二部图求解；`exhaustive_match` 是图像模板匹配；`proj_match_points_ransac` 是图像点对应与投影变换估计。它们不能表达本模块的稀疏缺边、最大基数、固定费用最优和替代证明。

这些算子均可经 `ImageLibDotNet.cv2` 使用，不再核验封装是否包含算子；仅实际 C# 类型/重载/封送有歧义时查公共签名或消费项目编译。其输入域是变量或图像/位姿，不提供本契约的固定稀疏图、最大基数、精确最小费用和替代证明；因此 Core 采用非视觉图算法。ROI 粗精、遮挡恢复、视觉自动参数和图像峰值资源由上游视觉模块负责，本模块不适用，也不另接 `halcondotnet.dll`。本轮复读目标 26.05 手册的 Description，复用既有候选比较，不宣称这些算子或 Core 已实测。

### 2.2 可借鉴资料

- [PKG-062 历史来源](../../shared-modules/packages/PKG-062_Assignment.md)：复用其精确费用、全图势和固定残量环推导；执行方法完整落入本文 §4，不要求开发者回到历史文件补公式。
- `docs/13-contract-candidates/CONTRACT-CANDIDATES.md#assignment-contract-semantics`：C-03/C-04/C-07 的候选字段语义；本文不生成第二份 Schema。
- `docs/01-governance/DEV-GOV-005_模块独立性与复用标准.md`、`docs/independent-modules/INDEPENDENT-MODULE-ARCHITECTURE.md`：独立模块、宿主和适配器边界。
- `docs/shared-modules/guidance/03-vision/DEV-VIS-020_Vision Contract与AsunImage边界开发指导.md`、`DEV-VIS-021_HALCON算子选择与算法决策矩阵开发指导.md`：视觉能力先核对、句柄不越界和失败可见。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_CameraCalib\CalibrationInterfaces.cs`、`CalibrationParameters.cs`：只读参考其参数校验、`IDisposable` 和进度事件表达方式，不复用其领域类型或错误模型。
- 固定版本 SciPy/OR-Tools 源码与测试仅用于独立 oracle、反例和溢出限制研究；未引入 Python、NumPy、C++ 或 native 运行时。具体来源见 `docs/references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#assignment-performance-research`。

### 2.3 本轮联网复读与决策落点

2026-10-09 复用归档原件，并联网读取固定提交源文件及相关测试；未重复下载快照、安装求解库或运行上游测试。以下是直接观察，不用上游宣传或返回的 `OPTIMAL` 证明本模块正确性。

| 固定来源/实际阅读 | 可复用强项与限制 | 本文落点 |
|---|---|---|
| [SciPy v1.16.2，commit b1296b9](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/optimize/rectangular_lsap/rectangular_lsap.cpp) 31～126 行；[test_linear_assignment.py](https://github.com/scipy/scipy/blob/b1296b9b4393e251511fe8fdd3e58c22a1124899/scipy/optimize/tests/test_linear_assignment.py) 全文及既有 LICENSE/依赖记录 | 矩形最短增广、常量费用确定性、空/NaN/不可行及稠密稀疏交叉测试可复用为测试思想。其 double 矩阵/满匹配和特定 tie-break 不等于缺边最大部分匹配、物理唯一或精确替代证明。BSD-3-Clause；局部 C++ 标准库和相邻 header，完整 SciPy 另需 Python/NumPy/Meson | §4.2、§4.4、§12；不复制 Python/C++ 作为运行依赖 |
| [OR-Tools v9.14，commit 0d60e8a](https://github.com/google/or-tools/blob/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/graph/min_cost_flow.cc) 1056～1185 行；min_cost_flow.h 251～367 行；[min_cost_flow_test.cc](https://github.com/google/or-tools/blob/0d60e8afe450ec817f510aae965ab8898310cb41/ortools/graph/min_cost_flow_test.cc) 287～341 行；CMake 159～192 行 | 最大流后最小费用路线可借鉴；int64 总费用饱和为 INT64_MAX 仍可 OPTIMAL，关闭 price scaling 可解扰动问题，Simple 接口不承诺 warm start。Apache-2.0；native C++、Abseil/Protobuf 等依赖由实际适配包管理，不能推断 C# 取消能力 | §4.3/4.6 精确复核、§7.3 候选端口；默认发布不捆绑 OR-Tools |
| [.NET 10 Progress<T>](https://learn.microsoft.com/en-us/dotnet/api/system.progress-1?view=net-10.0)、[Task.Run](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.task.run?view=net-10.0) 官方文档 | Progress<T> 捕获 SynchronizationContext，消费者处理可能晚于 Report 返回；排队取消令牌不能代替协作停止和排空 | §5.4、§6 迟到投影、单执行任务及 Task 终态 |

完整 commit/hash/许可原件继续引用 [REF-002 既有研究](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#assignment-performance-research)。联网读取的 SciPy 测试 SHA-256 为 `f8819b88189d2cd58080ca372c1b1ad5a93cbff207f8c4fa9e7e383214cf7d4b`，OR-Tools min_cost_flow.cc 为 `55562d99612f0ae15959a6de6641b7a7cbca3100134948057465ec8cdf8f0188`，与既有记录一致；本轮不新增原件。没有同样本 C# 实测，不能声称主路线最快。

<a id="3-公共契约候选"></a>

## 3. Core 公共契约

本节公开 C# 类型是已按 §15 接收的本模块 Core 契约；后续代码任务单独获准后按此实施，不等待平台 DTO 全部采纳。平台 JSON/protobuf/事实 Schema 映射另由原 Contract Owner 负责。附录 A 是本节及 §5/§7 的签名索引，不另建缩减 DTO。

### 3.1 基础类型

```csharp
public readonly record struct AssignmentVertexKey(string Value);
public readonly record struct AssignmentEvidenceKey(string Value);
public readonly record struct AssignmentRequestId(string Value);
public readonly record struct AssignmentInputRevision(string Value);
```

校验规则：`Value` 不为空/纯空白、不含控制字符或未配对代理项，严格 UTF-8 字节数 1..256；不 Trim、不改大小写、不作 Unicode 归一化。左右两侧允许相同文本但各自独立命名空间。键相等用 `StringComparer.Ordinal`；排序固定为无符号 UTF-8 字节的字典序，不以 UTF-16/本地化顺序替代。`Evidence` 在请求内唯一，才能无歧义定位被排除主解边；同一物理证据支持多边时由 Adapter 派生不同边证据键并保留上游映射。

```csharp
public sealed record AssignmentVertex(
    AssignmentVertexKey Key,
    string? DisplayLabel = null);

public sealed record AssignmentEdge(
    AssignmentVertexKey Left,
    AssignmentVertexKey Right,
    double Cost,
    AssignmentEvidenceKey Evidence);
```

`Cost` 的单位是调用方定义的无量纲目标费用；请求必须携带 `CostScaleId` 和费用方法修订号，模块不解释物理单位。费用必须是有限 binary64、`Cost >= 0`，`-0` 规范化为 `0`。同一 `(Left, Right)` 只能有一条边；不同证据不得用重复边表达竞争方法。

### 3.2 请求、完整性与费用政策

```csharp
public enum CandidateGraphCompleteness
{
    Complete = 0,
    Partial = 1,
    Unknown = 2
}

public enum AssignmentObjective
{
    MaxCardinalityThenMinCost = 0
}

public sealed record AmbiguityPolicy(
    double Delta = 0.0,
    bool CheckAlternatives = true,
    int MaxWitnesses = 1);

public sealed record AssignmentRequest(
    AssignmentRequestId RequestId,
    AssignmentInputRevision InputRevision,
    IReadOnlyList<AssignmentVertex> LeftVertices,
    IReadOnlyList<AssignmentVertex> RightVertices,
    IReadOnlyList<AssignmentEdge> Edges,
    CandidateGraphCompleteness Completeness,
    AssignmentObjective Objective,
    string CostScaleId,
    string CostMethodRevision,
    AmbiguityPolicy Ambiguity,
    AssignmentBudget Budget,
    string ContractRevision = "0.1");
```

`SolveAsync` 在返回 Task 前同步做有界封套检查和集合复制；调用方须保证这段期间输入稳定。随后只读取私有快照，不借用集合、租约或 HALCON/native 资源。先 checked 检查 Count 和预算，再分配复制空间；复制计入时间和内存预算，已取消/超时/非法时可提前停止而不必复制完。`Solve` 同样先复制，返回最终结果。记录为 IReadOnlyList 不等于运行时不可变；Core 输出集合必须只读封装且不泄漏可写数组，诊断Data也复制。Completeness 只描述上游覆盖，Partial/Unknown下只能证明图内结论。

DisplayLabel 可为null，否则严格UTF-8不超过1,024 bytes、无控制字符/非法代理项；不参与排序、费用或证明。CostScaleId/CostMethodRevision与键采用同样格式限制；所有集合/元素、Ambiguity、Budget不得为null；Objective未定义值为ASGN-005，其它枚举未定义值为ASGN-007。ContractRevision只接受字面量0.1，不兼容为ASGN-006；拒绝结果/事件的ContractRevision仍标本实现0.1，将所请求版本放诊断Data，不冒称使用了0.2。这些是入口校验，不由record生成构造函数隐式保证。

### 3.3 预算参数、单位、范围和默认值

以下为工程默认值和允许范围，属于可配置资源门，不是工业性能承诺。所有整数使用 checked 算术，超限在分配工作区前拒绝。

| 参数 | 类型/单位 | 允许范围 | 默认值 | 语义 |
|---|---|---:|---:|---|
| `MaxVertices` | `int` 个顶点 | 1..200,000 | 10,000 | `L + R` 上限 |
| `MaxEdges` | `int` 条原边 | 0..5,000,000 | 100,000 | 不含残量反向边 |
| `MaxCostBits` | `int` bit | 64..8,192 | 4,096 | 共同精确尺度及中间费用位宽上限 |
| `MaxMemoryBytes` | `long` bytes | 16 MiB..8 GiB | 256 MiB | 私有输入、索引、残量图、堆、势、BigInteger、证书、见证、结果及后端声明工作区的保守预留总额；不含宿主序列化/进程RSS |
| `MaxRelaxations` | `long` 次 | 1,000..2,000,000,000 | 20,000,000 | 包括验证后端和替代查询 |
| `MaxAlternativeChecks` | `int` 次 | 0..200,000 | 10,000 | 整个请求所有分量的禁边查询上限；`0` 表示仅主解 |
| `MaxWitnesses` | `int` 个 | 0..1,024 | 1 | 每分量见证存储上限；0 不启动替代检查，非0仍在首份已核实见证处停止，不承诺枚举到该数 |
| `Deadline` | `TimeSpan` | 1 ms..10 min | 30 s | 从接受请求开始的整次墙钟预算 |
| `ProgressInterval` | `TimeSpan` | 1 ms..10 s | 100 ms | 最小进度通知间隔；不改变数学结果 |

`AmbiguityPolicy.Delta` 必须有限且非负，单位与 Cost 相同；`MaxWitnesses` 范围同预算参数，每分量有效存储上限取两者最小值。替代检查有效开关为 CheckAlternatives 且 MaxAlternativeChecks>0 且两处 MaxWitnesses 均>0；否则不检查并返回 NotEvaluated。启用后首份满足 `C <= C* + delta` 的见证即足够证明存在，不枚举全部/逐目标稳定性。预算包含复制、验证、求解、证书和排空；deadline 到达只设置停止意图，必要清理仍须完成，实际 Elapsed 可超过 deadline，不重置预算。

对应 record 只承载参数；在入口校验表中范围，非法参数返回 InvalidInput/ASGN-007。不要求 record 构造时执行隐藏归一化或抛业务异常：

```csharp
public sealed record AssignmentBudget(
    int MaxVertices = 10_000,
    int MaxEdges = 100_000,
    int MaxCostBits = 4_096,
    long MaxMemoryBytes = 256L * 1024 * 1024,
    long MaxRelaxations = 20_000_000,
    int MaxAlternativeChecks = 10_000,
    int MaxWitnesses = 1,
    TimeSpan? Deadline = null,
    TimeSpan? ProgressInterval = null);
```

`null` 的 Deadline/ProgressInterval 在 Core 私有快照中分别解释为 30 秒/100 毫秒，原 DTO 不变。TimeSpan.Zero 不表示无限。宿主提高预算必须绑定新版 Profile；不自动提高 delta、删边或降低精度。

### 3.4 同步和异步入口

```csharp
public interface IAssignmentSolver
{
    AssignmentResult Solve(
        AssignmentRequest request,
        IAssignmentEventSink? events = null);

    Task<AssignmentResult> SolveAsync(
        AssignmentRequest request,
        CancellationToken cancellationToken = default,
        IProgress<AssignmentProgress>? progress = null,
        IAssignmentEventSink? events = null);
}
```

- `Solve` 只适合调用方自己的工作线程；库不得在 UI 线程内隐式阻塞，也不得内部启动无界线程。
- `SolveAsync` 同步复制后最多调度一个线程池执行任务，不捕获 UI SynchronizationContext；排队时长计入本请求 deadline。不得把调用方取消令牌直接作为 Task.Run 的排队取消令牌导致无结果的 Task 取消；进入执行封套后，已取消也必须返回带 Cancelled 状态的 AssignmentResult。
- 两个入口必须共用同一 Core、排序、数值尺度和结果模型；异步不是另一套算法。
- 两个入口以 §3.2 的复制边界隔离输入；标准集合的 Count/索引应为有限无副作用访问。自定义集合抛出访问异常时为 InvalidInput/ASGN-001，不重试枚举；无法保证有限访问的集合不得传入。
- `request=null` 属于无请求的调用错误，同步抛 ArgumentNullException，不发事件；其它输入错误返回 InvalidInput。非法 RequestId/InputRevision 在拒绝回执中原样回显（不得当有效键持久化），不生成虚假业务 ID。正常取消、deadline 和计算错误均返回结果，不以 Task.IsCanceled 或异常字符串承载。
- 对相同 RequestId 没有 Core 持久幂等/去重承诺：每次调用是独立计算，宿主须禁止混用订阅，重试创建新 RequestId；同图可保持 InputRevision。无 UI 的构造入口为 §7.3 的 `AssignmentSolver.Create()`，不需要服务容器。

## 4. 处理流程与算法约束

### 4.1 固定步骤

1. 进入请求执行封套并发布 `RequestAccepted`，随后复制输入并冻结 `RequestId`、`InputRevision`、方法修订和预算；该事件不代表输入有效或业务接纳。
2. 校验顶点唯一性、边端点存在性、重复边、费用有限性、`delta`、位宽和 checked 长度。
3. 按稳定键构建邻接表和残量图；孤立顶点保留在结果中。
4. 计算完整连通分量。分量拆分只基于图边，不按图片、行号、UI 分页或线程数切块。
5. 每个分量按 §4.2 逐次增加流量，同时保持当前流量下费用最小；直到无增广路得到 `K*` 及该基数下的 `C*`，再执行替代检查。目标优先级不是要求另跑一套未定义的最大匹配算法。
6. 逐项校验结果边属于原图、左右互斥、`K` 和精确费用重算一致；核实无增广路和全残量约化费用非负。
7. 记录阶段、停止原因、预算消耗和资源排空，再发布终止事件。

### 4.2 参考路线和主路线

冻结交付主路线为单位容量最小费用流 + 精确 BigInteger 势函数 Dijkstra；参考路线为独立 Bellman-Ford，oracle 为有界 DFS。不得把“主路线候选”留给开发者临时选型，也不得静默按图大小更换数学政策。各路线共用目标函数和精确尺度，测试可分步骤实现，但整模块验收含所有主/证明能力。

每分量按 UTF-8 稳定序排列左/右键。网络节点编号：s=0，左侧 1..nL，右侧 nL+1..nL+nR，t=nL+nR+1。原弧为 s→L、合法 L→R、R→t，容量1；每弧有容量0、费用相反的反向弧。弧按 (tail,head,原/反向标记) 稳定排序。零流时 h=0，所有有效弧的约化费用 `c'(u,v)=c(u,v)+h(u)-h(v)` 非负。

1. 索引二叉堆按 `(精确距离,节点编号)` 弹出；邻接稳定遍历，仅严格更短才换前驱，距离未达用独立标志，不用有限大数表示∞。执行完整 Dijkstra，不在 t 处提前结束，以免暂定距与全图势更新混淆。
2. t 不可达时终止增广；其可达集用于最大基数证明。t 可达时取 D=d(t)，对所有节点更新 `h(v)+=min(d(v),D)`，未达节点也加 D。只更新可达节点会破坏全图非负性：零费用 a→b、s到b距离5、a不可达时，只给b加5会产生 -5。
3. 前驱回溯必须得到无重复节点的完整 s→t 路，容量为正且不超过 V-1 弧；先整体验证再增广1，禁止部分修改后发布结果。新反向弧约化费用为0；下一轮之前核全残量弧非负和流守恒。
4. 无增广路后，按原边重算K/C、左右互斥和费用，复核最小覆盖及已注入候选的该分量K/C（如有），核对通过后提交CardinalityProved的完整快照；随后复核全图势，提交CostProved/MainSolutionProved。取消处于两项复核之间可返回CardinalityProved，但不得预填费用最优。没有增广路/最小覆盖证明最大K；全残量非负势证明固定K最小C（任意残量循环费用非负）。

Bellman-Ford 参考按节点/弧稳定序做最多 V-1 轮严格松弛并额外检查负环，保持反向弧、完整前驱链和同一停止门。DFS 逐左顶点枚举未配对或未占用右顶点，先比 K 后比 C；不能以当前费用高而剪掉可能增加 K 的分支。代表映射定义为上述主路线的确定性输出，不宣称所有最优映射中字典序最小；参考后端只须 K/C/替代结论一致，不必代表边相同。线程数、输入排列、Dictionary 枚举和后端 tie-break 均不能改变主路线代表解。

### 4.3 精确费用尺度

将有限 binary64 费用和 delta 解释为 `m * 2^e`。令 fraction 为52位尾数、exp为11位指数；normal 用 `m=2^52+fraction,e=exp-1023-52`，subnormal 用 `m=fraction,e=-1074`，零单列。取本完整分量所有非零费用及 delta 的最小 e，整数为 `m << (e-e_min)`；均为零时 e_min=0。不能剥除尾数零而不同时改变冻结尺度。同一尺度贯穿主解、后端对照、替代查询和 C*+delta 比较；不经十进制格式化或重新缩放改变 tie。

费用指数跨度、总费用、势函数、路径和中间差值的位宽必须在申请工作区前估计；预估超过 `MaxCostBits` 时返回 Status=NumericalUnresolved、Termination=NumericalRangeExceeded，运行中中间值越界则 Termination=NumericalUnresolved；两者均为 ASGN-030，不能饱和、截断、转 `Infinity` 后继续。

令 S 为本尺度最大输入整数（含 delta），U=max(1,S)，N=nL+nR+2，Kmax=min(nL,nR)。保守预留位宽为 `bit_length(U)+ceil(log2(max(2,8*(Kmax+1)*(N+1))))+1`，checked 计算；这是分配界，运行中对距离/势/和/差/乘积仍逐项检查绝对位宽。超过范围为 NumericalUnresolved/ASGN-030，不误映射成普通规模超限。ExactCost 显示按 round-to-nearest-ties-to-even 生成 binary64；DisplayRounded 表示显示值与精确值不同，超出有限范围时 DisplayOverflow=true，近似值可为正∞但不得参与计算。即使每条费用有限，总费用也可显示溢出，精确证明仍有效。

显示转换的固定实施步骤（非负ExactCost）：零输出+0且两个flag均false；非零整数I的位长b用整数计算，最高二进制指数q=b-1+e。若精确值大于 `(2^53-1)*2^971`，按本契约统一输出+∞、DisplayOverflow=true、DisplayRounded=true，不将“仅略大于MaxValue仍可能向下舍入”作为有限显示；精确大小用整数移位比较。否则normal(q≥-1022)保留53有效位：shift=b-53，shift≤0则左移，shift>0则商/余数除以2^shift，余数大于半数或等于半数且商为奇数时商加1，产生2^53时再右移1并增加指数；用保留商和e+shift的指数编码normal。subnormal(q<-1022)在2^-1074单位上用同样商/余数规则舍入I*2^(e+1074)，零编码+0，商达到2^52编码最小normal。直接拼接binary64位再用BitConverter转换，禁止先把大I cast为double再乘2^e产生中间∞或双重舍入。DisplayRounded由有限显示值的独立位解码与I*2^e精确比较决定。位宽预留中ceil(log2(x))固定用正整数 `bit_length(x-1)`，不调用浮点Log估算边界。

### 4.4 替代映射和歧义证明

主解 `M*` 完成后，对每条主解边 `e` 检查同一完整分量、同一目标函数下禁用 `e` 的最小费用子问题：

- 若最大基数仍为 `K*` 且 `C_e <= C* + delta`，返回不同边集合的替代见证，状态为 `AlternativeWithinDeltaFound`；
- 若最大基数下降，排除该边的子问题不构成同基数歧义，但该查询必须完成；
- 若所有需要的禁边查询都完成且没有带内见证，才可返回 `NoAlternativeWithinDeltaProved`；
- 查询被取消、超时、预算耗尽或数值未决时，返回 `AlternativeProofIncomplete`，不能报告唯一；
- `K*=0` 无主解边，不需要禁边查询；孤立顶点仍由调用方解释。

交付替代主路线固定为只读主解残量环；逐条禁边重解仅作独立参考。对主解边 e=(l,r)，临时排除其有效反向弧 r→l，在**保留 s/t 的原残量图**上从 l 到 r 执行精确 Dijkstra。存在最短路 P 时：

`Delta_e=d'(l,r)-h(l)+h(r)-c(e)`；把 P 和 r→l 构成的简单循环在独立暂存上增广1。校验仍为 K*、排除了 e、原边互斥且 `C(M_e)=C*+Delta_e`，Delta_e 必须非负；≤delta 时输出见证。无路时 e 不能在同 K 映射中移除，不把无路当零差。每个查询始终用同一 M*、h 和尺度，不继承上次替代流。

充分性：任何同 K 且排除 e 的匹配相对 M* 是包含 s/t 的整数循环流，至少一个循环包含 r→l；M* 最优使每个循环费用非负，因此只取该循环不会增加费用。最短 P 即该禁边同 K 子问题最低费用。两左一右的未匹配者交换须经 s，两右一左须经 t；删掉 s/t 会漏判，加入 t→s 会破坏固定 K，不允许。任意不同同 K 匹配至少排除 M* 一条边，全部主解边查询完成且无见证方可证明无带内替代。

MaxAlternativeChecks 是请求级累计的**已开始**查询数，按分量序、主解边序执行；未开始不增加，开始后取消也计数。找到首份已复核见证即可结束本分量并进入下一分量；次数耗尽且有未查边时为 BudgetExceeded/AlternativeBudgetExceeded，保留主解，不能将已发现见证降为 NotProved。K*=0 时：替代策略启用则无查询即可 AlternativesExhausted/NoAlternativeWithinDeltaProved；策略停用则 CostProved/NotEvaluated。

### 4.5 路线、备用、恢复和训练边界

| 路线 | 适用条件 | 处理与证明要求 | 失败后的动作 |
|---|---|---|---|
| 精确势函数 Dijkstra | 合法固定图的交付主路线 | 按 §4.2 全残量非负及完整增广执行 | 不变量破坏为 ASGN-040 停止；不能自动换后端掩盖算法故障 |
| Bellman-Ford 最短增广 | 独立测试、诊断复算；不是默认生产回退 | 同图/同尺度核对 K/C、取消及前驱简单性 | 预算不足保留已完成证明，不将 best-so-far 当最优 |
| 有界 DFS oracle | 小图测试、反例定位 | 枚举部分匹配，按 `(K,C,稳定键)` 对照；不得作为整板节拍路径 | 仅记录测试失败，不回退生产事实 |
| 外部候选后端 | 宿主显式注入 §7.3 端口，默认不启用 | 输入冻结、预算共享、只读候选；由 Core 独立主解/证书核对 | Unsupported 回到默认主路线；候选无效/费用非最优为 ASGN-031，异常为 ASGN-052；不采用后端自报 OPTIMAL |
| 训练/模型路线 | 本模块没有可训练参数、样本或模型 | **不适用**；不创建训练集、模型版本、置信度或推理后端 | 视觉候选质量由宿主处理；不得为“训练”扩展本模块职责 |

恢复只针对计算：输入或费用方法改变须新 InputRevision；只提高运行预算可保留图修订，但需新 RequestId 和 Profile。内存/数值越界停止，不自动降低精度或切换参考路线；算法不变量破坏保留诊断并要求修复。取消/超时后在 Core 任务完成后重放，不覆盖旧结果、不拼接旧分量或升级部分证明。

### 4.6 可外部核对的证明载荷与拒绝含义

CostProved 不是后端自报标签。AssignmentProofCertificate 返回最小顶点覆盖和精确全图势，调用方/测试仅用输入图、匹配与证书即可复核：由最终 s 可达集 Z 得覆盖 `(L\Z_L) ∪ Z_R`，覆盖每条合法边且大小等于匹配数 K；再重建相同节点编号的残量图，逐弧检查 `c+h(u)-h(v)>=0`。固定 K 无负循环即费用最优。证书 NodePotentials 使用与 TotalCost 相同的 BinaryExponent，长度恰为 nL+nR+2，h(s) 可整体平移归零；输出时统一令 h(s)=0。证书包含原图全部孤立顶点，不能按匹配边缩图。

每条禁边查询的完成仅在本请求内计数；无替代结论可通过相同查询/独立重解复核，证书不伪装成已枚举全部匹配。结果不输出概率置信度或自动拒绝物理对象：Complete 是调用方声明，低费用不等于高置信；主解精确唯一、替代带内、数值未决、候选缺失四者分列。宿主需按自身观测资格拒绝/重采；不得把拒绝的边改为高费用继续充当完整候选。

## 5. 输出、状态和错误

### 5.1 结果模型

```csharp
public enum AssignmentRequestStatus
{
    Completed = 0,
    InvalidInput = 1,
    Cancelled = 2,
    DeadlineExceeded = 3,
    BudgetExceeded = 4,
    NumericalUnresolved = 5,
    ComputationFaulted = 6
}

public enum ProofState
{
    NotStarted = 0,
    CardinalityProved = 1,
    CostProved = 2,
    AlternativeFound = 3,
    AlternativesExhausted = 4,
    AlternativeProofIncomplete = 5,
    Mixed = 6
}

public enum AmbiguityStatus
{
    NotEvaluated = 0,
    AlternativeWithinDeltaFound = 1,
    NoAlternativeWithinDeltaProved = 2,
    NotProved = 3
}

public sealed record AssignmentMatch(
    AssignmentVertexKey Left,
    AssignmentVertexKey Right,
    AssignmentEvidenceKey Evidence,
    double Cost);

public sealed record AssignmentProofCertificate(
    IReadOnlyList<AssignmentVertexKey> MinimumVertexCoverLeft,
    IReadOnlyList<AssignmentVertexKey> MinimumVertexCoverRight,
    IReadOnlyList<System.Numerics.BigInteger> NodePotentials);

public sealed record AssignmentComponentResult(
    string ComponentId,
    IReadOnlyList<AssignmentMatch> Matches,
    IReadOnlyList<AssignmentVertexKey> UnmatchedLeft,
    IReadOnlyList<AssignmentVertexKey> UnmatchedRight,
    long Cardinality,
    ExactCost TotalCost,
    ProofState Proof,
    AmbiguityStatus Ambiguity,
    IReadOnlyList<AssignmentAlternative> Alternatives,
    CandidateGraphCompleteness InputCompleteness,
    AssignmentProofCertificate? Certificate = null);

public sealed record AssignmentResult(
    AssignmentRequestId RequestId,
    AssignmentInputRevision InputRevision,
    AssignmentRequestStatus Status,
    IReadOnlyList<AssignmentComponentResult> Components,
    TerminationReason Termination,
    BudgetUsage Usage,
    IReadOnlyList<AssignmentDiagnostic> Diagnostics,
    bool ResourcesReleased,
    string AlgorithmRevision,
    string ContractRevision);
```

支撑结果类型的候选定义：

```csharp
public enum TerminationReason
{
    Completed = 0,
    InvalidInput = 1,
    CancelRequested = 2,
    DeadlineExceeded = 3,
    VertexBudgetExceeded = 4,
    EdgeBudgetExceeded = 5,
    MemoryBudgetExceeded = 6,
    RelaxationBudgetExceeded = 7,
    AlternativeBudgetExceeded = 8,
    NumericalRangeExceeded = 9,
    NumericalUnresolved = 10,
    InvariantViolation = 11,
    InternalFault = 12
}

public sealed record ExactCost(
    int BinaryExponent,
    System.Numerics.BigInteger IntegerValue,
    double DisplayApproximation,
    bool DisplayRounded,
    bool DisplayOverflow);

public sealed record AssignmentAlternative(
    IReadOnlyList<AssignmentMatch> Matches,
    ExactCost TotalCost,
    ExactCost DeltaFromPrimary,
    AssignmentEvidenceKey ExcludedPrimaryEvidence);

public sealed record BudgetUsage(
    long Vertices,
    long Edges,
    long Relaxations,
    int AlternativeChecks,
    long PeakMemoryBytes,
    TimeSpan Elapsed,
    TimeSpan Drain);

public sealed record AssignmentDiagnostic(
    string Code,
    string MessageKey,
    string? ComponentId = null,
    string? EdgeEvidence = null,
    IReadOnlyDictionary<string, string>? Data = null);

public sealed record AssignmentProgress(
    AssignmentRequestId RequestId,
    int CompletedComponents,
    int TotalComponentsKnown,
    long Relaxations,
    int AlternativeChecks,
    ProofState CurrentProof,
    bool WorkTotalKnown);

public enum AssignmentEventKind
{
    RequestAccepted = 0,
    ValidationCompleted = 1,
    ComponentStarted = 2,
    MainSolutionProved = 3,
    AlternativeCheckStarted = 4,
    AlternativeWitnessFound = 5,
    ComponentCompleted = 6,
    AlternativesCompleted = 7,
    LogicalCompleted = 8,
    StopRequested = 9,
    DrainStarted = 10,
    Drained = 11,
    ResourcesReleased = 12,
    RequestCompleted = 13,
    RequestStopped = 14
}

public sealed record AssignmentEvent(
    AssignmentEventKind Kind,
    AssignmentRequestId RequestId,
    AssignmentInputRevision InputRevision,
    long Sequence,
    DateTimeOffset TimestampUtc,
    string? ComponentId,
    ProofState Proof,
    TerminationReason? Termination,
    BudgetUsage Usage,
    string AlgorithmRevision,
    string ContractRevision);

public interface IAssignmentEventSink
{
    void OnEvent(AssignmentEvent value);
}
```

`ExactCost.IntegerValue` 与 `BinaryExponent` 表示 `IntegerValue * 2^BinaryExponent`；实现必须保证两者来自同一分量尺度。`DisplayApproximation` 仅用于显示，不能参与比较。`TotalComponentsKnown` 在未完成分量枚举时固定为 -1，此时 WorkTotalKnown=false，CompletedComponents=0；枚举完成后为全部分量数（含孤立点），空图为0。CompletedComponents 仅计完成所请求主解及替代策略的分量，不用耗时猜百分比。

ExactCost 保留共同尺度和整数，显示double不参与判断。Core 输入复制完成后宿主可修改原集合。Drained 表示算法及本次注入后端调用已退出，无仍访问工作区的后台工作；独立上游视觉Adapter不在其中。ResourcesReleased 表示私有输入/工作区/临时见证均解除持有，只读结果已脱离可复用工作区并转归调用方。资源释放和唯一终止后才返回，结果 ResourcesReleased 恒true。Core 不持有 native handle，也不提供 DrainUnknown 查询API；注入后端未排空时原Task保持未终结，独立上游视觉native状态由其Owner查询。

### 5.2 正交状态语义

`RequestStatus` 表示请求终止；`ProofState` 表示每个分量已完成的数学证明；`AmbiguityStatus` 表示带 `delta` 的替代结论；`CandidateGraphCompleteness` 表示调用方输入覆盖。四者不得合并成一个 `PASS/FAIL`。

组件结果中的 Proof 不能为 Mixed；带 ComponentId 的事件 Proof 就是该分量阶段。ComponentId=null 的事件及 AssignmentProgress.CurrentProof 聚合已完成枚举的**全部**组件（包括尚未开始的 NotStarted），枚举未完或空图时为 NotStarted；状态全部相同取该状态，否则 Mixed。这避免“前一分量完成、下一分量未开始”被投影为整体证明完成。例如主解已证、替代途中取消：Status=Cancelled、Proof=AlternativeProofIncomplete、Ambiguity=NotProved，主解证书仍保留。

Status=Completed 要求所有组件主解已证，且替代策略停用、找到见证或所有适用查询完成；Completeness 不影响该图内状态。策略停用条件见 §3.3，此时 Proof=CostProved、Ambiguity=NotEvaluated；不得声称唯一。启用策略且全部查询完成无见证才是 AlternativesExhausted/NoAlternativeWithinDeltaProved；查询未完是 AlternativeProofIncomplete/NotProved。见证已复核后，后续取消其它分量仍保留原分量 AlternativeFound/AlternativeWithinDeltaFound。

分量按最小 `(侧标记 L=0/R=1,UTF-8键)` 排序，ComponentId 为 `cmp-000001` 起的6位十进制序号；输入重排不变、图变化不承诺旧 ID 不变。结果 Matches/Unmatched/覆盖键按同一稳定序，Alternatives 的边也排序。分量枚举完成前被停止时 Components 为空，不能解释为没有顶点；枚举完成后输出全部分量，未证明的分量为 NotStarted、Matches/Unmatched/Alternatives 为空、Cardinality=0、TotalCost=(0,0,0,false,false)、Certificate=null，数值只是占位且不得消费为已知零/全集未匹配。CardinalityProved 表示已有最大基数及最小覆盖证书，NodePotentials 为空，费用只是该可行映射费用；CostProved 及其后续状态必须有完整势证书和对应 Matches/Unmatched 全集。取消于一次增广中不得发布半条路径或 best-so-far。

状态与终止原因对应：Completed↔Completed；InvalidInput↔InvalidInput；Cancelled↔CancelRequested；DeadlineExceeded↔DeadlineExceeded；BudgetExceeded↔Vertex/Edge/Memory/Relaxation/AlternativeBudgetExceeded；NumericalUnresolved↔NumericalRangeExceeded/NumericalUnresolved；ComputationFaulted↔InvariantViolation/InternalFault。算法故障撤销受影响证书，置该分量 NotStarted 并保留诊断；不能靠有匹配边保留最优标签。

### 5.3 错误码

错误码是稳定机器键，消息由宿主按语言资源投影；核心不生成产品化话术。每条诊断只定位本请求，不能以诊断创建产品事实。

| 错误码 | 触发条件 | 结果要求 |
|---|---|---|
| `ASGN-001` | 请求/键/修订为空或格式非法 | 不分配大工作区，`InvalidInput` |
| `ASGN-002` | 左右顶点重复 | 指明侧和键，拒绝请求 |
| `ASGN-003` | 边端点不存在或同对重复 | 指明边索引/证据键，拒绝请求 |
| `ASGN-004` | 费用非有限、负数或 `delta` 非法 | 拒绝请求，不静默修正 |
| `ASGN-005` | 不支持的AssignmentObjective | InvalidInput；容量/强制边等根本不在DTO中，宿主不得编码为复制顶点 |
| `ASGN-006` | ContractRevision 不支持 | InvalidInput，不静默降级 |
| `ASGN-007` | 参数/预算越有效域或非Objective枚举未定义 | InvalidInput，定位参数，不自动放宽 |
| `ASGN-010` | 顶点/边/内存预留不足 | BudgetExceeded，不截断输入；位宽单独用 ASGN-030 |
| `ASGN-011` | 松弛或替代查询次数耗尽 | 保留已完成证明，未完成阶段标未决 |
| `ASGN-020` | 调用方取消 | 协作式停止，等待 Core 工作区排空和释放后返回；上游 native 资源由其 Owner 负责 |
| `ASGN-021` | 到达整次 deadline | 与取消同样排空 Core 工作区；不声称硬实时终止 |
| `ASGN-030` | 精确尺度或中间值超位宽 | `NumericalUnresolved`，不得使用饱和值 |
| `ASGN-031` | 后端候选非法、非最大基数或非最小费用 | ComputationFaulted/InvariantViolation，撤销该候选证明；不得发布候选为主解 |
| `ASGN-040` | 前驱环、负约化边、互斥或费用不变量破坏 | `ComputationFaulted`，停止并保留故障上下文 |
| `ASGN-050` | 内部未分类故障 | 记录算法修订和输入摘要，不暴露堆栈作为契约 |
| `ASGN-051` | OnEvent 或 progress.Report 同步抛出异常 | 记录一次/通道的有界诊断；不改变数学证明或终态意图；不递归调用出错观察器 |
| `ASGN-052` | 注入后端抛出非取消异常或返回非法用量 | ComputationFaulted/InternalFault；等待该调用退出，不重试或重置预算 |

MessageKey 固定为 `Assignment.Diagnostics.ASGN_001` 形式（对应Code的连字符换下划线），不带语言；Data 只用 invariant string。输入/预算错误至少给 parameter，适用时给 side(L/R)、index(0起原输入索引)、vertexKey/evidenceKey、observed/limit；算法/后端错误至少给 phase 和适用的 backendRevision，观察器错误给 channel(events/progress)、eventKind(若适用)、exceptionType，不暴露堆栈/任意异常Message。Data每条至多16项，键≤64/值≤1,024 UTF-8 bytes，超长内容截取并记truncated=true；宿主保存的原输入/异常日志负责完整追溯。重复证据键用ASGN-003；参数domain错误用ASGN-007，不让构造函数和入口产生两套拒绝语义。

### 5.4 事件顺序

事件统一包含 `RequestId`、`InputRevision`、单调递增 `Sequence`、UTC 时间、算法修订和已用预算。`RequestAccepted` 只表示 Core 已进入请求执行封套、开始复制和校验输入，不代表输入有效、业务接纳或产品事实成立。输入校验失败仍走同一封套，并在校验事件后以 `InvalidInput` 停止。正常顺序为：

`RequestAccepted -> ValidationCompleted -> (ComponentStarted -> MainSolutionProved -> [AlternativeCheckStarted -> AlternativeWitnessFound?]* -> ComponentCompleted)* -> AlternativesCompleted -> LogicalCompleted -> DrainStarted -> Drained -> ResourcesReleased -> RequestCompleted`

括号是按分量序重复，不是所有分量先发 Started 再批发 MainSolutionProved；AlternativeCheckStarted 每条禁边查询一次，WitnessFound 仅在见证复核后一次/分量，策略停用或 K=0 时无查询事件。AlternativesCompleted 表示所请求策略结束（可为停用），不是统一无歧义证明。Sequence 从1开始，连续递增，每请求单一串行分发者；UTC 仅记录，排序依据 Sequence。ComponentStarted/MainSolutionProved/AlternativeCheckStarted/AlternativeWitnessFound/ComponentCompleted 必须有 ComponentId，其余为 null。终止事件的 Termination 必填且与结果一致；停止意图后其它生命周期事件携带同一原因，正常计算事件为 null。

停止顺序为：

`... -> StopRequested -> DrainStarted -> Drained -> ResourcesReleased -> RequestStopped`

验证失败：RequestAccepted→ValidationCompleted(Termination=InvalidInput)→DrainStarted→Drained→ResourcesReleased→RequestStopped；即使未申请求解工作区也按空释放成立，不直接跳到终止。完整校验前被取消/超时，不伪造 ValidationCompleted。ComponentCompleted 只用于已完成请求策略的组件；停止时不为未完成组件补发它。

OnEvent 为同步观察器、锁外串行调用，不作UI线程切换：封套/复制阶段可在调用线程，后续在Core执行线程，宿主不得假设固定线程或直接触碰WPF控件。不得阻塞等待同一请求终止、递归提交同RequestId或修改复制期间输入。同步异常为ASGN-051，每请求每观察通道最多记录一条，不递归通知该故障；仍按序尝试后续事件。终止回调失败也纳入随后返回Diagnostics。观察器耗时属于实际elapsed；异常本身不改数学结果或已冻结终态，但长时间阻塞可能使下一检查达到deadline。Core不能强杀不返回的用户回调，宿主只能隔离/等待，不能假报已排空。

progress.Report 也在锁外、按有效 ProgressInterval 节流，终止后不再调用；同步抛出处理同上。Progress<T> 后续排入 UI/线程池的处理不属于 Core 工作区，Core 不等待、不捕获其中异步异常；宿主负责处理异常和已关闭订阅。进度无终态权威，可能在最终结果后迟到；UI/遥测收到终态后按 RequestId 忽略进度，不得重开运行状态。事件 sink 自行排队时由宿主以 Sequence 去重/重排，Core 无事件回放 Store，重连补齐由宿主保存事件或直接读取其保存的结果。

## 6. 取消、超时、线程和资源

- 取消令牌由调用方拥有；模块只读取，不保存到全局。
- 在输入校验、分量遍历、每批松弛、每次增广、路径重建、每次替代查询和证明复核处检查取消与 deadline。单个 BigInteger 操作或排序是不可抢占工作块，最大工作块须纳入 Profile。
- deadline 是协作式停止上限，不是强制杀线程保证；需要硬隔离时由宿主使用进程/作业边界，本模块不自行终止线程。
- 每个请求独占复制后的输入快照、邻接表、残量图、势、堆、BigInteger 暂存和替代见证；请求结束、取消和失败路径都释放 Core 自有工作区。
- 同一原始输入可并发提交给两个请求，但每个请求拥有各自复制的快照和工作区；一个请求取消不得修改另一个请求的工作区或结果。
- 取消与完成竞态由单一执行 Owner 仲裁一个终止回执。已完成的 `K/C` 证明可保留，未完成的替代证明不能升级为唯一。
- 不使用无限 `Task`、静态数组、线程中止、终结器驱动的业务释放或隐式池扩容。

AssignmentSolver 无持久请求表、后台服务或 native 资源，不需要 Initialize/Reset/Dispose。实例可并发调用，每请求独立；注入后端必须支持并发且无跨请求可变工作区，否则宿主为每请求创建独立实例并自行串行化。宿主拥有并发上限/队列，Solver 不暗建队列。关闭时宿主停收新请求→取消所有本次 token→await 所有返回 Task→处理/隔离迟到投影→释放自己的 Adapter；等待超时仅为宿主“仍在排空”，不得制造 Core 终态。Core 只在后端调用/算法工作均退出后发 Drained，释放暂存后发 ResourcesReleased，然后唯一终态；只读结果集合转由调用方保留，不随暂存一起释放。

deadline/Elapsed 使用同一单调时钟，起点在 RequestAccepted 回调之前；TimestampUtc 仅作日志，不用系统墙钟调整延长或缩短预算。停止竞态在安全点冻结：尚未终止时，已发现算法不变量/内部故障优先，其次已观察调用方取消、其次 deadline、其次计数/内存门；未观察到的原因不倒填。正常逻辑完成与停止意图只能提交一个，之后取消/超时不改已冻结 Completed，只记录实际清理时长。同步 Solve 没有外部 token，只受预算 deadline；需要可取消关闭的宿主必须用 SolveAsync。进程崩溃/OOM/StackOverflow 等无法生成可信回执时由宿主记录结果 Unknown 并重新 Replay，Core 不编造 ComputationFaulted 回执或 PASS。

MaxMemoryBytes 为分配前保守预留账本，不是 GC heap/RSS 硬限制。实施冻结：以64 bytes计每对象/数组头，字符串另计2*字符数并16-byte向上对齐，集合按实际容量计槽；基础工作项每槽至少64 bytes，BigInteger 项另加 `16-byte-align(4*ceil(MaxCostBits/32))`，所有乘加 checked。同时存活的输入、索引、原/反向弧、堆（有索引，≤V项）、势/距离、临时见证、证书及输出均先预留；释放临时项再减账，峰值为账本高水位。默认不使用静态池、惰性重复堆或隐藏缓存；有额外包装/容量扩容时先追加预留，不把预算当一次性输入估算。PeakMemoryBytes 返回该保守预留峰值；实际分配/GC/RSS 在 Benchmark 另测，不混称实测峰值。后端通过端口声明的峰值与同时存活 Core 预留相加检查。

Relaxations 计所有求解/参考/替代/证明遍历中检查的有效残量弧次数（不只成功更新距离），查询开始即计 AlternativeChecks；Count、验证、排序和复制另计时间/预留，不伪装为免费工作。协作检查至少每256次弧检查、每256个输入项、每次增广/查询/证书发布前执行；排序比较器每256次比较检查 token/deadline，异常须转换为本请求停止原因。单次 BCL 分配、BigInteger 运算、输入索引或回调不可抢占，不宣称硬实时。

## 7. 适配器和宿主接入

### 7.1 宿主职责适配（不是 Core 公共接口）

以下名称是宿主职责角色，不是本模块要实现或导出的 I* 接口。宿主直接组装 §3 DTO、调用 §7.3 factory，并消费 §5 结果；不用补猜这些角色的签名或强制引用其它模块：

1. `IGraphSnapshotAdapter`：把宿主候选对象转换成稳定顶点、边、证据键和输入修订；完成物理去重和跨视野补边后才调用。
2. `ICostAdapter`：按宿主冻结的方法和 `CostScaleId` 计算费用；输出后不得由核心重算几何或更改费用。
3. `IAssignmentResultProjector`：把匹配、未匹配、见证和证明投影回宿主对象；不得把核心结果直接写成质量事实。
4. `IAssignmentTelemetry`：接收结构化事件、计数和耗时；不通过静态 logger 或数据库隐藏副作用。
5. `IAssignmentSerializer`（可选）：负责版本化快照和结果封存；必须保存输入摘要、算法修订、费用尺度和完整性。

两类宿主接入都固定按以下步骤执行：①保留调用方的左右全集和键到原对象的两个只读映射，孤立点不可丢；②仅把调用方已批准的合法边及冻结费用逐条构成AssignmentEdge，证据键与原边证据单独映射；③输入/方法/完整性与用途冻结后调用同一factory；④先核RequestId/InputRevision/ContractRevision/AlgorithmRevision，再按Proof消费可用匹配、覆盖和未匹配全集；NotStarted占位不投影为空缺陷；⑤使用键查回本次原对象和证据，缺键/版本不一致是宿主绑定故障，停止投影，不重新建边修补旧结果；⑥保存本次请求及回执，不把Alternatives或不完整结论提升为主映射事实。Core不计算距离或设计工艺费用公式，未知物理门由§15.1明确Owner提供。

### 7.2 版本兼容

公开合同按语义版本管理。补充可选字段不改变旧默认值时可在次版本兼容；改变目标函数、费用解释、证明状态、键排序、错误语义或结果精确性须改 ContractRevision 并重新建立 Golden（1.0 后升主版本，0.x 提升次版本亦视为破坏变更）。Request 携带 ContractRevision/InputRevision/CostMethodRevision，Result 携带 ContractRevision/AlgorithmRevision/InputRevision；费用方法与输入摘要通过 RequestId 关联宿主封存的请求，不假称 Result 有未定义字段。AlgorithmRevision 由包内只读常量固定为 `exact-ssp-residual-v1`，不得依机器/时间随机生成；同一修订不得偷换二进制。

宿主升级流程：读取旧快照 -> 验证依赖版本和 hash -> 在 Replay 中对照旧结果 -> 通过反例、Golden 和性能门 -> 小范围 Shadow -> 才切换默认实现。回退由宿主发布清单选择上一份已验证模块包；本模块不自动迁移或删除旧证据。

### 7.3 可构造 Core 与显式外部候选端口

以下为公开签名（静态方法只列签名，非带空实现的产品代码），与附录 A 同步。默认 factory 仅依赖 .NET 10 BCL，返回无状态 Solver；无服务定位器、文件读取、隐式 native 初始化或产品单例。

```csharp
public static class AssignmentSolver
{
    public static IAssignmentSolver Create(IAssignmentCandidateBackend? candidateBackend = null);
}

public sealed record AssignmentBackendRequest(
    AssignmentRequest Snapshot,
    TimeSpan RemainingTime,
    long RemainingRelaxations,
    long RemainingMemoryBytes);

public enum AssignmentBackendOutcome { Unsupported = 0, Candidate = 1 }

public sealed record AssignmentBackendReply(
    AssignmentBackendOutcome Outcome,
    IReadOnlyList<AssignmentMatch> Matches,
    long Relaxations,
    long PeakMemoryBytes,
    string BackendRevision);

public interface IAssignmentCandidateBackend
{
    AssignmentBackendReply Propose(
        AssignmentBackendRequest request,
        CancellationToken cancellationToken);
}
```

后端只接收全图私有只读快照；输入校验及完整分量枚举完成后、首个 ComponentStarted 前，每请求最多一次 Propose，不在每分量重置预算。RemainingTime 是从原始接纳时刻扣除复制/排队/校验后的正剩余量，计数/内存同理；无剩余额度按相应停止门返回（时间→DeadlineExceeded、松弛→RelaxationBudgetExceeded、内存→MemoryBudgetExceeded），不得静默跳过显式注入的对照后端。Core 为该调用创建“调用方token + 剩余deadline”的linked token，停止后仍等待Propose真正退出，再释放该CTS；仅deadline触发映射DeadlineExceeded，调用方也已取消时按 §6 优先级，不把所有OperationCanceledException当人工取消。未触发linked token的取消异常是后端故障ASGN-052。后端必须以 §4.3 精确费用工作，不自行设eps或补边；只能容纳int64的Adapter遇不能无损装入的图应Unsupported，不舍入为可装入。Unsupported的Matches必须空；两种回执Relaxations/PeakMemoryBytes均非负且不超过余量，BackendRevision用键格式（可含版本/hash）。用量累计到整请求；非法回执/未知枚举/空回执为ASGN-052。

Candidate匹配只作可验证候选，不能直接写最终Matches/代表解。后端回执集合须在Core复制期间稳定，返回后不得后台修改；Core先按剩余预算复制回执，不保留可写数组，再检查原边/证据/规范化Cost比特一致、互斥及分量覆盖。仍从零运行确定性主路线，每分量比较候选K/精确C并用主路线证书核对，核对通过后才提交该分量证明或发布 MainSolutionProved；不符为ASGN-031，该分量回到 NotStarted、清空候选/主解证明，已独立核对通过的其它分量仍可保留。合法不同最优映射允许，最终代表解仍按 §4.2，替代由Core负责。此端口用于后端对照/迁移，v0.1不承诺提速或以自报状态作证明；真实加速复用须另修订算法版本并获得同等证书/确定性验证，不能临时省略复核。

Propose 是同步有限调用，不能保存快照/回调、不能在返回后继续用后台线程写入，也不能返回仍持有请求资源的“已取消”。收到 token 后协作停止，回执返回或 OperationCanceledException 抛出前必须完成其请求资源释放；Core 捕获取消并按实际停止门生成结果。其它异常为 ASGN-052。宿主始终拥有后端实例的 Dispose/连接生命周期；Core 不替它释放实例。native/远程求解只允许宿主隔离适配，Adapter 须在本调用结束前等待真实停止/排空；未知时 Propose 保持未返回，Core Task 保持未终结且不发 Drained/ResourcesReleased。断连/迟到的旧回复不能被绑定到新请求，宿主隔离未排空进程和凭证；真实 OR-Tools/远程客户端实现是后续适配切片，不影响默认纯 Core。未具备此保证的后端不得注入。

## 8. 无 UI 调用示例

下面是未来 Core 程序集完成后可直接置于 net10.0 Console 的完整顶层 Program.cs 示例，当前未编译；不省略 solver 构造，不依赖 BuildSnapshot/telemetry/产品服务。数据是合成数学反例，不是现场样本；正式宿主负责费用方法及图修订。最小调用顺序：引用一个 Core 程序集→Create→冻结请求→SolveAsync→检查终态/证书→按本次快照投影→保存请求和结果；同步入口可在自己的工作线程替换调用。

```csharp
using System;
using System.Linq;
using System.Threading;
using Asun.Modules.Assignment;

IAssignmentSolver solver = AssignmentSolver.Create();
var request = new AssignmentRequest(
    new AssignmentRequestId("demo-001"),
    new AssignmentInputRevision("synthetic-n01-v1"),
    [new(new("l1")), new(new("l2"))],
    [new(new("r1")), new(new("r2"))],
    [
        new(new("l1"), new("r1"), 0.0, new("e-l1-r1")),
        new(new("l1"), new("r2"), 4.0, new("e-l1-r2")),
        new(new("l2"), new("r1"), 3.0, new("e-l2-r1"))
    ],
    CandidateGraphCompleteness.Complete,
    AssignmentObjective.MaxCardinalityThenMinCost,
    "host-cost-v1",
    "method-2026-09",
    new AmbiguityPolicy(Delta: 0.0, CheckAlternatives: true, MaxWitnesses: 1),
    new AssignmentBudget());

using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
AssignmentResult result = await solver.SolveAsync(request, cts.Token);
if (result.Status != AssignmentRequestStatus.Completed || !result.ResourcesReleased)
    throw new InvalidOperationException(result.Termination.ToString());
var component = result.Components.Single();
var pairs = component.Matches.Select(m => $"{m.Left.Value}/{m.Right.Value}");
if (component.Cardinality != 2 || string.Join(",", pairs) != "l1/r2,l2/r1" ||
    component.TotalCost.IntegerValue != (new System.Numerics.BigInteger(7) << 51) ||
    component.TotalCost.BinaryExponent != -51 || component.Certificate is null ||
    component.Ambiguity != AmbiguityStatus.NoAlternativeWithinDeltaProved)
    throw new InvalidOperationException("N-01");
```

此例共同尺度由 cost=3 的 normal exponent=-51 冻结，精确费用 `(7*2^51)*2^-51=7`；不能先把所有系数化为小整数却沿用原 exponent。生产宿主不直接用上述异常字符串做操作员消息；按 §5 错误键投影三语。事件/进度是可选，完全不订阅也必须得到同一数学结果。

## 9. 正常、边界和失败案例

| 编号 | 输入 | 必须得到 |
|---|---|---|
| N-01 | `l1-r1=0,l1-r2=4,l2-r1=3` | `K=2,C=7`；不能被贪心 `l1-r1` 降为 `K=1` |
| N-02 | 2x2 四条边费用均 0 | `K=2,C=0`，至少一份替代见证；稳定排序不代表唯一 |
| N-03 | 只有 `l1-r1=0`，全集含 `l2,r2` | 保留两个孤立/未匹配顶点，`K=1` |
| N-04 | 左或右为空、无边 | 合法 `K=0,C=0`；不返回异常或 PASS 业务结论 |
| N-05 | 两个左顶点争一个右顶点且费用相同 | `K=1`，未匹配左侧存在替代歧义 |
| N-06 | `l1-r1=l2-r2=l1-r2=1,l2-r1=1.25,delta=0.25` | 主解C=2，替代C=2.25，等号包含，返回 AlternativeWithinDeltaFound |
| N-07 | 输入顺序随机置换 | `K/C` 和歧义状态不变；代表解按稳定键可复算 |
| N-08 | `cost=0.5` 与 `1.0` | 同一尺度比较差值 0.5，不能因整数系数视觉相同误判 tie |
| N-09 | `Partial` 或丢跨域边 | 返回图内证明和完整性字段；不得转成物理唯一或缺失判定 |
| F-01 | 重复顶点、未知端点、重复同边 | `ASGN-002/003`，不静默合并或取最小 cost |
| F-02 | NaN、Infinity、负 cost、负 delta | `ASGN-004` |
| F-03 | 主解完成后在最后一次替代前取消 | 保留主解及证书，Proof=AlternativeProofIncomplete、Ambiguity=NotProved，Status=Cancelled |
| F-04 | 位宽、内存或 deadline 不足 | 保留已完成阶段，返回对应预算/数值停止原因，不截断输入 |
| F-05 | 前驱环、负约化边或费用复核不一致 | `ASGN-040/031`，撤销受影响证明 |
| F-06 | 两请求共享同一只读输入，一方取消 | 另一方结果不受影响，无静态工作区串写 |
| N-10 | 一左两右，l1-r1=l1-r2=0 | K=1，替代需经 t；N-05 的两左一右替代需经 s，都必须找到 |
| N-11 | 完全2×2图四边各 double.MaxValue | 单分量K=2、精确C=2*MaxValue；DisplayOverflow=true，不因显示∞撤销证明 |
| N-12 | 完全对称2×2零费用，启用替代但任一 MaxWitnesses=0，或 MaxAlternativeChecks=0 | Completed+CostProved+NotEvaluated，不得因稳定代表映射显示“唯一” |
| N-13 | N-06 的 delta 由0.25改为小于0.25的相邻 binary64 | 前者带内见证，后者可证明无带内见证；创建新 InputRevision/RequestId，不复用旧结论 |
| N-14 | 同一 N-02 图仅改显示标签/文化/原输入排列 | K/C、代表边和证明不变；仅显示标签变化；不得按显示排序重求解 |
| F-07 | 不同合法边使用相同 EvidenceKey；undefined Completeness；ContractRevision="0.2" | 分别 ASGN-003/007/006；不自动重编号、降级或猜语义 |
| F-08 | 外部候选返回1条贪心边作为 N-01 的 OPTIMAL，或饱和费用/缺边 | ASGN-031，拒绝后端候选，不输出 Completed |

## 10. 第二轮场景驱动架构复审

本节用两种独立审查视角：A 从数学能力/反例逐步执行建图校验、最大基数、费用、替代证明及证书；B 从不知平台内部的接入实现者追踪配置、并发、停止、未知回执、持久化和关闭。S-01～S-14 共同覆盖两者，不能用只读 API 表代替正常和失败链。弱信号/噪声/遮挡/几何退化不转入 Core 图像算法，而通过宿主候选完整性和合法边冻结表达。

### S-01 正常配置与执行

- 输入与参数来源：宿主适配器提供复制期间稳定的 `L/R/E` 快照、`InputRevision`、`CostMethodRevision`；目标函数固定；`delta` 来自宿主版本化策略；预算来自宿主 Profile，不从页面显示值推导。
- 处理顺序：接受事件 -> 复制并全量校验 -> 分量 -> 势函数主解 -> 替代检查 -> 精确复核 -> Core 工作区排空和释放。
- 输出/状态：各分量 `CardinalityProved`、`CostProved`，按策略完成替代证明；算法工作结束后发布 `Drained`，释放 Core 工作区后发布 `ResourcesReleased` 和整体 `Status=Completed`。返回结果的 `ResourcesReleased` 为 `true`。
- 恢复动作：纯计算可用同一快照确定性重放，重试创建新 RequestId；已有持久回执先由宿主按原 RequestId/InputRevision 查询，Core 本身没有查询/耐久幂等接口。
- 可判定验收：DFS、Bellman-Ford 和主路线的 `K/C` 一致，结果边互斥且费用按同一尺度重算相等。

### S-02 空输入与部分成功

- 输入与参数来源：空左右集合、无边图，或多个分量中只有部分图满足预算；参数仍来自同一请求快照。
- 处理顺序：空图直接完成；多分量按稳定顺序执行，在每个安全点检查取消/预算。
- 输出/状态：空图返回 `K=0,C=0` 和孤立全集；部分完成返回已完成分量及其证明，未完成分量标 `NotStarted` 或 `AlternativeProofIncomplete`，整体保留 `Cancelled/DeadlineExceeded/BudgetExceeded`，不得伪装为完整 `Completed`。
- 恢复动作：宿主保存已完成分量证据，以新 RequestId 重放同一完整快照；Core 无 resume/cursor 入口，不从未完成分量恢复，不拼接不同请求的部分结论。
- 可判定验收：空图不报输入错误；取消后已完成 `K/C` 不丢失，未完成分量不出现唯一性结论。

### S-03 歧义与错误输入

- 输入与参数来源：等费用或 `C_e <= C* + delta` 的图；另测重复键、未知端点、重复同边、NaN/Infinity/负费用。
- 处理顺序：先做结构/数值校验，合法图再主解和禁边查询；错误输入不得进入求解器。
- 输出/状态：合法歧义返回 AlternativeWithinDeltaFound 和不同边集合；错误输入返回 InvalidInput 及 ASGN-001..007；null 请求按 §3.4 为调用异常。
- 恢复动作：修正原始建图或费用方法并生成新的 `InputRevision/CostMethodRevision`；不在核心内合并边、取最小费用或自动增大 `delta`。
- 可判定验收：`delta` 等号包含；重复输入每次得到相同错误码和字段定位；错误请求不分配大工作区。

### S-04 超大、稠密与高并发

- 输入与参数来源：宿主一次提交大分量或多个并行不可变请求；预算包含顶点、边、位宽、内存、松弛和替代次数。
- 处理顺序：checked 估算规模和位宽 -> 预算门禁 -> 再租工作区；并发由宿主调度，单请求内部不无限开 Task。
- 输出/状态：预算内正常完成；超限返回 `BudgetExceeded`、`ASGN-010/011`，不截断边、不按 UI 页拆图、不宣称局部最优。
- 恢复动作：宿主排队、降低并发或提交更高版本 Profile；只有图论连通分量已明确且合同允许时才分量执行，不能按视觉 tile 任意拆分。
- 可判定验收：Core 预留峰值不超过 MaxMemoryBytes，实测托管/进程峰值另列；两个并行请求的 Sequence/Usage/Result 不串写，数值结论与并发度无关，是否因并发达到 deadline 须如实记录。

### S-05 噪声、遮挡与退化上游输入

- 输入与参数来源：模块不接图像。宿主先用其视觉/几何方法处理噪声、遮挡、粘连、缺边、退化位姿，并把候选覆盖写为 `Complete/Partial/Unknown`；边证据键指向宿主证据。
- 处理顺序：模块仅校验并求解给定图，不根据 cost 猜测缺失边，不把低质量候选补成边。
- 输出/状态：可计算时返回图内 `K/C`；`InputCompleteness != Complete` 时结果保留该标记，唯一性只能是图内证明；模块不产生拒识、缺陷或遮挡原因。
- 恢复动作：宿主改善采集/定位/候选生成后创建新快照重算；旧的 Partial/Unknown 结果保留为诊断，不覆盖新结果。
- 可判定验收：同一图的数学结果与上游质量标签解耦；不因单个图内解唯一而输出物理唯一或质量放行。

### S-06 取消、超时与 native 排空

- 输入与参数来源：宿主 `CancellationToken` 和 `Deadline`；本模块无 HALCON/native handle。上游 Adapter 若持有 native 资源，由该 Adapter Owner 管理其租约和排空。
- 处理顺序：入口同步复制输入；在校验、分量、松弛、增广、替代查询和复核处协作检查 -> `StopRequested` -> `DrainStarted` -> 算法工作结束并发布 `Drained` -> 释放 Core 工作区 -> `ResourcesReleased` -> `RequestStopped`。
- 输出/状态：取消为 Cancelled/ASGN-020，deadline 为 DeadlineExceeded/ASGN-021；结果只在 ResourcesReleased=true 后返回。原输入可在复制完成后复用；独立上游视觉排空不进入 Core 终态。若显式注入 §7.3 外部后端，则其本请求必须退出后 Core 才能 Drained，不能把后端未知排空归为无关上游。
- 恢复动作：等待唯一终止回执后，以新请求重放；上游 Adapter 按自身 Owner 完成 native 释放，模块不强杀线程、不假报 Core 停止。
- 可判定验收：取消竞态只产生一个终止事件；Core 返回前无工作区未释放；本模块 native 句柄计数恒为 0（不适用项需在宿主验收中单独证明）。

### S-07 资源上限与数值退化

- 输入与参数来源：费用位宽、指数跨度、总费用、BigInteger 中间值和内存由请求预算计算；不使用饱和整数。
- 处理顺序：估算 -> 拒绝或选择精确路线 -> 运行中持续核对位宽、内存和松弛额度。
- 输出/状态：超位宽为 `NumericalUnresolved/ASGN-030`；预算耗尽为 `BudgetExceeded/ASGN-010/011`；已完成证明独立保留。
- 恢复动作：宿主更换经批准的费用表示或提高 Profile 后新建修订；不能降低精度、放宽 `delta` 或把 Infinity 当费用。
- 可判定验收：0.5 与1.0差值在共同尺度正确；受预算中断的分量不得新增 NoAlternativeWithinDeltaProved；其它已经独立完成分量的证明保留。

### S-08 持久化、重放与版本修订

- 输入与参数来源：可选序列化适配器保存 `RequestId`、输入摘要、完整顶点/边闭包、费用尺度、方法/合同/算法修订和预算；核心不写数据库。
- 处理顺序：封存前完成输入闭包校验 -> 运行 -> 保存结果和终止原因 -> 回放时先验证依赖 hash 与修订。
- 输出/状态：缺依赖、hash 不符、同版本异内容返回宿主兼容错误，不把旧结果当新计算；合法快照可 Replay。
- 恢复动作：原结果未知时查询原操作；输入或方法改变必须新建 `InputRevision/CostMethodRevision`，不能覆盖旧事实。
- 可判定验收：同一版本/同一快照回放 `K/C/歧义状态` 一致；序列化往返不丢精确费用尺度和完整性标记。

### S-09 升级与回退

- 输入与参数来源：宿主发布清单绑定唯一 Asun.Modules.Assignment.Core 包版本、依赖 hash、Contract/Algorithm 修订和回退包。
- 处理顺序：旧快照 Replay -> 反例/Golden -> 性能门 -> Shadow -> 切换；任一门失败即停在旧版本。
- 输出/状态：版本差异必须可见，算法改变不得沿用旧的唯一性证明；回退仍能读取旧快照和旧结果。
- 恢复动作：宿主按清单选择上一份已验证包；不删除新版本诊断，不自动迁移或修改历史结果。
- 可判定验收：同一快照的差异可定位到版本/费用/排序/证明字段；回退后旧结果可查询且不发生静默重算。

### S-10 无 UI 调用与可选 UI 投影

- 输入与参数来源：无 UI 直接调用 `Solve/SolveAsync`；可选 UI 只订阅结果/事件投影，参数仍来自同一宿主配置和快照。
- 处理顺序：两种入口共用同一 Core；UI 不在页面重求解、不修改边、不把显示四舍五入写回请求。
- 输出/状态：无 UI 与 UI 得到相同 `K/C/Proof/Ambiguity`；页面显示 `Partial/Unknown/NotProved/Drain` 等状态和诊断。
- 恢复动作：UI 断开只影响投影订阅，不取消核心请求；参数修改创建新修订，旧请求按原 Owner 终结。
- 可判定验收：无窗口、无隐藏初始化也能完成最小调用；UI 重连后由宿主保存的 RequestId/Sequence 事件或结果补齐终态，不重复触发求解，迟到 Progress 不复活已结束状态。

### S-11 第二消费者接入

- 输入与参数来源：第二消费者使用独立适配器生成自己的键、证据、费用方法和输入修订，不引用第一个消费者的领域对象、数据库、页面或生产事实。
- 处理顺序：各自建图 -> 同一 Core 和同一 oracle 测试矩阵校验/求解 -> 各自投影和保存；共享的只有公共契约和算法程序集。
- 输出/状态：两消费者结果结构相同但键、证据、费用、`InputRevision/CostMethodRevision` 和结果存储相互独立；任何一方失败不污染另一方。
- 恢复动作：按各自发布和回放策略重试；核心不增加消费者专属分支。
- 可判定验收：第二消费者可在无图像、无设备、无产品 Shell 的最小宿主中运行，并通过同一 oracle 矩阵。

### S-12 长期运行和反复请求

- 输入与参数来源：长期进程反复提交不可变请求，预算和取消由每次请求携带；没有跨请求静态图、静态池或“最近一次”状态。
- 处理顺序：每请求独立创建/释放 Core 工作区；Core 资源释放事件后才允许复用对应工作区；遥测分别记录 Core 工作区和上游 Adapter 租约的峰值、排空及 GC。
- 输出/状态：长期运行中不得跨请求污染结果；序列号每请求从1开始，内存按 Profile 测量。Core 工作区泄漏由诊断测试发现，进程资源故障无法完成回执时为宿主 Unknown；上游租约诊断由其 Owner 提供，不假设 Core 能返回已释放结果。
- 恢复动作：宿主停止接收新请求、完成排空、收集诊断后再按发布策略重启进程；不得用重启掩盖未完成回执或丢失证据。
- 可判定验收：长稳 Profile 下无未归还工作区、无跨请求结果污染、取消后无后台继续写入；P50/P95/P99 和峰值内存满足批准预算。

### S-13 参数改变、弱信号与置信拒绝

- 输入：相同顶点/边但 delta、费用方法、合法边门或完整性政策改变；参数来自消费者版本化策略。
- 顺序：宿主先冻结独立位姿/物理去重和完整合法边→生成新 InputRevision/RequestId→Core 全量重算→宿主结合观测资格作解释；显示语言/排序不改图政策。
- 输出/恢复：低费用或数值唯一不产生 confidence/PASS。弱信号、遮挡、位姿退化不能用大罚分补边或改高置信；宿主可保留 Partial/Unknown 作诊断，改善候选后新修订重算；不自动推荐生产 delta。
- 验收：N-06/N-13 边界按 binary64 精确值判断，旧回执保留；物理门不满足时即使 Core Completed，宿主仍不得放行。

### S-14 关闭、观察器失效、后端断连与迟到

- 输入：双请求并发，一方取消；事件 sink 同步抛异常；Progress<T> 在 UI 关闭后迟到；后端超时/断连或返回前仍有未排空任务。
- 顺序：宿主停收→取消→await 本次任务；Core 等候已注入后端退出、发 Drained、释放暂存、唯一终止。无后端时不凭空创建连接状态；后端不退出则任务仍未完成，宿主等待超时不等于 Core 已终结。
- 输出/恢复：同步观察器异常 ASGN-051，后端异常 ASGN-052；迟到进度丢弃，旧后端回执不能写新 RequestId。进程崩溃无回执由宿主标 Unknown，核原存储后用新 RequestId Replay；不伪造成功或自动重发设备命令。
- 验收：可控后端先保持不退出，断言无 Drained/ResourcesReleased/终态；释放测试闸门后仅一次终止并无后台写。关闭后迟到进度不改终态，断开观察器不取消另一个请求。

## 11. 可选 UI 契约

IM-037 是纯 Core，不引用viewport WPF装配，因此Assembly v0.2的Presentation/Lifetime/Unbind/晚到Return不适用，不读改其Root/Close或在此另造lease。无独立控件/PageContract；UI 设计、DevExpress 25.2.3 控件/API 与1920×1080实界面验证在宿主页面切片验收，本模块不适用，也不为本轮新增界面或 dxdocs 调用。以下只约束宿主结果投影，不定义第二个公共 UI 模块。所有可见文字由宿主 zh-CN/zh-TW/en-US 动态资源提供，Core 只输出稳定 MessageKey/Data，不在模块重复设置语言入口。可选视图只显示：

- 输入修订、完整性和费用方法版本；
- 分量、顶点/边计数、主映射、未匹配全集；
- `K/C`、证明阶段、`delta`、替代见证和搜索未完成原因；
- 预算使用、取消/排空状态和可查诊断。

UI 不拖动或编辑生产对应，不以表格截断代替完整输入，不在页面重求解，不隐藏 `Partial`、`Unknown` 或 `NotProved`；运行期间按事件展示排空状态，完成结果的 `ResourcesReleased` 恒为 `true`。修改边、费用或 `delta` 必须创建新的输入修订和新的计算请求。

## 12. 测试与验收矩阵

本节是获准后的测试实施规格，当前不创建工程/测试、不宣称已执行。测试放在唯一 Core.Tests 工程，禁止依赖 UI、图像、设备或数据库；每项固定 Contract/Algorithm/Input 修订和精确期望，测试名对应下表。内部停止/时钟/故障闸门只供友元测试使用，不能成为第二套公开 API。

| 用例ID | 类别 | 覆盖内容 | 验收断言 |
|---|---|---|---|
| ASGN-T-01 | 契约 | 空值、键、重复顶点/边、未知端点、费用格式、输入集合复制隔离 | 错误码稳定，未分配大工作区；入口返回后修改原集合不改变运行请求 |
| ASGN-T-02 | 数学 oracle | 左右各0..3顶点的全部缺边拓扑，每拓扑分别全0费用及稳定边序 mod3 费用；再用固定种子37037生成2,000份左右各≤6的小图 | 独立 DFS 枚举部分匹配，K/C相等；证明覆盖全部输入边、覆盖大小=K，势逐有效残量弧非负；未匹配全集准确 |
| ASGN-T-03 | 主路线 | Bellman-Ford 与势函数 Dijkstra | 每轮流量、精确费用、残量不变量一致 |
| ASGN-T-04 | 替代证明 | 禁边重解与残量环对照 | 近等价见证/无替代结论一致 |
| ASGN-T-05 | 稳定性 | 左右输入、边顺序、分量顺序置换 | 结论不变，代表解可复算 |
| ASGN-T-06 | 数值 | 0、次正规、大指数跨度、大总和、`delta` 等号 | 共同尺度正确；超位宽明确未决 |
| ASGN-T-07 | 完整性 | Complete/Partial/Unknown、孤立点、断跨域边 | 图内证明与输入资格分列 |
| ASGN-T-08 | 取消 | 接纳前已取消、复制/校验、松弛、增广前后、替代末段、LogicalCompleted 后取消 | 返回 AssignmentResult 而非取消 Task；安全点之前无半路径结果、已冻结终态不改；唯一回执、工作区计数归零 |
| ASGN-T-09 | 预算 | 顶点、边、内存、松弛、替代、deadline | 不截断、不重置预算，保留已完成证明 |
| ASGN-T-10 | 并发 | 两请求同图、一方取消、不同图并行 | 无静态状态、结果不串写 |
| ASGN-T-11 | 故障注入 | 负约化边、环前驱、外部结果饱和/错边 | `ASGN-031/040`，撤销错误证明 |
| ASGN-T-12 | 序列化 | 输入/结果/版本/hash/精确费用 | 往返后可重放；缺依赖拒绝 |
| ASGN-T-13 | 第二消费者 | 通用几何候选关联工具独立接入 | 不引用具体制程对象或页面即可运行 |
| ASGN-T-14 | 生命周期/事件 | S-14，sink 在每个 Kind 抛出，progress.Report 同步抛出、异步处理迟到、关闭/观察器阻塞闸门 | ASGN-051诊断有界；Sequence从1连续；不省略释放链；无后端/算法任务运行时发 Drained；迟到投影不能复活终态 |
| ASGN-T-15 | 后端端口 | Unsupported、合法其它最优解、贪心次优、饱和/错证据/重复边、非法用量、取消、异常、延迟排空 | 候选不改变代表解；ASGN-031/052分类稳定；保留未结束后端时不得有资源释放/终态 |
| ASGN-T-16 | 版本/发布 | 不支持合同、精确数值往返、旧包/新包同图回放，独立引用构建 | ASGN-006；不读取产品 Store；每个包绑定算法和hash，差异不得冒称同修订 |

用例ID采用上述ASGN-T-01～ASGN-T-16类别ID加具名子例；§9反例保留N-01～N-14/F-01～F-08，枚举图/随机图附拓扑编号或种子及样本序号，停止/事件案例附阶段，确保失败可复现而不新建清单文件。

确定性输入生成不依赖System.Random跨运行时实现：测试内使用UInt32状态x=37037，Next先计算 `x=unchecked(1664525*x+1013904223)` 并返回x。每份随机图依次取nL=Next()%7、nR=Next()%7；按左/右索引嵌套遍历所有对，每对先取Next()%4，非0才建边，再取Next()%17除以4.0作精确四分之一费用；键为l/r加两位索引，证据为e加两侧索引，不读时钟。图序号固定0..1999，每图共享三种delta对照；置换用从尾到1的Fisher-Yates和同一Next取模，生成与置换状态分开，置换初始x=37037 XOR 图序号。全拓扑按nL/nR递增、掩码0..2^(nL*nR)-1枚举，bit=i*nR+j代表边，不因Dictionary遍历变序。DFS oracle通过独立有理数位解码比较费用；独立禁边冷重解与主路线不共用残量查询代码。

测试内精确往返codec固定为BCL System.Text.Json，仅测试工程持有显式镜像DTO，包含§3/§5全部字段（含证书/诊断/事件）。字段顺序与公开声明一致、枚举为底层整数、BigInteger为invariant十进制字符串、double为16位小写UInt64位模式十六进制（禁止∞/NaN转JSON number）、TimeSpan为Int64 ticks、TimestampUtc为UTC ticks；nullable保留null，字符串不归一化，列表保留顺序，Data按Ordinal键排序，所有property必出、禁止额外property或重复property。写入采用UTF-8无BOM、无缩进、默认System.Text.Json转义；读取先核字段集合、类型及版本，再按上述规则还原，不把反序列化DTO视为已通过请求校验。测试fixture SHA-256使用这些实际写入字节并绑定codec修订 `assignment-test-json-v1`，仅为本模块测试负载身份，不定义平台canonical hash或产品Schema。ASGN-T-12覆盖有限数、MaxValue/显示∞、次正规、-0输入、精确BigInteger/势、null及三种完整性往返；ASGN-T-16覆盖未知字段/版本拒绝。宿主产品持久化沿其已批准Schema，此测试codec不发布为Core服务，不替它猜测格式。

执行顺序：先参数/尺度/DFS→Bellman-Ford对照→主路线不变量→残量环与逐边重解→事件/并发/资源→两个最小消费者→独立打包/回退。关键反例 N-01～N-14/F-01～F-08 作为具名 C# 测试输入，不为每次修订生成 JSON/报告。替代验证对所有小图分别用 delta=0、0.5、1，逐原主解边以独立冷重解核同K费用；所有见证必须与主解边集合不同且同K，检查包括经s/t的非完美匹配。

数值专项用 BitConverter.Int64BitsToDouble 构造最小次正规、±0、相邻 binary64、MaxValue，精确期待值用独立位解码器或有理数 oracle，不调用待测转换函数生成期望。UTF-8键专项含 U+E000 与 U+10000（字节序与UTF-16顺序不同）、未配对代理项和两侧同名；重复证据键必须拒绝。MainSolutionProved 后取消用事件/内部闸门注入，deadline 用单调测试时钟推进，不靠 Thread.Sleep 竞态。内存用预留账本注入不足、BigInteger位宽上限及输出可变数组攻击验证，进程OOM不当可恢复测试。

测试执行栈固定沿当前仓库约定：唯一 Core.Tests 工程为 net10.0、仅 BCL、OutputType=Exe 的断言 harness，不在首次实现时再选择测试框架、SDK或runner。后续代码任务单独获准后执行（本轮未执行）：

```powershell
dotnet build src/Modules/assignment/Asun.Modules.Assignment.Core/Asun.Modules.Assignment.Core.csproj -c Release
dotnet run --project tests/Modules/assignment/Asun.Modules.Assignment.Core.Tests/Asun.Modules.Assignment.Core.Tests.csproj -c Release
```

build失败即停止，不把编译成功算断言执行。dotnet run同时构建并运行唯一Exe；dotnet test不执行此Exe，不作为本模块测试命令或通过证据。harness在代码中固定当前切片必需用例集合及预期断言数；默认执行该切片全部必需项，只在全部执行完成且通过时返回0。断言失败、异常、未完成、必需项跳过、零用例或超时均返回非零；逐用例输出ID及Passed/Failed/Incomplete/Skipped/TimedOut，失败定位到断言，结束时汇总实际与预期用例/断言数。过滤或诊断模式不能以部分通过给该切片成功退出码；不把未执行的后续切片或性能测量写成通过。

每用例以单调时钟设置120秒内部截止点，整次正确性harness设置15分钟内部截止点，超时记对应ID并非零退出；等待/闸门/任务均有限，超时禁止自动重试或延长预算。外层调用者对build设5分钟、对dotnet run设20分钟进程超时（含测试工程构建）；外层超时记录当前用例ID或HARNESS-STARTUP、标TimedOut/非零并终止本次测试进程树，保留输出。外层终止只用于隔离测试执行，不能冒充被测Core已排空。Benchmark独立模式沿 §13 的有限Profile截止点及明确大于内部上限的外层进程超时；Profile缺失或必需测点未完成不得给性能验收成功。上述工程超时不构成产品节拍目标。

打包切片另执行 `dotnet pack src/Modules/assignment/Asun.Modules.Assignment.Core/Asun.Modules.Assignment.Core.csproj -c Release --no-build`，外层进程超时5分钟，失败/超时非零。脱离仓库的 net10.0 Console 只引用产出的包，执行 §8，不能靠本仓库 Directory.Build.props、解决方案全量输出或产品启动器补依赖；此隔离 Host 是打包验收的临时构建，不新增长期空工程。

产品验收还需由各宿主另行完成真实图建图、方法资格、计量、页面、性能和现场证据；这些不是本模块测试的替代物。

## 13. 性能预算与可观测性

### 13.1 复杂度和测量

设每分量原顶点数 n=nL+nR，网络节点数 V=n+2，原合法边数 E，残量弧数 A=2*(E+n)，匹配数 K。Bellman-Ford 参考最坏 O((K+1)*V*A)，势函数主解 O((K+1)*(V+A)*log V) 算术操作，残量替代至多K次 O((V+A)*log V)；逐边冷重解参考另乘主解K级成本。不能把节点/弧混写为2E+V+2，也不能把索引堆和重复入堆峰值混同。BigInteger位宽B、比较/分配和GC另计，不把操作数当工业时延。

每个消费者必须提供不可变 `BenchmarkProfile`，绑定模块/Core 版本、算法/费用刻度修订、OS/CPU/运行时和输入 fixture hash。负载按 `L/R/E`、最大连通分量、边密度、匹配数 `K`、费用位宽、替代证明频率、并发、队列和冷/热状态分桶；任何尺寸只是测量维度，不是未经批准的节拍或容量承诺。Profile 预先冻结预热次数、测量次数、最低有效样本数、有限 deadline、资源/队列/并发上限、吞吐观察窗口及阈值来源。冷态无预热；热态按固定次数预热，预热样本不计入测量。

使用单调时钟测输入复制/校验、排队、分量构建、显式后端、主解、证书、替代及从接纳到 ResourcesReleased；宿主序列化/等待UI投影另测，不混入纯 Core 阶段。BudgetUsage.Elapsed 为接纳到 Core 资源释放，Drain 为 DrainStarted 到资源释放，Vertices/Edges 为已知输入Count（尚未取得为0且不能据此断言空图）；Relaxations/AlternativeChecks/PeakMemoryBytes 按 §6。另测取消到停止/释放；注入后端的native排空由其Adapter提供，独立上游视觉排空不算Core。未观测native标Unknown，不能计0。通用P50/P95/P99、样本有效性/失败/删失按 [DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，本模块不复制分位算法。K=0是合法图解，不计“求解无解失败”；分别统计输入拒绝、计算故障、替代未证、预算/数值终止和未排空。没有采纳目标时为 NotEvaluated/TargetPending，不声称达标。

可执行负载计划：在 Core.Tests 中以独立 Benchmark 模式重复调用同一 factory，固定种子37037生成链式竞争/稀疏局部/完全二部图/孤立点/多分量/大指数跨度图，并用N-01/N-05/N-10植入非完美匹配。每份消费者 Profile 显式列出 (nL,nR,E,最大分量,K,费用位宽,delta,替代开关/上限)、并发1/宿主实际批准并发、预算和输入hash；超大或稠密桶若越预算，应测拒绝路径而不是截边。先校验小图真值及预留界，再执行 Profile 规定的冷态/预热/测量批次，以资源释放事件取样，失败/未结束单列并停止性能判通过。没有Profile仍可做诊断测量，不在本指导编造批次、吞吐或客户节拍目标；长期运行与取消最长不可抢占块同属Profile门。

Benchmark调用固定为 `dotnet run --project tests/Modules/assignment/Asun.Modules.Assignment.Core.Tests/Asun.Modules.Assignment.Core.Tests.csproj -c Release -- --benchmark <已采纳ProfileId>`；Profile由测试工程内不可变配置提供，不让Core读取配置文件。ID不存在、必要字段/目标来源缺失或任何必需负载未完成时非零，记录ProfileId及负载ID，允许保留NotEvaluated诊断数据但不能返回验收成功。外层超时由该Profile的整批内部截止点加5分钟构建/退出余量给出，仍为有限值；未采纳Profile不启动无界批次。

生成图的拓扑固定：链式竞争含(i,i)及(i,i+1)合法索引边；稀疏局部含(i,i+d)，d取0/1/3且不环绕；完全二部含所有对；孤立点不补边；多分量按Profile各分量尺寸生成后以分量前缀合并、不补跨分量边。基础费用按§12的LCG逐稳定边序取Next()%17/4.0，生成的E/K/分量大小须与Profile登记值复核，否则拒绝该负载，不能静默截取。大指数跨度使用Profile提供的显式binary64位模式fixture，N-01/05/10植入作为独立分量、键加前缀，并计入最终总量及hash。尺寸/并发/冷热/采样数只取已采纳Profile，不从默认预算推导虚构节拍；每桶完成主解及所请求替代策略才可形成性能样本。

### 13.2 结构化观测

宿主可选遥测投影（§7.1的角色）从 AssignmentEvent/Result 及保存的 Request 得到以下字段，不表示 Core Event DTO 有同名全部字段：

- `request_id`、`input_revision`、`component_id`、`algorithm_revision`；
- `left_count`、`right_count`、`edge_count`、`matched_count`；
- `proof_state`、`ambiguity_status`、`termination_reason`；
- `elapsed_ms`、`queue_ms`、`drain_ms`、`peak_memory_bytes`；
- `relaxations`、`alternative_checks`、`cost_bits`、`budget_remaining`；
- `input_completeness` 和 `evidence_digest`。

日志不得记录完整图或敏感标签，除非宿主显式提供脱敏策略。指标不能替代结果字段；未知工作总量不生成虚假百分比。

## 14. 发布、回退和第二消费者

v0.1 固定单独发布 `Asun.Modules.Assignment.Core`：DTO/枚举/事件/factory/后端端口与纯计算同一 DLL、命名空间 Asun.Modules.Assignment，TargetFramework=net10.0（不是net10.0-windows）、UseWPF/UseWindowsForms均false，仅.NET BCL运行依赖。此处不再建议另建未绑定的Abstractions工程；将来拆包须明确版本和消费者迁移。打包应含程序集及XML文档，发布清单绑定包版本、合同/算法修订、构建提交或获准可审计快照、文件hash、反例/测试结果、兼容范围与回退包；复用既有发布流程，不提前造证据包。依赖外部后端由宿主独立适配包负责，Core 不捆绑 HALCON/AsunImage/UI/native求解器。

第一消费者为钻孔候选关联 Adapter：目标键来自宿主名义孔，观察键来自已物理去重的观测孔，宿主冻结独立位姿、合法边、无量纲归一费用与delta；Core只收键/边/费用。第二消费者为通用几何关联工具：独立点集/特征键/证据、自己的合法距离门与费用尺度，缺边明确不传入，不引用钻孔对象。两者分别生成InputRevision并保存请求/结果，调用同一Core；测试工程分别以DrillGraphConsumerFixture/GeometryGraphConsumerFixture两套薄Adapter执行N-01/N-02/N-05及不同费用图，不共享领域类型、数据库、页面、静态配置或生产事实。再测两Adapter同实例并发、一方取消/后端失败不污染另一方。真实图生成与钻孔阈值仍由消费者提供，合成Fixture只证明接入独立性。任何消费者不得从Core结果直接放行或驱动设备。

双消费者Fixture的薄Adapter由各自测试内私有记录承载：Drill侧只保存TargetKey/ObservedKey/LegalPair/已冻结Cost/证据，Geometry侧只保存FeatureKey/ObservationKey/AllowedPair/已冻结Score/证据；分别逐项映射到同一公开DTO，不共用领域记录或建图函数。N-01/02/05分别给两者键加drill-/geom-前缀，Expected按原反例替换键；各自保存返回键到原记录的映射并断言未匹配全集/替代边都能回查。再给Geometry独立2×2合法边费用1、2、3、4（按l1r1、l1r2、l2r1、l2r2）及delta=0：K=2、C=5、有带内替代；Drill同时运行N-01仍K=2、C=7、无替代。费用皆为合成冻结输入，不假装验证真实孔或距离阈值。生命周期用两份独立token、事件列表和后端实例；各自Replay请求后原结果不变。

回退测试在隔离进程各加载旧/新包，使用同一输入（新RequestId）对比K/C/主映射/证书/替代状态，差异定位到合同/算法/费用版本。破坏变更按 §7.2 升合同及包版本，宿主按清单保留旧程序集和读取器；Core不自动迁移快照，旧读取器不支持新增字段时明确拒绝而非忽略证明。回退不删除新证据，也不将旧证明移植到新图。

## 15. 开发准入和完成判据

唯一准入依据为 DEV-GOV-010 §3.1；不得要求“实现测试已经通过才准创建测试工程”，也不得以平台 Schema/客户物理阈值未定阻断无关纯 Core。主控于2026-10-09完整复核§1～§16及附录，并核对33个公开声明正文/附录一致，已接收C1～C4的六项文档规格。结论为 ModuleCoreImplementationReady（规格准备），不是产品编码授权；后续实现须另行派发并确认权威仓库/分支或获准可审计快照。下表分列已接收内容与未执行的实现/资格证据。

| 六项 | 已接收的文档规格 | 后续实现/资格证据 |
|---|---|---|
| 1 边界/消费者 | §1、§14：固定一对一图；钻孔与通用几何工具，两薄Adapter计划明确 | 已接收边界及消费者；真实消费者适配尚未实现/验证 |
| 2 精确API/状态/资源 | §3～§7、附录A：factory、版本输入、证书、后端端口、默认值/错误/停止已给出 | Core契约已接收；平台Schema映射仍待原Owner采纳 |
| 3 无UI最小宿主 | §7.3、§8、§14：BCL-only net10.0单DLL及完整Console调用 | 后续真实编译、隔离引用；本轮未创建代码 |
| 4 可判定测试 | §9～§12：反例、双视角、取消/关闭/迟到/后端排空、回退断言 | 实现后执行oracle/并发/资源及两个消费者Fixture；当前未测 |
| 5 性能计划 | §6、§13：账本/实际资源分列、负载/测点/统计引用、目标来源 | 测量方法已明确；实际消费者Profile和性能目标待采纳，不阻断纯Core准备 |
| 6 唯一落点/路径 | §8、Core implementation binding：Core/Tests唯一目录、最小调用和禁止路径 | 唯一落点已接收；代码开始前仍须确认权威仓库/分支或获准快照 |

可实施切片依次为：C1输入契约/精确数值与独立oracle；C2确定性主解/最大基数和费用证书；C3残量替代/事件/停止及完整输出；C4后端端口契约测试/双消费者/独立包与Benchmark。切片是实现依赖顺序，不缩减整模块范围，不得在C1完成时宣布模块完成。C1～C4的六项文档规格均已接收，状态为 ModuleCoreImplementationReady（规格准备）。本轮只有文档状态同步、测试执行约定补齐及定向检查；未创建工程，不授权产品编码，不表示切片已实现或测试通过。

后续边界：平台事实/序列化映射由原Contract Owner在集成切片采纳；真实HALCON建图、物理去重、方法资格/阈值、Golden/Replay/现场性能和宿主WPF由对应消费者切片关闭；实际OR-Tools/native/远程Adapter须另完成精确输入范围、有限取消和真实排空验证。以上不自动变为Core运行依赖，不阻断不依赖它们的C1～C3。任何Completed均仅指给定图内计算，不是视觉、工艺、质量或生产通过。

### 15.1 全批准范围结论与剩余Owner（2026-10-11）

原永久会话复用2026-10-09来源研究、算法/状态自审及已接收C1～C4规格；本轮仅关闭显示编码、确定性harness输入、独立双消费者接入及外部责任定位缺口。按当前架构IM-037全部批准能力，**可决定的软件设计欠账已闭合**：§1/§7/§14定义全部消费者与约束边界，§3～§6定义费用/版本/逐步算法/证明/停止资源，§8～§12定义调用、反例、测试codec和完整Exe harness，§13～§14定义负载/测点/失败判据与发布回退。纯图核心、候选端口、恢复和独立双消费者均有唯一实施路径；没有遗漏待自行设计的模块UI、自动参数或产品Adapter。全模块文档准备已完成；C1～C4保持ModuleCoreImplementationReady（规格准备）。这不是ImplementationSpecificationReady或代码/运行资格通过，不需要再等待总控内容复核。

| 未完成项 | 精确Owner与输入 | 影响/门禁 |
|---|---|---|
| 产品合法边/费用/物理资格 | 各消费者应用Owner：钻孔/微孔、插装/波峰针孔、OCR应用、适用SPI子问题及通用工具，提供独立基准/物理去重/完整性、合法边规则、费用方法/尺度与delta用途Profile | 只阻断该应用物理解释及产品接入；不改变Core目标函数 |
| 平台持久化/事实映射 | 原C-03/C-04/C-07 Contract与持久化Owner，提供正式Schema及历史读取器 | 阻断产品快照/事实集成；测试codec不代替正式Schema |
| 特定native/远程后端 | 实际被选中的Adapter Owner提供明确库/协议版本、精确可容纳范围、真实有限停止及排空证据；当前没有批准交付某个vendor Adapter | 未能满足§7.3则不得注入；固定端口/默认Core设计不受阻 |
| 消费者性能/长期运行目标 | 消费者Profile Owner给§13全部冻结字段、真实负载/样本hash、节拍/资源/取消上限和阈值来源 | 无Profile仅诊断NotEvaluated；独立数值、P50/P95/P99、实际峰值及排空尚未运行 |
| 实际实现与资格 | 后续获派模块实现Owner确认权威仓库/分支或获准快照，执行§12编译/harness/独立引用/资源；应用Owner执行真实视觉/计量/宿主WPF与现场验收 | 本轮不创建代码、测试、UI或包；合成例/文档校验不冒充运行门通过 |

上述是外部事实或未执行的实现验证，没有把应由本模块决定的算法、API、编码、状态、线程、资源或测试runner移交未来Owner；新增容量/目标函数/UI/native后端交付须先改变已批准范围，不计入本轮完成结论。

## 16. 自审记录

- 2026-10-11全范围收口只修改本唯一指导：复用有效研究/自审，针对新增步骤核对数值显示边界、生成顺序、双消费者期望、harness及外部门定位；检查本文件链接/锚点、围栏、公开签名与已有消费者兼容fragment。未运行C#、上游库、数值/性能、WPF或现场验收。
- 本文只写入 `docs/independent-modules/assignment/`，没有修改入口、进度、PKG、制程指导、客户项目或 AsunImage 内部。
- 核心职责限于有限二部图的最大基数、最小费用和分量级替代证明；候选生成、目标解释、工艺评价、质量放行和设备副作用均留给宿主。
- 没有把 HALCON 算子、`HObject`、`HTuple`、DevExpress、页面 ViewModel 或数据库事实放入公共契约。
- 第二轮场景复审已覆盖正常、空/部分、歧义/错误、超大/并发、噪声/遮挡/退化上游输入、取消/超时/native 排空、资源上限、持久化/重放、升级/回退、无 UI/UI、第二消费者和长期运行；视觉质量只通过宿主完整性字段表达。
- 算法路线已明确主路线、备用路线、oracle、外部后端复核、训练不适用、恢复和不可恢复条件；未新增图像、设备、质量或生产事实职责。
- 本轮以数学证明视角与外部接入视角复审，修订 §2～§15 和附录A：全图势/残量环、证书、版本/参数校验、可构造Core/后端端口、迟到投影、关闭/未知、两个消费者、独立发布及六项准备计划已落入正文。Core C1～C4文档规格已由主控接收；平台映射仍待相应Owner采纳。仅同步规格准备结论及Exe harness执行约定，未声称已实现、实机/性能或生产通过。

## HALCON 26.05 算子资料入口

本模块执行纯图分配，不生成几何或调用视觉算子。宿主候选生成以项目内 [HALCON 26.05 手册](../../../halcon算子手册/operators/) 为准，所有算子经 ImageLibDotNet.cv2 使用；仅实际C#类型/重载/封送有歧义时查公共签名，不扫描AsunImage内部、不重复核验存在性、不另接halcondotnet.dll。

## 附录 A：模块核心 API Contract v0.1（C1～C4规格已接收）

本节定义本独立模块的核心代码边界，优先于正文中仅针对产品集成的“候选/待采纳”措辞。本文已给出的公开类型、方法、事件、错误键、状态、参数表和代码形状，作为对应切片获准后唯一实施依据；本附录的存在不代表准入通过。实现者不得另造第二套核心 DTO、状态机或错误语义。

- Module API Contract v0.1 覆盖无产品事实写入的Core与显式候选后端端口，模拟/假后端只作契约测试，不为数学Core凭空创建Simulator产品。平台C-01～C-08、物理阈值/放行/产品字段/厂商类型不进入API。
- 本轮0.1 Core契约已随C1～C4文档规格接收，尚未代码实现，不伪称已有二进制兼容。本契约及正文为后续单独获准切片的唯一实施依据；任何未定义操作先补指导，平台映射仍归原Contract Owner。
- 本模块无HALCON调用；消费者有视觉Adapter时按26.05手册及ImageLibDotNet.cv2实现，仅实际类型/重载/封送歧义查公共签名。外部native/远程后端按 §7.3 排空契约验收，不让真实Adapter未实现阻断默认纯Core。
- 准入状态：C1～C4为 `ModuleCoreImplementationReady`（规格准备，主控2026-10-09接收六项文档规格）。不授权本轮产品编码；真实编译、独立数值/性能、产品适配和现场资格未执行，后续实现另行派发。

### A.1 Core 公开 API 与契约绑定

本 Core 契约只接收不可变二部图快照并返回图内关联及证明；图构造、物理去重、候选召回/费用解释、制程适用性和最终处置属于宿主。类型与 §3、§5 的字段一一对应，不另建缩减 DTO。

入口复制、异步Task、零请求/非法键和版本按 §3；null请求无事件、其余有执行封套。Proof聚合/证书、替代有效开关、Drained/资源释放和唯一终态按 §4～§6；同步观察异常有界记录，迟到UI投影由宿主过滤。以下为签名索引；静态factory仅列声明，不把该代码块冒充完整可编译实现。完整最小消费程序见 §8。

```csharp
namespace Asun.Modules.Assignment;

public readonly record struct AssignmentVertexKey(string Value);
public readonly record struct AssignmentEvidenceKey(string Value);
public readonly record struct AssignmentRequestId(string Value);
public readonly record struct AssignmentInputRevision(string Value);

public sealed record AssignmentVertex(
    AssignmentVertexKey Key,
    string? DisplayLabel = null);

public sealed record AssignmentEdge(
    AssignmentVertexKey Left,
    AssignmentVertexKey Right,
    double Cost,
    AssignmentEvidenceKey Evidence);

public enum CandidateGraphCompleteness
{
    Complete = 0,
    Partial = 1,
    Unknown = 2
}

public enum AssignmentObjective
{
    MaxCardinalityThenMinCost = 0
}

public sealed record AmbiguityPolicy(
    double Delta = 0.0,
    bool CheckAlternatives = true,
    int MaxWitnesses = 1);

public sealed record AssignmentRequest(
    AssignmentRequestId RequestId,
    AssignmentInputRevision InputRevision,
    IReadOnlyList<AssignmentVertex> LeftVertices,
    IReadOnlyList<AssignmentVertex> RightVertices,
    IReadOnlyList<AssignmentEdge> Edges,
    CandidateGraphCompleteness Completeness,
    AssignmentObjective Objective,
    string CostScaleId,
    string CostMethodRevision,
    AmbiguityPolicy Ambiguity,
    AssignmentBudget Budget,
    string ContractRevision = "0.1");

public sealed record AssignmentBudget(
    int MaxVertices = 10_000,
    int MaxEdges = 100_000,
    int MaxCostBits = 4_096,
    long MaxMemoryBytes = 256L * 1024 * 1024,
    long MaxRelaxations = 20_000_000,
    int MaxAlternativeChecks = 10_000,
    int MaxWitnesses = 1,
    TimeSpan? Deadline = null,
    TimeSpan? ProgressInterval = null);

public interface IAssignmentSolver
{
    AssignmentResult Solve(
        AssignmentRequest request,
        IAssignmentEventSink? events = null);

    Task<AssignmentResult> SolveAsync(
        AssignmentRequest request,
        CancellationToken cancellationToken = default,
        IProgress<AssignmentProgress>? progress = null,
        IAssignmentEventSink? events = null);
}

public enum AssignmentRequestStatus
{
    Completed = 0,
    InvalidInput = 1,
    Cancelled = 2,
    DeadlineExceeded = 3,
    BudgetExceeded = 4,
    NumericalUnresolved = 5,
    ComputationFaulted = 6
}

public enum ProofState
{
    NotStarted = 0,
    CardinalityProved = 1,
    CostProved = 2,
    AlternativeFound = 3,
    AlternativesExhausted = 4,
    AlternativeProofIncomplete = 5,
    Mixed = 6
}

public enum AmbiguityStatus
{
    NotEvaluated = 0,
    AlternativeWithinDeltaFound = 1,
    NoAlternativeWithinDeltaProved = 2,
    NotProved = 3
}

public sealed record AssignmentMatch(
    AssignmentVertexKey Left,
    AssignmentVertexKey Right,
    AssignmentEvidenceKey Evidence,
    double Cost);

public sealed record AssignmentProofCertificate(
    IReadOnlyList<AssignmentVertexKey> MinimumVertexCoverLeft,
    IReadOnlyList<AssignmentVertexKey> MinimumVertexCoverRight,
    IReadOnlyList<System.Numerics.BigInteger> NodePotentials);

public sealed record AssignmentComponentResult(
    string ComponentId,
    IReadOnlyList<AssignmentMatch> Matches,
    IReadOnlyList<AssignmentVertexKey> UnmatchedLeft,
    IReadOnlyList<AssignmentVertexKey> UnmatchedRight,
    long Cardinality,
    ExactCost TotalCost,
    ProofState Proof,
    AmbiguityStatus Ambiguity,
    IReadOnlyList<AssignmentAlternative> Alternatives,
    CandidateGraphCompleteness InputCompleteness,
    AssignmentProofCertificate? Certificate = null);

public sealed record AssignmentResult(
    AssignmentRequestId RequestId,
    AssignmentInputRevision InputRevision,
    AssignmentRequestStatus Status,
    IReadOnlyList<AssignmentComponentResult> Components,
    TerminationReason Termination,
    BudgetUsage Usage,
    IReadOnlyList<AssignmentDiagnostic> Diagnostics,
    bool ResourcesReleased,
    string AlgorithmRevision,
    string ContractRevision);

public enum TerminationReason
{
    Completed = 0,
    InvalidInput = 1,
    CancelRequested = 2,
    DeadlineExceeded = 3,
    VertexBudgetExceeded = 4,
    EdgeBudgetExceeded = 5,
    MemoryBudgetExceeded = 6,
    RelaxationBudgetExceeded = 7,
    AlternativeBudgetExceeded = 8,
    NumericalRangeExceeded = 9,
    NumericalUnresolved = 10,
    InvariantViolation = 11,
    InternalFault = 12
}

public sealed record ExactCost(
    int BinaryExponent,
    System.Numerics.BigInteger IntegerValue,
    double DisplayApproximation,
    bool DisplayRounded,
    bool DisplayOverflow);

public sealed record AssignmentAlternative(
    IReadOnlyList<AssignmentMatch> Matches,
    ExactCost TotalCost,
    ExactCost DeltaFromPrimary,
    AssignmentEvidenceKey ExcludedPrimaryEvidence);

public sealed record BudgetUsage(
    long Vertices,
    long Edges,
    long Relaxations,
    int AlternativeChecks,
    long PeakMemoryBytes,
    TimeSpan Elapsed,
    TimeSpan Drain);

public sealed record AssignmentDiagnostic(
    string Code,
    string MessageKey,
    string? ComponentId = null,
    string? EdgeEvidence = null,
    IReadOnlyDictionary<string, string>? Data = null);

public sealed record AssignmentProgress(
    AssignmentRequestId RequestId,
    int CompletedComponents,
    int TotalComponentsKnown,
    long Relaxations,
    int AlternativeChecks,
    ProofState CurrentProof,
    bool WorkTotalKnown);

public enum AssignmentEventKind
{
    RequestAccepted = 0,
    ValidationCompleted = 1,
    ComponentStarted = 2,
    MainSolutionProved = 3,
    AlternativeCheckStarted = 4,
    AlternativeWitnessFound = 5,
    ComponentCompleted = 6,
    AlternativesCompleted = 7,
    LogicalCompleted = 8,
    StopRequested = 9,
    DrainStarted = 10,
    Drained = 11,
    ResourcesReleased = 12,
    RequestCompleted = 13,
    RequestStopped = 14
}

public sealed record AssignmentEvent(
    AssignmentEventKind Kind,
    AssignmentRequestId RequestId,
    AssignmentInputRevision InputRevision,
    long Sequence,
    DateTimeOffset TimestampUtc,
    string? ComponentId,
    ProofState Proof,
    TerminationReason? Termination,
    BudgetUsage Usage,
    string AlgorithmRevision,
    string ContractRevision);

public interface IAssignmentEventSink
{
    void OnEvent(AssignmentEvent value);
}

public static class AssignmentSolver
{
    public static IAssignmentSolver Create(IAssignmentCandidateBackend? candidateBackend = null);
}

public sealed record AssignmentBackendRequest(
    AssignmentRequest Snapshot,
    TimeSpan RemainingTime,
    long RemainingRelaxations,
    long RemainingMemoryBytes);

public enum AssignmentBackendOutcome { Unsupported = 0, Candidate = 1 }

public sealed record AssignmentBackendReply(
    AssignmentBackendOutcome Outcome,
    IReadOnlyList<AssignmentMatch> Matches,
    long Relaxations,
    long PeakMemoryBytes,
    string BackendRevision);

public interface IAssignmentCandidateBackend
{
    AssignmentBackendReply Propose(
        AssignmentBackendRequest request,
        CancellationToken cancellationToken);
}
```

`ExactCost` 的数学语义、各状态正交关系、事件顺序和错误分类仍按正文 §5 冻结；重复代码摘录仅是签名索引，若未来变更必须与 §3、§5 同一修改中保持完全一致。`SolveAsync` 为 CPU 密集协作式异步入口，取消必须通过参数提供；同步 `Solve` 只允许调用方明确指定的非 UI 工作线程。

公开构造只通过 §7.3/本附录的 AssignmentSolver.Create，显式可选依赖仅为 IAssignmentCandidateBackend；时钟/测试闸门是内部实现，不向宿主增加未定义constructor/服务接口。事件/进度由每次调用提供；Core不依赖产品Store、UI或其它模块实现。职责Owner如下：

| Owner | 唯一责任 |
|---|---|
| 调用方/消费者 Adapter | 建图、候选完整性、物理去重、键/证据/费用构造和业务解释；保证入口复制期间集合稳定 |
| Assignment Core | 输入快照复制及校验、求解和图内证明、请求运行状态、Core 自有工作区生命周期 |
| 宿主持久化 Owner | 输入/结果快照和耐久回执；Core 不写 Store |
| 上游视觉/native Adapter Owner | HALCON/native 句柄、租约及其取消后的排空；此排空不进入 Core 终态 |
| 注入候选后端 Adapter Owner | 本次Propose资源和真实停止/排空；未退出时阻止Core发Drained；实例生命周期归宿主 |
| UI | 只读投影，不拥有求解状态或生产判定 |
| 第二消费者 | 自有独立适配器、键/证据/费用、输入修订、结果存储和业务事实 |
| Contract Owner | 平台 Schema、状态及错误映射；Core 不自行写入平台 Contract |

结果只能声明图内证明；调用方拥有完整性解释及任何业务决定。

Core 合同版本为 `0.1`，`ContractRevision` 必须严格匹配实现支持版本；不兼容值返回 `InvalidInput`/稳定诊断，不静默降级。类型约束与预算边界以 §3、结果状态以 §5 为唯一详述，算法修订须独立记录。


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

- 准入路径：`NewProjectRequired`。预定 Core 工程：`src/Modules/assignment/Asun.Modules.Assignment.Core/Asun.Modules.Assignment.Core.csproj`；namespace：`Asun.Modules.Assignment`。预定测试工程：`tests/Modules/assignment/Asun.Modules.Assignment.Core.Tests/Asun.Modules.Assignment.Core.Tests.csproj`。上述项目尚未创建。
- 后续实现允许变更范围：仅上述Core和测试工程目录；契约/事件/端口放Core公开目录，算法和账本为internal；Tests namespace固定Asun.Modules.Assignment.Core.Tests，包含oracle/反例/双Consumer Fixture、后端假实现及Benchmark。目标net10.0、仅BCL运行依赖，不另造Abstractions/Host/Simulator工程。测试工程固定net10.0、BCL、OutputType=Exe harness，执行命令/退出码/用例ID/有限截止点按§12；不引入待选测试框架或runner，不依靠机器全局NuGet或产品依赖。
- 禁止范围：其它独立模块的 `src/Modules/*`、`tests/Modules/*`，产品 Shell/Domain/Integration 项目、`asunimage/` 内部、只读参考快照和 `docs/references/` 原件。Core 通过本模块指导定义的端口依赖，不直接引用产品类型、AsunImage 或其它模块实现。
- 后续获准的实现任务应把创建 Core 与测试工程作为首个提交切片；创建前须确认权威代码仓库/分支。此文档修订不创建工程。
- 本轮文档任务只允许写本模块唯一DEVELOPMENT-GUIDE.md；上述src/tests路径仅为后续获准实现绑定，不是本轮写入授权。
- 当前状态：C1～C4为 `ModuleCoreImplementationReady`（规格准备）；DEV-GOV-010 §3.1六项文档规格已于2026-10-09由主控接收。产品编码仍需单独授权；本绑定不是实际编译、独立数值/性能、产品集成或现场资格通过声明。

