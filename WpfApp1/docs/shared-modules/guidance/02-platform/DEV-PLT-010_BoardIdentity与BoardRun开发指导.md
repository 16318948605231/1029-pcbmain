# BoardIdentity与BoardRun开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-PLT-010`
- 版本：`1.0.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：身份解析、BoardRun 生产运行、RecipeMatch、首件/换型门禁
- 直接依赖：`DEV-GOV-004`, `DEV-GOV-005`
- 主要输出：BarcodeIdentityPolicy → IdentityResolutionReceipt → BoardIdentity → EffectiveRuntimeManifest → BoardRun

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

`BarcodeIdentityPolicy → IdentityResolutionReceipt → BoardIdentity → EffectiveRuntimeManifest → BoardRun` 是本指导的稳定闭环。实现时必须优先建立接口和可回放测试，再接入真实设备/产品。

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

## 7. 身份专门要求

读码观察是 `Observation`，解析是 `IdentityResolutionReceipt`，最终 `BoardIdentity` 是生产绑定结果。解析未完成可以留证、Hold、人工恢复，但不能正常绑定生产 Recipe/Release。合法重检与重号冲突必须区分。首件/换型门禁不得继承上一次 BoardRun 的放行状态。


## 实施级关联功能

本指导的具体功能以以下实施规范为准：FS-001, FS-002。每个 FS-xxx 都包含输入/输出、算法、鲁棒性、性能、UI、测试、验收和禁止实现。

<a id="runtime-binding"></a>
## 运行绑定与计算尝试的补充边界

身份Owner/BoardRun不由任务图生成。机台应用在已批准激活边界解析已发布程序、实际设备/标定和能力，为该板/面/检测尝试绑定FS-002运行清单；发布r2只产生可选新版本，不影响板A的r1绑定。已有尝试的阶段结果保留其原清单，资格失效按产品策略处理，不能换参数继续后宣称仍是同一快照。

节点纯计算重试产生关联的计算实例，实体板、原BoardRun和检测尝试不因此改变；补采/重新检测/返修复测由原Owner按批准协议决定新的尝试及关联。提交未知查询同Fact/CommitIdentity，不能通过新建板运行绕过未知状态。重启重新建立执行epoch和当前设备位置确认，历史单调时钟/Task/句柄不复活。具体执行见[DEV-PLT-011 §4–5](<DEV-PLT-011_Inspection Pipeline与Attempt开发指导.md#attempt-cancellation>)，发布边界见[PKG-035](../../packages/PKG-035_ProgramPackage.md#program-lifecycle)。
