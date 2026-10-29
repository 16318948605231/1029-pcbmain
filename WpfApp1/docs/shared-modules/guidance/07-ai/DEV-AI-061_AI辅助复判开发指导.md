# AI辅助复判开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-AI-061`
- 版本：`1.0.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：相似案例、候选排序、解释、拒识
- 直接依赖：`DEV-AI-060`, `DEV-PLT-012`
- 主要输出：Suggestion，不改变 ReviewDecision

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

## 1. AI 生命周期

```text
Offline → Replay → Shadow → Advice → Automatic
```

每一级必须有退出条件。`Automatic` 不是“模型准确率够高”就自动开启，还需要拒识、回退、权限、审计、资源预算、版本快照、现场资格。

## 2. AI 输入/输出

AI 输入必须是已授权的 evidence/data snapshot；输出为 Candidate/Suggestion/Draft，除非明确的 AuthoritySource 允许生成新的受控 decisionRevision。不得直接写 MeasurementSet、InspectionFact、MachineDecision、RouteAuthorization。

## 3. 统计验证

按产品、缺陷类别、样本来源、班次/设备/材料分层；报告 Recall、False Alarm、Escape 以及置信区间，不仅报单一 accuracy。测试集不能与调参集混用。


## 实施级关联功能

本指导的具体功能以以下实施规范为准：FS-067。每个 FS-xxx 都包含输入/输出、算法、鲁棒性、性能、UI、测试、验收和禁止实现。
