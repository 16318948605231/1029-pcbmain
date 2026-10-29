# Contract / Schema / Validator 开发标准
- 文档 ID：`DEV-GOV-004`
- 版本：`1.0.0-prep`
- 状态：`ImplementationSpecificationReady`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：所有跨模块和持久化契约
- 直接依赖：`DEV-GOV-001`, `DEV-GOV-002`
- 主要输出：契约设计、兼容、验证、Golden Vector、消费者闭环

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

## 1. ContractCandidate 最低信息

必须绑定 `ContractId, SchemaId, SchemaMajor, Owner, BackupOwner, Producer, Validator, Consumer[], AuthoritySource, AuthorityScope, Status, CompatibilityPolicy, TestSuite, StateOwner, CommitOwner, QualificationOwner, ManifestReference`，适用时追加 `AcceptanceProfile`。

## 2. 三层验证

1. **格式验证**：Schema/必填/类型/枚举/范围。
2. **语义验证**：跨字段关系、单位、版本闭包、权限、状态合法性。
3. **运行验证**：真实消费者、乱序、重试、超时、断点、回读与历史兼容。

## 3. Golden Vector

对高风险契约维护：
- 正常样例
- 最小样例
- 最大合理样例
- 缺失/冲突样例
- 版本兼容样例
- 签名/hash 样例
- 失败恢复样例

## 4. 版本兼容

默认只允许 Schema major 不变的兼容演进；breaking change 必须新 major/新版本路径并建立回放兼容测试。字段含义改变视为 breaking change，不允许仅调整文档而保持旧版本号。


## 实施级补充

本包中的 `12-function-specs/FS-*.md` 是本治理规则的实施执行层。开发人员/AI 不得只阅读本治理文件就开始编码，必须继续读取对应 FS、ContractCandidate、State/Owner 和测试规范。
