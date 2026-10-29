# AI 数据集与模型治理独立模块开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C1, C2`

- 模块键：`ai-dataset-governance`
- 中文名称：AI 数据集与模型治理
- 独立模块编号：`IM-048`
- 来源指导：`PKG-053`
- 版本：`0.2.7-prep`
- 状态：`DesignReview/Prep`
- 限定接收：主控已接收0.2.4-prep A1-Qualification Golden/Benchmark执行与Recorded桥指导及model-assets Service0.3受影响原回执映射核对；C1/C2/S6桥/U1原接收保持。整Adapter、真实后端、报告耐久和客户资格不在本次接收范围；S7及qualification 0.2.5-prep Deming桥已主控限定接收；本模块无当前Deming消费者，复用边界见§13.1.7，本轮适用性说明已限定接收。
- 规划消费者：缺陷外观模型、OCR 模型、其它视觉项目的训练、评估、发布和回退工具
- 本文 Owner：模块 Owner（数据集、标签、评估和用途阶段事实）
- 工程准入：`NewProjectRequired`；未发现契约完全匹配的 AI Dataset Governance Core。实现切片开始时创建 `src/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Core/`，测试放在 `tests/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Core.Tests/`，namespace 为 `Asun.Modules.AiDatasetGovernance`。

## Core implementation binding

- 上述工程路径是本模块唯一 Core 写入位置；仅在实现切片获准启动时创建。数据/标签/资产/权限适配器和可选 WPF 投影不进入 Core。

本文是本目录内唯一的模块实施指导。它定义一个可以脱离本检测平台接入其它视觉项目的核心类库、适配器和可选 WPF 投影。本文不声明代码已实现、契约已批准、模型已取得资格或已通过生产验收。

整模块文档准备结论见§18（2026-10-12），本轮只窄消费qualification 0.2.6-prep的完整报告归档/存储公开契约（§13.1.8）。原接收范围、完整范围结论和有效研究/自审保留；原qualification报告codec软件契约欠项已关闭，实际部署绑定、耐久恢复与产品资格仍分别验证。不再等待总控内容审核，不用Core接收代替整模块结论。

## 1. 权威、职责、范围和禁止边界

### 1.1 读取顺序

实施前按以下顺序读取，并在实现任务中记录实际采用的版本：

1. 平台架构和 `INDEPENDENT-MODULE-ARCHITECTURE.md`；
2. `PKG-053_AiGovernance.md`；
3. `DEV-AI-060`（AI 生命周期、训练、部署、回退）；
4. `DEV-AI-063`（数据、GroundTruth、分组、统计分母）；
5. `PKG-033`（模型资产字节及精确闭包）和 `PKG-052`（推理执行）；
6. 已批准的 Contract/Schema、State/Owner、Authorization 和 PageContract；
7. 本文的实施步骤、测试和性能章节。

若本文与已批准 Contract/Schema、State/Owner 或未来批准架构冲突，停止受影响切片，登记冲突并以高层权威为准。§3—§5 是模块自身 Module API Contract v0.2，与候选产品 Schema 分开。产品映射未经采纳，不得在产品私表落地。v0.2 取代未实现的 v0.1 草案，不维持第二份活动 API。

### 1.2 模块负责的事实

模块只负责以下事实及其不可变修订：

- 受权限控制的数据来源引用、物理同源分组和数据快照；
- 标签候选、参照方法、仲裁引用、标签版本及适用范围；
- 训练/评估请求、固定的输入闭包、运行回执、分层事件和统计报告；
- `Offline -> Replay -> Shadow -> Advice -> Automatic` 阶段的资格证据包和漂移观察；阶段采用/撤回决定由外部授权/资格 Owner 签发，本模块只校验、关联并投影其只读回执；
- 操作状态、错误、取消、超时和未知回执。

模型文件、外部权重和特征 bank 的字节归 `PKG-033/041`；模型执行归 `PKG-052/024`；复判意见归 `PKG-044`；实验/计量资格归 `PKG-055`；最终质量判定、目标关联、工艺解释、质量放行和设备命令归调用应用。

### 1.3 明确禁止

核心类库不得：

- 写入或改写 `MeasurementSet`、`InspectionFact`、`MachineDecision`、质量放行、程序配方或设备命令；
- 依据模型输出自动生成“合格”、缺陷责任、客户处置或工艺阈值；
- 把 UI 文本、页面 ViewModel、产品私表、全局 ServiceLocator、机台 SDK 句柄带入公开契约；
- 通过扫描任意目录/生产私表自动训练，或默认上传用户数据到第三方服务；
- 复制 `DEV-AI-060/063`、`PKG-033/052/044/055` 的第二套状态、标签、资产或推理事实；
- 把同名 `latest`、磁盘上任意旧模型或“冠军”别名当作可部署版本；
- 以取消、回退或新标签静默改写已经发布的历史报告；
- 将未知、拒识、缺分母、超时、资源耗尽或执行未知转成 PASS/正常。

本模块不包含任何 PCB、PCBA、SPI、AOI、点胶、涂覆或其它制程判定。调用方提供对象关联和工艺语义，模块只保存可追溯的治理结果。

## 1B. 新架构适配要点

本模块的 L1-L4 训练闭环已在 §7.4 展开，本节补充面向新平台架构的适配约束。

**架构门禁**：`Asun.Modules.AiDatasetGovernance.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§9 已明确"两个自足无 UI Host"，Core 在无 WPF 宿主中完整运行。

**Blazor/Web**：数据集目录、标签分布、划分统计和 L1-L4 闭环进度通过 gRPC/REST 查询；数据集样本图像通过 HTTP Range 分片加载。**训练执行在服务端**（§9 的无 UI Host），浏览器不参与训练、不上传本地文件到训练环境。人工标注 Web 前端是本模块的合法消费形态之一，但标注决策经授权 gRPC 接口提交并绑定 principal 令牌。

**AI 推理 Tiling**：本模块是推理侧的数据与评估治理方，约束：
- 本模块从 `ai-inference` 获取仲裁证据（`ArbitrationEvidence`）用于评估与漂移分析，不调用推理执行路径
- L1 参数搜索调用 `imaging-optimization`；L2 监督信号来自 `parameter-editor` 的 `ParameterModificationEvent`；L3 漂移监控借助 `statistics`；L4 资格确认由 `qualification` 承接——**四层各有明确下游 Owner，本模块不越界执行**
- 本模块不持有推理 tile 租约，不参与分块编排

**HALCON 双跑**：本模块的评估基线若引用 HALCON 路线的检测结果，该引用经 `inspection-evidence` 的证据引用进入，不在 Core 内调用 HALCON 算子；HALCON 备选 CI 在产出证据的视觉模块中执行。

## 2. 交付形态和依赖方向

发布以下相互分离的单元：

```text
AiDatasetGovernance.Core       无 UI 的契约、校验、编排、状态和统计门禁
AiDatasetGovernance.Adapters   文件/对象存储、原证据、标签、资产、授权和时钟适配器
AiDatasetGovernance.Wpf        可选的 DevExpress/WPF 参数与状态投影
```

`Core` 只依赖 .NET 基础库和已批准公共契约；AsunImage、HALCON、DevExpress、数据库、对象存储、模型运行时均通过端口注入。独立模块不要求独立进程，但实例不得共享可变静态状态。消费者引用方向为“宿主 -> Core -> Adapter”，禁止 Adapter 反向引用宿主 ViewModel。

### 2.1 视觉算法路线核对

本模块的主要工作是数据身份、标签、划分、统计和用途治理，不执行图像算法，因此多数路径不适用 HALCON。涉及区域标签坐标、裁剪回映或几何匹配时，语义和参数以项目 HALCON 26.05 `halcon算子手册/operators` 为准，优先复用已批准的坐标/ROI 模块；需要算子调用时统一经 `ImageLibDotNet.cv2`，不另接 `HOperatorSet` 或 `halcondotnet.dll`，不重复核验封装是否包含算子。只有 C# 参数类型、重载或封送确有歧义时才查公共签名或由消费项目编译确认，不检查内部。匹配失败、坐标版本缺失或有效域不明确必须返回 `Unsupported`/`InvalidInput`，不能自行引入一个“等价”几何实现。

### 2.2 已核对的算法适配路线（不属于首片 Core）

首片 Core 不引用 HALCON/AsunImage，不读取图像，也不训练或执行模型。需要图像证据的工作进入可替换 Adapter/Integration slice，按以下已核对路线实现：

| 用途 | HALCON 26.05 算子路线（由适配器经 `ImageLibDotNet.cv2` 调用） | 备用/恢复 | 明确不支持 |
|---|---|---|---|
| 标签坐标回映 | `affine_trans_point_2d`、`affine_trans_region`、`intersection`、`count_obj`、`area_center` | 坐标版本或有效域不匹配时保留原标签并返回 `DG-002`/`DG-013`；不得自行改坐标 | 没有原图尺寸、面、变换链或有效域时不推断坐标 |
| 有监督训练 | `train_dl_model_batch` | 训练失败保留不可变输入闭包；从最近**已验证且独立保存**的资产重新开新 operation。未冻结 checkpoint 语义时不宣称 exact resume | Core 不创建训练器、不选择 best、不把训练结果直接变成资格 |
| 异常训练 | `train_dl_model_anomaly_dataset` | 缺少合格正常库、污染或资源不足返回 `DG-007`/`DG-008`，转人工或经典基线评估 | 不把正常库自动当生产真值，不把异常分数当概率 |
| 评估执行 | `apply_dl_model` | 结果结构、模型闭包或后处理不匹配返回 `DG-013`；保留已完成项和未评价项，不补零 | Core 不直接调用模型、不管理 GPU/批次、不写生产事实 |
| 模型资产交接 | `read_dl_model`/`write_dl_model` | hash/长度/依赖闭包不一致隔离为 `DG-005`；不能从任意旧路径加载 | 读写成功不等模型资格、部署通过或可回退 |

上述算子路线复用前轮对本仓库 HALCON Operator Reference `26.05.0.0` 的核对结果；本次来源吸收未新增视觉方法，H:\docs 的 24.11 内容不作为 API 或算法依据。训练随机性、GPU、native 取消和 checkpoint 语义仍需在对应 Adapter 的目标版本资料和实测中冻结；缺证据时保持 `Unsupported`/`Unknown`。

## 3. Module API Contract v0.2：值、输入与身份

本节是唯一当前模块契约，namespace `Asun.Modules.AiDatasetGovernance`，`net10.0`，仅 BCL。以下 C# 为公开声明规格，方法体由实现切片完成；不是已经存在的程序集。除特别说明外，所有位置 record 都是**不可信输入载体**，允许表达非法值，构造器不做领域校验。不能将 `IReadOnlyList`、record 或 `with` 称为不可变快照。工厂便利入口仅对 null 引用抛 `ArgumentNullException`；校验入口接受 nullable 输入并返回错误，不把验证错误转成构造异常。所有正文 API 以本节声明为准，不另保留旧附录签名。

### 3.1 预算、枚举和基础类型

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Threading;
using System.Threading.Tasks;

public readonly record struct ContentHash(string Value);
public sealed record Issue(string Code, string Path, string ResourceKey);
public sealed record Check<T>(T? Value, ImmutableArray<Issue> Issues) where T : class;
public enum TaskKind { Defect = 1, Ocr = 2, Classification = 3,
    Detection = 4, Segmentation = 5, Anomaly = 6 }
public enum Partition { Train = 1, Validation = 2, Test = 3, Challenge = 4 }
public enum Origin { Acquired = 1, Synthetic = 2, Injected = 3 }
public enum TruthStatus { Approved = 1, Missing = 2, Disputed = 3,
    Unobservable = 4, Invalid = 5 }
public enum PredictionStatus { Completed = 1, Abstained = 2, NotExecuted = 3,
    Failed = 4, TimedOut = 5, Invalid = 6 }
public enum OperationState { Accepted = 1, Validating = 2, Running = 3,
    Completing = 4, Draining = 5, DrainUnknown = 6, Drained = 7,
    ResourcesReleased = 8, Succeeded = 9, Rejected = 10,
    Cancelled = 11, Failed = 12, Unknown = 13 }
public enum Stage { Offline = 1, Replay = 2, Shadow = 3, Advice = 4, Automatic = 5 }
public enum IntervalKind { NotRequested = 1, GroupBootstrap = 2, OwnerMethod = 3 }
public sealed record Budget(int MaxItems, int MaxTextUtf8Bytes,
    long MaxCanonicalBytes, long MaxWorkingBytes, long MaxDpCells,
    int MaxParallelism, int WorkTimeoutMs, int CleanupTimeoutMs);
public sealed record RootLimits(int MaxSessions, int MaxOperations,
    long MaxRetainedBytes, int MaxEvents, int MaxPendingPortTasks);
public sealed record RevisionRef(string Id, string Version, ContentHash Hash);
public sealed record SnapshotRef(string Id, string ContractVersion, ContentHash Hash);
public sealed record AuthorizationQuery(string Principal, string Tenant,
    string Purpose, string Scope, string PolicyRevision);
public sealed record AuthorizationReceipt(string ReceiptId, string PolicyRevision,
    ContentHash RequestHash, DateTimeOffset ValidUntilUtc, bool Allowed);
```

所有预算必填，无位置参数对象默认值。测试示例的有限预算不是客户目标。`MaxItems` 为 1..10,000,000；文本 UTF-8 字节、canonical 字节、工作字节、DP 单元均为正且不超过对应 `long/int` 可表示值；并发 1..64；work/cleanup timeout 分别为 1..604800000 ms。整数表示界来自.NET类型；10,000,000项、64并发、7天是本模块接纳协议的防滥用工程硬界，由本轮技术判断冻结，并非实测处理能力、SDK限制或客户容量/节拍目标。实际可接纳量还受root和工作区预算，宿主Profile应更低；扩大这些硬界需新协议及负载/资源验证，不能只调UI数值。RootLimits 各数为正；host 显式选择有限值并记入运行环境。时间必须 UTC offset=0；hash 必须64位小写十六进制，不自动重算未知旧协议身份。不合法预算统一 DG-008，其它字段/编码/格式 DG-001；空版本 DG-001，非空但不支持版本 DG-002。

### 3.2 数据、标签、模型和评价请求

```csharp
public sealed record PixelBounds(int Row, int Column, int Height, int Width);
public sealed record RegionRef(string ObjectId, string ClassId, RevisionRef Region,
    string CoordinateRevision, PixelBounds Bounds);
public sealed record TruthValue(TruthStatus Status, string? ClassId, string? Text,
    IReadOnlyList<RegionRef> Regions, string Reason);
public sealed record LabelObservation(string ObservationId, string MemberId,
    RevisionRef Evidence, string ActorReceiptId, string VisibilityPolicyRevision,
    TruthValue Value);
public sealed record LabelSelection(string MemberId, string SelectedObservationId,
    string ArbitrationReceiptId);
public sealed record LabelSet(RevisionRef Revision, string TaxonomyRevision,
    IReadOnlyList<string> ClassIds,
    string TruthMethodRevision, string ApprovalReceiptId,
    IReadOnlyList<LabelObservation> Observations, IReadOnlyList<LabelSelection> Selections);
public sealed record DataMember(string Id, RevisionRef Evidence, long EvidenceBytes,
    string PhysicalGroupId, string? ParentId, Origin Origin, string Modality,
    string CoordinateRevision, IReadOnlyList<string> Strata);
public sealed record GroupAssignment(string PhysicalGroupId, Partition Partition);
public sealed record SplitSpec(string MethodRevision, uint Seed,
    IReadOnlyList<GroupAssignment> Assignments, IReadOnlyList<string> HoldoutRules);
public sealed record SnapshotDraft(string Id, string ContractVersion, string Purpose,
    IReadOnlyList<DataMember> Members, LabelSet Labels, SplitSpec Split);
public sealed record ModelBinding(TaskKind Task, SnapshotRef Snapshot,
    string ModelAssetRef, string PredictionRevision, string PreprocessRevision,
    string PostprocessRevision, string TaxonomyRevision, string ThresholdRevision,
    string BackendRevision);
public sealed record EvaluationPlan(string Revision, TaskKind Task,
    SnapshotRef Snapshot, RevisionRef Labels, string MethodRevision,
    Partition Partition, IReadOnlyList<string> Endpoints,
    IntervalKind Interval, int ConfidencePpm, string IntervalMethodRevision,
    int Resamples, uint Seed, int MinIndependentGroups,
    RegionMatchingPolicy? RegionMatching);
public sealed record RegionMatchingPolicy(string Revision, int MinimumIouPpm,
    int MaxTruthObjects, int MaxPredictionObjects, int MaxCandidatePairs,
    RevisionRef ValidDomain);
public sealed record EvaluationRequest(string OperationId, string IdempotencyKey,
    AuthorizationQuery Authorization, FrozenSnapshot Snapshot,
    ModelBinding Model, EvaluationPlan Plan, Budget Budget);
public sealed record SnapshotPublicationRequest(string OperationId, string IdempotencyKey,
    AuthorizationQuery Authorization, FrozenSnapshot Snapshot, Budget Budget);
public enum TrainingMode { SupervisedBatch = 1, AnomalyDataset = 2, GcAnomalyBatch = 3 }
public sealed record TrainingSpec(string Revision, TaskKind Task, TrainingMode Mode,
    RevisionRef Toolchain, RevisionRef Configuration, uint Seed, int Epochs,
    int BatchSize, int BatchMultiplier, string CheckpointPolicyRevision);
public sealed record TrainingRequest(string OperationId, string IdempotencyKey,
    AuthorizationQuery Authorization, FrozenSnapshot Snapshot,
    TrainingSpec Spec, Budget Budget);
public sealed record UsageIntent(string OperationId, string IdempotencyKey,
    AuthorizationQuery Authorization, Stage Stage, ModelBinding Model,
    IReadOnlyList<RevisionRef> Reports, RevisionRef OwnerDecision,
    string ApplicabilityRevision, bool Rollback, Budget Budget);
```

`EvaluationPlan.Snapshot` 保留 ID、ContractVersion 和 hash，必须与 `ModelBinding.Snapshot` 及 `FrozenSnapshot.Reference` 精确相等。计划标签引用也精确比较；不得把 `SnapshotId` 当完整身份。模块版本只接受 `ContractVersion="0.2"`；证据和标签 `RevisionRef.Version` 是各 Owner 的协议版本，非空即可通过结构校验，实际受支持性由对应端口确认，不能一律要求也等于0.2。模型引用固定 `asset://sha256/<64位小写hash>`；这是模块接入引用，不替代 IM-014 model-assets 原始 JCS 身份规则。不能接纳 latest/champion/路径/别名。

label observation 与 selection 分开：同一成员可有多次观察，只能有一个选定观察；选定关系必须存在且同成员，审批和仲裁回执不能为空。`Approved` 不靠调用者字符串自证，真实执行由授权/事实端口验证；缺失/争议/不可观察可发布为带缺口研究快照，不会补成正常。训练必须有 Train/Validation 义务；评价只读指定 Test 或 Challenge。真实、合成和注入分层不能混作现场结论。

### 3.3 输出、冻结与资源预检

LabelSet.ClassIds为ordinal排序的唯一非空ID数组；Defect/Anomaly二元方法必须精确negative/positive，Classification/Detection/Segmentation非空，OCR允许空。所有Approved真值class、Completed预测class必须在该类表，否则DG-013；不能借输入少了某类缩小taxonomy。Snapshot canonical中ClassIds按ordinal入码，改变类表产生新hash。Model.TaxonomyRevision须等于快照LabelSet.TaxonomyRevision，Plan.MethodRevision必须与TaskKind及endpoints支持集一致，结构Freeze即可判断此类匹配，无需等待Facts。Facts另外验证该方法对实际模态/参照/适用域成立，Evaluation的ClosureCheck必须带Model/Plan且Training=null；Training必须带TrainingSpec且Model/Plan=null，配置/toolchain/seed/mode由完整spec传入，不靠端口全局上下文。

`FrozenSnapshot`、`FrozenEvaluation`、`FrozenTraining`、`FrozenUsage`、`FrozenPublication` 为 sealed class、internal 构造器和下列只读 get 属性，没有公共 init、set、with 或底层可写集合；所有递归集合均为 `ImmutableArray<T>`，叶节点只含 scalar/string/只读值对象。公开输入 record 绝不直接暴露为冻结输出；实现内部 frozen DTO 不增加另一条公开构造路径。

| 类型 | 公开只读属性 |
|---|---|
| `FrozenSnapshot` | `SnapshotRef Reference`、`int MemberCount`、`int GroupCount`、`RevisionRef LabelRevision`、`ContentHash ContentHash`、`ImmutableArray<string> ClassIds` |
| `FrozenEvaluation` | `string OperationId`、`ContentHash RequestHash`、`SnapshotRef Snapshot`、`Budget Budget` |
| `FrozenTraining` | `string OperationId`、`ContentHash RequestHash`、`SnapshotRef Snapshot`、`Budget Budget` |
| `FrozenUsage` | `string OperationId`、`ContentHash RequestHash`、`Budget Budget` |
| `FrozenPublication` | `string OperationId`、`ContentHash RequestHash`、`FrozenSnapshot Dataset`、`Budget Budget` |

为使外部执行端口实际读取输入，冻结对象另外提供以下**有界独立输出**，不是访问私有夹具或保留原draft：

```csharp
public sealed record FrozenTruth(TruthStatus Status, string? ClassId, string? Text,
    ImmutableArray<RegionRef> Regions, string Reason);
public sealed record FrozenMember(string Id, RevisionRef Evidence, long EvidenceBytes,
    string PhysicalGroupId, Origin Origin, string Modality, string CoordinateRevision,
    ImmutableArray<string> Strata, Partition Partition, FrozenTruth Truth);
```

| 合并到类型的公开成员（不是第二种类型定义） | 签名 |
|---|---|
| FrozenSnapshot | `ImmutableArray<FrozenMember> CopyMembers(Partition partition);` |
| FrozenSnapshot | `SnapshotDraft CopyDraft();`（仅完整视图；训练视图拒绝，返回全部历史观察与selection的独立只读副本） |
| FrozenEvaluation | `FrozenSnapshot Dataset { get; }`、`ModelBinding CopyModel();`、`EvaluationPlan CopyPlan();` |
| FrozenTraining | `FrozenSnapshot Dataset { get; }`、`TrainingSpec CopySpec();` |
| FrozenUsage | `UsageIntent CopyIntent();` |
| FrozenPublication | `SnapshotPublicationRequest CopyRequest();` |

Copy成员只返回独立副本（或不可变叶项组成的ImmutableArray），内部不保留返回的record；输出额计入Budget/Root。FrozenTraining.Dataset公开引用为训练视图，CopyMembers仅允许Train/Validation，访问Test/Challenge抛InvalidOperationException；原始完整FrozenSnapshot并不交给训练端口。CopyPlan/CopyIntent的列表为独立只读副本，调用者with换字段不能影响原请求。FrozenMember无源路径/SDK句柄；生产训练adapter凭Evidence在用途授权下读精确字节，不能扫任意目录。

`Budget` 仅值字段，可作为冻结输出；复制一份，不保留输入对象。Snapshot 内部保存完整冻结成员、真值及 split，但不泄露可写引用。需要展示时通过 §8 的已授权投影读取。

```csharp
public sealed class CoreValidator {
    public Check<FrozenSnapshot> Freeze(SnapshotDraft? draft, Budget? budget);
    public Check<FrozenEvaluation> Freeze(EvaluationRequest? request);
    public Check<FrozenTraining> Freeze(TrainingRequest? request);
    public Check<FrozenUsage> Freeze(UsageIntent? request);
    public Check<FrozenPublication> Freeze(SnapshotPublicationRequest? request);
}
public static class GovernanceFactory {
    public static CoreValidator CreateCoreValidator();
    public static ContentHash HashContent(ReadOnlyMemory<byte> bytes, long maxBytes);
    public static byte[] EncodeBinding(ModelBinding binding, long maxBytes);
    public static ContentHash HashBinding(ModelBinding binding, long maxBytes);
    public static ContentHash HashRegionQuery(RegionPairQuery query, long maxBytes);
}
```

`HashContent` 只计算已显式提供的字节，不读取文件；先比较 Length 与 maxBytes。`EncodeBinding` 返回独立 byte[]，调用者可改自己的副本，不影响模块；超限/非法入参这些低层便利方法抛 `ArgumentException`，高层 Freeze 捕获映射为 Issues。工厂不查询权限、不解析真实资产；Freeze 只证明结构闭包一致，绝不证明存在、授权或标签方法的物理适用性。无共享可变静态状态；并发调用独立。

**先门后复制/hash**：①读标量预算和集合 Count（O(1)）；②checked 求所有集合项上限、文本 `.Length*3` UTF-8保守界、编码尺寸、DP cell、预计内部副本/索引/结果工作区；③根槽和本调用内存配额预留；④有界逐项验证，严格 UTF-16解码并计实际UTF-8，超限停止；⑤只复制接纳范围到模块所有的数组/字符串引用（string不可变），递归复制集合；⑥对内部副本做排序/引用/谱系/hash校验；⑦才产生 Frozen 值。静态 Freeze 使用本次 budget 的局部额度，session 还必须有 root 额度。不能先 `ToArray`、序列化或 hash 任意超大输入再限额。字符串 Length保守界拒绝不意味着可静默截断；调用者可用更合适预算重试。

输入仅接受有限、稳定、索引访问无副作用的 BCL array/List/ImmutableArray，拒绝任意延迟 enumerable/自定义列表或字典；无需接受可执行任意代码的 collection。调用者从预检开始至 Freeze 返回必须保持输入及所有递归集合不变；不支持并发修改。捕获 Count/index变化返回 DG-001，但不能声称检测了所有竞态。Freeze 返回后修改原数组不影响 frozen hash、执行或输出。资源核算使用 checked；上溢 DG-008，不尝试异常大分配，不以 OOM 为常规限额器。所有 Issues 按 Path ordinal、Code ordinal 排序并去重，Message 由资源键投影，不参与逻辑。

工程配额计算固定为协议保守账本，不声称CLR精确对象大小：MaxItems约束**递归记录总数**（members/observations/selections/assignments/regions/endpoints/strata项等），不能只数顶层members；MaxTextUtf8Bytes约束全部文本实际UTF8合计。输入冻结额度先以`256×recordCount + 16×collectionElements + 2×sumUtf16Length + 2×canonicalUpperBound` checked保守预留；运行另预留DP矩阵/回溯、匹配残量图、事件/结果副本和端口任务账本，允许Profile加更高安全系数，不能降低协议核算值。预算账本不等于进程工作集，真实峰值沿Benchmark记录。列表Count总数超限时不访问其中字符串、不hash；有界遍历文本Length仍在深复制之前。低层HashContent/EncodeBinding便利函数只检查其明确maxBytes，生产组合还须先在root预留后调用；测试的独立Golden也显式有限。

截止执行用单调`Stopwatch.GetTimestamp/GetElapsedTime`，注入IUtcClock只用于UTC授权/回执时点，不把固定测试UTC当无限业务deadline。timeout变化影响请求身份，cleanup/后续Lookup的独立观察预算不重算原业务请求hash。每个恢复Lookup接受原requestHash、当前AuthorizationQuery和新Budget；读权拒绝不能伪造原operation失败，返回本次查询错误且保留原事实。

## 4. Module API Contract v0.2：执行端口、回执与根 Owner

### 4.1 端口完整形状

端口只交换模块 DTO，宿主 Adapter 映射真实公共模块；不冒称下列签名就是其它模块已发布签名。所有 Task 是实际工作的**原 Task**，适配器不得用已取消/已超时包装 Task 遮蔽仍在运行的原工作。端口输入均为模块持有的冻结副本或只读标量，端口不得修改；输出按预算重新验收并复制。`CancellationToken` 仅是停止请求。

```csharp
public sealed record AccessCheck(AuthorizationQuery Query, ContentHash RequestHash,
    string OperationId, bool BeforeCommit);
public interface IAuthorizationPort {
    Task<AuthorizationReceipt> CheckAsync(AccessCheck check, CancellationToken token);
}
public interface IUtcClock { DateTimeOffset UtcNow { get; } }
public sealed record ClosureCheck(string OperationId, SnapshotRef Snapshot,
    FrozenSnapshot Dataset,
    RevisionRef Labels, ModelBinding? Model, EvaluationPlan? Plan,
    TrainingSpec? Training, bool Publication);
public sealed record ClosureReceipt(ContentHash RequestHash, bool Available,
    bool IntegrityVerified, bool LabelsApproved, bool MethodApplicable,
    bool Withdrawn, string ReceiptId);
public interface IFactPort {
    Task<ClosureReceipt> VerifyAsync(ClosureCheck check, ContentHash requestHash,
        CancellationToken token);
}
public sealed record Prediction(string MemberId, PredictionStatus Status,
    string? ClassId, string? Text, IReadOnlyList<RegionRef> Regions,
    bool AutomaticallyAccepted, string MethodRevision, string Reason);
public sealed record PredictionBatch(SnapshotRef Snapshot, ContentHash BindingHash,
    IReadOnlyList<Prediction> Items, string ExecutionReceiptId);
public interface IPredictionSource {
    Task<PredictionBatch> ReadAsync(FrozenEvaluation request, CancellationToken token);
}
public sealed record RegionPairQuery(string MemberId, ImmutableArray<RegionRef> Truth,
    ImmutableArray<RegionRef> Prediction, RevisionRef ValidDomain,
    string CoordinateRevision, string MethodRevision);
public sealed record RegionMeasure(long TruthPixels, long PredictionPixels,
    long IntersectionPixels, long ValidPixels, string CoordinateRevision,
    RevisionRef ValidDomain, ContentHash QueryHash, RevisionRef Evidence);
public interface IRegionMeasurePort {
    Task<RegionMeasure> MeasureAsync(RegionPairQuery query, CancellationToken token);
}
public sealed record TrainingProduct(string OperationId, SnapshotRef Snapshot,
    RevisionRef Configuration, RevisionRef Toolchain, string CandidateModelAssetRef,
    RevisionRef RunEvidence, bool NativeStopped, string ExecutionReceiptId);
public interface ITrainingPort {
    Task<TrainingProduct> TrainAsync(FrozenTraining request, CancellationToken token);
}
public sealed record Endpoint(string Name, string Stratum, long Numerator,
    long Denominator, double? Value, string Unit, string Reason);
public sealed record GroupStatistic(string GroupId, string EndpointName,
    long Numerator, long Denominator, long Obligations, long MissingTruth,
    long Abstained, long Incomplete);
public sealed record IntervalQuery(string MethodRevision, IntervalKind Kind,
    int ConfidencePpm, int Resamples, uint Seed, int MinIndependentGroups,
    IReadOnlyList<GroupStatistic> Groups, Budget Budget);
public sealed record IntervalResult(string EndpointName, double? Lower,
    double? Upper, int IndependentGroups, string MethodRevision, string Reason);
public interface IStatisticsPort {
    Task<IReadOnlyList<IntervalResult>> ComputeAsync(IntervalQuery query,
        CancellationToken token);
}
public sealed record CoverageCell(TruthStatus Truth, PredictionStatus Prediction,
    bool AutomaticallyAccepted, Origin Origin, long Count);
public sealed record EvaluationEvent(string MemberId, Origin Origin,
    TruthStatus TruthStatus, PredictionStatus PredictionStatus,
    bool AutomaticallyAccepted, string? TruthClass, string? PredictionClass,
    string? TruthText, string? PredictionText, long MatchedObjects,
    long MissedObjects, long ExtraObjects, long Substitutions, long Deletions,
    long Insertions, long TruthScalars, string Reason);
public sealed record EvaluationResult(SnapshotRef Snapshot, ContentHash BindingHash,
    RevisionRef Labels, string PlanRevision, ImmutableArray<Endpoint> Endpoints,
    ImmutableArray<CoverageCell> Coverage, ImmutableArray<IntervalResult> Intervals,
    ImmutableArray<EvaluationEvent> Events, ImmutableArray<string> Gaps,
    bool QualificationGranted);
public sealed record UsageProjection(Stage Stage, string ModelAssetRef,
    RevisionRef OwnerDecision, bool IsActive, bool Rollback, string Reason);
public sealed record SnapshotPublicationResult(SnapshotRef Snapshot, RevisionRef Labels,
    int Members, int Groups, ImmutableArray<string> Gaps);
public interface IUsageDecisionPort {
    Task<UsageProjection> ReadAsync(FrozenUsage request, CancellationToken token);
}
public sealed record CommitCommand(string OperationId, string IdempotencyKey,
    AuthorizationQuery Query,
    ContentHash RequestHash, AuthorizationReceipt Authorization,
    FrozenSnapshot? Dataset,
    EvaluationResult? Evaluation, TrainingProduct? Training, UsageProjection? Usage,
    SnapshotPublicationResult? Publication);
public enum CommitStatus { Confirmed = 1, NotCommitted = 2, Unknown = 3, Conflict = 4 }
public sealed record CommitReceipt(string OperationId, ContentHash RequestHash,
    CommitStatus Status, string? ResultId, string ReceiptId);
public interface IReportStore {
    Task<CommitReceipt> CommitAsync(CommitCommand command, CancellationToken token);
    Task<CommitReceipt> LookupAsync(string operationId, ContentHash originalRequestHash,
        AuthorizationQuery query, CancellationToken token);
}
public sealed record ReleaseReceipt(string OperationId, bool Stopped,
    bool AllLeasesReturned, string ReceiptId);
public interface IExecutionLifetimePort {
    Task<ReleaseReceipt> StopAndReleaseAsync(string operationId, CancellationToken token);
}
public sealed record GovernancePorts(IAuthorizationPort Authorization, IFactPort Facts,
    IPredictionSource Predictions, ITrainingPort Training, IReportStore Store,
    IExecutionLifetimePort Lifetime, IStatisticsPort? Statistics,
    IRegionMeasurePort? Regions, IUsageDecisionPort? Usage, IUtcClock Clock);
```

未启用的训练/预测能力也不能填 null；可注入显式返回不支持的 Adapter。统计/区域/用途仅在计划实际要求时必须非 null，不允许隐式降级。`ClosureReceipt` 不只是自报 ID：生产 Adapter 通过数据/标签/资产/资格公开契约核验精确内容与方法，返回来自原 Owner 的回执，批准签名/期限/撤销协议沿原 Owner；本模块不创信任根。`BeforeCommit` 第二次权限读取也不证明跨服务原子性：Store 必须在原子提交边界核验授权回执/策略 epoch，不能做到时返回 NotCommitted，不启用真实写切片。

`IReportStore` 是本模块报告/治理回执持久化端口，底层技术事务由 storage-database，业务事实由本模块持有；不复制模型/复判/生产/资格表。CommitCommand 恰有一个结果非 null；publication/evaluation/training必须带原完整FrozenSnapshot Dataset，Usage为null。Store通过CopyDraft取得全部成员/来源/观察/selection/split，不能仅存SnapshotRef+数量却宣称可重建。已有snapshot ID/version/hash相同复用，异hash拒绝；评价/训练提交前引用快照必须已发布或在同原子事务追加为明确研究快照，不把训练视图当完整原件。Store 在 tenant/principal/operation-kind/idempotency-key作用域原子比较完整 RequestHash，同键同hash返回原精确回执，同键异hash Conflict；同 operation 同hash重复查询不再执行。提交 Unknown 只 Lookup 原 operation，不能换键重写。端口成功返回不等于授权/方法适用：逐字段核对 operation、snapshot、hash和receipt，缺项或不一致拒绝。

### 4.2 运行 API 与原 Task

```csharp
public sealed record GovernanceEvent(string OperationId, long Generation,
    long Sequence, OperationState State, string ResourceKey);
public sealed record Outcome(string OperationId, ContentHash RequestHash,
    OperationState State, string? ErrorCode, string? ResultId,
    EvaluationResult? Evaluation, TrainingProduct? Training, UsageProjection? Usage,
    SnapshotPublicationResult? Publication, bool CommitConfirmed, bool ResourcesReleased);
public sealed class OperationHandle {
    public string OperationId { get; }
    public long Generation { get; }
    public Task<Outcome> Completion { get; }
    public void RequestCancel();
}
public sealed record CleanupResult(bool Released, bool ObservationTimedOut,
    string? ErrorCode, string SlotId);
public sealed record RetentionAck(string RootId, string SlotId, bool Accepted);
public sealed class GovernanceRoot {
    public GovernanceRoot(RootLimits limits);
    public bool TryReserve(long retainedBytes, out RootSlot? slot);
    public Task<CleanupResult> ObserveAllAsync(int timeoutMs);
    public int OutstandingSlots { get; }
}
public sealed class RootSlot {
    public string Id { get; }
    public GovernanceSession Open(GovernancePorts ports);
    public Task<CleanupResult> CloseAsync(int cleanupTimeoutMs);
    public RetentionAck TransferToRoot();
    public Check<BorrowedWork<T>> StartBorrowed<T>(Func<Task<T>> start,
        object borrowedOwner, Func<Task> release, long retainedBytes) where T : class;
    public Check<BorrowedScope> ReserveBorrowedScope(BorrowedScopeLimits limits,
        object borrowedOwner, Action requestStop);
}
public sealed record BorrowedScopeLimits(int WorkSlots, int CleanupSlots,
    int ObservationSlots, int MaxStarts, long RetainedBytes);
public enum BorrowedLane { Work = 1, Cleanup = 2, Observation = 3 }
public sealed record BorrowedScopeResult(string ScopeId, bool ResourcesReleased,
    ImmutableArray<Issue> WorkErrors, ImmutableArray<Issue> CleanupErrors);
public sealed class BorrowedTask<T> {
    public Task<T> Original { get; }
    public Task<T> Received { get; } // 原结果接收门完成；不替代Original退出证明
}
public sealed class BorrowedScope {
    public string Id { get; }
    public Task<BorrowedScopeResult> Completion { get; }
    public Check<BorrowedTask<BorrowedScopeResult>> StartLifetime(
        Func<Task<BorrowedScopeResult>> run);
    public Check<BorrowedTask<T>> Start<T>(BorrowedLane lane, int slot,
        Func<Task<T>> start, Action<T> accept);
    public Check<BorrowedTask<T>> CaptureProduced<T>(int workSlot,
        Task<T> original, Action<T> accept);
    public void RequestStop();
    public RetentionAck TransferToRoot();
}
public sealed class BorrowedWork<T> where T : class {
    public Task<T> Original { get; }
}
public sealed class GovernanceSession {
    public event Action<GovernanceEvent>? Changed;
    public Check<OperationHandle> StartEvaluation(EvaluationRequest? request);
    public Check<OperationHandle> StartTraining(TrainingRequest? request);
    public Check<OperationHandle> RecordUsage(UsageIntent? request);
    public Check<OperationHandle> PublishSnapshot(SnapshotPublicationRequest? request);
    public Task<CommitReceipt> LookupAsync(string operationId, ContentHash originalRequestHash,
        AuthorizationQuery query, Budget budget, CancellationToken waitToken);
    public void RequestClose();
    public Task<GovernanceProjection> ReadProjectionAsync(string operationId,
        AuthorizationQuery query, int maxRows, int maxMetrics, CancellationToken waitToken);
}
```

`Check<T>.Value` 非 null 当且仅当 Issues为空；拒绝没有 handle/operation，也不调用端口。session 的 Start 先预留 operation slot、端口Task预算及 retained bytes，再 Freeze；操作注册到 root，创建 Completion/CTS/原Task持有表后才允许启动端口，不存在先执行后 Track 的窗口。Completion 是该 operation 唯一 Task，重复接纳同operation同hash返回同一 handle；同ID异hash返回 DG-016。运行中的重试只查询，不重启。不同session隔离，root 限制总在途量。Lookup 也计入根在途/端口Task数；waitToken 只取消等待，原查询 Task 留在根内直至结束。没有 `Dispose` 提前释放捷径。

root 是调用进程持有的**实例对象**，不是 static ServiceLocator；必须在任何 Factory/Freeze/端口创建前获得进程根容量。宿主可持一个有界 Root 实例作为本应用服务；不得每次失败新建 root 来绕过额度。RootSlot.Open 只允许一次；Open 抛错/未Open也通过 CloseAsync 归还槽。端口/源资源由宿主借出，slot 强持端口、session、请求副本、原Task、CTS、事件队列及租约；只有真实释放后自动腾出槽。root 无后台无限重试，只登记原Task的完成 continuation 并按一次性状态推进。

`CloseAsync(ms)` 自身是有限观察任务，可多次观察同一个持久 cleanup 工作，绝不重新执行释放。它建立独立 cleanup CTS/deadline（不能链接已取消业务token）；到期返回 Released=false/ObservationTimedOut=true，原 cleanup/端口 Task及资源仍被root持有。`TransferToRoot` 给出 root/slot 强持有的确认，幂等；ack false时调用宿主保持引用并进入人工恢复，不能销毁借用对象。ack accepted仅表示移交成功，绝不表示已排空。原Task迟到成功/失败/取消由根继续观察，异常被记录，迟到结果不会覆盖已经确定的业务失败。

### 4.3 状态、事件、唯一释放

#### 4.3.1 U1有界借用scope公开补充（0.2.2；不改C1/C2算法）

旧StartBorrowed签名和语义保留，仍用于单一原调用；**不能用它假装已预约任意内层Task**。U1只通过上述ReserveBorrowedScope/StartLifetime/Start公开接线，不访问Core私有ledger。一次预约含1个生命周期槽、WorkSlots+CleanupSlots+ObservationSlots子调用槽及RetainedBytes；所有额度在同根原子扣除，总槽计入RootLimits.MaxPendingPortTasks、bytes计入该RootSlot和全根上限；拒绝Check.Value=null/DG-008，start/requestStop不调用，不创建scope/任务。关闭业务接纳后不能新Reserve，但已有scope仍有专用Cleanup/Observation容量。WorkSlots/CleanupSlots/ObservationSlots分别1..64，MaxStarts正Int32且至少槽数+1，RetainedBytes正；这是有界记录/防滥用配置，不是客户性能值。

预览首版明确WorkSlots=5、CleanupSlots=4、ObservationSlots=1、MaxStarts=4096：**共11槽**（包括生命周期）；与0.2.1“至多8原Task槽”的未闭合措辞不同，本版明确包含接收门/生命周期/观察容量。Work槽固定0=Open、1=Show、2=AuthorityChanged、3=Expiry timer、4=模块遮罩/呈现Dispatcher；Cleanup槽固定0=Clear、1=Release、2=Close、3=模块解绑Dispatcher；Observation槽0=QueryClear/QueryRelease择一串行。接收门任务是每槽固定内部记录/continuation，不另开无界Task队列，包含在本槽的保守bytes核算。桥的内部Dispatcher工作由相应Show/Clear/Close原Task保证等实际应用/退出后返回；桥不得启动与原Task失联的render/native工作。若真实adapter另有原Task，必须提高已批准槽/bytes预算并用Start登记，不能偷借其它ledger。

StartLifetime恰一次，scope在创建时已经强持borrowedOwner/requestStop和全量额度；生命周期原Task**在锁外run前**已占位登记，返回后核scope ID。Bind仅预约scope、登记lifetime并附View，然后返回；不await lifetime.Completion、root.Close或包括自己scope的账本，避免自等待。StartLifetime的run不包括Bind/Start方法本身，只运行预览Owner的消息处理与清理汇合。父slot.Close触发已有scope.RequestStop，再等待其真正Completion；lifetime禁止调用父slot.Close/ObserveAll或await自己的scope.Completion。没有公共Dispose/手动清空槽来绕过释放门。

Start先在指定lane/index占位/固定代次并增有界starts计数，才在锁外调用start；重复在途槽/越界/新Work已停均拒绝（DG-008/DG-001），不调用delegate。Original保存**实际返回Task**，ValueTask在delegate内只AsTask一次；不能传WaitAsync包装Task。Original完成后在结果接收门内执行同步非阻塞accept，执行期间仍持槽和结果；Received仅在accept完成后给调用者结果。accept应先把成功获得的lease/回执写入borrowedOwner，再登记其watch/后续子Task；如果代次已过期仍接管资源并触发清理，不丢成功结果。accept抛错保留原成功result和owner，记录错误并RequestStop，Received失败不等于Original未完成或资源未取得。start同步throw/null Task记录为失败启动（保留异常、占位owner，不启动未知任务），同样触发停止清理。槽只有Original确实结束、accept退出且结果已接管后才能为下一个不同代次复用；clear/release/close同一副作用ID的未决结果只Query不重发。

Root强持每个Original/Received接收门、结果与owner；Fault/Cancelled均必须被观察，不只看Received。MaxStarts限定整个binding的实际启动/捕获次数（含lifetime），另计尚未消费的捕获预约。每次Work.Start接纳时，保守为其accept门原子预留最多WorkSlots-1次CaptureProduced额度；本次启动与预约之和不得超过`MaxStarts-CleanupSlots-ObservationSlots`，不足则拒绝delegate并RequestStop。Capture消费该原结果门的预约，accept退出后归还未消费预约；Capture自身的accept不得递归Capture，也不从清理尾额取数。因此迟到Open即使遇到RequestStop或启动数边界，仍可接管已产生的watch。停止前所有lane的普通启动共用上述非尾额部分；容量不足转最终停止，不继续接纳下一选择。停止后Cleanup/Observation可使用专留尾额，覆盖最终Clear/Release/Close/解绑Dispatcher及一次查询，不被先前刷新/切换清理耗尽。再次恢复查询超额返回DG-008并保留scope，不自动换root或新scope逃逸。固定槽限制并发，总启动数限制串行滥用；不得每个tick生成scope或在Original未退出时覆盖引用。

`CaptureProduced`只允许在本scope的Work.Start结果accept接收门内调用，绑定由该结果产生、已经存在的原Task；不调用启动delegate，不获取新资源，使用已预留workSlot/捕获额度。它专用于Open返回lease时的AuthorityChanged登记，**即使Work已停仍允许接管**，避免迟到Open资源失主；原watch槽必须事先空闲（上一选择watch已结束才允许新Open），超限/错误注册仍强持已经接管的lease/原watch于该结果槽并保持未决，不丢引用。Received给外部前已完成Capture或明确记录接管失败；该特例不能从任意线程登记无限Task，也不能在accept中启动被禁止的新业务。expiry timer若Work已停则不启动，直接发清理信号；已启动timer有独立CTS，cleanup先取消它再汇合。

RequestStop幂等，先禁新Work，再在锁外调用预先登记的requestStop（要求有界、无IO，只发Owner清理信号/取消expiry），callback异常单列CleanupErrors且root仍持owner。Cleanup/Observation在这个已预留scope内仍能启动，**不要求其开始前lifetime已结束**，否则会自锁。只有所有已启动Original/接收门结束、Owner确认最后lease归还与View关闭、lifetime返回ResourcesReleased=true且ScopeId精确相同，scope.Completion才成功确认释放并归还整批预留；业务WorkErrors可非空且不被cleanup覆盖。lifetime若throw、返回false或错误ScopeId，root记录并保留未释放owner/额度，Completion保持未决，靠原Owner显式恢复，不以Task结束冒释放。TransferToRoot返回该scope所属原root/slot接管ACK，scope/owner/原Task无需搬到新对象。

`RootSlot.StartBorrowed`为UI/Adapter原调用的同一根接线：先预约Task/字节槽并强持borrowedOwner和release委托，再在锁外执行start；同步throw/null Task为DG-011且走唯一cleanup，不能丢owner。成功返回BorrowedWork.Original为实际原Task（ValueTask只AsTask一次），不外包WaitAsync；release只在原Task确实结束后调用一次并持有原释放Task，迟到throw同样观察。CloseAsync等待这些工作及资源；不能因事件退订/控件卸载删记录。若本操作根额度不足，在调用factory前返回DG-008。控件的投影/Dispatcher任务都用此入口，release=返回已明确不含租约的投影本地额度；真实影像/Store租约的release必须调用原Owner确认，不能用Task.CompletedTask冒充。Owner必须与Session相同，不允许外部转移进另一个无限root。

流程：Accepted→Validating→Running→Completing→Draining→Drained→ResourcesReleased→唯一终态。预检失败没有 operation；接纳后拒绝也须走排空。DrainUnknown 是停止或释放未确认的**非终态**；在此状态 Completion 不完成。根与UI可查询/移交，不能报成功、Cancelled或资源归还。端口完成后用 lifetime 的 StopAndRelease 确认（即使正常完成也确认所有借用租约）；只有原Task全部退出、提交及查询I/O原Task真正退出（知识可仍为Unknown）、事件发布退出且 Stopped=true/AllLeasesReturned=true 后才进 Drained。停止未知/释放失败保留根槽，最终人工隔离回执须经同端口确认后推进，不能强制清空。Terminal Unknown只允许资源已经释放但持久化结果仍未知；该状态保留原operation持久身份，不再自动执行。Store.Commit/Lookup原Task返回CommitStatus.Unknown且所有租约归还时，知识未知不阻断Drained/ResourcesReleased；后续Lookup是新的、有界、受读权及root预算约束的观察调用，不重执Commit。若原查询I/O尚在途（即使WaitAsync观察到期），仍保留root槽，不能宣称释放。

每种借用对象按 operation/generation只释放一次，释放动作由单一slot所有者CAS推进；重复Close/取消/迟到回调不得双释放。业务错误先保存为primary error，cleanup错误单独诊断且不覆盖；业务已确认提交即使随后取消也保留原提交结果。`Succeeded` 对训练仅为“候选资产及训练回执完成”，对评价仅为“报告提交完成”，对用途仅为“外部决定已校验并投影”，均非质量放行。

事件序号在同operation内严格递增，先更新可查询状态再发布事件。Accepted/状态/终态不可丢；progress允许合并。有界队列满时停接纳/背压，不为诊断创建无限Task；终态回执不依赖UI订阅成功。订阅者异常隔离；回调禁止阻塞，UI Dispatcher使用异步有界投影，回调长期不返回计为未排空。退订只停止后续投影，不能取消原Task或释放资源。每个回调带generation，关闭后迟到的旧generation只写原operation诊断，不覆盖新session显示。工作超时DG-010后请求取消，仍等真实停止；Task.WaitAsync timeout只意味着观察到期。

### 4.4 错误键及恢复

| 键 | 单一含义 | 恢复 |
|---|---|---|
| DG-001 | 必填/格式/未知枚举/编码非法、重复成员、输入变化 | 修正新请求 |
| DG-002 | 非空不支持的协议或方法版本 | 明确适配，不回落默认 |
| DG-003 | 权限不足/撤销/过期/提交原子保障缺失 | 重新授权新操作 |
| DG-004 | 精确来源暂不可读 | 原引用有限退避，由宿主发起 |
| DG-005 | 内容hash/闭包/回执身份冲突 | 隔离调查，不重算覆盖 |
| DG-006 | 硬谱系环/缺父/组跨不相容划分/组映射不完整 | 新划分和影响分析 |
| DG-007 | 真值或参照不满足所选任务 | 保留缺口；新标签修订 |
| DG-008 | 非法预算、容量/资源预留不足/checked溢出 | 不接纳或显式新预算 |
| DG-009 | 业务取消已请求并最终确认停止 | 确认释放后Cancelled |
| DG-010 | 业务deadline耗尽 | 查询并排空；不假定停止 |
| DG-011 | 可确定的端口程序失败 | 幂等条件下由宿主重试 |
| DG-012 | 提交结果未知 | 只查原operation |
| DG-013 | 任务/模型/坐标/预后处理/分母方法不匹配 | 固定新方法身份 |
| DG-014 | 分母/独立组/区间无法计算 | 诊断报告仍可保存，阻断资格建议 |
| DG-015 | 模型、标签或资格撤回 | 不复活旧资格；向原Owner请求回退 |
| DG-016 | 同operation/幂等键异内容 | 拒绝，不换键掩盖冲突 |

超时是DG-010，容量/预算非法是DG-008，二者不混用。现场参照缺失和运行失败独立；有缺口的有效诊断报告可以成功提交，但 `QualificationGranted` 始终 false（本模块无授予权限），Gaps保留；绝不把“有分数”当资格已获批。

## 5. canonical 字节、hash与兼容

模块canonical是**治理身份编码** `dg-le-v1`，不改变模型资产Owner的 `model-core-jcs-v1`。无JSON默认序列化/反射顺序/机器文化/DateTime本地格式。BCL `SHA256.HashData`，小写hex；所有字符串严格UTF-8，无BOM、不trim、不Unicode归一化；非法UTF-16 DG-001。字符串编码为uint32 LE字节数+实际字节；int/enum为int32 LE，long为int64 LE，uint为uint32 LE，bool为单字节0/1；nullable先单字节0/1，有值接原值编码；集合先uint32数量再各项。string必填不可null，可空text用nullable规则，空串与null不同。记录逐字段按§3/§4声明顺序递归编码，hash值编码其64字符字符串，utc若以后加入编码使用int64 Unix微秒且不得丢精度。编码预留最大长度，超过额度拒绝，不返回部分身份。

| 身份域 | 有序完整字段（按上述编码） |
|---|---|
| `DG-SNAPSHOT-1` | 域字符串、`0.2`、SnapshotDraft所有字段；Members按Id ordinal，Labels.Observations按ObservationId，Selections按MemberId，Assignments按PhysicalGroupId；Strata/HoldoutRules各自ordinal去重前必须拒绝重复 |
| `DG-BIND-1` | 域、`0.2`、Task固定token、Snapshot.Id、Snapshot.Hash、ModelAssetRef、PredictionRevision、PreprocessRevision、PostprocessRevision、TaxonomyRevision、ThresholdRevision、BackendRevision；Snapshot.ContractVersion预检必须0.2，已经编码在域版本，不另编码 |
| `DG-EVAL-1` | 域、`0.2`、OperationId、IdempotencyKey、Authorization全部字段、Snapshot.Reference、Model binding完整字节长度+字节、EvaluationPlan全部字段、Budget全部字段 |
| `DG-TRAIN-1` | 域、`0.2`、OperationId、IdempotencyKey、Authorization全部字段、Snapshot.Reference、TrainingSpec全部字段、Budget全部字段 |
| `DG-PUBLISH-1` | 域、`0.2`、SnapshotPublicationRequest全部字段；Snapshot按Reference编码，内容须来自此前FrozenSnapshot |
| `DG-USAGE-1` | 域、`0.2`、UsageIntent全部字段；Reports按Id/Version/hash ordinal排序，重复拒绝 |
| `DG-REGION-1` | 域、`0.2`、RegionPairQuery全部字段；Truth/Prediction按ObjectId ordinal且无重复；有效域完整Id/Version/Hash入码 |
| `DG-REPORT-1` | 域、`0.2`、operation/request hash、EvaluationResult/TrainingProduct/UsageProjection/SnapshotPublicationResult（四选一的int32 tag 1/2/3/4+对应全部字段）；Endpoint/coverage/interval/Event排序规则见§6 |

Binding Task token固定为Defect/Ocr/Classification/Detection/Segmentation/Anomaly，不接受任意Enum.ToString未知数值。请求的计划Endpoints先ordinal排序去重校验（重复是错误），集合顺序不改变语义身份；所有有业务顺序的数据，如字符原串或变换链，保持原顺序。序列化不得将报告自己的hash递归纳入自身，原模型内容也不能加入报告生成字段后重算模型身份。Report含double只用于派生值：普通计数比Endpoint按§6核原整数分子/分母，macro-recall按冻结方法核逐类召回的均值，IntervalResult保留原统计Owner按方法给出的上下界，不把均值或区间强套为某个总整数比。可用值必须finite，以IEEE754 binary64 LE编码，-0规范为+0；null编码0；不同算法浮点结果容差只用于实测比较，不能重写历史字节。旧协议只用显式旧reader和旧hash规则验证，新reader不自动升级未知枚举/缺字段。本次解释修正不改变任何已接收规范向量。

### 5.1 完整小型 Golden：Binding 270 bytes

输入：Task=Defect；Snapshot=(snap-A,0.2,64个a)；ModelAssetRef=asset://sha256/后64个b；其余依次predict-v1、pre-v1、post-v1、classes-v1、threshold-v1、backend-v1。以下是**完整**字节，不省略、不从受测codec产生Expected；各行连接后是一个hex序列：

```text
0900000044472d42494e442d3103000000302e3206000000446566656374
06000000736e61702d4140000000
6161616161616161616161616161616161616161616161616161616161616161
6161616161616161616161616161616161616161616161616161616161616161
4f00000061737365743a2f2f7368613235362f
6262626262626262626262626262626262626262626262626262626262626262
6262626262626262626262626262626262626262626262626262626262626262
0a000000707265646963742d7631060000007072652d7631
07000000706f73742d76310a000000636c61737365732d7631
0c0000007468726573686f6c642d76310a0000006261636b656e642d7631
```

SHA-256=`cca3c02d5294638a3041660609742a65b8d4c42fea839a4847b98bca68522efc`。Expected可由测试独立 `BinaryWriter.Write(uint byteLength)` 和严格UTF8逐字段拼接，并与上述literal bytes双重核对；不得调用EncodeBinding再将其结果设为Expected。另用BCL标准向量UTF8 abc→`ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`，空字节→`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`核底层hash。改snapshot版本9.9须先DG-002；改一个模型/标签/预算/方法字段须改变对应请求hash；重排无序成员不变；原数组后改不变；原串空白/NFC变化须改变身份。

## 6. 数据、标签、划分与任务评价实施卡

### 6.1 来源闭包与去重

1. 原证据Owner供精确版本/hash/字节/物理组/派生关系及来源限制；先预算后解析。相同ID版本解析成不同hash DG-005；相同内容hash不自动证明同一物理样本，反之文件名不同也不证明独立。
2. ParentId必须指向本快照成员（外部根先由宿主解析为明确成员），拒绝自环、环和缺父。按Id ordinal建立有向图，以有色DFS检环；再union-find合并同PhysicalGroupId及parent-child。最终component的规范组ID取成员声明PhysicalGroupId ordinal最小值，原组映射保留供追溯。若同component有两个分区，DG-006；Assignments须且仅覆盖所有声明组，分区值已定义。
3. 双面、多FOV、裁剪、增强、重拍、返修、相邻重叠卷段及同源注入由来源Owner提供硬边。感知相似只生成待复核候选，不自动union、改标签或转移真值。采集/合成/注入独立统计，未知provenance拒绝。
4. 显式来源保留/删除政策归数据Owner。本模块收墓碑与删除回执，追加影响关联，不擅自保留应删原件；无法重新读取时标来源不可重建，不改旧hash。

### 6.2 划分和参数建议

`SplitSpec.MethodRevision="group-explicit-v1"` 是可立即决定的首选路线：调用者提交精确组映射，模块验证覆盖、硬同源、外部/时间留出、挑战集隔离。seed记录且必填，但不凭seed制造映射。外部/时间规则由已批准Profile解释，规则本身不是自然语言执行器。Core只验证已给映射；IFactPort确认它符合来源/工艺时间规则。

自动建议为独立纯操作 `CoreValidator.SuggestSplit(SplitSuggestionRequest? request)`，返回 `Check<SplitSuggestion>`；其完整类型如下，不调用设备/不更改已发布split：

```csharp
public sealed record SplitGroup(string Id, int Items, IReadOnlyList<long> ClassCounts,
    Partition? LockedPartition);
public sealed record SplitSuggestionRequest(IReadOnlyList<SplitGroup> Groups,
    IReadOnlyList<int> TargetPpm, uint Seed, string MethodRevision, Budget Budget);
public sealed record SuggestedGroup(string Id, Partition Partition);
public sealed record SplitSuggestion(ImmutableArray<SuggestedGroup> Assignments,
    ImmutableArray<string> Gaps, string MethodRevision);
```

`TargetPpm`恰4项对应Train/Validation/Test/Challenge，非负且checked和=1,000,000；locked组先整体安置，不满足目标时保留差异不拆组。方法 `group-greedy-v1`：未锁组先按Items降序、再按SHA256(seed uint32LE+length-prefixed Id)字节序、最后Id ordinal；逐组计算分配后各partition样本数相对目标的平方偏差之和，使用BigInteger有理数精确比较（目标0的非锁partition不可选）；并列按累计各class计数相对目标偏差，再固定partition枚举顺序。类计数向量长度必须一致、每项0..Items；group-greedy-v1把各项视为可重叠分层标记，允许总和>Items，仅用于建议平衡，不推断为单标签混淆矩阵或真值。按总量/总class固定目标，不能在迭代中重算目标。输出类只存在一个硬组时写coverage gap，不把它拆成独立验证。说明这是样本/类别平衡近似，无独立资格保证；O(G×P×C)外加排序，预检预算计class矩阵。建议经数据Owner批准后才转换为显式SplitSpec新修订，失效输入/seed/目标变化不得复用旧建议。

固定scikit-learn 1.7.2源码与测试说明GroupKFold的shuffle分组并不保证样本均衡，StratifiedGroupKFold为近似，GroupShuffleSplit各轮独立抽组不能冒多轮独立外部测试。本模块选择显式组映射+有解释的建议，借思想不带Python运行依赖。参数选择仅用Train/Validation；Test在方法冻结后一次报告；Challenge访问与真值由独立Owner控制，看过挑战结果再调参必须新声明暴露/研究状态。

### 6.3 标签观察、选择与仲裁

保留全部Observation及Actor/可见性/原证据，不覆盖旧观察；Selection精确指向唯一观察和仲裁回执，不按时间最新/多数票自动选择。已看模型的观察不能冒盲审；盲审由human-review数据访问端口限制，UI折叠不算。缺席、平票、微缺陷分歧、缺参照归Missing/Disputed；Unobservable不是正常。更正产生LabelSet新Revision、Snapshot新hash和新评价，关联原报告影响，不重算旧事实。

Taxonomy/TruthMethod/ApprovalReceipt缺失为DG-007；class/text/regions与任务适用性由方法和IFactPort共同校验。OCR原文不是BOM期待；缺陷region不是客户放行意见；人工批准并不能证明图像具可观察性。所有隐藏标签读取仍核当前权限，历史报告不是新的读权凭证。

### 6.4 义务覆盖与统计通则

评价义务是选定Partition的全部成员/对象，不取预测成功子集作为全集。每成员保留TruthStatus×PredictionStatus×AutomaticallyAccepted×Origin交叉单元；Coverage各单元互斥且sum=全部义务。缺少prediction补 `NotExecuted`事件并写Gap，重复/未知MemberId DG-005；不能zip截短。拒识仍可保留原类别/文本作明确条件诊断，但不加入自动接受。Truth缺失且prediction失败可同时存在，不能把两个计数相加冒全集。

Endpoint存整数分子、分母、Unit和Reason；有限比例才算double。无分母Value=null且Reason，绝不加epsilon、clamp至1或返回100%。FP/board、报警/board、CER是比值，可能>1；不使用Probability值对象。单标签分类比例可≤1但按方法验证，不把所有endpoint强行限制到1。Endpoint排序Name/Stratum ordinal；coverage按四个enum/bool键排序；interval按EndpointName ordinal；Events按MemberId ordinal。每义务一项EvaluationEvent保留原truth/prediction、失败/拒识和计数，计数是整数，原串仅在获读权的报告范围持久化。未算的文本距离不补零解释，Status/Reason区分，正常非OCR项的文本计数为0且文本null。至少报告全义务数、可评价真值数、完成数、拒识数、自动接受数、各失败/未执行/未知数、Acquired/Synthetic/Injected分层。

### 6.5 缺陷二元分类/多类分类/异常

方法 `binary-v1`，合法class为positive/negative；`Approved`且Completed且class合法的可比子集计算TP/FN/FP/TN；recall=TP/(TP+FN)，precision=TP/(TP+FP)，fpr=FP/(FP+TN)。全义务端到端检出率另以已知positive全量为分母，拒识/失败/未执行不会从该分母消失，分子仅已完成正确positive；命名 `end-to-end-positive-hit`，不暗称现场escape。Unknown不计TN。10项软件向量：8可比TP2/FN1/FP1/TN4、1真值Missing、1positive拒识→条件recall2/3、precision2/3、fpr1/5，端到端positive-hit2/4，coverage10；拒识正确与否未自动判定。

多类方法 `multiclass-v1`：固定taxonomy类表，按真值行/预测列混淆矩阵，逐类one-vs-rest分母及support，macro只在方法规定可计算类上并列coverage；未出现类不自动100%。`Classification`采用此法时Plan.Endpoints必须列精确类键如recall:chip，类别来自Truth/Pred输入且需taxonomy匹配。异常检测方法 `anomaly-binary-v1` 使用冻结阈值后positive/negative义务，分数不叫概率；没有合格异常真值时只有正常误报/覆盖，不能声称异常召回。传统良品变化/异常模型的正常库污染、近重复、温漂/照明覆盖分别报告，不从训练正常标签推导现场正常。

### 6.6 自由检测与分割

RegionMatchingPolicy.ValidDomain指向不可变域manifest，精确登记每个MemberId/EvidenceHash/CoordinateRevision/图像尺寸/有效像素mask的原引用，不用同一个“当前ROI”套所有样本。RegionPairQuery由MemberId在该**已绑定manifest**内唯一查域，返回ValidDomain为同manifest引用；成员缺失/重名/坐标版本不同拒绝DG-013，不能拿别板的V补齐。完整域内容的长度/hash由Adapter读取时核验，未提供域内容即Unsupported。

检测方法 `region-iou-v1` 输入同一坐标修订、有效域、已观察真值region和预测region。行列像素边界整数、非负、Height/Width>0且checked不溢出，重复object ID拒绝。先按class与有效域划分，bbox不交且都是该region的可信外包框才粗筛为不匹配；框不可信必须由region端口核实，不能用bbox IoU当region IoU。对剩余每一对分别调用IRegionMeasurePort：Truth/Prediction各为单项ImmutableArray，ValidDomain逐字段取冻结Plan.RegionMatching.ValidDomain、CoordinateRevision取冻结成员坐标、MethodRevision取计划方法；返回必须逐字段绑定相同ValidDomain/CoordinateRevision及HashRegionQuery(query)。缺有效域或换域DG-013/005，不能隐式读“当前域”或构造器全局上下文；`U=T+P-I`，需0≤I≤min(T,P)、T/P≤ValidPixels、U>0；空region和0面积不当有效centroid。不同坐标DG-013，不自动缩放。

RegionMatchingPolicy.MinimumIouPpm在1..1,000,000，三个对象/配对上限为正且受Budget；有效域ValidDomain的Id/Version/Hash必填并合法；实际有效域内容由域Owner按此精确引用解析。此policy连同方法修订纳入请求hash并经IFactPort确认适用；缺policy/证据拒绝该视觉切片，不由UI补0.5。边比较 `I*1,000,000 >= thresholdPpm*U` 使用checked/BigInteger。最大基数一对一匹配，再最大总IoU，再按排序(truthID,predID)匹配列表字典序最小。实现用单位容量二分图：先用无费用网络求最大流量K，再从全新零流网络以精确有理费用-IoU、Bellman-Ford残量最短路逐次增广K单位求最小费用（不能用浮点负环容差）。平局对候选边按(truthID,predID)依次试强制入选，重新求解受强制约束的最优流；仍保留原基数和费用才固定该边，否则排除，直到固定完整匹配。重复求解成本计工作预算/deadline，超限DG-008/010不返回部分匹配冒完整；目标规模超预算DG-008。必要时沿assignment公开模块接入，接入前保持本模块上述确定目标，不猜它的签名。TP为匹配数、FN为未匹配truth、FP为未匹配prediction；自由检测没有天然TN，报告false-alarms-per-board=FP/已完整评价板数可>1，不能伪造FPR。重复报警只能一项TP，其余FP。未观察区既不补正常，也不悄悄删报警：按有效域策略单列不可判定。

分割 `pixel-confusion-v1`：同样必需冻结Plan.RegionMatching.ValidDomain；每class的Truth/Prediction数组按ObjectId固定，端口在指定有效域分别union后返回T/P/I/V（数组Empty仅表示该批准类没有区域，不是真值Missing）；对应Query携带完整域Id/Version/Hash与坐标，返回ValidDomain/CoordinateRevision/QueryHash精确一致才统计；TP=I、FN=T-I、FP=P-I、TN=V-(T+P-I)，检查非负和sum=V；IoU=I/(T+P-I)、Dice=2I/(T+P)，两个分母均0时未定义及空类事件，不能自动1。像素指标保留图/板层级，区间不把每像素当独立样本。多实例/多类必须先由方法冻结互斥/重叠语义；只有region对统计而没有完整有效域V时不宣称分割TN或像素准确率。

### 6.7 OCR原串与派生比较

方法唯一沿[DEV-AI-063 §14 OCR-EVAL-SCALAR-1](../../shared-modules/guidance/07-ai/DEV-AI-063_数据集、GroundTruth与统计验证开发指导.md#ocr-text-evaluation-method)，此处为调用绑定，不另造编辑距离路线。使用合法Unicode scalar，不能String.Length当字符数，非法UTF16显式Invalid；不trim、大小写/NFC归一化或先跨目标串接。单位成本有界DP、真值→原读、固定tie与独立小向量沿该节。MaxDpCells同时限制所有对象总计算，不只是峰值矩阵；checked预检后逐行取消检查。原串完全相同不反推AutomaticallyAccepted。

可比较非空真值集合K的micro CER=总(S+D+I)/总真值scalar数，合法空读为删除；超时/缺输出不是空串；A→AAAA CER=3。无字真值单列误读事件/插入数，不造0/0 CER；Missing/Disputed不可拿BOM期待补真值。端到端必读完成且原串正确率的分母含已知必读目标中的失败/拒识/未执行，另给条件准确率和自动接受错读率/覆盖。NFC等获批派生比较另具名方法和位置映射，不能覆盖原串结果。字符、token、字素簇和物理印字不是同一单位。

### 6.8 区间、配对比较和资格包

v0.2内置可请求端点闭集：binary-v1/anomaly-binary-v1为recall/precision/fpr/end-to-end-positive-hit；multiclass-v1为recall:<classID>/precision:<classID>/macro-recall；region-iou-v1为object-recall/object-precision/false-alarms-per-board；pixel-confusion-v1为iou:<classID>/dice:<classID>/pixel-accuracy；OCR-EVAL-SCALAR-1为cer/conditional-exact-string/end-to-end-exact-string/auto-accept-error/auto-accept-coverage/no-text-error。未定义endpoint DG-002，不补“相似率”。全部义务coverage不受Endpoints筛选；所有请求endpoint都输出，零分母null+reason。macro-recall明确取本次具有Approved真值support>0的类的条件recall算术均值，覆盖遗漏类另列，不能把这个选择子集当全部类证明。pixel-accuracy需class互斥且valid域闭合，未满足输出NotComputable，不把各class TN相加作为总像素。

Interval=NotRequested时不调用统计端口，Intervals为空，诊断可提交。GroupBootstrap只映射statistics已冻结的`group-percentile-bootstrap-v1`：ConfidencePpm在1..999999，Resamples≥2，MinIndependentGroups≥2，Tail固定TwoSided（当前IntervalQuery无单侧字段）；PRNG/quantile固定`pcg32-xsh-rr-v1`/`linear-hf7-v1`。这是A1适配预检，不改变C1/C2既有输入编码：旧Core可结构接纳Resamples=1，S6适配须在启动前明确拒绝DG-001，不静默改2。组数不足/零分母保留原组与STAT诊断、区间NotComputable及DG-014 gap，不改Wilson/删困难组。OwnerMethod仅调用已明确注册的公开provider，未注册不支持；加权、时间块、多层cluster、BCa等不在S6范围。

S6桥完整构造/调用/结果与资源映射唯一见§13.1.1–3。整组是已声明独立板/批次，不是字符/像素；端点分子分母与义务覆盖分别保留。既有GroupStatistic不是完整S6来源，Obligations/MissingTruth/Abstained/Incomplete无法反推Failed×Covered交叉表，更不等于权限：Adapter只接收宿主按原事件、冻结Snapshot/ModelBinding/Labels/Plan和独立组规则提供的完整封闭NumericalRequest，逐项核旧query与其投影一致，不从全局目录补数。

两模型比较用GroupPairedRatioTask保留相同组/原义务PairingKey、各自来源与全部覆盖，差值left−right、同一随机索引；缺组不能取交集继续。现有IntervalQuery不表达配对，本轮不扩C1/C2公开DTO：配对比较作为A1无UI报告装配消费者直接调用同一上游数值接口并保存完整结果，不塞入单模型Intervals冒同一语义。原预测/模型决定不被统计结果改写。模块不选客户置信门限、不签资格、不获得读权/质量放行；未获来源读取权不得构造请求，统计Coverage只描述义务执行，不能充当AuthorizationReceipt。

## 7. 训练、评价、用途与回退操作链

Snapshot发布为第四个独立治理操作：PublishSnapshot→Freeze SnapshotPublicationRequest→授权purpose=publish-snapshot→Facts Publication=true（Model/Plan/Training=null，精确Snapshot/Labels）→检查研究缺口/来源/split已批准的原回执→Store Commit仅Publication非null→排空→Outcome.Publication。有缺口快照只保留研究用途，不能转换成训练/生产资格。资料/标签观察追加使用同快照新修订发布，不覆盖原Revision。Core.Freeze草稿不等Published，也不能把本地hash当Store提交回执。UI首版不增加快照发布命令，宿主可无UI调用该公开入口；SnapshotPublicationRequest无原件路径、不执行推理/训练。

### 7.1 训练治理与实际训练分离

StartTraining接纳前验证FrozenSnapshot有Train/Validation、标签参照适用、split闭包和provenance；Epochs/BatchSize/BatchMultiplier均正，checked有效batch与成员/预算匹配。只允许TrainingSpec声明的模式：SupervisedBatch→`train_dl_model_batch`，传统AnomalyDataset→`train_dl_model_anomaly_dataset`完整正常集一次调用，GcAnomalyBatch→`train_dl_model_batch`。不能把传统异常训练说成任意chunk/resume；checkpoint policy明确 `none-new-operation-v1` 时失败从精确输入新operation重开，不能“继续最近文件”。其它checkpoint policy由训练Owner提供验证证据，未支持DG-002。

顺序：冻结请求→初次权限→Facts校验来源/标签/工具链/配置→ITrainingPort→验证Product的operation/snapshot/config/toolchain/native状态和精确candidate asset→提交前权限→Store→排空/唯一释放→Outcome。Train/Validation之外的Test/Challenge不得导出给训练器，训练端口由FrozenTraining的只读数据访问器限制用途，不能给整包文件路径后靠UI约束。运行代码/toolchain/config/seed/后端硬件/库版本、环境与随机性必须进入RunEvidence；确定性未证明就写不可复现限制。验证集best checkpoint的选择指标/方向/tie/早停规则来自Configuration，不拿Paddle日志norm_edit_dis当平台CER。训练损失/候选模型不是资格或可部署版本；文件资产提交归model-assets，治理只引用其精确回执。

#### 7.1.1 Training Adapter的配置、输入和调用顺序

本节是§4.1 `ITrainingPort`的内部实施规格，不新增Core训练任务、模型Store或训练框架。训练器由宿主显式注入，在隔离worker中通过`ImageLibDotNet.cv2`执行；治理服务不在WPF Dispatcher或生产检测线程训练。toolchain是固定版本的模型/预处理/训练工具闭包，configuration是完整参数值，不以“Owner以后补算法”代替下面的调度和拒绝规则。复用[DEV-AI-060 §12](../../shared-modules/guidance/07-ai/DEV-AI-060_AI运行治理开发指导.md#12-训练checkpoint导出与部署交接的实施方法)的已有效研究，不重新下载框架或复制事实Owner。

Adapter解析的配置版本为`dg-halcon-training-config/1`；文件字节/格式由输入Owner封存，完整Configuration.Id/Version/Hash经Facts核验且全读到EOF。配置只接纳有类型的以下字段；未知键、重复键、非finite数、缺必填、隐含默认值均拒绝。它不是产品Recipe Schema，也不改变TrainingSpec字段。

| 字段组 | 完整输入、来源与校验 |
|---|---|
| 模型与任务 | 精确InitialModelAsset、ModelType、Component（Whole/OcrDetection/OcrRecognition）、ClassMap（平台class ID→HALCON整数ID）、CharacterSetRef?；Defect/Classification对应classification，Detection对应detection，Segmentation对应segmentation，AnomalyDataset对应anomaly_detection，GcAnomalyBatch对应gc_anomaly_detection，OCR对应具名ocr_detection或ocr_recognition。二元ClassMap必须含negative/positive，两者不能互换；OCR组件候选不得伪装为完整Deep OCR组合 |
| 输入闭包 | PreprocessRef、PreparedSamplesManifestRef、LabelRevision、SplitRef、CoordinatePolicyRef；manifest逐行MemberId、EvidenceRef、原字节hash、预处理产物Ref/字节/hash、shape/channel/scalar/range、任务标签引用、变换/有效域引用。成员集恰为本FrozenTraining的Train/Validation，不含Test/Challenge；预处理参数与产物同修订。缺处理产物时由该toolchain的固定预处理工具生成并封存，不能让程序员选择resize/crop/归一化或随机重划分 |
| batch配置 | Seed、Epochs、BatchSize、BatchMultiplier、CheckpointPolicy必须逐值等于CopySpec；Sampling=`sha256-order-v1`、TailPolicy=`repeat-prefix-v1`、Augmentation=`none-v1`。首版固定无额外增强；需要增强须给有版本/代码/随机流的toolchain及新配置，不能临时开默认增强。Epochs为最大轮数，不是已运行轮数；传统异常模式要求BatchSize=BatchMultiplier=1作协议占位，不表示其原生整集训练为batch1 |
| HALCON参数 | Runtime/device精确选择、精度/solver及模型实际支持的typed参数表、batch模式每epoch的完整LearningRate数组（长度Epochs，值>0且finite；传统异常此字段为null，不设置不适用的solver/LR）；batch分支显式batch_size、batch_size_multiplier、learning_rate。只允许目标26.05手册为该ModelType列出的参数/类型；禁止任意键字符串透传。只写可set项，记录可get项的实际读回；只读或不可get项分别保留Requested/Observed/Unknown，不伪造实际值 |
| 传统异常 | max_num_epochs=Spec.Epochs、error_threshold、domain_ratio及其它显式采用的该算子GenParam；范围逐项沿26.05原手册，不默用示例默认值。训练Train成员必须全部为Approved negative/正常，含positive/Missing等即DG-013，不能筛掉后冒原完整Train；整集一次调用，batch轮次/LR不应用于此分支；不用batch损失冒其final_error |
| validation/选优 | ValidationFrequencyEpochs>0、Selection=Final或BestValidation；Best必须有本任务§6已支持的PrimaryEndpoint、Direction=min/max、逐项必要覆盖/拒识/finite约束，EqualTie固定较早完成更新；EarlyStop=Disabled或(PatienceEvaluations>0,MinImprovement有限≥0)。传统异常只支持Final、Disabled（停止由其GenParam控制）；约束值是输入，不由模块定客户质量阈值 |
| 资源与输出 | MaxPreparedBytes、MaxLiveSampleBytes、MaxUpdates、MaxCandidateBytes、MaxValidationCalls、MaxRunEvidenceBytes、worker CPU/GPU/磁盘额度和工作/清理期限均显式有限并受原Budget/资源准入约束；OutputRoles/format、模型native保存及fresh-read策略由toolchain固定。Configuration中的参数不是额度获得回执；准入不足在读取/创建native前拒绝 |

**源和DLSample。** 先读已批准初始资产至私有worker目录，按model-assets原完整文件/闭包核长度/hash/EOF；`cv2.read_dl_model`新建独占模型，`get_dl_model_param`核type、输入shape/channel/range和实际支持的class/字符配置。预处理产物只读按manifest映入DLSample：分类使用image及image_label_id；检测使用该模型批准的bbox类型、逐项坐标和bbox_label_id；分割使用同尺寸segmentation_image、类映射及未知域语义；OCR沿固定检测/识别procedure输出的正式DLSample键和字符/词框格式；异常使用批准的正常image。不能把RegionRef.Bounds直接当训练框、把Missing标签填0、把OCR完整行切成词或用未观察像素作背景。输入格式/标签转换由toolchain的固定source adapter声明并逐项核验；不支持的格式DG-002/013，无隐式替代。

HALCON Deep OCR的`read_dl_dataset_ocr_*`、`create_dl_preprocess_param_from_model`、`preprocess_dl_dataset`、`create_dl_train_param`、`train_dl_model`、`evaluate_dl_model`是procedure。生产接线由toolchain提供已固定版本的procedure实现/调用入口，或交付已封存的符合该模型要求的DLSample；不得写成不存在的同名cv2算子。原procedure若内部自行split/shuffle/选优，必须关闭或适配为下述冻结政策并核实际成员，否则拒绝这个toolchain，不能用其日志替代治理分母。本模块不自行设计字符检测/识别网络或训练标签转换算法。

**一个训练attempt的确定执行顺序：**

1. 预留原root工作/清理槽、worker及文件/CPU/GPU额度；授权并Facts核完后只解析本次配置与Train/Validation来源，核预处理产物manifest全覆盖。创建worker前保留原operation/request hash，worker与所有源借用均进入该原Task责任链。新attempt必须新operation，新配置不得沿旧hash重放。
2. fresh读取初始模型；先设置并读回可查询的batch/runtime/solver等批准参数，核实际ModelType和类映射。不通过set一个不存在的`seed`模型参数承诺确定性。Seed约束下面的采样排序；HALCON/训练工具的随机设置按toolchain记录实际接口/作用域，不能证明逐位重现时明确`NotEstablished`。
3. Train成员以MemberId Ordinal为规范序。第e轮（从0起）排序键为SHA-256(`dg-le-v1`字符串域`DG-TRAIN-ORDER-1`、uint Seed、int e、MemberId字符串)，digest按原32字节词典序，tie按MemberId。有效batch B=checked(BatchSize×BatchMultiplier)。每轮遍历一次排序序列，末尾不足B按本轮序列从头循环补齐，记录每个重复位置/原MemberId，不能将重复作新独立样本。N>0时更新数ceil(N/B)，预检Epochs×ceil(N/B)≤MaxUpdates；没有drop-tail或随机补样分支。
4. 每轮设置对应learning_rate；每个batch只在该独占模型上调用一次`cv2.train_dl_model_batch(model,完整B个DLSample,DLTrainResult)`，成功返回才计更新完成，保存total_loss及该模型返回的其它损失原键/值。非finite或缺必需损失即失败，不静默降LR/batch或跳过。batch=4×multiplier2不当作8×1的等价执行。DLSample/图像/字典在原算子实际退出后释放；缓存只能在MaxPreparedBytes内按manifest复用不可变产物，不能让后台预取越过取消边界。
5. AnomalyDataset分支不执行步骤3–4：按规范MemberId顺序组成完整正常集，预检整集可驻留额度，只调用一次`train_dl_model_anomaly_dataset`并保存final_error/final_epoch及实际GenParam。无足够额度DG-008，不分chunk。GcAnomalyBatch按batch调用；其归一化/统计若模型要求，执行toolchain固定的26.05 GC工作流，仅用批准Train/Validation用途；未完成该工作流不得导出正常完成候选。
6. 按固定频率及最后完成轮暂停模型写入；将该安全边界模型write_dl_model至独立文件→关闭写流→fresh read核type/input/class→按§13.1原model-assets封存完整模型/预后处理闭包，再对这份不可变精确候选validation。候选记录携完整ModelBinding（Snapshot/Task/精确asset及toolchain规定的Prediction/Preprocess/Postprocess/Taxonomy/Threshold/Backend修订）及Validation plan/成员manifest；不用可变训练句柄或未封存路径冒ModelAssetRef。比较直接复用§6对应任务的评价内核和原读/计数规则；训练视图只给Validation，不构造一个非法的Test评价请求来绕用途。保存完整义务、预测状态/拒识/缺项和端点；不把框架loss/accuracy/norm_edit_dis改名为平台CER。不可评价候选不参与Best，完全相等指标选较早更新。EarlyStop仅在完整有效validation后按Direction判断改善达到MinImprovement（相等不改善）；不足即计一次，达到Patience停止。validation失败/超预算本attempt失败，不跳过后继续选best。
7. Final选最后完整更新的候选，Best选满足冻结约束的最高优先候选；没有合格候选明确失败DG-013，不回Final。未经过步骤6的Final候选先执行同样write/fresh-read/seal及最终validation；已封存的Best/Final直接沿其精确原候选回执Resolve/read/Golden核验，不重新写当前训练模型或重发相同seal。Golden核验不得取Test/Challenge作调参输入。各候选仅是离线训练产物；OCR组件须由原OCR Owner组成精确完整模型后另评整链，不能自动更换生产组件。
8. 先核原seal完整回执和所有文件耐久身份（§13.1），再封存RunEvidence；它包含本请求/配置/toolchain、模型/样本/预处理/顺序hash、每batch原成员与重复位置、实际参数/环境、完成更新、validation选优、停止原因、候选/文件回执及所有未知。只有这些封存结果确认且native工作/源借用真正退出，才返回TrainingProduct.NativeStopped=true。治理报告随后沿§7.1原提交链保存；资产先成功而治理提交Unknown时只查原治理operation，不重训、不删除已封存资产。

`none-new-operation-v1`不提供exact resume、warm-start自动恢复或取消边界checkpoint。取消/期限停止新batch/validation/封存接纳，等待在途native/IO实际返回；已确认资产保原事实，晚到未交付产物只沿其Owner回收策略处理。停止未知保原worker/Task/输入/额度且NativeStopped不能true，原root有限观察，不kill后声称释放、不用“最后文件存在”恢复成功。首版自动参数只有§6.2分组划分建议和本节可解释顺序/尾补齐；不自动搜LR、batch、阈值、网络、增强或生产用途。

#### 7.1.2 HALCON Region Adapter的确定计数与证据

`IRegionMeasurePort`读取query引用的原区域/有效域，而不是当前UI叠加。来源目录按完整RevisionRef绑定格式、ObjectRef、尺寸/坐标/字节hash；支持HALCON Region文件或Owner已提供的整数行段mask。XLD仅在原Owner明确提供封闭轮廓→region的冻结栅格化方法时可用，不自动填开曲线或用Bounds补区域。读取全字节/EOF/hash、类型/count/整数行段和坐标失败拒绝；同域/同坐标/同方法的query先预检对象数、行段/像素/临时对象预算。无隐式缩放/裁剪/扩域。

顺序固定：read_region或按原行段gen_region_runs→各对象count_obj/尺寸范围核验→get_region_runs逐单region取实际像素段（ColumnEnd闭端checked转换）→检测单T/P或分割同class各自union1→各自intersection(T,V)/intersection(P,V)→intersection(T∩V,P∩V)。每一步保留独立临时对象；第二参数必须是这一次的单个region，不能批量Region2触发union。每个area_center返回像素数须finite、非负、可精确表示且≤2^53、≤Int64及本有效域像素上界；以整数行段checked计数复核T/P/I/V，发现不一致DG-005/013，不四舍五入大double。纯行段计数用于保真验证HALCON结果，不另实现交集/视觉算法。V/T/P为空时保留0及不可定义原因，不把area_center返回(0,0)当真实中心。

形成RegionMeasure时核§6.6守恒、原query完整HashRegionQuery、ValidDomain和CoordinateRevision逐值相同，Evidence指向封存的query/原引用/方法/计数诊断；不可算不伪造四个0。成功/失败/取消都等实际算子退出后Dispose区域/tuple/流，原Task未知留root，不把Dispose调用已发出当退出。区域读取、Mask坐标、空域、孔洞、两个不相交对象及重叠分割类为后续真实Adapter反例，不据本规范声称算法运行已通过。

### 7.2 评价操作链

StartEvaluation→Freeze→授权→Facts精确核标签/模型/预后处理/阈值/方法适用→PredictionSource按冻结义务读实际运行结果→版本/hash/count/成员和逐任务结果检查→覆盖/Endpoint/Intervals→重新授权→Store不可变报告→真实排空→完成。原预测归ai-inference；治理不偷偷重跑另一个模型来补缺输出。`Prediction.MethodRevision`等于Model.PredictionRevision；Batch绑定HashBinding(Model)、Snapshot精确相同。DG-005/013不替换成当前最新模型。

Completed/Abstained的text/class/regions按任务与方法检验；Abstained可提供原读，失败状态即使有诊断文字也不能当已完成预测。所有重复、超限、非法原文、未知成员先诊断，不能截前N项报告完整。partial运行可保存全义务缺口诊断，不宣称覆盖全通过。报告冻结时纳排/分母/方法不再变动，后续人工/标签更正新operation。

### 7.3 外部阶段决定和回退

RecordUsage从IUsageDecisionPort读取原授权/资格Owner决定，校验Decision、模型和Reports闭包、适用域/Stage及当前撤回状态；Owner明确Active才投影Active，不由本模块根据评分升级Offline→Automatic。回退意图必须Rollback=true且原Owner指定仍有效旧asset+decision，校验其预后处理/词表/阈值/后端/坐标闭包；新operation记录回退引用。软件二进制回退、数据/标签修订、模型用途撤回分别操作；不重算旧hash、不复活撤回资格、不改机判/放行/设备命令。旧报告保留旧reader；迁移器dry-run后创建新修订，不原地覆盖。部署动作归宿主，Unknown不能静默加载磁盘旧模型。

### 7.4 参数学习闭环（L1–L4）

本节描述 AI 检测参数的"越用越优"体系，对标 Mirtec Smart Learning"减少 90% 人工调参"目标。四层分别独立，每层可单独部署。

**参数来源与缺省口径（与 §3 同规格，适用本节全部四层）。** 本节出现的任何数值阈值、比例、窗口和样本规模都分两类，不得混写：

| 类别 | 本节示例 | 生效条件 |
|---|---|---|
| **模块工程硬界**（防滥用/资源封口） | 搜索样本上限、trial 总数上限、试产板数上限、统计窗口上限、PSI/KS 计算的最小样本量 | 由本轮技术判断冻结并写死，实现即拒绝越界值；**不**代表实测处理能力、SDK 限制或客户容量/节拍目标 |
| **客户过程目标**（工艺门槛/触发门） | 粗筛比例、早停无改善次数、L2 统计窗口、PSI 触发门、试产板数、过程能力门槛、连续无改善轮数 | **必须**由已采纳的用途 Profile 逐项给定；Profile 缺该字段时该判定为 `NotEvaluated`，**不**套用本节示例值，**不**默认成 0 或"通过" |

未采纳 Profile 时，模块只执行诊断性观察并把结果记为 `NotEvaluated`，不产出自动建议、不触发 L1 任务、不产生 `MeetsThreshold=true` 的适应结论。示例值不得被实现者当作已批准门槛：`Cpk` 门槛尤其如此——本平台 `OPEN-GATES` D-04 明确质量与性能 Profile 待输入、不能由竞品或行业经验值反推，故本节不写死具体 Cpk 数值。

各层的 Profile 字段名与取值域见 §7.4.6；§7.4.1–§7.4.4 出现的具体数字一律读作**该字段的工程示例**，实现时以 Profile 为准。

#### 7.4.1 L1 — 离线参数搜索（有界推荐）

**职责**：对给定的候选参数空间，在固定留出集上离线搜索最优参数，输出有界可解释的推荐值。

**算法**：Optuna / Hyperband（TPE + Successive Halving 二阶段）。
- 两阶段比例由 Profile `L1.ScreeningSampleRatio` 给出（工程示例 5%）；Profile 未采纳时只做全量单阶段搜索或整体记 `NotEvaluated`，不默认按该比例粗筛
- 早停由 Profile `L1.EarlyStopTrialsWithoutImprovement` 给出（工程示例 20 次 trial 无改善）；未采纳时不启用早停，改由 `L1.MaxTrials` 总数上限封口（工程硬界，见上表）
- 搜索结果写入不可变 `ParameterSuggestion`，携带：推荐值、置信区间、搜索样本数、搜索算法版本、评估指标

**实现边界**：
- 搜索在独立后台 worker 执行，不阻断生产检测线程
- 搜索结果是**建议草稿**，不自动写入生产配置
- 调用方（`parameter-editor` 模块 / 人工确认）确认后才写入配置，经 `storage-database` 持久化

```csharp
public sealed record ParameterSuggestion(
    string ParameterSetId,
    ImmutableDictionary<string, double> RecommendedValues,
    ImmutableDictionary<string, (double Lower, double Upper)> ConfidenceIntervals,
    int SamplesEvaluated,
    string SearchAlgorithmVersion,
    string EvaluationMetric,
    double MetricValue,
    string? LearningProfileId,        // 产出该建议时所用用途 Profile 的身份
    string? LearningProfileRevision,   // 其修订；Profile 未采纳时为 null
    ParameterSuggestionSource Source,  // L1 / L2 / L3Triggered
    DateTimeOffset CompletedAt);
```

`LearningProfileId`/`Revision` 随建议一并保留，使建议可按同一 Profile 与同一搜索版本复现（AGENTS.md 要求参数变更全程可 Replay）；Profile 未采纳时为 null，对应建议只能作为草稿候选、不得进入"生效"路径，且其复现依据是"无 Profile 的默认路径"本身，须在 `Source` 之外由 `EvaluationMetric` 与 `SamplesEvaluated` 完整说明。

`ParameterSuggestionSource` 封闭取值 `L1`（离线搜索）、`L2`（工程师修正挖掘）、`L3Triggered`（漂移触发后执行的 L1 搜索）；不新增第四种来源。

#### 7.4.2 L2 — 从工程师修正挖监督信号（核心竞争力）

**动机**：`parameter-editor` 模块记录了工程师每一次参数修改。这是隐式标注的监督信号——工程师修改参数是因为当前参数不好用。这是本平台独有的数据宝藏，训练平台竞品没有。

**处理流程**：
```
生产运行
  → 产生 (检测结果, 工程师确认/修改的参数, 最终判定)
  → ai-dataset-governance 持久化修改事件
  → 分析"哪些缺陷类型在哪些参数下漏检/误检"
  → 推导参数应调方向/量级
  → 写入新 ParameterSuggestion（L2 来源标记）
  → 工程师确认生效（三态：建议→草稿→生效）
```

**实现要求**：
- `ParameterModificationEvent` 必须携带：原参数值、修改后参数值、修改时间、对应生产批次 ID、修改人 principal
- 统计周期由 Profile `L2.AnalysisWindowBoards` / `L2.AnalysisWindowDays` 给出（工程示例：滑动窗口 500 块板或 7 天，取较早触发）；Profile 未采纳时不做周期聚合，事件只落 `ActiveLearningQueue` 待采纳，不产出 `ParameterLearningInsight`
- 分析结果写入 `ParameterLearningInsight`，不直接修改生产配置

```csharp
public sealed record ParameterModificationEvent(
    string BatchRunId,
    string ModifiedBy,
    ImmutableDictionary<string, double> OldValues,
    ImmutableDictionary<string, double> NewValues,
    DateTimeOffset ModifiedAt);

public sealed record ParameterLearningInsight(
    string InsightId,
    ImmutableArray<string> AffectedParameterIds,
    string AnalysisWindowDescription,
    int SamplesAnalyzed,
    string Direction,            // "increase" | "decrease" | "range-narrow"
    double SuggestedDelta,
    double Confidence,
    DateTimeOffset GeneratedAt);
```

#### 7.4.3 L3 — 在线漂移监控与触发

**职责**：监控生产检测特征分布的时间漂移（光源衰减、钢网磨损、批次材料变化），在漂移超过阈值时触发 L1 重优化。

**检测方法**：PSI（Population Stability Index）+ KS 检验。轻量统计，不需要 GPU。
- 采样频率由 Profile `L3.ObservationIntervalBoards` 给出（工程示例：每 100 块板一次）；未采纳时不做周期观察
- 触发门由 Profile `L3.PsiWarningThreshold` / `L3.PsiCriticalThreshold` 给出（工程示例：0.25 警告 / 0.5 触发重优化）；两个门都必须来自 Profile，缺任一则该层只记录原始 PSI/KS 数值并标 `NotEvaluated`，不产生 `DriftLevel.Warning` 或 `Critical`，不触发 L1
- PSI 的最小样本量是工程硬界（见上表），样本不足时该次观察为 `NotEvaluated`，不按小样本给出稳定/不稳定结论

```csharp
public enum DriftLevel { NotEvaluated, Stable, Warning, Critical }

public sealed record DriftObservation(
    string FeatureSetId,
    DriftLevel Level,
    double PsiValue,
    double KsStatistic,
    int SamplesInWindow,
    DateTimeOffset ObservedAt,
    string? TriggeredL1TaskId);
```

**实现边界**：
- 漂移观察只写 `DriftObservation`，不自动修改生产参数
- 触发 L1 任务需要用途 Profile 明确允许 `AutoTriggerL1: true`（见 §7.4.6）
- 漂移统计引用的基准分布从冻结的 `GoldenDatasetSnapshot` 计算
- 门槛未采纳、样本不足或 PSI/KS 无法计算时，`Level=NotEvaluated`；`DriftLevel.Stable` 只在两门均已采纳且实测低于 Warning 门时成立，**不得**用"未观测"冒充"稳定"

#### 7.4.4 L4 — 新物料自适应闭环（终态）

**职责**：新型号/新物料导入时，自动生成初始参数 → 试产 → L2 反馈微调 → 人工仅在越线时介入。

**流程**：
```
新物料导入
  → L1 搜索初始参数（基于类似物料的历史参数作起点）
  → 试产 Profile.L4.TrialBoardCount 块板（trial run，仅供调参，不入正式生产报表）
  → L2 分析试产结果，生成微调建议
  → 若 Profile.L4.ProcessCapabilityThreshold 与 Profile.L4.MissRateThreshold 均已采纳
    且实测值满足 → 标记"可推荐生效"（仍等人工批准）
  → 若门槛未采纳：判定为 NotEvaluated，不产生 MeetsThreshold=true 的结论
  → 若不满足：提示需要更多试产或人工介入
```

**试产规模与门槛的来源**：试产板数由 `Profile.L4.TrialBoardCount` 给出（工程示例 50 块板；工程硬界 `L4.TrialBoardCountLimit` 为上限），不得写死；过程能力门槛与漏检门槛必须由 `Profile.L4.ProcessCapabilityThreshold` / `Profile.L4.MissRateThreshold` 给出，**本节不写死 Cpk 数值**——OPEN-GATES D-04 明确质量 Profile 待输入、不得由行业经验值或竞品反推。门槛未采纳时 `AdaptationRun.ThresholdEvaluated=false`、`MeetsThreshold=false`，`Status` 停在 `InProgress` 并投影 `NotEvaluated`；"未判定"与"判定不通过"是不同事实，不得用 `NeedsIntervention` 表达前者（见下条护栏与 §7.4.6）。

**护栏**（必须保留，对标 §1A 三态仲裁的安全性要求）：
- 所有自动建议仍走"建议→草稿→生效"三态，不静默写入生产
- 试产结果和调整依据写入 `AdaptationEvidence`，完整可审计
- 连续无改善轮数由 Profile `L4.MaxIterationsWithoutImprovement` 给出（工程示例 3 轮）；未采纳时不自动停止，只在达到工程硬界 `L4.MaxAdaptationIterations` 时停止并报告需要人工介入
- 物料 ID 必须是已在 `model-assets` 注册的新物料，不能对未知物料自动操作

```csharp
public sealed record AdaptationRun(
    string AdaptationId,
    string MaterialId,
    string BaseMaterialId,      // 用于起点参数的类似物料
    int TrialBoardCount,
    ImmutableArray<ParameterSuggestion> L1Suggestions,
    ImmutableArray<ParameterLearningInsight> L2Adjustments,
    double? AchievedCpk,        // 未测得或门槛未采纳时为 null，不以 0 冒充
    double? ProcessCapabilityThreshold,  // Profile 采纳值；未采纳为 null
    double? MissRateThreshold,            // Profile 采纳值；未采纳为 null
    bool MeetsThreshold,        // 仅两门槛均已采纳且实测满足时为 true
    bool ThresholdEvaluated,    // 门槛是否已采纳并完成判定；false 时 MeetsThreshold 必为 false
    int L2IterationsWithoutImprovement,
    AdaptationStatus Status,    // InProgress | PendingApproval | NeedsIntervention
    DateTimeOffset LastUpdated);
```

`ThresholdEvaluated=false` 表示门槛未采纳或实测不足以判定；此时 `MeetsThreshold` 恒为 false，`Status` 不得据"未达标"推进为 `NeedsIntervention`（那是"判定不通过"，与"未判定"是不同事实），而是停在 `InProgress` 并投影 `NotEvaluated`。

#### 7.4.5 L1-L4 与三态仲裁的关系

```
ai-inference (三态仲裁)
  NeedsHuman → human-review → 人工结论
  NeedsSampling → ai-dataset-governance (L2 采样队列)

ai-dataset-governance (L1-L4)
  L2 分析工程师修正 → ParameterSuggestion → parameter-editor (人工确认) → 生效
  L3 漂移监控 → 触发 L1 搜索 → ParameterSuggestion
  L4 新物料适应 → AdaptationRun → 人工批准 → 生效
```

**关键约束**：ai-inference 的 NeedsSampling 结果进入本模块的 `ActiveLearningQueue`；本模块的 L2 分析使用 `parameter-editor` 记录的修改历史；两个模块通过公开端口交互，不直接耦合。

#### 7.4.6 L1–L4 用途 Profile 字段契约

本节只定义字段名、类型、取值域与缺省语义，**不定义数值**。每个字段由已采纳的用途 Profile 给出并随运行记录其 Profile 身份与修订；未采纳的字段一律为 null，触发该判定的结果为 `NotEvaluated`。

```csharp
public sealed record LearningLoopProfile(
    string ProfileId, string ProfileRevision,
    L1Profile? L1, L2Profile? L2, L3Profile? L3, L4Profile? L4);

public sealed record L1Profile(
    int MaxTrials,                        // 工程硬界：>0，总 trial 上限
    double? ScreeningSampleRatio,        // 客户目标：(0,1)；null=不做两阶段
    int? EarlyStopTrialsWithoutImprovement); // 客户目标：>=1；null=不启用早停

public sealed record L2Profile(
    int? AnalysisWindowBoards,           // 客户目标：>=1；与 AnalysisWindowDays 至少一项非 null
    int? AnalysisWindowDays);            // 客户目标：>=1；两者皆 null=不做周期聚合

public sealed record L3Profile(
    int? ObservationIntervalBoards,       // 客户目标：>=1；null=不做周期观察
    double? PsiWarningThreshold,         // 客户目标：有限且 >=0；null=不产生 Warning
    double? PsiCriticalThreshold,        // 客户目标：有限且 >=0 且 > PsiWarningThreshold；null=不产生 Critical
    bool AutoTriggerL1);                 // 客户目标：显式布尔；true 才允许自动触发 L1

public sealed record L4Profile(
    int? TrialBoardCount,                // 客户目标：>=1，且 <= 工程硬界 L4.TrialBoardCountLimit
    double? ProcessCapabilityThreshold,  // 客户目标：有限 >0；null=不判定 Cpk 门槛
    double? MissRateThreshold,           // 客户目标：有限 [0,1]；null=不判定漏检门槛
    int? MaxIterationsWithoutImprovement);// 客户目标：>=1；null=不因无改善自动停止
    int TrialBoardCountLimit,            // 工程硬界：>0
    int MaxAdaptationIterations);        // 工程硬界：>0
```

字段语义与缺省行为：

| 字段 | 缺省（Profile 未采纳该层/该字段） | 生效后的行为 |
|---|---|---|
| `L1.ScreeningSampleRatio` | 不做两阶段粗筛，只做单阶段搜索 | 按该比例粗筛后全量精化 |
| `L1.EarlyStopTrialsWithoutImprovement` | 不启用早停，仅由 `MaxTrials` 封口 | 连续该次数无改善即停 |
| `L2.AnalysisWindowBoards`/`Days` | 不做周期聚合，事件只入 `ActiveLearningQueue` | 两者取较早触发者聚合 |
| `L3.ObservationIntervalBoards` | 不做周期漂移观察 | 按间隔计算 PSI/KS |
| `L3.PsiWarningThreshold` | 只记录原始 PSI/KS 数值，不判 Warning | 达门则写 `DriftLevel.Warning` |
| `L3.PsiCriticalThreshold` | 同上，不判 Critical，不触发 L1 | 达门且 `AutoTriggerL1=true` 才触发 L1 任务 |
| `L3.AutoTriggerL1` | false | 达 Critical 只告警，须人工发起 L1 |
| `L4.TrialBoardCount` | 不做自动试产 | 按该规模试产 |
| `L4.ProcessCapabilityThreshold` / `MissRateThreshold` | `ThresholdEvaluated=false`，`MeetsThreshold=false` | 两门均采纳且实测满足才 `MeetsThreshold=true` |
| `L4.MaxIterationsWithoutImprovement` | 不因无改善自动停止，仅由 `MaxAdaptationIterations` 封口 | 达该轮数自动停止并报人工介入 |

校验规则：非 null 的比例必须在声明域内（比例 `(0,1)`、门槛有限且非负、Cpk 门 `>0`、漏检门 `[0,1]`、板数/轮数 `>=1`）；`PsiCriticalThreshold` 必须严格大于 `PsiWarningThreshold`，否则该 Profile 字段组合非法并拒绝接纳（不静默取其一）。工程硬界字段（`MaxTrials`、`TrialBoardCountLimit`、`MaxAdaptationIterations`）缺失时按 §3 口径拒绝，不使用对象默认值。

本契约不改变 §3 的预算口径，也不引入第二套 Profile 机制：用途 Profile 的身份/修订与其余字段由各层消费方按既有 Owner 规则冻结，本节只固定 L1–L4 需要的字段名与缺省语义。

## 8. 可选 WPF 公共接入与页面实施卡

`Asun.Modules.AiDatasetGovernance.Wpf`依Core，net10.0-windows/UseWPF，本机DevExpress25.2.3 direct Reference，不下载NuGet。控件名 `GovernanceControl`，不是产品Shell，不需要隐藏窗口初始化业务。UI绑定含以下完整公开契约；ImmutableArray项仅值/string，data权限在投影端口而非列表隐藏实现。

```csharp
public sealed record GovernanceRow(string Id, string ParentId, string Kind,
    string Version, string Hash, string Scope, string StatusKey, string GapKey,
    PreviewEvidenceRef? Evidence);
public sealed record MetricRow(string Name, string Stratum, long Numerator,
    long Denominator, double? Value, string Unit, string ReasonKey);
public sealed record GovernanceProjection(string OperationId, long Generation,
    long Sequence, OperationState State, ImmutableArray<GovernanceRow> Rows,
    ImmutableArray<MetricRow> Metrics, string StatusKey, bool CanSubmit,
    bool CanCancel, bool CanLookup);
public interface IGovernanceProjectionPort {
    Task<GovernanceProjection> ReadAsync(string operationId,
        AuthorizationQuery authorization, CancellationToken token);
}
public interface IGovernanceText {
    string CultureName { get; }
    string Get(string resourceKey);
}
public sealed record GovernanceBinding(GovernanceSession Session,
    RootSlot Owner,
    IGovernanceProjectionPort Projection, AuthorizationQuery Authorization,
    IGovernanceText Text, int MaxRows, int MaxMetrics, int RefreshMs,
    bool SupportsTraining, bool SupportsUsage,
    EvidencePreviewBinding? EvidencePreview,
    Func<EvaluationRequest> BuildEvaluation, Func<TrainingRequest> BuildTraining,
    Func<UsageIntent> BuildUsage);
// GovernanceBinding、EvidencePreviewBinding、桥及以下控件位于Wpf namespace；
// 其余值/投影/来源契约位于Core，不依赖WPF。
public sealed class GovernanceControl : System.Windows.Controls.UserControl {
    public Task BindAsync(GovernanceBinding binding, CancellationToken token);
    public Task UnbindAsync(int observationTimeoutMs);
    public void SetLanguage(IGovernanceText text);
    public GovernanceProjection? Projection { get; }
    public System.Windows.Input.ICommand PrecheckCommand { get; }
    public System.Windows.Input.ICommand EvaluateCommand { get; }
    public System.Windows.Input.ICommand TrainCommand { get; }
    public System.Windows.Input.ICommand UsageCommand { get; }
    public System.Windows.Input.ICommand CancelCommand { get; }
    public System.Windows.Input.ICommand LookupCommand { get; }
    public System.Windows.Input.ICommand ResetLayoutCommand { get; }
    public Task<PreviewObservation> SelectEvidenceAsync(string rowId,
        int observationTimeoutMs, CancellationToken waitToken);
    public Task<PreviewObservation> ClearEvidenceAsync(int observationTimeoutMs,
        CancellationToken waitToken);
    public Task<PreviewObservation> QueryEvidenceAsync(int observationTimeoutMs,
        CancellationToken waitToken);
}
public static class GovernanceText {
    public static IGovernanceText Create(string cultureName);
}
```

Bind只能UI线程调用且当前未绑定，引用/容量非法返回失败Task；Binding.Owner必须是Binding.Session所属未关闭slot；用Owner.StartBorrowed预留读取/Dispatcher工作，未预留不得启动Read。Build三个委托只生成未冻结输入，**禁止IO/副作用/耗时**；Precheck复用Core.Freeze，Evaluate/Train/Usage调用相同session.Start；不会从Grid可见行凑义务。命令真正可用性同时取决于状态、最新权限和输入预检，CanExecute不是授权证明。Usage按钮文字“提交审议请求”，不可“批准自动运行”；决定由Usage端口读取。

投影调用与Dispatcher呈现任务都保留原Task、generation和容量；RefreshMs≥100、MaxRows/MaxMetrics为正且受RootLimits/工作字节限制；只允许一个在途读取，后续刷新合并成一个pending标记，不每次tick新Task。返回后校验sequence、generation、operation/权限，再有界替换投影。Unbind退订且停止新refresh，等待当前读取与Dispatcher投影退出；到期不丢原Task，slot移交root并确认，控件仅在预览和投影真实结束后显示已解绑；观察超时显示DG.PreviewClearUnknown，不写ResourcesReleased。窗口关闭/Unloaded不证明业务session已关闭；宿主另行RequestClose/CloseAsync。SetLanguage动态重投影文本，不启动业务、不重新计算结果；宿主提供三语资源，控件不另放语言入口。

### 8.1 1920×1080布局与高级联动

用固定1920×1080验证viewport并扣除任务栏/标题/状态栏；按可用client区横向约22%来源树、52%主体、26%详情，中心图片优先。DockLayoutManager+LayoutGroup固定首开布局；可调整面板但关键命令/状态保持可见，ResetLayout可恢复。左GridControl+TreeListView通过KeyFieldName=Id/ParentFieldName=ParentId组织快照→组→成员；中部GridControl/TableView列义务、真值、预测、纳排、失败及版本，选行通过§8.2.1显式宿主桥联动影像与原ROI证据；没有影像租约时显示“影像不可读”及查询入口，不占位假图。下方ChartControl显示分子/分母、coverage与Acquired/Synthetic差异，禁止用缩短y轴夸大小分差。右PropertyGridControl.SelectedObject为只读参数投影，开发者显式设置ReadOnly=true并在真实WPF验证不可编辑（随附XML的value说明与名称有歧义，不盲抄）；草稿使用独立输入页，不改已发布记录。

Grid的ItemsSource/SelectedItem/AllowEditing及BeginDataUpdate/EndDataUpdate已核本机25.2随附XML；batch更新try/finally解锁，不在每事件重建所有行。大数据使用分页投影、稳定row ID与有界影像缓存，显示“已显示x/总n”，筛选不得改变报告分母。Ctrl+F搜当前已授权投影，Enter预览，Esc仅退出编辑/面板，取消必须明确按钮；Tab依次来源→主表→证据→详情→安全命令，危险提交无快捷误触。状态不只颜色；版本/hash可复制但路径/标签读权仍控制。批量预检显示每项失败及未完成范围，不隐藏冲突以制造“全选成功”。

| 资源键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| DG.Precheck | 预检 | 預檢 | Check inputs |
| DG.Evaluate | 运行评价 | 執行評估 | Run evaluation |
| DG.Train | 创建训练候选 | 建立訓練候選 | Train candidate |
| DG.Usage | 提交审议请求 | 提交審議請求 | Request review |
| DG.Cancel | 请求停止 | 請求停止 | Request stop |
| DG.Unknown | 状态待查 | 狀態待查 | Status unknown |
| DG.DrainUnknown | 停止未确认，请查询原操作 | 停止未確認，請查詢原作業 | Stop unconfirmed. Query the operation. |
| DG.MissingDenominator | 分母不足，不能判断资格 | 分母不足，無法判定資格 | Insufficient denominator for qualification |
| DG.Released | 资源已归还 | 資源已歸還 | Resources released |
| DG.PreviewOpen | 预览证据 | 預覽證據 | Preview evidence |
| DG.PreviewClear | 清空预览 | 清空預覽 | Clear preview |
| DG.PreviewSynthetic | 合成样本 | 合成樣本 | Synthetic sample |
| DG.PreviewUnavailable | 无可读影像证据 | 無可讀影像證據 | No readable image evidence |
| DG.PreviewDenied | 无影像读取权限 | 無影像讀取權限 | Image access denied |
| DG.PreviewOpening | 正在读取影像 | 正在讀取影像 | Reading image |
| DG.PreviewPresented | 预览已更新 | 預覽已更新 | Preview updated |
| DG.PreviewClearing | 正在清空影像 | 正在清空影像 | Clearing image |
| DG.PreviewClearUnknown | 清空未确认，请查询原预览 | 清空未確認，請查詢原預覽 | Clear unconfirmed. Query the preview. |
| DG.PreviewRevoked | 读取权限已撤回，正在清空 | 讀取權限已撤回，正在清空 | Access revoked. Clearing the image. |
| DG.PreviewReleased | 预览已清空，租约已归还 | 預覽已清空，租約已歸還 | Preview cleared. Lease returned. |

所有其它标题/列/状态/错误/参数/图例/tooltip按同资源体系扩展，缺key显示可定位资源错误，不把英文/AI宣传语当正常回退。SuperTip用于split、条件指标、资格/提交和资源未知的限制与恢复，持续可见的关键命令不藏进Flyout。DevExpress随附类型/方法读取是API依据，不是实际控件运行验收；dxdocs本轮无可调用入口，官方网站403，未宣称官网读取成功。

本模块随包提供GovernanceText.Create的基线三语资源，不要求宿主重新编译模块才能切语言；宿主可用自定义IGovernanceText覆盖术语，但必须覆盖完整key集合。Create只接受zh-CN/zh-TW/en-US，未知culture抛ArgumentException，不从全局线程Culture猜。状态key统一DG.State.<OperationState枚举名>，错误key统一DG.Error.<三位编号>，参数key为DG.Parameter.<Budget字段名>。除上表命令外，其余首版key/三语正文固定如下，tooltip用单独key，禁止把错误码/枚举名当正常文案：

| key（均加DG.前缀） | zh-CN | zh-TW | en-US |
|---|---|---|---|
| Title | 数据与模型治理 | 資料與模型治理 | Data and model governance |
| Dataset/Labels/Evaluation/Usage | 数据集/标签/评价/用途 | 資料集/標籤/評估/用途 | Dataset/Labels/Evaluation/Usage |
| Lookup/ResetLayout | 查询回执/恢复布局 | 查詢回執/還原版面 | Query receipt/Reset layout |
| Column.Id/Version/Hash/Scope | 标识/版本/摘要/范围 | 識別碼/版本/摘要/範圍 | ID/Version/Hash/Scope |
| Column.Status/Gap/Origin | 状态/缺口/来源 | 狀態/缺口/來源 | Status/Gap/Origin |
| Column.Truth/Prediction | 真值/预测 | 真值/預測 | Ground truth/Prediction |
| Column.Numerator/Denominator/Value/Unit | 分子/分母/数值/单位 | 分子/分母/數值/單位 | Numerator/Denominator/Value/Unit |
| ImageUnavailable/NotComputable | 影像不可读/不能计算 | 影像無法讀取/無法計算 | Image unavailable/Not computable |
| State.Accepted/Validating/Running | 已接纳/正在校验/正在执行 | 已接納/正在驗證/正在執行 | Accepted/Validating/Running |
| State.Completing/Draining/DrainUnknown | 正在提交/正在排空/停止未确认 | 正在提交/正在排空/停止未確認 | Completing/Draining/Stop unconfirmed |
| State.Drained/ResourcesReleased | 已排空/资源已归还 | 已排空/資源已歸還 | Drained/Resources released |
| State.Succeeded/Rejected/Cancelled/Failed/Unknown | 已完成/已拒绝/已取消/执行失败/状态待查 | 已完成/已拒絕/已取消/執行失敗/狀態待查 | Completed/Rejected/Cancelled/Execution failed/Status unknown |
| Error.001/002/003/004 | 输入无效/版本不支持/权限不足/来源不可读 | 輸入無效/版本不支援/權限不足/來源無法讀取 | Invalid input/Unsupported version/Permission denied/Source unavailable |
| Error.005/006/007/008 | 内容不一致/数据分组冲突/真值不足/资源超限 | 內容不一致/資料分組衝突/真值不足/資源超限 | Content mismatch/Group conflict/Insufficient ground truth/Resource limit exceeded |
| Error.009/010/011/012 | 已请求停止/执行超时/接口执行失败/提交状态待查 | 已請求停止/執行逾時/介面執行失敗/提交狀態待查 | Stop requested/Execution timed out/Adapter failed/Commit status unknown |
| Error.013/014/015/016 | 方法不匹配/分母不足/用途已撤回/重复操作内容冲突 | 方法不符/分母不足/用途已撤回/重複作業內容衝突 | Method mismatch/Insufficient denominator/Usage withdrawn/Conflicting repeated operation |
| Parameter.MaxItems/MaxTextUtf8Bytes/MaxCanonicalBytes/MaxWorkingBytes | 项目上限/文字字节上限/编码字节上限/工作区字节上限 | 項目上限/文字位元組上限/編碼位元組上限/工作區位元組上限 | Item limit/Text byte limit/Encoded byte limit/Working byte limit |
| Parameter.MaxDpCells/MaxParallelism/WorkTimeoutMs/CleanupTimeoutMs | 距离计算单元上限/并发上限/执行期限(ms)/清理观察期限(ms) | 距離計算單元上限/並行上限/執行期限(ms)/清理觀察期限(ms) | Distance cell limit/Parallel limit/Work deadline(ms)/Cleanup observation deadline(ms) |
| Tip.Split | 同源数据不能跨训练和测试；更正后生成新划分 | 同源資料不能跨訓練與測試；更正後建立新劃分 | Related data must stay in one partition. Changes create a new split. |
| Tip.Metric | 请同时查看分母、拒识和未完成项 | 請同時查看分母、拒識與未完成項 | Check the denominator, abstentions and incomplete items. |
| Tip.Usage | 报告完成不等于生产用途获批 | 報告完成不代表生產用途已核准 | A completed report does not grant production approval. |
| Tip.Recovery | 请查询原操作；停止未确认前不要释放借用资源 | 請查詢原作業；停止未確認前不要釋放借用資源 | Query the original operation. Keep borrowed resources until stop is confirmed. |

表内斜线表示对应各独立key/文案，不是一个串，字符串自身含(ms)保持单位；扩展新的可见字段必须增同一资源集合。Endpoint名称是机器key，不在UI直接显示：recall/precision/fpr/cer等分别以“召回率/精确率/误报率/字符错误率”“召回率/精確率/誤報率/字元錯誤率”“Recall/Precision/False positive rate/Character error rate”按key投影，额外具名端点显示该方法定义的自然名称并固定单位/分母。未知端点先DG-002，不能在UI编“准确率”。

#### 8.1.1 全模块操作者任务流与新增字段

数据工程师：选已授权来源→预检引用/标签/同源分组→查看分组建议及锁定留出差异→显式采用成新Split修订→发布研究快照。训练工程师：选已发布snapshot/精确toolchain/config→核Train/Validation成员、类表/处理差异、batch/LR/尾补齐/选优/资源摘要→预检→显式创建候选→查看原operation更新/validation/候选→请求停止或查询→将完整候选送原用途审议。结果审阅者：选原不可变报告→查看全部分母/拒识/缺项及只读原图/ROI→关联原资格/阶段决定；回退仅提交具名旧模型/OwnerDecision，不直接激活。角色名称是任务语义，实际能力仍由原授权Action/Resource给，不能因UI角色标签自授权限。

训练/配置草稿页是可选工程页，PropertyGrid仅编辑尚未封存的本方草稿；原Configuration由Owner封存，新训练前其精确ref/hash重新预检。生产工作台和只读审阅嵌入不显示训练/改参入口，Core/Adapter仍执行权限检查。失败回到原operation查询和明确恢复建议，Unknown/DrainUnknown期间禁同内容重开；无读权时不显示源文字/缩略图。TrainingSpec/Core控制链沿原参数合同，不由WPF控件自动改seed、batch或EarlyStop。

参数目录在原三语资源中增加以下独立键，不显示ModelType/Schema等实现文字让操作员自行判断；完整机器参数在受权工程详情中可复制，值/单位仍是原不可变值。

| 键 | zh-CN | zh-TW | en-US |
|---|---|---|---|
| DG.TrainingConfig | 训练配置 | 訓練設定 | Training configuration |
| DG.Epochs | 最大轮数 | 最大輪數 | Maximum epochs |
| DG.BatchSize | 批大小 | 批次大小 | Batch size |
| DG.BatchMultiplier | 梯度累积倍数 | 梯度累積倍數 | Batch multiplier |
| DG.LearningRate | 学习率 | 學習率 | Learning rate |
| DG.Seed | 随机种子 | 隨機種子 | Random seed |
| DG.Validation | 训练验证集 | 訓練驗證集 | Validation set |
| DG.FinalCandidate | 最后完整候选 | 最後完整候選 | Last complete candidate |
| DG.BestCandidate | 验证集选优候选 | 驗證集選優候選 | Validation-selected candidate |
| DG.NoCandidate | 无满足约束的候选 | 無符合限制的候選 | No candidate meets the constraints |
| DG.TailRepeat | 尾批补齐重复，不增加独立样本 | 尾批補齊重複，不增加獨立樣本 | Repeated tail items do not add independent samples |
| DG.TrainingNotResumable | 本次训练不能从中断点恢复 | 本次訓練無法從中斷點恢復 | This training cannot resume from the interrupted step |

其它typed参数使用原参数目录的三语标题/单位/限制/恢复资源，缺任何语言的键则草稿预检失败，不临时把参数英文名或异常原文当UI文本。SuperTip说明尾补齐、Best口径、仅新操作及候选未获生产用途；关键取消/查询持续可见，不藏菜单。未来U11在同两个STA Host核三语/键盘顺序、配置只读/草稿隔离、Training/Usage权限、数据页筛选不改分母及Unknown禁止重复派发；本轮不冒真实UI验收。

### 8.2 两个STA宿主与验收

### 8.2.1 只读证据预览桥（U1；0.2.2窄修）

本切片选用**显式受控宿主端口**，不把正在修订的viewport签名包装成已完成实现。只读参考[viewport §3.5/§4.2](../viewport/DEVELOPMENT-GUIDE.md#35-session运行态和端口的闭合模块契约)：ImageSourceDescriptor/OverlayLayer、IFramePort/IFrameLease、IViewportSession.AttachAsync/UpdateAsync/DisposeAsync以及Returned/Pending/Unknown租约语义。生产宿主的Bridge在其viewport接线范围映射实际版本；本模块只调用以下固定边界，不直接操作HALCON/native/ROI编辑、质量放行或产品参数。所有版本/字节/坐标均来自所选行的精确证据；不能按当前路径或最新ROI寻找“类似图片”。

Preview值/Row.Evidence/GovernanceBinding仅为已限定接收的U1进程内投影与接线，不修改C1/C2已接收算法、请求/模型Binding编码或事实Owner，不持久化为新产品Schema。0.2.2-prep是指导修订号，无已发布U1程序集/消费者，不作二进制Patch兼容声明；正式发布仍按§13 SemVer规则。

```csharp
// Core：只读值、来源与租约；WPF UI类型不进入这里。
public sealed record PreviewRoiRef(RegionRef Region, string SchemaId, long Bytes);
public sealed record PreviewEvidenceRef(string MemberId, RevisionRef Image,
    long ImageBytes, string ImageSchemaId, int Width, int Height, long StrideBytes,
    string Face, string CoordinateRevision, RevisionRef? ValidDomain,
    ImmutableArray<PreviewRoiRef> Rois, Origin Origin);
public sealed record PreviewLimits(long MaxSourceBytes, long MaxRetainedBytes,
    int MaxWidth, int MaxHeight, int MaxRois, int WorkTimeoutMs, int ClearObservationMs);
public sealed record PreviewSelectionRequest(string OperationId, long OperationGeneration,
    long BindingEpoch, long SelectionEpoch, string RowId, PreviewEvidenceRef Evidence,
    AuthorizationQuery Authorization, PreviewLimits Limits);
public sealed record PreviewPermit(string ReceiptId, string Principal, string Tenant,
    string Scope, string PolicyRevision, string Fence, DateTimeOffset ValidUntilUtc);
public enum PreviewAuthorityState { Revoked = 1, Expired = 2, Gap = 3, Closed = 4 }
public sealed record PreviewAuthorityNotice(PreviewAuthorityState State, string Fence);
public interface IPreviewPayload { } // opaque host-owned readonly payload; no SDK handles
public sealed record PreviewReleaseReceipt(string LeaseId, string ReleaseId,
    bool Released, string? ErrorCode);
public interface IPreviewEvidenceLease {
    string LeaseId { get; }
    PreviewEvidenceRef Evidence { get; }
    PreviewPermit Permit { get; }
    IPreviewPayload Payload { get; }
    Task<PreviewAuthorityNotice> AuthorityChanged { get; }
    bool CanDisclose(PreviewSelectionRequest request);
    Task<PreviewReleaseReceipt> ReleaseAsync(string releaseId, CancellationToken token);
    Task<PreviewReleaseReceipt> QueryReleaseAsync(string releaseId, CancellationToken token);
}
public sealed record PreviewOpenResult(IPreviewEvidenceLease? Lease, string? ErrorCode);
public interface IPreviewEvidenceSource {
    Task<PreviewOpenResult> OpenAsync(PreviewSelectionRequest request, CancellationToken token);
}
public enum PreviewState { Empty = 1, Opening = 2, Presenting = 3, Presented = 4,
    Clearing = 5, Unavailable = 6, Denied = 7, DrainUnknown = 8, Released = 9 }
public sealed record PreviewObservation(PreviewState State, long BindingEpoch,
    long SelectionEpoch, string? DisplayId, PreviewEvidenceRef? Evidence,
    bool ResourcesReleased, string? ErrorCode);
// Wpf：可嵌入View和只读显示桥，不是viewport SDK的新签名。
public sealed record PreviewDisplayRequest(PreviewSelectionRequest Selection, string DisplayId);
public sealed record PreviewShowReceipt(string DisplayId, long BindingEpoch,
    long SelectionEpoch, bool Presented, long PresentationSequence, string? ErrorCode);
public sealed record PreviewClearRequest(long BindingEpoch, long SelectionEpoch,
    string DisplayId, string ClearId, string ReasonKey);
public sealed record PreviewCloseRequest(long BindingEpoch, string CloseId);
public sealed record PreviewDetachReceipt(long BindingEpoch, long SelectionEpoch,
    string DisplayId, bool Detached, bool NoFurtherReads, bool ViewClosed,
    long PresentationSequence, string? ErrorCode);
public interface IEvidencePreviewBridge {
    System.Windows.FrameworkElement View { get; }
    Task<PreviewShowReceipt> ShowAsync(PreviewDisplayRequest request,
        IPreviewEvidenceLease lease, CancellationToken token);
    Task<PreviewDetachReceipt> ClearAsync(PreviewClearRequest request, CancellationToken token);
    Task<PreviewDetachReceipt> QueryClearAsync(PreviewClearRequest request, CancellationToken token);
    Task<PreviewDetachReceipt> CloseAsync(PreviewCloseRequest request, CancellationToken token);
}
public sealed record EvidencePreviewBinding(IPreviewEvidenceSource Source,
    IEvidencePreviewBridge Bridge, AuthorizationQuery Authorization, PreviewLimits Limits);
```

`GovernanceBinding.EvidencePreview`可空；null或row.Evidence=null时显示DG.PreviewUnavailable且不调用Open。它不是所有Host默认路径：§8.2.2两个正常Host明确提供实际合成像素/原ROI。Bridge每binding独占，View必须未有VisualParent，绑定在中心影像ContentControl；不得挂一个View到两窗口。Bridge.View get只创建/返回UI对象，无IO；源和Bridge由宿主借出，内部预览Owner强持到真实Close/release完成，不能在Unbind观察超时后dispose。PreviewEvidenceRef须原快照MemberId/证据hash/face/坐标一致，Roi.Region坐标相同且原ROI完整schema/hash明确；ValidDomain只读引用可空表示已批准全幅，不冒有效域未知。显示不新增标签、ROI或生产事实。

**有界显示和权限**：limits全部正且≤根/宿主预算；先checked图幅/stride/ImageBytes/ROI总bytes与深复制尺寸再Open，不先读图hash再限额。Open请求purpose必须显式preview-evidence，当前principal/tenant/scope/policy由EvidencePreviewBinding供给；不是沿用evaluate许可。源在实际读取前核当前读权和精确源闭包，完整EOF核image/ROI长度/hash，返回Lease成功时ErrorCode=null，否则Lease=null+错误；半构造资源未退出时Open原Task不得提前返回失败。Lease拥有稳定payload和当前Permit，来源Version/Hash/内容不可换。CanDisclose是有界、无IO的当前watch/fence/期限检查，不获得新权限；source必须提供可信连续撤权watch或等价受保护本地读屏障，无此能力生产源返回Denied。AuthorityChanged在撤销/到期/缺口时完成，正常release时以Closed完成，不能丢掉订阅Task。Bridge必须在Dispatcher**实际挂入影像之前**再调用CanDisclose，同样请求/代次不符不呈现；缓存许可不延长期限。期限到达由预览Owner的单个根持有定时Task触发清空，源watch断连/Gap与撤权同样处理。

**选择、显示、替换**：DataControlBase.SelectedItem只提取RowId，调用同一SelectEvidenceAsync入口；API从当前已授权Projection复制row.Evidence与operation/generation，使用单调BindingEpoch/SelectionEpoch。重复同选择正在进行时复用原观察，不能多次Open。切行/筛选移除当前行/换generation/撤权/关闭立即在模块自身UI层遮住旧View（遮罩不等清空ACK），停止旧呈现，至多保留一个latest pending row。旧Open/Show未退出时禁止启动新Open；迟到Open成功先把lease放入已登记Owner，再按旧epoch清理，绝不丢弃成功资源。旧Show即使迟到Presented也不撤新遮罩，仍对该DisplayId执行原Clear。清空、原Show退出、lease.Release确认后才允许新选择Open；不把新旧图/ROI叠加或借同名坐标拼图。

**真实清空与保持**：Show的Presented仅确认该DisplayId对应投影已由Dispatcher应用，不证明像素已被屏幕真实显示、GPU栅栏/渲染已完成或现场视觉正确；这些真实WPF/渲染事实留后续gate。**不归还租约**；Bridge仍读payload/纹理/ROI直到Clear或Close确认。ClearId在首次清理固定，Clear只针对完整binding/selection/DisplayId；迟到旧clear不得清掉新图。ACK必须Detached=true、NoFurtherReads=true、ErrorCode=null且原Show/Dispatcher/渲染Task已退出才允许Release；cleanup先发Clear/Close信号，确认NoFurtherReads后启动Release，再汇合watch/expiry，而不能先await AuthorityChanged(Closed)才调用Release（正常Closed由Release产生）。隐藏、从visual tree移除、Source=null或取消wait均不是该ACK。Clear返回Unknown/throw或原Task未退出时保持DrainUnknown和原lease；QueryClear只查询原clear，不再次Show/重建/重发清空副作用。Close关闭本bridge会话、等待全部渲染退出，ViewClosed=true和NoFurtherReads=true才允许关闭期间的payload归还；之后不能复用同bridge，需新binding。正常源Release只调用一次、保留原Task，Pending/Unknown仅QueryRelease；Released必须包含原LeaseId/ReleaseId且AuthorityChanged原watch已退出。业务primary错误与清理错误分别保留。

**根Owner与观察任务**：Bind在任何Open/Show/Dispatcher动作前通过§4.3.1的`Binding.Owner.ReserveBorrowedScope`一次取得11槽和MaxRetainedBytes，并调用scope.StartLifetime启动固定预览Owner生命周期；失败时不启动源/桥工作。所有stage通过scope.Start/CaptureProduced公开入口在预留额度内执行，WPF不读取Core私有ledger。旧StartBorrowed仍只用于单原投影/读取，不作为预览内部容量证明。Owner固定字段保存源/桥/View、请求/代次、原Task、lease、原clear/release/close ID、权限watch/expiry CTS及回执；原生命周期Completion只在原Task/接收门、最后Clear/Close/lease归还全部真实完成后返回ResourcesReleased=true，未决不完成。scope.Completion确认后才归还整批额度，root槽未释放不复用。

SelectEvidenceAsync/ClearEvidenceAsync/QueryEvidenceAsync的token和timeout只限制本次观察；返回DrainUnknown不取消原Task或清空引用。Unbind停新选择、遮罩→原Clear→lease Release/watch退出→Bridge.Close→全部原Task结束，才成功完成Unbind；有限观察到期不报成功，UnbindAsync抛TimeoutException，QueryEvidenceAsync可观察DrainUnknown，并调用slot.TransferToRoot，必须Ack.Accepted，root继续强持Owner/Bridge/View/payload及原Task。Clear.Unknown之后只有受预算显式QueryEvidence/Close观察，不后台无限重试。宿主保留同root恢复入口；没有ACK时仍由原host持有，禁止销毁借用对象。“UI看不到图”和“影像资源已归还”分别显示。预览owner资源独立于已完成评价Outcome.ResourcesReleased，不能后来的显示借用反向改写评价终态。

PreviewObservation.ResourcesReleased的作用域是该SelectionEpoch的影像/ROI/watch及对应阶段Task，不证明整个Bridge已Close或RootSlot已释放；Clear后可为true而binding继续接收新选择。最终Unbind还须Close原View并确认所有选择/投影Task结束。BindingEpoch、SelectionEpoch单调checked递增，溢出拒接纳；DisplayId/ClearId/ReleaseId/CloseId首次由Owner生成并固定，重查保留原ID。cleanup使用预留专用槽，停止新业务后仍可清理已接纳预览；不能因接纳停止拒绝清空而丢借用资源。

#### 可调用接线伪码：预留、接收、停止信号和汇合

以下是**WPF内部Owner的语义伪码**，scope/端口调用只用§4.2公开签名，不声称已有可编译产品实现。`owner`是Bind创建的单一有界记录：固定Source/Bridge/View/请求/lease、11个task字段、结果/错误两数组和一个latestPending；`owner.SignalCleanup()`只置关闭/清理标记、取消expiry CTS、发一个有界唤醒信号，无IO。`owner.RunAsync(scope)`是下面状态驱动器的唯一原Task，不是Bind Task，不await自己或父root的完成。`Need`语义为Check.Value非null才继续，否则记录Issues/停止（不调用未接纳delegate），不是隐藏产品工厂。

```text
Bind:
  owner = 固定记录（未启动任何IO/Task/Dispatcher，清理槽独立预留）
  scope = Need(binding.Owner.ReserveBorrowedScope(
      new BorrowedScopeLimits(5, 4, 1, 4096, preview.Limits.MaxRetainedBytes),
      owner, () => owner.SignalCleanup()))
  lifetime = Need(scope.StartLifetime(() => owner.RunAsync(scope)))
  owner强持lifetime.Original/Received；在预留内挂Bridge.View；Bind返回
  // 不等lifetime/scope.Completion/slot.Close，也不把Bind登记为lifetime。

选定固定request（由当前Projection/权限/代次复制，非任意外部草稿）:
  open = Need(scope.Start(BorrowedLane.Work, 0,
      () => source.OpenAsync(request, owner.WorkToken), result => {
          owner.OpenResult = result
          if (result.Lease == null) { 记录错误; 发清理信号; return; }
          owner.Lease = result.Lease // 先接管，即使已请求停止/代次过期
          owner.Watch = Need(scope.CaptureProduced(2, result.Lease.AuthorityChanged,
              notice => { owner.Notice = notice; owner.SignalCleanup(); }))
          // 原结果接收门完成登记后才能对外完成open.Received。
          // Work已停/选择过期时不启动expiry或Show，立即清理已有lease。
      }))
  驱动器继续处理停止/选择信号；open.Received完成后读取Owner状态
      // 不用串行await Open挡住清理；迟到lease仍由accept先接管。
  若允许继续:
      expiry = Need(scope.Start(BorrowedLane.Work, 3,
          () => 有限到Permit.ValidUntilUtc的原timer Task（独立expiry CTS，返回具名notice）, 
          notice => { owner.ExpiryNotice = notice; owner.SignalCleanup(); }))
      show = Need(scope.Start(BorrowedLane.Work, 1,
          () => bridge.ShowAsync(displayRequest, owner.Lease, owner.WorkToken),
          receipt => owner.ShowReceipt = receipt))
      show.Received完成时核当前epoch/permit和回执；Presented仅Dispatcher应用
  驱动器处理有界Owner唤醒信号（选择变化/撤权/expiry/Unbind）及stage完成
      // Show未完成也响应清理，不先await show/watch堵住Clear/Close启动。

清理（停止业务接纳之后仍可用预留Cleanup）:
  scope.RequestStop()仅用于最终Unbind/slot.Close；切换选择只owner.SignalCleanup()
  owner取消expiry CTS、遮罩（Work已停时用Cleanup槽3登记原Dispatcher任务）
  已发Show时先发clear = Need(scope.Start(BorrowedLane.Cleanup, 0,
      () => bridge.ClearAsync(原clearRequest, owner.CleanupToken),
      receipt => owner.ClearReceipt = receipt))
  最终关闭可以先发close = scope.Start(Cleanup,2,bridge.CloseAsync,接管回执)
      // Clear/Close信号先发；bridge需串行协调两个原Task，不与租约watch互等。
  驱动器处理clear.Received/已启动close.Received（汇合必要NoFurtherReads ACK）
      // Open仍在途时保持清理标记；其接收门取得lease后继续清理，不先结束Owner。
  await 原show/Open及Dispatcher任务确实结束；旧Show晚到后仍按原display清理
  若Detached/NoFurtherReads确认:
      release = Need(scope.Start(BorrowedLane.Cleanup, 1,
          () => lease.ReleaseAsync(原releaseId, owner.CleanupToken),
          receipt => owner.ReleaseReceipt = receipt))
      // Release先启动，Closed watch可能由它触发；不能反向先等watch。
      await release.Received；Released=false时只登记一次受预算QueryRelease观察
      await watch.Original及expiry.Original退出（Fault/Cancelled也观察并记原错误）
  Clear未知时Query = scope.Start(Observation,0,
      () => bridge.QueryClearAsync(原clearRequest,观察token),接管观察)，不重发Clear
  未决时owner生命周期保持未完成；观察到期QueryEvidence返回DrainUnknown
  最终Unbind取得Close.ViewClosed/NoFurtherReads，所有stage接收门/原Task结束后:
      owner.RunAsync返回 new BorrowedScopeResult(scope.Id,true,workErrors,cleanupErrors)
      // root只在这之后发布scope.Completion/归还预留，非零业务错误仍保存。

Unbind调用者:
  scope.RequestStop() // 先向Owner发清理信号
  仅await scope.Completion.WaitAsync(有限观察预算, waitToken)
  timeout/等待取消 => 记录观察未完成；Need(scope.TransferToRoot().Accepted)
  禁止因观察结束销毁owner/lease/View；清理继续使用独立CleanupToken
```

驱动器用预留内的固定stage完成continuation与单一合并唤醒信号推进，不为每次选择创建额外WaitAsync/WhenAny任务队列；任何在途业务stage都不能阻挡停止信号处理和Cleanup启动。未发Show时没有桥读者，仍须Open接收门完成、接管lease并确认未启动Show后才允许Release；最终Close仍须确认ViewClosed。timer的原Task必须在scope.Start delegate内部才创建，用有限剩余UTC期限转换本地单调deadline，不在delegate外先Task.Delay再声称预留。其Task<TResult>取消可由Original确认退出，不要求accept收到结果才可释放槽。watch接收门只发控制信号；若正常Released引起Closed，不额外再发Release。最后清理可同时启动Clear/Close来禁继续读取，但源Release仍必须等桥NoFurtherReads证据与旧Show实际退出，不能为了破死锁提前归还正在被读的payload。Bridge.Close不得等待lease.AuthorityChanged/源Release，源Release不得等待未来Bridge动作；这两个端口不互相持有生命周期所有权。有限观察只决定调用者何时返回，不是stop/release强制完成预算。

### 8.2.2 两个STA宿主与证据构造

两个STA Host共同编译以下**显式合成证据端口/桥**，不调用私有viewport类。它将abc三字节作为3×1 Gray8像素（97/98/99）应用到Dispatcher影像投影，并叠加由独立原ROI样例`0,0;0,3;1,3;1,0`给出的像素角坐标；不是“永远无输入”的占位图。图/ROI分别计算原字节hash并绑定MemberId=m1/face=top/pixel-v1。ROI来自测试宿主的只读原证据，不被治理模块创建为标签或覆盖Snapshot真值。生产Bridge可替换为受控viewport只读View，仍履行相同Show/Clear/Close证据与租约边界；本例只证明规格可构造，不证明真实WPF已跑。

```csharp
using System;
using System.Collections.Immutable;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;
using Asun.Modules.AiDatasetGovernance;
using Asun.Modules.AiDatasetGovernance.Wpf;

sealed record SyntheticPreviewPayload(ImmutableArray<byte> Pixels,
    ImmutableArray<double> RoiRowColumns) : IPreviewPayload;

sealed class SyntheticPreviewSource : IPreviewEvidenceSource {
    readonly PreviewEvidenceRef expected;
    readonly ImmutableArray<byte> image = ImmutableArray.Create<byte>(97, 98, 99);
    readonly ImmutableArray<byte> roi = Encoding.UTF8.GetBytes(
        "0,0;0,3;1,3;1,0").ToImmutableArray();
    public SyntheticPreviewSource(PreviewEvidenceRef evidence) => expected = evidence;
    public static PreviewEvidenceRef Describe(FrozenSnapshot snapshot) {
        var member = snapshot.CopyMembers(Partition.Test).Single(x => x.Id == "m1");
        var roiBytes = Encoding.UTF8.GetBytes("0,0;0,3;1,3;1,0");
        var region = new RegionRef("preview-roi-m1", "target",
            new RevisionRef("synthetic-roi-m1", "test-v1",
                GovernanceFactory.HashContent(roiBytes, 100)),
            "pixel-v1", new PixelBounds(0, 0, 1, 3));
        return new PreviewEvidenceRef("m1", member.Evidence, 3,
            "gray8-u8-row-major-v1", 3, 1, 3, "top", "pixel-v1", null,
            ImmutableArray.Create(new PreviewRoiRef(region, "test-roi-corners-v1",
                roiBytes.Length)), Origin.Synthetic);
    }
    public Task<PreviewOpenResult> OpenAsync(PreviewSelectionRequest q, CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        bool same = (q.Evidence with { Rois = expected.Rois }) == expected &&
            q.Evidence.Rois.SequenceEqual(expected.Rois);
        bool auth = q.Authorization == new AuthorizationQuery("synthetic-operator", "test",
            "preview-evidence", "synthetic-only", "test-policy-v1");
        bool content = expected.Image.Hash == GovernanceFactory.HashContent(image.ToArray(), 3) &&
            expected.Rois.Single().Region.Region.Hash ==
                GovernanceFactory.HashContent(roi.ToArray(), 100);
        if (!same || !content || !auth) return Task.FromResult(new PreviewOpenResult(null,
            !auth ? "DG-003" : "DG-005"));
        IPreviewEvidenceLease lease = new SyntheticPreviewLease(q,
            new SyntheticPreviewPayload(image, ImmutableArray.Create<double>(0, 0, 0, 3,
                1, 3, 1, 0)));
        return Task.FromResult(new PreviewOpenResult(lease, null));
    }
}
sealed class SyntheticPreviewLease : IPreviewEvidenceLease {
    readonly PreviewSelectionRequest request;
    readonly TaskCompletionSource<PreviewAuthorityNotice> watch = new(
        TaskCreationOptions.RunContinuationsAsynchronously);
    bool released; bool revoked; string? releaseId;
    public string LeaseId { get; }
    public PreviewEvidenceRef Evidence => request.Evidence;
    public PreviewPermit Permit { get; }
    public IPreviewPayload Payload { get; }
    public Task<PreviewAuthorityNotice> AuthorityChanged => watch.Task;
    public SyntheticPreviewLease(PreviewSelectionRequest q, IPreviewPayload payload) {
        request = q; Payload = payload; LeaseId = q.OperationId + "/" + q.SelectionEpoch;
        Permit = new PreviewPermit("synthetic-preview-auth", q.Authorization.Principal,
            q.Authorization.Tenant, q.Authorization.Scope, q.Authorization.PolicyRevision,
            "synthetic-fence", DateTimeOffset.UtcNow.AddMinutes(5));
    }
    public bool CanDisclose(PreviewSelectionRequest q) {
        lock (watch) return !released && !revoked && DateTimeOffset.UtcNow < Permit.ValidUntilUtc &&
            q.OperationId == request.OperationId && q.OperationGeneration == request.OperationGeneration &&
            q.BindingEpoch == request.BindingEpoch && q.SelectionEpoch == request.SelectionEpoch &&
            q.RowId == request.RowId && q.Authorization == request.Authorization &&
            (q.Evidence with { Rois = request.Evidence.Rois }) == request.Evidence &&
            q.Evidence.Rois.SequenceEqual(request.Evidence.Rois);
    }
    public void Revoke() { lock (watch) { revoked = true;
        watch.TrySetResult(new PreviewAuthorityNotice(PreviewAuthorityState.Revoked, Permit.Fence)); } }
    public Task<PreviewReleaseReceipt> ReleaseAsync(string id, CancellationToken ct) {
        // 固定ID幂等；此样例没有native/IO，真实源须等待实际退出。
        lock (watch) {
            releaseId ??= id;
            if (releaseId != id) return Task.FromResult(new PreviewReleaseReceipt(LeaseId,
                id, false, "DG-016"));
            released = true;
            watch.TrySetResult(new PreviewAuthorityNotice(PreviewAuthorityState.Closed, Permit.Fence));
            return Task.FromResult(new PreviewReleaseReceipt(LeaseId, id, true, null));
        }
    }
    public Task<PreviewReleaseReceipt> QueryReleaseAsync(string id, CancellationToken ct) {
        lock (watch) return Task.FromResult(new PreviewReleaseReceipt(LeaseId, id,
            released && id == releaseId, released && id == releaseId ? null : "DG-012"));
    }
}
sealed class SyntheticPreviewBridge : IEvidencePreviewBridge {
    readonly Grid view = new() { Width = 600, Height = 200, Background = Brushes.Black };
    IPreviewEvidenceLease? displayedLease;
    PreviewDisplayRequest? displayed;
    PreviewClearRequest? lastClear;
    PreviewDetachReceipt? lastClearReceipt;
    PreviewCloseRequest? lastClose;
    PreviewDetachReceipt? closeReceipt;
    long sequence; bool closed;
    public FrameworkElement View => view;
    public async Task<PreviewShowReceipt> ShowAsync(PreviewDisplayRequest q,
        IPreviewEvidenceLease lease, CancellationToken ct) {
        // Dispatcher原Task在桥内保存至完成；外层Owner保留本原Show Task。
        var apply = view.Dispatcher.InvokeAsync(() => {
            ct.ThrowIfCancellationRequested();
            if (closed || displayed != null || !lease.CanDisclose(q.Selection))
                return new PreviewShowReceipt(q.DisplayId, q.Selection.BindingEpoch,
                    q.Selection.SelectionEpoch, false, sequence, "DG-003");
            var data = (SyntheticPreviewPayload)lease.Payload;
            var bitmap = BitmapSource.Create(3, 1, 96, 96, PixelFormats.Gray8, null,
                data.Pixels.ToArray(), 3);
            bitmap.Freeze();
            view.Children.Add(new Image { Source = bitmap, Stretch = Stretch.Fill });
            var outline = new Polyline { Stroke = Brushes.Yellow, StrokeThickness = 2 };
            for (int i = 0; i < data.RoiRowColumns.Length; i += 2)
                outline.Points.Add(new Point(data.RoiRowColumns[i + 1] * 200,
                    data.RoiRowColumns[i] * 200));
            outline.Points.Add(outline.Points[0]);
            var canvas = new Canvas(); canvas.Children.Add(outline); view.Children.Add(canvas);
            displayed = q; displayedLease = lease; sequence++;
            return new PreviewShowReceipt(q.DisplayId, q.Selection.BindingEpoch,
                q.Selection.SelectionEpoch, true, sequence, null);
        });
        return await apply.Task;
    }
    public async Task<PreviewDetachReceipt> ClearAsync(PreviewClearRequest q, CancellationToken ct) {
        var clear = view.Dispatcher.InvokeAsync(() => {
            if (lastClear == q && lastClearReceipt != null) return lastClearReceipt;
            if (displayed != null && (displayed.DisplayId != q.DisplayId ||
                displayed.Selection.BindingEpoch != q.BindingEpoch ||
                displayed.Selection.SelectionEpoch != q.SelectionEpoch))
                return new PreviewDetachReceipt(q.BindingEpoch, q.SelectionEpoch, q.DisplayId,
                    false, false, false, sequence, "DG-016");
            view.Children.Clear(); displayed = null; displayedLease = null; sequence++;
            lastClear = q; lastClearReceipt = new PreviewDetachReceipt(q.BindingEpoch,
                q.SelectionEpoch, q.DisplayId, true, true, false, sequence, null);
            return lastClearReceipt;
        });
        return await clear.Task; // 无native读者，仅真实Dispatcher执行后确认。
    }
    public Task<PreviewDetachReceipt> QueryClearAsync(PreviewClearRequest q, CancellationToken ct)
        => view.Dispatcher.InvokeAsync(() => lastClear == q && lastClearReceipt != null ?
            lastClearReceipt : new PreviewDetachReceipt(q.BindingEpoch, q.SelectionEpoch,
                q.DisplayId, false, false, false, sequence, "DG-012")).Task;
    public async Task<PreviewDetachReceipt> CloseAsync(PreviewCloseRequest q, CancellationToken ct) {
        var close = view.Dispatcher.InvokeAsync(() => {
            if (lastClose == q && closeReceipt != null) return closeReceipt;
            if (lastClose != null) return new PreviewDetachReceipt(q.BindingEpoch, 0,
                "closed", false, false, false, sequence, "DG-016");
            view.Children.Clear(); displayed = null; displayedLease = null; closed = true; sequence++;
            lastClose = q;
            closeReceipt = new PreviewDetachReceipt(q.BindingEpoch, 0, "closed", true, true, true,
                sequence, null);
            return closeReceipt;
        });
        return await close.Task;
    }
}
```

上述Bridge只支持描述中固定3×1 Gray8与fixture ROI，Open已逐字段确认，其余schema/大小拒绝；不是生产通用解码器。Revoke为故障用例入口，真实源使用原authority watch。所有Displayed lease直到Clear/Close原Dispatcher Task确认都由Bridge和模块Owner双持，release由模块Owner唯一调用；Bridge不自行归还借用lease。展示后的sample保留源lease是刻意验证协议，即使Bitmap已经复制像素也不提前归还。UI实验源watch/bitmap限制清楚，不冒HALCON/native排空证明。

`GovernanceSession.ReadProjectionAsync`先核读权再从原operation记录生成有限Rows/Metrics（不从当前可变草稿拼），超界拒绝DG-008，事件/回执generation/sequence相同；原读取Task与授权Task在根有界持有。`operationId`必须已接纳；Unknown状态给查询命令和真实资源状态，未算指标为空。宿主Projection适配只调用此公开入口，未授权不输出原串。SupportsTraining/Usage=false时相应命令CanExecute=false；不是catch未知异常后伪装可用。此方法不启动新业务。

WPF测试入口`[STAThread] static int Main`，创建唯一Application+Dispatcher；宿主A用§9 Defect参数，宿主B用Ocr参数，均将同一公开GovernanceBinding注入GovernanceControl。绑定前取得同一进程GovernanceRoot/RootSlot，端口使用§9显式SyntheticPorts以及有界投影：Rows返回snapshot/model/operation及一个带精确证据的member-m1行，Metrics映射Outcome.Endpoints，未完成时返回空metrics和Running，不能填假分数；授权仍检查Query。Text实现为该表+所有界面键的三语词典，无产品Shell/全局服务；BuildRequest委托分别返回§9完全构造的request，未启用Train/Usage的委托抛明确NotSupported且命令CanExecute=false。

正常：绑定→Precheck→Evaluate→投影读取→DataBind优先级Dispatcher呈现回执→检查选中联动与端点分母→三语切换→Unbind→业务slot.Close。异常：慢投影、旧generation迟到、撤权、Unknown、关窗发生在预测/提交/Dispatcher阶段；保留UI读取/Dispatcher原Task在根，有限cleanup后移交确认。窗口设置client验证区不超过1920×1080，不改系统分辨率。真正的WPF/API行为、UIA键盘、长英语/繁体长度、只读属性、图表/影像租约和关闭排空必须后续实跑，当前无已通过声明。两个Host不是两个产品模型资格。

STA Host唯一入口源码形状如下（使用§9完整已定义SyntheticPorts/TwoHosts.BuildRequest，不读取产品夹具；SyntheticPorts/HostRun/TwoHosts辅助源码在两个测试Exe各自编译；WPF不复制§9的Program，只编译StaProgram为唯一Main，不能ProjectReference测试程序集）。命令通过控件公开ICommand执行，展示必须真实进入Dispatcher，不调用私有ViewModel。resourceMap是调用方显式词典，键全集是上表9键、全部列/面板/状态/命令/错误键；词典构造须拒重复/缺当前culture键，读取缺键抛可定位异常，不能生成英文假回退。

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Threading;
using Asun.Modules.AiDatasetGovernance;
using Asun.Modules.AiDatasetGovernance.Wpf;

sealed class SessionProjection : IGovernanceProjectionPort {
    readonly GovernanceSession session;
    readonly PreviewEvidenceRef evidence;
    public SessionProjection(GovernanceSession value, PreviewEvidenceRef source)
        { session = value; evidence = source; }
    public async Task<GovernanceProjection> ReadAsync(string id, AuthorizationQuery auth,
        CancellationToken token) {
        var p = await session.ReadProjectionAsync(id, auth, 100, 100, token);
        // session当前读权已核；source再核preview-evidence独立读权。
        var member = new GovernanceRow("member-m1", "", "member",
            evidence.Image.Version, evidence.Image.Hash.Value, "synthetic-only",
            "DG.PreviewSynthetic", "", evidence);
        return p with { Rows = p.Rows.Add(member) };
    }
}
sealed class HostText : IGovernanceText {
    readonly IReadOnlyDictionary<string, string> map;
    public string CultureName { get; }
    public HostText(string culture, IReadOnlyDictionary<string, string> values)
        { CultureName = culture; map = values; }
    public string Get(string key) => map.TryGetValue(key, out var text) ? text :
        throw new InvalidOperationException("Missing resource: " + key);
}
// 两个公开宿主入口，各自由[STAThread] Main在同一Application/Dispatcher内调用。
static class StaHosts {
    public static Task<int> DefectAsync(GovernanceRoot root, IGovernanceText text)
        => RunAsync(root, text, TaskKind.Defect, "sta-defect");
    public static Task<int> OcrAsync(GovernanceRoot root, IGovernanceText text)
        => RunAsync(root, text, TaskKind.Ocr, "sta-ocr");
    static async Task<int> RunAsync(GovernanceRoot root, IGovernanceText text, TaskKind task,
        string id)
    {
        if (!root.TryReserve(4 * 1024 * 1024, out var reserved) || reserved == null)
            return 1;
        var slot = reserved; GovernanceSession? session = null;
        GovernanceControl? control = null; Window? window = null;
        Exception? primary = null; var cleanupErrors = new List<Exception>(); bool shown = false;
        try {
            var ports = new SyntheticPorts();
            var budget = new Budget(100, 65536, 262144, 1048576, 100000, 1, 2000, 1000);
            var request = TwoHosts.BuildRequest(task, id, ports, budget);
            session = slot.Open(ports.Ports);
            var evidence = SyntheticPreviewSource.Describe(request.Snapshot);
            var preview = new EvidencePreviewBinding(new SyntheticPreviewSource(evidence),
                new SyntheticPreviewBridge(),
                new AuthorizationQuery("synthetic-operator", "test", "preview-evidence",
                    "synthetic-only", "test-policy-v1"),
                new PreviewLimits(1024, 2 * 1024 * 1024, 100, 100, 4, 2000, 1000));
            control = new GovernanceControl();
            window = new Window { Width = 1800, Height = 900, Content = control };
            window.Show();
            var binding = new GovernanceBinding(session, slot, new SessionProjection(session, evidence),
                request.Authorization, text, 100, 100, 100, false, false,
                preview,
                () => request,
                () => throw new NotSupportedException("Training not enabled in this host"),
                () => throw new NotSupportedException("Usage decisions not enabled in this host"));
            await control.BindAsync(binding, CancellationToken.None);
            control.PrecheckCommand.Execute(null);
            if (!control.EvaluateCommand.CanExecute(null))
                throw new InvalidOperationException("Evaluate unavailable after valid precheck");
            control.EvaluateCommand.Execute(null);
            // Start与控件命令同operation同hash，只取原handle，不重复预测/提交。
            var handle = session.StartEvaluation(request).Value ??
                throw new InvalidOperationException("No operation handle");
            await handle.Completion.WaitAsync(TimeSpan.FromSeconds(3));
            control.LookupCommand.Execute(null);
            // 验证必须等待控件呈现回执，不以一次Dispatcher空转假定刷新完成。
            var presentation = await control.WaitForPresentationAsync(id,
                handle.Generation, OperationState.Succeeded, 2000, CancellationToken.None);
            shown = presentation;
            var selected = await control.SelectEvidenceAsync("member-m1", 2000, CancellationToken.None);
            if (selected.State != PreviewState.Presented || selected.ResourcesReleased ||
                selected.Evidence?.Image.Hash != evidence.Image.Hash ||
                selected.Evidence?.Rois.Single().Region.Region.Hash !=
                    evidence.Rois.Single().Region.Region.Hash)
                throw new InvalidOperationException("Preview evidence or ownership mismatch");
            var cleared = await control.ClearEvidenceAsync(1000, CancellationToken.None);
            if (cleared.State != PreviewState.Released || !cleared.ResourcesReleased)
                throw new InvalidOperationException("Preview clear or lease release unresolved");
            foreach (var culture in new[] { "zh-CN", "zh-TW", "en-US" })
                control.SetLanguage(GovernanceText.Create(culture));
            await Application.Current.Dispatcher.InvokeAsync(() => {
                var p = control.Projection;
                if (p == null || p.OperationId != id || p.State != OperationState.Succeeded)
                    throw new InvalidOperationException("Projection mismatch");
            }, DispatcherPriority.DataBind);
        }
        catch (Exception ex) { primary = ex; }
        finally {
            if (control != null) {
                try { await control.UnbindAsync(1000); }
                catch (Exception ex) { cleanupErrors.Add(ex); }
            }
            try { session?.RequestClose(); } catch (Exception ex) { cleanupErrors.Add(ex); }
            try { window?.Close(); } catch (Exception ex) { cleanupErrors.Add(ex); }
        }
        CleanupResult cleanup;
        try { cleanup = await slot.CloseAsync(1000); }
        catch (Exception ex) { cleanupErrors.Add(ex);
            cleanup = new CleanupResult(false, false, "DG-011", slot.Id); }
        if (!cleanup.Released) {
            cleanupErrors.Add(new InvalidOperationException(cleanup.ErrorCode ?? "UI cleanup unresolved"));
            try {
                if (!slot.TransferToRoot().Accepted)
                    cleanupErrors.Add(new InvalidOperationException("UI root transfer rejected"));
            }
            catch (Exception ex) { cleanupErrors.Add(ex); }
        }
        if (primary != null) Console.Error.WriteLine("UI work: " + primary.GetType().Name);
        foreach (var error in cleanupErrors)
            Console.Error.WriteLine("UI cleanup: " + error.GetType().Name);
        return primary == null && cleanupErrors.Count == 0 && cleanup.Released && shown ? 0 : 1;
    }
}
static class StaProgram {
    [STAThread]
    static int Main() {
        var root = new GovernanceRoot(new RootLimits(2, 4, 16 * 1024 * 1024, 64, 32));
        var app = new Application { ShutdownMode = ShutdownMode.OnExplicitShutdown };
        int exitCode = 1;
        Task? originalHostTask = null;
        app.Startup += (_, _) => {
            // 保留整个双Host原Task；异常在其内部转换为非零，不用async void失去观察。
            originalHostTask = RunAllAsync();
        };
        async Task RunAllAsync() {
            try {
                var text = GovernanceText.Create("zh-CN");
                int a = await StaHosts.DefectAsync(root, text);
                int b = await StaHosts.OcrAsync(root, text);
                var end = await root.ObserveAllAsync(2000);
                exitCode = a == 0 && b == 0 && end.Released &&
                    root.OutstandingSlots == 0 ? 0 : 1;
            }
            catch (Exception ex) { Console.Error.WriteLine(ex.GetType().Name); exitCode = 1; }
            finally { app.Shutdown(exitCode); }
        }
        app.Run();
        if (originalHostTask == null || !originalHostTask.IsCompletedSuccessfully)
            return 1;
        return exitCode;
    }
}
```

控件公开补充 `Task<bool> WaitForPresentationAsync(string operationId, long generation, OperationState expected, int timeoutMs, CancellationToken waitToken)`，它只观察已授权投影最终应用到Dispatcher的sequence，不调用业务/生成投影；有限deadline返回false，token只取消等待。测试的根继续持Dispatcher原Task，false不释放资源。上面的测试[STAThread] Main在进程入口持Root和Application，Dispatcher启动后按序调用StaHosts.DefectAsync/OcrAsync及三语资源切换，最后root.ObserveAllAsync；U02故障矩阵由同测试Exe的额外固定用例执行，不声称此正常入口已经覆盖它；任一异常/未呈现/未释放非零后Shutdown。resourceMap按§8.1资源表和控件全键实际实现构建；源中的HostText仅词典接线，当前不声称整份资源文件已实现或真实UI已运行。

### 8.2.3 生产只读预览：viewport公开装配和清空恢复

§8.2.2的SyntheticPreviewBridge保持原用途；生产Adapter实现同一`IEvidencePreviewBridge`，消费[viewport §10.6–10.9、§15.2.2.1](../viewport/DEVELOPMENT-GUIDE.md)公开的WPF Assembly v0.2、Core API0.1、ImageFrame源工厂，及[image-frame §4.3–4.4](../image-frame/DEVELOPMENT-GUIDE.md)公开CPU服务。不把任意`IPreviewPayload`交给内置renderer；不扩展3D、ROI编辑、Probe、导出、模型评价或质量命令。

生产source实现`IPreviewEvidenceSource`，按§13.2.3读精确图像/原ROI/有效域字节并核EOF/hash/权限。它的私有`CpuPreviewPayload`只在本模块Source/Bridge之间使用：稳定`IFrameInputRows`、完整FrameDescriptor草稿、原Evidence引用、只读轮廓数组及当前Permit/watch；不含共享可变图像或逃逸native pointer。仅Source工厂产生此payload，未知payload拒绝DG-002，不能对marker反射。Gray8/Gray16/RGB8首版按单plane UInt8×1/UInt16×1/UInt8×3，紧凑行、小端、RGB显式顺序；16bit不量化为8bit。其它图像类型/多plane由来源提供有具名方法和父引用的派生预览证据，或明确Unavailable，不能换图仍标原hash。

宿主在本模块预览scope启动前建立并强持以下组合；各factory仅构造/校验，Bind等实际工作由原scope/root登记。借用source服务和viewport root各自有原Owner，治理root持整个Bridge生命周期及恢复入口，两个root不互相冒充释放证据。

| 装配项 | 唯一生产映射与所有权 |
|---|---|
| Frame服务 | 宿主提供`Asun.Modules.ImageFrame.Resources.IFrameService`及原ServiceEpoch，原ResourceLimits显式登记本binding的publish/read两个ConsumerId。Source/Bridge不Close共享service；只Retire自己成功发布的FrameKey。新FrameKey Guid/ulong修订登记关联原Evidence和selection，不强转外部版本或复用旧Key |
| Viewport root/control | `new Asun.UI.Viewports.ViewportRootFactory().Create(ViewportRootOptions)`、同STA `new Asun.UI.Viewports.Wpf.ViewportControl()`；Root先由长寿命HostOwner持有。control就是Bridge.View，不再套第二ViewportControl；一个binding只一个control/Dispatcher |
| CPU源 | `Asun.UI.Viewports.ImageFrame.ViewportImageFrameSourceFactory.Create(service,root,new ViewportImageFrameSourceOptions(readConsumerId,MaxBindings,MaxRetainedMetadataBytes))`；核PortResult成功+Value，稳定Frames/Coordinates一次注入session，后续换图只Register/Remove，不换端口。工厂不取得service所有权 |
| Renderer | 同control/root调用`ViewportRendererFactory.Create(control,root,new ViewportRendererOptions(HalconRequired,MaxNativeBaselineBytes,MaxRasterBytes,MaxPendingSubmissions,CleanupBudget))`；核结果后保存同一Backend/Lifetime。HALCON HWND/ROI绘制归该renderer，不用WPF Canvas盖native窗口，也不在本模块另开/关HALCON window |
| Session Options | root.CreateFactory().Create；完整必填ConsumerId、ReadOnly、Navigation\|Presentation、sourcePorts.Frames/Coordinates、可信viewport授权adapter、MaxDisplayBytes、MaxInFlightTiles、Required；DrainTimeout/OperationTimeout显式有限。Roi/Surface/Probe/IntentSink=null；Presentation=**同control.Presentation**，ResourceAdmission=宿主已接纳的公共资源准入端口，Limits完整9字段，BackendPolicy=HalconRequired，Backend=同renderer.Backend，UpdateThrottle=null。禁止生产EvidenceReview选择BudgetOnly |
| UI绑定 | `ViewportUiResourceCatalog.Get(language)`成功完整`viewport-ui-text/1`资源；`new ViewportUiBindingOptions(bindingId,true,resources,CleanupBudget,Lifetime:renderer.Lifetime,ExecutionBudget:完整ViewportUiExecutionBudget)`传同control.BindAsync(session,root,options,ct)。保存原Bind Task及结果IViewportUiBinding；OwnSession=true只代表本bridge独占session，不代表source服务独占。Bind失败/晚到仍按同root原清理链，无第二次Bind补救 |
| 本模块桥入口 | Wpf DLL提供`public sealed class ViewportEvidencePreviewBridge : IEvidencePreviewBridge`及唯一构造器`(ViewportControl control, IViewportSession session, IViewportUiBinding uiBinding, IViewportProcessRoot root, IViewportImageFrameSource sourcePorts, IFrameService frameService, string publishConsumerId, TimeSpan workBudget, TimeSpan cleanupBudget)`；类型分别来自上述公开namespace。构造无IO，核uiBinding.Session/BindingId、同Control/root/源实例的Host装配关联，预算>0且受已接纳Profile，保存原Task/发布键/注册键/Context与clear映射。View返回原control。宿主先完成原绑定才构造桥，不经全局容器找对象；Bridge不是额外Root或FrameService Owner |

**公开描述和修订保真。** 本模块绑定目录以原Image.Id/Version/Hash、Face、CoordinateRevision、解码方法/域完整引用为键，生成SourceId稳定字符串和局部正long CoordinateRevision；局部token映射保存原完整引用，checked单调分配，不把ulong/hash/版本字符串截为long或按行号命名。Frame.SourceId/SourceRevision与ImageSourceDescriptor逐值相同，Frame.CoordinateReference=PixelSpace（原明确整数中心像素空间）。SourceRevision是完整原引用的确定编码/摘要索引，仍保原引用反查，不能仅用版本号。DecodeRevision绑定解码方法/色序/有效域，不采用文件名。尺寸、channel、bit、signed取实际原布局，Convention=CenterInteger；level0为原Width/Height、identity AffineMap2D、Profile有限tile尺寸及完整decoded bytes上界，Channels精确Gray或R/G/B。ValidityDomain保原Owner/修订/半开Boundary；未知域不能Full，非全域保精确MaskAssetRevision，image-frame各plane原行段域同时保留。

生产撤权/切行的遮罩用覆盖原native绘图区的独立不透明Popup（PlacementTarget=原control、StaysOpen=true、Focusable=false，位置/尺寸随原client/DPI更新），旁边保留状态/查询命令；不能用透明WPF Canvas覆盖HWND。Popup及布局回调进入原UI生命周期，确认清空/关闭后移除；遮罩出现不证明资源归还，不能因native图仍被覆盖就发Clear ACK。

原ROI只读显示从原region经`gen_contour_region_xld(...,'border_holes')`→逐条`get_contour_xld`，保外边及孔洞、原坐标/顺序；原封闭XLD按其来源方法直接读取。它们转为`SourcePolyline` OverlayPayload，SourcePoint2D=(column,row)，Geometry为空、LabelResourceKey空、SelectionPriority=0；每个轮廓独立LayerId、ZOrder固定、Visible=true、Interactive=false，SourceRevision/CoordinateRevision与当前原图一致，GeometryRevision用局部映射保原ROI完整引用。HALCON border坐标按其原像素中心系原样转列/行，不因ValidityBoundary是半开再加减0.5。轮廓仅是原ROI显示投影，不作为面积/命中/训练标签；孔洞不连成一条、不以Bounds矩形替代原ROI。点数/层数/字节在提取前预检原来源上界并受Limits，超限Unavailable而非截前N点。face在影像区外本模块文字投影显示，不把制程语义交给viewport。

Bridge.Close在从未Attach且无任何Publish/Read/Show责任时，只关闭原UI binding/session并核原回执，不捏造一次清空BlankPresentation；若首次Show在途或Bind失败/迟到，仍按保存的原Task捕获/归还，不能走无资源快捷分支。Clear收到未知DisplayId拒绝DG-005，不清别的selection。

**Show→Clear→下一选择：**

1. Show核lease.Evidence、原selection/DisplayId、CanDisclose和完整payload。通过同原Task调用`frameService.PublishCopyAsync(new CopyPublishRequest(requestGuid,publishConsumerId,descriptor,rows,remainingBudget),token)`（原ValueTask只AsTask一次）。源rows在原Publish实际退出前不得Release；必须Completed/Error=None/OperationResourcesReleased且Frame非null，不能用Register验证替代成功发布。未知保原epoch/requestGuid查询，取消后晚到发布先登记再Retire本次Key，不创建新Key重发。
2. Register完整`ViewportPublishedFrameBinding(entryId,原Publish.Frame,完整ImageSourceDescriptor,ImmutableArray.Create(0),PixelSpace)`。失败不Attach；保留原结果，确认viewport未借用后Retire本次成功发布。为第一次有效Show构造Primary SourceBinding、Timing=null、CorrelationId=原operation/selection绑定，完整Overlay层、可信AuthorizationSnapshot、当前Language、ApiVersion(0,1)、ContextRevision=1、实际已布局Canvas/DPI的Fit2D；Attach仅一次。后续Show使用新ContextRevision全量Update，不能再次Attach/Bind。
3. 原Attach/Update Task完成、SourceStatus精确源Presented且同Context/generation的`uiBinding.GetPresentations()`中原Commit/Acquire/Confirm链确认为VisibleConfirmed后，才填本模块Presented；还须再核当前selection和CanDisclose。PresentationSequence使用本bridge checked单调确认序号，不拿显示代冒治理业务generation。失败/迟到只清理，不向已换行UI交付成功。
4. Clear按完整ClearId保存一次原任务，以session当前已接纳Context的Authorization/Language/View（Profile=null）和Sources/Layers均空构造新revision的ViewportUpdate。它是viewport§4.7.1安全Control清空，撤权时不请求旧Read再许可。Clear入口先独立发出本bridge停止信号、关闭旧Show继续呈现的门并遮罩，不能先await Show才发信号；Showworker收到停止后不得等待本Clear ACK才能收尾。原Attach/Update未完成时保它的原Task/迟到责任，按同session原取消/Control链观察已接纳Context，再用准确base启动这一Clear唯一空Update，避免用旧base覆盖新Context；任何在途native不能确认退出则保持Unknown，不靠信号伪ACK。首次Attach被取消/失败时原session不可复用，或原session已Draining而无法接纳空Update时，以原session.DisposeAsync关闭/排空取代继续呈现，Close回执确认后本bridge只能关闭；新预览须宿主显式建立新binding，禁止在未知旧session上重建。
5. 只在原空Update或同原snapshot的EmptyTransition精确匹配本Clear、三个Previous=true、PreviousCleanup=Drained、BlankPresentation.VisibleConfirmed且旧Show/Publish/源read/Presenter已退出，才确认Detached/NoFurtherReads。随后sourcePorts.Remove(entryId)成功→frameService.RetireAsync(本次FrameKey,cleanupBudget)真实ResourcesReleased→允许本模块lease.Release。Retire不是另一个人的FrameKey或共享service Close。Clear未知仅查保存的原Task及GetSnapshot，禁止重发Update、Unbind或开新session绕过。
6. 清空确认后桥仍绑定同session；下个已授权selection沿步骤1–3的Register→Update恢复。Close先停止新Show，完成原Clear/lease协议后uiBinding.UnbindAsync（OwnSession=true）观察其原关闭，再核同session.Dispose/viewport root的实际回执；本bridge不Close宿主共享root，HostOwner最终关闭root。Blank Presenter/native baseline在Close前可仍存在，不当作旧图借用。Close/Bind观察超时保原对象/Task，治理预览scope只有得到本桥ViewClosed/NoFurtherReads及自己lease/watch归还事实才结束。

来源读取Open、Bridge Show/Clear/Close的外层原Task仍沿§4.3.1已接收11槽，viewport/image-frame内部并发另在它们各自root/Profile限额内。生产viewport授权adapter把原PreviewPermit的actor/tenant/scope/policy/expiry与受信authority目录映入AuthorizationSnapshot：OwnerId=原权限Owner、Revision=完整policy+domain/generation索引、Purpose=EvidenceReview、Rights=Read、AccessDomain=原tenant/scope；Changed只由受信撤权/到期/watch-gap触发，新Snapshot不得扩大Rights。不能拿principal字符串或Synthetic许可生成生产权利。CanDisclose、viewport每次受保护读取及提交门全部保留，撤权时撤原显示而不披露旧OCR原文。

**两个STA Host的明确接线与验收输入。** 继续用§8.2.2的缺陷/OCR两Host、原abc=3×1 Gray8、top/pixel-v1、原15byte ROI、独立operation/BindingEpoch/selection和各自STA；增加`viewport-cpu`软件装配mode，各自创建独立CPU frame服务/root/control/renderer/session，Source在原合成值上提供稳定rows，不能把原SyntheticPreviewPayload直接交内置renderer。唯一来源映射为FrameKey=(新Guid,1)，紧凑3-byte plane，Full域、单位1/Scale1/Bias0/Channels={Gray}；Preview ROI四角在本软件mode明确按test-roi-corners-v1半开边界约定转换一次：SourcePolyline中心坐标为(-0.5,-0.5),(2.5,-0.5),(2.5,0.5),(-0.5,0.5),(-0.5,-0.5)，保Synthetic来源，不假装取得真实region。

两Host显式软件Profile：frame BudgetLimit(67108864,67108864,4096,4096,"dg-test","1","preview-cpu","1")；CPU64MiB/native=GPU=cache0、MaxFrames2、Active4/Queued4/Receipts128、Retention1min/Drain2s、publish/read两个ConsumerLimit各(64MiB,8,4,4)。viewport root=(本Host独立id,2,256,128,268435456,2s,2)，limits=(2,32,4096,32,64,64,4096,1,4096)，source options=(本HostreadId,2,1048576)；OfflineRasterOnly/native0/raster64MiB/pending2/cleanup2s，OfflineViewing+BudgetOnly、MaxDisplayBytes64MiB/InFlight4、Work30s/Drain2s、UI budget=(67108864,32,32)，level0 tile256×256/identity/MaxDecodedTileBytes65536；Catalog.Get分别zh-CN/en-US，验证再切zh-TW。其余Options沿上表显式null；离线读权为独立合成许可，不替生产authority。

未来U08–U10断言：U08核首次Attach/真Commit、原图/ROI/face/token、同Control Presentation/Lifetime与root；U09核空Update三个Previous/Blank确认、Remove/Retire/Release顺序及Clear后Update重新显示（无第二Attach/Bind）；U10注入撤权、Bind/Publish/Commit/clear迟到和Dispatcher关闭，核旧内容不再披露、原Task/lease保留、双root恢复及primary/cleanup两轴。1920×1080唯一验证viewport按§8.1扣除外框/任务栏；HALCON HWND airspace、键盘/UIA和生产Required路径另真实执行。本轮只冻结规格，不声称两个mode已实现、编译或运行。

## 9. 两个自足无 UI Host 与公开 Synthetic 端口

以下为**未来程序集存在后的完整接入样例源码**，不是本轮编译通过声明。只依BCL和本文公开API，无FixtureFactory、产品DB、Shell、AsunImage。两个消费者分别是缺陷二元义务和OCR原串义务；所有样本/模型/授权都是合成软件证据，不是实际权重或生产授权。模型字节UTF8 abc和每项data UTF8 abc显式算hash，真实adapter须读取并核实际资产。

共同端口实现可放唯一测试Exe内的`SyntheticPorts.cs`，没有私有产品接口。Production不能使用此端口。Clock固定，所有拒绝/不支持显式失败，无隐式成功。以下全部构造参数已给出：

```csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.AiDatasetGovernance;

sealed class SyntheticPorts : IAuthorizationPort, IFactPort, IPredictionSource,
    ITrainingPort, IReportStore, IExecutionLifetimePort, IUtcClock
{
    readonly object gate = new();
    readonly Dictionary<string, CommitReceipt> commits = new(StringComparer.Ordinal);
    readonly Dictionary<string, CommitReceipt> keys = new(StringComparer.Ordinal);
    readonly HashSet<string> released = new(StringComparer.Ordinal);
    public DateTimeOffset UtcNow => new(2026, 10, 10, 0, 0, 0, TimeSpan.Zero);
    public readonly ContentHash BytesHash = GovernanceFactory.HashContent(
        Encoding.UTF8.GetBytes("abc"), 3);
    public GovernancePorts Ports => new(this, this, this, this, this, this,
        null, null, null, this);
    public Task<AuthorizationReceipt> CheckAsync(AccessCheck q, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();
        bool allow = q.Query == new AuthorizationQuery("synthetic-operator", "test",
            "evaluate", "synthetic-only", "test-policy-v1");
        return Task.FromResult(new AuthorizationReceipt("synthetic-auth", "test-policy-v1",
            q.RequestHash, UtcNow.AddMinutes(5), allow));
    }
    public Task<ClosureReceipt> VerifyAsync(ClosureCheck q, ContentHash h, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();
        bool ok = q.Snapshot.ContractVersion == "0.2" &&
            q.Labels.Hash == BytesHash && q.Model != null &&
            q.Model.ModelAssetRef == "asset://sha256/" + BytesHash.Value &&
            q.Model.Snapshot == q.Snapshot;
        return Task.FromResult(new ClosureReceipt(h, ok, ok, ok, ok, false,
            "synthetic-closure"));
    }
    public Task<PredictionBatch> ReadAsync(FrozenEvaluation q, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();
        var model = q.CopyModel(); var plan = q.CopyPlan();
        var members = q.Dataset.CopyMembers(plan.Partition);
        var items = members.Select(m => new Prediction(m.Id, PredictionStatus.Completed,
            plan.Task == TaskKind.Defect ? "positive" : null,
            plan.Task == TaskKind.Ocr ? "AAAA" : null, Array.Empty<RegionRef>(),
            true, model.PredictionRevision, "synthetic" )).ToArray();
        return Task.FromResult(new PredictionBatch(q.Snapshot,
            GovernanceFactory.HashBinding(model, q.Budget.MaxCanonicalBytes),
            items, "synthetic-prediction"));
    }
    public Task<TrainingProduct> TrainAsync(FrozenTraining q, CancellationToken ct)
        => Task.FromException<TrainingProduct>(new NotSupportedException(
            "This host evaluates synthetic results; it has no trainer."));
    public Task<CommitReceipt> CommitAsync(CommitCommand q, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();
        lock (gate) {
            string key = q.Query.Tenant + "/" + q.Query.Principal + "/evaluate/" +
                q.IdempotencyKey;
            if (keys.TryGetValue(key, out var prior))
                return Task.FromResult(prior.RequestHash == q.RequestHash ? prior :
                    new CommitReceipt(q.OperationId, q.RequestHash,
                        CommitStatus.Conflict, null, "synthetic-key-conflict"));
            if (commits.TryGetValue(q.OperationId, out var old))
                return Task.FromResult(old.RequestHash == q.RequestHash ? old :
                    new CommitReceipt(q.OperationId, q.RequestHash,
                        CommitStatus.Conflict, null, "synthetic-conflict"));
            if (!q.Authorization.Allowed || q.Authorization.RequestHash != q.RequestHash ||
                q.Authorization.ValidUntilUtc <= UtcNow || q.Evaluation == null)
                return Task.FromResult(new CommitReceipt(q.OperationId, q.RequestHash,
                    CommitStatus.NotCommitted, null, "synthetic-denied"));
            var r = new CommitReceipt(q.OperationId, q.RequestHash, CommitStatus.Confirmed,
                "report-" + q.OperationId, "synthetic-commit");
            commits.Add(q.OperationId, r); keys.Add(key, r); return Task.FromResult(r);
        }
    }
    public Task<CommitReceipt> LookupAsync(string id, ContentHash h,
        AuthorizationQuery query, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();
        lock (gate) {
            return query.Principal == "synthetic-operator" && query.Tenant == "test" &&
                commits.TryGetValue(id, out var r) && r.RequestHash == h ? Task.FromResult(r) :
                Task.FromException<CommitReceipt>(new KeyNotFoundException(id));
        }
    }
    public Task<ReleaseReceipt> StopAndReleaseAsync(string id, CancellationToken ct)
    {
        ct.ThrowIfCancellationRequested();
        lock (gate) { released.Add(id); }
        return Task.FromResult(new ReleaseReceipt(id, true, true, "synthetic-release"));
    }
}

sealed record HostRun(Outcome? Business, Exception? PrimaryError,
    CleanupResult Cleanup, ImmutableArray<Exception> CleanupErrors, RetentionAck? Transfer);

static class TwoHosts
{
    public static Task<HostRun> DefectAsync(GovernanceRoot root)
        => RunAsync(root, TaskKind.Defect, "defect-host");
    public static Task<HostRun> OcrAsync(GovernanceRoot root)
        => RunAsync(root, TaskKind.Ocr, "ocr-host");

    public static EvaluationRequest BuildRequest(TaskKind task, string id,
        SyntheticPorts ports, Budget budget)
    {
            var auth = new AuthorizationQuery("synthetic-operator", "test", "evaluate",
                "synthetic-only", "test-policy-v1");
            var data = new RevisionRef("data-" + id, "test-v1", ports.BytesHash);
            var labelRef = new RevisionRef("labels-" + id, "test-v1", ports.BytesHash);
            var truth = new TruthValue(TruthStatus.Approved,
                task == TaskKind.Defect ? "positive" : null,
                task == TaskKind.Ocr ? "A" : null, Array.Empty<RegionRef>(), "synthetic");
            var members = new[] { new DataMember("m1", data, 3, "board-1", null,
                Origin.Synthetic, "2d", "pixel-v1", new[] { "test-source" }) };
            var labels = new LabelSet(labelRef, "classes-v1",
                task == TaskKind.Defect ? new[] { "negative", "positive" } :
                    Array.Empty<string>(),
                task == TaskKind.Defect ? "binary-truth-v1" : "ocr-truth-v1",
                "synthetic-approval", new[] { new LabelObservation("obs1", "m1", data,
                    "synthetic-actor", "synthetic-blind-v1", truth) },
                new[] { new LabelSelection("m1", "obs1", "synthetic-arbitration") });
            var split = new SplitSpec("group-explicit-v1", 7,
                new[] { new GroupAssignment("board-1", Partition.Test) },
                Array.Empty<string>());
            var core = GovernanceFactory.CreateCoreValidator();
            var check = core.Freeze(new SnapshotDraft("snapshot-" + id, "0.2",
                "evaluate", members, labels, split), budget);
            if (check.Value == null) throw new InvalidOperationException(
                string.Join(";", check.Issues.Select(x => x.Code + ":" + x.Path)));
            FrozenSnapshot snapshot = check.Value;
            var binding = new ModelBinding(task, snapshot.Reference,
                "asset://sha256/" + ports.BytesHash.Value, "predict-v1", "pre-v1",
                "post-v1", "classes-v1", "threshold-v1", "synthetic-backend-v1");
            var plan = new EvaluationPlan("plan-" + id, task, snapshot.Reference,
                labelRef, task == TaskKind.Defect ? "binary-v1" : "OCR-EVAL-SCALAR-1",
                Partition.Test, task == TaskKind.Defect ? new[] { "recall" } :
                    new[] { "cer" }, IntervalKind.NotRequested, 950000,
                "none", 0, 7, 2, null);
            return new EvaluationRequest(id, "key-" + id, auth, snapshot,
                binding, plan, budget);
    }

    static async Task<HostRun> RunAsync(GovernanceRoot root, TaskKind task, string id)
    {
        // 根容量先于Factory、hash、深复制与任何端口创建。
        if (!root.TryReserve(4 * 1024 * 1024, out var reserved) || reserved == null)
            throw new InvalidOperationException("DG-008: root capacity exhausted");
        RootSlot slot = reserved;
        Outcome? result = null; Exception? primary = null;
        var cleanupErrors = ImmutableArray.CreateBuilder<Exception>();
        GovernanceSession? session = null; OperationHandle? handle = null;
        CleanupResult cleanup; RetentionAck? ack = null;
        try {
            var budget = new Budget(100, 65536, 262144, 1048576, 100000,
                1, 2000, 1000);
            var ports = new SyntheticPorts();
            var request = BuildRequest(task, id, ports, budget);
            session = slot.Open(ports.Ports);
            var accepted = session.StartEvaluation(request);
            if (accepted.Value == null) throw new InvalidOperationException(
                string.Join(";", accepted.Issues.Select(x => x.Code + ":" + x.Path)));
            handle = accepted.Value; // root已经持有原Completion、端口与所有借用对象。
            result = await handle.Completion.WaitAsync(TimeSpan.FromSeconds(3));
            if (result.State != OperationState.Succeeded || !result.ResourcesReleased ||
                !result.CommitConfirmed || result.Evaluation == null)
                throw new InvalidOperationException(result.ErrorCode ?? "Incomplete operation");
            string endpoint = task == TaskKind.Defect ? "recall" : "cer";
            var metric = result.Evaluation.Endpoints.Single(x => x.Name == endpoint &&
                x.Stratum == "all");
            if (metric.Denominator != 1 || metric.Numerator !=
                (task == TaskKind.Defect ? 1 : 3) || metric.Value !=
                (task == TaskKind.Defect ? 1.0 : 3.0) ||
                result.Evaluation.QualificationGranted)
                throw new InvalidOperationException("Synthetic endpoint assertion failed");
        }
        catch (Exception ex) { primary = ex; handle?.RequestCancel(); }
        finally {
            try { session?.RequestClose(); } catch (Exception ex) { cleanupErrors.Add(ex); }
        }
        // 独立cleanup deadline，不连接业务CTS，且不覆盖primary。
        try { cleanup = await slot.CloseAsync(1000); }
        catch (Exception ex) {
            cleanup = new CleanupResult(false, false, "DG-011", slot.Id);
            cleanupErrors.Add(ex); // 清理错误另轴保存，不丢掉原业务错误或清理错误。
        }
        if (!cleanup.Released) {
            cleanupErrors.Add(new InvalidOperationException(cleanup.ErrorCode ?? "Cleanup unresolved"));
            try {
                ack = slot.TransferToRoot();
                if (!ack.Accepted) cleanupErrors.Add(new InvalidOperationException(
                    "Recovery owner did not accept the retained slot"));
            }
            catch (Exception ex) { cleanupErrors.Add(ex); }
        }
        return new HostRun(result, primary, cleanup, cleanupErrors.ToImmutable(), ack);
    }
}

static class Program
{
    static async Task<int> Main()
    {
        // 此对象由进程入口持有；生产宿主在进程生命周期持续持有并提供恢复查询。
        var root = new GovernanceRoot(new RootLimits(2, 4, 16 * 1024 * 1024, 64, 16));
        try {
            var defect = await TwoHosts.DefectAsync(root);
            var ocr = await TwoHosts.OcrAsync(root);
            var observed = await root.ObserveAllAsync(2000);
            bool ok = defect.PrimaryError == null && ocr.PrimaryError == null &&
                defect.CleanupErrors.IsEmpty && ocr.CleanupErrors.IsEmpty &&
                defect.Cleanup.Released && ocr.Cleanup.Released && observed.Released &&
                root.OutstandingSlots == 0;
            if (!ok) Console.Error.WriteLine("DG-HOST: failure or resources unresolved");
            return ok ? 0 : 1;
        }
        catch (Exception ex) { Console.Error.WriteLine(ex.GetType().Name); return 1; }
    }
}
```

测试端口内没有原生句柄且所有Task即刻退出，合成Host可以有限收尾；非零或外层杀进程只是**测试失败**，不能把它写成成功排空。真实宿主若根仍有未知借用资源，进程/服务的恢复Owner继续持root与查询入口，必须确认外部隔离/释放后才退出；不能以Main返回/用户关窗替代确认。HostRun包含primary/cleanup结果+全部cleanup异常/transfer独立结果，调用者不能只看Business.Succeeded就销毁仍借用的端口。

## 10. 正常、反例、并发和恢复验收矩阵

用例是未来实现的确定性软件断言；尚未创建或运行。Fake端口以`TaskCompletionSource<T>(RunContinuationsAsynchronously)`闩锁控制，不靠sleep竞态。每个原Task公开entered/finish闩锁、调用数、租约数及release数，控制包装等待和底层真实结束是两个不同信号。SyntheticPorts是正常路径；故障端口在唯一测试工程按下面明示行为实现，不成为产品默认。

| ID | 构造/触发 | 必须断言 |
|---|---|---|
| C01 | null draft/request、空必填、非法enum/hash/UTF16、版本9.9 | DG-001/002可定位、无端口调用、无大复制；Check.Value=null |
| C02 | 有效输入Freeze后更改原Members/Regions/Endpoints；用with改返回CopyPlan | 原frozen hash/执行不变；无可写内部引用泄露 |
| C03 | MaxItems/预算非法、checked尺寸溢出、Root只1槽第二Open/Start | DG-008发生在hash/复制/端口前；无静默截断，槽可回收 |
| C04 | snapshot ID同但version/hash变、labels hash变、模型别名或预测method换 | 精确身份失败DG-002/005/013；不读取latest |
| C05 | parent环、缺父、同component异split；唯一少数组、locked留出 | DG-006、建议不拆组；覆盖缺口明确且seed/目标改变可追溯 |
| C06 | observation追加/迟到、同成员两selection、盲审模型暴露 | 旧标签/报告不变；重复拒绝；暴露不冒盲审 |
| C07 | §6.5十项向量 | TP2/FN1/FP1/TN4、条件2/3、2/3、1/5；全量10，端到端2/4，QualificationGranted=false |
| C08 | OCR A→AAAA、😀→空、非法孤立代理项、(AB,C)→(A,BC)、空真值 | CER3、一次删除、编码无效、总距2/3、空真值不造CER；DP超限不截串 |
| C09 | 检测两个预测同truth；无truth合法正常域；分割T0/P0/V100；Query.ValidDomain=(domain-test,r1,abc-hash)，fake返回相同引用/QueryHash，再分别换version/hash/V证据 | 单一TP其余FP；检测无TN；分割IoU未定义而TN100；换域或QueryHash DG-005/013，拒绝统计；原有效域变动不影响冻结query；独立组不足不造区间 |
| C10 | classification缺类/方法拒识；anomaly正常库无异常真值 | 无该类分母不自动1；不造异常召回；原始/合成分层 |
| A01 | 两个§9 Host | defect recall1/1、OCR CER3/1；提交/释放确认，两个root槽归零 |
| A02 | 同operation同hash同时Start、同ID异hash、Store同幂等键异内容 | 同一handle/原Task、执行与提交一次；冲突DG-016，不能换键重执 |
| A03 | 预测entered闩锁后Cancel；原预测故意忽略token | 工作超时不等停止；Completion未完成、DrainUnknown/槽仍持有；释放闩锁后仅一次release并最终Cancelled/Failed |
| A04 | Commit已经落库但回执Unknown；Lookup返回Confirmed | 只查原operation不重写；恢复原ResultId，业务成功不被取消覆盖 |
| A05 | Commit/Lookup均完成返回Unknown；Lifetime完成且全租约归还 | ResourcesReleased=true，Terminal Unknown，原operation持久身份保留但root槽释放；后续新预算Lookup可读原状态、不重执Commit |
| A06 | Lookup原Task未完成，而等待者WaitAsync timeout | 原Task/root/租约仍持有；不可引用A05提前释放；迟到结束后观察异常并唯一释放 |
| A07 | 授权先允许、提交前撤销；Store策略epoch原子核验拒绝 | 不提交；两次权限读不自称原子保障；DG-003且真排空 |
| A08 | callback异常/旧generation迟到/队列满/回调未退出 | 错误隔离，有界背压；旧投影不覆盖；回调未退出不报Drained |
| A09 | primary DG-005后cleanup throw或超时；Close重复/Transfer重复 | primary保留，cleanup独立；root ack=true持原Task；资源归还一次；超时不变成功 |
| A10 | Training模式/配置/seed错、错误拿Test给train、训练候选撤回 | 输入拒绝；Test/Challenge不可见；训练成功非资格；旧撤回不能回退激活 |
| A11 | 软件reader0.2读未知0.3、旧report、失败迁移 | Unsupported不默认；旧身份/原件保留，明确旧reader；新修订失败不覆盖旧 |
| A12 | Freeze草稿后PublishSnapshot，审批/来源缺口和同ID换hash并发 | 仅调用Authorization/Facts/Store/Lifetime，不调用预测/训练；publication回执Confirmed才发布；Missing保留研究gap；同ID异内容DG-016，旧snapshot/label/hash不覆盖 |
| U01 | 两个STA Host正常、三语/长文本、键盘/影像选中 | 同输入与Core校验一致，分母不因筛选改变，无宣传词/隐藏关键命令 |
| U02 | close于预测/Store/投影/Dispatcher阶段、撤权及旧callback | 原Task仍在root，有限观察后确认移交；UI卸载不等业务释放，projection权限失败无图像泄露 |
| U03 | 双STA均选择member-m1：abc 3×1 Gray8、原ROI corners独立hash；然后Clear、Unbind | Open请求operation/generation/MemberId/face/坐标/图ROI精确；Presented时仅确认Dispatcher影像/原ROI投影已应用（真实可见性另测），ResourcesReleased=false；Clear ACK后源release仅一次，watch退出，Close真实完成；缺Evidence另案显示不可用但不影响正常预览 |
| U04 | Open/Show闩锁未完成时切行/换generation；旧Open迟到成功，旧Show迟到Presented，旧Clear迟到 | 立即遮罩但不声称已清空；只有一个latest pending选择；旧lease进入原Owner并唯一清理，全部旧Task/ACK收敛才新Open；旧epoch不能复写新View或清空新DisplayId |
| U05 | 显示中Revoke/Expiry/Gap；Clear原Task未结束、返回Unknown、Release Pending/Unknown；Close/Dispatcher未退出 | 禁新呈现、保持遮罩；读权guard拒绝再次公开；观察到期为DrainUnknown，root移交ACK持原View/lease/Task；仅Query原clear/release。Query确认且原IO退出才Released，清空未知不归还、UI关闭不强删；业务primary不被cleanup错误覆盖 |
| U06 | Root不足11槽/bytes；固定槽在途重启；普通启动数逼近边界后停止，Open迟到带watch | 预约失败源/桥零启动；在锁外delegate前占位，拒绝不调用delegate；捕获额度先预约，accept先持lease再登记watch，Work停止不丢迟到资源且不耗清理尾额；Cleanup/Observation仍能在lifetime在途时启动，不绕过RootLimits/MaxStarts |
| U07 | Show等待Clear信号才退出；watch仅在Release后Closed；Bind、Unbind、业务故障同时cleanup异常 | Bind登记lifetime后及时返回；Show未完成也先发Clear/Close，NoFurtherReads及原Show退出后才Release，再汇合watch；不等自己scope/父slot；primary与全部cleanup异常分别保留、非零退出；Presented只为Dispatcher应用回执，真实渲染另门 |

训练契约Fake采用全新合成Train/Validation各一组、test/challenge各一组：TrainAsync仅调用训练视图CopyMembers(Train/Validation)，尝试Test必须拒绝，按输入Snapshot/Config/Toolchain精确填TrainingProduct，CandidateModelAssetRef为abc hash、RunEvidence为测试Revision；不跑真正模型。统计Fake返回明确NotComputable或具名fixture区间，不冒真实覆盖；用途Fake返回外部已给决定Active/Withdrawn，模块只投影。区域Fake为显式T/P/I/V小整数，必须覆盖HALCON空域/坐标错误反例；它不证明真实区域算法。

## 11. 唯一工程、测试与有限执行

| 切片 | 唯一工程/namespace | 验证落点 |
|---|---|---|
| C1 值/Freeze/canonical/分组建议 | `src/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Core/Asun.Modules.AiDatasetGovernance.Core.csproj`；`Asun.Modules.AiDatasetGovernance` | 以下唯一Core.Tests Exe的C01–C08、C10、Golden |
| C2 执行端口/Root/评价训练治理/事件 | 同Core工程，不另建空包 | 同Exe的A01–A12、算法Fake C09 |
| A1 真实来源/Store/训练推理/区域/统计/用途Adapter | `src/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Adapters/Asun.Modules.AiDatasetGovernance.Adapters.csproj`；`.Adapters` | 同Exe只验证端口模拟；真实integration按同项目独立受控运行mode |
| U1 可选控件 | `src/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Wpf/Asun.Modules.AiDatasetGovernance.Wpf.csproj`；`.Wpf` | `tests/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Wpf.Tests/Asun.Modules.AiDatasetGovernance.Wpf.Tests.csproj`，net10.0-windows Exe/UseWPF/STA |

Core唯一测试工程：`tests/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Core.Tests/Asun.Modules.AiDatasetGovernance.Core.Tests.csproj`。Microsoft.NET.Sdk、OutputType=Exe、TargetFramework=net10.0、Nullable=enable、ImplicitUsings=enable；仅ProjectReference受测Core及BCL，不新选xUnit/NuGet，不跑dotnet test冒通过。Core工程同SDK/net10.0，TreatWarningsAsErrors=true；WPF只用本机固定程序集和相应ProjectReference。

正式实现允许写上述本模块src/tests；禁止其它模块/共享契约/产品页面/私表/原件/AsunImage内部。**本轮文档任务只写本文，不创建工程/源码/测试/脚本。**产品代码开工还须取得权威仓库/分支或已确认代码快照，本地无.git不冒称HEAD。

未来执行命令（当前未执行）：

```powershell
dotnet build src/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Core/Asun.Modules.AiDatasetGovernance.Core.csproj -c Release
dotnet run --project tests/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Core.Tests/Asun.Modules.AiDatasetGovernance.Core.Tests.csproj -c Release
dotnet build src/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Wpf/Asun.Modules.AiDatasetGovernance.Wpf.csproj -c Release
dotnet run --project tests/Modules/ai-dataset-governance/Asun.Modules.AiDatasetGovernance.Wpf.Tests/Asun.Modules.AiDatasetGovernance.Wpf.Tests.csproj -c Release
```

Core测试入口按固定case ID执行全部C/A用例，每case独立根和5秒观察deadline，suite90秒截止；闩锁清理用独立1秒cleanup+2秒根观察，仍未释放或异常/必需跳过均非零并输出case ID/primary/cleanup/root槽数。5秒只测试工程可终止性，不是客户时延目标。外层CI/调用宿主用120秒进程截止，超时终止测试树并非零，记录资源未决，不能把suite因WaitAsync提前返回视为0。WPF case15秒、suite180秒、外层240秒，使用Dispatcher完成闩锁，不sleep等待渲染；截图/模拟不冒真实训练/现场资格。

外层PowerShell执行时可用`Start-Process dotnet -ArgumentList <上面run命令参数> -PassThru -WindowStyle Hidden`，`WaitForExit(120000)`，超时调用该Process.Kill(true)、记录timeout并exit 124；否则exit原ExitCode。不得无deadline启动并遗留看不到的测试进程。该例是runner操作规范，不新增工具文件或自动运行。

## 12. BenchmarkProfile、预算与观测

U1预览另绑定image/ROI/有效域完整引用、图幅/stride/层级/字节、Display surface尺寸及解码/纹理副本预算、选择切换频率、单一pending选择、watch/Dispatcher积压与根保留量；测选择→真正呈现、撤权→遮罩、清空请求→NoFurtherReads ACK、release→watch退出、Unbind→Bridge.Close确认。合成Host显式2MiB预览额度加原4MiB根槽，不把3字节源像素当全部显示内存；真实viewport/GPU不可观测项写Unknown，不据此达标。

统计唯一沿[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md)，不另复制分位算法。消费者先冻结Profile身份、Core/adapter版本/hash、数据/标签/模型/方法/预算、OS/.NET/CPU/GPU/存储、负载、并发、预热/测量数/最低有效数、deadline和目标来源。模块负载维度：members/groups/谱系边/strata/class/region对数、输入/输出UTF8字节、原/派生证据字节、总DP cells、canonical字节、冷/热、Fake/真实IO、source读权命中率、interval resamples、训练mode/batch、事件/投影积压。Fake负载和native/现场分开，不混报。

测点：root预留→输入尺寸预检→复制→canonical/hash→引用/谱系/split→授权/Facts→预测/训练→匹配/文本/统计→提交/查询→真实排空/释放；纯C1端到端至临时副本/配额释放，C2至ResourcesReleased，另记取消到真实停止与cleanup观察。报告P50/P95/P99及n、分配/托管峰值、native/GPU/原Task/slot/队列高水位、每类终态、超时/拒识/失败/未计算/未排空；不可测写Unknown，不写0。只有确认释放样本进入完成分位，同时单列未决/删失/失败，不能隐藏它们判通过。

诊断软件Profile建议测试桶10/100/1000项，1/2并发，每桶冷1次、热预热3次测量20次，明确不足以可靠声明客户P99；客户实测样本计划与性能目标沿获批Profile，不从此表填达标值。缺目标允许测量但NotEvaluated；资源未决不能性能通过。预算与负载均需计输出副本、pair图、匹配多轮求解、DP/traceback、Store与投影任务，不能只计输入byte[]。

日志用OperationId/Generation/Sequence/RequestHash/阶段/错误/预算/分母缺口/提交状态/原Task是否退出/释放回执/移交ack；脱敏不写原图/完整OCR文本/密钥/秘密路径。指标低基数，不用每member或完整hash做label；受权限operation查询承担逐项调查。


S6桥Profile另显式冻结G独立组、B重采样、最大原始/交叉BigInteger位数、来源/closure/canonical字节、最多draw/rejection、失败/缺失/未知组率及配对不完整率，测完整字段封口/hash→managed compute→结果校验/有界证据消费→原engine Dispose→root Released；给出冷/热P50/P95/P99、buffer/工作集峰值、Cancelled/Undefined/RangeLoss/BudgetExceeded及未排空数。G/B/MaxPrngOutputs是输入预算，客户精度/节拍目标仍Profile TargetPending，不据G=2/B=8合成夹具宣称统计精度或性能通过。两个Host留在§11既有Integration mode，无新的产品csproj/UI/统计实现或报告Owner。

Qualification桥Profile见§13.1.4.1：明确案例/父组数、Profile/Recorded/源引用bytes、完整尝试/采样明细、预热/测量/并发、Prepare/Invoke/Total/Cleanup预算、目标原来源与metrics能力。Golden只消费原封存结果，不把报告读取时延叫推理性能；Recorded只分析原tick，不把当前Decode耗时混入源Queue/Service。Execute测真实纯计算probe屏障及端到端资源释放，当前分析Root与源SourceRun分别记。BP01的三次软件调用与100-byte采样仅fixture闭包验证，不能证明客户P99、GPU峰值、长稳或节拍；未来真实Profile由原Owner冻结，与本模块治理全链性能报告分开。

本轮Adapter性能验证补入原§12范围：训练记录真实已消费成员/重复位置、完整native更新/validation/fresh-read/seal/治理提交分段时点及取消到真实停止，峰值含预处理缓存、有效B个图/字典、训练模型+validation/候选新旧并存和输出磁盘，不拿CPU/gpu额度当实测峰值；Region按有效域行段/候选对数/对象数测整链，不仅量intersection；预览同时记录原源借用、CopyPublish、viewport旧/新/空Presenter及baseline归还，以Clear确认/下一Update/Close为测点；存储覆盖完整信封、全refs、并发同键及文件成功DB未知恢复。每条沿原§12已冻结冷热/分层/完整分母/P50/P95/P99/峰值/资源测法，同源Profile不变复用有效记录。上述都是未来测点，尚无性能数据；客户节拍/资源容量只影响其生产资格。

## 13. 发布、独立性与真实接入门

Core可独立build/test/release，无Dispatcher/DevExpress/数据库/设备SDK/HALCON；Adapters注入真实Owner公共端口，Wpf可完全不引用。无UI能力不能依赖窗口Loaded；WPF使用同Freeze/Start，宿主负责语言与生命周期。两个独立消费者只更换输入与公开端口，不修改Core，测试有明确第二消费者。包版本/契约版本/方法revision分开；公开破坏变更Major，不以新增可选字段掩盖分母/判定变化。

发布绑定程序集hash、显式依赖、合同/方法版本、实际测试结果、BenchmarkProfile、旧reader/迁移策略及撤回说明。只把已有且有consumer/gate的fixture/证据纳入，不堆重复报告/manifest。型号/设备/客户阈值不进公共包。模型资产和报告有各自原身份；模型alias可作为UI显示，执行前必须解析为已确认精确资产+闭包，并锁定同一运行，不在两个调用间重新读latest。

真实Adapter以如下不交叉写入的映射接入：data/label治理事实由本模块，复判观察/仲裁回执由human-review；model-assets供精确资产、ai-inference/OCR供原预测，qualification供分析/性能报告，用途由外部采用/授权Owner签发，storage-database只供持久化技术事务。签名/能力/取消/租约已按§13.1逐项映射当前指导公开API，本文不伪造其它模块的已发布程序集；精确不支持项单列，不一概写成“等待客户”。

### 13.1 A1确定映射：原Owner公开契约与确认点

本轮只读绑定：ai-inference **0.5.0-prep / API0.3**、model-assets **0.3.0-prep / Service0.3（S1软件六项已接收，PureCore v0.2保持）**、storage-database **0.3.0-prep**、statistics **0.3.0-prep / Core API0.3（S6六项规格于2026-10-11已主控接收）**；qualification **0.2.5-prep / Contract0.2（Core/Study/Replay及Benchmark执行/录制分析原接收保持，§6.4/A.3.1.1 Deming专用桥已主控限定接收）**；statistics S7已接收，本模块无当前Deming消费需求，确定边界见§13.1.7。此映射是本模块Adapter实施规格，不要求现有程序集已经构建；上游指导发生破坏变更时重读受影响字段，不猜签名或修改其它模块。

| 本模块入口 | 原Owner与公开入口定位 | 固定输入/输出映射、确认与失败 |
|---|---|---|
| IFactPort：模型完整性 | [model-assets §5A/附录B](../model-assets/DEVELOPMENT-GUIDE.md) `IModelAssetService.ResolveExactAsync(AssetResolveRequest,token)`；`AcquireContentLeaseAsync(ContentLeaseRequest,token)` | Adapter启动显式注册有限`ModelAssetRef→AssetRef(AssetIdentity,Digest)`表，URI hash须等于原Digest.Hex；同hash可多identity时拒歧义，不能只凭hash猜namespace/id/revision。Context固定Scope/OperationId/RequestDigest/RequestEpoch/ProfileId/ProfileRevision/Budget；Scope与Service.SessionInfo.Scope及Options.Scope相同、Access.PrincipalRef与可信Service固定PrincipalRef相同；ProjectResolve按model-operation-jcs-v2完整语义生成RequestDigest，不用DG BindingHash/URI文件hash冒操作摘要。ResolveExact返回ServiceResult<ResolvedClosure>，先核Observation.QueryStatus=Found、原OperationId/RequestDigest/Epoch、Outcome=Succeeded、Value非null、Errors与OwnedResources；仅再读取Value。DependencyPurpose按真实用途显式选，不给ReadHistory隐含ReadForUse。ResolvedClosure须RootRef精确、同StoreView、Completeness=Complete、UnverifiedLegacyRefs为空且预后处理/schema/taxonomy/threshold依赖都存在；失败/Unknown回ClosureReceipt中false/Unavailable，不补缓存最新 |
| IExecutionLifetimePort：模型内容 | 同服务`IAssetContentLease.OpenFileAsync(ContentOpenRequest,token)`、`ReleaseAsync(ResourceReleaseRequest,token)`；`QueryResourceAsync(ResourceQuery,token)` | Acquire同样核ServiceResult<IAssetContentLease>的原身份/Outcome/Value/OwnedResources，先接管成功lease再返回。OpenFileAsync返回ServiceResult<ContentReadLease>，只从Value读取成功子lease；内容lease类型是公开interface，不是可new DTO。仅打开closure列出的OwnerRef/role/path，用ProjectAcquire/ProjectOpen(父LeaseId,request)各自生成原操作摘要，按ReadOnlyStream实际EOF核ActualLengthBytes/FileDigest与原Entry。ContentReadLease及父IAssetContentLease均由adapter强持，子真实读完/退出→子release→父release；Released与PendingChildren确认，不把Acquire成功/业务Outcome当释放。Dispose完成前保留原Task，DrainUnknown原ResourceId查询；独占service才Drain/Dispose，共享service不可被一份评价停止 |
| IPredictionSource：新计算/原预测读回 | [ai-inference 附录A.1/A.4、§6.6](../ai-inference/DEVELOPMENT-GUIDE.md#a1-core-公开类型与边界) `IAiInferenceEngine.Validate/InferAsync(InferenceRequest,token)`、`QueryAsync(InferenceRequestId,token)` | Adapter配置显式有限`RevisionRef→InferenceContentReference`及输入values/shape/strides/layout/schema/坐标闭包映射，不从当前Store猜。RequestId=本operation的固定inference子ID，Consumer/Purpose/Attempt各自稳定修订；Model/Pre/Post精确引用，Input.ItemId=MemberId、Sequence按固定成员序，TaskKind映射Defect/Classification→classification，Ocr→ocr-comparison，Detection→detection，Segmentation→segmentation，Anomaly→anomaly。缺任务层/类表/阈值映射DG-013，不运行未知模型。已有运行回读由宿主已登记原InferenceRequestId用QueryAsync读取，不能自动再Infer |
| IPredictionSource：结果解码 | `InferenceResult`/`InferenceItemResult`及`ai.final-item v1`固定schema | 逐项核RequestId/Attempt/Model/Pre/Post/task/schema/OutputSha256/完整性和原义务。Completed解码selectedClassId/rawText/candidates/shape+classIds+validity/anomaly真实阈值后的类别；原score不自称Probability，Rejection不隐含正确。Rejected→Abstained（仅受支持的LowScore/Ood等政策并保留原只读诊断），Missing/Unknown→NotExecuted或Invalid并说明；Failed→Failed；Cancelled/TimedOut沿原终态拆分；无合法可消费原串不计算CER。OutputComplete=false或WasTruncated=true保留缺口，不静默补正常；OCR符号框缺省保持缺省。Canonical最终输出解析沿上游codec规范，不复制第二套推理算法 |
| IExecutionLifetimePort：推理 | `IAiInferenceEngine.DrainAsync(InferenceDrainRequest,token)`、`QueryAsync`、`IInferenceBackendLease.DrainAsync`由引擎内拥有 | Infer返回后核ResourcesReleased；若native可能继续，保留原engine/request/lease/Task，按原Query观察。独占engine才全实例Drain，AllOperationsDrained/InstanceStopped明确且原Task退出后Dispose；共享engine只取消自己的原请求，不停其它consumer。旧generation输出只归原operation，不能写新session |
| IReportStore：原子报告/标签/快照写与查询 | [storage-database §6/6.3/7.2](../storage-database/DEVELOPMENT-GUIDE.md#6-公开集成契约module-api-contract-v03-的-io-部分) `IStorageDatabase.OpenSessionAsync(SessionRequest,ct)`；`IStorageSession.ExecuteTransactionAsync(RegisteredTransactionRequest,ct)`/`ReadAsync(RegisteredReadRequest,ct)`；`QueryOperationAsync(OperationQuery,ct)`/`GetTaskStatusAsync(TaskQuery,ct)` | ownerKey固定ai-dataset-governance；Adapter注册本模块Transaction及Read Binding/Schema/Codec，不送任意SQL。OperationIdentity.Scope/Store/Generation来自宿主注册、OperationId/IdempotencyKey原值、PayloadHash用`StorageRequestHasher.Compute(request,binding,canonicalPayload,limits)`算**存储信封hash**；本模块RequestHash另在payload保留，二者不互相冒充。execute输出只有StorageExecutionState.Completed且TechnicalCommitReceipt.State=Committed、Identity/ResultSchema/ResultBytes匹配才CommitStatus.Confirmed；RolledBack/Rejected明确NotCommitted；Unknown/NotFound/ResultExpired→Unknown，不新键重执 |
| IReportStore：字节大对象及恢复 | `IFileObjectStore.StageAndSealFileAsync(FileObjectRequest,Stream,ct)`/`VerifyAsync`/`OpenReadAsync(FileReadRequest,ct)`；`IStorageSession.ReleaseAsync`及`IFileObjectReadLease.ReleaseAsync` | 有界canonical报告可内联；超过已注册row上限时先封为文件对象，只有SealedDurable+精确ObjectRef才可在事务引用，不用Verified冒耐久。数据库同一事务写不可变本模块报告/引用/唯一回执，未引用暂存保留原GC规则，不因失败自行删文件。原TaskHandle看执行资源，原OperationIdentity看耐久知识；Task已Completed+Unknown且租约Released允许本模块Terminal Unknown、root腾槽，后续只QueryOperation；I/O仍在途则保留root。先归还读lease/Session，确认ResourceState.Released/ActiveOperations=0，独占Runtime才Stop/Dispose |
| IStatisticsPort：当前数值能力 | [statistics §7.1.3/附录A](../statistics/DEVELOPMENT-GUIDE.md#a1-core-public-entry-points) `IStatisticsEngine.Compute/ComputeAsync`、`StatisticsRun.Completion/CancelAsync`、`QueryOperationAsync/DrainAsync` | 治理整数分母/coverage在本Core确定计数，不交SPC去决定真值。可选趋势/事件率投影用StatisticsObservation(kind CountExposure或ClassifiedUnit)/StatisticsInput/StatisticsRequest，scope/input fixed snapshot/hash/ExpectedMembers/Completeness.RequireAll绑定；FP/board用EventRate与board exposure，不能改成UnitRate。实际方法/Capabilities必须受支持；结果需DrainState.Drained/CanReuseResources，不把通知OutputReturned当已完成；statistics不保存事实，由本模块Store提交 |
| IStatisticsPort：S6整组区间/配对比较 | [statistics §7.1.3.9](../statistics/DEVELOPMENT-GUIDE.md#group-interval-bootstrap) `INumericalStatistics.ComputeNumerical/ComputeNumericalAsync`，`NumericalRun.Completion/CancelAsync/DisposeAsync`、`QueryNumericalOperationAsync` | GroupRatioTask/GroupPairedRatioTask及完整Policy/Budget/Coverage/Source/外层NumericalRequest按§13.1.1–3闭合；不再一概Unsupported。仅未注册OwnerMethod、超S6支持域或未发布运行能力明确不支持。完整NumericalResult/GroupIntervalResult保留，简要IntervalResult不得代替Provenance/计数/资源确认；不借SPC或qualification猜CI方法 |
| qualification evidence消费 | [qualification 附录A.1–A.3、A.3.3、A.5](../qualification/DEVELOPMENT-GUIDE.md) `ValidateDesign/EvaluateGoldenAsync(GoldenRequest,token)`、`BenchmarkAsync(BenchmarkRequest,token)`、`CancelCalculationAsync/QueryCalculationAsync(CalculationQueryRequest,token)`、`StopAsync(waitBudget,waitToken)` | §13.1.4–6完整GoldenPlan/QualificationRequest、BenchmarkProfile/WorkPlan/Recorded输入、Root/Factory/原Task/结果恢复和codec边界。Core/Study/Replay及Benchmark软件规格现已接收；本模块Golden/Benchmark确定桥已限定指导接收，不再一概写成DTO待定。治理义务与资格原案例/性能窗口分别保存，不授用途批准。Deming上游桥已限定接收，本模块无当前消费者，不新增桥，复用边界见§13.1.7 |
| IUsageDecisionPort/IAuthorizationPort | 外部授权/采用Owner，不调用qualification不存在的ReadStage/ApproveModel | qualification当前公开契约未定义生产用途决定读取。Adapter只接受宿主显式注入的本模块IUsageDecisionPort/IAuthorizationPort，精确OwnerDecision、期限、scope、model/report绑定，未知回执拒绝；这是确定公开边界。真实authority传输/凭证与产品阶段决定Schema尚未正式接入，禁止Automatic真实采用，仅允许诊断与原决定只读投影；不让qualification计算器替代人类授权 |
| ITrainingPort/IRegionMeasurePort | §2.2/§6.6/§7的AsunImage目标26.05路线；实际训练产品交model-assets `ImportAndSealAsync(AssetImportRequest,ImmutableArray<ContentInput>,token)` | 训练端口独占worker/模型句柄与输出源流；先由原Root持输入和原Task，用ProjectImport完整投影填Context.RequestDigest，ExpectedAbsent=true注册。返回ServiceResult<SealReceipt>先核Observation.QueryStatus=Found、原OperationId/RequestDigest/Epoch、Outcome=Succeeded、Value及OwnedResources，再核Value.CommitStatus=ConfirmedCommitted、RequestDigest相同、精确Ref/非空StoreReceiptRef；Files按每个ClosureFile完整身份核ActualLengthBytes/ActualFileDigest/ObjectReceiptRef/ConfirmedDurable，与实际读到EOF的输入完全一致且无缺项/意外项，才填CandidateModelAssetRef。ServiceResult与SealReceipt.EvidenceMode必须等于原Service.SessionInfo/Options；Simulation只保留软件候选证据，不写成Production保存或生产可用。Unknown保留原seal OperationId/ExpectedRequestDigest用QueryOperationAsync查询，不再训练、换ID或注册新身份；NotFound不证明未提交。region端口逐对intersection/area，无批量Region2误union；坐标/有效域/空域/参数固定，原native退出确认后释放。训练算法/native签名实质歧义和真实区域证据只影响此Adapter，不影响其公开端口/治理规格 |

### 13.1.1 S6完整请求构造（A1-Stats；仅本模块Adapter伪码）

本节是本模块调用上游 `statistics 0.3.0-prep / Core API0.3` 的逐字段接线，代码形状仅表示未来Adapter/TestHost调用，不声明程序集或方法已经编译。`GroupRatioTask` 与 `GroupPairedRatioTask` 是 statistics 已公开 DTO；本模块不再把所有 GroupBootstrap 写成 Unsupported，也不复制分位、PCG 或配对算法。统计输入只来自已冻结的 EvaluationResult/PredictionBatch 与其原 Owner 的来源回执；治理不读取原图、OCR 原串、模型文件或权限表来凑组。

每个组先由本模块从**原评价事件**形成完整 `GroupIntervalObservation`：`GroupId` 是已批准的板/批次独立单位，`EndpointName`、`NumeratorUnit`、`DenominatorUnit` 在任务内统一；`Numerator`/`Denominator` 是该 endpoint 的冻结计数。`GroupCoverageEvidence` 的 `Obligations/Covered/NotCovered/Failed/Missing/Unknown` 和五项 `FailureCoverageCrossCounts` 从事件明细逐项守恒生成；不把 `Coverage.Failed` 当分子，不把 `MissingTruth`、`Abstained` 或 `Incomplete` 反推交叉计数。每个左右来源都有独立 `ObservationReference(ObservationId, SourceRevision, ContentHash, EvidenceReference)`；hash 和证据引用来自原 Owner，缺失或没有读取权时在接纳前拒绝。组排序由 statistics 的 Ordinal 规则完成，不能沿用文件到达顺序。

外层固定值必须完整提供：`InputReference(SnapshotId, SnapshotRevision, FixedSnapshot, QueryReceiptId, SourceBoundary, ContentHash, WatermarkId, ReadComplete, CanReplay)`、`InputClosure(ExpectedMembers, ExpectedMemberSetHash, ReadComplete, PopulationClosed, ClosureReceiptReference, Gaps)`、`DefinitionReference Method/SelectionPolicy`、`CompletenessPolicy`、`NumericalPolicy` 和 `NumericalBudget`。`ContentHash` 按 statistics §7.1.3.9 的 `s6-field-encoding-v1` 由已封闭输入生成；本模块不另造 JSON/序列化格式。若 `ReadComplete/PopulationClosed`、成员集 hash、方法/选择正文、任一来源 hash 或预算未冻结，返回 DG-002/DG-008，不调用 engine。

S6 task 还必须逐字段冻结 `GroupIntervalPolicy(Identity, MethodRevision, Tail, ConfidencePpm, Resamples, Seed, MinIndependentGroups, PrngRevision, QuantileRevision)` 与 `GroupIntervalBudget(MaxGroups, MaxResamples, MaxIntegerBits, MaxPrngOutputs, MaxBufferedBytes, WallClockLimit, CancellationResponseLimit, DrainObservationLimit)`；task/outer预算逐项取较小值。当前支持声明为 `MethodRevision=group-percentile-bootstrap-v1`、`PrngRevision=pcg32-xsh-rr-v1`、`QuantileRevision=linear-hf7-v1`、`Tail=TwoSided`，`ConfidencePpm=1..999999`、`Resamples≥2`、`MinIndependentGroups≥2`。组数不足、零分母、单位/endpoint不一致、交叉计数不守恒、预算或 `MaxPrngOutputs` 不足均在接纳前或任务结果中保留明确 S6 诊断，不降级为 Wilson/独立 Bernoulli 或删组。

| 字段族 | 原输入→S6逐字段绑定与拒绝点 |
|---|---|
| 每组统计与覆盖 | `Numerator/Denominator`为endpoint的整数充分统计；`GroupId`=已冻结独立单位。`Covered`=真值已批准且预测Completed/合法Abstained可评价的义务；`NotCovered`=已观察但不能评价的义务；`Missing`=预期但未读到义务；`Unknown`=已观察但覆盖状态未知。`Failed`只标原执行Failed/Cancelled/TimedOut等失败事实，不能从分子反推；Abstained不是执行Failed。按每条事件交叉累计四个Failure×Covered桶，unknown桶独立，严格核四条守恒。MissingTruth不等于Missing读取，不能靠旧GroupStatistic重建交叉表 |
| 旧query与闭包装配时点 | 每operation只绑定一个显式Owner，内含FrozenEvaluation/Labels/ModelBinding/Plan、原PredictionBatch/事件、完整统计request/回执；在本次预测读取完成并被原Owner接管后封口S6请求，再给本次IStatisticsPort调用。产品Adapter可在同一个Owner构造时显式注入有界`Func<IntervalQuery,NumericalRequest>`：仅读取已冻结Owner值、按上述规则构造，无IO/全局查询；输出完整请求和旧query各字段须一致，未完成Source/事件/方法来源就拒绝。旧GroupStatistic的MissingTruth/Abstained/Incomplete仍与Owner事件投影逐项相等，作为治理证据保留，不能改名充S6.Coverage.Missing/Failed；不一致DG-005。此委托只属Adapters构造参数，不改Core接口、不要求预先猜预测结果；下方夹具使用已封口request直接装配 |
| 政策/方法/单位 | Method/SelectionPolicy/Policy.Identity均是Id/Revision/完整正文hash；GroupIntervalPolicy的全部10字段显式给定。只支持同endpoint的pooled ratio或left−right；`macro-recall`的类算术均值不是pooled ratio，未经另外批准估计量不得映成S6。IoU/Dice等须该方法已冻结组级充分统计/有效域闭包，不把样本均值改pooled后沿用旧端点名。PRNG初始化initseq=54、Seed:uint；不使用System.Random |
| 数值外层策略 | Identity=engineering-binary64-v1完整hash；9值依次`1e-14,1e-12,1e-10,1e-12,8·2^-52,5e-12,5e-12,1e-10,1e-9`，按官方已冻结策略，不填缺省/放宽门；GroupIntervalPolicy不替代此NumericalPolicy |
| 输入/请求身份 | SnapshotId/Revision、查询回执/来源边界、水位nullable、ReadComplete/CanReplay来自本次封闭读取；Closure.ExpectedMembers和成员集hash计独立组（paired G而非2G），PopulationClosed独立证明。FixedSnapshot、RequireAll、ObservedSubsetApproval=null；Gaps为空只适用完整Host，不掩盖生产缺口。Policy/Budget/source/左右计数/seed/方法变动均生成新完整输入hash和原operation内容摘要；OperationId固定由宿主分配，同ID异hash拒绝，不把snapshot hash当RequestHash |
| 有限预算 | DG.MaxItems限制S6 MaxRows/MaxGroups；MaxWorkingBytes限制NumericalBudget.MaxWorkingSetBytes及同时存活输入/数组/BigInteger/结果/hash scratch；WorkTimeoutMs/CleanupTimeoutMs限制task与outer wall/drain。MaxTextUtf8Bytes/MaxCanonicalBytes由Adapter先核完整字符串/编码，不冒成S6的不同字段；MaxDpCells不用于S6（无OCR距离计算）；MaxParallelism首桥=1。task专属MaxResamples/MaxIntegerBits/MaxPrngOutputs/CancellationResponseLimit与outer的MaxColumns/Categories/Tasks/DetailRows/Diagnostics/Notifications显式由Adapter Profile给定，不能从DG无对应字段猜值。下面小型夹具外层2/2/1/1/1/0/64/256/1MiB/4MiB/5s/2s/64，task2/8/256/64draw/1MiB/5s/1s/2s；Root保留8MiB含输入编码/工作集/结果与Owner，不把3字节图当工作预算 |

公开结果必须保留整个`NumericalProvenance`：CoreApiVersion、ImplementationVersion、Input、Closure、Method、SelectionPolicy、SubsetApproval、NumericPolicy、MemberSequenceHash及Backends；不要只留下方夹具所核的子集。完整来源Closure里的预计独立组与每组义务/错误机会分母是不同数量。实际backend只在发布Capabilities声明S6 TaskKinds与`managed-group-percentile-bootstrap-v1`已运行Validated时可用；本轮规格接收不保证已有可执行DLL。

两种 task 的构造保持原义务语义：

~~~csharp
// 以下为 Adapter 伪码；MakeObservation 只接受已核验原事件和 Owner source hash。
var ratioTask = new GroupRatioTask(
    taskId, endpointName, ratioUnit, groupPolicy, groupBudget,
    groups.Select(g => MakeObservation(g.GroupId, endpointName,
        g.Numerator, g.Denominator, g.Coverage,
        new ObservationReference(g.SourceId, g.SourceRevision,
            g.SourceContentHash, g.EvidenceReference)))
        .ToImmutableArray());

var pairedTask = new GroupPairedRatioTask(
    taskId, endpointName, "candidate", "baseline", "ratio-difference",
    groupPolicy, groupBudget,
    pairedGroups.Select(g => new GroupPair(
        g.GroupId,
        MakeObservation(g.GroupId, endpointName, g.Left.Numerator,
            g.Left.Denominator, g.Left.Coverage, g.Left.Source),
        MakeObservation(g.GroupId, endpointName, g.Right.Numerator,
            g.Right.Denominator, g.Right.Coverage, g.Right.Source),
        g.PairingKey)).ToImmutableArray());

var request = new NumericalRequest(
    operationId, inputReference, closure, method, selection,
    null /* RequireAll没有子集批准 */, CompletenessPolicy.RequireAll,
    numericPolicy, outerBudget,
    ImmutableArray.Create<NumericalTask>(ratioTask /* or pairedTask */));
// request 的 Input.ContentHash、任务排序 hash、Policy/Budget 必须在调用前已封口。
~~~

`GroupPairedRatioTask` 要求同一 `GroupId`/义务层级/`PairingKey` 的左右闭集；左右各自的来源、覆盖和分母都保留，差值固定为 candidate−baseline。不能先取有交集的组再声称完整，也不能把左右观察数加倍为独立组数。任务只含一个 `EndpointName`，一个请求可含多个 task，但每个 task 的方法、预算和资源诊断独立落在结果中。

### 13.1.2 两个无 UI 消费者与完整调用链

**缺陷外观消费者（ratio）。** 从冻结 `EvaluationResult.Events` 按MemberId回连FrozenSnapshot成员的 `GroupId`/已批准group key 聚合 recall、precision 或 event-rate 的原始分子/分母，并由覆盖事件生成完整 `GroupCoverageEvidence`。构造一个 `GroupRatioTask`，在 `NumericalRequest` 中绑定同一 Snapshot/Labels/ModelBinding、固定方法/选择/seed/预算；调用 `INumericalStatistics.ComputeNumerical(request, CancellationToken.None)`，读取唯一 `GroupIntervalResult`，校验 `TaskId/EndpointName/MethodRevision`、`Estimates[0].RawTotal*`、约分后 `Total*`、Point、Lower/Upper、`Diagnostics` 与 `Provenance`。该结果只能追加到 EvaluationReport 的 interval evidence；不修改 `Prediction`、`QualificationGranted`、UsageDecision 或模型资产。

**OCR 候选比较消费者（paired）。** 从同一冻结成员集的 candidate/baseline 原预测结果和原真值事件生成左右 `GroupIntervalObservation`，endpoint 选用已冻结的 `auto-accept-error` 或同义 ratio，`PairingKey` 固定为原义务身份；左右分别保留拒识、缺失、非法原串和完整覆盖诊断。构造 `GroupPairedRatioTask`，调用同一 `INumericalStatistics` 入口，校验 `RawLeftTotal*`、`RawRightTotal*`、交叉差值 `RawTotal*`、约分后左右/差值、共同组数、Invalid/Cancelled/Unexecuted 计数、边界和共享 PRNG hash。比较结果只作为报告中的候选差异证据，不把 candidate 区间转成部署/资格决定；OCR 原串和读权仍由 ai-inference/数据 Owner 控制。

两消费者均先完成根容量与输入闭包预检，再构造不可变 request；统计消费阶段不重启预测、训练、Store 或 UI，生产引用的原预测须已在原Owner完成。同步 Compute 返回前由 Core 释放 managed scratch；宿主engine仍须确认Dispose完成。完整结果在归还报告本地额度前消费/有界封口，不能因只返回IntervalResult而丢掉未消费证据。异步接线则 `await statistics.ComputeNumericalAsync(...)` 取得 `NumericalRun`，强持 `Completion`、原 request 和 engine，`CancelAsync` 只表达停止意图，观察取消/超时不能销毁 run。只有原 `Completion` 已结束且 `QueryNumericalOperationAsync` 返回同OperationId的 `Status.DrainState=Drained`、`Status.IsTerminal=true`、`Status.CanReuseResources=true` 后才 `run.DisposeAsync`；若等待被取消，使用原 `OperationId` 的 `QueryNumericalOperationAsync` 查询，不新建相同 task 或换 seed 重跑。清理/Dispose 异常单独进入治理 cleanup 诊断，不能覆盖原业务错误。

#### 13.1.2.1 从空Host装配的完整小型夹具与桥

以下两个入口为**未来本模块Integration TestHost的独立mode源码形状**，Microsoft.NET.Sdk/net10.0/Exe/ImplicitUsings，不复制§9 Program或STA入口进同一次编译。引用本模块Core、Adapters与statistics Core DLL；只依BCL，无Window、HALCON、DB、训练模型。一个验证单模型ratio的既有IStatisticsPort，另一个验证配对报告装配；它们都从空Host显式构造完整DTO，不调用统计模块的测试程序集/私有工厂。`governance-rate`是合成一般计数endpoint，仅测试桥；真实业务endpoint必须沿§6.8明确注册，不宣称此样例已运行缺陷/OCR生产评价。

编码helpers是对statistics §7.1.3.9唯一s6-field-encoding-v1的**小型调用方夹具实现**，不实现统计算法；仅支持本例空Gaps，生产按原Owner完整规则封口。helpers与Build参数正文读取于statistics 0.3.0-prep，本段来源helpers UTF-8 SHA-256为 `a833fa0890da83f33807a9cd1ad2411d5fe436a14230592e91f600cae003c67d`；没有新增运行依赖或第二活动编码规范。四侧来源/政策hash全部按完整字段生成，空hash只在封口前局部临时记录存在，不提交engine。

~~~csharp
using System;
using System.Collections.Generic;
using System.Collections.Immutable;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.Statistics;
using DG = Asun.Modules.AiDatasetGovernance;

// 本地TestHost夹具；所有helpers属于调用方，不是新增Statistics/Governance公开API。
static class S6Fixture {
static void S(BinaryWriter w, string v)
{
    var bytes = new UTF8Encoding(false, true).GetBytes(v);
    w.Write(bytes.Length); w.Write(bytes);
}
static void NS(BinaryWriter w, string? v)
{
    w.Write((byte)(v is null ? 0 : 1)); if (v is not null) S(w, v);
}
static string H(string domain, Action<BinaryWriter> body)
{
    // 小型 Golden/Host 有界内存编码；生产增量 SHA-256。
    using var ms = new MemoryStream();
    using var w = new BinaryWriter(ms, Encoding.UTF8, true);
    w.Write(Encoding.ASCII.GetBytes(domain)); w.Write((byte)0);
    body(w); w.Flush();
    return Convert.ToHexString(SHA256.HashData(ms.ToArray())).ToLowerInvariant();
}
static void Ref(BinaryWriter w, DefinitionReference d)
{
    S(w, d.Id); S(w, d.Revision); S(w, d.ContentHash);
}
static DefinitionReference Definition(string id, string revision, string text)
    => new(id, revision, H("S6-DEFINITION-V1", w =>
       { S(w, id); S(w, revision); S(w, text); }));
static void Cov(BinaryWriter w, GroupCoverageEvidence c)
{
    w.Write(c.Obligations); w.Write(c.Covered); w.Write(c.NotCovered);
    w.Write(c.Failed); w.Write(c.Missing); w.Write(c.Unknown);
    w.Write(c.CrossCounts.FailureAndCovered);
    w.Write(c.CrossCounts.FailureAndNotCovered);
    w.Write(c.CrossCounts.NonFailureAndCovered);
    w.Write(c.CrossCounts.NonFailureAndNotCovered);
    w.Write(c.CrossCounts.Unknown);
}
static void ObservationBody(BinaryWriter w, GroupIntervalObservation o)
{
    S(w, o.GroupId); S(w, o.EndpointName); w.Write(o.Numerator);
    w.Write(o.Denominator); S(w, o.NumeratorUnit); S(w, o.DenominatorUnit);
    Cov(w, o.Coverage);
}
static void Obs(BinaryWriter w, GroupIntervalObservation o)
{
    ObservationBody(w, o); S(w, o.Source.ObservationId);
    S(w, o.Source.SourceRevision); S(w, o.Source.ContentHash);
    NS(w, o.Source.EvidenceReference);
}
static GroupIntervalObservation MakeObservation(
    string group, string sourceId, long numerator, long denominator,
    GroupCoverageEvidence coverage)
{
    var source = new ObservationReference(sourceId, "src-r1", "", null);
    var o = new GroupIntervalObservation(group, "governance-rate",
        numerator, denominator, "event", "opportunity", coverage, source);
    string hash = H("S6-SOURCE-V1", w =>
    {
        S(w, source.ObservationId); S(w, source.SourceRevision);
        NS(w, source.EvidenceReference); ObservationBody(w, o);
    });
    return o with { Source = source with { ContentHash = hash } };
}
static void NPBody(BinaryWriter w, NumericalPolicy p)
{
    S(w, p.Identity.Id); S(w, p.Identity.Revision);
    w.Write(p.RankAbsolute); w.Write(p.RankRelative);
    w.Write(p.DecompositionTolerance); w.Write(p.PsdTolerance);
    w.Write(p.CorrelationRoundoffTolerance); w.Write(p.TQuantileAbsolute);
    w.Write(p.TQuantileRelative); w.Write(p.FQuantileRelative);
    w.Write(p.TailRelative);
}
static void GPBody(BinaryWriter w, GroupIntervalPolicy p)
{
    S(w, p.Identity.Id); S(w, p.Identity.Revision); S(w, p.MethodRevision);
    w.Write((int)p.Tail); w.Write(p.ConfidencePpm); w.Write(p.Resamples);
    w.Write(p.Seed); w.Write(p.MinIndependentGroups);
    S(w, p.PrngRevision); S(w, p.QuantileRevision);
}
static void GB(BinaryWriter w, GroupIntervalBudget b)
{
    w.Write(b.MaxGroups); w.Write(b.MaxResamples); w.Write(b.MaxIntegerBits);
    w.Write(b.MaxPrngOutputs); w.Write(b.MaxBufferedBytes);
    w.Write(b.WallClockLimit.Ticks); w.Write(b.CancellationResponseLimit.Ticks);
    w.Write(b.DrainObservationLimit.Ticks);
}
static void NB(BinaryWriter w, NumericalBudget b)
{
    w.Write(b.MaxRows); w.Write(b.MaxGroups); w.Write(b.MaxColumns);
    w.Write(b.MaxCategories); w.Write(b.MaxTasks); w.Write(b.MaxDetailRows);
    w.Write(b.MaxDiagnostics); w.Write(b.MaxIntegerBits);
    w.Write(b.MaxBufferedBytes); w.Write(b.MaxWorkingSetBytes);
    w.Write(b.WallClockLimit.Ticks); w.Write(b.DrainObservationLimit.Ticks);
    w.Write(b.MaxNotifications);
}
static void Closure(BinaryWriter w, InputClosure c)
{
    w.Write((byte)(c.ExpectedMembers.HasValue ? 1 : 0));
    if (c.ExpectedMembers.HasValue) w.Write(c.ExpectedMembers.Value);
    NS(w, c.ExpectedMemberSetHash); w.Write(c.ReadComplete);
    w.Write(c.PopulationClosed); NS(w, c.ClosureReceiptReference);
    if (!c.Gaps.IsEmpty) throw new InvalidOperationException("Host requires empty Gaps");
    w.Write(c.Gaps.Length);
}
static void SortedRatio(BinaryWriter w, ImmutableArray<GroupIntervalObservation> g)
{
    var a = g.OrderBy(o => o.GroupId, StringComparer.Ordinal).ToArray();
    w.Write(a.Length); foreach (var o in a) Obs(w, o);
}
static void SortedPairs(BinaryWriter w, ImmutableArray<GroupPair> g)
{
    var a = g.OrderBy(o => o.GroupId, StringComparer.Ordinal).ToArray();
    w.Write(a.Length);
    foreach (var p in a)
    { S(w, p.GroupId); S(w, p.PairingKey); Obs(w, p.Left); Obs(w, p.Right); }
}
static void TaskBody(BinaryWriter w, NumericalTask task)
{
    switch (task)
    {
        case GroupRatioTask t:
            S(w, "GroupRatioTask"); S(w, t.TaskId); S(w, t.EndpointName);
            S(w, t.RatioUnit); GPBody(w, t.Policy); S(w, t.Policy.Identity.ContentHash);
            GB(w, t.Budget); SortedRatio(w, t.Groups); break;
        case GroupPairedRatioTask t:
            S(w, "GroupPairedRatioTask"); S(w, t.TaskId); S(w, t.EndpointName);
            S(w, t.LeftRole); S(w, t.RightRole); S(w, t.DifferenceUnit);
            GPBody(w, t.Policy); S(w, t.Policy.Identity.ContentHash);
            GB(w, t.Budget); SortedPairs(w, t.Groups); break;
        default: throw new InvalidOperationException("Unsupported fixture task");
    }
}
static void SnapshotBody(BinaryWriter w, NumericalRequest r)
{
    var i = r.Input;
    S(w, i.SnapshotId); S(w, i.SnapshotRevision); w.Write((int)i.Mode);
    S(w, i.QueryReceiptId); S(w, i.SourceBoundary); NS(w, i.WatermarkId);
    w.Write(i.ReadComplete); w.Write(i.CanReplay); Closure(w, r.Closure);
    Ref(w, r.Method); Ref(w, r.SelectionPolicy);
    w.Write((byte)(r.ObservedSubsetApproval is null ? 0 : 1));
    if (r.ObservedSubsetApproval is not null) Ref(w, r.ObservedSubsetApproval);
    w.Write((int)r.Completeness); NPBody(w, r.Policy);
    S(w, r.Policy.Identity.ContentHash); NB(w, r.Budget);
    w.Write(r.Tasks.Length); foreach (var t in r.Tasks) TaskBody(w, t);
}
static NumericalRequest Seal(NumericalRequest r)
    => r with { Input = r.Input with
       { ContentHash = H("S6-INPUT-V1", w => SnapshotBody(w, r)) } };
static string RequestHash(NumericalRequest r)
    => H("S6-REQUEST-V1", w =>
       { S(w, r.OperationId); SnapshotBody(w, r); S(w, r.Input.ContentHash); });
static string OrderHash(NumericalTask task) => task switch
{
    GroupRatioTask t => H("S6-GROUP-ORDER-V1", w => SortedRatio(w, t.Groups)),
    GroupPairedRatioTask t => H("S6-PAIRED-GROUP-ORDER-V1", w =>
    { S(w, t.LeftRole); S(w, t.RightRole); S(w, t.DifferenceUnit);
      SortedPairs(w, t.Groups); }),
    _ => throw new InvalidOperationException("Unsupported fixture task")
};

public static NumericalRequest Build(bool paired) {
const string methodText =
    "independent-exchangeable-groups;equal-probability-with-replacement;" +
    "pooled-raw-integers;paired-shared-indices;left-minus-right;" +
    "pcg32-xsh-rr-v1;initseq=54;linear-hf7-v1;all-resamples-valid;" +
    "one-sided-infinite-bound;no-imputation;coverage-preserved;limits-before-draw";
const string selectionText =
    "synthetic-fixture;independent-exchangeable-group;GroupId-ordinal;" +
    "same-obligation-set-per-pair;complete-pairs;no-exclusion;no-imputation";
var method = Definition("group-percentile-bootstrap-v1", "1", methodText);
var selection = Definition("s6-independent-groups-v1", "1", selectionText);
var numeric0 = new NumericalPolicy(
    new DefinitionReference("engineering-binary64-v1", "1", ""),
    1e-14, 1e-12, 1e-10, 1e-12, 8 * Math.Pow(2, -52),
    5e-12, 5e-12, 1e-10, 1e-9);
var outerPolicy = numeric0 with { Identity = numeric0.Identity with
    { ContentHash = H("S6-NUMERIC-POLICY-V1", w => NPBody(w, numeric0)) } };
var policy0 = new GroupIntervalPolicy(
    new DefinitionReference("s6-group-policy", "1", ""),
    "group-percentile-bootstrap-v1", GroupIntervalTail.TwoSided,
    750000, 8, 42u, 2, "pcg32-xsh-rr-v1", "linear-hf7-v1");
var groupPolicy = policy0 with { Identity = policy0.Identity with
    { ContentHash = H("S6-GROUP-POLICY-V1", w => GPBody(w, policy0)) } };
var outerBudget = new NumericalBudget(
    2, 2, 1, 1, 1, 0, 64, 256, 1_048_576, 4_194_304,
    TimeSpan.FromSeconds(5), TimeSpan.FromSeconds(2), 64);
var groupBudget = new GroupIntervalBudget(
    2, 8, 256, MaxPrngOutputs: 64, MaxBufferedBytes: 1_048_576,
    WallClockLimit: TimeSpan.FromSeconds(5),
    CancellationResponseLimit: TimeSpan.FromSeconds(1),
    DrainObservationLimit: TimeSpan.FromSeconds(2));
var closure = new InputClosure(2, H("S6-MEMBER-SET-V1", w =>
    { w.Write(2); S(w, "G-A"); S(w, "G-B"); }),
    true, true, "closure-s6", ImmutableArray<InputGap>.Empty);
var leftCoverageA = new GroupCoverageEvidence(
    1, 1, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 1, 0, 0));
var leftCoverageB = new GroupCoverageEvidence(
    99, 99, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 99, 0, 0));
var left = ImmutableArray.Create(
    MakeObservation("G-A", "L-A", 1, 1, leftCoverageA),
    MakeObservation("G-B", "L-B", 0, 99, leftCoverageB));
var ratioTask = new GroupRatioTask("S6-RATIO-HOST-GOLDEN-001",
    "governance-rate", "ratio", groupPolicy, groupBudget, left);
var ratioRequest = Seal(new NumericalRequest("op-s6-ratio-001",
    new InputReference("snap-s6-ratio", "r1", InputMode.FixedSnapshot,
        "receipt-s6-ratio", "governance-groups", "", null, true, true),
    closure, method, selection, null, CompletenessPolicy.RequireAll,
    outerPolicy, outerBudget, ImmutableArray.Create<NumericalTask>(ratioTask)));
if (!paired) return ratioRequest;
// 配对右侧各有完整自身覆盖与来源；不复用左侧的 Source。
var rightCoverageA = new GroupCoverageEvidence(
    1, 1, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 1, 0, 0));
var rightCoverageB = new GroupCoverageEvidence(
    99, 99, 0, 0, 0, 0, new FailureCoverageCrossCounts(0, 0, 99, 0, 0));
var right = ImmutableArray.Create(
    MakeObservation("G-A", "R-A", 0, 1, rightCoverageA),
    MakeObservation("G-B", "R-B", 1, 99, rightCoverageB));
var pairs = ImmutableArray.Create(
    new GroupPair("G-A", left[0], right[0], "pair-G-A-v1"),
    new GroupPair("G-B", left[1], right[1], "pair-G-B-v1"));
var pairedTask = new GroupPairedRatioTask("S6-PAIRED-HOST-GOLDEN-001",
    "governance-rate", "left", "right", "ratio-difference",
    groupPolicy, groupBudget, pairs);
var pairedRequest = Seal(new NumericalRequest("op-s6-paired-001",
    new InputReference("snap-s6-paired", "r1", InputMode.FixedSnapshot,
        "receipt-s6-paired", "governance-groups", "", null, true, true),
    closure, method, selection, null, CompletenessPolicy.RequireAll,
    outerPolicy, outerBudget, ImmutableArray.Create<NumericalTask>(pairedTask)));
return pairedRequest;
}
public static string FullRequestHash(NumericalRequest request) => RequestHash(request);
public static string ExpectedOrder(NumericalTask task) => OrderHash(task);
}

// 仅使用完整请求的同步managed S6桥；调用发生在C2/Host非UI工作线程。
// 一实例一operation，原Owner持request/result直到报告提交和资源关闭。
sealed class S6RatioBridge : DG.IStatisticsPort {
    readonly INumericalStatistics engine;
    readonly NumericalRequest request;
    readonly DG.IntervalQuery expected;
    Task<IReadOnlyList<DG.IntervalResult>>? original;
    public NumericalResult? Evidence { get; private set; }
    public S6RatioBridge(INumericalStatistics engine, NumericalRequest request,
        DG.IntervalQuery expected) {
        this.engine = engine; this.request = request;
        this.expected = expected with { Groups = expected.Groups.ToImmutableArray() };
        if (request.Tasks.Length != 1 || request.Tasks[0] is not GroupRatioTask task ||
            task.Policy.Tail != GroupIntervalTail.TwoSided ||
            expected.Kind != DG.IntervalKind.GroupBootstrap ||
            expected.MethodRevision != task.Policy.MethodRevision ||
            expected.ConfidencePpm != task.Policy.ConfidencePpm ||
            expected.Resamples != task.Policy.Resamples || expected.Seed != task.Policy.Seed ||
            expected.MinIndependentGroups != task.Policy.MinIndependentGroups ||
            request.Budget.MaxRows > expected.Budget.MaxItems ||
            request.Budget.MaxGroups > expected.Budget.MaxItems ||
            task.Budget.MaxGroups > expected.Budget.MaxItems ||
            request.Budget.MaxWorkingSetBytes > expected.Budget.MaxWorkingBytes ||
            request.Budget.WallClockLimit.TotalMilliseconds > expected.Budget.WorkTimeoutMs ||
            request.Budget.DrainObservationLimit.TotalMilliseconds > expected.Budget.CleanupTimeoutMs ||
            !expected.Groups.OrderBy(g => g.GroupId, StringComparer.Ordinal)
                .Select(g => (g.GroupId, g.EndpointName, g.Numerator, g.Denominator, g.Obligations))
                .SequenceEqual(task.Groups.OrderBy(g => g.GroupId, StringComparer.Ordinal)
                .Select(g => (g.GroupId, g.EndpointName, g.Numerator, g.Denominator, g.Coverage.Obligations))))
            throw new InvalidOperationException("DG-013: S6 binding mismatch");
    }
    public Task<IReadOnlyList<DG.IntervalResult>> ComputeAsync(
        DG.IntervalQuery query, CancellationToken ct) {
        // 同operation只接纳同一完整旧query，不由它补造Source/CrossCounts。
        lock (this) {
            if (query.MethodRevision != expected.MethodRevision || query.Kind != expected.Kind ||
                query.ConfidencePpm != expected.ConfidencePpm || query.Resamples != expected.Resamples ||
                query.Seed != expected.Seed || query.MinIndependentGroups != expected.MinIndependentGroups ||
                query.Budget != expected.Budget || !query.Groups.SequenceEqual(expected.Groups))
                return Task.FromException<IReadOnlyList<DG.IntervalResult>>(
                    new InvalidOperationException("DG-005: interval query changed"));
            if (original != null) return original;
            try {
                ct.ThrowIfCancellationRequested();
                Evidence = engine.ComputeNumerical(request, ct);
                var mapped = S6Projection.Map(request, Evidence);
                original = Task.FromResult<IReadOnlyList<DG.IntervalResult>>(mapped);
            }
            catch (Exception error) {
                original = Task.FromException<IReadOnlyList<DG.IntervalResult>>(error);
            }
            return original;
        }
    }
}

static class S6Projection {
    public static ImmutableArray<DG.IntervalResult> Map(NumericalRequest q, NumericalResult r) {
        if (q.OperationId != r.OperationId || r.Provenance.CoreApiVersion != "0.3" ||
            r.Provenance.Input != q.Input || r.Provenance.Method != q.Method ||
            r.Provenance.SelectionPolicy != q.SelectionPolicy ||
            r.Provenance.NumericPolicy != q.Policy.Identity ||
            r.Provenance.SubsetApproval != q.ObservedSubsetApproval ||
            r.Provenance.Closure.ExpectedMembers != q.Closure.ExpectedMembers ||
            r.Provenance.Closure.ExpectedMemberSetHash != q.Closure.ExpectedMemberSetHash ||
            r.Provenance.Closure.ReadComplete != q.Closure.ReadComplete ||
            r.Provenance.Closure.PopulationClosed != q.Closure.PopulationClosed ||
            r.Provenance.Closure.ClosureReceiptReference != q.Closure.ClosureReceiptReference ||
            !r.Provenance.Closure.Gaps.SequenceEqual(q.Closure.Gaps) ||
            r.Tasks.Length != q.Tasks.Length)
            throw new InvalidOperationException("DG-005: S6 result identity");
        // 取消/超时/算法故障不能投影成正常完成的Intervals。
        if (r.State != ResultState.Complete)
            throw new InvalidOperationException("DG-011: S6 incomplete result: " + r.State);
        var output = ImmutableArray.CreateBuilder<DG.IntervalResult>();
        for (int i = 0; i < q.Tasks.Length; i++) {
            var result = r.Tasks[i] as GroupIntervalResult ??
                throw new InvalidOperationException("DG-013: S6 result type");
            var policy = q.Tasks[i] switch {
                GroupRatioTask t => t.Policy,
                GroupPairedRatioTask t => t.Policy,
                _ => throw new InvalidOperationException("DG-002: unsupported task") };
            if (policy.Tail != GroupIntervalTail.TwoSided ||
                result.TaskId != q.Tasks[i].TaskId || result.Policy != policy ||
                result.MethodRevision != policy.MethodRevision ||
                result.Provenance.MethodRevision != policy.MethodRevision ||
                result.Provenance.PrngRevision != policy.PrngRevision ||
                result.Provenance.QuantileRevision != policy.QuantileRevision ||
                result.Provenance.Seed != policy.Seed || result.Estimates.Length != 1)
                throw new InvalidOperationException("DG-005: S6 policy/result mismatch");
            var e = result.Estimates[0]; var d = e.Diagnostics;
            string endpoint = q.Tasks[i] switch {
                GroupRatioTask t => t.EndpointName, GroupPairedRatioTask t => t.EndpointName,
                _ => throw new InvalidOperationException("DG-002: task endpoint") };
            if (e.EndpointName != endpoint ||
                result.Provenance.GroupOrderHash != S6Fixture.ExpectedOrder(q.Tasks[i]) ||
                result.Provenance.PrngOutputCount < result.Provenance.PrngRejectionCount ||
                result.Provenance.PrngRejectionCount < 0)
                throw new InvalidOperationException("DG-005: S6 endpoint/order/draw mismatch");
            if (d.ExecutedRepeats + d.UnexecutedRepeats != policy.Resamples ||
                d.ExecutedRepeats != d.ValidRepeats + d.InvalidRepeats + d.CancelledRepeats)
                throw new InvalidOperationException("DG-005: S6 repeat conservation");
            bool computed = e.Point.State == NumericalValueState.Computed &&
                e.Point.Value.HasValue && double.IsFinite(e.Point.Value.Value) &&
                e.Lower.State == GroupIntervalBoundState.Computed &&
                e.Upper.State == GroupIntervalBoundState.Computed &&
                e.Lower.Value.HasValue && e.Upper.Value.HasValue &&
                double.IsFinite(e.Lower.Value.Value) && double.IsFinite(e.Upper.Value.Value) &&
                e.Lower.Value <= e.Upper.Value;
            string reason = string.Join(";", r.Diagnostics.Concat(result.Diagnostics)
                .Concat(d.Diagnostics).Select(x => x.Code).Distinct(StringComparer.Ordinal));
            if (!computed) reason = "DG-014;" + reason; // null边界保留；不能补0。
            output.Add(new DG.IntervalResult(e.EndpointName, computed ? e.Lower.Value : null,
                computed ? e.Upper.Value : null, d.IndependentGroups,
                result.MethodRevision, reason));
        }
        return output.ToImmutable();
    }
}

sealed record S6HostReceipt(bool Verified);
sealed class S6CallOwner {
    public StatisticsEngine? Engine;
    public NumericalRequest? Request;
    public NumericalResult? Evidence;
    public S6RatioBridge? Bridge;
    public async Task ReleaseAsync() {
        if (Engine != null) await Engine.DisposeAsync();
        // 只有原Dispose成功才清引用；失败由root继续持此Owner，不丢请求/诊断。
        Engine = null; Request = null; Evidence = null; Bridge = null;
    }
}
static class S6Host {
    static Task<S6HostReceipt> ComputeAndAssert(S6CallOwner owner, bool paired) {
        owner.Request = S6Fixture.Build(paired);
        owner.Engine = new StatisticsEngine(new EngineLimits(4, 4));
        var request = owner.Request; var engine = owner.Engine;
        string kind = paired ? "GroupPairedRatioTask" : "GroupRatioTask";
        var caps = engine.NumericalCapabilities;
        if (caps.ApiVersion != "0.3" || !caps.TaskKinds.Contains(kind) ||
            !caps.Backends.Any(x => x.Id == "managed-group-percentile-bootstrap-v1" &&
                x.Validation == NumericalBackendValidation.Validated))
            throw new InvalidOperationException("DG-002: S6 runtime capability not qualified");
        IReadOnlyList<DG.IntervalResult> intervals;
        if (paired) {
            owner.Evidence = engine.ComputeNumerical(request, CancellationToken.None);
            intervals = S6Projection.Map(request, owner.Evidence);
        } else {
            var budget = new DG.Budget(2, 65536, 262144, 4 * 1024 * 1024,
                100000, 1, 5000, 2000);
            var query = new DG.IntervalQuery("group-percentile-bootstrap-v1",
                DG.IntervalKind.GroupBootstrap, 750000, 8, 42u, 2,
                new[] { new DG.GroupStatistic("G-A", "governance-rate", 1, 1, 1, 0, 0, 0),
                    new DG.GroupStatistic("G-B", "governance-rate", 0, 99, 99, 0, 0, 0) }, budget);
            owner.Bridge = new S6RatioBridge(engine, request, query);
            var original = owner.Bridge.ComputeAsync(query, CancellationToken.None);
            if (!original.IsCompleted) throw new InvalidOperationException("S6 sync bridge violated");
            owner.Evidence = owner.Bridge.Evidence; // 映射抛错时同样保留完整原结果。
            intervals = original.GetAwaiter().GetResult(); // 已完成managed结果；不阻塞未知Task。
        }
        var evidence = owner.Evidence;
            if (evidence == null || intervals.Count != 1) throw new InvalidOperationException("S6 result absent");
            var o = (GroupIntervalResult)evidence.Tasks.Single(); var e = o.Estimates.Single();
            if (o.Provenance.GroupOrderHash != S6Fixture.ExpectedOrder(request.Tasks[0]) ||
                o.Provenance.PrngOutputByteHash != "7a40659e59745b6adacf411f7830b57137b8758f0bda4c6afd0ca709cc0945c8" ||
                o.Provenance.PrngOutputCount != 16 || o.Provenance.PrngRejectionCount != 0 ||
                o.Coverage.Expected != 2 || o.Coverage.Included != 2 ||
                e.Diagnostics.ValidRepeats != 8 || e.Diagnostics.InvalidRepeats != 0 ||
                e.Diagnostics.UnexecutedRepeats != 0 || e.Diagnostics.IndependentGroups != 2)
                throw new InvalidOperationException("S6 coverage/provenance");
            if (!paired) {
                if (S6Fixture.FullRequestHash(request) != "57ea74eb757fc713907c66bd01203f1502616c0d5b00f75769626ed9e1b30502" ||
                    e.RawTotalNumerator != 1 || e.RawTotalDenominator != 100 ||
                    e.TotalNumerator != 1 || e.TotalDenominator != 100 || e.Point.Value != 0.01d ||
                    e.Lower.Value != 0d || Math.Abs(e.Upper.Value!.Value - 0.13375d) > 1e-15)
                    throw new InvalidOperationException("DG-S6-RATIO-HOST");
            } else {
                if (S6Fixture.FullRequestHash(request) != "6f8b9588f1a8a11550b3d2fbc64120f0182b7d8c3ea46f7558b73629406a038c" ||
                    e.RawLeftTotalNumerator != 1 || e.RawLeftTotalDenominator != 100 ||
                    e.RawRightTotalNumerator != 1 || e.RawRightTotalDenominator != 100 ||
                    e.RawTotalNumerator != 0 || e.RawTotalDenominator != 10000 ||
                    e.TotalNumerator != 0 || e.TotalDenominator != 1 || e.Point.Value != 0d ||
                    Math.Abs(e.Lower.Value!.Value + 1d / 99d) > 1e-15 ||
                    Math.Abs(e.Upper.Value!.Value - 0.125d) > 1e-15)
                    throw new InvalidOperationException("DG-S6-PAIRED-HOST");
            }

        // 核对/消费完整证据在借用原Task返回前结束，只返回不保留大对象的小回执。
        // 生产调用方在此阶段追加完整evidence到有界报告payload，然后才交release。
        return Task.FromResult(new S6HostReceipt(true));
    }
    public static async Task<int> RunAsync(DG.GovernanceRoot root, bool paired) {
        if (!root.TryReserve(8 * 1024 * 1024, out var reserved) || reserved == null) return 1;
        var slot = reserved;
        var owner = new S6CallOwner(); // 无IO/engine/编码；先注册Owner才创建任何资源。
        Exception? primary = null; var cleanupErrors = new List<Exception>();
        try {
            var accepted = slot.StartBorrowed(() => ComputeAndAssert(owner, paired), owner,
                () => owner.ReleaseAsync(), 8 * 1024 * 1024);
            if (accepted.Value == null) throw new InvalidOperationException("DG-008: borrowed call rejected");
            if (!(await accepted.Value.Original).Verified)
                throw new InvalidOperationException("S6 assertion failed");
        }
        catch (Exception error) { primary = error; }
        DG.CleanupResult cleanup;
        try { cleanup = await slot.CloseAsync(2000); }
        catch (Exception error) { cleanupErrors.Add(error);
            cleanup = new DG.CleanupResult(false, false, "DG-011", slot.Id); }
        if (!cleanup.Released) {
            cleanupErrors.Add(new InvalidOperationException("S6 cleanup unresolved"));
            try { if (!slot.TransferToRoot().Accepted)
                cleanupErrors.Add(new InvalidOperationException("S6 transfer rejected")); }
            catch (Exception error) { cleanupErrors.Add(error); }
        }
        if (primary != null) Console.Error.WriteLine("work: " + primary.Message);
        foreach (var error in cleanupErrors) Console.Error.WriteLine("cleanup: " + error.Message);
        return primary == null && cleanupErrors.Count == 0 && cleanup.Released ? 0 : 1;
    }
}

// 既有本模块Integration TestHost的一种独立无UI运行mode；不另创建项目。
static class S6Program {
    static async Task<int> Main() {
        var root = new DG.GovernanceRoot(new DG.RootLimits(2, 4, 16 * 1024 * 1024, 64, 16));
        try {
            int ratio = await S6Host.RunAsync(root, false);
            int paired = await S6Host.RunAsync(root, true);
            var cleanup = await root.ObserveAllAsync(2000);
            return ratio == 0 && paired == 0 && cleanup.Released && root.OutstandingSlots == 0 ? 0 : 1;
        }
        catch (Exception error) { Console.Error.WriteLine(error.Message); return 1; }
    }
}
~~~

两份输入与上游已接收Golden严格同字段：ratioInput=1429 bytes/hash `c6c59c1f6df0a1be3e4c64553311027a47a9361db00ad807bc7b3ce3924b8290`、ratioRequest=1518 bytes/hash `57ea74eb757fc713907c66bd01203f1502616c0d5b00f75769626ed9e1b30502`；pairedInput=1990 bytes/hash `b67555033a62d2632a72e5625beee9afbe1968578b5076afb6b16eac422c90f3`、pairedRequest=2080 bytes/hash `6f8b9588f1a8a11550b3d2fbc64120f0182b7d8c3ea46f7558b73629406a038c`。ratio组A=1/1、B=0/99，pooled=1/100而非组均值0.5；paired右A=0/1、B=1/99，差值=0/1，原差0/10000仍保留。q=.125/.875得到ratio `[0,.13375]`、paired `[-1/99,.125]`；保留执行8/未执行0/有效8/无效0/取消0、G=2、draw16/rejection0。

### 13.1.3 结果、诊断、不可计算和权利边界

`GroupIntervalResult.Coverage` 的 Expected/Included/Unknown/Missing 等计**独立组**完整性；每组 `GroupCoverageEvidence` 才计原评价义务，不把paired两侧算2G、不把字符数或义务数填Expected。`Diagnostics` 保留 `STAT.INDEPENDENT_GROUPS_INSUFFICIENT`、`STAT.DENOMINATOR_UNKNOWN`、`STAT.PAIR_INCOMPLETE`、`STAT.DEGENERATE`、无效重复/预算/取消及排序、seed、draw hash 相关诊断。`GroupIntervalEstimate.Point` 可为 `Computed` 而 Lower/Upper 为 `Undefined`；此时保存点值、原始精确计数、无效/未执行重复和 gap，不能把 null 边界改成0或总体替代。`Provenance` 至少保存 `MethodRevision/PrngRevision/QuantileRevision/Seed/GroupOrderHash/PrngOutputByteHash/PrngOutputCount/PrngRejectionCount`；不得只写摘要区间而丢原始计数。

| 上游结果/诊断 | 本模块映射与恢复 |
|---|---|
| 输入结构/hash冲突、交叉计数不守恒、配对多行 | 接纳前无run；DG-001/005/013和原STAT错误可定位组/字段，原请求/证据保留；修资料形成新修订，禁止临时补0/换ID执行 |
| 组数不足/任组零分母/缺一侧 | `STAT.INDEPENDENT_GROUPS_INSUFFICIENT`/`STAT.DENOMINATOR_UNKNOWN`/`STAT.PAIR_INCOMPLETE`原码保留、对应端点DG-014 gap和null区间；缺组先核左右集合，禁止zip/交集构造假完整GroupPair。已有全量义务报告可保存诊断，不给质量FAIL/PASS |
| 完成且点/区间可算 | IntervalResult.EndpointName/Lower/Upper/IndependentGroups/MethodRevision/Reason仅为有界摘要；原GroupIntervalEstimate的12项原始/约分整数、Point.Unit/State/Code、两个Bound.State/Value/Code、完整Coverage/Diagnostics/Provenance都保存在同operation报告evidence；配对差值不冒成单模型率 |
| 点可算而边界Undefined；退化 | 原点/计数保留，DG-014及具体STAT码不丢；全部重复Valid才给区间；退化`[x,x]`仍保留STAT.DEGENERATE，不宣布零风险。ZeroDenominator/Overflow是InvalidRepeats子项，不二次加总；Executed=Valid+Invalid+Cancelled，Executed+Unexecuted=B |
| RangeLoss/NumericUncertain/InvalidInput/BudgetExceeded | 保留状态/原因、null不可算投影；DG-008用于预算，DG-013用于估计量/支持域，DG-005用于结果内容不一致；不得缩窄大整数或先double求和。绑定原task，不删失败组或换小预算相同ID重跑 |
| Cancelled/TimedOut/Failed | 不能投影成正常完成Intervals；原结果/已算子集在Owner，DG-009/010/011分别报告意图/执行错误；资源是否Released另轴，不能据ResultState反推排空。取消/超时后只观察/查询原NumericalRun，未决移交原root |

S6同步纯managed调用不登记异步OperationId查询记录，不为同步Host调用QueryNumericalOperationAsync造恢复对象；同步返回即确认scratch退出，宿主engine/完整证据的归还仍沿root的原release Task。异步接纳ValueTask在root预留入口内只AsTask一次并在结果门先接管run/Completion，取消/状态查询/Dispose也登记有界原Task，独立cleanup token不连接已取消业务token；Completion未退出或Status非Drained/CanReuseResources时继续持有。共享engine只处置本run，独占engine确认全部run与Dispose完成才释放；通知退出与算法释放不能用页面关闭代替。

`s6-field-encoding-v1`的生产编码/验证放本模块Adapters并以statistics唯一规则为准；示例S6Fixture只是空Gaps夹具，产品不可ProjectReference测试Exe或调用测试私有工厂。完整evidence在原report-append-v1同一Owner封闭payload里追加精确引用与规范字节；不新增第二报告事实Owner、不改变已接收C1/C2规范字节、旧EvaluationResult字段或Store获批Schema。实际产品报告codec注册/reader兼容需独立接收；尚无该注册时只可作无UI集成诊断证据，不声称治理报告已耐久保存。

本轮未来软件验收只追加到§11同一Integration运行mode，不新建工程：

| ID | 构造 | 必须断言（尚未实现/运行） |
|---|---|---|
| AS01/02 | §13.1.2.1两个独立Host | 完整4侧来源/政策/Input/Request按字段封口，ratio1/100非0.5、paired0/1及raw0/10000，精确区间、G=2、draw/hash和覆盖计数一致；根槽最终归零，未发布运行Capabilities非零 |
| AS03 | G=0/1、任组分母0；左右缺组/重复PairingKey；交叉不守恒 | 不删组、不补0、不取交集；具体STAT/DG定位，组不足/零分母Executed=0/Unexecuted=B；非法结构不产生run |
| AS04 | seed/右计数/Source.EvidenceReference/ConfidencePpm/MaxPrngOutputs改变 | Source/Policy/Input/Request/Order按各自包含字段改变；完整请求与DG-BIND-1不是同域。PCG生产seed42流16-output；G=3内部拒绝向量与draw上限2/3仅复用statistics既有Golden，不注入替代生产RNG |
| AS05 | 原始2/200；全部重复相同；无效/取消中断重复 | 同时保留raw2/200与约分1/100；退化诊断不丢；无效边界null，Executed/Unexecuted及Valid/Invalid/Cancelled守恒，尚未执行不算Invalid |
| AS06 | Factory/编码/能力拒绝/Compute抛错；原run/Dispose不退出；观察取消/晚完成 | Owner先登记，部分engine仍通过原release归还；同步无隐含run；异步仅查原operation、持续持原Completion/请求/engine，恢复无重复计算；业务和cleanup两轴保存、未Released非零/移交ACK不冒Released |
| AS07 | 没有Source读权、Coverage完整而Usage未知；宏平均/多层cluster等超域 | 无权不启动统计/披露证据；义务Coverage不授权、不改变用途/真值/机判；估计量不兼容明确不支持，不将S6区间充模型采用或qualification资格 |

统计不可计算、输入拒绝、异步取消、超时和资源未排空分别映射到治理的 DG 诊断与 operation 状态；禁止把 `NotComputable` 写成 `QualificationGranted=false` 的唯一原因，也禁止把它写成质量失败。治理保存 `ResultState`、完整 `NumericalResult`/精确 query receipt 和原 OperationId，待补资料由 Gap 表示。Statistics 只计算已授权读取到的数值，不授予数据读取权、模型用途、质量放行或设备命令；`AuthorizationReceipt`、UsageDecision、qualification Benchmark/Recorded/Deming 仍由原 Owner 保持。qualification已支持Golden/Benchmark证据桥见§13.1.4–6，Deming上游桥已限定接收；本模块当前计数/区间消费者不使用该点估计，复用边界见§13.1.7。

### 13.1.4 Qualification Contract0.2：Golden与性能证据完整装配

唯一上游为[qualification 0.2.3-prep 附录A.1–A.3/A.3.3/A.5](../qualification/DEVELOPMENT-GUIDE.md)；Core/Study/Replay、Benchmark执行/录制分析软件规格已主控接收。本节只消费`Asun.Modules.Qualification`公开值/端口/Root/Factory/Codec，不调用其Core.Tests私有fixture，不复制统计量、分位、比较器或数值算法。Core保持C1/C2既有治理接口，真实桥属于§11唯一Adapters工程；无UI调用不依赖Loaded、DevExpress、AsunImage或私表。

| 请求边界 | 本模块来源→公开字段/精确核对 |
|---|---|
| 计算身份与版本 | `QualificationRequest.ContractVersion="0.2"`；CalculationId由宿主在调用前固定、与本治理operation及用途关联但不是BindingHash；ExperimentId固定此次研究。MethodRef=(MethodId,Version,Parameters,NumericPolicy,BackendBuild)五字段逐项精确，ArtifactRef完整Namespace/Id/Revision/Sha256；版本不是prep文档号。parent是原Calculation报告引用而非当前UI行；同ID异RequestSha256Conflict，不换键重算 |
| 空标量快照及完整案例 | Golden/Benchmark可用空Observation快照：先EncodePlanContent取得QLEP/Plan ArtifactRef，再EncodeInputContent取得QLIP，InputSnapshot.Snapshot/ContentSha256/ActualBytes/Count/Plan与实际bytes/行数相等。Count=0不等于Golden计划案例0；实际分母来自GoldenPlan/BenchmarkPlan。真实Study才传Original Observation/重复层级/证书；本轮不造本模块测量原值、Deming请求或假物理独立性 |
| GoldenPlan全部字段 | PlanId=冻结回归计划；Cases=原封存QLCS内容引用，Comparator=原已声明比较策略内容引用；PlannedCases、ParentGroupingRef、StrategyRef、SeedSetRef、CaseManifest全给。CaseManifest每CaseId/ParentId/Status/ExpectedRef/ActualRef来自原ReplayOwner，CaseId唯一、父物理组沿数据治理CopyMembers/谱系不变；不按结果重新分组或覆盖Expected。SeedSetRef为空仅限未请求重复的本例，实际重复/种子集由原Owner固定 |
| Replay来源桥 | 宿主实现`IReplayQualificationReader.ReadAsync(GoldenPlan,token)`读取已封存的原结果，返回`ReplayResult(Planned,Executed,CasesSha256,Cases)`；CasesSha256按EncodeCases完整QLCS核一致，计划全外连接保留Changed/Incomparable/ExecutionFailed/NotExecuted，Executed不能把一致个数当执行个数。该端口不重跑模型/比较器、重标标签或改真值。ExpectedRef/ActualRef是opaque原Owner引用，不猜成ArtifactRef、URI或内容hash；生产必须由其明示映射核完整来源，不把示例E/A当真实证据 |
| Golden调用/两计划 | Request.Analysis=`GoldenAnalysis(plan)`；`GoldenRequest(request,plan)`中两个Plan的EncodeGoldenPlan bytes完全相同。Scope的量名/单位/版本/支持域/来源系统/条件均明示，Report的计数只描述这份案例计划；Evidence=SoftwareReplay只证明软件回放。本模块原CoverageCell/全义务事件保持在治理报告，不能用Consistent count取代模型召回、S6完整分母或QualificationGranted |
| BenchmarkPlan全部字段 | Probe/Build/Input是实际probe、构建和输入负载完整引用；WarmupIterations/MeasuredIterations/Parallelism/Deadline/ArrivalMode/CacheMode/FailurePolicy/Budgets/ExecutionMode/Profile/RecordedRun逐字段固定。ResourceMetricBudget的Metric/Scope/Unit/PeakLimit?/RetainedLimit?/Window/AllowedSlope?/TargetSource?均给，null目标NotEvaluated，不从工程MaxResidentBytes补客户限值。Request.Analysis及BenchmarkRequest.Plan必须完整字节等同 |
| 外层资源、方法与事实 | ResourceBudget.MaxRows/MaxCells/MaxColumns/MaxCovarianceDimension/MaxResidentBytes/Deadline，DeadlinePolicy.OperationDeadline/StopWaitBudget，Evidence、Assumptions、Reference?、Criteria?、ParentCalculation?全编码。Deadline同时提供须相等，有效总期限取Profile/Request/Plan较小值；取消另轴。Criteria仅表达原Owner已声明条件、不授用途。本轮无证书/测量/客户目标，Reference/Criteria/Parent=null、Assumptions空，不造Approved |

根必须在Codec/完整复制/Factory前由`QualificationRecoveryOwner.CreateRoot`原子登记，再`Root.Reserve`预留（本例16MiB/1实例/4观察/64task/16late lease，含至少8控制槽和2启动槽）。`RetainInput`、所有原Analyze/Benchmark/Read/Probe/Sampler/Ledger/Evidence/Query Task与CTS归同Root，Factory.Create仅显式装配`QualificationFactoryPorts`十二个字段：Numerics、Ledger、Reader、Replay、References、Probe、Sampler、Observer、EvidenceSink、Transfer、BenchmarkAssets、BenchmarkClock。Golden只需原Replay；Benchmark只需对应执行/录制ports；不因其它分支端口缺省阻断已支持分支。Numerics可显式注入不支持端口，本轮两分支不能暗触Bias/GRR/Deming。共享服务Cancel仅原CalculationQueryRequest身份，不调用Stop整个共享实例；下方Host各自独占Service，最终由Root.Close登记唯一Stop/Dispose。

#### 13.1.4.1 BenchmarkProfile、WorkPlan、RecordedRun逐字段闭包

| 完整对象 | 来源、参数、步骤及不变量 |
|---|---|
| Profile | `BenchmarkProfile(ProfileId,Revision,Environment,Workload,Dimensions,Arrivals,LatencyTargets,Sampling,Limits,Failures)`全部显式。Environment包括OS/.NET/CPU/后端/隔离范围的原Owner封口引用，Workload与Plan.Input相同负载；Dimensions每Name/Unit/Value为输入规模，不能从路径猜。RecordedSchedule Arrivals=(Iteration,Offset)覆盖原测量计划，ClosedLoop为空；LatencyTarget=(Stage,MinimumSamples,P50?,P95?,P99?,TargetSource?)按Prepare/Queue/Service/ProbeElapsed/ProbeReleased/EndToEnd/CancelToRelease允许集，客户目标须原来源，缺目标不默认95/99达标 |
| Sampling/Limits | BenchmarkSampling=(Period,ReadBudget,Metrics,MaximumSamples,RequireCompleteSampling)；ResourceMetricSpec=(Metric,Scope,TargetId,Unit,Acquisition,Attribution)，指标能力必须匹配。BenchmarkLimits=(PrepareBudget,InvokeBudget,TotalBudget,CleanupBudget,MaxResidentBytes,MaxAssetBytes,MaxDetailRows)；取root/请求剩余额度较小值，完整预热/测量明细及每metric行预算预估，不能只预算输入byte。Failures=null表示不比较，不默认0失败；非null MaxFailed/MaxCancelled/MaxTimedOut/MaxNotExecuted与TargetSource必需，计所有Warmup+Measured失败 |
| 资产读取与解析 | `IBenchmarkAssetReader.ReadAsync(source,maxBytes,token)`由Root.StartOwned预留内启动，ValueTask只AsTask一次，返回BenchmarkAsset(Source,Bytes)后逐项核全ArtifactRef、长度、SHA。DecodeBenchmarkProfile/DecodeBenchmarkRecordedRun用BenchmarkDecodeLimits(maxBytes,4096,≤1000000)，先大小再分配，Decode→Encode byte-for-byte/EOF；非法/缺资产不能先启动Probe。首次Profile读取预算=min(请求bytes/4,1MiB)，录制读取取Profile.MaxAssetBytes与剩余较小值 |
| WorkPlan身份 | `QualificationCodec.EncodeBenchmarkWorkPlan(plan)`的QLBW只绑定Probe/Build/Input、Warmup/Measured/Parallelism/Deadline、Arrival/Cache/Failure、全部Budgets、Profile；排除ExecutionMode/RecordedRun，避免录制hash循环。QLBP不含自己ArtifactRef；QLBR的OriginRequestSha256绑定原执行完整QLRQ，当前AnalyzeRecordedRun的QLRQ另有不同CalculationId/Mode/录制引用。不得以QLBW或录制hash冒请求hash/原模型BindingHash |
| ExecuteProbe | RecordedRun=null；BenchmarkAssets/Probe/Clock明确必需，Sampler按所请求指标装配；ProbeCapabilities.Probe/Build精确，HasProductionSideEffects=false、并发/bytes/task/leases受预留、冷模式必须SupportsFreshWorker真实worker。Sampler Prepare→baseline→Probe Prepare→warmup/measure→实际Completion→Probe Drain/lease归还→末样→Sampler Drain/lease归还；所有原Task/lease/root持有。返回Task须包含真正native/GPU完成屏障，没有则QLF-PROBE-CONTRACT，不称算法完成。生产probe只能调用已批准纯计算模块，不发设备/写产品事实 |
| AnalyzeRecordedRun | RecordedRun非null，Probe/Sampler/Clock **不装配且零次调用**；只读同reader核QLBR/QLBP/QLBW及原Origin引用。Clock=(DomainId,Frequency>0,Source)是记录里的同一单调tick域，不调用现时GetTimestamp重新计时。Sessions、Attempts、Samples全部保留原次序身份/时刻，经canonical排序不重排index、删失败或填时间0；Warmup+Measured全索引、lane/worker/session、到达/准备/释放时序核完整。资源ReleasedTick缺省/Complete=false/DroppedSamples保留缺口，只给诊断/NotEvaluated，不用新计算资源Drained补原运行Released |
| 原录制字段 | `BenchmarkRecordedRun`全部23字段：RunId/OriginCalculationId/OriginRequestSha256/Origin/WorkPlanSha256/Profile/Probe/Build/Input/Environment/Clock/AcceptedTick/PreparedTick?/MeasuredStartTick?/MeasuredEndTick?/ProbeReleasedTick?/ResourcesReleasedTick?/Complete/DroppedSamples/CancelRequestedTick?/Sessions/Attempts/Samples（公开位置字段按上游，不自行填新字段）。Session为LeaseId/WorkerId/Lane/Mode/PrepareStart/Prepared/Released?；ProbeRun为InvocationId/Iteration/Warmup/Lane/WorkerId/Outcome/Ready/Enqueued/Start?/ActualCompletion?/ResourcesReleased?/OutputHash?/Reason?；Sample为Tick/Phase/Metric/Unit/Scope/TargetId/Value?/Attribution/Reason?。Origin=SoftwareFixture只能SoftwareReplay/Synthetic，Executed也须真实来源权威；录制重算不提升证据层 |

原义务、不成功的尝试、录制源资源与当前分析资源四者分别保存。QualificationReport.Planned/Valid/Failed/Excluded/NotExecuted是其分析范围，BenchmarkReport的Warmup/Measured原Attempts与摘要保持；治理原评价分母、S6 G/B、模型用途决定不被这些计数覆盖。P50/P95/P99/throughput/资源派生计算全部在qualification已接收算法执行，本Adapter仅核结果状态/来源及具体小向量，不实现第二分位/趋势算法。

### 13.1.5 两个独立无UI消费者：完整Golden及Benchmark三模式

两个消费者位于§11现有Integration TestHost，分别是Golden报告读取装配和纯计算Benchmark/Recorded证据读取装配，独立入口只编译一个Main。以下完整夹具构造重用qualification §12/A.3.3.1已接收字段，非引用其Core.Tests私有代码；公开Codec由`Asun.Modules.Qualification`生产DLL提供。测试端口在本模块TestHost局部实现公开接口，不是新增Core公开API、报告或Schema。Golden只消费封存结果；性能Host可Execute或Recorded，生产可替换为实际纯计算probe/原录制reader，Core无需改。软件延时/100-byte采样是明确fixture，不能称OCR/缺陷客户性能。

~~~csharp
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Asun.Modules.Qualification;

static class QlFixture {
static QualificationRequest CreateReplayRequest()
{
    var pb = QualificationCodec.EncodePlanContent(Array.Empty<PlanCell>(),"f","r","a",0);
    var plan = new ExperimentPlan(QualificationCodec.ArtifactFromBytes("plan","replay","1",pb),
        Array.Empty<PlanCell>(),"f","r","a",0);
    var ib = QualificationCodec.EncodeInputContent(plan,Array.Empty<Observation>());
    var ir = QualificationCodec.ArtifactFromBytes("snapshot","replay","1",ib);
    var cases = new[] {new GoldenCaseResult("C01","P01","Consistent","E","A")};
    var cb = QualificationCodec.EncodeCases(cases);
    var gp = new GoldenPlan("P01",QualificationCodec.ArtifactFromBytes("cases","r01","1",cb),
        QualificationCodec.ArtifactFromBytes("cmp","r01","1",Encoding.UTF8.GetBytes("exact-v1")),
        1,"PARENT","exact-v1","",cases);
    return new QualificationRequest("0.2",new CalculationId("G01"),new ExperimentId("RG01"),
        new MethodRef("Golden.v1","1.0",
            QualificationCodec.ArtifactFromBytes("method","golden","1",Encoding.UTF8.GetBytes("golden-exact-v1")),
            QualificationCodec.ArtifactFromBytes("numeric","policy","1",Encoding.UTF8.GetBytes("engineering-binary64-v1")),
            QualificationCodec.ArtifactFromBytes("backend","replay","1",Encoding.UTF8.GetBytes("fixture-replay-v1"))),
        new Scope("result","1",new UnitId("one","1","1"),"s","replay","c"),
        new InputSnapshot(ir,0,ib.LongLength,ir.Sha256,Array.Empty<Observation>(),plan),EvidenceLevel.SoftwareReplay,
        new ResourceBudget(100,100,32,8,1048576,TimeSpan.FromSeconds(30)),
        new DeadlinePolicy(TimeSpan.FromSeconds(30),TimeSpan.FromSeconds(2)),
        new GoldenAnalysis(gp),null,Array.Empty<AssumptionEvidence>(),null,null);
}

static (QualificationRequest Request,BenchmarkAsset[] Assets) CreateBenchmarkRequest(bool recorded)
{
    static ArtifactRef Ref(string ns,string id,string text) =>
        QualificationCodec.ArtifactFromBytes(ns,id,"1",System.Text.Encoding.UTF8.GetBytes(text));
    var empty=CreateReplayRequest();
    var environment=Ref("env","test","software-fixture;no-devices");
    var workload=Ref("load","test","fixed-three-calls");
    var probe=Ref("probe","test","test-probe-v1");
    var build=Ref("build","test","fixture-bench-v1");
    var metrics=new[] {new ResourceMetricSpec("managed-live-bytes","Process","host","byte","Polled","Attributed")};
    var profile=new BenchmarkProfile("BP01","1",environment,workload,
        new[] {new WorkloadDimension("calls","count",3)},Array.Empty<ArrivalSlot>(),
        new[] {new LatencyTarget("Service",1,null,null,null,null)},
        new BenchmarkSampling(TimeSpan.FromMilliseconds(10),TimeSpan.FromSeconds(1),metrics,5000,true),
        new BenchmarkLimits(TimeSpan.FromSeconds(1),TimeSpan.FromSeconds(1),TimeSpan.FromSeconds(30),
            TimeSpan.FromSeconds(2),8388608,1048576,10),null);
    var pb=QualificationCodec.EncodeBenchmarkProfile(profile);
    var pr=QualificationCodec.ArtifactFromBytes("bench-profile","BP01","1",pb);
    var plan=new BenchmarkPlan(probe,build,workload,0,3,1,TimeSpan.FromSeconds(30),
        "ClosedLoop","WarmReuse","StopOnFailure",Array.Empty<ResourceMetricBudget>(),
        recorded ? BenchmarkExecutionMode.AnalyzeRecordedRun : BenchmarkExecutionMode.ExecuteProbe,pr);
    var assets=new List<BenchmarkAsset> {new(pr,pb)};
    var sourceRequest=empty with {CalculationId=new CalculationId("BEN-ORIGIN"),
        ExperimentId=new ExperimentId("BENCH-01"),
        Analysis=new BenchmarkAnalysis(plan with {ExecutionMode=BenchmarkExecutionMode.ExecuteProbe}),
        Resources=empty.Resources with {MaxResidentBytes=8388608},
        Method=new MethodRef("Benchmark.v1","1.0",Ref("method","benchmark","benchmark-v1"),
            empty.Method.NumericPolicy,build),Evidence=EvidenceLevel.SoftwareReplay};
    if (recorded) {
        string output=Ref("out","ok","result=ok").Sha256;
        long[] ready={10,30,60},start={12,33,61},done={22,48,69},release={25,50,70};
        var rows=new List<ProbeRun>();
        for (int i=0;i<3;i++) rows.Add(new ProbeRun("BEN-ORIGIN/measure/"+i,i,false,0,"W01",
            ProbeOutcome.Succeeded,ready[i],ready[i],start[i],done[i],release[i],output,null));
        var samples=new List<ResourceSample>();
        long[] ticks={0,2,10,20,30,40,50,60,70,75};
        BenchmarkSamplePhase[] phases={BenchmarkSamplePhase.BeforePrepare,BenchmarkSamplePhase.AfterPrepare,
            BenchmarkSamplePhase.AfterWarmup,BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.Measured,
            BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.Measured,
            BenchmarkSamplePhase.Measured,BenchmarkSamplePhase.AfterProbeRelease};
        for (int i=0;i<ticks.Length;i++) samples.Add(new ResourceSample(ticks[i],phases[i],
            "managed-live-bytes","byte","Process","host",100,"Attributed",null));
        var record=new BenchmarkRecordedRun("BR01",new CalculationId("BEN-ORIGIN"),
            QualificationCodec.ArtifactFromBytes("origin","request","1",
                QualificationCodec.EncodeRequest(sourceRequest)).Sha256,RecordedOrigin.SoftwareFixture,
            QualificationCodec.ArtifactFromBytes("work-plan","test","1",
                QualificationCodec.EncodeBenchmarkWorkPlan(plan)).Sha256,pr,probe,build,workload,environment,
            new BenchmarkClockIdentity("fixture-bench",1000,"fixture"),0,2,10,70,75,80,true,0,null,
            new[] {new ProbeSessionRecord("L01","W01",0,"WarmReuse",0,2,75)},rows,samples);
        var rb=QualificationCodec.EncodeBenchmarkRecordedRun(record);
        var rr=QualificationCodec.ArtifactFromBytes("bench-record","BR01","1",rb);
        assets.Add(new BenchmarkAsset(rr,rb));plan=plan with {RecordedRun=rr};
    }
    var request=sourceRequest with {CalculationId=new CalculationId(recorded ? "BR-ANALYZE" : "BX-EXECUTE"),
        Analysis=new BenchmarkAnalysis(plan)};
    return (request,assets.ToArray());
}
public static QualificationRequest Golden() => CreateReplayRequest();
public static (QualificationRequest Request,BenchmarkAsset[] Assets) Benchmark(bool recorded)
    => CreateBenchmarkRequest(recorded);
}

// 本模块TestHost局部BCL端口，不从qualification.Core.Tests引用其私有fixture。
sealed class NoNumerics : IQualificationNumerics {
    public int Calls { get; private set; }
    public NumericCapabilities Capabilities => new("no-numerics", "software-fixture",
        new HashSet<string>(StringComparer.Ordinal), 1, true, "no-numeric-tasks");
    public ValueTask<NumericResult> CalculateAsync(NumericRequest q, CancellationToken ct) {
        Calls++; return ValueTask.FromException<NumericResult>(
            new InvalidOperationException("Golden/Benchmark must not dispatch numerics"));
    }
}
sealed class FixtureLedger : IQualificationOperationLedger {
    readonly Dictionary<string,(string Hash,QualificationOperationSnapshot? Snapshot)> rows =
        new(StringComparer.Ordinal);
    public ValueTask<AdmissionReceipt> AdmitAsync(CalculationId id,string hash,CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        lock(rows) {
            if (rows.TryGetValue(id.Value,out var prior)) return ValueTask.FromResult(
                new AdmissionReceipt("admit/"+id.Value,prior.Hash==hash ? "Duplicate" : "Conflict",prior.Hash));
            if (rows.Count>=8) throw new InvalidOperationException("fixture ledger capacity");
            rows.Add(id.Value,(hash,null));
            return ValueTask.FromResult(new AdmissionReceipt("admit/"+id.Value,"ConfirmedAccepted",hash));
        }
    }
    public ValueTask<QualificationOperationSnapshot?> QueryAsync(CalculationQueryRequest q,CancellationToken ct) {
        ct.ThrowIfCancellationRequested(); lock(rows) {
            if (rows.TryGetValue(q.CalculationId.Value,out var prior)) {
                if (prior.Hash!=q.RequestSha256) throw new InvalidOperationException("fixture query hash conflict");
                return ValueTask.FromResult(prior.Snapshot);
            }
            return ValueTask.FromResult<QualificationOperationSnapshot?>(null);
        }
    }
    public ValueTask RecordAsync(QualificationOperationSnapshot snapshot,CancellationToken ct) {
        ct.ThrowIfCancellationRequested(); lock(rows) {
            if (!rows.TryGetValue(snapshot.CalculationId.Value,out var prior) || prior.Hash!=snapshot.RequestSha256)
                throw new InvalidOperationException("fixture ledger identity");
            rows[snapshot.CalculationId.Value]=(prior.Hash,snapshot);
        }
        return ValueTask.CompletedTask;
    }
}
sealed class SealedReplay : IReplayQualificationReader {
    readonly GoldenCaseResult[] rows;
    public int Calls { get; private set; }
    public SealedReplay(IReadOnlyList<GoldenCaseResult> rows) {
        if (rows.Count>100) throw new ArgumentOutOfRangeException(nameof(rows));
        this.rows=rows.ToArray();
    }
    public ValueTask<ReplayResult> ReadAsync(GoldenPlan p,CancellationToken ct) {
        ct.ThrowIfCancellationRequested(); Calls++;
        var sha=QualificationCodec.ArtifactFromBytes("cases","r01","1",QualificationCodec.EncodeCases(rows)).Sha256;
        if (p.PlannedCases!=rows.Length || p.Cases.Sha256!=sha || !p.CaseManifest.SequenceEqual(rows))
            throw new InvalidOperationException("sealed replay identity");
        // 原Replay的比较结果，示例E/A分别解析到同一result=ok；此处不运行比较器。
        return ValueTask.FromResult(new ReplayResult(rows.Length,
            rows.Count(x=>x.Status!="NotExecuted"),sha,rows));
    }
}
sealed class SealedBenchAssets : IBenchmarkAssetReader {
    readonly BenchmarkAsset[] assets;
    public int Calls { get; private set; }
    public SealedBenchAssets(IReadOnlyList<BenchmarkAsset> assets) {
        if (assets.Count>4) throw new ArgumentOutOfRangeException(nameof(assets));
        this.assets=assets.Select(x=>new BenchmarkAsset(x.Source,x.Bytes.ToArray())).ToArray();
        if (this.assets.GroupBy(x=>x.Source).Any(g=>g.Count()!=1))
            throw new InvalidOperationException("duplicate benchmark source");
    }
    public ValueTask<BenchmarkAsset> ReadAsync(ArtifactRef source,int maxBytes,CancellationToken ct) {
        ct.ThrowIfCancellationRequested();Calls++;
        var value=assets.Single(x=>x.Source==source);
        if (value.Bytes.Length>maxBytes || QualificationCodec.ArtifactFromBytes(source.Namespace,
            source.Id,source.Revision,value.Bytes.Span)!=source)
            throw new InvalidOperationException("benchmark bytes/hash limit");
        return ValueTask.FromResult(new BenchmarkAsset(source,value.Bytes.ToArray()));
    }
}
sealed class SoftwareClock : IBenchmarkClock {
    readonly long origin=Stopwatch.GetTimestamp();
    int calls;public int Calls => Volatile.Read(ref calls);
    public BenchmarkClockIdentity Identity => new("fixture-bench",1000,"fixture");
    public long GetTimestamp() {
        Interlocked.Increment(ref calls);
        long elapsed=Stopwatch.GetTimestamp()-origin;
        return checked(elapsed/Stopwatch.Frequency*1000 +
            elapsed%Stopwatch.Frequency*1000/Stopwatch.Frequency);
    }
    public async Task WaitUntilAsync(long target,CancellationToken ct) {
        if (target<0 || target>120000) throw new ArgumentOutOfRangeException(nameof(target));
        while (GetTimestamp()<target) await Task.Delay(1,ct);
    }
}
sealed class SoftwareLease : IQualificationLease {
    int disposed;
    public string LeaseId { get; }
    public long RetainedBytes => 4096;
    public bool IsReleased => Volatile.Read(ref disposed)!=0;
    public SoftwareLease(string id) => LeaseId=id;
    public ValueTask DisposeAsync() { Interlocked.Exchange(ref disposed,1);return ValueTask.CompletedTask; }
}
sealed class SoftwareProbe : IBenchmarkProbe {
    readonly SoftwareClock clock; readonly ArtifactRef probe,build;
    readonly object gate=new();Task<ProbeRun>? active;Task<ProbeDrain>? drain;
    public int Prepares,Invokes,Drains;
    public ProbeCapabilities Capabilities => new(probe,build,1,4096,8,1,true,false,false);
    public SoftwareProbe(SoftwareClock clock,ArtifactRef probe,ArtifactRef build)
        {this.clock=clock;this.probe=probe;this.build=build;}
    public async ValueTask<ProbeReady> PrepareAsync(ProbePrepareRequest q,CancellationToken ct) {
        Prepares++;long start=clock.GetTimestamp();
        await Task.Delay(2,ct);
        return new ProbeReady(new SoftwareLease(q.SessionId+"/probe"),
            new ProbeWorker(q.SessionId+"/worker",q.Plan.CacheMode,q.Profile.Environment),
            build,q.Plan.Input,clock.Identity,start,clock.GetTimestamp());
    }
    public Task<ProbeRun> InvokeAsync(ProbeReady ready,ProbeInvocation q,CancellationToken ct) {
        lock(gate) {
            if (drain!=null || (active!=null && !active.IsCompleted))
                throw new InvalidOperationException("fixture probe stopping/in-flight");
            active=InvokeCoreAsync(ready,q,ct);return active;
        }
    }
    async Task<ProbeRun> InvokeCoreAsync(ProbeReady ready,ProbeInvocation q,CancellationToken ct) {
        Invokes++;long? start=null;
        try {
            await Task.Delay(1,ct);start=clock.GetTimestamp();await Task.Delay(10,ct);
            long finished=clock.GetTimestamp();
            var hash=QualificationCodec.ArtifactFromBytes("out","ok","1",Encoding.UTF8.GetBytes("result=ok")).Sha256;
            return new ProbeRun(q.InvocationId,q.Iteration,q.Warmup,q.Lane,ready.Worker.WorkerId,
                ProbeOutcome.Succeeded,q.ReadyTick,q.EnqueuedTick,start,finished,finished,hash,null);
        } catch (OperationCanceledException) {
            // 本fixture无native/子Task，Task.Delay已退出；真实probe必须提供真正完成屏障。
            long finished=clock.GetTimestamp();start ??= finished;
            return new ProbeRun(q.InvocationId,q.Iteration,q.Warmup,q.Lane,ready.Worker.WorkerId,
                ProbeOutcome.Cancelled,q.ReadyTick,q.EnqueuedTick,start,finished,finished,null,"cancelled");
        }
    }
    public Task<ProbeDrain> DrainAsync(ProbeReady ready,TimeSpan budget,CancellationToken ct) {
        lock(gate) {
            if (drain!=null)return drain;
            Drains++;Task completion=active==null ? Task.CompletedTask : active;
            return drain=Task.FromResult(new ProbeDrain(ready.Lease.LeaseId,completion.IsCompleted,
                completion,completion.IsCompleted ? null : "fixture invoke still owned"));
        }
    }
}
sealed class SoftwareSampler : IResourceSampler {
    readonly SoftwareClock clock;
    readonly object gate=new();Task<SamplerDrain>? drain;
    readonly ResourceMetricSpec[] metrics={new("managed-live-bytes","Process","host","byte","Polled","Attributed")};
    public int Prepares,Samples,Drains;
    public ResourceSamplerCapabilities Capabilities => new("fixture-sampler",4096,8,1,metrics);
    public SoftwareSampler(SoftwareClock clock) => this.clock=clock;
    public ValueTask<SamplerReady> PrepareAsync(SamplerPrepareRequest q,CancellationToken ct) {
        ct.ThrowIfCancellationRequested();lock(gate) {
            if (drain!=null || Prepares!=0)throw new InvalidOperationException("fixture sampler prepare state");
            if (!q.Sampling.Metrics.SequenceEqual(metrics))throw new InvalidOperationException("fixture sampler metrics");
            Prepares++;
            return ValueTask.FromResult(new SamplerReady(new SoftwareLease(q.OperationId+"/sampler"),clock.Identity,metrics));
        }
    }
    public ValueTask<ResourceSampleBatch> SampleAsync(SamplerReady ready,BenchmarkSamplePhase phase,CancellationToken ct) {
        ct.ThrowIfCancellationRequested();lock(gate) {
            if (drain!=null || Prepares!=1 || !ready.Metrics.SequenceEqual(metrics))
                throw new InvalidOperationException("fixture sampler stopping/identity");
            Samples++;
            return ValueTask.FromResult(new ResourceSampleBatch(new[] {new ResourceSample(clock.GetTimestamp(),
                phase,"managed-live-bytes","byte","Process","host",100,"Attributed",null)}));
        }
    }
    public Task<SamplerDrain> DrainAsync(SamplerReady ready,TimeSpan budget,CancellationToken ct) {
        lock(gate) {
            if (drain!=null)return drain;
            Drains++;return drain=Task.FromResult(new SamplerDrain(ready.Lease.LeaseId,true,Task.CompletedTask,null));
        }
    }
}

static class QlConsumerHost {
    public static async Task<int> RunAsync(QualificationRecoveryOwner owner,string rootId,string mode) {
        QualificationRoot? root=null;QualificationOutcome? business=null;RootCloseResult? cleanup=null;
        Exception? primary=null;var cleanupErrors=new List<Exception>();
        int workCode=5,cleanupCode=0;
        try {
            if (mode!="golden" && mode!="execute" && mode!="recorded")
                throw new ArgumentOutOfRangeException(nameof(mode));
            root=owner.CreateRoot(rootId,new RootLimits(16777216,1,4,64,16,TimeSpan.FromSeconds(2)));
            var reservation=root.Reserve(rootId,16777216,1,64,16);
            bool golden=mode=="golden", recorded=mode=="recorded";
            var fixture=golden ? (QlFixture.Golden(),Array.Empty<BenchmarkAsset>()) : QlFixture.Benchmark(recorded);
            var request=fixture.Item1;
            root.RetainInput(reservation,request);
            var noNumbers=new NoNumerics();var ledger=new FixtureLedger();
            var gp=(request.Analysis as GoldenAnalysis)?.Plan;
            var bp=(request.Analysis as BenchmarkAnalysis)?.Plan;
            var replay=gp==null ? null : new SealedReplay(gp.CaseManifest);
            var assets=golden ? null : new SealedBenchAssets(fixture.Item2);
            // Recorded不创建clock/probe/sampler；fault矩阵另注入计数拒绝端口证明零调用。
            var clock=golden||recorded ? null : new SoftwareClock();
            var probe=clock==null ? null : new SoftwareProbe(clock,bp!.Probe,bp.Build);
            var sampler=clock==null ? null : new SoftwareSampler(clock);
            var ports=new QualificationFactoryPorts(noNumbers,ledger,null,replay,null,probe,sampler,
                null,null,null,assets,clock);
            var service=QualificationFactory.Create(root,reservation,ports);
            var validate=service.ValidateDesign(request);
            string hash=QualificationCodec.ArtifactFromBytes("request",request.CalculationId.Value,"1",
                QualificationCodec.EncodeRequest(request)).Sha256;
            if (!validate.CanAnalyze || validate.RequestSha256!=hash)
                throw new InvalidOperationException("qualification design/hash rejected");
            var cts=new CancellationTokenSource();
            try {root.RegisterCancellation(reservation,cts);} catch {cts.Dispose();throw;}
            var original=root.StartOwned(reservation,"qualification",()=>golden
                ? service.EvaluateGoldenAsync(new GoldenRequest(request,gp!),cts.Token)
                : service.BenchmarkAsync(new BenchmarkRequest(request,bp!),cts.Token));
            business=await original.WaitAsync(TimeSpan.FromSeconds(30));
            var report=business.Report ?? throw new InvalidOperationException("report absent");
            if (business.Terminal!=OperationTerminal.Completed || !business.Resources.Drained ||
                business.CalculationId!=request.CalculationId || report.CalculationId!=request.CalculationId ||
                report.RequestSha256!=hash || report.Input!=request.Input.Snapshot ||
                report.Method!=request.Method || report.Scope!=request.Scope ||
                report.Completeness!=ReportCompleteness.Complete || report.Evidence!=EvidenceLevel.SoftwareReplay ||
                report.Criteria!=CriteriaStatus.NotEvaluated || business.Resources.CleanupDiagnostics.Count!=0 ||
                report.NumericalResults.Count!=0 || noNumbers.Calls!=0)
                throw new InvalidOperationException("qualification outcome identity/resources");
            var query=root.StartOwned(reservation,"query",()=>service.QueryCalculationAsync(
                new CalculationQueryRequest(request.CalculationId,hash),CancellationToken.None),RootTaskRole.ControlWait);
            var snapshot=await query.WaitAsync(TimeSpan.FromSeconds(1));
            if (snapshot.CalculationId!=request.CalculationId || snapshot.RequestSha256!=hash || !snapshot.Drained)
                throw new InvalidOperationException("original qualification query");
            if (golden) {
                if (hash!="19b5c3d290046bebe246079501c31bb2ab557e96d4fc42acdba97e674338a14d" ||
                    report.PlannedCount!=1 || report.ValidCount!=1 || report.FailedCount!=0 ||
                    report.ExcludedCount!=0 || report.NotExecutedCount!=0 || replay!.Calls!=1 || report.Benchmark!=null)
                    throw new InvalidOperationException("DG-QL-GOLDEN");
            } else {
                var b=report.Benchmark ?? throw new InvalidOperationException("Benchmark report absent");
                if (b.Mode!=bp!.ExecutionMode || b.Profile!=bp.Profile || b.RecordedRun!=bp.RecordedRun ||
                    b.WorkPlanSha256!=QualificationCodec.ArtifactFromBytes("work-plan","test","1",
                        QualificationCodec.EncodeBenchmarkWorkPlan(bp)).Sha256 || b.Planned!=3 || b.Succeeded!=3 ||
                    b.Failed!=0 || b.Cancelled!=0 || b.TimedOut!=0 || b.NotExecuted!=0 ||
                    !b.ResourcesReleased || !b.SourceRun.Complete || b.DroppedSamples!=0 ||
                    b.Criteria!=CriteriaStatus.NotEvaluated || b.Attempts.Count!=3)
                    throw new InvalidOperationException("DG-QL-BENCH identity/counts");
                if (recorded) {
                    if (clock!=null||probe!=null||sampler!=null||assets!.Calls!=2 ||
                        hash!="9c8faac2c36c8440b878f68c3e76762ad5937f7bf4594f800972cc913f37ebcd" ||
                        b.Origin!=RecordedOrigin.SoftwareFixture || b.SourceRun.OriginCalculationId.Value!="BEN-ORIGIN" ||
                        b.SourceRun.OriginRequestSha256!="84ca63f41720dc748b4e68556938ab63a8002c38da5adcbd78c1ce36261d5188")
                        throw new InvalidOperationException("DG-QL-RECORDED origin/zero calls");
                    foreach (var item in new[] {("Queue",2,3), ("Service",10,15),
                        ("ProbeElapsed",12,18),("ProbeReleased",15,20),("EndToEnd",80,80)}) {
                        var q=b.Quantiles.Single(x=>x.Stage==item.Item1);
                        if (q.P50!=TimeSpan.FromMilliseconds(item.Item2)||q.P95!=TimeSpan.FromMilliseconds(item.Item3)||
                            q.P99!=TimeSpan.FromMilliseconds(item.Item3)||q.Criteria!=CriteriaStatus.NotEvaluated)
                            throw new InvalidOperationException("DG-QL-RECORDED quantile "+item.Item1);
                    }
                    var metric=b.Metrics.Single();
                    if (metric.SampledPeak!=100 || metric.RetainedDelta!=0 ||
                        b.Throughput.Window!=TimeSpan.FromMilliseconds(60)||b.Throughput.CompletedPerSecond!=50 ||
                        b.Throughput.SucceededPerSecond!=50) throw new InvalidOperationException("recorded resource/window");
                } else if (hash!="81a62fe88e1c39fcd336844cfe9acd7e9ab0aa25e0144ff904763251daab2bb9" ||
                    probe!.Prepares!=1||probe.Invokes!=3||probe.Drains!=1||
                    sampler!.Prepares!=1||sampler.Drains!=1||sampler.Samples<5||clock!.Calls==0)
                    throw new InvalidOperationException("DG-QL-EXECUTE actual calls");
            }
            // 核报告后只保存有界HostCompletion摘要；不调用Store/EvidenceSink，不能声称报告已耐久。
            workCode=0;
        } catch (TimeoutException e) {primary=e;workCode=7;}
          catch (OperationCanceledException e) {primary=e;workCode=4;}
          catch (Exception e) {primary=e;workCode=5;}
        finally {
            if (root!=null) {
                try { var originalClose=root.CloseAsync(TimeSpan.FromSeconds(2),CancellationToken.None);
                    cleanup=await originalClose.WaitAsync(TimeSpan.FromSeconds(2));
                    if (!cleanup.Drained || !cleanup.Completion.IsCompletedSuccessfully || cleanup.Diagnostics.Count!=0)
                        cleanupCode=6; }
                catch (Exception e) {cleanupErrors.Add(e);cleanupCode=6;}
                try {owner.RecordHostCompletion(rootId,new HostCompletion(
                    business?.CalculationId.Value??mode,business,primary?.GetType().Name,cleanup,
                    string.Join(";",cleanupErrors.Select(x=>x.GetType().Name)),workCode,cleanupCode));}
                catch(Exception e) {cleanupErrors.Add(e);cleanupCode=6;}
            }
        }
        if (primary!=null) Console.Error.WriteLine("work: "+primary.GetType().Name);
        foreach(var e in cleanupErrors) Console.Error.WriteLine("cleanup: "+e.GetType().Name);
        return cleanupCode!=0 ? cleanupCode : workCode;
    }
    public static async Task<int> RecoverAsync(QualificationRecoveryOwner owner,string rootId,int code) {
        if (owner.QueryRoot(rootId)==null) return code==0 ? 5 : code;
        try {var original=owner.ObserveRootAsync(rootId,TimeSpan.FromSeconds(1),CancellationToken.None);
            var state=await original.WaitAsync(TimeSpan.FromSeconds(1));
            if (!state.Drained || !state.Completion.IsCompletedSuccessfully || state.Diagnostics.Count!=0 ||
                owner.QueryHostCompletion(rootId)==null)return 6;
            owner.AcknowledgeReleased(rootId);return code;
        } catch(Exception e) {Console.Error.WriteLine("cleanup: "+e.GetType().Name);return 6;}
    }
}
// 两消费者各只选择一个Main。Benchmark Host的两个mode分别验证执行/录制，不是新消费者数量。
static class GoldenConsumer {
    static async Task<int> Main() {
        var owner=new QualificationRecoveryOwner("governance-golden-process",1,64,16,16777216);
        int code=await QlConsumerHost.RunAsync(owner,"dg-ql-golden","golden");
        code=await QlConsumerHost.RecoverAsync(owner,"dg-ql-golden",code);
        GC.KeepAlive(owner);return code;
    }
}
static class BenchmarkConsumer {
    static async Task<int> Main(string[] args) {
        bool recorded=args.SequenceEqual(new[] {"recorded"});
        if (!recorded&&!args.SequenceEqual(new[] {"execute"}))return 2;
        string rootId=recorded ? "dg-ql-recorded" : "dg-ql-execute";
        var owner=new QualificationRecoveryOwner("governance-bench-process",1,64,16,16777216);
        int code=await QlConsumerHost.RunAsync(owner,rootId,recorded ? "recorded" : "execute");
        code=await QlConsumerHost.RecoverAsync(owner,rootId,code);
        GC.KeepAlive(owner);return code;
    }
}
~~~

两个构造函数直接采纳上游已接收夹具字段，仅复制调用方构造不复制其数值算法或私有测试程序集；来源块按UTF-8、LF，从方法声明起至闭合花括号后两个LF（Golden）/一个LF（Benchmark），SHA-256：Golden=`0c5e0ee0154e754fc29f3483ff354997575d8ce9b6cdde4fa446349d1508d8b6`，Benchmark=`af65601ab0d13f383eee0b7ef842c9a300ec9ad2210613071ad5c0c845d842c3`。本模块局部ports是BCL隔离软件夹具；NoNumerics确保不存在隐藏统计调用，SealedReplay只传原Consistent等结果、不运行比较器，SoftwareProbe的Task.Delay不是产品算法/真实设备。实际输入通过宿主原Owner端口装配，公共能力声明/Codec及FieldPath只消费已冻结契约，不产生新产品API。


### 13.1.6 结果消费、原身份恢复、codec与接入验收

本节限定消费已接收的Golden/Benchmark软件合同；不会因上游新增其它分析字段而自动扩大本模块桥。Deming上游桥已限定接收，本模块当前无其请求/结果消费者，核对与复用边界见§13.1.7。

| 原结果 | 必须消费的完整字段与解释 |
|---|---|
| QualificationOutcome | 保存Terminal、CalculationId、Report?、Diagnostics、Resources；报告缺省是明确缺报告，不造空成功。业务Completed、报告可计算/完整/适用、已声明Criteria、资源Drained分别判断；Cancelled/TimedOut/Failed/Rejected保留原终态与诊断，不折成模型质量失败。Resources的Drained/ReleasedBytes/ReleasedSlots/DrainElapsed/CleanupDiagnostics全保留；不能用借用资源的业务回执替Root/Service自身最终关闭 |
| QualificationReport | 保存CalculationId/ReportSchemaVersion/Input/Plan/Method/Scope/Evidence、PlannedCount/ValidCount/FailedCount/ExcludedCount/NotExecutedCount、Values/Diagnostics、Completeness/Applicability/Criteria、RequestSha256/ContentSha256/NumericalResults/Benchmark?。Input/Method/Scope/RequestSha256精确核当前冻结请求；Plan与ContentSha256沿原qualification输出身份保存，归档时只由§13.1.8原QualificationReportCodec封口/核QLRP，不猜Plan投影或自行重算报告字段。Values的Available仅消费finite且单位/Method一致的量，Unavailable保留Reason；NumericStatus/数值来源留在原NumericalResults，不补0。Partial/Limited/NotEstablished、缺目标NotEvaluated均保留，不改成MeetsDeclaredCriteria |
| 原诊断 | Outcome.Diagnostics、Report.Diagnostics、Resources.CleanupDiagnostics和RootCloseResult.Diagnostics分开，逐项保留Code/Severity/Phase/FieldPath/CellId/ObservationId/MessageKey/EvidenceRefs/BackendCode/Build；治理按既有DG错误和Gap投影，同时引用原QLF诊断，不创造同义上游错误表。cleanup不覆盖primary，翻译/显示不能改原数值或状态 |
| BenchmarkReport身份/计数 | 保存Mode/RunId/Origin/Profile/RecordedRun?/WorkPlanSha256、Planned/Succeeded/Failed/Cancelled/TimedOut/NotExecuted、ResourcesReleased/DroppedSamples、Quantiles/Metrics/Criteria、Attempts/Samples/Throughput/SourceRun。完整ArtifactRef核原字节；Measured计数守恒，Warmup在SourceRun/Attempts单列且纳入失败政策，不混进Measured分母。SourceRun保留§13.1.4.1全部23字段，源资源未确认不得由本次分析Drained补真 |
| 分位、资源及吞吐 | Quantiles逐项Stage/Samples/P50?/P95?/P99?/Criteria/Reason；七个Stage包括无样本的Prepare与CancelToRelease条目，无样本保持null与原因。Metrics逐项Metric/Scope/TargetId/Unit/Acquisition/Attribution/Samples/Baseline?/SampledPeak?/RetainedDelta?/Slope?/Criteria/Reason，Shared/Unknown不升级Attributed。Throughput保留Window?/Completed/Succeeded/InFlight/CompletedPerSecond?/SucceededPerSecond?，缺窗口不可测用null；只由qualification计算，Adapter不另写分位/趋势算法。业务失败、未开始、缺采样、未释放全保留，不能只存成功P95 |

两个Host正常路径在原报告仍受Root持有时完成身份/结果核对，再记录HostCompletion；FixtureLedger只保存进程内原身份/查询投影，没有跨重启幂等或耐久能力。空Methods的NoNumerics明确声明无数值能力：Golden/Benchmark选择分支只依其各自Replay/Probe/Reader，不要求一个无关Bias/GRR能力；若实现错误派发CalculateAsync，夹具立即失败且Calls非零。SoftwareProbe的Drain只观察同一原Invoke Task，未完成时Drained=false；重复Drain复用原回执。Sampler无后台工作，Drain完成仅证明软件采样调用已退出。两种lease仍由qualification原协调门在Drain Completion后Dispose一次，lease.IsReleased仅是fixture检查，不能冒真实native退出。Factory前只有有界BCL输入/ports构造，无工作或外部资源；Factory接纳即由Root登记强持，部分创建失败同Root.Close。输入/资产复制均计入16MiB预约，真实规模按Profile调整而非放大无界内存。

**取消与恢复。** 宿主保存原CalculationId与EncodeRequest生成的RequestSha256；`CancelCalculationAsync(new CalculationQueryRequest(id,hash),waitToken)`请求取消这个计算，`QueryCalculationAsync(new CalculationQueryRequest(id,hash),waitToken)`只读原ledger。两者必须在Root.StartOwned的ControlWait预约内启动，原返回Task强持；ValueTask端口在delegate内AsTask一次。取消/查询的观察timeout仅结束WaitAsync，不释放原请求/Task/lease，不换ID/hash重发EvaluateGolden或Benchmark。snapshot逐项核CalculationId/InstanceId/RequestSha256/AdmissionId/TransferId?/Stage/ReportRef?/AdmissionState/Drained/RequestRevision；同ID异hash明确冲突，Unknown/NotFound不能推断无副作用或未执行。AdmissionUnknown不启动Replay/Probe；ConfirmedAbsent只保留未接纳事实，不自动再次接纳。独占Host才最终Root.Close统一Stop/Dispose，共享Service不能因本操作取消被Stop。

关闭失败保存primary/cleanup两轴及原HostCompletion；RootCloseResult.Drained、原Completion真正结束、诊断和全部lease归还共同作为确认条件。未确认保留原Owner/Root并用ObserveRootAsync原rootId继续观察，只有确认归还且HostCompletion存在才AcknowledgeReleased；等待包装Task完成不能作为释放证明。示例Main是有限软件Host，正常或可恢复失败均非零检查；生产宿主Owner生命周期必须长于这份操作，不能在未排空时退出进程并称资源已释放。确需转交只沿上游同进程原TransferOffer/TransferId/确认Owner协议，不序列化Task或造跨重启资源回执。

**codec与耐久。** 原QualificationCodec的输入/请求/Benchmark域保持；完整报告由qualification 0.2.6-prep另提供QualificationReportCodec、QualificationReportArchiveFactory及optional Storage adapter，准确消费见§13.1.8。SourceRun仍沿原EncodeBenchmarkRecordedRun，本桥不补同名codec、JSON私有报告、Schema或资格Store。现有两个Host的EvidenceSink=null且仅内存ledger/HostCompletion，保持未耐久事实；生产归档走原qualification Owner的Prepare/Save/Query/Read，治理§13.2只存自己的结果和精确外部报告/归档关联，不将QLAR送入dg.report-v1 codec或由治理事务冒资格提交。原Report.ContentSha256不证明耐久/来源真实/客户资格；Unknown沿原SaveIdentity技术查询，不重复计算或换键保存。

本夹具实际来源域如下，作为未来AQ01–03的精确输入断言；不是新产品Schema或第二套编码实现。QLBW不含Mode/Recorded，三份QLRQ分别绑定原执行、当前执行和当前录制分析。

| 域/身份 | 完整bytes | SHA-256 |
|---|---:|---|
| QLEP / plan-replay | 31 | `c5e04068ac72dafc3c115f33e3b59dfedf9d65200b132f1274f1d17581cbf0a8` |
| QLIP / snapshot-replay | 103 | `72c3e3d57bddedb2b46735ac960babc1bc7bd47d177ebe6333ab232ec9321a46` |
| QLCS / cases-r01 | 37 | `03b2bbeffe0aedf5781d54cb9eaead2fbb8b543d4f2a9448eebfceb575f65b90` |
| QLGP / P01 | 250 | `6eab19c20281531061098bcc6985e8b9165b39b7c4d0300d11d699b2ac5a7455` |
| QLRQ / G01 | 974 | `19b5c3d290046bebe246079501c31bb2ab557e96d4fc42acdba97e674338a14d` |
| QLBP / BP01 | 402 | `4dfdfb3ed4069f06fca30a816ab5563adeb52835928dcfad640990546bd497bc` |
| QLBW / 固定工作计划 | 444 | `bdc51b8843efefffc2cefdcfb5fe3c8235d0e2e1ff79484296830c2a56f84d80` |
| QLBR / BR01 | 2071 | `3b3aba3d0755d1bd7cb7086f7ddd7dad5849f1e80a5df32563ee17fc154e140a` |
| QLRQ / BEN-ORIGIN | 1171 | `84ca63f41720dc748b4e68556938ab63a8002c38da5adcbd78c1ce36261d5188` |
| QLRQ / BX-EXECUTE | 1171 | `81a62fe88e1c39fcd336844cfe9acd7e9ab0aa25e0144ff904763251daab2bb9` |
| QLRQ / BR-ANALYZE | 1268 | `9c8faac2c36c8440b878f68c3e76762ad5937f7bf4594f800972cc913f37ebcd` |

以下是未来本模块同一Integration TestHost中的验收断言，尚未实现或运行，不另建测试工程：

| ID | 输入/触发 | 可判定期望 |
|---|---|---|
| AQ01 | GoldenConsumer完整请求/封存Replay | G01请求974 bytes/hash、案例1/一致1/失败0/未执行0、Replay一次、Numerics零次；未重跑比较器，无Benchmark；查询原ID/hash，Root真正关闭，Host两轴0 |
| AQ02 | BenchmarkConsumer execute | 完整Profile/WorkPlan/QLRQ身份；Probe Prepare1/Invoke3/Drain1、Sampler Prepare1/Drain1且阶段采样≥5、Clock有调用，原完成Task后lease只归还一次；完整SourceRun/原Attempts，不声称客户时延达标 |
| AQ03 | BenchmarkConsumer recorded | Reader恰2次；Probe/Sampler/Clock用拒绝计数端口注入也零次调用；QLBR2071/源BEN-ORIGIN1171/当前1268身份精确，Queue2/3/3、Service10/15/15、ProbeElapsed12/18/18、ProbeReleased15/20/20、EndToEnd80ms，吞吐50/s、峰100/delta0；缺目标NotEvaluated |
| AQ04 | Profile/Recorded缺来源、同Ref异bytes、附尾/截断/超限、Clock/phase/索引非法 | 原QLF完整诊断/FieldPath；启动Probe前拒绝；不由文件名/latest补源，不生成部分可派发Plan，EOF严格消费 |
| AQ05 | 取消/观察超时/AdmissionUnknown/迟到Invoke或查询 | 同ID/hash查询；原Task/输入/lease仍Root持有，未执行不补0，Cancel不Stop共享Service；原Invoke退出后Drain/Dispose各一次，cleanup不覆盖primary，未确认非零且保持恢复入口 |
| AQ06 | 源Complete=false、DroppedSamples>0或ResourcesReleasedTick缺省 | 保留原缺口/失败/未派发行、null时刻和NotEvaluated；本次分析Drained不把源ResourcesReleased补true，来源不从SoftwareFixture升级实机 |
| AQ07 | qualification同ID异hash、model-assets错Scope/Principal/RequestEpoch/摘要/wrapper、seal Unknown/Simulation | 冲突或保留Unknown，禁止盲重提交/再训练；成功Value先接管OwnedResources、ActualLength/FileDigest/EOF与Files完整核对；Simulation不成为Production，model-assets仅原ResourceId/operation查询确认释放，无用途/质量放行 |

真实Adapter需编译核对公开DLL/namespace/全字段；实际Replay来源真实性、纯计算probe完成屏障/资源测点、报告codec注册/耐久恢复分别验收。客户阈值、现场分布/节拍、资格/用途采用由原授权Owner提供。Criteria/Coverage/报告生成/资产confirmed seal均不授生产质量放行、设备命令或模型用途。

本轮主控已限定接收§13.1.4–6的A1-Qualification指导内容及model-assets Service0.3受影响原回执映射核对；不授整Adapter、真实后端、报告耐久或客户资格。S7及qualification Deming桥现已限定接收；本模块是否使用按§13.1.7当前消费者边界，不据上游能力新增任务。

### 13.1.7 Deming消费适用性：复用上游，不新增本模块能力

本轮已定向读取[qualification 0.2.5-prep §6.4/A.3.1.1](../qualification/DEVELOPMENT-GUIDE.md#a311-constantratiodeming-s7-精确桥本轮新增范围)及本模块现有公开请求/端口/调用。主控已限定接收上游ConstantRatioDeming专用桥，statistics S7已接收；当前本模块**没有Agreement/Deming真实调用需求**。工程状态仍NewProjectRequired，预定Core/Tests目录不存在；本结论来自唯一指导已冻结消费者与调用路径，不声称审计了未创建的产品代码。

| 当前消费者或名称 | 已冻结输入与调用 | 本轮适用性结论 |
|---|---|---|
| 缺陷/OCR及其它视觉模型评价 | §3.2的六种TaskKind；TruthValue/Prediction只有类别、文本、区域，§6.8端点为计数/分类/区域/OCR；§7.2只经PredictionSource→覆盖/Endpoint/Intervals | 无带单位的双侧标量观测、CenterX、误差方差比证据或AgreementPlan；不能从类别序号、OCR距离、score、区域像素计数拼造Deming两轴 |
| training Validation / IFactPort核验 | Partition.Validation是训练验证划分，TrainingSpec/Configuration约束训练候选；IFactPort.VerifyAsync只核来源/标签/资产/方法与ClosureReceipt | Validation不代表计量一致性分析，MethodApplicable不启动回归。不得借核验增加AgreementAnalysis、生产资格或质量判定 |
| 统计区间与候选配对比较 | IStatisticsPort.ComputeAsync(IntervalQuery)输入为GroupStatistic整数分子/分母/义务；S6用GroupRatioTask/GroupPairedRatioTask | 配对计数比/差不是测量误差模型；不将IntervalKind.OwnerMethod注册成Deming CI，不新增Endpoint、IntervalResult或数值provider |
| qualification证据Host | §13.1.5只构造GoldenAnalysis或BenchmarkAnalysis，ValidateDesign检查这份请求；NoNumerics能力为空且CalculateAsync被调用即失败 | 未构造AgreementAnalysis/AnalyzeAsync/DemingNumericInput；两个既有消费者不因此增加统计调用，原输入/向量/Root/结果与收尾保持 |

无需在本模块重写逐字段Deming桥或新造“完整装配反例”；这些已有真实消费者和完整两Host/QDEM反例，唯一位置在上游A.3.1.1。若其它工具宿主需要双侧量值一致性，直接使用该已接收公开桥，原测量/配对/证据Owner提供完整请求并保存报告。本模块只按既有UsageIntent.Reports的RevisionRef关联外部精确报告，IFactPort沿原Owner核验完整性/方法适用，IUsageDecisionPort投影外部决定；不会由一份报告引用反向派发Deming或把Computed当用途授予。

复用上游时保留其原约束：λ=Var(error_Y)/Var(error_X)按原Y²/X²数值单位提供，显式轴转换同时转换λ与CenterX；完整计划配对/原来源、总体及左右Coverage、ScaledValue和诊断由原桥保留，不恢复超域double或删缺失对。无实际ConstantRatioDeming运行能力保持Unavailable/NotDispatched/NotEvaluated，不回退OLS/Pearson。原Root强持原NumericalRun/Completion/取消/查询与租约，业务和cleanup分轴、真正释放后收尾；本模块不复制其DTO、writer、算法、Owner或生命周期。CI、加权、异方差、相关误差、重复测量、误差校正与用途批准仍不属于此桥范围。

两轮有限自审仅核当前消费缺口：第一轮按请求→计算→结果核六任务输入、端点闭集、IntervalQuery与训练Validation含义，没有可支撑Deming的量值/配对/误差比来源；第二轮从空Host及Facts/Usage接线核两个分析变体、NoNumerics能力否定和外部报告关联，没有隐含Agreement派发。保留的反向断言沿既有DG-002未知任务/端点/未注册方法及NoNumerics失败门，不新增测试/工程或虚构计量fixture。本轮没有需要新增的消费者桥；今后若获批加入双侧量值任务，先明确真实消费者和原Owner输入契约，再定向接入上游，不能用当前分类/文本/区域字段补猜。真实上游DLL/能力/数值运行、物理配对/误差比来源与客户判据由对应工具验收；本模块既有真实Adapter/报告codec耐久/客户资格后门保持。本节适用性说明已主控限定接收，不改变既有切片接收。

### 13.1.8 qualification Report API 1：完整归档、技术回执与耐久恢复窄消费

本节只消费[qualification 0.2.6-prep A.3.4/A.5.4–A.5.6](../qualification/DEVELOPMENT-GUIDE.md#qualification-report-archive)和其[报告存储公开桥](../qualification/DEVELOPMENT-GUIDE.md#qualification-report-storage)。Core命名空间`Asun.Modules.Qualification`，optional Storage命名空间`Asun.Modules.Qualification.Storage`；IM-066 DTO来自`Asun.Platform.StorageDatabase.Contracts`。原Contract0.2、Golden/Benchmark/Recorded调用/夹具/向量、Deming无当前消费者、治理训练/UI/数据库设计保持；Report API 1不是请求Contract升级。以下类型与方法是公开规格，未声明实际DLL已构建。

| 本方装配/原公开入口 | 必须保留的输入、结果与作用域 |
|---|---|
| 纯归档codec/factory | `new QualificationReportCodec(new QualificationCodecLimits(MaxBytes,MaxStringBytes,MaxItems,MaxTotalItems,MaxDepth))`→`new QualificationReportArchiveFactory(codec)`→`Prepare(QualificationRequest,QualificationOutcome,QualificationReferenceDocument?,QualificationReplayEvidence?,IReadOnlyList<QualificationArchiveLink>)`。全部限额来自受管Host Profile并受治理Budget/root额度约束；参考软件限额沿上游(16777216,4096,1000000,2000000,32)，非客户容量。Root先预约输入/冻结副本/编码/流/结果的同时峰值，再调用，无UI线程大数组/隐含默认。PreparedQualificationArchive保存Archive、Report、RequestSha256、CanonicalBytes四字段，调用者只读，不逃逸修改底层数组 |
| 原参考与Replay来源 | 已有Reference/Replay事实由原Owner提供A.3.4的QualificationReferenceDocument、QualificationReplayEvidence完整值。若实际分析使用上游Reference/Replay adapter，则Host保留同原source返回的完整Use/Outputs/Result而非只投影的bool/一致率；不为归档再运行比较器。Golden缺实际Outputs不能用只有plan的旧fixture冒完整归档；Benchmark没有这两类证据可显式null。Links为每个原请求/结果/参考/Replay依赖的完整Path/Reference/Role/Owner/Bytes?/MediaType?/Format，按原Owner规则生成/核覆盖，未知不得编造Embedded或ObjectRef |
| Storage正式注册 | `QualificationStorageFactory.CreateRegistration(VersionRef statementCatalog,QualificationCodecLimits limits)`返回Catalog、Formats、ReferenceResolver、ReadValidation、WriteBinding、ReadBinding、InputSchema、ReadSchema。statementCatalog由qualification发布的精确SQL目录/部署提供，治理不编写第二份资格SQL。Host将原Catalog/Formats及OwnerKey=qualification的原scope/stores/引用与恢复验证版本加入IM-066正式注册；不以本模块ownerKey/Schema替换 |
| 原Storage adapter | `QualificationStorageFactory.Create(QualificationRoot root,RootReservation reservation,IStorageDatabase database,IStorageSession writeSession,IStorageSession readSession,QualificationStorageRegistration registration,IQualificationStoredArtifactResolver resolver,QualificationCodecLimits limits)`。Root/预约由原QualificationRecoveryOwner先持有；两session是Host已OpenSessionAsync并强持的Production/Query原实例。resolver只把原ArtifactRef关联受信ObjectRef/格式，不解释判定。Create无新runtime/数据库/隐藏窗口，adapter不Dispose共享database/session |
| 保存与原查询 | `SaveAsync(new QualificationArchiveSaveRequest(context,saveId,idempotencyKey,prepared),token)`→QualificationArchiveStoredReceipt的SaveId、State、Archive、Report、RequestSha256、SaveIdentity、Technical?、References。`QueryAsync(new QualificationArchiveQuery(currentContext,原SaveIdentity),waitToken)`只读原保存；nullable空返回不证明未提交。每个原Task在同root.StartOwned内登记，观察token不遮蔽原工作，未知不换SaveId或再Prepare/Save |
| 精确读回 | `ReadAsync(new QualificationArchiveReadRequest(currentContext,calculationId,原RequestSha256,原Report.Sha256,原Archive.Sha256),token)`返回QualificationArchiveReadResult?，完整Archive/Receipt/Links保留。当前Context获读权，不能沿旧写权/旧scope自动读；schema/hash/外对象缺失拒绝可用完整报告。只读不Analyze、不Probe、不重新训练/比较/分位或修旧报告 |

**归档顺序与身份核验。** 使用本模块§13.1.4–6持有的原完整request和真正完成的outcome（包括全部原诊断/Resources）；在原对象预算归还前Prepare。Report=null只保原ledger缺报告事实，不造空报告。完整失败/取消/TimedOut的部分报告可以封存，原Terminal/Completeness/Criteria/诊断/源资源不改为成功；业务完成与源资源释放/当前计算排空仍分轴。Prepare由原Owner封口QLQS/QLRP/QLRF/QLRE/QLAR并校跨字段；治理不复制writer/字段顺序或资格判定。

- RequestSha256必须等原`QualificationCodec.EncodeRequest(request)`的QLRQ hash；QLQS保存完整原请求/Plan/Input，不能把输入域hash替换原请求。
- prepared.Report为完整QLRP的ArtifactRef，Namespace=qualification-report、Id=CalculationId.Value+"/"+RequestSha256、Revision="1"；其Sha256与封口报告ContentSha256相同。QLRP不含自身ContentSha256；SealReport只能按上游规则封副本，原非空不一致hash拒绝，不能清hash绕校验。原旧fixture/hash不因此改写，也不声称已包含新报告向量。
- prepared.Archive为完整QLAR的ArtifactRef，Namespace=qualification-archive、同Id/Revision="1"，Sha256核CanonicalBytes全部字节。Archive hash、Report hash、原QLRQ hash、IM-066技术OperationIdentity.PayloadHash四域分别核，不能以QLAR/QLRP代技术请求hash。QLAR没有未来存储receipt回写环，不序列化Root/Task/CTS/native句柄。

**严格保存/读回。** 直接采用原Storage adapter的两个注册Binding `qualification.archive-append-v1`/`qualification.archive-exact-v1`，Formats `qualification.report-v1`/`qualification.archive-v1`以及原QLSP/QLSQ/QLSC/QLSD input/result codec；版本/hash由CreateRegistration按上游精确descriptor生成，实际发布仍绑定DLL/StatementCatalog hash，治理不手填格式hash/另注册相同ID。外link解析须完整ArtifactRef→ObjectRef，包括真实Bytes/Hash/MediaType/Format/StoreGeneration，去重引用仍保Path/角色；Embedded仅按原archive可重构内容验证。所有外对象可读/格式/EOF/hash及完整refs核验后才能确认耐久，未知/缺对象不得叫完整保存。

Save的成功消费条件为原StoredReceipt.State="Durable"、SaveId/Archive/Report/RequestSha256逐值等本次prepared、SaveIdentity的完整Scope/StoreId/StoreGeneration/OwnerKey=qualification/OperationId=saveId/IdempotencyKey/技术PayloadHash一致，Technical非null且Technical.Identity=SaveIdentity、State=Committed、ResultSchema=原registration.Catalog.Bindings中Version=registration.WriteBinding的唯一descriptor.ResultSchema、ResultBytes通过原QLSC strict codec并同所有References，原完整QLAR读回与所有外对象可读验真。QLSC内部状态Stored只是正文，不等于最终Durable；TechnicalCommitReceipt没有独立CommitId，只有原Identity/State/References/ResultSchema/ResultBytes/AtUtc，不造查询字段。读取Archive.Outcome.Report/Receipt.Report与原请求/QLRP/QLAR身份对应后才交给本模块Facts/用途关联；Available/Partial/NotEvaluated/Unknown参考等原值全部保留，不由耐久回执授用途。

未知保存保原SaveIdentity、原Save/Query Task、输入/Root/技术TaskHandle与资源回执；Save原Task尚未返回SaveIdentity时只观察并持有原Task/已登记saveId，不能猜技术PayloadHash拼出新identity查询或重发保存。取得原SaveIdentity后Query只观察同一保存，NotFound/null/ResultExpired不能证明无副作用。取消只停止本次观察/后续派发，晚到技术Committed留原身份，不重发Save或改报告。IM-066业务commit、操作任务/借用释放、外对象保持三个事实分别确认；释放按原ResourceHandle/ReleaseTask，原Root关闭只在实际工作结束后确认，不把返回StoredReceipt或Dispose已调用当pool已释放。已关闭的qualification root不能用于新保存：若计算已收尾，Host另在同永久会话规定的原RecoveryOwner建一个有界归档root/预约，持精确只读request/outcome再保存；这不是再启动计算、第二内容Owner或新会话。该归档root按原有限Close/Observe/Acknowledge协议收尾，未知仍由长寿命HostOwner持有。

重启只用保存的原完整SaveIdentity与当前Context Query/精确Read，旧Root/Task不跨进程复活；资格运行若未完成仍归原ledger/执行Owner，不能从半保存补算。Read路径由原adapter严格QLSD→原QLSP/QLSC/Technical关联→`codec.DecodeArchive(bytes,expectedArchiveSha256)`，完整typed还原且Encode逐byte相同。`DecodeReport(bytes,expectedReportSha256)`单独只证明QLRP报告，不证明原请求/来源/耐久闭包；未知Report/Archive版本、截断/附尾/键重复/超限/hash错按原QLF诊断拒绝，不能重序列化升级或用dg-le-v1 reader解析。恢复只有IM-066正式ReadValidation、原技术receipt与全部外引用读回核验通过才采用RestoredAndVerified；UI/Excel/PDF是原报告投影，不覆盖QLAR。

**治理存储的准确关联。** Host受信有限目录为本模块UsageIntent.Reports/IFactPort提供`RevisionRef→(原Report ArtifactRef,原Archive ArtifactRef,原QualificationArchiveStoredReceipt)`映射：RevisionRef完整Id/Version/Hash须逐值对应原ArtifactRef.Id/Revision/Sha256，同时目录必须固定其Namespace为qualification-report或qualification-archive及声明角色；同ref不同角色/不同归档/技术保存身份拒歧义，不用hash猜ID或相互替换。本模块只保存自己的dg.report-v1、原OwnerDecision和这份精确关联/回执引用；技术receipt完整内容保在原qualification/IM-066闭包，Facts通过原Query/Read当前核验。成功读取不自动构造OwnerDecision、Active、质量PASS或模型用途；外归档保存成功而治理commit Unknown时沿原治理operation查询，禁止重存资格报告或再跑计算。

新增AQ08–AQ10为未来§11同Integration mode的窄断言，未实现/运行：AQ08核完整Prepare/Save/Read四域身份、全Links/原诊断/源与当前Resources及原技术receipt（不替旧AQ01–03向量）；AQ09注入Report=null、错QLRP/QLAR/请求hash、未知版本/附尾/超限、缺外Object或错格式，核拒绝且Analyze/Probe/预测/训练/比较零次；AQ10注入Save/Query迟到/Unknown、原技术Committed但资源未退出、重启同SaveIdentity读回及治理commit Unknown，核原身份只读恢复、两轴错误/资源保持、无新SaveId/重算/隐含用途。上游QARC既有自审/存储断言直接复用，不复制其判定或重审数值。

### 13.2 本模块存储Binding与授权读回实施规格

采用IM-066公开注册契约，不通过私表/反射。本Adapter的`GovernanceStoragePayload : IOwnerStoragePayload`显式保存`VersionRef Schema`、`ContentHash GovernanceRequestHash`、`ImmutableArray<byte> CanonicalPayload`、`ImmutableArray<ObjectRef> References`；codec直接验证§5固定字段规范及下述Adapter信封，不重新JSON序列化。Binding目录冻结两个Transaction：`dg.snapshot-append-v1`（快照/标签选择/来源引用及publication结果追加）和`dg.report-append-v1`（evaluation/training/usage单一结果追加），两个Read：`dg.snapshot-exact-v1`和`dg.report-exact-v1`，都ownerKey=ai-dataset-governance。Transaction的InputSchema为`dg.append-v1`、ResultSchema为`dg.receipt-v1`；两个Read的InputSchema为`dg.query-v1`、ResultSchema分别为`dg.snapshot-v1`/`dg.report-v1`。原operation查询沿技术QueryOperation，不注册第五个事务。上游VersionRef的int Revision/hash由**本模块发布编码与SQL目录精确内容**计算，不能将字符串0.2或占位a hash当已发布VersionRef；未构建时示例仅Schema名，不宣称已注册真实系统。

每个Transaction单一完整治理修订，无更新/删除已发布行；StatementCatalog仅含有限参数化INSERT、同键hash读取/比较、引用登记及回执写，Serializable、同(scope/store/generation/owner/idempotency)唯一索引；执行者先原子取得该identity，不用先SELECT再INSERT冒唯一。并发同键同内容回精确原ResultId，同键异内容拒绝；MaxRetries=0由宿主依据技术Unknown查询，不盲重执。Min/MaxAffectedRows依据§13.2.2完整root/operation/引用计划checked总数，空批次拒绝，MaxCommands/rows/result/bytes按Profile显式预算。授权policy epoch和回执expiry在同事务/authority线性化边界核；没有可信映射时NotCommitted DG-003，不把两次Check当事务。

Read参数为精确ID/version/hash及当前读权receipt，按tenant/scope边界读不可变结果和引用；所有返回schema/bytes/hash/operation核一致，再复制成投影。页查询仅用于UI有界显示，具有总义务/水位/截断标记，不能拿一页当完整评估。原operation Query沿StorageRuntime公开QueryOperation，不依赖已释放Session。ExpectedMembers/Gaps/原观察/selection/模型binding/计划和原event ledger随canonical报告保存，保留政策由数据Owner决定；无读权不披露OCR原文。

以上Binding目录、codec与技术事务规格是**本模块可写内部Integration**，不是产品库迁移许可；实现只在本模块Adapter及测试生成专用隔离Store，产品部署需正式注册/权限/持久化环境。新增产品私表或全局权限仍禁止。全模块仍分PureCore、内部Integration、真实WPF/后端验证、现场用途，不以任一首片接收代替其余准备。

#### 13.2.1 Payload/报告/读回codec的完整规则

§5身份编码保持不变，新增的是Adapter存储信封与strict reader。Transaction的`GovernanceStoragePayload.CanonicalPayload`是完整`DG-APPEND-1`：域字符串、int32版本1、原治理RequestHash、必填原请求canonical bytes、nullable完整DG-SNAPSHOT-1 bytes、必填完整DG-REPORT-1 bytes；byte串均为uint32长度+字节，nullable先0/1。非Usage必须有完整Snapshot且与Report引用相同，Usage必须无Snapshot；snapshot-exact结果信封含单一DG-SNAPSHOT-1；report-exact结果信封含DG-STORED-REPORT-1（域字符串、int32版本1、原请求bytes、原报告bytes，依次以长度+字节编码）。不能只传EncodeBinding或报告后让SQL从私有Core对象找漏掉的Dataset/计划/Binding。References是精确文件对象引用，不把RevisionRef误强转ObjectRef。每个RevisionRef经原Owner的目录解析才取得ObjectRef，目录必须返回相同原ID/version/hash及实际ObjectRef，不可仅按文件名寻找。治理RequestHash与storage技术PayloadHash分别保存：前者是原治理请求，后者由上游StorageRequestHasher按完整事务信封计算，不互相替代。

**原输入传入存储Adapter的明确桥。** CommitCommand有完整Dataset和结果，但只有RequestHash/PlanRevision/BindingHash不能还原ModelBinding/EvaluationPlan；不得让Store读Core私有ledger。生产IReportStore实现同时提供本模块Adapters的公开`IGovernanceReportInputRegistration`：同一Adapters namespace提供`public sealed record ReportInputRegistrationReceipt(string OperationId, ContentHash RequestHash, bool Retained, string ReceiptId)`；四个同步重载`Check<ReportInputRegistrationReceipt> RegisterInput(EvaluationRequest request)`、`RegisterInput(TrainingRequest request)`、`RegisterInput(UsageIntent request)`、`RegisterInput(SnapshotPublicationRequest request)`。宿主在原RootSlot预留后、相应Start之前调用一次；Register用同CoreValidator.Freeze取得深冻结值，按§5相应DG-EVAL/TRAIN/USAGE/PUBLISH生成原完整canonical请求和原hash，按operation/hash保存受预算的本方只读副本；编码只读取Freeze输出的CopyModel/CopyPlan/CopySpec/CopyIntent/CopyRequest及入参不可变scalar，不再次遍历原draft列表。另提供`Check<ReportInputRegistrationReceipt> ReleaseInput(string operationId, ContentHash requestHash)`由原Host在未Start且已放弃或原operation真正结束时调用；在途Commit/读借用返回DG-008且Value=null并保留，重复已确认归还返回原Retained=false回执，异hash为DG-016，不重新派发工作。它不是另一Core输入协议。生产UI/无UI命令均经这个Host接线，注册拒绝不Start，Fake/内存夹具保持原端口实现无需该存储桥。

同operation同hash注册复用原值，异hashDG-016；实现保存字节及完整snapshot原引用，不保存原可变request/延迟collection/窗口。核验输出hash必须等于后续CommitCommand.RequestHash，Authorization/Idempotency/snapshot/spec/plan/model/usage逐值对应；未注册或不一致DG-005且无事务。注册回执Retained=true只表示输入副本仍受持有，ReceiptId由本实例operation/hash确定；Release的Retained=false仅表示本输入副本归还，不代表业务提交或外部资源。输入台账只在该Store实例中有界持有，容量/编码/CopyDraft计入同RootSlot/Budget，不能用静态字典；Commit原工作退出且技术提交知识已持久化后归还内存，Unknown未持久化保原root。重启Lookup直接核已耐久原请求bytes，不要求把Task或内存台账跨重启恢复。这里是新增Adapter消费桥，不修改已接收Core API/向量。

存储信封`DG-STORAGE-1`按§5标量规则依次编码：域字符串、int32版本1、Schema的(Id字符串、Revision int32、Hash字符串)、GovernanceRequestHash字符串、uint32 CanonicalPayload字节数及原字节、uint32 References数量及全部ObjectRef。ObjectRef按IM-066声明顺序递归编码，ObjectKey=(StoreId,Generation int64,TenantId,StorageDomain,ObjectId)，再Bytes int64/Hash/MediaType/Format VersionRef；按此Key的Ordinal/数值组合排序，重复Key或同Key异描述拒绝。CanonicalPayload的长度同时受本Budget.MaxCanonicalBytes及StorageInputLimits.MaxPayloadBytes，References数量受双方限额；预检信封总长度后才分配，不能压缩后绕预算。DG报告自己的ContentHash仅为对完整DG-REPORT-1 bytes的SHA-256，不递归纳入自身。

| 记录/Schema | 完整保存内容、校验和读取输出 |
|---|---|
| dg.snapshot-v1 | 完整CopyDraft按DG-SNAPSHOT-1，含全部成员、ParentId、来源、分层、类表、标签观察/selection/仲裁、split/holdout；按§5既有顺序，无训练视图/只存已选标签。reader重新构造SnapshotDraft→CoreValidator.Freeze→核Reference/成员/组数/hash一致，不用公开Frozen构造器。外部标签/来源引用只关联原Owner，不再创审批事实 |
| dg.report-v1 | DG-STORED-REPORT-1内完整原请求及DG-REPORT-1，含原ModelBinding/EvaluationPlan/spec/usage与原operation/request hash、四选一tag及原结果全部字段：Evaluation含Endpoints/Coverage/Intervals/Events/Gaps与QualificationGranted=false；Training含候选资产、Configuration/Toolchain/RunEvidence/NativeStopped/原执行回执；Usage含原Stage/decision/active/rollback/reason；Publication含Snapshot/labels/counts/gaps。原§5/§6排序全部保留。分别核原RequestHash、原DG报告hash和存储wrapper hash；ResultId仍是原报告hash索引，root contentHash为wrapper hash，不能互换。报告read输出原请求/结果独立只读投影；身份校验不替代Facts/权限/来源真实性 |
| dg.receipt-v1 | 原OperationId、GovernanceRequestHash、CommitStatus int32、nullable ResultId、ReceiptId，按CommitReceipt声明顺序；确认ResultId同时绑定本存储root记录中的entity/content hash。技术TechnicalCommitReceipt/资源回执由IM-066保存，治理receipt只关联其原TechnicalCommitReceipt.Identity，不伪造资源Drained。Lookup读技术原operation再对照这份原治理receipt，不能从某条report存在猜原请求已提交 |
| dg.query-v1（补足Read输入） | 自有`GovernanceReadPayload : IOwnerStoragePayload`，Schema、EntityKind int32（1快照/2报告）、EntityId、EntityVersion、ContentHash；这些字段依此顺序以域DG-READ-1/版本1编码。原CallContext带当前权限，不将凭证放进查询blob。snapshot-exact输入kind1/report-exact输入kind2，输出分别为上面完整信封。它是两个Read的明确InputSchema/InputCodec，纠正原概略目录把“输出Schema”也当查询参数的缺口，不改Core API |
| RunEvidence文件格式 | 采用DG-TRAIN-RUN-1/版本1、原operation/request hash、snapshot完整ref、spec原字段、完整configuration/toolchain ref、initial model ref、prepared manifest ref、实际环境ref、参数知识表、epoch/batch记录、validation记录、停止原因、候选/封存文件回执ref、未知/错误数组，依表次序递归按§5编码。环境/大型预测及模型状态保存原Owner精确引用，不复制上游私有报告或凭据。原字节完整封存后生成RevisionRef；TrainingProduct不会先回一个不存在的RunEvidence hash |

RunEvidence参数知识表按ParamName Ordinal保存Name/ValueType/RequestedCanonicalValue/nullable ObservedCanonicalValue/Knowledge（Observed或Unknown）/Reason；canonical value为具名scalar/tuple的§5有限typed编码，不取文化相关ToString。batch记录按(epoch,index)保存完整有序MemberId/重复位置、EffectiveBatch、LearningRate、CompletedUpdateOrdinal、原DLTrainResult键值/调用状态/回执引用；传统异常分支用单条整集记录及final_error/final_epoch，无假batch日志。validation记录依次保存完成更新ordinal（long）、输入manifest RevisionRef、完整ModelBinding（长度+EncodeBinding bytes）、完整EvaluationPlan（按原声明字段顺序，Partition必须Validation）、EvaluationResult（按§5该结果原字段顺序）、主要Endpoint名、nullable finite值、是否满足约束/是否被选中两个bool及原因。这些完整结果直接嵌入RunEvidence，复用评价内核/字段编码，不注册新的公共评价事务或把Validation伪装成DG-EVAL-1的Test请求；大结果仍受MaxRunEvidenceBytes和原Budget预检，超限失败而非缩写成无来源分数。因EvaluationResult不直接带Partition，用途由同一记录的plan/manifest及原training请求核明，不能脱离引用使用结果或反向授最终测试。停止/未知/错误用稳定Code/Phase/ReasonKey/原Owner receipt refs；不保存原exception对象/native handle。方法/字段缺失拒绝，不自动补seed/RNG状态。

注册使用`Asun.Platform.StorageDatabase.Contracts.IStoragePayloadCodec`（IM-066 §6.3）：Version、Schema、PayloadType、Encode(payload,maxBytes)、GetReferences(canonicalBytes,maxReferences)五项。输入codec分别只认GovernanceStoragePayload或GovernanceReadPayload，按Schema/Binding核kind；GetReferences必须严格读完信封再提取全部ObjectRef，Read参数返回Empty。结果codec实现同namespace的IStorageResultCodec.Version/Schema/Validate(resultBytes,maxBytes)，先strict decode/结构守恒再由本Adapter生成只读投影，不猜上游存在Decode泛型API。StorageBindingCatalog显式包含四个Binding及所需输入/结果codec；StorageOwnerRegistration包含原scope/store、ReferenceResolver和ReadValidation版本。

**strict reader**：先核bytes/count/每段长度和剩余范围，checked偏移；使用严格UTF8，未知版本/tag/enum、非法bool/null标志、非法UTF16、default数组、重复/乱序键、hash格式、超限/截断/附尾均拒绝。旧合法文档版本不等于新编码版本；原dg-le-v1 reader沿原Domain0.2，不自动改变字段。Report finite/整数计数/端点方法/coverage/Event/Gaps交叉约束按§6核对，区间不可算null保原Reason，不由codec重算统计。读回只验证已冻结值和原身份，**不重新预测、训练、仲裁或授资格**。Schema/codec/SQL目录以UTF8+LF发布精确字节、整数Revision和SHA-256；未知目录或错hash启动即拒绝受影响Binding，不用手填示例hash冒真实注册。

#### 13.2.2 不可变事务、幂等回查与重启恢复

IM-066采用PostgreSQL18/Npgsql10.0.3技术适配，治理只提供参数化StatementCatalog及Owner payload，不写第二连接池/驱动。内部隔离Store的逻辑表为dg_revision（entityKind/entityId/entityVersion/contentHash/canonical blob/governanceRequestHash）、dg_operation（完整Scope/StoreGeneration/owner/principal/kind/operation/idempotency、原请求hash、精确ResultId/ReceiptId）、dg_reference（entity完整键与全部ObjectRef描述）；tenant/scope/store-generation在每行及唯一键中必有，不用可改的全局schema代租户隔离。字段类型按§5的string/int/long/hash/byte[]，数据库约束保非空/非负/有限长度与Schema版本；不存图像/权重/native对象于DB。Read返回精确entity的完整blob与References，分页列表另由授权投影提供，不能替完整codec输入。

事务完整范围是§4.1 CommitCommand：Publication/Evaluation/Training带原完整Dataset，Usage的Dataset=null；恰一个结果非null。dg.snapshot-append-v1只处理Publication，dg.report-append-v1处理其它三种结果；每次同时生成原DG-REPORT-1 receipt结果。需要快照时完整CopyDraft必须来自治理原请求，而不是训练端口的受限Dataset；已有相同ID/version/hash复用，没有则同事务插入标为研究快照，不提升标签批准。

1. Adapter preflight核原RequestHash、结果全部闭包、refs和额度；构造IM-066 RegisteredTransactionRequest的Context、OperationIdentity、精确Binding VersionRef、Payload及同codec References，用StorageRequestHasher.Compute填**技术**PayloadHash。同一治理operation始终保同一storage identity/hash，Authorized Caller来自可信Host映射，不从command.Query字符串伪造。
2. Catalog用参数化INSERT ... ON CONFLICT取得dg_operation的原唯一幂等键，另有(scope/store/generation/owner/operation)唯一约束。原子锁定这行再核原治理/技术hash和principal/kind/idempotency；同hash已确认读原回执，同键异hash或同operation异key返回Conflict。不以先SELECT后INSERT提供“原子性”，重入不能再次追加子行。
3. 在同授权fence/技术WriterToken有效线性化边界核当前actor/tenant/scope/policy/domain/generation/expiry和技术单写者。当前权限不可确认则NotCommitted且无业务行；已经派发但提交结果未知则Unknown，不能把超时当回滚。权限Authority与DB事务若无法建立不可绕过的fence，生产写切片拒绝，不由UI或第二次Check弥补。
4. 在一个Serializable事务内插入/核对Snapshot root（可复用）、Report root、完整引用以及治理receipt，ResultId固定`dg-`+该DG-REPORT-1内容hash。entityId/version已有异hash拒绝；相同root也必须对照完整bytes/refs。原SQL目录固定这些步骤和完整参数，不接动态表名/任意SQL；Root数量/refs预检，MaxCommands/MaxAffectedRows是上述最坏总数，最小必需新增原operation及report/receipt为准，快照复用不使合法事务误判空批次。以StorageBindingDescriptor的有限上下界核执行计划；单次受影响行实际计数保原回执。
5. IM-066技术Committed且ResultId/bytes/hash/全部refs匹配才治理Confirmed；Rejected/RolledBack且能证明无该提交才NotCommitted，Conflict分别保存。任何Committed但报告缺项/错hash为DG-005并保原提交事实，不重写；Unknown/DG-012只保存原技术OperationIdentity/TaskHandle/TechnicalCommitReceipt和资源回执，Lookup原operation。重复Lookup是只读，不重执事务或重新计算；TechnicalCommitReceipt没有独立CommitId字段，不能捏造查询键。
6. StorageTaskStatus还在Accepted/Running/Draining时沿原TaskHandle有限GetTaskStatus/QueryOperation，不能把受管Task退出和CommitConfirmed互换。Close/资源释放沿IM-066原ResourceHandle/ReleaseTask；本模块原Task真实结束后才能归还自己的源/输入，技术worker未知不假释放。取消只停止观察/新派发；已耐久提交不被后到取消撤销。重启只恢复耐久identity/receipt并只读对账，无法恢复进程内Task/lease；技术Unknown的写者接管只由IM-066原fence/恢复协议执行。

**DB与文件不是天然跨库原子。** 新RunEvidence/数据manifest先在IM-066文件对象存储封口、核SealedDurable及EOF/hash，再进入引用事务；模型原件由model-assets封存，本模块不重存其文件。DB失败/Unknown不得直接删除新文件，保持原PendingPublication/引用保持并由原Owner的持有/GC策略对账；文件已封存而DB尚未知不授用途。ReferenceResolver按IM-066原OwnerReferenceSnapshot协议在同barrier下返回所有可达ObjectRef、稳定snapshot/epoch、有界页及Complete；查询一页/Unknown不能回答“没有引用”。ReadValidation验证完整dg_revision/operation/reference闭包及所有物理对象，无副作用；这两个公开Owner consumer均在本模块Adapter实现，不给存储模块访问私有产品表。

#### 13.2.3 来源、标签、审计与保留的唯一Owner

源目录是一份由数据Owner封存的有限manifest，完整行字段为Evidence RevisionRef、ObjectRef、EncodingId/Version、DecodedLayoutRef、CoordinateRef、Face、Modality、Origin、ParentEvidenceRefs、ValidDomainRef、可观察性/撤回receipt refs。manifest本身Id/version/hash与读用途授权必填；同Evidence重复或目录返回异身份DG-005，超限DG-008，未读到EOF/源不可达DG-004。所有实际文件经IM-066原受保护FileReadRequest/Read lease取得，不遍历任意路径或裸NAS文件。

支持解码注册表首版只有§8.2.2 raw Gray8格式、Owner声明的Gray8/Gray16/RGB8图像格式和§7.1.2 Region/整数行段格式；图像格式由原Encoding明确PNG/TIFF等及带版本decoder，生产AsunImage `read_image`在核完整原bytes的私有暂存文件上读取，随后核尺寸/channel/scalar/domain并经稳定rows PublishCopy。文件不是RGB时不猜交换色序，源TIFF/JPEG等若无法表达原域则独立ValidDomainRef必填；未知Encoding拒绝。不自造源物理单位/校准或给解码后的像素hash冒原容器hash：分别记录原bytes与派生像素/解码方法。解码/临时文件/流所有权在本source lease，成功/取消/失败都等实际读取/native退出再释放。NAS容错与耐久沿原storage Profile，本模块不加自动离线写分叉。

标签来自human-review原观察/仲裁/审批回执。Facts核完整LabelSet.Revision/Taxonomy/TruthMethod、ActorReceipt/VisibilityPolicy、selection与仲裁引用及当前撤回；本模块保存治理快照中不可变选择，不生成通用复判事务/伪审批，不将之后的人工意见改写历史。新真值、新来源或撤回产生新snapshot/operation并标明受影响报告，不覆盖已有评价。

授权Adapter的CheckAsync映射IM-authorization原AuthorizeAsync/RecheckAsync及GetOperationAsync，原ValueTask只AsTask一次登记；AuthorizationContext由当前Host受信会话提供，Query.Principal/Tenant必须匹配，Purpose/Scope/PolicyRevision映入精确ActionRef/ResourceRef/PolicyRef目录。只有当前非HistoricalReplay且Policy Allowed、未过期、完整原RequestHash关联可确认时才继续：UseKind.Read要求Audit NotRequired且不把Eligibility.Blocked误作读拒绝；UseKind.Mutate还必须EligibleAtEvaluation及Audit Persisted。两分支均核GateError=None及原完整AuthorityEvidence，满足才给Allowed=true；BeforeCommit是独立当前检查，原Store仍做fence。申请本模块写/读/预览各有独立Action/UseKind，不把训练权限当读OCR原文许可。

授权决策审计由authorization原Owner写；本模块不再写第二份“权限日志”。HostOutcome沿其RecordOutcomeAsync保存原请求/actor/approver/Action/Resource/Policy/authority/domain/generation、原业务Succeeded/Rejected/Unknown或CancelledBeforeDispatch及HostReceiptRef，原审计回执归该Owner。治理事实同时保完整request/hash、data/label/model/plan refs、覆盖/结果、commit knowledge和primary/cleanup两轴的有界诊断；敏感原文只在有明确读取权限的EvaluationEvent内容中保存。审计Unknown查询原AuditKey/RequestId，不生成新审计键重写；审计查询与报告查询均需当前技术读权，不披露凭据/native异常。

保留期、客户删除/脱敏权、原始数据授权及生产用途由数据/客户/权限Owner给有限版本化策略，软件不自定天数。删除影响采用不可变撤回/墓碑及原引用目录：已撤回/缺对象/缺完整目录→Facts不可用、UI显示不可读、训练/用途禁止新派发；历史报告hash和事实不改，不能把被删义务从分母去掉。实际物理删除/GC归IM-066获批计划及hold/fence，不是本模块按钮直接unlink。无删除授权仍可读授权允许的Core/离线研究输入，不阻断无关规格。

#### 13.2.4 Adapter增量的有限验收断言

以下补入§10同一Integration TestHost范围，尚未实现/运行；复用既有Budget/Root/错误/Unknown矩阵，不新建报告或脚本。

| ID | 输入/触发 | 必须断言 |
|---|---|---|
| AD01 | 完整Snapshot加Evaluation/Training/Usage/Publication各分支，封存/strict读回 | 原DG身份/观察/selection/全部义务和refs逐字段相同；训练受限视图不能替完整Dataset；宏均值/CI按方法保原值；外部报告只精确引用 |
| AD02 | 截断/附尾/超长/未知schema/tag/非法bool/重复或乱序refs/无分母/非finite | 无部分reader结果、无事务/外部工作派发；DG-001/002/005/008/013各按原语义；不能从一页构造完整报告 |
| AD03 | 并发同键同hash、同operation异key、跨tenant/principal、错技术hash/fence | 原唯一回执或Conflict，最多一次完整不可变事务；epoch/expiry变动在真实提交边界拒绝，第二次Check不能替fence |
| AD04 | 文件成功DB失败/Unknown、技术提交晚到、重启、审计Unknown | 原文件保持/原identity回查，无新键写/重训/自动删；耐久与业务/资源分别记录；进程内Task不跨重启伪复活 |
| AD05 | 训练N=3/B=2/2轮、N=1/B=4、best平局/无候选/early stop、传统异常 | 排序hash可复现，N=3每轮2更新及一次重复位置，N=1每轮3重复但仅1独立成员；平局选早、无候选失败；传统异常整集一次，无batch或exact resume；Test/Challenge零读取 |
| AD06 | 模型type/class/预处理变换错、损失非finite、配置缺LR、GC归一未完成、OOM/取消 | 派发前拒绝或原attempt失败，无自动batch/LR/网络改值；native未知保原worker与额度，不能NativeStopped=true；候选仅确认seal/fresh-read后交付 |
| AD07 | 有孔mask/空域/两对region/错坐标/超2^53计数/迟到native | HALCON逐对V交集，整数行段计数/守恒，空域不造centroid，Evidence/QueryHash完整；错误/未知不四个0，资源真正退出后释放 |
| AD08 | 撤权/标签更正/原对象删/ReferenceResolver缺页/读OCR无权 | 历史hash/分母不改，新操作按原Owner事实拒绝/不可读；原Actor/Audit不由字符串自证，GC不因缺页误判无引用 |

## 14. DEV-GOV-010六门与本轮结论

A1-Stats S6桥§6.8/§13.1.1–3已按本轮主控回执限定指导内容接收，C1/C2及U1原接收保持；实际statistics运行Capabilities/Adapter编译/报告codec注册与持久/客户资格仍另门。本版qualification Contract0.2的Golden/Benchmark执行/录制分析确定桥§13.1.4–6及model-assets Service0.3受影响原回执映射核对已由主控限定内容接收，不授整Adapter/真实后端/报告耐久/客户资格。S7及qualification Deming桥已主控限定接收；本模块当前无Deming消费者，§13.1.7只明确复用边界，本轮适用性说明已主控限定接收，不影响既有接收。

| 切片 | ①边界/消费者 | ②唯一API/单位/生命周期 | ③无UI宿主 | ④断言 | ⑤Profile | ⑥工程/范围/后门 | 当前接收 |
|---|---|---|---|---|---|---|---|
| C1 | §1/2、缺陷/OCR | §3/5/6.1–3 | §9输入/Freeze | C01–08/10/Golden | §12 | §11 | ModuleCoreImplementationReady：2026-10-10主控六项规格接收，无实现/运行声明 |
| C2 | §1/7、训练/评价工具 | §4/6/7 | §9完整端口/根 | A01–12/C09 | §12 | §11 | ModuleCoreImplementationReady：2026-10-10主控六项规格接收，无实现/运行声明 |
| A1 | 原Owner确定映射§7.1.1–2/§13.1–2 | 已明确公开DTO/方法/回执/租约及不支持项 | §9合成+固定Binding规范 | Integration矩阵、C09及AD01–08 | §12真实负载 | §11 | 原映射、S6桥、qualification桥§13.1.4–6及model-assets Service0.3受影响原回执映射核对已主控限定内容接收；本轮完整Adapter软件设计及§13.2自审已闭合；§13.1.8外部报告codec公开接线已闭合；真实后端/格式注册与耐久/产品资格另门 |
| U1 | 可选控件，不改事实 | §8Binding/命令/三语/根及只读证据桥 | §8.2.1–3精确图/ROI、双STA及生产viewport装配/清空恢复 | U01–U11 | §12投影/显示负载 | §11 | U1限定指导范围已主控接收（2026-10-11本轮派发确认）；本轮生产装配/任务流新增规格自审完成；真实WPF/viewport/后端资格未关闭 |
| A1-Stats S6桥 | §6.8/§13.1.1，单模型报告及候选配对报告 | §13.1.1全字段/预算，§13.1.3同步/异步原Owner | §13.1.2.1从空Host构造两个mode及根先预留 | §13.1.3 AS01–07、完整输入/请求与draw Golden | §12 S6桥负载/测点 | §11 Adapters/Integration同一Exe，§13.1.3只读证据/权利/codec门 | 本模块0.2.3 S6桥限定指导内容已主控接收；无实现/运行声明 |
| A1-Qualification Golden/Benchmark桥 | §13.1.4，原封存Golden和纯计算性能/录制分析两个消费者 | §13.1.4–6完整字段/来源/12参数Factory/Root/取消查询/codec | §13.1.5两个Main，完整构造及本模块局部BCL ports | §13.1.6 AQ01–07、11规范向量/录制分位/失败恢复 | §12与§13.1.4.1完整Profile/工作计划/负载、真实资源与当前分析两轴 | §11既有Adapters/Integration路径，§13.1.6禁止重新授用途/质量权及真实codec/后端门 | 0.2.4 A1-Qualification指导已主控限定内容接收；无编译/运行声明，不授整Adapter/真实后端/报告耐久/客户资格；S7及qualification Deming桥已接收，本模块无当前Deming消费者，见§13.1.7 |

本指导总体仍`DesignReview/Prep`。本轮整模块可决定的软件规格和自审已闭合，定位及精确外门见§18；原`PreparationIncomplete`中的本模块存储/训练/生产预览设计缺口由§7.1.1–2、§8.2.3、§13.2.1–4关闭，不再用这些缺口阻断无关准备。C1/C2的ModuleCoreImplementationReady保持原规格接收；整模块ImplementationSpecificationReady/实际Adapter和生产资格不由本轮自动授予，qualification 0.2.6-prep完整报告codec/归档存储契约已由§13.1.8准确消费，原上游软件契约欠项关闭；实际DLL/注册/耐久恢复仍须实跑。新增指导不等待总控再作内容审核。实际WPF/租约/后端/产品资格仍须实跑；本轮未执行产品build/run、真实HALCON/WPF/训练/推理、性能、Replay/Shadow/Advice/HIL/现场。文档结构/hash核对不是运行资格。

真正外门仅阻断依赖部分：客户/设备才能提供的物理可观察参照、任务taxonomy与误接受/拒绝阈值、真实数据授权及脱敏、现场分布/OOD和硬件资源/节拍目标、真实训练/模型/区域/存储/现场回退证据、生产用途Owner正式签发与产品Schema接入。模块内部API、Fake、根/取消/规范字节、通用统计/布局不借这些门延后。A1已有上游公共契约映射和本模块Binding规范；超S6支持域/未发布运行能力、真实authority传输只影响对应请求；Deming当前不在本模块消费者范围，上游桥的真实能力/物理资格门由原Owner维护。适配代码和U1真实控件行为属于后续实现/验证项，不冒充内部文档已缺整套接口。

## 15. 定向自审与研究采纳记录（2026-10-10）

两轮有限自审：第一轮从输入/数据科学反例检查版本丢失、非法可选默认值、集合深复制、覆盖交叉维度、CER/FP负担、同源划分和标签泄漏；第二轮从外部宿主检查端口输入可读取、根先预留、原Task保留、取消/查询/cleanup独立、提交知识Unknown与资源Unknown分离、迟到/唯一释放、两个Host和UI绑定的接线。问题修正在本文，不新建审计报告。实际定向检查结果见§16；不将自审文字当自动化实现测试。

技术证据复用：scikit-learn **1.7.2** commit `25dee604bae18205b01548348388baf7a1cdfe0e` 的`_split.py` GroupKFold/StratifiedGroupKFold/GroupShuffleSplit及`tests/test_split.py`相关无跨组/分层测试，BSD-3-Clause、Python≥3.10/numpy/scipy/joblib/threadpoolctl；借分组思想/反例，不复制Python产品依赖。MLflow **3.3.2** commit `9e9abf26f8aa7b546610652fa2556e09f2a83cd2` 的`sqlalchemy_store.py` alias merge/get与相应测试，Apache-2.0、Python≥3.10/Flask/alembic/sqlalchemy等；可变alias换绑不能作精确生产身份，不复制其Registry事实Owner。具体原件版本/hash/依赖记录复用[REF-002](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)，未安装/执行上游测试。

微软官方.NET10 `Task.WaitAsync`、协作取消与`Rune.DecodeFromUtf16`文档本轮只读核对：协作token不是强制停止，观察Task与原Task有区别，UTF16合法性需显式解码。OCR源码/测试及文本方法既有研究沿DEV-AI-063 §14复用，不再全研。DevExpress本机`Components/Bin/NetCore`随附25.2 XML定向读取DockLayoutManager、TreeListView Key/Parent字段、Grid.Core ItemsSource/SelectedItem/AllowEditing/Begin/EndDataUpdate、PropertyGrid.SelectedObject/ReadOnly、ChartControl；未扫描实现、不做依赖许可核验。PropertyGrid说明歧义保留真实行为验证。

HALCON26.05算子资料已读：region变换像素角/点变换原点差由坐标Adapter明确；intersection第二参数多对象先union，必须逐对匹配；area_center空域默认0不是有效中心。train_dl_model_anomaly_dataset整集与gc_anomaly batch不同，apply_dl_model按batch并padding，少样本不保证同比低内存。路线由AsunImage公共`ImageLibDotNet.cv2`执行，未重复确认覆盖/扫描内部；只在实际C#类型/重载歧义查公开签名。几何/训练native性能和停止仍需真实验收，不从手册或编译推定通过。

## 16. 本轮实做检查与保留限制

0.2.7-prep（2026-10-12）只消费qualification 0.2.6-prep A.3.4/A.5.4–A.5.6：§13.1.8补完整报告归档的公开Core codec/factory、原Reference/Replay输入、optional Storage CreateRegistration/Create/Save/Query/Read、QLRQ/QLRP/QLAR/技术PayloadHash四域、原TechnicalCommitReceipt、Unknown/重启只读恢复与治理精确关联，§13.1.6及§14/§18同步原上游软件契约欠项关闭。旧训练/预览/UI/数据库设计、Host代码/向量和完整范围结论保持；现有内存Host仍EvidenceSink=null，不能提升耐久或运行资格。

本轮两轮有限自审仅针对新消费桥：第一轮核原工厂/limits/Namespace/ArtifactRef完整四字段、归档与请求/报告不同身份、原Owner格式注册及完整外Links，不复制codec writer或判定；第二轮核原SaveIdentity/Technical字段、未取得identity的原Save Task保持、迟到/技术commit与资源释放分轴、原root收尾及重启不复活Task、治理提交Unknown不重存外报告。修正ArtifactRef字段为Namespace/Id/Revision/Sha256（不是Kind/Version），结果Schema从Catalog内WriteBinding唯一descriptor取，不猜CommitId。实际定向文档检查见本版收尾记录；历史0.2.6的“待上游codec”只表示当时状态，不覆盖本版§13.1.8/§18。


本版实际定向检查通过：复用tools/validate_docs.py targets解析，17个本地Markdown链接及全部fragment有效、38处围栏配对；22项qualification公开声明（codec/factory/存储请求/回执/注册/Save/Query/Read）的类型、顺序、nullable和参数与0.2.6-prep正文一致，IM-066 TechnicalCommitReceipt原Identity/字段及查询边界对应。修改前后的19个围栏块LF规范化hash和34处既有64位hash按原顺序完全相等，未重算向量或重审训练/预览/UI/数据库。只写本指导，无产品代码/工程/测试/新脚本/过程报告、其它模块或共享文件修改，无新会话/子代理。本轮没有C#编译/报告codec实际运行、格式/SQL/权限注册、耐久/断电恢复或现场验收；本模块原软件契约欠项关闭，实际未运行门保持，不等待主控内容审核。

以下保持旧版本检查与当时结论，不覆盖本版。

0.2.6-prep（2026-10-12）本轮覆盖整模块批准范围：补§7.1.1–2实际训练/typed配置/顺序/选优/封存与HALCON有效域计数，§8.1.1三语任务流、§8.2.3公开viewport Assembly0.2/ImageFrame生产预览与双STA软件mode，§13.2.1–4完整请求/快照/报告存储、strict codec、输入注册/释放、fence/原identity恢复、来源/标签/审计/保留，§12增量测点及§18全范围结论。原Core/公开scope/Host/规范向量保持；不重算有效S6/Qualification/Binding数值，不新增报告、工程或脚本。

第一轮有限自审沿正常→异常→取消→恢复核新增操作链：修正完整Dataset必须进入Append信封、Read输入必须有query Schema、宏均值/区间不能按普通总整数比校验、授权Read不因Eligibility.Blocked误拒绝、TechnicalCommitReceipt没有独立CommitId。第二轮从缺陷/OCR Host装配和原Owner追溯核：补原ModelBinding/EvaluationPlan请求bytes输入注册/读回（不读私有Core ledger）；验证集候选先封存并绑定完整ModelBinding，Best不误写当前模型；生产同Control/Lifetime/root及原空Update/Return/Retire责任，修正停止信号先于await Show、失败首次Attach不可复用、半开ROI fixture仅转换一次、HWND遮罩与无资源Close；输入注册回执用class满足既有Check<T>约束。两轮仅文档阅读自审，未编译/运行代码。

本轮定向检查复用tools/validate_docs.py的targets解析（只读、不产生脚本/缓存），15个本地Markdown链接及全部实际fragment可解析、38处围栏配对。选定40项viewport/image-frame/storage/authorization公开成员及Contracts namespace/Read-Mutate映射核对一致，15份所需HALCON26.05算子原页存在，本轮定向读模型set/get参数、batch/整集异常训练、get_region_runs及border_holes轮廓语义，其它区域/坐标依据沿原有效研究复用；围栏19块的LF规范化SHA-256及34处既有64位hash按原顺序与修改前逐项相同。检查覆盖本页结构/公开映射及已接收文本保真，不表示C#签名编译、真实codec注册、训练/统计/WPF/数据库耐久/性能或现场验收。唯一剩余上游软件契约门是qualification完整报告codec/耐久引用；其它实际部署/领域值及未运行门见§18。不再等待总控内容复审，本轮在原永久会话收尾。

以下旧版当轮检查与限定接收历史保持，不覆盖本轮结论。

0.2.5-prep（2026-10-11）仅接续Deming消费适用性：§13.1.7核当前六任务、TruthValue/Prediction/EvaluationPlan/TrainingSpec/IntervalQuery/GroupStatistic及Golden/Benchmark构造，没有Agreement/Deming真实调用；Validation为训练划分，Facts为来源/方法核验，计数区间和报告关联均不派发Deming。直接复用qualification 0.2.5-prep §6.4/A.3.1.1已限定接收桥，更新活动上游版本与接收状态，不新增本模块DTO/算法/端点/provider/Host/向量。两轮有限自审分别沿请求→结果和空Host→Facts/Usage接线，结论与边界见§13.1.7；既有C1/C2/S6/U1及A1-Qualification接收保持，本轮适用性说明已主控限定接收。

实际定向检查通过：六种TaskKind、六项输入DTO与两个现有分析构造无Deming/Agreement调用；预定本模块Core/Tests目录确实未创建。12个本地链接/锚点、38处围栏配对一致，活动“Deming上游桥已接收、本模块无当前消费者”口径已同步，旧版本历史记录保留。修改前后全部围栏中的API/源码/算法/向量及全部64位hash逐项相等，未重审或重建已接收向量，未执行C#编译/运行。只写本页，不修改其它模块/共享文件、不创建工程/脚本/子会话，不重核HALCON26.05或AsunImage cv2覆盖。真实DLL/能力/数值运行和物理配对/误差比证据由原消费者Owner验收；本模块真实Adapter、报告codec耐久、客户资格仍另门。

0.2.4-prep（2026-10-11）按本轮授权仅同步0.2.3 A1-Stats S6桥限定指导接收并补已接收qualification Contract0.2的确定消费：§13.1.4–4.1完整Golden/Benchmark请求、Profile/WorkPlan/Recorded来源和执行/录制边界；§13.1.5两个完整无UI Host及本模块局部公开端口实现；§13.1.6完整结果/诊断、原ID取消查询、资源两轴、codec/耐久界限与AQ01–07；§12补对应负载/性能边界，§14新增桥六项定位。model-assets仅定向同步0.3.0-prep/Service0.3的Context/Scope/公开投影、ServiceResult及实际seal文件回执，不扩模型研究或真实训练。C1/C2、U1与S6限定接收保持；本轮Qualification桥正文待主控接收，Deming按原派发边界另候接收/任务，不预造。

第一轮有限自审按正常→异常→恢复：核Golden全案例/Benchmark完整分母、源录制与当前排空，修正FixtureLedger同ID异hash的空返回，SoftwareProbe Drain改为观察原Invoke Task且重复Drain复用原回执；补Factory前预约、CTS登记失败释放、原Task等待超时不移除、Host业务/cleanup两轴、HostCompletion与真正关闭后才Acknowledge。第二轮从空Host装配：核完整公开构造/namespace/12参数Factory、两个Main选择、空Numerics能力不隐藏派发、Clock checked换算/线程计数、Sampler停止后不再采样及原lease单次归还；补source hash精确LF边界，不猜Report.Plan/报告编码，不把Simulation seal或Recorded分析当Production事实。两轮是文档接线自审，夹具源码仍未编译/运行。

实际定向检查通过：11个本地链接/锚点、38处围栏配对及新增Host片段括号嵌套；53处显式公开DTO构造参数数量、Factory12字段、15项选定qualification公开DTO与10项API成员、model-assets Context/wrapper/Seal/文件/资源公开字段一致。两份调用方构造块与上游原文完全相等，按正文规定的LF边界来源hash一致。从独立字段重建11个完整域：Golden QLEP31/QLIP103/QLCS37/QLGP250/QLRQ974 bytes，Benchmark QLBP402/QLBW444/QLBR2071和BEN-ORIGIN1171/BX-EXECUTE1171/BR-ANALYZE1268 bytes，长度及SHA-256均与冻结向量一致；四组nearest-rank分位与50/s吞吐核对一致。原C1/C2 DG-BIND-1逐字段/hex仍270 bytes、SHA-256 `cca3c02d5294638a3041660609742a65b8d4c42fea839a4847b98bca68522efc`，未重审S6旧向量。没有声称运行生产Codec、C# build/Host、真实WPF/HALCON/训练/推理/性能/数据库/现场验收。

仍需真实公开DLL/ports编译与来源/完成屏障/资源实测、报告codec实际注册及耐久/Unknown恢复、客户物理参照/阈值/节拍/权限与用途Owner正式回执；仅阻断依赖的切片。EvidenceSink=null与内存FixtureLedger不代表保存；AQ01–07是未来测试断言。本文为本轮唯一写入文件，未创建工程/脚本/Goal/会话/fork/子代理，未改共享文件、代码、上游指导、原件或AsunImage内部，未向其它会话发消息。

以下保留各旧版本当轮结果和接收状态，不能用于覆盖上面的当前结论。

0.2.3-prep（2026-10-11）仅增A1-Stats S6桥与当前接收状态同步：§6.8移除组CI一概Unsupported，§13.1.1逐字段闭合GroupRatioTask/GroupPairedRatioTask、Policy/Budget/Coverage/Source/数值外层请求及旧query投影限制；§13.1.2.1提供完整小型字段编码、ratio IStatisticsPort桥与配对报告装配两个无UI Host；§13.1.3保存完整结果/诊断/Provenance、区间非可算与原资源两轴，AS01–07为未来软件断言。第一轮局部自审按正常→异常→恢复检查：纠正部分engine在Factory/接纳失败时未被Owner先接管、完整结果过早交还、同步/异步资源证明混同；第二轮从空Host装配核对：完整字段来源/政策/编码、DLL/namespace/构造参数、旧query快照/预算、endpoint与Closure/seed/order校验、非零/cleanup和真实能力门。只复用已冻结S6资料/既有研究，不重审旧C1/C2/U1或qualification未接收片；本轮文档检查结果如下，均不表示C#编译或运行。

实际定向检查通过：10个本地链接/锚点、36处围栏配对，15项上游公开DTO和6项执行/资源成员，夹具helpers来源hash与两个完整请求构造块一致。独立字段编码重建四侧来源、方法/选择/数值/组政策、成员集和两个排序hash，ratioInput/Request=1429/1518 bytes、pairedInput/Request=1990/2080 bytes与原完整hash一致；独立生产seed42 PCG16输出及64字节draw hash一致，有理数区间ratio `[0,107/800]`、paired `[-1/99,1/8]`与冻结结果一致。原C1/C2 270-byte Binding逐字段/hash未变；没有C#编译/Host运行/真实WPF/性能/现场结果。定向链接检查发现model-assets旧v0.2 fragment已因上游修订失效，仅将本页该引用修为原指导入口，不接收其新Service DTO或扩本轮桥范围。C1/C2与U1限定指导接收保持；S6桥本模块正文待主控接收，qualification精确桥/报告codec实际注册及真实算法运行资格保持明确后门。本文是本轮唯一写入文件，不创建工程、脚本、Goal、会话、fork或子代理，不向其它会话发消息。


0.2.1-prep窄修实际定向检查：9个本地链接/锚点、30处代码围栏配对；原270字节Binding逐字段独立复算与hash保持一致。合成原图3字节hash为ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad，原ROI15字节hash为e7a6e349bb0429ee3193889e3a6d9027de0dd148a417328bddca60c3f3d7aeb4；逐项核对Evidence/Binding/Row/Selection构造字段与两个STA入口的预览分支，无C#编译/真实UI声明。已按主控回执同步C1/C2规格接收和A1映射内容接收；§8补EvidencePreviewBinding、精确图/ROI/face/坐标与当前权限、可嵌入View/Show/Clear/Close、原Task/lease/撤权watch/根Owner及选择代次；两个STA Host构造abc像素与独立原ROI并有Presented/Released断言，U03–U05覆盖迟到/撤权/未知清空。复用现有viewport只读边界，未猜其在改新签名，未改产品代码或其它模块。新增接口是本模块U1受控宿主端口，不把规范内容误写为真实viewport/WPF运行已完成。

本文是本轮唯一改动；未写产品代码/测试/tools/共享文件/原件，未创建或派生会话。版本0.2.2-prep沿用已接收v0.2核心算法与Binding规范字节，保留旧StartBorrowed，并补U1公开有界scope、预览值/桥和显式GovernanceBinding；取代未实现v0.1活动API。冻结输入版本及hash、预算完整必填、结构校验/事实核验区别、冻结输出所有权、工程门前置、根Owner/原Task/独立cleanup/移交及多任务分母已经落到正文。

0.2.2-prep窄修完成两轮局部阅读自审：第一轮核对公开scope容量、接收门和清理接线；第二轮核对捕获预约/清理尾额、迟到Open、Show在途时停止信号、自等待、Release→watch顺序及双Host错误两轴。修正Work结果门的Capture启动预约和状态驱动器对清理信号的响应，新增U06/U07未来验收断言；这些断言尚未实现/运行。本版定向检查为9个本地链接/锚点、32处围栏配对、270字节Binding独立字段/hex/hash及3字节图像/15字节ROI hash一致，并核对ReserveBorrowedScope/StartLifetime/Start/CaptureProduced公开签名与伪码入口、HostRun构造及两个Host的cleanup错误保留。未执行C#编译、产品构建、真实WPF/viewport/HALCON、性能或现场验证；U1正文仍待主控接收，C1/C2及A1原接收结论不变。

此前v0.2准备轮实际完成两轮定向阅读自审，以及8个本地Markdown链接/锚点解析、代码围栏配对、旧API名/版本检索；完整270字节Golden从独立字段拼接并与literal hex和SHA-256相等。逐项核对两Host的LabelSet/EvaluationPlan/Budget/Binding构造参数与状态/错误映射；这是文档一致性核对，没有C#编译或运行。没有Git diff/构建/真实UI/现场结果。主控已接收C1/C2六项规格与A1映射内容，270字节Binding独立复核一致；本轮只同步该接收并窄补U1，U1正文及跨文件权威一致性继续由主会话接收；本会话不改入口/进度/登记。

## 17. 参考和可借鉴实现

- 平台权威：`PKG-053_AiGovernance.md`、`DEV-AI-060`、`DEV-AI-063`、`PKG-033_ModelAssets.md`、`PKG-052_Inference.md`、`DEV-GOV-005`、`DEV-GOV-010`。
- 来源审查（2026-10-06）：`H:\docs\40-development\50-ai-review\AI模型与数据治理开发指导.md`，正文版本 2.6，SHA-256 `cd5c1df3e8e2e0763b52742e64abd7fcbeac0030d29c59e088b83be15151a03b`，与 `../../references/project-snapshots/PCBA-AOI/20261006/full-hdocs-inventory/source-manifest.json` 本项一致。仅吸收 §1–4、§8、§10、§14.2 G02/G03 的来源闭包、追加标签/仲裁、统计口径、回归/挑战集、工具链证据和删除影响，分别落入本文 §6、§10、§13；§0.1–0.2、§5 的授权与幂等原则落入 §4/§13.2。已有无副作用 Core、不可变修订、取消/排空、版本回退、资源测量和三语言要求直接复用，不重复冻结。来源的 AOI/REC05/AI02 接口与状态机、部署/Recipe 编排、客户阈值、固定容量、签名 wire/安装配置、HALCON 24.11 事实及项目验收结论均不采纳；不把其许可审批流程用于已授权依赖。该次来源吸收没有扩大当时的 Core；本轮 v0.2 技术修订另见 §16。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_Variation_Model\开发文档.md` 及其参数/训练/结果类：可借鉴“参数对象、创建→训练→准备→执行、显式释放和独立 UI”的组织方式；其 HALCON 句柄、`bool` 错误返回、WinForms 事件和产品参数默认值不能直接作为本模块契约。
- `../../references/project-snapshots/AsunControl/20261004/original/Vision_Aligment2D_ShapeModel\开发文档.md`、`ShapeModelParameters.cs`、`ShapeModelEngine.cs`：可借鉴训练/查找异步入口、`CancellationToken` 和模型元数据分离；其直接持有 `HObject`/句柄、XML 私有存储和控件耦合必须留在视觉算法适配器，不能进入治理核心。

上述资料只读参考；本模块不修改 AsunImage、AsunControl 或历史原件。


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

## 18. 整模块准备覆盖、责任与本轮收尾（2026-10-12）

本轮消费者是缺陷外观训练/评价工具、OCR训练/候选比较工具以及可嵌入只读治理工作台；阶段是**开发指导准备**，不是产品实现。只写本DEVELOPMENT-GUIDE，未写工程/代码/测试/脚本/共享文件/原件，未创建/fork/派生会话、未向其它会话发送消息。已核模块索引原永久会话`01a10307-1306-7981-ac71-918aa7c5007c`及架构IM-048范围；模块内容审核、修复和验证在原会话自行完成，总控只接收状态，不作为本轮收尾等待项。

| 批准范围 | 唯一实施正文、验收和当前设计结论 |
|---|---|
| 独立模块/DLL与事实权威 | §1–2/§11/§13：Core、Adapters、Wpf，真实缺陷/OCR两消费者，版本/工程/依赖/禁止路径；可无UI使用，产品事实和设备命令不下沉。职责/公开API已闭合，C1/C2原规格接收保持 |
| 来源、不可变快照、同源划分与自动建议 | §3/§5/§6.1–3/§13.2.1–3：完整Parent/同源闭包、全部标签观察/selection、group-greedy-v1精确目标/seed/tie/locked与缺口；建议显式采用产生新修订，不改生产参数；C01–06/A12/AD01/02/08 |
| 标签/真值与审批、权限/审计 | §4/§6.3/§13.1/§13.2.3：原human-review/authorization Owner，当前读/写/预览各自受权，Read与Mutate资格分开，实际commit fence不可绕过；A07/AD03/04/08，软件拒绝和恢复已定，真实authority由Host输入 |
| 六种任务评价/拒识/统计 | §6.4–8/§13.1.1–7：完整义务/分母、区域有效域/精确匹配、原串OCR、S6原数值能力与原Owner、Qualification Golden/Benchmark/Recorded；C07–10/AS01–07/AQ01–07。Deming无当前消费者，不新增范围；原向量及已接收装配保持 |
| 实际训练与参数/候选封存 | §7.1.1–2/§13.1/§13.2.1：typed config、精确源/toolchain/DLSample、确定batch尾补齐、Final/Best/early stop、异常整集/GC/OCR组件界限、fresh read/封存/RunEvidence；A10/AD05–07。无隐含exact resume或自动调生产参，软件顺序/拒绝已定 |
| 用途阶段、漂移观察与回退 | §1.2/§7.3/§13.1：只关联外部精确报告和OwnerDecision，当前撤回/适用域/旧闭包核验、不可变新operation；本模块不新造漂移检测算法/自动激活/质量放行。独立观察引用不静默改模型或生产事实 |
| 报告/存储/文件引用/恢复 | §4/§5/§13.2.1–4：Append完整snapshot+result、strict codec/查询schema、技术/治理hash分开、不可变事务/fence/原回执、ReferenceResolver/ReadValidation、DB/文件未知和墓碑；A02–06/11/12、AD01–04/08。本模块自有编码/事务准备闭合，§13.1.8已消费原qualification完整报告/归档与技术回执，实际耐久运行另验 |
| WPF全任务流/三语/生产预览 | §8.1–8.2.3：角色→任务→状态→安全下一步、DevExpress布局/联动/配置草稿隔离、完整三语资源，公开viewport Core0.1/Wpf Assembly0.2/ImageFrame producer、同Control/Lifetime、原Clear→Return→Remove/Retire→Release→再Update；U01–U11。仅1920×1080验证，软件装配与恢复已定 |
| 并发/取消/资源/错误/版本 | §3–5/§4.3.1/§8.2/§9–13：原Root/Task、11槽/迟到接收、一次释放、有限观察/原ID恢复、业务与cleanup两轴、资源Unknown不伪终态、显式旧reader；既有两无UI/两STA Host及反例，不重新审算旧向量 |
| 负载/可复用证据/交付 | §10–13/§15–16：唯一工程和同一测试Host模式、真实负载/冷热/尾延迟/峰值/读写耐久/资源归还、源码研究版本/许可元数据；用最小充分新增断言，不把合成软件或文档结构当现场结果 |

**本模块可决定的软件设计已闭合。** 新增源编码、训练调度/选优、报告读写和viewport生产接线不再留给普通程序员做架构/方法选择。产品值是显式输入（类表、处理、模型/设备参数、限额、物理阈值等），值缺失拒绝确实依赖它的操作，不构成无关Core/文档阻断。这个结论不提升全模块DEV-GOV-010实施准入或运行成熟度；qualification 0.2.6-prep原报告软件契约门已由§13.1.8关闭；以下仅保实际部署/耐久运行与外部领域/用途门，不声明已经实现。

| 未闭门/责任Owner | 精确所需输入/证据与受影响范围 |
|---|---|
| qualification/存储/部署Owner：**实际归档与耐久恢复门** | Report API1公开codec/Factory/格式目录与Storage Save/Query/Read软件设计已经准确消费（§13.1.8），不再作为待发布上游契约。实际DLL编译、StatementCatalog/Formats/Owner注册、当前读写授权/fence、外Object解析/EOF/hash、完整QLAR/原技术receipt读回及断电/Unknown恢复仍未运行。只影响实际外报告耐久/依赖它的用途证明，不阻断本模块自有codec/治理Core；不复制资格schema/判定或给未测运行授予资格 |
| Host/部署Owner：受信注册与实际运行接入 | 精确toolchain/config/初始资产/预处理格式/实际能力、authority context/Action/Resource/Policy及commit fence、StorageScope/StoreGeneration/Schema/SQL/codec注册、资源准入和现场Profile。软件字段/拒绝/流程在正文已定；缺绑定拒绝对应训练/生产写/预览，不按未知值自补，不重核已授权AsunImage/DevExpress依赖 |
| 数据/客户/参照Owner：外部领域与物理门 | 数据授权/脱敏/保留政策、已可观察真值/仲裁、任务taxonomy/误接受拒绝目标、实际分布/OOD/独立组和代表样本。不得编造客户阈值、数据可用或独立性；仅影响实际请求和用途资格 |
| 资格/用途/应用Owner：生产与回退门 | 正式Stage/OwnerDecision/方法适用、模型用途、回退采用、客户节拍/硬件容量、产品Contract/Schema接入、现场验证。训练完成/有报告/封存成功/显示可见均不能替这些决定，无设备/放行权 |

**尚未运行的验证：** C#真实公开DLL/Consumer编译、Core/Adapter/strict codec及新AD/U断言执行、真实WPF/三语/键盘/UIA/DPI/HALCON HWND显示、模型训练/推理/Region/统计能力及Golden/Replay、数据库注册/并发fence/断电耐久/恢复、冷热P50/P95/P99/峰值/长期资源、Shadow/Advice/物理参照/HIL/客户及现场验收，均未在本轮运行。已接收源码/规范字节/旧研究直接复用；文档自审和结构检查只证明本轮指导一致性，不能改写历史测试状态。

本轮以本页正文和§16定向检查结果收尾，不新建审计报告/队列/测试文件；外部门由上述原Owner提供，已批准范围内的本模块内容不再等待总控复审。

