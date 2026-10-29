# 文档自动审计规则与机器检查协议
- 文档 ID：`DEV-GOV-009`
- 版本：`1.0.0-prep`
- 状态：`ImplementationSpecificationReady`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：本开发准备包及未来仓库文档
- 直接依赖：`DEV-GOV-003`, `DEV-GOV-004`
- 主要输出：文档图谱、引用、闭环、冲突与覆盖审计

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

## 自动审计层级

1. 文件/标题/编号结构；
2. 文档元数据完整性；
3. 内部引用目标存在性；
4. Document Registry 依赖闭环；
5. 术语一致性；
6. Authority/Owner/Producer 冲突；
7. Architecture Section → Guide 覆盖；
8. Guide → Contract/Test/Acceptance 完整性；
9. 领域能力 → UI → Runtime → Evidence → Quality 链路；
10. 禁止路径扫描。

自动审计结果采用：`PASS / WARN / BLOCKED / NOT_VERIFIABLE`。

`NOT_VERIFIABLE` 用于必须依赖真实仓库、真实 HALCON 安装、实机或 HIL 的项目；不得伪装成 PASS。


## 实施级补充

本包中的 `12-function-specs/FS-*.md` 是本治理规则的实施执行层。开发人员/AI 不得只阅读本治理文件就开始编码，必须继续读取对应 FS、ContractCandidate、State/Owner 和测试规范。
