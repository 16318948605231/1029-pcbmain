# HIL、故障恢复与长稳开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-QLF-072`
- 版本：`1.0.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：断电、断网、卡板、设备断连、重启、升级
- 直接依赖：`DEV-PLT-015`, `DEV-PLT-016`
- 主要输出：故障注入、恢复矩阵、证据闭环

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

## 1. Qualification 与 Implementation Maturity 分离

`Contracted/Implemented/Tested/HIL/...` 描述工程成熟度；`ProductionAccepted` 只表示产品/现场资格，不是每个软件对象都必须经历的线性状态。

## 2. Golden Sample

样本至少分：正常、边界、典型缺陷、难例、拒识、噪声/污染、跨批次。每个样本记录采集设备、版本、标定、环境、预期真值和适用域。

## 3. 回放

Replay 必须冻结输入闭包：图像/HeightField、ManufacturingReference、Recipe/Program、LibrarySnapshot、CalibrationProfile、ModelRecord、Environment、AlgorithmVersion。结果差异必须可定位到发生改变的节点。

## 4. 故障恢复

恢复测试必须验证：没有重复事实、没有丢失事实、没有错误放行、没有绕过安全边界、重新启动后能解析 Active Manifest/BoardRun，迟到消息不会改写历史已提交事实。
