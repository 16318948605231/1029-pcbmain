# IM-066 storage-database 开发指导

> 状态标记：review=`DesignReview/Prep`｜module-ready=`PreparationIncomplete`｜core-ready=`C0, C1`

- 模块 ID：`IM-066`；模块键：`storage-database`
- 唯一实施指导：本文件；技术设计修订：`IM-REVIEW-20261009/storage-database`
- 当前契约版本：`0.3.1-prep`（未发布）；本轮补明启动注册快照、同事务引用epoch接线与全部批准范围的文档准备结论，公开声明及既有编码不变。
- 当前状态：`DesignReview/Prep`；C0、C1 为 `ModuleCoreImplementationReady`（主控已内容接收 DEV-GOV-010 §3.1 六项规格，2026-10-10 同步，仅规格准备）。C1 接收范围仅为 Runtime + 可控 fake 后端 + 托管维护组合 + 双无 UI Host；本轮 A1/A2/A3 的 §6.7/§7.1.4 装配增量已获主控限定内容接收，但 A1/A2/A3 整体仍为 `PreparationIncomplete`，真实 PG/Npgsql、NAS/耐久、工具、性能和生产 IO 门未关闭。不是实现或生产资格声明。
- 运行时：C# / .NET 10；无 UI。模块不引用 WPF、DevExpress、AsunImage 或 HALCON。
- 永久写入 Owner 会话：`01a109b6-49e5-7380-95ca-cbe3ba32b2c8`，已按 [模块索引](../MODULE-INDEX.md) 检索核对。
- 架构：[IM-ARCH-001](../INDEPENDENT-MODULE-ARCHITECTURE.md)；准入：[DEV-GOV-010 §3.1](../../01-governance/DEV-GOV-010_实施级规格唯一标准.md#31-独立模块核心代码开工门)。
- 数据主权：[DEV-PLT-018](../../shared-modules/guidance/02-platform/DEV-PLT-018_数据、报告、归档与数据主权开发指导.md)；[PKG-041](../../shared-modules/packages/PKG-041_Storage.md) 仅作历史映射，不维护第二套活动契约。

本轮受授权冻结可决定的模块工程语义；全部批准范围的内容核对、自审和补缺在本永久原会话完成，结论见§12.1，本轮收尾无需等待总控再次内容复核。既有切片接收状态保持，未测的后端、性能、恢复和现场资格分别保留。产品 Contract/Owner 若与本指导冲突，按用户当前决定→已批准 Contract→本指导→项目规则处理，先修订受影响切片，不让程序员裁决。来源项目的 SQLite 权威、AOI 放行、业务表和验收结论均不迁入。

## Core implementation binding

| 切片 | 唯一工程与命名空间 | 唯一测试/最小宿主 |
|---|---|---|
| C0 纯值分类 | `src/Modules/storage-database/Asun.Modules.StorageDatabase.Contracts/Asun.Modules.StorageDatabase.Contracts.csproj`（`Asun.Platform.StorageDatabase.Contracts`）；`src/Modules/storage-database/Asun.Modules.StorageDatabase.Core/Asun.Modules.StorageDatabase.Core.csproj`（`Asun.Platform.StorageDatabase`） | `tests/Modules/storage-database/Asun.Modules.StorageDatabase.Core.Tests/Asun.Modules.StorageDatabase.Core.Tests.csproj`；§10 的无 UI 调用同时作为测试宿主，不机械增加空工程 |
| C1 运行协调/故障模拟 | `src/Modules/storage-database/Asun.Modules.StorageDatabase.Runtime/Asun.Modules.StorageDatabase.Runtime.csproj`（`Asun.Platform.StorageDatabase.Runtime`） | `tests/Modules/storage-database/Asun.Modules.StorageDatabase.Runtime.Tests/Asun.Modules.StorageDatabase.Runtime.Tests.csproj`；假后端只证明接纳/排空/回查协议 |
| A1 PostgreSQL | `src/Modules/storage-database/Asun.Modules.StorageDatabase.PostgreSql/Asun.Modules.StorageDatabase.PostgreSql.csproj`（`Asun.Platform.StorageDatabase.PostgreSql`） | `tests/Modules/storage-database/Asun.Modules.StorageDatabase.PostgreSql.Tests/Asun.Modules.StorageDatabase.PostgreSql.Tests.csproj`，真实隔离数据库夹具 |
| A2 文件对象/GC | `src/Modules/storage-database/Asun.Modules.StorageDatabase.FileSystem/Asun.Modules.StorageDatabase.FileSystem.csproj`（`Asun.Platform.StorageDatabase.FileSystem`） | `tests/Modules/storage-database/Asun.Modules.StorageDatabase.FileSystem.Tests/Asun.Modules.StorageDatabase.FileSystem.Tests.csproj`，独占临时存储根与进程故障夹具 |
| A3 迁移/备份恢复组合 | 使用 Runtime + A1/A2，不再拆猜测性 DLL | `tests/Modules/storage-database/Asun.Modules.StorageDatabase.Integration.Tests/Asun.Modules.StorageDatabase.Integration.Tests.csproj`；第二宿主为隔离恢复 CLI 夹具 |

上述是精确的 `NewProjectRequired` 落点，不是工程已存在/获准创建的声明。C0 的代码任务仅允许 Contracts、Core、Core.Tests 三个目录；后续切片按表追加本模块范围，禁止机械创建整套空工程。所有工程 target `net10.0`，启用 nullable；Contracts/Core 仅依赖 .NET 基础库，Core→Contracts，Runtime→Core/Contracts，A1/A2→Contracts，消费者只依赖需要的公开包。Npgsql 只进入 A1；文件原生 API 只进入 A2，不向公共 API 泄漏连接、Reader、SDK 句柄、绝对路径或 provider exception。

当前文档任务只写本文件。任何代码任务均禁止其它模块、产品 Shell/Domain/Integration、共享 Contract、`tools/`、参考快照、用户配置及 AsunImage 内部；创建前由主会话绑定可审计仓库/分支或批准代码快照。当前目录无 `.git`，不能声明 HEAD/CI。程序集独立构建、测试和 pack；消费者无需平台 `.slnx` 或隐藏窗口初始化。

## 1. 职责、消费者和非目标

IM-066 提供长寿命数据库数据源、有界连接 scope、技术事务及幂等回查、文件暂存/封口/读取/保持、Schema 迁移、健康/诊断、GC、数据库与文件闭包备份和隔离恢复。PostgreSQL 是数据库服务，Npgsql 是其 .NET 驱动，只有一个数据库后端组合。不另写驱动或通用 SQL helper。

领域 Owner 独占业务 Schema、行含义、校验、结果/配方/模型/权限/复判/统计事实；本模块只拥有技术 operation ledger、对象目录、租约/GC journal、迁移历史及备份目录。各目录不是第二套产品事实。宿主通过已注册领域操作绑定组合，不开放任意 SQL、表/列、文件路径、远端 callback、动态程序集加载或自由查询 DSL。通用条件树、分页总体与导出归 `query`；本模块只提供 Owner 已注册的窄读取和技术回执查询。

两个获批复用消费者按架构计划具体绑定：① `inspection-evidence` 的宿主 Repository 先写文件后提交对象引用；② Replay/Query 工具的宿主只按同一 `ObjectRef` 读取并校验字节。第二个工具只获读权，不能引用第一个宿主的私表、连接、ViewModel 或静态单例。另有隔离恢复 CLI 消费同一管理端口验证闭包，不取得生产切换/设备动作权。

本模块无 UI。原“可选 WPF 运维工具”不构成控件交付承诺；状态和错误由宿主投影，不能为本轮新增窗口或运维页面。DevExpress 25.2.3、1920×1080/三语 UI 验收仅在未来获批宿主页面切片适用。本模块提供稳定错误键及结构化状态，不硬编码面向用户的异常文本；宿主语言资源可动态切换 zh-CN/zh-TW/en-US。示例键 `storage.commit_unknown` 对应“提交结果未确认，按原操作查询。”/“提交結果未確認，依原操作查詢。”/“Commit result unknown. Check the original operation.”。所有视觉退化、弱信号、遮挡与 ROI 算子选择均不适用：此模块把证据视作不透明字节，不能因图像 NG 或不可回放就拒绝合法技术保存或更改质量结果。

### 1A. 新架构适配要点

**架构门禁**：`Asun.Modules.StorageDatabase.Core` 不得引用 `System.Windows.*`、`PresentationFramework`、`DevExpress.*`；§1 已明确"本模块无 UI"，Core 是纯数据存储事务模块。

**Blazor/Web**：存储诊断（连接状态、磁盘使用率、慢查询统计）通过 gRPC/REST 查询；浏览器只展示诊断数据，不直接执行数据库操作。§1 已明确"视觉退化与 ROI 算子选择均不适用"——Web 端不因图像质量问题绕过存储事务。

**AI 存储集成**：`ai-dataset-governance` 的 Golden 数据集版本化存储和 `ai-inference` 的模型制品存储均使用本模块；模型二进制和数据集快照作为对象存储，通过 `ObjectRef`+hash 校验完整性，不经 SQL 直接读写二进制字段。

**HALCON 不适用**：本模块是纯存储事务，不执行视觉算法；HALCON 备选 CI 不涉及本模块。

## 2. 文件对象、引用和耐久

图像、原始 2D/3D、点云、高度场、视频等大体积证据必须在受控硬盘/服务器磁盘/NAS 保存，不写数据库 `bytea`/BLOB。数据库只存对象身份、长度（byte）、SHA-256、媒体/格式版本、技术状态、保持和 Owner 引用。空字节对象在对应格式允许且 `ExpectedBytes=0` 时合法；零字节不是“缺图”的替代。

1. 写入身份固定为 `ObjectKey(StoreId, Generation, TenantId, StorageDomain, ObjectId)`。介质根和 ObjectId 均由受信任宿主/服务产生，业务输入不能拼路径。默认物理去重只在同租户/存储域内进行；跨租户同 hash 不共享可发现性、目录、授权、计费或错误信息。
2. 接纳前校验权限、版本、格式验证器、长度/摘要声明、容量预约和有限预算。实际流式长度/hash 由模块计算，声明仅用于比较；未知长度按 `MaxObjectBytes` 留出有限最坏预约，不能边写边无界扩容。源流必须支持读，不能并发消费，始终归调用方；在真实读取排空前调用方不得关闭/重用它。
3. 独占创建受控同卷 staging，分块写并核长度/hash、格式，flush 到 Profile 声明边界，关闭写句柄后同卷原子发布；同对象已有记录只有完整元数据与字节均匹配才重放，异内容拒绝，不覆盖。文件内容持久、目录项可见及掉电耐久是不同断言；File.Move/Flush 成功不直接证明物理 RPO=0。
4. 封口回执带完整 ObjectRef、Profile 修订和状态。`SealedDurable` 只表示已验证的 Profile 耐久能力，不适用于未验证 NAS。`SealedNotDurable/IntegrityFailed/Unknown` 不允许建立生产引用。查询真实存储与 journal，不以 hash 文件存在冒认原写 operation 完成。
5. 封口后建立发布保持，Owner 在单个数据库事务中写领域事实、技术回执和精确对象引用；提交与 GC 协调必须线性化。保持在引用确认后转交持久引用保护；失联/Unknown 保留，不因临时 TTL 自动放开。数据库与文件没有跨介质原子提交。回滚留下 `OrphanPending`，宽限期和 GC 复核后才删除。
6. 读取同时取得不可复用 lease，返回只读且不可 Seek/Write 的有界 Stream；`Read` 与 `ReadAsync` 都检查范围/累计字节/取消并记录实际读进度，超限明确失败。Metadata 校验不等于已验全内容；整对象 `VerifyAsync` 另读完整长度/hash。恢复与完整性任务不得把仅打开句柄或只读首块作为校验通过。
7. 路径根需独占写 ACL；适配器按可信目录解析，禁止用户绝对路径、UNC 任意根、`..`、重解析点/junction/symlink 逃逸。仅字符串前缀校验不足，须按实际句柄/解析结果核根与对象代；共享可变目录的 TOCTOU 无法排除时拒绝 Profile。跨卷移动不可标原子发布。
8. 已提交引用的文件缺失/损坏返回 `IntegrityFailed` 并保留原回执，阻断该对象用途；不把数据库已提交改写为回滚，不补空文件，不改向“最新”对象。重新采集/再生成由领域 Owner 创建新身份。

## 3. PostgreSQL/Npgsql、事务和池

研究/软件适配基线采用 PostgreSQL 18 官方语义和 Npgsql 10.0.3（固定提交见 §13）；部署的具体服务器小版本、拓扑、凭据、容量和耐久由 Profile 绑定，本轮不升级或安装服务器。SQLite 单机离线/Replay 是后续独立适配，不作为共享生产主库或自动降级；中心故障时宿主按获批离线策略执行，不双主写同一事实。

每个 Runtime 按“Store Profile + 用途 + 凭据代”创建长寿命 `NpgsqlDataSourceBuilder.Build()` 的数据源（线程安全）；分开的生产写、查询、恢复、维护池是有预算的隔离池。Session 是逻辑授权 scope，不长期占连接；每次操作借连接，在一个连接上完成事务/Reader，再真实归还。单 Session 同时只允许一个在途操作，第二个返回 `ResourceBusy`；不同 Session 可并行。不在每请求创建 DataSource，不跨线程共享连接/事务/Reader。用途池、滚动更新新旧实例、监控、备份、运维及服务器保留槽的总和不得超过部署总预算。

冻结 `Pooling=true`、`Multiplexing=false`、`NoResetOnClose=false`、不使用环境 `TransactionScope`/隐式 Enlist、不把普通业务分布到多个库事务。TLS 全验证与 secret reference 由可信 Profile 注入，不降低为明文或信任任意证书。租户角色和 search_path 由注册绑定控制，所有值用位置参数 `$1...`，标识符只能来自可信预编译目录；不接受用户 SQL。批量先采用同事务有界参数化 batch；只有 Owner 显式批准的导入切片可使用 binary COPY，须验证 RLS/约束/错误/回滚；不是默认吞吐捷径。

新技术事务顺序：当前授权→核注册绑定与不可变请求摘要→权威原 operation 回查→同键重放/冲突→在一连接事务内争取唯一 reservation→执行完整领域映射→同事务写结果、operation 回执和引用→commit→真实排空→返回。幂等账本唯一键覆盖 Tenant/Store/Generation/Owner/IdempotencyKey，另对 OperationId 唯一；同键异内容或换 OperationId 拒绝。同键已提交重放不再执行当前业务状态校验或领域写入，但披露前仍核当前访问权。编码与 hash 必须由已注册版本化 codec 重算；客户端自报 hash 不可信。

领域写、技术结果/回执、对象引用，以及 Owner 要求的 Outbox 只能在该权威库同一事务原子提交；Outbox 消息语义、投递租约、外部业务 ACK 和质量放行归各 Owner，不在 IM-066 再建消息系统。外部 HTTP/文件/设备动作不允许在事务绑定内执行。提交前已证明回滚的 `40001`/`40P01` 按显式有限重试表重跑完整事务和依赖决策；`23505` 不能一律重试，先识别幂等唯一键重放或永久业务冲突。commit 已发出后断连、取消、超时不能分类为已回滚；`Unknown` 沿原身份到权威主库回查，不读有延迟副本推断 NotFound，不换键重跑。坏连接隔离/丢弃；客户端 Dispose 不证明服务端事务结论。

业务隔离级别由注册 Binding 显式给出（ReadCommitted/RepeatableRead/Serializable），请求不能自行放宽；默认语义不是整个多语句一致快照。ReadCommitted 下每语句快照不同。跨页固定总体/水位由 Query Owner 管理，不能以 timestamp 或最大 id 伪造稳定快照。事务时间/锁时间在剩余执行 deadline 内；重试间隔、次数、总耗时同时有界。参数改变形成新 Profile 修订，原操作按原修订恢复；旧 codec/结果回读保留到批准退役，不对生产未知事务用新配置重释。

## 4. 多租户、多设备和长期容量

所有入口、operation、对象目录、保持、诊断、缓存、备份清单与恢复目标都带 TenantId/StoreId/Generation，生产作用域还带 Site/Line/Station/Device。身份来自已授权宿主上下文，不从文件名、条码或自报 header 信任；模块 `IStorageAuthority` 逐操作检查，不拥有平台权限事实。不同租户使用相同业务键/hash 必须互不干扰。后台任务也须绑定租户，管理角色不能以“管理员”绕过对象/备份范围。

共享库先冻结显式 tenant 谓词和带 tenant 的关联/唯一键，并用 RLS 作第二道门：运行角色非超级用户、无 BYPASSRLS、非业务表 Owner；迁移角色分离；Owner Schema 对共享表启用 `ENABLE` 与 `FORCE ROW LEVEL SECURITY`，读 USING 与写 WITH CHECK 都覆盖。事务内绑定 tenant 的 `SET LOCAL`/受控 set_config，失败必须 rollback，池归还不能泄漏租户、角色或 search_path。RLS 不覆盖所有表级操作/约束错误，不允许 runtime TRUNCATE/DDL/任意 security-definer 函数；唯一键错误脱敏，不能暴露其它租户记录。未支持此约束的领域 Schema 只阻断该共享部署接入，不阻断纯 Core。

| 负载/变化 | 实施约束 | 可判定反例 |
|---|---|---|
| 单设备到多宿主/热点租户 | 按用途与 Tenant/Owner/Device 分配队列条数/字节、并发额度、最老年龄；调度为显式轮转+配额，生产与回查保留槽不被查询耗尽 | A 租户满队列只拒绝 A，不使 B 无限等待；不静默丢提交事实 |
| 长期事实表 | Owner 按查询条件定义 UTC 时间 range 分区，再决定是否 tenant 子分区；平台不强制每设备一张表/四维全笛卡尔分区 | NULL/越界时间、迟到数据路由按批准规则拒绝或隔离，不能默默改到当前分区 |
| 索引/分页 | Owner 冻结 tenant+实际过滤/稳定排序键及 tie-break 的 B-tree；大范围追加扫描 BRIN 为经测量的可选分支；EXPLAIN、索引大小/写放大/分区 pruning 一同验收 | keyset 相等排序值不漏不重，过滤改变不得复用 cursor；没有查询证据不宣称索引最优 |
| 跨分区幂等 | operation ledger 不随业务时间分区；若以后分区，方案须保持全作用域唯一性。业务 partition unique/PK 含全 partition key，不能替代 ledger | 同幂等键跨月份/迟到分区/设备并发只能一个执行 |
| 分区/索引维护 | 预建有限未来窗口；attach/detach/drop 属带批准 plan 的维护，校验引用/保持/备份并记录 journal。不可任意 drop partition 清理数据 | Legal Hold 或未复制闭包存在时禁止 detach 后物理删除；在线建索引未验证 invalid 状态不能报告完成 |
| 增长/压力 | Profile 记录日行数/对象数/字节分布、保留、分区数、WAL/archive/复制槽积压、dead tuples/autovacuum、磁盘余量/扩容门 | 慢查询长事务阻碍 vacuum 或 WAL 不归档时拒绝非关键负载并报警，不降低耐久 |

唯一性不能由“先 SELECT 再 INSERT”证明；由约束/事务 CAS 保证。分区周期、索引列、保留值属于 Owner 的版本化 Schema/部署 Profile，不由技术模块猜数。运维只执行已注册迁移/维护，不能管理界面修业务行。HA 主从、多 host failover、PgBouncer、跨站复制均按明确 Profile 接入；旧主未被 fencing 前保持 Unknown，不凭连接到新主证明原事务不存在。

## 5. 切片与范围

C0 保持原批准的纯值状态/幂等分类范围，现于 §10 补齐真正可编码契约；本轮整模块审查同时完善 C1/A1/A2/A3，不能用“只做分类”替代存储功能规格。C1 的运行状态机与假后端六项规格已限定接收，代码实施仍需对应授权与可审计基线；假后端不算磁盘、数据库、RPO 或部署资格。A1/A2 分别以真实目标后端证明，A3 组合按相同闭包完成隔离恢复；任何切片不得私自新增领域 DTO/表或改其它模块。

## 6. 公开集成契约（Module API Contract v0.3 的 IO 部分）

以下为本轮确定的设计形状，未发布、未编译；需主会话接收 C1/适配切片后才能实现。C0 只使用其纯值类型，绝不实现下列 IO 接口。代码块是公开声明规格，所有名称在本节或 §10 定义，不是已存在库的可执行调用。

```csharp
using System;
using System.Collections.Immutable;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
namespace Asun.Platform.StorageDatabase.Contracts;

public readonly record struct Sha256(string Hex);
public sealed record VersionRef(string Id, int Revision, Sha256 Hash);
public sealed record StorageScope(
    string TenantId, string SiteId, string LineId, string StationId, string DeviceId);
public sealed record StoreRef(string StoreId, long Generation, VersionRef Profile);
public sealed record CallerRef(string PrincipalId, string AuthorityContextId);
public sealed record CallContext(StorageScope Scope, StoreRef Store, CallerRef Caller,
    TimeSpan ExecutionBudget, TimeSpan WaitBudget);
public sealed record OperationIdentity(StorageScope Scope, string StoreId,
    long StoreGeneration, string OwnerKey, string OperationId,
    string IdempotencyKey, Sha256 PayloadHash);
public sealed record ObjectKey(string StoreId, long Generation, string TenantId,
    string StorageDomain, string ObjectId);
public sealed record ObjectRef(ObjectKey Key, long Bytes, Sha256 Hash,
    string MediaType, VersionRef Format);
public sealed record TaskHandle(string InstanceEpoch, string TaskId);
public sealed record ResourceHandle(string InstanceEpoch, string ResourceId);
public enum PoolPurpose { Production, Query, Recovery, Maintenance }
public enum StorageExecutionState {
    RequestRejected, Accepted, Running, Draining, DrainUnknown,
    Drained, ResourcesReleased, Completed
}
public enum CommitState { Committed, RolledBack, Rejected, Unknown }
public enum FileState {
    SealedDurable, SealedNotDurable, Rejected, Failed,
    Unknown, OrphanPending, IntegrityFailed, Verified
}
public enum StoredOperationState {
    InProgress, Committed, RolledBack, Rejected, Failed,
    Unknown, NotFound, IntegrityFailed, Succeeded
}
public enum MaintenanceKind { Migration, Backup, Restore, VerifyRecovery, Gc, GcPlan }
public enum MaintenanceState {
    Applied, AlreadyCurrent, Complete, RestoredAndVerified, Collected,
    NoEligibleObjects, Blocked, Partial, Failed, Unknown, Planned
}
public enum StorageError {
    None, InvalidInput, UnsupportedVersion, PermissionDenied, Conflict,
    ResourceBusy, CapacityExceeded, Unavailable, IntegrityFailed,
    MigrationBlocked, GcBlocked, NotRestorable, Cancelled, TimedOut,
    CommitUnknown, DrainIncomplete, InstanceMismatch, ResultExpired
}
public sealed record StorageFault(StorageError Code, string DiagnosticKey);
public sealed class StorageInitializationException : Exception {
    public StorageFault Fault { get; }
    public StorageInitializationException(StorageFault fault)
        : base((fault ?? throw new ArgumentNullException(nameof(fault))).DiagnosticKey) {
        Fault = fault;
    }
}
public sealed record TechnicalCommitReceipt(OperationIdentity Identity,
    CommitState State, ImmutableArray<ObjectRef> References,
    VersionRef ResultSchema, ImmutableArray<byte> ResultBytes, DateTimeOffset AtUtc);
public sealed record FileObjectReceipt(OperationIdentity Identity,
    ObjectKey Key, ObjectRef? Object, FileState State, VersionRef DurabilityProfile, DateTimeOffset AtUtc);
public sealed record MaintenanceReceipt(OperationIdentity Identity,
    MaintenanceKind Kind, MaintenanceState State, VersionRef? Artifact,
    long CompletedCount, long SkippedCount, long FailedCount, long UnknownCount,
    DateTimeOffset AtUtc);
public sealed record OperationRecord(OperationIdentity Identity,
    StoredOperationState State, TechnicalCommitReceipt? Commit,
    FileObjectReceipt? File, MaintenanceReceipt? Maintenance, StorageFault? Fault);
public sealed record StorageTaskStatus(TaskHandle? Task, OperationIdentity Identity,
    StorageExecutionState State, OperationRecord? Result, StorageFault? Fault);
public sealed record OperationQueryResult(OperationRecord? Record, StorageFault? Fault);
public sealed record TaskStatusResult(StorageTaskStatus? Status, StorageFault? Fault);
public sealed record OperationQuery(CallContext Context, OperationIdentity Identity);
public sealed record TaskQuery(CallContext Context, TaskHandle Handle);
public sealed record ResourceReleaseRequest(CallContext Context,
    OperationIdentity Identity, ResourceHandle Handle);
public sealed record ResourceQuery(CallContext Context, ResourceHandle Handle);
public enum ResourceState { Open, Draining, DrainUnknown, Released, Unknown }
public sealed record ResourceStatus(ResourceHandle Handle, ResourceState State,
    TaskHandle? ReleaseTask, int? ActiveOperations, StorageFault? Fault);
public sealed record StopRequest(CallContext Context, OperationIdentity Identity,
    string ExpectedInstanceEpoch);
public sealed record SessionRequest(CallContext Context, string OwnerKey, PoolPurpose Purpose);
public sealed record SessionOpenResult(IStorageSession? Session, StorageFault? Fault);
public interface IOwnerStoragePayload { VersionRef Schema { get; } }
public sealed record RegisteredTransactionRequest(CallContext Context,
    OperationIdentity Identity, VersionRef Binding, IOwnerStoragePayload Payload,
    ImmutableArray<ObjectRef> References);
public sealed record RegisteredReadRequest(CallContext Context, VersionRef Binding,
    IOwnerStoragePayload Parameters);
public sealed record OwnerReadResult(VersionRef? Schema, ImmutableArray<byte> Bytes,
    ImmutableArray<ObjectRef> References, StorageFault? Fault);
public sealed record FileObjectRequest(CallContext Context, OperationIdentity Identity,
    ObjectKey Key, string MediaType, VersionRef Format,
    long? ExpectedBytes, Sha256? ExpectedHash);
public sealed record FileReadRequest(CallContext Context, ObjectRef Object,
    long Offset, long Count);
public sealed record FileVerificationRequest(CallContext Context,
    OperationIdentity Identity, ObjectRef Object);
public sealed record RetentionHoldRequest(CallContext Context,
    OperationIdentity Identity, ObjectRef Object, string ReasonKey, TimeSpan Ttl);
public sealed record HoldRenewRequest(CallContext Context, OperationIdentity Identity,
    ResourceHandle Handle, long ExpectedVersion, TimeSpan Ttl);
public sealed record HoldStatus(ResourceStatus Resource, long? Version,
    DateTimeOffset? ExpiresAtUtc);
public sealed record FileReadOpenResult(IFileObjectReadLease? Lease, StorageFault? Fault);
public sealed record RetentionHoldOpenResult(IObjectRetentionLease? Lease, StorageFault? Fault);
public sealed record MigrationRequest(CallContext Context, OperationIdentity Identity,
    VersionRef CurrentSchema, VersionRef Plan);
public sealed record BackupRequest(CallContext Context, OperationIdentity Identity,
    VersionRef BackupProfile, VersionRef OwnerReferenceCatalog);
public sealed record RecoveryRequest(CallContext Context, OperationIdentity Identity,
    VersionRef BackupClosure, VersionRef RestorePoint, VersionRef IsolatedTarget);
public sealed record GcPlanRequest(CallContext Context, OperationIdentity Identity,
    VersionRef RetentionPlan, VersionRef OwnerReferenceCatalog, int MaxObjects);
public sealed record GcPlanReceipt(VersionRef? Plan, long CandidateCount, long CandidateBytes,
    StorageFault? Fault);
public sealed record GcRequest(CallContext Context, OperationIdentity Identity,
    VersionRef Plan, int MaxObjects);
public abstract record MaintenanceResumeInput;
public sealed record MigrationResumeInput(MigrationRequest Request) : MaintenanceResumeInput;
public sealed record BackupResumeInput(BackupRequest Request) : MaintenanceResumeInput;
public sealed record GcResumeInput(GcRequest Request) : MaintenanceResumeInput;
public sealed record RecoveryResumeInput(RecoveryRequest Request, bool VerifyOnly) : MaintenanceResumeInput;
public sealed record MaintenanceResumeRequest(CallContext Context, OperationIdentity Identity,
    StorageAssetLink Journal, int ExpectedAttempt, MaintenanceResumeInput Input);
public enum HealthState { Healthy, Degraded, Unavailable, Unknown }
public sealed record HealthRequest(CallContext Context);
public sealed record StorageHealth(HealthState State, VersionRef Profile,
    long? FreeBytes, int ActiveOperations, long UnknownOperations,
    DateTimeOffset AtUtc, StorageFault? Fault);
public sealed record DiagnosticCursor(string InstanceEpoch, long Sequence);
public sealed record DiagnosticQuery(CallContext Context,
    DiagnosticCursor? After, OperationIdentity? Identity, int MaxEntries);
public sealed record DiagnosticEntry(long Sequence, OperationIdentity? Identity,
    StorageExecutionState State, string DiagnosticKey, DateTimeOffset AtUtc,
    long ElapsedMilliseconds);
public sealed record DiagnosticPage(DiagnosticCursor Next, bool GapDetected,
    ImmutableArray<DiagnosticEntry> Entries, StorageFault? Fault);
public sealed record StorageAccessCheck(CallContext Context, string Capability,
    string OwnerKey, ObjectKey? Object);
public sealed record StorageAccessDecision(bool Allowed, StorageFault? Fault);
public interface IStorageAuthority {
    ValueTask<StorageAccessDecision> AuthorizeAsync(
        StorageAccessCheck request, CancellationToken cancellationToken);
}
public sealed record RuntimeConfiguration(string RuntimeId, StoreRef Store, CallContext ControlContext,
    VersionRef RelationalProfile, ImmutableArray<VersionRef> FileProfiles,
    VersionRef OwnerBindingCatalog, VersionRef ReferenceCoordinator);
public interface IStorageRuntimeFactory {
    ValueTask<IStorageDatabase> CreateAsync(RuntimeConfiguration configuration,
        IStorageAuthority authority, CancellationToken cancellationToken);
}
public interface IStorageDatabase : IAsyncDisposable {
    string InstanceEpoch { get; }
    IFileObjectStore FileObjects { get; }
    IStorageDiagnostics Diagnostics { get; }
    IStorageMaintenanceReader Maintenance { get; }
    ValueTask<SessionOpenResult> OpenSessionAsync(SessionRequest request, CancellationToken ct);
    ValueTask<OperationQueryResult> QueryOperationAsync(OperationQuery request, CancellationToken ct);
    ValueTask<TaskStatusResult> GetTaskStatusAsync(TaskQuery request, CancellationToken ct);
    ValueTask<StorageTaskStatus> StopAsync(StopRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> MigrateAsync(MigrationRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> CreateBackupClosureAsync(BackupRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> RestoreIsolatedAsync(RecoveryRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> VerifyRecoveryAsync(RecoveryRequest request, CancellationToken ct);
    ValueTask<GcPlanReceipt> PlanOrphanCollectionAsync(GcPlanRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> CollectEligibleOrphansAsync(GcRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> ResumeMaintenanceAsync(MaintenanceResumeRequest request, CancellationToken ct);
    ValueTask<StorageHealth> CheckHealthAsync(HealthRequest request, CancellationToken ct);
}
public interface IStorageSession : IAsyncDisposable {
    ResourceHandle Handle { get; }
    ValueTask<OwnerReadResult> ReadAsync(RegisteredReadRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> ExecuteTransactionAsync(RegisteredTransactionRequest request, CancellationToken ct);
    ValueTask<ResourceStatus> ReleaseAsync(ResourceReleaseRequest request, CancellationToken ct);
}
public interface IFileObjectStore {
    ValueTask<StorageTaskStatus> StageAndSealFileAsync(FileObjectRequest request, Stream source, CancellationToken ct);
    ValueTask<FileReadOpenResult> OpenReadAsync(FileReadRequest request, CancellationToken ct);
    ValueTask<StorageTaskStatus> VerifyAsync(FileVerificationRequest request, CancellationToken ct);
    ValueTask<RetentionHoldOpenResult> AcquireRetentionHoldAsync(RetentionHoldRequest request, CancellationToken ct);
}
public interface IFileObjectReadLease : IAsyncDisposable {
    ResourceHandle Handle { get; }
    ObjectRef Metadata { get; }
    Stream Content { get; }
    ValueTask<ResourceStatus> ReleaseAsync(ResourceReleaseRequest request, CancellationToken ct);
}
public interface IObjectRetentionLease : IAsyncDisposable {
    ResourceHandle Handle { get; }
    ValueTask<HoldStatus> GetStatusAsync(ResourceQuery request, CancellationToken ct);
    ValueTask<HoldStatus> RenewAsync(HoldRenewRequest request, CancellationToken ct);
    ValueTask<ResourceStatus> ReleaseAsync(ResourceReleaseRequest request, CancellationToken ct);
}
public interface IStorageDiagnostics {
    ValueTask<ResourceStatus> GetResourceStatusAsync(ResourceQuery request, CancellationToken ct);
    ValueTask<DiagnosticPage> ReadAsync(DiagnosticQuery request, CancellationToken ct);
}
```

### 6.1 字段、有效域和注册

所有 ID 是非空、大小写敏感、不含控制字符的 opaque 值，不做 trim/大小写折叠，不用作路径；最大 UTF-8 字节数由有限 `MaxIdBytes` 明示并在分配前检查。Site/Line/Station/Device 对生产 Session 必填；维护作用域用宿主注册的维护身份，不接受空串当全站。Generation>0，VersionRef Revision>0、Id 非空、Hash 为严格 64 个小写十六进制 SHA-256。所有 enum 未定义值、default ImmutableArray、null 载荷、NaN/无限/溢出均拒绝。允许的空数组只在明确无引用/无结果字节时使用 `ImmutableArray.Empty`。

字节长度/计数用checked Int64，非负；Offset/Count非负且checked Offset+Count≤Object.Bytes，Count=0合法，不误报完整验证。普通业务对象列表不得重复Key或跨tenant/store/generation；相同Key描述差异为冲突，完整cluster维护例外仅按§6.4验权。CallContext Scope/Store须与operation、Session、Object和Profile一致。ExecutionBudget/WaitBudget有限正TimeSpan，WaitBudget≤ExecutionBudget≤Profile.Runtime.MaxOperationTime；接纳后单调deadline固定，等待取消/预算不刷新。UTC只审计，不用墙钟回拨延长租约；lease有效boot/epoch由协调者保证，跨重启旧Handle无效。

Catalog 在创建时显式注入/绑定 hash，禁止全局静态注册和运行时请求注册。领域 Binding 目录精确记录 OwnerKey、Schema/codec 修订、唯一 CLR payload type、参数化语句目录、作用域/用途、结果 codec、期望影响行数、隔离级别、超时/重试、对象引用提取器和权限键。只接受 exact registered payload type，由注册 codec 深拷贝为不可变工作值并重算摘要（canonical 编码的选择归该 Owner，不重算历史身份）；不持有可变调用对象。事务绑定加载受信任域适配包，不能接受请求 delegate。领域事务映射只能使用本次授权的数据库事务；其它 IO/外部调用、越界行数或更改其它 Owner 表使绑定验收失败。输入/结果 codec 不得有 IO；格式 validator 可读取模块借出的有界只读 staging/对象流，不能打开其它资源或执行外部调用。Query Owner 的窄读取同样只执行已注册映射，既不新增通用查询 DSL，也不将数据库私有类型穿透本 API。

请求摘要绑定版本化域标记、Scope/Store/Generation/Owner、operation kind、Binding/Plan/Profile 修订、typed payload 与精确对象集合（按 Key 确定性排序）；等待预算、当前授权上下文和审计时间不进入历史语义摘要。PayloadHash 名称表示这个完整语义摘要，不只是 payload 字节。各 codec 在注册包提供 golden bytes/hash；缺少 codec 只阻断该绑定，不由技术模块猜 Protobuf/JCS。公开结果字节只按 ResultSchema 解码，有界且不可变；不是任意 SQL/序列化查询入口。对象/回执/保留状态不是权限凭据。

OperationRecord为严格tagged union：技术事务只填Commit，文件写/验证只填File，迁移/备份/GC/恢复/GC计划只填Maintenance，其余载荷null；回执完整Identity必须等于Record.Identity。未出回执的InProgress/Unknown/NotFound允许全null，不能填两种；Committed/Succeeded必有对应回执，NotFound无载荷且仅权威查无记录。Commit四状态映射同名StoredOperationState；File.SealedDurable/Verified→Succeeded，SealedNotDurable/Failed/OrphanPending→Failed，Rejected→Rejected，Unknown→Unknown，IntegrityFailed→IntegrityFailed。维护成功配对唯一：Migration+Applied/AlreadyCurrent、Backup+Complete、Restore/VerifyRecovery+RestoredAndVerified、Gc+Collected/NoEligibleObjects、GcPlan+Planned，均→Succeeded；各Kind的Blocked/Partial/Failed→Failed，Unknown→Unknown，错配成功State为InvalidInput。Committed/Succeeded/InProgress/NotFound的Fault=null，RolledBack/Rejected/Failed/Unknown/IntegrityFailed须非None Fault。不把Succeeded称业务PASS或计划生成称已删除。等待取消/超时的外层Fault与原事实分开，不据外层Fault改原回执；DiagnosticKey按§6.5封闭目录。

完成计数均非负，Partial/Unknown 不能称全成功；维护成功或已写 effect intent 的回执必须按§6.4返回 Artifact，指向不可变计划/逐项 journal/闭包验证记录，不能只靠合计数恢复。副作用前已拒绝且未形成资产允许 Artifact=null，不能伪造快照。事务 ResultBytes≤MaxResultBytes，C0 不复制/解析 ResultBytes；无业务结果的失败回执使用已注册 ResultSchema 和 Empty 字节，不能伪造类型。FileObjectReceipt.Key 始终回显；SealedDurable/SealedNotDurable/Verified/OrphanPending 必须有完整 Object，其 Key 与回显 Key 相同。其它状态 Object 可为 null；若非 null 仅保留既有描述供诊断，不能据此宣称新校验成功。未发布不得造零长度或零摘要。Verified 只表示本次内容验证通过，不提升介质耐久；只有写封口的 SealedDurable 才是持久引用前置。

OwnerReadResult 成功为 Schema 非 null、Bytes/References 非 default 且在 Profile 上限内、Fault=null；零行也由绑定的结果 codec 编码，不用 null Schema 表示空集。失败为 Schema=null、Bytes/References=Empty、Fault 非 null；不交付半页或失败前读到的载荷。成功引用集合仍须同 scope/store/generation，不授写入或跨页总体权。MaintenanceReceipt.Artifact指向§6.4的MaintenanceSnapshotV1；由其Plan/Journal/Closure/RestorePoint/Recovery引用读精确快照，不能靠hash或宿主访问私有journal代替。

所有 OpenResult 恰为成功资源非 null且 Fault=null，或资源 null且 Fault 非 null；QueryOperationAsync/GetTaskStatusAsync 的 lookup wrapper 同样二选一，权限拒绝、InstanceMismatch、ResultExpired 和读后端不可用返回外层 Fault，不伪造 operation/Task 的失败状态、身份或 NotFound。GC 计划失败 Plan=null，不编假 hash；诊断失败 Entries=Empty/Fault 非 null，Next 回显有效本实例 cursor 或 sequence=0，不泄未授权日志。Health.FreeBytes=null 表示未取得磁盘观测，不以 0 假低水位；非 Healthy 用 Fault 说明。

ResourceStatus.ActiveOperations 已知时非负；查询失败、InstanceMismatch、ResultExpired 或观察不可确定时 Resource.State=Unknown、ActiveOperations=null、Fault 非 null，不能以计数 0 推导 Released。Released 只能在实际释放后报告，且 ActiveOperations=0。Open/Draining/DrainUnknown 不等于释放，DrainUnknown 须含 DrainIncomplete。HoldStatus 的当前 Version/ExpiresAtUtc 只有已确认时给值（Version>0、UTC offset=0）；不能取得当前状态时均为 null，不以 0/最早日期替代。Renew 是实例内按原 identity/ExpectedVersion 幂等的 CAS；同身份同参数重放既有结果，异参数 Conflict，旧版本不能 ABA 续约。响应丢失或取消可能已有续约事实，沿同 Handle 的 GetStatusAsync 核当前版本，不能盲改 ExpectedVersion 重跑；跨 epoch 只返回 InstanceMismatch。

### 6.2 生命周期、取消、事件和资源

首次接纳分配 TaskHandle（InstanceEpoch+TaskId）并记录 operation identity。未接纳走 `RequestRejected`，Task/Result=null、Fault 非 null，不建任务/连接/文件。已接纳的快照 Task 非 null且 Identity 恒等于该任务原身份，走 `Accepted→Running→Draining→Drained→ResourcesReleased→Completed`，失败/取消也排空；DrainUnknown 是 Draining 的未确认观察，不是完成状态。正常方法等待至 Completed；WaitBudget 到期或接纳后 ct 触发时返回原任务当前非终态快照，不遗忘任务。运行协调者继续持有该 Task、连接/文件/Stream 借用和额度；原 Task 从 GetTaskStatusAsync 可查，不能由 Session.Release 或 UI 关闭删除。ExecutionBudget 到期启动合作取消，commit 已发送则结果 Unknown，不能硬中止后称回滚。停止的是该操作接纳路径，单请求取消不关闭整个 Runtime。

已知数据库提交/文件发布是存储事实，真实资源排空是执行事实，两者独立：IO 未排空时可在只读 OperationRecord 看到原事实，StorageTaskStatus 仍非终态；只有 Completed 且所需回执有效才报告本次调用完成。迟到 commit/封口结果必须写回原 journal/operation 以便恢复，绝不能“丢弃迟到结果”而失去事务事实。未知提交在实际本地资源归还后可以 Completed+Unknown，表示此次执行结束且提交结论未决；之后原身份 QueryOperationAsync 只读权威事实。对账执行者独立追加证据，不由Query产生写入，不伪造旧执行被取消或再次执行。

QueryOperationAsync 属 Runtime 而非 Session；Session 释放、重启新实例、断线后仍可沿原 operation 查询。它只读权威 ledger/journal，允许只读事务但不能发起新变更/上传或清理；NotFound 不证明旧写者未提交，只有权威主库、足够旧记录覆盖期、原写者已 fenced/结局可证明时才允许同身份重试。记录过保证期返回 ResultExpired/Unknown，禁止复用旧 key。恢复/回查连接使用 Recovery 保留池，Stop 期间只允许现有任务状态、释放、必要对账；不把普通新业务包装为回查。

StopAsync 针对 InstanceEpoch 唯一停止任务；首次有效请求原子关新 Session/新工作接纳，同原 identity 重放同 handle，异 identity 返回 Conflict 与既有停止 handle，不创建第二任务。停止等所有在途工作、Reader、写/读/保持 lease 和模块自有池/缓冲真实释放；每个 lease 须调用方释放，逾期仅报警/非终态，不能强制回收正在使用的 Stream。Session.Release 禁止新工作，并等其工作排空；ReadLease.Release 等活动读结束且之后读抛 ObjectDisposedException；Hold.Release 仅撤销自身临时保持，不取消持久 Owner/备份保护。相同 ResourceHandle 重复 release 幂等，首次 ReleaseOperation 固定；不同 operation 不能另起释放。Resource/Task handle 都是实例资源标识，不是耐久业务回执。

DisposeAsync 不带人为超时，它启动/复用原释放并等待实际完成；Stop 已开始时复用其任务。不得实现“提前调用 Dispose 一律拒绝而丢资源”的旁路，也不用 Task.WaitAsync 超时代替释放。宿主需有界等待时先显式 Stop/Release，再查原 handle；ResourcesReleased/Released 后 Dispose 立即完成。进程被强制结束后旧实例 handle 返回 InstanceMismatch，不能伪报 Released；新实例以耐久 operation/journal 恢复，对物理文件/数据库回查，不续跑旧设备任务。已经 Dispose 的 Runtime 不再查实例诊断，耐久业务查询由新 Runtime 承担。

OpenSession/OpenRead/AcquireRetentionHold/Renew/ReadAsync/PlanOrphanCollection 和 lookup/Health/Diagnostics 不返回执行 TaskHandle，不能采用“取消等待后后台继续交付资源”的规则。其 ct/ExecutionBudget 控制合作取消；接纳后等待真实 IO/授权结束，成功资源交付与取消观察在同一协调边界线性化。取消先胜出就回收本次创建的 lease/流/额度，再返回 Cancelled/TimedOut Fault 或抛 OperationCanceledException（ct）；成功先胜出则返回完整资源，调用方负责 Release，不同时报取消。两者之间无无主资源窗口。预算并不强制中止不配合的 IO，deadline 后如仍在清理方法尚未返回，Host 必须保留原 Task，不能以外部 WaitAsync 代替清理；唯一外层进程超时只能判未完成。查询 ct 取消同样等待查询资源释放；它不取消原业务 operation。OpenSession 是本地逻辑 scope，不建连接。

Stop 的 ExpectedInstanceEpoch 必须等于公开 InstanceEpoch；只有受信任 Runtime 控制主体获 storage.runtime_stop 才能关闭整实例，普通 tenant 只能 release 自己的资源。Stop 的 Completed 不需要 OperationRecord，Result=null/Fault=null 表示所有实例资源已释放；Stop 是实例控制，不写耐久业务 ledger。ReleaseTask 供 ResourceQuery 与 GetTaskStatus 查，Completed 的释放任务也 Result=null；查询口不为释放伪造文件/数据库回执。Dispose 启动的无参 release/stop 由 Runtime 生成固定实例控制身份并复用已有任务，同一资源只能一个释放任务；随后显式 Release/Stop 若身份不同得到 Conflict+既有 handle，不创建第二任务。

Stop 身份冲突返回既有停止任务的原 Task/Identity/State/Result，加 Conflict 的外层 Fault；不能回显新请求 Identity 冒充该任务。未接纳的其它请求才使用 RequestRejected/Task=null。释放身份冲突同理只回既有 Resource/ReleaseTask 状态并带 Fault。无参 Dispose 是持有实例/资源的受信任 Host 生命周期动作，继续清理已接纳借用，不借此执行新业务或取得管理数据；显式 Stop 仍独立核控制权限。

运行观察使用拉取端口，不提供 callback/event 订阅；因此无需猜线程/重入/解绑语义。Diagnostics 的环形日志是有界投影，序列在实例内递增，容量满丢最旧并报 GapDetected；task/resource 当前状态独立保存。读取者不能跨 epoch 拼日志。完成 task/resource 的 tombstone 按有限 Profile 保留，过期明确 ResultExpired；未排空记录不淘汰，满时拒绝新任务。日志不含 SQL、连接串、密钥、绝对路径、原始图像、客户私有载荷；诊断丢项不改变 operation 事实。所有状态/诊断读取仍按 caller tenant/权限过滤。

资源 Owner 表：Runtime 拥有任务、用途 DataSource 与额度；单操作 scope 拥有连接/transaction/command/reader/写流/hash器及暂存；调用方拥有上传源流；读 lease 拥有返回的 Stream 与保持；协调者拥有临时 hold 和 fence；领域 Owner 拥有持久引用，备份目录拥有闭包保持。成功、取消、异常、断线、关闭均按同一顺序释放，未结束的资源不得归还池。

### 6.3 托管运行注入契约

以下声明仍位于 `Asun.Platform.StorageDatabase.Contracts`，引用§6的using。具体工厂 `Asun.Platform.StorageDatabase.Runtime.StorageRuntimeFactory` 的公开构造器冻结为 `StorageRuntimeFactory(StorageRuntimeDependencies dependencies, StorageFactoryOptions options)`，实现已有 `IStorageRuntimeFactory.CreateAsync`；不能通过静态定位器补依赖。声明中的 codec/resolver/backend 是受信任 Host 在启动前提供的实例，绝不是请求携带的 delegate 或动态加载器。

```csharp
public sealed record StorageFactoryOptions(TimeSpan ResolutionBudget);
public sealed record StorageInputLimits(int MaxIdBytes, int MaxPayloadBytes,
    int MaxResultBytes, int MaxReferences, int MaxBatchRows, long MaxBatchBytes,
    int MaxCatalogEntries, int MaxCatalogBytes);
public sealed record StorageRuntimeLimits(int MaxQueuedItems, long MaxQueuedBytes,
    int MaxActiveTasks, int MaxOpenResources, int MaxDiagnosticEntries,
    int MaxDiagnosticPageEntries, int MaxTombstones, long MaxTombstoneBytes,
    TimeSpan StartupBudget, TimeSpan MaxOperationTime, TimeSpan QueueAgeLimit,
    TimeSpan OperationRetention, TimeSpan TombstoneRetention);
public sealed record StorageQuota(StorageScope Scope, string OwnerKey,
    int MaxQueuedItems, long MaxQueuedBytes, int MaxConcurrentOperations);
public sealed record StoragePoolProfile(PoolPurpose Purpose, VersionRef Credential,
    int MinPoolSize, int MaxPoolSize, int OpenTimeoutSeconds, int CommandTimeoutSeconds,
    int ConnectionIdleLifetimeSeconds, int ConnectionPruningIntervalSeconds,
    int CancellationTimeoutMilliseconds);
public sealed record StorageRelationalProfile(VersionRef Version,
    VersionRef Endpoint, VersionRef TlsPolicy, VersionRef AuthorityTopology,
    VersionRef TechnicalSchema, int PostgreSqlMajor, int TotalConnectionBudget,
    ImmutableArray<StoragePoolProfile> Pools);
public enum FileDurability { Unverified, VerifiedDurable }
public sealed record StorageFileProfile(VersionRef Version, string StorageDomain,
    VersionRef Root, VersionRef AccessPolicy, FileDurability Durability,
    long MaxObjectBytes, int ChunkBytes, int MaxConcurrentWriters, long MaxReadBytes,
    long LowDiskWatermarkBytes, long ReserveOverheadBytes);
public sealed record StorageMaintenanceLimits(int MaxResumeAttempts, int MaxPlanObjects, long MaxPlanBytes,
    int MaxClosureItems, long MaxClosureBytes, int MaxAssetPageEntries,
    int MaxAssetPageBytes, long MaxAssetBytes, long MaxJournalBytes,
    TimeSpan OrphanGracePeriod, TimeSpan MinLeaseTtl, TimeSpan MaxLeaseTtl,
    TimeSpan PlanRetention, TimeSpan BackupBudget, TimeSpan RecoveryBudget,
    long MaxWalBytes, long MaxArchiveBytes, long MaxReplicationSlotBytes,
    TimeSpan? RpoTarget, TimeSpan? RtoTarget);
public sealed record StorageRuntimeProfile(VersionRef Version, StorageInputLimits Input,
    StorageRuntimeLimits Runtime, StorageMaintenanceLimits Maintenance,
    ImmutableArray<StorageQuota> Quotas);
public enum StorageBindingKind { Transaction, Read }
public enum StorageIsolation { ReadCommitted, RepeatableRead, Serializable }
public sealed record StorageBindingDescriptor(VersionRef Version, string OwnerKey,
    StorageBindingKind Kind, VersionRef InputSchema, VersionRef InputCodec,
    VersionRef ResultSchema, VersionRef ResultCodec, VersionRef StatementCatalog,
    string PermissionKey, PoolPurpose Purpose, StorageIsolation Isolation,
    int MinAffectedRows, int MaxAffectedRows, int MaxCommands, int MaxRetries,
    TimeSpan RetryDelay, TimeSpan ServerLockTimeout, TimeSpan ServerStatementTimeout,
    bool AllowEmptyBatch);
public interface IStoragePayloadCodec {
    VersionRef Version { get; }
    VersionRef Schema { get; }
    Type PayloadType { get; }
    ImmutableArray<byte> Encode(IOwnerStoragePayload payload, int maxBytes);
    ImmutableArray<ObjectRef> GetReferences(ImmutableArray<byte> canonicalBytes, int maxReferences);
}
public interface IStorageResultCodec {
    VersionRef Version { get; }
    VersionRef Schema { get; }
    void Validate(ImmutableArray<byte> resultBytes, int maxBytes);
}
public interface IStorageObjectFormatValidator {
    VersionRef Format { get; }
    ValueTask ValidateAsync(Stream boundedReadStream, long bytes,
        CancellationToken cancellationToken);
}
public sealed record StorageBindingCatalog(VersionRef Version,
    ImmutableArray<StorageBindingDescriptor> Bindings,
    ImmutableArray<IStoragePayloadCodec> Codecs,
    ImmutableArray<IStorageResultCodec> ResultCodecs);
public sealed record StorageOwnerRegistration(string OwnerKey,
    ImmutableArray<StorageScope> Scopes, ImmutableArray<StoreRef> Stores,
    VersionRef ReferenceResolver, VersionRef ReadValidation);
public sealed record StorageReferenceCatalog(VersionRef Version, string AuthorityId,
    ImmutableArray<StorageOwnerRegistration> Owners);
public sealed record OwnerReferenceSnapshotRequest(CallContext Context,
    StorageOwnerRegistration Owner, VersionRef Catalog,
    StorageCoordinationToken Barrier, int MaxEntries, int MaxBytes);
public sealed record OwnerReferenceEntry(long Sequence, string EntityId,
    VersionRef EntityVersion, ObjectRef Object);
public sealed record OwnerReferencePage(string SnapshotId, long ReferenceEpoch,
    ImmutableArray<OwnerReferenceEntry> Entries, long? NextSequence,
    bool Complete, StorageFault? Fault);
public interface IStorageOwnerReferenceSnapshot : IAsyncDisposable {
    string SnapshotId { get; }
    long ReferenceEpoch { get; }
    ValueTask<OwnerReferencePage> ReadAsync(long nextSequence, CancellationToken ct);
}
public sealed record OwnerReferenceSnapshotResult(IStorageOwnerReferenceSnapshot? Snapshot,
    StorageFault? Fault);
public interface IStorageOwnerReferenceResolver {
    VersionRef Version { get; }
    ValueTask<OwnerReferenceSnapshotResult> OpenAsync(OwnerReferenceSnapshotRequest request,
        CancellationToken ct);
}
public sealed record ResolvedStorageConfiguration(StorageRuntimeProfile Profile,
    StorageRelationalProfile Relational, ImmutableArray<StorageFileProfile> Files,
    StorageBindingCatalog Bindings, StorageReferenceCatalog References,
    ImmutableArray<IStorageOwnerReferenceResolver> ReferenceResolvers,
    ImmutableArray<StorageBackupProfile> Backups,
    ImmutableArray<StorageIsolatedTargetProfile> IsolatedTargets,
    ImmutableArray<IStorageObjectFormatValidator> FormatValidators,
    ImmutableArray<StorageRetentionPlan> RetentionPlans);
public interface IStorageConfigurationResolver {
    ValueTask<ResolvedStorageConfiguration> ResolveAsync(RuntimeConfiguration configuration,
        CancellationToken cancellationToken);
}
public interface IStorageClock {
    long GetTimestamp();
    TimeSpan GetElapsedTime(long startTimestamp);
    DateTimeOffset GetUtcNow();
    ValueTask DelayAsync(TimeSpan delay, CancellationToken cancellationToken);
}
public enum StorageBarrierPoint {
    BeforeAdmission, AfterAdmission, BeforeBackend, AfterBackend,
    BeforeResourceRelease, AfterResourceRelease
}
public interface IStorageExecutionBarrier {
    ValueTask ReachAsync(StorageBarrierPoint point, OperationIdentity identity,
        CancellationToken cancellationToken);
}
public sealed record BackendExecution(string InstanceEpoch, string WorkId,
    TimeSpan RemainingBudget, StorageCoordinationToken? WriterToken, int Attempt);
public sealed record PreparedStorageTransaction(CallContext Context,
    OperationIdentity Identity, StorageBindingDescriptor Binding,
    ImmutableArray<byte> CanonicalPayload, ImmutableArray<ObjectRef> References,
    StorageCoordinationToken PublicationToken);
public sealed record PreparedStorageRead(CallContext Context,
    StorageBindingDescriptor Binding, ImmutableArray<byte> CanonicalParameters);
public sealed record BackendCommitResult(TechnicalCommitReceipt? Receipt, StorageFault? Fault);
public sealed record BackendFileResult(FileObjectReceipt? Receipt, StorageFault? Fault);
public enum StorageOperationKind {
    Transaction = 1, Stage = 2, Verify = 3, Hold = 4, Renew = 5,
    Migration = 6, Backup = 7, Restore = 8, VerifyRecovery = 9, GcPlan = 10, Gc = 11
}
public sealed record StorageOperationRegistration(OperationIdentity Identity,
    StorageOperationKind Kind, VersionRef RuntimeProfile, VersionRef SemanticVersion);
public sealed record StorageOperationRouteResult(StorageOperationRegistration? Registration,
    bool Created, StorageFault? Fault);
public sealed record StorageOperationEvidence(OperationIdentity Identity, long Revision,
    OperationRecord Record, StorageAssetLink? Journal, StorageAssetLink? Maintenance,
    string WriterEpoch, long WriterFence, int Attempt);
public sealed record StorageEvidenceAppendRequest(StorageOperationRegistration Registration,
    long ExpectedRevision, StorageOperationEvidence Evidence,
    StorageCoordinationToken WriterToken);
public sealed record StorageEvidenceResult(StorageOperationEvidence? Evidence, StorageFault? Fault);
public sealed record BackendResumeAdmissionRequest(MaintenanceResumeRequest Request,
    StorageOperationRegistration Registration, StorageCoordinationToken WriterToken);
public sealed record BackendResumeAdmissionResult(int? Attempt, bool Created, StorageFault? Fault);
public interface IStorageDatabaseBackend : IAsyncDisposable {
    ValueTask<StorageOperationRouteResult> RegisterAsync(StorageOperationRegistration registration,
        StorageCoordinationToken writerToken, CancellationToken cancellationToken);
    ValueTask<StorageOperationRouteResult> ReadRouteAsync(OperationQuery request,
        CancellationToken cancellationToken);
    ValueTask<StorageEvidenceResult> AppendEvidenceAsync(StorageEvidenceAppendRequest request,
        CancellationToken cancellationToken);
    ValueTask<StorageEvidenceResult> ReadEvidenceAsync(OperationQuery request,
        CancellationToken cancellationToken);
    ValueTask<BackendResumeAdmissionResult> BeginMaintenanceResumeAsync(
        BackendResumeAdmissionRequest request, CancellationToken cancellationToken);
    ValueTask<BackendEffectResult> ProbeEffectAsync(OperationIdentity identity,
        StorageAssetLink effectIntent, string itemId, CancellationToken cancellationToken);
    ValueTask<BackendCommitResult> ExecuteAsync(PreparedStorageTransaction request,
        BackendExecution execution, CancellationToken executionCancellation);
    ValueTask<OwnerReadResult> ReadAsync(PreparedStorageRead request,
        BackendExecution execution, CancellationToken executionCancellation);
    ValueTask<OperationQueryResult> QueryAsync(OperationQuery request,
        CancellationToken cancellationToken);
    ValueTask<StorageHealth> CheckHealthAsync(HealthRequest request,
        CancellationToken cancellationToken);
    ValueTask<BackendEffectResult> ApplyMigrationStepAsync(MigrationRequest request,
        MigrationStepV1 step, StorageAssetLink effectIntent,
        BackendExecution execution, CancellationToken ct);
    ValueTask<BackendBaseBackupResult> CreateBaseBackupAsync(BackupRequest request,
        StorageAssetLink effectIntent, BackendExecution execution, CancellationToken ct);
    ValueTask<BackendBaseBackupResult> ReadBaseBackupAsync(BackupRequest request,
        StorageAssetLink effectIntent, CancellationToken ct);
    ValueTask<BackendCutResult> ReadCutAsync(BackupRequest request,
        DatabaseRecoveryIdentity baseStart, DatabaseRecoveryIdentity baseEnd,
        StorageCoordinationToken cutToken, CancellationToken ct);
    ValueTask<BackendEffectResult> RestoreDatabaseAsync(RecoveryRequest request,
        RestorePointV1 point, StorageAssetLink effectIntent,
        BackendExecution execution, CancellationToken ct);
    ValueTask<BackendRecoveryTargetResult> VerifyDatabaseAsync(RecoveryRequest request,
        CancellationToken ct);
    ValueTask<BackendEffectResult> ValidateOwnerAsync(RecoveryRequest request,
        StorageOwnerRegistration owner, BackendExecution execution, CancellationToken ct);
}
public interface IStorageReadHandle : IAsyncDisposable {
    ObjectRef Metadata { get; }
    Stream Content { get; }
}
public sealed record BackendReadOpenResult(IStorageReadHandle? Handle, StorageFault? Fault);
public interface IStorageFileBackend : IAsyncDisposable {
    ValueTask<BackendEffectResult> ProbeEffectAsync(OperationIdentity identity,
        StorageAssetLink effectIntent, string itemId, CancellationToken cancellationToken);
    ValueTask<BackendFileResult> StageAndSealAsync(FileObjectRequest request, Stream source,
        StorageCoordinationToken writeToken, BackendExecution execution,
        CancellationToken executionCancellation);
    ValueTask<BackendReadOpenResult> OpenReadAsync(FileReadRequest request,
        StorageCoordinationToken readToken, CancellationToken cancellationToken);
    ValueTask<BackendFileResult> VerifyAsync(FileVerificationRequest request,
        StorageCoordinationToken readToken, BackendExecution execution,
        CancellationToken executionCancellation);
    ValueTask<OperationQueryResult> QueryAsync(OperationQuery request,
        CancellationToken cancellationToken);
    ValueTask<StorageHealth> CheckHealthAsync(HealthRequest request,
        CancellationToken cancellationToken);
    ValueTask<ObjectDirectoryOpenResult> OpenDirectoryAsync(CallContext context,
        StorageCoordinationToken token, int maxEntries, int maxBytes, CancellationToken ct);
    ValueTask<BackendEffectResult> ApplyGcAsync(GcCandidateV1 candidate,
        JournalAction action, StorageAssetLink effectIntent, OperationIdentity identity,
        StorageCoordinationToken token,
        BackendExecution execution, CancellationToken ct);
    ValueTask<BackendEffectResult> CopyBackupPartAsync(BackupPart part, ObjectRef? obj,
        OperationIdentity identity, StorageAssetLink effectIntent,
        BackendExecution execution, CancellationToken ct);
    ValueTask<BackendEffectResult> RestorePartAsync(BackupPart part, RecoveryRequest request,
        StorageAssetLink effectIntent, BackendExecution execution, CancellationToken ct);
    ValueTask<BackendEffectResult> VerifyRecoveryPartAsync(RecoveryEntryV1 part,
        RecoveryRequest request, BackendExecution execution, CancellationToken ct);
}
public enum StorageCoordinationKind { Write, Publish, Read, Hold, Gc, Backup, BackupCut, Operation, GcPlan }
public sealed record StorageCoordinationToken(ResourceHandle Handle, string AuthorityEpoch,
    long Fence, long ReferenceEpoch, StorageCoordinationKind Kind,
    VersionRef ReferenceCatalog, ImmutableArray<StoreRef> Stores,
    ImmutableArray<string> OwnerKeys, ImmutableArray<ObjectKey> Keys);
public sealed record StorageCoordinationRequest(CallContext Context,
    ResourceHandle Handle, OperationIdentity? Identity, StorageCoordinationKind Kind,
    ImmutableArray<ObjectKey> Keys, ImmutableArray<ObjectRef> Objects, VersionRef ReferenceCatalog,
    long? ExpectedReferenceEpoch, TimeSpan Ttl);
public sealed record StorageProtection(bool Complete, bool Referenced,
    bool ActiveIo, bool Held, bool BackupHeld, bool LegalHold,
    ImmutableArray<ObjectKey> PhysicalAliases, StorageFault? Fault);
public interface IStorageCoordinationLease : IAsyncDisposable {
    StorageCoordinationToken Token { get; }
    ValueTask<StorageProtection> CheckAsync(ObjectRef obj, CancellationToken ct);
    ValueTask<HoldStatus> RenewAsync(HoldRenewRequest request, CancellationToken ct);
    ValueTask<HoldStatus> GetStatusAsync(ResourceQuery request, CancellationToken ct);
}
public sealed record StorageCoordinationOpenResult(IStorageCoordinationLease? Lease,
    StorageFault? Fault);
public interface IStorageReferenceCoordinator : IAsyncDisposable {
    ValueTask<StorageCoordinationOpenResult> EnterAsync(StorageCoordinationRequest request,
        CancellationToken cancellationToken);
    ValueTask<StorageFault?> ValidateAsync(StorageCoordinationToken token,
        OperationIdentity identity, CancellationToken cancellationToken);
    ValueTask<StorageDurableProtectionResult> PreserveAsync(StorageDurableProtectionRequest request,
        CancellationToken cancellationToken);
    ValueTask<StorageFault?> ReconcilePublicationAsync(TechnicalCommitReceipt receipt,
        StorageCoordinationToken token, CancellationToken cancellationToken);
}
public enum StorageProtectionAction { PendingPublication, ReserveClosure, BindClosure }
public sealed record StorageDurableProtectionRequest(OperationIdentity Identity,
    StorageCoordinationToken Token, StorageProtectionAction Action,
    ImmutableArray<ObjectRef> Objects, string? ProtectionId, StorageAssetLink? Artifact);
public sealed record StorageDurableProtectionResult(string? ProtectionId, StorageFault? Fault);
public sealed record StorageRetentionPlan(VersionRef Version, StoreRef Store,
    ImmutableArray<string> StorageDomains, VersionRef OwnerRetentionPolicy,
    VersionRef LegalHoldProjection, TimeSpan OrphanGracePeriod,
    TimeSpan QuarantineGracePeriod, int MaxObjects, long MaxBytes);
public sealed record StorageBackendSet(IStorageDatabaseBackend Database,
    IStorageFileBackend Files, IStorageReferenceCoordinator References,
    IStorageMaintenanceBackend Maintenance, IStorageAssetBackend Assets);
public interface IStorageBackendFactory {
    ValueTask<StorageBackendSet> OpenAsync(ResolvedStorageConfiguration configuration,
        IStorageClock clock, CancellationToken cancellationToken);
}
public sealed record StorageRuntimeDependencies(IStorageConfigurationResolver Configuration,
    IStorageBackendFactory Backends, IStorageClock Clock, IStorageExecutionBarrier Barrier);
```

Resolved.Profile.Version=configuration.Store.Profile；Relational.Version=configuration.RelationalProfile，Files.Version集合与configuration.FileProfiles相同，Bindings.Version=configuration.OwnerBindingCatalog，References.Version=configuration.ReferenceCoordinator，全部exact匹配。configuration.ControlContext必须是受信任runtime控制上下文，Scope/Store与configuration一致，Caller具备`storage.runtime_create`；authority再次核验该能力，不能用普通租户上下文创建完整Runtime。References.AuthorityId、Owner/Scope/Store集合与Profile配额同样有限且完整。Endpoint/Root/Credential/TlsPolicy等是可信配置引用，不是路径/连接串；A1/A2在自己包内解析它们。Resolver不得创建数据源或产品状态；失败/不支持版本抛StorageInitializationException。工厂先按options.ResolutionBudget解析，再按Profile.Runtime.StartupBudget开后端；取消后等已建后端全部释放。Resolver/BackendFactory/Clock/Barrier始终由Host持有、不由Runtime Dispose；返回BackendSet的五个独占实例由Runtime拥有，禁止同实例交给两个Runtime。Open失败由factory释放部分实例；Runtime成功后按任务→lease→Maintenance/Assets→Files→References→Database顺序排空和Dispose，每实例仅一次。No-op barrier用于生产，不能从请求选择或替换它。

**启动注册快照的固定顺序。** Resolver返回后、调用BackendFactory之前，Runtime用Input.MaxCatalogEntries/MaxCatalogBytes累计检查整个注册图，复制Profile、所有descriptor/Owner/Scope/Store/嵌套数组为本实例独占不可变值并建立索引。default数组、超限、重复Binding.Version、重复OwnerKey、同类ref同Id/Revision异Hash或缺精确依赖均在零backend IO阶段拒绝；禁止last-wins覆盖、隐式补Owner、从请求补注册或启动后热替换。完整Scope/Store/VersionRef按字段值比较，不以record内ImmutableArray的引用相等代替目录一致性。Binding按Version定位，再核Owner/Kind/Schema/Purpose；**CLR PayloadType只在该Binding内校验**，不作为跨Binding唯一键，允许inspection-evidence七个不同绑定使用同一个封闭payload类型。多个Binding共用输入codec仅在完整Version/Schema/PayloadType一致、登记为同一稳定实例时允许；共用结果codec核其Version/Schema及同一实例，不给它编造PayloadType属性。同版本注入不同实例或不同声明拒绝。

注入codec/resolver/validator的对象不被克隆或转移所有权。Host保持原实例；其Version/Schema/PayloadType等声明必须从构造到所有借用真实结束均不可变、getter零IO。Runtime在启动捕获声明，在调用前核与原捕获值一致；变化按UnsupportedVersion封闭失败，不重新注册或重算历史hash。PostgreSql工厂同样在打开数据源前冻结marshal数组及其声明，并只消费Runtime交来的**同一已冻结配置**，不再次Resolve或查询另一个全局目录。两个Host各自构造注册快照，读Host只登记所需Read能力；如果要做完整GC/cluster备份，须另外登记该范围的全部Owner，不能把读Host的窄目录称完整。

启动只验证ReferenceResolver的声明、Owner映射及已部署技术Schema，不调用OwnerReferenceResolver.OpenAsync、不枚举领域根，也不要求依赖Store的slot提前Attach。inspection-evidence按package→配置快照→原Factory.CreateAsync成功→一次StoreSlot.Attach→开放本模块调用的顺序装配，消除创建Store与列举根的循环。slot未Attach/Attach失败时根查询Unavailable或Blocked，绝不返回空完整根；原Factory成功产生的Store仍归原Host，按既有强根/原Task/独立cleanup处理。关闭时Host先停消费者及新维护接纳、关闭resolver接纳并观察原任务/snapshot排空，再停Runtime及释放其backend，最后结束Host注册依赖的生命周期；resolver不反向Dispose借用Store。任一原借用/cleanup仍未知时继续强持同组对象/Task，不能因Dispose观察到期替换它们。

Codec必须 exact CLR PayloadType、Schema/Version匹配；Encode返回非default且有界的独立immutable bytes，不保留payload；GetReferences只解析该canonical快照，不再读调用方对象。Runtime比较提取集合与请求集合完全相同、检查ResultCodec注册和完整请求hash后才接纳。结果codec由Owner消费ResultSchema/Bytes，Runtime不解释领域结果。SQL只在A1通过StatementCatalog查可信注册包；它的内容/Golden归Owner，端口与载荷封装已冻结，缺一个Owner不阻断其它已注册绑定。各Max/TimeSpan有效域按§8；MinAffectedRows≥0且≤MaxAffectedRows，MaxCommands>0，MaxRetries≥0，RetryDelay/lock/statement timeout>0，Read只能Query用途。配置不存在所需用途/绑定/格式时明确拒绝，不能自动选默认。

ResultCodec.Validate不解码成公共领域对象、不写事实；bytes过限/Schema不符/领域校验失败在commit前回滚并转InvalidInput，绝不能在commit后抹掉已提交事实。输入codec调用前核exact Type/Schema，Encode(payload,MaxPayloadBytes)/GetReferences(bytes,MaxReferences)不得有IO/副作用或超预算分配。必需领域golden bytes/hash由Owner注册包提供，技术信封编码固定如下，不留给Owner选序列化。

请求hash唯一为SHA-256(ASCII `IM066-REQUEST-1`无终止byte + StorageOperationKind Int32 + Context.Scope + Context.Store + Identity.Scope/StoreId/StoreGeneration/OwnerKey/OperationId/IdempotencyKey + 下表tail)。同一字段若在Context及Identity各出现一次就都编码，Identity.PayloadHash本身不编码；Caller/ExecutionBudget/WaitBudget/审计时间不编码。原语/nullable/array顺序复用§6.4；References按ObjectKey五字段Ordinal排序、重复Key拒绝，所有VersionRef都编码Id/Revision/hash。Host与Runtime分别按此精确表重算；纯C0仍不计算hash。

| Kind | tail（严格顺序，且仅这些字段） |
|---|---|
| Transaction | Binding（请求VersionRef）、完整StorageBindingDescriptor、输入codec返回的canonical byte array、排序后的References |
| Stage | Key、MediaType、Format、ExpectedBytes、ExpectedHash；不编码Stream，实际内容hash由后端计算 |
| Verify | Object |
| Hold | Object、ReasonKey、Ttl |
| Renew | Handle、ExpectedVersion、Ttl |
| Migration | CurrentSchema、Plan |
| Backup | BackupProfile、OwnerReferenceCatalog |
| Restore/VerifyRecovery | BackupClosure、RestorePoint、IsolatedTarget |
| GcPlan | RetentionPlan、OwnerReferenceCatalog、MaxObjects |
| Gc | Plan、MaxObjects |

同请求语义只有等待/授权预算变化hash不变；Binding/codec/Profile版本、Object描述、Key或Kind改变hash必变，Unknown只按原identity回查。Stop/Release是实例控制身份，不进入此durable hash/route协议。控制上下文runtime_create授权失败不得建立route/backend。

公开摘要入口为Runtime namespace静态类`StorageRequestHasher`，同步返回Sha256。每个重载末尾都有显式`StorageInputLimits limits`，完整签名：`Compute(RegisteredTransactionRequest request, StorageBindingDescriptor binding, ImmutableArray<byte> canonicalPayload, StorageInputLimits limits)`；其余为`Compute(FileObjectRequest request, StorageInputLimits limits)`、`Compute(FileVerificationRequest request, StorageInputLimits limits)`、`Compute(RetentionHoldRequest request, StorageInputLimits limits)`、`Compute(HoldRenewRequest request, StorageInputLimits limits)`、`Compute(MigrationRequest request, StorageInputLimits limits)`、`Compute(BackupRequest request, StorageInputLimits limits)`、`Compute(RecoveryRequest request, bool verifyOnly, StorageInputLimits limits)`、`Compute(GcPlanRequest request, StorageInputLimits limits)`、`Compute(GcRequest request, StorageInputLimits limits)`。非法shape/limits抛ArgumentException；identity.PayloadHash忽略，可用合法占位sha构造请求后with填hash。仅增量SHA-256编码，不分配整个信封副本；编码前核字符串/数组/canonical byte limit，不能依赖隐藏Profile或静态状态。Runtime用当前Profile.Input再校验并调用，错误转InvalidInput。ObjectKey排序为StoreId Ordinal→Generation数值→TenantId/StorageDomain/ObjectId Ordinal。Format按FormatValidators精确注册；Stage封口前用内部有限只读staging流调用validator，Verify同样全读，validator不拥有/保留流或外部IO，未知Format拒UnsupportedVersion。C1使用不透明byte validator，无视觉算法。

ReferenceResolvers按OwnerRegistration.ReferenceResolver逐VersionRef exact注册，ReadValidation按Owner正式验证目录注入Maintenance适配器。OpenAsync必须在当前ReferenceCatalog与Backup/BackupCut/Gc/GcPlan协调token保护下建立有限不可变Owner快照；snapshot页在MaxEntries/MaxBytes内、Sequence从0递增、Next不回退、所有Object属于登记Scopes/Stores。Complete=true仅在已覆盖该Owner全部实体/引用且页流到尾后报告；失败Empty/Complete=false/Fault，未知或缺resolver不能当零引用。snapshot由调用者持有并Dispose，取消等待真实Reader结束，保护token在整个枚举/闭包保持转换期间有效。读取只是列举既有事实，不能建表/修引用；真实Owner SQL、根历史及完整性验证的实现属于该Owner的内部工程门，客户只提供无法由软件证据确定的领域政策/物理验收值。签名、预算和资源约定在此冻结。

Clock戳只在本实例比较，GetElapsedTime单调非负、单位TimeSpan，DelayAsync可取消且不产生后台遗留timer；UTC仅审计。C1夹具使用可推进clock+barrier，生产使用BCL Stopwatch/TimeProvider实现，不以墙钟控制截止。BeforeAdmission的取消尚未建任务；AfterAdmission及之后barrier受执行token而非等待token控制。AfterBackend/BeforeResourceRelease的阻塞使任务非终态并保留额度/借用，即使回执已知；解除后才Drained→ResourcesReleased→Completed。barrier不写事实、不改变后端结果，异常以固定错误收口并排空。

Runtime在BeforeResourceRelease barrier前将task置Draining并保存已取得原Result；barrier只阻止资源转交，backend自己已清理的内部IO不会被“复活”，但Runtime源流借用、协调lease/任务额度仍保留。执行取消穿过barrier后也必须真实释放，BeforeResourceRelease异常不能跳过Dispose。首次接纳线程/任务表插入和Stop关接纳使用同一互斥/CAS权威，无检查后再入队窗口；所有快照复制不可变、不返回可修改状态容器。

请求摘要最小向量已用BCL复算：Kind=Stage(2)、Scope=(t,s,l,n,d)、Store=(x,1,VersionRef(v,1,`aa`×32))、Identity Scope/Store重复上述、Owner=o、Operation=p、Idempotency=k、ObjectKey=(x,1,t,m,a)、MediaType=`application/octet-stream`、Format=(f,1,`aa`×32)、ExpectedBytes=3、ExpectedHash=`aa`×32；编码按`IM066-REQUEST-1`+Stage tail固定规则共290byte，SHA-256=`c891eef31addc1b271b36a202a9f0ea7d057d49dbe4c3eda040586be7957fc2e`。此向量只作为Hasher/C1 codec夹具，不是文件内容hash或生产Profile。

Backend Execute/Stage/Verify/Read等方法不能在真实本地IO、Reader/command/connection/内部stream清理前返回；原ValueTask由Runtime单次消费并保存在受管工作Task内，不把调用方ct直接当executionCancellation。ExecutionBudget发合作取消；不配合就Draining/DrainUnknown而非Dispose后假成功。BackendCommitResult的Receipt已知/Unknown时非null；Fault与§6.1映射一致；未取得回执允许null+Fault。File同理。接纳后、任何副作用前RegisterAsync用完整identity全键/OperationId约束耐久登记Kind/原Profile/SemanticVersion；同键同identity/Kind/version返回Created=false，异身份/种类/版本Conflict，原行不改；新登记Created=true。Register响应未知不能进入后端，由原identity读Route回查。ReadRoute成功Registration非null/Created=false，权威查无Registration=null/Created=false/Fault=null仅表示未登记；过保证期ResultExpired。Created=false不能重新执行；先查原事实及在途任务，未决写者需要fencing/恢复才允许同身份续作。路由不承担业务成功事实，Transaction仍在同业务事务写commit回执。QueryOperation先核授权并ReadRoute，再按Kind到Database/Files/Maintenance查原ledger/journal；Hold/Renew是实例lease CAS，不登记durable route且不产生OperationRecord，只从Hold.GetStatus/Resource查，给其身份作QueryOperation返回InvalidInput。不能“数据库NotFound就文件NotFound”；未知路由/旧主不明保留Unknown。

每个durable operation先由Runtime用EnterAsync取得Kind=Operation、Identity=原请求、Keys/Objects=Empty的单写lease，再以其Token调用RegisterAsync；Token.Stores只含当前Store、OwnerKeys只含原Owner，不能锁任意集群。此lease只授原identity写技术证据，不授对象删除/领域写入，Write/Publish/Read/Gc/Backup的保护另取。Register验证token当前有效并登记writer_epoch=Token.AuthorityEpoch、writer_fence=Token.Fence；完整注册内容同值重放不更改原writer或再次消费source。BackendExecution.WriterToken在durable执行/对账中必须是该Operation token，在窄读取中为null；InstanceEpoch/WorkId仍是Runtime本地执行标识，不混同authority epoch/fence。Runtime持有单写lease直至本地IO、迟到回执保存及其它借用真实排空；Ttl触发合作取消但不自动授新writer，未知旧写者不能凭超时接管。ValidateAsync返回null只证明token在同identity/authority/作用域下仍为当前持有者，失效返回Conflict、不可确认返回CommitUnknown；不续租、不改引用、不发effect。各后端在intent、实际effect及证据写入前核它，且与协调者的fence变更线性化；仅先检查后独立写不能证明安全。旧writer真正停止或其全部发布/effect路径被不可绕过地fenced后，才可授新Operation token。C1用显式lease表/CAS模拟，不据数据库连接消失证明物理IO停止。

Registration.RuntimeProfile固定为Context.Store.Profile；SemanticVersion取Transaction.Binding、Stage.Format、Verify.Object.Format、Migration.Plan、Backup.BackupProfile、Restore/VerifyRecovery.RestorePoint、GcPlan.RetentionPlan或Gc.Plan，对应Kind不得换来源。Operation/GcPlan lease不向Host交付公开资源，只由受管worker持有并真实Dispose；无TaskHandle的PlanOrphanCollection同样等它及快照Reader排空才返回。BackendExecution.RemainingBudget为当前单调deadline剩余的正有限TimeSpan，deadline已到不进入新的effect，排空/保存已发出effect的观察不重新开预算。

Runtime首先只读查原route/task；已有同请求走原事实观察，不为重放取第二writer。首次并发在route尚未出现时，Operation lease竞争的败者回查原route/task，尚不可见则ResourceBusy或Unknown，不消费source。单写lease与route唯一约束共同闭合“查无后并发登记”窗口。

AppendEvidence用于原技术operation的文件/维护/计划证据及Unknown对账，ExpectedRevision≥0、Evidence.Revision=checked(Expected+1)且WriterToken必须是该identity当前Operation token；Registration/Record/Journal/Maintenance完整identity一致（引用原Plan的Creator可以不同但该Plan不作为此处Journal）。同revision同canonical内容幂等重放，异内容/fence失效Conflict；不覆旧行。Transaction首次commit证据由ExecuteAsync同业务事务生成，AppendEvidence不能执行领域写、重写既有Committed或把已知Committed变RolledBack；允许原Unknown追加权威已确认Committed/RolledBack的观察证据，但不重新提交事务。维护组合器在Seal journal/maintenance后AppendEvidence更新原head；跨存储失败返回Unknown并保留已封口journal，沿原identity+fence回查不重新执行effect。ReadEvidence成功Evidence非null/Fault=null；权威无证据Evidence=null/Fault=null仅表示尚未取得，不作为NotFound安全重试证明；拒权/过期/不可用null+Fault。File自身封口journal仍为字节发布真值，DB索引缺失不丢迟到事实。C1 fake实现此有界CAS store，无业务数据库依赖。

证据追加先验证当前Operation token，Evidence.WriterEpoch/Fence必须与它一致；route头的revision必须等于ExpectedRevision。新证据行、evidence_head_revision及当前writer指针在同一事务/CAS中一起发布，失败不留半个head。不同writer只能在Coordinator已确认旧writer停止/不可绕过fencing后更新指针；epoch变化不能单凭数值较大认新writer。历史证据保留原writer。QueryOperation/ReadEvidence等读取口不调用AppendEvidence或执行恢复副作用；证据保存由原受管worker或明确获维护授权的对账执行承担，不把查询伪装成写入。

维护续作唯一入口是ResumeMaintenanceAsync，不适用于Transaction/Stage/Verify/GcPlan/Hold。Request.Input必须为四种精确封闭类型之一，Request/内部原请求/Journal.Creator的完整identity相同，当前Context只替换原请求的Caller和等待/执行预算，Scope/Store及所有语义字段不变；按原版本Hasher重算必须等于原PayloadHash/Registration。Runtime核`storage.maintenance_resume`及原Kind对应能力，Backup/Recovery再核全部Owner/Store范围。Journal必须是原操作当前head的精确JournalV1；ExpectedAttempt≥0、下一次attempt不得超过Profile.Maintenance.MaxResumeAttempts（0禁用续作）。原Succeeded、未决旧writer、缺journal/旧codec、原GC plan过期或未证明安全的effect不得重跑。

Runtime在接纳前读取原route/evidence和journal，取得可证明旧writer已停止/被fenced的Operation lease，再调用BeginMaintenanceResumeAsync。A1/fake在同原identity事务中比较当前attempt/head与ExpectedAttempt/Journal，插入下一attempt并原子更新writer；成功Attempt非null、等于ExpectedAttempt+1，Created=true才允许启动该次受管worker。已接纳过的同ExpectedAttempt+Journal请求Created=false并返回既有attempt，只查询既有task/原事实，不再次执行；同attempt异journal/Input摘要为Conflict。失败Attempt=null/Created=false/Fault非null，未知接纳不进effect。每个attempt有固定TaskHandle，单identity同时仅一个在途attempt；初次执行Attempt=0，resume在BackendExecution/Evidence中携带正attempt，不改变operation identity或历史证据。新attempt的Wait/ExecutionBudget独立有限，不刷新旧Task或绕过MaxResumeAttempts。停止/释放沿§6.2真实排空。

重放resume时先核原attempt接纳记录，再核当前head；原请求已经成功接纳，即使worker后来追加新journal，也返回Created=false/既有attempt，不因当前head改变而新建或错报Conflict。MaintenanceSnapshot.Attempt等于当前证据attempt，Host通过已授权ReadMaintenance取得ExpectedAttempt及Journal；不读后端私表。已接纳而本地task不可见时只查询原operation，不伪造新TaskHandle。

续作按原journal逐项先读后端权威结果：已确认动作不再执行；Unknown动作只能在同intent下检查既有结果，仍未知就返回Unknown。只有已证明原effect未发生且旧writer不能迟到执行，才允许调用原步骤；未发intent的后续步骤按原plan执行。不得仅凭文件存在/缺失、对象hash、当前数据库可连或一次超时判定安全。GC沿原PhysicalIdentity/隔离位置，迁移沿原step/checksum，Restore沿同隔离目标与恢复点；Backup沿持久BackupWork保存的同base/cut/对象集合，不取新cut或换ClosureHoldId。恢复入口不改变参数、plan、目标或工具版本，不自动补外部Owner内容。

ProbeEffectAsync仅按精确identity/intent/itemId只读后端的耐久effect记录和原物理身份，不启动effect或追加证据。Confirmed/Fault=null是原效果已确认；NoEffect/Fault=null只在已证明未发生且原writer不能迟到执行时返回；否则Unknown/CommitUnknown，不以一次NotFound替代证明。读权限/格式失败为NoEffect+对应Fault，不能许可重跑。ReadBaseBackupAsync沿原BackupCopy intent读准确Parts/Start/End；成功字段与CreateBaseBackup一致，未知为Empty/null/null/CommitUnknown，不创建新base。这些读取在真实IO清理后返回；Maintenance.ResumeAsync由真实组合器调用它们、封口新观察journal并追加证据，Runtime只负责接纳/权限/attempt/任务与排空。

维护资产失败也必须保留可读的原head；没有MaintenanceSnapshot时Host只允许只读回查，不能猜ExpectedAttempt或journal。完整事务Unknown的权威对账不重跑领域写，由受管恢复观察保存已取得结论；公开Query只返回该权威读到的事实。跨请求文件续传仍不进入ResumeMaintenance。

ReadHandle只暴露有界managed Stream，不泄SDK/native/path；Runtime用当前实例ResourceHandle包装它并持有Read协调lease至活动读结束、handle.Dispose完成。读token与Object完整描述绑定；备用Verify也必须由Runtime取得Read保护，不能越过GC。Runtime先分配ResourceHandle传Enter，再包装同一个Handle；Hold的Renew/GetStatus才可被lease识别。Write以Keys保护尚未形成ObjectRef的源对象，封口前由后端在同Coordinator建立durable PendingPublication保护，之后Write临时lease可释放，持久保护不阻Runtime Stop。Publish先于DB变更，数据库同事务建立持久引用；Unknown保留durable发布保持，临时lease Dispose不删除它。Gc进入独占物理别名集合、持有fence期间Check与移动/删除线性化；Complete=false/Fault/epoch变化均不删。Backup/BackupCut必须按ReferenceCatalog完整Stores/OwnerKeys授权与保护，空Keys在这两种表示保护全集、不是单租户。Operation的空Keys只锁单操作；GcPlan的空Keys只冻结当前Store登记Owner范围的有界目录/引用快照，阻止规划期间GC变更，不能授删除。其余Kind的Keys必填且与Objects/请求精确相同；零引用事务可用Empty的Publish token，只保护该Owner事务与reference epoch，不扩为全集。Fence>0、ReferenceEpoch≥0且不可复用，Token的Handle与请求相同、实例epoch有效。这些语义必须由真实Coordinator/Owner接入，C1 fake只能证明调用和保留规则。

PreserveAsync先验证当前token/完整Objects。PendingPublication仅Write/Publish允许，ProtectionId/Artifact=null，按原write/commit身份创建耐久保护；ReserveClosure仅Backup/BackupCut允许，ProtectionId/Artifact=null，预留同identity+完整对象集合的保持Id；BindClosure须原ProtectionId非null、Artifact为已封口BackupClosureV1且ClosureHoldId/Creator/对象集合相同，将预留绑定准确link。成功ProtectionId非null/Fault=null，同身份同Action/集合/link重放同Id，异描述Conflict；失败Id=null/Fault，不因失败释放临时保护或允许新引用。顺序为ReserveClosure→封口含Id的Closure→BindClosure→核保持完成后释放屏障；任何中断用原journal恢复，不把预留当已绑定，也无self-hash循环。ReconcilePublicationAsync只接受已确认Committed/RolledBack/Rejected回执，核token与精确引用；Committed将pending转持久引用保护，RolledBack/Rejected保留OrphanGracePeriod保护，Unknown返回CommitUnknown并保持。成功null Fault，其它Fault保留原pending；取消/释放lease不删除任何durable保护。闭包保持退役只能由已批准retention维护plan执行并journal，不由读API或Runtime.Dispose删除。

### 6.4 维护资产、结果Schema和分页契约

本节所有类型在Contracts，维护执行仍由Runtime+A1/A2组合，不新增A3 DLL。资产是技术记录，各页均为精确不可变snapshot；journal追加产生新修订，旧页不能读“最新”。

```csharp
public enum StorageAssetSchema { MaintenanceV1, GcPlanV1, JournalV1, BackupClosureV1,
    RestorePointV1, RecoveryV1, MigrationPlanV1, BackupWorkV1 }
public sealed record StorageAssetLink(VersionRef Version, StorageAssetSchema Schema,
    OperationIdentity Creator);
public interface IStorageAssetHeader { OperationIdentity Creator { get; } }
public interface IStorageAssetItem { long Sequence { get; } }
public sealed record MaintenanceSnapshotV1(OperationIdentity Creator, MaintenanceKind Kind,
    MaintenanceState State, StorageAssetLink? Plan, StorageAssetLink Journal,
    StorageAssetLink? Closure, StorageAssetLink? RestorePoint, StorageAssetLink? Recovery,
    long CompletedCount, long SkippedCount, long FailedCount, long UnknownCount,
    DateTimeOffset AtUtc, int Attempt) : IStorageAssetHeader;
public sealed record GcPlanV1(OperationIdentity Creator, StoreRef Store,
    VersionRef RetentionPlan, VersionRef ReferenceCatalog, long ReferenceEpoch,
    DateTimeOffset CreatedUtc, DateTimeOffset ExpiresUtc,
    long CandidateCount, long CandidateBytes, int MaxObjects) : IStorageAssetHeader;
public sealed record GcCandidateV1(long Sequence, ObjectRef Object,
    VersionRef PhysicalIdentity, ImmutableArray<ObjectKey> Aliases,
    long ReferenceEpoch, bool ProtectedAtPlanning) : IStorageAssetItem;
public enum JournalPhase { Planned, EffectIntent, EffectConfirmed, Skipped, Failed, Unknown }
public enum JournalAction { MigrateStep, Backfill, Quarantine, Delete,
    BackupCopy, SealClosure, RestoreCopy, Verify }
public sealed record JournalV1(OperationIdentity Creator, MaintenanceKind Kind,
    StorageAssetLink? Plan, long EntryCount, DateTimeOffset AtUtc) : IStorageAssetHeader;
public sealed record JournalEntryV1(long Sequence, string ItemId, ObjectRef? Object,
    VersionRef? PhysicalIdentity, JournalAction Action, JournalPhase Phase,
    string AuthorityEpoch, long Fence, int Attempt, DateTimeOffset AtUtc,
    StorageFault? Fault) : IStorageAssetItem;
public sealed record WalPosition(uint Timeline, ulong Lsn);
public sealed record DatabaseRecoveryIdentity(ulong SystemId, int ServerMajor,
    VersionRef ToolVersion, WalPosition Position, DateTimeOffset AtUtc);
public enum BackupPartKind { BaseBackup, Wal, Object, Catalog, Schema, Codec, KeyMetadata, TimelineHistory }
public sealed record BackupPart(string ItemId, BackupPartKind Kind, VersionRef Locator,
    long Bytes, Sha256 ContentHash, VersionRef Format, VersionRef Destination,
    WalPosition? WalStart, WalPosition? WalEnd);
public sealed record BackupClosureV1(OperationIdentity Creator,
    DatabaseRecoveryIdentity BaseStart, DatabaseRecoveryIdentity BaseEnd,
    DatabaseRecoveryIdentity Target, ImmutableArray<StoreRef> Stores,
    ImmutableArray<StorageOwnerRegistration> Owners, VersionRef BackupProfile,
    VersionRef ReferenceCatalog, VersionRef KeyReference, string ClosureHoldId,
    long ItemCount, long TotalBytes, bool Complete) : IStorageAssetHeader;
public sealed record BackupClosureEntryV1(long Sequence, BackupPart Part,
    ObjectRef? SourceObject, string OwnerKey, string TenantId,
    bool Required, bool Verified, StorageFault? Fault) : IStorageAssetItem;
public sealed record BackupWorkV1(OperationIdentity Creator, VersionRef BackupProfile,
    VersionRef ReferenceCatalog, ImmutableArray<StoreRef> Stores,
    ImmutableArray<StorageOwnerRegistration> Owners, DatabaseRecoveryIdentity? BaseStart,
    DatabaseRecoveryIdentity? BaseEnd, DatabaseRecoveryIdentity? Target,
    string? ClosureHoldId, long ItemCount, long TotalBytes, bool CutPinned) : IStorageAssetHeader;
public sealed record RestorePointV1(OperationIdentity Creator, StorageAssetLink Closure,
    DatabaseRecoveryIdentity Target, long RequiredItems, long RequiredBytes,
    bool Restorable) : IStorageAssetHeader;
public sealed record RestorePointEntryV1(long Sequence, string ItemId,
    StorageAssetLink Closure, long ClosureSequence, Sha256 ExpectedHash,
    long ExpectedBytes) : IStorageAssetItem;
public sealed record RecoveryV1(OperationIdentity Creator, StorageAssetLink Closure,
    StorageAssetLink RestorePoint, VersionRef IsolatedTarget,
    DatabaseRecoveryIdentity? ActualTarget, long RequiredCount, long VerifiedCount,
    long FailedCount, long UnknownCount, bool RestoredAndVerified,
    DateTimeOffset AtUtc) : IStorageAssetHeader;
public sealed record RecoveryEntryV1(long Sequence, string ItemId, ObjectRef? Object,
    VersionRef Verification, long ExpectedBytes, Sha256 ExpectedHash,
    bool Required, bool Verified, StorageFault? Fault) : IStorageAssetItem;
public enum MigrationStepKind { Transactional, NonTransactional, Backfill }
public sealed record MigrationPlanV1(OperationIdentity Creator, VersionRef FromSchema,
    VersionRef ToSchema, VersionRef MinimumReader, VersionRef MinimumWriter,
    long RequiredFreeBytes, long StepCount, bool AllowsCompensation) : IStorageAssetHeader;
public sealed record MigrationStepV1(long Sequence, string StepId, Sha256 StepHash,
    MigrationStepKind Kind, VersionRef StatementCatalog, VersionRef Validation,
    VersionRef? Compensation, int MaxRows, TimeSpan ExecutionBudget,
    TimeSpan LockBudget) : IStorageAssetItem;
public sealed record StorageBackupProfile(VersionRef Version,
    string AuthorityId, ImmutableArray<StoreRef> Stores, ImmutableArray<string> OwnerKeys,
    VersionRef ToolVersion, VersionRef Destination, VersionRef KeyReference);
public sealed record StorageIsolatedTargetProfile(VersionRef Version,
    VersionRef DatabaseTarget, VersionRef FileTarget, VersionRef AccessPolicy,
    VersionRef ToolVersion, bool DeviceWorkersDisabled, bool SendWorkersDisabled);
public enum BackendEffectState { Confirmed, NoEffect, Unknown }
public sealed record BackendEffectResult(BackendEffectState State, StorageFault? Fault);
public sealed record BackendBaseBackupResult(ImmutableArray<BackupPart> Parts,
    DatabaseRecoveryIdentity? Start, DatabaseRecoveryIdentity? End, StorageFault? Fault);
public sealed record BackendRecoveryTargetResult(DatabaseRecoveryIdentity? Target,
    StorageFault? Fault);
public sealed record BackendCutResult(DatabaseRecoveryIdentity? Target,
    ImmutableArray<BackupPart> RequiredWal, StorageFault? Fault);
public sealed record ObjectDirectoryEntry(ObjectRef Object, VersionRef PhysicalIdentity,
    ImmutableArray<ObjectKey> Aliases, DateTimeOffset UnreferencedSinceUtc,
    bool PendingPublication);
public sealed record ObjectDirectoryPage(ImmutableArray<ObjectDirectoryEntry> Entries,
    long? NextSequence, StorageFault? Fault);
public interface IStorageObjectDirectory : IAsyncDisposable {
    string SnapshotId { get; }
    long ReferenceEpoch { get; }
    ValueTask<ObjectDirectoryPage> ReadAsync(long nextSequence, CancellationToken ct);
}
public sealed record ObjectDirectoryOpenResult(IStorageObjectDirectory? Directory,
    StorageFault? Fault);
public sealed record StorageAssetQuery(CallContext Context, StorageAssetLink Asset);
public sealed record StorageAssetHeaderResult<T>(StorageAssetLink Asset,
    T? Header, StorageFault? Fault) where T : class, IStorageAssetHeader;
public sealed record StorageAssetCursor(StorageAssetLink Asset, long NextSequence);
public sealed record StorageAssetPageQuery(CallContext Context, StorageAssetLink Asset,
    StorageAssetCursor? After, int MaxEntries, int MaxBytes);
public sealed record StorageAssetPage<T>(StorageAssetLink Asset,
    ImmutableArray<T> Entries, StorageAssetCursor? Next, StorageFault? Fault)
    where T : IStorageAssetItem;
public interface IStorageMaintenanceReader {
    ValueTask<StorageAssetHeaderResult<MaintenanceSnapshotV1>> ReadMaintenanceAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetHeaderResult<GcPlanV1>> ReadGcPlanAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetHeaderResult<JournalV1>> ReadJournalAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetHeaderResult<BackupClosureV1>> ReadClosureAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetHeaderResult<RestorePointV1>> ReadRestorePointAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetHeaderResult<RecoveryV1>> ReadRecoveryAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetHeaderResult<MigrationPlanV1>> ReadMigrationPlanAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetHeaderResult<BackupWorkV1>> ReadBackupWorkAsync(StorageAssetQuery q, CancellationToken ct);
    ValueTask<StorageAssetPage<GcCandidateV1>> ReadGcCandidatesAsync(StorageAssetPageQuery q, CancellationToken ct);
    ValueTask<StorageAssetPage<JournalEntryV1>> ReadJournalEntriesAsync(StorageAssetPageQuery q, CancellationToken ct);
    ValueTask<StorageAssetPage<BackupClosureEntryV1>> ReadClosureEntriesAsync(StorageAssetPageQuery q, CancellationToken ct);
    ValueTask<StorageAssetPage<RestorePointEntryV1>> ReadRestorePointEntriesAsync(StorageAssetPageQuery q, CancellationToken ct);
    ValueTask<StorageAssetPage<RecoveryEntryV1>> ReadRecoveryEntriesAsync(StorageAssetPageQuery q, CancellationToken ct);
    ValueTask<StorageAssetPage<MigrationStepV1>> ReadMigrationStepsAsync(StorageAssetPageQuery q, CancellationToken ct);
    ValueTask<StorageAssetPage<BackupClosureEntryV1>> ReadBackupWorkEntriesAsync(StorageAssetPageQuery q, CancellationToken ct);
}
public sealed record StorageAssetWriteRequest(string AssetId, int Revision,
    StorageAssetSchema Schema, IStorageAssetHeader Header,
    ImmutableArray<IStorageAssetItem> Entries);
public sealed record StorageAssetSealResult(StorageAssetLink? Asset, StorageFault? Fault);
public interface IStorageAssetBackend : IStorageMaintenanceReader, IAsyncDisposable {
    ValueTask<StorageAssetSealResult> SealAsync(StorageAssetWriteRequest request, CancellationToken ct);
}
public sealed record BackendMaintenanceResult(MaintenanceReceipt? Receipt, StorageFault? Fault);
public interface IStorageMaintenanceBackend : IAsyncDisposable {
    ValueTask<BackendMaintenanceResult> ResumeAsync(MaintenanceResumeRequest request,
        BackendExecution execution, CancellationToken ct);
    ValueTask<GcPlanReceipt> PlanGcAsync(GcPlanRequest request, BackendExecution execution, CancellationToken ct);
    ValueTask<BackendMaintenanceResult> CollectAsync(GcRequest request, BackendExecution execution, CancellationToken ct);
    ValueTask<BackendMaintenanceResult> MigrateAsync(MigrationRequest request, BackendExecution execution, CancellationToken ct);
    ValueTask<BackendMaintenanceResult> BackupAsync(BackupRequest request, BackendExecution execution, CancellationToken ct);
    ValueTask<BackendMaintenanceResult> RestoreAsync(RecoveryRequest request, bool verifyOnly,
        BackendExecution execution, CancellationToken ct);
    ValueTask<OperationQueryResult> QueryAsync(OperationQuery request, CancellationToken ct);
}
```

Assets的schema枚举是封闭结果Schema，v1字段顺序就是上列record顺序；不另让Owner定义这些技术Schema。MaintenanceV1没有页项；其余匹配GcPlanV1/GcCandidateV1、JournalV1/JournalEntryV1、BackupClosureV1/BackupClosureEntryV1、RestorePointV1/RestorePointEntryV1、RecoveryV1/RecoveryEntryV1、MigrationPlanV1/MigrationStepV1、BackupWorkV1/BackupClosureEntryV1。后者是尚未完成的备份工作快照，不能冒称完整closure。精确CLR类型及Creator不符拒绝；不接受额外类型/任意JSON。AssetId/Revision与VersionRef合法域一致，Creator固定原完整identity，资产不是访问凭证；读口逐资产核当前scope和`storage.maintenance_read`，跨集群Backup需全部Owner/租户范围授权，普通租户不能读全库manifest。

Seal成功Asset非null/Fault=null，精确schema/creator/内容由backend自身重算hash后耐久封口；同Id/revision/hash重放相同link，异hashConflict。失败Asset=null/Fault非null（提交封口意图响应未知使用CommitUnknown），查询原operation/journal不能造hash；ct取消同样等写入/flush/Reader资源清理才OCE，已有sealed资产不删除。资产page和Seal的异常必须按§6.5转固定Fault，无raw exception逃到Host；OOM/进程退出由Host按未完成处理，不伪成功。

单事务/文件对象/读页仍严格单Scope/Store/Generation。Backup/BackupCut token及BackupClosure/BackupWork/RestorePoint/Recovery资产允许跨Store/租户，因为它们必须绑定完整已注册cluster集合并逐项验权；不能用这一例外放宽Transaction/GC任意跨租户引用。各资产条目Object都必须在其Header直接登记或通过Closure/RestorePoint引用的Stores/Owners范围，否则InvalidInput；普通tenant拿集群link只能PermissionDenied，不能看其它租户计数。

内建资产编码唯一为ASCII域标记`IM066-ASSET-1`（无终止byte）+StorageAssetWriteRequest的AssetId/Revision/Schema/Header/Entries，严格按声明字段顺序；Schema只出现一次，不在Header前再追加。整数Int32/Int64/UInt32/UInt64小端、bool一byte 0/1、enum Int32（按本文声明顺序从0编号，显式赋值者用所示值，已发布编号不得重排）、string严格UTF-8的Int32长度+字节、Sha256为32原始byte、TimeSpan为Int64 ticks、UTC DateTimeOffset为Int64 UTC ticks、nullable为0/1后编码值、array为Int32计数+项；record按字段顺序递归、VersionRef按Id/Revision/Hash，接口按唯一schema实际类型，不写CLR名。Header.Creator含完整原identity及PayloadHash。AssetLink在封口后以SHA-256生成VersionRef，未包含自身hash，没有自引用。版本或内容变更产生新Revision/hash；相同Id/Revision异hash→Conflict，不覆盖。Schema演进新增枚举/reader，不静默用当前schema改历史。MaxAssetBytes/MaxJournalBytes/嵌套ID/数组与页预算在分配前校验，sealed资产保留到已批准retention，未决journal/Unknown不得按TTL清除。所有物化数组count≤Int32.MaxValue且更小Profile限额；Header计数虽是Int64也不得超实际数组支持域。

固定合成canonical向量（本轮已用BCL内存编码/SHA-256复算，未运行产品）：AssetId=`g`、Revision=1、Schema=GcPlanV1（1）；Creator.Scope=(t,s,l,n,d)、StoreId=x、StoreGeneration=1、OwnerKey=o、OperationId=p、IdempotencyKey=k、PayloadHash=`aa`重复32次。GcPlanV1.Store=(x,1,VersionRef(v,1,同aa摘要))、RetentionPlan=(r,1,同摘要)、ReferenceCatalog=(c,1,同摘要)、ReferenceEpoch=0、CreatedUtc=1970-01-01T00:00:00Z、ExpiresUtc=1970-01-01T00:00:01Z、CandidateCount=CandidateBytes=0、MaxObjects=1、Entries=Empty。canonical长度295byte，SHA-256=`a80d850c6f5326cd941c8e0769bd7593f162ba7b6bc2c42fc980aeef75a5eb31`。单字符均ASCII；UTC ticks分别621355968000000000/621355968010000000。这是codec夹具，不是有效生产plan（其Expires已过期），读历史允许，执行过期plan必须GcBlocked。

Sequence从0连续至count−1；首次After=null从0读，cursor.NextSequence是下一项的索引，必须带相同AssetLink（含Creator/Schema/hash），跨快照/类型/身份拒绝。成功页Entries非default、≤MaxEntries且canonical entry bytes之和≤MaxBytes，Next只在还有项时非null，不返回“空页+同cursor”无限循环；空集合成功Empty/Next=null。请求MaxEntries/MaxBytes>0且≤Profile页上限，checked NextSequence+count不溢出。单项大于MaxBytes→CapacityExceeded，不拆对象、不skip；可以在同snapshot内提高到已批准上限。HeaderResult成功Header非null/Fault=null；页失败Entries=Empty/Next=null/Fault非null，均回显请求Asset，不伪造存在或零计数；不存在/过期返回ResultExpired，未知存储返回Unavailable，digest不符IntegrityFailed。页IO/Reader在方法返回前真实释放，ct取消等清理后OCE；无TaskHandle且不后台交付页。

GcPlan的candidate是按ObjectKey排序的完整有界候选，Aliases覆盖同物理身份所有别名，不漏Owner；ProtectedAtPlanning只作快照说明，绝不授删除。执行固定Plan的全部候选，MaxObjects必须等于plan.MaxObjects，不靠缩减请求偷换摘要。当前epoch/引用/lease/fence重新检查，保护变化写Skipped，IO未知写Unknown；每次Quarantine/Delete在effect前写耐久EffectIntent，确认后EffectConfirmed，重启沿同ItemId/PhysicalIdentity/Fence查询；Unknown禁止重开放/新身份删。已确认Quarantine但未到QuarantineGracePeriod，末项记Skipped/GcBlocked并保留隔离位置，不虚构Unknown或已删除；以后通过获批新plan选择已隔离对象，先核原effect结论与当前保护。Journal Phase Failed/Unknown必须Fault，Skipped的原因用GcBlocked，EffectConfirmed只证该动作不代表整个operation成功；counts按每item最后确认状态聚合，不把attempt数计为对象数。

RetentionPlans按VersionRef exact解析，StorageDomains非空去重且在Store.Files注册，OwnerRetentionPolicy/LegalHoldProjection来自可信Owner；OrphanGracePeriod>0且≥Profile.Maintenance.OrphanGracePeriod，QuarantineGracePeriod≥0，MaxObjects/MaxBytes正且不超Profile对应plan限额。GC只选择UnreferencedSinceUtc满足orphan宽限、无PendingPublication、所有resolver Complete且无保持的对象；隔离后新的quarantine时间需满足第二宽限再删（0仅批准Profile/软件夹具允许）。UTC用于持久记录，期限由Coordinator的单调/重启fence处理，不以时钟回拨或旧epoch缩短宽限。OwnerRetentionPolicy内容/Legal Hold事实外部Owner，技术字段和行为此处已定。

PlanOrphanCollection也是技术幂等操作但无TaskHandle：route Kind=GcPlan，封口GcPlanV1后保存MaintenanceReceipt(GcPlan,Planned,MaintenanceV1 link)，四个完成计数均0；MaintenanceSnapshot.Plan指向精确GcPlanV1，Journal只记录计划生成，不造Delete。原identity查询Succeeded代表计划生成，不代表收集；新Gc operation的Plan参数引用该plan。取消后sealed plan保留并原identity回查，未封口不造Plan。GcPlanReceipt成功Plan非null、CandidateCount/Bytes等于header，失败Plan=null且两个计数0。Planned成功只与GcPlan配对；其他Kind/Planned为InvalidInput。

已成功读取并验证的固定GC plan，其最终counts必须Completed+Skipped+Failed+Unknown=CandidateCount（checked）；Completed仅该item所有所需删除/清理已确认，未确认效果记Unknown而不算删除。UnknownCount>0→Unknown/CommitUnknown；否则FailedCount>0且Completed>0→Partial/Unavailable，Failed>0且Completed=0→Failed/Unavailable；否则Completed>0→Collected；否则NoEligibleObjects（可含保护SkippedCount）。空plan也是NoEligibleObjects且全0。全局lease/fence/plan失效在副作用前为Blocked/GcBlocked：每个已知候选写Skipped及原因，Completed/Failed/Unknown=0、Skipped=CandidateCount，不套用NoEligibleObjects成功映射。权限拒绝保留PermissionDenied，不泄候选数量；plan未读取/未通过完整性校验时只返回外层Fault或全0的Blocked回执且Artifact=null，不声称已覆盖候选。执行中全局阻断将尚未发出effect的项计Skipped，已有项按实际结论聚合；未决效果仍优先Unknown。不能把保护跳过称清理成功。Backup/Restore有任何必需Unknown均Unknown，已知缺闭包为Blocked/NotRestorable，成功条件按header完整全验，不凭GC这套计数推算恢复成功。

BackupPart.Locator是受控备份资产定位ref，不是文件路径/密钥。BaseBackup/Wal/Catalog/Schema/Codec/KeyMetadata/TimelineHistory以及每SourceObject Copy均列项；Object必须SourceObject非null且Part.Bytes/ContentHash相同，其余SourceObject=null。WalStart/End只对Wal有值，timeline>0、start<end、覆盖从BaseStart到Target的连续无缺口范围且包含BaseEnd；三个身份SystemId/ServerMajor/ToolVersion一致。跨timeline必须显式包含TimelineHistory项并由目标PG工具核祖先切换点，不把不同timeline的LSN直接相减；TimelineHistory项WalStart/End=null。Lsn使用UInt64不截为有符号long。SystemId>0、ServerMajor>0、所有UTC offset=0；ToolVersion精确固定。Owners/Stores完整列举集群，Catalog/Schema/Codec包含恢复旧版本所需资产；KeyReference只引用密钥服务，不存密钥。Complete要求所有Required项Verified且Fault=null，条数/checked总byte与header相同；不得以metadata一致冒称内容已验。Part.ItemId唯一，非Object项的OwnerKey/TenantId用已注册技术维护scope身份，不填空或伪全租户。

BackupWork初值base/target/HoldId均null、CutPinned=false；base成功后Start/End必须一起非null，Target仍可null。cut成功且完整引用枚举/ReserveClosure确认后，Target/HoldId非null、CutPinned=true，才允许复制后续对象。每个阶段及每项验证变化Seal新Work修订，并将Journal.Plan更新为精确Work link、持久发布head后才进入下一effect；ItemCount/TotalBytes严格等于页集合。未知base结果保留原意图并回查，不填默认Start/End；CutPinned=false的重启续作仅可在原base结论确定后完成尚未取得的首次cut。CutPinned=true后Target/Stores/Owners/对象集合/ClosureHoldId不可变，只能追加同target所需WAL元数据及更新逐项确认状态，不取得更晚恢复点。成功BackupClosure复制该Work的固定base/cut/范围/HoldId及已验证条目；Work本身无Complete资格，不用于RestorePoint。Work与Journal均按未决记录保留，取消/未知不按TTL删。

RestorePoint显式绑定精确Closure与Target LSN/timeline，无“最新”或自由UTC恢复；RequiredItems/Bytes与页条目对应。每项指向原closure sequence并核hash/length，未来目标须新closure（含base/WAL及新增对象）后新point；缺required项Restorable=false/NotRestorable。Recovery逐required项核对象与Owner ReadValidation版本、长度/hash/格式，Verified=false的必需项须Fault；成功为VerifiedCount=RequiredCount、FailedCount=UnknownCount=0，ActualTarget非null且SystemId/ServerMajor/Position精确等于目标、ToolVersion精确等于已解析StorageIsolatedTargetProfile.ToolVersion，AtUtc是本次实际观察UTC、不要求等于历史cut时间。该版本须与源BackupProfile.ToolVersion兼容并在实际工具资格中验证，不凭版本号推定可恢复。未知实际点ActualTarget=null且UnknownCount>0、RestoredAndVerified=false，不能编默认cluster/LSN。VerifyRecovery只读隔离目标、不改数据。Migration plan给每step确切statement/validation/compensation引用及有限预算，NonTransactional实际读回journal，不自选降级。实体SQL/验证codec内容是Owner外部输入，不是本模块Schema缺口。

Maintenance后台组合端口读取同一Assets/References/Database/Files，BackendFactory创建时把实例显式注入其构造器；不得建第二套连接池/事实库。成功Gc/Backup/Restore/VerifyRecovery/Migration的Receipt.Artifact指向MaintenanceV1，它的Journal必须可读；未开始副作用且已拒绝允许Artifact=null，已写effect intent后成功/Partial/Failed/Unknown都必须保存可读journal，若存储不可达则Result Unknown并按原identity回查，不能生成假Artifact。Backup成功还含Closure/RestorePoint，Recovery成功含Closure/RestorePoint/Recovery，GC含Plan；具体引用Creator可不同，read按各link.Creator验证。对账续作必须用原operation及旧plan/codec，读这些API绝不自动Seal/清理/恢复。

Database/File新增维护原语只供组合器：ApplyMigrationStep仅执行指定注册StatementCatalog及Validation，CreateBaseBackup输出有界Parts和准确开始/结束身份；ReadCut须传入本次baseStart/baseEnd和BackupCut全集token，核SystemId/ServerMajor/ToolVersion与当前集群及BackupProfile一致，再返回Target和从baseStart延伸到目标的RequiredWal/TimelineHistory，包含baseEnd且工具确认已归档、缺段不成功；不从静态缓存猜base身份。恢复目标必须匹配IsolatedTarget且两类workers均disabled。ValidateOwnerAsync仅在隔离目标执行登记Owner.ReadValidation的只读有限映射，核实体/引用完整性；没有正式验证实现→NotRestorable，不改业务行、不发Outbox。ApplyGc只允许Quarantine/Delete，核原PhysicalIdentity/fence/alias保护和durable intent后返回Confirmed/NoEffect/Unknown，不自选对象。Copy/Restore/Verify只按已封口Part定位，不接任意path。Effect Confirmed时Fault=null，NoEffect含Fault（保护跳过GcBlocked），Unknown含CommitUnknown，均等本地IO释放才返回。BaseBackup成功Parts非default、Start/End非null且WAL合法，失败Empty/null/null/Fault；Cut成功Target非null/RequiredWal非default，失败null/Empty/Fault。checkpoint在原journal，不交半份成功。目录Open二选一，页固定snapshot/epoch、有界且取消真释放，失败Empty/Next=null，Missing/Unknown不当空目录。PendingPublication和不满足OrphanGracePeriod不得GC。

上段NoEffect含Fault适用于执行原语；只读ProbeEffect的NoEffect/null是§6.3已证明未发生的唯一例外，调用者不可混用。每个MaintenanceSnapshot计数/Kind/State/AtUtc与对应Receipt一致，Attempt与Evidence一致；Creator/Journal.Creator始终是本次原identity。Plan按Kind仅允许MigrationPlan、GcPlan或BackupWork；恢复通过Closure/RestorePoint追溯原来源，Recovery.Creator仍为本次Restore/VerifyRecovery identity。Backup计数按全部Part，Migration按step，Recovery按必需Part与每个Owner.ReadValidation各一项聚合，不按journal条数/attempt计数；Unknown优先，所有必需项确认才成功。无effect的Rejected/Blocked不伪造已完成项。

Recovery.RequiredCount=checked(RestorePoint.RequiredItems+Closure.Owners.Length)，其页包含全部必需Part及每个登记Owner的只读验证项；验证项Object=null、Verification=Owner.ReadValidation、ExpectedBytes=0、ExpectedHash=SHA-256(Empty)，ItemId用有界注册OwnerKey+固定前缀生成且与Part项不重复。这是只读验证标记，不是实体数据摘要；Verified来自ValidateOwnerAsync实际结果。迁移成功所有step确认（AlreadyCurrent只在原to schema/完整history校验通过时全0），备份成功所有Part确认；失败/未知及未执行项逐项保留，不以总数替代journal。CopyBackupPart的Confirmed包含目标实际字节长度/hash读回，不能只证复制调用返回；格式验证按Part.Format注册。

具体组合器构造签名在Runtime冻结为`StorageMaintenanceBackend(ResolvedStorageConfiguration configuration, IStorageDatabaseBackend database, IStorageFileBackend files, IStorageReferenceCoordinator references, IStorageAssetBackend assets, IStorageClock clock)`，实现IStorageMaintenanceBackend。BackendFactory先建Database/Files/References/Assets再用这些实例构造它；其Dispose只等自己工作结束、不Dispose注入的兄弟实例，整体所有权属于Runtime。A3只用此类及A1/A2，不新增包。A1/A2在自己包实现上述Database/File接口；Host组合的IStorageBackendFactory按已绑定VersionRef解析可信连接/路径，原生配置仅在适配器内部，不透到Contracts。不存在的物理Profile/Owner内容只阻对应外部接入。

### 6.5 封闭错误与能力目录

StorageFault的Code/DiagnosticKey只能采用以下配对。None不能实例化Fault；用户文字由Host三语资源按key投影，provider exception/SQL/path不透出。已知错误优先于泛化Unavailable；缺数据/权限不能伪装NotFound或成功空集合。

| StorageError | 唯一DiagnosticKey | 含义与恢复 |
|---|---|---|
| InvalidInput | `storage.invalid_input` | shape/codec/schema/范围不符，改输入；不补默认值 |
| UnsupportedVersion | `storage.unsupported_version` | 未注册版本，提供精确目录/包 |
| PermissionDenied | `storage.permission_denied` | 当前授权拒绝，联系权限Owner |
| Conflict | `storage.conflict` | 原身份/内容或CAS冲突，查原操作 |
| ResourceBusy | `storage.resource_busy` | Session已有工作，等原任务结束 |
| CapacityExceeded | `storage.capacity_exceeded` | 额度/页/空间超限，按Profile背压 |
| Unavailable | `storage.unavailable` | 后端/目录不可达，恢复连接后原身份回查 |
| IntegrityFailed | `storage.integrity_failed` | 描述/字节/manifest不一致，隔离用途 |
| MigrationBlocked | `storage.migration_blocked` | schema/history/fence不符，按原plan核验 |
| GcBlocked | `storage.gc_blocked` | 引用/保持/resolver/epoch不确定，保留对象 |
| NotRestorable | `storage.not_restorable` | 必需闭包/WAL/key/目标不满足，保留源备份 |
| Cancelled | `storage.cancelled` | 合作取消已确认；未排空仍保留任务 |
| TimedOut | `storage.timed_out` | 等待或执行预算到期，不推断commit回滚 |
| CommitUnknown | `storage.commit_unknown` | 事务/封口/维护事实未知，按原身份查询 |
| DrainIncomplete | `storage.drain_incomplete` | 真实释放未确认，保留借用/Task |
| InstanceMismatch | `storage.instance_mismatch` | 旧实例handle，耐久查询用新Runtime |
| ResultExpired | `storage.result_expired` | 资产/墓碑过保证期，不复用旧key |

唯一兼容例外是§10分类Failed使用Unavailable/`storage.save_not_completed`，它仅表示保存未完成、不推断根因；IO不得使用它替代已知错误。Journal Skipped采用GcBlocked/`storage.gc_blocked`说明保护条件；诊断事件不构成Fault，封闭事件键为`storage.accepted/running/draining/drained/resources_released/completed/diagnostic_gap`，其State必须对应。Barrier/codec非预期异常转Unavailable并继续排空，原异常只进受控宿主日志。

能力目录冻结为`storage.runtime_create/session_open/transaction/read/file_write/file_read/file_verify/hold/hold_renew/gc_plan/gc/migrate/backup/restore/verify_recovery/maintenance_resume/operation_read/task_read/resource_read/maintenance_read/diagnostics/health/runtime_stop/resource_release`（均完整带`storage.`前缀）。入口对应同名能力；OpenSession还核Owner/Purpose，资源查询/释放还核实际Handle归属，operation/assets还核原Creator/全部数据范围。StorageAccessDecision Allowed=true时Fault=null，false时PermissionDenied；authority自身不可用转Unavailable，绝不当允许。ReferenceCoordinator和Backend不能扩大Runtime已核范围。



### 6.6 模块技术存储形状与写入权威

以下是IM-066自身技术Schema，不是任何Owner业务表。A1迁移包拥有独立`im066` schema，runtime角色无DDL/owner权限， tenant RLS和全键关系按§4；物理SQL/索引迁移在A1实现此精确逻辑形状，不要求领域Owner设计技术表。公开类型都序列化为§6固定canonical bytea，业务图像/原始数据不进入这些bytea。所有hash存32byte、VersionRef存id/revision/hash三列，Scope展开五ID列、IDs为受限非空text，generation/sequence/counters为bigint非负，UTC为timestamptz，enum为int带CHECK允许域，长寿命schema不得按业务月份拆。

| 表/唯一键 | 最小字段与含义 | 唯一写入/原子边界 |
|---|---|---|
| `operation_route`；PK=(tenant,store,generation,owner,idempotency)，另UK=(tenant,store,generation,operation_id) | 完整Scope/OperationIdentity、Kind、RuntimeProfile/SemanticVersion、registered_utc、writer_epoch/fence、evidence_head_revision、current_attempt（初值均0） | Database.Register CAS；身份/Kind/版本不可改，当前writer/fence、attempt和证据head只按§6.3授权CAS更新，不能更新历史请求 |
| `operation_attempt`；PK=(route键,attempt)，resume另UK=(route键,expected_attempt,journal_id/revision/hash) | 首次attempt=0；后续保存原Journal link、原请求语义hash、writer epoch/fence、执行状态及UTC | BeginMaintenanceResume同事务CAS current_attempt/head后插入；同attempt同输入只读重放，异输入Conflict；不删除未决attempt |
| `operation_receipt`；PK=(route键,evidence_revision)，FK route/attempt | kind、StoredOperationState、result_schema、canonical_receipt、fault code/key、at_utc、writer_epoch/fence、attempt、Journal/Maintenance link | revision从1递增；Transaction首次证据与Owner业务写/对象引用同事务追加；文件/维护由原journal对账追加。追加行与route head的ExpectedRevision CAS同事务，不覆旧行 |
| `object_catalog`；PK=ObjectKey五字段 | 完整ObjectRef、durability_profile、PhysicalIdentity、file_state、write_operation_id、unreferenced_since_utc、pending_publication、last_fence | File后端单写/fence封口journal确认后登记；记录不存在不证明字节不存在，响应未知回原identity核验。`last_fence`固定为`bigint NOT NULL DEFAULT 0 CHECK (last_fence>=0)`，只由对应PhysicalIdentity/原seal的受保护CAS更新，不能用当前epoch数值替代或回退 |
| `owner_object_reference`；PK=(tenant,store,generation,owner,entity_id,entity_version,ObjectKey) | 完整ObjectRef、绑定版本、owner事实引用、reference_epoch | A1同Owner事实事务写；Owner business release/retention有已注册事务才移除，不由GC/读口改业务行 |
| `reference_authority`；PK=authority_id | authority_epoch、next_fence、reference_epoch、approved_catalog | Coordinator事务锁/CAS，fence严格递增；进程消失不自动重置，旧writer必须fenced |
| `object_protection`；PK=protection_id，UK=(original_identity,action,item集合hash) | kind、完整scope/object集合、owner/backup/Legal Hold来源ref、reserved/bound状态、AssetLink、writer_epoch/fence、到期及未决标志 | Coordinator.Preserve/CAS，引用/GC判定在同协调锁域；临时lease与durable保护分开，Unknown不TTL删 |
| `asset_snapshot`；PK=(tenant,store,generation,asset_id,revision) | StorageAssetSchema、完整Creator、digest、header canonical、entry_count、canonical_bytes、created_utc、retention状态 | Assets.Seal原子完整发布，hash不自引用；同ID/revision异hashConflict |
| `asset_entry`；PK=(snapshot键,sequence)，FK snapshot | exact schema entry canonical/hash及bytes | 与snapshot同事务写，封口后不可变；page按sequence keyset，单snapshot一致，不能静默缺号 |
| `operation_journal_head`；PK=original identity | last immutable Journal link、MaintenanceSnapshot link、writer_epoch/fence、unfinished标记 | 单writer CAS追加revision，再原子更新head；current link只是定位，读旧资产必须指定旧hash |
| `schema_history`；PK=(plan_id,revision,step_id)，checksum不可变 | from/to schema、step hash、phase、fence、validation/compensation ref、UTC | 事务step与DDL同commit；非事务step先durable intent后执行/读回确认，保留invalid/Unknown |

所有effectIntent参数必须是Assets中已耐久封口JournalV1的精确link，Creator等于当前operation且含对应item/action的EffectIntent；GC另核candidate PhysicalIdentity及物理协调fence。ApplyMigrationStep对应MigrateStep/Backfill，CreateBaseBackup/CopyBackupPart对应BackupCopy，RestoreDatabase/RestorePart对应RestoreCopy；后端核该意图和当前Operation writer token，File.ApplyGc还核当前对象保护。不得先发effect再补意图；确认结果后追加新Journal修订及head，读旧link仍是原快照。维护组合器有独占database/phase日志，失败/Unknown保留head和原plan；新Runtime只读回查，继续副作用须当前维护授权、原请求摘要、明确的恢复入口及fencing，不能由Query或普通Created=false重放暗启，也不能启动设备或外发。跨库引用/不参与同一Coordinator的外部Owner拒GC/完整cluster闭包，正常保存/只读按已注册能力继续。

Backup物理身份的SystemId/LSN为UInt64，不在PG bigint截断；A1存为精确numeric(20,0)并CHECK 0..18446744073709551615（SystemId>0），timeline用bigint约束1..4294967295。canonical仍UInt64/UInt32。actor/凭据/实际路径不存公开canonical；从可信ref在适配器内部解析。维护资产嵌套tuple/数组预算按Profile，事务没空间写intent/receipt时先拒操作，不能成功后丢证据。

### GC 并发删除的线性化约束（Integration）

GC 的 dry-run 计划必须冻结 retention snapshot 的 ID/version/hash、reference epoch、候选对象的精确身份及摘要、批准的保留/Legal Hold 投影、操作身份和计划摘要。计划只能提供候选项，不授权删除。执行前取得针对该计划的独占、不可复用 quarantine lease/fence；每个对象在移动到隔离区或物理删除前，均须在同一引用协调边界重新确认仍无活动引用、写入/读取/导出 lease、备份/调查保持或 Legal Hold，且 reference epoch 和保护策略仍有效。此检查与该对象进入隔离/删除资格之间必须线性化；实现可采用共享锁/代际、事务性 MVCC 或等价机制，但不得留下“复核后新引用先提交、GC 后删除”的窗口。无法取得协调权、resolver 异常、版本变化、状态未知或协调 lease 失效时，受影响对象不移动、不删除，返回逐对象 `GcBlocked/Unknown`。

隔离/删除必须按对象写入耐久、可恢复的 journal，记录原物理代、计划与快照绑定、lease/fence、每次移动/删除结果。并发引用或保护条件在执行前变化时跳过该对象并保留字节；部分失败返回准确的逐对象结果，不把整批报告为零失败或完全成功。进入隔离后、物理清除前还须重验当前引用与保持；若删除请求已发出但结果未知，保持隔离并按原 GC operation 查询，禁止重新开放、改指向另一个物理对象或以新 operation 重复删除。重启恢复只续作/核验原 journal，不依据文件年龄或进程消失推定安全。对相同内容摘要的别名 `ObjectId/ArtifactId` 必须合并到同一可达性判断，不能因某个别名无引用就删除仍由其它别名引用的内容。

两次扫描一致、Bloom filter、缓存引用计数或过期的引用目录只能用于筛选/加速，不能单独构成并发安全证明。若所有引用 Owner 无法参与同一协调协议，GC 必须 fail closed 并保持对象；不得以延长扫描间隔或重扫次数代替协调。此处冻结并发安全语义；引用目录、后端协调者和物理耐久须在对应适配切片接收，无法参加同一协议的 Owner 只阻断该存储域的 GC。

本节借鉴用户提供的 `H:\docs` 中 `40-development/60-data/通用数据平台DLL开发指导.md` 的 `IFC-MOD-DATA-GC`、`IFC-MOD-DATA-RETENTION` 及“CAS GC竞态/并发保护”约束（审查输入 SHA-256：`331F71E883A1B13F1672DC86EA78F2DB94C078E2906DDA44F37DA87CD2FD2148`）。只吸收适用于独立存储模块的引用闭包、并发线性化、隔离恢复和别名可达性语义；不采纳其 AOI 业务表、SQLite/RPO=0、Parquet、具体错误码或未冻结 API。


### 可恢复文件写 claim 的身份与恢复边界（后续 Integration 条件）

v0.3交付有同请求单写/fence、耐久stage/封口journal、重启后的原identity只读回查；不交付跨请求分块续传或续用已关闭源流，故无claim上传/续传API缺口。下面是来源提炼的未来Integration约束，只有正式扩展范围时适用，不作为当前C1/A2开工待办。若未来引入可续传claim，稳定身份绑定存储域、对象、原摘要/预期描述，用获批单写/fence阻止迟到写者；staging由可信身份派生，准确重放读取原状态而不消费新流。扩展需另升Contract并在本指导冻结续传API/预算，不由当前实现者暗增。

恢复必须查询并续作原 claim 身份。只读检查不得暗中补元数据、清理暂存或重启上传；仅发现相同内容 hash 的对象，只能证明该内容对象存在且可验证，不能单独证明原 claim 已完成、原写者已退出或其操作回执已终结。TTL 到期、进程号消失、文件年龄、取消请求或一次 `NotStarted` 观察都不能证明原写者停止。`Incomplete/Unknown` 时保留原 claim 与相关字节，不以新身份重试或释放仍可能被使用的资源。只有能证明原写者和底层 IO 已停止、对象未发布且仅属于该 claim 的暂存已清理，并已持久化阻止迟到写入的终态后，才可报告 `Aborted`；已发布的不可变对象不得因 claim 结算失败而删除。

本约束提炼自用户提供的 `H:\docs` 中 `40-development/60-data/通用数据平台DLL开发指导.md` 的 `CAS-CLAIM-RECOVERY-01`（审查输入 SHA-256：`331F71E883A1B13F1672DC86EA78F2DB94C078E2906DDA44F37DA87CD2FD2148`）。仅吸收可恢复写入的原身份、单写者/迟到写保护和不确定状态保留语义；不采纳其 AOI 容量预约、SQLite 结算、具体合同/API、实现路径或源码状态。



### 6.7 A1/A2/A3 真实适配装配规格

本节新增真实适配切片的装配规格，不改§6.3–6.6及§10已接收的C0/C1语义。唯一数据库路线为PostgreSQL 18 + Npgsql 10.0.3；Npgsql是驱动，直接使用其DataSource、池、command、transaction，不另造连接池、SQL helper、ORM透传或查询DSL。图像/点云等字节仍只进受控硬盘/NAS。以下公开声明是尚未实现的A1/A2启动面，不表示已有程序集；普通消费者仍只调用§6端口，不取得启动文档、密码、SQL、连接、Reader、物理路径或provider exception。

#### 6.7.1 可信引用、解析和启动输入

以下新增窄端口在Contracts，仅供受信任Host启动装配和适配器之间使用；C1 fake不要求实现它们。所有依赖显式注入，不从环境变量、当前目录、注册表、默认连接串或请求解析物理配置。

```csharp
public enum StorageTrustedDocumentKind {
    Endpoint, TlsPolicy, AuthorityTopology, Credential, Root, AccessPolicy,
    StatementCatalog, TechnicalSchema, MigrationValidation, BackupTool,
    BackupDestination, IsolatedDatabase, IsolatedFiles, KeyMetadata
}
public sealed record StorageAdapterBootstrapLimits(int MaxDocumentBytes,
    int MaxDocuments, long MaxTotalDocumentBytes, int MaxJsonDepth, int MaxCredentialChars);
public sealed record StorageAdapterOpenContext(long StartedAtTimestamp, TimeSpan StartupBudget);
public interface IStorageTrustedDocumentSource {
    ValueTask<Stream> OpenAsync(VersionRef version, StorageTrustedDocumentKind kind,
        int maxBytes, CancellationToken ct);
}
public interface IStoragePhysicalGuard : IAsyncDisposable {
    ResourceHandle Handle { get; }
}
public sealed record StoragePhysicalGuardOpenResult(IStoragePhysicalGuard? Guard,
    StorageFault? Fault);
public interface IStoragePhysicalGuardProvider : IAsyncDisposable {
    ValueTask<StoragePhysicalGuardOpenResult> AcquireAsync(
        StorageCoordinationRequest request, CancellationToken ct);
}
public sealed record StorageFileCatalogRecord(ObjectDirectoryEntry Entry,
    FileObjectReceipt Receipt, VersionRef SealJournal);
public sealed record StorageFileCatalogReadResult(StorageFileCatalogRecord? Record,
    StorageFault? Fault);
public interface IStorageFileMetadataBackend {
    ValueTask<StorageFault?> PublishAsync(StorageFileCatalogRecord record,
        StorageCoordinationToken writeToken, BackendExecution execution, CancellationToken ct);
    ValueTask<StorageFileCatalogReadResult> ReadAsync(CallContext context, ObjectRef obj,
        CancellationToken ct);
    ValueTask<OperationQueryResult> ReadOperationAsync(OperationQuery request,
        CancellationToken ct);
    ValueTask<ObjectDirectoryOpenResult> OpenDirectoryAsync(CallContext context,
        StorageCoordinationToken token, int maxEntries, int maxBytes, CancellationToken ct);
    ValueTask<StorageFault?> RecordGcAsync(GcCandidateV1 candidate, JournalAction action,
        StorageAssetLink effectIntent, OperationIdentity identity,
        StorageCoordinationToken token, BackendExecution execution, CancellationToken ct);
}
```

DocumentSource由Host登记有限exact `(Kind,Id,Revision,Hash)`→只读文档，不接自由地址；请求中的ref不能扩展登记集。返回非null可读流后所有权交给该次适配工厂；工厂单次读取最多MaxDocumentBytes+1以检测超限，完成/失败/取消均Dispose原流后才返回。source未交付前负责自己的清理，不后台交付迟到流；原Open Task由启动Owner保持。适配器核SHA-256等于VersionRef.Hash，才用System.Text.Json解析严格UTF-8 JSON：拒重复/未知字段、注释、尾逗号、额外根、非有限/越界数字及过深嵌套。hash绑定原始文档字节，空白变更也需新ref，不另猜canonical。目录文档都带`kind/id/revision`，必须等于请求；嵌套ref为`{id,revision,hash}`并按同规则解析。限额为有限正值，MaxDocumentBytes<Int32.MaxValue且≤MaxTotalDocumentBytes，MaxCredentialChars≤MaxDocumentBytes；每次启动去重并计文档数/总原始字节，A1/A2预算合计由Host纳入§7.1.1预留。不得拿hash匹配代替可信来源/当前授权。解析后私有不可变工作值不保存原Stream；禁止自动建根、建库、迁移、生成凭据或下载证书。

| Kind / 引用来源 | 严格payload字段及私有解析结果 | 拒绝/验证规则 |
|---|---|---|
| Endpoint / Relational.Endpoint | `host,port,database`；单一DNS主机、1..65535端口及非空库名 | 本版装配只支持单权威端点；不接多host列表、自由连接串、Unix socket或自动failover；HA须另获明确子切片，不能静默选主 |
| TlsPolicy / Relational.TlsPolicy | `serverName,rootCertificateDerBase64`；精确服务器名及一张有界DER根证书 | serverName=Endpoint.host；固定VerifyFull，证书解析失败拒绝；不接任意验证callback或关闭主机名/链验证，未提供客户证书的部署不得猜mTLS |
| AuthorityTopology / Relational.AuthorityTopology | `authorityId,mode,endpoint,systemId,epochPolicy,reservedConnectionSlots`；mode=`SinglePrimary`，endpoint exact ref，systemId为UInt64十进制字符串，epochPolicy=`PersistentFence`，reservedConnectionSlots为非负Int32 | authorityId=References.AuthorityId；actual system id/PG18/read-write主库必须匹配；连接成功不证明旧writer终止，缺fencing结论保留Unknown |
| Credential / 源Relational.Pools、IsolatedDatabase.pool或BackupTool.backupCredential | `principal,secretVersion,purposes,roleKind`；secretVersion为可信ref，purposes为去重PoolPurpose集合，roleKind为Runtime/Migration/Backup/IsolatedRead | 凭据描述不含密码/hash(password)；principal与秘密租约实际身份相同。**源Relational**的Production/Query/Recovery为Runtime，Maintenance为Migration；**隔离target**的Recovery为IsolatedRead；物理备份工具用独立Backup角色（REPLICATION、非superuser）。用途与目标必须同时匹配下表，不能只看PoolPurpose；换secret代必须新描述/ref，不在途热替换 |
| Root / FileProfile.Root | `absoluteRoot,rootIdentity,authorityId,layoutVersion,transport,lockSemantics,durabilityEvidence`；rootIdentity及durabilityEvidence为ref，layoutVersion=`IM066-FILES-1` | rootIdentity绑定卷/根实际句柄身份；transport为`LocalWindows`或`QualifiedSmb`，lockSemantics=`WindowsShareModeV1`；无验证记录不能把SMB锁或FileDurability当已验证；未知NAS拒该写/GC装配，不能降级本地内存锁 |
| AccessPolicy / FileProfile.AccessPolicy | `authorityId,root,writerPrincipals,readerPrincipals,denyReparse,denyRootReplacement` | root exact、主体数组有限去重，两个deny均true；ACL由部署预置，工厂只核验不改ACL；只读身份也须获专用locks目录权限，不能因此获对象修改权 |
| StatementCatalog / Binding.StatementCatalog | `ownerKey,binding,codec,commands`；commands顺序固定，每项`kind,sql,parameterTypes,resultColumnTypes,maxRows,maxBytes`，kind为Read/Mutation | SQL/标识符只来自可信文档；仅位置参数，类型从下文封闭集选择；命令/行/字节上限≤Binding/Profile；拒任意请求SQL/动态表名，拒额外IO和未登记映射 |
| TechnicalSchema / Relational.TechnicalSchema | `schemaVersion,minimumReader,minimumWriter,migrationPackage`（后三者为ref） | 启动只读验证§6.6技术表/约束/RLS及history checksum；缺schema拒绝，不用Create绕开迁移流程 |

Root的实际绝对路径只存在A2私有解析对象；Endpoint及秘密只存在A1。上述文档是配置序列化，不是第二套业务契约；生产字段值须由部署提供，软件夹具可提供独占测试值。ReferenceResolvers、格式validator、Owner codec/SQL/Schema内容仍由各正式Owner登记，不能凭技术工厂补成客户事实。

Recovery精确装配分为以下两类，不新增PoolPurpose/roleKind或公开DTO。私有数据源键唯一为`(目标种类Source/Isolated, 精确Endpoint VersionRef, 目标Profile VersionRef, PoolPurpose, roleKind, 精确Credential VersionRef, 精确secretVersion)`；Source目标Profile取Relational.Version，Isolated取StorageIsolatedTargetProfile.Version。同Purpose、principal甚至相同host仍不得合池，Isolated endpoint/dataRoot身份与生产重合按既有规则拒绝；任何字段变化建立新受管代并计新旧预算，不在原池SET ROLE、换目标或借更高权限池。

| Recovery池 | 精确角色/权限和执行范围 | 核验与拒绝 |
|---|---|---|
| 源权威Recovery（Relational.Pools） | roleKind=Runtime、purposes含Recovery；非superuser/非Owner/无BYPASSRLS/无REPLICATION/无迁移角色membership。只允许按当前scope的注册技术route/receipt/head/Schema状态只读回查；原受管恢复worker明确获权时，可使用已冻结Register/AppendEvidence/BeginResume及协调/protection技术CAS，不能执行Owner领域mutation、DDL、COPY、物理工具或目标恢复 | 每次Open实际session_user/current_user须等于凭据principal且不可通过membership升权；源Endpoint/TLS/system id/PG18/read-write权威及im066最小SELECT/固定技术mutation权限/RLS按用途核验。Query入口仍零写；查询本身开READ ONLY事务，受管技术CAS另开明确READ WRITE事务，不把Query调用升级成对账执行 |
| 隔离target Recovery（IsolatedDatabase.pool） | roleKind=IsolatedRead、purposes必须恰为[Recovery]；非superuser/非Owner/无BYPASSRLS/无REPLICATION/无源Runtime/Migration/Backup membership。只有已注册完整恢复范围所需SELECT、Schema/引用完整性只读验证及批准的只读技术观测；无INSERT/UPDATE/DELETE/DDL/COPY写/序列写/外发函数权限，不调用任何源库技术CAS | 工厂先核target/endpoint/credential/ref及静态角色映射；尚未启动目标时不能假称动态核验已过。目标就绪后首借连接核实际身份/角色/membership/ACL、源备份SystemId及准确timeline/LSN、hot_standby/read-only/pause状态，再每次用READ ONLY事务。有任一写权、未登记验证或范围不足→NotRestorable；目标不可达/权限无法确认→Unavailable，不能借源Recovery/Production补足 |

上述权限是同一IStorageAuthority批准范围下的数据库最小授权要求，不授隔离校验角色跨租户生产读取；Owner.ReadValidation及技术观测目录必须覆盖且仅覆盖Closure正式登记范围。实际角色不符为PermissionDenied，精确配置版本不符为UnsupportedVersion，源/目标身份冲突为Conflict；返回固定§6.5键。用途池与目标池各自独立队列/连接额度、原Task及真实排空，停止target不取消源回查，停止源池也不把隔离服务误报已释放。

A1 namespace `Asun.Platform.StorageDatabase.PostgreSql` 的秘密/绑定入口冻结如下；只为启动注入，不由业务请求构造。参数和结果marshal不是通用SQL抽象：SQL及执行顺序始终固定在可信StatementCatalog，codec不获得连接/transaction/Reader、不决定SQL、不做IO。

```csharp
public interface IPostgreSqlCredentialSource {
    ValueTask<PostgreSqlCredentialLease> OpenAsync(VersionRef secretVersion,
        int maxChars, CancellationToken ct);
}
public sealed class PostgreSqlCredentialLease : IAsyncDisposable {
    // 实现为不透明实例，构造器private；没有公开密码/连接串/ToString载荷。
    public static PostgreSqlCredentialLease Create(VersionRef secretVersion,
        string principal, ReadOnlyMemory<char> password, int maxChars);
    public ValueTask DisposeAsync();
}
public sealed record PostgreSqlCommandResult(int CommandIndex, int AffectedRows,
    ImmutableArray<ImmutableArray<object?>> Rows);
public interface IPostgreSqlBindingCodec {
    VersionRef Version { get; }
    VersionRef InputSchema { get; }
    VersionRef ResultSchema { get; }
    ImmutableArray<object?> GetParameters(int commandIndex,
        ImmutableArray<byte> canonicalInput, StorageInputLimits limits);
    ImmutableArray<byte> EncodeResult(ImmutableArray<PostgreSqlCommandResult> commands,
        int maxResultBytes);
}
```

CredentialSource只允许Host已登记的secretVersion，Open/Create的maxChars固定取Bootstrap.MaxCredentialChars；maxChars≤0、密码超限/default/非法描述在复制前拒绝，source自身也不得先无界物化秘密。租约内部保存exact版本/主体及独立有界password字符副本；A1核描述后用于固定DataSource，不向Runtime结果/异常暴露。source仍归Host，交付的租约归PG group，在全部DataSource/借用连接排空后一次Dispose并清可控buffer。Npgsql所需string仅在A1内部生成，不承诺CLR/驱动string可原地擦除；禁日志、连接串ToString、IncludeErrorDetail及参数日志。无在途凭据轮换；新配置代另开Runtime时新旧池合计仍计预算。租约失败/取消真实清理再返回，无秘密值写入VersionRef或canonical receipt。

StatementCatalog.codec exact匹配注入codec.Version及Binding输入/结果Schema。parameterTypes/resultColumnTypes封闭为`Boolean,Int32,Int64,UInt32,UInt64,Decimal,Text,Bytea,Uuid,UtcTimestamp`，null值按登记PG类型发送DBNull；UInt32/UInt64映射numeric并查合法域，不溢出转long。其它运行值只能是对应BCL bool/int/long/uint/ulong/decimal/string/byte[]/Guid/DateTimeOffset（UTC）；default数组/异类型拒绝。bytea只承载已登记有限技术/Owner元数据，不能装图像/点云等证据。参数数目/结果列数须exact；值深拷贝和大小核查先于command/行分配；Reader先检查列类型及长度，再有界物化BCL值。Read命令无变更行，AffectedRows固定0；Mutation用实际非负RecordsAffected，checked总和须在Binding.MinAffectedRows/MaxAffectedRows内，未确认行数拒绝成功。返回Rows只到codec，结果经既有ResultCodec.Validate后commit；超限整体回滚，不交半页。Read Binding的全部命令须Read且用只读事务，禁止写命令、DDL和任意security-definer；SQL审核/RLS行为验证归该Owner注册包验收，不以字符串关键字筛查当安全证明。

#### 6.7.2 具体工厂、五实例和所有权

公开构造/创建签名按表落在既有A1/A2包，不新增DLL，也不改Runtime→Core/Contracts依赖。`OpenBudget`为正有限TimeSpan，各阶段实际期限为此上限与本次StartupBudget剩余值的较小者；整个组合只用调用传入的同一Clock、同一StorageAdapterOpenContext，不每阶段刷新。StartupBudget必须等于configuration.Profile.Runtime.StartupBudget，StartedAtTimestamp由组合Owner首次Open的Clock.GetTimestamp取得；每次启动新阶段前用同Clock.GetElapsedTime扣除已耗时，非正剩余不进入新分配。该context只在受信任装配面，不改已冻结IStorageBackendFactory签名。没有内部静态配置或第二Clock。

```csharp
// Asun.Platform.StorageDatabase.PostgreSql
public sealed record StoragePostgreSqlFactoryOptions(
    StorageAdapterBootstrapLimits Bootstrap, TimeSpan OpenBudget);
public sealed class StoragePostgreSqlBackendFactory {
    public StoragePostgreSqlBackendFactory(IStorageTrustedDocumentSource documents,
        IPostgreSqlCredentialSource credentials, ImmutableArray<IPostgreSqlBindingCodec> codecs,
        StoragePostgreSqlFactoryOptions options);
    public ValueTask<PostgreSqlBackendGroup> OpenAsync(ResolvedStorageConfiguration configuration,
        IStoragePhysicalGuardProvider physicalGuards, IStorageClock clock,
        StorageAdapterOpenContext startup, CancellationToken ct);
}
public sealed class PostgreSqlBackendGroup : IAsyncDisposable {
    public IStorageDatabaseBackend Database { get; }
    public IStorageReferenceCoordinator References { get; }
    public IStorageAssetBackend Assets { get; }
    public IStorageFileMetadataBackend FileMetadata { get; }
    public ValueTask DisposeAsync();
}
// Asun.Platform.StorageDatabase.FileSystem
public sealed record StorageFileSystemFactoryOptions(
    StorageAdapterBootstrapLimits Bootstrap, TimeSpan OpenBudget);
public sealed class StorageFileAuthority : IStoragePhysicalGuardProvider {
    // 构造器private；只能由下述OpenAuthorityAsync创建。
    public ValueTask<StoragePhysicalGuardOpenResult> AcquireAsync(
        StorageCoordinationRequest request, CancellationToken ct);
    public ValueTask DisposeAsync();
}
public sealed class StorageFileSystemBackendFactory {
    public StorageFileSystemBackendFactory(IStorageTrustedDocumentSource documents,
        StorageFileSystemFactoryOptions options);
    public ValueTask<StorageFileAuthority> OpenAuthorityAsync(
        ResolvedStorageConfiguration configuration, IStorageClock clock,
        StorageAdapterOpenContext startup, CancellationToken ct);
    public ValueTask<IStorageFileBackend> OpenAsync(ResolvedStorageConfiguration configuration,
        StorageFileAuthority physicalGuards, IStorageReferenceCoordinator references,
        IStorageFileMetadataBackend metadata, IStorageClock clock,
        StorageAdapterOpenContext startup, CancellationToken ct);
}
```

工厂类/Group声明中的方法体由后续实施任务提供；没有公开Group/Authority构造器。PG group拥有每用途唯一DataSource、秘密租约、Database/References/Assets三包装及FileMetadata窄桥；三包装共享这组池，不建立三组池。FileMetadata借用group，不是BackendSet第六实例，不独立Dispose，不被其它Runtime复用。Database.DisposeAsync与Group.DisposeAsync复用同一原Task，是整组最后释放锚；References/Assets.Dispose只禁止自己新调用并排空自身，不释放兄弟或DataSource。group最终等待所有包装/窄桥/物理guard借用结束，逆序关闭DataSource后释放秘密；某一步失败仍尝试其它已排空资源，保留各原cleanup Task，未释放不报完成。

OpenAuthority只打开已预置、身份/ACL/布局合格的根和锁命名空间，零业务effect。PG Open借用该Authority，不拥有/Dispose它；三个PG包装和窄桥只借用同一Clock/已解析快照。File Open借用PG References/FileMetadata；**只有成功交付File backend时**根Authority所有权才转给Files，失败由本次工厂先清自己的部分文件句柄，Authority仍归组合Owner。Files.Dispose等全部本地IO及Authority的guard借用结束，随后一次Dispose Authority；PG References必须在Runtime停止/drain阶段已交回所有guard，Dispose包装不再Acquire或发新effect。由此沿既有Runtime顺序Maintenance→Assets→Files→References→Database，Files能先关根而不遗留PG访问根的借用；未交回guard时Files保持原Dispose Task等待，不能强关锁。五实例均为本次Open独占，禁止Host单独提前Dispose某个包装。

Host私有组合类名冻结为`PostgreSqlFileBackendFactory : IStorageBackendFactory`（不发布为模块包），公开构造器仅为`PostgreSqlFileBackendFactory(StoragePostgreSqlBackendFactory databaseFactory, StorageFileSystemBackendFactory fileFactory)`。两独立Host各自在自身组合根实现该类；它无SQL/文件算法，只按下面顺序装配。所有子Open的原Task保存在这一次Open的有界Owner内，ValueTask转Task一次；整个Open被§7.1.1的原Create/HostTask强持。

1. 首次Open读取同一启动Clock戳并构造`startup = new StorageAdapterOpenContext(clock.GetTimestamp(), configuration.Profile.Runtime.StartupBudget)`，校验options/Resolved/Profile/目录限额；`fileFactory.OpenAuthorityAsync(configuration, clock, startup, ct)`→保存唯一Authority。随后`databaseFactory.OpenAsync(configuration, authority, clock, startup, ct)`→保存唯一PG group。随后`fileFactory.OpenAsync(configuration, authority, group.References, group.FileMetadata, clock, startup, ct)`→保存Files并转根所有权。每阶段合作token仅缩短原deadline，取消/释放观察不重新刷新startup。
2. 用已冻结`new StorageMaintenanceBackend(configuration, group.Database, files, group.References, group.Assets, clock)`构造唯一Maintenance；依次形成`new StorageBackendSet(group.Database, files, group.References, maintenance, group.Assets)`，健康/完整集合核验后才一次交付Runtime。配置/工厂/Clock/Barrier/当前IStorageAuthority均仍归Host；PG/A2不另造权限事实。部分创建状态只保存在此Open Owner，不向业务消费者返回半个Set。
3. 成功前任何失败/取消先关接纳、等原子Open真实结束；迟到Authority/group/Files先保存并接管再清理，不丢弃。按创建逆序Maintenance→Files→PG group→尚未转移的Authority释放；未构造者跳过，转移给Files的Authority不得第二次Dispose。PG group内部仍按Assets→References→Database锚排空；Files清理前先确认所有PG工作/guard借用已结束。无任务执行的初始化失败不存在生产lease，健康探测的原Reader/guard也必须先排空。
4. 每资源仅启动/保存一次Dispose原Task；取消不传给Dispose。后面的已排空兄弟资源清理以嵌套finally继续，但不能在一个IO尚借用兄弟时抢先关兄弟。异常与cleanup异常分别保留，公开最终只抛固定StorageInitializationException（不含InnerException/provider文本）；ct取消只在全部部分资源已释放后抛OCE。释放异常且归还未证明时原Open保持未终结、原Owner/Task/端口继续强持，不能fault原Create后让Host把runtime=null误认全部归还。
5. 外层只做§7.1.1有限观察；期限到期发合作取消并保持原Create/HostTask，不开第二组/换Runtime、不清Owner槽。成功交付与取消在唯一边界线性化：取消先胜出就完整清理；成功先胜出由Host先写hold.Runtime再核取消。此规则同样覆盖配置source及秘密租约的迟到交付。

#### 6.7.3 A1 固定执行与技术持久查询

A1具体实现私有`PostgreSqlDatabaseBackend/PostgreSqlReferenceCoordinator/PostgreSqlAssetBackend/PostgreSqlFileMetadataBackend`；只以本节工厂交付接口，构造器不公开。它们使用§6.6同一im066 schema及固定注册技术SQL。每用途池由NpgsqlDataSourceBuilder.Build创建一次，Host/Port/Database/Username/Password只由可信解析写入NpgsqlConnectionStringBuilder；固定Pooling=true、Multiplexing=false、NoResetOnClose=false、Enlist=false、SslMode=VerifyFull、IncludeErrorDetail=false、LogParameters=false。Root certificate经已核公开UseRootCertificate注入，证书对象持有到数据源Dispose。§8各池timeout单位精确映射，ConnectionString不进入日志/异常/回执；不使用连接串默认池合并或每请求Build。

每次方法按已固定deadline获取该用途连接，BeginTransaction绑定已注册隔离；`set_config('app.tenant_id',$1,true)`及受控lock_timeout/statement_timeout在本事务作用域设置，标识符来自审核目录。运行角色非Owner/非超级用户/无BYPASSRLS，业务和技术表explicit tenant predicate + FORCE RLS；技术集群维护凭据只按已授权全Store/Owner集合工作，不能用普通tenant角色绕过RLS。连接/transaction/command/Reader只在一次私有scope内；Reader→command→transaction→connection逆序真实Dispose完才归还方法，坏连接由驱动弃置，不访问私有connector/Statistics。

**Owner SQL的同事务引用epoch。** `PreparedStorageTransaction.PublicationToken`已经向A1交付原Publish保护，`BackendExecution.WriterToken`是另一原Operation保护，不能互换。A1在取得物理guard后进入原数据库事务，按固定次序锁reference_authority行→原route/attempt→本次对象/引用技术行→Owner固定命令所需领域行；不在持PG/Store/object锁时再申请Operation锁。重验authority/catalog、两个原token及原writer/fence后，读取已提交reference_epoch=e，checked分配E=e+1，并在**该同一事务**更新reference_authority。Int64耗尽在Owner命令前拒绝CapacityExceeded，不回绕、不重置。包括References=Empty的注册写事务也走此边界，因为Reserve/保持/根历史可以没有已解析对象；普通Read、QueryOperation、Created=false重放不分配E。

Register/AppendEvidence/BeginResume及协调/引用/GC投影等技术写，只要同时访问authority与route/object行，也须遵同一锁序；仅访问asset行的封口不凭空取得Owner锁。PG group在原连接/原事务内用私有已核规则检查token、原guard持有及fence，不能持行锁再通过公开Coordinator端口另借连接等待自己，也不向Owner codec交此连接。SQL锁等待及40001/40P01重试扣原execution deadline，不能另开无限恢复事务来解锁；真实rollback/Dispose沿原Task与独立cleanup观察，执行期限到期不截断清理或假报Released。

执行Owner commands前，A1以固定名`app.im066_authority_id`、`app.im066_authority_epoch`、`app.im066_publish_fence`、`app.im066_reference_epoch`调用参数化`set_config(name,value,true)`；值依次来自当前冻结AuthorityId、已核Publish.AuthorityEpoch、Publish.Fence和E，整数用InvariantCulture无符号正十进制ASCII（E/Fence的CLR值仍为正Int64）。参数值由A1生成，不来自Owner canonical输入或codec可变状态。Owner固定SQL用`current_setting('app.im066_reference_epoch',true)`读取并严格转bigint，缺失/空值/非正值拒绝，不自增另一套epoch；root_history关闭旧区间与建立新区间、owner_object_reference变更均使用同一个E。字段只在当前事务有效；每次事务先将上述四项置空，只有这个已授权写分支填入，Read不得取得可写epoch。不开放连接、SQL callback、新请求字段或额外公共端口。GUC仅传递技术上下文，**不是权限或fence证明**；Owner可信目录不得更改它，A1在Owner命令后再核值，实际写入范围仍靠双token、guard、RLS、全键和已审核SQL约束。

Token.ReferenceEpoch是该lease获取时的观测值，不能让Owner直接拿它给新提交的历史行定界；Publish/Operation token有效性由原lease/authority/fence/范围决定，不因无关事务已提交而把全局epoch数值当独占权。用于GcPlan/BackupCut的快照epoch取屏障建立后确认的已提交值，Owner历史读取始终指定该原值。A1持reference_authority行锁直到Owner写、精确引用变化、原技术receipt/head及E一起commit或rollback；commit未知就保留原身份/发布保护，不在第二事务补root/receipt或再分配E。回滚使E及Owner变化一起不可见；新写者必须先满足原writer/fencing门，不能靠epoch较大接管。

Owner实体ID/修订及Release/Hold决定仍由其已注册SQL确定，A1不得从PayloadType、ObjectId或operation id猜领域根。该目录可在同事务变更**本Owner/当前完整Scope/Store**的im066.owner_object_reference，技术列/约束及授权范围由IM066冻结；不得改其它Owner引用、reference_authority或操作回执。A1预验本次声明的精确ObjectRefs与封口/发布保护，注册包验收必须证明新建引用正是声明集合、释放只作用于原合法实体/保持。Binding.Min/MaxAffectedRows仅累计其StatementCatalog内Mutation的实际行数，A1自己的epoch/route/receipt SQL另按各自精确CAS行数核验，不把隐含技术写加到Owner命令计数。这样configuration多步行数、lighting的0/1 CAS和inspection-evidence原事实子mutation都不需要猜额外计数。

根枚举的调用者持有原协调lease，先用其GetStatusAsync核Open/当前版本并确认真实guard仍被强持，再调用resolver.Open/每次Read，整个快照使用与闭包转换前都重验原保护。Owner root Read仅在Query/READ ONLY事务按原catalog/authority epoch及指定reference epoch读历史；SQL观测可确认数据库视图，不能证明OS guard仍有效，resolver无需获取新lease或按next_fence最大值伪证当前持有者。无法证明保护、历史覆盖、总数/字节或任一ReservedKey解析时，不发布完整snapshot/GC许可。未知根只阻相关GC/完整闭包，不阻已登记普通保存和窄读。

软件反例固定为：已提交e=7，两次不同原写事务先后提交时Owner历史界值依次8、9；第一次在commit前失败时authority与所有Owner行均仍为7，不能出现界值8的半根；原Committed重放不新分配epoch。GcPlan在7枚举期间允许后续历史区间追加，但该次各页始终按7读取且旧版本不得退役；BackupCut取得全集Store独占gate后，所有已接纳引用写必须结局确定，epoch与LSN cut不得混取。两种隔离级别发生40001/40P01仍沿原有限重试/Unknown规则，不能为了分配epoch降低已登记隔离。authority行串行化成本计入§11.2热点多Owner/多Store测试，不宣称无争用或适用未测负载。

| 端口组 | 固定持久实现与原子边界 | 查询/失败边界 |
|---|---|---|
| Register/ReadRoute | 按§6.6完整双唯一键及当前Operation fence做INSERT/CAS；attempt=0及不可变Kind/Profile/SemanticVersion | 同值Created=false，异值Conflict；Recovery池权威只读，不把路由当提交回执 |
| Execute/Query | 锁原route/attempt、核原fence/发布保护，固定Owner commands；领域写、owner_object_reference、operation_receipt和head在一事务commit | commit已发送后不可证结论→Unknown；不换identity、不重发映射。Query仅读权威原route/head/receipt，零Append/修引用 |
| AppendEvidence/BeginResume | 锁原route/head/attempt，按§6.3exact revision/journal/hash/fence同时插入和CAS head/当前writer | 同参数重放原attempt；未知接纳只读回查，不能发effect；历史证据不可覆写 |
| Assets Seal/页读 | SHA和类型/预算在事务前核，snapshot+全部entry一次事务发布，同Id/revision异hashConflict；页按精确snapshot/sequence有界读 | 旧link不会读到新head，封口响应未知沿原identity/准确asset版本回查；缺页/摘要错IntegrityFailed |
| FileMetadata | Publish仅接§2已封口、Receipt/Entry.Object exact、PhysicalIdentity/SealJournal合法且write/Operation双token有效的记录；同事务核durable pending保护后登记object_catalog | 该桥只写技术索引，封口真值仍是文件journal；DB不可达时File.Unknown、pending保留，不能因catalog查无再写source。Read缺记录为Record=null/Unavailable，不推断物理NotFound；同Key异描述Conflict，损坏IntegrityFailed |
| GC索引/目录 | OpenDirectory在GcPlan/Backup保护下形成有界不可变完整目录；RecordGc核当前PhysicalIdentity/alias/fence及已封口intent，原item/action幂等更新quarantine/deleted技术状态 | 不能凭索引更新证明删除成功；物理journal/probe确认后才更新，未知保持原条目/保护；不修改Owner业务引用 |

FileMetadata.Publish仅允许SealedDurable/SealedNotDurable及对应Profile，Entry.PendingPublication=true，Aliases至少含该Key且PhysicalIdentity非null，Entry.UnreferencedSinceUtc等于本次封口UTC。同Key完全同描述/原Identity/SealJournal重放null Fault，异值Conflict；null Fault只证明该技术写已确认。ReadOperation只允许原route Kind=Stage/Verify，仅读同原identity的route/receipt/head，不执行其它Kind或对账写；故障/保证期沿§6.3，不以数据库查无证据推断文件未发布。object_catalog的file_state/GC扩展唯一迁移规格为下表及其CAS规则，不留给程序员决定。公开ObjectKey/PhysicalIdentity/原seal link不改，实际quarantine位置/时间仍只在A2原物理journal。RecordGc仅接受Quarantine/Delete、确认的原EffectIntent/item/action/物理身份及双token；同intent同动作重放，异身份Conflict；null Fault仅证明技术投影确认。Directory.Open仍复用既有二选一/paging预算/快照完整覆盖语义，不偷偷生成空目录；A2以原物理journal核现状，不以该投影单独授删除。

本次扩展列属于im066.object_catalog，沿用§6.6唯一ObjectKey及tenant/store/generation列，不涉及Owner业务表；迁移由既有TechnicalSchema/migrationPackage登记和§7.3流程执行，Create不得自动ALTER。下表enum数字就是已有声明值，不增加公开状态：FileState.SealedDurable=0、SealedNotDurable=1；JournalAction.Quarantine=2、Delete=3；StorageAssetSchema.JournalV1=2。

| 唯一列名 | PG18类型 / NULL / 默认 / CHECK | 含义与写入条件 |
|---|---|---|
| `file_state` | integer NOT NULL，无默认；`CHECK (file_state IN (0,1))` | 原成功封口的耐久属性，只可来自Publish的精确Receipt.State，并与原Receipt/耐久Profile一致；不可后续升降级。Rejected/Failed/Unknown不造catalog，OrphanPending/IntegrityFailed/Verified保留在各原operation/journal或protection投影，不覆盖此原seal属性 |
| `gc_action` | integer NULL，无默认；`CHECK (gc_action IS NULL OR gc_action IN (2,3))` | 最后已确认的物理动作；NULL=尚无确认GC投影，2=已隔离，3=已删除且catalog墓碑保留；不是未发出/Unknown effect标志 |
| `gc_intent` | bytea NULL，无默认；非null时`octet_length(gc_intent)>0` | 原已封口EffectIntent的完整StorageAssetLink，按§6.4精确canonical含Schema/Creator；长度≤Profile.Maintenance.MaxJournalBytes，在绑定/分配前核，不能存路径或用确认后的新journal替换原intent |
| `gc_intent_asset_id` | text COLLATE "C" NULL，无默认；非null时`octet_length(gc_intent_asset_id)>0` | gc_intent.Version.Id；严格UTF-8/MaxIdBytes由A1同输入校验，不trim/大小写折叠 |
| `gc_intent_asset_revision` | integer NULL，无默认；非null时`gc_intent_asset_revision>0` | gc_intent.Version.Revision，非当前“最新”修订 |
| `gc_intent_asset_hash` | bytea NULL，无默认；非null时`octet_length(gc_intent_asset_hash)=32` | gc_intent.Version.Hash原始32byte，非64字符text |
| `gc_intent_schema` | integer NULL，无默认；非null时`gc_intent_schema=2` | 必须JournalV1；对应snapshot实际Schema在同事务精确核验 |
| `gc_operation_id` | text COLLATE "C" NULL，无默认；非null时`octet_length(gc_operation_id)>0` | gc_intent.Creator.OperationId；Creator的完整Scope/Owner/key/hash必须与当前Gc原route一致，不能只按该字符串授权 |
| `gc_revision` | bigint NOT NULL DEFAULT 0；`CHECK (gc_revision IN (0,1,2))` | 本版一次不可变physical incarnation的投影CAS：0=无GC、1=Quarantine、2=Delete。重放不递增，不用于operation evidence revision/attempt；已删除物理代不再次发布或清零 |

唯一组合CHECK为：`(gc_revision=0 AND gc_action IS NULL AND gc_intent IS NULL AND gc_intent_asset_id IS NULL AND gc_intent_asset_revision IS NULL AND gc_intent_asset_hash IS NULL AND gc_intent_schema IS NULL AND gc_operation_id IS NULL) OR (gc_revision IN (1,2) AND gc_action IS NOT NULL AND gc_action=gc_revision+1 AND gc_intent IS NOT NULL AND gc_intent_asset_id IS NOT NULL AND gc_intent_asset_revision IS NOT NULL AND gc_intent_asset_hash IS NOT NULL AND gc_intent_schema IS NOT NULL AND gc_intent_schema=2 AND gc_operation_id IS NOT NULL)`。必须使用IS NOT NULL显式关住PG CHECK的UNKNOWN通过分支，单列CHECK也不能替代该全空/全有约束。

FK固定为：`(tenant,store,generation,gc_operation_id) → operation_route(tenant,store,generation,operation_id)`，复用既有UK；`(tenant,store,generation,gc_intent_asset_id,gc_intent_asset_revision,gc_intent_asset_hash) → asset_snapshot(tenant,store,generation,asset_id,revision,digest)`，本技术迁移在asset_snapshot既有PK+digest列建立这组唯一约束（不是新事实表）。两FK均MATCH SIMPLE、ON UPDATE RESTRICT、ON DELETE RESTRICT、NOT DEFERRABLE；gc_revision=0时全NULL可不关联，非0时组合CHECK确保实际关联。GC墓碑/未决intent引用不退役原route/asset；历史退役仍须原批准retention流程，不通过级联删事实。snapshot的Creator/Schema及canonical normalized列等值由下述锁定事务校验，不在CHECK中访问其它表，也不靠FK单独证明effect已发生。

Publish新行显式写file_state=Receipt.State、gc_revision=0及全部gc_* NULL；同Key已有行只在完整ObjectRef/PhysicalIdentity/原write Identity/SealJournal/file_state全等时重放，且**不重置现有GC列**。已隔离/删除或其保护不明的旧物件，原seal重放只回原事实，不重新开放字节。迁移既有行只有原完整Published journal/Receipt可证时才能回填file_state=0/1，不能给全部历史行默认0；缺证据阻该Store迁移，保留原行/资料，不扫描业务表补猜。

RecordGc固定事务顺序为：核原Operation/对象双token→按固定锁层次锁原Gc route/current writer/attempt、对应不可变intent snapshot及完整physical alias的catalog行→校验intent.Creator完整等于本Gc身份、normalized列逐字段/canonical全等、Schema=JournalV1且精确ItemId/action/PhysicalIdentity的EffectIntent存在→核A2已确认本次物理journal和当前protection/reference epoch→取得每行ExpectedGcRevision/既有last_fence→一次事务CAS更新全部alias。新隔离只允许0→1，新删除只允许1→2且原Quarantine/宽限/身份已证明；禁止0→2、2→任意新动作及对同物理代二次Quarantine。UPDATE同时写gc_action/整套intent列/gc_revision及既有last_fence=当前对象token.Fence，WHERE须匹配完整ObjectKey/PhysicalIdentity/原seal、ExpectedGcRevision及原last_fence；影响行数必须恰为锁定的完整alias数，不匹配整体rollback+Conflict，不留下部分别名已删。

当前fence仍须同authority/原identity验证有效，不能凭数值增大认新writer。同action/同intent canonical/同物理代已在该revision确认时不UPDATE，回放null Fault；任何异intent重发同action为Conflict。Quarantine旧请求在已确认Delete后只读原intent/journal确认其历史结果，不把当前gc_revision从2降回1。Unknown物理效果不写这组确认列，保持原revision/原intent并返回CommitUnknown；metadata提交响应丢失沿原intent/identity回查当前行及历史物理journal，不重复native effect或新身份CAS。file_state、完整ObjectRef/PhysicalIdentity及原seal全程不可改。

SQLSTATE分类及whole-transaction有限重试沿§3；23505只对已知技术唯一约束回查，其它业务冲突不泄表/记录。所有公开失败按§6.5固定Code/Key；provider exception仅在适配器受控内部诊断保留分类，Host普通日志不得输出SQL/path/秘密。Command.Cancel/取消token/驱动CancellationTimeout均为合作取消，不证明服务器回滚或Reader已释放；尚未清理的方法保持原Task，Runtime保持Draining，DataSource.Dispose不代替借出连接真实返还。

#### 6.7.4 A2 布局、物理guard、封口和恢复

`IM066-FILES-1`在预置root中固定使用`.im066/locks`、`.im066/journal`、`.im066/staging`、`.im066/quarantine`及`objects`。工厂只打开并验证，不补不存在的历史目录/对象；运行中只在已验证命名空间独占创建本次合法staging/journal/object子目录。物理组件和锁名必须采用本节下表的精确SHA-256预像，原业务ID不作路径片段；同digest必须比较完整原身份，冲突拒绝。默认不物理去重，一个Key一个不可变文件；Aliases仍精确列出实际别名，不能以同内容hash扩成别名。跨租户同hash使用不同Key路径。

staging名绑定完整write Identity、AuthorityEpoch/Fence与固定布局代，CreateNew/不覆盖；对象路径绑定ObjectKey和存储代。封口journal私有v1记录固定字段顺序为`layoutVersion,Identity,Profile,Key,Object?,PhysicalIdentity?,authorityEpoch,fence,phase,atUtc`，phase封闭为`Intent,Writing,Validated,PublishIntent,Published,Failed,Unknown`；nullable/字段原语沿§6.4编码，每修订写独立不可变记录并hash形成SealJournal ref，不能改旧记录。journal头发布使用同卷临时记录→flush→关闭→不覆盖发布，最大单条/总量受MaxJournalBytes及容量预约；尾部不完整记录不承认Published，保留Unknown。Record位置仅私有根映射，公共ref不含路径/文件句柄。

末次封口另外保存完整FileObjectReceipt/Fault canonical，绑定原SealJournal ref；两者确认后才能交付成功回执，不能靠当前Profile重新签旧耐久状态。Verify私有记录域为`IM066-VERIFY-1`+完整FileObjectReceipt+StorageFault?，只在全读/hash/格式已确认后封口；没有耐久记录不交Verified成功。GC/Copy/Restore的native effect私有记录域为`IM066-EFFECT-1`+Identity+effectIntent+ItemId+PhysicalIdentity?+JournalAction+JournalPhase+authorityEpoch+fence+atUtc+StorageFault?，字段原语沿§6.4；EffectIntent先封口，实际确认追加不可变EffectConfirmed，未决追加Unknown，不覆盖旧记录。记录全部纳入同容量/根/原writer预算。Files.Query先以FileMetadata.ReadOperation读原证据，再按原Kind/journal核真值；证据缺失仍只读本地原seal/verify journal，不后台补DB或冒认另一次同hash写。

根验证以真实目录句柄和GetFinalPathNameByHandleW的规范卷/路径为准；逐级拒FileAttributeTagInfo重解析标志并禁止根替换ACL，重新打开目标还核最终句柄所属根/卷/代，不仅做字符串StartsWith。Root.rootIdentity.Hash固定为SHA-256(ASCII `IM066-ROOT-1` + UInt64小端VolumeSerialNumber + 原始16byte FileId + layoutVersion的§6.4字符串编码)，Id/Revision由可信目录登记，不因重启换代。PhysicalIdentity及所有锁使用下面的实际句柄原始tuple和不可变birthIdentity，不能用root.Hash字串/32byte摘要、文件内容hash、路径或PID替代根FileId/对象FileId；公用API不出现Win32结构。持有对象句柄时禁止其它参与者覆盖/改名/删除，公开读Stream无SafeFileHandle或路径。尚不能排除TOCTOU或无法取得稳定实际身份时该Profile拒装配；不降为只核字符串。

**私有身份/锁编码的唯一规则。** `D(tag)`为严格ASCII域字节，无终止NUL/长度前缀；`S(value)`为§6.4严格UTF-8的Int32小端字节数+内容（不trim/折叠/Unicode normalization）；`U64/I64/I32`为对应小端整数；`B(value)`为一byte；`Raw16`是FILE_ID_128.Identifier按内存声明顺序的16个原始byte，不按Guid格式重排。`R=U64(root VolumeSerialNumber)+Raw16(root FileId)`，两值都从已核实际根句柄取得；`L=S("IM066-FILES-1")`。`K`为ObjectKey声明顺序`S(StoreId)+I64(Generation)+S(TenantId)+S(StorageDomain)+S(ObjectId)`；`I`为完整OperationIdentity声明顺序（Scope五S→StoreId S→Generation I64→OwnerKey S→OperationId S→IdempotencyKey S→PayloadHash原始32byte）。Generation>0，原始file-id始终16byte；UInt64不得先cast为Int64。每字符串/嵌套bytes预算沿Profile，在分配前检查，未定义值拒绝；不用CLR名、JSON、连接参数、当前授权/预算或额外长度替代下表。

`birthIdentity`是**首次创建该物理文件**的原Stage或Restore完整Identity，不是本次读取/Verify/GC identity。它与该文件实际VolumeSerialNumber/FileId一起写入本次不可变seal/native journal，创建时一次确定，alias/改名/隔离/重启不变；恢复实际创建另一个物理文件时沿原Restore identity及新实际tuple形成新PhysicalIdentity，不冒认原物理代。缺birth或实际tuple无法核实则Unknown/IntegrityFailed，不能从ObjectRef或root.Hash补猜。FileId被OS重用而birth不同必须形成新物理代；同birth重复创建仍由原route/不可覆盖规则拒绝，不能重置Revision掩盖。

| 私有键 / SHA-256精确预像（从左至右，无其它字段） | 命名与稳定规则 |
|---|---|
| Root（复用既有）=`D("IM066-ROOT-1")+R+L` | Hash按原规则，rootIdentity.Id/Revision仍由可信目录登记；锁预像读取R本身，不把此Hash当R |
| ObjectPath=`D("IM066-OBJECT-1")+L+R+K` | `objects/<digest前2小写hex>/<完整64小写hex>.bin`，同K描述不同争同路径后拒Conflict，不因内容hash/Format改变改路径 |
| StoreLock=`D("IM066-STORELOCK-1")+L+R+S(StoreId)+I64(Generation)` | `.im066/locks/store/<digest>.lck`；不含Tenant/Profile，全集cut与各租户争同Store gate |
| OperationIdempotencyLock=`D("IM066-OPLOCK-1")+L+R+B(0)+S(TenantId)+S(StoreId)+I64(Generation)+S(OwnerKey)+S(IdempotencyKey)` | `.im066/locks/operation/<digest>.lck`；精确匹配route PK作用域，同键异Scope/OperationId/hash仍争同锁、再由完整route核Conflict |
| OperationIdLock=`D("IM066-OPLOCK-1")+L+R+B(1)+S(TenantId)+S(StoreId)+I64(Generation)+S(OperationId)` | 同operation目录；精确匹配route UK，不加Owner或幂等键以免跨Owner绕过OperationId唯一性；每Operation guard必须取上述两锁 |
| ObjectLock=`D("IM066-OBJLOCK-1")+L+R+K` | `.im066/locks/object/<digest>.lck`；Write未形成PhysicalIdentity时先争逻辑锁。Read/Write/Publish/Gc共享同文件名，访问模式不入hash |
| Physical=`P=D("IM066-PHYSICAL-1")+L+R+U64(object VolumeSerialNumber)+Raw16(object FileId)+I(birthIdentity)` | `PhysicalIdentity=VersionRef(lowerhex(SHA256(P)),1,Sha256(lowerhex(SHA256(P))))`；Id无前缀、严格64字符，Revision恒1，一物理代不可修订；有新实际tuple/birth就新ref，不递增旧ref冒充同文件。A1/A2真实Profile.MaxIdBytes须≥64，否则创建前拒InvalidInput；C0/C1原限额不变 |
| PhysicalLock=`D("IM066-PHYLOCK-1")+I32(P.Length)+P` | `.im066/locks/physical/<digest>.lck`；嵌入精确原始P，不嵌入PhysicalIdentity.Id/Hash。全部alias争同一个物理锁，文件内容hash相同不授共享 |
| Staging=`D("IM066-STAGING-1")+L+R+I(writeIdentity)+S(AuthorityEpoch)+I64(Fence)` | `.im066/staging/<digest>.part`，Fence>0；仅在途工作名含原writer代，锁名不含它们 |
| JournalKey=`D("IM066-JOURNALKEY-1")+L+R+I(originalIdentity)` | `.im066/journal/<digest>/`；不可变记录组件为`<正Revision无前导零十进制>-<canonical记录64小写SHA>.rec`，同revision异内容Conflict，不扫“最新”重签 |
| Quarantine=`D("IM066-QUARANTINE-1")+L+R+I(gcIdentity)+S(ItemId)+I32(P.Length)+P+StorageAssetLink(effectIntent)的§6.4完整编码+S(AuthorityEpoch)+I64(Fence)` | `.im066/quarantine/<digest>.bin`，绑定原GC intent，不从alias顺序或临时路径生成；Unknown保存原名，不换名重复移动 |

所有表中digest均为整个预像SHA-256的小写64hex，不截短；受控组件无用户原ID。digest碰撞或同名映射不符时核完整预像/原journal并Conflict，不覆盖/另盐。锁文件永久保持原logical/actual身份，不能因登记Root.Id/Revision变化、更改alias列表顺序或参考epoch创建平行锁。ObjectRef长度/hash/MediaType/Format、Caller、execution budget、InstanceEpoch、当前AuthorityEpoch/Fence/ReferenceEpoch均**不进入任何锁预像**；Full birthIdentity中的历史PayloadHash仅进入P，它是不可变出生事实，不随当前epoch/权限更新。

排序/去重唯一为：跨root按R的24byte无符号逐byte字典序；同root的Store gate按StoreId Ordinal→Generation数值；Operation两锁按判别byte 0→1（跨root先R）；逻辑alias按§6.3 ObjectKey的StoreId Ordinal→Generation数值→TenantId/StorageDomain/ObjectId Ordinal；物理锁按P原始byte字典序。先核完整Aliases非default/无重复Key、集合与权威目录全等，再取**所有逻辑alias锁及去重后物理锁**，不能把alias集合hash作一个替代锁。去重只允许预像逐byte相等，不以相同digest跳过不等预像。固定层次为本operation两锁→全部Store gate→全部逻辑object锁→全部physical锁→PG协调行；取得物理代需在logical锁下读取已封口journal/实际句柄，再取P锁、重新核alias集合及fence，无保护窗口不得发布/删。原有BackupCut借用/禁止锁升级规则沿下文。

**最小完整软件字节向量。** layout=`IM066-FILES-1`；根VolumeSerialNumber=1、根FileId=`000102030405060708090a0b0c0d0e0f`；对象卷=1、对象FileId=`101112131415161718191a1b1c1d1e1f`；K=(x,1,t,m,a)；birth/write Identity.Scope=(t,s,l,n,d)、StoreId=x、Generation=1、Owner=o、Operation=p、Idempotency=k、PayloadHash=`aa`×32；当前AuthorityEpoch=e/Fence=1。下表hex均为完整预像，不是只写字段摘要；作者使用两种内存构造（手工逐字段小端拼接、BCL BinaryWriter）逐byte及SHA复算一致，仅作软件规格核查，不是实际文件/跨进程锁验证。既有Stage Hasher及290byte向量不变。

| 键 | byte长度 | SHA-256 | 完整预像hex |
|---|---|---|---|
| JournalKey | 144 | `9f961384be94648041a71ca84c0490019cd8e18990ab9897b7df21aacafac8da` | `494d3036362d4a4f55524e414c4b45592d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f01000000740100000073010000006c010000006e010000006401000000780100000000000000010000006f0100000070010000006baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` |
| ObjectLock | 84 | `374c1e9d3628d62520fc83a276e32e56db1188d31dce8d698b63d72aec85bc59` | `494d3036362d4f424a4c4f434b2d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f010000007801000000000000000100000074010000006d0100000061` |
| ObjectPath | 83 | `e357a45dd5eba5c4aecd706e1a149b291e40e1542c2398792d46f1cac17ff258` | `494d3036362d4f424a4543542d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f010000007801000000000000000100000074010000006d0100000061` |
| OperationIdempotencyLock | 84 | `ac35d78f84c9efd6f63c4cef22277b18ca2419141cd6d218360aa234aa33dd51` | `494d3036362d4f504c4f434b2d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f00010000007401000000780100000000000000010000006f010000006b` |
| OperationIdLock | 79 | `4d493476099fac6e57aecdfe05b4ebacc291c567199c3dfc3829cd331a97a587` | `494d3036362d4f504c4f434b2d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f010100000074010000007801000000000000000100000070` |
| Physical | 166 | `fcd62bff52b5631b565a4945731f73d47c840f3e5e8014d7fc575e77615274bc` | `494d3036362d504859534943414c2d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f0100000000000000101112131415161718191a1b1c1d1e1f01000000740100000073010000006c010000006e010000006401000000780100000000000000010000006f0100000070010000006baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` |
| PhysicalLock | 185 | `12b6d3ec7f702f9b3b6b3cb791e0ec712ec68c1f1bb313c2e299fdbda1c22bd9` | `494d3036362d5048594c4f434b2d31a6000000494d3036362d504859534943414c2d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f0100000000000000101112131415161718191a1b1c1d1e1f01000000740100000073010000006c010000006e010000006401000000780100000000000000010000006f0100000070010000006baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa` |
| Root | 53 | `081a566ca4d343636663ff9a92018bccbd749a995eb54b8824cff6558dd3c956` | `494d3036362d524f4f542d310100000000000000000102030405060708090a0b0c0d0e0f0d000000494d3036362d46494c45532d31` |
| Staging | 154 | `31e2cf79e68c253cfb630fa114ed453f507ea7743228764315c195a53c5cf1c4` | `494d3036362d53544147494e472d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f01000000740100000073010000006c010000006e010000006401000000780100000000000000010000006f0100000070010000006baaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa01000000650100000000000000` |
| StoreLock | 71 | `250123fc76ab0fc9630d1f3fde74737b586ad0bbe8c7a96824b65b7b4637c7ba` | `494d3036362d53544f52454c4f434b2d310d000000494d3036362d46494c45532d310100000000000000000102030405060708090a0b0c0d0e0f01000000780100000000000000` |

软件反例冻结如下：①Aliases=[K(a),K(b)]与反向输入先按ObjectKey排序，最终逻辑锁有序集合逐byte相同；两个alias指同一R/object tuple/birth时P及PhysicalLock逐byte相同，只取一物理锁，K(b)不会把K(a)的逻辑锁替掉。②当前epoch e→z、fence 1→9、reference epoch 0→7、InstanceEpoch改变时，表内Root/ObjectPath/Store/两Operation/Object/Physical/PhysicalLock/JournalKey预像和hash全不变；Staging/Quarantine按各自原工作字段改变，不能拿新工作名代替旧锁或原Unknown intent。③同route PK但OperationId/hash/非Tenant Scope字段改变，OperationIdempotencyLock不变；同route UK但Owner/idempotency改变，OperationIdLock不变，完整route比较须Conflict。④将根R换成rootIdentity.Hash的UTF-8 hex字串或32byte digest是错误预像，即使ObjectRef内容相同也与向量不等，必须拒绝该编码实现；更换实际根/对象FileId或birth则P必须改变，不能继续用旧PhysicalIdentity授权。

Authority的guard是真实跨进程共享模式锁，不用进程内Semaphore当物理资格：持久locks文件不DeleteOnClose、不允许参与者重命名/替换；共享Read/Write/Publish/GC访问先取各Store gate共享读句柄（FileAccess.Read/FileShare.Read），BackupCut按完整Store集合取独占句柄（FileAccess.ReadWrite/FileShare.None）。Kind=Operation按上表原route PK/UK取两个独占锁；其它Kind不重复取得这两锁，普通object Read/Hold的逻辑/物理锁为共享，Write/Publish/Gc为独占，物理alias集合必须全覆盖。原Operation锁先于资源保护；精确预像及排序按上表，不在持Store/object/PG锁时申请另一个operation锁。获取失败释放已取得部分，有限等待使用原Clock/deadline；不得反向拿锁/升级已持共享句柄。Backup临时屏障使用PG durable保护，不持自身共享Store gate再升级BackupCut；cut内同Owner后续Copy使用原token借用，不二次取与自身冲突的锁。Operation锁不持Store共享gate，避免请求全集cut时自锁。**锁预像不含可变AuthorityEpoch/fence/InstanceEpoch**，旧新实例争同锁，不能换锁文件绕过旧writer。

PG Coordinator.Enter先取得对应Authority guard并保存原Task/句柄，再按同scope完整keys锁PG协调行、授不可复用fence/token；保护lease同时持有OS guard及PG耐久登记。失败先真实释放部分guard再返回；成功guard归该协调lease，TTL只停止新effect/发取消，不自动close仍被IO借用的句柄。PG Validate、Preserve、publication/reference事务及GC effect均在同guard和协调锁域核当前fence，检查后不能先释放guard再写/删。DB连接断开时OS锁及durable pending仍在，另一Host拿不到物理排他权；仅OS锁可取得也不证明旧意图未发生，未决Publish/Delete/Restore intent须原identity Probe并fail closed。PG连接消失、PID查无、超时不授新writer。QualifiedSmb的断线/durable handle/跨Host共享锁须实测证明，否则关闭该写/GC装配；本地软件夹具不能授NAS资格。

Stage顺序为核原route/journal→容量/最坏字节预约→持Write和Operation保护→Intent耐久→分块写/hash/长度/格式→Validated→按已验证Profile Flush(true)/关闭写句柄→在原协调保护下Preserve PendingPublication→PublishIntent耐久→同卷不覆盖发布→实际句柄读回identity/完整长度/hash→Published journal耐久→FileMetadata.Publish→保存原operation证据→真实释放全部借用/句柄/预约。只有journal、字节、真实耐久Profile及技术索引均确认才交SealedDurable；未验证耐久只能SealedNotDurable，生产引用仍拒。发布已发生而索引/证据响应未知保留Published原真值及pending并返回Unknown，恢复观察不能重读新source。容量含journal/staging/对象分配/quarantine/临时封口/预留余量，任何checked溢出或水位不足在读source前拒绝；请求ExpectedBytes不代替最坏预约。

OpenRead先核完整ObjectRef/metadata/journal及Read token，打开不允许write/delete分享的只读句柄，交付既有有界Stream；活动sync/async读必须完成才Dispose句柄/归还Read guard，cancel仅合作取消。Verify全读全hash并运行登记格式validator，不提升耐久。Query/Probe只沿原identity、SealJournal和PhysicalIdentity读已存在的journal/实际目标，不修catalog、删staging或推进publication；文件存在但原journal不完整仍Unknown，缺文件且已提交引用为IntegrityFailed。重启旧Handle不复活；恢复执行必须显式获权、原identity/current fence，并先证明旧writer无迟到effect。

GC沿§6.4/§6.6已冻结plan及Asset EffectIntent，在原排他guard下复核全部alias/引用/hold/epoch，核对象实际PhysicalIdentity；先同卷不覆盖移动到绑定原GC identity/item/fence的quarantine，再核原物理身份及journal，宽限到期再次取原保护执行Delete。每次native move/delete原调用及本地文件journal结果保存在同worker，释放发生在它们真实结束后；Unknown不重开放、不新身份重复删除。确认后经FileMetadata.RecordGc更新技术投影，投影失败保留物理真值/intent并Unknown；读口不代做更新。Files.Dispose等待file/native/guard/Reader全部排空，SafeHandle关闭成功且实际IO已结束才释放预约；Dispose没有人为超时，外层观察到期仍强持原Task/根/端口。

#### 6.7.5 A3 维护工具装配及门限

仍由StorageMaintenanceBackend组合现有五实例，不新建A3 DLL/池。Migration StatementCatalog/Validation/Compensation精确ref进入A1可信目录，每step SQL及实际结构/history验证固定；事务step与history同commit，非事务step保留intent并Probe实际invalid index/结构。未知结果不凭版本行推定Applied；缺Owner迁移内容只拒该plan，不让技术表迁移设计由客户补猜。

BackupTool doc字段为`toolVersion,serverMajor,baseBackupExecutable,serverExecutable,controlExecutable,executableHashes,backupCredential,argumentsProfile`；工具路径只在A1私有启动配置，serverMajor=18、VersionRef与BackupProfile/IsolatedTarget.ToolVersion exact，可执行文件hash/实际版本须核，不下载/安装工具。argumentsProfile本版固定`Pg18PhysicalV1`，不接自由参数/脚本；用ProcessStartInfo.UseShellExecute=false及ArgumentList启动pg_basebackup/前台postgres/pg_ctl。BackupDestination/IsolatedFiles doc字段`root,accessPolicy,namespace`指向A2已注册根及受控namespace；IsolatedDatabase doc字段`dataRoot,endpoint,credential,pool,deviceWorkersDisabled,sendWorkersDisabled`，两个disabled须true且目标身份与生产不重合；pool为§6.3完整StoragePoolProfile，Purpose=Recovery、Credential等于本doc的credential，IsolatedRead角色只读。KeyMetadata只存服务/key版本ref，秘密取得归受信任Host，不进manifest；未提供批准key服务实现时只拒需要它的备份/恢复。

pg_basebackup使用固定`--format=plain --wal-method=stream --checkpoint=spread --no-password`及trusted host/port/principal/本次目标参数，不使用--write-recovery-conf/自动连接生产的standby设置。本版先查pg_tablespace拒额外用户tablespace，避免plain默认写到源绝对位置；确需额外tablespace时先在本指导另冻受控映射子切片，本次不猜位置。A1保留官方backup_manifest、backup_label与实际PG身份：要求PostgreSQL-Backup-Manifest-Version=2，核System-Identifier、WAL-Ranges的Timeline/Start-LSN/End-LSN，LSN按高低32位无符号组合；BaseStart/BaseEnd是manifest声明的必需重放起点/最早可结束点，不从stdout/墙钟猜LSN。当前SinglePrimary装配仅接受一个与实际timeline相同的WAL range，未知多timeline base拒确认，后续cut跨timeline仍须§6.4完整history证明。Manifest-Checksum按官方格式核最后一行前的精确字节，全部必需part实际长度/hash验证后才确认base结果。生成的PG数据/WAL字节属于备份part，不是业务图像入库。源/目标路径只从可信根和原operation生成，凭据使用有ACL的本次工具秘密文件，PGPASSFILE仅传子进程，路径/密码不在命令行或日志；文件由本次工具Owner在原child及stdout/stderr Reader真实结束后一次清理，清理失败保存cleanup状态，不递归清未知目录。stdout/stderr同时有界读取，计数超限发合作停止并保持原child Task/IO，不能WaitAsync超时就Dispose Process称退出。退出非0/取消/结果未知保留原intent；只有确认child/native/file真实停止才Probe NoEffect或进入原步骤恢复，不启动第二个工具替代。

ReadCut在原BackupCut全集屏障内使用PG18真实身份/LSN和已归档连续WAL清单，Start/End必须来自同一base结果，不能把current LSN缓存当已归档；timeline history/缺段沿§6.4拒完整闭包。隔离恢复固定base+WAL至RestorePoint的精确timeline/LSN，配置recovery_target_lsn/timeline、hot_standby=on及recovery_target_action=pause验证，不调用promote/replay_resume。直接启动前台postgres，由PG group有界目标槽持有原Process/WaitForExit/stdout/stderr Task和target Profile，不能只持pg_ctl start的短Task；一个已登记目标只一个服务Owner，未知旧服务不另起。Restore工作结束后可将已受管只读目标服务交给同group供后续VerifyRecovery；服务不是无Owner遗留，固定槽≤IsolatedTargets.Length，原Runtime Stop关新调用并关闭它。VerifyOnly只读既有已注册目标，不启动/改配置/促进恢复。

隔离target使用其预登记Recovery/IsolatedRead pool的长寿命DataSource，精确角色/权限/首连接验证及私有数据源键按§6.7.1 Recovery表，不每次校验建池；连接只到该target，不复用源库Recovery/Runtime连接。启动总预算固定核`主库各Pool.Max之和 + 全部隔离Pool.Max之和 + base backup的2个walsender槽 + 部署显式保留槽 ≤ TotalConnectionBudget`，有BackupProfile时预留两个stream备份连接，不能临时越额创建；部署保留槽由AuthorityTopology文档的`reservedConnectionSlots`非负Int32明示。target DataSource/凭据/服务同归PG group，startup可只Build尚未启动目标的池，恢复就绪后才探测连接。工具stdout/stderr合计已读取/保留字节≤Profile.Maintenance.MaxJournalBytes，各单次缓冲≤Profile.Input.MaxResultBytes，超限只保留固定Fault/计数、不无界存日志。停止隔离服务先等目标操作/Reader/连接排空，再对**同一已确认隔离dataRoot**一次发pg_ctl stop -m fast --wait；发停止成功仍须原postgres WaitForExit及其Reader真实结束才释放Process/根借用/目标槽，目标池随后Dispose。停止/退出未知保留原group/Task；不得指向生产dataRoot或只凭PID查无作归还证明。实际target/tool版本和全必需对象/Owner验证满足§6.4才RestoredAndVerified；成功不授生产启动、切换或Outbox发送权。

以上补齐可决定的内部装配、技术表/元数据桥、文件布局和工具步骤。§6.7/§7.1.4既有装配增量已获主控限定内容接收，本轮启动快照/epoch接线由原会话完成内容自审，不再等待总控重审；A1/A2/A3整体仍PreparationIncomplete。正式Owner注册实现、真实PG夹具与部署根/工具/秘密/Profile及耐久/性能/现场证据按附录B逐项保留。不得把尚未实现的Factory/桥/锁/journal或Owner SQL记成“等客户决定”的外门，也不以软件规格冻结冒认真实适配通过。

## 7. 逐能力执行顺序

### 7.1 初始化、最小 Host 和两个消费者

宿主显式注入 `IStorageRuntimeFactory` 的实现，提供可信配置及当前 `IStorageAuthority`。CreateAsync 先解析不可变 Profile/Catalog、验证版本/角色/租户集合/根/有限预算和所有注册 codec，再建立数据源和健康验证，最后返回 Runtime；失败关闭已创建资源，不建空库/目录冒充历史源，不触发迁移。初始化参数/版本/权限失败抛 §6 声明的 StorageInitializationException，不透出 raw provider exception。初始化仅有已创建 Runtime 或已完整释放后异常两个结果。初始化 token 取消后等资源释放再抛 OperationCanceledException；工厂启动期限来自已解析 Profile。

§6.3 已冻结 C1 的注入和构造边界：`StorageRuntimeFactory(StorageRuntimeDependencies, StorageFactoryOptions)` 是唯一公开构造形状；它先用 Configuration resolver 将 `RuntimeConfiguration` 的五个 VersionRef 解析为不可变 `ResolvedStorageConfiguration`，再由 `IStorageBackendFactory.OpenAsync` 创建唯一 `StorageBackendSet`。factory 只拥有并释放返回的五个后端实例，resolver、clock、barrier、authority 由宿主持有；没有静态定位器、环境变量回退、请求 delegate、动态程序集加载或隐式默认 Profile。启动验证顺序固定为：Configuration/版本/集合/配额→Authority 的 storage.runtime_create→BackendSet 能力和健康探测→Runtime 实例。任一失败按 `StorageInitializationException` 收口并逆序释放已创建对象；取消也等释放结束后再抛 OCE。

Runtime 对需要执行上下文的后端调用构造唯一五字段 `BackendExecution(InstanceEpoch, WorkId, RemainingBudget, WriterToken, Attempt)`，把 ExecutionBudget、当前 barrier 和适配后端交给唯一协调器；durable 执行的 WriterToken 必须是原 identity 当前有效的 Operation token，窄读取为 null；首次执行 Attempt=0，维护续作为 BeginMaintenanceResumeAsync 确认的正 attempt。字段顺序与§6.3公开声明一致，不把 Write/Publish/Read 等对象保护 token 冒充 WriterToken，也不把外部等待 token 直接传入 backend。`IStorageDatabaseBackend` 仅负责技术事务、窄读、operation 查询和数据库健康；`IStorageFileBackend` 负责文件 stage/read/verify；`IStorageReferenceCoordinator` 负责 publish/read/hold/GC/backup 保护；`IStorageMaintenanceBackend` 负责维护动作；`IStorageAssetBackend` 负责不可变资产封口/页读。所有后端调用均有真实资源排空后才返回，Runtime 用原 identity 写回 task/journal；C1 假后端只能实现这些端口和 barrier，不伪造整个 `IStorageDatabase` 或真实数据库/文件耐久。

无 UI C1 Host 必须调用真实 `StorageRuntimeFactory`，仅替换 `IStorageConfigurationResolver`、`IStorageBackendFactory`、`IStorageClock`、`IStorageExecutionBarrier` 为内存夹具；configuration resolver 返回固定最小 Profile/Binding/Reference 快照，backend factory 返回可控 database/file/reference/maintenance/assets fake。Host 至少执行 OpenSession、一个 StageAndSeal 或 ExecuteTransaction、GetTaskStatus、QueryOperation、Release/Stop/Dispose；在 `BeforeResourceRelease` barrier 上取消，断言方法返回前后底层 fake 仍持有 work/lease，解除 barrier 后按 `Draining→Drained→ResourcesReleased→Completed`，并用同一 operation 查询迟到回执。第二个 CLI 只能拿完整 ObjectRef 调 OpenRead/Verify/Release；不读 fake 私表。这个 Host 是 C1 唯一最小调用/测试形状，fake 只验证接纳、权限、排空、回查和资源所有权；A1/A2/A3 的真实后端资格仍是后续门。领域业务 Schema/SQL/codec 内容和生产 Profile 由 Owner/部署输入，不在本模块造私表或客户值。

C0 最小 Host 只引用 Contracts/Core 并调用 §10 两个同步方法，不需工厂、授权服务或 IO。后续写消费者的顺序是 Create→OpenSession(Production)→StageAndSealFile→查询原 Task 至 Completed→检查 SealedDurable→以精确 ObjectRef 执行已注册领域事务→必要时 QueryOperation→Release Session→Stop→Dispose。生产Host按§7.1.1–7.1.2在Create前预留原Owner保持槽；Source Stream保持到原Host Task与清理真正排空，不能在“方法等待超时已返回”时由外层await using关闭源流。

第二个独立 CLI Host 引用相同 Contracts 和适配包，使用 Query scope/当前读授权，只把第一个消费者回执的完整 ObjectRef 传给 OpenRead→流式消费→Release lease→Stop→Dispose；故意把两租户 ObjectId 或同 hash 互换必须拒绝。它不认识第一消费者私表，只能由 Owner 公开定向端口取得 ObjectRef。两个示例中的 stopFor 使用独立可信实例控制身份，读租户本身不获得 storage.runtime_stop；工厂/Host负责该实例生命周期。库拒绝创建目录、补文件或替换历史引用；两个宿主可在独立构建/进程和不同配置中运行。

### 7.1.0 C1 真实协调器与假后端Host

以下是Runtime.Tests内合成片段，using与§6相同并引用Runtime namespace；三种fake class分别置独立测试源文件，RunC1Host/Observe/RunMaintenance等方法是测试Host静态class成员，不能在顶层Program中把local函数放在类型声明之后。fixedResolver/authority/clock及其余四个fake backend由入口显式注入并满足§6.3；FixedBackendFactory仅返回独占组、不实现IStorageDatabase。fixtureReceipt是三byte的SealedDurable合成证据，fixtureRequest摘要按本文生成；syntheticHealth无耐久资格。调用真实StorageRuntimeFactory与Stage/Task/Operation端口。闩锁用RunContinuationsAsynchronously，suite60秒截止，异常不能放任fake无限等待。

```csharp
sealed class FixedBackendFactory(StorageBackendSet set) : IStorageBackendFactory {
    private bool opened;
    public ValueTask<StorageBackendSet> OpenAsync(ResolvedStorageConfiguration configuration,
        IStorageClock clock, CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        if (opened) throw new StorageInitializationException(
            new StorageFault(StorageError.ResourceBusy, "storage.resource_busy"));
        opened = true;
        return ValueTask.FromResult(set);
    }
}
sealed class BlockingFileBackend(FileObjectReceipt receipt, StorageHealth health)
    : IStorageFileBackend {
    public TaskCompletionSource Entered { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource AllowFinish { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public int Active;
    private FileObjectReceipt? recorded;
    public ValueTask<BackendEffectResult> ProbeEffectAsync(OperationIdentity identity,
        StorageAssetLink effectIntent, string itemId, CancellationToken ct) => ValueTask.FromResult(
        new BackendEffectResult(BackendEffectState.Unknown,
            new StorageFault(StorageError.CommitUnknown, "storage.commit_unknown")));
    public async ValueTask<BackendFileResult> StageAndSealAsync(FileObjectRequest request,
        Stream source, StorageCoordinationToken writeToken, BackendExecution execution,
        CancellationToken executionCancellation) {
        Interlocked.Increment(ref Active);
        Entered.TrySetResult();
        try {
            await AllowFinish.Task; // 模拟不立即响应合作取消的IO，仍需真实排空
            if (!source.CanRead) throw new InvalidOperationException("storage.drain_incomplete");
            recorded = receipt;
            return new BackendFileResult(receipt, null);
        } finally { Interlocked.Decrement(ref Active); }
    }
    public ValueTask<OperationQueryResult> QueryAsync(OperationQuery request, CancellationToken ct) {
        ct.ThrowIfCancellationRequested();
        if (request.Identity != receipt.Identity)
            return ValueTask.FromResult(new OperationQueryResult(null,
                new StorageFault(StorageError.Conflict, "storage.conflict")));
        return ValueTask.FromResult(new OperationQueryResult(new OperationRecord(receipt.Identity,
            recorded is null ? StoredOperationState.InProgress : StoredOperationState.Succeeded,
            null, recorded, null, null), null));
    }
    public ValueTask<BackendReadOpenResult> OpenReadAsync(FileReadRequest request,
        StorageCoordinationToken token, CancellationToken ct) => ValueTask.FromResult(
        new BackendReadOpenResult(null, new StorageFault(StorageError.Unavailable, "storage.unavailable")));
    public ValueTask<BackendFileResult> VerifyAsync(FileVerificationRequest request,
        StorageCoordinationToken readToken, BackendExecution execution, CancellationToken ct) => ValueTask.FromResult(
        new BackendFileResult(null, new StorageFault(StorageError.Unavailable, "storage.unavailable")));
    public ValueTask<StorageHealth> CheckHealthAsync(HealthRequest request, CancellationToken ct)
        => ValueTask.FromResult(health);
    public ValueTask<ObjectDirectoryOpenResult> OpenDirectoryAsync(CallContext context,
        StorageCoordinationToken token, int maxEntries, int maxBytes, CancellationToken ct)
        => ValueTask.FromResult(new ObjectDirectoryOpenResult(null, Unavailable()));
    public ValueTask<BackendEffectResult> ApplyGcAsync(GcCandidateV1 candidate,
        JournalAction action, StorageAssetLink effectIntent, OperationIdentity identity,
        StorageCoordinationToken token,
        BackendExecution execution, CancellationToken ct) => NoEffect();
    public ValueTask<BackendEffectResult> CopyBackupPartAsync(BackupPart part, ObjectRef? obj,
        OperationIdentity identity, StorageAssetLink effectIntent,
        BackendExecution execution, CancellationToken ct) => NoEffect();
    public ValueTask<BackendEffectResult> RestorePartAsync(BackupPart part, RecoveryRequest request,
        StorageAssetLink effectIntent, BackendExecution execution, CancellationToken ct) => NoEffect();
    public ValueTask<BackendEffectResult> VerifyRecoveryPartAsync(RecoveryEntryV1 part,
        RecoveryRequest request, BackendExecution execution, CancellationToken ct) => NoEffect();
    private static StorageFault Unavailable() => new(StorageError.Unavailable, "storage.unavailable");
    private static ValueTask<BackendEffectResult> NoEffect() => ValueTask.FromResult(
        new BackendEffectResult(BackendEffectState.NoEffect, Unavailable()));
    public ValueTask DisposeAsync() {
        if (Volatile.Read(ref Active) != 0) throw new InvalidOperationException("storage.drain_incomplete");
        return ValueTask.CompletedTask;
    }
}
sealed class ReleaseBarrier : IStorageExecutionBarrier {
    public TaskCompletionSource Entered { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public TaskCompletionSource AllowRelease { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
    public async ValueTask ReachAsync(StorageBarrierPoint point, OperationIdentity identity, CancellationToken ct) {
        if (point != StorageBarrierPoint.BeforeResourceRelease) return;
        Entered.TrySetResult();
        await AllowRelease.Task.WaitAsync(ct);
    }
}
static async Task RunC1HostAsync(IStorageConfigurationResolver fixedResolver,
    RuntimeConfiguration configuration, IStorageAuthority authority, IStorageClock clock,
    IStorageDatabaseBackend database, IStorageReferenceCoordinator references,
    IStorageMaintenanceBackend maintenance, IStorageAssetBackend assets,
    FileObjectRequest fixtureRequest, FileObjectReceipt fixtureReceipt,
    StorageHealth syntheticHealth, CancellationToken suiteDeadline) {
    var files = new BlockingFileBackend(fixtureReceipt, syntheticHealth);
    var barrier = new ReleaseBarrier();
    var factory = new StorageRuntimeFactory(new StorageRuntimeDependencies(fixedResolver,
        new FixedBackendFactory(new StorageBackendSet(database, files, references, maintenance, assets)),
        clock, barrier), new StorageFactoryOptions(TimeSpan.FromSeconds(5)));
    await using var source = new MemoryStream(new byte[] { 1, 2, 3 }, writable: false);
    await using var runtime = await factory.CreateAsync(configuration, authority, suiteDeadline);
    using var callerWait = new CancellationTokenSource();
    try {
        var pending = runtime.FileObjects.StageAndSealFileAsync(fixtureRequest, source, callerWait.Token).AsTask();
        await files.Entered.Task.WaitAsync(suiteDeadline);
        callerWait.Cancel();
        var observed = await pending.WaitAsync(suiteDeadline);
        if (observed.Task is null || observed.State is StorageExecutionState.Completed
            or StorageExecutionState.ResourcesReleased || files.Active != 1 || !source.CanRead)
            throw new InvalidOperationException("storage.drain_incomplete");
        files.AllowFinish.TrySetResult();
        await barrier.Entered.Task.WaitAsync(suiteDeadline);
        var held = await runtime.GetTaskStatusAsync(new TaskQuery(fixtureRequest.Context, observed.Task), suiteDeadline);
        if (held.Status?.State != StorageExecutionState.Draining || held.Fault is not null)
            throw new InvalidOperationException("storage.drain_incomplete");
        barrier.AllowRelease.TrySetResult();
        var completed = await ObserveAsync(runtime, fixtureRequest.Context, observed,
            100, TimeSpan.FromMilliseconds(1), suiteDeadline);
        var lookup = await runtime.QueryOperationAsync(
            new OperationQuery(fixtureRequest.Context, fixtureRequest.Identity), suiteDeadline);
        if (completed.State != StorageExecutionState.Completed || lookup.Fault is not null
            || lookup.Record?.File != fixtureReceipt || files.Active != 0)
            throw new InvalidOperationException("storage.integrity_failed");
    } finally {
        files.AllowFinish.TrySetResult();
        barrier.AllowRelease.TrySetResult();
    }
}
```

5秒/100次/1毫秒仅为此有限合成夹具观察值，不是生产参数。上例OpenRead/Verify显式Unavailable是本反例未提供的能力；suite的READ/VERIFY测试必须另注入完整byte fake，以§7.1.2及§11断言验证，不得把这些拒绝计为功能通过。fixedResolver中的Profile使startup/execution budget覆盖有限suite，clock可在专门deadline用例推进；BeforeAdmission/AfterAdmission/AfterBackend/AfterResourceRelease及重复Release/Stop由同一真实Runtime分别验证。异常finally先放开fake后再await using排空，源流最后Dispose，外层watchdog超时仍仅算未完成。ObserveAsync取§7.1.1的Host辅助函数；不使用伪Runtime代替。

### 7.1.1 写宿主的公开调用片段

以下只冻结生产Host的调用与所有权收尾形状，未编译/执行；不新增模块API。factory/authority/configuration及请求来自受信任宿主，buildTransaction只在Host使用已注册codec组装原摘要/精确引用；releaseSession/releaseRead/stopFor生成固定控制身份，调用前保存请求。§7.1.0的fake闩锁只能证明软件时序，不替代本节Host的存活Owner闭包。

Host在Factory/Create之前预留固定条数及总强持字节预算的槽；容量满先拒绝，零Create/Open/Stage。预留成功后source/destination的借用权转给该Host Owner，上层只拿ticket观察，清除自己的可关闭引用，不在UI关闭、观察取消或外层WaitAsync finally中Dispose原流。只有TryReturn成功才交回流；它与“业务成功”不同，失败或Unknown也必须先真实归还。未知长度按已绑定Profile的最大对象/输出及Host保留内存上界预约，不能仅按自报ExpectedBytes预约。输入、helper、Caller、factory和端口由同slot.Body闭包强持；模块借用源流的规则不变，模块仍不关闭它。

以下Host私有辅助类型在两个消费者各自的Host中实现，不进入Contracts/Runtime，不依赖另一消费者私有工程。每个类型放独立Host源文件，static helper和Start入口放同一Host静态class，WriteHostAsync/ReadHostAsync是各Start入口内的局部函数；不能把这些方法作为类型后的顶层语句。Owner实例由应用生命周期根持有，固定数组不是静态全局状态；关闭或移交拒绝不能清空未归还槽。HostCall各槽固定一份原Task及原identity；ValueTask只转AsTask一次、保存后才await。Poll/Read/OutputWrite只在上一原Task已结束后复用固定槽，未结束时不能覆盖；Stage/Commit/Verify/Release/Stop/Dispose不重发。运行中保存Runtime/Session/ReadLease和各回执，异常后不会因async状态机结束而失去它们。

```csharp
using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Asun.Platform.StorageDatabase.Contracts;

enum HostCall {
    Create, Open, Stage, Commit, Verify, OperationLookup, Poll,
    StageObserve, CommitObserve, VerifyObserve, Read, OutputWrite,
    Release, Stop, ResourceDispose, RuntimeDispose
}
sealed class HostRetentionOwner {
    private readonly object gate = new();
    private readonly HostHold?[] slots;
    private readonly long maxBytes;
    private long heldBytes;
    public HostRetentionOwner(int maxSlots, long maxRetainedBytes) {
        if (maxSlots <= 0 || maxRetainedBytes <= 0) throw new ArgumentOutOfRangeException();
        slots = new HostHold?[maxSlots];
        maxBytes = maxRetainedBytes;
    }
    public HostHold Start(Stream? source, Stream? destination, long reservedBytes,
        Func<HostHold, Task> body) {
        ArgumentNullException.ThrowIfNull(body);
        HostHold hold;
        lock (gate) {
            if (reservedBytes <= 0 || reservedBytes > maxBytes - heldBytes)
                throw new InvalidOperationException("storage.capacity_exceeded");
            if (Array.Exists(slots, item => item is not null
                && ((source is not null && (ReferenceEquals(item.Source, source)
                    || ReferenceEquals(item.Destination, source)))
                || (destination is not null && (ReferenceEquals(item.Source, destination)
                    || ReferenceEquals(item.Destination, destination)))))
                || (source is not null && ReferenceEquals(source, destination)))
                throw new InvalidOperationException("storage.resource_busy");
            var index = Array.FindIndex(slots, item => item is null);
            if (index < 0) throw new InvalidOperationException("storage.resource_busy");
            hold = new HostHold(index, source, destination, reservedBytes, body);
            slots[index] = hold; // Factory前已有强根；未归还槽不淘汰
            heldBytes = checked(heldBytes + reservedBytes);
        }
        hold.HostTask = RunOwnedAsync(hold);
        hold.StartGate.TrySetResult(); // 原Host Task保存后才放行；固定槽限定worker数量
        return hold; // 调用者只观察；不能关闭其Source/Destination
    }
    private static async Task RunOwnedAsync(HostHold hold) {
        try {
            await hold.StartGate.Task; // RunContinuationsAsynchronously，不在UI内同步执行Factory
            await hold.Body!(hold);
        }
        catch (Exception ex) { hold.Primary ??= ex; } // 未确认清理则AllReturned仍false
    }
    public bool TryReturn(HostHold hold, out Stream? source, out Stream? destination) {
        source = destination = null;
        lock (gate) {
            if (hold.Index < 0 || hold.Index >= slots.Length
                || !ReferenceEquals(slots[hold.Index], hold)
                || hold.HostTask is not { IsCompleted: true } || !hold.AllReturned) return false;
            source = hold.Source; destination = hold.Destination;
            slots[hold.Index] = null;
            heldBytes -= hold.ReservedBytes;
            hold.Source = hold.Destination = null;
            hold.Runtime = null; hold.Session = null; hold.ReadLease = null;
            hold.Body = null; // 已完成才解除factory/请求/端口强持
            Array.Clear(hold.Calls); Array.Clear(hold.Identities);
            hold.Work.Dispose();
            return true;
        }
    }
}
sealed class HostHold(int index, Stream? source, Stream? destination, long reservedBytes,
    Func<HostHold, Task> body) {
    internal int Index { get; } = index;
    internal long ReservedBytes { get; } = reservedBytes;
    internal Stream? Source = source, Destination = destination;
    internal Func<HostHold, Task>? Body = body;
    internal Task? HostTask;
    internal readonly TaskCompletionSource StartGate = new(TaskCreationOptions.RunContinuationsAsynchronously);
    internal readonly CancellationTokenSource Work = new();
    internal readonly Task?[] Calls = new Task?[Enum.GetValues<HostCall>().Length];
    internal readonly OperationIdentity?[] Identities = new OperationIdentity?[Enum.GetValues<HostCall>().Length];
    internal IStorageDatabase? Runtime;
    internal IStorageSession? Session;
    internal IFileObjectReadLease? ReadLease;
    internal StorageTaskStatus? StageStatus, CommitStatus, VerifyStatus, StopStatus;
    internal ResourceStatus? ReleaseStatus;
    internal ResourceReleaseRequest? ReleaseRequest;
    internal StopRequest? StopRequest;
    internal OperationRecord? WriteResult;
    internal bool ReadVerified, AllReturned;
    internal Exception? Primary;
    internal readonly Exception?[] Cleanup = new Exception?[5];
    private readonly object errorGate = new();
    internal void NoteCleanup(int phase, Exception error) {
        lock (errorGate) Cleanup[phase] ??= error;
    }
    internal Task<T> Keep<T>(HostCall call, OperationIdentity? identity,
        Func<Task<T>> invoke, bool next = false) {
        var i = (int)call;
        if (Calls[i] is Task<T> prior && !next) {
            if (Identities[i] != identity) throw new InvalidOperationException("storage.conflict");
            return prior;
        }
        if (Calls[i] is { IsCompleted: false })
            throw new InvalidOperationException("storage.resource_busy");
        Identities[i] = identity; // 原identity先保存，不从异常文本猜
        try { return (Task<T>)(Calls[i] = invoke()); }
        catch (Exception ex) { return (Task<T>)(Calls[i] = Task.FromException<T>(ex)); }
    }
    internal Task Keep(HostCall call, OperationIdentity? identity, Func<Task> invoke, bool next = false) {
        var i = (int)call;
        if (Calls[i] is Task prior && !next) {
            if (Identities[i] != identity) throw new InvalidOperationException("storage.conflict");
            return prior; // 不二次Dispose在途或已失败原调用
        }
        if (Calls[i] is { IsCompleted: false })
            throw new InvalidOperationException("storage.resource_busy");
        Identities[i] = identity;
        try { return Calls[i] = invoke(); }
        catch (Exception ex) { return Calls[i] = Task.FromException(ex); }
    }
    internal async Task<bool> ObserveAsync(TimeSpan waitBudget, TimeSpan cleanupBudget,
        CancellationToken viewerCancellation) {
        if (waitBudget <= TimeSpan.Zero || cleanupBudget <= TimeSpan.Zero)
            throw new ArgumentOutOfRangeException();
        var original = HostTask ?? throw new InvalidOperationException("storage.resource_busy");
        try { await original.WaitAsync(waitBudget, viewerCancellation); }
        catch (Exception ex) when (ex is TimeoutException or OperationCanceledException) {
            try { Work.Cancel(); }
            catch (Exception cancelError) { NoteCleanup(4, cancelError); }
            // 独立有限观察同一Host Task；不将超时改写为释放成功
            try { await original.WaitAsync(cleanupBudget, CancellationToken.None); }
            catch (TimeoutException) { return false; }
        }
        return original.IsCompleted && AllReturned;
    }
}
```

Start成功是借用接纳边界；任何已有流的外层await using必须在该边界前结束其关闭职责，不能在ticket观察超时后运行旧finally关闭流。TryReturn=false时原Owner继续持有同slot/HostTask/源流/端口，停止新增工作并按已保存任务/handle查询；其它Owner拒绝转交或UI未接收通知不改变该强根。示例不依赖退出事件、GC finalizer或Task.Run丢弃任务；Owner的关闭只能报告有未归还槽，不能Dispose Work或清空槽。TryReturn后Primary与Cleanup按不同字段保留，原异常不被清理异常替换；ReadVerified/WriteResult也不因Dispose成功而变成功。报告只投影固定错误键，不向操作员展示Exception或源流。

Owner.Start的预留/拒绝和TryReturn在同gate内线性化，流与整个Host任务只归该slot的原Owner；同一源/输出流重复占槽接纳前ResourceBusy，不能并发复用借用。启动闩锁在构造slot时创建，HostTask先保存再放行，固定槽限定worker数量，不增加无界Task.Run队列；原调用返回ValueTask后立即保存其唯一AsTask，若调用尚未返回，则原worker/启动阶段仍被整个HostTask强持。另一个Owner调用TryReturn必因槽引用不符而失败，不能以相同index冒认。UI线程仅调用有限观察，不能直接改内部Calls/端口字段。Keep槽由该Host worker串行写，外部观察只等HostTask并请求Work合作取消；恢复查询仍由原Owner单一调度，先等已保存的Poll/Reader Task结束，未结束不启动第二个查询。无Runtime时只观察原Create/Host Task；有Runtime时按保存的Stage/Commit/Verify/Release/Stop回执取原handle调用既有GetTaskStatus/Resource查询，并保存该查询Task。Dispose已成功结束后不再对它查询；清理失败或观察仍未知保留槽，不能据Task fault、GC或一次NotFound判归还。输入/输出流只借用不由示例Host清理关闭，实际借用归还由两资源Dispose成功且原Host Task结束证明。

清理先启动并保存原Release、Stop和两次不同资源的Dispose Task，再嵌套await；因此某个Release/Dispose不配合也不会漏掉Runtime关闭接纳。ResourceDispose与RuntimeDispose分别最多一次，后者复用已保存的原Stop；同一资源在途时不得再Invoke Dispose。Release/Stop的Fault或非终态都不能证明释放；仅其对应Dispose原Task实际成功才作归还证明。Dispose自身没有超时，有限的是上面ObserveAsync对整个原Host Task的观察，不给Dispose加取消token或另建Runtime接管。

```csharp
static async Task CleanupHostAsync(HostHold hold,
    Func<ResourceHandle, ResourceReleaseRequest> releaseFor, Func<string, StopRequest> stopFor) {
    var runtime = hold.Runtime;
    IAsyncDisposable? resource = (IAsyncDisposable?)hold.Session ?? hold.ReadLease;
    Task<ResourceStatus>? release = null;
    Task<StorageTaskStatus>? stop = null;
    Task? resourceDispose = null, runtimeDispose = null;
    var resourceReturned = resource is null;
    var runtimeReturned = runtime is null; // Create/Open已真实结束的失败，内部回滚仍归工厂/Runtime
    try {
        if (resource is not null) {
            var handle = hold.Session?.Handle ?? hold.ReadLease!.Handle;
            var request = releaseFor(handle);
            hold.ReleaseRequest = request;
            release = hold.Keep(HostCall.Release, request.Identity, () => hold.Session is not null
                ? hold.Session.ReleaseAsync(request, CancellationToken.None).AsTask()
                : hold.ReadLease!.ReleaseAsync(request, CancellationToken.None).AsTask());
        }
    } catch (Exception ex) { hold.NoteCleanup(0, ex); }
    finally {
        try {
            if (runtime is not null) {
                var request = stopFor(runtime.InstanceEpoch);
                hold.StopRequest = request;
                stop = hold.Keep(HostCall.Stop, request.Identity,
                    () => runtime.StopAsync(request, CancellationToken.None).AsTask());
            }
        } catch (Exception ex) { hold.NoteCleanup(1, ex); }
        finally {
            try {
                if (resource is not null)
                    resourceDispose = hold.Keep(HostCall.ResourceDispose,
                        hold.ReleaseRequest?.Identity, () => resource.DisposeAsync().AsTask());
            } catch (Exception ex) { hold.NoteCleanup(2, ex); }
            finally {
                try {
                    if (runtime is not null)
                        runtimeDispose = hold.Keep(HostCall.RuntimeDispose,
                            hold.StopRequest?.Identity, () => runtime.DisposeAsync().AsTask());
                } catch (Exception ex) { hold.NoteCleanup(3, ex); }
            }
        }
    }
    try {
        if (release is not null) {
            hold.ReleaseStatus = await release;
            if (hold.ReleaseStatus.Fault is not null)
                throw new InvalidOperationException(hold.ReleaseStatus.Fault.DiagnosticKey);
        }
    } catch (Exception ex) { hold.NoteCleanup(0, ex); }
    finally {
        try {
            if (stop is not null) {
                hold.StopStatus = await stop;
                if (hold.StopStatus.Fault is not null)
                    throw new InvalidOperationException(hold.StopStatus.Fault.DiagnosticKey);
            }
        } catch (Exception ex) { hold.NoteCleanup(1, ex); }
        finally {
            try {
                if (resourceDispose is not null) { await resourceDispose; resourceReturned = true; }
            } catch (Exception ex) { hold.NoteCleanup(2, ex); }
            finally {
                try {
                    if (runtimeDispose is not null) { await runtimeDispose; runtimeReturned = true; }
                } catch (Exception ex) { hold.NoteCleanup(3, ex); }
            }
        }
    }
    hold.AllReturned = resourceReturned && runtimeReturned;
}
static async Task<StorageTaskStatus> ObserveHeldAsync(HostHold hold, IStorageDatabase runtime,
    CallContext context, StorageTaskStatus status, int attempts, TimeSpan interval, CancellationToken ct) {
    if (attempts <= 0 || interval <= TimeSpan.Zero) throw new ArgumentOutOfRangeException();
    for (var i = 0; i < attempts; i++) {
        if (status.State is StorageExecutionState.Completed or StorageExecutionState.RequestRejected)
            return status;
        var handle = status.Task ?? throw new InvalidOperationException("storage.invalid_input");
        var lookup = await hold.Keep(HostCall.Poll, status.Identity,
            () => runtime.GetTaskStatusAsync(new TaskQuery(context, handle), ct).AsTask(), next: true);
        if (lookup.Fault is not null || lookup.Status is null)
            throw new InvalidOperationException(lookup.Fault?.DiagnosticKey ?? "storage.invalid_input");
        status = lookup.Status;
        if (i + 1 < attempts && status.State != StorageExecutionState.Completed)
            await Task.Delay(interval, ct);
    }
    if (status.State == StorageExecutionState.Completed) return status;
    throw new TimeoutException("storage.drain_incomplete");
}
// 只供§7.1.0/§7.1.3已在测试Host根中持有的夹具复用；生产调用必须使用上面的held版本。
static async Task<StorageTaskStatus> ObserveAsync(IStorageDatabase runtime, CallContext context,
    StorageTaskStatus status, int attempts, TimeSpan interval, CancellationToken ct) {
    if (attempts <= 0 || interval <= TimeSpan.Zero) throw new ArgumentOutOfRangeException();
    for (var i = 0; i < attempts; i++) {
        if (status.State is StorageExecutionState.Completed or StorageExecutionState.RequestRejected)
            return status;
        var handle = status.Task ?? throw new InvalidOperationException("storage.invalid_input");
        var lookup = await runtime.GetTaskStatusAsync(new TaskQuery(context, handle), ct);
        if (lookup.Fault is not null || lookup.Status is null)
            throw new InvalidOperationException(lookup.Fault?.DiagnosticKey ?? "storage.invalid_input");
        status = lookup.Status;
        if (i + 1 < attempts && status.State != StorageExecutionState.Completed)
            await Task.Delay(interval, ct);
    }
    if (status.State == StorageExecutionState.Completed) return status;
    throw new TimeoutException("storage.drain_incomplete");
}
```

ObserveAsync是原夹具轮询，由Runtime.Tests的suite根持原Host Task/查询Task，不在生产Host调用。它不是模块API，夹具异常finally解除所有fake闩锁；外层watchdog仍只判未完成。两个消费者生产入口如下，Start之外只观察ticket；Create原Task尚未交Runtime时保持槽也已存在，工厂继续负责未交付后端回滚。迟到Create先写hold.Runtime、迟到Open先写hold.Session/ReadLease，再观察Work取消进入同一finally，不能丢弃成功返回的资源。Create异常只有在原Task结束且工厂完成回滚后才允许runtime=null视为归还。

```csharp
static HostHold StartWriteHost(HostRetentionOwner owner, long reservedBytes,
    IStorageRuntimeFactory factory, RuntimeConfiguration configuration, IStorageAuthority authority,
    SessionRequest sessionRequest, FileObjectRequest fileRequest, Stream source,
    Func<ObjectRef, RegisteredTransactionRequest> buildTransaction,
    Func<ResourceHandle, ResourceReleaseRequest> releaseSession, Func<string, StopRequest> stopFor,
    int pollAttempts, TimeSpan pollInterval) {
    return owner.Start(source, null, reservedBytes, WriteHostAsync);
    async Task WriteHostAsync(HostHold hold) {
    var ct = hold.Work.Token;
    try {
        hold.Runtime = await hold.Keep(HostCall.Create, null,
            () => factory.CreateAsync(configuration, authority, ct).AsTask());
        ct.ThrowIfCancellationRequested();
        var opened = await hold.Keep(HostCall.Open, null,
            () => hold.Runtime.OpenSessionAsync(sessionRequest, ct).AsTask());
        hold.Session = opened.Session; // 成功先交付则先接管，再核取消
        if (opened.Fault is not null || hold.Session is null)
            throw new InvalidOperationException(opened.Fault?.DiagnosticKey ?? "storage.invalid_input");
        ct.ThrowIfCancellationRequested();
        hold.StageStatus = await hold.Keep(HostCall.Stage, fileRequest.Identity,
            () => hold.Runtime.FileObjects.StageAndSealFileAsync(fileRequest, hold.Source!, ct).AsTask());
        var sealedStatus = await hold.Keep(HostCall.StageObserve, fileRequest.Identity,
            () => ObserveHeldAsync(hold, hold.Runtime, fileRequest.Context, hold.StageStatus,
                pollAttempts, pollInterval, ct));
        var file = sealedStatus.Result?.File;
        if (sealedStatus.State != StorageExecutionState.Completed
            || file is not { State: FileState.SealedDurable, Object: not null })
            throw new InvalidOperationException(sealedStatus.Result?.Fault?.DiagnosticKey
                ?? sealedStatus.Fault?.DiagnosticKey ?? "storage.save_not_completed");
        var transaction = buildTransaction(file.Object);
        hold.CommitStatus = await hold.Keep(HostCall.Commit, transaction.Identity,
            () => hold.Session.ExecuteTransactionAsync(transaction, ct).AsTask());
        var completed = await hold.Keep(HostCall.CommitObserve, transaction.Identity,
            () => ObserveHeldAsync(hold, hold.Runtime, transaction.Context, hold.CommitStatus,
                pollAttempts, pollInterval, ct));
        var record = completed.Result;
        if (record?.State == StoredOperationState.Unknown) {
            var lookup = await hold.Keep(HostCall.OperationLookup, transaction.Identity,
                () => hold.Runtime.QueryOperationAsync(
                    new OperationQuery(transaction.Context, transaction.Identity), ct).AsTask());
            if (lookup.Fault is not null || lookup.Record is null)
                throw new InvalidOperationException(lookup.Fault?.DiagnosticKey ?? "storage.invalid_input");
            record = lookup.Record;
        }
        if (record is not { State: StoredOperationState.Committed, Commit: not null })
            throw new InvalidOperationException(record?.Fault?.DiagnosticKey
                ?? completed.Fault?.DiagnosticKey ?? "storage.save_not_completed");
        hold.WriteResult = record;
    } catch (Exception ex) { hold.Primary ??= ex; }
    finally { await CleanupHostAsync(hold, releaseSession, stopFor); }
    }
}
```

WriteHostAsync是入口内的局部函数，其闭包由slot.Body显式持有；不是全局状态。Source借用在原Host Task和清理Task真实结束前始终由slot强持。业务观察超限、helper错误、提交Unknown都走同一清理；外部Host观察有限，内部Dispose继续等原资源，不能关闭source、重传原文件或换Runtime。成功要求WriteResult为Committed、Primary/Cleanup均无错误、AllReturned且原HostTask结束；单有Task.IsCompleted或业务回执不够。

调用层必须按下面的借用交接形状关闭原流，拒绝前流仍归原调用者；该包装方法收到source时，上层已经将自己的可关闭字段置null，只允许包装方法管理关闭。Start成功后localSource置null，异常finally只会关闭未被接纳的流。TryReturn成功后流才重新归调用者，之后的输出/关闭错误不回溯改写存储事实。以下封装仍是Host helper，其他参数取StartWriteHost已冻结的可信输入；如果上层不能交出全部关闭职责，则接纳前拒绝而非假装强引用能阻止外部Dispose。

```csharp
Stream? localSource = source; // 位于Host方法内；外层不能再对source使用await using
HostHold? ticket = null;
try {
    ticket = StartWriteHost(owner, reservedBytes, factory, configuration, authority,
        sessionRequest, fileRequest, localSource, buildTransaction, releaseSession, stopFor,
        pollAttempts, pollInterval);
    localSource = null; // 原Owner已接纳，UI/外层finally失去关闭权
    var returned = await ticket.ObserveAsync(waitBudget, cleanupBudget, viewerCancellation);
    if (returned && owner.TryReturn(ticket, out var returnedSource, out _)) {
        if (returnedSource is not null) await returnedSource.DisposeAsync();
        // 业务成功另核ticket.WriteResult、Primary及Cleanup，不以归还代替Committed。
    }
    // false或异常时ticket仍在owner固定槽中；不能在这里Dispose source或重开Runtime。
} finally {
    if (localSource is not null) await localSource.DisposeAsync(); // 只关闭Start拒绝前的原流
}
```

### 7.1.2 独立读 CLI 的公开调用片段

此消费者在自己的Host内实现上述私有Owner/保持/清理辅助，不引用写消费者私有工程。ObjectRef来自Owner公开投影；readRequest为Offset=0/Count=Object.Bytes，destination借用随ticket交给读Host，在TryReturn前不可关闭/复用。每次ReadAsync/输出WriteAsync原Task保存在固定槽，只有完成后复用，原Host Task保存hash器/缓冲直至实际IO结束；64KiB仅为示例缓冲，Host预约包含它。先校验实际输出长度/hash，再显式Verify对象；异常输出隔离，不当已验对象。

```csharp
using System.Security.Cryptography;

static HostHold StartReadHost(HostRetentionOwner owner, long reservedBytes,
    IStorageRuntimeFactory factory, RuntimeConfiguration configuration, IStorageAuthority authority,
    FileReadRequest readRequest, FileVerificationRequest verification, Stream destination,
    Func<ResourceHandle, ResourceReleaseRequest> releaseRead, Func<string, StopRequest> stopFor,
    int pollAttempts, TimeSpan pollInterval) {
    return owner.Start(null, destination, reservedBytes, ReadHostAsync);
    async Task ReadHostAsync(HostHold hold) {
    var ct = hold.Work.Token;
    try {
        if (readRequest.Offset != 0 || readRequest.Count != readRequest.Object.Bytes
            || verification.Object != readRequest.Object)
            throw new ArgumentException("storage.invalid_input");
        hold.Runtime = await hold.Keep(HostCall.Create, null,
            () => factory.CreateAsync(configuration, authority, ct).AsTask());
        ct.ThrowIfCancellationRequested();
        var opened = await hold.Keep(HostCall.Open, null,
            () => hold.Runtime.FileObjects.OpenReadAsync(readRequest, ct).AsTask());
        hold.ReadLease = opened.Lease;
        if (opened.Fault is not null || hold.ReadLease is null)
            throw new InvalidOperationException(opened.Fault?.DiagnosticKey ?? "storage.invalid_input");
        ct.ThrowIfCancellationRequested();
        using var hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        var buffer = new byte[64 * 1024];
        long bytes = 0;
        int count;
        while ((count = await hold.Keep(HostCall.Read, null,
            () => hold.ReadLease.Content.ReadAsync(buffer.AsMemory(), ct).AsTask(), next: true)) != 0) {
            bytes = checked(bytes + count);
            if (bytes > readRequest.Count) throw new InvalidOperationException("storage.integrity_failed");
            hash.AppendData(buffer, 0, count);
            await hold.Keep(HostCall.OutputWrite, null,
                () => hold.Destination!.WriteAsync(buffer.AsMemory(0, count), ct).AsTask(), next: true);
        }
        if (bytes != readRequest.Object.Bytes
            || Convert.ToHexString(hash.GetHashAndReset()).ToLowerInvariant() != readRequest.Object.Hash.Hex)
            throw new InvalidOperationException("storage.integrity_failed");
        hold.VerifyStatus = await hold.Keep(HostCall.Verify, verification.Identity,
            () => hold.Runtime.FileObjects.VerifyAsync(verification, ct).AsTask());
        var verified = await hold.Keep(HostCall.VerifyObserve, verification.Identity,
            () => ObserveHeldAsync(hold, hold.Runtime, verification.Context, hold.VerifyStatus,
                pollAttempts, pollInterval, ct));
        if (verified.State != StorageExecutionState.Completed
            || verified.Result?.File?.State != FileState.Verified)
            throw new InvalidOperationException(verified.Result?.Fault?.DiagnosticKey
                ?? verified.Fault?.DiagnosticKey ?? "storage.integrity_failed");
        hold.ReadVerified = true;
    } catch (Exception ex) { hold.Primary ??= ex; }
    finally { await CleanupHostAsync(hold, releaseRead, stopFor); }
    }
}
```

ticket.ObserveAsync使用有限waitBudget以及独立cleanupBudget，不复用已取消viewer token观察清理。false表示原Owner仍在强持，不能交付/关闭destination或将槽标Released；true还须核Primary/Cleanup与ReadVerified，才交付已验输出。Owner.TryReturn是唯一流借用归还点，返回false（包括错误Owner、原Task未结束或释放未确认）保留原槽；返回true才允许原调用者关闭/重用流。清理Task失败即使HostTask已结束也默认保留端口和槽，以同Runtime已有Task/Resource/Stop handle有限查询恢复；不能第二次Dispose在途、创建新Runtime替代未排空实例或凭NotFound解除强持。C1注入与这些Host片段均未运行，A1/A2真实门保持。

### 7.1.3 维护快照读取与隔离恢复CLI

调用顺序为按原identity QueryOperation→确认MaintenanceReceipt.Artifact→构造MaintenanceV1 link（Creator=receipt.Identity）→ReadMaintenance→取准确Journal/Closure/RestorePoint/Recovery link→读header和全部分页→按header总数/必需项核完整性。未知receipt只读回查，不能用读口续作GC或恢复。以下Host helper只读取某个成功Backup的closure；page budget由当前已注册Profile注入，最多轮次按MaxClosureItems/MaxEntries算出并用checked限额，不造生产数字。恢复CLI另外调用RestoreIsolatedAsync和VerifyRecoveryAsync，等原Task到Completed后用RecoveryV1逐项验证，始终无设备/发送worker。

```csharp
static async Task InspectClosureAsync(IStorageDatabase runtime, CallContext context,
    MaintenanceReceipt receipt, int pageEntries, int pageBytes, int maxPages, CancellationToken ct) {
    if (receipt.Kind != MaintenanceKind.Backup || receipt.State != MaintenanceState.Complete
        || receipt.Artifact is null || maxPages <= 0)
        throw new ArgumentException("storage.invalid_input");
    var artifact = new StorageAssetLink(receipt.Artifact, StorageAssetSchema.MaintenanceV1, receipt.Identity);
    var read = await runtime.Maintenance.ReadMaintenanceAsync(new StorageAssetQuery(context, artifact), ct);
    if (read.Fault is not null || read.Header?.Closure is null)
        throw new InvalidOperationException(read.Fault?.DiagnosticKey ?? "storage.integrity_failed");
    var closure = read.Header.Closure;
    var header = await runtime.Maintenance.ReadClosureAsync(new StorageAssetQuery(context, closure), ct);
    if (header.Fault is not null || header.Header is not { Complete: true })
        throw new InvalidOperationException(header.Fault?.DiagnosticKey ?? "storage.not_restorable");
    StorageAssetCursor? cursor = null;
    long items = 0;
    long bytes = 0;
    for (var pageNumber = 0; pageNumber < maxPages; pageNumber++) {
        var page = await runtime.Maintenance.ReadClosureEntriesAsync(
            new StorageAssetPageQuery(context, closure, cursor, pageEntries, pageBytes), ct);
        if (page.Fault is not null) throw new InvalidOperationException(page.Fault.DiagnosticKey);
        foreach (var item in page.Entries) {
            if (item.Sequence != items || (item.Required && (!item.Verified || item.Fault is not null)))
                throw new InvalidOperationException("storage.not_restorable");
            items = checked(items + 1);
            bytes = checked(bytes + item.Part.Bytes);
        }
        if (page.Next is null) {
            if (items != header.Header.ItemCount || bytes != header.Header.TotalBytes)
                throw new InvalidOperationException("storage.integrity_failed");
            return;
        }
        if (page.Next.Asset != closure || page.Next.NextSequence != items)
            throw new InvalidOperationException("storage.integrity_failed");
        cursor = page.Next;
    }
    throw new InvalidOperationException("storage.capacity_exceeded");
}
```

Header/page取消均等其Reader/内部分配释放后返回，不持久读lease到下一页；资产保留与权限由同snapshot保障。不能只检查这段计数后称字节已现场验过；Verified是该资产原封口时记录的证据，隔离恢复仍需对实际恢复内容全量验证。

中断维护的Host按当前证据读取Journal后显式调用，下面original为原GC请求、expectedAttempt取已核技术证据；它们不能由“最新文件”推断。Backup/Migration/Recovery分别换用对应封闭ResumeInput。拒绝/Unknown时保留该请求及原身份回查，不递增expectedAttempt盲重跑。

```csharp
static async Task<StorageTaskStatus> ResumeGcHostAsync(IStorageDatabase runtime,
    CallContext currentContext, GcRequest original, StorageAssetLink journal,
    int expectedAttempt, int pollAttempts, TimeSpan pollInterval, CancellationToken ct) {
    var request = new MaintenanceResumeRequest(currentContext, original.Identity,
        journal, expectedAttempt, new GcResumeInput(original));
    var started = await runtime.ResumeMaintenanceAsync(request, ct);
    return await ObserveAsync(runtime, currentContext, started, pollAttempts, pollInterval, ct);
}
```

维护测试Host另以真实组合器执行，以下resolved必须与resolver返回同一精确快照；fake文件目录含3/5byte两对象，reference fake只保护5byte对象，clock固定夹具UTC/单调戳，工厂/authority范围匹配。buildGc仅在Host用Plan及新固定identity组装GcRequest并重算hash；不得把delegate传入模块事务。

```csharp
static async Task RunMaintenanceHostAsync(ResolvedStorageConfiguration resolved,
    IStorageConfigurationResolver resolver, RuntimeConfiguration configuration,
    IStorageAuthority authority, IStorageClock clock, IStorageExecutionBarrier barrier,
    IStorageDatabaseBackend databaseFake, IStorageFileBackend filesFake,
    IStorageReferenceCoordinator referencesFake, IStorageAssetBackend assetsFake,
    GcPlanRequest planRequest, Func<VersionRef, GcRequest> buildGc,
    int pollAttempts, TimeSpan pollInterval, CancellationToken ct) {
    var maintenance = new StorageMaintenanceBackend(resolved, databaseFake, filesFake,
        referencesFake, assetsFake, clock);
    var factory = new StorageRuntimeFactory(new StorageRuntimeDependencies(resolver,
        new FixedBackendFactory(new StorageBackendSet(databaseFake, filesFake, referencesFake,
            maintenance, assetsFake)), clock, barrier), new StorageFactoryOptions(TimeSpan.FromSeconds(5)));
    await using var runtime = await factory.CreateAsync(configuration, authority, ct);
    var plan = await runtime.PlanOrphanCollectionAsync(planRequest, ct);
    if (plan.Fault is not null || plan.Plan is null || plan.CandidateCount != 1 || plan.CandidateBytes != 3)
        throw new InvalidOperationException("storage.integrity_failed");
    var planLink = new StorageAssetLink(plan.Plan, StorageAssetSchema.GcPlanV1, planRequest.Identity);
    var planRead = await runtime.Maintenance.ReadGcPlanAsync(new StorageAssetQuery(planRequest.Context, planLink), ct);
    if (planRead.Fault is not null || planRead.Header?.CandidateCount != 1)
        throw new InvalidOperationException("storage.integrity_failed");
    var gc = buildGc(plan.Plan);
    var started = await runtime.CollectEligibleOrphansAsync(gc, ct);
    var ended = await ObserveAsync(runtime, gc.Context, started, pollAttempts, pollInterval, ct);
    var receipt = ended.Result?.Maintenance;
    if (receipt is not { Kind: MaintenanceKind.Gc, State: MaintenanceState.Collected,
            Artifact: not null, CompletedCount: 1, FailedCount: 0, UnknownCount: 0 })
        throw new InvalidOperationException("storage.integrity_failed");
    var snapshot = await runtime.Maintenance.ReadMaintenanceAsync(new StorageAssetQuery(gc.Context,
        new StorageAssetLink(receipt.Artifact, StorageAssetSchema.MaintenanceV1, gc.Identity)), ct);
    if (snapshot.Fault is not null || snapshot.Header is null)
        throw new InvalidOperationException("storage.integrity_failed");
    var journal = await runtime.Maintenance.ReadJournalEntriesAsync(new StorageAssetPageQuery(gc.Context,
        snapshot.Header.Journal, null, resolved.Profile.Maintenance.MaxAssetPageEntries,
        resolved.Profile.Maintenance.MaxAssetPageBytes), ct);
    if (journal.Fault is not null || journal.Entries.IsEmpty)
        throw new InvalidOperationException("storage.integrity_failed");
}
```

完整C1-MAINTENANCE用例继续读完journal并核最后Delete/EffectConfirmed；上例只展示组合器/公开读取接线。fixture retention允许立即执行隔离后清理，保护5byte对象始终不移/删；另一个反例在Plan后新增3byte对象引用，真实组合器必须返回保护Skipped并使File fake的Delete调用数为0。测试前后fake对象字节核验是软件断言，不是文件系统/介质资格。

### 7.1.4 两个独立Host的真实适配接线

本节复用§7.1.1–7.1.2完整Start/Owner/Keep/Cleanup/TryReturn实现，不把fake改名当真实backend。两个Host分别独立构建，只引用Contracts/Runtime/PostgreSql/FileSystem及BCL；写Host属于inspection-evidence宿主Repository，读Host属于独立Replay/Query CLI。各自实现§6.7.2唯一Host私有PostgreSqlFileBackendFactory及自己的Owner/helper，不引用对方工程、私表或内部状态。构造工厂只保存已验输入，不打开配置流、根、池或秘密；全部外部分配发生在Owner.Start预留后的原Create Task内。

下面片段为两个Host各自静态class中的方法签名/接线；所需类型来自§6/§6.7，using包含Runtime、PostgreSql、FileSystem namespace。documents/credentials/resolver/clock/barrier均由本Host显式注入，barrier为Host实现的无操作生产barrier（ReachAsync只核ct后返回CompletedTask），不使用ReleaseBarrier或任何fake backend。resolver提供已绑定同版本的ResolvedStorageConfiguration；PostgreSQL/根输入只由上述真实工厂解析，不能让resolver提前建池/目录。

```csharp
// 写Host内；本方法不建立外部资源，source接纳/强持由StartWriteHost负责。
static HostHold StartRealEvidenceWrite(HostRetentionOwner owner, long reservedBytes,
    IStorageTrustedDocumentSource documents, IPostgreSqlCredentialSource credentials,
    ImmutableArray<IPostgreSqlBindingCodec> ownerCodecs,
    IStorageConfigurationResolver resolver, IStorageClock clock, IStorageExecutionBarrier barrier,
    StoragePostgreSqlFactoryOptions pgOptions, StorageFileSystemFactoryOptions fileOptions,
    StorageFactoryOptions runtimeOptions, RuntimeConfiguration configuration,
    IStorageAuthority authority, SessionRequest session, FileObjectRequest file, Stream source,
    Func<ObjectRef, RegisteredTransactionRequest> buildTransaction,
    Func<ResourceHandle, ResourceReleaseRequest> releaseSession, Func<string, StopRequest> stopFor,
    int pollAttempts, TimeSpan pollInterval) {
    var pg = new StoragePostgreSqlBackendFactory(documents, credentials, ownerCodecs, pgOptions);
    var fs = new StorageFileSystemBackendFactory(documents, fileOptions);
    var factory = new StorageRuntimeFactory(new StorageRuntimeDependencies(resolver,
        new PostgreSqlFileBackendFactory(pg, fs), clock, barrier), runtimeOptions);
    return StartWriteHost(owner, reservedBytes, factory, configuration, authority, session, file,
        source, buildTransaction, releaseSession, stopFor, pollAttempts, pollInterval);
}
// 独立读CLI内；无写Host类型/私表/连接依赖，destination同样经自己的Owner接纳。
static HostHold StartRealReplayRead(HostRetentionOwner owner, long reservedBytes,
    IStorageTrustedDocumentSource documents, IPostgreSqlCredentialSource credentials,
    ImmutableArray<IPostgreSqlBindingCodec> registeredReadCodecs,
    IStorageConfigurationResolver resolver, IStorageClock clock, IStorageExecutionBarrier barrier,
    StoragePostgreSqlFactoryOptions pgOptions, StorageFileSystemFactoryOptions fileOptions,
    StorageFactoryOptions runtimeOptions, RuntimeConfiguration configuration,
    IStorageAuthority authority, FileReadRequest read, FileVerificationRequest verify, Stream destination,
    Func<ResourceHandle, ResourceReleaseRequest> releaseRead, Func<string, StopRequest> stopFor,
    int pollAttempts, TimeSpan pollInterval) {
    var pg = new StoragePostgreSqlBackendFactory(documents, credentials, registeredReadCodecs, pgOptions);
    var fs = new StorageFileSystemBackendFactory(documents, fileOptions);
    var factory = new StorageRuntimeFactory(new StorageRuntimeDependencies(resolver,
        new PostgreSqlFileBackendFactory(pg, fs), clock, barrier), runtimeOptions);
    return StartReadHost(owner, reservedBytes, factory, configuration, authority, read, verify,
        destination, releaseRead, stopFor, pollAttempts, pollInterval);
}
```

两方法接纳前核reservedBytes覆盖Host强持对象、catalog/secret上限、源/输出最大量及固定缓冲；额度计算取已绑定Profile/Bootstrap，不采用ExpectedBytes自报值。Host配置不足即拒接纳，零Create；输入流关闭职责交接照§7.1.1包装，输出照§7.1.2。构造器/Start抛异常时原调用方仍持流，Start成功后只保留ticket观察，迟到Runtime/lease由原slot接管。两Host的配置source可各自从已授权配置服务或exact本地登记读取；秘密source属可信启动，CLI普通参数只接受已登记ProfileId与Owner公开ObjectRef，不接受自由连接串、根、SQL或密码。读CLI的ControlContext只授该实例create/stop，当前数据上下文仅file_read/file_verify/operation_read及必要查询/释放，不能借启动凭据调用领域写/GC/迁移。

| 独立消费者 | 正常完整流程及成功断言 | 失败/取消/恢复及归还断言 |
|---|---|---|
| Evidence Repository写Host | 固定Owner codec/SQL/Profile与新stage/transaction各自原Identity；StartRealEvidenceWrite→真实Create→OpenSession Production→原source流式封口→Completed+SealedDurable→用回执完整ObjectRef构造注册领域事务→Completed+Committed→Session Release/Runtime Stop/两Dispose完成→原HostTask完成→自己的Owner.TryReturn。WriteResult保留精确Commit，之后才归还/关闭source | startup解析/TLS/ACL/schema失败只在内部完整清理后结束Create；stage失败零领域事务；commit响应丢失沿原transaction identity QueryOperation，不重传source、不换key。Primary/Cleanup分轴，有限观察到期保留slot、原Create/Stage/Commit/Release/Stop/Dispose Task及所有端口。进程仍活且未排空时不另开Runtime；全部原借用归还、实例已关或原进程已终止后，新的受管恢复Host才可按原耐久identity只读回查，未知旧writer仍不得执行effect |
| Replay/Query读CLI | 只取得Owner公开投影的完整ObjectRef，Offset=0/Count=Bytes；StartRealReplayRead→自己的真实Runtime→OpenRead/Read lease→固定缓冲全读到自己的destination并独立核总长度/hash→原Verify Completed+Verified→lease Release/Stop/两Dispose完成→HostTask完成→自己的TryReturn后交付输出。元数据、root、token与写Host相同技术权威，不共享其内存/私表 | 错tenant/generation/描述拒绝；缺/损坏文件IntegrityFailed，失败输出不交付。取消、输出Write失败或读native未排空时自己的slot保留destination/原IO Task，不能关闭输出或再次OpenRead替代。原资源真实归还后可按同ObjectRef在新受管读Host重读，不修改原ObjectRef/hash，不自动修catalog/文件；Verify成功不增加FileDurability/业务PASS资格 |

两个Host可在不同进程同时读写同一已批准根，参与同一Authority及跨进程guard，不需要共享static单例。真实测试夹具使用隔离PG18数据库/角色/预置根和登记值；文件耐久Profile只有真实资格通过才为VerifiedDurable。未验证介质会使写Host在SealedDurable前置处停止，是明确阻断而非fake成功；读/完整性子切片可另行按精确范围接收。独立编译、读回真实字节、错误/恢复及释放检查都属于待执行验证，本轮没有运行。

隔离恢复CLI是第三个管理消费者，复用同一真实组合工厂及自己的有界Owner。它在Factory前预约并保存原Create/Backup/Restore/VerifyRecovery/页读/Resume/Stop/Dispose任务，各操作固定原identity；无流时用owner.Start(null,null,reservedBytes,body)，body强持原Request/Closure/RestorePoint/目标及每次原Task，finally显式Stop/Dispose，只有原Task与全部工具/Reader/资源Dispose成功才置AllReturned。页读及maintenance原Task同样固定槽保存，轮询只在上一Task退出后复用；维护槽是本CLI私有固定enum，不扩展已接收C1 HostCall。调用Backup后经§7.1.3完整读取准确Closure/RestorePoint；RestoreIsolated/VerifyRecovery等至Completed并逐必需项/实际target核RecoveryV1；Unknown只读原head，获maintenance_resume后才按原Journal/ExpectedAttempt调用已冻结Resume，绝不自动改target/cut。工具启动/退出未知使原Owner保留子进程及Task，不因CLI窗口关闭清槽。两数据消费者无需持有维护工具权限。

### 7.2 技术事务、窄读取和批量

ExecuteTransactionAsync 只执行注册 Binding 的一个原子业务批次；空批次是否 no-op 由 Binding 显式定义，未定义则 InvalidInput。引用集合先验证文件状态/精确描述并取得发布保持，再争唯一 operation、同事务领域写/引用/回执，最终排空。一个批次全回滚或全提交，不返回部分成功；跨多个已独立提交批次，宿主逐批固定原身份与回执，本模块不能宣称整体回滚。batch rows/bytes、结果字节和命令数有界，超限在开始事务前拒绝。窄读取使用单独 ReadAsync/RegisteredReadRequest/OwnerReadResult，不经 ExecuteTransactionAsync，不写 operation ledger 或领域数据；绑定必须 read-only、Query 池，投影返回有限 ResultSchema/Bytes/References。它不建立跨页总体、不授权写入；参数 codec 和 read predicate 归 Owner，通用 DSL 仍归 query。

OperationQuery 首先核当前查询授权，再读原权威 operation；NotFound/InProgress/Unknown 三者不能混同。已持久的回执精确重放原 ResultSchema/ResultBytes/对象集合/commit UTC，不重签为新操作，不用当前 codec 改旧 hash。实例任务状态查询不能代替这个耐久事实查询。

### 7.3 Schema 迁移与回退

迁移由已注册 Plan 指定 from/to Schema、每 step id/hash、预检条件、事务内/事务外标记、验证查询、最低空间、锁/执行 budget、兼容读写区间和失败恢复规则。运行角色没有 DDL 权限；唯一迁移 Owner/fence 取得后重读实际 Schema 与迁移历史，同时验证版本/hash。两个 migrator、同 step 异 hash、历史缺失或实际结构不符必须 MigrationBlocked，不能只看单个版本号/最后一条历史记录。

顺序冻结为 expand→逐块幂等回填→实际 Schema/行完整性验证→新读写切换→确认旧写者已隔离→contract。事务内 step 的 DDL 与历史回执一起 commit；不能事务化的在线索引步骤独立 journal 并重读索引有效状态，再决定续作或补偿，不把整个 plan 写成单事务。迁移失败关闭该 Store 的受影响写通道，其他 Store 继续。回退是 Plan 明确支持的 reader/软件兼容或补偿迁移，不承诺任意 downgrade；contract 已删除旧数据时只按批准备份隔离恢复，禁止自动建空库/改旧 hash。

### 7.4 备份闭包与目标恢复点

主路线冻结为 **PostgreSQL 物理 base backup + 所需连续 WAL + 硬盘对象闭包**。普通 SQL dump 可以作为另一个明确 Logical Profile 的迁移/诊断输出，不能宣称 WAL/PITR。备份范围是可信 BackupProfile 规定的完整 Store/数据库集群及其全部 Owner/租户集合；逐 scope 验权，不能从一租户请求偷备其它租户。精确工具/服务器版本由适配 Profile 固定；调用采用无 shell 的受控参数列表，不接收用户命令行、路径或连接串。

顺序：①先在引用/GC协调边界建立备份保护屏障，保护已引用及本轮新增引用，阻止引用对应字节被回收；②创建物理base backup并保留从开始到结束所需连续WAL；③在BackupProfile覆盖的完整集群全部Store/Owner提交入口建立cut barrier，等已接纳事务结局确定并验证所有提交对象SealedDurable，调用ReadCutAsync(request,baseStart,baseEnd,cutToken,ct)冻结目标身份/timeline/LSN和WAL清单；④在该barrier内枚举准确目标点的全部Owner引用，ReserveClosure取得绑定完整集合的耐久ClosureHoldId；⑤复制数据库/WAL/对象及Profile/Schema/codec必需资产，逐项核长度/hash后Seal带该Id的不可变BackupClosure，再BindClosure核准确link/集合，确认完成后才释放cut及备份屏障；⑥封口指向该Closure/Target的RestorePoint、Journal和MaintenanceSnapshot，核必需项完整才返回Complete。Reserve失败保留当前保护；Seal/Bind响应未知沿原identity回查，不能换Id或假装绑定。备份屏障建立前不能先扫描引用，闭包Seal/Bind前不能放开保护。本版保守协议会在复制/验证期间保留cut barrier，其持续时间受BackupBudget和维护窗口约束，必须实测，不能称“短暂”或“对生产影响小”。任何未接入Owner、越过barrier的写者、未fencing的旧写者或未决commit都使该目标闭包不能确认。屏障不授权取消生产事务或擅自暂停生产；Owner按已批准维护范围接入。

BackupClosure manifest 精确含 cluster/system id、服务器版本、base backup 身份/摘要、timeline 与所需 WAL 起止、明确目标恢复点、Schema/迁移/Catalog 修订、参与 Owner/租户集合、全部 ObjectRef、备份目标介质/加密 key reference、验证结果与闭包保持 identity。不保存明文密钥。恢复点必须绑定该 manifest；PITR 到更晚任意时刻会新增数据库引用，因此只有对应时刻的对象连续归档/新增闭包及 WAL 均已验证时才能发布新 RestorePoint 修订。未形成该闭包时目标 NotRestorable，不能仅因 WAL 可重放就答应恢复。

隔离恢复在未对生产开放、无设备/发送 worker 的目标 Profile 上完成：验证 manifest/当前访问权→检查版本、空间、key 与完整 WAL→恢复 base+WAL 至批准目标点（核 timeline/LSN）→恢复所有对象→逐条核全部必需引用/长度/hash/格式与领域 Owner 已注册的只读验证→封口 MaintenanceReceipt(Kind=Restore/VerifyRecovery, State=RestoredAndVerified)。抽样不能替代必需对象的完整检查。恢复保持原 operation/历史版本，可回读旧 codec；不复活原进程 TaskHandle/设备命令/自动 Outbox 发送。生产切换、旧主 fencing 和外发对账由部署/领域 Owner 另批准；RestoredAndVerified 不授切换权。保留原目标/原备份可回退，不就地覆盖生产库。

### 7.5 GC、保持和归档

PlanOrphanCollectionAsync 只生成不可变 per-object plan（含 retention/hash/reference epoch/精确对象/保护快照），返回 VersionRef 与候选计数，不删对象。CollectEligibleOrphansAsync 只接已产生且当前授权的 Plan，不接受强制删除列表；plan 变更/超期/MaxObjects 缩减不能用旧 hash 偷换集合。无候选返回 NoEligibleObjects；合法对象部分被保持跳过计 Skipped，IO 部分失败为 Partial，未知项单列；统计和逐对象 journal 必须可回查。

具体引用线性化、隔离/删除和别名闭包规则见上文 §6 的 GC 专项。引用目录来自所有 Owner 正式注册的完整 resolver；未接入某 Owner 时不以零条引用推断安全。临时 Hold 的 Renew 带 Handle+ExpectedVersion+原 identity，旧 fence/重复 owner 名称不能 ABA 续约；期限失效只停止新使用，活动读/写未结束和持久备份/领域保持仍阻止 GC。归档/压缩只创建新不可变对象和版本化投影，由 Owner 原子切换，不能改原 ObjectRef/hash 或借 compaction 清原事实。

## 8. Profile、容量和性能参数

参数全部由受信任不可变 Profile 显式提供，调用方只能申请更小预算，不能扩大。Profile/Catalog 字段类型/语义如下；生产值/物理阈值未定是部署门，不从例子或 Npgsql 默认值抄数。

| 参数组 | 字段/单位/合法域 | 行为及来源 |
|---|---|---|
| 通用输入/账本 | MaxIdBytes/MaxPayloadBytes/MaxResultBytes/MaxReferences；有限正整数；OperationRetention/TombstoneRetention 正 TimeSpan | 新请求超限拒绝；未决 operation 不到期删除。保证期内 old codec 可精确回查；未批准的终态退役不得删旧键后新建 |
| 每用途池 | MinPoolSize≥0、MaxPoolSize>0、Min≤Max；OpenTimeoutSeconds/CommandTimeoutSeconds/ConnectionIdleLifetimeSeconds/ConnectionPruningIntervalSeconds 正 Int32；CancellationTimeoutMilliseconds 正 Int32 | 显式映射：OpenTimeoutSeconds→Timeout，CommandTimeoutSeconds→CommandTimeout，CancellationTimeoutMilliseconds→CancellationTimeout，Idle/Pruning 去 Seconds 后缀映射相应属性。没有 MaxIdleConnections 属性，不能虚构映射；IdleLifetime/Pruning 管理闲置回收，MaxPoolSize 限总连接；Recovery 槽使用单独池及接纳额度 |
| 全局/租户接纳 | MaxQueuedItems/MaxQueuedBytes/MaxActiveTasks/MaxOpenResources、每 Tenant/Owner/Device 并发与队列预算，均有限正整数；MaxOperationTime/QueueAgeLimit 正 TimeSpan | 队列和任务墓碑均有上限；原未决任务占用保留，超限拒绝新任务；不允许 hidden Task.Run 无界队列 |
| 事务 | Isolation（注册 Binding 必填）；ServerLockTimeout/ServerStatementTimeout 正 TimeSpan；有限 MaxRetries≥0、逐次 RetryDelay 正 TimeSpan | 阶段期限≤剩余 deadline；Npgsql Timeout 单位秒、CancellationTimeout 毫秒，服务器 lock/statement_timeout 明确换算不将 0 解释为有界；后台 drain 可继续，单次等待有限 |
| 批量/对象 | MaxBatchRows/MaxBatchBytes/MaxObjectBytes/ChunkBytes/MaxConcurrentWriters/MaxReadBytes 均有限正整数；LowDiskWatermarkBytes/ReserveOverheadBytes≥0 | 预约包括实际卷分配、journal、staging/原子替换临时文件、备份/隔离区；Bytes 加法 checked，不因流压缩量小忽略解码上限 |
| 保持/GC | OrphanGracePeriod/MinLeaseTtl/MaxLeaseTtl 正 TimeSpan，Min≤Max；Maintenance.MaxPlanObjects/plan.MaxObjects>0、PlanRetention | TTL/宽限不替代引用/原写者完成证明；lease 失效 fail closed；journal 元数据预算不足在读流/删文件前拒绝 |
| 备份/恢复 | 最大闭包对象数/总字节、WAL/archive/复制槽空间预算、backup/recovery deadline、目标介质/key/版本、RpoTarget/RtoTarget | 数值由部署 Owner 批准；无 RPO/RTO 来源写 TargetPending，保持可做隔离软件验证 |
| 诊断/状态 | MaxDiagnosticEntries/MaxDiagnosticPageEntries 正 Int32，任务/资源墓碑条数与总字节预算 | 环形投影报缺口；未排空记录不淘汰；实例查询过期显式 ResultExpired，耐久 ledger 不随环形日志截断 |

类型落点为§6.3的StorageRuntimeProfile.Input/Runtime/Maintenance及Relational/Files，不保留第二套松散配置。MaxCatalogEntries/Bytes覆盖profile、bindings、codecs、owners、registered targets和嵌套scope集合，正Int32且启动前拒超限/重复引用；不能只对业务payload有界。除MaxRetries/MaxResumeAttempts允许0外，所有Max*/Chunk*/TotalConnectionBudget正且checked，MaxPlanObjects≤MaxCatalogEntries并≤Int32.MaxValue，MaxAssetPageBytes≤MaxAssetBytes，MaxAssetPageEntries≤MaxClosureItems，MaxJournalBytes≤MaxAssetBytes，MaxObject/Read/closure bytes采用long且实际容器/页为Int32有界；MinPoolSize允许0，LowDiskWatermark/ReserveOverhead允许0，Min≤Max。Quotas精确按Scope+Owner匹配，所有已注册租户Device有配额，队列按固定轮转入队、每scope FIFO，QueueAgeLimit到期拒绝/超时但不丢已接纳事实。MinLeaseTtl≤MaxLeaseTtl，非nullRpoTarget允许0、RtoTarget必须>0；null明确TargetPending，不算达标。Options.ResolutionBudget独立正TimeSpan使resolver也有限；Profile.Runtime.StartupBudget用于其后端打开。GC使用Maintenance.MaxPlanObjects与plan.MaxObjects，过期按PlanRetention判断且未知writer保护始终保留。

所有物理容量至少计数据库主数据/索引/WAL/归档/复制槽、文件存量、同时 staging、quarantine、闭包保持、新旧备份、journal 和安全余量；去重收益不得作为最坏容量保障。每日行/字节/对象分布、保留周期、长稳窗口、扩容触发值必须有消费者 Profile 来源。池故障、disk low、WAL 归档断裂、复制槽积压或恢复预算不足都返回对应 Degraded/Unavailable，不能只报连接成功为 Healthy。Health 是只读，不隐式建目录、迁移、清理或修文件。

## 9. 故障和恢复的闭合断言

| 触发 | 保留/对外状态 | 唯一恢复动作；禁止行为 |
|---|---|---|
| 空/null/default/未定义 enum/越界预算/错租户 | RequestRejected+明确错误，无外部分配 | 修输入/授权后新合法请求；不自动补 Tenant、路径、Schema 或默认参数 |
| 同键同 hash 并发 | 一个 reservation，一个执行，其余同原 task/operation 观察 | 原身份查询；不第二次消费流/执行领域映射 |
| 同键异 hash、对象描述变化 | Conflict，原记录/字节不改 | 领域 Owner 决定新身份；不覆盖原物件或任意合并 |
| 池耗尽/队列满/磁盘低 | 接纳前 Rejected(CapacityExceeded/TimedOut)，未运行 SQL/读流 | 宿主按 Profile 背压；不旁路建池、不删旧证据、不降低耐久 |
| 已证明事务失败 40001/40P01 | 原事务排空/回滚，仍在本操作有限重试预算 | 重跑完整事务；不只重发最后语句，未知 commit 不入此分支 |
| commit 响应丢失、旧主不明 | Unknown 保留原 identity/对象保持 | 从权威主库回查/fence；副本 NotFound、Dispose 或 token 取消均不能证明回滚 |
| 文件部分写/封口意图不明 | 原 staging/journal，File.Unknown 或 Failed；Object=null | 沿原write identity只读回查；不按年龄清除正在写的对象、不读新流假重放；跨请求续传见范围外扩展 |
| 文件已封口/DB已知回滚 | OrphanPending；数据库 RolledBack | 宽限+完整引用/保持协调后 GC；不立即删 |
| 已引用文件损坏 | 技术 Commit 可仍 Committed；对象 IntegrityFailed | 隔离并阻用途，Owner 再生成新身份；不修历史 hash/改事务回执 |
| 等待取消/超时而 IO 未停 | 原 Task Draining/DrainUnknown，资源和源流借用保留 | 原 handle 查到 ResourcesReleased 后再释放；不提前返回 Cancelled/归还池 |
| 数据库/文件迟到成功 | journal/ledger 保存原真值 | 只读回查；不丢迟到提交、不重跑或触发质量/设备动作 |
| Migration/backup/GC 中断 | 各自 checkpoint、Unknown/Partial/Blocked | 同原 operation 核 journal 与实物，按已注册恢复步骤续作；不伪全成功/自动降级 |
| 版本/Store generation/Instance epoch 改变 | 旧资源 InstanceMismatch；旧 durable key 按原版本回读 | 新 Runtime 独立恢复/隔离；不把旧 handle 用于新对象/连接，不静默升级 Schema |
| 关闭且 consumer 未 release | stop 保持 Draining，diagnostics 可查 | 宿主先 release 原 lease；不强关正在读写的资源 |

可恢复文件写claim的额外单写者/迟到写约束在§6保留，只在未来正式扩展时适用；当前A2按原write identity、scope/generation/fence与封口journal验证，同hash不同write不能相互冒认。本轮不引入来源AOI的claim容量结算或Windows特定文件identity公共API。

## 10. C0 纯值契约、决策表和最小调用

C0 仅用已经构造的不可变证据作确定性分类；不计算 canonical hash，不授权新操作，不查数据库/文件，不建任务/租约/日志，亦不模拟耐久或 GC。Contracts 的纯 DTO 声明与 IO 接口可以单独编译，但实现 IO 不属于 C0。唯一公开 Core 类型如下；类型表使用 §6 的 Sha256/ObjectRef/回执/错误，不能再造平行 DTO。

```csharp
// DTO 位于 Asun.Platform.StorageDatabase.Contracts
public sealed record EvidenceLimits(int MaxIdBytes, int MaxReferences, int MaxResultBytes);
public sealed record SaveEvidenceRequest(ObjectRef Expected,
    FileObjectReceipt File, TechnicalCommitReceipt Commit, EvidenceLimits Limits);
public enum SaveClassification { Committed, Failed, Unknown, Inconsistent, Invalid }
public sealed record SaveClassificationResult(SaveClassification State, StorageFault? Fault);
public sealed record ReplayEvidenceRequest(OperationIdentity Candidate,
    OperationIdentity? Existing, StoredOperationState? ExistingState, EvidenceLimits Limits);
public enum ReplayClassification { Replay, InProgress, Unknown, Conflict, NoPriorEvidence, Invalid }
public sealed record ReplayClassificationResult(ReplayClassification State, StorageFault? Fault);
```

Core namespace 唯一为 `Asun.Platform.StorageDatabase`，公开静态类 `StorageCore` 的签名：`SaveClassificationResult ClassifySave(SaveEvidenceRequest request)`、`ReplayClassificationResult ClassifyReplay(ReplayEvidenceRequest request)`。方法同步、无全局状态、同输入同结果，不接取消/timeout/Dispose/回调；输入规模由 EvidenceLimits 控制，调用时不保留引用。MaxIdBytes/MaxReferences/MaxResultBytes 都必须>0且为 Int32，不用“Limits≤0”代替字段校验。null/default/不合法 ID/hash、References 超限/重复 Key、ResultBytes 超限、UTC 非零 offset、Object/回执 tenant/store/generation 不一致均返回 Invalid+InvalidInput，不抛原 provider 异常。File.Object 为 null 的 Rejected/Failed/Unknown/IntegrityFailed 回执合法；SealedDurable/SealedNotDurable/Verified/OrphanPending 却 null 是 Invalid。File 与 Commit 的 OperationId 可不同（文件写与 DB 提交是两个技术操作），Scope/Store/Generation 必须相同；不强行合并两者身份。

C0 不依赖未注入的 IO Profile：所有 ID（含 Scope/Owner/Key/VersionRef.Id）按严格 UTF-8 编码（未配对 surrogate 拒绝）核 MaxIdBytes；字节计数遇到上限即拒绝，不扫描任意长字符串到尾或分配编码副本。MediaType 为非空且不含控制字符的 opaque 格式标签，同样受 MaxIdBytes 限制，精确比较、不解析参数或猜格式。Sha256 必须为64个小写十六进制字符，VersionRef.Revision/Generation>0，对象 Bytes 为非负 Int64，所有 AtUtc.Offset=TimeSpan.Zero。两个方法均验证三项 Limits；Save 先取 References/ResultBytes 长度核上限，再遍历引用，不复制或解码结果字节。Replay 没有 ResultBytes，仅验证上限的有效性。字符串用 Ordinal 比较；ObjectRef/VersionRef/Scope 逐字段比较，引用集合按 ObjectKey 匹配，不用 ImmutableArray 底层实例相等代替描述相等。所有 ObjectKey 与对应 identity 的 tenant/store/generation 相同，File.Key 与 Expected.Key 的 Store/Generation/Tenant 相同；跨 scope 的证据优先 Invalid，合法同 Key 描述差异才 Inconsistent。任何非法形状在决策表前拒绝，不因另一回执 Unknown 而跳过校验。

ClassifySave 固定执行顺序：验证 shape/范围→核 Expected 与 File.Key/非 null Object 全字段→核 Commit 引用的同 Key 是否全描述相同→按下表从上到下分类。File.Object 非 null 时其 Key 必须等于 File.Key，否则为非法回执形状→Invalid；在同 tenant/store/generation 的合法形状下，File.Key 的 StorageDomain/ObjectId 与 Expected 不同，或相同 Key 的摘要/长度/媒体/格式冲突，或 Commit.Committed 缺 Expected 精确引用，均 Inconsistent+IntegrityFailed。跨租户/Store/Generation/Scope 是 Invalid，不把另一作用域证据当成本对象的损坏。该结果不改变输入回执，也不决定工艺 PASS/FAIL。

| 已有效验证的文件/事务证据 | 分类 |
|---|---|
| 任意状态，但有上述已知描述冲突或 Committed 缺精确引用 | Inconsistent |
| File.Unknown 或 Commit.Unknown，且无已知描述冲突 | Unknown（即使另一回执 Committed，也不能把未知观察当作已知文件损坏） |
| Commit.Committed + File.SealedDurable，且完整 Object=Expected/精确引用齐全 | Committed |
| Commit.Committed + File.Verified，且描述/引用齐全 | Unknown（内容已验，缺少写发布耐久证据） |
| Commit.Committed + 其余已知文件状态 | Inconsistent（保留两回执，不重写提交事实） |
| Commit.RolledBack/Rejected + 任何剩余已知文件状态 | Failed |

ClassifyReplay 固定顺序：验证 shape/枚举与 Candidate/Existing；Existing 与 ExistingState 必须同为 null 或同为非 null。两者 null→NoPriorEvidence；否则先核两者完整 Scope/Store/Generation/Owner/IdempotencyKey，作用域不一致→Invalid，再核 OperationId/hash，任一不同→Conflict，最后分类状态。全身份相同且 NotFound→NoPriorEvidence，Committed/RolledBack/Rejected/Failed/Succeeded→Replay（原状态不改变），InProgress→InProgress，Unknown/IntegrityFailed→Unknown。NoPriorEvidence 只表示缺证据，绝不授权执行/释放资源；ExistingState 不被 C0 当成真实 ledger 查询证明。不能把任意外作用域 NotFound 先判成无既有证据。

两个分类结果使用封闭键：Invalid→InvalidInput/`storage.invalid_input`；Inconsistent→IntegrityFailed/`storage.integrity_failed`；Conflict→Conflict/`storage.conflict`；Unknown→CommitUnknown/`storage.commit_unknown`；Failed→Unavailable/`storage.save_not_completed`。Committed/Replay/InProgress/NoPriorEvidence 的 Fault=null。Failed 只表示保存未完成，不推断权限、介质或业务冲突根因；具体恢复须读取输入原回执和 operation。

未来库已实现后，无 UI/DB 最小 Host 的调用片段如下；仅示范纯分类，不创建文件/连接，不作为生产事实证据，本轮未编译/运行：

```csharp
using System;
using System.Collections.Immutable;
using Asun.Platform.StorageDatabase;
using Asun.Platform.StorageDatabase.Contracts;
var hash = new Sha256(new string('a', 64)); // 合成摘要
var format = new VersionRef("test-format", 1, hash);
var scope = new StorageScope("tenant-a", "site-a", "line-a", "station-a", "device-a");
var obj = new ObjectRef(new ObjectKey("store-a", 1, "tenant-a", "images", "object-a"),
    3, hash, "application/octet-stream", format);
var write = new OperationIdentity(scope, "store-a", 1, "test-owner", "write-a", "write-key", hash);
var commit = new OperationIdentity(scope, "store-a", 1, "test-owner", "commit-a", "commit-key", hash);
var fileReceipt = new FileObjectReceipt(write, obj.Key, obj, FileState.SealedDurable,
    new VersionRef("test-durability", 1, hash), DateTimeOffset.UnixEpoch);
var commitReceipt = new TechnicalCommitReceipt(commit, CommitState.Committed,
    ImmutableArray.Create(obj), format, ImmutableArray<byte>.Empty, DateTimeOffset.UnixEpoch);
var result = StorageCore.ClassifySave(new SaveEvidenceRequest(obj, fileReceipt, commitReceipt,
    new EvidenceLimits(128, 8, 1024))); // 128/8/1024 只是合成夹具上限
if (result.State != SaveClassification.Committed) throw new InvalidOperationException();
var replay = StorageCore.ClassifyReplay(new ReplayEvidenceRequest(commit, commit,
    StoredOperationState.Committed, new EvidenceLimits(128, 8, 1024)));
if (replay.State != ReplayClassification.Replay) throw new InvalidOperationException();
return 0;
```

该片段落在 Core.Tests 的 `Program.cs`，不是第二个验证工程；完整 Exe 入口还必须执行 §11.1 全部 C0 断言。另两个独立消费者在同一工程的 `SaveConsumer.cs` 与 `ReplayConsumer.cs` 中分别只通过公开 StorageCore/Contracts 完成保存证据分类和既有幂等证据分类，不共享私有 Helper/状态；Program 顺序调用二者，再跑交叉篡改/边界样例。纯 Core 不需要像素容器或客户阈值，三 byte 是合成元数据而非真实文件。

## 11. 可执行验证和 BenchmarkProfile

本节是未来实现任务的测试计划，非本轮测试通过声明。测试路径唯一按 binding 表；C0 采用纯 DTO 夹具，C1 用可控 barrier 的假后端，A1 用真实隔离 PostgreSQL 目标版本，A2 用独占目录/子进程，A3 用隔离恢复库。断电、介质损坏、现场 RPO/RTO 另计；合成/进程故障不能替代物理掉电证据。

### 11.1 两种审查视角对应的测试断言

本表与§12.1新增启动快照/同事务epoch/根快照反例共同构成当前切片suite；后者不得因位于准备结论而跳过。启动注册/同CLR type分派/Factory不提前Open根/原Owner保持在C1可控fake夹具验证；同事务8/9 epoch、回滚、Query GUC隔离、真实CAS计数及统一SQL锁序在A1/Integration隔离PG夹具验证，物理guard失效另由A2夹具验证。所有assertion按其切片绑定的既有测试工程执行，不新建同义测试包，也不以内容检查冒充这些运行断言通过。

| 能力与夹具（全部为软件样例） | 正常/边界断言 | 并发/故障/第二消费者断言 |
|---|---|---|
| A1/A2真实启动装配（归A1-POOL/A2-SEAL） | exact Kind/ref/hash、有界文档/秘密/codec解析；只有一个PG group供Database/References/Assets/FileMetadata，Set恰五实例；主库/目标/备份/保留槽总预算精确；实际TLS/角色/RLS/根身份不匹配拒初始化 | 槽/字节满零Create；doc超限/重复字段/错误类型、秘密版本不符或第2/3阶段Open失败均真实逆序归还；阻塞/迟到Open与Dispose保留原Task，不二次Dispose/开组；source/credential/catalog/clock/barrier不被Runtime错关；异常无provider/SQL/秘密/path穿透 |
| A2跨进程物理保护（归A2-SEAL/GC） | 两独立进程参与同根/Authority，read共享、publish/GC排他；OS锁名不随epoch/fence变更；journal和DB索引响应丢失分别保留真实结论，Verify证据可原identity回读 | 旧DB连接断开但IO未结束时新writer/GC不得进入；BackupCut不能与自身共享gate自锁；根替换/重解析逃逸拒绝；Publish/Delete native在途不能归还guard或槽；目录索引缺失不重读source，未知SMB不授锁/耐久资格 |
| A3真实工具与独立Host（归A3-CLOSURE/RESTORE） | 两真实数据Host独立装配并读回相同字节/描述；原manifest v2的system/timeline/LSN/checksum及全part验证；前台postgres原Process由group持有，VerifyOnly零启动/写入 | 额外tablespace/multi-range base/工具hash不符副作用前拒；工具输出超限/取消/exit未知保留原child/Reader/秘密文件；隔离服务Stop未知保持target槽/原Task，不把pg_ctl退出当服务退出；恢复目标/worker/角色错误拒绝，原cut/point不变；Primary/Cleanup和归还/业务结果分轴 |
| C0 存储证据 | §10 三 byte 文件回执+相同引用→Committed；同 Id 异 hash/缺引用→Inconsistent；非 durable 不成功；Unknown 保留；Verified+Committed→Unknown；已知描述冲突优先于 Unknown | 多线程并行同值等价，无任务/全局状态；全 enum/default/null/重复/超限/UTC offset 拒绝；三个 EvidenceLimits 字段逐一0/负值/N/N+1；未配对 surrogate、最大 MediaType、ResultBytes N/N+1；换数组实例但引用描述相同仍 Committed；无取消/超时/关闭，因为无资源且同步有界 |
| C0 幂等证据 | 同全 key/hash 各历史状态按表，改 hash/OperationId→Conflict；NotFound→NoPriorEvidence | 外租户既有回执不能 Replay；参数/canonical 修订变化表现为原摘要差异；旧 Schema 只验证已给定值，不由 C0 迁移 |
| C0 历史/回退 | Format/ResultSchema/DurabilityProfile 的旧 Revision=1 且完整hash合法仍按原证据分类；所有对象描述一致改为Revision=2仍Committed，不能静默升级旧输入 | 同Key仅File.Object.Format改revision/hash→Inconsistent；任一VersionRef.Revision=0→Invalid；当前生产Profile改变不进入C0输入，不改历史判定。代码包回退/跨API版本运行未实现，不把纯值断言当二进制兼容测试 |
| A1 技术事务 | 空/超限批次拒绝；单批 3 行领域数据+回执+对象引用同事务出现；期望行数 0/多行回滚 | 两 Session 同 key 同 payload 仅一个执行，异 payload 不改原回执；40001/40P01 全事务有限重试；跨月份同 key 不双写；commit 前/响应前断连 Unknown 回查，无业务行已写但回执不存在窗口 |
| A1 租户/池 | A/B 相同业务 key/hash 互不可读写；无 tenant RLS default deny；读 USING/写 WITH CHECK 均核验 | A 设置 tenant/role/search_path 后取消/归还，B 借同物理 connector 不串租户；runtime 非 Owner/superuser/BYPASSRLS；恶意绑定跨 Owner 失败；查找副本 NotFound 不许可重试；查询满池时恢复保留槽可用 |
| A2 对象写/读取 | 流 0/1/Chunk−1/Chunk/Chunk+1/Max/Max+1，非 Seek 源正确流式；错预期长度/hash/格式拒绝；跨卷/NAS 不明拒耐久；范围 Offset+Count 溢出拒绝 | 同对象并发唯一发布，改内容 Conflict；等 WaitBudget 返回时源流仍不可关闭；恢复按原 identity；两租户同 hash 不能泄存在；第二 CLI 全读取/Verify 与原字节一致，不创建源目录 |
| C1 生命周期 | 接纳前取消 RequestRejected，零 backend 执行；接纳后释放顺序唯一；OwnerReadResult 成功/空集/失败字段互斥 | 用 test barrier 保持底层 IO：等待取消/Stop 返回非终态，连接/流/额度不返池；解除 barrier 后 Drained→ResourcesReleased→Completed；无 TaskHandle 的 Open/Read/Renew 取消先清理后返回；迟到 commit 原 ledger 可查；重复 Stop/Release 同任务，异身份 Conflict；Instance epoch 改变拒旧 handle；未知 Resource/Hold 不报计数0或版本0；诊断 ring 丢项显式 gap |
| C1 注入/路由/codec | exact Profile/Catalog/codec类型/Format注册、三类Input/Result/Format受限调用；配置解失败关闭已建实例且一次Dispose；同identity route Created=true后同值false，异Kind/hash/Schema Conflict | 调真实StorageRuntimeFactory和StorageMaintenanceBackend，仅后端/clock/barrier fake；resolver/authority/backend open中取消都无无主资源；clock回拨UTC不延長deadline；Created=false/route unknown不第二次读source；Operation token来源/旧fence/失效验证；同revision同证据重放、异内容Conflict，追加行/head原子且旧证据仍可读；任一Code/DiagnosticKey错配拒绝 |
| C1 生产Host保持（C1-LIFECYCLE/INJECT/STOP） | 在Create前耗尽槽条数或总字节预约→拒绝且零Factory/Open/Stage；每个原Task先保存，轮询/读写槽只在已完成后复用；归还与业务结果分开 | LIFECYCLE：业务异常+Release/Dispose异常同时保留Primary与各Cleanup，源/输出未归还时TryReturn=false，外层WaitAsync/观察取消后关闭计数仍0；INJECT：真实Factory配阻塞后端Open，Create未交Runtime原Task及工厂仍被slot强持，迟到Runtime/Open lease先接管再清理，失败回滚未结束不归还；STOP：Release/Stop已发但Draining、Dispose无限等待时独立cleanupBudget到期保留原Task/handle/端口，重复观察不二次Dispose/不换Runtime；转交拒绝/错误Owner/通知失败保留原根，迟到排空后才交回流 |
| 维护资产canonical/分页 | 两候选0/1项以MaxEntries=1读两页，每snapshot计数/bytes一致；空资产一页Empty/Next=null；三个byte对象hash沿receipt读回；IM066-ASSET-1按固定字段向量重算 | null/default/未定义Schema/错CLR类型/错Creator/重复sequence/单项超页budget/MaxBytes N+1拒；旧snapshot cursor换新revision/hash/Schema→InvalidInput；字节篡改→IntegrityFailed；不存在/过期→ResultExpired；读取消真释放且零Seal/副作用 |
| 托管GC/闭包组合 | 用内存目录/引用snapshot和asset backend运行真实组合器：两个对象3/5byte，第二对象referenced，plan候选仅第一个；journal planned→intent→confirmed且counts只按item；全局前置Blocked时已验证候选全计Skipped，未读plan不泄数量 | plan后并发加引用或别名hold→Skipped/GcBlocked且零Delete；intent后IO未知→Unknown保留；隔离宽限未到为已知Skipped；ReserveClosure后断点不释放屏障；Seal后BindClosure响应丢失同身份复核不换ProtectionId；baseStart/baseEnd错cluster/工具、第二Store未接入Owner、WAL延伸段缺失、Required对象无验证→不能Complete/Restorable；恢复目标workers开启或实际ToolVersion不等目标Profile均拒绝 |
| C1 显式维护续作 | 初次attempt=0；原Journal+ExpectedAttempt CAS只创建一个新attempt/task；确认effect不重跑，确认未发生且旧writer已fenced才执行原step | 双resume同参数观察同attempt；异journal/hash Conflict；旧writer未知、原Succeeded、过期GC plan、MaxResumeAttempts耗尽拒绝；Probe Unknown不重effect；BackupWork的已pin cut/HoldId不变；Query零Seal/Append/Resume |
| A2 GC/保持 | dry-run 零字节变更；候选/空候选/保护跳过/部分 IO 分项准确 | 新引用/读/导出/backup/Legal Hold、同 hash 别名、双 GC、lease/fence 变化、resolver 超时与未知删除；每对象 journal 崩溃后可原身份回查，不两扫描替代协调；当前单写的迟到封口不会被清/冒认；可续传claim仅在未来扩展测试 |
| A3 迁移 | Schema/plan exact hash，事务 step 的历史同 commit，非事务 step 重读 invalid index | 双 migrator、旧 writer、缺历史、checksum 变更均阻断；回填中断不重复修改；contract 后禁止盲降级；旧版本消费者按兼容区间回读/拒绝 |
| A3 备份恢复 | cut 点的 DB/文件完整闭包一致；每必需引用全校验；可追溯 UTC/LSN/timeline | 刻意先扫描再 pin 的反例必须被协议阻止；完整 cluster 含第二 Store/未接入 Owner/未决 commit 时不能只备当前 Store 报 Complete；WAL 到更晚目标而新增文件缺失→NotRestorable；缺 WAL/错 timeline/key/介质/Owner 目录拒绝；备份/恢复中取消保留原 journal；恢复不开设备/发送 worker；隔离 CLI 可复读同份闭包 |
| 长期容量/负载 | 记录分区/索引/WAL/对象/保持全部增长与实际 footprint；参数变更创建新修订 | 热租户、慢查询、慢磁盘、锁等待、分区边界/迟到、归档断网、复制槽积压、进程重启与滚动池并存；背压公平且不丢权威事实，old profile 回查不被新参数改变 |

对 A1–A3 必须使用唯一 operation/隔离夹具真实读回；同名测试、Schema 通过、文件存在、receipt 字段存在都不是所列 assertion 证据。首版验证全部采用 `Microsoft.NET.Sdk/net10.0/OutputType=Exe`，nullable/implicit usings 开启，只引用受测工程和 BCL，不引入测试框架包。约定直接复用 DEV-GOV-010 §3.1 的 BCL Exe 约定，不得用 `dotnet test` 的空执行当通过。A1 因受测适配器引入已冻结 Npgsql 依赖，验证入口自身仍为 BCL Exe。本轮不建工程/运行构建，命令仅供获准后的代码任务。

### 11.1.1 精确构建、执行和截止

工作目录为仓库根（由 PROJECT_ENTRY.md 定位）。C0 构建先 Contracts→Core→Core.Tests；C1/A1/A2/A3 的工程逐切片执行，不借一条总方案命令隐藏必需项。

```powershell
dotnet build src/Modules/storage-database/Asun.Modules.StorageDatabase.Contracts/Asun.Modules.StorageDatabase.Contracts.csproj -c Release
dotnet build src/Modules/storage-database/Asun.Modules.StorageDatabase.Core/Asun.Modules.StorageDatabase.Core.csproj -c Release
dotnet build tests/Modules/storage-database/Asun.Modules.StorageDatabase.Core.Tests/Asun.Modules.StorageDatabase.Core.Tests.csproj -c Release
dotnet run --project tests/Modules/storage-database/Asun.Modules.StorageDatabase.Core.Tests/Asun.Modules.StorageDatabase.Core.Tests.csproj -c Release --no-build -- --suite C0 --deadline-seconds 30
dotnet build src/Modules/storage-database/Asun.Modules.StorageDatabase.Runtime/Asun.Modules.StorageDatabase.Runtime.csproj -c Release
dotnet build tests/Modules/storage-database/Asun.Modules.StorageDatabase.Runtime.Tests/Asun.Modules.StorageDatabase.Runtime.Tests.csproj -c Release
dotnet run --project tests/Modules/storage-database/Asun.Modules.StorageDatabase.Runtime.Tests/Asun.Modules.StorageDatabase.Runtime.Tests.csproj -c Release --no-build -- --suite C1 --deadline-seconds 60
dotnet build src/Modules/storage-database/Asun.Modules.StorageDatabase.PostgreSql/Asun.Modules.StorageDatabase.PostgreSql.csproj -c Release
dotnet build tests/Modules/storage-database/Asun.Modules.StorageDatabase.PostgreSql.Tests/Asun.Modules.StorageDatabase.PostgreSql.Tests.csproj -c Release
dotnet run --project tests/Modules/storage-database/Asun.Modules.StorageDatabase.PostgreSql.Tests/Asun.Modules.StorageDatabase.PostgreSql.Tests.csproj -c Release --no-build -- --suite A1 --profile-id im066-a1-fixture --deadline-seconds 180
dotnet build src/Modules/storage-database/Asun.Modules.StorageDatabase.FileSystem/Asun.Modules.StorageDatabase.FileSystem.csproj -c Release
dotnet build tests/Modules/storage-database/Asun.Modules.StorageDatabase.FileSystem.Tests/Asun.Modules.StorageDatabase.FileSystem.Tests.csproj -c Release
dotnet run --project tests/Modules/storage-database/Asun.Modules.StorageDatabase.FileSystem.Tests/Asun.Modules.StorageDatabase.FileSystem.Tests.csproj -c Release --no-build -- --suite A2 --profile-id im066-a2-fixture --deadline-seconds 180
dotnet build tests/Modules/storage-database/Asun.Modules.StorageDatabase.Integration.Tests/Asun.Modules.StorageDatabase.Integration.Tests.csproj -c Release
dotnet run --project tests/Modules/storage-database/Asun.Modules.StorageDatabase.Integration.Tests/Asun.Modules.StorageDatabase.Integration.Tests.csproj -c Release --no-build -- --suite A3 --profile-id im066-a3-fixture --deadline-seconds 600
```

每条命令必须单独检查退出码，build非零立即停止该切片，不能运行旧DLL。`--suite`为以上封闭值，`--deadline-seconds`为正整数且≤对应测试上限，未知/缺参数退出2。ProfileId由受信任夹具目录映射到隔离库/根/工具/key reference；不存在夹具或必需依赖/权限/工具缺失退出2，不能skip后0，不能CLI传生产连接串/任意根。C0/C1不要求物理Profile。必需ID固定：C0-SAVE/REPLAY/BOUNDARY/PARALLEL/VERSION；C1-LIFECYCLE/WAIT-CANCEL/RELEASE/STOP/LATE/OBSERVE/INJECT/ROUTE/CODEC/ASSET/PAGING/MAINTENANCE/RESUME；A1-TX/TENANT/POOL/UNKNOWN/PARTITION；A2-SEAL/READ/GC；A3-MIGRATION/CLOSURE/RESTORE。每项带对应suite前缀并覆盖表内子场景；托管asset/GC/闭包组合及显式维护续作归C1，不依赖物理后端。跨进程可恢复claim不属v0.3交付（见§6历史边界），A2只验当前单写/journal/重启原identity回查，不机械要求不存在claim API。

退出码固定：0=本 suite 全部必需断言执行完成且释放确认；1=断言失败/异常/必需项跳过；2=用法或夹具不满足；3=内部测试截止到期/任务或释放未完成。不能吞异常后打印 passed。内部截止发合作取消、保留原任务/资源并收集未完成身份，必须由独立 BCL watchdog 在总截止到期时使 Exe 以3退出；退出只证明该测试未完成，不伪称底层 drain 或生产释放完成。真实后端仅在独占软件夹具使用这类进程故障，子进程/目录仍需后续原身份恢复，不递归清未知目录。

外层验证执行器分别给每条 build 180秒、run 的测试截止加30秒宽限；超时按124/非零记录，终止该验证进程树并保留夹具恢复信息，不打印通过。本指导不增加启动脚本；未来实现任务使用现有进程执行器的有限超时或 BCL `Process.WaitForExitAsync`+单调 deadline 实现外层，禁止只对断言 Task.WaitAsync 后让 process 返回0。以上30/60/180/600秒只限制确定性软件夹具运行，不是工业性能/客户 RPO/RTO 门槛；大规模/长稳 benchmark 使用单独获批 Profile 与命令，不能延长此 suite 后冒称压力验证。后续只跑受影响切片，主会话统一全仓文档校验。

### 11.2 BenchmarkProfile

统一冷/热采样、有限 deadline、失败/删失样本及 nearest-rank 分位统计按 DEV-GOV-010 §3.1，不复制算法。Profile 冻结唯一 ID/revision/hash、构建/依赖版本、OS/CPU/内存/存储/网络、输入集 hash 和分布、并发/到达模型、固定冷测/预热/测量数量、最低有效样本数、阶段测点/资源预算、故障注入点及每阈值来源。值缺来源时标 TargetPending，结果 NotEvaluated，允许测量但不能宣称达标；Profile 改变不跨修订合并样本。

C0 测点从同步调用入至返回（没有虚构 drain），分开测 ClassifySave/ClassifyReplay、冷进程/热循环、多线程只读、Reference 数 0/1/N/N+1、短/最大 ID、合法/拒绝/Unknown 分支，记录 CPU/托管分配/工作集和输入大小；硬上限由输入 EvidenceLimits 提供，验证超限在昂贵复制前拒绝。阈值来自已采纳消费者 Profile，示例夹具数值不是生产门槛。

C1/A1–A3 端到端从接纳至 ResourcesReleased，单列返回等待时间与取消至真实排空。记录连接获取/锁等待/SQL/commit/原 identity 回查、批量/文件分块 hash/flush/rename、范围读/Verify、GC 隔离/删除、迁移各 step、base backup/WAL 闭包枚举/复制/隔离恢复的 P50/P95/P99、吞吐与失败/未完成数。OS/DB/网络缓存未清时不标真正 cold。长稳观察窗明确，不从短跑外推长期增长；任何 DrainUnknown 样本不能算性能通过。

负载固定设备/租户/宿主数、每设备写入率/行数/对象大小分布、读写比例、batch rows/bytes、排序/索引/分区修订、查询长事务、HA/服务器版本、用途池与总预算、滚动实例并存、文件/NAS Profile、加密/压缩/备份闭包。资源计连接/reader/句柄、CPU/工作集/私有字节/GC 分配、队列条数/字节/最老年龄、原 staging/quarantine/journal/保持/物理分配、数据库/WAL/archive/复制槽/索引增长、对象积压/孤儿/Unknown 年龄、磁盘水位与网络 IO。恢复阶段逐必需对象验证也计入 RTO，不把数据库启动时间当 RTO。

## 12. 六项准备结论与独立发布

主控已内容接收 C0、C1 的 DEV-GOV-010 §3.1 六项规格，2026-10-10 同步为 `ModuleCoreImplementationReady`（仅规格准备）。C0 的已接收纯值契约、断言与范围保持原基线；C1 接收范围仅为 Runtime + 可控 fake 后端 + 托管维护组合 + 双无 UI Host，包括§7.1.1–7.1.2的有界原Owner保持与异常清理闭包。§6.7/§7.1.4 的 A1/A2/A3 真实装配增量已获主控限定内容接收，范围包括角色隔离、独立数据源/凭据、物理身份与锁编码、object_catalog CAS 约束及两个真实适配 Host 接线。该状态不表示代码、编译、运行、真实后端、耐久、性能或现场验收通过。A1/A2/A3 整体仍为 `PreparationIncomplete`，整模块不提升为 `ImplementationSpecificationReady`；真实 PG/Npgsql 运行、NAS/耐久、工具、性能和生产 IO 不提升。C0 没有未决物理数值；后端 Profile 门不阻断已接收的 C0/C1 托管规格。主控独立逐字段重建 Stage 信封（含 ExpectedBytes/ExpectedHash nullable presence），290 bytes/SHA-256 与§6.3向量一致，仅为编码规格核查。各切片接收以如下精确位置为据：

| DEV-GOV-010 §3.1 项 | 本轮实际落点 | 接收状态/受影响切片 |
|---|---|---|
| 1 边界/第二消费者 | §1、§7.1 两独立 Host，私表和质量事实排除 | C0/C1 限定范围规格已接收；A1/A2/A3 装配增量已限定内容接收；实际消费者运行未测 |
| 2 唯一 API/单位/错误/资源 | §6.3–6.7注入、资产/分页、错误目录、技术存储、真实装配与生命周期；§10两个C0同步方法 | C0/C1及托管维护组合规格已接收；A1/A2/A3装配增量已限定内容接收；不是已编译公开库，领域Payload/SQL/真实后端仍外部接入 |
| 3 无 UI 最小 Host/依赖注入 | §7.1.0真实Runtime+fake backend、§7.1.1–7.1.2预留强持槽/原Task/迟到接管/嵌套清理消费者、§7.1.4真实适配Host接线、§10最小调用 | C0/C1 双无UI Host及异常闭包规格已接收；A1/A2/A3装配增量已限定内容接收，Owner resolver与物理Profile仍后续门 |
| 4 正常/反例/恢复/回退测试 | §9、§11.1 的明确输入/输出与断言 | C0/C1测试规格已接收；装配反例已限定内容接收；未创建工程/执行测试；A1/A2/A3真实验证保留 |
| 5 测试/性能测点与来源 | §8、§11.2；所有物理/时延客户值 TargetPending | C0/C1测试与Benchmark规格已接收；装配增量的确定性断言已限定内容接收；运行达标/后端长稳/RPO/RTO未测 |
| 6 工程/路径/调用与后续门 | 唯一 binding 表、§7、附录 B | C0/C1限定范围工程/Host/后续门规格已接收；A1/A2/A3装配增量已限定内容接收；代码任务仍需主会话绑定可审计基线；本轮只改指导 |

逐切片判定如下。“已定”仅表示指导给出可复核规格；C0、C1限定范围的六项规格已接收，A1/A2/A3本轮装配增量已获主控限定内容接收，但完整切片仍为 `PreparationIncomplete`。“缺口”必须在唯一指导关闭后才可派发该切片。没有运行结果不是文档准入的替代门，也不把计划写成已验证。

| 切片 | 1 边界/复用 | 2 唯一契约 | 3 无 UI Host/注入 | 4 可判定测试 | 5 测量/阈值来源 | 6 工程/范围/门 | 本轮准备结论 |
|---|---|---|---|---|---|---|---|
| C0 | 已定；两个纯值消费者 | 已定；§6纯值DTO+§10，三字段Limits | 已定；§10，零IO | 已定；正常/反例/并发/版本；取消/排空因同步无资源不适用 | 方法已定，目标值待消费者Profile采纳；不虚构达标 | 已定；binding及BCL Exe命令，待可审计代码基线 | ModuleCoreImplementationReady（主控六项规格已接收；仅规格准备，未实施/未验证） |
| C1 | 已定；协调器，不写产品事实 | §6.3–6.5 Profile/Catalog/codec/backend/clock/barrier/错误键闭合；业务codec内容仍Owner | §7.1.0真实Runtime+fake后端调用/释放/回查形状闭合；§7.1.1–7.1.2双Host有界保持与异常闭包已接收 | barrier、取消、迟到回执、资源排空、重复/版本/权限断言已定 | 测点/资源维度已定，目标待Profile | Runtime工程/范围/构造器/Host形状已定；未创建/运行 | ModuleCoreImplementationReady（主控六项规格已接收；仅Runtime+可控fake后端+托管维护组合+双无UI Host规格准备，未实施/未验证） |
| A1 | 已定；唯一PG18/Npgsql10.0.3技术适配 | §6.7工厂/Options、可信文档/秘密、固定SQL marshal及FileMetadata窄桥已补；Owner正式内容仍待接入 | §6.7.2唯一PG group及五实例、§7.1.4双真实Host接线已补；装配增量已限定内容接收 | 原事务/RLS/池/Unknown反例保持，新增启动/预算/迟到/清理断言；真实夹具未绑定 | 方法已定；实际负载/集群预算待Profile | 既有A1工程；内部装配规格不列客户外门，不接生产库 | PreparationIncomplete；装配增量已获限定内容接收，未实施/真实验证 |
| A2 | 已定；不可变对象与协调GC | §6.7根解析/Authority/工厂、跨进程guard、固定布局/封口与native journal已补；真实耐久未验 | 同PG窄桥及References组合，Files拥有根；双Host复用原有界保持；装配增量已限定内容接收 | 字节/并发/GC断言保持，新增断DB仍持锁、稳定锁名/迟到native释放断言；物理掉电不冒认 | 方法已定；介质/空间/耐久目标待Profile | 既有A2工程；未知SMB/无法协调拒该写/GC，不换内存锁 | PreparationIncomplete；装配增量已获限定内容接收，未实施/真实验证 |
| A3 | 已定；既有包组合，无生产切换权 | §6.7.5工具配置/manifest/LSN、秘密/子进程及隔离服务Owner已补；完整Owner/实际工具/目标待接入 | StorageMaintenanceBackend及独立受管恢复CLI，目标池/服务槽归PG group；装配增量已限定内容接收 | 闭包/恢复原断言保持，新增无映射tablespace拒绝/原服务排空断言；真实夹具未绑定 | 方法已定；RPO/RTO/长稳和完整验证成本待Profile | Runtime+A1/A2，不新增A3 DLL；内部工具装配不写成客户欠账 | PreparationIncomplete；装配增量已获限定内容接收，未实施/真实验证 |

此表按本轮整个切片判断。后续如只请求 A2 的范围读取或 A3 某个只读校验，必须先明定子切片边界及它实际需要的契约/测试，再单独接收；不得用完整切片的“已定”列概括全部获准。

Contracts/Core 独立 pack；Runtime/适配包独立版本/发行依赖和精确 backend version 元数据。v0.x 仅相同已编译 Contract 互操作，本轮设计修订未发布，不能称已有二进制兼容。正式 1.x 的破坏公开语义/签名改主版本；可选兼容扩展改次版本。API、Schema、Object Format、部署 Profile 分别版本化，不用 API 版本推 Schema。

发布保留上一包/配置/hash，消费者显式选择包和注册目录；启动前校验兼容矩阵，不能自动迁移库。软件回退只在旧包仍支持当前 Schema/Format/旧 ledger codec 时允许；否则先在隔离目标按批准 plan 恢复，禁止就地改生产数据。回退不复活旧 Task/lease/fence。打包记录 .NET、Npgsql/服务器/File Profile、许可证和依赖；本机 DevExpress/AsunImage 与本模块无依赖关系，不安排它们核验或安装。

### 12.1 全部批准范围的文档准备结论（2026-10-11，0.3.1-prep）

按IM-ARCH-001的IM-066全部批准职责核对，**本模块可决定的软件设计已闭合，没有留给实现者再选接口、根算法、事务边界或恢复路线的设计欠账**。该结论覆盖C0/C1/A1/A2/A3完整指导，不只是最近装配片；它是DEV-GOV-010 §4的文档完整结论，保持§12逐切片准备状态，不将尚未绑定的正式Owner内容或真实验证记为通过。本轮由永久原会话完成执行与自审，总控仅接收此结论。

| 批准能力 | 唯一执行、结果及故障位置 | 剩余Owner与准确影响 |
|---|---|---|
| 纯值/接纳/身份/取消/排空 | §6.1–6.5、§7.1.0–4、§9–11；注册快照、两根/原Task/迟到接管、route/attempt/CAS均有确定分支 | 本模块实现与既定断言实际执行；主会话绑定可审计代码基线。C0/C1已接收范围保持，仅规格准备 |
| 多设备/租户共享数据库、技术事务/窄读/批量 | §3–4、§6.6/6.7.1–3、§7.2；独立用途池、固定marshal、同事务epoch/引用/回执、Unknown零重发 | 各领域Owner实现/采纳自身Schema、SQL、codec/golden及权限映射；IM066实现A1及PG夹具；部署Owner提供源端点/角色/TLS/凭据/连接预算。缺口只影响对应绑定/部署 |
| 文件暂存/封口/读取/校验/保持 | §2、§6.2–4、§6.7.4、§7.1.1–2、§9；不透明字节、单写/防逃逸/物理代/锁/journal/原流所有权 | IM066实现A2与异常/跨进程夹具；部署Owner提供根/ACL/介质空间与QualifiedSmb实际证明；生产耐久/掉电另验，不把Unverified升Durable |
| 长期容量、分区/索引/归档/健康诊断 | §4、§6.5–6.6、§7.5、§8、§11.2；Owner Schema分区/索引、注册维护、背压、完整资源计数及只读健康 | 领域Owner冻结其查询/排序/Schema与保留政策，部署/产品Owner提供负载/水位/维护窗口；IM066实现测点并实测。未测不宣称索引/容量最优 |
| Schema迁移、兼容与回退 | §6.4/6.6/6.7.5、§7.3、§12；expand/回填/验证/切换/contract、intent与原step Probe/Resume | IM066实现技术迁移与维护组合；领域Owner交付其准确plan/只读验证/补偿，部署Owner采纳维护和版本切换。缺plan拒该迁移，Factory零DDL |
| GC及完整Owner根快照 | §6.3–4/6.6/6.7.3–4、§7.5；固定epoch/完整分页、逐物理alias复核、隔离/删除原intent、未知阻断 | 各Owner实现/采纳完整resolver、root历史与保留/Legal Hold投影；IM066实现Coordinator/A2。任何漏Owner/未解析根只阻相关存储域GC及全闭包，普通已登记保存/窄读继续 |
| 备份闭包、WAL/恢复点、隔离恢复/验证 | §6.4/6.7.5、§7.1.3–4/7.4、§9、§11；base/cut/连续WAL/全引用闭包/保持、原工具/服务与只读目标 | IM066实现A3组合；Owner提供正式范围及恢复验证；部署Owner提供工具/hash、介质/key服务/隔离目标和预算；产品/部署Owner另批生产切换。未完整闭包NotRestorable，未实测RPO/RTO为NotEvaluated |

三个现有消费者只读核对如下，不改其指导或接口：

| 消费者及消费位置 | IM066确定供给与消费者责任 |
|---|---|
| [lighting-control A.5.3–5](../lighting-control/DEVELOPMENT-GUIDE.md#a53-owner-schema迁移固定sql与marshal) | `LightingLedgerPostgreSqlCodec`消费既有IPostgreSqlBindingCodec，Replace为Transaction/Production、Read为Read/Query，0/1 CAS计数仅指目录命令；Migration预置head，Recovery只查原技术身份。无需为无文件账本新增文件端口；全根Complete仍须所有登记partition校验，设备lease不等于数据库fence |
| [configuration §8.4.1.1–4](../configuration/DEVELOPMENT-GUIDE.md#8411-真实postgresql注册marshal与固定语句消费) | Prepare/Decide多命令、Read窄读与完整原Mutation/快照分片消费既有session/hash/marshal；UInt64经numeric保全域，codec零IO/固定SQL，原技术Unknown不补发。UTC由同PG事务提供；原Owner SQL/codec实现仍由configuration承担，IM066不造配置回执 |
| [inspection-evidence B.6.2–4](../inspection-evidence/DEVELOPMENT-GUIDE.md#b64-公开根resolver有限全快照与恢复) | 七个操作descriptor共用EvidenceEnvelopePayload，独立第八个RootRead descriptor使用EvidenceRootQueryPayload，均按Binding准确定位；package/StoreSlot遵启动快照顺序，Source强持沿原Stage/Finalize身份。Owner根历史通过§6.7.3同事务E与引用一起发布；root resolver有限全物化后交不可变页，上游持原保护。ReservedKey/Unknown未解析时阻GC/完整闭包；C-04原事实子mutation与C-07保持决定由原Owner采纳 |

本轮从程序员输入→装配→输出/失败，以及集成人空Host→注册→原请求→关闭/恢复两条路径定向自审：固定依赖/类型/Schema/Scope/池用途一致；启动不反向枚举未Attach根；Query不写/不续作；epoch、Owner事实/根、技术receipt同commit且结果codec先验；清理到期不转移原Owner；完整性/未知不误认零引用或生产成功。补充可执行断言为：同Id/Revision异Hash及重复Binding零backend调用；同CLR type不同Binding准确分派；codec声明变化拒绝且原身份不变；Factory不调用root.Open、未Attach根不是Complete；e=7提交/回滚/重放与并发原事务的8/9界值、读池GUC不继承、CAS计数排除隐含技术SQL；权限/guard在两页间失效或reserved根不能全量解析时不执行GC/闭包确认。这些是本指导的实现验收输入，当前未创建/运行测试。

既有两种编码构造、Stage/空GcPlan及10份身份/锁向量的有效核查复用；本轮定向结构/本地引用与三个消费者章节锚点检查通过，前后摘要核对确认公开C#声明、§10全文及10份身份/锁向量未改，不重复复算已接收向量。无UI、图像/点云算法与自动视觉参数均不适用，理由见§1；语言由宿主投影稳定键，本模块不新增UI范围。真实.NET构建/消费、PG/Npgsql/RLS/崩溃、文件/native/SMB耐久、PG工具/隔离恢复、性能及现场验收均未执行。内部实现和跨Owner采纳是软件工程工作，客户仅承担其真实政策、负载、物理验收和外部部署信息，不承担本模块设计补缺。

## 附录 A：Module API Contract v0.3 的唯一定位

本文件§6（Module API Contract v0.3）、§10的纯值方法、§6.1–6.7的校验/资源/版本/注入/维护资产/技术存储/真实适配装配语义共同构成唯一模块契约；不另写candidate DTO或在PKG-041更新平行状态机。C0、C1限定范围的六项规格已接收，后续实施仍按主会话授权和代码基线执行；A1/A2/A3按对应真实适配门另行接收。C1仅包含Runtime、可控fake后端、托管维护组合与双无UI Host，不授真实数据库/文件/灾备资格。平台C-01～C-08和业务载荷由领域Owner映射，不能在本模块补私表。文档中公开声明是设计输入，Host/fake调用是未运行示例，测试表是待执行计划，三者与批准/实现/生产证据分别记录。

## 附录 B：具体后续门

1. **代码基线/实施授权**：C0、C1限定范围的六项规格已由主控内容接收，仅规格准备为 ModuleCoreImplementationReady；主会话在代码任务前绑定可审计仓库或批准快照，当前不编码/建工程。A1/A2/A3实施范围及真实门逐切片处理，不要求52模块一起Ready；本轮全范围文档收尾不另等待总控内容复核。
2. **C1 模块运行注入**：主控已内容接收§6.3–6.5的Profile/Catalog/codec、数据库/文件/协调/维护/资产窄端口、clock/barrier、factory、错误及托管维护组合，以及§7.1.1–7.1.2 Factory前有界强持槽、原Task/身份、迟到Create/Open接管、独立有限cleanup观察与原异常/清理异常闭包。C1为ModuleCoreImplementationReady，仅Runtime+可控fake后端+托管维护组合+双无UI Host规格范围；使用既有API，Dispose无超时语义未变。实现仍按后续代码任务授权/可审计基线和§11验证，当前未建工程/编译/运行。正式Owner接入、真实A1/A2/A3后端及物理资格仍按各自门处理。
3. **领域接入（内部跨Owner工程门）**：每Owner实现并采纳正式Scope/Schema、typed payload/result/marshal codec及golden、固定语句/权限/引用目录/根历史和实体写规则；不是统一转嫁给客户的待决设计。只阻断该Owner的事务/读取；未知Owner会阻断相关存储域完整GC/集群闭包，不以零引用跳过，不阻断C0。只有客户保留/质量政策及无法公开确定的物理事实由产品/客户Owner提供。
4. **A1**：内部Factory/Options/可信解析、单PG group、固定技术SQL和FileMetadata桥按§6.7已获主控限定内容接收，不是客户待决设计。外部接入为目标PG18单权威部署、正式Owner SQL/Schema/golden、实际角色/TLS/秘密及连接预算Profile；真实commit Unknown/RLS/池验证尚未执行。HA/多host自动failover不在本次SinglePrimary装配范围。
5. **A2**：内部根Authority/实际句柄防逃逸、稳定跨进程guard、单写/封口/native journal及PG投影桥按§6.7已获主控限定内容接收。外部为预置根/ACL/实际介质与空间Profile、QualifiedSmb锁/耐久资格及真实故障/掉电证据。无法参加协调或未知SMB拒受影响写/GC，已批准只读子切片可单独接收；跨请求续传仍范围外扩展。
6. **A3**：内部维护/工具/manifest/LSN、子进程与隔离服务Owner装配按§6.7.5/§7.1.4已获主控限定内容接收。外部为完整正式Owner resolver/验证及迁移plan内容、实际PG18工具/备份介质/key服务/隔离目标/预算和生产切换Owner。当前无用户tablespace、SinglePrimary base范围先行；额外tablespace须另冻结映射子切片，跨库/未来PITR增量缺闭包时目标NotRestorable；没有真实恢复通过记录。
7. **客户/物理验收**：每租户设备率、对象分布/保留、扩容/水位/时延阈值、RPO/RTO、长稳窗口及现场断电/恢复证据。无来源不编数字；单元/模拟/读取官方资料不能关闭这些门。

已接收的C1托管规格包括Factory/Resolver/BackendSet/Clock/Barrier/Hasher/错误目录/Task与Resource生命周期、Operation writer token/追加证据CAS、GC Plan/Journal/Asset分页、Backup Cut/WAL Part/BackupWork/Closure/RestorePoint/Recovery、显式ResumeMaintenance/attempt/效果回查、托管维护组合与双无UI Host异常闭包；假后端只验证这些软件协议。§6.7/§7.1.4的A1/A2/A3装配增量已获主控限定内容接收，本轮全范围软件设计结论见§12.1；未编译的声明与Host仍须实现任务验证。正式业务codec/SQL/golden及resolver/validation属于各Owner内部接入，真实PG/介质/工具/凭据/Profile及客户验收是其对应部署/运行资格，本稿没有关闭这些门。C0接收保留；C1仅在上述规格范围为ModuleCoreImplementationReady，A1/A2/A3仍为PreparationIncomplete。


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

## 13. 来源、研究选择及适用限制

既有证据复用自 [REF-002 存储专项](../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md)。H:\docs 四来源已在2026-10-06定向比较，SHA-256 和采纳边界不因本轮设计而改写；其中 RPO=0 的 SQLite/AOI 双提交、工厂中心/公开容量数字和 DataService 领域事实均排除，通用对象先封口/DB后引用及 GC/claim 增量已在 §2/§6 保留。本轮不重新下载/全文审无变化原件，不修改 manifest/来源快照。

### 13.1 2026-10-09 官方资料与决定

本轮实际联网读取正文，PostgreSQL 固定版本路径 18，Npgsql 文档为官方维护页面，具体属性再以固定源码核实；没有新建参考快照。

| 资料/实际读取内容 | 冻结到正文的选择 | 适用限制 |
|---|---|---|
| [Npgsql Basic Usage](https://www.npgsql.org/doc/basic-usage.html)：DataSource/thread safety/pool、连接 Dispose 归池、参数占位、事务同连接 | §3 长寿命用途 DataSource、短操作连接、位置参数；不每请求新池 | 通用使用文档，不证明本平台长稳/断连回执/公平性 |
| [Npgsql connection parameters](https://www.npgsql.org/doc/connection-string-parameters.html)：Min/Max pool、Idle lifetime/Pruning、Timeout/CancellationTimeout、NoResetOnClose | §8 删除虚构 MaxIdleConnections，秒/毫秒分开；§3 显式重置、禁 multiplexing | 文档默认值不成为生产预算，具体值由真实 Profile 提供 |
| [PostgreSQL 18 Row Security](https://www.postgresql.org/docs/18/ddl-rowsecurity.html)：default deny、Owner/superuser/BYPASSRLS、FORCE、USING/WITH CHECK | §4 runtime 角色分离、tenant predicate+RLS、池复用反例 | RLS 不是完整隔离证明，表级操作/约束/函数仍须限制 |
| [PostgreSQL 18 Partitioning](https://www.postgresql.org/docs/18/ddl-partitioning.html)：partition pruning、unique/PK 必含 partition key、在线子索引/attach | §4 独立幂等账本、实际 workload 索引与 step journal | 不给生产分区周期/索引列，不证明 BRIN/B-tree 哪个更快 |
| [PostgreSQL 18 Serialization Failure Handling](https://www.postgresql.org/docs/18/mvcc-serialization-failure-handling.html)：40001、40P01、23505、完整事务重试 | §3 有限 whole-transaction retry，未知 commit 不重试 | 重试不保证最终成功，唯一约束错误可能永久冲突 |
| [PostgreSQL 18 Continuous Archiving](https://www.postgresql.org/docs/18/continuous-archiving.html)：base backup+连续 WAL、PITR、timeline 与 cluster 范围 | §7.4 base/WAL/精确对象闭包；更晚恢复点须新增闭包 | PostgreSQL WAL 不含外部图像字节，不能独自保证跨存储恢复 |
| 既有 .NET 10 FileStream.Flush/File.Move、Windows FlushFileBuffers、PG WAL reliability/async commit 归档（REF-002） | §2 内容/目录/物理耐久分开，不用 API 成功宣称 RPO=0 | 原文/软件实验不替代目标介质掉电验证 |

采用 Npgsql 官方驱动的原生池/参数化事务；不用自写池/ORM透传作为并行路线。普通有界 batch 为主，COPY 只在批准导入切片测试后；单权威 PostgreSQL 而非自动 SQLite 双写；PG 物理 WAL 备份为主而非任意 SQL dump 冒称 PITR；租户数据显式隔离而非全局内容 dedup。没有同负载测量，不宣称任何候选最快或支持100台。所有选择与客户/领域边界保持分离。

### 13.2 固定 GitHub 源码、测试、版本/许可

沿用 [npgsql/npgsql v10.0.3](https://github.com/npgsql/npgsql/tree/d3768398c17877b3a916c3c4d87e8e11698991fc)，commit `d3768398c17877b3a916c3c4d87e8e11698991fc`。既有本地源/测试本轮读取 DataSourceBuilder.Build、Transaction.CommitAsync/DisposeAsync 与 DataSourceTests.Dispose/DisposeAsync；许可证为 PostgreSQL 式宽松条款，分发保留声明，不把 AsunImage/DevExpress 放入许可审查。csproj target net8/net9/net10，runtime 依赖 Logging.Abstractions，测试依赖 NUnit/测试基类与真实 PG，分析器/源码生成器为构建依赖；精确传递版本随 A1 包锁定。

| 固定原件与实读范围 | 字节 SHA-256/定位 | 强项、局限及正文落点 |
|---|---|---|
| [NpgsqlTransaction.cs 本地](../../references/open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/NpgsqlTransaction.cs)：CommitAsync 146、DisposeAsync 338 起；[TransactionTests.cs](../../references/open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/TransactionTests.cs)：Commit/Rollback/Dispose | 已有 REF-002 的 `2a44d5f8fcb23459fc1f1f5cacaecce6c1ae1df9cee4f254ff389ae446b9ec6c` / `e76cc2ffcda3771c0a91a4f8f80d7efb9f2c4a3ac3148482556da92fab7fad0d` | 复用驱动与真实事务断言；取消 token 传入提交且 Dispose 可能处理坏连接，不能推断业务回滚；§3/§6 Unknown/迟到真值 |
| [DataSourceTests.cs 本地](../../references/open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/DataSourceTests.cs)：163–205；[DataSourceBuilder](../../references/open-source/npgsql_npgsql/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/NpgsqlDataSourceBuilder.cs)：595 | 原 REF-002 `ab79e557f03ccfa9153bf4303001fc62e3f0a54f55c0be8de82dc7cfac0e58f8` / `978c6fb138a62548eb86038c46961dc8db40150df261c5fba3717e5fd83c3d1e` | 数据源 Dispose 后借出连接仍需关闭，池统计由 busy→0；§6 显式实际排空，不能 Dispose 数据源就报完成；builder 一文件不证明全池实现 |
| 本轮在线 [NpgsqlConnectionStringBuilder.cs](https://github.com/npgsql/npgsql/blob/d3768398c17877b3a916c3c4d87e8e11698991fc/src/Npgsql/NpgsqlConnectionStringBuilder.cs)：819/840/863/885/933/958/981/1294/1378 | `d2496ae5f44d5d8008403285dddf7a2c3ea3233308e7d8518eeeb8fca0532d0a`（在线原始字节） | 精确核属性名、单位、默认和 setter 合法域；§3/§8 直接使用已有驱动，模块拒无界值，不照抄源码默认 |
| 本轮在线 [PoolTests.cs](https://github.com/npgsql/npgsql/blob/d3768398c17877b3a916c3c4d87e8e11698991fc/test/Npgsql.Tests/PoolTests.cs)：13/24、46/72/99、125–137、165 起 | `74e62d3bde94249cdf8c1da48f9ffa4a1c7557c8fa6259fca2a653e12b9fe472`（在线原始字节） | 复用 Min≤Max、耗尽池超时/取消、重置 search_path 的反例与测试思想；§11 租户池复用。OpenAsync_cancel/部分 prune 为 timing-based explicit，不能当平台确定时序/全租户隔离已通过 |

本轮未运行上游或产品测试、未连接/安装数据库、未执行文件耐久/断电/恢复实测，无竞品内部实现或容量承诺。参考源码仅作为驱动使用与测试思想，未复制到产品，不将上游私有 connector/Statistics 或测试基类当公共 API。

### 13.3 2026-10-11 真实装配增量的定向依据

复用§13.1–13.2原证据，仅为本次新增配置/文件锁/工具行为定向核官方正文及固定源码，不下载、不修改来源快照。读取下面资料不代表真实后端资格。

| 实际读取的官方/固定来源 | 本次选择及限制 |
|---|---|
| 原固定NpgsqlDataSourceBuilder.cs公开UseRootCertificate（294起）及固定提交NpgsqlConnectionStringBuilder的Host/Port/Database/Username/Password/Enlist/SslMode/IncludeErrorDetail/LogParameters属性 | §6.7直接使用原生builder/VerifyFull/秘密封装；原文件hash/版本沿§13.2，未复制驱动内部、未运行上游测试 |
| [.NET 10 FileShare](https://learn.microsoft.com/en-us/dotnet/api/system.io.fileshare?view=net-10.0)、[CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew)：共享模式在句柄关闭前约束其它open，删除分享亦影响rename | §6.7共享/排他guard持真实句柄，锁名不随epoch变；不能证明未知SMB断线时旧IO停止，必须实际资格验证 |
| [GetFinalPathNameByHandleW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew)、[GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex)：实际句柄路径、FileAttributeTagInfo/FileIdInfo | §6.7根/对象物理代及拒重解析，native仅在A2；字符串路径和文件年龄不能替代实际身份/ACL/TOCTOU验证 |
| [PG18 pg_basebackup](https://www.postgresql.org/docs/18/app-pgbasebackup.html)：plain/stream WAL、replication权限、tablespace默认位置及映射 | §6.7工具独立Backup角色/两个walsender预算；无额外tablespace本版先行，避免误写源绝对路径；工具调用成功不等于闭包Complete |
| [PG18 manifest顶层](https://www.postgresql.org/docs/18/backup-manifest-toplevel.html)、[WAL range](https://www.postgresql.org/docs/18/backup-manifest-wal-ranges.html)：v2 System-Identifier、精确Manifest-Checksum、Timeline及Start/End-LSN含义 | §6.7用真实manifest与完整part校验固定base身份，Start为必需重放起点、End为最早可结束点；不以stdout/墙钟推LSN，不自行扩成更晚恢复点 |
| [PG18 postgres](https://www.postgresql.org/docs/18/app-postgres.html)、[pg_ctl](https://www.postgresql.org/docs/18/app-pg-ctl.html)、[恢复目标设置](https://www.postgresql.org/docs/18/runtime-config-wal.html)：前台server、pg_ctl start后台化/fast stop、pause及hot_standby条件 | §6.7原group直接持有前台postgres和Reader任务、停原目标并实等退出；pause只读核恢复点，不promote；无Owner服务或未排空进程不能当归还 |
| 本轮定向读取[PG18 SET/LOCAL](https://www.postgresql.org/docs/18/sql-set.html)、[set_config/current_setting](https://www.postgresql.org/docs/18/functions-admin.html)、[row-level locks](https://www.postgresql.org/docs/18/explicit-locking.html)：LOCAL止于当前事务；FOR UPDATE锁到事务结束，RR/Serializable并发修改可能报错 | §6.7.3以同事务行锁/epoch及固定local GUC供Owner SQL消费，不改公开接口；参考资料只证明PG语义，不证明注册SQL、guard、RLS、跨Owner原子接线或性能已经通过 |

本次只修订唯一指导并定向自审，未创建工程/脚本/报告，未启动PG工具或访问真实数据库/文件介质；C0/C1接收状态保持，A1/A2/A3装配增量已获主控限定内容接收，真实后端验证与现场验收仍未执行，相关门仍未关闭。
