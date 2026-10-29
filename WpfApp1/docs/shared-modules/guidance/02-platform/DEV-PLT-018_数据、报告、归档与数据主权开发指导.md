# 数据、报告、归档与数据主权开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-PLT-018`
- 版本：`1.1.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：分级、容量、压缩、归档、报告、脱敏
- 直接依赖：`DEV-GOV-004`, `DEV-GOV-008`
- 主要输出：EvidencePolicy、ReportTemplate、ArchiveReader、数据最小化

>
本文均以 `ARCH-PCBA-VISION-001 v0.5.3` 为架构输入。该架构当前仍为候选基线/DocMapped，未因本开发准备包而自动获得架构批准或生产资格。若本包与未来获批架构、既有权威 Schema、状态/Owner 规范或实际仓库实现冲突，以获批权威资产为准，并必须登记冲突后再实现。


## 统一实施规则

1. **单一权威**：架构文档负责关系与边界；Schema 负责数据结构；状态/角色规范负责状态与 Owner；PageContract 负责 UI 行为；本开发指导负责实施语义、禁止路径、算法选择、性能、测试与验收；Validator/Test/Manifest 分别负责机器校验、验证和交付快照。
2. **不得复制第二套事实**：不得在产品目录、`spi/`、ViewModel、数据库或临时 JSON 中建立与既有 Schema/状态机/Owner 平行的定义。
3. **事实与投影分离**：UI、报告、统计、质量中心、AI 解释均不得成为事实的第二写入权威。
4. **生产副作用后移**：能在离线/Replay/Shadow 完成的验证，不要先绑定真实设备。
5. **所有失败可见**：失败、拒识、覆盖不足、资格不足、配置失效都必须形成显式状态或事实，禁止默认降级为 Success/OK。
6. **性能有预算**：算法、UI、IO、缓存和并发必须在设计时给出预算；不得在最后阶段才测性能。
7. **可回放优先**：能进入 Replay 的输入、参数、模型、库快照、标定、环境和算法版本尽量冻结为可引用资产。
8. **AI 不获得隐含权威**：AI 只能在既定 Contract 和 AuthorityScope 内产生建议/候选或受控 revision。
9. **真实硬件证据单独计门**：没有 HIL/实机/Golden Sample 证据时，文档状态只能为“准备完成/软件可验证”，不能写“生产通过”。

## 1. 实施目标

`EvidencePolicy、ReportTemplate、ArchiveReader、数据最小化` 是本指导的稳定闭环。实现时必须优先建立接口和可回放测试，再接入真实设备/产品。

## 2. 正常路径

```text
Input / Query
  → Validation
  → Capability / Authority Resolution
  → Execution
  → Fact / Candidate
  → Decision / Projection
  → Commit / Receipt
  → Evidence / Query
