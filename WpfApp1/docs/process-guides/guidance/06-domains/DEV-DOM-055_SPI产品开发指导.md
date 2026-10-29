# SPI产品开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-DOM-055`
- 版本：`1.1.0-prep`；日期：2026-09-29
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：3D 采集、HeightField、参考面、焊盘/开口、锡膏分割、量测、规则、SPC
- 直接依赖：`DEV-VIS-027`, `DEV-MET-032`, `DEV-MET-034`
- 主要输出：SPI 领域独立语义和跨工序反馈

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

## 1. 领域实施边界

领域包拥有自己的对象、规则、算法语义和工作流；只通过批准的契约消费平台服务。不得直接访问其他领域 Store、ViewModel、算法缓存或设备线程。

## 2. 统一运行链

```text
ManufacturingReference / BOM / PnP / LibrarySnapshot
 → TargetSet / InspectionProgram
 → Recipe / EffectiveRuntimeManifest
 → Acquisition / Vision
 → Measurement / Coverage
 → Fact / RuleEvaluation
 → Decisioning
 → Evidence Commit
 → Review / RouteAssessment / Quality
```

## 3. 可复用能力

优先复用：身份、坐标、采集、定位、计量、证据、Pipeline、性能、UI 工作台；领域专有：目标语义、缺陷解释、工艺规则、对象状态。

## 4. 开发验收

建立至少三类数据集：正常、边界、故障/污染。按缺陷类型和产品族分层统计，不允许把不同分母直接合并。所有领域结果必须能回溯到目标、算法版本、输入证据和覆盖状态。

## 5. SPI 纵向链

```text
3D Sensor/Acquisition
 → HeightField Quality
 → Board/Stencil/PAD Reference
 → Paste Segmentation
 → Feature Measurement
 → Paste Defect Rule
 → InspectionDecision
 → Evidence Commit
 → SPC / Printer Feedback
```

SPI不把印刷机命令直接写入自身机判。原040提交完成后，042/045固定读入统计与建议，原设备应用Owner接纳命令并交047可靠投递，再由048关联实际印刷范围与后效。传输完成、业务接收、配方激活、逐参数应用和效果各持独立证据；无应答查询原命令，不重印或换键调机。

详细方法唯一在[055A采集](<DEV-DOM-055A_SPI 3D Acquisition与HeightField质量开发指导.md>)、[055B目标/物理参考](<DEV-DOM-055B_SPI Reference Plane与Pad_Stencils Target开发指导.md#spi-reference-target-implementation>)、[055C材料/计量](<DEV-DOM-055C_SPI Paste Segmentation与Metrology开发指导.md#spi-paste-method>)及[055D规则/统计/反馈](<DEV-DOM-055D_SPI Rule SPC与Printer Feedback开发指导.md#spi-feedback-implementation>)；工艺义务/快编及页面接入回[PG014 §13](../../processes/PG-014_spi.md#spi-method-reception)。055A与公共矩的下一切片尚在深化，不据本页泛化流程宣称全部内部方法完成。

## 测试与验收

- 正常、边界、难例/污染、拒识样本；
- Replay 前后结果差异可解释；
- 关键参数变更触发必要回归；
- 失败/取消/恢复路径有证据。

## 性能

必须记录典型耗时、P95/P99、峰值内存、并发条件和数据规模；大图/3D 必须标明 ROI、分辨率和中间结果生命周期。

## 禁止实现

不得将领域专有对象降格为通用对象；不得绕过 Contract/Owner；不得将拒识/不可观察状态静默转换为 OK；不得用 AI/经验值修改生产权威。

## 6. Domain implementation freeze

本领域对应的实施规格必须覆盖：`3D acquisition quality;Reference plane;Pad target generation;Paste segmentation;Paste volume;Paste area;Paste height;Paste offset;Paste shape;SPI rule evaluation;SPC;Printer feedback`。除这些 FS/能力明确允许外，禁止在领域包中添加隐含流程或共享语义。

### 开发顺序

先冻结当前切片的输入/语义/验收反例，再接公共能力与无UI应用：制造/独立坐标→目标/参考→材料/具名量→039规则/完整性→原机判映射/040证据提交→042查询及045统计/建议→页面。契约/样例固定后，页面原型和不同独占应用切片可并行；测试/性能预算自始绑定，并非等UI完成才设计。

### 停止条件

发现跨领域内部 Store、第二事实模型、未登记状态/Owner、隐式阈值、未验证 API、无证据的质量结论时必须停止并登记 Blocker。
