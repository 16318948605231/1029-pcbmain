# 插件SDK与扩展点开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-PLT-017`
- 版本：`1.0.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：插件能力、签名、版本、卸载、权限
- 直接依赖：`DEV-GOV-005`, `DEV-GOV-006`
- 主要输出：PluginManifest、NotReady、Compatibility、Resource/Permission

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

`PluginManifest、NotReady、Compatibility、Resource/Permission` 是本指导的稳定闭环。实现时必须优先建立接口和可回放测试，再接入真实设备/产品。

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