```

## 3. 异常与恢复

至少覆盖：缺输入、版本不匹配、权限不足、资源不足、设备断开、超时、取消、进程重启、网络断开、重复消息、乱序消息、部分提交、Commit 重试。

## 4. 性能

建立 `PerformanceProfile`：吞吐、P50/P95/P99、峰值内存、CPU/GPU、队列深度、并发度、冷启动、恢复时间。任何“优化”必须有前后测量。

## 5. 测试

- Contract/Schema test
- Happy path
- Failure matrix
- Recovery/restart
- Concurrency/race
- Replay
- Security/permission
- Performance benchmark
- HIL（适用时）

## 6. 禁止实现

- UI 直接写事实；
- Adapter 自己定义领域 Owner；
- 通过字符串字段绕过版本 Schema；
- 失败后静默补写成功结果；
- 用全局锁掩盖并发设计；
- 把网络 ACK 当作业务 Applied；

<a id="query-storage"></a>
## 7. “万能查询”应是受控查询核心与可选查询UI

独立Query核心支持已注册数据集/字段/类型/单位/枚举/运算符、范围/排序/分组/聚合/分页和受控导出；UI可选条件构建器、结果表/图联动、保存查询、证据跳转。它消费各Owner公开只读投影，不拥有跨模块私表，不提供任意SQL文本或任意跨库写操作。Core可无UI供报告/API调用，业务权限在服务端/应用端再次执行。

查询请求固定用户/作用域、数据集/字段版本、过滤/排序、页大小/预算、水位/统计快照、时区和输出格式。值参数化，字段/表/排序表达式走目录白名单；值参数化不等于动态标识符安全。数值单位、Unicode/大小写、null与空字符串、时间边界/夏令时和首检/复测语义显式；原UTC保存，界面时区只影响表达。保存查询带schema版本，字段删除不能默默忽略条件。

大结果使用稳定排序＋唯一键的游标分页；页游标绑定查询hash、视图语义/水位和作用域，权限变化后重新验证。Offset适用小页/随机跳页场景但深页需评估代价；页之间数据变化必须选择固定快照或显式实时视图，不能声称混读结果是同一时刻。水位本身不冻结更新、删除或晚到数据。总数可延后/近似但清楚标注；导出必须绑定所声明的总体和完整页集合，不把Grid当前已加载行误当全部。

查询/导出有并发、行数/时间/内存/扫描成本限额和取消；超限返回明确原因与缩小范围建议。UI快速改筛选后丢弃旧响应，错误不显示上一查询的“正确结果”。CSV与数据型XLSX分别按格式的文本/公式规则处理不可信单元格，不能只靠给所有值加前缀并声称保留原值；版式XLSX由046负责。字段脱敏/行权限仍生效。拟验收包括引号/注入值、非法字段、同时间戳多行跨页不重漏、权限变化、空集、连接丢失、取消大导出和声明的总体一致性。
查询的公开API、目录、真正固定总体、keyset游标、权限撤回、流式导出和结束校验只在[IM-045唯一模块指导](../../../independent-modules/query/DEVELOPMENT-GUIDE.md)维护；[PKG-042](../../packages/PKG-042_Query.md#query-implementation)仅映射产品接入；本节只规定平台数据主权和存储边界。水位、时间点或增量游标不能在上层被简称为“快照”，报告或页面必须携带042返回的快照/实时视图语义、查询hash和字段版本。042不拥有业务表写权，也不因导出方便修改生产Schema。

## 8. 数据存储能力与数据库选择

**共享数据库的技术实施采用 [IM-066 storage-database](../../../independent-modules/storage-database/DEVELOPMENT-GUIDE.md) 冻结的 PostgreSQL + Npgsql 路线；两者不是两个数据库。** PostgreSQL 是数据库服务器，Npgsql 是其 .NET 驱动。具体软件适配基线、版本和官方依据只在 IM-066 维护；实际部署的小版本、拓扑、凭据、容量、耐久和验收仍由 Profile 绑定。已有客户数据库不自动迁移；SQLite 离线适配须独立规划并验证同步，不能默认两份生产主库。

| 部署条件 | PostgreSQL路线的验证内容 | 其它现有部署的接入条件 |
|---|---|---|
| 一致提交与追溯 | 事务/约束、版本冲突、结果与发件箱的原子交接；MVCC支持读写并发但隔离级别需明确 | 客户已有成熟部署/备份/维护团队时优先比较集成成本，不为技术喜好迁移 |
| 查询/统计 | 按实体/尝试/时间/产品的组合索引、分区/聚合与必要JSON扩展 | 同一数据和查询实测P95/P99/存储写放大，不以功能清单推断更快 |
| 现场部署 | 服务管理、升级/迁移、磁盘满/断电、备份恢复与权限 | 离线/嵌入式约束、RPO/RTO、运维成本和客户数据主权决定，不擅自采用云服务 |

独立 `IM-066 storage-database` 能力提供连接/会话工厂、明确事务、迁移执行/版本、健康/备份恢复适配及诊断；领域仍持有自己的Repository/查询语义与表写Owner。**不做暴露所有表任意增删改的God-class数据库模块**。`IM-015 inspection-evidence` 负责结果事实与证据引用，程序/权限/复判有各自Owner；同库不等于同权。查询UI只读权限和运维UI高权限分开，不能以“全量操作”开放生产原始结果修改。

图像、2D/3D原始数据、点云、高度场和视频**不得存入数据库字段**。它们必须写入受控硬盘文件存储（本机数据盘、专用磁盘或 NAS），按不可变对象、目录分区、文件长度和 hash 管理；数据库只保存对象 ID、相对定位、大小、hash、格式、来源、版本、保留和完整性状态。证据先可靠写入硬盘并完成封口/校验，再由结果事务记录文件引用和原子发件箱；中途失败保留待回收/待提交状态，禁止先报成功再写文件。清理/保留/备份必须同时保护数据库记录和硬盘文件闭包，不由通用库定时删用户数据。

Read Committed 的不同语句可见不同快照，Serializable 仍可能要求完整事务有限重试。技术回执、池、取消和 Unknown 的具体实施按 IM-066；领域 Owner 提供事务不变量及版本化绑定。外部设备动作不放入数据库重试。Npgsql 固定源码、测试与版本依据见 IM-066，不重复选择驱动；本轮未安装或连接数据库。

真实后端及产品资格按工作负载验证连续写入、复判争用、大查询与报表导出并发，覆盖磁盘满、进程中断、提交应答丢失、迁移中断、备份恢复和证据完整性。备份存在不等于可恢复，RPO/RTO 由已采纳 Profile 冻结并实测。没有同样本性能比较，不宣称 PostgreSQL 优于其它数据库；未执行的后端验证不阻断已接收的纯 Core 规格。

本轮实际阅读、固定提交与适用限制见[REF-002专项依据](../../../references/REF-002_GitHub_DevExpress与OpenSource研究基线.md#add-module-research)。

<a id="archive-consistency"></a>
## 9. 结果、归档与恢复的一致边界

数据/文件技术实施唯一见 [IM-066](../../../independent-modules/storage-database/DEVELOPMENT-GUIDE.md)，[PKG-041](../../packages/PKG-041_Storage.md#storage-transactions-durability) 保留产品接入映射；结果业务提交见 [DEV-PLT-012](<DEV-PLT-012_Evidence Graph与Result Commit开发指导.md#evidence-commit-protocol>)。源 AOI 的 SQLite 本机权威/远端投影不能直接迁入；每种部署须绑定唯一写入权威及离线行为，不能双主写同一事实。

报告/数据导出绑定 PKG-042 返回的固定总体标识或显式实时视图语义、查询水位、字段版本、作用域和完整分页集合；水位不能替代固定总体。同时保留失败/Unknown/未测等真实分母，不能因提交模块误拒坏结果而虚高良率。仅结果引用导出、含可视证据包、可重放闭包分别标用途，不把CSV或截图称完整追溯。关闭视图不取消已经提交的事实；导出失败不得公布半文件为完成包。
报表编排、模板可信性、渲染资源、分格式Partial、暂存→结束校验→持久发布、取消/恢复及可嵌入报告控件只在[IM-044 Reporting](../../../independent-modules/reporting/DEVELOPMENT-GUIDE.md)维护；[PKG-046](../../packages/PKG-046_Reporting.md#reporting-implementation)仅保留应用输入/用途/Owner映射。原始行查询与统计分母分别由IM-045和IM-043及领域Owner提供。质量工作站的报告页面组合见[UI-PCS-021 §12](../../guidance/14-page-contracts/UI-PCS-021_Quality_Control_Workbench.md#reporting-workflow)，页面不得另建查询、报告API或事实权威。

归档/压缩/分区合并先生成并验证新不可变对象，在原投影 Catalog 原子切换，不改变原证据 Manifest 的内容 hash。原件释放须满足引用、读/导出/备份保持、保留/调查策略及 GC 协调。备份 cut、数据库恢复点、对象闭包和持久保护顺序唯一按 [IM-066 §7.4](../../../independent-modules/storage-database/DEVELOPMENT-GUIDE.md#74-备份闭包与目标恢复点)，不将任意独立数据库快照与文件目录拼成可恢复包。恢复逐项核精确目标闭包、引用/Schema/业务样例；不复活旧设备任务，外发通知可能重复须对账。数据库提交、介质掉电耐久及 RPO/RTO 分别验收。
