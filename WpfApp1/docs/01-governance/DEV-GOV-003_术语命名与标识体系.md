# 术语、命名、标识与语义冻结标准
- 文档 ID：`DEV-GOV-003`
- 版本：`1.0.0-prep`
- 状态：`ImplementationSpecificationReady`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：对象名、状态名、契约名、UI 命令名、日志和审计事件
- 直接依赖：`ARCH-PCBA-VISION-001`
- 主要输出：统一术语、禁止同义词漂移、ID 规则

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

## 1. 核心语义严格区分

`Fact`、`Candidate`、`Decision`、`CommitReceipt`、`ReviewClaim`、`ReviewDecision`、`FinalDisposition`、`RouteAuthorization` 不得互换。

`Product` = 产品身份；`ProductRevision` = 产品版本；`InspectionProgram` = 检查什么；`Recipe` = 怎么执行；`MachineProfile` = 机器能力；`CalibrationProfile` = 标定定义与资格；`LibrarySnapshot` = 固定库版本集合；`EffectiveRuntimeManifest` = 本次运行的不可变闭包。

`BoardRun` 是生产生命周期；`ProcessAttempt`/`InspectionAttempt` 是动作语义；重试必须区分计算重试与提交重试。

## 2. 标识规则

- 公开契约 ID：稳定、不可复用、语义中立。
- AlgorithmId：命名算法族，不嵌入具体参数值。
- PageId / CommandId：稳定、可 UIA/自动化测试定位。
- HALCON 算子名必须使用官方拼写，不根据 C# 方法习惯改写。
- 不使用 `Universal*`、`Generic*`、`Any*` 作为生产领域对象名来掩盖边界问题。
