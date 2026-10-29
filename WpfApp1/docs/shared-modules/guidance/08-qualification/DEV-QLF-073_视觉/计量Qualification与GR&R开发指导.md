# 视觉/计量Qualification与GR&R开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-QLF-073`
- 版本：`1.1.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：量测资格、MSA/GR&R、跨机、有效期
- 直接依赖：`DEV-MET-033`, `DEV-GOV-008`
- 主要输出：资格证据包与影响分析；参考证书为输入，签发/撤销决定由原计量Owner执行。

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

<a id="metrology-qualification-acceptance"></a>
## 5. 计量资格证据的接收与使用

本页负责验收/交接，不复制[033实验与证书方法](<../../04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#metrology-qualification-method>)、[055独立能力](../../../packages/PKG-055_Qualification.md#metrology-qualification-integration)或[IM-043数值实现](../../../../independent-modules/statistics/DEVELOPMENT-GUIDE.md#qualification-numerical-backend)。软件实现验证、真实测量实验、计量审定与现场生产资格分别接收，不能用任一层的PASS代替其余层。

| 接收顺序 | 审核对象与拒绝范围 |
|---|---|
| 原参考与计划 | 按[033 §15](<../../04-metrology/DEV-MET-033_MSA、GR&R与计量资格开发指导.md#reference-certificate-adoption>)核原件/投影/实物/当前用途；计划固定被测量、层级/独立性、实验格、方法/估计量、验收界与失败处理。缺溯源只阻溯源结论，无参考散布不得更名为偏差资格 |
| 观测与计算 | 原计划有效/失败/未采/排除分母均保留，逐行追到真实观测；计数完整、数值有效和实验适用分别看。复制同帧/缺格补均值、时间完全混杂或单位错误不能被图表美观掩盖 |
| 分析报告 | 核方法版本、SS/df、原负分量/边界估计、残差/秩、共同参考与预算缺口、区间方法/支持域。点估计不等于已有置信界；有限精度/边界诊断不洗成0不确定度 |
| 审定交接 | 055只给证据，原计量Owner核实际标准件、方法范围、用途/条件与批准权限；沿原存储接收回执，Unknown查询原操作。UI/报表没有签发或放行权 |
| 当前消费与追溯 | 原能力/量测/质量Owner按用途消费精确资格，变更、损伤、撤销、环境越界沿033 §11追加影响并处置。历史报告保留原字节，后续撤销发布时间和适用起点分开 |

跨机比较须使用可识别实验和共同参考，不以两台机器相关性高或平均差为0授予等价；变化锡膏按SPI实际时间/材料方案执行，稳定标准件通过不等于材料分割或真实体积通过。SPI与PCB孔槽/钢网至少各验证一条同055/045核心的调用、失败和资格交接链；设备SDK与现场条件不足只阻依赖它们的验收。本页仍为DocMapped，未执行计量认证、跨机或FAT/SAT。
