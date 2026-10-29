# Stencil Inspection领域开发指导

> 2026-09-27 平台归位：当前职责与范围按[平台设计基线](<../../../00-baseline/PLATFORM-DESIGN-BASELINE.md>)及[所属指导目录](<../../README.md>)绑定。本页保留原ID与细化内容；原状态 `ImplementationSpecificationReady` 仅作历史记录，精确契约/Owner/参数未获批前不作为生产实施准入。
- 文档 ID：`DEV-DOM-054`
- 版本：`1.1.0-prep`
- 状态：`DocMapped`
- 架构基线：`ARCH-PCBA-VISION-001 v0.5.3`
- 适用范围：开口、孔壁、堵孔、污染、变形、厚度
- 直接依赖：`DEV-VIS-027`, `DEV-MET-032`
- 主要输出：具名开口/3D量测与缺陷事实、独立维护提案；提案不是设备执行或质量处置

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
StencilManufacturingReference / QualifiedCleanReference / LibrarySnapshot
 → TargetSet / InspectionProgram
 → Recipe / EffectiveRuntimeManifest
 → Acquisition / Vision
 → Measurement / Coverage
 → Fact / RuleEvaluation
 → Decisioning
 → Evidence Commit
 → Review / RouteAssessment / Quality
```

钢网实际顺序和精确主链以[PG-013](../../processes/PG-013_stencil.md)为准。原始量测/候选→039评价→原Owner通过040提交；维护功能读取已提交来源及当前资格。上图是责任概览，不允许在保存前向设备执行维护。PCB资料只能经批准制造规则形成钢网参考候选，不能把BOM/PnP或PCB焊盘直接当加工开口全集。

## 3. 可复用能力

优先复用：身份、坐标、采集、定位、计量、证据、Pipeline、性能、UI 工作台；领域专有：目标语义、缺陷解释、工艺规则、对象状态。

## 4. 开发验收

建立至少三类数据集：正常、边界、故障/污染。按缺陷类型和产品族分层统计，不允许把不同分母直接合并。所有领域结果必须能回溯到目标、算法版本、输入证据和覆盖状态。

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

本领域对应的实施规格必须覆盖：`Aperture geometry;Stencil thickness;Wall condition;Blocked aperture;Maintenance advice`。除这些 FS/能力明确允许外，禁止在领域包中添加隐含流程或共享语义。

### 开发顺序

`输入/制造参考 → 目标 → 算法/计量 → Quality Gate → Fact → Decision/Projection → Evidence → UI → Test/Benchmark`。

### 停止条件

发现跨领域内部 Store、第二事实模型、未登记状态/Owner、隐式阈值、未验证 API、无证据的质量结论时必须停止并登记 Blocker。

### 独立模块接入及并行边界

公共包只提供通用特征/关联/表面/量测/统计，钢网阶段、制造意图、清洁语义和维护规则留在本领域。2D、3D和维护三个应用切片可在公开合同及精确文件范围冻结后并行，共享项目/Contract/资源保持一个写入Owner；具体顺序和退出断言见[DEV-PLAN-014 §37](../../../09-development-plan/DEV-PLAN-014_全量研发工作包与并行依赖DAG.md#stencil-method-slices)。页面[UI017](../14-page-contracts/UI-PCS-017_Stencil_Inspection_Workbench.md)只投影原结果与命令，维护链唯一细节在[FS043 §28](../12-function-specs/FS-043_Maintenance_advice.md#stencil-maintenance-comparison)，不复制第二套状态/数据。当前仍为DesignReview/DocMapped，正式合同与工业资格各自关闭。
